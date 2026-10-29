#!/usr/bin/env python3
"""library_backup: complete snapshots and safety checks."""
import hashlib
import json
import os
import pathlib
import shutil
import tempfile
import unittest
import copy
from unittest import mock

import library_backup
from library_backup import (
    _snapshot_path, create_backup, latest_work_root_backup, preview, restore_backup, verify_backup,
)
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

    def artist_reports(self):
        report = self.work / "_reports" / "artists"
        paths = {
            "artists_gallery.html": b"generated artist browser",
            "artists_gallery_review.html": b"generated artist review",
            "thumbnails/" + "a" * 64 + ".jpg": b"generated thumbnail",
        }
        for relative, payload in paths.items():
            target = report / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        manifest = {
            "formatVersion": 1,
            "recipe": "artists-gallery-v1",
            "files": {relative: hashlib.sha256(payload).hexdigest() for relative, payload in paths.items()},
            "inputs": [{"source": "Artists/Example/gallery/photo.jpg", "sha256": "b" * 64}],
            "diagnostics": ["retained recovery context"],
        }
        (report / "gallery-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return report, paths, manifest

    def test_routine_backup_omits_only_verified_artist_outputs_and_restores_recovery_data(self):
        report, generated, _manifest = self.artist_reports()
        retained = {
            "_reports/artists/gallery-manifest.json": (report / "gallery-manifest.json").read_bytes(),
            "_reports/artists/notes.txt": b"user report notes",
            "_reports/artists/thumbnails/user-photo.jpg": b"user asset",
            "_reports/preparation/run/raw/source.jpg": b"raw retention original",
            "_reports/preparation/run/report.html": b"preparation evidence",
            "_reports/library/people_gallery.html": b"unproven legacy generated page",
            "_reports/library/people_gallery_review_files/photo_head_123456abcdef.jpg": b"unproven cache",
            "_likeness/artists/faces.npz": b"embedding cache",
            "_likeness/general/history.json": b"history",
            "Artists/Example/gallery/photo.jpg": b"original gallery photo",
            "Artists/Example/review/review.jpg": b"original review photo",
            "Artists/Example/metadata.json": b"placement metadata",
        }
        for relative, payload in retained.items():
            target = self.work / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        catalogue = self.repo.parent / "catalogue.json"
        catalogue.write_bytes(b"catalogue recovery")
        destination = create_backup(
            self.work, self.inputs, self.repo, stamp="artist-reports", apply=True,
            extra_sources=[("catalogue", catalogue)],
        )
        manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["generatedReports"]), len(generated))
        self.assertEqual(manifest["regenerable"], [])
        receipt = manifest["configurationReceipt"]
        self.assertEqual(len(receipt["effectiveConfigurationSha256"]), 64)
        self.assertEqual(
            receipt["resolvedPaths"]["libraryRoot"], str(self.work.resolve())
        )
        self.assertEqual(
            receipt["resolvedPaths"]["backupDestination"], str(destination.resolve())
        )
        self.assertTrue(verify_backup(destination))
        recovered = restore_backup(destination, self.tmp / "recovered", apply=True)
        for relative in generated:
            self.assertFalse((recovered / "work-root" / "_reports" / "artists" / relative).exists())
        for relative, payload in retained.items():
            self.assertEqual((recovered / "work-root" / relative).read_bytes(), payload)
        self.assertEqual((recovered / "catalogue" / catalogue.name).read_bytes(), catalogue.read_bytes())

    def test_full_and_transaction_backups_retain_generated_artist_outputs(self):
        _report, generated, _manifest = self.artist_reports()
        for stamp, options, label in (
            ("full-artists", {"include_regenerable": True}, "work-root"),
            ("scoped-artists", {"scoped_sources": [("reports", self.work / "_reports")]}, "reports"),
        ):
            with self.subTest(stamp=stamp):
                destination = create_backup(self.work, stamp=stamp, apply=True, **options)
                manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["generatedReports"], [])
                for relative, payload in generated.items():
                    prefix = "_reports/artists" if label == "work-root" else "artists"
                    self.assertEqual((destination / label / prefix / relative).read_bytes(), payload)

    def test_edited_unlisted_and_nonmanaged_manifest_entries_are_retained(self):
        report, _generated, manifest = self.artist_reports()
        (report / "artists_gallery.html").write_bytes(b"user-edited browser")
        unknown = "thumbnails/" + "c" * 64 + ".jpg"
        (report / unknown).write_bytes(b"unlisted thumbnail")
        for relative in ("notes.txt", "../preparation/raw.jpg", "thumbnails/not-a-hash.jpg"):
            target = report / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"user-owned")
            manifest["files"][relative] = hashlib.sha256(b"user-owned").hexdigest()
        (report / "gallery-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        destination = create_backup(self.work, stamp="retain-edits", apply=True)
        for relative in ("artists_gallery.html", unknown, "notes.txt", "thumbnails/not-a-hash.jpg"):
            self.assertEqual((destination / "work-root/_reports/artists" / relative).read_bytes(),
                             (report / relative).read_bytes())
        self.assertEqual((destination / "work-root/_reports/preparation/raw.jpg").read_bytes(), b"user-owned")

    def test_missing_invalid_or_unsupported_artist_manifest_retains_outputs(self):
        report, generated, manifest = self.artist_reports()
        for index, content in enumerate((
            None, "{", "[]", json.dumps({**manifest, "formatVersion": 2}),
            json.dumps({**manifest, "recipe": "unknown"}), json.dumps({**manifest, "files": []}),
        )):
            with self.subTest(content=content):
                manifest_path = report / "gallery-manifest.json"
                if content is None:
                    manifest_path.unlink()
                else:
                    manifest_path.write_text(content, encoding="utf-8")
                destination = create_backup(self.work, stamp=f"invalid-artist-{index}", apply=True)
                for relative, payload in generated.items():
                    self.assertEqual((destination / "work-root/_reports/artists" / relative).read_bytes(), payload)

    def test_preview_agrees_with_routine_artist_report_omissions(self):
        _report, generated, _manifest = self.artist_reports()
        entries, total = preview(self.work, self.inputs, self.repo)
        relative_paths = {relative.as_posix() for label, _path, relative, _size in entries if label == "work-root"}
        self.assertIn("_reports/artists/gallery-manifest.json", relative_paths)
        self.assertTrue(all("_reports/artists/" + relative not in relative_paths for relative in generated))
        self.assertEqual(total, sum(size for _label, _path, _relative, size in entries))
        self.assertIsNone(create_backup(self.work, stamp="artist-preview", apply=False))
        self.assertFalse((self.work / "_backup/library-artist-preview").exists())

    def people_reports(self):
        report = self.work / "_reports" / "library"
        paths = {
            "people_gallery.html": b"generated people browser",
            "people_gallery_review.html": b"generated people review",
            "people_gallery.md": b"generated people markdown",
            "people_gallery_review_files/person_image_123456_head_abcdef123456.jpg": b"head thumbnail",
            "people_gallery_review_files/person_image_123456_chest_abcdef123456.jpg": b"chest thumbnail",
            "people_gallery_review_files/person_image_123456_face_abcdef123456.jpg": b"face thumbnail",
        }
        for relative, payload in paths.items():
            target = report / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        manifest = {
            "formatVersion": 1, "recipe": "people-gallery-v1",
            "files": {relative: hashlib.sha256(payload).hexdigest() for relative, payload in paths.items()},
        }
        (report / "people-gallery-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return report, paths, manifest

    def test_verified_people_outputs_are_omitted_but_manifest_and_unknown_evidence_restore(self):
        report, generated, manifest = self.people_reports()
        retained = {
            "identity-rankings.md": b"retain evidence",
            "prospect-cast-audit.csv": b"retain audit",
            "people_gallery_review_files/user.jpg": b"user image",
            "people_gallery_review_files/unlisted_head_123456abcdef.jpg": b"unlisted cache",
            "../preparation/run/raw.jpg": b"raw retention",
        }
        for relative, payload in retained.items():
            target = report / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            manifest["files"][relative] = hashlib.sha256(payload).hexdigest()
        del manifest["files"]["people_gallery_review_files/unlisted_head_123456abcdef.jpg"]
        manifest_path = report / "people-gallery-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        entries, _total = preview(self.work)
        self.assertFalse(any(relative.as_posix() == "_reports/library/people_gallery.html"
                             for _label, _path, relative, _size in entries))
        destination = create_backup(self.work, stamp="people-owned", apply=True)
        snapshot_manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(snapshot_manifest["generatedReports"]), len(generated))
        self.assertTrue(all(row["recipe"] == "people-gallery-v1"
                            and row["manifestBackup"] == "work-root/_reports/library/people-gallery-manifest.json"
                            for row in snapshot_manifest["generatedReports"]))
        recovered = restore_backup(destination, self.tmp / "people-recovery", apply=True)
        for relative in generated:
            self.assertFalse((recovered / "work-root/_reports/library" / relative).exists())
        for relative, payload in retained.items():
            self.assertEqual((recovered / "work-root/_reports/library" / relative).read_bytes(), payload)
        self.assertEqual((recovered / "work-root/_reports/library/people-gallery-manifest.json").read_bytes(),
                         manifest_path.read_bytes())

    def test_people_outputs_without_supported_manifest_and_edited_files_are_retained(self):
        report, generated, manifest = self.people_reports()
        manifest_path = report / "people-gallery-manifest.json"
        for index, content in enumerate((
            None, "{", json.dumps({**manifest, "formatVersion": 2}),
            json.dumps({**manifest, "recipe": "artists-gallery-v1"}),
        )):
            with self.subTest(content=content):
                if content is None:
                    manifest_path.unlink()
                else:
                    manifest_path.write_text(content, encoding="utf-8")
                destination = create_backup(self.work, stamp=f"people-unproven-{index}", apply=True)
                for relative, payload in generated.items():
                    self.assertEqual((destination / "work-root/_reports/library" / relative).read_bytes(), payload)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        edited = ("people_gallery.html", "people_gallery_review_files/person_image_123456_head_abcdef123456.jpg")
        for relative in edited:
            (report / relative).write_bytes(b"user edit")
        destination = create_backup(self.work, stamp="people-edited", apply=True)
        for relative in edited:
            self.assertEqual((destination / "work-root/_reports/library" / relative).read_bytes(), b"user edit")

    def test_full_and_transaction_people_snapshots_keep_generated_files(self):
        report, generated, _manifest = self.people_reports()
        for stamp, options, prefix in (
            ("people-full", {"include_regenerable": True}, "work-root/_reports/library"),
            ("people-transaction", {"scoped_sources": [("report", report)]}, "report"),
        ):
            with self.subTest(stamp=stamp):
                destination = create_backup(self.work, stamp=stamp, apply=True, **options)
                for relative, payload in generated.items():
                    self.assertEqual((destination / prefix / relative).read_bytes(), payload)
                manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["generatedReports"], [])

    def test_full_snapshot_mode_keeps_regenerable_derivatives(self):
        omissions = {
            "Various/gallery/incoming.jpg": {
                "backup": "work-root/Various/gallery/incoming.jpg",
                "sourceBackup": "work-root/Various/gallery/incoming.jpg",
                "sourceSha256": "x",
                "sha256": "x",
                "recipe": 1,
                "framing": "padded",
                "box": None,
                "size": 8,
                "mtimeNs": 0,
                "atimeNs": 0,
            }
        }
        with mock.patch("library_backup.derivative_omissions", return_value=omissions), \
                mock.patch("library_backup.verify_backup", return_value=True):
            default = create_backup(self.work, self.inputs, self.repo, stamp="omit-default", apply=True)
            full = create_backup(
                self.work, self.inputs, self.repo, stamp="include-full", apply=True, include_regenerable=True
            )
        default_manifest = json.loads((default / "manifest.json").read_text(encoding="utf-8"))
        full_manifest = json.loads((full / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(default_manifest["regenerable"], list(omissions.values()))
        self.assertEqual(
            len([
                row for row in default_manifest["entries"]
                if row["backup"].replace("\\", "/") == "work-root/Various/gallery/incoming.jpg"
            ]),
            0,
        )
        self.assertEqual(full_manifest["regenerable"], [])
        self.assertEqual(
            len([
                row for row in full_manifest["entries"]
                if row["backup"].replace("\\", "/") == "work-root/Various/gallery/incoming.jpg"
            ]),
            1,
        )

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

    def test_configured_storage_roots_are_used_and_backup_is_not_copied_into_itself(self):
        backup_root = self.work / "operations" / "backups"
        prior = backup_root / "prior" / "snapshot"
        prior.parent.mkdir(parents=True)
        prior.write_bytes(b"old snapshot")
        report = self.work / "operations" / "reports" / "artists"
        report.mkdir(parents=True)
        generated = b"managed browser page"
        (report / "artists_gallery.html").write_bytes(generated)
        (report / "gallery-manifest.json").write_text(json.dumps({
            "formatVersion": 1,
            "recipe": "artists-gallery-v1",
            "files": {"artists_gallery.html": hashlib.sha256(generated).hexdigest()},
        }), encoding="utf-8")
        (report / "notes.txt").write_text("retain report notes", encoding="utf-8")
        cfg = copy.deepcopy(library_backup.cw.load_cfg())
        cfg["installsRoot"] = str(self.tmp / "installs")
        cfg["paths"].update({
            "productionRoot": str(self.tmp / "production"),
            "sandboxWorkingRoot": str(self.tmp / "sandbox"),
            "modelCacheRoot": str(self.tmp / "models"),
            "inputsRoot": str(self.tmp / "configured-inputs"),
            "outputRoot": str(self.tmp / "configured-outputs"),
        })
        cfg["sharedInput"] = str(self.tmp / "shared-input")
        cfg["sharedOutput"] = str(self.tmp / "shared-output")
        cfg["storageRoots"].update({
            "backup": "operations/backups",
            "reports": "operations/reports",
        })
        with mock.patch("library_backup.cw.load_cfg", return_value=cfg):
            destination = create_backup(self.work, self.inputs, self.repo, stamp="configured", apply=True)
            latest = latest_work_root_backup(self.work)
        self.assertEqual(destination, backup_root / "library-configured")
        self.assertEqual(latest, destination)
        self.assertFalse((destination / "work-root/operations/backups").exists())
        self.assertFalse((destination / "work-root/operations/reports/artists/artists_gallery.html").exists())
        self.assertTrue((destination / "work-root/operations/reports/artists/gallery-manifest.json").is_file())
        self.assertEqual(
            (destination / "work-root/operations/reports/artists/notes.txt").read_text(encoding="utf-8"),
            "retain report notes",
        )

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
