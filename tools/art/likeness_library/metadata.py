#!/usr/bin/env python3
"""Load and validate the git-tracked likeness decisions catalogue."""
import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile
import uuid
from datetime import datetime

from jsonschema import Draft7Validator

from . import report_assets

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/workflows"))
import comfy_workflows as cw  # noqa: E402

CATALOG_PATH = ROOT / "data/art/likeness-library.json"
SCHEMA_PATH = ROOT / "data/art/_schema/likeness-library.schema.json"
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


def new_person_id():
    """Return an opaque identity key that remains unchanged when a folder is renamed or promoted."""
    return f"person_{uuid.uuid4().hex}"


def photo_id_from_name(name):
    """Return the normalized source ID from an originals-managed filename, independent of its folder prefix."""
    key = cw.photo_key(pathlib.Path(name).name)
    return f"photo:{key}" if key else None


def content_sha256(path):
    """Hash current file bytes for stale-manifest detection; this is not the stable photo ID."""
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validation_errors(data):
    """Return schema and referential-integrity errors without modifying data."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = []
    validator = Draft7Validator(schema)
    for error in sorted(validator.iter_errors(data), key=lambda e: tuple(str(part) for part in e.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{location}: {error.message}")

    if errors or not isinstance(data, dict):
        return errors

    for index, action in enumerate(data["actions"]):
        timestamp = action["timestamp"].replace("Z", "+00:00")
        if not _TIMESTAMP.fullmatch(action["timestamp"]) or not _has_timezone(timestamp):
            errors.append(f"actions/{index}/timestamp: must be an ISO 8601 datetime with a timezone")

    people = data["people"]
    photos = data["photos"]
    folder_owners = {}
    anchor_owners = {}
    for person_id, person in people.items():
        names = person.get("names")
        if names and ((names["originalName"] is None) != (names["originalSource"] == "unavailable")):
            errors.append(f"people/{person_id}: unavailable original names require explicit unavailable provenance")
        family = person.get("family")
        if family:
            reference = people.get(family["referencePersonId"])
            if reference is None or reference.get("mergedInto"):
                errors.append(f"people/{person_id}: family reference must be an active registered identity")
            if "names" not in person:
                errors.append(f"people/{person_id}: family membership requires name provenance")
            reference_family = (reference or {}).get("family", {})
            if reference_family.get("id") != family["id"] or reference_family.get("surname") != family["surname"]:
                errors.append(f"people/{person_id}: family reference must belong to the same surname/group")
        if "mergedInto" in person:
            target = people.get(person["mergedInto"])
            if target is None or target["id"] == person_id or "mergedInto" in target:
                errors.append(f"people/{person_id}: mergedInto must reference a distinct active identity")
        if person["id"] != person_id:
            errors.append(f"people/{person_id}: record id does not match its catalogue key")
        folder = person["folder"]
        if folder in folder_owners:
            errors.append(f"people/{person_id}: folder {folder} is already assigned to {folder_owners[folder]}")
        else:
            folder_owners[folder] = person_id
        for photo_id in person["identityAnchors"]:
            if photo_id not in photos:
                errors.append(f"people/{person_id}: identity anchor {photo_id} has no photo record")
            if photo_id in anchor_owners:
                errors.append(
                    f"people/{person_id}: identity anchor {photo_id} is also assigned to {anchor_owners[photo_id]}"
                )
            else:
                anchor_owners[photo_id] = person_id

    action_ids = set()
    for photo_id, photo in photos.items():
        for person_id in photo.get("rejectedPersonIds", []):
            if person_id not in people:
                errors.append(f"photos/{photo_id}: rejected identity {person_id} has no person record")
    for index, action in enumerate(data["actions"]):
        if action["id"] in action_ids:
            errors.append(f"actions/{index}: duplicate action id {action['id']}")
        action_ids.add(action["id"])
        for photo_id in action["photoIds"]:
            if photo_id not in photos:
                errors.append(f"actions/{index}: photo {photo_id} has no photo record")
        person_id = action.get("personId")
        if person_id is not None and person_id not in people:
            errors.append(f"actions/{index}: person {person_id} has no person record")

    actions_by_id = {action["id"]: action for action in data["actions"]}
    undone_ids = set()
    for index, action in enumerate(data["actions"]):
        if action["type"] != "action-undone":
            continue
        target = action.get("undoes")
        if target not in actions_by_id or actions_by_id[target]["type"] == "action-undone":
            errors.append(f"actions/{index}: undoes must reference an existing applied action")
        elif target in undone_ids:
            errors.append(f"actions/{index}: action {target} has already been undone")
        elif action["photoIds"] != actions_by_id[target]["photoIds"]:
            errors.append(f"actions/{index}: undo photo IDs do not match the applied action")
        else:
            undone_ids.add(target)

    return errors


def _has_timezone(value):
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def validate_catalog(data):
    errors = validation_errors(data)
    if errors:
        raise ValueError("invalid likeness library metadata:\n  " + "\n  ".join(errors))


def load_catalog(path=CATALOG_PATH):
    """Load the catalogue and fail explicitly if JSON or its references are invalid."""
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    validate_catalog(data)
    return data


def path_for_root(root):
    """Use an isolated library's catalogue when it has one."""
    local = pathlib.Path(root) / ".likeness-library.json"
    return local if local.is_file() else CATALOG_PATH


def with_configured_anchors(catalog, cfg, photos):
    """Migrate legacy explicit anchor choices into a run-local catalogue view."""
    result = json.loads(json.dumps(catalog))
    folders = {}
    for photo in photos:
        folders.setdefault(photo.key, []).append(photo)
    owned = {person["folder"] for person in result["people"].values()}
    for folder, rows in folders.items():
        if folder in owned:
            continue
        patterns = next((
            values for name, values in cfg.get("likeness", {}).get("anchors", {}).items()
            if name.casefold() == folder.split("/")[-1].casefold()
        ), ())
        anchors = [
            photo for photo in rows
            if any(pattern.casefold() in photo.name.casefold() for pattern in patterns)
            and photo_id_from_name(photo.name)
        ]
        if not anchors:
            continue
        person_id = "person_" + uuid.uuid5(uuid.NAMESPACE_URL, "likeness:" + folder.casefold()).hex
        result["people"][person_id] = {
            "id": person_id, "folder": folder, "displayName": folder.split("/")[-1],
            "folderHistory": [], "identityAnchors": [photo_id_from_name(photo.name) for photo in anchors],
            "protected": False,
        }
        for photo in anchors:
            result["photos"].setdefault(photo_id_from_name(photo.name), {
                "contentSha256": content_sha256(photo.path), "protected": False,
            })
    return result


def save_catalog(data, path=None):
    """Validate and atomically save the tracked catalogue; filesystem errors propagate."""
    validate_catalog(data)
    destination = pathlib.Path(path) if path is not None else CATALOG_PATH
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as output:
            temporary_path = pathlib.Path(output.name)
            json.dump(data, output, ensure_ascii=False, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        report_assets.replace_file(temporary_path, destination)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return destination


if __name__ == "__main__":
    catalog = load_catalog()
    print(f"valid likeness metadata: {len(catalog['people'])} people, {len(catalog['photos'])} photos, "
          f"{len(catalog['actions'])} actions")
