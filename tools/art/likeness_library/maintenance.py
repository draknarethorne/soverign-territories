"""Verified, reversible execution boundary for shared reconciliation proposals."""
import datetime
import json
import pathlib
import uuid

from . import metadata, rejections
from .identity_maintenance import category_destination_available, relocated_path
from .sandbox import is_sandbox_working_path


def require_authorization(root, policy, sandbox_override=False):
    if sandbox_override and not is_sandbox_working_path(root):
        raise ValueError("draft-policy override is restricted to sandbox Working")
    if policy["status"] != "approved" and not sandbox_override:
        raise ValueError(
            "production reconciliation requires an approved policy; draft proposals remain preview-only"
        )


def proposed_moves(report, photos, root):
    """Resolve unique measured sources; a hold is not a new named identity."""
    root = pathlib.Path(root).resolve()
    by_id = {}
    for photo in photos:
        photo_id = metadata.photo_id_from_name(photo.name)
        by_id.setdefault(photo_id, []).append(photo)
    moves = []
    for row in report["assignments"] + report["held"]:
        if row.get("preserveStaged"):
            continue
        folder = row.get("destination")
        bucket = "gallery"
        if folder is None:
            destination = row.get("reviewDestination")
            if destination:
                folder, bucket = destination.rsplit("/", 1)
            elif row.get("clusterId"):
                if row["sourceBucket"] == "Review":
                    continue
                folder, bucket = "Various", "review"
            else:
                continue
        rows = by_id.get(row["photoId"], ())
        if len(rows) != 1:
            raise ValueError(f"cannot resolve a unique source for {row['photoId']}")
        photo = rows[0]
        source = photo.path.resolve()
        destination = root / folder / bucket / photo.name
        if source == destination:
            continue
        moves.append({
            "photoId": row["photoId"], "source": source.relative_to(root).as_posix(),
            "destination": destination.relative_to(root).as_posix(),
            "sha256": metadata.content_sha256(source), "reason": row["reason"],
        })
    validate_moves(root, moves)
    return moves


def validate_moves(root, moves, identity_actions=()):
    root = pathlib.Path(root).resolve()
    sources, destinations = set(), set()
    for row in moves:
        paths = []
        for name in ("source", "destination"):
            value = row[name]
            relative = pathlib.PurePosixPath(value)
            if (
                "\\" in value or ":" in value or relative.is_absolute()
                or len(relative.parts) < 3 or any(part in (".", "..", "") for part in value.split("/"))
                or (row.get("kind") != "identity-file" and relative.parts[-2] not in ("gallery", "review"))
                or relative.parts[0] not in ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various")
            ):
                raise ValueError(f"unsafe reconciliation {name}: {value}")
            path = root.joinpath(*relative.parts)
            if path.resolve() != path:
                raise ValueError(f"reparse point in reconciliation path: {path}")
            paths.append(path)
        if row.get("kind") == "identity-file" and not any(
            row.get("personId") == action["personId"]
            and (
                row["source"].startswith(action["sourceFolder"] + "/")
                and row["destination"] == relocated_path(action, row["source"])
                if not action.get("_undo") else
                row["destination"].startswith(action["sourceFolder"] + "/")
                and row["source"] == relocated_path(action, row["destination"])
            )
            for action in identity_actions
        ):
            raise ValueError("identity file move must belong to a validated folder transition")
        source, destination = paths
        source_key, destination_key = str(source).casefold(), str(destination).casefold()
        if source_key in sources or destination_key in destinations:
            raise ValueError("reconciliation repeats a source or destination")
        sources.add(source_key)
        destinations.add(destination_key)
        source_parts = pathlib.PurePosixPath(row["source"]).parts
        destination_parts = pathlib.PurePosixPath(row["destination"]).parts
        if (source_parts[0] == "Artists" or destination_parts[0] == "Artists") and (
            source_parts[:2] != destination_parts[:2]
        ):
            raise ValueError("reconciliation cannot move photos between artist sources or into the general library")
        if destination.exists():
            raise ValueError(f"reconciliation destination already exists: {destination}")
        if metadata.content_sha256(source) != row["sha256"]:
            raise ValueError(f"reconciliation source changed: {source}")


def _write(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _backup(root, cfg):
    import library_backup

    return library_backup.create_backup(
        root, cfg.get("paths", {}).get("inputsRoot"),
        metadata.ROOT / "workflows" / "workspaces.json", apply=True,
        extra_sources=[("likeness-catalogue", metadata.path_for_root(root))],
    )


def _validate_permissions(root, moves, policy, cfg, identity_actions=()):
    catalog = metadata.load_catalog(metadata.path_for_root(root))
    protected_ids = {
        photo_id for photo_id, record in catalog["photos"].items() if record["protected"]
    }
    protected_ids.update(
        photo_id for person in catalog["people"].values() for photo_id in person["identityAnchors"]
    )
    selected_names = list(cfg.get("photos", {}).values())
    for flow in cfg.get("flows", {}).values():
        selected_names.extend(flow.get("photos", {}).values())
    protected_ids.update(
        photo_id for name in selected_names if isinstance(name, str)
        if (photo_id := metadata.photo_id_from_name(name))
    )
    protected_folders = {
        person["folder"] for person in catalog["people"].values() if person.get("protected")
    }
    for row in moves:
        if row.get("photoId") in protected_ids:
            raise ValueError(f"protected or workflow-selected photo cannot move: {row['photoId']}")
        if row.get("photoId") and rejections.candidate_state(
            catalog, row["photoId"], row["sha256"],
        ).get("rejectionMetadataStale"):
            raise ValueError(f"{row['photoId']}: rejected-identity metadata is stale; review changed photo bytes")
        destination = pathlib.PurePosixPath(row["destination"]).parts
        if len(destination) >= 4 and destination[-2] in ("gallery", "review"):
            folder = "/".join(destination[:-2])
            target = next((person for person in catalog["people"].values() if person["folder"] == folder), None)
            if target and row.get("photoId"):
                rejections.require_destination(
                    catalog, row["photoId"], row["sha256"], target["id"],
                )
        if row.get("kind") == "identity-file":
            continue
        source = pathlib.PurePosixPath(row["source"]).parts
        destination = pathlib.PurePosixPath(row["destination"]).parts
        for parts in (source, destination):
            rules = policy["categoryPolicies"].get(parts[0], {})
            folder = "/".join(parts[:-2])
            if parts[-2] == "gallery" and (
                rules.get("identityProtectedByDefault") or folder in protected_folders
            ):
                raise ValueError(f"protected Gallery cannot change membership: {folder}")
        if (
            source[-2] == "gallery" and source[0] != "Various"
            and not policy["categoryPolicies"][source[0]]["automaticSplitEnabled"]
        ):
            raise ValueError(f"automatic Gallery removal is disabled: {row['source']}")
        if destination[-2] == "gallery" and not policy["categoryPolicies"][destination[0]]["automaticPhotoRoutingEnabled"]:
            raise ValueError(f"automatic Gallery admission is disabled: {row['destination']}")
        if destination[-2] == "review" and destination[0] != "Various" and not policy["categoryPolicies"][destination[0]]["reviewAdmissionEnabled"]:
            raise ValueError(f"Review admission is disabled: {row['destination']}")
    identity_folders = [
        action[key].casefold() for action in identity_actions
        for key in ("sourceFolder", "destinationFolder")
    ]
    if len(identity_folders) != len(set(identity_folders)):
        raise ValueError("identity actions must be disjoint; chains and cycles require a fresh plan")
    for action in identity_actions:
        person = catalog["people"].get(action["personId"])
        if not person or person["folder"] != action["sourceFolder"]:
            raise ValueError("identity transition no longer owns its source folder")
        if action.get("_undo") or action["type"] not in ("category-transition", "identity-merge"):
            raise ValueError("unsupported automatic identity action")
        for folder in (action["sourceFolder"], action["destinationFolder"]):
            parts = pathlib.PurePosixPath(folder).parts
            if (
                len(parts) != 2 or any(part in (".", "..") for part in parts)
                or "\\" in folder or ":" in folder
            ):
                raise ValueError("unsafe identity transition folder")
            rules = policy["categoryPolicies"].get(parts[0], {})
            if (
                not rules.get("automaticPhotoRoutingEnabled")
                or rules.get("identityProtectedByDefault") or person.get("protected")
                or person["identityAnchors"]
            ):
                raise ValueError("protected identity or anchors block automatic category transition")
        if action["type"] == "identity-merge":
            destination_person = catalog["people"].get(action["destinationPersonId"])
            if (
                not destination_person or destination_person["folder"] != action["destinationFolder"]
                or destination_person.get("protected") or destination_person["identityAnchors"]
                or not policy["categoryPolicies"][person["folder"].split("/")[0]]["automaticMergeEnabled"]
                or not policy["categoryPolicies"][destination_person["folder"].split("/")[0]]["automaticMergeEnabled"]
            ):
                raise ValueError("merge requires two current, unprotected identities with merge permission")
            conflict = (
                rejections.folder_conflict(root, person["folder"], catalog, destination_person["id"])
                or rejections.folder_conflict(root, destination_person["folder"], catalog, person["id"])
            )
            if conflict:
                raise ValueError(conflict)
            for current_person in (person, destination_person):
                rules = policy["categoryPolicies"][current_person["folder"].split("/")[0]]
                if action["score"] < rules["mergeMinimum"]:
                    raise ValueError("merge score no longer meets category policy")
            if min(action["independentSupport"]) < policy["identityActions"]["autoMergeMinimumIndependentPhotos"]:
                raise ValueError("merge lacks independent evidence")
            inventory = {}
            for path in (root / action["destinationFolder"]).rglob("*"):
                if path.is_symlink() or path.resolve() != path:
                    raise ValueError("reparse point in merge destination")
                if path.is_file():
                    inventory[path.relative_to(root).as_posix()] = metadata.content_sha256(path)
            if inventory != action["destinationInventory"]:
                raise ValueError("merge destination changed; replan from current evidence")
        elif (
            any(other["folder"] == action["destinationFolder"] for other in catalog["people"].values())
            or not category_destination_available(root, action["destinationFolder"])
        ):
            raise ValueError("identity transition destination already exists")
        current = set()
        for path in (root / action["sourceFolder"]).rglob("*"):
            if path.is_symlink() or path.resolve() != path:
                raise ValueError("reparse point in identity transition")
            if path.is_file():
                current.add(path.relative_to(root).as_posix())
                if metadata.photo_id_from_name(path.name) in protected_ids:
                    raise ValueError("protected photo blocks automatic category transition")
        planned = {
            row["source"] for row in moves
            if row["source"].startswith(action["sourceFolder"] + "/")
        }
        if not current or current != planned:
            raise ValueError("identity inventory changed; replan the category transition")
    return catalog


def _updated_catalog(catalog, moves, policy, identity_actions=()):
    updated = json.loads(json.dumps(catalog))
    for action in identity_actions:
        person = updated["people"][action["personId"]]
        if action["type"] == "identity-merge":
            for other in updated["people"].values():
                if other.get("mergedInto") == action["personId"]:
                    other["mergedInto"] = action["destinationPersonId"]
            person["mergedInto"] = action["destinationPersonId"]
        else:
            person["folderHistory"].append(person["folder"])
            person["folder"] = action["destinationFolder"]
    people = {person["folder"]: person for person in updated["people"].values()}
    for row in moves:
        if row.get("kind") == "identity-file":
            continue
        parts = pathlib.PurePosixPath(row["destination"]).parts
        if parts[0] != "Various":
            folder = "/".join(parts[:-2])
            if folder not in people:
                person_id = metadata.new_person_id()
                person = {
                    "id": person_id, "folder": folder, "displayName": parts[-3],
                    "folderHistory": [], "identityAnchors": [],
                    "protected": policy["categoryPolicies"][parts[0]]["identityProtectedByDefault"],
                }
                people[folder] = person
                updated["people"][person_id] = person
        photo_record = updated["photos"].setdefault(row["photoId"], {})
        photo_record.update({
            "contentSha256": row["sha256"],
            "protected": photo_record.get("protected", False),
        })
    metadata.validate_catalog(updated)
    return updated


def _rollback(completed, catalog, catalog_path):
    failures = []
    for source, destination in reversed(completed):
        try:
            destination.rename(source)
        except OSError as exc:
            failures.append(f"{destination} -> {source}: {exc}")
    try:
        metadata.save_catalog(catalog, catalog_path)
    except (OSError, ValueError) as exc:
        failures.append(f"catalogue restore: {exc}")
    return failures


def apply_moves(root, moves, policy, cfg, *, sandbox_override=False, backup_fn=None,
                identity_actions=()):
    require_authorization(root, policy, sandbox_override)
    root = pathlib.Path(root).resolve()
    if is_sandbox_working_path(root) and not (root / ".likeness-library.json").is_file():
        raise ValueError("sandbox catalogue is not initialized; install a clean rebase before maintenance")
    validate_moves(root, moves, identity_actions)
    catalog = _validate_permissions(root, moves, policy, cfg, identity_actions)
    if not moves:
        return None
    catalog_path = metadata.path_for_root(root)
    updated = _updated_catalog(catalog, moves, policy, identity_actions)
    backup = (backup_fn or _backup)(root, cfg)
    validate_moves(root, moves, identity_actions)
    if _validate_permissions(root, moves, policy, cfg, identity_actions) != catalog:
        raise ValueError("catalogue changed after backup; no reconciliation moves were applied")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    journal = root / "_reports" / "runs" / f"reconcile_{stamp}_{uuid.uuid4().hex[:8]}.json"
    journal.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schemaVersion": 1, "root": str(root), "policy": policy,
        "backup": str(backup), "status": "prepared", "moves": moves,
        "catalogBefore": catalog, "catalogAfter": updated,
        "catalogPath": str(catalog_path),
        "identityActions": list(identity_actions),
    }
    _write(journal, data)
    done = []
    try:
        for row in moves:
            source, destination = (root / row[key] for key in ("source", "destination"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.rename(destination)
            done.append((source, destination))
        metadata.save_catalog(updated, catalog_path)
        data["catalogAfterSHA256"] = metadata.content_sha256(catalog_path)
        data["status"] = "applied"
        _write(journal, data)
    except Exception as exc:
        failures = _rollback(done, catalog, catalog_path)
        data["status"] = "rollback-failed" if failures else "rolled-back"
        data["rollbackErrors"] = failures
        _write(journal, data)
        if failures:
            raise OSError(f"reconciliation failed: {exc}; rollback failed: {'; '.join(failures)}") from exc
        raise
    return journal


def undo_moves(root, journal, cfg, *, apply=False, backup_fn=None):
    root, journal = pathlib.Path(root).resolve(), pathlib.Path(journal).resolve()
    if root not in journal.parents:
        raise ValueError("reconciliation journal must be inside its library root")
    data = json.loads(journal.read_text(encoding="utf-8"))
    if data["root"] != str(root) or data["status"] != "applied":
        raise ValueError("only an applied reconciliation journal for this root can be undone")
    catalog_path = metadata.path_for_root(root)
    if str(catalog_path) != data["catalogPath"] or metadata.content_sha256(catalog_path) != data["catalogAfterSHA256"]:
        raise ValueError("catalogue changed after reconciliation; resolve later decisions before undo")
    reverse = [
        {**row, "source": row["destination"], "destination": row["source"]}
        for row in data["moves"]
    ]
    reverse_actions = [{**action, "_undo": True} for action in data.get("identityActions", [])]
    validate_moves(root, reverse, reverse_actions)
    if apply:
        (backup_fn or _backup)(root, cfg)
        validate_moves(root, reverse, reverse_actions)
        if (
            metadata.path_for_root(root) != catalog_path
            or metadata.content_sha256(catalog_path) != data["catalogAfterSHA256"]
        ):
            raise ValueError("catalogue changed after backup; no undo moves were applied")
        done = []
        try:
            for row in reverse:
                source, destination = (root / row[key] for key in ("source", "destination"))
                destination.parent.mkdir(parents=True, exist_ok=True)
                source.rename(destination)
                done.append((source, destination))
            metadata.save_catalog(data["catalogBefore"], catalog_path)
            data["status"] = "undone"
            _write(journal, data)
        except Exception as exc:
            failures = _rollback(done, data["catalogAfter"], catalog_path)
            if failures:
                data["status"], data["rollbackErrors"] = "undo-rollback-failed", failures
                _write(journal, data)
                raise OSError(f"undo failed: {exc}; rollback failed: {'; '.join(failures)}") from exc
            raise
    return reverse
