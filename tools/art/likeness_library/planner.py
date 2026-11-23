"""Policy-driven proposals, independent of filesystem execution authorization."""
import hashlib

import numpy as np

from .audit import audit_person
from .policy import classify_category, evaluate_photo_route, formation_minimums
from .rejections import excluded_folders
from .scoring import nz

SINGLE_PHOTO_LABEL = "single photo – not yet scoreable"
CAST_CATEGORIES = ("Sisters", "Angels")


def _group_id(rows):
    return hashlib.sha256("\n".join(sorted(row["photoId"] for row in rows)).encode()).hexdigest()[:16]


def _leave_one_out(rows):
    """Score each member against the normalized mean of the other members."""
    vectors = np.asarray([row["vector"] for row in rows], dtype=float)
    total = vectors.sum(axis=0)
    scores = []
    for vector in vectors:
        other = total - vector
        norm = np.linalg.norm(other)
        scores.append(float(np.clip(vector @ other / norm, -1., 1.)) if norm else -1.)
    return scores


def _band_trim(rows, minimum):
    """Drop the weakest member until every leave-one-out score reaches ``minimum``."""
    kept = sorted(rows, key=lambda row: row["photoId"])
    removed = []
    while len(kept) > 1:
        scores = _leave_one_out(kept)
        worst = min(range(len(kept)), key=lambda index: (scores[index], kept[index]["photoId"]))
        if scores[worst] >= minimum:
            return kept, removed, dict(zip((row["photoId"] for row in kept), scores))
        removed.append(kept.pop(worst))
    return kept, removed, {}


def _rank(vector, cores, side, excluded=()):
    return sorted(
        (
            (float(vector @ core["vector"]), folder)
            for folder, core in cores.items()
            if core["side"] == side and folder not in excluded
        ),
        key=lambda row: (-row[0], row[1].casefold()),
    )


def _core(rows, minimum):
    vectors = np.asarray([row["vector"] for row in rows])
    audit = audit_person(
        vectors, [row["photoId"] for row in rows],
        minimum_core=1, seed_floor=minimum, core_minimum=minimum,
    )
    return audit["core_vector"], set(audit["core_indices"])


def plan_candidates(candidates, cores, policy, name_factory, names_taken, cluster_fn, *, admission_context=None):
    """Keep grouping, matching, classification and proposed action states separate."""
    held, assignments, clusters = [], [], []
    routing = policy["photoRouting"]
    categories = policy["categoryPolicies"]
    cast = {
        folder: core for folder, core in cores.items()
        if categories[core.get("category", folder.split("/", 1)[0])]["identityProtectedByDefault"]
    }
    unresolved = []

    def excluded(rows, candidates_cores):
        folders = excluded_folders(rows, candidates_cores)
        if admission_context is not None and admission_context.get("redRelease"):
            folders.update(
                row["sourceFolder"] for row in rows
                if row.get("redRelease") and row.get("detachedOutlier")
            )
        return folders

    def classify(group):
        ranked = _rank(
            group["vector"], cast, group["side"], excluded(group["rows"], cast),
        )
        return classify_category(
            len(group["rows"]), ranked[0][0] if ranked else None, policy,
            best_cast_folder=ranked[0][1] if ranked else None,
            second_cast_folder=ranked[1][1] if len(ranked) > 1 else None,
            cast_margin=ranked[0][0] - ranked[1][0] if len(ranked) > 1 else 2.,
        )

    def evidence(rows, ranked, reason, **extra):
        group_id = _group_id(rows)
        return [
            {
                "photoId": row["photoId"], "sourceFolder": row["sourceFolder"],
                "sourceBucket": row["sourceBucket"], "clusterId": group_id,
                "bestMatch": ranked[0][1] if ranked else None,
                "bestScore": round(ranked[0][0], 4) if ranked else None,
                "excludedIdentityIds": row.get("rejectedPersonIds", []),
                **({"routingEvidence": {
                    "winner": ranked[0][1], "score": ranked[0][0],
                    "margin": ranked[0][0] - ranked[1][0] if len(ranked) > 1 else 2.,
                }} if ranked else {}),
                "reason": reason, **extra,
                **({"faceQuality": row["faceQuality"]} if row.get("faceQuality") else {}),
                **({"referenceEligible": False} if row.get("referenceQualityEligible") is False else {}),
            }
            for row in rows
        ]

    for row in candidates:
        if admission_context is not None:
            from .normal_admission import cast_route

            if not row.get("qualityEligible", False):
                quality = row.get("faceQuality") or {}
                held.extend(evidence(
                    [row], [], "single-face candidate quality is unavailable or ineligible"
                    + (f"; {quality['reason']}" if quality.get("reason") else ""),
                    preserveStaged=True,
                ))
                continue
            cast_result = None if admission_context.get("skipCast") else cast_route(row, cores, policy, admission_context)
            if cast_result is not None:
                collection, decision = cast_result
                (assignments if collection == "assignments" else held).append(decision)
                continue
            if admission_context.get("castOnly"):
                held.extend(evidence(
                    [row], [], "deferred to lower-category assessment",
                    preserveStaged=True, lowerDeferred=True,
                ))
                continue
        route_cores = cores
        if admission_context is not None:
            route_cores = {folder: core for folder, core in cores.items() if folder not in cast}
            if (row.get("rebaseCandidate") and row["sourceBucket"] == "Gallery"
                    and not (admission_context.get("redRelease") and row.get("redRelease"))):
                order = {category: index for index, category in enumerate(policy["categoryOrder"])}
                source_rank = order[row["sourceFolder"].split("/", 1)[0]]
                route_cores = {
                    folder: core for folder, core in route_cores.items()
                    if order[folder.split("/", 1)[0]] < source_rank
                }
        ranked = _rank(
            row["vector"], route_cores, row["side"],
            excluded=excluded([row], cores) | (
                {row["sourceFolder"]} if row.get("detachedOutlier") else set()
            ),
        )
        if row["side"] == "Artists":
            held.extend(evidence(
                [row], ranked, "artist-scoped candidate; excluded from the general identity pool",
                preserveStaged=True,
            ))
            continue
        if admission_context is not None and ranked:
            from .normal_admission import beats_home, home_score

            home = home_score(row, cores, admission_context)
            if not beats_home(ranked[0][0], home, policy):
                held.extend(evidence(
                    [row], ranked,
                    "home identity retained: no other identity beats the home score by the own-core lead",
                    preserveStaged=True, homeScore=round(home, 4),
                ))
                continue
        if not ranked:
            if (row.get("rebaseCandidate") and row["sourceBucket"] == "Gallery"
                    and not (admission_context and admission_context.get("redRelease") and row.get("redRelease"))):
                held.extend(evidence([row], [], "no qualified higher identity; current Gallery owner retained",
                                     preserveStaged=True))
            elif (admission_context is not None and row["sourceBucket"] == "Review"
                    and not row.get("regroupReview")
                    and not (admission_context.get("redRelease") and row.get("redRelease"))):
                held.extend(evidence([row], [], "unmatched Review remains non-recruiting with its current owner",
                                     preserveStaged=True))
            else:
                unresolved.append(row)
            continue
        score, folder = ranked[0]
        core = cores[folder]
        rules = categories[core.get("category", folder.split("/", 1)[0])]
        lead = score - ranked[1][0] if len(ranked) > 1 else 2.
        if folder in cast or score < routing["reviewMinimum"]:
            if (row.get("rebaseCandidate") and row["sourceBucket"] == "Gallery"
                    and not (admission_context and admission_context.get("redRelease") and row.get("redRelease"))):
                held.extend(evidence([row], ranked, "higher match is below entry floor; current Gallery owner retained",
                                     preserveStaged=True))
            elif (admission_context is not None and row["sourceBucket"] == "Review"
                    and not row.get("regroupReview")
                    and not (admission_context.get("redRelease") and row.get("redRelease"))):
                held.extend(evidence([row], ranked, "unmatched Review remains non-recruiting with its current owner",
                                     preserveStaged=True))
            else:
                unresolved.append(row)
        elif core.get("identityProtected"):
            held.extend(evidence(
                [row], ranked, "protected Gallery; candidate may enter Review only",
                reviewDestination=(
                    f"{folder}/review" if rules["reviewAdmissionEnabled"]
                    and score >= rules.get("reviewRouteMinimum", routing["reviewMinimum"])
                    and lead >= rules.get("reviewRouteMargin", rules["photoRouteMargin"]) else None
                ),
            ))
        elif evaluate_photo_route(
            core.get("category", folder.split("/", 1)[0]),
            score=score, margin=lead, policy=policy, propose=True,
        )["decision"] == "auto-route":
            assignments.extend(evidence(
                [row], ranked, "qualified photo match against frozen identity core",
                destination=folder, destinationType="existing", score=round(score, 4),
            ))
        else:
            review_destination = (
                f"{folder}/review" if rules["reviewAdmissionEnabled"]
                and score >= rules.get("reviewRouteMinimum", routing["reviewMinimum"])
                and lead >= rules.get("reviewRouteMargin", rules["photoRouteMargin"]) else None
            )
            held.extend(evidence(
                [row], ranked, "existing identity match needs review",
                reviewDestination=review_destination,
                preserveStaged=bool(
                    not review_destination and row.get("rebaseCandidate") and row["sourceBucket"] == "Gallery"
                ),
            ))

    if admission_context is not None and admission_context.get("deferGrouping"):
        for row in unresolved:
            held.extend(evidence(
                [row], [], "unresolved arrival awaits the one qualified reference boundary",
                preserveStaged=True,
            ))
        unresolved = []
    formation = formation_minimums(policy)
    yellow, green = formation["potential"], formation["established"]
    locked = bool(admission_context and admission_context.get("locked"))
    # Match-only (dominant-face) photos may join an existing identity through
    # ordinary matching above, but never seed, join or found a new identity core.
    match_only = [row for row in unresolved if row.get("referenceQualityEligible") is False]
    unresolved = [row for row in unresolved if row.get("referenceQualityEligible") is not False]
    by_side = {}
    for row in unresolved:
        by_side.setdefault(row["side"], []).append(row)
    groups = []
    for side, rows in sorted(by_side.items()):
        # Formation uses the score-band minimum, not a separate linkage value.
        for members in cluster_fn(rows, yellow):
            vector, core_indices = _core(members, yellow)
            core_members = [row for index, row in enumerate(members) if index in core_indices]
            # A below-yellow member must not follow a provisional core into an identity.
            for index, row in enumerate(members):
                if index not in core_indices:
                    groups.append({"rows": [row], "vector": row["vector"], "side": side})
            if core_members:
                groups.append({"rows": core_members, "vector": vector, "side": side})

    # Match small appearance groups to larger frozen provisional groups. Targets
    # never change their reference vectors and cannot themselves join another.
    groups.sort(key=lambda group: (-len(group["rows"]), _group_id(group["rows"])))
    targets, consumed = [], set()
    for index, group in enumerate(groups):
        category = classify(group)["category"]
        group["category"] = category
        ranked = sorted(
            (
                (float(group["vector"] @ groups[target]["vector"]), target)
                for target in targets if groups[target]["side"] == group["side"]
            ),
            key=lambda item: (-item[0], item[1]),
        )
        target = ranked[0][1] if ranked else None
        rules = categories[groups[target]["category"]] if target is not None else None
        existing = _rank(
            group["vector"], cores, group["side"], excluded(group["rows"], cores),
        )
        competitors = ([ranked[1][0]] if len(ranked) > 1 else []) + (
            [existing[0][0]] if existing else []
        )
        lead = ranked[0][0] - max(competitors, default=-1.) if ranked else -2.
        if (
            target is not None and rules is not None
            and ranked[0][0] >= (
                rules["photoRouteMinimum"] if len(group["rows"]) == 1 else rules["mergeMinimum"]
            )
            and lead >= rules["photoRouteMargin"]
            and all(
                float(row["vector"] @ groups[target]["vector"]) >= rules["photoRouteMinimum"]
                for row in group["rows"]
            )
        ):
            groups[target].setdefault("attached", []).extend(group["rows"])
            consumed.add(index)
        elif category not in (None, "Review"):
            targets.append(index)
    for row in sorted(match_only, key=lambda item: item["photoId"]):
        groups.append({"rows": [row], "vector": row["vector"], "side": row["side"], "matchOnly": True})

    def single_photo_rivals(row):
        """Every existing identity, minus rejected, cast-separated, detached or locked ones."""
        blocked = excluded([row], cores)
        if row.get("detachedOutlier"):
            blocked.add(row["sourceFolder"])
        for pair in policy["runtimeSettings"]["different"]:
            if row["sourceFolder"] in pair:
                blocked.update(folder for folder in pair if folder != row["sourceFolder"])
        if locked:
            blocked.update(folder for folder in cores if folder.split("/", 1)[0] in CAST_CATEGORIES)
        return _rank(row["vector"], cores, row["side"], excluded=blocked)

    taken = {name.casefold() for name in names_taken}
    for index, group in enumerate(groups):
        if index in consumed:
            continue
        rows = group["rows"] + group.get("attached", [])
        formation_scores = {}
        if len(rows) > 1:
            kept, removed, formation_scores = _band_trim(rows, yellow)
            # Members below yellow against their group leave it and follow the
            # single-photo rule; they never weaken a new identity.
            for row in removed:
                groups.append({"rows": [row], "vector": row["vector"], "side": row["side"]})
            kept_ids = {row["photoId"] for row in kept}
            core_rows = [row for row in group["rows"] if row["photoId"] in kept_ids] or kept
            core_ids = {row["photoId"] for row in core_rows}
            rows = [row for row in rows if row["photoId"] in kept_ids]
            if removed:
                group = {**group, "rows": core_rows,
                         "attached": [row for row in rows if row["photoId"] not in core_ids],
                         "vector": nz(np.mean([row["vector"] for row in core_rows], axis=0))}
        vector = group["vector"]
        gate = None
        if len(rows) == 1:
            row = rows[0]
            rivals = single_photo_rivals(row)
            gate = {
                "yellowMinimum": yellow,
                "bestRival": rivals[0][1] if rivals else None,
                "bestRivalScore": round(rivals[0][0], 4) if rivals else None,
            }
            if rivals and rivals[0][0] >= yellow:
                folder = rivals[0][1]
                rules = categories[cores[folder].get("category", folder.split("/", 1)[0])]
                own = folder == row["sourceFolder"] and row["sourceBucket"] == "Review"
                destination = f"{folder}/review" if rules["reviewAdmissionEnabled"] and not own else None
                held.extend(evidence(
                    [row], rivals,
                    "leftover photo reaches yellow against an existing identity; sent to that rival's Review"
                    if destination else
                    "leftover photo reaches yellow against an existing identity whose Review is unavailable; held",
                    reviewDestination=destination, singlePhotoGate=gate,
                    **({"preserveStaged": True} if not destination else {}),
                ))
                continue
            if group.get("matchOnly"):
                held.extend(evidence(
                    [row], rivals,
                    "match-only dominant-face photo has no existing match and cannot found a new identity",
                    preserveStaged=True, singlePhotoGate=gate,
                ))
                continue
        cast_ranked = _rank(vector, cast, group["side"], excluded(rows, cast))
        score = cast_ranked[0][0] if cast_ranked else None
        classification = classify({**group, "rows": rows})
        if classification["category"] in (None, "Review"):
            held.extend(evidence(
                rows, cast_ranked, classification["reason"],
                reviewDestination=classification["reviewDestination"],
                reviewAlternatives=classification["reviewAlternatives"],
                automaticReviewAssociation=bool(classification["reviewDestination"]),
            ))
            continue
        established = bool(formation_scores) and min(formation_scores.values()) >= green
        band_gate = None
        if len(rows) >= 5 and not established and classification["category"] != "Potentials":
            # A five-plus group that is yellow but not green forms as a Potential.
            band_gate = "five-plus group is yellow but not green; formed as a Potential"
            classification = {**classification, "category": "Potentials", "reason": band_gate}
        group_id = _group_id(rows)
        name = name_factory(group_id, taken)
        if not name or name.casefold() in taken:
            raise ValueError(f"name factory returned a missing or duplicate name for cluster {group_id}")
        taken.add(name.casefold())
        destination = f"{classification['category']}/{name}"
        single = len(rows) == 1
        reason = (
            f"{SINGLE_PHOTO_LABEL}; new 1-photo Potential because every existing identity scores below yellow"
            if single else
            f"new coherent {len(rows)}-photo identity; classification follows final planned membership"
            + (f"; {band_gate}" if band_gate else "")
        )
        formation_record = {
            "potentialMinimum": yellow, "establishedMinimum": green,
            "memberScores": {photo_id: round(value, 4) for photo_id, value in sorted(formation_scores.items())},
            "band": "single-photo" if single else "green" if established else "yellow",
        }
        member_ids = {row["photoId"] for row in rows}
        clusters.append({
            "clusterId": group_id, "destination": destination, "destinationType": "provisional",
            "photoIds": sorted(member_ids),
            "corePhotoIds": sorted(row["photoId"] for row in group["rows"] if row["photoId"] in member_ids),
            "score": round(score, 4) if score is not None else None,
            "reason": reason, "formation": formation_record,
            **({"singlePhoto": True, "singlePhotoLabel": SINGLE_PHOTO_LABEL} if single else {}),
        })
        assignments.extend(evidence(
            rows, cast_ranked, reason, destination=destination, destinationType="provisional",
            score=round(score, 4) if score is not None else None,
            **({"singlePhoto": True, "singlePhotoGate": gate} if single else {}),
        ))
    return {"assignments": assignments, "held": held, "clusters": clusters}
