"""Numeric-threshold family trees for rebased identities.

Family surnames are human-facing presentation only and are never matching evidence.
An identity joins the family of its closest Angel/Sister when that score reaches the
inclusive direct threshold; otherwise it links to its closest other identity strictly
above the secondary threshold. Score colours do not control membership.
Connected links form one family whose surname comes from the cast root
(configured override, then recorded person name) or, failing that, the oldest member.
Surnames are exclusive: Angel/Sister families claim theirs first, then other families and lone
identities by age; an identity whose surname another family owns gets a fresh unused surname.
"""
import collections
import hashlib
import uuid

import numpy as np

from . import identity_names

BAND_ORDER = ("green", "yellow", "orange")


def settings(policy):
    config = policy.get("familyNaming") or {}
    return {
        "enabled": bool(config.get("enabled", False)),
        "directCastMinimumSimilarity": float(config.get("directCastMinimumSimilarity", .4)),
        "secondaryMinimumSimilarityExclusive": float(config.get("secondaryMinimumSimilarityExclusive", .35)),
        "overrides": dict(config.get("castSurnameOverrides", {})),
    }


def band_of(score, policy):
    bands = policy["scoreBands"]
    for label in BAND_ORDER:
        if score >= bands[label]["minimum"]:
            return label
    return "red"


def surname_of(name):
    return name.split()[-1] if identity_names.is_full_person_name(name) else None


def centroid(vectors):
    value = np.mean(np.asarray(vectors, dtype=float), axis=0)
    norm = float(np.linalg.norm(value))
    return value / norm if norm else value


def family_id(root):
    return "family_" + uuid.uuid5(uuid.NAMESPACE_URL, "likeness-family-tree:" + root.casefold()).hex


def _age_key(member):
    """Oldest first: verified creation date, retained original name, larger identity, name."""
    date = member.get("ageDate")
    return (date is None, date or "", not member.get("retained"), -member.get("photoCount", 0),
            member["name"].casefold())


def _rotated(seed, pool):
    pool = list(pool)
    if not pool:
        return []
    start = int(hashlib.sha1(seed.encode("utf-8")).hexdigest(), 16) % len(pool)
    return pool[start:] + pool[:start]


def _fresh_surname(seed, taken, pool):
    return next((name for name in _rotated("surname:" + seed, pool) if name.casefold() not in taken), None)


def _fresh_first_name(seed, surname, used, pool):
    return next((f"{first} {surname}" for first in _rotated("first:" + seed, pool)
                 if f"{first} {surname}".casefold() not in used), None)


def plan(identities, cast, policy, *, reserved=(), surnames=(), first_names=()):
    """Return ({identity key: new name}, evidence) for one frozen final membership.

    identities: {key: {"name", "vector", "photoCount", "ageDate", "retained"}}
    cast: {folder: {"vector", "personName"}} for fixed Angels/Sisters slots.
    surnames/first_names: pools for fresh names when a surname belongs to another family or a name is taken.
    """
    config = settings(policy)
    direct_minimum = config["directCastMinimumSimilarity"]
    secondary_minimum = config["secondaryMinimumSimilarityExclusive"]
    parents = {}
    for key in sorted(identities, key=str.casefold):
        vector = identities[key]["vector"]
        ranked_cast = sorted(
            ((float(vector @ entry["vector"]), folder) for folder, entry in cast.items()),
            key=lambda row: (-row[0], row[1].casefold()),
        )
        if ranked_cast and ranked_cast[0][0] >= direct_minimum:
            score, target = ranked_cast[0]
            parents[key] = {"tier": "cast", "to": target, "score": score}
            continue
        ranked_peers = sorted(
            ((float(vector @ other["vector"]), other_key)
             for other_key, other in identities.items() if other_key != key),
            key=lambda row: (-row[0], row[1].casefold()),
        )
        if ranked_peers and ranked_peers[0][0] > secondary_minimum:
            score, target = ranked_peers[0]
            parents[key] = {"tier": "identity", "to": target, "score": score}

    leader = {}

    def find(node):
        leader.setdefault(node, node)
        while leader[node] != node:
            leader[node] = leader[leader[node]]
            node = leader[node]
        return node

    for key, link in parents.items():
        a, b = find(key), find(link["to"])
        if a != b:
            # Keep a cast slot as the representative so each tree has a visible root.
            if a in cast:
                leader[b] = a
            else:
                leader[a] = b
    components = collections.defaultdict(list)
    for key in identities:
        components[find(key)].append(key)
    for folder in cast:
        components.setdefault(find(folder), [])

    def path(key):
        steps, seen = [], {key}
        node = key
        while node in parents:
            link = parents[node]
            steps.append({"from": node, "to": link["to"], "score": link["score"],
                          "band": band_of(link["score"], policy), "tier": link["tier"]})
            node = link["to"]
            if node in cast or node in seen:
                break
            seen.add(node)
        return steps

    used = {identities[key]["name"].casefold() for key in identities}
    used |= {name.casefold() for name in reserved if name}
    used |= {entry["personName"].casefold() for entry in cast.values() if entry.get("personName")}
    overrides = {key.casefold(): value for key, value in config["overrides"].items()}
    groups = []
    for root, members in components.items():
        root_cast = root if root in cast else None
        ordered = sorted(members, key=lambda key: _age_key(identities[key]))
        preferred = []
        if root_cast:
            if overrides.get(root_cast.casefold()):
                preferred.append((overrides[root_cast.casefold()], "configured"))
            recorded = surname_of(cast[root_cast].get("personName") or "")
            if recorded:
                preferred.append((recorded, "recorded person name"))
        for index, key in enumerate(ordered):
            own = surname_of(identities[key]["name"])
            if own:
                if not root_cast and len(ordered) == 1:
                    label = "own surname"
                elif index == 0:
                    label = "adopted from oldest family member " + identities[key]["name"]
                else:
                    label = ("adopted from family member " + identities[key]["name"]
                             + "; older surnames belong to other families")
                preferred.append((own, label))
        if preferred:
            priority = (0, root.casefold()) if root_cast else (1, _age_key(identities[ordered[0]]), root.casefold())
            groups.append({"root": root, "cast": root_cast, "ordered": ordered, "preferred": preferred,
                           "priority": priority})
    # Every surname anywhere in the frozen roster; a fresh surname must be new to all of them.
    held = {surname_of(name).casefold() for name in used if surname_of(name)}
    held |= {value.casefold() for value in overrides.values()}
    owned, allocated = {}, {}
    for group in sorted(groups, key=lambda item: item["priority"]):
        choice = next(((name, label) for name, label in group["preferred"] if name.casefold() not in owned), None)
        displaced = None
        if choice is None:
            wanted = group["preferred"][0][0]
            displaced = {"surname": wanted, "owner": owned[wanted.casefold()]}
            fresh = _fresh_surname(group["root"], held | set(owned), surnames)
            if fresh is None:
                choice = (wanted, "shared: no unused surname available")
            else:
                choice = (fresh, f"fresh surname; {wanted} belongs to the family of {displaced['owner']}")
                held.add(fresh.casefold())
        owned.setdefault(choice[0].casefold(), group["root"])
        allocated[group["root"]] = (choice[0], choice[1], displaced)

    renames, families, cast_evidence = {}, [], {}
    for group in sorted(groups, key=lambda item: item["root"].casefold()):
        root_cast, ordered = group["cast"], group["ordered"]
        surname, source, displaced = allocated[group["root"]]
        if not root_cast and len(ordered) < 2 and displaced is None:
            continue
        reference = root_cast or ordered[0]
        rows = []
        for key in ordered:
            current = identities[key]["name"]
            proposed = " ".join(current.split()[:-1] + [surname]) if surname_of(current) else current
            status = "unchanged"
            if proposed.casefold() != current.casefold():
                if proposed.casefold() in used:
                    alternative = _fresh_first_name(key, surname, used, first_names)
                    if alternative is None:
                        status, proposed = "collision kept previous name", current
                    else:
                        used.discard(current.casefold())
                        used.add(alternative.casefold())
                        renames[key] = proposed = alternative
                        status = "renamed (first name changed to avoid an existing name)"
                else:
                    used.discard(current.casefold())
                    used.add(proposed.casefold())
                    renames[key] = proposed
                    status = "renamed"
            link = parents.get(key)
            rows.append({
                "identity": key, "name": proposed, "previousName": current, "status": status,
                "parent": link["to"] if link else None, "tier": link["tier"] if link else "root",
                "score": link["score"] if link else None,
                "band": band_of(link["score"], policy) if link else None,
                "path": path(key),
            })
        family = {
            "id": family_id(reference), "root": reference, "rootKind": "cast" if root_cast else "identity",
            "surname": surname, "surnameSource": source, "members": rows,
        }
        if displaced:
            family["displacedFrom"] = displaced
        families.append(family)
        if root_cast:
            person_name = cast[root_cast].get("personName")
            base = person_name or root_cast.rsplit("/", 1)[-1]
            # A cast name without a surname adopts the family surname upward.
            current_person = (
                " ".join(base.split()[:-1] + [surname]) if surname_of(base) else f"{base} {surname}"
            )
            cast_evidence[root_cast] = {
                "familyId": family["id"], "surname": surname, "surnameSource": source,
                "recordedPersonName": person_name, "currentPersonName": current_person,
                "memberCount": len(rows),
            }
    evidence = {
        "enabled": True,
        "directCastMinimumSimilarity": direct_minimum,
        "secondaryMinimumSimilarityExclusive": secondary_minimum,
        # Retained for older log/report readers; numeric fields above define both link rules.
        "linkBand": band_of(direct_minimum, policy), "linkMinimum": direct_minimum,
        "rule": (f"closest Angel/Sister at similarity >= {direct_minimum:g}, otherwise closest other identity "
                 f"at similarity > {secondary_minimum:g}; every chain edge must qualify. "
                 "Score colours do not control membership; connected links share the cast root's surname "
                 "(configured, then recorded) "
                 "or the oldest member's surname. Each surname belongs to one family: Angel/Sister families claim "
                 "first, then the oldest; anyone else holding a claimed surname gets a fresh unused one. "
                 "Presentation only, never matching evidence."),
        "families": families, "cast": cast_evidence,
        "linkedIdentityCount": len(parents), "renamedIdentityCount": len(renames),
        "displacedFamilyCount": sum(1 for family in families if family.get("displacedFrom")),
        "unlinkedIdentityCount": sum(1 for key in identities if key not in parents and not any(
            link["to"] == key for link in parents.values())),
    }
    return renames, evidence
