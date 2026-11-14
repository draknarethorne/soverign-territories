"""Connect frozen subgroup evidence to existing routing gates, without installation."""
import collections
import copy

from . import fragment_review, refinement, shadow


def index(rows, name):
    result = {row["photoId"]: row for row in rows}
    if len(result) != len(rows) or not all(result):
        raise ValueError(f"{name} requires unique stable photo IDs")
    return result


def repaired_references(candidate, ledger):
    result = copy.deepcopy(candidate)
    identities = {item["folder"]: item for item in result["identities"]}
    if len(identities) != len(result["identities"]):
        raise ValueError("duplicate candidate identity")
    for proposal in ledger["referenceProposals"]:
        if proposal["referenceUse"] != "withdraw-in-shadow" or not proposal["wasReference"]:
            continue
        identity = identities[proposal["folder"]]
        if proposal["photoId"] not in identity["referencePhotoIds"]:
            raise ValueError("withdrawal absent from frozen reference set")
        if identity.get("referenceEvidence", {}).get("construction") == "confirmed-character-intent":
            raise ValueError("cannot withdraw confirmed-character reference")
        identity["referencePhotoIds"].remove(proposal["photoId"])
    return result


def policy_rows(candidate, evidence, run, ledger):
    photos = index(run["photos"], "receipt")
    saved = index(run["finalMembershipAudit"]["rows"], "audit")
    rows = index(evidence["rows"], "subgroup evidence")
    original = index(candidate["rows"], "candidate")
    if not photos.keys() == saved.keys() == rows.keys() == original.keys():
        raise ValueError("candidate replay population differs")
    identity_folders = {item["folder"] for item in candidate["identities"]}
    labels = collections.defaultdict(dict)
    for pair in ledger["pairs"]:
        a, b = pair["photoIds"]
        if a not in photos or b not in photos or a == b or pair["label"] not in ("same", "different", "uncertain"):
            raise ValueError("invalid candidate safety pair")
        labels[a][b] = labels[b][a] = pair["label"]
    unresolved = {row["photoId"] for row in ledger["unresolved"]}
    output = []
    for pid, row in sorted(rows.items()):
        audit = saved[pid]
        if (audit["destination"] != photos[pid]["destination"]
                or shadow.folder_for(audit) != row["currentFolder"]
                or original[pid]["currentFolder"] != row["currentFolder"]):
            raise ValueError("candidate replay placement binding differs")
        own = row["own"]
        rivals, seen = [], set()
        for rival in row["topCandidates"]:
            if rival["folder"] not in identity_folders:
                raise ValueError("unknown candidate destination")
            if rival["subgroupScore"] is not None and rival["folder"] not in seen:
                rivals.append(rival)
                seen.add(rival["folder"])
        top = rivals[0] if rivals else None
        own_score = own["subgroupScore"] if own else None
        probe = copy.deepcopy(audit)
        probe.update(
            ownScore=own_score, rivals=[{"folder": r["folder"], "score": r["subgroupScore"]} for r in rivals],
            higherRival=bool(top and own_score is not None and top["subgroupScore"] > own_score),
            refinementTarget={
                "folder": top["folder"], "score": top["subgroupScore"],
                "independentSupport": top["supportCount"],
                "identityProtected": run["policy"]["categoryPolicies"][top["folder"].split("/")[0]]["identityProtectedByDefault"],
            } if top else None,
        )
        decision = refinement.membership_decision(probe, run["policy"])
        safety = []
        if top:
            safety = sorted({
                labels[pid][ref] for ref in top["referencePhotoIds"]
                if labels[pid].get(ref) in ("different", "uncertain")
            })
        extra_holds = []
        if pid in unresolved:
            extra_holds.append("explicit Neither: owner unresolved")
        if row.get("hold"):
            extra_holds.append(row["hold"])
        if safety:
            extra_holds.append("direct " + "/".join(safety) + " reference evidence")
        if top and top["blockers"]:
            extra_holds.extend(top["blockers"])
        if extra_holds:
            decision = {"decision": "hold", "reason": "; ".join(sorted(set(extra_holds))),
                        "sharedPolicyDecision": decision}
        target = top["folder"] if top else None
        baseline = audit.get("refinementDecision") or {"decision": "hold", "reason": audit["reason"]}
        output.append({
            "photoId": pid, "currentFolder": row["currentFolder"],
            "currentDestination": photos[pid]["destination"],
            "baselineDecision": baseline, "candidateDecision": decision,
            "proposedDestination": decision.get("destination"),
            "tentativeAssociationFolder": target,
            "own": own, "topCandidates": rivals,
            "referenceWithdrawals": [
                p["folder"] for p in ledger["referenceProposals"]
                if p["photoId"] == pid and p["referenceUse"] == "withdraw-in-shadow"
            ],
            "family": "unassigned-identity-assessment-first",
            "execution": "not-authorized", "reconsiderable": True,
            "placement": "unchanged",
        })
    return output


def compare(candidate, baseline, repaired, run, ledger):
    before = policy_rows(candidate, baseline, run, ledger)
    after = policy_rows(candidate, repaired, run, ledger)
    previous = index(before, "reference control")
    for row in after:
        old = previous[row["photoId"]]
        row["referenceControlDecision"] = old["candidateDecision"]
        row["referenceControlAssociation"] = old["tentativeAssociationFolder"]
        row["changedByReferenceRepair"] = (
            row["candidateDecision"] != old["candidateDecision"]
            or row["tentativeAssociationFolder"] != old["tentativeAssociationFolder"]
        )
    return {
        "schemaVersion": 1, "kind": "connected-candidate-replay", "rows": after,
        "summary": {
            "photoCount": len(after),
            "policyMoveProposals": sum(r["candidateDecision"]["decision"] == "move" for r in after),
            "heldCount": sum(r["candidateDecision"]["decision"] == "hold" for r in after),
            "referenceRepairChangedOutcomes": sum(r["changedByReferenceRepair"] for r in after),
            "executedMoves": 0, "familyAssignments": 0,
        },
        "limits": [
            "One frozen diagnostic pass through shared membership_decision; not converged refinement or a completed rebase.",
            "Scoring receives zero direct pair labels; confirmed character references and three explicit repairs remain development inputs.",
            "Negative/uncertain direct labels veto separately; positive answers never generate a destination.",
            "All original competitors retained; query/equal-content exclusion and unchanged saved policy apply.",
            "No reference growth, transitive association, accepted appearance-series detector or family classification.",
            "Move proposals are non-executable; saved protection, quality, workflow and rejection gates remain active.",
            "Context is diagnostic only; no new model, threshold, fusion weight, installed membership or intake.",
        ],
    }


def packet(result, candidate, run, vectors, ledger, source_packet, *, max_photos=40):
    """Prefer new source/target identities and show repair changes, qualified and held controls."""
    photos = index(run["photos"], "receipt")
    identities = {item["folder"]: item for item in candidate["identities"]}
    reviewed = {pid for pair in ledger["pairs"] for pid in pair["photoIds"]}
    known_folders = {case[k] for case in source_packet["cases"] for k in ("currentFolder", "targetFolder")}
    cases, used, sources = [], set(), set()

    def eligible(row):
        return bool(row["topCandidates"]) and row["photoId"] not in reviewed

    ordered = sorted((r for r in result["rows"] if eligible(r)), key=lambda r: (
        r["currentFolder"] in known_folders or r["tentativeAssociationFolder"] in known_folders,
        not r["changedByReferenceRepair"],
        r["candidateDecision"]["decision"] != "move", r["photoId"],
    ))
    for row in ordered:
        pid, folder = row["photoId"], row["currentFolder"]
        if folder in sources or folder not in identities:
            continue
        top = row["topCandidates"][0]
        def score(ref):
            return float(vectors[pid] @ vectors[ref])
        own = [
            ref for ref in identities[folder]["referencePhotoIds"]
            if ref in vectors and ref != pid
            and photos[ref]["preparedSHA256"] != photos[pid]["preparedSHA256"]
        ]
        refs = top["referencePhotoIds"]
        if not own or len(refs) < 2:
            continue
        own_ref = min(own, key=lambda ref: (-score(ref), ref))
        target_refs = list(dict.fromkeys([
            min(refs, key=lambda ref: (-score(ref), ref)),
            min(refs, key=lambda ref: (score(ref), ref)),
        ]))
        ids = {pid, own_ref, *target_refs}
        if len(used | ids) > max_photos:
            continue
        sources.add(folder)
        used.update(ids)
        decision = row["candidateDecision"]
        cases.append({
            "id": f"candidate-{len(cases)+1:02d}", "photoId": pid, "currentFolder": folder,
            "targetFolder": top["folder"], "currentReferenceId": own_ref, "targetReferenceIds": target_refs,
            "selectionReason": (
                f"Installed: {row['currentDestination']}. "
                f"Candidate: {decision.get('destination', 'KEEP CURRENT / HOLD')}. "
                f"Reason: {decision['reason']}. "
                f"Reference-repair effect: {'changed' if row['changedByReferenceRepair'] else 'unchanged'}. "
                "Association examples are not whole-folder or move approval."
            ),
            "priorJudgment": None, "developmentFixture": False,
            "faceEvidence": top, "baselineTarget": row["referenceControlAssociation"],
            "candidateDecision": decision,
            "evaluationScope": "new-query-development-diagnostic-not-independent-holdout",
        })
        if len(cases) >= 10:
            break
    if len(cases) < 6 or not 30 <= len(used) <= max_photos:
        raise ValueError(f"insufficient new visual coverage: {len(cases)} cases / {len(used)} photos")
    result_packet = {
        "schemaVersion": 1, "kind": "identity-fragment-review",
        "candidateSHA256": fragment_review.digest(candidate),
        "evidenceSHA256": fragment_review.digest(result),
        "cases": cases, "usedPhotoIds": sorted(used),
        "summary": {"caseCount": len(cases), "distinctPhotoCount": len(used),
                    "developmentCaseCount": 0, "unreviewedQueryCount": len(cases)},
        "limits": result["limits"] + [
            "New queries exclude all saved direct-pair photo IDs; references/related identities may still overlap development.",
            "Packet answers judge identity compatibility and exact pairs, not permission to move or install.",
        ],
    }
    result_packet["packetSHA256"] = fragment_review.digest(result_packet)
    return result_packet
