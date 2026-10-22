"""Deterministic, read-only routing plan for incoming and reviewed likeness candidates."""
import hashlib
import heapq

import numpy as np

from .audit import audit_person
from .policy import classify_category, evaluate_photo_route
from .scoring import nz


def frozen_identity_cores(
    space,
    catalog,
    *,
    photo_id_fn,
    content_sha256_fn,
    additional_photos=(),
    policy=None,
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
    for person in catalog.get("people", {}).values():
        records_by_folder.setdefault(person["folder"], []).append(person)

    cores, diagnostics, effective_anchor_ids = {}, [], set()
    for folder in sorted(space.by_key):
        records = records_by_folder.get(folder, [])
        if len(records) > 1:
            diagnostics.append(f"{folder}: conflicting catalogue records; skipped")
            continue
        photos = space.by_key[folder]
        usable = [photo for photo in photos if photo.usable(space.st["minFace"])]
        if not usable:
            continue
        person = records[0] if records else None
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
            protected_ids=protected_ids,
            stale_ids=stale_ids,
            ambiguous_ids=ambiguous_ids,
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
            "identityProtected": bool(person and person.get("protected")),
            "mode": result["mode"],
            "photoScores": {
                photo.name: result["scores"][index]
                for index, photo in enumerate(usable)
            },
        }

    return cores, protected_ids | ambiguous_ids | effective_anchor_ids, diagnostics


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
):
    """Plan assignments from one frozen set of identity cores and candidate vectors.

    Candidate records require photoId, sourceFolder, sourceBucket, side and vector.
    Core records map folder names to vector and side fields. Results are suggestions
    only; this function never changes the library or catalogue.
    """
    if minimum_cluster < 2:
        raise ValueError("minimum_cluster must be at least 2")
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
        if candidate.get("identityProtected"):
            held.append({
                "photoId": photo_id,
                "sourceFolder": candidate.get("sourceFolder"),
                "sourceBucket": candidate.get("sourceBucket"),
                "reason": "protected identity; photo remains in its current identity",
            })
            continue
        if candidate.get("workflowSelected") or candidate.get("protected"):
            held.append({
                "photoId": photo_id,
                "sourceFolder": candidate.get("sourceFolder"),
                "sourceBucket": candidate.get("sourceBucket"),
                "reason": "workflow-selected photo; remains staged"
                if candidate.get("workflowSelected")
                else "protected photo; remains staged",
            })
            continue
        if candidate.get("sourceBucket") not in {"Pool", "Review"}:
            raise ValueError(f"{photo_id}: sourceBucket must be Pool or Review")
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

    assignments = []
    unresolved = []
    for candidate in prepared:
        ranked = _rank(candidate["vector"], cores, candidate["side"])
        if (
            policy is not None
            and candidate.get("side") != "Artists"
            and ranked
        ):
            score, folder = ranked[0]
            lead = score - ranked[1][0] if len(ranked) > 1 else 2.0
            category = cores[folder].get("category", folder.split("/", 1)[0])
            decision = evaluate_photo_route(
                category,
                score=score,
                margin=lead,
                identity_protected=bool(cores[folder].get("identityProtected")),
                policy=policy,
            )
            if decision["decision"] == "auto-route":
                assignments.append({
                    "photoId": candidate["photoId"],
                    "sourceFolder": candidate["sourceFolder"],
                    "sourceBucket": candidate["sourceBucket"],
                    "destination": folder,
                    "destinationType": "existing",
                    "score": round(score, 4),
                    "reason": decision["reason"],
                })
            elif (
                category in {"Angels", "Sisters"}
                and candidate.get("sourceBucket") == "Pool"
            ):
                unresolved.append(candidate)
            elif decision["decision"] != "no-match":
                held.append({
                    "photoId": candidate["photoId"],
                    "sourceFolder": candidate["sourceFolder"],
                    "sourceBucket": candidate["sourceBucket"],
                    "reason": decision["reason"],
                    "bestMatch": folder,
                    "bestScore": round(score, 4),
                })
            else:
                unresolved.append(candidate)
        else:
            match = _confident(ranked, assign, margin)
            if match:
                score, folder = match
                assignments.append({
                    "photoId": candidate["photoId"],
                    "sourceFolder": candidate["sourceFolder"],
                    "sourceBucket": candidate["sourceBucket"],
                    "destination": folder,
                    "destinationType": "existing",
                    "score": round(score, 4),
                    "reason": "confident match against frozen identity core",
                })
            else:
                unresolved.append(candidate)

    provisional_cores = {}
    provisional_rows = []
    pending = []
    groups_by_side = {}
    for candidate in unresolved:
        groups_by_side.setdefault(candidate["side"], []).append(candidate)

    taken = {name.casefold() for name in names_taken}
    for side in sorted(groups_by_side):
        for group in _average_linkage(groups_by_side[side], cluster):
            if len(group) < minimum_cluster:
                pending.extend(group)
                continue
            cluster_vector = nz(np.mean([candidate["vector"] for candidate in group], axis=0))
            ranked = _rank(cluster_vector, cores, side)
            if policy is not None:
                cast_rows = [
                    row for row in ranked
                    if row[1].startswith(("Angels/", "Sisters/"))
                ]
                cast_score = cast_rows[0][0] if cast_rows else None
                proposed = classify_category(
                    len(group),
                    cast_score,
                    policy,
                    best_cast_folder=cast_rows[0][1] if cast_rows else None,
                    second_cast_folder=cast_rows[1][1] if len(cast_rows) > 1 else None,
                    cast_margin=(
                        cast_rows[0][0] - cast_rows[1][0]
                        if len(cast_rows) > 1 else None
                    ),
                )
                if proposed["category"] == "Review":
                    for candidate in group:
                        held.append({
                            "photoId": candidate["photoId"],
                            "sourceFolder": candidate["sourceFolder"],
                            "sourceBucket": candidate["sourceBucket"],
                            "reason": proposed["reason"],
                            "bestScore": round(cast_score, 4) if cast_score is not None else None,
                            "bestMatch": cast_rows[0][1] if cast_rows else None,
                            "reviewDestination": proposed["reviewDestination"],
                            "reviewAlternatives": proposed["reviewAlternatives"],
                            "clusterId": _cluster_id(group),
                        })
                    continue
                non_cast_ranked = [
                    row for row in ranked
                    if not row[1].startswith(("Angels/", "Sisters/"))
                ]
                if non_cast_ranked and non_cast_ranked[0][0] >= policy["photoRouting"]["reviewMinimum"]:
                    score, folder = non_cast_ranked[0]
                    lead = score - non_cast_ranked[1][0] if len(non_cast_ranked) > 1 else 2.0
                    category = cores[folder].get("category", folder.split("/", 1)[0])
                    decision = evaluate_photo_route(
                        category,
                        score=score,
                        margin=lead,
                        identity_protected=bool(cores[folder].get("identityProtected")),
                        policy=policy,
                    )
                    if decision["decision"] == "auto-route":
                        destination = folder
                        destination_type = "existing"
                        reason = decision["reason"]
                        provisional_rows.append({
                            "clusterId": _cluster_id(group),
                            "destination": destination,
                            "destinationType": destination_type,
                            "photoIds": sorted(candidate["photoId"] for candidate in group),
                            "score": round(score, 4),
                            "reason": reason,
                        })
                        for candidate in group:
                            assignments.append({
                                "photoId": candidate["photoId"],
                                "sourceFolder": candidate["sourceFolder"],
                                "sourceBucket": candidate["sourceBucket"],
                                "destination": destination,
                                "destinationType": destination_type,
                                "clusterId": _cluster_id(group),
                                "score": round(score, 4),
                                "reason": reason,
                            })
                    else:
                        for candidate in group:
                            held.append({
                                "photoId": candidate["photoId"],
                                "sourceFolder": candidate["sourceFolder"],
                                "sourceBucket": candidate["sourceBucket"],
                                "reason": decision["reason"],
                                "bestMatch": folder,
                                "bestScore": round(score, 4),
                            })
                    continue
                if proposed["category"] not in {"Potentials", "Prospects"}:
                    seed = _cluster_id(group)
                    name = name_factory(seed, taken)
                    if not name or name.casefold() in taken:
                        raise ValueError(f"name factory returned a missing or duplicate name for cluster {seed}")
                    taken.add(name.casefold())
                    destination = f"{proposed['category']}/{name}"
                    destination_type = "provisional"
                    reason = f"new distinct-person cluster routed to {proposed['category']}"
                    provisional_cores[destination] = {
                        "vector": cluster_vector,
                        "side": side,
                        "category": proposed["category"],
                    }
                    cluster_id = _cluster_id(group)
                    provisional_rows.append({
                        "clusterId": cluster_id,
                        "destination": destination,
                        "destinationType": destination_type,
                        "photoIds": sorted(candidate["photoId"] for candidate in group),
                        "score": round(cast_score, 4),
                        "reason": reason,
                    })
                    for candidate in group:
                        assignments.append({
                            "photoId": candidate["photoId"],
                            "sourceFolder": candidate["sourceFolder"],
                            "sourceBucket": candidate["sourceBucket"],
                            "destination": destination,
                            "destinationType": destination_type,
                            "clusterId": cluster_id,
                            "score": round(cast_score, 4),
                            "reason": reason,
                        })
                    continue
                root = proposed["category"]
                seed = _cluster_id(group)
                name = name_factory(seed, taken)
                if not name or name.casefold() in taken:
                    raise ValueError(f"name factory returned a missing or duplicate name for cluster {seed}")
                taken.add(name.casefold())
                destination = f"{root}/{name}"
                destination_type = "provisional"
                reason = f"new provisional cluster of {len(group)} candidates"
                provisional_cores[destination] = {
                    "vector": cluster_vector,
                    "side": side,
                    "category": root,
                }
                cluster_id = _cluster_id(group)
                provisional_rows.append({
                    "clusterId": cluster_id,
                    "destination": destination,
                    "destinationType": destination_type,
                    "photoIds": sorted(candidate["photoId"] for candidate in group),
                    "score": None,
                    "reason": reason,
                })
                for candidate in group:
                    assignments.append({
                        "photoId": candidate["photoId"],
                        "sourceFolder": candidate["sourceFolder"],
                        "sourceBucket": candidate["sourceBucket"],
                        "destination": destination,
                        "destinationType": destination_type,
                        "clusterId": cluster_id,
                        "score": None,
                        "reason": reason,
                    })
                continue
            cast_match = _confident(ranked, cast_merge, margin)
            if cast_match and not (
                cast_match[1].startswith("Angels/")
                or cast_match[1].startswith("Sisters/")
            ):
                cast_match = None
            ordinary_match = _confident(ranked, assign, margin)
            if cast_match:
                score, destination = cast_match
                destination_type = "existing"
                reason = "candidate cluster confidently matches a cast identity core"
            elif ordinary_match:
                score, destination = ordinary_match
                if destination.startswith("Angels/") or destination.startswith("Sisters/"):
                    pending.extend(group)
                    continue
                destination_type = "existing"
                reason = "candidate cluster confidently matches an existing identity core"
            elif ranked and ranked[0][0] >= assign:
                pending.extend(group)
                continue
            else:
                seed = _cluster_id(group)
                name = name_factory(seed, taken)
                if not name or name.casefold() in taken:
                    raise ValueError(f"name factory returned a missing or duplicate name for cluster {seed}")
                taken.add(name.casefold())
                root = "Prospects" if len(group) >= 5 else "Potentials"
                destination = f"{root}/{name}"
                destination_type = "provisional"
                score = None
                reason = f"new provisional cluster of {len(group)} candidates"
                provisional_cores[destination] = {"vector": cluster_vector, "side": side}
            cluster_id = _cluster_id(group)
            provisional_rows.append({
                "clusterId": cluster_id,
                "destination": destination,
                "destinationType": destination_type,
                "photoIds": sorted(candidate["photoId"] for candidate in group),
                "score": round(score, 4) if score is not None else None,
                "reason": reason,
            })
            for candidate in group:
                assignments.append({
                    "photoId": candidate["photoId"],
                    "sourceFolder": candidate["sourceFolder"],
                    "sourceBucket": candidate["sourceBucket"],
                    "destination": destination,
                    "destinationType": destination_type,
                    "clusterId": cluster_id,
                    "score": round(score, 4) if score is not None else None,
                    "reason": reason,
                })

    available_cores = dict(cores)
    available_cores.update(provisional_cores)
    while pending:
        newly_assigned = []
        remaining = []
        for candidate in pending:
            ranked = _rank(candidate["vector"], available_cores, candidate["side"])
            match = _confident(ranked, assign, margin)
            if policy is not None and candidate.get("side") != "Artists":
                review_match = next(
                    (
                        row for row in ranked
                        if row[0] >= policy["photoRouting"]["reviewMinimum"]
                    ),
                    None,
                )
                if review_match:
                    score, folder = review_match
                    lead = score - ranked[1][0] if len(ranked) > 1 and ranked[0][1] == folder else 2.0
                    category = available_cores[folder].get("category", folder.split("/", 1)[0])
                    decision = evaluate_photo_route(
                        category,
                        score=score,
                        margin=lead,
                        identity_protected=bool(available_cores[folder].get("identityProtected")),
                        policy=policy,
                    )
                    if decision["decision"] == "auto-route":
                        match = review_match
                    else:
                        cast_review = None
                        if category in {"Angels", "Sisters"}:
                            cast_ranked = [
                                row for row in ranked
                                if row[1].startswith(("Angels/", "Sisters/"))
                            ]
                            cast_review = classify_category(
                                1, score, policy, best_cast_folder=folder,
                                second_cast_folder=cast_ranked[1][1] if len(cast_ranked) > 1 else None,
                                cast_margin=(
                                    score - cast_ranked[1][0] if len(cast_ranked) > 1 else None
                                ),
                            )
                        held.append({
                            "photoId": candidate["photoId"],
                            "sourceFolder": candidate["sourceFolder"],
                            "sourceBucket": candidate["sourceBucket"],
                            "reason": decision["reason"],
                            "bestMatch": folder,
                            "bestScore": round(score, 4),
                            "reviewDestination": (
                                cast_review.get("reviewDestination") if cast_review else None
                            ),
                        })
                        continue
            if match:
                score, folder = match
                is_provisional = folder in provisional_cores
                newly_assigned.append({
                    "photoId": candidate["photoId"],
                    "sourceFolder": candidate["sourceFolder"],
                    "sourceBucket": candidate["sourceBucket"],
                    "destination": folder,
                    "destinationType": "provisional" if is_provisional else "existing",
                    "score": round(score, 4),
                    "reason": "confident match against frozen provisional cluster"
                    if is_provisional else "confident match against frozen identity core",
                })
            else:
                remaining.append(candidate)
        if not newly_assigned:
            pending = remaining
            break
        assignments.extend(newly_assigned)
        pending = remaining

    assignment_ids = [row["photoId"] for row in assignments]
    if len(assignment_ids) != len(set(assignment_ids)):
        raise AssertionError("a candidate was assigned more than once")
    for candidate in pending:
        ranked = _rank(candidate["vector"], available_cores, candidate["side"])
        match = _confident(ranked, assign, margin)
        reason = "ambiguous destination; remains staged" if ranked and ranked[0][0] >= assign else (
            "no destination or qualifying cluster; remains staged"
        )
        if match:
            reason = "unstable destination; remains staged"
        held.append({
            "photoId": candidate["photoId"],
            "sourceFolder": candidate["sourceFolder"],
            "sourceBucket": candidate["sourceBucket"],
            "reason": reason,
            "bestMatch": ranked[0][1] if ranked else None,
            "bestScore": round(ranked[0][0], 4) if ranked else None,
        })

    assignments.sort(key=lambda row: row["photoId"])
    held.sort(key=lambda row: (row.get("photoId") or "", row.get("sourceFolder") or ""))
    provisional_rows.sort(key=lambda row: row["clusterId"])
    return {
        "assignments": assignments,
        "held": held,
        "clusters": provisional_rows,
        "candidateCount": len(candidates),
        "assignedCount": len(assignments),
        "heldCount": len(held),
        "coreFolders": len(cores),
    }
