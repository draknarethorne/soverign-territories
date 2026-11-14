"""Run-bound Sandbox quality disposition through the existing guarded action transaction."""

import datetime
import hashlib
import json
import pathlib

from . import actions, clean_rebase, metadata, sandbox


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _backup_callback(root, run, sources, *, reverse=False):
    paths = sorted({root / ".likeness-library.json", *sources})

    def backup(_root, _cfg, batch):
        return actions.library_backup.create_backup(
            root, stamp=f"quality-actions-{batch}", apply=True,
            scoped_sources=[(f"transaction-{index}", path) for index, path in enumerate(paths)],
            recovery={"kind": "directed-quality-actions", "run": str(run),
                      "runSHA256": metadata.content_sha256(run / "run.json"),
                      "batchId": batch, "reverse": reverse},
        )
    return backup


def _unusable(evidence):
    if not isinstance(evidence, dict) or evidence.get("faces") != 1:
        return False
    if evidence.get("classification") == "measured-face-too-small":
        pixels, minimum = evidence.get("facePixels"), evidence.get("minimumFacePixels")
        return (isinstance(pixels, (int, float)) and isinstance(minimum, (int, float))
                and 0 < pixels < minimum)
    return (evidence.get("classification") == "measured-head-obstruction"
            and "bars cover her head" in str(evidence.get("reason", "")))


def _conservation(root, plan, moves, *, applied):
    moved = {item["photoId"]: item for item in moves}
    expected_active, tuples = {}, []
    for row in plan["photos"]:
        pid = row.get("photoId")
        if not pid or pid in expected_active:
            raise ValueError("disposition requires unique stable run photo IDs")
        move = moved.get(pid) if applied else None
        relative = move["destination"] if move else row["destination"]
        expected = row.get("preparedSHA256", row["sha256"])
        path = clean_rebase._publication_path(root, relative)
        if metadata.content_sha256(path) != expected:
            raise ValueError(f"disposition content changed: {relative}")
        if move and clean_rebase._publication_path(root, move["source"]).exists():
            raise ValueError("quarantined photo also exists at active source")
        expected_active[pid] = [] if move else [path]
        tuples.append([pid, row["sha256"], expected])
    actual = actions._index_photos(root)
    if {pid: paths for pid, paths in expected_active.items() if paths} != actual:
        raise ValueError("active plus quarantine inventory differs from the bound run")
    return {"total": len(tuples), "active": len(tuples) - (len(moved) if applied else 0),
            "quarantined": len(moved) if applied else 0, "tupleSHA256": _digest(sorted(tuples))}


def _verify(root, run, plan, receipt, cfg):
    required = {"version", "root", "runSHA256", "status", "installedCatalogSHA256",
                "currentCatalogSHA256", "batchId", "actionRecordsSHA256", "backup",
                "backupManifestSHA256", "moves", "conservation"}
    if (not isinstance(receipt, dict) or not required <= receipt.keys()
            or receipt.get("version") != 1 or receipt.get("root") != str(root)
            or receipt.get("runSHA256") != metadata.content_sha256(run / "run.json")
            or receipt.get("installedCatalogSHA256") != plan.get("installedCatalogSHA256")
            or receipt.get("status") not in ("applied", "undone")):
        raise ValueError("incomplete or changed disposition binding; inspect action history/recovery")
    catalog = metadata.load_catalog(root / ".likeness-library.json")
    if metadata.content_sha256(root / ".likeness-library.json") != receipt["currentCatalogSHA256"]:
        raise ValueError("catalogue changed since disposition; inspect newer actions")
    records = [item for item in catalog["actions"] if item.get("batchId") == receipt["batchId"]]
    if _digest(records) != receipt["actionRecordsSHA256"]:
        raise ValueError("disposition action history changed")
    if receipt["status"] == "applied":
        errors, batch, reverse_plans = actions.plan_undo(
            catalog, root, receipt["batchId"], actions.selected_photo_ids(cfg), cfg,
        )
        if errors or batch != receipt["batchId"]:
            raise ValueError("disposition no longer independently reversible: " + "; ".join(errors))
        actions._undo_retained(root, batch, reverse_plans, cfg)
    backup = pathlib.Path(receipt["backup"])
    actions.library_backup.verify_backup(backup)
    if metadata.content_sha256(backup / "manifest.json") != receipt["backupManifestSHA256"]:
        raise ValueError("disposition recovery manifest changed")
    recovery = json.loads((backup / "manifest.json").read_bytes()).get("recovery") or {}
    if (recovery.get("runSHA256") != receipt["runSHA256"]
            or recovery.get("batchId") != receipt["batchId"] or recovery.get("reverse")):
        raise ValueError("disposition backup belongs to a different transaction")
    if receipt["status"] == "undone":
        if not {"undoBatchId", "undoBackup", "undoBackupManifestSHA256", "undoActionRecordsSHA256"} <= receipt.keys():
            raise ValueError("incomplete undo disposition binding")
        undo_records = [item for item in catalog["actions"] if item.get("batchId") == receipt["undoBatchId"]]
        if _digest(undo_records) != receipt["undoActionRecordsSHA256"]:
            raise ValueError("undo action history changed")
        undo_backup = pathlib.Path(receipt["undoBackup"])
        actions.library_backup.verify_backup(undo_backup)
        if metadata.content_sha256(undo_backup / "manifest.json") != receipt["undoBackupManifestSHA256"]:
            raise ValueError("undo recovery manifest changed")
    for move in receipt["moves"]:
        matching = [item for item in records if item["id"] == move["actionId"]]
        if len(matching) != 1 or any(matching[0].get(key) != move[key]
                                    for key in ("source", "destination", "contentSha256")):
            raise ValueError("disposition move differs from recorded action")
        if matching[0]["photoIds"] != [move["photoId"]] or matching[0]["type"] != "photo-junked":
            raise ValueError("disposition action population differs")
        if receipt["status"] == "undone" and clean_rebase._publication_path(root, move["destination"]).exists():
            raise ValueError("undone quarantine destination still exists")
    actual = _conservation(root, plan, receipt["moves"], applied=receipt["status"] == "applied")
    if actual != receipt["conservation"]:
        raise ValueError("disposition conservation receipt differs")
    return catalog


def execute(run, cfg, *, apply=False, check=False, undo=False, backup_fn=None):
    if check and (undo or apply):
        raise ValueError("check cannot be combined with apply or undo")
    run = pathlib.Path(run).resolve()
    raw = (run / "run.json").read_bytes()
    run_hash = hashlib.sha256(raw).hexdigest()
    plan = json.loads(raw)
    root = pathlib.Path(plan["workingRoot"]).resolve()
    if not sandbox.is_sandbox_working_path(root) or not run.is_relative_to(root):
        raise ValueError("quality disposition is Sandbox Working-local only")
    if plan.get("status") != "applied" or not plan.get("groupLifecycle", {}).get("assignmentSummary"):
        raise ValueError("quality disposition requires an applied directed intake run")
    path = run / "quality-disposition.json"
    pool = actions.likeness.pool_home(actions.likeness.settings(cfg))
    if path.exists():
        receipt = json.loads(path.read_bytes())
        catalog = _verify(root, run, plan, receipt, cfg)
        if undo and receipt["status"] == "applied":
            if not apply:
                print(f"Preview undo quality batch {receipt['batchId']}; no writes")
                return receipt
            errors, _, reverse_plans = actions.plan_undo(
                catalog, root, receipt["batchId"], actions.selected_photo_ids(cfg), cfg,
            )
            transfers, _ = actions._undo_retained(root, receipt["batchId"], reverse_plans, cfg)
            sources = [item["source"] for item in reverse_plans if item.get("source")]
            sources += [clean_rebase._publication_path(root, item["destination"])
                        for transfer in transfers for item in transfer["files"]]
            batch, backup, _ = actions.undo_actions(
                catalog, root, cfg, pool, batch_id=receipt["batchId"],
                backup_fn=backup_fn or _backup_callback(root, run, sources, reverse=True),
                save_fn=lambda data: metadata.save_catalog(data, root / ".likeness-library.json"),
            )
            receipt.update(status="undone", undoBatchId=batch, undoBackup=str(backup),
                           undoBackupManifestSHA256=metadata.content_sha256(pathlib.Path(backup) / "manifest.json"),
                           currentCatalogSHA256=metadata.content_sha256(root / ".likeness-library.json"),
                           conservation=_conservation(root, plan, receipt["moves"], applied=False))
            receipt["undoActionRecordsSHA256"] = _digest([
                item for item in metadata.load_catalog(root / ".likeness-library.json")["actions"]
                if item.get("batchId") == batch
            ])
            receipt["actionRecordsSHA256"] = _digest([
                item for item in metadata.load_catalog(root / ".likeness-library.json")["actions"]
                if item.get("batchId") == receipt["batchId"]
            ])
            clean_rebase._write_json(path, receipt)
            _verify(root, run, plan, receipt, cfg)
        print(f"Verified quality disposition: {receipt['status']}; {receipt['conservation']}")
        return receipt
    if check or undo:
        raise ValueError("no applied quality disposition receipt")
    catalog_path = root / ".likeness-library.json"
    catalog_hash = metadata.content_sha256(catalog_path)
    if catalog_hash != plan.get("installedCatalogSHA256"):
        raise ValueError("installed catalogue differs from the applied run")
    catalog = metadata.load_catalog(catalog_path)
    clean_rebase._check_publication(root, plan)
    baseline = _conservation(root, plan, [], applied=False)
    selected, held = [], []
    for row in plan["photos"]:
        if not row["destination"].startswith("Various/"):
            continue
        evidence = row.get("qualityEvidence") or {}
        if not _unusable(evidence):
            held.append({"photoId": row["photoId"], "reason": evidence.get("reason")
                         or "no unequivocal measured unusable evidence"})
            continue
        relative = pathlib.PurePosixPath(row["destination"])
        selected.append({
            "type": "photo-junked", "photoId": row["photoId"],
            "contentSha256": row.get("preparedSHA256", row["sha256"]),
            "sourceBucket": relative.parent.name.title(),
            "personFolder": relative.parent.parent.as_posix(),
        })
    document = {"manifestVersion": 1, "source": "people-gallery-review",
                "generatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(), "actions": selected}
    if not selected:
        raise ValueError(f"no unequivocal measured unusable candidates; {len(held)} held")
    errors, proposed = actions.validate_manifest(
        document, root, catalog, pool, actions.selected_photo_ids(cfg), cfg,
    )
    if errors:
        raise ValueError("quality action refused: " + "; ".join(errors))
    actions.print_preview(proposed)
    if not apply:
        print(f"Preview only: {len(selected)} measured unusable; {len(held)} explicit holds; {baseline}")
        return document
    receipt = {"version": 1, "status": "prepared", "root": str(root),
               "runSHA256": run_hash,
               "installedCatalogSHA256": catalog_hash, "held": held, "manifest": document}
    clean_rebase._write_json(path, receipt)
    transfers = actions._retained_plans(root, proposed)
    sources = [item["source"] for item in proposed]
    sources += [clean_rebase._publication_path(root, item["source"])
                for transfer in transfers for item in transfer["files"]]
    if metadata.content_sha256(run / "run.json") != run_hash:
        raise ValueError("applied run changed during disposition preview; no actions applied")
    try:
        batch, backup = actions.apply_actions(
            document, root, catalog, cfg, pool,
            backup_fn=backup_fn or _backup_callback(root, run, sources),
            save_fn=lambda data: metadata.save_catalog(data, catalog_path),
        )
    except (OSError, ValueError):
        # A prepared receipt is deliberately retained: never repeat an uncertain transaction.
        raise
    updated = metadata.load_catalog(catalog_path)
    records = [item for item in updated["actions"] if item.get("batchId") == batch]
    moves = [{"photoId": item["photoIds"][0], "actionId": item["id"],
              **{key: item[key] for key in ("source", "destination", "contentSha256")}}
             for item in records]
    receipt.update(status="applied", batchId=batch, backup=str(backup), moves=moves,
                   backupManifestSHA256=metadata.content_sha256(pathlib.Path(backup) / "manifest.json"),
                   actionRecordsSHA256=_digest(records),
                   currentCatalogSHA256=metadata.content_sha256(catalog_path),
                   conservation=_conservation(root, plan, moves, applied=True))
    clean_rebase._write_json(path, receipt)
    _verify(root, run, plan, receipt, cfg)
    print(f"Applied quality disposition: {batch}; {receipt['conservation']}")
    return receipt
