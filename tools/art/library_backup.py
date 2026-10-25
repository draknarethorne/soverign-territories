#!/usr/bin/env python3
"""Create a dated, integrity-manifested snapshot before photo-library changes.

  python tools/art/library_backup.py              preview the full snapshot
  python tools/art/library_backup.py --apply       copy it under <work>\\_backup

The snapshot includes the work root except prior backups and the work-root
archive, configured ComfyUI inputs and the repository workspace configuration.
Routine snapshots omit hash-verified People and Artist browser outputs, retaining
their manifests; restore requires rebuilding those views. --full keeps outputs.
ComfyUI output renders are not changed by the library pipeline and are not copied.
"""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
import comfy_workflows as cw  # noqa: E402

CHUNK_SIZE = 1024 * 1024


def generated_report_omissions(work):
    """Omit only unchanged, manifest-owned browser outputs, not report evidence."""
    work = pathlib.Path(work).resolve()
    omissions = {}
    for folder, manifest_name, recipe, pages, thumbnail_pattern in (
        ("artists", "gallery-manifest.json", "artists-gallery-v1",
         {"artists_gallery.html", "artists_gallery_review.html"},
         r"thumbnails/[0-9a-f]{64}\.jpg"),
        ("library", "people-gallery-manifest.json", "people-gallery-v1",
         {"people_gallery.html", "people_gallery_review.html", "people_gallery.md"},
         r"people_gallery_review_files/[A-Za-z0-9_.-]+_(?:chest|head|face)_[0-9a-f]{12}\.jpg"),
    ):
        omissions.update(_owned_report_omissions(
            work, folder, manifest_name, recipe, pages, thumbnail_pattern))
    return omissions


def _owned_report_omissions(work, folder, manifest_name, recipe, pages, thumbnail_pattern):
    report = work / "_reports" / folder
    manifest = report / manifest_name
    if any(path.is_symlink() for path in (work / "_reports", report, manifest)):
        return {}
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if (not isinstance(data, dict) or data.get("formatVersion") != 1
                or data.get("recipe") != recipe
                or not isinstance(data.get("files"), dict)):
            return {}
    except (OSError, ValueError):
        return {}
    omissions = {}
    for relative, expected in data["files"].items():
        if relative not in pages and not re.fullmatch(thumbnail_pattern, relative):
            continue
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            continue
        target = report / relative
        if target.is_symlink() or target.parent.is_symlink() or not target.is_file():
            continue
        try:
            before = target.stat()
            digest = hashlib.sha256()
            with target.open("rb") as stream:
                for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
                    digest.update(block)
            after = target.stat()
            if (digest.hexdigest() != expected or before.st_size != after.st_size
                    or before.st_mtime_ns != after.st_mtime_ns):
                continue
            key = target.relative_to(work).as_posix()
            omissions[key] = {
                "backup": (pathlib.Path("work-root") / key).as_posix(),
                "manifestBackup": (pathlib.Path("work-root") / manifest.relative_to(work)).as_posix(),
                "sha256": expected, "size": after.st_size, "recipe": data["recipe"],
            }
        except OSError:
            continue
    return omissions


def derivative_omissions(work):
    """Prove each exact managed file is reproducible before omitting any bytes."""
    from likeness_library import derivatives
    work = pathlib.Path(work).resolve()
    files = {relative.as_posix(): path for path, relative in _files(work, True)}
    omissions = {}
    for relative, manifest in files.items():
        if manifest.name != derivatives.MANIFEST:
            continue
        if any(part.casefold() in ("gallery_org", "gallery_intake") for part in manifest.relative_to(work).parts):
            continue
        try:
            data = derivatives.load(manifest.parent)
            for output, record in data["entries"].items():
                try:
                    source = (manifest.parent / record["source"]).resolve()
                    target = (manifest.parent / output).resolve()
                    if source.parent.name not in {"gallery", "review"} or source.parent.parent != manifest.parent:
                        continue
                    framing = next((mode for mode in ("padded", "head", "chest")
                                    if derivatives.relative_target(source, mode).as_posix() == output), None)
                    key = target.relative_to(work).as_posix()
                    source_key = source.relative_to(work).as_posix()
                    if (not framing or record.get("recipe") != derivatives.RECIPE
                            or key not in files or source_key not in files or source.is_symlink()
                            or derivatives.digest(source) != record["sourceSha256"]
                            or derivatives.digest(target) != record["sha256"]):
                        continue
                    payload = derivatives.render(source, framing, record.get("box"))
                    if hashlib.sha256(payload).hexdigest() != record["sha256"]:
                        continue
                    omissions[key] = {
                        "backup": (pathlib.Path("work-root") / key).as_posix(),
                        "sourceBackup": (pathlib.Path("work-root") / source_key).as_posix(),
                        "sourceSha256": record["sourceSha256"], "sha256": record["sha256"],
                        "recipe": derivatives.RECIPE, "framing": framing, "box": record.get("box"),
                        "size": len(payload), "mtimeNs": target.stat().st_mtime_ns,
                        "atimeNs": target.stat().st_atime_ns,
                    }
                except (OSError, ValueError, KeyError, TypeError):
                    continue
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return omissions


def _regenerated(root, manifest):
    from likeness_library import derivatives
    seen = {entry["backup"].replace("\\", "/") for entry in manifest.get("entries", [])}
    for entry in manifest.get("regenerable", []):
        target_relative = pathlib.Path(entry["backup"])
        source_relative = pathlib.Path(entry["sourceBackup"])
        target, source = (root / target_relative).resolve(), (root / source_relative).resolve()
        if (root not in target.parents or root not in source.parents or source.is_symlink()
                or target_relative.parts[0] != "work-root" or source_relative.parts[0] != "work-root"
                or target_relative.as_posix() in seen or not source.is_file()
                or entry.get("recipe") != derivatives.RECIPE
                or source.parent.name not in {"gallery", "review"}):
            raise OSError("unsafe or unsupported derivative recovery entry")
        if derivatives.relative_target(source, entry["framing"]) != target.relative_to(source.parent.parent):
            raise OSError("derivative recovery filename does not match recipe")
        if derivatives.digest(source) != entry["sourceSha256"]:
            raise OSError(f"derivative recovery source checksum mismatch: {source}")
        payload = derivatives.render(source, entry["framing"], entry.get("box"))
        if len(payload) != entry["size"] or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise OSError(f"derivative cannot be regenerated exactly: {target_relative}")
        seen.add(target_relative.as_posix())
        yield target_relative, payload, entry


def restore_backup(snapshot, destination, *, apply=False):
    """Materialize an exact work-root recovery tree into a new, empty destination."""
    verify_backup(snapshot)
    root = _snapshot_path(snapshot)
    destination = pathlib.Path(destination).expanduser().resolve()
    if destination.exists() or destination == root or root in destination.parents:
        raise ValueError("recovery destination must not exist and must be outside the snapshot")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("scope") == "transaction":
        raise ValueError("transaction snapshots require their action-specific recovery, not full restore")
    print(f"restore preview: {root} -> {destination}; new tree only, live library untouched")
    if not apply:
        return destination
    stage = destination.with_name(destination.name + ".restoring")
    if stage.exists():
        raise ValueError(f"recovery staging already exists: {stage}")
    try:
        shutil.copytree(root, _snapshot_path(stage))
        verify_backup(stage)
        for relative, payload, entry in _regenerated(stage.resolve(), manifest):
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            os.utime(target, ns=(entry["atimeNs"], entry["mtimeNs"]))
        (stage / "manifest.json").unlink()
        os.replace(stage, destination)
    except Exception:
        if stage.exists():
            shutil.rmtree(_snapshot_path(stage))
        raise
    print(f"recovery materialized: {destination}; original names, bytes and derivative hashes restored")
    if manifest.get("generatedReports"):
        print("  omitted generated browser files are not restored; regenerate from retained sources and metadata")
    return destination


def _snapshot_path(path):
    """Use extended Windows paths when nested backup copies exceed MAX_PATH."""
    path = pathlib.Path(path).resolve()
    if os.name != "nt" or str(path).startswith("\\\\?\\"):
        return path
    value = str(path)
    if value.startswith("\\\\"):
        return pathlib.Path("\\\\?\\UNC\\" + value[2:])
    return pathlib.Path("\\\\?\\" + value)


def _files(source, exclude_library_storage=False):
    """Yield regular files in deterministic order; refuse symlinks rather than omit data."""
    source = pathlib.Path(source)
    if source.is_file():
        if source.is_symlink():
            raise OSError(f"refusing to back up symbolic link: {source}")
        yield source, pathlib.Path(source.name)
        return
    if not source.is_dir():
        raise FileNotFoundError(f"backup source does not exist: {source}")
    for current, dirs, names in os.walk(source, followlinks=False):
        current_path = pathlib.Path(current)
        if exclude_library_storage and current_path == source:
            dirs[:] = [name for name in dirs if name.casefold() not in {"_backup", "_archive"}]
        for name in list(dirs):
            item = current_path / name
            if item.is_symlink():
                raise OSError(f"refusing to back up symbolic link: {item}")
        dirs.sort(key=str.casefold)
        for name in sorted(names, key=str.casefold):
            item = current_path / name
            if item.is_symlink():
                raise OSError(f"refusing to back up symbolic link: {item}")
            yield item, item.relative_to(source)


def _directories(source, exclude_library_storage=False):
    source = pathlib.Path(source)
    if not source.is_dir():
        return []
    out = [pathlib.Path()]
    for current, dirs, _names in os.walk(source, followlinks=False):
        current_path = pathlib.Path(current)
        if exclude_library_storage and current_path == source:
            dirs[:] = [name for name in dirs if name.casefold() not in {"_backup", "_archive"}]
        for name in list(dirs):
            item = current_path / name
            if item.is_symlink():
                raise OSError(f"refusing to back up symbolic link: {item}")
        dirs.sort(key=str.casefold)
        out.extend((current_path / name).relative_to(source) for name in dirs)
    return out


def sources(work_root, inputs_root=None, config_path=None, extra_sources=()):
    work = pathlib.Path(work_root).resolve()
    result = [("work-root", work, True)]
    if inputs_root:
        inputs = pathlib.Path(inputs_root).resolve()
        if inputs != work and work not in inputs.parents and inputs not in work.parents:
            result.append(("comfy-inputs", inputs, False))
    if config_path:
        result.append(("repository-config", pathlib.Path(config_path).resolve(), False))
    for label, source in extra_sources:
        if any(existing == label for existing, _path, _exclude in result):
            raise ValueError(f"duplicate backup source label: {label}")
        result.append((label, pathlib.Path(source).resolve(), False))
    return result


def preview(work_root, inputs_root=None, config_path=None, extra_sources=()):
    entries, total = [], 0
    source_list = sources(work_root, inputs_root, config_path, extra_sources)
    omissions = derivative_omissions(work_root)
    report_omissions = generated_report_omissions(work_root)
    for label, source, exclude_library_storage in source_list:
        for path, relative in _files(source, exclude_library_storage):
            if label == "work-root" and (relative.as_posix() in omissions
                                         or relative.as_posix() in report_omissions):
                continue
            size = path.stat().st_size
            entries.append((label, path, relative, size))
            total += size
    print(f"snapshot preview: {len(entries)} file(s), {total:,} bytes")
    for label, source, _ in source_list:
        print(f"  {label}: {source}")
    print("  excluded from work-root: _backup, _archive")
    print(f"  omitted {len(omissions)} exactly reproducible managed derivatives; edited/unproven files retained")
    print(f"  omitted {len(report_omissions)} hash-verified generated browser files; report manifest retained")
    print("  destination: <work-root>\\_backup\\library-<timestamp>")
    return entries, total


def verify_backup(snapshot):
    """Verify manifest coverage, byte counts and hashes for a completed snapshot."""
    root = _snapshot_path(snapshot)
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise OSError(f"no completed backup manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete":
        raise OSError(f"backup is not marked complete: {root}")
    expected, total = set(), 0
    for entry in manifest.get("entries", []):
        relative = pathlib.Path(entry["backup"])
        target = (root / relative).resolve()
        if root not in target.parents or not target.is_file() or target.is_symlink():
            raise OSError(f"missing or unsafe backup file: {relative}")
        if target.stat().st_size != entry["size"]:
            raise OSError(f"backup size mismatch: {relative}")
        digest = hashlib.sha256()
        with target.open("rb") as stream:
            for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
                digest.update(block)
        if digest.hexdigest() != entry["sha256"]:
            raise OSError(f"backup checksum mismatch: {relative}")
        expected.add(relative.as_posix())
        total += entry["size"]
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path != manifest_path
    }
    if actual != expected:
        raise OSError(f"backup file-list mismatch: {root}")
    regenerated = sum(1 for _ in _regenerated(root, manifest))
    if regenerated:
        print(f"  verified exact regeneration: {regenerated} omitted derivative(s)")
    print(f"snapshot verified: {len(expected)} file(s), {total:,} bytes")
    print(f"  backup: {root}")
    return True


def latest_work_root_backup(work_root):
    """Return the newest complete snapshot that includes this exact work root."""
    work = pathlib.Path(work_root).expanduser().resolve()
    backup_root = work / "_backup"
    if not backup_root.is_dir():
        raise OSError(f"no backup directory exists for work root: {work}")
    candidates = sorted(
        (path for path in backup_root.iterdir() if path.is_dir() and path.name.startswith("library-")),
        key=lambda path: path.name,
        reverse=True,
    )
    for candidate in candidates:
        manifest_path = candidate / "manifest.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if manifest.get("status") != "complete":
            continue
        sources_list = manifest.get("sources", [])
        if any(
            entry.get("name") == "work-root"
            and pathlib.Path(entry.get("path", "")).expanduser().resolve() == work
            for entry in sources_list
            if isinstance(entry, dict)
        ):
            return candidate
    raise OSError(f"no complete backup exists for work root: {work}")


def create_backup(work_root, inputs_root=None, config_path=None, stamp=None, apply=True, extra_sources=(),
                  *, scoped_sources=None, recovery=None, include_regenerable=False):
    """Preview or create a complete snapshot; publish its manifest only after all copies verify."""
    work = pathlib.Path(work_root).resolve()
    if scoped_sources is None:
        source_list = sources(work, inputs_root, config_path, extra_sources)
    else:
        source_list = [(label, pathlib.Path(path).resolve(), False) for label, path in scoped_sources]
        if not source_list or len({label for label, _, _ in source_list}) != len(source_list):
            raise ValueError("scoped backup requires nonempty, uniquely named sources")
        if any(not label or pathlib.Path(label).name != label or label in (".", "..")
               or any(char in label for char in "\\/:") for label, _, _ in source_list):
            raise ValueError("unsafe scoped backup source label")
    entries, total = [], 0
    omissions = (
        derivative_omissions(work)
        if scoped_sources is None and not include_regenerable
        else {}
    )
    report_omissions = (
        generated_report_omissions(work)
        if scoped_sources is None and not include_regenerable
        else {}
    )
    for label, source, exclude in source_list:
        for path, relative in _files(source, exclude):
            if label == "work-root" and (relative.as_posix() in omissions
                                         or relative.as_posix() in report_omissions):
                continue
            size = path.stat().st_size
            entries.append((label, path, relative, size))
            total += size
    print(f"snapshot preview: {len(entries)} file(s), {total:,} bytes", flush=True)
    for label, source, _ in source_list:
        print(f"  {label}: {source}", flush=True)
    if scoped_sources is None:
        print("  excluded from work-root: _backup, _archive")
        if include_regenerable:
            print("  backup mode: full (includes managed derivatives and generated browser files)")
        else:
            print(f"  omitted {len(omissions)} exactly reproducible managed derivatives; edited/unproven files retained")
            print(f"  omitted {len(report_omissions)} hash-verified generated browser files; regenerate after restore")
    else:
        print("  scope: explicit transaction sources; not a full-library snapshot")
    if not apply:
        return None

    stamp = stamp or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = work / "_backup" / f"library-{stamp}"
    snapshot = _snapshot_path(destination)
    snapshot.mkdir(parents=True, exist_ok=False)
    required = total + 256 * 1024 * 1024
    free = shutil.disk_usage(destination.parent).free
    if free < required:
        marker = destination / "INCOMPLETE.txt"
        marker.write_text(
            f"Insufficient space: need approximately {required:,} bytes; available {free:,}.\n",
            encoding="utf-8",
        )
        raise OSError(f"insufficient space for full backup: need about {required:,} bytes; have {free:,}")

    manifest_files = []
    try:
        root_map = {label: source for label, source, _ in source_list}
        for label, source, exclude_library_storage in source_list:
            if source.is_dir():
                for relative in _directories(source, exclude_library_storage):
                    (snapshot / label / relative).mkdir(parents=True, exist_ok=True)
        for label, source_file, relative, expected_size in entries:
            source_root = root_map[label]
            target = snapshot / label / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            before = source_file.stat()
            digest = hashlib.sha256()
            copied = 0
            with source_file.open("rb") as src, target.open("xb") as dst:
                while True:
                    block = src.read(CHUNK_SIZE)
                    if not block:
                        break
                    dst.write(block)
                    digest.update(block)
                    copied += len(block)
            shutil.copystat(source_file, target)
            after = source_file.stat()
            if copied != expected_size or before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns:
                raise OSError(f"source changed while backing up: {source_file}")
            if target.stat().st_size != copied:
                raise OSError(f"backup size verification failed: {target}")
            manifest_files.append({
                "source": str(source_file),
                "backup": str(target.relative_to(snapshot)),
                "size": copied,
                "sha256": digest.hexdigest(),
            })

        for label, source, exclude_library_storage in source_list:
            current = {
                (relative.as_posix(), path.stat().st_size)
                for path, relative in _files(source, exclude_library_storage)
                if not (label == "work-root" and (relative.as_posix() in omissions
                                                  or relative.as_posix() in report_omissions))
            }
            expected = {
                (relative.as_posix(), size)
                for entry_label, _path, relative, size in entries
                if entry_label == label
            }
            if current != expected:
                raise OSError(f"source file list changed while backing up: {source}")
        if scoped_sources is None and not include_regenerable:
            checked = derivative_omissions(work)
            def stable(records):
                return {key: {k: v for k, v in value.items() if k != "atimeNs"}
                        for key, value in records.items()}
            if stable(checked) != stable(omissions):
                raise OSError("managed derivative proof changed during backup")
            if generated_report_omissions(work) != report_omissions:
                raise OSError("generated browser ownership proof changed during backup")

        manifest = {
            "status": "complete",
            "created": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "snapshot": str(destination),
            "files": len(manifest_files),
            "bytes": sum(entry["size"] for entry in manifest_files),
            "sources": [
                {"name": label, "path": str(source), "exclude_library_storage": exclude}
                for label, source, exclude in source_list
            ],
            "entries": manifest_files,
            "regenerable": list(omissions.values()),
            "generatedReports": list(report_omissions.values()),
        }
        if scoped_sources is not None:
            manifest["scope"] = "transaction"
            manifest["recovery"] = recovery
        temporary = destination / "manifest.json.tmp"
        temporary.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        temporary.replace(destination / "manifest.json")
        verify_backup(destination)
    except Exception as exc:
        manifest_path = destination / "manifest.json"
        if manifest_path.is_file():
            failed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            failed_manifest["status"] = "incomplete"
            failed_manifest["error"] = str(exc)
            manifest_path.write_text(json.dumps(failed_manifest, indent=2), encoding="utf-8")
        (destination / "INCOMPLETE.txt").write_text(f"Backup incomplete: {exc}\n", encoding="utf-8")
        raise

    print(f"snapshot complete: {len(manifest_files)} file(s), {manifest['bytes']:,} bytes")
    print(f"  backup: {destination}")
    print(f"  manifest: {destination / 'manifest.json'}")
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="create the snapshot (default: preview only)")
    parser.add_argument("--verify", metavar="SNAPSHOT", help="verify a completed snapshot's file list and SHA-256 hashes")
    parser.add_argument("--restore", metavar="SNAPSHOT", help="materialize full recovery into a new destination")
    parser.add_argument("--destination", help="new nonexisting recovery directory; live data is never overwritten")
    parser.add_argument("--full", action="store_true",
                        help="include managed derivatives and generated browser files (complete monthly snapshots)")
    parser.add_argument("--root", help="photo library root (default: workspaces.json paths.workRoot)")
    parser.add_argument("--inputs", help="ComfyUI inputs root (default: workspaces.json paths.inputsRoot)")
    args = parser.parse_args(argv)
    if args.restore:
        if not args.destination:
            parser.error("--restore requires --destination")
        try:
            restore_backup(args.restore, args.destination, apply=args.apply)
        except (OSError, ValueError, KeyError) as exc:
            print(f"restore failed: {exc}", file=sys.stderr)
            return 1
        return 0
    if args.verify:
        try:
            verify_backup(args.verify)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            print(f"backup verification failed: {exc}", file=sys.stderr)
            return 1
        return 0
    cfg = cw.load_cfg()
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    inputs = args.inputs if args.inputs else cfg.get("paths", {}).get("inputsRoot")
    config = ROOT / "workflows" / "workspaces.json"
    try:
        create_backup(work, inputs, config, apply=args.apply, include_regenerable=args.full)
    except (OSError, ValueError) as exc:
        print(f"backup failed: {exc}", file=sys.stderr)
        return 1
    if not args.apply:
        print("preview only; add --apply to create the snapshot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
