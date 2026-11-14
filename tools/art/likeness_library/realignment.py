"""Bounded, report-only full-population identity and reference hypotheses."""
import collections
import hashlib
import math
import pathlib

import numpy as np

from . import audit, character_packet, policy, protection
from .scoring import nz


MAX_PHOTOS = 5000
MAX_IDENTITIES = 512
MAX_PHOTOS_PER_IDENTITY = 1024
MAX_REFERENCES = 16000
MAX_REFERENCES_PER_IDENTITY = 256
MAX_CONFIRMED_CHARACTER_SETS = 32
MAX_EXPLICIT_INTENTS_PER_PHOTO = 16
MAX_DIRECT_PAIRS = 100_000
MAX_CANDIDATE_CELLS = 1_000_000
MAX_CANDIDATE_VECTOR_OPS = 1_500_000_000
MAX_APPEARANCE_PAIRS = 20_000_000
MAX_LOOKALIKE_PAIRS = 250_000
POSITIVE_CHOICES = {"reference", "same-not-reference"}
KNOWN_CHOICES = POSITIVE_CHOICES | {"different", "uncertain"}


def _unique(rows, name):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{name} must be a list of records")
    result = {row.get("photoId"): row for row in rows}
    if len(result) != len(rows) or not all(isinstance(pid, str) and pid for pid in result):
        raise ValueError(f"{name} requires unique stable photo IDs")
    return result


def _location(row):
    destination = row.get("destination")
    if not isinstance(destination, str) or not destination:
        raise ValueError("saved photo destination is missing")
    parts = pathlib.PurePosixPath(destination).parts
    if len(parts) == 3 and parts[0] == "Various" and parts[1] in {"gallery", "review"}:
        return "Various", parts[1]
    if len(parts) == 4 and parts[-2] in {"gallery", "review"}:
        return "/".join(parts[:2]), parts[-2]
    raise ValueError(f"unsupported baseline photo location: {destination}")


def _sha(row):
    value = row.get("preparedSHA256") or row.get("sha256")
    return value if isinstance(value, str) and value else None


def _manual_opt_out(*rows):
    return any(
        row.get("manualOptOut")
        or row.get("automaticProtectionOverride") == "disabled"
        or row.get("automaticProtectionDisabled")
        or isinstance(row.get("automaticProtection"), dict)
        and (
            row["automaticProtection"].get("manualOptOut")
            or row["automaticProtection"].get("override") == "disabled"
        )
        for row in rows
    )


def _finite_vector(value, photo_id):
    vector = np.asarray(value, dtype=float)
    if vector.ndim != 1 or not vector.size or not np.isfinite(vector).all():
        raise ValueError(f"invalid saved vector: {photo_id}")
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm) or norm == 0:
        raise ValueError(f"invalid saved vector: {photo_id}")
    return vector / norm


def _safe_number(value):
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite likeness evidence")
    return round(number, 6)


def _pair_evidence(effective_labels, photo_ids):
    if not isinstance(effective_labels, dict) or not isinstance(effective_labels.get("pairs"), list):
        raise ValueError("effective direct-pair evidence is missing")
    if len(effective_labels["pairs"]) > MAX_DIRECT_PAIRS:
        raise ValueError(f"direct pair evidence exceeds limit of {MAX_DIRECT_PAIRS}")
    pairs, adjacency = [], collections.defaultdict(list)
    seen = set()
    for pair in effective_labels["pairs"]:
        ids = pair.get("photoIds") if isinstance(pair, dict) else None
        label = pair.get("label") if isinstance(pair, dict) else None
        if (not isinstance(ids, list) or len(ids) != 2 or ids[0] == ids[1]
                or any(pid not in photo_ids for pid in ids)
                or not isinstance(label, str)
                or label not in {"same", "different", "uncertain"}):
            raise ValueError("invalid effective direct pair evidence")
        key = tuple(sorted(ids))
        if key in seen:
            raise ValueError("duplicate effective direct pair evidence")
        seen.add(key)
        pairs.append({"photoIds": list(key), "label": label})
        adjacency[ids[0]].append((ids[1], label))
        adjacency[ids[1]].append((ids[0], label))
    return sorted(pairs, key=lambda row: row["photoIds"]), adjacency


def _identity_id(folder, rows):
    lineage = sorted({
        identity_id
        for row in rows
        for identity_id in row.get("identityIds", [])
        if isinstance(identity_id, str) and identity_id
    })
    if len(lineage) == 1:
        return lineage[0]
    material = "\n".join([folder, *lineage])
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    return f"lineage:{digest}"


def _content_reference_set(rows, vectors, policy_config):
    return protection._independent([
        {"photoId": pid, "vector": vectors[pid], "sha256": rows[pid]["sha"]}
        for pid in sorted(vectors)
    ], policy_config)


def _appearance_groups(identity_id, photo_ids, vectors, threshold):
    photo_ids = sorted(photo_ids)
    if not photo_ids:
        return []
    matrix = np.asarray([vectors[pid] for pid in photo_ids], dtype=float)
    similarities = matrix @ matrix.T
    clusters = []
    for index, photo_id in enumerate(photo_ids):
        for members in clusters:
            if all(similarities[index, other] >= threshold for other in members):
                members.append(index)
                break
        else:
            clusters.append([index])
    result = []
    for members in clusters:
        ids = [photo_ids[index] for index in members]
        group_hash = hashlib.sha256(
            (identity_id + "\n" + "\n".join(ids)).encode("utf-8"),
        ).hexdigest()[:16]
        result.append((f"face-view:{group_hash}", ids))
    return result


def evaluate(run, vectors, packet, answers, effective_labels, *, excluded_reference_ids=()):
    """Rebuild frozen references and emit only bounded, non-executable hypotheses.

    The optional ID set is for label-blind diagnostics: excluded photos and every
    equal-content copy remain queryable but cannot enter any reconstructed core.
    """
    if not isinstance(run, dict) or not isinstance(run.get("policy"), dict):
        raise ValueError("run receipt and saved policy are required")
    policy_config = run["policy"]
    policy.validate_policy(policy_config)
    character_packet.validate_answers(packet, answers)
    photos = _unique(run.get("photos"), "receipt")
    saved_audit = _unique(
        run.get("finalMembershipAudit", {}).get("rows"), "audit",
    )
    if len(photos) > MAX_PHOTOS:
        raise ValueError(f"population exceeds realignment limit of {MAX_PHOTOS} photos")
    if photos.keys() != saved_audit.keys():
        raise ValueError("receipt/audit candidate conservation differs")
    for pid in photos:
        if photos[pid].get("destination") != saved_audit[pid].get("destination"):
            raise ValueError(f"receipt/audit placement differs: {pid}")
    if not isinstance(vectors, dict):
        raise ValueError("saved vectors must be keyed by stable photo ID")
    unknown_vectors = set(vectors) - set(photos)
    if unknown_vectors:
        raise ValueError(f"saved vectors contain unknown photo IDs: {sorted(unknown_vectors)[:5]}")

    if isinstance(excluded_reference_ids, (str, bytes)):
        raise ValueError("excluded_reference_ids must be an iterable of stable photo IDs")
    try:
        exclusion_values = list(excluded_reference_ids)
    except TypeError as exc:
        raise ValueError("excluded_reference_ids must be an iterable of stable photo IDs") from exc
    if any(not isinstance(pid, str) or not pid for pid in exclusion_values):
        raise ValueError("excluded_reference_ids must contain non-empty stable photo IDs")
    diagnostic_excluded_ids = frozenset(exclusion_values)
    unknown_exclusions = diagnostic_excluded_ids - set(photos)
    if unknown_exclusions:
        raise ValueError(f"unknown excluded reference photo IDs: {sorted(unknown_exclusions)[:5]}")

    labels, adjacency = _pair_evidence(effective_labels, set(photos))
    binding, audit_by_folder, photo_folder, bucket = {}, collections.defaultdict(list), {}, {}
    for pid in sorted(photos):
        photo, saved = photos[pid], saved_audit[pid]
        required_audit = {
            "qualityEligible", "ambiguousPhotoId", "metadataStale", "protected",
            "anchor", "workflowSelected", "identityProtected", "rejectionHistory",
        }
        missing_audit = sorted(required_audit - saved.keys())
        if missing_audit:
            raise ValueError(
                f"saved audit safeguards missing for {pid}: {', '.join(missing_audit)}"
            )
        if not isinstance(saved["qualityEligible"], bool):
            raise ValueError(f"saved audit quality eligibility is invalid: {pid}")
        folder, saved_bucket = _location(saved)
        photo_folder[pid], bucket[pid] = folder, saved_bucket
        if _location(photo)[0] != folder or _location(photo)[1] != saved_bucket:
            raise ValueError(f"receipt/audit location differs: {pid}")
        if saved.get("bucket") and saved["bucket"].casefold() != saved_bucket:
            raise ValueError(f"saved audit bucket differs from receipt location: {pid}")
        digest, audit_digest = _sha(photo), _sha(saved)
        if digest and audit_digest and digest != audit_digest:
            raise ValueError(f"receipt/audit content binding differs: {pid}")
        digest = digest or audit_digest
        eligible = bool(saved.get("qualityEligible"))
        if eligible and pid not in vectors:
            raise ValueError(f"missing eligible saved vector: {pid}")
        if saved.get("coreMember") and pid not in vectors:
            raise ValueError(f"missing saved core vector: {pid}")
        if eligible and not digest:
            raise ValueError(f"missing content hash for eligible photo: {pid}")
        vector = _finite_vector(vectors[pid], pid) if pid in vectors else None
        binding[pid] = {
            "sha": digest, "vector": vector, "eligible": eligible,
            "stale": bool(saved.get("metadataStale") or saved.get("stale")),
            "ambiguous": bool(saved.get("ambiguousPhotoId")),
            "rejected": bool(
                saved.get("rejectionHistory") or saved.get("rejectedPersonIds")
                or saved.get("rejectionMetadataStale")
            ),
            "manualOptOut": _manual_opt_out(saved, photo),
            "automaticProtection": (
                saved.get("automaticProtection", photo.get("automaticProtection"))
            ),
            "protectionProvenance": (
                saved.get("protectionProvenance", photo.get("protectionProvenance"))
            ),
            "saved": saved,
        }
        audit_by_folder[folder].append(pid)
    dimensions = {item["vector"].shape for item in binding.values() if item["vector"] is not None}
    if len(dimensions) > 1:
        raise ValueError("inconsistent saved vector dimensions")

    if len(answers["characters"]) > MAX_CONFIRMED_CHARACTER_SETS:
        raise ValueError(
            f"confirmed character sets exceed limit of {MAX_CONFIRMED_CHARACTER_SETS}"
        )
    for group in answers["characters"]:
        if group["folder"] not in audit_by_folder:
            raise ValueError(f"confirmed character has no current identity: {group['folder']}")
    intent = collections.defaultdict(dict)
    confirmed_refs = collections.defaultdict(list)
    confirmed_folders = set()
    for group in answers["characters"]:
        confirmed_folders.add(group["folder"])
        for decision in group["decisions"]:
            pid, choice = decision["photoId"], decision["choice"]
            if choice == "unreviewed":
                continue
            intent[pid][group["folder"]] = choice
            if choice == "reference":
                confirmed_refs[group["folder"]].append(pid)
    if any(
        sum(choice in POSITIVE_CHOICES for choice in choices.values())
        > MAX_EXPLICIT_INTENTS_PER_PHOTO
        for choices in intent.values()
    ):
        raise ValueError(
            f"per-photo explicit intents exceed limit of {MAX_EXPLICIT_INTENTS_PER_PHOTO}"
        )
    ref_owner = {}
    for folder, ids in sorted(confirmed_refs.items()):
        if len(set(ids)) != len(ids):
            raise ValueError(f"duplicate confirmed reference: {folder}")
        for pid in ids:
            if pid in ref_owner:
                raise ValueError(f"reference assigned to multiple characters: {pid}")
            ref_owner[pid] = folder
    globally_eligible_gallery = {
        pid for pid, row in binding.items()
        if bucket[pid] == "gallery" and row["eligible"] and not row["stale"]
        and not row["ambiguous"] and not row["rejected"]
        and not row["manualOptOut"]
        and row["vector"] is not None
    }

    # Equal-content copies of held-out IDs are also removed from every reference set.
    excluded_hashes = {
        binding[pid]["sha"] for pid in diagnostic_excluded_ids if binding[pid]["sha"]
    }
    excluded_ref_ids = {
        pid for pid, row in binding.items()
        if pid in diagnostic_excluded_ids or row["sha"] in excluded_hashes
    }
    all_reference_ids = set()
    identities_by_folder = {}
    for folder, ids in sorted(audit_by_folder.items()):
        if folder.startswith("Various/") or folder == "Various":
            category = "Models"
        else:
            category = folder.split("/", 1)[0]
        if category not in policy_config["categoryPolicies"]:
            raise ValueError(f"identity category has no saved policy: {category}")
        members = [saved_audit[pid] for pid in ids]
        identity_id = _identity_id(folder, members)
        identities_by_folder[folder] = {
            "identityId": identity_id, "category": category,
            "side": "Artists" if category == "Artists" else "other",
        }
    if len(identities_by_folder) > MAX_IDENTITIES:
        raise ValueError(f"population exceeds realignment limit of {MAX_IDENTITIES} identities")
    oversized = [
        (folder, len(ids)) for folder, ids in audit_by_folder.items()
        if len(ids) > MAX_PHOTOS_PER_IDENTITY
    ]
    if oversized:
        folder, count = sorted(oversized)[0]
        raise ValueError(
            f"identity {folder} has {count} photos, exceeding the per-identity limit "
            f"of {MAX_PHOTOS_PER_IDENTITY}"
        )
    if len({item["identityId"] for item in identities_by_folder.values()}) != len(identities_by_folder):
        raise ValueError("current folders do not have unique stable identity lineage")

    # Build references from every current Gallery identity, replacing confirmed cast
    # sets with precisely the explicit human reference choices.
    reference_rows = {}
    for folder, group in sorted(identities_by_folder.items()):
        category = group["category"]
        rules = policy_config["categoryPolicies"][category]
        eligible_ids = [
            pid for pid in audit_by_folder[folder]
            if bucket[pid] == "gallery" and binding[pid]["eligible"]
            and not binding[pid]["stale"] and not binding[pid]["ambiguous"]
            and not binding[pid]["rejected"] and pid not in excluded_ref_ids
            and not binding[pid]["manualOptOut"]
            and pid not in ref_owner
            and binding[pid]["vector"] is not None
        ]
        if folder in confirmed_folders:
            proposed = [
                pid for pid in confirmed_refs[folder]
                if pid in globally_eligible_gallery and pid not in excluded_ref_ids
            ]
            loo_scores = {}
            for pid in proposed:
                others = [
                    other for other in proposed if other != pid
                    and binding[other]["sha"] != binding[pid]["sha"]
                ]
                loo_scores[pid] = (
                    float(binding[pid]["vector"] @ nz(np.sum(
                        [binding[other]["vector"] for other in others], axis=0,
                    ))) if others else None
                )
            seed_mode = "confirmed-character-intent"
            candidates = proposed
        else:
            anchors = {
                pid for pid in eligible_ids
                if saved_audit[pid].get("anchor") or photos[pid].get("castSeedAnchor")
            }
            protected = {
                pid for pid in eligible_ids if saved_audit[pid].get("protected")
            }
            audit_result = audit.audit_person(
                np.asarray([binding[pid]["vector"] for pid in eligible_ids], dtype=float),
                eligible_ids,
                anchor_ids=anchors, protected_ids=protected,
                minimum_core=rules["minimumUsablePhotosForOutlierActions"],
                seed_floor=rules["identityCoreMinimumSimilarity"],
                core_minimum=rules["identityCoreMinimumSimilarity"],
            )
            core_indices = audit_result["core_indices"]
            candidates = [eligible_ids[index] for index in core_indices]
            loo_scores = {
                eligible_ids[index]: audit_result["scores"][index]
                for index in core_indices
            }
            candidates = [
                pid for pid in candidates
                if loo_scores.get(pid) is not None
                and loo_scores[pid] >= rules["identityCoreMinimumSimilarity"]
            ]
            seed_mode = "audit-person-provisional"
        independent = _content_reference_set(binding, {
            pid: binding[pid]["vector"] for pid in candidates
        }, policy_config)
        independent_ids = [row["photoId"] for row in independent]
        if len(independent_ids) > MAX_REFERENCES_PER_IDENTITY:
            raise ValueError(f"identity exceeds reference limit: {folder}")
        all_reference_ids.update(independent_ids)
        reference_rows[folder] = {
            "candidateIds": sorted(candidates), "references": independent,
            "referenceIds": independent_ids, "looScores": loo_scores,
            "seedMode": seed_mode, "candidateCount": len(candidates),
            "eligibleCount": len(eligible_ids),
        }
    if len(all_reference_ids) > MAX_REFERENCES:
        raise ValueError(f"population exceeds realignment limit of {MAX_REFERENCES} references")

    minimum_support = policy_config["protection"]["automatic"]["minimumIndependentReferences"]
    min_lead = policy_config["photoRouting"]["minimumOwnCoreLead"]
    cluster_threshold = policy_config["identityActions"]["identityClusterMinimumSimilarity"]
    for folder, group in identities_by_folder.items():
        rules = policy_config["categoryPolicies"][group["category"]]
        refs = reference_rows[folder]["references"]
        independent_count = len(refs)
        core_count = reference_rows[folder]["candidateCount"]
        enough = (
            independent_count >= minimum_support
            and core_count >= rules["minimumUsablePhotosForOutlierActions"]
        )
        needed = max(
            0, minimum_support - independent_count,
            rules["minimumUsablePhotosForOutlierActions"] - core_count,
        )
        human_confirmed = reference_rows[folder]["seedMode"] == "confirmed-character-intent"
        reference_rows[folder].update(
            referenceStatus=(
                "confirmed-intent" if enough and human_confirmed else
                "provisional" if enough else "reference-needed"
            ),
            referenceNeeded=needed,
            independentCount=independent_count,
            categoryMinimum=rules["identityCoreMinimumSimilarity"],
        )

    query_ids = [
        pid for pid in sorted(photos)
        if binding[pid]["eligible"] and not binding[pid]["stale"]
        and not binding[pid]["ambiguous"] and binding[pid]["vector"] is not None
    ]
    identity_folders = sorted(identities_by_folder)
    if len(query_ids) * len(identity_folders) > MAX_CANDIDATE_CELLS:
        raise ValueError("candidate ranking exceeds bounded photo-by-identity limit")
    dimension = next(iter(dimensions), (0,))[0]
    if len(query_ids) * len(identity_folders) * dimension > MAX_CANDIDATE_VECTOR_OPS:
        raise ValueError("candidate ranking exceeds bounded vector-operation limit")
    ref_centers, ref_sums, ref_counts = {}, {}, {}
    ref_ids_by_folder, refs_by_sha = {}, collections.defaultdict(set)
    for folder, rows in reference_rows.items():
        if rows["references"]:
            ref_ids_by_folder[folder] = {
                item["photoId"] for item in rows["references"]
            }
            ref_sums[folder] = np.sum(
                [item["vector"] for item in rows["references"]], axis=0,
            )
            ref_counts[folder] = len(rows["references"])
            ref_centers[folder] = nz(np.mean(
                [item["vector"] for item in rows["references"]], axis=0,
            ))
            for item in rows["references"]:
                refs_by_sha[item["sha256"]].add(folder)
    query_matrix = np.asarray([binding[pid]["vector"] for pid in query_ids], dtype=float)
    center_folders = sorted(ref_centers)
    center_matrix = (
        np.asarray([ref_centers[folder] for folder in center_folders], dtype=float)
        if center_folders else np.empty((0, dimension))
    )
    center_scores = query_matrix @ center_matrix.T if center_folders else np.empty((len(query_ids), 0))
    scores_by_photo = {
        pid: {
            folder: float(center_scores[row_index, column])
            for column, folder in enumerate(center_folders)
        } for row_index, pid in enumerate(query_ids)
    }
    for pid in query_ids:
        excluded_folders = set(refs_by_sha.get(binding[pid]["sha"], ()))
        excluded_folders.update(
            folder for folder, ids in ref_ids_by_folder.items() if pid in ids
        )
        for folder in excluded_folders:
            query_excluded_ids = {
                ref["photoId"] for ref in reference_rows[folder]["references"]
                if ref["photoId"] == pid or ref["sha256"] == binding[pid]["sha"]
            }
            if not query_excluded_ids:
                continue
            excluded_vectors = [
                binding[ref_id]["vector"] for ref_id in sorted(query_excluded_ids)
            ]
            remaining_count = ref_counts[folder] - len(excluded_vectors)
            if remaining_count <= 0:
                scores_by_photo[pid].pop(folder, None)
                continue
            adjusted_sum = ref_sums[folder] - np.sum(excluded_vectors, axis=0)
            score = float(binding[pid]["vector"] @ nz(adjusted_sum))
            scores_by_photo[pid][folder] = score

    # A query is compared only with the best three same-side candidates; reference
    # support is calculated lazily for those bounded hypotheses.
    ranked_by_photo, support_cache = {}, {}
    support_candidate_bound = len(query_ids) * min(3, len(identity_folders))
    support_candidate_bound += sum(
        len({folder for folder, choice in intent.get(pid, {}).items()
             if choice in POSITIVE_CHOICES})
        for pid in query_ids
    )
    if support_candidate_bound * MAX_REFERENCES_PER_IDENTITY * dimension > MAX_CANDIDATE_VECTOR_OPS:
        raise ValueError("candidate support scoring exceeds bounded vector-operation limit")
    for pid in query_ids:
        source = photo_folder[pid]
        source_identity = identities_by_folder[source]
        ranked = sorted(
            (
                (score, folder) for folder, score in scores_by_photo[pid].items()
                if folder != source
                and identities_by_folder[folder]["side"] == source_identity["side"]
            ),
            key=lambda item: (-item[0], item[1].casefold()),
        )
        ranked_by_photo[pid] = ranked[:3]
        explicit_targets = {
            folder for folder, choice in intent.get(pid, {}).items()
            if choice in POSITIVE_CHOICES
        }
        selected_targets = {
            target for _score, target in ranked_by_photo[pid]
        } | explicit_targets
        for target in sorted(selected_targets):
            if target == source or target not in reference_rows:
                continue
            if identities_by_folder[target]["side"] != source_identity["side"]:
                continue
            key = (pid, target)
            if key not in support_cache:
                query_sha = binding[pid]["sha"]
                supporters = [
                    row["photoId"] for row in reference_rows[target]["references"]
                    if row["photoId"] != pid
                    and row["sha256"] != query_sha
                    and float(binding[pid]["vector"] @ row["vector"])
                    >= policy_config["categoryPolicies"][
                        identities_by_folder[target]["category"]
                    ]["photoRouteMinimum"]
                ]
                support_cache[key] = supporters
    support_work = len(support_cache) * MAX_REFERENCES_PER_IDENTITY * dimension
    if support_work > MAX_CANDIDATE_VECTOR_OPS:
        raise ValueError("candidate support scoring exceeds bounded vector-operation limit")

    # Rebuild bounded complete-link face-view hypotheses within current identities.
    appearance_pairs = sum(
        len([pid for pid in ids if binding[pid]["vector"] is not None
             and binding[pid]["eligible"]
             and not binding[pid]["stale"] and not binding[pid]["ambiguous"]]) ** 2
        for ids in audit_by_folder.values()
    )
    if appearance_pairs > MAX_APPEARANCE_PAIRS:
        raise ValueError("face-view grouping exceeds bounded pair-comparison limit")
    appearances, appearance_for_photo = [], {}
    for folder in identity_folders:
        identity_id = identities_by_folder[folder]["identityId"]
        usable = [
            pid for pid in audit_by_folder[folder]
            if binding[pid]["vector"] is not None and binding[pid]["eligible"]
            and not binding[pid]["stale"]
            and not binding[pid]["ambiguous"]
        ]
        for group_id, photo_ids in _appearance_groups(
            identity_id, usable, {pid: binding[pid]["vector"] for pid in usable},
            cluster_threshold,
        ):
            appearances.append({
                "groupId": group_id, "identityId": identity_id,
                "photoIds": photo_ids, "evidenceKind": "face-view hypothesis",
            })
            for pid in photo_ids:
                appearance_for_photo[pid] = group_id

    # Appearance similarity links are deliberately non-merging and non-kinship.
    folders_with_refs = sorted(ref_centers)
    if len(folders_with_refs) * (len(folders_with_refs) - 1) // 2 > MAX_LOOKALIKE_PAIRS:
        raise ValueError("lookalike association inventory exceeds bounded pair limit")
    lookalike_policy = policy_config["lookalikeGroups"]
    associations = []
    if lookalike_policy["automaticAssociationEnabled"]:
        for left_index, left in enumerate(folders_with_refs):
            for right in folders_with_refs[left_index + 1:]:
                if identities_by_folder[left]["side"] != identities_by_folder[right]["side"]:
                    continue
                similarity = float(ref_centers[left] @ ref_centers[right])
                if (
                    not lookalike_policy["associationMinimumSimilarity"] <= similarity
                    < lookalike_policy["associationMaximumSimilarityExclusive"]
                    or min(
                        reference_rows[left]["independentCount"],
                        reference_rows[right]["independentCount"],
                    ) < lookalike_policy["minimumIndependentPhotos"]
                ):
                    continue
                left_rivals = [
                    float(ref_centers[left] @ ref_centers[other])
                    for other in folders_with_refs
                    if other not in {left, right}
                    and identities_by_folder[other]["side"] == identities_by_folder[left]["side"]
                ]
                right_rivals = [
                    float(ref_centers[right] @ ref_centers[other])
                    for other in folders_with_refs
                    if other not in {left, right}
                    and identities_by_folder[other]["side"] == identities_by_folder[right]["side"]
                ]
                left_margin = similarity - max(left_rivals, default=-1.0)
                right_margin = similarity - max(right_rivals, default=-1.0)
                if min(left_margin, right_margin) < lookalike_policy["minimumReferenceMargin"]:
                    continue
                associations.append({
                    "identityIds": [
                        identities_by_folder[left]["identityId"],
                        identities_by_folder[right]["identityId"],
                    ],
                    "kind": "lookalike", "score": _safe_number(similarity),
                    "role": None, "relationshipState": "unassigned",
                    "provenance": "face similarity hypothesis; authored fictional roles only",
                })

    intent_by_folder_photo = collections.defaultdict(dict)
    for pid, choices in intent.items():
        for folder, choice in choices.items():
            intent_by_folder_photo[pid][folder] = choice
    character_positive_ids = collections.defaultdict(set)
    character_negative_ids = collections.defaultdict(set)
    for pid, choices in intent_by_folder_photo.items():
        for folder, choice in choices.items():
            if choice in POSITIVE_CHOICES:
                character_positive_ids[folder].add(pid)
            elif choice == "different":
                character_negative_ids[folder].add(pid)
    rows = []
    for pid in sorted(photos):
        saved = saved_audit[pid]
        source = photo_folder[pid]
        identity = identities_by_folder[source]
        row_binding = binding[pid]
        positive = sorted(
            folder for folder, choice in intent_by_folder_photo[pid].items()
            if choice in POSITIVE_CHOICES
        )
        negative = {
            folder for folder, choice in intent_by_folder_photo[pid].items()
            if choice == "different"
        }
        uncertain = {
            folder for folder, choice in intent_by_folder_photo[pid].items()
            if choice == "uncertain"
        }
        safeguards = []
        for field in (
            "protected", "anchor", "workflowSelected", "identityProtected",
            "metadataStale", "ambiguousPhotoId", "rejectionHistory",
            "rejectionMetadataStale",
        ):
            if saved.get(field):
                safeguards.append(field)
        if row_binding["stale"] and "metadataStale" not in safeguards:
            safeguards.append("metadataStale")
        if row_binding["ambiguous"] and "ambiguousPhotoId" not in safeguards:
            safeguards.append("ambiguousPhotoId")
        if row_binding["rejected"] and "rejectionHistory" not in safeguards:
            safeguards.append("rejectionHistory")
        if row_binding["manualOptOut"]:
            safeguards.append("manualOptOut")
        blockers = list(safeguards)
        is_eligible = row_binding["eligible"] and row_binding["vector"] is not None
        if not is_eligible:
            blockers.append("quality-ineligible")
        if pid in diagnostic_excluded_ids:
            blockers.append("diagnostic-reference-exclusion")
        if row_binding["sha"] in excluded_hashes:
            blockers.append("equal-content-diagnostic-exclusion")
        candidate_target, state, origin, reason = None, "baseline", "baseline", "saved membership retained as baseline"
        own_score = None
        if is_eligible and source in ref_centers:
            own_rows = [
                ref for ref in reference_rows[source]["references"]
                if ref["photoId"] != pid and ref["sha256"] != row_binding["sha"]
            ]
            if own_rows:
                own_score = float(row_binding["vector"] @ nz(np.mean(
                    [ref["vector"] for ref in own_rows], axis=0,
                )))
        top_candidates = []
        for score, target in ranked_by_photo.get(pid, []):
            target_refs = reference_rows[target]["references"]
            supporters = support_cache.get((pid, target), [])
            independent_query_refs = [
                ref["photoId"] for ref in target_refs
                if ref["photoId"] != pid and ref["sha256"] != row_binding["sha"]
            ]
            top_candidates.append({
                "folder": target,
                "identityId": identities_by_folder[target]["identityId"],
                "score": _safe_number(score),
                "support": len(supporters),
                "referencePhotoIds": independent_query_refs,
                "supportingReferencePhotoIds": supporters,
                "referenceStatus": reference_rows[target]["referenceStatus"],
            })
        for target in sorted(positive):
            if target in {item["folder"] for item in top_candidates}:
                continue
            score = scores_by_photo.get(pid, {}).get(target)
            if score is None:
                continue
            supporters = support_cache.get((pid, target), [])
            target_refs = reference_rows[target]["references"]
            independent_query_refs = [
                ref["photoId"] for ref in target_refs
                if ref["photoId"] != pid and ref["sha256"] != row_binding["sha"]
            ]
            top_candidates.append({
                "folder": target,
                "identityId": identities_by_folder[target]["identityId"],
                "score": _safe_number(score),
                "support": len(supporters),
                "referencePhotoIds": independent_query_refs,
                "supportingReferencePhotoIds": supporters,
                "referenceStatus": reference_rows[target]["referenceStatus"],
            })
        top_candidates.sort(key=lambda item: (-item["score"], item["folder"].casefold()))

        if positive:
            origin = "explicit-intent"
            if len(positive) == 1:
                candidate_target = positive[0]
                state = "tentative"
                reason = "explicit positive character intent; placement remains unapproved"
                if reference_rows[candidate_target]["referenceStatus"] == "reference-needed":
                    blockers.append("target-reference-needed")
                contradictory_pairs = [
                    (other, label) for other, label in adjacency.get(pid, [])
                    if (
                        label == "different"
                        and other in character_positive_ids[candidate_target]
                        or label == "same"
                        and other in character_negative_ids[candidate_target]
                    )
                ]
                direct_uncertain = [
                    other for other, label in adjacency.get(pid, [])
                    if label == "uncertain"
                    and (
                        other in reference_rows[candidate_target]["candidateIds"]
                        or other in character_positive_ids[candidate_target]
                    )
                    and binding[other]["sha"] != row_binding["sha"]
                ]
                direct_different = sorted(
                    other for other, label in adjacency.get(pid, [])
                    if label == "different"
                    and (
                        other in reference_rows[candidate_target]["candidateIds"]
                        or other in character_positive_ids[candidate_target]
                    )
                    and binding[other]["sha"] != row_binding["sha"]
                )
                if contradictory_pairs or direct_different:
                    state = "unresolved"
                    reason = "direct human different evidence vetoes the explicit candidate"
                    blockers.append("direct-human-different-veto")
                elif direct_uncertain:
                    blockers.append("direct-human-uncertainty")
            else:
                state = "unresolved"
                reason = "multiple positive character intents conflict"
                blockers.append("multiple-positive-character-intent")
        elif is_eligible and bucket[pid] == "gallery" and top_candidates:
            best = top_candidates[0]
            target = best["folder"]
            route_min = policy_config["categoryPolicies"][
                identities_by_folder[target]["category"]
            ]["photoRouteMinimum"]
            candidate_target = target if best["score"] >= route_min else None
            origin = "automatic-hypothesis" if candidate_target else "baseline"
            if candidate_target:
                second_score = top_candidates[1]["score"] if len(top_candidates) > 1 else None
                runnerup_margin = (
                    best["score"] - second_score if second_score is not None else 2.0
                )
                lead = min(
                    best["score"] - own_score if own_score is not None else -2.0,
                    runnerup_margin,
                )
                direct_different = sorted(
                    other for other, label in adjacency.get(pid, [])
                    if label == "different"
                    and (
                        other in reference_rows[target]["referenceIds"]
                        or other in character_positive_ids[target]
                    )
                    and binding[other]["sha"] != row_binding["sha"]
                )
                direct_same_negative = sorted(
                    other for other, label in adjacency.get(pid, [])
                    if label == "same" and other in character_negative_ids[target]
                    and binding[other]["sha"] != row_binding["sha"]
                )
                direct_uncertain = sorted(
                    other for other, label in adjacency.get(pid, [])
                    if label == "uncertain"
                    and other in reference_rows[target]["referenceIds"]
                    and binding[other]["sha"] != row_binding["sha"]
                )
                target_group = identities_by_folder[target]
                if target_group["category"] in {"Angels", "Sisters", "Demons"}:
                    if identity["category"] in {"Angels", "Sisters", "Demons"} and source != target:
                        blockers.append("cross-character-ownership-conflict")
                if target in negative:
                    blockers.append("explicit-different-veto")
                if target in uncertain:
                    blockers.append("explicit-uncertainty")
                if direct_different:
                    blockers.append("direct-human-different-veto")
                if direct_same_negative:
                    blockers.append("direct-human-contradiction")
                if direct_uncertain:
                    blockers.append("direct-human-uncertainty")
                if reference_rows[target]["referenceStatus"] == "reference-needed":
                    blockers.append("target-reference-needed")
                if reference_rows[source]["referenceStatus"] == "reference-needed":
                    blockers.append("source-reference-needed")
                if best["score"] < route_min:
                    blockers.append("below-target-photo-route-minimum")
                if best["support"] < minimum_support:
                    blockers.append("insufficient-independent-positive-reference-support")
                if own_score is None or lead < min_lead:
                    blockers.append("insufficient-own-or-runner-up-margin")
                rejected_ids = set(saved.get("rejectedPersonIds", []))
                destination_ids = {
                    identity_id for pid2 in audit_by_folder[target]
                    for identity_id in saved_audit[pid2].get("identityIds", [])
                }
                if rejected_ids.intersection(destination_ids):
                    blockers.append("destination-explicitly-rejected")
                # The shared policy is still the decision authority for normal moves.
                route = policy.evaluate_photo_route(
                    target_group["category"], score=best["score"], margin=max(0.0, lead),
                    identity_protected=any(
                        saved_audit[pid2].get("identityProtected")
                        for pid2 in audit_by_folder[target]
                    ),
                    photo_protected=bool(saved.get("protected")),
                    workflow_selected=bool(saved.get("workflowSelected")),
                    policy=policy_config, propose=True,
                )
                if route["decision"] != "auto-route":
                    blockers.append("shared-photo-route-policy-hold")
                if direct_different or direct_same_negative or target in negative or target in uncertain:
                    state = "unresolved"
                    reason = "human different/uncertain evidence blocks automatic association"
                elif blockers:
                    state = "tentative"
                    reason = "automatic candidate hypothesis does not clear every existing safeguard"
                else:
                    state = "tentative"
                    reason = "independent member-level match hypothesis; never a folder merge"
        if not positive and is_eligible:
            for target in sorted(negative | uncertain):
                if target == source:
                    state = "unresolved"
                    origin = "baseline"
                    candidate_target = None
                    reason = (
                        "explicitly different from current identity; destination unresolved"
                        if target in negative else
                        "human identity judgment is uncertain, not negative"
                    )
                    blockers.append(
                        "explicit-different-current-identity" if target in negative
                        else "explicit-uncertainty-current-identity"
                    )
        if not is_eligible or row_binding["stale"] or row_binding["ambiguous"]:
            state = "unresolved"
            if not positive:
                origin = "baseline"
                candidate_target = None
            reason = "saved quality/content/identity evidence is unavailable or ambiguous"
        if blockers and candidate_target is not None and origin == "automatic-hypothesis":
            state = "unresolved" if (
                "direct-human-different-veto" in blockers
                or "explicit-different-veto" in blockers
                or "explicit-uncertainty" in blockers
            ) else "tentative"
        if row_binding["rejected"]:
            state = "unresolved"
            if origin == "automatic-hypothesis":
                candidate_target = None
            reason = "persistent rejection evidence requires reconsideration, not silent reversal"
        if row_binding["manualOptOut"]:
            state = "unresolved"
            candidate_target = None
            reason = "manual opt-out prevents candidate and reference admission"

        cross_cast = (
            candidate_target is not None and source != candidate_target
            and identity["category"] in {"Angels", "Sisters", "Demons"}
            and identities_by_folder[candidate_target]["category"] in {"Angels", "Sisters", "Demons"}
        )
        if cross_cast and "cross-character-ownership-conflict" not in blockers:
            blockers.append("cross-character-ownership-conflict")
        if candidate_target in intent_by_folder_photo.get(pid, {}) and (
            intent_by_folder_photo[pid][candidate_target] in {"different", "uncertain"}
        ):
            state = "unresolved"
            candidate_target = None
            reason = "direct character intent is different or uncertain; no identity inferred"
            blockers.append("human-character-intent-veto")
        rows.append({
            "photoId": pid, "currentFolder": source,
            "candidateFolder": candidate_target, "state": state,
            "origin": origin, "referenceEligible": (
                is_eligible and pid in all_reference_ids
                and pid not in excluded_ref_ids
            ),
            "referenceReason": (
                "eligible reference in the rebuilt frozen set; see identity referenceStatus"
                if pid in all_reference_ids
                else (
                    "manual opt-out prevents reference admission" if row_binding["manualOptOut"]
                    else "excluded from current reference set by quality, content, safeguards or recipe"
                )
            ),
            "appearanceGroupId": appearance_for_photo.get(pid),
            "reason": reason, "blockers": sorted(set(blockers)),
            "reconsiderable": True,
            "evidence": {
                "ownScore": _safe_number(own_score),
                "topCandidates": top_candidates,
                "explicitIntentByFolder": dict(sorted(intent_by_folder_photo[pid].items())),
                "directPairEvidence": [
                    {
                        "otherPhotoId": other, "label": label,
                        "sameContent": binding[other]["sha"] == row_binding["sha"],
                    }
                    for other, label in sorted(adjacency.get(pid, []))
                ],
                "manualOptOut": row_binding["manualOptOut"],
                "automaticProtection": row_binding["automaticProtection"],
                "protectionProvenance": row_binding["protectionProvenance"],
            },
            "execution": "not-authorized",
        })

    identity_rows = []
    for folder in identity_folders:
        identity_id = identities_by_folder[folder]["identityId"]
        reference = reference_rows[folder]
        identity_rows.append({
            "identityId": identity_id, "folder": folder,
            "referencePhotoIds": reference["referenceIds"],
            "referenceStatus": reference["referenceStatus"],
            "referenceNeeded": reference["referenceNeeded"],
            "appearanceGroupIds": sorted(
                appearance["groupId"] for appearance in appearances
                if appearance["identityId"] == identity_id
            ),
            "referenceEvidence": {
                "construction": reference["seedMode"],
                "candidateCount": reference["candidateCount"],
                "independentCount": reference["independentCount"],
                "leaveOneOutScores": {
                    pid: _safe_number(score)
                    for pid, score in sorted(reference["looScores"].items())
                },
            },
        })
    explicit_count = sum(row["origin"] == "explicit-intent" for row in rows)
    automatic_count = sum(row["origin"] == "automatic-hypothesis" for row in rows)
    automatic_supported = sum(
        row["origin"] == "automatic-hypothesis"
        and row["candidateFolder"] is not None
        and not row["blockers"]
        for row in rows
    )
    output = {
        "schemaVersion": 1,
        "kind": "bounded-realignment-candidates",
        "recipe": {
            "referenceConstruction": (
                "all current Gallery identities; audit_person provisional cores; "
                "confirmed character reference choices replace those folders' cores"
            ),
            "categoryCoreMinimumSimilarity": {
                category: rules["identityCoreMinimumSimilarity"]
                for category, rules in sorted(policy_config["categoryPolicies"].items())
            },
            "minimumUsablePhotosForOutlierActions": {
                category: rules["minimumUsablePhotosForOutlierActions"]
                for category, rules in sorted(policy_config["categoryPolicies"].items())
            },
            "minimumIndependentReferences": minimum_support,
            "independentEvidenceMaximumSimilarity": policy_config["identityActions"][
                "independentEvidenceMaximumSimilarity"
            ],
            "photoRouteMinimumByCategory": {
                category: rules["photoRouteMinimum"]
                for category, rules in sorted(policy_config["categoryPolicies"].items())
            },
            "minimumOwnCoreLead": min_lead,
            "photoRouteMarginByCategory": {
                category: rules["photoRouteMargin"]
                for category, rules in sorted(policy_config["categoryPolicies"].items())
            },
            "identityClusterMinimumSimilarity": cluster_threshold,
            "lookalikeAssociationMinimumSimilarity": lookalike_policy[
                "associationMinimumSimilarity"
            ],
            "lookalikeAssociationMaximumSimilarityExclusive": lookalike_policy[
                "associationMaximumSimilarityExclusive"
            ],
            "lookalikeMinimumIndependentPhotos": lookalike_policy[
                "minimumIndependentPhotos"
            ],
            "lookalikeMinimumReferenceMargin": lookalike_policy[
                "minimumReferenceMargin"
            ],
            "automaticCandidateLimit": 3,
            "maxExplicitIntentTargetsPerPhoto": MAX_EXPLICIT_INTENTS_PER_PHOTO,
            "appearanceGrouping": "deterministic complete-link face-view hypothesis",
        },
        "identities": identity_rows,
        "appearances": appearances,
        "rows": rows,
        "associations": associations,
        "summary": {
            "photoCount": len(rows),
            "galleryPhotoCount": sum(value == "gallery" for value in bucket.values()),
            "eligibleQueryCount": len(query_ids),
            "identityCount": len(identity_rows),
            "qualifiedIdentityCount": sum(
                row["referenceStatus"] != "reference-needed" for row in identity_rows
            ),
            "referenceNeededIdentityCount": sum(
                row["referenceStatus"] == "reference-needed" for row in identity_rows
            ),
            "referenceCount": len(all_reference_ids),
            "appearanceGroupCount": len(appearances),
            "explicitIntentCandidateCount": explicit_count,
            "explicitIntentDecisionCount": sum(
                choice in KNOWN_CHOICES
                for choices in intent_by_folder_photo.values()
                for choice in choices.values()
            ),
            "automaticHypothesisCount": automatic_count,
            "automaticSupportedCandidateCount": automatic_supported,
            "unresolvedCount": sum(row["state"] == "unresolved" for row in rows),
            "excludedReferenceIdCount": len(diagnostic_excluded_ids),
            "excludedReferenceContentHashCount": len(excluded_hashes),
            "excludedReferencePhotoCount": len(excluded_ref_ids),
            "directPairCount": len(labels),
        },
        "limits": [
            "Report-only candidate generation; every row has execution=not-authorized.",
            "Saved vectors and receipt evidence only; no pixel reads, model inference or new measurements.",
            "This is not a full legacy routing replay or proof of identity truth.",
            "Face-view groups are hypotheses, not measured outfit/session or verified same-person groups.",
            "Direct pair labels do not propagate transitively; different labels veto, uncertainty is not negative.",
            "Cross-folder consolidation remains member-level hypotheses; no folder merge is proposed.",
            "Diagnostic reference exclusion is label-blind evidence partitioning, not a series-independent held-out evaluation.",
            "Manual opt-out blocks candidate/reference admission; automatic protection is surfaced but is not a new permanent lock.",
            (
                f"Hard limits: {MAX_PHOTOS} photos, {MAX_IDENTITIES} identities, "
                f"{MAX_REFERENCES} references, {MAX_CANDIDATE_CELLS} photo/identity cells, "
                f"{MAX_APPEARANCE_PAIRS} appearance pairs, {MAX_LOOKALIKE_PAIRS} lookalike pairs, "
                f"{MAX_DIRECT_PAIRS} direct pairs."
            ),
        ],
    }
    # JSON serialization is also a finite-value and public-contract check.
    import json

    json.dumps(output, allow_nan=False, sort_keys=True)
    return output
