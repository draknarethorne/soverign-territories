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
Filters compose (all default to "any"); omitting all of them generates every card under
data/art/_sets/.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))


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
        "HAIR": decap(pal["hairColor"]),
        "HAIRSTYLE": decap(resolve_hairstyle(pal)),
        "LEGS": phy["legs"],
        "EYE_NEG": eye_neg,
        "SKIN_NEG": skin_neg,
        "HERO_NEG": hero_neg,
    }


_COMPONENT_META_KEYS = {"id", "kind", "name", "compatibleStages", "sourceVariant", "status", "notes", "mood"}


def resolve_component_tokens(card):
    """A base-set card may reference a reusable component (data/art/hair/*.json,
    data/art/motion/*.json, ...). Every non-metadata field becomes a token of the
    same name, UPPERCASED (snake_case fields -> TOKEN_NAME); list fields (e.g.
    'extras') join with newlines. Lets Hair/Motion/Armor stages compose a prompt
    from hero data + a reusable, hero-agnostic component."""
    ref = card.get("component")
    if not ref:
        return {}
    component = load_json(ROOT / ref)
    toks = {}
    for key, val in component.items():
        if key in _COMPONENT_META_KEYS:
            continue
        token = key.upper()
        toks[token] = "\n".join(val) if isinstance(val, list) else val
    return toks


def resolve_components_tokens(card):
    """A base-set card may compose a prompt from SEVERAL named-slot pieces instead
    of one complete component -- 'components': {'wearing': '<path>', 'jewelry':
    '<path>', 'back': '<path>', ...}. This is how a full outfit (armor/clothing) is
    assembled from small, independently reusable pieces (a necklace, a cape, a
    weapon) instead of re-describing jewelry inline in every complete-outfit file.
    The token takes the SLOT's name (not the piece file's own field name) -- e.g.
    components.jewelry -> {{JEWELRY}} -- so any interchangeable piece can fill that
    slot. A piece file's single content field (by convention 'description') becomes
    that token directly; a piece with several content fields gets them namespaced
    as SLOT_FIELD."""
    slots = card.get("components")
    if not slots:
        return {}
    toks = {}
    for slot, ref in slots.items():
        piece = load_json(ROOT / ref)
        content = {k: v for k, v in piece.items() if k not in _COMPONENT_META_KEYS}
        if len(content) == 1:
            (val,) = content.values()
            toks[slot.upper()] = "\n".join(val) if isinstance(val, list) else val
        else:
            for key, val in content.items():
                toks[f"{slot.upper()}_{key.upper()}"] = "\n".join(val) if isinstance(val, list) else val
    return toks


def generate(card_path):
    card = load_json(ROOT / card_path)
    hero = load_json(ROOT / card["heroArt"])
    # Base-set card may override any palette/physique attribute from the hero definition.
    overrides = card.get("overrides", {})
    for section in ("palette", "physique"):
        if section in overrides:
            hero["art"][section].update(overrides[section])
    template = (ROOT / card["template"]).read_text(encoding="utf-8")
    toks = tokens_for(hero)
    toks.update(resolve_component_tokens(card))
    toks.update(resolve_components_tokens(card))
    # Literal, per-card one-off strings that aren't reusable pieces on their own
    # (e.g. this specific composed outfit's display "name" or "aesthetic" line).
    _CARD_META_KEYS = {"artId", "kind", "stage", "heroArt", "component", "components",
                        "template", "output", "denoise", "overrides", "notes"}
    for key, val in card.items():
        if key not in _CARD_META_KEYS and isinstance(val, str):
            toks[key.upper()] = val

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
    args = parser.parse_args()

    if args.card:
        generate(args.card)
        return

    paths = iter_card_paths(args.group, args.slug, args.stage, args.family)
    if not paths:
        sys.exit("No cards matched the given filters.")

    ok = fail = 0
    for p in paths:
        rel = str(p.relative_to(ROOT))
        try:
            generate(rel)
            ok += 1
        except SystemExit as e:
            print(f"FAILED {rel}: {e}")
            fail += 1
    print(f"ok={ok} fail={fail}")


if __name__ == "__main__":
    main()
