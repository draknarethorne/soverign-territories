#!/usr/bin/env python3
"""Tests for reusable piece resolution and the shared edit prompt's token contract.

Most tests use throwaway pieces; the edit-pilot integration test reads the real
assembly card and template without writing generated output.

Run: python -m unittest tools.generators.test_gen_prompt_extends
"""
import copy
import contextlib
import io
import json
import pathlib
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import gen_prompt as gp  # noqa: E402
import scaffold_angel_set as angel_scaffold  # noqa: E402
import scaffold_generic_set as generic_scaffold  # noqa: E402


def female_outfit_card(name):
    folder = pathlib.Path("data/art/_sets/sovereign-females/female/1_Alpha/4_Outfits")
    for prefix, family in (("celestial-", "celestial"), ("gown", "gowns"), ("halter", "dresses"),
                           ("silk", "sets"), ("two-piece", "sets")):
        if name.startswith(prefix):
            folder /= family
            break
    return folder / f"female-alpha-outfit-{name}.json"


class ExtendsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.patch = mock.patch.object(gp, "ROOT", self.tmp)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def put(self, rel, **fields):
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"id": rel, "kind": "jewelry", "name": rel, "compatibleStages": ["scene"], **fields}), encoding="utf-8")
        return p

    BASE = "a plain {{METAL}} necklace."

    def test_cleanup_keeps_reference_bound_prompt_when_assembly_moves(self):
        directory = self.tmp / "prompts" / "sovereign-females" / "Female" / "0_Edit" / "cleanup"
        directory.mkdir(parents=True)
        bound = directory / "Female_Edit_Cleanup_Basic.txt"
        current = directory / "Female_Edit_Cleanup_Basic_Audition.txt"
        orphan = directory / "Female_Edit_Obsolete.txt"
        for path in (bound, current, orphan):
            path.write_text(path.name, encoding="utf-8")
        expected = {current.relative_to(self.tmp).as_posix()}
        found = gp.cleanup_orphans(expected, apply=True)
        self.assertEqual(found, [orphan.relative_to(self.tmp).as_posix()])
        self.assertTrue(bound.is_file())
        self.assertTrue(current.is_file())
        self.assertFalse(orphan.exists())

    def test_cleanup_keeps_retained_legacy_prime_prompt(self):
        directory = self.tmp / "prompts" / "sovereign-females" / "Female" / "1_Alpha" / "1_Prime"
        directory.mkdir(parents=True)
        legacy = directory / "Female_Alpha_1_Prime.txt"
        current = directory / "Female_Alpha_1_Prime_Audition.txt"
        legacy.write_text("legacy", encoding="utf-8")
        current.write_text("current", encoding="utf-8")
        self.assertEqual(gp.cleanup_orphans({current.relative_to(self.tmp).as_posix()}, apply=True), [])
        self.assertEqual(legacy.read_text(encoding="utf-8"), "legacy")

    def test_a_piece_without_extends_is_unchanged(self):
        p = self.put("a.json", description=self.BASE)
        self.assertEqual(gp.load_piece(p)["description"], self.BASE)

    def test_a_set_joins_the_descriptions_of_the_pieces_it_includes(self):
        self.put("ring.json", description="a slim {{METAL}} band.")
        self.put("ear.json", description="small {{METAL}} studs")
        p = self.put("set.json", includes=["ring.json", "ear.json"])
        out = gp.load_piece(p)
        self.assertEqual(out["description"], "a slim {{METAL}} band; small {{METAL}} studs")
        self.assertNotIn("includes", out)

    def test_a_set_can_include_a_piece_that_extends_a_frame(self):
        self.put("base.json", description="a pendant of [[SHAPE]]")
        self.put("hero.json", extends="base.json", vars={"SHAPE": "a curved feather"})
        self.put("ring.json", description="a slim band")
        p = self.put("set.json", includes=["hero.json", "ring.json"])
        self.assertEqual(gp.load_piece(p)["description"], "a pendant of a curved feather; a slim band")

    def test_base_placeholder_splices_the_base_text(self):
        self.put("base.json", description=self.BASE)
        p = self.put("hero.json", extends="base.json", description="{{BASE}} A tiny {{GEM}} sun hangs from it.")
        self.assertEqual(gp.load_piece(p)["description"], "a plain {{METAL}} necklace. A tiny {{GEM}} sun hangs from it.")

    def test_leading_plus_appends_to_the_base(self):
        self.put("base.json", description=self.BASE)
        p = self.put("hero.json", extends="base.json", description="+ A tiny sun hangs from it.")
        self.assertEqual(gp.load_piece(p)["description"], "a plain {{METAL}} necklace. A tiny sun hangs from it.")

    def test_plus_before_punctuation_continues_the_base_sentence(self):
        self.put("base.json", description="a plain {{METAL}} necklace")
        p = self.put("hero.json", extends="base.json", description="+, with a tiny sun hanging from it")
        self.assertEqual(gp.load_piece(p)["description"], "a plain {{METAL}} necklace, with a tiny sun hanging from it")

    def test_a_plain_description_replaces_the_base(self):
        self.put("base.json", description=self.BASE)
        p = self.put("hero.json", extends="base.json", description="a different thing")
        self.assertEqual(gp.load_piece(p)["description"], "a different thing")

    def test_negatives_merge_and_other_fields_are_inherited(self):
        self.put("base.json", description=self.BASE, negatives=["chains", "straps"], compatibleStages=["armor"])
        p = self.put("hero.json", extends="base.json", description="+ more", negatives=["straps", "cups"])
        out = gp.load_piece(p)
        self.assertEqual(out["negatives"], ["chains", "straps", "cups"])
        self.assertNotIn("extends", out)

    def test_selected_negative_slots_deduplicate_whole_phrases_in_template_order(self):
        self.put("a.json", description="first", negatives=["Hands, fingers", "blur"])
        self.put("b.json", description="second", negatives=["hands, FINGERS", "noise"])
        card = {"components": {"a": "a.json", "b": "b.json"}}
        original = gp.resolve_components_tokens(card)
        deduped = gp.resolve_components_tokens(card, ("B", "A"))
        self.assertEqual(original["A_NEG"], "Hands, fingers, blur")
        self.assertEqual(original["B_NEG"], "hands, FINGERS, noise")
        self.assertEqual(deduped["B_NEG"], "hands, FINGERS, noise")
        self.assertEqual(deduped["A_NEG"], "blur")

    def test_chains_resolve_through_several_bases(self):
        self.put("a.json", description="one")
        self.put("b.json", extends="a.json", description="{{BASE}} two")
        p = self.put("c.json", extends="b.json", description="{{BASE}} three")
        self.assertEqual(gp.load_piece(p)["description"], "one two three")

    def test_a_cycle_stops_with_an_error(self):
        self.put("a.json", extends="b.json", description="{{BASE}} x")
        p = self.put("b.json", extends="a.json", description="{{BASE}} y")
        with self.assertRaises(SystemExit) as cm:
            gp.load_piece(p)
        self.assertIn("extends itself", str(cm.exception))

    def test_a_missing_base_stops_with_an_error(self):
        p = self.put("a.json", extends="nope.json", description="x")
        with self.assertRaises(SystemExit) as cm:
            gp.load_piece(p)
        self.assertIn("does not exist", str(cm.exception))

    FRAME = "armor of {{METAL}}: plates shaped like [[SHAPE]], set with [[GEM]]."

    def test_slots_in_a_frame_are_filled_by_vars(self):
        self.put("frame.json", description=self.FRAME)
        p = self.put("hero.json", extends="frame.json", vars={"SHAPE": "feathers", "GEM": "a jade gem"})
        out = gp.load_piece(p)
        self.assertEqual(out["description"], "armor of {{METAL}}: plates shaped like feathers, set with a jade gem.")
        self.assertNotIn("vars", out)

    def test_vars_chain_and_the_nearest_value_wins(self):
        self.put("frame.json", description=self.FRAME, vars={"GEM": "a plain gem"})
        self.put("mid.json", extends="frame.json", vars={"SHAPE": "moons"})
        p = self.put("hero.json", extends="mid.json", vars={"GEM": "a moonstone"})
        self.assertEqual(gp.load_piece(p)["description"], "armor of {{METAL}}: plates shaped like moons, set with a moonstone.")

    def test_an_unfilled_slot_is_an_error(self):
        self.put("frame.json", description=self.FRAME)
        p = self.put("hero.json", extends="frame.json", vars={"SHAPE": "feathers"})
        with self.assertRaises(SystemExit) as cm:
            gp.load_piece(p)
        self.assertIn("GEM", str(cm.exception))

    def test_vars_from_a_design_file_are_shared_and_own_vars_win(self):
        self.put("frame.json", description=self.FRAME)
        design = self.put("design.json", kind="design", vars={"SHAPE": "feathers", "GEM": "a jade gem"})
        design.write_text(json.dumps({"id": "design", "kind": "design", "name": "d", "compatibleStages": ["armor"], "vars": {"SHAPE": "feathers", "GEM": "a jade gem"}}), encoding="utf-8")
        p = self.put("hero.json", extends="frame.json", varsFrom="design.json")
        self.assertEqual(gp.load_piece(p)["description"], "armor of {{METAL}}: plates shaped like feathers, set with a jade gem.")
        q = self.put("other.json", extends="frame.json", varsFrom="design.json", vars={"GEM": "a ruby"})
        self.assertTrue(gp.load_piece(q)["description"].endswith("set with a ruby."))

    def test_slots_also_fill_inside_a_plus_extension_and_negatives(self):
        self.put("frame.json", description=self.FRAME, negatives=["no [[SHAPE]] cups"])
        p = self.put("hero.json", extends="frame.json", description="+ Extra [[SHAPE]].", vars={"SHAPE": "wings", "GEM": "a ruby"})
        out = gp.load_piece(p)
        self.assertTrue(out["description"].endswith("a ruby. Extra wings."))
        self.assertEqual(out["negatives"], ["no wings cups"])


class MasculineTests(unittest.TestCase):
    def test_possessive_and_object_pronouns(self):
        self.assertEqual(gp.masculine("She leaps with her weapon swept behind her and her free hand flung forward."),
                         "He leaps with his weapon swept behind him and his free hand flung forward.")

    def test_her_before_a_noun_is_his_and_at_the_end_is_him(self):
        self.assertEqual(gp.masculine("Her hair lifts around her. She smiles to her left."), "His hair lifts around him. He smiles to his left.")

    def test_himself_and_hers(self):
        self.assertEqual(gp.masculine("the choice is hers; she steadies herself"), "the choice is his; he steadies himself")


class SlugFilterTests(unittest.TestCase):
    def test_a_slug_named_like_a_division_matches_only_that_hero(self):
        """The generic Female hero must not pick the named female Angel division."""
        paths = gp.iter_card_paths(group="sovereign-females", slug="female")
        self.assertTrue(paths)
        self.assertTrue(all("/sovereign-females/female/" in p.as_posix() for p in paths))
        self.assertTrue(all("/female/azaline/" not in p.as_posix() for p in paths))
        self.assertFalse(gp.iter_card_paths(group="angel-primes", slug="female"))
        self.assertTrue(any("/female/azaline/" in p.as_posix() for p in gp.iter_card_paths(group="angel-primes", slug="azaline")), "a normal angel is still found by her slug")

    def test_generic_group_move_preserves_generated_tokens(self):
        for group, slug in (("sovereign-females", "female"), ("sovereign-males", "male")):
            cards = gp.iter_card_paths(group=group, slug=slug)
            self.assertTrue(cards)
            self.assertFalse(gp.iter_card_paths(group="angel-primes", slug=slug))
            for card in cards:
                with self.subTest(card=card):
                    current = gp.generate(card, tokens_only=True)
                    with mock.patch.object(gp, "group_of", return_value="angel-primes"):
                        previous = gp.generate(card, tokens_only=True)
                    self.assertEqual(current, previous)

    def test_generic_scaffolding_previews_and_preserves_existing_cards(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            art = pathlib.Path(tmp) / "art"
            with mock.patch.object(generic_scaffold, "ART", art), \
                    mock.patch.object(generic_scaffold.library.subprocess, "run",
                                      side_effect=AssertionError("unexpected Angel scaffold")):
                for slug in ("female", "male"):
                    group = f"sovereign-{slug}s"
                    before = {p: p.read_bytes() for p in art.rglob("*") if p.is_file()}
                    preview = generic_scaffold.build_generic(slug)
                    self.assertGreater(preview.made, 0)
                    self.assertEqual(before, {p: p.read_bytes() for p in art.rglob("*") if p.is_file()})
                    built = generic_scaffold.build_generic(slug, dry_run=False)
                    self.assertEqual(built.made, preview.made)
                    cards = sorted((art / "_sets" / group / slug).rglob("*.json"))
                    self.assertTrue(cards)
                    for path in cards:
                        card = json.loads(path.read_text(encoding="utf-8"))
                        self.assertTrue(card["output"].startswith(f"prompts/{group}/{slug.capitalize()}/"))
                        self.assertEqual(card["heroArt"], f"data/art/heroes/{group}/{slug}.json")
                    protected = next(p for p in cards if p.name == f"{slug}-view-back.json")
                    edited = json.loads(protected.read_text(encoding="utf-8"))
                    edited["notes"] = "Retain the user's change"
                    protected.write_text(json.dumps(edited), encoding="utf-8")
                    original = protected.read_bytes()
                    repeat = generic_scaffold.build_generic(slug, dry_run=False)
                    self.assertEqual(repeat.made, 0)
                    self.assertEqual(protected.read_bytes(), original)
                self.assertFalse((art / "_sets" / "angel-primes").exists())

    def test_angel_scaffolder_does_not_run_generic_sets(self):
        with mock.patch.object(sys, "argv", ["scaffold_angel_set.py", "--all"]), \
                mock.patch.object(angel_scaffold, "build") as build, \
                mock.patch.object(angel_scaffold, "build_older"), \
                mock.patch.object(generic_scaffold, "build_generic") as generic:
            angel_scaffold.main()
            self.assertTrue(build.called)
            generic.assert_not_called()
        with mock.patch.object(sys, "argv", ["scaffold_angel_set.py", "--alpha"]), \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            angel_scaffold.main()
        with mock.patch.object(sys, "argv", ["scaffold_angel_set.py", "--slug", "female"]), \
                self.assertRaisesRegex(SystemExit, "scaffold-generic"):
            angel_scaffold.main()


class ArtPromptIntegrationTests(unittest.TestCase):
    def assert_only_duplicate_negatives_removed(self, current, previous):
        current_positive, current_negative = current.split("negative prompt:", 1)
        previous_positive, previous_negative = previous.split("negative prompt:", 1)
        self.assertEqual(current_positive, previous_positive)

        def terms(text):
            return [term.strip().lower().rstrip(".") for term in text.replace("\n", " ").split(",") if term.strip()]

        self.assertEqual(terms(current_negative), list(dict.fromkeys(terms(previous_negative))))

    def test_background_enhance_continues_existing_clothing_when_extending(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        card = root / "data/art/_sets/sovereign-females/female/0_Edit/background/female-edit-background-enhance.json"
        with mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(card)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("If clothing is present, preserve its fabric, colors and coverage", positive)
        self.assertIn("continuing it naturally into any newly visible areas", positive)
        self.assertIn("changed clothing", negative)

    def test_named_enhance_uses_character_identity_and_not_generic_figure(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = root / "data/art/_sets/angel-primes/female/angelica/0_Edit/enhance/angelica-edit-enhance-basic.json"
        card = json.loads(path.read_text(encoding="utf-8"))
        identity = gp.load_identity(card["heroArt"])
        expected = gp.tokens_for(identity, card["keyDetails"])
        with mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn(expected["FIGURE_FRAME"], positive)
        for field in ("build", "torso", "legs"):
            self.assertIn(gp.decap(identity["art"]["physique"][field]), positive)
        for token in ("HAIR", "EYE", "SKIN"):
            self.assertIn(expected[token], positive)
        self.assertNotIn(identity["art"]["physique"]["bust"].lower(), positive.lower())
        self.assertIn("Wearing: If clothing is present", positive)
        self.assertIn("continuing it naturally into any newly visible areas", positive)
        self.assertNotIn("reshaped body", negative)
        other = copy.deepcopy(identity)
        other["art"]["physique"]["build"] = "SECOND_CHARACTER_FRAME"
        other["art"]["physique"]["bust"] = "SECOND_CHARACTER_DETAIL"
        with mock.patch.object(gp, "load_identity", return_value=other), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as second_write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        self.assertIn("second_character_frame", second_write.call_args.args[1].lower())
        self.assertNotIn("second_character_detail", second_write.call_args.args[1].lower())

    def test_named_pose_audition_preserves_source_body_and_outfit_policy(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = root / "data/art/_sets/angel-primes/female/angelica/0_Edit/pose/angelica-edit-pose-grounded-three-quarter.json"
        card = json.loads(path.read_text(encoding="utf-8"))
        with mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("Preserve visible body proportions", positive)
        self.assertIn("both feet flat on the floor", positive)
        self.assertIn("Preserve the incoming clothing and accessories, if any", positive)
        self.assertIn("Continue existing clothing naturally into any newly visible areas", positive)
        self.assertIn("do not select a replacement outfit or add accessories", positive)
        self.assertNotIn("Wearing:", positive)
        self.assertEqual(positive.count("Preserve the same person's recognizable face"), 1)
        self.assertIn("reshaped body", negative)
        self.assertNotIn(gp.decap(gp.load_identity(card["heroArt"])["art"]["physique"]["build"]), positive)

    def test_generic_pose_auditions_preserve_outfit_with_extension(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/pose")
        for variant in ("grounded-three-quarter", "relaxed-three-quarter"):
            path = folder / f"female-edit-pose-{variant}.json"
            with self.subTest(variant=variant), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn("Preserve the incoming clothing and accessories, if any", positive)
            self.assertIn("Continue existing clothing naturally into any newly visible areas", positive)
            self.assertIn("do not select a replacement outfit", positive)
            self.assertEqual(positive.count("Preserve the same person's recognizable face"), 1)
            self.assertIn("changed clothing", negative)

    def test_named_background_preserves_clothing_but_removes_accessories(self):
        path = pathlib.Path("data/art/_sets/angel-primes/female/angelica/0_Edit/background/angelica-edit-background-basic.json")
        card = json.loads(path.read_text(encoding="utf-8"))
        identity = gp.load_identity(card["heroArt"])
        tokens = gp.tokens_for(identity, card["keyDetails"])
        with mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        for token in ("FIGURE_FRAME", "HAIR", "EYE", "SKIN"):
            self.assertIn(tokens[token], positive)
        self.assertIn("Preserve the incoming clothing, if any", positive)
        self.assertIn("Do not add clothing.", positive)
        self.assertIn("free of purses, accessories and jewelry", positive)
        self.assertNotIn("preserve the incoming clothing and accessories", positive.lower())
        self.assertIn("Wearing: Preserve the incoming clothing, if any", positive)
        self.assertIn("changed clothing", negative)

    def test_adaptive_character_background_keeps_source_appearance_and_character_frame(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/angel-primes/female/azaline/0_Edit/background/azaline-edit-background-basic.json")
        card = json.loads((root / path).read_text(encoding="utf-8"))
        identity = gp.load_identity(card["heroArt"])
        frame = gp.tokens_for(identity, [])["FIGURE_FRAME"]
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn(frame, positive)
        self.assertIn("preserve expression and eye color", positive.lower())
        self.assertIn("Keep the incoming hairstyle, hair length, texture and color", positive)
        self.assertIn("Keep the incoming skin tone and tan", positive)
        self.assertIn("Wearing: Preserve the incoming clothing, if any", positive)
        self.assertIn("free of purses, accessories and jewelry", positive)
        for field in ("hairColor", "eyeColor", "skinTone"):
            self.assertNotIn(identity["art"]["palette"][field].lower(), positive.lower())
        self.assertIn("changed clothing", negative)
        self.assertNotIn("{{", positive)

    def test_adaptive_angel_background_batch_uses_each_character_frame(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes/female")
        for slug in ("azaline", "camaris", "gavrielle", "haniya", "nyxene",
                     "ravaelle", "remiah", "sammara", "sandalyn", "seraphine"):
            path = base / slug / "0_Edit/background" / f"{slug}-edit-background-basic.json"
            card = json.loads((root / path).read_text(encoding="utf-8"))
            identity = gp.load_identity(card["heroArt"])
            frame = gp.tokens_for(identity, [])["FIGURE_FRAME"]
            with self.subTest(hero=slug), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn(frame, positive)
            self.assertIn("Keep the incoming skin tone and tan", positive)
            self.assertIn("Keep the incoming hairstyle", positive)
            self.assertIn("preserve expression and eye color", positive.lower())
            self.assertIn("Wearing: Preserve the incoming clothing, if any", positive)
            self.assertIn("changed clothing", negative)
            for field in ("hairColor", "eyeColor", "skinTone"):
                self.assertNotIn(identity["art"]["palette"][field].lower(), positive.lower())
            self.assertNotIn("{{", positive)

    def test_character_grounded_pose_preserves_source_in_every_angel(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes/female")
        for slug in ("angelica", "azaline", "camaris", "gavrielle", "haniya",
                     "nyxene", "ravaelle", "remiah", "sammara", "sandalyn", "seraphine"):
            path = base / slug / "0_Edit/pose" / f"{slug}-edit-pose-grounded-three-quarter.json"
            card = json.loads((root / path).read_text(encoding="utf-8"))
            self.assertEqual(pathlib.Path(card["heroArt"]).stem, slug)
            with self.subTest(hero=slug), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
            self.assertIn("preserve the incoming", positive)
            self.assertIn("clothing", positive)
            self.assertIn("hair", positive)
            self.assertNotIn("{{", positive)

    def test_adaptive_angel_enhance_uses_character_frame_and_source_appearance(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes/female")
        for slug in ("azaline", "camaris", "gavrielle", "haniya", "nyxene",
                     "ravaelle", "remiah", "sammara", "sandalyn", "seraphine"):
            path = base / slug / "0_Edit/enhance" / f"{slug}-edit-enhance-basic.json"
            card = json.loads((root / path).read_text(encoding="utf-8"))
            identity = gp.load_identity(card["heroArt"])
            frame = gp.tokens_for(identity, [])["FIGURE_FRAME"]
            with self.subTest(hero=slug), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive = write.call_args.args[1].split("negative prompt:", 1)[0]
            self.assertIn(frame, positive)
            self.assertIn("Keep the incoming skin tone and tan", positive)
            self.assertIn("Keep the incoming hairstyle", positive)
            self.assertIn("preserve expression and eye color", positive.lower())
            self.assertIn("If clothing is present, preserve its fabric, colors and coverage", positive)
            for field in ("hairColor", "eyeColor", "skinTone"):
                self.assertNotIn(identity["art"]["palette"][field].lower(), positive.lower())
            self.assertNotIn("{{", positive)

    def test_character_preservation_edits_keep_generic_prompt_semantics(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes")
        for folder, suffix in (("background", "edit-background"),
                               ("background", "edit-background-bust"),
                               ("pose", "edit-pose-relaxed-three-quarter")):
            generic = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit") / folder / f"female-{suffix}.json"
            heroes = ("angelica", "azaline", "camaris", "gavrielle", "haniya",
                      "nyxene", "ravaelle", "remiah", "sammara", "sandalyn", "seraphine")
            rendered = {}
            for slug in ("generic", *heroes):
                path = generic if slug == "generic" else base / "female" / slug / "0_Edit" / folder / f"{slug}-{suffix}.json"
                if slug != "generic":
                    card = json.loads((root / path).read_text(encoding="utf-8"))
                    self.assertEqual(pathlib.Path(card["heroArt"]).stem, slug)
                with mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                rendered[slug] = write.call_args.args[1].split("\nprompt:\n", 1)[1]
                if slug != "generic":
                    with self.subTest(family=suffix, hero=slug):
                        self.assertEqual(rendered["generic"], rendered[slug])
                        self.assertNotIn("{{", rendered[slug])

    def test_character_cleanup_uses_identity_frame_and_keeps_family_selections(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes")
        for suffix in ("edit-cleanup", "edit-cleanup-basic", "edit-cleanup-enhance"):
            generic = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/cleanup") / f"female-{suffix}.json"
            original = json.loads((root / generic).read_text(encoding="utf-8"))
            for slug in ("angelica", "azaline", "camaris", "gavrielle", "haniya",
                         "nyxene", "ravaelle", "remiah", "sammara", "sandalyn", "seraphine"):
                path = base / "female" / slug / "0_Edit/cleanup" / f"{slug}-{suffix}.json"
                card = json.loads((root / path).read_text(encoding="utf-8"))
                expected_components = dict(original["components"], body="{{FIGURE_FRAME}}")
                self.assertEqual(card["components"], expected_components)
                self.assertEqual(pathlib.Path(card["heroArt"]).stem, slug)
                identity = gp.load_identity(card["heroArt"])
                frame = gp.tokens_for(identity, [])["FIGURE_FRAME"]
                with self.subTest(family=suffix, hero=slug), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                positive = write.call_args.args[1].split("negative prompt:", 1)[0]
                self.assertIn(frame, positive)
                self.assertIn("Slightly increase the tan", positive)
                self.assertIn("existing outfit", positive)
                self.assertNotIn("{{", positive)

    def test_character_background_changes_only_generic_frame(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes")
        for variant in ("enhance", "plus"):
            suffix = f"edit-background-{variant}"
            generic = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/background") / f"female-{suffix}.json"
            original = json.loads((root / generic).read_text(encoding="utf-8"))
            for slug in ("angelica", "azaline", "camaris", "gavrielle", "haniya",
                         "nyxene", "ravaelle", "remiah", "sammara", "sandalyn", "seraphine"):
                path = base / "female" / slug / "0_Edit/background" / f"{slug}-{suffix}.json"
                card = json.loads((root / path).read_text(encoding="utf-8"))
                self.assertEqual(card["components"], dict(original["components"], body="{{FIGURE_FRAME}}"))
                self.assertEqual(pathlib.Path(card["heroArt"]).stem, slug)
                frame = gp.tokens_for(gp.load_identity(card["heroArt"]), [])["FIGURE_FRAME"]
                with self.subTest(variant=variant, hero=slug), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                self.assertIn(frame, positive)
                self.assertNotIn("{{", positive)
                if variant == "enhance":
                    self.assertIn("If clothing is present", positive)
                    self.assertIn("changed clothing", negative)
                else:
                    self.assertIn("original outfit's colors", positive)
                    self.assertIn("source outfit remnants", negative)

    def test_character_deluxe_and_full_use_identity_frame(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes")
        for folder, suffix in (("deluxe", "edit-deluxe-reclining"),
                               ("deluxe", "edit-deluxe-resting"),
                               ("deluxe", "edit-deluxe-seated"),
                               ("deluxe", "edit-deluxe-side-resting"),
                               ("full", "edit-full")):
            generic = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit") / folder / f"female-{suffix}.json"
            original = json.loads((root / generic).read_text(encoding="utf-8"))
            for slug in ("angelica", "azaline", "camaris", "gavrielle", "haniya",
                         "nyxene", "ravaelle", "remiah", "sammara", "sandalyn", "seraphine"):
                path = base / "female" / slug / "0_Edit" / folder / f"{slug}-{suffix}.json"
                card = json.loads((root / path).read_text(encoding="utf-8"))
                self.assertEqual(card["components"], dict(original["components"], body="{{FIGURE_FRAME}}"))
                self.assertEqual(pathlib.Path(card["heroArt"]).stem, slug)
                frame = gp.tokens_for(gp.load_identity(card["heroArt"]), [])["FIGURE_FRAME"]
                with self.subTest(family=suffix, hero=slug), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                positive = write.call_args.args[1].split("negative prompt:", 1)[0]
                self.assertIn(frame, positive)
                self.assertNotIn("{{", positive)
                if folder == "full":
                    self.assertIn("Keep the existing outfit", positive)
                else:
                    self.assertNotIn("Wearing:", positive)

    def test_character_enhance_variants_follow_appearance_and_expression_policy(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes/female")
        for variant in ("plus", "pose"):
            for slug in ("angelica", "azaline", "camaris", "gavrielle", "haniya",
                         "nyxene", "ravaelle", "remiah", "sammara", "sandalyn", "seraphine"):
                path = base / slug / "0_Edit/enhance" / f"{slug}-edit-enhance-{variant}.json"
                card = json.loads((root / path).read_text(encoding="utf-8"))
                identity = gp.load_identity(card["heroArt"])
                tokens = gp.tokens_for(identity, card.get("keyDetails", []))
                with self.subTest(variant=variant, hero=slug), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                self.assertIn(tokens["FIGURE_FRAME"], positive)
                if slug == "angelica":
                    for token in ("HAIR", "EYE", "SKIN"):
                        self.assertIn(tokens[token], positive)
                else:
                    self.assertIn("Keep the incoming skin tone and tan", positive)
                    self.assertIn("Keep the incoming hairstyle", positive)
                    self.assertIn("incoming eye color" if variant == "pose" else "eye color", positive.lower())
                    for field in ("hairColor", "eyeColor", "skinTone"):
                        self.assertNotIn(identity["art"]["palette"][field].lower(), positive.lower())
                if variant == "pose":
                    self.assertIn("knowing smirk", positive.lower())
                    eye_detail = gp.load_piece(root / "data/art/studio/photography/eye-definition.json")["description"]
                    self.assertIn(eye_detail, positive)
                    self.assertNotIn("preserve expression", positive.lower())
                    self.assertIn("If clothing is present", positive)
                    self.assertIn("changed clothing", negative)
                else:
                    self.assertIn("original outfit's colors", positive)
                    self.assertIn("source outfit remnants", negative)
                self.assertNotIn("{{", positive)

    def test_sister_edit_pilots_resolve_identity_and_preservation_independently(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/drakn-sisters/drakness/0_Edit")
        for folder, filename in (("background", "drakness-edit-background-basic.json"),
                                 ("pose", "drakness-edit-pose-grounded-three-quarter.json")):
            path = base / folder / filename
            card = json.loads((root / path).read_text(encoding="utf-8"))
            identity = gp.load_identity(card["heroArt"])
            tokens = gp.tokens_for(identity, card.get("keyDetails", []))
            with self.subTest(family=folder), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive = write.call_args.args[1].split("negative prompt:", 1)[0]
            self.assertNotIn("{{", positive)
            if folder == "background":
                for token in ("FIGURE_FRAME", "HAIR", "EYE", "SKIN"):
                    self.assertIn(tokens[token], positive)
                self.assertIn("Preserve the incoming clothing, if any", positive)
            else:
                self.assertIn("Preserve visible body proportions", positive)
                self.assertIn("Preserve the incoming clothing and accessories, if any", positive)
                self.assertNotIn(tokens["FIGURE_FRAME"], positive)

    def test_male_edit_pilots_distinguish_source_and_identity_frame(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        for slug in ("angelo", "auriel", "baracel", "elarion", "judiel",
                     "luzariel", "metrael", "urael", "verael", "vexiel", "zadriel"):
            base = pathlib.Path("data/art/_sets/angel-primes/male") / slug / "0_Edit"
            for folder, suffix in (("background", "background"),
                                   ("enhance", "enhance-basic")):
                path = base / folder / f"{slug}-edit-{suffix}.json"
                card = json.loads((root / path).read_text(encoding="utf-8"))
                identity = gp.load_identity(card["heroArt"])
                tokens = gp.tokens_for(identity, ["hair", "eyes", "skin"])
                with self.subTest(hero=slug, family=folder), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                positive = write.call_args.args[1].split("negative prompt:", 1)[0]
                self.assertNotIn("Bust:", positive)
                self.assertNotIn("{{", positive)
                if folder == "background":
                    self.assertNotIn(tokens["FIGURE_FRAME"], positive)
                    self.assertIn("Preserve the incoming clothing, if any", positive)
                else:
                    self.assertIn(tokens["FIGURE_FRAME"], positive)
                    self.assertIn("If clothing is present", positive)
                    if slug == "angelo":
                        for token in ("HAIR", "EYE", "SKIN"):
                            self.assertIn(tokens[token], positive)
                    else:
                        self.assertIn("Keep the incoming skin tone", positive)
                        self.assertIn("Keep the incoming hairstyle", positive)
                        self.assertIn("preserve expression and eye color", positive)
                        for token in ("HAIR", "EYE", "SKIN"):
                            self.assertNotIn(tokens[token], positive)

    def test_male_pose_auditions_preserve_source_physique_and_clothing(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        for slug in ("angelo", "auriel", "baracel", "elarion", "judiel",
                     "luzariel", "metrael", "urael", "verael", "vexiel", "zadriel"):
            base = pathlib.Path("data/art/_sets/angel-primes/male") / slug / "0_Edit/pose"
            for variant, cue in (("grounded", "both feet flat on the floor"),
                                 ("relaxed", "one hand resting naturally on the hip")):
                path = base / f"{slug}-edit-pose-{variant}-three-quarter.json"
                with self.subTest(hero=slug, variant=variant), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                positive = write.call_args.args[1].split("negative prompt:", 1)[0]
                self.assertIn(cue, positive)
                self.assertIn("keeping the source physique unchanged", positive)
                self.assertIn("Preserve the incoming clothing", positive)
                self.assertNotIn("Bust:", positive)
                self.assertNotIn("{{", positive)

    def test_male_character_edit_variants_resolve_their_frame(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        variants = (("background", "background-basic"), ("background", "background-enhance"),
                    ("cleanup", "cleanup"), ("cleanup", "cleanup-basic"),
                    ("cleanup", "cleanup-enhance"), ("enhance", "enhance-pose"),
                    ("full", "full"))
        for slug in ("angelo", "auriel", "baracel", "elarion", "judiel",
                     "luzariel", "metrael", "urael", "verael", "vexiel", "zadriel"):
            base = pathlib.Path("data/art/_sets/angel-primes/male") / slug / "0_Edit"
            for family, suffix in variants:
                path = base / family / f"{slug}-edit-{suffix}.json"
                card = json.loads((root / path).read_text(encoding="utf-8"))
                tokens = gp.tokens_for(gp.load_identity(card["heroArt"]), ["hair", "eyes", "skin"])
                with self.subTest(hero=slug, variant=suffix), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                positive = write.call_args.args[1].split("negative prompt:", 1)[0]
                self.assertIn(tokens["FIGURE_FRAME"], positive)
                self.assertNotIn("Bust:", positive)
                self.assertNotIn("{{", positive)
                if family == "cleanup":
                    self.assertIn("Slightly increase the tan", positive)
                    self.assertIn("jewelry", positive)
                if suffix == "enhance-pose":
                    self.assertIn("over the shoulder", positive)
                    self.assertIn("smirk", positive)
                if family == "full":
                    self.assertIn("Newly visible regions are synthesized", positive)
                    self.assertIn("Keep the existing outfit", positive)
                if suffix == "background-basic" and slug == "angelo":
                    for token in ("HAIR", "EYE", "SKIN"):
                        self.assertIn(tokens[token], positive)
                if suffix in ("background-basic", "enhance-pose") and slug != "angelo":
                    for token in ("HAIR", "EYE", "SKIN"):
                        self.assertNotIn(tokens[token], positive)

    def test_male_deluxe_and_outfit_variants_keep_explicit_selections(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        variants = (("background", "background-plus"), ("enhance", "enhance-plus"),
                    ("deluxe", "deluxe-reclining"), ("deluxe", "deluxe-resting"),
                    ("deluxe", "deluxe-seated"), ("deluxe", "deluxe-side-resting"),
                    ("background", "background-frame"))
        for slug in ("angelo", "auriel", "baracel", "elarion", "judiel",
                     "luzariel", "metrael", "urael", "verael", "vexiel", "zadriel"):
            base = pathlib.Path("data/art/_sets/angel-primes/male") / slug / "0_Edit"
            for family, suffix in variants:
                path = base / family / f"{slug}-edit-{suffix}.json"
                card = json.loads((root / path).read_text(encoding="utf-8"))
                tokens = gp.tokens_for(gp.load_identity(card["heroArt"]), [])
                with self.subTest(hero=slug, variant=suffix), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                positive = write.call_args.args[1].split("negative prompt:", 1)[0]
                self.assertIn(tokens["FIGURE_FRAME"], positive)
                self.assertNotIn("Bust:", positive)
                self.assertNotIn("{{", positive)
                if suffix.endswith("plus"):
                    self.assertIn("two-piece swimsuit in the original outfit's colors", positive)
                if family == "deluxe":
                    self.assertIn("jewelry", positive.lower())
                    self.assertNotIn("two-piece swimsuit", positive)
                if suffix in ("deluxe-reclining", "deluxe-seated"):
                    self.assertIn("high-heeled shoes", positive)
                if suffix == "background-frame":
                    self.assertIn("Preserve the incoming clothing, if any", positive)

    def test_denoise_hint_is_opt_in(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies")
        for path, legacy in (
            (base / "body/female-view-back.json", "~0.8-0.9"),
            (base / "hair/down/female-hair-beach-waves.json", "~0.7-0.8"),
            (base / "head/closeups/female-head-face-closeup.json", "~0.7-0.8"),
            (pathlib.Path("data/art/_sets/sovereign-females/female/4_Wardrobe/armor/wardrobe/female-armor-half-plate.json"), "~0.8-0.9"),
            (pathlib.Path("data/art/_sets/sovereign-females/female/4_Wardrobe/clothing/gowns/female-clothing-long-evening-gown.json"), "~0.8-0.9"),
            (pathlib.Path("data/art/_sets/sovereign-females/female/5_Scenes/glamour/female-scene-glamour.json"), "~0.8-0.9"),
            (pathlib.Path("data/art/_sets/sovereign-females/female/5_Scenes/signature/female-scene-signature.json"), "~0.8-0.9"),
            (pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies/motions/dynamic/female-motion-twirl-spin.json"), "~0.85-0.95"),
        ):
            card = json.loads((root / path).read_text(encoding="utf-8"))
            original_load = gp.load_json
            with self.subTest(path=path):
                rendered = []
                for hint in (None, "{{DENOISE}}"):
                    modified = dict(card)
                    if hint is not None:
                        modified["denoise_hint"] = hint

                    def load(source):
                        if source == root / path:
                            return modified
                        return original_load(source)

                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(gp, "load_json", side_effect=load), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(path)
                    rendered.append(write.call_args.args[1])
                self.assertIn(f"Denoise {legacy}.", rendered[0])
                self.assertEqual(rendered[0].replace(f"Denoise {legacy}.",
                                                    f"Denoise {card['denoise']}."), rendered[1])

    def test_studies_auditions_preserve_source_prompt_except_denoise(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies")
        auditions = sorted((root / base).rglob("*-denoise-audition.json"))
        self.assertEqual(len(auditions), 12)
        for absolute in auditions:
            path = absolute.relative_to(root)
            source = path.with_name(path.name.replace("-denoise-audition.json", ".json"))
            card = json.loads(absolute.read_text(encoding="utf-8"))
            rendered = []
            with self.subTest(path=path), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                for candidate in (source, path):
                    gp.generate(candidate)
                    rendered.append(write.call_args.args[1])
            legacy = {"pose": "~0.8-0.9", "motion": "~0.85-0.95"}.get(card["stage"], "~0.7-0.8")
            self.assertEqual(rendered[0].replace(f"Denoise {legacy}.",
                                                f"Denoise {card['denoise']}."), rendered[1])

    def test_studies_denoise_hint_rejects_invalid_input(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies/body/female-view-back.json")
        original = json.loads((root / path).read_text(encoding="utf-8"))
        original_load = gp.load_json
        for field, value in (("denoise", "not-a-range"), ("denoise", "~0.8-0.4"),
                             ("denoise", "~0.8-1.2"), ("denoise_hint", "unparseable"),
                             ("template", "data/art/_templates/heroes/1_Alpha/alpha-reference-human.txt")):
            card = dict(original, denoise_hint="{{DENOISE}}")
            card[field] = value

            def load(source):
                return card if source == root / path else original_load(source)

            with self.subTest(field=field, value=value), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(gp, "load_json", side_effect=load), \
                 self.assertRaisesRegex(SystemExit, "denoise_hint requires"):
                gp.generate(path)

    def test_later_phase_denoise_auditions_only_change_the_header(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/sovereign-females/female")
        for folder, source, audition in (
            ("4_Wardrobe/armor/wardrobe", "female-armor-half-plate-routing-audition", "female-armor-half-plate-denoise-audition"),
            ("4_Wardrobe/clothing/gowns", "female-clothing-long-evening-gown-routing-audition", "female-clothing-long-evening-gown-denoise-audition"),
            ("5_Scenes/glamour", "female-routing-audition-scene-glamour", "female-denoise-audition-scene-glamour"),
            ("5_Scenes/signature", "female-routing-audition-scene-signature", "female-denoise-audition-scene-signature"),
            ("2_Studies/motions/dynamic", "female-motion-twirl-spin-routing-audition", "female-motion-twirl-spin-denoise-audition"),
            ("2_Studies/motions/standing", "female-motion-hand-on-hip-power-routing-audition", "female-motion-hand-on-hip-power-denoise-audition"),
            ("2_Studies/motions/walking", "female-motion-catwalk-confident-routing-audition", "female-motion-catwalk-confident-denoise-audition"),
        ):
            source_path = base / folder / f"{source}.json"
            audition_path = base / folder / f"{audition}.json"
            card = json.loads((root / audition_path).read_text(encoding="utf-8"))
            rendered = []
            with self.subTest(audition=audition), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                for path in (source_path, audition_path):
                    gp.generate(path)
                    rendered.append(write.call_args.args[1])
            legacy = "~0.85-0.95" if card["stage"] == "motion" else "~0.8-0.9"
            self.assertEqual(rendered[0].replace(f"Denoise {legacy}.",
                                                f"Denoise {card['denoise']}."), rendered[1])

    def test_directional_studies_preserve_identity_without_forcing_front_gaze(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies/body")
        for variant, view in (
            ("back", "head facing straight away"),
            ("profile-left", "head in clean profile looking ahead toward frame-left"),
        ):
            path = folder / f"female-view-{variant}-visibility-audition.json"
            with self.subTest(variant=variant), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
            positive, negative = prompt.split("negative prompt:", 1)
            self.assertIn(view, positive)
            self.assertIn("Keep the exact outfit from the incoming image", positive)
            self.assertIn("strict fidelity to the incoming image", positive)
            self.assertNotIn("Eyes:", positive)
            self.assertNotIn("Expression:", positive)
            self.assertNotIn("eyes warm and engaged with the camera", positive)
            self.assertNotIn("{{", prompt)
            self.assertIn("changed outfit", negative)

    def test_hair_preservation_auditions_do_not_require_an_a_pose(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies/hair")
        for variant in ("down/female-hair-beach-waves", "updo/female-hair-high-bun"):
            path = folder / f"{variant}-preserve-audition.json"
            with self.subTest(variant=variant), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
            self.assertIn("Incoming image: a selected reference image", prompt)
            self.assertNotIn("A-pose", prompt)
            self.assertIn("Preserve the incoming pose and framing.", prompt)
            self.assertIn("Preserve the incoming setting and lighting.", prompt)
            self.assertNotIn("{{", prompt)

    def test_named_prime_audition_selects_character_identity_and_order(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/angel-primes/female/angelica/1_Alpha/1_Prime/angelica-alpha-prime-ordered-audition.json")
        card = json.loads((root / path).read_text(encoding="utf-8"))
        tokens = gp.tokens_for(gp.load_identity(card["heroArt"]), ["hair", "eyes", "skin"])
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive = write.call_args.args[1].split("negative prompt:", 1)[0]
        labels = ("Pose:", "Background:", "Lighting:", "Camera:", "Edit the incoming image:",
                  "Result:", "Hair:", "Bust:", "Eyes:", "Skin:", "Body:", "Likeness:", "Wearing:")
        self.assertEqual([positive.index(label) for label in labels],
                         sorted(positive.index(label) for label in labels))
        for token in ("HAIR", "EYE", "SKIN", "FIGURE_FRAME"):
            self.assertIn(tokens[token], positive)
        self.assertIn("color-blocked panels", positive)
        self.assertIn("eyes to camera", positive)
        self.assertIn("wide environmental film still", positive)
        self.assertIn("eyes matched, level and symmetrical, wide open", positive)
        self.assertNotIn("{{", positive)

    def test_adaptive_prime_audition_uses_frame_without_forcing_palette(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes/female")
        for slug in ("azaline", "camaris", "gavrielle", "haniya", "nyxene",
                     "ravaelle", "remiah", "sammara", "sandalyn", "seraphine"):
            path = base / slug / "1_Alpha/1_Prime" / f"{slug}-alpha-prime-ordered-audition.json"
            card = json.loads((root / path).read_text(encoding="utf-8"))
            identity = gp.load_identity(card["heroArt"])
            tokens = gp.tokens_for(identity, ["hair", "eyes", "skin"])
            with self.subTest(hero=slug), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
            positive = prompt.split("negative prompt:", 1)[0]
            self.assertIn(tokens["FIGURE_FRAME"], positive)
            self.assertIn("Keep the incoming hair color unchanged", positive)
            self.assertIn("incoming skin tone", positive)
            self.assertIn("eye color", positive)
            self.assertIn("Wear the hair down", positive)
            self.assertIn("wide environmental film still", positive)
            self.assertIn("eyes matched, level and symmetrical, wide open", positive)
            self.assertNotIn("Keep the incoming hairstyle", positive)
            for token in ("HAIR", "EYE", "SKIN"):
                self.assertNotIn(tokens[token], positive)
            negative = prompt.split("negative prompt:", 1)[1]
            self.assertIn("changed eye color", negative)
            self.assertIn("changed skin tone", negative)
            for key in ("eyeColorNegatives", "skinColorNegatives"):
                for excluded in identity["art"]["palette"].get(key, []):
                    self.assertNotIn(excluded.lower(), negative.lower())
            self.assertNotIn("{{", prompt)

    def test_sister_ordered_prime_selects_identity_appearance_and_frame(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/drakn-sisters")
        for slug in ("draknara", "draknava", "drakness", "drakneta", "draknira",
                     "draknisa", "drakniss", "drakniya", "draknora", "draknoxa"):
            path = base / slug / "1_Alpha/1_Prime" / f"{slug}-alpha-prime-ordered-audition.json"
            card = json.loads((root / path).read_text(encoding="utf-8"))
            tokens = gp.tokens_for(gp.load_identity(card["heroArt"]), ["hair", "eyes", "skin"])
            with self.subTest(hero=slug), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive = write.call_args.args[1].split("negative prompt:", 1)[0]
            for token in ("HAIR", "EYE", "SKIN", "FIGURE_FRAME"):
                self.assertIn(tokens[token], positive)
            self.assertIn("two-piece swimsuit", positive)
            self.assertIn("eyes to camera", positive)
            self.assertIn("wide environmental film still", positive)
            self.assertIn("eyes matched, level and symmetrical, wide open", positive)
            self.assertNotIn("{{", positive)

    def test_male_ordered_prime_selects_identity_frame_and_source_policy(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/angel-primes/male")
        for slug in ("angelo", "auriel", "baracel", "elarion", "judiel",
                     "luzariel", "metrael", "urael", "verael", "vexiel", "zadriel"):
            path = base / slug / "1_Alpha/1_Prime" / f"{slug}-alpha-prime-ordered-audition.json"
            card = json.loads((root / path).read_text(encoding="utf-8"))
            identity = gp.load_identity(card["heroArt"])
            tokens = gp.tokens_for(identity, ["hair", "eyes", "skin"])
            with self.subTest(hero=slug), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
            positive, negative = prompt.split("negative prompt:", 1)
            self.assertIn(tokens["FIGURE_FRAME"], positive)
            self.assertIn(tokens["HAIRSTYLE"], positive)
            self.assertIn("wide environmental film still", positive)
            self.assertIn("eyes matched, level and symmetrical, wide open", positive)
            self.assertNotIn("Bust:", positive)
            self.assertNotIn("{{", prompt)
            self.assertNotIn("feet Replace", positive)
            self.assertNotIn("unchanged.;", positive)
            if slug == "angelo":
                for token in ("HAIR", "EYE", "SKIN"):
                    self.assertIn(tokens[token], positive)
                self.assertIn("pastel colour-blocked side panels", positive)
            else:
                self.assertIn("Keep the incoming hair color unchanged", positive)
                self.assertIn("changed eye color", negative)
                self.assertIn("changed skin tone", negative)
                for token in ("HAIR", "EYE", "SKIN"):
                    self.assertNotIn(tokens[token], positive)
                for key in ("eyeColorNegatives", "skinColorNegatives"):
                    for excluded in identity["art"]["palette"].get(key, []):
                        self.assertNotIn(excluded.lower(), negative.lower())

    def test_later_phase_routing_auditions_preserve_original_prompts(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/sovereign-females/female")
        paths = []
        for phase in ("3_Layers", "4_Wardrobe", "5_Scenes", "2_Studies/motions"):
            paths.extend((root / base / phase).rglob("*.json"))
        cards = {json.loads(p.read_text(encoding="utf-8"))["output"]: p.relative_to(root)
                 for p in paths}
        auditions = [p for output, p in cards.items() if output.endswith("_Routing_Audition.txt")]
        self.assertEqual(len(auditions), 9)
        for path in auditions:
            card = json.loads((root / path).read_text(encoding="utf-8"))
            original_output = card["output"].replace("_Routing_Audition.txt", ".txt")
            source = cards[original_output]
            with self.subTest(path=path), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(source)
                expected = write.call_args.args[1]
                gp.generate(path)
                self.assertEqual(expected, write.call_args.args[1])

    def test_sister_edit_suites_use_character_identity_only_when_selected(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        identities = sorted((root / "data/art/heroes/drakn-sisters").glob("*-thorne.json"))
        self.assertEqual(len(identities), 10)
        required = (
            "background", "background-basic", "background-bust", "background-enhance", "background-plus",
            "cleanup", "cleanup-basic", "cleanup-enhance", "deluxe-reclining", "deluxe-resting",
            "deluxe-seated", "deluxe-side-resting", "enhance-basic", "enhance-plus", "enhance-pose",
            "full", "pose-grounded-three-quarter", "pose-relaxed-three-quarter",
        )
        for identity_path in identities:
            slug = identity_path.stem.removesuffix("-thorne")
            hero_art = f"data/art/heroes/drakn-sisters/{slug}-thorne.json"
            cards = sorted((root / f"data/art/_sets/drakn-sisters/{slug}/0_Edit").glob("*/*.json"))
            self.assertTrue({f"{slug}-edit-{name}.json" for name in required}
                            .issubset({path.name for path in cards}), slug)
            tokens = gp.tokens_for(gp.load_identity(hero_art), ["hair", "eyes", "skin"])
            for path in cards:
                card = json.loads(path.read_text(encoding="utf-8"))
                components = card["components"]
                with self.subTest(hero=slug, card=path.name), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path.relative_to(root))
                positive = write.call_args.args[1].split("negative prompt:", 1)[0]
                self.assertNotIn("{{", positive)
                self.assertEqual(card["heroArt"], hero_art)
                if components.get("body") == "{{FIGURE_FRAME}}":
                    self.assertIn(tokens["FIGURE_FRAME"], positive)
                if card.get("keyDetails") == ["hair", "eyes", "skin"]:
                    for token in ("HAIR", "EYE", "SKIN"):
                        self.assertIn(tokens[token], positive)
                if components.get("body") == "data/art/edits/policies/body-preserve.json":
                    self.assertIn("Preserve visible body proportions", positive)
                    self.assertNotIn(tokens["FIGURE_FRAME"], positive)
                if card["artId"].endswith("-edit-enhance-pose"):
                    self.assertIn("Both eyes matched and symmetrical", positive)

    def test_enhance_basic_continues_incoming_clothing_when_extending(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        cards = (
            pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/enhance/female-edit-enhance-basic.json"),
            pathlib.Path("data/art/_sets/angel-primes/female/angelica/0_Edit/enhance/angelica-edit-enhance-basic.json"),
        )
        for path in cards:
            with self.subTest(card=path), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn("Wearing: If clothing is present", positive)
            self.assertIn("continuing it naturally into any newly visible areas", positive)
            self.assertIn("free of purses, accessories and jewelry", positive)
            self.assertIn("changed clothing", negative)
            self.assertNotIn("Do not add clothing", positive)

    def test_generic_backgrounds_preserve_clothing_while_clearing_accessories(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/background")
        for variant in ("", "-basic", "-bust"):
            path = folder / f"female-edit-background{variant}.json"
            with self.subTest(variant=variant), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn("Wearing: Preserve the incoming clothing, if any", positive)
            self.assertIn("Do not add clothing.", positive)
            self.assertIn("free of purses, accessories and jewelry", positive)
            self.assertNotIn("preserve the incoming clothing and accessories", positive.lower())
            self.assertIn("changed clothing", negative)

    def test_ordered_reference_prompts_keep_positive_anchors_without_duplicate_negatives(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/0_Edit"
        cards = sorted((folder / "pose").glob("*.json")) + sorted((folder / "deluxe").glob("*.json"))
        for card in cards:
            with self.subTest(card=card.name), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(card)
                positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                expected_count = 1 if card.parent.name == "pose" else 2
                self.assertEqual(positive.count("Preserve the same person's recognizable face"), expected_count)
                terms = [term.strip().lower().strip(".") for term in negative.replace("\n", " ").split(",") if term.strip()]
                self.assertEqual(len(terms), len(set(terms)))
                self.assertIn("changed identity", terms)

    def test_alpha_reference_prompts_do_not_repeat_component_negatives(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/1_Alpha"
        cards = [path for path in folder.rglob("*.json")
                 if json.loads(path.read_text(encoding="utf-8"))["template"].endswith("/alpha-reference-human.txt")]
        self.assertIn(folder / "1_Prime/female-alpha-prime.json", cards)
        self.assertIn(folder / "2_Bare/female-alpha-bare-covered-figure-audition.json", cards)
        for card in cards:
            with self.subTest(card=card.name), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(card)
                positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                terms = [term.strip().lower().strip(".") for term in negative.replace("\n", " ").split(",") if term.strip()]
                self.assertEqual(len(terms), len(set(terms)))
                self.assertIn("Likeness:", positive)

    def test_source_inspired_outfits_select_natural_makeup_and_hair(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/1_Alpha/4_Outfits"
        cards = [path for path in folder.rglob("*.json")
                 if path.name not in ("female-alpha-outfit-grounded.json", "female-alpha-outfit-relaxed.json")]
        self.assertEqual(len(cards), 13)
        for card in cards:
            with self.subTest(card=card.name), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(card)
                positive = write.call_args.args[1].split("negative prompt:", 1)[0]
                self.assertIn("Makeup: soft, natural makeup and natural-looking lips.", positive)
                self.assertIn("Hair: Wear the hair down, retaining its natural texture and keeping the face clear.", positive)
                self.assertIn("Keep the incoming hair length.", positive)
                self.assertIn("Gaze: eyes to camera.", positive)

    def test_source_preserving_outfits_do_not_replace_expression(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/1_Alpha/4_Outfits"
        for name in ("female-alpha-outfit-grounded.json", "female-alpha-outfit-relaxed.json"):
            with self.subTest(card=name), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(folder / name)
                positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                self.assertIn("Expression: preserve the incoming facial expression.", positive)
                self.assertNotIn("Gaze:", positive)
                self.assertNotIn("replace the source photo's expression", positive)
                self.assertNotIn("wide smile", negative)

    def test_grey_backdrop_can_separate_lighting_without_changing_existing_bundle(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        bundle = gp.load_piece(root / "data/art/backgrounds/studio/grey-even.json")
        self.assertEqual(
            bundle["description"],
            "a plain neutral light-grey seamless studio backdrop with even, soft, "
            "neutral frontal studio lighting - a flat, clean key light",
        )
        self.assertEqual(bundle["negatives"], ["colored studio backdrop", "busy background"])
        self.assertEqual(
            bundle["compatibleStages"],
            ["edit", "alpha", "pose", "head", "hair", "motion", "armor", "clothing"],
        )

        source = root / "data/art/_sets/sovereign-females/female/0_Edit/cleanup/female-edit-cleanup-basic.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        card["components"]["background"] = "data/art/backgrounds/studio/light-grey-seamless.json"
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("Background: a plain neutral light-grey seamless studio backdrop", positive)
        self.assertEqual(positive.lower().count("even, soft, neutral frontal studio lighting"), 1)
        self.assertIn("colored studio backdrop", negative)
        self.assertIn("busy background", negative)

    def test_prime_can_resolve_shared_photography_and_reference_components(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/1_Alpha/4_Outfits/female-alpha-outfit-relaxed.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        card["components"].update({
            "background": "data/art/reference/background/preserve-scenery.json",
            "lighting": "data/art/studio/lighting/neutral-frontal.json",
            "photo_style": "data/art/studio/photography/beauty-85mm.json",
            "camera": "data/art/studio/framing/pullback-full.json",
        })
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            template = pathlib.Path(tmp) / "template.txt"
            template.write_text("{{BACKGROUND}}\n{{LIGHTING}}\n{{PHOTO_STYLE}}\n{{CAMERA}}\n", encoding="utf-8")
            card["template"] = str(template)
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
        self.assertIn("original scenery", prompt)
        self.assertIn("neutral frontal studio lighting", prompt)
        self.assertIn("85mm lens", prompt)
        self.assertIn("Pull the camera back", prompt)

    def test_female_prime_renders_source_order_and_configured_identity(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/sovereign-females/female/1_Alpha/1_Prime/female-alpha-prime.json")
        card = json.loads((root / path).read_text(encoding="utf-8"))
        identity = gp.load_identity(card["heroArt"])
        identity["art"]["palette"]["hairColor"] = "IDENTITY_HAIR"
        identity["art"]["palette"]["eyeColorGlamour"] = "IDENTITY_EYES"
        identity["art"]["palette"]["skinTone"] = "IDENTITY_SKIN"
        identity["art"]["palette"]["primaryColor"] = "IDENTITY_WHITE"
        identity["art"]["palette"]["accentColors"] = ["IDENTITY_GOLD"]
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(gp, "load_identity", return_value=identity), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        prompt = write.call_args.args[1]
        positive, negative = prompt.split("negative prompt:", 1)
        labels = ("Pose:", "Background:", "Lighting:", "Camera:",
                  "Edit the incoming image:", "Result:", "Critical details",
                  "Bust:", "Body:", "Likeness:", "Wearing:", "Footwear:", "Hair:",
                  "Makeup:", "Eyes:", "Expression:")
        positions = [positive.rindex(label) if label in ("Hair:", "Eyes:")
                     else positive.index(label) for label in labels]
        self.assertEqual(positions, sorted(positions))
        critical = positive.index("Critical details")
        self.assertLess(positive.index("Hair:", critical), positive.index("Bust:", critical))
        self.assertLess(positive.index("Bust:", critical), positive.index("Eyes:", critical))
        for marker in ("IDENTITY_HAIR", "IDENTITY_EYES", "IDENTITY_SKIN",
                       "IDENTITY_WHITE", "IDENTITY_GOLD"):
            self.assertIn(marker.lower(), positive.lower())
        self.assertIn("standing a-pose", positive.lower())
        self.assertIn("head facing the camera squarely", positive.lower())
        self.assertIn("two-piece swimsuit", positive.lower())
        self.assertIn("soft rose, sky blue, mint and lilac", positive.lower())
        self.assertIn("feather emblem", positive.lower())
        self.assertIn("replace the incoming outfit", positive.lower())
        self.assertIn("bare feet", positive.lower())
        self.assertIn("Gaze: eyes to camera.", positive)
        self.assertIn("natural lip balm", positive.lower())
        self.assertIn("source outfit remnants", negative.lower())
        self.assertNotIn("changed clothing", negative.lower())
        self.assertNotIn("{{", prompt)
        self.assertEqual(card["output"], "prompts/sovereign-females/Female/1_Alpha/1_Prime/Female_Alpha_1_Prime_Audition.txt")

    def test_cleanup_variants_render_ordered_supported_source_instructions(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/cleanup")
        for variant in ("basic", "standard", "enhance"):
            card = folder / f"female-edit-cleanup-{variant}.json"
            if variant == "standard":
                card = folder / "female-edit-cleanup.json"
            with self.subTest(variant=variant):
                with mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(card)
                prompt = write.call_args.args[1]
                positive, negative = prompt.split("negative prompt:", 1)
                labels = ["Pose:", "Background:", "Lighting:", "Professional",
                          "Edit the incoming image:", "Result:", "Critical details",
                          "Bust:", "Body:", "Skin:", "Likeness:", "Wearing:"]
                positions = [positive.index(label) for label in labels]
                self.assertEqual(positions, sorted(positions))
                self.assertIn("Denoise ~0.9.", prompt)
                self.assertIn("retain existing jewelry", positive.lower())
                self.assertIn("non-jewelry accessories", positive.lower())
                self.assertIn("slightly increase the tan", positive.lower())
                self.assertIn("preserve expression and eye color", positive.lower())
                self.assertIn("incoming hairstyle", positive.lower())
                self.assertNotIn("fully clothed", positive.lower())
                self.assertNotIn("changed lighting direction", negative)
                self.assertNotIn("changed skin tone", negative)
                self.assertNotIn("{{", prompt)
                if variant == "standard":
                    self.assertEqual(positive.count("Keep the existing outfit"), 1)
                elif variant == "basic":
                    self.assertEqual(positive.count("Keep the existing outfit"), 2)
                if variant == "enhance":
                    self.assertLess(positive.index("Camera:"), positive.index("Edit the incoming image:"))
                    self.assertIn("feet", positive.lower())
                else:
                    self.assertNotIn("Camera:", positive)

    def test_background_basic_uses_source_order_and_clears_jewelry(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        card = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/background/female-edit-background-basic.json")
        assembly = json.loads((root / card).read_text(encoding="utf-8"))
        self.assertEqual(gp.art_layout.family(assembly, "angel-primes", root), ["background"])
        hero = gp.load_identity("data/art/heroes/sovereign-females/female.json")
        hero["art"]["physique"]["bust"] = "IDENTITY_DETAIL_MUST_NOT_LEAK"
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(gp, "load_identity", return_value=hero), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(card)
        prompt = write.call_args.args[1]
        positive, negative = prompt.split("negative prompt:", 1)
        labels = ("Pose:", "Background:", "Lighting:", "Professional",
                  "Edit the incoming image:", "Result:", "Critical details:",
                  "Body:", "Likeness:")
        positions = [positive.index(label) for label in labels]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Denoise ~0.9.", positive)
        self.assertIn("light-grey seamless studio backdrop", positive)
        self.assertEqual(positive.lower().count("neutral frontal studio lighting"), 1)
        self.assertIn("adapt the hands", positive.lower())
        self.assertIn("remove jewelry", positive.lower())
        self.assertIn("extend the selected background", positive.lower())
        self.assertIn("face, expression and makeup", positive.lower())
        self.assertNotIn("retain existing jewelry", positive.lower())
        self.assertIn("Wearing: Preserve the incoming clothing, if any", positive)
        self.assertNotIn("Skin:", positive)
        self.assertNotIn("IDENTITY_DETAIL_MUST_NOT_LEAK", prompt)
        self.assertNotIn("changed background", negative)
        self.assertNotIn("changed pose", negative)
        self.assertNotIn("{{", prompt)

    def test_optional_background_sections_preserve_cleanup_prompts(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/0_Edit/cleanup"
        template = root / "data/art/_templates/heroes/0_Edit/edit-cleanup-human.txt"
        previous = template.read_text(encoding="utf-8").replace(
            "?Skin: {{SKIN_EDIT}}", "Skin: {{SKIN_EDIT}}"
        ).replace("?{{ORDERED_KEY_BLOCK}}\n", "Critical details:\n").replace(
            "?Body: {{BODY}}", "Body: {{BODY}}"
        ).replace("?Hair: {{HAIR_POLICY}}", "Hair: {{HAIR_POLICY}}").replace(
            "?{{FACE_POLICY}}\n", ""
        ).replace("?{{FACE_POLICY_NEG}},\n", "").replace(
            "?Eyes: {{EYE_DETAIL}}\n", ""
        ).replace("?Gaze: {{GAZE}}\n", "").replace(
            "?Expression: {{EXPRESSION}}\n", "").replace(
            "?{{EYE_DETAIL_NEG}},\n", ""
        ).replace("?{{GAZE_NEG}},\n", "").replace("?{{EXPRESSION_NEG}},\n", "")
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            old_template = pathlib.Path(tmp) / "previous-template.txt"
            old_template.write_text(previous, encoding="utf-8")
            for path in sorted(folder.glob("*.json")):
                card = json.loads(path.read_text(encoding="utf-8"))
                card["template"] = str(old_template)
                old_card = pathlib.Path(tmp) / path.name
                old_card.write_text(json.dumps(card), encoding="utf-8")
                rendered = []
                for source in (path, old_card):
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(source)
                    rendered.append(write.call_args.args[1])
                with self.subTest(card=path.name):
                    self.assertEqual(rendered[0], rendered[1])

    def test_optional_footwear_does_not_change_other_edit_prompts(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/0_Edit"
        template = root / "data/art/_templates/heroes/0_Edit/edit-cleanup-human.txt"
        previous = template.read_text(encoding="utf-8").replace(
            "?Footwear: {{LEGS_FEET}}\n", ""
        ).replace("?{{LEGS_FEET_NEG}},\n", "")
        cards = [path for path in folder.rglob("*.json")
                 if path.parent.name not in ("deluxe", "pose")
                 and "legs_feet" not in json.loads(path.read_text(encoding="utf-8")).get("components", {})]
        self.assertTrue(cards)
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            old_template = pathlib.Path(tmp) / "previous-template.txt"
            old_template.write_text(previous, encoding="utf-8")
            for path in cards:
                card = json.loads(path.read_text(encoding="utf-8"))
                card["template"] = str(old_template)
                old_card = pathlib.Path(tmp) / path.name
                old_card.write_text(json.dumps(card), encoding="utf-8")
                rendered = []
                for source in (path, old_card):
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(source)
                    rendered.append(write.call_args.args[1])
                with self.subTest(card=path.name):
                    self.assert_only_duplicate_negatives_removed(rendered[0], rendered[1])

    def test_background_variants_have_independent_source_intent(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/background")
        for variant in ("standard", "basic", "enhance", "plus"):
            name = "female-edit-background.json" if variant == "standard" else f"female-edit-background-{variant}.json"
            path = folder / name
            with self.subTest(variant=variant):
                assembly = json.loads((root / path).read_text(encoding="utf-8"))
                self.assertEqual(gp.art_layout.family(assembly, "angel-primes", root), ["background"])
                with mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                prompt = write.call_args.args[1]
                positive, negative = prompt.split("negative prompt:", 1)
                self.assertIn("light-grey seamless studio backdrop", positive)
                self.assertIn("jewelry", positive.lower())
                self.assertNotIn("changed background", negative)
                self.assertNotIn("{{", prompt)
                self.assertEqual("Critical details:" in positive, variant != "standard")
                self.assertEqual("Bust:" in positive, variant != "standard")
                self.assertEqual("Camera:" in positive, variant == "enhance")
                self.assertIn("Wearing:", positive)
                if variant == "plus":
                    self.assertIn("original outfit's colors", positive)
                    self.assertIn("source outfit remnants", negative)

    def test_background_bust_selects_figure_detail_without_changing_other_edits(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/background")
        for variant in ("bust", "basic", "standard"):
            name = "female-edit-background.json" if variant == "standard" else f"female-edit-background-{variant}.json"
            path = folder / name
            card = json.loads((root / path).read_text(encoding="utf-8"))
            identity = gp.load_identity(card["heroArt"])
            identity["art"]["physique"]["bust"] = "IDENTITY_DETAIL_MUST_NOT_LEAK"
            with self.subTest(variant=variant), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(gp, "load_identity", return_value=identity), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
            positive, negative = prompt.split("negative prompt:", 1)
            self.assertEqual(gp.art_layout.family(card, "angel-primes", root), ["background"])
            self.assertEqual("Bust:" in positive, variant != "standard")
            self.assertNotIn("IDENTITY_DETAIL_MUST_NOT_LEAK", prompt)
            self.assertNotIn("{{", prompt)
            if variant == "bust":
                self.assertIn("naturally rounded bust", positive)
                self.assertLess(positive.index("Critical details:"), positive.index("Bust:"))
                self.assertLess(positive.index("Bust:"), positive.index("Likeness:"))
                self.assertNotIn("Body:", positive)
                self.assertIn("Wearing: Preserve the incoming clothing, if any", positive)
                self.assertIn("remove jewelry", positive.lower())
                self.assertNotIn("changed background", negative)

    def test_edit_can_select_reusable_figure_profiles_independently(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/0_Edit/background/female-edit-background-basic.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for name, expected, excluded in (
                ("athletic-balanced", "balanced athletic frame", "softly curved frame"),
                ("soft-curved", "softly curved frame", "balanced athletic frame"),
                ("pear-balanced", "narrower shoulders", "runner's frame"),
                ("straight-athletic", "straight athletic frame", "narrower shoulders"),
                ("runner-lean", "runner's frame", "straight athletic frame"),
                ("natural-soft", "softly rounded abdomen", "runner's frame"),
            ):
                with self.subTest(profile=name):
                    card["components"]["body"] = f"data/art/studio/figure/{name}.json"
                    path.write_text(json.dumps(card), encoding="utf-8")
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(path)
                    positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
                    self.assertIn(expected, positive)
                    self.assertNotIn(excluded, positive)
                    self.assertIn("wearing: preserve the incoming clothing, if any", positive)

    def test_alpha_can_select_bust_detail_without_replacing_body_or_outfit(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/1_Alpha/1_Prime/female-alpha-prime.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for name, expected, excluded in (
                ("small-bust-natural", "small bust", "moderate bust"),
                ("moderate-bust-natural", "moderate bust", "small bust"),
            ):
                with self.subTest(detail=name):
                    card["components"]["bust"] = f"data/art/studio/figure/{name}.json"
                    path.write_text(json.dumps(card), encoding="utf-8")
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(path)
                    positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
                    self.assertIn(expected, positive)
                    self.assertNotIn(excluded, positive)
                    self.assertIn("body:", positive)
                    self.assertIn("wearing:", positive)

    def test_selected_bust_detail_negatives_follow_the_component(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/1_Alpha/1_Prime/female-alpha-prime.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            piece = pathlib.Path(tmp) / "figure.json"
            piece.write_text(json.dumps({
                "id": "test-figure", "kind": "figure", "name": "Test figure",
                "compatibleStages": ["alpha"], "description": "A selected figure detail.",
                "negatives": ["incompatible figure detail"],
            }), encoding="utf-8")
            card["components"]["bust"] = str(piece)
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn("A selected figure detail", positive)
            self.assertIn("incompatible figure detail", negative)

    def test_covered_alpha_figure_audition_does_not_replace_bare_chain(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/sovereign-females/female/1_Alpha/2_Bare/female-alpha-bare-covered-figure-audition.json")
        card = json.loads((root / path).read_text(encoding="utf-8"))
        family = gp.art_layout.family(card, "angel-primes", root)
        self.assertEqual(gp.art_layout.phase_path("alpha", family), ["1_Alpha", "2_Bare"])
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("one-piece swimsuit", positive)
        self.assertIn("Standing A-pose", positive)
        self.assertIn("strict fidelity to the reference person's facial features", positive.lower())
        self.assertNotIn("remove all clothing", positive.lower())
        self.assertNotIn("{{", positive + negative)

    def test_scene_can_select_new_textile_garments(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/5_Scenes/signature/female-scene-signature.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for name, cue in (("structured-wool-blazer", "wool blazer"),
                              ("chunky-mohair-sweater", "mohair sweater"),
                              ("oversized-poplin-shirt", "poplin button-down shirt"),
                              ("distressed-denim-jacket", "denim jacket")):
                with self.subTest(garment=name):
                    card["components"]["wearing"] = f"data/art/wardrobe/clothing/tops/{name}.json"
                    path.write_text(json.dumps(card), encoding="utf-8")
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(path)
                    positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
                    self.assertIn(cue, positive)
                    self.assertNotIn("{{", positive)

    def test_edit_and_alpha_can_select_skin_finish_without_recoloring(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        sources = (
            root / "data/art/_sets/sovereign-females/female/0_Edit/full/female-edit-full.json",
            root / "data/art/_sets/sovereign-females/female/1_Alpha/1_Prime/female-alpha-prime.json",
        )
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for source in sources:
                card = json.loads(source.read_text(encoding="utf-8"))
                for name, cue in (("natural-texture", "including visible pores"),
                                  ("soft-matte", "soft matte finish"),
                                  ("subtle-dew", "subtle dewy highlight")):
                    with self.subTest(source=source.name, finish=name):
                        card["components"]["skin_edit"] = f"data/art/reference/appearance/skin-finish-{name}.json"
                        path.write_text(json.dumps(card), encoding="utf-8")
                        with mock.patch.object(gp, "ROOT", root), \
                             mock.patch.object(pathlib.Path, "mkdir"), \
                             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                             mock.patch("builtins.print"):
                            gp.generate(path)
                        positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
                        self.assertIn(cue, positive)
                        self.assertIn("keep the selected skin tone and natural texture", positive)
                        self.assertNotIn("{{", positive)

    def test_scene_can_select_environmental_effects_independently(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/5_Scenes/signature/female-scene-signature.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for name, cue in (("gentle-breeze", "a gentle breeze"),
                              ("dust-in-sunbeams", "fine dust motes"),
                              ("fine-water-droplets", "fine water droplets"),
                              ("window-blind-shadows", "angled bands of shadow")):
                with self.subTest(effect=name):
                    card["components"]["effects"] = f"data/art/wardrobe/effects/ambient/{name}.json"
                    path.write_text(json.dumps(card), encoding="utf-8")
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(path)
                    positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
                    self.assertIn(cue, positive)
                    self.assertNotIn("soft ambient glow", positive)
                    self.assertNotIn("{{", positive)

    def test_alpha_can_select_expression_independently_of_gaze(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/1_Alpha/1_Prime/female-alpha-prime.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for name, cue in (("thoughtful-composed", "thoughtful, composed expression"),
                              ("soft-melancholy", "subtle melancholy")):
                with self.subTest(expression=name):
                    card["components"]["expression"] = f"data/art/motion/expressions/composed/{name}.json"
                    path.write_text(json.dumps(card), encoding="utf-8")
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(path)
                    positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
                    self.assertIn(cue, positive)
                    self.assertIn("gaze: eyes to camera", positive)
                    self.assertNotIn("soft closed-mouth smile", positive)

    def test_head_names_keep_root_and_other_studies_keep_families(self):
        for art_id in ("female-head", "female-x-head", "female-head-denoise-audition", "female-denoise-audition-x-head"):
            with self.subTest(art_id=art_id):
                self.assertEqual(gp.art_layout.family({"stage": "head", "artId": art_id}, "sovereign-females"), [])
        self.assertEqual(gp.art_layout.family({"stage": "head", "artId": "female-head-face-closeup"}, "sovereign-females"), ["closeups"])
        self.assertEqual(gp.art_layout.family({"stage": "head", "artId": "female-head-profile-left",
                                               "components": {"view": "profile"}}, "sovereign-females"), ["views"])

    def test_layer_preservation_auditions_replace_only_selected_outfit(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/sovereign-females/female/3_Layers")
        for folder, slug, selected in (
            ("bikini", "two-piece", "two-piece swimsuit"),
            ("one-piece", "one-piece", "one-piece swimsuit"),
        ):
            path = base / folder / f"female-layer-{slug}-preserve-audition.json"
            card = json.loads((root / path).read_text(encoding="utf-8"))
            family = gp.art_layout.family(card, "angel-primes", root)
            self.assertEqual(gp.art_layout.phase_path("poses", family), ["3_Layers", folder])
            with self.subTest(slug=slug), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn(selected, positive)
            self.assertIn("Preserve the incoming pose", positive)
            self.assertIn("Preserve the incoming setting and lighting", positive)
            self.assertIn("recognizable face, body proportions, hair, eye and skin colors", positive)
            self.assertIn("source outfit remnants", negative)
            self.assertNotIn("replace the source photo's hairstyle", positive)
            self.assertNotIn("{{", positive + negative)

    def test_hair_study_can_select_natural_afro_without_changing_color(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/2_Studies/hair/down/female-hair-beach-waves.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        card["component"] = "data/art/races/human/cosmetics/hair/down/natural-afro.json"
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
        positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
        self.assertIn("natural afro with defined coils", positive)
        self.assertIn("keep the hair colour and highlights", positive)
        self.assertIn("maintain existing outfit", positive)

    def test_profile_head_audition_does_not_require_frontal_eyes(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies/head/views/female-head-profile-left-visibility-audition.json")
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        prompt = write.call_args.args[1]
        positive = prompt.split("negative prompt:", 1)[0].lower()
        self.assertIn("clean side profile", positive)
        self.assertIn("eyes looking ahead toward frame-left", positive)
        self.assertIn("preserve the incoming expression and outfit", positive)
        self.assertNotIn("both eyes matched", positive)
        self.assertNotIn("engaged with the camera", positive)
        self.assertNotIn("{{", prompt)
        self.assertIn("denoise ~0.4-0.6", positive)

    def test_remaining_directional_studies_select_views_and_preserve_expression(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies")
        for card, expected in (
            ("body/female-view-three-quarter-left-visibility-audition.json", "three-quarter"),
            ("head/views/female-head-three-quarter-left-visibility-audition.json", "three-quarter"),
            ("head/closeups/female-head-face-closeup-visibility-audition.json", "front-facing"),
            ("head/closeups/female-head-standard-visibility-audition.json", "front-facing"),
        ):
            with self.subTest(card=card), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(folder / card)
            prompt = write.call_args.args[1].lower()
            positive = prompt.split("negative prompt:", 1)[0]
            self.assertIn(expected, positive)
            self.assertNotIn("replace the source photo's expression", positive)
            self.assertNotIn("{{", prompt)
            if card.startswith("head/"):
                self.assertIn("preserve the incoming expression and outfit", positive)
                self.assertIn("denoise ~0.4-0.6", positive)
            else:
                self.assertIn("keep the exact outfit from the incoming image", positive)
                self.assertIn("denoise ~0.5-0.7", positive)

    def test_hair_preservation_auditions_keep_environment_and_select_style(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies/hair")
        for card, expected in (("updo/female-hair-high-bun-preserve-audition.json", "sleek high bun"),
                               ("down/female-hair-beach-waves-preserve-audition.json", "soft, tousled beach waves")):
            with self.subTest(card=card), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(folder / card)
            prompt = write.call_args.args[1].lower()
            positive, negative = prompt.split("negative prompt:", 1)
            self.assertIn(expected, positive)
            self.assertIn("preserve the incoming setting and lighting", positive)
            self.assertIn("keeping the incoming hair color and highlights", positive)
            self.assertIn("expression and outfit", positive)
            self.assertNotIn("flat chest", negative)
            self.assertNotIn("{{", prompt)
            self.assertIn("denoise ~0.4-0.6", positive)

    def test_wardrobe_replacement_auditions_do_not_assume_an_underlayer(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/4_Wardrobe")
        for card, selected, arm in (
            ("armor/wardrobe/female-armor-half-plate-replace-audition.json", "half-plate", "leather sleeves with plate vambraces"),
            ("clothing/gowns/female-clothing-long-evening-gown-replace-audition.json", "evening gown", "bare arms"),
        ):
            with self.subTest(card=card), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(folder / card)
            prompt = write.call_args.args[1].lower()
            positive, negative = prompt.split("negative prompt:", 1)
            self.assertIn(selected, positive)
            self.assertIn(arm, positive)
            self.assertIn("replace the previous outfit, accessories and background", positive)
            self.assertIn("without remnants of the previous outfit or background", positive)
            self.assertIn("standing a-pose", positive)
            self.assertIn("keep the hands empty", positive)
            self.assertIn("background: replace the incoming background", positive)
            self.assertIn("lighting: even, soft, neutral frontal studio lighting", positive)
            self.assertIn("seated pose", negative)
            self.assertIn("colored studio backdrop", negative)
            self.assertNotIn("bikini underlayer", positive)
            self.assertNotIn("flat chest", negative)
            self.assertNotIn("{{", prompt)
            self.assertIn("denoise ~0.5-0.7", positive)

    def test_wardrobe_replacement_uses_selected_view_background_and_light(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/sovereign-females/female/4_Wardrobe/armor/wardrobe/female-armor-half-plate-replace-audition.json")
        card = gp.load_json(root / path)
        card["components"].update({
            "view": "A relaxed standing pose.",
            "background": "a plain blue studio backdrop",
            "lighting": "data/art/studio/lighting/soft-neutral-fill.json",
        })
        load_json = gp.load_json

        def load_selected(filename):
            return copy.deepcopy(card) if filename == root / path else load_json(filename)

        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(gp, "load_json", side_effect=load_selected), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive, negative = write.call_args.args[1].lower().split("negative prompt:", 1)
        self.assertIn("pose: a relaxed standing pose.", positive)
        self.assertIn("background: replace the incoming background with a plain blue studio backdrop.", positive)
        self.assertIn("lighting: soft neutral frontal light with gentle natural fill", positive)
        self.assertNotIn("standing a-pose", positive)
        self.assertNotIn("neutral light-grey seamless", positive)
        self.assertNotIn("seated pose", negative)
        self.assertNotIn("colored studio backdrop", negative)
        self.assertIn("dramatic lighting", negative)
        self.assertNotIn("{{", positive + negative)

    def test_scene_replacement_light_is_optional_and_independently_selectable(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/sovereign-females/female/5_Scenes/signature/female-replace-audition-scene-signature.json")
        card = gp.load_json(root / path)
        load_json = gp.load_json
        expected = (root / card["output"]).read_text(encoding="utf-8")

        def render():
            def load_selected(filename):
                return copy.deepcopy(card) if filename == root / path else load_json(filename)

            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(gp, "load_json", side_effect=load_selected), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            return write.call_args.args[1]

        self.assertEqual(render(), expected)
        card["components"]["lighting"] = "data/art/studio/lighting/warm-late-day.json"
        positive, negative = render().split("negative prompt:", 1)
        self.assertIn("Lighting: Warm late-day sunlight creates soft directional light.", positive)
        self.assertIn("sunlit white marble terrace", positive)
        self.assertNotIn("{{", positive + negative)
        card["components"]["lighting"] = "data/art/studio/lighting/soft-neutral-fill.json"
        positive, negative = render().split("negative prompt:", 1)
        self.assertIn("Lighting: Soft neutral frontal light", positive)
        self.assertIn("dramatic lighting, colored lighting", negative)

    def test_scene_replacement_auditions_resolve_source_color_and_selected_scene(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/5_Scenes")
        for card, expected in (
            ("glamour/female-replace-audition-scene-glamour.json", "moonlit castle terrace"),
            ("signature/female-replace-audition-scene-signature.json", "sunlit white marble terrace"),
        ):
            with self.subTest(card=card), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(folder / card)
            prompt = write.call_args.args[1].lower()
            positive, negative = prompt.split("negative prompt:", 1)
            self.assertIn(expected, positive)
            self.assertIn("replace the previous outfit, accessories and setting", positive)
            self.assertIn("incoming natural iris color", positive)
            self.assertNotIn("the natural the reference", positive)
            self.assertNotIn("flat chest", negative)
            self.assertNotIn("{{", prompt)
            self.assertIn("denoise ~0.5-0.7", positive)

    def test_motion_preservation_auditions_apply_selected_pose_and_expression(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/2_Studies/motions")
        for card, expected in (
            ("walking/female-motion-catwalk-confident-preserve-audition.json", "walking towards the camera"),
            ("standing/female-motion-hand-on-hip-power-preserve-audition.json", "one hand firmly on the hip"),
            ("dynamic/female-motion-twirl-spin-preserve-audition.json", "captured mid-twirl"),
        ):
            with self.subTest(card=card), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(folder / card)
            prompt = write.call_args.args[1].lower()
            positive, negative = prompt.split("negative prompt:", 1)
            self.assertIn(expected, positive)
            self.assertIn("preserve the incoming setting and lighting", positive)
            self.assertIn("apply the selected motion and expression", positive)
            self.assertIn("keeping the existing outfit and hairstyle", positive)
            self.assertNotIn("flat chest", negative)
            self.assertNotIn("{{", prompt)
            self.assertIn("denoise ~0.4-0.6", positive)
            if card.startswith("dynamic/"):
                self.assertIn("any loose fabric moves naturally", positive)
                self.assertNotIn("skirt or drape", positive)

    def test_ordered_reference_templates_can_select_independent_gestures(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        sources = (
            "data/art/_sets/sovereign-females/female/0_Edit/background/female-edit-background-basic.json",
            "data/art/_sets/sovereign-females/female/1_Alpha/1_Prime/female-alpha-prime.json",
        )
        gestures = (
            ("jaw-framing", "framing it without obscuring the face"),
            ("editorial-hand-tension", "tension visible at the knuckles"),
            ("relaxed-fingers", "softly curled fingers"),
            ("loosely-clasped-hands", "hands loosely clasped together"),
            ("cheek-touch", "lightly brush the cheekbone"),
            ("blowing-kiss", "blowing-kiss gesture"),
        )
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for source in sources:
                card = json.loads((root / source).read_text(encoding="utf-8"))
                for name, cue in gestures:
                    with self.subTest(source=source, gesture=name):
                        card["components"]["gesture"] = f"data/art/studio/gesture/{name}.json"
                        path.write_text(json.dumps(card), encoding="utf-8")
                        with mock.patch.object(gp, "ROOT", root), \
                             mock.patch.object(pathlib.Path, "mkdir"), \
                             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                             mock.patch("builtins.print"):
                            gp.generate(path)
                        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                        self.assertIn(cue, positive)
                        self.assertLess(positive.index("Pose:"), positive.index("Gesture:"))
                        self.assertLess(positive.index("Gesture:"), positive.index("Background:"))
                        self.assertNotIn("{{", positive + negative)

    def test_prime_input_footwear_auditions_change_only_footwear(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/1_Alpha/3_Footwear")
        for variant, selected in (("barefoot", "bare feet planted flat"),
                                  ("heels", "high-heeled shoes")):
            path = folder / f"female-alpha-{variant}-prime-input-audition.json"
            with self.subTest(variant=variant), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn("Replace only the footwear", positive)
            self.assertIn(selected, positive)
            self.assertIn("clothing and accessories", positive)
            self.assertIn("changed outfit", negative)
            self.assertNotIn("{{", positive + negative)
            if variant == "barefoot":
                self.assertIn("shoes", negative)
            else:
                self.assertNotIn("high heels", negative)

    def test_ordered_reference_templates_can_select_neck_and_shoulder_details(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        sources = (
            "data/art/_sets/sovereign-females/female/0_Edit/background/female-edit-background-basic.json",
            "data/art/_sets/sovereign-females/female/1_Alpha/1_Prime/female-alpha-prime.json",
        )
        details = (
            ("neck-long-elegant", "long, elegant neck"),
            ("collarbones-defined", "defined collarbones"),
            ("shoulders-gently-sloped", "sloped shoulders"),
            ("collarbones-angular", "angular collarbone line"),
        )
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for source in sources:
                card = json.loads((root / source).read_text(encoding="utf-8"))
                for name, cue in details:
                    with self.subTest(source=source, detail=name):
                        card["components"]["neck_shoulders"] = f"data/art/studio/figure/{name}.json"
                        path.write_text(json.dumps(card), encoding="utf-8")
                        with mock.patch.object(gp, "ROOT", root), \
                             mock.patch.object(pathlib.Path, "mkdir"), \
                             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                             mock.patch("builtins.print"):
                            gp.generate(path)
                        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                        self.assertIn(cue, positive)
                        self.assertIn("Neck and shoulders:", positive)
                        self.assertNotIn("{{", positive + negative)

    def test_selected_neck_detail_can_supply_negative_terms(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/1_Alpha/1_Prime/female-alpha-prime.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            detail = pathlib.Path(tmp) / "detail.json"
            detail.write_text(json.dumps({
                "id": "test-neck-detail", "kind": "figure", "name": "Test neck detail",
                "compatibleStages": ["alpha"], "description": "A selected neck detail.",
                "negatives": ["distorted neck"],
            }), encoding="utf-8")
            card["components"]["neck_shoulders"] = str(detail)
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("A selected neck detail", positive)
        self.assertIn("distorted neck", negative)

    def test_source_inspired_edit_pullbacks_include_environmental_film_still(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit")
        cards = (
            "background/female-edit-background-enhance.json",
            "cleanup/female-edit-cleanup-enhance.json",
            "enhance/female-edit-enhance-basic.json",
            "enhance/female-edit-enhance-plus.json",
            "enhance/female-edit-enhance-pose.json",
            "full/female-edit-full.json",
        )
        for card in cards:
            with self.subTest(card=card), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(folder / card)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            camera = next(line for line in positive.splitlines() if line.startswith("Camera:"))
            self.assertIn("wide environmental film still", camera)
            self.assertIn("legs", camera)
            self.assertIn("feet", camera)
            if card.endswith("enhance-pose.json"):
                self.assertNotIn("retaining the same pose", camera)
            else:
                self.assertIn("retaining the same pose", camera)
            self.assertNotIn("{{", positive + negative)

    def test_named_edit_pullbacks_keep_character_policies_and_camera_modes(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        for folder, hero in (
            ("angel-primes/female/angelica", "angelica"),
            ("angel-primes/male/angelo", "angelo"),
            ("drakn-sisters/drakness", "drakness"),
        ):
            for family, variant in (("background", "background-enhance"), ("enhance", "enhance-pose")):
                card = root / f"data/art/_sets/{folder}/0_Edit/{family}/{hero}-edit-{variant}.json"
                with self.subTest(card=card), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(card)
                positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                camera = next(line for line in positive.splitlines() if line.startswith("Camera:"))
                self.assertIn("wide environmental film still", camera)
                self.assertEqual("retaining the same pose" in camera, variant == "background-enhance")
                self.assertIn("Likeness:", positive)
                self.assertNotIn("{{", positive + negative)

    def test_edit_source_eye_detail_uses_wide_open_without_forcing_level_gaze(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        cards = (
            "sovereign-females/female/0_Edit/enhance/female-edit-enhance-basic.json",
            "sovereign-females/female/0_Edit/full/female-edit-full.json",
            "angel-primes/female/azaline/0_Edit/enhance/azaline-edit-enhance-plus.json",
            "drakn-sisters/drakness/0_Edit/full/drakness-edit-full.json",
        )
        for card in cards:
            with self.subTest(card=card), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(root / "data/art/_sets" / card)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn("Eyes: Both eyes matched and symmetrical, wide open", positive)
            self.assertNotIn("eyes matched, level", positive.lower())
            self.assertNotIn("{{", positive + negative)

    def test_selected_gesture_can_supply_negative_terms(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/1_Alpha/1_Prime/female-alpha-prime.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            gesture = pathlib.Path(tmp) / "gesture.json"
            gesture.write_text(json.dumps({
                "id": "test-gesture", "kind": "view", "name": "Test gesture",
                "compatibleStages": ["alpha"], "description": "A selected hand position.",
                "negatives": ["obscured gesture"],
            }), encoding="utf-8")
            card["components"]["gesture"] = str(gesture)
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("A selected hand position", positive)
        self.assertIn("obscured gesture", negative)

    def test_gown_replacement_audition_retains_source_material_conditionally(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        card = female_outfit_card("gown-replace-audition")
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(card)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("Replace the incoming outfit with a gown.", positive)
        self.assertIn("If an outfit is present, reuse its colors and fabric", positive)
        self.assertIn("without retaining its original garment design", positive)
        self.assertIn("extra clothing", negative)
        self.assertNotIn("{{", positive + negative)

    def test_silk_kiss_audition_selects_matching_gesture_and_expression(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        card = female_outfit_card("silk-kiss-audition")
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(card)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("one hand near the lips in a blowing-kiss gesture", positive)
        self.assertIn("Gently purse the lips as if blowing a kiss", positive)
        self.assertNotIn("smile", positive.lower())
        self.assertIn("silk two-piece", positive.lower())
        self.assertIn("extra clothing", negative.lower())
        self.assertNotIn("{{", positive + negative)

    def test_edit_can_select_lighting_and_gaze_without_adding_a_pose_change(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/0_Edit/full/female-edit-full.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for lighting, gaze, expected_light, expected_gaze in (
                ("dramatic-single-source", "soft-downcast", "single light source", "eyes gently lowered"),
                ("warm-late-day", "upward", "warm late-day sunlight", "eyes looking upward"),
                ("direct-flash", "past-camera", "direct photographic flash", "eyes looking past the camera"),
                ("soft-neutral-fill", "sidelong", "soft", "eyes glancing to one side"),
                ("soft-overcast", "past-camera", "soft overcast daylight", "eyes looking past the camera"),
                ("colored-neon", "past-camera", "colored neon light", "eyes looking past the camera"),
                ("water-caustics", "past-camera", "rippling caustic patterns", "eyes looking past the camera"),
                ("vanity-bulbs", "past-camera", "warm vanity bulb light", "eyes looking past the camera"),
                ("high-key", "past-camera", "bright high-key light", "eyes looking past the camera"),
            ):
                with self.subTest(lighting=lighting, gaze=gaze):
                    card["components"]["lighting"] = f"data/art/studio/lighting/{lighting}.json"
                    card["components"]["gaze"] = f"data/art/motion/gaze/{gaze}.json"
                    path.write_text(json.dumps(card), encoding="utf-8")
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(path)
                    positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
                    self.assertIn(expected_light, positive)
                    self.assertIn(expected_gaze, positive)
                    self.assertIn("keep the original scenery", positive)
                    self.assertNotIn("neutral frontal studio lighting", positive)

    def test_edit_can_expand_canvas_without_changing_camera_angle(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/0_Edit/full/female-edit-full.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        card["components"]["camera"] = "data/art/studio/framing/canvas-expand-preserve-angle.json"
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
        positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
        self.assertIn("preserve the incoming camera angle", positive)
        self.assertIn("newly visible areas are synthesized", positive)
        self.assertIn("keep the original scenery", positive)

    def test_edit_can_select_high_angle_framing_without_changing_pose(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/0_Edit/full/female-edit-full.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            card["components"]["camera"] = "data/art/studio/framing/pullback-full-environment-high-angle.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
        positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
        self.assertIn("above the subject and angle it downward", positive)
        self.assertIn("surrounding scene", positive)
        self.assertIn("keep the original scenery", positive)

    def test_optional_alpha_bust_preserves_existing_reference_prompts(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/1_Alpha"
        template = root / "data/art/_templates/heroes/1_Alpha/alpha-reference-human.txt"
        previous = template.read_text(encoding="utf-8").replace(
            "?Bust: {{BUST}}\n", ""
        ).replace("?{{KEY_AFTER_BUST}}\n", "").replace(
            "?{{ORDERED_KEY_BLOCK}}", "?{{KEY_BLOCK}}"
        ).replace("?{{BUST_NEG}},\n", "")
        cards = [path for path in folder.rglob("*.json")
                 if json.loads(path.read_text(encoding="utf-8"))["template"].endswith("alpha-reference-human.txt")
                 and "bust" not in json.loads(path.read_text(encoding="utf-8")).get("components", {})]
        self.assertTrue(cards)
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            old_template = pathlib.Path(tmp) / "previous-template.txt"
            old_template.write_text(previous, encoding="utf-8")
            for path in cards:
                card = json.loads(path.read_text(encoding="utf-8"))
                card["template"] = str(old_template)
                old_card = pathlib.Path(tmp) / path.name
                old_card.write_text(json.dumps(card), encoding="utf-8")
                rendered = []
                for source in (path, old_card):
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(source)
                    rendered.append(write.call_args.args[1])
                with self.subTest(card=path.name):
                    self.assert_only_duplicate_negatives_removed(rendered[0], rendered[1])

    def test_optional_bust_does_not_change_existing_edit_prompts(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/0_Edit"
        template = root / "data/art/_templates/heroes/0_Edit/edit-cleanup-human.txt"
        previous = template.read_text(encoding="utf-8").replace(
            "?Bust: {{BUST}}\n", ""
        ).replace("?{{KEY_AFTER_BUST}}\n", "").replace(
            "?{{ORDERED_KEY_BLOCK}}", "?{{KEY_BLOCK}}"
        ).replace("?{{BUST_NEG}},\n", "")
        cards = [path for path in folder.rglob("*.json")
                 if "bust" not in json.loads(path.read_text(encoding="utf-8")).get("components", {})]
        self.assertTrue(cards)
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            old_template = pathlib.Path(tmp) / "previous-template.txt"
            old_template.write_text(previous, encoding="utf-8")
            for path in cards:
                card = json.loads(path.read_text(encoding="utf-8"))
                card["template"] = str(old_template)
                old_card = pathlib.Path(tmp) / path.name
                old_card.write_text(json.dumps(card), encoding="utf-8")
                rendered = []
                for source in (path, old_card):
                    with mock.patch.object(gp, "ROOT", root), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(source)
                    rendered.append(write.call_args.args[1])
                with self.subTest(card=path.name):
                    self.assert_only_duplicate_negatives_removed(rendered[0], rendered[1])

    def test_enhance_variants_select_identity_and_supported_changes(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/enhance")
        for variant in ("basic", "plus", "pose"):
            path = folder / f"female-edit-enhance-{variant}.json"
            card = json.loads((root / path).read_text(encoding="utf-8"))
            identity = gp.load_identity(card["heroArt"])
            identity["art"]["palette"]["hairColor"] = "IDENTITY_HAIR"
            identity["art"]["palette"]["eyeColorGlamour"] = "IDENTITY_EYES"
            identity["art"]["palette"]["skinTone"] = "IDENTITY_SKIN"
            with self.subTest(variant=variant), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(gp, "load_identity", return_value=identity), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
            positive, negative = prompt.split("negative prompt:", 1)
            self.assertEqual(gp.art_layout.family(card, "angel-primes", root), ["enhance"])
            for value in ("IDENTITY_HAIR", "IDENTITY_EYES", "IDENTITY_SKIN"):
                self.assertIn(value.lower(), positive.lower())
            positions = [positive.index(label) for label in (
                "Pose:", "Background:", "Lighting:", "Camera:",
                "Edit the incoming image:", "Result:", "Critical details",
                "Hair:", "Bust:", "Eyes:", "Skin:", "Body:", "Likeness:",
            )]
            self.assertEqual(positions, sorted(positions))
            self.assertIn("original scenery", positive.lower())
            self.assertIn("changed background", negative)
            self.assertNotIn("changed eye color", negative)
            self.assertNotIn("{{", prompt)
            self.assertIn("Wearing:", positive)
            self.assertEqual("Expression:" in positive, variant == "pose")
            if variant == "pose":
                self.assertIn("over the shoulder", positive.lower())
                self.assertIn("knowing smirk", positive.lower())
                self.assertNotIn("preserve expression", positive.lower())
                self.assertIn("If clothing is present", positive)
                self.assertIn("changed clothing", negative)
                self.assertNotIn("retaining the same pose", positive.lower())

    def test_full_extends_source_scenery_and_appearance_without_preserving_jewelry(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/full/female-edit-full.json")
        card = json.loads((root / path).read_text(encoding="utf-8"))
        identity = gp.load_identity(card["heroArt"])
        identity["art"]["palette"]["hairColor"] = "IDENTITY_HAIR"
        identity["art"]["palette"]["eyeColorGlamour"] = "IDENTITY_EYES"
        identity["art"]["palette"]["skinTone"] = "IDENTITY_SKIN"
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(gp, "load_identity", return_value=identity), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        prompt = write.call_args.args[1]
        positive, negative = prompt.split("negative prompt:", 1)
        self.assertEqual(gp.art_layout.family(card, "angel-primes", root), ["full"])
        self.assertIn("Denoise ~1.0", positive)
        self.assertIn("Bust: A full, naturally rounded bust", positive)
        critical = positive.index("Critical details:")
        self.assertLess(positive.index("Hair:", critical), positive.index("Bust:", critical))
        self.assertLess(positive.index("Bust:", critical), positive.index("Eyes:", critical))
        self.assertIn("Keep the original scenery", positive)
        self.assertIn("Remove jewelry", positive)
        self.assertIn("Keep the incoming hairstyle", positive)
        self.assertIn("Keep the incoming eye color", positive)
        self.assertIn("Keep the incoming skin tone and tan", positive)
        self.assertIn("Keep the existing outfit", positive)
        self.assertIn("Gaze: eyes to camera", positive)
        self.assertNotIn("preserve the fabric, colors, coverage and accessories", positive.lower())
        self.assertNotIn("identity_hair", positive.lower())
        self.assertNotIn("identity_eyes", positive.lower())
        self.assertNotIn("identity_skin", positive.lower())
        self.assertIn("changed background", negative)
        self.assertNotIn("{{", prompt)

    def test_cleanup_can_omit_outfit_instructions(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/0_Edit/cleanup/female-edit-cleanup-basic.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        card["components"].pop("wearing")
        card["components"].pop("result_outfit")
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
        positive = write.call_args.args[1].split("negative prompt:", 1)[0]
        self.assertNotIn("Wearing:", positive)
        self.assertNotIn("existing outfit", positive)
        self.assertNotIn("{{", positive)

    def test_reference_edits_without_outfit_changes_omit_wearing(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit")
        cards = (
            folder / "pose/female-edit-pose-relaxed-three-quarter.json",
            folder / "pose/female-edit-pose-grounded-three-quarter.json",
        )
        for card in cards:
            with self.subTest(card=card), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(card)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertNotIn("Clothing:", positive)
            self.assertNotIn("Wearing:", positive)
            self.assertNotIn("fully clothed", positive.lower())
            self.assertIn("changed clothing", negative)

    def test_cleanup_keeps_source_appearance_instead_of_fixed_hero_colors(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        card = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/cleanup/female-edit-cleanup-basic.json")
        hero = gp.load_identity("data/art/heroes/sovereign-females/female.json")
        for marker in ("FIRSTIDENTITY", "SECONDIDENTITY"):
            identity = copy.deepcopy(hero)
            identity["art"]["palette"]["hairColor"] = marker + "HAIR"
            identity["art"]["palette"]["eyeColorGlamour"] = marker + "EYES"
            identity["art"]["palette"]["skinTone"] = marker + "SKIN"
            with self.subTest(identity=marker), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(gp, "load_identity", return_value=identity), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(card)
            self.assertNotIn(marker, write.call_args.args[1])

    def test_character_edit_can_select_identity_palette_and_figure(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/0_Edit/enhance/female-edit-enhance-basic.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        card["components"]["body"] = "{{FIGURE}}"
        del card["components"]["bust"]
        identity = gp.load_identity(card["heroArt"])
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            for marker in ("FIRST", "SECOND"):
                selected = copy.deepcopy(identity)
                selected["art"]["palette"]["hairColor"] = marker + "_HAIR"
                selected["art"]["palette"]["eyeColorGlamour"] = marker + "_EYES"
                selected["art"]["palette"]["skinTone"] = marker + "_SKIN"
                selected["art"]["physique"] = {
                    "build": marker + "_BUILD", "legs": marker + "_LEGS",
                    "bust": marker + "_FIGURE_DETAIL",
                }
                with self.subTest(identity=marker), \
                     mock.patch.object(gp, "ROOT", root), \
                     mock.patch.object(gp, "load_identity", return_value=selected), \
                     mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(path)
                positive = write.call_args.args[1].split("negative prompt:", 1)[0].upper()
                for detail in ("HAIR", "EYES", "SKIN", "BUILD", "LEGS", "FIGURE_DETAIL"):
                    self.assertIn(marker + "_" + detail, positive)
                self.assertNotIn(("SECOND" if marker == "FIRST" else "FIRST") + "_", positive)
                self.assertNotIn("RUNWAY MODEL PROPORTIONS", positive)
                self.assertNotIn("{{", positive)

    def test_cleanup_negatives_prioritize_source_failure_modes(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/cleanup")
        for name in ("cleanup", "cleanup-basic", "cleanup-enhance"):
            card = folder / f"female-edit-{name}.json"
            with self.subTest(variant=name), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(card)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            terms = [term.strip().rstrip(".") for term in negative.split(",")]
            self.assertLessEqual(len(terms), 15)
            for term in ("cropped body", "cropped feet", "blurred", "extra limbs",
                         "extra digits", "deformed hands", "text", "watermark", "logo",
                         "changed identity", "changed hair"):
                self.assertIn(term, terms)
            self.assertIn("Keep the incoming hairstyle, hair length, texture and color.", positive)
            self.assertIn("Retain existing jewelry.", positive)

    def test_cleanup_can_select_independent_lighting_and_skin_pieces(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/0_Edit/cleanup/female-edit-cleanup-basic.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = pathlib.Path(tmp)
            for slot, description in (("lighting", "A different lighting selection."),
                                      ("skin_edit", "Preserve the source skin tone."),
                                      ("likeness", "Keep the original facial likeness.")):
                piece = fixture / f"{slot}.json"
                piece.write_text(json.dumps({"id": slot, "kind": "edit", "name": slot,
                                             "compatibleStages": ["edit"], "description": description}), encoding="utf-8")
                card["components"][slot] = str(piece)
            card_path = fixture / "card.json"
            card_path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(card_path)
            prompt = write.call_args.args[1]
        self.assertIn("Lighting: A different lighting selection.", prompt)
        self.assertIn("Skin: Preserve the source skin tone.", prompt)
        self.assertIn("Background: Keep the original scenery", prompt)
        self.assertNotIn("slightly increase the tan", prompt)

    def test_subtle_rim_lighting_keeps_selected_scenery(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/0_Edit/cleanup/female-edit-cleanup-basic.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        card["components"]["lighting"] = "data/art/studio/lighting/subtle-rim.json"
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("Lighting: Subtle rim lighting outlines the subject's silhouette.", positive)
        self.assertIn("Background: Keep the original scenery", positive)
        self.assertIn("changed background", negative)

    def test_cleanup_background_selection_replaces_its_negative(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/0_Edit/cleanup/female-edit-cleanup-basic.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        card["components"]["background"] = "data/art/backgrounds/studio/grey-even.json"
        with tempfile.TemporaryDirectory() as tmp:
            card_path = pathlib.Path(tmp) / "card.json"
            card_path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(card_path)
            prompt = write.call_args.args[1]
        positive, negative = prompt.split("negative prompt:", 1)
        self.assertIn("plain neutral light-grey seamless studio backdrop", positive)
        self.assertNotIn("changed background", negative)
        self.assertIn("busy background", negative)

    def test_edit_and_prime_wearing_selection_controls_outfit_and_negatives(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        cards = (
            root / "data/art/_sets/sovereign-females/female/0_Edit/background/female-edit-background-basic.json",
            root / "data/art/_sets/sovereign-females/female/1_Alpha/4_Outfits/female-alpha-outfit-relaxed.json",
        )
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            fixture = pathlib.Path(tmp)
            for source in cards:
                card = json.loads(source.read_text(encoding="utf-8"))
                for piece, expected, negative in (
                    ("data/art/edits/policies/clothing-preserve.json", "same outfit", True),
                    ("data/art/reference/wardrobe/existing-fitted.json", "fitted silhouette", False),
                ):
                    with self.subTest(stage=card["stage"], piece=piece):
                        card["components"]["wearing"] = piece
                        path = fixture / "card.json"
                        path.write_text(json.dumps(card), encoding="utf-8")
                        with mock.patch.object(gp, "ROOT", root), \
                             mock.patch.object(pathlib.Path, "mkdir"), \
                             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                             mock.patch("builtins.print"):
                            gp.generate(path)
                        positive, negatives = write.call_args.args[1].split("negative prompt:", 1)
                        self.assertIn(expected, positive)
                        self.assertEqual("changed clothing" in negatives, negative)

    def test_legacy_outfit_slots_remain_usable_with_wearing_templates(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        source = root / "data/art/_sets/sovereign-females/female/1_Alpha/4_Outfits/female-alpha-outfit-relaxed.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        wearing = card["components"].pop("wearing")
        with tempfile.TemporaryDirectory(dir=root / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            for slot in ("clothing_policy", "clothing"):
                with self.subTest(slot=slot):
                    card["components"][slot] = wearing
                    path.write_text(json.dumps(card), encoding="utf-8")
                    with mock.patch.object(gp, "ROOT", root):
                        tokens = gp.generate(path, tokens_only=True)
                    self.assertIn("same outfit", tokens["WEARING"])
                    self.assertIn("changed clothing", tokens["WEARING_NEG"])
                    del card["components"][slot]
            card["components"].update({"clothing": wearing, "clothing_policy": wearing})
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root), \
                 self.assertRaisesRegex(SystemExit, "multiple legacy outfit slots"):
                gp.generate(path, tokens_only=True)
            card["components"].pop("clothing")
            card["components"]["wearing"] = "data/art/reference/wardrobe/existing-fitted.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(gp, "ROOT", root):
                tokens = gp.generate(path, tokens_only=True)
            self.assertIn("fitted silhouette", tokens["WEARING"])
            self.assertNotIn("changed clothing", tokens["WEARING_NEG"])

    def test_outfit_auditions_reuse_preservation_controls_in_the_correct_stage(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/1_Alpha/4_Outfits"
        cards = [folder / f"female-alpha-outfit-{name}.json" for name in ("grounded", "relaxed")]
        for path in cards:
            card = json.loads(path.read_text(encoding="utf-8"))
            tokens = gp.generate(path.relative_to(root).as_posix(), tokens_only=True)
            self.assertEqual(card["stage"], "alpha")
            self.assertIn("/1_Alpha/4_Outfits/", card["output"])
            self.assertIn("same outfit", tokens["WEARING"])
            self.assertIn("recognizable face", tokens["LIKENESS"])
            with mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path.relative_to(root).as_posix())
            prompt = write.call_args.args[1]
            positive, negative = prompt.split("negative prompt:", 1)
            labels = ("Pose:", "Background:", "Lighting:", "Camera:",
                      "Edit the incoming image:", "Result:", "Body:",
                      "Likeness:", "Wearing:", "Hair:")
            positions = [positive.index(label) for label in labels]
            self.assertEqual(positions, sorted(positions))
            self.assertIn("same outfit", positive)
            self.assertIn("recognizable face", positive)
            self.assertNotIn("Bust:", positive)
            self.assertIn("changed clothing", negative)
            self.assertIn("changed eye color", negative)
            self.assertIn("changed hair", negative)
            self.assertNotIn("{{", prompt)

    def test_source_inspired_outfits_select_slender_heels_without_forcing_leg_exposure(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        variants = (
            "celestial-covered", "celestial-covered-hair-touch",
            "gown", "gown-source-fabric-and-colors", "gown-replace-audition",
            "halter", "halter-source-fabric-and-colors", "silk", "silk-kiss-audition",
            "silk-crouch", "two-piece-source-fabric-and-colors", "source-three-quarter",
        )
        for variant in variants:
            path = female_outfit_card(variant)
            with self.subTest(variant=variant), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn("Footwear: high-heeled shoes with slender stiletto heels", positive)
            self.assertNotIn("bare legs", positive.lower())
            self.assertNotIn("no footwear", negative.lower())
            self.assertNotIn("{{", positive + negative)

    def test_outfit_source_variants_render_distinct_views_and_garments(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        for name, view, garment in (
            ("source-three-quarter", "heel slightly raised", "Keep the existing outfit"),
            ("gown", "gesture toward the camera", "into a gown"),
            ("halter", "relaxed stride", "into a halter dress"),
            ("silk", "one hand on the lower thigh", "into a silk two-piece outfit"),
        ):
            path = female_outfit_card(name)
            card = json.loads((root / path).read_text(encoding="utf-8"))
            with self.subTest(variant=name), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
            positive = prompt.split("negative prompt:", 1)[0]
            expected_family = {"gown": ["outfits", "gowns"], "halter": ["outfits", "dresses"],
                               "silk": ["outfits", "sets"]}.get(name, ["outfits"])
            self.assertEqual(gp.art_layout.family(card, "angel-primes", root), expected_family)
            self.assertIn(view.lower(), positive.lower())
            self.assertIn(garment.lower(), positive.lower())
            self.assertIn("Bust:", positive)
            self.assertNotIn("{{", prompt)
            if name != "source-three-quarter":
                self.assertIn("existing colors", positive)
                self.assertNotIn("changed clothing", prompt.lower())
                self.assertIn("extra clothing", prompt.split("negative prompt:", 1)[1].lower())
            if name in ("halter", "silk"):
                self.assertNotIn("standing a-pose", positive.lower())

    def test_source_inspired_alpha_auditions_retain_hair_and_environment(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        base = pathlib.Path("data/art/_sets/sovereign-females/female/1_Alpha")
        paths = [base / "1_Prime/female-alpha-prime.json"]
        paths.extend(female_outfit_card(name) for name in (
            "source-apose", "source-three-quarter", "gown", "gown-source-fabric-and-colors",
            "halter", "halter-source-fabric-and-colors", "silk", "two-piece-source-fabric-and-colors",
            "silk-crouch", "celestial-covered", "celestial-covered-hair-touch",
            "silk-kiss-audition", "gown-replace-audition",
        ))
        for path in paths:
            with self.subTest(path=path), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive = write.call_args.args[1].split("negative prompt:", 1)[0]
            self.assertIn("Keep the incoming hair length", positive)
            self.assertIn("ends visible", positive)
            self.assertIn("Sweep the front sections slightly back", positive)
            self.assertIn("eyes, brows and temples clear", positive)
            self.assertIn("reveal the complete figure and show the feet", positive)
            self.assertIn("Include the surrounding scene and extend it seamlessly", positive)
            self.assertIn("Frame the surrounding scene as a wide environmental film still", positive)
            self.assertIn("Both eyes matched, level and symmetrical, wide open", positive)

    def test_outfit_pose_variants_preserve_source_pose_distinctions(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        for name, details in (
            ("source-three-quarter", ("three-quarter", "upper torso toward the camera", "toes", "heel slightly raised")),
            ("gown", ("hip to the side", "one hand on the hip", "gesture toward the camera")),
            ("gown-source-fabric-and-colors", ("hip to the side", "gesture toward the camera")),
            ("halter", ("relaxed stride", "step the other forward", "fingers apart")),
            ("halter-source-fabric-and-colors", ("relaxed stride", "fingers apart")),
            ("silk", ("one hand on the lower thigh", "raise the other near the face")),
            ("two-piece-source-fabric-and-colors", ("one hand on the lower thigh", "raise the other near the face")),
        ):
            path = female_outfit_card(name)
            with self.subTest(variant=name), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive = write.call_args.args[1].split("negative prompt:", 1)[0].lower()
            for detail in details:
                self.assertIn(detail, positive)

    def test_covered_celestial_adaptation_preserves_supported_source_cues(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = female_outfit_card("celestial-covered")
        card = json.loads((root / path).read_text(encoding="utf-8"))
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        self.assertEqual(gp.art_layout.family(card, "angel-primes", root), ["outfits", "celestial"])
        for cue in ("both hands on the hips", "foot lifted", "Replace the incoming outfit completely",
                    "Do not retain details of the previous garments", "covered celestial-inspired ensemble",
                    "existing colors", "polished metallic fabric", "high-heeled shoes"):
            self.assertIn(cue, positive)
        self.assertIn("extra clothing", negative)
        self.assertNotIn("changed clothing", negative)
        self.assertNotIn("{{", positive)

    def test_silk_crouch_adapts_pose_and_source_color_outfit(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = female_outfit_card("silk-crouch")
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        for cue in ("relaxed crouch", "one heel raised", "one hand on the knee",
                    "other on the hip", "silk two-piece outfit", "existing colors", "high-heeled shoes"):
            self.assertIn(cue, positive)
        self.assertIn("extra clothing", negative)
        self.assertNotIn("changed clothing", negative)
        self.assertNotIn("{{", positive)

    def test_covered_celestial_hair_touch_keeps_distinct_pose(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = female_outfit_card("celestial-covered-hair-touch")
        with mock.patch.object(gp, "ROOT", root), \
             mock.patch.object(pathlib.Path, "mkdir"), \
             mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
             mock.patch("builtins.print"):
            gp.generate(path)
        positive, negative = write.call_args.args[1].split("negative prompt:", 1)
        for cue in ("toes on the floor", "heel slightly raised", "one hand on the hip",
                    "touch the hair", "Replace the incoming outfit completely",
                    "Do not retain details of the previous garments", "covered celestial-inspired ensemble", "existing colors"):
            self.assertIn(cue, positive)
        self.assertNotIn("foot lifted", positive)
        self.assertIn("extra clothing", negative)

    def test_source_inspired_outfits_place_selected_detail_between_identity_lines(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        for name in (
            "gown", "gown-source-fabric-and-colors", "halter",
            "halter-source-fabric-and-colors", "silk", "source-apose",
            "source-three-quarter", "two-piece-source-fabric-and-colors",
        ):
            path = female_outfit_card(name)
            with self.subTest(variant=name), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive = write.call_args.args[1].split("negative prompt:", 1)[0]
            critical = positive.index("Critical details")
            positions = [positive.index(label, critical) for label in ("Hair:", "Bust:", "Eyes:", "Skin:", "Body:")]
            self.assertEqual(positions, sorted(positions))
            self.assertIn("Wearing:", positive)
            self.assertNotIn("{{", positive)

    def test_outfit_fabric_variants_preserve_source_material_without_forcing_silk(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        for name, garment in (
            ("gown", "gown"),
            ("halter", "halter dress"),
            ("two-piece", "two-piece outfit"),
        ):
            path = female_outfit_card(f"{name}-source-fabric-and-colors")
            with self.subTest(variant=name), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
            positive = prompt.split("negative prompt:", 1)[0].lower()
            self.assertIn(garment, positive)
            self.assertIn("fabric or material", positive)
            self.assertIn("colors", positive)
            self.assertNotIn("silk", positive)
            self.assertNotIn("changed clothing", prompt.lower())
            self.assertIn("extra clothing", prompt.split("negative prompt:", 1)[1].lower())
            self.assertNotIn("{{", prompt)

    def test_outfit_source_apose_selects_appearance_and_preserves_outfit(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        path = pathlib.Path("data/art/_sets/sovereign-females/female/1_Alpha/4_Outfits/female-alpha-outfit-source-apose.json")
        card = json.loads((root / path).read_text(encoding="utf-8"))
        with mock.patch.object(gp, "ROOT", root):
            generic = gp.generate(path, tokens_only=True)
        for label in ("Hair:", "Eyes:", "Skin:"):
            self.assertIn(label, generic["KEY_BLOCK"])
        self.assertGreaterEqual(generic["KEY_BLOCK"].lower().count("reference image"), 3)
        for marker in ("FIRST", "SECOND"):
            identity = gp.load_identity(card["heroArt"])
            identity["art"]["palette"]["hairColor"] = f"{marker}_HAIR"
            identity["art"]["palette"]["eyeColorGlamour"] = f"{marker}_EYES"
            identity["art"]["palette"]["skinTone"] = f"{marker}_SKIN"
            with self.subTest(identity=marker), \
                 mock.patch.object(gp, "ROOT", root), \
                 mock.patch.object(gp, "load_identity", return_value=identity), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            prompt = write.call_args.args[1]
            positive, negative = prompt.split("negative prompt:", 1)
            positions = [positive.index(label) for label in (
                "Pose:", "Background:", "Lighting:", "Camera:",
                "Edit the incoming image:", "Result:", "Critical details",
                "Body:", "Likeness:", "Wearing:", "Footwear:",
            )]
            self.assertEqual(positions, sorted(positions))
            for value in (f"{marker}_HAIR", f"{marker}_EYES", f"{marker}_SKIN"):
                self.assertIn(value.lower(), positive.lower())
            self.assertIn("replace the incoming pose", positive)
            self.assertIn("head facing the camera squarely", positive.lower())
            self.assertNotIn("same overall pose", positive)
            self.assertIn("Remove jewelry", positive)
            self.assertIn("Keep the existing outfit", positive)
            self.assertIn("high-heeled shoes", positive)
            self.assertIn("changed clothing", negative)
            self.assertNotIn("{{", prompt)

    def test_reference_edit_cards_resolve_policies_without_fixed_identity(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        cards = sorted((root / "data/art/_sets/sovereign-females/female/0_Edit").rglob("*.json"))
        self.assertGreaterEqual(len(cards), 6)
        for path in cards:
            card = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(card=card["artId"]):
                tokens = gp.generate(path.relative_to(root).as_posix(), tokens_only=True)
                template = (root / card["template"]).read_text(encoding="utf-8")
                required = set(re.findall(r"{{(\w+)}}", gp.apply_optional_lines(template, tokens)))
                self.assertEqual(required - tokens.keys(), set())
                self.assertEqual(tokens["DENOISE"], card["denoise"])
                if path.parent.name in ("deluxe", "pose"):
                    self.assertIn("recognizable face", tokens["LIKENESS"])
                    if path.parent.name == "pose":
                        self.assertNotIn("FACE_POLICY", tokens)
                        self.assertIn("visible body proportions", tokens["BODY"])
                    else:
                        self.assertEqual(tokens["FACE_POLICY"], tokens["LIKENESS"])
                        self.assertIn("runway model proportions", tokens["BODY"])
                        self.assertIn("naturally rounded bust", tokens["BUST"])
                    self.assertNotIn("WEARING", required)
                self.assertNotIn("Angelica", " ".join(tokens[k] for k in required))

    def test_three_quarter_poses_are_distinct_and_not_locked_to_a_pose(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/sovereign-females/female/0_Edit/pose"
        resolved = {}
        for path in folder.glob("*.json"):
            card = json.loads(path.read_text(encoding="utf-8"))
            tokens = gp.generate(path.relative_to(root).as_posix(), tokens_only=True)
            resolved[card["artId"]] = tokens["VIEW"]
            self.assertNotIn("same A-pose", tokens["VIEW"])
        self.assertIn("one hand resting naturally on the hip",
                      resolved["female-edit-pose-relaxed-three-quarter"])
        grounded = resolved["female-edit-pose-grounded-three-quarter"]
        self.assertIn("both feet flat on the floor", grounded)
        self.assertIn("forward knee softly bent", grounded)

    def test_generic_edit_pilot_fills_every_template_token(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        card_path = "data/art/_sets/sovereign-females/female/0_Edit/cleanup/female-edit-cleanup-basic.json"
        with mock.patch.object(gp, "ROOT", root):
            card = json.loads((root / card_path).read_text(encoding="utf-8"))
            tokens = gp.generate(card_path, tokens_only=True)
            template = (root / card["template"]).read_text(encoding="utf-8")

        required = set(re.findall(r"{{(\w+)}}", gp.apply_optional_lines(template, tokens)))
        self.assertEqual(required - tokens.keys(), set())
        self.assertTrue(tokens["EDIT_TASK_NEG"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
