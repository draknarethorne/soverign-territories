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
    skin = decap(pal["skinTone"]) + " complexion, evenly tanned, no pale areas"
    return {
        "HERO": hero["name"],
        "PRIMARY": primary,
        "ACCENT_SOFT": accent.split()[-1].lower(),
        "NAIL": "Light " + primary.split()[-1],
        "FIGURE": figure,
        "SKIN": skin,
        "EYE": decap(pal["eyeColorGlamour"]),
        "HAIR": decap(pal["hairColor"]),
        "HAIRSTYLE": decap(pal["hairStyle"]),
    }


def generate(card_path):
    card = load_json(ROOT / card_path)
    hero = load_json(ROOT / card["heroFile"])
    template = (ROOT / card["template"]).read_text(encoding="utf-8")
    toks = tokens_for(hero)

    needed = set(re.findall(r"{{(\w+)}}", template))
    missing = needed - set(toks)
    if missing:
        sys.exit(f"ERROR: template needs tokens with no value: {sorted(missing)}")

    out = template
    for key, val in toks.items():
        out = out.replace("{{" + key + "}}", val)

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
