"""Bounded group/member split diagnostics; resemblance never authorizes a union."""
import collections
import html
import json

import numpy as np

from . import candidate_replay, fragment_review, protection


MAX_MEMBERS = 500
MAX_PAIRS = 50_000


def build(candidate, run, vectors, packet, evaluation, result, ledger):
    photos = candidate_replay.index(run["photos"], "split receipt")
    current = candidate_replay.index(candidate["rows"], "split candidate")
    outcomes = candidate_replay.index(result["rows"], "split outcomes")
    audit = candidate_replay.index(run["finalMembershipAudit"]["rows"], "split audit")
    if not photos.keys() == current.keys() == outcomes.keys() == audit.keys():
        raise ValueError("split population conservation differs")
    cases = {case["id"]: case for case in packet["cases"]}
    identities = {item["folder"]: item for item in candidate["identities"]}
    notes = {item["caseId"]: item for item in evaluation["recommendations"]}
    labels = {}
    for pair in ledger["pairs"]:
        key = tuple(sorted(pair["photoIds"]))
        if key in labels or len(set(key)) != 2 or not set(key) <= photos.keys():
            raise ValueError("invalid or duplicate saved split pair")
        labels[key] = pair["label"]
    groups = collections.defaultdict(list)
    conflicts = []
    for decision in sorted(evaluation["identityAnswers"]["decisions"], key=lambda row: row["caseId"]):
        case = cases[decision["caseId"]]
        for pair in decision["pairs"]:
            key = tuple(sorted((case["photoId"], pair["referencePhotoId"])))
            if not set(key) <= photos.keys() or len(set(key)) != 2:
                raise ValueError("unknown/self split label")
            old = labels.get(key)
            label = pair["label"]
            if old is not None and old != label:
                conflicts.append({"photoIds": list(key), "previous": old, "incoming": label})
                label = "uncertain"
            labels[key] = label
        if decision["currentMatch"] == decision["targetMatch"] == "same":
            groups[tuple(sorted((case["currentFolder"], case["targetFolder"])))].append(case["id"])
    if not groups or len(groups) > 10:
        raise ValueError("split investigation requires one to ten explicitly supported group pairs")
    folders = {f for pair in groups for f in pair}
    members = {f: sorted(pid for pid, row in current.items() if row["currentFolder"] == f) for f in folders}
    used = {pid for ids in members.values() for pid in ids}
    reference_ids = {pid for folder in folders for pid in identities[folder]["referencePhotoIds"]}
    if not reference_ids <= photos.keys():
        raise ValueError("split reference absent from frozen population")
    if len(used) > MAX_MEMBERS:
        raise ValueError("split investigation member cap exceeded")
    normalized = {}
    for pid in sorted(used | reference_ids):
        if pid not in vectors:
            if audit[pid]["qualityEligible"]:
                raise ValueError("eligible split member missing measurement")
            continue
        vector = np.asarray(vectors[pid], dtype=float)
        if vector.ndim != 1 or not np.isfinite(vector).all() or not np.isclose(np.linalg.norm(vector), 1.):
            raise ValueError("invalid normalized split vector")
        normalized[pid] = vector
    pair_count = sum(len(members[a]) * len(members[b]) for a, b in groups)
    if pair_count > MAX_PAIRS:
        raise ValueError("split investigation cross-pair cap exceeded")
    def content(pid):
        value = photos[pid].get("preparedSHA256") or photos[pid].get("sha256")
        if not value:
            raise ValueError("split member content hash missing")
        return value
    def score(ids_a, ids_b):
        a = sorted({pid for pid in ids_a if pid in normalized})
        b = sorted({pid for pid in ids_b if pid in normalized})
        # Exclude content shared by either side from centroid comparison.
        shared = {content(pid) for pid in a} & {content(pid) for pid in b}
        a = list({content(pid): pid for pid in reversed(a) if content(pid) not in shared}.values())
        b = list({content(pid): pid for pid in reversed(b) if content(pid) not in shared}.values())
        if not a or not b:
            return None
        av = np.sum([normalized[p] for p in sorted(a)], axis=0)
        bv = np.sum([normalized[p] for p in sorted(b)], axis=0)
        if not np.linalg.norm(av) or not np.linalg.norm(bv):
            return None
        return round(float(av @ bv / (np.linalg.norm(av) * np.linalg.norm(bv))), 6)
    pairs = []
    display = set()
    for (left, right), case_ids in sorted(groups.items()):
        if left not in identities or right not in identities:
            raise ValueError("split folder missing from identity construction")
        refs = {f: sorted(identities[f]["referencePhotoIds"]) for f in (left, right)}
        cross = [
            float(normalized[a] @ normalized[b])
            for a in members[left] if a in normalized
            for b in members[right] if b in normalized and content(a) != content(b)
        ]
        directions = []
        for source, target in ((left, right), (right, left)):
            floor = run["policy"]["categoryPolicies"][target.split("/")[0]]["photoRouteMinimum"]
            minimum = run["policy"]["protection"]["automatic"]["minimumIndependentReferences"]
            rows = []
            for pid in members[source]:
                available = [rid for rid in refs[target] if rid in normalized and rid != pid and content(rid) != content(pid)]
                scores = sorted(((float(normalized[pid] @ normalized[rid]), rid) for rid in available),
                                key=lambda item: (-item[0], item[1])) if pid in normalized else []
                supporting = [rid for value, rid in scores if value >= floor]
                independent = protection._independent([
                    {"photoId": rid, "vector": normalized[rid], "sha256": content(rid)} for rid in supporting
                ], run["policy"])
                direct = [{"photoId": rid, "label": labels[tuple(sorted((pid, rid)))]}
                          for rid in members[target] if tuple(sorted((pid, rid))) in labels]
                blockers = []
                if pid not in normalized:
                    blockers.append("missing-face-measurement")
                if not audit[pid]["qualityEligible"]:
                    blockers.append("saved-quality-gate")
                if len(independent) < minimum:
                    blockers.append("insufficient-independent-opposite-references")
                if any(item["label"] in ("different", "uncertain") for item in direct):
                    blockers.append("direct-different-or-uncertain-pair")
                raw = photos[pid]
                saved = audit[pid]
                state = outcomes[pid]
                specific = next((r for r in state["topCandidates"] if r["folder"] == target), None)
                rows.append({
                    "photoId": pid, "currentFolder": source, "comparedFolder": target,
                    "currentDestination": raw["destination"], "source": raw.get("source"),
                    "crossReferenceCentroidScore": score([pid], available),
                    "bestOppositePhotoId": scores[0][1] if scores else None,
                    "bestOppositePairScore": round(scores[0][0], 6) if scores else None,
                    "independentOppositeSupport": len(independent), "requiredSupport": minimum,
                    "routeFloor": floor, "diagnosticBlockers": blockers,
                    "directPairEvidence": direct,
                    "candidateComparedGroupEvidence": specific,
                    "candidateDecision": state["candidateDecision"],
                    "candidateDecisionComparedFolder": state["tentativeAssociationFolder"],
                    "candidateDecisionAppliesToThisPair": state["tentativeAssociationFolder"] == target,
                    "savedHistory": {key: raw.get(key) for key in (
                        "oldFolder", "retainedCast", "releasedCast", "castSeedScore", "castSeedThreshold",
                        "castSeedReason", "initialBestCast", "initialBestCastScore", "initialCastMargin",
                        "reason", "bestMatch", "bestScore", "clusterId", "identityNameEvidence",
                    )},
                    "savedFinalDecision": saved.get("refinementDecision"),
                    "protection": {key: saved[key] for key in (
                        "protected", "anchor", "workflowSelected", "identityProtected", "qualityEligible",
                        "metadataStale", "rejectionHistory",
                    )},
                    "execution": "not-authorized", "reconsiderable": True,
                })
            ranked = sorted(rows, key=lambda row: (
                row["crossReferenceCentroidScore"] is None,
                -(row["crossReferenceCentroidScore"] or 0), row["photoId"],
            ))
            selected = {
                pid for cid in case_ids
                for pid in [cases[cid]["photoId"], cases[cid]["currentReferenceId"], *cases[cid]["targetReferenceIds"]]
                if pid in members[source]
            }
            # Include scored strongest and weakest members; no hidden truncation in numerical rows.
            if ranked:
                selected.update(row["photoId"] for row in (ranked[0], ranked[-1]))
            display.update(pid for pid in selected if pid in normalized)
            directions.append({
                "sourceFolder": source, "targetFolder": target, "memberCount": len(rows),
                "referenceCount": len(refs[target]), "members": rows,
                "crossSupportOnlyCount": sum(not row["diagnosticBlockers"] for row in rows),
                "missingMeasurementCount": sum(row["photoId"] not in normalized for row in rows),
                "originalFolders": dict(sorted(collections.Counter(
                    row["savedHistory"]["oldFolder"] or "not recorded" for row in rows).items())),
                "savedFormationReasons": dict(sorted(collections.Counter(
                    row["savedHistory"]["reason"] or "not recorded" for row in rows).items())),
                "candidateHoldReasons": dict(sorted(collections.Counter(
                    row["candidateDecision"]["reason"] for row in rows).items())),
            })
        comment_rows = [{"caseId": cid, **notes[cid]} for cid in sorted(case_ids) if cid in notes]
        pair_labels = [{"photoIds": list(key), "label": label} for key, label in sorted(labels.items())
                       if (key[0] in members[left] and key[1] in members[right])
                       or (key[1] in members[left] and key[0] in members[right])]
        pairs.append({
            "folders": [left, right], "caseIds": sorted(case_ids), "userComments": comment_rows,
            "referenceLocations": {
                f: [{"photoId": pid, "currentFolder": current[pid]["currentFolder"],
                     "construction": identities[f]["referenceEvidence"]["construction"]}
                    for pid in refs[f]] for f in (left, right)
            },
            "allMemberCentroidScore": score(members[left], members[right]),
            "frozenReferenceCentroidScore": score(refs[left], refs[right]),
            "crossMemberPairDistribution": {
                "count": len(cross),
                "minimum": round(min(cross), 6) if cross else None,
                "median": round(float(np.median(cross)), 6) if cross else None,
                "maximum": round(max(cross), 6) if cross else None,
            },
            "knownCrossPairs": pair_labels, "directions": directions,
            "wholeGroupCombination": "not-established",
        })
    if len(display) > 40:
        raise ValueError("split representative display cap exceeded; explicit scope revision required")
    return {
        "schemaVersion": 1, "kind": "split-group-investigation",
        "evaluationSHA256": fragment_review.digest(evaluation),
        "packetSHA256": packet["packetSHA256"], "pairs": pairs, "conflicts": conflicts,
        "usedPhotoIds": sorted(display),
        "summary": {
            "groupPairCount": len(pairs), "uniqueGroupCount": len(folders),
            "uniqueMemberCount": len(used), "directedMemberRows": sum(
                d["memberCount"] for pair in pairs for d in pair["directions"]),
            "crossPairCount": sum(pair["crossMemberPairDistribution"]["count"] for pair in pairs),
            "displayPhotoCount": len(display), "executedMoves": 0,
        },
        "limits": [
            "Group centroid similarity is resemblance evidence, not identity truth or an automatic merge threshold.",
            "All group members have numerical rows; thumbnails show bounded labelled/strong/weak representatives only.",
            "Cross-support counts use existing route floors/independence gates only; rival competition, ownership, coherence and protection still apply.",
            "A query's Same/Both label does not certify unseen members; direct different/uncertain evidence is never propagated.",
            "Recorded initial routing, source and final decisions describe history; saved evidence alone may not prove every original split cause.",
            "All-member/reference centroids here are explicitly defined diagnostics, not claimed parity with installed Gallery core/render scores.",
            "Reference sets stay frozen; no transitive union, inferred kinship, family type, threshold change, model calls, intake or installation.",
            "Authored preferred owner in comments is intent to investigate, not blanket admission of every folder member.",
        ],
    }


def render(result, images):
    esc = lambda value: html.escape(str(value), quote=True)
    def number(value):
        return "unavailable" if value is None else f"{value:.3f}"
    cards = []
    for pair in result["pairs"]:
        left, right = pair["folders"]
        body = f"<h2>{esc(left)} &harr; {esc(right)}</h2>"
        body += "<p class=notice><strong>No whole-group combination established; nothing moves.</strong></p>"
        body += (f"<p>All-member centroid: <b>{number(pair['allMemberCentroidScore'])}</b> | "
                 f"Frozen-reference centroid: <b>{number(pair['frozenReferenceCentroidScore'])}</b></p>"
                 f"<p>Cross-photo pairs: {esc(pair['crossMemberPairDistribution'])}. "
                 "Scores are similarities, not probabilities or a merge decision.</p>")
        external = [(folder, row) for folder, refs in pair["referenceLocations"].items()
                    for row in refs if row["currentFolder"] != folder]
        if external:
            body += "<p class=notice>Confirmed/reference identity and installed folder already differ:</p><ul>"
            for folder, row in external:
                body += (f"<li>{esc(row['photoId'])}: reference for {esc(folder)}, currently in "
                         f"{esc(row['currentFolder'])} ({esc(row['construction'])})</li>")
            body += "</ul>"
        for comment in pair["userComments"]:
            body += f"<blockquote>{esc(comment['caseId'])} ({esc(comment['judgment'])}): {esc(comment['reason'])}</blockquote>"
        for direction in pair["directions"]:
            body += (f"<h3>{esc(direction['sourceFolder'])}: {direction['memberCount']} members</h3>"
                     f"<p>{direction['crossSupportOnlyCount']} clear the diagnostic cross-support/veto checks "
                     f"against {direction['referenceCount']} frozen opposite references. "
                     "This is NOT a count approved to move. All member rows are included below.</p><div class=photos>")
            for row in direction["members"]:
                pid = row["photoId"]
                if pid not in images:
                    continue
                record = images[pid]
                body += (f"<figure><a href=\"{esc(record['href'])}\" target=_blank rel=noopener>"
                         f"<img src=\"{esc(record['full'])}\" alt=\"{esc(pid)}\" loading=lazy></a>"
                         f"<figcaption>{esc(pid)}<br>Opposite refs: {number(row['crossReferenceCentroidScore'])}"
                         f"<br>Independent support: {row['independentOppositeSupport']}/{row['requiredSupport']}"
                         f"<br>{esc('; '.join(row['diagnosticBlockers']) or 'Cross-support checks clear ONLY')}"
                         "</figcaption></figure>")
            body += "</div><details><summary>Every member: evidence, history, safeguards and held reasons</summary>"
            for row in direction["members"]:
                compared = row["candidateComparedGroupEvidence"]
                comparison = (
                    f"Saved best subgroup for this opposite group: {number(compared['subgroupScore'])}; "
                    f"independent support {compared['supportCount']}. "
                    if compared else "This opposite group is not in the saved top three subgroup suggestions. "
                )
                body += (f"<details><summary>{esc(row['photoId'])}: opposite refs "
                         f"{number(row['crossReferenceCentroidScore'])}, support {row['independentOppositeSupport']}, "
                         f"{esc(row['candidateDecision']['decision'])} in candidate</summary>"
                         f"<p>{esc(comparison)}</p>"
                         f"<p>Candidate compares {esc(row['candidateDecisionComparedFolder'])}: "
                         f"{esc(row['candidateDecision']['reason'])}. "
                         f"Applies to this group pair: {esc(row['candidateDecisionAppliesToThisPair'])}.</p>"
                         "<p>Recorded original formation and later routing:</p>"
                         f"<p>{esc(row['savedHistory']['reason'])}</p>"
                         "<details><summary>Complete numerical/provenance record</summary>"
                         f"<pre>{esc(json.dumps(row, indent=2))}</pre></details>")
                body += "</details>"
            body += "</details>"
            body += ("<h4>What the saved run actually recorded</h4>"
                     "<p>Original folder counts (before this rebase): "
                     f"{esc(direction['originalFolders'])}</p>"
                     "<p>Formation/routing records describe the earlier run, not the current diagnostic. "
                     "A high old group/core score is not the same metric as individual cross-photo support.</p>"
                     f"<pre>{esc(json.dumps(direction['savedFormationReasons'], indent=2))}</pre>"
                     "<p>Current candidate reasons across these members (may refer to a different best competitor):</p>"
                     f"<pre>{esc(json.dumps(direction['candidateHoldReasons'], indent=2))}</pre>")
        cards.append("<section>" + body + "</section>")
    return (
        "<!doctype html><html lang=en><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>Why are these identities split?</title><style>"
        "body{font:16px system-ui;background:#151b23;color:#e5edf6;margin:20px;line-height:1.5}"
        "main{max-width:1300px;margin:auto}p,summary,blockquote,figcaption{overflow-wrap:anywhere}"
        ".notice,blockquote{background:#283445;padding:12px}.photos{display:grid;"
        "grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:16px}"
        "figure{margin:0;min-width:0}img{width:100%;height:330px;object-fit:contain}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere}details{margin:12px 0}a{color:#a6d9ff}"
        "</style><main><h1>Why are these identities split?</h1>"
        "<p>Your returned feedback supports these comparisons as the same intended person. "
        "This investigation checks both directions and every current member, not only the reviewed query. "
        "It does not assume all photos in either folder are that person.</p>"
        "<p>Use group scores to locate a split worth investigating, then inspect member coverage, "
        "exceptions and original routing. A high average can hide mixed people. "
        "Your Nyxene preference is retained verbatim in the comments, not silently installed.</p>"
        f"<pre>{esc(json.dumps(result['summary'], indent=2))}</pre>"
        + "".join(cards) + "<h2>Limits and next decision</h2><ul>"
        + "".join("<li>" + esc(line) + "</li>" for line in result["limits"])
        + "</ul><p>No new questionnaire is required. Flag specific mismatched images or canonical-owner "
        "preferences if useful; do not approve a whole-folder move based on this score.</p>"
        '<a href="splits.json">Complete numerical member evidence</a></main></html>'
    )
