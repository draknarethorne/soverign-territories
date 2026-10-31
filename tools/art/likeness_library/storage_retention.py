#!/usr/bin/env python3
"""Preview and explicitly apply dependency-aware sandbox run retention."""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/art"))
sys.path.insert(0, str(ROOT))
from . import preparation_history, report_assets, sandbox  # noqa: E402
from tools.workflows import comfy_workflows as cw  # noqa: E402


MANIFEST_NAME = "retention-manifest.json"
POLICY = {"latestAcceptedPerPipeline": 1, "explicitPruneApproval": True}
CLASSES = {"active", "review", "accepted", "superseded", "pruned"}
TEXT_SUFFIXES = {".csv", ".html", ".json", ".log", ".md", ".txt", ".xml", ".yaml", ".yml"}
MAX_RUN_MANIFEST_BYTES = 64 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
RUN_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _working_root(value):
    root = pathlib.Path(value).expanduser().resolve(strict=True)
    if not sandbox.is_sandbox_working_path(root):
        raise ValueError("storage retention requires the exact sandbox Working directory")
    if sandbox._is_reparse_point(root):
        raise ValueError(f"refusing linked Working root: {root}")
    return root


def _roots(root, cfg):
    state = cw.storage_root(cfg, "sandboxState", root=root)
    reports = cw.storage_root(cfg, "reports", root=root)
    if root == state or root not in state.parents:
        raise ValueError(f"configured sandbox-state root must remain inside Working: {state}")
    if root == reports or root not in reports.parents:
        raise ValueError(f"configured reports root must remain inside Working: {reports}")
    return state, reports


def _run_name(value):
    if not isinstance(value, str) or not RUN_NAME.fullmatch(value) or value in {".", ".."}:
        raise ValueError(f"invalid sandbox run ID: {value!r}")
    return value


def _read_json(path, limit=MAX_RUN_MANIFEST_BYTES):
    if sandbox._is_reparse_point(path) or not path.is_file():
        raise ValueError(f"missing or unsafe run manifest: {path}")
    if path.stat().st_size > limit:
        raise ValueError(f"run manifest exceeds {limit} bytes: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"run manifest must contain an object: {path}")
    return value


def _file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def _file_signature(path):
    stat_result = path.stat()
    return stat_result.st_size, stat_result.st_mtime_ns


def _run_manifests(run):
    result = {}
    for name in ("run.json", "intake.json"):
        path = run / name
        if path.exists():
            before = _file_signature(path)
            value = _read_json(path)
            digest = _file_sha256(path)
            if _file_signature(path) != before:
                raise ValueError(f"run manifest changed while being read: {path}")
            result[name] = {
                "value": value,
                "sha256": digest,
            }
    return result


def _manifest_hashes(run):
    hashes = {}
    for name in ("run.json", "intake.json"):
        path = run / name
        if path.exists():
            if sandbox._is_reparse_point(path) or not path.is_file():
                raise ValueError(f"missing or unsafe run manifest: {path}")
            before = _file_signature(path)
            if before[0] > MAX_RUN_MANIFEST_BYTES:
                raise ValueError(f"run manifest exceeds {MAX_RUN_MANIFEST_BYTES} bytes: {path}")
            digest = _file_sha256(path)
            if _file_signature(path) != before:
                raise ValueError(f"run manifest changed while being fingerprinted: {path}")
            hashes[name] = digest
    return hashes


def _pipeline(manifests):
    run = manifests.get("run.json", {}).get("value", {})
    intake = manifests.get("intake.json", {}).get("value", {})
    value = run.get("mode")
    if isinstance(value, str) and value:
        return value
    recipe = intake.get("recipe")
    if isinstance(recipe, dict) and isinstance(recipe.get("id"), str):
        return recipe["id"]
    return "unclassified"


def _run_status(manifests):
    run = manifests.get("run.json", {}).get("value", {})
    if isinstance(run.get("status"), str):
        return run["status"]
    return "intake" if "intake.json" in manifests else "unclassified"


def _new_manifest(cfg, root, state):
    path = state / MANIFEST_NAME
    return {
        "schemaVersion": 1,
        "policy": dict(POLICY),
        "updatedAt": _now(),
        "runs": {},
        "configurationReceipt": cw.storage_configuration_receipt(
            cfg, root, {"sandboxStateRoot": state, "retentionManifest": path}
        ),
    }


def _load_manifest(cfg, root, state):
    path = state / MANIFEST_NAME
    if not path.exists():
        return _new_manifest(cfg, root, state)
    document = _read_json(path)
    if document.get("schemaVersion") != 1 or document.get("policy") != POLICY:
        raise ValueError(f"unsupported retention manifest or policy: {path}")
    if not isinstance(document.get("runs"), dict):
        raise ValueError(f"retention manifest runs must be an object: {path}")
    for name, record in document["runs"].items():
        _run_name(name)
        if not isinstance(record, dict) or record.get("retentionClass") not in CLASSES:
            raise ValueError(f"invalid retention record for run {name}")
    return document


def _write_json_atomic(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with pending.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(pending, path)
    finally:
        if pending.exists():
            pending.unlink()


def _discover_runs(state):
    if not state.exists():
        return []
    if sandbox._is_reparse_point(state) or not state.is_dir():
        raise ValueError(f"refusing unsafe sandbox-state root: {state}")
    runs = []
    for path in sorted(state.iterdir(), key=lambda item: item.name.casefold()):
        if not path.is_dir():
            continue
        if sandbox._is_reparse_point(path):
            raise ValueError(f"refusing linked run directory: {path}")
        runs.append(path)
    return runs


def _register_record(manifests):
    return {
        "pipeline": _pipeline(manifests),
        "runStatus": _run_status(manifests),
        "retentionClass": "review",
        "registeredAt": _now(),
        "acceptedAt": None,
        "reviewCleared": False,
        "undoCleared": False,
        "auditCleared": False,
        "pruneApproved": False,
        "reason": "Registered; awaiting explicit review and disposition.",
        "manifestHashes": {
            name: value["sha256"] for name, value in manifests.items()
        },
    }


def register_runs(root, cfg, run_names=None, register_all=False):
    state, _ = _roots(root, cfg)
    manifest_path = state / MANIFEST_NAME
    document = _load_manifest(cfg, root, state)
    found = {path.name: path for path in _discover_runs(state)}
    if register_all:
        selected = []
        skipped = []
        for name, run in sorted(found.items()):
            if _run_manifests(run):
                selected.append(name)
            else:
                skipped.append(name)
    else:
        selected = [_run_name(name) for name in (run_names or [])]
        skipped = []
    if not selected:
        raise ValueError("register requires --all or one or more --run IDs")
    changed = []
    for name in selected:
        run = found.get(name)
        if run is None:
            raise ValueError(f"run directory does not exist: {name}")
        manifests = _run_manifests(run)
        if not manifests:
            raise ValueError(f"run has no supported run.json or intake.json receipt: {run}")
        prior = document["runs"].get(name)
        if prior is None:
            document["runs"][name] = _register_record(manifests)
        else:
            old_hashes = prior.get("manifestHashes", {})
            new_hashes = {key: value["sha256"] for key, value in manifests.items()}
            if old_hashes != new_hashes:
                prior["manifestHashes"] = new_hashes
                prior["pipeline"] = _pipeline(manifests)
                prior["runStatus"] = _run_status(manifests)
                prior["pruneApproved"] = False
                prior.pop("approvedTreeSha256", None)
                prior.pop("approvedFiles", None)
                prior.pop("approvedBytes", None)
                prior.pop("pruneState", None)
                if prior.get("retentionClass") in {"accepted", "superseded"}:
                    prior["retentionClass"] = "review"
                    prior["acceptedAt"] = None
                    prior["reviewCleared"] = False
                    prior["undoCleared"] = False
                    prior["auditCleared"] = False
                    prior["reason"] = "Run manifest changed; explicit review and acceptance required again."
            changed.append(name)
    document["updatedAt"] = _now()
    _write_json_atomic(manifest_path, document)
    return {
        "manifest": manifest_path,
        "registered": selected,
        "refreshed": changed,
        "skipped": skipped,
    }


def _latest_accepted(document):
    latest = {}
    for name, record in document["runs"].items():
        if record.get("retentionClass") != "accepted":
            continue
        pipeline = record.get("pipeline")
        accepted_at = record.get("acceptedAt")
        if not isinstance(pipeline, str) or not pipeline or not isinstance(accepted_at, str):
            continue
        candidate = (accepted_at, name.casefold(), name)
        if pipeline not in latest or candidate > latest[pipeline]:
            latest[pipeline] = candidate
    return {entry[2] for entry in latest.values()}


def _walk_files(root):
    def raise_walk_error(error):
        raise error

    for current, directories, names in os.walk(
        root, followlinks=False, onerror=raise_walk_error
    ):
        base = pathlib.Path(current)
        for name in list(directories):
            path = base / name
            if sandbox._is_reparse_point(path):
                raise ValueError(f"refusing reparse point in run tree: {path}")
        directories.sort(key=str.casefold)
        for name in sorted(names, key=str.casefold):
            path = base / name
            if sandbox._is_reparse_point(path) or not path.is_file():
                raise ValueError(f"refusing non-regular run artifact: {path}")
            yield path


def _tree_inventory(run, hash_contents=False):
    files = 0
    total_bytes = 0
    tree_hash = hashlib.sha256()
    for path in _walk_files(run):
        relative = path.relative_to(run).as_posix()
        signature = _file_signature(path)
        size = signature[0]
        files += 1
        total_bytes += size
        if hash_contents:
            tree_hash.update(relative.encode("utf-8"))
            tree_hash.update(b"\0")
            tree_hash.update(str(size).encode("ascii"))
            tree_hash.update(b"\0")
            digest = _file_sha256(path)
            if _file_signature(path) != signature:
                raise ValueError(f"run artifact changed while being fingerprinted: {path}")
            tree_hash.update(digest.encode("ascii"))
            tree_hash.update(b"\n")
    return {
        "files": files,
        "bytes": total_bytes,
        "treeSha256": tree_hash.hexdigest() if hash_contents else None,
    }


def _workspace_references(root, state, reports, run_names):
    names = {name: name.casefold().encode("utf-8") for name in run_names}
    references = {name: [] for name in run_names}
    if not names:
        return references, []
    if not root.exists():
        return references, []
    if sandbox._is_reparse_point(root):
        raise ValueError(f"refusing linked Working root: {root}")
    scan_errors = []

    def raise_walk_error(error):
        raise error

    for current, directories, filenames in os.walk(
        root, followlinks=False, onerror=raise_walk_error
    ):
        base = pathlib.Path(current)
        retained_directories = []
        for directory in directories:
            path = base / directory
            if path == reports / "storage-retention":
                continue
            if sandbox._is_reparse_point(path):
                raise ValueError(f"refusing reparse point in Working: {path}")
            retained_directories.append(directory)
        directories[:] = sorted(retained_directories, key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            path = base / filename
            if path == state / MANIFEST_NAME or path.parent == reports / "storage-retention":
                continue
            if sandbox._is_reparse_point(path):
                raise ValueError(f"refusing linked Working file: {path}")
            if (
                path.name.casefold() == "intake_runs.html"
                and (path.parent == reports or reports in path.parents)
            ):
                continue
            if path.suffix.casefold() not in TEXT_SUFFIXES:
                continue
            unresolved = set(names)
            tail = b""
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
                    data = (tail + block).lower()
                    for run_name in tuple(unresolved):
                        if state / run_name == path.parent or state / run_name in path.parents:
                            continue
                        if names[run_name] in data:
                            references[run_name].append(str(path))
                            unresolved.remove(run_name)
                    if not unresolved:
                        break
                    tail = data[-max((len(names[name]) for name in unresolved), default=1):]
    return references, scan_errors


def _manifest_matches(record, manifests):
    actual = {name: value["sha256"] for name, value in manifests.items()}
    return bool(actual) and actual == record.get("manifestHashes")


def _manifest_hashes_match(record, hashes):
    return bool(hashes) and hashes == record.get("manifestHashes")


def preview(root, cfg):
    state, reports = _roots(root, cfg)
    document = _load_manifest(cfg, root, state)
    directories = _discover_runs(state)
    directory_names = {run.name for run in directories}
    latest = _latest_accepted(document)
    entries = []
    provisional = []
    for run in directories:
        name = run.name
        record = document["runs"].get(name)
        hashes = _manifest_hashes(run) if record else {}
        entry = {
            "runId": name,
            "pipeline": record.get("pipeline", "unclassified") if record else "unclassified",
            "status": record.get("runStatus", "unclassified") if record else "unregistered",
            "retentionClass": record.get("retentionClass") if record else None,
            "files": None,
            "bytes": None,
            "disposition": "keep",
            "reasons": [],
        }
        if not record:
            entry["reasons"].append("unregistered; default keep")
        elif record.get("pruneState") in {"deleting", "partial"}:
            entry["disposition"] = "blocked"
            entry["reasons"].append("interrupted or partial prune needs receipt reconciliation")
        elif record.get("retentionClass") == "pruned":
            entry["disposition"] = "blocked"
            entry["reasons"].append("manifest says pruned but directory still exists")
        elif not _manifest_hashes_match(record, hashes):
            entry["disposition"] = "blocked"
            entry["reasons"].append("run manifest changed or is missing; re-register and review")
        elif record.get("retentionClass") == "active":
            entry["reasons"].append("current/active run")
        elif record.get("retentionClass") == "accepted" and name in latest:
            entry["reasons"].append("latest accepted run for its pipeline")
        elif record.get("retentionClass") != "superseded":
            entry["reasons"].append("review or accepted history is retained")
        elif not record.get("pruneApproved"):
            entry["reasons"].append("explicit prune approval is missing")
        elif not all(record.get(flag) is True for flag in (
            "reviewCleared", "undoCleared", "auditCleared",
        )):
            entry["reasons"].append("review, undo, or audit hold is not cleared")
        elif entry["status"] == "applied" and not record.get("undoCleared"):
            entry["reasons"].append("applied run still has undo data")
        elif not record.get("approvedTreeSha256"):
            entry["reasons"].append("approved content fingerprint is missing")
        else:
            entry["disposition"] = "candidate"
            provisional.append(entry)
        entries.append(entry)

    for name, record in document["runs"].items():
        if name not in directory_names and record.get("retentionClass") == "pruned":
            receipt_value = record.get("receipt")
            receipt_dir = reports / "storage-retention"
            receipt_path = pathlib.Path(receipt_value) if isinstance(receipt_value, str) else None
            valid_receipt = (
                receipt_path is not None
                and receipt_path.is_absolute()
                and receipt_path.parent == receipt_dir
                and not sandbox._is_reparse_point(receipt_dir)
                and receipt_path.is_file()
                and not sandbox._is_reparse_point(receipt_path)
            )
            status = None
            if valid_receipt:
                receipt = _read_json(receipt_path)
                if (
                    receipt.get("runId") == name
                    and receipt.get("workingRoot") == str(root)
                    and receipt.get("runPath") == str(state / name)
                ):
                    status = receipt.get("status")
            if record.get("pruneState") != "complete" or status != "complete":
                entries.append({
                    "runId": name,
                    "pipeline": record.get("pipeline", "unclassified"),
                    "status": "pruned",
                    "retentionClass": "pruned",
                    "files": 0,
                    "bytes": 0,
                    "disposition": "blocked",
                    "reasons": ["pruned run lacks a complete, verified retention receipt"],
                })
        elif name not in directory_names:
            entries.append({
                "runId": name,
                "pipeline": record.get("pipeline", "unclassified"),
                "status": "missing",
                "retentionClass": record.get("retentionClass"),
                "files": 0,
                "bytes": 0,
                "disposition": "blocked",
                "reasons": [
                    "registered run directory is missing; reconcile its retention receipt"
                ],
            })

    reference_map, scan_errors = _workspace_references(
        root, state, reports, [entry["runId"] for entry in provisional]
    )
    for entry in provisional:
        refs = reference_map[entry["runId"]]
        if refs:
            entry["disposition"] = "keep"
            entry["reasons"].append("referenced by non-regenerable report(s)")
            entry["references"] = refs
        else:
            run = state / entry["runId"]
            fingerprint = _tree_inventory(run, hash_contents=True)
            record = document["runs"][entry["runId"]]
            entry["files"] = fingerprint["files"]
            entry["bytes"] = fingerprint["bytes"]
            if fingerprint["treeSha256"] != record["approvedTreeSha256"]:
                entry["disposition"] = "blocked"
                entry["reasons"].append("run contents changed after prune approval")
            else:
                entry["approvedTreeSha256"] = fingerprint["treeSha256"]
                entry["reasons"].append("approved; no external report dependencies")
    return {
        "schemaVersion": 1,
        "previewOnly": True,
        "workingRoot": str(root),
        "sandboxStateRoot": str(state),
        "reportsRoot": str(reports),
        "retentionManifest": str(state / MANIFEST_NAME),
        "policy": document["policy"],
        "unregisteredRunCount": sum(
            1 for entry in entries if entry["retentionClass"] is None
        ),
        "blockedRunCount": sum(
            1 for entry in entries if entry["disposition"] == "blocked"
        ),
        "blockedReportScanErrors": scan_errors,
        "runs": entries,
    }


def _update_manifest(root, cfg, state, mutate):
    path = state / MANIFEST_NAME
    document = _load_manifest(cfg, root, state)
    mutate(document)
    document["updatedAt"] = _now()
    if not document.get("configurationReceipt"):
        document["configurationReceipt"] = cw.storage_configuration_receipt(
            cfg, root, {"sandboxStateRoot": state, "retentionManifest": path}
        )
    _write_json_atomic(path, document)
    return document


def accept_run(root, cfg, run_name, reason):
    name = _run_name(run_name)
    if not reason.strip():
        raise ValueError("acceptance requires a non-empty reason")
    state, _ = _roots(root, cfg)
    run = state / name
    manifests = _run_manifests(run)
    if not manifests:
        raise ValueError(f"run has no supported manifest: {run}")
    if _run_status(manifests) != "applied":
        raise ValueError("only a successfully applied run can be accepted")

    def mutate(document):
        record = document["runs"].get(name)
        if not record or not _manifest_matches(record, manifests):
            raise ValueError("run must be registered with current manifest hashes before acceptance")
        if record.get("retentionClass") == "pruned":
            raise ValueError("a pruned run cannot be accepted")
        record.update({
            "pipeline": _pipeline(manifests),
            "runStatus": _run_status(manifests),
            "retentionClass": "accepted",
            "acceptedAt": _now(),
            "reviewCleared": True,
            "auditCleared": True,
            "undoCleared": False,
            "pruneApproved": False,
            "reason": reason,
        })
        record.pop("approvedTreeSha256", None)
        record.pop("approvedFiles", None)
        record.pop("approvedBytes", None)

    _update_manifest(root, cfg, state, mutate)


def approve_prune(root, cfg, run_name, reason, *, review_cleared, undo_cleared, audit_cleared):
    name = _run_name(run_name)
    if not reason.strip():
        raise ValueError("prune approval requires a non-empty reason")
    state, reports = _roots(root, cfg)
    run = state / name
    manifests = _run_manifests(run)
    if not manifests:
        raise ValueError(f"run has no supported manifest: {run}")
    document = _load_manifest(cfg, root, state)
    record = document["runs"].get(name)
    if not record or not _manifest_matches(record, manifests):
        raise ValueError("run must be registered with current manifest hashes before prune approval")
    if record.get("retentionClass") not in {"accepted", "superseded"}:
        raise ValueError("only previously accepted historical runs can be superseded")
    if _run_status(manifests) not in {"applied", "undone"}:
        raise ValueError("incomplete or unapplied runs are always retained")
    if name in _latest_accepted(document):
        raise ValueError("the latest accepted run for its pipeline must be retained")
    if not (review_cleared and undo_cleared and audit_cleared):
        raise ValueError("prune approval requires explicit review, undo, and audit clearance")
    references, _ = _workspace_references(root, state, reports, [name])
    if references[name]:
        raise ValueError(
            "run is referenced by non-regenerable reports: " + "; ".join(references[name])
        )
    fingerprint = _tree_inventory(run, hash_contents=True)
    record.update({
        "pipeline": _pipeline(manifests),
        "runStatus": _run_status(manifests),
        "retentionClass": "superseded",
        "reviewCleared": True,
        "undoCleared": True,
        "auditCleared": True,
        "pruneApproved": True,
        "pruneState": "approved",
        "reason": reason,
        "manifestHashes": {key: value["sha256"] for key, value in manifests.items()},
        "approvedTreeSha256": fingerprint["treeSha256"],
        "approvedFiles": fingerprint["files"],
        "approvedBytes": fingerprint["bytes"],
        "approvedAt": _now(),
    })
    record.pop("acceptedAt", None)
    document["updatedAt"] = _now()
    _write_json_atomic(state / MANIFEST_NAME, document)
    return fingerprint


def _refresh_history_pages(root, cfg, reports):
    pages = []
    if not reports.exists():
        return pages
    for path in _walk_files(reports):
        if path.name.casefold() == "intake_runs.html":
            pages.append(path)
    for page in pages:
        domain = "artists" if page.parent.name.casefold() == "artists" else "general"
        preparation_history.publish_staged(root, page.parent, domain=domain, cfg=cfg)
        payload = page.read_bytes()
        people_manifest = page.parent / report_assets.MANIFEST
        if people_manifest.is_file():
            report_assets.record(page.parent, {page.name: payload})
        artist_manifest = page.parent / "gallery-manifest.json"
        if artist_manifest.is_file():
            value = _read_json(artist_manifest)
            files = value.get("files")
            if not isinstance(files, dict):
                raise ValueError(f"invalid artist gallery manifest: {artist_manifest}")
            files[page.name] = hashlib.sha256(payload).hexdigest()
            _write_json_atomic(artist_manifest, value)
    return [str(path) for path in pages]


def delete_run(root, cfg, run_name):
    name = _run_name(run_name)
    state, reports = _roots(root, cfg)
    current = preview(root, cfg)
    entry = next((item for item in current["runs"] if item["runId"] == name), None)
    if entry is None:
        raise ValueError(f"run directory does not exist: {name}")
    if entry["disposition"] != "candidate":
        raise ValueError(f"run is not safe to prune: {'; '.join(entry['reasons'])}")
    record = _load_manifest(cfg, root, state)["runs"][name]
    target = state / name
    if sandbox._is_reparse_point(target) or target.resolve(strict=True).parent != state.resolve(strict=True):
        raise ValueError(f"refusing unsafe run deletion target: {target}")
    fingerprint = _tree_inventory(target, hash_contents=True)
    if fingerprint["treeSha256"] != record.get("approvedTreeSha256"):
        raise ValueError("run contents changed after prune approval")

    receipt_dir = reports / "storage-retention"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / f"retention-{datetime.datetime.now(datetime.timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}.json"
    receipt = {
        "receiptPath": str(receipt_path),
        "schemaVersion": 1,
        "status": "deleting",
        "createdAt": _now(),
        "workingRoot": str(root),
        "runId": name,
        "runPath": str(target),
        "runPipeline": record["pipeline"],
        "tree": fingerprint,
        "reason": record["reason"],
        "configurationReceipt": cw.storage_configuration_receipt(
            cfg, root, {"sandboxStateRoot": state, "retentionManifest": state / MANIFEST_NAME,
                        "reportsRoot": reports, "runPath": target, "retentionReceipt": receipt_path}
        ),
        "deleted": False,
        "refreshedHistoryPages": [],
    }
    _write_json_atomic(receipt_path, receipt)
    try:
        document = _load_manifest(cfg, root, state)
        record = document["runs"][name]
        record["pruneState"] = "deleting"
        record["receipt"] = str(receipt_path)
        document["updatedAt"] = _now()
        _write_json_atomic(state / MANIFEST_NAME, document)
        shutil.rmtree(target)
        receipt["deleted"] = True
        record.update({
            "retentionClass": "pruned",
            "prunedAt": _now(),
            "pruneState": "complete",
        })
        record.pop("approvedTreeSha256", None)
        document["updatedAt"] = _now()
        _write_json_atomic(state / MANIFEST_NAME, document)
        _write_json_atomic(receipt_path, receipt)
        receipt["refreshedHistoryPages"] = _refresh_history_pages(root, cfg, reports)
        receipt["status"] = "complete"
        receipt["completedAt"] = _now()
        _write_json_atomic(receipt_path, receipt)
    except (OSError, ValueError):
        receipt["status"] = "partial"
        receipt["completedAt"] = _now()
        _write_json_atomic(receipt_path, receipt)
        if target.exists():
            document = _load_manifest(cfg, root, state)
            document["runs"][name]["pruneState"] = "partial"
            document["updatedAt"] = _now()
            _write_json_atomic(state / MANIFEST_NAME, document)
        raise
    return receipt


def repair_history(root, cfg, run_name):
    name = _run_name(run_name)
    state, reports = _roots(root, cfg)
    document = _load_manifest(cfg, root, state)
    record = document["runs"].get(name)
    if not record or record.get("retentionClass") != "pruned":
        raise ValueError(f"run is not recorded as pruned: {name}")
    if (state / name).exists():
        raise ValueError("run directory still exists; resolve the partial prune before refreshing history")
    receipt_value = record.get("receipt")
    receipt_dir = reports / "storage-retention"
    receipt_path = pathlib.Path(receipt_value) if isinstance(receipt_value, str) else None
    if (
        receipt_path is None
        or not receipt_path.is_absolute()
        or receipt_path.parent != receipt_dir
        or sandbox._is_reparse_point(receipt_dir)
        or not receipt_path.is_file()
        or sandbox._is_reparse_point(receipt_path)
    ):
        raise ValueError("pruned run has no safe retention receipt to repair")
    receipt = _read_json(receipt_path)
    if (
        receipt.get("runId") != name
        or receipt.get("workingRoot") != str(root)
        or receipt.get("runPath") != str(state / name)
    ):
        raise ValueError("retention receipt identity does not match the pruned run")
    if receipt.get("status") not in {"deleting", "partial"}:
        raise ValueError("retention receipt is not awaiting history repair")
    receipt["deleted"] = True
    receipt["refreshedHistoryPages"] = _refresh_history_pages(root, cfg, reports)
    receipt["status"] = "complete"
    receipt["completedAt"] = _now()
    _write_json_atomic(receipt_path, receipt)
    record["pruneState"] = "complete"
    document["updatedAt"] = _now()
    _write_json_atomic(state / MANIFEST_NAME, document)
    return receipt


def _print_preview(document):
    print(f"Working: {document['workingRoot']}")
    print(f"Retention manifest: {document['retentionManifest']}")
    print(
        f"Policy: keep {document['policy']['latestAcceptedPerPipeline']} latest accepted run "
        "per pipeline; require explicit review/undo/audit clearance before pruning."
    )
    print(f"Unregistered runs: {document['unregisteredRunCount']}")
    for run in document["runs"]:
        size = (
            f"{run['files']} files / {run['bytes']:,} bytes"
            if run["files"] is not None and run["bytes"] is not None
            else "size not scanned"
        )
        print(
            f"{run['disposition']:9} {run['runId']} {size} - "
            + "; ".join(run["reasons"])
        )
        for reference in run.get("references", []):
            print(f"  report dependency: {reference}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="exact sandbox Working root")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("preview", help="read-only run inventory and retention decisions")
    subparsers.add_parser("check", help="read-only check for unregistered or unsafe run state")
    register = subparsers.add_parser("register", help="register run receipts as retained pending review")
    selection = register.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="register every supported run")
    selection.add_argument("--run", action="append", default=[], help="one run ID; repeat as needed")
    register.add_argument("--apply", action="store_true", help="write the retention manifest")
    accept = subparsers.add_parser("accept", help="mark a reviewed run as accepted")
    accept.add_argument("run_id")
    accept.add_argument("--reason", required=True)
    accept.add_argument("--review-cleared", action="store_true", required=True)
    accept.add_argument("--audit-cleared", action="store_true", required=True)
    accept.add_argument("--apply", action="store_true", help="write the acceptance record")
    supersede = subparsers.add_parser("supersede", help="approve a run for later pruning")
    supersede.add_argument("run_id")
    supersede.add_argument("--reason", required=True)
    supersede.add_argument("--review-cleared", action="store_true", required=True)
    supersede.add_argument("--undo-cleared", action="store_true", required=True)
    supersede.add_argument("--audit-cleared", action="store_true", required=True)
    supersede.add_argument("--apply", action="store_true", help="write approval and fingerprint the run")
    delete = subparsers.add_parser("delete", help="delete one explicitly approved superseded run")
    delete.add_argument("run_id")
    delete.add_argument("--apply", action="store_true", help="perform the exact deletion")
    repair = subparsers.add_parser(
        "repair-history", help="finish history publication after a completed deletion"
    )
    repair.add_argument("run_id")
    repair.add_argument("--apply", action="store_true", help="refresh history and close its receipt")
    args = parser.parse_args(argv)
    try:
        root = _working_root(args.root)
        cfg = cw.load_cfg()
        _roots(root, cfg)
        if args.command in {"preview", "check"}:
            result = preview(root, cfg)
            _print_preview(result)
            if args.command == "check":
                return int(bool(
                    result["unregisteredRunCount"]
                    or result["blockedRunCount"]
                    or result["blockedReportScanErrors"]
                ))
            return 0
        if not args.apply:
            raise ValueError(f"{args.command} is preview-only unless --apply is supplied")
        if args.command == "register":
            result = register_runs(root, cfg, args.run, args.all)
            print(
                f"registered {len(result['registered'])} run(s), skipped "
                f"{len(result['skipped'])} unsupported director(ies) in {result['manifest']}"
            )
            return 0
        if args.command == "accept":
            accept_run(root, cfg, args.run_id, args.reason)
            print(f"accepted run {args.run_id}")
            return 0
        if args.command == "supersede":
            fingerprint = approve_prune(
                root, cfg, args.run_id, args.reason,
                review_cleared=args.review_cleared,
                undo_cleared=args.undo_cleared,
                audit_cleared=args.audit_cleared,
            )
            print(
                f"approved {args.run_id}: {fingerprint['files']} files, "
                f"{fingerprint['bytes']:,} bytes; deletion still requires `delete --apply`"
            )
            return 0
        if args.command == "repair-history":
            receipt = repair_history(root, cfg, args.run_id)
            print(f"refreshed history for {args.run_id}; receipt: {receipt['receiptPath']}")
            return 0
        receipt = delete_run(root, cfg, args.run_id)
        print(f"pruned {args.run_id}; receipt: {receipt['receiptPath']}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
