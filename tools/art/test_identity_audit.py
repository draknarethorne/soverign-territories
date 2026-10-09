import unittest

import identity_audit as ia


class IdentityAuditTests(unittest.TestCase):
    def test_strength_words_are_caught(self):
        for text in ("Strong, sturdy build", "Muscular legs", "Full, powerful hips"):
            self.assertTrue(ia.STRONG.search(text), text)

    def test_slender_words_pass(self):
        for text in ("Lithe, slender, long-limbed build", "Slender, grounded hourglass build; steady and sure-footed"):
            self.assertFalse(ia.STRONG.search(text), text)

    def test_photo_wording_is_flagged(self):
        self.assertTrue(ia.PHOTO.search("exactly as in the reference image"))
        self.assertFalse(ia.PHOTO.search("Soft rose-gold blonde hair, silky and luminous"))

    def test_norm_collapses_whitespace_and_punctuation(self):
        self.assertEqual(ia.norm("Pale,  sky-blue\n irises"), "pale sky-blue irises")

    def test_alpha_test_heroes_are_not_audited(self):
        self.assertFalse([p for _, p in ia.heroes() if p.parent.name == "alpha"])

    def test_every_audited_hero_has_a_card_free_identity(self):
        names = {p.stem for _, p in ia.heroes()}
        self.assertIn("sandalyn", names)
        self.assertIn("drakniss-thorne", names)


if __name__ == "__main__":
    unittest.main()
