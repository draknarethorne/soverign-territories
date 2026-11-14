"""Clean, cast-seeded sandbox rebuild with a saved plan and reversible installation."""
import collections
import copy
import csv
import datetime
import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import time
import uuid
from types import SimpleNamespace

import numpy as np

from . import (
    clean_preparation, family_tree, identity_names, metadata, protection, refinement, rejections, sandbox,
)
from .engine import Cache, Photo, Space
from .policy import effective_settings, load_policy, validate_policy
from .reconciliation import frozen_identity_cores, plan_reconciliation
from .sandbox import (
    RESET_CATEGORIES,
    _is_reparse_point,
    _source_files,
    require_sandbox_output,
    validate_sandbox,
)


def _implementation_path(name):
    module = pathlib.Path(__file__)
    return module.parent.parent / name if name == "likeness.py" else module.with_name(name)


def _verify_implementation_hashes(plan):
    hashes = plan.get("implementationHashes", {})
    if "likeness.py" not in hashes:
        raise ValueError("engine binding missing likeness.py; create a new preview")
    if any(metadata.content_sha256(_implementation_path(name)) != digest for name, digest in hashes.items()):
        raise ValueError("engine changed since preview; create a new preview")


def _write_json(path, value):
    if path.name == "run.json" and value.get("groupLifecycle"):
        payload = json.dumps(value, separators=(",", ":")).encode("utf-8")
    else:
        payload = json.dumps(value, indent=2).replace("\n", os.linesep).encode("utf-8")
    retention_root = None
    if path.name == "run.json" and isinstance(value.get("workingRoot"), str):
        working_root = pathlib.Path(value["workingRoot"])
        if sandbox.is_sandbox_working_path(working_root):
            from . import storage_retention

            if len(payload) > storage_retention.MAX_RUN_MANIFEST_BYTES:
                sections = {
                    key: len(json.dumps(item, separators=(",", ":")).encode("utf-8"))
                    for key, item in value.items()
                }
                for section in ("photos", "groupLifecycle", "finalMembershipAudit", "workflowSelection"):
                    item = value.get(section)
                    if isinstance(item, dict):
                        for key, child in item.items():
                            sections[f"{section}.{key}"] = len(
                                json.dumps(child, separators=(",", ":")).encode("utf-8"))
                    elif isinstance(item, list):
                        for key in {key for row in item for key in row}:
                            sections[f"{section}.{key}"] = sum(
                                len(json.dumps(row[key], separators=(",", ":")).encode("utf-8"))
                                for row in item if key in row)
                raise ValueError(
                    f"run manifest exceeds {storage_retention.MAX_RUN_MANIFEST_BYTES} bytes "
                    f"(actual {len(payload)}): {path}; section bytes: "
                    f"{json.dumps(dict(sorted(sections.items(), key=lambda item: -item[1])[:16]))}"
                )
            retention_root = working_root
    original = path.read_bytes() if retention_root is not None and path.exists() else None
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)
    if retention_root is not None:
        try:
            storage_retention.register_runs(
                retention_root, metadata.cw.load_cfg(), run_names=[path.parent.name],
            )
        except Exception:
            if original is None:
                path.unlink()
            else:
                temporary.write_bytes(original)
                temporary.replace(path)
            raise


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
            key = row["photoId"].removeprefix("photo:")
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


def _matching_photo_ids(photos, source, api, duplicates=None, digests=None):
    """Give every non-cast input a stable photo ID without renaming the frozen inputs.

    Download IDs in the name come first. Any other name gets the originals content ID
    (`pic_<sha1[:8]>`), the same ID `originals.py` assigns. A content-ID photo whose bytes
    equal a photo that already has an ID (else the copy outside Various, else the first path)
    gets no ID and is recorded in `duplicates` (relative -> canonical relative).
    `digests` (relative -> SHA-256) avoids re-reading files the manifest already hashed.
    """
    identifiers, inferred, by_content = {}, {}, {}
    by_relative = {}
    for photo in photos:
        relative = photo.path.relative_to(source).as_posix()
        by_relative[relative] = photo
        identifier = metadata.photo_id_from_name(photo.name)
        if identifier is None and photo.group not in ("Angels", "Sisters"):
            normalized = api.originals.standard_name(photo.name, "incoming")
            identifier = metadata.photo_id_from_name(normalized)
            if identifier:
                inferred[relative] = identifier
            else:
                by_content[relative] = f"photo:pic_{api.originals.content_id(photo.path)}"
        identifiers[relative] = identifier
    counts = collections.Counter(value for value in identifiers.values() if value)
    for relative, identifier in inferred.items():
        if counts[identifier] != 1:
            identifiers[relative] = None
    if not by_content:
        return identifiers
    known = dict(digests or {})

    def digest(relative):
        if relative not in known:
            known[relative] = metadata.content_sha256(by_relative[relative].path)
        return known[relative]

    def preference(relative):
        return relative.startswith("Various/"), relative.casefold()

    owners = {identifier for identifier in identifiers.values() if identifier}
    by_bytes = {}
    for relative in sorted((item for item, value in identifiers.items() if value), key=preference):
        by_bytes.setdefault(digest(relative), relative)
    for relative in sorted(by_content, key=preference):
        canonical = by_bytes.get(digest(relative))
        if canonical is not None:
            if duplicates is not None:
                duplicates[relative] = canonical
            continue
        if by_content[relative] in owners:
            raise ValueError(f"content-derived photo ID collision for different bytes: {relative}")
        identifiers[relative] = by_content[relative]
        owners.add(by_content[relative])
        by_bytes[digest(relative)] = relative
    return identifiers


def _curation_inventory(layout, catalog=None):
    """Freeze active Working inputs; unknown or missing decision-bearing inputs need review."""
    import image_preparation
    import originals

    working = layout["working_root"]
    if catalog is None:
        catalog = metadata.load_catalog(metadata.path_for_root(working))
    source_rows = clean_preparation.inventory(layout)
    source = layout["source_root"]
    source_photos = [
        SimpleNamespace(path=source / relative, name=pathlib.PurePosixPath(relative).name,
                        group=pathlib.PurePosixPath(relative).parts[0])
        for relative in source_rows if not relative.startswith("Artists/")
    ]
    source_identifiers = _matching_photo_ids(
        source_photos, source, SimpleNamespace(originals=originals), digests=source_rows,
    )
    source_ids = set(source_identifiers.values()) - {None}
    source_hashes = collections.defaultdict(set)
    for relative, digest in source_rows.items():
        if not relative.startswith("Artists/"):
            photo_id = source_identifiers.get(relative)
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
        elif len(matching) > 1:
            # Identical copies of the immutable input are one photo; anything else must be isolated.
            for path in paths:
                if path in matching:
                    continue
                relative = path.relative_to(working).as_posix()
                record = overlay_inputs.get(relative)
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
            alias = overlay_inputs.get(relative, {})
            if (not alias or alias.get("sha256") != source_rows.get(alias.get("target"))
                    or metadata.content_sha256(path) != alias["sha256"]):
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


def _working_baseline(layout):
    """Bind current assigned inputs without reviving historical Source-only photos."""
    import image_preparation

    working = layout["working_root"]
    records = {}
    for path in image_preparation.inventory(working):
        relative = path.relative_to(working).as_posix()
        if relative.startswith("Various/"):
            continue
        for parent in (path, *path.parents):
            if parent == working:
                break
            if _is_reparse_point(parent):
                raise ValueError(f"linked Working baseline input: {parent}")
        records[relative] = (path.stat().st_size, metadata.content_sha256(path))
    return {
        **layout,
        "source_root": working,
        "manifest_files": records,
    }, {relative: record[1] for relative, record in records.items()}


def _current_various_overlay_rows(layout, source_rows=None):
    """Map active Working Various images to immutable IDs without losing either byte version."""
    import image_preparation
    from tools.art import originals

    def input_id(name):
        return (metadata.photo_id_from_name(name)
                or metadata.photo_id_from_name(originals.standard_name(name, "incoming")))

    if source_rows is None:
        source_rows = clean_preparation.inventory(layout)
    source_ids = collections.defaultdict(list)
    source_paths = set(source_rows)
    for relative in source_rows:
        if relative.startswith("Artists/"):
            continue
        photo_id = input_id(pathlib.PurePosixPath(relative).name)
        if photo_id:
            source_ids[photo_id].append(relative)

    current_paths = [
        path for path in image_preparation.inventory(layout["working_root"])
        if path.relative_to(layout["working_root"]).as_posix().startswith("Various/")
    ]
    current_ids = collections.defaultdict(list)
    current_without_id = []
    for path in current_paths:
        photo_id = input_id(path.name)
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
            original_paths = grouped.get(original_hash, [])
            if len(original_paths) != 1:
                raise ValueError(
                    f"duplicate current Various ID has no unique byte-verified immutable match: {photo_id}"
                )
            canonical = original_paths[0]
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
    # Resolve exact incoming aliases against the final byte versions, not replaced baseline bytes.
    replacements = {row["target"]: row["sha256"] for row in rows}
    canonical = {}
    for relative, digest in sorted(source_rows.items(), key=lambda item: item[0].casefold()):
        if relative.startswith("Artists/") or replacements.get(relative, digest) != digest:
            continue
        canonical.setdefault(digest, relative)
    representatives = {}
    for row in sorted(rows, key=lambda item: (
            item["target"] not in source_rows, item["photoId"] is None, item["target"].casefold())):
        if len(pathlib.PurePosixPath(row["current"]).parts) > 3:
            representatives[row["target"]] = row
            continue
        replacement = row["target"] in source_rows and source_rows[row["target"]] != row["sha256"]
        target = row["target"] if replacement else canonical.setdefault(row["sha256"], row["target"])
        canonical.setdefault(row["sha256"], target)
        if target not in representatives:
            representatives[target] = {
                **row, "target": target,
                "photoId": (row["photoId"] if target == row["target"]
                            else input_id(pathlib.PurePosixPath(target).name)),
                "aliases": list(row["aliases"]),
            }
        else:
            representatives[target]["aliases"].extend([
                {"current": row["current"], "sha256": row["sha256"]}, *row["aliases"],
            ])
    return source_rows, list(representatives.values())


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


def _create_source_overlay(layout, run, *, current_working=False):
    from tools.art import temporary_storage
    from .report_assets import rename_directory
    overlay = pathlib.Path(run) / "source-overlay"
    if overlay.exists():
        raise ValueError("unfinished or existing source overlay; inspect it and use a new run")
    cfg = metadata.cw.load_cfg()
    temporary_root = metadata.cw.storage_root(cfg, "temporary", root=layout["working_root"])
    with temporary_storage.staging_directory(temporary_root, "source-overlay-") as stage:
        _build_source_overlay(layout, stage, current_working=current_working)
        rename_directory(stage, overlay)
    return _verify_source_overlay(layout, run)


def _build_source_overlay(layout, overlay, *, current_working=False):
    if current_working:
        layout, baseline_rows = _working_baseline(layout)
        immutable_rows, current_rows = _current_various_overlay_rows(layout, baseline_rows)
    else:
        immutable_rows, current_rows = _current_various_overlay_rows(layout)
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
            label = "Working baseline" if current_working else "immutable"
            print(f"source overlay: copied {index}/{len(immutable_rows)} {label} inputs", flush=True)

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
        "baselineMode": "working" if current_working else "source",
        "baselineInputCount": len(immutable_rows),
        "immutableInputCount": 0 if current_working else len(immutable_rows),
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


def _decision_matches_input(record, source_hash, working, current):
    if record["contentSha256"] == source_hash:
        return True
    from . import retained_preparation

    link = retained_preparation.verify_link(working, current) if current else None
    return bool(link and link["currentSha256"] == record["contentSha256"]
                and link["sourceSha256"] == source_hash)


def _identity_core_continuity_ids(person_id, person, catalog, photo_folders, *, enabled=False):
    """Return recipe-proven automatic core locks and all mandatory photo references."""
    automatic_core, mandatory = set(), set(person.get("identityAnchors", []))
    for photo_id, record in catalog.get("photos", {}).items():
        source = photo_folders.get(photo_id, {})
        if isinstance(source, str):
            source = {"folder": source}
        if source.get("folder", "").casefold() != person["folder"].casefold():
            continue
        provenance = record.get("protectionProvenance")
        core_ids = set(provenance.get("frozenCorePhotoIds", [])) if provenance else set()
        automatic = bool(
            enabled and record.get("protected") and provenance
            and provenance.get("recipeVersion") == "independent-gallery-loo-v1"
            and photo_id in core_ids
            and source.get("sha256") == record.get("contentSha256")
        )
        if automatic:
            automatic_core.add(photo_id)
        elif record.get("protected"):
            mandatory.add(photo_id)
    return automatic_core, mandatory


def _cluster_name_routes(clusters, by_id, catalog, source, api, minimum_cluster, cast_folders=(),
                         preserved=(), rebase_protection=False):
    """Choose display names from surviving, recorded identities after matching."""
    clusters = sorted(
        clusters, key=lambda group: (-len(group["photoIds"]), group.get("clusterId") or ""),
    )
    people_by_folder = collections.defaultdict(list)
    for person_id, person in catalog["people"].items():
        people_by_folder[person["folder"].casefold()].append((person_id, person))
    for folder, people in people_by_folder.items():
        if len(people) > 1:
            raise ValueError(f"multiple catalogue people claim {folder}")

    cluster_support = collections.defaultdict(collections.Counter)
    cluster_folders = []
    cluster_photo_ids = []
    photo_folders = {
        photo_id: {"folder": row["oldFolder"], "sha256": row.get("sha256")}
        for photo_id, row in by_id.items()
    }
    retained_mandatory = collections.defaultdict(set)
    for row in preserved:
        if ("protected/workflow photo retained" in row.get("reason", "")
                and row.get("oldFolder", "").split("/", 1)[0] in RESET_CATEGORIES):
            retained_mandatory[row["oldFolder"].casefold()].add(row.get("photoId"))
    for index, group in enumerate(clusters):
        support = collections.Counter()
        photo_ids = set(group["photoIds"])
        cluster_photo_ids.append(photo_ids)
        for photo_id in group["photoIds"]:
            folder = by_id[photo_id]["oldFolder"]
            if folder.split("/", 1)[0] in RESET_CATEGORIES:
                support[folder.casefold()] += 1
        cluster_folders.append(support)
        cluster_key = f"{index}:{group.get('clusterId') or group.get('destination', '')}"
        for folder, count in support.items():
            cluster_support[folder][cluster_key] += count

    cast_names = set()
    for folder in cast_folders:
        cast_names.add(folder.split("/", 1)[-1].casefold())
    for person in catalog["people"].values():
        if person["folder"].split("/", 1)[0] not in ("Angels", "Sisters"):
            continue
        cast_names.add(person["folder"].split("/", 1)[1].casefold())
        if person.get("displayName"):
            cast_names.add(person["displayName"].casefold())

    active_name_owners = collections.defaultdict(set)
    for person in catalog["people"].values():
        if person.get("mergedInto") or person["folder"].split("/", 1)[0] not in RESET_CATEGORIES:
            continue
        names = identity_names.rebase_snapshot(
            person, pathlib.Path(source) / pathlib.PurePosixPath(person["folder"]), catalog=catalog,
        )
        current_name = (names or {}).get("currentName")
        if identity_names.is_full_person_name(current_name):
            active_name_owners[" ".join(current_name.split()).casefold()].add(
                person["folder"].casefold()
            )

    taken = set(cast_names) | set(active_name_owners)
    for row in preserved:
        folder = row.get("oldFolder", "")
        if folder.split("/", 1)[0] in RESET_CATEGORIES:
            name = folder.split("/", 1)[-1]
            if identity_names.is_full_person_name(name):
                taken.add(" ".join(name.split()).casefold())

    names_by_destination, evidence_by_destination = {}, {}
    claimed = set()
    for index, group in enumerate(clusters):
        destination = group["destination"]
        category = destination.split("/", 1)[0]
        source_folders = cluster_folders[index]
        source_keys = set(source_folders)
        candidates, excluded = [], []
        for folder_key, support in sorted(source_folders.items()):
            folder = next(
                (by_id[photo_id]["oldFolder"] for photo_id in group["photoIds"]
                 if by_id[photo_id]["oldFolder"].casefold() == folder_key),
                folder_key,
            )
            people = people_by_folder.get(folder_key, [])
            person_id, person = people[0] if people else (None, {
                "folder": folder, "displayName": pathlib.PurePosixPath(folder).name,
            })
            if support < minimum_cluster:
                excluded.append({"folder": folder, "reason": "below minimum surviving core"})
                continue
            supports = cluster_support[folder_key]
            strongest = max(supports.values(), default=0)
            automatic_core_ids, mandatory_ids = _identity_core_continuity_ids(
                person_id, person, catalog, photo_folders, enabled=rebase_protection,
            )
            mandatory_ids.update(retained_mandatory[folder_key])
            preserves_core = bool(automatic_core_ids) and automatic_core_ids.issubset(
                cluster_photo_ids[index],
            )
            preserves_mandatory = mandatory_ids.issubset(cluster_photo_ids[index])
            retains_original_route = (
                preserves_core and preserves_mandatory
                if automatic_core_ids else
                support == strongest and sum(value == strongest for value in supports.values()) == 1
            )
            if not retains_original_route:
                excluded.append({"folder": folder, "reason": "original identity split or tied across clusters"})
                continue
            source_folder = pathlib.Path(source) / pathlib.PurePosixPath(folder)
            names = identity_names.rebase_snapshot(person, source_folder, catalog=catalog)
            if names and names.get("sourceNameConflict"):
                excluded.append({"folder": folder, "reason": "catalogue name conflicts with source record"})
                continue
            current_name = (names or {}).get("currentName")
            if not identity_names.is_full_person_name(current_name):
                excluded.append({"folder": folder, "reason": "no recorded first-and-last name"})
                continue
            current_name = " ".join(current_name.split())
            if current_name.casefold() in cast_names:
                excluded.append({"folder": folder, "reason": "name is reserved by a fixed cast slot"})
                continue
            other_owners = active_name_owners.get(current_name.casefold(), set()) - source_keys
            if other_owners:
                excluded.append({"folder": folder, "reason": "name belongs to another active identity"})
                continue
            age = identity_names.original_age(person_id, person, source_folder, catalog=catalog)
            candidates.append({
                "folder": folder, "personId": person_id, "supportPhotoCount": support,
                "name": current_name, "nameSource": (names or {}).get("originalSource", "unavailable"),
                "originalName": (names or {}).get("originalName"),
                "corePhotoIds": sorted(automatic_core_ids),
                "mandatoryPhotoIds": sorted(mandatory_ids),
                "preservesCore": preserves_core,
                "ageEvidence": age,
            })

        winner = None
        age_review = False
        if len(candidates) == 1:
            winner = candidates[0]
        elif len(candidates) > 1:
            ages = [candidate["ageEvidence"] for candidate in candidates]
            if all(age["status"] == "verified" for age in ages):
                oldest = min(age["date"] for age in ages)
                oldest_candidates = [
                    candidate for candidate in candidates
                    if candidate["ageEvidence"]["date"] == oldest
                ]
                if len(oldest_candidates) == 1:
                    winner = oldest_candidates[0]
                else:
                    age_review = True
            else:
                age_review = True

        if winner and winner["name"].casefold() not in claimed:
            name = winner["name"]
            reason = "retained original identity name"
            review_required = False
        else:
            name = api.invent_name(group.get("clusterId", destination), taken | claimed)
            if (not identity_names.is_full_person_name(name)
                    or name.casefold() in cast_names
                    or name.casefold() in taken
                    or name.casefold() in claimed):
                raise ValueError(f"generated non-character identity name is unsafe: {name!r}")
            reason = (
                "review original-name age evidence; generated collision-safe name"
                if age_review else "no sufficiently supported, collision-safe original name"
            )
            review_required = age_review or bool(candidates) or bool(excluded)
        if category in RESET_CATEGORIES and not identity_names.is_full_person_name(name):
            raise ValueError(f"non-character identity requires first and last names: {name!r}")
        claimed.add(name.casefold())
        names_by_destination[destination] = f"{category}/{name}"
        evidence_by_destination[destination] = {
            "name": name, "decision": reason, "reviewRequired": review_required,
            "originalCandidates": candidates, "excludedOriginals": excluded,
            "survivorPersonId": winner["personId"] if winner else None,
            "survivorFolder": winner["folder"] if winner else None,
        }
    return names_by_destination, evidence_by_destination


def _apply_family_tree(clusters, cluster_names, name_evidence, candidates, cores, catalog, source, policy,
                       preserved=(), api=None):
    """Give each score-band family one surname after membership and name continuity are final."""
    if not family_tree.settings(policy)["enabled"]:
        return None
    vectors = {row["photoId"]: row["vector"] for row in candidates}
    identities = {}
    for group in clusters:
        destination = group["destination"]
        category, _, name = cluster_names.get(destination, destination).partition("/")
        members = [vectors[photo_id] for photo_id in group["photoIds"] if photo_id in vectors]
        if category not in RESET_CATEGORIES or not members or not identity_names.is_full_person_name(name):
            continue
        evidence = name_evidence.get(destination, {})
        winner = next((
            candidate for candidate in evidence.get("originalCandidates", [])
            if candidate.get("personId") and candidate["personId"] == evidence.get("survivorPersonId")
        ), None)
        age = (winner or {}).get("ageEvidence") or {}
        identities[destination] = {
            "name": name, "vector": family_tree.centroid(members), "photoCount": len(group["photoIds"]),
            "ageDate": age.get("date") if age.get("status") == "verified" else None,
            "retained": evidence.get("decision") == "retained original identity name",
        }
    people = {
        person["folder"].casefold(): person for person in catalog["people"].values()
        if not person.get("mergedInto")
    }
    cast = {}
    for folder, core in cores.items():
        names = identity_names.rebase_snapshot(
            people.get(folder.casefold()), pathlib.Path(source) / pathlib.PurePosixPath(folder), catalog=catalog,
        )
        cast[folder] = {"vector": core["vector"], "personName": (names or {}).get("currentName")}
    reserved = {folder.split("/", 1)[-1] for folder in cores}
    reserved |= {
        person["folder"].split("/", 1)[-1] for person in catalog["people"].values()
        if person["folder"].split("/", 1)[0] in RESET_CATEGORIES
    }
    reserved |= {
        row.get("oldFolder", "").split("/", 1)[-1] for row in preserved
        if row.get("oldFolder", "").split("/", 1)[0] in RESET_CATEGORIES
    }
    reserved -= {identity["name"] for identity in identities.values()}
    renames, evidence = family_tree.plan(
        identities, cast, policy, reserved=reserved,
        surnames=getattr(api, "LAST", ()), first_names=getattr(api, "FIRST", ()),
    )
    for destination, name in sorted(renames.items()):
        category, _, before = cluster_names[destination].partition("/")
        record = name_evidence.setdefault(destination, {})
        record["nameBeforeFamily"] = before
        record["name"] = name
        cluster_names[destination] = f"{category}/{name}"
    folder_of = lambda key: cluster_names.get(key, key) if key else None
    for family in evidence["families"]:
        family["rootFolder"] = folder_of(family["root"])
        for member in family["members"]:
            member["folder"] = folder_of(member["identity"])
            member["parentFolder"] = folder_of(member["parent"])
            for step in member["path"]:
                step["fromFolder"], step["toFolder"] = folder_of(step["from"]), folder_of(step["to"])
            record = name_evidence.get(member["identity"])
            if record is not None:
                record["family"] = {
                    "id": family["id"], "surname": family["surname"], "root": family["rootFolder"],
                    "parent": member["parentFolder"], "score": member["score"], "band": member["band"],
                    "status": member["status"],
                }
    secondary = (
        f"secondary > {evidence.get('secondaryMinimumSimilarityExclusive', .35):.2f}"
        if evidence.get("secondarySurnameLinksEnabled", True)
        else "secondary surname links disabled"
    )
    print(
        f"clean rebase: family naming (direct cast >= {evidence['linkMinimum']:.2f}, "
        f"{secondary}): "
        f"{len(evidence['families'])} families, {evidence['linkedIdentityCount']} linked, "
        f"{evidence['renamedIdentityCount']} surname change(s), "
        f"{evidence['displacedFamilyCount']} given a fresh surname owned elsewhere",
        flush=True,
    )
    return evidence


def _record_families(catalog, evidence, cluster_names, name_evidence, source, policy, *, replace=False):
    """Write catalogue family/name records so galleries present the same families as the plan."""
    if not evidence:
        return
    previous_families = {}
    if replace:
        previous_families = {
            pid: person.pop("family") for pid, person in catalog["people"].items() if person.get("family")
        }
        evidence["previousCatalogueFamilies"] = copy.deepcopy(previous_families)
    people = {
        person["folder"].casefold(): person for person in catalog["people"].values()
        if not person.get("mergedInto")
    }
    recorded = 0
    for family in evidence["families"]:
        reference = people.get(family["rootFolder"].casefold())
        family["catalogueRecorded"] = False
        if reference is None:
            continue
        entries = []
        if family["rootKind"] == "cast":
            info = evidence["cast"].get(family["root"], {})
            names = identity_names.rebase_snapshot(
                reference, pathlib.Path(source) / pathlib.PurePosixPath(family["rootFolder"]), catalog=catalog,
            ) or {}
            if info.get("currentPersonName"):
                slot = family["rootFolder"].rsplit("/", 1)[-1]
                entries.append((reference, info.get("recordedPersonName") or slot, info["currentPersonName"], 1.0, {
                    "originalName": names.get("originalName") or info.get("recordedPersonName"),
                    "originalSource": (names.get("originalSource") or "recorded-history")
                    if (names.get("originalName") or info.get("recordedPersonName")) else "unavailable",
                }, "cast root"))
        for member in family["members"]:
            person = people.get((member["folder"] or "").casefold())
            if person is None:
                continue
            evidence_row = name_evidence.get(member["identity"], {})
            winner = next((
                candidate for candidate in evidence_row.get("originalCandidates", [])
                if candidate.get("personId") and candidate["personId"] == evidence_row.get("survivorPersonId")
            ), None)
            original = {
                "originalName": (winner or {}).get("originalName") or member["previousName"],
                "originalSource": (winner or {}).get("nameSource") or "catalogue-registration",
            }
            if replace and winner is None and person.get("names"):
                original = {
                    "originalName": person["names"]["originalName"],
                    "originalSource": person["names"]["originalSource"],
                }
            via = (f"{member['tier']} link to {member['parentFolder']} {member['score']:.3f} ({member['band']})"
                   if member["parent"] else "family root (oldest member)")
            entries.append((person, member["previousName"], member["name"],
                            member["score"] if member["score"] is not None else 1.0, original, via))
        for person, previous, current, score, original, via in entries:
            if original["originalSource"] not in (
                "recorded-history", "rename-history", "catalogue-registration",
            ):
                original = {"originalName": None, "originalSource": "unavailable"}
            person["names"] = {
                "originalName": original["originalName"], "currentName": current,
                "originalSource": original["originalSource"],
            }
            person["family"] = {
                "id": family["id"], "referencePersonId": reference["id"], "surname": family["surname"],
                "score": float(score), "policyVersion": policy["version"], "previousPersonName": previous,
                "reason": (f"Score-band family tree ({evidence['linkBand']} band or above): {via}; surname "
                           f"{family['surname']} from {family['surnameSource']}. Presentation only, not kinship "
                           "or same-person evidence."),
            }
            recorded += 1
        family["catalogueRecorded"] = True
    evidence["catalogueRecordCount"] = recorded
    if replace:
        evidence["catalogueReconciliation"] = [
            {
                "personId": pid, "previousFamily": previous,
                "currentFamily": copy.deepcopy(catalog["people"][pid].get("family")),
                "decision": "refreshed" if catalog["people"][pid].get("family") else "retired",
                "reason": "recomputed from final qualified references; prior creative family retained as run history",
            }
            for pid, previous in sorted(previous_families.items())
        ]


def _migrate_continuity(catalog, rows, working, images, *, current_inputs=None,
                        rebase_protection=False):
    """Reuse identities only for complete, scored continuity or name-proven merges."""
    destinations = collections.defaultdict(set)
    owners = collections.defaultdict(set)
    rows_by_owner = collections.defaultdict(list)
    membership = {}
    membership_ids = collections.defaultdict(set)
    current_paths = collections.defaultdict(list)
    photo_folders = {}
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
                membership_ids[person["folder"]].add(key)
                current_paths[key].append(path)
    for row in rows:
        previous = membership.get(row.get("photoId"), row["oldFolder"])
        if previous.split("/")[0] not in RESET_CATEGORIES:
            continue
        photo_folders[row.get("photoId")] = {
            "folder": previous, "sha256": row.get("sha256"),
        }
        folder = str(pathlib.PurePosixPath(row["destination"]).parent.parent)
        destinations[previous].add(folder)
        owners[folder].add(previous)
        rows_by_owner[previous].append(row)
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

    people_by_folder = collections.defaultdict(list)
    for person_id, person in catalog["people"].items():
        people_by_folder[person["folder"].casefold()].append((person_id, person))
    merge_plans = []
    merged_ids = set()
    continuity_by_person = {
        person_id: _identity_core_continuity_ids(
            person_id, person, catalog, photo_folders, enabled=rebase_protection,
        )
        for person_id, person in catalog["people"].items()
    }
    for person_id, person in catalog["people"].items():
        retained = {
            row.get("photoId") for row in rows_by_owner.get(person["folder"], ())
            if "protected/workflow photo retained" in row.get("reason", "")
        }
        continuity_by_person[person_id][1].update(retained)
    mandatory_target_by_person = {}
    for person_id, person in catalog["people"].items():
        folder = person["folder"]
        if folder.split("/")[0] not in RESET_CATEGORIES:
            continue
        automatic_core_ids, mandatory_ids = continuity_by_person[person_id]
        required_ids = automatic_core_ids | mandatory_ids
        if not required_ids:
            continue
        targets_by_id = {
            row.get("photoId"): pathlib.PurePosixPath(row["destination"]).parent.parent.as_posix()
            for row in rows_by_owner.get(folder, ())
        }
        missing = required_ids - targets_by_id.keys()
        if missing:
            raise ValueError(f"mandatory identity photos are missing after matching: {folder}")
        required_targets = {targets_by_id[photo_id].casefold() for photo_id in required_ids}
        if len(required_targets) != 1:
            raise ValueError(f"protected core or mandatory photos split across destinations: {folder}")
        mandatory_target_by_person[person_id] = next(
            targets_by_id[photo_id] for photo_id in required_ids
        )

    def split_core_target(person_id, folder):
        targets = destinations.get(folder, set())
        automatic_core_ids, _ = continuity_by_person[person_id]
        if len(targets) <= 1 or not automatic_core_ids or not rebase_protection:
            return None
        target = mandatory_target_by_person.get(person_id)
        if not target or target not in targets or len(owners[target]) != 1:
            return None
        target_rows = [
            row for row in rows_by_owner.get(folder, ())
            if pathlib.PurePosixPath(row["destination"]).parent.parent.as_posix().casefold()
            == target.casefold()
        ]
        for row in target_rows:
            rejections.require_destination(
                catalog, row.get("photoId"), row["sha256"], person_id,
            )
        evidences = [row.get("identityNameEvidence") for row in target_rows]
        if not evidences or any(not isinstance(value, dict) for value in evidences):
            return None
        evidence_key = json.dumps(evidences[0], sort_keys=True, ensure_ascii=False)
        if any(json.dumps(value, sort_keys=True, ensure_ascii=False) != evidence_key
               for value in evidences[1:]):
            return None
        evidence = evidences[0]
        candidate = next(
            (row for row in evidence.get("originalCandidates", [])
             if row.get("personId") == person_id and row.get("preservesCore") is True),
            None,
        )
        if (
            evidence.get("decision") != "retained original identity name"
            or evidence.get("reviewRequired")
            or evidence.get("survivorPersonId") != person_id
            or not candidate
            or evidence.get("name", "").casefold() != candidate.get("name", "").casefold()
            or target.split("/", 1)[-1].casefold() != evidence.get("name", "").casefold()
        ):
            return None
        return target

    def supported_name_candidate(person_id, folder, target):
        target_rows = [
            row for row in rows_by_owner.get(folder, ())
            if pathlib.PurePosixPath(row["destination"]).parent.parent.as_posix().casefold()
            == target.casefold()
        ]
        evidences = [row.get("identityNameEvidence") for row in target_rows]
        if not evidences or any(not isinstance(value, dict) for value in evidences):
            return None
        evidence_key = json.dumps(evidences[0], sort_keys=True, ensure_ascii=False)
        if any(json.dumps(value, sort_keys=True, ensure_ascii=False) != evidence_key
               for value in evidences[1:]):
            return None
        evidence = evidences[0]
        candidate = next(
            (row for row in evidence.get("originalCandidates", [])
             if row.get("personId") == person_id),
            None,
        )
        if (
            evidence.get("decision") != "retained original identity name"
            or evidence.get("reviewRequired")
            or evidence.get("survivorPersonId") != person_id
            or not candidate
            or evidence.get("name", "").casefold() != candidate.get("name", "").casefold()
            or target.split("/", 1)[-1].casefold() != evidence.get("name", "").casefold()
        ):
            return None
        return evidence, candidate

    for target, source_folders in owners.items():
        if len(source_folders) < 2 or target.split("/", 1)[0] not in RESET_CATEGORIES:
            continue
        if any(folder.split("/", 1)[0] not in RESET_CATEGORIES for folder in source_folders):
            continue
        member_records = []
        for folder in sorted(source_folders, key=str.casefold):
            matches = people_by_folder.get(folder.casefold(), [])
            if len(matches) != 1 or matches[0][1].get("mergedInto"):
                member_records = []
                break
            person_id, person = matches[0]
            routed_ids = {row.get("photoId") for row in rows_by_owner.get(folder, ())}
            automatic_core_ids, mandatory_ids = continuity_by_person[person_id]
            required_ids = automatic_core_ids | mandatory_ids
            target_ids = {
                row.get("photoId") for row in rows_by_owner.get(folder, ())
                if pathlib.PurePosixPath(row["destination"]).parent.parent.as_posix().casefold()
                == target.casefold()
            }
            if required_ids:
                if mandatory_target_by_person.get(person_id, "").casefold() != target.casefold():
                    member_records = []
                    break
                if not required_ids.issubset(target_ids):
                    member_records = []
                    break
            if not automatic_core_ids and (
                  destinations.get(folder) != {target}
                  or not membership_ids.get(folder, set()).issubset(routed_ids)):
                member_records = []
                break
            member_records.append((person_id, person, folder))
        if len(member_records) != len(source_folders):
            continue
        target_rows = [
            row for folder in source_folders for row in rows_by_owner.get(folder, ())
            if pathlib.PurePosixPath(row["destination"]).parent.parent.as_posix().casefold()
            == target.casefold()
        ]
        evidence_rows = [row.get("identityNameEvidence") for row in target_rows]
        if not evidence_rows or any(not isinstance(value, dict) for value in evidence_rows):
            continue
        evidence = evidence_rows[0]
        evidence_key = json.dumps(evidence, sort_keys=True, ensure_ascii=False)
        if any(json.dumps(value, sort_keys=True, ensure_ascii=False) != evidence_key
               for value in evidence_rows[1:]):
            continue
        member_ids = {person_id for person_id, _, _ in member_records}
        candidates = evidence.get("originalCandidates", [])
        candidate_ids = {candidate.get("personId") for candidate in candidates}
        survivor_id = evidence.get("survivorPersonId")
        survivor_candidate = next(
            (candidate for candidate in candidates if candidate.get("personId") == survivor_id), None,
        )
        candidate_folders = {
            candidate.get("personId"): candidate.get("folder", "").casefold()
            for candidate in candidates
        }
        age_rows = [candidate.get("ageEvidence", {}) for candidate in candidates]
        verified_oldest = (
            len(candidates) == len(member_ids)
            and all(row.get("status") == "verified" and row.get("date") for row in age_rows)
            and sum(row.get("date") == min(age.get("date", "9999") for age in age_rows)
                    for row in age_rows) == 1
            and survivor_candidate is not None
            and survivor_candidate.get("ageEvidence", {}).get("date")
            == min(age.get("date", "9999") for age in age_rows)
        )
        if (
            evidence.get("decision") != "retained original identity name"
            or evidence.get("reviewRequired")
            or candidate_ids != member_ids
            or any(
                continuity_by_person[person_id][0]
                and not next(
                    (candidate.get("preservesCore") is True
                     for candidate in candidates if candidate.get("personId") == person_id),
                    False,
                )
                for person_id, _, _ in member_records
            )
            or any(candidate_folders.get(person_id) != person["folder"].casefold()
                   for person_id, person, _ in member_records)
            or not verified_oldest
            or survivor_id not in member_ids
            or not survivor_candidate
            or evidence.get("survivorFolder", "").casefold()
            != survivor_candidate.get("folder", "").casefold()
            or target.split("/", 1)[-1].casefold() != evidence.get("name", "").casefold()
        ):
            continue
        target_occupants = people_by_folder.get(target.casefold(), [])
        if any(person_id not in member_ids for person_id, _ in target_occupants):
            raise ValueError(f"identity merge destination is owned by an unrelated identity: {target}")
        families = {
            (person.get("family") or {}).get("id")
            for _, person, _ in member_records if person.get("family")
        }
        surnames = {
            (person.get("family") or {}).get("surname", "").casefold()
            for _, person, _ in member_records if person.get("family")
        }
        overrides = {
            person.get("automaticProtectionOverride")
            for _, person, _ in member_records
            if person.get("automaticProtectionOverride")
        }
        if len(families) > 1 or len(surnames) > 1 or len(overrides) > 1:
            raise ValueError(f"identity merge has conflicting family or protection decisions: {target}")
        source_ids = member_ids
        anchors = {
            photo_id for _, person, _ in member_records
            for photo_id in person.get("identityAnchors", [])
        }
        target_rows_by_id = {row.get("photoId"): row for row in target_rows}
        for photo_id in anchors:
            row = target_rows_by_id.get(photo_id)
            if (not row or pathlib.PurePosixPath(row["destination"]).parent.parent.as_posix().casefold()
                    != target.casefold() or pathlib.PurePosixPath(row["destination"]).parent.name != "gallery"):
                raise ValueError(f"identity merge would not preserve mandatory anchor {photo_id}: {target}")
        for row in target_rows:
            state = rejections.candidate_state(catalog, row.get("photoId"), row["sha256"])
            if state.get("rejectionMetadataStale"):
                raise ValueError(
                    f"{row.get('photoId')}: rejected-identity metadata is stale; review changed photo bytes"
                )
            rejected = set(state.get("rejectedPersonIds", []))
            if rejected & source_ids:
                raise ValueError(
                    f"{row.get('photoId')}: destination identity was explicitly rejected"
                )
            rejections.require_destination(
                catalog, row.get("photoId"), row["sha256"], survivor_id,
            )
        merge_plans.append({
            "target": target, "members": member_records, "survivorId": survivor_id,
            "evidence": evidence, "anchors": anchors,
        })
        merged_ids.update(source_ids)

    for person_id, person in catalog["people"].items():
        if person_id in merged_ids:
            continue
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
        target = next(iter(targets)) if unique else split_core_target(person_id, folder)
        unique = unique or target is not None
        if target and target.split("/")[0] in ("Various", "Angels", "Sisters"):
            unique = False
        if has_decisions and not unique:
            raise ValueError(f"identity decisions cannot migrate unambiguously after matching: {folder}")
        if unique and target != folder and any(
            other["folder"].casefold() == target.casefold()
            for other_id, other in catalog["people"].items() if other_id != person_id
        ):
            raise ValueError(f"stable identity migration would collide: {folder} -> {target}")

    for merge in merge_plans:
        target = merge["target"]
        survivor_id = merge["survivorId"]
        survivor = catalog["people"][survivor_id]
        members = merge["members"]
        candidate = next(
            row for row in merge["evidence"]["originalCandidates"]
            if row["personId"] == survivor_id
        )
        all_families = [person["family"] for _, person, _ in members if person.get("family")]
        if all_families:
            family = copy.deepcopy(all_families[0])
            member_ids = {person_id for person_id, _, _ in members}
            if family["referencePersonId"] in member_ids:
                family["referencePersonId"] = survivor_id
            survivor["family"] = family
        survivor["identityAnchors"] = sorted(set(survivor.get("identityAnchors", [])) | merge["anchors"])
        survivor["protected"] = any(person.get("protected", False) for _, person, _ in members)
        overrides = {
            person.get("automaticProtectionOverride")
            for _, person, _ in members if person.get("automaticProtectionOverride")
        }
        if overrides:
            survivor["automaticProtectionOverride"] = next(iter(overrides))
        survivor["displayName"] = merge["evidence"]["name"]
        names = survivor.get("names")
        if names is None:
            survivor["names"] = {
                "originalName": candidate.get("originalName") or candidate["name"],
                "currentName": candidate["name"],
                "originalSource": candidate.get("nameSource", "recorded-history"),
            }
        else:
            names["currentName"] = candidate["name"]
        for _, person, folder in members:
            if folder.casefold() != target.casefold():
                histories = survivor.setdefault("folderHistory", [])
                for alias in [folder, *person.get("folderHistory", [])]:
                    if all(existing.casefold() != alias.casefold() for existing in histories):
                        histories.append(alias)
            if person["id"] != survivor_id:
                person["mergedInto"] = survivor_id
                person["identityAnchors"] = []
        old_folder = survivor["folder"]
        if old_folder.casefold() != target.casefold():
            history = survivor.setdefault("folderHistory", [])
            if all(existing.casefold() != old_folder.casefold() for existing in history):
                history.append(old_folder)
            survivor["folder"] = target
        for person in catalog["people"].values():
            if person.get("mergedInto") in member_ids and person["id"] != survivor_id:
                person["mergedInto"] = survivor_id
            family = person.get("family")
            if family and family.get("referencePersonId") in member_ids:
                family["referencePersonId"] = survivor_id

    for person_id, person in catalog["people"].items():
        folder = person["folder"]
        targets = destinations.get(folder, set())
        if not targets:
            continue
        if person_id in merged_ids:
            continue
        has_decisions = bool(
            person.get("automaticProtectionOverride") or person.get("names") or person.get("family")
            or person.get("identityAnchors") or person.get("protected")
            or any(person_id in photo.get("rejectedPersonIds", []) for photo in catalog["photos"].values())
        )
        unique = len(targets) == 1 and len(owners[next(iter(targets))]) == 1
        target = next(iter(targets)) if unique else split_core_target(person_id, folder)
        unique = unique or target is not None
        if target and target.split("/")[0] in ("Various", "Angels", "Sisters"):
            unique = False
        if has_decisions and not unique:
            raise ValueError(f"identity decisions cannot migrate unambiguously after matching: {folder}")
        if unique and target != folder:
            if any(other["folder"].casefold() == target.casefold()
                   for other_id, other in catalog["people"].items() if other_id != person_id):
                raise ValueError(f"stable identity migration would collide: {folder} -> {target}")
        if unique:
            selected = supported_name_candidate(person_id, folder, target)
            if selected:
                evidence, candidate = selected
                person["displayName"] = evidence["name"]
                names = person.get("names")
                if names is None:
                    person["names"] = {
                        "originalName": candidate.get("originalName") or candidate["name"],
                        "currentName": candidate["name"],
                        "originalSource": candidate.get("nameSource", "recorded-history"),
                    }
                else:
                    names["currentName"] = candidate["name"]
            if target.casefold() != folder.casefold():
                if all(existing.casefold() != folder.casefold()
                       for existing in person.setdefault("folderHistory", [])):
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
    lifecycle = plan.get("groupLifecycle") or {}
    if "decisionEvidence" in lifecycle:
        from .directed_reformation import unpack_runtime_decisions

        evidence = unpack_runtime_decisions(lifecycle["decisionEvidence"])
        expected = {row["photoId"] for row in plan["photos"] if row.get("directedReformation")}
        if set(evidence) != expected:
            raise ValueError("directed decision evidence population differs")
        for row in plan["photos"]:
            for key, value in row.get("directedReformation", {}).items():
                if key != "decisionEvidencePhotoId" and evidence[row["photoId"]].get(key) != value:
                    raise ValueError("directed decision evidence summary differs")
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
        if (
            plan.get("castSeedPolicy", "all") == "core"
            and relative.parts[0] in ("Angels", "Sisters")
            and relative.parts[2] == "gallery"
        ):
            required_evidence = {
                "retainedCast", "releasedCast", "castSeedScore", "castSeedThreshold",
                "castSeedCore", "castSeedAnchor", "castSeedProtectedIdentity",
                "castSeedProtectedPhoto", "castSeedWorkflowSelected",
                "castSeedDecision", "castSeedReason",
            }
            category = relative.parts[0]
            expected_threshold = plan["policy"]["categoryPolicies"][category][
                "identityCoreMinimumSimilarity"
            ]
            score = row.get("castSeedScore")
            if (
                not required_evidence <= set(row)
                or row.get("castSeedThreshold") != expected_threshold
                or row.get("castSeedDecision") not in ("retained", "released")
                or row.get("retainedCast") is not (row.get("castSeedDecision") == "retained")
                or row.get("releasedCast") is not (row.get("castSeedDecision") == "released")
                or not isinstance(row.get("castSeedReason"), str)
                or not row["castSeedReason"].strip()
                or (
                    score is not None
                    and (
                        isinstance(score, bool) or not isinstance(score, (int, float))
                        or not -1 <= score <= 1
                    )
                )
            ):
                raise ValueError(f"cast seed decision lacks complete policy evidence: {relative}")
        released_cast = (
            relative.parts[0] in ("Angels", "Sisters")
            and row.get("releasedCast") is True
            and plan.get("castSeedPolicy", "all") == "core"
        )
        if released_cast:
            category = relative.parts[0]
            expected_threshold = plan["policy"]["categoryPolicies"][category][
                "identityCoreMinimumSimilarity"
            ]
            if (
                row.get("retainedCast") is not False
                or row.get("castSeedThreshold") != expected_threshold
                or not row.get("castSeedReason")
            ):
                raise ValueError(f"released cast photo lacks bound seed-policy evidence: {relative}")
        admitted_cast = False
        if destination.parts[0] in ("Angels", "Sisters") and destination.parts[2] != "review" and not retained_cast:
            from .policy import evaluate_cast_admission

            admission = row.get("castAdmission", {})
            required = {
                "score", "margin", "independentSupport", "qualityEligible", "metadataStale",
                "rejectionHistory", "protected", "folder",
            }
            if not required <= admission.keys() or admission["folder"] != destination.parent.parent.as_posix():
                raise ValueError(
                    "cast candidates may enter Gallery, never the cast core without frozen evidence: "
                    f"{relative} -> {destination}; retainedCast={row.get('retainedCast')}; "
                    f"admissionFolder={admission.get('folder')}"
                )
            decision = evaluate_cast_admission(
                destination.parts[0], score=admission["score"], margin=admission["margin"],
                independent_support=admission["independentSupport"],
                quality_eligible=admission["qualityEligible"],
                metadata_stale=admission["metadataStale"],
                rejection_history=admission["rejectionHistory"], protected=admission["protected"],
                policy=plan["policy"],
            )
            if decision["decision"] != "admit":
                raise ValueError("cast Gallery admission does not satisfy every approved gate")
            admitted_cast = True
        if relative.parts[0] in ("Angels", "Sisters") and not (retained_cast or released_cast or admitted_cast):
            raise ValueError("cast preparation cannot change cast membership")
        if row["source"] in sources or row["destination"].casefold() in destinations:
            raise ValueError("duplicate source or destination in clean rebase")
        sources.add(row["source"])
        destinations.add(row["destination"].casefold())
        path = source.joinpath(*relative.parts)
        if metadata.content_sha256(path) != row["sha256"]:
            raise ValueError(f"source changed since preview: {path}")


def core_protection_policy(policy):
    """Bind approved trial thresholds to this run, not the ordinary library policy."""
    policy = copy.deepcopy(policy)
    if not policy["protection"].get("automatic"):
        raise ValueError("core rebase requires the shared automatic-protection evidence recipe")
    policy["version"] = policy["version"].removesuffix("-core-rebase-v1") + "-core-rebase-v1"
    policy["rebaseProtection"] = {
        "enabled": True,
        "minimumOwnCoreSimilarities": {
            "Angels": .40, "Sisters": .40, "Models": .50,
            "Prospects": .60, "Potentials": None,
        },
    }
    policy["protection"]["automatic"]["enabled"] = True
    for category in ("Angels", "Sisters"):
        policy["categoryPolicies"][category]["identityCoreMinimumSimilarity"] = .40
    return validate_policy(policy)


def _final_membership_outcomes(photos, routed, catalog, policy, settings, root, selected, api,
                               source_root, analysis_paths, *, acquire_protection=True, moving_photo_ids=()):
    """Audit one frozen final membership without silently moving lookalikes again."""
    by_source = {photo.path.relative_to(source_root).as_posix(): photo for photo in photos}
    final = Space([], settings)
    final.photos = []
    final.by_key = collections.defaultdict(list)
    rows_by_photo = {}
    hashes = {}
    for row in routed:
        original = by_source.get(row["source"])
        if original is None:
            raise ValueError(f"final audit cannot resolve measured source: {row['source']}")
        photo = copy.copy(original)
        destination = pathlib.PurePosixPath(row["destination"])
        photo.name = destination.name
        photo.key = destination.parent.parent.as_posix()
        photo.group, _, photo.folder = photo.key.partition("/")
        photo.bucket = destination.parent.name
        photo.path = analysis_paths[row["source"]]
        photo.sha = row.get("preparedSHA256", row["sha256"])
        hashes[photo.path] = photo.sha
        final.photos.append(photo)
        rows_by_photo[id(photo)] = row
        if (
            photo.bucket == "gallery" and photo.key.split("/", 1)[0] in policy["categoryPolicies"]
            and photo.usable(settings["minFace"]) and photo.vec is not None
            and np.isfinite(photo.vec).all() and np.linalg.norm(photo.vec) > 0
            and photo.faces == 1 and photo.f2 <= settings["multiFace"]
            and not row.get("castSeedQualityReason")
            and not row.get("qualityHold")
            and not (callable(getattr(api, "junk_reason", None)) and api.junk_reason(photo, settings))
        ):
            final.by_key[photo.key].append(photo)
    final.keys = sorted(final.by_key)
    audit_catalog = copy.deepcopy(catalog)
    for photo in final.photos:
        photo_id = metadata.photo_id_from_name(photo.name)
        row = rows_by_photo[id(photo)]
        if (
            photo_id in audit_catalog["photos"]
            and audit_catalog["photos"][photo_id]["contentSha256"] in (row["sha256"], photo.sha)
        ):
            audit_catalog["photos"][photo_id]["contentSha256"] = photo.sha
    cores, _, diagnostics = frozen_identity_cores(
        final, audit_catalog, photo_id_fn=metadata.photo_id_from_name,
        content_sha256_fn=lambda path: hashes[path], policy=policy,
    )
    anchors = {
        photo_id
        for person in audit_catalog["people"].values()
        if not person.get("mergedInto") and person["folder"] in cores
        for photo_id in person.get("identityAnchors", [])
        if photo_id in cores[person["folder"]]["corePhotoIds"]
    }
    automatic, protection_evidence = [], []
    if acquire_protection and policy.get("rebaseProtection", {}).get("enabled"):
        automatic, protection_evidence = protection.plan_protection(
            final, cores, audit_catalog, policy, root=root,
            selected_ids={
                metadata.photo_id_from_name(photo.name) for photo in final.photos
                if api.cw.photo_key(photo.name) in selected
            },
            moving_photo_ids=moving_photo_ids,
            category_minimums=policy["rebaseProtection"]["minimumOwnCoreSimilarities"],
        )
        batch_id = "batch_" + uuid.uuid4().hex
        for action in automatic:
            person_id, photo_id = action.get("personId"), action.get("photoId")
            field = "person" if person_id else "photo"
            catalog["people" if person_id else "photos"][person_id or photo_id] = action["after"]
            catalog["actions"].append({
                "id": "action_" + uuid.uuid4().hex, "batchId": batch_id,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "actor": "tool", "type": "person-protected" if person_id else "photo-protected",
                "photoIds": [] if person_id else [photo_id],
                **({"personId": person_id} if person_id else {"contentSha256": action["after"]["contentSha256"]}),
                "reason": action["reason"],
                "beforeState": {"person": None, "photo": None, field: action["before"]},
                "afterState": {"person": None, "photo": None, field: copy.deepcopy(action["after"])},
            })
    protection_by_photo = {
        row["photoId"]: row for row in protection_evidence if row.get("photoId")
    }
    id_counts = collections.Counter(metadata.photo_id_from_name(photo.name) for photo in final.photos)
    support = {}
    if policy.get("rebaseProtection", {}).get("enabled") or any(
        rules.get("galleryAdmissionEnabled") for rules in policy["categoryPolicies"].values()
    ):
        for folder, core in cores.items():
            support[folder] = protection._independent([
                {
                    "photoId": metadata.photo_id_from_name(photo.name),
                    "vector": photo.vec, "sha256": photo.sha,
                }
                for photo in final.by_key[folder]
                if metadata.photo_id_from_name(photo.name)
                and id_counts[metadata.photo_id_from_name(photo.name)] == 1
                and metadata.photo_id_from_name(photo.name) in core["corePhotoIds"]
                and not rejections.candidate_state(
                    audit_catalog, metadata.photo_id_from_name(photo.name), photo.sha,
                ).get("rejectedPersonIds")
            ], policy)
    core_references = {}
    for folder, core in cores.items():
        if folder.split("/", 1)[0] not in ("Angels", "Sisters"):
            continue
        references = []
        for photo in final.by_key[folder]:
            photo_id = metadata.photo_id_from_name(photo.name)
            if photo_id not in core["corePhotoIds"]:
                continue
            row = rows_by_photo[id(photo)]
            references.append({
                "source": row["source"], "destination": row["destination"], "photoId": photo_id,
                "score": core["photoScores"].get(photo.name), "anchor": photo_id in anchors,
            })
        core_references[folder] = sorted(
            references, key=lambda row: (
                not row["anchor"], row["score"] is None,
                -(row["score"] if row["score"] is not None else 0), row["destination"],
            ),
        )[:10]
    audit_rows = []
    for photo in final.photos:
        row = rows_by_photo[id(photo)]
        own = cores.get(photo.key)
        photo_id = metadata.photo_id_from_name(photo.name)
        valid = (
            photo.vec is not None and np.isfinite(photo.vec).all() and np.linalg.norm(photo.vec) > 0
            and photo.usable(settings["minFace"]) and photo.faces == 1 and photo.f2 <= settings["multiFace"]
            and not row.get("qualityHold")
            and not (callable(getattr(api, "junk_reason", None)) and api.junk_reason(photo, settings))
        )
        score = (
            own["photoScores"].get(photo.name, float(photo.vec @ own["vector"]))
            if own and valid else None
        )
        rivals = sorted(
            ({"folder": folder, "score": float(photo.vec @ core["vector"])}
             for folder, core in cores.items() if folder != photo.key and valid
             and core["side"] == ("Artists" if photo.key.startswith("Artists/") else "Prospects")),
            key=lambda rival: (-rival["score"], rival["folder"]),
        )[:3]
        cast_references = sorted(
            (
                {
                    "folder": folder,
                    "score": (
                        round(score, 6) if score is not None else None
                    ) if folder == photo.key else round(float(photo.vec @ core["vector"]), 6),
                }
                for folder, core in cores.items()
                if valid and folder.split("/", 1)[0] in ("Angels", "Sisters")
            ),
            key=lambda reference: (
                reference["score"] is None,
                -(reference["score"] if reference["score"] is not None else 0),
                reference["folder"],
            ),
        )[:3]
        higher = bool(score is not None and rivals and rivals[0]["score"] > score)
        locked = bool(catalog["photos"].get(photo_id, {}).get("protected"))
        photo_record = catalog["photos"].get(photo_id, {})
        workflow = api.cw.photo_key(photo.name) in selected
        reason = (
            "quality gate: no eligible single-face measurement" if not valid else
            "Review or unassigned: not an accepted Gallery member" if photo.bucket != "gallery" or not own else
            "own leave-one-out score unavailable (singleton or excluded evidence)" if score is None else
            "photo protection or mandatory anchor/workflow selection prevents automatic removal"
            if locked or photo_id in anchors or workflow else
            "higher rival: diagnostic only; relatives and lookalikes need bounded follow-up"
            if higher else "no higher rival against the frozen final identity cores"
        )
        followup = bool(
            higher and photo.bucket == "gallery" and not (locked or photo_id in anchors or workflow)
            and rivals[0]["score"] - score >= policy["photoRouting"]["minimumOwnCoreLead"]
        )
        comparison = {
            "source": row["source"], "destination": row["destination"],
            "ownScore": score, "rivals": rivals,
            "castReferences": cast_references,
            "higherRival": higher, "reason": reason, "protected": locked,
            "anchor": photo_id in anchors, "workflowSelected": workflow,
            "followupCandidate": followup,
            "photoId": photo_id, "identityIds": own.get("personIds", []) if own else [],
            "coreMember": bool(own and photo_id in own["corePhotoIds"]),
            "automaticProtection": bool(photo_record.get("protectionProvenance")),
            "manualOptOut": photo_record.get("automaticProtectionOverride") == "disabled",
            "automaticReviewAssociation": row.get("automaticReviewAssociation") is True,
            "rivalMargin": round(score - rivals[0]["score"], 6) if score is not None and rivals else None,
            "independentProtectionSupport": protection_by_photo.get(photo_id, {}).get("independentSupport"),
            "protectionReason": protection_by_photo.get(photo_id, {}).get("reason"),
        }
        if policy.get("rebaseProtection", {}).get("enabled") or any(
            rules.get("galleryAdmissionEnabled") for rules in policy["categoryPolicies"].values()
        ):
            target = rivals[0] if rivals else None
            maximum = policy["identityActions"]["independentEvidenceMaximumSimilarity"]
            refs = [
                other for other in support.get(target["folder"], []) if valid
                and other["photoId"] != photo_id and other["sha256"] != photo.sha
                and float(photo.vec @ other["vector"]) <= maximum
            ] if target else []
            state = rejections.candidate_state(audit_catalog, photo_id, photo.sha)
            source_persons = [
                person for person in audit_catalog["people"].values()
                if not person.get("mergedInto") and person["folder"] == photo.key
            ]
            comparison.update(
                qualityEligible=bool(valid and not row.get("castSeedQualityReason")),
                ambiguousPhotoId=id_counts[photo_id] != 1,
                bucket=photo.bucket,
                identityProtected=bool(
                    photo.group not in ("Angels", "Sisters")
                    and any(person.get("protected") for person in source_persons)
                ),
                rejectionHistory=bool(state.get("rejectionMetadataStale") or state.get("rejectedPersonIds")),
                metadataStale=bool(
                    photo_record and photo_record.get("contentSha256") not in (row["sha256"], photo.sha)
                ),
                refinementTarget=({
                    **target, "independentSupport": len(refs),
                    "identityProtected": cores[target["folder"]]["identityProtected"],
                } if target else None),
            )
            from .policy import evaluate_cast_admission

            references = ([{"folder": photo.key, "score": score}] if score is not None else []) + rivals
            references.sort(key=lambda item: (-item["score"], item["folder"].casefold()))
            admission_target = references[0] if references else None
            admission_refs = [
                other for other in support.get(admission_target["folder"], []) if valid
                and other["photoId"] != photo_id and other["sha256"] != photo.sha
                and float(photo.vec @ other["vector"]) <= maximum
            ] if admission_target else []
            admission_margin = (
                admission_target["score"] - references[1]["score"] if len(references) > 1 else 2.
            )
            admission = evaluate_cast_admission(
                admission_target["folder"].split("/", 1)[0] if admission_target else "",
                score=admission_target["score"] if admission_target else None,
                margin=admission_margin, independent_support=len(admission_refs),
                quality_eligible=comparison["qualityEligible"] and not comparison["ambiguousPhotoId"],
                rejection_history=comparison["rejectionHistory"],
                metadata_stale=comparison["metadataStale"],
                protected=locked or workflow or photo_id in anchors or comparison["identityProtected"],
                policy=policy,
            )
            comparison["castAdmission"] = {
                **admission, "folder": admission_target["folder"] if admission_target else None,
                "score": admission_target["score"] if admission_target else None,
                "margin": admission_margin, "independentSupport": len(admission_refs),
                "qualityEligible": comparison["qualityEligible"],
                "metadataStale": comparison["metadataStale"],
                "rejectionHistory": comparison["rejectionHistory"],
                "protected": locked or workflow or photo_id in anchors or comparison["identityProtected"],
            }
            if policy.get("rebaseProtection", {}).get("enabled"):
                comparison["refinementDecision"] = refinement.membership_decision(comparison, policy)
        comparison["ownScore"] = round(score, 6) if score is not None else None
        comparison["rivals"] = [{**rival, "score": round(rival["score"], 6)} for rival in rivals]
        audit_rows.append(comparison)
    return {
        "reference": "frozen final Gallery cores; own core members use leave-one-out; rivals exclude own identity",
        "pass": 1, "state": "audited", "rows": audit_rows, "diagnostics": diagnostics,
        "higherRivalCount": sum(row["higherRival"] for row in audit_rows),
        "followupCandidateCount": sum(row["followupCandidate"] for row in audit_rows),
        "nextPassNeeded": any(row["followupCandidate"] for row in audit_rows),
        "automaticMoves": 0,
        "protectionEvidence": protection_evidence,
        "automaticPhotoProtectionCount": sum("photoId" in action for action in automatic),
        "automaticIdentityProtectionCount": sum("personId" in action for action in automatic),
        "coreReferences": core_references,
    }


def _admit_cast(rows, audit, policy):
    """Apply one staged admission pass; no admitted photo can support another."""
    rows = copy.deepcopy(rows)
    comparisons = {row["source"]: row for row in audit["rows"]}
    decisions = []
    for row in rows:
        comparison = comparisons[row["source"]]
        admission = comparison.get("castAdmission", {})
        destination = pathlib.PurePosixPath(row["destination"])
        target = admission.get("folder")
        if not target or target.split("/", 1)[0] not in ("Angels", "Sisters"):
            continue
        if (
            row.get("retainedCast") and not row.get("releasedCast")
            and pathlib.PurePosixPath(row["source"]).parent.name == "gallery"
        ):
            continue
        if destination.parent.as_posix() == f"{target}/gallery":
            continue
        decision = {
            "source": row["source"], "photoId": comparison["photoId"], **admission,
            "kind": "existing-cast-review" if row["source"].startswith(f"{target}/review/") else
                    "cast-return" if row["source"].startswith(f"{target}/gallery/") else "cast-gain",
        }
        decisions.append(decision)
        if admission.get("decision") != "admit":
            continue
        row["destination"] = f"{target}/gallery/{destination.name}"
        row["castAdmission"] = decision
        row["reason"] += "; " + admission["reason"]
        if pathlib.PurePosixPath(row["source"]).parts[0] in ("Angels", "Sisters"):
            category = pathlib.PurePosixPath(row["source"]).parts[0]
            row.update(
                retainedCast=False, releasedCast=True, castSeedDecision="released",
                castSeedReason="released from initial membership; approved staged Gallery admission",
                castSeedThreshold=policy["categoryPolicies"][category]["identityCoreMinimumSimilarity"],
            )
    destinations = [row["destination"].casefold() for row in rows]
    if len(set(destinations)) != len(destinations):
        raise ValueError("staged cast admission would collide destination filenames")
    return rows, {
        "reference": audit["reference"], "passes": 1,
        "admittedCount": sum(row["decision"] == "admit" for row in decisions),
        "decisions": decisions,
    }


def _cast_seed_outcomes(
    entries, cores, catalog, selected, policy, api, seed_policy, min_face,
    quality_exclusions=None, reset_photo_ids=(), insufficient_reference_holds=False,
):
    """Split cast Gallery inputs into retained seeds and ordinary matching candidates."""
    if seed_policy not in {"all", "core"}:
        raise ValueError("cast seed policy must be all or core")
    if seed_policy == "all":
        retained = []
        for relative, photo, _bucket, digest in entries:
            retained.append({
                "source": relative, "destination": relative, "oldFolder": photo.key,
                "photoId": metadata.photo_id_from_name(photo.name), "sha256": digest,
                "retainedCast": True, "releasedCast": False,
                "reason": "Cast membership retained by the default all-seeds policy",
            })
        return retained, {}, {}

    quality_exclusions = quality_exclusions or {}
    reset_photo_ids = set(reset_photo_ids)
    people_by_folder = collections.defaultdict(list)
    for person_id, person in catalog["people"].items():
        if person["folder"].split("/", 1)[0] in ("Angels", "Sisters"):
            people_by_folder[person["folder"]].append((person_id, person))
    entries_by_folder = collections.defaultdict(list)
    digest_by_path = {}
    id_locations = collections.defaultdict(list)
    for relative, photo, bucket, _digest in entries:
        digest_by_path[relative] = _digest
        photo_id = metadata.photo_id_from_name(photo.name)
        if photo_id:
            id_locations[photo_id].append((photo.key, relative))
        if bucket != "gallery":
            continue
        entries_by_folder[photo.key].append((relative, photo))
    duplicates = sorted(photo_id for photo_id, locations in id_locations.items() if len(locations) > 1)
    if duplicates:
        raise ValueError(f"cast seed selection has ambiguous photo IDs: {duplicates[:10]}")

    retained, released, evidence = [], {}, {}
    for folder, gallery in sorted(entries_by_folder.items()):
        owners = people_by_folder.get(folder, [])
        if len(owners) > 1:
            raise ValueError(f"cast seed release has ambiguous identity ownership: {folder}")
        person_id, person = owners[0] if owners else (None, None)
        anchor_ids = set(person.get("identityAnchors", [])) if person else set()
        gallery_ids = {
            metadata.photo_id_from_name(photo.name): (photo, relative)
            for relative, photo in gallery
            if metadata.photo_id_from_name(photo.name)
        }
        missing_anchors = anchor_ids - set(gallery_ids)
        if missing_anchors:
            raise ValueError(
                f"cast seed release cannot resolve configured anchors in {folder}: "
                f"{sorted(missing_anchors)}"
            )
        usable_ids = {
            photo_id for photo_id, (photo, relative) in gallery_ids.items()
            if photo.usable(min_face)
            and relative not in quality_exclusions
        }
        identity_blocks_release = not policy.get("rebaseProtection", {}).get("enabled", False)
        def identity_retains(photo_id):
            return bool(person and person.get("protected") and identity_blocks_release
                        and photo_id not in reset_photo_ids)

        core = cores.get(folder)
        if core is None and not insufficient_reference_holds and not all(
                identity_retains(metadata.photo_id_from_name(photo.name))
                or catalog["photos"].get(metadata.photo_id_from_name(photo.name), {}).get("protected")
                or metadata.photo_id_from_name(photo.name) in anchor_ids
                or api.cw.photo_key(photo.name) in selected
                for _relative, photo in gallery
        ):
            raise ValueError(
                f"cast seed release cannot score {folder}: no eligible identity core under current policy"
            )
        core = core or {}
        core_ids = set(core.get("corePhotoIds", []))
        unusable_core_ids = {
            metadata.photo_id_from_name(photo.name)
            for relative, photo in gallery if relative in quality_exclusions
        } & core_ids
        if unusable_core_ids:
            raise ValueError(
                f"cast seed release refuses unusable faces in the current core for {folder}: "
                f"{sorted(unusable_core_ids)}"
            )
        unusable_anchors = anchor_ids - usable_ids
        excluded_anchors = (anchor_ids & usable_ids) - core_ids
        if excluded_anchors:
            raise ValueError(
                f"cast seed release refuses anchors excluded by the current core in {folder}: "
                f"{sorted(excluded_anchors)}"
            )
        threshold = policy["categoryPolicies"][folder.split("/", 1)[0]][
            "identityCoreMinimumSimilarity"
        ]
        minimum_usable = policy["categoryPolicies"][folder.split("/", 1)[0]][
            "minimumUsablePhotosForOutlierActions"
        ]
        reference_hold = insufficient_reference_holds and (not core or len(usable_ids) < minimum_usable)
        releasable = [
            photo for _relative, photo in gallery
            if not (
                identity_retains(metadata.photo_id_from_name(photo.name))
                or catalog["photos"].get(metadata.photo_id_from_name(photo.name), {}).get("protected")
                or metadata.photo_id_from_name(photo.name) in anchor_ids
                or api.cw.photo_key(photo.name) in selected
                or metadata.photo_id_from_name(photo.name) in core_ids
            )
        ]
        if releasable and len(usable_ids) < minimum_usable and not reference_hold:
            raise ValueError(
                f"cast seed release refused for {folder}: {len(usable_ids)} usable Gallery photos "
                f"are below the configured {minimum_usable}-photo outlier-action minimum"
            )
        if releasable and unusable_anchors:
            raise ValueError(
                f"cast seed release refused for {folder}: configured anchors are not usable core evidence "
                f"({sorted(unusable_anchors)})"
            )
        for relative, photo in gallery:
            photo_id = metadata.photo_id_from_name(photo.name)
            photo_record = catalog["photos"].get(photo_id, {})
            score = (
                None if relative in quality_exclusions
                else core.get("photoScores", {}).get(photo.name)
            )
            anchor = bool(photo_id and photo_id in anchor_ids)
            core_member = bool(photo_id and photo_id in core_ids)
            identity_protected = bool(person and person.get("protected"))
            photo_protected = bool(photo_record.get("protected"))
            workflow_selected = api.cw.photo_key(photo.name) in selected
            reasons = []
            if reference_hold:
                reasons.append("reference-needed hold: insufficient eligible core; no automatic release or reference authority")
            if identity_retains(photo_id):
                reasons.append("protected identity")
            if photo_protected:
                reasons.append("protected photo")
            if anchor:
                reasons.append("configured identity anchor")
            if workflow_selected:
                reasons.append("workflow-selected photo")
            if core_member:
                reasons.append("member of the current configured identity core")
            keep = bool(
                identity_retains(photo_id)
                or photo_protected or anchor or workflow_selected or core_member or reference_hold
            )
            reason = "; ".join(reasons) if keep else (
                "below configured identity-core similarity minimum"
                if score is not None and score < threshold else
                "excluded from current identity core by its configured eligibility gates"
            )
            row = {
                "source": relative, "destination": relative, "oldFolder": photo.key,
                "photoId": photo_id, "sha256": digest_by_path[relative],
                "retainedCast": keep, "releasedCast": not keep,
                "castSeedScore": score, "castSeedThreshold": threshold,
                "castSeedUsableCount": len(usable_ids),
                "castSeedMinimumUsablePhotos": minimum_usable,
                "castSeedQualityReason": quality_exclusions.get(relative),
                "castSeedCore": core_member, "castSeedAnchor": anchor,
                "castSeedReferenceHold": reference_hold,
                "castSeedProtectedIdentity": identity_protected,
                "castSeedProtectedPhoto": photo_protected,
                "castSeedWorkflowSelected": workflow_selected,
                "castSeedDecision": "retained" if keep else "released",
                "castSeedReason": reason,
                "reason": reason if keep else "Released from cast core for fresh matching: " + reason,
            }
            if keep:
                retained.append(row)
            else:
                released[relative] = (photo, "gallery", row["sha256"])
                evidence[relative] = {key: value for key, value in row.items()
                                      if key.startswith("castSeed") or key in ("retainedCast", "releasedCast")}
    # Existing cast Review images remain staged; they are not core candidates.
    for relative, photo, bucket, digest in entries:
        if bucket == "review":
            retained.append({
                "source": relative, "destination": relative, "oldFolder": photo.key,
                "photoId": metadata.photo_id_from_name(photo.name), "sha256": digest,
                "retainedCast": True, "releasedCast": False,
                "castSeedDecision": "retained-review",
                "castSeedReason": "Existing cast Review image remains staged outside core release",
                "reason": "Existing cast Review image remains staged outside core release",
            })
    return retained, released, evidence


def _quality_hold_evidence(photo, settings, reason):
    kind = (
        "ambiguous-multiface" if photo.faces > 1 and photo.f2 >= settings.get("multiFace", .3)
        else "measured-face-too-small" if 0 < photo.px < settings["minFace"]
        else "measured-head-obstruction" if reason and "bars cover her head" in reason
        else "missing-or-unusable-measurement" if photo.vec is None
        else "unclassified-quality-hold"
    )
    return {
        "classification": kind, "reason": reason, "faces": photo.faces, "facePixels": photo.px,
        "minimumFacePixels": settings["minFace"], "secondaryFaceRatio": photo.f2,
        "secondaryFaceRatioAvailable": bool(getattr(photo, "secondary_face_ratio_available", False)),
        "recoverableJunkCandidate": kind in ("measured-face-too-small", "measured-head-obstruction"),
    }


def create_plan(
    layout, run, policy, api, embedder=None, *, reuse_measurements=False,
    preparation=None, cast_seeds="all", seed_catalog=None, config_snapshot=None,
    working_inputs=None, matching_inputs=None, workflow_reset=None, regroup=False, review_source=None,
    directed_recipe=None, dominant_provisional=False,
):
    if dominant_provisional and directed_recipe is None:
        raise ValueError("dominant provisional assignment requires directed mode")
    """Flatten source photos before building any non-cast identity references."""
    if cast_seeds not in {"all", "core"}:
        raise ValueError("cast seed policy must be all or core")
    if regroup and directed_recipe is None:
        from .group_lifecycle import runtime_policy
        policy = runtime_policy(policy)
    elif regroup:
        from . import directed_reformation
        policy = directed_reformation.runtime_policy(policy, directed_reformation.recipe_named(directed_recipe))
    source = layout["source_root"]
    cache_path = run / "likeness-cache.json"
    if cache_path.exists() and not reuse_measurements:
        raise ValueError("clean rebase requires a new run directory and empty embedding cache")
    from . import cast_workflow

    cfg = copy.deepcopy(config_snapshot) if config_snapshot is not None else api.cw.load_cfg()
    catalog_path = metadata.path_for_root(layout["working_root"])
    source_catalog_hash = metadata.content_sha256(catalog_path)
    catalog = copy.deepcopy(seed_catalog) if seed_catalog is not None else metadata.load_catalog(catalog_path)
    metadata.validate_catalog(catalog)
    if seed_catalog is None and catalog_path.is_file():
        (run / "seed-catalog.json").write_bytes(catalog_path.read_bytes())
    else:
        _write_json(run / "seed-catalog.json", catalog)
    _write_json(run / "config-snapshot.json", cfg)
    working_inputs = (
        copy.deepcopy(working_inputs) if working_inputs is not None
        else _curation_inventory(layout) if preparation else None
    )
    matching_inputs = (
        copy.deepcopy(matching_inputs) if matching_inputs is not None else {
            relative: value[1] for relative, value in layout["manifest_files"].items()
            if pathlib.PurePosixPath(relative).parent.name in ("gallery", "review")
        } if seed_catalog is not None else working_inputs
    )
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
    configure_evidence = getattr(embed, "configure_evidence", None)
    if callable(configure_evidence):
        configure_evidence(
            api.cw.storage_root(
                cfg, "likeness", root=layout["working_root"]
            ) / "general" / "face-evidence",
            library_root=layout["working_root"],
        )
    needs_alignment_evidence = getattr(embed, "needs_alignment_evidence", None)
    photos, records = [], {}
    quality_photos = {}
    prepared_rows = {row["source"]: row for row in preparation[1]["photos"]} if preparation else {}
    cast_entries = []
    cast_quality_exclusions = {}
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
                refresh_evidence = (
                    digest in cache.emb
                    and callable(needs_alignment_evidence)
                    and needs_alignment_evidence(cache.emb[digest], analysis_path)
                )
                if digest not in cache.emb or refresh_evidence:
                    cache.emb[digest] = embed(analysis_path) or {"faces": -1}
                photo = Photo(path, group, name, digest, cache.emb[digest])
                photos.append(photo)
                quality_photo = copy.copy(photo)
                quality_photo.path = analysis_path
                quality_photos[relative] = quality_photo
                if cast_seeds == "core" and category in ("Angels", "Sisters") and bucket == "gallery":
                    junk_reason = getattr(api, "junk_reason", None)
                    if callable(junk_reason):
                        reason = junk_reason(quality_photo, settings)
                        if reason:
                            cast_quality_exclusions[relative] = reason
                if category in (*RESET_CATEGORIES, "Various"):
                    records[relative] = (photo, bucket, manifest[relative][1])
                elif category in ("Angels", "Sisters"):
                    digest = (
                        manifest[relative][1] if relative in manifest
                        else metadata.content_sha256(path)
                    )
                    cast_entries.append((relative, photo, bucket, digest))
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
        relative = photo.path.relative_to(source).as_posix()
        if (
            photo.usable(settings["minFace"])
            and relative not in cast_quality_exclusions
        ):
            space.by_key[photo.key].append(photo)
    space.keys = sorted(space.by_key)
    catalog = metadata.with_configured_anchors(catalog, cfg, cast_photos)
    regroup_catalog = copy.deepcopy(catalog) if regroup else catalog
    core_catalog = catalog
    if preparation:
        core_catalog = copy.deepcopy(catalog)
        current_paths = {
            metadata.photo_id_from_name(pathlib.PurePosixPath(relative).name): layout["working_root"] / relative
            for relative in matching_inputs
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
    workflow_receipt = None
    reset_ids = set()
    if cast_seeds == "core":
        core_catalog, reset_ids, workflow_receipt = cast_workflow.reset_plan(
            cfg, core_catalog, cast_entries, cores, api, workflow_reset,
        )
        if reset_ids:
            for folder in space.by_key:
                space.by_key[folder] = [
                    photo for photo in space.by_key[folder]
                    if metadata.photo_id_from_name(photo.name) not in reset_ids
                ]
            cores, _, reset_diagnostics = frozen_identity_cores(
                space, core_catalog, photo_id_fn=metadata.photo_id_from_name,
                content_sha256_fn=metadata.content_sha256, policy=policy,
            )
            diagnostics.extend(reset_diagnostics)
    if not cores or any(not key.startswith(("Angels/", "Sisters/")) for key in cores):
        raise ValueError("clean rebuild must start with Angel/Sister cores only")
    selected = api.chosen_keys(cfg) - {
        api.cw.photo_key(photo.name) for _relative, photo, _bucket, _digest in cast_entries
        if metadata.photo_id_from_name(photo.name) in reset_ids
    }
    cast_rows, released_cast, cast_seed_evidence = _cast_seed_outcomes(
        cast_entries, cores, core_catalog, selected, policy, api, cast_seeds,
        settings["minFace"], cast_quality_exclusions,
        reset_photo_ids=reset_ids,
        insufficient_reference_holds=regroup,
    )
    records.update(released_cast)
    duplicates = {}
    input_ids = _matching_photo_ids(
        photos, source, api, duplicates,
        digests={relative: manifest[relative][1] for relative in manifest},
    )
    duplicate_counts = collections.Counter()
    protected_folders = {
        person["folder"] for person in catalog["people"].values()
        if person.get("protected") and not policy.get("rebaseProtection", {}).get("enabled")
    }
    candidates, by_id = [], {}
    preserved, unusable = [], []
    named = _named_routes(source, catalog, api) if preparation else {}
    for relative, (photo, bucket, sha256) in sorted(records.items()):
        photo_id = input_ids[relative]
        base = {
            "source": relative, "sha256": sha256, "photoId": photo_id,
            "oldFolder": photo.key,
        }
        if photo_id and metadata.photo_id_from_name(photo.name) is None:
            content = api.cw.photo_key(api.originals.standard_name(photo.name, "incoming"))
            base["photoIdOrigin"] = (
                "originals-normalized-filename" if content and photo_id.endswith(content)
                else "originals-content-id"
            )
        base.update(cast_seed_evidence.get(relative, {}))
        if relative in named:
            destination, reason = named[relative]
            preserved.append({**base, "destination": destination, "reason": reason})
            continue
        photo_record = core_catalog["photos"].get(photo_id, {})
        provenance = photo_record.get("protectionProvenance", {})
        protected_core = bool(
            policy.get("rebaseProtection", {}).get("enabled")
            and photo.key.split("/", 1)[0] in RESET_CATEGORIES
            and photo_record.get("protected")
            and photo_record.get("automaticProtectionOverride") != "disabled"
            and photo_record.get("contentSha256") == sha256
            and provenance.get("recipeVersion") == "independent-gallery-loo-v1"
            and photo_id in provenance.get("frozenCorePhotoIds", [])
        )
        if protected_core:
            base["rebaseProtectedCore"] = True
        protected = (
            api.cw.photo_key(photo.name) in selected
            or photo.key in protected_folders and photo_id not in reset_ids
            or photo_record.get("protected", False) and not protected_core
        )
        if protected:
            preserved.append({
                **base, "destination": relative,
                "reason": "protected/workflow photo retained; excluded from candidate clustering",
            })
            continue
        if not photo_id and relative in duplicates:
            canonical = duplicates[relative]
            # Deliberately no photo-ID token, so the held copy never competes with the canonical ID.
            key = f"duplicate_{sha256[:12]}"
            duplicate_counts[key] += 1
            suffix = pathlib.PurePosixPath(photo.name).suffix.lower().replace(".jpeg", ".jpg")
            unusable.append({
                **base,
                "destination": (
                    f"Various/review/various_{key}_duplicate-{duplicate_counts[key]}{suffix}"
                ),
                "reason": f"exact byte duplicate of {canonical}; held in Review, excluded from clustering",
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
        quality_reason = cast_quality_exclusions.get(relative)
        if not quality_reason and hasattr(api, "junk_reason"):
            quality_reason = api.junk_reason(quality_photos[relative], settings)
        if not photo.usable(settings["minFace"]) or quality_reason:
            unusable.append({
                **base,
                "destination": f"Various/review/{photo.name}",
                "qualityHold": True,
                "qualityEvidence": _quality_hold_evidence(photo, settings, quality_reason),
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
    if regroup:
        result = {
            "assignments": [], "clusters": [],
            "held": [{"photoId": row["photoId"], "reason": "released to member-first regrouping; not yet assessed"}
                     for row in candidates],
        }
    else:
        result = plan_reconciliation(
            candidates, cores, assign=settings["assign"], margin=settings["margin"],
            cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
            minimum_cluster=settings["minCluster"], cast_merge=settings["castMerge"],
            name_factory=lambda seed, taken: api.invent_name(seed, taken),
            policy=policy,
        )
    locked_ids = {
        photo_id for photo_id, record in core_catalog["photos"].items() if record.get("protected")
    } | {
        photo_id for person in core_catalog["people"].values() for photo_id in person.get("identityAnchors", [])
    } | {
        input_ids[relative] for relative, (photo, _, _) in records.items()
        if input_ids.get(relative) and api.cw.photo_key(photo.name) in selected
    }
    result, refinement_evidence = refinement.refine(
        result, candidates, cores, policy, locked_ids=locked_ids,
    )
    print(
        f"clean rebase: refinement {refinement_evidence['passCount']} pass(es), "
        f"{refinement_evidence['moveCount']} move(s), {refinement_evidence['mergeCount']} merge(s), "
        f"{len(refinement_evidence['unresolved'])} unresolved; {refinement_evidence['stopReason']}",
        flush=True,
    )
    routed = list(preserved) + list(unusable)
    for row in result["assignments"]:
        base = by_id[row["photoId"]]
        routed.append({
            **base, **row, "destination": f"{row['destination']}/gallery/{pathlib.PurePosixPath(base['source']).name}",
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
    final_refinement = None
    if policy.get("rebaseProtection", {}).get("enabled") and not regroup:
        if preparation:
            _bind_preparation(routed, prepared_rows, preparation[0], api)
        analysis_paths = {relative: photo.path for relative, photo in quality_photos.items()}

        def evaluate_membership(rows):
            audit = _final_membership_outcomes(
                photos, rows, core_catalog, policy, settings, layout["sandbox_root"], selected, api,
                source, analysis_paths, acquire_protection=False,
            )
            for comparison in audit["rows"]:
                if comparison["photoId"] in locked_ids:
                    comparison["refinementDecision"] = {
                        "decision": "hold", "reason": "protected, anchored, workflow-selected or rejection-history photo",
                    }
            return audit

        print("clean rebase: rebuilding Gallery cores for audit-aligned membership refinement", flush=True)
        routed, final_refinement = refinement.refine_membership(routed, evaluate_membership)
        print(
            f"clean rebase: final membership {final_refinement['passCount']} pass(es), "
            f"{final_refinement['moveCount']} move(s), {len(final_refinement['residuals'])} residual(s); "
            f"{final_refinement['stopReason']}", flush=True,
        )
        membership = collections.defaultdict(list)
        for row in routed:
            destination = pathlib.PurePosixPath(row["destination"])
            if destination.parent.name == "gallery":
                membership[destination.parent.parent.as_posix()].append(row.get("photoId"))
            if row.get("photoId"):
                by_id.setdefault(row["photoId"], row)
        for group in result["clusters"]:
            group["photoIds"] = sorted(photo_id for photo_id in membership[group["destination"]] if photo_id)
        result["clusters"] = [group for group in result["clusters"] if group["photoIds"]]
        for photo in photos:
            relative = photo.path.relative_to(source).as_posix()
            photo_id = input_ids.get(relative)
            if photo_id and photo_id not in vectors and photo.vec is not None:
                vectors[photo_id] = photo.vec
                candidates.append({"photoId": photo_id, "vector": photo.vec})
    # Historical names and surnames follow the refined membership, never matching evidence.
    if preparation:
        _bind_preparation(routed, prepared_rows, preparation[0], api)
    admission_audit = _final_membership_outcomes(
        photos, routed, core_catalog, policy, settings, layout["sandbox_root"], selected, api,
        source, {relative: photo.path for relative, photo in quality_photos.items()},
        acquire_protection=False,
    )
    routed, cast_admission = _admit_cast(routed, admission_audit, policy)
    if final_refinement and not policy.get("groupCastReviewEnabled", True):
        admission_boundary = final_refinement["passCount"]
        routed, final_refinement = refinement.refine_membership(
            routed, evaluate_membership, prior_evidence=final_refinement,
        )
        final_refinement["admissionBoundaryAfterPass"] = admission_boundary
        print(
            f"clean rebase: post-admission membership {final_refinement['passCount'] - admission_boundary} "
            f"pass(es); {final_refinement['moveCount']} total move(s); "
            f"{final_refinement['stopReason']}", flush=True,
        )
    membership = collections.defaultdict(list)
    for row in routed:
        destination = pathlib.PurePosixPath(row["destination"])
        if destination.parent.name == "gallery":
            membership[destination.parent.parent.as_posix()].append(row.get("photoId"))
    for group in result["clusters"]:
        group["photoIds"] = sorted(pid for pid in membership[group["destination"]] if pid)
    result["clusters"] = [group for group in result["clusters"] if group["photoIds"]]
    cluster_names, name_evidence = _cluster_name_routes(
        result["clusters"], by_id, catalog, source, api, settings["minCluster"],
        cast_folders=cores, preserved=preserved,
        rebase_protection=bool(policy.get("rebaseProtection", {}).get("enabled")),
    )
    family_evidence = _apply_family_tree(
        result["clusters"], cluster_names, name_evidence, candidates, cores, catalog, source, policy,
        preserved, api,
    )
    refinement.rename_evidence(refinement_evidence, cluster_names)
    if final_refinement:
        refinement.rename_membership_evidence(final_refinement, cluster_names)
    for row in routed:
        destination = pathlib.PurePosixPath(row["destination"])
        folder = destination.parent.parent.as_posix()
        if folder in cluster_names:
            row["destination"] = f"{cluster_names[folder]}/{destination.parent.name}/{destination.name}"
            row["identityNameEvidence"] = name_evidence[folder]
        if row.get("bestMatch") in cluster_names:
            row["bestMatch"] = cluster_names[row["bestMatch"]]
    refinement.rename_steps(routed, cluster_names)
    if preparation:
        _bind_preparation(routed, prepared_rows, preparation[0], api)
        if not regroup:
            _migrate_continuity(
                catalog, routed, source if seed_catalog is not None else layout["working_root"],
                api.originals.images, current_inputs=matching_inputs,
                rebase_protection=bool(policy.get("rebaseProtection", {}).get("enabled")),
            )
    else:
        for row in routed:
            if row.get("photoIdOrigin") == "originals-content-id":
                destination = pathlib.PurePosixPath(row["destination"])
                prefix = api.originals.prefix_of(destination.parent.parent.name)
                key = row["photoId"].removeprefix("photo:")
                row["destination"] = destination.with_name(
                    f"{prefix}_{key}{destination.suffix}",
                ).as_posix()
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
    if not regroup:
        _record_families(catalog, family_evidence, cluster_names, name_evidence, source, policy)
    group_lifecycle = None
    review_bindings = {}
    if regroup:
        from . import group_lifecycle as lifecycle

        catalog = regroup_catalog
        for folder in sorted({row["oldFolder"] for row in routed if row["oldFolder"].startswith(("Angels/", "Sisters/"))}):
            if not any(person["folder"] == folder for person in catalog["people"].values()):
                person_id = "person_" + uuid.uuid5(uuid.NAMESPACE_URL, f"likeness:{source}:{folder.casefold()}").hex
                catalog["people"][person_id] = {
                    "id": person_id, "folder": folder, "displayName": folder.split("/", 1)[-1],
                    "folderHistory": [], "identityAnchors": [], "protected": True,
                }
        measured = {p.path.relative_to(source).as_posix(): quality_photos[p.path.relative_to(source).as_posix()]
                    for p in photos}
        # Quality photos retain the selected pixels; centering belongs to this complete input population.
        for photo in photos:
            measured[photo.path.relative_to(source).as_posix()].vec = photo.vec
        selected_ids = {
            input_ids[relative] for relative, photo in (
                (p.path.relative_to(source).as_posix(), p) for p in photos
            ) if input_ids.get(relative) and api.cw.photo_key(photo.name) in selected
        }
        ledger, review_bindings = lifecycle.review_evidence(review_source, routed) if review_source else ({"pairs": []}, {})
        reference_exclusions = {
            proposal["photoId"] for proposal in ledger.get("referenceProposals", [])
            if proposal["referenceUse"] == "withdraw-in-shadow"
        }
        routed, group_lifecycle = lifecycle.regroup(
            routed, measured, catalog, policy, selected_ids, run.name, name_factory=api.invent_name, pairs=ledger["pairs"],
            reference_exclusions=reference_exclusions, directed_recipe=directed_recipe,
            dominant_provisional=dominant_provisional,
        )
        group_lifecycle["evaluation"]["reviewedPairCount"] = len(ledger["pairs"])
        final_members = collections.defaultdict(list)
        for row in routed:
            if row["membership"]["status"] == "supported" and row["membership"]["coreUse"]:
                folder = pathlib.PurePosixPath(row["destination"]).parent.parent.as_posix()
                final_members[folder].append(row["photoId"])
        final_clusters = [{"destination": folder, "photoIds": ids} for folder, ids in sorted(final_members.items())]
        cluster_names = {group["destination"]: group["destination"] for group in final_clusters}
        name_evidence = {
            folder: {"decision": "retained original identity name", "name": folder.split("/", 1)[-1],
                     "originalCandidates": [], "reason": "member-first canonical naming after grouping"}
            for folder in final_members
        }
        if directed_recipe is not None:
            independent_folders = {item["folder"] for item in group_lifecycle["independentIdentities"]}
            named_clusters = [
                {**group, "clusterId": group["destination"]}
                for group in final_clusters
                if group["destination"].split("/", 1)[0] in RESET_CATEGORIES
                and group["destination"] not in independent_folders
            ]
            directed_names, directed_name_evidence = _cluster_name_routes(
                named_clusters, {row["photoId"]: row for row in routed if row["photoId"]},
                catalog, source, api, settings["minCluster"], cast_folders=cores,
                preserved=preserved,
                rebase_protection=bool(policy.get("rebaseProtection", {}).get("enabled")),
            )
            cluster_names.update(directed_names)
            name_evidence.update(directed_name_evidence)
            for folder in independent_folders & name_evidence.keys():
                name_evidence[folder]["decision"] = "created independent identity name"
        family_candidates = [
            {"photoId": row["photoId"], "vector": measured[row["source"]].vec}
            for row in routed if row["photoId"] and measured[row["source"]].vec is not None
        ]
        family_cores = cores
        if directed_recipe is not None:
            family_vectors = {item["photoId"]: item["vector"] for item in family_candidates}
            family_cores = {
                folder: {"vector": family_tree.centroid([family_vectors[pid] for pid in ids
                                                       if pid in family_vectors])}
                for folder, ids in final_members.items() if folder.startswith(("Angels/", "Sisters/"))
            }
        family_evidence = _apply_family_tree(
            final_clusters, cluster_names, name_evidence, family_candidates, family_cores, catalog, source, policy,
            preserved, api,
        )
        if directed_recipe is not None and family_evidence:
            family_evidence["ownerAssessment"] = [{
                "personId": person_id, "sourceFolder": person["folder"],
                "folder": cluster_names.get(person["folder"], person["folder"]),
                "identityStatus": person.get("identityStatus", "confirmed"),
                "qualifiedReferenceCount": len(final_members.get(person["folder"], [])),
                "status": (
                    "provisional-no-reference-authority" if person.get("identityStatus") == "provisional"
                    else "insufficient-qualified-references" if not final_members.get(person["folder"])
                    else "cast-reference-assessed" if person["folder"].startswith(("Angels/", "Sisters/"))
                    else "name-not-family-eligible" if not identity_names.is_full_person_name(
                        cluster_names.get(person["folder"], person["folder"]).split("/", 1)[-1])
                    else "qualified-owner-assessed"
                ),
            } for person_id, person in sorted(catalog["people"].items()) if not person.get("mergedInto")]
            family_evidence["ownerAssessmentCounts"] = dict(collections.Counter(
                item["status"] for item in family_evidence["ownerAssessment"]
            ))
        for person in catalog["people"].values():
            folder = person["folder"]
            if folder in cluster_names and cluster_names[folder] != folder:
                person["folderHistory"].append(folder)
                person["folder"] = cluster_names[folder]
                person["displayName"] = person["folder"].split("/", 1)[-1]
        for row in routed:
            destination = pathlib.PurePosixPath(row["destination"])
            folder = destination.parent.parent.as_posix()
            if folder in cluster_names:
                row["destination"] = f"{cluster_names[folder]}/{destination.parent.name}/{destination.name}"
            row["identityNameEvidence"] = {
                "decision": "member-first evidence before canonical creative name",
                "personId": row["membership"]["personId"],
                "sourceFolder": row["oldFolder"],
            }
        _record_families(catalog, family_evidence, cluster_names, name_evidence, source, policy, replace=True)
        if preparation:
            _bind_preparation(routed, prepared_rows, preparation[0], api)
        final_destinations = {row["photoId"]: row["destination"] for row in routed if row["photoId"]}
        if directed_recipe is not None:
            from . import directed_reformation
            decisions = directed_reformation.unpack_runtime_decisions(group_lifecycle["decisionEvidence"])
            for row in routed:
                if row.get("photoId") not in decisions:
                    continue
                decision = decisions[row["photoId"]]
                decision["matchingProposedDestination"] = decision["proposedDestination"]
                decision["proposedDestination"] = row["destination"]
                row["directedReformation"] = decision
            group_lifecycle["decisionEvidence"] = directed_reformation.pack_runtime_decisions(routed)
            for view in group_lifecycle["qualifiedReferences"]:
                view["proposedCanonicalFolder"] = cluster_names.get(view["folder"], view["folder"])
        for stage in group_lifecycle["stages"]:
            if stage["id"] == "publication":
                for stage_row in stage["rows"]:
                    if stage_row["photoId"] in final_destinations:
                        stage_row["destination"] = final_destinations[stage_row["photoId"]]
                        stage_row["proposedDestination"] = final_destinations[stage_row["photoId"]]
        summary = {key: value for key, value in group_lifecycle["evaluation"].items()
                   if isinstance(value, (str, int, float))}
        print(f"clean rebase: {lifecycle.RECIPE}: {summary}", flush=True)
    pending = {}
    if final_refinement and not regroup:
        confirmation = _final_membership_outcomes(
            photos, routed, catalog, policy, settings, layout["sandbox_root"], selected, api,
            source, {relative: photo.path for relative, photo in quality_photos.items()},
            acquire_protection=False,
        )
        pending = {
            row["source"]: row for row in confirmation["rows"]
            if row["refinementDecision"]["decision"] == "move"
        }
    final_audit = _final_membership_outcomes(
        photos, routed, catalog, policy, settings, layout["sandbox_root"], selected, api,
        source, {relative: photo.path for relative, photo in quality_photos.items()},
        moving_photo_ids={row["photoId"] for row in pending.values()},
        acquire_protection=not regroup,
    )
    if regroup:
        for comparison in final_audit["rows"]:
            row = next(r for r in routed if r["source"] == comparison["source"])
            comparison["groupMembership"] = row.get("membership")
            if "refinementDecision" in comparison:
                comparison["legacyRefinementDecision"] = comparison["refinementDecision"]
            comparison["refinementDecision"] = {
                "decision": "keep" if row["membership"]["status"] == "supported" else "hold",
                "reason": row["membership"]["reason"],
            }
        final_audit["nextPassNeeded"] = False
    final_audit.update(
        automaticMoves=refinement_evidence["moveCount"] + (final_refinement["moveCount"] if final_refinement else 0),
        automaticMerges=refinement_evidence["mergeCount"],
        refinementPasses=refinement_evidence["passCount"],
        refinementStopReason=refinement_evidence["stopReason"],
        state="refined-then-audited",
    )
    if final_refinement and not regroup:
        final_audit.update(
            finalRefinementPasses=final_refinement["passCount"],
            finalRefinementMoves=final_refinement["moveCount"],
            finalRefinementStopReason=final_refinement["stopReason"],
            postContinuityPendingCount=len(pending),
        )
        residuals = {row["source"]: row for row in final_refinement["residuals"]}
        for row in final_audit["rows"]:
            if row["higherRival"]:
                row["refinementHoldReason"] = (
                    residuals[row["source"]]["reason"] if row["source"] in residuals
                    else "post-continuity comparison qualifies; requires a further reviewed preview"
                    if row["source"] in pending
                    else row["refinementDecision"]["reason"]
                )
        final_audit["nextPassNeeded"] = final_audit["nextPassNeeded"] or bool(pending)
    if workflow_receipt is not None:
        workflow_receipt = cast_workflow.finish_receipt(workflow_receipt, final_audit, routed)
        workflow_receipt["publicationInventory"] = cast_workflow.publication_inventory(cfg, workflow_receipt, api)
        _write_json(run / "workflow-selection.json", workflow_receipt)
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
        "castSeedPolicy": cast_seeds,
        "directedReformation": {
            "enabled": directed_recipe is not None,
            "recipe": directed_recipe,
        },
        "workflowSelection": workflow_receipt,
        "groupLifecycle": group_lifecycle,
        "reviewEvidenceBindings": review_bindings,
        "castSeedThresholds": {
            category: {
                "identityCoreMinimumSimilarity": policy["categoryPolicies"][category][
                    "identityCoreMinimumSimilarity"
                ],
                "minimumUsablePhotosForOutlierActions": policy["categoryPolicies"][category][
                    "minimumUsablePhotosForOutlierActions"
                ],
            }
            for category in ("Angels", "Sisters")
        },
        "castSeedUsability": {
            "minimumFacePixels": settings["minFace"],
            "multiFaceRatio": settings.get("multiFace"),
            "qualityGate": "configured junk_reason plus usable face vector",
        },
        "embeddingCache": str(cache_path), "embeddingCacheStartedEmpty": True,
        "cacheMeasurementsReusedForReplan": reuse_measurements,
        "centeringMean": mean.tolist(), "candidateCount": len(records),
        "coreDiagnostics": diagnostics, "photos": sorted(routed, key=lambda r: r["source"]),
        "finalMembershipAudit": final_audit,
        "castGalleryAdmission": cast_admission,
        "membershipRefinement": refinement_evidence,
        "finalMembershipRefinement": final_refinement,
        "familyNaming": family_evidence,
        "catalogSHA256": metadata.content_sha256(run / "catalog.json"),
        "sourceCatalogSHA256": source_catalog_hash,
        "seedCatalogSHA256": metadata.content_sha256(run / "seed-catalog.json"),
        "configSnapshotSHA256": metadata.content_sha256(run / "config-snapshot.json"),
        "implementationHashes": {
            name: metadata.content_sha256(_implementation_path(name))
            for name in ("clean_rebase.py", "planner.py", "policy.py", "reconciliation.py",
                         "audit.py", "engine.py", "rejections.py", "protection.py", "refinement.py",
                         "family_tree.py", "cast_workflow.py", "likeness.py")
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
            "storageMode": preparation[1].get("storageMode", "full"),
            "processingProfile": preparation[1].get("processingProfile", "standard"),
            "artistCount": sum(row["source"].startswith("Artists/") for row in prepared_rows.values()),
        }
        for name in ("clean_preparation.py", "retained_preparation.py", "derivatives.py", "fast_preparation.py",
                     "verification_reads.py", "metadata.py"):
            plan["implementationHashes"][name] = metadata.content_sha256(pathlib.Path(__file__).with_name(name))
    if regroup:
        plan["implementationHashes"]["group_lifecycle.py"] = metadata.content_sha256(
            pathlib.Path(__file__).with_name("group_lifecycle.py"),
        )
    if directed_recipe is not None:
        for name in (
            "directed_reformation.py", "entrance_trial.py", "membership_reassessment.py",
            "fragment_evidence.py", "reformation.py", "metadata.py",
        ):
            plan["implementationHashes"][name] = metadata.content_sha256(
                pathlib.Path(__file__).with_name(name),
            )
    source_manifest = layout["sandbox_root"] / "source-manifest.json"
    plan["configurationReceipt"] = metadata.cw.storage_configuration_receipt(
        cfg if config_snapshot is not None else metadata.cw.load_cfg(),
        layout["working_root"],
        {
            "runDirectory": run,
            "embeddingCache": cache_path,
            "sourceSnapshotRoot": layout["source_root"],
            "sourceManifest": source_manifest,
        },
    )
    _verify_routes(plan, source)
    if directed_recipe is not None:
        directed_reformation.pack_lifecycle_stages(plan["groupLifecycle"])
    return plan


def _prior_external_files(working, plan, *, preserve_legacy=False):
    from . import verification_reads

    with verification_reads.session(working, label="External inventory", reuse=True) as reads:
        files = _collect_prior_external_files(working, plan, preserve_legacy=preserve_legacy)
        for relative, expected in files.items():
            path = _publication_path(working, relative)
            if reads.digest(path) != expected:
                raise ValueError(f"external inventory changed during verification: {path}")
        return files


def _collect_prior_external_files(working, plan, *, preserve_legacy=False):
    from . import derivatives, retained_preparation, verification_reads

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
        manifest = derivatives.manifest_path(folder)
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
        files[manifest.relative_to(working).as_posix()] = verification_reads.sha256(manifest)
    legacy = {}
    for row in plan["photos"]:
        if not row["destination"].startswith(("Angels/", "Sisters/")):
            continue
        source = _publication_path(working, row["destination"])
        for framing in ("padded", "head", "chest"):
            target = source.parent.parent / derivatives.relative_target(source, framing)
            relative = target.relative_to(working).as_posix()
            if target.exists() and relative not in files:
                target = _publication_path(working, relative)
                legacy[relative] = metadata.content_sha256(target)
    if legacy and not preserve_legacy:
        raise ValueError(
            f"{len(legacy)} unowned legacy derivative collisions; inspect and explicitly use "
            "--preserve-legacy-derivatives to journal their exact bytes for undo")
    if legacy:
        print(f"Verified {len(legacy)} unowned legacy derivative collisions; recovery follows the selected mode.")
        files.update(legacy)
    return files


def _category_roots(root, categories):
    """Category folders and their mirrored processing-store subtrees are replaced as one unit."""
    from . import retained_preparation

    prefix = retained_preparation._processing_prefix(root)
    return [*categories, *(f"{prefix}/{category}" for category in categories)]


def _in_roots(relative, roots):
    parts = pathlib.PurePosixPath(relative).parts
    return any(parts[:len(pathlib.PurePosixPath(item).parts)] == pathlib.PurePosixPath(item).parts
               for item in roots)


def _category_inventory(working, categories):
    return {
        path.relative_to(working).as_posix(): metadata.content_sha256(path)
        for category in _category_roots(working, categories) if (working / category).exists()
        for path in _source_files(working / category)
    }


def verify_staged_install(layout, run, plan):
    """Prove a completed, unpublished stage against frozen preparation and measurements."""
    from PIL import Image
    import originals
    from . import derivatives, retained_preparation

    staged, previous = run / "staged", run / "previous"
    if (plan["status"] != "preview" or not plan.get("preparation")
            or any(key in plan for key in (
                "publishedFiles", "installedCatalogSHA256", "previousCategoryNames", "externalFiles",
                "previousCategories", "previousExternalHashes", "previousCategoryFiles"))):
        raise ValueError("resume requires an unpublished preparation-aware preview")
    disposable = plan.get("recoveryMode") == "disposable"
    if (not staged.is_dir() or _is_reparse_point(staged) or _is_reparse_point(previous)
            or (previous.exists() if disposable else not previous.is_dir() or any(_source_files(previous)))):
        raise ValueError(
            "resume requires safe completed staging and "
            + ("no disposable rollback directory" if disposable else "an empty previous directory")
        )
    working, source = layout["working_root"], layout["source_root"]
    if _curation_inventory(layout) != plan["workingInputs"]:
        raise ValueError("Working inputs changed since matching preview")
    if metadata.content_sha256(metadata.path_for_root(working)) != plan["sourceCatalogSHA256"]:
        raise ValueError("source catalogue changed since preview")
    if metadata.content_sha256(run / "catalog.json") != plan["catalogSHA256"]:
        raise ValueError("prepared sandbox catalogue changed since preview")
    metadata.load_catalog(run / "catalog.json")
    preparation, data = clean_preparation.verify(layout, run)
    if metadata.content_sha256(preparation / "manifest.json") != plan["preparation"]["manifestSHA256"]:
        raise ValueError("preparation evidence differs from matched preview")
    prepared_rows = {row["source"]: row for row in data["photos"]}
    measured = json.loads((run / "likeness-cache.json").read_text(encoding="utf-8"))["emb"]
    expected, manifests, entries = {}, {}, collections.defaultdict(set)
    for number, row in enumerate(plan["photos"], 1):
        native = _publication_path(staged, row["destination"])
        digest = row["preparedSHA256"]
        if metadata.content_sha256(native) != digest:
            raise ValueError(f"staged native checksum mismatch: {native}")
        expected[row["destination"]] = digest
        link = retained_preparation.verify_link(staged, native, row.get("photoId"))
        if (link is None or link["row"] != prepared_rows[row["source"]]
                or link["recipe"] != data["recipe"]):
            raise ValueError(f"staged retained preparation differs: {native}")
        for artifact in link["artifacts"]:
            expected[artifact["path"]] = artifact["sha256"]
        manifest_path = _publication_path(staged, link["manifest"])
        expected[link["manifest"]] = metadata.content_sha256(manifest_path)
        if (row["preparationOutcome"] == "unprocessable"
                or plan["preparation"].get("processingProfile") == "fast"):
            continue
        face = measured.get(hashlib.sha1(native.read_bytes()).hexdigest(), {})
        box, px = face.get("box"), face.get("px", 0)
        folder = native.parent.parent
        if folder not in manifests:
            manifest = derivatives.manifest_path(folder)
            manifests[folder] = derivatives.load(folder)
            expected[manifest.relative_to(staged).as_posix()] = metadata.content_sha256(manifest)
        for framing in ("padded", "head", "chest"):
            available = framing == "padded" or bool(box and px >= originals.MIN_FACE_PX)
            if framing == "head" and available:
                available = originals.headshot(native, None, derivatives.SIZE, box, cleanup=False)
            key = derivatives.relative_target(native, framing).as_posix()
            record = manifests[folder]["entries"].get(key)
            if not available:
                if record is not None:
                    raise ValueError(f"staged derivative bypasses quality gate: {native}: {framing}")
                continue
            # The exact retained link above proves prepared pixels without rescanning the owner.
            if (not record or record.get("recipe") != derivatives.RECIPE
                    or record.get("source") != native.relative_to(folder).as_posix()
                    or record.get("sourceSha256") != digest or record.get("sourcePrepared") is not True
                    or record.get("box") != (list(box) if box else None)):
                raise ValueError(f"staged derivative ownership differs: {native}: {framing}")
            target = _publication_path(staged, (folder / key).relative_to(staged).as_posix())
            with Image.open(target) as image:
                if image.size != derivatives.SIZE or image.format != "PNG":
                    raise ValueError(f"staged derivative dimensions/format differ: {target}")
            rendered = derivatives.render_pixels(native, framing, box, prepared=True)
            if hashlib.sha256(rendered).hexdigest() != record["sha256"]:
                raise ValueError(f"staged derivative pixels differ from the recipe: {target}")
            expected[target.relative_to(staged).as_posix()] = record["sha256"]
            entries[folder].add(key)
        if number % 100 == 0:
            print(f"STAGED VERIFY: {number}/{len(plan['photos'])} native/retained/derivative sets", flush=True)
    for folder, manifest in manifests.items():
        if set(manifest["entries"]) != entries[folder]:
            raise ValueError(f"unaccounted staged derivative entries: {folder}")
    destinations = {
        tuple(pathlib.PurePosixPath(row["destination"]).parts[:2])
        for row in plan["photos"]
        if pathlib.PurePosixPath(row["destination"]).parts[0] in RESET_CATEGORIES
    }
    for category, name in sorted(destinations):
        file_name, copied, payload = _reset_name_file(plan, source, category, name)
        relative = f"{category}/{name}/gallery/{file_name}"
        expected[relative] = (metadata.content_sha256(copied) if copied is not None
                              else _reset_name_payload_hash(payload))
    actual = {path.relative_to(staged).as_posix(): metadata.content_sha256(path)
              for path in _source_files(staged)}
    if actual != expected:
        differences = sorted(key for key in actual.keys() | expected.keys()
                             if actual.get(key) != expected.get(key))
        raise ValueError(f"staged inventory changed or incomplete: {differences[:10]}")
    print(f"Completed staging verified: {len(plan['photos'])} photos, {len(actual)} files.", flush=True)
    return [{"path": path, "sha256": digest} for path, digest in sorted(actual.items())]


def _reset_name_file(plan, source, category, name):
    """Return (file name, source path to copy or None, text payload or None) for one rebuilt identity."""
    renamed = {}
    for family in (plan.get("familyNaming") or {}).get("families", []):
        for member in family["members"]:
            if member["status"].startswith("renamed") and member.get("folder"):
                displaced = family.get("displacedFrom")
                why = (f"surname {displaced['surname']} belongs to the family of {displaced['owner']}"
                       if displaced else f"family {family['surname']}")
                renamed[member["folder"]] = (member["previousName"], why)
    previous, surname = renamed.get(f"{category}/{name}", (name, None))
    former = sorted({
        row["oldFolder"] for row in plan["photos"]
        if pathlib.PurePosixPath(row["destination"]).parts[:2] == (category, name)
        and row["oldFolder"].partition("/")[2] == previous
    })
    names = [path for old in former for path in (pathlib.Path(source) / pathlib.Path(old) / "gallery").glob("z_*.txt")]
    file_name = f"z_{name.lower().replace(' ', '_')}.txt"
    if len(names) == 1 and surname is None:
        return names[0].name, names[0], None
    if len(names) == 1:
        history = names[0].read_text(encoding="utf-8").splitlines()[1:]
        date = plan.get("createdAt", "")[:10]
        lines = [f"name: {name}", *history, f"{date} renamed from {previous} ({surname})"]
        return file_name, None, "\n".join(lines) + "\n"
    return file_name, None, f"name: {name}\nClean sandbox rebuild; prior folders recorded in run.json\n"


def _reset_name_payload_hash(payload):
    return hashlib.sha256(payload.replace("\n", os.linesep).encode("utf-8")).hexdigest()


def _phase_timer(label):
    """Print elapsed seconds per install phase so slow rebase steps are measurable."""
    started = [time.perf_counter()]

    def mark(phase):
        now = time.perf_counter()
        print(f"{label}: {phase} in {now - started[0]:.1f}s", flush=True)
        started[0] = now

    return mark


def install_plan(layout, run, plan, *, resume_install=False, preserve_legacy=False):
    """Stage and publish candidates; only FULL retains replaced categories for rollback."""
    import library_backup

    if (plan.get("finalMembershipAudit") or {}).get("postContinuityPendingCount", 0):
        raise ValueError(
            "final-membership comparison still has qualifying moves after continuity; "
            "review residuals and prepare a resolved preview before installation"
        )
    phase = _phase_timer("Install")
    working, source = layout["working_root"], layout["source_root"]
    disposable = plan.get("recoveryMode", "full") == "disposable"
    if disposable:
        _require_disposable_sandbox(layout, run, plan)
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
    if disposable:
        print("DISPOSABLE SANDBOX: no baseline backup; recovery is a full reset, not undo.", flush=True)
    else:
        library_backup.verify_backup(library_backup.latest_work_root_backup(working))
    phase("preflight (no backup/rollback)" if disposable else "preflight and backup verification")
    staged, previous = run / "staged", run / "previous"
    if not resume_install and (staged.exists() or previous.exists()):
        raise ValueError("staging already exists; inspect the previous attempt before applying")
    staged_files = verify_staged_install(layout, run, plan) if resume_install else None
    local_catalog = working / ".likeness-library.json"
    previous_catalog = local_catalog.read_bytes() if local_catalog.exists() and not disposable else None
    if "catalogSHA256" in plan:
        if metadata.content_sha256(run / "catalog.json") != plan["catalogSHA256"]:
            raise ValueError("prepared sandbox catalogue changed since preview")
        metadata.load_catalog(run / "catalog.json")
        plan["previousLocalCatalog"] = previous_catalog is not None
        if previous_catalog is not None:
            (run / "previous-catalog.json").write_bytes(previous_catalog)
    categories = (*RESET_CATEGORIES, "Various") if plan.get("preparation") else RESET_CATEGORIES
    roots = _category_roots(working, categories)
    for category in roots:
        path = working / category
        if _is_reparse_point(path) or _is_reparse_point(path.parent):
            raise ValueError(f"unsafe generated-category target: {path}")
        if path.exists():
            list(_source_files(path))
    previous_category_files = _category_inventory(working, categories) if not disposable else {}
    previous_external_hashes = (
        _prior_external_files(working, plan, preserve_legacy=preserve_legacy)
        if plan.get("preparation") else {}
    )
    phase("current category and external inventory")
    if not resume_install:
        staged.mkdir()
        if not disposable:
            previous.mkdir()
    preparation_rows = {}
    if plan.get("preparation"):
        preparation, data = clean_preparation.verify(layout, run)
        if metadata.content_sha256(preparation / "manifest.json") != plan["preparation"]["manifestSHA256"]:
            raise ValueError("preparation evidence differs from matched preview")
        preparation_rows = {row["source"]: row for row in data["photos"]}
        phase("preparation evidence verification")
    for row in (() if resume_install else plan["photos"]):
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
                storage_mode=data.get("storageMode", "full"),
            )
    for category in (() if resume_install else RESET_CATEGORIES):
        for folder in sorted((staged / category).iterdir()) if (staged / category).exists() else ():
            gallery = folder / "gallery"
            gallery.mkdir(exist_ok=True)
            file_name, copied, payload = _reset_name_file(plan, source, category, folder.name)
            if copied is not None:
                shutil.copy2(copied, gallery / file_name)
            else:
                (gallery / file_name).write_text(payload, encoding="utf-8")
    phase("staging copies and retained preparation")
    if plan.get("preparation") and not resume_install:
        from . import derivatives, verification_reads

        measured = json.loads((run / "likeness-cache.json").read_text(encoding="utf-8"))["emb"]
        fast = plan["preparation"].get("processingProfile") == "fast"
        with verification_reads.session(staged, label="Install derivatives", seal_content=not disposable):
            for index, row in enumerate(() if fast else plan["photos"], 1):
                path = staged / row["destination"]
                face = measured.get(hashlib.sha1(path.read_bytes()).hexdigest(), {})
                if row["preparationOutcome"] == "unprocessable":
                    print(f"DERIVATIVE HOLD: undecodable source retained without derivatives: {row['source']}")
                    continue
                _, messages = derivatives.maintain(path, face.get("box"), face.get("px", 0), apply=True)
                for message in messages:
                    print(f"DERIVATIVE: {message}")
                if index % 100 == 0:
                    print(f"DERIVATIVES: {index}/{len(plan['photos'])} photos", flush=True)
        phase("FAST: editing and 944x1104 derivatives deferred" if fast else "944x1104 derivatives")
        with verification_reads.session(staged, label="Install details", seal_content=not disposable):
            for index, row in enumerate(plan["photos"], 1):
                retained_preparation.refresh_detail(
                    staged, staged / row["destination"], include_gallery_navigation=True,
                )
                if index % 100 == 0:
                    print(f"DETAILS: {index}/{len(plan['photos'])} photos", flush=True)
        phase("detail pages")
        plan["publishedFiles"] = [
            {"path": path.relative_to(staged).as_posix(), "sha256": metadata.content_sha256(path)}
            for path in _source_files(staged)
        ]
        phase("staged file hashes")
    if resume_install:
        plan["publishedFiles"] = staged_files
    if "publishedFiles" in plan:
        external_files = [item for item in plan["publishedFiles"] if not _in_roots(item["path"], roots)]
    else:
        external_files = [
            {"path": path.relative_to(staged).as_posix(), "sha256": metadata.content_sha256(path)}
            for path in _source_files(staged)
            if not _in_roots(path.relative_to(staged).as_posix(), roots)
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
    if not disposable and _category_inventory(working, categories) != previous_category_files:
        raise ValueError("Working category files changed during staging; no rebuild installed")
    for relative, expected_hash in (() if disposable else previous_external_hashes.items()):
        if metadata.content_sha256(_publication_path(working, relative)) != expected_hash:
            raise ValueError(f"external files changed during staging; no rebuild installed: {relative}")
    phase("pre-publication rechecks")
    moved, installed, cast_added, cast_saved, created_directories = [], [], [], [], []
    try:
        for relative in prior_external:
            current, saved = working / relative, previous / "external" / relative
            if disposable:
                current.unlink()
            else:
                saved.parent.mkdir(parents=True, exist_ok=True)
                current.rename(saved)
                cast_saved.append((current, saved))
        for category in roots:
            target = working / category
            if target.exists():
                if disposable:
                    sandbox._remove_tree(target)
                else:
                    (previous / category).parent.mkdir(parents=True, exist_ok=True)
                    target.rename(previous / category)
                    moved.append(category)
            if (staged / category).exists():
                if not target.parent.exists():
                    target.parent.mkdir(parents=True)
                    created_directories.append(target.parent)
                (staged / category).rename(target)
                installed.append(category)
        for item in external_files:
            path = pathlib.PurePosixPath(item["path"])
            src, dest = staged.joinpath(*path.parts), working.joinpath(*path.parts)
            missing = []
            parent = dest.parent
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            dest.parent.mkdir(parents=True, exist_ok=True)
            created_directories.extend(reversed(missing))
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
        if not disposable:
            plan["previousCategories"] = str(previous)
            plan["previousCategoryNames"] = [category for category in moved if category in categories]
        plan["installedCategoryNames"] = list(categories)
        plan["externalFiles"] = external_files
        if disposable:
            plan["rollbackRetired"] = True
            plan["rollbackCreated"] = False
            plan["recoveryInstruction"] = "No backup or rollback exists; reset sandbox and rebase from source."
        else:
            plan["previousExternalFiles"] = prior_external
            plan["previousExternalHashes"] = previous_external_hashes
            plan["previousCategoryFiles"] = previous_category_files
        _write_json(run / "run.json", plan)
        phase("publication and installed checksums")
    except Exception as error:
        if disposable:
            plan["status"] = "reset-required"
            plan["rollbackCreated"] = False
            plan["publicationError"] = f"{type(error).__name__}: {error}"
            _write_json(run / "run.json", plan)
            raise RuntimeError(
                "Disposable LEAN publication failed; no rollback exists. "
                "Perform a full sandbox reset before another install."
            ) from error
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
        for directory in reversed(created_directories):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
        raise


def _require_disposable_sandbox(layout, run, plan):
    working = layout["working_root"]
    if (not sandbox.is_sandbox_working_path(working)
            or working.parent != layout["sandbox_root"]
            or not (working.parent / "Source").is_dir()
            or not (working.parent / "source-manifest.json").is_file()
            or pathlib.Path(run).parent != working / "_sandbox-state"
            or plan.get("preparation", {}).get("storageMode") != "lean"):
        raise ValueError("disposable recovery requires a verified sandbox-local LEAN prepared run")
    for path in (working, working.parent, pathlib.Path(run)):
        if _is_reparse_point(path):
            raise ValueError(f"linked disposable sandbox path: {path}")


def retire_disposable_rollback(layout, run, plan):
    """Keep transaction rollback until publication is verified, then recover by fresh reset only."""
    _require_disposable_sandbox(layout, run, plan)
    if plan["status"] != "applied":
        raise ValueError("cannot retire rollback before verified publication")
    _check_publication(layout["working_root"], plan)
    previous = _publication_path(pathlib.Path(run), "previous")
    expected = dict(plan.get("previousCategoryFiles", {}))
    expected.update({f"external/{key}": value for key, value in plan.get("previousExternalHashes", {}).items()})
    if previous.exists():
        for path in _source_files(previous):
            relative = path.relative_to(previous).as_posix()
            if expected.get(relative) != metadata.content_sha256(path):
                raise ValueError(f"unverified disposable rollback artifact: {path}")
        sandbox._remove_tree(previous)
    plan["rollbackRetired"] = True
    _write_json(pathlib.Path(run) / "run.json", plan)
    print("DISPOSABLE SANDBOX: transaction rollback retired; exact source evidence and movement reports retained.",
          flush=True)


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
    if plan.get("recoveryMode") == "disposable":
        raise ValueError("disposable sandbox has no undo contract; use a full sandbox reset")
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
    roots = _category_roots(working, categories)
    for category in roots:
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
        for category in roots:
            if (working / category).exists():
                (withdrawn / category).parent.mkdir(parents=True, exist_ok=True)
                (working / category).rename(withdrawn / category)
                moved.append(category)
            if (previous / category).exists():
                (working / category).parent.mkdir(parents=True, exist_ok=True)
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
                    if _in_roots(item["path"], _category_roots(working, categories))}
        disposable = plan.get("recoveryMode") == "disposable"
        actual_inventory = (
            {path.relative_to(working).as_posix() for category in _category_roots(working, categories)
             if (working / category).exists()
             for path in _source_files(working / category)}
            if disposable else _category_inventory(working, categories)
        )
        if actual_inventory != (set(expected) if disposable else expected):
            raise ValueError("installed category inventory changed; review added/removed/edited files")
        output_hashes = {item["path"]: item["sha256"] for item in outputs}
        cast = {
            path.relative_to(working).as_posix(): (
                output_hashes.get(path.relative_to(working).as_posix())
                if disposable else metadata.content_sha256(path)
            )
            for path in image_preparation.inventory(working)
            if path.relative_to(working).parts[0] in ("Angels", "Sisters")
        }
        expected_cast = {row["destination"]: row.get("preparedSHA256", row["sha256"])
                         for row in plan["photos"] if row["destination"].startswith(("Angels/", "Sisters/"))}
        if cast != expected_cast:
            raise ValueError("installed cast inventory changed; review added/removed/edited photos")


def _set_aside_undone_attempt(run, plan):
    """Keep an undone install's journal as evidence and clear the run for a new install from the same intake."""
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = run / "superseded" / stamp
    if target.exists():
        raise ValueError(f"superseded attempt already exists: {target}")
    target.mkdir(parents=True)
    for name in ("staged", "previous", "withdrawn", "previous-catalog.json"):
        path = run / name
        if _is_reparse_point(path):
            raise ValueError(f"unsafe run journal entry: {path}")
        if path.exists():
            path.rename(target / name)
    _write_json(target / "run.json", plan)
    print(f"Undone install set aside as evidence: {target}", flush=True)


def _refresh_galleries(working, run):
    import gallery_maintenance

    cfg = gallery_maintenance.cw.load_cfg()
    gallery_maintenance.refresh_reports(
        working, gallery_maintenance.folders(cfg, working),
        run / "likeness-cache.json", run / "policy.json",
        gallery_maintenance.cw.storage_root(cfg, "reports", root=working) / "library",
    )


def _core_preview_catalog(working):
    catalog_path = pathlib.Path(working) / ".likeness-library.json"
    if _is_reparse_point(catalog_path):
        raise ValueError(f"unsafe Sandbox-local catalogue: {catalog_path}")
    if not catalog_path.exists():
        return {
            "schemaVersion": 1, "people": {}, "photos": {}, "actions": [],
        }, "no Sandbox-local catalogue; repository catalogue deliberately not used"
    if not catalog_path.is_file():
        raise ValueError(f"unsafe Sandbox-local catalogue: {catalog_path}")
    return metadata.load_catalog(catalog_path), f"Sandbox-local catalogue: {catalog_path}"


def _preview_image_inventory(working):
    image_extensions = {
        ".avif", ".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp",
    }
    categories = ("Sisters", "Angels", "Models", "Prospects", "Potentials", "Various")
    source_rows, derivative_rows, other_rows = [], [], []

    def is_regenerable_derivative(parts, filename):
        for part in (value.casefold() for value in parts):
            if part == "944x1104" or part == "headshots" or part == "_processing":
                return True
            if re.search(r"(?:gallery|review|headshot|chest).*_\d+x\d+(?:_org)?$", part):
                return True
        return bool(re.search(r"(?:_head|_chest)?_944x1104$", pathlib.Path(filename).stem.casefold()))

    for category in categories:
        root = pathlib.Path(working) / category
        if _is_reparse_point(root):
            raise ValueError(f"unsafe baseline category root: {root}")
        if not root.is_dir():
            continue
        for path in _source_files(root):
            if path.suffix.casefold() not in image_extensions:
                continue
            relative = path.relative_to(working).as_posix()
            parts = pathlib.PurePosixPath(relative).parts
            if "_archive" in {part.casefold() for part in parts}:
                continue
            if is_regenerable_derivative(parts[1:-1], path.name):
                derivative_rows.append({
                    "category": category, "source": relative, "bytes": path.stat().st_size,
                })
                continue
            folder_parts = parts[1:-1]
            direct_gallery_review = (
                len(folder_parts) == 2 and folder_parts[-1].casefold() in ("gallery", "review")
            )
            direct_various = (
                category == "Various" and len(folder_parts) == 1
                and folder_parts[0].casefold() in ("gallery", "review")
            )
            nested_various = category == "Various" and not direct_various
            if not (direct_gallery_review or direct_various or nested_various):
                other_rows.append({
                    "category": category, "source": relative, "bytes": path.stat().st_size,
                })
                continue
            source_rows.append({
                "category": category, "source": relative,
                "photoId": metadata.photo_id_from_name(path.name),
                "bytes": path.stat().st_size,
                "inventoryTier": "nested-incoming" if nested_various else "gallery-review",
            })

    def summary(items):
        ids = collections.defaultdict(list)
        unresolved = 0
        for item in items:
            if item["photoId"] is None:
                unresolved += 1
            else:
                ids[item["photoId"]].append(item["source"])
        duplicate_ids = {
            photo_id: sorted(paths) for photo_id, paths in ids.items() if len(paths) > 1
        }
        return {
            "imageFileCount": len(items),
            "uniqueStablePhotoIdCount": len(ids),
            "unresolvedPhotoIdCount": unresolved,
            "duplicateStablePhotoIdCount": len(duplicate_ids),
            "duplicateFileCount": sum(len(paths) - 1 for paths in duplicate_ids.values()),
            "duplicatePhotoIds": [
                {"photoId": photo_id, "sources": paths}
                for photo_id, paths in sorted(duplicate_ids.items())
            ],
        }

    per_category = {
        category: {
            **summary([row for row in source_rows if row["category"] == category]),
            "galleryReviewImageFileCount": sum(
                row["inventoryTier"] == "gallery-review"
                for row in source_rows if row["category"] == category
            ),
            "nestedIncomingImageFileCount": sum(
                row["inventoryTier"] == "nested-incoming"
                for row in source_rows if row["category"] == category
            ),
        }
        for category in categories
    }
    derivative_summary = {
        "imageFileCount": len(derivative_rows),
        "categories": {
            category: sum(row["category"] == category for row in derivative_rows)
            for category in categories
        },
    }
    other_summary = {
        "imageFileCount": len(other_rows),
        "categories": {
            category: sum(row["category"] == category for row in other_rows)
            for category in categories
        },
    }
    return source_rows, summary(source_rows), per_category, derivative_summary, other_summary


def core_selection_preview(working, catalog, policy, recipe, *, catalog_source=None):
    """Review current Sandbox candidate metadata without face analysis or intake."""
    working = pathlib.Path(working)
    (
        baseline_files, baseline_summary, category_summaries,
        derivative_summary, other_summary,
    ) = _preview_image_inventory(working)
    ids_by_source = {
        row["source"]: row["photoId"] for row in baseline_files
    }
    id_counts = collections.Counter(
        row["photoId"] for row in baseline_files if row["photoId"] is not None
    )
    people_by_folder = {
        person["folder"]: (person_id, person) for person_id, person in catalog["people"].items()
        if not person.get("mergedInto")
    }
    photos = catalog.get("photos", {})
    groups = catalog.get("photoGroups", {})
    candidates = []
    for item in baseline_files:
        relative = item["source"]
        parts = pathlib.PurePosixPath(relative).parts
        if (not parts or parts[0] not in ("Angels", "Sisters") or "gallery" not in parts
                or parts.index("gallery") != len(parts) - 2 or "_processing" in parts):
            continue
        digest = metadata.content_sha256(working / pathlib.Path(relative))
        folder = "/".join(parts[:parts.index("gallery")])
        pid = ids_by_source[relative]
        owner = people_by_folder.get(folder)
        person_id, person = owner if owner else (None, None)
        record = photos.get(pid, {}) if pid else {}
        provenance = record.get("protectionProvenance")
        proof_ids = set((provenance or {}).get("frozenCorePhotoIds", []))
        proof_current = bool(
            provenance and provenance.get("recipeVersion") == "independent-gallery-loo-v1"
            and pid in proof_ids and record.get("contentSha256") == digest
        )
        anchor = bool(pid and person and pid in person.get("identityAnchors", []))
        content_matched_anchor = bool(anchor and record.get("contentSha256") == digest)
        supported_core = bool(
            pid and record.get("membership", {}).get("status") == "supported"
            and record.get("membership", {}).get("coreUse")
            and record.get("membership", {}).get("personId") == person_id
            and record.get("contentSha256") == digest
        )
        group_refs = sorted(
            group_id for group_id, group in groups.items()
            if group.get("status") == "supported" and group.get("personId") == person_id
            and pid in group.get("referencePhotoIds", [])
            and record.get("contentSha256") == digest
            and record.get("membership", {}).get("status") == "supported"
            and record.get("membership", {}).get("coreUse")
        )
        legacy_protected = bool(record.get("protected") and not provenance)
        sources = []
        if anchor:
            sources.append("authored identity anchor")
        if supported_core:
            sources.append("saved supported core-use membership")
        if proof_current:
            sources.append("content-matched automatic protection core")
        if group_refs:
            sources.append("supported appearance reference: " + ", ".join(group_refs))
        if legacy_protected:
            sources.append("legacy protected placement; not automatic reference evidence")
        if not sources:
            sources.append("unmarked Gallery member; candidate only")
        candidates.append({
            "photoId": pid, "source": relative, "identityFolder": folder,
            "personId": person_id, "candidateSources": sources,
            "contentSha256": digest, "byteLength": item["bytes"],
            "stableIdStatus": (
                "unresolved" if pid is None else
                "duplicate-stable-id" if id_counts[pid] > 1 else "unique-stable-id"
            ),
            "authoredIdentityAnchor": anchor,
            "identityAnchorContentMatched": content_matched_anchor,
            "savedSupportedCoreUse": supported_core,
            "protectionProvenanceCoreCandidate": proof_current,
            "legacyProtectedPlacementHold": legacy_protected,
            "staleOrUnqualifiedProtectionProvenance": bool(provenance and not proof_current),
            "measurementEligibility": "not measured; face count, quality, vectors, and independent support are unknown",
            "selection": "candidate only; requires human review",
        })
    counts = collections.Counter(
        source for row in candidates for source in row["candidateSources"]
    )
    return {
        "kind": "directed-core-selection-candidate-preview",
        "baselineRoot": str(working.resolve()),
        "scope": (
            "The six active photo categories count source photos, regenerable derivatives, and other "
            "images separately; only Angels/Sisters direct Gallery rows are core candidates. Various "
            "is incoming mixed intake, not a core source. Read-only."
        ),
        "catalogSource": catalog_source or "caller-supplied catalogue",
        "baselineInventory": {
            **baseline_summary,
            "sourcePhotoCount": baseline_summary["imageFileCount"],
            "allImageFileCount": (
                baseline_summary["imageFileCount"] + derivative_summary["imageFileCount"]
                + other_summary["imageFileCount"]
            ),
            "categories": category_summaries,
            "regenerableDerivatives": derivative_summary,
            "otherNonSourceImages": other_summary,
            "truncated": False, "selectionCap": None,
        },
        "incomingVarious": {
            **category_summaries["Various"],
            "sourcePhotoCount": category_summaries["Various"]["imageFileCount"],
            "role": "incoming mixed intake; excluded from core/reference candidates",
        },
        "photoCount": len(candidates),
        "candidatePhotoCount": len(candidates),
        "candidateIdSummary": {
            "unresolvedPhotoIdCount": sum(row["photoId"] is None for row in candidates),
            "duplicateStablePhotoIdCount": len({
                row["photoId"] for row in candidates
                if row["photoId"] is not None and id_counts[row["photoId"]] > 1
            }),
        },
        "candidateSourceCounts": dict(sorted(counts.items())),
        "policyCastCoreThresholds": {
            category: {
                "identityCoreMinimumSimilarity": policy["categoryPolicies"][category][
                    "identityCoreMinimumSimilarity"
                ],
                "minimumUsablePhotosForOutlierActions": policy["categoryPolicies"][category][
                    "minimumUsablePhotosForOutlierActions"
                ],
            }
            for category in ("Angels", "Sisters")
        },
        "directedRecipe": {
            "name": recipe["name"], "core": copy.deepcopy(recipe["core"]),
            "admission": copy.deepcopy(recipe["admission"]),
            "retention": copy.deepcopy(recipe["retention"]),
            "strongRelease": copy.deepcopy(recipe["strongRelease"]),
            "joinSupport": recipe["joinSupport"], "coreSupport": recipe["coreSupport"],
            "retainSupport": recipe["retainSupport"], "referenceSupport": recipe["referenceSupport"],
            "sameIdentityMargin": copy.deepcopy(recipe["sameIdentityMargin"]),
        },
        "measuredEligibility": "not evaluated; this preview does not establish a trusted core",
        "workflowSelection": "not read; workflow intent is evaluated only by the matched run",
        "photos": candidates,
    }


def write_core_selection_preview(report, output_dir):
    """Write a JSON receipt and original-backed local HTML candidate viewer."""
    output_dir = pathlib.Path(output_dir)
    if _is_reparse_point(output_dir):
        raise ValueError(f"unsafe candidate preview output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "core-selection-preview.json"
    html_path = output_dir / "core-selection-preview.html"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    def format_count(value):
        return f"{value:,}"

    def category_row(category, values):
        label = category + (
            " (incoming mixed intake; excluded from core)" if category == "Various" else ""
        )
        return (
            "<tr><th>" + html.escape(label) + "</th><td>"
            + format_count(values["galleryReviewImageFileCount"]) + "</td><td>"
            + format_count(values["nestedIncomingImageFileCount"]) + "</td><td>"
            + format_count(values["uniqueStablePhotoIdCount"]) + "</td><td>"
            + format_count(values["unresolvedPhotoIdCount"]) + "</td><td>"
            + format_count(values["duplicateStablePhotoIdCount"]) + "</td></tr>"
        )

    def render_duplicate(item):
        return (
            "<li><code>" + html.escape(item["photoId"]) + "</code>: "
            + html.escape(" | ".join(item["sources"])) + "</li>"
        )

    duplicate_limit = 50
    duplicates = report["baselineInventory"]["duplicatePhotoIds"]
    duplicate_rows = "".join(render_duplicate(item) for item in duplicates[:duplicate_limit])
    if not duplicate_rows:
        duplicate_rows = "<li>None detected among original-source photos.</li>"
    duplicate_note = (
        f"<p>Showing at most {duplicate_limit:,} of {len(duplicates):,} source-photo duplicate IDs; "
        "the JSON receipt contains the complete list.</p>"
        if len(duplicates) > duplicate_limit else
        f"<p>Complete source-photo duplicate list ({len(duplicates):,} IDs).</p>"
    )
    categories = report["baselineInventory"]["categories"]
    category_rows = "".join(category_row(category, values) for category, values in categories.items())
    derivative_rows = "".join(
        "<tr><th>" + html.escape(category) + "</th><td>"
        + format_count(count) + "</td></tr>"
        for category, count in report["baselineInventory"]["regenerableDerivatives"]["categories"].items()
    )
    other_rows = "".join(
        "<tr><th>" + html.escape(category) + "</th><td>"
        + format_count(count) + "</td></tr>"
        for category, count in report["baselineInventory"]["otherNonSourceImages"]["categories"].items()
    )
    cards = []
    for row in report["photos"]:
        source = pathlib.PurePosixPath(row["source"])
        image_uri = (pathlib.Path(report["baselineRoot"]) / pathlib.Path(*source.parts)).resolve().as_uri()
        cards.append({**row, "imageUrl": image_uri})
    card_data = json.dumps(cards, ensure_ascii=False).replace("<", "\\u003c").replace(
        ">", "\\u003e",
    ).replace("&", "\\u0026")
    recipe = report["directedRecipe"]
    recipe_rows = "".join(
        "<tr><th>" + html.escape(category) + "</th><td>" + html.escape(str(recipe["core"][category]))
        + "</td><td>" + html.escape(str(recipe["admission"][category])) + "</td><td>"
        + html.escape(str(recipe["retention"][category])) + "</td><td>"
        + html.escape(str(recipe["sameIdentityMargin"][category])) + "</td></tr>"
        for category in recipe["core"]
    )
    policy_rows = "".join(
        "<tr><th>" + html.escape(category) + "</th><td>"
        + html.escape(str(values["identityCoreMinimumSimilarity"])) + "</td><td>"
        + html.escape(str(values["minimumUsablePhotosForOutlierActions"])) + "</td></tr>"
        for category, values in report["policyCastCoreThresholds"].items()
    )
    identities = collections.Counter(row["identityFolder"] for row in report["photos"])
    identity_options = "".join(
        "<option value=\"" + html.escape(folder, quote=True) + "\">"
        + html.escape(folder) + " (" + format_count(count) + ")</option>"
        for folder, count in sorted(identities.items())
    )
    source_count = report["baselineInventory"]["sourcePhotoCount"]
    derivative_count = report["baselineInventory"]["regenerableDerivatives"]["imageFileCount"]
    other_count = report["baselineInventory"]["otherNonSourceImages"]["imageFileCount"]
    page = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Directed core selection candidates</title>
<style>
*{{box-sizing:border-box}} body{{font:14px/1.45 system-ui,sans-serif;margin:0;color:#222}}
main{{max-width:1280px;margin:0 auto;padding:clamp(.65rem,2vw,1.5rem);min-width:0}}
table{{border-collapse:collapse;width:100%}} .table-wrap{{max-width:100%;overflow-x:auto}}
th,td{{border:1px solid #bbb;padding:.4rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}}
code{{overflow-wrap:anywhere;word-break:break-word}} .warning{{background:#fff3cd;padding:.8rem}}
.small{{font-size:12px;color:#444}} details{{margin:.7rem 0}} summary{{cursor:pointer;font-weight:600}}
.filters,.pager{{display:flex;align-items:center;gap:.65rem;flex-wrap:wrap;margin:.8rem 0}}
label{{display:flex;align-items:center;gap:.35rem}} select,button{{font:inherit;padding:.45rem;max-width:100%}}
#cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:1rem}}
.card{{border:1px solid #bbb;border-radius:.4rem;padding:.65rem;min-width:0;overflow:hidden}}
.card img{{display:block;width:100%;height:auto;max-height:60vh;object-fit:contain;background:#f2f2f2}}
.card h3{{font-size:1rem;margin:.5rem 0}} .card p{{margin:.25rem 0;overflow-wrap:anywhere}}
.hash{{font-size:.75rem;color:#555}} button:disabled{{opacity:.45}}
@media(max-width:480px){{main{{padding:.5rem}} .filters label{{width:100%;align-items:flex-start;flex-direction:column}}}}
</style><body><main>
<h1>Directed core candidate review</h1>
<p class="warning">Candidate metadata only. No face quality, measurements, independent support,
workflow selection, or trusted-core decision was evaluated. Various is incoming mixed intake,
not a core/reference source. No matching or intake was run.</p>
<p>Baseline: <code>{html.escape(report["baselineRoot"])}</code><br>
Catalogue: {html.escape(report["catalogSource"])}</p>
<h2>Source-photo inventory (all counts complete; no cap or truncation)</h2>
<p>{format_count(source_count)} source photo files (including Various nested incoming);
{format_count(report["baselineInventory"]["uniqueStablePhotoIdCount"])} unique filename-derived IDs;
{format_count(report["baselineInventory"]["unresolvedPhotoIdCount"])} unresolved IDs;
{format_count(report["baselineInventory"]["duplicateStablePhotoIdCount"])} duplicate IDs among source photos.
Regenerable derivatives are counted separately ({format_count(derivative_count)}); other non-source
images are separate ({format_count(other_count)}). Neither contributes to source duplicate counts.</p>
<div class="table-wrap"><table><thead><tr><th>Category</th><th>Direct Gallery/Review sources</th>
<th>Nested Various incoming</th><th>Unique source IDs</th><th>Unresolved source IDs</th>
<th>Duplicate source IDs</th></tr></thead><tbody>{category_rows}</tbody></table></div>
<details><summary>Source-photo duplicate IDs ({format_count(len(duplicates))}; complete list in JSON)</summary>
{duplicate_note}<ul>{duplicate_rows}</ul></details>
<details><summary>Regenerable derivative image inventory ({format_count(derivative_count)})</summary>
<div class="table-wrap"><table><thead><tr><th>Category</th><th>Derivative files</th></tr></thead>
<tbody>{derivative_rows}</tbody></table></div></details>
<details><summary>Other non-source image inventory ({format_count(other_count)})</summary>
<div class="table-wrap"><table><thead><tr><th>Category</th><th>Other files</th></tr></thead>
<tbody>{other_rows}</tbody></table></div></details>
<details><summary>Recipe and configured thresholds (comparison only)</summary>
<h2>Selected experimental recipe: {html.escape(recipe["name"])}</h2>
<div class="table-wrap"><table><thead><tr><th>Category</th><th>Core</th><th>Admission</th><th>Retention</th>
<th>Same-identity margin</th></tr></thead><tbody>{recipe_rows}</tbody></table></div>
<p>Strong release source/destination/margin: {recipe["strongRelease"]["sourceMaximum"]}/
{recipe["strongRelease"]["destinationMinimum"]}/{recipe["strongRelease"]["signedMargin"]}.
Independent support: join {recipe["joinSupport"]}, core {recipe["coreSupport"]},
retention {recipe["retainSupport"]}, references {recipe["referenceSupport"]}.</p>
<h3>Configured cast-core policy thresholds</h3>
<div class="table-wrap"><table><thead><tr><th>Category</th><th>Identity core minimum</th>
<th>Minimum usable photos for outlier actions</th></tr></thead><tbody>{policy_rows}</tbody></table></div>
</details>
<h2>Angels/Sisters Gallery candidates ({report["candidatePhotoCount"]})</h2>
<p class="small">Only visible page cards are created in the DOM. All {report["candidatePhotoCount"]}
candidate records remain in this viewer and the complete JSON receipt; each image links directly
to its original source bytes. Hashes bind the preview to observed bytes, not identity correctness.</p>
<div class="filters">
<label>Category <select id="category-filter"><option value="">All cast categories</option>
<option value="Angels">Angels</option><option value="Sisters">Sisters</option></select></label>
<label>Identity <select id="identity-filter"><option value="">All cast identities</option>
{identity_options}</select></label>
</div>
<div class="pager"><button id="previous-page" type="button">Previous</button>
<span id="page-status" aria-live="polite"></span>
<button id="next-page" type="button">Next</button></div>
<section id="cards" aria-live="polite"></section>
<div class="pager"><button id="previous-page-bottom" type="button">Previous</button>
<span id="page-status-bottom" aria-live="polite"></span>
<button id="next-page-bottom" type="button">Next</button></div>
<script id="candidate-data" type="application/json">{card_data}</script>
<script>
(() => {{
  const rows = JSON.parse(document.getElementById("candidate-data").textContent);
  const pageSize = 24;
  let pageIndex = 0;
  const category = document.getElementById("category-filter");
  const identity = document.getElementById("identity-filter");
  const cards = document.getElementById("cards");
  const previous = [document.getElementById("previous-page"), document.getElementById("previous-page-bottom")];
  const next = [document.getElementById("next-page"), document.getElementById("next-page-bottom")];
  const statuses = [document.getElementById("page-status"), document.getElementById("page-status-bottom")];
  const filtered = () => rows.filter(row =>
    (!category.value || row.identityFolder.split("/")[0] === category.value) &&
    (!identity.value || row.identityFolder === identity.value));
  const addText = (parent, tag, text, className) => {{
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    parent.appendChild(node);
    return node;
  }};
  const render = () => {{
    const selection = filtered();
    const pageCount = Math.max(1, Math.ceil(selection.length / pageSize));
    pageIndex = Math.min(pageIndex, pageCount - 1);
    const start = pageIndex * pageSize;
    cards.replaceChildren();
    for (const row of selection.slice(start, start + pageSize)) {{
      const card = document.createElement("article");
      card.className = "card";
      const image = document.createElement("img");
      image.src = row.imageUrl;
      image.alt = row.source;
      image.loading = "eager";
      image.decoding = "async";
      card.appendChild(image);
      addText(card, "h3", row.identityFolder);
      addText(card, "p", row.photoId || "Unresolved filename-derived ID");
      addText(card, "p", row.stableIdStatus + " · " + row.selection);
      addText(card, "p", row.source);
      addText(card, "p", "Metadata: " + row.candidateSources.join("; "));
      addText(card, "p", "SHA-256 " + row.contentSha256, "hash");
      cards.appendChild(card);
    }}
    const status = selection.length
      ? `Showing ${{start + 1}}–${{Math.min(start + pageSize, selection.length)}} of ${{selection.length}} candidates · page ${{pageIndex + 1}} of ${{pageCount}}`
      : "No candidates match these filters.";
    statuses.forEach(node => node.textContent = status);
    previous.forEach(button => button.disabled = pageIndex === 0);
    next.forEach(button => button.disabled = pageIndex >= pageCount - 1);
  }};
  previous.forEach(button => button.addEventListener("click", () => {{ pageIndex--; render(); }}));
  next.forEach(button => button.addEventListener("click", () => {{ pageIndex++; render(); }}));
  category.addEventListener("change", () => {{ pageIndex = 0; render(); }});
  identity.addEventListener("change", () => {{ pageIndex = 0; render(); }});
  render();
}})();
</script></main></body></html>"""
    html_path.write_text(page, encoding="utf-8")
    return {"json": str(json_path.resolve()), "html": str(html_path.resolve())}


def command(args, api):
    if sum(bool(flag) for flag in (args.apply, args.check, args.dry_run, args.undo, args.replan)) > 1:
        raise ValueError("choose only one of --apply, --check, --dry-run, --undo, or --replan")
    cast_seeds = getattr(args, "cast_seeds", "all")
    if cast_seeds not in {"all", "core"}:
        raise ValueError("--cast-seeds must be all or core")
    reset_mode = getattr(args, "workflow_reset", None)
    if reset_mode is not None and cast_seeds != "core":
        raise ValueError("--workflow-reset requires --cast-seeds core")
    workflow_reset = {"mode": reset_mode or "all"}
    if reset_mode == "scoped":
        workflow_reset["slots"] = getattr(args, "workflow_reset_slot", [])
    if reset_mode == "low-score":
        workflow_reset["maximumOwnCoreSimilarity"] = getattr(args, "workflow_reset_cutoff", None)
    policy = load_policy(args.policy)
    if getattr(args, "record_core_protection", False):
        if cast_seeds != "core":
            raise ValueError("--record-core-protection requires --cast-seeds core")
        policy = core_protection_policy(policy)
    if policy.get("rebaseProtection", {}).get("enabled") and cast_seeds != "core":
        raise ValueError("enabled rebase protection policy requires --cast-seeds core")
    layout = validate_sandbox(args.root)
    run = require_sandbox_output(args.root, args.run_dir)
    if run == layout["working_root"] or any(
        run == layout["working_root"] / category
        or layout["working_root"] / category in run.parents
        for category in (*RESET_CATEGORIES, "Various", "Angels", "Sisters", "Artists")
    ):
        raise ValueError("run directory must be outside identity category roots")
    intake_only = getattr(args, "intake_only", False)
    storage_mode = getattr(args, "storage_mode", None)
    profile = getattr(args, "profile", None)
    regroup = getattr(args, "regroup", False)
    review_source = getattr(args, "review_source", None)
    directed = getattr(args, "directed", False)
    directed_recipe = getattr(args, "directed_recipe", None)
    core_selection_preview_requested = getattr(args, "core_selection_preview", False)
    if review_source and not regroup:
        raise ValueError("--review-source requires --regroup")
    if regroup and cast_seeds != "core":
        raise ValueError("--regroup requires --cast-seeds core")
    if directed and not regroup:
        raise ValueError("--directed requires --regroup")
    if directed and not directed_recipe:
        raise ValueError("--directed requires an explicit --directed-recipe")
    if directed_recipe and not directed:
        raise ValueError("--directed-recipe requires --directed")
    if directed:
        from . import directed_reformation

        directed_recipe = directed_reformation.recipe_named(directed_recipe)["name"]
    if core_selection_preview_requested and not (
        args.dry_run and directed and regroup and cast_seeds == "core"
    ):
        raise ValueError("--core-selection-preview requires --dry-run --regroup --cast-seeds core --directed")
    if regroup and not directed:
        from .group_lifecycle import runtime_policy
        policy = runtime_policy(policy)
    if profile not in (None, "fast", "lean", "full"):
        raise ValueError("profile must be fast, lean or full")
    processing_profile = None if profile is None else "fast" if profile == "fast" else "standard"
    if profile in ("lean", "full"):
        if storage_mode is not None and storage_mode != profile:
            raise ValueError("--profile and --storage-mode differ")
        storage_mode = profile
    recovery_mode = getattr(args, "recovery_mode", None)
    if recovery_mode not in (None, "full", "disposable"):
        raise ValueError("recovery mode must be full or disposable")
    if recovery_mode == "disposable" and storage_mode == "full":
        raise ValueError("disposable sandbox recovery requires LEAN storage")
    if storage_mode not in (None, "full", "lean"):
        raise ValueError("storage mode must be full or lean")
    resume_install = getattr(args, "resume_install", False)
    preserve_legacy = getattr(args, "preserve_legacy_derivatives", False)
    if resume_install and (intake_only or not (args.check or args.apply)):
        raise ValueError("--resume-install requires --check or --apply without --intake-only")
    if preserve_legacy and not (args.check or args.apply):
        raise ValueError("--preserve-legacy-derivatives requires --check or --apply")
    include_various = getattr(args, "include_current_various", False)
    baseline = getattr(args, "baseline", None)
    if baseline not in {None, "source", "working"}:
        raise ValueError("--baseline must be source or working")
    current_working = baseline == "working"
    include_various = include_various or current_working
    if intake_only and (args.undo or args.replan):
        raise ValueError("--intake-only cannot undo or replan matching")
    if args.dry_run:
        if core_selection_preview_requested:
            catalog, catalog_source = _core_preview_catalog(layout["working_root"])
            report = core_selection_preview(
                layout["working_root"], catalog, policy,
                directed_reformation.recipe_named(directed_recipe),
                catalog_source=catalog_source,
            )
            report_paths = write_core_selection_preview(report, run / "core-selection-preview")
            summary = {
                "status": "core-selection-preview",
                "directedMode": "experimental-directed-sandbox; preview only",
                "recipe": report["directedRecipe"]["name"],
                "candidatePhotoCount": report["candidatePhotoCount"],
                "baselineSourcePhotoCount": report["baselineInventory"]["sourcePhotoCount"],
                "baselineAllImageFileCount": report["baselineInventory"]["allImageFileCount"],
                "regenerableDerivativeImageCount": report["baselineInventory"][
                    "regenerableDerivatives"
                ]["imageFileCount"],
                "unresolvedPhotoIdCount": report["baselineInventory"]["unresolvedPhotoIdCount"],
                "duplicateStablePhotoIdCount": report["baselineInventory"]["duplicateStablePhotoIdCount"],
                "incomingVariousImageFileCount": report["incomingVarious"]["imageFileCount"],
                "incomingVariousNestedImageFileCount": report["incomingVarious"][
                    "nestedIncomingImageFileCount"
                ],
                "truncated": False,
                "reportPaths": report_paths,
            }
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return summary
        if include_various:
            if current_working:
                baseline_layout, baseline_rows = _working_baseline(layout)
                rows, current = _current_various_overlay_rows(baseline_layout, baseline_rows)
            else:
                rows, current = _current_various_overlay_rows(layout)
            total = len(set(rows) | {item["target"] for item in current})
            replaced = sum(1 for item in current if item["target"] in rows and rows[item["target"]] != item["sha256"])
            added = sum(1 for item in current if item["target"] not in rows)
            print(
                f"Clean-start preview: {len(rows)} {'current Working assigned' if current_working else 'immutable'} "
                f"images plus {added} new current Various "
                f"images = {total} preparation outcomes; {replaced} baseline IDs use newer Various bytes."
            )
        else:
            rows = clean_preparation.inventory(layout)
            print(f"Clean-start preview: {len(rows)} immutable images will receive preparation outcomes.")
        print("No images, reports, caches or models changed.")
        if profile is not None:
            print(f"Profile: {profile.upper()}; recovery: {recovery_mode or 'full'} (separate contract).")
        if cast_seeds == "all":
            print("Cast-seed policy: all. The matched preview will retain existing cast membership.")
        else:
            print(
                "Cast-seed policy: core. The matched preview will evaluate protected/core/workflow-selected "
                "cast retention and eligible releases under configured thresholds."
            )
        print("Inventory only: no cast retention/release decisions or matching were evaluated.")
        print("Use --intake-only --apply to prepare and stop, or omit --dry-run for a full matched preview.")
        return {"status": "inventory", "inputCount": total if include_various else len(rows)}
    if intake_only and not (args.apply or args.check):
        if include_various:
            if current_working:
                baseline_layout, baseline_rows = _working_baseline(layout)
                rows, current = _current_various_overlay_rows(baseline_layout, baseline_rows)
            else:
                rows, current = _current_various_overlay_rows(layout)
            total = len(set(rows) | {item["target"] for item in current})
        else:
            rows = clean_preparation.inventory(layout)
            total = len(rows)
        print(f"Intake preview: {total} inputs; use --intake-only --apply to write sidecars.")
        return {"status": "inventory", "inputCount": total}
    if args.check or args.undo or args.replan or resume_install:
        if not run.is_dir():
            raise ValueError("no saved clean-start run exists")
    else:
        run.mkdir(parents=True, exist_ok=True)
    overlay_path = run / "source-overlay"
    if overlay_path.exists():
        layout = _verify_source_overlay(layout, run)
        saved_baseline = layout["source_overlay_manifest"].get("baselineMode", "source")
        if baseline is not None and baseline != saved_baseline:
            raise ValueError("saved run baseline differs; use the same baseline or a new run")
    elif include_various and not (args.check or args.undo or args.replan):
        layout = _create_source_overlay(layout, run, current_working=current_working)
    plan_path = run / "run.json"
    if (run / "intake.json").exists():
        saved_intake = json.loads((run / "intake.json").read_text(encoding="utf-8"))
        saved_profile = saved_intake.get("processingProfile", "standard")
        if processing_profile is not None and processing_profile != saved_profile:
            raise ValueError("saved intake processing profile differs; use a new run")
        processing_profile = saved_profile
        saved_recovery = saved_intake.get("recoveryMode", "full")
        if recovery_mode is not None and recovery_mode != saved_recovery:
            raise ValueError("saved intake recovery mode differs; use the saved mode or a new run")
        recovery_mode = saved_recovery
    if storage_mode is not None and (run / "intake.json").exists():
        _, saved_preparation = clean_preparation.verify(layout, run)
        if saved_preparation.get("storageMode", "full") != storage_mode:
            raise ValueError("saved intake storage mode differs; use the saved mode or a new run")
    if intake_only or args.check and not plan_path.exists():
        if args.check:
            output, data = clean_preparation.verify(layout, run)
        elif args.apply:
            had_intake = (run / "intake.json").is_file()
            output, data = clean_preparation.prepare(
                layout, run, getattr(args, "workers", None), storage_mode=storage_mode,
                recovery_mode=recovery_mode, processing_profile=processing_profile)
            from . import preparation_history

            storage_cfg = api.cw.load_cfg()
            reports_root = api.cw.storage_root(
                storage_cfg, "reports", root=layout["working_root"]
            )
            if not had_intake:
                preparation_history.publish_staged(
                    layout["working_root"], reports_root / "library", cfg=storage_cfg
                )
        print(f"Intake verified: {len(data['photos'])} outcomes. Review {output / 'index.html'}")
        print("Stopped before matching/assignment. The same run resumes without repeating preparation.")
        return {"status": "intake", "inputCount": len(data["photos"]), "report": str(output / "index.html")}
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if regroup != bool(plan.get("groupLifecycle")) and not (args.check or args.undo):
            raise ValueError("saved run regrouping mode differs; repeat --regroup or use a new run")
        saved_directed = plan.get("directedReformation", {"enabled": False, "recipe": None})
        expected_directed = {"enabled": bool(directed), "recipe": directed_recipe}
        if saved_directed != expected_directed:
            raise ValueError("saved directed reformation mode or recipe differs; repeat the same flags or use a new run")
        if (
            cast_seeds == "core" and not (args.replan or args.undo or args.check)
            and (plan.get("workflowSelection") or {}).get("policy") != workflow_reset
        ):
            raise ValueError("saved workflow reset differs or is unbound; create a new matching preview")
        if recovery_mode is not None and recovery_mode != plan.get("recoveryMode", "full"):
            raise ValueError("saved run recovery mode differs; use the saved mode or a new run")
        if (
            (plan["policy"] != policy or plan.get("castSeedPolicy", "all") != cast_seeds)
            and not (args.replan or args.undo or args.check)
        ) or plan["workingRoot"] != str(layout["working_root"]):
            raise ValueError("saved plan policy, cast-seed mode, or root differs; use a new run directory")
        if plan["sourceManifestSHA256"] != metadata.content_sha256(layout["sandbox_root"] / "source-manifest.json"):
            raise ValueError("source manifest changed since preview")
        if plan.get("sourceOverlaySHA256") != layout.get("source_overlay_sha256"):
            raise ValueError("saved plan source overlay differs; use the same verified overlay")
        if args.replan:
            saved_recovery_mode = plan.get("recoveryMode", "full")
            if (
                plan["status"] not in ("preview", "undone") or not plan["embeddingCacheStartedEmpty"]
                or plan["embeddingCache"] != str(run / "likeness-cache.json")
            ):
                raise ValueError("only a fresh-cache preview or an undone install can be replanned")
            if plan["status"] == "undone":
                _set_aside_undone_attempt(run, plan)
            _verify_routes(plan, layout["source_root"])
            original_preview = run / "initial-preview.json"
            if not original_preview.exists():
                _write_json(original_preview, plan)
            plan = create_plan(
                layout, run, policy, api, getattr(args, "embedder", None),
                reuse_measurements=True,
                preparation=clean_preparation.verify(layout, run) if plan.get("preparation") else None,
                cast_seeds=cast_seeds,
                workflow_reset=workflow_reset,
                regroup=regroup,
                review_source=review_source,
                directed_recipe=directed_recipe,
            )
            plan["recoveryMode"] = recovery_mode or saved_recovery_mode
            _write_json(plan_path, plan)
    else:
        if args.check or args.undo:
            raise ValueError("no saved clean rebase plan exists")
        if args.apply:
            raise ValueError("create and review the prepared matching preview before --apply")
        if args.replan and not ((run / "intake.json").is_file() and (run / "likeness-cache.json").is_file()):
            raise ValueError("resuming incomplete matching requires verified preparation and saved measurements")
        had_intake = (run / "intake.json").is_file()
        preparation = clean_preparation.prepare(
            layout, run, getattr(args, "workers", None), storage_mode=storage_mode,
            recovery_mode=recovery_mode, processing_profile=processing_profile)
        from . import preparation_history

        storage_cfg = api.cw.load_cfg()
        reports_root = api.cw.storage_root(
            storage_cfg, "reports", root=layout["working_root"]
        )
        if not had_intake:
            preparation_history.publish_staged(
                layout["working_root"], reports_root / "library", cfg=storage_cfg
            )
        plan = create_plan(
            layout, run, policy, api, getattr(args, "embedder", None),
            reuse_measurements=args.replan, preparation=preparation,
            cast_seeds=cast_seeds,
            workflow_reset=workflow_reset,
            regroup=regroup,
            review_source=review_source,
            directed_recipe=directed_recipe,
        )
        plan["recoveryMode"] = recovery_mode or "full"
        if plan["recoveryMode"] == "disposable":
            _require_disposable_sandbox(layout, run, plan)
        _write_json(plan_path, plan)
    if plan.get("preparation"):
        verified = _phase_timer("Plan")
        output, verified_data = clean_preparation.verify(layout, run)
        if (plan["preparation"].get("processingProfile", "standard")
                != verified_data.get("processingProfile", "standard")):
            raise ValueError("saved plan processing profile differs from intake")
        if metadata.content_sha256(output / "manifest.json") != plan["preparation"]["manifestSHA256"]:
            raise ValueError("prepared inputs changed since matching; use a new run")
        verified("preparation evidence verification")
    elif args.apply:
        raise ValueError("matcher-only previews cannot be installed; create a new intake-aware run")
    _verify_routes(plan, layout["source_root"])
    if args.apply or args.check or resume_install:
        _verify_implementation_hashes(plan)
    for path, digest in plan.get("reviewEvidenceBindings", {}).items():
        if metadata.content_sha256(path) != digest:
            raise ValueError(f"bound human evidence changed since preview: {path}")
    if args.check and (resume_install or preserve_legacy):
        if plan["status"] != "preview":
            raise ValueError("installation recovery preview requires an unpublished plan; use ordinary --check")
        if resume_install:
            verify_staged_install(layout, run, plan)
        _prior_external_files(layout["working_root"], plan, preserve_legacy=preserve_legacy)
        return {"status": "staged-verified" if resume_install else "legacy-preservation-preview"}
    if args.apply:
        if plan["status"] == "applied":
            _check_publication(layout["working_root"], plan)
            if plan.get("recoveryMode") == "disposable" and not plan.get("rollbackRetired"):
                retire_disposable_rollback(layout, run, plan)
        else:
            install_plan(layout, run, plan, resume_install=resume_install, preserve_legacy=preserve_legacy)
        _write_json(run / "policy.json", plan["policy"])
        refresh = _phase_timer("Apply")
        _refresh_galleries(layout["working_root"], run)
        refresh("gallery, overview and Review refresh")
    if args.undo:
        undo_plan(layout, run, plan)
    if args.check and plan["status"] == "applied":
        _check_publication(layout["working_root"], plan)
    if not args.check:
        _write_json(run / "policy.json", plan["policy"])
        cast_seed_thresholds = plan.get("castSeedThresholds", {
            category: {
                "identityCoreMinimumSimilarity": plan["policy"]["categoryPolicies"][category][
                    "identityCoreMinimumSimilarity"
                ],
                "minimumUsablePhotosForOutlierActions": plan["policy"]["categoryPolicies"][category][
                    "minimumUsablePhotosForOutlierActions"
                ],
            }
            for category in ("Angels", "Sisters")
        })
        cast_seed_usability = plan.get("castSeedUsability", {
            "minimumFacePixels": plan["settings"]["minFace"],
            "multiFaceRatio": plan["settings"].get("multiFace"),
            "qualityGate": "configured junk_reason plus usable face vector",
        })
        with (run / "photos.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            fields = (
                "source", "destination", "photoId", "sha256", "bestMatch", "bestScore",
                "score", "initialBestCast", "initialBestCastScore", "initialSecondCast",
                "initialCastMargin", "reason", "retainedCast", "releasedCast",
                "castSeedScore", "castSeedThreshold", "castSeedUsableCount",
                "castSeedMinimumUsablePhotos", "castSeedCore", "castSeedAnchor",
                "castSeedProtectedIdentity", "castSeedProtectedPhoto",
                "castSeedWorkflowSelected", "castSeedDecision", "castSeedReason",
                "castSeedQualityReason",
                "preparedSHA256", "preparedPath", "preparationOutcome",
                "photoIdOrigin",
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
            f"Cast seed policy: {plan.get('castSeedPolicy', 'all')}",
            f"Policy: {plan['policy']['version']}",
            f"Candidate clustering minimum: {plan['policy']['identityActions']['identityClusterMinimumSimilarity']}",
            "",
            "Every source, destination, hash, match score, and reason is in photos.csv.",
            "The exact policy, centering mean, references, and per-photo decisions are in run.json.",
            "Review additions never enter an Angel/Sister gallery or identity core.",
            "",
            "Cast-seed decisions, source scores, protection/workflow conflicts and actual thresholds "
            "are recorded per photo in photos.csv.",
            ("Disposable sandbox: no baseline backup or post-publication undo; recover by full reset."
             if plan.get("recoveryMode") == "disposable"
             else "Previous category directories are retained in previous/ after installation."),
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
            *[
                f"| {category} identity-core minimum similarity | "
                f"{cast_seed_thresholds[category]['identityCoreMinimumSimilarity']} |"
                for category in ("Angels", "Sisters")
            ],
            *[
                f"| {category} minimum usable photos for outlier actions | "
                f"{cast_seed_thresholds[category]['minimumUsablePhotosForOutlierActions']} |"
                for category in ("Angels", "Sisters")
            ],
            f"| Minimum usable face pixels | {cast_seed_usability['minimumFacePixels']} |",
            f"| Second-face size ratio | {cast_seed_usability['multiFaceRatio']} |",
            "",
            "## Cast seed outcomes",
            "",
            "| Outcome | Photos |",
            "| --- | ---: |",
            *[
                f"| {name} | {count} |"
                for name, count in sorted(collections.Counter(
                    row.get("castSeedDecision", "retained-default")
                    for row in plan["photos"] if row.get("retainedCast") or row.get("releasedCast")
                ).items())
            ],
            "",
            "The per-photo audit lists all retained, released, protected, workflow-selected, and "
            "Review outcomes before apply. No threshold is adjusted to avoid Review.",
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
