"""Overlay reference review regressions on a generated fixture report; no models load, no sources change."""
import contextlib
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import image_preparation as preparation  # noqa: E402
import overlay_reference_review as review  # noqa: E402

SCRATCH = ROOT / "reports"
MAGENTA = (230, 40, 200)


def person(size):
    width, height = size
    mask = np.zeros((height, width), dtype=bool)
    mask[:580, :] = True
    return {"box": [0, 0, width, 580], "mask": mask, "people": 1, "dropped": 0}


def flat_fill(image, mask):
    array = np.array(image)
    array[mask] = (128, 120, 110)
    return Image.fromarray(array)


def canvas(color=(90, 110, 150)):
    return Image.new("RGB", (400, 900), color)


def middle_badge():
    image = canvas()
    ImageDraw.Draw(image).ellipse((170, 430, 230, 470), fill=MAGENTA)
    return image


def corner_badge():
    image = canvas()
    ImageDraw.Draw(image).ellipse((320, 800, 380, 840), fill=MAGENTA)
    return image


def pill():
    image = canvas((90, 40, 20))
    ImageDraw.Draw(image).rounded_rectangle((40, 60, 360, 90), radius=14, fill=(120, 120, 120))
    return image


class OverlayReferenceReviewTests(unittest.TestCase):
    MIDDLE = "Various/gallery/middle.png"
    CORNER = "Various/gallery/corner.png"
    PILL = "Various/gallery/pill.png"
    PLAIN = "Various/gallery/plain.png"
    SAME = "Various/gallery/same-as-middle.png"

    @classmethod
    def setUpClass(cls):
        SCRATCH.mkdir(exist_ok=True)
        cls.fixture = tempfile.TemporaryDirectory(prefix="", dir=SCRATCH)
        root = pathlib.Path(cls.fixture.name) / "Sovereign Territories Sandbox" / "Working"
        images = {cls.MIDDLE: middle_badge(), cls.CORNER: corner_badge(), cls.PILL: pill(),
                  cls.PLAIN: canvas((90, 40, 20))}
        for relative, image in images.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path)
        shutil.copyfile(root / cls.MIDDLE, root / cls.SAME)
        with mock.patch.object(preparation.preparation_geometry, "detect_faces",
                               return_value=([[140., 180., 60., 70.]], "One local test face")), \
                mock.patch.object(preparation.pipeline.subjects, "detect", side_effect=lambda i: person(i.size)), \
                mock.patch.object(preparation.pipeline.fill, "fill", side_effect=flat_fill), \
                contextlib.redirect_stdout(io.StringIO()):
            code = preparation.main(["--root", str(root), "--out", str(root / "_reports" / "preparation" / "pilot"),
                                     "--source-folder", "Various/gallery", "--limit", "0", "--apply"])
        if code != 0:
            cls.fixture.cleanup()
            raise RuntimeError("fixture preparation report failed")
        cls.template = root

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="", dir=SCRATCH)
        self.root = pathlib.Path(self.tmp.name) / "Sovereign Territories Sandbox" / "Working"
        shutil.copytree(self.template, self.root)
        self.report = self.root / "_reports" / "preparation" / "pilot"
        data = self.report_manifest()
        data["root"] = str(self.root)
        (self.report / "manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.out = self.root / "_reports" / "eraser-compare" / "refs"
        self.sources = pathlib.Path(self.tmp.name) / "sources.json"
        guard = mock.patch.object(preparation.pipeline.fill, "fill", side_effect=AssertionError("model load"))
        self.no_model = guard.start()
        self.addCleanup(guard.stop)
        self.select([self.MIDDLE, self.CORNER, self.PILL, self.PLAIN, self.SAME])

    def tearDown(self):
        self.tmp.cleanup()

    def select(self, sources):
        self.sources.write_text(json.dumps(sources), encoding="utf-8")

    def call(self, *flags, out=None):
        with contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()) as stderr:
            code = review.main(["--report", str(self.report), "--sources", str(self.sources),
                                "--out", str(out or self.out), *flags])
        self.output = stdout.getvalue() + stderr.getvalue()
        return code

    def report_manifest(self):
        return json.loads((self.report / "manifest.json").read_text(encoding="utf-8"))

    def run_manifest(self):
        return json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))

    def rows(self):
        return {row["source"]: row for row in self.run_manifest()["rows"]}

    def tree(self, path):
        return {p.relative_to(path).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in path.rglob("*") if p.is_file()}

    def test_preview_writes_nothing_and_check_without_run_fails(self):
        before = self.tree(self.root)
        self.assertEqual(self.call("--dry-run"), 0, self.output)
        self.assertIn("propose " + self.MIDDLE, self.output)
        self.assertIn("same    " + self.SAME, self.output)
        self.assertEqual(self.call(), 0, "preview is the default")
        self.assertEqual(self.call("--check"), 2)
        self.assertEqual(self.tree(self.root), before)
        self.assertFalse(self.out.parent.exists())

    def test_apply_proposes_unconfirmed_candidates_anywhere_without_touching_sources(self):
        sources = self.tree(self.root / "Various")
        report = self.tree(self.report)
        self.assertEqual(self.call("--apply"), 0, self.output)
        self.assertEqual(self.tree(self.root / "Various"), sources, "no source is processed or repainted")
        self.assertEqual(self.tree(self.report), report)
        rows = self.rows()
        middle = rows[self.MIDDLE]["candidates"]
        self.assertEqual([c["detectors"] for c in middle], [["emblem-any-location"]],
                         "a mid-frame badge is found only with location clipping disabled")
        x0, y0, x1, y1 = middle[0]["box"]
        self.assertTrue(x0 <= 170 and y0 <= 430 and x1 >= 230 and y1 >= 470, middle[0]["box"])
        self.assertEqual([c["detectors"] for c in rows[self.CORNER]["candidates"]],
                         [["emblem-corner", "emblem-any-location"]], "overlapping detections merge into one")
        self.assertEqual([c["detectors"] for c in rows[self.PILL]["candidates"]], [["search-pill"]])
        self.assertEqual(rows[self.PLAIN]["candidates"], [])
        self.assertEqual(rows[self.SAME]["status"], "duplicate")
        self.assertEqual(rows[self.SAME]["duplicateOf"], self.MIDDLE)
        self.assertNotIn("candidates", rows[self.SAME], "same bytes reuse the first row's proposals")
        for row in rows.values():
            if row["status"] != "proposed":
                continue
            retained = (self.report / row["retained"]).read_bytes()
            self.assertEqual((self.out / row["copy"]["path"]).read_bytes(), retained)
            for c in row["candidates"]:
                self.assertEqual((c["status"], c["confirmed"], c["label"]), ("unconfirmed", False, review.LABEL))
                self.assertEqual((c["sourceId"], c["sourceSha256"]), (row["source"], row["sourceSha256"]))
                with Image.open(self.out / c["mask"]["path"]) as opened:
                    mask = np.array(opened)
                with Image.open(self.out / c["crop"]["path"]) as opened:
                    crop = opened.size
                self.assertTrue(np.isin(mask, (0, 255)).all())
                self.assertEqual(int((mask[..., 0] == 255).sum()), c["maskInCropPixels"])
                self.assertEqual(crop, (c["cropBox"][2] - c["cropBox"][0], c["cropBox"][3] - c["cropBox"][1]))
                self.assertGreater(c["maskInCropPixels"], 0)
        page = (self.out / "index.html").read_text(encoding="utf-8")
        for text in (review.LABEL, "not assumed to be a GMW badge", "in chat", "Same bytes as", "c01"):
            self.assertIn(text, page)
        for forbidden in ("<form", "<script", "<input", "<button"):
            self.assertNotIn(forbidden, page.lower())
        self.assertNotIn("GMW badge", json.dumps(self.run_manifest()["rows"]), "colour is not identity")
        self.assertFalse(any(p.name.startswith(".overlay-review-") for p in self.out.parent.iterdir()))
        self.no_model.assert_not_called()

    def test_configured_reports_root_routes_overlay_page_and_banner(self):
        reports = self.root / "operations" / "reports"
        reports.parent.mkdir(parents=True)
        (self.root / "_reports").rename(reports)
        self.report = reports / "preparation" / "pilot"
        self.out = reports / "eraser-compare" / "refs"
        config = {"storageRoots": {"reports": "operations/reports"}}
        with mock.patch.object(preparation.cw, "load_cfg", return_value=config):
            self.assertEqual(self.call("--apply"), 0, self.output)
            self.assertEqual(self.call("--check"), 0, self.output)
        self.assertTrue((reports / "_assets" / "gallery-banner.jpg").is_file())
        self.assertFalse((self.root / "_reports").exists())

    def test_repeat_apply_is_read_only_and_check_passes(self):
        self.assertEqual(self.call("--apply"), 0, self.output)
        before = self.tree(self.out)
        self.assertEqual(self.call("--apply"), 0, self.output)
        self.assertIn("without rewriting", self.output)
        self.assertEqual(self.call("--check"), 0, self.output)
        self.assertEqual(self.tree(self.out), before)

    def test_check_rejects_tampered_missing_or_extra_outputs(self):
        self.assertEqual(self.call("--apply"), 0, self.output)
        crop = self.out / self.rows()[self.MIDDLE]["candidates"][0]["crop"]["path"]
        original = crop.read_bytes()
        crop.write_bytes(original + b"x")
        self.assertEqual(self.call("--check"), 2)
        self.assertIn("hash mismatch", self.output)
        self.assertEqual(self.call("--apply"), 2, "repeat apply never rewrites a damaged run")
        crop.unlink()
        self.assertEqual(self.call("--check"), 2)
        self.assertIn("missing or extra", self.output)
        crop.write_bytes(original)
        self.assertEqual(self.call("--check"), 0, self.output)
        (self.out / "extra.txt").write_text("x", encoding="utf-8")
        self.assertEqual(self.call("--check"), 2)

    def test_manifest_cannot_auto_confirm_a_candidate(self):
        self.assertEqual(self.call("--apply"), 0, self.output)
        manifest = self.out / "manifest.json"
        data = self.run_manifest()
        data["rows"][0]["candidates"][0].update(status="confirmed", confirmed=True)
        manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(self.call("--check"), 2)
        self.assertIn("not an unconfirmed proposal", self.output)

    def test_check_rejects_changed_report_selection_or_retained_source(self):
        self.assertEqual(self.call("--apply"), 0, self.output)
        self.select([self.MIDDLE])
        self.assertEqual(self.call("--check"), 2)
        self.select([self.MIDDLE, self.CORNER, self.PILL, self.PLAIN, self.SAME])
        retained = self.report / self.rows()[self.MIDDLE]["retained"]
        payload = retained.read_bytes()
        retained.write_bytes(payload + b"tamper")
        self.assertEqual(self.call("--check"), 2)
        self.assertEqual(self.call("--dry-run", out=self.out.parent / "other"), 2, "tampered input refused up front")
        retained.write_bytes(payload)
        self.assertEqual(self.call("--check"), 0, self.output)
        data = self.report_manifest()
        data["photos"][0]["diagnostics"].append("edited")
        (self.report / "manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(self.call("--check"), 2)

    def test_source_list_rules_and_locations(self):
        for sources in ([], [self.MIDDLE, self.MIDDLE], ["Various/gallery/missing.png"], ["../escape.png"],
                        [{"source": self.MIDDLE, "sourceSha256": "0" * 64}]):
            self.select(sources)
            self.assertEqual(self.call("--apply"), 2, sources)
        self.select([self.MIDDLE])
        for out in (self.report / "refs", self.root / "_reports" / "preparation" / "refs",
                    self.root / "Various" / "gallery" / "refs", self.root / "_reports" / "eraser-compare" / "_x"):
            self.assertEqual(self.call("--apply", out=out), 2, out)
        self.assertFalse((self.root / "_reports" / "eraser-compare").exists())

    def test_truncation_is_warned_on_the_page(self):
        real = review.propose
        self.select([self.MIDDLE])
        with mock.patch.object(review, "propose", side_effect=lambda array: (real(array)[0], 3)):
            self.assertEqual(self.call("--apply"), 0, self.output)
        self.assertIn("WARNING", self.output)
        self.assertEqual(self.rows()[self.MIDDLE]["truncated"], 3)
        self.assertIn("Truncated", (self.out / "index.html").read_text(encoding="utf-8"))


class ProposalTests(unittest.TestCase):
    def test_many_regions_are_capped_in_a_fixed_order(self):
        image = canvas()
        draw = ImageDraw.Draw(image)
        for row in range(4):
            for col in range(3):
                x, y = 30 + col * 120, 80 + row * 200
                draw.ellipse((x, y, x + 50, y + 35), fill=MAGENTA)
        found, dropped = review.propose(np.asarray(image))
        self.assertEqual((len(found), dropped), (review.MAX_PER_ROW, 4))
        corner = [c for c in found if "emblem-corner" in c["detectors"]]
        rest = [c for c in found if "emblem-corner" not in c["detectors"]]
        self.assertEqual(found, corner + rest, "corner-heuristic proposals come first")
        self.assertTrue(corner and rest)
        self.assertEqual(rest, sorted(rest, key=lambda c: (c["box"][1], c["box"][0])))

    def test_broad_colour_region_is_not_proposed(self):
        image = canvas()
        ImageDraw.Draw(image).rectangle((0, 300, 400, 700), fill=MAGENTA)
        self.assertEqual(review.propose(np.asarray(image)), ([], 0))

    def test_detector_does_not_change_the_image(self):
        array = np.asarray(middle_badge()).copy()
        before = array.copy()
        review.propose(array)
        self.assertTrue(np.array_equal(array, before))


if __name__ == "__main__":
    unittest.main()
