"""User-named intake registry: identities the user created from ``Various/<Name>`` folders.

``likeness.py seed --apply`` records each named folder here; the SIMPLE rebase reads it
to apply the named-intake Review rules (near-miss and tie Review) and the cohesion report.
Entries are keyed by display name so a category move (Potential/Prospect) keeps them.
"""
import datetime
import json
import pathlib

FILE_NAME = "named-intake.json"
KIND = "likeness-named-intake"


def registry_path(root, cfg):
    try:
        from tools.workflows import comfy_workflows as cw
    except ImportError:  # likeness.py runs with tools/workflows on sys.path
        import comfy_workflows as cw

    return cw.storage_root(cfg, "likeness", root=pathlib.Path(root)) / FILE_NAME


def load(root, cfg):
    path = registry_path(root, cfg)
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("kind") != KIND or not isinstance(data.get("identities"), dict):
        raise ValueError(f"not a named-intake registry: {path}")
    return data["identities"]


def record(root, cfg, plans):
    """Merge ``{"source", "destination", "photos"}`` seed plans into the registry."""
    path = registry_path(root, cfg)
    identities = load(root, cfg)
    stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    for plan in plans:
        name = pathlib.PurePosixPath(plan["destination"]).name
        entry = identities.setdefault(name, {"firstRecordedAt": stamp, "photoCount": 0, "sources": []})
        entry["folder"] = plan["destination"]
        entry["photoCount"] += len(plan["photos"])
        entry["lastRecordedAt"] = stamp
        if plan["source"] not in entry["sources"]:
            entry["sources"].append(plan["source"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"kind": KIND, "schemaVersion": 1, "identities": identities}, indent=1) + "\n",
                    encoding="utf-8")
    return path


def named_folders(identities, folders):
    """Current identity folders whose display name was user-named."""
    return {folder for folder in folders if pathlib.PurePosixPath(folder).name in identities}
