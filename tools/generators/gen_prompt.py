#!/usr/bin/env python3
"""Generate a prompt .txt from an art-source card + hero card + stage template.

Reads a card (data/art/_sets/<group>/<slug>/<phase folders>/<name>.json), pulls traits
from the referenced hero def, fills the {{TOKEN}} slots in the template, and writes the
output .txt under prompts/<group>/<Hero>/... Model-agnostic — the output feeds any ComfyUI
workflow.

Usage:
    python tools/generators/gen_prompt.py                                   # everything
    python tools/generators/gen_prompt.py <card.json>                       # one exact file
    python tools/generators/gen_prompt.py --group drakn-sisters             # one group
    python tools/generators/gen_prompt.py --group drakn-sisters --slug drakness
    python tools/generators/gen_prompt.py --group drakn-sisters --slug drakness --stage hair
    python tools/generators/gen_prompt.py --group drakn-sisters --slug drakness --stage hair --family down
    python tools/generators/gen_prompt.py --cleanup                         # PREVIEW orphaned .txt output (safe)
    python tools/generators/gen_prompt.py --cleanup --yes                   # actually delete them
Filters compose (all default to "any"); omitting all of them generates every card under
data/art/_sets/. --cleanup is a two-phase plan/apply, like `terraform plan`/`apply`: alone it
only lists prompts/<group>/ .txt files that no longer match a current card's output (e.g.
leftovers from a renamed artId) -- add --yes to actually delete them. Scoped to groups touched
this run; never touches prompts/_archive/.
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import art_layout  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))


_SLOT = re.compile(r"\[\[([A-Za-z0-9_]+)\]\]")


def piece_slots(text):
    """Names of the [[SLOT]] markers in a piece's text."""
    return set(_SLOT.findall(text)) if isinstance(text, str) else set()


def _load_chain(path, _seen=()):
    path = pathlib.Path(path)
    piece = load_json(path)
    base_ref = piece.get("extends") if isinstance(piece, dict) else None
    if not base_ref:
        return piece
    if str(path) in _seen:
        sys.exit(f"ERROR: {path} extends itself through {' -> '.join(_seen)}")
    base_path = ROOT / base_ref
    if not base_path.exists():
        sys.exit(f"ERROR: {path} extends {base_ref}, which does not exist")
    base = _load_chain(base_path, _seen + (str(path),))
    out = {k: v for k, v in base.items() if k not in ("id", "name", "notes", "tags")}
    for key, val in piece.items():
        if key in ("extends", "vars", "varsFrom"):
            continue
        if key == "negatives":
            val = list(dict.fromkeys(list(base.get("negatives", [])) + list(val)))
        elif isinstance(val, str) and isinstance(base.get(key), str):
            if "{{BASE}}" in val:
                val = val.replace("{{BASE}}", base[key].rstrip())
            elif val.startswith("+"):
                tail = val[1:].strip()
                val = base[key].rstrip() + ("" if tail[:1] in ",;.:" else " ") + tail
        out[key] = val
    design = load_json(ROOT / piece["varsFrom"]).get("vars", {}) if piece.get("varsFrom") else {}
    if "vars" in base or design or "vars" in piece:
        out["vars"] = {**base.get("vars", {}), **design, **piece.get("vars", {})}
    return out


def load_piece(path):
    """A reusable art piece with its `extends` chain resolved.

    A piece may name a base piece ("extends": "data/art/...json") and then only carry what is different, so a hero's own necklace is the library necklace plus her details
    instead of a second full description. Its own fields replace the base's; in a text field `{{BASE}}` is replaced by the base's text (put the base wherever it reads best),
    and a value starting with "+" is the base's text followed by the rest (no space is added when the rest starts with , ; . or :, so "+, with fine engraving" continues the base's sentence);
    `negatives` are the base's plus its own. Bases may extend further bases; a cycle is an error.

    A base can also be a frame with named gaps, `[[SLOT]]` in its text; a piece that extends it fills them with `"vars": {"SLOT": "text"}`, so ten heroes share one frame and
    each writes only her own metal, shape or engraving. `"varsFrom": "data/art/...json"` takes the values from a design file (kind `design`) so several pieces of one hero
    share one set of values. Every slot of a derived piece must be filled.

    A set piece has `"includes": [piece, piece, ...]` instead of a description: its description is theirs joined with "; " (a jewellery set is a real ring, earring and necklace)."""
    piece = _load_chain(path)
    if not isinstance(piece, dict):
        return piece
    if piece.get("includes"):  # a set: the description is the included pieces' descriptions in order
        piece = dict(piece)
        parts = [load_piece(ROOT / ref).get("description", "") for ref in piece.pop("includes")]
        piece["description"] = "; ".join(p.strip().rstrip(".;") for p in parts if p)
    derived = bool(load_json(path).get("extends"))
    values = piece.pop("vars", {})
    if not derived and not values:
        return piece

    def fill(text):
        return _SLOT.sub(lambda m: str(values[m.group(1)]) if m.group(1) in values else m.group(0), text)

    out = {k: fill(v) if isinstance(v, str) else [fill(x) if isinstance(x, str) else x for x in v] if isinstance(v, list) else v for k, v in piece.items()}
    left = sorted(set().union(*(piece_slots(v) for v in out.values() if isinstance(v, str))))
    if derived and left:
        sys.exit(f"ERROR: {path} leaves slot(s) {', '.join(left)} unfilled; add them to its \"vars\"")
    return out

_CARD_INDEX = None


def card_index():
    """cardId -> parsed gameplay card, for every card under data/cards/. Built once.
    Gameplay cards are the primary record of a card; art identities link to them by
    cardId and pull identity attributes (name, element, sex, ...) from here rather
    than duplicating them."""
    global _CARD_INDEX
    if _CARD_INDEX is None:
        _CARD_INDEX = {}
        for p in sorted((ROOT / "data/cards").rglob("*.json")):
            d = load_json(p)
            if isinstance(d, dict) and "cardId" in d:
                _CARD_INDEX[d["cardId"]] = d
    return _CARD_INDEX


def load_identity(rel_path):
    """Load an art identity (data/art/heroes|dragons/**) and resolve its cardId link.
    The card-owned attributes become fields of the returned dict (name, element, sex,
    race, class) so callers see one merged view; the identity's own fields (palette,
    physique, description) are never overwritten by the card. A test-bed identity
    (testBed: true) has no card and carries its own name. A dangling cardId is a hard
    error -- a broken link must never silently produce a prompt."""
    ident = load_json(ROOT / rel_path)
    if ident.get("kind") in ("brand", "cardart"):
        return ident  # no gameplay card of its own: brand names heroes and the world; cardart styles many gameplay cards
    cid = ident.get("cardId")
    if cid is None:
        if not ident.get("testBed"):
            sys.exit(f"ERROR: {rel_path} has no cardId and is not a testBed identity")
        return ident
    card = card_index().get(cid)
    if card is None:
        sys.exit(f"ERROR: {rel_path} links to cardId '{cid}' but no such card exists under data/cards/")
    for field in ("name", "element", "sex", "race", "class"):
        if field in card:
            ident.setdefault(field, card[field])
    return ident


def decap(s):
    """Lower-case the first letter for mid-sentence injection."""
    return (s[0].lower() + s[1:]) if s else s


_PHRASES = None


def phrases():
    """data/art/_settings/phrases.json: every sentence the generator adds to a hero prompt on its own, so none is hidden in code."""
    global _PHRASES
    if _PHRASES is None:
        _PHRASES = load_json(ROOT / "data/art/_settings/phrases.json")
    return _PHRASES


def cleanup(text):
    """Collapse artifacts left by empty tokens (e.g. an empty HERO_NEG between two
    literal commas): ', , ' -> ', ', and an empty token right before the trailing
    period (', .' -> '.', when HERO_NEG is the last item in a negative list)."""
    while ", ," in text:
        text = text.replace(", ,", ",")
    while ", ." in text:
        text = text.replace(", .", ".")
    return text


def apply_optional_lines(template, toks):
    """A template line starting with '?' is optional: kept (without the '?') only if every token
    in it has a non-empty value, otherwise dropped. Lets a template offer slots like Headwear that
    most cards never fill, without printing an empty 'Headwear: .' line."""
    out, dropped = [], False
    for line in template.split("\n"):
        if line.startswith("?"):
            names = re.findall(r"{{(\w+)}}", line)
            if all(toks.get(n) for n in names):
                out.append(line[1:])
            else:
                dropped = True
            continue
        out.append(line)
    text = "\n".join(out)
    if dropped:
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
    return text


def resolve_hair(pal):
    """Base hair colour, plus an optional highlight-style piece (hairHighlights) whose
    {{HIGHLIGHT_COLOR}} is filled from hairHighlightColor. No highlights -> hairColor unchanged."""
    base = pal["hairColor"]
    if "hairHighlights" in pal:
        style = load_json(ROOT / pal["hairHighlights"])["description"]
        base += ", " + style.replace("{{HIGHLIGHT_COLOR}}", pal["hairHighlightColor"])
    return base


def resolve_hairstyle(pal):
    """HAIRSTYLE comes either from a referenced component (data/art/hair/*.json,
    field 'aPoseStyle') or, for back-compat, a plain 'hairStyle' string on the hero.
    A component reference lets a hero carry a unique/signature A-pose hairstyle
    with a one-line swap, instead of every hero inlining the same text."""
    if "hairStyleComponent" in pal:
        component = load_json(ROOT / pal["hairStyleComponent"])
        return component["a_pose_style"]
    return pal["hairStyle"]


def resolve_breeze(pal):
    """The hair piece's own 'breeze' line (a very slight lift ...), so the template never hard-codes it."""
    if "hairStyleComponent" in pal:
        return load_json(ROOT / pal["hairStyleComponent"]).get("breeze", phrases()["defaultBreeze"])
    return phrases()["defaultBreeze"]


def resolve_hairstyle_negatives(pal):
    """Optional 'a_pose_negatives' list on the hair component (e.g. ponytail, bun) so a
    style that must fully replace the source photo's hair can ban what leaks through."""
    if "hairStyleComponent" in pal:
        component = load_json(ROOT / pal["hairStyleComponent"])
        return ", ".join(component.get("a_pose_negatives", []))
    return ""


def soft_eye(glamour):
    """Iris colour only (e.g. 'Deep violet irises'), dropping striations/limbal-ring detail.
    Used by stages that preserve the incoming eyes, where the full glamour line over-emphasises them."""
    m = re.match(r"(.*?\biris(?:es)?)\b", glamour)
    return decap(m.group(1) if m else glamour)


# A template token that a card does not fill (components.<slot>) falls back to a default
# piece, chosen by the card's stage and, where it differs, the hero's sex. Templates stay thin
# shells; the proven text lives in data/art pieces. Override per card with components.<slot>
# (a piece path, a literal, or '+literal' to extend).
SLOT_DEFAULTS = {
    "eye_effect": {"*": "data/art/wardrobe/effects/eyes/partial-glow.json"},
    "background": {
        stage: "data/art/backgrounds/studio/cream-even.json"
        for stage in ("pose", "head", "hair", "motion", "armor", "clothing")
    },
    "realm": {"scene": "data/art/realms/fantasy.json"},
    "framing": {"*": "data/art/studio/framing/bust-up.json"},
    "view": {
        "head": "data/art/studio/views/head/front.json",
        "pose": "data/art/studio/views/body/front.json",
    },
    "expression": {
        "head": "data/art/motion/expressions/studio/studio-soft-smile.json",
        "pose": {
            "female": "data/art/motion/expressions/studio/studio-soft-smile.json",
            "male": "data/art/motion/expressions/studio/studio-confident-soft-smile.json",
        },
    },
    "underlayer": {
        "pose": {
            "female": "data/art/wardrobe/swimwear/bikini/triangle-bikini.json",
            "male": "data/art/wardrobe/swimwear/trunks/swim-brief.json",
        },
    },
    # Swimwear pieces end with {{FOOTWEAR}}; males wear none.
    "footwear": {
        "pose": {"female": "data/art/wardrobe/footwear/heels/matching-open-toed-heels.json"},
    },
    # Surface finish of metallic pieces (wardrobe/finishes/*); swimwear pieces embed {{SHEEN}}.
    "sheen": {
        "pose": {"female": "data/art/wardrobe/finishes/satin.json"},
    },
}


BAREFOOT_A_POSE = "data/art/wardrobe/footwear/barefoot/barefoot-a-pose.json"

# The alpha stage (the hero's creation chain) uses the same slot defaults as the pose stage.
for _entry in SLOT_DEFAULTS.values():
    if "pose" in _entry:
        _entry["alpha"] = _entry["pose"]


def studio_defaults():
    return json.loads((ROOT / "data/art/_settings/studio.json").read_text(encoding="utf-8"))


def group_of(card_path):
    """The set group (angel-primes, drakn-sisters ...) of a card file under data/art/_sets."""
    parts = pathlib.PurePath(str(card_path).replace("\\", "/")).parts
    return parts[parts.index("_sets") + 1] if "_sets" in parts else None


def default_slot(slot, stage, sex):
    entry = SLOT_DEFAULTS[slot]
    value = entry.get(stage, entry.get("*"))
    if isinstance(value, dict):
        value = value.get(sex)
    return value

# One shared studio face-styling line for every cream-backdrop stage, so makeup stays
# present-but-subtle and identical from the full-body shot to the close-up.
def face_style(female, eyeshadow, blush, brow=None):
    p = phrases()["faceStyle"]
    brows = p["brows"].format(brow=brow) if brow else p["browsDefault"]
    blush_text = p["blush"].format(blush=blush) if blush else p["blushDefault"]
    return p["female" if female else "male"].format(eyeshadow=eyeshadow, blush=blush_text, brows=brows)


# Fidelity line (phrases.json keepLine) for every stage that takes in an A-pose; stages that need more re-assert it per card
# with keyDetails (the Critical details block).

# Details a stage can call out up front in one Critical details block; the later lines then do not repeat them.
# A card picks its own with "keyDetails"; a template without a card choice uses its default here (none = no block).
# "bust" is the shared enlarging line (phrases.json bustKey); "ownBust" is the hero's own physique bust line.
KEY_LABELS = {"hair": "Hair", "bust": "Bust", "ownBust": "Bust", "eyes": "Eyes", "skin": "Skin", "legs": "Legs"}
TEMPLATE_KEY_DEFAULTS = {
    "pose-female-human.txt": ["hair", "bust", "eyes", "skin", "legs"],
    "bare-human.txt": ["hair", "ownBust", "eyes", "skin"],  # the Bare step re-asserts the likeness; the rest of the build is the Body line
    "bare-male-human.txt": ["hair", "eyes", "skin"],
}
# The edit stages run at a high denoise (_templates/heroes/*.txt, 0.7 to 0.95), where the incoming image no longer pins the likeness, so they state it too: the same
# hair, eyes, skin and own-bust lines as the Prime and Bare steps. Hair edits do not restate the hair; a staged scene only restates the face.
for _t in ("armor-human.txt", "clothing-human.txt", "scene-combat-human.txt", "scene-glamour-human.txt", "scene-minimal-human.txt", "scene-with-companion-human.txt",
           "scene-with-outfit-human.txt", "showcase-human.txt", "showcase-photo-human.txt", "pose-view-human.txt", "motion-human.txt"):
    TEMPLATE_KEY_DEFAULTS[_t] = ["hair", "ownBust", "eyes", "skin"]
TEMPLATE_KEY_DEFAULTS["head-human.txt"] = ["hair", "eyes", "skin"]
TEMPLATE_KEY_DEFAULTS["hair-human.txt"] = ["eyes", "skin"]
TEMPLATE_KEY_DEFAULTS["scene-staged-human.txt"] = ["eyes", "skin"]

# Physique fields that make the Figure line, in order (the female schema has bust and hips, the male chest and waist).
FIGURE_FIELDS_FEMALE = ("build", "torso", "bust", "arms", "hips", "legs")
FIGURE_FIELDS_MALE = ("build", "chest", "arms", "waist", "legs")


def apply_figure_profile(hero, profile):
    """figureProfile: standard swaps the hero's individual build for the standard figure (phrases.json standardFigure),
    keeping her bust; any other value keeps her own physique. Card overrides.physique still wins afterwards."""
    if profile != "standard":
        return
    phy = hero["art"]["physique"]
    sex = "female" if "bust" in phy else "male"
    std = phrases()["standardFigure"].get(sex)
    if not std:
        sys.exit(f"ERROR: figureProfile standard has no standardFigure for {sex} in _settings/phrases.json")
    own = set(FIGURE_FIELDS_FEMALE) | set(FIGURE_FIELDS_MALE)
    hero["art"]["physique"] = {**{k: v for k, v in phy.items() if k not in own or k == "bust"}, **std}


def tokens_for(hero, keys=()):
    pal = hero["art"]["palette"]
    phy = hero["art"]["physique"]
    primary = pal["primaryColor"]
    accent = pal["accentColors"][0]
    eyeshadow = pal.get("eyeshadowColor", accent.split()[-1].lower())
    # The Figure line is the physique fields in this order, nothing added by the generator. Items promoted to the
    # Critical details block (bust, legs) are not repeated in it.
    order = FIGURE_FIELDS_FEMALE if "bust" in phy else FIGURE_FIELDS_MALE
    shown = set(keys) | ({"bust"} if "ownBust" in keys else set())
    figure = "; ".join([decap(phy[k]) for k in order if phy.get(k) and k not in shown] + list(phy.get("distinguishingMarks", [])))
    skin = decap(pal["skinTone"])
    eye_neg = ", ".join(pal.get("eyeColorNegatives", []))
    skin_neg = ", ".join(pal.get("skinColorNegatives", []))
    # Generic, PERMANENT hero-specific negatives beyond eye/skin (e.g. a hero who must
    # never show wings/fangs/a tail). May be empty; cleanup() below removes the slack.
    hero_neg = ", ".join(hero["art"].get("negatives", []))
    key_text = {
        "hair": resolve_hair(pal),
        "bust": phrases()["bustKey"] if "bust" in phy else None,
        "ownBust": phy.get("bust"),
        "eyes": pal["eyeColorGlamour"],
        "skin": pal["skinTone"],
        "legs": phy["legs"],
    }
    key_lines = [f"{KEY_LABELS[k]}: {decap(key_text[k])}." for k in keys if key_text.get(k)]
    hair_style = "{{HAIRSTYLE}}; " + decap(resolve_breeze(pal)).rstrip(".")
    return {
        "KEY_BLOCK": ("Critical details - these must be clearly visible:\n" + "\n".join(key_lines)) if key_lines else "",
        "EYE_COLOR_PART": "" if "eyes" in keys else "{{EYE}}, ",
        "SKIN_LINE": "" if "skin" in keys else skin,
        "HERO": hero["name"],
        "PRIMARY": primary,
        "METAL": pal.get("metal", accent.split()[-1].lower()),
        "ACCENT_SOFT": accent.split()[-1].lower(),
        "NAIL": pal.get("nailColor", "Light " + primary.split()[-1]),
        "LIP": pal.get("lipColor", "berry"),
        "EYESHADOW": eyeshadow,
        "BLUSH": pal.get("blushColor", "natural"),
        "LASH": pal.get("lashColor", "black"),
        "BROW": pal.get("browColor", "natural"),
        "MAGIC": pal.get("magicColor", accent.split()[-1].lower()),
        "GEM": pal.get("gemColor", accent.split()[-1].lower()),
        "FIGURE": figure,
        "SKIN": skin,
        "EYE": decap(pal["eyeColorGlamour"]),
        "EYE_SOFT": soft_eye(pal["eyeColorGlamour"]),
        "HAIR": decap(resolve_hair(pal)),
        "HAIR_NEG": ", ".join(pal.get("hairColorNegatives", [])),
        "HAIRSTYLE": decap(resolve_hairstyle(pal)),
        "HAIRSTYLE_NEG": resolve_hairstyle_negatives(pal),
        # One hair block for the A-pose (colour, highlights, style, breeze); later stages keep it through KEEP_LINE.
        "HAIR_ESTABLISH": hair_style if "hair" in keys else "{{HAIR}}; " + hair_style,
        "KEEP_LINE": phrases()["keepLine"]["female" if "bust" in phy else "male"],
        "FACE_STYLE": face_style("bust" in phy, eyeshadow, pal.get("blushColor"), pal.get("browColor")),
        "FIGURE_NEG": phrases()["figureNegatives"]["female" if "bust" in phy else "male"],
        "LEGS": phy["legs"],
        "EYE_NEG": eye_neg,
        "SKIN_NEG": skin_neg,
        "HERO_NEG": hero_neg,
    }


def tokens_for_brand(ident, card):
    """Tokens for the brand templates (data/art/_templates/brand): the lineup of heroes in key-art order, the shared light and
    world, and, for an element icon card (card 'element'), that element's motif with its hero's colour and metal."""
    b = ident["brand"]
    rows = {"front": [], "back": []}
    for i, e in enumerate(b["lineup"], 1):
        if not (ROOT / f"data/art/heroes/drakn-sisters/{e['hero']}-thorne.json").exists():
            sys.exit(f"ERROR: brand lineup hero '{e['hero']}' has no identity under data/art/heroes/drakn-sisters/")
        rows[e["row"]].append(f"{i}) a woman in {e['look']}")
    sky, light = b["sky"], b["light"]
    toks = {
        "NAME": b["name"], "NAME_UPPER": b["name"].upper(), "TAGLINE": b["tagline"], "RIDGE": b["ridge"], "LIGHT": light,
        "LIGHT_SENTENCE": light[0].upper() + light[1:], "SKY": sky, "SKY_SENTENCE": sky[0].upper() + sky[1:],
        "WORLD": b.get("world", ""),
        "LINEUP_FRONT": "; ".join(rows["front"]) + ".", "LINEUP_BACK": "; ".join(rows["back"]) + ".",
    }
    element = card.get("element")
    if element:
        match = next((e for e in b["elements"] if e["element"] == element), None)
        if match is None:
            sys.exit(f"ERROR: brand has no element '{element}' (card {card['artId']})")
        pal = load_json(ROOT / f"data/art/heroes/drakn-sisters/{match['hero']}-thorne.json")["art"]["palette"]
        toks.update({"ELEMENT": element, "MOTIF": match["motif"], "ELEMENT_COLOR": pal["primaryColor"], "ELEMENT_METAL": pal.get("metal", "gold")})
    return toks


def tokens_for_cardart(ident, card):
    """Tokens for the card-art template: the gameplay card's name, element and lore, the shared style, and the category framing."""
    ca = ident["cardart"]
    gp = card_index().get(card["cardId"])
    if gp is None:
        sys.exit(f"ERROR: card-art card {card['artId']} names cardId '{card['cardId']}' but no such card exists under data/cards/")
    cat = ca["categories"].get(card["category"])
    el = ca["elements"].get(gp.get("element", "Neutral"))
    if cat is None or el is None:
        sys.exit(f"ERROR: card-art card {card['artId']}: unknown category '{card['category']}' or element '{gp.get('element')}'")
    return {
        "NAME": gp.get("creatureType") or gp["name"], "LORE": gp.get("lore", "").strip(), "STYLE": ca["style"],
        "FRAMING": cat["framing"][0].upper() + cat["framing"][1:], "BACKGROUND": cat["background"],
        "ELEMENT_LINE": f"Colour palette of {el['color']}, with {el['fx']} around the subject.",
        "GRANDEUR": phrases()["grandeur"].get(gp.get("rarity", {}).get("tier", "Common"), ""),
    }


def tokens_for_dragon(dragon):
    """A dragon identity (data/art/dragons/elder-dragons/*.json) has no 'art' section
    -- no palette/physique, since it's not a humanoid hero. Its tokens are its
    name/element (pulled from its gameplay card by load_identity) and its own
    description, for the dragon archetype's text-to-image templates (no incoming
    reference image to edit -- a dragon is generated entirely from its description,
    unlike a hero's img2img pipeline)."""
    morphology = phrases()["dragonMorphology"]
    fields = {k: label for k, label in morphology.items() if k not in ("notes", "headFields") and dragon.get(k)}

    def line(keys):
        return " ".join(label.format(decap(dragon[k]).rstrip(".")) for k, label in fields.items() if k in keys)

    return {
        "DRAGON": dragon["name"],
        "DESCRIPTION": dragon["description"],
        "MORPHOLOGY": line(fields),
        "MORPHOLOGY_HEAD": line(morphology["headFields"]),
        "ELEMENT": dragon.get("element", ""),
    }


_COMPONENT_META_KEYS = {"id", "kind", "name", "compatibleStages", "sourceVariant", "status", "notes", "mood", "element", "tags", "backgroundRealm"}


# A motion's own default gaze/expression are stored under these names so the
# slot/field they describe (gaze, expression) stays a distinct, independently
# overridable concern -- not baked into "motion" itself. See data/art/README.md
# "Field-name vocabulary" and data/art/_schema/field-vocabulary.json.
_FIELD_ALIASES = {"defaultGaze": "gaze", "defaultExpression": "expression"}

_FIELD_VOCAB = load_json(ROOT / "data/art/_schema/field-vocabulary.json")


def _resolve_field_value(key, val):
    """A field's value (e.g. a motion's defaultGaze/defaultExpression) may itself
    be a path to a shared motion/gaze or motion/expressions piece -- for a default
    that's genuinely reused across several motions -- instead of inline literal
    text -- for a one-off default unique to that motion. Resolve a path reference
    down to its own plain-text value; a literal string passes through unchanged.
    This is the read-side counterpart to _is_literal_ref (the write/override side
    used by components.<slot>) -- same path-or-literal duality, single source of
    truth instead of copy-pasted duplicate text drifting apart over time."""
    if not (isinstance(val, str) and val.lower().endswith(".json") and (ROOT / val).exists()):
        return val
    canonical = _FIELD_ALIASES.get(key, key)
    piece = load_piece(ROOT / val)
    return piece.get(canonical, val)


def resolve_component_tokens(card):
    """A base-set card may reference a reusable component (data/art/hair/*.json,
    data/art/motion/*.json, ...). Every non-metadata field becomes a token of the
    same name, UPPERCASED (snake_case fields -> TOKEN_NAME; defaultGaze/
    defaultExpression -> GAZE/EXPRESSION, their canonical alias); list fields
    (e.g. 'extras') join with newlines. Lets Hair/Motion/Armor stages compose a
    prompt from hero data + a reusable, hero-agnostic component."""
    ref = card.get("component")
    if not ref:
        return {}
    component = load_piece(ROOT / ref)
    toks = {}
    for key, val in component.items():
        if key in _COMPONENT_META_KEYS:
            continue
        token = _FIELD_ALIASES.get(key, key).upper()
        val = _resolve_field_value(key, val)
        toks[token] = "\n".join(val) if isinstance(val, list) else val
    return toks


def _is_literal_ref(ref):
    """A components.<slot> value is either a path to a piece JSON, or -- for a
    quick final tweak, or a one-off scene authored entirely from scratch -- a
    literal inline string used directly as that slot's own content."""
    path = ROOT / ref
    return not (ref.lower().endswith(".json") and path.exists())


_EXTEND_PREFIX = "+"


def resolve_components_tokens(card):
    """A base-set card may compose a prompt from SEVERAL named-slot pieces instead
    of one complete component -- 'components': {'wearing': '<path>', 'jewelry':
    '<path>', 'back': '<path>', ...}. This is how a full outfit (armor/clothing) is
    assembled from small, independently reusable pieces (a necklace, a cape, a
    weapon) instead of re-describing jewelry inline in every complete-outfit file.
    The token takes the SLOT's name (not the piece file's own field name) -- e.g.
    components.jewelry -> {{JEWELRY}} -- so any interchangeable piece can fill that
    slot. Always exactly ONE token per slot, regardless of how many content fields
    the piece has (joined with spaces if more than one) -- this is what lets a
    scene reference a rich multi-field motion component (body/head/pose/...) for
    its 'pose' slot without exploding into a dozen new per-field template tokens.
    Keep the template's token surface flat and small; let pieces be rich.

    A slot's value may also be a literal inline string instead of a path (see
    _is_literal_ref) -- a quick scene-level tweak, or a fully from-scratch scene,
    without needing a reusable piece file at all.

    Field-name override rule: fields marked "overridable" in
    data/art/_schema/field-vocabulary.json (currently: gaze, expression) can be
    swapped independently of the piece that embeds them. If a slot's own content
    has a field whose canonical name (see _FIELD_ALIASES) matches the slot's own
    name -- e.g. components.expression -> a piece/literal with field 'expression'
    -- that value is registered as an override. Any OTHER slot's piece with a
    field of that same canonical name (e.g. a motion's own 'defaultExpression')
    gets it SUBSTITUTED IN PLACE, not just dropped -- so a motion's embedded
    default expression is silently replaced by an explicit components.expression
    override inside the motion's own joined {{POSE}} text, with no risk of both
    showing up and contradicting each other, and no template changes required.
    Non-overridable fields (body, head, pose, ...) can never be hijacked this way
    even if a future slot happens to share a field name -- only fields explicitly
    opted into the registry participate.

    Override vs extend: a literal override value that starts with "+" (e.g.
    "+teeth just visible, a faint smirk.") EXTENDS whatever the default would
    otherwise have been (the motion's own defaultExpression/defaultGaze, or
    another slot's value for that canonical field) instead of replacing it --
    appended after it. A plain literal or a piece reference (no "+") is a full
    replace, as before. Lets a scene reuse a proven, "validated" default and only
    tweak the one small thing that's different this time, instead of re-authoring
    the whole expression/gaze from scratch for a minor variation."""
    slots = card.get("components")
    if not slots:
        return {}

    piece_content = {}
    extensions = {}
    for slot, ref in slots.items():
        if isinstance(ref, str) and ref.startswith(_EXTEND_PREFIX):
            extensions[slot] = ref[len(_EXTEND_PREFIX):].strip()
            continue
        if _is_literal_ref(ref):
            piece_content[slot] = {slot: ref}
            continue
        piece = load_piece(ROOT / ref)
        content = {k: v for k, v in piece.items() if k not in _COMPONENT_META_KEYS}
        for field in content:
            canonical = _FIELD_ALIASES.get(field, field)
            if canonical not in _FIELD_VOCAB:
                sys.exit(f"ERROR: unknown field '{field}' in {ref} -- "
                         f"add it to data/art/_schema/field-vocabulary.json")
        piece_content[slot] = {k: _resolve_field_value(k, v) for k, v in content.items()}

    # An extend-mode slot has no content of its own yet -- its base is whatever
    # other slot's piece carries that canonical field (e.g. the "pose" slot's
    # motion carries defaultExpression). No base found just falls back to the
    # fragment alone, which is harmless.
    for slot, fragment in extensions.items():
        base = ""
        for other_slot, content in piece_content.items():
            for field, val in content.items():
                if _FIELD_ALIASES.get(field, field) == slot:
                    base = val
        piece_content[slot] = {slot: (base + " " + fragment).strip() if base else fragment}

    overrides = {}
    for slot, content in piece_content.items():
        for field, val in content.items():
            canonical = _FIELD_ALIASES.get(field, field)
            if canonical == slot and _FIELD_VOCAB.get(canonical, {}).get("overridable"):
                overrides[canonical] = val

    toks = {}
    for slot, content in piece_content.items():
        # A piece's 'negatives' list feeds a separate {{<SLOT>_NEG}} token, not the slot's own text.
        neg = content.pop("negatives", None)
        if neg is not None:
            toks[slot.upper() + "_NEG"] = ", ".join(neg)
        parts = []
        for key, val in content.items():
            canonical = _FIELD_ALIASES.get(key, key)
            if key != slot and canonical in overrides:
                val = overrides[canonical]
            parts.append("\n".join(val) if isinstance(val, list) else val)
        toks[slot.upper()] = " ".join(p for p in parts if p)
    return toks


def generate(card_path, tokens_only=False):
    card = load_json(ROOT / card_path)
    hero = load_identity(card["heroArt"])
    if "art" in hero:
        apply_figure_profile(hero, card.get("figureProfile", "individual"))
    # Base-set card may override any palette/physique attribute from the hero definition.
    overrides = card.get("overrides", {})
    for section in ("palette", "physique"):
        if section in overrides:
            hero["art"][section].update(overrides[section])
    template = (ROOT / card["template"]).read_text(encoding="utf-8")
    contour = card.get("components", {}).get("body_contour")
    default_contour = studio_defaults().get("bodyContour", "off")
    if isinstance(default_contour, dict):  # per-stage defaults with a "default" fallback
        default_contour = default_contour.get(card["stage"], default_contour.get("default", "off"))
    if contour == "off":  # a card can opt out of the global default
        card["components"].pop("body_contour")
    elif contour is None and "{{BODY_CONTOUR}}" in template and default_contour != "off" and "physique" in hero.get("art", {}):
        male = "bust" not in hero["art"]["physique"]  # male heroes use the <piece>-male variant
        piece = f"data/art/wardrobe/effects/contour/{default_contour}{'-male' if male else ''}.json"
        if (ROOT / piece).exists():
            card.setdefault("components", {})["body_contour"] = piece
    sex = None
    if "art" in hero:
        sex = "female" if "bust" in hero["art"]["physique"] else "male"
        hero_defaults = {"underlayer": "defaultUnderlayer", "footwear": "defaultFootwear", "sheen": "defaultSheen", "realm": "defaultRealm"}
        for slot in SLOT_DEFAULTS:
            # Footwear and sheen tokens live inside the underlayer pieces, so any template with an underlayer needs them.
            uses_slot = "{{" + slot.upper() + "}}" in template or (slot in ("footwear", "sheen") and "{{UNDERLAYER}}" in template)
            if uses_slot:
                default = default_slot(slot, card["stage"], sex)
                # The realm (how realistic the world looks) can be set for a whole group in _settings/studio.json realmByGroup, and a hero's art.defaultRealm wins over it.
                if slot == "realm":
                    default = studio_defaults().get("realmByGroup", {}).get(group_of(card_path), default)
                # A hero can carry her own default underlayer (her signature metallic look) and shoe.
                if hero["art"].get(hero_defaults.get(slot, "")):
                    default = hero["art"][hero_defaults[slot]]
                # One switch for every A-pose: _settings/studio.json aPoseFootwear = "barefoot" replaces each sister's heels.
                if slot == "footwear" and card["stage"] in ("pose", "alpha") and sex == "female" and studio_defaults().get("aPoseFootwear") == "barefoot":
                    default = BAREFOOT_A_POSE
                if default:
                    card.setdefault("components", {}).setdefault(slot, default)
    # A dragon or brand identity has no 'art' section (not humanoid) -- its own, simpler token set.
    keys = card.get("keyDetails", TEMPLATE_KEY_DEFAULTS.get(pathlib.Path(card["template"]).name, []))
    unknown = [k for k in keys if k not in KEY_LABELS]
    if unknown:
        sys.exit(f"ERROR: {card_path}: unknown keyDetails {unknown}; use {sorted(KEY_LABELS)}")
    if "art" in hero:
        toks = tokens_for(hero, keys)
    elif hero.get("kind") == "brand":
        toks = tokens_for_brand(hero, card)
    elif hero.get("kind") == "cardart":
        toks = tokens_for_cardart(hero, card)
    else:
        toks = tokens_for_dragon(hero)
    toks.update(resolve_component_tokens(card))
    toks.update(resolve_components_tokens(card))
    for neg_token in ("FOOTWEAR_NEG", "UNDERLAYER_NEG", "WEARING_NEG", "EXPRESSION_NEG"):
        if "{{" + neg_token + "}}" in template:
            toks.setdefault(neg_token, "")  # only a piece that carries negatives (barefoot, bareskin) fills it
    # A makeup piece (components.makeup) replaces the default studio face-styling line everywhere,
    # and also feeds scene templates through the optional {{MAKEUP_LINE}}.
    if toks.get("MAKEUP"):
        toks["MAKEUP_LINE"] = "Makeup: " + toks["MAKEUP"].rstrip(".") + "."
        toks["FACE_STYLE"] = toks["MAKEUP_LINE"]
    # Literal, per-card one-off strings that aren't reusable pieces on their own
    # (e.g. this specific composed outfit's display "name" or "aesthetic" line).
    _CARD_META_KEYS = {"artId", "kind", "stage", "heroArt", "component", "components",
                        "template", "output", "denoise", "overrides", "notes", "hairFrom", "keyDetails", "figureProfile"}
    # hairFrom: "incoming" makes a complete scene take hair from the incoming image instead of the hero's description.
    if card.get("hairFrom") == "incoming" and "HAIR" in toks:
        toks["HAIR"] = phrases()["hairFromIncoming"]
    for key, val in card.items():
        if key not in _CARD_META_KEYS and isinstance(val, str):
            toks[key.upper()] = val

    # Pieces can embed hero-level tokens (e.g. {{PRIMARY}}, {{ACCENT_SOFT}}) in their
    # own text -- this is what makes a wardrobe/ piece genuinely reusable across every
    # hero (same piece file, each hero's own colour) instead of duplicated per-hero.
    # Two passes: a piece can embed {{FOOTWEAR}}, whose own text embeds {{PRIMARY}}.
    for _ in range(2):
        for key, val in toks.items():
            for other_key, other_val in toks.items():
                if other_key != key:
                    val = val.replace("{{" + other_key + "}}", other_val)
            toks[key] = val

    if tokens_only:
        return toks

    template = apply_optional_lines(template, toks)
    needed = set(re.findall(r"{{(\w+)}}", template))
    missing = needed - set(toks)
    if missing:
        sys.exit(f"ERROR: template needs tokens with no value: {sorted(missing)}")

    out = template
    for key, val in toks.items():
        out = out.replace("{{" + key + "}}", val)
    out = cleanup(out)
    if sex == "male":
        out = masculine(out)

    # Rare escape hatch: base-set card may still remove a specific negative term
    # that neither the universal template nor the hero's own data accounts for.
    for term in overrides.get("negativeRemove", []):
        out = out.replace(term + ", ", "").replace(", " + term, "")

    # Per-render addition: this specific card/stage bans something extra (e.g. an
    # armor variant that must never show bracers, or a crown-free stance).
    add = overrides.get("negativeAdd", [])
    if add:
        out = out.rstrip()
        if out.endswith("."):
            out = out[:-1] + ", " + ", ".join(add) + ".\n"

    leftover = re.findall(r"{{\w+}}", out)
    if leftover:
        sys.exit(f"ERROR: unresolved tokens remain: {leftover}")

    dst = ROOT / card["output"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(f"wrote {card['output']}")
    return card["output"]


_NOT_POSSESSIVE = r"(?:and|or|to|with|as|in|on|at|from|so|while|by|toward|towards|into|onto|of|for|than|but|then|when|until|if)"
_MASCULINE = [
    (r"\bherself\b", "himself"), (r"\bHerself\b", "Himself"), (r"\bhers\b", "his"), (r"\bShe\b", "He"), (r"\bshe\b", "he"),
    (rf"\bher(?=\s+(?!{_NOT_POSSESSIVE}\b)[A-Za-z-])", "his"), (rf"\bHer(?=\s+(?!{_NOT_POSSESSIVE}\b)[A-Za-z-])", "His"),
    (r"\bher\b", "him"), (r"\bHer\b", "Him"),
]


def masculine(text):
    """Pieces and scene text are mostly written for women (a motion's "her hair", a hairstyle's "she"); a male hero's finished prompt gets he / his / him instead."""
    for pattern, repl in _MASCULINE:
        text = re.sub(pattern, repl, text)
    return text


def cleanup_orphans(expected_outputs, apply=False):
    """Two-phase plan/apply, like `terraform plan`/`apply`: always finds candidate
    orphans -- any .txt sitting in a directory that received at least one output THIS
    run, but which isn't itself one of the outputs just (re)generated (e.g. a stale
    file left behind after a card's artId/output was renamed). Deliberately scoped to
    the EXACT directories touched (not the whole group) -- a narrow --slug/--stage run
    must never flag a sibling hero's untouched files as orphans just because they
    weren't part of this run. Only DELETES when apply=True; otherwise a safe,
    side-effect-free preview. Never touches prompts/_archive/ (not generator-tracked)."""
    dirs_touched = {(ROOT / out).parent for out in expected_outputs}
    found = []
    for d in dirs_touched:
        for txt in d.glob("*.txt"):
            rel = str(txt.relative_to(ROOT)).replace("\\", "/")
            if rel not in expected_outputs:
                found.append((rel, txt))
    if apply:
        for _, txt in found:
            txt.unlink()
    return [rel for rel, _ in found]


def iter_card_paths(group="*", slug="*", stage="*", family=None):
    """Every card under data/art/_sets/<group>/<slug>/ (the folders below the slug are the pipeline phase and family), narrowed by the
    card's own stage (as written in the card or as its prompt folder, e.g. pose or poses) and by a family folder of its output."""
    base = ROOT / "data/art/_sets"
    paths = sorted(base.glob(f"{group}/**/*.json"))
    if slug != "*":  # the slug folder follows the group, or the group's division folder; a division named like the slug (female, male) is not a hero
        def hero_folder(p):
            parts = p.relative_to(base).parts
            return parts[2] if len(parts) > 2 and parts[1] in art_layout.divisions(parts[0]) else parts[1]
        paths = [p for p in paths if hero_folder(p) == slug]
    if stage == "*" and not family:
        return paths
    keep = []
    for p in paths:
        card = json.loads(p.read_text(encoding="utf-8"))
        if stage != "*" and stage not in (card.get("stage"), art_layout.stage_folder(card.get("stage", ""))):
            continue
        if family and family not in art_layout.parse_dirs(pathlib.PurePosixPath(card.get("output", "")).parts[3:-1])[1]:
            continue
        keep.append(p)
    return keep


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("card", nargs="?", help="Path to one exact card JSON (back-compat).")
    parser.add_argument("--group", default="*", help="e.g. drakn-sisters, angel-primes")
    parser.add_argument("--slug", default="*", help="a hero/entity slug within the group")
    parser.add_argument("--stage", default="*", help="e.g. pose, head, hair, motion")
    parser.add_argument("--family", default=None, help="e.g. down, walking, romantic")
    parser.add_argument("--cleanup", action="store_true",
                        help="Check for .txt files under prompts/<group>/ (for any group touched "
                             "this run) that no longer match a current card's output -- e.g. "
                             "leftovers from a renamed artId/output. By DEFAULT this only PREVIEWS "
                             "what it would remove (safe, no deletions) -- pass --yes too to "
                             "actually delete. Never touches prompts/_archive/.")
    parser.add_argument("--yes", action="store_true",
                        help="Combined with --cleanup, actually deletes the orphaned files found. "
                             "Without this, --cleanup only lists them (dry-run).")
    args = parser.parse_args()

    if args.card:
        generate(args.card)
        return

    paths = iter_card_paths(args.group, args.slug, args.stage, args.family)
    if not paths:
        sys.exit("No cards matched the given filters.")

    ok = fail = 0
    expected_outputs = set()
    for p in paths:
        rel = str(p.relative_to(ROOT))
        try:
            out = generate(rel)
            expected_outputs.add(out)
            ok += 1
        except SystemExit as e:
            print(f"FAILED {rel}: {e}")
            fail += 1
    print(f"ok={ok} fail={fail}")

    if args.cleanup:
        found = cleanup_orphans(expected_outputs, apply=args.yes)
        if found:
            verb = "removed" if args.yes else "would remove"
            print(f"cleanup: {verb} {len(found)} orphaned file(s):")
            for r in found:
                print(f"  - {r}")
            if not args.yes:
                print("cleanup: this was a preview -- re-run with --cleanup --yes to actually delete these.")
        else:
            print("cleanup: no orphaned files found")


if __name__ == "__main__":
    main()
