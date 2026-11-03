"""Name provenance independent of cast slots, folder labels and face evidence."""
import copy
import base64
import datetime
import re


def is_full_person_name(value):
    """Return whether a non-slot display name has distinct first and last tokens."""
    if not isinstance(value, str):
        return False
    parts = value.split()
    return (
        len(parts) >= 2
        and all(re.fullmatch(r"[^\W_][\w'’-]*", part, re.UNICODE) for part in parts)
        and "/" not in value and "\\" not in value
    )


def snapshot(person, folder=None, *, catalog=None):
    """Read recorded history without guessing missing real-person names from cast keys."""
    import people

    if person and person.get("names"):
        return copy.deepcopy(person["names"])
    recorded = people.read(folder) if folder is not None else None
    current = recorded[0] if recorded else None
    category = (person or {}).get("folder", "").split("/", 1)[0]
    if not current and person and category not in ("Angels", "Sisters", "Various"):
        current = person["displayName"]
    if not current:
        return None
    original = current
    source = "recorded-history" if recorded else "catalogue-registration"
    if recorded:
        for line in recorded[1]:
            match = re.fullmatch(r"\d{4}-\d{2}-\d{2} (?:name swap with person_[0-9a-f]{32}: )?renamed from (.+) \((.+)\)", line)
            if match:
                original = match[1]
                source = "rename-history"
                break
    if catalog and person:
        for action in catalog.get("actions", []):
            for record in (action, action.get("swapPartner", {})):
                if record.get("personId") != person.get("id") or record.get("type") != "person-renamed":
                    continue
                prior = (record.get("beforeState", {}).get("person") or {}).get("names")
                if prior:
                    original, source = prior["originalName"], prior["originalSource"]
                else:
                    state = record.get("renameState", {})
                    old = base64.b64decode(state.get("oldHistoryBase64", ""), validate=True).decode("utf-8")
                    first = old.splitlines()[0] if old.splitlines() else ""
                    if first.lower().startswith("name:") and first[5:].strip():
                        original, source = first[5:].strip(), "rename-history"
                break
            else:
                continue
            break
    return {"originalName": original, "currentName": current, "originalSource": source}


def rebase_snapshot(person, folder, *, catalog=None):
    """Prefer a recorded full display name, never a one-token folder or cast key."""
    names = snapshot(person, folder, catalog=catalog)
    import people

    recorded = people.read(folder) if folder is not None else None
    if recorded and is_full_person_name(recorded[0]):
        result = {
            "originalName": names["originalName"] if names else recorded[0],
            "currentName": recorded[0],
            "originalSource": names["originalSource"] if names else "recorded-history",
        }
        if names and is_full_person_name(names.get("currentName")) \
                and names["currentName"].casefold() != recorded[0].casefold():
            result["sourceNameConflict"] = {
                "catalogueName": names["currentName"], "recordedName": recorded[0],
            }
        return result
    if names and is_full_person_name(names.get("currentName")):
        return names
    return names


def original_age(person_id, person, folder, *, catalog=None):
    """Read explicit identity-creation evidence; filesystem timestamps are not provenance."""
    evidence = []
    if isinstance(person, dict):
        created = person.get("createdAt") or person.get("identityCreatedAt")
        if isinstance(created, str):
            date = created[:10]
            try:
                datetime.date.fromisoformat(date)
            except ValueError:
                pass
            else:
                evidence.append({"date": date, "source": "catalogue-creation-record", "detail": created})
    for action in (catalog or {}).get("actions", []):
        if (
            action.get("personId") == person_id
            and action.get("type") in ("person-created", "identity-created")
            and isinstance(action.get("timestamp"), str)
        ):
            date = action["timestamp"][:10]
            try:
                datetime.date.fromisoformat(date)
            except ValueError:
                continue
            evidence.append({
                "date": date, "source": "catalogue-creation-action",
                "detail": action["timestamp"],
            })
    if folder is not None:
        import people

        recorded = people.read(folder)
        for line in recorded[1] if recorded else ():
            match = re.match(r"^(\d{4}-\d{2}-\d{2})\s+.*\bnew person\b", line, re.IGNORECASE)
            if match:
                try:
                    datetime.date.fromisoformat(match[1])
                except ValueError:
                    continue
                evidence.append({
                    "date": match[1], "source": "z-history-new-person",
                    "detail": line,
                })
    dates = {row["date"] for row in evidence}
    if len(dates) == 1:
        return {"date": next(iter(dates)), "status": "verified", "evidence": evidence}
    if len(dates) > 1:
        return {"date": None, "status": "conflict", "evidence": evidence}
    return {"date": None, "status": "missing", "evidence": []}


def presentation(person, folder=None, *, catalog=None):
    names = snapshot(person, folder, catalog=catalog)
    key = (person or {}).get("folder", "")
    category, _, slot = key.partition("/")
    family = (person or {}).get("family") or {}
    character = slot if category in ("Angels", "Sisters") else None
    if character and family.get("surname") and not character.casefold().endswith(" " + family["surname"].casefold()):
        character += " " + family["surname"]
    return {
        "characterName": character,
        "currentPersonName": names["currentName"] if names else None,
        "originalPersonName": names["originalName"] if names else None,
        "originalNameSource": names["originalSource"] if names else "unavailable",
        "familyId": family.get("id"),
        "familySurname": family.get("surname"),
        "familyReason": family.get("reason"),
    }


def renamed(person, name, folder):
    names = snapshot(person, folder)
    if names is None:
        names = {"originalName": None, "currentName": name, "originalSource": "unavailable"}
    names["currentName"] = name
    return names
