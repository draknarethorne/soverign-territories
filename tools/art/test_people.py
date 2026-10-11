#!/usr/bin/env python3
"""The z_ file module. Run: python tools/art/test_people.py"""
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import people as P  # noqa: E402


class PeopleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.folder = self.tmp / "Prospects" / "Mia Wolfe"
        (self.folder / "gallery").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_an_empty_hand_made_file_still_gives_the_name(self):
        (self.folder / "gallery" / "z_lia_lujan.txt").write_text("")
        self.assertEqual(P.read(self.folder), ("Lia Lujan", []))

    def test_note_creates_the_file_and_never_repeats_a_line(self):
        P.note(self.folder, "+3 from Various", when="2026-10-10")
        P.note(self.folder, "+3 from Various", when="2026-10-10")
        self.assertEqual(P.read(self.folder), ("Mia Wolfe", ["2026-10-10 +3 from Various"]))
        self.assertTrue((self.folder / "gallery" / "z_mia_wolfe.txt").exists())

    def test_note_keeps_the_existing_name(self):
        (self.folder / "gallery" / "z_mia.txt").write_text("")
        P.note(self.folder, "paired", name="Other", when="2026-10-10")
        self.assertEqual(P.read(self.folder)[0], "Mia")
        self.assertEqual([p.name for p in (self.folder / "gallery").glob("z_*")], ["z_mia.txt"], "one file, not two")

    def test_adopt_renames_the_file_and_remembers_who_was_there(self):
        P.write(self.folder, "Seraphine", [])
        P.adopt(self.folder, "Kylie Voss", "now the angel Seraphine", when="2026-10-10")
        self.assertEqual(P.read(self.folder), ("Kylie Voss", ["2026-10-10 was Seraphine", "2026-10-10 now the angel Seraphine"]))
        self.assertEqual([p.name for p in (self.folder / "gallery").glob("z_*")], ["z_kylie_voss.txt"])

    def test_a_folder_without_a_file_reads_as_none(self):
        self.assertIsNone(P.read(self.folder))
        self.assertIsNone(P.name_of(self.folder))


if __name__ == "__main__":
    unittest.main()
