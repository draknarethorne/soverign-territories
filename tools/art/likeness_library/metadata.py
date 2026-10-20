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
    for person_id, person in people.items():
        if person["id"] != person_id:
            errors.append(f"people/{person_id}: record id does not match its catalogue key")
        for photo_id in person["identityAnchors"]:
            if photo_id not in photos:
                errors.append(f"people/{person_id}: identity anchor {photo_id} has no photo record")

    action_ids = set()
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


def save_catalog(data):
    """Validate and atomically save the tracked catalogue; filesystem errors propagate."""
    validate_catalog(data)
    destination = CATALOG_PATH
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
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return destination


if __name__ == "__main__":
    catalog = load_catalog()
    print(f"valid likeness metadata: {len(catalog['people'])} people, {len(catalog['photos'])} photos, "
          f"{len(catalog['actions'])} actions")
