"""Same-mask eraser A/B regressions on generated fixture reports; no models load."""
import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import eraser_benchmark as benchmark  # noqa: E402
import image_preparation as preparation  # noqa: E402

SCRATCH = ROOT / "tmp"
PERSON = (0, 0, 400, 580)


def person(size, box):
    width, height = size
    mask = np.zeros((height, width), dtype=bool)
    mask[box[1]:box[3], box[0]:box[2]] = True
    return {"box": list(box), "mask": mask, "people": 1, "dropped": 0}


def flat_fill(image, mask):
    array = np.array(image)
    array[mask] = (128, 120, 110)
    return Image.fromarray(array)


def screenshot():
    image = Image.new("RGB", (400, 900), (90, 110, 150))
    image.paste("black", (0, 0, 400, 120))
    image.paste("black", (0, 700, 400, 869))
    image.paste("white", (0, 869, 400, 900))
    draw = ImageDraw.Draw(image)
    draw.rectangle((350, 440, 370, 460), fill="black")
    draw.rectangle((354, 444, 366, 456), fill="white")
    return image


class EraserBenchmarkTests(unittest.TestCase):
    ERASED = "Various/gallery/panels.png"
    PLAIN = "Various/gallery/plain.png"

    @classmethod
    def setUpClass(cls):
        """One fixture report per class (no models: faces, people and the LaMa fill are mocked)."""
        SCRATCH.mkdir(exist_ok=True)
        cls.fixture = tempfile.TemporaryDirectory(prefix="", dir=SCRATCH)  # short: Windows MAX_PATH
        root = pathlib.Path(cls.fixture.name) / "Sovereign Territories Sandbox" / "Working"
        for relative, image in ((cls.ERASED, screenshot()), (cls.PLAIN, Image.new("RGB", (400, 900), (90, 40, 20)))):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path)
        with mock.patch.object(preparation, "CURRENT", "preparation-comparison-v16"), \
                mock.patch.object(preparation, "STEPS", preparation.pipeline.STEPS), \
                mock.patch.dict(preparation.RECIPE, {"id": "preparation-comparison-v16"}), \
                mock.patch.object(preparation.pipeline, "recommended_candidates",
                                  preparation.pipeline.processing_candidates), \
                mock.patch.object(preparation.preparation_geometry, "detect_faces",
                               return_value=([[140., 180., 60., 70.]], "One local test face")), \
                mock.patch.object(preparation.pipeline.subjects, "detect",
                                  side_effect=lambda image: person(image.size, PERSON)), \
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
        self.write_report_manifest(data)
        self.out = self.root / "_reports" / "eraser-compare" / "ab"
        self.sources = pathlib.Path(self.tmp.name) / "sources.json"
        self.erased, self.plain = self.ERASED, self.PLAIN
        guard = mock.patch.object(preparation.pipeline.fill, "fill", side_effect=AssertionError("model load"))
        self.no_model = guard.start()
        self.addCleanup(guard.stop)
        self.select([self.erased, self.plain])

    def tearDown(self):
        self.tmp.cleanup()

    def select(self, sources):
        self.sources.write_text(json.dumps(sources), encoding="utf-8")

    def call(self, *flags, out=None, report=None):
        with contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()) as stderr:
            code = benchmark.main(["--report", str(report or self.report), "--sources", str(self.sources),
                                   "--out", str(out or self.out), *flags])
        self.output = stdout.getvalue() + stderr.getvalue()
        return code

    def report_manifest(self):
        return json.loads((self.report / "manifest.json").read_text(encoding="utf-8"))

    def write_report_manifest(self, data):
        (self.report / "manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def row(self, source):
        return next(r for r in self.report_manifest()["photos"] if r["source"] == source)

    def run_manifest(self):
        return json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))

    def tree(self, path):
        return {p.relative_to(path).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in path.rglob("*") if p.is_file()}

    def test_fixture_report_has_an_eraser_and_a_skip(self):
        steps = {s["name"]: s for s in self.row(self.erased)["processing"]["steps"]}
        self.assertEqual(steps["eraser"]["status"], "attempted-selected")
        plain = {s["name"]: s for s in self.row(self.plain)["processing"]["steps"]}
        self.assertEqual(plain["eraser"]["status"], "skipped")

    def test_enhancements_share_native_input_and_do_not_rank_blur_as_quality(self):
        import intake_sequence_benchmark as sequence
        image = Image.new("RGB", (120, 160), (80, 90, 100))
        before = image.tobytes()
        row = {"experiment": {"final": "eraser"}}
        outputs = dict(sequence.enhancement_candidates(image, row))
        self.assertEqual(set(outputs), {"enhance-denoise", "enhance-tone", "enhance-sharpen"})
        self.assertTrue(all(candidate.size == image.size for candidate in outputs.values()))
        self.assertEqual(image.tobytes(), before)
        evidence = row["experiment"]["enhancements"]
        self.assertEqual(evidence["recommendation"], "eraser")
        self.assertEqual(row["experiment"]["final"], "eraser")
        self.assertEqual(evidence["diagnostics"]["laplacianVariance"], 0)
        self.assertTrue(all(c["input"] == "eraser" and c["status"] == "comparison-only"
                            for c in evidence["candidates"].values()))
        self.assertNotIn("blurry", evidence["diagnostics"])

    def test_head_overlay_is_unselected_complete_mask_and_preserves_outside(self):
        import intake_sequence_benchmark as sequence
        image = Image.new("RGB", (400, 900), (110, 80, 60))
        mask = np.zeros((900, 400), dtype=bool)
        mask[90:130, 20:370] = True
        part = {"kind": "search-bubble", "box": [20, 90, 370, 130], "mask": mask}
        row = {"eligibility": {"status": "usable"}, "geometry": {"overlayDetected": True},
               "experiment": {"final": "control"}}
        with mock.patch.object(sequence.clutter, "bubbles", return_value=[part]), \
                mock.patch.object(sequence.clutter, "glyphs", return_value=[]), \
                mock.patch.object(sequence.fill, "fill", side_effect=flat_fill):
            outputs = dict(sequence.head_overlay_candidates(image, row))
        self.assertEqual(row["experiment"]["final"], "control")
        self.assertFalse(row["experiment"]["headOverlay"]["selected"])
        self.assertEqual(row["experiment"]["headOverlay"]["status"], "comparison-only")
        result = np.asarray(outputs["head-overlay-reconstruction"])
        self.assertTrue(np.array_equal(result[~mask], np.asarray(image)[~mask]))
        self.assertTrue(np.all(np.asarray(outputs["head-overlay-mask"])[mask] == 255))

    def test_integrated_head_keeps_prior_cleanup_coordinates_and_feeds_enhancements(self):
        import intake_sequence_benchmark as sequence
        original = Image.new("RGB", (400, 900), (110, 80, 60))
        cleaned = original.crop((10, 20, 390, 880))
        cleaned.putpixel((8, 600), (128, 120, 110))
        erase = np.zeros((860, 380), dtype=bool)
        erase[600, 8] = True
        mask = np.zeros_like(erase)
        mask[90:130, 20:350] = True
        row = {"eligibility": {"status": "usable"}, "geometry": {"overlayDetected": True},
               "experiment": {"final": "eraser", "steps": [], "candidates": {
                   "eraser": {"sourceBox": [10, 20, 390, 880]},
                   "composition": {"box": [0, 10, 380, 850], "sourceBox": [10, 30, 390, 870]}}}}
        with mock.patch.object(sequence.clutter, "bubbles", return_value=[
                {"kind": "search-bubble", "box": [20, 90, 350, 130], "mask": mask}]), \
                mock.patch.object(sequence.clutter, "glyphs", return_value=[]), \
                mock.patch.object(sequence.fill, "fill", side_effect=flat_fill):
            outputs = dict(sequence.integrated_head_candidates(
                cleaned, row, original, sequence.pipeline.mask_image(erase)))
        final = row["experiment"]["final"]
        self.assertEqual(final, "head-overlay-reconstruction")
        self.assertEqual(outputs[final].getpixel((8, 600)), (128, 120, 110))
        self.assertEqual(row["experiment"]["headOverlay"]["sourceBox"], [10, 20, 390, 880])
        self.assertTrue(row["experiment"]["headOverlay"]["cumulativeOutsideMaskIdentical"])
        cumulative = np.asarray(outputs["cumulative-erase-mask"])[..., 0] > 0
        self.assertTrue(cumulative[620, 18])
        self.assertTrue(cumulative[110:150, 30:360].all())
        self.assertEqual(int(cumulative.sum()), int(mask.sum()) + 1)
        self.assertEqual(outputs["head-overlay-composition"].size, (380, 840))
        self.assertEqual(row["experiment"]["candidates"]["head-overlay-composition"]["input"], final)
        list(sequence.enhancement_candidates(outputs[final], row))
        self.assertEqual(row["experiment"]["enhancements"]["input"], final)
        self.assertEqual(row["experiment"]["guardedFinal"], "eraser")
        self.assertFalse(row["experiment"]["headOverlay"]["likenessEligible"])

    def test_integrated_head_failure_retains_guarded_final(self):
        import intake_sequence_benchmark as sequence
        image = Image.new("RGB", (400, 900))
        mask = np.zeros((900, 400), dtype=bool)
        mask[90:130, 20:370] = True
        row = {"eligibility": {"status": "usable"}, "geometry": {"overlayDetected": True},
               "experiment": {"final": "control", "steps": [],
                              "candidates": {"control": {"sourceBox": [0, 0, 400, 900]}}}}
        with mock.patch.object(sequence.clutter, "bubbles", return_value=[
                {"kind": "search-bubble", "box": [20, 90, 370, 130], "mask": mask}]), \
                mock.patch.object(sequence.clutter, "glyphs", return_value=[]), \
                mock.patch.object(sequence.fill, "fill", side_effect=RuntimeError("test failure")):
            outputs = dict(sequence.integrated_head_candidates(image, row, image))
        self.assertNotIn("head-overlay-reconstruction", outputs)
        self.assertEqual(row["experiment"]["final"], "control")
        self.assertEqual(row["experiment"]["headOverlay"]["status"], "failed")

    def test_observed_picture_composition_is_selected_after_ui_reconstruction(self):
        import intake_sequence_benchmark as sequence
        original = Image.new("RGB", (400, 900), (110, 80, 60))
        prepared = original.crop((0, 70, 400, 720))
        mask = np.zeros((650, 400), dtype=bool)
        mask[5:55, 40:360] = True
        row = {"eligibility": {"status": "usable", "faces": [[170, 150, 60, 70]]},
               "geometry": {"overlayDetected": True},
               "experiment": {"final": "first-crop", "steps": [], "candidates": {
                   "first-crop": {"sourceBox": [0, 70, 400, 720]}},
                   "screenshotLayout": {"pictureBox": [0, 100, 400, 720], "overlayParts": [
                       {"kind": "rendered-screenshot-ui", "box": [355, 500, 380, 540]},
                       {"kind": "rendered-screenshot-ui", "box": [60, 650, 300, 670]}]}}}
        with mock.patch.object(sequence.clutter, "bubbles", return_value=[
                {"kind": "search-bubble", "box": [40, 5, 360, 55], "mask": mask}]), \
                mock.patch.object(sequence.clutter, "glyphs", return_value=[]), \
                mock.patch.object(sequence.fill, "fill", side_effect=flat_fill):
            outputs = dict(sequence.integrated_head_candidates(prepared, row, original))
        final = row["experiment"]["final"]
        self.assertEqual(final, "head-overlay-composition")
        self.assertEqual(outputs[final].size, (400, 620))
        self.assertEqual(outputs[final].tobytes(),
                         outputs["head-overlay-reconstruction"].crop((0, 30, 400, 650)).tobytes())
        self.assertEqual(outputs[final].getpixel((365, 420)), (128, 120, 110))
        self.assertEqual(outputs[final].getpixel((200, 560)), (128, 120, 110))
        list(sequence.enhancement_candidates(outputs[final], row))
        self.assertEqual(row["experiment"]["enhancements"]["input"], final)
        self.assertEqual(row["experiment"]["candidates"][final]["sourceBox"], [0, 100, 400, 720])

    def test_review_summary_final_is_third_with_visible_status_and_lineage(self):
        import intake_sequence_benchmark as sequence
        image = {"path": "native.png", "padded": "padded.png", "size": [400, 900]}
        row = {"source": "Various/gallery/test.png", "images": {
            name: dict(image) for name in ("original", "saved-v16-final", "control",
                                          "head-overlay-reconstruction", "composition", "eraser-mask")},
            "evidence": {"final": "head-overlay-reconstruction", "steps": [],
                         "headOverlay": {"selected": True}, "candidates": {
                             "head-overlay-reconstruction": {"input": "control"}}}}
        data = {"reviewLayout": 2, "out": str(self.out), "working": str(self.root), "rows": [row]}
        page = sequence.page(data).decode()
        self.assertLess(page.index("1. Original"), page.index("2. Historical"))
        self.assertLess(page.index("2. Historical"), page.index("3. Current"))
        self.assertIn("SELECTED — head-overlay-reconstruction", page)
        self.assertIn("REJECTED — composition", page)
        self.assertIn("DIAGNOSTIC — eraser-mask", page)
        self.assertIn("Input: control", page)
        self.assertIn("Feeds: head-overlay-reconstruction", page)
        self.assertIn("SYNTHETIC HEAD RECONSTRUCTION", page)
        self.assertNotIn("h2{overflow-wrap:anywhere}", page)
        data["reviewLayout"] = 3
        self.assertIn("h2{overflow-wrap:anywhere}", sequence.page(data).decode())
        data["out"] = str(
            self.root / "operations" / "archive" / "reports" / "eraser-compare" / "sequence"
        )
        with mock.patch.object(
            preparation.cw,
            "load_cfg",
            return_value={"storageRoots": {"reports": "operations/archive/reports"}},
        ):
            self.assertIn("../../_assets/gallery-banner.jpg", sequence.page(data).decode())

    def test_pill_icon_proposals_reject_solid_highlight_and_keep_outline(self):
        import intake_sequence_benchmark as sequence
        image = Image.new("RGB", (400, 900), (110, 80, 60))
        draw = ImageDraw.Draw(image)
        draw.rectangle((360, 95, 380, 116), outline="white", width=3)
        found = sequence.pill_icons(np.asarray(image), 80, 140)
        self.assertEqual(len(found), 1)
        self.assertTrue(found[0]["mask"][105, 370], "erase hollow icon interior as well")
        draw.rectangle((360, 95, 380, 116), fill="white")
        self.assertEqual(sequence.pill_icons(np.asarray(image), 80, 140), [])

    def test_head_overlay_model_failure_is_visible_not_success(self):
        import intake_sequence_benchmark as sequence
        image = Image.new("RGB", (400, 900))
        mask = np.zeros((900, 400), dtype=bool)
        mask[90:130, 20:370] = True
        row = {"eligibility": {"status": "usable"}, "geometry": {"overlayDetected": True},
               "experiment": {"final": "control"}}
        with mock.patch.object(sequence.clutter, "bubbles",
                               return_value=[{"kind": "search-bubble", "box": [20, 90, 370, 130], "mask": mask}]), \
                mock.patch.object(sequence.clutter, "glyphs", return_value=[]), \
                mock.patch.object(sequence.fill, "fill", side_effect=RuntimeError("test failure")):
            outputs = dict(sequence.head_overlay_candidates(image, row))
        self.assertNotIn("head-overlay-reconstruction", outputs)
        self.assertEqual(row["experiment"]["headOverlay"]["status"], "failed")
        self.assertIn("test failure", row["experiment"]["headOverlay"]["reason"])

    def test_head_overlay_fills_pattern_badge_disc_without_pill(self):
        import intake_sequence_benchmark as sequence
        image = Image.new("RGB", (400, 600), (90, 90, 90))
        row = {"eligibility": {"status": "usable", "faces": [[150., 100., 60., 70.]]},
               "geometry": {"overlayDetected": False},
               "experiment": {"final": "control", "candidates": {"control": {"sourceBox": [0, 0, 400, 600]}},
                              "overlayParts": [
                                  {"kind": "confirmed-badge", "box": [20, 400, 81, 461], "pattern": "gmw",
                                   "circle": [50.0, 430.0, 30.0]},
                                  {"kind": "watermark", "box": [150, 110, 200, 130], "pattern": "corner-text"}]}}
        with mock.patch.object(sequence.fill, "fill",
                               side_effect=lambda img, m: Image.fromarray(np.where(m[..., None], 0, np.asarray(img))
                                                                          .astype(np.uint8))):
            outputs = dict(sequence.head_overlay_candidates(image, row))
        mask = np.asarray(outputs["head-overlay-mask"])[..., 0] > 0
        self.assertTrue(mask[430, 50])
        self.assertFalse(mask[402, 22])  # disc, not the bounding square
        self.assertFalse(mask[120, 175])  # on the face: refused
        self.assertEqual(len(row["experiment"]["headOverlay"]["refusedParts"]), 1)
        self.assertIn("head-overlay-reconstruction", outputs)

    def test_head_overlay_ignores_avatar_face_inside_pattern_part(self):
        import intake_sequence_benchmark as sequence
        image = Image.new("RGB", (400, 600), (90, 90, 90))
        row = {"eligibility": {"status": "usable", "faces": [[150., 100., 60., 70.], [30., 505., 20., 25.]]},
               "geometry": {"overlayDetected": False},
               "experiment": {"final": "control", "candidates": {"control": {"sourceBox": [0, 0, 400, 600]}},
                              "overlayParts": [
                                  {"kind": "reel-avatar", "box": [20, 500, 60, 540], "pattern": "phone-reel"}]}}
        with mock.patch.object(sequence.fill, "fill",
                               side_effect=lambda img, m: Image.fromarray(np.where(m[..., None], 0, np.asarray(img))
                                                                          .astype(np.uint8))):
            outputs = dict(sequence.head_overlay_candidates(image, row))
        mask = np.asarray(outputs["head-overlay-mask"])[..., 0] > 0
        self.assertTrue(mask[520, 40])
        self.assertNotIn("refusedParts", row["experiment"]["headOverlay"])
        import intake_sequence_benchmark as sequence
        row = {"eligibility": {"status": "junk-candidate"}, "experiment": {"final": "control"}}
        with mock.patch.object(sequence.clutter, "bubbles", side_effect=AssertionError("not eligible")):
            self.assertEqual(list(sequence.head_overlay_candidates(Image.new("RGB", (20, 20)), row)), [])
        self.assertEqual(row["experiment"]["headOverlay"]["status"], "skipped")
        self.assertEqual(row["experiment"]["final"], "control")

    def test_sequence_preview_apply_check_repeat_and_artifact_tamper(self):
        def experiment(image, row):
            row["experiment"] = {"steps": [{"name": "control", "status": "comparison-only"}],
                                 "final": "control"}
            yield "control", image.copy()

        before = self.tree(self.report)
        with mock.patch.object(preparation.pipeline, "EXPERIMENT_POLICY", {"test": True}, create=True), \
                mock.patch.object(preparation.pipeline, "experimental_candidates", experiment, create=True):
            self.assertEqual(self.call("--sequence", "--dry-run"), 0, self.output)
            self.assertFalse(self.out.exists())
            self.assertEqual(self.call("--sequence", "--apply"), 0, self.output)
            self.assertEqual(self.call("--sequence", "--check"), 0, self.output)
            first = self.tree(self.out)
            self.assertEqual(self.call("--sequence", "--apply"), 0, self.output)
            self.assertEqual(self.tree(self.out), first)
            self.assertEqual(self.tree(self.report), before)
            data = self.run_manifest()
            self.assertEqual(len(data["rows"]), 2, "clean/no-eraser inputs also exercise the sequence")
            panel = self.out / data["rows"][0]["images"]["control"]["path"]
            panel.write_bytes(b"tampered")
            self.assertEqual(self.call("--sequence", "--check"), 2)
            self.assertIn("hash mismatch", self.output)

    def test_sequence_refuses_changed_selection_and_failed_stage_publishes_nothing(self):
        with mock.patch.object(preparation.pipeline, "EXPERIMENT_POLICY", {"test": True}, create=True), \
                mock.patch.object(preparation.pipeline, "experimental_candidates",
                                  side_effect=ValueError("experiment failed"), create=True):
            self.assertEqual(self.call("--sequence", "--apply"), 2)
            self.assertIn("experiment failed", self.output)
            self.assertFalse(self.out.exists())
            self.assertFalse(list(self.out.parent.glob(".intake-sequence-*")))

    def test_preview_writes_nothing_and_check_without_run_fails(self):
        before = self.tree(self.root)
        self.assertEqual(self.call("--dry-run"), 0)
        self.assertIn("compare " + self.erased, self.output)
        self.assertIn("skip    " + self.plain, self.output)
        self.assertEqual(self.call(), 0, "preview is the default")
        self.assertEqual(self.call("--check"), 2)
        self.assertEqual(self.tree(self.root), before)
        self.assertFalse(self.out.parent.exists())
        self.no_model.assert_not_called()

    def test_same_mask_fills_change_only_masked_pixels_of_the_pre_eraser_input(self):
        self.assertEqual(self.call("--apply"), 0, self.output)
        data = self.run_manifest()
        compared, skipped = data["rows"]
        self.assertEqual((compared["status"], skipped["status"]), ("compared", "skipped"))
        self.assertIn("No clutter detected", skipped["reason"])
        report_row = self.row(self.erased)
        step = next(s for s in report_row["processing"]["steps"] if s["name"] == "eraser")
        self.assertEqual(compared["inputs"]["input"]["variant"], step["input"])
        self.assertNotEqual(step["input"], report_row["processing"]["final"], "pre-eraser input, not the final")
        self.assertEqual(compared["inputs"]["input"]["sha256"], report_row["variants"][step["input"]]["sha256"])
        self.assertEqual(compared["copies"]["mask"]["sha256"], report_row["variants"]["eraser-mask"]["sha256"])
        self.assertEqual(compared["copies"]["baseline"]["sha256"], report_row["variants"]["eraser"]["sha256"])
        with Image.open(self.report / report_row["variants"][step["input"]]["path"]) as opened:
            original = np.array(opened)
        with Image.open(self.report / report_row["variants"]["eraser-mask"]["path"]) as opened:
            mask = np.array(opened)[..., 0] == 255
        self.assertTrue(mask.any())
        for name in ("telea", "ns"):
            output = compared["outputs"][name]
            self.assertEqual(output["radius"], benchmark.RADIUS)
            self.assertTrue(output["outsideMaskIdentical"])
            with Image.open(self.out / output["path"]) as opened:
                filled = np.array(opened)
                self.assertEqual(filled.shape, original.shape)
            self.assertTrue(np.array_equal(filled[~mask], original[~mask]), name)
            self.assertFalse(np.array_equal(filled[mask], original[mask]), name)
            with Image.open(self.out / output["padded"]) as opened:
                self.assertEqual(opened.size, (944, 1104))
        self.assertTrue(compared["baseline"]["outsideMaskIdentical"])
        page = (self.out / "index.html").read_text(encoding="utf-8")
        for text in ("Pixel change is not quality", "not recovery", "NOT an erase-first sequence",
                     "comparison only", "Skipped"):
            self.assertIn(text, page)
        self.assertEqual((self.out / "sources.json").read_bytes(), self.sources.read_bytes())
        self.assertEqual(data["selection"]["sources"], [self.erased, self.plain])
        self.assertFalse(any(p.name.startswith(".eraser-compare-") for p in self.out.parent.iterdir()))
        self.no_model.assert_not_called()

    def test_repeat_apply_is_idempotent_and_check_passes(self):
        self.assertEqual(self.call("--apply"), 0, self.output)
        before = self.tree(self.out)
        self.assertEqual(self.call("--apply"), 0, self.output)
        self.assertIn("without rewriting", self.output)
        self.assertEqual(self.call("--check"), 0, self.output)
        self.assertEqual(self.tree(self.out), before)

    def test_check_rejects_tampered_missing_or_extra_outputs(self):
        self.assertEqual(self.call("--apply"), 0, self.output)
        telea = self.out / self.run_manifest()["rows"][0]["outputs"]["telea"]["path"]
        original = telea.read_bytes()
        telea.write_bytes(original + b"x")
        self.assertEqual(self.call("--check"), 2)
        self.assertEqual(self.call("--apply"), 2, "repeat apply never rewrites a damaged run")
        telea.unlink()
        self.assertEqual(self.call("--check"), 2)
        telea.write_bytes(original)
        self.assertEqual(self.call("--check"), 0, self.output)
        (self.out / "extra.txt").write_text("x", encoding="utf-8")
        self.assertEqual(self.call("--check"), 2)

    def test_check_rejects_changed_report_or_selection(self):
        self.assertEqual(self.call("--apply"), 0, self.output)
        self.select([self.erased])
        self.assertEqual(self.call("--check"), 2)
        self.select([self.erased, self.plain])
        retained = self.report / self.row(self.erased)["retained"]
        payload = retained.read_bytes()
        retained.write_bytes(payload + b"tamper")
        self.assertEqual(self.call("--check"), 2)
        retained.write_bytes(payload)
        self.assertEqual(self.call("--check"), 0, self.output)
        data = self.report_manifest()
        data["photos"][0]["diagnostics"].append("edited")
        self.write_report_manifest(data)
        self.assertEqual(self.call("--check"), 2)
        self.assertIn("report differs", self.output)

    def test_selected_input_tamper_refuses_without_writes(self):
        row = self.row(self.erased)
        step = next(s for s in row["processing"]["steps"] if s["name"] == "eraser")
        path = self.report / row["variants"][step["input"]]["path"]
        path.write_bytes(path.read_bytes() + b"x")
        self.assertEqual(self.call("--dry-run"), 2)
        self.assertEqual(self.call("--apply"), 2)
        self.assertFalse(self.out.exists())
        self.select([self.plain])
        self.assertEqual(self.call("--apply"), 0, "only selected artifacts are read")

    def replace_mask(self, image):
        data = self.report_manifest()
        row = next(r for r in data["photos"] if r["source"] == self.erased)
        path = self.report / row["variants"]["eraser-mask"]["path"]
        path.unlink()
        image.save(path)
        row["variants"]["eraser-mask"]["sha256"] = preparation.sha_file(path)
        self.write_report_manifest(data)
        return row["variants"]["eraser-mask"]["size"]

    def test_non_binary_mask_is_refused(self):
        width, height = self.row(self.erased)["variants"]["eraser-mask"]["size"]
        self.replace_mask(Image.new("RGB", (width, height), (128, 128, 128)))
        self.assertEqual(self.call("--apply"), 2)
        self.assertIn("binary", self.output)
        self.assertFalse(self.out.exists())

    def test_mask_size_mismatch_is_refused(self):
        width, height = self.row(self.erased)["variants"]["eraser-mask"]["size"]
        mask = Image.new("RGB", (width + 3, height), (0, 0, 0))
        mask.paste((255, 255, 255), (0, 0, 10, 10))
        self.replace_mask(mask)
        self.assertEqual(self.call("--apply"), 2)
        self.assertIn("sizes differ", self.output)
        self.assertFalse(self.out.exists())

    def test_source_list_rules(self):
        for sources in ([], [self.erased, self.erased], ["Various/gallery/missing.png"],
                        [f"Various/gallery/{i}.png" for i in range(65)], {"source": self.erased},
                        ["../escape.png"]):
            self.select(sources)
            self.assertEqual(self.call("--apply"), 2, sources)
        self.sources.write_text("not json", encoding="utf-8")
        self.assertEqual(self.call("--apply"), 2)
        self.assertFalse(self.out.parent.exists())

    def test_object_selection_binds_source_hashes(self):
        rows = [{"role": "named-case", "source": self.erased, "sourceSha256": self.row(self.erased)["sourceSha256"]},
                {"role": "control", "source": self.plain}]
        self.select(rows)
        self.assertEqual(self.call("--apply"), 0, self.output)
        self.assertEqual(self.run_manifest()["selection"]["sources"], [self.erased, self.plain])
        self.assertEqual(self.call("--check"), 0, self.output)
        rows[0]["sourceSha256"] = "0" * 64
        self.select(rows)
        self.assertEqual(self.call("--dry-run", out=self.out.parent / "other"), 2)
        self.assertIn("hashes differ", self.output)
        self.select([{"source": self.erased}, self.plain])
        self.assertEqual(self.call("--dry-run", out=self.out.parent / "other"), 2)

    def test_output_and_report_locations_are_guarded(self):
        for out in (self.report / "ab", self.root / "_reports" / "preparation" / "ab",
                    self.root / "Various" / "gallery" / "ab", self.root / "_reports" / "eraser-compare" / ".hidden"):
            self.assertEqual(self.call("--apply", out=out), 2, out)
        self.assertEqual(self.call("--apply", out=pathlib.Path("relative")), 2)
        data = self.report_manifest()
        data["root"] = str(pathlib.Path(self.tmp.name) / "Elsewhere" / "Working")
        self.write_report_manifest(data)
        self.assertEqual(self.call("--apply"), 2)
        self.assertFalse((self.root / "_reports" / "eraser-compare").exists())

    def test_launcher_previews_and_checks(self):
        if os.name != "nt":
            self.skipTest("Windows launcher")
        launcher = ROOT / "bin" / "eraser-compare.cmd"
        base = ["cmd", "/c", str(launcher), "--report", str(self.report), "--sources", str(self.sources),
                "--out", str(self.out)]
        preview = subprocess.run(base + ["--dry-run"], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertIn("Preview only", preview.stdout)
        self.assertFalse(self.out.parent.exists())
        check = subprocess.run(base + ["--check"], capture_output=True, text=True, cwd=ROOT)
        self.assertNotEqual(check.returncode, 0)


    def test_apply_publishes_the_shared_banner_once(self):
        banner = self.root / "_reports" / "_assets" / "gallery-banner.jpg"
        self.assertEqual(self.call("--dry-run"), 0)
        self.assertFalse(banner.exists())
        self.assertEqual(self.call("--apply"), 0, self.output)
        self.assertTrue(banner.is_file())
        self.assertIn("../../_assets/gallery-banner.jpg", (self.out / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(self.call("--check"), 0, self.output)

    def test_configured_reports_root_routes_output_and_banner(self):
        reports = self.root / "operations" / "reports"
        reports.parent.mkdir(parents=True)
        (self.root / "_reports").rename(reports)
        self.report = reports / "preparation" / "pilot"
        self.out = reports / "eraser-compare" / "ab"
        config = {"storageRoots": {"reports": "operations/reports"}}
        with mock.patch.object(preparation.cw, "load_cfg", return_value=config):
            self.assertEqual(self.call("--apply"), 0, self.output)
            self.assertEqual(self.call("--check"), 0, self.output)
        self.assertTrue((reports / "_assets" / "gallery-banner.jpg").is_file())
        self.assertFalse((self.root / "_reports").exists())


class NestedIntakeRootTests(EraserBenchmarkTests.__base__):
    """A clean-rebase intake mirror (Working\\_sandbox-state\\RUN\\inputs) bound by the run's intake.json."""

    ERASED, PLAIN = EraserBenchmarkTests.ERASED, EraserBenchmarkTests.PLAIN

    @classmethod
    def setUpClass(cls):
        EraserBenchmarkTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="", dir=SCRATCH)
        self.working = pathlib.Path(self.tmp.name) / "Sovereign Territories Sandbox" / "Working"
        self.run = self.working / "_sandbox-state" / "r"
        self.mirror = self.run / "inputs"
        self.report = self.mirror / "_reports" / "preparation" / "all"
        for relative in (EraserBenchmarkTests.ERASED, EraserBenchmarkTests.PLAIN):
            (self.mirror / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.template / relative, self.mirror / relative)
        shutil.copytree(self.template / "_reports" / "preparation" / "pilot", self.report)
        self.bind(self.mirror, self.report)
        self.out = self.working / "_reports" / "eraser-compare" / "ab"
        self.sources = pathlib.Path(self.tmp.name) / "sources.json"
        self.sources.write_text(json.dumps([EraserBenchmarkTests.ERASED, EraserBenchmarkTests.PLAIN]),
                                encoding="utf-8")
        guard = mock.patch.object(preparation.pipeline.fill, "fill", side_effect=AssertionError("model load"))
        self.no_model = guard.start()
        self.addCleanup(guard.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def bind(self, root, report, receipt=None):
        manifest = report / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["root"] = str(root)
        manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        value = {"schemaVersion": 1, "preparationManifestSHA256": preparation.sha_file(manifest),
                 "recipe": data["recipe"], "inputs": {r["source"]: r["sourceSha256"] for r in data["photos"]}}
        (receipt or root.parent / "intake.json").write_text(json.dumps(value), encoding="utf-8")
        return value

    def call(self, *flags, out=None, report=None):
        with contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()) as stderr:
            code = benchmark.main(["--report", str(report or self.report), "--sources", str(self.sources),
                                   "--out", str(out or self.out), *flags])
        self.output = stdout.getvalue() + stderr.getvalue()
        return code

    def tree(self, path):
        return {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob("*") if p.is_file()}

    def test_nested_preview_apply_check_and_repeat(self):
        before = self.tree(self.run)
        self.assertEqual(self.call("--dry-run"), 0, self.output)
        self.assertIn("compare " + EraserBenchmarkTests.ERASED, self.output)
        self.assertFalse((self.working / "_reports").exists(), "preview writes nothing")
        self.assertEqual(self.call("--apply"), 0, self.output)
        data = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual((data["root"], data["working"]), (str(self.mirror), str(self.working)))
        self.assertEqual([r["status"] for r in data["rows"]], ["compared", "skipped"])
        self.assertTrue((self.working / "_reports" / "_assets" / "gallery-banner.jpg").is_file())
        published = self.tree(self.out)
        self.assertEqual(self.call("--apply"), 0, self.output)
        self.assertIn("without rewriting", self.output)
        self.assertEqual(self.call("--check"), 0, self.output)
        self.assertEqual(self.tree(self.out), published)
        self.assertEqual(self.tree(self.run), before, "intake run bytes are untouched")
        self.no_model.assert_not_called()

    def test_output_must_be_the_real_working_reports(self):
        for out in (self.mirror / "_reports" / "eraser-compare" / "ab", self.run / "eraser-compare" / "ab"):
            self.assertEqual(self.call("--apply", out=out), 2, out)
        self.assertFalse((self.mirror / "_reports" / "eraser-compare").exists())

    def test_configured_state_and_reports_roots_accept_nested_input(self):
        state_root = self.working / "o" / "s"
        state_root.parent.mkdir(parents=True)
        (self.working / "_sandbox-state").rename(state_root)
        self.run = state_root / "r"
        self.mirror = self.run / "inputs"
        reports = self.mirror / "r"
        (self.mirror / "_reports").rename(reports)
        self.report = reports / "preparation" / "all"
        self.bind(self.mirror, self.report)
        self.out = self.working / "r" / "eraser-compare" / "ab"
        config = {
            "storageRoots": {
                "sandboxState": "o/s",
                "reports": "r",
            },
        }
        with mock.patch.object(preparation.cw, "load_cfg", return_value=config):
            self.assertEqual(self.call("--apply"), 0, self.output)
            self.assertEqual(self.call("--check"), 0, self.output)
        self.assertTrue((self.working / "r" / "_assets" / "gallery-banner.jpg").is_file())

    def forged(self):
        self.assertEqual(self.call("--dry-run"), 2, self.output)
        self.assertEqual(self.call("--apply"), 2, self.output)
        self.assertFalse((self.working / "_reports").exists())

    def test_missing_receipt_is_rejected(self):
        (self.run / "intake.json").unlink()
        self.forged()
        self.assertIn("no intake receipt", self.output)

    def test_receipt_for_another_manifest_is_rejected(self):
        value = json.loads((self.run / "intake.json").read_text(encoding="utf-8"))
        value["preparationManifestSHA256"] = "0" * 64
        (self.run / "intake.json").write_text(json.dumps(value), encoding="utf-8")
        self.forged()
        self.assertIn("does not bind", self.output)

    def test_receipt_inventory_mismatch_is_rejected(self):
        value = json.loads((self.run / "intake.json").read_text(encoding="utf-8"))
        value["inputs"].pop(EraserBenchmarkTests.PLAIN)
        (self.run / "intake.json").write_text(json.dumps(value), encoding="utf-8")
        self.forged()

    def test_edited_report_manifest_breaks_the_receipt(self):
        manifest = self.report / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["photos"][0]["diagnostics"].append("edited")
        manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.forged()

    def test_forged_root_shapes_are_rejected(self):
        self.assertEqual(self.call("--apply"), 0, self.output)
        cases = []
        other = self.working / "_sandbox-state" / "r" / "other"
        shutil.copytree(self.mirror, other)
        cases.append((other, other / "_reports" / "preparation" / "all"))
        hidden = self.working / "_sandbox-state" / "_r" / "inputs"
        shutil.copytree(self.mirror, hidden)
        cases.append((hidden, hidden / "_reports" / "preparation" / "all"))
        loose = self.working / "elsewhere" / "r" / "inputs"
        shutil.copytree(self.mirror, loose)
        cases.append((loose, loose / "_reports" / "preparation" / "all"))
        renamed = self.mirror / "_reports" / "preparation" / "all2"
        shutil.copytree(self.report, renamed)
        cases.append((self.mirror, renamed))
        foreign = pathlib.Path(self.tmp.name) / "Other" / "Working" / "_sandbox-state" / "r" / "inputs"
        shutil.copytree(self.mirror, foreign)
        cases.append((foreign, foreign / "_reports" / "preparation" / "all"))
        for root, report in cases:
            receipt = root.parent / "intake.json"
            self.bind(root, report, receipt if receipt.parent.exists() else None)
            out = self.working / "_reports" / "eraser-compare" / ("f" + str(len(self.output)))
            self.assertEqual(self.call("--dry-run", report=report, out=out), 2, root)
        mismatch = self.working / "_sandbox-state" / "r2" / "inputs"
        shutil.copytree(self.mirror, mismatch)
        report = mismatch / "_reports" / "preparation" / "all"
        self.bind(self.mirror, report, mismatch.parent / "intake.json")
        self.assertEqual(self.call("--dry-run", report=report, out=self.working / "_reports" / "eraser-compare" / "m"),
                         2, "the manifest root must be the report's own mirror")


if __name__ == "__main__":
    unittest.main()
