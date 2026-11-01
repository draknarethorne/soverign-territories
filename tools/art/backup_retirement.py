"""Sandbox-only Recycle Bin experiment. No permanent deletion or purge operation.

Public launcher: bin\\backup-retire.cmd
  retire ABS_SNAPSHOT --bundle ABS_BUNDLE --receipt ABS_NEW_JSON
      --sample ABS_GENERATED_SAMPLE_JSON --recovery-proof ABS_PROOF_DIRECTORY
      --comparison ABS_BASELINE --reason TEXT [--dry-run | --apply]
  --check ABS_RECEIPT
  recover --receipt ABS_RECEIPT [--dry-run | --apply]

Only synthetic fixtures under ignored repo tmp\\retire-proof are eligible.
The sample marker is an explicit operator attestation, not authentication.
Recovery proof contains archive-materialized `snapshot` and ordinary
library_backup.restore_backup `recovered` trees. All content is independently
verified, including derivative rendering, rather than trusting their status.
Receipts and the independent archive must be retained outside the retired tree.
Recycle Bin storage remains allocated. Eventual permanent purge is NOT provided.
"""
import argparse
import contextlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import zipfile

import library_backup_archive as archive

RECIPE = "sandbox-backup-retirement-v1"
SAMPLE = "synthetic-backup-retirement-v1"
HOME = archive.ROOT / "tmp" / "retire-proof"
SCRIPT = pathlib.Path(__file__).with_name("recycle_directory.ps1")
ACTIVE = {"active", "running", "pending", "in_progress", "in-progress",
          "prepared", "applied", "undoable", "interrupted", "started"}


def local(value):
    """Require explicit local absolute spelling; refuse traversal before resolve."""
    text = os.fspath(value)
    if text.startswith("\\\\?\\") and not text.startswith("\\\\?\\UNC\\"):
        text = text[4:]
    if (not pathlib.Path(text).is_absolute()
            or ".." in pathlib.Path(text).parts
            or text.startswith(("\\\\", "//"))
            or any(":" in p for p in pathlib.Path(text).parts[1:])):
        raise ValueError("explicit local absolute path without traversal required")
    return archive.output_path(text)


def scope(value):
    path = local(value)
    if archive.guarded(HOME) not in path.parents:
        raise ValueError("only generated samples below tmp\\retire-proof are eligible")
    return path


def separate(*paths):
    for i, left in enumerate(paths):
        for right in paths[i + 1:]:
            archive.nonoverlap(left, right)


def tree(root):
    """Bounded exact inventory, including empty directories and directory times."""
    root = archive.guarded(root)
    if not root.is_dir():
        raise ValueError(f"missing directory: {root}")
    files, directories, total = [], [], 0
    for current, children, names in archive.walk(root):
        for child in sorted(children):
            path = archive.guarded(pathlib.Path(current) / child)
            if not path.is_dir():
                raise ValueError("nonregular directory")
            directories.append({"path": archive.name(path.relative_to(root).as_posix()),
                                "mtimeNs": path.stat().st_mtime_ns})
            if len(directories) > archive.MAX_DIRS:
                raise ValueError("directory bound exceeded")
        for child in sorted(names):
            path = archive.guarded(pathlib.Path(current) / child)
            before = path.stat()
            if not path.is_file() or before.st_nlink != 1:
                raise ValueError("nonregular or hard-linked file")
            total += before.st_size
            if len(files) >= archive.MAX_FILES or total > archive.MAX_BYTES:
                raise ValueError("20,000 files / 2 GiB bound exceeded")
            digest = archive.file_hash(path, before.st_size)
            after = path.stat()
            if ((before.st_size, before.st_mtime_ns, before.st_ino)
                    != (after.st_size, after.st_mtime_ns, after.st_ino)):
                raise ValueError("tree changed during verification")
            files.append({"path": archive.name(path.relative_to(root).as_posix()),
                          "mtimeNs": before.st_mtime_ns, "size": before.st_size,
                          "sha256": digest})
    return {"rootMtimeNs": root.stat().st_mtime_ns,
            "files": sorted(files, key=lambda row: row["path"]),
            "directories": sorted(directories, key=lambda row: row["path"])}


def exact_snapshot(path, index):
    actual = tree(path)
    if actual != {key: index[key] for key in actual}:
        raise ValueError("snapshot membership/bytes/mtime differs from archive index")
    archive.backup.verify_backup(path)
    return actual


def seal(data):
    body = {key: value for key, value in data.items() if key != "sealSha256"}
    return {**body, "sealSha256": archive.sha(archive.canonical(body))}


def read(path):
    data = archive.read_json(archive.metadata_bytes(path))
    if not isinstance(data, dict) or seal(data) != data:
        raise ValueError("receipt/sample integrity seal mismatch")
    return data


def write(path, data, *, new=False):
    path = scope(path)
    payload = archive.canonical(seal(data))
    if len(payload) > archive.MAX_METADATA:
        raise ValueError("receipt exceeds metadata bound")
    path.parent.mkdir(parents=True, exist_ok=True)
    if new:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    else:
        pending = archive.guarded(path.with_name(path.name + ".writing"))
        with pending.open("wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(pending, path)


def shell(action, target, identity=None):
    if os.name != "nt":
        raise ValueError("Windows Recycle Bin is required; no deletion fallback")
    command = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
               "Bypass", "-File", str(SCRIPT), "-Action", action,
               "-Target", str(target).removeprefix("\\\\?\\")]
    if identity:
        command.extend(["-Identity", identity["itemPath"]])
    result = subprocess.run(command, capture_output=True, text=True, timeout=100)
    if result.returncode:
        raise RuntimeError(f"Recycle Bin API refused: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    if not isinstance(data, dict):
        raise ValueError("invalid Recycle Bin API result")
    return data


def active_references(target, sample_root):
    """Fail closed on active run/undo references in the generated sample area."""
    count = 0
    for current, children, names in archive.walk(sample_root):
        for child in children:
            archive.guarded(pathlib.Path(current) / child)
        for name in names:
            path = archive.guarded(pathlib.Path(current) / name)
            count += 1
            if count > archive.MAX_FILES:
                raise ValueError("active-reference scan bound exceeded")
            if path.suffix.lower() not in {".json", ".jsonl"} or target in path.parents:
                continue
            raw = archive.metadata_bytes(path)
            try:
                documents = ([archive.read_json(line) for line in raw.splitlines() if line]
                             if path.suffix.lower() == ".jsonl" else [archive.read_json(raw)])
            except ValueError as error:
                raise ValueError(f"unreadable run/undo metadata: {path}") from error

            def walk(value, active=False):
                if isinstance(value, dict):
                    active = active or any(
                        str(value.get(key, "")).lower() in ACTIVE
                        for key in ("status", "state"))
                    active = active or value.get("undoAvailable") is True
                    for child in value.values():
                        walk(child, active)
                elif isinstance(value, list):
                    for child in value:
                        walk(child, active)
                elif active and isinstance(value, str) and pathlib.Path(value).is_absolute():
                    reference = archive.guarded(value)
                    if (reference == target or reference in target.parents
                            or target in reference.parents):
                        raise ValueError(f"target referenced by active run/undo: {path}")
            for document in documents:
                walk(document)


def mapping(manifest, sample_root, index):
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 8:
        raise ValueError("missing bounded source mapping")
    roots, preserved = {}, {}
    source_area = scope(sample_root / "source")
    for row in sources:
        label = archive.name(row["name"])
        if "/" in label or label in roots:
            raise ValueError("unsafe source label")
        path = scope(row["path"])
        if source_area not in path.parents:
            raise ValueError("only generated source paths are permitted")
        if not path.is_dir():
            raise ValueError("fixture sources must be directories")
        roots[label] = path
        preserved[str(path)] = tree(path)
    if "work-root" not in roots or manifest.get("scope") == "transaction":
        raise ValueError("requires ordinary synthetic work-root backup")
    rows = {row["path"]: row for row in index["files"]}
    for entry in manifest["entries"]:
        relative = archive.name(entry["backup"].replace("\\", "/"))
        label, member = relative.split("/", 1)
        if label not in roots:
            raise ValueError("unmapped snapshot label")
        source = scope(entry["source"])
        if source != archive.guarded(roots[label] / member):
            raise ValueError("manifest source/backup mapping mismatch")
        info, expected = source.stat(), rows[relative]
        if (info.st_nlink != 1 or info.st_size != expected["size"]
                or info.st_mtime_ns != expected["mtimeNs"]
                or archive.file_hash(source, info.st_size) != expected["sha256"]):
            raise ValueError("original generated source differs from archived file")
    # Every current source byte must have an exact retained or regenerable mapping.
    # Legacy exclude_backup and current exclude_library_storage mean the same thing.
    covered = {row["backup"].replace("\\", "/") for row in manifest["entries"]}
    covered.update(row["backup"].replace("\\", "/")
                   for row in manifest.get("regenerable", []) + manifest.get("generatedReports", []))
    for row in sources:
        label, root = row["name"], roots[row["name"]]
        excluded = row.get("exclude_library_storage", row.get("exclude_backup", False))
        for file in preserved[str(root)]["files"]:
            relative = file["path"]
            if excluded and relative.split("/")[0] in {"_backup", "_archive"}:
                continue
            if f"{label}/{relative}" not in covered:
                raise ValueError("unique generated source bytes absent from snapshot metadata")
    return preserved


def recovery_proof(proof, index):
    snapshot, recovered = proof / "snapshot", proof / "recovered"
    exact_snapshot(snapshot, index)
    manifest = archive.read_json(archive.metadata_bytes(snapshot / "manifest.json"))
    expected = {row["path"]: row for row in index["files"] if row["path"] != "manifest.json"}
    for relative, payload, entry in archive.backup._regenerated(snapshot, manifest):
        relative = archive.name(relative.as_posix())
        expected[relative] = {"path": relative, "size": len(payload),
                              "sha256": archive.sha(payload), "mtimeNs": entry["mtimeNs"]}
    actual = tree(recovered)
    if {r["path"]: r for r in actual["files"]} != expected:
        raise ValueError("ordinary recovery files/bytes/mtime or regenerated derivatives mismatch")
    directories = {row["path"] for row in index["directories"]}
    for relative in expected:
        parent = pathlib.PurePosixPath(relative).parent
        while str(parent) != ".":
            directories.add(parent.as_posix())
            parent = parent.parent
    if {r["path"] for r in actual["directories"]} != directories:
        raise ValueError("ordinary recovery directory membership mismatch")
    return {"snapshot": tree(snapshot), "recovered": actual}


def prepare(target, bundle, receipt, sample, proof, baseline, reason):
    target, bundle, receipt, sample, proof, baseline = map(
        scope, (target, bundle, receipt, sample, proof, baseline))
    if not reason or not reason.strip() or len(reason) > 2000:
        raise ValueError("explicit bounded --reason is required")
    separate(target, bundle, receipt, sample, proof, baseline)
    marker = read(sample)
    sample_root = sample.parent
    if (sample.name != "generated-sample.json" or marker.get("recipe") != SAMPLE
            or marker.get("syntheticOnly") is not True
            or target.parent != sample_root / "snapshots"
            or marker.get("snapshot") != str(target)
            or marker.get("comparison") != str(baseline)):
        raise ValueError("not an explicitly generated synthetic sample snapshot")
    if target.name in {"source", "Working", "work-root", "snapshots", "_backup"}:
        raise ValueError("broad or active source root refused")
    bundle_receipt, index = archive.check_bundle(bundle)
    if bundle_receipt["source"] != str(target):
        raise ValueError("archive source must be the exact retirement target")
    if marker.get("indexSha256") != archive.sha(archive.canonical(index)):
        raise ValueError("sample attestation does not bind this archive index")
    exact_snapshot(target, index)
    manifest = archive.read_json(archive.metadata_bytes(target / "manifest.json"))
    preserved = mapping(manifest, sample_root, index)
    for source in preserved:
        separate(target, scope(source))
    if any((target / name).exists() for name in
           ("Artists", "Various", "Characters", "People", "gallery", "_likeness")):
        raise ValueError("active library category root refused")
    proof_tree = recovery_proof(proof, index)
    baseline_tree = tree(baseline)
    if marker.get("comparisonSha256") != archive.sha(archive.canonical(baseline_tree)):
        raise ValueError("comparison baseline changed since sample creation")
    active_references(target, sample_root)
    return {"recipe": RECIPE, "state": "recycle-pending", "target": str(target),
            "bundle": str(bundle), "bundleReceipt": bundle_receipt, "index": index,
            "receipt": str(receipt), "sample": str(sample), "sampleData": marker,
            "recoveryProof": str(proof), "proofTrees": proof_tree,
            "comparison": str(baseline), "comparisonTree": baseline_tree,
            "sources": preserved, "reason": reason.strip(),
            "movedBytes": archive.metrics(index)["logicalBytes"],
            "storageFreedByRecycling": False}


def verify_evidence(data, receipt):
    if (data.get("recipe") != RECIPE or data["receipt"] != str(scope(receipt))
            or data["state"] not in {"recycle-pending", "recycled", "recovery-pending", "recovered"}):
        raise ValueError("receipt recipe/path/state mismatch")
    target, bundle, sample, proof, baseline = map(
        scope, (data["target"], data["bundle"], data["sample"],
                data["recoveryProof"], data["comparison"]))
    separate(target, bundle, scope(receipt), sample, proof, baseline)
    marker = read(sample)
    if marker != data["sampleData"] or marker.get("recipe") != SAMPLE:
        raise ValueError("sample marker changed")
    bundle_receipt, index = archive.check_bundle(bundle)
    if (bundle_receipt != data["bundleReceipt"] or index != data["index"]
            or bundle_receipt["source"] != str(target)):
        raise ValueError("independent archive changed")
    if tree(baseline) != data["comparisonTree"]:
        raise ValueError("comparison baseline changed")
    for source, expected in data["sources"].items():
        if tree(scope(source)) != expected:
            raise ValueError("generated source changed")
    if recovery_proof(proof, index) != data["proofTrees"]:
        raise ValueError("recovery proof changed")
    active_references(target, sample.parent)
    return target, index


def reconcile(data, receipt):
    target, index = verify_evidence(data, receipt)
    found = shell("inspect", target, data.get("identity"))
    identity = found.get("identity")
    exists = target.exists()
    if exists and identity:
        raise ValueError("both original and recycled item exist; ambiguous")
    if not exists and not identity:
        raise ValueError("neither original nor exact Recycle Bin item exists")
    if identity:
        if data.get("identity") and identity != data["identity"]:
            raise ValueError("Recycle Bin identity changed")
        item = archive.guarded(identity["itemPath"])
        if (identity["originalPath"].casefold()
                != str(target).removeprefix("\\\\?\\").casefold()
                or item.name[:2] != "$R" or "$Recycle.Bin" not in item.parts
                or item.drive.casefold() != target.drive.casefold()):
            raise ValueError("wrong Recycle Bin identity")
        exact_snapshot(item, index)
        state = "recycled"
    else:
        exact_snapshot(target, index)
        state = "recovered" if data["state"] in {"recovery-pending", "recovered"} else "ready"
    if data["state"] == "recycled" and state != "recycled":
        raise ValueError("recycled receipt has no actual recycled payload")
    if data["state"] == "recovered" and state != "recovered":
        raise ValueError("recovered receipt has no actual restored payload")
    return state, identity


@contextlib.contextmanager
def locked(receipt):
    """OS lock releases on interruption; leftover lock file is harmless."""
    import msvcrt
    path = scope(str(receipt) + ".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        if not stream.tell():
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        try:
            yield
        finally:
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def check(receipt):
    receipt = scope(receipt)
    data = read(receipt)
    state, identity = reconcile(data, receipt)
    result = {"actualState": state, "identity": identity,
              "movedBytes": data["movedBytes"], "storageFreedByRecycling": False}
    print(json.dumps(result))
    return result


def retire(target, bundle, receipt, sample, proof, baseline, reason, *, apply=False):
    receipt = scope(receipt)
    if receipt.exists():
        data = read(receipt)
        for key, value in (("target", target), ("bundle", bundle), ("sample", sample),
                           ("recoveryProof", proof), ("comparison", baseline)):
            if data[key] != str(scope(value)):
                raise ValueError("existing receipt argument mismatch")
        if data["reason"] != reason.strip():
            raise ValueError("existing receipt reason mismatch")
        state, identity = reconcile(data, receipt)
        if state != "ready":
            print(json.dumps({"actualState": state, "noOp": True}))
            return data
    else:
        data = prepare(target, bundle, receipt, sample, proof, baseline, reason)
        found = shell("inspect", scope(target))
        if found.get("identity"):
            raise ValueError("preexisting recycled item for target; refuse duplicate")
    print(json.dumps({"preview": not apply, "target": data["target"],
                      "movedBytes": data["movedBytes"],
                      "storageFreedByRecycling": False,
                      "warning": "Recycle Bin does not free storage; purge is not implemented"}))
    if not apply:
        return data
    with locked(receipt):
        if receipt.exists():
            data = read(receipt)
            state, _ = reconcile(data, receipt)
            if state != "ready":
                return data
        else:
            write(receipt, data, new=True)
        target, index = verify_evidence(data, receipt)
        exact_snapshot(target, index)
        data["diskFreeBefore"] = shutil.disk_usage(target).free
        write(receipt, data)
        # A failed/ interrupted API call deliberately leaves durable intent.
        shell("recycle", target)
        state, identity = reconcile(data, receipt)
        if state != "recycled":
            raise ValueError("Recycle Bin did not move the source")
        data.update(state="recycled", identity=identity,
                    diskFreeAfter=shutil.disk_usage(target.parent).free)
        data["observedDiskFreeDelta"] = data["diskFreeAfter"] - data["diskFreeBefore"]
        write(receipt, data)
        return data


def recover(receipt, *, apply=False):
    receipt = scope(receipt)
    data = read(receipt)
    state, identity = reconcile(data, receipt)
    if state == "ready":
        raise ValueError("retirement never occurred; nothing to recover")
    if state == "recovered":
        print("actual restored content and archive verified; no operation")
        if apply and data["state"] == "recovery-pending":
            with locked(receipt):
                data.update(state="recovered")
                write(receipt, data)
        return data
    print(f"recover exact recycled identity: {identity['itemPath']} -> {data['target']}")
    if not apply:
        return data
    with locked(receipt):
        data = read(receipt)
        state, identity = reconcile(data, receipt)
        if state != "recycled":
            raise ValueError("recovery state changed")
        data.update(state="recovery-pending", identity=identity)
        write(receipt, data)
        shell("recover", scope(data["target"]), identity)
        state, _ = reconcile(data, receipt)
        if state != "recovered":
            raise ValueError("undelete failed exact restored-content verification")
        data.update(state="recovered")
        write(receipt, data)
        return data


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "--check":
        argv[0] = "check"
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    retiring = sub.add_parser("retire")
    retiring.add_argument("target")
    for flag in ("bundle", "receipt", "sample", "recovery-proof", "comparison", "reason"):
        retiring.add_argument("--" + flag, required=True)
    recovering = sub.add_parser("recover")
    recovering.add_argument("--receipt", required=True)
    checking = sub.add_parser("check")
    checking.add_argument("receipt")
    for command in (retiring, recovering):
        action = command.add_mutually_exclusive_group()
        action.add_argument("--apply", action="store_true")
        action.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            check(args.receipt)
        elif args.command == "recover":
            recover(args.receipt, apply=args.apply)
        else:
            retire(args.target, args.bundle, args.receipt, args.sample,
                   args.recovery_proof, args.comparison, args.reason, apply=args.apply)
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError,
            subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print(f"backup retirement refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
