"""Policy-driven proposals, independent of filesystem execution authorization."""
import hashlib

import numpy as np

from .audit import audit_person
from .policy import classify_category, evaluate_photo_route
from .rejections import excluded_folders


def _group_id(rows):
    return hashlib.sha256("\n".join(sorted(row["photoId"] for row in rows)).encode()).hexdigest()[:16]


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


def plan_candidates(candidates, cores, policy, name_factory, names_taken, cluster_fn):
    """Keep grouping, matching, classification and proposed action states separate."""
    held, assignments, clusters = [], [], []
    routing = policy["photoRouting"]
    categories = policy["categoryPolicies"]
    cast = {
        folder: core for folder, core in cores.items()
        if categories[core.get("category", folder.split("/", 1)[0])]["identityProtectedByDefault"]
    }
    unresolved = []

    def classify(group):
        ranked = _rank(
            group["vector"], cast, group["side"], excluded_folders(group["rows"], cast),
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
                "reason": reason, **extra,
            }
            for row in rows
        ]

    for row in candidates:
        ranked = _rank(
            row["vector"], cores, row["side"],
            excluded=excluded_folders([row], cores) | (
                {row["sourceFolder"]} if row.get("detachedOutlier") else set()
            ),
        )
        if row["side"] == "Artists":
            held.extend(evidence(
                [row], ranked, "artist-scoped candidate; excluded from the general identity pool",
                preserveStaged=True,
            ))
            continue
        if not ranked:
            unresolved.append(row)
            continue
        score, folder = ranked[0]
        core = cores[folder]
        rules = categories[core.get("category", folder.split("/", 1)[0])]
        lead = score - ranked[1][0] if len(ranked) > 1 else 2.
        if folder in cast or score < routing["reviewMinimum"]:
            unresolved.append(row)
        elif core.get("identityProtected"):
            held.extend(evidence(
                [row], ranked, "protected Gallery; candidate may enter Review only",
                reviewDestination=(
                    f"{folder}/review" if rules["reviewAdmissionEnabled"]
                    and lead >= rules["photoRouteMargin"] else None
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
            held.extend(evidence(
                [row], ranked, "existing identity match needs review",
                reviewDestination=(
                    f"{folder}/review" if rules["reviewAdmissionEnabled"]
                    and lead >= rules["photoRouteMargin"] else None
                ),
            ))

    by_side = {}
    for row in unresolved:
        by_side.setdefault(row["side"], []).append(row)
    groups = []
    for side, rows in sorted(by_side.items()):
        for members in cluster_fn(rows, policy["identityActions"]["identityClusterMinimumSimilarity"]):
            vector, core_indices = _core(
                members, policy["scoreBands"]["orange"]["minimum"],
            )
            core_members = [row for index, row in enumerate(members) if index in core_indices]
            # A red outlier must not follow a provisional core into an identity.
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
            group["vector"], cores, group["side"], excluded_folders(group["rows"], cores),
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

    taken = {name.casefold() for name in names_taken}
    for index, group in enumerate(groups):
        if index in consumed:
            continue
        rows = group["rows"] + group.get("attached", [])
        vector = group["vector"]
        cast_ranked = _rank(vector, cast, group["side"], excluded_folders(rows, cast))
        score = cast_ranked[0][0] if cast_ranked else None
        classification = classify({**group, "rows": rows})
        if classification["category"] in (None, "Review"):
            held.extend(evidence(
                rows, cast_ranked, classification["reason"],
                reviewDestination=classification["reviewDestination"],
                reviewAlternatives=classification["reviewAlternatives"],
            ))
            continue
        group_id = _group_id(rows)
        name = name_factory(group_id, taken)
        if not name or name.casefold() in taken:
            raise ValueError(f"name factory returned a missing or duplicate name for cluster {group_id}")
        taken.add(name.casefold())
        destination = f"{classification['category']}/{name}"
        reason = f"new coherent {len(rows)}-photo identity; classification follows final planned membership"
        clusters.append({
            "clusterId": group_id, "destination": destination, "destinationType": "provisional",
            "photoIds": sorted(row["photoId"] for row in rows),
            "corePhotoIds": sorted(row["photoId"] for row in group["rows"]),
            "score": round(score, 4) if score is not None else None,
            "reason": reason,
        })
        assignments.extend(evidence(
            rows, cast_ranked, reason, destination=destination, destinationType="provisional",
            score=round(score, 4) if score is not None else None,
        ))
    return {"assignments": assignments, "held": held, "clusters": clusters}
