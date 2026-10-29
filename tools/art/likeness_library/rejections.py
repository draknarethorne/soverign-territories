"""Content-bound negative identity decisions shared by routing and execution."""
import pathlib
from typing import TypedDict


class CandidateState(TypedDict, total=False):
    rejectedPersonIds: list[str]
    rejectionMetadataStale: bool


def identity_ids(catalog, person_id):
    """Include identities that were explicitly merged into this active identity."""
    return {person_id} | {
        key for key, person in catalog["people"].items()
        if person.get("mergedInto") == person_id
    }


def candidate_state(catalog, photo_id, content_hash) -> CandidateState:
    record = catalog["photos"].get(photo_id, {})
    rejected = record.get("rejectedPersonIds", [])
    if rejected and record["contentSha256"] != content_hash:
        return {"rejectionMetadataStale": True}
    return {"rejectedPersonIds": list(rejected)}


def photo_state(catalog, photo) -> CandidateState:
    from . import metadata

    photo_id = metadata.photo_id_from_name(photo.name)
    if not catalog["photos"].get(photo_id, {}).get("rejectedPersonIds"):
        return {"rejectedPersonIds": []}
    return candidate_state(catalog, photo_id, metadata.content_sha256(photo.path))


def excluded_folders(rows, cores):
    rejected = {person_id for row in rows for person_id in row.get("rejectedPersonIds", [])}
    return {
        folder for folder, core in cores.items()
        if rejected.intersection(core.get("personIds", []))
    }


def require_destination(catalog, photo_id, content_hash, person_id):
    state = candidate_state(catalog, photo_id, content_hash)
    if state.get("rejectionMetadataStale"):
        raise ValueError(f"{photo_id}: rejected-identity metadata is stale; review changed photo bytes")
    if set(state.get("rejectedPersonIds", [])) & identity_ids(catalog, person_id):
        raise ValueError(f"{photo_id}: destination identity was explicitly rejected")


def folder_conflict(root, folder, catalog, target_id):
    """Include Review originals when checking a proposed whole-identity merge."""
    from . import metadata

    for bucket in ("gallery", "review"):
        directory = pathlib.Path(root) / folder / bucket
        if not directory.is_dir():
            continue
        for path in sorted(directory.iterdir()):
            photo_id = metadata.photo_id_from_name(path.name)
            if not path.is_file() or not catalog["photos"].get(photo_id, {}).get("rejectedPersonIds"):
                continue
            try:
                require_destination(catalog, photo_id, metadata.content_sha256(path), target_id)
            except ValueError as exc:
                return str(exc)
    return None


def require_legacy_moves(root, moves):
    """Old CLI matchers must not bypass decisions they do not understand."""
    from . import metadata

    catalog = metadata.load_catalog(metadata.path_for_root(root))
    for move in moves:
        photo_id = metadata.photo_id_from_name(move.photo.name)
        if catalog["photos"].get(photo_id, {}).get("rejectedPersonIds"):
            raise ValueError(
                f"{photo_id}: legacy likeness moves cannot process persistent identity rejections; "
                "use policy-driven reconcile or staged actions"
            )
