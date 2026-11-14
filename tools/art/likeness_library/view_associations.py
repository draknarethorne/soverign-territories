"""Build non-core association state without changing reference or rival hypotheses."""
import collections
import math

from . import entrance_trial, reformation, view_hypotheses, view_reconciliation


def _reference_record(evidence, pid, refs, floor):
    refs = sorted(set(evidence.others(pid, refs)))
    score = evidence.measure(pid, refs)
    return {
        "referencePhotoIds": refs,
        "independentReferencePhotoIds": evidence.independent(refs),
        "independentSupportPhotoIds": evidence.support(pid, refs, floor),
        "centroidScore": round(score, 6) if score is not None and math.isfinite(score) else None,
    }


def _reference_comparison(evidence, pid, anchor_refs, rival_refs, floor):
    anchors = set(evidence.others(pid, anchor_refs))
    rivals = set(evidence.others(pid, rival_refs))
    anchor_hashes = {evidence.hashes[p] for p in anchors}
    rival_hashes = {evidence.hashes[p] for p in rivals}
    shared = {p for p in rivals if evidence.hashes[p] in anchor_hashes}
    exclusive_rival = rivals - shared
    exclusive_anchors = {p for p in anchors if evidence.hashes[p] not in rival_hashes}
    if not anchors or not rivals:
        kind = "insufficient-reference-coverage"
    elif not shared:
        kind = "disjoint"
    elif not exclusive_rival and not exclusive_anchors:
        kind = "same-reference-content"
    elif not exclusive_rival:
        kind = "rival-contained-in-original-anchors"
    elif not exclusive_anchors:
        kind = "original-anchors-contained-in-rival"
    else:
        kind = "partial-overlap"
    return {
        "basis": "surviving-original-anchors-versus-strongest-outside-rival",
        "kind": kind, "supportFloor": floor,
        "exactSharedPhotoIds": sorted(anchors & rivals),
        "equalContentSharedRivalPhotoIds": sorted(shared - anchors),
        "originalAnchors": _reference_record(evidence, pid, anchors, floor),
        "outsideRival": _reference_record(evidence, pid, rivals, floor),
        "sharedRival": _reference_record(evidence, pid, shared, floor),
        "exclusiveRival": _reference_record(evidence, pid, exclusive_rival, floor),
        "exclusiveOriginalAnchors": _reference_record(evidence, pid, exclusive_anchors, floor),
        "decisionUse": "diagnostic-only; full signed rival margin remains unchanged",
    }


def build(state, run, vectors, ledger, baseline):
    recipe = entrance_trial.recipes()[1]
    original = entrance_trial.Evidence(state, run, vectors, ledger)
    coalesced, reconciliation = view_reconciliation.build(original, recipe)
    evidence, reconciliation = view_hypotheses.build(coalesced, reconciliation, recipe)
    if reconciliation != baseline["viewReconciliation"]:
        raise ValueError("association original-anchor construction differs from saved baseline")
    control = next(v for v in baseline["variants"] if v["recipe"]["name"] == "ordered-middle-reconciled")
    if not control["summary"]["stable"]:
        raise ValueError("associations require a stable reference baseline")
    source_rows = {r["photoId"]: r for r in control["rows"]}
    if source_rows.keys() != evidence.source.keys():
        raise ValueError("association baseline population differs")
    views = {v["appearanceId"]: v for v in evidence.views}
    inventory = control["references"]
    if inventory.keys() != views.keys():
        raise ValueError("association reference inventory differs")
    values = evidence.scores(inventory)
    unions = {u["personId"]: u for u in reconciliation["unions"]}
    intent_people = {}
    for view in evidence.views:
        if view["explicitIntent"]:
            for pid in view["original"]:
                if pid in intent_people and intent_people[pid] != view["personId"]:
                    raise ValueError("conflicting explicit association intent")
                intent_people[pid] = view["personId"]
    assigned = collections.defaultdict(set)
    for pid, row in source_rows.items():
        person = row["proposalPersonId"] or intent_people.get(pid)
        if person:
            assigned[person].add(pid)
    groups, rows = [], []
    for check in reconciliation["hypothesisReconciliation"]["checks"]:
        if check["accepted"]:
            continue
        view = views[check["candidateViewId"]]
        person = check["personId"]
        union = unions[person]
        joint = views[union["jointViewId"]]
        available = set(inventory[joint["appearanceId"]])
        anchor_ids = sorted({
            c["viewIds"][1] for c in check["comparisons"] if c["viewIds"][0] == view["appearanceId"]
        })
        anchors = [views[key] for key in anchor_ids]
        # Surviving original witnesses only: never tentative/candidate references.
        anchor_refs = {v["appearanceId"]: sorted(set(v["original"]) & available) for v in anchors}
        refs = sorted({pid for ids in anchor_refs.values() for pid in ids})
        members = sorted({
            *view["original"],
            *(pid for pid, row in source_rows.items()
              if any(row[key] and row[key]["appearanceId"] == view["appearanceId"] for key in ("own", "best"))),
        })
        group_id = reformation._id("non-core-association", [person, view["appearanceId"]])
        group = {
            "groupId": group_id, "sourceViewId": view["appearanceId"], "sourceFolder": view["folder"],
            "targetPersonId": person, "displayOwner": union["provisionalDisplayOwner"],
            "originalFolders": union["originalFolders"], "memberPhotoIds": members,
            "originalAnchorViewIds": anchor_ids, "survivingOriginalAnchorPhotoIds": anchor_refs,
            "coreUse": "forbidden", "appearanceStatus": "not-certified",
            "meaning": "per-member non-core association candidates; not a merged view or installed identity",
        }
        groups.append(group)
        for pid in members:
            source = evidence.source[pid]
            row = {
                "associationId": reformation._id("non-core-member", [group_id, pid]),
                "groupId": group_id, "photoId": pid, "oldFolder": source["oldFolder"],
                "sourceViewId": view["appearanceId"], "targetPersonId": person,
                "displayOwner": group["displayOwner"], "originalFolders": union["originalFolders"],
                "status": "unsupported-association", "supportBlockers": [], "actionBlockers": [],
                "baselineProposalPersonId": source_rows[pid]["proposalPersonId"],
                "baselineMembership": source_rows[pid]["membership"],
                "baselineOwnScore": source_rows[pid]["own"]["activeScore"] if source_rows[pid]["own"] else None,
                "target": None, "outsideRival": None, "lead": None, "rivalReferenceComparison": None,
                "anchorEvidence": [], "entranceSupportPhotoIds": [],
                "coreUse": "forbidden", "installedMove": False,
            }
            rows.append(row)
            if pid not in evidence.eligible:
                row["supportBlockers"].append("scope-or-measurement-ineligible")
                continue
            index = evidence.cache.indices[pid]
            rankings = []
            for j, candidate in enumerate(evidence.views):
                active, old = values[index, j], evidence.original_scores[index, j]
                score = active if math.isfinite(active) else old
                if math.isfinite(score):
                    rankings.append((float(score), candidate, float(active) if math.isfinite(active) else None))
            rankings.sort(key=lambda r: (-r[0], r[1]["appearanceId"]))
            target = next((r for r in rankings if r[1]["personId"] == person and r[2] is not None), None)
            rival = next((r for r in rankings if r[1]["personId"] != person), None)
            if target:
                score, receiving, _ = target
                admission = max(recipe["admission"][receiving["category"]], recipe["admission"][view["category"]])
                margin = max(recipe["margin"][receiving["category"]], recipe["margin"][view["category"]])
                row["target"] = {
                    "appearanceId": receiving["appearanceId"], "folder": receiving["folder"],
                    "score": round(score, 6), "admissionFloor": admission, "marginRequired": margin,
                    "referencePhotoIds": evidence.others(pid, inventory[receiving["appearanceId"]]),
                }
                if score < admission:
                    row["supportBlockers"].append("below-member-entrance-floor")
                witnesses = evidence.support(pid, refs, admission)
                row["entranceSupportPhotoIds"] = witnesses
                if len(witnesses) < recipe["joinSupport"]:
                    row["supportBlockers"].append("insufficient-independent-original-entrance-witnesses")
                lead = score - (rival[0] if rival else -1.)
                row["lead"] = round(lead, 6)
                if lead < margin:
                    row["actionBlockers"].append("unresolved-outside-hypothesis")
                rules = evidence.settings["categoryPolicies"][receiving["category"]]
                if (rules["identityProtectedByDefault"] and not rules.get("galleryAdmissionEnabled", False)
                        and receiving["folder"] != source["oldFolder"]):
                    row["actionBlockers"].append("saved-gallery-admission-disabled")
            else:
                row["supportBlockers"].append("no-active-qualified-target")
            if rival:
                score, competing, active = rival
                row["outsideRival"] = {
                    "appearanceId": competing["appearanceId"], "personId": competing["personId"],
                    "folder": competing["folder"], "score": round(score, 6), "active": active is not None,
                    "referencePhotoIds": evidence.others(
                        pid, inventory[competing["appearanceId"]] if active is not None else competing["original"],
                    ),
                }
                if row["target"]:
                    row["rivalReferenceComparison"] = _reference_comparison(
                        evidence, pid, refs, row["outsideRival"]["referencePhotoIds"],
                        row["target"]["admissionFloor"],
                    )
            for anchor in anchors:
                floor = max(recipe["core"][anchor["category"]], recipe["core"][view["category"]])
                support = evidence.support(pid, anchor_refs[anchor["appearanceId"]], floor)
                row["anchorEvidence"].append({
                    "appearanceId": anchor["appearanceId"], "folder": anchor["folder"],
                    "floor": floor, "supportPhotoIds": support, "required": 2,
                })
                if len(support) < 2:
                    row["supportBlockers"].append("insufficient-original-anchor:" + anchor["appearanceId"])
            targets = {p for v in evidence.views if v["personId"] == person for p in v["original"]}
            conflicts = sorted(evidence.negatives[pid].intersection(targets | assigned[person]))
            if conflicts:
                row["supportBlockers"].append("exact-different-or-uncertain-veto")
            row["exactConflictPhotoIds"] = conflicts
            cast = {v["folder"] for v in [view, joint] if v["category"] in ("Sisters", "Angels")}
            if len(cast) > 1:
                row["supportBlockers"].append("distinct-authored-cast-slots")
            if source["placementBlocks"]:
                row["actionBlockers"].append("physical-action-locked")
            if source["explicitIntentFolder"]:
                row["actionBlockers"].append("explicit-intent-preserved")
            if not row["supportBlockers"]:
                row["status"] = (
                    "already-qualified-membership" if source_rows[pid]["proposalPersonId"] == person else
                    "tentative-non-core" if row["actionBlockers"] else "qualified-non-core-proposal"
                )
    supported = collections.defaultdict(set)
    for row in rows:
        if not row["supportBlockers"]:
            supported[row["photoId"]].add(row["targetPersonId"])
    for row in rows:
        if len(supported.get(row["photoId"], set())) > 1 and not row["supportBlockers"]:
            row["status"] = "tentative-non-core"
            row["actionBlockers"].append("multiple-supported-art-identity-associations")
    proposed = collections.defaultdict(set)
    for row in rows:
        if row["status"] == "qualified-non-core-proposal":
            proposed[row["targetPersonId"]].add(row["photoId"])
    for row in rows:
        if row["status"] == "qualified-non-core-proposal":
            if evidence.negatives[row["photoId"]].intersection(proposed[row["targetPersonId"]]):
                row["status"] = "tentative-non-core"
                row["actionBlockers"].append("exact-member-conflict-between-new-associations")
    photo_states = []
    for pid, source in sorted(evidence.source.items()):
        associations = [r for r in rows if r["photoId"] == pid]
        photo_states.append({
            "photoId": pid, "oldFolder": source["oldFolder"],
            "baselineProposalPersonId": source_rows[pid]["proposalPersonId"],
            "associationIds": [r["associationId"] for r in associations],
            "qualifiedNonCorePersonIds": sorted({
                r["targetPersonId"] for r in associations if r["status"] == "qualified-non-core-proposal"
            }),
            "placement": "unchanged", "newCoreUse": False,
        })
    counts = collections.Counter(r["status"] for r in rows)
    return {
        "kind": "non-core-view-association-state", "schemaVersion": 1,
        "recipe": recipe, "groups": groups, "rows": rows, "photoStates": photo_states,
        "summary": {
            "photoCount": len(photo_states), "groupCount": len(groups), "associationRows": len(rows),
            "uniqueScopedPhotos": len({r["photoId"] for r in rows}), "states": dict(counts),
            "uniqueSupportedPhotos": len(supported),
            "uniqueTentativePhotos": len({r["photoId"] for r in rows if r["status"] == "tentative-non-core"}),
            "tentativeReferenceOverlap": dict(collections.Counter(
                r["rivalReferenceComparison"]["kind"] if r["rivalReferenceComparison"] else "unavailable"
                for r in rows if r["status"] == "tentative-non-core"
            )),
            "newQualifiedPhotos": sum(bool(r["qualifiedNonCorePersonIds"]) for r in photo_states),
            "referenceAdditions": 0, "removedRivals": 0, "installedMoves": 0, "modelCalls": 0,
            "positivePairLabelsUsed": 0,
        },
        "limits": [
            "Only uncertified views of the existing three provisional union lineages are examined.",
            "Forward support permits a tentative non-core association, never a certified appearance or core vote.",
            "Every original anchor uses surviving frozen witnesses; self/content/correlated support is excluded.",
            "All original/active outside hypotheses remain in the signed margin, including the candidate's old view.",
            "Tentative associations do not merge people, move files, acquire protection, train labels or certify one another.",
            "Qualified non-core proposals still require per-member entrance, full outside margin, exact vetoes and action permission.",
            "Shared/exclusive reference subsets are diagnostics, not replacement rivals, new anchors or permission to waive margins.",
            "All photos and previous membership proposals remain represented; this is not runtime or full rebase acceptance.",
        ],
    }
