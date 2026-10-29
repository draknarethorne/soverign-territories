"""Explicit, standalone identity renames with content-checked recovery."""
import base64
import copy
import datetime
import hashlib
import json
import pathlib
import stat
import uuid

from . import identity_names, metadata


ACTION = "person-renamed"
CATEGORIES = ("Models", "Prospects", "Potentials")
CAST_CATEGORIES = ("Angels", "Sisters")


def valid_name(name):
    stem = name.split(".", 1)[0].upper()
    reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    reserved.update(f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(10))
    return (
        bool(name) and name == name.strip() and len(name) <= 100
        and name not in (".", "..") and not name.endswith((".", " "))
        and stem not in reserved and name.casefold() != "various"
        and not any(char in '<>:"/\\|?*' or ord(char) < 32 for char in name)
    )


def tree_hash(folder):
    """Include empty directories and reject links/junctions anywhere in the tree."""
    folder = pathlib.Path(folder)
    entries = []
    for path in [folder, *sorted(folder.rglob("*"))]:
        info = path.lstat()
        if path.is_symlink() or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError(f"rename cannot traverse a link or junction: {path}")
        if not path.is_dir() and not path.is_file():
            raise ValueError(f"unsupported entry in identity folder: {path}")
        if path != folder and any(not valid_name(part) for part in path.relative_to(folder).parts):
            raise ValueError(f"identity contains an unsafe Windows entry: {path}")
        entries.append([
            path.relative_to(folder).as_posix(),
            None if path.is_dir() else metadata.content_sha256(path),
        ])
    return hashlib.sha256(json.dumps(entries, separators=(",", ":")).encode()).hexdigest()


def _folder(root, relative):
    parts = pathlib.PurePosixPath(relative).parts
    if len(parts) != 2 or parts[0] not in (*CATEGORIES, *CAST_CATEGORIES) or not valid_name(parts[1]):
        raise ValueError("rename requires a safe registered identity folder")
    path = pathlib.Path(root).resolve().joinpath(*parts)
    if path.resolve() != path:
        raise ValueError("rename folder resolves through a link or junction")
    return path


def _unreferenced(folder, cfg):
    if folder.parent.name in CAST_CATEGORIES:
        return
    selected = list(cfg.get("photos", {}).values())
    for flow in cfg.get("flows", {}).values():
        selected.extend(flow.get("photos", {}).values())
    selected_ids = {metadata.photo_id_from_name(name) for name in selected if isinstance(name, str)}
    selected_ids.discard(None)
    if any(metadata.photo_id_from_name(path.name) in selected_ids for path in folder.rglob("*") if path.is_file()):
        raise ValueError("rename refused: identity contains a workflow-selected photo")
    key = folder.parent.name + "/" + folder.name
    if any(
        isinstance(value, str) and value.casefold() == key.casefold()
        for pair in cfg.get("likeness", {}).get("different", []) for value in pair
    ):
        raise ValueError("rename refused: identity has a folder-based workspace exclusion; migrate it first")


def decision(root, folder, person_id, person, cfg):
    """Snapshot export state once per identity while generating the report."""
    import people

    if not person_id or not person or person.get("mergedInto") or folder.split("/")[0] not in (*CATEGORIES, *CAST_CATEGORIES):
        return None, ""
    try:
        path = _folder(root, folder)
        _unreferenced(path, cfg)
        digest = tree_hash(path)
    except (OSError, ValueError) as exc:
        return None, str(exc)
    return {
        "type": ACTION, "personId": person_id, "personFolder": folder,
        "expectedDisplayName": person["displayName"], "expectedTreeSha256": digest,
        "expectedRecordedName": (identity_names.snapshot(person, path) or {}).get("currentName") or person["displayName"],
        "expectedProtected": bool(person.get("protected", False)),
    }, ""


def _check_name_available(root, catalog, name, excluded_ids):
    import people

    excluded = {_folder(root, catalog["people"][pid]["folder"]) for pid in excluded_ids}
    for other_id, other in catalog["people"].items():
        if other_id not in excluded_ids and (
            other["displayName"].casefold() == name.casefold()
            or (other.get("names") or {}).get("currentName", "").casefold() == name.casefold()
            or other["folder"].split("/")[-1].casefold() == name.casefold()
        ):
            raise ValueError("rename collides with an existing catalogue identity; confirm a standalone name swap in Review")
    for category in (*CAST_CATEGORIES, *CATEGORIES):
        parent = pathlib.Path(root) / category
        if parent.is_dir() and any(
            path not in excluded and (
                path.name.casefold() == name.casefold()
                or (path.is_dir() and (people.name_of(path) or "").casefold() == name.casefold())
            )
            for path in parent.iterdir()
        ):
            raise ValueError("rename collides with an existing library entry")


def validate(document, root, catalog, cfg, *, _participants=()):
    import people

    rows = [row for row in document["actions"] if row["type"] == ACTION]
    if not rows:
        return [], []
    if len(document["actions"]) != 1:
        return ["rename or name swap must be applied alone; stage other actions separately"], []
    action = rows[0]
    if "swapWith" in action:
        return _validate_swap(document, root, catalog, cfg)
    try:
        person = catalog["people"].get(action["personId"])
        if (
            not person or person.get("mergedInto") or person["folder"] != action["personFolder"]
            or person["displayName"] != action["expectedDisplayName"]
            or sum(p["folder"].casefold() == action["personFolder"].casefold()
                   for p in catalog["people"].values()) != 1
        ):
            raise ValueError("rename identity ownership or recorded name is stale")
        source = _folder(root, action["personFolder"])
        if not source.is_dir() or not (source / "gallery").is_dir():
            raise ValueError("rename requires an existing identity and Gallery directory")
        name = action["newName"]
        cast = source.parent.name in CAST_CATEGORIES
        recorded_name = (identity_names.snapshot(person, source) or {}).get("currentName") or person["displayName"]
        if recorded_name != action["expectedRecordedName"]:
            raise ValueError("recorded person name is stale; regenerate the gallery")
        if not valid_name(name) or name.casefold() == (
            recorded_name if cast else source.name
        ).casefold():
            raise ValueError("use a new Windows-safe identity name; case-only renames are not supported")
        _check_name_available(root, catalog, name, _participants or (action["personId"],))
        destination = source if cast else _folder(root, f"{source.parent.name}/{name}")
        _unreferenced(source, cfg)
        if tree_hash(source) != action["expectedTreeSha256"]:
            raise ValueError("identity files changed since the gallery was generated; regenerate before renaming")
        histories = [
            path for parent in (source / "gallery", source)
            for path in parent.iterdir() if path.is_file() and people.Z_FILE.match(path.name)
        ]
        if len(histories) > 1:
            raise ValueError("identity has multiple name/history records; resolve before renaming")
        old = histories[0] if histories else None
        old_bytes = old.read_bytes() if old else b""
        lines = old_bytes.decode("utf-8").splitlines(keepends=True)
        # Preserve every original history byte after the name line.
        history = "".join(lines[1:] if lines and lines[0].lower().startswith("name:") else lines)
        if history and not history.endswith("\n"):
            history += "\n"
        new_bytes = (
            f"name: {name}\n" + history
            + f"{datetime.date.today().isoformat()} "
            + (f"name swap with {_participants[1 - _participants.index(action['personId'])]}: "
               if _participants else "")
            + f"renamed from {recorded_name} ({person['folder']})\n"
        ).encode("utf-8")
        new_path = f"gallery/z_{people.slug(name)}.txt"
        new_file = source / pathlib.Path(new_path)
        if new_file.exists() and new_file != old:
            raise ValueError("new name/history file already exists")
        state = {
            "beforeTreeSha256": action["expectedTreeSha256"],
            "afterTreeSha256": "0" * 64,
            "oldHistoryPath": old.relative_to(source).as_posix() if old else None,
            "oldHistoryBase64": base64.b64encode(old_bytes).decode("ascii"),
            "newHistoryPath": new_path,
            "newHistoryBase64": base64.b64encode(new_bytes).decode("ascii"),
        }
        return [], [{
            "type": ACTION, "action": action, "personId": action["personId"],
            "source": source, "destination": destination, "rename": state,
            "names": identity_names.renamed(person, name, source),
        }]
    except (OSError, ValueError) as exc:
        return [f"rename: {exc}"], []


def catalog_action(catalog, plan, batch):
    person = catalog["people"][plan["personId"]]
    before = copy.deepcopy(person)
    person["names"] = copy.deepcopy(plan["names"])
    if plan["source"] != plan["destination"]:
        person["folderHistory"].append(person["folder"])
        person["folder"] = plan["destination"].parent.name + "/" + plan["destination"].name
        person["displayName"] = plan["action"]["newName"]
    record = {
        "id": "action_" + uuid.uuid4().hex, "batchId": batch,
        "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "actor": "user", "type": ACTION, "photoIds": [], "personId": plan["personId"],
        "source": before["folder"], "destination": person["folder"],
        "reason": "explicit identity rename staged in the Review gallery",
        "beforeState": {"person": before, "photo": None},
        "afterState": {"person": copy.deepcopy(person), "photo": None},
        "renameState": copy.deepcopy(plan["rename"]),
    }
    catalog["actions"].append(record)
    if plan.get("partner"):
        partner = catalog_action(catalog, plan["partner"], batch)
        catalog["actions"].pop()
        record["swapPartner"] = partner
        record["reason"] = "explicit confirmed two-person name swap; both identities preserved"
    return record


def _history_path(folder, relative):
    parts = pathlib.PurePosixPath(relative).parts
    if (
        len(parts) not in (1, 2) or (len(parts) == 2 and parts[0] != "gallery")
        or not parts[-1].startswith("z_") or not parts[-1].endswith(".txt")
        or any(part in (".", "..") or "\\" in part or ":" in part for part in parts)
    ):
        raise ValueError("unsafe rename history path")
    return folder.joinpath(*parts)


def _write_history(folder, state, reverse):
    remove = state["newHistoryPath"] if reverse else state["oldHistoryPath"]
    write = state["oldHistoryPath"] if reverse else state["newHistoryPath"]
    content = state["oldHistoryBase64"] if reverse else state["newHistoryBase64"]
    if write:
        _history_path(folder, write).write_bytes(base64.b64decode(content, validate=True))
    if remove and remove != write:
        _history_path(folder, remove).unlink(missing_ok=True)


def change_files(plan, *, reverse=False):
    """Rename and change history, restoring the source if any step fails."""
    if plan.get("partner"):
        return _change_swap(plan, reverse=reverse)
    source, destination = plan["source"], plan["destination"]
    state = plan["rename"]
    if reverse:
        source, destination = destination, source
    expected = state["afterTreeSha256"] if reverse else state["beforeTreeSha256"]
    moving = source != destination
    if (moving and destination.exists()) or tree_hash(source) != expected:
        raise ValueError("rename folder changed or destination appeared; no rename applied")
    if moving:
        source.rename(destination)
    try:
        _write_history(destination, state, reverse)
        digest = tree_hash(destination)
        if reverse and digest != state["beforeTreeSha256"]:
            raise ValueError("renamed identity did not restore its original inventory")
        if not reverse:
            state["afterTreeSha256"] = digest
    except (OSError, ValueError) as exc:
        try:
            _write_history(destination, state, not reverse)
            if moving:
                destination.rename(source)
        except (OSError, ValueError) as rollback:
            raise OSError(f"rename failed ({exc}); rollback failed ({rollback})") from exc
        raise


def undo_plan(catalog, action, root, cfg, *, _participants=()):
    if action.get("swapPartner"):
        partner = action["swapPartner"]
        ids = (action["personId"], partner["personId"])
        if ids[0] == ids[1] or action.get("batchId") != partner.get("batchId"):
            raise ValueError("swap history has ambiguous identity or batch ownership")
        first = undo_plan(catalog, {k: v for k, v in action.items() if k != "swapPartner"},
                          root, cfg, _participants=ids)
        first["partner"] = undo_plan(catalog, partner, root, cfg, _participants=ids)
        if swap_staging(first).exists():
            raise ValueError("swap recovery staging already exists; inspect recovery before undo")
        return first
    person = catalog["people"].get(action["personId"])
    if person != action["afterState"]["person"]:
        raise ValueError("renamed identity catalogue state changed; cannot undo")
    source = _folder(root, action["source"])
    destination = _folder(root, action["destination"])
    occupied_by_partner = any(
        _folder(root, catalog["people"][pid]["folder"]) == source
        for pid in _participants if pid != action["personId"]
    )
    if (source != destination and source.exists() and not occupied_by_partner) or not destination.is_dir():
        raise ValueError("rename undo destination is occupied or renamed folder is missing")
    if any(
        other_id != action["personId"] and other_id not in _participants and (
            other["folder"].casefold() == action["source"].casefold()
            or other["displayName"].casefold() == action["beforeState"]["person"]["displayName"].casefold()
        )
        for other_id, other in catalog["people"].items()
    ):
        raise ValueError("rename undo collides with another catalogue identity")
    _unreferenced(destination, cfg)
    if _participants:
        import people

        old_bytes = base64.b64decode(action["renameState"]["oldHistoryBase64"], validate=True)
        lines = [line.rstrip() for line in old_bytes.decode("utf-8").splitlines() if line.strip()]
        old_path = action["renameState"]["oldHistoryPath"]
        name = action["beforeState"]["person"]["displayName"]
        if old_path:
            name = people.unslug(people.Z_FILE.match(pathlib.PurePosixPath(old_path).name)[1])
        if lines and lines[0].lower().startswith("name:"):
            name = lines[0][5:].strip() or name
        _check_name_available(root, catalog, name, _participants)
    if tree_hash(destination) != action["renameState"]["afterTreeSha256"]:
        raise ValueError("renamed identity files changed; cannot undo")
    return {
        "type": ACTION, "personId": action["personId"], "source": source, "destination": destination,
        "rename": action["renameState"],
    }


def restore_catalog(catalog, record):
    catalog["people"][record["personId"]] = copy.deepcopy(record["beforeState"]["person"])
    if record.get("swapPartner"):
        restore_catalog(catalog, record["swapPartner"])


def _validate_swap(document, root, catalog, cfg):
    action = document["actions"][0]
    try:
        if action.get("swapConfirmed") is not True:
            raise ValueError("both identities and effects must be explicitly confirmed")
        partner = action["swapWith"]
        ids = (action["personId"], partner["personId"])
        if ids[0] == ids[1]:
            raise ValueError("swap requires two distinct identities")
        for row in (action, partner):
            person = catalog["people"].get(row["personId"], {})
            if ("expectedProtected" not in row
                    or bool(person.get("protected", False)) != row["expectedProtected"]):
                raise ValueError("identity protection changed; refresh and confirm both identities")
        clean = {k: v for k, v in action.items() if k not in ("swapWith", "swapConfirmed")}
        if action["newName"] != partner["expectedRecordedName"]:
            raise ValueError("swap target name is stale")
        second = {**partner, "type": ACTION, "newName": action["expectedRecordedName"]}
        plans = []
        for row in (clean, second):
            errors, result = validate({**document, "actions": [row]}, root, catalog, cfg,
                                      _participants=ids)
            if errors:
                raise ValueError("; ".join(errors))
            plans.extend(result)
        destinations = [plan["destination"] for plan in plans]
        if len({str(path).casefold() for path in destinations}) != 2:
            raise ValueError("swap would collide with a fixed cast slot")
        sources = {plan["source"] for plan in plans}
        for plan in plans:
            if plan["destination"].exists() and plan["destination"] not in sources:
                raise ValueError("swap destination is occupied by a third party")
        plans[0]["partner"] = plans[1]
        if swap_staging(plans[0]).exists():
            raise ValueError("swap recovery staging already exists; inspect recovery before applying")
        return [], [plans[0]]
    except (KeyError, OSError, ValueError) as exc:
        return [f"name swap: {exc}"], []


def swap_staging(plan):
    members = (plan, plan["partner"])
    payload = [
        [str(member["source"]), str(member["destination"]), member["rename"]["beforeTreeSha256"]]
        for member in members
    ]
    token = hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()[:24]
    return plan["source"].parent.parent / (".name-swap-" + token)


def _change_swap(plan, *, reverse=False):
    """Evacuate both trees privately before crossing same-category paths."""
    members = (plan, plan["partner"])
    stage = swap_staging(plan)
    moves = []
    for member in members:
        source = member["destination"] if reverse else member["source"]
        destination = member["source"] if reverse else member["destination"]
        expected = member["rename"]["afterTreeSha256" if reverse else "beforeTreeSha256"]
        if tree_hash(source) != expected:
            raise ValueError("swap identity files changed; no swap applied")
        moves.append((source, destination, stage / str(len(moves)), member["rename"]))
    sources = {item[0] for item in moves}
    if any(destination.exists() and destination not in sources for _, destination, _, _ in moves):
        raise ValueError("swap destination appeared; no swap applied")
    stage.mkdir()
    evacuated, installed, histories = [], [], []
    try:
        for source, destination, private, state in moves:
            source.rename(private)
            evacuated.append((source, destination, private, state))
        for source, destination, private, state in moves:
            histories.append((private, state))
            _write_history(private, state, reverse)
            digest = tree_hash(private)
            if reverse and digest != state["beforeTreeSha256"]:
                raise ValueError("swap did not restore original inventory")
            if not reverse:
                state["afterTreeSha256"] = digest
        for source, destination, private, state in moves:
            private.rename(destination)
            installed.append((destination, private))
    except (OSError, ValueError) as exc:
        try:
            for destination, private in reversed(installed):
                destination.rename(private)
            for private, state in reversed(histories):
                _write_history(private, state, not reverse)
            for source, _, private, _ in reversed(evacuated):
                private.rename(source)
            for source, _, _, state in evacuated:
                expected = state["afterTreeSha256" if reverse else "beforeTreeSha256"]
                if tree_hash(source) != expected:
                    raise OSError(f"swap rollback inventory changed: {source}")
            stage.rmdir()
        except (OSError, ValueError) as rollback:
            raise OSError(f"swap failed ({exc}); rollback failed ({rollback}); recovery staging: {stage}") from exc
        raise
    stage.rmdir()
