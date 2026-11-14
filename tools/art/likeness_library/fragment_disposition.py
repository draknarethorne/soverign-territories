"""Member-scoped appearance and fictional-family handoffs, never identity unions."""
import collections

from . import fragment_review


def build(packet, answers, ledger, comparison):
    fragment_review.validate_answers(packet, answers)
    if (ledger["packetSHA256"] != packet["packetSHA256"]
            or ledger["answersSHA256"] != fragment_review.digest(answers)):
        raise ValueError("disposition evidence binding differs")
    combined = comparison["variants"]["combined"]["rows"]
    photos = {row["photoId"]: row for row in combined}
    if len(photos) != len(combined):
        raise ValueError("duplicate disposition population")
    for variant in comparison["variants"].values():
        ids = [row["photoId"] for row in variant["rows"]]
        if len(set(ids)) != len(ids) or set(ids) != set(photos):
            raise ValueError("disposition population conservation differs")
        if any(row["execution"] != "not-authorized" or row["placement"] != "unchanged"
               or row["reconsiderable"] is not True for row in variant["rows"]):
            raise ValueError("disposition source contains executable or locked changes")
    labels = {}
    for pair in ledger["pairs"]:
        ids = pair["photoIds"]
        if (len(ids) != 2 or any(not isinstance(pid, str) or pid not in photos for pid in ids)
                or ids[0] == ids[1] or pair["label"] not in ("same", "different", "uncertain")):
            raise ValueError("invalid disposition direct pair")
        key = tuple(sorted(ids))
        if key in labels:
            raise ValueError("duplicate disposition direct pair")
        labels[key] = pair["label"]
    cases = {case["id"]: case for case in packet["cases"]}
    decisions = []
    for answer in sorted(answers["decisions"], key=lambda row: row["caseId"]):
        case = cases[answer["caseId"]]
        query = case["photoId"]
        refs = {case["currentReferenceId"], *case["targetReferenceIds"]}
        if not {query, *refs} <= photos.keys():
            raise ValueError("disposition photo absent from population")
        if any(tuple(sorted((query, ref))) not in labels for ref in refs):
            raise ValueError("disposition is missing reviewed direct evidence")
        def direct(ref):
            return labels[tuple(sorted((query, ref)))]
        current_positive = [case["currentReferenceId"]] if direct(case["currentReferenceId"]) == "same" else []
        target_positive = sorted(ref for ref in case["targetReferenceIds"] if direct(ref) == "same")
        both = answer["currentMatch"] == answer["targetMatch"] == "same"
        separate = (
            answer["currentMatch"] == "same" and answer["targetMatch"] == "different"
            and bool(current_positive) and all(direct(ref) == "different" for ref in case["targetReferenceIds"])
        ) or (
            answer["targetMatch"] == "same" and answer["currentMatch"] == "different"
            and bool(target_positive) and direct(case["currentReferenceId"]) == "different"
        )
        state = ("same-person-appearance-candidate" if both and current_positive and target_positive else
                 "distinct-lookalike-candidate" if separate else "unresolved-identity")
        groups = []
        if state == "same-person-appearance-candidate":
            for folder, positive in ((case["currentFolder"], current_positive),
                                     (case["targetFolder"], target_positive)):
                groups.append({
                    "sourceFolder": folder, "memberPhotoIds": sorted({query, *positive}),
                    "scope": "direct-query-pairs-only", "coreAdmission": "not-proposed",
                    "grouping": "appearance-hypothesis-not-verified-series",
                })
        decisions.append({
            "caseId": case["id"], "photoId": query, "currentFolder": case["currentFolder"],
            "targetFolder": case["targetFolder"], "disposition": state,
            "appearanceGroups": groups,
            "differentReferencePhotoIds": sorted(ref for ref in refs if direct(ref) == "different"),
            "uncertainReferencePhotoIds": sorted(ref for ref in refs if direct(ref) == "uncertain"),
            "family": {
                "status": "eligible-after-distinct-identity-validation" if separate else "not-eligible",
                "relationship": None, "fictionalOnly": True,
                "samePersonAuthority": False, "surnameChange": False,
            },
            "execution": "not-authorized", "reconsiderable": True,
            "origin": "explicit-human-direct-evidence",
            "residualMembers": "not-certified", "placement": "unchanged",
        })
    by_query = collections.defaultdict(list)
    for decision in decisions:
        by_query[decision["photoId"]].append(decision["caseId"])
    rows = [{
        "photoId": pid, "currentFolder": row["currentFolder"],
        "dispositionCaseIds": sorted(by_query[pid]), "execution": "not-authorized",
        "evidenceScope": "reviewed-query" if by_query[pid] else "not-a-reviewed-query",
        "placement": "unchanged", "reconsiderable": True,
    } for pid, row in sorted(photos.items())]
    return {
        "schemaVersion": 1, "kind": "fragment-end-to-end-disposition",
        "packetSHA256": packet["packetSHA256"], "ledgerSHA256": fragment_review.digest(ledger),
        "cases": decisions, "rows": rows,
        "summary": {
            "photoCount": len(rows), "reviewedCases": len(decisions),
            "dispositions": dict(sorted(collections.Counter(d["disposition"] for d in decisions).items())),
            "appearanceGroupHypotheses": sum(len(d["appearanceGroups"]) for d in decisions),
            "automaticFamilyAssignments": 0, "executableMoves": 0,
            "automaticIdentityDiscoveries": 0,
        },
        "limits": [
            "Human-supported disposition candidates, not an automatic unlabelled identity classifier.",
            "Appearance groups retain direct member provenance; no transitive union or whole-folder certification.",
            "Appearance hypotheses do not establish outfit/series membership, core admission or physical folders.",
            "Separate lookalikes are only a downstream family assessment handoff, not confirmed distinct whole identities.",
            "Family type is fictional, unassigned and cannot resolve identity uncertainty or rename anyone.",
            "Unknown cases stay reconsiderable; placement, protection, art selection and derivatives are untouched.",
        ],
    }
