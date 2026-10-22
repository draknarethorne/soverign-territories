"""Guarded reset helpers for the disposable likeness sandbox."""
import hashlib
import json
import os
import pathlib
import re
import shutil
import stat
import time
import uuid

RESET_CATEGORIES = ("Models", "Prospects", "Potentials")
CHUNK_SIZE = 1024 * 1024


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
    def clear_readonly(function, target, error_info):
        error = error_info[1]
        if not isinstance(error, PermissionError):
            raise error
        os.chmod(target, stat.S_IREAD | stat.S_IWRITE)
        function(target)

    shutil.rmtree(path, onerror=clear_readonly)


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
        if path.is_symlink() or not path.is_dir():
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


def reset_generated_categories(working_root, apply=False):
    """Restore only the generated category roots from the verified Source snapshot."""
    layout = validate_sandbox(working_root)
    working = layout["working_root"]
    source = layout["source_root"]
    state = working / "_sandbox-state"

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
