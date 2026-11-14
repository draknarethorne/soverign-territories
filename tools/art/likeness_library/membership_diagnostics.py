"""Category counterfactuals measure policy sensitivity, not new identity decisions."""
import collections

import numpy as np

from . import fragment_evidence, policy, protection, reformation


CATEGORIES = ("Sisters", "Angels", "Models", "Prospects")


def build(state, run, vectors):
    settings = run["policy"]
    photos = {p["photoId"]: p for p in run["photos"]}
    audit = {p["photoId"]: p for p in run["finalMembershipAudit"]["rows"]}
    rows = {r["photoId"]: r for r in state["rows"]}
    if photos.keys() != rows.keys() or audit.keys() != rows.keys():
        raise ValueError("diagnostic population differs")
    vectors = {pid: fragment_evidence._normalize_vector(v, pid) for pid, v in vectors.items()}
    cache = reformation._FrozenScores(vectors)
    hashes = {pid: p.get("preparedSHA256") or p.get("sha256") for pid, p in photos.items()}
    if any(not value for value in hashes.values()):
        raise ValueError("diagnostic content hashes missing")
    references = {
        pid: {"photoId": pid, "sha256": hashes[pid],
              "vector": fragment_evidence._CachedReferenceVector(pid, cache)} for pid in vectors
    }

    def independent(ids):
        return [r["photoId"] for r in protection._independent([references[pid] for pid in ids], settings)]

    def support(pid, ids, floor):
        return independent([other for other in ids
                            if pid != other and hashes[pid] != hashes[other]
                            and cache.get(pid, other) >= floor])

    def measure(pid, ids):
        ids = sorted(other for other in ids if pid != other and hashes[pid] != hashes[other])
        if not ids or pid not in vectors:
            return None, []
        total = np.sum([vectors[other] for other in ids], axis=0)
        norm = np.linalg.norm(total)
        return (round(float(vectors[pid] @ total / norm), 6), ids) if norm else (None, [])

    core_trials, by_folder = [], collections.defaultdict(list)
    minimum = settings["protection"]["automatic"]["minimumIndependentReferences"]

    def reference_trial(view, floor):
        ids = sorted(view["frozenReferencePhotoIds"])
        history = []
        for number in range(1, reformation.MAX_PASSES + 1):
            kept = [pid for pid in ids if len(support(pid, ids, floor)) >= minimum]
            removed = sorted(set(ids) - set(kept))
            history.append({"pass": number, "withdrawnPhotoIds": removed})
            ids = kept
            if not removed:
                break
        return ids, history

    for view in state["appearances"]:
        if view["pooled"]:
            continue
        by_folder[view["folder"]].append(view)
        if view["category"] not in CATEGORIES:
            continue
        for category in CATEGORIES:
            floor = settings["categoryPolicies"][category]["identityCoreMinimumSimilarity"]
            ids, history = reference_trial(view, floor)
            strict_floor = max(floor, settings["protection"]["automatic"]["minimumOwnCoreSimilarity"])
            strict_ids, strict_history = reference_trial(view, strict_floor)
            core_trials.append({
                "appearanceId": view["appearanceId"], "folder": view["folder"],
                "counterfactualCategory": category, "categoryCoreFloor": floor,
                "originalReferenceCount": len(view["frozenReferencePhotoIds"]),
                "strictShadowReferenceCount": len(view["referencePhotoIds"]),
                "strictNumericReferenceCount": len(strict_ids),
                "strictNumericStable": not strict_history[-1]["withdrawnPhotoIds"],
                "strictNumericPasses": strict_history,
                "categoryOnlyReferenceCount": len(ids), "categoryOnlyReferencePhotoIds": ids,
                "stable": not history[-1]["withdrawnPhotoIds"], "passes": history,
                "authority": "unaccepted-reference-sensitivity-not-certified-core",
                "explicitIntentInSource": view["explicitIntent"],
            })
    output = []
    usable = collections.Counter(r["oldFolder"] for r in rows.values() if audit[r["photoId"]]["qualityEligible"])
    for pid, row in sorted(rows.items()):
        own = row["membershipAssessment"]["own"]
        active_score, active_refs = measure(pid, own["referencePhotoIds"]) if own else (None, [])
        if own and active_score != own["activeScore"]:
            raise ValueError(f"own score does not reproduce from frozen reference inventory: {pid}")
        frozen_options = []
        for view in by_folder[row["oldFolder"]]:
            score, ids = measure(pid, view["frozenReferencePhotoIds"])
            if score is not None:
                frozen_options.append((score, view["appearanceId"], ids))
        frozen = sorted(frozen_options, key=lambda x: (-x[0], x[1]))
        rival = row["membershipAssessment"]["rivals"][:1]
        lead = round(active_score - rival[0]["score"], 6) if active_score is not None and rival else (
            2.0 if active_score is not None else None
        )
        comparison = []
        for category in CATEGORIES:
            rules = settings["categoryPolicies"][category]
            floor = rules.get("galleryAdmissionMinimumSimilarity", rules["photoRouteMinimum"]) \
                if rules["identityProtectedByDefault"] else rules["photoRouteMinimum"]
            supported = support(pid, active_refs, floor) if pid in vectors else []
            blockers = []
            if active_score is None:
                blockers.append("no-qualified-active-own-references")
            elif active_score < floor:
                blockers.append("score-below-new-join-floor")
            if len(supported) < minimum:
                blockers.append("insufficient-independent-support")
            if lead is not None and lead < rules["photoRouteMargin"]:
                blockers.append("rival-separation-insufficient")
            if own:
                blockers.extend(r for r in own["blockers"] if r in (
                    "direct-different-or-uncertain-veto", "reference-boundary-incomplete",
                ))
            consistency = policy.evaluate_photo_consistency(
                category, score=active_score, usable_photo_count=max(1, usable[row["oldFolder"]]),
                policy=settings,
            )
            comparison.append({
                "category": category, "sameActiveOwnScore": active_score, "joinFloor": floor,
                "joinMargin": rules["photoRouteMargin"], "supportPhotoIds": supported,
                "requiredSupport": minimum, "numericJoinPass": not blockers, "numericJoinBlockers": blockers,
                "existingMemberConsistencyIgnoringLocks": consistency,
                "categoryCoreEligible": consistency["coreMember"] if active_score is not None else None,
                "categoryCoreFloor": rules["identityCoreMinimumSimilarity"],
                "actionAuthorization": "none; same evidence only; not a regrouping or category migration",
            })
        own_category = row["oldFolder"].split("/")[0]
        current = next((c for c in comparison if c["category"] == own_category), None)
        output.append({
            "photoId": pid, "oldFolder": row["oldFolder"], "installedDestination": row["installedDestination"],
            "disposition": row["disposition"], "assessmentStatus": row["membershipAssessment"]["status"],
            "placementBlocks": row["placementBlocks"], "scopeAndDecisionReasons": row["reasons"],
            "activeOwnScore": active_score, "activeOwnReferencePhotoIds": active_refs,
            "savedInstalledOwnScore": audit[pid].get("ownScore"),
            "bestOriginalViewScore": frozen[0][0] if frozen else None,
            "bestOriginalViewReferences": frozen[0][2] if frozen else [],
            "rival": rival[0] if rival else None, "ownLeadOverAllHypotheses": lead,
            "categoryComparisons": comparison,
            "retentionAdmissionDisagreement": bool(current and active_score is not None
                and current["existingMemberConsistencyIgnoringLocks"]["decision"] == "keep"
                and not current["numericJoinPass"]),
            "belowHalfButRetainable": bool(current and active_score is not None and active_score < .5
                and current["existingMemberConsistencyIgnoringLocks"]["decision"] == "keep"),
            "physicalPlacement": "unchanged; does not certify identity membership",
        })
    return {
        "kind": "own-core-category-diagnostics", "schemaVersion": 1, "rows": output,
        "referenceSensitivity": core_trials,
        "summary": {
            "photoCount": len(output),
            "activeOwnScoreAvailable": sum(r["activeOwnScore"] is not None for r in output),
            "originalViewScoreOnly": sum(r["activeOwnScore"] is None and r["bestOriginalViewScore"] is not None for r in output),
            "retentionAdmissionDisagreements": sum(r["retentionAdmissionDisagreement"] for r in output),
            "belowHalfButRetainable": sum(r["belowHalfButRetainable"] for r in output),
            "numericJoinPassByCategory": {
                category: sum(c["numericJoinPass"] for r in output for c in r["categoryComparisons"]
                              if c["category"] == category) for category in CATEGORIES
            },
            "placementBlocked": sum(bool(r["placementBlocks"]) for r in output),
            "identityDecisionsChanged": 0, "libraryWrites": 0,
        },
        "limits": [
            "Existing-member keep is not identity confirmation, new admission, or reference eligibility.",
            "Scores are cosine similarity, not probabilities; each score names a different frozen reference inventory.",
            "Changing category does not change embeddings. These counterfactuals do not rerun full identity regrouping.",
            "The original views may be contaminated or reference-starved; their scores cannot certify admission.",
            "The strict shadow core floor uses the automatic-protection minimum; it is not the maintained category core rule.",
            "Reference-sensitivity trials ignore confirmed intent to isolate numeric construction, not override it.",
            "Compare category-only to strict-numeric trials for the isolated floor ablation; final shadow references also include intent/veto/continuation.",
            "Full-hypothesis rival separation includes provisional pooled groups, not only established other people.",
            "No new threshold selected or activated; independent validation and multi-view reconciliation remain required.",
        ],
    }
