"""Reconcile fully witnessed sibling views, retaining mixed views as rivals."""
import copy
import math

from . import reformation


def compare(evidence, left, right, recipe):
    a, b = left["original"], right["original"]
    floor = max(recipe["core"][left["category"]], recipe["core"][right["category"]])
    witnesses = []
    for source, target in ((left, right), (right, left)):
        for pid in source["original"]:
            support = evidence.support(pid, target["original"], floor)
            witnesses.append({
                "photoId": pid, "sourceViewId": source["appearanceId"],
                "oppositeViewId": target["appearanceId"], "supportPhotoIds": support,
            })
    conflicts = sorted({tuple(sorted((pid, other))) for pid in a
                        for other in evidence.negatives[pid].intersection(b)})
    cast = {v["folder"] for v in (left, right) if v["category"] in ("Sisters", "Angels")}
    failures = [r for r in witnesses if len(r["supportPhotoIds"]) < 2]
    return {
        "viewIds": [left["appearanceId"], right["appearanceId"]], "coreFloor": floor,
        "witnesses": witnesses, "unsupportedReferences": failures,
        "exactConflicts": [list(pair) for pair in conflicts],
        "distinctCastSlots": len(cast) > 1,
        "compatible": bool(a and b and not failures and not conflicts and len(cast) <= 1),
    }


def build(evidence, reconciliation, recipe):
    output = copy.copy(evidence)
    output.views = copy.deepcopy(evidence.views)
    output.own_people = copy.deepcopy(evidence.own_people)
    report = copy.deepcopy(reconciliation)
    checks, extensions = [], []
    original_by_id = {v["appearanceId"]: v for v in evidence.views}
    for union in report["unions"]:
        joint = original_by_id[union["jointViewId"]]
        anchors = [v for v in evidence.views
                   if v["personId"] == union["personId"] and v["appearanceId"] != joint["appearanceId"]]
        if not anchors:
            raise ValueError("view reconciliation has no original anchors")
        # Candidate scope is lineage-bound, but lineage never qualifies an edge.
        candidates = sorted([
            v for v in evidence.views if not v["pooled"]
            and v["personId"] in union["originalPersonIds"] and v["original"]
        ], key=lambda v: v["appearanceId"])
        accepted, refs = [], list(joint["original"])
        for view in candidates:
            comparisons = [compare(evidence, view, anchor, recipe) for anchor in anchors]
            row = {
                "personId": union["personId"], "candidateViewId": view["appearanceId"],
                "folder": view["folder"], "referencePhotoIds": view["original"],
                "comparisons": comparisons, "accepted": False, "reasons": [],
            }
            if not all(c["compatible"] for c in comparisons):
                row["reasons"].append("original-anchor-complete-link-not-qualified")
            else:
                peers = [compare(evidence, view, peer, recipe) for peer in accepted]
                row["comparisons"].extend(peers)
                if not all(c["compatible"] for c in peers):
                    row["reasons"].append("candidate-peer-complete-link-not-qualified")
                combined = sorted(set(refs + view["original"]))
                qualified, stable = evidence.qualify(joint, combined, recipe)
                row["jointCoreRemovedPhotoIds"] = sorted(set(combined) - set(qualified))
                row["jointCoreStable"] = stable
                if not stable or qualified != combined:
                    row["reasons"].append("complete-expanded-core-not-qualified")
                if not row["reasons"]:
                    row["accepted"] = True
                    accepted.append(view)
                    refs = combined
            checks.append(row)
        if not accepted:
            continue
        expanded = {
            **copy.deepcopy(joint), "original": refs, "frozenReferencePhotoIds": refs,
            "appearanceId": reformation._id("reconciled-art-view", refs),
        }
        ids = {view["appearanceId"] for view in accepted}
        for view in output.views:
            if view["appearanceId"] in ids:
                view["personId"] = union["personId"]
        if expanded["appearanceId"] not in {v["appearanceId"] for v in output.views}:
            output.views.append(expanded)
        extensions.append({
            "personId": union["personId"], "originalAnchorViewIds": [v["appearanceId"] for v in anchors],
            "previousJointViewId": joint["appearanceId"], "expandedJointViewId": expanded["appearanceId"],
            "acceptedViewIds": sorted(ids), "referencePhotoIds": refs,
            "originalFolders": union["originalFolders"],
            "provisionalDisplayOwner": union["provisionalDisplayOwner"],
        })
        union["jointViewId"] = expanded["appearanceId"]
        union["referencePhotoIds"] = refs
    output.views.sort(key=lambda v: v["appearanceId"])
    output.original_scores = output.scores({v["appearanceId"]: v["original"] for v in output.views})
    report["hypothesisReconciliation"] = {
        "extensions": extensions, "checks": checks, "positivePairLabelsUsed": 0,
        "crossSupportRequiredPerReference": 2, "installedMoves": 0,
        "limits": [
            "Only existing union lineages are examined; all global rivals remain in scoring.",
            "Every candidate reference must support every original anchor and vice versa.",
            "Accepted candidate views must also be pairwise compatible; no bridge or chained certification.",
            "The complete expanded core must qualify; no failed member is silently transported or discarded.",
            "Mixed/partial views remain rival hypotheses with exact unsupported-reference exceptions.",
            "Frozen development construction, not runtime lifecycle, appearance certification or independent acceptance.",
        ],
    }
    return output, report


def annotate(result, evidence, reconciliation):
    """Expose the actual strongest outside rival used by the frozen scorer."""
    inventory = result["references"]
    values = evidence.scores(inventory)
    report = reconciliation["hypothesisReconciliation"]
    checks = {r["candidateViewId"]: r for r in report["checks"]}
    union_people = {r["personId"] for r in reconciliation["unions"]}
    for row in result["rows"]:
        target = row["best"]
        row["competingView"] = None
        row["reconciledViewIds"] = []
        if target is None:
            continue
        pid = row["photoId"]
        index = evidence.cache.indices[pid]
        ranked = []
        for j, view in enumerate(evidence.views):
            if view["personId"] == target["personId"]:
                if view["appearanceId"] in checks and checks[view["appearanceId"]]["accepted"]:
                    row["reconciledViewIds"].append(view["appearanceId"])
                continue
            active = values[index, j]
            original = evidence.original_scores[index, j]
            score = active if math.isfinite(active) else original
            if math.isfinite(score):
                ranked.append((float(score), view["appearanceId"], view, math.isfinite(active)))
        if not ranked:
            continue
        score, key, view, active = min(ranked, key=lambda r: (-r[0], r[1]))
        check = checks.get(key)
        row["competingView"] = {
            "appearanceId": key, "personId": view["personId"], "folder": view["folder"],
            "score": round(score, 6), "active": bool(active),
            "referencePhotoIds": evidence.others(pid, inventory[key] if active else view["original"]),
            "reconciliationStatus": (
                "not-certified-complete-view" if check and not check["accepted"] else
                "separate-qualified-union" if view["personId"] in union_people else "outside-hypothesis"
            ),
            "exceptionPhotoIds": sorted({
                r["photoId"] for c in check["comparisons"] for r in c["unsupportedReferences"]
            }) if check else [],
            "exactConflicts": [pair for c in check["comparisons"] for pair in c["exactConflicts"]] if check else [],
        }
    result["summary"]["reconciledViews"] = sum(r["accepted"] for r in report["checks"])
    result["summary"]["retainedUncertifiedViews"] = sum(not r["accepted"] for r in report["checks"])
    return result
