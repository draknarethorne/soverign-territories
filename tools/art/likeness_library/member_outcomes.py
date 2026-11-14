"""Report-only member proposals: human intent is not a placement permission."""
import collections
import copy

from . import shadow


POSITIVE = {"reference", "same-not-reference"}
CHOICES = POSITIVE | {"different", "uncertain"}
SAFEGUARDS = (
    "protected", "anchor", "workflowSelected", "identityProtected",
    "metadataStale", "ambiguousPhotoId", "rejectionHistory",
)


def build(result, run):
    """Conserve receipt rows and expose independent reference/placement proposals."""
    photos = {row["photoId"]: row for row in run["photos"]}
    audit = {row["photoId"]: row for row in run["finalMembershipAudit"]["rows"]}
    rows = {row["photoId"]: row for row in result["rows"]}
    for name, indexed, original in (
        ("receipt", photos, run["photos"]),
        ("audit", audit, run["finalMembershipAudit"]["rows"]),
        ("trial", rows, result["rows"]),
    ):
        if len(indexed) != len(original) or not all(indexed):
            raise ValueError(f"{name} requires unique stable photo IDs")
    if photos.keys() != audit.keys() or photos.keys() != rows.keys():
        raise ValueError("member outcome receipt/audit/trial conservation differs")
    characters = {item["folder"]: item for item in result["characters"]}
    if len(characters) != len(result["characters"]):
        raise ValueError("duplicate character reference set")
    baseline, scored = collections.defaultdict(set), collections.defaultdict(set)
    for pid, row in audit.items():
        if row.get("coreMember"):
            baseline[pid].add(shadow.folder_for(row))
    for pid, folders in baseline.items():
        scored[pid].update(folder for folder in folders if folder not in characters)
    reference_owner = {}
    for folder, character in sorted(characters.items()):
        ids = character["referenceIds"]
        if len(set(ids)) != len(ids) or any(pid not in rows for pid in ids):
            raise ValueError(f"invalid character reference IDs: {folder}")
        expected = sorted(pid for pid, row in rows.items()
                          if row["choiceByCharacter"].get(folder) == "reference")
        if sorted(ids) != expected:
            raise ValueError(f"character reference IDs disagree with explicit intent: {folder}")
        for pid in ids:
            if pid in reference_owner:
                raise ValueError(f"reference assigned to multiple characters: {pid}")
            reference_owner[pid] = folder
            scored[pid] = {folder}

    adjacency = collections.defaultdict(list)
    seen = set()
    for pair in result["pairEvidence"]:
        ids = pair["photoIds"]
        if (len(ids) != 2 or ids[0] == ids[1] or any(pid not in rows for pid in ids)
                or pair["label"] not in {"same", "different", "uncertain"}):
            raise ValueError("invalid direct pair evidence for member outcomes")
        key = tuple(sorted(ids))
        if key in seen:
            raise ValueError("duplicate direct pair evidence for member outcomes")
        seen.add(key)
        for pid, other in (ids, ids[::-1]):
            adjacency[pid].append((other, pair["label"]))
    conflicts = collections.defaultdict(set)
    for conflict in result["intentConflicts"]:
        if conflict["folder"] not in characters or any(pid not in rows for pid in conflict["photoIds"]):
            raise ValueError("unknown character/photo in intent conflict")
        for pid in conflict["photoIds"]:
            conflicts[pid].add(conflict["folder"])

    def content_hash(pid):
        value = photos[pid].get("preparedSHA256") or photos[pid].get("sha256")
        if not value:
            raise ValueError(f"missing content hash for member evidence: {pid}")
        return value

    output = []
    for pid, row in sorted(rows.items()):
        saved = audit[pid]
        folder = shadow.folder_for(saved)
        if (saved["destination"] != photos[pid]["destination"]
                or folder != row["currentFolder"]
                or bool(saved["qualityEligible"]) != row["qualityEligible"]):
            raise ValueError(f"member outcome placement/quality binding differs: {pid}")
        choices = row["choiceByCharacter"]
        if any(char not in characters or choice not in CHOICES for char, choice in choices.items()):
            raise ValueError(f"invalid member character intent: {pid}")
        guards = {name: copy.deepcopy(saved[name]) for name in SAFEGUARDS}
        positives = sorted(char for char, choice in choices.items() if choice in POSITIVE)
        negative = sorted(char for char, choice in choices.items() if choice == "different")
        uncertain = sorted(char for char, choice in choices.items() if choice == "uncertain")
        evidence = []
        direct_conflicts = set(conflicts[pid])
        for char, character in sorted(characters.items()):
            pools = {label: [] for label in ("same", "different", "uncertain")}
            excluded = []
            refs = set(character["referenceIds"])
            for other, label in sorted(adjacency[pid]):
                if other not in refs:
                    continue
                if content_hash(other) == content_hash(pid):
                    excluded.append(other)
                else:
                    pools[label].append(other)
            if not any(pools.values()) and not excluded:
                continue
            mixed = bool(pools["same"] and pools["different"])
            if mixed or (char in positives and pools["different"]) or (char in negative and pools["same"]):
                direct_conflicts.add(char)
            evidence.append({
                "folder": char, "samePhotoIds": pools["same"],
                "differentPhotoIds": pools["different"], "uncertainPhotoIds": pools["uncertain"],
                "excludedSameContentPhotoIds": excluded,
                "state": "conflicting" if mixed else "same-pair-evidence" if pools["same"] else
                "different-pair-evidence" if pools["different"] else
                "uncertain" if pools["uncertain"] else "no-independent-pair-evidence",
            })
        intent_conflict = len(positives) > 1 or bool(direct_conflicts)
        probe = copy.deepcopy(row["confirmed"]["policyDecision"])
        if probe["decision"] not in {"move", "hold"}:
            raise ValueError(f"unsupported membership probe decision: {pid}")
        target, bucket = None, None
        if intent_conflict:
            action, reason = "hold", "conflicting human evidence; no automatic identity resolution"
        elif len(positives) == 1:
            target, bucket = positives[0], "gallery"
            action = "retain" if target == folder and saved["bucket"] == bucket else "recover"
            reason = "explicit character intent; not inferred from face scores or pair chains"
        elif folder in negative:
            action, reason = "reassess", "explicitly different from current character; destination unresolved"
        elif folder in uncertain:
            action, reason = "hold", "current-character intent uncertain; not a negative identity label"
        elif probe["decision"] == "move":
            destination = probe["destination"]
            parts = destination.rsplit("/", 1)
            if len(parts) != 2 or parts[1] not in {"gallery", "review"}:
                raise ValueError(f"unsupported membership probe destination: {pid}")
            target, bucket = parts
            direct_negative = any(
                item["folder"] == target and item["differentPhotoIds"] for item in evidence
            )
            if target in negative or target in uncertain or direct_negative:
                action, reason = "hold", "policy destination has negative or uncertain human evidence"
                target, bucket = None, None
            else:
                action, reason = "policy-proposal", "existing policy probe only; identity remains unverified"
        else:
            action, reason = "hold", "no explicit placement intent or accepted policy proposal"

        blockers = [name for name, value in guards.items() if value]
        if (target and target != folder
                and run["policy"]["categoryPolicies"][folder.split("/", 1)[0]]["identityProtectedByDefault"]):
            blockers.append("source-character-ownership")
        if not row["qualityEligible"]:
            blockers.append("quality-ineligible")
        if intent_conflict:
            blockers.append("human-evidence-conflict")
        if probe["decision"] == "hold":
            policy_agreement = "policy-holds"
        elif target and probe["destination"] == f"{target}/{bucket}":
            policy_agreement = "policy-matches-proposal"
        else:
            policy_agreement = "policy-proposes-other-destination"
        proposed_refs = set(scored[pid])
        blocked_refs = {}
        for char in sorted(proposed_refs):
            if len(positives) == 1 and char != positives[0]:
                blocked_refs[char] = "explicit positive intent belongs to another character"
            elif choices.get(char) in {"different", "uncertain", "same-not-reference"}:
                blocked_refs[char] = "explicit non-reference intent"
            elif intent_conflict:
                blocked_refs[char] = "conflicting human evidence"
            elif not row["qualityEligible"]:
                blocked_refs[char] = "quality-ineligible reference"
            elif any(guards[name] for name in ("metadataStale", "ambiguousPhotoId", "rejectionHistory")):
                blocked_refs[char] = "stale, ambiguous or rejected reference evidence"
            if char in blocked_refs:
                proposed_refs.remove(char)
        changes = []
        for char in sorted(baseline[pid] | proposed_refs):
            before, after = char in baseline[pid], char in proposed_refs
            if before == after:
                continue
            why = (
                "explicit confirmed reference intent" if after else
                blocked_refs[char] if char in blocked_refs else
                "confirmed reference belongs to another character" if positives and char not in positives else
                "explicit non-reference intent" if char in choices else
                "not selected in frozen confirmed set; identity not judged different"
            )
            changes.append({"folder": char, "before": before, "after": after, "reason": why})
        evidence_folders = set(choices) | {item["folder"] for item in evidence}
        if folder in characters:
            evidence_folders.add(folder)
        if target in characters:
            evidence_folders.add(target)
        gaps = []
        if not positives:
            gaps.append("no-explicit-positive-character-intent")
        if not row["qualityEligible"]:
            gaps.append("no-quality-eligible-measurement")
        if not evidence:
            gaps.append("no-direct-reference-pair-evidence")
        if not positives and probe["decision"] != "move":
            gaps.append("no-accepted-member-rule")
        output.append({
            "photoId": pid, "currentFolder": folder, "currentDestination": saved["destination"],
            "qualityEligible": row["qualityEligible"], "safeguards": guards,
            "characterIntent": dict(sorted(choices.items())),
            "reference": {
                "baselineFolders": sorted(baseline[pid]), "scoredFolders": sorted(scored[pid]),
                "proposedFolders": sorted(proposed_refs), "blockedAdmissions": blocked_refs,
                "changes": changes,
                "status": "confirmed-intent" if proposed_refs and any(
                    choices.get(char) == "reference" for char in proposed_refs
                ) else "provisional" if proposed_refs else "non-reference-in-proposal",
            },
            "placement": {
                "action": action, "targetFolder": target, "targetBucket": bucket,
                "reason": reason, "execution": "not-authorized",
                "blockers": blockers, "policyAgreement": policy_agreement,
            },
            "policyProbe": probe, "directReferenceEvidence": evidence,
            "frozenComparison": copy.deepcopy(row["confirmed"]),
            "characterEvidence": {
                char: copy.deepcopy(row["characterScores"][char]) for char in sorted(evidence_folders)
            },
            "evidenceGaps": gaps,
            "conflictingCharacters": sorted(direct_conflicts),
        })
    changes = [change for row in output for change in row["reference"]["changes"]]
    return {
        "schemaVersion": 1, "kind": "experimental-member-outcomes", "rows": output,
        "summary": {
            "photoCount": len(output),
            "placementActions": dict(sorted(collections.Counter(
                row["placement"]["action"] for row in output
            ).items())),
            "referenceAdditions": sum(change["after"] for change in changes),
            "referenceWithdrawals": sum(not change["after"] for change in changes),
            "conflictPhotoCount": sum("human-evidence-conflict" in row["placement"]["blockers"] for row in output),
            "executableMoves": 0,
        },
        "limits": [
            "Proposals only; no installed references, placements, protection or workflow selections changed.",
            "Explicit human character intent is not an installation permission or held-out accuracy.",
            "Unlabelled photos abstain unless the unchanged policy proposes a move; no new score thresholds.",
            "Direct pair evidence is query/content-excluded, never propagated or promoted to character truth.",
            "Scored references describe the earlier frozen comparison; blocked proposal admissions do not rescore that comparison.",
            "Reference withdrawal is independent of protected placement; unchanged non-character references remain provisional.",
            "No new reference growth or same-pass self-certification; complete routing replay remains required.",
        ],
    }
