#!/usr/bin/env python3
"""Pull text that is pasted into several art cards out into reusable pieces (a pure refactor: every generated prompt must stay byte-identical).

A card's components slot may hold a literal sentence instead of a path to a piece. When the same sentence sits in two or more cards it belongs in a piece, so one edit fixes them all
(and a hero can extend it, see `extends` in data/art/README.md). This finds those sentences and, with --apply, writes the piece and points the cards at it.

  slots handled   jewelry, legs_feet, effects, companion, pose, expression      (generic fillers such as "bare arms" and "empty hands" stay inline by design)
  where it goes   an identical existing piece is reused; else used by one hero -> heroes/<group>/[<division>/]<slug>/<kind>/ ; used by several -> wardrobe/<kind>/<shared family>/
  safety          preview unless --apply; afterwards regenerate the prompts and check `git status prompts/` shows nothing changed

Example:  python tools/art/extract_literals.py                 (preview)
          python tools/art/extract_literals.py --apply --min-uses 2
"""
import argparse
import collections
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SETS = ROOT / "data/art/_sets"
SLOTS = {  # slot -> (piece kind, hero folder, shared folder, text field)
    "jewelry": ("jewelry", "jewelry", "wardrobe/jewelry/studio", "description"),
    "legs_feet": ("legs_feet", "footwear", "wardrobe/footwear/studio", "description"),
    "effects": ("effects", "effects", "wardrobe/effects/shared", "description"),
    "companion": ("companion", "companion", None, "description"),
    "pose": ("pose", "motion", "motion/scene", "pose"),
    "expression": ("expression", "expressions", "motion/expressions/scene", "expression"),
}
KINDS = tuple(v[0] for v in SLOTS.values())


PRESET_NAMES = {  # sentence starts -> a readable piece name
    "a simple {{METAL}} necklace and small matching earrings": "simple-necklace-and-earrings",
    "a simple {{METAL}} chain with a small pendant": "simple-chain-with-pendant",
    "Fine stars drift and glitter around her": "celestial-starlight-rising",
    "Rainbow light splits across her armor": "celestial-prismatic-ascended",
    "bare feet, fine {{METAL}} anklets": "barefoot-fine-anklets",
    "bare feet with fine {{METAL}} anklets": "barefoot-with-fine-anklets",
    "She leaps mid-air with her weapon swept behind her": "battle-leap",
    "She stands close to her bonded companion": "bond-hand-on-companion",
    "She stands tall and square to the camera, feet a little apart": "lineup-square-stance",
}


def slugify(text, limit=48):
    for start, name in PRESET_NAMES.items():
        if text.startswith(start):
            return name
    words = re.findall(r"[A-Za-z0-9]+", re.sub(r"\{\{[A-Z_]+\}\}", " ", text))
    while len(words) > 3 and words[0].lower() in ("a", "an", "the", "she", "he", "her", "his"):
        words = words[1:]
    words = words[:6]
    return "-".join(w.lower() for w in words)[:limit].strip("-") or "piece"


def existing_by_text():
    out = {}
    for p in (ROOT / "data/art").rglob("*.json"):
        if "_sets" in p.parts or "_schema" in p.parts or "_kits" in p.parts or "_settings" in p.parts:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8-sig"))
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("kind") in KINDS and not d.get("extends"):
            field = next(v[3] for v in SLOTS.values() if v[0] == d["kind"])
            if isinstance(d.get(field), str) and (d["kind"] not in ("pose", "expression") or len(d) <= 7):
                out.setdefault((d["kind"], d[field]), p.relative_to(ROOT).as_posix())
    return out


def hero_of(card_path):
    """(group, division or None, slug) for a card file under _sets."""
    parts = card_path.relative_to(SETS).parts
    group = parts[0]
    divisions = json.loads((ROOT / "data/art/_settings/groups.json").read_text(encoding="utf-8")).get("divisions", {}).get(group, [])
    if len(parts) > 2 and parts[1] in divisions:
        return group, parts[1], parts[2]
    return group, None, parts[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--min-uses", type=int, default=2, help="how many cards must carry the same sentence (default 2)")
    args = ap.parse_args()

    uses = collections.defaultdict(list)  # (slot, text) -> [(card path, stage)]
    for p in sorted(SETS.rglob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for slot, val in d.get("components", {}).items():
            if slot in SLOTS and isinstance(val, str) and not val.startswith("+") and not (val.endswith(".json") and (ROOT / val).exists()):
                uses[(slot, val)].append((p, d["stage"]))

    known = existing_by_text()
    taken = set()
    plan = []
    for (slot, text), cards in sorted(uses.items(), key=lambda kv: -len(kv[1])):
        if len(cards) < args.min_uses or len(text) < 20:
            continue
        kind, hero_dir, shared, field = SLOTS[slot]
        heroes = {hero_of(p) for p, _ in cards}
        target = known.get((kind, text))
        action = "reuse"
        if not target:
            action = "new"
            if len(heroes) == 1:
                group, division, slug = next(iter(heroes))
                folder = "/".join(["data/art/heroes", group, *([division] if division else []), slug, hero_dir])
            elif shared:
                folder = "data/" + "art/" + shared
            else:
                continue
            name = slugify(text)
            if kind == "effects" and len(heroes) == 1 and len(cards) >= 8 and name not in PRESET_NAMES.values():
                name = "elemental-aura"  # the aura line one hero reuses across her scenes and showcases
            n = 1
            while (ROOT / f"{folder}/{name}{'' if n == 1 else '-' + str(n)}.json").exists() or f"{folder}/{name}{'' if n == 1 else '-' + str(n)}" in taken:
                n += 1
            name = f"{name}{'' if n == 1 else '-' + str(n)}"
            taken.add(f"{folder}/{name}")
            target = f"{folder}/{name}.json"
        plan.append((slot, text, cards, target, action, kind))

    print(f"{len(plan)} repeated sentence(s) in {sum(len(c) for _, _, c, *_ in plan)} card slot(s) ({sum(1 for x in plan if x[4] == 'reuse')} reuse an existing piece)")
    for slot, text, cards, target, action, kind in plan[:60]:
        print(f"  {len(cards):4} x [{slot}] {action:5} {target}\n         {text[:110]}")
    if not args.apply:
        print("\npreview only; add --apply to write the pieces and rewrite the cards")
        return

    changed = 0
    for slot, text, cards, target, action, kind in plan:
        if action == "new":
            stages = sorted({s for _, s in cards} | {"scene"} if kind != "companion" else {"scene"})
            stage_map = {"pose": "pose", "head": "head", "hair": "hair", "motion": "motion", "armor": "armor", "clothing": "clothing", "showcase": "showcase", "scene": "scene", "final": "final"}
            stages = sorted({stage_map[s] for s in stages if s in stage_map}) or ["scene"]
            field = SLOTS[slot][3]
            piece = {"id": target[len("data/art/"):-len(".json")],
                     "kind": kind, "name": slugify(text).replace("-", " ").capitalize(), field: text, "compatibleStages": stages,
                     "notes": f"Extracted from {len(cards)} cards that carried this sentence inline; edit it here and every one follows."}
            path = ROOT / target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(piece, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        needle = f'"{slot}": {json.dumps(text, ensure_ascii=False)}'
        for p, _ in cards:
            body = p.read_text(encoding="utf-8")
            if body.count(needle) != 1:
                print(f"  SKIP {p.relative_to(ROOT).as_posix()}: the sentence is not written the expected way in the file")
                continue
            p.write_text(body.replace(needle, f'"{slot}": "{target}"'), encoding="utf-8", newline="")
            changed += 1
    print(f"wrote {sum(1 for x in plan if x[4] == 'new')} piece(s), rewrote {changed} card slot(s)")


if __name__ == "__main__":
    main()
