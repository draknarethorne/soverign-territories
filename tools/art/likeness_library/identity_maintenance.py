"""Frozen established-identity proposals and recoverable folder-file relocation."""
import copy
import pathlib
from types import SimpleNamespace

from . import metadata
from .policy import (
    classify_category, evaluate_identity_action, evaluate_photo_consistency, evaluate_photo_route,
)


def independent_count(rows, policy):
    """Count a deterministic diverse subset; near-duplicate shots add no support."""
    maximum = policy["identityActions"].get("independentEvidenceMaximumSimilarity")
    if maximum is None:
        return 0
    selected = []
    for row in sorted((row for row in rows if row.get("photoId")), key=lambda item: item["photoId"]):
        if (
            all(row["photoId"] != other["photoId"] for other in selected)
            and all(float(row["vector"] @ other["vector"]) <= maximum for other in selected)
        ):
            selected.append(row)
    return len(selected)


def merge_actions(space, cores, catalog, locked_ids, selected_ids, policy, root, photo_moves):
    """Choose disjoint reciprocal matches; a frozen identity participates at most once."""
    people = {}
    for person_id, person in catalog["people"].items():
        if "mergedInto" not in person:
            people.setdefault(person["folder"], []).append((person_id, person))
    blocked = set(locked_ids) | set(selected_ids)
    changed = {
        pathlib.PurePosixPath(row[key]).parent.parent.as_posix()
        for row in photo_moves for key in ("source", "destination")
    }
    eligible = {}
    for folder, core in sorted(cores.items()):
        rules = policy["categoryPolicies"][core["category"]]
        records = people.get(folder, [])
        if (
            core["side"] == "Artists" or core["identityProtected"]
            or rules["identityProtectedByDefault"] or not rules["automaticMergeEnabled"]
            or len(records) != 1 or records[0][1]["identityAnchors"] or folder in changed
        ):
            continue
        photos = space.by_key[folder]
        if any(metadata.photo_id_from_name(photo.name) in blocked for photo in photos):
            continue
        eligible[folder] = records[0][0]
    pairs, evidence = [], []
    for left in eligible:
        for right in eligible:
            if left >= right:
                continue
            score = float(cores[left]["vector"] @ cores[right]["vector"])
            if score < policy["identityActions"]["matchReviewMinimum"]:
                continue
            decisions = []
            support_counts = []
            for source, target in ((left, right), (right, left)):
                competitors = [
                    float(cores[source]["vector"] @ other["vector"])
                    for folder, other in cores.items()
                    if folder not in (source, target) and other["side"] == cores[source]["side"]
                ]
                rows = [{
                    "photoId": metadata.photo_id_from_name(photo.name), "vector": photo.vec,
                } for photo in space.by_key[source] if photo.usable(space.st["minFace"])]
                rules = policy["categoryPolicies"][cores[target]["category"]]
                all_supported = all(
                    float(row["vector"] @ cores[target]["vector"]) >= rules["photoRouteMinimum"]
                    for row in rows
                )
                count = independent_count(rows, policy) if all_supported else 0
                support_counts.append(count)
                decisions.append(evaluate_identity_action(
                    "merge", cores[source]["category"], score=score,
                    margin=max(0., score - max(competitors, default=-1.)),
                    evidence_count=max(1, count), policy=policy, propose=True,
                ))
            if all(row["decision"] == "auto-merge" for row in decisions):
                pairs.append((score, left, right, support_counts))
            else:
                evidence.append({
                    "sourceFolder": left, "destinationFolder": right,
                    "decision": "review", "score": score, "independentSupport": support_counts,
                    "reason": "; ".join(row["reason"] for row in decisions),
                })
    actions, consumed = [], set()
    for score, left, right, counts in sorted(pairs, key=lambda row: (-row[0], row[1], row[2])):
        if left in consumed or right in consumed:
            continue
        destination, source = sorted(
            (left, right),
            key=lambda folder: (
                policy["categoryOrder"].index(cores[folder]["category"]),
                -len(space.by_key[folder]), folder.casefold(),
            ),
        )
        action = {
            "type": "identity-merge", "sourceFolder": source, "destinationFolder": destination,
            "personId": eligible[source], "destinationPersonId": eligible[destination],
            "score": score, "independentSupport": counts,
            "reason": "reciprocal frozen-core match with diverse photo support in both directions",
            "destinationInventory": {
                path.relative_to(pathlib.Path(root)).as_posix(): metadata.content_sha256(path)
                for path in (pathlib.Path(root) / destination).rglob("*") if path.is_file()
            },
        }
        try:
            moves = relocate_files(root, [], [action])
            if any((pathlib.Path(root) / row["destination"]).exists() for row in moves):
                evidence.append({**action, "decision": "hold", "reason": "merge destination file collision"})
                continue
        except OSError as exc:
            raise OSError(f"cannot inventory proposed identity merge {source}: {exc}") from exc
        actions.append(action)
        consumed.update((source, destination))
    return actions, evidence


def relocated_path(action, relative):
    suffix = pathlib.PurePosixPath(relative).relative_to(action["sourceFolder"])
    if action["type"] == "identity-merge" and suffix.parts[0] not in (
        "gallery", "review", "gallery_944x1104", "gallery_911x1104", "headshots",
    ):
        suffix = pathlib.PurePosixPath("_identity-history", action["personId"]) / suffix
    return (pathlib.PurePosixPath(action["destinationFolder"]) / suffix).as_posix()


def split_candidates(space, cores, locked_ids, selected_ids, policy):
    """Reconsider unprotected Gallery outliers without admitting core members."""
    candidates, evidence = [], []
    categories = policy["categoryPolicies"]
    for folder, core in sorted(cores.items()):
        rules = categories[core["category"]]
        if core["side"] == "Artists":
            continue
        photos = space.by_key[folder]
        retained_ids = core.get("corePhotoIds")
        retained_core = [{
            "photoId": metadata.photo_id_from_name(photo.name), "vector": photo.vec,
        } for photo in photos if (
            core["photoScores"].get(photo.name) is not None
            and core["photoScores"][photo.name] >= rules["identityCoreMinimumSimilarity"]
            and (retained_ids is None or metadata.photo_id_from_name(photo.name) in retained_ids)
        )]
        retained_support = independent_count(retained_core, policy)
        for photo in photos:
            photo_id = metadata.photo_id_from_name(photo.name)
            own = core["photoScores"].get(photo.name)
            if own is None:
                continue
            decision = evaluate_photo_consistency(
                core["category"], score=own, usable_photo_count=len(photos),
                photo_protected=photo_id in locked_ids,
                workflow_selected=photo_id in selected_ids,
                identity_protected=core["identityProtected"], policy=policy,
            )
            if decision["decision"] not in ("review", "split-review"):
                continue
            alternatives = sorted(
                (
                    (float(photo.vec @ other["vector"]), target)
                    for target, other in cores.items()
                    if target != folder and other["side"] == core["side"]
                ),
                key=lambda row: (-row[0], row[1].casefold()),
            )
            evidence.append({
                "photoId": photo_id, "sourceFolder": folder, "ownScore": float(own),
                "decision": decision["decision"], "reason": decision["reason"],
                "alternatives": [{"folder": target, "score": score} for score, target in alternatives[:3]],
            })
            if not rules["automaticSplitEnabled"] or not photo_id:
                continue
            if (
                rules.get("unmatchedOutlierSplitEnabled", False)
                and own < rules["splitCandidateBelowSimilarity"]
                and own < policy["identityActions"]["splitReviewMaximum"]
                and retained_support >= policy["identityActions"]["splitMinimumIndependentPhotos"]
                and (not alternatives or alternatives[0][0] < policy["photoRouting"]["reviewMinimum"])
            ):
                candidates.append({
                    "photoId": photo_id, "sourceFolder": folder, "sourceBucket": "Gallery",
                    "side": core["side"], "vector": photo.vec, "detachedOutlier": True,
                    "outlierCandidate": True,
                    "protected": False, "workflowSelected": False, "identityProtected": False,
                })
                evidence[-1]["decision"] = "split-new-identity"
                evidence[-1]["independentRetainedCorePhotos"] = retained_support
                continue
            if not alternatives:
                continue
            best, target = alternatives[0]
            lead = best - max(own, alternatives[1][0] if len(alternatives) > 1 else -1.)
            route = evaluate_photo_route(
                cores[target]["category"], score=best, margin=lead,
                identity_protected=cores[target]["identityProtected"], policy=policy, propose=True,
            )
            if (
                own < rules["splitCandidateBelowSimilarity"]
                and lead >= policy["photoRouting"]["minimumOwnCoreLead"]
                and route["decision"] == "auto-route"
            ):
                candidates.append({
                    "photoId": photo_id, "sourceFolder": folder, "sourceBucket": "Gallery",
                    "side": core["side"], "vector": photo.vec,
                    "protected": False, "workflowSelected": False, "identityProtected": False,
                    "splitOwnScore": float(own), "splitAlternativeScore": best,
                    "outlierCandidate": True,
                })
    by_target = {}
    detached = [row for row in candidates if row.get("detachedOutlier")]
    for row in candidates:
        if row.get("detachedOutlier"):
            continue
        ranking = sorted(
            (
                (float(row["vector"] @ other["vector"]), target)
                for target, other in cores.items()
                if target != row["sourceFolder"] and other["side"] == row["side"]
            ),
            reverse=True,
        )
        by_target.setdefault((row["sourceFolder"], ranking[0][1]), []).append(row)
    candidates = detached
    for rows in by_target.values():
        count = independent_count(rows, policy)
        for row in rows:
            decision = evaluate_identity_action(
                "split", cores[row["sourceFolder"]]["category"],
                score=row["splitOwnScore"],
                margin=max(0., row["splitAlternativeScore"] - row["splitOwnScore"]),
                evidence_count=max(1, count), policy=policy, propose=True,
            )
            if decision["decision"] == "auto-split":
                candidates.append(row)
    return candidates, evidence


def category_destination_available(root, folder):
    """Empty directory shells from earlier moves are safe to reuse, never delete."""
    destination = pathlib.Path(root) / folder
    if destination.is_symlink() or destination.resolve() != destination:
        raise ValueError("reparse point in category destination")
    if not destination.exists():
        return True
    if not destination.is_dir():
        return False
    for path in destination.rglob("*"):
        if path.is_symlink() or path.resolve() != path:
            raise ValueError("reparse point in category destination")
        if not path.is_dir():
            return False
    return True


def category_transitions(space, cores, report, catalog, locked_ids, selected_ids, policy, root,
                         measured_photos=None):
    """Classify final planned usable membership, preserving established identity IDs."""
    root = pathlib.Path(root).resolve()
    by_folder = {}
    for person_id, person in catalog["people"].items():
        by_folder.setdefault(person["folder"], []).append((person_id, person))
    photo_by_id = {
        metadata.photo_id_from_name(photo.name): photo for photo in (
            space.photos if measured_photos is None else measured_photos
        )
        if photo.usable(space.st["minFace"])
    }
    members = {
        folder: {
            metadata.photo_id_from_name(photo.name) for photo in space.by_key[folder]
            if photo.usable(space.st["minFace"])
        }
        for folder in cores
    }
    for move in report["moves"]:
        source = pathlib.PurePosixPath(move["source"])
        destination = pathlib.PurePosixPath(move["destination"])
        if source.parts[-2] == "gallery":
            members.get(source.parent.parent.as_posix(), set()).discard(move["photoId"])
        if destination.parts[-2] == "gallery" and move["photoId"] in photo_by_id:
            members.setdefault(destination.parent.parent.as_posix(), set()).add(move["photoId"])
    cast = {
        folder: core for folder, core in cores.items()
        if policy["categoryPolicies"][core["category"]]["identityProtectedByDefault"]
    }
    transitions, evidence = [], []
    for folder, ids in sorted(members.items()):
        if folder not in cores or not ids:
            continue
        if None in ids:
            evidence.append({
                "sourceFolder": folder, "decision": "hold",
                "reason": "missing stable photo IDs prevent category transition",
            })
            continue
        core = cores[folder]
        rules = policy["categoryPolicies"][core["category"]]
        if (
            core["side"] == "Artists" or rules["identityProtectedByDefault"]
            or core["identityProtected"] or not rules["automaticPhotoRoutingEnabled"]
        ):
            continue
        ranked = sorted(
            ((float(core["vector"] @ other["vector"]), key) for key, other in cast.items()),
            key=lambda row: (-row[0], row[1].casefold()),
        )
        classification = classify_category(
            len(ids), ranked[0][0] if ranked else None, policy,
            best_cast_folder=ranked[0][1] if ranked else None,
            second_cast_folder=ranked[1][1] if len(ranked) > 1 else None,
            cast_margin=ranked[0][0] - ranked[1][0] if len(ranked) > 1 else 2.,
        )
        category = classification["category"]
        if category in (None, "Review", core["category"]):
            continue
        record = {
            "sourceFolder": folder, "destinationFolder": f"{category}/{folder.split('/', 1)[1]}",
            "usablePhotos": len(ids), "reason": "category follows final planned usable membership",
        }
        records = by_folder.get(folder, [])
        if len(records) != 1:
            evidence.append({**record, "decision": "hold", "reason": "category transition requires one stable catalogue identity"})
            continue
        person_id, person = records[0]
        folder_ids = {
            metadata.photo_id_from_name(photo.name) for photo in space.by_key[folder]
        }
        if folder_ids & (set(locked_ids) | set(selected_ids)) or person["identityAnchors"]:
            evidence.append({**record, "decision": "hold", "reason": "protected, anchored or workflow photo blocks folder transition"})
            continue
        if (
            record["destinationFolder"] in by_folder
            or not category_destination_available(root, record["destinationFolder"])
        ):
            evidence.append({**record, "decision": "hold", "reason": "category destination already exists"})
            continue
        transitions.append({**record, "type": "category-transition", "personId": person_id})
    return transitions, evidence


def relocate_files(root, photo_moves, transitions):
    """Compile a complete file inventory; no directories or sidecars are discarded."""
    root = pathlib.Path(root).resolve()
    moves = [dict(row) for row in photo_moves]
    claimed = {row["source"] for row in moves}
    for transition in transitions:
        source = root / transition["sourceFolder"]
        for path in source.rglob("*"):
            if path.is_symlink() or path.resolve() != path:
                raise ValueError(f"reparse point in identity transition: {path}")
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if relative in claimed:
                continue
            moves.append({
                "source": relative,
                "destination": relocated_path(transition, relative),
                "sha256": metadata.content_sha256(path), "kind": "identity-file",
                "personId": transition["personId"], "reason": transition["reason"],
            })
        for row in moves:
            prefix = transition["sourceFolder"] + "/"
            if row["destination"].startswith(prefix):
                row["destination"] = transition["destinationFolder"] + row["destination"][len(prefix) - 1:]
    return moves


def check_applied_membership(root, measured_photos, moves, identity_actions, settings,
                             selected_ids, policy):
    """One read-only final-core check; never cascade moves from newly changed cores."""
    from .engine import matches
    from .reconciliation import frozen_identity_cores

    root = pathlib.Path(root).resolve()
    destinations = {row["source"]: row["destination"] for row in moves}
    gallery, review, by_key = [], [], {}
    affected = {
        action[key] for action in identity_actions
        for key in ("sourceFolder", "destinationFolder")
    }
    for row in moves:
        if row.get("kind") != "identity-file":
            affected.update(
                pathlib.PurePosixPath(row[key]).parent.parent.as_posix()
                for key in ("source", "destination")
            )
    for original in measured_photos:
        photo = copy.copy(original)
        relative = original.path.relative_to(root).as_posix()
        photo.path = root / destinations.get(relative, relative)
        photo.key = photo.path.parent.parent.relative_to(root).as_posix()
        if photo.path.parent.name == "gallery":
            gallery.append(photo)
            if photo.usable(settings["minFace"]) and not matches(photo.key, settings["mixed"]):
                by_key.setdefault(photo.key, []).append(photo)
        else:
            review.append(photo)
    space = SimpleNamespace(photos=gallery, by_key=by_key, st=settings)
    catalog = metadata.load_catalog(metadata.path_for_root(root))
    cores, locked, diagnostics = frozen_identity_cores(
        space, catalog, photo_id_fn=metadata.photo_id_from_name,
        content_sha256_fn=metadata.content_sha256, additional_photos=review, policy=policy,
    )
    outliers, outlier_evidence = split_candidates(space, cores, locked, selected_ids, policy)
    merges, _ = merge_actions(space, cores, catalog, locked, selected_ids, policy, root, [])
    transitions, category_evidence = category_transitions(
        space, cores, {"moves": []}, catalog, locked, selected_ids, policy, root,
        measured_photos=gallery + review,
    )
    outliers = [row["photoId"] for row in outliers if row["sourceFolder"] in affected]
    actions = [
        row for row in merges + transitions
        if {row["sourceFolder"], row["destinationFolder"]} & affected
    ]
    return {
        "status": "further-maintenance-candidates" if outliers or actions else "no-further-maintenance-candidates",
        "passes": 1, "automaticFollowupApplied": False,
        "affectedFolders": sorted(affected), "outlierPhotoIds": outliers,
        "identityActions": actions, "coreDiagnostics": diagnostics,
        "outlierEvidence": [row for row in outlier_evidence if row["sourceFolder"] in affected],
        "categoryEvidence": [row for row in category_evidence if row["sourceFolder"] in affected],
    }
