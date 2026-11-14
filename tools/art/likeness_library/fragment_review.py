"""Identity-fragment review: exact example labels, never whole-folder truth."""
import collections
import hashlib
import json

import numpy as np


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def ingest(candidate, answers):
    if (not isinstance(answers, dict)
            or set(answers) != {"schemaVersion", "kind", "candidateSHA256", "assessments"}
            or type(answers["schemaVersion"]) is not int or answers["schemaVersion"] != 1
            or answers["kind"] != "realignment-hypothesis-assessments"
            or answers["candidateSHA256"] != digest(candidate)
            or not isinstance(answers["assessments"], list)):
        raise ValueError("identity assessment schema/candidate binding mismatch")
    rows = {row["photoId"]: row for row in candidate["rows"]}
    seen = set()
    for item in answers["assessments"]:
        if (not isinstance(item, dict) or set(item) != {"photoId", "candidateFolder", "judgment"}
                or not isinstance(item["photoId"], str) or item["photoId"] not in rows
                or item["photoId"] in seen or not isinstance(item["judgment"], str)
                or item["judgment"] not in {"support", "reject", "uncertain"}
                or not rows[item["photoId"]]["candidateFolder"]
                or item["candidateFolder"] != rows[item["photoId"]]["candidateFolder"]):
            raise ValueError("invalid, duplicate or wrong-target identity assessment")
        seen.add(item["photoId"])
    return {
        "counts": dict(sorted(collections.Counter(a["judgment"] for a in answers["assessments"]).items())),
        "observations": sorted(answers["assessments"], key=lambda a: a["photoId"]),
        "interpretation": "Identity compatibility only; no preferred placement, pair labels or reference purity inferred.",
    }


def build(candidate, evidence, run, vectors, prior, *, max_photos=40):
    if type(max_photos) is not int or not 30 <= max_photos <= 40:
        raise ValueError("fragment review requires a 30-40 distinct-photo budget")
    old = {row["photoId"]: row for row in candidate["rows"]}
    photos = {row["photoId"]: row for row in run["photos"]}
    new = {row["photoId"]: row for row in evidence["rows"]}
    if set(new) != set(old) or set(new) != set(photos):
        raise ValueError("fragment review candidate conservation differs")
    identities = {item["folder"]: item for item in candidate["identities"]}
    labelled = {item["photoId"]: item for item in prior["observations"]}
    cases, used, selected = [], set(), set()

    def content(pid):
        value = photos[pid].get("preparedSHA256") or photos[pid].get("sha256")
        if not value:
            raise ValueError("review requires content-bound photos")
        return value

    def score(a, b):
        av, bv = np.asarray(vectors[a]), np.asarray(vectors[b])
        return float(av @ bv / (np.linalg.norm(av) * np.linalg.norm(bv)))

    def add(pid, target, reason, *, outside=False):
        key = (pid, target)
        if key in selected or pid not in vectors or target == old[pid]["currentFolder"]:
            return
        current = old[pid]["currentFolder"]
        refs = [
            rid for rid in identities[target]["referencePhotoIds"]
            if rid != pid and rid in vectors and content(rid) != content(pid)
        ]
        own = [
            rid for rid in identities[current]["referencePhotoIds"]
            if rid != pid and rid in vectors and content(rid) != content(pid)
        ]
        if not refs or not own:
            return
        # Inspect a group's heterogeneous edge as well as a strong example.
        close = min(refs, key=lambda rid: (-score(pid, rid), rid))
        edge = min(refs, key=lambda rid: (score(close, rid), rid))
        reference_ids = list(dict.fromkeys([close, edge]))
        own_id = min(own, key=lambda rid: (-score(pid, rid), rid))
        ids = {pid, own_id, *reference_ids}
        if len(used | ids) > max_photos:
            return
        selected.add(key)
        used.update(ids)
        row = new[pid]
        target_evidence = next((item for item in row["topCandidates"] if item["folder"] == target), None)
        cases.append({
            "id": f"fragment-{len(cases) + 1:02d}", "photoId": pid,
            "currentFolder": current, "targetFolder": target,
            "currentReferenceId": own_id, "targetReferenceIds": reference_ids,
            "selectionReason": reason, "priorJudgment": labelled.get(pid),
            "developmentFixture": pid in labelled, "additionalUserAssociation": outside,
            "faceEvidence": target_evidence,
            "baselineTarget": old[pid]["candidateFolder"],
            "boundary": "Example labels are photo pairs only; identity answers do not approve placement or all members.",
        })

    # Known mixed references and rejected controls are deliberate development fixtures.
    flags = {"Prospects/Zoe Mallory", "Potentials/Viola Lujan", "Models/Ruby Vale",
             "Prospects/Xena Eden", "Prospects/Francesca Oakes"}
    for item in prior["observations"]:
        if item["candidateFolder"] in flags:
            add(item["photoId"], item["candidateFolder"], "Reported mixed references / prior development control")
    for source, target in (
        ("Models/Quinn Duval", "Sisters/Drakness"),
        ("Models/Mara Savannah", "Sisters/Drakniss"),
        ("Models/Sabine Santos", "Sisters/Draknora"),
    ):
        if source not in identities or target not in identities:
            raise ValueError(f"expected fragmentation fixture missing: {source} / {target}")
        source_ids = [r["photoId"] for r in candidate["rows"] if r["currentFolder"] == source and r["photoId"] in vectors]
        if source_ids:
            # Reverse-direction member check, not a folder merge or universal identity label.
            pid = min(source_ids, key=lambda p: (
                -max((score(p, rid) for rid in identities[target]["referencePhotoIds"] if rid != p), default=-1), p,
            ))
            add(pid, target, "Reverse-direction cast-fragment check; association does not certify every member", outside=True)
    seen_sources = {case["currentFolder"] for case in cases}
    for row in sorted(new.values(), key=lambda row: row["photoId"]):
        pid = row["photoId"]
        if pid in labelled or row["currentFolder"] in seen_sources or not row["topCandidates"]:
            continue
        target = row["topCandidates"][0]["folder"]
        before = len(cases)
        add(pid, target, "Unreviewed source identity; strongest coherent-reference rival")
        if len(cases) != before:
            seen_sources.add(row["currentFolder"])
    if len(cases) < 6 or not 30 <= len(used) <= max_photos:
        raise ValueError(f"cannot fill bounded review coverage: {len(cases)} cases / {len(used)} photos")
    packet = {
        "schemaVersion": 1, "kind": "identity-fragment-review",
        "candidateSHA256": digest(candidate), "evidenceSHA256": digest(evidence),
        "cases": cases, "usedPhotoIds": sorted(used),
        "summary": {
            "caseCount": len(cases), "distinctPhotoCount": len(used),
            "developmentCaseCount": sum(case["developmentFixture"] for case in cases),
            "unreviewedQueryCount": sum(not case["developmentFixture"] for case in cases),
        },
        "limits": [
            "Selected diagnostic coverage, not random precision or independent held-out accuracy.",
            "Prior answers remain identity compatibility; no implied pair labels or preferred folder.",
            "Reference examples are frozen selections, not certified clean; exact exceptions are labelable.",
            "Appearance/context features cannot establish identity or override different/uncertain labels.",
            "No group merge, reference admission, folder naming, placement, protection or workflow change.",
        ],
    }
    packet["packetSHA256"] = digest(packet)
    return packet


def validate_answers(packet, answers):
    if (not isinstance(answers, dict)
            or set(answers) != {"schemaVersion", "kind", "packetSHA256", "decisions"}
            or type(answers["schemaVersion"]) is not int or answers["schemaVersion"] != 1
            or answers["kind"] != "identity-fragment-answers"
            or answers["packetSHA256"] != packet["packetSHA256"]
            or not isinstance(answers["decisions"], list)):
        raise ValueError("fragment answer schema/packet mismatch")
    cases = {item["id"]: item for item in packet["cases"]}
    seen = set()
    for item in answers["decisions"]:
        if (not isinstance(item, dict)
                or set(item) != {"caseId", "currentMatch", "targetMatch", "pairs", "context"}
                or not isinstance(item["caseId"], str) or item["caseId"] not in cases
                or item["caseId"] in seen
                or item["currentMatch"] not in ("same", "different", "uncertain")
                or item["targetMatch"] not in ("same", "different", "uncertain")
                or item["context"] not in ("helpful", "misleading", "unavailable", "uncertain")
                or not isinstance(item["pairs"], list)):
            raise ValueError("invalid or duplicate fragment answer")
        seen.add(item["caseId"])
        case = cases[item["caseId"]]
        expected = {case["currentReferenceId"], *case["targetReferenceIds"]}
        pair_seen = set()
        for pair in item["pairs"]:
            if (not isinstance(pair, dict) or set(pair) != {"referencePhotoId", "label"}
                    or not isinstance(pair["referencePhotoId"], str)
                    or pair["referencePhotoId"] not in expected or pair["referencePhotoId"] in pair_seen
                    or pair["label"] not in ("same", "different", "uncertain")):
                raise ValueError("invalid or duplicate exact reference-pair answer")
            pair_seen.add(pair["referencePhotoId"])
        if pair_seen != expected:
            raise ValueError("fragment answer is missing exact reference-pair labels")
    return {"answered": len(seen), "total": len(cases)}
