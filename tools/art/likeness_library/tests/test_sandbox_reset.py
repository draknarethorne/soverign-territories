"""Tests for isolated likeness sandbox reset guards."""
import hashlib
import json
import pathlib
import tempfile
import unittest

from tools.art.likeness_library.sandbox import (
    is_sandbox_working_path,
    require_sandbox_cache,
    require_sandbox_output,
    reset_generated_categories,
)


class SandboxResetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self.temp.name)
        self.sandbox = self.base / "Sovereign Territories Sandbox"
        self.source = self.sandbox / "Source"
        self.working = self.sandbox / "Working"
        self.production = self.base / "Sovereign Territories"
        self.source.mkdir(parents=True)
        self.working.mkdir()
        self.production.mkdir()
        self.source_files = {
            "Prospects/Seed/gallery/seed.jpg": b"seed prospect",
            "Potentials/Seed/gallery/seed.jpg": b"seed potential",
            "Angels/Keep/gallery/keep.jpg": b"untouched source",
        }
        for relative, contents in self.source_files.items():
            path = self.source / pathlib.Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        self.manifest = {
            "schemaVersion": 1,
            "sourceRoot": str(self.production),
            "snapshotRoot": "Source",
            "workingRootAtCreation": "Working",
            "fileCount": len(self.source_files),
            "totalBytes": sum(map(len, self.source_files.values())),
            "files": [
                {
                    "path": relative,
                    "bytes": len(contents),
                    "sha256": hashlib.sha256(contents).hexdigest(),
                }
                for relative, contents in self.source_files.items()
            ],
        }
        (self.sandbox / "source-manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def _working_file(self, relative, contents):
        path = self.working / pathlib.Path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
        return path

    def test_reset_restores_only_allowlisted_category_roots(self):
        self._working_file("Models/Generated/model.jpg", b"generated model")
        self._working_file("Prospects/Generated/gallery/old.jpg", b"generated prospect")
        self._working_file("Potentials/Generated/gallery/old.jpg", b"generated potential")
        self._working_file("Angels/Keep/gallery/keep.jpg", b"working angel")
        self._working_file("_reports/keep.md", b"report")
        self._working_file("_sandbox-state/likeness-cache.json", b"cache")

        result = reset_generated_categories(self.working, apply=True)

        self.assertTrue(result["applied"])
        self.assertFalse((self.working / "Models").exists())
        self.assertEqual(
            (self.working / "Prospects/Seed/gallery/seed.jpg").read_bytes(),
            b"seed prospect",
        )
        self.assertEqual(
            (self.working / "Potentials/Seed/gallery/seed.jpg").read_bytes(),
            b"seed potential",
        )
        self.assertEqual(
            (self.working / "Angels/Keep/gallery/keep.jpg").read_bytes(),
            b"working angel",
        )
        self.assertEqual((self.working / "_reports/keep.md").read_bytes(), b"report")
        self.assertEqual(
            (self.working / "_sandbox-state/likeness-cache.json").read_bytes(),
            b"cache",
        )
        self.assertEqual(
            (self.source / "Prospects/Seed/gallery/seed.jpg").read_bytes(),
            b"seed prospect",
        )

    def test_preview_does_not_modify_working_copy(self):
        old = self._working_file("Prospects/Generated/old.jpg", b"old")

        result = reset_generated_categories(self.working)

        self.assertFalse(result["applied"])
        self.assertEqual(old.read_bytes(), b"old")

    def test_rejects_non_sandbox_root_before_writing(self):
        with self.assertRaisesRegex(ValueError, "Working directory"):
            reset_generated_categories(self.production, apply=True)
        self.assertFalse((self.production / "Prospects").exists())

    def test_rejects_modified_source_before_writing(self):
        self._working_file("Prospects/Generated/old.jpg", b"old")
        changed = self.source / "Prospects/Seed/gallery/seed.jpg"
        changed.write_bytes(b"modified")

        with self.assertRaisesRegex(ValueError, "size mismatch|checksum mismatch"):
            reset_generated_categories(self.working, apply=True)

        self.assertEqual(
            (self.working / "Prospects/Generated/old.jpg").read_bytes(),
            b"old",
        )

    def test_rejects_manifest_path_traversal(self):
        self.manifest["files"][0]["path"] = "../outside.jpg"
        (self.sandbox / "source-manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "invalid source-manifest path"):
            reset_generated_categories(self.working, apply=True)

    def test_rejects_manifest_that_does_not_identify_the_sibling_library(self):
        self.manifest["sourceRoot"] = str(self.sandbox / "wrong-source")
        (self.sandbox / "source-manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "sibling of the named production"):
            reset_generated_categories(self.working, apply=True)

    def test_sandbox_cache_and_report_paths_must_stay_inside_working(self):
        self.assertTrue(is_sandbox_working_path(self.working))
        cache = self.working / "_sandbox-state" / "cache.json"
        report = self.working / "_reports" / "diagnostics"
        self.assertEqual(require_sandbox_cache(self.working, cache), cache.resolve())
        self.assertEqual(require_sandbox_output(self.working, report), report.resolve())
        with self.assertRaisesRegex(ValueError, "explicit Working-local"):
            require_sandbox_cache(self.working, None)
        with self.assertRaisesRegex(ValueError, "cache must stay inside Working"):
            require_sandbox_cache(self.working, self.production / "cache.json")
        with self.assertRaisesRegex(ValueError, "output must stay inside Working"):
            require_sandbox_output(self.working, self.production / "report")


if __name__ == "__main__":
    unittest.main()
