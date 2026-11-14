"""Own-membership assessment and pooled reformation over frozen saved measurements."""
import collections

import numpy as np

from . import fragment_evidence, policy, protection, reformation


PLACEMENT_LOCKS = {"protected", "anchor", "workflowSelected", "identityProtected", "rejectionHistory"}
REFERENCE_BLOCKS = {
    "quality-ineligible", "metadataStale", "ambiguousPhotoId", "artist-scope-held",
    "non-scoring-domain", "review-admission-not-implemented", "rejectionHistory",
    "explicit-owner-unresolved",
}


def build(candidate, run, ledger, photos, audit, previous, vectors, hashes,
          holds, negatives, confirmed, intent, cache, *, progress=None):
    history, limits, pool_inventory = [], None, None
    for boundary in range(1, reformation.MAX_PASSES + 1):
        state = _build_boundary(
            candidate, run, ledger, photos, audit, previous, vectors, hashes,
            holds, negatives, confirmed, intent, cache, progress=progress,
            reference_limits=limits, pool_inventory=pool_inventory,
        )
        if pool_inventory is None:
            pool_inventory = [group["photoIds"] for group in state["reassessmentGroups"]]
        next_limits = {
            view["appearanceId"]: view["nextBoundaryReferencePhotoIds"]
            for view in state["appearances"]
        }
        used = {view["appearanceId"]: view["referencePhotoIds"] for view in state["appearances"]}
        if limits is not None and (
            used.keys() != limits.keys()
            or any(not set(refs) <= set(limits[view]) for view, refs in used.items())
        ):
            raise ValueError("reference continuation changed frozen hypotheses or grew references")
        transition = {
            "boundary": boundary, "referenceCount": sum(map(len, used.values())),
            "nextReferenceCount": sum(map(len, next_limits.values())),
            "qualificationWithdrawals": list(state["passes"]),
            "withdrawals": {
                view: sorted(set(refs) - set(next_limits[view]))
                for view, refs in used.items() if set(refs) != set(next_limits[view])
            },
            "pendingViews": list(state["pendingReferenceWithdrawals"]),
            "membershipDispositions": state["summary"]["membershipDispositions"],
        }
        history.append(transition)
        if progress:
            progress(f"Frozen boundary {boundary}/{reformation.MAX_PASSES}: "
                     f'{transition["referenceCount"]} references -> {transition["nextReferenceCount"]}; '
                     f'{len(transition["pendingViews"])} pending views; growth disabled.')
        if state["summary"]["stable"]:
            break
        limits = next_limits
    state["referenceBoundaries"] = history
    state["summary"]["referenceBoundaryCount"] = len(history)
    state["summary"]["referenceWithdrawals"] = sum(
        len(step["qualificationWithdrawals"]) + sum(map(len, step["withdrawals"].values()))
        for step in history
    )
    state["recipe"]["name"] = "own-reference-assessment-and-pooled-reformation-v2"
    state["recipe"]["maximumReferenceBoundaries"] = reformation.MAX_PASSES
    state["recipe"]["continuation"] = "withdraw-only; fixed discovery pool; frozen rival hypotheses retained"
    state["limits"].append(
        "Reference continuation freezes discovery groups and only withdraws references; "
        "newly freed references remain residuals until a separately constructed discovery boundary."
    )
    return state


def _build_boundary(candidate, run, ledger, photos, audit, previous, vectors, hashes,
                    holds, negatives, confirmed, intent, cache, *, progress=None,
                    reference_limits=None, pool_inventory=None):
    settings = run["policy"]
    categories = settings["categoryPolicies"]
    minimum = settings["protection"]["automatic"]["minimumIndependentReferences"]
    threshold = settings["identityActions"]["identityClusterMinimumSimilarity"]
    identities = {item["folder"]: item for item in candidate["identities"]}
    negatives_by_photo = collections.defaultdict(set)
    for a, b in negatives:
        negatives_by_photo[a].add(b)
        negatives_by_photo[b].add(a)
    withdrawn = {r["photoId"] for r in ledger["referenceProposals"]
                 if r["referenceUse"] == "withdraw-in-shadow" and r["wasReference"]}
    eligible = {pid for pid in vectors if not set(holds[pid]) & REFERENCE_BLOCKS}

    def groups(ids):
        output = []
        for pid in sorted(ids):
            for group in output:
                if all(cache.get(pid, other) >= threshold and other not in negatives_by_photo[pid] for other in group):
                    group.append(pid)
                    break
            else:
                output.append([pid])
        return output

    reference_rows = {
        pid: {"photoId": pid, "sha256": hashes[pid],
              "vector": fragment_evidence._CachedReferenceVector(pid, cache)} for pid in vectors
    }
    independence_cache, centroid_cache = {}, {}

    def independent(ids):
        key = tuple(ids)
        if key not in independence_cache:
            independence_cache[key] = [
                r["photoId"] for r in protection._independent([reference_rows[pid] for pid in key], settings)
            ]
        return independence_cache[key]

    def support(pid, refs, floor):
        return independent([
            other for other in refs
            if other != pid and hashes[pid] != hashes[other] and cache.get(pid, other) >= floor
        ])

    def centroid(refs):
        key = tuple(refs)
        if key not in centroid_cache:
            total = np.sum([vectors[other] for other in refs], axis=0)
            norm = np.linalg.norm(total)
            centroid_cache[key] = total / norm if norm else None
        return centroid_cache[key]

    targets, reference_changes = [], []
    def target(folder, members, *, pooled=False):
        category = folder.split("/")[0]
        rules = categories[category]
        person_id = (
            reformation._id("pooled-candidate", members) if pooled else
            identities[folder].get("identityId") or reformation._id("existing-person", [folder])
        )
        return {
            "folder": folder, "category": category, "personId": person_id,
            "appearanceId": reformation._id("assessed-view", [person_id, *members]),
            "frozenReferencePhotoIds": sorted(members), "referencePhotoIds": sorted(members),
            "pooled": pooled, "explicitIntent": folder in confirmed and not pooled,
            "routeMinimum": rules.get("galleryAdmissionMinimumSimilarity", rules["photoRouteMinimum"])
            if rules["identityProtectedByDefault"] else rules["photoRouteMinimum"],
            "routeMargin": rules["photoRouteMargin"],
        }

    # Rebuild reference influence independently from placement permissions.
    # Withdrawing core use does not certify a different person or evict a photo.
    for folder, identity in sorted(identities.items()):
        if folder.split("/")[0] not in categories or folder.startswith("Artists/"):
            continue
        refs = identity["referencePhotoIds"]
        if len(set(refs)) != len(refs) or not set(refs) <= photos.keys():
            raise ValueError("invalid assessed identity reference inventory")
        allowed = [pid for pid in refs if pid in eligible and pid not in withdrawn]
        for members in groups(allowed):
            item = target(folder, members)
            targets.append(item)
    if progress:
        progress(f"Own-membership assessment: {len(targets)} frozen existing-identity views; "
                 "qualifying reference influence separately from physical locks.")
    if len(targets) * len(photos) > fragment_evidence.MAX_PAIR_OPERATIONS:
        raise ValueError("assessed membership comparison cap exceeded")

    def qualify(item):
        refs = list(item["referencePhotoIds"] if reference_limits is None
                    else reference_limits[item["appearanceId"]])
        core_floor = max(
            categories[item["category"]]["identityCoreMinimumSimilarity"],
            settings["protection"]["automatic"]["minimumOwnCoreSimilarity"],
        )
        history = []
        for number in range(1, reformation.MAX_PASSES + 1):
            kept = refs if item["explicitIntent"] else [
                pid for pid in refs if len(support(pid, refs, core_floor)) >= minimum
            ]
            removed = sorted(set(refs) - set(kept))
            history.append({"pass": number, "withdrawnPhotoIds": removed})
            refs = kept
            if not removed:
                break
        item["referencePhotoIds"] = refs
        item["referenceStable"] = not history[-1]["withdrawnPhotoIds"]
        item["referencePasses"] = history
        item["coreMinimum"] = core_floor
        reference_changes.extend(
            {"photoId": pid, "appearanceId": item["appearanceId"], "folder": item["folder"],
             "pass": row["pass"], "reason": "independent-reference-support-failed"}
            for row in history for pid in row["withdrawnPhotoIds"]
        )
    for item in targets:
        qualify(item)
    frozen_existing = list(targets)

    def compare(pid, item):
        refs = [other for other in item["referencePhotoIds"] if other != pid and hashes[other] != hashes[pid]]
        frozen = [other for other in item["frozenReferencePhotoIds"]
                  if other != pid and hashes[other] != hashes[pid]]
        if pid not in vectors or not frozen:
            return None
        frozen_center = centroid(frozen)
        if frozen_center is None:
            return None
        frozen_score = float(vectors[pid] @ frozen_center)
        active = centroid(refs) if refs else None
        score = float(vectors[pid] @ active) if active is not None else None
        supporting = support(pid, refs, item["routeMinimum"])
        negative_refs = sorted(negatives_by_photo[pid] & set(frozen))
        blockers = []
        if len(supporting) < minimum:
            blockers.append("insufficient-independent-support")
        if score is None:
            blockers.append("reference-needed")
        elif score < item["routeMinimum"]:
            blockers.append("below-route-minimum")
        if negative_refs:
            blockers.append("direct-different-or-uncertain-veto")
        if not item["referenceStable"]:
            blockers.append("reference-boundary-incomplete")
        rules = categories[item["category"]]
        if (rules["identityProtectedByDefault"] and not rules.get("galleryAdmissionEnabled", False)
                and previous[pid]["currentFolder"] != item["folder"]):
            blockers.append("gallery-admission-disabled")
        return {
            "folder": item["folder"], "personId": item["personId"], "appearanceId": item["appearanceId"],
            "score": round(score if score is not None else frozen_score, 6),
            "activeScore": round(score, 6) if score is not None else None,
            "frozenScore": round(frozen_score, 6), "referencePhotoIds": refs,
            "frozenReferencePhotoIds": frozen, "supportPhotoIds": supporting,
            "independentReferenceCount": len(independent(refs)),
            "routeMinimum": item["routeMinimum"], "routeMargin": item["routeMargin"],
            "requiredSupport": minimum, "blockers": blockers,
            "category": item["category"], "pooled": item["pooled"],
        }

    def score_targets(pid, inventory):
        best = {}
        for item in inventory:
            record = compare(pid, item)
            if record is None:
                continue
            old = best.get(item["personId"])
            # A qualified alternate view must not lose to an unsupported view
            # of the same person. Other people remain competitors regardless.
            rank = lambda r: (bool(r["blockers"]), -r["score"], r["appearanceId"])
            if old is None or rank(record) < rank(old):
                best[item["personId"]] = record
        return sorted(best.values(), key=lambda r: (-r["score"], r["personId"]))

    assessments = {}
    for pid in sorted(photos):
        ranked = score_targets(pid, frozen_existing) if pid in eligible else []
        own = next((r for r in ranked if r["folder"] == previous[pid]["currentFolder"]), None)
        rivals = [r for r in ranked if r is not own]
        if pid not in eligible:
            status = "assessment-unavailable"
        elif pid in intent:
            status = "explicit-intent"
        elif own and not own["blockers"]:
            status = "supported" if not rivals or own["score"] - rivals[0]["score"] >= own["routeMargin"] else "ambiguous"
        elif own and own["activeScore"] is not None and own["independentReferenceCount"] >= minimum:
            status = "questionable"
        elif previous[pid]["currentFolder"] in settings["runtimeSettings"]["pool"]:
            status = "no-current-identity"
        else:
            status = "reference-needed"
        assessments[pid] = {"status": status, "own": own, "rivals": rivals[:3],
                            "competitorCount": len(ranked)}
    original_reference_ids = {pid for item in frozen_existing for pid in item["referencePhotoIds"]}
    # All eligible unprotected non-core members may be reconsidered, including
    # reference-starved candidates. Supported membership is not evicted on a tie.
    pool = sorted(pid for pid in eligible
                  if not set(holds[pid]) & PLACEMENT_LOCKS and pid not in intent
                  and (pid not in original_reference_ids or assessments[pid]["status"] == "questionable"))
    pool_groups = []
    discovery_groups = groups(pool) if pool_inventory is None else pool_inventory
    pool = sorted({pid for members in discovery_groups for pid in members})
    for members in discovery_groups:
        classification = policy.classify_category(len(members), policy=settings)
        category = classification["category"]
        if len(members) < minimum + 1 or category not in categories or categories[category]["identityProtectedByDefault"]:
            pool_groups.append({
                "groupId": reformation._id("pool-group", members), "photoIds": members,
                "status": "provisional-only-insufficient-independent-members",
                "categoryProposal": None, "personId": None,
            })
            continue
        item = target(category + "/pooled-candidate", members, pooled=True)
        qualify(item)
        targets.append(item)
        pool_groups.append({
            "groupId": item["appearanceId"], "photoIds": members,
            "status": "provisional-not-yet-admitted", "categoryProposal": category,
            "personId": item["personId"],
        })
    if progress:
        progress(f"Reassessment pool: {len(pool)} eligible photos; {len(pool_groups)} provisional groups; "
                 f"{len(targets) - len(frozen_existing)} independently assessed group targets. No singleton people.")
    if len(targets) * len(photos) > fragment_evidence.MAX_PAIR_OPERATIONS:
        raise ValueError("assessed membership comparison cap exceeded")
    target_by_view = {item["appearanceId"]: item for item in targets}
    frozen_reference_ids = {pid for item in targets for pid in item["referencePhotoIds"]}
    outcomes = []
    for pid in sorted(photos):
        old_folder = previous[pid]["currentFolder"]
        assessment = assessments[pid]
        ranked = score_targets(pid, targets) if pid in eligible else []
        own = assessment["own"]
        rivals = [r for r in ranked if own is None or r["personId"] != own["personId"]]
        if assessment["status"] == "supported" and rivals and own["score"] - rivals[0]["score"] < own["routeMargin"]:
            assessment = {**assessment, "status": "ambiguous"}
        assessment = {**assessment, "rivals": rivals[:3], "competitorCount": len(ranked)}
        alternative = next((r for r in ranked if r["folder"] != old_folder), None)
        action_blocks = sorted(set(holds[pid]) & PLACEMENT_LOCKS)
        reasons = []
        person_id = None
        appearance = None
        origin = "held" if action_blocks or pid not in eligible else "unresolved"
        disposition = "assessment-unavailable"
        reference_used = pid in frozen_reference_ids
        explicit = intent.get(pid)
        if explicit and pid in eligible and not action_blocks:
            item = next(item for item in targets if item["folder"] == explicit and pid in item["frozenReferencePhotoIds"])
            person_id, appearance = item["personId"], item["appearanceId"]
            origin, disposition = "confirmed-character-reference", "explicit-intent"
        elif action_blocks:
            disposition = "change-blocked"
        elif assessment["status"] == "supported":
            item = next(item for item in targets if item["appearanceId"] == own["appearanceId"])
            person_id, appearance = item["personId"], item["appearanceId"]
            origin, disposition = "automatic", "current-membership-supported"
        elif pid in eligible:
            if alternative:
                # The old core is still a competitor. A pool cluster cannot
                # win by erasing inconvenient current/rival evidence.
                competitors = [r for r in ranked if r["personId"] != alternative["personId"]]
                lead = alternative["score"] - max((r["score"] for r in competitors), default=-1.)
                reasons.extend(alternative["blockers"])
                if lead < max(alternative["routeMargin"], settings["photoRouting"]["minimumOwnCoreLead"]):
                    reasons.append("ambiguous-full-competitor-margin")
                if not reasons:
                    person_id, appearance = alternative["personId"], alternative["appearanceId"]
                    origin = "automatic"
                    disposition = "pooled-group-proposed" if alternative["pooled"] else "reassignment-proposed"
            if person_id is None:
                if assessment["status"] == "questionable":
                    disposition = "released-to-reassessment-pool"
                elif assessment["status"] == "ambiguous":
                    disposition = "membership-ambiguous"
                elif pid in pool:
                    disposition = "pooled-awaiting-evidence"
                else:
                    disposition = "reference-needed"
        outcomes.append({
            "photoId": pid, "oldFolder": old_folder, "installedDestination": photos[pid]["destination"],
            "oldPersonId": identities.get(old_folder, {}).get("identityId") or reformation._id("existing-person", [old_folder]),
            "proposedPersonId": person_id, "appearanceId": appearance,
            "origin": origin, "disposition": disposition, "membershipAssessment": assessment,
            "referenceEligible": reference_used, "placementBlocks": action_blocks,
            "releasedFromSupportedMembership": assessment["status"] == "questionable" and not action_blocks,
            "currentMembershipQuestionable": assessment["status"] == "questionable",
            "inReassessmentPool": pid in pool, "explicitIntentFolder": explicit,
            "reasons": sorted(set(reasons) | set(holds[pid])),
            "topCandidates": ranked[:3], "competitorPersonCount": len(ranked),
            "placement": "unchanged", "family": "unassigned-identity-assessment-first",
        })
    by_id = {row["photoId"]: row for row in outcomes}
    conflicts = set()
    for a, b in negatives:
        if by_id[a]["proposedPersonId"] and by_id[a]["proposedPersonId"] == by_id[b]["proposedPersonId"]:
            conflicts.update(pid for pid in (a, b) if by_id[pid]["origin"] == "automatic")
    for pid in sorted(conflicts):
        by_id[pid].update(proposedPersonId=None, appearanceId=None, origin="unresolved",
                         disposition="direct-member-conflict", referenceEligible=False)
        by_id[pid]["reasons"] = sorted(set(by_id[pid]["reasons"]) | {"direct-member-conflict"})
    # A discovered cluster is not a new person merely because one member
    # happens to pass. Retain the whole provisional cluster as evidence.
    for item in targets:
        if not item["pooled"]:
            continue
        assigned = [row for row in outcomes if row["proposedPersonId"] == item["personId"]]
        if len(assigned) < minimum + 1:
            for row in assigned:
                row.update(proposedPersonId=None, appearanceId=None, origin="unresolved",
                           disposition="pooled-awaiting-evidence")
                row["reasons"] = sorted(set(row["reasons"]) | {"insufficient-qualified-group-members"})
    # Freeze this boundary's evidence. If a final member veto invalidates a
    # reference, suppress dependent admissions rather than silently certifying
    # decisions made from a different reference inventory.
    invalid_views = set()
    for _ in range(len(targets) + 1):
        newly_invalid = {
            item["appearanceId"] for item in targets
            if any(
                (not item["pooled"] and by_id[pid]["currentMembershipQuestionable"])
                or by_id[pid]["disposition"] == "direct-member-conflict"
                or (item["pooled"] and by_id[pid]["proposedPersonId"] != item["personId"])
                for pid in item["referencePhotoIds"]
            )
        } - invalid_views
        if not newly_invalid:
            break
        invalid_views.update(newly_invalid)
        for row in outcomes:
            if row["origin"] == "automatic" and row["appearanceId"] in invalid_views:
                row.update(proposedPersonId=None, appearanceId=None, origin="unresolved",
                           disposition="reference-needed")
                row["reasons"] = sorted(set(row["reasons"]) | {"reference-boundary-incomplete"})
                if row["membershipAssessment"]["status"] == "supported":
                    row["membershipAssessment"] = {**row["membershipAssessment"], "status": "reference-needed"}
    else:
        raise ValueError("reference admission veto did not reach a fixed point")
    valid_reference_ids = {
        pid for item in targets if item["appearanceId"] not in invalid_views
        for pid in item["referencePhotoIds"]
    }
    people, retained, appearances = {}, {}, []
    for row in outcomes:
        row["referenceEligible"] = row["photoId"] in valid_reference_ids
        row["effectivePersonId"] = row["proposedPersonId"]
        if row["proposedPersonId"]:
            item = target_by_view[row["appearanceId"]]
            person = people.setdefault(row["proposedPersonId"], {
                "personId": row["proposedPersonId"], "memberPhotoIds": [], "appearanceIds": [],
                "intentFolder": item["folder"] if item["explicitIntent"] else None,
                "canonicalOwner": None if item["pooled"] else item["folder"],
                "ownerStatus": "provisional-new-group-not-named" if item["pooled"] else "existing-owner-proposal",
                "lineage": {},
            })
            person["memberPhotoIds"].append(row["photoId"])
            if row["appearanceId"] not in person["appearanceIds"]:
                person["appearanceIds"].append(row["appearanceId"])
            person["lineage"][row["oldFolder"]] = person["lineage"].get(row["oldFolder"], 0) + 1
        else:
            record = retained.setdefault(row["oldFolder"], {
                "personId": row["oldPersonId"], "folder": row["oldFolder"], "memberPhotoIds": [],
                "status": "physical-lineage-only-not-certified-membership",
            })
            record["memberPhotoIds"].append(row["photoId"])
    invalid_reference_ids = {}
    for item in targets:
        invalid_reference_ids[item["appearanceId"]] = {
            pid for pid in item["referencePhotoIds"]
            if (not item["pooled"] and by_id[pid]["currentMembershipQuestionable"])
            or by_id[pid]["disposition"] == "direct-member-conflict"
            or (item["pooled"] and by_id[pid]["proposedPersonId"] != item["personId"])
        }
        members = [r["photoId"] for r in outcomes if r["appearanceId"] == item["appearanceId"]]
        appearances.append({
            **item, "memberPhotoIds": members,
            "referencePhotoIds": list(item["referencePhotoIds"]),
            "nextBoundaryReferencePhotoIds": [pid for pid in item["referencePhotoIds"]
                                              if pid not in invalid_reference_ids[item["appearanceId"]]],
            "status": "frozen-face-view-not-outfit-certified", "core": False,
        })
    for group in pool_groups:
        assigned = [pid for pid in group["photoIds"] if by_id[pid]["proposedPersonId"] == group["personId"]]
        group["admittedPhotoIds"] = assigned if group["personId"] else []
    residuals = [{
        "oldFolder": folder, "residualPhotoIds": [r["photoId"] for r in outcomes if r["oldFolder"] == folder and not r["proposedPersonId"]],
        "releasedPhotoIds": [r["photoId"] for r in outcomes if r["oldFolder"] == folder and r["releasedFromSupportedMembership"]],
        "status": "membership-and-reference-assessed-not-blindly-retained",
    } for folder in sorted({r["oldFolder"] for r in outcomes})]
    counts = collections.Counter(r["disposition"] for r in outcomes)
    stable = not invalid_views and all(item["referenceStable"] for item in targets)
    return {
        "schemaVersion": 1, "kind": "cross-folder-reformation-state",
        "status": "assessed-shadow-unaccepted" if stable else "bounded-incomplete",
        "rows": outcomes, "people": sorted(people.values(), key=lambda p: p["personId"]),
        "retainedPeople": list(retained.values()), "appearances": appearances, "residuals": residuals,
        "reassessmentGroups": pool_groups, "passes": reference_changes,
        "pendingReferenceWithdrawals": sorted(
            invalid_views | {item["appearanceId"] for item in targets if not item["referenceStable"]}
        ),
        "summary": {
            "photoCount": len(outcomes), "proposedPeople": len(people),
            "crossFolderPeople": sum(len(p["lineage"]) > 1 for p in people.values()),
            "automaticMembers": sum(r["origin"] == "automatic" for r in outcomes),
            "explicitIntentMembers": sum(r["origin"] == "confirmed-character-reference" for r in outcomes),
            "heldPhotos": sum(r["origin"] == "held" for r in outcomes),
            "unresolvedPhotos": sum(r["origin"] == "unresolved" for r in outcomes),
            "membershipDispositions": dict(sorted(counts.items())),
            "referenceWithdrawals": len(reference_changes), "poolPhotos": len(pool),
            "provisionalPoolGroups": len(pool_groups), "newNamedIdentities": 0,
            "stable": stable, "executedMoves": 0,
        },
        "recipe": {
            "name": "own-reference-assessment-and-pooled-reformation-v1",
            "perCategoryMembershipFloors": {c: r.get("galleryAdmissionMinimumSimilarity", r["photoRouteMinimum"])
                                          if r["identityProtectedByDefault"] else r["photoRouteMinimum"]
                                          for c, r in sorted(categories.items())},
            "coreMinimum": settings["protection"]["automatic"]["minimumOwnCoreSimilarity"],
            "independentReferences": minimum, "clusterMinimum": threshold,
            "fullCompetitors": True, "positivePairLabelsInDiscovery": 0,
            "samePassReferenceGrowth": False,
        },
        "limits": [
            "Experimental assessment and proposed state only; no installed moves or accepted accuracy.",
            "Questionable membership is released logically; physical lineage is preserved, not certified.",
            "Insufficient own references mean reference-needed, not proof of a different person.",
            "Pooled groups are provisional, not automatically named singleton identities or certified appearances.",
            "Category proposals reuse count rules, not completed readiness/variety classification.",
            "Protection metadata is respected; no automatic unlocking or workflow-selection invalidation is installed.",
            "General-person multi-view consolidation, secondary cues, growth and incremental runtime remain open.",
        ],
    }
