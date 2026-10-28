"""Synthetic checks for the profile-driven overlay patterns (frames, badges, watermarks)."""
import sys
import pathlib
import unittest

import cv2
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from intake_library import overlays  # noqa: E402


def photo(width, height, seed=1):
    """Mid-tone textured picture: no pure white, no pure black rows."""
    rng = np.random.default_rng(seed)
    base = np.zeros((height, width, 3), dtype=np.uint8)
    base[..., 0] = np.linspace(90, 150, width, dtype=np.uint8)[None, :]
    base[..., 1] = np.linspace(80, 130, height, dtype=np.uint8)[:, None]
    base[..., 2] = 100
    return np.clip(base.astype(np.int16) + rng.integers(-12, 12, base.shape), 40, 190).astype(np.uint8)


class ReelFrameTest(unittest.TestCase):
    def test_full_bleed_reel_bottom_panel(self):
        array = photo(540, 1170)
        array[1100:] = 0
        frame = overlays.reel_frame(array)
        self.assertIsNotNone(frame)
        self.assertEqual(frame["layout"], "full-bleed")
        self.assertEqual(frame["pictureBox"][3], 1100)
        self.assertIsNotNone(frame["statusBand"])

    def test_boxed_reel_top_panel(self):
        array = photo(540, 1170)
        array[:80] = 0
        array[1100:] = 0
        frame = overlays.reel_frame(array)
        self.assertEqual(frame["layout"], "boxed")
        self.assertGreaterEqual(frame["pictureBox"][1], 78)

    def test_ordinary_photo_is_not_a_reel(self):
        self.assertIsNone(overlays.reel_frame(photo(800, 1000)))
        self.assertIsNone(overlays.reel_frame(photo(540, 1170)))  # tall, but no bottom UI


class BadgeTest(unittest.TestCase):
    @staticmethod
    def canvas():
        array = np.full((800, 800, 3), 45, dtype=np.uint8)
        return array

    def test_ring_with_lettering_is_confirmed(self):
        array = self.canvas()
        cv2.circle(array, (400, 400), 90, (235, 40, 170), 14)
        cv2.putText(array, "GMW", (325, 425), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (215, 215, 215), 7)
        found = overlays.badges(array)
        self.assertEqual(len(found), 1)
        cx, cy, radius = found[0]["confirmation"]["circle"]
        self.assertLess(abs(cx - 400) + abs(cy - 400), 20)
        self.assertTrue(found[0]["mask"][400, 400])

    def test_filled_magenta_shape_is_refused(self):
        array = self.canvas()
        cv2.circle(array, (400, 400), 90, (235, 40, 170), cv2.FILLED)
        self.assertEqual(overlays.badges(array), [])

    def test_ring_without_lettering_is_refused(self):
        array = self.canvas()
        cv2.circle(array, (400, 400), 90, (235, 40, 170), 14)
        self.assertEqual(overlays.badges(array), [])


class WatermarkTest(unittest.TestCase):
    def test_corner_text_line_is_found(self):
        array = photo(1550, 2048)
        cv2.putText(array, "Dola AI", (1290, 1960), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (250, 250, 250), 3)
        found = overlays.watermarks(array)
        self.assertEqual(len(found), 1)
        x0, y0, x1, y1 = found[0]["box"]
        self.assertTrue(x0 <= 1290 and x1 >= 1420 and y0 <= 1935 and y1 >= 1960)
        self.assertEqual(found[0]["pattern"], "corner-text")

    def test_clean_and_edge_highlight_are_ignored(self):
        array = photo(1550, 2048)
        self.assertEqual(overlays.watermarks(array), [])
        array[2030:, 100:240] = 245  # a bright highlight touching the bottom edge
        self.assertEqual(overlays.watermarks(array), [])

    def test_stacked_caption_grows_into_one_block(self):
        array = photo(1024, 1536)
        for y, text in ((1260, "Grateful for today,"), (1300, "excited for next."), (1360, "x Aria")):
            size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, .8, 2)[0][0]
            cv2.putText(array, text, (300 - size // 2, y), cv2.FONT_HERSHEY_SIMPLEX, .8, (250, 250, 250), 2)
        found = overlays.watermarks(array)
        self.assertEqual(len(found), 1)
        self.assertIn("caption block", found[0]["reason"])
        self.assertLessEqual(found[0]["box"][1], 1240)

    def test_tiny_bright_specks_are_not_text(self):
        array = photo(1152, 2048)
        for x in range(280, 340, 12):  # pile-like specks, 9 px tall
            array[1835:1844, x:x + 3] = 250
        self.assertEqual(overlays.watermarks(array), [])


class SparkleTest(unittest.TestCase):
    @staticmethod
    def star(array, cx, cy, r):
        points = []
        for i in range(8):
            angle = np.pi / 4 * i - np.pi / 2
            radius = r if i % 2 == 0 else r * .45
            points.append([cx + radius * np.cos(angle), cy + radius * np.sin(angle)])
        cv2.fillPoly(array, [np.round(points).astype(np.int32)], (225, 222, 218))

    def test_corner_sparkle_is_found(self):
        array = photo(1080, 1778)
        self.star(array, 900, 1625, 36)
        found = overlays.sparkles(array)
        self.assertEqual(len(found), 1)
        x0, y0, x1, y1 = found[0]["box"]
        self.assertTrue(x0 <= 864 and x1 >= 936 and y0 <= 1589 and y1 >= 1661)

    def test_round_highlight_is_not_a_sparkle(self):
        array = photo(1080, 1778)
        cv2.circle(array, (900, 1625), 36, (225, 222, 218), cv2.FILLED)
        self.assertEqual(overlays.sparkles(array), [])


class LetterboxTest(unittest.TestCase):
    def test_flat_dark_bars_with_sharp_edge(self):
        array = photo(937, 2048)
        array[:180] = np.linspace(13, 27, 180, dtype=np.uint8)[:, None, None]
        array[1870:] = 30
        self.assertEqual(overlays.letterbox(array), (180, 1870))

    def test_plain_photo_and_soft_dark_sky_have_no_letterbox(self):
        self.assertIsNone(overlays.letterbox(photo(937, 2048)))
        array = photo(937, 2048)
        array[:180] = 25
        array[180:260] = np.linspace(25, 100, 80, dtype=np.uint8)[:, None, None]  # soft gradient, no edge
        self.assertIsNone(overlays.letterbox(array))


def card(array, centre, size, angle, letters=True):
    """Draw a rotated flat pale card with dark lettering."""
    box = cv2.boxPoints((centre, size, angle)).astype(np.int32)
    cv2.fillPoly(array, [box], (200, 200, 200))
    if letters:
        cx, cy = centre
        for dx in range(-int(size[0] * .35), int(size[0] * .35), 18):
            cv2.rectangle(array, (int(cx + dx), int(cy - 8)), (int(cx + dx + 8), int(cy + 8)), (40, 40, 40), -1)
    return array


class TiltedStickerTest(unittest.TestCase):
    def test_rotated_lettered_card_is_found_with_a_polygon(self):
        array = card(photo(600, 1000), (450, 820), (220, 90), -30)
        found = overlays.tilted_stickers(array)
        self.assertEqual(len(found), 1)
        self.assertEqual(len(found[0]["polygon"]), 4)
        x0, y0, x1, y1 = found[0]["box"]
        self.assertTrue(x0 <= 380 and x1 >= 520 and y0 <= 780 and y1 >= 860)

    def test_upright_and_blank_cards_are_left_alone(self):
        self.assertEqual(overlays.tilted_stickers(card(photo(600, 1000), (300, 500), (200, 70), 0)), [])
        self.assertEqual(overlays.tilted_stickers(card(photo(600, 1000), (300, 500), (200, 70), -30, False)), [])


class ViewerIconsTest(unittest.TestCase):
    def test_close_x_and_menu_dots_in_top_corners(self):
        array = photo(1000, 1800)
        cv2.line(array, (40, 40), (78, 78), (255, 255, 255), 5)
        cv2.line(array, (78, 40), (40, 78), (255, 255, 255), 5)
        for x in (930, 950, 970):
            cv2.rectangle(array, (x, 60), (x + 8, 68), (255, 255, 255), -1)
        reasons = sorted(item["reason"] for item in overlays.viewer_icons(array))
        self.assertEqual(reasons, ["viewer-corner-icons close X", "viewer-corner-icons menu dots"])

    def test_white_plus_or_centre_marks_are_not_icons(self):
        array = photo(1000, 1800)
        cv2.line(array, (59, 40), (59, 78), (255, 255, 255), 5)
        cv2.line(array, (40, 59), (78, 59), (255, 255, 255), 5)
        for x in (480, 500, 520):
            cv2.rectangle(array, (x, 60), (x + 8, 68), (255, 255, 255), -1)
        self.assertEqual(overlays.viewer_icons(array), [])


class ReferenceLogoTest(unittest.TestCase):
    def test_stored_logo_is_found_at_another_scale_and_not_on_a_plain_photo(self):
        logo = cv2.cvtColor(cv2.imread(str(overlays.REFERENCES / "echoes-of-fantasia.png")), cv2.COLOR_BGR2RGB)
        logo = cv2.resize(logo, None, fx=.8, fy=.8, interpolation=cv2.INTER_AREA)
        array = photo(1092, 1640)
        h, w = logo.shape[:2]
        array[1400:1400 + h, 300:300 + w] = logo
        found = overlays.references(array)
        self.assertEqual(len(found), 1)
        x0, y0, x1, y1 = found[0]["box"]
        self.assertTrue(x0 <= 300 and y0 <= 1400 and x1 >= 300 + w and y1 >= 1400 + h)
        self.assertEqual(overlays.references(photo(1092, 1640)), [])


class BoxedReelBottomTest(unittest.TestCase):
    def test_tall_full_width_black_top_panel_runs_past_the_cap(self):
        array = photo(540, 1170)
        array[:165] = 0  # taller than maxHeight (12% = 140)
        array[1100:] = 0
        frame = overlays.reel_frame(array)
        self.assertEqual(frame["pictureBox"][1], 165)

    def test_caption_black_below_boxed_picture_is_excluded(self):
        array = photo(540, 1170)
        array[:140] = 0
        array[840:] = 0
        cv2.putText(array, "Felicia Lazar", (60, 900), cv2.FONT_HERSHEY_SIMPLEX, .7, (255, 255, 255), 2)
        array[1100:] = 235  # light nav bar
        frame = overlays.reel_frame(array)
        self.assertEqual(frame["layout"], "boxed")
        self.assertLessEqual(abs(frame["pictureBox"][3] - 840), 2)
        self.assertGreater(frame["uiBottom"], frame["pictureBox"][3])


if __name__ == "__main__":
    unittest.main()
