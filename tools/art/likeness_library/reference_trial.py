"""Receipt-only frozen-reference scoring and one-pass shared membership probes."""
import collections
import copy

import numpy as np

from . import character_packet, protection, refinement, review_packet, shadow
from .scoring import nz


def _unique(rows, name):
    result = {row["photoId"]: row for row in rows}
    if len(result) != len(rows) or not all(result):
        raise ValueError(f"{name} requires unique stable photo IDs")
    return result


def evaluate(run, vectors, packet, answers, effective_labels):
    """Compare frozen saved cores with confirmed references; never route or mutate."""
    character_packet.validate_answers(packet, answers)
    photos = _unique(run["photos"], "receipt")
    audit = _unique(run["finalMembershipAudit"]["rows"], "audit")
    if photos.keys() != audit.keys():
        raise ValueError("receipt/audit candidate conservation differs")
    for pid in photos:
        if photos[pid]["destination"] != audit[pid]["destination"]:
            raise ValueError(f"receipt/audit placement differs: {pid}")
    policy = run["policy"]
    maximum = policy["identityActions"]["independentEvidenceMaximumSimilarity"]
    measurements, dimension = {}, None
    for pid in sorted(photos):
        if pid not in vectors:
            if audit[pid].get("qualityEligible") or audit[pid].get("coreMember"):
                raise ValueError(f"missing eligible/core vector: {pid}")
            continue
        vector = np.asarray(vectors[pid])
        if (vector.ndim != 1 or not vector.size or not np.isfinite(vector).all()
                or not np.linalg.norm(vector)):
            raise ValueError(f"invalid saved vector: {pid}")
        if dimension is not None and vector.shape != dimension:
            raise ValueError(f"inconsistent saved vector dimension: {pid}")
        dimension = vector.shape
        measurements[pid] = vector
    canonical_run = {
        **run, "finalMembershipAudit": {
            **run["finalMembershipAudit"], "rows": [audit[pid] for pid in sorted(audit)],
        },
    }
    parity, saved_groups = review_packet.final_score_parity(canonical_run, measurements)
    baseline = {folder: sorted(ids) for folder, ids in sorted(saved_groups.items())}
    choices = {
        group["folder"]: {item["photoId"]: item["choice"] for item in group["decisions"]}
        for group in answers["characters"]
    }
    if not choices:
        raise ValueError("no reviewed characters")
    references, owner = {}, {}
    for folder in sorted(choices):
        if folder not in baseline:
            raise ValueError(f"reviewed character has no baseline core: {folder}")
        references[folder] = []
        for pid, choice in sorted(choices[folder].items()):
            if pid not in photos:
                raise ValueError(f"unknown reviewed photo: {pid}")
            if choice != "reference":
                continue
            if not audit[pid].get("qualityEligible") or pid not in measurements:
                raise ValueError(f"confirmed reference lacks eligible measurement: {pid}")
            if pid in owner:
                raise ValueError(f"reference assigned to multiple characters: {pid}")
            owner[pid] = folder
            references[folder].append(pid)
        if len(references[folder]) < 2:
            raise ValueError(f"insufficient confirmed references for leave-one-out: {folder}")
    confirmed = {
        folder: references[folder] if folder in references else [
            pid for pid in ids if pid not in owner
        ]
        for folder, ids in baseline.items()
    }
    transfers = [
        {"photoId": pid, "fromFolder": folder, "toFolder": owner[pid],
         "reason": "withdraw confirmed reference from another frozen core"}
        for folder, ids in baseline.items() for pid in ids
        if pid in owner and owner[pid] != folder
    ]
    unavailable = [
        {"variant": "confirmed", "folder": folder,
         "reason": "frozen core empty after confirmed-reference withdrawal",
         "removedPhotoIds": baseline[folder]}
        for folder, ids in confirmed.items() if not ids
    ]
    characters = [{
        "folder": folder, "baselineReferenceCount": len(baseline[folder]),
        "confirmedReferenceCount": len(references[folder]),
        "choices": dict(sorted(collections.Counter(choices[folder].values()).items())),
        "referenceIds": references[folder],
        "baselineReferenceIds": baseline[folder],
        "referenceRemovals": [pid for pid in baseline[folder] if pid not in references[folder]],
    } for folder in sorted(choices)]

    def content_hash(pid):
        value = photos[pid].get("preparedSHA256") or photos[pid].get("sha256")
        if not value:
            raise ValueError(f"missing content hash for independent support: {pid}")
        return value

    protected = collections.defaultdict(bool)
    for pid, row in audit.items():
        folder = shadow.folder_for(row)
        protected[folder] |= bool(row.get("identityProtected"))
        target = row.get("refinementTarget")
        if target:
            protected[target["folder"]] |= bool(target.get("identityProtected"))
    contexts, frozen_cache, support_cache = {}, {}, {}
    for name, groups in (("baseline", baseline), ("confirmed", confirmed)):
        frozen = {}
        for folder, ids in groups.items():
            if not ids:
                continue
            key = tuple(ids)
            if key not in frozen_cache:
                total = np.sum([measurements[pid] for pid in ids], axis=0)
                frozen_cache[key] = {
                    "center": nz(np.mean([measurements[pid] for pid in ids], axis=0)),
                    "total": total, "members": frozenset(ids),
                    "independent": protection._independent([
                        {"photoId": pid, "vector": measurements[pid], "sha256": content_hash(pid)}
                        for pid in ids if not audit[pid].get("rejectionHistory")
                        and not audit[pid].get("ambiguousPhotoId")
                    ], policy),
                }
            frozen[folder] = frozen_cache[key]
        contexts[name] = (groups, frozen)

    profile_references = {
        folder: [
            (pid, content_hash(pid), measurements[pid]) for pid in ids
        ] for folder, ids in references.items()
    }

    def confirmed_profile(pid, folder, eligible):
        ranked = []
        if eligible:
            query_sha = content_hash(pid)
            ranked = sorted(
                ((float(measurements[pid] @ vector), other)
                 for other, sha, vector in profile_references[folder]
                 if other != pid and sha != query_sha),
                key=lambda item: (-item[0], item[1]),
            )
        return {
            "nearestScore": round(ranked[0][0], 6) if ranked else None,
            "secondScore": round(ranked[1][0], 6) if len(ranked) > 1 else None,
            "topTwoMean": round((ranked[0][0] + ranked[1][0]) / 2, 6)
            if len(ranked) > 1 else None,
            "nearestReferencePhotoId": ranked[0][1] if ranked else None,
            "referenceCount": len(ranked),
        }

    def comparison(pid, name):
        groups, frozen = contexts[name]
        vector = measurements[pid]
        scores, support, counts, unavailable_here = {}, {}, {}, []
        for folder, ids in groups.items():
            core = frozen.get(folder)
            inside = core is not None and pid in core["members"]
            counts[folder] = len(ids) - inside
            if not counts[folder]:
                scores[folder], support[folder] = None, 0
                unavailable_here.append(folder)
                continue
            reference = (
                nz(core["total"] - vector) if inside else core["center"]
            )
            value = float(vector @ reference)
            scores[folder] = (
                float(np.clip(value, -1, 1)) if folder == shadow.folder_for(audit[pid]) else value
            )
        folder = shadow.folder_for(audit[pid])
        own = scores.get(folder)
        rivals = sorted(
            ({"folder": other, "score": value} for other, value in scores.items()
             if other != folder and value is not None
             and other.startswith("Artists/") == folder.startswith("Artists/")),
            key=lambda row: (-row["score"], row["folder"]),
        )[:3]
        needed = set(choices)
        if rivals:
            needed.add(rivals[0]["folder"])
        for target in sorted(needed):
            core = frozen.get(target)
            if core is None or scores.get(target) is None:
                support[target] = 0
                continue
            key = (pid, tuple(groups[target]))
            if key not in support_cache:
                query_sha = content_hash(pid)
                support_cache[key] = sum(
                    other["photoId"] != pid and other["sha256"] != query_sha
                    and float(vector @ other["vector"]) <= maximum
                    for other in core["independent"]
                )
            support[target] = support_cache[key]
        probe = copy.deepcopy(audit[pid])
        probe.update(
            ownScore=own, rivals=rivals,
            higherRival=bool(own is not None and rivals and rivals[0]["score"] > own),
            refinementTarget=({
                **rivals[0], "independentSupport": support[rivals[0]["folder"]],
                "identityProtected": protected[rivals[0]["folder"]],
            } if rivals else None),
        )
        decision = refinement.membership_decision(probe, policy)
        output = {
            "ownScore": round(own, 6) if own is not None else None,
            "rivals": [{**rival, "score": round(rival["score"], 6)} for rival in rivals],
            "higherRival": probe["higherRival"],
            "refinementTarget": ({
                **probe["refinementTarget"], "score": round(rivals[0]["score"], 6),
            } if rivals else None),
            "policyDecision": decision, "unavailableCompetitors": unavailable_here,
        }
        return output, scores, support, counts

    rows, evidence, move_counts = [], [], collections.Counter()
    changed = 0
    for pid in sorted(photos):
        folder = shadow.folder_for(audit[pid])
        eligible = bool(audit[pid].get("qualityEligible") and pid in measurements)
        by_character = {char: values[pid] for char, values in sorted(choices.items()) if pid in values}
        row = {
            "photoId": pid, "currentFolder": folder, "qualityEligible": eligible,
            "choiceByCharacter": by_character, "characterScores": {},
        }
        comparisons = {}
        for name in contexts:
            if eligible:
                output, scores, support, counts = comparison(pid, name)
            else:
                probe = copy.deepcopy(audit[pid])
                probe.update(ownScore=None, rivals=[], higherRival=False, refinementTarget=None)
                output = {
                    "ownScore": None, "rivals": [], "higherRival": False,
                    "refinementTarget": None,
                    "policyDecision": refinement.membership_decision(probe, policy),
                    "unavailableCompetitors": [],
                }
                scores, support, counts = {}, {}, {}
            row[name] = output
            comparisons[name] = (scores, support, counts)
            move_counts[name] += output["policyDecision"]["decision"] == "move"
        def top(name):
            return row[name]["rivals"][0]["folder"] if row[name]["rivals"] else None
        changed += top("baseline") != top("confirmed")
        for char in sorted(choices):
            entry = {
                "choice": choices[char].get(pid),
                "confirmedProfile": confirmed_profile(pid, char, eligible),
            }
            for name in contexts:
                scores, support, counts = comparisons[name]
                score = scores.get(char)
                entry[name] = round(score, 6) if score is not None else None
                entry[name + "ReferenceCount"] = counts.get(
                    char, len(contexts[name][0].get(char, [])),
                )
                entry[name + "Support"] = support.get(char, 0)
            row["characterScores"][char] = entry
            if pid in choices[char]:
                choice = choices[char][pid]
                evidence.append({
                    "folder": char, "photoId": pid, "choice": choice,
                    "baselineScore": entry["baseline"], "confirmedScore": entry["confirmed"],
                    "baselineSupport": entry["baselineSupport"],
                    "confirmedSupport": entry["confirmedSupport"],
                    "confirmedProfile": entry["confirmedProfile"],
                    "evaluationRole": (
                        "training leave-one-out diagnostic" if choice == "reference" else
                        "explicit non-reference positive" if choice == "same-not-reference" else
                        "explicit negative" if choice == "different" else "not a positive or negative"
                    ),
                })
        rows.append(row)
    pairs, conflicts = [], []
    seen_pairs = set()
    for pair in effective_labels.get("pairs", []):
        ids = pair.get("photoIds", [])
        if (not isinstance(ids, list) or len(ids) != 2 or ids[0] == ids[1]
                or any(pid not in photos for pid in ids)
                or pair.get("label") not in {"same", "different", "uncertain"}):
            raise ValueError("invalid effective direct pair evidence")
        a, b = sorted(ids)
        if (a, b) in seen_pairs:
            raise ValueError("duplicate effective direct pair evidence")
        seen_pairs.add((a, b))
        value = float(measurements[a] @ measurements[b]) if (
            a in measurements and b in measurements
        ) else None
        pairs.append({
            "photoIds": [a, b], "label": pair["label"],
            "score": round(value, 6) if value is not None else None,
        })
        for char in sorted(choices):
            left, right = choices[char].get(a), choices[char].get(b)
            positives = {"reference", "same-not-reference"}
            implied = (
                "same" if left in positives and right in positives else
                "different" if (left in positives and right == "different"
                                or right in positives and left == "different") else None
            )
            if implied is not None and pair["label"] not in {implied, "uncertain"}:
                conflicts.append({
                    "folder": char, "photoIds": [a, b], "pairLabel": pair["label"],
                    "characterIntentRelation": implied, "choices": [left, right],
                    "resolution": "none; both direct evidence sources preserved",
                })
    return {
        "schemaVersion": 1, "characters": characters, "rows": rows,
        "summary": {
            "photoCount": len(rows), "eligibleCount": sum(row["qualityEligible"] for row in rows),
            "baselineParity": parity, "changedTopRivalCount": changed,
            "policyMoves": {name: move_counts[name] for name in contexts},
            "confirmedReferenceCount": len(owner),
            "referenceTransferCount": len(transfers), "intentConflictCount": len(conflicts),
            "policyProbePasses": 1,
        },
        "referenceTransfers": transfers, "unavailableCompetitors": unavailable,
        "knownCharacterEvidence": sorted(evidence, key=lambda item: (item["folder"], item["photoId"])),
        "pairEvidence": sorted(pairs, key=lambda item: item["photoIds"]),
        "intentConflicts": sorted(conflicts, key=lambda item: (item["folder"], item["photoIds"])),
        "supportStandard": {
            "implementation": "protection._independent plus saved-audit query/content exclusion",
            "independentEvidenceMaximumSimilarity": maximum,
            "queryRule": "different photo ID and content SHA; query dot reference <= maximum",
            "positiveSimilarityCutoff": None,
        },
        "limits": [
            "Score-only reconstruction and separate one-pass membership_decision probes, not an "
            "independent final routing replay; no placement or protection changes.",
            "Saved full-population measurements and centering reused unchanged; no model calls.",
            "Every query excluded from every reference set, including different-folder cores.",
            "Full frozen sets compete within the saved Artists/Prospects side; only top three shown.",
            "Confirmed references are training leave-one-out diagnostics, not held-out metrics.",
            "Same-not-reference positives, different negatives and uncertain choices never added "
            "to confirmed cores; uncertainty is neither positive nor negative.",
            "No pair-label propagation, thresholds inferred from labels, or conflict overrides.",
            "Shared independent support is audit evidence, not a positive resemblance threshold.",
            "Saved source protections, anchors, workflow and rejection safeguards retained; "
            "reference confirmation confers no placement protection.",
            "Empty withdrawn cores are unavailable, never replaced with an inherited fallback.",
            "Confirmed per-reference profiles exclude query photo ID and content SHA; raw-score "
            "ranking uses photo ID ties. Diagnostic representation only, never a nearest-neighbour "
            "router, threshold, inferred label or replacement for mean-score policy probes.",
        ],
    }
