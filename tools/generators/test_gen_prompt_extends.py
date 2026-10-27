#!/usr/bin/env python3
"""Tests for reusable piece resolution and the shared edit prompt's token contract.

Most tests use throwaway pieces; the edit-pilot integration test reads the real
assembly card and template without writing generated output.

Run: python -m unittest tools.generators.test_gen_prompt_extends
"""
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
        """alpha/female is a hero; angel-primes/female is a division of ten women. --slug female must not pick the whole division."""
        paths = gp.iter_card_paths(group="angel-primes", slug="female")
        self.assertTrue(paths)
        self.assertTrue(all("/alpha/female/" in p.as_posix() for p in paths), "only the alpha test hero")
        self.assertTrue(all("/female/azaline/" not in p.as_posix() for p in paths))
        self.assertTrue(any("/female/azaline/" in p.as_posix() for p in gp.iter_card_paths(group="angel-primes", slug="azaline")), "a normal angel is still found by her slug")


class ArtPromptIntegrationTests(unittest.TestCase):
    def test_reference_edit_cards_resolve_policies_without_fixed_identity(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        cards = sorted((root / "data/art/_sets/angel-primes/alpha/female/0_Edit").rglob("*.json"))
        self.assertEqual(len(cards), 6)
        for path in cards:
            card = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(card=card["artId"]):
                tokens = gp.generate(path.relative_to(root).as_posix(), tokens_only=True)
                template = (root / card["template"]).read_text(encoding="utf-8")
                required = set(re.findall(r"{{(\w+)}}", template))
                self.assertEqual(required - tokens.keys(), set())
                self.assertEqual(tokens["DENOISE"], card["denoise"])
                if "face_policy" in card["components"]:
                    self.assertIn("recognizable face", tokens["FACE_POLICY"])
                    self.assertIn("fully clothed in the same outfit", tokens["CLOTHING_POLICY"])
                    self.assertIn("visible body proportions", tokens["BODY_POLICY"])
                    self.assertNotIn("Angelica", " ".join(tokens[k] for k in required))

    def test_three_quarter_poses_are_distinct_and_not_locked_to_a_pose(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        folder = root / "data/art/_sets/angel-primes/alpha/female/0_Edit/pose"
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
        card_path = "data/art/_sets/angel-primes/alpha/female/0_Edit/cleanup/female-edit-cleanup-basic.json"
        with mock.patch.object(gp, "ROOT", root):
            card = json.loads((root / card_path).read_text(encoding="utf-8"))
            tokens = gp.generate(card_path, tokens_only=True)
            template = (root / card["template"]).read_text(encoding="utf-8")

        required = set(re.findall(r"{{(\w+)}}", template))
        self.assertEqual(required - tokens.keys(), set())
        self.assertTrue(tokens["EDIT_TASK_NEG"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
