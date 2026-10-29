"""Guarded reset helpers for the disposable likeness sandbox."""
import collections
import hashlib
import json
import os
import pathlib
import re
import shutil
import stat
import sys
import time
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.art import temporary_storage  # noqa: E402
from tools.workflows import comfy_workflows as cw  # noqa: E402

RESET_CATEGORIES = ("Models", "Prospects", "Potentials")
CHUNK_SIZE = 1024 * 1024
FULL_RESET_STAGE_PREFIX = "full-reset-stage-"
RESERVED_PRODUCTION_ROOTS = {"_archive"}
PRESERVED_PHOTO_STORAGE_ROOTS = {"junk", "retired"}


def is_sandbox_working_path(path):
    path = pathlib.Path(path).expanduser().resolve(strict=False)
    return (
        path.name.casefold() == "working"
        and path.parent.name.casefold() == "sovereign territories sandbox"
    )


def _require_inside_working(working_root, target, label):
    working_root = pathlib.Path(working_root).expanduser().resolve(strict=True)
    target = pathlib.Path(target).expanduser().resolve(strict=False)
    if working_root != target and working_root not in target.parents:
        raise ValueError(f"sandbox {label} must stay inside Working: {target}")
    return target


def require_sandbox_cache(working_root, cache_path):
    if not cache_path:
        raise ValueError("sandbox commands require an explicit Working-local --cache")
    return _require_inside_working(working_root, cache_path, "cache")


def require_sandbox_output(working_root, output_path):
    return _require_inside_working(working_root, output_path, "output")


def _overlaps(first, second):
    return first == second or first in second.parents or second in first.parents


def _is_reparse_point(path):
    if path.is_symlink():
        return True
    try:
        attributes = path.lstat().st_file_attributes
    except FileNotFoundError:
        return False
    except AttributeError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _remove_tree(path):
    from tools.art.library_backup import _snapshot_path

    def clear_readonly(function, target, error_info):
        error = error_info[1]
        if not isinstance(error, PermissionError):
            raise error
        os.chmod(target, stat.S_IREAD | stat.S_IWRITE)
        function(target)

    shutil.rmtree(_snapshot_path(path), onerror=clear_readonly)


def _safe_source_path(relative):
    if not isinstance(relative, str) or "\\" in relative or ":" in relative:
        raise ValueError(f"invalid source-manifest path: {relative!r}")
    path = pathlib.PurePosixPath(relative)
    parts = relative.split("/")
    if (
        path.is_absolute()
        or not path.parts
        or any(part in ("", ".", "..") for part in parts)
    ):
        raise ValueError(f"invalid source-manifest path: {relative!r}")
    return path.parts


def _source_files(root):
    def raise_walk_error(error):
        raise error

    for current, directories, names in os.walk(
        root, followlinks=False, onerror=raise_walk_error
    ):
        current_path = pathlib.Path(current)
        for name in list(directories):
            path = current_path / name
            if _is_reparse_point(path):
                raise ValueError(f"refusing reparse point in source snapshot: {path}")
        directories.sort(key=str.casefold)
        for name in sorted(names, key=str.casefold):
            path = current_path / name
            if _is_reparse_point(path) or not path.is_file():
                raise ValueError(f"refusing non-regular source file: {path}")
            yield path


def _file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_inventory(root, hash_files, excluded_roots=()):
    inventory = {}
    excluded_roots = {
        tuple(pathlib.PurePosixPath(item).parts)
        if isinstance(item, str)
        else tuple(item)
        for item in excluded_roots
    }
    file_count = 0
    total_bytes = 0
    excluded_count = 0
    excluded_bytes = 0
    for path in _source_files(root):
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        file_count += 1
        total_bytes += size
        parts = pathlib.PurePosixPath(relative).parts
        if any(parts[:len(prefix)] == prefix for prefix in excluded_roots):
            excluded_count += 1
            excluded_bytes += size
            continue
        inventory[relative] = {
            "bytes": size,
            "sha256": _file_digest(path) if hash_files else None,
        }
    return inventory, file_count, total_bytes, excluded_count, excluded_bytes


def validate_sandbox(working_root):
    """Validate layout and the immutable source snapshot before any reset."""
    started = time.perf_counter()
    working_root = pathlib.Path(working_root).expanduser()
    if not working_root.is_absolute():
        raise ValueError("sandbox reset requires an explicit absolute --root")
    if working_root.name.casefold() != "working":
        raise ValueError("sandbox reset root must be the sandbox's Working directory")
    sandbox_root = working_root.parent
    if sandbox_root.name.casefold() != "sovereign territories sandbox":
        raise ValueError("sandbox reset requires a 'Sovereign Territories Sandbox\\Working' path")

    for path in (sandbox_root, working_root):
        if _is_reparse_point(path) or not path.is_dir():
            raise ValueError(f"missing or unsafe sandbox directory: {path}")
    sandbox_root = sandbox_root.resolve(strict=True)
    working_root = working_root.resolve(strict=True)
    if (
        sandbox_root.name.casefold() != "sovereign territories sandbox"
        or working_root.name.casefold() != "working"
        or working_root.parent != sandbox_root
    ):
        raise ValueError("resolved paths do not preserve the required sandbox layout")
    source_root = sandbox_root / "Source"
    manifest_path = sandbox_root / "source-manifest.json"
    if _is_reparse_point(source_root) or not source_root.is_dir():
        raise ValueError(f"missing or unsafe immutable source snapshot: {source_root}")
    if _is_reparse_point(manifest_path) or not manifest_path.is_file():
        raise ValueError(f"missing or unsafe source manifest: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schemaVersion") != 1
        or manifest.get("snapshotRoot") != "Source"
        or manifest.get("workingRootAtCreation") != "Working"
    ):
        raise ValueError("unsupported or mismatched sandbox source manifest")
    production_root = pathlib.Path(manifest.get("sourceRoot", "")).expanduser()
    if not production_root.is_absolute():
        raise ValueError("source manifest must identify an absolute production sourceRoot")
    production_root = production_root.resolve(strict=False)
    if (
        production_root.name.casefold() != "sovereign territories"
        or production_root.parent != sandbox_root.parent
        or any(parent.name.casefold() == "sovereign territories" for parent in sandbox_root.parents)
    ):
        raise ValueError("sandbox must be a sibling of the named production library")
    if _overlaps(production_root, sandbox_root):
        raise ValueError("sandbox overlaps the production sourceRoot")

    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ValueError("source manifest files must be a list")
    expected = {}
    expected_bytes = 0
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("invalid source manifest file entry")
        relative = entry.get("path")
        _safe_source_path(relative)
        size = entry.get("bytes")
        digest = entry.get("sha256")
        if not isinstance(size, int) or size < 0:
            raise ValueError(f"invalid source-manifest size: {relative!r}")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"invalid source-manifest checksum: {relative!r}")
        if relative in expected:
            raise ValueError(f"duplicate source-manifest path: {relative!r}")
        expected[relative] = (size, digest)
        expected_bytes += size

    if len(expected) != manifest.get("fileCount") or expected_bytes != manifest.get("totalBytes"):
        raise ValueError("source manifest file count or byte total is inconsistent")

    actual_paths = set()
    actual_bytes = 0
    for path in _source_files(source_root):
        relative = path.relative_to(source_root).as_posix()
        if relative not in expected:
            raise ValueError(f"unlisted file in source snapshot: {relative}")
        expected_size, expected_digest = expected[relative]
        size = path.stat().st_size
        if size != expected_size:
            raise ValueError(f"source snapshot size mismatch: {relative}")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
                digest.update(block)
        if digest.hexdigest() != expected_digest:
            raise ValueError(f"source snapshot checksum mismatch: {relative}")
        actual_paths.add(relative)
        actual_bytes += size
    if actual_paths != set(expected):
        missing = sorted(set(expected) - actual_paths)
        raise ValueError(f"source snapshot is missing manifest file(s): {', '.join(missing[:5])}")

    return {
        "sandbox_root": sandbox_root,
        "working_root": working_root,
        "source_root": source_root.resolve(strict=True),
        "production_root": production_root,
        "file_count": len(actual_paths),
        "total_bytes": actual_bytes,
        "manifest_files": expected,
        "verification_seconds": time.perf_counter() - started,
    }


def _configured_storage_paths(cfg, root):
    return {
        name: cw.storage_root(cfg, name, root=root)
        for name in cw.STORAGE_ROOT_DEFAULTS
    }


def _full_reset_analysis(working_root, production_root=None, cfg=None, layout=None):
    """Build the verified copy plan used by preview and full reset apply."""
    layout = validate_sandbox(working_root) if layout is None else layout
    working = layout["working_root"]
    cfg = cw.load_cfg() if cfg is None else cfg
    configured_production = (
        layout["production_root"]
        if production_root is None
        else pathlib.Path(production_root).expanduser()
    )
    if _is_reparse_point(configured_production):
        raise ValueError(f"refusing reparse point for production library: {configured_production}")
    production = configured_production.resolve(strict=True)
    if production != layout["production_root"]:
        raise ValueError(
            "configured production root does not match the verified sandbox manifest"
        )
    if _is_reparse_point(production) or not production.is_dir():
        raise ValueError(f"missing or unsafe production library: {production}")

    production_storage_paths = _configured_storage_paths(cfg, production)
    excluded_storage_roots = {
        tuple(pathlib.PurePosixPath(root).parts)
        for root in RESERVED_PRODUCTION_ROOTS
    } | {
        tuple(path.relative_to(production).parts)
        for name, path in production_storage_paths.items()
        if name not in PRESERVED_PHOTO_STORAGE_ROOTS
    }
    (
        production_files,
        production_count,
        production_bytes,
        excluded_production_count,
        excluded_production_bytes,
    ) = _tree_inventory(
        production,
        hash_files=True,
        excluded_roots=excluded_storage_roots,
    )
    working_files, working_count, working_bytes, _, _ = _tree_inventory(
        working, hash_files=False
    )
    active_roots = set(cw.PHOTO_ROOTS)
    active_working = {}
    active_production = {}

    for relative, entry in working_files.items():
        if pathlib.PurePosixPath(relative).parts[0] in active_roots:
            path = working / pathlib.Path(relative)
            active_working[relative] = {
                "bytes": entry["bytes"],
                "sha256": _file_digest(path),
            }

    for relative, entry in production_files.items():
        if pathlib.PurePosixPath(relative).parts[0] in active_roots:
            active_production[relative] = entry

    production_active_hashes = {
        entry["sha256"] for entry in active_production.values()
    }
    image_extensions = {
        ".avif", ".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"
    }
    carry_forward = []
    for relative, entry in sorted(active_working.items(), key=lambda item: item[0].casefold()):
        production_at_path = active_production.get(relative)
        if production_at_path and (
            production_at_path["bytes"] == entry["bytes"]
            and production_at_path["sha256"] == entry["sha256"]
        ):
            continue
        if production_at_path is None and entry["sha256"] in production_active_hashes:
            status = "already-present-at-different-active-path"
            destination = None
        elif production_at_path is not None:
            status = "path-conflict-review-required"
            destination = f"_reports/reset-review-bundle/path-conflicts/{relative}"
        elif pathlib.PurePosixPath(relative).suffix.casefold() in image_extensions:
            status = "carry-forward-active-photo"
            destination = relative
        else:
            status = "review-bundle-metadata"
            destination = f"_reports/reset-review-bundle/{relative}"
        carry_forward.append({
            "path": relative,
            "bytes": entry["bytes"],
            "sha256": entry["sha256"],
            "status": status,
            "destination": destination,
        })

    source_files = layout["manifest_files"]
    source_roots = {relative.split("/", 1)[0] for relative in source_files}
    preserved_storage_roots = {
        path.relative_to(production).parts[0]
        for name, path in production_storage_paths.items()
        if name in PRESERVED_PHOTO_STORAGE_ROOTS
    }
    known_production_roots = (
        source_roots | active_roots | preserved_storage_roots
    )
    unexpected_production_roots = sorted(
        {
            pathlib.PurePosixPath(relative).parts[0]
            for relative in production_files
            if pathlib.PurePosixPath(relative).parts[0] not in known_production_roots
        },
        key=str.casefold,
    )
    production_added = sorted(set(production_files) - set(source_files), key=str.casefold)
    production_removed = sorted(set(source_files) - set(production_files), key=str.casefold)
    production_changed = sorted(
        (
            relative for relative in set(source_files) & set(production_files)
            if source_files[relative]
            != (production_files[relative]["bytes"], production_files[relative]["sha256"])
        ),
        key=str.casefold,
    )
    counts = collections.Counter(entry["status"] for entry in carry_forward)
    reset_blockers = []
    if unexpected_production_roots:
        reset_blockers.append("unclassified-production-roots")
    if counts["path-conflict-review-required"]:
        reset_blockers.append("active-path-conflicts")
    temporary_root = cw.storage_root(cfg, "temporary", root=working)
    transaction_path = temporary_root / "full-reset-transaction.json"
    if transaction_path.exists():
        reset_blockers.append("unfinished-full-reset-transaction")
    result = {
        "schemaVersion": 1,
        "previewOnly": True,
        "resetReady": not reset_blockers,
        "resetBlockers": reset_blockers,
        "resetTarget": str(working),
        "productionRoot": str(production),
        "verifiedSourceSnapshot": {
            "root": str(layout["source_root"]),
            "fileCount": layout["file_count"],
            "totalBytes": layout["total_bytes"],
            "verificationSeconds": round(layout["verification_seconds"], 3),
        },
        "currentProduction": {
            "managedFileCount": len(production_files),
            "managedBytes": sum(entry["bytes"] for entry in production_files.values()),
            "wholeRootFileCount": production_count,
            "wholeRootBytes": production_bytes,
            "excludedStorageRoots": sorted(
                "/".join(parts) for parts in excluded_storage_roots
            ),
            "excludedStorageFileCount": excluded_production_count,
            "excludedStorageBytes": excluded_production_bytes,
            "fileCount": len(production_files),
            "totalBytes": sum(entry["bytes"] for entry in production_files.values()),
            "activeFileCount": len(active_production),
            "activeBytes": sum(entry["bytes"] for entry in active_production.values()),
            "addedSinceSnapshot": len(production_added),
            "removedSinceSnapshot": len(production_removed),
            "changedSinceSnapshot": len(production_changed),
            "addedPaths": production_added,
            "removedPaths": production_removed,
            "changedPaths": production_changed,
            "unexpectedTopLevelRoots": unexpected_production_roots,
        },
        "workingBeforeReset": {
            "fileCount": working_count,
            "totalBytes": working_bytes,
            "activeFileCount": len(active_working),
            "activeBytes": sum(entry["bytes"] for entry in active_working.values()),
        },
        "workingActiveFiles": carry_forward,
        "carryForwardCounts": dict(sorted(counts.items())),
    }
    return result, {
        "layout": layout,
        "working": working,
        "production": production,
        "production_files": production_files,
        "production_storage_paths": production_storage_paths,
        "excluded_storage_roots": excluded_storage_roots,
        "carry_forward": carry_forward,
        "temporary_root": temporary_root,
    }


def full_reset_preview(working_root, production_root=None, cfg=None):
    """Compare current Production with Working and list active files needing carry-forward."""
    result, _plan = _full_reset_analysis(working_root, production_root, cfg=cfg)
    return result


def _copy_verified_file(source, destination, expected_bytes, expected_digest):
    source = pathlib.Path(source)
    destination = pathlib.Path(destination)
    if _is_reparse_point(source) or not source.is_file():
        raise ValueError(f"refusing missing or linked reset input: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    copied_bytes = 0
    with source.open("rb") as input_stream, destination.open("xb") as output_stream:
        for block in iter(lambda: input_stream.read(CHUNK_SIZE), b""):
            output_stream.write(block)
            digest.update(block)
            copied_bytes += len(block)
    if copied_bytes != expected_bytes or digest.hexdigest() != expected_digest:
        raise ValueError(f"reset input changed while copying: {source}")
    shutil.copystat(source, destination, follow_symlinks=False)


def _write_json_file(path, data):
    content = (json.dumps(data, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return {
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _write_reset_journal(path, data):
    path = pathlib.Path(path)
    temporary = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write((json.dumps(data, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _simple_entry_names(names, field):
    if not isinstance(names, list) or any(not isinstance(name, str) for name in names):
        raise ValueError(f"invalid reset transaction {field}")
    if len(names) != len(set(names)):
        raise ValueError(f"invalid reset transaction {field}")
    for name in names:
        if (
            not name
            or name in (".", "..")
            or "/" in name
            or "\\" in name
            or ":" in name
        ):
            raise ValueError(f"invalid reset transaction {field}: {name!r}")
    return names


def _rollback_full_reset(working, stage, journal):
    staged = stage / "new"
    previous = stage / "rollback" / "old"
    old_entries = set(journal["oldEntries"])
    for name in reversed(journal["newEntries"]):
        source = staged / name
        destination = working / name
        old = previous / name
        if source.exists():
            if name not in old_entries and destination.exists():
                raise ValueError(f"unexpected path blocks reset rollback: {destination}")
            if name in old_entries and old.exists() and destination.exists():
                raise ValueError(f"ambiguous paths block reset rollback: {destination}")
            continue
        if not destination.exists():
            raise ValueError(f"missing reset entry blocks rollback: {destination}")
        if name in old_entries and not old.exists():
            raise ValueError(f"missing previous reset entry blocks rollback: {old}")
        destination.rename(source)
    for name in reversed(journal["oldEntries"]):
        source = previous / name
        destination = working / name
        if source.exists():
            if destination.exists():
                raise ValueError(f"ambiguous paths block reset rollback: {destination}")
            source.rename(destination)
        elif not destination.exists():
            raise ValueError(f"missing previous Working entry: {destination}")


def _recover_full_reset(temporary_root, working):
    temporary_root = pathlib.Path(temporary_root)
    journal_path = temporary_root / "full-reset-transaction.json"
    if not journal_path.exists():
        return False
    if _is_reparse_point(journal_path) or not journal_path.is_file():
        raise ValueError(f"refusing unsafe full reset journal: {journal_path}")
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    if (
        journal.get("schemaVersion") != 1
        or pathlib.Path(journal.get("target", "")).resolve(strict=False) != working
        or journal.get("phase") not in {"swapping", "committed"}
    ):
        raise ValueError(f"invalid or mismatched full reset journal: {journal_path}")
    stage_name = journal.get("stageName")
    _simple_entry_names([stage_name], "stageName")
    if not stage_name.startswith(FULL_RESET_STAGE_PREFIX):
        raise ValueError(f"invalid full reset stage name: {stage_name!r}")
    old_entries = _simple_entry_names(journal.get("oldEntries"), "oldEntries")
    new_entries = _simple_entry_names(journal.get("newEntries"), "newEntries")
    stage = temporary_root / stage_name
    lock_path = stage.with_name(stage.name + ".lock")
    if _is_reparse_point(stage) or _is_reparse_point(lock_path) or not lock_path.is_file():
        raise ValueError(f"missing or unsafe full reset recovery lock: {lock_path}")

    remove_lock = False
    with lock_path.open("r+b") as lock:
        temporary_storage._ensure_lock_byte(lock)
        if not temporary_storage._lock(lock):
            raise RuntimeError(f"full reset is still active; recovery is blocked: {stage}")
        try:
            if journal["phase"] == "committed":
                previous = stage / "rollback"
                if previous.exists():
                    _remove_tree(previous)
            else:
                if not stage.is_dir():
                    raise ValueError(f"full reset recovery stage is missing: {stage}")
                _rollback_full_reset(working, stage, journal)
            journal_path.unlink()
            if stage.exists():
                _remove_tree(stage)
            remove_lock = not stage.exists()
        finally:
            temporary_storage._unlock(lock)
    if remove_lock:
        lock_path.unlink(missing_ok=True)
    return journal["phase"]


def _require_empty_reset_temporary_root(temporary_root):
    if _is_reparse_point(temporary_root):
        raise ValueError(f"refusing reparse point for reset staging root: {temporary_root}")
    if temporary_root.exists() and not temporary_root.is_dir():
        raise ValueError(f"reset staging root is not a directory: {temporary_root}")
    if not temporary_root.exists():
        return
    removed = temporary_storage.clean_orphaned_staging(
        temporary_root, FULL_RESET_STAGE_PREFIX
    )
    for orphan in removed:
        print(f"Removed orphaned full-reset staging directory: {orphan}", flush=True)
    remaining = list(temporary_root.iterdir())
    if remaining:
        names = ", ".join(sorted(path.name for path in remaining)[:10])
        raise ValueError(
            f"reset temporary root contains unclassified files; review before reset: "
            f"{temporary_root} ({names})"
        )


def full_reset_apply(
    working_root,
    production_root=None,
    cfg=None,
    storage_receipt=None,
):
    """Replace only sandbox Working with the verified current Production baseline."""
    cfg = cw.load_cfg() if cfg is None else cfg
    layout = validate_sandbox(working_root)
    working = layout["working_root"]
    temporary_root = cw.storage_root(cfg, "temporary", root=working)
    if temporary_root.parent != working:
        raise ValueError("full reset staging root must be a direct child of Working")
    if temporary_root.exists():
        recovered_phase = _recover_full_reset(temporary_root, working)
        if recovered_phase == "committed":
            receipt_path = (
                cw.storage_root(cfg, "reports", root=working)
                / "reset-review-bundle"
                / "full-reset-receipt.json"
            )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            return {
                "previewOnly": False,
                "applied": True,
                "recoveredCommittedReset": True,
                "resetTarget": str(working),
                "productionFileCount": receipt["productionFileCount"],
                "productionBytes": receipt["productionBytes"],
                "carryForwardCounts": receipt["carryForwardCounts"],
                "receipt": str(receipt_path),
            }
    _require_empty_reset_temporary_root(temporary_root)

    result, plan = _full_reset_analysis(
        working_root, production_root, cfg=cfg, layout=layout
    )
    if not result["resetReady"]:
        blockers = ", ".join(result["resetBlockers"])
        raise ValueError(f"full sandbox reset is blocked: {blockers}")
    if plan["temporary_root"] != temporary_root:
        raise ValueError("full reset staging root changed during validation")

    storage_roots = _configured_storage_paths(cfg, working)
    temporary_relative = temporary_root.relative_to(working)
    report_relative = plan["production_storage_paths"]["reports"].relative_to(
        plan["production"]
    )
    journal_path = temporary_root / "full-reset-transaction.json"
    applied_result = dict(result)
    applied_result["previewOnly"] = False
    applied_result["applied"] = True
    copied = {
        relative: {
            "bytes": entry["bytes"],
            "sha256": entry["sha256"],
        }
        for relative, entry in plan["production_files"].items()
    }

    with temporary_storage.staging_directory(
        temporary_root,
        FULL_RESET_STAGE_PREFIX,
        preserve_on_error=True,
    ) as stage:
        staged = stage / "new"
        previous = stage / "rollback" / "old"
        staged.mkdir()
        previous.mkdir(parents=True)
        journal = None
        journal_written = False
        try:
            for relative, entry in sorted(
                plan["production_files"].items(),
                key=lambda item: item[0].casefold(),
            ):
                source = plan["production"] / pathlib.Path(*_safe_source_path(relative))
                destination = staged / pathlib.Path(*_safe_source_path(relative))
                _copy_verified_file(
                    source, destination, entry["bytes"], entry["sha256"]
                )

            for entry in plan["carry_forward"]:
                if entry["status"] in {
                    "already-present-at-different-active-path",
                }:
                    continue
                if entry["status"] not in {
                    "carry-forward-active-photo",
                    "review-bundle-metadata",
                }:
                    raise ValueError(
                        f"unapproved carry-forward status: {entry['status']}"
                    )
                source = working / pathlib.Path(*_safe_source_path(entry["path"]))
                destination = staged / pathlib.Path(
                    *_safe_source_path(entry["destination"])
                )
                _copy_verified_file(
                    source, destination, entry["bytes"], entry["sha256"]
                )
                copied[entry["destination"]] = {
                    "bytes": entry["bytes"],
                    "sha256": entry["sha256"],
                }

            for name, root in storage_roots.items():
                relative = root.relative_to(working)
                if relative == temporary_relative:
                    continue
                (staged / relative).mkdir(parents=True, exist_ok=True)

            receipt_path = (
                staged
                / report_relative
                / "reset-review-bundle"
                / "full-reset-receipt.json"
            )
            receipt = {
                "schemaVersion": 1,
                "resetTarget": str(working),
                "productionRoot": str(plan["production"]),
                "verifiedSourceSnapshot": result["verifiedSourceSnapshot"],
                "productionFileCount": len(plan["production_files"]),
                "productionBytes": sum(
                    entry["bytes"] for entry in plan["production_files"].values()
                ),
                "carryForwardCounts": result["carryForwardCounts"],
                "configurationReceipt": storage_receipt,
            }
            receipt_metadata = _write_json_file(receipt_path, receipt)
            receipt_relative = receipt_path.relative_to(staged).as_posix()
            copied[receipt_relative] = receipt_metadata

            staged_files, _, _, _, _ = _tree_inventory(staged, hash_files=True)
            expected_files = {
                relative: (entry["bytes"], entry["sha256"])
                for relative, entry in copied.items()
            }
            actual_files = {
                relative: (entry["bytes"], entry["sha256"])
                for relative, entry in staged_files.items()
            }
            if actual_files != expected_files:
                raise ValueError("staged Working file list or checksum verification failed")

            old_entries = sorted(
                (
                    path.name
                    for path in working.iterdir()
                    if path != temporary_root
                ),
                key=str.casefold,
            )
            new_entries = sorted(
                (path.name for path in staged.iterdir()),
                key=str.casefold,
            )
            if temporary_root.name in new_entries:
                raise ValueError("staged Production tree overlaps reset staging root")
            journal = {
                "schemaVersion": 1,
                "target": str(working),
                "stageName": stage.name,
                "phase": "swapping",
                "oldEntries": old_entries,
                "newEntries": new_entries,
            }
            _write_reset_journal(journal_path, journal)
            journal_written = True

            for name in old_entries:
                source = working / name
                if source.exists():
                    source.rename(previous / name)
            for name in new_entries:
                source = staged / name
                destination = working / name
                if destination.exists():
                    raise ValueError(f"reset destination unexpectedly exists: {destination}")
                source.rename(destination)

            for name in new_entries:
                if not (working / name).exists():
                    raise ValueError(f"reset destination was not installed: {working / name}")
            committed_journal = dict(journal)
            committed_journal["phase"] = "committed"
            _write_reset_journal(journal_path, committed_journal)
            journal = committed_journal
            _remove_tree(stage / "rollback")
            journal_path.unlink()
        except BaseException as error:
            if journal_written and journal is not None and journal["phase"] != "committed":
                try:
                    _rollback_full_reset(working, stage, journal)
                    if journal_path.exists():
                        journal_path.unlink()
                except BaseException as rollback_error:
                    raise RuntimeError(
                        f"full reset failed and rollback requires recovery; "
                        f"journal: {journal_path}; stage: {stage}"
                    ) from rollback_error
            elif journal is not None and journal["phase"] == "committed":
                raise RuntimeError(
                    f"full reset is committed but cleanup requires recovery; "
                    f"journal: {journal_path}; stage: {stage}"
                ) from error
            try:
                _remove_tree(stage)
            except OSError as cleanup_error:
                raise RuntimeError(
                    f"full reset failed and staging cleanup requires recovery; "
                    f"stage: {stage}"
                ) from cleanup_error
            raise

    if storage_receipt is not None:
        applied_result["configurationReceipt"] = storage_receipt
    applied_result["installedProductionFileCount"] = len(plan["production_files"])
    applied_result["installedProductionBytes"] = sum(
        entry["bytes"] for entry in plan["production_files"].values()
    )
    return applied_result


def _verify_staged_category(category, staged_root, expected):
    staged_files = {}
    for path in _source_files(staged_root):
        relative = path.relative_to(staged_root).as_posix()
        manifest_path = f"{category}/{relative}"
        if manifest_path not in expected:
            raise ValueError(f"unlisted file copied into staged category: {manifest_path}")
        expected_size, expected_digest = expected[manifest_path]
        if path.stat().st_size != expected_size:
            raise ValueError(f"staged category size mismatch: {manifest_path}")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
                digest.update(block)
        if digest.hexdigest() != expected_digest:
            raise ValueError(f"staged category checksum mismatch: {manifest_path}")
        staged_files[manifest_path] = None
    required_files = {
        path for path in expected
        if path.split("/", 1)[0] == category
    }
    if set(staged_files) != required_files:
        raise ValueError(f"staged category file list mismatch: {category}")


def reset_generated_categories(working_root, apply=False, state_root=None):
    """Restore only the generated category roots from the verified Source snapshot."""
    layout = validate_sandbox(working_root)
    working = layout["working_root"]
    source = layout["source_root"]
    state = (
        cw.storage_root(cw.load_cfg(), "sandboxState", root=working)
        if state_root is None
        else _require_inside_working(working, state_root, "state")
    )

    for category in RESET_CATEGORIES:
        destination = working / category
        source_category = source / category
        for path in (destination, source_category):
            if _is_reparse_point(path):
                raise ValueError(f"refusing reparse point in reset path: {path}")
        if destination.exists() and not destination.is_dir():
            raise ValueError(f"reset target is not a directory: {destination}")
        if source_category.exists() and not source_category.is_dir():
            raise ValueError(f"source category is not a directory: {source_category}")
        if destination.is_dir():
            for _path in _source_files(destination):
                pass

    summary = {
        "snapshot_file_count": layout["file_count"],
        "snapshot_bytes": layout["total_bytes"],
        "verification_seconds": layout["verification_seconds"],
        "categories": {},
        "applied": bool(apply),
    }
    for category in RESET_CATEGORIES:
        source_category = source / category
        count = sum(1 for path in _source_files(source_category)) if source_category.is_dir() else 0
        summary["categories"][category] = count

    if not apply:
        return summary

    if _is_reparse_point(state) or (state.exists() and not state.is_dir()):
        raise ValueError(f"missing or unsafe sandbox state directory: {state}")
    state.mkdir(parents=True, exist_ok=True)
    stage = state / f"reset-{uuid.uuid4().hex}"
    stage.mkdir()
    staged = stage / "new"
    previous = stage / "previous"
    staged.mkdir()
    previous.mkdir()
    try:
        for category in RESET_CATEGORIES:
            source_category = source / category
            if source_category.is_dir():
                shutil.copytree(source_category, staged / category)
                _verify_staged_category(
                    category, staged / category, layout["manifest_files"]
                )

        moved_previous = set()
        installed_new = set()
        try:
            for category in RESET_CATEGORIES:
                destination = working / category
                old = previous / category
                new = staged / category
                if destination.exists():
                    destination.rename(old)
                    moved_previous.add(category)
                if new.exists():
                    new.rename(destination)
                    installed_new.add(category)
        except Exception:
            for category in reversed(RESET_CATEGORIES):
                destination = working / category
                old = previous / category
                if category in installed_new and destination.exists():
                    destination.rename(staged / category)
                if category in moved_previous and old.exists():
                    old.rename(destination)
            raise
    except Exception:
        _remove_tree(stage)
        raise
    _remove_tree(stage)
    return summary
