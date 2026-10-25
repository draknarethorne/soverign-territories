"""Explicit report-bound quarantine for loose intake; never delete or cross artist scopes."""
import json
import os
import shutil
import uuid

import library_backup
from likeness_library import metadata, sandbox
import comfy_workflows as cw

JOURNAL = "junk-disposition.json"


def read_path(root, relative):
    parts = sandbox._safe_source_path(relative)
    path = root.joinpath(*parts)
    for parent in (path, *path.parents):
        if sandbox._is_reparse_point(parent):
            raise ValueError(f"refusing linked quarantine path: {parent}")
        if parent == root:
            break
    if root.resolve() not in path.resolve().parents:
        raise ValueError(f"quarantine path escapes Working: {path}")
    return path


def digest(path):
    return metadata.content_sha256(path)


def save(path, data):
    stage = path.with_suffix(".json.pending")
    if stage.exists():
        raise ValueError(f"unfinished quarantine journal: {stage}")
    with stage.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")
    os.replace(stage, path)


def protected(root, source, catalog, cfg):
    """Only unregistered loose incoming photos may use automatic quarantine."""
    relative = source.relative_to(root)
    parts = relative.parts
    loose = (parts[:2] == ("Various", "gallery") and len(parts) == 3
             or parts[0] == "Artists" and len(parts) == 4 and parts[2] == "gallery")
    if not loose:
        return "Not loose Various/gallery or Artists/<artist>/gallery intake; use a staged manual action."
    folder = relative.parent.parent.as_posix()
    if any(person["folder"].casefold() == folder.casefold() for person in catalog["people"].values()):
        return "Registered identity folder: use guarded staged manual Junk/retire action."
    photo_id = metadata.photo_id_from_name(source.name)
    if photo_id and (photo_id in catalog["photos"] or any(
            photo_id in p["identityAnchors"] for p in catalog["people"].values())):
        return "Photo has catalogue decisions/identity evidence; use a staged manual action."
    names = list(cfg.get("photos", {}).values())
    for flow in cfg.get("flows", {}).values():
        names.extend(flow.get("photos", {}).values())
    key = cw.photo_key(source.name)
    if key and any(cw.photo_key(name) == key for name in names):
        return "Photo is selected by a workflow; manual reference resolution required."
    return None


def plan(root, report, data, cfg):
    catalog_path = root / ".likeness-library.json"
    if not catalog_path.is_file():
        raise ValueError("automatic sandbox Junk requires a Working-local catalogue")
    catalog = metadata.load_catalog(catalog_path)
    moves, holds = [], []
    for row in data["photos"]:
        if row["outcome"] != "junk-candidate":
            continue
        source = read_path(root, row["source"])
        why = protected(root, source, catalog, cfg)
        if why:
            holds.append({"source": row["source"], "reason": why})
            continue
        target_relative = "_junk/" + row["source"]
        target = read_path(root, target_relative)
        if target.exists():
            raise ValueError(f"Junk destination already exists; refusing overwrite: {target}")
        if not source.is_file() or digest(source) != row["sourceSha256"]:
            raise ValueError(f"Junk source changed/missing: {source}; create a new report")
        moves.append({"source": row["source"], "target": target_relative,
                      "sha256": row["sourceSha256"], "reason": row["eligibility"]["reason"]})
    return {"version": 1, "status": "planned", "root": str(root),
            "reportSha256": digest(report / "manifest.json"), "moves": moves, "holds": holds,
            "catalogueSha256": digest(catalog_path)}


def verified_journal(root, report):
    path = report / JOURNAL
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or not {"version", "root", "reportSha256", "status", "moves", "holds", "snapshot"} <= data.keys()
            or data.get("version") != 1 or data.get("root") != str(root)
            or data.get("reportSha256") != digest(report / "manifest.json")
            or data.get("status") not in ("applied", "undone")
            or not isinstance(data["moves"], list) or not isinstance(data["holds"], list)
            or not isinstance(data["snapshot"], str) or not data["snapshot"].startswith("_backup/")):
        raise ValueError(f"incomplete/unsupported Junk journal: {path}; inspect recovery snapshot")
    manifest = json.loads((report / "manifest.json").read_text(encoding="utf-8"))
    rows = {r["source"]: r for r in manifest["photos"] if r["outcome"] == "junk-candidate"}
    seen = set()
    for move in data["moves"]:
        if (not isinstance(move, dict) or set(move) != {"source", "target", "sha256", "reason"}
                or not all(isinstance(value, str) for value in move.values())):
            raise ValueError("invalid Junk journal move record")
        source = read_path(root, move["source"])
        target = read_path(root, move["target"])
        if (move["source"] in seen or move["source"] not in rows
                or move["target"] != "_junk/" + move["source"]
                or move["sha256"] != rows[move["source"]]["sourceSha256"]):
            raise ValueError("Junk journal does not match eligible report sources")
        seen.add(move["source"])
        present, absent = (target, source) if data["status"] == "applied" else (source, target)
        if absent.exists() or not present.is_file() or digest(present) != move["sha256"]:
            raise ValueError(f"Junk journal inventory changed: {present}")
    snapshot = read_path(root, data["snapshot"])
    library_backup.verify_backup(snapshot)
    backup = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
    retained = {entry["source"]: entry["sha256"] for entry in backup["entries"]}
    if (backup.get("scope") != "transaction"
            or backup.get("recovery") != {"kind": "preparation-junk", "moves": data["moves"]}
            or any(retained.get(str(read_path(root, move["source"]))) != move["sha256"] for move in data["moves"])):
        raise ValueError("Junk recovery backup is not bound to this disposition")
    return data


def move_exact(source, target, expected):
    """Exclusive verified copy/remove works on drives without hard-link support."""
    if not source.is_file() or digest(source) != expected:
        raise ValueError(f"quarantine source changed: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with target.open("xb") as outgoing:
            created = True
            with source.open("rb") as incoming:
                shutil.copyfileobj(incoming, outgoing)
    except FileExistsError:
        raise ValueError(f"refusing to overwrite quarantine destination: {target}") from None
    except OSError:
        if created and target.exists():
            target.unlink()
        raise
    try:
        shutil.copystat(source, target)
        if digest(target) != expected or digest(source) != expected:
            raise ValueError(f"quarantine copy verification failed: {target}; source retained")
        source.unlink()
    except (OSError, ValueError):
        target.unlink()
        raise


def route(root, report, data, cfg, *, apply=False, undo=False):
    journal_path = report / JOURNAL
    existing = verified_journal(root, report)
    if existing:
        if (undo and existing["status"] == "undone") or (not undo and existing["status"] == "applied"):
            print(f"Junk disposition already {existing['status']}; verified without rewriting.")
            return int(bool(existing["holds"]))
        if not undo:
            raise ValueError("Junk disposition was undone; create a new report before another apply")
        transaction = existing
    elif undo:
        raise ValueError("no completed Junk disposition to undo")
    else:
        transaction = plan(root, report, data, cfg)
    moves = transaction["moves"]
    for hold in transaction["holds"]:
        print(f"HELD {hold['source']}: {hold['reason']}")
    for move in moves:
        print(f"{'RESTORE' if undo else 'JUNK'} {move['source']} <-> {move['target']}: {move['reason']}")
    print(f"{len(moves)} {'restore' if undo else 'Junk'} move(s), {len(transaction['holds'])} held; "
          "no deletion, matching, or automatic retry.")
    if not apply or not moves:
        return int(bool(transaction["holds"]))
    if not undo:
        scoped = [(f"photo-{index}", read_path(root, move["source"])) for index, move in enumerate(moves)]
        scoped += [("catalogue", root / ".likeness-library.json"), ("preparation-report", report / "manifest.json")]
        transaction["snapshot"] = str(library_backup.create_backup(
            root, stamp=f"preparation-junk-{uuid.uuid4().hex}", scoped_sources=scoped,
            recovery={"kind": "preparation-junk", "moves": moves}).relative_to(root)).replace("\\", "/")
        if digest(root / ".likeness-library.json") != transaction["catalogueSha256"]:
            raise ValueError("catalogue changed during Junk backup; no files moved")
        if cw.load_cfg() != cfg:
            raise ValueError("workflow configuration changed during Junk backup; no files moved")
    else:
        # Refuse to revive a source into a folder newly claimed by an identity/action.
        catalog = metadata.load_catalog(root / ".likeness-library.json")
        for move in moves:
            why = protected(root, read_path(root, move["source"]), catalog, cfg)
            if why:
                raise ValueError(f"Junk undo blocked: {why}")
    prior = "applied" if undo else "planned"
    transaction["status"] = "undoing" if undo else "applying"
    save(journal_path, transaction)
    completed = []
    try:
        for move in moves:
            source, target = read_path(root, move["source"]), read_path(root, move["target"])
            if undo:
                source, target = target, source
            move_exact(source, target, move["sha256"])
            completed.append((source, target, move["sha256"]))
        transaction["status"] = "undone" if undo else "applied"
        save(journal_path, transaction)
    except (OSError, ValueError):
        for source, target, expected in reversed(completed):
            move_exact(target, source, expected)
        transaction["status"] = prior
        save(journal_path, transaction)
        raise
    verified_journal(root, report)
    return int(bool(transaction["holds"]))
