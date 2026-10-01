#!/usr/bin/env python3
"""Generate a prompt .txt from an art-source card + hero card + stage template.

Pilot scope: X_Pose. Reads an art-source card (data/art/base-set/<hero>/<art>.json),
pulls traits from the referenced hero card, fills the {{TOKEN}} slots in the template,
and writes the output .txt. Model-agnostic — the output feeds any ComfyUI workflow.

Usage:
    python tools/generators/gen_prompt.py [art-card.json]
Defaults to the Drakness X-Pose card.
"""
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
    literal commas): ', , ' -> ', ', and a stray '.  ' -> '. '."""
    while ", ," in text:
        text = text.replace(", ,", ",")
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
    figure = "; ".join([
        decap(phy["build"]),
        decap(phy["bust"]),
        "slim waist",
        decap(phy["hips"]),
        "slim, tapering thighs",
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


_COMPONENT_META_KEYS = {"id", "kind", "name", "compatibleStages", "sourceVariant", "status", "notes"}


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


if __name__ == "__main__":
    card = sys.argv[1] if len(sys.argv) > 1 else "data/art/base-set/drakness/drakness-x-pose.json"
    generate(card)
