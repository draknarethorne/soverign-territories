"""Report-only evidence for coherent subgroups inside frozen identities."""

import math
import re

import numpy as np

from . import protection


MAX_PHOTOS = 5000
MAX_IDENTITIES = 512
MAX_REFERENCES = 16000
MAX_CANDIDATE_CELLS = 1_000_000
MAX_PAIR_OPERATIONS = 20_000_000
MAX_DIRECT_PAIRS = 100_000
_LABELS = {"same", "different", "uncertain"}


def _records(value, name):
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError(f"{name} must be a list of records")
    return value


def _hash(row):
    value = row.get("preparedSHA256") or row.get("sha256")
    if value is not None and (not isinstance(value, str) or not value):
        raise ValueError("photo content hashes must be non-empty strings")
    return value


def _number(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def _safe(value):
    if value is None:
        return None
    return round(float(value), 6)


def _normalize_vector(value, photo_id):
    vector = np.asarray(value, dtype=float)
    if vector.ndim != 1 or not vector.size or not np.isfinite(vector).all():
        raise ValueError(f"invalid saved vector: {photo_id}")
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm) or norm == 0:
        raise ValueError(f"invalid saved vector: {photo_id}")
    if not math.isclose(norm, 1.0, rel_tol=1e-5, abs_tol=1e-5):
        raise ValueError(f"saved vector is not normalized: {photo_id}")
    return vector


def _is_review(row, photo):
    if any(
        isinstance(bucket, str) and bucket.casefold() == "review"
        for bucket in (row.get("bucket"), photo.get("bucket"))
    ):
        return True
    destination = photo.get("destination")
    locations = [row.get("currentFolder"), destination]
    return any(
        isinstance(location, str)
        and "review" in [part.casefold() for part in re.split(r"[/\\]+", location)]
        for location in locations
    )


class _PairBudget:
    def __init__(self):
        self.reference = 0
        self.query = 0
        self.centroid = 0
        self.support_cache_hits = 0

    @property
    def total(self):
        return self.reference + self.query + self.centroid

    def charge(self, kind, count=1):
        if self.total + count > MAX_PAIR_OPERATIONS:
            raise ValueError(
                f"fragment evidence pair operations exceed limit of {MAX_PAIR_OPERATIONS}: "
                f"{self.total} completed; next {kind} computation requires {count}"
            )
        setattr(self, kind, getattr(self, kind) + count)


class _ReferenceSimilarities:
    """One triangular similarity cache reused by clustering and the shared gate."""

    def __init__(self, photo_ids, vectors, budget):
        self.ids = tuple(sorted(photo_ids))
        self.indices = {photo_id: index for index, photo_id in enumerate(self.ids)}
        self.budget = budget
        size = len(self.ids)
        count = size * (size - 1) // 2
        budget.charge("reference", count)
        self.values = np.empty(count, dtype=float)
        if count:
            matrix = np.asarray([vectors[photo_id] for photo_id in self.ids], dtype=float)
            offset = 0
            for index in range(size - 1):
                length = size - index - 1
                self.values[offset:offset + length] = matrix[index + 1:] @ matrix[index]
                offset += length

    def get(self, left, right):
        first, second = sorted((self.indices[left], self.indices[right]))
        if first == second:
            raise ValueError("reference similarity cache does not score a photo against itself")
        offset = len(self.ids) * first - first * (first + 1) // 2 + second - first - 1
        return self.values[offset]


class _CachedReferenceVector:
    def __init__(self, photo_id, similarities):
        self.photo_id = photo_id
        self.similarities = similarities

    def __matmul__(self, other):
        if self.similarities is not other.similarities:
            raise ValueError("independent support crossed frozen identity reference sets")
        self.similarities.budget.support_cache_hits += 1
        return self.similarities.get(self.photo_id, other.photo_id)


def _complete_link_groups(similarities, threshold):
    ordered = similarities.ids
    if not ordered:
        return []
    groups = []
    for photo_id in ordered:
        for group in groups:
            if all(similarities.get(photo_id, member) >= threshold for member in group):
                group.append(photo_id)
                break
        else:
            groups.append([photo_id])
    return [tuple(group) for group in groups]


def _centroid_score(query, photo_ids, vectors, budget):
    if not photo_ids:
        return None
    members = np.asarray([vectors[photo_id] for photo_id in photo_ids], dtype=float)
    total = members.sum(axis=0)
    norm = float(np.linalg.norm(total))
    if not math.isfinite(norm) or norm == 0:
        return None
    budget.charge("centroid")
    return float(query @ (total / norm))


def _independent_support(
    query_scores, photo_ids, similarities, photos, route_minimum, policy_config,
):
    candidates = [
        photo_id for photo_id in photo_ids
        if query_scores[photo_id] >= route_minimum
    ]
    rows = [
        {
            "photoId": photo_id,
            "vector": _CachedReferenceVector(photo_id, similarities),
            "sha256": _hash(photos[photo_id]) or f"missing-hash:{photo_id}",
        }
        for photo_id in candidates
    ]
    chosen = protection._independent(rows, policy_config)
    return candidates, [row["photoId"] for row in chosen]


def _candidate_record(
    identity,
    subgroup,
    query_id,
    query_vector,
    query_scores,
    whole_score,
    whole_mean,
    photos,
    vectors,
    direct_labels,
    policy_config,
    similarities,
    budget,
):
    folder = identity["folder"]
    category = folder.split("/", 1)[0]
    route_minimum = float(policy_config["categoryPolicies"][category]["photoRouteMinimum"])
    route_margin = float(policy_config["categoryPolicies"][category]["photoRouteMargin"])
    excluded = {
        photo_id for photo_id in subgroup
        if photo_id == query_id
        or (
            query_vector is not None
            and _hash(photos[photo_id]) is not None
            and _hash(photos[photo_id]) == _hash(photos[query_id])
        )
    }
    used_ids = tuple(photo_id for photo_id in subgroup if photo_id not in excluded)
    blockers = []
    if query_vector is None:
        subgroup_score = subgroup_mean = None
        support_candidates, support_ids = [], []
        blockers.append("missing-query-vector")
    else:
        subgroup_score = _centroid_score(query_vector, used_ids, vectors, budget)
        subgroup_mean = (
            float(np.mean([query_scores[photo_id] for photo_id in used_ids]))
            if used_ids else None
        )
        support_candidates, support_ids = _independent_support(
            query_scores, used_ids, similarities, photos, route_minimum, policy_config,
        )
    minimum_support = policy_config["protection"]["automatic"]["minimumIndependentReferences"]
    if not used_ids:
        blockers.append("no-reference-evidence-after-query-exclusion")
    if subgroup_score is not None and subgroup_score < route_minimum:
        blockers.append("below-target-photo-route-minimum")
    if len(support_ids) < minimum_support:
        blockers.append("insufficient-independent-reference-support")

    labels = {
        direct_labels[other_id]
        for other_id in subgroup
        if other_id in direct_labels
        and direct_labels[other_id] in {"different", "uncertain"}
    }
    if "different" in labels:
        blockers.append("direct-different-veto")
    if "uncertain" in labels:
        blockers.append("direct-uncertainty-veto")

    return {
        "folder": folder,
        "wholeScore": _safe(whole_score),
        "subgroupScore": _safe(subgroup_score),
        "referencePhotoIds": list(used_ids),
        "supportCount": len(support_ids),
        "blockers": sorted(set(blockers)),
        "wholeMeanScore": _safe(whole_mean),
        "subgroupMeanScore": _safe(subgroup_mean),
        "subgroupMeanDelta": _safe(
            subgroup_mean - whole_mean
            if subgroup_mean is not None and whole_mean is not None else None
        ),
        "subgroupCentroidDelta": _safe(
            subgroup_score - whole_score
            if subgroup_score is not None and whole_score is not None else None
        ),
        "supportCandidateCount": len(support_candidates),
        "supportPhotoIds": support_ids,
        "status": "tentative",
        "identityEstablished": False,
        "_routeMargin": route_margin,
        "_subgroupKey": list(subgroup),
    }


def _sort_candidates(rows):
    return sorted(
        rows,
        key=lambda row: (
            row["subgroupScore"] is None,
            -(row["subgroupScore"] if row["subgroupScore"] is not None else 0.0),
            row["folder"],
            row["_subgroupKey"],
        ),
    )


def evaluate(candidate, run, vectors, effective):
    """Score each query against every frozen identity without changing membership."""
    if not isinstance(candidate, dict) or not isinstance(run, dict):
        raise ValueError("candidate output and run receipt must be records")
    policy_config = run.get("policy")
    if not isinstance(policy_config, dict):
        raise ValueError("run receipt and saved policy are required")
    try:
        cluster_threshold = _number(
            policy_config["identityActions"]["identityClusterMinimumSimilarity"],
            "identity cluster minimum",
        )
        independent_maximum = _number(
            policy_config["identityActions"]["independentEvidenceMaximumSimilarity"],
            "independent evidence maximum similarity",
        )
        minimum_support = policy_config["protection"]["automatic"]["minimumIndependentReferences"]
        categories = policy_config["categoryPolicies"]
    except (KeyError, TypeError) as exc:
        raise ValueError("saved policy is missing fragment evidence settings") from exc
    if not 0 <= cluster_threshold <= 1 or not 0 <= independent_maximum <= 1:
        raise ValueError("saved similarity settings must be between zero and one")
    if isinstance(minimum_support, bool) or not isinstance(minimum_support, int) or minimum_support < 1:
        raise ValueError("minimum independent references must be a positive integer")
    if not isinstance(categories, dict):
        raise ValueError("saved category policies are required")
    for category, rules in categories.items():
        if not isinstance(rules, dict):
            raise ValueError(f"invalid saved category policy: {category}")
        route_minimum = _number(rules.get("photoRouteMinimum"), f"{category} photo route minimum")
        route_margin = _number(rules.get("photoRouteMargin"), f"{category} photo route margin")
        if not 0 <= route_minimum <= 1 or not 0 <= route_margin <= 2:
            raise ValueError(f"invalid saved route settings for category: {category}")

    photo_rows = _records(run.get("photos"), "receipt photos")
    if len(photo_rows) > MAX_PHOTOS:
        raise ValueError(f"population exceeds fragment evidence limit of {MAX_PHOTOS} photos")
    photos = {}
    for photo in photo_rows:
        photo_id = photo.get("photoId")
        if not isinstance(photo_id, str) or not photo_id or photo_id in photos:
            raise ValueError("receipt requires unique stable photo IDs")
        _hash(photo)
        photos[photo_id] = photo

    identity_rows = _records(candidate.get("identities"), "candidate identities")
    if len(identity_rows) > MAX_IDENTITIES:
        raise ValueError(f"identity count exceeds fragment evidence limit of {MAX_IDENTITIES}")
    identities = {}
    reference_owner = {}
    total_references = 0
    identity_folders = set()
    for identity in identity_rows:
        identity_id, folder = identity.get("identityId"), identity.get("folder")
        refs = identity.get("referencePhotoIds")
        if (
            not isinstance(identity_id, str) or not identity_id
            or identity_id in identities
            or not isinstance(folder, str) or not folder
            or folder in identity_folders
            or not isinstance(refs, list)
            or any(not isinstance(photo_id, str) or photo_id not in photos for photo_id in refs)
            or len(set(refs)) != len(refs)
        ):
            raise ValueError("invalid candidate identity/reference set")
        if any(photo_id in reference_owner for photo_id in refs):
            raise ValueError("reference photo belongs to multiple identities")
        for photo_id in refs:
            reference_owner[photo_id] = identity_id
        total_references += len(refs)
        identity_folders.add(folder)
        identities[identity_id] = {
            **identity, "folder": folder, "referencePhotoIds": sorted(refs),
        }
    if total_references > MAX_REFERENCES:
        raise ValueError(f"reference count exceeds fragment evidence limit of {MAX_REFERENCES}")
    scoring_identities = {
        identity_id: identity for identity_id, identity in identities.items()
        if identity["folder"].split("/", 1)[0] in categories
    }
    scoring_references = {
        photo_id for photo_id, identity_id in reference_owner.items()
        if identity_id in scoring_identities
    }

    if not isinstance(vectors, dict):
        raise ValueError("saved vectors must be keyed by stable photo ID")
    unknown_vectors = set(vectors) - set(photos)
    if unknown_vectors:
        raise ValueError(f"saved vectors contain unknown photo IDs: {sorted(unknown_vectors)[:5]}")
    normalized = {
        photo_id: _normalize_vector(value, photo_id)
        for photo_id, value in vectors.items()
    }
    dimensions = {vector.shape[0] for vector in normalized.values()}
    if len(dimensions) > 1:
        raise ValueError("saved vectors must have one consistent dimension")
    missing_references = sorted(scoring_references - set(normalized))
    if missing_references:
        raise ValueError(f"missing saved vector for reference photo: {missing_references[0]}")

    query_rows = _records(candidate.get("rows"), "candidate rows")
    query_by_id = {}
    for row in query_rows:
        photo_id = row.get("photoId")
        if (
            not isinstance(photo_id, str) or photo_id not in photos
            or photo_id in query_by_id
            or not isinstance(row.get("currentFolder"), str)
            or not row["currentFolder"]
            or not isinstance(row.get("evidence"), dict)
            or not isinstance(row["evidence"].get("topCandidates"), list)
        ):
            raise ValueError("invalid or duplicate candidate query row")
        query_by_id[photo_id] = row
    if set(query_by_id) != set(photos):
        raise ValueError("candidate rows must cover every receipt photo exactly once")

    appearances = _records(candidate.get("appearances"), "candidate appearances")
    for appearance in appearances:
        if (
            not isinstance(appearance.get("identityId"), str)
            or appearance.get("identityId") not in identities
            or not isinstance(appearance.get("photoIds"), list)
            or any(
                not isinstance(photo_id, str) or photo_id not in photos
                for photo_id in appearance["photoIds"]
            )
        ):
            raise ValueError("invalid candidate appearance membership")

    if not isinstance(effective, dict) or not isinstance(effective.get("pairs"), list):
        raise ValueError("effective direct-pair evidence is required")
    if len(effective["pairs"]) > MAX_DIRECT_PAIRS:
        raise ValueError(f"direct pair evidence exceeds limit of {MAX_DIRECT_PAIRS}")
    direct = {}
    seen_pairs = set()
    for pair in effective["pairs"]:
        pair_ids = pair.get("photoIds") if isinstance(pair, dict) else None
        label = pair.get("label") if isinstance(pair, dict) else None
        if (
            not isinstance(pair_ids, list) or len(pair_ids) != 2
            or any(not isinstance(photo_id, str) for photo_id in pair_ids)
            or pair_ids[0] == pair_ids[1]
            or any(photo_id not in photos for photo_id in pair_ids)
            or not isinstance(label, str) or label not in _LABELS
        ):
            raise ValueError("invalid effective direct pair evidence")
        key = tuple(sorted(pair_ids))
        if key in seen_pairs:
            raise ValueError("duplicate effective direct pair evidence")
        seen_pairs.add(key)
        direct.setdefault(pair_ids[0], {})[pair_ids[1]] = label
        direct.setdefault(pair_ids[1], {})[pair_ids[0]] = label

    reference_pair_operations = sum(
        len(identity["referencePhotoIds"]) * (len(identity["referencePhotoIds"]) - 1) // 2
        for identity in scoring_identities.values()
    )
    scoring_query_count = sum(
        row["photoId"] in normalized and row["currentFolder"].split("/", 1)[0] in categories
        for row in query_rows
    )
    required_pair_operations = (
        reference_pair_operations + scoring_query_count * len(scoring_references)
    )
    if required_pair_operations > MAX_PAIR_OPERATIONS:
        raise ValueError(
            f"fragment evidence pair operations exceed limit of {MAX_PAIR_OPERATIONS}: "
            f"{required_pair_operations} required before centroid scoring "
            f"({reference_pair_operations} frozen reference pairs; "
            f"{scoring_query_count * len(scoring_references)} query-reference pairs)"
        )
    candidate_cells = len(query_rows) * len(identities)
    if candidate_cells > MAX_CANDIDATE_CELLS:
        raise ValueError(
            f"fragment evidence candidate cells exceed limit of {MAX_CANDIDATE_CELLS}"
        )

    budget = _PairBudget()
    similarities = {
        identity_id: _ReferenceSimilarities(identity["referencePhotoIds"], normalized, budget)
        for identity_id, identity in scoring_identities.items()
    }
    groups = {
        identity_id: _complete_link_groups(cache, cluster_threshold)
        for identity_id, cache in similarities.items()
    }
    output_rows = []
    supported_count = insufficient_count = direct_veto_count = review_count = 0
    baseline_disagreement_count = non_scoring_hold_count = 0
    for photo_id in sorted(query_by_id):
        row = query_by_id[photo_id]
        current_folder = row["currentFolder"]
        query_vector = normalized.get(photo_id)
        query_hash = _hash(photos[photo_id])
        non_scoring_hold = current_folder.split("/", 1)[0] not in categories
        own_identity = next(
            (
                identity for identity in scoring_identities.values()
                if identity["folder"] == current_folder
            ),
            None,
        )
        if query_vector is not None and not non_scoring_hold:
            budget.charge("query", len(scoring_references))
        query_scores = (
            {
                ref_id: float(query_vector @ normalized[ref_id])
                for ref_id in sorted(scoring_references)
            }
            if query_vector is not None and not non_scoring_hold else {}
        )

        def score_identity(identity):
            subgroups = groups[identity["identityId"]]
            if not subgroups:
                subgroups = [tuple()]
            all_refs = tuple(
                ref_id for ref_id in identity["referencePhotoIds"]
                if ref_id != photo_id
                and not (
                    query_hash is not None
                    and _hash(photos[ref_id]) is not None
                    and _hash(photos[ref_id]) == query_hash
                )
            )
            whole_score = (
                _centroid_score(query_vector, all_refs, normalized, budget)
                if query_vector is not None else None
            )
            whole_mean = (
                float(np.mean([query_scores[ref_id] for ref_id in all_refs]))
                if query_vector is not None and all_refs else None
            )
            return [
                _candidate_record(
                    identity, subgroup, photo_id, query_vector, query_scores,
                    whole_score, whole_mean, photos, normalized,
                    direct.get(photo_id, {}), policy_config,
                    similarities[identity["identityId"]], budget,
                )
                for subgroup in subgroups
            ]

        own_records = score_identity(own_identity) if own_identity else []
        own_record = _sort_candidates(own_records)[0] if own_records else None
        rivals = []
        query_is_artist = current_folder.split("/", 1)[0] == "Artists"
        for identity in scoring_identities.values():
            if non_scoring_hold:
                continue
            if own_identity is not None and identity["identityId"] == own_identity["identityId"]:
                continue
            if (identity["folder"].split("/", 1)[0] == "Artists") != query_is_artist:
                continue
            rivals.extend(score_identity(identity))
        ranked = _sort_candidates(rivals)
        direct_veto_count += sum(
            bool({"direct-different-veto", "direct-uncertainty-veto"}.intersection(record["blockers"]))
            for record in ranked
        )

        review_hold = _is_review(row, photos[photo_id])
        visible_ranked = ranked[:3]
        selected = None
        if visible_ranked and not review_hold:
            for record in visible_ranked:
                if (
                    record["subgroupScore"] is not None
                    and not {"direct-different-veto", "direct-uncertainty-veto"}
                    .intersection(record["blockers"])
                ):
                    selected = record
                    break
        suggestion = selected["folder"] if selected else None
        if suggestion is not None:
            selected["blockers"] = sorted(set(selected["blockers"]))
            better = [
                record for record in ranked
                if record["folder"] != suggestion
                and record["subgroupScore"] is not None
                and not {"direct-different-veto", "direct-uncertainty-veto"}
                .intersection(record["blockers"])
            ]
            runner_score = max((record["subgroupScore"] for record in better), default=None)
            if (
                selected["subgroupScore"] is not None
                and runner_score is not None
                and selected["subgroupScore"] - runner_score < selected["_routeMargin"]
            ):
                selected["blockers"] = sorted(
                    set(selected["blockers"]) | {"ambiguous-rival-margin"},
                )
            supported_count += not bool(
                {
                    "below-target-photo-route-minimum",
                    "insufficient-independent-reference-support",
                    "ambiguous-rival-margin",
                }
                .intersection(selected["blockers"])
            )
            insufficient_count += bool(
                {
                    "below-target-photo-route-minimum",
                    "insufficient-independent-reference-support",
                    "ambiguous-rival-margin",
                }
                .intersection(selected["blockers"])
            )
        if review_hold:
            review_count += 1
        if non_scoring_hold:
            non_scoring_hold_count += 1
        baseline_target = row.get("candidateFolder")
        if baseline_target is not None and not isinstance(baseline_target, str):
            raise ValueError("baseline candidate folder must be a string or null")
        if baseline_target != suggestion and baseline_target is not None:
            baseline_disagreement_count += 1

        def public_record(record):
            if record is None:
                return None
            return {key: value for key, value in record.items() if not key.startswith("_")}

        old_top = row["evidence"]["topCandidates"]
        baseline_top = None
        baseline_top_score = None
        if old_top:
            first = old_top[0]
            if not isinstance(first, dict):
                raise ValueError("baseline top candidate must be a record")
            baseline_top = first.get("folder")
            if baseline_top is not None and not isinstance(baseline_top, str):
                raise ValueError("baseline top candidate folder must be a string or null")
            baseline_top_score = _safe(first.get("score"))
        output_rows.append({
            "photoId": photo_id,
            "currentFolder": current_folder,
            "baselineTarget": baseline_target,
            "baselineTop": baseline_top,
            "baselineTopScore": baseline_top_score,
            "own": public_record(own_record),
            "topCandidates": [public_record(record) for record in visible_ranked],
            "suggestedFolder": suggestion,
            "execution": "not-authorized",
            "reconsiderable": True,
            "hold": (
                "review-placement-hold" if review_hold else
                "non-scoring-category-hold" if non_scoring_hold else None
            ),
        })

    reference_subgroup_count = sum(len(groups_) for groups_ in groups.values())
    return {
        "schemaVersion": 1,
        "kind": "coherent-fragment-evidence",
        "recipe": {
            "referenceGroups": "deterministic complete-link over frozen references",
            "identityClusterMinimumSimilarity": cluster_threshold,
            "independentEvidenceMaximumSimilarity": independent_maximum,
            "minimumIndependentReferences": minimum_support,
            "photoRouteMinimumByCategory": {
                category: rules["photoRouteMinimum"]
                for category, rules in sorted(categories.items())
            },
            "photoRouteMarginByCategory": {
                category: rules["photoRouteMargin"]
                for category, rules in sorted(categories.items())
            },
            "queryAndEqualContentExclusion": True,
            "explicitReviewAnswersUsedForScoring": False,
            "directPairLabelsPropagated": False,
            "unconfiguredCategoryHandling": "non-scoring identities; queries held without admission",
            "pairComputation": "frozen triangular reference cache shared with protection._independent",
            "suggestionSemantics": "tentative subgroup evidence; never an identity declaration",
            "supportedCandidateSemantics": (
                "selected tentative suggestion meets subgroup route floor, independent support "
                "minimum and rival margin; not baseline eligibility or execution approval"
            ),
        },
        "rows": output_rows,
        "summary": {
            "photoCount": len(output_rows),
            "identityCount": len(identities),
            "nonScoringIdentityCount": len(identities) - len(scoring_identities),
            "referenceCount": total_references,
            "referenceSubgroupCount": reference_subgroup_count,
            "candidateCellCount": candidate_cells,
            "pairOperationCount": budget.total,
            "referencePairOperationCount": budget.reference,
            "queryReferencePairOperationCount": budget.query,
            "centroidPairOperationCount": budget.centroid,
            "independentSupportCacheHitCount": budget.support_cache_hits,
            "suggestedCount": sum(row["suggestedFolder"] is not None for row in output_rows),
            "supportedCandidateCount": supported_count,
            "insufficientSupportCandidateCount": insufficient_count,
            "directVetoCandidateCount": direct_veto_count,
            "reviewHoldCount": review_count,
            "nonScoringCategoryHoldCount": non_scoring_hold_count,
            "baselineDisagreementCount": baseline_disagreement_count,
        },
        "limits": [
            f"Refuses populations above {MAX_PHOTOS} photos, {MAX_IDENTITIES} identities, "
            f"or {MAX_REFERENCES} frozen references; no truncation.",
            f"Refuses above {MAX_CANDIDATE_CELLS} query-identity cells or "
            f"{MAX_PAIR_OPERATIONS} estimated pair operations; no truncation.",
            "Report-only fragment comparison; no membership merges, reference writes, photo moves, "
            "or accepted precision claims.",
            "Baseline quality, stale metadata, opt-out, protection and character ownership are not "
            "admission gates replayed here; tentative evidence cannot override their saved holds.",
            "Direct different/uncertain labels veto only their linked query-reference pair and do "
            "not spread transitively.",
        ],
    }
