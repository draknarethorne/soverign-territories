"""Propose art-identity view unions; never transport a folder or infer kinship."""
import copy

from . import reformation


def build(evidence, recipe):
    e = evidence
    cross_support = 2
    candidates = [v for v in e.views if not v["pooled"] and len(v["original"]) >= cross_support]
    compatible, edges = set(), []
    for i, left in enumerate(candidates):
        for right in candidates[i+1:]:
            if left["personId"] == right["personId"]:
                continue
            a, b = left["original"], right["original"]
            if any(e.negatives[pid].intersection(b) for pid in a):
                continue
            # Distinct authored cast slots are not automatic merge targets.
            cast = {v["folder"] for v in (left, right) if v["category"] in ("Sisters", "Angels")}
            if len(cast) > 1:
                continue
            floor = max(recipe["core"][left["category"]], recipe["core"][right["category"]])
            if not all(len(e.support(pid, b, floor)) >= cross_support for pid in a):
                continue
            if not all(len(e.support(pid, a, floor)) >= cross_support for pid in b):
                continue
            merged = sorted(set(a+b))
            category = next((v["category"] for v in (left, right) if v["folder"] in cast), left["category"])
            trial = {"explicitIntent": False, "category": category}
            qualified, stable = e.qualify(trial, merged, recipe)
            if not stable or qualified != merged:
                continue
            pair = tuple(sorted((left["appearanceId"], right["appearanceId"])))
            compatible.add(pair)
            edges.append({
                "views": list(pair), "folders": [left["folder"], right["folder"]],
                "coreFloor": floor, "crossSupportRequiredPerReference": cross_support,
                "leftPhotoIds": a, "rightPhotoIds": b,
                "construction": "all-reference-mutual-independent-support-and-joint-core",
            })
    # Complete-link, not connected components: A-B and B-C never establish A-C.
    groups = []
    for view in sorted(candidates, key=lambda v: v["appearanceId"]):
        for group in groups:
            people = {v["personId"] for v in group}
            if view["personId"] in people:
                continue
            cast = {v["folder"] for v in [*group, view] if v["category"] in ("Sisters", "Angels")}
            if len(cast) > 1:
                continue
            if all(tuple(sorted((view["appearanceId"], other["appearanceId"]))) in compatible for other in group):
                group.append(view)
                break
        else:
            groups.append([view])
    output = copy.copy(e)
    output.views = copy.deepcopy(e.views)
    output.own_people = {pid: {row["oldPersonId"]} for pid, row in e.source.items()}
    unions, used_people = [], set()
    for group in groups:
        if len(group) < 2:
            continue
        people = {v["personId"] for v in group}
        # A person's multiple views cannot be used to chain otherwise
        # unqualified unions; ambiguous overlapping unions remain separate.
        if used_people & people:
            continue
        refs = sorted({pid for view in group for pid in view["original"]})
        cast = [v for v in group if v["category"] in ("Sisters", "Angels")]
        owner = min(cast or group, key=lambda v: v["folder"])
        merged = {
            **copy.deepcopy(owner), "original": refs, "explicitIntent": False,
            "frozenReferencePhotoIds": refs,
        }
        qualified, stable = e.qualify(merged, refs, recipe)
        if not stable or qualified != refs:
            continue
        person_id = reformation._id("reconciled-art-person", sorted(people))
        merged.update(personId=person_id, appearanceId=reformation._id("reconciled-art-view", refs))
        participating = {v["appearanceId"] for v in group}
        for view in output.views:
            if view["appearanceId"] in participating:
                view["personId"] = person_id
        output.views.append(merged)
        for pid, old_people in output.own_people.items():
            if old_people & people:
                output.own_people[pid] = old_people | {person_id}
        unions.append({
            "personId": person_id, "jointViewId": merged["appearanceId"],
            "originalPersonIds": sorted(people), "originalFolders": sorted({v["folder"] for v in group}),
            "referencePhotoIds": refs, "provisionalDisplayOwner": owner["folder"],
            "ownerStatus": "existing-cast-name-preserved" if cast else "provisional-source-name-not-final-owner",
            "meaning": "compatible-art-identity-reference-views; every photo still requires individual admission",
        })
        used_people.update(people)
    output.views.sort(key=lambda v: v["appearanceId"])
    output.original_scores = output.scores({v["appearanceId"]: v["original"] for v in output.views})
    return output, {
        "unions": unions, "qualifyingEdges": edges,
        "crossSupportRequiredPerReference": cross_support,
        "positivePairLabelsUsed": 0, "foldersMoved": 0, "newNames": 0,
        "fictionalRelationshipAssignments": 0,
        "limits": [
            "Exploratory all-reference view coalescence, not real-world person identification.",
            "Mixed/partially matching views and ambiguous overlapping unions remain unresolved.",
            "No new standalone discovery or appearance/outfit certification.",
            "Distinct cast slots, direct negative/uncertain pairs and incomplete cores prevent unions.",
            "Core support floor and two-way cross-reference witnesses are not independent acceptance.",
        ],
    }
