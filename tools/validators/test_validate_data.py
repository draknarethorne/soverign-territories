#!/usr/bin/env python3
"""Mutation tests for validate_data.py: corrupt the data in each way the art/gameplay separation is meant to
prevent, and assert the validator catches it. Guards against the validator silently going dead (as the old CI
schema workflow did).

Each case changes a few real files in place, runs the validator, and puts them back (copying a 7,000-file tree
per case cost a minute on Windows, so a case undoes itself instead). Every change is first written to a journal
in the temp folder, so if a run is killed half-way the next run restores the files before it starts.

Run: python tools/validators/test_validate_data.py            all cases (about 5 minutes)
     python tools/validators/test_validate_data.py --quick    the baseline plus one case per kind of check (about 1 minute)
"""
import json
import pathlib
import shutil
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import validate_data as vd  # noqa: E402

REAL_ROOT = vd.ROOT
JOURNAL = pathlib.Path(tempfile.gettempdir()) / "sovereign-validator-selftest" / "journal.json"
_ops = []  # undo steps of the running case, newest last


def _save_journal():
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text(json.dumps(_ops), encoding="utf-8")


def _undo(op):
    kind = op[0]
    if kind == "restore":  # put a file's original bytes back
        shutil.copy2(op[2], op[1])
    elif kind == "delete":  # remove a file or folder the case created
        target = pathlib.Path(op[1])
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        elif target.exists():
            target.unlink()
    elif kind == "move":  # move something back
        if pathlib.Path(op[1]).exists():
            pathlib.Path(op[2]).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(op[1], op[2])


def _record(op):
    _ops.append(op)
    _save_journal()


def undo_all():
    while _ops:
        _undo(_ops.pop())
    if JOURNAL.exists():
        JOURNAL.unlink()


def recover():
    """Undo what a killed run left behind."""
    if JOURNAL.exists():
        for op in reversed(json.loads(JOURNAL.read_text(encoding="utf-8"))):
            _undo(op)
        JOURNAL.unlink()
        print("restored files left changed by an interrupted run")


def edit(path, fn):
    d = json.loads(path.read_text(encoding="utf-8-sig"))
    backup = JOURNAL.parent / f"backup-{len(_ops)}-{path.name}"
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
    _record(["restore", str(path), str(backup)])
    fn(d)
    path.write_text(json.dumps(d, indent=2), encoding="utf-8")


def make_dir(path, exist_ok=False):
    if not path.exists():
        _record(["delete", str(path)])
    path.mkdir(exist_ok=exist_ok)


def copy_file(src, dst):
    _record(["delete", str(dst)])
    shutil.copy(src, dst)


def move(src, dst):
    _record(["move", str(dst), str(src)])
    shutil.move(str(src), str(dst))


def run_validation(mutate):
    """Apply a case's change to the real data, run the full validation, undo the change, return the errors."""
    try:
        mutate(REAL_ROOT)
        report = vd.Report()
        counts = {}
        vd.check_instances(report, counts)
        cards, identity_of = vd.check_card_art_links(report)
        vd.check_art_cards(report)
        vd.check_variants(report, cards)
        vd.check_kits(report)
        vd.check_pets(report)
        vd.check_piece_refs(report)
        vd.check_animation_cards(report)
        return report.errors
    finally:
        undo_all()


CARD = "data/cards/sovereign-dawn/heroes/hero-drakness-thorne.json"
IDENT = "data/art/heroes/drakn-sisters/drakness-thorne.json"
SCENE = "data/art/_sets/drakn-sisters/drakness/5_Scenes/signature/drakness-scene-signature.json"
ANIM = "data/animation/_sets/drakn-sisters/drakness/drakness-anim-x-pose-kiss-toss-laugh.json"
SIB_SCENE = "data/art/_sets/drakn-sisters/draknora/5_Scenes/signature/draknora-scene-signature.json"
CELESTIAL = "data/art/heroes/drakn-sisters/draknava/armor/celestial-plate-armor.json"
HOLO_SCENE = "data/art/_sets/drakn-sisters/drakness/5_Scenes/signature/drakness-scene-signature-holo.json"

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
     lambda r: copy_file(r / "data/art/backgrounds/studio/cream-even.json", r / "data/art/backgrounds/stray.json"), "fantasy/, modern/ or studio/"),
    ("piece id no longer equal to its path (stale id after a move)",
     lambda r: edit(r / "data/art/wardrobe/weapons/swords/greatsword.json", lambda d: d.update({"id": "wardrobe/weapons/greatsword"})), "must equal its path"),
    ("piece extending a base that does not exist",
     lambda r: edit(r / "data/art/wardrobe/weapons/swords/greatsword.json", lambda d: d.update({"extends": "data/art/wardrobe/weapons/swords/no-such-sword.json"})), "which does not exist"),
    ("piece extending a base of another kind",
     lambda r: edit(r / "data/art/wardrobe/weapons/swords/greatsword.json", lambda d: d.update({"extends": "data/art/wardrobe/jewelry/necklaces/bone-skull-pendant.json"})), "of kind"),
    ("pieces extending each other in a cycle",
     lambda r: (edit(r / "data/art/wardrobe/weapons/swords/greatsword.json", lambda d: d.update({"extends": "data/art/wardrobe/weapons/swords/longsword.json"})),
                edit(r / "data/art/wardrobe/weapons/swords/longsword.json", lambda d: d.update({"extends": "data/art/wardrobe/weapons/swords/greatsword.json"}))), "cycle"),
    ("{{BASE}} in a piece that extends nothing",
     lambda r: edit(r / "data/art/wardrobe/weapons/swords/greatsword.json", lambda d: d.update({"description": "{{BASE}} with a plain grip"})), "{{BASE}}"),
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
     lambda r: edit(r / "data/art/_sets/drakn-sisters/draknora/1_Alpha/1_Prime/draknora-alpha-prime.json",
                    lambda d: d.update({"output": d["output"].replace("/1_Alpha/1_Prime/", "/3_Layers/")})), "must sit in the 'alpha' folder"),
    ("sister companion piece that no longer extends her Elder Dragon's frame",
     lambda r: edit(r / "data/art/heroes/drakn-sisters/draknora/companion/draknora-bond-dragon.json",
                    lambda d: d.pop("extends")), "must extend her Elder Dragon"),
    ("sister scene that types the dragon instead of naming the piece",
     lambda r: edit(r / "data/art/_sets/drakn-sisters/draknora/5_Scenes/story/draknora-scene-bond.json",
                    lambda d: d["components"].update({"companion": "her aligned Elder Dragon, Pyraxis, beside her"})), "not type the dragon"),
    ("scene file name no longer matching its artId",
     lambda r: move(r / SCENE, (r / SCENE).with_name("signature.json")), "scene file name must equal"),
    ("theme folder without a theme.json manifest",
     lambda r: make_dir(r / "data/art/themes/seasonal/stray"), "no theme.json"),
    ("variant art card that does not carry its finish",
     lambda r: edit(r / HOLO_SCENE, lambda d: d.pop("finish")), "bidirectional"),
    ("art card with a finish that its card does not list",
     lambda r: edit(r / CARD, lambda d: d["art"].update({"variants": d["art"]["variants"][:1]})), "does not list it"),
    ("variant with a finish missing from finishes.json",
     lambda r: edit(r / CARD, lambda d: d["art"]["variants"][0].update({"finish": "mythic"})), "finishes.json"),
    ("studio kit naming a piece that does not exist",
     lambda r: edit(r / "data/art/_kits/draknara.json", lambda d: d["clothing"].append("wardrobe/clothing/dresses/no-such-dress")), "kit names"),
    ("scene output not in its family folder",
     lambda r: edit(r / SCENE, lambda d: d.update({"output": d["output"].replace("/5_Scenes/signature/", "/5_Scenes/")})), "below its hero folder"),
    ("card file filed in the wrong family folder",
     lambda r: (make_dir(r / "data/art/_sets/drakn-sisters/drakness/5_Scenes/story", exist_ok=True),
                move(r / HOLO_SCENE, r / "data/art/_sets/drakn-sisters/drakness/5_Scenes/story/drakness-scene-signature-holo.json")), "card file must sit in"),
    ("variant artCard belonging to a different hero",
     lambda r: edit(r / CARD, lambda d: d["art"]["variants"][0].update(
         {"artCard": "data/art/_sets/drakn-sisters/draknora/5_Scenes/signature/draknora-scene-signature-shiny.json"})), "belongs to"),
    ("pet bonded to a different angel than the one that lists it",
     lambda r: edit(r / "data/art/pets/angel-primes/lumen.json",
                    lambda d: d.update({"bondedTo": "data/art/heroes/angel-primes/male/auriel.json"})), "does not point back"),
    ("angel card filed outside its division folder",
     lambda r: move(r / "data/art/_sets/angel-primes/female/seraphine", r / "data/art/_sets/angel-primes/seraphine"), "division folder"),
    ("angel output with a different division than its card file",
     lambda r: edit(r / "data/art/_sets/angel-primes/female/seraphine/1_Alpha/1_Prime/seraphine-alpha-prime.json",
                    lambda d: d.update({"output": d["output"].replace("/female/", "/male/")})), "same division folder"),
    ("piece extending a frame without filling its slots",
     lambda r: edit(r / CELESTIAL, lambda d: d.pop("varsFrom")), "not filled"),
    ("vars that fill no slot of the frame",
     lambda r: edit(r / CELESTIAL, lambda d: d.update({"vars": {"NO_SUCH_SLOT": "x"}})), "fill no [[SLOT]]"),
    ("vars on a piece that extends nothing",
     lambda r: edit(r / "data/art/wardrobe/weapons/swords/greatsword.json", lambda d: d.update({"vars": {"A": "b"}})), "vars only make sense"),
    ("varsFrom pointing at something that is not a design",
     lambda r: edit(r / CELESTIAL, lambda d: d.update({"varsFrom": "data/art/wardrobe/weapons/swords/greatsword.json"})), "not a kind 'design'"),
]


# One case per kind of check, for --quick.
QUICK = {"baseline is clean", "animation action pointing at a motion piece that does not exist", "art direction creeping back onto a gameplay card",
         "typo'd piece path would silently render as prompt text", "unknown field on a reusable piece", "piece extending a base that does not exist",
         "pieces extending each other in a cycle", "piece extending a frame without filling its slots", "output folder not matching the card's stage", "studio kit naming a piece that does not exist",
         "pet bonded to a different angel than the one that lists it", "angel card filed outside its division folder",
         "sister companion piece that no longer extends her Elder Dragon's frame", "sister scene that types the dragon instead of naming the piece"}


def main():
    recover()
    cases = [c for c in CASES if "--quick" not in sys.argv or c[0] in QUICK]
    failures, started = 0, time.time()
    for name, mutate, needle in cases:
        errors = run_validation(mutate)
        ok = (not errors) if needle is None else any(needle in e for e in errors)
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"\n      got: {errors[:3]}"), flush=True)
        failures += not ok
    print(f"\n{len(cases) - failures}/{len(cases)} validator tests passed in {int(time.time() - started)} s")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
