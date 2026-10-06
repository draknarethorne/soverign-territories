#!/usr/bin/env python3
"""Scaffold a sister's whole studio kit from data/art/_kits/<slug>.json (re-runnable; existing cards are kept).

A kit lists what to try for ONE hero, chosen to suit her class and element:
  underlayers  A-pose bases to test                     -> _sets/<group>/<slug>/pose/      (components.underlayer)
  clothing     outfits on the studio backdrop             -> .../clothing/
  armor        armor sets on the studio backdrop          -> .../armor/   (the celestial armor piece is added automatically)
  motions      "all" or a list of data/art/motion pieces  -> .../motion/<family>/
  showcase     studio shots on a coloured backdrop with magic and flair (stage "showcase")  -> .../showcase/
  library      true = also the body views, head views, framings and expressions (scaffold_studio_library.py)
Studio work (everything here) deploys to the sister's own workspace; her scenes stay in the shared one.

Then:  gen_prompt.py --group G --slug S ; comfy_workflows.py make --hero H --class studio --create ;
       comfy_workflows.py deploy --to uat --hero H --class studio

Example:  python tools/generators/scaffold_sister_studio.py --slug draknara
          python tools/generators/scaffold_sister_studio.py --slug drakness --celestial-only
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import art_layout  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data/art"
TPL = "data/art/_templates/heroes"
DEFAULT_SHOWCASE = {
    "jewelry": "a simple {{METAL}} necklace and small matching earrings",
    "legs_feet": "data/art/wardrobe/footwear/barefoot/barefoot-anklets.json",
}
STUDIO = {"arms": "bare arms", "jewelry": "a simple {{METAL}} necklace and small matching earrings",
          "back": "the back of the armor fully visible", "holding": "empty hands relaxed at the sides",
          "legs_feet": "data/art/wardrobe/footwear/barefoot/barefoot.json"}


def camel(name):
    return "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", name) if w)


def norm(p):
    p = p.removeprefix("data/art/")
    return "data/art/" + (p if p.endswith(".json") else p + ".json")


class Writer:
    def __init__(self, base, group):
        self.base, self.group, self.made, self.skipped = base, group, 0, 0
        # Hand-made cards use their own file names, so also skip anything whose output file already has a card.
        self.outputs = {json.loads(p.read_text(encoding="utf-8")).get("output") for p in base.rglob("*.json")} if base.exists() else set()

    def write(self, sub, art_id, card):
        fam = art_layout.family(card, self.group, ROOT)  # the card decides its folder; hair and motion keep theirs
        if fam is not None:
            hero, stem = card["output"].split("/")[2], pathlib.PurePosixPath(card["output"]).stem
            card["output"] = art_layout.output_for(card, self.group, hero, stem, ROOT)
            sub = "/".join([sub.split("/")[0], *fam])
        target = self.base / sub / f"{art_id}.json"
        if target.exists() or card.get("output") in self.outputs:
            self.skipped += 1
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        self.made += 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--group", default="drakn-sisters")
    ap.add_argument("--celestial-only", action="store_true", help="only the celestial armor studio card (no kit file needed)")
    args = ap.parse_args()
    slug, group = args.slug, args.group
    kit_path = ART / "_kits" / f"{slug}.json"
    kit = json.loads(kit_path.read_text(encoding="utf-8")) if kit_path.exists() and not args.celestial_only else {}
    hero = kit.get("hero") or slug.capitalize()
    ident = f"data/art/heroes/{group}/{slug}-thorne.json"
    wr = Writer(ART / "_sets" / group / slug, group)
    out = lambda folder, name: f"prompts/{group}/{hero}/{folder}/{name}.txt"

    def clothing_card(stage, path, note):
        piece = json.loads((ROOT / path).read_text(encoding="utf-8"))
        short = pathlib.Path(path).stem
        comps = {"wearing": path, **{k: v for k, v in STUDIO.items() if stage == "armor" or k not in ("back", "holding")}}
        art_id = f"{slug}-{stage}-{short}"
        wr.write(stage, art_id, {"artId": art_id, "kind": "base-set", "stage": stage, "heroArt": ident, "name": piece["name"],
                "aesthetic": f"a clean studio presentation of the {piece['name'].lower()}", "components": comps,
                "template": f"{TPL}/{stage}-human.txt", "denoise": "~0.5-0.7",
                "output": out(stage, f"{hero}_{stage.capitalize()}_{camel(short)}"), "notes": note})

    celestial = f"data/art/heroes/{group}/{slug}/armor/celestial-armor.json"
    if args.celestial_only:
        kit = {"armor": []}
    for path in kit.get("underlayers", []):
        path = norm(path)
        short = pathlib.Path(path).stem
        sex = "male" if "male" in json.loads((ROOT / path).read_text(encoding="utf-8")).get("tags", []) else "female"
        art_id = f"{slug}-x-pose-{short}"
        wr.write("pose", art_id, {"artId": art_id, "kind": "base-set", "stage": "pose", "heroArt": ident,
                 "template": f"{TPL}/pose-{sex}-human.txt", "output": out("poses", f"{hero}_X_Pose_{camel(short)}"),
                 "denoise": "~1.0", "components": {"underlayer": path},
                 "notes": "UNDERLAYER TEST. Same original photo as the base A-pose; only the underlayer piece differs."})
    for path in kit.get("clothing", []):
        clothing_card("clothing", norm(path), "WARDROBE TEST: same hero, only the outfit differs.")
    for path in kit.get("armor", []) + ([celestial] if (ROOT / celestial).exists() else []):
        clothing_card("armor", norm(path), "WARDROBE TEST: same hero, only the armor differs.")

    motions = kit.get("motions", [])
    if motions == "all":
        motions = [p.relative_to(ROOT).as_posix() for p in sorted((ART / "motion").glob("*/*.json"))
                   if p.parent.name not in ("expressions", "gaze")]
    for path in motions:
        path = norm(path)
        fam, short = pathlib.Path(path).parent.name, pathlib.Path(path).stem
        art_id = f"{slug}-motion-{short}"
        wr.write(f"motion/{fam}", art_id, {"artId": art_id, "kind": "base-set", "stage": "motion", "heroArt": ident,
                 "component": path, "template": f"{TPL}/motion-human.txt", "denoise": "~0.4-0.6",
                 "output": out(f"motion/{fam}", f"{hero}_Motion_{camel(fam)}_{camel(short)}")})

    for s in kit.get("showcase", []):
        comps = {**DEFAULT_SHOWCASE, **{k: (norm(v) if str(v).startswith(("wardrobe/", "heroes/", "backgrounds/", "motion/", "data/art/")) else v)
                 for k, v in s["components"].items()}}
        short = re.sub(r"[^a-z0-9]+", "-", s["name"].lower()).strip("-")
        art_id = f"{slug}-showcase-{short}"
        wr.write("showcase", art_id, {"artId": art_id, "kind": "base-set", "stage": "showcase", "heroArt": ident, "name": s["name"],
                 "components": comps, "template": f"{TPL}/showcase-human.txt", "denoise": "~0.5-0.7",
                 "output": out("showcase", f"{hero}_Showcase_{camel(short)}"),
                 "notes": s.get("notes", "SHOWCASE: a studio shot on a coloured backdrop with magic and flair, before it becomes a scene.")})

    if kit.get("library"):
        subprocess.run([sys.executable, str(ROOT / "tools/generators/scaffold_studio_library.py"), "--group", group, "--slug", slug,
                        "--hero", hero, "--identity", ident, "--underlayer", "data/art/wardrobe/swimwear/bikini/metallic-triangle-bikini.json"], check=True)
    print(f"{slug}: made {wr.made} cards, {wr.skipped} already existed")


if __name__ == "__main__":
    main()
