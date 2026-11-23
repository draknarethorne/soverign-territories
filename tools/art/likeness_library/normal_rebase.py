"""Stable whole-library composition over the accepted normal-flow primitives."""
import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import re
import sys
import time

import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.art import originals
from tools.art.likeness_library import (
    empty_retirement, face_quality, maintenance, metadata, normal_finish, normal_import, normal_products,
    normal_transaction, normal_recap, reconciliation, rejections, normal_admission,
    verification_reads,
)
from tools.art.likeness_library.policy import effective_settings, load_policy, settle_settings
from tools.art.likeness_library.scoring import nz
from tools.art.likeness_library import sandbox
from tools.art.likeness_library.sandbox import is_normal_flow_proof_path, is_sandbox_working_path

RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
IDENTITY_ROOTS = normal_import.IDENTITY_ROOTS
REQUIRED_VIEWERS = frozenset({
    "gallery.html", "people_gallery.html", "people_gallery_review.html",
    "native-generations.html", "intake_runs.html", "index.html",
})


def _file_sha256(path):
    return metadata.content_sha256(path)


def _naming_digest(photo_id):
    value = photo_id.split(":", 1)[-1]
    return value[4:] if value.startswith("pic_") else value


def _released_photo_bindings(reports, inventory):
    """Conserve already-verified chronological release reports against a frozen inventory.

    This is a pure consistency check, not report, journal, or inventory verification.
    Reports contain ``moves``; inventory rows use the normal source/sourceHash fields.
    """
    def relative(value):
        if (
            not isinstance(value, str) or not value or value.startswith("/")
            or "\\" in value or ":" in value
            or any(part in ("", ".", "..") for part in value.split("/"))
        ):
            raise ValueError("release lineage has an invalid relative path")
        return value

    def digest(value):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("release lineage has an invalid SHA-256")
        return value

    if not isinstance(reports, list) or not reports:
        raise ValueError("release lineage reports are missing")
    current = {}
    for report in reports:
        if not isinstance(report, dict) or not isinstance(report.get("moves"), list):
            raise ValueError("release lineage report moves are missing")
        batch, ids, sources, destinations = [], set(), set(), set()
        occupied = {path.casefold(): photo_id for photo_id, (path, _) in current.items()}
        for move in report["moves"]:
            if not isinstance(move, dict):
                raise ValueError("release lineage move is invalid")
            photo_id = move.get("photoId")
            if not isinstance(photo_id, str) or not photo_id or photo_id != photo_id.strip():
                raise ValueError("release lineage move lacks a stable photo ID")
            source = relative(move.get("source"))
            destination = relative(move.get("destination"))
            checksum = digest(move.get("sha256"))
            source_key, destination_key = source.casefold(), destination.casefold()
            if photo_id in ids or source_key in sources or destination_key in destinations:
                raise ValueError("release lineage has ambiguous moves in one report")
            if photo_id in current and current[photo_id] != (source, checksum):
                raise ValueError(f"{photo_id}: discontinuous release lineage")
            if source_key in occupied and occupied[source_key] != photo_id:
                raise ValueError(f"{photo_id}: ambiguous release source ownership")
            ids.add(photo_id)
            sources.add(source_key)
            destinations.add(destination_key)
            batch.append((photo_id, destination, checksum))
        stationary = {key: photo_id for key, photo_id in occupied.items() if photo_id not in ids}
        if destinations.intersection(stationary):
            raise ValueError("release lineage has an ambiguous occupied destination")
        for photo_id, destination, checksum in batch:
            current[photo_id] = (destination, checksum)
    if not current:
        raise ValueError("release lineage has no move records")
    if not isinstance(inventory, list):
        raise ValueError("release inventory is missing")
    by_id, by_path = collections.defaultdict(list), collections.defaultdict(list)
    for row in inventory:
        if not isinstance(row, dict):
            raise ValueError("release inventory row is invalid")
        source = relative(row.get("source"))
        checksum = digest(row.get("sourceHash"))
        photo_id = row.get("photoId")
        if photo_id is not None and (not isinstance(photo_id, str) or not photo_id):
            raise ValueError("release inventory photo ID is invalid")
        by_id[photo_id].append((source, checksum))
        by_path[source.casefold()].append(photo_id)
    result = []
    for photo_id, (path, checksum) in sorted(current.items()):
        entries = by_id.get(photo_id, [])
        if len(entries) > 1 or len(by_path.get(path.casefold(), [])) > 1:
            raise ValueError(f"{photo_id}: ambiguous release inventory")
        if entries != [(path, checksum)] or by_path.get(path.casefold()) != [photo_id]:
            raise ValueError(f"{photo_id}: missing or stale release inventory")
        result.append({"photoId": photo_id, "currentPath": path, "sha256": checksum})
    return result


def _released_candidate_roles(bindings, active, held, archived=()):
    """Classify every bound release without granting duplicate-content votes.

    A released byte-identical copy is archived like any other duplicate; only
    its keeper is placed by matching.
    """
    expected = {row["photoId"]: (row["currentPath"], row["sha256"]) for row in bindings}
    if len(expected) != len(bindings):
        raise ValueError("ambiguous released candidate bindings")
    roles = {}
    for rows, kind in ((active, "active"), (held, "held"), (archived, "archived")):
        for row in rows:
            photo_id = row.get("photoId")
            if photo_id not in expected:
                continue
            if photo_id in roles or (row.get("source"), row.get("sourceHash")) != expected[photo_id]:
                raise ValueError(f"{photo_id}: ambiguous or changed released source")
            if kind == "active" and row.get("sourceStatus") == "eligible":
                roles[photo_id] = "candidate"
            elif kind == "held" and row.get("sourceStatus") == "same-content-nonvoting":
                roles[photo_id] = "nonvoting-candidate"
            elif (kind == "archived" and row.get("sourceStatus") == "duplicate-archive"
                  and row.get("crossIdExactArchive")):
                roles[photo_id] = "archived-duplicate"
            else:
                raise ValueError(f"{photo_id}: released source requires unresolved disposition")
    if set(roles) != set(expected):
        raise ValueError("released candidates are missing from classified sources")
    return roles


def _fresh_gallery_assessment(root, rows, active, held, photos, native_paths, catalog, settings, policy):
    """Build the selector's complete pre-retirement Gallery evidence from classified sources."""
    from tools.art.likeness_library import audit

    gallery = [row for row in rows if row["group"] in IDENTITY_ROOTS and row["bucket"] == "gallery"]
    classified = {row["source"]: row for row in active + held}
    id_counts = collections.Counter(row.get("photoId") for row in rows if row.get("photoId"))
    people = collections.defaultdict(list)
    for person_id, person in catalog.get("people", {}).items():
        people[person["folder"]].append((person_id, person))
    protected, stale, ambiguous = audit.catalog_photo_flags(
        [(row.get("photoId"), row["sourceHash"]) for row in rows], catalog,
    )
    protected_excluded = audit.core_excluded_protection(catalog, protected)
    excluded = audit.membership_excluded(catalog, [row.get("photoId") for row in gallery if row.get("photoId")])
    inputs = []
    for row in gallery:
        source, photo_id = row["source"], row.get("photoId")
        if row.get("sourceStatus") == "duplicate-archive":
            # Archived recoverably before core formation; it neither votes nor is released.
            continue
        if source not in classified or classified[source] is not row or source not in photos:
            raise ValueError(f"{source}: initial Gallery source was not classified and measured")
        if row.get("sourceStatus") not in ("eligible", "same-content-nonvoting"):
            raise ValueError(f"{source}: initial Gallery source requires unresolved disposition: {row.get('sourceStatus')}")
        owner_records = people.get(row["owner"], [])
        person_id, person = owner_records[0] if len(owner_records) == 1 else (None, None)
        owner_ids = sorted(rejections.identity_ids(catalog, person_id)) if person_id else []
        record = catalog.get("photos", {}).get(photo_id, {})
        state = rejections.candidate_state(catalog, photo_id, row["sourceHash"])
        parent = record.get("membership", {}).get("personId")
        parent_owner = catalog.get("people", {}).get(parent, {}).get("folder") if parent else row["owner"]
        identity_ambiguous = (
            len(owner_records) > 1 or bool(person and person.get("mergedInto"))
            or parent_owner != row["owner"]
        )
        source_ambiguous = photo_id in stale or photo_id in ambiguous or id_counts[photo_id] != 1
        photo = photos[source]
        vector = photo.vec
        if vector is not None:
            vector = np.asarray(vector, dtype=float)
            if vector.ndim != 1 or not vector.size or not np.isfinite(vector).all():
                raise ValueError(f"{source}: invalid centered measurement")
            if not np.linalg.norm(vector):
                vector = None
        quality = bool(
            photo.usable(settings["minFace"]) and photo.faces == 1
            and getattr(photo, "f2", 0.) <= settings["multiFace"] and vector is not None
        )
        anchor = bool(person and photo_id in person.get("identityAnchors", ()))
        rejected = list(record.get("rejectedPersonIds", []))
        stale_rejection = bool(state.get("rejectionMetadataStale"))
        eligible = bool(
            row["sourceStatus"] == "eligible" and quality and not source_ambiguous
            and not identity_ambiguous and not stale_rejection and not set(rejected).intersection(owner_ids)
            and photo_id not in excluded and (photo_id not in protected_excluded or anchor)
            and not (person and person.get("identityStatus") == "provisional")
        )
        measured_path = native_paths.get(source, root / pathlib.PurePosixPath(source))
        inputs.append({
            "photoId": photo_id, "owner": row["owner"], "currentPath": source,
            "sha256": row["sourceHash"], "measurementSha256": metadata.content_sha256(measured_path),
            "vector": vector, "qualityEligible": quality, "referenceEligible": eligible,
            "identityAnchor": anchor, "identityAmbiguous": identity_ambiguous,
            "sourceAmbiguous": source_ambiguous, "rejectionMetadataStale": stale_rejection,
            "ownerPersonIds": owner_ids, "rejectedPersonIds": rejected,
            "sourceStatus": row["sourceStatus"], "standardName": row.get("standardName"),
        })
    duplicate_votes = _single_vote_per_content(inputs)
    result = normal_admission.fresh_baseline_release_candidates(inputs, policy)
    result["duplicateContentVotes"] = duplicate_votes
    if result["blockedBindings"]:
        raise ValueError("fresh source release has ambiguous, stale or unbindable Gallery selections: "
                         + ", ".join(item["currentPath"] for item in result["blockedBindings"]))
    return result


def _seed_score_against(decision, owner):
    """Recorded post-release score against the released photo's own seeded identity, if any."""
    def number(value):
        return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None

    if decision.get("bestMatch") == owner and number(decision.get("bestScore")) is not None:
        return number(decision["bestScore"])
    routing = decision.get("routingEvidence") or {}
    if routing.get("winner") == owner and number(routing.get("score")) is not None:
        return number(routing["score"])
    cast = decision.get("castAdmission") or {}
    if cast.get("winner") == owner and number(cast.get("score")) is not None:
        return number(cast["score"])
    for item in [*(cast.get("alternatives") or []), *(decision.get("lowerCategoryEvidence") or [])]:
        if isinstance(item, dict) and item.get("folder") == owner and number(item.get("score")) is not None:
            return number(item["score"])
    unresolved = decision.get("unresolvedReleaseReview") or {}
    if unresolved.get("target") == f"{owner}/review" and number(unresolved.get("score")) is not None:
        return number(unresolved["score"])
    return None


def _fresh_cast_seed_outcomes(assessment, moves, archives, released_evidence, workflow_ids):
    """Report where each released Sisters/Angels member landed and propose workflow replacements.

    Planning evidence only: workflow configuration is never changed. A released
    workflow-selected photo that does not return to its identity Gallery gets
    the highest initial own-scoring other photo of that identity that remains
    in its Gallery after this plan, excluding other workflow selections.
    """
    seed = assessment["castSeed"]
    final = {(move["photoId"], move["source"]): move["destination"] for move in moves}
    decisions = {item["photoId"]: item for item in released_evidence}

    def location(row):
        archive = archives.get(row["currentPath"])
        if archive and archive.get("photoId") == row["photoId"]:
            return archive["destination"], "archived-duplicate"
        return final.get((row["photoId"], row["currentPath"]), row["currentPath"]), None

    identities, proposals, used = [], [], set()
    for owner, info in sorted(seed["identities"].items()):
        members = sorted(
            (row for row in assessment["assessment"] if row["owner"] == owner),
            key=lambda row: (row["currentPath"].casefold(), row["currentPath"]),
        )
        remaining, released = [], []
        for row in members:
            destination, special = location(row)
            path = pathlib.PurePosixPath(destination)
            folder, bucket = path.parent.parent.as_posix(), path.parent.name
            if special is None and folder == owner and bucket == "gallery":
                remaining.append((row, destination))
            if not row["selected"]:
                continue
            outcome = (
                special or ("returned-gallery" if folder == owner and bucket == "gallery" else
                            "own-review" if folder == owner and bucket == "review" else "elsewhere")
            )
            decision = (decisions.get(row["photoId"]) or {}).get("decision") or {}
            released.append({
                "photoId": row["photoId"], "currentPath": row["currentPath"], "sha256": row["sha256"],
                "beforeScore": row["score"], "beforeBand": row["band"],
                "seedRank": (row.get("castSeed") or {}).get("rank"),
                "selectionReasons": list(row["selectionReasons"]),
                "outcome": outcome, "finalPath": destination,
                "afterScore": _seed_score_against(decision, owner),
                "afterBestMatch": decision.get("bestMatch"),
                "afterBestScore": decision.get("bestScore"),
                "workflowSelected": row["photoId"] in workflow_ids,
            })
        candidates = sorted(
            (item for item in remaining
             if item[0]["score"] is not None and item[0]["photoId"] not in workflow_ids),
            key=lambda item: (-item[0]["score"], item[1].casefold(), item[1]),
        )
        for item in released:
            if not item["workflowSelected"] or item["outcome"] == "returned-gallery":
                continue
            choice = next((row for row in candidates if row[0]["photoId"] not in used), None)
            replacement = None
            if choice is not None:
                used.add(choice[0]["photoId"])
                replacement = {
                    "photoId": choice[0]["photoId"], "currentPath": choice[0]["currentPath"],
                    "finalPath": choice[1], "ownScore": choice[0]["score"],
                }
            proposals.append({
                "identity": owner, "photoId": item["photoId"], "currentPath": item["currentPath"],
                "outcome": item["outcome"], "finalPath": item["finalPath"], "replacement": replacement,
                "basis": ("highest initial own score among this identity's photos remaining in its Gallery "
                          "after the plan, excluding workflow selections; configuration is not changed"),
            })
        identities.append({
            "identity": owner, "memberCount": info["memberCount"],
            "seedSize": len(info["seedPhotoIds"]), "seedPhotoIds": list(info["seedPhotoIds"]),
            "seedBandExemptCount": len(info["seedBandExemptPhotoIds"]),
            "releasedCount": len(released),
            "seedReleaseCount": len(info["seedReleasedPhotoIds"]),
            "returnedCount": sum(item["outcome"] == "returned-gallery" for item in released),
            "released": released,
        })
    seed_ids = {pid for info in seed["identities"].values() for pid in info["seedReleasedPhotoIds"]}
    return {
        "topCount": seed["topCount"], "releaseBelow": seed["releaseBelow"],
        "identities": identities, "workflowReplacementProposals": proposals,
        "summary": {
            "identityCount": len(identities),
            "seedKeptCount": seed["seedKeptCount"], "seedReleaseCount": seed["seedReleaseCount"],
            "seedReturnedCount": sum(
                item["outcome"] == "returned-gallery"
                for identity in identities for item in identity["released"] if item["photoId"] in seed_ids
            ),
        },
        "configurationChanged": False,
    }


def _single_vote_per_content(inputs):
    """Leave one reference vote per source or prepared-measurement content; others stay scored non-voters."""
    parent = {}

    def find(index):
        while parent.setdefault(index, index) != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    eligible = [index for index, row in enumerate(inputs) if row["referenceEligible"]]
    first = {}
    for index in eligible:
        for key in ("sha256", "measurementSha256"):
            seen = first.setdefault((key, inputs[index][key]), index)
            parent[find(index)] = find(seen)
    groups = collections.defaultdict(list)
    for index in eligible:
        groups[find(index)].append(index)
    records = []
    for members in groups.values():
        if len(members) < 2:
            continue
        members.sort(key=lambda index: (inputs[index]["currentPath"].casefold(), inputs[index]["currentPath"]))
        for index in members[1:]:
            inputs[index]["referenceEligible"] = False
        records.append({
            "keeper": inputs[members[0]]["photoId"],
            "nonVoting": [inputs[index]["photoId"] for index in members[1:]],
            "paths": [inputs[index]["currentPath"] for index in members],
        })
    return sorted(records, key=lambda row: row["paths"][0].casefold())


def _fresh_measurement_proof(root, measured_rows, raw_data, native_paths, embedder, mean):
    """Bind the entire centering population and vectors to one current local model."""
    import cv2

    model, model_id = embedder._model_identity(cv2)
    measurements = []
    for row in sorted(measured_rows, key=lambda item: item["source"]):
        source = row["source"]
        path = native_paths.get(source, root / pathlib.PurePosixPath(source))
        native_hash = metadata.content_sha256(path)
        digest, data = raw_data[source]
        if not isinstance(data, dict):
            raise ValueError(f"{source}: fresh assessment measurement unavailable")
        evidence = data.get("alignmentEvidence") or {}
        if data.get("v") and (
            evidence.get("state") not in ("persisted", "read-only-not-persisted")
            or evidence.get("sourceSha256") != native_hash
            or evidence.get("modelId") != model_id or evidence.get("model") != model
        ):
            raise ValueError(f"{source}: fresh assessment measurement lacks current source/model provenance")
        measurements.append({
            "source": source, "sourceSHA256": row["sourceHash"], "measurementSHA256": native_hash,
            "cacheKey": digest, "vector": data.get("v"), "faces": data.get("faces"),
            "facePixels": data.get("px"), "secondaryFaceRatio": data.get("f2"),
        })
    centered = np.asarray(mean, dtype=float)
    if centered.ndim != 1 or not centered.size or not np.isfinite(centered).all():
        raise ValueError("fresh assessment centering mean is unavailable or invalid")
    return {
        "modelId": model_id, "model": model, "centeringMean": centered.tolist(),
        "measurementCount": len(measurements),
        "measurementsSHA256": _preparation_fingerprint(measurements),
    }


def _fragment_evidence(reference_space, cores, catalog, policy, blocked_ids):
    references = {folder: [] for folder in cores}
    for photo in reference_space.photos:
        core = cores.get(photo.key)
        photo_id = metadata.photo_id_from_name(photo.name)
        if core is None or photo_id not in core["corePhotoIds"]:
            continue
        checksum = metadata.content_sha256(photo.path)
        references[photo.key].append({
            "photoId": photo_id, "sha256": checksum, "vector": photo.vec,
            "qualityEligible": (
                photo.usable(reference_space.st["minFace"]) and photo.faces == 1
                and getattr(photo, "f2", 0.) <= reference_space.st["multiFace"]
            ),
            **rejections.candidate_state(catalog, photo_id, checksum),
        })
    return reconciliation.fragment_proposals(
        cores, references, policy, blocked_ids=blocked_ids,
    )


def _validate_stable_viewers(paths):
    by_name = {pathlib.Path(path).name: pathlib.Path(path) for path in paths}
    missing = sorted(REQUIRED_VIEWERS - set(by_name))
    if missing:
        raise ValueError("stable Gallery/Overview/Review/history viewer set is incomplete: " + ", ".join(missing))
    for name in sorted(REQUIRED_VIEWERS):
        path = by_name[name]
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"stable Gallery/Overview/Review/history viewer set is incomplete: missing or empty {path}")
        if "<html" not in path.read_text(encoding="utf-8").casefold():
            raise ValueError(f"required stable viewer is not an HTML page: {path}")
    return [str(by_name[name]) for name in sorted(REQUIRED_VIEWERS)]


def _preparation_fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _write_new_json(path, value):
    import os

    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise ValueError(f"preparation origin record already exists: {path}") from exc
    return metadata.content_sha256(path)


def _preparation_origin_paths(output):
    run = pathlib.Path(output).resolve().parents[4]
    return run / "preparation-origin.start.json", run / "preparation-origin.complete.json"


def _write_preparation_origin_start(root, cfg, run, profile, source_paths, *, workers=1):
    from tools.art import image_preparation
    from tools.workflows import comfy_workflows as cw

    normal_products.validate_workers(workers)
    root = pathlib.Path(root).resolve()
    run = pathlib.Path(run).resolve()
    if root not in run.parents:
        raise ValueError("preparation origin records must remain under this Working root")
    output = run / "preparation" / "inputs" / "_reports" / "preparation" / "selected"
    mirror = output.parents[2]
    input_rows = sorted(
        (pathlib.Path(path).resolve().relative_to(root).as_posix(),
         metadata.content_sha256(path))
        for path in source_paths
    )
    configuration = cw.storage_configuration_receipt(
        cfg,
        mirror,
        {
            "runOutput": output,
            "temporaryRoot": cw.storage_root(cfg, "temporary", root=mirror),
        },
    )
    producer = metadata.content_sha256(pathlib.Path(image_preparation.__file__))
    record = {
        "kind": "normal-rebase-preparation-origin-start",
        "schemaVersion": 1,
        "root": str(root),
        "preparationRoot": str(output),
        "profile": profile,
        "workers": workers,
        "generationProducerSHA256": producer,
        "recipeSHA256": _preparation_fingerprint(image_preparation.RECIPE),
        "configurationReceiptSHA256": _preparation_fingerprint(configuration),
        "inputCount": len(input_rows),
        "inputSetSHA256": _preparation_fingerprint(input_rows),
    }
    start_path, _complete_path = _preparation_origin_paths(output)
    start_hash = _write_new_json(start_path, record)
    if metadata.content_sha256(pathlib.Path(image_preparation.__file__)) != producer:
        raise ValueError("image_preparation.py changed before selected preparation started")
    return record, start_path, start_hash


def _write_preparation_origin_complete(root, cfg, profile, source_paths, prepared, start_record, start_hash):
    from tools.art import image_preparation
    from tools.workflows import comfy_workflows as cw

    output, data, _native = prepared
    output = pathlib.Path(output).resolve()
    root = pathlib.Path(root).resolve()
    producer_after = metadata.content_sha256(pathlib.Path(image_preparation.__file__))
    if producer_after != start_record["generationProducerSHA256"]:
        raise ValueError("image_preparation.py changed while selected preparation was running")
    mirror = output.parents[2]
    configuration = cw.storage_configuration_receipt(
        cfg,
        mirror,
        {
            "runOutput": output,
            "temporaryRoot": cw.storage_root(cfg, "temporary", root=mirror),
        },
    )
    input_rows = sorted(
        (path.relative_to(root).as_posix(), metadata.content_sha256(path))
        for path in source_paths
    )
    if (
        data.get("recipe") != image_preparation.RECIPE
        or _preparation_fingerprint(data.get("recipe")) != start_record["recipeSHA256"]
        or data.get("configurationReceipt") != configuration
        or _preparation_fingerprint(configuration) != start_record["configurationReceiptSHA256"]
        or sorted((row["source"], row["sourceSha256"]) for row in data["photos"]) != input_rows
        or len(input_rows) != start_record["inputCount"]
        or _preparation_fingerprint(input_rows) != start_record["inputSetSHA256"]
        or data.get("storageMode", "full") != ("full" if profile == "full" else "lean")
        or str(output) != start_record["preparationRoot"]
    ):
        raise ValueError("completed preparation differs from its start origin seal")
    record = {
        "kind": "normal-rebase-preparation-origin-complete",
        "schemaVersion": 1,
        "root": str(root),
        "preparationRoot": str(output),
        "profile": profile,
        "workers": start_record["workers"],
        "generationProducerSHA256": start_record["generationProducerSHA256"],
        "producerAfterGenerationSHA256": producer_after,
        "producerUnchangedDuringGeneration": True,
        "startRecordSHA256": start_hash,
        "manifestSHA256": metadata.content_sha256(output / "manifest.json"),
        "recipeSHA256": start_record["recipeSHA256"],
        "configurationReceiptSHA256": start_record["configurationReceiptSHA256"],
        "inputCount": start_record["inputCount"],
        "inputSetSHA256": start_record["inputSetSHA256"],
    }
    _start_path, complete_path = _preparation_origin_paths(output)
    _write_new_json(complete_path, record)
    return record


def _read_preparation_origin(output, data, root, profile, input_rows, manifest_hash):
    from tools.art import image_preparation

    start_path, complete_path = _preparation_origin_paths(output)
    start_exists, complete_exists = start_path.is_file(), complete_path.is_file()
    if not start_exists and not complete_exists:
        return None
    if not start_exists or not complete_exists:
        raise ValueError("reused preparation has an incomplete generation-origin seal")
    try:
        start = json.loads(start_path.read_text(encoding="utf-8"))
        complete = json.loads(complete_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read preparation origin seal: {exc}") from exc
    expected = {
        "root": str(pathlib.Path(root).resolve()),
        "preparationRoot": str(pathlib.Path(output).resolve()),
        "profile": profile,
        "recipeSHA256": _preparation_fingerprint(data["recipe"]),
        "configurationReceiptSHA256": _preparation_fingerprint(data["configurationReceipt"]),
        "inputCount": len(input_rows),
        "inputSetSHA256": _preparation_fingerprint(input_rows),
    }
    if (
        start.get("kind") != "normal-rebase-preparation-origin-start"
        or start.get("schemaVersion") != 1
        or any(start.get(key) != value for key, value in expected.items())
        or complete.get("kind") != "normal-rebase-preparation-origin-complete"
        or complete.get("schemaVersion") != 1
        or any(complete.get(key) != value for key, value in expected.items())
        or complete.get("manifestSHA256") != manifest_hash
        or complete.get("generationProducerSHA256") != start.get("generationProducerSHA256")
        or complete.get("workers") != start.get("workers")
        or ("workers" in start and (
            isinstance(start["workers"], bool) or not isinstance(start["workers"], int)
            or not 1 <= start["workers"] <= 3
        ))
        or complete.get("producerAfterGenerationSHA256") != start.get("generationProducerSHA256")
        or complete.get("producerUnchangedDuringGeneration") is not True
        or complete.get("startRecordSHA256") != metadata.content_sha256(start_path)
        or not re.fullmatch(r"[0-9a-f]{64}", str(start.get("generationProducerSHA256", "")))
    ):
        raise ValueError("reused preparation origin seal does not match its manifest and inputs")
    return complete


def _validate_preparation_reuse(root, cfg, profile, prepared, source_paths):
    from tools.art import image_preparation
    from tools.workflows import comfy_workflows as cw

    root = pathlib.Path(root).resolve()
    output, data, _native = prepared
    output = pathlib.Path(output).resolve()
    reports = cw.storage_root(cfg, "reports", root=root).resolve()
    try:
        relative = output.relative_to(reports)
    except ValueError as exc:
        raise ValueError("reused preparation must be under this Working reports root") from exc
    if (
        len(relative.parts) != 7
        or relative.parts[0] != "runs"
        or not relative.parts[1].startswith("normal-rebase-")
        or not relative.parts[1].endswith("-preview")
        or relative.parts[2:] != (
            "preparation", "inputs", "_reports", "preparation", "selected",
        )
    ):
        raise ValueError("reused preparation is not a prior stable rebase preview output")
    if data.get("recipe") != image_preparation.RECIPE:
        raise ValueError("reused preparation recipe differs from the current producer")
    expected_mode = "full" if profile == "full" else "lean"
    if data.get("storageMode", "full") != expected_mode:
        raise ValueError("reused preparation profile differs from the current rebase")
    mirror = output.parents[2]
    expected_configuration = cw.storage_configuration_receipt(
        cfg,
        mirror,
        {
            "runOutput": output,
            "temporaryRoot": cw.storage_root(cfg, "temporary", root=mirror),
        },
    )
    if data.get("configurationReceipt") != expected_configuration:
        raise ValueError("reused preparation configuration differs from the current configuration")
    input_rows = sorted(
        (row["source"], row["sourceSha256"]) for row in data["photos"]
    )
    expected_inputs = sorted(
        (path.relative_to(root).as_posix(), metadata.content_sha256(path))
        for path in source_paths
    )
    aliases = data.get("reuseSourceAliases", {})
    mapped_inputs = [
        (aliases.get(source, {}).get("preparedSource", source), digest)
        for source, digest in expected_inputs
    ]
    if (
        not expected_inputs
        or len(input_rows) != len(set(source for source, _digest in input_rows))
        or not set(mapped_inputs).issubset(input_rows)
        or not set(aliases).issubset(source for source, _digest in expected_inputs)
        or any(aliases[source]["sourceSha256"] != digest
               for source, digest in expected_inputs if source in aliases)
    ):
        raise ValueError("reused preparation source bindings differ from the selected inputs")
    manifest_hash = metadata.content_sha256(output / "manifest.json")
    generation_seal = _read_preparation_origin(
        output, data, root, profile, input_rows, manifest_hash,
    )
    validation_producer = metadata.content_sha256(pathlib.Path(image_preparation.__file__))
    return {
        "kind": "verified-existing-selected-preparation",
        "path": str(output),
        "manifestSHA256": manifest_hash,
        "recipeId": data["recipe"]["id"],
        "recipeSHA256": _preparation_fingerprint(data["recipe"]),
        "generationProducerSHA256": (
            generation_seal["generationProducerSHA256"] if generation_seal else None
        ),
        "generationProvenance": (
            "origin-sealed" if generation_seal else "legacy-generation-hash-unrecorded"
        ),
        "validationProducerSHA256": validation_producer,
        "provenanceWarning": (
            None if generation_seal else
            "Legacy preparation manifest does not record its historical image_preparation.py hash."
        ),
        "generationSeal": generation_seal,
        "configurationReceiptSHA256": _preparation_fingerprint(data["configurationReceipt"]),
        "profile": profile,
        "inputCount": len(input_rows),
        "inputSetSHA256": _preparation_fingerprint(input_rows),
        "selectedInputCount": len(expected_inputs),
        "selectedInputSetSHA256": _preparation_fingerprint(expected_inputs),
        "unusedVerifiedInputCount": len(input_rows) - len(set(mapped_inputs)),
        "selectedSourceAliases": aliases,
    }


def _prepare_with_origin(root, cfg, run, profile, source_paths, *, workers=1):
    normal_products.require_worker_memory(workers)
    start_record, _start_path, start_hash = _write_preparation_origin_start(
        root, cfg, run, profile, source_paths, workers=workers,
    )
    prepared = normal_products.prepare(
        root, pathlib.Path(run) / "preparation", source_paths, profile, workers=workers,
    )
    generation_seal = _write_preparation_origin_complete(
        root, cfg, profile, source_paths, prepared, start_record, start_hash,
    )
    validated = _validate_preparation_reuse(root, cfg, profile, prepared, source_paths)
    if validated.get("generationSeal") != generation_seal:
        raise ValueError("completed preparation origin seal failed verification")
    return prepared, generation_seal


def _validate_move_destinations(moves):
    destinations = {}
    for move in moves:
        destination = move["destination"]
        if metadata.photo_id_from_name(pathlib.PurePosixPath(destination).name) != move["photoId"]:
            raise ValueError(f"planned destination changes the stable photo ID: {move['source']} -> {destination}")
        key = destination.casefold()
        if key in destinations:
            raise ValueError(
                f"planned destination collision: {destinations[key]} and {move['source']} -> {destination}"
            )
        destinations[key] = move["source"]


def _exact_alias_targets(rows, moves, *, updates=None, archives=None):
    by_source = {row["source"].casefold(): row for row in rows}
    aliases = {}
    for move in moves:
        target = by_source.get(move["destination"].casefold())
        update = (updates or {}).get(move["photoId"])
        if update is not None:
            source = by_source.get(move["source"].casefold())
            if not (
                source and target
                and source.get("sourceStatus") == "incoming-update"
                and move["source"] == update["source"]
                and move["destination"] == update["previousSource"]
                and move["sha256"] == update["sourceHash"] == source["sourceHash"]
                and target["sourceHash"] == update["previousHash"]
                and source["photoId"] == target["photoId"] == move["photoId"]
                and target.get("sourceStatus") == "preserved-version"
                and target.get("selectedSource") == move["source"]
            ):
                raise ValueError(f"planned destination is not its bound incoming replacement: {move['destination']}")
            continue
        if not target or target["source"].casefold() == move["source"].casefold():
            continue
        archive = (archives or {}).get(target["source"])
        if archive and (
            target["source"] == move["destination"]
            and archive["selectedSource"] == move["source"]
            and archive["photoId"] == move["photoId"]
        ):
            continue
        if not (
            target.get("sourceStatus") == "exact-byte-alias"
            and target.get("canonicalSource") == move["source"]
            and target["photoId"] == move["photoId"]
            and target["sourceHash"] == move["sha256"]
        ):
            raise ValueError(
                f"planned destination is not its source's verified exact alias: {move['destination']}"
            )
        aliases[move["destination"]] = {
            "source": move["source"], "sha256": move["sha256"],
        }
    return aliases


def _check_frozen_consistency(api, space, catalog, policy, moves, *, update_ids=()):
    pool_moves = [
        row for row in moves
        if pathlib.PurePosixPath(row["destination"]).parts[0] == "Various"
    ]
    identity_moves = [row for row in moves if row not in pool_moves]
    checked, audit = normal_finish.check_batch(
        api, space, catalog, policy, identity_moves, update_ids=update_ids,
    )
    checked.extend(pool_moves)
    audit["poolRetention"] = [
        {
            "photoId": row["photoId"],
            "destination": row["destination"],
            "decision": "retain-in-Various-pool",
            "reason": (
                "Various pool destinations are not identity categories; preserve the candidate role "
                "without applying identity-category consistency policy"
            ),
        }
        for row in pool_moves
    ]
    return checked, audit


def _ensure_intake_viewer(root, cfg, profile, prepared):
    from html import escape
    import os
    from tools.workflows import comfy_workflows as cw

    output = cw.storage_root(cfg, "reports", root=root) / "library" / "intake_runs.html"
    if not output.exists():
        if profile == "fast":
            detail = (
                "<p>FAST used original-byte matching. Image editing and 944 framing are deferred; "
                "no image preparation artifacts are claimed for this run.</p>"
            )
        elif prepared and (pathlib.Path(prepared[0]) / "index.html").is_file():
            relative = os.path.relpath(
                pathlib.Path(prepared[0]) / "index.html", output.parent,
            ).replace(os.sep, "/")
            detail = (
                "<p>Accepted selected-input preparation report:</p><p><a href=\""
                + escape(relative, quote=True) + "\">FULL/LEAN preparation details</a></p>"
            )
        else:
            detail = "<p>No selected-image preparation was required for this run.</p>"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            "<!doctype html><html><head><meta charset='utf-8'><title>Rebase intake runs</title></head>"
            "<body><h1>Rebase intake runs</h1>" + detail + "</body></html>\n",
            encoding="utf-8",
        )
    return output


def _hash_sources(root, cfg, api):
    root = pathlib.Path(root).resolve()
    rows = []
    folders = api.cw.photo_folders(cfg, root)
    prefixes = sorted(
        {originals.prefix_of(name) for group, name, _folder in folders if group in IDENTITY_ROOTS},
        key=lambda item: (-len(item), item.casefold()),
    )
    for group, name, folder in folders:
        supported_group = group in IDENTITY_ROOTS or group == "Various"
        folder = pathlib.Path(folder)
        owner = f"{group}/{name}" if name != group else group
        for bucket in ("gallery", "review"):
            for path in originals.images(folder / bucket):
                resolved = path.resolve()
                if resolved != path or root not in resolved.parents:
                    raise ValueError(f"source is a linked or escaping path: {path}")
                digest = _file_sha256(path)
                photo_id = metadata.photo_id_from_name(path.name)
                if not supported_group:
                    rows.append({
                        "source": path.relative_to(root).as_posix(),
                        "sourceHash": digest, "originalName": path.name,
                        "owner": owner, "group": group, "folderName": name,
                        "bucket": bucket, "photoId": photo_id,
                        "idBasis": "separate-domain-filename" if photo_id else "separate-domain-unassigned",
                        "sourceStatus": "excluded-separate-domain",
                        "reason": "separate domain is preserved and is not part of the stable general-library likeness pass",
                    })
                    continue
                retained = None
                from tools.art.likeness_library import retained_preparation

                if retained_preparation.claims_photo(root, path):
                    retained = retained_preparation.verify_link(root, path)
                    if (
                        retained is None or not retained.get("photoId")
                        or (photo_id and retained["photoId"] != photo_id)
                    ):
                        rows.append({
                            "source": path.relative_to(root).as_posix(),
                            "sourceHash": digest, "originalName": path.name,
                            "owner": owner, "group": group, "folderName": name,
                            "bucket": bucket,
                            "photoId": photo_id, "idBasis": "invalid-retained-lineage",
                            "sourceStatus": "held",
                            "reason": "retained preparation claims this photo but its ID/source/current-byte binding is invalid or conflicting",
                        })
                        continue
                    photo_id = photo_id or retained["photoId"]
                if retained:
                    id_basis = "verified-retained-photo-id"
                elif photo_id:
                    id_basis = "filename"
                else:
                    proposed_name = normal_import._arrival_name(path, originals, metadata)
                    photo_id = metadata.photo_id_from_name(proposed_name)
                    if not photo_id:
                        raise ValueError(f"existing original naming rules produced no stable ID: {path}")
                    id_basis = (
                        "raw-content-sha1-8" if photo_id.startswith("photo:pic_")
                        else "normalized-source-filename"
                    )
                target_prefix = originals.prefix_of(name)
                name_basis = path.name
                if retained and not metadata.photo_id_from_name(name_basis):
                    name_basis = pathlib.PurePosixPath(retained["row"]["source"]).name
                standard_name = originals.standard_name(
                    name_basis, target_prefix, known=prefixes,
                    digest=_naming_digest(photo_id),
                )
                if metadata.photo_id_from_name(standard_name) != photo_id:
                    standard_name = originals.standard_name(
                        "incoming.jpg", target_prefix, known=prefixes,
                        digest=_naming_digest(photo_id),
                    )
                if metadata.photo_id_from_name(standard_name) != photo_id:
                    rows.append({
                        "source": path.relative_to(root).as_posix(),
                        "sourceHash": digest, "originalName": path.name,
                        "owner": owner, "group": group, "folderName": name,
                        "bucket": bucket, "photoId": photo_id, "idBasis": id_basis,
                        "sourceStatus": "held",
                        "reason": "existing ID or verified lineage has no safe standard filename representation",
                        "retainedSourceHash": retained.get("sourceSha256") if retained else None,
                        "retainedSource": retained.get("row", {}).get("source") if retained else None,
                        "retainedOriginal": retained.get("original") if retained else None,
                        "retainedManifest": retained.get("manifest") if retained else None,
                    })
                    continue
                rows.append({
                    "source": path.relative_to(root).as_posix(),
                    "sourceHash": digest,
                    "originalName": path.name,
                    "standardName": standard_name,
                    "owner": owner,
                    "group": group,
                    "folderName": name,
                    "bucket": bucket,
                    "photoId": photo_id,
                    "idBasis": id_basis,
                    "retainedSourceHash": retained.get("sourceSha256") if retained else None,
                    "retainedCurrentHash": retained.get("currentSha256") if retained else None,
                    "retainedSource": retained.get("row", {}).get("source") if retained else None,
                    "retainedOriginal": retained.get("original") if retained else None,
                    "retainedManifest": retained.get("manifest") if retained else None,
                    "retainedSelected": retained.get("selected") if retained else None,
                    "sourceStatus": "unclassified",
                })
    return rows, folders, prefixes


def _decision_ids(cfg, metadata_module):
    names = list(cfg.get("photos", {}).values())
    for flow in cfg.get("flows", {}).values():
        names.extend(flow.get("photos", {}).values())
    return {
        photo_id for name in names if isinstance(name, str)
        if (photo_id := metadata_module.photo_id_from_name(name))
    }


def _resolve_collision(root, entries, record, anchor_owners, chosen, workflow_selected, protected_folders):
    from tools.art import duplicates

    def pick(rows):
        ranked = duplicates.keeper([
            (root / row["source"], row["group"], root / row["owner"], row["bucket"])
            for row in rows
        ], chosen)
        return next(row for row in rows if root / row["source"] == ranked[0])

    def hold(reason):
        for row in entries:
            row.update(sourceStatus="held", versionConflict=True, reason=reason)
        return None

    selected = [row for row in entries if pathlib.Path(row["originalName"]).stem.casefold() in chosen]
    bound = [row for row in entries if row["sourceHash"] == record.get("contentSha256")]
    protected = [row for row in entries if row["bucket"] == "gallery" and row["owner"] in protected_folders]
    if not protected and (len(selected) > 1 or len(anchor_owners) > 1):
        return hold("conflicting selected references or anchors")
    required = protected or list(entries)
    if anchor_owners:
        anchored = [row for row in required if row["owner"] in anchor_owners and row["bucket"] == "gallery"]
        required = anchored or (required if protected else [])
    if selected:
        selected_required = [row for row in required if row in selected]
        required = selected_required or (required if protected else [])
    elif workflow_selected and not protected:
        return hold("workflow-selected copy could not be resolved by its filename")
    if record.get("protected"):
        bound_required = [row for row in required if row in bound]
        required = bound_required or (required if protected else [])
        if not protected and len({row["owner"] for row in required}) > 1:
            return hold("catalogue-bound ownership is ambiguous")
    if not required:
        return hold("selected reference or confirmed ownership conflicts with the available copies")

    prepared = [row for row in entries if row.get("retainedManifest")]
    raw_aliases = {
        row["source"]: natives for row in entries if not row.get("retainedManifest")
        and (natives := [
            native for native in prepared if native.get("retainedSourceHash") == row["sourceHash"]
            and native["sourceHash"] != row["sourceHash"]
        ])
    }
    versions = [row for row in entries if row["source"] not in raw_aliases]
    if not protected and any(len({native["sourceHash"] for native in natives}) > 1 for natives in raw_aliases.values()):
        return hold("retained original identifies more than one prepared version")
    for row in entries:
        row["collisionModifiedNs"] = (root / row["source"]).stat().st_mtime_ns
    hashes = {row["sourceHash"] for row in versions}
    rule = "exact-byte keeper"
    if protected:
        eligible = [row for row in required if row in versions] or required
        preferred = [row for row in eligible if row in bound] or eligible
        keeper = pick([row for row in preferred if row.get("retainedManifest")] or preferred)
        rule = "protected Gallery keeper; conflicting copies archived without changing keeper's owner"
    elif len(hashes) > 1 and len({row["sourceHash"] for row in required}) == 1 and (
        anchor_owners or selected or record.get("protected")
    ):
        hashes = {required[0]["sourceHash"]}
        rule = "kept the uniquely selected, anchored, or protected version"
    elif len(hashes) > 1:
        if all(row["idBasis"] == "raw-content-sha1-8" for row in versions):
            return hold("short content-derived ID collision across different full SHA-256 values")
        recent = max(row["collisionModifiedNs"] for row in versions)
        newest = [row for row in versions if row["collisionModifiedNs"] == recent]
        hashes = {row["sourceHash"] for row in newest}
        if len(hashes) > 1:
            eligible_ties = [row for row in newest if row in required]
            bound_ties = [row for row in eligible_ties if row in bound]
            if eligible_ties:
                hashes = {pick(bound_ties or eligible_ties)["sourceHash"]}
            rule = "newest modification time tied; kept catalogue-bound or stable keeper preference"
        else:
            rule = "unique newest version by filesystem modification time"
    elif raw_aliases:
        rule = "verified prepared native instead of its retained raw original"
    if not protected:
        eligible = [row for row in required if row in versions and row["sourceHash"] in hashes]
        if not eligible:
            return hold("newest or prepared version conflicts with the selected or anchored copy")
        keeper = pick([row for row in eligible if row.get("retainedManifest")] or eligible)
    keeper.update(sourceStatus="canonical", collisionRule=rule)
    for row in entries:
        if row is keeper:
            continue
        reason = (
            "exact-byte copy" if row["sourceHash"] == keeper["sourceHash"] else
            "verified retained raw original" if row["source"] in raw_aliases else
            "non-keeper same-ID version"
        )
        row.update(sourceStatus="duplicate-archive", selectedSource=keeper["source"], reason=reason)
    return keeper


def _disposition_destination(root, prefix, run_id, source):
    token = hashlib.sha256(source.casefold().encode("utf-8")).hexdigest()[:24]
    destination = pathlib.PurePosixPath(prefix, run_id, token, source).as_posix()
    if normal_transaction.safe(root, destination).exists():
        raise ValueError(f"disposition destination already exists: {destination}")
    return destination


def _duplicate_archives(root, rows, run_id):
    archives = {}
    for row in rows:
        if row.get("sourceStatus") != "duplicate-archive":
            continue
        destination = _disposition_destination(root, "_duplicates", run_id, row["source"])
        archives[row["source"]] = {
            "source": row["source"], "destination": destination, "photoId": row["photoId"],
            "sha256": row["sourceHash"], "reason": row["reason"], "selectedSource": row["selectedSource"],
            **({"selectedPhotoId": row["contentVoteCanonicalId"]} if row.get("crossIdExactArchive") else {}),
            **({"retainedOriginalProof": row["retainedOriginalProof"]} if row.get("retainedOriginalProof") else {}),
        }
    if len({row["destination"].casefold() for row in archives.values()}) != len(archives):
        raise ValueError("duplicate archive destinations collide")
    return archives


def _retained_duplicate_sources(root, archives):
    from tools.art.likeness_library import retained_preparation

    checksums = {}
    verified = {}
    for row in archives.values():
        proof = row.get("retainedOriginalProof")
        if not proof:
            continue
        keeper, photo_id = row["selectedSource"], row["selectedPhotoId"]
        key = (keeper, photo_id)
        if key not in verified:
            verified[key] = retained_preparation.verify_link(root, keeper, photo_id)
        link = verified[key]
        if not link or (
            link["original"], link["manifest"], link["currentSha256"], link["sourceSha256"]
        ) != (proof["path"], proof["manifest"], proof["keeperNativeSha256"], row["sha256"]):
            raise ValueError(f"duplicate keeper's retained original changed before publication: {keeper}")
        checksums[proof["path"]] = row["sha256"]
        checksums[proof["manifest"]] = verification_reads.sha256(normal_transaction.safe(root, proof["manifest"]))
    return checksums


def _no_face_dispositions(root, active, raw_data, catalog, workflow_ids, prefix):
    guarded_ids = set(workflow_ids) | {
        photo_id for person in catalog.get("people", {}).values()
        for photo_id in person.get("identityAnchors", ())
    } | {
        photo_id for action in catalog.get("actions", ())
        if action.get("actor") == "user"
        for photo_id in action.get("photoIds", ())
    }
    results = {}
    for row in active:
        record = catalog.get("photos", {}).get(row["photoId"], {})
        if (
            row["group"] != "Various" or row["sourceStatus"] != "eligible"
            or row["photoId"] in guarded_ids or row.get("collisionRule") or row.get("retainedContentKeeper")
            or bool(set(record) - {"contentSha256", "protected"})
            or record.get("protected") or record.get("contentSha256", row["sourceHash"]) != row["sourceHash"]
        ):
            continue
        _digest, measurement = raw_data[row["source"]]
        if (
            type(measurement.get("faces")) is not int or measurement["faces"] != 0
            or not normal_import._current_measurement(measurement) or measurement.get("v")
        ):
            continue
        source = row["source"]
        destination = pathlib.PurePosixPath(prefix, source).as_posix()
        if normal_transaction.safe(root, destination).exists():
            raise ValueError(f"junk disposition destination already exists: {destination}")
        reason = "selected native decoded and measured with zero detected faces; recoverable junk"
        results[source] = {
            "photoId": row["photoId"], "source": source, "sha256": row["sourceHash"],
            "destination": destination,
            "faces": 0, "reason": reason,
        }
        row.update(sourceStatus="confirmed-no-face-junk", rebaseRole="recoverable-junk", reason=reason)
    return results


def _unresolved_duplicate_ids(rows, archives):
    remaining = collections.Counter(
        row["photoId"] for row in rows
        if row.get("photoId") and row["group"] in IDENTITY_ROOTS | {"Various"}
        and row["source"] not in archives
    )
    return sorted(pid for pid, count in remaining.items() if count > 1)


def _require_resolved_duplicate_ids(ids):
    if ids:
        raise ValueError(f"{len(ids)} unresolved same-ID collision(s) block apply; see ID collisions in recap")


def _archive_retained_original_copies(rows, active, guarded_ids, chosen):
    """Use verified inventory lineage, never a basename or a historical ID alone."""
    by_native, by_original = collections.defaultdict(list), collections.defaultdict(list)
    for row in rows:
        if row["group"] not in IDENTITY_ROOTS | {"Various"}:
            continue
        by_native[row["sourceHash"]].append(row)
        if row.get("retainedManifest") and row.get("retainedOriginal"):
            by_original[row["retainedSourceHash"]].append(row)
    active_sources = {row["source"] for row in active}
    for digest, keepers in by_original.items():
        if len(keepers) != 1 or not by_native.get(digest):
            continue
        keeper = keepers[0]
        native_hash = keeper["sourceHash"]
        copies = by_native[digest]
        if (
            keeper["source"] not in active_sources or keeper["sourceStatus"] != "eligible"
            or native_hash == digest or native_hash != keeper["retainedCurrentHash"]
            or any(row["photoId"] != keeper["photoId"] for row in by_native[native_hash])
            or any(row["group"] in IDENTITY_ROOTS or row.get("retainedManifest") for row in copies)
        ):
            continue
        for row in copies:
            if (
                row["source"] not in active_sources or row["bucket"] != "gallery"
                or row["sourceStatus"] != "eligible" or row.get("collisionRule")
                or row["photoId"] == keeper["photoId"] or row["photoId"] in guarded_ids
                or pathlib.Path(row["originalName"]).stem.casefold() in chosen
            ):
                continue
            keeper["retainedContentKeeper"] = True
            row.update(
                sourceStatus="duplicate-archive", crossIdExactArchive=True,
                selectedSource=keeper["source"], contentVoteCanonicalSource=keeper["source"],
                contentVoteCanonicalId=keeper["photoId"], contentVoteStatus="nonvoting-duplicate-content",
                reason="identical bytes to the verified retained original under a different stable ID",
                retainedOriginalProof={
                    "path": keeper["retainedOriginal"], "manifest": keeper["retainedManifest"],
                    "keeperNativeSha256": native_hash,
                },
            )
    active[:] = [row for row in active if row["sourceStatus"] != "duplicate-archive"]


def _classify_sources(root, rows, cfg, catalog, api, *, archive_collisions=False):
    """Choose one physical input per ID; preserve every alias/version in evidence."""
    from tools.art import duplicates

    chosen = duplicates.chosen_stems(cfg)
    workflow_ids = _decision_ids(cfg, metadata)
    anchors = collections.defaultdict(set)
    for person_id, person in catalog.get("people", {}).items():
        for photo_id in person.get("identityAnchors", ()):
            anchors[photo_id].add(person.get("folder") or person_id)

    by_id = collections.defaultdict(list)
    for row in rows:
        if row.get("photoId"):
            by_id[row["photoId"]].append(row)
    protected_folders = {
        row["owner"] for row in rows if row["group"] in ("Sisters", "Angels")
    } | {person["folder"] for person in catalog["people"].values() if person.get("protected")}
    active, held, updates, aliases = [], [
        row for row in rows
        if row.get("sourceStatus") == "held" and not row.get("photoId")
    ], {}, []

    def canonical_exact(photo_id, same_bytes):
        keeper_rows = [
            (root / pathlib.PurePosixPath(row["source"]), row["group"],
             root / pathlib.PurePosixPath(row["owner"]), row["bucket"])
            for row in same_bytes
        ]
        selected = [
            row for row in same_bytes
            if pathlib.Path(row["originalName"]).stem.casefold() in chosen
        ]
        owner_folders = {row["owner"] for row in same_bytes}
        anchor_owners = anchors.get(photo_id, set())
        record = catalog.get("photos", {}).get(photo_id, {})
        selected_owners = {row["owner"] for row in selected}
        if (
            len(selected) > 1
            or len(anchor_owners) > 1
            or (anchor_owners and not anchor_owners.issubset(owner_folders))
            or (anchor_owners and selected_owners and selected_owners != anchor_owners)
            or (record.get("protected") and len(owner_folders) > 1 and not anchor_owners)
        ):
            for row in same_bytes:
                row.update({
                    "sourceStatus": "held",
                    "reason": "conflicting chosen-photo, lock, or anchor ownership decisions block exact-alias canonicalization",
                })
                held.append(row)
            return None
        if anchor_owners:
            keeper_rows = [
                entry for entry in keeper_rows
                if entry[2].relative_to(root).as_posix() in anchor_owners
            ]
        kept_entry = duplicates.keeper(keeper_rows, chosen)
        keeper_path = kept_entry[0].relative_to(root).as_posix()
        keeper = next(row for row in same_bytes if row["source"] == keeper_path)
        keeper["sourceStatus"] = "canonical"
        for row in same_bytes:
            if row is keeper:
                continue
            row.update({
                "sourceStatus": "exact-byte-alias",
                "canonicalSource": keeper["source"],
                "reason": "same stable photo ID and exact SHA-256; one canonical representation votes",
                "keeperRule": "tools.art.duplicates.keeper",
            })
            aliases.append(row)
        return keeper

    for photo_id, entries in sorted(by_id.items()):
        entries = [
            row for row in entries
            if row.get("sourceStatus") != "excluded-separate-domain"
        ]
        if not entries:
            continue
        if any(row.get("sourceStatus") == "held" for row in entries):
            for row in entries:
                row["sourceStatus"] = "held"
                if archive_collisions and len(entries) > 1:
                    row["versionConflict"] = True
                row.setdefault(
                    "reason",
                    "another same-ID source has invalid retained lineage or no safe ID filename",
                )
                held.append(row)
            continue
        record = catalog.get("photos", {}).get(photo_id, {})
        if archive_collisions and len(entries) > 1:
            keeper = _resolve_collision(
                root, entries, record, anchors.get(photo_id, set()), chosen,
                photo_id in workflow_ids, protected_folders,
            )
            if keeper:
                active.append(keeper)
            else:
                held.extend(entries)
            continue
        retained_current = [
            row for row in entries
            if row["group"] in IDENTITY_ROOTS and row["bucket"] == "gallery"
            and row.get("retainedManifest")
            and row["sourceHash"] == record.get("contentSha256")
            and anchors.get(photo_id, set()).issubset({row["owner"]})
        ]
        if len(retained_current) == 1:
            current = retained_current[0]
            original_aliases = [
                row for row in entries
                if row["group"] == "Various" and row["bucket"] == "gallery"
                and not row.get("retainedManifest")
                and row["sourceHash"] == current.get("retainedSourceHash")
                and row["sourceHash"] != current["sourceHash"]
            ]
            for row in original_aliases:
                row.update({
                    "sourceStatus": "preserved-version",
                    "selectedSource": current["source"],
                    "versionOf": photo_id,
                    "retainedOriginalAlias": True,
                    "reason": "exact retained original of the catalogue-bound prepared native; preserve without replacement or another vote",
                })
                held.append(row)
            entries = [row for row in entries if row not in original_aliases]
        by_hash = collections.defaultdict(list)
        for row in entries:
            by_hash[row["sourceHash"]].append(row)
        canonical_versions = []
        alias_decision_conflict = False
        for same_bytes in by_hash.values():
            if len(same_bytes) == 1:
                canonical_versions.append(same_bytes[0])
                continue
            canonical = canonical_exact(photo_id, same_bytes)
            if canonical:
                canonical_versions.append(canonical)
            else:
                alias_decision_conflict = True
        if not canonical_versions:
            continue
        if alias_decision_conflict:
            for row in canonical_versions:
                row.update({
                    "sourceStatus": "held",
                    "reason": "an exact-byte alias group has conflicting chosen-photo, lock, or anchor ownership",
                    "versionConflict": True,
                })
                held.append(row)
            continue
        if len(by_hash) == 1:
            row = canonical_versions[0]
            if row["sourceStatus"] == "unclassified":
                row["sourceStatus"] = "eligible"
            active.append(row)
            continue

        incoming_entries = [
            (root / pathlib.PurePosixPath(row["source"]), row["group"],
             root / pathlib.PurePosixPath(row["owner"]), row["bucket"])
            for row in canonical_versions
        ]
        selection = duplicates.select_incoming_version(incoming_entries)
        incoming_rows = [row for row in canonical_versions if row["group"] == "Various" and row["bucket"] == "gallery"]
        current_rows = [row for row in canonical_versions if row not in incoming_rows]
        current_gallery = [row for row in current_rows if row["bucket"] == "gallery" and row["group"] in IDENTITY_ROOTS]
        owner_folders = {row["owner"] for row in current_gallery}
        anchor_owners = anchors.get(photo_id, set())
        record = catalog.get("photos", {}).get(photo_id, {})
        lock_conflict = (
            photo_id in workflow_ids or bool(record.get("protected"))
            or len(anchor_owners) > 1
            or (anchor_owners and owner_folders and not anchor_owners.issubset(owner_folders))
        )
        current_is_bound = (
            len(current_gallery) == 1
            and len(owner_folders) == 1
            and record.get("contentSha256") == current_gallery[0]["sourceHash"]
        )
        generated_id_collision = all(
            row.get("idBasis") == "raw-content-sha1-8" for row in canonical_versions
        )
        if (
            selection["status"] == "selected-incoming"
            and not current_rows
            and not lock_conflict
            and not anchor_owners
            and not generated_id_collision
        ):
            selected_path = selection["selected"][0].relative_to(root).as_posix()
            selected_row = next(row for row in incoming_rows if row["source"] == selected_path)
            selected_row.update({
                "sourceStatus": "eligible-incoming",
                "versionRule": "unique newest Various/gallery input per tools.art.duplicates.select_incoming_version",
            })
            active.append(selected_row)
            for row in canonical_versions:
                if row is selected_row:
                    continue
                row.update({
                    "sourceStatus": "preserved-version",
                    "selectedSource": selected_row["source"],
                    "reason": "non-selected same-ID incoming version is preserved and does not vote",
                    "versionOf": photo_id,
                })
                held.append(row)
            continue
        if (
            selection["status"] == "selected-incoming"
            and len(current_gallery) == 1
            and current_is_bound
            and not lock_conflict
            and not (anchor_owners and anchor_owners != owner_folders)
        ):
            selected_entry = selection["selected"]
            selected_path = selected_entry[0].relative_to(root).as_posix()
            selected_row = next(row for row in incoming_rows if row["source"] == selected_path)
            selected_row.update({
                "sourceStatus": "incoming-update",
                "updateOwner": current_gallery[0]["owner"],
                "previousSource": current_gallery[0]["source"],
                "previousHash": current_gallery[0]["sourceHash"],
                "versionRule": "unique newest Various/gallery input per tools.art.duplicates.select_incoming_version",
            })
            updates[photo_id] = selected_row
            active.append(selected_row)
            for row in canonical_versions:
                if row is selected_row:
                    continue
                row.update({
                    "sourceStatus": "preserved-version",
                    "selectedSource": selected_row["source"],
                    "reason": "non-selected same-ID version is preserved and does not vote",
                    "versionOf": photo_id,
                })
                held.append(row)
            continue

        if selection["status"] == "ambiguous-incoming-time-tie":
            reason = "multiple incoming originals tie for newest; no version selected"
        elif lock_conflict:
            reason = "a true lock, workflow selection, or conflicting anchor blocks same-ID replacement"
        elif not current_is_bound:
            reason = "same-ID versions lack one unambiguous current Gallery owner bound by the catalogue"
        else:
            reason = "same-ID versions do not satisfy the accepted incoming-version selection"
        if generated_id_collision:
            reason = "short content-derived ID collision across different full SHA-256 values"
        for row in canonical_versions:
            row.update({
                "sourceStatus": "held",
                "reason": reason,
                "versionConflict": True,
            })
            held.append(row)

    user_ids = {
        photo_id for action in catalog.get("actions", ())
        if action.get("actor") == "user" for photo_id in action.get("photoIds", ())
    }
    if archive_collisions:
        _archive_retained_original_copies(
            rows, active, user_ids | workflow_ids | set(anchors) | set(catalog.get("photos", {})), chosen,
        )

    by_digest = collections.defaultdict(list)
    for row in active:
        by_digest[row["sourceHash"]].append(row)
    for digest, same_content in by_digest.items():
        if len({row["photoId"] for row in same_content}) <= 1:
            continue
        named_owners = {
            row["owner"] for row in same_content
            if row["group"] in IDENTITY_ROOTS
        }
        selected_rows = [
            row for row in same_content
            if pathlib.Path(row["originalName"]).stem.casefold() in chosen
        ]
        workflow_rows = [row for row in same_content if row["photoId"] in workflow_ids]
        protected_rows = [
            row for row in same_content
            if catalog.get("photos", {}).get(row["photoId"], {}).get("protected")
        ]
        anchor_owners = set().union(*(
            anchors.get(row["photoId"], set()) for row in same_content
        ))
        conflict = (
            len(named_owners) > 1
            or len(selected_rows) > 1
            or len(workflow_rows) > 1
            or len(protected_rows) > 1
            or len(anchor_owners) > 1
            or (anchor_owners and (not named_owners or not anchor_owners.issubset(named_owners)))
            or (
                anchor_owners
                and any(row["owner"] not in anchor_owners for row in (
                    *selected_rows, *workflow_rows, *protected_rows,
                ))
            )
        )
        forced = [*selected_rows, *workflow_rows, *protected_rows]
        if forced and any(row is not forced[0] for row in forced[1:]):
            conflict = True
        if conflict:
            reason = (
                "identical bytes under different stable IDs have conflicting named-owner, chosen-photo, "
                "workflow, lock, or anchor decisions; preserve all IDs and hold from voting"
            )
            for row in same_content:
                row.update({"sourceStatus": "held", "reason": reason, "versionConflict": True})
                held.append(row)
                active.remove(row)
                updates.pop(row["photoId"], None)
            canonical_paths = {row["source"] for row in same_content}
            for row in aliases:
                if row.get("canonicalSource") in canonical_paths:
                    row.update({
                        "nonVoting": True,
                        "contentVoteStatus": "held-with-conflicting-cross-ID-owner",
                    })
            continue

        eligible = list(same_content)
        if selected_rows:
            eligible = [row for row in eligible if row is selected_rows[0]]
        if workflow_rows:
            eligible = [row for row in eligible if row is workflow_rows[0]]
        if protected_rows:
            eligible = [row for row in eligible if row is protected_rows[0]]
        if anchor_owners:
            eligible = [row for row in eligible if row["owner"] in anchor_owners]
        if not eligible:
            raise ValueError(f"no safe keeper for identical content hash {digest}")
        keeper_entries = [
            (
                root / pathlib.PurePosixPath(row["source"]), row["group"],
                root / pathlib.PurePosixPath(row["owner"]), row["bucket"],
            )
            for row in eligible
        ]
        kept_entry = duplicates.keeper(keeper_entries, chosen)
        kept_path = kept_entry[0].relative_to(root).as_posix()
        keeper_row = next(row for row in eligible if row["source"] == kept_path)
        for row in same_content:
            if row is keeper_row:
                row["contentVoteCanonical"] = True
                continue
            # Every byte-identical copy under another ID is archived recoverably;
            # the keeper alone is placed by matching. Only an identity anchor on
            # the copy, a same-ID collision decision, a forced keeper binding or
            # removal of the only copy from a protected Gallery keeps it held.
            protected_copy = (
                row["group"] in IDENTITY_ROOTS and row["bucket"] == "gallery"
                and row["owner"] in protected_folders and keeper_row["owner"] != row["owner"]
            )
            archive_copy = (
                archive_collisions
                and not row.get("collisionRule") and row["photoId"] not in anchors
                and not any(row is bound for bound in forced)
                and not protected_copy
            )
            row.update({
                "sourceStatus": "duplicate-archive" if archive_copy else "same-content-nonvoting",
                "reason": (
                    "identical bytes under a different stable ID; recoverable duplicate archive, IDs not merged; "
                    "the keeper selected by tools.art.duplicates.keeper is placed by matching"
                    if archive_copy else
                    "identical bytes under a different stable ID; preserved without ID/owner merge, "
                    "and excluded from independent voting by tools.art.duplicates.keeper"
                ),
                "contentVoteCanonicalSource": keeper_row["source"],
                "contentVoteCanonicalId": keeper_row["photoId"],
                "contentVoteStatus": "nonvoting-duplicate-content",
            })
            if archive_copy:
                row.update(selectedSource=keeper_row["source"], crossIdExactArchive=True)
            else:
                held.append(row)
            active.remove(row)
            updates.pop(row["photoId"], None)
            for alias in aliases:
                if alias.get("canonicalSource") == row["source"]:
                    alias.update({
                        "nonVoting": True,
                        "contentVoteCanonicalSource": keeper_row["source"],
                        "contentVoteCanonicalId": keeper_row["photoId"],
                    })

    active_ids = [row["photoId"] for row in active]
    duplicates_active = sorted(pid for pid, count in collections.Counter(active_ids).items() if count > 1)
    if duplicates_active:
        raise ValueError("source normalization produced more than one eligible input per ID: " + ", ".join(duplicates_active))
    return active, held, aliases, updates, workflow_ids


def _bindings(api, cfg, policy):
    from tools.art import duplicates
    from tools.art.likeness_library import clean_preparation
    from tools.art import library_backup
    from tools.workflows import comfy_workflows as cw

    bindings = normal_import._bindings(api, cfg, policy)
    bindings["normalRebase.py"] = metadata.content_sha256(pathlib.Path(__file__))
    bindings["normalImport.py"] = metadata.content_sha256(pathlib.Path(normal_import.__file__))
    bindings["duplicates.py"] = metadata.content_sha256(pathlib.Path(duplicates.__file__))
    bindings["sandbox.py"] = metadata.content_sha256(pathlib.Path(sandbox.__file__))
    bindings["clean_preparation.py"] = metadata.content_sha256(pathlib.Path(clean_preparation.__file__))
    bindings["library_backup.py"] = metadata.content_sha256(pathlib.Path(library_backup.__file__))
    bindings["art:likeness.py"] = metadata.content_sha256(pathlib.Path(api.__file__))
    bindings["workflows:comfy_workflows.py"] = metadata.content_sha256(pathlib.Path(cw.__file__))
    return bindings


def _infer(api, cache, embedder, path, *, persist_evidence=False):
    digest = normal_import._refresh_content_digest(cache, path)
    data = cache.emb.get(digest)
    if normal_import._current_measurement(data):
        return digest, data
    if embedder.det is None:
        # Load the pinned local models before enabling apply-time evidence writes.
        # Engine loading in read-only mode fails closed when either model is absent.
        token = api.domains.READ_ONLY.set(True)
        try:
            embedder.load()
        finally:
            api.domains.READ_ONLY.reset(token)
    token = api.domains.READ_ONLY.set(not persist_evidence)
    try:
        data = embedder(path)
    finally:
        api.domains.READ_ONLY.reset(token)
    if not data or not data.get("v"):
        data = data or {"faces": -1}
    cache.emb[digest] = data
    return digest, data


def _as_photo(api, row, measured_path, data, digest):
    photo = api.Photo(
        pathlib.Path(measured_path),
        row["group"],
        row["folderName"],
        digest,
        data,
    )
    photo.name = row["standardName"]
    return photo


def _explicit_review_placements(catalog, *, action_types=("sent-to-review", "match-accepted")):
    actions = catalog.get("actions", ())
    undone = {action["undoes"] for action in actions if action.get("type") == "action-undone" and "undoes" in action}
    return {
        (photo_id, action.get("destination"))
        for action in actions
        if action.get("type") in action_types
        and action.get("actor") == "user" and action.get("id") not in undone
        for photo_id in action.get("photoIds", ())
    }


def _pre_settle_bindings(plan):
    """The fresh selection bound by a preview, without the members its settle passes released."""
    settled = {row["photoId"] for row in plan.get("settleReleasedBindings") or []}
    selected = [row for row in plan.get("releasedPhotoBindings") or [] if row["photoId"] not in settled]
    return selected or None


def _settle_plan(api, report, *, rows, candidates, raw_photos, release_ids, folders, cores, catalog,
                 rejection_catalog, settings, policy, names_taken, locked, max_passes, fresh_assessment,
                 candidate_quality=None, locked_ids=(), workflow_ids=(), protected_folders=()):
    """Run bounded settle passes over the planned decisions.

    Returns ``(evidence, timings, bindings, settle_candidates)``. Every measured
    planned photo becomes a settle entry. Photos this run placed are
    releasable unless their candidate evidence carries a protection, explicit
    Review placement or stale rejection (the bound release cohort's source
    protections were already overridden). Original named-Gallery members
    planned at their source location are releasable only in the Sandbox
    fresh source release, whose user-authorized release already covers every
    bindable named-Gallery member: a released original that leaves its
    source becomes an additional release binding (source path and SHA-256)
    so membership/anchor retirement and the release permission override
    cover it. Cast top-N seeds stay exempt. In any other rebase originals are
    scored and reported, never released.
    """
    candidate_by_id = {row["photoId"]: row for row in candidates}
    rows_by_id = {row["photoId"]: row for row in rows}
    assessed = {row["photoId"]: row for row in (fresh_assessment or {}).get("assessment", [])}
    seeds = {
        photo_id: owner
        for owner, info in ((fresh_assessment or {}).get("castSeed") or {}).get("identities", {}).items()
        for photo_id in info["seedPhotoIds"]
    }
    people = collections.defaultdict(list)
    for person_id, person in catalog.get("people", {}).items():
        people[person["folder"]].append((person_id, person))
    identity_meta = {}
    for group, name, _path in folders:
        if group not in IDENTITY_ROOTS:
            continue
        folder = f"{group}/{name}"
        records = people.get(folder, [])
        person_id, person = records[0] if len(records) == 1 else (None, None)
        identity_meta[folder] = {
            "side": "Prospects", "category": group,
            "personIds": sorted(rejections.identity_ids(catalog, person_id)) if person_id else [],
            "identityProtected": bool(person and person.get("protected")),
        }
        if folder in cores:
            identity_meta[folder].update(
                personIds=list(cores[folder].get("personIds", [])),
                identityProtected=bool(cores[folder].get("identityProtected")),
            )

    def original(row):
        return (row["group"] in IDENTITY_ROOTS and row["bucket"] == "gallery"
                and row["photoId"] not in release_ids)

    def fresh_bindable(row):
        evidence = assessed.get(row["photoId"])
        return bool(
            evidence is not None and not evidence["bindingBlocked"]
            and evidence["currentPath"] == row["source"] and evidence["sha256"] == row["sourceHash"]
            and row["sourceStatus"] in ("eligible", "same-content-nonvoting")
        )

    entries = []
    for row in sorted(rows, key=lambda item: item["photoId"]):
        photo = raw_photos.get(row["source"])
        if photo is None:
            continue
        photo_id = row["photoId"]
        candidate = candidate_by_id.get(photo_id)
        single = bool(
            photo.usable(settings["minFace"]) and photo.faces == 1
            and getattr(photo, "f2", 0.) <= settings["multiFace"]
        )
        vector = None
        if photo.vec is not None:
            vector = np.asarray(photo.vec, dtype=float)
            vector = nz(vector) if vector.ndim == 1 and np.isfinite(vector).all() and np.linalg.norm(vector) else None
        stay = None
        if original(row):
            if fresh_assessment is None:
                stay = "existing member outside a release cohort; settle releases only photos this run placed"
            elif not fresh_bindable(row):
                stay = "existing member cannot be bound for release (ambiguous, stale or unbindable source)"
        exempt = None
        if candidate is not None and photo_id not in release_ids and not (
            fresh_assessment is not None and original(row) and stay is None
        ):
            exempt = (
                "stale rejected-identity metadata" if candidate.get("rejectionMetadataStale") else
                "explicit Review placement" if candidate.get("explicitReviewPlacement") else
                "protected photo" if candidate.get("protected") else
                "workflow-selected photo" if candidate.get("workflowSelected") else
                "member of a protected identity" if candidate.get("identityProtected") else None
            )
        state = (
            {key: candidate[key] for key in ("rejectedPersonIds", "rejectionMetadataStale") if key in candidate}
            if candidate is not None else rejections.photo_state(rejection_catalog, photo)
        )
        entries.append({
            "photoId": photo_id, "sha256": row["sourceHash"], "vector": vector,
            "sourceFolder": row["owner"], "sourceLocation": (row["owner"], row["bucket"]),
            "voter": row["sourceStatus"] == "eligible" and (
                face_quality.reference_quality(candidate) if candidate is not None else single
            ),
            "scorable": bool(candidate.get("qualityEligible")) if candidate is not None else single,
            "exemptReason": exempt, "stayExemptReason": stay,
            "seedOf": seeds.get(photo_id), "candidateState": state, "candidate": candidate,
        })
    settle_candidates = {}

    def candidate_for(entry):
        """Candidate evidence for an original fresh member that has no planned decision yet."""
        row = rows_by_id[entry["photoId"]]
        photo = raw_photos[row["source"]]
        record = catalog.get("photos", {}).get(row["photoId"], {})
        candidate = {
            "photoId": row["photoId"], "sourceFolder": row["owner"], "sourceBucket": "Pool",
            "side": "Prospects", "vector": photo.vec, "sha256": row["sourceHash"],
            "protected": bool(row["photoId"] in locked_ids or record.get("protected")),
            "workflowSelected": row["photoId"] in workflow_ids,
            "identityProtected": row["owner"] in protected_folders,
            "explicitReviewPlacement": False, "priorExplicitReviewPlacement": False,
            "rebaseCandidate": True, "regroupReview": True, "detachedOutlier": False,
            **(face_quality.candidate_fields(candidate_quality(photo, row["source"]))
               if candidate_quality is not None else {"qualityEligible": True}),
            **rejections.photo_state(rejection_catalog, photo),
            **({"releaseStandardName": row["standardName"]} if row.get("standardName") else {}),
        }
        settle_candidates[row["photoId"]] = candidate
        return candidate

    unkeyed = [row for row in report["held"] if not row.get("photoId")]
    decisions = {row["photoId"]: row for row in report["assignments"] + report["held"] if row.get("photoId")}
    before = {
        entry["photoId"]: normal_admission.settle_location(entry, decisions.get(entry["photoId"]))
        for entry in entries
    }
    evidence, timings = normal_admission.settle_passes(
        api, entries, decisions, report["clusters"], identity_meta, settings, policy, names_taken,
        locked=locked, max_passes=max_passes,
        candidate_for=candidate_for if fresh_assessment is not None else None,
    )
    bindings = []
    for entry in entries:
        row = rows_by_id[entry["photoId"]]
        after = normal_admission.settle_location(entry, decisions.get(entry["photoId"]))
        if not original(row) or before[entry["photoId"]] != entry["sourceLocation"] or after == before[entry["photoId"]]:
            continue
        # An original member that settle moved off its source location.
        if fresh_assessment is None or entry["stayExemptReason"]:
            raise ValueError(f'{entry["photoId"]}: settle cannot release an original member outside a fresh release')
        bindings.append({"photoId": row["photoId"], "currentPath": row["source"], "sha256": row["sourceHash"]})
    report["assignments"] = sorted(
        (row for row in decisions.values() if row.get("destination")), key=lambda row: row["photoId"],
    )
    report["held"] = sorted(
        (row for row in decisions.values() if not row.get("destination")), key=lambda row: row["photoId"],
    ) + unkeyed
    report["assignedCount"] = len(report["assignments"])
    return evidence, timings, sorted(bindings, key=lambda row: row["photoId"]), settle_candidates

def _plan(
    root, profile, run_id, *, api, cache_path=None, policy_path=None,
    for_apply=False, reuse_plan=None, reuse_preparation=None,
    reuse_preparation_sha256=None, lock_cast_admission=False, preparation_workers=1,
    released_bindings=None, reconsider_holds=False, fresh_source_release=False,
):
    from tools.workflows import comfy_workflows as cw

    root = pathlib.Path(root).resolve()
    cfg = api.configuration()
    policy = load_policy(policy_path)
    if type(fresh_source_release) is not bool:
        raise ValueError("fresh source release must be explicit")
    if fresh_source_release:
        if not is_sandbox_working_path(root):
            raise ValueError("fresh source release requires Sandbox Working")
        if released_bindings is not None:
            raise ValueError("fresh source release cannot replay release lineage")
        if "castAdmission" not in policy:
            raise ValueError("fresh source release requires normal two-round admission")
        if for_apply and reuse_plan is None:
            raise ValueError("fresh source release apply requires its bound preview plan")
        reconsider_holds = True
    if reuse_plan is not None and bool(reuse_plan.get("freshSourceRelease")) != fresh_source_release:
        raise ValueError("fresh source release selection differs from preview")
    if released_bindings is not None:
        if not isinstance(released_bindings, list) or not released_bindings:
            raise ValueError("released cohort requires nonempty verified bindings")
        if any(
            not isinstance(row, dict) or set(row) != {"photoId", "currentPath", "sha256"}
            or not isinstance(row["photoId"], str) or not row["photoId"]
            or not isinstance(row["currentPath"], str) or not row["currentPath"]
            or not isinstance(row["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
            for row in released_bindings
        ):
            raise ValueError("released cohort has malformed verified bindings")
        if "castAdmission" not in policy:
            raise ValueError("released cohort requires normal two-round admission")
        if for_apply and reuse_plan is None:
            raise ValueError("released cohort apply requires its bound preview plan")
        released_bindings = sorted(released_bindings, key=lambda row: row["photoId"])
    if reuse_plan is not None and not fresh_source_release and reuse_plan.get("releasedPhotoBindings") != released_bindings:
        raise ValueError("released cohort bindings differ from preview")
    if reuse_plan is not None and bool(reuse_plan.get("lockCastAdmission")) != lock_cast_admission:
        raise ValueError("cast receiving lock differs from preview")
    if reuse_plan is not None and bool(reuse_plan.get("reconsiderHolds")) != reconsider_holds:
        raise ValueError("existing hold reassessment differs from preview")
    if reconsider_holds and for_apply and reuse_plan is None:
        raise ValueError("existing hold reassessment requires its bound preview plan")
    normal_products.validate_workers(preparation_workers)
    if reuse_plan is not None and reuse_plan.get("preparationWorkersRequested", 1) != preparation_workers:
        raise ValueError("selected preparation worker request differs from preview")
    admission_enabled = "castAdmission" in policy
    settings = effective_settings(cfg, policy)
    settings["poolHome"] = "Various"
    if cache_path is None:
        cache_path = api.cache_path(argparse.Namespace(cache=None), root)
    cache = api.Cache(cache_path)
    embedder = api.Embedder()
    embedder.configure_evidence(
        cw.storage_root(cfg, "likeness", root=root) / "general" / "face-evidence",
        library_root=root,
    )
    redetect = face_quality.redetector(embedder)

    def candidate_quality(photo, source):
        """Bounded framing/re-detection only for multi-face photos; read-only."""
        measured = native_paths.get(source, root / pathlib.PurePosixPath(source))
        return face_quality.assess(
            photo, settings, path=measured, redetect=redetect, framing=face_quality.derivative_framing,
        )
    catalog = metadata.load_catalog(metadata.path_for_root(root))
    phase_started = time.perf_counter()
    with verification_reads.session(root, label="SIMPLE source inventory"):
        rows, folders, prefixes = _hash_sources(root, cfg, api)
    inventory_seconds = time.perf_counter() - phase_started
    phase_started = time.perf_counter()
    if released_bindings is not None:
        for binding in released_bindings:
            by_id = [row for row in rows if row.get("photoId") == binding["photoId"]]
            by_path = [
                row for row in rows
                if row["source"].casefold() == binding["currentPath"].casefold()
            ]
            if (
                len(by_id) != 1 or len(by_path) != 1 or by_id[0] is not by_path[0]
                or (by_id[0]["source"], by_id[0]["sourceHash"])
                != (binding["currentPath"], binding["sha256"])
            ):
                raise ValueError(f"{binding['photoId']}: released binding is stale or ambiguous in frozen inventory")
    if reuse_plan is not None:
        current_hashes = {row["source"]: row["sourceHash"] for row in rows}
        if current_hashes != reuse_plan.get("sourceHashes"):
            raise ValueError("source rows changed since preview; create a new preview")
        if metadata.content_sha256(metadata.path_for_root(root)) != reuse_plan.get("catalogueSHA256"):
            raise ValueError("catalogue changed since preview; create a new preview")
    anchor_photos = []
    for row in rows:
        if (
            row.get("photoId") and row.get("standardName")
            and row.get("group") in IDENTITY_ROOTS
        ):
            photo = api.Photo(
                root / pathlib.PurePosixPath(row["source"]),
                row["group"], row["folderName"], row["sourceHash"],
                {"faces": 0},
            )
            photo.name = row["standardName"]
            anchor_photos.append(photo)
    decision_catalog = metadata.with_configured_anchors(catalog, cfg, anchor_photos)
    active, held, aliases, updates, workflow_ids = _classify_sources(
        root, rows, cfg, decision_catalog, api, archive_collisions=admission_enabled,
    )
    release_roles = {}
    retirement = None
    archived_rows = [row for row in rows if row.get("sourceStatus") == "duplicate-archive"]
    if released_bindings is not None:
        release_roles = _released_candidate_roles(released_bindings, active, held, archived_rows)
        retirement = normal_admission.retire_released_catalog(decision_catalog, released_bindings)
        decision_catalog = retirement["catalog"]
    release_ids = {photo_id for photo_id, role in release_roles.items() if role != "archived-duplicate"}
    released_nonvoting = [row for row in held if release_roles.get(row.get("photoId")) == "nonvoting-candidate"]
    reconsidered_nonvoting = [
        row for row in held
        if reconsider_holds and admission_enabled and row.get("sourceStatus") == "same-content-nonvoting"
        and row not in released_nonvoting and (
            row["group"] == "Various" or row["bucket"] == "review"
            or fresh_source_release and row["group"] in IDENTITY_ROOTS and row["bucket"] == "gallery"
        )
    ]
    nonvoting = released_nonvoting + reconsidered_nonvoting
    for row in released_nonvoting:
        row["rebaseRole"] = "released-nonvoting-candidate"
    for row in reconsidered_nonvoting:
        row["rebaseRole"] = "reconsidered-nonvoting-hold"
    nonvoting_hashes = {row["sourceHash"] for row in released_nonvoting}
    archives = _duplicate_archives(root, rows, run_id) if admission_enabled else {}
    unresolved_ids = _unresolved_duplicate_ids(rows, archives) if admission_enabled else []
    if for_apply:
        _require_resolved_duplicate_ids(unresolved_ids)
    collision_dates = {
        row["source"]: row["collisionModifiedNs"] for row in rows if "collisionModifiedNs" in row
    }
    if reuse_plan is not None and (
        archives != reuse_plan.get("duplicateArchives", {})
        or collision_dates != reuse_plan.get("collisionModifiedNs", {})
    ):
        raise ValueError("duplicate decisions or source modification times changed since preview")
    for row in list(active):
        if not admission_enabled and row.get("retainedManifest") and (
            row["group"] == "Various" or row["bucket"] == "review"
        ):
            row.update({
                "sourceStatus": "held",
                "reason": (
                    "verified retained native is not re-prepared or moved by this stable composition; "
                    "preserve its existing source/preparation lineage for separate review"
                ),
                "rebaseRole": "verified-retained-native-held",
            })
            held.append(row)
            active.remove(row)
            updates.pop(row["photoId"], None)

    run_suffix = f"normal-rebase-{run_id}" if for_apply else f"normal-rebase-{run_id}-preview"
    run = cw.storage_root(cfg, "reports", root=root) / "runs" / run_suffix
    raw_photos, raw_data = {}, {}
    measured_rows = active + nonvoting
    prepare_paths = [
        root / pathlib.PurePosixPath(row["source"])
        for row in measured_rows if not row.get("retainedManifest")
    ]
    prepared = None
    preparation_reuse = None
    preparation_generation = None
    native_paths = {
        row["source"]: root / pathlib.PurePosixPath(row["source"])
        for row in measured_rows if row.get("retainedManifest")
    }
    normalization_seconds = time.perf_counter() - phase_started
    read_token = api.domains.CURRENT.set("general")
    read_only_token = api.domains.READ_ONLY.set(True)
    try:
        phase_started = time.perf_counter()
        if profile in ("full", "lean") and prepare_paths:
            if reuse_plan is not None:
                preparation_root = reuse_plan.get("preparationRoot")
                manifest_hash = reuse_plan.get("preparationManifestSHA256")
                if not preparation_root or not manifest_hash:
                    raise ValueError("preview lacks complete FULL/LEAN preparation evidence")
                prepared = normal_products.reuse_prepared(
                    root, preparation_root, prepare_paths, profile, manifest_hash,
                    allow_subset=bool(reuse_plan.get("preparationReuse")),
                )
                if reuse_plan.get("preparationReuse") or reuse_plan.get("preparationGeneration"):
                    preparation_reuse = _validate_preparation_reuse(
                        root, cfg, profile, prepared, prepare_paths,
                    )
                    if reuse_plan.get("preparationReuse"):
                        if preparation_reuse != reuse_plan["preparationReuse"]:
                            raise ValueError("reused preparation binding changed since preview")
                    if reuse_plan.get("preparationGeneration"):
                        preparation_generation = reuse_plan["preparationGeneration"]
                        if preparation_reuse.get("generationSeal") != preparation_generation:
                            raise ValueError("preparation generation origin seal changed since preview")
            elif reuse_preparation is not None:
                prepared = normal_products.reuse_prepared(
                    root, reuse_preparation, prepare_paths, profile,
                    reuse_preparation_sha256, allow_subset=True,
                )
                preparation_reuse = _validate_preparation_reuse(
                    root, cfg, profile, prepared, prepare_paths,
                )
                preparation_generation = preparation_reuse.get("generationSeal")
            else:
                prepared, preparation_generation = _prepare_with_origin(
                    root, cfg, run, profile, prepare_paths, workers=preparation_workers,
                )
            native_paths.update(prepared[2])
        elif (
            (reuse_plan is not None and reuse_plan.get("preparationRoot"))
            or reuse_preparation is not None
        ):
            raise ValueError("preview preparation scope differs from current selected source set")

        preparation_seconds = time.perf_counter() - phase_started
        phase_started = time.perf_counter()
        # FULL/LEAN measure the selected native output for references and candidates
        # alike. FAST measures unchanged source pixels.
        for row in measured_rows:
            source = root / pathlib.PurePosixPath(row["source"])
            measured_path = native_paths.get(row["source"], source)
            digest, data = _infer(api, cache, embedder, measured_path, persist_evidence=for_apply)
            raw_photos[row["source"]] = _as_photo(api, row, source, data, digest)
            raw_data[row["source"]] = (digest, data)
        junk_prefix = cw.storage_root(cfg, "junk", root=root).relative_to(root).as_posix()
        junk = _no_face_dispositions(
            root, [row for row in active if row["photoId"] not in release_ids],
            raw_data, decision_catalog, workflow_ids, junk_prefix,
        ) if admission_enabled else {}
        if junk:
            active = [row for row in active if row["source"] not in junk]
        if reuse_plan is not None and junk != reuse_plan.get("junkDispositions", {}):
            raise ValueError("confirmed no-face dispositions changed since preview")
        usable_raw = [raw_photos[row["source"]].raw for row in active
                      if raw_photos[row["source"]].usable(settings["minFace"])]
        mean = np.mean(usable_raw, axis=0) if usable_raw else None
        cache.centering_mean = mean.tolist() if mean is not None else None
        cache.centering_domain = "general"
        raw_space = api.Space([raw_photos[row["source"]] for row in active], settings, mean=mean)
        nonvoting_candidates = []
        if nonvoting:
            api.Space([raw_photos[row["source"]] for row in nonvoting], settings, mean=mean)
        fresh_assessment = None
        fresh_measurement_proof = None
        fresh_selection_seconds = 0.
        fresh_measurement_seconds = None
        if fresh_source_release:
            selection_started = time.perf_counter()
            fresh_measurement_seconds = selection_started - phase_started
            fresh_measurement_proof = _fresh_measurement_proof(
                root, measured_rows, raw_data, native_paths, embedder, raw_space.mean,
            )
            if reuse_plan is not None and reuse_plan.get("freshMeasurementProof") != fresh_measurement_proof:
                raise ValueError("fresh source measurement proof differs from preview")
            fresh_assessment = _fresh_gallery_assessment(
                root, rows, active, held, raw_photos, native_paths, decision_catalog, settings, policy,
            )
            if reuse_plan is not None and reuse_plan.get("freshSourceAssessment") != fresh_assessment:
                raise ValueError("fresh source assessment differs from preview")
            selected = sorted(fresh_assessment["bindings"], key=lambda row: row["photoId"])
            released_bindings = selected or None
            if reuse_plan is not None and _pre_settle_bindings(reuse_plan) != released_bindings:
                raise ValueError("fresh source release bindings differ from preview")
            if released_bindings is not None:
                release_roles = _released_candidate_roles(released_bindings, active, held, archived_rows)
                standard_names = {
                    row["photoId"]: row["standardName"] for row in rows
                    if row.get("photoId") in {item["photoId"] for item in released_bindings}
                    and row.get("standardName")
                }
                retirement = normal_admission.retire_released_catalog(
                    decision_catalog, released_bindings, standard_names,
                )
                decision_catalog = retirement["catalog"]
            release_ids = {photo_id for photo_id, role in release_roles.items() if role != "archived-duplicate"}
            released_nonvoting = [
                row for row in held if release_roles.get(row.get("photoId")) == "nonvoting-candidate"
            ]
            reconsidered_nonvoting = [
                row for row in reconsidered_nonvoting if row not in released_nonvoting
            ]
            nonvoting = released_nonvoting + reconsidered_nonvoting
            for row in released_nonvoting:
                row["rebaseRole"] = "released-nonvoting-candidate"
            nonvoting_hashes = {row["sourceHash"] for row in released_nonvoting}
            fresh_selection_seconds = time.perf_counter() - selection_started
        reference_photos = [
            raw_photos[row["source"]]
            for row in active
            if row["group"] in IDENTITY_ROOTS
            and row["bucket"] == "gallery"
            and row["sourceStatus"] != "incoming-update"
            and row["photoId"] not in release_ids
            and row["sourceHash"] not in nonvoting_hashes
        ]
        reference_space = api.Space(reference_photos, settings, mean=mean)
        all_cores, locked_ids, core_diagnostics = reconciliation.frozen_identity_cores(
            reference_space, decision_catalog,
            photo_id_fn=metadata.photo_id_from_name,
            content_sha256_fn=metadata.content_sha256,
            policy=policy,
            require_single_face=admission_enabled,
        )
        cores = {
            folder: value for folder, value in all_cores.items()
            if folder.split("/", 1)[0] in IDENTITY_ROOTS
        }
        fragment_evidence = _fragment_evidence(
            reference_space, cores, decision_catalog, policy, locked_ids | workflow_ids,
        )
        core_ids = {photo_id for core in cores.values() for photo_id in core["corePhotoIds"]}
        for row in list(active):
            if not admission_enabled and row.get("retainedManifest") and row["photoId"] not in core_ids:
                row.update({
                    "sourceStatus": "held",
                    "reason": (
                        "verified retained native is not re-prepared or moved by this stable composition; "
                        "preserve its existing source/preparation lineage for separate review"
                    ),
                    "rebaseRole": "verified-retained-native-held",
                })
                held.append(row)
                active.remove(row)
                updates.pop(row["photoId"], None)
        candidate_paths = []
        audit_only = []
        update_ids = set(updates)
        for row in active:
            photo_id = row["photoId"]
            if release_roles.get(photo_id) == "candidate":
                row["rebaseRole"] = "released-intake-candidate"
                candidate_paths.append(root / pathlib.PurePosixPath(row["source"]))
                continue
            if row["sourceStatus"] == "incoming-update":
                row["rebaseRole"] = "selected-incoming-version-update"
                continue
            if admission_enabled and row["group"] in ("Models", "Prospects", "Potentials") and row["bucket"] == "gallery":
                row["rebaseRole"] = "lower-gallery-upward-candidate"
                candidate_paths.append(root / pathlib.PurePosixPath(row["source"]))
                continue
            if photo_id in core_ids:
                row["rebaseRole"] = "frozen-core-reference"
                continue
            if row["group"] in IDENTITY_ROOTS and row["bucket"] == "gallery":
                row["rebaseRole"] = "single-low-member-audit-only"
                audit_only.append(row)
                continue
            if row["group"] == "Various" or row["bucket"] == "review":
                row["rebaseRole"] = "candidate"
                candidate_paths.append(root / pathlib.PurePosixPath(row["source"]))
                continue
            row["rebaseRole"] = "held-out-of-scope"
            row.update({
                "sourceStatus": "held",
                "reason": "source is outside the stable rebase candidate scope",
            })
            held.append(row)

        candidate_sources = {
            row["source"]: row for row in active
            if row["source"] in {path.relative_to(root).as_posix() for path in candidate_paths}
        }
        planning_photos, move_photos = [], []
        planned_measurements = {}
        for source, row in candidate_sources.items():
            photo = raw_photos[source]
            digest, data = raw_data[source]
            planning_photos.append(photo)
            planned_measurements[source] = (digest, data)
            move_photos.append(_as_photo(
                api, row, root / pathlib.PurePosixPath(source), data, digest,
            ))

        all_names = {name for _group, name, _folder in folders}
        candidates = []
        candidates_by_id = {row["photoId"]: row for row in candidate_sources.values()}
        protected_folders = {
            person["folder"] for person in decision_catalog["people"].values() if person.get("protected")
        }
        explicit_reviews = _explicit_review_placements(catalog)
        accepted_reviews = _explicit_review_placements(catalog, action_types=("match-accepted",))
        for photo in planning_photos:
            photo_id = metadata.photo_id_from_name(photo.name)
            row = candidates_by_id[photo_id]
            record = decision_catalog.get("photos", {}).get(photo_id, {})
            review = admission_enabled and row["bucket"] == "review"
            prior_explicit_review = review and (photo_id, row["source"]) in explicit_reviews
            explicit_review = prior_explicit_review and (
                not reconsider_holds or (photo_id, row["source"]) in accepted_reviews
            )
            candidates.append({
                "photoId": photo_id,
                "sourceFolder": row["owner"],
                "sourceBucket": (
                    "Pool" if photo_id in release_ids else
                    "Pool" if row["group"] == "Various" and row["bucket"] == "gallery"
                    else row["bucket"].title()
                ),
                "side": "Prospects",
                "protected": bool(photo_id in locked_ids or record.get("protected")),
                "workflowSelected": photo_id in workflow_ids,
                "vector": photo.vec,
                "sha256": row["sourceHash"],
                # Matching accepts single and dominant main faces (match-only);
                # reference votes stay limited to single-face quality.
                **(face_quality.candidate_fields(candidate_quality(photo, row["source"]))
                   if admission_enabled else {"qualityEligible": False}),
                "identityProtected": row["bucket"] == "gallery" and row["owner"] in protected_folders,
                "rebaseCandidate": admission_enabled,
                "explicitReviewPlacement": explicit_review,
                "priorExplicitReviewPlacement": prior_explicit_review,
                "regroupReview": photo_id in release_ids or (review and not explicit_review),
                "detachedOutlier": photo_id not in release_ids and row["group"] in IDENTITY_ROOTS and row["bucket"] == "gallery",
                **({"releaseStandardName": row["standardName"]}
                   if photo_id in release_ids and row.get("standardName") else {}),
                **rejections.photo_state(catalog, photo),
            })
        measurement_seconds = time.perf_counter() - phase_started - fresh_selection_seconds
        fresh_core_seconds = (
            measurement_seconds - fresh_measurement_seconds if fresh_source_release else None
        )
        phase_started = time.perf_counter()
        if admission_enabled:
            reference_rows = normal_admission.reference_rows(reference_space, cores, decision_catalog)
            # The verified cohort explicitly releases source-side protections.
            # Keep their actual values in candidates/evidence; receiving-identity,
            # explicit Review, rejection and quality safeguards remain unchanged.
            scoring_candidates = [
                {**candidate, "protected": False, "workflowSelected": False, "identityProtected": False}
                if candidate["photoId"] in release_ids else candidate
                for candidate in candidates
            ]
            report = normal_admission.two_round_plan(
                api, scoring_candidates, cores,
                reference_rows,
                settings, policy, all_names, locked=lock_cast_admission,
                **({"released_bindings": [
                    binding for binding in released_bindings
                    if release_roles[binding["photoId"]] == "candidate"
                ]} if released_bindings is not None else {}),
            )
        else:
            report = normal_import._route_plan(
                api, candidates, cores, settings, policy, all_names,
            )
        if released_nonvoting:
            snapshot = report.get("referenceSnapshots", {}).get("2")
            if not snapshot or not isinstance(snapshot.get("photoIds"), dict):
                raise ValueError("released non-voting scoring lacks the final voting reference snapshot")
            candidate_by_id = {row["photoId"]: row for row in candidates}
            # A canonical keeper may earn its single vote; each non-voter is
            # scored with its own content retired, so it never scores itself.
            report["releasedNonVotingKeeperReferences"] = sorted(
                photo_id for photo_ids in snapshot["photoIds"].values()
                for photo_id in photo_ids
                if photo_id in candidate_by_id and candidate_by_id[photo_id]["sha256"] in nonvoting_hashes
            )
            existing_refs = {
                row["photoId"]: row for refs in reference_rows.values() for row in refs
            }
            final_refs = {}
            snapshot_content = set()
            for folder, photo_ids in snapshot["photoIds"].items():
                if folder not in cores or len(photo_ids) != len(set(photo_ids)):
                    raise ValueError("released non-voting final reference snapshot is ambiguous")
                final_refs[folder] = []
                for photo_id in photo_ids:
                    ref = existing_refs.get(photo_id)
                    candidate = candidate_by_id.get(photo_id)
                    if ref is None and candidate is not None:
                        ref = {
                            "photoId": photo_id, "sha256": candidate["sha256"],
                            "vector": candidate["vector"],
                            "qualityEligible": candidate["qualityEligible"],
                            **{key: candidate[key] for key in ("rejectionMetadataStale", "rejectedPersonIds")
                               if key in candidate},
                        }
                    if ref is None:
                        raise ValueError(f"{photo_id}: final voting reference cannot be reconstructed")
                    if ref["sha256"] in snapshot_content:
                        raise ValueError("final voting references give duplicate content more than one vote")
                    snapshot_content.add(ref["sha256"])
                    final_refs[folder].append(ref)
            final_cores, final_refs = normal_admission.refresh_references(cores, final_refs)
            final_version = normal_admission.context(
                final_cores, final_refs, policy, locked=lock_cast_admission,
            )["referenceVersion"]
            if final_version != snapshot.get("referenceVersion"):
                raise ValueError("released non-voting final voting references differ from the recorded snapshot")
            canonical_sources = []
            seen_canonical = set()
            for row in released_nonvoting:
                matches = [
                    source for source in rows
                    if source.get("photoId") == row.get("contentVoteCanonicalId")
                    and source.get("source") == row.get("contentVoteCanonicalSource")
                    and source.get("sourceHash") == row["sourceHash"]
                ]
                if len(matches) != 1:
                    raise ValueError(f"{row['photoId']}: non-voting canonical inventory is missing or ambiguous")
                if matches[0]["photoId"] not in seen_canonical:
                    canonical_sources.append(matches[0])
                    seen_canonical.add(matches[0]["photoId"])
                photo = raw_photos[row["source"]]
                record = decision_catalog.get("photos", {}).get(row["photoId"], {})
                review = row["bucket"] == "review"
                nonvoting_candidates.append({
                    **row, "sha256": row["sourceHash"], "sourceFolder": row["owner"],
                    "sourceBucket": (
                        "Pool" if row["group"] == "Various" and row["bucket"] == "gallery"
                        else row["bucket"].title()
                    ),
                    "side": "Prospects", "vector": photo.vec,
                    "measurementSha256": metadata.content_sha256(
                        native_paths.get(row["source"], root / pathlib.PurePosixPath(row["source"]))
                    ),
                    "protected": bool(row["photoId"] in locked_ids or record.get("protected")),
                    "workflowSelected": row["photoId"] in workflow_ids,
                    "identityProtected": row["bucket"] == "gallery" and row["owner"] in protected_folders,
                    "explicitReviewPlacement": (
                        review and (row["photoId"], row["source"]) in explicit_reviews
                        and (not reconsider_holds or (row["photoId"], row["source"]) in accepted_reviews)
                    ),
                    "priorExplicitReviewPlacement": (
                        review and (row["photoId"], row["source"]) in explicit_reviews
                    ),
                    "qualityEligible": (
                        photo.usable(settings["minFace"]) and photo.faces == 1
                        and getattr(photo, "f2", 0.) <= settings["multiFace"]
                    ),
                    **rejections.photo_state(catalog, photo),
                })
            nonvoting_report = normal_admission.score_nonvoting_duplicates(
                api, [
                    {**candidate, "protected": False, "workflowSelected": False, "identityProtected": False}
                    for candidate in nonvoting_candidates
                ], final_cores, final_refs, settings, policy,
                canonical_sources, locked=lock_cast_admission,
            )
            canonical_ids = {row["contentVoteCanonicalId"] for row in released_nonvoting}
            voting_candidates = [
                {
                    **candidate,
                    "source": candidates_by_id[candidate["photoId"]]["source"],
                    "measurementSha256": (
                        metadata.content_sha256(
                            native_paths.get(
                                candidates_by_id[candidate["photoId"]]["source"],
                                root / pathlib.PurePosixPath(candidates_by_id[candidate["photoId"]]["source"]),
                            )
                        ) if candidate["photoId"] in canonical_ids else None
                    ),
                }
                for candidate in scoring_candidates
            ]
            nonvoting_report = normal_admission.follow_nonvoting_provisional(
                nonvoting_report, [
                    {**candidate, "protected": False, "workflowSelected": False, "identityProtected": False}
                    for candidate in nonvoting_candidates
                ], voting_candidates, report["assignments"] + report["held"], report["clusters"],
                locked=lock_cast_admission,
            )
            nonvoting_by_id = {row["photoId"]: row for row in nonvoting_candidates}
            for result in nonvoting_report["results"]:
                decision = result["decision"]
                if decision.get("preserveStaged") or not (
                    decision.get("destination") or decision.get("reviewDestination")
                ):
                    candidate = nonvoting_by_id[result["photoId"]]
                    if candidate.get("rejectionMetadataStale") or candidate.get("explicitReviewPlacement"):
                        raise ValueError(
                            f"{result['photoId']}: released non-voting candidate has no safe independent "
                            "placement; resolve its canonical, quality, rejection or Review evidence"
                        )
                    decision = result["decision"] = normal_admission.unresolved_release_review(
                        decision, result.get("comparisons") or [], locked=lock_cast_admission,
                    )
                decision["normalAdmission"] = True
                decision.setdefault("referenceVersion", final_version)
                (report["assignments"] if decision.get("destination") else report["held"]).append(decision)
                row = next(item for item in released_nonvoting if item["photoId"] == result["photoId"])
                candidate_sources[row["source"]] = row
                planned_measurements[row["source"]] = raw_data[row["source"]]
                move_photos.append(raw_photos[row["source"]])
            report["releasedNonVotingEvidence"] = nonvoting_report["results"]
        if reconsidered_nonvoting:
            canonical_sources = []
            seen_canonical = set()
            ordinary_candidates = []
            for row in reconsidered_nonvoting:
                matches = [
                    source for source in rows
                    if source.get("photoId") == row.get("contentVoteCanonicalId")
                    and source.get("source") == row.get("contentVoteCanonicalSource")
                    and source.get("sourceHash") == row["sourceHash"]
                ]
                if len(matches) != 1:
                    raise ValueError(f"{row['photoId']}: non-voting canonical inventory is missing or ambiguous")
                if matches[0]["photoId"] not in seen_canonical:
                    canonical_sources.append(matches[0])
                    seen_canonical.add(matches[0]["photoId"])
                photo = raw_photos[row["source"]]
                record = decision_catalog.get("photos", {}).get(row["photoId"], {})
                review = row["bucket"] == "review"
                placement = (row["photoId"], row["source"])
                ordinary_candidates.append({
                    **row, "sha256": row["sourceHash"], "sourceFolder": row["owner"],
                    "sourceBucket": (
                        "Pool" if row["group"] == "Various" and row["bucket"] == "gallery"
                        else row["bucket"].title()
                    ),
                    "side": "Prospects", "vector": photo.vec,
                    "measurementSha256": metadata.content_sha256(
                        native_paths.get(row["source"], root / pathlib.PurePosixPath(row["source"]))
                    ),
                    "protected": bool(row["photoId"] in locked_ids or record.get("protected")),
                    "workflowSelected": row["photoId"] in workflow_ids,
                    "identityProtected": row["bucket"] == "gallery" and row["owner"] in protected_folders,
                    "explicitReviewPlacement": review and placement in accepted_reviews,
                    "priorExplicitReviewPlacement": review and placement in explicit_reviews,
                    "qualityEligible": (
                        photo.usable(settings["minFace"]) and photo.faces == 1
                        and getattr(photo, "f2", 0.) <= settings["multiFace"]
                    ),
                    **rejections.photo_state(catalog, photo),
                })
            canonical_ids = {row["contentVoteCanonicalId"] for row in reconsidered_nonvoting}
            voting_candidates = [
                {
                    **candidate,
                    "source": candidates_by_id[candidate["photoId"]]["source"],
                    "measurementSha256": (
                        metadata.content_sha256(
                            native_paths.get(
                                candidates_by_id[candidate["photoId"]]["source"],
                                root / pathlib.PurePosixPath(candidates_by_id[candidate["photoId"]]["source"]),
                            )
                        ) if candidate["photoId"] in canonical_ids else None
                    ),
                }
                for candidate in scoring_candidates
            ]
            reconsidered = normal_admission.reconsider_nonvoting_holds(
                api, ordinary_candidates, cores, reference_rows, settings, policy,
                canonical_sources, voting_candidates, report, locked=lock_cast_admission,
                **({"include_named_gallery": True} if fresh_source_release else {}),
            )
            for result in reconsidered["results"]:
                decision = result["decision"]
                decision["normalAdmission"] = True
                decision.setdefault("referenceVersion", reconsidered["finalReferenceVersion"])
                (report["assignments"] if decision.get("destination") else report["held"]).append(decision)
                if decision.get("destination") or decision.get("reviewDestination"):
                    row = next(item for item in reconsidered_nonvoting if item["photoId"] == result["photoId"])
                    candidate_sources[row["source"]] = row
                    planned_measurements[row["source"]] = raw_data[row["source"]]
                    move_photos.append(raw_photos[row["source"]])
            nonvoting_candidates.extend(ordinary_candidates)
            report["reconsideredNonVotingEvidence"] = reconsidered
        settle_limit = settle_settings(policy)["passes"] if admission_enabled else 0
        settle_seconds, settle_timings, settle_bindings, settle_candidates = 0., [], [], {}
        if settle_limit:
            settle_started = time.perf_counter()
            settle_rows = [
                row for row in active
                if row.get("photoId") and row["sourceStatus"] not in ("incoming-update", "held")
            ] + list(nonvoting)
            settle_evidence, settle_timings, settle_bindings, settle_candidates = _settle_plan(
                api, report, rows=settle_rows,
                candidates=scoring_candidates + [
                    {**row, "protected": False, "workflowSelected": False, "identityProtected": False}
                    if row["photoId"] in release_ids else row
                    for row in nonvoting_candidates
                ],
                raw_photos=raw_photos, release_ids=release_ids, folders=folders,
                cores=all_cores, catalog=decision_catalog, rejection_catalog=catalog,
                settings=settings, policy=policy, names_taken=all_names,
                locked=lock_cast_admission, max_passes=settle_limit,
                fresh_assessment=fresh_assessment if fresh_source_release else None,
                candidate_quality=candidate_quality, locked_ids=locked_ids, workflow_ids=workflow_ids,
                protected_folders=protected_folders,
            )
            report["settle"] = settle_evidence
            if settle_bindings:
                # Fresh release only: originals released by settle join the bound release cohort,
                # so membership/anchor retirement and the release permission override cover them.
                settle_roles = _released_candidate_roles(settle_bindings, active, held, archived_rows)
                release_roles.update(settle_roles)
                release_ids.update(settle_roles)
                settled_ids = set(settle_roles)
                for row in settle_rows:
                    if row["photoId"] in settled_ids:
                        row["rebaseRole"] = "settle-released-member"
                audit_only = [row for row in audit_only if row["photoId"] not in settled_ids]
                standard_names = {
                    row["photoId"]: row["standardName"] for row in rows
                    if row.get("photoId") in settled_ids and row.get("standardName")
                }
                settle_retirement = normal_admission.retire_released_catalog(
                    decision_catalog, settle_bindings, standard_names,
                )
                decision_catalog = settle_retirement["catalog"]
                retirement = {
                    "catalog": decision_catalog,
                    "retiredAnchors": (retirement or {}).get("retiredAnchors", [])
                    + settle_retirement["retiredAnchors"],
                    "retiredGroups": (retirement or {}).get("retiredGroups", [])
                    + settle_retirement["retiredGroups"],
                }
                released_bindings = sorted(
                    (released_bindings or []) + settle_bindings, key=lambda row: row["photoId"],
                )
            # A settled non-voter that was held in place may now have a placement to publish.
            placed = {
                row["photoId"] for row in report["assignments"] + report["held"]
                if (row.get("destination") or row.get("reviewDestination")) and not row.get("preserveStaged")
            }
            for row in settle_rows:
                if row["photoId"] in placed and row["source"] not in candidate_sources:
                    candidate_sources[row["source"]] = row
                    planned_measurements[row["source"]] = raw_data[row["source"]]
                    move_photos.append(raw_photos[row["source"]])
            report["settleReleasedBindings"] = settle_bindings
            report["settleFingerprint"] = _preparation_fingerprint({
                "settle": settle_evidence, "settleReleasedBindings": settle_bindings,
                "assignments": report["assignments"], "held": report["held"], "clusters": report["clusters"],
            })
            if reuse_plan is not None and reuse_plan.get("settleFingerprint") != report["settleFingerprint"]:
                raise ValueError("settle pass decisions differ from preview")
            settle_seconds = time.perf_counter() - settle_started
        elif reuse_plan is not None and reuse_plan.get("settleFingerprint") is not None:
            raise ValueError("settle pass decisions differ from preview")
        if released_bindings is not None:
            decisions = report["assignments"] + report["held"]
            measured_candidates = {row["photoId"]: row for row in candidates}
            measured_candidates.update(settle_candidates)
            measured_candidates.update({row["photoId"]: row for row in (
                nonvoting_candidates if nonvoting else []
            )})
            blocked = []
            for photo_id in sorted(release_ids):
                matches = [row for row in decisions if row["photoId"] == photo_id]
                candidate = measured_candidates.get(photo_id, {})
                match_only_unplaced = (
                    candidate.get("qualityEligible") is True
                    and candidate.get("referenceQualityEligible") is False
                )
                if (len(matches) == 1 and matches[0].get("preserveStaged")
                        and (candidate.get("qualityEligible") is False or match_only_unplaced)
                        and not candidate.get("rejectionMetadataStale")
                        and not candidate.get("explicitReviewPlacement")):
                    # No trustworthy score exists; hold it as unassigned rather than keep
                    # the released photo in its former identity or invent a rival.
                    # A match-only photo cannot found an identity; it may go to a
                    # yellow-or-better rival's Review, never Gallery.
                    rival = matches[0].get("bestMatch")
                    rival_score = matches[0].get("bestScore")
                    yellow = policy["scoreBands"]["yellow"]["minimum"]
                    rivals = ([{"folder": rival, "score": float(rival_score)}]
                              if match_only_unplaced and rival and isinstance(rival_score, (int, float))
                              and rival_score >= yellow
                              else [])
                    matches[0].update(normal_admission.unresolved_release_review(
                        matches[0], rivals, locked=lock_cast_admission,
                    ))
                    matches[0]["reason"] += (
                        "; released match-only dominant-face photo has no existing Gallery match"
                        if match_only_unplaced else
                        "; released photo failed the single-face quality gate"
                    )
                    matches[0].setdefault(
                        "referenceVersion",
                        report.get("referenceSnapshots", {}).get("2", {}).get("referenceVersion"),
                    )
                    matches[0]["normalAdmission"] = True
                if len(matches) != 1 or matches[0].get("preserveStaged"):
                    reasons = [row.get("reason", "no reason recorded") for row in matches]
                    blocked.append(f"{photo_id}: {len(matches)} decision(s): {', '.join(reasons)}")
            if blocked:
                raise ValueError(
                    "released candidates missing, ambiguous or protected/held: " + "; ".join(blocked)
                )
            evidence = []
            for photo_id in release_ids:
                matches = [row for row in decisions if row["photoId"] == photo_id]
                decision = matches[0]
                decision.setdefault("referenceEligible", False)
                candidate = measured_candidates[photo_id]
                binding = next(row for row in released_bindings if row["photoId"] == photo_id)
                evidence.append({
                    **binding, "role": release_roles[photo_id],
                    "actualSourceFolder": candidate["sourceFolder"],
                    "actualSourceBucket": pathlib.PurePosixPath(binding["currentPath"]).parent.name,
                    "matchingBucket": "Pool",
                    "protected": candidate["protected"],
                    "workflowSelected": candidate["workflowSelected"],
                    "identityProtected": candidate["identityProtected"],
                    "explicitReviewPlacement": candidate["explicitReviewPlacement"],
                    "priorExplicitReviewPlacement": candidate["priorExplicitReviewPlacement"],
                    "qualityEligible": candidate["qualityEligible"],
                    "sourceProtectionOverride": True,
                    **{key: candidate[key] for key in ("rejectionMetadataStale", "rejectedPersonIds")
                       if key in candidate},
                    "decision": dict(decision),
                })
            for photo_id, role in sorted(release_roles.items()):
                if role != "archived-duplicate":
                    continue
                binding = next(row for row in released_bindings if row["photoId"] == photo_id)
                archive = archives.get(binding["currentPath"])
                if not archive or archive["photoId"] != photo_id or archive["sha256"] != binding["sha256"]:
                    raise ValueError(f"{photo_id}: released identical copy lacks its bound duplicate archive")
                evidence.append({
                    **binding, "role": role,
                    "decision": {
                        "photoId": photo_id, "duplicateArchive": archive["destination"],
                        "keeperPhotoId": archive.get("selectedPhotoId"), "keeperSource": archive["selectedSource"],
                        "referenceEligible": False,
                        "reason": "released byte-identical copy archived recoverably; its keeper is placed by matching",
                    },
                })
            report["releasedPhotoBindings"] = released_bindings
            report["releasedDecisionEvidence"] = sorted(evidence, key=lambda row: row["photoId"])
            report["releasedSourceRetirement"] = {
                "retiredAnchors": retirement["retiredAnchors"],
                "retiredGroups": retirement["retiredGroups"],
            }
        admission_seconds = time.perf_counter() - phase_started - settle_seconds
        phase_started = time.perf_counter()
        report["lockCastAdmission"] = lock_cast_admission
        report["reconsiderHolds"] = reconsider_holds
        if fresh_source_release:
            report["freshSourceRelease"] = True
            report["freshSourceAssessment"] = fresh_assessment
            report["freshMeasurementProof"] = fresh_measurement_proof
            report["freshGalleryCount"] = len(fresh_assessment["assessment"])
            report["freshSelectedCount"] = len(fresh_assessment["bindings"])
            report["freshBlockedCount"] = len(fresh_assessment["blockedBindings"])
            report["freshUnavailableCount"] = sum(
                row["score"] is None for row in fresh_assessment["assessment"]
            )
            report["freshNonVotingCount"] = sum(
                row["sourceStatus"] == "same-content-nonvoting" for row in fresh_assessment["assessment"]
            )
        prior_review_candidates = [
            {"photoId": candidate["photoId"], "source": candidates_by_id[candidate["photoId"]]["source"]}
            for candidate in candidates if candidate["priorExplicitReviewPlacement"]
        ]
        if nonvoting:
            prior_review_candidates.extend(
                {"photoId": candidate["photoId"], "source": candidate["source"]}
                for candidate in nonvoting_candidates if candidate["priorExplicitReviewPlacement"]
            )
        report["priorExplicitReviewPlacements"] = sorted(
            prior_review_candidates, key=lambda row: (row["photoId"], row["source"]),
        )
        report["preparationWorkersRequested"] = preparation_workers
        primary_rows = [
            row for row in rows if row["group"] in IDENTITY_ROOTS | {"Various"}
        ]
        separate_domain_rows = [
            row for row in rows if row["group"] not in IDENTITY_ROOTS | {"Various"}
        ]
        same_content_nonvoters = [
            row for row in held
            if row.get("contentVoteStatus") == "nonvoting-duplicate-content"
        ]
        cross_id_owner_conflicts = [
            row for row in held
            if row.get("versionConflict")
            and "different stable IDs" in row.get("reason", "")
        ]
        # Stable rebase never performs an identity auto-merge. Keep any planner
        # merge-like diagnostic as a hold rather than granting an implicit action.
        report["identityActions"] = []
        report.update({
            "kind": "normal-rebase-plan",
            "schemaVersion": 1,
            "scope": "selected Working Gallery/Review root only; no external prior-Working overlay",
            "profile": profile,
            "runId": run_id,
            "sourceRows": rows,
            "sourceHashes": {row["source"]: row["sourceHash"] for row in rows},
            "sourceRowCount": len(rows),
            "primaryPhysicalPhotoRows": len(primary_rows),
            "separateDomainPhysicalRows": len(separate_domain_rows),
            "distinctPrimaryContentSHA256Count": len({
                row["sourceHash"] for row in primary_rows
            }),
            "uniqueLogicalPhotoIdCount": len({
                row["photoId"] for row in primary_rows if row.get("photoId")
            }),
            "uniquePhotoIdsAcrossSeparateDomains": len({
                row["photoId"] for row in rows if row.get("photoId")
            }),
            "physicalRowsByRootAndBucket": dict(sorted(collections.Counter(
                f"{row.get('group')}/{row['bucket']}" for row in rows
            ).items())),
            "canonicalInputCount": len(active),
            "exactAliasCount": len(aliases),
            "sameContentNonVotingDuplicateCount": len(same_content_nonvoters),
            "crossIdOwnerConflictCount": len(cross_id_owner_conflicts),
            "heldSourceCount": len(held) - len(nonvoting),
            "incomingUpdates": {
                photo_id: {
                    "source": row["source"], "owner": row["updateOwner"],
                    "previousSource": row["previousSource"],
                    "previousHash": row["previousHash"],
                    "sourceHash": row["sourceHash"],
                    "rule": row["versionRule"],
                }
                for photo_id, row in sorted(updates.items())
            },
            "exactAliases": aliases,
            "duplicateArchives": archives,
            "junkDispositions": junk,
            "junkStorage": junk_prefix,
            "unresolvedDuplicateIds": unresolved_ids,
            "collisionModifiedNs": collision_dates,
            "sourceHolds": [row for row in held if row not in nonvoting],
            "inputPolicy": {
                "idless": "tools.art.originals.content_id(raw bytes) plus standard_name; no source rename during preview",
                "sameIdVersions": (
                    "archive redundant copies and route one keeper normally; choose the unique newest "
                    "different-byte version unless protected or lineage-conflicted"
                    if admission_enabled else "legacy Various/gallery incoming version selection"
                ),
                "exactDuplicates": "tools.art.duplicates.keeper; one canonical ID+SHA input",
                "differentIdsSameBytes": (
                    "use duplicates.keeper for one same-owner content vote while preserving all IDs; "
                    "archive eligible redundant Various copies, including exact matches to a unique "
                    "verified retained original; conflicting named owners/decisions "
                    "are held without cross-ID identity merge"
                ),
                "oldWorking": "no external overlay; verified retained sources inside the selected root remain eligible",
            },
            "coreCount": len(cores),
            "coreDiagnostics": core_diagnostics,
            "fragmentQualification": fragment_evidence,
            "configuredAnchorPeople": sorted(
                person_id for person_id in decision_catalog.get("people", {})
                if person_id not in catalog.get("people", {})
            ),
            "lockedPhotoIds": sorted(locked_ids),
            "policyVersion": policy["version"],
            "policyStatus": policy["status"],
            "bindings": _bindings(api, cfg, policy),
            "catalogueSHA256": metadata.content_sha256(metadata.path_for_root(root)),
            "configurationSHA256": hashlib.sha256(
                json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
            "profileMatchingPolicy": "shared frozen-core and candidate rules",
            "sourceRowScope": (
                "Primary image files in Gallery/Review only. Derivatives, retained metadata, "
                "reports and other non-image files are preserved but are not photo inputs. "
                "Artists are counted and hash-bound as a separate untouched domain."
            ),
            "viewerContract": {
                "required": sorted(REQUIRED_VIEWERS),
                "experimentalArtifactsRequired": False,
                "missingOptionalHistory": "publish a truthful intake_runs.html page; do not fabricate experimental output",
            },
            "phaseLog": [
                {"phase": "source-inventory-and-sha256", "status": "complete", "durationSeconds": inventory_seconds},
                {"phase": "stable-id-normalization-and-version-selection", "status": "complete", "durationSeconds": normalization_seconds},
                {"phase": "accepted-profile-preparation", "status": "complete" if prepared else "deferred",
                 **({"durationSeconds": preparation_seconds,
                     "timingScope": "current reuse verification" if (reuse_plan is not None or reuse_preparation is not None)
                     else "current preparation and verification"} if prepared else {})},
                {"phase": "source-bound-measurement-and-frozen-cores", "status": "complete", "durationSeconds": measurement_seconds},
                {"phase": "bounded-two-round-admission" if admission_enabled else "single-candidate-plan", "status": "complete", "durationSeconds": admission_seconds},
                {"phase": "bound-admission-and-retained-member-check" if admission_enabled else "single-frozen-low-member-audit", "status": "complete"},
                {"phase": "final-rival-family-viewer-publication", "status": "apply-only"},
            ],
        })
        if fresh_source_release:
            report["phaseLog"][3:4] = [
                {"phase": "fresh-source-measurement", "status": "complete",
                 "durationSeconds": fresh_measurement_seconds},
                {"phase": "fresh-source-release-selection", "status": "complete",
                 "durationSeconds": fresh_selection_seconds},
                {"phase": "fresh-post-release-frozen-cores", "status": "complete",
                 "durationSeconds": fresh_core_seconds},
            ]
        if report.get("settle"):
            settle = report["settle"]
            position = next(
                index for index, row in enumerate(report["phaseLog"])
                if row["phase"] == "bounded-two-round-admission"
            ) + 1
            report["phaseLog"][position:position] = [
                {"phase": f"settle-pass-{item['pass']}", "status": "complete", "durationSeconds": seconds,
                 "settlePass": item["pass"], "releasedCount": item["releasedCount"],
                 "movedCount": item["movedCount"], "remainingFlaggedCount": item["remainingFlaggedCount"],
                 "newIdentityCount": len(item["newIdentities"])}
                for item, seconds in zip(settle["passes"], settle_timings)
            ]
            report["settlePassCount"] = settle["passCount"]
            report["settleReleasedCount"] = sum(item["releasedCount"] for item in settle["passes"])
            report["settleMovedCount"] = len({
                photo_id for item in settle["passes"] for photo_id in item["movedPhotoIds"]
            })
            report["settleDidNotSettleCount"] = len(settle["didNotSettle"])
        report["assignedCount"] = len(report["assignments"])
        report["heldCount"] = len(report["held"]) + len(held) - len(nonvoting)
        report["canonicalSourceHashes"] = {
            row["source"]: row["sourceHash"] for row in active
        }
        report["preparation"] = (
            "FAST original-byte matching; editing and 944 framing deferred; pixels are not certified clean"
            if profile == "fast" else
            "FULL/LEAN accepted native recipe; original files retained in selected-input evidence"
        )
        prepared_sources = set(prepared[2]) if prepared else set()
        report["preparationScope"] = (
            ("all eligible non-retained active and selected non-voting Gallery/Review originals; "
             if nonvoting else "all eligible non-retained active Gallery/Review originals; ")
            + "references and candidates are both measured from the selected prepared native"
            if profile in ("full", "lean") else
            ("all eligible active and selected non-voting Gallery/Review originals are measured from unchanged raw bytes"
             if nonvoting else "all eligible active Gallery/Review originals are measured from unchanged raw bytes")
        )
        report["preparationInputCount"] = len(prepared_sources)
        report["preparedReferenceCount"] = sum(
            1 for row in active
            if row["source"] in prepared_sources
            and row["group"] in IDENTITY_ROOTS and row["bucket"] == "gallery"
            and row["photoId"] not in release_ids and row["sourceHash"] not in nonvoting_hashes
        )
        report["preparedCandidateCount"] = sum(
            1 for row in measured_rows
            if row["source"] in prepared_sources
            and row["source"] in candidate_sources
        )
        report["preparationReusedFromPreview"] = bool(
            prepared and (reuse_plan is not None or reuse_preparation is not None)
        )
        if prepared:
            report["preparationRoot"] = str(prepared[0])
            report["preparationManifestSHA256"] = metadata.content_sha256(prepared[0] / "manifest.json")
        if preparation_reuse:
            report["preparationReuse"] = preparation_reuse
        if preparation_generation:
            report["preparationGeneration"] = preparation_generation

        update_moves = []
        photos_for_moves = list(move_photos)
        stage_photos = list(move_photos)
        update_audit = []
        for photo_id, row in updates.items():
            source = root / pathlib.PurePosixPath(row["source"])
            measured_path = native_paths.get(row["source"], source)
            digest, data = _infer(api, cache, embedder, measured_path, persist_evidence=for_apply)
            photo = _as_photo(api, row, source, data, digest)
            photos_for_moves.append(photo)
            stage_photos.append(photo)
            update_audit.append(_as_photo(
                api, row, root / "Various" / "review" / row["standardName"], data, digest,
            ))
            update_moves.append({
                "photoId": photo_id,
                "source": row["source"],
                "destination": row["previousSource"],
                "sha256": row["sourceHash"],
                "reason": "accepted unique-newest same-ID incoming update; current owner/name retained",
            })
        moves = maintenance.proposed_moves(
            report, photos_for_moves, root, **({"duplicate_archives": archives} if archives else {}),
        )
        moves = [move for move in moves if move["photoId"] not in updates]
        for move in moves:
            source_row = candidate_sources.get(move["source"])
            if source_row:
                destination_folder = pathlib.PurePosixPath(move["destination"]).parent.parent.as_posix()
                destination_prefix = originals.prefix_of(pathlib.PurePosixPath(destination_folder).name)
                target_name = originals.standard_name(
                    source_row["standardName"], destination_prefix, known=prefixes,
                    digest=_naming_digest(source_row["photoId"]),
                )
                move["destination"] = (
                    pathlib.PurePosixPath(destination_folder) / pathlib.PurePosixPath(move["destination"]).parent.name / target_name
                ).as_posix()
                move["sha256"] = source_row["sourceHash"]
                if move["destination"] != move["source"]:
                    move.pop("membershipOnly", None)
                    move.pop("preparationOnly", None)
        moves.extend(update_moves)
        normalization_moves = []
        planned_sources = {move["source"] for move in moves}
        audit_only_sources = {row["source"] for row in audit_only}
        for row in active:
            if (
                row["sourceStatus"] == "incoming-update"
                or row["photoId"] in core_ids
                or row["source"] in audit_only_sources
            ):
                continue
            if row["idBasis"] not in (
                "raw-content-sha1-8", "normalized-source-filename", "verified-retained-photo-id",
            ):
                continue
            if row["source"] in planned_sources:
                continue
            source_path = pathlib.PurePosixPath(row["source"])
            destination = (source_path.parent / row["standardName"]).as_posix()
            if destination == row["source"]:
                continue
            normalization_moves.append({
                "photoId": row["photoId"], "source": row["source"],
                "destination": destination, "sha256": row["sourceHash"],
                "reason": "controlled stable-ID filename normalization; original name/path/hash retained in receipt and recovery",
                "normalizationOnly": True,
            })
            planned_sources.add(row["source"])
        moves.extend(normalization_moves)
        # One correction pass over initial frozen cores only. Candidate Gallery
        # sources are presented as Various so they cannot become reference votes.
        audit_photos = [
            photo for photo in raw_space.photos
            if metadata.photo_id_from_name(photo.name) in core_ids
            and photo.path.relative_to(root).as_posix() not in candidate_sources
        ]
        audit_photos.extend(update_audit)
        for row in audit_only:
            source = row["source"]
            measured_path = native_paths.get(source, root / pathlib.PurePosixPath(source))
            digest, data = _infer(api, cache, embedder, measured_path, persist_evidence=for_apply)
            audit_photo = _as_photo(
                api, row, root / "Various" / "review" / row["standardName"], data, digest,
            )
            stage_photos.append(_as_photo(
                api, row, root / pathlib.PurePosixPath(source), data, digest,
            ))
            source_path = pathlib.PurePosixPath(source)
            own_destination = (
                (source_path.parent / row["standardName"]).as_posix()
                if row["idBasis"] in ("raw-content-sha1-8", "normalized-source-filename")
                else source
            )
            audit_photos.append(audit_photo)
            moves.append({
                "photoId": row["photoId"], "source": source,
                "destination": own_destination, "sha256": row["sourceHash"],
                "reason": "existing non-core Gallery member; owner retained for the single frozen policy audit",
                "auditOnly": True,
            })
        for source, row in candidate_sources.items():
            digest, data = planned_measurements[source]
            audit_photo = _as_photo(
                api, row, root / "Various" / "review" / row["standardName"], data, digest,
            )
            audit_photos.append(audit_photo)
        audit_space = api.Space(audit_photos, settings, mean=mean)
        checked, audit = _check_frozen_consistency(
            api, audit_space, decision_catalog, policy, moves, update_ids=update_ids,
        )
        report["frozenConsistencyCheck"] = audit
        report["moves"] = checked
        report["moves"] = [
            row for row in report["moves"] if row["source"] != row["destination"] or row.get("membershipOnly")
        ]
        # Existing current-owner audit rows that were not corrected are evidence
        # only; they need no publication move or preparation.
        report["moves"] = [
            row for row in report["moves"]
            if not row.get("auditOnly") or row["destination"].endswith("/review/" + pathlib.PurePosixPath(row["destination"]).name)
        ]
        unversioned = sorted(
            row["photoId"] for row in report["moves"]
            if (row.get("castAdmission") or row.get("normalAdmission")) and not row.get("referenceVersion")
        )
        if unversioned:
            # Publication records the reference version on every admitted membership.
            raise ValueError("admission moves lack a reference version: " + ", ".join(unversioned))
        if profile in ("full", "lean") and prepared:
            for move in report["moves"]:
                if move.get("membershipOnly") and move["source"] in prepared[2]:
                    move.pop("membershipOnly")
            moved_ids = {row["photoId"] for row in report["moves"]}
            staged_ids = {
                metadata.photo_id_from_name(photo.name) for photo in stage_photos
            }
            for row in active:
                if row["source"] not in prepared[2] or row["photoId"] in moved_ids:
                    continue
                source_path = pathlib.PurePosixPath(row["source"])
                destination = (
                    (source_path.parent / row["standardName"]).as_posix()
                    if row["idBasis"] in ("raw-content-sha1-8", "normalized-source-filename")
                    else row["source"]
                )
                report["moves"].append({
                    "photoId": row["photoId"],
                    "source": row["source"],
                    "destination": destination,
                    "sha256": row["sourceHash"],
                    "reason": (
                        "accepted FULL/LEAN native refresh; identity and owner unchanged"
                        + (" with stable content-ID filename" if destination != row["source"] else "")
                    ),
                    "preparationOnly": destination == row["source"],
                })
                moved_ids.add(row["photoId"])
                if destination != row["source"]:
                    normalization_moves.append({
                        "photoId": row["photoId"],
                        "source": row["source"],
                        "destination": destination,
                        "sha256": row["sourceHash"],
                        "reason": "generated stable content-ID filename; original name/path/hash retained in receipt and recovery",
                    })
                if row["photoId"] not in staged_ids:
                    stage_photos.append(raw_photos[row["source"]])
                    staged_ids.add(row["photoId"])
            report["moves"].sort(key=lambda row: (row["photoId"], row["source"], row["destination"]))
        report["candidateCount"] = len(candidates) + len(nonvoting)
        report["normalizationMoves"] = normalization_moves
        report["sourceConservation"] = {
            "physicalRows": len(rows),
            "primaryPhysicalPhotoRows": len(primary_rows),
            "separateDomainPhysicalRows": len(separate_domain_rows),
            "distinctPrimaryContentSHA256Count": len({
                row["sourceHash"] for row in primary_rows
            }),
            "classifiedRows": sum(
                1 for row in rows if row.get("sourceStatus") not in (None, "unclassified")
            ),
            "unclassifiedRows": sum(
                1 for row in rows if row.get("sourceStatus") == "unclassified"
            ),
            "exactAliases": len(aliases),
            "duplicateArchives": len(archives),
            "junkDispositions": len(junk),
            "sameContentNonVotingDuplicates": len(same_content_nonvoters),
            "crossIdOwnerConflicts": len(cross_id_owner_conflicts),
            "uniqueLogicalPhotoIds": report["uniqueLogicalPhotoIdCount"],
            "sourceHashCount": len(report["sourceHashes"]),
            "allSourceRowsHashBoundToReceipt": len(report["sourceHashes"]) == len(rows),
            "selectedSourceRecovery": (
                "moved sources and overwritten targets are included in the scoped transaction backup; selected "
                "FULL/LEAN inputs are also copied into preparation evidence, while FAST output keeps raw bytes"
            ),
            "logicalInputRoles": dict(sorted(collections.Counter(
                row.get("rebaseRole", row.get("sourceStatus", "unclassified")) for row in active + nonvoting
            ).items())),
        }
        for row in active:
            if not row.get("collisionRule"):
                continue
            record = catalog["photos"].get(row["photoId"], {})
            membership = record.get("membership", {})
            person = catalog["people"].get(membership.get("personId"), {})
            changed_binding = bool(record) and (
                record.get("contentSha256") != row["sourceHash"]
                or (person and person["folder"] != row["owner"])
            )
            if not changed_binding:
                continue
            move = next((move for move in report["moves"] if move["source"] == row["source"]), None)
            if move is None:
                move = {
                    "photoId": row["photoId"], "source": row["source"], "destination": row["source"],
                    "sha256": row["sourceHash"], "reason": "bind catalogue to the selected same-ID keeper",
                    "preparationOnly": True, "membershipOnly": True,
                }
                report["moves"].append(move)
                stage_photos.append(raw_photos[row["source"]])
            move["collisionRebind"] = True
        if fresh_source_release:
            report["freshCastSeed"] = _fresh_cast_seed_outcomes(
                fresh_assessment, report["moves"], archives,
                report.get("releasedDecisionEvidence", []), workflow_ids,
            )
            seed_summary = report["freshCastSeed"]["summary"]
            report["freshCastSeedIdentityCount"] = seed_summary["identityCount"]
            report["freshCastSeedKeptCount"] = seed_summary["seedKeptCount"]
            report["freshCastSeedReleaseCount"] = seed_summary["seedReleaseCount"]
            report["freshCastSeedReturnedCount"] = seed_summary["seedReturnedCount"]
            report["freshCastWorkflowReplacementCount"] = len(
                report["freshCastSeed"]["workflowReplacementProposals"]
            )
            if reuse_plan is not None and reuse_plan.get("freshCastSeed") != report["freshCastSeed"]:
                raise ValueError("fresh cast seed outcomes differ from preview")
        # Item (g): identity folders left with no Gallery/Review original are
        # retired inside the publication transaction; an emptied cast folder stops here.
        report["emptiedIdentityRetirement"] = {
            "retiredRoot": empty_retirement.retired_root(root, cfg),
            "folders": empty_retirement.plan_emptied(
                root, cfg, [move for move in report["moves"] if not move.get("membershipOnly")],
                [*report.get("duplicateArchives", {}).values(), *report.get("junkDispositions", {}).values()],
            ),
        }
        report["emptiedIdentityFingerprint"] = _preparation_fingerprint(report["emptiedIdentityRetirement"])
        if reuse_plan is not None and reuse_plan.get("emptiedIdentityFingerprint") != report["emptiedIdentityFingerprint"]:
            raise ValueError("emptied identity folders to retire differ from preview")
        if released_bindings is not None:
            for binding in released_bindings:
                if release_roles.get(binding["photoId"]) == "archived-duplicate":
                    # Bound above to its duplicate archive; publication archives it.
                    continue
                matches = [
                    move for move in report["moves"]
                    if move["photoId"] == binding["photoId"]
                    and move["source"] == binding["currentPath"]
                    and move["sha256"] == binding["sha256"]
                ]
                if len(matches) != 1 or not matches[0].get("normalAdmission"):
                    raise ValueError(
                        f"{binding['photoId']}: released decision lacks one bound normal-admission move; "
                        "held or same-path selections require explicit publication evidence"
                    )
                matches[0]["releasedPhotoId"] = binding["photoId"]
            report["releasedPlanFingerprint"] = _preparation_fingerprint({
                "bindings": released_bindings,
                "decisionEvidence": report["releasedDecisionEvidence"],
                "nonVotingEvidence": report.get("releasedNonVotingEvidence", []),
                "reconsideredNonVotingEvidence": report.get("reconsideredNonVotingEvidence"),
                "reconsiderHolds": report["reconsiderHolds"],
                "priorExplicitReviewPlacements": report["priorExplicitReviewPlacements"],
                "retirement": report["releasedSourceRetirement"],
                **({"freshSourceAssessment": fresh_assessment} if fresh_source_release else {}),
                **({"freshMeasurementProof": fresh_measurement_proof} if fresh_source_release else {}),
                **({"freshCastSeed": report["freshCastSeed"]} if fresh_source_release else {}),
                "referenceSnapshots": report.get("referenceSnapshots"),
                "clusters": report["clusters"],
                "moves": report["moves"],
            })
            if reuse_plan is not None and report["releasedPlanFingerprint"] != reuse_plan.get("releasedPlanFingerprint"):
                raise ValueError("released cohort decisions or publication plan differ from preview")
        if reconsider_holds:
            report["reconsiderHoldsFingerprint"] = _preparation_fingerprint({
                "priorExplicitReviewPlacements": report["priorExplicitReviewPlacements"],
                "nonVotingEvidence": report.get("reconsideredNonVotingEvidence"),
                "assignments": report["assignments"],
                "held": report["held"],
                "referenceSnapshots": report.get("referenceSnapshots"),
                "clusters": report["clusters"],
                "moves": report["moves"],
            })
            if reuse_plan is not None and report["reconsiderHoldsFingerprint"] != reuse_plan.get("reconsiderHoldsFingerprint"):
                raise ValueError("existing hold reassessment decisions differ from preview")
        _validate_move_destinations(report["moves"])
        report["exactAliasTargets"] = _exact_alias_targets(rows, report["moves"], updates=updates, archives=archives)
        report["sourceConservation"]["coalescedExactAliasTargets"] = len(report["exactAliasTargets"])
        permission_moves = [
            move for move in report["moves"]
            if not move.get("preparationOnly") and move["photoId"] not in updates
        ]
        if permission_moves:
            maintenance._validate_permissions(
                root, permission_moves, policy, cfg,
                **({"released_bindings": released_bindings} if released_bindings is not None else {}),
            )
        report["publicationPermissionsVerified"] = True
        publication_space = api.Space(
            [
                raw_photos[row["source"]]
                for row in active + nonvoting if row.get("sourceStatus") != "held"
            ],
            settings, mean=mean,
        )
        next(row for row in report["phaseLog"] if row["phase"] in (
            "bound-admission-and-retained-member-check", "single-frozen-low-member-audit",
        ))["durationSeconds"] = time.perf_counter() - phase_started
        return report, stage_photos, publication_space, catalog, cfg, policy, cache, prepared, run, rows
    finally:
        api.domains.READ_ONLY.reset(read_only_token)
        api.domains.CURRENT.reset(read_token)


def _receipt_path(root, run_id, cfg, explicit=None, *, preview=False):
    if explicit:
        path = pathlib.Path(explicit).resolve()
    else:
        from tools.workflows import comfy_workflows as cw

        suffix = "-preview" if preview else ""
        path = cw.storage_root(cfg, "reports", root=root) / "runs" / f"normal-rebase-{run_id}{suffix}.json"
    if pathlib.Path(root).resolve() not in path.parents:
        raise ValueError("normal rebase receipt must be stored inside the selected library root")
    return path


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="clean Production-derived Working root")
    parser.add_argument("--cache", help="content-addressed embedding cache")
    parser.add_argument("--policy", help="versioned likeness policy JSON")
    parser.add_argument(
        "--reuse-preparation",
        help="verified prior stable-preview selected-preparation output; preview only",
    )
    parser.add_argument(
        "--reuse-preparation-sha256",
        help="expected SHA-256 of the reused preparation manifest.json",
    )
    parser.add_argument("--profile", choices=("full", "lean", "fast"), default="lean")
    parser.add_argument(
        "--preparation-workers", type=int, choices=(1, 2, 3), default=1,
        help="selected FULL/LEAN preparation workers (default 1); repeat on apply",
    )
    parser.add_argument("--run-id", help="stable receipt/run directory identifier")
    parser.add_argument("--receipt", help="receipt path; defaults to the configured reports root under runs/")
    parser.add_argument("--preview-receipt", help="custom preview receipt path to reuse during --apply")
    parser.add_argument("--release-receipt", help="original applied rebase receipt for a verified release cohort")
    parser.add_argument("--release-audit", help="hash-bound original release audit snapshot")
    parser.add_argument("--release-review", help="checked final Review directory following the releases")
    parser.add_argument("--release-run", action="append", default=[],
                        help="release run ID in chronological order; repeat for each release")
    parser.add_argument(
        "--fresh-source-release", action="store_true",
        help="Sandbox-only initial Gallery release assessment before identity formation; repeat on apply",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="preview only (the default)")
    mode.add_argument("--apply", action="store_true", help="publish the complete proposal with scoped recovery")
    mode.add_argument("--check", action="store_true", help="verify a previous applied receipt without rescoring")
    mode.add_argument("--repeat", action="store_true", help="verify the last applied receipt; never repeats mutations")
    mode.add_argument("--recover", action="store_true", help="preview exact publication recovery")
    mode.add_argument("--recover-apply", action="store_true", help="restore the exact pre-publication snapshot")
    parser.add_argument("--sandbox-apply-draft", action="store_true", help="authorize draft policy only in sandbox Working")
    parser.add_argument(
        "--lock-cast-admission", action="store_true",
        help="receiving-only lock for Sisters/Angels; keep cast rivals visible (repeat on apply/check)",
    )
    parser.add_argument(
        "--reconsider-holds", action="store_true",
        help="reconsider prior Review placements in Sandbox Working (repeat on apply)",
    )
    return parser


def _check(root, path, bindings=None):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if data.get("kind") != "normal-rebase-receipt" or data.get("schemaVersion") != 1:
        raise ValueError("not a supported normal rebase receipt")
    if pathlib.Path(data.get("root", "")).resolve() != pathlib.Path(root).resolve():
        raise ValueError("normal rebase receipt is bound to another library root")
    if data.get("status") != "applied":
        raise ValueError(f"normal rebase is {data.get('status')}, not applied")
    if data.get("implementationSHA256") != metadata.content_sha256(pathlib.Path(__file__)):
        raise ValueError("normal rebase implementation changed; preview a new run")
    if bindings is not None and data.get("bindings") != bindings:
        raise ValueError("policy, configuration or shared implementation changed")
    journal = normal_transaction.verify(root, data["journal"])
    _check_retired_folders(data.get("retiredIdentityFolders", []), journal)
    return data


def _check_retired_folders(recorded, journal):
    """The receipt's retired identities must be exactly the journal's retired folders."""
    expected = [(row["source"], row["destination"]) for row in recorded]
    actual = [(row["source"], row["destination"]) for row in journal.get("retiredFolders", [])]
    if expected != actual:
        raise ValueError("receipt retired identity folders differ from the publication journal")


def _recovery_receipt(root, path, bindings=None):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if data.get("kind") != "normal-rebase-receipt" or data.get("schemaVersion") != 1:
        raise ValueError("not a supported normal rebase receipt")
    if pathlib.Path(data.get("root", "")).resolve() != pathlib.Path(root).resolve():
        raise ValueError("normal rebase receipt is bound to another library root")
    if data.get("status") not in ("applied", "recovery-required"):
        raise ValueError(f"normal rebase cannot be recovered from {data.get('status')}")
    if data.get("implementationSHA256") != metadata.content_sha256(pathlib.Path(__file__)):
        raise ValueError("normal rebase implementation changed; recovery requires the exact recorded code")
    if bindings is not None and data.get("bindings") != bindings:
        raise ValueError("policy, configuration or shared implementation changed")
    return data


def _preview_for_apply(root, path, run_id, profile, bindings, cfg=None):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if data.get("kind") != "normal-rebase-preview" or data.get("schemaVersion") != 1:
        raise ValueError("apply requires the matching stable normal-rebase preview receipt")
    if data.get("status") != "preview":
        raise ValueError("apply preview receipt is not in preview state")
    if pathlib.Path(data.get("root", "")).resolve() != pathlib.Path(root).resolve():
        raise ValueError("preview receipt is bound to another library root")
    if data.get("runId") != run_id or data.get("profile") != profile:
        raise ValueError("apply run-id/profile differs from its preview")
    if data.get("implementationSHA256") != metadata.content_sha256(pathlib.Path(__file__)):
        raise ValueError("composer changed since preview; create a new preview")
    if data.get("bindings") != bindings:
        raise ValueError("policy, configuration or shared implementation changed since preview")
    plan = data.get("plan")
    if not isinstance(plan, dict):
        raise ValueError("preview receipt has no bound plan")
    _require_resolved_duplicate_ids(plan.get("unresolvedDuplicateIds", []))
    if plan.get("preparationRoot"):
        if plan.get("preparationReuse"):
            reuse = plan["preparationReuse"]
            if (
                pathlib.Path(plan["preparationRoot"]).resolve()
                != pathlib.Path(reuse.get("path", "")).resolve()
                or plan.get("preparationManifestSHA256") != reuse.get("manifestSHA256")
                or reuse.get("profile") != profile
            ):
                raise ValueError("preview's reused preparation binding is incomplete")
        if plan.get("preparationGeneration"):
            generation = plan["preparationGeneration"]
            if (
                pathlib.Path(plan["preparationRoot"]).resolve()
                != pathlib.Path(generation.get("preparationRoot", "")).resolve()
                or plan.get("preparationManifestSHA256") != generation.get("manifestSHA256")
                or generation.get("profile") != profile
                or generation.get("producerUnchangedDuringGeneration") is not True
            ):
                raise ValueError("preview's preparation generation seal is incomplete")
        if not plan.get("preparationReuse"):
            from tools.workflows import comfy_workflows as cw

            expected = (
                cw.storage_root(cfg or {}, "reports", root=root) / "runs"
                / f"normal-rebase-{run_id}-preview" / "preparation" / "inputs"
                / "_reports" / "preparation" / "selected"
            ).resolve()
            if pathlib.Path(plan["preparationRoot"]).resolve() != expected:
                raise ValueError("preview preparation is not under this run's configured reports root")
    return plan


def _verified_released_lineage(root, cfg, receipt, audit, review, runs):
    from tools.art.likeness_library import movement_history, sandbox_red_release
    from tools.workflows import comfy_workflows as cw

    if not is_sandbox_working_path(root):
        raise ValueError("released cohort rebase requires Sandbox Working")
    reports = cw.storage_root(cfg, "reports", root=root).relative_to(root).as_posix()
    _, records, hashes, successor, inputs = movement_history.collect(
        root, receipt, audit, review, runs, reports,
    )
    if successor is not None:
        raise ValueError("released cohort must start from the current verified release state")
    bindings = sorted(
        ({"photoId": row["photoId"], "currentPath": final, "sha256": row["preparedSHA256"]}
         for row, history, final, active in records if active and history),
        key=lambda row: row["photoId"],
    )
    if not bindings or len({row["photoId"] for row in bindings}) != len(bindings):
        raise ValueError("released cohort is empty or ambiguous")
    evidence = {
        "receipt": str(pathlib.Path(receipt).absolute()),
        "audit": str(pathlib.Path(audit).absolute()),
        "review": str(pathlib.Path(review).absolute()),
        "runs": list(runs), "journalSHA256": hashes, "inputs": inputs,
        "producers": {
            module.__name__: metadata.content_sha256(pathlib.Path(module.__file__))
            for module in (movement_history, sandbox_red_release, normal_recap)
        },
    }
    return bindings, evidence


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    if args.reuse_preparation_sha256 and not args.reuse_preparation:
        parser.error("--reuse-preparation-sha256 requires --reuse-preparation")
    if args.reuse_preparation:
        if not pathlib.Path(args.reuse_preparation).is_absolute():
            parser.error("--reuse-preparation must be an absolute path")
        if not args.reuse_preparation_sha256 or not re.fullmatch(
            r"[0-9a-fA-F]{64}", args.reuse_preparation_sha256,
        ):
            parser.error("--reuse-preparation requires a 64-digit --reuse-preparation-sha256")
        if args.profile == "fast":
            parser.error("--reuse-preparation requires the FULL or LEAN profile")
        if args.preparation_workers != 1:
            parser.error("--preparation-workers applies to new preparation, not --reuse-preparation")
        if args.apply or args.check or args.repeat or args.recover or args.recover_apply:
            parser.error("--reuse-preparation is supported only when creating a new preview")
        args.reuse_preparation_sha256 = args.reuse_preparation_sha256.lower()
    from tools.art import likeness as api
    from tools.workflows import comfy_workflows as cw

    cfg = api.configuration()
    root = pathlib.Path(args.root or cw.work_root(cfg)).resolve()
    run_id = args.run_id or datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if not RUN_ID.fullmatch(run_id):
        parser.error("--run-id must contain only letters, digits, dot, underscore or hyphen")
    if args.apply and not args.run_id:
        parser.error("--apply requires the exact --run-id used for preview")
    if args.preview_receipt and not args.apply:
        parser.error("--preview-receipt is only valid with --apply")
    release_options = (args.release_receipt, args.release_audit, args.release_review, args.release_run)
    if any(release_options) and not all(release_options):
        parser.error("--release-receipt, --release-audit, --release-review and --release-run are required together")
    if any(release_options) and (args.check or args.repeat or args.recover or args.recover_apply):
        parser.error("release lineage options are only valid for a preview or apply")
    if any(release_options) and not is_sandbox_working_path(root):
        parser.error("release lineage requires Sandbox Working")
    if args.fresh_source_release and any(release_options):
        parser.error("--fresh-source-release cannot be combined with release lineage")
    if args.fresh_source_release and not is_sandbox_working_path(root):
        parser.error("--fresh-source-release requires Sandbox Working")
    if args.fresh_source_release and (args.check or args.repeat or args.recover or args.recover_apply):
        parser.error("--fresh-source-release is only valid for a preview or apply")
    if args.reconsider_holds and not is_sandbox_working_path(root):
        parser.error("--reconsider-holds requires Sandbox Working")
    if args.reconsider_holds and (args.check or args.repeat or args.recover or args.recover_apply):
        parser.error("--reconsider-holds is only valid for a preview or apply")
    if (args.check or args.repeat or args.recover or args.recover_apply) and not args.run_id:
        parser.error("--check/--repeat/--recover require the exact --run-id")
    if args.preparation_workers != 1 and (args.profile == "fast" or args.check or args.repeat
                                          or args.recover or args.recover_apply):
        parser.error("--preparation-workers is only valid for a FULL/LEAN preview or apply")
    try:
        receipt_path = _receipt_path(
            root, run_id, cfg, args.receipt,
            preview=not (args.apply or args.check or args.repeat or args.recover or args.recover_apply),
        )
    except ValueError as exc:
        print(f"normal rebase stopped safely: {exc}", file=sys.stderr)
        return 1
    if args.check or args.repeat or args.recover or args.recover_apply:
        pass
    else:
        from tools.workflows import comfy_workflows as cw

        if receipt_path.exists():
            print(f"normal rebase stopped safely: receipt already exists; choose a new run-id: {receipt_path}", file=sys.stderr)
            return 1
        run_suffix = f"normal-rebase-{run_id}" if args.apply else f"normal-rebase-{run_id}-preview"
        run_directory = cw.storage_root(cfg, "reports", root=root) / "runs" / run_suffix
        if run_directory.exists():
            print(f"normal rebase stopped safely: run directory already exists; choose a new run-id: {run_directory}", file=sys.stderr)
            return 1
    journal_path = None
    saved_status = None
    report = None
    policy = None
    preview_plan = None
    if args.check or args.repeat or args.recover or args.recover_apply:
        try:
            policy = load_policy(args.policy)
            bindings = _bindings(api, cfg, policy)
            receipt = (
                _check(root, receipt_path, bindings)
                if args.check or args.repeat else
                _recovery_receipt(root, receipt_path, bindings)
            )
            if bool(receipt["plan"].get("lockCastAdmission")) != args.lock_cast_admission:
                raise ValueError("cast receiving lock differs from the saved run")
            if args.check or args.repeat:
                print(f"normal rebase verified: {receipt_path}")
                print(f"source rows={receipt['plan']['sourceRowCount']}, moves={len(receipt['moves'])}, viewers={len(receipt['viewerPaths'])}, "
                      f"retired identity folders={len(receipt.get('retiredIdentityFolders', []))}")
                for row in receipt.get("retiredIdentityFolders", []):
                    print(f"  retired {row['source']} -> {row['destination']} (verified present; source absent)")
                return 0
            normal_transaction.recover(
                root, receipt["journal"], apply=args.recover_apply,
            )
            if args.recover_apply:
                receipt["status"] = "recovered"
                normal_import._write_receipt(receipt_path, receipt)
            print("recovery applied" if args.recover_apply else "recovery preview only")
            return 0
        except (OSError, ValueError, KeyError) as exc:
            print(f"normal rebase stopped safely: {exc}", file=sys.stderr)
            return 1
    if args.apply:
        if not is_sandbox_working_path(root) and not (
            args.sandbox_apply_draft and is_normal_flow_proof_path(root)
        ):
            print("normal rebase stopped safely: stable whole-library apply is restricted to sandbox Working", file=sys.stderr)
            return 1
        try:
            policy = load_policy(args.policy)
            maintenance.require_authorization(
                root, policy, args.sandbox_apply_draft,
                allow_isolated_proof=args.sandbox_apply_draft and is_normal_flow_proof_path(root),
            )
            preview_path = _receipt_path(
                root, run_id, cfg, args.preview_receipt, preview=True,
            )
            preview_plan = _preview_for_apply(
                root, preview_path, run_id, args.profile, _bindings(api, cfg, policy), cfg,
            )
        except (OSError, ValueError) as exc:
            print(f"normal rebase stopped safely: {exc}", file=sys.stderr)
            return 1
    try:
        release_bindings, release_evidence = (None, None)
        if all(release_options):
            release_bindings, release_evidence = _verified_released_lineage(
                root, cfg, args.release_receipt, args.release_audit, args.release_review, args.release_run,
            )
        if preview_plan is not None and preview_plan.get("releaseLineage") != release_evidence:
            raise ValueError("released lineage differs from preview")
        report, photos, space, catalog, cfg, policy, cache, prepared, run, rows = _plan(
            root, args.profile, run_id, api=api, cache_path=args.cache, policy_path=args.policy,
            for_apply=args.apply, reuse_plan=preview_plan,
            reuse_preparation=args.reuse_preparation,
            reuse_preparation_sha256=args.reuse_preparation_sha256,
            lock_cast_admission=args.lock_cast_admission,
            preparation_workers=args.preparation_workers,
            released_bindings=release_bindings,
            reconsider_holds=args.reconsider_holds,
            fresh_source_release=args.fresh_source_release,
        )
        if args.fresh_source_release:
            release_bindings = report.get("releasedPhotoBindings")
        if release_evidence is not None:
            report["releaseLineage"] = release_evidence
        if args.apply:
            publication_started = time.perf_counter()
            moves = report["moves"]
            move_sources = {row["source"] for row in moves}
            ordinary = [row for row in moves if row.get("photoId") not in report["incomingUpdates"]]
            relocations = [row for row in ordinary if not row.get("preparationOnly")]
            maintenance.validate_moves(
                root, relocations, exact_alias_targets=report["exactAliasTargets"],
                duplicate_archives=report.get("duplicateArchives", {}),
            )
            maintenance._validate_permissions(
                root, relocations, policy, cfg,
                **({"released_bindings": release_bindings} if release_bindings is not None else {}),
            )
            for row in ordinary:
                if not row.get("preparationOnly"):
                    continue
                source = root / pathlib.PurePosixPath(row["source"])
                if (
                    row["source"] != row["destination"]
                    or source.resolve() != source
                    or root not in source.parents
                    or metadata.content_sha256(source) != row["sha256"]
                ):
                    raise ValueError(f"unsafe or changed in-place preparation source: {row['source']}")
            for source, checksum in report["sourceHashes"].items():
                if metadata.content_sha256(root / pathlib.PurePosixPath(source)) != checksum:
                    raise ValueError(f"frozen source changed before publication: {source}")
            if metadata.load_catalog(metadata.path_for_root(root)) != catalog:
                raise ValueError("catalogue changed before publication")
            for source, modified_ns in report.get("collisionModifiedNs", {}).items():
                if normal_transaction.safe(root, source).stat().st_mtime_ns != modified_ns:
                    raise ValueError(f"collision modification time changed before publication: {source}")
            stage_root = run / "publication"
            journal_path = run / "publication-journal.json"
            stage_catalog = (
                normal_admission.retire_released_catalog(catalog, release_bindings, {
                    move["photoId"]: pathlib.PurePosixPath(move["destination"]).name
                    for move in moves if move.get("photoId") in {row["photoId"] for row in release_bindings}
                })["catalog"]
                if release_bindings is not None else catalog
            )
            published, updated, removed = normal_products.stage(
                root, stage_root, moves, prepared, profile=args.profile,
                photos=photos, cfg=cfg, catalog=stage_catalog, policy=policy,
                archives=report.get("duplicateArchives", {}), junk=report.get("junkDispositions", {}),
                **({"released_source_catalog": catalog} if release_bindings is not None else {}),
            )
            projected = normal_finish.projected(api, root, stage_root, space, cache, moves)
            report["finalComparisonAndFamily"] = normal_finish.family_and_final(
                api, root, stage_root, projected, updated, policy, moves,
            )
            reports_relative = api.cw.storage_root(cfg, "reports", root=root).relative_to(root).as_posix()

            def publish_viewers():
                paths = normal_finish.viewers(
                    api, root, cfg, space, cache, moves, args.policy, profile=args.profile,
                )
                paths.append(str(_ensure_intake_viewer(root, cfg, args.profile, prepared)))
                report["viewerPaths"] = _validate_stable_viewers(paths)
                return report["viewerPaths"]

            archives = report.get("duplicateArchives", {})
            with verification_reads.session(root):
                retained_sources = _retained_duplicate_sources(root, archives)
            journal = normal_transaction.publish(
                root, stage_root,
                sorted(move_sources | set(removed) | set(report.get("duplicateArchives", {}))
                       | set(report.get("junkDispositions", {}))),
                journal=journal_path,
                bindings=report["bindings"], profile=args.profile, run_id=run_id,
                expected_sources={**report["sourceHashes"], **removed, **retained_sources},
                expected_modified_ns=report.get("collisionModifiedNs", {}),
                finalizer=publish_viewers,
                report_directories=[
                    reports_relative + "/library",
                    reports_relative + "/comparisons/pairings",
                    reports_relative + "/_assets",
                ],
                retire_folders=report["emptiedIdentityRetirement"]["folders"],
            )
            for row in published:
                normal_import._refresh_content_digest(cache, root / pathlib.PurePosixPath(row["native"]))
            cache.save()
            if report.get("phaseLog"):
                report["phaseLog"][-1].update(
                    status="complete", durationSeconds=time.perf_counter() - publication_started,
                    timingScope="current validation, staging, transaction, viewers and cache save; excludes receipt and recap",
                )
            receipt = {
                "kind": "normal-rebase-receipt",
                "schemaVersion": 1,
                "status": "applied",
                "runId": run_id,
                "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "root": str(root),
                "profile": args.profile,
                "implementationSHA256": metadata.content_sha256(pathlib.Path(__file__)),
                "bindings": report["bindings"],
                "sourceHashes": report["sourceHashes"],
                "sourceRows": report["sourceRowCount"],
                "plan": report,
                "moves": moves,
                "journal": str(journal),
                "publication": True,
                "publishedNative": published,
                "retiredIdentityFolders": report["emptiedIdentityRetirement"]["folders"],
                "viewerPaths": report["viewerPaths"],
                "preparationReport": str(prepared[0] / "index.html") if prepared else None,
                "recovery": "normal_transaction journal and scoped backup (includes retired identity folders)",
            }
            normal_import._write_receipt(receipt_path, receipt)
            saved_status = "applied"
            normal_recap.publish(receipt_path, apply=True)
            print(f"normal rebase applied: {len(moves)} move(s), {len(report.get('duplicateArchives', {}))} "
                  f"duplicate archive(s), {len(report.get('junkDispositions', {}))} junk disposition(s), "
                  f"{len(rows)} source row(s), {len(receipt['retiredIdentityFolders'])} emptied identity folder(s) retired")
            print(f"receipt: {receipt_path}")
            return 0
        if receipt_path.exists():
            raise ValueError(f"receipt already exists; choose a new --run-id or --receipt: {receipt_path}")
        report["status"] = "preview"
        report["root"] = str(root)
        report["implementationSHA256"] = metadata.content_sha256(pathlib.Path(__file__))
        report["createdAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        normal_import._write_receipt(receipt_path, {
            "kind": "normal-rebase-preview",
            "schemaVersion": 1,
            "status": "preview",
            "runId": run_id,
            "root": str(root),
            "profile": args.profile,
            "implementationSHA256": report["implementationSHA256"],
            "bindings": report["bindings"],
            "plan": report,
        })
        saved_status = "preview"
        normal_recap.publish(receipt_path, apply=True)
        print(
            f"Normal rebase preview ({args.profile.upper()}): {report['sourceRowCount']} source row(s), "
            f"{report['coreCount']} frozen identity core(s), {len(report['moves'])} proposed move(s), "
            f"{len(report.get('duplicateArchives', {}))} proposed duplicate archive(s), "
            f"{len(report.get('junkDispositions', {}))} proposed junk disposition(s), "
            f"{len(report.get('unresolvedDuplicateIds', []))} apply-blocking collision(s), "
            f"{report['heldCount']} held source/candidate row(s)."
        )
        print(f"receipt: {receipt_path}")
        retiring = report.get("emptiedIdentityRetirement", {}).get("folders", [])
        print(f"emptied identity folders to retire inside apply: {len(retiring)}")
        for row in retiring:
            print(f"  RETIRE {row['source']} -> {row['destination']} ({len(row['photos'])} photo(s) leave it)")
        print("preview only; recap/audit reports written; no membership, catalogue, cache or source originals were changed")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        if saved_status is not None:
            print(
                f"normal rebase {saved_status} receipt saved: {receipt_path}; "
                f"recap/audit generation failed: {exc}. "
                "Repair reports with bin\\rebase-recap.cmd RECEIPT --apply; "
                "do not repeat publication or reset the library.",
                file=sys.stderr,
            )
            return 1
        if (
            args.apply and journal_path is not None and pathlib.Path(journal_path).is_file()
            and not receipt_path.exists() and report is not None and policy is not None
        ):
            try:
                normal_import._write_receipt(receipt_path, {
                    "kind": "normal-rebase-receipt",
                    "schemaVersion": 1,
                    "status": "recovery-required",
                    "runId": run_id,
                    "root": str(root),
                    "profile": args.profile,
                    "implementationSHA256": metadata.content_sha256(pathlib.Path(__file__)),
                    "bindings": report["bindings"],
                    "sourceHashes": report["sourceHashes"],
                    "plan": report,
                    "moves": report.get("moves", []),
                    "journal": str(journal_path),
                    "error": str(exc),
                })
            except (OSError, ValueError):
                pass
        print(f"normal rebase stopped safely: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
