#!/usr/bin/env python3
"""Validate every schema-covered JSON file under data/ and enforce cross-file integrity.

Three layers:
  1. SCHEMA   - each file class is validated against its own schema (registry below).
  2. LINKS    - cross-file rules JSON Schema cannot express: the card <-> art identity
                link is bidirectional, art cards point at files that exist, a typo'd
                piece path is not silently treated as literal prompt text, generated
                outputs are unique, physique shape matches the card's sex, ids are unique.
  3. COVERAGE - prints which areas are enforced and which are known, tracked debt.

Gameplay cards (data/cards) and art direction (data/art) are separate pipelines with
separate schemas; they meet ONLY at the cardId link and the card's art asset references.

Usage:  python tools/validators/validate_data.py        # exit 1 on any error
"""
import collections
import json
import pathlib
import sys

from jsonschema import Draft7Validator, validators

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "data/schemas"
ART_SCHEMAS = ROOT / "data/art/_schema"


def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))


def rel(path):
    return pathlib.Path(path).relative_to(ROOT).as_posix()


def rglob(pattern):
    return sorted(ROOT.glob(pattern))


# -- registry: (label, files, schema) -----------------------------------------------
def card_files():
    out = []
    for p in rglob("data/cards/sovereign-dawn/**/*.json"):
        if "element-lists" in p.parts:
            continue
        out.append(p)
    return out


def art_piece_files():
    out = []
    for p in rglob("data/art/**/*.json"):
        parts = p.relative_to(ROOT / "data/art").parts
        if parts[0] in ("_schema", "_sets"):
            continue
        if parts[0] == "heroes" and len(parts) == 3:
            continue  # identity, not a piece
        if parts[0] == "dragons":
            continue
        if parts[0] == "themes" and len(parts) == 3 and parts[2] == "theme.json":
            continue  # theme manifest, not a piece
        out.append(p)
    return out


def hero_identity_files():
    return [p for p in rglob("data/art/heroes/*/*.json")]


REGISTRY = [
    ("gameplay cards", card_files, SCHEMAS / "codex-schema.json"),
    ("art hero identities", hero_identity_files, ART_SCHEMAS / "hero-identity.schema.json"),
    ("art dragon identities", lambda: rglob("data/art/dragons/**/*.json"), ART_SCHEMAS / "dragon-identity.schema.json"),
    ("art pieces", art_piece_files, ART_SCHEMAS / "art-piece.schema.json"),
    ("art themes", lambda: rglob("data/art/themes/*/theme.json"), ART_SCHEMAS / "theme.schema.json"),
    ("art assembly cards", lambda: rglob("data/art/_sets/**/*.json"), ART_SCHEMAS / "art-card.schema.json"),
]

# Known, tracked debt: files with no schema that actually fits them yet.
# (area, glob, reason) -- shown in the coverage report so the gap is visible, not hidden.
PENDING = [
    ("products/packs", "data/products/packs/*.json", "pack-schema.json predates current pack data (0/16 match); rewrite schema or data"),
    ("products/boxes", "data/products/boxes/*.json", "no schema fits current box files"),
    ("products/rewards", "data/products/rewards/*.json", "reward-schema.json predates current data"),
    ("decks/starter", "data/decks/starter/*.json", "starter-deck-schema.json predates current data"),
    ("manifests", "data/manifests/*.json", "no manifest schema yet"),
    ("collection", "data/collection/*.json", "no collection schema yet"),
    ("card element-lists", "data/cards/sovereign-dawn/element-lists/**/*.json", "id-list helper files; no schema yet"),
]


class Report:
    def __init__(self):
        self.errors = []

    def error(self, where, msg):
        self.errors.append(f"{where}: {msg}")


def check_schemas_valid(report):
    for p in sorted(SCHEMAS.glob("*.json")) + sorted(ART_SCHEMAS.glob("*.schema.json")):
        s = load(p)
        try:
            validators.validator_for(s, default=Draft7Validator).check_schema(s)
        except Exception as e:  # noqa: BLE001 - report any schema defect
            report.error(rel(p), f"not a valid JSON Schema: {str(e).splitlines()[0]}")


def check_instances(report, counts):
    for label, getter, schema_path in REGISTRY:
        schema = load(schema_path)
        validator = validators.validator_for(schema, default=Draft7Validator)(schema)
        files = getter()
        counts[label] = len(files)
        for f in files:
            try:
                data = load(f)
            except Exception as e:  # noqa: BLE001
                report.error(rel(f), f"invalid JSON: {e}")
                continue
            if label == "gameplay cards" and not (isinstance(data, dict) and "cardId" in data):
                report.error(rel(f), "expected a card object with cardId")
                continue
            for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
                loc = "/".join(str(x) for x in err.absolute_path) or "<root>"
                report.error(rel(f), f"[{schema_path.name}] {loc}: {err.message[:160]}")


def check_card_art_links(report):
    cards = {}
    for f in card_files():
        d = load(f)
        if not isinstance(d, dict) or "cardId" not in d:
            continue
        if d["cardId"] in cards:
            report.error(rel(f), f"duplicate cardId {d['cardId']} (also {rel(cards[d['cardId']][0])})")
        cards[d["cardId"]] = (f, d)

    numbers = collections.defaultdict(list)
    for cid, (f, d) in cards.items():
        numbers[d.get("collectionNumber")].append(cid)
    for num, cids in numbers.items():
        if num and len(cids) > 1:
            report.error("data/cards", f"collectionNumber {num} used by {len(cids)} cards: {', '.join(sorted(cids))}")

    # identity -> card
    identity_of = {}
    identity_files = hero_identity_files() + rglob("data/art/dragons/**/*.json")
    for f in identity_files:
        d = load(f)
        cid = d.get("cardId")
        if cid is None:
            continue  # testBed heroes are schema-checked; they have no card by design
        if cid not in cards:
            report.error(rel(f), f"cardId {cid} has no card under data/cards/")
            continue
        if cid in identity_of:
            report.error(rel(f), f"cardId {cid} is also claimed by {identity_of[cid]}")
        identity_of[cid] = rel(f)
        back = cards[cid][1].get("art", {}).get("artIdentity")
        if back != rel(f):
            report.error(rel(f), f"card {cid} art.artIdentity is {back!r}, expected {rel(f)!r} (link must be bidirectional)")
        card = cards[cid][1]
        if "art" in d and "physique" in d["art"]:
            is_female_shape = "bust" in d["art"]["physique"]
            if card.get("sex") == "Female" and not is_female_shape:
                report.error(rel(f), f"card {cid} is Female but physique uses the male shape (chest/waist)")
            if card.get("sex") == "Male" and is_female_shape:
                report.error(rel(f), f"card {cid} is Male but physique uses the female shape (bust/hips)")

    # card -> identity
    for cid, (f, d) in cards.items():
        ref = d.get("art", {}).get("artIdentity")
        if ref is None:
            continue
        target = ROOT / ref
        if not target.exists():
            report.error(rel(f), f"art.artIdentity {ref} does not exist")
        elif load(target).get("cardId") != cid:
            report.error(rel(f), f"art.artIdentity {ref} does not link back to {cid}")
    return cards, identity_of


def looks_like_path(value):
    return value.startswith("data/art/") or value.lower().endswith(".json")


def check_art_cards(report):
    outputs = {}
    for f in rglob("data/art/_sets/**/*.json"):
        d = load(f)
        where = rel(f)
        group = f.relative_to(ROOT / "data/art/_sets").parts[0]
        for key in ("heroArt", "template"):
            if key in d and not (ROOT / d[key]).exists():
                report.error(where, f"{key} {d[key]} does not exist")
        refs = []
        if "component" in d:
            refs.append(("component", d["component"]))
        for slot, val in d.get("components", {}).items():
            refs.append((f"components.{slot}", val))
        for slot, val in refs:
            if val.startswith("+"):
                continue
            # The generator treats a non-existent .json path as LITERAL prompt text, so a typo
            # would silently put a file path into the prompt. Catch it here instead.
            if looks_like_path(val) and not (ROOT / val).exists():
                report.error(where, f"{slot} looks like a path but {val} does not exist (would be rendered as literal text)")
        # Realm rule: a scene's background folder must match its realm (default: fantasy), so a
        # modern or studio background can never slip into canon art without an explicit opt-in.
        bg = d.get("components", {}).get("background", "")
        if bg.startswith("data/art/") and "/backgrounds/" in bg and d["stage"] == "scene":
            parts = bg.split("/")
            bg_realm = parts[parts.index("backgrounds") + 1]
            realm = pathlib.PurePosixPath(d.get("components", {}).get("realm", "data/art/realms/fantasy.json")).stem
            if bg_realm != realm:
                report.error(where, f"scene realm is '{realm}' but background {bg} is under backgrounds/{bg_realm}/ "
                                    f"(set components.realm to match, or pick a {realm} background)")
        # Staged vs complete scenes: a staged scene expects a pre-rendered stage image, so it must say
        # so in its name (and use the staged template); every other scene must be complete from the A-pose.
        if d["stage"] == "scene":
            is_staged_tpl = pathlib.PurePosixPath(d["template"]).name.startswith("scene-staged-")
            if ("-staged-" in d["artId"]) != is_staged_tpl or ("_Staged_" in d.get("output", "")) != is_staged_tpl:
                report.error(where, "staged scenes must use a scene-staged-* template AND have '-staged-' in the artId "
                                    "and '_Staged_' in the output name; complete scenes must have none of these")
        out = d.get("output")
        if out:
            if out.split("/")[1] != group:
                report.error(where, f"output {out} is not under prompts/{group}/")
            if out in outputs:
                report.error(where, f"output {out} is also produced by {outputs[out]} (one would overwrite the other)")
            outputs[out] = where


def check_piece_refs(report):
    for f in rglob("data/art/**/backgrounds/**/*.json"):
        parts = f.relative_to(ROOT / "data/art").parts
        realm_dir = parts[parts.index("backgrounds") + 1]
        if realm_dir not in ("fantasy", "modern", "studio") or len(parts) <= parts.index("backgrounds") + 2:
            report.error(rel(f), "backgrounds must live under fantasy/, modern/ or studio/ (that folder is the realm)")
    # Core wardrobe and theme pieces: the id is the path, so a move can never leave a stale id behind.
    for f in rglob("data/art/wardrobe/**/*.json") + rglob("data/art/themes/*/**/*.json") + rglob("data/art/cosmetics/**/*.json"):
        if f.name == "theme.json":
            continue
        expected = f.relative_to(ROOT / "data/art").with_suffix("").as_posix()
        actual = load(f).get("id")
        if actual != expected:
            report.error(rel(f), f"id {actual!r} must equal its path {expected!r}")
    for f in rglob("data/art/themes/*"):
        if f.is_dir() and not (f / "theme.json").exists():
            report.error(rel(f), "theme folder has no theme.json")
        elif f.is_dir() and load(f / "theme.json").get("id") != f"themes/{f.name}":
            report.error(rel(f / "theme.json"), f"id must be 'themes/{f.name}'")
    for f in art_piece_files():
        d = load(f)
        for field in ("defaultGaze", "defaultExpression"):
            val = d.get(field)
            if isinstance(val, str) and looks_like_path(val) and not (ROOT / val).exists():
                report.error(rel(f), f"{field} {val} does not exist")
    for f in hero_identity_files():
        ref = load(f).get("art", {}).get("palette", {}).get("hairStyleComponent")
        if ref and not (ROOT / ref).exists():
            report.error(rel(f), f"hairStyleComponent {ref} does not exist")


def coverage(report, counts, cards, identity_of):
    print("COVERAGE")
    for label, n in counts.items():
        print(f"  enforced  {n:4}  {label}")
    for area, pattern, reason in PENDING:
        n = len(rglob(pattern))
        print(f"  PENDING   {n:4}  {area}: {reason}")
    heroes = [cid for cid, (_, d) in cards.items() if d.get("type") == "Hero" or d.get("class") == "Elder Dragon"]
    linked = [c for c in heroes if c in identity_of]
    print(f"  art link  {len(linked):4}  of {len(heroes)} hero/dragon cards have an art identity "
          f"({len(cards)} cards total)")
    unlinked = sorted(set(heroes) - set(linked))
    if unlinked:
        print("            without art yet: " + ", ".join(unlinked[:8]) + (" ..." if len(unlinked) > 8 else ""))


def main():
    report = Report()
    counts = {}
    check_schemas_valid(report)
    check_instances(report, counts)
    cards, identity_of = check_card_art_links(report)
    check_art_cards(report)
    check_piece_refs(report)
    coverage(report, counts, cards, identity_of)
    if report.errors:
        print(f"\nFAILED: {len(report.errors)} problem(s)")
        for e in report.errors[:60]:
            print("  - " + e)
        if len(report.errors) > 60:
            print(f"  ... and {len(report.errors) - 60} more")
        return 1
    print("\nOK: all schema-covered files valid, all card <-> art links intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
