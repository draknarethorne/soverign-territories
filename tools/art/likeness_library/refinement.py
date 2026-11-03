"""Bounded in-place refinement of planned provisional identities.

Runs after first-pass routing and before naming, so merged identities still choose the
oldest recorded original name and every change flows through the normal install/undo path.
Each pass freezes its references, applies photo moves, then reciprocal identity merges.
"""
import copy

import numpy as np

from .planner import _core
from .policy import classify_category, evaluate_photo_route
from .rejections import excluded_folders

MAX_PASSES = 4


def _unit(vector):
    vector = np.asarray(vector, dtype=float)
    norm = np.linalg.norm(vector)
    if vector.ndim != 1 or not vector.size or not np.isfinite(vector).all() or norm == 0:
        return None
    return vector / norm


def _category(folder):
    return folder.split("/", 1)[0]


def _ranked(vector, references, excluded=()):
    return sorted(
        ((float(vector @ ref), folder) for folder, ref in references.items() if folder not in excluded),
        key=lambda item: (-item[0], item[1].casefold()),
    )


def _rename(value, names):
    if not isinstance(value, str):
        return value
    if value in names:
        return names[value]
    head, _, tail = value.rpartition("/")
    return f"{names[head]}/{tail}" if head in names else value


def rename_steps(rows, names):
    for row in rows:
        for step in row.get("refinement", ()):
            for key in ("from", "to"):
                step[key] = _rename(step.get(key), names)


def rename_evidence(evidence, names):
    """Translate provisional cluster folders in evidence to their chosen identity names."""
    def rename(value):
        return _rename(value, names)

    for item in evidence["passes"]:
        for row in item["moves"] + item["merges"] + item["dissolved"] + item["reclassified"]:
            for key in ("from", "to", "survivor", "loser", "folder"):
                if key in row:
                    row[key] = rename(row[key])
    for row in evidence["unresolved"]:
        for key in ("survivor", "loser"):
            if key in row:
                row[key] = rename(row[key])
    return evidence


def refine(result, candidates, cores, policy, *, locked_ids=(), max_passes=MAX_PASSES):
    """Return (refined result, evidence); never mutates the inputs."""
    result = copy.deepcopy(result)
    categories = policy["categoryPolicies"]
    routing = policy["photoRouting"]
    orange = policy["scoreBands"]["orange"]["minimum"]
    minima = (
        policy.get("rebaseProtection", {}).get("minimumOwnCoreSimilarities", {})
        if policy.get("rebaseProtection", {}).get("enabled") else {}
    )
    cast = {
        folder: core for folder, core in cores.items()
        if core.get("side") == "Prospects"
        and categories[core.get("category", _category(folder))]["identityProtectedByDefault"]
    }
    cast_vectors = {folder: _unit(core["vector"]) for folder, core in cast.items()}
    by_id = {row["photoId"]: row for row in candidates if row.get("photoId")}
    vectors = {}
    for photo_id, row in by_id.items():
        vector = _unit(row.get("vector"))
        if vector is not None and row.get("side") == "Prospects":
            vectors[photo_id] = vector
    locked = set(locked_ids) | {
        photo_id for photo_id, row in by_id.items()
        if row.get("rejectedPersonIds") or row.get("rejectionMetadataStale")
    }

    clusters = {group["destination"]: group for group in result["clusters"]}
    assignments = {row["photoId"]: row for row in result["assignments"]}
    members = {folder: set(group["photoIds"]) for folder, group in clusters.items()}
    held = {}
    for row in result["held"]:
        photo_id = row.get("photoId")
        if (
            photo_id in vectors and photo_id not in locked and not row.get("preserveStaged")
            and not row.get("reviewDestination") and photo_id not in held
        ):
            held[photo_id] = row
    visited = {photo_id: {folder} for folder, ids in members.items() for photo_id in ids}
    for photo_id in held:
        visited.setdefault(photo_id, set()).add("Various/review")
    frozen, unresolved, passes = set(), [], []
    stop_reason = "stable"

    def core_of(folder):
        rows = [{"photoId": photo_id, "vector": vectors[photo_id]} for photo_id in sorted(members[folder])
                if photo_id in vectors]
        if not rows:
            return None, set()
        vector, indices = _core(rows, orange)
        return _unit(vector), {rows[index]["photoId"] for index in indices}

    def note(photo_id, kind, detail, pass_number):
        unresolved.append({"pass": pass_number, "photoId": photo_id, "kind": kind, "detail": detail})

    for pass_number in range(1, max_passes + 1):
        references = {}
        for folder in sorted(members):
            vector, _ = core_of(folder)
            if vector is not None:
                references[folder] = vector
        moves = []
        for folder in sorted(members):
            for photo_id in sorted(members[folder]):
                if photo_id not in vectors or photo_id in frozen:
                    continue
                vector = vectors[photo_id]
                others = [vectors[other] for other in members[folder] if other != photo_id and other in vectors]
                own_vector = _unit(np.mean(others, axis=0)) if others else None
                own = float(vector @ own_vector) if own_vector is not None else None
                minimum = minima.get(_category(folder))
                if own is not None and minimum is not None and own >= minimum:
                    continue
                rival_refs = {**{k: v for k, v in references.items() if k != folder}, **cast_vectors}
                excluded = excluded_folders([by_id[photo_id]], cast)
                ranked = _ranked(vector, rival_refs, excluded)
                if not ranked:
                    continue
                best, target = ranked[0]
                lead = min(
                    best - (own if own is not None else -1.),
                    best - ranked[1][0] if len(ranked) > 1 else 2.,
                )
                if lead <= 0:
                    continue
                if target in cast:
                    rules = categories[cast[target].get("category", _category(target))]
                    accepted = (
                        rules["reviewAdmissionEnabled"] and best >= routing["reviewMinimum"]
                        and best >= rules["photoRouteMinimum"] and lead >= rules["photoRouteMargin"]
                    )
                    destination = f"{target}/review"
                else:
                    accepted = evaluate_photo_route(
                        _category(target), score=best, margin=min(lead, 2.), policy=policy, propose=True,
                    )["decision"] == "auto-route"
                    destination = target
                if not accepted:
                    continue
                if photo_id in locked:
                    note(photo_id, "locked", f"fits {target} better but is protected, anchored, "
                         "workflow-selected or carries rejection history", pass_number)
                    frozen.add(photo_id)
                    continue
                if destination in visited[photo_id]:
                    note(photo_id, "oscillation", f"would return to {destination}", pass_number)
                    frozen.add(photo_id)
                    continue
                moves.append({
                    "photoId": photo_id, "kind": "photo-move", "from": folder, "to": destination,
                    "ownScore": round(own, 6) if own is not None else None,
                    "rivalScore": round(best, 6), "lead": round(lead, 6),
                })
        for photo_id in sorted(held):
            if photo_id in frozen:
                continue
            ranked = _ranked(vectors[photo_id], {**references, **cast_vectors},
                             excluded_folders([by_id[photo_id]], cast))
            if not ranked or ranked[0][1] in cast:
                continue
            best, target = ranked[0]
            lead = best - ranked[1][0] if len(ranked) > 1 else 2.
            if lead <= 0 or evaluate_photo_route(
                _category(target), score=best, margin=min(lead, 2.), policy=policy, propose=True,
            )["decision"] != "auto-route":
                continue
            if target in visited[photo_id]:
                note(photo_id, "oscillation", f"would return to {target}", pass_number)
                frozen.add(photo_id)
                continue
            moves.append({
                "photoId": photo_id, "kind": "review-attach", "from": "Various/review", "to": target,
                "ownScore": None, "rivalScore": round(best, 6), "lead": round(lead, 6),
            })

        for move in moves:
            photo_id = move["photoId"]
            visited[photo_id].add(move["to"])
            step = {"pass": pass_number, **{k: v for k, v in move.items() if k != "photoId"}}
            if move["kind"] == "review-attach":
                row = held.pop(photo_id)
                result["held"].remove(row)
                row = {key: value for key, value in row.items() if key not in ("reviewDestination",
                                                                              "reviewAlternatives")}
                row.update(destination=move["to"], destinationType="provisional")
                assignments[photo_id] = row
                result["assignments"].append(row)
                members[move["to"]].add(photo_id)
            else:
                members[move["from"]].discard(photo_id)
                row = assignments[photo_id]
                if move["to"].endswith("/review"):
                    result["assignments"].remove(row)
                    del assignments[photo_id]
                    row = {key: value for key, value in row.items() if key not in ("destination",
                                                                                  "destinationType")}
                    row["reviewDestination"] = move["to"]
                    result["held"].append(row)
                else:
                    row["destination"] = move["to"]
                    members[move["to"]].add(photo_id)
            row["reason"] = (
                f"{row['reason']}; refinement pass {pass_number}: {move['kind']} "
                f"{move['from']} -> {move['to']} ({move['rivalScore']:.3f})"
            )
            row.setdefault("refinement", []).append(step)

        merges = []
        live = {}
        for folder in sorted(members):
            vector, _ = core_of(folder)
            if vector is not None:
                live[folder] = vector
        best_of = {}
        for folder, vector in live.items():
            ranked = _ranked(vector, {k: v for k, v in live.items() if k != folder})
            best_of[folder] = ranked
        used = set()
        pairs = sorted(
            {tuple(sorted((folder, ranked[0][1]))) for folder, ranked in best_of.items()
             if ranked and best_of.get(ranked[0][1]) and best_of[ranked[0][1]][0][1] == folder},
            key=lambda pair: (-float(live[pair[0]] @ live[pair[1]]), pair),
        )
        for left, right in pairs:
            if left in used or right in used:
                continue
            survivor, loser = sorted(
                (left, right), key=lambda folder: (-len(members[folder]), folder.casefold()),
            )
            rules = categories[_category(survivor)]
            similarity = float(live[left] @ live[right])
            competitors = [
                ranked[1][0] for ranked in (best_of[left], best_of[right]) if len(ranked) > 1
            ] + [
                score for score, _ in (
                    _ranked(live[loser], cast_vectors)[:1] + _ranked(live[survivor], cast_vectors)[:1]
                )
            ]
            lead = similarity - max(competitors, default=-1.)
            loser_ids = sorted(members[loser])
            reasons = []
            if similarity < rules["mergeMinimum"] or lead < rules["photoRouteMargin"]:
                continue
            if any(photo_id in locked for photo_id in loser_ids):
                reasons.append("locked or rejection-history photo")
            if any(float(vectors[photo_id] @ live[survivor]) < rules["photoRouteMinimum"]
                   for photo_id in loser_ids if photo_id in vectors):
                reasons.append("a member falls below the survivor's route minimum")
            if reasons:
                unresolved.append({
                    "pass": pass_number, "kind": "merge-refused", "survivor": survivor, "loser": loser,
                    "similarity": round(similarity, 6), "detail": "; ".join(reasons),
                })
                continue
            used.update((left, right))
            merges.append({
                "kind": "identity-merge", "survivor": survivor, "loser": loser,
                "similarity": round(similarity, 6), "lead": round(lead, 6), "photoCount": len(loser_ids),
            })
            for photo_id in loser_ids:
                row = assignments[photo_id]
                row["destination"] = survivor
                row["reason"] = (
                    f"{row['reason']}; refinement pass {pass_number}: identity merge {loser} -> {survivor} "
                    f"({similarity:.3f})"
                )
                row.setdefault("refinement", []).append({
                    "pass": pass_number, "kind": "identity-merge", "from": loser, "to": survivor,
                    "similarity": round(similarity, 6),
                })
                visited[photo_id].add(survivor)
            members[survivor].update(members.pop(loser))
            clusters[survivor].setdefault("mergedClusterIds", []).append(clusters.pop(loser)["clusterId"])

        dissolved, renamed = [], {}
        changed = {move["from"] for move in moves} | {move["to"] for move in moves} | {
            merge["survivor"] for merge in merges
        }
        for folder in sorted(changed & set(members)):
            if not members[folder]:
                del members[folder]
                clusters.pop(folder, None)
                dissolved.append({"folder": folder, "reason": "no members remain"})
                continue
            vector, core_ids = core_of(folder)
            if vector is None:
                continue
            rows = [by_id[photo_id] for photo_id in members[folder]]
            ranked = _ranked(vector, cast_vectors, excluded_folders(rows, cast))
            classification = classify_category(
                len(rows), ranked[0][0] if ranked else None, policy,
                best_cast_folder=ranked[0][1] if ranked else None,
                second_cast_folder=ranked[1][1] if len(ranked) > 1 else None,
                cast_margin=min(ranked[0][0] - ranked[1][0], 2.) if len(ranked) > 1 else 2.,
            )
            group = clusters[folder]
            if classification["category"] in (None, "Review"):
                for photo_id in sorted(members.pop(folder)):
                    row = assignments.pop(photo_id)
                    result["assignments"].remove(row)
                    row = {key: value for key, value in row.items()
                           if key not in ("destination", "destinationType")}
                    row["reviewDestination"] = classification["reviewDestination"]
                    row["reason"] += f"; refinement pass {pass_number}: identity dissolved ({classification['reason']})"
                    row.setdefault("refinement", []).append({
                        "pass": pass_number, "kind": "identity-dissolved", "from": folder,
                        "to": classification["reviewDestination"] or "Various/review",
                    })
                    result["held"].append(row)
                clusters.pop(folder)
                dissolved.append({"folder": folder, "reason": classification["reason"]})
                continue
            group["photoIds"] = sorted(members[folder])
            group["corePhotoIds"] = sorted(core_ids)
            target = f"{classification['category']}/{folder.split('/', 1)[1]}"
            if target != folder:
                renamed[folder] = target
        for folder, target in sorted(renamed.items()):
            group = clusters.pop(folder)
            group["destination"] = target
            group["reason"] += f"; refinement pass {pass_number}: reclassified {folder} -> {target}"
            clusters[target] = group
            members[target] = members.pop(folder)
            for photo_id in members[target]:
                assignments[photo_id]["destination"] = target
                visited[photo_id].add(target)
        passes.append({
            "pass": pass_number, "moves": moves, "merges": merges, "dissolved": dissolved,
            "reclassified": [{"from": k, "to": v} for k, v in sorted(renamed.items())],
        })
        if not moves and not merges and not dissolved and not renamed:
            break
        if pass_number == max_passes:
            stop_reason = "pass-limit"
    result["clusters"] = sorted(clusters.values(), key=lambda group: group["destination"])
    evidence = {
        "schemaVersion": 1, "maxPasses": max_passes, "passCount": len(passes),
        "stopReason": stop_reason,
        "moveCount": sum(len(item["moves"]) for item in passes),
        "mergeCount": sum(len(item["merges"]) for item in passes),
        "dissolvedCount": sum(len(item["dissolved"]) for item in passes),
        "passes": passes, "unresolved": unresolved,
    }
    return result, evidence
