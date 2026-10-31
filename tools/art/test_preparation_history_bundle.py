"""Bounded history fixtures, publication, tamper refusal and supported launcher."""
import contextlib
import copy
import io
import json
import os
import pathlib
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from unittest import mock
from html.parser import HTMLParser

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
import preparation_history_bundle as history  # noqa: E402


def image_bytes(size, color, image_format="PNG"):
    with Image.new("RGB", size, color) as image:
        stream = io.BytesIO()
        image.save(stream, format=image_format)
        return stream.getvalue()


def create_fixture(base, count=2, storage_mode="full", selected="original"):
    """Create only isolated synthetic images; also usable for launcher smoke tests."""
    root = pathlib.Path(base) / "Sovereign Territories Sandbox" / "Working"
    root.mkdir(parents=True, exist_ok=True)
    cfg = history.preparation.cw.load_cfg()
    reports = history.preparation.cw.storage_root(cfg, "reports", root=root)
    report = reports / "preparation" / storage_mode
    report.mkdir(parents=True)
    data = {"schemaVersion": 1, "root": str(root),
            "recipe": {"id": "preparation-comparison-v23", "trialPolicy": {
                "models": {"fixture": "no model loading"}, "note": "complete stored provenance fixture"}},
            "inventory": {"Various": count}, "limit": count, "photos": [],
            "configurationReceipt": history.preparation.cw.storage_configuration_receipt(cfg, root)}
    if storage_mode == "lean":
        data["storageMode"] = "lean"

    def put(relative, payload):
        target = report / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return relative, history.digest_bytes(payload)

    original_bytes = image_bytes((96, 128), (30, 60, 90))
    for number in range(count):
        original, original_sha = put(f"originals/{number}.png", original_bytes)
        detail, detail_sha = put(f"photos/{number}.html", b"fixture diagnostic page")
        row = {
            "source": (f"Artists/Fixture Artist/gallery/test_image_{number}.png" if number % 2
                       else f"Various/gallery/test_image_{number}.png"),
            "photoId": f"photo:image_{number}", "sourceSha256": original_sha, "retained": original,
            "detail": detail, "detailSha256": detail_sha, "outcome": "compared", "diagnostics": [],
            "sourceScope": {"category": "Artists" if number % 2 else "Various",
                            "artist": "Fixture Artist" if number % 2 else None,
                            "matchingDomain": "Artists/Fixture Artist" if number % 2 else "general",
                            "reason": "Synthetic isolated scope"},
            "geometry": {"box": [8, 8, 88, 120], "method": "full-span-solid-border-v1",
                         "changed": True, "reason": "fixture crop", "overlayDetected": False,
                         "uiCropBox": None, "uiCropAssessment": "no overlay"},
            "eligibility": {"status": "usable", "faces": [[10., 10., 65., 65.]],
                            "largestFacePixels": 65, "minFace": 60, "reason": "fixture"},
            "recommendation": {"use": selected, "reason": "fixture unchanged processing selection"},
            "variants": {},
        }
        source = root / row["source"]
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(original_bytes)
        for name, size in (("geometry", (80, 112)), ("control", (96, 128))):
            payload = original_bytes if name == "control" else image_bytes(size, (30, 60, 90))
            path, digest = put(f"candidates/{number}/{name}.png", payload)
            if storage_mode == "lean" and name == "control":
                (report / path).unlink()
                path = original
            preview, preview_sha = put(f"candidates/{number}/{name}-preview.jpg",
                                       image_bytes(size, (30, 60, 90), "JPEG"))
            row["variants"][name] = {
                "path": path, "sha256": digest, "thumbnail": preview, "thumbnailSha256": preview_sha,
                "size": list(size), "seconds": 0.001, "meanAbsolutePixelChange": 0,
            }
        padded, padded_sha = put(f"recommended/{number}.png",
                                image_bytes((944, 1104), (120, 120, 120)))
        if selected == "original":
            row["recommendedPadded"] = {"path": padded, "sha256": padded_sha, "source": original}
        else:
            row["variants"][selected].update({"padded": padded, "paddedSha256": padded_sha})
        final = "control" if selected == "original" else selected
        steps = []
        current = "control"
        for index, name in enumerate(history.preparation.STEPS):
            choose = index == 0 and final != "control"
            steps.append({"name": name, "status": "attempted-selected" if choose else "skipped",
                          "input": current, "candidate": final if choose else None,
                          "selected": final if choose else current, "reason": "fixture"})
            if choose:
                current = final
        row["processing"] = {"steps": steps, "cleanup": final, "final": final, "faceAssessment": "fixture"}
        data["photos"].append(row)
    _, data["reportSha256"] = put("index.html", b"<!doctype html><title>Synthetic preparation fixture</title>")
    (report / "manifest.json").write_bytes(history.encoded(data))
    history.preparation.verify(root, report)
    return root, report, reports / "preparation-history" / "compact"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        self.targets.extend(value for name, value in attrs if name in ("href", "src"))


class HistoryTests(unittest.TestCase):
    def setUp(self):
        ignored = subprocess.run(["git", "check-ignore", "tmp"], cwd=ROOT, capture_output=True)
        self.assertEqual(ignored.returncode, 0)
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="history-tests-", dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.base = pathlib.Path(self.temporary.name)
        self.root, self.report, self.output = create_fixture(self.base)
        self.before = history.tree(self.report)

    def call(self, *flags, report=True, output=None):
        args = ["--root", str(self.root), "--out", str(output or self.output)]
        if report:
            args += ["--report", str(self.report)]
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = history.main([*args, *flags])
        self.stdout, self.stderr = stdout.getvalue(), stderr.getvalue()
        return code

    def apply(self, mode="compact"):
        self.assertEqual(self.call("--apply", "--mode", mode), 0, self.stderr)
        return json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))

    def save_source(self, data):
        (self.report / "manifest.json").write_bytes(history.encoded(data))

    def test_preview_default_and_explicit_are_read_only(self):
        for flags in ((), ("--dry-run",)):
            self.assertEqual(self.call(*flags), 0, self.stderr)
            self.assertIn('"preview": true', self.stdout)
            self.assertFalse(self.output.parent.exists())
            self.assertEqual(history.tree(self.report), self.before)

    def test_compact_exact_sha_aliases_and_independent_check(self):
        data = self.apply()
        self.assertEqual(data["sourceManifest"], history.read_json(self.report / "manifest.json"))
        for row in data["photos"]:
            self.assertEqual(row["exact"]["original"]["path"], row["exact"]["selectedNative"]["path"])
            original_roles = [r for r in row["roles"] if r["sourceSha256"] == row["sourceSha256"]]
            self.assertEqual(len({r["history"]["path"] for r in original_roles}), 1)
            self.assertEqual(len({r["exactPath"] for r in original_roles}), 1)
        self.assertNotEqual(data["photos"][0]["exact"]["original"]["path"],
                            data["photos"][1]["exact"]["original"]["path"])
        self.assertEqual(history.tree(self.report), self.before)
        shutil.rmtree(self.report)
        self.assertEqual(self.call("--check", report=False), 0, self.stderr)

    def test_selected_nonoriginal_keeps_three_exact_artifacts_per_row(self):
        root, report, output = create_fixture(self.base / "selected", selected="geometry")
        history.publish(root, report, output, "compact")
        data, result = history.check(root, output)
        self.assertEqual(result["exactFiles"], 6)
        self.assertEqual(data["photos"][0]["exact"]["selectedNative"]["role"], "geometry/native")

    def test_collage_one_jpeg_per_photo_labels_and_html_links(self):
        data = self.apply("collage")
        self.assertEqual(data["statistics"]["historyFiles"], 2)
        for row in data["photos"]:
            self.assertEqual(len({r["history"]["path"] for r in row["roles"]}), 1)
            self.assertTrue(all(r["history"]["stage"] >= 1 for r in row["roles"]))
        page = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn("LOSSY", page)
        self.assertIn("NOT exact workflow or recovery evidence", page)
        self.assertIn("conversion is NOT pruning", page)
        self.assertIn("persistedTotals", page)
        parser = Links()
        parser.feed(page)
        self.assertTrue(parser.targets)
        for target in parser.targets:
            self.assertTrue(history.relative_path(self.output, target).is_file())
        _, result = history.check(self.root, self.output)
        self.assertEqual(data["persistedTotals"]["actualFiles"], result["actualFiles"])
        self.assertEqual(data["persistedTotals"]["actualBytes"], result["actualBytes"])

    def test_lean_input_and_full_input_both_supported(self):
        root, report, output = create_fixture(self.base / "lean", storage_mode="lean")
        history.publish(root, report, output, "collage")
        data, _ = history.check(root, output)
        self.assertEqual(data["sourceManifest"]["storageMode"], "lean")
        self.assertEqual(data["sourceManifest"]["recipe"]["trialPolicy"]["models"],
                         {"fixture": "no model loading"})

    def mirror_fixture(self):
        mirror = self.root / "_sandbox-state" / "trial" / "inputs"
        mirror.mkdir(parents=True)
        cfg = history.preparation.cw.load_cfg()
        destination = history.preparation.cw.storage_root(cfg, "reports", root=mirror) / "preparation" / "all"
        destination.parent.mkdir(parents=True)
        shutil.move(str(self.report), str(destination))
        for category in ("Various", "Artists"):
            shutil.copytree(self.root / category, mirror / category)
        self.report = destination
        data = history.read_json(destination / "manifest.json")
        data["root"] = str(mirror)
        data["configurationReceipt"] = history.preparation.cw.storage_configuration_receipt(cfg, mirror)
        self.save_source(data)
        history.preparation.verify(mirror, destination)
        return mirror

    def test_real_input_mirror_conversion_preserves_roots_and_independent_check(self):
        mirror = self.mirror_fixture()
        before = history.tree(self.report)
        original_verify = history.preparation.verify
        for mode in ("compact", "collage"):
            output = self.output.with_name(mode)
            self.assertEqual(self.call("--dry-run", "--mode", mode, output=output), 0, self.stderr)
            with mock.patch.object(history.preparation, "verify", wraps=original_verify) as verify:
                self.assertEqual(self.call("--apply", "--mode", mode, output=output), 0, self.stderr)
            verify.assert_called_once_with(mirror, self.report, current_sources=False)
            self.assertEqual(self.call("--apply", "--mode", mode, output=output), 0, self.stderr)
            data, _ = history.check(self.root, output)
            self.assertEqual(data["root"], str(self.root))
            self.assertEqual(data["sourceRoot"], str(mirror))
            self.assertEqual(data["sourceManifest"]["root"], str(mirror))
            mutated = copy.deepcopy(data)
            mutated["sourceRoot"] = str(self.root)
            with self.assertRaises(ValueError):
                history.validate_bundle(mutated)
        self.assertEqual(history.tree(self.report), before)
        shutil.rmtree(mirror)
        for mode in ("compact", "collage"):
            self.assertEqual(self.call("--check", report=False, output=self.output.with_name(mode)), 0,
                             self.stderr)

    def test_input_mirror_wrong_escape_and_nested_recorded_roots_refused(self):
        mirror = self.mirror_fixture()
        source = history.read_json(self.report / "manifest.json")
        invalid = (
            self.root, self.base, self.root / "_sandbox-state" / "different" / "inputs",
            self.root / "_sandbox-state" / "trial", mirror / "nested",
            self.root / "_sandbox-state" / "trial" / "not-inputs",
            self.root / "_sandbox-state" / "nested" / "trial" / "inputs",
            self.root / "_sandbox-state" / "trial" / ".." / "trial" / "inputs",
            pathlib.Path("relative-root"),
        )
        for recorded in invalid:
            with self.subTest(root=str(recorded)):
                data = copy.deepcopy(source)
                data["root"] = str(recorded)
                self.save_source(data)
                self.assertEqual(self.call("--apply"), 1)
                self.assertFalse(self.output.exists())
        self.save_source(source)
        valid = self.report
        wrong = valid.parent / "nested" / valid.name
        wrong.parent.mkdir()
        valid.rename(wrong)
        self.report = wrong
        self.assertEqual(self.call("--apply"), 1)
        self.assertFalse(self.output.exists())

    def test_input_mirror_linked_root_refused(self):
        mirror = self.mirror_fixture()
        actual_lstat = pathlib.Path.lstat

        def reparse(path, *args, **kwargs):
            info = actual_lstat(path, *args, **kwargs)
            if path == mirror:
                return mock.Mock(st_file_attributes=0x400, st_mode=info.st_mode)
            return info

        with mock.patch.object(pathlib.Path, "lstat", reparse):
            self.assertEqual(self.call("--apply"), 1)
        self.assertFalse(self.output.exists())

    def test_apply_and_check_idempotent_no_source_or_payload_rewrites(self):
        self.apply()
        files = {path: (path.stat().st_mtime_ns, path.read_bytes())
                 for path in self.output.rglob("*") if path.is_file()}
        self.assertEqual(self.call("--apply"), 0, self.stderr)
        self.assertEqual(self.call("--check"), 0, self.stderr)
        self.assertEqual(files, {path: (path.stat().st_mtime_ns, path.read_bytes()) for path in files})
        self.assertEqual(history.tree(self.report), self.before)

    def test_mode_or_report_mismatch_does_not_overwrite(self):
        self.apply()
        before = history.tree(self.output)
        self.assertEqual(self.call("--apply", "--mode", "collage"), 1)
        self.assertEqual(history.tree(self.output), before)
        _, other, _ = create_fixture(self.base / "other")
        with self.assertRaises(ValueError):
            history.check(self.root, self.output, expected_report=other)

    def test_missing_check_and_missing_report_fail_without_writes(self):
        self.assertEqual(self.call("--check", report=False), 1)
        self.assertEqual(self.call(report=False), 1)
        self.assertFalse(self.output.parent.exists())

    def test_stale_source_manifest_refuses_repeated_apply(self):
        self.apply()
        data = history.read_json(self.report / "manifest.json")
        data["recipe"]["newNote"] = "changed"
        self.save_source(data)
        before = history.tree(self.output)
        self.assertEqual(self.call("--apply"), 1)
        self.assertEqual(history.tree(self.output), before)
        self.assertEqual(self.call("--check", report=False), 0, self.stderr)

    def test_source_missing_or_tampered_payload_refused(self):
        data = history.read_json(self.report / "manifest.json")
        target = self.report / data["photos"][0]["retained"]
        target.write_bytes(b"tampered")
        self.assertEqual(self.call("--apply"), 1)
        target.unlink()
        self.assertEqual(self.call("--apply"), 1)
        self.assertFalse(self.output.exists())

    def test_missing_tampered_and_stale_bundle_metadata_refused(self):
        self.apply()
        for name in ("manifest.json", "receipt.json", "index.html"):
            target = self.output / name
            payload = target.read_bytes()
            with self.subTest(name=name, mutation="missing"):
                target.unlink()
                self.assertEqual(self.call("--check", report=False), 1)
            target.write_bytes(payload)
            with self.subTest(name=name, mutation="tampered"):
                target.write_bytes(b"{}" if name.endswith(".json") else b"tampered")
                self.assertEqual(self.call("--check", report=False), 1)
            target.write_bytes(payload)
        receipt = history.read_json(self.output / "receipt.json")
        receipt["output"] += "-stale"
        (self.output / "receipt.json").write_bytes(history.encoded(receipt))
        self.assertEqual(self.call("--check", report=False), 1)

    def test_payload_tamper_missing_extra_file_and_directory_refused(self):
        data = self.apply()
        name = next(iter(data["payloads"]))
        target = self.output / name
        original = target.read_bytes()
        target.write_bytes(b"tampered")
        self.assertEqual(self.call("--check", report=False), 1)
        target.unlink()
        self.assertEqual(self.call("--check", report=False), 1)
        target.write_bytes(original)
        (self.output / "unexpected.txt").write_text("extra", encoding="utf-8")
        self.assertEqual(self.call("--check", report=False), 1)
        (self.output / "unexpected.txt").unlink()
        (self.output / "unexpected-directory").mkdir()
        self.assertEqual(self.call("--check", report=False), 1)

    def test_semantic_selection_and_cross_row_pooling_refused(self):
        data = self.apply()
        mutated = copy.deepcopy(data)
        mutated["photos"][1]["exact"]["original"] = mutated["photos"][0]["exact"]["original"]
        with self.assertRaises(ValueError):
            history.validate_bundle(mutated)
        mutated = copy.deepcopy(data)
        mutated["photos"][0]["roles"][0]["sourceSha256"] = "0" * 64
        with self.assertRaises(ValueError):
            history.validate_bundle(mutated)

    def test_source_changed_during_conversion_cleans_owned_stage(self):
        convert = history.convert_row
        changed = False

        def mutate(*args):
            nonlocal changed
            row = convert(*args)
            if not changed:
                changed = True
                (self.report / "index.html").write_bytes(b"changed while converting")
            return row

        with mock.patch.object(history, "convert_row", side_effect=mutate):
            self.assertEqual(self.call("--apply"), 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.output.parent.iterdir()), [])

    def test_source_changed_at_final_publication_gate_refused(self):
        original_check = history.check

        def mutate(*args, **kwargs):
            result = original_check(*args, **kwargs)
            (self.report / "index.html").write_bytes(b"changed immediately before publication")
            return result

        with mock.patch.object(history, "check", side_effect=mutate):
            self.assertEqual(self.call("--apply"), 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.output.parent.iterdir()), [])

    def test_conversion_failure_cleans_stage_without_touching_source(self):
        with mock.patch.object(history, "jpeg", side_effect=OSError("simulated encoder failure")):
            self.assertEqual(self.call("--apply"), 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(history.tree(self.report), self.before)
        self.assertEqual(list(self.output.parent.iterdir()), [])

    def test_cap_64_and_24_photo_batch(self):
        root, report, output = create_fixture(self.base / "batch", count=24)
        for mode in ("compact", "collage"):
            target = output.with_name(mode)
            result = history.publish(root, report, target, mode)
            self.assertEqual(result["photos"], 24)
            self.assertEqual(history.check(root, target)[1]["photos"], 24)
        data = history.read_json(self.report / "manifest.json")
        data["photos"] = [data["photos"][0]] * 65
        self.save_source(data)
        self.assertEqual(self.call(), 1)
        self.assertIn("1..64", self.stderr)

    def test_byte_count_manifest_and_role_bounds(self):
        with mock.patch.object(history, "MAX_TOTAL_BYTES", 10):
            self.assertEqual(self.call(), 1)
        with mock.patch.object(history, "MAX_FILE_BYTES", 10):
            self.assertEqual(self.call(), 1)
        with mock.patch.object(history, "MAX_JSON_BYTES", 10):
            self.assertEqual(self.call(), 1)
        with mock.patch.object(history, "MAX_FILES", 2):
            self.assertEqual(self.call(), 1)
        with mock.patch.object(history, "MAX_ROLES", 2):
            self.assertEqual(self.call(), 1)

    def test_malformed_and_huge_image_geometry_fail_before_decode(self):
        path = self.base / "malformed.png"
        path.write_bytes(b"not an image")
        with self.assertRaises(ValueError):
            history.thumbnail(path)
        image = history.thumbnail(path, allow_invalid=True)
        self.assertLessEqual(max(image.size), history.COMPACT_EDGE)
        image.close()
        # A valid PNG header declaring an enormous image, with no pixel allocation.
        header = struct.pack(">IIBBBBB", 100000, 100000, 8, 2, 0, 0, 0)
        chunk = b"IHDR" + header
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", len(header)) + chunk
                         + struct.pack(">I", zlib.crc32(chunk)) + b"\0\0\0\0IEND\xaeB`\x82")
        with self.assertRaises((ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning)):
            history.thumbnail(path)
        with mock.patch.object(history, "MAX_PIXELS", 20):
            with self.assertRaisesRegex(ValueError, "geometry"):
                history.thumbnail(self.report / "originals" / "0.png")

    def test_unprocessable_retains_exact_bad_original_and_labels_placeholder(self):
        data = history.read_json(self.report / "manifest.json")
        for row in data["photos"]:
            for field in ("processing", "geometry", "eligibility", "recommendedPadded"):
                row.pop(field, None)
            row["outcome"] = "unprocessable"
            row["recommendation"] = {"use": "none", "reason": "malformed fixture"}
            row["variants"] = {}
            payload = b"malformed exact original"
            (self.report / row["retained"]).write_bytes(payload)
            row["sourceSha256"] = history.digest_bytes(payload)
        self.save_source(data)
        bundle = self.apply()
        for row in bundle["photos"]:
            self.assertEqual(set(row["exact"]), {"original"})
            self.assertEqual((self.output / row["exact"]["original"]["path"]).read_bytes(),
                             b"malformed exact original")
        self.assertEqual(self.call("--check", report=False), 0, self.stderr)

    def test_exif_orientation_and_alpha_images_become_bounded_rgb_jpegs(self):
        path = self.base / "alpha.png"
        with Image.new("RGBA", (1000, 800), (100, 40, 20, 128)) as source:
            source.save(path)
        image = history.thumbnail(path)
        try:
            self.assertEqual(image.mode, "RGB")
            self.assertLessEqual(max(image.size), history.COMPACT_EDGE)
            with Image.open(io.BytesIO(history.jpeg(image))) as decoded:
                self.assertEqual(decoded.mode, "RGB")
        finally:
            image.close()
        path = self.base / "orientation.jpg"
        with Image.new("RGB", (800, 400), "white") as source:
            exif = Image.Exif()
            exif[274] = 6
            source.save(path, exif=exif)
        image = history.thumbnail(path)
        try:
            self.assertGreater(image.height, image.width)
        finally:
            image.close()

    def test_jpeg_and_collage_geometry_bound(self):
        with Image.new("RGB", (4097, 1)) as image:
            with self.assertRaises(ValueError):
                history.jpeg(image)
        self.apply("collage")
        for path in self.output.glob("photos/*collage.jpg"):
            with Image.open(path) as image:
                self.assertEqual(image.format, "JPEG")
                self.assertLessEqual(max(image.size), 4096)

    def test_paths_traversal_outside_root_source_overlap_refused(self):
        for value in ("../escape", "/absolute", "C:/escape", "a\\b", "a//b", "a/./b", "a:stream"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                history.relative_path(self.root, value)
        for target in (self.base / "outside", self.report / "nested", self.root / "_reports" / "wrong"):
            self.assertEqual(self.call("--apply", output=target), 1)
            self.assertFalse(target.exists())

    def test_reparse_and_hardlinks_refused(self):
        source = self.report / "index.html"
        target = self.report / "hardlink.html"
        os.link(source, target)
        self.assertEqual(self.call(), 1)
        target.unlink()
        try:
            target.symlink_to(source)
        except OSError:
            # Windows often disallows symlinks; exercise the same reparse guard.
            actual_lstat = pathlib.Path.lstat

            def reparse(path, *args, **kwargs):
                info = actual_lstat(path, *args, **kwargs)
                return mock.Mock(st_file_attributes=0x400, st_mode=info.st_mode) if path == source else info

            with mock.patch.object(pathlib.Path, "lstat", reparse):
                self.assertEqual(self.call(), 1)
        else:
            self.assertEqual(self.call(), 1)
            target.unlink()

    def test_prune_receipt_keeps_source_and_explicit_gap(self):
        data = self.apply()
        receipt = history.read_json(self.output / "receipt.json")
        for value in (data["prune"], receipt["prune"]):
            self.assertTrue(value["sourceReportKept"])
            self.assertTrue(value["dependencyApprovalRequired"])
            self.assertEqual(value["sourceReportsDeleted"], 0)
            self.assertIn("dependency", value["remainingGap"])
        self.assertEqual(history.tree(self.report), self.before)

    @unittest.skipUnless(os.name == "nt", "Windows supported launcher")
    def test_launcher_preview_apply_check_and_repeat(self):
        prefix = ["cmd", "/c", str(ROOT / "bin" / "preparation-history.cmd"),
                  "--root", str(self.root), "--report", str(self.report), "--out", str(self.output)]
        for flags in ([], ["--apply"], ["--check"], ["--apply"]):
            completed = subprocess.run([*prefix, *flags], cwd=ROOT, capture_output=True, text=True,
                                       timeout=120)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            result = json.loads(completed.stdout)
            self.assertTrue(result["prune"]["sourceReportKept"])
            if not flags:
                self.assertFalse(self.output.exists())
        self.assertEqual(history.tree(self.report), self.before)


if __name__ == "__main__":
    unittest.main()
