"""Replay reviewed Various cleanup decisions on a matching raw library copy."""

import argparse
import collections
import hashlib
import json
import ntpath
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.art import temporary_storage
from tools.art.likeness_library import sandbox

NAMED = {"Angels", "Sisters", "Models", "Prospects", "Potentials"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _digest(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value):
        raise ValueError(f"invalid SHA-256: {value!r}")
    return value


def _safe(root, relative):
    path = root
    for part in sandbox._safe_source_path(relative):
        reserved = ntpath.isreserved(part) if hasattr(ntpath, "isreserved") else pathlib.PureWindowsPath(part).is_reserved()
        if (part.rstrip(" .") != part or re.search(r'[<>"|?*\x00-\x1f]', part)
                or reserved):
            raise ValueError(f"unsafe Windows path: {relative}")
        path /= part
        if sandbox._is_reparse_point(path):
            raise ValueError(f"refusing linked path: {path}")
    return path


def _library(root, *, raw_only=True):
    if not root.is_absolute():
        raise ValueError("--root must be an absolute library path")
    if any(sandbox._is_reparse_point(path) for path in (root, *root.parents)):
        raise ValueError(f"refusing linked library path: {root}")
    root = root.resolve(strict=True)
    if root.name.casefold() != "sovereign territories" and not sandbox.is_sandbox_working_path(root):
        raise ValueError("use a Production copy or Sandbox Working, not sealed Source")
    if any(p.name.casefold() == "sovereign territories" for p in root.parents):
        raise ValueError("nested library roots are not supported")
    if not _safe(root, "Various/gallery").is_dir():
        raise ValueError("missing Various/gallery in selected library")
    if raw_only:
        for name in (".likeness-library.json", ".normal-history.json", "_processing", "_likeness"):
            if _safe(root, name).exists():
                raise ValueError(f"managed library has {name}; this tool is only for raw baselines")
    return root


def _read_bound(path, digest):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != _digest(digest):
        raise ValueError(f"file does not match the requested SHA-256: {path}")
    return json.loads(raw)


def export_plan(receipt_path, receipt_sha256):
    receipt = _read_bound(receipt_path, receipt_sha256)
    if receipt["kind"] != "normal-rebase-preview" or receipt["status"] != "preview":
        raise ValueError("expected a sealed SIMPLE preview")
    report = receipt["plan"]
    if report["unresolvedDuplicateIds"]:
        raise ValueError("preview contains unresolved IDs")
    groups = {}
    for row in report["sourceRows"]:
        if not row.get("photoId"):
            continue
        if report["sourceHashes"][row["source"]] != row["sourceHash"]:
            raise ValueError(f"preview source hash does not bind {row['source']}")
        groups.setdefault(row["photoId"], []).append(row)
    entries = []
    for photo_id, rows in sorted(groups.items()):
        incoming = [r for r in rows if r["source"].startswith("Various/gallery/")]
        named = [r for r in rows if r["group"] in NAMED]
        if not incoming or not named:
            continue
        if len(named) != 1 or any(r.get("retainedManifest") for r in (*incoming, *named)):
            raise ValueError(f"expected one raw named counterpart for {photo_id}")
        old, = named
        entries.append({
            "photoId": photo_id, "namedPath": old["source"], "namedSHA256": old["sourceHash"],
            "incoming": {r["source"]: r["sourceHash"] for r in incoming},
        })
    return {"schemaVersion": 1, "previewSHA256": receipt_sha256, "entries": entries}


def _entry(root, entry, archive_root):
    named = entry["namedPath"]
    parts = sandbox._safe_source_path(named)
    if len(parts) != 4 or parts[0] not in NAMED or parts[2] not in ("gallery", "review"):
        raise ValueError(f"not a named Gallery/Review original: {named}")
    target = _safe(root, named)
    if target.suffix.lower() not in IMAGE_EXT:
        raise ValueError(f"not a photo path: {target}")
    old_sha = _digest(entry["namedSHA256"])
    incoming = {}
    for path, digest in entry["incoming"].items():
        parts = sandbox._safe_source_path(path)
        if len(parts) != 3 or parts[:2] != ("Various", "gallery"):
            raise ValueError(f"not a Various Gallery original: {path}")
        source = _safe(root, path)
        if source.suffix.lower() not in IMAGE_EXT:
            raise ValueError(f"not a photo path: {source}")
        incoming[source] = _digest(digest)
    replacements = [p for p, sha in incoming.items() if sha != old_sha]
    if not incoming or len(replacements) > 1:
        raise ValueError(f"missing copies or ambiguous edited versions: {entry['photoId']}")
    edit = replacements[0] if replacements else None
    if edit and edit.suffix.lower().replace(".jpeg", ".jpg") != target.suffix.lower().replace(".jpeg", ".jpg"):
        raise ValueError(f"edited file format differs from the original name: {edit}")
    archive = _safe(root, f"{archive_root}/{named}") if edit else None
    return target, old_sha, incoming, edit, archive


def _file_sha(path):
    if not path.exists():
        return None
    if not path.is_file() or sandbox._is_reparse_point(path):
        raise ValueError(f"not a regular photo file: {path}")
    return sandbox._file_digest(path)


def _photo_paths(root, directory):
    if not directory.exists():
        return []
    return [
        _safe(root, path.relative_to(root).as_posix()) for path in sorted(directory.iterdir())
        if path.suffix.casefold() in IMAGE_EXT and (path.is_file() or sandbox._is_reparse_point(path))
    ]


def scan_exact(root):
    """Find redundant inputs without preparing any image or hashing unrelated named photos."""
    from tools.art import likeness, originals
    from tools.art.likeness_library import metadata, normal_import, retained_preparation

    root = _library(root, raw_only=False)
    cfg = likeness.configuration()
    chosen = list(cfg.get("photos", {}).values())
    for flow in cfg.get("flows", {}).values():
        chosen.extend(flow.get("photos", {}).values())
    protected_names = {pathlib.PureWindowsPath(name).name.casefold() for name in chosen if isinstance(name, str)}

    def photo_id(path):
        return metadata.photo_id_from_name(normal_import._arrival_name(path, originals, metadata))

    def relative(path):
        return path.relative_to(root).as_posix()

    incoming, owners = collections.defaultdict(list), collections.defaultdict(list)
    for path in _photo_paths(root, _safe(root, "Various/gallery")):
        incoming[photo_id(path)].append(path)
    if incoming:
        for group in sorted(NAMED):
            category = _safe(root, group)
            for person in sorted(category.iterdir()) if category.is_dir() else ():
                if not person.is_dir():
                    continue
                for bucket in ("gallery", "review"):
                    for path in _photo_paths(root, _safe(root, f"{group}/{person.name}/{bucket}")):
                        pid = photo_id(path)
                        if pid in incoming:
                            owners[pid].append(path)
    entries = []
    for pid, arrivals in sorted(incoming.items()):
        named = owners[pid]
        if len(named) == 1:
            keeper = named[0]
            candidates = [p for p in arrivals if p.stat().st_size == keeper.stat().st_size]
        elif not named and len(arrivals) > 1:
            # Do not change the winner of any mixed-byte incoming version group.
            if len({p.stat().st_size for p in arrivals}) != 1 or len({_file_sha(p) for p in arrivals}) != 1:
                continue
            keeper = max(arrivals, key=lambda p: (p.name.casefold() in protected_names, p.stat().st_mtime_ns, p.name))
            candidates = [p for p in arrivals if p != keeper]
        else:
            continue
        if not candidates or (
            retained_preparation.claims_photo(root, keeper)
            and retained_preparation.verify_link(root, keeper, pid) is None
        ):
            continue
        digest = _file_sha(keeper)
        for path in candidates:
            if (path.name.casefold() not in protected_names
                    and not retained_preparation.claims_photo(root, path)
                    and _file_sha(path) == digest):
                entries.append({"photoId": pid, "discard": relative(path), "keeper": relative(keeper), "sha256": digest})
    return {"schemaVersion": 1, "kind": "exact-arrival-discard", "root": str(root), "entries": entries}


def run_exact(root, plan, mode):
    root = _library(root, raw_only=False)
    if plan["schemaVersion"] != 1 or plan["root"] != str(root):
        raise ValueError("exact-arrival plan belongs to a different root or schema")
    entries = plan["entries"]
    removed = {row["discard"].casefold() for row in entries}
    if len(removed) != len(entries) or any(row["keeper"].casefold() in removed for row in entries):
        raise ValueError("plan must retain a separate keeper for every discard")

    def execute():
        pending = []
        for row in entries:
            parts = sandbox._safe_source_path(row["discard"])
            if len(parts) != 3 or parts[:2] != ("Various", "gallery"):
                raise ValueError("only Various/gallery arrivals can be discarded")
            source, keeper = (_safe(root, row[key]) for key in ("discard", "keeper"))
            digest = _digest(row["sha256"])
            actual = _file_sha(source)
            if _file_sha(keeper) != digest or (actual is not None and actual != digest):
                raise ValueError(f"exact-arrival evidence changed: {source}")
            if actual is not None:
                pending.append(row)
        if mode == "check" and pending:
            raise ValueError(f"{len(pending)} exact arrivals are still present")
        if mode == "apply" and pending:
            current = {row["discard"]: row for row in scan_exact(root)["entries"]}
            if any(row != current.get(row["discard"]) for row in pending):
                raise ValueError("current selection or keeper changed; scan again before discarding")
            for row in pending:
                source, keeper = (_safe(root, row[key]) for key in ("discard", "keeper"))
                if _file_sha(source) != row["sha256"] or _file_sha(keeper) != row["sha256"]:
                    raise ValueError(f"exact-arrival evidence changed: {source}")
                source.unlink()
                if source.exists() or _file_sha(keeper) != row["sha256"]:
                    raise ValueError(f"discard verification failed: {source}")
        return {**plan, "mode": mode, "pendingBefore": len(pending),
                "discarded": len(pending) if mode == "apply" else 0}

    if mode == "apply" and entries:
        with temporary_storage.resumable_staging_directory(_safe(root, "_archive/various-cleanup"), "operation") as lock_dir:
            result = execute()
            lock_dir.rmdir()
            return result
    return execute()


def _state(operation):
    target, old_sha, incoming, edit, archive = operation
    current = _file_sha(target)
    saved = _file_sha(archive) if archive else None
    files = {path: _file_sha(path) for path in incoming}
    for path, actual in files.items():
        if actual is not None and actual != incoming[path]:
            raise ValueError(f"incoming original has changed: {path}")
    if not edit and current == old_sha:
        return "kept", files
    if edit:
        if saved is None and current == old_sha and files[edit] is not None:
            return "replace", files
        if saved == old_sha and current is None and files[edit] is not None:
            return "resume-replacement", files
        if saved == old_sha and current == incoming[edit] and files[edit] is None:
            return "replaced", files
    raise ValueError(f"original, edited copy or archive does not match the plan: {target}")


def run(root, plan_path, plan_sha256, mode):
    root = _library(root)
    plan = _read_bound(plan_path, plan_sha256)
    if plan["schemaVersion"] != 1 or not plan["entries"]:
        raise ValueError("unsupported or empty cleanup plan")
    archive_root = f"_archive/various-cleanup/{plan_sha256[:16]}"
    archive = _safe(root, archive_root)
    seen_paths = set()
    seen_ids = set()
    operations = []
    for entry in plan["entries"]:
        operation = _entry(root, entry, archive_root)
        target, _, incoming, _, _ = operation
        paths = {str(path).casefold() for path in (target, *incoming)}
        if paths & seen_paths or len(paths) != len(incoming) + 1 or entry["photoId"] in seen_ids:
            raise ValueError(f"plan contains duplicate IDs or paths: {target}")
        seen_ids.add(entry["photoId"])
        seen_paths.update(paths)
        operations.append(operation)

    def execute():
        states, errors = [], []
        for operation in operations:
            try:
                states.append(_state(operation))
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
        if errors:
            raise ValueError(f"{len(errors)} group(s) fail preflight; nothing changed: " + "; ".join(errors[:8]))
        pending_removals = sum(
            actual is not None for operation, (_, files) in zip(operations, states)
            for path, actual in files.items() if path != operation[3]
        )
        pending_replacements = sum(state in ("replace", "resume-replacement") for state, _ in states)
        if mode == "check" and (pending_replacements or pending_removals):
            raise ValueError(f"incomplete: {pending_removals} exact copies and {pending_replacements} edits pending")
        if mode == "apply":
            for operation, (state, files) in zip(operations, states):
                if state in ("kept", "replaced") and not any(files.values()):
                    continue
                _apply_one(operation)
            if any(state not in ("kept", "replaced") or any(files.values())
                   for state, files in map(_state, operations)):
                raise ValueError("cleanup verification found pending work")
        return {
            "mode": mode, "root": str(root), "archiveRoot": str(archive),
            "planSHA256": plan_sha256, "groups": len(operations),
            "exactCopiesInPlan": sum(len(op[2]) - int(op[3] is not None) for op in operations),
            "editsInPlan": sum(op[3] is not None for op in operations),
            "pendingExactCopiesBefore": pending_removals,
            "pendingEditsBefore": pending_replacements,
        }

    if mode == "apply":
        with temporary_storage.resumable_staging_directory(archive.parent, "operation") as lock_dir:
            result = execute()
            lock_dir.rmdir()
            return result
    return execute()


def _apply_one(operation):
    target, old_sha, incoming, edit, archive = operation
    state, files = _state(operation)
    if state == "replace":
        archive.parent.mkdir(parents=True, exist_ok=True)
        if _file_sha(archive) is not None:
            raise ValueError(f"archive already exists: {archive}")
        target.rename(archive)
        state = "resume-replacement"
    if state == "resume-replacement":
        if _state(operation)[0] != "resume-replacement":
            raise ValueError(f"replacement changed during archive: {target}")
        edit.rename(target)
    keeper = archive if edit else target
    for source in files:
        if source == edit or files[source] is None:
            continue
        if _file_sha(keeper) != old_sha or _file_sha(source) != incoming[source]:
            raise ValueError(f"exact copy changed before removal: {source}")
        source.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path)
    parser.add_argument("--plan", type=pathlib.Path)
    parser.add_argument("--sha256", help="known SHA-256 of the plan or preview receipt")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--scan-exact", action="store_true", help="print a same-ID, byte-identical discard plan for this root")
    mode.add_argument("--export-preview", type=pathlib.Path, help="read a SIMPLE preview and print a portable plan")
    parser.add_argument("--backup-confirmed", action="store_true", help="confirm exact incoming copies may be removed")
    args = parser.parse_args(argv)
    if args.scan_exact:
        if not args.root or args.plan or args.sha256 or args.backup_confirmed:
            parser.error("--scan-exact requires only --root")
    elif args.export_preview:
        if args.root or args.plan or args.backup_confirmed or not args.sha256:
            parser.error("--export-preview only requires --sha256")
    elif not args.root or not args.plan or not args.sha256 or (args.apply and not args.backup_confirmed):
        parser.error("--root, --plan and --sha256 required; --apply also requires --backup-confirmed")
    try:
        if args.scan_exact:
            result = scan_exact(args.root)
        elif args.export_preview:
            result = export_plan(args.export_preview, args.sha256)
        else:
            operation = "apply" if args.apply else "check" if args.check else "preview"
            plan = _read_bound(args.plan, args.sha256)
            if plan.get("kind") == "exact-arrival-discard":
                result = run_exact(args.root, plan, operation)
            else:
                result = run(args.root, args.plan, args.sha256, operation)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        parser.exit(2, f"various cleanup stopped: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
