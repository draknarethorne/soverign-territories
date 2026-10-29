"""Tests for isolated likeness sandbox reset guards."""
import hashlib
import json
import pathlib
import os
import stat
import tempfile
import unittest
from unittest import mock

from tools.art.likeness_library.sandbox import (
    _remove_tree,
    _recover_full_reset,
    full_reset_apply,
    full_reset_preview,
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
        readonly = self._working_file(
            "Prospects/Generated/gallery/readonly.jpg", b"readonly generated prospect"
        )
        os.chmod(readonly, stat.S_IREAD)
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

    def test_full_reset_preview_classifies_active_files_without_writing(self):
        from tools.workflows import comfy_workflows as cw

        production_files = {
            "Various/gallery/current.jpg": b"current production photo",
            "Angels/Keep/gallery/duplicate.jpg": b"duplicate content",
            "Angels/Keep/gallery/conflict.jpg": b"production version",
        }
        for relative, contents in production_files.items():
            path = self.production / pathlib.Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        storage_roots = {
            name: cw.storage_root(cw.load_cfg(), name, root=self.production)
            for name in cw.STORAGE_ROOT_DEFAULTS
        }
        for root in set(storage_roots.values()) | {self.production / "_archive"}:
            path = root / "not-for-working.bin"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(root.name.encode("ascii"))

        self._working_file(
            "Various/gallery/current.jpg", b"current production photo"
        )
        self._working_file(
            "Various/gallery/copied.jpg", b"duplicate content"
        )
        self._working_file("Various/gallery/new.jpg", b"new source photo")
        self._working_file(
            "Various/gallery/z_history.json", b'{"history": []}'
        )
        self._working_file(
            "Angels/Keep/gallery/conflict.jpg", b"working version"
        )
        unchanged_working = {
            path.relative_to(self.working).as_posix(): path.read_bytes()
            for path in self.working.rglob("*")
            if path.is_file()
        }
        unchanged_production = {
            path.relative_to(self.production).as_posix(): path.read_bytes()
            for path in self.production.rglob("*")
            if path.is_file()
        }

        result = full_reset_preview(self.working, self.production)

        self.assertTrue(result["previewOnly"])
        self.assertFalse(result["resetReady"])
        self.assertEqual(result["resetBlockers"], ["active-path-conflicts"])
        self.assertEqual(result["resetTarget"], str(self.working.resolve()))
        self.assertEqual(result["currentProduction"]["managedFileCount"], 5)
        self.assertEqual(
            result["currentProduction"]["excludedStorageFileCount"],
            8,
        )
        self.assertEqual(
            result["currentProduction"]["wholeRootFileCount"],
            13,
        )
        self.assertIn("_archive", result["currentProduction"]["excludedStorageRoots"])
        self.assertIn("_backup", result["currentProduction"]["excludedStorageRoots"])
        self.assertIn("_reports", result["currentProduction"]["excludedStorageRoots"])
        self.assertNotIn("_junk", result["currentProduction"]["excludedStorageRoots"])
        self.assertNotIn("_retired", result["currentProduction"]["excludedStorageRoots"])
        entries = {
            entry["path"]: entry for entry in result["workingActiveFiles"]
        }
        self.assertEqual(
            set(entries),
            {
                "Various/gallery/copied.jpg",
                "Various/gallery/new.jpg",
                "Various/gallery/z_history.json",
                "Angels/Keep/gallery/conflict.jpg",
            },
        )
        self.assertEqual(
            entries["Various/gallery/copied.jpg"]["status"],
            "already-present-at-different-active-path",
        )
        self.assertIsNone(entries["Various/gallery/copied.jpg"]["destination"])
        self.assertEqual(
            entries["Various/gallery/new.jpg"]["destination"],
            "Various/gallery/new.jpg",
        )
        self.assertEqual(
            entries["Various/gallery/z_history.json"]["status"],
            "review-bundle-metadata",
        )
        self.assertEqual(
            entries["Angels/Keep/gallery/conflict.jpg"]["status"],
            "path-conflict-review-required",
        )
        self.assertEqual(
            entries["Angels/Keep/gallery/conflict.jpg"]["destination"],
            "_reports/reset-review-bundle/path-conflicts/Angels/Keep/gallery/conflict.jpg",
        )
        self.assertEqual(
            unchanged_working,
            {
                path.relative_to(self.working).as_posix(): path.read_bytes()
                for path in self.working.rglob("*")
                if path.is_file()
            },
        )
        self.assertEqual(
            unchanged_production,
            {
                path.relative_to(self.production).as_posix(): path.read_bytes()
                for path in self.production.rglob("*")
                if path.is_file()
            },
        )

    def test_full_reset_preview_flags_unknown_production_roots(self):
        unknown = self.production / "unclassified" / "data.bin"
        unknown.parent.mkdir(parents=True)
        unknown.write_bytes(b"not in the verified baseline")

        result = full_reset_preview(self.working, self.production)

        self.assertFalse(result["resetReady"])
        self.assertEqual(
            result["resetBlockers"], ["unclassified-production-roots"]
        )
        self.assertEqual(
            result["currentProduction"]["unexpectedTopLevelRoots"],
            ["unclassified"],
        )

    def test_full_reset_preview_is_ready_without_conflicts_or_unknown_roots(self):
        result = full_reset_preview(self.working, self.production)

        self.assertTrue(result["resetReady"])
        self.assertEqual(result["resetBlockers"], [])

    def test_full_reset_apply_rebuilds_working_and_preserves_unique_active_files(self):
        from tools.workflows import comfy_workflows as cw

        production_files = {
            "Various/gallery/current.jpg": b"current production photo",
            "Angels/Keep/gallery/duplicate.jpg": b"duplicate content",
        }
        for relative, contents in production_files.items():
            path = self.production / pathlib.Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        storage_roots = {
            name: cw.storage_root(cw.load_cfg(), name, root=self.production)
            for name in cw.STORAGE_ROOT_DEFAULTS
        }
        for root in set(storage_roots.values()) | {self.production / "_archive"}:
            path = root / "discarded.bin"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"storage output")

        self._working_file("_reports/obsolete.md", b"discarded report")
        self._working_file(
            "Various/gallery/new.jpg", b"unique active photo"
        )
        self._working_file(
            "Various/gallery/copied.jpg", b"duplicate content"
        )
        self._working_file(
            "Various/gallery/z_notes.json", b'{"history": []}'
        )
        source_before = {
            path.relative_to(self.source).as_posix(): path.read_bytes()
            for path in self.source.rglob("*")
            if path.is_file()
        }
        receipt = {"configurationHash": "test-hash"}

        result = full_reset_apply(
            self.working,
            self.production,
            storage_receipt=receipt,
        )

        self.assertTrue(result["applied"])
        self.assertFalse(result["previewOnly"])
        self.assertEqual(
            (self.working / "Various/gallery/current.jpg").read_bytes(),
            production_files["Various/gallery/current.jpg"],
        )
        self.assertEqual(
            (self.working / "Angels/Keep/gallery/duplicate.jpg").read_bytes(),
            production_files["Angels/Keep/gallery/duplicate.jpg"],
        )
        self.assertEqual(
            (self.working / "Various/gallery/new.jpg").read_bytes(),
            b"unique active photo",
        )
        self.assertFalse((self.working / "Various/gallery/copied.jpg").exists())
        self.assertFalse((self.working / "_reports/obsolete.md").exists())
        metadata = (
            self.working
            / "_reports/reset-review-bundle/Various/gallery/z_notes.json"
        )
        self.assertEqual(metadata.read_bytes(), b'{"history": []}')
        reset_receipt = json.loads(
            (
                self.working
                / "_reports/reset-review-bundle/full-reset-receipt.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            reset_receipt["configurationReceipt"]["configurationHash"],
            "test-hash",
        )
        self.assertTrue((self.working / "_backup").is_dir())
        self.assertEqual(list((self.working / "_backup").iterdir()), [])
        self.assertEqual(
            (self.working / "_junk/discarded.bin").read_bytes(),
            b"storage output",
        )
        self.assertEqual(
            (self.working / "_retired/discarded.bin").read_bytes(),
            b"storage output",
        )
        self.assertTrue((self.working / "_tmp").is_dir())
        self.assertEqual(list((self.working / "_tmp").iterdir()), [])
        self.assertEqual(
            source_before,
            {
                path.relative_to(self.source).as_posix(): path.read_bytes()
                for path in self.source.rglob("*")
                if path.is_file()
            },
        )
        self.assertTrue((self.production / "_backup/discarded.bin").is_file())

    def test_full_reset_apply_refuses_conflicts_without_changing_working(self):
        production_conflict = self.production / "Angels/Keep/gallery/keep.jpg"
        production_conflict.parent.mkdir(parents=True, exist_ok=True)
        production_conflict.write_bytes(b"production version")
        self._working_file("Angels/Keep/gallery/keep.jpg", b"working version")
        before = (
            self.working / "Angels/Keep/gallery/keep.jpg"
        ).read_bytes()

        with self.assertRaisesRegex(ValueError, "active-path-conflicts"):
            full_reset_apply(self.working, self.production)

        self.assertEqual(
            (self.working / "Angels/Keep/gallery/keep.jpg").read_bytes(),
            before,
        )
        self.assertFalse((self.working / "_tmp").exists())

    def test_full_reset_recovery_rolls_back_interrupted_swap(self):
        temporary_root = self.working / "_tmp"
        stage = temporary_root / "full-reset-stage-interrupted"
        staged = stage / "new"
        previous = stage / "rollback" / "old"
        (staged / "Angels").mkdir(parents=True)
        (staged / "_reports").mkdir()
        previous.mkdir(parents=True)
        old_angel = self._working_file("Angels/Keep/gallery/old.jpg", b"old angel")
        old_report = self._working_file("_reports/old.md", b"old report")
        new_angel = staged / "Angels/new.jpg"
        new_angel.write_bytes(b"new angel")
        new_report = staged / "_reports/new.md"
        new_report.write_bytes(b"new report")
        temporary_root.mkdir(parents=True, exist_ok=True)
        lock_path = stage.with_name(stage.name + ".lock")
        lock_path.write_bytes(b"\0")
        journal = {
            "schemaVersion": 1,
            "target": str(self.working.resolve()),
            "stageName": stage.name,
            "phase": "swapping",
            "oldEntries": ["Angels", "_reports"],
            "newEntries": ["Angels", "_reports"],
        }
        (temporary_root / "full-reset-transaction.json").write_text(
            json.dumps(journal), encoding="utf-8"
        )
        (self.working / "Angels").rename(previous / "Angels")
        (staged / "Angels").rename(self.working / "Angels")

        self.assertTrue(_recover_full_reset(temporary_root, self.working.resolve()))

        self.assertEqual(old_angel.read_bytes(), b"old angel")
        self.assertEqual(old_report.read_bytes(), b"old report")
        self.assertFalse((self.working / "Angels/new.jpg").exists())
        self.assertFalse((self.working / "_reports/new.md").exists())
        self.assertFalse(stage.exists())
        self.assertFalse(lock_path.exists())
        self.assertFalse((temporary_root / "full-reset-transaction.json").exists())

    def test_full_reset_recovery_finishes_cleanup_after_commit(self):
        temporary_root = self.working / "_tmp"
        stage = temporary_root / "full-reset-stage-committed"
        new = stage / "new"
        previous = stage / "rollback" / "old"
        new.mkdir(parents=True)
        previous.mkdir(parents=True)
        self._working_file("Angels/new.jpg", b"new angel")
        (previous / "Angels").mkdir()
        (previous / "Angels/old.jpg").write_bytes(b"old angel")
        temporary_root.mkdir(parents=True, exist_ok=True)
        lock_path = stage.with_name(stage.name + ".lock")
        lock_path.write_bytes(b"\0")
        journal = {
            "schemaVersion": 1,
            "target": str(self.working.resolve()),
            "stageName": stage.name,
            "phase": "committed",
            "oldEntries": ["Angels"],
            "newEntries": ["Angels"],
        }
        (temporary_root / "full-reset-transaction.json").write_text(
            json.dumps(journal), encoding="utf-8"
        )

        self.assertTrue(_recover_full_reset(temporary_root, self.working.resolve()))

        self.assertEqual((self.working / "Angels/new.jpg").read_bytes(), b"new angel")
        self.assertFalse(stage.exists())
        self.assertFalse(lock_path.exists())
        self.assertFalse((temporary_root / "full-reset-transaction.json").exists())

    def test_apply_after_committed_cleanup_does_not_reset_again(self):
        temporary_root = self.working / "_tmp"
        temporary_root.mkdir()
        receipt = {
            "productionFileCount": 3,
            "productionBytes": 123,
            "carryForwardCounts": {"activePhotos": 1, "metadata": 1},
        }
        self._working_file(
            "_reports/reset-review-bundle/full-reset-receipt.json",
            json.dumps(receipt).encode("utf-8"),
        )
        retained = self._working_file(
            "_reports/reset-review-bundle/Various/gallery/z_notes.json",
            b'{"history": []}',
        )
        with mock.patch(
            "tools.art.likeness_library.sandbox._recover_full_reset",
            return_value="committed",
        ), mock.patch(
            "tools.art.likeness_library.sandbox._full_reset_analysis",
        ) as analysis:
            result = full_reset_apply(self.working, self.production)

        analysis.assert_not_called()
        self.assertTrue(result["recoveredCommittedReset"])
        self.assertEqual(result["carryForwardCounts"], receipt["carryForwardCounts"])
        self.assertEqual(retained.read_bytes(), b'{"history": []}')

    @unittest.skipUnless(os.name == "nt", "Windows extended-length cleanup")
    def test_reset_cleanup_removes_nested_paths_beyond_max_path(self):
        from tools.art.library_backup import _snapshot_path

        stage = self.working / "_tmp" / "full-reset-stage-long-path"
        nested = stage / "rollback" / "old" / "_backup" / ("snapshot-" + "x" * 100)
        nested = nested / "work-root" / "_reports" / "library" / "people_gallery_review_files"
        extended = _snapshot_path(nested)
        extended.mkdir(parents=True)
        photo = extended / ("person_image_" + "1" * 40 + "_head.jpg")
        photo.write_bytes(b"generated thumbnail")
        self.assertGreater(len(str(nested / photo.name)), 260)

        _remove_tree(stage)

        self.assertFalse(stage.exists())
        self.assertTrue(self.working.is_dir())

    def test_full_reset_preview_rejects_production_root_different_from_manifest(self):
        other_production = self.base / "Other Library"
        other_production.mkdir()

        with self.assertRaisesRegex(ValueError, "does not match the verified sandbox manifest"):
            full_reset_preview(self.working, other_production)

    def test_reset_uses_configured_working_local_state_root(self):
        state = self.working / "_tmp" / "reset-state"

        result = reset_generated_categories(
            self.working, apply=True, state_root=state
        )

        self.assertTrue(result["applied"])
        self.assertTrue(state.is_dir())
        self.assertEqual(list(state.iterdir()), [])
        self.assertFalse((self.working / "_sandbox-state").exists())

    def test_reset_rejects_state_root_outside_working(self):
        with self.assertRaisesRegex(ValueError, "sandbox state must stay inside Working"):
            reset_generated_categories(
                self.working, apply=True, state_root=self.production / "_sandbox-state"
            )
        self.assertFalse((self.production / "Prospects").exists())

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
