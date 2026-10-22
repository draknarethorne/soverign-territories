#!/usr/bin/env python3
"""Create a dated, integrity-manifested snapshot before photo-library changes.

  python tools/art/library_backup.py              preview the full snapshot
  python tools/art/library_backup.py --apply       copy it under <work>\\_backup

The snapshot includes the work root except prior backups and the work-root
archive, configured ComfyUI inputs and the repository workspace configuration.
ComfyUI output renders are not changed by the library pipeline and are not copied.
"""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
import comfy_workflows as cw  # noqa: E402

CHUNK_SIZE = 1024 * 1024


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
    for label, source, exclude_library_storage in source_list:
        for path, relative in _files(source, exclude_library_storage):
            size = path.stat().st_size
            entries.append((label, path, relative, size))
            total += size
    print(f"snapshot preview: {len(entries)} file(s), {total:,} bytes")
    for label, source, _ in source_list:
        print(f"  {label}: {source}")
    print("  excluded from work-root: _backup, _archive")
    print("  destination: <work-root>\\_backup\\library-<timestamp>")
    return entries, total


def verify_backup(snapshot):
    """Verify manifest coverage, byte counts and hashes for a completed snapshot."""
    root = pathlib.Path(snapshot).resolve()
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


def create_backup(work_root, inputs_root=None, config_path=None, stamp=None, apply=True, extra_sources=()):
    """Preview or create a complete snapshot; publish its manifest only after all copies verify."""
    work = pathlib.Path(work_root).resolve()
    entries, total = preview(work, inputs_root, config_path, extra_sources)
    if not apply:
        return None

    stamp = stamp or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = work / "_backup" / f"library-{stamp}"
    destination.mkdir(parents=True, exist_ok=False)
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
        source_list = sources(work, inputs_root, config_path, extra_sources)
        root_map = {label: source for label, source, _ in source_list}
        for label, source, exclude_library_storage in source_list:
            if source.is_dir():
                for relative in _directories(source, exclude_library_storage):
                    (destination / label / relative).mkdir(parents=True, exist_ok=True)
        for label, source_file, relative, expected_size in entries:
            source_root = root_map[label]
            target = destination / label / relative
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
                "backup": str(target.relative_to(destination)),
                "size": copied,
                "sha256": digest.hexdigest(),
            })

        for label, source, exclude_library_storage in source_list:
            current = {
                (relative.as_posix(), path.stat().st_size)
                for path, relative in _files(source, exclude_library_storage)
            }
            expected = {
                (relative.as_posix(), size)
                for entry_label, _path, relative, size in entries
                if entry_label == label
            }
            if current != expected:
                raise OSError(f"source file list changed while backing up: {source}")

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
        }
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
    parser.add_argument("--root", help="photo library root (default: workspaces.json paths.workRoot)")
    parser.add_argument("--inputs", help="ComfyUI inputs root (default: workspaces.json paths.inputsRoot)")
    args = parser.parse_args(argv)
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
        create_backup(work, inputs, config, apply=args.apply)
    except (OSError, ValueError) as exc:
        print(f"backup failed: {exc}", file=sys.stderr)
        return 1
    if not args.apply:
        print("preview only; add --apply to create the snapshot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
