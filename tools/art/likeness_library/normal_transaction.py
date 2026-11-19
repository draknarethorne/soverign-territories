"""Content-bound publication/recovery for one explicitly scoped normal batch."""
import json
import os
import pathlib
import shutil
import uuid

from . import metadata


def safe(root, relative):
    root = pathlib.Path(root).resolve()
    path = pathlib.PurePosixPath(relative)
    if path.is_absolute() or "\\" in relative or ":" in relative or any(
        part in ("", ".", "..") for part in relative.split("/")
    ):
        raise ValueError(f"unsafe normal transaction path: {relative}")
    target = root.joinpath(*path.parts)
    if root not in target.resolve().parents or target.resolve() != target:
        raise ValueError(f"linked/escaping normal transaction path: {target}")
    return target


def write(path, data):
    from .normal_import import _write_receipt

    _write_receipt(path, data)


def _replace(source, destination, checksum):
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.normal-swap")
    try:
        shutil.copy2(source, staged)
        if metadata.content_sha256(staged) != checksum:
            raise OSError(f"normal transaction copy changed: {source}")
        os.replace(staged, destination)
    finally:
        if staged.exists():
            staged.unlink()


def verify(root, journal, *, applied=True):
    if pathlib.Path(root).resolve() not in pathlib.Path(journal).resolve().parents:
        raise ValueError("normal publication journal must stay inside its library")
    data = json.loads(pathlib.Path(journal).read_text(encoding="utf-8"))
    if data.get("kind") != "normal-publication" or data.get("root") != str(pathlib.Path(root).resolve()):
        raise ValueError("normal publication journal is bound to another root or unsupported")
    if applied and data["status"] != "applied":
        raise ValueError(f"normal publication is {data['status']}, not applied")
    for relative, expected in data["after"].items():
        path = safe(root, relative)
        if applied and (not path.is_file() or metadata.content_sha256(path) != expected):
            raise ValueError(f"normal published content changed: {relative}")
    if applied:
        for relative in data["removed"]:
            if safe(root, relative).exists():
                raise ValueError(f"normal removed source reappeared: {relative}")
    return data


def _restore(root, data):
    backup = pathlib.Path(data["backup"])
    manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    before = {entry["source"]: entry for entry in manifest["entries"]}
    for entry in before.values():
        archived = backup / pathlib.PurePosixPath(entry["backup"])
        if not archived.is_file() or metadata.content_sha256(archived) != entry["sha256"]:
            raise ValueError(f"normal recovery snapshot changed: {archived}")
    before_relative = {
        pathlib.Path(source).relative_to(root).as_posix(): entry for source, entry in before.items()
    }
    for relative in set(before_relative) | set(data["after"]):
        target = safe(root, relative)
        if target.exists():
            accepted = {data["after"].get(relative)}
            if relative in before_relative:
                accepted.add(before_relative[relative]["sha256"])
            if not target.is_file() or metadata.content_sha256(target) not in accepted:
                raise ValueError(f"normal recovery refuses unexpected newer content: {relative}")
    for relative, entry in before_relative.items():
        _replace(
            backup / pathlib.PurePosixPath(entry["backup"]),
            safe(root, relative), entry["sha256"],
        )
        if relative in data.get("beforeModifiedNs", {}):
            target = safe(root, relative)
            os.utime(target, ns=(target.stat().st_atime_ns, data["beforeModifiedNs"][relative]))
    for relative, expected in data["after"].items():
        if relative not in before_relative:
            target = safe(root, relative)
            if target.exists():
                if metadata.content_sha256(target) != expected:
                    raise ValueError(f"normal recovery refuses changed generated file: {relative}")
                target.unlink()


def recover(root, journal, *, apply=False):
    data = verify(root, journal, applied=False)
    if data["status"] not in ("applied", "publishing", "rollback-failed", "rolled-back"):
        raise ValueError(f"normal transaction state cannot be recovered: {data['status']}")
    if data["status"] == "applied":
        verify(root, journal)
    if apply:
        _restore(pathlib.Path(root).resolve(), data)
        data["status"] = "undone"
        write(journal, data)
    return data


def publish(root, stage, source_relatives, *, journal, bindings, profile, run_id, expected_sources=None,
            expected_modified_ns=None,
            preserved_sources=None, finalizer=None, report_directories=()):
    from tools.art import library_backup

    root, stage = pathlib.Path(root).resolve(), pathlib.Path(stage).resolve()
    if root not in stage.parents:
        raise ValueError("normal publication staging must stay within its library")
    targets = {
        path.relative_to(stage).as_posix(): metadata.content_sha256(path)
        for path in stage.rglob("*") if path.is_file()
    }
    if any(safe(root, relative).exists() for relative in targets if relative.startswith("_duplicates/")):
        raise ValueError("normal duplicate archive target already exists")
    report_roots = [safe(root, relative) for relative in report_directories]
    report_before = {
        path.relative_to(root).as_posix()
        for directory in report_roots if directory.exists()
        for path in directory.rglob("*") if path.is_file()
    }
    before_paths = set(source_relatives) | set(preserved_sources or {}) | report_before | {
        relative for relative in targets if safe(root, relative).exists()
    }
    before = [(f"file-{index:04d}", safe(root, relative)) for index, relative in enumerate(sorted(before_paths))]
    def check_modified():
        for relative, modified_ns in (expected_modified_ns or {}).items():
            if safe(root, relative).stat().st_mtime_ns != modified_ns:
                raise ValueError(f"normal collision date changed before publication: {relative}")

    check_modified()
    for relative, checksum in {**(expected_sources or {}), **(preserved_sources or {})}.items():
        if metadata.content_sha256(safe(root, relative)) != checksum:
            raise ValueError(f"normal frozen source changed before snapshot: {relative}")
    backup = library_backup.create_backup(root, apply=True, scoped_sources=before)
    snapshot = json.loads((pathlib.Path(backup) / "manifest.json").read_text(encoding="utf-8"))
    frozen_sources = {entry["source"]: entry["sha256"] for entry in snapshot["entries"]}
    for source, checksum in frozen_sources.items():
        if metadata.content_sha256(pathlib.Path(source)) != checksum:
            raise ValueError(f"normal source changed after snapshot: {source}")
    check_modified()
    data = {
        "schemaVersion": 1, "kind": "normal-publication", "status": "publishing",
        "root": str(root), "runId": run_id, "profile": profile, "bindings": bindings,
        "backup": str(backup), "after": {**targets, **(preserved_sources or {})},
        "removed": sorted(set(source_relatives) - set(targets)),
        **({"beforeModifiedNs": {relative: expected_modified_ns[relative] for relative in before_paths
                                if relative in expected_modified_ns}} if expected_modified_ns else {}),
    }
    write(journal, data)
    try:
        for relative, checksum in targets.items():
            _replace(safe(stage, relative), safe(root, relative), checksum)
        for relative in data["removed"]:
            if metadata.content_sha256(safe(root, relative)) != frozen_sources[str(safe(root, relative))]:
                raise ValueError(f"normal source changed during publication: {relative}")
            safe(root, relative).unlink()
        if finalizer is not None:
            try:
                data["viewerPaths"] = finalizer()
            finally:
                report_after = {
                    path.relative_to(root).as_posix(): metadata.content_sha256(path)
                    for directory in report_roots if directory.exists()
                    for path in directory.rglob("*") if path.is_file()
                }
                data["after"].update(report_after)
                data["removed"] = sorted(set(data["removed"]) | (report_before - set(report_after)))
                write(journal, data)
        data["status"] = "applied"
        write(journal, data)
        verify(root, journal)
    except Exception as exc:
        try:
            _restore(root, data)
            data["status"] = "rolled-back"
        except Exception as rollback:
            data["status"] = "rollback-failed"
            data["rollbackError"] = str(rollback)
        data["error"] = str(exc)
        write(journal, data)
        raise OSError(f"normal publication failed ({data['status']}): {exc}; journal={journal}") from exc
    return pathlib.Path(journal)
