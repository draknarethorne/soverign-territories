"""User-named identities (``Various/<Name>`` intake) recorded on likeness catalogue person records.

``likeness.py seed --apply`` marks each named person with ``namedIntake``. The marker
lives on the person record, so it follows category moves and, in Production's
git-tracked catalogue, survives Sandbox rebuilds. A SIMPLE rebase retains named
identities like Angels/Sisters unless ``--release-named-category`` forces a category.
"""
import datetime
import pathlib

import numpy as np

from . import identity_names, metadata, person_rename, sandbox

CAST = ("Angels", "Sisters")
FORCEABLE = ("Models", "Prospects", "Potentials")
PERSON_ROOTS = (*CAST, *FORCEABLE)


def catalogue_path(root):
    """The catalogue ``seed`` may write: never Production's from a Sandbox or universe Working."""
    path = metadata.path_for_root(root)
    if path == metadata.CATALOG_PATH and sandbox.is_sandbox_working_path(pathlib.Path(root)):
        return pathlib.Path(root) / ".likeness-library.json"
    return path


def mark(root, plans, *, now=None):
    """Mark seed destinations ``{"source": "Various/<Name>", "destination": "<Category>/<Name>"}``."""
    stamp = (now or datetime.datetime.now().astimezone()).isoformat(timespec="seconds")
    catalog = metadata.load_catalog(metadata.path_for_root(root))
    by_folder = {person["folder"]: person for person in catalog["people"].values() if not person.get("mergedInto")}
    marked = []
    for plan in plans:
        folder = plan["destination"]
        if folder.split("/", 1)[0] in CAST:
            continue
        person = by_folder.get(folder)
        if person is None:
            name = pathlib.PurePosixPath(folder).name
            person = {
                "id": metadata.new_person_id(), "displayName": name, "folder": folder,
                "folderHistory": [], "identityAnchors": [], "protected": False,
                "names": {"originalName": name, "currentName": name, "originalSource": "catalogue-registration"},
            }
            catalog["people"][person["id"]] = person
            by_folder[folder] = person
        person.setdefault("namedIntake", {"recordedAt": stamp, "sourceFolder": plan["source"]})
        marked.append(folder)
    path = catalogue_path(root)
    if marked:
        metadata.save_catalog(catalog, path)
    return path, marked


def named_folders(catalog, release_categories=()):
    """Current folders of named people, minus categories whose release was forced."""
    return {
        person["folder"] for person in catalog.get("people", {}).values()
        if person.get("namedIntake") and not person.get("mergedInto")
        and person["folder"].split("/", 1)[0] not in set(release_categories)
    }

def clear_match(vectors, centroids, policy):
    """Merge-rule test of a named folder against identity cores.

    vectors: centred, normalised face vectors of the folder's usable photos; centroids: {folder: core vector}.
    Returns {"decision": "match"|"no-match"|"too-few", "best": [score, folder] | None, "rival": ... | None}.
    """
    rules = policy["identityActions"]
    if len(vectors) < rules["autoMergeMinimumIndependentPhotos"]:
        return {"decision": "too-few", "best": None, "rival": None, "photos": len(vectors)}
    mean = np.mean(vectors, axis=0)
    centre = mean / (np.linalg.norm(mean) or 1.0)
    ranked = sorted(((round(float(centre @ core), 4), key) for key, core in centroids.items()), reverse=True)
    best = list(ranked[0]) if ranked else None
    rival = list(ranked[1]) if len(ranked) > 1 else None
    clear = (
        best is not None and best[0] >= rules["autoMergeMinimum"]
        and round(best[0] - (rival[0] if rival else -1.0), 4) >= rules["autoMergeMinimumMargin"]
    )
    return {"decision": "match" if clear else "no-match", "best": best, "rival": rival, "photos": len(vectors)}


def _active(catalog):
    return {pid: p for pid, p in catalog["people"].items() if not p.get("mergedInto")}


def _current(person, folder):
    return (identity_names.snapshot(person, folder) or {}).get("currentName") or person["displayName"]


def _manifest(row):
    stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    return {"manifestVersion": 1, "generatedAt": stamp, "source": "likeness-seed", "actions": [row]}


def plan_correction(root, catalog, cfg, folder, name, source, *, invent):
    """Plan the person-name correction for a named folder that clearly matched ``folder``.

    Returns {"kind": "already-named"|"rename"|"swap"|"generated"|"hold", "documents": [manifest, ...], ...}.
    ``invent(seed, taken)`` supplies a generated name for a displaced identity when a swap is unsafe.
    """
    root = pathlib.Path(root)
    people = _active(catalog)
    owner = [(pid, p) for pid, p in people.items() if p["folder"] == folder]
    if len(owner) != 1:
        return {"kind": "hold", "reason": f"{folder} is not one registered catalogue identity"}
    pid, person = owner[0]
    current = _current(person, root / folder)
    if current.casefold() == name.casefold():
        return {"kind": "already-named", "documents": [], "personId": pid}
    occupants = [
        (other_id, other) for other_id, other in people.items()
        if other_id != pid and name.casefold() in {
            _current(other, root / other["folder"]).casefold(), other["displayName"].casefold(),
            other["folder"].split("/")[-1].casefold(),
        }
    ]
    if len(occupants) > 1:
        return {"kind": "hold", "reason": f"the name {name} is held by several identities: "
                + ", ".join(sorted(other["folder"] for _, other in occupants))}
    row, why = person_rename.decision(root, folder, pid, person, cfg)
    if row is None:
        return {"kind": "hold", "reason": f"{folder} cannot be renamed: {why}"}
    row.update(newName=name, nameCorrection="named-intake", namedSource=source)
    result = {"personId": pid, "folder": folder, "previousName": current}
    if not occupants:
        return {**result, "kind": "rename", "documents": [_manifest(row)]}
    other_id, other = occupants[0]
    other_row, why = person_rename.decision(root, other["folder"], other_id, other, cfg)
    if other_row is None:
        return {"kind": "hold", "reason": f"{other['folder']} holds the name {name} and cannot be renamed: {why}"}
    old = identity_names.snapshot(person, root / folder) or {}
    swappable = (
        identity_names.is_full_person_name(current)
        and old.get("originalSource") not in (None, "unavailable", "generated")
        and other_row["expectedRecordedName"].casefold() == name.casefold()
    )
    result["displaced"] = {"personId": other_id, "folder": other["folder"]}
    if swappable:
        row["newName"] = other_row["expectedRecordedName"]
        row["swapConfirmed"] = True
        row["swapWith"] = {k: v for k, v in other_row.items() if k != "type"}
        return {**result, "kind": "swap", "documents": [_manifest(row)], "displacedName": current}
    taken = [p["folder"] for p in people.values()] + [_current(p, root / p["folder"]) for p in people.values()]
    generated = invent(other_id, taken)
    other_row.update(newName=generated, nameCorrection="generated")
    return {**result, "kind": "generated", "documents": [_manifest(other_row), _manifest(row)],
            "displacedName": generated}
