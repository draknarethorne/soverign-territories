#!/usr/bin/env python3
"""Mutation tests for validate_data.py: corrupt a throwaway copy of data/ in each way the
art/gameplay separation is meant to prevent, and assert the validator catches it. Guards
against the validator silently going dead (as the old CI schema workflow did).

Run: python tools/validators/test_validate_data.py
"""
import json
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import validate_data as vd  # noqa: E402

REAL_ROOT = vd.ROOT


def run_on_copy(mutate):
    """Copy data/ to a temp dir, apply mutate(root), run the full validation, return errors."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        shutil.copytree(REAL_ROOT / "data", tmp / "data")
        mutate(tmp)
        vd.ROOT = tmp
        report = vd.Report()
        counts = {}
        vd.check_instances(report, counts)
        cards, identity_of = vd.check_card_art_links(report)
        vd.check_art_cards(report)
        vd.check_variants(report, cards)
        vd.check_kits(report)
        vd.check_piece_refs(report)
        vd.check_animation_cards(report)
        return report.errors
    finally:
        vd.ROOT = REAL_ROOT
        shutil.rmtree(tmp, ignore_errors=True)


def edit(path, fn):
    d = json.loads(path.read_text(encoding="utf-8-sig"))
    fn(d)
    path.write_text(json.dumps(d, indent=2), encoding="utf-8")


CARD = "data/cards/sovereign-dawn/heroes/hero-drakness-thorne.json"
IDENT = "data/art/heroes/drakn-sisters/drakness-thorne.json"
SCENE = "data/art/_sets/drakn-sisters/drakness/scene/signature/drakness-scene-signature.json"
ANIM = "data/animation/_sets/drakn-sisters/drakness/drakness-anim-x-pose-kiss-toss-laugh.json"
SIB_SCENE = "data/art/_sets/drakn-sisters/draknora/scene/signature/draknora-scene-signature.json"
HOLO_SCENE = "data/art/_sets/drakn-sisters/drakness/scene/signature/drakness-scene-signature-holo.json"

CASES = [
    ("baseline is clean", lambda r: None, None),
    ("animation action pointing at a motion piece that does not exist",
     lambda r: edit(r / ANIM, lambda d: d["actions"].append({"motion": "data/animation/motions/magic/nope.json"})), "does not exist"),
    ("animation action with an unknown transition",
     lambda r: edit(r / ANIM, lambda d: d["actions"].append({"beat": "x", "seconds": 1, "transition": "teleport"})), "transition"),
    ("art direction creeping back onto a gameplay card",
     lambda r: edit(r / CARD, lambda d: d["art"].update({"palette": {"primaryColor": "Red"}})), "palette"),
    ("card art.artIdentity pointing at the wrong file",
     lambda r: edit(r / CARD, lambda d: d["art"].update({"artIdentity": "data/art/heroes/drakn-sisters/draknora-thorne.json"})), "bidirectional"),
    ("art identity cardId with no card",
     lambda r: edit(r / IDENT, lambda d: d.update({"cardId": "HERO_NOBODY"})), "no card"),
    ("art identity with a stray gameplay field",
     lambda r: edit(r / IDENT, lambda d: d.update({"element": "Darkness"})), "element"),
    ("female card with a male-shaped physique",
     lambda r: edit(r / IDENT, lambda d: (d["art"]["physique"].pop("bust"), d["art"]["physique"].pop("hips"),
                                          d["art"]["physique"].update({"chest": "x", "waist": "y"}))), "Female"),
    ("typo'd piece path would silently render as prompt text",
     lambda r: edit(r / SCENE, lambda d: d["components"].update({"effects": "data/art/wardrobe/effects/no-such-piece.json"})), "literal text"),
    ("two cards writing the same output file",
     lambda r: edit(r / SCENE, lambda d: d.update({"output": json.loads((r / SIB_SCENE).read_text(encoding="utf-8"))["output"]})), "overwrite"),
    ("duplicate collectionNumber",
     lambda r: edit(r / "data/cards/sovereign-dawn/heroes/hero-draknora-thorne.json", lambda d: d.update({"collectionNumber": "SD-001"})), "collectionNumber"),
    ("unknown field on a reusable piece",
     lambda r: edit(r / "data/art/wardrobe/footwear/heels/glowing-strap-heels.json", lambda d: d.update({"colour": "red"})), "colour"),
    ("modern background slipping into a canon (fantasy-realm) scene",
     lambda r: edit(r / SCENE, lambda d: d["components"].update({"background": "data/art/backgrounds/modern/urban/city-street-daytime.json"})), "scene realm"),
    ("background piece outside fantasy/modern/studio",
     lambda r: shutil.copy(r / "data/art/backgrounds/studio/cream-even.json", r / "data/art/backgrounds/stray.json"), "fantasy/, modern/ or studio/"),
    ("piece id no longer equal to its path (stale id after a move)",
     lambda r: edit(r / "data/art/wardrobe/weapons/swords/greatsword.json", lambda d: d.update({"id": "wardrobe/weapons/greatsword"})), "must equal its path"),
    ("complete scene card switched to the staged template without being renamed",
     lambda r: edit(r / SCENE, lambda d: d.update({"template": "data/art/_templates/heroes/scene-staged-human.txt"})), "staged scenes must use"),
    ("staged-looking name on a complete scene",
     lambda r: edit(r / SCENE, lambda d: d.update({"artId": "drakness-scene-staged-signature"})), "staged scenes must use"),
    ("hair highlight style pointing at a missing piece",
     lambda r: edit(r / "data/art/heroes/drakn-sisters/draknoxa-thorne.json",
                    lambda d: d["art"]["palette"].update({"hairHighlights": "data/art/cosmetics/highlights/no-such-style.json"})), "hairHighlights"),
    ("default underlayer pointing at a missing piece",
     lambda r: edit(r / "data/art/heroes/drakn-sisters/draknoxa-thorne.json",
                    lambda d: d["art"].update({"defaultUnderlayer": "data/art/wardrobe/swimwear/no-such-bikini.json"})), "defaultUnderlayer"),
    ("default footwear pointing at a missing piece",
     lambda r: edit(r / "data/art/heroes/drakn-sisters/draknoxa-thorne.json",
                    lambda d: d["art"].update({"defaultFootwear": "data/art/wardrobe/footwear/heels/no-such-heel.json"})), "defaultFootwear"),
    ("default sheen pointing at a missing piece",
     lambda r: edit(r / "data/art/heroes/drakn-sisters/draknoxa-thorne.json",
                    lambda d: d["art"].update({"defaultSheen": "data/art/wardrobe/finishes/no-such-finish.json"})), "defaultSheen"),
    ("female hero missing a signature cosmetic colour",
     lambda r: edit(r / "data/art/heroes/drakn-sisters/draknoxa-thorne.json",
                    lambda d: d["art"]["palette"].pop("lipColor")), "lipColor"),
    ("female hero missing a signature magic colour",
     lambda r: edit(r / "data/art/heroes/drakn-sisters/draknoxa-thorne.json",
                    lambda d: d["art"]["palette"].pop("magicColor")), "magicColor"),
    ("output folder not matching the card's stage",
     lambda r: edit(r / "data/art/_sets/drakn-sisters/draknora/alpha/draknora-alpha-prime.json",
                    lambda d: d.update({"output": d["output"].replace("/alpha/", "/poses/")})), "must sit in the 'alpha' folder"),
    ("scene file name no longer matching its artId",
     lambda r: (r / SCENE).rename((r / SCENE).with_name("signature.json")), "scene file name must equal"),
    ("theme folder without a theme.json manifest",
     lambda r: (r / "data/art/themes/seasonal/stray").mkdir(), "no theme.json"),
    ("variant art card that does not carry its finish",
     lambda r: edit(r / HOLO_SCENE, lambda d: d.pop("finish")), "bidirectional"),
    ("art card with a finish that its card does not list",
     lambda r: edit(r / CARD, lambda d: d["art"].update({"variants": d["art"]["variants"][:1]})), "does not list it"),
    ("variant with a finish missing from finishes.json",
     lambda r: edit(r / CARD, lambda d: d["art"]["variants"][0].update({"finish": "mythic"})), "finishes.json"),
    ("studio kit naming a piece that does not exist",
     lambda r: edit(r / "data/art/_kits/draknara.json", lambda d: d["clothing"].append("wardrobe/clothing/dresses/no-such-dress")), "kit names"),
    ("scene output not in its family folder",
     lambda r: edit(r / SCENE, lambda d: d.update({"output": d["output"].replace("/scene/signature/", "/scene/")})), "family folder"),
    ("card file filed in the wrong family folder",
     lambda r: (r / "data/art/_sets/drakn-sisters/drakness/scene/story").mkdir(exist_ok=True) or shutil.move(
         str(r / HOLO_SCENE), str(r / "data/art/_sets/drakn-sisters/drakness/scene/story/drakness-scene-signature-holo.json")), "card file must sit in"),
    ("variant artCard belonging to a different hero",
     lambda r: edit(r / CARD, lambda d: d["art"]["variants"][0].update(
         {"artCard": "data/art/_sets/drakn-sisters/draknora/scene/signature/draknora-scene-signature-shiny.json"})), "belongs to"),
]


def main():
    failures = 0
    for name, mutate, needle in CASES:
        errors = run_on_copy(mutate)
        if needle is None:
            ok = not errors
        else:
            ok = any(needle in e for e in errors)
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"\n      got: {errors[:3]}"))
        failures += not ok
    print(f"\n{len(CASES) - failures}/{len(CASES)} validator tests passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
