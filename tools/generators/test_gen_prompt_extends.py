#!/usr/bin/env python3
"""Tests for piece `extends` in gen_prompt.load_piece, using throwaway pieces (no real art data is read).

Run: python tools/generators/test_gen_prompt_extends.py
"""
import json
import pathlib
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


if __name__ == "__main__":
    unittest.main(verbosity=1)
