"""Versioned, member-first regrouping for maintained sandbox rebase profiles."""
import collections
import copy
import datetime
import hashlib
import json
import pathlib
import uuid

import numpy as np

from . import metadata, protection, rejections


RECIPE = "member-first-appearances-v1"
LADDER = ("Sisters", "Angels", "Models", "Prospects", "Potentials")
ENTRANCE = dict(zip(LADDER, (.50, .45, .40, .35, .35)))
CORE = dict(zip(LADDER, (.40, .35, .30, .25, .25)))
RETAIN = dict(zip(LADDER, (.25, .22, .18, .15, .15)))
MARGIN = dict(zip(LADDER, (.12, .10, .08, .06, .06)))
MAX_PHOTOS = 5000


def runtime_policy(policy):
    result = copy.deepcopy(policy)
    if not result["version"].endswith(":" + RECIPE):
        result["version"] += ":" + RECIPE
    for category in LADDER:
        rules = result["categoryPolicies"][category]
        rules["photoRouteMinimum"], rules["photoRouteMargin"] = ENTRANCE[category], MARGIN[category]
        rules["identityCoreMinimumSimilarity"] = CORE[category]
        if category in ("Sisters", "Angels"):
            rules["galleryAdmissionEnabled"] = True
            rules["galleryAdmissionMinimumSimilarity"] = ENTRANCE[category]
    return result


def _key(prefix, values):
    return prefix + uuid.uuid5(uuid.NAMESPACE_URL, RECIPE + ":" + "|".join(sorted(values))).hex


def _category(folder):
    value = folder.split("/", 1)[0]
    return value if value in CORE else "Potentials"


def _partition(ids, similarities, indices, threshold, conflicts):
    groups = []
    for pid in sorted(ids):
        for group in groups:
            if all(similarities[indices[pid], indices[other]] >= threshold
                   and other not in conflicts[pid] for other in group):
                group.append(pid)
                break
        else:
            groups.append([pid])
    return groups


def residual_identity(cohort, by_id, people, claimed, name_factory, *, category="Potentials",
                      rejected_parent=None):
    """Share stable residual ownership and collision-safe creative naming."""
    origins = collections.Counter(by_id[p].get("oldFolder", "") for p in cohort)
    folder = next((f for f, _ in origins.most_common()
                   if f in people and f not in claimed and not f.startswith(("Sisters/", "Angels/"))
                   and not any(rejected_parent and rejected_parent(p, people[f]["id"]) for p in cohort)), None)
    if folder is None:
        if name_factory is None:
            raise ValueError("residual identities require the maintained creative name generator")
        taken = {f.rsplit("/", 1)[-1] for f in (*people, *claimed)}
        name = name_factory(_key("person_", cohort), taken)
        if (not name or name.casefold() in {item.casefold() for item in taken}
                or any(c in name for c in "/\\") or name in (".", "..")):
            raise ValueError("residual identity name is unsafe or already occupied")
        folder = f"{category}/{name}"
    claimed.add(folder)
    return (people[folder]["id"] if folder in people else _key("person_", cohort)), folder


def reconcile_history(groups, previous, states, run_id, at):
    """Keep lineage for unambiguous continuations; never restore a stale member snapshot."""
    groups = copy.deepcopy(groups)
    claimed = set()
    for key in list(groups):
        group = groups[key]
        candidates = [
            old for old in previous.values() if old["id"] not in claimed
            and old["personId"] == group["personId"]
            and set(old["memberPhotoIds"]).intersection(group["memberPhotoIds"])
        ]
        if len(candidates) != 1:
            continue
        old = candidates[0]
        claimed.add(old["id"])
        group["id"], group["name"] = old["id"], old["name"]
        event = {"timestamp": at, "runId": run_id, "reason": "membership reassessed; stable appearance lineage retained"}
        group["history"] = [*old["history"], event]
        del groups[key]
        groups[group["id"]] = group
    occupied = {p for group in groups.values() for p in group["memberPhotoIds"]}
    for old in previous.values():
        if old["id"] in claimed or old["id"] in groups:
            continue
        members = sorted(
            p for p in old["memberPhotoIds"] if p in states and p not in occupied
            and states[p].get("personId") == old["personId"] and states[p]["status"] == old["status"]
        )
        group = copy.deepcopy(old)
        group["memberPhotoIds"] = members
        group["referencePhotoIds"] = [p for p in members if states[p]["coreUse"] and old["status"] == "supported"]
        group["history"].append({
            "timestamp": at, "runId": run_id,
            "reason": "appearance retained after member extraction/shrink" if members
            else "historical empty appearance retained; no current membership or reference authority",
        })
        groups[old["id"]] = group
        occupied.update(members)
    for group in groups.values():
        for pid in group["memberPhotoIds"]:
            states[pid]["groupId"] = group["id"]
    return groups


def review_evidence(source, rows):
    """Reuse exact human evidence, not the old experiment's now-obsolete algorithm."""
    from tools.art import likeness_diagnostics

    source = pathlib.Path(source)
    if not source.is_absolute():
        raise ValueError("review evidence source must be absolute")
    receipt = json.loads((source / "receipt.json").read_bytes())
    bindings = receipt["inputs"]

    def find(name):
        found = [pathlib.Path(p) for p in bindings if pathlib.Path(p).name == name]
        if len(found) != 1:
            raise ValueError(f"review evidence requires one bound {name}")
        return found[0]

    paths = [find("ledger.json"), find("run.json")]
    evaluations = [pathlib.Path(p) for p in bindings if pathlib.Path(p).name.startswith("candidate_evaluation_")]
    if len(evaluations) != 1:
        raise ValueError("review evidence requires one returned candidate evaluation")
    evaluation = json.loads(evaluations[0].read_bytes())
    packets = [pathlib.Path(p) for p in bindings if pathlib.Path(p).name == "packet.json"
               and json.loads(pathlib.Path(p).read_bytes()).get("packetSHA256") == evaluation["packetSHA256"]]
    if len(packets) != 1:
        raise ValueError("review evidence packet binding is unavailable")
    paths += [evaluations[0], packets[0]]
    for path in paths:
        if metadata.content_sha256(path) != bindings[str(path)]:
            raise ValueError(f"human review source changed: {path}")
    prior = {r["photoId"]: r for r in json.loads(paths[1].read_bytes())["photos"] if r.get("photoId")}
    current = {r["photoId"]: r for r in rows if r.get("photoId")}
    ledger = likeness_diagnostics.reformation_report.effective_ledger(
        json.loads(paths[0].read_bytes()), json.loads(packets[0].read_bytes()), evaluation,
    )
    for pair in ledger["pairs"]:
        for pid in pair["photoIds"]:
            if pid not in prior or pid not in current:
                raise ValueError(f"human pair is outside current regrouping scope: {pid}")
            old, new = prior[pid], current[pid]
            if old.get("preparedSHA256", old["sha256"]) != new.get("preparedSHA256", new["sha256"]):
                raise ValueError(f"human pair pixels changed; revalidation required: {pid}")
    return ledger, {str(p): metadata.content_sha256(p) for p in paths}


def regroup(rows, measured, catalog, policy, selected, run_id, *, at=None, pairs=(), name_factory=None,
            reference_exclusions=(), directed_recipe=None):
    """Rebuild unprotected hypotheses; old folders provide lineage, never admission."""
    live_clock = at is None
    at = at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows = copy.deepcopy(rows)
    if len(rows) > MAX_PHOTOS:
        raise ValueError("regrouping exceeds the bounded photo inventory")
    by_id = {}
    for row in rows:
        pid = row.get("photoId")
        if pid:
            if pid in by_id:
                raise ValueError("regrouping requires unambiguous stable photo IDs")
            by_id[pid] = row
    valid = {}
    for pid, row in by_id.items():
        photo = measured.get(row["source"])
        if (photo is not None and photo.vec is not None and photo.usable(policy["runtimeSettings"]["minFace"])
                and photo.faces == 1 and not row.get("qualityHold") and not row.get("castSeedQualityReason")):
            vector = np.asarray(photo.vec, dtype=float)
            norm = np.linalg.norm(vector)
            if not np.isfinite(vector).all() or norm == 0:
                raise ValueError(f"invalid regrouping vector: {pid}")
            valid[pid] = vector / norm
        elif directed_recipe is not None:
            from . import clean_rebase

            reason = row.get("castSeedQualityReason")
            if not reason and row.get("qualityHold"):
                reason = row.get("reason")
            if photo is None:
                quality = {
                    "classification": "missing-measurement", "reason": "measurement record unavailable",
                    "recoverableJunkCandidate": False,
                }
            else:
                quality = clean_rebase._quality_hold_evidence(photo, policy["runtimeSettings"], reason)
                if photo.faces != 1:
                    quality.update(
                        classification="ambiguous-multiface" if photo.faces > 1
                        else "missing-or-unusable-measurement",
                        reason=(f"independent identity gate requires exactly one detected face; "
                                f"measurement reports {photo.faces}; not proof image is unusable"),
                        recoverableJunkCandidate=False,
                    )
                elif not quality.get("reason"):
                    quality["reason"] = (
                        f"identity measurement unavailable/ineligible ({quality['classification']}); "
                        "not proof image is unusable"
                    )
            row["qualityEvidence"] = {**(row.get("qualityEvidence") or {}), **quality}
    ids = sorted(valid)
    if not ids:
        raise ValueError("regrouping requires eligible face measurements")
    reference_exclusions = set(reference_exclusions)
    if not reference_exclusions <= set(by_id):
        raise ValueError("reviewed reference withdrawal is outside the current input population")
    if directed_recipe is not None:
        from . import directed_reformation

        recipe = (directed_reformation.recipe_named(directed_recipe)
                  if isinstance(directed_recipe, str) else copy.deepcopy(directed_recipe))
        return directed_reformation.regroup_runtime(
            rows, valid, catalog, policy, set(selected), run_id, recipe=recipe,
            at=at, pairs=pairs, reference_exclusions=reference_exclusions, name_factory=name_factory,
        )
    indices = {pid: i for i, pid in enumerate(ids)}
    matrix = np.asarray([valid[pid] for pid in ids])
    similarities = matrix @ matrix.T
    hashes = {pid: row.get("preparedSHA256", row["sha256"]) for pid, row in by_id.items()}
    reference_rows = {
        pid: {"photoId": pid, "sha256": hashes[pid], "vector": valid[pid]} for pid in ids
    }
    conflicts = collections.defaultdict(set)
    for pair in pairs:
        left, right = pair["photoIds"]
        if left not in by_id or right not in by_id or left == right:
            raise ValueError("regrouping direct evidence has an unknown or self photo")
        if pair["label"] not in ("same", "different", "uncertain"):
            raise ValueError("invalid regrouping direct label")
        if pair["label"] != "same":
            conflicts[left].add(right)
            conflicts[right].add(left)
    people = {p["folder"]: p for p in catalog["people"].values() if not p.get("mergedInto")}
    def rejected_parent(pid, person_id):
        state = rejections.candidate_state(catalog, pid, hashes[pid])
        return bool(state.get("rejectionMetadataStale") or
                    set(state.get("rejectedPersonIds", [])) & rejections.identity_ids(catalog, person_id))
    anchors = {pid for p in people.values() for pid in p["identityAnchors"]}
    locked = set(anchors) | set(selected)
    for pid, row in by_id.items():
        if row.get("castSeedReferenceHold"):
            locked.add(pid)
        record = catalog["photos"].get(pid, {})
        provenance = record.get("protectionProvenance")
        if record.get("protected") and not provenance:
            locked.add(pid)
        if record and record["contentSha256"] not in (row["sha256"], hashes[pid]):
            locked.add(pid)
        person = people.get(row.get("oldFolder"))
        if person and person.get("protected") and person["folder"].split("/")[0] not in ("Sisters", "Angels"):
            locked.add(pid)
        if "Explicit named-person" in row.get("reason", ""):
            locked.add(pid)

    def others(pid, refs):
        return sorted(p for p in refs if p != pid and hashes[p] != hashes[pid])

    def support(pid, refs, floor):
        candidates = [reference_rows[p] for p in others(pid, refs)
                      if similarities[indices[pid], indices[p]] >= floor and p not in conflicts[pid]]
        return [r["photoId"] for r in protection._independent(candidates, policy)]

    reference_sums = {}

    def score(pid, refs):
        if not refs:
            return None
        key = tuple(refs)
        if key not in reference_sums:
            center = np.sum([valid[p] for p in refs], axis=0)
            norm = np.linalg.norm(center)
            by_hash = collections.defaultdict(list)
            for p in refs:
                by_hash[hashes[p]].append(p)
            reference_sums[key] = center, center / norm if norm else None, by_hash
        center, unit, by_hash = reference_sums[key]
        excluded = by_hash.get(hashes[pid], ())
        if not excluded:
            return float(valid[pid] @ unit) if unit is not None else None
        if len(excluded) == len(refs):
            return None
        center = center - np.sum([valid[p] for p in excluded], axis=0)
        norm = np.linalg.norm(center)
        return float(valid[pid] @ center / norm) if norm else None

    version = hashlib.sha256(json.dumps({
        "recipe": RECIPE, "pixels": hashes, "policy": policy,
        "thresholds": [ENTRANCE, CORE, RETAIN, MARGIN],
        "vectors": {p: valid[p].tolist() for p in ids},
        "pairs": sorted(pairs, key=lambda pair: sorted(pair["photoIds"])),
        "referenceExclusions": sorted(reference_exclusions),
    }, sort_keys=True).encode()).hexdigest()
    stages = []

    def snapshot(key, title, states, only=None):
        stage_rows = []
        for row in rows:
            if only is not None and row.get("photoId") not in only:
                continue
            state = states.get(row.get("photoId"), {})
            stage_rows.append({
                "photoId": row.get("photoId"), "source": row["source"],
                "destination": row["source"] if key == "input" else row["destination"],
                "personId": state.get("personId"), "groupId": state.get("groupId"),
                "status": state.get("status", "unresolved"), "coreUse": state.get("coreUse", False),
                "score": state.get("score"), "rivalScore": state.get("rivalScore"),
                "margin": state.get("margin"), "reason": state.get("reason", row["reason"]),
                "actor": RECIPE,
            })
        stages.append({"id": key, "title": title,
                       "at": datetime.datetime.now(datetime.timezone.utc).isoformat() if live_clock else at, "rows": stage_rows,
                       "populationCount": len(rows), "scope": "all inputs" if only is None else "withdrawn references",
                       "summary": dict(collections.Counter(r["status"] for r in stage_rows))})

    snapshot("input", "Frozen input and inherited placement", {
        pid: {"status": "inherited-not-assessed", "coreUse": False,
              "personId": people.get(row.get("oldFolder"), {}).get("id"),
              "reason": "inherited location is input lineage, not confirmed membership"}
        for pid, row in by_id.items()
    })
    cast_refs = collections.defaultdict(list)
    for pid in ids:
        row = by_id[pid]
        folder = row.get("oldFolder", "")
        if (pid not in reference_exclusions and folder.startswith(("Sisters/", "Angels/")) and not row.get("castSeedReferenceHold")
                and (row.get("castSeedCore") or pid in anchors)):
            cast_refs[folder].append(pid)
    views = []
    for folder, refs in sorted(cast_refs.items()):
        for group in _partition(refs, similarities, indices, CORE[_category(folder)], conflicts):
            views.append({"refs": group, "folder": folder, "cast": True, "lineage": [folder]})
    seeds = set(p for refs in cast_refs.values() for p in refs)
    # All unprotected/non-core candidates rediscover together, not inside old identities.
    pool = [pid for pid in ids if pid not in seeds and pid not in locked and pid not in reference_exclusions]
    for group in _partition(pool, similarities, indices, .45, conflicts):
        source_folders = collections.Counter(by_id[p].get("oldFolder", "") for p in group)
        folder = next((f for f, _ in source_folders.most_common()
                       if f in people and not f.startswith(("Sisters/", "Angels/"))), None)
        folder = folder or "Potentials/Unassigned"
        views.append({"refs": group, "folder": folder, "cast": False, "lineage": sorted(source_folders)})
    qualification_boundaries = []
    for view in views:
        category = _category(view["folder"])
        original = list(view["refs"])
        qualified = original
        for boundary in range(len(original) + 1):
            kept = [p for p in qualified if p in anchors or (
                len(support(p, qualified, CORE[category])) >= 4
                and not conflicts[p].intersection(qualified)
            )]
            if kept == qualified:
                break
            if not set(kept) < set(qualified):
                raise ValueError("initial reference qualification lost its strict-decrease invariant")
            qualification_boundaries.append({
                "viewId": _key("view_", original), "boundary": boundary + 1,
                "withdrawnPhotoIds": sorted(set(qualified) - set(kept)),
                "remainingReferenceOccurrences": len(kept),
            })
            qualified = kept
        else:
            raise ValueError("initial reference qualification exceeded its finite strict-decrease bound")
        view["original"] = original
        view["refs"] = qualified
        view["viewId"] = _key("view_", original)
    reference_states = {p: {"status": "supported", "coreUse": True,
                           "reason": "qualified independent frozen reference; not placement protection"}
                        for v in views for p in v["refs"]}
    snapshot("references", "Independent reference qualification and withdrawal", reference_states)

    # Complete-link view union: no single best reference and no transitive bridge.
    components = []
    for view in sorted(views, key=lambda v: (not v["cast"], v["folder"], v["viewId"])):
        if not view["refs"]:
            continue
        for component in components:
            cast_folders = {v["folder"] for v in [*component, view] if v["cast"]}
            if len(cast_folders) > 1:
                continue
            compatible = True
            for other in component:
                floor = max(CORE[_category(view["folder"])], CORE[_category(other["folder"])])
                if (any(conflicts[p].intersection(other["refs"]) for p in view["refs"])
                        or any(len(support(p, other["refs"], floor)) < 4 for p in view["refs"])
                        or any(len(support(p, view["refs"], floor)) < 4 for p in other["refs"])):
                    compatible = False
                    break
            if compatible:
                component.append(view)
                break
        else:
            components.append([view])
    claimed = set()
    targets = []
    for component in components:
        cast = next((v["folder"] for v in component if v["cast"]), None)
        counts = collections.Counter(by_id[p].get("oldFolder", "") for v in component for p in v["refs"])
        folder = cast or next((f for f, _ in counts.most_common()
                               if f in people and f not in claimed and not f.startswith(("Sisters/", "Angels/"))), None)
        refs = sorted({p for v in component for p in v["refs"]})
        if folder is None:
            if name_factory is None:
                raise ValueError("new regrouped identities require the maintained creative name generator")
            name = name_factory(_key("person_", refs), {f.rsplit("/", 1)[-1] for f in (*people, *claimed)})
            folder = f"Potentials/{name}"
        claimed.add(folder)
        person_id = people[folder]["id"] if folder in people else _key("person_", refs)
        targets.append({"personId": person_id, "folder": folder, "views": component,
                        "refs": refs, "category": _category(folder)})
    combined = {}
    for target in targets:
        if target["personId"] in combined:
            previous = combined[target["personId"]]
            previous["views"].extend(target["views"])
            previous["refs"] = sorted(set(previous["refs"]) | set(target["refs"]))
        else:
            combined[target["personId"]] = target
    targets = list(combined.values())
    def assess():
        states, target_for = {}, {}
        for pid, row in sorted(by_id.items()):
            if pid not in valid:
                states[pid] = {"status": "quality-hold", "coreUse": False, "reason": "no qualified single-face measurement"}
                continue
            rankings = []
            for target in targets:
                best = max((value for v in target["views"] if (value := score(pid, v["refs"])) is not None), default=None)
                if best is not None:
                    rankings.append((best, target))
            rankings.sort(key=lambda r: (-r[0], r[1]["personId"]))
            best, target = rankings[0] if rankings else (None, None)
            second = rankings[1][0] if len(rankings) > 1 else -1.
            current = row.get("oldFolder", "")
            state = {"status": "unresolved", "coreUse": False, "personId": None, "groupId": None,
                     "score": best,
                     "rivalScore": second, "margin": best - second if best is not None else None,
                     "reason": "insufficient independent identity evidence; preserved as explicit review task"}
            if target is not None and best is not None:
                category = target["category"]
                veto = bool(conflicts[pid].intersection(target["refs"]) or rejected_parent(pid, target["personId"]))
                witnesses = support(pid, target["refs"], ENTRANCE[category])
                founding = pid in target["refs"]
                admitted = (not veto and best >= ENTRANCE[category] and best - second >= MARGIN[category]
                            and len(witnesses) >= 4)
                if admitted:
                    state.update(status="supported", personId=target["personId"], coreUse=founding,
                                 reason="independent member entrance, full rival margin and conflict guards passed")
                    target_for[pid] = target
                elif not veto and best >= RETAIN[category] and len(support(pid, target["refs"], CORE[category])) >= 2:
                    state.update(status="tentative", personId=target["personId"],
                                 reason="plausible non-core association; entrance/support or full rival margin not qualified")
                    target_for[pid] = target
                state["independentSupportPhotoIds"] = witnesses
                state["referenceViewIds"] = [v["viewId"] for v in target["views"]]
            if pid in locked:
                own = people.get(current)
                state.update(personId=own["id"] if own else None, status="supported" if pid in anchors else "tentative",
                             coreUse=pid in seeds and pid in anchors and pid not in reference_exclusions,
                             reason=row["castSeedReason"] if row.get("castSeedReferenceHold")
                             else "explicit anchor/placement/workflow intent preserved independently of reference eligibility")
                target_for.pop(pid, None)
            states[pid] = state
        return states, target_for

    withdrawal_boundaries = []
    staged_dependencies = {}
    def settle(phase):
        bound = 1 + sum(len(view["refs"]) for target in targets for view in target["views"])
        for boundary in range(bound):
            states, target_for = assess()
            before = sum(len(view["refs"]) for target in targets for view in target["views"])
            withdrawals = []
            for target in targets:
                for view in target["views"]:
                    kept = [
                        p for p in view["refs"] if states[p]["status"] == "supported"
                        and states[p].get("personId") == target["personId"]
                        and (p in anchors or len(support(p, view["refs"], CORE[target["category"]])) >= 4)
                        and (
                            (view["viewId"], p) not in staged_dependencies
                            or len(support(p, sorted(
                                staged_dependencies[(view["viewId"], p)] & set(view["refs"])
                            ), CORE[target["category"]])) >= 4
                        )
                    ]
                    withdrawals.extend(set(view["refs"]) - set(kept))
                    view["refs"] = kept
                target["refs"] = sorted({p for view in target["views"] for p in view["refs"]})
            after = sum(len(view["refs"]) for target in targets for view in target["views"])
            withdrawal_boundaries.append({
                "phase": phase, "boundary": boundary + 1, "withdrawnPhotoIds": sorted(set(withdrawals)),
                "remainingReferenceOccurrences": after, "terminationBound": bound,
            })
            print(f"regroup {phase} boundary {boundary + 1}: {len(set(withdrawals))} withdrawals; {after} references", flush=True)
            if not withdrawals:
                return states, target_for
            if after >= before:
                raise ValueError("reference withdrawal lost its strict monotonic termination invariant")
            for pid in withdrawals:
                states[pid]["coreUse"] = False
            snapshot(f"{phase}-withdrawal-{boundary + 1}", "Frozen member/reference consistency withdrawal",
                     states, set(withdrawals))
        raise ValueError("reference withdrawal exceeded its finite strict-decrease bound")

    states, target_for = settle("membership")
    snapshot("membership", "Member-first decisions against all frozen competitors", states)
    # One explicit growth boundary, witnessed solely by original frozen references.
    additions = 0
    for target in targets:
        original = list(target["refs"])
        growth = [
            p for p, assigned in target_for.items() if assigned is target
            and states[p]["status"] == "supported" and p not in original
            and p not in reference_exclusions
            and len(support(p, original, CORE[target["category"]])) >= 4
            and not conflicts[p].intersection(original)
        ]
        if growth:
            for view in target["views"]:
                # Growth cannot erase an original rival or make a separate view disappear.
                eligible = [p for p in growth if len(support(p, view["refs"], CORE[target["category"]])) >= 4]
                for pid in eligible:
                    staged_dependencies[(view["viewId"], pid)] = set(support(pid, view["refs"], CORE[target["category"]]))
                view["refs"] = sorted(set(view["refs"]) | set(eligible))
                for pid in eligible:
                    states[pid]["coreUse"] = True
                additions += len(eligible)
            target["refs"] = sorted({p for view in target["views"] for p in view["refs"]})
    snapshot("growth", "Staged references supported by original witnesses only", states)
    if additions:
        states, target_for = settle("post-growth")
    residual_cohorts = _partition(
        [p for p in ids if p not in locked and states[p]["status"] == "unresolved"],
        similarities, indices, .45, conflicts,
    )
    independent_candidates = 0
    for cohort in residual_cohorts:
        if len(cohort) < 2:
            continue
        person_id, folder = residual_identity(
            cohort, by_id, people, claimed, name_factory, rejected_parent=rejected_parent,
        )
        target = {"personId": person_id, "folder": folder, "category": _category(folder),
                  "views": [], "refs": [], "residual": True}
        targets.append(target)
        independent_candidates += 1
        for pid in cohort:
            states[pid].update(
                status="tentative", personId=person_id, coreUse=False, groupId=None,
                rivalScore=states[pid]["score"], score=None, margin=None,
                independentSupportPhotoIds=[], referenceViewIds=[],
                reason="coherent independent residual candidate; no qualified parent/reference claim",
            )
            target_for[pid] = target
    snapshot("residual", "Released members rediscovered as coherent independent candidates", states)
    # Tentative associations cannot provide reference authority.
    groups = {}
    for target in targets:
        if not target["views"]:
            continue
        members = [p for p, t in target_for.items() if t is target and states[p]["status"] == "supported"]
        # A reference view is an appearance only when distinct from the main view.
        principal = max(target["views"], key=lambda v: (len(v["refs"]), v["viewId"]))
        winning_views = {}
        for pid in members:
            ranked_views = [
                (value, view["viewId"]) for view in target["views"]
                if (value := score(pid, view["refs"])) is not None
                and value >= ENTRANCE[target["category"]]
                and len(support(pid, view["refs"], ENTRANCE[target["category"]])) >= 4
            ]
            winning_views[pid] = max(ranked_views)[1] if ranked_views else None
        for view in target["views"]:
            selected_members = [p for p in members if winning_views[p] == view["viewId"]]
            if view is principal or len(selected_members) < 2:
                continue
            group_id = _key("group_", [target["personId"], view["viewId"]])
            origin = next((f.rsplit("/", 1)[-1] for f in view["lineage"] if f != target["folder"]), "Variation")
            groups[group_id] = {
                "id": group_id, "personId": target["personId"], "name": origin + " appearance",
                "status": "supported", "memberPhotoIds": sorted(selected_members),
                "referencePhotoIds": sorted(set(view["refs"]) & set(selected_members)),
                "sourcePersonIds": sorted({people[f]["id"] for f in view["lineage"] if f in people}),
                "history": [{"timestamp": at, "runId": run_id, "reason": "qualified same-parent reference view"}],
                "reason": "coherent independently qualified view; source lineage retained",
            }
            for pid in selected_members:
                states[pid]["groupId"] = group_id
    tentative = collections.defaultdict(list)
    for pid, target in target_for.items():
        if states[pid]["status"] == "tentative" and not target.get("residual"):
            tentative[target["personId"]].append(pid)
    for person_id, members in sorted(tentative.items()):
        for cohort in _partition(members, similarities, indices, .45, conflicts):
            if len(cohort) < 2:
                continue
            group_id = _key("group_", [person_id, *cohort])
            origins = collections.Counter(by_id[p].get("oldFolder", "") for p in cohort)
            origin = origins.most_common(1)[0][0].rsplit("/", 1)[-1] or "Variation"
            groups[group_id] = {
                "id": group_id, "personId": person_id, "name": origin + " tentative appearance",
                "status": "tentative", "memberPhotoIds": sorted(cohort), "referencePhotoIds": [],
                "sourcePersonIds": sorted({people[f]["id"] for f in origins if f in people}),
                "history": [{"timestamp": at, "runId": run_id, "reason": "coherent tentative association, no core authority"}],
                "reason": "coherent variation; parent identity remains tentative and requires attention",
            }
            for pid in cohort:
                states[pid]["groupId"] = group_id
    groups = reconcile_history(groups, catalog.get("photoGroups", {}), states, run_id, at)
    for pid, row in by_id.items():
        state = states[pid]
        target = target_for.get(pid)
        if target and pid not in locked:
            # Tentative hosting is review, never a falsely accepted Gallery member.
            bucket = "gallery" if state["status"] == "supported" else "review"
            row["destination"] = f"{target['folder']}/{bucket}/{pathlib.PurePosixPath(row['destination']).name}"
            row["reason"] = state["reason"]
            if target["folder"].startswith(("Sisters/", "Angels/")):
                if bucket == "gallery":
                    row["castAdmission"] = {
                        "folder": target["folder"], "score": state["score"], "margin": state["margin"],
                        "independentSupport": len(state.get("independentSupportPhotoIds", [])),
                        "qualityEligible": True, "metadataStale": False, "rejectionHistory": False, "protected": False,
                    }
        elif pid not in locked and state["status"] == "unresolved":
            row["destination"] = f"Various/review/{pathlib.PurePosixPath(row['destination']).name}"
            row["reason"] = state["reason"]
        if row["source"].startswith(("Sisters/", "Angels/")) and row.get("castSeedDecision"):
            same_gallery = pathlib.PurePosixPath(row["source"]).parent == pathlib.PurePosixPath(row["destination"]).parent
            row["retainedCast"], row["releasedCast"] = same_gallery, not same_gallery
            row["castSeedDecision"] = "retained" if same_gallery else "released"
        row["membership"] = {
            key: state.get(key) for key in ("personId", "groupId", "status", "coreUse", "reason")
        }
        row["membership"]["referenceVersion"] = version
    snapshot("appearances", "Named supported/tentative appearances and primary singletons", states)
    snapshot("refinement", "Frozen final decisions; no tentative reference promotion", states)
    for target in targets:
        if target["personId"] not in catalog["people"] and any(
            state.get("personId") == target["personId"] for state in states.values()
        ):
            catalog["people"][target["personId"]] = {
                "id": target["personId"], "folder": target["folder"],
                "displayName": target["folder"].rsplit("/", 1)[-1], "folderHistory": [],
                "identityAnchors": [], "protected": False,
            }
    # No implicit identity/folder merge: old people remain lineage, active homes resolve by folder.
    catalog["photoGroups"] = groups
    for pid, row in by_id.items():
        record = catalog["photos"].setdefault(pid, {"contentSha256": hashes[pid], "protected": False})
        record["contentSha256"] = hashes[pid]
        record["membership"] = row["membership"]
    snapshot("publication", "Final names, destinations and file publication plan", states)
    same_pairs = [pair for pair in pairs if pair["label"] == "same"]
    def coassigned(pair, statuses):
        left, right = (states[p] for p in pair["photoIds"])
        return (left["status"] in statuses and right["status"] in statuses
                and left.get("personId") is not None and left.get("personId") == right.get("personId"))

    evaluation = {
        "photoCount": len(rows), "identifiedPhotos": len(by_id), "eligibleMeasurements": len(valid),
        "supported": sum(s["status"] == "supported" for s in states.values()),
        "tentative": sum(s["status"] == "tentative" for s in states.values()),
        "unresolved": sum(s["status"] == "unresolved" for s in states.values()),
        "qualityHolds": sum(s["status"] == "quality-hold" for s in states.values()),
        "namedGroups": sum(bool(g["memberPhotoIds"]) for g in groups.values()), "referenceVersion": version,
        "independentResidualCandidates": independent_candidates,
        "stagedReferenceOccurrences": additions,
        "stagedDependencies": [
            {"viewId": view_id, "photoId": pid, "originalWitnessPhotoIds": sorted(witnesses)}
            for (view_id, pid), witnesses in sorted(staged_dependencies.items())
        ],
        "reviewedReferenceExclusions": sorted(reference_exclusions),
        "referenceQualificationBoundaries": qualification_boundaries,
        "withdrawalBoundaries": withdrawal_boundaries,
        "reviewedSamePairs": len(same_pairs),
        "supportedSamePairCoassignments": sum(coassigned(pair, {"supported"}) for pair in same_pairs),
        "tentativeOrSupportedSamePairCoassignments": sum(
            coassigned(pair, {"supported", "tentative"}) for pair in same_pairs
        ),
        "sourceMoves": sum(row["source"] != row["destination"] for row in rows),
        "reformedMultiSourceIdentities": sum(
            len({by_id[p].get("oldFolder") for p, t in target_for.items()
                 if t is target and states[p]["status"] == "supported"}) > 1 for target in targets
        ),
        "referenceMembershipConflicts": sum(
            states[p]["status"] != "supported" or states[p].get("personId") != target["personId"]
            or not states[p]["coreUse"] for target in targets for p in target["refs"]
        ),
        "directConflictAdmissions": sum(
            states[a]["status"] == states[b]["status"] == "supported"
            and states[a].get("personId") == states[b].get("personId")
            for a in states for b in conflicts[a] if a < b
        ),
        "tentativeReferences": sum(bool(g["referencePhotoIds"]) for g in groups.values() if g["status"] == "tentative"),
        "evidenceScope": "development and structural regression; not blind real-person accuracy",
        "fictionalRelationships": "creative narrative, not measured biological relationship",
        "processingProfiles": ["fast", "lean", "full"],
    }
    if evaluation["directConflictAdmissions"] or evaluation["tentativeReferences"] or evaluation["referenceMembershipConflicts"]:
        raise ValueError("regrouping violated conflict or tentative-reference acceptance")
    return rows, {"recipe": RECIPE, "stages": stages, "evaluation": evaluation,
                  "thresholds": {"entrance": ENTRANCE, "core": CORE, "retention": RETAIN, "margin": MARGIN},
                  "groups": list(groups.values())}
