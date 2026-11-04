"""Score-band family trees for rebased identities.

Family surnames are human-facing presentation only and are never matching evidence.
An identity joins the family of its closest Angel/Sister when that score reaches the
configured band (yellow by default); otherwise it links to its closest other identity
in that band. Connected links form one family whose surname comes from the cast root
(configured override, then recorded person name) or, failing that, the oldest member.
"""
import collections
import uuid

import numpy as np

from . import identity_names

BAND_ORDER = ("green", "yellow", "orange")


def settings(policy):
    config = policy.get("familyNaming") or {}
    band = config.get("linkMinimumBand", "yellow")
    return {
        "enabled": bool(config.get("enabled", False)),
        "band": band,
        "minimum": float(policy["scoreBands"][band]["minimum"]),
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


def plan(identities, cast, policy, *, reserved=()):
    """Return ({identity key: new name}, evidence) for one frozen final membership.

    identities: {key: {"name", "vector", "photoCount", "ageDate", "retained"}}
    cast: {folder: {"vector", "personName"}} for fixed Angels/Sisters slots.
    """
    config = settings(policy)
    minimum = config["minimum"]
    parents = {}
    for key in sorted(identities, key=str.casefold):
        vector = identities[key]["vector"]
        ranked_cast = sorted(
            ((float(vector @ entry["vector"]), folder) for folder, entry in cast.items()),
            key=lambda row: (-row[0], row[1].casefold()),
        )
        if ranked_cast and ranked_cast[0][0] >= minimum:
            score, target = ranked_cast[0]
            parents[key] = {"tier": "cast", "to": target, "score": score}
            continue
        ranked_peers = sorted(
            ((float(vector @ other["vector"]), other_key)
             for other_key, other in identities.items() if other_key != key),
            key=lambda row: (-row[0], row[1].casefold()),
        )
        if ranked_peers and ranked_peers[0][0] >= minimum:
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
            steps.append({"from": node, "to": link["to"], "score": round(link["score"], 6),
                          "band": band_of(link["score"], policy), "tier": link["tier"]})
            node = link["to"]
            if node in cast or node in seen:
                break
            seen.add(node)
        return steps

    used = {identities[key]["name"].casefold() for key in identities}
    used |= {name.casefold() for name in reserved if name}
    used |= {entry["personName"].casefold() for entry in cast.values() if entry.get("personName")}
    renames, families, cast_evidence = {}, [], {}
    for root, members in sorted(components.items(), key=lambda item: item[0].casefold()):
        root_cast = root if root in cast else None
        ordered = sorted(members, key=lambda key: _age_key(identities[key]))
        if not root_cast and len(ordered) < 2:
            continue
        surname, source = None, None
        if root_cast:
            override = {key.casefold(): value for key, value in config["overrides"].items()}.get(root_cast.casefold())
            recorded = surname_of(cast[root_cast].get("personName") or "")
            if override:
                surname, source = override, "configured"
            elif recorded:
                surname, source = recorded, "recorded person name"
        if not surname:
            for key in ordered:
                surname = surname_of(identities[key]["name"])
                if surname:
                    source = "adopted from oldest family member " + identities[key]["name"]
                    break
        if not surname:
            continue
        reference = root_cast or ordered[0]
        rows = []
        for key in ordered:
            current = identities[key]["name"]
            proposed = " ".join(current.split()[:-1] + [surname]) if surname_of(current) else current
            status = "unchanged"
            if proposed.casefold() != current.casefold():
                if proposed.casefold() in used:
                    status, proposed = "collision kept previous name", current
                else:
                    used.discard(current.casefold())
                    used.add(proposed.casefold())
                    renames[key] = proposed
                    status = "renamed"
            link = parents.get(key)
            rows.append({
                "identity": key, "name": proposed, "previousName": current, "status": status,
                "parent": link["to"] if link else None, "tier": link["tier"] if link else "root",
                "score": round(link["score"], 6) if link else None,
                "band": band_of(link["score"], policy) if link else None,
                "path": path(key),
            })
        family = {
            "id": family_id(reference), "root": reference, "rootKind": "cast" if root_cast else "identity",
            "surname": surname, "surnameSource": source, "members": rows,
        }
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
        "enabled": True, "linkBand": config["band"], "linkMinimum": minimum,
        "rule": ("closest Angel/Sister at or above the link band, otherwise closest other identity at or "
                 "above it; connected links share the cast root's surname (configured, then recorded) "
                 "or the oldest member's surname. Presentation only, never matching evidence."),
        "families": families, "cast": cast_evidence,
        "linkedIdentityCount": len(parents), "renamedIdentityCount": len(renames),
        "unlinkedIdentityCount": sum(1 for key in identities if key not in parents and not any(
            link["to"] == key for link in parents.values())),
    }
    return renames, evidence
