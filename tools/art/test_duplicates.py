#!/usr/bin/env python3
"""duplicates: the same picture kept twice is found, one copy is kept (a chosen photo first), the others go to _archive. Run: python tools/art/test_duplicates.py"""
import contextlib
import io
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import duplicates  # noqa: E402


class DuplicatesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.work = self.tmp / "lib"

    def photo(self, root, folder, name, data, bucket="gallery"):
        d = self.work / root / folder / bucket
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_bytes(data)
        return d / name

    def folders(self):
        out = []
        for root in sorted(self.work.iterdir()):
            for d in sorted(root.iterdir()):
                out.append((root.name, d.name, d))
        return out

    def run_it(self, chosen=(), apply=True):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            groups, ids = duplicates.run({"photos": {f"h{i}": n for i, n in enumerate(chosen)}}, self.work, self.folders(), apply)
        return groups, ids, out.getvalue()

    def run_prefer_incoming(self, apply=True):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            groups, ids = duplicates.run({}, self.work, self.folders(), apply, prefer_incoming_copies=True)
        return groups, ids, out.getvalue()

    def test_identical_bytes_under_two_ids_keep_one_and_archive_the_other(self):
        a = self.photo("Prospects", "Mia Wolfe", "mia_wolfe_image_1111.jpg", b"same")
        b = self.photo("Prospects", "Mia Wolfe", "mia_wolfe_image_22222.jpg", b"same")
        self.photo("Prospects", "Mia Wolfe", "mia_wolfe_image_3333.jpg", b"other")
        groups, ids, _ = self.run_it()
        self.assertEqual((len(groups), ids), (1, []))
        self.assertTrue(a.exists() and not b.exists(), "the shorter name is kept")
        self.assertTrue((self.work / "_archive/Prospects/Mia Wolfe/gallery_duplicates/mia_wolfe_image_22222.jpg").exists(), "set aside, not deleted")

    def test_the_angel_copy_beats_a_prospect_and_various_and_a_gallery_beats_review(self):
        keep = self.photo("Angels", "angelica", "angelica_image_1.jpg", b"x")
        v = self.photo("Various", "Various", "various_image_1.jpg", b"x")
        p = self.photo("Prospects", "Ana Cole", "ana_cole_image_1.jpg", b"x")
        self.run_it()
        self.assertEqual((keep.exists(), v.exists(), p.exists()), (True, False, False))
        g = self.photo("Prospects", "Bea Cole", "bea_cole_image_9.jpg", b"y")
        r = self.photo("Prospects", "Bea Cole", "bea_cole_image_8.jpg", b"y", bucket="review")
        self.run_it()
        self.assertEqual((g.exists(), r.exists()), (True, False))

    def test_a_chosen_photo_is_always_the_copy_kept(self):
        a = self.photo("Angels", "angelica", "angelica_image_1.jpg", b"x")
        b = self.photo("Prospects", "Ana Cole", "ana_cole_image_1.jpg", b"x")
        self.run_it(chosen=["ana_cole_image_1_944x1104.png"])
        self.assertEqual((a.exists(), b.exists()), (False, True))

    def test_two_chosen_copies_are_left_alone(self):
        a = self.photo("Angels", "angelica", "angelica_image_1.jpg", b"x")
        b = self.photo("Prospects", "Ana Cole", "ana_cole_image_1.jpg", b"x")
        self.run_it(chosen=["angelica_image_1_944x1104.png", "ana_cole_image_1_frame_944x1104.png"])
        self.assertTrue(a.exists() and b.exists())

    def test_the_same_id_with_different_bytes_is_listed_and_nothing_moves(self):
        a = self.photo("Angels", "angelica", "angelica_image_5555.jpg", b"big photo")
        b = self.photo("Various", "Various", "various_image_5555.jpg", b"smaller")
        groups, ids, out = self.run_it()
        self.assertEqual((groups, len(ids)), ([], 1))
        self.assertTrue(a.exists() and b.exists())
        self.assertIn("yours to pick", out)

    def test_a_preview_moves_nothing(self):
        a = self.photo("Prospects", "Mia Wolfe", "mia_wolfe_image_1111.jpg", b"same")
        b = self.photo("Prospects", "Mia Wolfe", "mia_wolfe_image_22222.jpg", b"same")
        self.run_it(apply=False)
        self.assertTrue(a.exists() and b.exists())

    def test_a_changed_incoming_same_id_replaces_and_archives_the_existing_copy(self):
        old = self.photo("Prospects", "Mia Wolfe", "mia_wolfe_shot_20261014123456.jpg", b"old version")
        incoming = self.photo("Various", "Various", "various_shot_20261014123456.jpg", b"fixed version")
        _, ids, out = self.run_prefer_incoming()
        archive = self.work / "_archive/Prospects/Mia Wolfe/gallery_replaced/mia_wolfe_shot_20261014123456.jpg"
        self.assertTrue(incoming.exists())
        self.assertFalse(old.exists())
        self.assertEqual(archive.read_bytes(), b"old version")
        self.assertEqual(ids, [])
        self.assertIn("REPLACED", out)

    def test_updated_incoming_copy_replaces_matching_junk_version(self):
        junk = self.work / "_junk/Prospects"
        junk.mkdir(parents=True)
        old = junk / "mia_wolfe_shot_20261014123456.jpg"
        old.write_bytes(b"old junk version")
        incoming = self.photo("Various", "Various", "various_shot_20261014123456.jpg", b"fixed version")
        _, ids, _ = self.run_prefer_incoming()
        archive = self.work / "_archive/_junk/Prospects/gallery_replaced/mia_wolfe_shot_20261014123456.jpg"
        self.assertTrue(incoming.exists())
        self.assertFalse(old.exists())
        self.assertEqual(archive.read_bytes(), b"old junk version")
        self.assertEqual(ids, [])

    def test_incoming_same_id_replacement_preview_keeps_both_files(self):
        old = self.photo("Prospects", "Mia Wolfe", "mia_wolfe_shot_20261014123456.jpg", b"old version")
        incoming = self.photo("Various", "Various", "various_shot_20261014123456.jpg", b"fixed version")
        _, ids, out = self.run_prefer_incoming(apply=False)
        self.assertTrue(old.exists() and incoming.exists())
        self.assertEqual(ids, [])
        self.assertIn("would replace", out)

    def test_tied_newest_incoming_copies_and_existing_version_are_left_for_manual_review(self):
        old = self.photo("Prospects", "Mia Wolfe", "mia_wolfe_shot_20261014123456.jpg", b"old version")
        first = self.photo("Various", "Various", "various_shot_20261014123456.jpg", b"fixed one")
        second = self.photo("Various", "Various", "various_shot_20261014123456_copy.jpg", b"fixed two")
        os.utime(first, ns=(1_000_000_000, 1_000_000_000))
        os.utime(second, ns=(1_000_000_000, 1_000_000_000))
        _, ids, out = self.run_prefer_incoming()
        self.assertTrue(old.exists() and first.exists() and second.exists())
        self.assertEqual(len(ids), 1)
        self.assertIn("ambiguous", out)
        self.assertFalse((self.work / "Various/Various/duplicates").exists())

    def test_newest_incoming_copy_stays_in_gallery_and_older_copy_goes_to_duplicates(self):
        old = self.photo("Prospects", "Mia Wolfe", "mia_wolfe_shot_20261014123456.jpg", b"existing")
        older = self.photo("Various", "Various", "Screenshot_20261014_123456_Facebook.jpg", b"older")
        newest = self.photo("Various", "Various", "various_shot_20261014123456.jpg", b"newest")
        os.utime(older, ns=(1_000_000_000, 1_000_000_000))
        os.utime(newest, ns=(2_000_000_000, 2_000_000_000))

        _, ids, out = self.run_prefer_incoming()

        stashed = self.work / "Various/Various/duplicates/Screenshot_20261014_123456_Facebook.jpg"
        archived = self.work / "_archive/Prospects/Mia Wolfe/gallery_replaced/mia_wolfe_shot_20261014123456.jpg"
        self.assertTrue(newest.exists())
        self.assertFalse(older.exists())
        self.assertEqual(stashed.read_bytes(), b"older")
        self.assertEqual(archived.read_bytes(), b"existing")
        self.assertEqual(ids, [])
        self.assertIn("newest modification time stays in gallery", out)

    def test_older_incoming_copy_does_not_overwrite_existing_duplicates_review(self):
        older = self.photo("Various", "Various", "older_shot_20261014123456.jpg", b"older")
        newest = self.photo("Various", "Various", "newest_shot_20261014123456.jpg", b"newest")
        duplicates = self.work / "Various/Various/duplicates"
        duplicates.mkdir(parents=True)
        existing = duplicates / older.name
        existing.write_bytes(b"previously set aside")
        os.utime(older, ns=(1_000_000_000, 1_000_000_000))
        os.utime(newest, ns=(2_000_000_000, 2_000_000_000))

        self.run_prefer_incoming()

        self.assertEqual(existing.read_bytes(), b"previously set aside")
        self.assertEqual((duplicates / "older_shot_20261014123456_duplicate_1.jpg").read_bytes(), b"older")
        self.assertTrue(newest.exists())


if __name__ == "__main__":
    unittest.main()
