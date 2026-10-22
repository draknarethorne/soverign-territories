"""Stable-ID person protection decisions, separate from photo decisions."""
import copy
import datetime
import pathlib
import uuid


PROTECTION_ACTIONS = {"person-protected", "person-unprotected"}


def validate_actions(document, root, catalog):
    """Validate current ownership and state; never infer a person from a photo."""
    errors, plans, occupied = [], [], {}
    photo_folders = {
        action[key].casefold()
        for action in document["actions"] if action["type"] not in PROTECTION_ACTIONS
        for key in ("personFolder", "destinationFolder") if key in action
    }
    root = pathlib.Path(root).resolve()
    for index, action in enumerate(document["actions"]):
        if action["type"] not in PROTECTION_ACTIONS:
            continue
        label = f"actions/{index}"
        folder = pathlib.PurePosixPath(action["personFolder"])
        person_id = action["personId"]
        person = catalog["people"].get(person_id)
        if len(folder.parts) != 2 or folder.parts[0] not in ("Models", "Prospects") or any(
            part in (".", "..") for part in folder.parts
        ):
            errors.append(f"{label}: person protection requires a Model or Prospect folder")
            continue
        target = root.joinpath(*folder.parts)
        owners = [
            key for key, record in catalog["people"].items()
            if record["folder"].casefold() == action["personFolder"].casefold()
        ]
        if (
            not person or owners != [person_id] or person.get("mergedInto")
            or person["folder"] != action["personFolder"]
            or not target.is_dir() or target.resolve() != target
        ):
            errors.append(f"{label}: personId must own an existing, active, unambiguous folder")
            continue
        if bool(person.get("protected", False)) != action["expectedProtected"]:
            errors.append(f"{label}: person protection state is stale")
            continue
        enabled = action["type"] == "person-protected"
        if enabled == action["expectedProtected"]:
            errors.append(f"{label}: person protection already has the requested state")
        if person_id in occupied:
            errors.append(f"{label}: conflicts with actions/{occupied[person_id]} for this identity")
        occupied[person_id] = index
        if action["personFolder"].casefold() in photo_folders:
            errors.append(f"{label}: stage person protection separately from this identity's photo actions")
        plans.append({
            "type": action["type"], "personId": person_id, "action": action,
            "source": target, "destination": None,
        })
    return errors, plans


def apply_action(catalog, plan, batch_id):
    person_id = plan["personId"]
    person = catalog["people"][person_id]
    before = {"person": copy.deepcopy(person), "photo": None}
    person["protected"] = plan["type"] == "person-protected"
    catalog["actions"].append({
        "id": "action_" + uuid.uuid4().hex, "batchId": batch_id,
        "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "actor": "user", "type": plan["type"], "photoIds": [], "personId": person_id,
        "reason": "identity protection staged in the local likeness review gallery",
        "beforeState": before, "afterState": {"person": copy.deepcopy(person), "photo": None},
    })


def restore_action(catalog, action, root):
    """Restore only when the identity still exactly matches its recorded state."""
    person_id = action["personId"]
    person = catalog["people"].get(person_id)
    if person != action["afterState"]["person"]:
        raise ValueError(f"person state changed after action {action['id']}")
    relative = pathlib.PurePosixPath(person["folder"])
    if len(relative.parts) != 2 or relative.parts[0] not in ("Models", "Prospects") or any(
        part in (".", "..") for part in relative.parts
    ):
        raise ValueError(f"unsafe person folder after action {action['id']}")
    folder = pathlib.Path(root).resolve().joinpath(*relative.parts)
    if not folder.is_dir() or folder.resolve() != folder:
        raise ValueError(f"person folder changed after action {action['id']}")
    catalog["people"][person_id] = copy.deepcopy(action["beforeState"]["person"])
