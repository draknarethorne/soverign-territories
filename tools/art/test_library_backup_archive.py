"""Lossless archive experiment, isolated under ignored repository tmp."""
import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import unittest
import uuid
import warnings
import zipfile
from unittest import mock

import library_backup as backup
import library_backup_archive as archive


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.root = backup.ROOT / "tmp" / ("backup-archive-tests-" + uuid.uuid4().hex)
        archive.output_path(self.root)
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root, True)
        quiet = contextlib.redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)
        self.work = self.root / "work"
        gallery = self.work / "People" / "Example" / "gallery"
        gallery.mkdir(parents=True)
        (gallery / "a.jpg").write_bytes(b"identical image payload")
        (gallery / "b.png").write_bytes(b"identical image payload")
        (self.work / "notes.json").write_bytes(b'{"recovery":"keep exact bytes"}\r\n')
        (self.work / "empty").mkdir()
        for path in self.work.rglob("*"):
            os.utime(path, ns=(1_700_000_000_123456700, 1_700_000_000_123456700))
        os.utime(gallery / "b.png", ns=(1_700_000_000_987654300, 1_700_000_000_987654300))
        self.snapshot = backup.create_backup(self.work, stamp="fixture", apply=True)
        self.bundle = self.root / "bundle"

    def pack(self, kind="hybrid"):
        return archive.pack(self.snapshot, self.bundle, kind=kind, apply=True)

    def reseal(self):
        receipt_path = self.bundle / "receipt.json"
        receipt = json.loads(receipt_path.read_bytes())
        receipt["archiveSha256"] = archive.file_hash(self.bundle / "payload.zip")
        receipt["archiveBytes"] = (self.bundle / "payload.zip").stat().st_size
        receipt.pop("sealSha256")
        receipt["sealSha256"] = archive.sha(archive.canonical(receipt))
        receipt_path.write_bytes(archive.canonical(receipt))

    def rewrite_zip(self, transform):
        path = self.bundle / "payload.zip"
        with zipfile.ZipFile(path) as src:
            members = [(info, src.read(info)) for info in src.infolist()]
        members = transform(members)
        with zipfile.ZipFile(path, "w", allowZip64=True) as dst:
            for info, payload in members:
                dst.writestr(info, payload)
        self.reseal()

    def assert_no_stage(self):
        self.assertFalse(self.bundle.exists())
        self.assertFalse(self.bundle.with_name("bundle.packing").exists())

    def test_roundtrip_exact_snapshot_and_original_restore(self):
        original = archive.inventory(self.snapshot)
        manifest_bytes = (self.snapshot / "manifest.json").read_bytes()
        receipt = self.pack()
        self.assertLess(receipt["metrics"]["uniquePayloads"], receipt["metrics"]["fileCount"])
        self.assertLess(receipt["metrics"]["uniqueBytes"], receipt["metrics"]["logicalBytes"])
        # Independent check must not consult even the original directory.
        shutil.rmtree(self.snapshot)
        checked, index = archive.check_bundle(self.bundle)
        self.assertEqual(receipt, checked)
        self.assertEqual(original, index)
        materialized = self.root / "materialized"
        archive.restore(self.bundle, materialized)
        self.assertFalse(materialized.exists())
        archive.restore(self.bundle, materialized, apply=True)
        self.assertEqual(archive.inventory(materialized), original)
        self.assertEqual((materialized / "manifest.json").read_bytes(), manifest_bytes)
        self.assertTrue(backup.verify_backup(materialized))
        recovered = backup.restore_backup(materialized, self.root / "recovered", apply=True)
        for row in original["files"]:
            if row["path"] == "manifest.json":
                continue
            actual = recovered / row["path"]
            self.assertEqual(archive.file_hash(actual), row["sha256"])
            self.assertEqual(actual.stat().st_mtime_ns, row["mtimeNs"])
        self.assertTrue((materialized / "work-root" / "empty").is_dir())
        with self.assertRaisesRegex(ValueError, "NEW"):
            archive.restore(self.bundle, materialized, apply=True)

    def test_real_regenerable_metadata_and_derivatives_survive(self):
        from PIL import Image
        from likeness_library import derivatives
        work = self.root / "derivative-work"
        source = work / "People" / "Photo" / "gallery" / "source.png"
        source.parent.mkdir(parents=True)
        Image.new("RGB", (80, 120), (70, 95, 160)).save(source)
        derivatives.maintain(source, None, 0, apply=True)
        target = source.parent.parent / derivatives.relative_target(source, "padded")
        expected = target.read_bytes()
        mtime = target.stat().st_mtime_ns
        report = work / "_reports" / "artists"
        report.mkdir(parents=True)
        page = b"generated browser, recover from retained metadata"
        (report / "artists_gallery.html").write_bytes(page)
        report_manifest = {
            "formatVersion": 1, "recipe": "artists-gallery-v1",
            "files": {"artists_gallery.html": archive.sha(page)},
            "inputs": [{"source": source.relative_to(work).as_posix()}],
        }
        (report / "gallery-manifest.json").write_text(json.dumps(report_manifest), encoding="utf-8")
        snapshot = backup.create_backup(work, stamp="derivative", apply=True)
        manifest = (snapshot / "manifest.json").read_bytes()
        self.assertEqual(len(json.loads(manifest)["regenerable"]), 1)
        self.assertEqual(len(json.loads(manifest)["generatedReports"]), 1)
        bundle = self.root / "derivative-bundle"
        archive.pack(snapshot, bundle, apply=True)
        shutil.rmtree(snapshot)
        archive.check_bundle(bundle)
        materialized = archive.restore(bundle, self.root / "derivative-materialized", apply=True)
        self.assertEqual((materialized / "manifest.json").read_bytes(), manifest)
        self.assertTrue(backup.verify_backup(materialized))
        recovered = backup.restore_backup(materialized, self.root / "derivative-recovered", apply=True)
        restored = recovered / "work-root" / target.relative_to(work)
        self.assertEqual(restored.read_bytes(), expected)
        self.assertEqual(restored.stat().st_mtime_ns, mtime)
        self.assertEqual(json.loads((recovered / "work-root" / "_reports" / "artists" /
                                    "gallery-manifest.json").read_bytes()), report_manifest)

    def test_preview_and_idempotent_repeat(self):
        original = archive.inventory(self.snapshot)
        archive.pack(self.snapshot, self.bundle)
        self.assert_no_stage()
        first = self.pack()
        before = (self.bundle / "payload.zip").stat().st_mtime_ns
        second = self.pack()
        self.assertEqual(first, second)
        self.assertEqual((self.bundle / "payload.zip").stat().st_mtime_ns, before)
        self.assertEqual(archive.inventory(self.snapshot), original)
        with self.assertRaisesRegex(ValueError, "format"):
            self.pack(kind="stored")

    def test_stored_control_and_hybrid_images(self):
        self.pack()
        receipt, index = archive.check_bundle(self.bundle)
        with zipfile.ZipFile(self.bundle / "payload.zip") as packed:
            for row in index["files"]:
                info = packed.getinfo("payload/" + row["sha256"])
                expected = zipfile.ZIP_DEFLATED if row["path"].endswith(".json") else zipfile.ZIP_STORED
                self.assertEqual(info.compress_type, expected)
        stored = self.root / "stored"
        archive.pack(self.snapshot, stored, kind="stored", apply=True)
        archive.check_bundle(stored)
        with zipfile.ZipFile(stored / "payload.zip") as packed:
            self.assertTrue(all(info.compress_type == zipfile.ZIP_STORED for info in packed.infolist()))
        self.assertEqual(receipt["metrics"], archive.check_bundle(stored)[0]["metrics"])

    def test_corrupt_archive_and_receipt(self):
        self.pack()
        payload = self.bundle / "payload.zip"
        with payload.open("r+b") as stream:
            stream.seek(80)
            byte = stream.read(1)
            stream.seek(80)
            stream.write(bytes([byte[0] ^ 1]))
        with self.assertRaisesRegex(ValueError, "checksum"):
            archive.check_bundle(self.bundle)
        self.reseal()
        with self.assertRaises((ValueError, zipfile.BadZipFile)):
            archive.check_bundle(self.bundle)
        receipt_path = self.bundle / "receipt.json"
        receipt = json.loads(receipt_path.read_bytes())
        receipt["source"] = "changed"
        receipt_path.write_bytes(archive.canonical(receipt))
        with self.assertRaisesRegex(ValueError, "seal"):
            archive.check_bundle(self.bundle)

    def test_extra_missing_duplicate_and_traversal_archive_members(self):
        for variant in ("extra", "missing", "duplicate", "traversal", "case"):
            with self.subTest(variant=variant):
                self.bundle = self.root / ("bundle-" + variant)
                self.pack()
                def change(rows):
                    if variant == "missing":
                        return rows[:-1]
                    if variant == "duplicate":
                        return rows + [rows[-1]]
                    if variant == "case":
                        info, payload = rows[-1]
                        return rows + [(zipfile.ZipInfo(info.filename.upper()), payload)]
                    extra = "../escape" if variant == "traversal" else "unexpected"
                    return rows + [(zipfile.ZipInfo(extra), b"extra")]
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    self.rewrite_zip(change)
                with self.assertRaises((ValueError, KeyError)):
                    archive.check_bundle(self.bundle)
                with self.assertRaises((ValueError, KeyError)):
                    archive.restore(self.bundle, self.root / "unsafe-restore", apply=True)
                self.assertFalse((self.root / "unsafe-restore").exists())

    def test_missing_extra_and_unsafe_original_snapshot(self):
        extra = self.snapshot / "extra"
        extra.write_bytes(b"not owned")
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.pack()
        extra.unlink()
        image = next((self.snapshot / "work-root").rglob("a.jpg"))
        image.unlink()
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.pack()
        self.assert_no_stage()

    def test_source_mutation_refuses_atomic_publication(self):
        real = archive.build_zip
        def mutate(*args):
            real(*args)
            path = next((self.snapshot / "work-root").rglob("a.jpg"))
            path.write_bytes(b"changed")
        with mock.patch.object(archive, "build_zip", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "mismatch|changed"):
                self.pack()
        self.assert_no_stage()

    def test_atomic_build_and_publish_failures_clean_owned_stage(self):
        with mock.patch.object(archive, "build_zip", side_effect=OSError("injected")):
            with self.assertRaisesRegex(OSError, "injected"):
                self.pack()
        self.assert_no_stage()
        with mock.patch.object(archive.os, "rename", side_effect=OSError("publish failure")):
            with self.assertRaisesRegex(OSError, "publish failure"):
                self.pack()
        self.assert_no_stage()
        stage = self.bundle.with_name("bundle.packing")
        stage.mkdir()
        sentinel = stage / "do-not-touch"
        sentinel.write_bytes(b"pre-existing")
        with self.assertRaises(FileExistsError):
            self.pack()
        self.assertEqual(sentinel.read_bytes(), b"pre-existing")

    def test_stream_copy_and_hash_refuse_growth_and_truncation(self):
        for data, size in ((b"too long", 3), (b"short", 20)):
            with self.assertRaisesRegex(ValueError, "grew|truncated"):
                archive.copy_payload(io.BytesIO(data), io.BytesIO(), size)
        path = self.root / "growing"
        path.write_bytes(b"longer than expected")
        with self.assertRaisesRegex(ValueError, "bounded size"):
            archive.file_hash(path, max_bytes=1)

    def test_invalid_manifest_paths_and_recovery_collisions_refused(self):
        manifest_path = self.snapshot / "manifest.json"
        original = json.loads(manifest_path.read_bytes())
        for path in ("../escape", "C:\\escape", "work-root\\CON"):
            manifest = json.loads(json.dumps(original))
            manifest["entries"][0]["backup"] = path
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsafe"):
                self.pack()
        manifest = json.loads(json.dumps(original))
        manifest["regenerable"] = [{
            "backup": "work-root/empty",
            "sourceBackup": "work-root/notes.json",
        }]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "recovery target"):
            self.pack()
        self.assert_no_stage()

    def test_materialize_failure_does_not_publish(self):
        self.pack()
        destination = self.root / "restore-failure"
        with mock.patch.object(backup, "verify_backup", side_effect=OSError("verify failure")):
            with self.assertRaisesRegex(OSError, "verify failure"):
                archive.restore(self.bundle, destination, apply=True)
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_name("restore-failure.materializing").exists())

    def test_final_path_and_bundle_membership_sealed(self):
        self.pack()
        moved = self.root / "moved"
        shutil.copytree(self.bundle, moved)
        with self.assertRaisesRegex(ValueError, "final path"):
            archive.check_bundle(moved)
        extra = self.bundle / "additional"
        extra.write_bytes(b"extra")
        with self.assertRaisesRegex(ValueError, "membership"):
            archive.check_bundle(self.bundle)
        extra.unlink()
        (self.bundle / "receipt.json").unlink()
        with self.assertRaisesRegex(ValueError, "membership"):
            archive.check_bundle(self.bundle)

    def test_strict_names_case_parent_collisions_and_bounds(self):
        for unsafe in ("../escape", "/absolute", "a//b", "a\\b", "c:x",
                       "CON", "a/NUL.txt", "a.", "a ", "a/\x00x", "a/./b"):
            with self.subTest(name=unsafe), self.assertRaises(ValueError):
                archive.name(unsafe)
        index = archive.inventory(self.snapshot)
        duplicate = dict(index["files"][0])
        duplicate["path"] = duplicate["path"].upper()
        index["files"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "collision|colliding"):
            archive.validate_rows(index)
        with mock.patch.object(archive, "MAX_FILES", 1):
            with self.assertRaisesRegex(ValueError, "bounds"):
                self.pack()
        with mock.patch.object(archive, "MAX_BYTES", 1):
            with self.assertRaisesRegex(ValueError, "bounds"):
                self.pack()
        with mock.patch.object(archive, "MAX_METADATA", 1):
            with self.assertRaisesRegex(ValueError, "manifest"):
                self.pack()
        self.assert_no_stage()

    def test_absolute_ignored_outputs_only_and_overlap(self):
        for unsafe in ("tmp\\relative-bundle", backup.ROOT / "outside-tmp"):
            with self.assertRaisesRegex(ValueError, "absolute|tmp"):
                archive.pack(self.snapshot, unsafe)
        with self.assertRaisesRegex(ValueError, "overlap"):
            archive.pack(self.snapshot, self.snapshot / "nested-bundle")

    def test_archive_central_directory_bound_checked_before_parse(self):
        self.pack()
        with mock.patch.object(archive, "MAX_FILES", 1), \
                mock.patch.object(zipfile, "ZipFile", side_effect=AssertionError("must not parse")):
            with self.assertRaisesRegex(ValueError, "central-directory"):
                archive.check_bundle(self.bundle)

    @unittest.skipUnless(os.name == "nt", "Windows junction ancestor safety")
    def test_linked_source_output_and_bundle_member_refused(self):
        alias = self.root / "junction"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(self.snapshot)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(os.rmdir, alias)
        with self.assertRaisesRegex(ValueError, "linked/reparse"):
            archive.pack(alias, self.bundle, apply=True)
        with self.assertRaisesRegex(ValueError, "linked/reparse"):
            archive.pack(self.snapshot, alias / "new", apply=True)
        member = self.snapshot / "linked-directory"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(member), str(self.work)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(os.rmdir, member)
        with self.assertRaisesRegex(ValueError, "linked/reparse"):
            self.pack()

    @unittest.skipUnless(os.name == "nt", "Windows launcher")
    def test_launcher_preview_apply_check_and_restore(self):
        launcher = str(backup.ROOT / "bin" / "backup-archive.cmd")
        calls = [
            [str(self.snapshot), "--out", str(self.bundle)],
            [str(self.snapshot), "--out", str(self.bundle), "--apply"],
            ["--check", str(self.bundle)],
            ["--restore", str(self.bundle), "--destination", str(self.root / "launcher-restore")],
            ["--restore", str(self.bundle), "--destination", str(self.root / "launcher-restore"), "--apply"],
        ]
        for index, arguments in enumerate(calls):
            result = subprocess.run(["cmd", "/c", launcher, *arguments],
                                    cwd=backup.ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            if index == 0:
                self.assertFalse(self.bundle.exists())
        self.assertTrue(backup.verify_backup(self.root / "launcher-restore"))


if __name__ == "__main__":
    unittest.main()
