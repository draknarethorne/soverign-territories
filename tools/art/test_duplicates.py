#!/usr/bin/env python3
"""duplicates: the same picture kept twice is found, one copy is kept (a chosen photo first), the others go to _archive. Run: python tools/art/test_duplicates.py"""
import contextlib
import io
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


if __name__ == "__main__":
    unittest.main()
