"""Clean, cast-seeded sandbox rebuild with a saved plan and reversible installation."""
import collections
import copy
import csv
import datetime
import hashlib
import json
import pathlib
import shutil
import uuid

import numpy as np

from . import clean_preparation, metadata, rejections, sandbox
from .engine import Cache, Photo, Space
from .policy import effective_settings, load_policy
from .reconciliation import frozen_identity_cores, plan_reconciliation
from .sandbox import (
    RESET_CATEGORIES,
    _is_reparse_point,
    _source_files,
    require_sandbox_output,
    validate_sandbox,
)


def _write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    temporary.replace(path)


def _bind_preparation(rows, prepared_rows, output, api):
    for row in rows:
        prepared = prepared_rows[row["source"]]
        path = clean_preparation.selected_path(output, prepared)
        row["preparedPath"] = path.relative_to(output).as_posix()
        row["preparedSHA256"] = metadata.content_sha256(path)
        row["preparationOutcome"] = prepared["outcome"]
        row["preparationSource"] = prepared["source"]
        if row["preparedSHA256"] != row["sha256"]:
            row["destination"] = str(pathlib.PurePosixPath(row["destination"]).with_suffix(path.suffix))
        if row.get("photoId") and not row.get("retainedCast"):
            destination = pathlib.PurePosixPath(row["destination"])
            prefix = api.originals.prefix_of(destination.parent.parent.name)
            key = api.cw.photo_key(pathlib.PurePosixPath(row["source"]).name)
            row["destination"] = destination.with_name(prefix + "_" + key + destination.suffix).as_posix()
    counts = collections.Counter(row["destination"].casefold() for row in rows)
    for row in rows:
        destination = pathlib.PurePosixPath(row["destination"])
        if (
            counts[row["destination"].casefold()] > 1
            and row.get("photoId") is None
            and destination.parent.as_posix() == "Various/review"
            and row["reason"] == "missing stable photo ID; held in Review, excluded from clustering"
        ):
            token = uuid.uuid5(uuid.NAMESPACE_URL, f"clean-rebase-review:{row['source']}").hex
            row["destination"] = destination.with_name(
                f"{destination.stem}_held-{token}{destination.suffix}",
            ).as_posix()
            row["reason"] += "; filename disambiguated by immutable source path"
            print(f"clean rebase: preserving separate Review hold {row['source']} -> {row['destination']}",
                  flush=True)


def _curation_inventory(layout, catalog=None):
    """Freeze active Working inputs; unknown or missing decision-bearing inputs need review."""
    import image_preparation

    working = layout["working_root"]
    source_rows = clean_preparation.inventory(layout)
    source_ids = {
        metadata.photo_id_from_name(pathlib.PurePosixPath(relative).name)
        for relative in source_rows if not relative.startswith("Artists/")
    } - {None}
    source_hashes = collections.defaultdict(set)
    for relative, digest in source_rows.items():
        if not relative.startswith("Artists/"):
            photo_id = metadata.photo_id_from_name(pathlib.PurePosixPath(relative).name)
            if photo_id:
                source_hashes[photo_id].add(digest)
    current, seen = {}, set()
    current_paths = [
        path for path in image_preparation.inventory(working)
        if not path.relative_to(working).as_posix().startswith("Artists/")
    ]
    by_id = collections.defaultdict(list)
    for path in current_paths:
        photo_id = metadata.photo_id_from_name(path.name)
        if photo_id:
            by_id[photo_id].append(path)
    overlay_inputs = {
        record["current"]: record
        for record in layout.get("source_overlay_manifest", {}).get("currentVarious", [])
    }
    replaced_originals = {
        record["source"]: record["sha256"]
        for record in layout.get("source_overlay_manifest", {}).get("rawRecovery", [])
        if record["role"] == "immutable-original"
    }
    allowed_unbound = set()
    for photo_id, paths in by_id.items():
        if len(paths) < 2:
            continue
        expected_hashes = source_hashes.get(photo_id, set())
        if len(expected_hashes) > 1:
            raise ValueError(f"ambiguous immutable inputs share a current photo ID: {photo_id}")
        matching = [
            path for path in paths
            if expected_hashes and metadata.content_sha256(path) in expected_hashes
        ]
        if len(matching) == 1:
            replacement = overlay_inputs.get(matching[0].relative_to(working).as_posix(), {})
            target = replacement.get("target", "")
            original_hash = replaced_originals.get(target)
            original_matches = [
                path for path in paths
                if original_hash and metadata.content_sha256(path) == original_hash
            ]
            for path in paths:
                if path != matching[0]:
                    relative = path.relative_to(working).as_posix()
                    record = overlay_inputs.get(relative)
                    if (metadata.photo_id_from_name(pathlib.PurePosixPath(target).name) == photo_id
                            and replacement.get("photoId") == photo_id
                            and replacement.get("sha256") in expected_hashes
                            and original_matches == [path]):
                        continue
                    if not record or not record.get("sanitized"):
                        raise ValueError(f"duplicate current photo ID is not safely isolated: {relative}")
                    allowed_unbound.add(relative)
        elif len({metadata.content_sha256(path) for path in paths}) == 1:
            pass
        else:
            raise ValueError(f"ambiguous current photo ID has no byte-verified source match: {photo_id}")
    for path in current_paths:
        relative = path.relative_to(working).as_posix()
        photo_id = metadata.photo_id_from_name(path.name)
        if photo_id:
            if relative in allowed_unbound:
                pass
            elif photo_id not in source_ids:
                if relative in overlay_inputs:
                    current[relative] = metadata.content_sha256(path)
                    continue
                raise ValueError(f"current photo is outside immutable inputs; preserve it before rebuilding: {relative}")
            else:
                seen.add(photo_id)
        elif relative not in source_rows:
            raise ValueError(f"current photo lacks immutable continuity: {relative}")
        current[relative] = metadata.content_sha256(path)
    if catalog:
        missing = (set(catalog["photos"]) & source_ids) - seen
        if missing:
            raise ValueError(
                "catalogued immutable photos are absent from active Working inputs; "
                f"review retirement/missing-source decisions before rebuilding: {sorted(missing)}"
            )
    return current


def _current_various_overlay_rows(layout):
    """Map active Working Various images to immutable IDs without losing either byte version."""
    import image_preparation

    source_rows = clean_preparation.inventory(layout)
    source_ids = collections.defaultdict(list)
    source_paths = set(source_rows)
    for relative in source_rows:
        if relative.startswith("Artists/"):
            continue
        photo_id = metadata.photo_id_from_name(pathlib.PurePosixPath(relative).name)
        if photo_id:
            source_ids[photo_id].append(relative)

    current_paths = [
        path for path in image_preparation.inventory(layout["working_root"])
        if path.relative_to(layout["working_root"]).as_posix().startswith("Various/")
    ]
    current_ids = collections.defaultdict(list)
    current_without_id = []
    for path in current_paths:
        photo_id = metadata.photo_id_from_name(path.name)
        if photo_id:
            current_ids[photo_id].append(path)
        else:
            current_without_id.append(path)

    rows, assigned = [], {}

    def add(path, target, photo_id, *, aliases=(), sanitized=False):
        relative = path.relative_to(layout["working_root"]).as_posix()
        if target in assigned:
            raise ValueError(f"multiple current Various photos map to one immutable input: {target}")
        assigned[target] = relative
        rows.append({
            "current": relative,
            "target": target,
            "photoId": photo_id,
            "sha256": metadata.content_sha256(path),
            "aliases": [
                {"current": alias.relative_to(layout["working_root"]).as_posix(),
                 "sha256": metadata.content_sha256(alias)}
                for alias in aliases
            ],
            "sanitized": sanitized,
        })

    for photo_id, paths in sorted(current_ids.items()):
        paths = sorted(paths, key=lambda item: item.relative_to(layout["working_root"]).as_posix().casefold())
        immutable_matches = source_ids.get(photo_id, [])
        if len(immutable_matches) > 1:
            raise ValueError(f"current Various photo ID maps to multiple immutable inputs: {paths[0]}")
        if len(paths) == 1:
            relative = paths[0].relative_to(layout["working_root"]).as_posix()
            target = relative if relative in source_paths or not immutable_matches else immutable_matches[0]
            add(paths[0], target, photo_id)
            continue

        grouped = collections.defaultdict(list)
        for path in paths:
            grouped[metadata.content_sha256(path)].append(path)
        if len(grouped) == 1:
            selected = paths[0]
            aliases = paths[1:]
            relative = selected.relative_to(layout["working_root"]).as_posix()
            digest = next(iter(grouped))
            if immutable_matches and digest != layout["manifest_files"][immutable_matches[0]][1]:
                suffix = pathlib.Path(selected.name).suffix.lower()
                target = (pathlib.PurePosixPath(relative).parent
                          / f"incoming-{digest[:16]}{suffix}").as_posix()
                add(selected, target, None, aliases=aliases, sanitized=True)
            else:
                target = relative if relative in source_paths or not immutable_matches else immutable_matches[0]
                add(selected, target, photo_id, aliases=aliases)
            continue

        if immutable_matches:
            original_hash = layout["manifest_files"][immutable_matches[0]][1]
            originals = grouped.get(original_hash, [])
            if len(originals) != 1:
                raise ValueError(
                    f"duplicate current Various ID has no unique byte-verified immutable match: {photo_id}"
                )
            canonical = originals[0]
            add(canonical, immutable_matches[0], photo_id)
            for digest, duplicates in sorted(grouped.items()):
                if digest == original_hash:
                    continue
                selected, *aliases = duplicates
                relative = selected.relative_to(layout["working_root"]).as_posix()
                suffix = pathlib.Path(selected.name).suffix.lower()
                target = (pathlib.PurePosixPath(relative).parent
                          / f"incoming-{digest[:16]}{suffix}").as_posix()
                add(selected, target, None, aliases=aliases, sanitized=True)
            continue

        for digest, duplicates in sorted(grouped.items()):
            selected, *aliases = duplicates
            relative = selected.relative_to(layout["working_root"]).as_posix()
            suffix = pathlib.Path(selected.name).suffix.lower()
            target = (pathlib.PurePosixPath(relative).parent
                      / f"incoming-{digest[:16]}{suffix}").as_posix()
            add(selected, target, None, aliases=aliases, sanitized=True)

    for path in sorted(current_without_id, key=lambda item: item.relative_to(layout["working_root"]).as_posix().casefold()):
        relative = path.relative_to(layout["working_root"]).as_posix()
        add(path, relative, None)
    return source_rows, rows


def _verify_source_overlay(layout, run):
    """Validate a run-local overlay and its raw recovery copies before using it."""
    overlay = pathlib.Path(run) / "source-overlay"
    manifest_path = overlay / "overlay.json"
    if not manifest_path.is_file() or _is_reparse_point(manifest_path):
        raise ValueError(f"missing or unsafe source overlay receipt: {manifest_path}")
    if _is_reparse_point(overlay):
        raise ValueError(f"unsafe source overlay directory: {overlay}")
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    immutable_manifest = layout["sandbox_root"] / "source-manifest.json"
    if value.get("schemaVersion") != 1 or value.get("immutableManifestSHA256") != metadata.content_sha256(immutable_manifest):
        raise ValueError("source overlay does not bind to the verified immutable snapshot")
    inputs = value.get("inputs")
    if not isinstance(inputs, dict) or not inputs:
        raise ValueError("source overlay has no prepared input inventory")

    def verified_path(relative, label):
        sandbox._safe_source_path(relative)
        path = overlay.joinpath(*pathlib.PurePosixPath(relative).parts)
        for parent in (path, *path.parents):
            if parent == overlay.parent:
                break
            if _is_reparse_point(parent):
                raise ValueError(f"linked {label}: {parent}")
        return path

    expected = {}
    for relative, record in inputs.items():
        path = verified_path(relative, "source overlay input")
        if not path.is_file():
            raise ValueError(f"source overlay input is missing or linked: {relative}")
        digest = metadata.content_sha256(path)
        if digest != record.get("sha256") or path.stat().st_size != record.get("bytes"):
            raise ValueError(f"source overlay input changed: {relative}")
        expected[relative] = (record["bytes"], digest)
    for record in value.get("rawRecovery", []):
        relative = record["path"]
        path = verified_path(relative, "source overlay raw recovery copy")
        if not path.is_file():
            raise ValueError(f"source overlay raw recovery copy is missing or linked: {relative}")
        if metadata.content_sha256(path) != record["sha256"]:
            raise ValueError(f"source overlay raw recovery copy changed: {relative}")
    for record in value.get("sidecars", []):
        path = verified_path(record["path"], "source overlay sidecar")
        if not path.is_file() or metadata.content_sha256(path) != record["sha256"]:
            raise ValueError(f"source overlay sidecar changed: {record['path']}")
    layout = dict(layout)
    layout["source_root"] = overlay
    layout["manifest_files"] = expected
    layout["source_overlay_manifest"] = value
    layout["source_overlay_sha256"] = metadata.content_sha256(manifest_path)
    return layout


def _create_source_overlay(layout, run):
    """Stage immutable inputs plus current Various versions in a recoverable run-local tree."""
    overlay = pathlib.Path(run) / "source-overlay"
    if overlay.exists():
        raise ValueError("unfinished or existing source overlay; inspect it and use a new run")
    immutable_rows, current_rows = _current_various_overlay_rows(layout)
    overlay.mkdir(parents=True)
    raw_recovery = []
    input_records = {}
    for index, (relative, digest) in enumerate(immutable_rows.items(), start=1):
        source = layout["source_root"].joinpath(*pathlib.PurePosixPath(relative).parts)
        target = overlay.joinpath(*pathlib.PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if metadata.content_sha256(target) != digest:
            raise OSError(f"immutable source overlay copy checksum mismatch: {relative}")
        input_records[relative] = {"bytes": target.stat().st_size, "sha256": digest}
        if index % 250 == 0:
            print(f"source overlay: copied {index}/{len(immutable_rows)} immutable inputs", flush=True)

    for row in current_rows:
        current = layout["working_root"].joinpath(*pathlib.PurePosixPath(row["current"]).parts)
        target = overlay.joinpath(*pathlib.PurePosixPath(row["target"]).parts)
        baseline = immutable_rows.get(row["target"])
        baseline_hash = baseline
        if baseline_hash and baseline_hash != row["sha256"]:
            original = layout["source_root"].joinpath(*pathlib.PurePosixPath(row["target"]).parts)
            recovery = overlay / "recovery" / "immutable-originals" / pathlib.Path(row["target"])
            recovery.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, recovery)
            raw_recovery.append({
                "role": "immutable-original", "path": recovery.relative_to(overlay).as_posix(),
                "source": row["target"], "sha256": baseline_hash,
            })
        if not baseline_hash or baseline_hash != row["sha256"]:
            recovery = overlay / "recovery" / "working-various" / pathlib.Path(row["current"])
            recovery.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(current, recovery)
            if metadata.content_sha256(recovery) != row["sha256"]:
                raise OSError(f"Working Various recovery copy checksum mismatch: {row['current']}")
            raw_recovery.append({
                "role": "working-various", "path": recovery.relative_to(overlay).as_posix(),
                "source": row["current"], "sha256": row["sha256"],
            })
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(current, target)
            input_records[row["target"]] = {
                "bytes": target.stat().st_size, "sha256": row["sha256"],
            }
        for alias in row["aliases"]:
            alias_path = layout["working_root"].joinpath(*pathlib.PurePosixPath(alias["current"]).parts)
            recovery = overlay / "recovery" / "working-various" / pathlib.Path(alias["current"])
            recovery.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(alias_path, recovery)
            if metadata.content_sha256(recovery) != alias["sha256"]:
                raise OSError(f"Working Various duplicate recovery checksum mismatch: {alias['current']}")
            raw_recovery.append({
                "role": "working-various-duplicate", "path": recovery.relative_to(overlay).as_posix(),
                "source": alias["current"], "sha256": alias["sha256"],
            })

    # Retain identity-name sidecars needed by the existing reversible installer.
    sidecars = []
    folders = {pathlib.PurePosixPath(relative).parent for relative in immutable_rows}
    for folder in sorted(folders, key=lambda item: item.as_posix().casefold()):
        source_folder = layout["source_root"].joinpath(*folder.parts)
        for sidecar in source_folder.glob("z_*.txt"):
            relative = sidecar.relative_to(layout["source_root"]).as_posix()
            target = overlay.joinpath(*pathlib.PurePosixPath(relative).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sidecar, target)
            sidecars.append({"path": relative, "sha256": metadata.content_sha256(target)})

    value = {
        "schemaVersion": 1,
        "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "immutableManifestSHA256": metadata.content_sha256(layout["sandbox_root"] / "source-manifest.json"),
        "immutableInputCount": len(immutable_rows),
        "workingVariousCount": sum(1 + len(row["aliases"]) for row in current_rows),
        "replacementCount": sum(
            1 for row in current_rows
            if row["target"] in immutable_rows and immutable_rows[row["target"]] != row["sha256"]
        ),
        "newInputCount": sum(1 for row in current_rows if row["target"] not in immutable_rows),
        "inputs": input_records,
        "currentVarious": [
            {"current": row["current"], "target": row["target"], "sha256": row["sha256"],
             "photoId": row["photoId"], "sanitized": row["sanitized"]}
            for row in current_rows
        ] + [
            {"current": alias["current"], "target": row["target"], "sha256": alias["sha256"],
             "photoId": row["photoId"], "sanitized": row["sanitized"], "duplicateOf": row["current"]}
            for row in current_rows for alias in row["aliases"]
        ],
        "sidecars": sidecars,
        "rawRecovery": raw_recovery,
    }
    _write_json(overlay / "overlay.json", value)
    return _verify_source_overlay(layout, run)


def _decision_matches_input(record, source_hash, working, current):
    if record["contentSha256"] == source_hash:
        return True
    from . import retained_preparation

    link = retained_preparation.verify_link(working, current) if current else None
    return bool(link and link["currentSha256"] == record["contentSha256"]
                and link["sourceSha256"] == source_hash)


def _migrate_continuity(catalog, rows, working, images, *, current_inputs=None):
    """Reuse identities only after scoring, where their membership proves one-to-one continuity."""
    destinations = collections.defaultdict(set)
    owners = collections.defaultdict(set)
    membership = {}
    current_paths = collections.defaultdict(list)
    for relative in current_inputs or ():
        photo_id = metadata.photo_id_from_name(pathlib.PurePosixPath(relative).name)
        if photo_id:
            current_paths[photo_id].append(working / relative)
    for person_id, person in catalog["people"].items():
        for bucket in ("gallery", "review"):
            for path in images(working / person["folder"] / bucket):
                key = metadata.photo_id_from_name(path.name)
                if not key:
                    continue
                if key in membership:
                    raise ValueError(f"ambiguous current identity ownership: {key}")
                membership[key] = person["folder"]
                current_paths[key].append(path)
    for row in rows:
        previous = membership.get(row.get("photoId"), row["oldFolder"])
        if previous.split("/")[0] not in RESET_CATEGORIES:
            continue
        folder = str(pathlib.PurePosixPath(row["destination"]).parent.parent)
        destinations[previous].add(folder)
        owners[folder].add(previous)
    occupied = {person["folder"].casefold(): person_id
                for person_id, person in catalog["people"].items()}
    labels = {}
    for person_id, person in catalog["people"].items():
        folder = person["folder"]
        targets = destinations.get(folder, set())
        if len(targets) != 1 or folder.split("/")[0] not in RESET_CATEGORIES:
            continue
        target = next(iter(targets))
        if (len(owners[target]) == 1 and target.split("/")[0] in RESET_CATEGORIES
                and occupied.get(target.casefold(), person_id) != person_id
                and not any(existing.casefold() == folder.casefold() for existing in owners)):
            labels[target] = folder
            print(f"clean rebase: retaining stable identity label {folder}; "
                  f"historical label {target} belongs to another identity", flush=True)
    if labels:
        for row in rows:
            path = pathlib.PurePosixPath(row["destination"])
            folder = path.parent.parent.as_posix()
            if folder in labels:
                row["destination"] = (pathlib.PurePosixPath(labels[folder]) / path.parent.name / path.name).as_posix()
            if row.get("bestMatch") in labels:
                row["bestMatch"] = labels[row["bestMatch"]]
        destinations = {folder: {labels.get(target, target) for target in targets}
                        for folder, targets in destinations.items()}
        owners = collections.defaultdict(set)
        for folder, targets in destinations.items():
            for target in targets:
                owners[target].add(folder)
    for person_id, person in catalog["people"].items():
        folder = person["folder"]
        targets = destinations.get(folder, set())
        if not targets:
            continue
        has_decisions = bool(
            person.get("automaticProtectionOverride") or person.get("names") or person.get("family")
            or person.get("identityAnchors") or person.get("protected")
            or any(person_id in photo.get("rejectedPersonIds", []) for photo in catalog["photos"].values())
        )
        unique = len(targets) == 1 and len(owners[next(iter(targets))]) == 1
        target = next(iter(targets)) if unique else None
        if target and target.split("/")[0] in ("Various", "Angels", "Sisters"):
            unique = False
        if has_decisions and not unique:
            raise ValueError(f"identity decisions cannot migrate unambiguously after matching: {folder}")
        if unique and target != folder:
            if any(other["folder"].casefold() == target.casefold()
                   for other_id, other in catalog["people"].items() if other_id != person_id):
                raise ValueError(f"stable identity migration would collide: {folder} -> {target}")
            person["folderHistory"].append(folder)
            person["folder"] = target
    for row in rows:
        record = catalog["photos"].get(row.get("photoId"))
        if record:
            paths = current_paths.get(row["photoId"], [])
            if not _decision_matches_input(record, row["sha256"], working, None) and not any(
                _decision_matches_input(record, row["sha256"], working, path) for path in paths
            ):
                raise ValueError(f"photo decision bytes differ from immutable input: {row['source']}")
            record["contentSha256"] = row["preparedSHA256"]


def _named_routes(source, catalog, api):
    from . import seeded_folders

    seeds = seeded_folders.seeded_folders(source, api.originals.images)
    plans, held = seeded_folders.plan_seeded(
        seeds, [person["folder"] for person in catalog["people"].values() if not person.get("mergedInto")],
        rejected=lambda path: bool(catalog["photos"].get(
            metadata.photo_id_from_name(path.name), {}).get("rejectedPersonIds")),
    )
    routes = {}
    for plan in plans:
        destination = plan["destination"]
        for path, bucket in plan["photos"]:
            bucket = "review" if destination.startswith(("Angels/", "Sisters/")) else bucket
            routes[path.relative_to(source).as_posix()] = (
                f"{destination}/{bucket}/{path.name}", "Explicit named-person intake; not a face-match inference",
            )
        for path, reason in plan["skipped"]:
            routes[path.relative_to(source).as_posix()] = (f"Various/review/{path.name}", reason)
    for group in held:
        for name, folder, buckets in seeds:
            if name == group["name"]:
                for paths in buckets.values():
                    for path in paths:
                        routes[path.relative_to(source).as_posix()] = (
                            f"Various/review/{path.name}", group["reason"],
                        )
    return routes


def _verify_routes(plan, source):
    sources, destinations = set(), set()
    for row in plan["photos"]:
        relative = pathlib.PurePosixPath(row["source"])
        destination = pathlib.PurePosixPath(row["destination"])
        for path in (relative, destination):
            if (
                path.is_absolute() or len(path.parts) not in (3, 4)
                or any(p in ("..", ".") for p in path.parts)
                or ":" in str(path) or "\\" in str(path)
                or (
                    path.parts[0] == "Various"
                    and not (
                        len(path.parts) == 3 and path.parts[1] in ("gallery", "review")
                        or path == relative and len(path.parts) == 4
                        and path.parts[2] in ("gallery", "review")
                    )
                )
                or (
                    path.parts[0] != "Various" and (len(path.parts) != 4 or path.parts[2] not in ("gallery", "review"))
                )
            ):
                raise ValueError(f"unsafe rebase path: {path}")
        if relative.parts[0] not in (*RESET_CATEGORIES, "Various", "Angels", "Sisters"):
            raise ValueError(f"candidate outside generated categories: {relative}")
        if destination.parts[0] not in (*RESET_CATEGORIES, "Angels", "Sisters", "Various"):
            raise ValueError(f"invalid rebase destination: {destination}")
        retained_cast = (
            row.get("retainedCast") is True
            and relative.parts[0] in ("Angels", "Sisters")
            and relative.parent == destination.parent
            and relative.stem == destination.stem
        )
        if destination.parts[0] in ("Angels", "Sisters") and destination.parts[2] != "review" and not retained_cast:
            raise ValueError("cast candidates may only enter Review, never the cast core")
        if relative.parts[0] in ("Angels", "Sisters") and not retained_cast:
            raise ValueError("cast preparation cannot change cast membership")
        if row["source"] in sources or row["destination"].casefold() in destinations:
            raise ValueError("duplicate source or destination in clean rebase")
        sources.add(row["source"])
        destinations.add(row["destination"].casefold())
        path = source.joinpath(*relative.parts)
        if metadata.content_sha256(path) != row["sha256"]:
            raise ValueError(f"source changed since preview: {path}")


def create_plan(layout, run, policy, api, embedder=None, *, reuse_measurements=False, preparation=None):
    """Flatten source photos before building any non-cast identity references."""
    source = layout["source_root"]
    cache_path = run / "likeness-cache.json"
    if cache_path.exists() and not reuse_measurements:
        raise ValueError("clean rebase requires a new run directory and empty embedding cache")
    cfg = api.cw.load_cfg()
    catalog_path = metadata.path_for_root(layout["working_root"])
    source_catalog_hash = metadata.content_sha256(catalog_path)
    catalog = metadata.load_catalog(catalog_path)
    working_inputs = _curation_inventory(layout, catalog) if preparation else None
    if preparation is None and any(
        (person.get("automaticProtectionOverride") or person.get("names") or person.get("family"))
        and person["folder"].split("/")[0] in RESET_CATEGORIES
        for person in catalog["people"].values()
    ):
        raise ValueError(
            "clean rebuild cannot regenerate identities with manual protection overrides or name/family provenance; "
            "stable-ID migration is required before rebuilding"
        )
    rejected = {
        person_id for photo in catalog["photos"].values()
        for person_id in photo.get("rejectedPersonIds", [])
    }
    if preparation is None and any(
        catalog["people"][person_id]["folder"].split("/")[0] not in ("Angels", "Sisters")
        or catalog["people"][person_id].get("mergedInto")
        for person_id in rejected
    ):
        raise ValueError(
            "clean rebuild cannot regenerate identities with persistent non-cast rejections; "
            "stable-ID migration is required before rebuilding"
        )
    settings = effective_settings(cfg, policy)
    cache = Cache(cache_path)
    embed = embedder or api.Embedder()
    photos, records = [], {}
    prepared_rows = {row["source"]: row for row in preparation[1]["photos"]} if preparation else {}
    cast_rows = []
    manifest = layout["manifest_files"]
    if preparation:
        folders = {}
        for relative in prepared_rows:
            parts = pathlib.PurePosixPath(relative).parts
            if parts[0] == "Artists":
                continue
            folder = source.joinpath(*parts[:-2])
            name = "/".join(parts[1:-2]) or parts[0]
            folders[(parts[0], name, folder)] = None
        source_folders = sorted(folders, key=lambda item: str(item[2]).casefold())
    else:
        source_folders = api.cw.photo_folders(cfg, source)
    for group, name, folder in source_folders:
        category = group.split("/", 1)[0]
        if category not in (*RESET_CATEGORIES, "Angels", "Sisters", "Various"):
            continue
        buckets = ("gallery", "review") if preparation or category in (*RESET_CATEGORIES, "Various") else ("gallery",)
        for bucket in buckets:
            for path in api.originals.images(folder / bucket):
                relative = path.relative_to(source).as_posix()
                prepared = prepared_rows.get(relative)
                if preparation and prepared is None:
                    raise ValueError(f"missing preparation outcome: {relative}")
                analysis_path = clean_preparation.selected_path(preparation[0], prepared) if prepared else path
                digest = cache.sha(analysis_path)
                if digest not in cache.emb:
                    cache.emb[digest] = embed(analysis_path) or {"faces": -1}
                photo = Photo(path, group, name, digest, cache.emb[digest])
                photos.append(photo)
                if category in (*RESET_CATEGORIES, "Various"):
                    records[relative] = (photo, bucket, manifest[relative][1])
                elif preparation:
                    cast_rows.append({
                        "source": relative, "destination": relative, "oldFolder": photo.key,
                        "photoId": metadata.photo_id_from_name(path.name), "sha256": manifest[relative][1],
                        "retainedCast": True, "reason": "Cast membership retained; image prepared before analysis",
                    })
                if len(photos) % 25 == 0:
                    print(f"clean rebase: measured {len(photos)} photos", flush=True)
                    cache.save()
    cache.save()
    # Center once over the selected photo population, not the old folder centroids.
    cast_photos = [p for p in photos if p.group in ("Angels", "Sisters") and p.path.parent.name == "gallery"]
    usable = [p.raw for p in photos if p.usable(settings["minFace"])]
    if not usable:
        raise ValueError("clean rebase has no usable input faces")
    mean = np.mean(usable, axis=0)
    cache.centering_mean = mean.tolist()
    cache.centering_domain = "general"
    cache.save()
    for photo in photos:
        if photo.raw is not None:
            photo.vec = api.nz(photo.raw - mean)
    space = Space([], settings)
    space.photos = cast_photos
    space.by_key = collections.defaultdict(list)
    for photo in cast_photos:
        if photo.usable(settings["minFace"]):
            space.by_key[photo.key].append(photo)
    space.keys = sorted(space.by_key)
    catalog = metadata.with_configured_anchors(catalog, cfg, cast_photos)
    core_catalog = catalog
    if preparation:
        core_catalog = copy.deepcopy(catalog)
        current_paths = {
            metadata.photo_id_from_name(pathlib.PurePosixPath(relative).name): layout["working_root"] / relative
            for relative in working_inputs
        }
        for photo in photos:
            photo_id = metadata.photo_id_from_name(photo.name)
            record = core_catalog["photos"].get(photo_id)
            if record:
                source_hash = metadata.content_sha256(photo.path)
                if not _decision_matches_input(
                    record, source_hash, layout["working_root"], current_paths.get(photo_id),
                ):
                    raise ValueError(f"photo decision bytes differ from immutable input: {photo.path}")
                record["contentSha256"] = source_hash
    cores, _, diagnostics = frozen_identity_cores(
        space, core_catalog, photo_id_fn=metadata.photo_id_from_name,
        content_sha256_fn=metadata.content_sha256, policy=policy,
    )
    if not cores or any(not key.startswith(("Angels/", "Sisters/")) for key in cores):
        raise ValueError("clean rebuild must start with Angel/Sister cores only")
    selected = api.chosen_keys(cfg)
    protected_folders = {
        person["folder"] for person in catalog["people"].values() if person.get("protected")
    }
    candidates, by_id = [], {}
    preserved, unusable = [], []
    named = _named_routes(source, catalog, api) if preparation else {}
    for relative, (photo, bucket, sha256) in sorted(records.items()):
        photo_id = metadata.photo_id_from_name(photo.name)
        base = {
            "source": relative, "sha256": sha256, "photoId": photo_id,
            "oldFolder": photo.key,
        }
        if relative in named:
            destination, reason = named[relative]
            preserved.append({**base, "destination": destination, "reason": reason})
            continue
        protected = (
            api.cw.photo_key(photo.name) in selected
            or photo.key in protected_folders
            or catalog["photos"].get(photo_id, {}).get("protected", False)
        )
        if protected:
            preserved.append({
                **base, "destination": relative,
                "reason": "protected/workflow photo retained; excluded from candidate clustering",
            })
            continue
        if not photo_id:
            unusable.append({
                **base,
                "destination": f"Various/review/{photo.name}",
                "reason": "missing stable photo ID; held in Review, excluded from clustering",
            })
            continue
        if photo_id in by_id:
            raise ValueError(f"duplicate candidate photo ID: {relative}")
        by_id[photo_id] = base
        quality_reason = api.junk_reason(photo, settings) if hasattr(api, "junk_reason") else None
        if not photo.usable(settings["minFace"]) or quality_reason:
            unusable.append({
                **base,
                "destination": f"Various/review/{photo.name}",
                "reason": (
                    f"quality hold: {quality_reason}; excluded from matching"
                    if quality_reason else
                    "unusable face; held in Review, excluded from matching"
                ),
            })
            continue
        candidates.append({
            "photoId": photo_id, "sourceFolder": "Various", "sourceBucket": "Pool",
            "side": "Prospects", "vector": photo.vec,
            **rejections.photo_state(core_catalog, photo),
        })
    print(f"clean rebase: {len(cores)} cast-only cores; {len(candidates)} flattened candidates", flush=True)
    result = plan_reconciliation(
        candidates, cores, assign=settings["assign"], margin=settings["margin"],
        cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
        minimum_cluster=settings["minCluster"], cast_merge=settings["castMerge"],
        name_factory=lambda seed, taken: api.invent_name(seed, taken),
        policy=policy,
    )
    # Historical names are display provenance only, never matching evidence.
    cluster_names = {}
    taken = {row["oldFolder"].split("/", 1)[1].casefold() for row in preserved
             if "/" in row["oldFolder"]}
    for group in sorted(result["clusters"], key=lambda g: (-len(g["photoIds"]), g["clusterId"])):
        old_names = collections.Counter(
            by_id[photo_id]["oldFolder"].split("/", 1)[1] for photo_id in group["photoIds"]
            if by_id[photo_id]["oldFolder"].split("/")[0] in RESET_CATEGORIES
        )
        name = next(
            (name for name, _ in sorted(old_names.items(), key=lambda r: (-r[1], r[0].casefold()))
             if name.casefold() not in taken),
            None,
        )
        if name is None:
            name = api.invent_name(group["clusterId"], taken)
        taken.add(name.casefold())
        category = group["destination"].split("/", 1)[0]
        cluster_names[group["destination"]] = f"{category}/{name}"
    routed = list(preserved) + list(unusable)
    for row in result["assignments"]:
        base = by_id[row["photoId"]]
        destination = cluster_names.get(row["destination"], row["destination"])
        routed.append({
            **base, **row, "destination": f"{destination}/gallery/{pathlib.PurePosixPath(base['source']).name}",
        })
    for row in result["held"]:
        base = by_id[row["photoId"]]
        destination = row.get("reviewDestination")
        if not destination:
            destination = "Various/review"
        routed.append({
            **base, **row, "destination": f"{destination}/{pathlib.PurePosixPath(base['source']).name}",
        })
    vectors = {row["photoId"]: row["vector"] for row in candidates}
    for row in routed:
        if row.get("bestMatch") in cluster_names:
            row["bestMatch"] = cluster_names[row["bestMatch"]]
        vector = vectors.get(row.get("photoId"))
        if vector is None:
            continue
        ranked = sorted(
            ((float(vector @ core["vector"]), folder) for folder, core in cores.items()),
            key=lambda item: (-item[0], item[1].casefold()),
        )
        row["initialBestCast"] = ranked[0][1]
        row["initialBestCastScore"] = ranked[0][0]
        row["initialSecondCast"] = ranked[1][1] if len(ranked) > 1 else None
        row["initialCastMargin"] = ranked[0][0] - ranked[1][0] if len(ranked) > 1 else None
    if len(routed) != len(records):
        raise AssertionError("clean rebase did not account for every source candidate")
    routed += cast_rows
    if preparation:
        _bind_preparation(routed, prepared_rows, preparation[0], api)
        _migrate_continuity(
            catalog, routed, layout["working_root"], api.originals.images, current_inputs=working_inputs,
        )
    people_by_folder = {person["folder"]: person for person in catalog["people"].values()}
    folders = set(cores) | {
        "/".join(pathlib.PurePosixPath(row["destination"]).parts[:2])
        for row in routed if not row["destination"].startswith("Various/")
    }
    for folder in sorted(folders):
        if folder in people_by_folder:
            continue
        person_id = "person_" + uuid.uuid5(
            uuid.NAMESPACE_URL, f"likeness:{layout['source_root']}:{folder.casefold()}",
        ).hex
        category = folder.split("/", 1)[0]
        catalog["people"][person_id] = {
            "id": person_id, "folder": folder, "displayName": folder.split("/")[-1],
            "folderHistory": [], "identityAnchors": [],
            "protected": policy["categoryPolicies"][category]["identityProtectedByDefault"],
        }
    metadata.validate_catalog(catalog)
    destinations = {person["folder"]: person["id"] for person in catalog["people"].values()
                    if not person.get("mergedInto")}
    for row in routed:
        folder = pathlib.PurePosixPath(row["destination"]).parent.parent.as_posix()
        if folder in destinations:
            rejections.require_destination(
                catalog, row.get("photoId"), row.get("preparedSHA256", row["sha256"]), destinations[folder],
            )
    if metadata.content_sha256(metadata.path_for_root(layout["working_root"])) != source_catalog_hash:
        raise ValueError("source catalogue changed while preparing clean rebuild; regenerate preview")
    if preparation and _curation_inventory(layout) != working_inputs:
        raise ValueError("Working inputs changed while matching; regenerate preview")
    _write_json(run / "catalog.json", catalog)
    plan = {
        "schemaVersion": 1, "mode": "clean-cast-seeded-rebuild",
        "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sourceRoot": str(source), "workingRoot": str(layout["working_root"]),
        "sourceManifestSHA256": metadata.content_sha256(layout["sandbox_root"] / "source-manifest.json"),
        "sourceOverlaySHA256": layout.get("source_overlay_sha256"),
        "policy": policy, "settings": settings, "referenceFolders": sorted(cores),
        "embeddingCache": str(cache_path), "embeddingCacheStartedEmpty": True,
        "cacheMeasurementsReusedForReplan": reuse_measurements,
        "centeringMean": mean.tolist(), "candidateCount": len(records),
        "coreDiagnostics": diagnostics, "photos": sorted(routed, key=lambda r: r["source"]),
        "catalogSHA256": metadata.content_sha256(run / "catalog.json"),
        "sourceCatalogSHA256": source_catalog_hash,
        "implementationHashes": {
            name: metadata.content_sha256(pathlib.Path(__file__).with_name(name))
            for name in ("clean_rebase.py", "planner.py", "policy.py", "reconciliation.py", "audit.py", "engine.py", "rejections.py")
        },
        "status": "preview",
    }
    if preparation:
        plan["workingInputs"] = working_inputs
        plan["preparation"] = {
            "root": str(preparation[0]),
            "manifestSHA256": metadata.content_sha256(preparation[0] / "manifest.json"),
            "recipe": preparation[1]["recipe"],
            "inputCount": len(prepared_rows),
            "artistCount": sum(row["source"].startswith("Artists/") for row in prepared_rows.values()),
        }
        for name in ("clean_preparation.py", "retained_preparation.py", "derivatives.py", "metadata.py"):
            plan["implementationHashes"][name] = metadata.content_sha256(pathlib.Path(__file__).with_name(name))
    _verify_routes(plan, source)
    return plan


def _prior_external_files(working, plan):
    from . import derivatives, retained_preparation

    native = {
        relative: digest for relative, digest in plan["workingInputs"].items()
        if pathlib.PurePosixPath(relative).parts[0] in ("Angels", "Sisters")
    }
    files = dict(native)
    for relative in native:
        path = _publication_path(working, relative)
        if retained_preparation.crop_guard(working, path, metadata.photo_id_from_name(path.name)):
            files.update({
                row["path"]: row["sha256"] for row in retained_preparation.owned_files(working, path)
            })
    for relative in sorted({str(pathlib.PurePosixPath(path).parent.parent) for path in native}):
        folder = working / relative
        manifest = folder / derivatives.MANIFEST
        if not manifest.exists():
            continue
        for target, record in derivatives.load(folder)["entries"].items():
            source_relative = f"{relative}/{record['source']}"
            source = _publication_path(working, source_relative)
            if source_relative not in native:
                raise ValueError(f"stale or unaccounted external derivative source: {source}")
            framing = next((mode for mode in ("padded", "head", "chest")
                            if derivatives.relative_target(source, mode).as_posix() == target), None)
            if framing is None:
                raise ValueError(f"unknown external derivative target: {manifest}: {target}")
            output, checked = derivatives.verified(source, framing, record.get("box"))
            files[output.relative_to(working).as_posix()] = checked["sha256"]
        files[manifest.relative_to(working).as_posix()] = metadata.content_sha256(manifest)
    return files


def _category_inventory(working, categories):
    return {
        path.relative_to(working).as_posix(): metadata.content_sha256(path)
        for category in categories if (working / category).exists()
        for path in _source_files(working / category)
    }


def install_plan(layout, run, plan):
    """Stage and hash-check every candidate, retaining old categories for rollback."""
    import library_backup

    working, source = layout["working_root"], layout["source_root"]
    if plan.get("preparation") and _curation_inventory(layout) != plan["workingInputs"]:
        raise ValueError("Working inputs changed since matching preview; regenerate preview")
    current_catalog_path = metadata.path_for_root(working)
    if "sourceCatalogSHA256" in plan:
        if metadata.content_sha256(current_catalog_path) != plan["sourceCatalogSHA256"]:
            raise ValueError("source catalogue changed since clean rebuild preview; regenerate preview")
    elif any(
        photo.get("rejectedPersonIds")
        for photo in metadata.load_catalog(current_catalog_path)["photos"].values()
    ):
        raise ValueError("clean rebuild preview predates persistent rejections; regenerate preview")
    _verify_routes(plan, source)
    if plan["status"] != "preview":
        raise ValueError("this clean rebase plan has already been applied")
    for relative, (_, expected_hash) in layout["manifest_files"].items() if not plan.get("preparation") else ():
        parts = pathlib.PurePosixPath(relative).parts
        if parts[0] in ("Angels", "Sisters") and len(parts) > 2 and parts[2] == "gallery":
            path = working.joinpath(*parts)
            if not path.is_file() or metadata.content_sha256(path) != expected_hash:
                raise ValueError(f"Working cast reference differs from Source: {path}")
    library_backup.verify_backup(library_backup.latest_work_root_backup(working))
    staged, previous = run / "staged", run / "previous"
    if staged.exists() or previous.exists():
        raise ValueError("staging already exists; inspect the previous attempt before applying")
    local_catalog = working / ".likeness-library.json"
    previous_catalog = local_catalog.read_bytes() if local_catalog.exists() else None
    if "catalogSHA256" in plan:
        if metadata.content_sha256(run / "catalog.json") != plan["catalogSHA256"]:
            raise ValueError("prepared sandbox catalogue changed since preview")
        metadata.load_catalog(run / "catalog.json")
        plan["previousLocalCatalog"] = previous_catalog is not None
        if previous_catalog is not None:
            (run / "previous-catalog.json").write_bytes(previous_catalog)
    categories = (*RESET_CATEGORIES, "Various") if plan.get("preparation") else RESET_CATEGORIES
    for category in categories:
        path = working / category
        if _is_reparse_point(path):
            raise ValueError(f"unsafe generated-category target: {path}")
        if path.exists():
            list(_source_files(path))
    previous_category_files = _category_inventory(working, categories)
    previous_external_hashes = _prior_external_files(working, plan) if plan.get("preparation") else {}
    staged.mkdir()
    previous.mkdir()
    preparation_rows = {}
    if plan.get("preparation"):
        preparation, data = clean_preparation.verify(layout, run)
        if metadata.content_sha256(preparation / "manifest.json") != plan["preparation"]["manifestSHA256"]:
            raise ValueError("preparation evidence differs from matched preview")
        preparation_rows = {row["source"]: row for row in data["photos"]}
    for row in plan["photos"]:
        src = source.joinpath(*pathlib.PurePosixPath(row["source"]).parts)
        dest = staged.joinpath(*pathlib.PurePosixPath(row["destination"]).parts)
        if pathlib.PurePosixPath(row["destination"]).parts[0] not in categories:
            target = working.joinpath(*pathlib.PurePosixPath(row["destination"]).parts)
            if (target.exists() and row["destination"] not in previous_external_hashes
                    and not (row.get("retainedCast") and row["destination"] == row["source"])):
                raise ValueError(f"external Review target already exists: {target}")
            if target.parent.resolve() != target.parent:
                raise ValueError(f"unsafe external Review path: {target}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if plan.get("preparation"):
            prepared_row = preparation_rows[row["source"]]
            src = clean_preparation.selected_path(preparation, prepared_row)
        shutil.copy2(src, dest)
        if metadata.content_sha256(dest) != row.get("preparedSHA256", row["sha256"]):
            raise OSError(f"staged candidate checksum mismatch: {dest}")
        if plan.get("preparation"):
            from . import retained_preparation

            retained_preparation.stage_photo(
                staged, row["destination"], preparation, prepared_row, recipe=data["recipe"],
            )
    for category in RESET_CATEGORIES:
        for folder in sorted((staged / category).iterdir()) if (staged / category).exists() else ():
            gallery = folder / "gallery"
            gallery.mkdir(exist_ok=True)
            former_folders = sorted({
                row["oldFolder"] for row in plan["photos"]
                if pathlib.PurePosixPath(row["destination"]).parts[:2] == (category, folder.name)
                and row["oldFolder"].partition("/")[2] == folder.name
            })
            name_files = [
                path for former in former_folders
                for path in (source / pathlib.Path(former) / "gallery").glob("z_*.txt")
            ]
            if len(name_files) == 1:
                shutil.copy2(name_files[0], gallery / name_files[0].name)
                continue
            name_file = gallery / f"z_{folder.name.lower().replace(' ', '_')}.txt"
            name_file.write_text(
                f"name: {folder.name}\nClean sandbox rebuild; prior folders recorded in run.json\n",
                encoding="utf-8",
            )
    if plan.get("preparation"):
        from . import derivatives

        measured = json.loads((run / "likeness-cache.json").read_text(encoding="utf-8"))["emb"]
        for row in plan["photos"]:
            path = staged / row["destination"]
            face = measured.get(hashlib.sha1(path.read_bytes()).hexdigest(), {})
            if row["preparationOutcome"] == "unprocessable":
                print(f"DERIVATIVE HOLD: undecodable source retained without derivatives: {row['source']}")
                continue
            _, messages = derivatives.maintain(path, face.get("box"), face.get("px", 0), apply=True)
            for message in messages:
                print(f"DERIVATIVE: {message}")
        for row in plan["photos"]:
            retained_preparation.refresh_detail(
                staged, staged / row["destination"], include_gallery_navigation=True,
            )
        plan["publishedFiles"] = [
            {"path": path.relative_to(staged).as_posix(), "sha256": metadata.content_sha256(path)}
            for path in _source_files(staged)
        ]
    external_files = [
        {"path": path.relative_to(staged).as_posix(), "sha256": metadata.content_sha256(path)}
        for path in _source_files(staged)
        if path.relative_to(staged).parts[0] not in categories
    ]
    prior_external = sorted(previous_external_hashes)
    for item in external_files:
        path = working / item["path"]
        if path.exists() and item["path"] not in prior_external:
            raise ValueError(f"external retained artifact already exists: {path}")
        for ancestor in (path, *path.parents):
            if _is_reparse_point(ancestor):
                raise ValueError(f"linked external publication target: {ancestor}")
            if ancestor == working:
                break
    _verify_routes(plan, source)
    if "sourceCatalogSHA256" in plan and metadata.content_sha256(current_catalog_path) != plan["sourceCatalogSHA256"]:
        raise ValueError("source catalogue changed during staging; no rebuild installed")
    if plan.get("preparation") and _curation_inventory(layout) != plan["workingInputs"]:
        raise ValueError("Working inputs changed during staging; no rebuild installed")
    if _category_inventory(working, categories) != previous_category_files:
        raise ValueError("Working category files changed during staging; no rebuild installed")
    for relative, expected_hash in previous_external_hashes.items():
        if metadata.content_sha256(_publication_path(working, relative)) != expected_hash:
            raise ValueError(f"external files changed during staging; no rebuild installed: {relative}")
    moved, installed, cast_added, cast_saved = [], [], [], []
    try:
        for relative in prior_external:
            current, saved = working / relative, previous / "external" / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            current.rename(saved)
            cast_saved.append((current, saved))
        for category in categories:
            target = working / category
            if target.exists():
                target.rename(previous / category)
                moved.append(category)
            if (staged / category).exists():
                (staged / category).rename(target)
                installed.append(category)
        for item in external_files:
            path = pathlib.PurePosixPath(item["path"])
            src, dest = staged.joinpath(*path.parts), working.joinpath(*path.parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dest)
            cast_added.append((dest, src))
        for row in plan["photos"]:
            target = working.joinpath(*pathlib.PurePosixPath(row["destination"]).parts)
            if metadata.content_sha256(target) != row.get("preparedSHA256", row["sha256"]):
                raise OSError(f"installed candidate checksum mismatch: {target}")
        if "catalogSHA256" in plan:
            metadata.save_catalog(metadata.load_catalog(run / "catalog.json"), local_catalog)
            plan["installedCatalogSHA256"] = metadata.content_sha256(local_catalog)
        plan["status"] = "applied"
        plan["previousCategories"] = str(previous)
        plan["previousCategoryNames"] = moved
        plan["installedCategoryNames"] = list(categories)
        plan["externalFiles"] = external_files
        plan["previousExternalFiles"] = prior_external
        plan["previousExternalHashes"] = previous_external_hashes
        plan["previousCategoryFiles"] = previous_category_files
        _write_json(run / "run.json", plan)
    except Exception:
        if "catalogSHA256" in plan:
            _restore_catalog(local_catalog, previous_catalog)
        for dest, src in reversed(cast_added):
            dest.rename(src)
        for category in reversed(installed):
            (working / category).rename(staged / category)
        for category in reversed(moved):
            (previous / category).rename(working / category)
        for current, saved in reversed(cast_saved):
            saved.rename(current)
        raise


def _restore_catalog(path, data):
    if data is None:
        if path.exists():
            path.unlink()
    else:
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(data)
        temporary.replace(path)


def undo_plan(layout, run, plan):
    """Restore saved categories and withdraw only this run's verified cast additions."""
    if plan["status"] != "applied":
        raise ValueError("only an applied clean rebase can be undone")
    working = layout["working_root"]
    local_catalog = working / ".likeness-library.json"
    installed_catalog = None
    if "installedCatalogSHA256" in plan:
        if metadata.content_sha256(local_catalog) != plan["installedCatalogSHA256"]:
            raise ValueError("sandbox catalogue changed; review decisions before undoing this rebuild")
        installed_catalog = local_catalog.read_bytes()
        if plan["previousLocalCatalog"] and not (run / "previous-catalog.json").is_file():
            raise ValueError("previous sandbox catalogue is missing")
    previous, withdrawn = run / "previous", run / "withdrawn"
    if _is_reparse_point(previous) or not previous.is_dir():
        raise ValueError("verified prior categories are missing or unsafe")
    categories = tuple(plan.get("installedCategoryNames", RESET_CATEGORIES))
    if any(category not in (*RESET_CATEGORIES, "Various") for category in categories):
        raise ValueError("unsupported installed category in rebase journal")
    for category in plan["previousCategoryNames"]:
        if category not in categories or not (previous / category).is_dir():
            raise ValueError(f"prior category is missing: {category}")
    if withdrawn.exists():
        raise ValueError("withdrawn outputs already exist; inspect the prior undo")
    external_files = plan.get("externalFiles", [
        {"path": row["destination"], "sha256": row.get("preparedSHA256", row["sha256"])}
        for row in plan["photos"]
        if pathlib.PurePosixPath(row["destination"]).parts[0] not in categories
    ])
    for item in plan.get("publishedFiles", external_files):
        path = _publication_path(working, item["path"])
        if metadata.content_sha256(path) != item["sha256"]:
            raise ValueError(f"published rebuild output changed; cannot undo automatically: {path}")
    if plan.get("preparation"):
        _check_publication(working, plan)
    for relative in plan.get("previousExternalFiles", []):
        saved = previous / "external" / pathlib.Path(*_safe_journal_path(relative))
        expected = plan.get("previousExternalHashes", {}).get(relative)
        if expected is None:
            expected = next(row["sha256"] for row in plan["photos"] if row["source"] == relative)
        if metadata.content_sha256(saved) != expected:
            raise ValueError(f"previous cast input changed: {saved}")
    for relative, expected in plan.get("previousCategoryFiles", {}).items():
        saved = _publication_path(previous, relative)
        if metadata.content_sha256(saved) != expected:
            raise ValueError(f"previous category file changed: {saved}")
    for category in categories:
        for root in (working / category, previous / category):
            if root.exists():
                list(_source_files(root))
    withdrawn.mkdir()
    moved, restored, cast_moved, cast_restored = [], [], [], []
    try:
        for item in external_files:
            relative = pathlib.PurePosixPath(item["path"])
            source, target = working.joinpath(*relative.parts), withdrawn.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            source.rename(target)
            cast_moved.append((source, target))
        for relative in plan.get("previousExternalFiles", []):
            saved, current = previous / "external" / relative, working / relative
            current.parent.mkdir(parents=True, exist_ok=True)
            saved.rename(current)
            cast_restored.append((saved, current))
        for category in categories:
            if (working / category).exists():
                (working / category).rename(withdrawn / category)
                moved.append(category)
            if (previous / category).exists():
                (previous / category).rename(working / category)
                restored.append(category)
        if "installedCatalogSHA256" in plan:
            _restore_catalog(
                local_catalog,
                (run / "previous-catalog.json").read_bytes() if plan["previousLocalCatalog"] else None,
            )
        plan["status"] = "undone"
        _write_json(run / "run.json", plan)
    except Exception:
        if installed_catalog is not None:
            _restore_catalog(local_catalog, installed_catalog)
        for category in reversed(restored):
            (working / category).rename(previous / category)
        for category in reversed(moved):
            (withdrawn / category).rename(working / category)
        for saved, current in reversed(cast_restored):
            current.rename(saved)
        for source, target in reversed(cast_moved):
            target.rename(source)
        raise


def _safe_journal_path(relative):
    from .sandbox import _safe_source_path

    return _safe_source_path(relative)


def _publication_path(root, relative):
    path = root.joinpath(*_safe_journal_path(relative))
    for candidate in (path, *path.parents):
        if _is_reparse_point(candidate):
            raise ValueError(f"linked rebuild publication path: {candidate}")
        if candidate == root:
            break
    return path


def _check_publication(working, plan):
    outputs = plan.get("publishedFiles", [
        {"path": row["destination"], "sha256": row.get("preparedSHA256", row["sha256"])}
        for row in plan["photos"]
    ])
    for item in outputs:
        path = _publication_path(working, item["path"])
        if _is_reparse_point(path) or metadata.content_sha256(path) != item["sha256"]:
            raise ValueError(f"installed output changed: {path}")
    if plan.get("preparation"):
        import image_preparation

        categories = tuple(plan["installedCategoryNames"])
        expected = {item["path"]: item["sha256"] for item in outputs
                    if pathlib.PurePosixPath(item["path"]).parts[0] in categories}
        if _category_inventory(working, categories) != expected:
            raise ValueError("installed category inventory changed; review added/removed/edited files")
        cast = {
            path.relative_to(working).as_posix(): metadata.content_sha256(path)
            for path in image_preparation.inventory(working)
            if path.relative_to(working).parts[0] in ("Angels", "Sisters")
        }
        expected_cast = {row["destination"]: row.get("preparedSHA256", row["sha256"])
                         for row in plan["photos"] if row["destination"].startswith(("Angels/", "Sisters/"))}
        if cast != expected_cast:
            raise ValueError("installed cast inventory changed; review added/removed/edited photos")


def _refresh_galleries(working, run):
    import people_gallery
    from . import review_gallery

    shared = ["--root", str(working), "--cache", str(run / "likeness-cache.json"),
              "--policy", str(run / "policy.json"), "--no-renders"]
    for generate in (review_gallery.main, people_gallery.main):
        if generate(shared):
            raise ValueError("rebuild installed, but gallery refresh failed; retry --apply after resolving the diagnostic")


def command(args, api):
    if sum(bool(flag) for flag in (args.apply, args.check, args.dry_run, args.undo, args.replan)) > 1:
        raise ValueError("choose only one of --apply, --check, --dry-run, --undo, or --replan")
    policy = load_policy(args.policy)
    layout = validate_sandbox(args.root)
    run = require_sandbox_output(args.root, args.run_dir)
    if run == layout["working_root"] or any(
        run == layout["working_root"] / category
        or layout["working_root"] / category in run.parents
        for category in (*RESET_CATEGORIES, "Various", "Angels", "Sisters", "Artists")
    ):
        raise ValueError("run directory must be outside identity category roots")
    intake_only = getattr(args, "intake_only", False)
    include_various = getattr(args, "include_current_various", False)
    if intake_only and (args.undo or args.replan):
        raise ValueError("--intake-only cannot undo or replan matching")
    if args.dry_run:
        if include_various:
            rows, current = _current_various_overlay_rows(layout)
            total = len(set(rows) | {item["target"] for item in current})
            replaced = sum(1 for item in current if item["target"] in rows and rows[item["target"]] != item["sha256"])
            added = sum(1 for item in current if item["target"] not in rows)
            print(
                f"Clean-start preview: {len(rows)} immutable images plus {added} new current Various "
                f"images = {total} preparation outcomes; {replaced} immutable IDs use newer Working bytes."
            )
        else:
            rows = clean_preparation.inventory(layout)
            print(f"Clean-start preview: {len(rows)} immutable images will receive preparation outcomes.")
        print("No images, reports, caches or models changed. Existing cast membership stays retained.")
        print("Use --intake-only --apply to prepare and stop, or omit --dry-run for a full matched preview.")
        return {"status": "inventory", "inputCount": total if include_various else len(rows)}
    if intake_only and not (args.apply or args.check):
        if include_various:
            rows, current = _current_various_overlay_rows(layout)
            total = len(set(rows) | {item["target"] for item in current})
        else:
            rows = clean_preparation.inventory(layout)
            total = len(rows)
        print(f"Intake preview: {total} inputs; use --intake-only --apply to write sidecars.")
        return {"status": "inventory", "inputCount": total}
    if args.check or args.undo or args.replan:
        if not run.is_dir():
            raise ValueError("no saved clean-start run exists")
    else:
        run.mkdir(parents=True, exist_ok=True)
    overlay_path = run / "source-overlay"
    if overlay_path.exists():
        layout = _verify_source_overlay(layout, run)
    elif include_various and not (args.check or args.undo or args.replan):
        layout = _create_source_overlay(layout, run)
    plan_path = run / "run.json"
    if intake_only or args.check and not plan_path.exists():
        if args.check:
            output, data = clean_preparation.verify(layout, run)
        elif args.apply:
            output, data = clean_preparation.prepare(layout, run)
            from . import preparation_history

            preparation_history.publish_staged(layout["working_root"], layout["working_root"] / "_reports" / "library")
        print(f"Intake verified: {len(data['photos'])} outcomes. Review {output / 'index.html'}")
        print("Stopped before matching/assignment. The same run resumes without repeating preparation.")
        return {"status": "intake", "inputCount": len(data["photos"]), "report": str(output / "index.html")}
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if (
            plan["policy"] != policy and not (args.replan or args.undo or args.check)
        ) or plan["workingRoot"] != str(layout["working_root"]):
            raise ValueError("saved plan policy/root differs; use a new run directory")
        if plan["sourceManifestSHA256"] != metadata.content_sha256(layout["sandbox_root"] / "source-manifest.json"):
            raise ValueError("source manifest changed since preview")
        if plan.get("sourceOverlaySHA256") != layout.get("source_overlay_sha256"):
            raise ValueError("saved plan source overlay differs; use the same verified overlay")
        if args.replan:
            if (
                plan["status"] != "preview" or not plan["embeddingCacheStartedEmpty"]
                or plan["embeddingCache"] != str(run / "likeness-cache.json")
            ):
                raise ValueError("only a fresh-cache, unapplied preview can be replanned")
            _verify_routes(plan, layout["source_root"])
            original_preview = run / "initial-preview.json"
            if not original_preview.exists():
                _write_json(original_preview, plan)
            plan = create_plan(
                layout, run, policy, api, getattr(args, "embedder", None),
                reuse_measurements=True,
                preparation=clean_preparation.verify(layout, run) if plan.get("preparation") else None,
            )
            _write_json(plan_path, plan)
    else:
        if args.check or args.undo:
            raise ValueError("no saved clean rebase plan exists")
        if args.apply:
            raise ValueError("create and review the prepared matching preview before --apply")
        if args.replan and not ((run / "intake.json").is_file() and (run / "likeness-cache.json").is_file()):
            raise ValueError("resuming incomplete matching requires verified preparation and saved measurements")
        preparation = clean_preparation.prepare(layout, run)
        from . import preparation_history

        preparation_history.publish_staged(layout["working_root"], layout["working_root"] / "_reports" / "library")
        plan = create_plan(
            layout, run, policy, api, getattr(args, "embedder", None),
            reuse_measurements=args.replan, preparation=preparation,
        )
        _write_json(plan_path, plan)
    if plan.get("preparation"):
        output, _ = clean_preparation.verify(layout, run)
        if metadata.content_sha256(output / "manifest.json") != plan["preparation"]["manifestSHA256"]:
            raise ValueError("prepared inputs changed since matching; use a new run")
    elif args.apply:
        raise ValueError("matcher-only previews cannot be installed; create a new intake-aware run")
    _verify_routes(plan, layout["source_root"])
    if args.apply:
        if any(
            metadata.content_sha256(pathlib.Path(__file__).with_name(name)) != digest
            for name, digest in plan.get("implementationHashes", {}).items()
        ):
            raise ValueError("engine changed since preview; replan before applying")
        if plan["status"] == "applied":
            _check_publication(layout["working_root"], plan)
        else:
            install_plan(layout, run, plan)
        _write_json(run / "policy.json", plan["policy"])
        _refresh_galleries(layout["working_root"], run)
    if args.undo:
        undo_plan(layout, run, plan)
    if args.check and plan["status"] == "applied":
        _check_publication(layout["working_root"], plan)
    if not args.check:
        _write_json(run / "policy.json", plan["policy"])
        with (run / "photos.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            fields = (
                "source", "destination", "photoId", "sha256", "bestMatch", "bestScore",
                "score", "initialBestCast", "initialBestCastScore", "initialSecondCast",
                "initialCastMargin", "reason", "preparedSHA256", "preparedPath", "preparationOutcome",
            )
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(plan["photos"])
        summary = [
            "# Clean cast-seeded sandbox rebuild", "",
            f"Status: {plan['status']}", "",
            "All candidate photos were flattened before matching. Old names were used only after scoring.",
            f"Fresh embedding cache: {plan['embeddingCacheStartedEmpty']}",
            f"Initial reference identities: {len(plan['referenceFolders'])} (Angels/Sisters only)",
            f"Candidate photos accounted for: {plan['candidateCount']}",
            f"Policy: {plan['policy']['version']}",
            f"Candidate clustering minimum: {plan['policy']['identityActions']['identityClusterMinimumSimilarity']}",
            "",
            "Every source, destination, hash, match score, and reason is in photos.csv.",
            "The exact policy, centering mean, references, and per-photo decisions are in run.json.",
            "Review additions never enter an Angel/Sister gallery or identity core.",
            "Previous category directories are retained in previous/ after installation.",
            "",
            "## Initial reference folders", "",
        ] + [f"- {folder}" for folder in plan["referenceFolders"]]
        summary += [
            "", "## Effective thresholds", "",
            "| Rule | Value |", "| --- | --- |",
            *[
                f"| {name} display minimum | {plan['policy']['scoreBands'][name]['minimum']} |"
                for name in ("green", "yellow", "orange")
            ],
            f"| Red display band | <{plan['policy']['scoreBands']['red']['maximumExclusive']} |",
            f"| Small-group cast Review minimum | {plan['policy']['smallGroupCastReviewMinimum']} |",
            f"| High cast Review minimum | {plan['policy']['highCastSimilarityMinimum']} |",
            f"| Specific cast Review margin | {plan['policy']['photoRouting']['minimumMargin']} |",
            f"| Candidate clustering minimum | {plan['policy']['identityActions']['identityClusterMinimumSimilarity']} |",
            f"| Minimum initial cluster size | {plan['settings']['minCluster']} |",
            "", "## Actual destinations", "",
            "| Category / identity / bucket | Photos |", "| --- | ---: |",
        ] + [
            f"| {destination} | {count} |"
            for destination, count in sorted(collections.Counter(
                "/".join(pathlib.PurePosixPath(row["destination"]).parts[:3])
                for row in plan["photos"]
            ).items())
        ]
        for relative in (
            "diagnostics/diagnostics.md", "identity-core-audit.txt",
            "post-rebase-reconciliation.json",
        ):
            if (run / pathlib.Path(relative)).is_file():
                summary.append(f"\nPost-run evidence: [{relative}]({relative})")
        (run / "report.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    counts = collections.Counter(
        "/".join(pathlib.PurePosixPath(row["destination"]).parts[:3])
        for row in plan["photos"]
    )
    print(f"clean rebase {plan['status']}: {plan['candidateCount']} candidates; "
          f"{len(plan['referenceFolders'])} cast-only initial references")
    for destination, count in sorted(counts.items()):
        print(f"  {count:4} {destination}")
    print(f"per-photo audit and rollback locations: {plan_path}")
