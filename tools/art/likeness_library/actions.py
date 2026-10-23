#!/usr/bin/env python3
"""Validate, preview, apply and undo user-staged likeness actions."""
import argparse
import copy
import datetime
import json
import os
import pathlib
import shutil
import sys
import uuid

from jsonschema import Draft7Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/art"))
import likeness  # noqa: E402
import originals  # noqa: E402
import library_backup  # noqa: E402
import people  # noqa: E402
from likeness_library import metadata, person_actions, person_rename, rejections  # noqa: E402

cw = likeness.cw

MANIFEST_SCHEMA = ROOT / "data/art/_schema/likeness-action-manifest.schema.json"
PHOTO_ROOTS = ("Angels", "Sisters", "Prospects", "Potentials", "Artists", "Models", "Various")
IGNORED_PARTS = {"_archive", "_junk", "_retired"}
MOVE_ACTIONS = {"sent-to-review", "rejected-to-various", "match-rejected", "review-approved", "match-accepted", "photo-retired"}
ANCHOR_ACTIONS = {"anchor-added", "anchor-removed"}
PROTECTION_ACTIONS = {"photo-protected", "photo-unprotected"}
WORKFLOW_ACTIONS = {"workflow-photo-selected"}


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
    if action_type in WORKFLOW_ACTIONS:
        return "workflow"
    return None


def _destination(action, root, pool_folder):
    if action["type"] == "photo-retired":
        return root / "_retired" / "photos" / action["personFolder"] / action["sourceBucket"].lower()
    if action["type"] == "match-accepted":
        return root / action["destinationFolder"] / "review"
    if action["type"] == "sent-to-review":
        return root / action["personFolder"] / "review"
    if action["type"] == "review-approved":
        return root / action["personFolder"] / "gallery"
    if action["type"] in ("rejected-to-various", "match-rejected"):
        return root / pool_folder / "gallery"
    return None


def _workflow_photo_plan(action, source, root, cfg):
    """Resolve a staged workflow-photo choice and its restorable current selection."""
    if cfg is None:
        raise ValueError("workflow-photo selection requires workspace configuration")
    folder = pathlib.Path(root) / pathlib.Path(*pathlib.PurePosixPath(action["personFolder"]).parts)
    group, hero = action["personFolder"].split("/", 1)
    if group not in ("Angels", "Sisters"):
        raise ValueError("workflow-photo selection is supported only for Angels and Sisters")
    configured = cfg.get("photos", {})
    hero_key = next((name for name in configured if name.casefold() == hero.casefold()), None)
    if hero_key is None:
        raise ValueError(f"no base workflow photo is configured for {hero}")
    current_name = configured[hero_key]
    target_id = metadata.photo_id_from_name(source.name)
    if metadata.photo_id_from_name(current_name) == target_id:
        raise ValueError(f"{target_id} is already the configured workflow photo for {hero}")
    width, height = cfg.get("standardSize") or (944, 1104)

    def scaled_path(original):
        return (
            original.parent.parent / f"gallery_{width}x{height}"
            / f"{original.stem}_{width}x{height}.png"
        )

    current_id = metadata.photo_id_from_name(current_name)
    old_matches = [
        photo for photo in originals.images(folder / "gallery")
        if metadata.photo_id_from_name(photo.name) == current_id
    ]
    if len(old_matches) != 1:
        raise ValueError(
            f"configured workflow photo for {hero} must match exactly one Gallery original to support undo"
        )
    old_scaled = scaled_path(old_matches[0])
    new_scaled = scaled_path(source)
    if not old_scaled.is_file():
        raise ValueError(f"current scaled workflow photo is missing: {old_scaled}")
    if not new_scaled.is_file():
        raise ValueError(f"scaled version of the staged photo is missing: {new_scaled}")
    return {
        "workflowHero": hero_key,
        "workflowPhotoBefore": current_name,
        "workflowPhotoAfter": new_scaled.name,
        "workflowSourceBefore": _relative_file(root, old_scaled),
        "workflowSourceAfter": _relative_file(root, new_scaled),
        "workflowBeforePath": old_scaled,
        "workflowAfterPath": new_scaled,
    }


def selected_photo_ids(cfg):
    """Return source IDs currently selected by a base or flow-specific workspace."""
    names = list(cfg.get("photos", {}).values())
    for flow in cfg.get("flows", {}).values():
        names.extend(flow.get("photos", {}).values())
    return {photo_id for name in names if (photo_id := metadata.photo_id_from_name(name))}


def _require_configured_work_root(root, cfg):
    configured_root = pathlib.Path(cw.work_root(cfg)).resolve()
    if pathlib.Path(root).resolve() != configured_root:
        raise ValueError(
            "workflow-photo actions can only be applied against the configured library root; "
            "do not apply them with an isolated sandbox --root"
        )


def validate_manifest(document, root, catalog, pool_folder="Prospects/Various", chosen_ids=(), cfg=None):
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

    if any(action["type"] == person_rename.ACTION for action in document["actions"]):
        return person_rename.validate(document, root, catalog, cfg or {})
    person_errors, person_plans = person_actions.validate_actions(document, root, catalog)
    if person_errors:
        return person_errors, []
    photo_index = _index_photos(root) if any(
        action["type"] not in person_actions.PROTECTION_ACTIONS for action in document["actions"]
    ) else {}
    people_by_folder, duplicate_folders = _catalog_people_by_folder(catalog)
    anchor_owners = _catalog_anchor_owners(catalog)
    pool_key = pathlib.PurePosixPath(pool_folder).as_posix().casefold()
    occupied = {}
    workflow_targets = {}
    plans = list(person_plans)
    for index, action in enumerate(document["actions"]):
        if action["type"] in person_actions.PROTECTION_ACTIONS:
            continue
        label = f"actions/{index}"
        photo_id = action["photoId"]
        relative_folder = pathlib.PurePosixPath(action["personFolder"])
        if any(
            part in (".", "..") or any(character in part for character in ("\\", ":"))
            for part in relative_folder.parts
        ):
            errors.append(f"{label}: unsafe person folder path")
            continue
        folder_key = relative_folder.as_posix().casefold()
        if folder_key == pool_key:
            errors.append(f"{label}: the unassigned pool is not a person identity folder")
        if action["type"] in WORKFLOW_ACTIONS and action["sourceBucket"] != "Gallery":
            errors.append(f"{label}: workflow photo must be selected from Gallery")
            continue
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
        if action["type"] in MOVE_ACTIONS and photo_id in chosen_ids:
            errors.append(f"{label}: {photo_id} is selected by an active workspace workflow")
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
        if category == "workflow" and "move" in photo_actions:
            errors.append(f"{label}: a workflow photo cannot move in the same manifest")
        if category == "move" and "workflow" in photo_actions:
            errors.append(f"{label}: a workflow photo cannot move in the same manifest")
        if category == "workflow":
            previous = workflow_targets.get(folder_key)
            if previous is not None:
                errors.append(f"{label}: conflicts with actions/{previous} (one workflow photo per person)")
            workflow_targets[folder_key] = index
        photo_actions[category] = index

        if person_record:
            person_id = person_record[0]
            anchored = photo_id in person_record[1]["identityAnchors"]
        else:
            person_id, anchored = action.get("personId"), False
        stored_photo = catalog["photos"].get(photo_id)
        if (
            stored_photo and stored_photo.get("rejectedPersonIds")
            and stored_photo["contentSha256"] != actual_hash
        ):
            errors.append(f"{label}: rejected-identity metadata is stale; review changed photo bytes")
            continue
        protected = bool(
            stored_photo
            and stored_photo["protected"]
            and stored_photo["contentSha256"] == actual_hash
        )
        if action["type"] == "match-rejected":
            if not person_record or person_record[1].get("mergedInto"):
                errors.append(f"{label}: persistent rejection requires an active registered identity")
                continue
            if photo_id in anchor_owners or protected:
                errors.append(f"{label}: remove photo protection or anchor before persistent rejection")
                continue
            if stored_photo and stored_photo["contentSha256"] != actual_hash:
                errors.append(f"{label}: photo metadata is stale; resolve changed photo bytes first")
                continue
        if action["type"] in ("match-accepted", "review-approved"):
            target_id = (
                action["destinationPersonId"] if action["type"] == "match-accepted"
                else person_id
            )
            if target_id:
                try:
                    rejections.require_destination(catalog, photo_id, actual_hash, target_id)
                except ValueError as exc:
                    errors.append(f"{label}: {exc}")
                    continue
        if action["type"] == "photo-retired":
            if protected or photo_id in anchor_owners:
                errors.append(f"{label}: remove photo protection or identity anchor before retirement")
                continue
            if any(
                other["photoId"] == photo_id and other["type"] in PROTECTION_ACTIONS
                for other in document["actions"] if "photoId" in other
            ):
                errors.append(f"{label}: photo protection and retirement require separate manifests")
                continue
        if action["type"] == "match-accepted":
            destination_folder = pathlib.PurePosixPath(action["destinationFolder"])
            if any(part in (".", "..") for part in destination_folder.parts):
                errors.append(f"{label}: unsafe destination folder path")
                continue
            target_folder = root.joinpath(*destination_folder.parts)
            destination_person = people_by_folder.get(action["destinationFolder"].casefold())
            if (
                not target_folder.is_dir()
                or target_folder.resolve() != target_folder
                or action["destinationFolder"].casefold() == folder_key
                or action["destinationFolder"].casefold() in duplicate_folders
                or not destination_person
                or destination_person[0] != action["destinationPersonId"]
                or "mergedInto" in destination_person[1]
            ):
                errors.append(f"{label}: destination must be a distinct, existing, unambiguous identity with its current stable ID")
                continue
            if protected or photo_id in anchor_owners:
                errors.append(f"{label}: remove photo protection or identity anchor before reassignment")
                continue
        if action["type"] == "anchor-added" and anchored:
            errors.append(f"{label}: {photo_id} is already an identity anchor")
        elif action["type"] == "anchor-removed" and not anchored:
            errors.append(f"{label}: {photo_id} is not a registered identity anchor")
        elif action["type"] == "photo-protected" and protected:
            errors.append(f"{label}: {photo_id} is already protected")
        elif action["type"] == "photo-unprotected" and not protected:
            errors.append(f"{label}: {photo_id} is not currently protected")

        workflow = None
        if action["type"] in WORKFLOW_ACTIONS:
            try:
                workflow = _workflow_photo_plan(action, source, root, cfg)
            except (OSError, ValueError) as exc:
                errors.append(f"{label}: {exc}")
                continue
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
            "action": action,
            "source": source,
            "destination": target,
            "personId": person_id,
            "workflow": workflow,
        })
    return errors, plans


def print_preview(plans):
    for plan in plans:
        if plan["type"] == person_rename.ACTION:
            if plan.get("partner"):
                print("  confirmed two-person name swap (standalone transaction):")
                print_preview([{k: v for k, v in plan.items() if k != "partner"}, plan["partner"]])
                continue
            print(f"  rename identity {plan['personId']}: {plan['source']} -> {plan['destination']}")
            print(f"    recorded person name: {plan['action']['expectedRecordedName']} -> {plan['action']['newName']}")
            if plan["source"] == plan["destination"]:
                print("    fixed character slot/folder and workflow inputs remain unchanged")
            if "expectedProtected" in plan["action"]:
                print(f"    identity protection remains {'ON' if plan['action']['expectedProtected'] else 'OFF'}; membership unchanged")
            print("    preserve original filenames/IDs and history; refresh reports after apply")
            continue
        if plan["type"] in person_actions.PROTECTION_ACTIONS:
            print(f"  {plan['type']}: {plan['personId']} ({plan['action']['personFolder']}; identity permission only)")
            continue
        if plan.get("workflow"):
            workflow = plan["workflow"]
            print(
                f"  select workflow photo for {workflow['workflowHero']}: "
                f"{workflow['workflowPhotoBefore']} -> {workflow['workflowPhotoAfter']}"
            )
            continue
        if plan["destination"] is None:
            print(f"  {plan['type']}: {plan['photoId']} (catalogue decision only)")
        else:
            suffix = " (destination folder will be created)" if not plan["destination"].parent.exists() else ""
            print(f"  {plan['type']}: {plan['source']} -> {plan['destination']}{suffix}")


def _person_record(catalog, folder):
    matches = [
        (person_id, person)
        for person_id, person in catalog["people"].items()
        if person["folder"].casefold() == folder.casefold()
    ]
    if len(matches) > 1:
        raise ValueError(f"multiple catalogue people claim {folder}")
    return matches[0] if matches else (None, None)


def _ensure_person(catalog, action, root):
    folder = action["personFolder"]
    person_id, person = _person_record(catalog, folder)
    if person:
        return person_id, person
    person_id = action.get("personId") or metadata.new_person_id()
    display_name = people.name_of(pathlib.Path(root) / folder) or pathlib.PurePosixPath(folder).name
    person = {
        "id": person_id,
        "displayName": display_name,
        "folder": folder,
        "folderHistory": [],
        "identityAnchors": [],
    }
    catalog["people"][person_id] = person
    return person_id, person


def _catalog_state(catalog, person_id, photo_id):
    return {
        "person": copy.deepcopy(catalog["people"].get(person_id)),
        "photo": copy.deepcopy(catalog["photos"].get(photo_id)),
    }


def _relative_file(root, path):
    try:
        return pathlib.Path(path).resolve().relative_to(pathlib.Path(root).resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path is outside the photo-library root: {path}") from exc


def _apply_catalog_action(catalog, plan, root, batch_id):
    action = plan["action"]
    photo_id = action["photoId"]
    source = plan["source"]
    actual_hash = metadata.content_sha256(source)
    before_person_id, _ = _person_record(catalog, action["personFolder"])
    before_state = _catalog_state(catalog, before_person_id, photo_id)
    person_id, person = _ensure_person(catalog, action, root)
    old_photo = catalog["photos"].get(photo_id)
    protected = bool(
        old_photo
        and old_photo["protected"]
        and old_photo["contentSha256"] == actual_hash
    )
    photo = copy.deepcopy(old_photo) if old_photo else {}
    photo.update({"contentSha256": actual_hash, "protected": protected})

    action_type = action["type"]
    if action_type == "anchor-added":
        person["identityAnchors"].append(photo_id)
    elif action_type == "anchor-removed":
        person["identityAnchors"].remove(photo_id)
    elif action_type == "photo-protected":
        photo["protected"] = True
    elif action_type == "photo-unprotected":
        photo["protected"] = False
    elif action_type in ("sent-to-review", "rejected-to-various", "match-rejected"):
        person["identityAnchors"] = [
            anchor for anchor in person["identityAnchors"] if anchor != photo_id
        ]
    if action_type == "match-rejected":
        photo["rejectedPersonIds"] = sorted(set(photo.get("rejectedPersonIds", [])) | {person_id})
    catalog["photos"][photo_id] = photo
    after_state = _catalog_state(catalog, person_id, photo_id)
    source_relative = _relative_file(root, source)
    destination_relative = (
        _relative_file(root, plan["destination"]) if plan["destination"] is not None else source_relative
    )
    record = {
        "id": "action_" + uuid.uuid4().hex,
        "batchId": batch_id,
        "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "actor": "user",
        "type": action_type,
        "photoIds": [photo_id],
        "personId": person_id,
        "contentSha256": actual_hash,
        "source": source_relative,
        "destination": destination_relative,
        "reason": "staged in the local likeness review gallery",
        "beforeState": before_state,
        "afterState": after_state,
    }
    if action_type == "match-accepted":
        record["destinationPersonId"] = action["destinationPersonId"]
    catalog["actions"].append(record)


def _apply_workflow_action(catalog, plan, root, batch_id):
    action = plan["action"]
    photo_id = action["photoId"]
    person_id, _person = _person_record(catalog, action["personFolder"])
    before_state = _catalog_state(catalog, person_id, photo_id)
    old_photo = catalog["photos"].get(photo_id)
    protected = bool(
        old_photo
        and old_photo["protected"]
        and old_photo["contentSha256"] == action["contentSha256"]
    )
    catalog["photos"][photo_id] = copy.deepcopy(old_photo) if old_photo else {}
    catalog["photos"][photo_id].update({
        "contentSha256": action["contentSha256"], "protected": protected,
    })
    after_state = _catalog_state(catalog, person_id, photo_id)
    source_relative = _relative_file(root, plan["source"])
    workflow = plan["workflow"]
    record = {
        "id": "action_" + uuid.uuid4().hex,
        "batchId": batch_id,
        "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "actor": "user",
        "type": action["type"],
        "photoIds": [photo_id],
        "contentSha256": action["contentSha256"],
        "source": source_relative,
        "destination": source_relative,
        "reason": "workflow photo selected from the local likeness review gallery",
        "beforeState": before_state,
        "afterState": after_state,
        **{
            key: workflow[key]
            for key in (
                "workflowHero",
                "workflowPhotoBefore",
                "workflowPhotoAfter",
                "workflowSourceBefore",
                "workflowSourceAfter",
            )
        },
    }
    if person_id:
        record["personId"] = person_id
    catalog["actions"].append(record)


def _repoint_workflow_photos(plans, cfg):
    selections = {
        plan["workflow"]["workflowHero"]: (
            plan["workflow"]["workflowPhotoBefore"],
            plan["workflow"]["workflowAfterPath"],
        )
        for plan in plans if plan.get("workflow")
    }
    if selections:
        cw.repoint_photos(cfg, selections, False)


def _restore_workflow_photos(plans, cfg):
    selections = {
        plan["workflow"]["workflowHero"]: (
            plan["workflow"]["workflowPhotoAfter"],
            plan["workflow"]["workflowBeforePath"],
        )
        for plan in plans if plan.get("workflow")
    }
    if selections:
        cw.repoint_photos(cfg, selections, False)


def _create_action_backup(root, cfg, batch_id, *, rename_plan=None, reverse=False):
    catalogue = metadata.path_for_root(root)
    if (
        rename_plan is not None and catalogue.is_file()
        and (rename_plan.get("partner") or (
            rename_plan["source"] == rename_plan["destination"]
            and rename_plan["source"].parent.name in person_rename.CAST_CATEGORIES
        ))
    ):
        swap = bool(rename_plan.get("partner"))
        members = (rename_plan, rename_plan["partner"]) if swap else (rename_plan,)
        scoped_sources = [("likeness-catalogue", catalogue)]
        recovery_members = []
        for index, member in enumerate(members):
            state = member["rename"]
            folder = member["destination"] if reverse else member["source"]
            history = state["newHistoryPath"] if reverse else state["oldHistoryPath"]
            if history:
                label = f"identity-history-{index}" if swap else "identity-history"
                scoped_sources.append((label, folder / pathlib.Path(history)))
            recovery_members.append({
                "personId": member["personId"],
                "source": str(member["source"]), "destination": str(member["destination"]),
                "renameState": copy.deepcopy(state),
                "unchangedIdentityTreeSha256": state[
                    "afterTreeSha256" if reverse else "beforeTreeSha256"
                ],
            })
            if swap:
                recovery_members[-1]["privateStaging"] = str(person_rename.swap_staging(rename_plan) / str(index))
        recovery = {
            "type": "person-name-swap" if swap else person_rename.ACTION,
            "batchId": batch_id, "reverse": reverse,
            "note": (
                "Both identity trees move intact via private staging; only histories and catalogue bytes change."
                if swap else "Fixed cast slot: only history and catalogue bytes change; images are guarded, not copied."
            ),
        }
        if swap:
            recovery["members"] = recovery_members
        else:
            recovery.update(recovery_members[0])
        return library_backup.create_backup(
            root, stamp=f"likeness-actions-{batch_id}", apply=True,
            scoped_sources=scoped_sources, recovery=recovery,
        )
    return library_backup.create_backup(
        root,
        cfg.get("paths", {}).get("inputsRoot"),
        ROOT / "workflows" / "workspaces.json",
        stamp=f"likeness-actions-{batch_id}",
        apply=True,
        extra_sources=[("likeness-catalogue", metadata.path_for_root(root))],
    )


def _catalog_guard(root, catalog):
    paths = {metadata.path_for_root(root), pathlib.Path(root) / ".likeness-library.json"}
    return copy.deepcopy(catalog), {
        path: path.read_bytes() if path.exists() else None for path in paths
    }


def _revalidate_catalog(guard, catalog):
    before, files = guard
    if before != catalog or any(
        (path.read_bytes() if path.exists() else None) != content
        for path, content in files.items()
    ):
        raise ValueError("catalogue changed during backup; no actions applied")


def _rollback_moves(completed, created_directories):
    failures = []
    for source, destination in reversed(completed):
        try:
            if not destination.is_file() or source.exists():
                raise OSError(f"cannot safely restore moved photo: {destination} -> {source}")
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(destination), str(source))
        except OSError as exc:
            failures.append(str(exc))
    for directory in reversed(created_directories):
        try:
            directory.rmdir()
        except FileNotFoundError:
            pass
        except OSError as exc:
            failures.append(f"could not remove rollback directory {directory}: {exc}")
    return failures


def _move_files(plans, root):
    completed, created_directories = [], []
    root = pathlib.Path(root).resolve()
    try:
        for plan in plans:
            destination = plan["destination"]
            if destination is None or _key(destination) == _key(plan["source"]):
                continue
            source = plan["source"]
            try:
                source.resolve().relative_to(root)
                destination.resolve().relative_to(root)
            except ValueError as exc:
                raise OSError(f"move path resolves outside the photo-library root: {source} -> {destination}") from exc
            if metadata.content_sha256(source) != plan["action"]["contentSha256"]:
                raise OSError(f"photo changed after validation: {source}")
            if destination.exists():
                raise OSError(f"move destination appeared after validation: {destination}")
            missing = []
            parent = destination.parent
            while not parent.exists() and parent != root:
                missing.append(parent)
                parent = parent.parent
            if parent != root and root not in parent.parents:
                raise OSError(f"destination parent escapes the photo-library root: {destination}")
            for directory in reversed(missing):
                try:
                    directory.mkdir()
                except FileExistsError:
                    if not directory.is_dir():
                        raise
                else:
                    created_directories.append(directory)
            shutil.move(str(source), str(destination))
            completed.append((source, destination))
    except OSError as exc:
        if not completed and not created_directories:
            raise
        failures = _rollback_moves(completed, created_directories)
        if failures:
            raise OSError(f"{exc}; rollback also failed: {'; '.join(failures)}") from exc
        raise
    return completed, created_directories


def apply_actions(document, root, catalog, cfg, pool_folder, *, backup_fn=None, save_fn=None):
    """Back up, revalidate, apply staged actions transactionally, and save an audit history."""
    root = pathlib.Path(root).resolve()
    if any(action["type"] in WORKFLOW_ACTIONS for action in document["actions"]):
        _require_configured_work_root(root, cfg)
    chosen_ids = selected_photo_ids(cfg)
    errors, plans = validate_manifest(document, root, catalog, pool_folder, chosen_ids, cfg)
    if errors:
        raise ValueError("cannot apply invalid manifest:\n  " + "\n  ".join(errors))
    batch_id = "batch_" + uuid.uuid4().hex
    updated = copy.deepcopy(catalog)
    rename_record = None
    for plan in plans:
        if plan["type"] == person_rename.ACTION:
            rename_record = person_rename.catalog_action(updated, plan, batch_id)
        elif plan["type"] in person_actions.PROTECTION_ACTIONS:
            person_actions.apply_action(updated, plan, batch_id)
        elif plan.get("workflow"):
            _apply_workflow_action(updated, plan, root, batch_id)
        else:
            _apply_catalog_action(updated, plan, root, batch_id)
    metadata.validate_catalog(updated)

    catalog_guard = _catalog_guard(root, catalog)
    rename_plan = next((plan for plan in plans if plan["type"] == person_rename.ACTION), None)
    backup = (
        backup_fn(root, cfg, batch_id) if backup_fn else
        _create_action_backup(root, cfg, batch_id, rename_plan=rename_plan)
    )
    _revalidate_catalog(catalog_guard, catalog)
    errors, checked_plans = validate_manifest(document, root, catalog, pool_folder, chosen_ids, cfg)
    if errors:
        raise ValueError("library changed after backup; no actions applied:\n  " + "\n  ".join(errors))
    if any(
        _key(before["source"]) != _key(after["source"])
        or (before["destination"] is None) != (after["destination"] is None)
        or (
            before["destination"] is not None
            and _key(before["destination"]) != _key(after["destination"])
        )
        or before.get("workflow") != after.get("workflow")
        or before.get("rename") != after.get("rename")
        or before.get("partner") != after.get("partner")
        for before, after in zip(plans, checked_plans)
    ):
        raise ValueError("action destinations changed after backup; no actions applied")

    rename_plan = next((plan for plan in checked_plans if plan["type"] == person_rename.ACTION), None)
    completed, created_directories = _move_files(
        [plan for plan in checked_plans if plan["type"] != person_rename.ACTION], root,
    )
    workflow_attempted = any(plan.get("workflow") for plan in checked_plans)
    rename_completed = False
    try:
        if rename_plan:
            person_rename.change_files(rename_plan)
            rename_completed = True
            assert rename_record is not None
            rename_record["renameState"] = copy.deepcopy(rename_plan["rename"])
            if rename_plan.get("partner"):
                rename_record["swapPartner"]["renameState"] = copy.deepcopy(rename_plan["partner"]["rename"])
            metadata.validate_catalog(updated)
        _repoint_workflow_photos(checked_plans, cfg)
        (save_fn or metadata.save_catalog)(updated)
    except (OSError, ValueError) as exc:
        workflow_failures = []
        if rename_completed:
            try:
                person_rename.change_files(rename_plan, reverse=True)
            except (OSError, ValueError) as restore_exc:
                workflow_failures.append(f"rename rollback failed: {restore_exc}")
        if workflow_attempted:
            try:
                _restore_workflow_photos(checked_plans, cfg)
            except (OSError, ValueError) as restore_exc:
                workflow_failures.append(f"workflow rollback failed: {restore_exc}")
        failures = _rollback_moves(completed, created_directories)
        failures.extend(workflow_failures)
        if failures:
            raise OSError(
                f"action apply failed ({exc}); rollback also failed: {'; '.join(failures)}; "
                f"verified backup: {backup}"
            ) from exc
        raise
    return batch_id, backup


def _safe_relative_path(root, relative):
    path = pathlib.PurePosixPath(relative)
    if (
        path.is_absolute()
        or ".." in path.parts
        or any(character in relative for character in ("\\", ":"))
    ):
        raise ValueError(f"unsafe action history path: {relative}")
    resolved = (pathlib.Path(root) / pathlib.Path(*path.parts)).resolve()
    try:
        resolved.relative_to(pathlib.Path(root).resolve())
    except ValueError as exc:
        raise ValueError(f"action history path escapes the photo-library root: {relative}") from exc
    return resolved


def plan_undo(catalog, root, batch_id=None, chosen_ids=(), cfg=None):
    """Plan undo of the newest non-undone action batch and detect later state changes."""
    action_records = catalog["actions"]
    undone = {
        action["undoes"]
        for action in action_records
        if action["type"] == "action-undone" and "undoes" in action
    }
    groups = {}
    for action in action_records:
        if action["type"] != "action-undone" and action.get("batchId"):
            groups.setdefault(action["batchId"], []).append(action)
    active_batches = [
        current_batch for current_batch, actions in groups.items()
        if any(action["id"] not in undone for action in actions)
    ]
    if not active_batches:
        return ["there is no applied action batch to undo"], None, []
    selected_batch = active_batches[-1]
    if batch_id and batch_id != selected_batch:
        return [f"only the newest active batch can be undone: {selected_batch}"], None, []
    batch_actions = groups[selected_batch]
    if any(action["id"] in undone for action in batch_actions):
        return [f"batch {selected_batch} was only partly undone; inspect the action history"], None, []

    simulated = copy.deepcopy(catalog)
    reverse_plans = []
    for action in reversed(batch_actions):
        if "beforeState" not in action or "afterState" not in action:
            return [f"action {action['id']} has no undo snapshot"], None, []
        if action["type"] == person_rename.ACTION:
            try:
                rename_plan = person_rename.undo_plan(simulated, action, root, cfg or {})
            except (OSError, ValueError) as exc:
                return [str(exc)], None, []
            person_rename.restore_catalog(simulated, action)
            reverse_plans.append({
                "actionRecord": action, "beforeState": action["beforeState"],
                "renamePlan": rename_plan,
            })
            continue
        if action["type"] in person_actions.PROTECTION_ACTIONS:
            try:
                person_actions.restore_action(simulated, action, root)
            except ValueError as exc:
                return [str(exc)], None, []
            reverse_plans.append({"actionRecord": action, "beforeState": action["beforeState"]})
            continue
        person_id = action.get("personId")
        photo_id = action["photoIds"][0]
        if action["source"] != action["destination"] and photo_id in chosen_ids:
            return [f"photo {photo_id} is selected by an active workflow and cannot be moved during undo"], None, []
        current_state = _catalog_state(simulated, person_id, photo_id)
        if current_state != action["afterState"]:
            return [f"catalogue state changed after action {action['id']}"], None, []
        source = _safe_relative_path(root, action["source"])
        destination = _safe_relative_path(root, action["destination"])
        if action.get("destinationPersonId"):
            target = simulated["people"].get(action["destinationPersonId"])
            expected_folder = pathlib.PurePosixPath(action["destination"]).parent.parent.as_posix()
            if not target or target["folder"] != expected_folder or target.get("mergedInto"):
                return [f"destination identity changed after action {action['id']}"], None, []
        workflow = None
        if action["type"] in WORKFLOW_ACTIONS:
            if cfg is None:
                return ["workflow-photo undo requires workspace configuration"], None, []
            configured = cfg.get("photos", {})
            hero_key = action.get("workflowHero")
            current_name = next(
                (name for hero, name in configured.items() if hero.casefold() == hero_key.casefold()),
                None,
            ) if isinstance(hero_key, str) else None
            if current_name != action.get("workflowPhotoAfter"):
                return [f"workflow photo for {hero_key} changed after action {action['id']}"], None, []
            old_path = _safe_relative_path(root, action.get("workflowSourceBefore", ""))
            new_path = _safe_relative_path(root, action.get("workflowSourceAfter", ""))
            if not old_path.is_file() or not new_path.is_file():
                return [f"workflow photo files needed to undo {action['id']} are missing"], None, []
            workflow = {
                "workflowHero": hero_key,
                "workflowPhotoBefore": current_name,
                "workflowPhotoAfter": action["workflowPhotoBefore"],
                "workflowBeforePath": new_path,
                "workflowAfterPath": old_path,
            }
        if action["source"] != action["destination"]:
            if not destination.is_file() or source.exists():
                return [f"cannot safely undo move {destination} -> {source}"], None, []
            if metadata.content_sha256(destination) != action["contentSha256"]:
                return [f"moved photo changed after action {action['id']}"], None, []
            reverse_plans.append({
                "source": destination,
                "destination": source,
                "action": {"contentSha256": action["contentSha256"]},
            })
        else:
            if not source.is_file() or metadata.content_sha256(source) != action["contentSha256"]:
                return [f"photo changed after action {action['id']}: {source}"], None, []

        before = action["beforeState"]
        if action["type"] in WORKFLOW_ACTIONS:
            if before["photo"] is None:
                simulated["photos"][photo_id] = {
                    "contentSha256": action["contentSha256"],
                    "protected": False,
                }
            else:
                simulated["photos"][photo_id] = copy.deepcopy(before["photo"])
        else:
            if before["person"] is None:
                after_person = action["afterState"]["person"]
                simulated["people"][person_id] = {
                    "id": person_id,
                    "displayName": after_person["displayName"],
                    "folder": after_person["folder"],
                    "folderHistory": [],
                    "identityAnchors": [],
                }
            else:
                simulated["people"][person_id] = copy.deepcopy(before["person"])
            if before["photo"] is None:
                simulated["photos"][photo_id] = {
                    "contentSha256": action["contentSha256"],
                    "protected": False,
                }
            else:
                simulated["photos"][photo_id] = copy.deepcopy(before["photo"])
        reverse_plans.append({
            "actionRecord": action,
            "beforeState": before,
            **({"workflow": workflow} if workflow else {}),
        })
    try:
        metadata.validate_catalog(simulated)
    except ValueError as exc:
        return [f"undo would create invalid catalogue state: {exc}"], None, []
    return [], selected_batch, reverse_plans


def undo_actions(catalog, root, cfg, pool_folder, *, batch_id=None, backup_fn=None, save_fn=None):
    """Back up and transactionally undo the newest action batch."""
    root = pathlib.Path(root).resolve()
    chosen_ids = selected_photo_ids(cfg)
    errors, selected_batch, reverse_plans = plan_undo(catalog, root, batch_id, chosen_ids, cfg)
    if errors:
        raise ValueError("cannot undo action batch:\n  " + "\n  ".join(errors))
    if any(
        item.get("actionRecord", {}).get("type") in WORKFLOW_ACTIONS
        for item in reverse_plans
    ):
        _require_configured_work_root(root, cfg)
    undo_batch_id = "batch_" + uuid.uuid4().hex
    catalog_guard = _catalog_guard(root, catalog)
    rename_plan = next((item["renamePlan"] for item in reverse_plans if "renamePlan" in item), None)
    backup = (
        backup_fn(root, cfg, undo_batch_id) if backup_fn else
        _create_action_backup(root, cfg, undo_batch_id, rename_plan=rename_plan, reverse=True)
    )
    _revalidate_catalog(catalog_guard, catalog)
    errors, checked_batch, checked_plans = plan_undo(
        catalog, root, selected_batch, chosen_ids, cfg
    )
    if errors or checked_batch != selected_batch:
        detail = "\n  ".join(errors) if errors else "latest action batch changed"
        raise ValueError(f"action state changed after backup; no undo applied:\n  {detail}")

    updated = copy.deepcopy(catalog)
    for item in checked_plans:
        if "actionRecord" not in item:
            continue
        action = item["actionRecord"]
        before = item["beforeState"]
        person_id = action.get("personId")
        photo_id = action["photoIds"][0] if action["photoIds"] else None
        if action["type"] == person_rename.ACTION:
            person_rename.restore_catalog(updated, action)
        elif action["type"] in person_actions.PROTECTION_ACTIONS:
            person_actions.restore_action(updated, action, root)
        elif action["type"] in WORKFLOW_ACTIONS:
            if before["photo"] is None:
                updated["photos"][photo_id] = {
                    "contentSha256": action["contentSha256"],
                    "protected": False,
                }
            else:
                updated["photos"][photo_id] = copy.deepcopy(before["photo"])
        else:
            if before["person"] is None:
                after_person = action["afterState"]["person"]
                updated["people"][person_id] = {
                    "id": person_id,
                    "displayName": after_person["displayName"],
                    "folder": after_person["folder"],
                    "folderHistory": [],
                    "identityAnchors": [],
                }
            else:
                updated["people"][person_id] = copy.deepcopy(before["person"])
            if before["photo"] is None:
                updated["photos"][photo_id] = {
                    "contentSha256": action["contentSha256"],
                    "protected": False,
                }
            else:
                updated["photos"][photo_id] = copy.deepcopy(before["photo"])
        undone_record = {
            "id": "action_" + uuid.uuid4().hex,
            "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "actor": "user",
            "type": "action-undone",
            "photoIds": action["photoIds"],
            "reason": f"undid action batch {selected_batch}",
            "undoes": action["id"],
        }
        if person_id:
            undone_record["personId"] = person_id
        updated["actions"].append(undone_record)
    metadata.validate_catalog(updated)

    file_plans = [item for item in checked_plans if "source" in item]
    completed, created_directories = _move_files(file_plans, root)
    workflow_attempted = any(item.get("workflow") for item in checked_plans)
    rename_plan = next((item["renamePlan"] for item in checked_plans if "renamePlan" in item), None)
    rename_completed = False
    try:
        if rename_plan:
            person_rename.change_files(rename_plan, reverse=True)
            rename_completed = True
        _repoint_workflow_photos(checked_plans, cfg)
        (save_fn or metadata.save_catalog)(updated)
    except (OSError, ValueError) as exc:
        workflow_failures = []
        if rename_completed:
            try:
                person_rename.change_files(rename_plan)
            except (OSError, ValueError) as restore_exc:
                workflow_failures.append(f"rename rollback failed: {restore_exc}")
        if workflow_attempted:
            try:
                _restore_workflow_photos(checked_plans, cfg)
            except (OSError, ValueError) as restore_exc:
                workflow_failures.append(f"workflow rollback failed: {restore_exc}")
        failures = _rollback_moves(completed, created_directories)
        failures.extend(workflow_failures)
        if failures:
            raise OSError(
                f"undo catalogue save failed ({exc}); rollback also failed: {'; '.join(failures)}; "
                f"verified backup: {backup}"
            ) from exc
        raise
    return undo_batch_id, backup, selected_batch


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "preview", "apply"):
        subparser = subparsers.add_parser(command, help=f"{command} a staged action manifest")
        subparser.add_argument("manifest", help="JSON file downloaded from the review gallery")
        subparser.add_argument("--root", help="photo library root (default: workspaces.json paths.workRoot)")
        if command == "apply":
            subparser.add_argument("--apply", action="store_true", help="create a verified backup and apply the manifest")
    undo_parser = subparsers.add_parser("undo", help="preview or undo the newest action batch")
    undo_parser.add_argument("batch_id", nargs="?", help="batch ID printed by apply (defaults to the newest active batch)")
    undo_parser.add_argument("--root", help="photo library root (default: workspaces.json paths.workRoot)")
    undo_parser.add_argument("--apply", action="store_true", help="create a verified backup and undo the batch")
    args = parser.parse_args(argv)

    try:
        cfg = likeness.cw.load_cfg()
        root = pathlib.Path(args.root) if args.root else pathlib.Path(likeness.cw.work_root(cfg))
        root = root.resolve()
        if (
            getattr(args, "apply", False) and likeness.is_sandbox_working_path(root)
            and not (root / ".likeness-library.json").is_file()
        ):
            raise ValueError("sandbox catalogue is not initialized; install a clean rebase before applying actions")
        catalog_path = metadata.path_for_root(root)
        catalog = metadata.load_catalog(catalog_path)
        save_catalog = lambda data: metadata.save_catalog(data, catalog_path)
        pool_folder = likeness.pool_home(likeness.settings(cfg))
        if args.command == "undo":
            chosen_ids = selected_photo_ids(cfg)
            errors, batch_id, undo_plans = plan_undo(
                catalog, root, args.batch_id, chosen_ids, cfg
            )
            if errors:
                print("invalid undo:")
                for error in errors:
                    print(f"  {error}")
                return 1
            print(f"undo batch {batch_id}: {sum('actionRecord' in item for item in undo_plans)} action(s)")
            for plan in undo_plans:
                if "renamePlan" in plan:
                    record = plan["actionRecord"]
                    if record.get("swapPartner"):
                        print("  restore both identities in the confirmed name swap:")
                    for member in (record, record["swapPartner"]) if record.get("swapPartner") else (record,):
                        print(f"  restore identity {member['personId']}: {member['destination']} -> {member['source']}; exact original history")
                if "source" in plan:
                    print(f"  move back: {plan['source']} -> {plan['destination']}")
                if plan.get("workflow"):
                    workflow = plan["workflow"]
                    print(
                        f"  restore workflow photo for {workflow['workflowHero']}: "
                        f"{workflow['workflowPhotoBefore']} -> {workflow['workflowPhotoAfter']}"
                    )
            if args.apply:
                undo_batch, backup, undone = undo_actions(
                    catalog, root, cfg, pool_folder, batch_id=batch_id, save_fn=save_catalog,
                )
                print(f"undid {undone}; undo record {undo_batch}; verified backup: {backup}")
            else:
                print("preview only; add --apply to create a verified backup and undo")
            return 0

        manifest = load_manifest(args.manifest)
        errors, plans = validate_manifest(
            manifest, root, catalog, pool_folder, selected_photo_ids(cfg), cfg
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("invalid manifest:")
        for error in errors:
            print(f"  {error}")
        return 1
    print(f"valid likeness action manifest: {len(plans)} action(s)")
    if args.command in ("preview", "apply"):
        print_preview(plans)
        if args.command == "preview":
            print("preview only; no files or catalogue data were changed")
        elif args.apply:
            try:
                batch_id, backup = apply_actions(
                    manifest, root, catalog, cfg, pool_folder, save_fn=save_catalog,
                )
            except (OSError, ValueError) as exc:
                print(f"apply failed: {exc}", file=sys.stderr)
                return 1
            print(f"applied batch {batch_id}; verified backup: {backup}")
            if any(plan["type"] == person_rename.ACTION for plan in plans):
                print("refresh the index and bin\\people-gallery.cmd with this root and saved cache/policy; "
                      "rename does not require matching or image normalization")
            else:
                print("run bin\\library.cmd to refresh derived gallery files and reports")
        else:
            print("preview only; add --apply to create a verified backup and apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
