#!/usr/bin/env python3
"""Scaffold an Angel Primes angel's set from data/art/_kits/angel-primes/<slug>.json (re-runnable; existing cards are kept).

Per angel (a kit lists the choices; the identity in data/art/heroes/angel-primes/<slug>.json supplies sex and look). This file writes the core set:
  1_Alpha      Prime, Bare_Figure (+ Barefoot, Heels for the female angels; males have no Barefoot or Heels step)
  2_Studies    the head          3_Layers  the kit's A-pose underlayer tests          4_Wardrobe  the kit's clothing and armor on the studio backdrop
  2_Studies/motions the kit's motions      5_Scenes/signature  one signature scene with wings, element effect and the bonded pet
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
from scaffold_sister_studio import STUDIO, Writer, camel, norm  # noqa: E402
from scaffold_hero_core import BAREFOOT, DEFAULT_HEELS as OLDER_HEELS, alpha_chain, card_factory  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data/art"
GROUP = "angel-primes"


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


# The older pair, as long as it has no kit (its wardrobe, scenes and layers are hand-picked), still gets the same creation chain and studies as every other angel.
# Once data/art/_kits/angel-primes/<slug>.json exists the normal kit builder takes over and only adds what is missing.
OLDER = {"angelica": "data/art/heroes/angel-primes/female/angelica.json", "angelo": "data/art/heroes/angel-primes/male/angelo.json"}


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
    art_id = f"{slug}-layer-{short}"
    wr.write("pose", art_id, card(art_id, "pose", "poses", f"{hero}_Layer_{camel(short)}", f"pose-{sex}-human.txt", {"underlayer": underlayer}, denoise="~1.0",
             note="UNDERLAYER TEST: fed the Bare image; only the underlayer piece differs. This is the look of her Prime A-pose."))
    alpha_chain(wr, card, slug, hero, female, OLDER_HEELS)
    ang = library.Angel.older(slug, hero, ident, sex, division, wr, out, underlayer)
    ang.extend_older()
    print(f"{slug}: made {wr.made} cards, {wr.skipped} already existed")


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
    wr.write("head", f"{slug}-head", card(f"{slug}-head", "head", "head", f"{hero}_Head", "head-human.txt", denoise="~0.4-0.6",
             note=f"{hero} head, the golden head."))
    # (the face close-up, views and expressions come from the studio library in scaffold_angel_library.py)

    # Layers
    for path in kit["underlayers"]:
        path = norm(path)
        short = pathlib.Path(path).stem
        art_id = f"{slug}-layer-{short}"
        wr.write("pose", art_id, card(art_id, "pose", "poses", f"{hero}_Layer_{camel(short)}", f"pose-{sex}-human.txt", {"underlayer": path}, denoise="~1.0",
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


def build_character(slug):
    """Only the character scenes (Lineup, duty, quiet, domain, celebration) for a kit angel; everything else is left as it is."""
    kit = load(f"data/art/_kits/angel-primes/{slug}.json")
    ident = kit["identity"]
    sex = "female" if "bust" in load(ident)["art"]["physique"] else "male"
    division = pathlib.PurePosixPath(ident).parts[4]
    wr = Writer(ART / "_sets" / GROUP / division / slug, GROUP)
    out = lambda folder, name: f"prompts/{GROUP}/{division}/{kit['hero']}/{folder}/{name}.txt"
    library.Angel(slug, kit, ident, sex, division, wr, out).character()
    print(f"{slug}: made {wr.made} character cards, {wr.skipped} already existed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--character", action="store_true", help="only the character scenes (Lineup, duty, quiet, domain, celebration) for every kit angel, or --slug")
    ap.add_argument("--realm", action="store_true", help="opt in: the realm series (homeland, wayfarer, settlement, weather, nightfall in her element's realistic realm) for every kit angel, or --slug")
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--coverage", action="store_true", help="report which library pieces the angel cards use; writes nothing")
    args = ap.parse_args()
    if args.coverage:
        library.coverage()
        return
    kits = {p.stem for p in (ART / "_kits" / GROUP).glob("*.json")}
    if args.realm:
        for slug in ([args.slug] if args.slug else sorted(kits)):
            kit = load(f"data/art/_kits/angel-primes/{slug}.json")
            ident = kit["identity"]
            sex = "female" if "bust" in load(ident)["art"]["physique"] else "male"
            division = pathlib.PurePosixPath(ident).parts[4]
            wr = Writer(ART / "_sets" / GROUP / division / slug, GROUP)
            out = lambda folder, name, d=division, h=kit["hero"]: f"prompts/{GROUP}/{d}/{h}/{folder}/{name}.txt"
            library.Angel(slug, kit, ident, sex, division, wr, out).realm_series()
            print(f"{slug}: made {wr.made} realm cards, {wr.skipped} already existed")
        return
    if args.character:
        for slug in ([args.slug] if args.slug else sorted(kits)):
            build_character(slug)
        return
    slugs = sorted(kits) if args.all else [args.slug]
    if args.all:
        slugs = sorted(kits | set(OLDER))
    if not slugs or slugs == [None]:
        sys.exit("give --slug or --all")
    for slug in slugs:
        if slug in ("female", "male"):
            sys.exit("Generic sets use bin\\scaffold-generic.cmd, not the Angel scaffolder.")
        elif slug in OLDER and slug not in kits:
            build_older(slug)
        else:
            build(slug)


if __name__ == "__main__":
    main()
