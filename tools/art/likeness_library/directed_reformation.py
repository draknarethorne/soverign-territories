"""Receipt-only, non-installable comparison of directed identity reformation recipes."""
import base64
import collections
import copy
import datetime
import gzip
import hashlib
import html
import json
import pathlib

import numpy as np

from . import entrance_trial, metadata


LADDER = entrance_trial.LADDER
RANK = {category: index for index, category in enumerate(LADDER)}
MAX_RECOVERY_BOUNDARIES = 4
MAX_CLUSTER_OPERATIONS = 2_000_000
MAX_SOURCE_JSON_BYTES = 192 * 1024 * 1024
GROUP_PROTECTION_FLAGS = {"identityProtected", "groupProtected", "nameProtected", "parentProtected"}


def recipes():
    middle = entrance_trial.recipes()[1]
    return [
        {
            "name": "directed-core-continuity",
            "admission": copy.deepcopy(middle["admission"]),
            "core": dict(zip(LADDER, (.60, .60, .50, .45, .40))),
            "retention": copy.deepcopy(middle["retain"]),
            "strongRelease": {"sourceMaximum": .30, "destinationMinimum": .60, "signedMargin": .30},
            "joinSupport": middle["joinSupport"],
            "coreSupport": middle["coreSupport"],
            "retainSupport": middle["retainSupport"],
            "referenceSupport": 2,
            "sameIdentityMargin": copy.deepcopy(middle["margin"]),
            "residualSimilarity": .25,
        },
        {
            "name": "directed-lower-category-admission",
            "admission": dict(zip(LADDER, (.50, .45, .35, .30, .25))),
            "core": dict(zip(LADDER, (.60, .60, .50, .45, .40))),
            "retention": copy.deepcopy(middle["retain"]),
            "strongRelease": {"sourceMaximum": .30, "destinationMinimum": .60, "signedMargin": .30},
            "joinSupport": middle["joinSupport"],
            "coreSupport": middle["coreSupport"],
            "retainSupport": middle["retainSupport"],
            "referenceSupport": 2,
            "sameIdentityMargin": copy.deepcopy(middle["margin"]),
            "residualSimilarity": .25,
        },
        {
            "name": "directed-stricter-retention",
            "admission": copy.deepcopy(middle["admission"]),
            "core": dict(zip(LADDER, (.60, .60, .50, .45, .40))),
            "retention": dict(zip(LADDER, (.35, .30, .25, .20, .20))),
            "strongRelease": {"sourceMaximum": .30, "destinationMinimum": .60, "signedMargin": .30},
            "joinSupport": middle["joinSupport"],
            "coreSupport": middle["coreSupport"],
            "retainSupport": middle["retainSupport"],
            "referenceSupport": 2,
            "sameIdentityMargin": copy.deepcopy(middle["margin"]),
            "residualSimilarity": .25,
        },
        {
            "name": "directed-stronger-release",
            "admission": copy.deepcopy(middle["admission"]),
            "core": dict(zip(LADDER, (.60, .60, .50, .45, .40))),
            "retention": copy.deepcopy(middle["retain"]),
            "strongRelease": {"sourceMaximum": .25, "destinationMinimum": .65, "signedMargin": .35},
            "joinSupport": middle["joinSupport"],
            "coreSupport": middle["coreSupport"],
            "retainSupport": middle["retainSupport"],
            "referenceSupport": 2,
            "sameIdentityMargin": copy.deepcopy(middle["margin"]),
            "residualSimilarity": .25,
        },
    ]


def recipe_names():
    return tuple(recipe["name"] for recipe in recipes())


def runtime_policy(policy, recipe):
    """Bind the selected experiment without changing the saved standard policy."""
    validate_recipe(recipe)
    result = copy.deepcopy(policy)
    suffix = ":" + recipe["name"]
    if not result["version"].endswith(suffix):
        result["version"] += suffix
    for category in LADDER:
        rules = result["categoryPolicies"][category]
        rules["photoRouteMinimum"] = recipe["admission"][category]
        rules["photoRouteMargin"] = recipe["sameIdentityMargin"][category]
        if category in ("Sisters", "Angels"):
            # An explicit refusal survives selection; an absent draft flag does not.
            rules.setdefault("galleryAdmissionEnabled", True)
            rules["galleryAdmissionMinimumSimilarity"] = recipe["admission"][category]
    return result


def recipe_named(name):
    match = next((recipe for recipe in recipes() if recipe["name"] == name), None)
    if match is None:
        raise ValueError(f"unknown directed recipe: {name}")
    validate_recipe(match)
    return match


def validate_recipe(recipe):
    for axis in ("admission", "core", "retention", "sameIdentityMargin"):
        values = [recipe[axis][category] for category in LADDER]
        if any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not np.isfinite(v) or not 0 <= v <= 1 for v in values):
            raise ValueError(f"invalid directed recipe {axis}")
        if any(a < b for a, b in zip(values, values[1:])):
            raise ValueError(f"category ladder inverted: {axis}")
    for category in LADDER:
        if recipe["retention"][category] > min(recipe["core"][category], recipe["admission"][category]):
            raise ValueError("retention floor exceeds core or admission")
    release = recipe["strongRelease"]
    if not (0 <= release["sourceMaximum"] < release["destinationMinimum"] <= 1
            and 0 < release["signedMargin"] <= 1):
        raise ValueError("invalid strong-release axis")
    for key in ("joinSupport", "coreSupport", "retainSupport", "referenceSupport"):
        if type(recipe[key]) is not int or recipe[key] < 2:
            raise ValueError("independent support must be at least two")


def _digest_id(prefix, parts):
    raw = "\0".join([prefix, *(str(part) for part in parts)]).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]


def load_saved_source(source):
    """Load receipt-bound vectors without replaying historical grouping code."""
    from tools.art import likeness_diagnostics
    from tools.art import likeness_candidate_replay
    from . import reformation_report, review_packet, shadow

    source = pathlib.Path(source)
    if not source.is_absolute():
        raise ValueError("directed source report must be absolute")
    receipt_path = source / "receipt.json"
    receipt = json.loads(receipt_path.read_bytes())
    if (receipt.get("kind") != "reformation-state-receipt"
            or not receipt.get("reverseVerified") or receipt.get("libraryWrites")):
        raise ValueError("directed mode requires a reverse-verified, non-installing assessed state")
    bindings = {
        **receipt["inputs"], **receipt["code"],
        str(receipt_path): shadow.digest(receipt_path),
        **{str(review_packet.safe_path(source, name)): digest
           for name, digest in receipt["outputs"].items()},
    }
    likeness_diagnostics.verify(bindings)
    state = json.loads((source / "state.json").read_bytes())
    if any("membershipAssessment" not in row for row in state.get("rows", [])):
        raise ValueError("directed mode requires saved own-membership assessments")

    def find(name):
        matches = [pathlib.Path(path) for path in receipt["inputs"]
                   if pathlib.Path(path).name == name]
        if len(matches) != 1:
            raise ValueError(f"directed source requires exactly one bound {name}")
        return matches[0]

    run_names = ("run.json", "likeness-cache.json", "policy.json",
                 "seed-catalog.json", "config-snapshot.json")
    run_paths = {name: find(name) for name in run_names}
    raw = {name: path.read_bytes() for name, path in run_paths.items()}
    if sum(map(len, raw.values())) > MAX_SOURCE_JSON_BYTES:
        raise ValueError("directed source JSON exceeds the explicit 192 MiB cap")
    data = {name: json.loads(value) for name, value in raw.items()}
    run, cache = data["run.json"], data["likeness-cache.json"]
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in raw.items()}
    if (run.get("status") != "applied" or run.get("castSeedPolicy") != "core"
            or run.get("policy") != data["policy.json"]
            or run.get("continuationCacheSHA256") != hashes["likeness-cache.json"]
            or run.get("seedCatalogSHA256") != hashes["seed-catalog.json"]
            or run.get("configSnapshotSHA256") != hashes["config-snapshot.json"]
            or not np.array_equal(np.asarray(run.get("centeringMean"), dtype=float),
                                  np.asarray(cache.get("centeringMean"), dtype=float))
            or data["seed-catalog.json"].get("photos")
            or data["seed-catalog.json"].get("people")
            or data["seed-catalog.json"].get("actions")
            or run.get("workflowSelection", {}).get("policy") != {"mode": "all"}):
        raise ValueError("saved run, policy, cache, seed or configuration provenance is inconsistent")
    mean = np.asarray(run["centeringMean"], dtype=float)
    if mean.ndim != 1 or not mean.size or not np.isfinite(mean).all():
        raise ValueError("invalid saved centering mean")
    measurements, model_ids = {}, set()
    for item in cache.get("emb", {}).values():
        evidence = item.get("alignmentEvidence") or {}
        sha = evidence.get("sourceSha256")
        vector = item.get("v")
        if not sha or not vector:
            continue
        if sha in measurements and measurements[sha] != item:
            raise ValueError(f"conflicting cached measurements for content {sha}")
        model = evidence.get("model")
        model_id = hashlib.sha256(json.dumps(model, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if not model or evidence.get("modelId") != model_id:
            raise ValueError(f"invalid model provenance for cached content {sha}")
        model_ids.add(model_id)
        measurements[sha] = item
    if len(model_ids) != 1:
        raise ValueError("saved vectors require exactly one content-bound measurement model")
    vectors, photo_ids = {}, set()
    for photo in run["photos"]:
        pid = photo.get("photoId")
        if not pid or pid in photo_ids:
            raise ValueError("saved run requires unique stable photo IDs")
        photo_ids.add(pid)
        item = measurements.get(photo.get("preparedSHA256"))
        if item is None:
            if photo.get("castSeedCore") or "initialBestCast" in photo:
                raise ValueError(f"missing content-bound cached measurement: {pid}")
            continue
        vector = np.asarray(item["v"], dtype=float)
        if vector.shape != mean.shape or not np.isfinite(vector).all():
            raise ValueError(f"invalid cached vector: {pid}")
        vector = vector - mean
        norm = np.linalg.norm(vector)
        if not np.isfinite(norm) or norm == 0:
            raise ValueError(f"invalid centered cached vector: {pid}")
        vectors[pid] = vector / norm

    ledger_path = find("ledger.json")
    ledger = json.loads(ledger_path.read_bytes())
    evaluations = [
        json.loads(pathlib.Path(path).read_bytes()) for path in receipt["inputs"]
        if pathlib.Path(path).name.startswith("candidate_evaluation_")
    ]
    if len(evaluations) != 1:
        raise ValueError("directed source requires one saved human-review candidate evaluation")
    evaluation = evaluations[0]
    packets = [
        pathlib.Path(path) for path in receipt["inputs"]
        if pathlib.Path(path).name == "packet.json"
        and json.loads(pathlib.Path(path).read_bytes()).get("packetSHA256") == evaluation["packetSHA256"]
    ]
    if len(packets) != 1:
        raise ValueError("directed source human-review packet is unavailable")
    packet_path = packets[0]
    packet = json.loads(packet_path.read_bytes())
    candidate_path = packet_path.parent / "candidate.json"
    likeness_candidate_replay.validate_evaluation(
        packet, json.loads(candidate_path.read_bytes()), evaluation,
    )
    bindings[str(candidate_path)] = shadow.digest(candidate_path)
    ledger = reformation_report.effective_ledger(ledger, packet, evaluation)
    current_impl = {
        name: shadow.digest(pathlib.Path(__file__).parent / name)
        for name in shadow.REPLAY_MODULES
    }
    expected_impl = run.get("implementationHashes", {})
    drift = [
        {"module": name, "savedSHA256": expected_impl.get(name), "currentSHA256": current_impl[name]}
        for name in shadow.REPLAY_MODULES
        if expected_impl.get(name) and expected_impl[name] != current_impl[name]
    ]
    integrity = {
        "stateReceiptAndAllBindingsVerified": True,
        "measurementModelIds": sorted(model_ids),
        "savedVectorCount": len(vectors),
        "savedPhotoCount": len(run["photos"]),
        "imageReads": 0, "modelCalls": 0,
        "bindingCount": len(bindings),
        "sourceSHA256": {
            str(path): shadow.digest(pathlib.Path(path))
            for path in sorted(set([
                str(receipt_path), str(source / "state.json"),
                *(str(path) for path in run_paths.values()), str(ledger_path),
            ]))
        },
        "historicalImplementationDrift": drift,
        "assessmentBoundary": (
            "Saved state, input hashes, model provenance and vectors are verified. "
            "Historical grouping implementation is not replayed."
        ),
    }
    return state, run, vectors, ledger, bindings, integrity


def _category(folder):
    return folder.split("/", 1)[0] if folder else None


def _source_view(evidence, source):
    own = source.get("membershipAssessment", {}).get("own") or {}
    preferred = own.get("appearanceId")
    candidates = [
        view for view in evidence.views
        if view["folder"] == source.get("oldFolder")
    ]
    if preferred:
        match = next((view for view in candidates if view["appearanceId"] == preferred), None)
        if match and match["original"]:
            return match
    containing = [view for view in candidates if source["photoId"] in view["original"]]
    if containing:
        return containing[0]
    if candidates and source["photoId"] in evidence.vectors:
        return max(candidates, key=lambda view:
                   (evidence.measure(source["photoId"], view["original"]) or -1.)
                   if view["original"] else -2.)
    return candidates[0] if candidates else None


def _photo_evidence(evidence, source, photo):
    own = source.get("membershipAssessment", {}).get("own") or {}
    active_view = _source_view(evidence, source)
    source_view = getattr(evidence, "directed_source_views", {}).get(source["photoId"])
    if source_view is None:
        source_view = active_view
    frozen_refs = sorted(set(own.get("frozenReferencePhotoIds", [])))
    if not frozen_refs and source_view:
        frozen_refs = list(source_view["original"])
    frozen_refs = [pid for pid in frozen_refs if pid in evidence.vectors]
    core = bool(photo.get("castSeedCore") or source_view and
                source["photoId"] in source_view["frozenReferencePhotoIds"] or any(
        source["photoId"] in view["frozenReferencePhotoIds"]
        for view in evidence.views if view["folder"] == source.get("oldFolder")
    ))
    if "runtimeCastAdmission" in source:
        frozen_score = evidence.measure(source["photoId"], frozen_refs)
        score_basis = "content-bound independent own-seed measurement; no saved-score substitution"
    elif photo.get("castSeedCore") and photo.get("castSeedScore") is not None:
        frozen_score = float(photo["castSeedScore"])
        score_basis = "saved cast-seed core score"
    else:
        frozen_score = evidence.measure(source["photoId"], frozen_refs)
        score_basis = "saved pre-withdrawal own-reference inventory"
        if frozen_score is None and own.get("frozenScore") is not None:
            frozen_score = float(own["frozenScore"])
            score_basis = "saved pre-withdrawal own score"
    return {
        "view": source_view, "personId": source.get("oldPersonId") or (source_view or {}).get("personId"),
        "category": _category(source.get("oldFolder")), "frozenRefs": frozen_refs,
        "activeRefs": list(active_view["original"]) if active_view else [],
        "frozenScore": frozen_score, "scoreBasis": score_basis, "coreMember": core,
    }


def _label_map(evidence):
    labels = collections.defaultdict(dict)
    for pair in evidence.labels:
        a, b = pair["photoIds"]
        labels[a][b] = pair["label"]
        labels[b][a] = pair["label"]
    return labels


def _placement_protection(source):
    flags = set(source.get("placementBlocks", []))
    return sorted(flags - GROUP_PROTECTION_FLAGS), sorted(flags & GROUP_PROTECTION_FLAGS)


def _distinct_rival_scores(evidence, scores):
    people = sorted({view["personId"] for view in evidence.views})
    if not people:
        return {}
    values = np.column_stack([
        np.max(np.where(np.isfinite(scores[:, [i for i, view in enumerate(evidence.views)
                                               if view["personId"] == person]]),
                        scores[:, [i for i, view in enumerate(evidence.views)
                                   if view["personId"] == person]], -1.0), axis=1)
        for person in people
    ])
    winner = np.argmax(values, axis=1)
    best = values[np.arange(len(values)), winner]
    if len(people) > 1:
        second = np.partition(values, -2, axis=1)[:, -2]
    else:
        second = np.full(len(values), -1.0)
    return {person: np.where(winner == i, second, best) for i, person in enumerate(people)}


def _identity_ids(evidence, refs=(), person_id=None):
    result = {person_id} if person_id else set()
    for pid in refs:
        source = evidence.source.get(pid, {})
        result.update(source.get("sourceIdentityIds", []))
        if source.get("oldPersonId"):
            result.add(source["oldPersonId"])
    return result


def _identity_conflict(evidence, left, right):
    pairs = getattr(evidence, "configured_identity_negatives", set())
    return any(frozenset((a, b)) in pairs for a in left for b in right)


def _configured_negative_bindings(people, configured):
    aliases = collections.defaultdict(set)
    for person_id, person in people.items():
        for folder in [person["folder"], *person.get("folderHistory", [])]:
            aliases[folder.casefold()].add(person_id)
    pairs, diagnostics = set(), []
    for folders in configured:
        matches = [aliases[folder.casefold()] for folder in folders]
        if any(len(ids) > 1 for ids in matches):
            raise ValueError(f"ambiguous configured identity negative: {folders}")
        ids = [next(iter(found)) if found else None for found in matches]
        if ids[0] is not None and ids[0] == ids[1]:
            raise ValueError(f"configured identity negative resolves to the same owner: {folders}")
        participating = all(ids)
        if participating:
            pairs.add(frozenset(ids))
        diagnostics.append({
            "folders": list(folders), "personIds": ids,
            "status": "resolved" if participating else "nonparticipating-absent-owner",
            "absentFolders": [folder for folder, found in zip(folders, ids) if found is None],
        })
    return pairs, diagnostics


def _anchor_reference_hypotheses(evidence, view, candidates, recipe):
    floor = recipe["core"][view["category"]]
    operations = len(candidates) ** 2
    if operations > MAX_CLUSTER_OPERATIONS:
        raise ValueError("directed reference-neighbourhood operation cap exceeded")
    seen = set()
    for anchor in sorted(candidates):
        refs = sorted({anchor, *evidence.support(anchor, candidates, floor)})
        signature = tuple(refs)
        if signature in seen or len(refs) <= recipe["coreSupport"]:
            continue
        seen.add(signature)
        operations += len(refs) ** 2
        if operations > MAX_CLUSTER_OPERATIONS:
            raise ValueError("directed reference-neighbourhood qualification cap exceeded")
        qualified, stable = evidence.qualify(view, refs, recipe)
        if stable and anchor in qualified:
            yield qualified, refs


def prepare_reference_views(evidence, recipe):
    output = copy.copy(evidence)
    output.views = copy.deepcopy(evidence.views)
    output.directed_source_views = {
        pid: copy.deepcopy(_source_view(evidence, source)) for pid, source in evidence.source.items()
    }
    withdrawals = []
    for view in output.views:
        original = list(view["original"])
        view["candidateReferencePhotoIds"] = sorted(set(
            view.get("candidateReferencePhotoIds", original)
        ))
        qualified, stable = evidence.qualify(view, original, recipe)
        view["original"] = qualified if stable else []
        view["frozenReferencePhotoIds"] = list(view["original"])
        view["referenceStable"] = stable and bool(qualified)
        unavailable = sorted(set(view.get("unavailableReferencePhotoIds", [])))
        if set(original) != set(view["original"]) or unavailable or not view["referenceStable"]:
            withdrawals.append({
                "appearanceId": view["appearanceId"], "personId": view["personId"], "folder": view["folder"],
                "withdrawnPhotoIds": sorted(set(original) - set(view["original"])),
                "unavailableReferencePhotoIds": unavailable,
                "qualifiedPhotoIds": sorted(view["original"]), "stable": stable,
                "referenceUnavailable": not view["referenceStable"],
                "reason": "independent core validation; physical membership is unchanged",
            })
    # A heterogeneous source inventory can fail as a whole while containing
    # valid independent appearances. Discover subsets; never restore raw refs.
    recovered = []
    for view in output.views:
        candidates = sorted(set(view["candidateReferencePhotoIds"]) & evidence.eligible)
        if set(candidates) == set(view["original"]):
            continue
        hypotheses = [
            (cohort, cohort, "complete-link-candidate")
            for cohort in _complete_link_clusters(
                candidates, evidence, recipe["core"][view["category"]], MAX_CLUSTER_OPERATIONS)
        ]
        hypotheses.extend(
            (qualified, cohort, "independent-anchor-neighbourhood")
            for qualified, cohort in _anchor_reference_hypotheses(evidence, view, candidates, recipe)
        )
        seen_qualified = {tuple(view["original"])}
        for trial, cohort, construction in hypotheses:
            qualified, stable = evidence.qualify(view, trial, recipe)
            if not stable or not qualified or set(qualified) <= set(view["original"]) \
                    or tuple(qualified) in seen_qualified:
                continue
            seen_qualified.add(tuple(qualified))
            subset = copy.deepcopy(view)
            subset.update(
                appearanceId=_digest_id("qualified-view", [view["appearanceId"], *qualified]),
                original=qualified, frozenReferencePhotoIds=list(qualified), referenceStable=True,
                candidateReferencePhotoIds=list(cohort), reconstructedFrom=view["appearanceId"],
                referenceConstruction=construction,
            )
            recovered.append(subset)
    output.views.extend(recovered)
    for withdrawal in withdrawals:
        reconstructed = sorted({
            pid for view in recovered
            if view.get("reconstructedFrom") == withdrawal["appearanceId"] for pid in view["original"]
        })
        withdrawal["reconstructedQualifiedPhotoIds"] = reconstructed
        withdrawal["withdrawnPhotoIds"] = sorted(set(withdrawal["withdrawnPhotoIds"]) - set(reconstructed))
        withdrawal["qualifiedPhotoIds"] = sorted(set(withdrawal["qualifiedPhotoIds"]) | set(reconstructed))
        withdrawal["referenceUnavailable"] = not withdrawal["qualifiedPhotoIds"]
        if reconstructed:
            withdrawal["reason"] += "; coherent subsets independently requalified at unchanged core floors"
    candidates_by_person = collections.defaultdict(set)
    for view in output.views:
        candidates_by_person[view["personId"]].update(view["candidateReferencePhotoIds"])
    conflicted_people = {
        person_id for person_id, candidates in candidates_by_person.items()
        if any(evidence.negatives[pid].intersection(candidates) for pid in candidates)
        or _identity_conflict(evidence, _identity_ids(evidence, candidates, person_id),
                              _identity_ids(evidence, candidates, person_id))
    }
    for view in output.views:
        if view["personId"] not in conflicted_people:
            continue
        withdrawals.append({
            "appearanceId": view["appearanceId"], "personId": view["personId"], "folder": view["folder"],
            "withdrawnPhotoIds": list(view["original"]), "unavailableReferencePhotoIds": [],
            "qualifiedPhotoIds": [], "stable": False, "referenceUnavailable": True,
            "reason": "direct or configured negative evidence contradicts shared source ownership; explicit source-reference hold",
        })
        view.update(original=[], frozenReferencePhotoIds=[], referenceStable=False)
    for view in output.views:
        view["strongBaselinePhotoIds"] = [
            pid for pid in view["original"]
            if view["category"] in ("Sisters", "Angels")
            and (evidence.measure(pid, view["original"]) or -1.) >= .80
            and len(evidence.support(pid, view["original"], recipe["core"][view["category"]]))
            >= recipe["coreSupport"]
        ]
    return output, withdrawals


def reconcile_views(evidence, recipe, *, progress=None):
    """Reconcile mutually supported subsets without treating a bridge as personhood."""
    output = copy.copy(evidence)
    output.views = copy.deepcopy(evidence.views)
    output.directed_source_views = getattr(evidence, "directed_source_views", {
        pid: copy.deepcopy(_source_view(evidence, source)) for pid, source in evidence.source.items()
    })
    output.directed_owners = {}
    views = sorted(evidence.views, key=lambda view: (RANK[view["category"]], view["folder"], view["appearanceId"]))
    inventory = {view["appearanceId"]: list(view["original"]) for view in views}
    scores = evidence.scores(inventory)
    columns = {view["appearanceId"]: i for i, view in enumerate(evidence.views)}
    edges = []
    used_refs = set()
    for i, owner in enumerate(views):
        if owner.get("pooled"):
            continue
        if len(evidence.independent(owner["original"])) < recipe["joinSupport"]:
            continue
        for candidate in views[i + 1:]:
            if candidate.get("explicitIntent"):
                continue
            if owner["personId"] == candidate["personId"]:
                continue
            if _identity_conflict(
                    evidence, _identity_ids(evidence, owner["original"], owner["personId"]),
                    _identity_ids(evidence, candidate["original"], candidate["personId"])):
                continue
            if owner["category"] in ("Sisters", "Angels") and candidate["category"] in ("Sisters", "Angels"):
                continue
            if owner["category"] == candidate["category"]:
                # Same-rank canonical choice is deterministic, not a score-based demotion.
                if owner["folder"] > candidate["folder"]:
                    continue
            if len(evidence.independent(candidate["original"])) < recipe["joinSupport"]:
                continue
            floor = recipe["admission"][owner["category"]]
            left = [pid for pid in owner["original"] if pid not in used_refs]
            right = [pid for pid in candidate["original"] if pid not in used_refs]
            if not left or not right:
                continue
            # Cheap shortlist uses measured references; it is not the acceptance gate.
            cross = [scores[evidence.cache.indices[pid], columns[owner["appearanceId"]]]
                     for pid in right if pid in evidence.cache.indices]
            if not cross or not any(np.isfinite(value) and value >= floor for value in cross):
                continue
            original_left, original_right = list(left), list(right)
            core_floor = recipe["core"][owner["category"]]
            for _ in range(len(left) + len(right) + 1):
                kept_left = [pid for pid in left
                             if not evidence.negatives[pid].intersection(right)
                             and len(evidence.support(pid, right, floor)) >= recipe["joinSupport"]
                             and len(evidence.support(pid, left, core_floor)) >= recipe["coreSupport"]
                             and (evidence.measure(pid, left) or -1) >= core_floor]
                kept_right = [pid for pid in right
                              if not evidence.negatives[pid].intersection(left)
                              and len(evidence.support(pid, left, floor)) >= recipe["joinSupport"]
                              and len(evidence.support(pid, right, core_floor)) >= recipe["coreSupport"]
                              and (evidence.measure(pid, right) or -1) >= core_floor]
                if kept_left == left and kept_right == right:
                    break
                left, right = kept_left, kept_right
            if len(evidence.independent(left)) < recipe["joinSupport"] \
                    or len(evidence.independent(right)) < recipe["joinSupport"]:
                continue
            core_floor = recipe["core"][owner["category"]]
            if any(len(evidence.support(pid, refs, core_floor)) < recipe["coreSupport"]
                   or (evidence.measure(pid, refs) or -1) < core_floor
                   for refs in (left, right) for pid in refs):
                continue
            # Preserve all outside hypotheses, including other views of either old person.
            excluded = {owner["appearanceId"], candidate["appearanceId"]}
            outside = [columns[v["appearanceId"]] for v in evidence.views if v["appearanceId"] not in excluded]
            witnesses = []
            accepted = True
            for members, refs in ((left, right), (right, left)):
                for pid in members:
                    score = evidence.measure(pid, refs)
                    idx = evidence.cache.indices[pid]
                    rival = max((float(scores[idx, j]) for j in outside
                                 if np.isfinite(scores[idx, j])), default=-1.0)
                    if score is None or score < floor or score - rival < recipe["sameIdentityMargin"][owner["category"]]:
                        accepted = False
                        break
                    witnesses.append({"photoId": pid, "receivingScore": round(score, 6),
                                      "outsideRivalScore": round(rival, 6),
                                      "supportPhotoIds": evidence.support(pid, refs, floor)})
                if not accepted:
                    break
            if not accepted:
                continue
            view_id = _digest_id("reconciled-appearance", [owner["appearanceId"], candidate["appearanceId"], *right])
            attached = {
                **copy.deepcopy(candidate), "appearanceId": view_id,
                "personId": owner["personId"], "folder": owner["folder"], "category": owner["category"],
                "original": sorted(right), "frozenReferencePhotoIds": sorted(right),
                "sourceAppearanceId": candidate["appearanceId"], "sourceFolder": candidate["folder"],
                "referenceStable": True,
            }
            output.views.append(attached)
            residual = next(v for v in output.views if v["appearanceId"] == candidate["appearanceId"])
            residual["original"] = sorted(set(residual["original"]) - set(right))
            residual["frozenReferencePhotoIds"] = list(residual["original"])
            for pid in right:
                output.directed_owners[pid] = owner["personId"]
            used_refs.update(right)
            edges.append({
                "appearanceId": view_id, "ownerPersonId": owner["personId"], "ownerFolder": owner["folder"],
                "sourceFolder": candidate["folder"], "sourceAppearanceId": candidate["appearanceId"],
                "acceptedPhotoIds": sorted(right), "ownerWitnessPhotoIds": sorted(left),
                "exceptionPhotoIds": sorted(set(original_right) - set(right)),
                "ownerExceptionPhotoIds": sorted(set(original_left) - set(left)),
                "residualReferencePhotoIds": residual["original"], "perMemberEvidence": witnesses,
                "admissionFloor": floor, "outsideMargin": recipe["sameIdentityMargin"][owner["category"]],
                "basis": "mutual independent subset support and full frozen outside-rival margin",
            })
    output.views.sort(key=lambda view: view["appearanceId"])
    if progress:
        progress(f"Reconciled {len(edges)} qualified appearance subsets; original exceptions remain rivals.")
    return output, edges


def _target_options(evidence, score_matrix, recipe, label_map, *, inventory, base_inventory,
                    stage, source, source_info, photo_index, original_support=None, distinct_scores=None):
    pid = source["photoId"]
    if pid not in evidence.cache.indices:
        return []
    idx = evidence.cache.indices[pid]
    options = []
    for j, view in enumerate(evidence.views):
        refs = list(inventory[view["appearanceId"]])
        relevant_refs = evidence.others(pid, refs)
        score = score_matrix[idx, j]
        if not np.isfinite(score) or not relevant_refs:
            continue
        category = view["category"]
        labels = label_map.get(pid, {})
        conflicts = sorted(
            (ref, labels[ref]) for ref in relevant_refs if labels.get(ref) in ("different", "uncertain")
        )
        same_identity = (source_info["personId"] == view["personId"]
                         or getattr(evidence, "directed_owners", {}).get(pid) == view["personId"])
        distinct_cast_slot = (
            source_info["category"] in ("Sisters", "Angels")
            and category in ("Sisters", "Angels")
            and source_info["personId"] != view["personId"]
        )
        relevant_floor = recipe["admission"][category] - recipe["sameIdentityMargin"][category]
        if float(score) < relevant_floor and not conflicts and not same_identity and not distinct_cast_slot:
            continue
        support = evidence.support(pid, refs, recipe["admission"][category])
        independent_refs = evidence.independent(relevant_refs)
        base_refs = base_inventory[view["appearanceId"]]
        base_support = evidence.support(pid, base_refs, recipe["admission"][category]) if stage == 2 else []
        blockers = []
        if _identity_conflict(
                evidence, _identity_ids(evidence, [pid], source_info["personId"]),
                _identity_ids(evidence, refs, view["personId"])):
            blockers.append("configured-different-identity-veto")
        if score < recipe["admission"][category]:
            blockers.append("below-admission-floor")
        if len(support) < recipe["joinSupport"]:
            blockers.append("insufficient-independent-member-support")
        if conflicts:
            blockers.append("exact-different-or-uncertain-veto")
        if not view.get("referenceStable", True):
            blockers.append("frozen-reference-qualification-incomplete")
        if view.get("pooled"):
            blockers.append("unestablished-pooled-destination")
        if stage == 2 and len(base_support) < 1:
            blockers.append("no-independent-original-boundary-support")
        if source_info["category"] not in (*RANK, "Various"):
            blockers.append("source-category-outside-directed-ladder")
        if distinct_cast_slot:
            blockers.append("distinct-authored-cast-slot")
        if distinct_scores is None:
            margin_competitors = [
                float(score_matrix[idx, other_index])
                for other_index, other in enumerate(evidence.views)
                if other["personId"] != view["personId"] and np.isfinite(score_matrix[idx, other_index])
            ]
            best_distinct = max(margin_competitors, default=-1.0)
        else:
            best_distinct = float(distinct_scores[view["personId"]][idx])
        signed_margin = float(score) - best_distinct
        cast_admission = None
        if category in ("Sisters", "Angels") and view["folder"] != source.get("oldFolder") \
                and "runtimeCastAdmission" in source:
            from .policy import evaluate_cast_admission

            frozen_score = evidence.measure(pid, base_refs)
            frozen_margin = max(0., float(frozen_score) - best_distinct) if frozen_score is not None else 0.
            maximum = evidence.settings["identityActions"]["independentEvidenceMaximumSimilarity"]
            frozen_support = [
                ref for ref in evidence.support(pid, base_refs, recipe["admission"][category])
                if evidence.cache.get(pid, ref) <= maximum
            ]
            cast_admission = {
                **source["runtimeCastAdmission"], "folder": view["folder"],
                "score": float(frozen_score) if frozen_score is not None else None,
                "margin": frozen_margin, "independentSupport": len(frozen_support),
                "referencePhotoIds": sorted(frozen_support),
            }
            cast_admission.update(evaluate_cast_admission(
                category, policy=evidence.settings, score=cast_admission["score"],
                margin=cast_admission["margin"],
                independent_support=cast_admission["independentSupport"],
                quality_eligible=cast_admission["qualityEligible"],
                metadata_stale=cast_admission["metadataStale"],
                rejection_history=cast_admission["rejectionHistory"],
                protected=cast_admission["protected"],
            ))
            if cast_admission["decision"] != "admit":
                blockers.append("cast-gallery-admission: " + cast_admission["reason"])
        options.append({
            "appearanceId": view["appearanceId"], "personId": view["personId"],
            "folder": view["folder"], "category": category, "score": round(float(score), 6),
            "admissionFloor": recipe["admission"][category],
            "independentSupportPhotoIds": sorted(support),
            "originalBoundarySupportPhotoIds": sorted(base_support),
            "independentReferenceCount": len(independent_refs),
            "referencePhotoIds": sorted(relevant_refs),
            "sharedOriginalReferencePhotoIds": sorted(set(relevant_refs) & set(base_refs)),
            "exactConflicts": [{"photoId": other, "label": label} for other, label in conflicts],
            "veto": bool(conflicts), "sameIdentity": same_identity,
            "signedDistinctRivalMargin": round(signed_margin, 6),
            "bestDistinctRivalScore": round(best_distinct, 6) if best_distinct >= -1 else None,
            "stage": stage, "blockers": blockers,
            "individuallyQualified": not blockers,
            "castAdmission": cast_admission,
        })
    return sorted(options, key=lambda row: (-row["score"], row["appearanceId"], row["personId"]))


def validate_growth(evidence, recipe, base_inventory, staged_by_view, rejected, boundary):
    dispositions = []
    for view in evidence.views:
        key = view["appearanceId"]
        additions = set(staged_by_view.get(key, []))
        if not additions:
            continue
        base = set(base_inventory[key])
        qualified, stable = evidence.qualify(view, sorted(base | additions), recipe)
        kept = additions & set(qualified) if stable and base <= set(qualified) else set()
        removed = additions - kept
        staged_by_view[key] = sorted(kept)
        for pid in sorted(removed):
            rejected.add((pid, key))
            dispositions.append({
                "photoId": pid, "appearanceId": key, "boundary": boundary,
                "reason": "joint reference validation failed or would invalidate frozen-base prerequisites",
                "physicalPlacementChanged": False,
            })
    return dispositions


def _source_incompatibility(evidence, source, source_info, recipe, labels):
    pid = source["photoId"]
    explicit = sorted(
        other for other, label in labels.get(pid, {}).items()
        if label == "different" and other in source_info["frozenRefs"]
    )
    independent_source_refs = evidence.independent(evidence.others(pid, source_info["frozenRefs"]))
    score = source_info["frozenScore"]
    measured = (
        score is not None and score <= recipe["strongRelease"]["sourceMaximum"]
        and len(independent_source_refs) >= recipe["referenceSupport"]
    )
    return {
        "qualified": bool(explicit or measured),
        "basis": "exact human different-pair" if explicit else
        "low score against frozen source references with independent witnesses" if measured else None,
        "exactDifferentWitnesses": explicit,
        "frozenSourceScore": round(float(score), 6) if score is not None else None,
        "independentSourceReferenceIds": sorted(independent_source_refs),
    }


def _strong_destination(option, recipe):
    return (
        option["individuallyQualified"]
        and option["score"] >= recipe["strongRelease"]["destinationMinimum"]
        and len(option["independentSupportPhotoIds"]) >= recipe["referenceSupport"]
        and not option["veto"]
        and option["signedDistinctRivalMargin"] >= recipe["strongRelease"]["signedMargin"]
        and "distinct-authored-cast-slot" not in option["blockers"]
    )


def _complete_link_clusters(ids, evidence, threshold, max_operations):
    ids = sorted(ids)
    if len(ids) * len(ids) > max_operations:
        raise ValueError("directed residual-cluster operation cap exceeded; report is incomplete")
    conflicts = evidence.negatives
    clusters = []
    for pid in ids:
        for group in clusters:
            if all(
                pid in evidence.cache.indices and other in evidence.cache.indices
                and evidence.hashes[pid] != evidence.hashes[other]
                and other not in conflicts[pid]
                and not _identity_conflict(evidence, _identity_ids(evidence, [pid]),
                                            _identity_ids(evidence, [other]))
                and evidence.cache.get(pid, other) >= threshold
                for other in group
            ):
                group.append(pid)
                break
        else:
            clusters.append([pid])
    return clusters


def _make_groups(rows, evidence, recipe):
    groups = {}
    associations = collections.defaultdict(list)

    def add(kind, key, member_ids, parent, source_folder, display, lineage):
        for cluster in _complete_link_clusters(
            member_ids, evidence, recipe["residualSimilarity"], MAX_CLUSTER_OPERATIONS,
        ):
            anchor = cluster[0]
            group_id = _digest_id("directed", [kind, key, anchor])
            lineage_id = _digest_id("lineage", [source_folder or "", parent or "", anchor])
            groups[group_id] = {
                "id": group_id, "lineageId": lineage_id, "name": display,
                "state": kind, "memberPhotoIds": cluster, "candidateParentId": parent,
                "sourceFolder": source_folder,                 "lineageIds": sorted(value for value in set(lineage) if value),
                "physicalHomeRemainsSource": kind == "tentative",
                "referenceAuthority": "none; reference recovery is separately staged and evidenced",
            }
            for pid in cluster:
                associations[pid].append(group_id)

    supported = collections.defaultdict(list)
    tentative = collections.defaultdict(list)
    residual = collections.defaultdict(list)
    for row in rows:
        supported_info = row["supportedAssociation"] or row["correctionAssociation"]
        if supported_info:
            info = supported_info
            key = (info["appearanceId"], row["oldFolder"])
            supported[key].append(row["photoId"])
        elif row["membershipState"] == "supported-in-place":
            supported[(f'existing:{row["sourcePersonId"]}', row["oldFolder"])].append(row["photoId"])
        for option in row["tentativeAssociations"]:
            tentative[(option["appearanceId"], row["oldFolder"])].append(row["photoId"])
        if not supported_info and row["membershipState"] != "supported-in-place" \
                and not row["tentativeAssociations"]:
            residual[row["oldFolder"]].append(row["photoId"])
    for (view_id, folder), members in sorted(supported.items()):
        view = next((item for item in evidence.views if item["appearanceId"] == view_id), None)
        if view:
            parent_id, parent_folder = view["personId"], view["folder"]
            label = f'{view["folder"]} · {folder} appearance'
            lineage = [view_id, parent_id]
        else:
            first = next(row for row in rows if row["photoId"] in members)
            parent_id, parent_folder = first["sourcePersonId"], folder
            label = f'{folder} · supported existing identity'
            lineage = [parent_id] if parent_id else []
        add("supported", [view_id, folder], members, parent_id, folder, label,
            [*lineage, *(row["sourcePersonId"] for row in rows if row["photoId"] in members)])
    for (view_id, folder), members in sorted(tentative.items()):
        view = next(item for item in evidence.views if item["appearanceId"] == view_id)
        label = f'{view["folder"]} · tentative association'
        add("tentative", [view_id, folder], members, view["personId"], folder, label,
            [view_id, view["personId"]])
    for folder, members in sorted(residual.items()):
        identity = next((row["sourcePersonId"] for row in rows if row["oldFolder"] == folder), None)
        label = f'{folder or "Unknown source"} · residual cluster'
        add("residual", [folder], members, identity, folder, label, [identity] if identity else [])
    for row in rows:
        row["clusterIds"] = sorted(set(associations[row["photoId"]]))
    return [groups[key] for key in sorted(groups)]


def run_variant(evidence, recipe, *, progress=None, reconcile=False):
    validate_recipe(recipe)
    reconciliation = []
    withdrawals = []
    boundary_snapshots = []
    boundary_bytes = 0

    def snapshot(boundary_id, current, inventory, *, options=None, decisions=None, groups=None):
        nonlocal boundary_bytes
        frozen_inventory = {key: sorted(refs) for key, refs in sorted(inventory.items())}
        own_views = collections.defaultdict(list)
        for view in current.views:
            own_views[view["personId"]].append(view)
        rows = []
        decision_map = {row["photoId"]: row for row in decisions or []}
        for pid, source in sorted(current.source.items()):
            person_id = source.get("oldPersonId")
            own = own_views[person_id]
            own_refs = sorted({ref for view in own for ref in inventory[view["appearanceId"]]})
            selected_options = (options or {}).get(pid, [])
            best = next((option for option in selected_options if not option["sameIdentity"]), None)
            decision = decision_map.get(pid)
            association = ((decision.get("supportedAssociation") or decision.get("correctionAssociation"))
                           if decision else None)
            source_path = current.photos[pid].get("destination")
            source_path = source.get("sourcePath") or source_path or f'{source.get("oldFolder")}/{pid}'
            destination = source_path
            if association:
                destination = f'{association["folder"]}/gallery/{pathlib.PurePosixPath(source_path).name}'
            rows.append({
                "photoId": pid, "source": source_path, "sourceDestination": source_path,
                "contentHash": current.hashes.get(pid),
                "destination": destination, "proposedDestination": destination,
                "personId": association["personId"] if association else person_id,
                "groupId": (decision.get("clusterIds") or [None])[0] if decision and groups else None,
                "clusterIds": list(decision.get("clusterIds", [])) if decision and groups else [],
                "status": decision["membershipState"] if decision else
                "initial-options-assessed" if options is not None else "membership-not-yet-assessed",
                "coreUse": bool(decision["referenceUseEligible"]) if decision else False,
                "referenceEligibleAtBoundary": pid in own_refs,
                "verifiedStrongBaselineAtBoundary": any(
                    pid in view.get("strongBaselinePhotoIds", []) for view in own
                ),
                "qualifiedOwnReferenceCount": len(own_refs),
                "qualifiedOwnReferenceViewIds": sorted(view["appearanceId"] for view in own
                                                      if inventory[view["appearanceId"]]),
                "score": current.measure(pid, own_refs) if pid in current.vectors else None,
                "rivalScore": best["score"] if best else None,
                "margin": best["signedDistinctRivalMargin"] if best else None,
                "independentSupportPhotoIds": best["independentSupportPhotoIds"][:recipe["joinSupport"]] if best else [],
                "independentSupportCount": len(best["independentSupportPhotoIds"]) if best else 0,
                "admissionBlockers": best["blockers"] if best else [],
                "reason": decision["shadowAction"] if decision else
                "frozen initial admission options; no final placement decision yet" if options is not None else
                "qualified reference state only; no membership or placement decision yet",
                "placementBlocks": list(source.get("placementBlocks", [])),
            })
            if boundary_id == "references":
                seed_view = getattr(current, "directed_source_views", {}).get(pid)
                seed_refs = (seed_view or {}).get("original", [])
                category = (seed_view or {}).get("category")
                if category in RANK and pid in current.vectors:
                    floor = recipe["core"][category]
                    support = current.support(pid, seed_refs, floor)
                    rows[-1]["candidateReferenceQualification"] = {
                        "appearanceId": seed_view["appearanceId"],
                        "independentOwnCentroidScore": current.measure(pid, seed_refs),
                        "centroidMinimum": floor, "pairSupportMinimum": floor,
                        "requiredIndependentPairSupport": recipe["coreSupport"],
                        "actualIndependentPairSupport": len(support),
                        "exactConflictCount": len(current.negatives[pid].intersection(seed_refs)),
                        "configuredIdentityConflict": _identity_conflict(
                            current, _identity_ids(current, [pid], seed_view["personId"]),
                            _identity_ids(current, seed_refs, seed_view["personId"])),
                        "eligibleMeasurement": pid in current.eligible,
                        "reason": "qualified in surviving own view" if pid in own_refs else
                        "not qualified; inspect independent centroid/pair support, conflicts and withdrawal records",
                    }
        frozen = copy.deepcopy({
            "id": boundary_id, "evidenceKind": "computational-boundary-snapshot",
            "rows": rows, "referenceInventory": frozen_inventory,
            "witnessPolicy": {
                "recipe": recipe, "policyVersion": getattr(current, "settings", {}).get("version"),
                "independence": "self/content/near-duplicate excluded; independent witnesses",
                "placement": "unchanged until a qualified proposal is recorded",
                "configuredDistinctPersonPairs": sorted(
                    sorted(pair) for pair in getattr(current, "configured_identity_negatives", set())
                ),
            },
            "groups": groups or [],
            "referenceWithdrawals": withdrawals if boundary_id == "references" else [],
            "candidateReferenceInventory": {
                view["appearanceId"]: list(view.get("candidateReferencePhotoIds", []))
                for view in current.views
            } if boundary_id == "references" else {},
            "referenceGrowthWitnessKeys": [
                {"photoId": pid, "appearanceId": view_id,
                 "provenanceRecord": "referenceRecovery.provenance"}
                for pid, view_id in sorted(staged_evidence)
                if pid in inventory.get(view_id, [])
            ] if boundary_id.startswith("growth-") else [],
        })
        payload = json.dumps(frozen, sort_keys=True, separators=(",", ":")).encode()
        boundary_bytes += len(payload)
        if boundary_bytes > 64 * 1024 * 1024:
            raise ValueError("directed immutable boundary evidence exceeds 64 MiB; comparison incomplete")
        boundary_snapshots.append(frozen)

    if reconcile:
        evidence, withdrawals = prepare_reference_views(evidence, recipe)
        snapshot("references", evidence, {view["appearanceId"]: view["original"] for view in evidence.views})
        if progress:
            progress(f"Validated initial reference cores: {len(withdrawals)} inventories have withdrawals/unavailable references.")
        evidence, reconciliation = reconcile_views(evidence, recipe, progress=progress)
    base_inventory = {view["appearanceId"]: list(view["original"]) for view in evidence.views}
    snapshot("reconciliation", evidence, base_inventory)
    base_scores = evidence.scores(base_inventory)
    base_distinct = _distinct_rival_scores(evidence, base_scores)
    labels = _label_map(evidence)
    sources = evidence.source
    photos = evidence.photos
    source_info = {
        pid: _photo_evidence(evidence, source, photos[pid])
        for pid, source in sources.items()
    }
    # Stage-one additions must first pass member admission, then the stricter reference-core gate.
    staged_by_view = collections.defaultdict(list)
    staged_evidence = {}
    no_growth_upward = set()
    initial_options = {}
    for pid in sorted(sources):
        if pid not in evidence.eligible or pid not in evidence.cache.indices:
            continue
        info = source_info[pid]
        idx = evidence.cache.indices[pid]
        candidates = []
        source = sources[pid]
        if not info["category"] or info["category"] not in (*RANK, "Various"):
            continue
        member_options = _target_options(
            evidence, base_scores, recipe, labels,
            inventory=base_inventory, base_inventory=base_inventory, stage=1,
            source=source, source_info=info, photo_index=idx, distinct_scores=base_distinct,
        )
        initial_options[pid] = member_options
        if info["category"] not in RANK:
            continue
        if not _placement_protection(source)[0] and not source.get("explicitIntentFolder") and any(
            option["individuallyQualified"]
            and RANK[option["category"]] < RANK[info["category"]]
            and option["signedDistinctRivalMargin"] >= recipe["sameIdentityMargin"][option["category"]]
            for option in member_options
        ):
            no_growth_upward.add(pid)
        for option in member_options:
            view = next(
                (view for view in evidence.views if view["appearanceId"] == option["appearanceId"]),
                None,
            )
            if view is None:
                continue
            same_identity = info["personId"] == view["personId"]
            if not same_identity and RANK[view["category"]] >= RANK[info["category"]]:
                continue
            refs = base_inventory[view["appearanceId"]]
            if pid in refs or evidence.hashes[pid] in {evidence.hashes[r] for r in refs}:
                continue
            score = option["score"]
            if not option["individuallyQualified"] or score < recipe["core"][view["category"]]:
                continue
            core_floor = max(recipe["admission"][view["category"]], recipe["core"][view["category"]])
            core_support = evidence.support(pid, refs, core_floor)
            if len(core_support) < recipe["referenceSupport"]:
                continue
            if option["signedDistinctRivalMargin"] < recipe["sameIdentityMargin"][view["category"]]:
                continue
            candidates.append((
                float(score), view["appearanceId"], view,
                option["independentSupportPhotoIds"], sorted(core_support),
            ))
        candidates.sort(key=lambda item: (-item[0], item[1]))
        if len(candidates) != 1:
            continue
        score, _, view, admission_support, core_support = candidates[0]
        view_id = view["appearanceId"]
        existing = base_inventory[view_id]
        current = staged_by_view[view_id]
        candidate_set = [*existing, *current, pid]
        if pid not in evidence.independent(candidate_set):
            continue
        staged_by_view[view_id].append(pid)
        staged_evidence[(pid, view_id)] = {
            "originalScore": round(score, 6),
            "originalAdmissionSupportPhotoIds": admission_support,
            "originalCoreSupportPhotoIds": core_support,
            "originalReferencePhotoIds": sorted(existing),
            "contentHash": evidence.hashes[pid],
        }

    snapshot("membership", evidence, base_inventory, options=initial_options)
    rejected_references = set()
    growth_validation = []
    if reconcile:
        growth_validation.extend(validate_growth(
            evidence, recipe, base_inventory, staged_by_view, rejected_references, 1,
        ))
    stage_inventory = {
        view_id: sorted(set(refs + staged_by_view.get(view_id, [])))
        for view_id, refs in base_inventory.items()
    }
    stage_scores = evidence.scores(stage_inventory)
    snapshot("growth-1", evidence, stage_inventory)
    recovery_history = [{"boundary": 1, "addedPhotoIds": sorted({p for refs in staged_by_view.values() for p in refs})}]
    for boundary in range(2, MAX_RECOVERY_BOUNDARIES + 1):
        distinct = _distinct_rival_scores(evidence, stage_scores)
        additions = []
        for pid in sorted(sources):
            if pid not in evidence.eligible:
                continue
            info = source_info[pid]
            if info["category"] not in RANK:
                continue
            options = _target_options(
                evidence, stage_scores, recipe, labels, inventory=stage_inventory,
                base_inventory=base_inventory, stage=2, source=sources[pid], source_info=info,
                photo_index=evidence.cache.indices[pid], distinct_scores=distinct,
            )
            qualified = []
            for option in options:
                view_id = option["appearanceId"]
                if pid in stage_inventory[view_id] or (pid, view_id) in rejected_references \
                        or not option["individuallyQualified"]:
                    continue
                if not option["sameIdentity"] and RANK[option["category"]] >= RANK[info["category"]]:
                    continue
                if option["signedDistinctRivalMargin"] < recipe["sameIdentityMargin"][option["category"]]:
                    continue
                # New additions never self-certify an otherwise unsupported reference.
                core_support = evidence.support(pid, base_inventory[view_id], recipe["core"][option["category"]])
                if len(option["originalBoundarySupportPhotoIds"]) < recipe["joinSupport"] \
                        or len(core_support) < recipe["coreSupport"] \
                        or option["score"] < recipe["core"][option["category"]]:
                    continue
                if pid not in evidence.independent([*stage_inventory[view_id], pid]):
                    continue
                qualified.append((option, core_support))
            if len(qualified) == 1:
                additions.append((pid, *qualified[0]))
        recovery_history.append({"boundary": boundary, "addedPhotoIds": sorted({pid for pid, _, _ in additions})})
        if not additions:
            break
        if boundary == MAX_RECOVERY_BOUNDARIES:
            raise ValueError("appearance recovery reached its explicit boundary cap; comparison incomplete")
        for pid, option, core_support in additions:
            view_id = option["appearanceId"]
            staged_by_view[view_id].append(pid)
            staged_evidence[(pid, view_id)] = {
                "boundary": boundary, "originalScore": option["score"],
                "originalAdmissionSupportPhotoIds": option["originalBoundarySupportPhotoIds"],
                "originalCoreSupportPhotoIds": core_support,
                "originalReferencePhotoIds": sorted(base_inventory[view_id]),
                "contentHash": evidence.hashes[pid],
            }
        if reconcile:
            growth_validation.extend(validate_growth(
                evidence, recipe, base_inventory, staged_by_view, rejected_references, boundary,
            ))
        stage_inventory = {view_id: sorted(set(refs + staged_by_view.get(view_id, [])))
                           for view_id, refs in base_inventory.items()}
        stage_scores = evidence.scores(stage_inventory)
        snapshot(f"growth-{boundary}", evidence, stage_inventory)
        if progress:
            progress(f"Frozen appearance recovery boundary {boundary}: {len(additions)} original-witness additions.")
    stage_distinct = _distinct_rival_scores(evidence, stage_scores)
    rows = []
    for pid in sorted(sources):
        source = sources[pid]
        photo = photos[pid]
        info = source_info[pid]
        blockers, group_protection = _placement_protection(source)
        explicit_owner = source.get("explicitIntentFolder")
        source_view = info["view"]
        own_score = evidence.measure(pid, info["activeRefs"]) if source_view and pid in evidence.cache.indices else None
        own_support = evidence.support(pid, info["activeRefs"], recipe["retention"][info["category"]]) \
            if info["category"] in RANK and pid in evidence.cache.indices else []
        own_vetoes = [
            {"photoId": ref, "label": labels[pid][ref]}
            for ref in info["activeRefs"] if labels.get(pid, {}).get(ref) in ("different", "uncertain")
        ]
        retention_supported = (
            own_score is not None and info["category"] in RANK
            and own_score >= recipe["retention"][info["category"]]
            and len(own_support) >= recipe["retainSupport"] and not own_vetoes
        )
        core_use = (
            info["coreMember"] and own_score is not None and info["category"] in RANK
            and any(pid in stage_inventory[view["appearanceId"]] for view in evidence.views
                    if view["personId"] == info["personId"])
            and own_score >= recipe["core"][info["category"]]
            and len(evidence.independent(evidence.others(pid, info["activeRefs"]))) >= recipe["coreSupport"]
            and not own_vetoes
        )
        current_index = evidence.cache.indices.get(pid)
        matrix = stage_scores if current_index is not None else base_scores
        stage = 2 if stage_inventory != base_inventory else 1
        options = _target_options(
            evidence, matrix, recipe, labels, inventory=stage_inventory,
            base_inventory=base_inventory, stage=stage, source=source,
            source_info=info, photo_index=current_index, original_support=None,
            distinct_scores=stage_distinct,
        ) if current_index is not None else []
        candidate_options = []
        for option in options:
            if option["sameIdentity"] and option["folder"] == source.get("oldFolder"):
                continue
            if info["category"] == "Various" and option["individuallyQualified"] \
                    and option["signedDistinctRivalMargin"] >= recipe["sameIdentityMargin"][option["category"]]:
                option["decision"] = "supported-upward-same-identity"
                option["relationshipStatus"] = "individually-supported-incoming-association"
                candidate_options.append(option)
                continue
            if getattr(evidence, "directed_owners", {}).get(pid) == option["personId"] \
                    and info["category"] == option["category"] and option["individuallyQualified"] \
                    and option["signedDistinctRivalMargin"] >= recipe["sameIdentityMargin"][option["category"]]:
                option["decision"] = "supported-same-rank-reconciliation"
                option["relationshipStatus"] = "mutually-reconciled-same-identity"
                candidate_options.append(option)
                continue
            if option["sameIdentity"] and info["category"] in RANK \
                    and RANK[option["category"]] < RANK[info["category"]]:
                if option["individuallyQualified"] and option["signedDistinctRivalMargin"] >= \
                        recipe["sameIdentityMargin"][option["category"]]:
                    option["decision"] = "supported-upward-same-identity"
                    option["relationshipStatus"] = "individually-supported-same-identity"
                    option["canonicalOwnerFolder"] = option["folder"]
                    candidate_options.append(option)
                    continue
            elif not option["sameIdentity"] and info["category"] in RANK \
                    and option["category"] in RANK \
                    and RANK[option["category"]] < RANK[info["category"]]:
                if option["individuallyQualified"] and option["signedDistinctRivalMargin"] >= \
                        recipe["sameIdentityMargin"][option["category"]]:
                    option["decision"] = "supported-upward-same-identity"
                    option["relationshipStatus"] = "individually-supported-same-identity"
                    option["canonicalOwnerFolder"] = option["folder"]
                    candidate_options.append(option)
                    continue
            option["decision"] = "candidate-rival"
            candidate_options.append(option)
        incompatibility = _source_incompatibility(evidence, source, info, recipe, labels)
        release_candidates = [
            option for option in candidate_options
            if not option["sameIdentity"] and _strong_destination(option, recipe)
            and incompatibility["qualified"]
        ]
        release_candidates.sort(key=lambda row: (-row["score"], row["appearanceId"]))
        supported_options = [
            option for option in candidate_options
            if option["decision"] in ("supported-upward-same-identity", "supported-same-rank-reconciliation")
        ]
        supported_options.sort(key=lambda row: (
            RANK[row["category"]], -row["score"], row["appearanceId"],
        ))
        proposal = None
        action = "retain-in-place"
        release_reason = None
        if explicit_owner:
            action = "explicit-intent-preserved"
        elif blockers:
            action = "physical-lock-preserved"
        elif supported_options:
            proposal = supported_options[0]
            action = ("supported-same-rank-appearance" if proposal["decision"] == "supported-same-rank-reconciliation"
                      else "supported-upward-appearance")
            proposal["canonicalOwnerFolder"] = proposal["folder"]
            proposal["canonicalOwnerReason"] = "individually supported same-identity link; hierarchy applied after qualification"
        elif release_candidates:
            proposal = release_candidates[0]
            action = "strong-wrong-identity-correction"
            release_reason = incompatibility
        tentative = []
        for option in candidate_options:
            if option is proposal:
                continue
            near = option["score"] >= option["admissionFloor"] - recipe["sameIdentityMargin"][option["category"]]
            if near or option["veto"]:
                tentative.append(option)
        core_initial = bool(
            info["coreMember"] and photo.get("castSeedScore") is not None
            and float(photo["castSeedScore"]) >= recipe["core"][info["category"]]
            if info["category"] in RANK else False
        )
        move = proposal is not None
        dest = proposal["folder"] if move else source.get("oldFolder")
        source_id = info["personId"]
        rows.append({
            "photoId": pid, "oldFolder": source.get("oldFolder"), "sourcePersonId": source_id,
            "sourceCategory": info["category"], "currentDestination": photo.get("destination"),
            "candidateDestination": dest if move else None, "shadowAction": action,
            "membershipState": (
                "supported-association" if proposal and action in ("supported-upward-appearance", "supported-same-rank-appearance")
                else "strong-correction-candidate" if proposal and action == "strong-wrong-identity-correction"
                else "supported-in-place" if retention_supported
                else "uncertain-retained-in-place" if own_score is None or not retention_supported
                else "residual"
            ),
            "frozenSourceScore": round(float(info["frozenScore"]), 6)
            if info["frozenScore"] is not None else None,
            "frozenSourceScoreBasis": info["scoreBasis"],
            "currentOwnScore": round(float(own_score), 6) if own_score is not None else None,
            "strongInitialCastCoreDiagnostic": core_initial,
            "verifiedStrongBaseline": any(
                pid in view.get("strongBaselinePhotoIds", []) for view in evidence.views
                if view["personId"] == info["personId"]
            ),
            "referenceUseEligible": bool(core_use),
            "referenceUseDisposition": "eligible" if core_use else
            "withdrawn-or-unqualified-independent-of-placement" if info["coreMember"] else "not-a-core-reference",
            "ownIndependentSupportPhotoIds": sorted(own_support),
            "ownExactConflicts": own_vetoes,
            "sourceIncompatibility": incompatibility,
            "placementBlocks": blockers, "groupProtectionMetadata": group_protection,
            "explicitIntentFolder": explicit_owner,
            "supportedAssociation": proposal if action in ("supported-upward-appearance", "supported-same-rank-appearance") else None,
            "correctionAssociation": proposal if action == "strong-wrong-identity-correction" else None,
            "tentativeAssociations": tentative,
            "familyAssessmentCandidates": [
                option for option in options
                if any(conflict["label"] == "different" for conflict in option["exactConflicts"])
                and option["score"] >= max(.50, option["admissionFloor"])
                and len(option["independentSupportPhotoIds"]) >= recipe["referenceSupport"]
            ],
            "fictionalFamilyAssessment": {
                "eligible": bool(any(
                    any(conflict["label"] == "different" for conflict in option["exactConflicts"])
                    and option["score"] >= max(.50, option["admissionFloor"])
                    and len(option["independentSupportPhotoIds"]) >= recipe["referenceSupport"]
                    for option in options
                )),
                "status": "candidate assessment only; no family or story role inferred",
            },
            "rivals": options,
            "allRelevantRivalsCount": len(options),
            "stagedReferenceCandidates": sorted(
                view_id for view_id, members in staged_by_view.items() if pid in members
            ),
            "reconciledAppearanceIds": sorted(
                edge["appearanceId"] for edge in reconciliation if pid in edge["acceptedPhotoIds"]
            ),
        })

    snapshot("final-membership", evidence, stage_inventory, decisions=rows)
    clusters = _make_groups(rows, evidence, recipe)
    snapshot("appearance-hypotheses", evidence, stage_inventory, decisions=rows, groups=clusters)
    for row in rows:
        if row["correctionAssociation"]:
            row["clusterIds"] = sorted(set(row["clusterIds"] + [
                group["id"] for group in clusters
                if row["photoId"] in group["memberPhotoIds"]
                and group["state"] == "supported"
            ]))
    changed = [row for row in rows if row["candidateDestination"] and row["candidateDestination"] != row["oldFolder"]]
    cast_rows = [row for row in rows if row["sourceCategory"] in ("Sisters", "Angels")]
    strong_cast = [row for row in cast_rows if row["strongInitialCastCoreDiagnostic"]]
    by_category = {}
    for category in LADDER:
        rows_for_category = [row for row in rows if row["sourceCategory"] == category]
        by_category[category] = {
            "population": len(rows_for_category),
            "supportedUpward": sum(row["shadowAction"] == "supported-upward-appearance"
                                    for row in rows_for_category),
            "strongCorrections": sum(row["shadowAction"] == "strong-wrong-identity-correction"
                                     for row in rows_for_category),
            "tentative": sum(bool(row["tentativeAssociations"]) for row in rows_for_category),
            "changedSourceDestinations": sum(
                bool(row["candidateDestination"] and row["candidateDestination"] != row["oldFolder"])
                for row in rows_for_category
            ),
        }
    other_categories = sorted({
        row["sourceCategory"] for row in rows
        if row["sourceCategory"] not in RANK
    })
    summary = {
        "populationCount": len(rows),
        "eligibleMeasuredCount": sum(row["photoId"] in evidence.eligible for row in rows),
        "byCategory": by_category,
        "outsideDirectedLadder": {
            category: sum(row["sourceCategory"] == category for row in rows)
            for category in other_categories
        },
        "supportedUpwardAssociations": sum(row["shadowAction"] == "supported-upward-appearance" for row in rows),
        "supportedSameRankAssociations": sum(row["shadowAction"] == "supported-same-rank-appearance" for row in rows),
        "strongWrongIdentityCorrections": sum(row["shadowAction"] == "strong-wrong-identity-correction" for row in rows),
        "tentativeRows": sum(bool(row["tentativeAssociations"]) for row in rows),
        "residualRows": sum(row["membershipState"] in ("residual", "uncertain-retained-in-place") for row in rows),
        "referenceUseEligible": sum(row["referenceUseEligible"] for row in rows),
        "referenceUseWithdrawnWithoutPlacementChange": sum(
            row["referenceUseDisposition"] == "withdrawn-or-unqualified-independent-of-placement"
            and row["shadowAction"] in ("retain-in-place", "physical-lock-preserved", "explicit-intent-preserved")
            for row in rows
        ),
        "changedSourceDestinations": len(changed),
        "castPopulation": len(cast_rows),
        "castStrongInitialCoreCount": len(strong_cast),
        "castStrongInitialCoreRetained": sum(
            row["shadowAction"] != "strong-wrong-identity-correction" for row in strong_cast
        ),
        "castStrongCoreProposedOut": sum(
            row["shadowAction"] == "strong-wrong-identity-correction" for row in strong_cast
        ),
        "castContinuity": [
            {
                "folder": folder,
                "sourceCount": sum(row["oldFolder"] == folder for row in cast_rows),
                "heldInSource": sum(row["oldFolder"] == folder and not row["candidateDestination"] for row in cast_rows),
                "proposedOut": sum(row["oldFolder"] == folder and bool(row["candidateDestination"]) for row in cast_rows),
                "proposedArrivals": sum(row["candidateDestination"] == folder and row["oldFolder"] != folder for row in rows),
                "strongCoreCount": sum(row["oldFolder"] == folder for row in strong_cast),
                "strongCoreProposedOut": sum(row["oldFolder"] == folder and bool(row["candidateDestination"]) for row in strong_cast),
            }
            for folder in sorted({row["oldFolder"] for row in cast_rows})
        ],
        "hardLockBlocks": sum(row["shadowAction"] == "physical-lock-preserved" for row in rows),
        "tentativeClusters": sum(group["state"] == "tentative" for group in clusters),
        "supportedClusters": sum(group["state"] == "supported" for group in clusters),
        "residualClusters": sum(group["state"] == "residual" for group in clusters),
        "stagedReferenceAdditions": sum(map(len, staged_by_view.values())),
        "referenceBoundaries": len(recovery_history) + 1,
        "referenceConvergence": "bounded frozen growth; every addition has original-base witnesses",
        "reconciledAppearanceSubsets": len(reconciliation),
        "installedMoves": 0,
    }
    return {
        "recipe": recipe, "summary": summary, "rows": rows, "clusters": clusters,
        "boundarySnapshots": boundary_snapshots,
        "qualifiedReferences": [
            {
                **copy.deepcopy(view),
                "original": list(stage_inventory[view["appearanceId"]]),
                "qualifiedReferencePhotoIds": list(stage_inventory[view["appearanceId"]]),
            }
            for view in sorted(evidence.views, key=lambda item: item["appearanceId"])
        ],
        "viewReconciliation": reconciliation,
        "initialReferenceValidation": withdrawals,
        "growthReferenceValidation": growth_validation,
        "recoveryBoundaries": recovery_history,
        "growthComparison": {
            "basis": "same reconciled frozen population/recipe; no-growth versus staged-growth upward admission",
            "noGrowthSupportedUpwardPhotoIds": sorted(no_growth_upward),
            "stagedGrowthSupportedUpwardPhotoIds": sorted(
                row["photoId"] for row in rows if row["shadowAction"] == "supported-upward-appearance"
            ),
            "gainedUpwardPhotoIds": sorted(
                row["photoId"] for row in rows
                if row["shadowAction"] == "supported-upward-appearance" and row["photoId"] not in no_growth_upward
            ),
            "lostUpwardPhotoIds": sorted(
                no_growth_upward - {row["photoId"] for row in rows if row["shadowAction"] == "supported-upward-appearance"}
            ),
        },
        "referenceRecovery": [
            {
                "appearanceId": view_id,
                "originalReferencePhotoIds": sorted(base_inventory[view_id]),
                "stagedReferencePhotoIds": sorted(staged_by_view.get(view_id, [])),
                "provenance": [
                    {"photoId": pid, **staged_evidence[(pid, view_id)]}
                    for pid in sorted(staged_by_view.get(view_id, []))
                ],
            }
            for view_id in sorted(base_inventory)
        ],
        "limits": [
            "The .60 core diagnostic and .30/.60/.30 strong-release values are illustrative comparison recipes, not selected or installed policy.",
            "Placement is proposed only in this report; no source destinations, reference settings or runtime group lifecycle are changed.",
            "Reconciliation uses mutually supported subsets and complete frozen outside-rival margins; residual exceptions remain separate competitors. Distinct cast slots never merge.",
            "Repeated frozen reference recovery requires original-base admission/core witnesses, converges within an explicit cap, and never chains identity unions.",
            "Human Keep is not represented by this saved evidence; explicit placement blocks and intent are preserved, and Keep behavior is deferred.",
            "Fictional family assessment is eligible only when explicit distinctness and independently supported resemblance evidence coexist; no family or story role is inferred.",
        ],
    }


def pack_lifecycle_stages(lifecycle):
    """Keep immutable full boundary evidence once, with a small readable index."""
    for index, stage in enumerate(lifecycle.get("stages", [])):
        if "boundaryEvidence" in stage:
            continue
        packed = pack_runtime_decisions([
            {"photoId": "boundary", "directedReformation": stage},
        ])
        compact = {
            key: copy.deepcopy(stage[key])
            for key in ("id", "title", "at", "scope", "populationCount", "summary", "evidenceKind")
            if key in stage
        }
        compact["rows"] = [
            {key: row[key] for key in ("photoId", "status", "coreUse") if key in row}
            for row in stage.get("rows", [])
        ]
        compact["boundaryEvidence"] = packed
        lifecycle["stages"][index] = compact


def lifecycle_stage(stage):
    """Materialize saved or legacy boundary rows without changing the receipt."""
    if "boundaryEvidence" not in stage:
        return stage
    full = unpack_runtime_decisions(stage["boundaryEvidence"])["boundary"]
    expected = [
        {key: row[key] for key in ("photoId", "status", "coreUse") if key in row}
        for row in full.get("rows", [])
    ]
    if expected != stage.get("rows"):
        raise ValueError("boundary evidence differs from readable row index")
    for key in ("id", "title", "at", "scope", "populationCount", "summary", "evidenceKind"):
        if stage.get(key) != full.get(key):
            raise ValueError("boundary evidence differs from readable metadata")
    return full


def pack_runtime_decisions(rows):
    """Keep complete diagnostic evidence once inside the bounded run receipt."""
    import base64
    import gzip

    evidence = {row["photoId"]: row["directedReformation"]
                for row in rows if row.get("directedReformation")}
    sections = collections.Counter()
    for decision in evidence.values():
        for key, value in decision.items():
            sections[key] += len(json.dumps({key: value}, sort_keys=True, separators=(",", ":")).encode())
    expanded_bytes = len(json.dumps(evidence, separators=(",", ":"), sort_keys=True).encode())
    nodes, indices = [], {}
    strings, string_indices, schemas, schema_indices = [], {}, [], {}

    def string_index(value):
        if value not in string_indices:
            string_indices[value] = len(strings)
            strings.append(value)
        return string_indices[value]

    def intern(value):
        if isinstance(value, dict):
            keys = tuple(sorted(value))
            if keys not in schema_indices:
                schema_indices[keys] = len(schemas)
                schemas.append([string_index(key) for key in keys])
            node = ["record", [schema_indices[keys], [intern(value[key]) for key in keys]]]
        elif isinstance(value, list):
            node = (["strings", [string_index(item) for item in value]]
                    if value and all(isinstance(item, str) for item in value)
                    else ["list", [intern(item) for item in value]])
        elif isinstance(value, str):
            return {"s": string_index(value)}
        else:
            return value
        key = json.dumps(node, separators=(",", ":"), sort_keys=True)
        if key not in indices:
            indices[key] = len(nodes)
            nodes.append(node)
        return {"$": indices[key]}

    root = intern(evidence)
    components = {"nodes": nodes, "root": root, "strings": strings, "schemas": schemas}
    stored_sections = {
        key: len(json.dumps(value, separators=(",", ":"), sort_keys=True).encode())
        for key, value in components.items()
    }
    payload = json.dumps(components, separators=(",", ":"), sort_keys=True).encode()
    if len(payload) > 64 * 1024 * 1024:
        raise ValueError(
            "directed decision evidence exceeds 64 MiB uncompressed after lossless interning: "
            + json.dumps({"storedBytes": len(payload), "expandedBytes": expanded_bytes,
                          "expandedSectionBytes": dict(sorted(sections.items())),
                          "storedSectionBytes": stored_sections}, sort_keys=True)
        )
    packed = {
        "encoding": "gzip-base64-interned-json-v2", "uncompressedBytes": len(payload),
        "expandedBytes": expanded_bytes,
        "expandedSectionBytes": dict(sorted(sections.items())),
        "internedNodeCount": len(nodes),
        "storedSectionBytes": stored_sections,
        "sharedStringCount": len(strings), "sharedRecordSchemaCount": len(schemas),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "data": base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii"),
    }
    for row in rows:
        decision = row.get("directedReformation")
        if decision:
            row["directedReformation"] = {
                key: value for key, value in decision.items()
                if value is None or isinstance(value, (str, bool, int, float))
            }
            row["directedReformation"]["decisionEvidencePhotoId"] = row["photoId"]
    return packed


def unpack_runtime_decisions(packed):
    import base64
    import gzip
    import io

    if packed.get("encoding") not in (
            "gzip-base64-json", "gzip-base64-interned-json-v1", "gzip-base64-interned-json-v2"):
        raise ValueError("unsupported directed evidence encoding")
    size = packed.get("uncompressedBytes")
    if type(size) is not int or not 0 <= size <= 64 * 1024 * 1024:
        raise ValueError("invalid directed evidence size")
    with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(packed["data"], validate=True))) as stream:
        payload = stream.read(size + 1)
    if len(payload) != size or hashlib.sha256(payload).hexdigest() != packed["sha256"]:
        raise ValueError("directed evidence content binding differs")
    decoded = json.loads(payload)
    if packed["encoding"] == "gzip-base64-json":
        return decoded
    nodes = decoded["nodes"]
    strings = decoded.get("strings", [])
    schemas = decoded.get("schemas", [])
    if any(not isinstance(value, str) for value in strings):
        raise ValueError("invalid interned evidence string table")
    for schema in schemas:
        if (not isinstance(schema, list) or any(type(i) is not int or not 0 <= i < len(strings)
                                               for i in schema)
                or len({strings[i] for i in schema}) != len(schema)):
            raise ValueError("invalid interned evidence record schema")

    def record_entries(entries):
        schema, values = entries
        if (type(schema) is not int or not 0 <= schema < len(schemas)
                or len(values) != len(schemas[schema])):
            raise ValueError("invalid interned evidence record")
        return [(strings[key], value) for key, value in zip(schemas[schema], values)]

    def shared_string(value):
        index = value.get("s")
        if set(value) != {"s"} or type(index) is not int or not 0 <= index < len(strings):
            raise ValueError("invalid interned evidence string reference")
        return strings[index]

    lengths = []

    def expanded_length(value, before):
        if not isinstance(value, dict):
            if isinstance(value, list):
                raise ValueError("invalid interned evidence scalar")
            return len(json.dumps(value, separators=(",", ":"), sort_keys=True))
        if "s" in value:
            return len(json.dumps(shared_string(value)))
        index = value.get("$")
        if set(value) != {"$"} or type(index) is not int or not 0 <= index < before:
            raise ValueError("invalid or cyclic interned evidence reference")
        return lengths[index]

    for index, (kind, entries) in enumerate(nodes):
        if kind == "record":
            kind, entries = "dict", record_entries(entries)
        if kind == "dict":
            keys = [key for key, _ in entries]
            if len(set(keys)) != len(keys) or any(not isinstance(key, str) for key in keys):
                raise ValueError("invalid interned evidence keys")
            length = 2 + max(0, len(entries) - 1) + sum(
                len(json.dumps(key)) + 1 + expanded_length(item, index) for key, item in entries
            )
        elif kind == "list":
            length = 2 + max(0, len(entries) - 1) + sum(expanded_length(item, index) for item in entries)
        elif kind == "strings":
            length = 2 + max(0, len(entries) - 1) + sum(
                len(json.dumps(shared_string({"s": item}))) for item in entries
            )
        else:
            raise ValueError("invalid interned evidence node")
        lengths.append(length)
    if expanded_length(decoded["root"], len(nodes)) != packed["expandedBytes"]:
        raise ValueError("interned evidence expanded byte count differs")

    def materialize(value, before, depth=0):
        if not isinstance(value, dict):
            if isinstance(value, list):
                raise ValueError("invalid interned evidence scalar")
            return value
        if "s" in value:
            return shared_string(value)
        index = value.get("$")
        if set(value) != {"$"} or type(index) is not int or not 0 <= index < before or depth > 64:
            raise ValueError("invalid or cyclic interned evidence reference")
        kind, entries = nodes[index]
        if kind == "record":
            kind, entries = "dict", record_entries(entries)
        if kind == "dict":
            keys = [key for key, _ in entries]
            if len(set(keys)) != len(keys):
                raise ValueError("duplicate interned evidence key")
            return {key: materialize(item, index, depth + 1) for key, item in entries}
        if kind == "list":
            return [materialize(item, index, depth + 1) for item in entries]
        if kind == "strings":
            return [shared_string({"s": item}) for item in entries]
        raise ValueError("invalid interned evidence node")

    result = materialize(decoded["root"], len(nodes))
    if len(result) > 5000:
        raise ValueError("interned evidence expanded population differs")
    return result


def regroup_runtime(rows, valid_vectors, catalog, policy, selected, run_id, *, recipe,
                   at=None, pairs=(), reference_exclusions=(), name_factory=None):
    """Run the directed evidence engine on maintained rebase inputs and preserve its ledger."""
    from . import clean_rebase, group_lifecycle, rejections

    validate_recipe(recipe)
    policy = runtime_policy(policy, recipe)
    at = at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows = copy.deepcopy(rows)
    by_id = {}
    for row in rows:
        pid = row.get("photoId")
        if pid:
            if pid in by_id:
                raise ValueError("directed regrouping requires unambiguous stable photo IDs")
            by_id[pid] = row
    # Source ownership is lineage, not reference or membership certification.
    for folder in sorted({row.get("oldFolder") for row in rows if row.get("oldFolder")}):
        matches = [
            person for person in catalog["people"].values() if not person.get("mergedInto")
            and folder.casefold() in {
                alias.casefold() for alias in [person["folder"], *person.get("folderHistory", [])]
            }
        ]
        if len(matches) > 1:
            raise ValueError(f"ambiguous directed source identity alias: {folder}")
        if _category(folder) not in RANK or matches:
            continue
        person_id = group_lifecycle._key("person_", ["source-owner", folder.casefold()])
        catalog["people"][person_id] = {
            "id": person_id, "folder": folder, "displayName": folder.rsplit("/", 1)[-1],
            "folderHistory": [], "identityAnchors": [],
            "protected": _category(folder) in ("Sisters", "Angels"),
        }
    hashes = {
        pid: row.get("preparedSHA256") or row["sha256"]
        for pid, row in by_id.items()
    }
    active_people = {
        person_id: person for person_id, person in catalog["people"].items()
        if not person.get("mergedInto")
    }
    people_by_folder = {person["folder"]: (person_id, person)
                        for person_id, person in active_people.items()}
    for folder in sorted({row.get("oldFolder") for row in rows if row.get("oldFolder")}):
        matches = [
            (person_id, person) for person_id, person in active_people.items()
            if folder.casefold() in {
                alias.casefold() for alias in [person["folder"], *person.get("folderHistory", [])]
            }
        ]
        if len(matches) > 1:
            raise ValueError(f"ambiguous directed source identity alias: {folder}")
        if matches:
            people_by_folder[folder] = matches[0]
    configured_negatives, negative_bindings = _configured_negative_bindings(
        active_people, policy["runtimeSettings"]["different"],
    )
    folder_by_person = {person_id: person["folder"] for person_id, person in active_people.items()}
    assignment_only = {
        pid for pid, row in by_id.items()
        if catalog["photos"].get(pid, {}).get("membership", {}).get("status") == "tentative"
        or catalog["photos"].get(pid, {}).get("membership", {}).get("assignmentDisposition")
        in ("tentative-parent", "provisional")
        or any(person.get("identityStatus") == "provisional" and (
            row.get("oldFolder", "").casefold() in {
                alias.casefold() for alias in [person["folder"], *person.get("folderHistory", [])]
            }) for person in active_people.values())
    }
    reference_exclusions = set(reference_exclusions) | assignment_only
    references = collections.defaultdict(set)
    unavailable_references = collections.defaultdict(set)
    anchors = set()

    for person_id, person in active_people.items():
        for pid in person.get("identityAnchors", []):
            anchors.add(pid)
            if pid in by_id:
                references[person_id].add(pid)
            else:
                unavailable_references[person_id].add(pid)

    for pid, row in by_id.items():
        owner = people_by_folder.get(row.get("oldFolder"))
        if not owner:
            continue
        person_id, _person = owner
        if row.get("castSeedCore") and not row.get("castSeedReferenceHold"):
            references[person_id].add(pid)
        if row.get("castSeedAnchor"):
            anchors.add(pid)
            references[person_id].add(pid)
        record = catalog["photos"].get(pid, {})
        if (pid in valid_vectors
                and pathlib.PurePosixPath(row["source"]).parent.name == "gallery"
                and not row.get("castSeedQualityReason")
                and not row.get("qualityHold")
                and (not record.get("contentSha256") or record["contentSha256"] in (row["sha256"], hashes[pid]))):
            references[person_id].add(pid)
        membership = record.get("membership", {})
        if (membership.get("status") == "supported" and membership.get("coreUse")
                and membership.get("personId") == person_id
                and record.get("contentSha256") == hashes[pid]):
            references[person_id].add(pid)

    photo_folders = {
        pid: {"folder": row.get("oldFolder") or "", "sha256": hashes[pid]}
        for pid, row in by_id.items()
    }
    automatic_core_enabled = bool(policy.get("rebaseProtection", {}).get("enabled"))
    for person_id, person in active_people.items():
        automatic, _mandatory = clean_rebase._identity_core_continuity_ids(
            person_id, person, catalog, photo_folders, enabled=automatic_core_enabled,
        )
        references[person_id].update(pid for pid in automatic if pid in by_id)

    views = []
    primary_view_by_person = {}

    def add_view(person_id, refs, *, appearance_id=None, display_name=None, unavailable=()):
        person = active_people[person_id]
        folder = person["folder"]
        category = _category(folder)
        if category not in RANK:
            return None
        refs = sorted(set(refs))
        unavailable = set(unavailable) | (set(refs) - set(valid_vectors))
        if appearance_id is None:
            appearance_id = _digest_id("runtime-identity", [person_id, *refs])
        view = {
            "appearanceId": appearance_id, "personId": person_id, "folder": folder,
            "category": category, "original": refs, "frozenReferencePhotoIds": refs,
            "unavailableReferencePhotoIds": sorted(unavailable),
            "displayName": display_name,
        }
        views.append(view)
        return view

    for person_id in sorted(active_people):
        refs = references[person_id]
        view = add_view(
            person_id, refs,
            unavailable=unavailable_references[person_id],
        )
        if view:
            primary_view_by_person[person_id] = view

    for group_id, group in sorted(catalog.get("photoGroups", {}).items()):
        if group.get("status") != "supported":
            continue
        person_id = group.get("personId")
        if person_id not in active_people:
            continue
        original_refs = set(group.get("referencePhotoIds", []))
        current_refs = original_refs & set(by_id)
        unavailable = original_refs - set(by_id)
        add_view(person_id, current_refs, appearance_id=group_id,
                 display_name=group.get("name"), unavailable=unavailable)

    source_rows, run_photos = [], []
    for pid, row in sorted(by_id.items()):
        person = people_by_folder.get(row.get("oldFolder"))
        person_id = person[0] if person else None
        own_view = primary_view_by_person.get(person_id)
        own_refs = list(own_view["frozenReferencePhotoIds"]) if own_view else []
        record = catalog["photos"].get(pid, {})
        placement_blocks = []
        if pid in selected:
            placement_blocks.append("workflow-selected")
        if pid in anchors:
            placement_blocks.append("identity-anchor")
        if row.get("castSeedReferenceHold"):
            placement_blocks.append("source-reference-hold")
        provenance = record.get("protectionProvenance")
        if record.get("protected") and not provenance:
            placement_blocks.append("legacy-photo-protection")
        if (record.get("contentSha256")
                and record["contentSha256"] not in (row.get("sha256"), hashes[pid])):
            placement_blocks.append("source-content-binding-mismatch")
        if (person and person[1].get("protected")
                and not str(row.get("oldFolder", "")).startswith(("Sisters/", "Angels/"))):
            placement_blocks.append("protected-source-identity")
        explicit_intent = row.get("oldFolder") if "Explicit named-person" in row.get("reason", "") else None
        source_rows.append({
            "photoId": pid, "oldFolder": row.get("oldFolder"), "oldPersonId": person_id,
            "sourceIdentityIds": sorted({
                value for value in (person_id, record.get("membership", {}).get("personId"),
                                    *record.get("membership", {}).get("sourcePersonIds", []))
                if value in active_people
            }),
            "sourcePath": row["source"],
            "membershipAssessment": {"own": {
                "appearanceId": own_view["appearanceId"] if own_view else None,
                "frozenReferencePhotoIds": own_refs,
                "frozenScore": row.get("castSeedScore"),
            }},
            "placementBlocks": placement_blocks, "explicitIntentFolder": explicit_intent,
            "reasons": (
                (["metadataStale"] if "source-content-binding-mismatch" in placement_blocks else [])
                + (["quality-ineligible"] if pid not in valid_vectors else [])
                + (["rejectionHistory"] if rejections.candidate_state(
                    catalog, pid, hashes[pid],
                ).get("rejectedPersonIds") else [])
            ),
            "runtimeCastAdmission": {
                "qualityEligible": pid in valid_vectors and not row.get("castSeedQualityReason"),
                "metadataStale": bool(record.get("contentSha256")
                                      and record["contentSha256"] not in (row.get("sha256"), hashes[pid])),
                "rejectionHistory": bool(
                    rejections.candidate_state(catalog, pid, hashes[pid]).get("rejectedPersonIds")
                    or rejections.candidate_state(catalog, pid, hashes[pid]).get("rejectionMetadataStale")
                ),
                "protected": bool(placement_blocks or record.get("protected")),
            },
        })
        run_photos.append({
            "photoId": pid, "destination": row["destination"],
            "preparedSHA256": hashes[pid],
            "castSeedCore": bool(row.get("castSeedCore")),
            "castSeedScore": row.get("castSeedScore"),
        })

    ledger = {
        "pairs": copy.deepcopy(list(pairs)),
        "referenceProposals": [
            {"photoId": pid, "referenceUse": "withdraw-in-shadow", "wasReference": True}
            for pid in sorted(set(reference_exclusions))
        ],
    }
    state = {"rows": source_rows, "appearances": views}
    run = {"photos": run_photos, "policy": policy}
    evidence = entrance_trial.Evidence(state, run, valid_vectors, ledger)
    evidence.configured_identity_negatives = configured_negatives
    result = run_variant(evidence, recipe, reconcile=True)
    decision_by_id = {row["photoId"]: row for row in result["rows"]}
    view_by_id = {view["appearanceId"]: view for view in result["qualifiedReferences"]}
    references_by_view = {
        view_id: set(view["qualifiedReferencePhotoIds"])
        for view_id, view in view_by_id.items()
    }

    grouped = collections.defaultdict(list)
    group_meta = {}
    state_by_photo = {}
    action_categories = {}
    for decision in result["rows"]:
        pid = decision["photoId"]
        source = by_id[pid]
        evidence_hold = pid not in evidence.eligible
        quality_hold = pid not in valid_vectors
        association = decision["supportedAssociation"] or decision["correctionAssociation"]
        tentative = decision["tentativeAssociations"]
        if evidence_hold:
            group_status, parent_id, view_id = "unresolved", None, None
            group_reason = (
                "no qualified single-face measurement; source placement retained" if quality_hold else
                "content-binding or rejection-history evidence hold; source placement retained"
            )
            association_kind = "hold"
        elif association:
            group_status = "supported"
            parent_id = association["personId"]
            view_id = association["appearanceId"]
            group_reason = (
                association.get("canonicalOwnerReason") or association.get("relationshipStatus")
                or "independently qualified directed association"
            )
            association_kind = "correction" if decision["correctionAssociation"] else (
                "same-rank" if decision["shadowAction"] == "supported-same-rank-appearance" else "upward"
            )
        elif decision["membershipState"] == "supported-in-place":
            group_status = "supported"
            parent_id = decision["sourcePersonId"]
            own_views = [view for view in view_by_id.values()
                         if view["personId"] == parent_id and view["folder"] == decision["oldFolder"]]
            own_view = next((view for view in own_views if pid in view["original"]),
                            next((view for view in own_views if view["original"]), None))
            view_id = own_view["appearanceId"] if own_view else f'existing:{parent_id}'
            group_reason = "supported in source identity; physical home unchanged"
            association_kind = "same-home"
        elif tentative:
            option = tentative[0]
            group_status, parent_id, view_id = "tentative", option["personId"], option["appearanceId"]
            group_reason = "tentative parent association; physical source home retained"
            association_kind = "hold"
        else:
            group_status = "tentative"
            parent_id = decision["sourcePersonId"]
            view_id = f'residual:{parent_id}:{decision["oldFolder"]}'
            group_reason = "source lineage retained; no qualified destination or membership evidence"
            association_kind = "hold"

        if parent_id not in active_people:
            group_status, parent_id, view_id = "unresolved", None, None
        if pid in assignment_only and parent_id is not None:
            group_status = "tentative"
        if group_status in ("supported", "tentative") and parent_id is not None:
            key = (group_status, parent_id, view_id, decision["oldFolder"])
            grouped[key].append(pid)
            group_meta[key] = (group_reason, association_kind)

        shadow_action = decision["shadowAction"]
        if association_kind == "same-home" or shadow_action == "retain-in-place" \
                and decision["membershipState"] == "supported-in-place":
            action_category = "same-home"
        elif association_kind in ("upward", "same-rank", "correction"):
            action_category = association_kind
        else:
            action_category = "hold"
        action_categories[pid] = action_category
        if action_category == "same-home":
            status, member_parent = "supported", decision["sourcePersonId"]
            reference = decision["referenceUseEligible"] and pid in references_by_view.get(view_id, set())
        elif association:
            status, member_parent = "supported", parent_id
            reference = pid in references_by_view.get(view_id, set())
        elif group_status == "tentative" and parent_id is not None:
            status, member_parent, reference = "tentative", parent_id, False
        else:
            status, member_parent, reference = (
                "quality-hold" if decision["membershipState"] == "quality-hold" else "unresolved",
                None, False,
            )
        if pid in assignment_only and member_parent is not None:
            status, reference = "tentative", False
            decision.update(referenceUseEligible=False, referenceUseDisposition="persisted-assignment-only-no-reference")
        state_by_photo[pid] = {
            "personId": member_parent, "groupId": None,
            "status": "quality-hold" if quality_hold else status, "coreUse": bool(reference),
            "reason": decision["shadowAction"] + ": " + (
                (association.get("canonicalOwnerReason") or association.get("relationshipStatus")
                 or group_reason) if association else group_reason
            ),
            "assignmentDisposition": (
                "provisional" if member_parent and active_people.get(member_parent, {}).get("identityStatus") == "provisional"
                else "supported" if status == "supported" else
                "tentative-parent" if status == "tentative" and member_parent else "exception"
            ),
            "sourcePersonIds": sorted(_identity_ids(evidence, [pid])),
            "assignmentEvidence": {
                "source": by_id[pid]["source"], "sourceSha256": hashes[pid],
                "blockers": list(decision["placementBlocks"]),
            },
        }

    independent_identities = []
    residual_classifications = []
    parentless = [
        pid for pid, decision in decision_by_id.items()
        if decision["sourcePersonId"] is None and pid in evidence.eligible
        and not decision["supportedAssociation"] and not decision["correctionAssociation"]
        and not decision["tentativeAssociations"] and not decision["placementBlocks"]
        and not decision.get("explicitIntentFolder")
    ]
    claimed = set()
    from .policy import classify_category

    for cohort in _complete_link_clusters(parentless, evidence, .45, MAX_CLUSTER_OPERATIONS):
        source_owners = _identity_ids(evidence, cohort)
        if _identity_conflict(evidence, source_owners, source_owners):
            residual_classifications.append({
                "memberPhotoIds": list(cohort), "sourcePersonIds": sorted(source_owners),
                "disposition": "configured-different-identity-veto",
            })
            for pid in cohort:
                decision_by_id[pid]["independentCandidateDisposition"] = "configured-different-identity-veto"
            continue
        if len(evidence.independent(cohort)) < 2:
            for pid in cohort:
                decision_by_id[pid]["independentCandidateDisposition"] = "no-qualifying-independent-cluster"
            continue
        independent_cohort = evidence.independent(cohort)
        cohort_center = np.sum([evidence.vectors[pid] for pid in independent_cohort], axis=0)
        cohort_norm = np.linalg.norm(cohort_center)
        cast_scores = {}
        for view_id, view in view_by_id.items():
            if view["category"] not in ("Sisters", "Angels"):
                continue
            refs = evidence.independent(sorted(references_by_view[view_id]))
            if not refs or not cohort_norm:
                continue
            center = np.sum([evidence.vectors[pid] for pid in refs], axis=0)
            norm = np.linalg.norm(center)
            if norm:
                similarity = float(np.clip(cohort_center @ center / cohort_norm / norm, -1., 1.))
                cast_scores[view["folder"]] = max(similarity, cast_scores.get(view["folder"], -1.))
        ranked_cast = sorted(cast_scores.items(), key=lambda item: (-item[1], item[0]))
        classification = classify_category(
            len(independent_cohort),
            cast_similarity=ranked_cast[0][1] if ranked_cast else None, policy=policy,
            best_cast_folder=ranked_cast[0][0] if ranked_cast else None,
            second_cast_folder=ranked_cast[1][0] if len(ranked_cast) > 1 else None,
            cast_margin=max(0., ranked_cast[0][1] - ranked_cast[1][1]) if len(ranked_cast) > 1 else
            2. if ranked_cast else None,
        )
        diagnostic = {
            "memberPhotoIds": list(cohort), "independentPhotoCount": len(independent_cohort),
            "rankedQualifiedCastScores": [{"folder": folder, "score": score}
                                        for folder, score in ranked_cast],
            "classification": copy.deepcopy(classification),
            "scoreBasis": "independent cohort centroid versus authoritative qualified cast-view centroids",
            "castReferenceUnavailable": not ranked_cast,
        }
        residual_classifications.append(diagnostic)
        if classification["category"] not in RANK:
            diagnostic["disposition"] = "classification-review-hold"
            for pid in cohort:
                decision_by_id[pid]["independentCandidateDisposition"] = "classification-review-hold"
            continue
        category = classification["category"]
        parent_id, folder = group_lifecycle.residual_identity(
            cohort, by_id, people_by_folder, claimed, name_factory, category=category,
        )
        view_id = _digest_id("independent-view", [parent_id, *cohort])
        candidate_view = {
            "appearanceId": view_id, "personId": parent_id, "folder": folder, "category": category,
        }
        qualified, stable = evidence.qualify(candidate_view, cohort, recipe)
        refs = set(qualified) if stable else set()
        diagnostic.update(
            candidateId=parent_id, candidateFolder=folder,
            qualifiedReferencePhotoIds=sorted(refs), referenceStable=stable and bool(refs),
            coreMinimum=recipe["core"][category], coreSupportMinimum=recipe["coreSupport"],
            candidateQualification=[{
                "photoId": pid, "independentOwnCentroidScore": evidence.measure(pid, cohort),
                "independentPairSupport": len(evidence.support(pid, cohort, recipe["core"][category])),
            } for pid in cohort],
        )
        if not refs or classification["reviewRequired"]:
            disposition = ("classification-review-hold" if classification["reviewRequired"]
                           else "independent-reference-insufficient")
            diagnostic["disposition"] = disposition
            for pid in cohort:
                decision_by_id[pid].update(
                    independentCandidateId=parent_id, independentCandidateFolder=folder,
                    independentCandidateDisposition=disposition,
                )
            continue
        diagnostic["disposition"] = "qualified-independent-identity"
        person = {
            "id": parent_id, "folder": folder, "displayName": folder.rsplit("/", 1)[-1],
            "folderHistory": [], "identityAnchors": [], "protected": False,
        }
        catalog["people"][parent_id] = active_people[parent_id] = person
        folder_by_person[parent_id] = folder
        references_by_view[view_id] = refs
        candidate_view.update(
            original=sorted(refs), qualifiedReferencePhotoIds=sorted(refs),
            candidateReferencePhotoIds=list(cohort), frozenReferencePhotoIds=sorted(refs),
            unavailableReferencePhotoIds=[], referenceStable=stable and bool(refs),
        )
        view_by_id[view_id] = candidate_view
        independent_identities.append({
            "personId": parent_id, "folder": folder, "memberPhotoIds": list(cohort),
            "qualifiedReferencePhotoIds": sorted(refs), "classification": classification,
        })
        for pid in cohort:
            supported = (pid in refs and len(evidence.support(pid, refs, recipe["admission"][category]))
                         >= recipe["joinSupport"])
            status = "supported" if supported else "tentative"
            key = (status, parent_id, view_id, by_id[pid].get("oldFolder"))
            grouped[key].append(pid)
            group_meta[key] = ("coherent independent identity; no existing parent qualified", "independent")
            state_by_photo[pid].update(
                personId=parent_id, status=status, coreUse=supported and pid in refs,
                assignmentDisposition="supported" if supported else "tentative-parent",
                reason="independent residual identity; independently supported" if supported
                else "independent residual identity; tentative membership, no reference authority",
            )
            decision_by_id[pid].update(
                shadowAction="independent-identity-created" if supported else "retain-in-place",
                candidateDestination=folder if supported else None,
                membershipState="supported-independent" if supported else "tentative-independent",
                referenceUseEligible=supported and pid in refs,
                referenceUseDisposition="eligible" if supported else "tentative-independent-no-reference",
            )
            action_categories[pid] = "independent" if supported else "hold"

    provisional_containers = []
    intake_ids = [
        pid for pid, row in by_id.items() if _category(row.get("oldFolder", "")) == "Various"
        and state_by_photo[pid]["status"] != "supported"
    ]
    for pid in intake_ids:
        decision = decision_by_id[pid]
        if pid not in evidence.eligible or decision["placementBlocks"] \
                or decision.get("explicitIntentFolder") or evidence.source[pid].get("reasons"):
            blockers = list(dict.fromkeys([
                *decision["placementBlocks"], *evidence.source[pid].get("reasons", []),
                *(["explicit-placement-intent"] if decision.get("explicitIntentFolder") else []),
                *(["recoverable-junk-publication-unavailable"]
                  if (by_id[pid].get("qualityEvidence") or {}).get("recoverableJunkCandidate") else []),
            ]))
            state_by_photo[pid]["assignmentEvidence"]["blockers"] = blockers
            state_by_photo[pid]["assignmentEvidence"]["qualityReason"] = (
                (by_id[pid].get("qualityEvidence") or {}).get("reason")
                or (by_id[pid].get("reason") if by_id[pid].get("qualityHold") else None)
            )
            state_by_photo[pid]["reason"] += (
                "; intake exception: " + ", ".join(blockers or ["ineligible measurement"]) + "; "
                "not inferred unusable from low identity score"
            )
            continue
        options = [
            option for option in decision["tentativeAssociations"]
            if option["score"] >= option["admissionFloor"]
            and len(option["independentSupportPhotoIds"]) >= recipe["referenceSupport"]
            and option["signedDistinctRivalMargin"] >= recipe["sameIdentityMargin"][option["category"]]
            and not set(option["blockers"]) - {"insufficient-independent-member-support"}
            and active_people[option["personId"]].get("identityStatus") != "provisional"
        ]
        if not options:
            continue
        option = options[0]
        for key in list(grouped):
            if pid in grouped[key]:
                grouped[key].remove(pid)
        key = ("tentative", option["personId"], option["appearanceId"], by_id[pid].get("oldFolder"))
        grouped[key].append(pid)
        group_meta[key] = ("credible unambiguous assignment; no reference authority", "tentative-parent")
        state_by_photo[pid].update(
            personId=option["personId"], status="tentative", coreUse=False,
            assignmentDisposition="tentative-parent",
            reason="credible unambiguous tentative parent assignment; no reference authority",
            assignmentEvidence={
                "source": by_id[pid]["source"], "sourceSha256": hashes[pid],
                "score": option["score"], "margin": option["signedDistinctRivalMargin"],
                "supportPhotoIds": option["independentSupportPhotoIds"], "blockers": [],
            },
        )
        decision.update(candidateDestination=option["folder"], assignmentGallery=True,
                        shadowAction="tentative-parent-assignment", membershipState="tentative-assigned",
                        referenceUseEligible=False, referenceUseDisposition="assignment-only-no-reference")
        action_categories[pid] = "tentative-parent"

    unmatched = [
        pid for pid in intake_ids if pid in evidence.eligible
        and not decision_by_id[pid]["placementBlocks"]
        and not decision_by_id[pid].get("explicitIntentFolder")
        and not evidence.source[pid].get("reasons")
        and not decision_by_id[pid].get("assignmentGallery")
    ]
    for cohort in _complete_link_clusters(unmatched, evidence, .45, MAX_CLUSTER_OPERATIONS):
        prior = active_people.get(group_lifecycle._key("person_", cohort))
        candidate = next((item for item in residual_classifications
                          if item.get("candidateId") and item["memberPhotoIds"] == cohort), None)
        if prior and prior.get("identityStatus") == "provisional":
            parent_id, folder = prior["id"], prior["folder"]
        elif candidate:
            parent_id = candidate["candidateId"]
            folder = "Potentials/" + candidate["candidateFolder"].split("/", 1)[-1]
            claimed.add(folder)
        else:
            parent_id, folder = group_lifecycle.residual_identity(
                cohort, by_id, people_by_folder, claimed, name_factory, category="Potentials",
            )
        person = {
            "id": parent_id, "folder": folder, "displayName": folder.rsplit("/", 1)[-1],
            "folderHistory": [], "identityAnchors": [], "protected": False,
            "identityStatus": "provisional",
            **(prior if prior and prior.get("identityStatus") == "provisional" else {}),
        }
        catalog["people"][parent_id] = active_people[parent_id] = person
        folder_by_person[parent_id] = folder
        view_id = _digest_id("provisional-container", [parent_id, *cohort])
        provisional_containers.append({
            "personId": parent_id, "folder": folder, "memberPhotoIds": list(cohort),
            "identityStatus": "provisional", "qualifiedReferencePhotoIds": [],
            "reason": "usable unmatched assignment container; not a certified distinct identity",
        })
        for pid in cohort:
            for key in list(grouped):
                if pid in grouped[key]:
                    grouped[key].remove(pid)
            key = ("tentative", parent_id, view_id, by_id[pid].get("oldFolder"))
            grouped[key].append(pid)
            group_meta[key] = ("provisional cohort; identity uncertainty retained, no reference authority", "provisional")
            state_by_photo[pid].update(
                personId=parent_id, status="tentative", coreUse=False, assignmentDisposition="provisional",
                reason="usable unmatched provisional Potential; not a certified distinct person; no reference authority",
            )
            state_by_photo[pid]["assignmentEvidence"]["blockers"] = [
                candidate["disposition"] if candidate else "no-credible-unambiguous-qualified-parent",
            ]
            decision_by_id[pid].update(
                candidateDestination=folder, assignmentGallery=True, shadowAction="provisional-assignment",
                membershipState="provisional-assigned", referenceUseEligible=False,
                referenceUseDisposition="provisional-no-reference",
            )
            action_categories[pid] = "provisional"

    groups = {}
    for key, members in sorted(grouped.items()):
        status, parent_id, view_id, source_folder = key
        parent_folder = folder_by_person[parent_id]
        for cluster in _complete_link_clusters(
                members, evidence, recipe["residualSimilarity"], MAX_CLUSTER_OPERATIONS):
            if not cluster:
                continue
            cluster_key = [recipe["name"], status, parent_id, view_id, source_folder, *cluster]
            group_id = "group_" + hashlib.sha256("\0".join(map(str, cluster_key)).encode()).hexdigest()[:32]
            source_person_ids = sorted({
                people_by_folder[row.get("oldFolder")][0]
                for pid in cluster if (row := by_id[pid]).get("oldFolder") in people_by_folder
            })
            label = pathlib.PurePosixPath(source_folder or "").name or "Source"
            name = (f'{parent_folder.rsplit("/", 1)[-1]} · {label} appearance'
                    if status == "supported" else
                    f'{parent_folder.rsplit("/", 1)[-1]} · {label} tentative appearance')
            reference_view = references_by_view.get(view_id, set())
            reference_ids = sorted(
                pid for pid in cluster
                if status == "supported" and pid in reference_view
                and state_by_photo[pid]["status"] == "supported"
            )
            group = {
                "id": group_id, "personId": parent_id, "name": name, "status": status,
                "memberPhotoIds": sorted(cluster), "referencePhotoIds": reference_ids,
                "sourcePersonIds": source_person_ids,
                "history": [{"timestamp": at or "runtime", "runId": run_id,
                             "reason": group_meta[key][0]}],
                "reason": group_meta[key][0],
            }
            groups[group_id] = group
            for pid in cluster:
                state_by_photo[pid]["groupId"] = group_id
                state_by_photo[pid]["status"] = status
                state_by_photo[pid]["personId"] = parent_id
                state_by_photo[pid]["coreUse"] = pid in reference_ids

    groups = group_lifecycle.reconcile_history(
        groups, catalog.get("photoGroups", {}), state_by_photo, run_id, at or "runtime",
    )
    qualified_by_person = collections.defaultdict(set)
    for view_id, view in view_by_id.items():
        qualified_by_person[view["personId"]].update(references_by_view[view_id])
    for pid, state in state_by_photo.items():
        if state["coreUse"] and (
                state["status"] != "supported" or pid not in qualified_by_person[state["personId"]]):
            raise ValueError(f"unqualified directed reference export: {pid}")
        decision = decision_by_id[pid]
        decision["initialReferenceUseEligible"] = decision["referenceUseEligible"]
        decision["referenceUseEligible"] = state["coreUse"]
        if state["coreUse"]:
            decision["referenceUseDisposition"] = "eligible"
    for group in groups.values():
        if any(not state_by_photo[pid]["coreUse"]
               or state_by_photo[pid]["personId"] != group["personId"]
               for pid in group["referencePhotoIds"]):
            raise ValueError("directed group reference differs from authoritative membership")
    references_version = hashlib.sha256(json.dumps({
        "recipe": recipe, "hashes": hashes, "pairs": sorted(pairs, key=lambda pair: tuple(sorted(pair["photoIds"]))),
        "referenceExclusions": sorted(set(reference_exclusions)),
        "configuredIdentityNegatives": negative_bindings,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    source_by_id = {row["photoId"]: row for row in rows if row.get("photoId")}
    for pid, decision in decision_by_id.items():
        row = source_by_id[pid]
        action_category = action_categories[pid]
        candidate = decision.get("candidateDestination")
        row["destination"] = row["source"]
        if candidate and candidate != decision.get("oldFolder"):
            bucket = "gallery" if state_by_photo[pid]["status"] == "supported" \
                or decision.get("assignmentGallery") else "review"
            row["destination"] = (
                f'{candidate}/{bucket}/{pathlib.PurePosixPath(row["source"]).name}'
            )
            association = decision["supportedAssociation"] or decision["correctionAssociation"] or {}
            if association.get("castAdmission") is not None:
                row["castAdmission"] = copy.deepcopy(association["castAdmission"])
        row["directedReformation"] = {
            **copy.deepcopy(decision), "actionCategory": action_category,
            "sourceDestination": row["source"], "proposedDestination": row["destination"],
            "referenceVersion": references_version,
        }
        row["membership"] = {
            **row.get("membership", {}), **state_by_photo[pid],
            "referenceVersion": references_version,
        }
        row["reason"] = state_by_photo[pid]["reason"]
        if decision.get("independentCandidateDisposition"):
            row["reason"] += "; " + decision["independentCandidateDisposition"]
        if not (decision["supportedAssociation"] or decision["correctionAssociation"]):
            row.pop("castAdmission", None)
        record = catalog["photos"].setdefault(
            pid, {"contentSha256": hashes[pid], "protected": False},
        )
        if not record.get("contentSha256") or record["contentSha256"] in (row["sha256"], hashes[pid]):
            record["contentSha256"] = hashes[pid]
        record["membership"] = copy.deepcopy(row["membership"])
        if row["source"].startswith(("Angels/", "Sisters/")) and row.get("castSeedDecision"):
            same_gallery = pathlib.PurePosixPath(row["source"]).parent == pathlib.PurePosixPath(row["destination"]).parent
            row["retainedCast"], row["releasedCast"] = same_gallery, not same_gallery
            row["castSeedDecision"] = "retained" if same_gallery else "released"

    catalog["photoGroups"] = groups
    evaluation = {
        **result["summary"],
        "referenceUseEligible": sum(state["coreUse"] for state in state_by_photo.values()),
        "sameHomeAssignments": sum(value == "same-home" for value in action_categories.values()),
        "upwardAssignments": sum(value == "upward" for value in action_categories.values()),
        "sameRankAssignments": sum(value == "same-rank" for value in action_categories.values()),
        "correctionAssignments": sum(value == "correction" for value in action_categories.values()),
        "heldAssignments": sum(value == "hold" for value in action_categories.values()),
        "independentResidualCandidates": len(independent_identities),
        "independentAssignments": sum(value == "independent" for value in action_categories.values()),
        "verifiedStrongBaselineCount": sum(row["verifiedStrongBaseline"] for row in result["rows"]),
        "reviewedReferenceExclusions": sorted(set(reference_exclusions)),
        "proposedCrossFolderMoves": sum(
            row["source"] != row["destination"] for row in rows
        ),
        "sourceCoreSelection": {
            "selectedRecipe": recipe["name"],
            "strongBaselineMinimumOwnSeedScore": .80,
            "strongBaselineBasis": "initial qualified own-seed views; content-bound independent witnesses, not saved scores or locks",
            "candidateReferenceCount": sum(len(view["frozenReferencePhotoIds"]) for view in views),
            "qualifiedReferenceCount": sum(len(refs) for refs in references_by_view.values()),
            "referenceCountBasis": "view occurrences; a photo may qualify in multiple same-person views",
            "qualifiedReferencePhotoCount": len(set().union(*references_by_view.values())),
            "exportedCorePhotoCount": sum(state["coreUse"] for state in state_by_photo.values()),
            "referenceUnavailablePersonIds": sorted(
                person_id for person_id in active_people
                if not any(view["personId"] == person_id and references_by_view.get(view_id)
                           for view_id, view in view_by_id.items())
                and person_id not in {item["personId"] for item in independent_identities
                                     if item["qualifiedReferencePhotoIds"]}
            ),
            "measurementEligibility": "evaluated only by this matched run; pre-intake preview is not a trusted-core result",
        },
        "referenceVersion": references_version,
    }

    def stage_rows():
        stage = []
        for row in sorted(rows, key=lambda item: item.get("photoId") or ""):
            decision = row.get("directedReformation", {})
            membership = row.get("membership", {})
            stage.append({
                "photoId": row.get("photoId"), "source": row["source"],
                "sourceDestination": row["source"], "destination": row["destination"],
                "proposedDestination": row["destination"], "actionCategory": decision.get("actionCategory", "hold"),
                "personId": membership.get("personId"), "groupId": membership.get("groupId"),
                "status": membership.get("status", "unresolved"), "coreUse": membership.get("coreUse", False),
                "assignmentDisposition": membership.get("assignmentDisposition"),
                "assignmentEvidence": membership.get("assignmentEvidence"),
                "score": decision.get("currentOwnScore"), "rivalScore": None, "margin": None,
                "reason": decision.get("shadowAction", "not assessed"),
                "referenceUseDisposition": decision.get("referenceUseDisposition"),
                "sourceReferenceHold": not any(
                    view["personId"] == decision.get("sourcePersonId") and view["original"]
                    for view in view_by_id.values()
                ) if decision.get("sourcePersonId") else True,
                "referenceWithdrawalReason": next((
                    item["reason"] for item in result["initialReferenceValidation"]
                    if row.get("photoId") in item["withdrawnPhotoIds"]
                ), "explicit reviewed reference withdrawal; growth cannot restore it"
                    if row.get("photoId") in reference_exclusions else None),
                "admissionReason": (decision.get("supportedAssociation") or
                                    decision.get("correctionAssociation") or {}).get("castAdmission"),
                "decisionEvidencePhotoId": row.get("photoId"),
                "tentativeAssociationCount": len(decision.get("tentativeAssociations", [])),
                "independentCandidateFolder": decision.get("independentCandidateFolder"),
                "independentCandidateDisposition": decision.get("independentCandidateDisposition"),
            })
            options = decision.get("rivals", [])
            best = next((option for option in options if not option["sameIdentity"]), None)
            if best:
                stage[-1]["rivalScore"] = best["score"]
                stage[-1]["margin"] = best["signedDistinctRivalMargin"]
                if stage[-1]["admissionReason"] is None:
                    stage[-1]["admissionReason"] = "; ".join(best["blockers"]) or "no cast admission required"
        return stage

    stages = [
        {"id": "input", "title": "Frozen source locations", "at": at or "runtime",
         "scope": "all inputs", "populationCount": len(rows), "summary": {"inputs": len(rows)},
         "rows": [{
             "photoId": row.get("photoId"), "source": row["source"], "sourceDestination": row["source"],
             "destination": row["source"], "proposedDestination": row["source"],
             "actionCategory": "hold", "status": "inherited-not-assessed", "coreUse": False,
             "reason": "source folder is lineage, not automatic membership",
         } for row in sorted(rows, key=lambda item: item.get("photoId") or "")]},
        {"id": "references", "title": "Validated frozen references", "at": at or "runtime",
         "scope": "all inputs", "populationCount": len(rows),
         "summary": {"withdrawnViews": len(result["initialReferenceValidation"])},
         "rows": stage_rows()},
        {"id": "reconciliation", "title": "Qualified subset reconciliation", "at": at or "runtime",
         "scope": "all inputs", "populationCount": len(rows),
         "summary": {"reconciledSubsets": len(result["viewReconciliation"])},
         "rows": stage_rows()},
        {"id": "membership", "title": "Member decisions against distinct rivals", "at": at or "runtime",
         "scope": "all inputs", "populationCount": len(rows), "summary": dict(evaluation),
         "rows": stage_rows()},
        {"id": "growth", "title": "Original-witness growth and joint validation", "at": at or "runtime",
         "scope": "all inputs", "populationCount": len(rows),
         "summary": {"stagedReferences": evaluation["stagedReferenceAdditions"],
                     "validatedBoundaries": len(result["growthReferenceValidation"])},
         "rows": stage_rows()},
        {"id": "appearances", "title": "Named supported, tentative, and residual groups", "at": at or "runtime",
         "scope": "all inputs", "populationCount": len(rows),
         "summary": {"supportedGroups": sum(g["status"] == "supported" for g in groups.values()),
                     "tentativeGroups": sum(g["status"] == "tentative" for g in groups.values())},
         "rows": stage_rows()},
        {"id": "publication", "title": "Proposed destinations and preserved holds", "at": at or "runtime",
         "scope": "all inputs", "populationCount": len(rows), "summary": dict(evaluation),
         "rows": stage_rows()},
    ]
    for stage in stages:
        if stage["id"] == "input":
            stage["evidenceKind"] = "source-snapshot"
        elif stage["id"] == "publication":
            stage["evidenceKind"] = "proposal-snapshot"
        elif stage["id"] == "appearances":
            stage["evidenceKind"] = "computational-boundary-snapshot"
            stage["scope"] = "named runtime groups after independent residual formation; before canonical/family renaming"
        else:
            boundary_id = "growth-1" if stage["id"] == "growth" else stage["id"]
            boundary = next(item for item in result["boundarySnapshots"] if item["id"] == boundary_id)
            stage.update({key: copy.deepcopy(value) for key, value in boundary.items() if key != "id"})
            stage["scope"] = "actual frozen computational boundary; source routes unchanged until proposal"
    extra_boundaries = [
        {
            **copy.deepcopy(boundary), "title": boundary["id"], "at": at,
            "scope": "actual frozen computational boundary", "populationCount": len(rows),
            "summary": {"referenceOccurrences": sum(map(len, boundary["referenceInventory"].values()))},
        }
        for boundary in result["boundarySnapshots"]
        if boundary["id"] in ("final-membership", "appearance-hypotheses")
        or boundary["id"].startswith("growth-") and boundary["id"] != "growth-1"
    ]
    growth_stages = [stage for stage in extra_boundaries if stage["id"].startswith("growth-")]
    final_stages = [stage for stage in extra_boundaries if not stage["id"].startswith("growth-")]
    growth_position = next(i for i, stage in enumerate(stages) if stage["id"] == "growth") + 1
    stages[growth_position:growth_position] = growth_stages + final_stages
    report = {
        "mode": "experimental-directed-sandbox",
        "recipe": recipe["name"], "thresholds": copy.deepcopy(recipe),
        "stages": stages, "evaluation": evaluation, "groups": list(groups.values()),
        "initialReferenceValidation": result["initialReferenceValidation"],
        "viewReconciliation": result["viewReconciliation"],
        "growthReferenceValidation": result["growthReferenceValidation"],
        "referenceRecovery": result["referenceRecovery"],
        "qualifiedReferences": list(view_by_id.values()),
        "independentIdentities": independent_identities,
        "provisionalContainers": provisional_containers,
        "assignmentSummary": {
            **dict(collections.Counter(state["assignmentDisposition"] for state in state_by_photo.values())),
            "confirmedIndependentIdentities": len(independent_identities),
            "createdProvisionalContainers": len(provisional_containers),
            "provisionalContainers": sum(
                person.get("identityStatus") == "provisional"
                for person in active_people.values() if not person.get("mergedInto")
            ),
            "activeVarious": sum(_category(row["destination"]) == "Various" for row in rows),
            "junk": 0,
            "review": sum(pathlib.PurePosixPath(row["destination"]).parent.name == "review" for row in rows),
            "qualityExceptionCounts": dict(collections.Counter(
                (row.get("qualityEvidence") or {}).get("classification", "unclassified-quality-hold")
                for row in rows if _category(row["destination"]) == "Various"
                and (row.get("qualityEvidence") or row.get("qualityHold"))
            )),
            "exceptions": [{
                "photoId": row["photoId"], "source": row["source"], "destination": row["destination"],
                "reason": state_by_photo[row["photoId"]]["reason"],
                "qualityEvidence": {
                    **(row.get("qualityEvidence") or {}),
                    "qualityHold": bool(row.get("qualityHold")),
                    "castSeedQualityReason": row.get("castSeedQualityReason"),
                    "eligibleMeasurement": row["photoId"] in evidence.eligible,
                    "qualityReason": state_by_photo[row["photoId"]]["assignmentEvidence"].get("qualityReason"),
                },
            } for row in rows if _category(row["destination"]) == "Various"],
            "qualityDisposition": "explicit exceptions retained; clean-rebase does not publish recoverable Junk transactions",
        },
        "residualClassifications": residual_classifications,
        "configuredIdentityNegatives": negative_bindings,
        "admissionPolicy": {
            "version": policy["version"],
            "categories": {category: copy.deepcopy(policy["categoryPolicies"][category])
                           for category in ("Sisters", "Angels")},
        },
        "limits": result["limits"] + [
            "Maintained integration proposes destinations only; no automatic installation or live GUI transaction.",
            "Pre-intake core-selection candidates are authored/protected metadata only; no measured eligibility is asserted.",
        ],
    }
    report["decisionEvidence"] = pack_runtime_decisions(rows)
    metadata.validate_catalog(catalog)
    return rows, report


def _control_summary(evidence):
    result = entrance_trial.run_variant(evidence, entrance_trial.recipes()[1])
    rows = result["rows"]
    return {
        "name": "current ordered-middle entrance/core/retention control",
        "recipe": entrance_trial.recipes()[1],
        "populationCount": len(rows),
        "proposalCount": result["summary"]["proposals"],
        "logicalReleases": result["summary"]["logicalReleases"],
        "tentativeOrBlocked": sum(bool(row.get("entranceBlockers")) for row in rows),
        "changedSourceDestinations": sum(
            bool(row.get("proposalPersonId") and row.get("best")
                 and row["best"]["folder"] != row["oldFolder"])
            for row in rows
        ),
        "castPopulation": sum(row["oldFolder"].startswith(("Sisters/", "Angels/")) for row in rows),
        "castStrongCoreOutcomesNotClassified": "control is not a directed, source-incompatibility release model",
        "installedMoves": 0,
    }


def _run_once(state, run, vectors, ledger, *, progress=None):
    evidence = entrance_trial.Evidence(state, run, vectors, ledger)
    if progress:
        progress("Running unchanged ordered-middle control.")
    control = _control_summary(evidence)
    variants = []
    for recipe in recipes():
        if progress:
            progress(f"Starting {recipe['name']} on {len(state['rows'])} saved photos.")
        variants.append(run_variant(evidence, recipe, progress=progress, reconcile=True))
        if progress:
            summary = variants[-1]["summary"]
            progress(f"Completed {recipe['name']}: {summary['supportedUpwardAssociations']} upward, "
                     f"{summary['strongWrongIdentityCorrections']} corrections.")
    return {
        "kind": "directed-reformation-shadow",
        "populationCount": len(state["rows"]),
        "sourcePhotoCount": len(run["photos"]),
        "control": control,
        "variants": variants,
        "comparison": {
            "orderedRecipes": [control["name"], *(item["recipe"]["name"] for item in variants)],
            "axes": {
                "admission": "per-category independent member admission; lower-category recipe is paired",
                "core": "frozen source-core continuity and separate reference eligibility; directed base raises core floors",
                "retention": "own frozen-source evidence; stricter-retention recipe is paired",
                "strongRelease": "source incompatibility + independent destination + signed rival margin; stricter-release recipe is paired",
            },
            "positiveFixtures": "reviewed labels are conflict/support controls, not blind accuracy",
            "canonicalDirection": "category rank is applied only after individually supported same-identity association",
        },
    }


def _semantic(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def compact_for_report(result):
    def compact_option(option):
        compact = {
            key: value for key, value in option.items()
            if key not in (
                "referencePhotoIds", "sharedOriginalReferencePhotoIds",
                "originalBoundarySupportPhotoIds",
            )
        }
        compact["referencePhotoCount"] = len(option["referencePhotoIds"])
        compact["sharedOriginalReferenceCount"] = len(option["sharedOriginalReferencePhotoIds"])
        compact["originalBoundarySupportCount"] = len(option["originalBoundarySupportPhotoIds"])
        compact["referenceExamplePhotoIds"] = option["referencePhotoIds"][:3]
        if option["individuallyQualified"]:
            compact["originalBoundarySupportPhotoIds"] = option["originalBoundarySupportPhotoIds"]
        return compact

    compact = {
        key: value for key, value in result.items()
        if key not in ("variants",)
    }
    compact["variants"] = []
    for variant in result["variants"]:
        compact_variant = {
            key: value for key, value in variant.items()
            if key not in ("rows",)
        }
        compact_variant["rows"] = []
        for row in variant["rows"]:
            compact_row = {
                key: value for key, value in row.items()
                if key not in (
                    "rivals", "tentativeAssociations", "supportedAssociation",
                    "correctionAssociation", "familyAssessmentCandidates",
                )
            }
            compact_row.update({
                "rivals": [compact_option(option) for option in row["rivals"]],
                "tentativeAssociations": [
                    option["appearanceId"] for option in row["tentativeAssociations"]
                ],
                "supportedAssociation": (
                    row["supportedAssociation"]["appearanceId"]
                    if row["supportedAssociation"] else None
                ),
                "correctionAssociation": (
                    row["correctionAssociation"]["appearanceId"]
                    if row["correctionAssociation"] else None
                ),
                "familyAssessmentCandidates": [
                    option["appearanceId"] for option in row["familyAssessmentCandidates"]
                ],
            })
            compact_variant["rows"].append(compact_row)
        compact["variants"].append(compact_variant)
    return compact


def summary_for_page(result):
    row_fields = (
        "photoId", "oldFolder", "sourceCategory", "membershipState", "shadowAction",
        "candidateDestination", "frozenSourceScore", "currentOwnScore",
        "strongInitialCastCoreDiagnostic", "referenceUseDisposition",
        "referenceUseEligible", "sourceIncompatibility", "placementBlocks",
        "groupProtectionMetadata", "explicitIntentFolder", "supportedAssociation",
        "correctionAssociation", "tentativeAssociations", "ownExactConflicts",
        "fictionalFamilyAssessment", "familyAssessmentCandidates", "clusterIds",
        "allRelevantRivalsCount", "stagedReferenceCandidates",
        "reconciledAppearanceIds",
    )
    page_variants = []
    for variant in result["variants"]:
        clusters = variant["clusters"]
        cluster_summary = {
            "count": len(clusters),
            "byState": {
                state: sum(group["state"] == state for group in clusters)
                for state in ("supported", "tentative", "residual")
            },
        }
        recovery = variant["referenceRecovery"]
        recovery_summary = {
            "appearanceCount": len(recovery),
            "originalReferenceCount": sum(len(view["originalReferencePhotoIds"]) for view in recovery),
            "stagedReferenceCount": sum(len(view["stagedReferencePhotoIds"]) for view in recovery),
            "viewsWithStagedReferences": [
                {
                    "appearanceId": view["appearanceId"],
                    "stagedReferencePhotoIds": view["stagedReferencePhotoIds"],
                }
                for view in recovery if view["stagedReferencePhotoIds"]
            ],
        }
        page_variant = {
            key: value for key, value in variant.items()
            if key not in ("rows", "clusters", "referenceRecovery")
        }
        page_variant["clusters"] = cluster_summary
        page_variant["referenceRecovery"] = recovery_summary
        page_variant["rows"] = [
            {
                **{key: row.get(key) for key in row_fields},
                "candidateTarget": _candidate_target(row),
            }
            for row in variant["rows"]
        ]
        page_variants.append(page_variant)
    return {
        key: value for key, value in result.items()
        if key != "variants"
    } | {
        "variants": page_variants,
    }


def _candidate_target(row):
    proposed = row["supportedAssociation"] or row["correctionAssociation"]
    if isinstance(proposed, str):
        proposed = next(
            (rival for rival in row["rivals"] if rival["appearanceId"] == proposed),
            None,
        )
    option = proposed or (row["rivals"][0] if row["rivals"] else None)
    if option is None:
        return None
    return {
        "status": "proposed" if proposed else "strongest rival, not proposed",
        "appearanceId": option["appearanceId"],
        "personId": option["personId"],
        "folder": option["folder"],
        "score": option["score"],
        "signedDistinctRivalMargin": option["signedDistinctRivalMargin"],
        "independentSupportPhotoIds": option["independentSupportPhotoIds"],
        "referencePhotoIds": option.get(
            "referenceExamplePhotoIds", option.get("referencePhotoIds", []),
        ),
        "blockers": option["blockers"],
        "individuallyQualified": option["individuallyQualified"],
    }


def resolve_photo_locations(source, run):
    from . import metadata, review_packet

    source_by_id = {row["photoId"]: row for row in source["rows"]}
    root = pathlib.Path(run["workingRoot"])
    current = collections.defaultdict(list)
    # Only active identity originals; never walk backups, archives or derivatives.
    for category in (*LADDER, "Various"):
        category_root = root / category
        if not category_root.is_dir():
            continue
        identity_roots = [category_root] if category == "Various" else [
            path for path in category_root.iterdir() if path.is_dir() and not path.name.startswith("_")
        ]
        for identity in identity_roots:
            for bucket in ("gallery", "Review"):
                directory = identity / bucket
                if not directory.is_dir():
                    continue
                for path in directory.iterdir():
                    if path.is_file():
                        pid = metadata.photo_id_from_name(path.name)
                        if pid in source_by_id:
                            current[pid].append(path)
    catalog_path = root / ".likeness-library.json"
    catalog = json.loads(catalog_path.read_bytes()) if catalog_path.is_file() else None
    locations = {}
    for photo in run["photos"]:
        pid = photo["photoId"]
        destination = photo.get("destination")
        filename = pathlib.PurePosixPath(destination).name if destination else ""
        try:
            path = review_packet.safe_path(root, destination) if destination else None
        except (TypeError, ValueError, OSError):
            path = None
            status = "unsafe-receipt-destination"
        else:
            status = "available" if path is not None and path.is_file() else "missing"
        resolution = "historical-receipt-destination"
        matches = current.get(pid, [])
        if matches:
            path = matches[0] if len(matches) == 1 else None
            resolution = "unique-current-stable-photo-id"
            status = "available" if path is not None else "ambiguous-current-photo-id"
            if catalog is not None:
                expected = photo.get("preparedSHA256") or photo.get("sha256")
                if catalog["photos"].get(pid, {}).get("contentSha256") != expected:
                    status = "current-catalog-content-binding-differs"
            if path is not None:
                try:
                    path = review_packet.safe_path(root, path.relative_to(root).as_posix())
                except (TypeError, ValueError, OSError):
                    path = None
                    status = "unsafe-current-destination"
        locations[pid] = {
            "filename": path.name if path else filename or pid,
            "href": path.as_uri() if status == "available" else None,
            "status": status,
            "destination": destination,
            "currentImageDestination": path.relative_to(root).as_posix() if path is not None else None,
            "resolution": resolution,
            "sourceFolder": source_by_id.get(pid, {}).get("oldFolder"),
        }
    return locations


def run_sweep(state, run, vectors, ledger, *, progress=None, source_integrity=None):
    if len(state.get("rows", [])) != len(run.get("photos", [])):
        raise ValueError("directed shadow requires the complete saved source population")
    if len(state["rows"]) > 5000:
        raise ValueError("directed shadow exceeds the explicit 5,000-photo cap; report incomplete")
    result = _run_once(state, run, vectors, ledger, progress=progress)
    reverse_state = copy.deepcopy(state)
    reverse_state["rows"].reverse()
    reverse_state["appearances"].reverse()
    reverse_run = copy.deepcopy(run)
    reverse_run["photos"].reverse()
    reverse_ledger = copy.deepcopy(ledger)
    reverse_ledger["pairs"].reverse()
    reverse_ledger["referenceProposals"].reverse()
    reverse_vectors = dict(reversed(list(vectors.items())))
    if progress:
        progress("Verifying reversed full-population order.")
    reverse = _run_once(reverse_state, reverse_run, reverse_vectors, reverse_ledger, progress=progress)
    if _semantic(result) != _semantic(reverse):
        raise ValueError("directed shadow differs under reversed inputs; report incomplete")
    result["verification"] = {
        "reverseOrderVerified": True,
        "sameInputRepeatable": "covered by focused tests and receipt recheck; this run is immutable",
        "inputRowsReversed": True,
        "installedMoves": 0,
    }
    if source_integrity:
        result["sourceIntegrity"] = source_integrity
    if progress:
        progress(
            f'Directed shadow: {result["populationCount"]} saved photos; '
            f'{len(result["variants"])} paired recipes; reverse-order equality verified.'
        )
    return result


def render(result, photo_locations):
    browser_variants = []
    parent_folders = {}
    for variant in result["variants"]:
        for row in variant["rows"]:
            parent_folders.setdefault(row["sourcePersonId"], row["oldFolder"])
            for rival in row["rivals"]:
                parent_folders.setdefault(rival["personId"], rival["folder"])
    for variant in result["variants"]:
        rows = summary_for_page({"variants": [variant]})["variants"][0]["rows"]
        clusters = [
            {
                "id": group["id"], "name": group["name"], "state": group["state"],
                "candidateParentId": group["candidateParentId"],
                "candidateParentFolder": parent_folders.get(group["candidateParentId"]),
                "sourceFolder": group["sourceFolder"], "lineageIds": group["lineageIds"],
                "memberPhotoIds": group["memberPhotoIds"],
                "physicalHomeRemainsSource": group["physicalHomeRemainsSource"],
                "referenceAuthority": group["referenceAuthority"],
            }
            for group in variant["clusters"]
        ]
        browser_variants.append({
            "recipe": variant["recipe"], "summary": variant["summary"],
            "rows": rows, "clusters": clusters,
            "viewReconciliation": variant.get("viewReconciliation", []),
            "initialReferenceValidation": variant.get("initialReferenceValidation", []),
        })
    payload = {
        "variants": browser_variants,
        "photos": photo_locations,
        "limits": result["variants"][0]["limits"],
        "sourceIntegrity": result.get("sourceIntegrity", {}),
        "verification": result["verification"],
    }
    encoded = base64.b64encode(gzip.compress(
        json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8"),
        compresslevel=6, mtime=0,
    )).decode("ascii")
    summary_rows = [
        "<tr><td>" + html.escape(result["control"]["name"]) + "</td><td>"
        + str(result["control"]["populationCount"]) + "</td><td>"
        + str(result["control"]["proposalCount"]) + "</td><td>"
        + str(result["control"]["logicalReleases"]) + "</td><td>"
        + str(result["control"]["changedSourceDestinations"]) + "</td></tr>"
    ]
    for variant in result["variants"]:
        summary = variant["summary"]
        summary_rows.append(
            "<tr><td>" + html.escape(variant["recipe"]["name"]) + "</td><td>"
            + str(summary["populationCount"]) + "</td><td>"
            + str(summary["supportedUpwardAssociations"]) + "</td><td>"
            + str(summary["strongWrongIdentityCorrections"]) + "</td><td>"
            + str(summary["changedSourceDestinations"]) + "</td></tr>"
        )
    controls = (
        "<table><thead><tr><th>Recipe</th><th>Population</th><th>Proposal / upward</th>"
        "<th>Release / strong correction</th><th>Changed source destinations</th></tr></thead><tbody>"
        + "".join(summary_rows) + "</tbody></table>"
    )
    page = r"""<!doctype html><meta charset="utf-8"><title>Directed reformation shadow</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font:14px system-ui,sans-serif;max-width:1280px;margin:2em auto;padding:0 1em;color:#20242a}
table{border-collapse:collapse;table-layout:fixed;width:100%;margin:1em 0}th,td{border:1px solid #bbb;padding:.4em;text-align:left;vertical-align:top;overflow-wrap:anywhere}
th{background:#edf1f5}.warning{border-left:4px solid #b66;padding:.6em 1em;background:#fff8e9}
label{display:inline-grid;gap:.2em;margin:.4em .8em .4em 0;max-width:calc(100% - 1em);min-width:0}input,select,button{font:inherit;padding:.35em;max-width:100%;box-sizing:border-box}
.controls{display:flex;flex-wrap:wrap;align-items:end}.cards{display:grid;gap:12px}
article{border:1px solid #aeb8c2;border-radius:8px;padding:12px;background:#fff;min-width:0;overflow-wrap:anywhere}
article>div{min-width:0}pre{white-space:pre-wrap;overflow-wrap:anywhere}
.member-card{display:grid;grid-template-columns:minmax(180px,260px) 1fr;gap:14px}
.pictures{display:flex;flex-wrap:wrap;gap:8px;align-content:start}.pictures figure{margin:0;max-width:140px}
.pictures img{width:128px;height:128px;object-fit:cover;background:#edf1f5;border:1px solid #bbb}
figcaption{overflow-wrap:anywhere;font-size:12px}.badge{display:inline-block;padding:2px 6px;margin:2px;border-radius:10px;background:#edf1f5}
.supported{background:#e3f2e5}.tentative{background:#fff2d8}.residual{background:#e8e8f4}
.missing{color:#8a2c20;background:#fff0ec;padding:.4em}.muted{color:#555}.pager{margin:1em 0}
@media(max-width:700px){.member-card{grid-template-columns:1fr}.pictures img{width:104px;height:104px}}
</style>
<h1>Directed reformation — saved-measurement shadow</h1>
<p>Non-installable comparison only. Saved pre-incident Sandbox preview11 organisation and measurements,
not Production and not today's FAST organisation. Current originals are located by unique stable ID;
the current catalogue content binding is checked without re-reading image bytes. Images load only in your browser.
No photo copy, face extraction, model calls, moves or policy changes.</p>
<p class="warning">Positive controls are reviewed development fixtures, not blind accuracy. Threshold values are experimental recipes, not selected defaults. Fictional family assessment and GUI actions are not implemented here.</p>
<p>Candidate/rival details and frozen references are in <a href="directed-details.json.gz">the complete compressed evidence archive</a>. This page renders one bounded page of cards at a time; it does not place the full population or cluster inventory in the DOM.</p>
__CONTROLS__
<details><summary>Recipe parameters and per-category counts</summary><div id="recipeInfo"></div></details>
<h2>Image-first review</h2>
<div class="controls">
<label>Recipe<select id="variant"></select></label>
<label>Review mode<select id="view"><option value="members">Member decisions</option><option value="groups">Named cluster groups</option></select></label>
<label>Search<input id="search" placeholder="Photo, filename, folder, group or parent"></label>
<label>Exact source folder<select id="source"><option value="">All source folders</option></select></label>
<label>Filter<select id="filter"></select></label>
</div>
<p id="availability"></p><p id="count" aria-live="polite"></p>
<div class="pager"><button id="prev">Previous</button> <button id="next">Next</button></div>
<p id="loaderror" role="alert"></p><div id="cards" class="cards"></div>
<details><summary>Missing image links and source-map status</summary><div id="missing"></div></details>
<details><summary>Limitations, integrity and verification</summary><div id="limits"></div></details>
<p><a href="directed.json">Machine-readable page summary, including missing photo-link IDs</a></p>
<script type="application/octet-stream" id="data">__DATA__</script>
<script>
async function start(){
 const raw=Uint8Array.from(atob(document.getElementById("data").textContent),c=>c.charCodeAt(0));
 const stream=new Blob([raw]).stream().pipeThrough(new DecompressionStream("gzip"));
 const data=JSON.parse(await new Response(stream).text()),el=id=>document.getElementById(id);
 const pageSize=24;let page=0,visible=[],selectedCluster=null;
 const variants=data.variants,photos=data.photos;
 const score=value=>value===null||value===undefined?"unavailable":Number(value).toFixed(3);
 const text=(parent,value,tag="p")=>{const node=document.createElement(tag);node.textContent=value;parent.append(node);return node;};
 const groupsFor=variant=>new Map(variant.clusters.map(group=>[group.id,group]));
 const photoSearch=pid=>{const p=photos[pid]||{};return [pid,p.filename,p.sourceFolder,p.destination].join(" ").toLowerCase();};
 function picture(parent,pid,role){
  const info=photos[pid],fig=document.createElement("figure");
  if(!info||!info.href){const miss=text(fig,`Missing image link (${info?.status||"no receipt mapping"}): ${info?.filename||pid}`, "div");
   miss.className="missing";parent.append(fig);return;}
  const link=document.createElement("a"),img=document.createElement("img"),caption=document.createElement("figcaption");
  link.href=info.href;link.target="_blank";link.rel="noopener";img.src=info.href;img.alt=role+" — "+info.filename;
  img.loading="lazy";img.decoding="async";img.onerror=()=>{img.replaceWith(text(fig,"Image unavailable; receipt destination link retained.","span"));};
  caption.textContent=role+": "+info.filename;link.append(img);fig.append(link,caption);parent.append(fig);
 }
 function option(select,value,label){const node=document.createElement("option");node.value=value;node.textContent=label;select.append(node);}
 for(const variant of variants)option(el("variant"),variant.recipe.name,variant.recipe.name);
 for(const folder of [...new Set(variants[0].rows.map(r=>r.oldFolder).filter(Boolean))].sort()){
  option(el("source"),folder,folder);
 }
 const makeFilter=()=>{
  const f=el("filter");f.replaceChildren();
  if(el("view").value==="members"){
   [["all","All members"],["upward","Proposed upward appearance"],["correction","Strong correction proposal"],
    ["held","Held / no destination proposal"],["tentative","Tentative association"],["strongCore","Strong initial cast core"],
    ["referenceEligible","Eligible reference use"],["referenceWithdrawn","Reference use withdrawn / unqualified"],        ["locked","Physical placement block"],["reconciled","Reconciled lower-core appearance"],
    ["sameRank","Supported same-rank canonical appearance"]]
    .forEach(([v,l])=>option(f,v,l));
  }else{
   [["all","All named groups"],["supported","Supported"],["tentative","Tentative"],["residual","Residual"]]
    .forEach(([v,l])=>option(f,v,l));
  }
 };
 function draw(reset=false){
  if(reset)page=0;const variant=variants.find(v=>v.recipe.name===el("variant").value),mode=el("view").value;
  const query=el("search").value.trim().toLowerCase(),filter=el("filter").value,byGroup=groupsFor(variant);
  el("cards").replaceChildren();
  if(mode==="members"){
   visible=variant.rows.filter(r=>{
    const groups=r.clusterIds.map(id=>byGroup.get(id)).filter(Boolean);
    const hay=[r.photoId,r.oldFolder,r.shadowAction,r.candidateDestination,r.candidateTarget?.folder,
     ...groups.map(g=>g.name),...groups.map(g=>g.id),photoSearch(r.photoId)].join(" ").toLowerCase();
    return (!query||hay.includes(query))&&(!el("source").value||r.oldFolder===el("source").value)&&
     (!selectedCluster||r.clusterIds.includes(selectedCluster))&&
     (filter==="all"||(filter==="upward"&&r.shadowAction==="supported-upward-appearance")||
      (filter==="correction"&&r.shadowAction==="strong-wrong-identity-correction")||
      (filter==="held"&&!r.candidateDestination)||(filter==="tentative"&&r.tentativeAssociations.length>0)||
      (filter==="strongCore"&&r.strongInitialCastCoreDiagnostic)||
      (filter==="referenceEligible"&&r.referenceUseEligible)||
      (filter==="referenceWithdrawn"&&r.referenceUseDisposition==="withdrawn-or-unqualified-independent-of-placement")||
      (filter==="locked"&&r.placementBlocks.length>0)||
      (filter==="reconciled"&&(r.reconciledAppearanceIds||[]).length>0)||
      (filter==="sameRank"&&r.shadowAction==="supported-same-rank-appearance"));
   });
   for(const r of visible.slice(page*pageSize,(page+1)*pageSize)){
    const card=document.createElement("article");card.className="member-card";
    const pictures=document.createElement("div");pictures.className="pictures";picture(pictures,r.photoId,"Source");card.append(pictures);
    const body=document.createElement("div");card.append(body);
    text(body,r.shadowAction+" · "+r.membershipState,"h3");
    text(body,"Source: "+r.oldFolder+" · "+r.photoId);
    text(body,"Current image home: "+(photos[r.photoId]?.currentImageDestination||"unavailable"));
    for(const id of r.reconciledAppearanceIds||[]){
     const edge=variant.viewReconciliation.find(e=>e.appearanceId===id);
     if(edge)text(body,"Reconciled appearance: "+edge.sourceFolder+" → "+edge.ownerFolder+
      " · "+edge.acceptedPhotoIds.length+" accepted references; "+edge.exceptionPhotoIds.length+
      " held exceptions · mutual independent support, outside-rival margin "+score(edge.outsideMargin));
    }
    text(body,"Proposed destination: "+(r.candidateDestination||"none; remains in source home"));
    text(body,"Source own score: frozen "+score(r.frozenSourceScore)+"; current "+score(r.currentOwnScore)+
     ". Strong initial cast core: "+r.strongInitialCastCoreDiagnostic+
     ". Source reference use: "+r.referenceUseDisposition+(r.referenceUseEligible?" (eligible)":""));
    const target=r.candidateTarget;
    if(target){
     text(body,(target.status==="proposed"?"Proposed target":"Strongest rival, not proposed")+": "+
      target.folder+" · appearance "+target.appearanceId+" · score "+score(target.score)+
      " · signed margin "+score(target.signedDistinctRivalMargin)+
      " · independent support "+target.independentSupportPhotoIds.length+
      " · qualification "+(target.individuallyQualified?"qualified":"blocked"));
     if(target.blockers.length)text(body,"Target blockers: "+target.blockers.join(", "));
     const targetPictures=document.createElement("div");targetPictures.className="pictures";
     target.referencePhotoIds.slice(0,3).forEach(pid=>picture(targetPictures,pid,"Target reference"));
     if(targetPictures.childElementCount)body.append(targetPictures);
    }else text(body,"No measured target/rival available.");
    text(body,"Tentative associations: "+r.tentativeAssociations.length+
     " · all relevant rivals: "+r.allRelevantRivalsCount+" (complete evidence archive)");
    const unavailable=(variant.initialReferenceValidation||[]).filter(v=>v.referenceUnavailable);
    text(body,unavailable.length+" reference views unavailable after independent core validation; "+
     "withdrawal IDs and reasons remain in directed.json, not hidden competitors or placement releases.");
    const badges=document.createElement("div");
    for(const id of r.clusterIds){const group=byGroup.get(id);if(!group)continue;
     const badge=document.createElement("button");badge.className="badge "+group.state;
     badge.textContent=group.name+" ["+group.state+"]";badge.title="Browse this named group";
     badge.onclick=()=>{selectedCluster=id;el("view").value="members";makeFilter();el("filter").value="all";draw(true);};
     badges.append(badge);
    }
    body.append(badges);el("cards").append(card);
   }
  }else{
   visible=variant.clusters.filter(g=>{
    const hay=[g.id,g.name,g.state,g.candidateParentId,g.candidateParentFolder,g.sourceFolder,...g.memberPhotoIds]
     .join(" ").toLowerCase();
    return (!query||hay.includes(query))&&(!el("source").value||g.sourceFolder===el("source").value)&&
     (filter==="all"||g.state===filter);
   });
   for(const g of visible.slice(page*pageSize,(page+1)*pageSize)){
    const card=document.createElement("article");card.className="group-card";
    const badge=document.createElement("span");badge.className="badge "+g.state;badge.textContent=g.state;card.append(badge);
    text(card,g.name,"h3");text(card,"Group ID: "+g.id+" · lineage: "+g.lineageIds.join(", "));
    text(card,"Candidate parent: "+(g.candidateParentFolder||"unresolved")+" · "+(g.candidateParentId||"none"));
    text(card,"Source home: "+(g.sourceFolder||"unknown")+" · "+g.memberPhotoIds.length+
     " members · physical home remains source: "+g.physicalHomeRemainsSource);
    text(card,"Reference authority: "+g.referenceAuthority);
    const pictures=document.createElement("div");pictures.className="pictures";
    g.memberPhotoIds.slice(0,3).forEach(pid=>picture(pictures,pid,"Group member"));card.append(pictures);
    if(g.memberPhotoIds.length>3)text(card,"Representative images shown; "+(g.memberPhotoIds.length-3)+
     " additional members. Search member mode by group name or ID to page through them.","p").className="muted";
    const inspect=document.createElement("button");inspect.textContent="Inspect member decisions";
    inspect.onclick=()=>{selectedCluster=g.id;el("view").value="members";makeFilter();el("filter").value="all";draw(true);};
    card.append(inspect);el("cards").append(card);
   }
  }
  const start=visible.length?page*pageSize+1:0,end=Math.min((page+1)*pageSize,visible.length);
  el("count").textContent=visible.length?`${start}-${end} / ${visible.length} ${mode==="members"?"members":"named groups"}`
   +(selectedCluster?" · selected cluster "+selectedCluster:""):"No results";
  el("prev").disabled=page===0;el("next").disabled=(page+1)*pageSize>=visible.length;
 }
 el("variant").onchange=()=>{selectedCluster=null;draw(true);};
 el("view").onchange=()=>{selectedCluster=null;makeFilter();draw(true);};
 el("filter").onchange=()=>draw(true);el("search").oninput=()=>draw(true);
 el("source").onchange=()=>{selectedCluster=null;draw(true);};
 el("prev").onclick=()=>{page=Math.max(0,page-1);draw();};
 el("next").onclick=()=>{page++;draw();};
 const initial=variants[0];el("variant").value=initial.recipe.name;
 makeFilter();
 el("filter").value="upward";
 const available=Object.values(photos).filter(p=>p.status==="available").length;
 const missing=Object.entries(photos).filter(([,p])=>p.status!=="available");
 el("availability").textContent=`Receipt-bound photo destinations: ${available} available; ${missing.length} missing or unsafe. No image bytes were read/copied by report generation.`;
 const list=document.createElement("ul");
 for(const [pid,p] of missing.slice(0,200)){const item=document.createElement("li");
  item.textContent=pid+" · "+p.status+" · "+p.filename+" · "+(p.destination||"no saved destination");list.append(item);}
 if(missing.length>200)text(el("missing"),`${missing.length-200} additional missing/unsafe IDs are listed in directed.json.`,"p");
 el("missing").prepend(list);
 const limits=document.createElement("ul");
 for(const limit of data.limits)text(limits,limit,"li");
 el("limits").append(limits);
 text(el("limits"),"Historical source bindings and code drift: "+JSON.stringify(data.sourceIntegrity),"pre");
 text(el("limits"),"Verification: "+JSON.stringify(data.verification),"pre");
 for(const variant of variants){
  const details=document.createElement("details"),summary=document.createElement("summary");
  summary.textContent=variant.recipe.name+" · "+variant.summary.populationCount+" members · "+
   variant.summary.supportedUpwardAssociations+" upward · "+variant.summary.castStrongInitialCoreRetained+
   "/"+variant.summary.castStrongInitialCoreCount+" strong cast cores retained";
  details.append(summary);text(details,JSON.stringify({recipe:variant.recipe,summary:variant.summary},null,2),"pre");
  el("recipeInfo").append(details);
 }
 draw(true);
}
start().catch(error=>{document.getElementById("loaderror").textContent="Report data failed to load: "+error;});
</script></html>"""
    page = page.replace("__CONTROLS__", controls).replace("__DATA__", encoded)
    return page
