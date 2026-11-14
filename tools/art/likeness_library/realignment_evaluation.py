"""Evidence-blinded diagnostics; not independent series-held-out acceptance."""
import copy


def evaluate(run, vectors, packet, answers, effective, evaluator):
    """Mask non-reference character answers and pairs before scoring those queries."""
    masked_packet, masked_answers = copy.deepcopy((packet, answers))
    withheld = [
        {"folder": group["folder"], "photoId": item["photoId"], "choice": item["choice"]}
        for group in answers["characters"] for item in group["decisions"]
        if item["choice"] != "reference"
    ]
    excluded = {item["photoId"] for item in withheld}
    for group in masked_packet["characters"]:
        group["cards"] = [
            {"photoId": card["photoId"]} for card in group["cards"] if card["photoId"] not in excluded
        ]
    for group in masked_answers["characters"]:
        group["decisions"] = [item for item in group["decisions"] if item["photoId"] not in excluded]
    labels = {"pairs": [
        copy.deepcopy(pair) for pair in effective.get("pairs", [])
        if not excluded.intersection(pair["photoIds"])
    ]}
    candidate = evaluator(
        run, vectors, masked_packet, masked_answers, labels,
        excluded_reference_ids=sorted(excluded),
    )
    rows = {row["photoId"]: row for row in candidate["rows"]}
    if set(rows) != {row["photoId"] for row in run["photos"]}:
        raise ValueError("label-blinded evaluation lost query rows")
    hashes = {
        row["photoId"]: row.get("preparedSHA256") or row.get("sha256") for row in run["photos"]
    }
    if not all(hashes.values()):
        raise ValueError("label-blinded evaluation requires content-bound photos")
    excluded_hashes = {hashes[pid] for pid in excluded}
    for identity in candidate["identities"]:
        if any(pid in excluded or hashes[pid] in excluded_hashes for pid in identity["referencePhotoIds"]):
            raise ValueError("label-blinded query content leaked into reconstructed references")
    cases = []
    for item in sorted(withheld, key=lambda value: (value["folder"], value["photoId"])):
        row = rows[item["photoId"]]
        attracted = row["candidateFolder"] == item["folder"]
        choice = item["choice"]
        routing_blockers = [
            blocker for blocker in row["blockers"]
            if blocker not in {"diagnostic-reference-exclusion", "equal-content-diagnostic-exclusion"}
        ]
        cases.append({
            **item, "candidateFolder": row["candidateFolder"], "state": row["state"],
            "origin": row["origin"], "attractedToJudgedCharacter": attracted,
            "clearsSafeguards": (
                attracted and row["origin"] == "automatic-hypothesis" and not routing_blockers
            ),
            "blockers": row["blockers"],
            "routingBlockers": routing_blockers,
            "outcome": (
                "positive-target-proposed" if choice == "same-not-reference" and attracted else
                "positive-not-recovered" if choice == "same-not-reference" else
                "negative-attraction" if choice == "different" and attracted else
                "negative-not-attracted" if choice == "different" else
                "uncertain-not-scored-as-correct-or-incorrect"
            ),
        })
    return {
        "schemaVersion": 1, "kind": "label-blinded-realignment-diagnostic",
        "maskedPhotoCount": len(excluded),
        "removedIncidentPairCount": len(effective.get("pairs", [])) - len(labels["pairs"]),
        "referenceExclusions": sorted(excluded),
        "summary": {
            outcome: sum(row["outcome"] == outcome for row in cases)
            for outcome in (
                "positive-target-proposed", "positive-not-recovered",
                "negative-attraction", "negative-not-attracted",
                "uncertain-not-scored-as-correct-or-incorrect",
            )
        },
        "qualifiedPositiveCount": sum(
            row["choice"] == "same-not-reference" and row["clearsSafeguards"] for row in cases
        ),
        "qualifiedNegativeAttractionCount": sum(
            row["choice"] == "different" and row["clearsSafeguards"] for row in cases
        ),
        "cases": cases,
        "limits": [
            "Non-reference character answers and incident pairs are hidden from this diagnostic evaluator.",
            "Withheld query IDs and equal-content measurements cannot supply any reconstructed reference set.",
            "Reference examples remain training inputs; leave-one-out is not independent held-out accuracy.",
            "Photos were selected using earlier scores and feedback; identities/series are not independently held out.",
            "Absence of a negative attraction is not proof of correct grouping or overall precision.",
            "A proposed target may still fail safeguards; target proposal is not qualified recovery.",
            "No acceptance threshold, routing policy, installation approval or matching accuracy claim follows.",
        ],
    }
