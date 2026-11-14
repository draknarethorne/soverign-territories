#!/usr/bin/env python3
"""Strict, read-only ingestion of human review feedback for a likeness review packet.

Pure dict-in / dict-out: no file I/O and no mutation of the inputs. Labels are evidence about
photo pairs only; no pair labels or identity components are inferred beyond what a human stated.
"""
import copy
import hashlib
import json

LABELS = ("same", "different", "uncertain")
RESIDUE_NOTE = "temporary ui verification"


def packet_digest(packet):
    body = {key: value for key, value in packet.items() if key != "packetSHA256"}
    text = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _keys(value, expected, where):
    _require(isinstance(value, dict), f"{where} must be an object.")
    extra, missing = sorted(set(value) - set(expected)), sorted(set(expected) - set(value))
    _require(not missing, f"{where} is missing {missing}.")
    _require(not extra, f"{where} has unexpected fields {extra}.")


def _string(value, where):
    _require(isinstance(value, str) and value.strip(), f"{where} must be a non-empty string.")
    return value


def _pair_key(a, b):
    return (a, b) if a <= b else (b, a)


def _case_references(case):
    refs = []
    for panel in case["panels"]:
        for ref in panel["references"]:
            if ref["photoId"] not in refs:
                refs.append(ref["photoId"])
    return refs


def _check_packet(packet):
    _require(isinstance(packet, dict), "Packet must be an object.")
    _require(packet.get("schemaVersion") == 1, "Packet schemaVersion must be 1.")
    digest = packet.get("packetSHA256")
    _require(isinstance(digest, str) and digest, "Packet is missing packetSHA256.")
    _require(digest == packet_digest(packet), "Packet packetSHA256 does not match its canonical content.")
    cases = packet.get("cases")
    _require(isinstance(cases, list) and cases, "Packet cases must be a non-empty list.")
    expected, pairs = {}, set()
    for case in cases:
        _require(isinstance(case, dict), "Packet case must be an object.")
        case_id = _string(case.get("id"), "Packet case id")
        _require(case_id not in expected, f"Packet repeats case {case_id}.")
        photo = _string(case.get("photoId"), f"Packet case {case_id} photoId")
        _require(isinstance(case.get("panels"), list), f"Packet case {case_id} panels must be a list.")
        refs = _case_references(case)
        _require(refs, f"Packet case {case_id} has no references.")
        _require(photo not in refs, f"Packet case {case_id} references its own photo {photo}.")
        expected[case_id] = {"photoId": photo, "references": refs}
        pairs.update(_pair_key(photo, ref) for ref in refs)
    return digest, expected, pairs


def _observations(digest, packet, expected, feedback):
    _keys(feedback, ("schemaVersion", "packetSHA256", "binding", "decisions"), "Feedback")
    _require(feedback["schemaVersion"] == 1, "Feedback schemaVersion must be 1.")
    _require(feedback["packetSHA256"] == digest, "Feedback belongs to a different packet (packetSHA256).")
    _require(feedback["binding"] == packet.get("binding"), "Feedback binding differs from the packet binding.")
    decisions = feedback["decisions"]
    _require(isinstance(decisions, list), "Feedback decisions must be a list.")
    seen, rows, notes, excluded = set(), [], [], 0
    for entry in decisions:
        _require(isinstance(entry, dict), "Feedback decision must be an object.")
        case_id = entry.get("caseId")
        _require(case_id in expected, f"Feedback names unknown case {case_id!r}.")
        _require(case_id not in seen, f"Feedback repeats case {case_id}.")
        seen.add(case_id)
        _keys(entry, ("caseId", "photoId", "pairs", "note"), f"Feedback case {case_id}")
        case = expected[case_id]
        _require(entry["photoId"] == case["photoId"], f"Feedback case {case_id} photoId differs from the packet.")
        _require(isinstance(entry["note"], str), f"Feedback case {case_id} note must be a string.")
        _require(isinstance(entry["pairs"], list), f"Feedback case {case_id} pairs must be a list.")
        refs_seen = set()
        for pair in entry["pairs"]:
            _keys(pair, ("referencePhotoId", "label"), f"Feedback case {case_id} pair")
            ref, label = pair["referencePhotoId"], pair["label"]
            _require(ref in case["references"], f"Feedback case {case_id} has unknown reference {ref!r}.")
            _require(ref not in refs_seen, f"Feedback case {case_id} repeats reference {ref}.")
            refs_seen.add(ref)
            _require(label != "unreviewed", f"Feedback case {case_id} reference {ref} is unreviewed.")
            _require(label in LABELS, f"Feedback case {case_id} reference {ref} has invalid label {label!r}.")
            rows.append({"caseId": case_id, "photoId": case["photoId"], "referencePhotoId": ref,
                         "rawLabel": label, "label": label})
        missing = [ref for ref in case["references"] if ref not in refs_seen]
        _require(not missing, f"Feedback case {case_id} is missing references {missing}.")
        note = entry["note"].strip()
        if not note:
            continue
        if RESIDUE_NOTE in note.lower():
            excluded += 1
        else:
            notes.append({"caseId": case_id, "photoId": case["photoId"], "note": note})
    missing_cases = [case_id for case_id in expected if case_id not in seen]
    _require(not missing_cases, f"Feedback is missing cases {missing_cases}.")
    return rows, notes, excluded


def _overrides(digest, packet_pairs, clarifications):
    if not clarifications:
        return {}
    _keys(clarifications, ("schemaVersion", "packetSHA256", "overrides"), "Clarifications")
    _require(clarifications["schemaVersion"] == 1, "Clarifications schemaVersion must be 1.")
    _require(clarifications["packetSHA256"] == digest, "Clarifications belong to a different packet (packetSHA256).")
    _require(isinstance(clarifications["overrides"], list), "Clarification overrides must be a list.")
    result = {}
    for item in clarifications["overrides"]:
        _keys(item, ("photoIds", "label", "source"), "Clarification override")
        ids = item["photoIds"]
        _require(isinstance(ids, list) and len(ids) == 2 and all(isinstance(i, str) and i for i in ids)
                 and ids[0] != ids[1], "Clarification photoIds must be exactly two distinct photo IDs.")
        key = _pair_key(*ids)
        _require(key in packet_pairs, f"Clarification pair {list(key)} is not a pair in the packet.")
        _require(key not in result, f"Clarifications repeat pair {list(key)}.")
        _require(item["label"] in LABELS, f"Clarification for {list(key)} has invalid label {item['label']!r}.")
        result[key] = {"label": item["label"], "source": _string(item["source"], f"Clarification source for {list(key)}")}
    return result


def _same_path(edges, start, goal):
    adjacency = {}
    for a, b in edges:
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, []).append(a)
    previous, queue = {start: None}, [start]
    for node in queue:
        for other in sorted(adjacency.get(node, [])):
            if other not in previous:
                previous[other] = node
                queue.append(other)
    if goal not in previous:
        return None
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = previous[node]
    return path[::-1]


def ingest(packet, feedback, clarifications):
    """Validate feedback against a packet and return normalised observations and pair labels."""
    packet, feedback, clarifications = (copy.deepcopy(x) for x in (packet, feedback, clarifications))
    digest, expected, packet_pairs = _check_packet(packet)
    rows, notes, excluded = _observations(digest, packet, expected, feedback)
    overrides = _overrides(digest, packet_pairs, clarifications)

    grouped = {}
    for row in rows:
        grouped.setdefault(_pair_key(row["photoId"], row["referencePhotoId"]), []).append(row)
    pairs, mixed = [], 0
    for key in sorted(grouped):
        observed = grouped[key]
        labels = {row["label"] for row in observed}
        override = overrides.get(key)
        if override:
            label = override["label"]
        elif {"same", "different"} <= labels:
            cases = sorted(f"{row['caseId']}={row['label']}" for row in observed)
            raise ValueError(f"Conflicting definite labels for pair {list(key)}: {cases}; a clarification is required.")
        elif len(labels) > 1:
            label = "uncertain"
            mixed += 1
        else:
            label = next(iter(labels))
        entry = {"photoIds": list(key), "label": label, "observations": copy.deepcopy(observed)}
        if override:
            entry["override"] = {"label": override["label"], "source": override["source"]}
        pairs.append(entry)

    same = [tuple(p["photoIds"]) for p in pairs if p["label"] == "same"]
    for pair in pairs:
        if pair["label"] != "different":
            continue
        a, b = pair["photoIds"]
        path = _same_path(same, a, b)
        if path:
            raise ValueError(f"Contradiction: {a} and {b} are labelled different but connected as same via {path}.")

    counts = {label: sum(p["label"] == label for p in pairs) for label in LABELS}
    return {
        "schemaVersion": 1, "packetSHA256": digest, "binding": copy.deepcopy(packet.get("binding")),
        "observations": rows, "pairs": pairs, "notes": notes,
        "summary": {
            "caseCount": len(expected), "observationCount": len(rows), "pairCount": len(pairs),
            "labelCounts": counts,
            "repeatedPairCount": sum(len(p["observations"]) > 1 for p in pairs),
            "mixedUncertainPairCount": mixed,
            "overrideCount": len(overrides), "overriddenPairCount": sum("override" in p for p in pairs),
            "noteCount": len(notes), "excludedNoteCount": excluded,
            "independentEvidence": False,
        },
    }
