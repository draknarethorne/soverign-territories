#!/usr/bin/env python3
"""Scaffold the trimmed Angel Primes set for each angel from data/art/_kits/angel-primes/<slug>.json (re-runnable; existing cards are kept).

Per angel (a kit lists the choices; the identity in data/art/heroes/angel-primes/<slug>.json supplies sex and look):
  1_Alpha      Prime, Bare_Figure (+ Bare_Chest, Barefoot, Heels for the female angels; males have no Barefoot or Heels step)
  2_Studies    the head and a face close-up
  3_Layers     the A-pose underlayer tests          4_Wardrobe  clothing and armor on the studio backdrop
  Bench/motion four motions                         5_Scenes    one signature scene with wings, element effect and the bonded pet

Then:  gen_prompt.py --group angel-primes ; comfy_workflows.py make --create --group angel-primes

Example:  python tools/generators/scaffold_angel_set.py --all
          python tools/generators/scaffold_angel_set.py --slug seraphine
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import art_layout  # noqa: E402
from scaffold_sister_studio import STUDIO, TPL, Writer, camel, norm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data/art"
GROUP = "angel-primes"
BAREFOOT = "data/art/wardrobe/footwear/barefoot/barefoot.json"
MALE_NECKLACE = "a simple {{METAL}} chain with a small pendant"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def build(slug):
    kit = load(f"data/art/_kits/angel-primes/{slug}.json")
    ident = kit["identity"]
    hero = kit["hero"]
    female = "bust" in load(ident)["art"]["physique"]
    sex = "female" if female else "male"
    division = pathlib.PurePosixPath(ident).parts[4]  # data/art/heroes/angel-primes/<division>/<slug>.json
    wr = Writer(ART / "_sets" / GROUP / division / slug, GROUP)
    out = lambda folder, name: f"prompts/{GROUP}/{division}/{hero}/{folder}/{name}.txt"
    studio = dict(STUDIO)
    if not female:
        studio["jewelry"] = MALE_NECKLACE

    def card(art_id, stage, folder, stem, template, comps=None, denoise="~0.5-0.7", note=None, **extra):
        body = {"artId": art_id, "kind": "base-set", "stage": stage, "heroArt": ident, "template": f"{TPL}/{template}",
                "output": out(folder, stem), "denoise": denoise, **extra}
        if comps:
            body["components"] = comps
        if note:
            body["notes"] = note
        return body

    # Alpha: the creation chain
    wr.write("alpha", f"{slug}-alpha-prime", card(f"{slug}-alpha-prime", "alpha", "alpha", f"{hero}_Alpha_1_Prime", f"pose-{sex}-human.txt", denoise="~1.0",
             note=f"{hero} Prime A-pose, built from the original photo.", **({"figureProfile": "standard"} if female else {})))
    bare_tpl = "bare-human.txt" if female else "bare-male-human.txt"
    study = "bare-skin-study" if female else "bare-skin-study-male"
    wr.write("alpha", f"{slug}-alpha-bare-figure", card(f"{slug}-alpha-bare-figure", "alpha", "alpha", f"{hero}_Alpha_2_Bare_Figure", bare_tpl,
             {"wearing": f"data/art/wardrobe/swimwear/base/edit/{study}.json"}, name="Bare edit: bare skin figure",
             note="Alpha 2 Bare: fed the Prime, sets the individual build and likeness."))
    if female:
        wr.write("alpha", f"{slug}-alpha-bare-chest", card(f"{slug}-alpha-bare-chest", "alpha", "alpha", f"{hero}_Alpha_2_Bare_Chest", bare_tpl,
                 {"wearing": "data/art/wardrobe/swimwear/base/edit/bare-chest-study.json"}, name="Bare edit: bare chest figure",
                 note="Alpha 2 Bare, chest variant."))
        wr.write("alpha", f"{slug}-alpha-barefoot", card(f"{slug}-alpha-barefoot", "alpha", "alpha", f"{hero}_Alpha_3_Barefoot", "pose-female-human.txt",
                 {"footwear": "data/art/wardrobe/footwear/barefoot/barefoot-a-pose.json"}, note="Alpha 3 Barefoot A-pose, fed the Bare image."))
        wr.write("alpha", f"{slug}-alpha-heels", card(f"{slug}-alpha-heels", "alpha", "alpha", f"{hero}_Alpha_3_Heels", "pose-female-human.txt",
                 {"footwear": norm(kit["heels"])}, note="Alpha 3 Heeled A-pose, fed the Bare image."))

    # Studies
    wr.write("head", f"{slug}-x-head", card(f"{slug}-x-head", "head", "head", f"{hero}_X_Head", "head-human.txt", denoise="~0.4-0.6",
             note=f"{hero} head, the golden head."))
    wr.write("head", f"{slug}-head-face-closeup", card(f"{slug}-head-face-closeup", "head", "head", f"{hero}_Head_Face_Closeup", "head-human.txt",
             {"framing": "data/art/studio/framing/face-closeup.json"}, denoise="~0.4-0.6", name="Face close-up"))

    # Layers
    for path in kit["underlayers"]:
        path = norm(path)
        short = pathlib.Path(path).stem
        art_id = f"{slug}-x-pose-{short}"
        wr.write("pose", art_id, card(art_id, "pose", "poses", f"{hero}_X_Pose_{camel(short)}", f"pose-{sex}-human.txt", {"underlayer": path}, denoise="~1.0",
                 note="UNDERLAYER TEST: fed the Bare image; only the underlayer piece differs."))

    # Wardrobe
    for stage, key in (("clothing", "clothing"), ("armor", "armor")):
        for path in kit[key]:
            path = norm(path)
            piece = load(path)
            short = pathlib.Path(path).stem
            art_id = f"{slug}-{stage}-{short}"
            comps = {"wearing": path, **{k: v for k, v in studio.items() if stage == "armor" or k not in ("back", "holding")}}
            wr.write(stage, art_id, card(art_id, stage, stage, f"{hero}_{stage.capitalize()}_{camel(short)}", f"{stage}-human.txt", comps, name=piece["name"],
                     aesthetic=f"a clean studio presentation of the {piece['name'].lower()}", note="WARDROBE TEST: same hero, only the piece differs."))

    # Motion
    for path in kit["motions"]:
        path = norm(path)
        fam, short = pathlib.Path(path).parent.name, pathlib.Path(path).stem
        art_id = f"{slug}-motion-{short}"
        wr.write(f"motion/{fam}", art_id, card(art_id, "motion", "/".join(art_layout.dirs_for("motion", [fam])), f"{hero}_Motion_{camel(fam)}_{camel(short)}",
                 "motion-human.txt", denoise="~0.4-0.6", component=path))

    # Signature scene: wings, element effect and the bonded pet
    sc = kit["scene"]
    armor = "/armor/" in sc["wearing"]
    comps = {"pose": norm(sc["pose"]), "expression": norm(sc["expression"]), "wearing": norm(sc["wearing"]), "jewelry": studio["jewelry"],
             "legs_feet": "data/art/wardrobe/footwear/boots/knight-boots.json" if (armor and not female) else BAREFOOT, "back": norm(sc["back"]),
             "effects": sc["effects"], "companion": norm(sc["companion"]), "background": norm(sc["background"])}
    wr.write("scene", f"{slug}-scene-signature", card(f"{slug}-scene-signature", "scene", "scene", f"{hero}_Scene_Signature", "scene-with-companion-human.txt",
             comps, name="Signature", note="Complete scene from the A-pose: outfit, wings, element effect, bonded pet and an element realm."))
    print(f"{slug}: made {wr.made} cards, {wr.skipped} already existed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    slugs = sorted(p.stem for p in (ART / "_kits" / GROUP).glob("*.json")) if args.all else [args.slug]
    if not slugs or slugs == [None]:
        sys.exit("give --slug or --all")
    for slug in slugs:
        build(slug)


if __name__ == "__main__":
    main()
