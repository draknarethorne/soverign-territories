"""Direct, reversible family-name proposals from frozen identity evidence."""
import copy
import pathlib
import uuid

from . import identity_names, metadata
from .identity_maintenance import independent_count


def augment_actions(actions, space, cores, catalog, policy, root, *, changed_folders=()):
    """Compose name/family patches with protection without two writes to one person."""
    overlay = copy.deepcopy(catalog)
    combined = copy.deepcopy(actions)
    by_person = {}
    for action in combined:
        collection, key = ("people", action["personId"]) if "personId" in action else ("photos", action["photoId"])
        overlay[collection][key] = copy.deepcopy(action["after"])
        if collection == "people":
            by_person[key] = action
    families, diagnostics = plan(space, cores, overlay, policy, root, changed_folders=changed_folders)
    for action in families:
        prior = by_person.get(action["personId"])
        if prior:
            prior["after"] = action["after"]
            prior["reason"] += "; " + action["reason"]
            prior.setdefault("sourceChecks", []).extend(action["sourceChecks"])
        else:
            combined.append(action)
    return combined, diagnostics


def plan(space, cores, catalog, policy, root, *, changed_folders=()):
    """Return person snapshots; never rename folders or use names as matching inputs."""
    import people as person_files

    root = pathlib.Path(root).resolve()
    rules = policy["lookalikeGroups"]
    people = catalog["people"]
    changed = set(changed_folders)
    proposals, diagnostics = [], []
    eligible, names_by_id, checks_by_id = {}, {}, {}
    folder_counts = {}
    photo_counts = {}
    for person in people.values():
        folder_counts[person["folder"].casefold()] = folder_counts.get(person["folder"].casefold(), 0) + 1
    for photo in space.photos:
        key = metadata.photo_id_from_name(photo.name)
        photo_counts[key] = photo_counts.get(key, 0) + 1
    for pid, person in sorted(people.items()):
        folder = person["folder"]
        if person.get("mergedInto") or folder.startswith("Artists/") or folder in changed:
            continue
        if folder_counts[folder.casefold()] != 1:
            diagnostics.append({"personId": pid, "reason": "conflicting folder ownership"})
            continue
        names = identity_names.snapshot(person, pathlib.Path(root) / folder, catalog=catalog)
        if names:
            names_by_id[pid] = names
        history = person_files.find(root / folder)
        history_checks = (
            [{"source": history.relative_to(root).as_posix(), "sha256": metadata.content_sha256(history)}]
            if history else []
        )
        checks_by_id[pid] = history_checks
        core = cores.get(folder)
        if not core or not names:
            diagnostics.append({"personId": pid, "reason": "missing core or recorded name"})
            continue
        photos = [
            photo for photo in space.by_key.get(folder, [])
            if metadata.photo_id_from_name(photo.name) in core["corePhotoIds"]
            and photo.usable(space.st["minFace"]) and photo.path.parent.name == "gallery"
        ]
        support, checks = [], []
        invalid = False
        for photo in photos:
            photo_id = metadata.photo_id_from_name(photo.name)
            digest = metadata.content_sha256(photo.path)
            record = catalog["photos"].get(photo_id, {})
            if photo_counts.get(photo_id) != 1 or record.get("rejectedPersonIds") or (
                record and record.get("contentSha256") != digest
            ):
                invalid = True
                break
            support.append({"photoId": photo_id, "vector": photo.vec})
            checks.append({"source": photo.path.relative_to(root).as_posix(), "sha256": digest})
        checks_by_id[pid] = history_checks + checks
        if invalid or independent_count(support, policy) < rules.get("minimumIndependentPhotos", 5):
            diagnostics.append({"personId": pid, "reason": "insufficient independent, current core evidence"})
            continue
        eligible[pid] = core

    updates = {}
    for pid, names in names_by_id.items():
        if "names" not in people[pid]:
            updates[pid] = {**copy.deepcopy(people[pid]), "names": names}

    if rules["automaticAssociationEnabled"]:
        rankings = {}
        for pid, core in eligible.items():
            rankings[pid] = sorted(
                ((float(core["vector"] @ other["vector"]), other_id)
                 for other_id, other in eligible.items() if pid != other_id and core["side"] == other["side"]),
                key=lambda row: (-row[0], row[1]),
            )
        used = set()
        occupied = {
            identity_names.presentation(person, pathlib.Path(root) / person["folder"], catalog=catalog)["currentPersonName"].casefold(): pid
            for pid, person in people.items()
            if identity_names.presentation(person, pathlib.Path(root) / person["folder"], catalog=catalog)["currentPersonName"]
        }
        for pid in sorted(eligible, key=lambda key: (people[key]["folder"].casefold(), key)):
            ranked = rankings[pid]
            if pid in used or people[pid].get("family") or not ranked:
                continue
            score, other = ranked[0]
            reverse = rankings[other]
            if other in used or people[other].get("family") or not reverse or reverse[0][1] != pid:
                diagnostics.append({"personId": pid, "reason": "no unambiguous reciprocal family reference"})
                continue
            maximum = min(
                rules["associationMaximumSimilarityExclusive"],
                policy["categoryPolicies"][eligible[pid]["category"]]["mergeMinimum"],
                policy["categoryPolicies"][eligible[other]["category"]]["mergeMinimum"],
            )
            if not rules["associationMinimumSimilarity"] <= score < maximum or any(
                len(ranks) > 1 and ranks[0][0] - ranks[1][0] < rules["minimumReferenceMargin"]
                for ranks in (ranked, reverse)
            ):
                diagnostics.append({"personId": pid, "reason": "outside distinct-lookalike band or ambiguous reference"})
                continue
            pair = sorted((pid, other), key=lambda key: (
                people[key]["folder"].split("/")[0] not in ("Angels", "Sisters"),
                people[key]["folder"].casefold(), key,
            ))
            leader = pair[0]
            leader_name = names_by_id[leader]["currentName"]
            if len(leader_name.split()) < 2:
                diagnostics.append({"personId": pid, "reason": "reference name has no recorded surname"})
                continue
            surname = leader_name.rsplit(None, 1)[-1]
            proposed = {}
            for member in pair:
                current = names_by_id[member]["currentName"]
                if len(current.split()) < 2:
                    break
                proposed[member] = current.rsplit(None, 1)[0] + " " + surname
            if len(proposed) != 2 or len({name.casefold() for name in proposed.values()}) != 2 or any(
                occupied.get(name.casefold(), member) not in pair for member, name in proposed.items()
            ):
                diagnostics.append({"personId": pid, "reason": "missing full name or family-name collision"})
                continue
            family_id = "family_" + uuid.uuid5(uuid.NAMESPACE_URL, "likeness-family:" + leader).hex
            reason = (
                f"Direct reciprocal resemblance {score:.3f}; independent core support and rival margin passed "
                f"policy {policy['version']}. Organizational family, not confirmed kinship or same-person identity."
            )
            for member in pair:
                after = updates.setdefault(member, copy.deepcopy(people[member]))
                after["names"] = {**names_by_id[member], "currentName": proposed[member]}
                after["family"] = {
                    "id": family_id, "referencePersonId": leader, "surname": surname,
                    "score": score, "policyVersion": policy["version"],
                    "previousPersonName": names_by_id[member]["currentName"], "reason": reason,
                }
                occupied[proposed[member].casefold()] = member
                used.add(member)
            combined_checks = checks_by_id[pair[0]] + checks_by_id[pair[1]]
            for member in pair:
                checks_by_id[member] = list(combined_checks)

        leaders = {
            person["family"]["referencePersonId"]
            for person in people.values() if person.get("family")
        } & set(eligible)
        for pid in sorted(eligible):
            if pid in used or people[pid].get("family"):
                continue
            core = eligible[pid]
            ranked = sorted(
                ((float(core["vector"] @ eligible[leader]["vector"]), leader)
                 for leader in leaders if eligible[leader]["side"] == core["side"]),
                key=lambda row: (-row[0], row[1]),
            )
            if not ranked:
                continue
            score, leader = ranked[0]
            family = people[leader].get("family")
            if not family or family["referencePersonId"] != leader:
                continue
            maximum = min(
                rules["associationMaximumSimilarityExclusive"],
                policy["categoryPolicies"][core["category"]]["mergeMinimum"],
                policy["categoryPolicies"][eligible[leader]["category"]]["mergeMinimum"],
            )
            # A close same-person alternative anywhere still blocks a family join.
            if any(value >= maximum for value, _ in rankings[pid]) or (
                not rules["associationMinimumSimilarity"] <= score < maximum
                or (len(ranked) > 1 and score - ranked[1][0] < rules["minimumReferenceMargin"])
            ):
                diagnostics.append({"personId": pid, "reason": "family join ambiguous or possible same-person match"})
                continue
            current = names_by_id[pid]["currentName"]
            if len(current.split()) < 2:
                continue
            proposed = current.rsplit(None, 1)[0] + " " + family["surname"]
            if occupied.get(proposed.casefold(), pid) != pid:
                diagnostics.append({"personId": pid, "reason": "family-name collision"})
                continue
            after = updates.setdefault(pid, copy.deepcopy(people[pid]))
            after["names"] = {**names_by_id[pid], "currentName": proposed}
            after["family"] = {
                **family, "score": score, "policyVersion": policy["version"],
                "previousPersonName": current,
                "reason": f"Direct established-family reference {score:.3f}; not transitive kinship or identity evidence.",
            }
            checks_by_id[pid].extend(checks_by_id[leader])
            occupied[proposed.casefold()] = pid

    for pid, after in sorted(updates.items()):
        if after != people[pid]:
            proposals.append({
                "personId": pid, "before": copy.deepcopy(people[pid]), "after": after,
                "reason": after.get("family", {}).get("reason", "Preserve recorded original/current name provenance"),
                "sourceChecks": checks_by_id.get(pid, []),
            })
    return proposals, diagnostics
