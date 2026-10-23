#!/usr/bin/env python3
"""library_backup: complete snapshots and safety checks."""
import json
import os
import pathlib
import shutil
import tempfile
import unittest

from library_backup import _snapshot_path, create_backup, verify_backup
from likeness_library import metadata


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

    def test_scoped_backup_rejects_unsafe_or_duplicate_labels(self):
        for labels in (["../escape"], ["same", "same"], []):
            with self.subTest(labels=labels):
                with self.assertRaises(ValueError):
                    create_backup(self.work, stamp="unsafe", scoped_sources=[
                        (label, self.repo) for label in labels
                    ])
        self.assertFalse((self.work / "_backup" / "library-unsafe").exists())

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

    def test_snapshot_path_is_absolute_and_idempotent(self):
        path = _snapshot_path(self.work / "_backup" / "snapshot")
        self.assertTrue(path.is_absolute())
        self.assertEqual(_snapshot_path(path), path)
        if os.name == "nt":
            self.assertTrue(str(path).startswith("\\\\?\\"))
        else:
            self.assertEqual(path, (self.work / "_backup" / "snapshot").resolve())

    @unittest.skipUnless(os.name == "nt", "Windows extended-length backup paths")
    def test_nested_source_can_exceed_max_path_only_in_snapshot(self):
        stamp = "likeness-actions-batch_" + "a" * 32
        relative = pathlib.Path("_sandbox-state")
        while len(str(self.work / "_backup" / f"library-{stamp}" / "work-root" / relative / "photo.jpg")) <= 280:
            relative /= "nested-state"
        source = self.work / relative / "photo.jpg"
        self.assertLess(len(str(source)), 260)
        source.parent.mkdir(parents=True)
        source.write_bytes(b"retained sandbox evidence")

        destination = create_backup(self.work, self.inputs, self.repo, stamp=stamp, apply=True)
        target = _snapshot_path(destination) / "work-root" / relative / source.name
        self.assertGreater(len(str(target)), 260)
        self.assertEqual(target.read_bytes(), source.read_bytes())
        manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
        entry = next(row for row in manifest["entries"] if row["source"] == str(source))
        self.assertFalse(pathlib.Path(entry["backup"]).is_absolute())
        self.assertTrue(verify_backup(destination))
        target.write_bytes(b"changed")
        with self.assertRaisesRegex(OSError, "size mismatch|checksum mismatch"):
            verify_backup(destination)

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

    def test_restored_photo_retains_its_stable_id_and_content_hash(self):
        photo = self.work / "Prospects" / "Sophie" / "gallery" / "sophie_image_123456.jpg"
        photo.parent.mkdir(parents=True)
        photo.write_bytes(b"photo bytes")
        photo_id = metadata.photo_id_from_name(photo.name)
        content_hash = metadata.content_sha256(photo)

        destination = create_backup(self.work, self.inputs, self.repo, stamp="restore-id", apply=True)
        saved_photo = destination / "work-root" / "Prospects" / "Sophie" / "gallery" / photo.name
        restored = self.work / "Prospects" / "Sydney Sky" / "gallery" / "sydney_sky_image_123456.jpg"
        restored.parent.mkdir(parents=True)
        shutil.copy2(saved_photo, restored)

        self.assertEqual(metadata.photo_id_from_name(restored.name), photo_id)
        self.assertEqual(metadata.content_sha256(restored), content_hash)
        self.assertTrue(verify_backup(destination))


if __name__ == "__main__":
    unittest.main()
