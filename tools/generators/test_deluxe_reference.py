#!/usr/bin/env python3
"""Focused tests for the Deluxe bedroom audition cards."""
import json
import pathlib
import re
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import gen_prompt as gp  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[2]
CARD_DIR = pathlib.Path("data/art/_sets/sovereign-females/female/0_Edit/deluxe")
EXPECTED = {
    "female-edit-deluxe-seated.json": ("Female_Edit_Deluxe_Seated.txt", "~1.0"),
    "female-edit-deluxe-reclining.json": ("Female_Edit_Deluxe_Relaxed_Recline.txt", "~0.9"),
    "female-edit-deluxe-side-resting.json": ("Female_Edit_Deluxe_Side_Resting.txt", "~1.0"),
    "female-edit-deluxe-resting.json": ("Female_Edit_Deluxe_Resting.txt", "~0.9"),
}
PRESERVATION_COMPONENTS = {
    "face_policy": "data/art/edits/policies/face-preserve.json",
    "likeness": "data/art/edits/policies/face-preserve.json",
    "hair_policy": "data/art/edits/policies/hair-preserve.json",
    "camera": "data/art/edits/policies/framing-full-length.json",
}


class DeluxeReferenceTests(unittest.TestCase):
    def test_original_neutral_bedroom_cards_use_shared_edit_controls(self):
        paths = [ROOT / CARD_DIR / name for name in sorted(EXPECTED)]
        self.assertTrue(all(path.is_file() for path in paths))
        views = set()

        for path in paths:
            card = json.loads(path.read_text(encoding="utf-8"))
            relative = path.relative_to(ROOT).as_posix()
            with self.subTest(card=card["artId"]):
                self.assertEqual(card["artId"], path.stem)
                self.assertEqual(card["stage"], "edit")
                self.assertEqual(card["template"], "data/art/_templates/heroes/0_Edit/edit-cleanup-human.txt")
                self.assertEqual(
                    card["output"],
                    f"prompts/sovereign-females/Female/0_Edit/deluxe/{EXPECTED[path.name][0]}",
                )
                self.assertEqual(card["denoise"], EXPECTED[path.name][1])
                self.assertEqual(card["components"]["edit_task"], "data/art/edits/deluxe/bedroom-pose.json")
                for component, reference in PRESERVATION_COMPONENTS.items():
                    self.assertEqual(card["components"][component], reference)
                self.assertNotIn("wearing", card["components"])
                self.assertEqual(
                    card["components"]["background"],
                    "data/art/backgrounds/modern/bedroom-neutral.json",
                )
                self.assertEqual(card["components"]["lighting"], "data/art/studio/lighting/neutral-frontal.json")
                views.add(card["components"]["view"])

                tokens = gp.generate(relative, tokens_only=True)
                template = (ROOT / card["template"]).read_text(encoding="utf-8")
                required = set(re.findall(r"{{(\w+)}}", gp.apply_optional_lines(template, tokens)))
                self.assertEqual(required - tokens.keys(), set())
                self.assertEqual(tokens["DENOISE"], card["denoise"])
                self.assertIn("bedroom", tokens["BACKGROUND"])
                self.assertTrue(tokens["VIEW"])

                with mock.patch.object(pathlib.Path, "mkdir"), \
                     mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                     mock.patch("builtins.print"):
                    gp.generate(relative)
                prompt = write.call_args.args[1]
                positive, negative = prompt.split("negative prompt:", 1)
                self.assertIn("Retain existing jewelry", positive)
                self.assertIn("Remove props and non-jewelry accessories", positive)
                self.assertNotIn("Remove jewelry", positive)
                self.assertIn("Bust: A full, naturally rounded bust", positive)
                self.assertIn("Body: A slender frame", positive)
                self.assertNotIn("reshaped body", negative)
                self.assertNotIn("fully clothed", positive.lower())
                self.assertNotIn("Clothing:", positive)
                self.assertNotIn("Wearing:", positive)
                self.assertNotIn("same outfit", positive.lower())
                self.assertNotIn("changed clothing", negative)
                labels = ("Pose:", "Background:", "Lighting:", "Camera:",
                          "Edit the incoming image:", "Result:", "Bust:", "Body:", "Likeness:", "Hair:")
                positions = [positive.index(label) for label in labels]
                self.assertEqual(positions, sorted(positions))
                self.assertEqual(positive.count("Preserve the same person's recognizable face"), 2)
                self.assertIn("synthesized, not recovered from the original", positive)
                self.assertIn("frontal studio lighting with a flat, clean key light", positive)
                self.assertNotIn("dramatic lighting", negative)
                self.assertIn("changed identity", negative)
                has_heels = path.name in {
                    "female-edit-deluxe-seated.json",
                    "female-edit-deluxe-reclining.json",
                }
                self.assertEqual("Footwear: high-heeled shoes" in positive, has_heels)

        self.assertEqual(
            views,
            {
                "data/art/studio/views/body/deluxe-seated-upright.json",
                "data/art/studio/views/body/deluxe-relaxed-recline.json",
                "data/art/studio/views/body/deluxe-side-resting.json",
                "data/art/studio/views/body/deluxe-supine-resting.json",
            },
        )

    def test_source_inspired_deluxe_auditions_use_high_angle_without_level_conflict(self):
        for variant, cue, heels in (
            ("side-propped", "support the upper body on one elbow", False),
            ("relaxed-edge", "let one leg hang over the side", True),
            ("resting-propped", "angle one leg toward the camera", False),
            ("seated-edge", "sit near the edge of the bed", True),
        ):
            path = CARD_DIR / f"female-edit-deluxe-{variant}-audition.json"
            with self.subTest(variant=variant), \
                 mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
            positive, negative = write.call_args.args[1].split("negative prompt:", 1)
            self.assertIn(cue, positive.lower())
            self.assertIn("above the subject and angle it downward", positive)
            self.assertIn("wide environmental film still", positive)
            self.assertIn("frontal studio lighting with a flat, clean key light", positive)
            self.assertNotIn("camera level", positive.lower())
            self.assertIn("Retain existing jewelry", positive)
            self.assertNotIn("Wearing:", positive)
            self.assertEqual("Footwear: high-heeled shoes" in positive, heels)
            self.assertNotIn("{{", positive + negative)

    def test_named_source_inspired_deluxe_uses_each_character_frame(self):
        roots = (
            ROOT / "data/art/_sets/angel-primes/female",
            ROOT / "data/art/_sets/angel-primes/male",
            ROOT / "data/art/_sets/drakn-sisters",
        )
        variants = (
            ("side-propped", "support the upper body on one elbow", False),
            ("relaxed-edge", "let one leg hang over the side", True),
            ("resting-propped", "angle one leg toward the camera", False),
            ("seated-edge", "sit near the edge of the bed", True),
        )
        for root in roots:
            for seed in root.rglob("*-edit-deluxe-seated.json"):
                slug = seed.name.removesuffix("-edit-deluxe-seated.json")
                for variant, cue, heels in variants:
                    path = seed.with_name(f"{slug}-edit-deluxe-{variant}-audition.json")
                    card = json.loads(path.read_text(encoding="utf-8"))
                    identity = gp.load_identity(card["heroArt"])
                    frame = gp.tokens_for(identity, ["hair", "eyes", "skin"])["FIGURE_FRAME"]
                    with self.subTest(card=card["artId"]), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(path.relative_to(ROOT))
                    positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                    self.assertIn(frame, positive)
                    self.assertIn(cue, positive.lower())
                    self.assertIn("above the subject and angle it downward", positive)
                    self.assertIn("wide environmental film still", positive)
                    self.assertIn("frontal studio lighting with a flat, clean key light", positive)
                    self.assertNotIn("Wearing:", positive)
                    self.assertEqual("Footwear: high-heeled shoes" in positive, heels)
                    self.assertNotIn("{{", positive + negative)
                    if "male" in root.parts:
                        self.assertNotIn("Bust:", positive)

    def test_original_named_deluxe_uses_character_frame_and_source_light(self):
        roots = (
            ROOT / "data/art/_sets/angel-primes/female",
            ROOT / "data/art/_sets/angel-primes/male",
            ROOT / "data/art/_sets/drakn-sisters",
        )
        for root in roots:
            for seed in root.rglob("*-edit-deluxe-seated.json"):
                slug = seed.name.removesuffix("-edit-deluxe-seated.json")
                for variant in ("reclining", "resting", "seated", "side-resting"):
                    path = seed.with_name(f"{slug}-edit-deluxe-{variant}.json")
                    card = json.loads(path.read_text(encoding="utf-8"))
                    frame = gp.tokens_for(gp.load_identity(card["heroArt"]), ["hair", "eyes", "skin"])["FIGURE_FRAME"]
                    with self.subTest(card=card["artId"]), \
                         mock.patch.object(pathlib.Path, "mkdir"), \
                         mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                         mock.patch("builtins.print"):
                        gp.generate(path.relative_to(ROOT))
                    positive, negative = write.call_args.args[1].split("negative prompt:", 1)
                    self.assertIn(frame, positive)
                    self.assertIn("frontal studio lighting with a flat, clean key light", positive)
                    self.assertNotIn("dramatic lighting", negative)
                    self.assertNotIn("Wearing:", positive)
                    self.assertNotIn("{{", positive + negative)

    def test_deluxe_can_explicitly_select_a_wearing_piece(self):
        source = ROOT / CARD_DIR / "female-edit-deluxe-seated.json"
        card = json.loads(source.read_text(encoding="utf-8"))
        card["components"]["wearing"] = "data/art/reference/wardrobe/existing-fitted.json"
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as tmp:
            path = pathlib.Path(tmp) / "card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with mock.patch.object(pathlib.Path, "mkdir"), \
                 mock.patch.object(pathlib.Path, "write_text", autospec=True) as write, \
                 mock.patch("builtins.print"):
                gp.generate(path)
        positive, _ = write.call_args.args[1].split("negative prompt:", 1)
        self.assertIn("Wearing: Keep the existing outfit with a fitted silhouette", positive)
        self.assertNotIn("fully clothed", positive.lower())


if __name__ == "__main__":
    unittest.main(verbosity=1)
