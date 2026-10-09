#!/usr/bin/env python3
"""The MiniMax video templates: consistent links, the canvas follows the still, nothing is stretched. Run: python tools/workflows/test_video_templates.py"""
import copy
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402
import video_templates as vt  # noqa: E402

CFG = cw.load_cfg()
PROMPT = "=== X ===\nSource image: a.png\nFormat: {fmt}\nLength: 8\n\n----\nprompt:\n\nx\n"


def wf(key):
    return vt.read(vt.OUT / vt.NAMES[key])


def named(w):
    o = vt.outer(w)
    return dict(zip(o["widgets_values_named"], o["widgets_values"]))


class VideoTemplateTests(unittest.TestCase):
    def test_links_are_consistent(self):
        for key in vt.NAMES:
            self.assertEqual(vt.check_links(wf(key)), [], key)
        self.assertEqual(vt.check_links(vt.read(vt.LEGACY)), [])

    def test_the_checker_catches_a_broken_link(self):
        w = wf("reel")
        w["links"].append([99, 10, 0, 20, 0, "IMAGE"])
        self.assertTrue(vt.check_links(w))

    def test_shipped_templates_match_the_builder(self):
        legacy = vt.read(vt.LEGACY)
        self.assertEqual(wf("reel"), {**vt.build_reel(legacy), "id": "st6-minimax-reel"})
        self.assertEqual(wf("match"), {**vt.build_match(legacy), "id": "st6-minimax-match"})

    def test_reel_canvas_is_9_16_in_steps_of_32(self):
        w = wf("reel")
        sel = vt.node(w, "ResolutionSelector")
        aspect, mp, step = sel["widgets_values"]
        scale = math.sqrt(mp * 1024 * 1024 / (9 * 16))
        self.assertEqual((round(9 * scale / step) * step, round(16 * scale / step) * step), (640, 1152))
        self.assertEqual(vt.node(w, "ImageScale")["widgets_values"][3], "center")  # cover-crop, never a stretch

    def test_match_canvas_follows_the_still(self):
        mp, step = vt.MATCH["megapixels"], vt.MATCH["step"]
        scale = math.sqrt(mp * 1024 * 1024 / (944 * 1104))
        w, h = round(944 * scale / step) * step, round(1104 * scale / step) * step
        self.assertEqual((w, h), (928, 1088))
        self.assertLess(abs(w / h - 944 / 1104), 0.005)

    def test_the_frame_the_model_gets_is_the_frame_whose_size_is_the_canvas(self):
        for key, kind in (("reel", "ImageScale"), ("match", "ImageScaleToTotalPixels")):
            w = wf(key)
            o, scaler = vt.outer(w), vt.node(w, kind)
            first = next(l for l in w["links"] if l[3] == o["id"] and l[4] == vt.slot(o, "first_frame"))
            self.assertEqual(first[1], scaler["id"], key)
            for name in ("width", "height"):
                self.assertIsNotNone(o["inputs"][vt.slot(o, name)]["link"], f"{key} {name} must be wired")

    def test_defaults(self):
        for key in vt.NAMES:
            n = named(wf(key))
            self.assertEqual((n["value_1"], n["value"], n["value_2"]), (8, True, 8))
            self.assertTrue(n["vae_name"].startswith("minimax_h3_video_vae"))

    def test_format_picks_the_template(self):
        self.assertTrue(cw.video_template(CFG, PROMPT.format(fmt="match")).endswith("ST6_MiniMax_Match.json"))
        self.assertTrue(cw.video_template(CFG, PROMPT.format(fmt="reel")).endswith("ST6_MiniMax_Reel.json"))
        self.assertTrue(cw.video_template(CFG, "no header here").endswith("ST6_MiniMax_Reel.json"))
        with self.assertRaises(SystemExit):
            cw.video_template(CFG, PROMPT.format(fmt="square"))

    def test_set_video_sets_length_and_turbo_but_leaves_wired_sizes_alone(self):
        for key in vt.NAMES:
            w = copy.deepcopy(wf(key))
            before = named(w)
            text = PROMPT.format(fmt=key).replace("Format", "Size: 111x222\nFormat").replace("Length: 8", "Length: 7.5")
            src = cw.set_video(w, text, {"turbo": False})
            after = named(w)
            self.assertEqual((after["width"], after["height"]), (before["width"], before["height"]), key)
            self.assertEqual((after["value_1"], after["value"]), (7.5, False))
            self.assertEqual(src, "a.png")

    def test_every_template_named_in_config_exists(self):
        for rel in CFG["engines"]["minimax"]["templates"].values():
            self.assertTrue((cw.ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
