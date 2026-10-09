#!/usr/bin/env python3
"""The stage templates must keep the standard image size: no unlinked resize-to-total-pixels node may target anything but the standard megapixels. Run: python tools/workflows/test_templates.py"""
import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402


class TemplateSizeTests(unittest.TestCase):
    def test_every_template_targets_the_standard_size(self):
        cfg = cw.load_cfg()
        bad = []
        for p in sorted((cw.WF / "_templates").glob("ST*.json")):
            if cw.align_size(copy.deepcopy(cw.read_wf(p)), cfg):
                bad.append(p.name)
        self.assertEqual(bad, [], "run: python tools/workflows/align_templates.py --apply   (then make, and deploy)")

    def test_a_944x1104_image_comes_out_944x1104(self):
        cfg = cw.load_cfg()
        w, h = cfg["standardSize"]
        mp = cw.standard_megapixels(cfg)
        scale = (int(mp * 1024 * 1024) / (w * h)) ** 0.5  # ComfyUI counts a megapixel as 1024 x 1024
        self.assertEqual((round(w * scale), round(h * scale)), (w, h))
        self.assertEqual((round(w * scale / 16) * 16, round(h * scale / 16) * 16), (w, h))
        self.assertEqual(w % 16, 0)
        self.assertEqual(h % 16, 0)

    def test_align_size_fixes_a_node_left_at_one_megapixel_and_is_idempotent(self):
        cfg = {"standardSize": [944, 1104]}
        node = {"type": "ImageScaleToTotalPixels", "widgets_values": ["area", 1, 1], "widgets_values_named": {"megapixels": 1, "resolution_steps": 1}, "inputs": [{"name": "megapixels", "link": None}]}
        wf = {"definitions": {"subgraphs": [{"nodes": [node]}]}}
        self.assertTrue(cw.align_size(wf, cfg))
        self.assertEqual((node["widgets_values"][1], node["widgets_values"][2], node["widgets_values_named"]["megapixels"]), (0.993896, 16, 0.993896))
        self.assertFalse(cw.align_size(wf, cfg))

    def test_a_node_driven_by_another_node_is_left_alone(self):
        cfg = {"standardSize": [944, 1104]}
        node = {"type": "ImageScaleToTotalPixels", "widgets_values": ["nearest-exact", 1, 16], "inputs": [{"name": "megapixels", "link": 58}]}
        wf = {"definitions": {"subgraphs": [{"nodes": [node]}]}}
        self.assertFalse(cw.align_size(wf, cfg))
        self.assertEqual(node["widgets_values"][1], 1)


if __name__ == "__main__":
    unittest.main()
