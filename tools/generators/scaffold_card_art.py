#!/usr/bin/env python3
"""Scaffold card-art assembly cards (data/art/_sets/sovereign-dawn/<category>/card/) for the non-hero gameplay cards.

Each art card only points at its gameplay card by cardId; the prompt takes name, element and lore from there, so a card's
art follows its design. Existing art cards are never overwritten.

  python tools/generators/scaffold_card_art.py                    # all categories
  python tools/generators/scaffold_card_art.py --category pets    # one category
"""
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
CARDS = ROOT / "data" / "cards" / "sovereign-dawn"
SETS = ROOT / "data" / "art" / "_sets" / "sovereign-dawn"
CATEGORIES = ["units", "pets", "buildings", "tactics", "equipment", "workers"]
SIZE = "960x1440"  # 2:3 card art (provisional, see STATUS C1)


def pascal(name):
    return "".join(w[:1].upper() + w[1:] for w in re.findall(r"[A-Za-z0-9]+", name))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--category", choices=CATEGORIES, help="only this category")
    args = ap.parse_args()
    made = 0
    for cat in [args.category] if args.category else CATEGORIES:
        folder = cat.capitalize()
        for path in sorted((CARDS / cat).glob("*.json")):
            gp = json.loads(path.read_text(encoding="utf-8"))
            art_id = f"{path.stem}-card"
            out = SETS / cat / "card" / f"{art_id}.json"
            if out.exists():
                continue
            card = {
                "artId": art_id, "kind": "base-set", "stage": "card",
                "heroArt": "data/art/cards/sovereign-dawn.json",
                "template": "data/art/_templates/cards/card-art.txt",
                "denoise": "1.0", "size": SIZE, "category": cat, "cardId": gp["cardId"],
                "output": f"prompts/sovereign-dawn/{folder}/card/{folder}_Card_{pascal(gp['name'])}.txt",
                "notes": f"Mechanical card art for {gp['cardId']} ({gp['collectionNumber']}); prompt built from the card's name, element and lore.",
            }
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
            made += 1
    print(f"{made} card-art cards created")


if __name__ == "__main__":
    main()
