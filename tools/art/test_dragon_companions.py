"""Tests for dragon_companions.py: a typed companion sentence splits into frame vars and joins back byte for byte."""
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import dragon_companions as dc  # noqa: E402

IDENT = {"pyraxis": {"description": "an Elder Dragon with ember-red scales and a swept crest"}}


class DecomposeTests(unittest.TestCase):
    def test_full_text_round_trips(self):
        text = "her aligned Elder Dragon, Pyraxis, behind her, an Elder Dragon with ember-red scales and a swept crest, wings half open"
        slug, kind, vars_ = dc.decompose(text, IDENT)
        self.assertEqual((slug, kind), ("pyraxis", "full"))
        self.assertEqual(vars_["PLACEMENT"], "behind her, ")
        self.assertEqual(dc.rebuild(slug, kind, vars_, IDENT), text)

    def test_full_text_with_no_placement(self):
        text = "her aligned Elder Dragon, Pyraxis, an Elder Dragon with ember-red scales and a swept crest"
        slug, kind, vars_ = dc.decompose(text, IDENT)
        self.assertEqual(vars_["PLACEMENT"], "")
        self.assertEqual(dc.rebuild(slug, kind, vars_, IDENT), text)

    def test_reworded_text_uses_the_distant_frame(self):
        text = "her aligned Elder Dragon, Pyraxis, a vast red silhouette against the clouds"
        slug, kind, vars_ = dc.decompose(text, IDENT)
        self.assertEqual(kind, "far")
        self.assertEqual(dc.rebuild(slug, kind, vars_, IDENT), text)

    def test_other_openings_are_left_alone(self):
        self.assertIsNone(dc.decompose("a dragon behind her", IDENT))
        self.assertIsNone(dc.decompose("her aligned Elder Dragon, Nobody, beside her", IDENT))


class FrameTests(unittest.TestCase):
    def test_frames_carry_the_identity_description(self):
        (fp, full), (dp, far) = dc.frames("pyraxis", IDENT["pyraxis"])
        self.assertIn(IDENT["pyraxis"]["description"], full["description"])
        self.assertTrue(full["description"].endswith("[[DETAIL]]"))
        self.assertTrue(far["description"].endswith("[[PLACEMENT]]"))
        self.assertTrue(fp.endswith("pyraxis-companion.json") and dp.endswith("pyraxis-companion-distant.json"))

    def test_written_frames_match_the_identities(self):
        for f in dc.DRAGONS.glob("*.json"):
            ident = json.loads(f.read_text(encoding="utf-8"))
            (fp, full), _ = dc.frames(f.stem, ident)
            on_disk = json.loads((dc.ROOT / fp).read_text(encoding="utf-8"))
            self.assertEqual(on_disk["description"], full["description"], f"{f.stem}: run tools/art/dragon_companions.py --apply")


if __name__ == "__main__":
    unittest.main()
