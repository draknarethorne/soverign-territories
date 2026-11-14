"""Non-installable entrance/retention/reference ablations over saved face views."""
import collections
import copy
import math
import time

import numpy as np

from . import fragment_evidence, membership_reassessment, protection, reformation


LADDER = ("Sisters", "Angels", "Models", "Prospects", "Potentials")
MAX_BOUNDARIES = 4


def recipes():
    def recipe(name, admission, core, retain, *, core_support=4, growth=False):
        return {
            "name": name, "admission": dict(zip(LADDER, admission)),
            "core": dict(zip(LADDER, core)), "retain": dict(zip(LADDER, retain)),
            "margin": dict(zip(LADDER, (.12, .10, .08, .06, .06))),
            "joinSupport": 4, "coreSupport": core_support, "retainSupport": 2,
            "growth": growth,
        }
    middle = recipe("ordered-middle", (.50, .45, .40, .35, .35),
                    (.40, .35, .30, .25, .25), (.25, .22, .18, .15, .15))
    return [
        {**copy.deepcopy(middle), "name": "ordered-strict-reference-control",
         "core": dict.fromkeys(LADDER, .55)},
        copy.deepcopy(middle),
        {**copy.deepcopy(middle), "name": "ordered-middle-growth", "growth": True},
        recipe("ordered-higher-entrance", (.55, .50, .45, .40, .40),
               (.40, .35, .30, .25, .25), (.25, .22, .18, .15, .15)),
        recipe("ordered-lower-entrance", (.45, .40, .35, .30, .30),
               (.40, .35, .30, .25, .25), (.25, .22, .18, .15, .15)),
        recipe("ordered-lower-core", (.50, .45, .40, .35, .35),
               (.35, .30, .25, .20, .20), (.25, .22, .18, .15, .15)),
        {**copy.deepcopy(middle), "name": "ordered-three-core-support", "coreSupport": 3},
        {**copy.deepcopy(middle), "name": "ordered-higher-release-floor",
         "retain": dict(zip(LADDER, (.35, .30, .25, .20, .20)))},
    ]


def validate_recipe(recipe):
    for axis in ("admission", "core", "retain", "margin"):
        values = [recipe[axis][c] for c in LADDER]
        if any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not math.isfinite(v) or not 0 <= v <= 1 for v in values):
            raise ValueError(f"invalid entrance recipe {axis}")
        if any(a < b for a, b in zip(values, values[1:])):
            raise ValueError(f"category ladder inverted: {axis}")
    for category in LADDER:
        if recipe["retain"][category] > min(recipe["core"][category], recipe["admission"][category]):
            raise ValueError("retention floor exceeds core or admission")
    for key in ("joinSupport", "coreSupport", "retainSupport"):
        if type(recipe[key]) is not int or recipe[key] < 2:
            raise ValueError("independent support must be at least two")
    if type(recipe["growth"]) is not bool:
        raise ValueError("invalid growth flag")


class Evidence:
    def __init__(self, state, run, vectors, ledger):
        self.source = {row["photoId"]: row for row in state["rows"]}
        self.photos = {row["photoId"]: row for row in run["photos"]}
        if (len(self.source) != len(state["rows"]) or self.source.keys() != self.photos.keys()
                or len(self.photos) > reformation.MAX_PHOTOS):
            raise ValueError("entrance trial population differs or exceeds cap")
        self.settings = run["policy"]
        self.vectors = {pid: fragment_evidence._normalize_vector(v, pid) for pid, v in vectors.items()}
        self.cache = reformation._FrozenScores(self.vectors)
        self.ids = self.cache.ids
        self.matrix = np.asarray([self.vectors[pid] for pid in self.ids])
        self.hashes = {pid: row.get("preparedSHA256") or row.get("sha256") for pid, row in self.photos.items()}
        if any(not value for value in self.hashes.values()):
            raise ValueError("missing content hashes")
        self.negatives = collections.defaultdict(set)
        self.labels = sorted(ledger["pairs"], key=lambda pair: tuple(sorted(pair["photoIds"])))
        seen = set()
        for pair in self.labels:
            a, b = pair["photoIds"]
            key = tuple(sorted((a, b)))
            if a == b or a not in self.source or b not in self.source or key in seen:
                raise ValueError("invalid or duplicate exact pair")
            seen.add(key)
            if pair["label"] not in ("same", "different", "uncertain"):
                raise ValueError("invalid pair label")
            if pair["label"] != "same":
                self.negatives[a].add(b)
                self.negatives[b].add(a)
        withdrawn = {r["photoId"] for r in ledger["referenceProposals"]
                     if r["referenceUse"] == "withdraw-in-shadow" and r["wasReference"]}
        self.reference_exclusions = withdrawn
        self.eligible = {
            pid for pid, row in self.source.items() if pid in self.vectors
            and not set(row["reasons"]) & membership_reassessment.REFERENCE_BLOCKS
        }
        self.reference_rows = {
            pid: {"photoId": pid, "sha256": self.hashes[pid],
                  "vector": fragment_evidence._CachedReferenceVector(pid, self.cache)}
            for pid in self.vectors
        }
        self.views = sorted(copy.deepcopy(state["appearances"]), key=lambda view: view["appearanceId"])
        if len({v["appearanceId"] for v in self.views}) != len(self.views):
            raise ValueError("duplicate view")
        for view in self.views:
            if view["category"] not in LADDER:
                raise ValueError("view category outside entrance ladder")
            if not set(view["frozenReferencePhotoIds"]) <= self.photos.keys():
                raise ValueError("unknown reference")
            view["original"] = sorted(set(view["frozenReferencePhotoIds"]) & self.eligible - withdrawn)
            if view.get("explicitIntent") and set(view["original"]) != set(view["frozenReferencePhotoIds"]):
                raise ValueError("confirmed references unavailable; explicit resolution required")
        self.independence = {}
        self.original_scores = self.scores({v["appearanceId"]: v["original"] for v in self.views})

    def independent(self, ids):
        key = tuple(sorted(ids))
        if key not in self.independence:
            self.independence[key] = [
                r["photoId"] for r in protection._independent([self.reference_rows[pid] for pid in key], self.settings)
            ]
        return self.independence[key]

    def others(self, pid, refs):
        maximum = self.settings["identityActions"]["independentEvidenceMaximumSimilarity"]
        return [other for other in refs if pid != other and self.hashes[pid] != self.hashes[other]
                and (pid not in self.vectors or self.cache.get(pid, other) <= maximum)]

    def support(self, pid, refs, floor):
        return self.independent([other for other in self.others(pid, refs) if self.cache.get(pid, other) >= floor])

    def measure(self, pid, refs):
        refs = self.independent(self.others(pid, refs))
        if pid not in self.vectors or not refs:
            return None
        total = np.sum([self.vectors[p] for p in refs], axis=0)
        norm = np.linalg.norm(total)
        return float(self.vectors[pid] @ total / norm) if norm else None

    def scores(self, inventory):
        # Dense centroid ranking is bounded by the existing photo/view cap.
        if len(self.ids) * len(self.views) > fragment_evidence.MAX_PAIR_OPERATIONS:
            raise ValueError("entrance score matrix exceeds cap")
        if not self.views:
            return np.empty((len(self.ids), 0))
        centers = []
        for view in self.views:
            refs = self.independent(inventory[view["appearanceId"]])
            total = np.sum([self.vectors[p] for p in refs], axis=0) if refs else np.zeros(self.matrix.shape[1])
            norm = np.linalg.norm(total)
            centers.append(total / norm if norm else np.zeros_like(total))
        values = self.matrix @ np.asarray(centers).T
        for j, view in enumerate(self.views):
            refs = inventory[view["appearanceId"]]
            if not refs:
                values[:, j] = np.nan
            else:
                contents = {self.hashes[p] for p in refs}
                for pid in self.ids:
                    if self.hashes[pid] in contents:
                        score = self.measure(pid, refs)
                        values[self.cache.indices[pid], j] = score if score is not None else np.nan
        return values

    def qualify(self, view, refs, recipe):
        refs = sorted(set(refs) - self.reference_exclusions)
        if view.get("explicitIntent"):
            return sorted(refs), True
        floor = recipe["core"][view["category"]]
        for _ in range(MAX_BOUNDARIES):
            kept = [pid for pid in refs if not self.negatives[pid].intersection(refs)
                    and len(self.support(pid, refs, floor)) >= recipe["coreSupport"]
                    and (self.measure(pid, refs) or -1) >= floor]
            if kept == refs:
                return kept, True
            refs = kept
        return refs, False


def run_variant(evidence, recipe):
    validate_recipe(recipe)
    start = time.perf_counter()
    e = evidence
    bases, stable_views = {}, {}
    for view in e.views:
        key = view["appearanceId"]
        bases[key], stable_views[key] = e.qualify(view, view["original"], recipe)
    promotions = {v["appearanceId"]: [] for v in e.views}
    histories, initial_inventory = [], None
    seen_signatures = set()
    for boundary in range(1, MAX_BOUNDARIES + 1):
        inventory = {key: sorted(set(refs + promotions[key])) for key, refs in bases.items()}
        if initial_inventory is None:
            initial_inventory = copy.deepcopy(inventory)
        values = e.scores(inventory)
        rows = []
        for pid, source in sorted(e.source.items()):
            eligible = pid in e.eligible
            rankings = []
            if eligible:
                index = e.cache.indices[pid]
                for j, view in enumerate(e.views):
                    active = values[index, j]
                    original = e.original_scores[index, j]
                    score = active if np.isfinite(active) else original
                    if not np.isfinite(score):
                        continue
                    rankings.append((float(score), j, float(active) if np.isfinite(active) else None))
                rankings.sort(key=lambda r: (-r[0], e.views[r[1]]["appearanceId"]))
            own_ranked = [
                r for r in rankings if e.views[r[1]]["folder"] == source["oldFolder"]
                or e.views[r[1]]["personId"] in getattr(e, "own_people", {}).get(pid, set())
            ]
            own = next((r for r in own_ranked if r[2] is not None), own_ranked[0] if own_ranked else None)

            def record(ranked):
                if ranked is None:
                    return None
                score, j, active = ranked
                view = e.views[j]
                refs = e.others(pid, inventory[view["appearanceId"]])
                floor = recipe["admission"][view["category"]]
                return {
                    "appearanceId": view["appearanceId"], "personId": view["personId"],
                    "folder": view["folder"], "category": view["category"], "pooled": view["pooled"],
                    "score": round(score, 6), "activeScore": round(active, 6) if active is not None else None,
                    "originalScore": round(float(e.original_scores[e.cache.indices[pid], j]), 6)
                    if np.isfinite(e.original_scores[e.cache.indices[pid], j]) else None,
                    "referencePhotoIds": refs,
                    "originalReferencePhotoIds": e.others(pid, view["original"]),
                    "independentCount": len(e.independent(refs)),
                    "joinSupportPhotoIds": e.support(pid, refs, floor),
                    "veto": bool(e.negatives[pid].intersection(view["original"] + refs)),
                    "stable": stable_views[view["appearanceId"]],
                }

            own_record = record(own)
            membership = "not-assessed-scope-or-measurement"
            if eligible:
                if own_record is None or own_record["activeScore"] is None or not own_record["stable"]:
                    membership = "comparison-unavailable"
                elif own_record["veto"]:
                    membership = "exact-pair-conflict"
                elif own_record["independentCount"] < recipe["retainSupport"]:
                    membership = "comparison-insufficient-independent-references"
                elif own[2] < recipe["retain"][own_record["category"]]:
                    membership = "below-retention-range"
                elif len(e.support(pid, own_record["referencePhotoIds"],
                                   recipe["retain"][own_record["category"]])) < recipe["retainSupport"]:
                    membership = "comparison-insufficient-independent-support"
                else:
                    membership = "retention-compatible-not-identity-confirmation"
            # An inactive high-scoring hypothesis remains a competitor, but
            # is never substituted for qualified receiving evidence.
            best = next((r for r in rankings if r[2] is not None), None)
            target = record(best)
            lead, blockers = None, []
            if target:
                competitors = [r[0] for r in rankings if e.views[r[1]]["personId"] != target["personId"]]
                lead = best[2] - max(competitors, default=-1.)
                cat = target["category"]
                if best[2] < recipe["admission"][cat]:
                    blockers.append("below-entrance-floor")
                if len(target["joinSupportPhotoIds"]) < recipe["joinSupport"]:
                    blockers.append("insufficient-independent-entrance-support")
                if lead < recipe["margin"][cat]:
                    blockers.append("unresolved-competing-hypothesis")
                if target["veto"]:
                    blockers.append("exact-different-or-uncertain-veto")
                if not target["stable"]:
                    blockers.append("reference-qualification-incomplete")
                rules = e.settings["categoryPolicies"][cat]
                if (rules["identityProtectedByDefault"] and not rules.get("galleryAdmissionEnabled", False)
                        and target["folder"] != source["oldFolder"]):
                    blockers.append("saved-gallery-admission-disabled")
            else:
                blockers.append("no-qualified-receiving-comparison")
            if source["placementBlocks"]:
                blockers.append("physical-action-locked")
            if source["explicitIntentFolder"]:
                blockers.append("explicit-intent-preserved")
            proposed = target["personId"] if target and not blockers else None
            rows.append({
                "photoId": pid, "oldFolder": source["oldFolder"], "membership": membership,
                "own": own_record, "best": target, "lead": round(lead, 6) if lead is not None else None,
                "proposalPersonId": proposed, "proposalViewId": target["appearanceId"] if proposed else None,
                "entranceBlockers": blockers,
                "releaseCandidate": membership in ("below-retention-range", "exact-pair-conflict"),
                "logicalRelease": membership in ("below-retention-range", "exact-pair-conflict")
                and not source["placementBlocks"] and not source["explicitIntentFolder"],
                "placementBlocks": source["placementBlocks"],
                "explicitIntentFolder": source["explicitIntentFolder"], "corePromotionStaged": False,
            })
        by_id = {r["photoId"]: r for r in rows}

        def withdraw_proposal(row, reason):
            row.update(proposalPersonId=None, proposalViewId=None)
            row["entranceBlockers"].append(reason)

        intent_people = {}
        for view in e.views:
            if view["explicitIntent"]:
                for pid in view["original"]:
                    if pid in intent_people and intent_people[pid] != view["personId"]:
                        raise ValueError("conflicting explicit intent")
                    intent_people[pid] = view["personId"]
        for pair in e.labels:
            if pair["label"] == "same":
                continue
            a, b = pair["photoIds"]
            left = by_id[a]["proposalPersonId"] or intent_people.get(a)
            right = by_id[b]["proposalPersonId"] or intent_people.get(b)
            if left and left == right:
                for pid in (a, b):
                    if by_id[pid]["proposalPersonId"]:
                        withdraw_proposal(by_id[pid], "exact-member-conflict")
                    elif pid in intent_people:
                        if a in intent_people and b in intent_people:
                            raise ValueError("negative pair conflicts with explicit intent")
        for view in e.views:
            if view["pooled"]:
                assigned = [r for r in rows if r["proposalPersonId"] == view["personId"]]
                if len(assigned) < recipe["joinSupport"] + 1:
                    for row in assigned:
                        withdraw_proposal(row, "provisional-group-too-small")
        next_bases = {}
        next_stable = {}
        for view in e.views:
            key = view["appearanceId"]
            kept = bases[key] if view["explicitIntent"] else [
                pid for pid in bases[key]
                if not (by_id[pid]["releaseCandidate"] and e.source[pid]["oldFolder"] == view["folder"])
                and by_id[pid]["proposalPersonId"] in (None, view["personId"])
                and (not view["pooled"] or by_id[pid]["proposalPersonId"] == view["personId"])
                and "exact-member-conflict" not in by_id[pid]["entranceBlockers"]
            ]
            next_bases[key], next_stable[key] = e.qualify(view, kept, recipe)
        next_promotions = {key: [] for key in bases}
        staged = []
        for view in e.views:
            key, cat = view["appearanceId"], view["category"]
            # Promote once from frozen original evidence. Added references
            # cannot certify another addition or rescue an insufficient base.
            candidates = ([r["photoId"] for r in rows if r["proposalViewId"] == key]
                          if boundary == 1 and recipe["growth"] else promotions[key])
            for pid in candidates:
                if pid in bases[key] or not recipe["growth"] or not next_stable[key]:
                    continue
                row = by_id[pid]
                score = e.measure(pid, next_bases[key])
                if (row["proposalViewId"] != key or score is None
                        or score < max(recipe["core"][cat], recipe["admission"][cat])
                        or len(e.support(pid, next_bases[key], max(recipe["core"][cat], recipe["admission"][cat])))
                        < max(recipe["coreSupport"], recipe["joinSupport"])
                        or e.negatives[pid].intersection(next_bases[key])
                        or e.negatives[pid].intersection(next_promotions[key])):
                    continue
                next_promotions[key].append(pid)
                row["corePromotionStaged"] = True
                staged.append({"photoId": pid, "appearanceId": key,
                               "originalBaseWitnessPhotoIds": e.support(
                                   pid, next_bases[key], max(recipe["core"][cat], recipe["admission"][cat]))})
        next_inventory = {key: sorted(set(next_bases[key] + next_promotions[key])) for key in bases}
        changed = sorted(key for key in inventory if next_inventory[key] != inventory[key] or not next_stable[key])
        histories.append({
            "boundary": boundary, "referenceCount": sum(map(len, inventory.values())),
            "nextReferenceCount": sum(map(len, next_inventory.values())),
            "added": {k: sorted(set(next_inventory[k]) - set(inventory[k])) for k in changed},
            "removed": {k: sorted(set(inventory[k]) - set(next_inventory[k])) for k in changed},
            "changedViews": changed, "corePromotionWitnesses": staged,
        })
        if not changed:
            break
        signature = tuple((key, tuple(ids)) for key, ids in sorted(next_inventory.items()))
        if signature in seen_signatures:
            break
        seen_signatures.add(signature)
        bases, promotions, stable_views = next_bases, next_promotions, next_stable
    stable = not histories[-1]["changedViews"]
    if not stable:
        for row in rows:
            if row["proposalPersonId"]:
                withdraw_proposal(row, "bounded-reference-work-incomplete")
    effective = {r["photoId"]: r["proposalPersonId"] or intent_people.get(r["photoId"]) for r in rows}
    pairs = collections.Counter()
    for pair in e.labels:
        a, b = pair["photoIds"]
        pairs[pair["label"] + "Total"] += 1
        pairs[pair["label"] + "Coassigned"] += int(bool(effective[a] and effective[a] == effective[b]))
    if pairs["differentCoassigned"] or pairs["uncertainCoassigned"]:
        raise ValueError("exact negative/uncertain co-assignment escaped veto")
    counts = collections.Counter(r["membership"] for r in rows)
    return {
        "recipe": recipe, "rows": rows, "boundaries": histories,
        "summary": {
            "photoCount": len(rows), "membership": dict(counts), "stable": stable,
            "referenceCount": sum(map(len, inventory.values())),
            "initialReferenceCount": sum(map(len, initial_inventory.values())),
            "addedReferenceOccurrences": sum(len(set(inventory[k]) - set(initial_inventory[k])) for k in inventory),
            "uniqueReferencePhotos": len({pid for refs in inventory.values() for pid in refs}),
            "proposals": sum(r["proposalPersonId"] is not None for r in rows),
            "crossFolderProposals": sum(bool(r["proposalPersonId"] and r["best"]["folder"] != r["oldFolder"]) for r in rows),
            "logicalReleases": sum(r["logicalRelease"] for r in rows),
            "exactPairControls": dict(pairs), "elapsedSeconds": time.perf_counter() - start,
            "installedMoves": 0, "automaticProtectionAcquired": 0,
        },
        "references": inventory,
    }


def run_sweep(state, run, vectors, ledger, *, variants=None, progress=None, coalesce=False):
    evidence = Evidence(state, run, vectors, ledger)
    output = []
    for recipe in variants or recipes():
        result = run_variant(evidence, recipe)
        output.append(result)
        if progress:
            progress(f'{recipe["name"]}: {result["summary"]}')
    reconciliation = None
    if coalesce:
        from . import view_reconciliation
        middle = recipes()[1]
        merged, reconciliation = view_reconciliation.build(evidence, middle)
        for growth in (False, True):
            recipe = {**copy.deepcopy(middle), "name": "ordered-middle-coalesced" + ("-growth" if growth else ""),
                      "growth": growth}
            result = run_variant(merged, recipe)
            output.append(result)
            if progress:
                progress(f'{recipe["name"]}: {result["summary"]}')
    return {
        "kind": "entrance-reference-range-trial", "schemaVersion": 1,
        "variants": output, "viewReconciliation": reconciliation,
        "installedPolicyChanged": False, "installedMoves": 0,
        "limits": [
            "Exploratory ranges explicitly authorized by the user; no winning recipe selected or installed.",
            "Fixed saved face views; optional mutual-reference coalescence is not full discovery or general appearance certification.",
            "Missing/insufficient own evidence is not a release or a different-person finding.",
            "Retention compatible means eligible non-core handling, not identity confirmation.",
            "Protection is an action restriction, never a core threshold or identity proof.",
            "All original hypotheses remain rivals even when their active references disappear.",
            "Promotion occurs once against original-base witnesses at the next frozen boundary; no chained growth.",
            "Direct negative/uncertain labels veto proposals; zero violations is a safeguard, not blind accuracy.",
            "Previously reviewed same-person pairs are development evaluation only, never seed discoveries.",
            "No new model, photo movement, naming, protected-identity merge or intake.",
        ],
    }
