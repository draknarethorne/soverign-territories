#!/usr/bin/env python3
"""Scaffold an Angel Primes angel's set from data/art/_kits/angel-primes/<slug>.json (re-runnable; existing cards are kept).

Per angel (a kit lists the choices; the identity in data/art/heroes/angel-primes/<slug>.json supplies sex and look). This file writes the core set:
  1_Alpha      Prime, Bare_Figure (+ Bare_Chest, Barefoot, Heels for the female angels; males have no Barefoot or Heels step)
  2_Studies    the head          3_Layers  the kit's A-pose underlayer tests          4_Wardrobe  the kit's clothing and armor on the studio backdrop
  Bench/motion the kit's motions           5_Scenes/signature  one signature scene with wings, element effect and the bonded pet
and scaffold_angel_library.py then adds the rest of the standard sister set (studies library and hairstyles, covering and celestial experiments, rotating layers, wardrobe,
themes, showcases, scenes, finish skeletons and more motions), rotated across the twenty angels so together they exercise the whole library.

Then:  gen_prompt.py --group angel-primes ; comfy_workflows.py make --create --group angel-primes

Example:  python tools/generators/scaffold_angel_set.py --all
          python tools/generators/scaffold_angel_set.py --slug seraphine
          python tools/generators/scaffold_angel_set.py --coverage      (which library pieces the angels use, no files written)
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import art_layout  # noqa: E402
import scaffold_angel_library as library  # noqa: E402
from scaffold_sister_studio import STUDIO, TPL, Writer, camel, norm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data/art"
GROUP = "angel-primes"
BAREFOOT = "data/art/wardrobe/footwear/barefoot/barefoot.json"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def migrate_signature(slug, hero, division):
    """The signature scene used to sit flat in 5_Scenes; scenes now have the sisters' folders (5_Scenes/signature/). Move the card and point its output at the new folder."""
    base = ART / "_sets" / GROUP / division / slug / "5_Scenes"
    old = base / f"{slug}-scene-signature.json"
    if not old.exists():
        return
    card = json.loads(old.read_text(encoding="utf-8"))
    stem = pathlib.PurePosixPath(card["output"]).stem
    card["output"] = art_layout.output_for(card, GROUP, hero, stem, ROOT, division)
    new = base / "signature" / old.name
    new.parent.mkdir(parents=True, exist_ok=True)
    new.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    old.unlink()
    print(f"{slug}: moved the signature scene card to 5_Scenes/signature/")


def card_factory(ident, out):
    """A base-set card for this hero: card(art_id, stage, folder, stem, template, comps, ...) with the hero's identity and output folder filled in."""
    def card(art_id, stage, folder, stem, template, comps=None, denoise="~0.5-0.7", note=None, **extra):
        body = {"artId": art_id, "kind": "base-set", "stage": stage, "heroArt": ident, "template": f"{TPL}/{template}",
                "output": out(folder, stem), "denoise": denoise, **extra}
        if comps:
            body["components"] = comps
        if note:
            body["notes"] = note
        return body
    return card


def alpha_chain(wr, card, slug, hero, female, heels):
    """1_Alpha, the creation chain every angel has: Prime (A-pose from the photo), Bare (figure; chest too for women), and for women the Footwear step
    (Barefoot and Heels A-poses fed the Bare image). Men stay barefoot in every A-pose, so they have no footwear step."""
    sex = "female" if female else "male"
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
                 {"footwear": norm(heels)}, note="Alpha 3 Heeled A-pose, fed the Bare image."))


# The older pair, as long as it has no kit (its wardrobe, scenes and layers are hand-picked), still gets the same creation chain and studies as every other angel.
# Once data/art/_kits/angel-primes/<slug>.json exists the normal kit builder takes over and only adds what is missing.
OLDER = {"angelica": "data/art/heroes/angel-primes/female/angelica.json", "angelo": "data/art/heroes/angel-primes/male/angelo.json"}
OLDER_HEELS = "data/art/wardrobe/footwear/heels/matching-open-toed-heels.json"  # what her original A-pose wore, now a Heels step instead of baked into the bikini


def retire_x_pose(slug, hero, division):
    """The old single A-pose card (X_Pose) is replaced by the 1_Alpha chain; remove its card and prompt (workflows are cleaned up by the workspace tool)."""
    card_path = ART / "_sets" / GROUP / division / slug / "1_Alpha" / f"{slug}-x-pose.json"
    if card_path.exists():
        prompt = ROOT / json.loads(card_path.read_text(encoding="utf-8"))["output"]
        card_path.unlink()
        if prompt.exists():
            prompt.unlink()
        print(f"{slug}: retired the legacy X_Pose card and prompt")


def build_older(slug):
    ident = OLDER[slug]
    hero = slug.capitalize()
    female = "bust" in load(ident)["art"]["physique"]
    sex = "female" if female else "male"
    division = pathlib.PurePosixPath(ident).parts[4]
    wr = Writer(ART / "_sets" / GROUP / division / slug, GROUP)
    out = lambda folder, name: f"prompts/{GROUP}/{division}/{hero}/{folder}/{name}.txt"
    retire_x_pose(slug, hero, division)
    underlayer = load(ident)["art"]["defaultUnderlayer"]  # her own pastel A-pose look, as the sisters' signature bikinis are theirs
    # The pastel look stays a layer test, as it was the whole of her old X_Pose card.
    card = card_factory(ident, out)
    short = pathlib.Path(underlayer).stem
    art_id = f"{slug}-x-pose-{short}"
    wr.write("pose", art_id, card(art_id, "pose", "poses", f"{hero}_X_Pose_{camel(short)}", f"pose-{sex}-human.txt", {"underlayer": underlayer}, denoise="~1.0",
             note="UNDERLAYER TEST: fed the Bare image; only the underlayer piece differs. This is the look of her Prime A-pose."))
    alpha_chain(wr, card, slug, hero, female, OLDER_HEELS)
    ang = library.Angel.older(slug, hero, ident, sex, division, wr, out, underlayer)
    ang.extend_older()
    print(f"{slug}: made {wr.made} cards, {wr.skipped} already existed")


# The alpha test heroes (division alpha): a small version of the phases for trying any photo before giving it to an angel. No signature items, no kit, only library pieces.
ALPHA = {"female": ("Female", "data/art/heroes/angel-primes/alpha/female.json"), "male": ("Male", "data/art/heroes/angel-primes/alpha/male.json")}
ALPHA_PLAN = {
    "female": {"layers": ["triangle-bikini", "one-piece/one-piece-swimsuit"], "clothing": "gowns/long-evening-gown", "pose": "standing/three-quarter-glamour",
               "motions": ["standing/hand-on-hip-power", "walking/catwalk-confident", "dynamic/twirl-spin"]},
    "male": {"layers": ["trunks/athletic-trunks", "trunks/board-shorts"], "clothing": "sets/tailored-dress-shirt-set", "pose": "walking/strut-runway",
             "motions": ["standing/hand-on-hip-power", "walking/relaxed-stroll", "action/guard-stance"]},
}
WINGS = "data/art/wardrobe/capes/wings/white-angel-wings.json"
GLOW = "data/art/wardrobe/effects/ambient/soft-ambient-glow.json"


def build_alpha(slug):
    hero, ident = ALPHA[slug]
    female = slug == "female"
    plan = ALPHA_PLAN[slug]
    wr = Writer(ART / "_sets" / GROUP / "alpha" / slug, GROUP)
    out = lambda folder, name: f"prompts/{GROUP}/alpha/{hero}/{folder}/{name}.txt"
    card = card_factory(ident, out)
    swim = lambda name: f"data/art/wardrobe/swimwear/{name if '/' in name else ('bikini/' if female else 'trunks/') + name}.json"
    # Phase 1 (the full chain, minus the 2b experiments) and Phase 2 (short)
    alpha_chain(wr, card, slug, hero, female, OLDER_HEELS)
    wr.write("head", f"{slug}-x-head", card(f"{slug}-x-head", "head", "head", f"{hero}_X_Head", "head-human.txt", denoise="~0.4-0.6", note=f"{hero} head, the golden head."))
    library.Angel.alpha(slug, hero, ident, slug, wr, out).studies()
    # Phase 3: two layer tests
    for name in plan["layers"]:
        path = swim(name)
        short = pathlib.Path(path).stem
        art_id = f"{slug}-x-pose-{short}"
        wr.write("pose", art_id, card(art_id, "pose", "poses", f"{hero}_X_Pose_{camel(short)}", f"pose-{slug}-human.txt", {"underlayer": path}, denoise="~1.0",
                 note="UNDERLAYER TEST: fed the Bare image; only the underlayer piece differs."))
    # Phase 4: one outfit and one armor on the studio backdrop
    studio = dict(STUDIO)
    studio["jewelry"] = library.NECKLACE if female else library.CHAIN
    outfits = {"clothing": f"data/art/wardrobe/clothing/{plan['clothing']}.json", "armor": "data/art/wardrobe/armor/plate/half-plate.json"}
    for stage, path in outfits.items():
        piece, short = load(path), pathlib.Path(path).stem
        comps = {"wearing": path, **{k: v for k, v in studio.items() if stage == "armor" or k not in ("back", "holding")}}
        wr.write(stage, f"{slug}-{stage}-{short}", card(f"{slug}-{stage}-{short}", stage, stage, f"{hero}_{stage.capitalize()}_{camel(short)}", f"{stage}-human.txt", comps, name=piece["name"],
                 aesthetic=f"a clean studio presentation of the {piece['name'].lower()}", note="WARDROBE TEST: same hero, only the piece differs."))
    # Phase 5: two scenes, with the generic wings
    common = {"back": WINGS, "jewelry": library.NECKLACE if female else library.CHAIN, "legs_feet": library.ANKLETS if female else BAREFOOT, "effects": GLOW}
    wr.write("scene", f"{slug}-scene-glamour", card(f"{slug}-scene-glamour", "scene", "scene", f"{hero}_Scene_Glamour", "scene-glamour-human.txt",
             {"pose": f"data/art/motion/{plan['pose']}.json", "wearing": outfits["clothing"], **common, "background": "data/art/backgrounds/fantasy/evening/moonlit-terrace.json"},
             name="Glamour", note="GLAMOUR: a relaxed portrait in an evening setting, with wings: does the photo still look like the person?"))
    wr.write("scene", f"{slug}-scene-signature", card(f"{slug}-scene-signature", "scene", "scene", f"{hero}_Scene_Signature", "scene-with-outfit-human.txt",
             {"pose": "data/art/motion/standing/hand-on-hip-power.json", "wearing": outfits["armor"], **common,
              "background": "data/art/backgrounds/fantasy/elemental/grounded/radiant-sun-realm.json"},
             name="Signature", note="SIGNATURE: armor and wings in a sunlit setting (the cinematic realm Angel Primes uses)."))
    # Phase 6: three motions on the A-pose
    for path in (f"data/art/motion/{m}.json" for m in plan["motions"]):
        fam, short = pathlib.Path(path).parent.name, pathlib.Path(path).stem
        art_id = f"{slug}-motion-{short}"
        wr.write(f"motion/{fam}", art_id, card(art_id, "motion", "/".join(art_layout.dirs_for("motion", [fam])), f"{hero}_Motion_{camel(fam)}_{camel(short)}",
                 "motion-human.txt", denoise="~0.4-0.6", component=path))
    print(f"alpha/{slug}: made {wr.made} cards, {wr.skipped} already existed")


def build(slug):
    kit = load(f"data/art/_kits/angel-primes/{slug}.json")
    ident = kit["identity"]
    hero = kit["hero"]
    female = "bust" in load(ident)["art"]["physique"]
    sex = "female" if female else "male"
    division = pathlib.PurePosixPath(ident).parts[4]  # data/art/heroes/angel-primes/<division>/<slug>.json
    migrate_signature(slug, hero, division)
    wr = Writer(ART / "_sets" / GROUP / division / slug, GROUP)
    out = lambda folder, name: f"prompts/{GROUP}/{division}/{hero}/{folder}/{name}.txt"
    studio = dict(STUDIO)
    studio["jewelry"] = library.NECKLACE if female else library.CHAIN
    ang = library.Angel(slug, kit, ident, sex, division, wr, out)
    card = card_factory(ident, out)

    alpha_chain(wr, card, slug, hero, female, kit["heels"])

    # Studies
    wr.write("head", f"{slug}-x-head", card(f"{slug}-x-head", "head", "head", f"{hero}_X_Head", "head-human.txt", denoise="~0.4-0.6",
             note=f"{hero} head, the golden head."))
    # (the face close-up, views and expressions come from the studio library in scaffold_angel_library.py)

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
    comps = {"pose": norm(sc["pose"]), "expression": norm(sc["expression"]), "wearing": norm(sc["wearing"]), "headwear": ang.sig["headwear"], "jewelry": ang.sig["jewelry"],
             "legs_feet": "data/art/wardrobe/footwear/boots/knight-boots.json" if (armor and not female) else BAREFOOT, "back": norm(sc["back"]),
             "effects": sc["effects"], "companion": norm(sc["companion"]), "background": ang.scene["background"]}
    wr.write("scene", f"{slug}-scene-signature", card(f"{slug}-scene-signature", "scene", "scene", f"{hero}_Scene_Signature", "scene-with-companion-human.txt",
             comps, name="Signature", note="Complete scene from the A-pose: outfit, wings, element effect, bonded pet and an element realm."))
    ang.extend()
    illustrated = dict(comps, realm="data/art/realms/fantasy.json", background=ang.illustrated_background)
    wr.write("scene", f"{slug}-scene-signature-illustrated", card(f"{slug}-scene-signature-illustrated", "scene", "scene", f"{hero}_Scene_Signature_Illustrated", "scene-with-companion-human.txt",
             illustrated, name="Signature (illustrated)", note="The Signature scene again in the illustrated high-fantasy realm (realms/fantasy), to compare with the cinematic realm Angel Primes uses by default (_settings/studio.json realmByGroup)."))
    print(f"{slug}: made {wr.made} cards, {wr.skipped} already existed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--alpha", action="store_true", help="only the two alpha test heroes (alpha/female, alpha/male)")
    ap.add_argument("--coverage", action="store_true", help="report which library pieces the angel cards use; writes nothing")
    args = ap.parse_args()
    if args.coverage:
        library.coverage()
        return
    kits = {p.stem for p in (ART / "_kits" / GROUP).glob("*.json")}
    slugs = sorted(kits) if args.all else [args.slug]
    if args.all:
        slugs = sorted(kits | set(OLDER) | set(ALPHA))
    if args.alpha:
        slugs = sorted(ALPHA)
    if not slugs or slugs == [None]:
        sys.exit("give --slug or --all")
    for slug in slugs:
        build_older(slug) if slug in OLDER and slug not in kits else build_alpha(slug) if slug in ALPHA else build(slug)


if __name__ == "__main__":
    main()
