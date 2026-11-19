"""Immutable native generations; retire active claims without rewriting evidence."""
import html
import json
import pathlib
import shutil
import os
import re
from urllib.parse import quote

from . import metadata
from .normal_transaction import safe

INDEX = ".normal-history.json"


def retired(root, directory):
    path = pathlib.Path(directory) / INDEX
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("formatVersion") != 1 or not isinstance(data.get("entries"), dict):
        raise ValueError("unsupported normal native-history index")
    result = set()
    for entry in data["entries"].values():
        if not isinstance(entry, dict) or not isinstance(entry.get("generations"), list) or not isinstance(
            entry.get("retiredManifests"), dict,
        ):
            raise ValueError("malformed normal native-history entry")
        if metadata.content_sha256(safe(root, entry["current"])) != entry["currentSha256"]:
            raise ValueError("normal native-history current content binding changed")
        for generation in entry["generations"]:
            if metadata.content_sha256(safe(root, generation["native"])) != generation["sha256"]:
                raise ValueError("normal previous-native generation changed")
        for relative, checksum in entry["retiredManifests"].items():
            manifest = safe(root, relative)
            if pathlib.Path(directory).resolve() not in manifest.resolve().parents:
                raise ValueError("normal history cannot retire another owner's evidence")
            if metadata.content_sha256(manifest) != checksum:
                raise ValueError("normal retired manifest changed; old evidence was not re-bound")
            old = json.loads(manifest.read_text(encoding="utf-8"))
            for artifact in old.get("artifacts", []):
                if metadata.content_sha256(safe(root, artifact["path"])) != artifact["sha256"]:
                    raise ValueError("normal immutable previous preparation artifact changed")
            result.add(manifest)
        for view in entry.get("historyViews", {}).values():
            if metadata.content_sha256(safe(root, view["path"])) != view["sha256"]:
                raise ValueError("normal immutable historical alias view changed")
    return result


def stage(root, stage_root, moves):
    from . import retained_preparation as retained

    root, stage_root = pathlib.Path(root).resolve(), pathlib.Path(stage_root).resolve()
    indexes = {}
    for move in moves:
        target = safe(root, move["destination"])
        previous = target if target.is_file() else safe(root, move["source"])
        current = previous.relative_to(root).as_posix()
        claimed = retained.claims_photo(root, previous)
        if not claimed and previous == safe(root, move["source"]):
            continue
        if claimed and retained.verify_link(root, previous, move["photoId"]) is None:
            raise ValueError(f"normal update refuses invalid retained history: {current}")
        owner = previous.parent.parent.relative_to(root).as_posix()
        directory = retained._processing_prefix(root) + "/" + owner
        if directory not in indexes:
            index = safe(root, directory + "/" + INDEX)
            retired(root, index.parent)
            indexes[directory] = json.loads(index.read_text(encoding="utf-8")) if index.exists() else {
                "formatVersion": 1, "entries": {},
            }
        index = indexes[directory]
        key = next((key for key, value in index["entries"].items() if value.get("current") == current), current)
        entry = index["entries"].setdefault(key, {
            "generations": [], "retiredManifests": {},
        })
        checksum = metadata.content_sha256(previous)
        frozen = directory + "/normal-history/native-" + checksum[:16] + previous.suffix.lower()
        staged = safe(stage_root, frozen)
        staged.parent.mkdir(parents=True, exist_ok=True)
        if staged.exists() and metadata.content_sha256(staged) != checksum:
            raise ValueError("normal previous-native generation filename collision")
        shutil.copyfile(previous, staged)
        if metadata.content_sha256(staged) != checksum:
            raise OSError("normal previous-native freeze changed bytes")
        generation = {"native": frozen, "sha256": checksum}
        if generation not in entry["generations"]:
            entry["generations"].append(generation)
        for manifest in retained._manifests(root, current):
            old = retained._load(manifest)
            if old["current"] == current:
                relative = manifest.relative_to(root).as_posix()
                entry["retiredManifests"][relative] = metadata.content_sha256(manifest)
                view_relative = pathlib.PurePosixPath(old["detail"]).with_name(
                    "native-history.html",
                ).as_posix()
                text = safe(root, old["detail"]).read_text(encoding="utf-8")
                old_href = quote(os.path.relpath(previous, safe(root, old["detail"]).parent).replace(os.sep, "/"), safe="/._-")
                new_href = quote(os.path.relpath(safe(root, frozen), safe(root, view_relative).parent).replace(os.sep, "/"), safe="/._-")
                for delimiter in ('"', "'"):
                    text = text.replace(delimiter + old_href + delimiter, delimiter + new_href + delimiter)
                text = re.sub(
                    r"(<body[^>]*>)",
                    lambda match: match[1] + "<p><strong>Historical recipe snapshot:</strong> "
                    "former native aliases resolve to exact previous pixels, not today's native.</p>",
                    text, count=1,
                )
                view = safe(stage_root, view_relative)
                view.parent.mkdir(parents=True, exist_ok=True)
                view.write_text(text, encoding="utf-8")
                entry.setdefault("historyViews", {})[relative] = {
                    "path": view_relative, "sha256": metadata.content_sha256(view),
                }
        entry.update({
            "current": move["destination"],
            "currentSha256": metadata.content_sha256(safe(stage_root, move["destination"])),
            "photoId": move["photoId"],
        })
        prefix = safe(root, retained._processing_prefix(root))
        for other in prefix.rglob(INDEX) if prefix.exists() else ():
            other_directory = other.parent.relative_to(root).as_posix()
            if other_directory == directory:
                continue
            data = indexes.get(other_directory) or json.loads(other.read_text(encoding="utf-8"))
            affected = [value for value in data.get("entries", {}).values() if value.get("current") == current]
            if not affected:
                continue
            retired(root, other.parent)
            for value in affected:
                value["current"] = move["destination"]
                value["currentSha256"] = entry["currentSha256"]
            indexes[other_directory] = data
    for directory, data in indexes.items():
        target = safe(stage_root, directory + "/" + INDEX)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def render(root):
    from . import retained_preparation as retained

    prefix = safe(root, retained._processing_prefix(root))
    output = ["<!doctype html><html><head><meta charset='utf-8'><title>Native generations</title></head><body>",
              "<h1>Immutable native generations</h1><p>Previous pixels and evidence are retained, not re-bound to new content.</p>"]
    for index in sorted(prefix.rglob(INDEX)) if prefix.exists() else []:
        retired(root, index.parent)
        data = json.loads(index.read_text(encoding="utf-8"))
        for entry in data["entries"].values():
            output.append("<h2>" + html.escape(entry["photoId"]) + "</h2>")
            output.append('<a href="' + safe(root, entry["current"]).as_uri() + '">Current native</a>')
            for generation in entry["generations"]:
                output.append('<p><a href="' + safe(root, generation["native"]).as_uri() +
                              '">Exact previous native</a> ' + html.escape(generation["sha256"]) + "</p>")
            for relative in entry["retiredManifests"]:
                output.append('<a href="' + safe(root, relative).as_uri() + '">Immutable previous manifest</a> ')
                view = entry.get("historyViews", {}).get(relative)
                if view:
                    output.append('<a href="' + safe(root, view["path"]).as_uri() +
                                  '">Historical recipe / resolved previous-native aliases</a> ')
    return "\n".join(output + ["</body></html>"])
