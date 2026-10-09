#!/usr/bin/env python3
"""The originals tool: names follow the folder, copies are scaled, copies of removed originals are archived. Run: python tools/art/test_originals.py"""
import contextlib
import io
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
try:
    from PIL import Image
except ImportError:  # the tool itself says: pip install pillow
    Image = None
import originals  # noqa: E402
import comfy_workflows as cw  # noqa: E402

CFG = {"standardSize": [94, 110], "photos": {}, "workspaces": {}}


def jpeg(path, size=(60, 30), orientation=None):
    img = Image.new("RGB", size, (0, 0, 255))
    if orientation:
        exif = Image.Exif()
        exif[0x0112] = orientation
        img.save(path, "JPEG", exif=exif)
    else:
        img.save(path, "JPEG")


@unittest.skipIf(Image is None, "Pillow is not installed")
class OriginalsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.lib = self.tmp / "lib"
        for r in ("Angels", "Prospects"):
            (self.lib / r).mkdir(parents=True)
        self.patch = mock.patch.object(cw, "load_cfg", lambda: CFG)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def gallery(self, root, name):
        g = self.lib / root / name / "gallery"
        g.mkdir(parents=True, exist_ok=True)
        return g

    def run_tool(self, *args, apply=True):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            originals.main([*(["--apply"] if apply else []), "--root", str(self.lib), "--no-repoint", *args])
        return out.getvalue()

    def names(self, root, name, sub="gallery_94x110"):
        d = self.lib / root / name / sub
        return sorted(p.name for p in d.iterdir()) if d.is_dir() else []

    def test_names_follow_the_folder(self):
        self.assertEqual(originals.standard_name("facebook_17000_123.jpeg", "angelica"), "angelica_image_123.jpg")
        self.assertEqual(originals.standard_name("various_image_123.JPG", "angelica"), "angelica_image_123.jpg")
        self.assertEqual(originals.standard_name("Screenshot_20260922_114223_Facebook.png", "remiah"), "remiah_screenshot_20260922_114223.png")
        self.assertEqual(originals.standard_name("various_screenshot_20260922_114223.jpg", "remiah"), "remiah_screenshot_20260922_114223.jpg")
        self.assertEqual(originals.standard_name("Draknara Face Left.png", "draknara"), "draknara_face_left.png")
        self.assertEqual(originals.standard_name("Some Walk.png", "drakness"), "drakness_some_walk.png")
        self.assertEqual(originals.standard_name("Some Pose.png", "drakness"), "drakness_pose.png")
        self.assertEqual(originals.standard_name("drakneta_screenshot_20260918_101800_facebook.jpg", "drakneta"), "drakneta_screenshot_20260918_101800_facebook.jpg")

    def test_a_preview_changes_nothing(self):
        jpeg(self.gallery("Prospects", "Various") / "various_image_1.jpg")
        out = self.run_tool(apply=False)
        self.assertIn("preview", out)
        self.assertEqual(self.names("Prospects", "Various", "gallery"), ["various_image_1.jpg"])
        self.assertEqual(self.names("Prospects", "Various"), [])

    def test_a_moved_original_is_renamed_for_its_new_folder_and_its_old_copy_archived(self):
        src = self.gallery("Prospects", "Various") / "various_image_7.jpg"
        jpeg(src)
        self.run_tool()
        self.assertEqual(self.names("Prospects", "Various"), ["various_image_7_94x110.png"])
        shutil.move(src, self.gallery("Angels", "Angelica") / src.name)
        self.run_tool()
        self.assertEqual(self.names("Angels", "Angelica", "gallery"), ["angelica_image_7.jpg"])
        self.assertEqual(self.names("Angels", "Angelica"), ["angelica_image_7_94x110.png"])
        self.assertEqual(self.names("Prospects", "Various"), [], "the old copy is pruned")
        self.assertEqual(self.names("Prospects", "Various", "gallery_94x110_org"), ["various_image_7_94x110.png"], "and archived, not deleted")

    def test_a_removed_original_prunes_its_copy_and_other_files_stay(self):
        g = self.gallery("Angels", "Angelica")
        jpeg(g / "angelica_image_1.jpg")
        jpeg(g / "angelica_image_2.jpg")
        self.run_tool()
        out_dir = self.lib / "Angels" / "Angelica" / "gallery_94x110"
        (out_dir / "notes.txt").write_text("keep", encoding="utf-8")
        (g / "angelica_image_2.jpg").unlink()
        self.run_tool()
        self.assertEqual(self.names("Angels", "Angelica"), ["angelica_image_1_94x110.png", "notes.txt"])
        self.assertEqual(self.names("Angels", "Angelica", "gallery_94x110_org"), ["angelica_image_2_94x110.png"])

    def test_an_emptied_gallery_archives_its_copies(self):
        g = self.gallery("Angels", "Angelica")
        jpeg(g / "angelica_image_1.jpg")
        self.run_tool()
        (g / "angelica_image_1.jpg").unlink()
        self.run_tool()
        self.assertEqual(self.names("Angels", "Angelica"), [])
        self.assertEqual(self.names("Angels", "Angelica", "gallery_94x110_org"), ["angelica_image_1_94x110.png"])

    def test_a_folder_without_a_gallery_is_left_alone(self):
        (self.lib / "Angels" / "Angelica" / "gallery_94x110").mkdir(parents=True)
        (self.lib / "Angels" / "Angelica" / "gallery_94x110" / "angelica_image_1_94x110.png").write_bytes(b"x")
        self.run_tool()
        self.assertEqual(self.names("Angels", "Angelica"), ["angelica_image_1_94x110.png"])

    def test_two_files_for_one_name_are_reported_not_overwritten(self):
        g = self.gallery("Angels", "Angelica")
        jpeg(g / "Foo Bar.jpg")
        jpeg(g / "angelica_foo_bar.jpg")
        out = self.run_tool()
        self.assertIn("already used", out)
        self.assertEqual(self.names("Angels", "Angelica", "gallery"), ["Foo Bar.jpg", "angelica_foo_bar.jpg"])

    def test_the_copy_is_the_standard_size_shape_kept_and_a_second_run_changes_nothing(self):
        jpeg(self.gallery("Angels", "Angelica") / "angelica_image_1.jpg", (60, 30))
        self.run_tool()
        png = self.lib / "Angels" / "Angelica" / "gallery_94x110" / "angelica_image_1_94x110.png"
        with Image.open(png) as im:
            self.assertEqual(im.size, (94, 110))
            self.assertEqual(im.getpixel((2, 2)), originals.CREAM, "letterboxed on cream")
            blue = im.getpixel((47, 55))  # JPEG is lossy: close to pure blue
            self.assertTrue(blue[0] < 5 and blue[1] < 5 and blue[2] > 250, blue)
        again = self.run_tool()
        self.assertIn("0 made", again)
        self.assertIn("0 renamed", again)

    def test_exif_rotation_is_applied(self):
        jpeg(self.gallery("Angels", "Angelica") / "angelica_image_1.jpg", (60, 30), orientation=6)  # 60x30 turned to 30x60
        self.run_tool()
        png = self.lib / "Angels" / "Angelica" / "gallery_94x110" / "angelica_image_1_94x110.png"
        with Image.open(png) as im:
            self.assertEqual(im.getpixel((2, 55)), originals.CREAM, "upright: cream at the sides, not top and bottom")

    def test_only_limits_the_folders(self):
        jpeg(self.gallery("Angels", "Angelica") / "angelica_image_1.jpg")
        jpeg(self.gallery("Angels", "Remiah") / "remiah_image_1.jpg")
        self.run_tool("--only", "Remiah")
        self.assertEqual(self.names("Angels", "Angelica"), [])
        self.assertEqual(self.names("Angels", "Remiah"), ["remiah_image_1_94x110.png"])


if __name__ == "__main__":
    unittest.main()
