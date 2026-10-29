"""Name provenance independent of cast slots, folder labels and face evidence."""
import copy
import base64
import re


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
