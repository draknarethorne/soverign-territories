#!/usr/bin/env python3
"""Tests for finals.py: tolerant parsing of saved workflow names and slots. Run: python tools/workflows/test_finals.py"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import finals  # noqa: E402

HEROES = ["Remiah", "Draknara", "Draknava", "Seraphine", "Sandalyn"]
STEMS = ["Remiah_Qwen_Alpha_1_Prime", "Remiah_Qwen_Alpha_2_Bare_Figure", "Remiah_Qwen_Alpha_2_Bare_Chest",
         "Remiah_FireRed_Alpha_1_Prime", "Draknara_Qwen_X_Pose", "Draknava_Qwen_X_Pose", "Seraphine_Qwen_Scene_Glamour"]


class ParseTests(unittest.TestCase):
    def test_exact_name_with_counter(self):
        r = finals.parse_name("Remiah_Qwen_Alpha_1_Prime_00015_.json", HEROES, STEMS)
        self.assertEqual((r["hero"], r["engine"], r["rest"], r["counter"], r["exact"]), ("Remiah", "Qwen", "Alpha_1_Prime", "00015", True))

    def test_name_without_counter_or_extension(self):
        r = finals.parse_name("Remiah_FireRed_Alpha_1_Prime", HEROES, STEMS)
        self.assertEqual((r["engine"], r["counter"]), ("FireRed", None))

    def test_case_and_typos_are_corrected_and_flagged(self):
        for name in ("remiah_qwen_alpha_1_prime_00004_.json", "Remaih_Qwen_Alpha_1_Prime_00004_.json", "Remiah_Qwn_Alpha_1_Prime_00004_.json",
                     "Remiah_Qwen_Alpha_1_Prim_00004_.json"):
            r = finals.parse_name(name, HEROES, STEMS)
            self.assertIsNotNone(r, name)
            self.assertEqual(r["stem"], "Remiah_Qwen_Alpha_1_Prime", name)
            self.assertFalse(r["exact"], name)

    def test_a_correct_hero_is_never_swapped_for_a_near_one(self):
        self.assertEqual(finals.parse_name("Draknara_Qwen_X_Pose_00002_.json", HEROES, STEMS)["hero"], "Draknara")
        self.assertEqual(finals.parse_name("Draknava_Qwen_X_Pose_00002_.json", HEROES, STEMS)["hero"], "Draknava")

    def test_an_ambiguous_hero_is_refused(self):
        self.assertIsNone(finals.parse_name("Drakna_Qwen_X_Pose_00002_.json", HEROES, STEMS))

    def test_a_similar_stage_is_not_guessed(self):
        r = finals.parse_name("Remiah_Qwen_Alpha_2_Bare_Figure_00001_.json", HEROES, STEMS)
        self.assertEqual(r["stem"], "Remiah_Qwen_Alpha_2_Bare_Figure")

    def test_a_renamed_stage_is_placed_by_the_current_stage_and_keeps_its_own_file_name(self):
        r = finals.parse_name("Alice_Qwen_X_Pose_00004_.json", ["Alice"], ["Alice_Qwen_Alpha_1_Prime"], {"X_Pose": "Alpha_1_Prime"})
        self.assertEqual((r["stem"], r["file_stem"], r["counter"]), ("Alice_Qwen_Alpha_1_Prime", "Alice_Qwen_X_Pose", "00004"))
        self.assertIsNone(finals.parse_name("Alice_Qwen_X_Pose_00004_.json", ["Alice"], ["Alice_Qwen_Alpha_1_Prime"]))

    def test_phase_renames_keep_saved_names_and_resolve_exactly(self):
        cases = (
            ("X_Pose_TriangleBikini", "Layer_TriangleBikini"),
            ("X_Pose_Layer_OnePiece_Preserve_Audition", "Layer_OnePiece_Preserve_Audition"),
            ("X_Head", "Head"),
            ("X_Head_Denoise_Audition", "Head_Denoise_Audition"),
            ("Alpha_1b_BareBase", "Alpha_2_BareBase"),
            ("Alpha_2b_CelestialCore", "Alpha_4_Outfits_CelestialCore"),
        )
        for old, new in cases:
            with self.subTest(old=old):
                result = finals.parse_name(f"Alice_Qwen_{old}_00004_.json", ["Alice"], [f"Alice_Qwen_{new}"])
                self.assertEqual(result["stem"], f"Alice_Qwen_{new}")
                self.assertEqual(result["file_stem"], f"Alice_Qwen_{old}")
                both = finals.parse_name(f"Alice_Qwen_{old}.json", ["Alice"], [f"Alice_Qwen_{old}", f"Alice_Qwen_{new}"])
                self.assertEqual(both["stem"], f"Alice_Qwen_{old}")

    def test_explicit_migration_precedes_a_similar_old_stage(self):
        stems = ["Alice_Qwen_Layer_TriangleBikini", "Alice_Qwen_X_Pose_TriangleBikinis"]
        result = finals.parse_name("Alice_Qwen_X_Pose_TriangleBikini_00004_.json", ["Alice"], stems)
        self.assertEqual(result["stem"], "Alice_Qwen_Layer_TriangleBikini")
        self.assertEqual(result["file_stem"], "Alice_Qwen_X_Pose_TriangleBikini")

    def test_unknown_things_are_refused(self):
        for name in ("Nobody_Qwen_Alpha_1_Prime_00001_.json", "Remiah_Qwen_Totally_Other_00001_.json", "Remiah.json", "ST1_Qwen_A_Pose.json"):
            self.assertIsNone(finals.parse_name(name, HEROES, STEMS), name)


class SlotTests(unittest.TestCase):
    SLOTS = {"prime": ["Alpha_1_Prime", "X_Pose"], "bare": ["Alpha_2_Bare_Figure"], "golden": ["Alpha_3_Barefoot"]}

    def test_slots(self):
        self.assertEqual(finals.slot_of("Remiah_Qwen_Alpha_1_Prime", self.SLOTS), "prime")
        self.assertEqual(finals.slot_of("Draknara_Qwen_X_Pose", self.SLOTS), "prime")
        self.assertEqual(finals.slot_of("Remiah_Qwen_Alpha_2_Bare_Figure", self.SLOTS), "bare")
        self.assertIsNone(finals.slot_of("Seraphine_Qwen_Scene_Glamour", self.SLOTS))


if __name__ == "__main__":
    unittest.main()
