#!/usr/bin/env python3
"""Add the first-shot experiment cards to every female hero that has a Prime card (re-runnable; existing cards are kept).

The Prime (1_Prime) is one way to start from the original photo: a head-to-toe A-pose in her swimsuit. Two other ways are tested beside it, in 1_Alpha/1b_Experiments/<family>/
(the same convention as 2b_Experiments/celestial), each with its own folder so the outputs in ComfyUI never mix:

  bare-base      the bare figure straight from the photo, her own build from the art data (Alpha_1b_BareBase; wearing = the bare-skin study). It is the body master: no Bare Figure step after it.
  neutral-base   a skin-tone base layer with the standard slender figure like the Prime (Alpha_1b_NeutralBase); Alpha 2 Bare Figure follows and sets her own build.

The winner is promoted to 1_Prime (git mv the card, template and prompt name) and the other is removed; see docs/plans/2026-10-11-first-shot-flows.md.

  python tools/generators/scaffold_first_shots.py            write the missing cards
  python tools/generators/scaffold_first_shots.py --check    list what would be written
Then:  python tools/generators/gen_prompt.py ; python tools/workflows/comfy_workflows.py make --create --engine both --match Alpha_1b --apply

What each card wears is not set here: the template's {{BARE_BASE}} and {{BASE_LAYER}} tags take their piece from the slot defaults in gen_prompt.py (SLOT_DEFAULTS), a hero's own
art.defaultBareBase / art.defaultBaseLayer when she has one, and a card's components.<slot> when it sets one, like every other tag.
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import art_layout  # noqa: E402
from template_paths import template_path  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
SETS = ROOT / "data/art/_sets"

# (family, card suffix, prompt stem name, template, figure profile, note). The garment is a slot (see the module doc), not written into the card.
KINDS = [
    ("bare-base", "bare-base", "BareBase", "base-bare-human.txt", None,
     "Alpha 1b Bare Base (experiment P3): the first shot as a bare figure, her own build from the art data. It is the body master; no Bare Figure step after it."),
    ("neutral-base", "neutral-base", "NeutralBase", "base-neutral-human.txt", "standard",
     "Alpha 1b Neutral Base (experiment P2): a skin-tone base layer on the standard figure; Alpha 2 Bare Figure follows."),
]


def cards():
    """[(slug folder, prime card)] of every female hero's Prime."""
    out = []
    for p in sorted(SETS.rglob("*-alpha-prime.json")):
        prime = json.loads(p.read_text(encoding="utf-8"))
        hero = json.loads((ROOT / prime["heroArt"]).read_text(encoding="utf-8"))
        if "bust" not in hero.get("art", {}).get("physique", {}):
            continue
        out.append((p.parents[2], prime))  # <slug>/1_Alpha/1_Prime/<card>.json
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="list what would be written, write nothing")
    args = ap.parse_args(argv)
    made = kept = 0
    for slug_dir, prime in cards():
        slug = prime["artId"][: -len("-alpha-prime")]
        group, division, hero, _dirs, _file = art_layout.split_output(prime["output"])
        for family, suffix, stem, template, profile, note in KINDS:
            art_id = f"{slug}-alpha-1b-{suffix}"
            card = {"artId": art_id, "kind": "base-set", "stage": "alpha", "heroArt": prime["heroArt"], "template": template_path(template),
                    "output": "", "denoise": "~1.0", "notes": note}
            if profile:
                card["figureProfile"] = profile
            card["output"] = art_layout.output_for(card, group, hero, f"{hero}_Alpha_1b_{stem}", ROOT, division)
            path = slug_dir.joinpath(*art_layout.card_dirs(card, group, ROOT), f"{art_id}.json")
            if path.exists():
                kept += 1
                continue
            made += 1
            print(f"  {'would write' if args.check else 'wrote'}  {path.relative_to(ROOT).as_posix()}")
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"first shots: {made} card(s) {'to write' if args.check else 'written'}, {kept} already there")


if __name__ == "__main__":
    main()
