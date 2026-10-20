#!/usr/bin/env python3
"""Validate and preview user-staged likeness actions without applying them."""
import argparse
import json
import os
import pathlib
import sys

from jsonschema import Draft7Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/art"))
import likeness  # noqa: E402
import originals  # noqa: E402
from likeness_library import metadata  # noqa: E402

MANIFEST_SCHEMA = ROOT / "data/art/_schema/likeness-action-manifest.schema.json"
PHOTO_ROOTS = ("Angels", "Sisters", "Prospects", "Potentials", "Artists", "Models", "Various")
IGNORED_PARTS = {"_archive", "_junk", "_retired"}
MOVE_ACTIONS = {"sent-to-review", "rejected-to-various", "review-approved"}
ANCHOR_ACTIONS = {"anchor-added", "anchor-removed"}
PROTECTION_ACTIONS = {"photo-protected", "photo-unprotected"}


def load_manifest(path):
    """Read a manifest and reject schema errors before any photo-library access."""
    document = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda item: str(item.absolute_path))
    ]
    if errors:
        raise ValueError("invalid likeness action manifest:\n  " + "\n  ".join(errors))
    return document


def _key(path):
    return os.path.normcase(str(pathlib.Path(path).resolve()))


def _index_photos(root):
    """Index active source IDs across person Gallery and Review folders."""
    result = {}
    root = pathlib.Path(root).resolve()
    for section in PHOTO_ROOTS:
        section_path = root / section
        if not section_path.is_dir():
            continue
        for bucket in ("gallery", "review"):
            for directory in section_path.rglob(bucket):
                if not directory.is_dir() or any(part.casefold() in IGNORED_PARTS for part in directory.parts):
                    continue
                try:
                    directory.resolve().relative_to(root)
                except ValueError:
                    continue
                for photo in originals.images(directory):
                    photo_id = metadata.photo_id_from_name(photo.name)
                    if photo_id:
                        result.setdefault(photo_id, []).append(photo)
    return result


def _catalog_people_by_folder(catalog):
    people = {}
    duplicates = set()
    for person_id, person in catalog["people"].items():
        folder = person["folder"].casefold()
        if folder in people:
            duplicates.add(folder)
        else:
            people[folder] = (person_id, person)
    return people, duplicates


def _catalog_anchor_owners(catalog):
    owners = {}
    for person_id, person in catalog["people"].items():
        for photo_id in person["identityAnchors"]:
            owners[photo_id] = person_id
    return owners


def _category_for_action(action_type):
    if action_type in MOVE_ACTIONS:
        return "move"
    if action_type in ANCHOR_ACTIONS:
        return "anchor"
    if action_type in PROTECTION_ACTIONS:
        return "protection"
    return None


def _destination(action, root, pool_folder):
    if action["type"] == "sent-to-review":
        return root / action["personFolder"] / "review"
    if action["type"] == "review-approved":
        return root / action["personFolder"] / "gallery"
    if action["type"] == "rejected-to-various":
        return root / pool_folder / "gallery"
    return None


def validate_manifest(document, root, catalog, pool_folder="Prospects/Various"):
    """Return structural/current-library errors and safe preview records; perform no writes."""
    root = pathlib.Path(root).resolve()
    schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = [
        f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda item: str(item.absolute_path))
    ]
    if errors:
        return errors, []
    if not root.is_dir():
        return [f"photo-library root does not exist: {root}"], []

    photo_index = _index_photos(root)
    people_by_folder, duplicate_folders = _catalog_people_by_folder(catalog)
    anchor_owners = _catalog_anchor_owners(catalog)
    pool_key = pathlib.PurePosixPath(pool_folder).as_posix().casefold()
    occupied = {}
    plans = []
    for index, action in enumerate(document["actions"]):
        label = f"actions/{index}"
        photo_id = action["photoId"]
        relative_folder = pathlib.PurePosixPath(action["personFolder"])
        folder_key = relative_folder.as_posix().casefold()
        if folder_key == pool_key:
            errors.append(f"{label}: the unassigned pool is not a person identity folder")
        if folder_key in duplicate_folders:
            errors.append(f"{label}: multiple catalogue people claim {action['personFolder']}")
        person_record = people_by_folder.get(folder_key)
        if person_record and action.get("personId") and person_record[0] != action["personId"]:
            errors.append(f"{label}: personId does not own folder {action['personFolder']}")
        if action.get("personId") and not person_record:
            errors.append(f"{label}: personId is not registered to {action['personFolder']}")
        if (
            action["type"] == "anchor-added"
            and photo_id in anchor_owners
            and (not person_record or anchor_owners[photo_id] != person_record[0])
        ):
            errors.append(f"{label}: {photo_id} is already anchored to another person")

        current_paths = photo_index.get(photo_id, [])
        if not current_paths:
            errors.append(f"{label}: photo {photo_id} is missing from the active library")
            continue
        if len(current_paths) != 1:
            errors.append(f"{label}: photo {photo_id} is ambiguous ({len(current_paths)} active copies)")
            continue
        source = current_paths[0]
        try:
            source.resolve().relative_to(root)
        except ValueError:
            errors.append(f"{label}: photo path resolves outside the photo-library root")
            continue
        expected_directory = root / pathlib.Path(*relative_folder.parts) / action["sourceBucket"].lower()
        if _key(source.parent) != _key(expected_directory):
            errors.append(
                f"{label}: photo is in {source.parent.relative_to(root).as_posix()}, "
                f"not {action['personFolder']}/{action['sourceBucket'].lower()}"
            )
            continue
        actual_hash = metadata.content_sha256(source)
        if actual_hash != action["contentSha256"]:
            errors.append(f"{label}: content hash is stale for {photo_id}")
            continue

        photo_actions = occupied.setdefault(photo_id, {})
        category = _category_for_action(action["type"])
        if category in photo_actions:
            errors.append(
                f"{label}: conflicts with actions/{photo_actions[category]} for {photo_id} ({category} action)"
            )
        if category == "move" and "anchor" in photo_actions:
            errors.append(f"{label}: a photo cannot change identity anchor state and move in the same manifest")
        if category == "anchor" and "move" in photo_actions:
            errors.append(f"{label}: a photo cannot move and change identity anchor state in the same manifest")
        photo_actions[category] = index

        if person_record:
            person_id = person_record[0]
            anchored = photo_id in person_record[1]["identityAnchors"]
        else:
            person_id, anchored = action.get("personId"), False
        stored_photo = catalog["photos"].get(photo_id)
        protected = bool(
            stored_photo
            and stored_photo["protected"]
            and stored_photo["contentSha256"] == actual_hash
        )
        if action["type"] == "anchor-added" and anchored:
            errors.append(f"{label}: {photo_id} is already an identity anchor")
        elif action["type"] == "anchor-removed" and not anchored:
            errors.append(f"{label}: {photo_id} is not a registered identity anchor")
        elif action["type"] == "photo-protected" and protected:
            errors.append(f"{label}: {photo_id} is already protected")
        elif action["type"] == "photo-unprotected" and not protected:
            errors.append(f"{label}: {photo_id} is not currently protected")

        destination = _destination(action, root, pool_folder)
        if destination is not None:
            try:
                destination.resolve().relative_to(root)
            except ValueError:
                errors.append(f"{label}: destination resolves outside the photo-library root")
                continue
            target = destination / source.name
            if _key(target) != _key(source) and target.exists():
                errors.append(f"{label}: destination already exists: {target}")
        else:
            target = None
        plans.append({
            "index": index,
            "type": action["type"],
            "photoId": photo_id,
            "source": source,
            "destination": target,
            "personId": person_id,
        })
    return errors, plans


def print_preview(plans):
    for plan in plans:
        if plan["destination"] is None:
            print(f"  {plan['type']}: {plan['photoId']} (catalogue decision only)")
        else:
            suffix = " (destination folder will be created)" if not plan["destination"].parent.exists() else ""
            print(f"  {plan['type']}: {plan['source']} -> {plan['destination']}{suffix}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "preview"):
        subparser = subparsers.add_parser(command, help=f"{command} a staged action manifest")
        subparser.add_argument("manifest", help="JSON file downloaded from the review gallery")
        subparser.add_argument("--root", help="photo library root (default: workspaces.json paths.workRoot)")
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest)
        cfg = likeness.cw.load_cfg()
        root = pathlib.Path(args.root) if args.root else pathlib.Path(likeness.cw.work_root(cfg))
        root = root.resolve()
        catalog = metadata.load_catalog()
        pool_folder = likeness.pool_home(likeness.settings(cfg))
        errors, plans = validate_manifest(manifest, root, catalog, pool_folder)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("invalid manifest:")
        for error in errors:
            print(f"  {error}")
        return 1
    print(f"valid likeness action manifest: {len(plans)} action(s)")
    if args.command == "preview":
        print_preview(plans)
        print("preview only; no files or catalogue data were changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
