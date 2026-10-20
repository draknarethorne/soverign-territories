#!/usr/bin/env python3
"""prime_compare: the variants of a hero's Prime, where their renders are found, and the face score. Run: python tools/art/test_prime_compare.py"""
import pathlib
import shutil
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
sys.path.insert(0, str(ROOT / "tools/workflows"))
import comfy_workflows as cw  # noqa: E402
import prime_compare as pc  # noqa: E402

CFG = {"photos": {"Alice": "alice_image_1_944x1104.png"}, "flows": {"alternate": {"photos": {"Alice": "alice_image_1_alt_944x1104.png"}}}}


class PrimeCompareTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_a_hero_has_two_prime_variants_per_configured_flow(self):
        self.assertEqual([(lab, name) for lab, name, _f, _e in pc.variants(CFG, "Alice")],
                         [("Qwen", "Alice_Qwen_Alpha_1_Prime"), ("FireRed", "Alice_FireRed_Alpha_1_Prime"),
                          ("Qwen / alternate", "Alice_Qwen_Alpha_1_Prime_Alternate"), ("FireRed / alternate", "Alice_FireRed_Alpha_1_Prime_Alternate")])
        self.assertEqual(len(pc.variants(CFG, "Bob")), 2, "no alternate photo, no alternate variants")

    def test_the_first_shot_experiments_are_extra_variants_with_their_own_labels(self):
        got = [(lab, name) for lab, name, _f, _e in pc.variants(CFG, "Alice", ("neutral", "bare"))]
        self.assertEqual(got[0], ("Qwen P2 neutral", "Alice_Qwen_Alpha_1b_NeutralBase"))
        self.assertIn(("FireRed P3 bare / alternate", "Alice_FireRed_Alpha_1b_BareBase_Alternate"), got)
        self.assertEqual(len(got), 8)
        self.assertEqual(len(pc.variants(CFG, "Alice", tuple(pc.SHOTS))), 12)

    def test_renders_are_found_newest_first_and_a_variant_never_picks_up_another_ones(self):
        out = self.tmp / "out" / "deep"
        out.mkdir(parents=True)
        for i, name in enumerate(("Alice_Qwen_Alpha_1_Prime_00001_.png", "Alice_Qwen_Alpha_1_Prime_00002_.png", "Alice_Qwen_Alpha_1_Prime_Alternate_00001_.png", "Alice_Qwen_Alpha_1_Prime_00003_NOPE.png")):
            (out / name).write_bytes(b"x")
            import os
            os.utime(out / name, (time.time() + i, time.time() + i))
        with mock.patch.object(cw, "output_roots", lambda cfg: [self.tmp / "out"]):
            self.assertEqual([p.name for p in pc.renders(CFG, "Alice_Qwen_Alpha_1_Prime", every=True)], ["Alice_Qwen_Alpha_1_Prime_00002_.png", "Alice_Qwen_Alpha_1_Prime_00001_.png"])
            self.assertEqual([p.name for p in pc.renders(CFG, "Alice_Qwen_Alpha_1_Prime")], ["Alice_Qwen_Alpha_1_Prime_00002_.png"])
            self.assertEqual([p.name for p in pc.renders(CFG, "Alice_Qwen_Alpha_1_Prime_Alternate")], ["Alice_Qwen_Alpha_1_Prime_Alternate_00001_.png"])
            self.assertEqual(pc.renders(CFG, "Alice_FireRed_Alpha_1_Prime"), [])

    def test_the_score_is_the_cosine_of_the_centred_faces_and_a_picture_without_a_face_has_none(self):
        faces = {"a.png": [1.0, 0.2, 0.0], "same.png": [0.9, 0.3, 0.0], "other.png": [0.0, 0.2, 1.0], "none.png": None}
        s = pc.Scorer.__new__(pc.Scorer)
        s.space = types.SimpleNamespace(mean=np.array([0.1, 0.1, 0.1]))
        s.embed = lambda p: {"v": faces[p.name]} if faces[p.name] else {"faces": 0}
        s.vecs = {}
        a = pathlib.Path("a.png")
        self.assertGreater(s.score(a, pathlib.Path("same.png")), 0.9)
        self.assertLess(s.score(a, pathlib.Path("other.png")), 0.3)
        self.assertIsNone(s.score(a, pathlib.Path("none.png")))

    def test_the_sheet_is_written_with_the_original_and_each_variant(self):
        from PIL import Image
        for n in ("o.png", "r.png"):
            Image.new("RGB", (94, 110), (200, 100, 50)).save(self.tmp / n)
        out = self.tmp / "sheet.png"
        pc.sheet([("Alice", [("original", self.tmp / "o.png", None), ("Qwen", self.tmp / "r.png", 0.61)]), ("Bob", [("original", self.tmp / "o.png", None)])], out, size=(47, 55))
        with Image.open(out) as im:
            self.assertEqual(im.size, (90 + 2 * 47, 2 * (55 + 30)))


if __name__ == "__main__":
    unittest.main()
