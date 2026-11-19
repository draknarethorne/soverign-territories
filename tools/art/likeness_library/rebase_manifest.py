"""Build a read-only proposal manifest for a later full-library rebase."""

import argparse
import copy
import csv
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys


ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if not __package__:
    __package__ = "tools.art.likeness_library"

RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
SOURCE_CATEGORIES = ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Various")
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".bmp"})
MODEL_FILES = ("face_detection_yunet_2023mar.onnx", "face_recognition_sface_2021dec.onnx")
MANIFEST_NAME = "manifest.json"
CSV_NAME = "manifest.csv"
RECEIPT_NAME = "receipt.json"
MEASUREMENTS_NAME = "measurement-evidence.json"
MEASURED_MANIFEST_NAME = "measured-manifest.json"
MEASURED_CSV_NAME = "measured-manifest.csv"
MEASUREMENT_RECEIPT_NAME = "measurement-receipt.json"
RESOLVED_SCOPE_INTEGRITIES = frozenset({
    "unique",
    "production-exact-id-content-canonical",
    "production-exact-id-content-alias",
    "verified-production-alias",
    "verified-retained-prepared-version",
    "verified-unique-sandbox-arrival",
})
CANONICAL_POPULATION_INTEGRITIES = frozenset({
    "unique",
    "production-exact-id-content-canonical",
    "verified-unique-sandbox-arrival",
})


def _sha256(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _hash_source(path):
    path = pathlib.Path(path)
    before = path.stat()
    sha256, sha1, size = hashlib.sha256(), hashlib.sha1(), 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha256.update(block)
            sha1.update(block)
            size += len(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or size != after.st_size:
        raise ValueError(f"source changed while hashing: {path}")
    return sha256.hexdigest(), sha1.hexdigest(), size


def _root_is_reparse(path):
    from .sandbox import _is_reparse_point

    return _is_reparse_point(path)


def _assert_no_reparse_components(path, root):
    root = pathlib.Path(root).resolve(strict=True)
    path = pathlib.Path(path)
    relative = path.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if _root_is_reparse(current):
            raise ValueError(f"linked source path is not permitted: {current}")
    return current


def _bound_source_path(row):
    root = pathlib.Path(row["sourceRoot"]).resolve(strict=True)
    source_path = str(row.get("sourcePath", "")).replace("\\", "/")
    relative = pathlib.PurePosixPath(source_path)
    if not source_path or relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError(f"invalid bound source path: {source_path}")
    path = _assert_no_reparse_components(root.joinpath(*relative.parts), root)
    if not path.is_file():
        raise ValueError(f"bound source file is missing: {source_path}")
    absolute_path = row.get("absolutePath")
    if absolute_path and pathlib.Path(absolute_path).resolve(strict=True) != path.resolve(strict=True):
        raise ValueError(f"absolute source path differs from bound source path: {source_path}")
    return path


def _scan_root(root, label):
    root = pathlib.Path(root).resolve(strict=True)
    if _root_is_reparse(root):
        raise ValueError(f"{label} root is a reparse point: {root}")
    rows, issues, missing_categories = [], [], []
    for category in SOURCE_CATEGORIES:
        category_path = root / category
        if not category_path.exists():
            missing_categories.append(category)
            continue
        if not category_path.is_dir() or _root_is_reparse(category_path):
            issues.append({"path": category, "reason": "missing directory or reparse point"})
            continue
        if category == "Various":
            owners = [(category, category_path)]
        else:
            owners = []
            try:
                children = sorted(category_path.iterdir(), key=lambda item: item.name.casefold())
            except OSError as error:
                issues.append({"path": category, "reason": str(error)})
                continue
            for child in children:
                if child.name.startswith("_") or child.name.casefold() == "archive":
                    continue
                if child.is_dir() and not _root_is_reparse(child):
                    owners.append((f"{category}/{child.name}", child))
                elif child.is_dir():
                    issues.append({
                        "path": child.relative_to(root).as_posix(),
                        "reason": "reparse-point owner directory",
                    })
        for owner, owner_path in owners:
            for bucket in ("gallery", "review"):
                folder = owner_path / bucket
                if not folder.exists():
                    continue
                if not folder.is_dir() or _root_is_reparse(folder):
                    issues.append({
                        "path": folder.relative_to(root).as_posix(),
                        "reason": "reparse point or non-directory bucket",
                    })
                    continue
                try:
                    files = sorted(folder.iterdir(), key=lambda item: item.name.casefold())
                except OSError as error:
                    issues.append({"path": folder.relative_to(root).as_posix(), "reason": str(error)})
                    continue
                for path in files:
                    if path.suffix.casefold() not in IMAGE_EXTENSIONS:
                        continue
                    if _root_is_reparse(path) or not path.is_file():
                        issues.append({
                            "path": path.relative_to(root).as_posix(),
                            "reason": "reparse point or non-regular source",
                        })
                        continue
                    rows.append({
                        "origin": label,
                        "sourceRoot": str(root),
                        "sourcePath": path.relative_to(root).as_posix(),
                        "absolutePath": str(path),
                        "category": category,
                        "ownerFolder": owner,
                        "bucket": "Pool" if category == "Various" else bucket.title(),
                        "photoId": None,
                        "sourceSha256": None,
                        "cacheKeySha1": None,
                        "byteLength": path.stat().st_size,
                        "role": None,
                        "roleReason": None,
                        "measurement": None,
                    })
    return rows, issues, missing_categories


def _count_excluded_artists(root):
    root = pathlib.Path(root)
    artist_root = root / "Artists"
    result = {"files": 0, "bytes": 0, "byBucket": {"Gallery": 0, "Review": 0}, "issues": []}
    if not artist_root.exists() or _root_is_reparse(artist_root):
        return result
    try:
        artists = sorted(artist_root.iterdir(), key=lambda item: item.name.casefold())
    except OSError as error:
        result["issues"].append({"path": "Artists", "reason": str(error)})
        return result
    for artist in artists:
        if artist.name.startswith("_") or not artist.is_dir():
            continue
        if _root_is_reparse(artist):
            result["issues"].append({
                "path": artist.relative_to(root).as_posix(),
                "reason": "reparse-point excluded Artist directory",
            })
            continue
        owners = [artist]
        try:
            owners.extend(
                child for child in sorted(artist.iterdir(), key=lambda item: item.name.casefold())
                if child.is_dir() and not child.name.startswith("_") and not _root_is_reparse(child)
            )
        except OSError as error:
            result["issues"].append({"path": artist.relative_to(root).as_posix(), "reason": str(error)})
        for owner in owners:
            for bucket_name, bucket_label in (("gallery", "Gallery"), ("review", "Review")):
                folder = owner / bucket_name
                if not folder.exists() or not folder.is_dir() or _root_is_reparse(folder):
                    continue
                try:
                    files = folder.iterdir()
                    for path in files:
                        if path.suffix.casefold() in IMAGE_EXTENSIONS and path.is_file() and not _root_is_reparse(path):
                            result["files"] += 1
                            result["bytes"] += path.stat().st_size
                            result["byBucket"][bucket_label] += 1
                except OSError as error:
                    result["issues"].append({
                        "path": folder.relative_to(root).as_posix(),
                        "reason": str(error),
                    })
    return result


def _record_hashes(rows, cache, *, progress=None):
    from tools.art import originals

    by_key = cache.get("emb", {})
    if not isinstance(by_key, dict):
        raise ValueError("embedding cache has a malformed emb map")
    cache_collisions = {}
    processed_bytes = 0
    for index, row in enumerate(rows, 1):
        path = pathlib.Path(row["absolutePath"])
        sha256, sha1, size = _hash_source(path)
        original_name = pathlib.Path(row["sourcePath"]).name
        original_photo_id = _photo_id(original_name)
        owner_name = row["ownerFolder"].rsplit("/", 1)[-1]
        prefix = originals.prefix_of(owner_name)
        normalized_name = originals.standard_name(original_name, prefix)
        normalized_photo_id = _photo_id(normalized_name)
        if original_photo_id:
            photo_id = original_photo_id
            id_status = "existing-stable-photo-id"
            id_basis = "metadata.photo_id_from_name(original filename)"
        elif normalized_photo_id:
            photo_id = normalized_photo_id
            id_status = "standard-name-derived-stable-photo-id"
            id_basis = (
                f"originals.standard_name(original filename, {prefix!r}) then "
                "metadata.photo_id_from_name(normalized filename)"
            )
        else:
            photo_id = None
            id_status = "unresolved-preserved-filename"
            id_basis = (
                "no supported stable ID in the original or normalized filename; "
                "no content-derived ID or new namespace proposed"
            )
        row["photoId"] = photo_id
        row["photoIdEvidence"] = {
            "status": id_status,
            "originalName": original_name,
            "normalizedName": normalized_name,
            "originalPhotoId": original_photo_id,
            "proposedPhotoId": photo_id,
            "basis": id_basis,
            "sourceRenamed": False,
        }
        row["sourceSha256"] = sha256
        row["cacheKeySha1"] = sha1
        row["byteLength"] = size
        processed_bytes += size
        cache_collisions.setdefault(sha1, set()).add(sha256)
        data = by_key.get(sha1)
        row["measurement"] = _measurement(data, sha1, sha256) if data is not None else {
            "status": "needs-source-bound-measurement",
            "cacheKeySha1": sha1,
            "sourceSha256": sha256,
            "data": None,
        }
        if progress and (index == len(rows) or index % 500 == 0):
            progress(index, len(rows), processed_bytes)
    collisions = {key for key, values in cache_collisions.items() if len(values) > 1}
    for row in rows:
        if row["cacheKeySha1"] in collisions:
            row["measurement"] = {
                "status": "hold-cache-key-collision",
                "cacheKeySha1": row["cacheKeySha1"],
                "sourceSha256": row["sourceSha256"],
                "data": None,
            }


def _photo_id(filename):
    from . import metadata

    return metadata.photo_id_from_name(filename)


def _measurement(data, sha1, sha256):
    from .normal_import import _current_measurement

    if not isinstance(data, dict) or not _current_measurement(data):
        return {
            "status": "needs-source-bound-measurement",
            "cacheKeySha1": sha1,
            "sourceSha256": sha256,
            "data": None,
        }
    vector = data.get("v")
    if isinstance(vector, list) and vector and data.get("px", 0) > 0:
        status = "cached-vector"
    elif data.get("faces") == 0:
        status = "cached-no-face"
    else:
        status = "cached-no-usable-vector"
    return {
        "status": status,
        "cacheKeySha1": sha1,
        "sourceSha256": sha256,
        "dataSummary": {
            key: data.get(key) for key in ("faces", "an", "s", "f2", "box", "px", "t")
            if key in data
        },
        "vectorSha256": (
            hashlib.sha256(json.dumps(vector, separators=(",", ":")).encode("utf-8")).hexdigest()
            if isinstance(vector, list) else None
        ),
        "data": data,
    }


def _group_counts(rows):
    result = {}
    for row in rows:
        key = f"{row['origin']}:{row['category']}:{row['bucket']}"
        value = result.setdefault(key, {"files": 0, "bytes": 0})
        value["files"] += 1
        value["bytes"] += row["byteLength"]
    return result


def _identity_name(folder_path):
    from tools.art import people
    from . import metadata

    name_file = people.find(folder_path)
    if name_file and _root_is_reparse(name_file):
        raise ValueError(f"linked Production name record is not permitted: {name_file}")
    recorded = people.read(folder_path)
    return {
        "currentName": recorded[0] if recorded else None,
        "source": "Production z_ identity record" if recorded else "Production folder label only",
        "nameFile": str(name_file) if name_file else None,
        "nameFileSha256": metadata.content_sha256(name_file) if name_file else None,
        "history": list(recorded[1]) if recorded else [],
    }


def _load_local_catalog(root):
    from . import metadata

    path = pathlib.Path(root) / ".likeness-library.json"
    if not path.is_file():
        return None, {"path": str(path), "status": "absent; no global fallback used", "sha256": None}
    if _root_is_reparse(path):
        raise ValueError(f"linked local catalogue is not permitted: {path}")
    catalog = metadata.load_catalog(path)
    return catalog, {
        "path": str(path),
        "status": "validated local catalogue; Sandbox metadata is display/conflict evidence only",
        "sha256": metadata.content_sha256(path),
    }


def _settings_and_cache(working):
    from types import SimpleNamespace
    from tools.art import likeness as api
    domains = api.domains

    current_token = domains.CURRENT.set("general")
    read_only_token = domains.READ_ONLY.set(True)
    try:
        cfg = api.cw.load_cfg()
        storage_root = pathlib.Path(api.cw.storage_root(cfg, "likeness", root=working))
        expected = (storage_root / "general" / "cache.json").resolve()
        path = pathlib.Path(api.cache_path(SimpleNamespace(cache=None), working))
        if path.resolve() != expected:
            raise ValueError(
                f"unexpected general-domain likeness cache path: {path.resolve()}; expected {expected}"
            )
        _assert_no_reparse_components(path, working)
        path = path.resolve()
        cache_api = api.Cache(path)
        cache = {
            "stat": cache_api.stat,
            "emb": cache_api.emb,
            "centeringMean": cache_api.centering_mean,
            "centeringDomain": cache_api.centering_domain,
            "evidenceSource": "api.Cache accepted embedding map",
            "cacheFilePresent": path.is_file(),
        }
    finally:
        domains.CURRENT.reset(current_token)
        domains.READ_ONLY.reset(read_only_token)
    return path, cache


def _working_catalog_action_history(catalog):
    actions = (catalog or {}).get("actions", ())
    undone_action_ids = {
        action.get("undoes") for action in actions
        if action.get("type") == "action-undone" and action.get("undoes")
    }
    history = []
    for action in actions:
        record = {
            key: action.get(key)
            for key in ("id", "type", "photoIds", "contentSha256", "source", "destination", "timestamp", "reason")
            if key in action
        }
        record["disposition"] = (
            "undone" if action.get("id") in undone_action_ids
            else "undo-record" if action.get("type") == "action-undone"
            else "recorded"
        )
        record["origin"] = "Sandbox Working local catalogue action history"
        history.append(record)
    return history


def _decision_maps(cfg, rows, working_catalog):
    from . import metadata

    anchor_patterns = cfg.get("likeness", {}).get("anchors", {})
    anchors = {}
    source_names = {}
    for row in rows:
        if row["origin"] != "Production":
            continue
        owner_name = row["ownerFolder"].rsplit("/", 1)[-1]
        configured_owner, patterns = next((
            (key, values) for key, values in anchor_patterns.items()
            if key.casefold() == owner_name.casefold()
        ), (None, ()))
        matches = [pattern for pattern in patterns if pattern.casefold() in pathlib.Path(row["sourcePath"]).name.casefold()]
        if matches and row["photoId"]:
            record = {
                "ownerFolder": row["ownerFolder"],
                "configuredOwner": configured_owner,
                "patterns": sorted(set(matches)),
                "origin": f"workflows/workspaces.json:likeness.anchors[{configured_owner}]",
                "sourceOrigin": "Production source filename",
                "sourcePath": row["sourcePath"],
            }
            records = anchors.setdefault(row["photoId"], [])
            if record not in records:
                records.append(record)

    locks, workflow = {}, set()
    photos = cfg.get("photos", {})
    for person_name in cfg.get("likeness", {}).get("keepPhoto", ()):
        selected = photos.get(person_name)
        photo_id = metadata.photo_id_from_name(selected) if isinstance(selected, str) else None
        if photo_id:
            origin = f"workflows/workspaces.json:likeness.keepPhoto[{person_name}]"
            origins = locks.setdefault(photo_id, [])
            if origin not in origins:
                origins.append(origin)
    selected_names = list(photos.values())
    for flow in cfg.get("flows", {}).values():
        selected_names.extend(flow.get("photos", {}).values())
    for selected in selected_names:
        if isinstance(selected, str):
            photo_id = metadata.photo_id_from_name(selected)
            if photo_id:
                workflow.add(photo_id)

    people_by_folder = {
        person.get("folder"): person
        for person in (working_catalog or {}).get("people", {}).values()
    }
    people_by_id = {
        person.get("id"): person
        for person in (working_catalog or {}).get("people", {}).values()
    }
    working_anchors = {}
    for person in (working_catalog or {}).get("people", {}).values():
        for photo_id in person.get("identityAnchors", ()):
            working_anchors.setdefault(photo_id, []).append({
                "personId": person.get("id"),
                "folder": person.get("folder"),
                "displayName": person.get("displayName"),
                "origin": "Sandbox Working local catalogue",
                "usedForCoreOrRole": False,
                "status": "explicit anchor disclosed for review; not promoted as a source reference",
            })
    actions_by_photo = {}
    for action in _working_catalog_action_history(working_catalog):
        for photo_id in action.get("photoIds", ()):
            actions_by_photo.setdefault(photo_id, []).append(action)
    working_photos = (working_catalog or {}).get("photos", {})
    for row in rows:
        row["sourceName"] = None
        row["sourceNameEvidence"] = None
        if row["origin"] == "Production" and row["category"] != "Various":
            if row["ownerFolder"] not in source_names:
                source_names[row["ownerFolder"]] = _identity_name(
                    pathlib.Path(row["sourceRoot"]) / pathlib.PurePosixPath(row["ownerFolder"])
                )
            row["sourceNameEvidence"] = source_names[row["ownerFolder"]]
            row["sourceName"] = row["sourceNameEvidence"]["currentName"]
        photo = working_photos.get(row["photoId"], {}) if row["photoId"] else {}
        membership = photo.get("membership") or {}
        person = (
            people_by_folder.get(row["ownerFolder"])
            if row["origin"] == "Sandbox"
            else people_by_id.get(photo.get("personId") or membership.get("personId"))
        )
        working_name = None
        if person:
            names = person.get("names") or {}
            working_name = names.get("currentName") or person.get("displayName")
        row["workingCurrentOwner"] = (
            person.get("folder") if person else row["ownerFolder"] if row["origin"] == "Sandbox" else None
        )
        row["workingCurrentName"] = working_name
        row["workingCurrentPersonId"] = person.get("id") if person else None
        anchor_records = anchors.get(row["photoId"], []) if row["photoId"] else []
        row["decisions"] = {
            "truePhotoLock": {
                "locked": row["photoId"] in locks,
                "origin": next(iter(locks.get(row["photoId"], ())), None),
                "origins": sorted(locks.get(row["photoId"], ())),
            },
            "workflowSelected": row["photoId"] in workflow,
            "configuredIdentityAnchor": sorted({
                pattern for record in anchor_records for pattern in record["patterns"]
            }),
            "configuredIdentityAnchorOwners": anchor_records,
            "sandboxIdentityAnchors": working_anchors.get(row["photoId"], []),
            "sandboxActionHistory": actions_by_photo.get(row["photoId"], []),
            "sandboxProtection": {
                "value": bool(photo.get("protected")),
                "provenance": photo.get("protectionProvenance"),
                "status": "unverified Sandbox evidence; not promoted to source authority",
            } if photo else None,
            "sandboxRejections": {
                "personIds": list(photo.get("rejectedPersonIds", ())),
                "status": "unverified Sandbox evidence; held for review if present",
            } if photo else None,
            "sandboxMembership": {
                "value": photo.get("membership"),
                "usedForCoreOrRole": False,
                "status": "ignored as experimental or unverified seed authority",
            } if photo and photo.get("membership") else None,
        }
        row["reviewFlags"] = []
        if row["sourceName"] and working_name and row["sourceName"].casefold() != working_name.casefold():
            row["reviewFlags"].append("Working and Production recorded names differ; Production name is proposed, not final")
    return anchors


def _production_duplicate_entries(rows):
    entries = []
    for row in rows:
        path = _bound_source_path(row)
        bucket = "gallery" if row["bucket"] == "Pool" else row["bucket"].lower()
        entries.append((path, row["category"], path.parent.parent, bucket))
    return entries


def _exact_alias_decision_conflicts(rows, entries, chosen, keeper_entry):
    conflicts = []
    chosen_entries = [entry for entry in entries if entry[0].stem.lower() in chosen]
    if len(chosen_entries) > 1:
        conflicts.append("multiple physical copies are selected by configured workflow photo stems")

    owner_folders = {row["ownerFolder"].casefold() for row in rows}
    locked_origins = set()
    locked_owners = set()
    locked_present = False
    unresolved_lock_owner = False
    for row in rows:
        lock = row.get("decisions", {}).get("truePhotoLock", {})
        if not lock.get("locked"):
            continue
        locked_present = True
        origins = lock.get("origins")
        if not isinstance(origins, (list, tuple)):
            origins = [lock.get("origin")]
        origins = [origin for origin in origins if origin]
        if not origins:
            unresolved_lock_owner = True
        for origin in origins:
            if isinstance(origin, str):
                locked_origins.add(origin)
                match = re.search(r"keepPhoto\[([^\]]+)\]", origin, re.IGNORECASE)
                if match:
                    locked_owners.add(match.group(1).casefold())
                else:
                    unresolved_lock_owner = True
            else:
                unresolved_lock_owner = True
    if len(locked_origins) > 1 or len(locked_owners) > 1:
        conflicts.append("multiple true photo locks name conflicting ownership decisions")
    elif locked_present and len(owner_folders) > 1:
        lock_owner = next(iter(locked_owners), None)
        matching = [
            row for row in rows
            if lock_owner and (
                row["ownerFolder"].rsplit("/", 1)[-1].casefold() == lock_owner
                or (row.get("sourceName") or "").casefold() == lock_owner
            )
        ]
        keeper_row = next(row for row in rows if _row_id(row) == keeper_entry[1])
        if unresolved_lock_owner or len(matching) != 1 or matching[0] is not keeper_row:
            conflicts.append("true photo lock does not uniquely confirm the proposed owner representation")

    anchor_records = {}
    unattributed_anchor = False
    for row in rows:
        decisions = row.get("decisions", {})
        patterns = decisions.get("configuredIdentityAnchor", ())
        records = decisions.get("configuredIdentityAnchorOwners", ())
        if patterns and not records:
            unattributed_anchor = True
        for record in records:
            key = (
                record.get("ownerFolder"),
                record.get("configuredOwner"),
                tuple(record.get("patterns", ())),
                record.get("origin"),
                record.get("sourcePath"),
            )
            anchor_records[key] = record
    anchored_owners = {
        record["ownerFolder"].casefold()
        for record in anchor_records.values()
        if isinstance(record.get("ownerFolder"), str) and record.get("ownerFolder")
    }
    if unattributed_anchor or any(
        not isinstance(record.get("ownerFolder"), str) or not record.get("ownerFolder")
        for record in anchor_records.values()
    ):
        conflicts.append("configured identity anchor lacks authoritative owner provenance")
    if len(anchored_owners) > 1:
        conflicts.append("explicit configured anchors name multiple owners for the same source")
    elif anchored_owners and len(owner_folders) > 1:
        keeper_row = next(row for row in rows if _row_id(row) == keeper_entry[1])
        if keeper_row["ownerFolder"].casefold() not in anchored_owners:
            conflicts.append("configured identity anchor conflicts with the proposed owner representation")
    return sorted(set(conflicts))


def _scope_integrity_report(rows):
    blockers = [
        row for row in rows
        if row.get("scopeIntegrity") not in RESOLVED_SCOPE_INTEGRITIES
    ]
    grouped = {}
    for row in blockers:
        grouped.setdefault(row.get("scopeIntegrity", "unknown"), []).append(row)
    diagnostics = []
    for status, items in sorted(grouped.items()):
        diagnostics.append({
            "status": status,
            "count": len(items),
            "rowIds": sorted(row.get("rowId") or _row_id(row) for row in items),
            "reasons": sorted({
                row.get("scopeIntegrityReason") or "Material source-integrity disposition requires review."
                for row in items
            }),
        })
    return not blockers, blockers, diagnostics


def _classify_unique_sources(rows, cfg=None):
    from tools.art import duplicates
    from . import retained_preparation, verification_reads

    cfg = cfg or {"photos": {}, "flows": {}}
    chosen = duplicates.chosen_stems(cfg)
    production = [row for row in rows if row["origin"] == "Production"]
    sandbox_rows = [row for row in rows if row["origin"] == "Sandbox"]
    production_by_id, production_by_hash, production_by_pair = {}, {}, {}
    working_by_id, working_by_hash = {}, {}
    for row in production:
        if row["photoId"]:
            production_by_id.setdefault(row["photoId"], []).append(row)
        production_by_hash.setdefault(row["sourceSha256"], []).append(row)
        production_by_pair.setdefault((row["photoId"], row["sourceSha256"]), []).append(row)
    for row in sandbox_rows:
        if row["photoId"]:
            working_by_id.setdefault(row["photoId"], []).append(row)
        working_by_hash.setdefault(row["sourceSha256"], []).append(row)

    prod_duplicate_ids = {key for key, items in production_by_id.items() if len(items) > 1}
    prod_duplicate_hashes = {
        key for key, items in production_by_hash.items()
        if len({item["photoId"] for item in items}) > 1
    }
    work_duplicate_ids = {key for key, items in working_by_id.items() if len(items) > 1}
    work_duplicate_hashes = {key for key, items in working_by_hash.items() if len(items) > 1}

    for row in production:
        row.update(canonical=False, aliasOf=None, aliasType=None, canonicalSourceRowId=None)
        if not row["photoId"]:
            row["scopeIntegrity"] = "missing-stable-photo-id"
            row["scopeIntegrityReason"] = "No supported stable photo ID was derived from the preserved filename."
        elif len({item["sourceSha256"] for item in production_by_id[row["photoId"]]}) > 1:
            row["scopeIntegrity"] = "duplicate-production-photo-id"
            row["scopeIntegrityReason"] = "The same Production photo ID has different source bytes; version ownership is unresolved."
        elif row["sourceSha256"] in prod_duplicate_hashes:
            row["scopeIntegrity"] = "duplicate-production-content"
            row["scopeIntegrityReason"] = "Identical Production bytes carry different photo IDs; no identity merge is proposed."
        else:
            row["canonical"] = True
            row["scopeIntegrity"] = "unique"
            row["scopeIntegrityReason"] = "Unique Production photo ID and source content."
            row["canonicalSourceRowId"] = row.get("rowId") or _row_id(row)

    exact_group_count = 0
    exact_alias_row_count = 0
    exact_ambiguous_group_count = 0
    exact_group_ids = {
        key for key, items in production_by_pair.items() if key[0] and len(items) > 1
    }
    for photo_id, checksum in sorted(exact_group_ids):
        group = production_by_pair[(photo_id, checksum)]
        if len(group) != len(production_by_id[photo_id]):
            for row in production_by_id[photo_id]:
                row["canonical"] = False
                row["canonicalSourceRowId"] = None
                row["scopeIntegrity"] = "duplicate-production-photo-id"
                row["scopeIntegrityReason"] = "The same Production photo ID has different source bytes; exact-copy subset cannot resolve the version conflict."
            production_by_pair.pop((photo_id, checksum), None)
            continue
        if checksum in prod_duplicate_hashes:
            for row in group:
                row["canonical"] = False
                row["scopeIntegrity"] = "duplicate-production-content"
                row["scopeIntegrityReason"] = "Identical Production bytes carry different photo IDs; no identity merge is proposed."
            production_by_pair.pop((photo_id, checksum), None)
            continue
        try:
            entries = _production_duplicate_entries(group)
        except (OSError, ValueError, KeyError) as error:
            entries = []
            path_error = str(error)
        else:
            path_error = None
        if path_error:
            for row in group:
                row["scopeIntegrity"] = "production-exact-source-unavailable"
                row["scopeIntegrityReason"] = path_error
                row["canonical"] = False
            production_by_pair.pop((photo_id, checksum), None)
            exact_ambiguous_group_count += 1
            continue
        entry_by_row_id = {
            _row_id(row): entry for row, entry in zip(group, entries)
        }
        keeper_entry = duplicates.keeper(entries, chosen)
        keeper_row_id = next(
            row_id for row_id, entry in entry_by_row_id.items() if entry is keeper_entry
        )
        conflicts = _exact_alias_decision_conflicts(group, entries, chosen, (keeper_entry, keeper_row_id))
        members = [
            {
                "rowId": _row_id(row),
                "sourcePath": row["sourcePath"],
                "ownerFolder": row["ownerFolder"],
                "workflowChosen": entry[0].stem.lower() in chosen,
            }
            for row, entry in sorted(zip(group, entries), key=lambda pair: pair[0]["sourcePath"].casefold())
        ]
        alias_evidence = {
            "photoId": photo_id,
            "sourceSha256": checksum,
            "canonicalRowId": None if conflicts else keeper_row_id,
            "proposedKeeperRowId": keeper_row_id,
            "proposedKeeperSourcePath": next(row["sourcePath"] for row in group if _row_id(row) == keeper_row_id),
            "keeperRule": "tools.art.duplicates.keeper(entries, tools.art.duplicates.chosen_stems(config))",
            "keeperReason": "proposed source representation only; no originals are moved, deleted, merged, or reassigned",
            "decisionConflicts": conflicts,
            "members": members,
        }
        if conflicts:
            exact_ambiguous_group_count += 1
            for row in group:
                row["canonical"] = False
                row["canonicalSourceRowId"] = None
                row["scopeIntegrity"] = "ambiguous-production-exact-alias-decisions"
                row["scopeIntegrityReason"] = "; ".join(conflicts)
                row["exactSourceAliasEvidence"] = alias_evidence
            production_by_pair.pop((photo_id, checksum), None)
            continue

        exact_group_count += 1
        exact_alias_row_count += len(group) - 1
        production_by_pair[(photo_id, checksum)] = [
            next(row for row in group if _row_id(row) == keeper_row_id)
        ]
        for row in group:
            is_keeper = _row_id(row) == keeper_row_id
            row["canonical"] = is_keeper
            row["canonicalSourceRowId"] = keeper_row_id
            row["aliasOf"] = None if is_keeper else keeper_row_id
            row["aliasType"] = "production-exact-id-content" if not is_keeper else None
            row["scopeIntegrity"] = (
                "production-exact-id-content-canonical" if is_keeper
                else "production-exact-id-content-alias"
            )
            row["scopeIntegrityReason"] = (
                "Selected by the existing duplicate keeper among byte-identical copies with the same stable photo ID."
                if is_keeper else "Exact stable photo ID and SHA-256 match the proposed Production canonical representation."
            )
            row["exactSourceAliasEvidence"] = {
                **alias_evidence,
                "canonicalRowId": keeper_row_id,
                "rowDisposition": "canonical" if is_keeper else "alias",
            }

    # Keep one canonical Production representation for each independently resolved ID/content pair.
    for row in production:
        pair = (row["photoId"], row["sourceSha256"])
        if row["scopeIntegrity"] == "unique":
            production_by_pair[pair] = [row]

    retained_candidates = []
    for row in sandbox_rows:
        photo_id = row["photoId"]
        prod_ids = production_by_id.get(photo_id, [])
        if not photo_id or not prod_ids:
            continue
        production_hashes = {item["sourceSha256"] for item in prod_ids}
        if row["sourceSha256"] in production_hashes:
            continue
        work_ids = working_by_id.get(photo_id, [])
        if len(work_ids) != 1:
            row["retainedPreparationEvidence"] = {
                "status": "ambiguous-sandbox-photo-id",
                "reason": "multiple Sandbox rows share this stable photo ID; lineage cannot select a canonical source",
            }
            continue
        if len(production_hashes) != 1:
            row["retainedPreparationEvidence"] = {
                "status": "production-source-version-conflict",
                "reason": "Production rows with this stable photo ID have different source hashes",
            }
            continue
        production_row = production_by_pair.get((photo_id, next(iter(production_hashes))))
        if (
            production_row is None or len(production_row) != 1
            or production_row[0]["scopeIntegrity"] not in (
                "unique", "production-exact-id-content-canonical",
            )
        ):
            row["retainedPreparationEvidence"] = {
                "status": "production-source-not-canonical",
                "reason": "The exact-ID/content Production source set has no unambiguous proposed canonical representation",
            }
            continue
        production_row = production_row[0]
        try:
            current_path = _bound_source_path(row)
            working_root = pathlib.Path(row["sourceRoot"]).resolve(strict=True)
        except (OSError, ValueError, KeyError) as error:
            row["retainedPreparationEvidence"] = {
                "status": "bound-sandbox-source-unavailable",
                "reason": str(error),
            }
            continue
        retained_candidates.append((row, production_row, working_root, current_path))

    candidates_by_root = {}
    for candidate in retained_candidates:
        candidates_by_root.setdefault(candidate[2], []).append(candidate)
    for working_root, candidates in candidates_by_root.items():
        with verification_reads.session(working_root, seal_content=False):
            for row, production_row, _root, current_path in candidates:
                try:
                    claims = retained_preparation.claims_photo(working_root, current_path)
                    if not claims:
                        row["retainedPreparationEvidence"] = {
                            "status": "no-retained-preparation-claim",
                            "reason": "no destination-owned retained-preparation manifest claims this current path",
                        }
                        continue
                    link = retained_preparation.verify_link(working_root, current_path, row["photoId"])
                except (OSError, ValueError, KeyError, TypeError) as error:
                    row["retainedPreparationEvidence"] = {
                        "status": "invalid-or-stale-retained-preparation",
                        "reason": str(error),
                    }
                    continue
                if link is None:
                    row["retainedPreparationEvidence"] = {
                        "status": "invalid-or-stale-retained-preparation",
                        "reason": "a retained-preparation claim exists but shared verification did not validate it",
                    }
                    continue
                if link.get("photoId") != row["photoId"]:
                    row["retainedPreparationEvidence"] = {
                        "status": "retained-photo-id-mismatch",
                        "reason": "verified retained-preparation photo ID differs from the proposed stable ID",
                    }
                    continue
                if link.get("sourceSha256") != production_row["sourceSha256"]:
                    row["retainedPreparationEvidence"] = {
                        "status": "retained-source-does-not-match-production",
                        "reason": "verified retained source bytes do not match the canonical Production source",
                    }
                    continue
                if link.get("currentSha256") != row["sourceSha256"]:
                    row["retainedPreparationEvidence"] = {
                        "status": "retained-current-does-not-match-sandbox",
                        "reason": "verified retained current bytes do not match the Sandbox source row",
                    }
                    continue
                retained_row = link.get("row") if isinstance(link.get("row"), dict) else {}
                row["retainedPreparationEvidence"] = {
                    "status": "verified-retained-prepared-version",
                    "reason": "shared retained-preparation verification binds the current Sandbox version to the canonical Production source",
                    "productionRowId": production_row.get("rowId") or _row_id(production_row),
                    "productionSource": {
                        "root": production_row.get("sourceRoot"),
                        "path": production_row.get("sourcePath"),
                        "sha256": production_row.get("sourceSha256"),
                    },
                    "sandboxCurrent": {
                        "root": row.get("sourceRoot"),
                        "path": row.get("sourcePath"),
                        "sha256": row.get("sourceSha256"),
                    },
                    "retainedManifest": link.get("manifest"),
                    "retainedOriginal": link.get("original"),
                    "retainedSource": retained_row.get("source"),
                    "retainedSourceSha256": link.get("sourceSha256"),
                    "retainedCurrentSha256": link.get("currentSha256"),
                    "retainedSelected": link.get("selected"),
                    "recipe": link.get("recipe"),
                    "artifactMap": link.get("artifactMap", {}),
                    "artifacts": [
                        {"path": item.get("path"), "sha256": item.get("sha256")}
                        for item in link.get("artifacts", ()) if isinstance(item, dict)
                    ],
                    "linkage": "verified prepared version; not a new arrival, duplicate alias, or additional identity vote",
                }

    for row in sandbox_rows:
        row.update(canonical=False, aliasOf=None, aliasType=None, canonicalSourceRowId=None)
        row["scopeIntegrity"] = "unresolved"
        photo_id, checksum = row["photoId"], row["sourceSha256"]
        if not photo_id:
            row["scopeIntegrity"] = "missing-stable-photo-id"
            row["scopeIntegrityReason"] = "No supported stable photo ID was derived from the preserved filename."
            continue
        if photo_id in work_duplicate_ids:
            row["scopeIntegrity"] = "duplicate-sandbox-photo-id"
            row["scopeIntegrityReason"] = "Multiple Sandbox rows use this stable photo ID; no Sandbox canonical source is selected."
            continue
        if checksum in work_duplicate_hashes:
            row["scopeIntegrity"] = "duplicate-sandbox-content"
            row["scopeIntegrityReason"] = "Multiple Sandbox rows share these bytes; no Sandbox source is selected."
            continue
        prod_ids = production_by_id.get(photo_id, [])
        prod_hashes = production_by_hash.get(checksum, [])
        pair_sources = production_by_pair.get((photo_id, checksum), [])
        id_hashes = {item["sourceSha256"] for item in prod_ids}
        if (
            len(id_hashes) == 1 and len(pair_sources) == 1
            and checksum not in prod_duplicate_hashes
            and pair_sources[0]["scopeIntegrity"] in (
                "unique", "production-exact-id-content-canonical",
            )
        ):
            canonical_row = pair_sources[0]
            row["scopeIntegrity"] = "verified-production-alias"
            row["scopeIntegrityReason"] = "Exact stable photo ID and SHA-256 match the canonical Production source."
            row["aliasOf"] = canonical_row.get("rowId") or _row_id(canonical_row)
            row["canonicalSourceRowId"] = row["aliasOf"]
            row["aliasType"] = "cross-root-production-exact-id-content"
            row["crossRootAliasEvidence"] = {
                "canonicalRowId": row["aliasOf"],
                "canonicalSourcePath": canonical_row["sourcePath"],
                "photoId": photo_id,
                "sourceSha256": checksum,
                "reason": "byte-identical stable photo ID is already represented by the proposed Production source",
            }
            continue
        if prod_ids:
            retained = row.get("retainedPreparationEvidence", {})
            if retained.get("status") == "verified-retained-prepared-version":
                row["scopeIntegrity"] = "verified-retained-prepared-version"
                row["scopeIntegrityReason"] = "Verified retained version is linked to the single canonical Production source."
                row["retainedVersionOf"] = retained["productionRowId"]
            else:
                row["scopeIntegrity"] = "photo-id-content-conflict"
                row["scopeIntegrityReason"] = (
                    "Same stable photo ID has different bytes without a verified retained lineage tying it to one canonical Production source."
                )
            continue
        if prod_hashes:
            row["scopeIntegrity"] = "duplicate-content-different-photo-id"
            row["scopeIntegrityReason"] = "Identical bytes have a different stable photo ID; no identity merge is proposed."
            continue
        row["canonical"] = True
        row["scopeIntegrity"] = "verified-unique-sandbox-arrival"
        row["scopeIntegrityReason"] = "No Production row has this stable photo ID or source content."

    return {
        "productionDuplicatePhotoIds": sorted(prod_duplicate_ids),
        "productionDuplicateContentHashes": sorted(prod_duplicate_hashes),
        "sandboxDuplicatePhotoIds": sorted(work_duplicate_ids),
        "sandboxDuplicateContentHashes": sorted(work_duplicate_hashes),
        "productionExactIdContentAliasGroups": exact_group_count,
        "productionExactIdContentAliasRows": exact_alias_row_count,
        "productionExactIdContentAmbiguousGroups": exact_ambiguous_group_count,
        "productionSameIdDifferentContentGroups": sum(
            len({row["sourceSha256"] for row in items}) > 1
            for items in production_by_id.values()
        ),
        "productionDifferentIdSameContentHashes": len(prod_duplicate_hashes),
        "crossRootVerifiedProductionAliasRows": sum(
            row["scopeIntegrity"] == "verified-production-alias" for row in sandbox_rows
        ),
    }


def _row_id(row):
    return hashlib.sha256(
        (row["origin"] + "\n" + row["sourcePath"] + "\n" + row["sourceSha256"]).encode("utf-8")
    ).hexdigest()


def _source_models(model_root):
    result = []
    for name in MODEL_FILES:
        path = pathlib.Path(model_root) / "models" / name
        record = {"name": name, "path": str(path), "available": path.is_file(), "bytes": None, "sha256": None}
        if record["available"]:
            record["bytes"] = path.stat().st_size
            record["sha256"] = _sha256(path)
        result.append(record)
    return result


def _implementation_hashes():
    from . import metadata

    library = pathlib.Path(__file__).parent
    paths = {
        "manifestBuilder": pathlib.Path(__file__),
        "normalImport": library / "normal_import.py",
        "normalProducts": library / "normal_products.py",
        "normalFinish": library / "normal_finish.py",
        "normalHistory": library / "normal_history.py",
        "normalTransaction": library / "normal_transaction.py",
        "reconciliation": library / "reconciliation.py",
        "audit": library / "audit.py",
        "policy": library / "policy.py",
        "engine": library / "engine.py",
        "metadata": library / "metadata.py",
        "identityNames": library / "identity_names.py",
        "retainedPreparation": library / "retained_preparation.py",
        "verificationReads": library / "verification_reads.py",
        "duplicates": library.parent / "duplicates.py",
        "sandboxGuards": library / "sandbox.py",
        "likenessApi": library.parent / "likeness.py",
        "originals": library.parent / "originals.py",
        "workspaceConfig": ROOT / "workflows" / "workspaces.json",
        "likenessPolicy": ROOT / "data" / "art" / "likeness-engine-policy.json",
        "manifestLauncher": ROOT / "bin" / "rebase-manifest.cmd",
    }
    return {name: metadata.content_sha256(path) for name, path in paths.items() if path.is_file()}


def _working_catalog_summary(catalog):
    if catalog is None:
        return {
            "people": 0, "photos": 0, "membershipFlagsIgnored": 0,
            "protectedFlagsUnverified": 0, "identityAnchorCount": 0,
            "actionHistoryCount": 0,
        }
    photos = catalog.get("photos", {})
    people = catalog.get("people", {})
    return {
        "people": len(people),
        "photos": len(photos),
        "membershipFlagsIgnored": sum("membership" in photo for photo in photos.values()),
        "protectedFlagsUnverified": sum(bool(photo.get("protected")) for photo in photos.values()),
        "rejectionFlagsUnverified": sum(bool(photo.get("rejectedPersonIds")) for photo in photos.values()),
        "identityAnchorCount": sum(len(person.get("identityAnchors", ())) for person in people.values()),
        "actionHistoryCount": len(catalog.get("actions", ())),
    }


def _qualify_cores(rows, cfg, policy, centering_mean):
    from tools.art import likeness as api
    from . import normal_finish
    from .policy import effective_settings

    population = [
        row for row in rows
        if row.get("canonical")
        and row["scopeIntegrity"] in CANONICAL_POPULATION_INTEGRITIES
        and (
            row["origin"] == "Production"
            or row["scopeIntegrity"] == "verified-unique-sandbox-arrival"
        )
    ]
    photos = []
    photo_by_row_id = {}
    for row in population:
        measurement = row["measurement"]
        data = measurement.get("data") if isinstance(measurement, dict) else None
        if not isinstance(data, dict):
            continue
        owner = row["ownerFolder"] if row["origin"] == "Production" else "Various"
        category, _, name = owner.partition("/")
        if not name:
            name = category
        photo = api.Photo(
            _bound_source_path(row), category, name, row["cacheKeySha1"], data,
        )
        photos.append(photo)
        photo_by_row_id[row["rowId"]] = photo
    settings = effective_settings(cfg, policy)
    population_space = api.Space(photos, settings, mean=centering_mean)
    eligible_rows = [
        row for row in rows
        if row["origin"] == "Production"
        and row["category"] != "Various"
        and row["bucket"] == "Gallery"
        and row["scopeIntegrity"] in (
            "unique", "production-exact-id-content-canonical",
        )
        and row.get("canonical")
        and row.get("photoId")
        and row["rowId"] in photo_by_row_id
    ]
    core_space = api.Space(
        [photo_by_row_id[row["rowId"]] for row in eligible_rows],
        settings,
        mean=population_space.mean,
    )
    minimal_catalog = {"people": {}, "photos": {}, "actions": []}
    for row in eligible_rows:
        if row["photoId"]:
            decisions = row["decisions"]
            unverified_hold = (
                bool((decisions.get("sandboxProtection") or {}).get("value"))
                or bool((decisions.get("sandboxRejections") or {}).get("personIds"))
            )
            minimal_catalog["photos"][row["photoId"]] = {
                "contentSha256": row["sourceSha256"],
                "protected": bool(
                    decisions["truePhotoLock"]["locked"]
                    or decisions["workflowSelected"]
                    or unverified_hold
                ),
            }
    for row in eligible_rows:
        folder = row["ownerFolder"]
        category = row["category"]
        person = minimal_catalog["people"].setdefault(folder, {
            "id": folder,
            "folder": folder,
            "displayName": row.get("sourceName") or folder.rsplit("/", 1)[-1],
            "folderHistory": [],
            "identityAnchors": [],
            "protected": bool(policy["categoryPolicies"][category]["identityProtectedByDefault"]),
        })
        owner_anchors = row["decisions"].get("configuredIdentityAnchorOwners", ())
        if row["photoId"] and any(
            isinstance(anchor.get("ownerFolder"), str)
            and anchor["ownerFolder"].casefold() == folder.casefold()
            for anchor in owner_anchors
        ):
            person["identityAnchors"].append(row["photoId"])
    for person in minimal_catalog["people"].values():
        person["identityAnchors"] = sorted(set(person["identityAnchors"]))
    cores, diagnostics = normal_finish.cores(api, core_space, minimal_catalog, policy)
    core_ids = {
        photo_id for core in cores.values() for photo_id in core["corePhotoIds"] if photo_id
    }
    return cores, core_ids, diagnostics, population_space.mean


def _apply_roles(rows, *, complete, cores, core_ids, diagnostics):
    core_folder_by_id = {
        photo_id: folder
        for folder, core in cores.items() for photo_id in core["corePhotoIds"] if photo_id
    }
    for row in rows:
        row["role"] = "hold"
        row["roleReason"] = "scope record has not been qualified"
        row["proposedRole"] = None
        if row["scopeIntegrity"] == "verified-production-alias":
            row["role"] = "duplicate-alias"
            row["roleReason"] = "byte-identical stable photo ID is already represented by its Production source"
            continue
        if row["scopeIntegrity"] == "production-exact-id-content-alias":
            row["role"] = "production-exact-alias"
            evidence = row.get("exactSourceAliasEvidence", {})
            row["roleReason"] = (
                "byte-identical Production row with the same stable photo ID is preserved as a physical alias "
                f"of proposed keeper row {evidence.get('canonicalRowId')}; no cleanup or reassignment"
            )
            continue
        if row["scopeIntegrity"] not in (
            "unique", "production-exact-id-content-canonical", "verified-unique-sandbox-arrival",
        ):
            retained = row.get("retainedPreparationEvidence", {})
            if row["scopeIntegrity"] == "verified-retained-prepared-version":
                row["roleReason"] = (
                    "verified retained/prepared version linked to its unique Production source; "
                    "preserved as provenance, not a new candidate or identity vote"
                )
            elif retained:
                row["roleReason"] = (
                    row["scopeIntegrity"] + "; retained lineage "
                    + retained.get("status", "unverified") + ": "
                    + retained.get("reason", "requires review")
                )
            else:
                row["roleReason"] = row["scopeIntegrity"] + "; resolve duplicate or identity conflict before approval"
            continue
        if row["origin"] == "Production":
            if row["bucket"] == "Gallery":
                row["proposedRole"] = "reference-or-noncore-gallery-candidate"
                if not complete:
                    row["roleReason"] = "Production Gallery; exact core/non-core role awaits complete source-bound measurements and collision review"
                elif row["photoId"] in core_ids:
                    row["role"] = "frozen-reference"
                    row["roleReason"] = "selected by shared frozen_identity_cores under the configured policy; working membership flags were not used"
                    if row["scopeIntegrity"] == "production-exact-id-content-canonical":
                        row["roleReason"] += "; exact-byte aliases contribute one proposed source representation"
                    row["referenceFolder"] = core_folder_by_id.get(row["photoId"])
                else:
                    row["role"] = "candidate"
                    row["roleReason"] = "non-core Production Gallery source in the approved reassessment scope"
                    if row["scopeIntegrity"] == "production-exact-id-content-canonical":
                        row["roleReason"] += "; exact-byte aliases contribute one proposed source representation"
            else:
                row["role"] = "candidate"
                row["proposedRole"] = "candidate"
                row["roleReason"] = "Production Review/Various source in the approved reassessment scope"
        else:
            row["role"] = "candidate"
            row["proposedRole"] = "candidate"
            row["roleReason"] = "verified unique Sandbox arrival; current Sandbox placement/membership is not seed authority"

        decisions = row["decisions"]
        if decisions["truePhotoLock"]["locked"]:
            if row["photoId"] not in core_ids:
                row["role"] = "hold"
                row["roleReason"] = "true configured photo lock; preserved and not reassigned"
        working_protection = decisions.get("sandboxProtection")
        if working_protection and working_protection["value"]:
            row["role"] = "hold"
            row["roleReason"] = "unverified Sandbox protection evidence; hold for decision review, not promoted as a reference"
        rejections = decisions.get("sandboxRejections")
        if rejections and rejections["personIds"]:
            row["role"] = "hold"
            row["roleReason"] = "Sandbox rejection decision requires content-bound human review; not imported as a source decision"
        if decisions.get("sandboxIdentityAnchors"):
            row["role"] = "hold"
            row["roleReason"] = "Working catalogue identity anchor is disclosed but not promoted; review its source-bound identity before assigning a role"
        active_actions = [
            action for action in decisions.get("sandboxActionHistory", ())
            if action.get("disposition") == "recorded"
        ]
        if active_actions:
            row["role"] = "hold"
            row["roleReason"] = "active Working catalogue action history requires source-bound human review"
        if decisions["workflowSelected"] and row["role"] != "frozen-reference":
            row["role"] = "hold"
            row["roleReason"] = "workflow-selected photo is retained and not reassessed"
        if not complete and row["role"] == "candidate":
            row["measurementReady"] = False
        else:
            row["measurementReady"] = row.get("measurement", {}).get("status") in (
                "cached-vector", "cached-no-face", "cached-no-usable-vector", "report-measured-vector",
                "report-measured-no-face", "report-measured-no-usable-vector",
            )
    return {
        folder: {
            "corePhotoIds": sorted(photo_id for photo_id in core["corePhotoIds"] if photo_id),
            "mode": core["mode"],
            "identityProtectedByPolicy": bool(core["identityProtected"]),
            "coreCount": len(core["corePhotoIds"]),
        }
        for folder, core in sorted(cores.items())
    }, diagnostics


def _csv_bytes(rows):
    import io

    output = io.StringIO(newline="")
    columns = (
        "rowId", "origin", "sourcePath", "sourceSha256", "byteLength", "photoId",
        "sourceOriginalName", "normalizedSourceName", "photoIdEvidenceStatus", "photoIdBasis",
        "category", "ownerFolder", "bucket", "sourceName", "workingCurrentOwner",
        "workingCurrentName", "scopeIntegrity", "scopeIntegrityReason",
        "canonical", "canonicalSourceRowId", "aliasOf", "aliasType",
        "exactSourceAliasEvidence", "crossRootAliasEvidence",
        "measurementStatus", "measurementReady",
        "truePhotoLock", "workflowSelected", "configuredIdentityAnchor",
        "configuredIdentityAnchorOwners",
        "sandboxIdentityAnchors", "sandboxActionHistory", "role",
        "proposedRole", "roleReason", "retainedPreparationEvidence", "reviewFlags",
    )
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        decisions = row.get("decisions", {})
        writer.writerow({
            **row,
            "sourceOriginalName": row.get("photoIdEvidence", {}).get("originalName"),
            "normalizedSourceName": row.get("photoIdEvidence", {}).get("normalizedName"),
            "photoIdEvidenceStatus": row.get("photoIdEvidence", {}).get("status"),
            "photoIdBasis": row.get("photoIdEvidence", {}).get("basis"),
            "retainedPreparationEvidence": json.dumps(
                row.get("retainedPreparationEvidence"), ensure_ascii=True,
            ) if row.get("retainedPreparationEvidence") else None,
            "exactSourceAliasEvidence": json.dumps(
                row.get("exactSourceAliasEvidence"), ensure_ascii=True,
            ) if row.get("exactSourceAliasEvidence") else None,
            "crossRootAliasEvidence": json.dumps(
                row.get("crossRootAliasEvidence"), ensure_ascii=True,
            ) if row.get("crossRootAliasEvidence") else None,
            "measurementStatus": row.get("measurement", {}).get("status"),
            "truePhotoLock": decisions.get("truePhotoLock", {}).get("locked"),
            "workflowSelected": decisions.get("workflowSelected"),
            "configuredIdentityAnchor": ";".join(decisions.get("configuredIdentityAnchor", ())),
            "configuredIdentityAnchorOwners": json.dumps(
                decisions.get("configuredIdentityAnchorOwners", ()), ensure_ascii=True,
            ),
            "sandboxIdentityAnchors": json.dumps(decisions.get("sandboxIdentityAnchors", ()), ensure_ascii=True),
            "sandboxActionHistory": json.dumps(decisions.get("sandboxActionHistory", ()), ensure_ascii=True),
            "reviewFlags": "; ".join(row.get("reviewFlags", ())),
        })
    return output.getvalue().encode("utf-8")


def _manifest_summary(rows, cores, measurements_complete, inventories, issues, collisions):
    roles = {}
    roles_by_origin = {}
    measurements = {}
    integrity = {}
    for row in rows:
        roles[row["role"]] = roles.get(row["role"], 0) + 1
        origin_roles = roles_by_origin.setdefault(row["origin"], {})
        origin_roles[row["role"]] = origin_roles.get(row["role"], 0) + 1
        status = row.get("measurement", {}).get("status", "unknown")
        measurements[status] = measurements.get(status, 0) + 1
        scope_status = row.get("scopeIntegrity", "unknown")
        integrity[scope_status] = integrity.get(scope_status, 0) + 1
    return {
        "sourceInventory": inventories,
        "scopeIssues": issues,
        "collisions": collisions,
        "photoRows": len(rows),
        "roles": dict(sorted(roles.items())),
        "rolesByOrigin": {
            origin: dict(sorted(values.items()))
            for origin, values in sorted(roles_by_origin.items())
        },
        "measurements": dict(sorted(measurements.items())),
        "scopeIntegrity": dict(sorted(integrity.items())),
        "qualifiedIdentityCoreCount": len(cores),
        "qualifiedReferencePhotoCount": sum(core["coreCount"] for core in cores.values()),
        "measurementCoverageComplete": measurements_complete,
    }


def _measurement_coverage(rows):
    working_identity = [
        row for row in rows
        if row["origin"] == "Sandbox" and row["category"] != "Various" and row["bucket"] == "Gallery"
    ]
    current_status = {}
    for row in working_identity:
        status = row.get("measurement", {}).get("status", "unknown")
        current_status[status] = current_status.get(status, 0) + 1
    in_scope = [row for row in rows if row.get("canonical")]
    missing = [
        row for row in rows
        if row.get("measurement", {}).get("status") in (
            "needs-source-bound-measurement", "hold-cache-key-collision",
        )
    ]
    missing_in_scope = [row for row in missing if row.get("canonical")]
    return {
        "currentSandboxIdentityGalleryRows": len(working_identity),
        "currentSandboxIdentityGalleryByMeasurementStatus": dict(sorted(current_status.items())),
        "allPhysicalSourceRows": len(rows),
        "inScopePhysicalRows": len(in_scope),
        "needsSourceBoundMeasurementRows": len(missing),
        "needsSourceBoundMeasurementUniqueRawContents": len({row["sourceSha256"] for row in missing}),
        "inScopeNeedsSourceBoundMeasurementRows": len(missing_in_scope),
        "missingByCategory": {
            category: sum(
                row["category"] == category and row.get("measurement", {}).get("status")
                in ("needs-source-bound-measurement", "hold-cache-key-collision")
                for row in rows
            )
            for category in SOURCE_CATEGORIES
        },
        "missingByOrigin": {
            origin: sum(row["origin"] == origin for row in missing)
            for origin in ("Production", "Sandbox")
        },
        "measurementSourceBinding": "SHA-256 raw bytes plus exact SHA-1 cache key; cache stat paths are not trusted",
        "measurementWritesToLibraryCache": False,
    }


def _preview_samples(rows):
    selected, roles = [], set()
    for preferred in ("frozen-reference", "candidate", "production-exact-alias", "duplicate-alias", "hold"):
        row = next((item for item in rows if item["role"] == preferred), None)
        if row is not None and preferred not in roles:
            selected.append(row)
            roles.add(preferred)
    if len(selected) < 5:
        for row in rows:
            if row not in selected:
                selected.append(row)
            if len(selected) == 5:
                break
    samples = []
    for row in selected:
        sample = {key: row.get(key) for key in (
            "origin", "sourcePath", "photoId", "sourceSha256", "ownerFolder",
            "sourceName", "workingCurrentOwner", "workingCurrentName", "scopeIntegrity",
            "scopeIntegrityReason", "canonical", "canonicalSourceRowId", "aliasOf",
            "aliasType", "exactSourceAliasEvidence", "crossRootAliasEvidence",
            "role", "roleReason",
        )}
        sample["measurement"] = {
            key: value for key, value in row.get("measurement", {}).items() if key != "data"
        }
        decisions = row.get("decisions", {})
        sample["decisions"] = {
            "truePhotoLock": decisions.get("truePhotoLock"),
            "workflowSelected": decisions.get("workflowSelected"),
            "configuredIdentityAnchor": decisions.get("configuredIdentityAnchor"),
            "configuredIdentityAnchorOwners": decisions.get("configuredIdentityAnchorOwners"),
            "sandboxIdentityAnchors": decisions.get("sandboxIdentityAnchors"),
            "sandboxActionHistory": decisions.get("sandboxActionHistory"),
            "sandboxProtection": decisions.get("sandboxProtection"),
            "sandboxRejections": decisions.get("sandboxRejections"),
            "sandboxMembership": (
                {
                    "status": (decisions.get("sandboxMembership", {}).get("value") or {}).get("status"),
                    "coreUse": (decisions.get("sandboxMembership", {}).get("value") or {}).get("coreUse"),
                    "usedForCoreOrRole": False,
                }
                if decisions.get("sandboxMembership") else None
            ),
        }
        samples.append(sample)
    return samples


def _public_manifest(manifest):
    public = copy.deepcopy(manifest)
    for row in public.get("rows", ()):
        measurement = row.get("measurement")
        if isinstance(measurement, dict):
            measurement.pop("data", None)
    return public


def _assert_roots(production, working, cfg):
    from tools.workflows import comfy_workflows as cw

    production = pathlib.Path(production).expanduser().resolve(strict=True)
    working = pathlib.Path(working).expanduser().resolve(strict=True)
    expected_production = cw.production_root(cfg).resolve(strict=True)
    expected_working = cw.sandbox_work_root(cfg).resolve(strict=True)
    if production != expected_production or working != expected_working:
        raise ValueError("manifest roots must exactly match configured Production and Sandbox Working")
    if production == working or production in working.parents or working in production.parents:
        raise ValueError("Production and Sandbox Working roots must not overlap")
    return production, working


def _build(production_root, working_root, run_id, *, emit=True):
    from tools.art import likeness as api
    from tools.art.likeness_library import metadata
    from tools.art.likeness_library.policy import effective_settings, load_policy
    from tools.workflows import comfy_workflows as cw

    cfg = cw.load_cfg()
    production_root, working_root = _assert_roots(production_root, working_root, cfg)
    report_root = working_root / "_reports" / "library" / "rebase-manifests" / run_id
    if report_root.exists():
        raise ValueError(f"report path already exists; choose a new run-id: {report_root}")
    source_rows = []
    scan_issues, missing_categories = [], {"Production": [], "Sandbox": []}
    excluded_artists = {}
    for label, root in (("Production", production_root), ("Sandbox", working_root)):
        rows, issues, missing = _scan_root(root, label)
        source_rows.extend(rows)
        scan_issues.extend({"origin": label, **row} for row in issues)
        missing_categories[label] = missing
        excluded_artists[label] = _count_excluded_artists(root)

    pre_hash_inventory = {
        "Production": {"files": sum(row["origin"] == "Production" for row in source_rows),
                       "bytes": sum(row["byteLength"] for row in source_rows if row["origin"] == "Production")},
        "Sandbox": {"files": sum(row["origin"] == "Sandbox" for row in source_rows),
                    "bytes": sum(row["byteLength"] for row in source_rows if row["origin"] == "Sandbox")},
        "ExcludedArtists": {
            label: {"files": value["files"], "bytes": value["bytes"]}
            for label, value in excluded_artists.items()
        },
    }
    if emit:
        print(json.dumps({
            "phase": "metadata-budget-before-hashing",
            "sourceCountsAndBytes": pre_hash_inventory,
            "BDriveFreeBytes": shutil.disk_usage(working_root).free,
            "message": "No source content has been hashed or modified yet.",
        }, indent=2))

    cache_path, cache = _settings_and_cache(working_root)
    _record_hashes(
        source_rows, cache,
        progress=(lambda done, total, byte_count: print(
            f"source hash progress: {done}/{total} files; {byte_count} bytes"
        )) if emit else None,
    )
    for row in source_rows:
        row["rowId"] = _row_id(row)
    local_catalog, working_catalog_evidence = _load_local_catalog(working_root)
    production_catalog, production_catalog_evidence = _load_local_catalog(production_root)
    anchors = _decision_maps(cfg, source_rows, local_catalog)
    collisions = _classify_unique_sources(source_rows, cfg)

    policy_path = pathlib.Path(ROOT / "data" / "art" / "likeness-engine-policy.json")
    policy = load_policy(policy_path)
    settings = effective_settings(api.configuration(), policy)
    model_root = cw.model_cache_root(cfg)
    models = _source_models(model_root)
    scope_integrity_complete, unresolved_integrity, integrity_diagnostics = _scope_integrity_report(source_rows)
    measured_unavailable = [
        row for row in source_rows
        if row.get("measurement", {}).get("status") in (
            "needs-source-bound-measurement", "hold-cache-key-collision",
        )
    ]
    source_hash_complete = not scan_issues
    measurement_complete = not measured_unavailable
    center_domain = cache.get("centeringDomain")
    center_valid = center_domain in (None, "general")
    complete = source_hash_complete and scope_integrity_complete and measurement_complete and center_valid
    qualification_blockers = []
    if not source_hash_complete:
        qualification_blockers.append("source inventory contains scan or path issues")
    if not scope_integrity_complete:
        qualification_blockers.append(
            f"{len(unresolved_integrity)} source rows have unresolved or unrecognized scope-integrity dispositions"
        )
    if not measurement_complete:
        qualification_blockers.append("source-bound measurement evidence is incomplete")
    if not center_valid:
        qualification_blockers.append("measurement centering evidence is not from the general domain")
    cores, core_ids, core_diagnostics, centering_mean = (
        {}, set(), ["frozen reference qualification pending full source evidence"], None,
    )
    if complete:
        cores, core_ids, core_diagnostics, centering_mean = _qualify_cores(
            source_rows, cfg, policy, cache.get("centeringMean"),
        )
    else:
        core_diagnostics = [
            "frozen reference qualification skipped: " + blocker
            for blocker in qualification_blockers
        ]
    _core_summary, role_diagnostics = _apply_roles(
        source_rows, complete=complete, cores=cores, core_ids=core_ids,
        diagnostics=core_diagnostics,
    )
    names = {
        row["ownerFolder"]: row["sourceNameEvidence"]
        for row in source_rows if row["origin"] == "Production" and row.get("sourceNameEvidence")
    }
    for row in source_rows:
        row.pop("absolutePath", None)
        row["sourcePath"] = row["sourcePath"].replace("\\", "/")
        if row.get("sourceNameEvidence"):
            row["sourceNameEvidence"] = {
                key: value for key, value in row["sourceNameEvidence"].items() if key != "history"
            }

    metadata_files = {}
    for label, root in (("Production", production_root), ("Sandbox", working_root)):
        for relative in (".likeness-library.json", "_origins.json", "people_index.csv", "_cleanup_hold.json"):
            path = root / relative
            if path.is_file():
                if _root_is_reparse(path):
                    raise ValueError(f"linked source metadata is not permitted: {path}")
                metadata_files[f"{label}:{relative}"] = {
                    "path": str(path), "sha256": metadata.content_sha256(path), "bytes": path.stat().st_size,
                }
    if local_catalog is None:
        working_catalog_info = working_catalog_evidence
    else:
        working_catalog_info = working_catalog_evidence
    policy_sha = metadata.content_sha256(policy_path)
    cache_hash = metadata.content_sha256(cache_path) if cache_path.is_file() else None
    names_missing = sorted({
        row["ownerFolder"] for row in source_rows
        if row["origin"] == "Production" and row["category"] != "Various"
        and not row.get("sourceName")
    })
    sandbox_membership_ignored = _working_catalog_summary(local_catalog)
    inputs = {
        "kind": "full-rebase-manifest-proposal",
        "schemaVersion": 1,
        "runId": run_id,
        "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "proposal; actual IDs and roles require human review",
        "roots": {"production": str(production_root), "sandboxWorking": str(working_root)},
        "reportPath": str(report_root),
        "plannedPaths": {
            "runDirectory": str(report_root),
            "proposalJson": str(report_root / MANIFEST_NAME),
            "proposalCsv": str(report_root / CSV_NAME),
            "proposalReceipt": str(report_root / RECEIPT_NAME),
            "measurementEvidenceJson": str(report_root / MEASUREMENTS_NAME),
            "measuredManifestJson": str(report_root / MEASURED_MANIFEST_NAME),
            "measurementReceipt": str(report_root / MEASUREMENT_RECEIPT_NAME),
        },
        "scope": {
            "sources": "Production Gallery/Review/Various originals plus unique content-bound Sandbox arrivals",
            "artists": "excluded from this people-library proposal under the existing separate Artist domain",
            "workingPlacement": "descriptive only; experimental Sandbox membership flags never seed references or roles",
            "rolePolicy": "Production Gallery may provide frozen references; non-core Gallery, Review, Various and verified arrivals are candidates; uncertain/locked/rejected entries remain held",
            "publication": "manifest report only; no reset, source copy, native preparation, matching or assignment",
        },
        "configuration": {
            "workspaceConfigSha256": metadata.content_sha256(ROOT / "workflows" / "workspaces.json"),
            "policyPath": str(policy_path),
            "policyVersion": policy["version"],
            "policyStatus": policy["status"],
            "policySha256": policy_sha,
            "settings": settings,
            "cachePath": str(cache_path),
            "cacheSha256": cache_hash,
            "cacheEntryCount": len(cache.get("emb", {})),
            "cacheFilePresent": cache.get("cacheFilePresent", cache_path.is_file()),
            "cacheEvidenceSource": cache.get("evidenceSource"),
            "cacheCenteringDomain": center_domain,
            "cacheCenteringMeanAvailable": cache.get("centeringMean") is not None,
            "cacheCenteringMeanSha256": (
                hashlib.sha256(json.dumps(cache["centeringMean"], separators=(",", ":")).encode()).hexdigest()
                if cache.get("centeringMean") is not None else None
            ),
            "models": models,
            "modelDownloads": "disabled; only existing local files are reported/used",
        },
        "sourceMetadata": {
            "productionLocalCatalog": production_catalog_evidence,
            "sandboxLocalCatalog": working_catalog_info,
            "sandboxCatalogDisposition": "names, owner, explicit anchors, and action history are disclosed; anchors/actions hold affected rows for review; membership/protection/reference flags are not promoted",
            "workingCatalogSummary": sandbox_membership_ignored,
            "workingCatalogExplicitAnchors": [
                {
                    "personId": person.get("id"),
                    "folder": person.get("folder"),
                    "displayName": person.get("displayName"),
                    "photoIds": sorted(person.get("identityAnchors", ())),
                    "origin": "Sandbox Working local catalogue",
                    "usedForCoreOrRole": False,
                    "status": "disclosed; matching source rows held for review",
                }
                for person in (local_catalog or {}).get("people", {}).values()
                if person.get("identityAnchors")
            ],
            "workingCatalogActionHistory": _working_catalog_action_history(local_catalog),
            "metadataFiles": metadata_files,
            "identityNames": names,
            "missingProductionIdentityNames": names_missing,
            "configuredAnchors": {
                key: sorted({pattern for record in value for pattern in record["patterns"]})
                for key, value in sorted(anchors.items())
            },
            "configuredAnchorOwners": {
                key: value for key, value in sorted(anchors.items())
            },
            "manualDecisionCoverage": {
                "source": "Production folder labels/z_ records and explicit workflows/workspaces.json anchors/keepPhoto selections",
                "configuredAnchorOwnerProvenance": "Configured anchor patterns retain their matched Production owner folder, configured owner key, source path and workflows/workspaces.json origin; ID-shared aliases do not become additional owner claims.",
                "productionCatalogueAvailable": production_catalog is not None,
                "sandboxMembershipUsedAsDecision": False,
                "workingMembershipFlagsIgnored": sandbox_membership_ignored["membershipFlagsIgnored"],
                "workingAnchorsPromotedAsSeed": False,
                "workingActionHistoryDisposition": "disclosed with content hashes and undo status; active matching actions hold rows",
                "unrecordedManualDecisions": "must be reviewed before any subsequent rebase/reset",
            },
        },
        "sourceInventory": {
            "preHashCountsAndBytes": pre_hash_inventory,
            "excludedArtistInventory": excluded_artists,
            "byOriginCategoryBucket": _group_counts(source_rows),
            "missingCategories": missing_categories,
            "scopeIssues": scan_issues,
            "collisions": collisions,
            "sourceHashComplete": source_hash_complete,
            "scopeIntegrityComplete": scope_integrity_complete,
            "unresolvedIntegrityCount": len(unresolved_integrity),
            "scopeIntegrityDiagnostics": integrity_diagnostics,
            "explicitHoldIntegrityCount": len(unresolved_integrity),
            "productionExactIdContentAliasGroups": collisions["productionExactIdContentAliasGroups"],
            "productionExactIdContentAliasRows": collisions["productionExactIdContentAliasRows"],
            "productionExactIdContentAmbiguousGroups": collisions["productionExactIdContentAmbiguousGroups"],
            "crossRootVerifiedProductionAliasRows": collisions["crossRootVerifiedProductionAliasRows"],
        },
        "coreProposal": {
            "status": "qualified" if complete else "pending-source-bound-measurements-or-inventory-resolution",
            "algorithm": "shared normal_finish.cores -> reconciliation.frozen_identity_cores -> audit_person",
            "policyDriven": True,
            "sandboxMembershipFlagsUsed": False,
            "centeringMeanSha256": (
                hashlib.sha256(json.dumps(centering_mean.tolist(), separators=(",", ":")).encode()).hexdigest()
                if centering_mean is not None else None
            ),
            "qualifiedCores": _core_summary,
            "diagnostics": role_diagnostics,
            "qualificationBlockers": qualification_blockers,
            "newNumericalRules": False,
        },
        "rows": source_rows,
        "sourceMeasurementStatus": _measurement_coverage(source_rows),
        "measurementPlan": {
            "priorDocumentedMissingCurrentIdentityMeasurementCount": 3268,
            "currentWorkingIdentityGalleryRows": _measurement_coverage(source_rows)["currentSandboxIdentityGalleryRows"],
            "observedMissingCurrentWorkingIdentityMeasurements": sum(
                row["origin"] == "Sandbox"
                and row["category"] != "Various"
                and row["bucket"] == "Gallery"
                and row.get("measurement", {}).get("status")
                in ("needs-source-bound-measurement", "hold-cache-key-collision")
                for row in source_rows
            ),
            "observedCurrentWorkingIdentityMeasurementsAlreadySHA1Bound": sum(
                row["origin"] == "Sandbox"
                and row["category"] != "Various"
                and row["bucket"] == "Gallery"
                and row.get("measurement", {}).get("status")
                in ("cached-vector", "cached-no-face", "cached-no-usable-vector")
                for row in source_rows
            ),
            "missingSourceRowsToMeasure": len(measured_unavailable),
            "uniqueRawContentMeasurementsToAcquire": len({
                row["sourceSha256"] for row in measured_unavailable
            }),
            "inScopeMissingSourceRows": sum(row["canonical"] for row in measured_unavailable),
            "allMissingRowsRetained": True,
            "reconciliationStatus": "validated-general-domain-cache-source",
            "reconciliation": (
                f"Measurements use tools.art.likeness.Cache from the normal general-domain cache at {cache_path}. "
                "An absent domain cache contributes no cached measurements; no global or legacy cache fallback is used. "
                "Each accepted cache entry remains bound to the raw source SHA-256 and cache-key SHA-1."
            ),
        },
        "implementationHashes": _implementation_hashes(),
    }
    summary = _manifest_summary(
        source_rows, _core_summary, measurement_complete, inputs["sourceInventory"],
        scan_issues, collisions,
    )
    inputs["summary"] = summary
    json_bytes = json.dumps(_public_manifest(inputs), indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    csv_bytes = _csv_bytes(source_rows)
    disk = shutil.disk_usage(working_root)
    inputs["outputEstimate"] = {
        "manifestJsonBytes": len(json_bytes),
        "manifestCsvBytes": len(csv_bytes),
        "estimatedMissingMeasurementEvidenceBytes": (
            4096 + 2048 * len({row["sourceSha256"] for row in measured_unavailable})
        ),
        "estimatedTotalPlannedReportBytes": (
            len(json_bytes) + len(csv_bytes) + 8192
            + 2048 * len({row["sourceSha256"] for row in measured_unavailable})
        ),
        "measurementEstimateMethod": "approximately 2 KiB per distinct missing raw content plus receipt overhead; vectors are report-bound, original photos are never copied",
        "availableWorkingBytes": disk.free,
        "estimatedWorkingBytesAfterReport": max(
            0, disk.free - len(json_bytes) - len(csv_bytes) - 8192
            - 2048 * len({row["sourceSha256"] for row in measured_unavailable})
        ),
        "noPhotoCopies": True,
    }
    # Re-serialize after recording the report estimate.
    json_bytes = json.dumps(_public_manifest(inputs), indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    return inputs, json_bytes, csv_bytes, report_root, {
        "cfg": cfg,
        "policy": policy,
        "cache": cache,
        "cachePath": cache_path,
        "workingCatalog": local_catalog,
        "models": models,
        "measuredRows": measured_unavailable,
    }


def _atomic_exclusive(path, payload):
    path = pathlib.Path(path)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _write_report(manifest, json_payload, csv_payload, report_root, *, measured=False):
    from . import metadata

    report_root = pathlib.Path(report_root)
    if report_root.exists():
        raise ValueError(f"refusing to overwrite an existing report directory: {report_root}")
    if not report_root.parent.is_dir():
        report_root.parent.mkdir(parents=True, exist_ok=True)
    report_root.mkdir()
    json_name = MEASURED_MANIFEST_NAME if measured else MANIFEST_NAME
    csv_name = MEASURED_CSV_NAME if measured else CSV_NAME
    receipt_name = MEASUREMENT_RECEIPT_NAME if measured else RECEIPT_NAME
    _atomic_exclusive(report_root / json_name, json_payload)
    _atomic_exclusive(report_root / csv_name, csv_payload)
    receipt = {
        "schemaVersion": 1,
        "kind": "full-rebase-manifest-report-receipt",
        "runId": manifest["runId"],
        "root": manifest["roots"]["sandboxWorking"],
        "manifest": {"path": json_name, "sha256": _sha256(report_root / json_name)},
        "csv": {"path": csv_name, "sha256": _sha256(report_root / csv_name)},
        "sourceAndImplementationBindings": manifest["implementationHashes"],
        "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "reportOnly": True,
    }
    _atomic_exclusive(report_root / receipt_name, json.dumps(receipt, indent=2).encode("utf-8") + b"\n")
    return receipt


def _verify_report(working_root, run_id):
    from . import metadata

    report_root = pathlib.Path(working_root) / "_reports" / "library" / "rebase-manifests" / run_id
    receipt_path = report_root / RECEIPT_NAME
    if not receipt_path.is_file():
        raise ValueError(f"no applied manifest report receipt: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("kind") != "full-rebase-manifest-report-receipt" or receipt.get("runId") != run_id:
        raise ValueError("manifest report receipt is malformed or bound to another run")
    if pathlib.Path(receipt.get("root", "")).resolve() != pathlib.Path(working_root).resolve():
        raise ValueError("manifest report receipt is bound to another Working root")
    for item in (receipt["manifest"], receipt["csv"]):
        path = report_root / item["path"]
        if not path.is_file() or metadata.content_sha256(path) != item["sha256"]:
            raise ValueError(f"manifest report artifact changed: {path}")
    manifest_path = report_root / receipt["manifest"]["path"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if receipt.get("sourceAndImplementationBindings") != manifest.get("implementationHashes"):
        raise ValueError("manifest code bindings differ from its report receipt")
    current_hashes = _implementation_hashes()
    for name, digest in manifest.get("implementationHashes", {}).items():
        if current_hashes.get(name) != digest:
            raise ValueError(f"implementation changed since manifest preview: {name}")
    roots = manifest.get("roots", {})
    production_root = pathlib.Path(roots.get("production", "")).resolve(strict=True)
    sandbox_root = pathlib.Path(roots.get("sandboxWorking", "")).resolve(strict=True)
    if sandbox_root != pathlib.Path(working_root).resolve(strict=True):
        raise ValueError("manifest proposal is bound to another Sandbox Working root")
    for row in manifest.get("rows", ()):
        expected_root = production_root if row.get("origin") == "Production" else sandbox_root
        source_root = pathlib.Path(row.get("sourceRoot", "")).resolve(strict=True)
        relative = pathlib.PurePosixPath(row.get("sourcePath", ""))
        if source_root != expected_root or not relative.parts or ".." in relative.parts:
            raise ValueError(f"manifest row escapes the approved source roots: {row.get('sourcePath')}")
        path = _assert_no_reparse_components(source_root.joinpath(*relative.parts), source_root)
        if not path.is_file():
            raise ValueError(f"manifest source is missing: {row['sourcePath']}")
        if not path.is_file() or _sha256(path) != row["sourceSha256"]:
            raise ValueError(f"source content changed since manifest preview: {row['sourcePath']}")
    for label, item in manifest.get("sourceMetadata", {}).get("metadataFiles", {}).items():
        path = pathlib.Path(item["path"]).resolve(strict=True)
        root = production_root if production_root in path.parents else sandbox_root
        if root not in path.parents:
            raise ValueError(f"source metadata escapes approved roots: {label}")
        _assert_no_reparse_components(path, root)
        if not path.is_file() or _sha256(path) != item["sha256"]:
            raise ValueError(f"source metadata changed since manifest preview: {label}")
    for folder, evidence in manifest.get("sourceMetadata", {}).get("identityNames", {}).items():
        if not evidence.get("nameFile"):
            continue
        path = pathlib.Path(evidence["nameFile"]).resolve(strict=True)
        if production_root not in path.parents:
            raise ValueError(f"Production identity-name evidence escapes root: {folder}")
        _assert_no_reparse_components(path, production_root)
        if _sha256(path) != evidence["nameFileSha256"]:
            raise ValueError(f"Production identity-name evidence changed: {folder}")
    cache_path = pathlib.Path(manifest["configuration"]["cachePath"])
    expected_cache = manifest["configuration"].get("cacheSha256")
    if expected_cache and (not cache_path.is_file() or _sha256(cache_path) != expected_cache):
        raise ValueError("likeness cache changed since manifest preview")
    if expected_cache is None and cache_path.exists():
        raise ValueError("likeness cache appeared since manifest preview")
    for model in manifest.get("configuration", {}).get("models", ()):
        path = pathlib.Path(model["path"])
        if model.get("available"):
            if (
                not path.is_file() or path.stat().st_size != model.get("bytes")
                or _sha256(path) != model.get("sha256")
            ):
                raise ValueError(f"local model changed since manifest preview: {model.get('name')}")
        elif path.exists():
            raise ValueError(f"local model availability changed since manifest preview: {model.get('name')}")
    measurement_receipt_path = report_root / MEASUREMENT_RECEIPT_NAME
    if measurement_receipt_path.is_file():
        measurement_receipt = json.loads(measurement_receipt_path.read_text(encoding="utf-8"))
        if (
            measurement_receipt.get("kind") != "report-only-measurement-receipt"
            or measurement_receipt.get("runId") != run_id
            or pathlib.Path(measurement_receipt.get("root", "")).resolve() != sandbox_root
            or measurement_receipt.get("sourceManifestSha256") != receipt["manifest"]["sha256"]
        ):
            raise ValueError("measurement report receipt is malformed or bound to another manifest")
        for field, filename in (
            ("measurementsSha256", MEASUREMENTS_NAME),
            ("measuredManifestSha256", MEASURED_MANIFEST_NAME),
            ("measuredCsvSha256", MEASURED_CSV_NAME),
        ):
            path = report_root / filename
            if not path.is_file() or _sha256(path) != measurement_receipt.get(field):
                raise ValueError(f"report-only measurement artifact changed: {filename}")
    return manifest, receipt, report_root


def _measure_missing(working_root, run_id):
    from tools.art import likeness as api
    domains = api.domains

    manifest, receipt, report_root = _verify_report(working_root, run_id)
    output_paths = [
        report_root / MEASUREMENTS_NAME,
        report_root / MEASURED_MANIFEST_NAME,
        report_root / MEASURED_CSV_NAME,
        report_root / MEASUREMENT_RECEIPT_NAME,
    ]
    if any(path.exists() for path in output_paths):
        raise ValueError("measurement report already exists; preserve it and select a new manifest run-id")
    model_records = manifest["configuration"].get("models", [])
    model_root = pathlib.Path(model_records[0]["path"]).parent.parent if model_records else api.DATA
    if model_root.resolve() != pathlib.Path(api.DATA).resolve():
        raise ValueError("configured local model-cache root changed since manifest preview")
    missing_models = [name for name in MODEL_FILES if not (model_root / "models" / name).is_file()]
    if missing_models:
        raise ValueError("local face models are unavailable; downloads are disabled: " + ", ".join(missing_models))
    for model in model_records:
        path = pathlib.Path(model["path"])
        if (
            not model.get("available") or not path.is_file()
            or path.stat().st_size != model.get("bytes")
            or _sha256(path) != model.get("sha256")
        ):
            raise ValueError(f"local model differs from manifest preview: {model.get('name')}")
    pending = [
        row for row in manifest["rows"]
        if row.get("measurement", {}).get("status") == "needs-source-bound-measurement"
    ]
    unique_pending = {}
    for row in pending:
        unique_pending.setdefault(row["sourceSha256"], row)
    read_only_token = domains.READ_ONLY.set(True)
    domain_token = domains.CURRENT.set("general")
    measured = []
    errors = []
    try:
        import cv2
        from likeness_library.engine import AlignmentEvidenceError

        embedder = api.Embedder()
        embedder.configure_evidence(
            report_root / "read-only-alignment-evidence",
            library_root=working_root,
        )
        embedder.load()
        for index, (sha256, row) in enumerate(sorted(unique_pending.items()), 1):
            path = _bound_source_path(row)
            actual_sha, sha1, _size = _hash_source(path)
            if actual_sha != sha256 or sha1 != row["cacheKeySha1"]:
                raise ValueError(f"source changed before report-only measurement: {row['sourcePath']}")
            try:
                data = embedder(path)
            except (OSError, cv2.error, AlignmentEvidenceError) as error:
                errors.append({
                    "sourceSha256": sha256,
                    "sourcePath": row["sourcePath"],
                    "error": f"{type(error).__name__}: {error}",
                    "errorType": type(error).__name__,
                    "recoverable": True,
                })
            else:
                if not isinstance(data, dict):
                    raise TypeError(
                        f"local model returned {type(data).__name__}, not a measurement for {row['sourcePath']}"
                    )
                status = (
                    "report-measured-vector" if data.get("v") and data.get("px", 0) > 0
                    else "report-measured-no-face" if data.get("faces") == 0
                    else "report-measured-no-usable-vector"
                )
                measured.append({
                    "sourceSha256": sha256,
                    "cacheKeySha1": sha1,
                    "sourcePath": row["sourcePath"],
                    "measurementStatus": status,
                    "data": data,
                })
            if index % 100 == 0 or index == len(unique_pending):
                print(f"report-only measurements: {index}/{len(unique_pending)}")
    finally:
        domains.CURRENT.reset(domain_token)
        domains.READ_ONLY.reset(read_only_token)

    measurement_report = {
        "schemaVersion": 1,
        "kind": "report-only-source-measurements",
        "status": "incomplete" if errors else "complete",
        "complete": not errors,
        "runId": run_id,
        "sourceManifestSha256": receipt["manifest"]["sha256"],
        "modelFiles": [
            {"name": name, "sha256": _sha256(model_root / "models" / name),
             "bytes": (model_root / "models" / name).stat().st_size}
            for name in MODEL_FILES
        ],
        "measurementCount": len(measured),
        "errorCount": len(errors),
        "measurements": measured,
        "errors": errors,
        "libraryCacheWritten": False,
        "sourceFilesWritten": False,
        "alignmentArtifactsPersisted": False,
        "measurementPlan": manifest.get("measurementPlan"),
    }
    by_hash = {row["sourceSha256"]: row for row in measured}
    by_hash.update({row["sourceSha256"]: row for row in errors})
    measured_manifest = json.loads(json.dumps(manifest))
    for row in measured_manifest["rows"]:
        evidence = by_hash.get(row["sourceSha256"])
        if evidence and "data" in evidence:
            row["measurement"] = _measurement(
                evidence["data"], evidence["cacheKeySha1"], evidence["sourceSha256"],
            )
            row["measurement"]["status"] = evidence["measurementStatus"]
            row["measurement"]["origin"] = "report-only local-model inference"
        elif evidence:
            row["measurement"] = {
                "status": "measurement-error",
                "sourceSha256": evidence["sourceSha256"],
                "error": evidence["error"],
                "errorType": evidence.get("errorType"),
                "recoverable": evidence.get("recoverable", False),
                "data": None,
            }
    # Qualification is recomputed only when every source measurement is bound.
    cfg = api.cw.load_cfg()
    from .policy import load_policy

    policy = load_policy(ROOT / "data" / "art" / "likeness-engine-policy.json")
    cache_path, cache = _settings_and_cache(working_root)
    if cache_path != pathlib.Path(manifest["configuration"]["cachePath"]):
        raise ValueError("likeness cache location changed since manifest preview")
    for row in measured_manifest["rows"]:
        measurement = row.get("measurement", {})
        if measurement.get("status", "").startswith("cached-"):
            data = cache.get("emb", {}).get(row.get("cacheKeySha1"))
            restored = _measurement(data, row.get("cacheKeySha1"), row.get("sourceSha256"))
            if restored["status"] != measurement["status"] or (
                restored.get("vectorSha256") != measurement.get("vectorSha256")
            ):
                raise ValueError(f"cached measurement changed since manifest preview: {row.get('sourcePath')}")
            measurement["data"] = data
    complete = (
        not errors
        and manifest["sourceInventory"]["sourceHashComplete"]
        and manifest["sourceInventory"]["scopeIntegrityComplete"]
        and cache.get("centeringDomain") in (None, "general")
        and all(
        row.get("measurement", {}).get("status") not in (
            "needs-source-bound-measurement", "hold-cache-key-collision", "measurement-error",
        )
        for row in measured_manifest["rows"]
        )
    )
    cores, core_ids, diagnostics = {}, set(), ["source evidence incomplete; no frozen cores qualified"]
    if complete:
        cores, core_ids, diagnostics, mean = _qualify_cores(
            measured_manifest["rows"], cfg, policy, cache.get("centeringMean"),
        )
        measured_manifest["coreProposal"]["centeringMeanSha256"] = (
            hashlib.sha256(json.dumps(mean.tolist(), separators=(",", ":")).encode()).hexdigest()
            if mean is not None else None
        )
    core_summary, diagnostics = _apply_roles(
        measured_manifest["rows"], complete=complete, cores=cores, core_ids=core_ids,
        diagnostics=diagnostics,
    )
    measured_manifest["coreProposal"].update({
        "status": (
            "measurement-errors-recorded" if errors
            else "qualified" if complete
            else "pending-source-bound-measurements-or-inventory-resolution"
        ),
        "qualifiedCores": core_summary,
        "diagnostics": diagnostics,
    })
    measured_manifest["status"] = (
        f"incomplete measurement report; {len(errors)} recoverable per-image failure(s) recorded"
        if errors else "measurement report; actual IDs and roles still require human review"
    )
    measured_manifest["measurementEvidenceFile"] = MEASUREMENTS_NAME
    measured_manifest["summary"] = _manifest_summary(
        measured_manifest["rows"], core_summary, complete,
        measured_manifest["sourceInventory"], measured_manifest["sourceInventory"]["scopeIssues"],
        measured_manifest["sourceInventory"]["collisions"],
    )
    measurement_payload = json.dumps(measurement_report, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    measured_payload = json.dumps(
        _public_manifest(measured_manifest), indent=2, ensure_ascii=False,
    ).encode("utf-8") + b"\n"
    csv_payload = _csv_bytes(measured_manifest["rows"])
    for path in output_paths:
        if path.exists():
            raise ValueError(f"refusing to overwrite report evidence: {path}")
    _atomic_exclusive(report_root / MEASUREMENTS_NAME, measurement_payload)
    _atomic_exclusive(report_root / MEASURED_MANIFEST_NAME, measured_payload)
    _atomic_exclusive(report_root / MEASURED_CSV_NAME, csv_payload)
    measured_receipt = {
        "schemaVersion": 1,
        "kind": "report-only-measurement-receipt",
        "runId": run_id,
        "root": str(pathlib.Path(working_root).resolve()),
        "sourceManifestSha256": receipt["manifest"]["sha256"],
        "status": "incomplete" if errors else "complete",
        "complete": not errors,
        "measurementsSha256": _sha256(report_root / MEASUREMENTS_NAME),
        "measuredManifestSha256": _sha256(report_root / MEASURED_MANIFEST_NAME),
        "measuredCsvSha256": _sha256(report_root / MEASURED_CSV_NAME),
        "measurementCount": len(measured),
        "errorCount": len(errors),
        "libraryCacheWritten": False,
        "sourceFilesWritten": False,
    }
    _atomic_exclusive(
        report_root / MEASUREMENT_RECEIPT_NAME,
        json.dumps(measured_receipt, indent=2).encode("utf-8") + b"\n",
    )
    print(json.dumps({
        "status": "report-only measurement incomplete" if errors else "report-only measurement complete",
        "measurementCount": len(measured),
        "errorCount": len(errors),
        "measuredManifest": str(report_root / MEASURED_MANIFEST_NAME),
        "receipt": str(report_root / MEASUREMENT_RECEIPT_NAME),
        "noLibraryOrSourceWrites": True,
    }, indent=2))
    return 2 if errors else 0


def _parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--production-root", help="must equal configured Production root")
    parser.add_argument("--working-root", help="must equal configured Sandbox Working root")
    parser.add_argument("--run-id", required=True, help="safe, unique report directory name")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="default; inventory/hash/qualify in memory only")
    mode.add_argument("--apply", action="store_true", help="write only a new JSON/CSV proposal under Working reports")
    mode.add_argument("--check", action="store_true", help="verify the report, code/config bindings and source hashes")
    mode.add_argument("--measure-missing", action="store_true",
                      help="after approved report apply, use local models read-only and write separate measurement evidence")
    return parser


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    if not RUN_ID.fullmatch(args.run_id):
        parser.error("--run-id contains unsupported characters")
    try:
        from tools.workflows import comfy_workflows as cw

        cfg = cw.load_cfg()
        production = pathlib.Path(args.production_root or cw.production_root(cfg)).resolve(strict=True)
        working = pathlib.Path(args.working_root or cw.sandbox_work_root(cfg)).resolve(strict=True)
        production, working = _assert_roots(production, working, cfg)
        if args.check:
            manifest, receipt, report_root = _verify_report(working, args.run_id)
            print(json.dumps({
                "status": "verified",
                "runId": args.run_id,
                "report": str(report_root),
                "manifestRows": len(manifest["rows"]),
                "receiptSha256": _sha256(report_root / RECEIPT_NAME),
            }, indent=2))
            return 0
        if args.measure_missing:
            return _measure_missing(working, args.run_id)
        manifest, payload, csv_payload, report_root, _context = _build(
            production, working, args.run_id, emit=True,
        )
        if args.apply:
            receipt = _write_report(manifest, payload, csv_payload, report_root)
            print(json.dumps({
                "status": "manifest proposal written; human review required",
                "report": str(report_root),
                "receiptSha256": _sha256(report_root / RECEIPT_NAME),
                "manifestSha256": receipt["manifest"]["sha256"],
                "csvSha256": receipt["csv"]["sha256"],
            }, indent=2))
            return 0
        print(json.dumps({
            "status": "preview only; no report or library files written",
            "runId": args.run_id,
            "reportPath": str(report_root),
            "plannedPaths": manifest["plannedPaths"],
            "summary": manifest["summary"],
            "coreProposal": manifest["coreProposal"],
            "sourceMeasurementStatus": manifest["sourceMeasurementStatus"],
            "measurementPlan": manifest["measurementPlan"],
            "outputEstimate": manifest["outputEstimate"],
            "modelAvailability": manifest["configuration"]["models"],
            "sampleRows": _preview_samples(manifest["rows"]),
        }, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"full-rebase manifest stopped safely: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
