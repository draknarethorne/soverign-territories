"""Verified, reversible execution boundary for shared reconciliation proposals."""
import datetime
import json
import pathlib
import uuid

from . import metadata
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


def validate_moves(root, moves):
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
                or relative.parts[-2] not in ("gallery", "review")
                or relative.parts[0] not in ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various")
            ):
                raise ValueError(f"unsafe reconciliation {name}: {value}")
            path = root.joinpath(*relative.parts)
            if path.resolve() != path:
                raise ValueError(f"reparse point in reconciliation path: {path}")
            paths.append(path)
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


def _validate_permissions(root, moves, policy, cfg):
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
        metadata.photo_id_from_name(name) for name in selected_names if isinstance(name, str)
    )
    protected_folders = {
        person["folder"] for person in catalog["people"].values() if person.get("protected")
    }
    for row in moves:
        if row["photoId"] in protected_ids:
            raise ValueError(f"protected or workflow-selected photo cannot move: {row['photoId']}")
        source = pathlib.PurePosixPath(row["source"]).parts
        destination = pathlib.PurePosixPath(row["destination"]).parts
        for parts in (source, destination):
            rules = policy["categoryPolicies"].get(parts[0], {})
            folder = "/".join(parts[:-2])
            if parts[-2] == "gallery" and (
                rules.get("identityProtectedByDefault") or folder in protected_folders
            ):
                raise ValueError(f"protected Gallery cannot change membership: {folder}")
        if destination[-2] == "gallery" and not policy["categoryPolicies"][destination[0]]["automaticPhotoRoutingEnabled"]:
            raise ValueError(f"automatic Gallery admission is disabled: {row['destination']}")
        if destination[-2] == "review" and destination[0] != "Various" and not policy["categoryPolicies"][destination[0]]["reviewAdmissionEnabled"]:
            raise ValueError(f"Review admission is disabled: {row['destination']}")
    return catalog


def _updated_catalog(catalog, moves, policy):
    updated = json.loads(json.dumps(catalog))
    people = {person["folder"]: person for person in updated["people"].values()}
    for row in moves:
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
        updated["photos"][row["photoId"]] = {
            "contentSha256": row["sha256"],
            "protected": updated["photos"].get(row["photoId"], {}).get("protected", False),
        }
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


def apply_moves(root, moves, policy, cfg, *, sandbox_override=False, backup_fn=None):
    require_authorization(root, policy, sandbox_override)
    root = pathlib.Path(root).resolve()
    if is_sandbox_working_path(root) and not (root / ".likeness-library.json").is_file():
        raise ValueError("sandbox catalogue is not initialized; install a clean rebase before maintenance")
    validate_moves(root, moves)
    catalog = _validate_permissions(root, moves, policy, cfg)
    if not moves:
        return None
    catalog_path = metadata.path_for_root(root)
    updated = _updated_catalog(catalog, moves, policy)
    backup = (backup_fn or _backup)(root, cfg)
    validate_moves(root, moves)
    if _validate_permissions(root, moves, policy, cfg) != catalog:
        raise ValueError("catalogue changed after backup; no reconciliation moves were applied")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    journal = root / "_reports" / "runs" / f"reconcile_{stamp}_{uuid.uuid4().hex[:8]}.json"
    journal.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schemaVersion": 1, "root": str(root), "policy": policy,
        "backup": str(backup), "status": "prepared", "moves": moves,
        "catalogBefore": catalog, "catalogAfter": updated,
        "catalogPath": str(catalog_path),
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
    validate_moves(root, reverse)
    if apply:
        (backup_fn or _backup)(root, cfg)
        validate_moves(root, reverse)
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
