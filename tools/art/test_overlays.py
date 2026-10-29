"""Synthetic checks for the profile-driven overlay patterns (frames, badges, watermarks)."""
import sys
import pathlib
import unittest
from unittest import mock

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


class RGBBoundsTest(unittest.TestCase):
    def test_exact_signed_extrema_for_all_channel_values_and_strided_views(self):
        red, green = np.indices((256, 256), dtype=np.uint8)
        for blue in (0, 1, 127, 254, 255):
            image = np.stack((red, green, np.full_like(red, blue)), axis=2)
            for array in (image, image[::-1, ::2], image.transpose(1, 0, 2)):
                with self.subTest(blue=blue, strides=array.strides):
                    low, high = overlays.rgb_bounds(array)
                    np.testing.assert_array_equal(low, array.min(axis=2).astype(np.int16))
                    np.testing.assert_array_equal(high, array.max(axis=2).astype(np.int16))
                    self.assertEqual(low.dtype, np.dtype(np.int16))
                    self.assertEqual(high.dtype, np.dtype(np.int16))
                    self.assertTrue(np.all(high - low >= 0))

    def test_rendered_components_match_axis_reductions_with_contrast_and_vivid_edges(self):
        array = photo(360, 480)
        array[20:40, 20:80] = 255
        array[50:70, 30:90] = (255, 0, 0)
        rule = {
            "whiteMin": 220, "whiteChroma": 30, "contrastReach": .02,
            "darkEdge": 100, "plainWhiteMin": 230, "plainWhiteChroma": 20,
            "minArea": 2, "maxWidth": .8, "maxHeight": .8,
        }
        for contrast, vivid in ((False, None), (True, None), (True, 80)):
            with self.subTest(contrast=contrast, vivid=vivid):
                actual = overlays.rendered(array, [10, 10, 330, 470], rule,
                                           contrast=contrast, vivid=vivid)
                with mock.patch.object(overlays, "rgb_bounds", side_effect=lambda pixels: (
                        pixels.min(axis=2).astype(np.int16), pixels.max(axis=2).astype(np.int16))):
                    expected = overlays.rendered(array, [10, 10, 330, 470], rule,
                                                 contrast=contrast, vivid=vivid)
                self.assertEqual(actual, expected)


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

    def test_textured_dark_clothing_is_not_a_phone_navigation_panel(self):
        array = photo(540, 1170)
        rng = np.random.default_rng(42)
        cloth = rng.integers(5, 28, (140, 540, 1), dtype=np.uint8)
        array[1030:] = np.repeat(cloth, 3, axis=2)
        self.assertIsNone(overlays.reel_frame(array))

    def test_compressed_uniform_bottom_panel_still_qualifies(self):
        array = photo(540, 1170)
        rng = np.random.default_rng(42)
        array[1100:] = rng.integers(12, 16, (70, 540, 3), dtype=np.uint8)
        frame = overlays.reel_frame(array)
        self.assertIsNotNone(frame)
        self.assertEqual(frame["pictureBox"][3], 1100)


class OutlinedPillTest(unittest.TestCase):
    def test_paired_rounded_outline_survives_textured_transparent_background(self):
        array = photo(1080, 2340)
        cv2.line(array, (160, 132), (864, 132), (245, 245, 245), 2)
        cv2.line(array, (160, 238), (864, 238), (245, 245, 245), 2)
        cv2.ellipse(array, (160, 185), (53, 53), 0, 90, 270, (245, 245, 245), 2)
        cv2.ellipse(array, (864, 185), (53, 53), 0, -90, 90, (245, 245, 245), 2)
        found = overlays.outlined_pills(array, [0, 0, 1080, 280])
        self.assertEqual(len(found), 1)
        x0, y0, x1, y1 = found[0]
        self.assertLessEqual(x0, 107)
        self.assertLessEqual(y0, 131)
        self.assertGreaterEqual(x1, 917)
        self.assertGreaterEqual(y1, 239)
        frame = {"pictureBox": [0, 181, 1080, 1835], "uiBottom": 1872, "statusBand": None}
        with mock.patch.object(overlays.clutter, "bubbles", return_value=[]):
            parts = overlays.frame_parts(array, frame)
        pills = [part for part in parts if part["kind"] == "reel-search-pill"]
        self.assertEqual(len(pills), 1)
        self.assertLess(pills[0]["box"][1], frame["pictureBox"][1])

    def test_parallel_lines_or_rectangle_do_not_confirm_a_pill(self):
        for rectangle in (False, True):
            with self.subTest(rectangle=rectangle):
                array = photo(1080, 2340)
                cv2.line(array, (160, 132), (864, 132), (245, 245, 245), 2)
                cv2.line(array, (160, 238), (864, 238), (245, 245, 245), 2)
                if rectangle:
                    cv2.line(array, (160, 132), (160, 238), (245, 245, 245), 2)
                    cv2.line(array, (864, 132), (864, 238), (245, 245, 245), 2)
                self.assertEqual(overlays.outlined_pills(array, [0, 0, 1080, 280]), [])


class ReelAdditionalControlsTest(unittest.TestCase):
    @staticmethod
    def frame():
        return {"pictureBox": [0, 0, 1080, 2016], "uiBottom": 2016,
                "statusBand": [0, 0, 1080, 110]}

    def test_playback_requires_play_triangle_and_both_aligned_skip_rings(self):
        for rings in (0, 1, 2):
            with self.subTest(rings=rings):
                array = photo(1080, 2340)
                cv2.fillPoly(array, [np.array([[519, 981], [519, 1035], [568, 1008]])],
                             (255, 255, 255))
                for x in (330, 750)[:rings]:
                    cv2.circle(array, (x, 1008), 32, (255, 255, 255), 6)
                cv2.putText(array, "0:01", (40, 1950), cv2.FONT_HERSHEY_SIMPLEX, 1.6,
                            (255, 255, 255), 3)
                parts = overlays.frame_parts(array, self.frame())
                playback = [p for p in parts if p["kind"] == "reel-playback"]
                self.assertEqual(len(playback), 3 if rings == 2 else 0)
                if rings == 2:
                    self.assertTrue(all("circle" in p for p in playback))
                    self.assertGreater(playback[1]["circle"][2], 90)
                timers = [p for p in parts if p["kind"] == "reel-timecode"]
                self.assertEqual(len(timers), 1 if rings == 2 else 0)

    def test_nested_reel_screen_requires_small_face_and_phone_frame_evidence(self):
        array = photo(1080, 2340)
        box = (70, 1560, 310, 2030)
        cv2.rectangle(array, box[:2], box[2:], (245, 245, 245), -1)
        cv2.rectangle(array, (83, 1576), (307, 2022), (25, 25, 25), -1)
        cv2.rectangle(array, (83, 1576), (307, 1645), (10, 10, 10), -1)
        cv2.circle(array, (190, 1680), 16, (220, 180, 145), -1)
        frame = {"pictureBox": [0, 277, 1080, 1738], "uiBottom": 2016,
                 "statusBand": None}
        faces = [[460, 520, 160, 210], [175, 1660, 30, 40]]

        parts = overlays.frame_parts(array, frame, faces=faces)
        inset = [part for part in parts if part["kind"] == "reel-picture-in-picture"]
        self.assertEqual(len(inset), 1)
        self.assertEqual(inset[0]["box"], [70, 1560, 310, 1738])

        without_secondary_face = overlays.frame_parts(array, frame, faces=faces[:1])
        self.assertFalse(any(part["kind"] == "reel-picture-in-picture"
                             for part in without_secondary_face))

    def test_nested_reel_screen_requires_bright_bezel_even_with_face_and_edges(self):
        array = photo(1080, 2340)
        cv2.rectangle(array, (70, 1560), (310, 2030), (100, 100, 100), -1)
        cv2.rectangle(array, (83, 1576), (307, 2022), (25, 25, 25), -1)
        cv2.rectangle(array, (83, 1576), (307, 1645), (10, 10, 10), -1)
        cv2.circle(array, (190, 1680), 16, (220, 180, 145), -1)
        frame = {"pictureBox": [0, 277, 1080, 1738], "uiBottom": 2016,
                 "statusBand": None}
        faces = [[460, 520, 160, 210], [175, 1660, 30, 40]]
        parts = overlays.frame_parts(array, frame, faces=faces)
        self.assertFalse(any(part["kind"] == "reel-picture-in-picture" for part in parts))

    def test_rounded_caption_button_includes_its_outline_not_just_letters(self):
        array = photo(1080, 2340)
        cv2.rectangle(array, (540, 1785), (885, 1865), (190, 190, 190), 2)
        cv2.putText(array, "Following", (558, 1840), cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                    (255, 255, 255), 3)
        parts = overlays.frame_parts(array, self.frame())
        buttons = [p for p in parts if p["kind"] == "reel-caption-button"]
        self.assertEqual(len(buttons), 1)
        x0, y0, x1, y1 = buttons[0]["box"]
        self.assertLess(x0, 540)
        self.assertLess(y0, 1785)
        self.assertGreater(x1, 885)
        self.assertGreater(y1, 1865)

    def test_blank_or_open_caption_rectangle_is_not_a_button(self):
        for closed in (False, True):
            array = photo(1080, 2340)
            cv2.line(array, (540, 1785), (885, 1785), (190, 190, 190), 2)
            cv2.line(array, (540, 1865), (885, 1865), (190, 190, 190), 2)
            if closed:
                cv2.line(array, (540, 1785), (540, 1865), (190, 190, 190), 2)
                cv2.line(array, (885, 1785), (885, 1865), (190, 190, 190), 2)
            else:
                cv2.putText(array, "Following", (558, 1840), cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                            (255, 255, 255), 3)
            self.assertFalse(any(p["kind"] == "reel-caption-button"
                                 for p in overlays.frame_parts(array, self.frame())))


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

    @staticmethod
    def transparent_badge(background, centre, radius):
        array = np.full((800, 800, 3), background, dtype=np.uint8)
        cx, cy = centre
        pink = (235, 40, 170)
        cv2.circle(array, centre, radius, pink, max(3, radius // 14))
        scale = radius / 43
        origin = (cx - round(.85 * radius), cy + round(.23 * radius))
        cv2.putText(array, "GMW", origin, cv2.FONT_HERSHEY_SIMPLEX, scale, (45, 35, 40),
                    max(3, round(.10 * radius)))
        cv2.putText(array, "GMW", origin, cv2.FONT_HERSHEY_SIMPLEX, scale, (220, 220, 220),
                    max(2, round(.05 * radius)))
        cv2.putText(array, "M", (cx - round(.34 * radius), origin[1]), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, pink, max(3, round(.10 * radius)))
        return array

    def test_transparent_badge_on_pale_background_uses_complete_outer_ring(self):
        for background, centre, radius in ((180, (210, 620), 90), (145, (590, 630), 80)):
            with self.subTest(background=background, centre=centre):
                array = self.transparent_badge(background, centre, radius)
                found = overlays.badges(array)
                self.assertEqual(len(found), 1)
                cx, cy, detected = found[0]["confirmation"]["circle"]
                self.assertLess(np.hypot(cx - centre[0], cy - centre[1]), radius * .15)
                self.assertGreater(detected, radius * .85)
                for angle in overlays.ANGLES:
                    x = round(centre[0] + radius * 1.04 * np.cos(angle))
                    y = round(centre[1] + radius * 1.04 * np.sin(angle))
                    self.assertTrue(found[0]["mask"][y, x])
                self.assertLess(found[0]["mask"].mean(), .1)

    def test_pale_background_ring_and_filled_centre_are_not_lettering(self):
        for filled in (False, True):
            array = np.full((800, 800, 3), 180, dtype=np.uint8)
            cv2.circle(array, (400, 400), 90, (235, 40, 170), 7)
            if filled:
                cv2.circle(array, (400, 400), 60, (235, 40, 170), cv2.FILLED)
            self.assertEqual(overlays.badges(array), [])

    def test_transparent_lettering_keeps_ring_silver_and_isolation_guards(self):
        badge = overlays.profiles()["badges"][0]
        score = {"ringCoverage": .85, "silverFraction": .3, "letterBand": .3, "offBand": .4,
                 "magentaLetterBand": .35, "magentaOffBand": .1,
                 "innerMagenta": .16, "outerMagenta": .01}
        self.assertTrue(overlays.accepted(score, badge))
        for key, value in (("ringCoverage", .7), ("silverFraction", .05),
                           ("magentaLetterBand", .2), ("magentaOffBand", .2),
                           ("innerMagenta", .3), ("outerMagenta", .2)):
            with self.subTest(key=key):
                self.assertFalse(overlays.accepted(dict(score, **{key: value}), badge))
        old_badge = dict(badge, structure={key: value for key, value in badge["structure"].items()
                                         if key != "transparentLettering"})
        self.assertIs(overlays.accepted(score, old_badge), False)


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

    def test_dola_watermark_is_found_but_other_white_text_is_not(self):
        mark = cv2.cvtColor(cv2.imread(str(overlays.REFERENCES / "dola-ai.png")), cv2.COLOR_BGR2RGB)
        mark = cv2.resize(mark, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
        array = photo(1340, 2450)
        h, w = mark.shape[:2]
        array[2330:2330 + h, 1100:1100 + w] = mark
        found = [item for item in overlays.references(array) if item["pattern"] == "dola-ai"]
        self.assertEqual(len(found), 1)
        x0, y0, x1, y1 = found[0]["box"]
        self.assertTrue(x0 <= 1100 and y0 <= 2330 and x1 >= 1100 + w and y1 >= 2330 + h)
        other = photo(1340, 2450)
        cv2.putText(other, "Hello World", (1000, 2380), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
        self.assertEqual([item for item in overlays.references(other) if item["pattern"] == "dola-ai"], [])


class BadgeReconstructionMaskTest(unittest.TestCase):
    def test_badge_mask_reaches_past_the_fitted_ring_to_its_glow(self):
        from PIL import Image
        from intake_library import reconstruction

        width, height = 1000, 1500
        row = {"eligibility": {"status": "usable", "faces": []}, "geometry": {"overlayDetected": False},
               "experiment": {"final": "control", "candidates": {"control": {"sourceBox": [0, 0, width, height]}},
                              "overlayParts": [{"kind": "confirmed-badge", "box": [600, 1100, 900, 1400],
                                                "pattern": "gmw", "circle": [750, 1250, 140]}]}}
        image = Image.fromarray(photo(width, height))
        with mock.patch.object(reconstruction.fill, "fill", side_effect=lambda img, mask: img):
            outputs = dict(reconstruction.head_overlay_candidates(image, row))
        mask = np.asarray(outputs["head-overlay-mask"])[..., 0] > 0
        reach = 140 + round(min(width, height) * reconstruction.BADGE_GROW)
        self.assertTrue(mask[1250, 750 + reach - 1], "glow ring just outside the fitted circle is repainted")
        self.assertFalse(mask[1250, 750 + reach + 3])
        self.assertFalse(mask[200, 200])


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
