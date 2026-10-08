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
import re
import sys

from jsonschema import Draft7Validator, validators

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools" / "generators"))
import art_layout  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "data/schemas"
ART_SCHEMAS = ROOT / "data/art/_schema"


_TEXT = {}


def load(path):
    """Parsed JSON of a file. The text is cached by (volume, file id, mtime, size), so a file read twice, or hard-linked into the self-test's copies, is read from disk once;
    parsing stays per call, so a caller may modify what it gets."""
    p = pathlib.Path(path)
    st = p.stat()
    key = (st.st_dev, st.st_ino, st.st_mtime_ns, st.st_size) if st.st_ino else None
    text = _TEXT.get(key) if key else None
    if text is None:
        text = p.read_text(encoding="utf-8-sig")
        if key:
            _TEXT[key] = text
    return json.loads(text)


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
        if parts[0] in ("_schema", "_sets", "_kits", "_settings"):
            continue
        if parts[0] == "heroes" and (len(parts) == 3 or (len(parts) == 4 and parts[2] in art_layout.divisions(parts[1]))):
            continue  # identity, not a piece
        if parts[0] == "dragons" and len(parts) <= 3:
            continue  # a dragon identity (dragons/<group>/<slug>.json); the pieces below it (companion frames) are checked as pieces
        if parts[0] == "pets":
            continue  # pet identities, not pieces
        if parts[0] in ("brand", "cards"):
            continue  # brand and card-art identities, not pieces
        if parts[0] == "themes" and parts[-1] == "theme.json":
            continue  # theme manifest, not a piece
        out.append(p)
    return out


def hero_identity_files():
    out = list(rglob("data/art/heroes/*/*.json"))
    for group, divs in art_layout.divisions().items():
        for div in divs:
            out += rglob(f"data/art/heroes/{group}/{div}/*.json")
    return sorted(out)


REGISTRY = [
    ("gameplay cards", card_files, SCHEMAS / "codex-schema.json"),
    ("art hero identities", hero_identity_files, ART_SCHEMAS / "hero-identity.schema.json"),
    ("art dragon identities", lambda: rglob("data/art/dragons/*/*.json"), ART_SCHEMAS / "dragon-identity.schema.json"),
    ("art pet identities", lambda: rglob("data/art/pets/**/*.json"), ART_SCHEMAS / "pet-identity.schema.json"),
    ("art brand identities", lambda: rglob("data/art/brand/*.json"), ART_SCHEMAS / "brand-identity.schema.json"),
    ("art card-art identities", lambda: rglob("data/art/cards/*.json"), ART_SCHEMAS / "cardart-identity.schema.json"),
    ("art pieces", art_piece_files, ART_SCHEMAS / "art-piece.schema.json"),
    ("art themes", lambda: rglob("data/art/themes/**/theme.json"), ART_SCHEMAS / "theme.schema.json"),
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
    identity_files = hero_identity_files() + rglob("data/art/dragons/*/*.json")
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
    stages = load(ART_SCHEMAS / "stages.json")
    known_folders = {f for fs in stages["classes"].values() for f in fs}
    for f in rglob("data/art/_sets/**/*.json"):
        d = load(f)
        where = rel(f)
        group = f.relative_to(ROOT / "data/art/_sets").parts[0]
        set_parts = f.relative_to(ROOT / "data/art/_sets").parts
        division = set_parts[1] if len(set_parts) > 2 and set_parts[1] in art_layout.divisions(group) else None
        lead = 3 if division else 2  # folders before the phase folders: <group>/[<division>/]<slug>
        if art_layout.divisions(group) and division is None:
            report.error(where, f"group {group} files its cards below a division folder ({', '.join(art_layout.divisions(group))}), see _settings/groups.json")
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
            group_realm = load(ROOT / "data/art/_settings/studio.json").get("realmByGroup", {}).get(pathlib.PurePosixPath(rel(f)).parts[3] if len(pathlib.PurePosixPath(rel(f)).parts) > 3 else "")
            realm_ref = d.get("components", {}).get("realm") or group_realm or "data/art/realms/fantasy.json"
            realm_piece = load(ROOT / realm_ref) if (ROOT / realm_ref).exists() else {}
            realm = realm_piece.get("backgroundRealm") or pathlib.PurePosixPath(realm_ref).stem
            if bg_realm != realm:
                report.error(where, f"scene realm is '{realm}' but background {bg} is under backgrounds/{bg_realm}/ "
                                    f"(set components.realm to match, or pick a {realm} background)")
        # Staged vs complete scenes: a staged scene expects a pre-rendered stage image, so it must say
        # so in its name (and use the staged template); every other scene must be complete from the A-pose.
        if d["stage"] == "scene":
            slug = set_parts[lead - 1]
            hero = pathlib.PurePosixPath(d.get("output", "")).name
            if f.stem != d["artId"]:
                report.error(where, f"scene file name must equal its artId ({d['artId']}.json)")
            if not (d["artId"].startswith(slug.split("-")[0] + "-") and "-scene-" in d["artId"]):
                report.error(where, f"scene artId must look like '<hero>-scene-<name>' (got {d['artId']})")
            if not re.fullmatch(r"[A-Z][A-Za-z]*_Scene_(Staged_)?[A-Za-z0-9_]+\.txt", hero):
                report.error(where, f"scene output name must look like '<Hero>_Scene_<Name>.txt' (got {hero})")
            is_staged_tpl = pathlib.PurePosixPath(d["template"]).name.startswith("scene-staged-")
            if ("-staged-" in d["artId"]) != is_staged_tpl or ("_Staged_" in d.get("output", "")) != is_staged_tpl:
                report.error(where, "staged scenes must use a scene-staged-* template AND have '-staged-' in the artId "
                                    "and '_Staged_' in the output name; complete scenes must have none of these")
        out = d.get("output")
        # The card file, its prompt and the ComfyUI output share one set of folders: the pipeline phase and the family, both decided by the card
        # (tools/generators/art_layout.py). Hair and motion cards name their own family in their output.
        if out:
            want = art_layout.card_dirs(d, group, ROOT)
            card_dirs = list(set_parts[lead:-1])
            where_to = "/".join(want) or "(slug root)"
            if card_dirs != want:
                report.error(where, f"card file must sit in {where_to}/ (the phase and family come from the card, see tools/generators/art_layout.py)")
            if art_layout.split_output(out)[3] != want:
                report.error(where, f"output {out} must sit in the folder '{where_to}' below its hero folder")
            if art_layout.split_output(out)[1] != division:
                report.error(where, f"output {out} must use the same division folder as the card file ({division or 'none'})")
        if out:
            if out.split("/")[1] != group:
                report.error(where, f"output {out} is not under prompts/{group}/")
            folder = stages["cardStageToFolder"].get(d["stage"], d["stage"])
            if folder not in known_folders:
                report.error(where, f"stage folder '{folder}' is in no class (studio or scene) in _schema/stages.json")
            elif len(out.split("/")) < 5 or art_layout.parse_dirs(art_layout.split_output(out)[3])[0] != folder:
                report.error(where, f"output {out} must sit in the '{folder}' folder for stage '{d['stage']}'")
            if out in outputs:
                report.error(where, f"output {out} is also produced by {outputs[out]} (one would overwrite the other)")
            outputs[out] = where


def check_variants(report, cards):
    """card.art.variants <-> art cards with a finish: both directions, unique codes, naming."""
    finishes = load(ART_SCHEMAS / "finishes.json")["finishes"]
    listed = {}
    for cid, (f, d) in cards.items():
        ident = d.get("art", {}).get("artIdentity")
        seen = set()
        for v in d.get("art", {}).get("variants", []):
            fin, ac = v.get("finish"), v.get("artCard", "")
            if fin not in finishes:
                report.error(rel(f), f"variant finish {fin!r} is not in _schema/finishes.json")
                continue
            if fin in seen:
                report.error(rel(f), f"card {cid} lists the {fin} variant twice")
            seen.add(fin)
            if not (ROOT / ac).exists():
                report.error(rel(f), f"variant {fin} artCard {ac} does not exist")
                continue
            art = load(ROOT / ac)
            listed[ac] = (cid, fin)
            if art.get("finish") != fin:
                report.error(rel(f), f"variant {fin} artCard {ac} must set \"finish\": \"{fin}\" (link must be bidirectional)")
            if art.get("heroArt") != ident:
                report.error(rel(f), f"variant {fin} artCard {ac} belongs to {art.get('heroArt')}, not this card's art identity")
            if art.get("stage") != "scene":
                report.error(rel(f), f"variant {fin} artCard {ac} must be a scene card")
    for f in rglob("data/art/_sets/**/*.json"):
        d = load(f)
        fin = d.get("finish")
        aid = d.get("artId", "")
        suffix_fin = next((k for k in finishes if aid.endswith("-" + k)), None)
        if fin and fin not in finishes:
            report.error(rel(f), f"finish {fin!r} is not in _schema/finishes.json")
        elif fin and listed.get(rel(f), (None, None))[1] != fin:
            report.error(rel(f), f"art card has finish {fin!r} but its hero's card does not list it under art.variants")
        if suffix_fin and fin != suffix_fin:
            report.error(rel(f), f"artId ends in -{suffix_fin} so it must set \"finish\": \"{suffix_fin}\"")


def check_kits(report):
    """data/art/_kits: every piece or card a sister's studio kit names must exist."""
    def paths(v):
        if isinstance(v, str):
            if v.startswith(("wardrobe/", "heroes/", "backgrounds/", "motion/", "data/art/")):
                yield v
        elif isinstance(v, list):
            for x in v:
                yield from paths(x)
        elif isinstance(v, dict):
            for x in v.values():
                yield from paths(x)
    for f in rglob("data/art/_kits/**/*.json"):
        d, where = load(f), rel(f)
        for key in (("hero", "slug", "group") if f.parent.name == "_kits" else ()):
            if key not in d:
                report.error(where, f"kit is missing '{key}'")
        for ref in paths({k: v for k, v in d.items() if k != "motions" or v != "all"}):
            full = ref if ref.startswith("data/art/") else "data/art/" + ref
            if not (ROOT / (full if full.endswith(".json") else full + ".json")).exists():
                report.error(where, f"kit names {ref}, which does not exist")


def check_pets(report):
    """A pet and its angel point at each other (profile.pet <-> bondedTo), and every angel with a profile has a pet."""
    for f in rglob("data/art/pets/**/*.json"):
        d, where = load(f), rel(f)
        hero = d.get("bondedTo")
        if not hero or not (ROOT / hero).exists():
            report.error(where, f"bondedTo {hero} does not exist")
        elif load(ROOT / hero).get("profile", {}).get("pet") != where:
            report.error(where, f"{hero} profile.pet does not point back at this pet (link must be bidirectional)")
    for f in hero_identity_files():
        pet = load(f).get("profile", {}).get("pet")
        if pet and not (ROOT / pet).exists():
            report.error(rel(f), f"profile.pet {pet} does not exist")


def check_animation_cards(report):
    """data/animation/_sets cards: every file they name exists, and every action and transition is usable."""
    def exists(where, what, path):
        if not (ROOT / path).exists():
            report.error(where, f"{what} {path} does not exist")
    def action(where, item):
        if isinstance(item, str):
            return
        if item.get("sequence"):
            exists(where, "sequence", item["sequence"])
            if (ROOT / item["sequence"]).exists():
                for inner in load(item["sequence"]).get("actions", []):
                    action(where, inner)
            return
        for key in ("motion", "scene"):
            ref = item.get(key)
            if ref and ref.endswith(".json"):
                exists(where, f"action {key}", ref)
        if not any(k in item for k in ("motion", "scene", "beat")):
            report.error(where, f"action {item} needs a motion, a scene or a beat")
        if "seconds" in item and not (isinstance(item["seconds"], (int, float)) and item["seconds"] > 0):
            report.error(where, f"action seconds must be a positive number (got {item['seconds']!r})")
        tr = item.get("transition")
        if tr and re.fullmatch(r"[a-z-]+", tr):
            exists(where, "transition", f"data/animation/transitions/{tr}.json")
        for other in item.get("with", []):
            action(where, other)
    for f in rglob("data/animation/_sets/**/*.json"):
        d, where = load(f), rel(f)
        for key in ("animId", "name", "heroArt", "look", "actions", "template"):
            if key not in d:
                report.error(where, f"animation card is missing '{key}'")
        if d.get("animId") != f.stem:
            report.error(where, f"animId must equal the file name ({f.stem})")
        for key in ("heroArt", "look", "template"):
            if key in d:
                exists(where, key, d[key])
        if d.get("source", {}).get("artCard"):
            exists(where, "source.artCard", d["source"]["artCard"])
        if str(d.get("camera", "")).endswith(".json"):
            exists(where, "camera", d["camera"])
        if not d.get("actions"):
            report.error(where, "animation card needs at least one action")
        for item in d.get("actions", []):
            action(where, item)
        if "transition" in d and re.fullmatch(r"[a-z-]+", d["transition"]):
            exists(where, "transition", f"data/animation/transitions/{d['transition']}.json")


def check_piece_refs(report):
    for f in rglob("data/art/**/backgrounds/**/*.json"):
        parts = f.relative_to(ROOT / "data/art").parts
        realm_dir = parts[parts.index("backgrounds") + 1]
        if realm_dir not in ("fantasy", "modern", "studio") or len(parts) <= parts.index("backgrounds") + 2:
            report.error(rel(f), "backgrounds must live under fantasy/, modern/ or studio/ (that folder is the realm)")
    # Core wardrobe and theme pieces: the id is the path, so a move can never leave a stale id behind.
    for f in rglob("data/art/wardrobe/**/*.json") + rglob("data/art/themes/**/*.json") + rglob("data/art/cosmetics/**/*.json"):
        if f.name == "theme.json":
            continue
        expected = f.relative_to(ROOT / "data/art").with_suffix("").as_posix()
        actual = load(f).get("id")
        if actual != expected:
            report.error(rel(f), f"id {actual!r} must equal its path {expected!r}")
    # Themes sit one level down in a group folder (themes/<group>/<theme>/theme.json) so the list stays browsable.
    for group in rglob("data/art/themes/*"):
        if not group.is_dir():
            continue
        if (group / "theme.json").exists():
            report.error(rel(group / "theme.json"), "a theme must sit inside a group folder: themes/<group>/<theme>/")
        for f in group.iterdir():
            if f.is_dir() and not (f / "theme.json").exists():
                report.error(rel(f), "theme folder has no theme.json")
            elif f.is_dir() and load(f / "theme.json").get("id") != f"themes/{group.name}/{f.name}":
                report.error(rel(f / "theme.json"), f"id must be 'themes/{group.name}/{f.name}'")
    for f in art_piece_files():
        d = load(f)
        base = d.get("extends")
        if base:
            chain, cur = [rel(f)], base
            while cur:
                if not (ROOT / cur).exists():
                    report.error(rel(f), f"extends {cur}, which does not exist")
                    break
                if cur in chain:
                    report.error(rel(f), f"extends forms a cycle: {' -> '.join(chain + [cur])}")
                    break
                chain.append(cur)
                parent = load(ROOT / cur)
                if parent.get("kind") != d.get("kind"):
                    report.error(rel(f), f"extends {cur} of kind {parent.get('kind')!r}, but this piece is kind {d.get('kind')!r}")
                cur = parent.get("extends")
            texts, supplied, own = [], {}, {}
            for step in reversed(chain):
                piece = d if step == chain[0] else load(ROOT / step)
                ref = piece.get("varsFrom")
                if ref:
                    if not (ROOT / ref).exists():
                        report.error(rel(f), f"varsFrom {ref} does not exist")
                    elif load(ROOT / ref).get("kind") != "design":
                        report.error(rel(f), f"varsFrom {ref} is not a kind 'design' piece")
                    else:
                        supplied.update(load(ROOT / ref).get("vars") or {})
                supplied.update(piece.get("vars") or {})
                own.update(piece.get("vars") or {})
                texts += [x for k, v in piece.items() if k not in ("notes", "name", "id") for x in ([v] if isinstance(v, str) else v if isinstance(v, list) else []) if isinstance(x, str)]
            wanted = set(re.findall(r"\[\[([A-Za-z0-9_]+)\]\]", "\n".join(texts)))
            if wanted - set(supplied):
                report.error(rel(f), f"slot(s) {', '.join(sorted(wanted - set(supplied)))} of its base are not filled; add them to \"vars\" or its varsFrom design")
            if set(own) - wanted:
                report.error(rel(f), f"vars {', '.join(sorted(set(own) - wanted))} fill no [[SLOT]] in the base")
        elif d.get("vars") and d.get("kind") != "design":
            report.error(rel(f), "vars only make sense in a piece that extends a frame")
        elif any(isinstance(v, str) and "{{BASE}}" in v for v in d.values()):
            report.error(rel(f), "{{BASE}} is only meaningful in a piece that extends another")
        for field in ("defaultGaze", "defaultExpression"):
            val = d.get(field)
            if isinstance(val, str) and looks_like_path(val) and not (ROOT / val).exists():
                report.error(rel(f), f"{field} {val} does not exist")
    for f in hero_identity_files():
        ref = load(f).get("art", {}).get("palette", {}).get("hairStyleComponent")
        pal = load(f).get("art", {}).get("palette", {})
        du = load(f).get("art", {}).get("defaultUnderlayer")
        if du and not (ROOT / du).exists():
            report.error(rel(f), f"defaultUnderlayer {du} does not exist")
        df = load(f).get("art", {}).get("defaultFootwear")
        if df and not (ROOT / df).exists():
            report.error(rel(f), f"defaultFootwear {df} does not exist")
        ds = load(f).get("art", {}).get("defaultSheen")
        if ds and not (ROOT / ds).exists():
            report.error(rel(f), f"defaultSheen {ds} does not exist")
        if "hairHighlights" in pal:
            if not (ROOT / pal["hairHighlights"]).exists():
                report.error(rel(f), f"hairHighlights {pal['hairHighlights']} does not exist")
            if "hairHighlightColor" not in pal:
                report.error(rel(f), "hairHighlights needs hairHighlightColor")
        if ref and not (ROOT / ref).exists():
            report.error(rel(f), f"hairStyleComponent {ref} does not exist")

    # A sister's dragon companion comes from her Elder Dragon's definition: the piece extends the dragon's companion frame (data/art/dragons/...) and only says where the dragon is,
    # and a scene card names that piece instead of typing the dragon again (tools/art/dragon_companions.py does the conversion).
    for f in rglob("data/art/heroes/drakn-sisters/*/companion/*.json"):
        if not str(load(f).get("extends", "")).startswith("data/art/dragons/"):
            report.error(rel(f), "a sister's companion piece must extend her Elder Dragon's companion frame (data/art/dragons/elder-dragons/<slug>/companion/...); see tools/art/dragon_companions.py")
    for f in rglob("data/art/_sets/drakn-sisters/**/*.json"):
        slot = load(f).get("components", {}).get("companion")
        if isinstance(slot, str) and not slot.endswith(".json"):
            report.error(rel(f), "a sister scene must name her dragon companion as a piece, not type the dragon in the card (see tools/art/dragon_companions.py)")

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
    check_variants(report, cards)
    check_kits(report)
    check_pets(report)
    check_piece_refs(report)
    check_animation_cards(report)
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
