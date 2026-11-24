"""User-named identities (``Various/<Name>`` intake) recorded on likeness catalogue person records.

``likeness.py seed --apply`` marks each named person with ``namedIntake``. The marker
lives on the person record, so it follows category moves and, in Production's
git-tracked catalogue, survives Sandbox rebuilds. A SIMPLE rebase retains named
identities like Angels/Sisters unless ``--release-named-category`` forces a category.
"""
import datetime
import pathlib

from . import metadata, sandbox

CAST = ("Angels", "Sisters")
FORCEABLE = ("Models", "Prospects", "Potentials")


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
