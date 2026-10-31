"""Opt-in bounded snapshot format experiment; never writes to a library."""
import hashlib
import json
import os
import pathlib
import shutil
import stat
import subprocess
import time
import zipfile

from library_backup import CHUNK_SIZE, ROOT, _snapshot_path

FORMATS = ("directory", "zip64-stored", "zip64-deflate1")
RECIPE = "backup-benchmark-v1"


def guarded(path):
    """Reject symlinks, junctions and all other reparse points before resolving."""
    path = pathlib.Path(os.path.abspath(path))
    for item in (path, *path.parents):
        if item.is_symlink() or (item.exists() and
                getattr(item.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError(f"linked/reparse path refused: {item}")
    return _snapshot_path(path)


def relative_name(value):
    if not isinstance(value, str) or "\\" in value or ":" in value:
        raise ValueError("unsafe benchmark member")
    path = pathlib.PurePosixPath(value)
    if (path.is_absolute() or not path.parts or any(p in (".", "..") for p in path.parts)
            or path.as_posix() != value):
        raise ValueError("unsafe benchmark member")
    return path


def digest(stream):
    result = hashlib.sha256()
    for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
        result.update(block)
    return result.hexdigest()


def file_hash(path):
    with guarded(path).open("rb") as stream:
        return digest(stream)


def output_path(path):
    path = guarded(path)
    scratch = guarded(ROOT / "tmp")
    if scratch not in path.parents:
        raise ValueError("benchmark output must be a child of repository tmp")
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", str(path.relative_to(guarded(ROOT)))],
        cwd=ROOT, check=False)
    if result.returncode:
        raise ValueError("benchmark output must be git-ignored")
    return path


def select_sample(snapshot, limit, max_bytes):
    if not 1 <= limit <= 64 or not 1 <= max_bytes <= 128 * 1024 * 1024:
        raise ValueError("sample bounds: 1..64 files, 1..128 MiB")
    snapshot = guarded(snapshot)
    manifest_path = guarded(snapshot / "manifest.json")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("status") != "complete" or (snapshot / "INCOMPLETE.txt").exists():
        raise ValueError("benchmark requires a completed snapshot")
    # Enumerate manifest metadata only, never walk/hash the whole snapshot.
    groups, names = {}, set()
    for entry in manifest["entries"]:
        name = entry["backup"].replace("\\", "/")
        path = relative_name(name)
        if name.casefold() in names:
            raise ValueError("duplicate snapshot member")
        names.add(name.casefold())
        size = entry["size"]
        if not isinstance(size, int) or size < 0:
            raise ValueError("invalid snapshot size")
        if not isinstance(entry["sha256"], str) or len(entry["sha256"]) != 64:
            raise ValueError("invalid snapshot hash")
        # Round-robin extension/path strata, stable hash order within each stratum.
        group = (path.suffix.lower(), path.parts[1] if len(path.parts) > 1 else "")
        groups.setdefault(group, []).append({
            "path": name, "size": size, "sha256": entry["sha256"]})
    for rows in groups.values():
        rows.sort(key=lambda row: hashlib.sha256(row["path"].encode()).hexdigest())
    selected, total = [], 0
    while groups and len(selected) < limit:
        for key in sorted(list(groups)):
            row = groups[key].pop(0)
            if not groups[key]:
                del groups[key]
            if total + row["size"] > max_bytes:
                continue
            selected.append(row)
            total += row["size"]
            if len(selected) == limit:
                break
    if not selected:
        raise ValueError("no snapshot files fit sample bounds")
    for row in selected:
        source = guarded(snapshot / row["path"])
        if not source.is_file() or source.stat().st_size != row["size"]:
            raise ValueError("selected snapshot file missing or changed")
        row["mtimeNs"] = source.stat().st_mtime_ns
    return {
        "recipe": RECIPE, "snapshot": str(snapshot),
        "manifestSha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "limit": limit, "maxBytes": max_bytes, "entries": selected,
        "sampleFiles": len(selected), "sampleBytes": total,
        "snapshotFiles": len(manifest["entries"]),
        "snapshotBytes": sum(e["size"] for e in manifest["entries"]),
    }


def verify_tree(root, rows):
    root = guarded(root)
    expected = {row["path"] for row in rows}
    actual = set()
    # Guard each directory before descending (junctions are not symlinks).
    for current, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            guarded(pathlib.Path(current) / name)
        for name in names:
            path = pathlib.Path(current) / name
            if not path.is_file():
                raise ValueError("nonregular benchmark tree member")
            actual.add(path.relative_to(root).as_posix())
    if actual != expected:
        raise ValueError("benchmark tree file list mismatch")
    for row in rows:
        path = guarded(root / relative_name(row["path"]))
        info = path.stat()
        if (info.st_size != row["size"] or info.st_mtime_ns != row["mtimeNs"]
                or file_hash(path) != row["sha256"]):
            raise ValueError(f"benchmark tree content/mtime mismatch: {path}")


def verify_source(selection):
    for row in selection["entries"]:
        source = guarded(pathlib.Path(selection["snapshot"]) / row["path"])
        info = source.stat()
        if (info.st_size != row["size"] or info.st_mtime_ns != row["mtimeNs"]
                or file_hash(source) != row["sha256"]):
            raise ValueError(f"selected snapshot content/mtime changed: {source}")


def verify_archive(path, rows, restore=None):
    expected = {row["path"]: row for row in rows}
    with zipfile.ZipFile(guarded(path)) as archive:
        infos = archive.infolist()
        if len(infos) != len(expected) or {i.filename for i in infos} != set(expected):
            raise ValueError("archive member list mismatch")
        for info in infos:
            name = relative_name(info.filename)
            row = expected[info.filename]
            mode = info.external_attr >> 16
            if (info.is_dir() or stat.S_ISLNK(mode) or
                    (stat.S_IFMT(mode) not in (0, stat.S_IFREG)) or
                    info.file_size != row["size"]):
                raise ValueError("unsafe archive member/type/size")
            with archive.open(info) as stream:
                if restore is None:
                    actual = digest(stream)
                else:
                    target = guarded(restore / name)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as destination:
                        shutil.copyfileobj(stream, destination, CHUNK_SIZE)
                    os.utime(target, ns=(row["mtimeNs"], row["mtimeNs"]))
                    actual = None  # The restored tree receives a full hash pass below.
                if restore is None and actual != row["sha256"]:
                    raise ValueError("archive content hash mismatch")


def build_format(kind, destination, selection):
    rows = selection["entries"]
    source = pathlib.Path(selection["snapshot"])
    folder = destination / kind
    folder.mkdir()
    payload = folder / ("payload" if kind == "directory" else "payload.zip")
    started = time.perf_counter()
    if kind == "directory":
        payload.mkdir()
        for row in rows:
            target = payload / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(guarded(source / row["path"]), target)
    else:
        compression = zipfile.ZIP_STORED if kind == "zip64-stored" else zipfile.ZIP_DEFLATED
        with zipfile.ZipFile(payload, "x", compression=compression,
                             compresslevel=None if compression == zipfile.ZIP_STORED else 1,
                             allowZip64=True) as archive:
            for row in rows:
                with guarded(source / row["path"]).open("rb") as src:
                    with archive.open(row["path"], "w", force_zip64=True) as dst:
                        shutil.copyfileobj(src, dst, CHUNK_SIZE)
    build_seconds = time.perf_counter() - started
    started = time.perf_counter()
    if kind == "directory":
        verify_tree(payload, rows)
    else:
        verify_archive(payload, rows)
    verify_seconds = time.perf_counter() - started
    restored = folder / "restored"
    started = time.perf_counter()
    if kind == "directory":
        shutil.copytree(payload, restored)
    else:
        restored.mkdir()
        verify_archive(payload, rows, restore=restored)
    verify_tree(restored, rows)
    restore_seconds = time.perf_counter() - started
    return {
        "format": kind, "buildSeconds": build_seconds, "verifySeconds": verify_seconds,
        "restoreVerifySeconds": restore_seconds,
        "outputFiles": len(rows) if kind == "directory" else 1,
        "outputBytes": selection["sampleBytes"] if kind == "directory" else payload.stat().st_size,
        "restoreFiles": len(rows), "restoreBytes": selection["sampleBytes"],
        "archiveSha256": None if kind == "directory" else file_hash(payload),
    }


def check_receipt(destination, selection):
    destination = output_path(destination)
    receipt = json.loads(guarded(destination / "receipt.json").read_text(encoding="utf-8"))
    if receipt.get("status") != "complete" or receipt.get("selection") != selection:
        raise ValueError("benchmark receipt/input changed; use a new ignored output directory")
    verify_source(selection)
    results = receipt["results"]
    if len(results) != len(FORMATS) or [r["format"] for r in results] != list(FORMATS):
        raise ValueError("benchmark receipt format list mismatch")
    for result in results:
        kind = result["format"]
        folder = guarded(destination / kind)
        for key in ("buildSeconds", "verifySeconds", "restoreVerifySeconds"):
            if not isinstance(result[key], (float, int)) or not 0 <= result[key] < float("inf"):
                raise ValueError("invalid measured timing")
        if (result["restoreFiles"] != selection["sampleFiles"] or
                result["restoreBytes"] != selection["sampleBytes"]):
            raise ValueError("invalid restore denominator")
        if kind == "directory":
            verify_tree(folder / "payload", selection["entries"])
            size, count = selection["sampleBytes"], selection["sampleFiles"]
        else:
            archive = guarded(folder / "payload.zip")
            if file_hash(archive) != result["archiveSha256"]:
                raise ValueError("persisted archive changed")
            verify_archive(archive, selection["entries"])
            size, count = archive.stat().st_size, 1
        if result["outputBytes"] != size or result["outputFiles"] != count:
            raise ValueError("output byte/file count mismatch")
        verify_tree(folder / "restored", selection["entries"])
    return receipt


def run(snapshot, out=None, limit=24, max_bytes=32 * 1024 * 1024, apply=False, check=False):
    selection = select_sample(snapshot, limit, max_bytes)
    destination = output_path(out or ROOT / "tmp" / "backup-benchmarks" /
                              f"{pathlib.Path(snapshot).name}-f{limit}-b{max_bytes}")
    source = guarded(snapshot)
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("benchmark output and snapshot must not overlap")
    print(f"benchmark: {selection['sampleFiles']}/{selection['snapshotFiles']} files; "
          f"{selection['sampleBytes']:,}/{selection['snapshotBytes']:,} bytes")
    print(f"output: {destination}; formats: {', '.join(FORMATS)}")
    if check or destination.exists():
        receipt = check_receipt(destination, selection)
        print("persisted benchmark verified; no outputs rewritten")
        return receipt
    if not apply:
        print("preview only; --apply measures; --check verifies saved receipt and all payloads/restores")
        return selection
    verify_source(selection)
    destination.mkdir(parents=True, exist_ok=False)
    # Publish only after every format and source check passes. Incomplete runs are
    # retained and refused, never silently replaced or mistaken for measurements.
    results = [build_format(kind, destination, selection) for kind in FORMATS]
    verify_source(selection)
    receipt = {
        "status": "complete", "selection": selection, "results": results,
        "caveats": [
            "single pass, fixed directory/stored/deflate1 order; warm OS caches, no fsync",
            "snapshot reads and repo-tmp writes; not a same-volume B: throughput benchmark",
            "logical bytes exclude allocation/receipt overhead; restore timings include full hash verification",
            "selected regular-file bytes/names/mtimeNs only; no ACL, empty-directory or directory-time recovery",
            "only selected snapshot hashes verified; no full snapshot verification or new backup format adoption",
        ],
    }
    temporary = destination / "receipt.json.writing"
    temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, destination / "receipt.json")
    check_receipt(destination, selection)
    for result in results:
        print(json.dumps(result))
    return receipt
