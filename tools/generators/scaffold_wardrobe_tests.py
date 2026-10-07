#!/usr/bin/env python3
"""Scaffold test cards that put wardrobe pieces on ONE hero, so a whole family can be rendered in a batch.

Pick pieces by folder (or single file) under data/art/wardrobe. Each `wearing` piece becomes one card, and the
card type follows the piece's compatibleStages:
  pose     -> an A-pose underlayer test  (components.underlayer)         -> _sets/<group>/<slug>/pose/
  clothing -> a studio clothing render   (components.wearing + defaults)  -> _sets/<group>/<slug>/clothing/
  armor    -> a studio armor render      (components.wearing + defaults)  -> _sets/<group>/<slug>/armor/
Pieces tagged for the other sex are skipped (female/male tags; unisex and untagged pieces always apply).
Existing cards are never overwritten. Then run gen_prompt.py and comfy_workflows.py make for the same hero.

Example:
  python tools/generators/scaffold_wardrobe_tests.py --group drakn-sisters --slug drakness --hero Drakness \
      wardrobe/clothing/dresses wardrobe/clothing/gowns
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import art_layout  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data/art"
TEMPLATES = "data/art/_templates/heroes"
BAREFOOT = "data/art/wardrobe/footwear/barefoot/barefoot.json"
DEFAULTS = {
    "arms": "bare arms",
    "jewelry": "a simple {{METAL}} necklace and small matching earrings",
    "back": "the back of the armor fully visible",
    "holding": "empty hands relaxed at the sides",
}


def camel(name):
    return "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", name) if w)


def pieces_under(arg):
    p = ART / arg.removeprefix("data/art/")
    files = [p] if p.suffix == ".json" else sorted(p.rglob("*.json"))
    return [f for f in files if f.is_file()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--group", required=True, help="_sets group, e.g. drakn-sisters")
    ap.add_argument("--slug", required=True, help="hero folder slug under _sets/<group>/, e.g. drakness")
    ap.add_argument("--hero", required=True, help="display name used in output files, e.g. Drakness")
    ap.add_argument("--identity", help="art identity path (default: first data/art/heroes/<group>/<slug>*.json)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("paths", nargs="+", help="folders or files under data/art/wardrobe")
    args = ap.parse_args()

    ident = args.identity or sorted((ART / "heroes" / args.group).glob(f"{args.slug}*.json"))[0].relative_to(ROOT).as_posix()
    female = "bust" in json.loads((ROOT / ident).read_text(encoding="utf-8"))["art"]["physique"]
    sex = "female" if female else "male"
    other = "male" if female else "female"
    made = skipped = 0
    base = ART / "_sets" / args.group / args.slug
    outputs = {json.loads(p.read_text(encoding="utf-8")).get("output") for p in base.rglob("*.json")} if base.exists() else set()
    for arg in args.paths:
        for f in pieces_under(arg):
            piece = json.loads(f.read_text(encoding="utf-8"))
            if piece.get("kind") != "wearing" or other in piece.get("tags", []) and sex not in piece.get("tags", []):
                continue
            stages = piece["compatibleStages"]
            stage = "pose" if "pose" in stages else "clothing" if "clothing" in stages else "armor" if "armor" in stages else None
            if stage is None:
                continue
            pid = f.relative_to(ROOT).as_posix()
            short = f.stem
            folder = {"pose": "poses", "clothing": "clothing", "armor": "armor"}[stage]
            out_name = {"pose": f"{args.hero}_X_Pose_{camel(short)}", "clothing": f"{args.hero}_Clothing_{camel(short)}",
                        "armor": f"{args.hero}_Armor_{camel(short)}"}[stage]
            art_id = {"pose": f"{args.slug}-x-pose-{short}", "clothing": f"{args.slug}-clothing-{short}", "armor": f"{args.slug}-armor-{short}"}[stage]
            if stage == "pose":
                card = {"artId": art_id, "kind": "base-set", "stage": "pose", "components": {"underlayer": pid}}
            else:
                card = {"artId": art_id, "kind": "base-set", "stage": stage, "components": {"wearing": pid}}
            fam = art_layout.family(card, args.group, ROOT)
            folder = "/".join(art_layout.dirs_for(folder, fam))
            target = ART / "_sets" / args.group / args.slug / folder / f"{art_id}.json"
            if target.exists():
                skipped += 1
                continue
            if stage == "pose":
                card = {"artId": art_id, "kind": "base-set", "stage": "pose", "heroArt": ident,
                        "template": f"{TEMPLATES}/pose-{sex}-human.txt", "denoise": "~1.0",
                        "components": {"underlayer": pid}}
            else:
                comps = {"wearing": pid, "arms": DEFAULTS["arms"], "jewelry": DEFAULTS["jewelry"], "legs_feet": BAREFOOT}
                if stage == "armor":
                    comps.update(back=DEFAULTS["back"], holding=DEFAULTS["holding"])
                card = {"artId": art_id, "kind": "base-set", "stage": stage, "heroArt": ident, "name": piece["name"],
                        "aesthetic": f"a clean studio presentation of the {piece['name'].lower()}",
                        "components": comps, "template": f"{TEMPLATES}/{stage}-human.txt", "denoise": "~0.5-0.7"}
            card["output"] = f"prompts/{args.group}/{args.hero}/{folder}/{out_name}.txt"
            if card["output"] in outputs:
                skipped += 1
                continue
            card["notes"] = f"WARDROBE TEST. Same hero, only the {stage} piece differs ({pid})."
            made += 1
            if args.dry_run:
                print("would write", target.relative_to(ROOT).as_posix())
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{'would make' if args.dry_run else 'made'} {made} cards, {skipped} already existed")


if __name__ == "__main__":
    main()
