#!/usr/bin/env python3
"""Focused tests for the fully-clothed Deluxe bedroom audition cards."""
import json
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import gen_prompt as gp  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[2]
CARD_DIR = pathlib.Path("data/art/_sets/angel-primes/alpha/female/0_Edit/deluxe")
EXPECTED = {
    "female-edit-deluxe-clothed-seated.json": "Female_Edit_Deluxe_Clothed_Seated.txt",
    "female-edit-deluxe-clothed-reclining.json": "Female_Edit_Deluxe_Clothed_Relaxing.txt",
    "female-edit-deluxe-clothed-side-resting.json": "Female_Edit_Deluxe_Clothed_Side_Resting.txt",
    "female-edit-deluxe-clothed-resting.json": "Female_Edit_Deluxe_Clothed_Resting.txt",
}
PRESERVATION_COMPONENTS = {
    "face_policy": "data/art/edits/policies/face-preserve.json",
    "hair_policy": "data/art/edits/policies/hair-preserve.json",
    "body_policy": "data/art/edits/policies/body-preserve.json",
    "clothing_policy": "data/art/edits/policies/clothing-preserve.json",
    "framing": "data/art/edits/policies/framing-full-length.json",
}


class DeluxeReferenceTests(unittest.TestCase):
    def test_exactly_four_neutral_bedroom_cards_use_shared_edit_controls(self):
        paths = sorted((ROOT / CARD_DIR).glob("*.json"))
        self.assertEqual({path.name for path in paths}, set(EXPECTED))
        views = set()

        for path in paths:
            card = json.loads(path.read_text(encoding="utf-8"))
            relative = path.relative_to(ROOT).as_posix()
            with self.subTest(card=card["artId"]):
                self.assertEqual(card["stage"], "edit")
                self.assertEqual(card["template"], "data/art/_templates/heroes/0_Edit/edit-reference-human.txt")
                self.assertEqual(
                    card["output"],
                    f"prompts/angel-primes/alpha/Female/0_Edit/deluxe/{EXPECTED[path.name]}",
                )
                self.assertEqual(card["components"]["edit_task"], "data/art/edits/deluxe/bedroom-clothed.json")
                for component, reference in PRESERVATION_COMPONENTS.items():
                    self.assertEqual(card["components"][component], reference)
                self.assertEqual(
                    card["components"]["background"],
                    "data/art/backgrounds/modern/bedroom-soft-neutral.json",
                )
                views.add(card["components"]["view"])

                tokens = gp.generate(relative, tokens_only=True)
                template = (ROOT / card["template"]).read_text(encoding="utf-8")
                required = set(re.findall(r"{{(\w+)}}", template))
                self.assertEqual(required - tokens.keys(), set())
                self.assertEqual(tokens["DENOISE"], card["denoise"])
                self.assertIn("fully clothed", tokens["EDIT_TASK"])
                self.assertIn("same outfit", tokens["CLOTHING_POLICY"])
                self.assertIn("bedroom", tokens["BACKGROUND"])
                self.assertTrue(tokens["VIEW"])

        self.assertEqual(
            views,
            {
                "data/art/studio/views/body/deluxe-seated-upright.json",
                "data/art/studio/views/body/deluxe-relaxed-recline.json",
                "data/art/studio/views/body/deluxe-side-resting.json",
                "data/art/studio/views/body/deluxe-supine-resting.json",
            },
        )

    def test_deluxe_task_is_tagged_and_limits_source_inheritance_to_scene(self):
        task = json.loads((ROOT / "data/art/edits/deluxe/bedroom-clothed.json").read_text(encoding="utf-8"))
        self.assertEqual(task["sourceVariant"], "0d_Deluxe")
        self.assertIn("deluxe", task["tags"])
        self.assertIn("fully clothed", task["description"])
        self.assertIn("same outfit", task["description"])
        self.assertIn("bedroom setting", task["notes"])
        self.assertIn("original pose and wardrobe directions are intentionally excluded", task["notes"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
