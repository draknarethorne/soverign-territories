"""Verify exact-copy removal and interrupted raw-original replacement."""

import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art.likeness_library import various_cleanup as cleanup


def sha(data):
    return hashlib.sha256(data).hexdigest()


class VariousCleanupTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = pathlib.Path(temp.name)
        self.root = base / "Sovereign Territories"
        self.target = self.write("Angels/Named/gallery/named_image_123.jpg", b"before")
        self.exact = self.write("Various/gallery/exact.jpg", b"before")
        self.edit = self.write("Various/gallery/edit.jpg", b"intentional edit")
        self.unlisted = self.write("Various/gallery/keep.jpg", b"unrelated arrival")
        self.plan = base / "plan.json"
        self.entries = [{
            "photoId": "photo:image_123",
            "namedPath": self.target.relative_to(self.root).as_posix(), "namedSHA256": sha(b"before"),
            "incoming": {
                self.exact.relative_to(self.root).as_posix(): sha(b"before"),
                self.edit.relative_to(self.root).as_posix(): sha(b"intentional edit"),
            },
        }]

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def clean(self, mode):
        raw = json.dumps({"schemaVersion": 1, "entries": self.entries}).encode()
        self.plan.write_bytes(raw)
        return cleanup.run(self.root, self.plan, sha(raw), mode)

    def test_exact_copy_removed_without_backup_and_edit_takes_original_path(self):
        before = self.clean("preview")
        self.assertEqual((before["pendingExactCopiesBefore"], before["pendingEditsBefore"]), (1, 1))
        self.assertFalse((self.root / "_archive").exists())
        self.assertEqual(self.target.read_bytes(), b"before")
        after = self.clean("apply")
        archive = pathlib.Path(after["archiveRoot"])
        self.assertEqual((archive / self.target.relative_to(self.root)).read_bytes(), b"before")
        self.assertEqual(len([p for p in archive.rglob("*") if p.is_file()]), 1)
        self.assertFalse(self.exact.exists())
        self.assertFalse(self.edit.exists())
        self.assertEqual(self.target.read_bytes(), b"intentional edit")
        self.assertEqual(self.unlisted.read_bytes(), b"unrelated arrival")
        self.assertEqual(self.clean("apply")["pendingEditsBefore"], 0)
        self.assertEqual(self.clean("check")["pendingExactCopiesBefore"], 0)

    def test_exact_only_keeps_named_original(self):
        del self.entries[0]["incoming"][self.edit.relative_to(self.root).as_posix()]
        self.clean("apply")
        self.assertFalse(self.exact.exists())
        self.assertTrue(self.edit.exists())
        self.assertEqual(self.target.read_bytes(), b"before")

    def test_changed_arrival_blocks_all_removals_and_replacements(self):
        self.edit.write_bytes(b"unreviewed edit")
        with self.assertRaisesRegex(ValueError, "incoming original has changed"):
            self.clean("apply")
        self.assertEqual(self.target.read_bytes(), b"before")
        self.assertTrue(self.exact.exists())

    def test_interruption_after_archive_can_resume(self):
        original = pathlib.Path.rename

        def interrupt(path, target):
            if path == self.edit:
                raise OSError("interrupted")
            return original(path, target)

        with mock.patch.object(pathlib.Path, "rename", interrupt):
            with self.assertRaisesRegex(OSError, "interrupted"):
                self.clean("apply")
        self.assertFalse(self.target.exists())
        self.assertTrue(self.exact.exists())
        self.assertEqual(self.clean("preview")["pendingEditsBefore"], 1)
        self.clean("apply")
        self.clean("check")
        self.assertEqual(self.target.read_bytes(), b"intentional edit")

    def test_refuses_catalogued_library_and_sealed_source(self):
        catalog = self.write(".likeness-library.json", b"{}")
        with self.assertRaisesRegex(ValueError, "managed library"):
            self.clean("apply")
        catalog.unlink()
        base = self.root.parent / "Sovereign Territories Sandbox"
        base.mkdir()
        self.root = self.root.rename(base / "Source")
        with self.assertRaisesRegex(ValueError, "not sealed Source"):
            self.clean("apply")

    def test_rejects_bad_digest_and_path_escape(self):
        self.clean("preview")
        with self.assertRaisesRegex(ValueError, "does not match"):
            cleanup.run(self.root, self.plan, "a" * 64, "apply")
        self.entries[0]["incoming"]["Various/gallery/../escape.jpg"] = sha(b"x")
        with self.assertRaisesRegex(ValueError, "invalid source-manifest path"):
            self.clean("apply")
        self.assertTrue(self.exact.exists())

    def test_exact_scan_checks_id_and_full_bytes_before_discard(self):
        from tools.art import likeness

        exact = self.write("Various/gallery/facebook_1790000000000_123.jpg", b"before")
        # Use a valid platform ID for the generic download name.
        original = self.target.rename(self.target.with_name("named_image_7508205778272844316.jpg"))
        exact = exact.rename(exact.with_name("facebook_1790000000000_7508205778272844316.jpg"))
        edited = self.write("Various/gallery/edited_image_7508205778272844316.jpg", b"edited")
        other_id = self.write("Various/gallery/other_image_999.jpg", b"before")
        self.write(".likeness-library.json", b"{}")
        with mock.patch.object(likeness, "configuration", return_value={}):
            plan = cleanup.scan_exact(self.root)
            self.assertEqual(plan["entries"], [{
                "photoId": "photo:image_7508205778272844316",
                "discard": exact.relative_to(self.root).as_posix(),
                "keeper": original.relative_to(self.root).as_posix(),
                "sha256": sha(b"before"),
            }])
            self.assertEqual(cleanup.run_exact(self.root, plan, "apply")["discarded"], 1)
            self.assertEqual(cleanup.run_exact(self.root, plan, "check")["pendingBefore"], 0)
        self.assertFalse(exact.exists())
        self.assertTrue(edited.is_file())
        self.assertTrue(other_id.is_file())
        self.assertEqual(original.read_bytes(), b"before")
        self.assertFalse(any(path.suffix == ".jpg" for path in (self.root / "_archive").rglob("*")))
        self.assertFalse((self.root / "_duplicates").exists())

    def test_exact_scan_keeps_pool_only_keeper_and_blocks_changed_bytes(self):
        from tools.art import likeness

        self.exact.unlink()
        self.edit.unlink()
        a = self.write("Various/gallery/a_image_777.jpg", b"same")
        b = self.write("Various/gallery/b_image_777.jpg", b"same")
        with mock.patch.object(likeness, "configuration", return_value={}):
            plan = cleanup.scan_exact(self.root)
            self.assertEqual(len(plan["entries"]), 1)
            removal = self.root / plan["entries"][0]["discard"]
            removal.write_bytes(b"edit")
            with self.assertRaisesRegex(ValueError, "evidence changed"):
                cleanup.run_exact(self.root, plan, "apply")
        self.assertTrue(a.is_file())
        self.assertTrue(b.is_file())
