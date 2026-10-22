"""Explicit, standalone identity renames with content-checked recovery."""
import base64
import copy
import datetime
import hashlib
import json
import pathlib
import stat
import uuid

from . import metadata


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
        "expectedRecordedName": people.name_of(path) or person["displayName"],
    }, ""


def validate(document, root, catalog, cfg):
    import people

    rows = [row for row in document["actions"] if row["type"] == ACTION]
    if not rows:
        return [], []
    if len(document["actions"]) != 1:
        return ["rename must be applied alone; stage swaps and other actions separately"], []
    action = rows[0]
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
        recorded_name = people.name_of(source) or person["displayName"]
        if recorded_name != action["expectedRecordedName"]:
            raise ValueError("recorded person name is stale; regenerate the gallery")
        if not valid_name(name) or name.casefold() == (
            recorded_name if cast else source.name
        ).casefold():
            raise ValueError("use a new Windows-safe identity name; case-only renames are not supported")
        for other_id, other in catalog["people"].items():
            if other_id != action["personId"] and (
                other["displayName"].casefold() == name.casefold()
                or other["folder"].split("/")[-1].casefold() == name.casefold()
            ):
                raise ValueError("rename collides with an existing catalogue identity; swaps are not supported")
        for category in (*CAST_CATEGORIES, *CATEGORIES):
            parent = pathlib.Path(root) / category
            if parent.is_dir() and any(
                p != source and (
                    p.name.casefold() == name.casefold()
                    or (p.is_dir() and (people.name_of(p) or "").casefold() == name.casefold())
                )
                for p in parent.iterdir()
            ):
                raise ValueError("rename collides with an existing library entry")
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
            + f"{datetime.date.today().isoformat()} renamed from {recorded_name} ({person['folder']})\n"
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
        }]
    except (OSError, ValueError) as exc:
        return [f"rename: {exc}"], []


def catalog_action(catalog, plan, batch):
    person = catalog["people"][plan["personId"]]
    before = copy.deepcopy(person)
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


def undo_plan(catalog, action, root, cfg):
    person = catalog["people"].get(action["personId"])
    if person != action["afterState"]["person"]:
        raise ValueError("renamed identity catalogue state changed; cannot undo")
    source = _folder(root, action["source"])
    destination = _folder(root, action["destination"])
    if (source != destination and source.exists()) or not destination.is_dir():
        raise ValueError("rename undo destination is occupied or renamed folder is missing")
    if any(
        other_id != action["personId"] and (
            other["folder"].casefold() == action["source"].casefold()
            or other["displayName"].casefold() == action["beforeState"]["person"]["displayName"].casefold()
        )
        for other_id, other in catalog["people"].items()
    ):
        raise ValueError("rename undo collides with another catalogue identity")
    _unreferenced(destination, cfg)
    if tree_hash(destination) != action["renameState"]["afterTreeSha256"]:
        raise ValueError("renamed identity files changed; cannot undo")
    return {
        "type": ACTION, "source": source, "destination": destination,
        "rename": action["renameState"],
    }
