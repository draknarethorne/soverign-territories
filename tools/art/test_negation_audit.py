"""Tests for negation_audit.py: what counts as a negation in a positive prompt, and what is left alone."""
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import negation_audit as na  # noqa: E402

RULES = {
    "command": [r"\b(?:do not|does not|don't|never|avoid)\b"],
    "flip": [r"\bnot (?:glowing|squinting|recolou?red)\b", r"\bno (?:pale areas|squint|breeze)\b"],
    "review": r"\b(?:no|not|nothing|without)\b",
    "allow": [{"paths": "prompts/*_Video_*", "why": "video"}],
}


class PositivePartTests(unittest.TestCase):
    def test_only_the_positive_prompt_is_read(self):
        text = "=== header: do not repeat ===\nIncoming image.\n\nprompt:\nKeep her eyes.\n\nnegative prompt:\nblue eyes, no text"
        body = na.positive_part(text)
        self.assertIn("Keep her eyes", body)
        self.assertNotIn("do not repeat", body)
        self.assertNotIn("blue eyes", body)

    def test_a_file_without_a_prompt_marker_is_skipped(self):
        self.assertEqual(na.positive_part("just notes"), "")


class PhraseTests(unittest.TestCase):
    def test_a_phrase_is_the_match_and_the_rest_of_its_clause(self):
        line = "natural eyes - do not recolour at the rim, iris visible"
        m = re.search(RULES["command"][0], line) or re.search(r"do not", line)
        self.assertEqual(na.phrase_of(line, re.search(r"do not", line)), "do not recolour at the rim")

    def test_allowlist_matches_by_path(self):
        self.assertEqual(na.allowed_by("prompts/drakn-sisters/X/X_Video_Scene_Dawn.txt", RULES["allow"]), "video")
        self.assertIsNone(na.allowed_by("prompts/drakn-sisters/X/X_Scene_Dawn.txt", RULES["allow"]))


class RepoSettingsTests(unittest.TestCase):
    """The shipped rules catch the phrases they were written for and let a positive sentence through."""

    def setUp(self):
        import json
        rules = json.loads(na.SETTINGS.read_text(encoding="utf-8"))
        self.command = [re.compile(p, re.I) for p in rules["command"]]
        self.flip = [re.compile(p, re.I) for p in rules["flip"]]

    def hits(self, text):
        return [r.pattern for r in self.command + self.flip if r.search(text)]

    def test_known_flip_phrases_are_caught(self):
        for text in ("do not recolour", "Do not alter undertone", "eyes, not glowing", "wide open, not squinting", "evenly tanned, no pale areas", "held high rather than drooping",
                     "Change nothing else: keep", "no gap between them", "never hidden or flattened", "nothing from the modern world"):
            self.assertTrue(self.hits(text), text)

    def test_a_positive_sentence_is_clean(self):
        for text in ("natural eye colour from the reference image, clarified with crisp definition", "Keep the face, expression and the pose",
                     "held firm and high, the inner curves meeting at the centre line", "evenly tanned, natural studio eyes, both eyes wide open"):
            self.assertFalse(self.hits(text), text)


if __name__ == "__main__":
    unittest.main()
