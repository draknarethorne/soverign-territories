"""Strict Source-to-Working baseline and interrupted publication checks."""

import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art.likeness_library import sandbox, sandbox_baseline as baseline


class SandboxBaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = pathlib.Path(self.temp.name)
        self.production = root / "Sovereign Territories"
        self.working = root / "Sovereign Territories Sandbox" / "Working"
        self.source = self.working.parent / "Source"
        for path in (self.production, self.working, self.source):
            path.mkdir(parents=True)
        self.relative = "Angels/Named/gallery/named_image_123.jpg"
        self.write(self.production, self.relative, b"current production")
        self.write(self.source, self.relative, b"old snapshot")
        self.write(self.working, self.relative, b"experimental pixels")
        self.write(self.working, "Potentials/Experiment/gallery/unknown.jpg", b"experiment")
        self.write(self.working, "_reports/obsolete.html", b"old report")
        self.write(self.working, "_tmp/obsolete.bin", b"old scratch")
        self.write(self.production, "Artists/Separate/gallery/artist.jpg", b"artist")
        self.write(self.production, "_reports/old.html", b"production report")
        self.write(self.production, "_junk/rejected.jpg", b"dispositioned")
        self.save_manifest()

    def write(self, root, relative, contents):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
        return path

    def save_manifest(self):
        rows = [
            {"path": path.relative_to(self.source).as_posix(),
             "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in self.source.rglob("*") if path.is_file()
        ]
        (self.source.parent / "source-manifest.json").write_text(json.dumps({
            "schemaVersion": 1, "sourceRoot": str(self.production),
            "snapshotRoot": "Source", "workingRootAtCreation": "Working",
            "fileCount": len(rows), "totalBytes": sum(row["bytes"] for row in rows),
            "files": rows,
        }), encoding="utf-8")

    def test_preview_then_apply_rebuilds_source_and_working_without_history(self):
        before = (self.working / self.relative).read_bytes()
        proposed = baseline.preview(self.working)
        self.assertTrue(proposed["sourceNeedsRefresh"])
        self.assertEqual(proposed["workingBeforeReset"]["activeFileCount"], 2)
        self.assertEqual((self.working / self.relative).read_bytes(), before)
        with mock.patch.object(sandbox, "_copy_verified_file", wraps=sandbox._copy_verified_file) as copies:
            result = baseline.apply(self.working, "fresh")
        working_inputs = [
            call.args[0] for call in copies.call_args_list
            if call.args[1].is_relative_to(self.working)
        ]
        self.assertTrue(working_inputs)
        self.assertTrue(all(path.is_relative_to(self.source) for path in working_inputs))
        self.assertTrue(result["checked"])
        for root in (self.source, self.working):
            self.assertEqual((root / self.relative).read_bytes(), b"current production")
            self.assertFalse((root / "Artists").exists())
            self.assertEqual((root / "_junk/rejected.jpg").read_bytes(), b"dispositioned")
        self.assertFalse((self.working / "Potentials").exists())
        self.assertFalse((self.working / "_reports/obsolete.html").exists())
        self.assertFalse((self.working / "_tmp/obsolete.bin").exists())
        self.assertTrue((self.production / "Artists/Separate/gallery/artist.jpg").exists())
        self.assertEqual(baseline.apply(self.working, "fresh"), baseline.check(self.working, "fresh"))

    def test_strict_reset_rejects_stale_source_without_touching_working(self):
        (self.working / "_tmp/obsolete.bin").unlink()
        with self.assertRaisesRegex(ValueError, "Source to match"):
            sandbox.full_reset_apply(self.working, discard_working_history=True)
        self.assertEqual((self.working / self.relative).read_bytes(), b"experimental pixels")

    def test_copy_failure_preserves_both_old_trees_and_can_retry(self):
        with mock.patch.object(sandbox, "_copy_verified_file", side_effect=OSError("copy failed")):
            with self.assertRaisesRegex(OSError, "copy failed"):
                baseline.apply(self.working, "copy-retry")
        self.assertEqual((self.source / self.relative).read_bytes(), b"old snapshot")
        self.assertEqual((self.working / self.relative).read_bytes(), b"experimental pixels")
        self.assertTrue(baseline.apply(self.working, "copy-retry")["checked"])

    def test_source_publish_failure_rolls_back_then_retries(self):
        original_validate = sandbox.validate_sandbox

        def fail_new_source(root):
            if (self.source / self.relative).read_bytes() == b"current production":
                raise ValueError("publication check failed")
            return original_validate(root)

        with mock.patch.object(sandbox, "validate_sandbox", side_effect=fail_new_source):
            with self.assertRaisesRegex(ValueError, "publication check failed"):
                baseline.apply(self.working, "publish-retry")
        self.assertEqual((self.source / self.relative).read_bytes(), b"old snapshot")
        self.assertEqual((self.working / self.relative).read_bytes(), b"experimental pixels")
        self.assertTrue(baseline.apply(self.working, "publish-retry")["checked"])

    def test_working_failure_resumes_from_verified_source(self):
        with mock.patch.object(sandbox, "full_reset_apply", side_effect=OSError("Working busy")):
            with self.assertRaisesRegex(OSError, "Working busy"):
                baseline.apply(self.working, "working-retry")
        self.assertEqual((self.source / self.relative).read_bytes(), b"current production")
        self.assertEqual((self.working / self.relative).read_bytes(), b"experimental pixels")
        self.assertTrue(baseline.apply(self.working, "working-retry")["checked"])

    def test_receipt_written_before_cleanup_interruption_resumes_without_reset(self):
        original_rmdir = pathlib.Path.rmdir

        def interrupt_state_cleanup(path):
            if path.name == "transaction":
                raise OSError("cleanup interrupted")
            return original_rmdir(path)

        with mock.patch.object(pathlib.Path, "rmdir", interrupt_state_cleanup):
            with self.assertRaisesRegex(OSError, "cleanup interrupted"):
                baseline.apply(self.working, "cleanup-retry")
        with mock.patch.object(sandbox, "full_reset_apply", side_effect=AssertionError("must not reset twice")):
            self.assertTrue(baseline.apply(self.working, "cleanup-retry")["checked"])

    def test_check_detects_native_or_snapshot_mutation(self):
        baseline.apply(self.working, "binding")
        (self.working / self.relative).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "contents differ"):
            baseline.check(self.working, "binding")

    def test_unknown_production_root_blocks_before_source_refresh(self):
        self.write(self.production, "Unknown/payload.dat", b"unclassified")
        self.assertFalse(baseline.preview(self.working)["resetReady"])
        with self.assertRaisesRegex(ValueError, "blocked"):
            baseline.apply(self.working, "unknown")
        self.assertEqual((self.source / self.relative).read_bytes(), b"old snapshot")

    def test_explicit_sandbox_root_and_safe_run_id_required(self):
        for root in (self.production, pathlib.Path("Working"), self.working.parent):
            with self.assertRaises(ValueError):
                baseline.preview(root)
        with self.assertRaisesRegex(ValueError, "run ID"):
            baseline.apply(self.working, "../escape")

    def test_nested_production_root_is_rejected_before_creating_state(self):
        nested_working = self.production / "Sovereign Territories Sandbox" / "Working"
        nested_working.mkdir(parents=True)
        (nested_working.parent / "Source").mkdir()
        with self.assertRaisesRegex(ValueError, "inside Production"):
            baseline.apply(nested_working, "nested")
        self.assertFalse((nested_working.parent / "_baseline-state").exists())


if __name__ == "__main__":
    unittest.main()
