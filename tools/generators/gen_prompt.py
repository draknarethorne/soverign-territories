#!/usr/bin/env python3
"""Generate a prompt .txt from an art-source card + hero card + stage template.

Reads a card (data/art/_sets/<group>/<slug>/<stage>/[<family>/]<name>.json), pulls traits
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

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))


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


def cleanup(text):
    """Collapse artifacts left by empty tokens (e.g. an empty HERO_NEG between two
    literal commas): ', , ' -> ', ', and an empty token right before the trailing
    period (', .' -> '.', when HERO_NEG is the last item in a negative list)."""
    while ", ," in text:
        text = text.replace(", ,", ",")
    while ", ." in text:
        text = text.replace(", .", ".")
    return text


def resolve_hairstyle(pal):
    """HAIRSTYLE comes either from a referenced component (data/art/hair/*.json,
    field 'aPoseStyle') or, for back-compat, a plain 'hairStyle' string on the hero.
    A component reference lets a hero carry a unique/signature A-pose hairstyle
    with a one-line swap, instead of every hero inlining the same text."""
    if "hairStyleComponent" in pal:
        component = load_json(ROOT / pal["hairStyleComponent"])
        return component["a_pose_style"]
    return pal["hairStyle"]


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
    "framing": {"*": "data/art/shots/framing/bust-up.json"},
    "view": {
        "head": "data/art/shots/views/head/front.json",
        "pose": "data/art/shots/views/body/front.json",
    },
    "expression": {
        "head": "data/art/motion/expressions/studio-glamour-smile.json",
        "pose": {
            "female": "data/art/motion/expressions/studio-glamour.json",
            "male": "data/art/motion/expressions/studio-confident.json",
        },
    },
    "underlayer": {
        "pose": {
            "female": "data/art/wardrobe/swimwear/triangle-bikini.json",
            "male": "data/art/wardrobe/swimwear/swim-brief.json",
        },
    },
}


def default_slot(slot, stage, sex):
    entry = SLOT_DEFAULTS[slot]
    value = entry.get(stage, entry.get("*"))
    if isinstance(value, dict):
        value = value[sex]
    return value

# One shared studio face-styling line for every cream-backdrop stage, so makeup stays
# present-but-subtle and identical from the full-body shot to the close-up.
FACE_STYLE = {
    "female": "Makeup: soft and natural, with a subtly blended {{ACCENT_SOFT}}-toned eyeshadow, a light natural blush, "
              "groomed brows and softly defined eyes - present for the character's theme but never heavy or overly accented.",
    "male": "Grooming: natural, clean and well-groomed, groomed brows, no cosmetics.",
}


# Bust bans only make sense for the female physique; a male hero gets none.
FIGURE_NEG = {
    "female": "flat chest, small bust, narrow bust, flattened breasts, wide-set breasts, wide cleavage gap, reduced bust size",
    "male": "",
}


def tokens_for(hero):
    pal = hero["art"]["palette"]
    phy = hero["art"]["physique"]
    primary = pal["primaryColor"]
    accent = pal["accentColors"][0]
    if "bust" in phy:
        figure = "; ".join([
            decap(phy["build"]),
            decap(phy["bust"]),
            "slim waist",
            decap(phy["hips"]),
            "slim, tapering thighs",
            decap(phy["legs"]),
        ])
    else:
        # Male physique schema: build/chest/waist/legs (no bust/hips).
        figure = "; ".join([
            decap(phy["build"]),
            decap(phy["chest"]),
            decap(phy["waist"]),
            decap(phy["legs"]),
        ])
    skin = decap(pal["skinTone"])
    eye_neg = ", ".join(pal.get("eyeColorNegatives", []))
    skin_neg = ", ".join(pal.get("skinColorNegatives", []))
    # Generic, PERMANENT hero-specific negatives beyond eye/skin (e.g. a hero who must
    # never show wings/fangs/a tail). May be empty; cleanup() below removes the slack.
    hero_neg = ", ".join(hero["art"].get("negatives", []))
    return {
        "HERO": hero["name"],
        "PRIMARY": primary,
        "ACCENT_SOFT": accent.split()[-1].lower(),
        "NAIL": "Light " + primary.split()[-1],
        "FIGURE": figure,
        "SKIN": skin,
        "EYE": decap(pal["eyeColorGlamour"]),
        "EYE_SOFT": soft_eye(pal["eyeColorGlamour"]),
        "HAIR": decap(pal["hairColor"]),
        "HAIRSTYLE": decap(resolve_hairstyle(pal)),
        "HAIRSTYLE_NEG": resolve_hairstyle_negatives(pal),
        "FACE_STYLE": FACE_STYLE["female" if "bust" in phy else "male"],
        "FIGURE_NEG": FIGURE_NEG["female" if "bust" in phy else "male"],
        "LEGS": phy["legs"],
        "EYE_NEG": eye_neg,
        "SKIN_NEG": skin_neg,
        "HERO_NEG": hero_neg,
    }


def tokens_for_dragon(dragon):
    """A dragon identity (data/art/dragons/elder-dragons/*.json) has no 'art' section
    -- no palette/physique, since it's not a humanoid hero. Its tokens are its
    name/element (pulled from its gameplay card by load_identity) and its own
    description, for the dragon archetype's text-to-image templates (no incoming
    reference image to edit -- a dragon is generated entirely from its description,
    unlike a hero's img2img pipeline)."""
    return {
        "DRAGON": dragon["name"],
        "DESCRIPTION": dragon["description"],
        "ELEMENT": dragon.get("element", ""),
    }


_COMPONENT_META_KEYS = {"id", "kind", "name", "compatibleStages", "sourceVariant", "status", "notes", "mood", "element", "tags"}


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
    piece = load_json(ROOT / val)
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
    component = load_json(ROOT / ref)
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
        piece = load_json(ROOT / ref)
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


def generate(card_path):
    card = load_json(ROOT / card_path)
    hero = load_identity(card["heroArt"])
    # Base-set card may override any palette/physique attribute from the hero definition.
    overrides = card.get("overrides", {})
    for section in ("palette", "physique"):
        if section in overrides:
            hero["art"][section].update(overrides[section])
    template = (ROOT / card["template"]).read_text(encoding="utf-8")
    sex = None
    if "art" in hero:
        sex = "female" if "bust" in hero["art"]["physique"] else "male"
        for slot in SLOT_DEFAULTS:
            if "{{" + slot.upper() + "}}" in template:
                default = default_slot(slot, card["stage"], sex)
                if default:
                    card.setdefault("components", {}).setdefault(slot, default)
    # A dragon identity has no 'art' section (not humanoid) -- its own, simpler token set.
    toks = tokens_for_dragon(hero) if "art" not in hero else tokens_for(hero)
    toks.update(resolve_component_tokens(card))
    toks.update(resolve_components_tokens(card))
    # Literal, per-card one-off strings that aren't reusable pieces on their own
    # (e.g. this specific composed outfit's display "name" or "aesthetic" line).
    _CARD_META_KEYS = {"artId", "kind", "stage", "heroArt", "component", "components",
                        "template", "output", "denoise", "overrides", "notes"}
    for key, val in card.items():
        if key not in _CARD_META_KEYS and isinstance(val, str):
            toks[key.upper()] = val

    # Pieces can embed hero-level tokens (e.g. {{PRIMARY}}, {{ACCENT_SOFT}}) in their
    # own text -- this is what makes a wardrobe/ piece genuinely reusable across every
    # hero (same piece file, each hero's own colour) instead of duplicated per-hero.
    # One pass is enough: hero-level tokens (inserted first, from tokens_for) never
    # themselves contain further placeholders.
    for key, val in toks.items():
        for other_key, other_val in toks.items():
            if other_key != key:
                val = val.replace("{{" + other_key + "}}", other_val)
        toks[key] = val

    needed = set(re.findall(r"{{(\w+)}}", template))
    missing = needed - set(toks)
    if missing:
        sys.exit(f"ERROR: template needs tokens with no value: {sorted(missing)}")

    out = template
    for key, val in toks.items():
        out = out.replace("{{" + key + "}}", val)
    out = cleanup(out)

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
    """Glob data/art/_sets/<group>/<slug>/<stage>/[<family>/]*.json. "**" absorbs the
    optional family level, since some stages (pose, head) have no family subfolder."""
    base = ROOT / "data/art/_sets"
    pattern = f"{group}/{slug}/{stage}/{family}/**/*.json" if family else f"{group}/{slug}/{stage}/**/*.json"
    return sorted(base.glob(pattern))


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
