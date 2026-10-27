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

SCRATCH = ROOT / "reports"
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
        with mock.patch.object(preparation.preparation_geometry, "detect_faces",
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
