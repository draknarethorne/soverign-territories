"""Frozen, leave-one-out protection acquisition; never changes core eligibility."""
import copy
import hashlib
import json
import pathlib
from collections import Counter

import numpy as np

from . import metadata, rejections
from .scoring import nz


MODEL = "YuNet-2023mar/SFace-2021dec;space-centered-v1"


def describe(record):
    """Describe recorded decisions without asserting fresh confidence."""
    if not record:
        return "No recorded protection decision"
    if record.get("automaticProtectionOverride") == "disabled":
        return "Manual opt-out: auto-protection disabled until explicitly protected again"
    provenance = record.get("protectionProvenance")
    if provenance and record.get("protected"):
        return (
            f"Recorded automatic protection · {provenance['policyVersion']} · "
            f"{provenance['independentSupport']} independent observations · {provenance['reason']}"
        )
    return "Explicitly protected" if record.get("protected") else "Unprotected; automatic evidence gates apply"


def _independent(rows, policy):
    maximum = policy["identityActions"]["independentEvidenceMaximumSimilarity"]
    chosen, hashes = [], set()
    for row in sorted(rows, key=lambda item: item["photoId"]):
        if row["sha256"] in hashes:
            continue
        if all(float(row["vector"] @ other["vector"]) <= maximum for other in chosen):
            chosen.append(row)
            hashes.add(row["sha256"])
    return chosen


def plan_protection(space, cores, catalog, policy, *, root, moving_photo_ids=(),
                    moving_folders=(), selected_ids=(), additional_photos=()):
    """Return metadata patches and diagnostic holds from one immutable evidence set.

    Missing catalogue photo rows may be created only from fresh measured bytes.
    Existing stale rows are held, never silently rebound to a new source.
    """
    settings = policy["protection"].get("automatic", {})
    if not settings.get("enabled"):
        return [], []
    root = pathlib.Path(root).resolve()
    photos = list(space.photos) + list(additional_photos)
    counts = Counter(metadata.photo_id_from_name(photo.name) for photo in photos)
    moving_ids, moving_folders = set(moving_photo_ids), set(moving_folders)
    maximum = policy["identityActions"]["independentEvidenceMaximumSimilarity"]
    valid, evidence, actions = {}, [], []
    for photo in photos:
        photo_id = metadata.photo_id_from_name(photo.name)
        reason = None
        record = catalog["photos"].get(photo_id)
        digest = None
        if not photo_id or counts[photo_id] != 1:
            reason = "missing or ambiguous stable photo ID"
        elif photo.path.parent.name.casefold() != "gallery":
            reason = "Review and non-Gallery photos cannot acquire protection"
        elif photo_id in moving_ids or photo.key in moving_folders:
            reason = "membership changes require fresh reconciliation evidence"
        elif (
            not photo.usable(space.st["minFace"]) or getattr(photo, "faces", 0) != 1
            or getattr(photo, "f2", 1) > space.st.get("multiFace", policy["runtimeSettings"]["multiFace"])
        ):
            reason = "photo is not an unambiguous usable single-face observation"
        elif photo.vec is None or not np.isfinite(photo.vec).all() or not np.linalg.norm(photo.vec):
            reason = "missing or invalid measured identity vector"
        else:
            digest = metadata.content_sha256(photo.path)
            if digest != getattr(photo, "sha", None) or (record and digest != record["contentSha256"]):
                reason = "stale source hash or measurement"
        if reason:
            evidence.append({"photoId": photo_id, "folder": photo.key, "decision": "hold", "reason": reason})
            continue
        state = rejections.candidate_state(catalog, photo_id, digest)
        if state.get("rejectionMetadataStale") or state.get("rejectedPersonIds"):
            evidence.append({
                "photoId": photo_id, "folder": photo.key, "decision": "hold",
                "reason": "persistent rejected-identity evidence requires manual review",
            })
            continue
        valid[photo_id] = {
            "photoId": photo_id, "vector": nz(photo.vec), "sha256": digest,
            "path": photo.path.resolve().relative_to(root).as_posix(), "folder": photo.key,
        }

    references = {}
    for folder, core in cores.items():
        if folder in moving_folders:
            continue
        rows = [
            valid[photo_id] for photo_id in core["corePhotoIds"]
            if photo_id in valid and valid[photo_id]["folder"] == folder
        ]
        references[folder] = _independent(rows, policy)
    # Bind the complete frozen comparison inventory, including rival references.
    sources = [
        {key: row[key] for key in ("photoId", "path", "sha256")}
        for _, row in sorted(valid.items())
    ]
    fingerprint = {
        "sources": sources,
        "references": {folder: [row["photoId"] for row in rows] for folder, rows in sorted(references.items())},
        "vectors": {photo_id: row["vector"].tolist() for photo_id, row in sorted(valid.items())},
        "recipe": settings["recipeVersion"], "policy": policy["version"], "model": MODEL,
    }
    core_version = hashlib.sha256(json.dumps(fingerprint, sort_keys=True).encode()).hexdigest()
    people_by_folder = {}
    for person_id, person in catalog["people"].items():
        if not person.get("mergedInto"):
            people_by_folder.setdefault(person["folder"], []).append((person_id, person))
    for folder, people in sorted(people_by_folder.items()):
        if len(people) != 1:
            evidence.append({"folder": folder, "decision": "hold", "reason": "ambiguous identity ownership"})
            continue
        person_id, person = people[0]
        if folder in moving_folders or folder not in cores:
            evidence.append({"personId": person_id, "decision": "hold", "reason": "missing unchanged frozen identity core"})
            continue
        if person.get("automaticProtectionOverride") == "disabled":
            evidence.append({"personId": person_id, "decision": "hold", "reason": "persistent manual identity opt-out"})
            continue
        qualified = []
        for row in sorted((row for row in valid.values() if row["folder"] == folder), key=lambda row: row["photoId"]):
            photo_id = row["photoId"]
            record = catalog["photos"].get(photo_id, {})
            refs = [
                other for other in references.get(folder, [])
                if other["photoId"] != photo_id and other["sha256"] != row["sha256"]
                and float(row["vector"] @ other["vector"]) <= maximum
            ]
            support = len(refs)
            score = float(row["vector"] @ nz(np.mean([other["vector"] for other in refs], axis=0))) if refs else None
            rivals = [
                float(row["vector"] @ nz(np.mean([other["vector"] for other in rows], axis=0)))
                for other_folder, rows in references.items()
                if other_folder != folder and rows and cores[other_folder]["side"] == cores[folder]["side"]
            ]
            margin = score - max(rivals, default=-1.0) if score is not None else None
            reason = (
                "persistent manual photo opt-out" if record.get("automaticProtectionOverride") == "disabled" else
                "insufficient independent leave-one-out core support" if support < settings["minimumIndependentReferences"] else
                "own-core confidence below protection threshold" if score < settings["minimumOwnCoreSimilarity"] else
                "ambiguous rival identity margin" if margin < settings["minimumRivalMargin"] else
                None
            )
            diagnostic = {
                "personId": person_id, "photoId": photo_id, "score": score,
                "rivalMargin": margin, "independentSupport": support,
                "decision": "hold" if reason else "qualified",
                "reason": reason or "independent Gallery leave-one-out confidence qualifies",
            }
            evidence.append(diagnostic)
            if not reason:
                qualified.append((row, diagnostic))
        established_support = len(_independent([row for row, _ in qualified], policy))
        established = established_support >= settings["minimumEstablishedPhotos"]
        provenance = {
            "recipeVersion": settings["recipeVersion"], "policyVersion": policy["version"],
            "model": MODEL, "coreVersion": core_version,
            "frozenCorePhotoIds": list(cores[folder]["corePhotoIds"]),
        }
        if established and not person.get("protected"):
            reason = "established identity has independently qualifying Gallery observations"
            after = copy.deepcopy(person)
            after.update({
                "protected": True,
                "protectionProvenance": {
                    **provenance, "independentSupport": established_support, "reason": reason,
                },
            })
            actions.append({"personId": person_id, "before": copy.deepcopy(person), "after": after, "reason": reason})
        protected_identity = person.get("protected") or established or policy["categoryPolicies"][cores[folder]["category"]]["identityProtectedByDefault"]
        if not protected_identity:
            evidence.append({
                "personId": person_id, "decision": "hold", "independentSupport": established_support,
                "reason": "identity is not protected or independently established",
            })
            continue
        for row, diagnostic in qualified:
            photo_id = row["photoId"]
            before = catalog["photos"].get(photo_id)
            if before and before.get("protected"):
                continue
            after = copy.deepcopy(before) if before else {"contentSha256": row["sha256"]}
            after.update({
                "protected": True,
                "protectionProvenance": {
                    **provenance, "contentSha256": row["sha256"], "score": diagnostic["score"],
                    "rivalMargin": diagnostic["rivalMargin"],
                    "independentSupport": diagnostic["independentSupport"], "reason": diagnostic["reason"],
                },
            })
            actions.append({"photoId": photo_id, "before": copy.deepcopy(before), "after": after, "reason": diagnostic["reason"]})
    if actions:
        # The transaction binds the shared inventory once, not once per locked photo.
        actions[0]["sourceChecks"] = [
            {"source": row["path"], "sha256": row["sha256"]} for row in sources
        ]
    return actions, evidence
