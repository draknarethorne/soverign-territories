#!/usr/bin/env python3
"""library_backup: complete snapshots and safety checks."""
import json
import pathlib
import shutil
import tempfile
import unittest

from library_backup import create_backup, verify_backup


class LibraryBackupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.work = self.tmp / "work"
        self.inputs = self.tmp / "inputs"
        self.repo = self.tmp / "repo" / "workspaces.json"
        self.work.mkdir()
        self.inputs.mkdir()
        self.repo.parent.mkdir()
        (self.work / "Various" / "gallery").mkdir(parents=True)
        (self.work / "Various" / "gallery" / "incoming.jpg").write_bytes(b"incoming")
        (self.work / "_archive").mkdir()
        (self.work / "_archive" / "old.jpg").write_bytes(b"old archive content")
        (self.work / "_backup" / "prior").mkdir(parents=True)
        (self.work / "_backup" / "prior" / "snapshot").write_bytes(b"prior")
        (self.inputs / "Angel Primes").mkdir()
        (self.inputs / "Angel Primes" / "prime.png").write_bytes(b"input")
        self.repo.write_text('{"photos": {}}', encoding="utf-8")

    def test_preview_does_not_write_backup(self):
        destination = create_backup(self.work, self.inputs, self.repo, stamp="preview", apply=False)
        self.assertIsNone(destination)
        self.assertFalse((self.work / "_backup" / "library-preview").exists())

    def test_snapshot_excludes_work_archive_and_prior_backups_but_copies_inputs_and_config(self):
        destination = create_backup(self.work, self.inputs, self.repo, stamp="test", apply=True)
        self.assertEqual((destination / "work-root/Various/gallery/incoming.jpg").read_bytes(), b"incoming")
        self.assertFalse((destination / "work-root/_archive").exists())
        self.assertEqual((destination / "comfy-inputs/Angel Primes/prime.png").read_bytes(), b"input")
        self.assertEqual((destination / "repository-config/workspaces.json").read_bytes(), self.repo.read_bytes())
        self.assertFalse((destination / "work-root/_backup/prior/snapshot").exists())
        manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "complete")
        self.assertEqual(manifest["files"], 3)
        self.assertTrue(manifest["sources"][0]["exclude_library_storage"])
        self.assertEqual(len(manifest["entries"][0]["sha256"]), 64)

    def test_existing_snapshot_is_never_overwritten(self):
        first = create_backup(self.work, self.inputs, self.repo, stamp="same", apply=True)
        with self.assertRaises(FileExistsError):
            create_backup(self.work, self.inputs, self.repo, stamp="same", apply=True)
        self.assertTrue((first / "manifest.json").exists())

    def test_verification_rejects_a_changed_snapshot_file(self):
        destination = create_backup(self.work, self.inputs, self.repo, stamp="verify", apply=True)
        verify_backup(destination)
        (destination / "work-root/Various/gallery/incoming.jpg").write_bytes(b"tampered")
        with self.assertRaisesRegex(OSError, "checksum mismatch"):
            verify_backup(destination)

    def test_extra_repository_source_is_copied_and_verified(self):
        catalogue = self.tmp / "repo" / "likeness-library.json"
        catalogue.write_text('{"schemaVersion": 1}\n', encoding="utf-8")
        destination = create_backup(
            self.work,
            self.inputs,
            self.repo,
            stamp="extra-source",
            apply=True,
            extra_sources=[("likeness-catalogue", catalogue)],
        )
        snapshot_copy = destination / "likeness-catalogue" / catalogue.name
        self.assertEqual(snapshot_copy.read_bytes(), catalogue.read_bytes())
        self.assertTrue(verify_backup(destination))


if __name__ == "__main__":
    unittest.main()
