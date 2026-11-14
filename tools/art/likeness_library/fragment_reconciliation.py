"""Frozen reference-use repair and direct associations; never routing authority."""
import copy

from . import fragment_review


def prepare(candidate, packet, answers, effective, run):
    fragment_review.validate_answers(packet, answers)
    if fragment_review.digest(candidate) != packet["candidateSHA256"]:
        raise ValueError("reconciliation candidate differs from reviewed packet")
    photos = {row["photoId"]: row for row in run["photos"]}
    if len(photos) != len(run["photos"]) or set(photos) != {r["photoId"] for r in candidate["rows"]}:
        raise ValueError("reconciliation population mismatch")
    identities = {row["folder"]: row for row in candidate["identities"]}
    cases = {row["id"]: row for row in packet["cases"]}
    labels, history = {}, []
    for pair in effective["pairs"]:
        key = tuple(sorted(pair["photoIds"]))
        if len(key) != 2 or key[0] == key[1] or any(pid not in photos for pid in key):
            raise ValueError("invalid existing direct pair")
        if key in labels or pair["label"] not in ("same", "different", "uncertain"):
            raise ValueError("duplicate or invalid existing pair label")
        labels[key] = pair["label"]
    decisions = sorted(answers["decisions"], key=lambda row: row["caseId"])
    associations, proposals, unresolved = [], [], []
    for decision in decisions:
        case = cases[decision["caseId"]]
        query = case["photoId"]
        if query not in photos:
            raise ValueError("review query absent from population")
        for pair in decision["pairs"]:
            key = tuple(sorted((query, pair["referencePhotoId"])))
            previous = labels.get(key)
            label = pair["label"]
            if previous is not None and previous != label:
                # Contradictory direct evidence is held, never overwritten or propagated.
                labels[key] = "uncertain"
                history.append({"photoIds": list(key), "previous": previous, "incoming": label,
                                "effective": "uncertain", "caseId": case["id"]})
            else:
                labels[key] = label
    for decision in decisions:
        case = cases[decision["caseId"]]
        query = case["photoId"]
        if decision["currentMatch"] == decision["targetMatch"] == "different":
            unresolved.append({"caseId": case["id"], "photoId": query, "reason": "neither-identity",
                               "owner": None, "reconsiderable": True})
        for folder, refs, fit in (
            (case["currentFolder"], [case["currentReferenceId"]], decision["currentMatch"]),
            (case["targetFolder"], case["targetReferenceIds"], decision["targetMatch"]),
        ):
            positive = sorted(pid for pid in refs if labels.get(tuple(sorted((query, pid)))) == "same")
            if fit != "same" or not positive:
                continue
            associations.append({
                "caseId": case["id"], "photoId": query, "folder": folder,
                "sameReferencePhotoIds": positive, "origin": "explicit-human-evidence",
                "execution": "not-authorized", "allMembersCertified": False,
            })
            identity = identities[folder]
            for pid in refs:
                if labels.get(tuple(sorted((query, pid)))) != "different":
                    continue
                protected_reference = identity.get("referenceEvidence", {}).get("construction") == "confirmed-character-intent"
                proposals.append({
                    "caseId": case["id"], "folder": folder, "photoId": pid, "queryPhotoId": query,
                    "matchingAnchorPhotoIds": positive,
                    "referenceUse": "conflict-hold" if protected_reference else "withdraw-in-shadow",
                    "wasReference": pid in identity["referencePhotoIds"],
                    "origin": "explicit-human-exception", "placement": "unchanged",
                    "protection": "unchanged", "execution": "not-authorized",
                })
    repaired = copy.deepcopy(candidate)
    withdrawals = {(p["folder"], p["photoId"]) for p in proposals if p["referenceUse"] == "withdraw-in-shadow"}
    for identity in repaired["identities"]:
        identity["referencePhotoIds"] = [
            pid for pid in identity["referencePhotoIds"] if (identity["folder"], pid) not in withdrawals
        ]
    bindings = []
    for pid in sorted(set(packet["usedPhotoIds"])):
        value = photos[pid].get("preparedSHA256") or photos[pid].get("sha256")
        if not value:
            raise ValueError("review evidence requires photo content binding")
        bindings.append({"photoId": pid, "sha256": value})
    ledger = {
        "schemaVersion": 1, "kind": "fragment-reconciliation-ledger",
        "packetSHA256": packet["packetSHA256"], "answersSHA256": fragment_review.digest(answers),
        "photos": bindings, "associations": associations, "referenceProposals": proposals,
        "conflicts": history, "unresolved": unresolved,
        "pairs": [{"photoIds": list(key), "label": label} for key, label in sorted(labels.items())],
        "limits": [
            "Direct human fixtures, not independent accuracy or automatic identity discoveries.",
            "No same-person transitive closure, folder union, pooled reference growth or physical movement.",
            "A different pair is not an identity-wide exclusion unless intended-person and same-anchor evidence also exist.",
            "Reference-use repairs are frozen experimental hypotheses; protection and photo ownership stay unchanged.",
        ],
    }
    return repaired, ledger


def compare(original, repaired, ledger):
    before = {r["photoId"]: r for r in original["rows"]}
    after = {r["photoId"]: r for r in repaired["rows"]}
    if set(before) != set(after):
        raise ValueError("reconciliation loses population")
    by_query = {}
    for association in ledger["associations"]:
        by_query.setdefault(association["photoId"], []).append(association)
    unresolved = {row["photoId"] for row in ledger["unresolved"]}
    output = {"schemaVersion": 1, "kind": "fragment-reconciliation-comparison", "variants": {}}
    for name, linked in (
        ("label-updated-baseline", False), ("reference-repair", False),
        ("association-only", True), ("combined", True),
    ):
        rows = []
        for pid in sorted(before):
            record = (after if name in ("reference-repair", "combined") else before)[pid]
            links = sorted(by_query.get(pid, []), key=lambda r: (r["folder"], r["caseId"])) if linked else []
            rows.append({
                "photoId": pid, "currentFolder": record["currentFolder"],
                "suggestedFolder": record["suggestedFolder"], "hold": record.get("hold"),
                "own": record["own"], "topCandidates": record["topCandidates"],
                "directAssociations": links,
                "outcome": "unresolved-neither" if pid in unresolved else
                "direct-supported-association" if links else "unaccepted-scoring-hypothesis",
                "execution": "not-authorized", "reconsiderable": True, "placement": "unchanged",
            })
        output["variants"][name] = {
            "rows": rows,
            "summary": {
                "photoCount": len(rows),
                "suggestionChangesFromLabelControl": sum(r["suggestedFolder"] != before[r["photoId"]]["suggestedFolder"] for r in rows),
                "directAssociationQueryCount": sum(bool(r["directAssociations"]) for r in rows),
                "unresolvedNeitherCount": sum(r["outcome"] == "unresolved-neither" for r in rows),
                "executableMoves": 0, "automaticIdentityDiscoveries": 0,
            },
        }
    return output
