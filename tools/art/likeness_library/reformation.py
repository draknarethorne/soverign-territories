"""Opt-in cross-folder person state construction; never an installation plan."""
import collections

import numpy as np

from . import candidate_replay, fragment_evidence, fragment_review, protection, shadow


MAX_PHOTOS = 5000
MAX_PASSES = 4
SAFETY_FIELDS = (
    "ambiguousPhotoId", "metadataStale", "protected", "anchor",
    "workflowSelected", "identityProtected", "rejectionHistory",
)


def _id(kind, members):
    return kind + ":" + fragment_review.digest(sorted(members))[:20]


class _FrozenScores:
    def __init__(self, vectors):
        self.ids = tuple(sorted(vectors))
        self.indices = {pid: index for index, pid in enumerate(self.ids)}
        if len(self.ids) ** 2 > fragment_evidence.MAX_PAIR_OPERATIONS:
            raise ValueError("reformation similarity matrix exceeds operation cap")
        matrix = np.asarray([vectors[pid] for pid in self.ids])
        self.values = matrix @ matrix.T if self.ids else np.empty((0, 0))
        self.budget = fragment_evidence._PairBudget()

    def get(self, left, right):
        if left == right:
            raise ValueError("reformation cannot use self similarity as independent evidence")
        return self.values[self.indices[left], self.indices[right]]


def build(candidate, run, vectors, ledger, *, progress=None, assess_membership=False):
    photos = candidate_replay.index(run["photos"], "reformation photos")
    audit = candidate_replay.index(run["finalMembershipAudit"]["rows"], "reformation audit")
    previous = candidate_replay.index(candidate["rows"], "reformation baseline")
    if not photos.keys() == audit.keys() == previous.keys() or len(photos) > MAX_PHOTOS:
        raise ValueError("reformation population differs or exceeds cap")
    settings = run["policy"]
    categories = settings["categoryPolicies"]
    general_rules = [
        rules for rules in categories.values()
        if rules["automaticPhotoRoutingEnabled"] and not rules["identityProtectedByDefault"]
    ]
    if not general_rules:
        raise ValueError("reformation needs an enabled non-character routing policy")
    floor = max(r["photoRouteMinimum"] for r in general_rules)
    margin = max(r["photoRouteMargin"] for r in general_rules)
    minimum = settings["protection"]["automatic"]["minimumIndependentReferences"]
    threshold = settings["identityActions"]["identityClusterMinimumSimilarity"]
    normalized, hashes, holds = {}, {}, {}
    identities = {item["folder"]: item for item in candidate["identities"]}
    if len(identities) != len(candidate["identities"]):
        raise ValueError("duplicate reformation baseline identity")
    for pid in sorted(photos):
        raw, saved, old = photos[pid], audit[pid], previous[pid]
        required = {*SAFETY_FIELDS, "qualityEligible", "bucket", "destination"}
        if not required <= saved.keys():
            raise ValueError(f"reformation missing saved safeguards: {pid}")
        if raw["destination"] != saved["destination"] or shadow.folder_for(saved) != old["currentFolder"]:
            raise ValueError("reformation placement binding differs")
        digest = raw.get("preparedSHA256") or raw.get("sha256")
        if not isinstance(digest, str) or not digest:
            raise ValueError("reformation requires content hashes")
        hashes[pid] = digest
        if pid in vectors:
            normalized[pid] = fragment_evidence._normalize_vector(vectors[pid], pid)
        elif saved["qualityEligible"]:
            raise ValueError(f"eligible reformation photo missing vector: {pid}")
        reasons = [field for field in SAFETY_FIELDS if saved[field]]
        if not saved["qualityEligible"]:
            reasons.append("quality-ineligible")
        if saved["bucket"] != "gallery":
            reasons.append("review-admission-not-implemented")
        if (old["currentFolder"].split("/")[0] not in categories
                and old["currentFolder"] not in settings["runtimeSettings"]["pool"]):
            reasons.append("non-scoring-domain")
        if old["currentFolder"].split("/")[0] == "Artists":
            reasons.append("artist-scope-held")
        holds[pid] = sorted(reasons)
    if len({v.shape for v in normalized.values()}) > 1:
        raise ValueError("reformation vector dimensions differ")
    negatives, seen_pairs = {}, set()
    for pair in ledger["pairs"]:
        a, b = pair["photoIds"]
        key = tuple(sorted((a, b)))
        if a == b or a not in photos or b not in photos or key in seen_pairs:
            raise ValueError("invalid or duplicate reformation direct pair")
        seen_pairs.add(key)
        if pair["label"] not in ("same", "different", "uncertain"):
            raise ValueError("invalid reformation pair label")
        if pair["label"] != "same":
            negatives[key] = pair["label"]
    for row in ledger["unresolved"]:
        if row["photoId"] not in photos:
            raise ValueError("unknown unresolved reformation photo")
        holds[row["photoId"]].append("explicit-owner-unresolved")
    withdrawn = {
        row["photoId"] for row in ledger["referenceProposals"]
        if row["referenceUse"] == "withdraw-in-shadow" and row["wasReference"]
    }
    if not withdrawn <= photos.keys():
        raise ValueError("unknown withdrawn reformation reference")
    confirmed, intent = {}, {}
    for folder, identity in sorted(identities.items()):
        if identity.get("referenceEvidence", {}).get("construction") != "confirmed-character-intent":
            continue
        refs = sorted(identity["referencePhotoIds"])
        if not refs or len(set(refs)) != len(refs):
            raise ValueError("empty or duplicate confirmed reformation references")
        for pid in refs:
            if pid not in normalized or not audit[pid]["qualityEligible"] or pid in intent or pid in withdrawn:
                raise ValueError("invalid or conflicting confirmed reformation reference")
            intent[pid] = folder
        confirmed[folder] = refs
    for a, b in negatives:
        if a in intent and intent.get(b) == intent[a]:
            raise ValueError("conflicting confirmed reference intent requires explicit resolution")
    discovery = sorted(
        pid for pid in normalized if pid not in intent and pid not in withdrawn
        and not set(holds[pid]) - {"protected", "anchor", "workflowSelected", "identityProtected"}
    )
    reference_ids = sorted(set(discovery) | set(intent))
    if progress:
        progress(f"Frozen measurements: {len(photos)} photos; {len(discovery)} discovery references; "
                 f"{len(intent)} confirmed references. Building one bounded similarity matrix.")
    cache = _FrozenScores(normalized)
    if assess_membership:
        from . import membership_reassessment
        return membership_reassessment.build(
            candidate, run, ledger, photos, audit, previous, normalized, hashes,
            holds, negatives, confirmed, intent, cache, progress=progress,
        )

    def groups(ids):
        result = []
        for pid in sorted(ids):
            for group in result:
                if all(
                    cache.get(pid, other) >= threshold
                    and tuple(sorted((pid, other))) not in negatives
                    for other in group
                ):
                    group.append(pid)
                    break
            else:
                result.append([pid])
        return result

    hypotheses = []
    for members in groups(discovery):
        hypotheses.append({
            "personId": _id("person", members), "appearanceId": _id("face-view", members),
            "references": members, "intentFolder": None, "routeMinimum": floor, "routeMargin": margin,
        })
    for folder, refs in sorted(confirmed.items()):
        rules = categories[folder.split("/")[0]]
        for members in groups(refs):
            hypotheses.append({
                "personId": _id("intent-person", refs), "appearanceId": _id("face-view", members),
                "references": members, "intentFolder": folder,
                "routeMinimum": rules["photoRouteMinimum"], "routeMargin": rules["photoRouteMargin"],
            })
    hypotheses.sort(key=lambda h: h["appearanceId"])
    if len(hypotheses) * len(photos) > fragment_evidence.MAX_PAIR_OPERATIONS:
        raise ValueError("reformation candidate operation cap exceeded")
    original_refs = {h["appearanceId"]: list(h["references"]) for h in hypotheses}
    active = {key: list(ids) for key, ids in original_refs.items()}
    confirmed_by_person = collections.defaultdict(list)
    for h in hypotheses:
        if h["intentFolder"]:
            confirmed_by_person[h["personId"]].extend(h["references"])
    if progress:
        progress(f"Discovered {len(hypotheses)} frozen cross-folder face-view hypotheses. "
                 "Ranking all competitors once, before reference withdrawal.")
    frozen_totals = {}
    for h in hypotheses:
        refs = original_refs[h["appearanceId"]]
        total = np.sum([normalized[pid] for pid in refs], axis=0)
        frozen_totals[h["appearanceId"]] = (total, np.linalg.norm(total), {hashes[pid] for pid in refs})
    ranked_frozen = {}
    for pid in sorted(photos):
        scored = {}
        if pid in normalized and not set(holds[pid]) - {
            "protected", "anchor", "workflowSelected", "identityProtected",
        }:
            for h in hypotheses:
                centroid, norm, content_hashes = frozen_totals[h["appearanceId"]]
                if hashes[pid] in content_hashes:
                    frozen_refs = [other for other in original_refs[h["appearanceId"]]
                                   if other != pid and hashes[other] != hashes[pid]]
                    if not frozen_refs:
                        continue
                    centroid = np.sum([normalized[other] for other in frozen_refs], axis=0)
                    norm = np.linalg.norm(centroid)
                if not norm:
                    continue
                raw_score = float(normalized[pid] @ centroid / norm)
                record = {"hypothesis": h, "score": round(raw_score, 6), "rawScore": raw_score}
                old = scored.get(h["personId"])
                if old is None or (-record["score"], h["appearanceId"]) < (
                    -old["score"], old["hypothesis"]["appearanceId"],
                ):
                    scored[h["personId"]] = record
        ranked = sorted(scored.values(), key=lambda r: (-r["score"], r["hypothesis"]["personId"]))
        ranked_frozen[pid] = (len(ranked), ranked[:3])
    passes, outcomes = [], []
    for number in range(1, MAX_PASSES + 1):
        outcomes = []
        for pid in sorted(photos):
            competitor_count, frozen_top = ranked_frozen[pid]
            ranked = []
            if frozen_top:
                scores = cache.values[cache.indices[pid]]
                for frozen in frozen_top:
                    h = frozen["hypothesis"]
                    frozen_refs = [other for other in original_refs[h["appearanceId"]]
                                   if other != pid and hashes[other] != hashes[pid]]
                    refs = [other for other in active[h["appearanceId"]]
                            if other != pid and hashes[other] != hashes[pid]]
                    score = frozen["rawScore"]
                    active_centroid = np.sum([normalized[other] for other in refs], axis=0) if refs else None
                    active_norm = np.linalg.norm(active_centroid) if refs else 0.
                    active_score = float(normalized[pid] @ active_centroid / active_norm) if active_norm else None
                    support = protection._independent([
                        {"photoId": other, "sha256": hashes[other],
                         "vector": fragment_evidence._CachedReferenceVector(other, cache)}
                        for other in refs if float(scores[cache.indices[other]]) >= h["routeMinimum"]
                    ], settings)
                    blockers = []
                    if score < h["routeMinimum"]:
                        blockers.append("below-route-minimum")
                    if active_score is None or active_score < h["routeMinimum"]:
                        blockers.append("withdrawn-reference-set-insufficient")
                    if len(support) < minimum:
                        blockers.append("insufficient-independent-support")
                    check_refs = confirmed_by_person.get(h["personId"], frozen_refs)
                    if any(tuple(sorted((pid, other))) in negatives for other in check_refs if other != pid):
                        blockers.append("direct-different-or-uncertain-veto")
                    record = {
                        "personId": h["personId"], "appearanceId": h["appearanceId"],
                        "score": round(score, 6), "supportPhotoIds": [r["photoId"] for r in support],
                        "activeScore": round(active_score, 6) if active_score is not None else None,
                        "referencePhotoIds": refs, "routeMinimum": h["routeMinimum"],
                        "frozenReferencePhotoIds": frozen_refs,
                        "requiredSupport": minimum, "routeMargin": h["routeMargin"], "blockers": blockers,
                    }
                    ranked.append(record)
            best = ranked[0] if ranked else None
            evidence_reasons = []
            if best:
                evidence_reasons.extend(best["blockers"])
                lead = best["score"] - ranked[1]["score"] if len(ranked) > 1 else 2.
                if lead < max(best["routeMargin"], settings["photoRouting"]["minimumOwnCoreLead"]):
                    evidence_reasons.append("ambiguous-full-competitor-margin")
            else:
                evidence_reasons.append("no-independent-reference-hypothesis")
            reasons = list(holds[pid]) + evidence_reasons
            # Confirmed intent is recorded explicitly, not credited as automatic discovery.
            explicit = intent.get(pid)
            assigned = best if best and not reasons else None
            if explicit and not holds[pid]:
                h = next(item for item in hypotheses if pid in original_refs[item["appearanceId"]])
                proposed_person, appearance = h["personId"], h["appearanceId"]
                origin = "confirmed-character-reference"
            else:
                proposed_person = assigned["personId"] if assigned else None
                appearance = assigned["appearanceId"] if assigned else None
                origin = "automatic" if assigned else "held" if holds[pid] else "unresolved"
            outcomes.append({
                "photoId": pid, "oldFolder": previous[pid]["currentFolder"],
                "installedDestination": photos[pid]["destination"],
                "proposedPersonId": proposed_person, "appearanceId": appearance,
                "origin": origin, "reasons": sorted(set(reasons)), "topCandidates": ranked[:3],
                "qualifiedReferencePersonId": best["personId"] if best and not evidence_reasons else None,
                "competitorPersonCount": competitor_count, "placement": "unchanged",
                "referenceEligible": pid in reference_ids,
                "family": "unassigned-identity-assessment-first",
            })
        by_id = {row["photoId"]: row for row in outcomes}
        conflicted = set()
        for a, b in negatives:
            left, right = by_id[a], by_id[b]
            if left["proposedPersonId"] and left["proposedPersonId"] == right["proposedPersonId"]:
                conflicted.update(
                    row["photoId"] for row in (left, right) if row["origin"] == "automatic"
                )
        for pid in sorted(conflicted):
            by_id[pid].update(
                proposedPersonId=None, appearanceId=None, qualifiedReferencePersonId=None,
                origin="unresolved", reasons=sorted(set(by_id[pid]["reasons"]) | {"direct-member-conflict"}),
            )
        withdrawals = []
        next_active = {}
        for h in hypotheses:
            refs = active[h["appearanceId"]]
            kept = refs if h["intentFolder"] else [
                pid for pid in refs if by_id[pid]["qualifiedReferencePersonId"] == h["personId"]
            ]
            next_active[h["appearanceId"]] = kept
            withdrawals.extend({"photoId": pid, "appearanceId": h["appearanceId"]}
                               for pid in refs if pid not in kept)
        passes.append({"pass": number, "referenceWithdrawals": withdrawals,
                       "assignedPhotos": sum(row["proposedPersonId"] is not None for row in outcomes)})
        if progress:
            progress(f"Pass {number}/{MAX_PASSES}: {passes[-1]['assignedPhotos']} proposed members; "
                     f"{len(withdrawals)} reference withdrawals; growth disabled.")
        if not withdrawals:
            break
        if number < MAX_PASSES:
            active = next_active
    stable = not passes[-1]["referenceWithdrawals"]
    active_reference_ids = {pid for refs in active.values() for pid in refs}
    for row in outcomes:
        folder = row["oldFolder"]
        row["oldPersonId"] = identities.get(folder, {}).get("identityId") or _id("retained-person", [folder])
        row["effectivePersonId"] = row["proposedPersonId"] or row["oldPersonId"]
        row["explicitIntentFolder"] = intent.get(row["photoId"])
        row["frozenReferenceCandidate"] = row["referenceEligible"]
        row["referenceEligible"] = row["photoId"] in active_reference_ids
    people, appearances = {}, []
    for h in hypotheses:
        members = [r["photoId"] for r in outcomes if r["appearanceId"] == h["appearanceId"]]
        appearances.append({
            "appearanceId": h["appearanceId"], "personId": h["personId"],
            "memberPhotoIds": members, "frozenReferencePhotoIds": original_refs[h["appearanceId"]],
            "referencePhotoIds": active[h["appearanceId"]],
            "status": "proposed-face-view-not-outfit-certified", "core": False,
        })
        if not members:
            continue
        person = people.setdefault(h["personId"], {
            "personId": h["personId"], "memberPhotoIds": [], "appearanceIds": [],
            "intentFolder": h["intentFolder"], "canonicalOwner": None, "ownerStatus": "unresolved",
        })
        person["memberPhotoIds"].extend(members)
        person["appearanceIds"].append(h["appearanceId"])
    for person in people.values():
        person["memberPhotoIds"].sort()
        lineage = collections.Counter(previous[pid]["currentFolder"] for pid in person["memberPhotoIds"])
        person["lineage"] = dict(sorted(lineage.items()))
        if person["intentFolder"]:
            person["canonicalOwner"] = person["intentFolder"]
            person["ownerStatus"] = "confirmed-character-intent"
        elif len(lineage) == 1:
            person["canonicalOwner"] = next(iter(lineage))
            person["ownerStatus"] = "single-lineage-suggestion-not-installation"
        else:
            person["ownerStatus"] = "cross-folder-owner-unresolved"
    residuals = []
    retained_people = []
    for folder in sorted({row["currentFolder"] for row in previous.values()}):
        remaining = [row for row in outcomes if row["oldFolder"] == folder and row["proposedPersonId"] is None]
        residuals.append({
            "oldFolder": folder, "residualPhotoIds": [r["photoId"] for r in remaining],
            "heldPhotoIds": [r["photoId"] for r in remaining if r["origin"] == "held"],
            "unresolvedPhotoIds": [r["photoId"] for r in remaining if r["origin"] == "unresolved"],
            "proposedPeople": sorted({r["proposedPersonId"] for r in outcomes
                                     if r["oldFolder"] == folder and r["proposedPersonId"]}),
            "status": "residual-kept-reconsiderable-no-folder-transport",
        })
        if remaining:
            retained_people.append({
                "personId": remaining[0]["oldPersonId"], "folder": folder,
                "memberPhotoIds": [r["photoId"] for r in remaining],
                "status": "retained-unassessed-membership-not-certified",
            })
    return {
        "schemaVersion": 1, "kind": "cross-folder-reformation-state",
        "status": "stable-unaccepted" if stable else "bounded-incomplete",
        "rows": outcomes, "people": sorted(people.values(), key=lambda p: p["personId"]),
        "appearances": appearances, "residuals": residuals, "passes": passes,
        "retainedPeople": retained_people,
        "pendingReferenceWithdrawals": passes[-1]["referenceWithdrawals"],
        "summary": {
            "photoCount": len(outcomes), "proposedPeople": len(people),
            "crossFolderPeople": sum(len(p["lineage"]) > 1 for p in people.values()),
            "crossFolderMembers": sum(len(p["memberPhotoIds"]) for p in people.values() if len(p["lineage"]) > 1),
            "crossFolderAutomaticMembers": sum(
                row["origin"] == "automatic" and row["proposedPersonId"] in people
                and len(people[row["proposedPersonId"]]["lineage"]) > 1 for row in outcomes
            ),
            "automaticMembers": sum(r["origin"] == "automatic" for r in outcomes),
            "explicitIntentMembers": sum(r["origin"] == "confirmed-character-reference" for r in outcomes),
            "heldPhotos": sum(r["origin"] == "held" for r in outcomes),
            "unresolvedPhotos": sum(r["origin"] == "unresolved" for r in outcomes),
            "discoveryReferences": len(discovery), "frozenHypotheses": len(hypotheses),
            "passCount": len(passes), "stable": stable, "executedMoves": 0,
            "retainedPeople": len(retained_people),
        },
        "recipe": {
            "name": "global-complete-link-frozen-loo-withdrawal-v1",
            "clusterMinimum": threshold, "generalRouteMinimum": floor, "generalRouteMargin": margin,
            "minimumIndependentReferences": minimum, "referenceGrowth": False,
            "positivePairLabelsInDiscovery": 0, "negativePairVetoes": len(negatives),
            "oldFoldersInDiscovery": False, "fullCompetitors": True,
            "withdrawnHypothesesRetainedAsRivals": True,
        },
        "limits": [
            "Experimental proposed state, not an accepted rule or executable move plan.",
            "Discovery references freeze before admission; only withdrawal is implemented between passes.",
            "Face views are not certified outfit/appearance identities; disconnected views may still split.",
            "Protected/selected/Review/Artist placements held; explicit reference intent is not automatic recovery.",
            "Cross-folder canonical ownership and existing family-edge reconciliation remain unresolved.",
            "No secondary cues, reference growth, physical path/derivative/viewer migration or runtime activation.",
        ],
    }
