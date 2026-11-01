"""Bounded, opt-in, lossless snapshot packing; no live-library selection or pruning.

The new bundle contains payload.zip and a path-bound integrity receipt. Checks
need no source. Restore materializes the original snapshot, including its exact
manifest, for library_backup.verify_backup/restore_backup. This is not an
authenticated signature, ACL backup, or a concurrent-writer locking protocol.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import stat
import sys
import time
import zipfile

import library_backup as backup
from library_backup_benchmark import guarded

ROOT = backup.ROOT
MAX_FILES = 20_000
MAX_BYTES = 2 * 1024**3
MAX_METADATA = 16 * 1024**2
MAX_DIRS = 20_000
MAX_ARCHIVE_BYTES = MAX_BYTES + 2 * MAX_METADATA
RECIPE = "lossless-snapshot-zip64-v1"
TEXT = {".json", ".jsonl", ".txt", ".md", ".html", ".htm", ".csv", ".yaml",
        ".yml", ".xml", ".log", ".cmd", ".py", ".js", ".css", ".svg"}
HEX = re.compile(r"[0-9a-f]{64}")


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def integer(value, maximum):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError("invalid or out-of-bounds integer")
    return value


def name(value):
    """Canonical portable member names, including Windows device/ADS rules."""
    if not isinstance(value, str) or not value or len(value) > 32700:
        raise ValueError("unsafe member name")
    parts = value.split("/")
    for part in parts:
        if (not part or part in (".", "..") or part[-1] in ". "
                or any(ord(c) < 32 or c in '\\:<>|"?*' for c in part)
                or re.fullmatch(r"(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?",
                                part, re.IGNORECASE)):
            raise ValueError(f"unsafe member name: {value!r}")
    return value


def output_path(value):
    if not pathlib.Path(value).is_absolute():
        raise ValueError("output must be explicitly absolute and below ignored repository tmp")
    path = guarded(value)
    scratch = guarded(ROOT / "tmp")
    if scratch not in path.parents:
        raise ValueError("output must be below ignored repository tmp (experiment only)")
    # Use the established git-ignore check, with an explicit absolute-path gate.
    from library_backup_benchmark import output_path as checked_output
    checked_output(path)
    return path


def file_hash(path, max_bytes=MAX_ARCHIVE_BYTES):
    digest = hashlib.sha256()
    total = 0
    with guarded(path).open("rb") as stream:
        for block in iter(lambda: stream.read(backup.CHUNK_SIZE), b""):
            total += len(block)
            if total > max_bytes:
                raise ValueError("file grew beyond bounded size")
            digest.update(block)
    return digest.hexdigest()


def copy_payload(src, dst, size):
    remaining = size
    while True:
        block = src.read(min(backup.CHUNK_SIZE, remaining + 1))
        if not block:
            if remaining:
                raise ValueError("payload truncated while copying")
            return
        if len(block) > remaining:
            raise ValueError("payload grew while copying")
        dst.write(block)
        remaining -= len(block)


def read_json(payload):
    if len(payload) > MAX_METADATA:
        raise ValueError("metadata exceeds 16 MiB bound")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(payload, object_pairs_hook=unique)


def metadata_bytes(path):
    path = guarded(path)
    if not path.is_file() or path.stat().st_size > MAX_METADATA:
        raise ValueError("missing or oversized metadata")
    with path.open("rb") as stream:
        data = stream.read(MAX_METADATA + 1)
    if len(data) > MAX_METADATA:
        raise ValueError("metadata exceeds 16 MiB bound")
    return data


def validate_rows(index):
    if not isinstance(index, dict) or index.get("recipe") != RECIPE:
        raise ValueError("unsupported archive index")
    rows, dirs = index["files"], index["directories"]
    if (not isinstance(rows, list) or not 1 <= len(rows) <= MAX_FILES
            or not isinstance(dirs, list) or len(dirs) > MAX_DIRS):
        raise ValueError("archive file/directory count bound exceeded")
    names, files, directories, total = {}, {}, {}, 0
    for kind, entries, result in (("directory", dirs, directories), ("file", rows, files)):
        for row in entries:
            path = name(row["path"])
            key = path.casefold()
            if key in names:
                raise ValueError("duplicate/case-colliding snapshot path")
            names[key] = path
            integer(row["mtimeNs"], 2**63 - 1)
            result[path] = row
            if kind == "file":
                total += integer(row["size"], MAX_BYTES)
                if not isinstance(row["sha256"], str) or not HEX.fullmatch(row["sha256"]):
                    raise ValueError("invalid payload hash")
    if total > MAX_BYTES:
        raise ValueError("snapshot exceeds 2 GiB input bound")
    integer(index["rootMtimeNs"], 2**63 - 1)
    for path in names.values():
        parent = pathlib.PurePosixPath(path).parent
        while str(parent) != ".":
            if parent.as_posix() not in directories:
                raise ValueError("missing or case-colliding parent directory")
            parent = parent.parent
    if "manifest.json" not in files or files["manifest.json"]["size"] > MAX_METADATA:
        raise ValueError("missing/oversized original snapshot manifest")
    return files, directories


def validate_manifest(payload, files, directories=()):
    manifest = read_json(payload)
    if not isinstance(manifest, dict) or manifest.get("status") != "complete":
        raise ValueError("requires a completed snapshot")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or len(entries) > MAX_FILES:
        raise ValueError("invalid snapshot entries")
    expected, seen = {}, set()
    for row in entries:
        relative = name(row["backup"].replace("\\", "/"))
        if relative.casefold() in seen or relative == "manifest.json":
            raise ValueError("duplicate/case-colliding snapshot manifest entry")
        seen.add(relative.casefold())
        expected[relative] = row
        if (relative not in files or row["size"] != files[relative]["size"]
                or row["sha256"] != files[relative]["sha256"]):
            raise ValueError("original snapshot manifest/payload mismatch")
    if set(expected) != set(files) - {"manifest.json"}:
        raise ValueError("original snapshot manifest coverage mismatch")
    recovery = manifest.get("regenerable", [])
    reports = manifest.get("generatedReports", [])
    if not isinstance(recovery, list) or not isinstance(reports, list):
        raise ValueError("invalid snapshot recovery metadata")
    if len(recovery) + len(reports) > MAX_FILES:
        raise ValueError("recovery metadata count bound exceeded")
    directory_keys = {path.casefold() for path in directories}
    for existing in files:
        parent = pathlib.PurePosixPath(existing).parent
        while str(parent) != ".":
            directory_keys.add(parent.as_posix().casefold())
            parent = parent.parent
    for row in recovery + reports:
        target = name(row["backup"].replace("\\", "/"))
        if target.casefold() in seen or target.casefold() in directory_keys:
            raise ValueError("duplicate recovery target")
        parent = pathlib.PurePosixPath(target).parent
        while str(parent) != ".":
            if parent.as_posix().casefold() in seen:
                raise ValueError("recovery file/directory collision")
            directory_keys.add(parent.as_posix().casefold())
            parent = parent.parent
        seen.add(target.casefold())
        for field in ("sourceBackup", "manifestBackup"):
            if field in row:
                reference = name(row[field].replace("\\", "/"))
                if reference not in files:
                    raise ValueError("missing recovery source/manifest")
    return manifest


def inventory(snapshot):
    root = guarded(snapshot)
    if not root.is_dir():
        raise ValueError("snapshot must be a directory")
    rows, dirs, total = [], [], 0
    root_time = root.stat().st_mtime_ns
    for current, children, names in os.walk(root, followlinks=False):
        children.sort()
        names.sort()
        for child in children:
            path = guarded(pathlib.Path(current) / child)
            if not stat.S_ISDIR(path.stat().st_mode):
                raise ValueError("nonregular snapshot directory")
            dirs.append({"path": path.relative_to(root).as_posix(),
                         "mtimeNs": path.stat().st_mtime_ns})
            if len(dirs) > MAX_DIRS:
                raise ValueError("snapshot exceeds 20,000 directory bound")
        for child in names:
            path = guarded(pathlib.Path(current) / child)
            info = path.stat()
            if not stat.S_ISREG(info.st_mode):
                raise ValueError("nonregular snapshot file")
            total += info.st_size
            if len(rows) >= MAX_FILES or total > MAX_BYTES:
                raise ValueError("snapshot exceeds bounds: 20,000 files / 2 GiB input")
            relative = name(path.relative_to(root).as_posix())
            if relative == "manifest.json" and info.st_size > MAX_METADATA:
                raise ValueError("snapshot manifest exceeds 16 MiB bound")
            if relative == "INCOMPLETE.txt":
                raise ValueError("incomplete snapshot refused")
            rows.append({"path": relative, "size": info.st_size,
                         "mtimeNs": info.st_mtime_ns})
    # All size/count/name bounds are checked before hashing any image.
    for row in rows:
        path = guarded(root / row["path"])
        before = path.stat()
        row["sha256"] = file_hash(path, row["size"])
        after = path.stat()
        if (before.st_size != row["size"] or after.st_size != row["size"]
                or before.st_mtime_ns != row["mtimeNs"]
                or after.st_mtime_ns != row["mtimeNs"]
                or before.st_ino != after.st_ino):
            raise ValueError("source changed while hashing")
    index = {"recipe": RECIPE, "rootMtimeNs": root_time,
             "files": sorted(rows, key=lambda row: row["path"]),
             "directories": sorted(dirs, key=lambda row: row["path"])}
    files, directories = validate_rows(index)
    validate_manifest(metadata_bytes(root / "manifest.json"), files, directories)
    if len(canonical(index)) > MAX_METADATA:
        raise ValueError("archive index exceeds metadata bound")
    return index


def metrics(index):
    unique = {}
    for row in index["files"]:
        old = unique.setdefault(row["sha256"], row["size"])
        if old != row["size"]:
            raise ValueError("payload hash/size conflict")
    return {"fileCount": len(index["files"]), "uniquePayloads": len(unique),
            "logicalBytes": sum(row["size"] for row in index["files"]),
            "uniqueBytes": sum(unique.values())}


def zip_info(member, compression):
    info = zipfile.ZipInfo(member)
    info.compress_type = compression
    info.external_attr = (stat.S_IFREG | 0o600) << 16
    info._compresslevel = 1 if compression == zipfile.ZIP_DEFLATED else None
    return info


def build_zip(path, source, index, kind):
    with zipfile.ZipFile(path, "x", allowZip64=True) as archive:
        archive.writestr(zip_info("snapshot.json", zipfile.ZIP_DEFLATED
                                 if kind == "hybrid" else zipfile.ZIP_STORED), canonical(index))
        groups = {}
        for row in index["files"]:
            groups.setdefault(row["sha256"], []).append(row)
        for digest, rows in sorted(groups.items()):
            compress = (kind == "hybrid" and all(
                pathlib.PurePosixPath(row["path"]).suffix.lower() in TEXT for row in rows))
            info = zip_info("payload/" + digest,
                            zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED)
            with guarded(source / rows[0]["path"]).open("rb") as src:
                with archive.open(info, "w", force_zip64=True) as dst:
                    copy_payload(src, dst, rows[0]["size"])
    with path.open("r+b") as stream:
        os.fsync(stream.fileno())


def bounded_zip(path):
    """Bound ZIP central-directory allocation before ZipFile parses members."""
    path = guarded(path)
    if not path.is_file() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("archive exceeds bounded size")
    with path.open("rb") as stream:
        end = zipfile._EndRecData(stream)
    if (end is None or end[zipfile._ECD_ENTRIES_TOTAL] > MAX_FILES + 1
            or end[zipfile._ECD_ENTRIES_THIS_DISK] != end[zipfile._ECD_ENTRIES_TOTAL]
            or end[zipfile._ECD_DISK_NUMBER] or end[zipfile._ECD_DISK_START]
            or end[zipfile._ECD_SIZE] > MAX_METADATA):
        raise ValueError("archive central-directory count/bytes/disk bounds exceeded")
    return path


def checked_archive(path, expected_index_hash, kind):
    with zipfile.ZipFile(bounded_zip(path), "r", allowZip64=True) as archive:
        members = archive.infolist()
        if not 2 <= len(members) <= MAX_FILES + 1:
            raise ValueError("archive member count bound exceeded")
        seen = set()
        for info in members:
            member = name(info.filename)
            if member.casefold() in seen:
                raise ValueError("duplicate/case-colliding ZIP member")
            seen.add(member.casefold())
            mode = info.external_attr >> 16
            if (info.is_dir() or stat.S_IFMT(mode) not in (0, stat.S_IFREG)
                    or info.flag_bits & 1 or info.file_size > MAX_BYTES
                    or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
                raise ValueError("unsafe archive member/type/size/compression")
        metadata = archive.getinfo("snapshot.json")
        if metadata.file_size > MAX_METADATA:
            raise ValueError("oversized archive metadata")
        raw = archive.read(metadata)
        if sha(raw) != expected_index_hash:
            raise ValueError("archive index checksum mismatch")
        index = read_json(raw)
        files, directories = validate_rows(index)
        groups = {}
        for row in files.values():
            groups.setdefault(row["sha256"], []).append(row)
        if {m.filename for m in members} != {"snapshot.json", *(
                "payload/" + digest for digest in groups)}:
            raise ValueError("archive membership mismatch")
        for digest, rows in groups.items():
            info = archive.getinfo("payload/" + digest)
            compressed = kind == "hybrid" and all(
                pathlib.PurePosixPath(row["path"]).suffix.lower() in TEXT for row in rows)
            expected_type = zipfile.ZIP_DEFLATED if compressed else zipfile.ZIP_STORED
            if (any(row["size"] != info.file_size for row in rows)
                    or info.compress_type != expected_type):
                raise ValueError("archive payload size/compression mismatch")
            actual = hashlib.sha256()
            with archive.open(info) as stream:
                for block in iter(lambda: stream.read(backup.CHUNK_SIZE), b""):
                    actual.update(block)
            if actual.hexdigest() != digest:
                raise ValueError("archive payload checksum mismatch")
        manifest_row = files["manifest.json"]
        manifest_bytes = archive.read("payload/" + manifest_row["sha256"])
        validate_manifest(manifest_bytes, files, directories)
        return index


def check_bundle(bundle, *, published_path=None):
    started = time.perf_counter()
    root = output_path(bundle)
    if not root.is_dir():
        raise ValueError("missing archive bundle")
    if {p.name for p in root.iterdir()} != {"payload.zip", "receipt.json"}:
        raise ValueError("bundle membership mismatch")
    receipt = read_json(metadata_bytes(root / "receipt.json"))
    seal = receipt.pop("sealSha256", None)
    if seal != sha(canonical(receipt)):
        raise ValueError("bundle receipt seal mismatch")
    if (receipt.get("recipe") != RECIPE or receipt.get("status") != "complete"
            or receipt.get("bundle") != str(guarded(published_path or root))
            or receipt.get("format") not in ("hybrid", "stored")):
        raise ValueError("bundle final path/format/status mismatch")
    payload = bounded_zip(root / "payload.zip")
    if (not payload.is_file() or payload.stat().st_size != receipt["archiveBytes"]
            or file_hash(payload) != receipt["archiveSha256"]):
        raise ValueError("archive checksum/size mismatch")
    index = checked_archive(payload, receipt["indexSha256"], receipt["format"])
    if metrics(index) != receipt["metrics"]:
        raise ValueError("bundle metrics mismatch")
    for key in ("buildSeconds",):
        if (type(receipt[key]) not in (int, float)
                or not 0 <= receipt[key] < float("inf")):
            raise ValueError("invalid bundle timing")
    receipt["sealSha256"] = seal
    print(json.dumps({**receipt["metrics"], "archiveBytes": receipt["archiveBytes"],
                      "checkSeconds": time.perf_counter() - started}))
    return receipt, index


def nonoverlap(left, right):
    if left == right or left in right.parents or right in left.parents:
        raise ValueError("source/output paths must not overlap")


def publish(stage, destination):
    # Windows scanners can briefly retain directory handles after verification.
    for attempt in range(6):
        guarded(destination)
        if destination.exists():
            raise ValueError("publication destination appeared")
        try:
            os.rename(stage, destination)
            return
        except PermissionError:
            if os.name != "nt" or attempt == 5:
                raise
            time.sleep(0.05 * (attempt + 1))


def pack(snapshot, out, *, kind="hybrid", apply=False):
    if kind not in ("hybrid", "stored"):
        raise ValueError("unsupported archive format")
    source, destination = guarded(snapshot), output_path(out)
    nonoverlap(source, destination)
    if destination.exists():
        receipt, index = check_bundle(destination)
        if (receipt["source"] != str(source) or receipt["format"] != kind
                or inventory(source) != index):
            raise ValueError("existing bundle does not match exact source/format")
        print("existing bundle verified; no rewrite")
        return receipt
    index = inventory(source)
    backup.verify_backup(source)
    print(json.dumps({**metrics(index), "format": kind, "eligible": True,
                      "source": str(source), "out": str(destination)}))
    if not apply:
        print("preview only; --apply publishes a new bundle; source remains untouched")
        return index
    stage = guarded(destination.with_name(destination.name + ".packing"))
    nonoverlap(source, stage)
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage.mkdir(exist_ok=False)
    started = time.perf_counter()
    try:
        build_zip(stage / "payload.zip", source, index, kind)
        receipt = {"recipe": RECIPE, "status": "complete", "bundle": str(destination),
                   "source": str(source), "format": kind, "metrics": metrics(index),
                   "indexSha256": sha(canonical(index)),
                   "archiveSha256": file_hash(stage / "payload.zip"),
                   "archiveBytes": (stage / "payload.zip").stat().st_size,
                   "buildSeconds": time.perf_counter() - started}
        receipt["sealSha256"] = sha(canonical(receipt))
        data = canonical(receipt)
        if len(data) > MAX_METADATA:
            raise ValueError("receipt metadata bound exceeded")
        with (stage / "receipt.json").open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        check_bundle(stage, published_path=destination)
        # Final exact path, membership, mtime and source-byte recheck before publish.
        if inventory(source) != index:
            raise ValueError("source changed before publication")
        publish(stage, destination)
    except BaseException:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    print(json.dumps({"buildSeconds": receipt["buildSeconds"],
                      "archiveBytes": receipt["archiveBytes"], "bundle": str(destination)}))
    return receipt


def restore(bundle, destination, *, apply=False):
    started = time.perf_counter()
    source, target = output_path(bundle), output_path(destination)
    nonoverlap(source, target)
    receipt, index = check_bundle(source)
    if target.exists():
        raise ValueError("materialized destination must be NEW")
    print(f"materialize snapshot: {source} -> {target}")
    if not apply:
        print("preview only; --apply materializes the original snapshot manifest and all paths")
        return target
    stage = guarded(target.with_name(target.name + ".materializing"))
    nonoverlap(source, stage)
    target.parent.mkdir(parents=True, exist_ok=True)
    stage.mkdir(exist_ok=False)
    try:
        for row in index["directories"]:
            (stage / row["path"]).mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(guarded(source / "payload.zip")) as archive:
            for row in index["files"]:
                path = guarded(stage / row["path"])
                with archive.open("payload/" + row["sha256"]) as src, path.open("xb") as dst:
                    copy_payload(src, dst, row["size"])
                os.utime(path, ns=(row["mtimeNs"], row["mtimeNs"]))
        for row in sorted(index["directories"], key=lambda r: r["path"].count("/"), reverse=True):
            os.utime(stage / row["path"], ns=(row["mtimeNs"], row["mtimeNs"]))
        os.utime(stage, ns=(index["rootMtimeNs"], index["rootMtimeNs"]))
        if inventory(stage) != index:
            raise ValueError("materialized snapshot content/mtime mismatch")
        backup.verify_backup(stage)
        # Reject archive/receipt mutation during materialization too.
        checked, _ = check_bundle(source)
        if checked != receipt:
            raise ValueError("bundle changed during materialization")
        publish(stage, target)
    except BaseException:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    print(json.dumps({"restoreSeconds": time.perf_counter() - started,
                      "destination": str(target), **metrics(index)}))
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", nargs="?", help="existing completed directory snapshot")
    parser.add_argument("--out", help="NEW explicitly absolute ignored repository tmp bundle")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", metavar="BUNDLE", help="independent read-only archive verification")
    modes.add_argument("--restore", metavar="BUNDLE", help="materialize original directory snapshot")
    parser.add_argument("--destination", help="NEW explicitly absolute ignored repository tmp directory")
    parser.add_argument("--format", choices=("hybrid", "stored"), default="hybrid")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--apply", action="store_true")
    action.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.check:
            if args.snapshot or args.out or args.destination or args.apply:
                parser.error("--check takes only a bundle (read-only)")
            check_bundle(args.check)
        elif args.restore:
            if args.snapshot or args.out or not args.destination:
                parser.error("--restore requires --destination, not snapshot/--out")
            restore(args.restore, args.destination, apply=args.apply)
        else:
            if not args.snapshot or not args.out or args.destination:
                parser.error("packing requires SNAPSHOT --out ABSOLUTE_NEW_TMP_BUNDLE")
            pack(args.snapshot, args.out, kind=args.format, apply=args.apply)
        return 0
    except (OSError, ValueError, KeyError, TypeError, RecursionError, zipfile.BadZipFile,
            NotImplementedError, RuntimeError) as error:
        print(f"backup archive refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
