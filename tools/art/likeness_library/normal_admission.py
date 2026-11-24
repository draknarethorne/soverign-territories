"""Cast-priority individual admission from independently frozen references."""
import hashlib
import json
import pathlib
import re

import numpy as np

from . import metadata, protection, rejections
from .face_quality import reference_quality
from .policy import cast_seed_settings, evaluate_photo_route, score_band, validate_score_bands
from .scoring import nz

CAST = frozenset(("Sisters", "Angels"))


NAMED_RETAINED_UNSCORED = frozenset((
    "no independent comparison reference", "independent comparison core unavailable",
    "source does not meet the existing face-quality gate", "centered measurement unavailable",
))


def fresh_baseline_release_candidates(rows, policy, named_folders=()):
    """Assess a complete frozen named-Gallery inventory before identity formation.

    Selection is red/orange/unscored own scores plus, for Sisters/Angels only,
    scored members outside the configured cast seed (``castAdmission``
    ``seedTopCount``/``seedReleaseBelow``); cast seed members are exempt from
    band release. Unscored members of user-named identities (``named_folders``,
    IU16) are retained; their red/orange members are still released.
    The caller must bind each centered vector to its prepared measurement hash
    and the listed source bytes, establish quality/reference eligibility,
    effective trusted-anchor status and ambiguity from the initial source
    assessment, and supply *all* named
    Gallery rows, including non-voters and unavailable measurements. This
    function does no I/O, verifies none of those attestations, and authorizes
    neither routing nor publication. Review-entry thresholds are not own-score
    display bands.
    """
    from .audit import audit_person

    if not isinstance(rows, list):
        raise ValueError("fresh baseline Gallery inventory must be an array")
    validate_score_bands(policy["scoreBands"])
    seed_settings = cast_seed_settings(policy)
    categories = {"Sisters", "Angels", "Models", "Prospects", "Potentials"}
    owners, paths, ids, dimensions = {}, set(), set(), set()
    checked = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("fresh baseline Gallery row must be an object")
        photo_id, owner, path = row.get("photoId"), row.get("owner"), row.get("currentPath")
        digest, measured = row.get("sha256"), row.get("measurementSha256")
        if (not isinstance(photo_id, str) or not photo_id
                or not isinstance(owner, str) or len(owner.split("/")) != 2
                or owner.split("/")[0] not in categories
                or not owner.split("/")[1]
                or not isinstance(path, str) or "\\" in path or ":" in path
                or len(path.split("/")) != 4 or path.split("/")[:3] != owner.split("/") + ["gallery"]
                or any(part in ("", ".", "..") for part in path.split("/"))
                or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            raise ValueError("fresh baseline row lacks a valid ID, Gallery path or source SHA-256")
        if photo_id in ids or path.casefold() in paths:
            raise ValueError("fresh baseline inventory has ambiguous IDs or paths")
        ids.add(photo_id)
        paths.add(path.casefold())
        for key in ("qualityEligible", "referenceEligible", "identityAnchor", "identityAmbiguous",
                    "sourceAmbiguous", "rejectionMetadataStale"):
            if type(row.get(key)) is not bool:
                raise ValueError(f"{photo_id}: missing explicit {key}")
        for key in ("ownerPersonIds", "rejectedPersonIds"):
            value = row.get(key)
            if (not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value)
                    or len(value) != len(set(value))):
                raise ValueError(f"{photo_id}: invalid {key}")
        status = row.get("sourceStatus")
        if not isinstance(status, str) or not status:
            raise ValueError(f"{photo_id}: missing source assessment status")
        vector = row.get("vector")
        if vector is not None:
            vector = np.asarray(vector, dtype=float)
            if (vector.ndim != 1 or not vector.size or not np.isfinite(vector).all()
                    or not np.isclose(np.linalg.norm(vector), 1.)
                    or not isinstance(measured, str) or not re.fullmatch(r"[0-9a-f]{64}", measured)):
                raise ValueError(f"{photo_id}: invalid or unbound centered measurement")
            dimensions.add(vector.size)
        elif measured is not None and (
            not isinstance(measured, str) or not re.fullmatch(r"[0-9a-f]{64}", measured)
        ):
            raise ValueError(f"{photo_id}: invalid measurement hash")
        owner_state = (tuple(sorted(row["ownerPersonIds"])), row["identityAmbiguous"])
        if owner in owners and owners[owner] != owner_state:
            raise ValueError(f"{owner}: inconsistent identity assessment")
        owners[owner] = owner_state
        checked.append((row, vector))
    if len(dimensions) > 1:
        raise ValueError("fresh baseline centered vector dimensions differ")

    # A content hash can vote at most once in the entire initial inventory.
    voting_hashes, voting_measurements = set(), set()
    for row, vector in checked:
        if row["referenceEligible"]:
            if (row["sourceStatus"] != "eligible" or not row["qualityEligible"]
                    or vector is None or row["sourceAmbiguous"]
                    or row["identityAmbiguous"] or row["rejectionMetadataStale"]
                    or set(row["rejectedPersonIds"]) & set(row["ownerPersonIds"])):
                raise ValueError(f'{row["photoId"]}: unsafe reference eligibility')
            if row["sha256"] in voting_hashes or row["measurementSha256"] in voting_measurements:
                raise ValueError("fresh baseline duplicate content has multiple reference votes")
            voting_hashes.add(row["sha256"])
            voting_measurements.add(row["measurementSha256"])

    assessed, bindings, blocked = [], [], []
    for row, vector in sorted(checked, key=lambda item: (item[0]["currentPath"].casefold(), item[0]["currentPath"])):
        photo_id, owner = row["photoId"], row["owner"]
        binding = {key: row[key] for key in ("photoId", "currentPath", "sha256")}
        evidence = {
            **binding, "owner": owner, "measurementSha256": row["measurementSha256"],
            "qualityEligible": row["qualityEligible"], "referenceEligible": row["referenceEligible"],
            "identityAnchor": row["identityAnchor"],
            "sourceStatus": row["sourceStatus"], "sourceAmbiguous": row["sourceAmbiguous"],
            "identityAmbiguous": row["identityAmbiguous"],
            "ownerPersonIds": sorted(row["ownerPersonIds"]),
            "rejectedPersonIds": sorted(row["rejectedPersonIds"]),
            "rejectionMetadataStale": row["rejectionMetadataStale"],
            "score": None, "band": None, "comparisonCoreMode": None, "comparisonReferences": [],
        }
        reason = None
        if row["sourceAmbiguous"] or row["identityAmbiguous"]:
            reason = "source or identity ambiguity requires resolution"
        elif row["rejectionMetadataStale"]:
            reason = "rejected-identity metadata is stale"
        elif set(row["rejectedPersonIds"]) & set(row["ownerPersonIds"]):
            reason = "own identity was explicitly rejected"
        elif not row["qualityEligible"]:
            reason = "source does not meet the existing face-quality gate"
        elif vector is None:
            reason = "centered measurement unavailable"
        else:
            refs = sorted(
                ((other, other_vector) for other, other_vector in checked
                 if other["owner"] == owner and other["referenceEligible"]
                 and other["photoId"] != photo_id and other["sha256"] != row["sha256"]
                 and other["measurementSha256"] != row["measurementSha256"]),
                key=lambda item: (item[0]["currentPath"].casefold(), item[0]["currentPath"]),
            )
            if refs:
                rules = policy["categoryPolicies"][owner.split("/")[0]]
                # Exclude the candidate and all its content aliases *before*
                # choosing the comparison core, not just from its centroid.
                audit = audit_person(
                    [ref_vector for _, ref_vector in refs],
                    [ref["photoId"] for ref, _ in refs],
                    anchor_ids=[ref["photoId"] for ref, _ in refs if ref["identityAnchor"]],
                    minimum_core=rules["minimumUsablePhotosForOutlierActions"],
                    core_minimum=rules["identityCoreMinimumSimilarity"],
                    seed_floor=rules["identityCoreMinimumSimilarity"],
                )
                chosen = [refs[index] for index in audit["core_indices"]]
                evidence["comparisonCoreMode"] = audit["mode"]
                center = nz(np.sum([ref_vector for _, ref_vector in chosen], axis=0)) if chosen else None
                if center is not None and np.linalg.norm(center):
                    evidence["score"] = float(np.clip(vector @ center, -1., 1.))
                    evidence["band"] = score_band(evidence["score"], policy)
                    evidence["comparisonReferences"] = [
                        {key: ref[key] for key in ("photoId", "currentPath", "sha256", "measurementSha256")}
                        for ref, _ in chosen
                    ]
                else:
                    reason = "independent comparison core unavailable"
            else:
                reason = "no independent comparison reference"
        evidence["unavailableReason"] = reason
        reasons = []
        named_owner = owner in set(named_folders)
        if evidence["score"] is None:
            # IU16: a named identity keeps members that are unscored only for lack of evidence;
            # rejections, stale metadata and ambiguity still release them.
            if named_owner and reason in NAMED_RETAINED_UNSCORED:
                evidence["namedRetained"] = True
            else:
                reasons.append("unscored")
        elif evidence["band"] == "orange" and named_owner:
            # IU16 (user, Nov 24): only truly low (red) members leave a user-named identity.
            evidence["namedRetained"] = True
        elif evidence["band"] in ("red", "orange"):
            reasons.append(f'band:{evidence["band"]}')
        evidence["selectionReasons"] = reasons
        evidence["castSeed"] = None
        block_reasons = []
        if row["sourceAmbiguous"] or row["identityAmbiguous"]:
            block_reasons.append("source or identity ambiguity")
        if row["rejectionMetadataStale"]:
            block_reasons.append("stale rejected-identity metadata")
        standard = row.get("standardName")
        if standard is not None and (not isinstance(standard, str) or "/" in standard or "\\" in standard):
            raise ValueError(f"{photo_id}: invalid standard filename")
        if (metadata.photo_id_from_name(pathlib.PurePosixPath(row["currentPath"]).name) != photo_id
                and (standard is None or metadata.photo_id_from_name(standard) != photo_id)):
            block_reasons.append("neither source nor standard filename encodes the bound photo ID")
        evidence["bindingBlocked"] = bool(block_reasons)
        evidence["bindingBlockReasons"] = block_reasons
        assessed.append((evidence, binding))
    seed = (_apply_cast_seed([evidence for evidence, _binding in assessed], seed_settings)
            if seed_settings["enabled"] else None)
    for evidence, binding in assessed:
        evidence["selected"] = bool(evidence["selectionReasons"])
        if evidence["selected"]:
            (blocked if evidence["bindingBlocked"] else bindings).append(binding)
    assessed = [evidence for evidence, _binding in assessed]
    return {
        "bindings": bindings, "blockedBindings": blocked, "assessment": assessed,
        "castSeed": seed,
        "policyEvidence": {
            "version": policy.get("version"),
            "scoreBands": json.loads(json.dumps(policy["scoreBands"])),
            "photoRoutingReviewMinimum": policy.get("photoRouting", {}).get("reviewMinimum"),
            "castReviewMinimum": policy.get("castAdmission", {}).get("reviewMinimum"),
            "castSeed": dict(seed_settings),
            "categoryReviewThresholds": {
                category: {
                    key: rules[key] for key in ("reviewRouteMinimum", "reviewSuggestionBelowSimilarity")
                    if key in rules
                }
                for category, rules in sorted(policy["categoryPolicies"].items())
                if category in categories
            },
        },
        "planningOnly": True,
    }


def _apply_cast_seed(assessed, settings):
    """Select scored Sisters/Angels members outside the seed for release.

    Per cast identity, the seed is the ``topCount`` highest own scores
    (no matter what the score is) plus every member at or above
    ``releaseBelow``. Seed members are exempt from all fresh release selection,
    including red/orange band release, so each identity keeps
    min(``topCount``, scored members) seeds. Other scored members are released
    in addition to the existing band selection. Unscored members cannot be
    ranked and stay released; ineligible/ambiguous rules are unchanged.
    """
    top, below = settings["topCount"], settings["releaseBelow"]
    identities = {}
    owners = sorted({row["owner"] for row in assessed if row["owner"].split("/", 1)[0] in CAST})
    for owner in owners:
        members = [row for row in assessed if row["owner"] == owner]
        scored = sorted(
            (row for row in members if row["score"] is not None),
            key=lambda row: (-row["score"], row["currentPath"].casefold(), row["currentPath"]),
        )
        for rank, row in enumerate(scored, 1):
            by_rank, by_score = rank <= top, row["score"] >= below
            row["castSeed"] = {
                "rank": rank, "seedMember": by_rank or by_score,
                "basis": ("top-count-and-threshold" if by_rank and by_score else
                          "top-count" if by_rank else "threshold" if by_score else None),
                "exemptedSelectionReasons": [],
            }
            if by_rank or by_score:
                # Scored rows can only carry band reasons; the seed overrides them.
                row["castSeed"]["exemptedSelectionReasons"] = list(row["selectionReasons"])
                row["selectionReasons"].clear()
            elif not row["selectionReasons"]:
                row["selectionReasons"].append("cast-seed-release")
        identities[owner] = {
            "memberCount": len(members), "scoredCount": len(scored),
            "seedPhotoIds": [row["photoId"] for row in scored if row["castSeed"]["seedMember"]],
            "seedBandExemptPhotoIds": [row["photoId"] for row in scored
                                       if row["castSeed"]["exemptedSelectionReasons"]],
            "seedReleasedPhotoIds": [row["photoId"] for row in scored
                                     if "cast-seed-release" in row["selectionReasons"]],
            "bandReleasedPhotoIds": [row["photoId"] for row in scored
                                     if any(reason.startswith("band:") for reason in row["selectionReasons"])],
            "unscoredReleasedPhotoIds": sorted(row["photoId"] for row in members if row["score"] is None),
        }
    return {
        "scope": "Sisters/Angels named Galleries in the fresh Sandbox source release only",
        "topCount": top, "releaseBelow": below, "identities": identities,
        "seedKeptCount": sum(len(item["seedPhotoIds"]) for item in identities.values()),
        "seedReleaseCount": sum(len(item["seedReleasedPhotoIds"]) for item in identities.values()),
    }


def reference_rows(space, cores, catalog):
    rows = {folder: [] for folder in cores}
    for photo in space.photos:
        photo_id = metadata.photo_id_from_name(photo.name)
        if photo.key not in cores or photo_id not in cores[photo.key]["corePhotoIds"]:
            continue
        checksum = metadata.content_sha256(photo.path)
        rows[photo.key].append({
            "photoId": photo_id, "sha256": checksum, "vector": photo.vec,
            "qualityEligible": (
                photo.usable(space.st["minFace"]) and photo.faces == 1
                and getattr(photo, "f2", 0.) <= space.st["multiFace"]
            ),
            **rejections.candidate_state(catalog, photo_id, checksum),
        })
    return rows


def context(cores, references, policy, *, locked=False):
    basis = {
        folder: protection._independent([
            row for row in rows
            if row["qualityEligible"] and not row.get("rejectionMetadataStale")
            and folder not in rejections.excluded_folders([row], cores)
        ], policy)
        for folder, rows in references.items()
    }
    fingerprint = {
        "cores": {folder: core["vector"].tolist() for folder, core in sorted(cores.items())},
        "references": {
            folder: [{"photoId": row["photoId"], "sha256": row["sha256"],
                      "vector": row["vector"].tolist()} for row in rows]
            for folder, rows in sorted(basis.items())
        },
    }
    return {
        "references": references, "independent": basis, "locked": locked,
        "castVectors": {
            folder: core["vector"] for folder, core in cores.items() if folder.split("/", 1)[0] in CAST
        },
        "referenceKeys": {
            folder: ({row["photoId"] for row in rows}, {row["sha256"] for row in rows})
            for folder, rows in references.items()
        },
        "referenceVersion": hashlib.sha256(
            json.dumps(fingerprint, sort_keys=True, allow_nan=False).encode()
        ).hexdigest(),
    }


def home_score(candidate, cores, admission):
    """An existing Gallery member's score against its own core without itself; None otherwise."""
    source = candidate.get("sourceFolder")
    if (not candidate.get("rebaseCandidate") or candidate.get("sourceBucket") != "Gallery"
            or source not in cores):
        return None
    rows = [
        row for row in ((admission or {}).get("references") or {}).get(source, [])
        if row["photoId"] != candidate["photoId"] and row["sha256"] != candidate.get("sha256")
    ]
    if rows:
        vector = nz(np.mean([row["vector"] for row in rows], axis=0))
    elif candidate["photoId"] in cores[source].get("corePhotoIds", ()):
        return None
    else:
        vector = cores[source]["vector"]
    if not np.linalg.norm(vector):
        return None
    return float(np.clip(candidate["vector"] @ vector, -1., 1.))


def beats_home(score, home, policy):
    """IU13a: an existing member moves only when the rival beats its home score by the own-core lead."""
    return home is None or score >= home + policy["photoRouting"]["minimumOwnCoreLead"]


def cast_route(candidate, cores, policy, admission):
    """Return one terminal cast decision, or None for ordinary lower routing."""
    if candidate["side"] != "Prospects":
        return None
    settings = policy["castAdmission"]
    excluded = rejections.excluded_folders([candidate], cores)
    if admission.get("redRelease") and candidate.get("redRelease") and candidate.get("detachedOutlier"):
        excluded.add(candidate["sourceFolder"])
    for pair in policy["runtimeSettings"]["different"]:
        if candidate["sourceFolder"] in pair:
            excluded.update(folder for folder in pair if folder != candidate["sourceFolder"])
    ranked = []
    for folder, core in cores.items():
        if folder.split("/", 1)[0] not in CAST or folder in excluded:
            continue
        refs = admission["references"].get(folder, [])
        keys = admission["referenceKeys"].get(folder, (set(), set()))
        if candidate["photoId"] in keys[0] or candidate.get("sha256") in keys[1]:
            remaining = [
                row for row in refs if row["photoId"] != candidate["photoId"]
                and row["sha256"] != candidate.get("sha256") and row["qualityEligible"]
                and not row.get("rejectionMetadataStale")
            ]
            if not remaining:
                continue
            vector = nz(np.mean([row["vector"] for row in remaining], axis=0))
        else:
            vector = admission["castVectors"].get(folder, core["vector"])
        if not np.linalg.norm(vector):
            continue
        ranked.append((float(np.clip(candidate["vector"] @ vector, -1., 1.)), folder))
    ranked.sort(key=lambda row: (-row[0], row[1].casefold(), row[1]))
    if not ranked or ranked[0][0] < settings["reviewMinimum"]:
        return None
    score, folder = ranked[0]
    if not beats_home(score, home_score(candidate, cores, admission), policy):
        # The home identity keeps the member; ordinary routing applies the same rule.
        return None
    rules = policy["categoryPolicies"][folder.split("/", 1)[0]]
    lead = score - ranked[1][0] if len(ranked) > 1 else 2.
    floor = rules.get("galleryAdmissionMinimumSimilarity", rules["photoRouteMinimum"])
    witnesses = [
        row for row in admission["independent"].get(folder, [])
        if row["photoId"] != candidate["photoId"]
        and row["sha256"] != candidate.get("sha256")
        and float(candidate["vector"] @ row["vector"]) <= policy["identityActions"]["independentEvidenceMaximumSimilarity"]
    ]
    enough = len(witnesses) >= settings["minimumIndependentReferences"]
    blockers = [other for other_score, other in ranked[1:] if score - other_score < rules["photoRouteMargin"]]
    approved = {frozenset(pair) for pair in settings["approvedClosePairs"]}
    close = bool(blockers) and all(frozenset((folder, other)) in approved for other in blockers)
    gallery = score >= floor and enough and rules.get("galleryAdmissionEnabled", False)
    mode = (
        "supported-gallery" if gallery and not blockers else
        "optimistic-gallery" if gallery and close else
        "ambiguous-review" if blockers else "named-review"
    )
    evidence = {
        "mode": mode, "winner": folder, "score": score, "margin": lead,
        "alternatives": [{"folder": other, "score": other_score} for other_score, other in ranked[1:]],
        "closePairs": [
            {"folders": [folder, other],
             "coreSimilarity": float(np.clip(cores[folder]["vector"] @ cores[other]["vector"], -1., 1.))}
            for other in blockers if frozenset((folder, other)) in approved
        ],
    }
    row = {
        "photoId": candidate["photoId"], "sourceFolder": candidate["sourceFolder"],
        "sourceBucket": candidate["sourceBucket"], "bestMatch": folder, "bestScore": score,
        "castAdmission": evidence, "referenceVersion": admission["referenceVersion"],
        "independentSupportCount": len(witnesses),
        "supportPhotoIds": [ref["photoId"] for ref in witnesses],
        "referenceEligible": mode == "supported-gallery" and reference_quality(candidate) and all(
            ref["photoId"] != candidate["photoId"]
            and ref["sha256"] != candidate.get("sha256")
            and float(candidate["vector"] @ ref["vector"]) <= policy["identityActions"]["independentEvidenceMaximumSimilarity"]
            for ref in admission["references"].get(folder, [])
        ),
        "lowerCategoryEvidence": sorted([
            {"folder": other, "score": float(np.clip(candidate["vector"] @ core["vector"], -1., 1.))}
            for other, core in cores.items()
            if other.split("/", 1)[0] in ("Models", "Prospects", "Potentials")
        ], key=lambda item: (-item["score"], item["folder"])),
    }
    if not candidate.get("qualityEligible", False):
        return "held", {**row, "preserveStaged": True, "reason": "cast candidate lacks eligible single-face quality"}
    if admission["locked"]:
        return "held", {**row, "preserveStaged": True, "reason": "cast receiving is locked for this run; rivals remain visible"}
    if mode.endswith("gallery"):
        row.update(
            destination=folder, destinationType="existing",
            reason="independent cast Gallery admission" if mode == "supported-gallery" else
            "approved close-pair Gallery placement; high rival, unconfirmed, non-core and unprotected",
        )
        if lead == 0:
            row["reason"] += "; exact cast tie: stable folder order is storage-only, not identity certainty"
        return "assignments", row
    if rules["reviewAdmissionEnabled"]:
        row.update(
            reviewDestination=f"{folder}/review", referenceEligible=False,
            reason=("cast ambiguity; provisional Review, not a new identity" if blockers else
                    "cast likeness requires Review: Gallery score, receiving or independent support gate not met"),
        )
        if lead == 0:
            row["reason"] += "; exact cast tie: stable folder order is storage-only, not identity certainty"
        return "held", row
    return "held", {**row, "preserveStaged": True, "reason": "cast Review admission is disabled"}


def refresh_references(cores, references, *, retire_ids=(), retire_sha256=()):
    """Rebuild frozen cores without retired IDs or content, without mutating inputs."""
    retired, retired_content = set(retire_ids), set(retire_sha256)
    remaining = {
        folder: [
            row for row in rows
            if row["photoId"] not in retired and row["sha256"] not in retired_content
        ]
        for folder, rows in references.items()
    }
    refreshed = {}
    for folder, rows in remaining.items():
        if not rows:
            continue
        vector = nz(np.mean([row["vector"] for row in rows], axis=0))
        if not np.linalg.norm(vector):
            continue
        refreshed[folder] = {
            **cores[folder], "vector": vector,
            "corePhotoIds": [row["photoId"] for row in rows],
        }
    return refreshed, {folder: remaining[folder] for folder in refreshed}


def _validate_red_references(cores, references):
    if set(cores) != set(references):
        raise ValueError("red release requires a complete frozen reference inventory")
    seen = set()
    shape = None
    for folder, core in cores.items():
        vector = np.asarray(core["vector"], dtype=float)
        if (vector.ndim != 1 or not np.isfinite(vector).all()
                or not np.isclose(np.linalg.norm(vector), 1.)):
            raise ValueError(f"{folder}: invalid frozen core vector")
        if shape is None:
            shape = vector.shape
        elif vector.shape != shape:
            raise ValueError(f"{folder}: inconsistent frozen vector dimensions")
        ids = core["corePhotoIds"]
        rows = references[folder]
        row_ids = [row["photoId"] for row in rows]
        if (not ids or len(ids) != len(set(ids)) or len(row_ids) != len(set(row_ids))
                or set(ids) != set(row_ids) or seen.intersection(row_ids)):
            raise ValueError(f"{folder}: incomplete or ambiguous frozen references")
        seen.update(row_ids)
        vectors = []
        for row in rows:
            reference = np.asarray(row["vector"], dtype=float)
            if (not isinstance(row["photoId"], str) or not row["photoId"]
                    or not isinstance(row["sha256"], str)
                    or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
                    or reference.shape != shape or not np.isfinite(reference).all()
                    or not np.isclose(np.linalg.norm(reference), 1.)):
                raise ValueError(f"{folder}: invalid frozen reference")
            vectors.append(reference)
        rebuilt = nz(np.mean(vectors, axis=0))
        if not np.allclose(vector, rebuilt, rtol=1e-6, atol=1e-8):
            raise ValueError(f"{folder}: frozen core differs from its references")
    return shape


def score_nonvoting_duplicates(api, candidates, cores, references, settings, policy, canonical_sources, *, locked=False):
    """Score bound non-voters individually against eligible frozen references.

    The caller must verify source bytes, canonical selection and measurements. This
    helper does not publish or grant reference authority. Each candidate is routed
    as an intake candidate, with its actual source restored in the returned decision;
    no candidate may form a cluster or become a reference for another candidate.
    """
    def relative(path):
        if (not isinstance(path, str) or not path or path.startswith("/") or "\\" in path or ":" in path
                or any(part in ("", ".", "..") for part in path.split("/"))):
            raise ValueError("non-voting candidate has an invalid source path")
        return path

    def sha(value):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("non-voting candidate has an invalid source SHA-256")
        return value

    if not isinstance(candidates, list) or not isinstance(canonical_sources, list):
        raise ValueError("non-voting candidates and canonical sources must be lists")
    if type(locked) is not bool:
        raise ValueError("non-voting cast lock must be explicit")
    canonical_by_path, canonical_by_id = {}, {}
    for row in canonical_sources:
        if not isinstance(row, dict):
            raise ValueError("non-voting canonical source is invalid")
        path, digest, photo_id = relative(row.get("source")), sha(row.get("sourceHash")), row.get("photoId")
        if not isinstance(photo_id, str) or not photo_id or photo_id != photo_id.strip():
            raise ValueError("non-voting canonical source lacks a stable ID")
        if path.casefold() in canonical_by_path or photo_id in canonical_by_id:
            raise ValueError("non-voting canonical source is ambiguous")
        canonical_by_path[path.casefold()] = (path, photo_id, digest)
        canonical_by_id[photo_id] = path

    _validate_red_references(cores, references)
    reference_content = set()
    for folder, rows in references.items():
        for row in rows:
            if (row.get("qualityEligible") is not True or row.get("rejectionMetadataStale")
                    or folder in rejections.excluded_folders([row], cores)):
                raise ValueError(f"{folder}: non-voting scoring requires eligible references")
            if row["sha256"] in reference_content:
                raise ValueError("non-voting scoring has duplicate reference content")
            reference_content.add(row["sha256"])

    ids, paths, results = set(), set(), []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("non-voting candidate is invalid")
        photo_id = candidate.get("photoId")
        if not isinstance(photo_id, str) or not photo_id or photo_id != photo_id.strip():
            raise ValueError("non-voting candidate lacks a stable ID")
        flags = ("protected", "workflowSelected", "identityProtected", "explicitReviewPlacement")
        rejection_stale = candidate.get("rejectionMetadataStale", False)
        rejected = candidate.get("rejectedPersonIds")
        if (any(type(candidate.get(flag)) is not bool for flag in flags)
                or type(rejection_stale) is not bool
                or (rejection_stale is False and (
                    not isinstance(rejected, list)
                    or any(not isinstance(item, str) or not item for item in rejected)))):
            raise ValueError(f"{photo_id}: non-voting guard evidence is missing or invalid")
        source = relative(candidate.get("source"))
        digest = sha(candidate.get("sourceHash"))
        canonical_source = relative(candidate.get("contentVoteCanonicalSource"))
        canonical_id = candidate.get("contentVoteCanonicalId")
        if (photo_id in ids or source.casefold() in paths
                or candidate.get("sourceStatus") != "same-content-nonvoting"
                or candidate.get("contentVoteStatus") != "nonvoting-duplicate-content"
                or candidate.get("sha256") != digest
                or canonical_by_path.get(canonical_source.casefold()) != (canonical_source, canonical_id, digest)
                or canonical_id == photo_id or source.casefold() == canonical_source.casefold()
                or type(candidate.get("qualityEligible")) is not bool):
            raise ValueError(f"{photo_id}: non-voting candidate or canonical binding is ambiguous or stale")
        parts = pathlib.PurePosixPath(source).parts
        bucket = candidate.get("sourceBucket")
        if (len(parts) < 3 or parts[-2] not in ("gallery", "review")
                or "/".join(parts[:-2]) != candidate.get("sourceFolder")
                or bucket not in ("Gallery", "Review", "Pool")
                or (bucket == "Pool" and (parts[-2] != "gallery" or parts[:-2] != ("Various",)))
                or (bucket != "Pool" and bucket.lower() != parts[-2])):
            raise ValueError(f"{photo_id}: non-voting source owner or bucket differs")
        ids.add(photo_id)
        paths.add(source.casefold())

        excluded = []
        for rows in references.values():
            for reference in rows:
                if reference["photoId"] == photo_id and reference["sha256"] != digest:
                    raise ValueError(f"{photo_id}: reference ID is bound to different content")
                if reference["photoId"] == photo_id or reference["sha256"] == digest:
                    excluded.append(reference["photoId"])
        frozen, frozen_rows = refresh_references(
            cores, references, retire_ids=(photo_id,), retire_sha256=(digest,),
        )
        admission = context(frozen, frozen_rows, policy, locked=locked)
        admission["deferGrouping"] = True
        try:
            measured_vector = np.asarray(candidate.get("vector"), dtype=float)
        except (TypeError, ValueError):
            measured_vector = np.asarray([])
        with np.errstate(over="ignore", invalid="ignore"):
            norm = np.linalg.norm(measured_vector)
        if (measured_vector.ndim != 1 or not measured_vector.size
                or not np.isfinite(measured_vector).all() or not np.isfinite(norm) or norm == 0):
            measured_vector = None
        # Matching uses the intake role, not a fabricated source path or owner.
        scoring = {**candidate, "sourceBucket": "Pool", "rebaseCandidate": False,
                   "detachedOutlier": False, "vector": measured_vector}
        planned = api.plan_reconciliation(
            [scoring], frozen, assign=settings["assign"], margin=settings["margin"],
            cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
            minimum_cluster=settings["minCluster"], cast_merge=policy["identityActions"]["autoMergeMinimum"],
            names_taken=(), name_factory=api.invent_name, policy=policy, admission_context=admission,
        )
        decisions = planned["assignments"] + planned["held"]
        if (planned["clusters"] or len(decisions) != 1
                or decisions[0].get("photoId") != photo_id
                or decisions[0].get("sourceFolder") != candidate["sourceFolder"]
                or decisions[0].get("sourceBucket") != "Pool"
                or decisions[0].get("destinationType") == "provisional"
                or (decisions[0].get("destination") and decisions[0].get("reviewDestination"))):
            raise ValueError(f"{photo_id}: non-voting scoring did not conserve its candidate")
        decision = {**decisions[0], "sourceBucket": bucket, "referenceEligible": False}
        score = decision.get("bestScore")
        if score is not None and (isinstance(score, bool) or not isinstance(score, (int, float, np.number))
                                  or not np.isfinite(score)):
            raise ValueError(f"{photo_id}: non-voting scoring returned an invalid score")
        comparisons = []
        if candidate["qualityEligible"] and not rejection_stale and measured_vector is not None:
            vector = nz(measured_vector)
            excluded_folders = rejections.excluded_folders([candidate], frozen)
            for folder, core in frozen.items():
                if (folder in excluded_folders or core["side"] != candidate.get("side")
                        or vector.shape != np.asarray(core["vector"]).shape):
                    continue
                if folder.split("/", 1)[0] in CAST and any(
                    candidate["sourceFolder"] in pair and folder in pair
                    and folder != candidate["sourceFolder"]
                    for pair in policy["runtimeSettings"]["different"]
                ):
                    continue
                comparisons.append({"folder": folder, "score": float(vector @ core["vector"])})
        comparisons.sort(key=lambda row: (-row["score"], row["folder"].casefold(), row["folder"]))
        if score is not None:
            matched = [row for row in comparisons if row["folder"] == decision.get("bestMatch")]
            if len(matched) != 1 or not np.isclose(score, matched[0]["score"], rtol=0., atol=0.00005 + 1e-12):
                raise ValueError(f"{photo_id}: non-voting decision score differs from independent comparisons")
        decision.setdefault("bestScore", None)
        decision.setdefault("bestMatch", None)
        results.append({
            "photoId": photo_id, "source": source, "sha256": digest,
            "canonicalPhotoId": canonical_id, "canonicalSource": canonical_source,
            "excludedReferencePhotoIds": sorted(excluded),
            "referenceVersion": admission["referenceVersion"],
            "scoreStatus": "available" if comparisons else "unavailable",
            "comparisons": comparisons,
            "decision": decision,
        })
    if ids.intersection(canonical_by_id) or paths.intersection(canonical_by_path):
        raise ValueError("non-voting canonical source is also a candidate")
    return {"results": sorted(results, key=lambda row: row["photoId"]), "clusters": []}


def follow_nonvoting_provisional(scored, candidates, voting_candidates, decisions, clusters, *, locked=False):
    """Attach exact duplicates after voting, without changing cluster membership or votes."""
    voters = {}
    for row in voting_candidates:
        photo_id = row.get("photoId")
        if not photo_id or photo_id in voters:
            raise ValueError("ambiguous voting candidate in non-voting cluster evidence")
        voters[photo_id] = row
    by_id = {}
    for row in decisions:
        by_id.setdefault(row.get("photoId"), []).append(row)
    duplicates = {row["photoId"]: row for row in candidates}
    if len(duplicates) != len(candidates):
        raise ValueError("ambiguous non-voting candidate in cluster evidence")
    results = []
    for original in scored["results"]:
        result = dict(original)
        candidate = duplicates.get(result["photoId"])
        if candidate is None:
            raise ValueError("non-voting score has no bound candidate")
        canonical_id = result["canonicalPhotoId"]
        if (
            candidate.get("source") != result.get("source")
            or candidate.get("sourceHash") != result.get("sha256")
            or candidate.get("sha256") != result.get("sha256")
            or candidate.get("contentVoteCanonicalId") != canonical_id
            or candidate.get("contentVoteCanonicalSource") != result.get("canonicalSource")
            or candidate.get("sourceStatus") != "same-content-nonvoting"
            or candidate.get("contentVoteStatus") != "nonvoting-duplicate-content"
        ):
            raise ValueError(f"{result['photoId']}: non-voting scored binding changed")
        canonical = voters.get(canonical_id)
        canonical_decisions = by_id.get(canonical_id, [])
        if canonical is None:
            results.append(result)
            continue
        if len(canonical_decisions) != 1:
            raise ValueError(f"{canonical_id}: canonical final decision is missing or ambiguous")
        decision = canonical_decisions[0]
        if decision.get("destinationType") != "provisional":
            results.append(result)
            continue
        if (
            canonical.get("source") != result["canonicalSource"]
            or canonical.get("sha256") != result["sha256"]
            or canonical.get("sourceFolder") != decision.get("sourceFolder")
            or canonical.get("sourceBucket") != decision.get("sourceBucket")
            or decision.get("normalAdmission") is not True
            or not decision.get("referenceVersion")
            or canonical.get("qualityEligible") is not True
            or canonical.get("rejectionMetadataStale")
            or decision.get("preserveStaged")
        ):
            raise ValueError(f"{canonical_id}: canonical provisional decision is stale or unbound")
        cluster_id, destination = decision.get("clusterId"), decision.get("destination")
        matching = [group for group in clusters if group.get("clusterId") == cluster_id]
        if len(matching) != 1:
            raise ValueError(f"{canonical_id}: canonical provisional cluster is missing or ambiguous")
        group = matching[0]
        members, core_ids = group.get("photoIds"), group.get("corePhotoIds")
        if (
            not isinstance(members, list) or not isinstance(core_ids, list)
            or not members or not core_ids
            or any(not isinstance(item, str) or not item for item in members + core_ids)
            or len(members) != len(set(members)) or len(core_ids) != len(set(core_ids))
            or not set(core_ids).issubset(members) or canonical_id not in members
            or result["photoId"] in members or group.get("destination") != destination
            or not isinstance(destination, str) or len(destination.split("/")) != 2
            or any(part in ("", ".", "..") or "\\" in part or ":" in part for part in destination.split("/"))
            or group.get("destinationType") != "provisional"
            or cluster_id != hashlib.sha256("\n".join(sorted(members)).encode()).hexdigest()[:16]
            or sum(
                canonical_id in other["photoIds"]
                for other in clusters if isinstance(other.get("photoIds"), list)
            ) != 1
        ):
            raise ValueError(f"{canonical_id}: canonical provisional cluster membership is ambiguous")
        for member in members:
            member_decisions = by_id.get(member, [])
            if (
                member not in voters or len(member_decisions) != 1
                or member_decisions[0].get("destination") != destination
                or member_decisions[0].get("clusterId") != cluster_id
                or member_decisions[0].get("destinationType") != "provisional"
                or member_decisions[0].get("referenceVersion") != decision["referenceVersion"]
                or member_decisions[0].get("normalAdmission") is not True
                or member_decisions[0].get("sourceFolder") != voters[member].get("sourceFolder")
                or member_decisions[0].get("sourceBucket") != voters[member].get("sourceBucket")
            ):
                raise ValueError(f"{canonical_id}: provisional cluster final decisions conflict")
        guards = (
            candidate.get("protected") or candidate.get("workflowSelected")
            or candidate.get("identityProtected") or candidate.get("explicitReviewPlacement")
            or candidate.get("rejectionMetadataStale") or not candidate.get("qualityEligible")
        )
        if guards or (locked and str(destination).split("/", 1)[0] in CAST):
            result["decision"] = {
                **result["decision"], "destination": None, "reviewDestination": None,
                "preserveStaged": True, "referenceEligible": False,
                "reason": "non-voting provisional placement blocked by quality, protection, Review, rejection or cast lock",
            }
            if not candidate.get("qualityEligible") or candidate.get("rejectionMetadataStale"):
                result.update(scoreStatus="unavailable", comparisons=[])
                result["decision"].update(bestScore=None, bestMatch=None)
            results.append(result)
            continue
        if candidate.get("rejectedPersonIds"):
            result["decision"] = {
                **result["decision"], "destination": None, "reviewDestination": None,
                "preserveStaged": True, "referenceEligible": False,
                "reason": "provisional identity cannot be bound safely to the candidate's rejected identities",
            }
            results.append(result)
            continue
        try:
            measured = np.asarray(candidate.get("vector"), dtype=float)
        except (TypeError, ValueError):
            measured = np.asarray([])
        with np.errstate(over="ignore", invalid="ignore"):
            measured_norm = np.linalg.norm(measured)
        if (measured.ndim != 1 or not measured.size or not np.isfinite(measured).all()
                or not np.isfinite(measured_norm) or not measured_norm):
            result["decision"] = {
                **result["decision"], "destination": None, "reviewDestination": None,
                "preserveStaged": True, "referenceEligible": False,
                "bestScore": None, "bestMatch": None,
                "reason": "non-voting provisional placement lacks an eligible measured vector",
            }
            result.update(scoreStatus="unavailable", comparisons=[])
            results.append(result)
            continue
        measured_sha = candidate.get("measurementSha256")
        if (
            not isinstance(measured_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", measured_sha)
            or measured_sha != canonical.get("measurementSha256")
        ):
            raise ValueError(f"{result['photoId']}: canonical prepared measurement bytes differ")
        try:
            canonical_vector = np.asarray(canonical.get("vector"), dtype=float)
        except (TypeError, ValueError):
            canonical_vector = np.asarray([])
        if (
            canonical_vector.shape != measured.shape or not np.isfinite(canonical_vector).all()
            or not np.allclose(measured, canonical_vector, rtol=1e-6, atol=1e-8)
        ):
            raise ValueError(f"{result['photoId']}: canonical and duplicate measurements differ")
        refs, content_seen = [], set()
        for member in core_ids:
            voter = voters[member]
            vector = np.asarray(voter.get("vector"), dtype=float)
            checksum = voter.get("sha256")
            if (
                voter.get("qualityEligible") is not True or voter.get("rejectionMetadataStale")
                or not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum)
                or checksum in content_seen or vector.shape != measured.shape
                or not np.isfinite(vector).all() or not np.isclose(np.linalg.norm(vector), 1.)
            ):
                raise ValueError(f"{canonical_id}: provisional core measurement is incomplete or ambiguous")
            content_seen.add(checksum)
            if checksum != result["sha256"] and member != result["photoId"]:
                refs.append(voter)
        core = nz(np.mean([row["vector"] for row in refs], axis=0)) if refs else None
        score = float(nz(measured) @ core) if core is not None and np.linalg.norm(core) else None
        result["provisionalEvidence"] = {
            "clusterId": cluster_id, "destination": destination,
            "photoIds": list(members), "corePhotoIds": list(core_ids),
            "canonicalCoreMember": canonical_id in core_ids,
            "independentReferencePhotoIds": [row["photoId"] for row in refs],
            "independentReferenceSHA256": [row["sha256"] for row in refs],
            "scoreStatus": "available" if score is not None else "unavailable",
            "score": score, "measurementSha256": measured_sha,
            "canonicalReferenceVersion": decision["referenceVersion"],
        }
        result["decision"] = {
            "photoId": result["photoId"], "sourceFolder": candidate["sourceFolder"],
            "sourceBucket": candidate["sourceBucket"], "destination": destination,
            "destinationType": "provisional", "clusterId": cluster_id,
            "bestMatch": destination if score is not None else None,
            "bestScore": score, "referenceVersion": result["referenceVersion"],
            "referenceEligible": False,
            "reason": "exact-content non-voter follows the bound canonical provisional decision; no additional vote",
        }
        results.append(result)
    if {row["photoId"] for row in results} != set(duplicates) or len(results) != len(duplicates):
        raise ValueError("non-voting scored results are missing or ambiguous")
    return {"results": results, "clusters": []}


def final_nonvoting_references(cores, references, voting_candidates, report, policy, *, locked=False):
    """Reconstruct the recorded second-round basis, then retire its final departures."""
    _validate_red_references(cores, references)
    if not isinstance(voting_candidates, list) or not isinstance(report, dict):
        raise ValueError("non-voting final reference evidence is invalid")
    snapshots = report.get("referenceSnapshots")
    rounds = report.get("matchingRounds")
    if (not isinstance(snapshots, dict) or not isinstance(snapshots.get("2"), dict)
            or not isinstance(snapshots["2"].get("photoIds"), dict)
            or not isinstance(rounds, list) or len(rounds) != 2
            or [row.get("round") for row in rounds if isinstance(row, dict)] != [1, 2]
            or not isinstance(rounds[1].get("retiredReferenceIds"), list)):
        raise ValueError("non-voting scoring lacks a complete two-round reference history")
    initial_refs = {row["photoId"]: row for rows in references.values() for row in rows}
    voters = {}
    for candidate in voting_candidates:
        photo_id = candidate.get("photoId")
        if not photo_id or photo_id in voters:
            raise ValueError("non-voting final reference candidates are ambiguous")
        voters[photo_id] = candidate
    snapshot = snapshots["2"]
    reconstructed = {}
    seen = set()
    for folder, photo_ids in snapshot["photoIds"].items():
        if (folder not in cores or not isinstance(photo_ids, list) or not photo_ids
                or len(photo_ids) != len(set(photo_ids)) or seen.intersection(photo_ids)):
            raise ValueError("non-voting final reference snapshot is ambiguous")
        seen.update(photo_ids)
        reconstructed[folder] = []
        for photo_id in photo_ids:
            ref, candidate = initial_refs.get(photo_id), voters.get(photo_id)
            if candidate is not None and ref is not None:
                try:
                    same_vector = np.allclose(candidate["vector"], ref["vector"], rtol=1e-6, atol=1e-8)
                except (KeyError, TypeError, ValueError):
                    same_vector = False
                if candidate.get("sha256") != ref["sha256"] or not same_vector:
                    raise ValueError(f"{photo_id}: candidate and frozen reference evidence differ")
            if ref is None and candidate is not None:
                ref = {
                    "photoId": photo_id, "sha256": candidate.get("sha256"),
                    "vector": candidate.get("vector"), "qualityEligible": candidate.get("qualityEligible"),
                    **{key: candidate[key] for key in ("rejectionMetadataStale", "rejectedPersonIds")
                       if key in candidate},
                }
            if ref is None:
                raise ValueError(f"{photo_id}: final voting reference cannot be reconstructed")
            reconstructed[folder].append(ref)
    frozen, reconstructed = refresh_references(cores, reconstructed)
    _validate_red_references(frozen, reconstructed)
    if context(frozen, reconstructed, policy, locked=locked)["referenceVersion"] != snapshot.get("referenceVersion"):
        raise ValueError("non-voting reference snapshot fingerprint differs")
    decisions = report.get("assignments", []) + report.get("held", [])
    by_id = {}
    for decision in decisions:
        by_id.setdefault(decision.get("photoId"), []).append(decision)
    retired = rounds[1]["retiredReferenceIds"]
    if len(retired) != len(set(retired)):
        raise ValueError("non-voting final retirement history is ambiguous")
    for photo_id in retired:
        entries = by_id.get(photo_id, [])
        if len(entries) != 1:
            raise ValueError(f"{photo_id}: final retiring decision is missing or ambiguous")
        decision = entries[0]
        review = decision.get("reviewDestination")
        target = decision.get("destination") or (review.rsplit("/", 1)[0] if review else None)
        if not target or (target == decision.get("sourceFolder") and not review):
            raise ValueError(f"{photo_id}: final retirement differs from its decision")
    # A release residual reassessment can change a held decision after the
    # round-two history was recorded; it cannot remain a voting reference.
    retired = set(retired) | {
        row["photoId"] for row in decisions if row.get("residualScoring")
    }
    retired_hashes = {
        row["sha256"] for rows in reconstructed.values() for row in rows
        if row["photoId"] in retired
    }
    final_cores, final_rows = refresh_references(
        frozen, reconstructed, retire_ids=retired, retire_sha256=retired_hashes,
    )
    return {
        "cores": final_cores, "references": final_rows,
        "referenceVersion": context(final_cores, final_rows, policy, locked=locked)["referenceVersion"],
        "retiredReferenceIds": sorted(retired),
        "retiredReferenceSHA256": sorted(retired_hashes),
    }


def reconsider_nonvoting_holds(api, candidates, cores, references, settings, policy, canonical_sources,
                               voting_candidates, report, *, locked=False, include_named_gallery=False):
    """Reconsider bound non-voters without adding any identity vote.

    The caller must verify classified source and canonical bytes, measurements,
    and all guard flags. Existing placements are never replaced by a weaker
    provisional-follow proposal; unsupported cases remain explicit holds.
    Named Gallery is opt-in, scoring-only and requires its own bound prepared
    measurement; a missing measurement remains unavailable, never borrowed
    from its keeper. A separate ownership-retirement transaction is needed
    before a Gallery proposal can become a move.
    """
    if type(include_named_gallery) is not bool:
        raise ValueError("named Gallery non-voting reconsideration must be explicit")
    def valid_source(source, photo_id, standard=None):
        if (not isinstance(source, str) or not source or "\\" in source or ":" in source
                or any(part in ("", ".", "..") for part in source.split("/"))):
            return False
        parts = pathlib.PurePosixPath(source).parts
        return (
            len(parts) in (3, 4)
            and parts[0] in {"Sisters", "Angels", "Models", "Prospects", "Potentials", "Various"}
            and (parts[0] == "Various") == (len(parts) == 3)
            and parts[-2] in ("gallery", "review")
            and (metadata.photo_id_from_name(parts[-1]) == photo_id
                 or (isinstance(standard, str) and "/" not in standard
                     and metadata.photo_id_from_name(standard) == photo_id))
        )

    for candidate in candidates:
        source = candidate.get("source")
        if not valid_source(source, candidate.get("photoId"), candidate.get("standardName")):
            raise ValueError("non-voting reconsideration requires a bound Review or Various source")
        parts = pathlib.PurePosixPath(source).parts
        named_gallery = parts[-2] == "gallery" and parts[0] != "Various"
        if (named_gallery and not include_named_gallery) or candidate.get("side") != "Prospects":
            raise ValueError("non-voting reconsideration requires a bound Review or Various source")
        if named_gallery:
            measured = candidate.get("measurementSha256")
            if candidate.get("vector") is not None and (
                not isinstance(measured, str) or not re.fullmatch(r"[0-9a-f]{64}", measured)
            ):
                raise ValueError(f'{candidate["photoId"]}: named Gallery measurement is not bound')
            if measured is not None and (
                not isinstance(measured, str) or not re.fullmatch(r"[0-9a-f]{64}", measured)
            ):
                raise ValueError(f'{candidate["photoId"]}: invalid named Gallery measurement binding')
    for source in canonical_sources:
        if not valid_source(source.get("source"), source.get("photoId"), source.get("standardName")):
            raise ValueError("non-voting canonical source identity differs from its filename")
    final = final_nonvoting_references(cores, references, voting_candidates, report, policy, locked=locked)
    scored = score_nonvoting_duplicates(
        api, candidates, final["cores"], final["references"], settings, policy,
        canonical_sources, locked=locked,
    )
    by_id = {row["photoId"]: row for row in candidates}
    unresolved = [
        row for row in scored["results"]
        if not row["decision"].get("destination") and not row["decision"].get("reviewDestination")
        and row["decision"].get("reason") ==
        "unresolved arrival awaits the one qualified reference boundary"
    ]
    followed = follow_nonvoting_provisional(
        {"results": unresolved}, [by_id[row["photoId"]] for row in unresolved],
        voting_candidates, report["assignments"] + report["held"], report.get("clusters", []), locked=locked,
    )
    followed_by_id = {row["photoId"]: row for row in followed["results"]}
    voters = {row["photoId"]: row for row in voting_candidates}
    results = []
    for original in scored["results"]:
        result = followed_by_id.get(original["photoId"], original)
        decision = result["decision"]
        if decision.get("destinationType") == "provisional":
            proof = result["provisionalEvidence"]
            if proof["canonicalReferenceVersion"] != report["referenceSnapshots"]["2"]["referenceVersion"]:
                raise ValueError(f'{original["photoId"]}: provisional cluster reference version differs')
            measured = nz(np.asarray(by_id[original["photoId"]]["vector"], dtype=float))
            maximum = policy["identityActions"]["independentEvidenceMaximumSimilarity"]
            witnesses = protection._independent([
                voters[photo_id] for photo_id in proof["independentReferencePhotoIds"]
                if float(measured @ voters[photo_id]["vector"]) <= maximum
            ], policy)
            center = nz(np.mean([row["vector"] for row in witnesses], axis=0)) if witnesses else None
            score = float(np.clip(measured @ center, -1., 1.)) if center is not None and np.linalg.norm(center) else None
            proof.update({
                "independentReferencePhotoIds": [row["photoId"] for row in witnesses],
                "independentReferenceSHA256": [row["sha256"] for row in witnesses],
                "independenceMaximumSimilarity": maximum,
                "scoreStatus": "available" if score is not None else "unavailable", "score": score,
            })
            decision["bestScore"] = score
            decision["bestMatch"] = decision["destination"] if score is not None else None
            comparisons = original["comparisons"]
            margin = score - max((item["score"] for item in comparisons), default=-1.) if score is not None else None
            category = decision["destination"].split("/", 1)[0]
            allowed = (
                score is not None and bool(proof["independentReferencePhotoIds"])
                and margin >= 0
                and policy.get("categoryPolicies", {}).get(category) is not None
                and score <= 1. and margin <= 2.
                and evaluate_photo_route(
                    category, score=score, margin=margin, policy=policy, propose=True,
                )["decision"] == "auto-route"
            )
            proof["distinctIdentityMargin"] = margin
            if not allowed:
                result["decision"] = {
                    **original["decision"], "preserveStaged": True, "referenceEligible": False,
                    "reason": "non-voting provisional follow lacks independent score or ordinary routing margin",
                }
        decision = result["decision"]
        decision["referenceEligible"] = False
        if not decision.get("destination") and not decision.get("reviewDestination"):
            decision["preserveStaged"] = True
        source_parts = pathlib.PurePosixPath(by_id[original["photoId"]]["source"]).parts
        if source_parts[0] != "Various" and source_parts[-2] == "gallery":
            result["routingProposal"] = dict(decision)
            result["decision"] = {
                **decision, "destination": None, "reviewDestination": None,
                "preserveStaged": True, "referenceEligible": False,
                "reason": "named Gallery scoring only; source ownership requires separate retirement",
            }
        results.append(result)
    return {
        "results": results, "clusters": [],
        "finalReferenceVersion": final["referenceVersion"],
        "retiredReferenceIds": final["retiredReferenceIds"],
        "retiredReferenceSHA256": final["retiredReferenceSHA256"],
    }


def verified_red_snapshot(receipt, report, root, routing_policy, *, diagnostic_workflow_gaps=False,
                          workflow_configuration_path=None):
    """Recheck a saved audit before using its candidate set for planning."""
    from . import actions, normal_recap

    root = pathlib.Path(root).resolve()
    report = pathlib.Path(report).absolute()
    manifest = normal_recap.publish(
        receipt, out=report, check=True, bind_red_natives=True,
        inspect_workflow_selections=True,
        workflow_configuration_path=workflow_configuration_path,
    )
    data = normal_recap.collect(receipt)
    if pathlib.Path(data["workingRoot"]).resolve() != root:
        raise ValueError("red snapshot is bound to another library root")
    normal_recap._attach_workflow_selection_bindings(data, configuration_path=workflow_configuration_path)
    normal_recap._bind_red_native_evidence(data)
    if data["inputs"] != manifest["inputs"]:
        raise ValueError("red snapshot inputs changed during verification")
    config = data["workflowConfig"]
    workflow_gaps = []
    if not config["rootMatches"]:
        workflow_gaps.append("workflow configuration is not isolated to this library")
    if config["unidentified"]:
        workflow_gaps.append("unidentified workflow selections")
    if workflow_gaps and not diagnostic_workflow_gaps:
        raise ValueError("red snapshot " + "; ".join(workflow_gaps))
    review = pathlib.Path(data["libraryRoot"]) / "people_gallery_review.html"
    payload = review.read_bytes()
    if hashlib.sha256(payload).hexdigest() != manifest["inputs"][str(review)]:
        raise ValueError("red Review snapshot changed during verification")
    snapshot_policy = normal_recap._script(payload.decode("utf-8"), "likeness-policy-data")
    if (not isinstance(snapshot_policy, dict)
            or snapshot_policy.get("scoreBands") != routing_policy["scoreBands"]):
        raise ValueError("red Review score bands differ from the routing policy")
    if normal_recap._red_candidate_evidence(data) != manifest["redCandidates"]:
        raise ValueError("red candidates changed during verification")
    config_path = pathlib.Path(
        actions.cw.CFG_PATH if workflow_configuration_path is None else workflow_configuration_path
    ).absolute()
    config_bytes = config_path.read_bytes()
    if hashlib.sha256(config_bytes).hexdigest() != manifest["inputs"][str(config_path)]:
        raise ValueError("red workflow configuration changed during verification")
    validated_config = actions.cw.validate_config(json.loads(config_bytes))
    for path, digest in manifest["inputs"].items():
        if metadata.content_sha256(pathlib.Path(path)) != digest:
            raise ValueError(f"red snapshot input changed during verification: {path}")
    report_bytes = report.with_suffix(".report.json").read_bytes()
    if json.loads(report_bytes) != manifest:
        raise ValueError("red report manifest changed during verification")
    return {
        "snapshotBands": snapshot_policy["scoreBands"],
        "snapshotCandidates": manifest["redCandidates"],
        "selectedIds": sorted({
            binding["photoId"] for binding in config["bindings"] if binding["photoId"]
        }),
        "inputBindings": manifest["inputs"],
        "configurationSHA256": hashlib.sha256(
            json.dumps(validated_config, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "reportManifestSHA256": hashlib.sha256(report_bytes).hexdigest(),
        "consumerCoverageVerified": False,
        "workflowGaps": workflow_gaps,
    }


def _red_cache_vectors(root, cache_path, needed):
    from . import normal_transaction

    root = pathlib.Path(root).resolve()
    cache_path = pathlib.Path(cache_path).absolute()
    try:
        relative = cache_path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("red measurement cache must be inside the selected library") from exc
    cache_path = normal_transaction.safe(root, relative)
    payload = cache_path.read_bytes()
    cache_hash = hashlib.sha256(payload).hexdigest()
    cache = json.loads(payload)
    mean = np.asarray(cache.get("centeringMean"), dtype=float)
    if (cache.get("centeringDomain") != "general" or mean.ndim != 1
            or not mean.size or not np.isfinite(mean).all()):
        raise ValueError("red measurement cache requires a finite general-domain centering mean")
    bound = {}
    for measurement in cache["emb"].values():
        evidence = measurement.get("alignmentEvidence") or {}
        digest = evidence.get("sourceSha256")
        if digest not in needed:
            continue
        if digest in bound and bound[digest] != measurement:
            raise ValueError(f"conflicting cached measurements for {digest}")
        bound[digest] = measurement
    vectors, model_ids = {}, set()
    for digest in needed:
        measurement = bound.get(digest)
        if not isinstance(measurement, dict):
            raise ValueError(f"missing content-bound red measurement: {digest}")
        evidence = measurement.get("alignmentEvidence") or {}
        model = evidence.get("model")
        if not isinstance(model, dict):
            raise ValueError(f"missing red measurement model provenance: {digest}")
        model_id = hashlib.sha256(
            json.dumps(model, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if (evidence.get("state") != "persisted" or evidence.get("modelId") != model_id
                or not isinstance(model.get("detector"), dict)
                or model["detector"].get("name") != "YuNet"
                or model["detector"].get("file") != "face_detection_yunet_2023mar.onnx"
                or not re.fullmatch(r"[0-9a-f]{64}", str(model["detector"].get("sha256", "")))
                or not isinstance(model.get("recognizer"), dict)
                or model["recognizer"].get("name") != "SFace"
                or model["recognizer"].get("file") != "face_recognition_sface_2021dec.onnx"
                or not re.fullmatch(r"[0-9a-f]{64}", str(model["recognizer"].get("sha256", "")))
                or not isinstance(model.get("opencv"), str) or not model["opencv"]
                or model.get("alignment") != "FaceRecognizerSF.alignCrop"):
            raise ValueError(f"invalid red measurement model provenance: {digest}")
        model_ids.add(model_id)
        raw = np.asarray(measurement.get("v"), dtype=float)
        if raw.shape != mean.shape or not np.isfinite(raw).all():
            raise ValueError(f"invalid cached red measurement vector: {digest}")
        vector = nz(raw - mean)
        if not np.linalg.norm(vector):
            raise ValueError(f"zero centered red measurement vector: {digest}")
        vectors[digest] = vector
    if needed and len(model_ids) != 1:
        raise ValueError("red Review evidence requires one measurement model")
    return cache_path, cache_hash, vectors, model_ids, bound


def verify_red_review_measurements(root, cache_path, snapshot_candidates):
    """Reproduce caller-verified saved scores from a root-local cache without inference."""
    needed = {
        digest
        for row in snapshot_candidates
        for digest in [row["nativeSha256"], *(member["sha256"] for member in row["reviewCore"])]
    }
    cache_path, cache_hash, vectors, model_ids, _ = _red_cache_vectors(root, cache_path, needed)
    differences = []
    for row in snapshot_candidates:
        context = row.get("scoreContext") or {}
        core = row["reviewCore"]
        ids = [member["photoId"] for member in core]
        member = context.get("coreMember")
        if (type(member) is not bool or type(context.get("coreSize")) is not int
                or context["coreSize"] != len(core) or len(ids) != len(set(ids))
                or (row["photoId"] in ids) != member
                or type(row.get("score")) not in (int, float) or not np.isfinite(row["score"])):
            raise ValueError(f'{row["photoId"]}: inconsistent saved Review core membership')
        refs = [vectors[item["sha256"]] for item in core
                if not member or item["photoId"] != row["photoId"]]
        if not refs:
            raise ValueError(f'{row["photoId"]}: saved Review score has no comparison core')
        center = nz(np.sum(refs, axis=0))
        if not np.linalg.norm(center):
            raise ValueError(f'{row["photoId"]}: saved Review comparison core is zero')
        score = float(np.clip(vectors[row["nativeSha256"]] @ center, -1., 1.))
        difference = abs(score - row["score"])
        if not np.isfinite(difference) or difference > 1e-8:
            raise ValueError(f'{row["photoId"]}: cached measurement does not reproduce saved Review score')
        differences.append(difference)
    if metadata.content_sha256(cache_path) != cache_hash:
        raise ValueError("red measurement cache changed during verification")
    return {
        "cacheSHA256": cache_hash, "modelIds": sorted(model_ids),
        "scoreCount": len(differences), "maxScoreDifference": max(differences, default=0.),
        "scoreTolerance": 1e-8, "rivalInventoryVerified": False,
    }


def measure_unscored_release_candidates(api, root, cache_path, candidates, settings):
    """Measure unscored candidates without changing the saved cache or reference population."""
    from . import normal_transaction

    root = pathlib.Path(root).resolve()
    cache_path = pathlib.Path(cache_path).absolute()
    try:
        cache_path = normal_transaction.safe(root, cache_path.relative_to(root).as_posix())
    except ValueError as exc:
        raise ValueError("unscored measurement cache must be inside the selected library") from exc
    cache_bytes = cache_path.read_bytes()
    cache_hash = hashlib.sha256(cache_bytes).hexdigest()
    cache = json.loads(cache_bytes)
    needed, missing, source_paths, hashes = set(), [], {}, set()
    for row in candidates:
        photo_id, digest, relative = row["photoId"], row["nativeSha256"], row["currentPath"]
        if row.get("score") is not None or photo_id in source_paths or digest in hashes:
            raise ValueError("unscored candidates require unique IDs, native hashes and unavailable scores")
        path = normal_transaction.safe(root, relative)
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != digest:
            raise ValueError(f"{photo_id}: unscored native changed")
        source_paths[photo_id] = path
        hashes.add(digest)
        cached = cache.get("emb", {}).get(hashlib.sha1(payload).hexdigest())
        if cached and cached.get("v") and (cached.get("alignmentEvidence") or {}).get("state") == "persisted":
            needed.add(digest)
        else:
            missing.append(row)
    _, checked_hash, vectors, model_ids, measurements = _red_cache_vectors(root, cache_path, needed)
    if checked_hash != cache_hash or (candidates and len(model_ids) != 1):
        raise ValueError("unscored candidates require one verified saved measurement model")
    mean = np.asarray(cache["centeringMean"], dtype=float)
    if missing:
        domains = api.domains
        domain_token = domains.CURRENT.set("general")
        read_token = domains.READ_ONLY.set(True)
        try:
            embedder = api.Embedder()
            embedder.load()
            if embedder.model_id not in model_ids:
                raise ValueError("local face models differ from the saved unscored measurement model")
            for row in missing:
                photo_id, digest = row["photoId"], row["nativeSha256"]
                data = embedder(source_paths[photo_id])
                evidence = (data or {}).get("alignmentEvidence") or {}
                raw = np.asarray((data or {}).get("v"), dtype=float)
                if (evidence.get("state") != "read-only-not-persisted"
                        or evidence.get("sourceSha256") != digest
                        or evidence.get("modelId") != embedder.model_id
                        or raw.shape != mean.shape or not np.isfinite(raw).all()):
                    raise ValueError(f"{photo_id}: local unscored measurement is unavailable or unbound")
                vector = nz(raw - mean)
                if not np.linalg.norm(vector):
                    raise ValueError(f"{photo_id}: local unscored centered vector is zero")
                measurements[digest], vectors[digest] = data, vector
            import cv2
            if embedder._model_identity(cv2)[1] != embedder.model_id:
                raise ValueError("local face models changed during unscored measurement")
        finally:
            domains.READ_ONLY.reset(read_token)
            domains.CURRENT.reset(domain_token)
    result = []
    for row in candidates:
        photo_id, digest = row["photoId"], row["nativeSha256"]
        if metadata.content_sha256(source_paths[photo_id]) != digest:
            raise ValueError(f"{photo_id}: unscored native changed during measurement")
        result.append({
            "photoId": photo_id, "sha256": digest, "vector": vectors[digest],
            "measurement": measurements[digest],
            "qualityEligible": _red_measurement_quality(measurements[digest], settings, photo_id),
        })
    if cache_path.read_bytes() != cache_bytes:
        raise ValueError("saved measurement cache changed during unscored measurement")
    return {
        "candidates": result, "cacheSHA256": cache_hash, "modelIds": sorted(model_ids),
        "remeasuredCount": len(missing), "measurementsPersisted": False,
    }


def red_refresh_score_census(rows, red_ids, vectors, bands):
    """Compare saved own scores with scores after retiring red Review-core votes."""
    validate_score_bands(bands)
    by_id = {}
    cores = {}
    for row in rows:
        photo_id = row["photoId"]
        if not photo_id or photo_id in by_id:
            raise ValueError("red refresh census requires unique photo IDs")
        by_id[photo_id] = row
        if row.get("coreMember") is True:
            cores.setdefault(row["owner"], []).append(row)
    retired = set(red_ids)
    if not retired or not retired.issubset(by_id):
        raise ValueError("red refresh census is missing retiring photos")
    for photo_id in retired:
        if score_band(by_id[photo_id].get("score"), {"scoreBands": bands}) != "red":
            raise ValueError(f"{photo_id}: retiring score is not red")
    retired_hashes = {by_id[photo_id]["sha256"] for photo_id in retired}
    affected = {
        owner for owner, members in cores.items()
        if any(member["photoId"] in retired or member["sha256"] in retired_hashes for member in members)
    }
    needed = {row["sha256"] for row in rows if row["owner"] in affected
              and (row.get("score") is not None or row.get("coreMember") is True)}
    dimensions = set()
    for digest in needed:
        if digest not in vectors:
            raise ValueError(f"red refresh census is missing vector: {digest}")
        vector = np.asarray(vectors[digest], dtype=float)
        if vector.ndim != 1 or not vector.size or not np.isfinite(vector).all() or not np.isclose(
                np.linalg.norm(vector), 1.):
            raise ValueError(f"red refresh census has invalid vector: {digest}")
        dimensions.add(vector.size)
    if len(dimensions) > 1:
        raise ValueError("red refresh census vector dimensions differ")
    new_red, unavailable = [], []
    checked = 0
    for row in rows:
        owner = row["owner"]
        if owner not in affected or row["photoId"] in retired:
            continue
        score = row.get("score")
        if score is None:
            unavailable.append({"photoId": row["photoId"], "reason": "saved score unavailable"})
            continue
        if type(score) not in (int, float) or not np.isfinite(score):
            raise ValueError(f'{row["photoId"]}: invalid saved Review score')
        core = cores.get(owner, [])
        if (type(row.get("coreMember")) is not bool or type(row.get("coreSize")) is not int
                or row["coreSize"] != len(core)
                or (row["photoId"] in {member["photoId"] for member in core}) != row["coreMember"]):
            raise ValueError(f'{row["photoId"]}: inconsistent saved Review core')
        own = vectors[row["sha256"]]
        saved = [vectors[member["sha256"]] for member in core
                 if not row["coreMember"] or member["photoId"] != row["photoId"]]
        if not saved:
            raise ValueError(f'{row["photoId"]}: saved Review score has no comparison core')
        center = nz(np.sum(saved, axis=0))
        actual = float(np.clip(own @ center, -1., 1.))
        if not np.linalg.norm(center) or abs(actual - score) > 1e-8:
            raise ValueError(f'{row["photoId"]}: saved Review score is not reproducible')
        if score_band(score, {"scoreBands": bands}) == "red":
            raise ValueError(f'{row["photoId"]}: saved red is missing from the retiring set')
        remaining = [vectors[member["sha256"]] for member in core
                     if member["photoId"] not in retired and member["sha256"] not in retired_hashes
                     and (not row["coreMember"] or member["photoId"] != row["photoId"])]
        if not remaining:
            unavailable.append({"photoId": row["photoId"], "reason": "no comparison core after retirement"})
            continue
        center = nz(np.sum(remaining, axis=0))
        if not np.linalg.norm(center):
            unavailable.append({"photoId": row["photoId"], "reason": "zero comparison core after retirement"})
            continue
        refreshed = float(np.clip(own @ center, -1., 1.))
        checked += 1
        if score_band(refreshed, {"scoreBands": bands}) == "red":
            new_red.append({"photoId": row["photoId"], "owner": owner,
                            "savedScore": score, "refreshedScore": refreshed})
    return {"affectedOwners": sorted(affected), "checkedCount": checked,
            "newlyRed": new_red, "unavailable": unavailable, "planningOnly": True}


def rebuilt_red_review_census(rows, red_ids, vectors, policy, *, destinations=None):
    """Rebuild provisional Review cores after red Gallery members move to Review."""
    from .audit import audit_person

    validate_score_bands(policy["scoreBands"])
    by_id = {}
    for row in rows:
        photo_id = row["photoId"]
        if not photo_id or photo_id in by_id:
            raise ValueError("rebuilt Review census requires unique photo IDs")
        if (row["bucket"] not in ("gallery", "review") or row["usable"] is not True
                or (row["bucket"] == "gallery" and (
                    row["identityAnchor"] or row["membershipExcluded"] or row["protected"]
                    or row["state"] in ("Stale metadata", "Ambiguous ID")
                ))):
            raise ValueError(f"{photo_id}: unsupported Review core eligibility")
        vector = np.asarray(vectors.get(row["sha256"]), dtype=float)
        if (vector.ndim != 1 or not vector.size or not np.isfinite(vector).all()
                or not np.isclose(np.linalg.norm(vector), 1.)):
            raise ValueError(f"{photo_id}: invalid Review census vector")
        by_id[photo_id] = row
    retired = set(red_ids)
    if not retired or not retired.issubset(by_id):
        raise ValueError("rebuilt Review census is missing retiring photos")
    for photo_id in retired:
        row = by_id[photo_id]
        if (row["bucket"] != "gallery"
                or score_band(row["score"], policy) != "red"):
            raise ValueError(f"{photo_id}: retirement requires a red Gallery score")
    owners = {by_id[photo_id]["owner"] for photo_id in retired}
    if destinations is not None:
        if set(destinations) != retired:
            raise ValueError("rebuilt Review census destinations must cover every retiring photo")
        for photo_id, owner in destinations.items():
            if (not isinstance(owner, str) or not owner
                    or owner == by_id[photo_id]["owner"]
                    or (owner != "Various" and (
                        len(owner.split("/")) != 2 or not owner.split("/")[1]
                        or owner.split("/")[0] not in policy["categoryPolicies"]
                    ))):
                raise ValueError(f"{photo_id}: invalid Review destination")
            if owner != "Various":
                owners.add(owner)
    if {row["owner"] for row in rows} != owners:
        raise ValueError("rebuilt Review census contains an unrelated owner")
    new_red, unavailable, changes, moved = [], [], [], []
    checked = 0

    def compare(saved, actual, label):
        if saved is None or actual is None:
            if saved is not None or actual is not None:
                raise ValueError(f"{label}: saved Review score is not reproducible")
        elif (type(saved) not in (int, float) or not np.isfinite(saved)
              or not np.isfinite(actual) or abs(float(saved) - float(actual)) > 1e-8):
            raise ValueError(f"{label}: saved Review score is not reproducible")

    for owner in sorted(owners):
        category = owner.split("/", 1)[0]
        if category not in policy["categoryPolicies"]:
            raise ValueError(f"{owner}: unsupported Review category")
        rules = policy["categoryPolicies"][category]
        gallery = sorted(
            (row for row in rows if row["owner"] == owner and row["bucket"] == "gallery"),
            key=lambda row: row["name"].lower() if "name" in row else row["photoId"].lower(),
        )
        reviews = [row for row in rows if row["owner"] == owner and row["bucket"] == "review"]

        def audit(items):
            return audit_person(
                [vectors[row["sha256"]] for row in items], [row["photoId"] for row in items],
                minimum_core=rules.get("minimumUsablePhotosForOutlierActions", 3),
                core_minimum=rules.get("identityCoreMinimumSimilarity", .3),
                seed_floor=rules.get("identityCoreMinimumSimilarity", .3),
            )

        before = audit(gallery)
        core = set(before["core_indices"])
        for index, row in enumerate(gallery):
            if (row["coreMode"] != before["mode"] or row["coreSize"] != len(core)
                    or row["coreMember"] is not (index in core)):
                raise ValueError(f'{row["photoId"]}: saved Review core is not reproducible')
            compare(row["score"], before["scores"][index], row["photoId"])
        for row in reviews:
            actual = None if before["core_vector"] is None else float(
                vectors[row["sha256"]] @ before["core_vector"]
            )
            if (row["coreMode"] != before["mode"] or row["coreSize"] != len(core)
                    or row["coreMember"] is not False):
                raise ValueError(f'{row["photoId"]}: saved Review core is not reproducible')
            compare(row["score"], actual, row["photoId"])
        remaining = [row for row in gallery if row["photoId"] not in retired]
        after = audit(remaining)
        changes.append({
            "owner": owner,
            "beforeCore": [gallery[index]["photoId"] for index in before["core_indices"]],
            "afterCore": [remaining[index]["photoId"] for index in after["core_indices"]],
        })
        if destinations is not None:
            for photo_id in sorted(retired):
                if destinations[photo_id] != owner:
                    continue
                score = (None if after["core_vector"] is None else
                         float(vectors[by_id[photo_id]["sha256"]] @ after["core_vector"]))
                moved.append({
                    "photoId": photo_id, "owner": owner, "score": score,
                    "band": score_band(score, policy) if score is not None else None,
                    **({"reason": "destination comparison core unavailable"} if score is None else {}),
                })
        for index, row in enumerate(remaining + reviews):
            previous = row["score"]
            refreshed = (after["scores"][index] if index < len(remaining) else
                         None if after["core_vector"] is None else
                         float(vectors[row["sha256"]] @ after["core_vector"]))
            if previous is None or refreshed is None:
                unavailable.append({"photoId": row["photoId"], "owner": owner,
                                    "reason": "saved or rebuilt score unavailable"})
                continue
            if score_band(previous, policy) == "red":
                raise ValueError(f'{row["photoId"]}: saved red is missing from the retiring set')
            checked += 1
            if score_band(refreshed, policy) == "red":
                new_red.append({"photoId": row["photoId"], "owner": owner,
                                "savedScore": previous, "refreshedScore": refreshed})
    result = {"affectedOwners": sorted(owners), "checkedCount": checked, "newlyRed": new_red,
              "unavailable": unavailable, "coreChanges": changes, "planningOnly": True}
    if destinations is not None:
        moved.extend({
            "photoId": photo_id, "owner": "Various", "score": None, "band": None,
            "reason": "unassigned Review has no identity score",
        } for photo_id in sorted(retired) if destinations[photo_id] == "Various")
        result["movedScores"] = sorted(moved, key=lambda row: row["photoId"])
    return result


def verified_red_refresh_census(root, receipt, cache_path, snapshot, expected_cache_hash):
    """Recheck saved Review scores under hypothetical retirement, not a rebuilt routing core."""
    from . import normal_recap, normal_transaction

    root = pathlib.Path(root).resolve()
    data = normal_recap.collect(receipt)
    if data["snapshotDiagnostics"] or data["snapshotIdUnavailable"]:
        raise ValueError("red refresh census requires complete identifiable saved Review records")
    for path, digest in data["inputs"].items():
        if snapshot["inputBindings"].get(path) != digest:
            raise ValueError(f"red refresh census input differs from checked snapshot: {path}")
    rows = []
    for item in data["auditRecords"]:
        record, source = item["record"], item["row"]
        context = record.get("scoreContext") or {}
        rows.append({
            "photoId": source["photoId"], "owner": source["newPerson"],
            "path": source["destination"], "sha256": record["contentSha256"],
            "score": item["score"], "coreMember": context.get("coreMember"),
            "coreSize": context.get("coreSize"),
        })
    by_id = {row["photoId"]: row for row in rows}
    for saved in snapshot["snapshotCandidates"]:
        row = by_id.get(saved["photoId"])
        if (row is None or row["owner"] != saved["owner"] or row["path"] != saved["currentPath"]
                or row["sha256"] != saved["nativeSha256"] or row["score"] != saved["score"]):
            raise ValueError(f'{saved["photoId"]}: refresh census differs from saved red evidence')
    retired_ids = {row["photoId"] for row in snapshot["snapshotCandidates"]}
    retired_hashes = {row["nativeSha256"] for row in snapshot["snapshotCandidates"]}
    affected = {
        row["owner"] for row in rows if row["coreMember"] is True
        and (row["photoId"] in retired_ids or row["sha256"] in retired_hashes)
    }
    bound_rows = [row for row in rows if row["owner"] in affected
                  and (row["score"] is not None or row["coreMember"] is True)]
    for row in bound_rows:
        if metadata.content_sha256(normal_transaction.safe(root, row["path"])) != row["sha256"]:
            raise ValueError(f'{row["photoId"]}: refresh census native changed')
    _, cache_hash, vectors, _, _ = _red_cache_vectors(root, cache_path, {row["sha256"] for row in bound_rows})
    if cache_hash != expected_cache_hash:
        raise ValueError("red refresh census cache differs from checked inventory")
    result = red_refresh_score_census(rows, retired_ids, vectors, snapshot["snapshotBands"])
    for row in bound_rows:
        if metadata.content_sha256(normal_transaction.safe(root, row["path"])) != row["sha256"]:
            raise ValueError(f'{row["photoId"]}: refresh census native changed during scoring')
    for path, digest in data["inputs"].items():
        if metadata.content_sha256(pathlib.Path(path)) != digest:
            raise ValueError(f"red refresh census input changed: {path}")
    if metadata.content_sha256(cache_path) != cache_hash:
        raise ValueError("red refresh census cache changed")
    result["referenceBasis"] = "saved Review core only; not a post-routing refreshed core"
    return result


def verified_rebuilt_red_review_census(root, receipt, cache_path, cfg, policy, snapshot, inventory, routing, *,
                                      include_destinations=False):
    """Rebuild affected Review cores for an evidence-bound all-Review hypothetical."""
    import originals
    from . import normal_recap, normal_transaction
    from .audit import membership_excluded
    from .policy import effective_settings

    root = pathlib.Path(root).resolve()
    if routing["assignments"] or any(
        row.get("releaseBlocked") or not isinstance(row.get("reviewDestination"), str)
        or not row["reviewDestination"].endswith("/review") for row in routing["held"]
    ):
        raise ValueError("rebuilt Review census supports only complete hypothetical Review holds")
    saved = snapshot["snapshotCandidates"]
    retired = {row["photoId"] for row in saved}
    if (len(routing["held"]) != len(retired)
            or {row["photoId"] for row in routing["held"]} != retired):
        raise ValueError("rebuilt Review census routing does not conserve red candidates")
    data = normal_recap.collect(receipt)
    if data["snapshotDiagnostics"] or data["snapshotIdUnavailable"]:
        raise ValueError("rebuilt Review census requires complete identifiable saved Review records")
    for path, digest in data["inputs"].items():
        if snapshot["inputBindings"].get(path) != digest:
            raise ValueError(f"rebuilt Review census input differs from snapshot: {path}")
    review_path = pathlib.Path(data["libraryRoot"]) / "people_gallery_review.html"
    payload = review_path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != data["inputs"].get(str(review_path)):
        raise ValueError("rebuilt Review census snapshot changed")
    page = payload.decode("utf-8")
    records = normal_recap._script(page, "review-data")
    saved_policy = normal_recap._script(page, "likeness-policy-data")
    if not isinstance(records, list) or not isinstance(saved_policy, dict):
        raise ValueError("rebuilt Review census requires saved records and policy")
    owners = {row["owner"] for row in saved}
    destinations = None
    if include_destinations:
        destinations = {
            row["photoId"]: row["reviewDestination"].rsplit("/", 1)[0] for row in routing["held"]
        }
        owners.update(owner for owner in destinations.values() if owner != "Various")
    for category in {owner.split("/", 1)[0] for owner in owners}:
        if saved_policy.get("categoryPolicies", {}).get(category) != policy["categoryPolicies"].get(category):
            raise ValueError(f"{category}: saved Review core policy differs")
    audit_items = [item for item in data["auditRecords"] if item["row"]["newPerson"] in owners]
    snapshot_paths = {
        (pathlib.PurePosixPath(record["folder"]) / record["bucket"].lower() / record["name"]).as_posix()
        for record in records if record["folder"] in owners
    }
    if (len(snapshot_paths) != sum(record["folder"] in owners for record in records)
            or snapshot_paths != {item["row"]["destination"] for item in audit_items}):
        raise ValueError("rebuilt Review census does not cover every affected snapshot photo")
    all_ids = [record["photoId"] for record in records]
    if any(not photo_id for photo_id in all_ids) or len(all_ids) != len(set(all_ids)):
        raise ValueError("rebuilt Review census requires globally unambiguous snapshot IDs")
    saved_by_id = {row["photoId"]: row for row in saved}
    retired_hashes = {row["nativeSha256"] for row in saved}
    retired_paths = {row["currentPath"] for row in saved}
    for path, digest in inventory["nativeBindings"].items():
        if digest in retired_hashes and path not in retired_paths:
            raise ValueError(f"{path}: retired red has a surviving Gallery content alias")
    for record in records:
        photo_id = record["photoId"]
        if photo_id in retired:
            row = saved_by_id[photo_id]
            relative = (pathlib.PurePosixPath(record["folder"]) / record["bucket"].lower()
                        / record["name"]).as_posix()
            if (record["contentSha256"] != row["nativeSha256"]
                    or record["folder"] != row["owner"] or relative != row["currentPath"]
                    or record["bucket"].lower() != row["bucket"] or record["score"] != row["score"]):
                raise ValueError(f"{photo_id}: rebuilt Review red differs from saved evidence")
        elif record["bucket"] == "Gallery" and record["contentSha256"] in retired_hashes:
            raise ValueError(f"{photo_id}: retired red has a surviving Gallery content alias")
    catalog_path = normal_transaction.safe(root, ".likeness-library.json")
    catalog = metadata.load_catalog(catalog_path)
    if metadata.content_sha256(catalog_path) != inventory["catalogSHA256"]:
        raise ValueError("rebuilt Review census catalogue differs from checked inventory")
    settings = effective_settings(cfg, policy)
    rows = []
    for item in audit_items:
        record, source = item["record"], item["row"]
        photo_id, owner, relative = source["photoId"], source["newPerson"], source["destination"]
        context = record.get("scoreContext") or {}
        entry = catalog["photos"].get(photo_id, {})
        if entry and entry["contentSha256"] != record["contentSha256"]:
            raise ValueError(f"{photo_id}: rebuilt Review census metadata is stale")
        if context.get("minFace") != settings["minFace"]:
            raise ValueError(f"{photo_id}: rebuilt Review face gate differs")
        rows.append({
            "photoId": photo_id, "owner": owner, "bucket": source["newBucket"], "name": record["name"],
            "path": relative, "sha256": record["contentSha256"], "score": item["score"],
            "coreMember": context.get("coreMember"), "coreSize": context.get("coreSize"),
            "coreMode": context.get("coreMode"), "usable": context.get("usable"),
            "identityAnchor": record["identityAnchor"], "membershipExcluded": record["membershipExcluded"],
            "protected": bool(entry.get("protected")), "state": record["state"],
        })
    for owner in owners:
        gallery = [row for row in rows if row["owner"] == owner and row["bucket"] == "gallery"]
        people = [person for person in catalog["people"].values() if person["folder"] == owner]
        if len(people) > 1 or (people and people[0]["identityAnchors"]):
            raise ValueError(f"{owner}: rebuilt Review census does not support identity anchors")
        if not people:
            patterns = next((values for name, values in cfg.get("likeness", {}).get("anchors", {}).items()
                             if name.casefold() == owner.split("/")[-1].casefold()), ())
            if any(pattern.casefold() in row["name"].casefold() for row in gallery for pattern in patterns):
                raise ValueError(f"{owner}: rebuilt Review census does not support configured anchors")
        excluded = membership_excluded(catalog, [row["photoId"] for row in gallery])
        if any(row["membershipExcluded"] != (row["photoId"] in excluded) for row in gallery):
            raise ValueError(f"{owner}: rebuilt Review membership differs from catalogue")

    def check_natives():
        for owner in owners:
            for bucket in ("gallery", "review"):
                directory = normal_transaction.safe(root, f"{owner}/{bucket}")
                actual = {path.relative_to(root).as_posix() for path in originals.images(directory)}
                expected = {row["path"] for row in rows if row["owner"] == owner and row["bucket"] == bucket}
                if actual != expected:
                    raise ValueError(f"{owner}/{bucket}: rebuilt Review inventory changed")
        for row in rows:
            if metadata.content_sha256(normal_transaction.safe(root, row["path"])) != row["sha256"]:
                raise ValueError(f'{row["photoId"]}: rebuilt Review native changed')

    check_natives()
    _, cache_hash, vectors, model_ids, measurements = _red_cache_vectors(
        root, cache_path, {row["sha256"] for row in rows},
    )
    if cache_hash != inventory["cacheSHA256"] or sorted(model_ids) != inventory["modelIds"]:
        raise ValueError("rebuilt Review census cache differs from checked inventory")
    for row in rows:
        pixels = measurements[row["sha256"]].get("px")
        if (type(pixels) not in (int, float) or not np.isfinite(pixels)
                or (pixels >= settings["minFace"]) != row["usable"]):
            raise ValueError(f'{row["photoId"]}: rebuilt Review usability differs from cache')
    result = rebuilt_red_review_census(rows, retired, vectors, policy, destinations=destinations)
    check_natives()
    if (metadata.content_sha256(catalog_path) != inventory["catalogSHA256"]
            or metadata.content_sha256(cache_path) != cache_hash):
        raise ValueError("rebuilt Review census catalogue or cache changed")
    for path, digest in data["inputs"].items():
        if metadata.content_sha256(pathlib.Path(path)) != digest:
            raise ValueError(f"rebuilt Review census input changed: {path}")
    result["referenceBasis"] = "hypothetical Review holds; rebuilt saved-policy affected cores"
    return result


def _red_measurement_quality(measurement, settings, label):
    faces, pixels, secondary = measurement.get("faces"), measurement.get("px", 0), measurement.get("f2", 0.)
    if (type(faces) is not int or faces < 0 or type(pixels) not in (int, float)
            or not np.isfinite(pixels) or pixels < 0 or type(secondary) not in (int, float)
            or not np.isfinite(secondary) or not 0 <= secondary <= 1):
        raise ValueError(f"{label}: invalid cached face-quality evidence")
    return faces == 1 and pixels >= settings["minFace"] and secondary <= settings["multiFace"]


def verify_red_routing_measurements(root, cache_path, candidates, references, reference_paths, settings):
    """Bind the supplied routing vectors to current native bytes and cached evidence."""
    from . import normal_transaction

    root = pathlib.Path(root).resolve()
    needed = {row["sha256"] for row in candidates}
    needed.update(row["sha256"] for rows in references.values() for row in rows)
    cache_path, cache_hash, vectors, model_ids, measurements = _red_cache_vectors(root, cache_path, needed)
    reference_ids = [row["photoId"] for rows in references.values() for row in rows]
    if len(reference_ids) != len(set(reference_ids)) or set(reference_ids) != set(reference_paths):
        raise ValueError("red routing requires exactly one path for each frozen reference")
    sources = {}

    def bind(row, relative, owner, bucket):
        path = normal_transaction.safe(root, relative)
        parts = pathlib.PurePosixPath(relative)
        if (parts.parent.name != bucket or parts.parent.parent.as_posix() != owner
                or metadata.photo_id_from_name(parts.name) != row["photoId"]):
            raise ValueError(f'{row["photoId"]}: routing measurement path differs from its owner or ID')
        digest = row["sha256"]
        if relative in sources and sources[relative] != digest:
            raise ValueError(f"conflicting red routing native hashes: {relative}")
        if metadata.content_sha256(path) != digest:
            raise ValueError(f"red routing native changed: {relative}")
        sources[relative] = digest
        vector = np.asarray(row["vector"], dtype=float)
        if vector.shape != vectors[digest].shape or not np.allclose(vector, vectors[digest], rtol=0., atol=1e-8):
            raise ValueError(f'{row["photoId"]}: routing vector differs from cached measurement')
        quality = _red_measurement_quality(measurements[digest], settings, row["photoId"])
        if row.get("qualityEligible") is not quality:
            raise ValueError(f'{row["photoId"]}: routing quality differs from cached measurement')

    for row in candidates:
        bind(row, row["currentPath"], row["sourceFolder"], row["sourceBucket"].lower())
    for folder, rows in references.items():
        for row in rows:
            bind(row, reference_paths[row["photoId"]], folder, "gallery")
    for relative, digest in sources.items():
        if metadata.content_sha256(normal_transaction.safe(root, relative)) != digest:
            raise ValueError(f"red routing native changed during verification: {relative}")
    if metadata.content_sha256(cache_path) != cache_hash:
        raise ValueError("red measurement cache changed during routing verification")
    return {
        "cacheSHA256": cache_hash, "modelIds": sorted(model_ids), "nativeBindings": sources,
        "rivalInventoryVerified": False, "centeringPopulationVerified": False,
        "currentModelBytesVerified": False,
    }


def verified_red_nonvoting_gallery(receipt, report, root, *, workflow_configuration_path=None):
    """Bind the saved run's unchanged non-voting Gallery dispositions to current bytes."""
    from . import normal_import, normal_recap, normal_transaction

    root = pathlib.Path(root).resolve()
    receipt = pathlib.Path(receipt).absolute()
    manifest = normal_recap.publish(
        receipt, out=report, check=True, bind_red_natives=True, inspect_workflow_selections=True,
        workflow_configuration_path=workflow_configuration_path,
    )
    payload = receipt.read_bytes()
    if hashlib.sha256(payload).hexdigest() != manifest["inputs"].get(str(receipt)):
        raise ValueError("red non-voting receipt changed during verification")
    saved = json.loads(payload)
    if saved.get("status") != "applied" or pathlib.Path(saved["root"]).resolve() != root:
        raise ValueError("red non-voting evidence requires the applied receipt for this library")
    data = normal_recap.collect(receipt)
    rows = {row["source"]: row for row in data["rows"]}
    result = {}
    for source in saved["plan"]["sourceRows"]:
        if source.get("sourceStatus") != "same-content-nonvoting":
            continue
        row = rows[source["source"]]
        if row["newPerson"].split("/", 1)[0] not in normal_import.IDENTITY_ROOTS:
            continue
        if (row["newBucket"] != "gallery" or row["destination"] != source["source"]
                or row["preparedSHA256"] != source["sourceHash"]):
            raise ValueError("non-voting Gallery disposition changed since the saved run")
        path = normal_transaction.safe(root, row["destination"])
        if metadata.content_sha256(path) != row["preparedSHA256"]:
            raise ValueError(f"non-voting Gallery native changed: {row['destination']}")
        result[row["destination"]] = row["preparedSHA256"]
    if hashlib.sha256(receipt.read_bytes()).hexdigest() != manifest["inputs"][str(receipt)]:
        raise ValueError("red non-voting receipt changed during verification")
    return result


def verify_red_centering_population(receipt, report, root, cache_path, cfg, policy, *,
                                    workflow_configuration_path=None):
    """Reconstruct a supported saved preparation population without modifying it."""
    from . import normal_recap
    report_manifest = normal_recap.publish(
        receipt, out=report, check=True, bind_red_natives=True, inspect_workflow_selections=True,
        workflow_configuration_path=workflow_configuration_path,
    )
    return _verify_red_centering_population(receipt, root, cache_path, cfg, policy, report_manifest)


def _verify_red_centering_population(receipt, root, cache_path, cfg, policy, report_manifest):
    from . import clean_preparation, normal_import, normal_transaction
    from .policy import effective_settings

    root = pathlib.Path(root).resolve()
    receipt = pathlib.Path(receipt).absolute()
    receipt_bytes = receipt.read_bytes()
    receipt_hash = hashlib.sha256(receipt_bytes).hexdigest()
    if report_manifest["inputs"].get(str(receipt)) != receipt_hash:
        raise ValueError("red centering receipt changed during verification")
    saved = json.loads(receipt_bytes)
    if saved.get("status") != "applied" or pathlib.Path(saved["root"]).resolve() != root:
        raise ValueError("red centering requires the applied receipt for this library")
    plan = saved["plan"]
    for key, value in (("configurationSHA256", cfg), ("policySHA256", policy)):
        digest = hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if plan["bindings"].get(key) != digest:
            raise ValueError(f"red centering {key} differs from the saved run")
    if saved.get("profile") not in {"lean", "full"}:
        raise ValueError("red centering requires saved FULL/LEAN preparation")
    if plan.get("preparationReuse", {}).get("selectedSourceAliases"):
        raise ValueError("red centering does not yet support reused preparation aliases")
    preparation = pathlib.Path(plan["preparationRoot"]).absolute()
    try:
        relative = preparation.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("red centering preparation must be inside the selected library") from exc
    preparation = normal_transaction.safe(root, relative)
    manifest_path = normal_transaction.safe(root, f"{relative}/manifest.json")
    manifest_bytes = manifest_path.read_bytes()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    if manifest_hash != plan["preparationManifestSHA256"]:
        raise ValueError("red centering preparation manifest changed")
    prepared = json.loads(manifest_bytes)
    prepared_rows = {row["source"]: row for row in prepared["photos"]}
    if len(prepared_rows) != len(prepared["photos"]):
        raise ValueError("red centering preparation contains duplicate sources")
    rows = plan["sourceRows"]
    allowed = {"eligible", "confirmed-no-face-junk", "same-content-nonvoting", "duplicate-archive"}
    if any(row.get("sourceStatus") not in allowed or row.get("retainedManifest") for row in rows):
        raise ValueError("red centering source disposition is not supported")
    active = [row for row in rows if row["sourceStatus"] == "eligible"]
    selected = [row for row in rows if row["sourceStatus"] in {"eligible", "confirmed-no-face-junk"}]
    if (len({row["source"] for row in rows}) != len(rows)
            or {row["source"] for row in selected} != set(prepared_rows)
            or any(prepared_rows[row["source"]]["sourceSha256"] != row["sourceHash"] for row in selected)):
        raise ValueError("red centering preparation does not match the saved active sources")

    cache_path = pathlib.Path(cache_path).absolute()
    try:
        cache_relative = cache_path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("red centering cache must be inside the selected library") from exc
    cache_path = normal_transaction.safe(root, cache_relative)
    cache_bytes = cache_path.read_bytes()
    cache = json.loads(cache_bytes)
    minimum = effective_settings(cfg, policy)["minFace"]
    vectors, needed, selected_hashes = [], set(), {}
    for row in active:
        prepared_row = prepared_rows[row["source"]]
        path = clean_preparation.selected_path(preparation, prepared_row)
        payload = path.read_bytes()
        checksum = hashlib.sha256(payload).hexdigest()
        choice = prepared_row.get("recommendation", {}).get("use", "none")
        expected_checksum = (
            prepared_row["sourceSha256"] if choice in ("original", "none")
            else prepared_row["variants"][choice]["sha256"]
        )
        if checksum != expected_checksum:
            raise ValueError(f"red centering selected preparation changed: {row['source']}")
        selected_hashes[path] = checksum
        measurement = cache["emb"].get(hashlib.sha1(payload).hexdigest())
        if not normal_import._current_measurement(measurement):
            raise ValueError(f"red centering measurement is missing: {row['source']}")
        _red_measurement_quality(measurement, {"minFace": minimum, "multiFace": 1.}, row["source"])
        if measurement.get("v"):
            if (measurement.get("alignmentEvidence") or {}).get("sourceSha256") != checksum:
                raise ValueError(f"red centering measurement is not content-bound: {row['source']}")
            needed.add(checksum)
            if measurement.get("px", 0) >= minimum:
                vectors.append(np.asarray(measurement["v"], dtype=float))
    if not vectors:
        raise ValueError("red centering has no usable saved measurements")
    _, checked_cache_hash, _, model_ids, _ = _red_cache_vectors(root, cache_path, needed)
    if checked_cache_hash != hashlib.sha256(cache_bytes).hexdigest():
        raise ValueError("red centering cache changed during collection")
    actual = np.mean(vectors, axis=0)
    expected = np.asarray(cache["centeringMean"], dtype=float)
    if actual.shape != expected.shape or not np.isfinite(actual).all():
        raise ValueError("red centering population has invalid dimensions")
    difference = float(np.max(np.abs(actual - expected)))
    if difference > 1e-8:
        raise ValueError("saved centering mean differs from the reconstructed population")
    if (hashlib.sha256(receipt.read_bytes()).hexdigest() != receipt_hash
            or hashlib.sha256(manifest_path.read_bytes()).hexdigest() != manifest_hash
            or metadata.content_sha256(cache_path) != checked_cache_hash
            or any(metadata.content_sha256(path) != digest for path, digest in selected_hashes.items())):
        raise ValueError("red centering evidence changed during verification")
    return {
        "activeCount": len(active), "usableCount": len(vectors), "minFace": minimum,
        "maxMeanDifference": difference, "cacheSHA256": checked_cache_hash,
        "preparationManifestSHA256": manifest_hash, "receiptSHA256": receipt_hash,
        "modelIds": sorted(model_ids), "centeringPopulationVerified": True,
    }


def red_workflow_replacement_proposal(root, cache_path, snapshot_candidate, cfg, policy, *, retired_ids):
    """Propose a higher-scoring replacement from caller-verified saved Review evidence."""
    from . import actions, derivatives, normal_transaction
    from .policy import effective_settings

    root = pathlib.Path(root).resolve()
    cfg_hash = hashlib.sha256(
        json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    photo_id = snapshot_candidate["photoId"]
    owner = snapshot_candidate["owner"]
    retired = set(retired_ids)
    if (photo_id not in retired or score_band(snapshot_candidate["score"], policy) != "red"
            or snapshot_candidate["bucket"] != "gallery"
            or owner.split("/", 1)[0] not in CAST or len(owner.split("/")) != 2):
        raise ValueError("workflow replacement requires a retiring red cast Gallery photo")
    core = snapshot_candidate["reviewCore"]
    if retired.intersection(member["photoId"] for member in core):
        raise ValueError("workflow replacement requires a newly scored core after reference retirement")
    candidates = snapshot_candidate["workflowReplacementCandidates"]
    if not candidates or len({row["photoId"] for row in candidates}) != len(candidates):
        raise ValueError("workflow replacement candidates are missing or ambiguous")
    saved = [snapshot_candidate] + [{**row, "reviewCore": core} for row in candidates]
    proof = verify_red_review_measurements(root, cache_path, saved)
    _, checked_cache_hash, _, _, measurements = _red_cache_vectors(
        root, cache_path, {row["nativeSha256"] for row in saved},
    )
    if checked_cache_hash != proof["cacheSHA256"]:
        raise ValueError("workflow replacement cache changed during verification")
    catalog_path = normal_transaction.safe(root, ".likeness-library.json")
    catalog_bytes = catalog_path.read_bytes()
    catalog = metadata.load_catalog(catalog_path)
    settings = effective_settings(cfg, policy)
    photo_index = actions._index_photos(root)
    native_bindings = {}
    for member in core:
        relative = member["path"]
        path = normal_transaction.safe(root, relative)
        if (path.parent.name != "gallery" or path.parent.parent.relative_to(root).as_posix() != owner
                or metadata.photo_id_from_name(path.name) != member["photoId"]
                or metadata.content_sha256(path) != member["sha256"]
                or photo_index.get(member["photoId"]) != [path]):
            raise ValueError(f'{member["photoId"]}: workflow replacement core is changed or ambiguous')
        native_bindings[relative] = member["sha256"]
    eligible = []
    for row in saved:
        relative = row["currentPath"]
        path = normal_transaction.safe(root, relative)
        if (path.parent.name != "gallery" or path.parent.parent.relative_to(root).as_posix() != owner
                or metadata.photo_id_from_name(path.name) != row["photoId"]
                or metadata.content_sha256(path) != row["nativeSha256"]
                or photo_index.get(row["photoId"]) != [path]):
            raise ValueError(f'{row["photoId"]}: workflow replacement native is changed or ambiguous')
        if relative in native_bindings and native_bindings[relative] != row["nativeSha256"]:
            raise ValueError(f'{row["photoId"]}: workflow replacement core and native differ')
        native_bindings[relative] = row["nativeSha256"]
        if row is snapshot_candidate:
            continue
        record = catalog["photos"].get(row["photoId"], {})
        if record and record.get("contentSha256") != row["nativeSha256"]:
            raise ValueError(f'{row["photoId"]}: workflow replacement metadata is stale')
        rejected = rejections.candidate_state(catalog, row["photoId"], row["nativeSha256"])
        if (row["photoId"] not in retired
                and row["nativeSha256"] != snapshot_candidate["nativeSha256"]
                and score_band(row["score"], policy) != "red"
                and row["score"] > snapshot_candidate["score"]
                and _red_measurement_quality(measurements[row["nativeSha256"]], settings, row["photoId"])
                and not rejected.get("rejectionMetadataStale") and not rejected.get("rejectedPersonIds")):
            eligible.append(row)
    if not eligible:
        raise ValueError("no eligible higher-scoring workflow replacement")
    replacement = sorted(eligible, key=lambda row: (-row["score"], row["photoId"], row["currentPath"]))[0]
    if tuple(cfg.get("standardSize") or derivatives.SIZE) != derivatives.SIZE:
        raise ValueError("workflow replacement requires the maintained standard derivative size")
    source = normal_transaction.safe(root, snapshot_candidate["currentPath"])
    replacement_source = normal_transaction.safe(root, replacement["currentPath"])
    derivative_manifest = derivatives.manifest_path(source.parent.parent)
    derivative_manifest = normal_transaction.safe(root, derivative_manifest.relative_to(root).as_posix())
    derivative_manifest_hash = metadata.content_sha256(derivative_manifest)
    before, before_record = derivatives.verified(source, "padded")
    after, after_record = derivatives.verified(replacement_source, "padded")
    before = normal_transaction.safe(root, before.relative_to(root).as_posix())
    after = normal_transaction.safe(root, after.relative_to(root).as_posix())
    bindings = actions.workflow_replacement_bindings(cfg, photo_id, owner.split("/", 1)[1], after.name)
    if any(binding["before"].casefold() != before.name.casefold() for binding in bindings):
        raise ValueError("configured workflow selection differs from the verified old derivative")
    for relative, digest in native_bindings.items():
        if metadata.content_sha256(normal_transaction.safe(root, relative)) != digest:
            raise ValueError(f"workflow replacement native changed during verification: {relative}")
    final_index = actions._index_photos(root)
    if any(final_index.get(metadata.photo_id_from_name(pathlib.PurePosixPath(relative).name))
           != [normal_transaction.safe(root, relative)] for relative in native_bindings):
        raise ValueError("workflow replacement photo inventory changed during verification")
    if (metadata.content_sha256(cache_path) != checked_cache_hash
            or catalog_path.read_bytes() != catalog_bytes
            or metadata.content_sha256(derivative_manifest) != derivative_manifest_hash
            or hashlib.sha256(json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != cfg_hash
            or metadata.content_sha256(before) != before_record["sha256"]
            or metadata.content_sha256(after) != after_record["sha256"]):
        raise ValueError("workflow replacement evidence changed during verification")
    return {
        "photoId": photo_id, "replacementPhotoId": replacement["photoId"],
        "replacementPath": replacement["currentPath"], "replacementScore": replacement["score"],
        "beforeDerivative": str(before), "beforeDerivativeSHA256": before_record["sha256"],
        "afterDerivative": str(after), "afterDerivativeSHA256": after_record["sha256"],
        "derivativeManifest": str(derivative_manifest), "derivativeManifestSHA256": derivative_manifest_hash,
        "configurationSHA256": cfg_hash,
        "selectionChanges": bindings, "reviewMeasurementProof": proof,
        "planningOnly": True, "consumerCoverageVerified": False,
    }


def _release_bands(bands):
    if (not isinstance(bands, (list, tuple)) or not bands
            or any(band not in ("red", "orange") for band in bands)
            or len(set(bands)) != len(bands)):
        raise ValueError("release bands must uniquely select red and/or orange")
    return tuple(sorted(bands))


def current_release_candidates(records, policy, *, release_bands=("red",), include_unscored=False):
    """Select named Review records and their exact saved comparison cores."""
    selected_bands = _release_bands(release_bands)
    validate_score_bands(policy["scoreBands"])
    if not isinstance(records, list):
        raise ValueError("current Review records must be an array")
    by_id, by_path, cores, all_natives = {}, {}, {}, {}
    categories = {"Sisters", "Angels", "Models", "Prospects", "Potentials"}
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("current Review records must be objects")
        photo_id = row.get("photoId")
        owner, bucket, name = row.get("folder"), row.get("bucket"), row.get("name")
        digest = row.get("contentSha256")
        if (not isinstance(owner, str) or not isinstance(bucket, str) or not isinstance(name, str)
                or not isinstance(photo_id, str) or not photo_id
                or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or bucket not in ("Gallery", "Review")):
            raise ValueError("current Review record lacks a stable ID, path or native hash")
        relative = f"{owner}/{bucket.lower()}/{name}"
        parts = pathlib.PurePosixPath(relative).parts
        if (relative.startswith("/") or "\\" in relative or ":" in relative
                or any(part in ("", ".", "..") for part in relative.split("/"))
                or metadata.photo_id_from_name(name) != photo_id
                or row.get("generationSource") != relative):
            raise ValueError(f"{photo_id}: invalid current Review path")
        if photo_id in by_id or relative.casefold() in by_path:
            raise ValueError("current Review has ambiguous IDs or paths")
        by_id[photo_id] = row
        by_path[relative.casefold()] = photo_id
        all_natives[relative] = digest
        context = row.get("scoreContext") or {}
        if context.get("coreMember") is True:
            if bucket != "Gallery":
                raise ValueError(f"{photo_id}: Review photo cannot vote in a Gallery core")
            cores.setdefault(owner, []).append({
                "photoId": photo_id, "path": relative, "sha256": digest,
            })
        if parts[0] in categories and len(parts) != 4:
            raise ValueError(f"{photo_id}: invalid people identity path")

    candidates, unavailable = [], []
    for photo_id, row in by_id.items():
        owner = row["folder"]
        if owner.split("/", 1)[0] not in categories:
            continue
        score = row.get("score")
        if score is None:
            unavailable.append(photo_id)
            if not include_unscored:
                continue
        elif score_band(score, policy) not in selected_bands:
            continue
        context = row.get("scoreContext") or {}
        core = sorted(cores.get(owner, []), key=lambda member: member["path"])
        if (type(context.get("coreMember")) is not bool
                or type(context.get("coreSize")) is not int
                or context["coreSize"] != len(core)
                or (photo_id in {member["photoId"] for member in core}) != context["coreMember"]):
            raise ValueError(f"{photo_id}: current Review core is incomplete or inconsistent")
        candidates.append({
            "photoId": photo_id, "owner": owner, "bucket": row["bucket"].lower(),
            "currentPath": f'{owner}/{row["bucket"].lower()}/{row["name"]}',
            "nativeSha256": row["contentSha256"], "score": score,
            "scoreContext": context, "comparison": row.get("comparison"), "reviewCore": core,
            "identityProtected": row.get("identityProtected"), "identityAnchor": row.get("identityAnchor"),
            "photoProtectionInfo": row.get("photoProtectionInfo"),
            "workflowSelected": row.get("workflowSelected"),
        })
    return {
        "snapshotCandidates": sorted(candidates, key=lambda row: row["currentPath"]),
        "unavailableIds": sorted(unavailable), "releaseBands": list(selected_bands),
        "allNativeBindings": all_natives,
    }


def verified_current_release_snapshot(root, report_dir, cache_path, cfg, policy, *,
                                      release_bands=("red",), include_unscored=False):
    """Bind the current reports-only Review and reproduce each selected score."""
    from tools.art import gallery_maintenance
    from . import normal_recap, normal_transaction

    root = pathlib.Path(root).resolve()
    report_dir = pathlib.Path(report_dir).absolute()
    cache_path = pathlib.Path(cache_path).absolute()
    for path in (report_dir, cache_path):
        normal_recap._under(root, path)
    review = normal_recap._under(root, report_dir / "people_gallery_review.html")
    state = normal_recap._under(root, report_dir / ".gallery-maintenance-report-state.json")
    state_bytes, review_bytes = state.read_bytes(), review.read_bytes()
    library = gallery_maintenance.folders(cfg, root)
    if gallery_maintenance.reports_pending(root, library, cache_path, None, report_dir):
        raise ValueError("current Review reports or source bindings are stale")
    page = review_bytes.decode("utf-8")
    if normal_recap._script(page, "likeness-policy-data") != policy:
        raise ValueError("current Review policy differs from release policy")
    result = current_release_candidates(
        normal_recap._script(page, "review-data"), policy,
        release_bands=release_bands, include_unscored=include_unscored,
    )
    bindings = {}
    for row in result["snapshotCandidates"]:
        members = [{"path": row["currentPath"], "sha256": row["nativeSha256"]}, *row["reviewCore"]]
        for member in members:
            if member["path"] in bindings and bindings[member["path"]] != member["sha256"]:
                raise ValueError(f"current Review native has conflicting hashes: {member['path']}")
            if member["path"] in bindings:
                continue
            path = normal_transaction.safe(root, member["path"])
            if metadata.content_sha256(path) != member["sha256"]:
                raise ValueError(f"current Review native differs: {member['path']}")
            bindings[member["path"]] = member["sha256"]
    proof = verify_red_review_measurements(
        root, cache_path, [row for row in result["snapshotCandidates"] if row["score"] is not None],
    )
    if (state.read_bytes() != state_bytes or review.read_bytes() != review_bytes
            or gallery_maintenance.folders(cfg, root) != library
            or gallery_maintenance.reports_pending(root, library, cache_path, None, report_dir)):
        raise ValueError("current Review evidence changed during verification")
    result.update({
        "reviewSHA256": hashlib.sha256(review_bytes).hexdigest(),
        "reportStateSHA256": hashlib.sha256(state_bytes).hexdigest(),
        "nativeBindings": bindings, "reviewMeasurementProof": proof,
    })
    return result


def _retire_source_membership(updated, photo_id, owner, checksum, retired_anchors, retired_groups):
    record = updated["photos"].get(photo_id)
    if record and record["contentSha256"] != checksum:
        raise ValueError(f"{photo_id}: release catalogue content is stale")
    for person_id, person in updated["people"].items():
        if photo_id not in person["identityAnchors"]:
            continue
        if person["folder"] != owner:
            raise ValueError(f"{photo_id}: anchor belongs to another identity")
        person["identityAnchors"].remove(photo_id)
        retired_anchors.append({"photoId": photo_id, "personId": person_id})
    membership = (record or {}).get("membership", {})
    parent_id = membership.get("personId")
    if parent_id is not None and updated["people"][parent_id]["folder"] != owner:
        raise ValueError(f"{photo_id}: membership belongs to another identity")
    for group_id, group in updated.get("photoGroups", {}).items():
        if photo_id not in group["memberPhotoIds"] and photo_id not in group["referencePhotoIds"]:
            continue
        if membership.get("groupId") != group_id:
            raise ValueError(f"{photo_id}: conflicting group membership")
        group["memberPhotoIds"] = [pid for pid in group["memberPhotoIds"] if pid != photo_id]
        group["referencePhotoIds"] = [pid for pid in group["referencePhotoIds"] if pid != photo_id]
        retired_groups.append({"photoId": photo_id, "groupId": group_id})
    if record is None:
        record = {"contentSha256": checksum, "protected": False}
        updated["photos"][photo_id] = record
    record.pop("membership", None)


def retire_released_catalog(catalog, bindings, standard_names=None):
    """Prepare source membership retirement for an independently verified cohort.

    ``standard_names`` optionally maps photo IDs to inventory-verified standard
    filenames for sources whose descriptive filename does not encode the ID.
    """
    metadata.validate_catalog(catalog)
    standard_names = standard_names or {}
    updated = json.loads(json.dumps(catalog))
    seen, retired_anchors, retired_groups = set(), [], []
    for row in bindings:
        photo_id, source, checksum = row["photoId"], row["currentPath"], row["sha256"]
        path = pathlib.PurePosixPath(source)
        standard = standard_names.get(photo_id)
        if (photo_id in seen or not isinstance(source, str) or "\\" in source or ":" in source
                or path.is_absolute() or any(part in ("", ".", "..") for part in source.split("/"))
                or path.parts[0] not in {"Sisters", "Angels", "Models", "Prospects", "Potentials", "Various"}
                or len(path.parts) not in (3, 4) or path.parent.name not in ("gallery", "review")
                or (path.parts[0] == "Various") != (len(path.parts) == 3)
                or (metadata.photo_id_from_name(path.name) != photo_id
                    and (not isinstance(standard, str) or metadata.photo_id_from_name(standard) != photo_id))
                or not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum)):
            raise ValueError(f"{photo_id}: invalid released source binding")
        seen.add(photo_id)
        _retire_source_membership(updated, photo_id, path.parent.parent.as_posix(), checksum,
                                  retired_anchors, retired_groups)
    metadata.validate_catalog(updated)
    return {"catalog": updated, "retiredAnchors": retired_anchors, "retiredGroups": retired_groups}


def red_release_hold_catalog(catalog, moves, snapshot_candidates, policy, *,
                             release_bands=("red",), include_unscored=False):
    """Prepare catalogue changes for checked red moves into the unassigned Review hold."""
    metadata.validate_catalog(catalog)
    selected_bands = _release_bands(release_bands)
    evidence = {row["photoId"]: row for row in snapshot_candidates}
    if len(evidence) != len(snapshot_candidates):
        raise ValueError("red hold snapshot has ambiguous photo IDs")
    updated = json.loads(json.dumps(catalog))
    seen, retired_anchors, retired_groups = set(), [], []
    for move in moves:
        photo_id = move["photoId"]
        row = evidence.get(photo_id)
        source = pathlib.PurePosixPath(move["source"])
        destination = pathlib.PurePosixPath(move["destination"])
        score_selected = (
            row is not None and (
                (row.get("score") is None and include_unscored)
                or (row.get("score") is not None and score_band(row["score"], policy) in selected_bands)
            )
        )
        if (row is None or photo_id in seen or not score_selected
                or source.is_absolute() or any(part in ("", ".", "..") for part in move["source"].split("/"))
                or "\\" in move["source"] or ":" in move["source"]
                or len(source.parts) != 4 or source.parts[0] not in
                {"Sisters", "Angels", "Models", "Prospects", "Potentials"}
                or row.get("currentPath") != move["source"] or row.get("nativeSha256") != move["sha256"]
                or source.parent.name != row.get("bucket")
                or source.parent.parent.as_posix() != row.get("owner")
                or metadata.photo_id_from_name(source.name) != photo_id
                or destination != pathlib.PurePosixPath("Various", "review", source.name)):
            raise ValueError(f"{photo_id}: unassigned hold differs from checked red evidence")
        seen.add(photo_id)
        _retire_source_membership(updated, photo_id, row["owner"], move["sha256"],
                                  retired_anchors, retired_groups)
    metadata.validate_catalog(updated)
    return {"catalog": updated, "retiredAnchors": retired_anchors, "retiredGroups": retired_groups}


def red_release_routed_catalog(catalog, moves, snapshot_candidates, policy, routing_plan):
    """Stage catalogue changes bound to every unblocked red routing decision."""
    version = routing_plan.get("referenceVersion")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9a-f]{64}", version):
        raise ValueError("red routing plan requires a reference version")
    move_ids = {move["photoId"] for move in moves}
    if (not moves or len({move["sha256"] for move in moves}) != len(moves)
            or routing_plan.get("planningOnly") is not True
            or routing_plan.get("candidateCount") != len(moves)
            or move_ids != {row["photoId"] for row in snapshot_candidates}
            or set(routing_plan.get("retiredReferenceIds", ())) != move_ids
            or set(routing_plan.get("retiredReferenceSHA256", ())) != {move["sha256"] for move in moves}):
        raise ValueError("red routing staging requires the complete retired snapshot candidate set")
    decisions = routing_plan.get("assignments", []) + routing_plan.get("held", [])
    by_id = {}
    for row in decisions:
        photo_id = row.get("photoId")
        if not photo_id or photo_id in by_id:
            raise ValueError("red routing plan has ambiguous candidate decisions")
        by_id[photo_id] = row
    if len(moves) != len(by_id) or move_ids != set(by_id):
        raise ValueError("red routing moves must conserve the complete decision set")
    normalized = []
    for move in moves:
        decision = by_id[move["photoId"]]
        source = pathlib.PurePosixPath(move["source"])
        if decision.get("preserveStaged") or decision.get("releaseBlocked"):
            raise ValueError(f'{move["photoId"]}: blocked decision cannot be staged')
        folder = decision.get("destination")
        review = decision.get("reviewDestination")
        if bool(folder) == bool(review):
            raise ValueError(f'{move["photoId"]}: decision requires exactly one destination')
        destination = f"{folder}/gallery" if folder else review
        parts = pathlib.PurePosixPath(destination).parts
        if not (
            destination == "Various/review"
            or (len(parts) == 3 and parts[0] in {"Sisters", "Angels", "Models", "Prospects", "Potentials"}
                and parts[1] not in ("", ".", "..") and parts[2] in ("gallery", "review")
                and "/".join(parts[:2]) != source.parent.parent.as_posix())
        ):
            raise ValueError(f'{move["photoId"]}: invalid red routing destination')
        if (decision.get("sourceFolder") != source.parent.parent.as_posix()
                or decision.get("sourceBucket", "").lower() != source.parent.name
                or decision.get("reason") != move.get("reason")
                or move["destination"] != f"{destination}/{source.name}"):
            raise ValueError(f'{move["photoId"]}: move differs from red routing decision')
        normalized.append({**move, "destination": f"Various/review/{source.name}"})
    result = red_release_hold_catalog(
        catalog, normalized, snapshot_candidates, policy,
        release_bands=routing_plan.get("releaseBands", ("red",)),
        include_unscored=routing_plan.get("includeUnscored", False),
    )
    updated = result["catalog"]
    people = {}
    for person_id, person in updated["people"].items():
        if person.get("mergedInto"):
            continue
        folder = person["folder"]
        if folder in people:
            raise ValueError(f"red routing destination has ambiguous catalogue identity: {folder}")
        people[folder] = person_id
    for move in moves:
        decision = by_id[move["photoId"]]
        destination = pathlib.PurePosixPath(move["destination"])
        if destination.parts[0] == "Various":
            if destination.parent.as_posix() != "Various/review":
                raise ValueError(f'{move["photoId"]}: invalid unassigned red destination')
            continue
        folder = destination.parent.parent.as_posix()
        person_id = people.get(folder)
        if person_id is None:
            raise ValueError(f'{move["photoId"]}: destination is not an existing catalogue identity')
        rejections.require_destination(catalog, move["photoId"], move["sha256"], person_id)
        old = catalog["photos"].get(move["photoId"], {}).get("membership", {})
        admission = decision.get("castAdmission")
        if (admission and admission["mode"] == "optimistic-gallery"
                and updated["photos"][move["photoId"]]["protected"]):
            raise ValueError(f'{move["photoId"]}: protected optimistic Gallery conflicts with metadata contract')
        tentative = destination.parent.name == "review" or bool(
            admission and admission["mode"] == "optimistic-gallery"
        )
        updated["photos"][move["photoId"]]["membership"] = {
            "personId": person_id, "groupId": None,
            "status": "tentative" if tentative else "supported",
            "coreUse": bool(not tentative and decision.get("referenceEligible")),
            "reason": decision["reason"], "referenceVersion": version,
            "assignmentDisposition": "provisional" if tentative else "supported",
            "sourcePersonIds": sorted(set(old.get("sourcePersonIds", ())) | (
                {old["personId"]} if old.get("personId") else set()
            )),
            **({"assignmentEvidence": {"castAdmission": admission}} if admission else {}),
        }
    metadata.validate_catalog(updated)
    return result


def frozen_red_gallery_inventory(api, root, cfg, policy, cache_path, *, nonvoting_paths,
                                 measure_missing=False, collapse_identical_same_owner=False):
    """Rebuild people Gallery references; optional local inference never writes evidence."""
    from tools.art import duplicates, originals
    from . import actions, normal_import, normal_transaction, reconciliation
    from .policy import effective_settings

    root = pathlib.Path(root).resolve()
    cache_path = pathlib.Path(cache_path).absolute()
    try:
        cache_relative = cache_path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("red inventory cache must be inside the selected library") from exc
    cache_path = normal_transaction.safe(root, cache_relative)
    cache_bytes = cache_path.read_bytes()
    cache = json.loads(cache_bytes)
    catalog_path = normal_transaction.safe(root, ".likeness-library.json")
    catalog_bytes = catalog_path.read_bytes()
    catalog = metadata.load_catalog(catalog_path)
    groups = normal_import.IDENTITY_ROOTS
    nonvoting = dict(nonvoting_paths)
    configured = set(cfg.get("paths", {}).get("photoRoots", api.cw.PHOTO_ROOTS))
    omitted = sorted(group for group in groups if (root / group).is_dir() and group not in configured)
    if omitted:
        raise ValueError("red inventory configuration omits identity roots: " + ", ".join(omitted))
    settings = effective_settings(cfg, policy)

    def inventory():
        rows = []
        for group, name, folder in api.cw.photo_folders(cfg, root):
            if group not in groups:
                continue
            for path in originals.images(folder / "gallery"):
                relative = path.relative_to(root).as_posix()
                rows.append((group, name, normal_transaction.safe(root, relative), relative))
        return sorted(rows, key=lambda row: row[3])

    entries = inventory()
    photos, hashes, measured, photo_ids, missing, excluded = [], {}, set(), set(), [], {}
    voting_hashes, entries_by_path, native_digests = {}, {}, {}
    for group, name, path, relative in entries:
        photo_id = metadata.photo_id_from_name(path.name)
        if not photo_id or photo_id in photo_ids:
            raise ValueError(f"red inventory has an unidentified or duplicate Gallery photo: {relative}")
        photo_ids.add(photo_id)
        payload = path.read_bytes()
        digest = hashlib.sha1(payload).hexdigest()
        checksum = hashlib.sha256(payload).hexdigest()
        hashes[relative] = checksum
        native_digests[relative] = digest
        entries_by_path[relative] = (group, name, path, relative)
        if relative in nonvoting:
            if nonvoting[relative] != checksum:
                raise ValueError(f"non-voting Gallery native changed: {relative}")
            excluded[relative] = checksum
            continue
        voting_hashes.setdefault(checksum, []).append((group, name, path, relative))
    if set(excluded) != set(nonvoting):
        raise ValueError("non-voting Gallery bindings include missing or out-of-scope paths")

    derived_nonvoting = {}
    selections = actions.selected_photo_bindings(cfg)
    chosen = duplicates.chosen_stems(cfg)
    anchor_ids = {
        photo_id for person in catalog.get("people", {}).values()
        for photo_id in person.get("identityAnchors", [])
    }
    for checksum, duplicates_found in voting_hashes.items():
        if len(duplicates_found) < 2:
            continue
        owners = {(group, name) for group, name, _, _ in duplicates_found}
        ids = {metadata.photo_id_from_name(path.name) for _, _, path, _ in duplicates_found}
        ambiguous = (
            not collapse_identical_same_owner or len(owners) != 1
            or bool(ids & anchor_ids)
            or any(binding["photoId"] in ids for binding in selections)
            or any(
                binding["photoId"] is None and binding["hero"].casefold() == name.casefold()
                for _, name, _, _ in duplicates_found for binding in selections
            )
        )
        for photo_id in ids:
            record = catalog.get("photos", {}).get(photo_id, {})
            if (record.get("protected") or record.get("contentSha256", checksum) != checksum
                    or set(record) - {"contentSha256", "protected"}):
                ambiguous = True
        if ambiguous:
            raise ValueError(
                "duplicate Gallery content has ambiguous voting authority: "
                + ", ".join(row[3] for row in duplicates_found)
            )
        candidates = [
            (path, group, path.parent.parent, "gallery")
            for group, _, path, _ in duplicates_found
        ]
        keeper = duplicates.keeper(candidates, chosen)[0]
        keep_relative = keeper.relative_to(root).as_posix()
        for _, _, path, relative in duplicates_found:
            if path != keeper:
                excluded[relative] = checksum
                derived_nonvoting[relative] = {"sha256": checksum, "keeper": keep_relative}

    for relative, (group, name, path, _) in entries_by_path.items():
        if relative in excluded:
            continue
        checksum = hashes[relative]
        digest = native_digests[relative]
        measurement = cache.get("emb", {}).get(digest)
        if (not normal_import._current_measurement(measurement)
                or type(measurement.get("faces")) is not int or measurement["faces"] < 0
                or (measurement["faces"] > 0) != bool(measurement.get("v"))):
            missing.append((group, name, path, relative, digest, checksum))
            continue
        _red_measurement_quality(measurement, settings, relative)
        if measurement.get("v"):
            if (measurement.get("alignmentEvidence") or {}).get("sourceSha256") != checksum:
                raise ValueError(f"red Gallery measurement is not bound to native bytes: {relative}")
            measured.add(checksum)
        photos.append(api.Photo(path, group, name, digest, measurement))
    if missing and not measure_missing:
        raise ValueError(
            f"red inventory is missing a current Gallery measurement for {len(missing)} photo(s): "
            + ", ".join(row[3] for row in missing[:8])
        )
    _, checked_cache_hash, _, model_ids, _ = _red_cache_vectors(root, cache_path, measured)
    if checked_cache_hash != hashlib.sha256(cache_bytes).hexdigest():
        raise ValueError("red inventory cache changed during collection")
    domains = api.domains
    domain_token = domains.CURRENT.set("general")
    read_token = domains.READ_ONLY.set(True)
    supplemental = {}
    try:
        if missing:
            if len(model_ids) != 1:
                raise ValueError("red inventory requires one saved model identity before local inference")
            embedder = api.Embedder()
            embedder.load()
            if embedder.model_id not in model_ids:
                raise ValueError("local face models differ from the saved red inventory model")
            for group, name, path, relative, digest, checksum in missing:
                data = embedder(path)
                if (not normal_import._current_measurement(data)
                        or type(data.get("faces")) is not int or data["faces"] < 0
                        or (data["faces"] > 0) != bool(data.get("v"))):
                    raise ValueError(f"local face model did not produce a usable measurement: {relative}")
                _red_measurement_quality(data, settings, relative)
                if data.get("v"):
                    raw = np.asarray(data["v"], dtype=float)
                    mean = np.asarray(cache["centeringMean"], dtype=float)
                    if raw.shape != mean.shape or not np.isfinite(raw).all() or not np.linalg.norm(nz(raw - mean)):
                        raise ValueError(f"local Gallery measurement has an invalid vector: {relative}")
                    evidence = data.get("alignmentEvidence") or {}
                    if (evidence.get("state") != "read-only-not-persisted"
                            or evidence.get("sourceSha256") != checksum
                            or evidence.get("modelId") != embedder.model_id):
                        raise ValueError(f"local Gallery measurement has invalid provenance: {relative}")
                supplemental[digest] = data
                photos.append(api.Photo(path, group, name, digest, data))
            import cv2

            if embedder._model_identity(cv2)[1] != embedder.model_id:
                raise ValueError("local face models changed during red inventory measurement")
        photos.sort(key=lambda photo: photo.path.relative_to(root).as_posix())
        space = api.Space(photos, settings, mean=cache.get("centeringMean"))
        cores, _, diagnostics = reconciliation.frozen_identity_cores(
            space, catalog, photo_id_fn=metadata.photo_id_from_name,
            content_sha256_fn=metadata.content_sha256, policy=policy, require_single_face=True,
        )
        references = reference_rows(space, cores, catalog)
    finally:
        domains.READ_ONLY.reset(read_token)
        domains.CURRENT.reset(domain_token)
    if [row[3] for row in inventory()] != list(hashes):
        raise ValueError("red Gallery inventory changed during collection")
    for relative, digest in hashes.items():
        if metadata.content_sha256(normal_transaction.safe(root, relative)) != digest:
            raise ValueError(f"red Gallery native changed during collection: {relative}")
    if (hashlib.sha256(cache_path.read_bytes()).hexdigest() != checked_cache_hash
            or catalog_path.read_bytes() != catalog_bytes):
        raise ValueError("red inventory cache or catalogue changed during collection")
    return {
        "cores": cores, "references": references,
        "referencePaths": {
            metadata.photo_id_from_name(photo.name): photo.path.relative_to(root).as_posix()
            for photo in photos if photo.key in cores
            and metadata.photo_id_from_name(photo.name) in cores[photo.key]["corePhotoIds"]
        },
        "nativeBindings": hashes, "cacheSHA256": checked_cache_hash,
        "nonvotingBindings": excluded,
        "derivedNonvotingBindings": derived_nonvoting,
        "catalogSHA256": hashlib.sha256(catalog_bytes).hexdigest(), "modelIds": sorted(model_ids),
        "diagnostics": diagnostics, "centeringPopulationVerified": False,
        "currentModelBytesVerified": bool(missing), "supplementalMeasurements": supplemental,
        "supplementalMeasurementsPersisted": False,
    }


def red_release_plan(api, candidates, cores, references, settings, policy, names_taken, *,
                     snapshot_bands, snapshot_candidates, selected_ids, locked=False,
                     release_bands=("red",), allow_empty_source_cores=False, include_unscored=False):
    """Plan from caller-verified snapshot evidence; never authorize or publish moves."""
    validate_score_bands(snapshot_bands)
    selected_bands = _release_bands(release_bands)
    if snapshot_bands != policy["scoreBands"]:
        raise ValueError("saved Review score bands differ from the routing policy")
    saved = {}
    for row in snapshot_candidates:
        if not isinstance(row, dict):
            raise ValueError("saved red candidates must be objects")
        photo_id = row.get("photoId")
        if not photo_id or photo_id in saved:
            raise ValueError("saved red candidate IDs are missing or ambiguous")
        saved[photo_id] = row
    selected_ids = set(selected_ids)
    pending, blocked, ids, hashes = [], [], set(), set()
    for candidate in candidates:
        photo_id = candidate.get("photoId")
        digest = candidate.get("sha256")
        owner = candidate.get("sourceFolder")
        if (not isinstance(photo_id, str) or not photo_id or not isinstance(digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or not isinstance(owner, str) or not owner
                or candidate.get("sourceBucket") not in {"Gallery", "Review"}):
            raise ValueError("red release requires a stable ID, native SHA-256, owner and Gallery/Review bucket")
        if ("/" not in owner or owner.split("/", 1)[0] not in
                {"Sisters", "Angels", "Models", "Prospects", "Potentials"}
                or candidate.get("side") != "Prospects"):
            raise ValueError(f"{photo_id}: red release is restricted to people identities")
        if photo_id in ids or digest in hashes:
            raise ValueError("red release candidate IDs and native content must be unambiguous")
        ids.add(photo_id)
        hashes.add(digest)
        evidence = saved.get(photo_id)
        if (evidence is None or evidence.get("owner") != owner
                or evidence.get("bucket") != candidate["sourceBucket"].lower()
                or evidence.get("currentPath") != candidate.get("currentPath")
                or not candidate.get("currentPath")
                or evidence.get("nativeSha256") != digest
                or evidence.get("score") != candidate.get("redScore")):
            raise ValueError(f"{photo_id}: candidate differs from saved Review evidence")
        score = candidate.get("redScore")
        if not ((score is None and include_unscored)
                or (score is not None and score_band(score, {"scoreBands": snapshot_bands}) in selected_bands)):
            raise ValueError(f"{photo_id}: saved own-core score is not red or in selected release bands")
        reason = None
        if candidate.get("workflowSelected") or photo_id in selected_ids:
            reason = "workflow replacement and consumer recovery are not verified"
        elif candidate.get("rejectionMetadataStale"):
            reason = "rejected-identity metadata is stale"
        elif owner not in cores and score is not None:
            reason = "former identity has no usable frozen core"
        if reason:
            blocked.append({
                "photoId": photo_id, "sourceFolder": owner,
                "sourceBucket": candidate["sourceBucket"], "reason": reason,
                "preserveStaged": True, "releaseBlocked": True,
            })
        else:
            pending.append({**candidate, "redRelease": True, "detachedOutlier": True})

    if ids != set(saved):
        raise ValueError("red release candidates do not match the saved evidence set")
    pending_by_id = {row["photoId"]: row for row in pending}
    seen_reference_ids = set()
    for folder, rows in references.items():
        for row in rows:
            if (not row.get("qualityEligible") or row.get("rejectionMetadataStale")
                    or folder in rejections.excluded_folders([row], cores)):
                raise ValueError(f"{folder}: reference is not eligible for red-release scoring")
            photo_id = row["photoId"]
            if photo_id not in pending_by_id:
                continue
            candidate = pending_by_id[photo_id]
            if (photo_id in seen_reference_ids or folder != candidate["sourceFolder"]
                    or row["sha256"] != candidate["sha256"]):
                raise ValueError(f"{photo_id}: frozen reference differs from red candidate evidence")
            seen_reference_ids.add(photo_id)
    shape = _validate_red_references(cores, references)
    for row in pending:
        vector = np.asarray(row["vector"], dtype=float)
        if (vector.shape != shape or not np.isfinite(vector).all()
                or not np.isclose(np.linalg.norm(vector), 1.)):
            raise ValueError(f'{row["photoId"]}: invalid red candidate vector')
    retired_ids = {row["photoId"] for row in pending}
    retired_hashes = {row["sha256"] for row in pending}
    refreshed, remaining = refresh_references(
        cores, references, retire_ids=retired_ids, retire_sha256=retired_hashes,
    )
    lost = sorted(set(cores) - set(refreshed))
    source_owners = {row["sourceFolder"] for row in pending}
    if lost and (not allow_empty_source_cores or not set(lost).issubset(source_owners)):
        raise ValueError("red reference retirement leaves unusable cores: " + ", ".join(lost))
    if not refreshed:
        raise ValueError("red reference retirement leaves no usable destination cores")
    ctx = context(refreshed, remaining, policy, locked=locked)
    ctx["redRelease"] = True
    ctx["deferGrouping"] = True
    result = api.plan_reconciliation(
        pending, refreshed, assign=settings["assign"], margin=settings["margin"],
        cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
        minimum_cluster=settings["minCluster"], cast_merge=policy["identityActions"]["autoMergeMinimum"],
        names_taken=names_taken, name_factory=api.invent_name, policy=policy,
        admission_context=ctx,
    )
    assignments = []
    for row in result["assignments"]:
        candidate = pending_by_id.get(row["photoId"])
        cast = row.get("castAdmission")
        if candidate and candidate.get("nonVoting"):
            held = {key: value for key, value in row.items() if key not in ("destination", "destinationType")}
            held["reason"] = "previously non-voting photo requires independent review"
            result["held"].append(held)
        elif candidate and candidate.get("protected") and cast and cast["mode"] == "optimistic-gallery":
            folder = row["destination"]
            rules = policy["categoryPolicies"][folder.split("/", 1)[0]]
            held = {key: value for key, value in row.items() if key not in ("destination", "destinationType")}
            held.update({
                "castAdmission": {**cast, "mode": "ambiguous-review"},
                "referenceEligible": False,
                "reason": "protected red photo cannot enter unconfirmed Gallery; held for Review",
            })
            if rules["reviewAdmissionEnabled"]:
                held["reviewDestination"] = f"{folder}/review"
            result["held"].append(held)
        else:
            assignments.append(row)
    result["assignments"] = assignments
    decisions = result["assignments"] + result["held"]
    decision_ids = [row["photoId"] for row in decisions]
    if len(decision_ids) != len(set(decision_ids)) or set(decision_ids) != retired_ids:
        raise ValueError("red release routing did not conserve the pending candidate set")
    for row in decisions:
        candidate = pending_by_id[row["photoId"]]
        if candidate.get("redScore") is None:
            excluded = rejections.excluded_folders([candidate], refreshed) | {candidate["sourceFolder"]}
            ranked = sorted(
                ((float(np.clip(candidate["vector"] @ core["vector"], -1., 1.)), folder)
                 for folder, core in refreshed.items() if folder not in excluded),
                key=lambda item: (-item[0], item[1].casefold(), item[1]),
            )
            row["unscoredAssessment"] = {
                "bestRival": ranked[0][1] if ranked else None,
                "bestRivalScore": ranked[0][0] if ranked else None,
                "qualityEligible": candidate["qualityEligible"],
                "basis": "independent rival core; former own-core score unavailable",
            }
        if (row.get("sourceFolder") != candidate["sourceFolder"]
                or row.get("sourceBucket") != candidate["sourceBucket"]):
            raise ValueError(f'{row["photoId"]}: routing changed the frozen source identity')
        destination = row.get("destination")
        review = row.get("reviewDestination")
        if destination and review:
            raise ValueError(f'{row["photoId"]}: routing produced multiple destinations')
        if destination and (destination not in refreshed or destination == candidate["sourceFolder"]):
            raise ValueError(f'{row["photoId"]}: routing produced an invalid destination identity')
        if review:
            parts = review.rsplit("/", 1)
            if (len(parts) != 2 or parts[1] != "review" or parts[0] not in refreshed
                    or parts[0] == candidate["sourceFolder"] or row.get("preserveStaged")):
                raise ValueError(f'{row["photoId"]}: routing produced an invalid Review destination')
    if any(not row.get("destination") for row in result["assignments"]):
        raise ValueError("red release assignment has no destination identity")
    for row in result["held"]:
        if pending_by_id[row["photoId"]].get("nonVoting"):
            row.pop("reviewDestination", None)
            row["reason"] = "previously non-voting photo requires independent review"
        if not row.get("reviewDestination"):
            row["releaseHold"] = True
            row["reviewDestination"] = "Various/review"
            row["preserveStaged"] = False
            row["reason"] += "; explicit unassigned hold in Various/review"
    result["held"].extend(blocked)
    result["held"].sort(key=lambda row: row["photoId"])
    result.update({
        "candidateCount": len(candidates), "heldCount": len(result["held"]),
        "retiredReferenceIds": sorted(retired_ids),
        "retiredReferenceSHA256": sorted(retired_hashes),
        "referenceVersion": ctx["referenceVersion"],
        "releaseBands": list(selected_bands),
        "includeUnscored": include_unscored,
        "nonVotingIds": sorted(row["photoId"] for row in pending if row.get("nonVoting")),
        "emptySourceCores": lost,
        "planningOnly": True,
    })
    return result


def red_release_from_snapshot(api, candidates, cores, references, settings, policy, names_taken, *,
                              receipt, report, root, cache_path, reference_paths, locked=False,
                              diagnostic_workflow_gaps=False, workflow_configuration_path=None):
    """Create a non-executable plan from a checked saved audit and caller measurements."""
    snapshot = verified_red_snapshot(
        receipt, report, root, policy, diagnostic_workflow_gaps=diagnostic_workflow_gaps,
        workflow_configuration_path=workflow_configuration_path,
    )
    review_measurements = verify_red_review_measurements(root, cache_path, snapshot["snapshotCandidates"])
    routing_measurements = verify_red_routing_measurements(
        root, cache_path, candidates, references, reference_paths, settings,
    )
    if (routing_measurements["cacheSHA256"] != review_measurements["cacheSHA256"]
            or routing_measurements["modelIds"] != review_measurements["modelIds"]):
        raise ValueError("red Review and routing measurement bindings differ")
    evidence = {row["photoId"]: row for row in snapshot["snapshotCandidates"]}
    checked_candidates = []
    for candidate in candidates:
        saved = evidence.get(candidate.get("photoId"), {})
        checked_candidates.append({
            **candidate,
            "workflowSelected": bool(
                snapshot["workflowGaps"] or candidate.get("workflowSelected") or saved.get("workflowSelected")
            ),
        })
    result = red_release_plan(
        api, checked_candidates, cores, references, settings, policy, names_taken,
        snapshot_bands=snapshot["snapshotBands"], snapshot_candidates=snapshot["snapshotCandidates"],
        selected_ids=snapshot["selectedIds"], locked=locked,
    )
    for path, digest in snapshot["inputBindings"].items():
        if metadata.content_sha256(pathlib.Path(path)) != digest:
            raise ValueError(f"red snapshot input changed during planning: {path}")
    if metadata.content_sha256(pathlib.Path(cache_path)) != routing_measurements["cacheSHA256"]:
        raise ValueError("red measurement cache changed during planning")
    result.update({
        "snapshotInputs": snapshot["inputBindings"],
        "snapshotReportManifestSHA256": snapshot["reportManifestSHA256"],
        "reviewMeasurementProof": review_measurements,
        "routingMeasurementProof": routing_measurements,
        "workflowConsumerCoverageVerified": False,
        "workflowGaps": snapshot["workflowGaps"],
        "measurementEvidenceVerified": False,
    })
    return result


def checked_red_release_diagnostic(api, root, cfg, policy, cache_path, *, receipt, report,
                                   simulate_all=False, simulate_core_refresh=False,
                                   workflow_configuration_path=None, simulate_destination_scores=False):
    """Reconstruct a non-executable diagnostic from the complete saved evidence."""
    from . import normal_transaction
    from .policy import effective_settings

    if simulate_core_refresh and not simulate_all:
        raise ValueError("rebuilt Review census requires hypothetical routing")
    if simulate_destination_scores and not simulate_core_refresh:
        raise ValueError("destination scoring requires rebuilt Review cores")
    root = pathlib.Path(root).resolve()
    snapshot = verified_red_snapshot(
        receipt, report, root, policy, diagnostic_workflow_gaps=True,
        workflow_configuration_path=workflow_configuration_path,
    )
    workflow_cfg = cfg if workflow_configuration_path is None else api.cw.validate_config(
        json.loads(pathlib.Path(workflow_configuration_path).read_bytes())
    )
    cfg_hash = hashlib.sha256(
        json.dumps(workflow_cfg, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if cfg_hash != snapshot["configurationSHA256"]:
        raise ValueError("red diagnostic configuration differs from the checked snapshot")
    nonvoting = verified_red_nonvoting_gallery(
        receipt, report, root, workflow_configuration_path=workflow_configuration_path,
    )
    centering = verify_red_centering_population(
        receipt, report, root, cache_path, cfg, policy,
        workflow_configuration_path=workflow_configuration_path,
    )
    inventory = frozen_red_gallery_inventory(
        api, root, cfg, policy, cache_path, nonvoting_paths=nonvoting,
        collapse_identical_same_owner=True,
    )
    if inventory["diagnostics"]:
        raise ValueError("red diagnostic has unresolved frozen core diagnostics")
    if (centering["cacheSHA256"] != inventory["cacheSHA256"]
            or centering["modelIds"] != inventory["modelIds"]):
        raise ValueError("red diagnostic centering and Gallery inventory bindings differ")
    settings = effective_settings(cfg, policy)
    _, cache_hash, vectors, model_ids, measurements = _red_cache_vectors(
        root, cache_path, {row["nativeSha256"] for row in snapshot["snapshotCandidates"]},
    )
    if cache_hash != inventory["cacheSHA256"] or sorted(model_ids) != inventory["modelIds"]:
        raise ValueError("red diagnostic candidates and Gallery inventory bindings differ")
    catalog_path = normal_transaction.safe(root, ".likeness-library.json")
    catalog = metadata.load_catalog(catalog_path)
    if metadata.content_sha256(catalog_path) != inventory["catalogSHA256"]:
        raise ValueError("red diagnostic catalogue changed after inventory")
    protected_folders = {
        person["folder"] for person in catalog["people"].values() if person.get("protected")
    }
    candidates = []
    for row in snapshot["snapshotCandidates"]:
        photo_id, digest, owner = row["photoId"], row["nativeSha256"], row["owner"]
        record = catalog["photos"].get(photo_id, {})
        if record and record["contentSha256"] != digest:
            raise ValueError(f"{photo_id}: red diagnostic catalogue content is stale")
        candidates.append({
            "photoId": photo_id, "sourceFolder": owner, "sourceBucket": row["bucket"].title(),
            "currentPath": row["currentPath"], "sha256": digest, "redScore": row["score"],
            "side": "Prospects", "vector": vectors[digest],
            "qualityEligible": _red_measurement_quality(measurements[digest], settings, photo_id),
            "protected": bool(record.get("protected")), "identityProtected": owner in protected_folders,
            **rejections.candidate_state(catalog, photo_id, digest),
        })
    retired_ids = {row["photoId"] for row in snapshot["snapshotCandidates"]}
    replacement_proposals = []
    for row in snapshot["snapshotCandidates"]:
        if row["photoId"] not in snapshot["selectedIds"]:
            continue
        try:
            proposal = red_workflow_replacement_proposal(
                root, cache_path, row, workflow_cfg, policy, retired_ids=retired_ids,
            )
        except ValueError as exc:
            replacement_proposals.append({
                "photoId": row["photoId"], "state": "blocked", "reason": str(exc),
            })
        else:
            replacement_proposals.append({"state": "proposed", **proposal})
    folders = list(api.cw.photo_folders(cfg, root))
    result = red_release_from_snapshot(
        api, candidates, inventory["cores"], inventory["references"], settings, policy,
        {name for _, name, _ in folders}, receipt=receipt, report=report, root=root,
        cache_path=cache_path, reference_paths=inventory["referencePaths"],
        diagnostic_workflow_gaps=True, workflow_configuration_path=workflow_configuration_path,
    )
    if simulate_all:
        result["hypotheticalRouting"] = red_release_plan(
            api, candidates, inventory["cores"], inventory["references"], settings, policy,
            {name for _, name, _ in folders}, snapshot_bands=snapshot["snapshotBands"],
            snapshot_candidates=snapshot["snapshotCandidates"], selected_ids=set(),
        )
    if (result["snapshotReportManifestSHA256"] != snapshot["reportManifestSHA256"]
            or result["routingMeasurementProof"]["cacheSHA256"] != inventory["cacheSHA256"]
            or result["routingMeasurementProof"]["modelIds"] != inventory["modelIds"]
            or metadata.content_sha256(catalog_path) != inventory["catalogSHA256"]
            or list(api.cw.photo_folders(cfg, root)) != folders):
        raise ValueError("red diagnostic evidence changed during planning")
    for relative, digest in inventory["nativeBindings"].items():
        if metadata.content_sha256(normal_transaction.safe(root, relative)) != digest:
            raise ValueError(f"red diagnostic Gallery changed during planning: {relative}")
    result.update({
        "centeringProof": centering,
        "workflowReplacementProposals": replacement_proposals,
        "redRefreshCensus": verified_red_refresh_census(root, receipt, cache_path, snapshot, cache_hash),
        "redCandidateBindings": [{
            "photoId": row["photoId"], "path": row["currentPath"], "sha256": row["nativeSha256"],
        } for row in snapshot["snapshotCandidates"]],
        "galleryInventoryProof": {
            key: inventory[key] for key in (
                "nativeBindings", "nonvotingBindings", "derivedNonvotingBindings",
                "catalogSHA256", "cacheSHA256", "modelIds",
            )
        },
        "releaseAuthorized": False,
    })
    if simulate_core_refresh:
        import originals
        from . import normal_import

        result["hypotheticalReviewCensus"] = verified_rebuilt_red_review_census(
            root, receipt, cache_path, cfg, policy, snapshot, inventory, result["hypotheticalRouting"],
            include_destinations=simulate_destination_scores,
        )
        current_folders = list(api.cw.photo_folders(cfg, root))
        current_paths = {
            path.relative_to(root).as_posix()
            for group, _, folder in current_folders if group in normal_import.IDENTITY_ROOTS
            for path in originals.images(folder / "gallery")
        }
        if current_folders != folders or current_paths != set(inventory["nativeBindings"]):
            raise ValueError("red diagnostic Gallery inventory changed during rebuilt Review census")
        for relative, digest in inventory["nativeBindings"].items():
            if metadata.content_sha256(normal_transaction.safe(root, relative)) != digest:
                raise ValueError(f"red diagnostic Gallery changed during rebuilt Review census: {relative}")
    return result


def _released_bindings(candidates, bindings):
    """Validate the caller-verified voting release cohort against planning inputs."""
    if not isinstance(bindings, list):
        raise ValueError("released bindings must be a list")
    by_id = {}
    for candidate in candidates:
        by_id.setdefault(candidate.get("photoId"), []).append(candidate)
    checked, paths = {}, set()
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"photoId", "currentPath", "sha256"}:
            raise ValueError("invalid released candidate binding")
        photo_id, source, digest = binding["photoId"], binding["currentPath"], binding["sha256"]
        if (not isinstance(photo_id, str) or not photo_id or not isinstance(source, str)
                or not source or "\\" in source or ":" in source
                or any(part in ("", ".", "..") for part in source.split("/"))
                or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            raise ValueError("invalid released candidate binding")
        path = pathlib.PurePosixPath(source)
        matches = by_id.get(photo_id, [])
        standard = matches[0].get("releaseStandardName") if len(matches) == 1 else None
        if (path.is_absolute() or path.parts[0] not in
                {"Sisters", "Angels", "Models", "Prospects", "Potentials", "Various"}
                or len(path.parts) not in (3, 4)
                or (path.parts[0] == "Various") != (len(path.parts) == 3)
                or path.parent.name not in ("gallery", "review")
                or (metadata.photo_id_from_name(path.name) != photo_id
                    and (not isinstance(standard, str) or metadata.photo_id_from_name(standard) != photo_id))
                or photo_id in checked or source.casefold() in paths):
            raise ValueError(f"{photo_id}: invalid or ambiguous released source binding")
        if (len(matches) != 1 or matches[0].get("sha256") != digest
                or matches[0].get("sourceFolder") != path.parent.parent.as_posix()
                or matches[0].get("sourceBucket") != "Pool"
                or matches[0].get("regroupReview") is not True
                or matches[0].get("rebaseCandidate") is not True):
            raise ValueError(f"{photo_id}: released binding differs from the intake candidate")
        checked[photo_id] = binding
        paths.add(source.casefold())
    return checked


def _rescore_released_holds(api, candidates, decisions, current, current_rows, retired_ids,
                            bindings, settings, policy, names_taken, locked, *, original_rows=None):
    """Individually assess guarded releases against independent final residuals."""
    guarded = [
        row for row in candidates
        if row["photoId"] in bindings and row.get("qualityEligible") is True
        and decisions[row["photoId"]].get("reason") ==
        "old lower core lost reference authority; hold instead of creating another fragment"
    ]
    if not guarded:
        return
    _validate_red_references(current, current_rows)
    retired_hashes = {
        row["sha256"] for inventory in (current_rows, original_rows or {})
        for rows in inventory.values() for row in rows
        if row["photoId"] in retired_ids
    }
    release_hashes = {binding["sha256"] for binding in bindings.values()}
    # Never allow a released photo, identical content, or any departing reference
    # to be part of this final independent assessment.
    frozen, rows = refresh_references(
        current, current_rows, retire_ids=set(retired_ids) | set(bindings),
        retire_sha256=retired_hashes | release_hashes,
    )
    counts_id, counts_hash = {}, {}
    for refs in rows.values():
        for ref in refs:
            counts_id[ref["photoId"]] = counts_id.get(ref["photoId"], 0) + 1
            counts_hash[ref["sha256"]] = counts_hash.get(ref["sha256"], 0) + 1
    if any(count != 1 for count in counts_id.values()) or any(count != 1 for count in counts_hash.values()):
        raise ValueError("released residual assessment has ambiguous reference IDs or content")
    for folder, refs in rows.items():
        if any(
            ref.get("qualityEligible") is not True or ref.get("rejectionMetadataStale")
            or folder in rejections.excluded_folders([ref], frozen)
            for ref in refs
        ):
            raise ValueError(f"{folder}: released residual assessment has ineligible reference evidence")
    independent_rows = {folder: protection._independent(refs, policy) for folder, refs in rows.items()}
    frozen, rows = refresh_references(frozen, independent_rows)
    ctx = context(frozen, rows, policy, locked=locked)
    ctx["deferGrouping"] = True
    for candidate in sorted(guarded, key=lambda row: row["photoId"]):
        excluded = rejections.excluded_folders([candidate], frozen)
        if candidate.get("detachedOutlier"):
            excluded.add(candidate["sourceFolder"])
        excluded.update(
            folder for folder in frozen if folder.split("/", 1)[0] in CAST
            and any(
                candidate["sourceFolder"] in pair and folder in pair and folder != candidate["sourceFolder"]
                for pair in policy["runtimeSettings"]["different"]
            )
        )
        vector = nz(np.asarray(candidate["vector"], dtype=float))
        comparisons = []
        for folder, core in frozen.items():
            if folder in excluded or core["side"] != candidate["side"]:
                continue
            comparisons.append({
                "folder": folder, "score": float(np.clip(vector @ core["vector"], -1., 1.)),
                "referencePhotoIds": [ref["photoId"] for ref in rows[folder]],
                "referenceSHA256": [ref["sha256"] for ref in rows[folder]],
            })
        comparisons.sort(key=lambda row: (-row["score"], row["folder"].casefold(), row["folder"]))
        report = api.plan_reconciliation(
            [candidate], frozen, assign=settings["assign"], margin=settings["margin"],
            cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
            minimum_cluster=settings["minCluster"], cast_merge=policy["identityActions"]["autoMergeMinimum"],
            names_taken=names_taken, name_factory=api.invent_name, policy=policy,
            admission_context=ctx,
        )
        result = report["assignments"] + report["held"]
        if (report.get("clusters") or len(result) != 1 or result[0].get("photoId") != candidate["photoId"]
                or result[0].get("sourceFolder") != candidate["sourceFolder"]
                or result[0].get("sourceBucket") != candidate["sourceBucket"]
                or result[0].get("destinationType") == "provisional"
                or (result[0].get("destination") and result[0].get("reviewDestination"))):
            raise ValueError(f'{candidate["photoId"]}: residual assessment did not conserve its candidate')
        proposed = result[0]
        destination = proposed.get("destination")
        review = proposed.get("reviewDestination")
        target = destination
        if review:
            parts = review.rsplit("/", 1)
            if len(parts) != 2 or parts[1] != "review":
                raise ValueError(f'{candidate["photoId"]}: invalid residual Review destination')
            target = parts[0]
        if target and (
            target not in frozen or target in excluded
            or frozen[target]["side"] != candidate["side"]
            or (destination and proposed.get("destinationType") != "existing")
        ):
            raise ValueError(f'{candidate["photoId"]}: invalid residual identity destination')
        mode = proposed.get("castAdmission", {}).get("mode")
        accepted = bool(proposed.get("destination") or proposed.get("reviewDestination"))
        if mode in ("optimistic-gallery", "ambiguous-review"):
            accepted = False
        accepted = accepted and not proposed.get("preserveStaged")
        evidence = {
            "binding": dict(bindings[candidate["photoId"]]),
            "referenceVersion": ctx["referenceVersion"], "comparisons": comparisons,
            "excludedReferenceIds": sorted(set(retired_ids) | set(bindings)),
            "excludedReferenceSHA256": sorted(retired_hashes | release_hashes),
            "assessmentReason": proposed.get("reason"), "castMode": mode,
            "outcome": "placement" if accepted else "held",
        }
        if accepted:
            decisions[candidate["photoId"]] = {
                **proposed, "normalAdmission": True, "referenceEligible": False,
                "referenceVersion": ctx["referenceVersion"], "residualScoring": evidence,
            }
        else:
            decisions[candidate["photoId"]]["residualScoring"] = evidence
            best = (
                f'{comparisons[0]["folder"]} {comparisons[0]["score"]:.8f}'
                if comparisons else "no eligible reference"
            )
            decisions[candidate["photoId"]]["reason"] += (
                f'; residual assessment did not yield an unambiguous placement; highest residual: {best}; '
                f'reference version: {ctx["referenceVersion"]}'
            )
            decisions[candidate["photoId"]] = unresolved_release_review(
                decisions[candidate["photoId"]], comparisons, locked=locked,
            )


def unresolved_release_review(decision, comparisons, *, locked=False):
    """Send an unresolved released photo to its highest-scoring rival's Review, else Various Review.

    Review is not identity membership and grants no reference vote. ``comparisons``
    must already exclude rejected, cast-separated and retired evidence.
    """
    rivals = [
        row for row in comparisons
        if not (locked and row["folder"].split("/", 1)[0] in CAST)
    ]
    target = f'{rivals[0]["folder"]}/review' if rivals else "Various/review"
    return {
        **decision, "destination": None, "reviewDestination": target, "preserveStaged": False,
        "referenceEligible": False, "unresolvedReleaseReview": {
            "target": target, "basis": "highest-scoring rival" if rivals else "no eligible rival score",
            "score": rivals[0]["score"] if rivals else None,
        },
        "reason": decision.get("reason", "") + (
            f"; unresolved release sent to highest-scoring rival Review ({target})" if rivals
            else "; unresolved release held in Various Review (no eligible rival score)"
        ),
    }


def two_round_plan(api, candidates, cores, references, settings, policy, names_taken, *,
                   locked=False, released_bindings=None, named_folders=()):
    """Resolve members first; optionally rescore caller-verified released guard holds.

    The caller must verify each binding's source bytes and supply only voting
    candidates. The optional final assessment never recruits or forms identities.
    """
    release = _released_bindings(candidates, released_bindings) if released_bindings is not None else {}
    initial = {folder: dict(core) for folder, core in cores.items()}
    original_rows = {folder: list(rows) for folder, rows in references.items()}
    current, current_rows = initial, original_rows
    by_id = {row["photoId"]: row for row in candidates}
    decisions, clusters, histories = {}, [], []
    snapshots = {}

    def route(rows, frozen, ctx):
        return api.plan_reconciliation(
            rows, frozen, assign=settings["assign"], margin=settings["margin"],
            cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
            minimum_cluster=settings["minCluster"], cast_merge=policy["identityActions"]["autoMergeMinimum"],
            names_taken=names_taken, name_factory=api.invent_name, policy=policy,
            admission_context=ctx,
        )

    def owner(row):
        return row.get("destination") or (
            row["reviewDestination"].rsplit("/", 1)[0] if row.get("reviewDestination") else None
        )

    def leaving(rows):
        return {
            row["photoId"] for row in rows
            if owner(row) and (
                owner(row) != row["sourceFolder"] or row.get("reviewDestination")
            )
        }

    def pool_candidate(row):
        return row["sourceFolder"] == "Various" or row.get("regroupReview")

    pending = list(candidates)
    for round_index in (1, 2):
        ctx = context(current, current_rows, policy, locked=locked)
        ctx["namedFolders"] = set(named_folders)
        ctx["deferGrouping"] = round_index == 1
        snapshots[str(round_index)] = {
            "referenceVersion": ctx["referenceVersion"],
            "photoIds": {folder: list(core["corePhotoIds"]) for folder, core in sorted(current.items())},
        }
        round_rows, retired_ids, retired_folders, recomputed_folders = [], set(), set(), set()
        existing = [row for row in pending if not pool_candidate(row)]
        arrivals = [row for row in pending if pool_candidate(row)]
        deferred = []
        for batch in (existing, arrivals):
            report = route(batch, current, {**ctx, "castOnly": True})
            terminal = report["assignments"] + [row for row in report["held"] if not row.get("lowerDeferred")]
            deferred.extend(by_id[row["photoId"]] for row in report["held"] if row.get("lowerDeferred"))
            round_rows.extend(terminal)
            retired_ids.update(leaving(terminal))
        for batch in (
            [row for row in deferred if not pool_candidate(row)],
            [row for row in deferred if pool_candidate(row)],
        ):
            # IU13: a departing member's identity is recomputed from its remaining
            # members; only an identity left with no members loses its core.
            affected = {
                folder for folder, core in current.items()
                if folder.split("/", 1)[0] not in CAST and retired_ids.intersection(core["corePhotoIds"])
            }
            recomputed, recomputed_rows = refresh_references(
                {folder: current[folder] for folder in affected},
                {folder: current_rows.get(folder, []) for folder in affected},
                retire_ids=retired_ids,
            )
            retired_folders.update(affected - set(recomputed))
            recomputed_folders.update(recomputed)
            retained = {
                folder: recomputed.get(folder, core) for folder, core in current.items()
                if folder not in retired_folders
            }
            retained_rows = {
                folder: recomputed_rows.get(folder, current_rows.get(folder, [])) for folder in retained
            }
            eligible = []
            for candidate in batch:
                # Bound releases never vote mid-run: a recomputed former home still
                # sends them to the final residual assessment, as before IU13.
                held_folders = retired_folders | (affected if candidate["photoId"] in release else set())
                retired_score = max((
                    float(candidate["vector"] @ current[folder]["vector"]) for folder in held_folders
                ), default=-1.)
                retained_score = max((
                    float(candidate["vector"] @ core["vector"]) for folder, core in retained.items()
                    if folder.split("/", 1)[0] not in CAST and folder not in held_folders
                ), default=-1.)
                if retired_score >= max(retained_score, policy["photoRouting"]["reviewMinimum"]):
                    round_rows.append({
                        "photoId": candidate["photoId"], "sourceFolder": candidate["sourceFolder"],
                        "sourceBucket": candidate["sourceBucket"], "preserveStaged": True,
                        "reason": "old lower core lost reference authority; hold instead of creating another fragment",
                    })
                else:
                    eligible.append(candidate)
            report = route(eligible, retained, {**ctx, "skipCast": True, "references": retained_rows})
            rows = report["assignments"] + report["held"]
            round_rows.extend(rows)
            retired_ids.update(leaving(rows))
            clusters.extend(report.get("clusters", []))
        for row in round_rows:
            row["normalAdmission"] = True
            row.setdefault("referenceVersion", ctx["referenceVersion"])
            if row.get("destinationType") == "provisional":
                row["referenceEligible"] = any(
                    row["photoId"] in group["corePhotoIds"]
                    for group in clusters if group["destination"] == row.get("destination")
                )
            decisions[row["photoId"]] = row
        histories.append({
            "round": round_index, "candidateCount": len(pending),
            "existingFirst": True, "retiredReferenceIds": sorted(retired_ids),
            "retiredLowerCores": sorted(retired_folders),
            "recomputedCores": sorted(recomputed_folders - retired_folders),
        })
        next_rows = {
            folder: [row for row in rows if row["photoId"] not in retired_ids]
            for folder, rows in current_rows.items()
        }
        for decision in sorted(round_rows, key=lambda row: row["photoId"]):
            target = decision.get("destination")
            if not target or target not in current or decision.get("castAdmission", {}).get("mode") == "optimistic-gallery":
                continue
            candidate = by_id[decision["photoId"]]
            if candidate["sourceFolder"] == target or not candidate.get("qualityEligible"):
                continue
            if not reference_quality(candidate):
                # Match-only (dominant-face) admissions never become reference votes.
                decision["referenceEligible"] = False
                continue
            rules = policy["categoryPolicies"][target.split("/", 1)[0]]
            prior = [
                row for row in ctx["independent"].get(target, [])
                if row["photoId"] != candidate["photoId"] and row["sha256"] != candidate["sha256"]
                and float(candidate["vector"] @ row["vector"]) >= rules["identityCoreMinimumSimilarity"]
            ]
            minimum = policy["castAdmission"]["minimumIndependentReferences"] if target.split("/", 1)[0] in CAST else 1
            present = next_rows.setdefault(target, [])
            independent = (
                len(prior) >= minimum and all(
                    row["sha256"] != candidate["sha256"]
                    and float(candidate["vector"] @ row["vector"]) <= policy["identityActions"]["independentEvidenceMaximumSimilarity"]
                    for row in present
                )
            )
            decision["referenceEligible"] = independent
            if independent:
                present.append({
                    "photoId": candidate["photoId"], "sha256": candidate["sha256"],
                    "vector": candidate["vector"], "qualityEligible": True,
                })
        if round_index == 2:
            if release:
                _rescore_released_holds(
                    api, candidates, decisions, current, current_rows,
                    {photo_id for history in histories for photo_id in history["retiredReferenceIds"]},
                    release, settings, policy, names_taken, locked, original_rows=original_rows,
                )
            break
        current, current_rows = refresh_references(initial, next_rows)
        pending = [
            by_id[photo_id] for photo_id, row in decisions.items()
            if not row.get("destination")
        ]
    assignments = [row for row in decisions.values() if row.get("destination")]
    held = [row for row in decisions.values() if not row.get("destination")]
    return {
        "assignments": sorted(assignments, key=lambda row: row["photoId"]),
        "held": sorted(held, key=lambda row: row["photoId"]), "clusters": clusters,
        "candidateCount": len(candidates), "assignedCount": len(assignments), "heldCount": len(held),
        "matchingRounds": histories, "referenceSnapshots": snapshots,
        "referenceRefreshCount": 1,
        "passCapReached": any(
            row.get("reviewDestination") or row.get("preserveStaged")
            for row in held
        ) or any(row.get("castAdmission", {}).get("mode") == "optimistic-gallery" for row in assignments),
    }


def validate_move(move, policy):
    """Recheck publication semantics against the bound final-round evidence."""
    data = move["castAdmission"]
    parts = move["destination"].split("/")
    if "/".join(parts[:-2]) != data["winner"] or parts[0] not in CAST:
        raise ValueError("cast admission evidence does not own its destination")
    rules = policy["categoryPolicies"][parts[0]]
    gallery = parts[-2] == "gallery"
    if gallery:
        floor = rules.get("galleryAdmissionMinimumSimilarity", rules["photoRouteMinimum"])
        if data["score"] < floor or len(set(move.get("supportPhotoIds", ()))) < policy["castAdmission"]["minimumIndependentReferences"]:
            raise ValueError("cast Gallery lacks bound score or independent support")
        blockers = [
            row["folder"] for row in data["alternatives"]
            if data["score"] - row["score"] < rules["photoRouteMargin"]
        ]
        if data["mode"] == "optimistic-gallery":
            approved = {frozenset(pair) for pair in policy["castAdmission"]["approvedClosePairs"]}
            if not blockers or any(frozenset((data["winner"], rival)) not in approved for rival in blockers):
                raise ValueError("optimistic Gallery has an unapproved blocking rival")
            if move.get("referenceEligible"):
                raise ValueError("optimistic Gallery cannot grant reference authority")
        elif data["mode"] != "supported-gallery" or blockers:
            raise ValueError("cast Gallery retains an unresolved distinct-identity rival")
    elif (
        parts[-2] != "review" or data["mode"] not in ("ambiguous-review", "named-review")
        or data["score"] < policy["castAdmission"]["reviewMinimum"]
        or move.get("referenceEligible")
    ):
        raise ValueError("invalid provisional cast Review disposition")


SETTLE_IDENTITY_CATEGORIES = frozenset(("Sisters", "Angels", "Models", "Prospects", "Potentials"))
SETTLE_RELEASE_BANDS = ("red", "orange")


def settle_location(entry, decision):
    """Planned (folder, bucket) for one settle entry, mirroring ``maintenance.proposed_moves``."""
    if decision is None:
        return entry["sourceLocation"]
    if decision.get("destination"):
        return decision["destination"], "gallery"
    if decision.get("reviewDestination"):
        folder, bucket = decision["reviewDestination"].rsplit("/", 1)
        return folder, bucket
    if decision.get("preserveStaged"):
        return entry["sourceLocation"]
    if decision.get("clusterId") and decision.get("sourceBucket") != "Review":
        return "Various", "review"
    return entry["sourceLocation"]


def _settle_members(entries, decisions):
    members = {}
    for entry in entries:
        folder, bucket = settle_location(entry, decisions.get(entry["photoId"]))
        if bucket == "gallery" and folder.split("/", 1)[0] in SETTLE_IDENTITY_CATEGORIES:
            members.setdefault(folder, []).append(entry)
    return members


def _settle_voters(members, decisions, released=()):
    """One reference vote per content among single-face, voting, non-optimistic members."""
    voters = {}
    for folder, rows in sorted(members.items()):
        seen = {}
        for entry in sorted(rows, key=lambda row: row["photoId"]):
            decision = decisions.get(entry["photoId"]) or {}
            if (not entry["voter"] or entry["photoId"] in released
                    or (decision.get("castAdmission") or {}).get("mode") == "optimistic-gallery"
                    or entry["sha256"] in seen):
                continue
            seen[entry["sha256"]] = entry
        voters[folder] = list(seen.values())
    return voters


def _settle_scores(members, voters, policy):
    """Leave-one-out own score: each member against its identity's other voters (content excluded)."""
    scores = {}
    for folder, rows in sorted(members.items()):
        for entry in rows:
            score = band = None
            if entry["scorable"] and entry["vector"] is not None:
                others = [
                    row["vector"] for row in voters.get(folder, [])
                    if row["photoId"] != entry["photoId"] and row["sha256"] != entry["sha256"]
                ]
                if others:
                    center = nz(np.sum(others, axis=0))
                    if np.linalg.norm(center):
                        score = float(np.clip(entry["vector"] @ center, -1., 1.))
                        band = score_band(score, policy)
            scores[entry["photoId"]] = {"identity": folder, "score": score, "band": band}
    return scores


def _settle_cores(voters, identity_meta):
    cores, refs = {}, {}
    for folder, rows in sorted(voters.items()):
        if not rows:
            continue
        vector = nz(np.mean([row["vector"] for row in rows], axis=0))
        if not np.linalg.norm(vector):
            continue
        meta = identity_meta.get(folder) or {
            "side": "Prospects", "category": folder.split("/", 1)[0],
            "personIds": [], "identityProtected": False,
        }
        cores[folder] = {**meta, "vector": vector, "corePhotoIds": [row["photoId"] for row in rows]}
        refs[folder] = [
            {"photoId": row["photoId"], "sha256": row["sha256"], "vector": row["vector"],
             "qualityEligible": True,
             **{key: row["candidateState"][key] for key in ("rejectedPersonIds", "rejectionMetadataStale")
                if key in row.get("candidateState", {})}}
            for row in rows
        ]
    return cores, refs


def _settle_rivals(entry, cores, policy, *, locked, exclude=()):
    blocked = set(rejections.excluded_folders([entry.get("candidateState", {})], cores)) | set(exclude)
    for pair in policy["runtimeSettings"]["different"]:
        if entry["sourceFolder"] in pair:
            blocked.update(folder for folder in pair if folder != entry["sourceFolder"])
    if locked:
        blocked.update(folder for folder in cores if folder.split("/", 1)[0] in CAST)
    return sorted(
        ({"folder": folder, "score": float(np.clip(entry["vector"] @ core["vector"], -1., 1.))}
         for folder, core in cores.items() if folder not in blocked and core.get("side") == "Prospects"),
        key=lambda row: (-row["score"], row["folder"].casefold(), row["folder"]),
    )


def settle_passes(api, entries, decisions, clusters, identity_meta, settings, policy, names_taken, *,
                  locked=False, max_passes=3, candidate_for=None, clock=None):
    """Rebuild planned identities, release red/orange members and rematch them, up to ``max_passes``.

    ``entries`` are every measured planned photo: ``photoId``, ``sha256``,
    centered ``vector``, ``sourceFolder``, ``sourceLocation`` (folder, bucket
    when no decision moves it), ``voter`` (single-face voting content),
    ``scorable`` (match quality), ``exemptReason`` (never released),
    ``stayExemptReason`` (not released while it is planned at its source
    location, i.e. an original member that stayed in place),
    ``seedOf`` (cast seed identity), optional ``candidateState`` and the
    ``candidate`` evidence used to rematch a released photo (or
    ``candidate_for(entry)``, which builds it lazily).
    ``decisions`` (photo ID to decision) and ``clusters`` are updated in place.
    Each pass rescores every planned Gallery member leave-one-out against its
    identity's other voters (one vote per content; match-only, non-voters,
    optimistic and Review placements never vote), releases red/orange
    members except cast seeds and exempt photos, and rematches the released
    photos together against the identities rebuilt without them through the
    shared planner (existing Gallery or Review, band-aligned new identities,
    single-photo gate), falling back to the highest rival's Review or Various
    Review. Identities reduced to one photo follow the single-photo rule.
    Passes stop when a pass changes no planned location; flags left after
    the final pass are reported as did-not-settle. Deterministic; no I/O.
    """
    import time

    from .planner import SINGLE_PHOTO_LABEL

    clock = clock or time.perf_counter
    reduced = set()
    by_id = {entry["photoId"]: entry for entry in entries}
    if len(by_id) != len(entries):
        raise ValueError("settle entries have ambiguous photo IDs")
    entries = [by_id[photo_id] for photo_id in sorted(by_id)]
    yellow = policy["scoreBands"]["yellow"]["minimum"]
    taken = set(names_taken) | {cluster["destination"].split("/", 1)[1] for cluster in clusters if cluster.get("destination")}
    passes, timings, released_ever = [], [], {}
    starting_members = {folder: len(rows) for folder, rows in _settle_members(entries, decisions).items()}
    starting_cluster_members = {
        cluster["destination"]: sorted(
            entry["photoId"] for entry in _settle_members(entries, decisions).get(cluster["destination"], [])
        )
        for cluster in clusters if cluster.get("destination")
    }

    def exempt(entry, folder):
        if entry.get("seedOf") == folder:
            return "cast seed member (exempt)"
        if entry.get("exemptReason"):
            return entry["exemptReason"]
        if (entry.get("stayExemptReason")
                and settle_location(entry, decisions.get(entry["photoId"])) == entry["sourceLocation"]):
            return entry["stayExemptReason"]
        return None

    def assess():
        members = _settle_members(entries, decisions)
        voters = _settle_voters(members, decisions)
        return members, voters, _settle_scores(members, voters, policy)

    def provisional(folder):
        return next((cluster for cluster in clusters if cluster.get("destination") == folder), None)

    members, voters, scores = assess()
    lead = policy["photoRouting"]["minimumOwnCoreLead"]

    def below_category_bar(pid):
        # A member admitted on its category's Gallery bar is not released for clearing it.
        folder = scores[pid]["identity"]
        rules = policy["categoryPolicies"].get(folder.split("/", 1)[0], {})
        bar = rules.get("photoRouteMinimum")
        return folder.split("/", 1)[0] in CAST or bar is None or scores[pid]["score"] is None or scores[pid]["score"] < bar

    def rival_target(pid, cores):
        """IU17: an original member may leave only for a clearly better established rival."""
        entry, row = by_id[pid], scores[pid]
        if (not entry.get("rivalRelease") or entry.get("exemptReason") or entry.get("seedOf")
                or row["score"] is None or entry["vector"] is None):
            return None
        sizes = {folder: len(rows) for folder, rows in members.items()}
        rivals = [rival for rival in _settle_rivals(entry, cores, policy, locked=locked, exclude={row["identity"]})
                  if sizes.get(rival["folder"], 0) >= 2 and rival["folder"].split("/", 1)[0] not in CAST]
        if rivals and rivals[0]["score"] >= yellow and rivals[0]["score"] >= row["score"] + lead:
            return rivals[0]["folder"]
        return None

    for pass_index in range(1, max_passes + 1):
        started = clock()
        before = {entry["photoId"]: settle_location(entry, decisions.get(entry["photoId"])) for entry in entries}
        flagged = sorted(pid for pid, row in scores.items()
                         if row["band"] in SETTLE_RELEASE_BANDS and below_category_bar(pid))
        pass_cores, _pass_refs = _settle_cores(voters, identity_meta)
        rival_for = {}
        for pid in flagged:
            if exempt(by_id[pid], scores[pid]["identity"]) is not None and by_id[pid].get("rivalRelease"):
                target = rival_target(pid, pass_cores)
                if target:
                    rival_for[pid] = target
        release = [pid for pid in flagged if exempt(by_id[pid], scores[pid]["identity"]) is None or pid in rival_for]
        release_scores = {pid: dict(scores[pid]) for pid in release}
        record = {
            "pass": pass_index, "memberCount": len(scores),
            "scoredCount": sum(row["score"] is not None for row in scores.values()),
            "flaggedCount": len(flagged), "releasedCount": len(release),
            "released": [], "newIdentities": [], "singlePhotoReductions": [],
        }
        if release:
            released = set(release)
            cores, refs = _settle_cores(_settle_voters(members, decisions, released), identity_meta)
            ctx = context(cores, refs, policy, locked=locked)
            candidates = []
            for pid in release:
                entry = by_id[pid]
                base = entry.get("candidate") or (candidate_for(entry) if candidate_for else None)
                if base is None:
                    raise ValueError(f"{pid}: settle release lacks its candidate evidence")
                entry["candidate"] = base
                candidates.append({
                    **base, "photoId": pid, "sourceFolder": entry["sourceFolder"], "sourceBucket": "Pool",
                    "side": "Prospects", "vector": entry["vector"], "sha256": entry["sha256"],
                    "regroupReview": True, "rebaseCandidate": True, "protected": False,
                    "workflowSelected": False, "identityProtected": False,
                    "explicitReviewPlacement": False, "detachedOutlier": False,
                    **({} if entry["voter"] else {"referenceQualityEligible": False}),
                })
            result = api.plan_reconciliation(
                candidates, cores, assign=settings["assign"], margin=settings["margin"],
                cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
                minimum_cluster=settings["minCluster"], cast_merge=policy["identityActions"]["autoMergeMinimum"],
                names_taken=sorted(taken), name_factory=api.invent_name, policy=policy,
                admission_context=ctx,
            )
            new_clusters = {cluster["destination"]: cluster for cluster in result.get("clusters", [])}
            rows = {row["photoId"]: row for row in result["assignments"] + result["held"]}
            if set(rows) != released:
                raise ValueError("settle rematch did not conserve its released photos")
            for pid in release:
                row, entry = rows[pid], by_id[pid]
                if pid in rival_for:
                    landed = row.get("destination") or (row.get("reviewDestination") or "").rsplit("/", 1)[0]
                    if landed != rival_for[pid]:
                        # IU17: no churn; an original member stays home unless it lands at its rival.
                        record.setdefault("rivalReleaseKept", []).append(
                            {"photoId": pid, "identity": scores[pid]["identity"], "rival": rival_for[pid]})
                        continue
                previous = "/".join(before[pid])
                decision = {
                    **row, "normalAdmission": True, "referenceVersion": ctx["referenceVersion"],
                    "referenceEligible": False,
                }
                if row.get("destinationType") == "provisional":
                    decision["referenceEligible"] = pid in new_clusters[row["destination"]]["corePhotoIds"]
                if not (decision.get("destination") or decision.get("reviewDestination")) or decision.get("preserveStaged"):
                    if "castAdmission" in decision:
                        # Cast evidence that did not place the photo cannot own a fallback Review.
                        decision["castAdmissionEvidence"] = decision.pop("castAdmission")
                    decision = unresolved_release_review(
                        decision, _settle_rivals(entry, cores, policy, locked=locked), locked=locked,
                    )
                elif decision.get("destination") and provisional(decision["destination"]) is not None:
                    # Joining a provisional identity planned in this run, not an existing folder.
                    decision.update(
                        destinationType="provisional",
                        clusterId=provisional(decision["destination"])["clusterId"],
                    )
                decision["settle"] = {
                    "pass": pass_index, "releasedFrom": scores[pid]["identity"],
                    "releaseScore": scores[pid]["score"], "releaseBand": scores[pid]["band"],
                    "previousLocation": previous,
                }
                decision["reason"] = (
                    f'settle pass {pass_index}: {scores[pid]["band"]} member of {scores[pid]["identity"]} '
                    f'released and rematched; ' + decision.get("reason", "")
                )
                decisions[pid] = decision
                released_ever.setdefault(pid, []).append(pass_index)
            for destination, cluster in sorted(new_clusters.items()):
                clusters.append({**cluster, "settlePass": pass_index})
                starting_cluster_members[destination] = sorted(cluster["photoIds"])
                taken.add(destination.split("/", 1)[1])
                record["newIdentities"].append({
                    "destination": destination, "photoIds": list(cluster["photoIds"]),
                    "singlePhoto": bool(cluster.get("singlePhoto")),
                })
        # Identities reduced to one photo follow the single-photo rule.
        current = _settle_members(entries, decisions)
        for cluster in [item for item in clusters if item.get("destination")]:
            ids = sorted(entry["photoId"] for entry in current.get(cluster["destination"], []))
            if ids == starting_cluster_members.get(cluster["destination"], ids):
                continue  # membership not changed by settle
            starting_cluster_members[cluster["destination"]] = ids
            if not ids:
                clusters.remove(cluster)
            else:
                cluster["photoIds"] = ids
                cluster["corePhotoIds"] = sorted(set(cluster.get("corePhotoIds", ())) & set(ids)) or ids
                if len(ids) > 1 and cluster.pop("singlePhoto", None):
                    # A single-photo Potential that gains photos is no longer labelled single.
                    cluster.pop("singlePhotoLabel", None)
                    for photo_id in ids:
                        (decisions.get(photo_id) or {}).pop("singlePhoto", None)
        post_cores, post_refs = _settle_cores(_settle_voters(current, decisions), identity_meta)
        post_version = None
        for folder, rows in sorted(current.items()):
            if len(rows) != 1 or folder.split("/", 1)[0] in CAST or folder in reduced:
                continue
            cluster = provisional(folder)
            if cluster is not None and cluster.get("singlePhoto"):
                continue  # already formed as a single-photo Potential under the gate
            if cluster is None and starting_members.get(folder, 0) < 2:
                continue  # an existing identity this settle did not reduce
            entry = rows[0]
            if entry["vector"] is None or not entry["scorable"]:
                continue
            reduced.add(folder)
            rivals = _settle_rivals(entry, post_cores, policy, locked=locked, exclude={folder})
            gate = {
                "yellowMinimum": yellow, "bestRival": rivals[0]["folder"] if rivals else None,
                "bestRivalScore": round(rivals[0]["score"], 4) if rivals else None,
            }
            outcome = {"identity": folder, "photoId": entry["photoId"], "singlePhotoGate": gate}
            if rivals and rivals[0]["score"] >= yellow:
                rival = rivals[0]["folder"]
                rules = policy["categoryPolicies"][rival.split("/", 1)[0]]
                if not rules["reviewAdmissionEnabled"] or exempt(entry, folder):
                    outcome["outcome"] = "kept; rival Review unavailable or photo exempt"
                else:
                    if post_version is None:
                        post_version = context(post_cores, post_refs, policy, locked=locked)["referenceVersion"]
                    decisions[entry["photoId"]] = {
                        "photoId": entry["photoId"], "sourceFolder": entry["sourceFolder"],
                        "sourceBucket": "Pool", "destination": None, "reviewDestination": f"{rival}/review",
                        "preserveStaged": False, "referenceEligible": False, "normalAdmission": True,
                        "referenceVersion": post_version,
                        "bestMatch": rival, "bestScore": round(rivals[0]["score"], 4),
                        "singlePhotoGate": gate,
                        "settle": {"pass": pass_index, "releasedFrom": folder, "releaseScore": None,
                                   "releaseBand": None, "previousLocation": f"{folder}/gallery",
                                   "singlePhotoReduction": True},
                        "reason": (f"settle pass {pass_index}: identity reduced to one photo; it reaches yellow "
                                   f"against {rival}; sent to that rival's Review"),
                    }
                    if cluster is not None:
                        clusters.remove(cluster)
                    outcome["outcome"] = f"{rival}/review"
            elif cluster is not None:
                cluster.update(singlePhoto=True, singlePhotoLabel=SINGLE_PHOTO_LABEL)
                decision = decisions.get(entry["photoId"])
                if decision is not None:
                    decision.update(singlePhoto=True, singlePhotoGate=gate)
                    decision["reason"] = decision.get("reason", "") + f"; {SINGLE_PHOTO_LABEL} after settle pass {pass_index}"
                outcome["outcome"] = "single-photo Potential"
            else:
                outcome["outcome"] = "kept; every existing rival scores below yellow"
            record["singlePhotoReductions"].append(outcome)
        members, voters, scores = assess()
        after = {entry["photoId"]: settle_location(entry, decisions.get(entry["photoId"])) for entry in entries}
        moved = sorted(pid for pid in after if after[pid] != before[pid])
        for pid in release:
            record["released"].append({
                "photoId": pid, "identity": release_scores[pid]["identity"],
                "score": release_scores[pid]["score"], "band": release_scores[pid]["band"],
                "outcome": "/".join(after[pid]), "moved": after[pid] != before[pid],
            })
        record["movedCount"] = len(moved)
        record["movedPhotoIds"] = moved
        record["remainingFlaggedCount"] = sum(row["band"] in SETTLE_RELEASE_BANDS for row in scores.values())
        passes.append(record)
        timings.append(clock() - started)
        if not moved:
            break
    did_not_settle = []
    for pid, row in sorted(scores.items()):
        if row["band"] not in SETTLE_RELEASE_BANDS:
            continue
        reason = exempt(by_id[pid], row["identity"])
        if reason is None:
            reason = (
                "released and rematched but still red/orange" if pid in released_ever
                else "flagged after the final settle pass"
            )
        did_not_settle.append({
            "photoId": pid, "identity": row["identity"], "score": row["score"], "band": row["band"],
            "reason": reason, "releasedInPasses": released_ever.get(pid, []),
        })
    return {
        "maximumPasses": max_passes, "passCount": len(passes),
        # Converged: the last pass changed no planned location (or no pass ran).
        "converged": not passes or not passes[-1]["movedCount"],
        "passes": passes, "didNotSettle": did_not_settle,
        "releasedPhotoIds": sorted(released_ever),
        "finalScores": {pid: dict(row) for pid, row in sorted(scores.items())},
    }, timings
