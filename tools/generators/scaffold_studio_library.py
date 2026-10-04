#!/usr/bin/env python3
"""Scaffold the studio reference library for ONE hero, all derived from that hero's A-pose.

Writes assembly cards under data/art/_sets/<group>/<slug>/ (re-runnable: it overwrites its own
files only). Every card is a thin recipe: a template plus tag slots (view / framing /
expression / underlayer) that point at proven pieces under data/art/. Then run
tools/generators/gen_prompt.py --group <group> --slug <slug> to produce the prompts.

Library (per hero):
  pose views  : 3/4 left+right, profile left+right, back, back glance      (pose-view-human.txt)
  head views  : 3/4 left+right, profile left+right, looking down, chin up,
                over the shoulder, head tilt                                (head-human.txt)
  head framing: face close-up, chest-and-hair                               (head-human.txt)
  expressions : soft closed smile, sultry, serious, joyful laugh            (head-human.txt)
The front-facing A-pose and the default glamour-smile head are the hero's existing X cards.

Example:
  python tools/generators/scaffold_studio_library.py --group angel-primes --slug angelica-prime \
      --hero Angelica --underlayer data/art/heroes/angel-primes/angelica-prime/wearing/angelic-pastel-bikini.json
"""
import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
VIEW = "data/art/studio/views"
POSE_VIEW_TEMPLATE = "data/art/_templates/heroes/pose-view-human.txt"
HEAD_TEMPLATE = "data/art/_templates/heroes/head-human.txt"

# (slug, display name, piece)
POSE_VIEWS = [
    ("three-quarter-left", "Three-Quarter Left", f"{VIEW}/body/three-quarter-left.json"),
    ("three-quarter-right", "Three-Quarter Right", f"{VIEW}/body/three-quarter-right.json"),
    ("profile-left", "Profile Left", f"{VIEW}/body/profile-left.json"),
    ("profile-right", "Profile Right", f"{VIEW}/body/profile-right.json"),
    ("back", "Back", f"{VIEW}/body/back.json"),
    ("back-glance", "Back Glance", f"{VIEW}/body/back-glance.json"),
]
HEAD_VIEWS = [
    ("three-quarter-left", "Three-Quarter Left", f"{VIEW}/head/three-quarter-left.json"),
    ("three-quarter-right", "Three-Quarter Right", f"{VIEW}/head/three-quarter-right.json"),
    ("profile-left", "Profile Left", f"{VIEW}/head/profile-left.json"),
    ("profile-right", "Profile Right", f"{VIEW}/head/profile-right.json"),
    ("looking-down", "Looking Down", f"{VIEW}/head/looking-down.json"),
    ("chin-up", "Chin Up", f"{VIEW}/head/chin-up.json"),
    ("over-shoulder", "Over Shoulder", f"{VIEW}/head/over-shoulder.json"),
    ("head-tilt", "Head Tilt", f"{VIEW}/head/head-tilt.json"),
]
HEAD_FRAMING = [
    ("face-closeup", "Face Close-up", "data/art/studio/framing/face-closeup.json"),
    ("chest-and-hair", "Chest and Hair", "data/art/studio/framing/chest-and-hair.json"),
]
HEAD_EXPRESSIONS = [
    ("soft-closed-smile", "Soft Closed Smile", "data/art/motion/expressions/soft-closed-smile.json"),
    ("sultry-lips-parted", "Sultry", "data/art/motion/expressions/sultry-lips-parted.json"),
    ("serious-poised", "Serious", "data/art/motion/expressions/serious-poised.json"),
    ("joyful-laugh", "Joyful Laugh", "data/art/motion/expressions/joyful-laugh.json"),
]


def write(path, card):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT).as_posix()}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--group", required=True, help="_sets group, e.g. angel-primes")
    ap.add_argument("--slug", required=True, help="hero slug, e.g. angelica-prime")
    ap.add_argument("--hero", required=True, help="prompts/<group>/<hero>/ folder name, e.g. Angelica")
    ap.add_argument("--identity", help="hero identity json (default: data/art/heroes/<group>/<slug>.json)")
    ap.add_argument("--underlayer", help="underlayer piece to keep identical to the hero's A-pose (pose views only)")
    args = ap.parse_args()

    identity = args.identity or f"data/art/heroes/{args.group}/{args.slug}.json"
    if not (ROOT / identity).exists():
        raise SystemExit(f"identity not found: {identity}")
    base = ROOT / "data/art/_sets" / args.group / args.slug

    def card(art_id, stage, name, template, output, denoise, components, note):
        return {
            "artId": art_id, "kind": "base-set", "stage": stage, "heroArt": identity, "name": name,
            "components": components, "template": template, "output": output, "denoise": denoise,
            "notes": note,
        }

    for slug, name, piece in POSE_VIEWS:
        comps = {"view": piece}
        if args.underlayer:
            comps["underlayer"] = args.underlayer
        write(base / "pose" / f"{args.slug}-view-{slug}.json", card(
            f"{args.slug}-view-{slug}", "pose", name, POSE_VIEW_TEMPLATE,
            f"prompts/{args.group}/{args.hero}/poses/{args.hero}_View_{slug.replace('-', '_')}.txt",
            "~0.5-0.7", comps, "Reference-library body view, edited from the front A-pose. Scaffolded."))

    for slug, name, piece in HEAD_VIEWS:
        write(base / "head" / f"{args.slug}-head-{slug}.json", card(
            f"{args.slug}-head-{slug}", "head", name, HEAD_TEMPLATE,
            f"prompts/{args.group}/{args.hero}/head/{args.hero}_Head_{slug.replace('-', '_')}.txt",
            "~0.4-0.6", {"view": piece}, "Reference-library head view, zoomed from the A-pose. Scaffolded."))

    for slug, name, piece in HEAD_FRAMING:
        write(base / "head" / f"{args.slug}-head-{slug}.json", card(
            f"{args.slug}-head-{slug}", "head", name, HEAD_TEMPLATE,
            f"prompts/{args.group}/{args.hero}/head/{args.hero}_Head_{slug.replace('-', '_')}.txt",
            "~0.4-0.6", {"framing": piece}, "Reference-library head framing (front view). Scaffolded."))

    for slug, name, piece in HEAD_EXPRESSIONS:
        write(base / "head" / f"{args.slug}-head-{slug}.json", card(
            f"{args.slug}-head-{slug}", "head", name, HEAD_TEMPLATE,
            f"prompts/{args.group}/{args.hero}/head/{args.hero}_Head_{slug.replace('-', '_')}.txt",
            "~0.4-0.6", {"expression": piece}, "Reference-library head expression (front view). Scaffolded."))


if __name__ == "__main__":
    main()
