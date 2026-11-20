"""Cast-priority individual admission from independently frozen references."""
import hashlib
import json

import numpy as np

from . import metadata, protection, rejections
from .scoring import nz

CAST = frozenset(("Sisters", "Angels"))


def reference_rows(space, cores, catalog):
    rows = {folder: [] for folder in cores}
    for photo in space.photos:
        photo_id = metadata.photo_id_from_name(photo.name)
        if photo.key not in cores or photo_id not in cores[photo.key]["corePhotoIds"]:
            continue
        checksum = metadata.content_sha256(photo.path)
        rows[photo.key].append({
            "photoId": photo_id, "sha256": checksum, "vector": photo.vec,
            "qualityEligible": (
                photo.usable(space.st["minFace"]) and photo.faces == 1
                and getattr(photo, "f2", 0.) <= space.st["multiFace"]
            ),
            **rejections.candidate_state(catalog, photo_id, checksum),
        })
    return rows


def context(cores, references, policy, *, locked=False):
    basis = {
        folder: protection._independent([
            row for row in rows
            if row["qualityEligible"] and not row.get("rejectionMetadataStale")
            and folder not in rejections.excluded_folders([row], cores)
        ], policy)
        for folder, rows in references.items()
    }
    fingerprint = {
        "cores": {folder: core["vector"].tolist() for folder, core in sorted(cores.items())},
        "references": {
            folder: [{"photoId": row["photoId"], "sha256": row["sha256"],
                      "vector": row["vector"].tolist()} for row in rows]
            for folder, rows in sorted(basis.items())
        },
    }
    return {
        "references": references, "independent": basis, "locked": locked,
        "castVectors": {
            folder: core["vector"] for folder, core in cores.items() if folder.split("/", 1)[0] in CAST
        },
        "referenceKeys": {
            folder: ({row["photoId"] for row in rows}, {row["sha256"] for row in rows})
            for folder, rows in references.items()
        },
        "referenceVersion": hashlib.sha256(
            json.dumps(fingerprint, sort_keys=True, allow_nan=False).encode()
        ).hexdigest(),
    }


def cast_route(candidate, cores, policy, admission):
    """Return one terminal cast decision, or None for ordinary lower routing."""
    if candidate["side"] != "Prospects":
        return None
    settings = policy["castAdmission"]
    excluded = rejections.excluded_folders([candidate], cores)
    for pair in policy["runtimeSettings"]["different"]:
        if candidate["sourceFolder"] in pair:
            excluded.update(folder for folder in pair if folder != candidate["sourceFolder"])
    ranked = []
    for folder, core in cores.items():
        if folder.split("/", 1)[0] not in CAST or folder in excluded:
            continue
        refs = admission["references"].get(folder, [])
        keys = admission["referenceKeys"].get(folder, (set(), set()))
        if candidate["photoId"] in keys[0] or candidate.get("sha256") in keys[1]:
            remaining = [
                row for row in refs if row["photoId"] != candidate["photoId"]
                and row["sha256"] != candidate.get("sha256") and row["qualityEligible"]
                and not row.get("rejectionMetadataStale")
            ]
            if not remaining:
                continue
            vector = nz(np.mean([row["vector"] for row in remaining], axis=0))
        else:
            vector = admission["castVectors"].get(folder, core["vector"])
        if not np.linalg.norm(vector):
            continue
        ranked.append((float(np.clip(candidate["vector"] @ vector, -1., 1.)), folder))
    ranked.sort(key=lambda row: (-row[0], row[1].casefold(), row[1]))
    if not ranked or ranked[0][0] < settings["reviewMinimum"]:
        return None
    score, folder = ranked[0]
    rules = policy["categoryPolicies"][folder.split("/", 1)[0]]
    lead = score - ranked[1][0] if len(ranked) > 1 else 2.
    floor = rules.get("galleryAdmissionMinimumSimilarity", rules["photoRouteMinimum"])
    witnesses = [
        row for row in admission["independent"].get(folder, [])
        if row["photoId"] != candidate["photoId"]
        and row["sha256"] != candidate.get("sha256")
        and float(candidate["vector"] @ row["vector"]) <= policy["identityActions"]["independentEvidenceMaximumSimilarity"]
    ]
    enough = len(witnesses) >= settings["minimumIndependentReferences"]
    blockers = [other for other_score, other in ranked[1:] if score - other_score < rules["photoRouteMargin"]]
    approved = {frozenset(pair) for pair in settings["approvedClosePairs"]}
    close = bool(blockers) and all(frozenset((folder, other)) in approved for other in blockers)
    gallery = score >= floor and enough and rules.get("galleryAdmissionEnabled", False)
    mode = (
        "supported-gallery" if gallery and not blockers else
        "optimistic-gallery" if gallery and close else
        "ambiguous-review" if blockers else "named-review"
    )
    evidence = {
        "mode": mode, "winner": folder, "score": score, "margin": lead,
        "alternatives": [{"folder": other, "score": other_score} for other_score, other in ranked[1:]],
        "closePairs": [
            {"folders": [folder, other],
             "coreSimilarity": float(np.clip(cores[folder]["vector"] @ cores[other]["vector"], -1., 1.))}
            for other in blockers if frozenset((folder, other)) in approved
        ],
    }
    row = {
        "photoId": candidate["photoId"], "sourceFolder": candidate["sourceFolder"],
        "sourceBucket": candidate["sourceBucket"], "bestMatch": folder, "bestScore": score,
        "castAdmission": evidence, "referenceVersion": admission["referenceVersion"],
        "independentSupportCount": len(witnesses),
        "supportPhotoIds": [ref["photoId"] for ref in witnesses],
        "referenceEligible": mode == "supported-gallery" and all(
            ref["photoId"] != candidate["photoId"]
            and ref["sha256"] != candidate.get("sha256")
            and float(candidate["vector"] @ ref["vector"]) <= policy["identityActions"]["independentEvidenceMaximumSimilarity"]
            for ref in admission["references"].get(folder, [])
        ),
        "lowerCategoryEvidence": sorted([
            {"folder": other, "score": float(np.clip(candidate["vector"] @ core["vector"], -1., 1.))}
            for other, core in cores.items()
            if other.split("/", 1)[0] in ("Models", "Prospects", "Potentials")
        ], key=lambda item: (-item["score"], item["folder"])),
    }
    if not candidate.get("qualityEligible", False):
        return "held", {**row, "preserveStaged": True, "reason": "cast candidate lacks eligible single-face quality"}
    if admission["locked"]:
        return "held", {**row, "preserveStaged": True, "reason": "cast receiving is locked for this run; rivals remain visible"}
    if mode.endswith("gallery"):
        row.update(
            destination=folder, destinationType="existing",
            reason="independent cast Gallery admission" if mode == "supported-gallery" else
            "approved close-pair Gallery placement; high rival, unconfirmed, non-core and unprotected",
        )
        if lead == 0:
            row["reason"] += "; exact cast tie: stable folder order is storage-only, not identity certainty"
        return "assignments", row
    if rules["reviewAdmissionEnabled"]:
        row.update(
            reviewDestination=f"{folder}/review", referenceEligible=False,
            reason=("cast ambiguity; provisional Review, not a new identity" if blockers else
                    "cast likeness requires Review: Gallery score, receiving or independent support gate not met"),
        )
        if lead == 0:
            row["reason"] += "; exact cast tie: stable folder order is storage-only, not identity certainty"
        return "held", row
    return "held", {**row, "preserveStaged": True, "reason": "cast Review admission is disabled"}


def two_round_plan(api, candidates, cores, references, settings, policy, names_taken, *, locked=False):
    """Resolve existing members first; grow references only once from prior evidence."""
    initial = {folder: dict(core) for folder, core in cores.items()}
    original_rows = {folder: list(rows) for folder, rows in references.items()}
    current, current_rows = initial, original_rows
    by_id = {row["photoId"]: row for row in candidates}
    decisions, clusters, histories = {}, [], []
    snapshots = {}

    def route(rows, frozen, ctx):
        return api.plan_reconciliation(
            rows, frozen, assign=settings["assign"], margin=settings["margin"],
            cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
            minimum_cluster=settings["minCluster"], cast_merge=policy["identityActions"]["autoMergeMinimum"],
            names_taken=names_taken, name_factory=api.invent_name, policy=policy,
            admission_context=ctx,
        )

    def owner(row):
        return row.get("destination") or (
            row["reviewDestination"].rsplit("/", 1)[0] if row.get("reviewDestination") else None
        )

    def leaving(rows):
        return {
            row["photoId"] for row in rows
            if owner(row) and (
                owner(row) != row["sourceFolder"] or row.get("reviewDestination")
            )
        }

    def pool_candidate(row):
        return row["sourceFolder"] == "Various" or row.get("regroupReview")

    pending = list(candidates)
    for round_index in (1, 2):
        ctx = context(current, current_rows, policy, locked=locked)
        ctx["deferGrouping"] = round_index == 1
        snapshots[str(round_index)] = {
            "referenceVersion": ctx["referenceVersion"],
            "photoIds": {folder: list(core["corePhotoIds"]) for folder, core in sorted(current.items())},
        }
        round_rows, retired_ids, retired_folders = [], set(), set()
        existing = [row for row in pending if not pool_candidate(row)]
        arrivals = [row for row in pending if pool_candidate(row)]
        deferred = []
        for batch in (existing, arrivals):
            report = route(batch, current, {**ctx, "castOnly": True})
            terminal = report["assignments"] + [row for row in report["held"] if not row.get("lowerDeferred")]
            deferred.extend(by_id[row["photoId"]] for row in report["held"] if row.get("lowerDeferred"))
            round_rows.extend(terminal)
            retired_ids.update(leaving(terminal))
        for batch in (
            [row for row in deferred if not pool_candidate(row)],
            [row for row in deferred if pool_candidate(row)],
        ):
            retired_folders.update(
                folder for folder, core in current.items()
                if folder.split("/", 1)[0] not in CAST and retired_ids.intersection(core["corePhotoIds"])
            )
            retained = {folder: core for folder, core in current.items() if folder not in retired_folders}
            eligible = []
            for candidate in batch:
                retired_score = max((
                    float(candidate["vector"] @ current[folder]["vector"]) for folder in retired_folders
                ), default=-1.)
                retained_score = max((
                    float(candidate["vector"] @ core["vector"]) for folder, core in retained.items()
                    if folder.split("/", 1)[0] not in CAST
                ), default=-1.)
                if retired_score >= max(retained_score, policy["photoRouting"]["reviewMinimum"]):
                    round_rows.append({
                        "photoId": candidate["photoId"], "sourceFolder": candidate["sourceFolder"],
                        "sourceBucket": candidate["sourceBucket"], "preserveStaged": True,
                        "reason": "old lower core lost reference authority; hold instead of creating another fragment",
                    })
                else:
                    eligible.append(candidate)
            report = route(eligible, retained, {**ctx, "skipCast": True})
            rows = report["assignments"] + report["held"]
            round_rows.extend(rows)
            retired_ids.update(leaving(rows))
            clusters.extend(report.get("clusters", []))
        for row in round_rows:
            row["normalAdmission"] = True
            row.setdefault("referenceVersion", ctx["referenceVersion"])
            if row.get("destinationType") == "provisional":
                row["referenceEligible"] = any(
                    row["photoId"] in group["corePhotoIds"]
                    for group in clusters if group["destination"] == row.get("destination")
                )
            decisions[row["photoId"]] = row
        histories.append({
            "round": round_index, "candidateCount": len(pending),
            "existingFirst": True, "retiredReferenceIds": sorted(retired_ids),
            "retiredLowerCores": sorted(retired_folders),
        })
        next_rows = {
            folder: [row for row in rows if row["photoId"] not in retired_ids]
            for folder, rows in current_rows.items()
        }
        for decision in sorted(round_rows, key=lambda row: row["photoId"]):
            target = decision.get("destination")
            if not target or target not in current or decision.get("castAdmission", {}).get("mode") == "optimistic-gallery":
                continue
            candidate = by_id[decision["photoId"]]
            if candidate["sourceFolder"] == target or not candidate.get("qualityEligible"):
                continue
            rules = policy["categoryPolicies"][target.split("/", 1)[0]]
            prior = [
                row for row in ctx["independent"].get(target, [])
                if row["photoId"] != candidate["photoId"] and row["sha256"] != candidate["sha256"]
                and float(candidate["vector"] @ row["vector"]) >= rules["identityCoreMinimumSimilarity"]
            ]
            minimum = policy["castAdmission"]["minimumIndependentReferences"] if target.split("/", 1)[0] in CAST else 1
            present = next_rows.setdefault(target, [])
            independent = (
                len(prior) >= minimum and all(
                    row["sha256"] != candidate["sha256"]
                    and float(candidate["vector"] @ row["vector"]) <= policy["identityActions"]["independentEvidenceMaximumSimilarity"]
                    for row in present
                )
            )
            decision["referenceEligible"] = independent
            if independent:
                present.append({
                    "photoId": candidate["photoId"], "sha256": candidate["sha256"],
                    "vector": candidate["vector"], "qualityEligible": True,
                })
        if round_index == 2:
            break
        current = {}
        for folder, rows in next_rows.items():
            if not rows:
                continue
            vector = nz(np.mean([row["vector"] for row in rows], axis=0))
            if not np.linalg.norm(vector):
                continue
            current[folder] = {
                **initial[folder], "vector": vector,
                "corePhotoIds": [row["photoId"] for row in rows],
            }
        current_rows = {folder: next_rows[folder] for folder in current}
        pending = [
            by_id[photo_id] for photo_id, row in decisions.items()
            if not row.get("destination")
        ]
    assignments = [row for row in decisions.values() if row.get("destination")]
    held = [row for row in decisions.values() if not row.get("destination")]
    return {
        "assignments": sorted(assignments, key=lambda row: row["photoId"]),
        "held": sorted(held, key=lambda row: row["photoId"]), "clusters": clusters,
        "candidateCount": len(candidates), "assignedCount": len(assignments), "heldCount": len(held),
        "matchingRounds": histories, "referenceSnapshots": snapshots,
        "referenceRefreshCount": 1,
        "passCapReached": any(
            row.get("reviewDestination") or row.get("preserveStaged")
            for row in held
        ) or any(row.get("castAdmission", {}).get("mode") == "optimistic-gallery" for row in assignments),
    }


def validate_move(move, policy):
    """Recheck publication semantics against the bound final-round evidence."""
    data = move["castAdmission"]
    parts = move["destination"].split("/")
    if "/".join(parts[:-2]) != data["winner"] or parts[0] not in CAST:
        raise ValueError("cast admission evidence does not own its destination")
    rules = policy["categoryPolicies"][parts[0]]
    gallery = parts[-2] == "gallery"
    if gallery:
        floor = rules.get("galleryAdmissionMinimumSimilarity", rules["photoRouteMinimum"])
        if data["score"] < floor or len(set(move.get("supportPhotoIds", ()))) < policy["castAdmission"]["minimumIndependentReferences"]:
            raise ValueError("cast Gallery lacks bound score or independent support")
        blockers = [
            row["folder"] for row in data["alternatives"]
            if data["score"] - row["score"] < rules["photoRouteMargin"]
        ]
        if data["mode"] == "optimistic-gallery":
            approved = {frozenset(pair) for pair in policy["castAdmission"]["approvedClosePairs"]}
            if not blockers or any(frozenset((data["winner"], rival)) not in approved for rival in blockers):
                raise ValueError("optimistic Gallery has an unapproved blocking rival")
            if move.get("referenceEligible"):
                raise ValueError("optimistic Gallery cannot grant reference authority")
        elif data["mode"] != "supported-gallery" or blockers:
            raise ValueError("cast Gallery retains an unresolved distinct-identity rival")
    elif (
        parts[-2] != "review" or data["mode"] not in ("ambiguous-review", "named-review")
        or data["score"] < policy["castAdmission"]["reviewMinimum"]
        or move.get("referenceEligible")
    ):
        raise ValueError("invalid provisional cast Review disposition")
