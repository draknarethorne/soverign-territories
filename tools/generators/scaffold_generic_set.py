#!/usr/bin/env python3
"""Preview or add missing generic Female and Male assembly cards."""
import argparse
import json
import pathlib
import types

import art_layout
import scaffold_angel_library as library
import scaffold_studio_library as studio_library
from scaffold_hero_core import BAREFOOT, DEFAULT_HEELS, alpha_chain, card_factory
from scaffold_sister_studio import STUDIO, Writer, camel

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data/art"
IDENTITIES = {"female": ("Female", "data/art/heroes/sovereign-females/female.json"),
              "male": ("Male", "data/art/heroes/sovereign-males/male.json")}
PLAN = {
    "female": {"layers": ["triangle-bikini", "one-piece/one-piece-swimsuit"], "clothing": "gowns/long-evening-gown", "pose": "standing/three-quarter-glamour",
               "motions": ["standing/hand-on-hip-power", "walking/catwalk-confident", "dynamic/twirl-spin"]},
    "male": {"layers": ["trunks/athletic-trunks", "trunks/board-shorts"], "clothing": "sets/tailored-dress-shirt-set", "pose": "walking/strut-runway",
             "motions": ["standing/hand-on-hip-power", "walking/relaxed-stroll", "action/guard-stance"]},
}
WINGS = "data/art/wardrobe/capes/wings/white-angel-wings.json"
GLOW = "data/art/wardrobe/effects/ambient/soft-ambient-glow.json"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def build_generic(slug, dry_run=True):
    hero, ident = IDENTITIES[slug]
    female = slug == "female"
    plan = PLAN[slug]
    group = f"sovereign-{slug}s"
    wr = Writer(ART / "_sets" / group / slug, group, dry_run=dry_run)
    out = lambda folder, name: f"prompts/{group}/{hero}/{folder}/{name}.txt"
    card = card_factory(ident, out)
    swim = lambda name: f"data/art/wardrobe/swimwear/{name if '/' in name else ('bikini/' if female else 'trunks/') + name}.json"
    alpha_chain(wr, card, slug, hero, female, DEFAULT_HEELS)
    wr.write("head", f"{slug}-head", card(f"{slug}-head", "head", "head", f"{hero}_Head", "head-human.txt", denoise="~0.4-0.6", note=f"{hero} head, the golden head."))
    under = "data/art/wardrobe/swimwear/bikini/triangle-bikini.json" if female else library.BRIEF
    args = types.SimpleNamespace(group=group, slug=slug, hero=hero, identity=ident,
                                 division="", underlayer=under, small=True)
    for path, study in studio_library.cards(args):
        wr.write(study["stage"], path.stem, study)
    library.Angel.alpha(slug, hero, ident, slug, wr, out).studies(include_studio=False)
    for name in plan["layers"]:
        path = swim(name)
        short = pathlib.Path(path).stem
        art_id = f"{slug}-layer-{short}"
        wr.write("pose", art_id, card(art_id, "pose", "poses", f"{hero}_Layer_{camel(short)}", f"pose-{slug}-human.txt", {"underlayer": path}, denoise="~1.0",
                 note="UNDERLAYER TEST: fed the Bare image; only the underlayer piece differs."))
    studio = dict(STUDIO)
    studio["jewelry"] = library.NECKLACE if female else library.CHAIN
    outfits = {"clothing": f"data/art/wardrobe/clothing/{plan['clothing']}.json", "armor": "data/art/wardrobe/armor/plate/half-plate.json"}
    for stage, path in outfits.items():
        piece, short = load(path), pathlib.Path(path).stem
        comps = {"wearing": path, **{k: v for k, v in studio.items() if stage == "armor" or k not in ("back", "holding")}}
        wr.write(stage, f"{slug}-{stage}-{short}", card(f"{slug}-{stage}-{short}", stage, stage, f"{hero}_{stage.capitalize()}_{camel(short)}", f"{stage}-human.txt", comps, name=piece["name"],
                 aesthetic=f"a clean studio presentation of the {piece['name'].lower()}", note="WARDROBE TEST: same hero, only the piece differs."))
    common = {"back": WINGS, "jewelry": library.NECKLACE if female else library.CHAIN, "legs_feet": library.ANKLETS if female else BAREFOOT, "effects": GLOW}
    wr.write("scene", f"{slug}-scene-glamour", card(f"{slug}-scene-glamour", "scene", "scene", f"{hero}_Scene_Glamour", "scene-glamour-human.txt",
             {"pose": f"data/art/motion/{plan['pose']}.json", "wearing": outfits["clothing"], **common, "background": "data/art/backgrounds/fantasy/evening/moonlit-terrace.json"},
             name="Glamour", note="GLAMOUR: a relaxed portrait in an evening setting, with wings: does the photo still look like the person?"))
    wr.write("scene", f"{slug}-scene-signature", card(f"{slug}-scene-signature", "scene", "scene", f"{hero}_Scene_Signature", "scene-with-outfit-human.txt",
             {"pose": "data/art/motion/standing/hand-on-hip-power.json", "wearing": outfits["armor"], **common,
              "background": "data/art/backgrounds/fantasy/elemental/grounded/radiant-sun-realm.json"},
             name="Signature", note="SIGNATURE: armor and wings in a sunlit cinematic realm."))
    for path in (f"data/art/motion/{m}.json" for m in plan["motions"]):
        fam, short = pathlib.Path(path).parent.name, pathlib.Path(path).stem
        art_id = f"{slug}-motion-{short}"
        wr.write(f"motion/{fam}", art_id, card(art_id, "motion", "/".join(art_layout.dirs_for("motion", [fam])), f"{hero}_Motion_{camel(fam)}_{camel(short)}",
                 "motion-human.txt", denoise="~0.4-0.6", component=path))
    print(f"{group}/{slug}: {wr.made} {'would be created' if dry_run else 'created'}, {wr.skipped} already exist")
    return wr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", nargs="?", choices=("female", "male", "all"), default="all")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="create missing cards; never overwrite existing cards")
    mode.add_argument("--check", action="store_true", help="fail if any scaffold cards are missing")
    args = parser.parse_args()
    results = [build_generic(slug, dry_run=not args.apply)
               for slug in (("female", "male") if args.slug == "all" else (args.slug,))]
    if args.check and any(writer.made for writer in results):
        raise SystemExit("Generic scaffold is incomplete; preview the listed cards before --apply.")


if __name__ == "__main__":
    main()
