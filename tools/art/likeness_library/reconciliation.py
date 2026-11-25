"""Deterministic, read-only routing plan for incoming and reviewed likeness candidates."""
import hashlib
import heapq

import numpy as np

from .audit import audit_person, core_excluded_protection, membership_excluded
from .scoring import nz
from . import protection, rejections


def frozen_identity_cores(
    space,
    catalog,
    *,
    photo_id_fn,
    content_sha256_fn,
    additional_photos=(),
    policy=None,
    require_single_face=False,
):
    """Build immutable person-core vectors using only current, unambiguous metadata."""
    all_photos = list(space.photos) + list(additional_photos)
    id_counts = {}
    for photo in all_photos:
        photo_id = photo_id_fn(photo.name)
        if photo_id:
            id_counts[photo_id] = id_counts.get(photo_id, 0) + 1
    ambiguous_ids = {photo_id for photo_id, count in id_counts.items() if count > 1}

    stale_ids, protected_ids = set(), set()
    for photo in all_photos:
        photo_id = photo_id_fn(photo.name)
        record = catalog.get("photos", {}).get(photo_id)
        if not photo_id or not record or photo_id in ambiguous_ids:
            continue
        if content_sha256_fn(photo.path) != record["contentSha256"]:
            stale_ids.add(photo_id)
        elif record["protected"]:
            protected_ids.add(photo_id)

    records_by_folder = {}
    for person_id, person in catalog.get("people", {}).items():
        records_by_folder.setdefault(person["folder"], []).append((person_id, person))

    cores, diagnostics, effective_anchor_ids = {}, [], set()
    for folder in sorted(space.by_key):
        records = records_by_folder.get(folder, [])
        if len(records) > 1:
            diagnostics.append(f"{folder}: conflicting catalogue records; skipped")
            continue
        photos = space.by_key[folder]
        usable = [
            photo for photo in photos if photo.usable(space.st["minFace"])
            and (
                not require_single_face
                or photo.faces == 1 and getattr(photo, "f2", 0.) <= space.st["multiFace"]
            )
        ]
        if not usable:
            continue
        person_id, person = records[0] if records else (None, None)
        if person and person.get("mergedInto"):
            diagnostics.append(f"{folder}: merged identity history is not an active reference; skipped")
            continue
        if require_single_face and person and person.get("identityStatus") == "provisional":
            diagnostics.append(f"{folder}: provisional container has no reference authority; skipped")
            continue
        anchor_ids = set(person["identityAnchors"]) if person else set()
        photo_ids = [photo_id_fn(photo.name) for photo in usable]
        category = folder.split("/", 1)[0]
        category_policy = (policy or {}).get("categoryPolicies", {}).get(category, {})
        effective_anchor_ids.update(
            (anchor_ids & set(photo_ids)) - stale_ids - ambiguous_ids
        )
        result = audit_person(
            np.asarray([photo.vec for photo in usable]),
            photo_ids,
            anchor_ids=anchor_ids,
            protected_ids=core_excluded_protection(catalog, protected_ids),
            stale_ids=stale_ids,
            ambiguous_ids=ambiguous_ids,
            excluded_ids=membership_excluded(catalog, photo_ids, require_record=category != "Artists"),
            minimum_core=category_policy.get("minimumUsablePhotosForOutlierActions", 3),
            core_minimum=category_policy.get("identityCoreMinimumSimilarity", 0.3),
            seed_floor=category_policy.get("identityCoreMinimumSimilarity", 0.3),
        )
        if not result["core_indices"]:
            diagnostics.append(f"{folder}: no eligible identity core; skipped")
            continue
        core_vector = nz(np.mean(
            [usable[index].vec for index in result["core_indices"]],
            axis=0,
        ))
        cores[folder] = {
            "vector": core_vector,
            "side": "Artists" if folder.startswith("Artists/") else "Prospects",
            "category": folder.split("/", 1)[0],
            "personIds": sorted(rejections.identity_ids(catalog, person_id)) if person else [],
            "identityProtected": bool(person and person.get("protected")),
            "mode": result["mode"],
            "corePhotoIds": [
                photo_ids[index] for index in result["core_indices"]
            ],
            "photoScores": {
                photo.name: result["scores"][index]
                for index, photo in enumerate(usable)
            },
        }

    return cores, protected_ids | ambiguous_ids | effective_anchor_ids, diagnostics


def fragment_proposals(cores, references, policy, *, blocked_ids=()):
    """Describe direct upward identity hypotheses; never authorize or suppress a rival."""
    categories = policy["categoryPolicies"]
    order = {category: index for index, category in enumerate(policy["categoryOrder"])}
    minimum = policy["identityActions"]["autoMergeMinimumIndependentPhotos"]
    blocked_ids = set(blocked_ids)
    counts = {}
    for folder, core in cores.items():
        ids = list(core["corePhotoIds"])
        if len(ids) != len(set(ids)):
            raise ValueError(f"{folder}: repeated frozen core photo ID")
        for photo_id in ids:
            counts[photo_id] = counts.get(photo_id, 0) + 1
    prepared = {}
    for folder, core in sorted(cores.items()):
        core_vector = np.asarray(core["vector"], dtype=float)
        zero_core = core_vector.ndim == 1 and np.isfinite(core_vector).all() and not np.linalg.norm(core_vector)
        if (
            core_vector.ndim != 1 or not np.isfinite(core_vector).all()
            or not zero_core and not np.isclose(np.linalg.norm(core_vector), 1.)
        ):
            raise ValueError(f"{folder}: invalid frozen fragment core vector")
        members = references.get(folder, [])
        by_id = {}
        for row in members:
            photo_id = row["photoId"]
            if photo_id in by_id:
                raise ValueError(f"{folder}: repeated fragment reference {photo_id}")
            vector = np.asarray(row["vector"], dtype=float)
            if (
                vector.ndim != 1 or vector.shape != core_vector.shape
                or not np.isfinite(vector).all()
                or not zero_core and not np.isclose(np.linalg.norm(vector), 1.)
                or not isinstance(row.get("sha256"), str) or not row["sha256"]
            ):
                raise ValueError(f"{folder}: invalid fragment reference {photo_id}")
            by_id[photo_id] = row
        ids = set(core["corePhotoIds"])
        rows = [by_id[photo_id] for photo_id in sorted(ids & by_id.keys())]
        reason = (
            "zero-norm frozen core cannot qualify a fragment" if zero_core else
            "frozen core reference evidence is incomplete" if ids != set(by_id) or not ids else
            "ambiguous reference photo ID" if any(counts[photo_id] != 1 for photo_id in ids) else
            "reference quality or rejection metadata requires review"
            if any(not row["qualityEligible"] or row.get("rejectionMetadataStale") for row in rows) else
            None
        )
        prepared[folder] = (rows, protection._independent(rows, policy), reason)
    different = {
        frozenset(folder.replace("\\", "/") for folder in pair)
        for pair in policy["runtimeSettings"]["different"]
    }
    results = []
    for source, source_core in sorted(cores.items()):
        source_category = source_core.get("category", source.split("/", 1)[0])
        if source_category not in ("Models", "Prospects", "Potentials"):
            continue
        source_rows, source_support, source_reason = prepared[source]
        source_rules = categories[source_category]
        for target, target_core in sorted(cores.items()):
            target_category = target_core.get("category", target.split("/", 1)[0])
            if (
                order[target_category] >= order[source_category]
                or source_core["side"] != target_core["side"]
            ):
                continue
            target_rows, target_support, target_reason = prepared[target]
            target_rules = categories[target_category]
            threshold = max(source_rules["mergeMinimum"], target_rules["mergeMinimum"])
            floor = target_rules.get("galleryAdmissionMinimumSimilarity", target_rules["photoRouteMinimum"])
            score = float(source_core["vector"] @ target_core["vector"])
            reason = (
                source_reason or target_reason
                or ("protected source identity or reference"
                    if source_core.get("identityProtected")
                    or not source_rules["automaticMergeEnabled"]
                    or blocked_ids.intersection(source_core["corePhotoIds"]) else None)
                or ("explicit different-identity evidence"
                    if frozenset((source, target)) in different else None)
                or ("explicit rejected-identity evidence"
                    if target in rejections.excluded_folders(source_rows, cores)
                    or source in rejections.excluded_folders(target_rows, cores) else None)
                or ("shared source/target content is not independent identity evidence"
                    if {row["sha256"] for row in source_rows}
                    & {row["sha256"] for row in target_rows} else None)
                or ("core similarity is below the stricter identity-merge threshold"
                    if score < threshold else None)
                or ("insufficient independent frozen references on one or both sides"
                    if min(len(source_support), len(target_support)) < minimum else None)
            )
            member_evidence = []
            if not reason:
                for row in source_rows:
                    member_score = float(row["vector"] @ target_core["vector"])
                    witnesses = [
                        other for other in target_support
                        if other["photoId"] != row["photoId"]
                        and other["sha256"] != row["sha256"]
                        and float(row["vector"] @ other["vector"]) >= floor
                    ]
                    member_evidence.append({
                        "photoId": row["photoId"], "score": member_score,
                        "witnessPhotoIds": [other["photoId"] for other in witnesses[:minimum]],
                        "independentSupportCount": len(witnesses),
                        "qualified": member_score >= floor and len(witnesses) >= minimum,
                    })
                if not all(row["qualified"] for row in member_evidence):
                    reason = "not every source core member has independent destination support"
            results.append({
                "sourceFolder": source, "targetFolder": target, "score": score,
                "identityMinimum": threshold, "memberMinimum": floor,
                "minimumIndependentReferences": minimum,
                "sourceIndependentPhotoIds": [row["photoId"] for row in source_support],
                "targetIndependentPhotoIds": [row["photoId"] for row in target_support],
                "members": member_evidence,
                "decision": "hold" if reason else "candidate",
                "reason": reason or "direct independently supported fragment hypothesis; not movement authorization",
            })
    for source in sorted({row["sourceFolder"] for row in results}):
        qualified = [row for row in results if row["sourceFolder"] == source and row["decision"] == "candidate"]
        if len(qualified) > 1:
            for row in qualified:
                row["decision"] = "hold"
                row["reason"] = "multiple higher identity hypotheses qualify; no automatic equivalence"
    return {
        "recipe": "conservative-direct-core-v1", "activation": "diagnostic-only",
        "candidateLinks": [row for row in results if row["decision"] == "candidate"],
        "comparisons": results,
        "scope": "frozen direct proposals only; no rival suppression, transitive closure, movement or reference growth",
    }


def _candidate_key(candidate):
    return candidate["photoId"]


def _rank(vector, cores, side):
    ranked = []
    for folder, core in cores.items():
        if core["side"] == side:
            ranked.append((float(vector @ core["vector"]), folder))
    return sorted(ranked, key=lambda item: (-item[0], item[1].casefold()))


def _confident(ranked, threshold, margin):
    if not ranked or ranked[0][0] < threshold:
        return None
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < margin:
        return None
    return ranked[0]


def _average_linkage(candidates, threshold):
    """Return stable average-linkage clusters; ties follow sorted source photo IDs."""
    ordered = sorted(candidates, key=_candidate_key)
    if not ordered:
        return []
    vectors = np.asarray([candidate["vector"] for candidate in ordered])
    similarities = vectors @ vectors.T
    groups = {index: [index] for index in range(len(ordered))}
    versions = {index: 0 for index in groups}
    scores = {
        (left, right): float(similarities[left, right])
        for left in groups for right in groups if left < right
    }
    queue = [
        (-score, left, right, 0, 0)
        for (left, right), score in scores.items() if score >= threshold
    ]
    heapq.heapify(queue)
    while queue:
        negative_score, left, right, left_version, right_version = heapq.heappop(queue)
        if (
            left not in groups or right not in groups
            or versions[left] != left_version or versions[right] != right_version
        ):
            continue
        left_count, right_count = len(groups[left]), len(groups[right])
        groups[left] = sorted(groups[left] + groups.pop(right))
        versions[left] += 1
        for other in groups:
            if other == left:
                continue
            first = tuple(sorted((left, other)))
            second = tuple(sorted((right, other)))
            score = (
                scores[first] * left_count + scores[second] * right_count
            ) / (left_count + right_count)
            scores[first] = score
            if score >= threshold:
                a, b = first
                heapq.heappush(queue, (-score, a, b, versions[a], versions[b]))
    return [[ordered[index] for index in groups[key]] for key in sorted(groups)]


def _centroid_linkage(candidates, threshold):
    """Merge the closest groups while their normalized centroids reach ``threshold`` (IU10 option).

    A photo joins a group by matching the group's centroid, not by the mean of its
    pairwise scores. Ties follow sorted source photo IDs.
    """
    ordered = sorted(candidates, key=_candidate_key)
    if not ordered:
        return []
    groups = {index: [index] for index in range(len(ordered))}
    sums = {index: np.asarray(ordered[index]["vector"], dtype=float) for index in groups}
    while len(groups) > 1:
        keys = sorted(groups)
        centroids = np.asarray([nz(sums[key]) for key in keys])
        similarities = centroids @ centroids.T
        np.fill_diagonal(similarities, -2.)
        first, second = np.unravel_index(int(np.argmax(similarities)), similarities.shape)
        if similarities[first, second] < threshold:
            break
        left, right = sorted((keys[first], keys[second]))
        groups[left] = sorted(groups[left] + groups.pop(right))
        sums[left] = sums[left] + sums.pop(right)
    return [[ordered[index] for index in groups[key]] for key in sorted(groups)]


def _cluster_id(candidates):
    seed = "\n".join(sorted(candidate["photoId"] for candidate in candidates))
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def plan_reconciliation(
    candidates,
    cores,
    *,
    assign=0.40,
    margin=0.10,
    cluster=0.25,
    minimum_cluster=3,
    cast_merge=0.55,
    names_taken=(),
    name_factory,
    policy=None,
    admission_context=None,
):
    """Plan assignments from one frozen set of identity cores and candidate vectors.

    Candidate records require photoId, sourceFolder, sourceBucket, side and vector.
    Core records map folder names to vector and side fields. Results are suggestions
    only; this function never changes the library or catalogue.
    """
    if minimum_cluster < (1 if policy is not None else 2):
        raise ValueError("minimum_cluster is below the supported minimum")
    if not 0 <= assign <= 1 or not 0 <= margin <= 2 or not -1 <= cluster <= 1:
        raise ValueError("invalid reconciliation threshold")
    if not -1 <= cast_merge <= 1:
        raise ValueError("invalid cast_merge threshold")

    normalized_cores = {}
    dimensions = set()
    for folder, core in cores.items():
        vector = np.asarray(core["vector"], dtype=float)
        if vector.ndim != 1 or not vector.size or not np.isfinite(vector).all() or np.linalg.norm(vector) == 0:
            raise ValueError(f"{folder}: invalid frozen identity-core vector")
        if core.get("side") not in {"Prospects", "Artists"}:
            raise ValueError(f"{folder}: side must be Prospects or Artists")
        dimensions.add(vector.size)
        normalized_cores[folder] = {**core, "vector": nz(vector)}
    if len(dimensions) > 1:
        raise ValueError("frozen identity cores have inconsistent vector dimensions")
    cores = normalized_cores

    prepared, held = [], []
    by_id = {}
    for candidate in candidates:
        photo_id = candidate.get("photoId")
        if not photo_id:
            held.append({
                "photoId": None,
                "sourceFolder": candidate.get("sourceFolder"),
                "sourceBucket": candidate.get("sourceBucket"),
                "reason": "missing stable photo ID",
            })
            continue
        by_id.setdefault(photo_id, []).append(candidate)
    ambiguous_ids = {photo_id for photo_id, rows in by_id.items() if len(rows) > 1}

    for photo_id in sorted(by_id):
        rows = by_id[photo_id]
        if photo_id in ambiguous_ids:
            for candidate in rows:
                held.append({
                    "photoId": photo_id,
                    "sourceFolder": candidate.get("sourceFolder"),
                    "sourceBucket": candidate.get("sourceBucket"),
                    "reason": "duplicate stable photo ID; remains staged",
                })
            continue
        candidate = dict(rows[0])
        red_release = bool(
            admission_context is not None and admission_context.get("redRelease")
            and candidate.get("redRelease")
        )
        if admission_context is not None and candidate.get("explicitReviewPlacement") and not red_release:
            held.append({
                "photoId": photo_id, "sourceFolder": candidate["sourceFolder"],
                "sourceBucket": candidate["sourceBucket"], "preserveStaged": True,
                "reason": "explicit Review placement; remains staged",
            })
            continue
        if candidate.get("rejectionMetadataStale"):
            held.append({
                "photoId": photo_id, "sourceFolder": candidate.get("sourceFolder"),
                "sourceBucket": candidate.get("sourceBucket"),
                "reason": "rejected-identity metadata is stale; review changed photo bytes",
                "preserveStaged": True,
            })
            continue
        if candidate.get("identityProtected") and not red_release:
            held.append({
                "photoId": photo_id,
                "sourceFolder": candidate.get("sourceFolder"),
                "sourceBucket": candidate.get("sourceBucket"),
                "reason": "protected identity; photo remains in its current identity",
            })
            continue
        if candidate.get("workflowSelected") or (candidate.get("protected") and not red_release):
            held.append({
                "photoId": photo_id,
                "sourceFolder": candidate.get("sourceFolder"),
                "sourceBucket": candidate.get("sourceBucket"),
                "reason": "workflow-selected photo; remains staged"
                if candidate.get("workflowSelected")
                else "protected photo; remains staged",
            })
            continue
        gallery_outlier = (
            policy is not None and candidate.get("sourceBucket") == "Gallery"
            and candidate.get("outlierCandidate")
            and candidate.get("sourceFolder") in cores
        )
        rebase_member = (
            admission_context is not None and candidate.get("rebaseCandidate")
            and candidate.get("sourceBucket") == "Gallery"
            and candidate.get("sourceFolder", "").split("/", 1)[0] in ("Models", "Prospects", "Potentials")
        )
        if (candidate.get("sourceBucket") not in {"Pool", "Review"}
                and not gallery_outlier and not rebase_member
                and not (red_release and candidate.get("sourceBucket") == "Gallery")):
            raise ValueError(f"{photo_id}: sourceBucket must be Pool, Review or a validated Gallery outlier")
        if candidate.get("side") not in {"Prospects", "Artists"}:
            raise ValueError(f"{photo_id}: side must be Prospects or Artists")
        vector = np.asarray(candidate.get("vector"), dtype=float)
        if vector.ndim != 1 or not vector.size or not np.isfinite(vector).all() or np.linalg.norm(vector) == 0:
            held.append({
                "photoId": photo_id,
                "sourceFolder": candidate.get("sourceFolder"),
                "sourceBucket": candidate.get("sourceBucket"),
                "reason": "missing or invalid face vector",
            })
            continue
        if dimensions and vector.size not in dimensions:
            raise ValueError(f"{photo_id}: vector dimensions do not match the frozen identity cores")
        candidate["vector"] = nz(vector)
        prepared.append(candidate)

    if policy is not None:
        from .planner import plan_candidates

        linkage = (
            _centroid_linkage if policy["identityActions"].get("formationLinkage", "average") == "centroid"
            else _average_linkage
        )
        result = plan_candidates(
            prepared, cores, policy, name_factory, names_taken, linkage,
            admission_context=admission_context,
        )
        result["held"].extend(held)
        result["assignments"].sort(key=lambda row: row["photoId"])
        result["held"].sort(key=lambda row: (row.get("photoId") or "", row.get("sourceFolder") or ""))
        result["clusters"].sort(key=lambda row: row["clusterId"])
        ids = [
            row["photoId"] for row in result["assignments"] + result["held"]
            if row["photoId"] and row["photoId"] not in ambiguous_ids
        ]
        if len(ids) != len(set(ids)):
            raise AssertionError("a candidate was planned more than once")
        if len(result["assignments"]) + len(result["held"]) != len(candidates):
            raise AssertionError("reconciliation did not account for every candidate")
        result.update({
            "candidateCount": len(candidates), "assignedCount": len(result["assignments"]),
            "heldCount": len(result["held"]), "coreFolders": len(cores),
            "authorizationRequired": policy["status"] != "approved",
            "policyVersion": policy["version"],
        })
        return result

    from .legacy_reconciliation import plan_legacy
    if any(row.get("rejectedPersonIds") for row in prepared):
        raise ValueError("persistent identity rejections require the policy-driven planner")
    return plan_legacy(
        prepared,
        cores,
        held,
        candidates,
        assign=assign,
        margin=margin,
        cluster=cluster,
        minimum_cluster=minimum_cluster,
        cast_merge=cast_merge,
        names_taken=names_taken,
        name_factory=name_factory,
    )
