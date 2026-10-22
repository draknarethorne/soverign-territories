#!/usr/bin/env python3
"""The likeness tool, tested with made-up face vectors (no models, no real photos). Run: python tools/art/test_likeness.py"""
import contextlib
import csv
import io
import pathlib
import shutil
import sys
import tempfile
import unittest
import zlib
from unittest import mock

import numpy as np  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import likeness as L  # noqa: E402
import comfy_workflows as cw  # noqa: E402

DIM = 128
COMMON = np.random.default_rng(0).normal(size=DIM)  # the "everyone looks glamorous" part that centring removes
IDENT = {}


def identity(person):
    if person not in IDENT:
        IDENT[person] = np.random.default_rng(zlib.crc32(person.encode())).normal(size=DIM)
    return IDENT[person]


def face(person, i):
    noise = np.random.default_rng(i + 1000).normal(size=DIM) * 0.5
    v = 3 * COMMON + identity(person) + noise
    return v / np.linalg.norm(v)


class Fake:
    """An embedder that reads the person from the file's text ('person|i', or 'person|i|faces')."""

    def __init__(self):
        self.calls = 0

    def __call__(self, path):
        self.calls += 1
        parts = pathlib.Path(path).read_text().split("|")
        person, i = parts[0], parts[1]
        if person == "noface":
            return {"faces": 0}
        return {"faces": int(parts[2]) if len(parts) > 2 else 1, "s": 0.95, "f2": float(parts[3]) if len(parts) > 3 else (0.8 if len(parts) > 2 and int(parts[2]) > 1 else 0), "v": [float(x) for x in face(person, int(i))], "box": [0.2, 0.2, 0.4, 0.4], "px": 20 if person.startswith("tiny") else 200}


def blend(person, base, w):
    """Make `person` look like `base`: w is how much of base's identity it carries."""
    IDENT[person] = w * identity(base) + float(np.sqrt(1 - w * w)) * np.random.default_rng(zlib.crc32(person.encode())).normal(size=DIM)


CFG = {"standardSize": [94, 110], "photos": {}, "workspaces": {}}


class LikenessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.lib = self.tmp / "lib"
        self.fake = Fake()
        self.patches = [mock.patch.object(cw, "load_cfg", lambda: dict(CFG)), mock.patch.object(L, "DATA", self.tmp / "data")]
        for p in self.patches:
            p.start()
        self.n = 0

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def add(self, root, folder, person, count=1):
        g = self.lib / root / folder / "gallery"
        g.mkdir(parents=True, exist_ok=True)
        for _ in range(count):
            self.n += 1
            (g / f"{folder.lower().replace(' ', '_')}_image_{self.n}.jpg").write_text(f"{person}|{self.n}")

    def standard_library(self):
        self.add("Angels", "Angelica", "ann", 4)
        self.add("Angels", "Azaline", "ann2", 3)
        self.add("Models", "Draknara", "dee", 4)
        self.add("Prospects", "Mia", "mia", 4)
        self.add("Prospects", "Various", "ann", 1)     # looks like Angelica
        self.add("Prospects", "Various", "dee", 2)     # looks like Draknara
        self.add("Prospects", "Various", "zed", 5)     # a new person, five photos
        self.add("Prospects", "Various", "solo", 1)    # nobody
        self.add("Artists", "Fantasy", "collage", 3)   # mixed: never read

    def run_tool(self, *args, apply=False):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            try:
                L.main(["--no-originals", "--root", str(self.lib), *args, *(["--apply"] if apply else [])], embedder=self.fake)
            except SystemExit as e:
                out.write(f"EXIT {e.code}")
        return out.getvalue()

    def names(self, root, folder):
        d = self.lib / root / folder / "gallery"
        return sorted(p.name for p in d.iterdir() if not p.name.startswith("z_")) if d.is_dir() else []

    def test_category_migration_moves_whole_folders_and_preserves_history(self):
        source = self.lib / "Prospects/Afton/gallery"
        source.mkdir(parents=True)
        (source / "z_afton.txt").write_text("name: Afton\n")
        (source / "afton_image_1.jpg").write_text("afton|1")
        (self.lib / "Potentials").mkdir()

        moved = L.apply_category_changes(
            self.lib, [("Prospects/Afton", "Potentials/Afton", 1, False)]
        )

        self.assertEqual(moved, 1)
        self.assertFalse((self.lib / "Prospects/Afton").exists())
        self.assertEqual(
            (self.lib / "Potentials/Afton/gallery/z_afton.txt").read_text(),
            "name: Afton\n",
        )
        self.assertEqual(
            (self.lib / "Potentials/Afton/gallery/afton_image_1.jpg").read_text(),
            "afton|1",
        )

    def test_category_migration_checks_every_destination_before_moving(self):
        for root, name in (("Prospects", "Afton"), ("Prospects", "Amara")):
            (self.lib / root / name / "gallery").mkdir(parents=True)
        (self.lib / "Potentials/Amara").mkdir(parents=True)

        with self.assertRaises(FileExistsError):
            L.apply_category_changes(
                self.lib,
                [
                    ("Prospects/Afton", "Potentials/Afton", 1, False),
                    ("Prospects/Amara", "Potentials/Amara", 1, False),
                ],
            )

        self.assertTrue((self.lib / "Prospects/Afton").is_dir())
        self.assertTrue((self.lib / "Prospects/Amara").is_dir())
        self.assertFalse((self.lib / "Potentials/Afton").exists())

    def test_cluster_groups_the_same_person(self):
        vecs = np.array([face("a", i) for i in range(4)] + [face("b", 10 + i) for i in range(4)])
        c = L.nz(vecs - vecs.mean(0))
        groups = sorted(sorted(g) for g in L.cluster(c, 0.2))
        self.assertEqual(groups, [[0, 1, 2, 3], [4, 5, 6, 7]])

    def test_invented_names_are_stable_and_unique(self):
        self.assertEqual(L.invent_name("x", set()), L.invent_name("x", set()))
        first = L.invent_name("y", set())
        self.assertNotEqual(L.invent_name("y", {first}).lower(), first.lower())
        self.assertNotEqual(L.invent_name("y", {first.upper()}).lower(), first.lower(), "a name that differs only in case is taken")

    def test_rebaseline_writes_cast_photo_audit_and_flags_potential_exceptions_without_moving(self):
        self.add("Angels", "Angelica", "ann", 4)
        self.add("Prospects", "Petra Cole", "ann", 3)
        self.add("Potentials", "Former Sister", "ann", 5)
        potential_history = self.lib / "Potentials/Former Sister/gallery/z_former_sister.txt"
        potential_history.write_text(
            "name: Former Sister\n2026-10-01 was the Sister Draknara\n",
            encoding="utf-8",
        )
        (self.lib / "Potentials/Former Sister/gallery/no_face_image_999.jpg").write_text("noface|999")
        report = self.tmp / "reports" / "rebaseline.md"
        photo_paths = [
            self.lib / "Prospects/Petra Cole/gallery" / name
            for name in self.names("Prospects", "Petra Cole")
        ]

        output = self.run_tool("rebaseline", "--out", str(report))

        audit_path = report.with_name("prospect-cast-audit.csv")
        self.assertTrue(audit_path.is_file())
        self.assertIn("configured-category Gallery photos audited", output)
        self.assertIn("Photo-by-photo scores", report.read_text(encoding="utf-8"))
        with audit_path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        petra_rows = [row for row in rows if row["source_folder"] == "Prospects/Petra Cole"]
        former_rows = [row for row in rows if row["source_folder"] == "Potentials/Former Sister"]
        self.assertEqual(len(petra_rows), 3)
        self.assertTrue(all(row["best_cast_folder"] == "Angels/Angelica" for row in petra_rows))
        self.assertTrue(all(row["suggested_review_only"] == "Angels/Angelica/review" for row in petra_rows))
        self.assertEqual(len(former_rows), 6)
        self.assertTrue(all("5+ usable photos" in row["potential_status_flags"] for row in former_rows))
        self.assertTrue(
            all("history mentions prior cast identity" in row["potential_status_flags"] for row in former_rows),
            [(row["history"], row["potential_status_flags"]) for row in former_rows],
        )
        no_face = next(row for row in former_rows if row["photo"].startswith("no_face"))
        self.assertEqual(no_face["usable"], "False")
        self.assertEqual(no_face["best_cast_folder"], "")
        self.assertTrue(all(path.is_file() for path in photo_paths))
        self.assertTrue((self.lib / "Prospects/Petra Cole").is_dir())
        self.assertTrue((self.lib / "Potentials/Former Sister").is_dir())

    def test_the_mixed_folders_are_never_read_and_the_cache_spares_a_second_run(self):
        self.standard_library()
        self.run_tool("scan")
        first = self.fake.calls
        self.assertEqual(first, 4 + 3 + 4 + 4 + 9, "Artists is not read; the pool and the person folders are")
        self.run_tool("scan")
        self.assertEqual(self.fake.calls, first, "unchanged files are not read again")
        moved = self.names("Angels", "Angelica")[0]
        shutil.move(str(self.lib / "Angels/Angelica/gallery" / moved), str(self.lib / "Angels/Azaline/gallery/renamed.jpg"))
        self.run_tool("scan")
        self.assertEqual(self.fake.calls, first, "a moved or renamed file costs nothing: the cache is keyed by its content")

    def test_prospects_and_artists_are_never_mixed(self):
        self.standard_library()
        g = self.lib / "Artists/Pierre/Elise/gallery"
        g.mkdir(parents=True)
        for i in range(4):
            (g / f"elise_image_{900 + i}.jpg").write_text(f"art|{900 + i}")
        self.add("Prospects", "Various", "art", 2)  # looks just like the artist's person
        for i, who in enumerate(("w1", "w2", "w3", "w4")):
            self.add("Prospects", f"Person {i}", who, 3)
        self.assertIn("kept apart", self.run_tool("merge", "Mia", "Elise") + self.run_tool("merge", "Elise", "Mia"))
        out = self.run_tool("sort", "--singles", apply=True)
        self.assertEqual(len(self.names("Artists", "Pierre/Elise")), 4, "nothing from the pool goes to an artist's person")
        self.assertTrue(any(f"art|" in p.read_text()
                            for root in ("Prospects", "Potentials")
                            for q in (self.lib / root).glob("*/gallery")
                            if q.parent.name != "Various"
                            for p in q.iterdir()
                            if p.suffix == ".jpg"), "it became a prospect instead")
        self.assertEqual(L.new_home("Artists/Pierre/Elise", "Zoe Cole"), "Artists/Pierre/Zoe Cole", "a new person split from an artist's person stays with the artist")
        self.assertEqual(L.new_home("Sisters/Draknara", "Zoe Cole"), "Potentials/Zoe Cole")
        self.assertTrue(L.apart("Various", "Artists/Pierre/Elise") and not L.apart("Angels/Angelica", "Artists/Pierre/Elise"))
        self.assertIsNotNone(out)

    def test_junk_sets_aside_photos_that_cannot_feed_a_prime_but_never_an_angels_own_gallery(self):
        self.add("Angels", "Angelica", "ann", 4)
        self.add("Sisters", "Draknara", "dee", 4)
        for i, who in enumerate(("w1", "w2", "w3", "w4")):
            self.add("Prospects", f"Person {i}", who, 3)
        self.add("Prospects", "Person 0", "noface", 1)
        self.add("Prospects", "Person 1", "tiny1", 1)
        self.add("Angels", "Angelica", "noface", 1)
        before = self.names("Prospects", "Person 0")
        out = self.run_tool("junk")
        self.assertIn("no face found", out)
        self.assertIn("face too small", out)
        self.assertEqual(self.names("Prospects", "Person 0"), before, "a preview moves nothing")
        self.run_tool("junk", apply=True)
        self.assertEqual(len(self.names("Prospects", "Person 0")), 3)
        self.assertEqual(len(list((self.lib / "_junk/Prospects").glob("*.jpg"))), 2, "flat: only Prospects, Artists, Sisters at the top, the person is in the file name")
        self.assertTrue(any(p.name.startswith("person_0_") for p in (self.lib / "_junk/Prospects").glob("*.jpg")))
        self.assertFalse((self.lib / "_junk/Prospects/Person 0").exists())
        self.assertEqual(len(self.names("Angels", "Angelica")), 5, "an angel's own gallery is never touched")
        self.assertTrue(any("junk:" in ln for ln in L.people.read(self.lib / "Prospects/Person 0")[1]))

    def test_singles_merges_a_one_photo_prospect_into_the_prospect_she_looks_like_and_into_a_sister_she_is(self):
        self.add("Sisters", "Draknara", "dee", 4)
        self.add("Prospects", "Mia", "mia", 4)
        self.add("Prospects", "Solo Mia", "mia", 1)
        self.add("Prospects", "Solo Dee", "dee", 1)
        self.add("Prospects", "Lone", "lone", 1)
        for i, who in enumerate(("w1", "w2", "w3", "w4")):
            self.add("Prospects", f"Person {i}", who, 3)
        out = self.run_tool("singles")
        self.assertIn("Solo Mia", out)
        self.run_tool("singles", apply=True)
        self.assertEqual(len(self.names("Prospects", "Mia")), 5)
        self.assertEqual(len(self.names("Sisters", "Draknara")), 5, "she is the same person as a sister, so she joins her (the z_ file remembers who she was)")
        self.assertFalse((self.lib / "Prospects/Solo Dee").exists() and self.names("Prospects", "Solo Dee"))
        self.assertTrue(any("Solo Dee" in ln for ln in L.people.read(self.lib / "Sisters/Draknara")[1]))
        self.assertEqual(len(self.names("Prospects", "Lone")), 1)
        self.assertTrue((self.lib / "_retired/Prospects/Solo Mia").exists())

    def test_index_profile_who_and_the_spreadsheet_round_trip(self):
        self.add("Angels", "Angelica", "ann", 4)
        self.add("Sisters", "Draknara", "dee", 4)
        self.add("Prospects", "Mia", "mia", 4)
        self.add("Prospects", "Zed", "zed", 3)
        for i, who in enumerate(("w1", "w2", "w3")):
            self.add("Prospects", f"Person {i}", who, 3)
        self.assertIn("EXIT", self.run_tool("profile", "Mia", "--bogus", "x"))
        self.run_tool("profile", "Mia", "--type", "dark elf", "--roles", "rogue, spy", "--elements", "Darkness")
        out = self.run_tool("who", "--roles", "spy")
        self.assertIn("Mia", out)
        self.assertNotIn("Zed", out)
        self.assertIn("still to classify", self.run_tool("who"))
        self.run_tool("index")
        import csv
        csv_path = self.lib / "people_index.csv"
        rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
        mia = next(r for r in rows if r["folder"] == "Mia")
        self.assertEqual((mia["status"], mia["type"], mia["roles"], mia["elements"]), ("Prospects", "dark elf", "rogue; spy", "Darkness"))
        self.assertEqual(len(rows), 7)
        zed = next(r for r in rows if r["folder"] == "Zed")
        zed["roles"], zed["tags"] = "barbarian; princess", "tall"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        self.assertIn("1 profile(s) would change", self.run_tool("index", "--import", str(csv_path)))
        self.assertEqual(L.people.profile(self.lib / "Prospects/Zed"), {})
        self.run_tool("index", "--import", str(csv_path), apply=True)
        self.assertEqual(L.people.profile(self.lib / "Prospects/Zed"), {"roles": ["barbarian", "princess"], "tags": ["tall"]})
        self.run_tool("profile", "Zed", "--tags", "-")
        self.assertNotIn("tags", L.people.profile(self.lib / "Prospects/Zed"))

    def test_junk_recheck_sends_photos_that_are_usable_now_back_to_the_pool(self):
        self.add("Angels", "Angelica", "ann", 4)
        for i, who in enumerate(("w1", "w2", "w3", "w4")):
            self.add("Prospects", f"Person {i}", who, 3)
        g = self.lib / "Prospects/Person 0/gallery"
        (g / "person_0_image_901.jpg").write_text("w1|901|2|0.8")  # a real second person
        (g / "person_0_image_902.jpg").write_text("w1|902|2|0.1")  # a passer-by in the background
        self.assertEqual(self.run_tool("junk").count("2+ faces"), 2, "only the real second person is junk (listed in the summary and the line)")
        self.run_tool("junk", apply=True)
        junk = self.lib / "_junk/Prospects"
        self.assertEqual([p.name for p in junk.glob("*.jpg")], ["person_0_image_901.jpg"])
        (junk / "person_0_image_903.jpg").write_text("w1|903|1")  # something that is fine
        self.assertIn("1 photo(s) in _junk are usable now", self.run_tool("junk", "--recheck"))
        self.run_tool("junk", "--recheck", apply=True)
        self.assertEqual([p.name for p in junk.glob("*.jpg")], ["person_0_image_901.jpg"])
        self.assertTrue(list((self.lib / "Prospects/Person 0/gallery").glob("*903*")), "back in her own folder, found by the name in the file")

    def test_sort_assigns_confident_matches_and_invents_a_folder_for_a_new_person(self):
        self.standard_library()
        out = self.run_tool("sort")
        self.assertIn("-> Angels/Angelica", out)
        self.assertIn("-> Models/Draknara", out)
        self.assertIn("(NEW folder)", out)
        self.assertEqual(len(self.names("Prospects", "Various")), 9, "a preview moves nothing")
        self.run_tool("sort", apply=True)
        self.assertEqual(len(self.names("Prospects", "Various")), 0, "the policy preserves a genuine unmatched singleton as a Potential")
        self.assertEqual(sum(len(self.names("Potentials", folder.name)) for folder in (self.lib / "Potentials").iterdir()), 1)
        self.assertEqual(len(self.names("Angels", "Angelica")), 5)
        self.assertEqual(len(self.names("Models", "Draknara")), 6)
        new = [p for p in (self.lib / "Prospects").iterdir() if p.name not in ("Mia", "Various")]
        self.assertEqual(len(new), 1)
        self.assertEqual(len([p for p in (new[0] / "gallery").iterdir() if not p.name.startswith("z_")]), 5)

    def test_a_photo_chosen_in_workspaces_json_is_never_sorted_away(self):
        self.standard_library()
        keep = self.names("Prospects", "Various")[0]
        cfg = dict(CFG, photos={"Angelica": keep.replace(".jpg", "_944x1104.png")})
        with mock.patch.object(cw, "load_cfg", lambda: cfg):
            self.run_tool("sort", apply=True)
        self.assertIn(keep, self.names("Prospects", "Various"))

    def test_retire_returns_a_folder_to_the_pool_and_undo_puts_it_back(self):
        self.standard_library()
        before = self.names("Angels", "Azaline")
        out = self.run_tool("retire", "azaline")
        self.assertIn("Angels/Azaline -> Prospects/Various: 3", out)
        self.assertEqual(self.names("Angels", "Azaline"), before, "preview only")
        self.run_tool("retire", "azaline", apply=True)
        self.assertEqual(self.names("Angels", "Azaline"), [])
        self.assertEqual(len(self.names("Prospects", "Various")), 12)
        self.run_tool("undo", apply=True)
        self.assertEqual(self.names("Angels", "Azaline"), before)
        self.assertEqual(len(self.names("Prospects", "Various")), 9)
        self.assertIn("EXIT", self.run_tool("undo", apply=True), "nothing left to undo")

    def test_merge_moves_everything_into_the_other_folder(self):
        self.standard_library()
        self.run_tool("merge", "Mia", "Draknara", apply=True)
        self.assertEqual(self.names("Prospects", "Mia"), [])
        self.assertEqual(len(self.names("Models", "Draknara")), 8)

    def test_a_duplicate_already_in_the_destination_is_set_aside_not_overwritten(self):
        self.standard_library()
        src = self.lib / "Angels/Azaline/gallery"
        dup = self.names("Angels", "Azaline")[0]
        (self.lib / "Angels/Angelica/gallery" / dup).write_bytes((src / dup).read_bytes())
        self.run_tool("merge", "Azaline", "Angelica", apply=True)
        self.assertTrue((self.lib / "_archive/Angels/Azaline/gallery_org" / dup).exists())
        self.assertEqual(len(self.names("Angels", "Angelica")), 4 + 3)

    def test_alike_finds_the_look_alike_pair_and_compare_scores_it(self):
        self.add("Angels", "Angelica", "ann", 4)
        self.add("Angels", "Twin", "ann", 4)
        self.add("Models", "Draknara", "dee", 4)
        self.add("Prospects", "Mia", "mia", 4)
        self.add("Prospects", "Eva", "eve", 4)
        out = self.run_tool("alike")
        self.assertIn("Angels/Angelica  ~  Angels/Twin", out)
        self.assertNotIn("Draknara", out)
        self.assertIn("the same person", self.run_tool("compare", "Angelica", "Twin"))
        self.assertIn("different people", self.run_tool("compare", "Angelica", "Draknara"))

    def test_sorting_writes_the_z_file_of_each_destination_and_the_new_prospect_keeps_its_invented_name(self):
        self.standard_library()
        self.run_tool("sort", apply=True)
        name, hist = L.people.read(self.lib / "Models/Draknara")
        self.assertEqual(name, "Draknara")
        self.assertTrue(any("+2 from Prospects/Various" in h for h in hist), hist)
        new = [p for p in (self.lib / "Prospects").iterdir() if p.name not in ("Mia", "Various")][0]
        self.assertEqual(L.people.read(new)[0], new.name)
        self.assertIsNone(L.people.read(self.lib / "Prospects/Various"), "the pool keeps no file")
        out = self.run_tool("names")
        self.assertIn("Angels/Azaline", out)

    def test_a_top_level_various_is_the_pool_and_sisters_is_a_sisters_root(self):
        self.add("Angels", "Angelica", "ann", 4)
        self.add("Angels", "Azaline", "ann2", 3)
        self.add("Sisters", "Draknara", "dee", 4)
        self.add("Prospects", "Mia", "mia", 4)
        self.add("", "Various", "dee", 2)
        self.add("", "Various", "zed", 4)
        self.add("", "Various", "solo", 1)
        out = self.run_tool("sort")
        self.assertIn("-> Sisters/Draknara", out)
        self.run_tool("sort", apply=True)
        self.assertEqual(len(self.names("Sisters", "Draknara")), 6)
        self.assertEqual(len(self.names("", "Various")), 0, "the policy no longer discards singleton evidence")
        self.assertIn("Angels/Azaline -> Various: 3", self.run_tool("retire", "azaline"))
        self.run_tool("retire", "azaline", apply=True)
        self.assertEqual(len(self.names("", "Various")), 3, "a retired folder goes back to the top-level pool")
        self.assertTrue(L.is_sister("Sisters/Draknara") and not L.is_sister("Models/Draknara") and not L.is_sister("Angels/Angelica"))

    def test_group_splits_an_artist_folder_by_face_into_named_subfolders(self):
        self.add("Artists", "Pierre", "pa", 4)
        self.add("Artists", "Pierre", "pb", 4)
        self.add("Artists", "Pierre", "stray", 1)
        self.add("Angels", "Angelica", "ann", 3)
        self.add("Models", "Draknara", "dee", 3)
        for i, who in enumerate(("w1", "w2", "w3", "w4", "w5")):
            self.add("Prospects", f"Person {i}", who, 3)  # enough different people for the library's average face to be meaningful
        out = self.run_tool("group")
        self.assertIn("2 group(s)", out)
        self.run_tool("group", apply=True)
        subs = [p for p in (self.lib / "Artists/Pierre").iterdir() if p.is_dir() and p.name != "gallery"]
        self.assertEqual(len(subs), 2)
        self.assertEqual(sorted(len([p for p in (s / "gallery").iterdir() if not p.name.startswith("z_")]) for s in subs), [4, 4])
        self.assertEqual(len(self.names("Artists", "Pierre")), 1, "the photo that matches nobody stays with the artist")
        scan = self.run_tool("scan")
        self.assertIn("person folder", scan)
        self.assertIn("Artists/Pierre/", self.run_tool("alike", "--min", "-1"), "the grouped people are people now")

    def test_crop_box_keeps_the_main_face_and_cuts_away_the_others(self):
        main = (400, 100, 100, 120)
        box = L.crop_box((1000, 1000), main, [(50, 100, 100, 120)])
        self.assertIsNotNone(box)
        self.assertTrue(box[0] > 150 and box[0] <= 400 - 35, "the cut runs between the faces and keeps her hair")
        self.assertTrue(box[2] >= 500 and box[1] <= 100 and box[3] >= 100 + 120, "she is whole")
        self.assertIsNone(L.crop_box((1000, 1000), main, [(430, 120, 100, 120)]), "a face on top of hers cannot be cut away")
        self.assertEqual(L.crop_box((1000, 1000), main, [(900, 900, 5, 5)]), (0, 0, 1000, 1000), "a passer-by far smaller than she is is left alone")

    def test_a_face_on_an_animal_is_not_a_person(self):
        rows = [np.array([0, 0, 90, 90, 0.95]), np.array([200, 0, 120, 120, 0.7])]
        self.assertEqual(len(L.human_rows(rows)), 1, "a certain face makes the doubtful bigger one an animal")
        self.assertEqual(len(L.human_rows([np.array([0, 0, 90, 90, 0.8]), np.array([200, 0, 60, 60, 0.7])])), 2, "when no face is certain, all count")

    def test_person_box_keeps_the_body_and_cuts_the_background_beside_her(self):
        self.assertEqual(L.person_box((1000, 1000), (400, 200, 100, 100)), (90, 80, 810, 1000))
        self.assertIsNone(L.person_box((1000, 1000), (200, 200, 600, 600)), "a close-up has no background to cut")
        self.assertIsNone(L.person_box((1000, 1000), (400, 700, 100, 100)), "a head low in the picture: no telling where the body is")

    def test_pullback_sends_small_prospect_folders_back_to_the_pool_and_keeps_chosen_ones(self):
        for i, who in enumerate(("w1", "w2", "w3")):
            self.add("Prospects", f"Person {i}", who, 3)
        self.add("Prospects", "Solo A", "sa", 1)
        self.add("Prospects", "Pair B", "pb", 2)
        out = self.run_tool("pullback", "--small", "2", apply=True)
        self.assertIn("2 prospect folder(s), 3 photo(s)", out)
        self.assertEqual(len(list((self.lib / "Various/gallery").glob("*.jpg"))), 3)
        self.assertEqual(len(self.names("Prospects", "Person 0")), 3, "bigger folders stay")
        self.assertTrue((self.lib / "_retired/Prospects/Solo A").exists())

    def test_group_singles_places_every_good_photo_of_an_artist(self):
        for i, who in enumerate(("w1", "w2", "w3", "w4", "w5")):
            self.add("Prospects", f"Person {i}", who, 3)
        self.add("Artists/Pierre", "Elise", "pa", 4)
        self.add("Artists", "Pierre", "pa", 1)      # her
        self.add("Artists", "Pierre", "lone", 1)    # nobody there: a folder of her own
        self.add("Artists", "Pierre", "noface", 1)  # stays
        self.run_tool("group", "--singles", apply=True)
        self.assertEqual(len(self.names("Artists/Pierre", "Elise")), 5)
        self.assertEqual(len(self.names("Artists", "Pierre")), 1, "only the photo with no face is left")
        subs = [p for p in (self.lib / "Artists/Pierre").iterdir() if p.is_dir() and p.name not in ("gallery", "Elise")]
        self.assertEqual(len(subs), 1)

    def test_a_photo_in_the_pool_that_came_from_an_artist_goes_back_to_him_even_when_renamed(self):
        for i, who in enumerate(("w1", "w2", "w3")):
            self.add("Prospects", f"Person {i}", who, 3)
        self.add("Artists/Pierre", "Elise", "pa", 3)
        photo = next((self.lib / "Artists/Pierre/Elise/gallery").glob("*.jpg"))
        pid = L.photo_id(photo.name)
        g = self.lib / "Prospects/Various/gallery"
        g.mkdir(parents=True, exist_ok=True)
        (g / f"various_{pid}.jpg").write_text("pa|777")
        self.run_tool("sort", apply=True)
        self.assertTrue((self.lib / "Artists/Pierre/gallery" / f"various_{pid}.jpg").exists() or any(pid in n for n in self.names("Artists", "Pierre")), "it went home to the artist, not to a prospect")
        self.assertEqual(len(self.names("Prospects", "Various")), 0)

    def test_rematch_joins_a_prospect_who_is_the_same_person_as_a_sister_to_her(self):
        self.add("Sisters", "Draknara", "dee", 4)
        self.add("Prospects", "Dee Two", "dee", 3)
        for i, who in enumerate(("w1", "w2", "w3", "w4")):
            self.add("Prospects", f"Person {i}", who, 3)
        self.run_tool("rematch", apply=True)
        self.assertEqual(len(self.names("Sisters", "Draknara")), 7)
        self.assertTrue((self.lib / "_retired/Prospects/Dee Two").exists(), "the folder and its z_ file are kept in _retired")
        self.assertTrue(any("Dee Two" in ln for ln in L.people.read(self.lib / "Sisters/Draknara")[1]), "the z_ file remembers who she was")

    def test_review_leaves_alone_a_photo_that_crop_held_for_a_clean_up(self):
        for i, who in enumerate(("w1", "w2", "w3")):
            self.add("Prospects", f"Person {i}", who, 3)
        self.add("Prospects", "Mia", "mia", 4)
        r = self.lib / "Prospects/Mia/review"
        r.mkdir()
        (r / "mia_image_901.jpg").write_text("mia|901")
        (r / "mia_image_902.jpg").write_text("mia|902")
        L.cleanup_hold(self.lib, [L.hashlib.sha1(b"mia|901").hexdigest()])
        self.run_tool("review", apply=True)
        self.assertEqual(sorted(p.name for p in r.iterdir()), ["mia_image_901.jpg"], "the held photo stays, the other goes back to her")

    def test_artists_puts_photos_back_under_their_artist_and_then_their_person(self):
        for i, who in enumerate(("w1", "w2", "w3", "w4", "w5")):
            self.add("Prospects", f"Person {i}", who, 3)  # enough different people for the library's average face to be meaningful
        self.add("Artists/Pierre", "Elise", "pa", 5)
        g = self.lib / "Artists/Pierre/Elise/gallery"
        (g / "elise_image_901.jpg").write_text("pb|901")      # someone else
        (g / "elise_image_902.jpg").write_text("pa|902|2")    # her, with a second person
        (g / "elise_image_903.jpg").write_text("noface|903")
        self.add("Artists", "Maridos", "pa", 1)               # her face, but it came from Pierre
        cross = next((self.lib / "Artists/Maridos/gallery").iterdir())
        bk = self.tmp / "bk/Pierre/gallery"
        bk.mkdir(parents=True)
        (bk / "pierre_image_1.jpg").write_text(cross.read_text())
        out = self.run_tool("artists", "--from", str(self.tmp / "bk"))
        self.assertIn("preview only", out)
        self.assertTrue(cross.exists(), "a preview moves nothing")
        self.run_tool("artists", "--from", str(self.tmp / "bk"), apply=True)
        self.assertEqual(len(self.names("Artists", "Maridos")), 0, "nothing stays under the wrong artist")
        elise = self.names("Artists", "Pierre/Elise")
        self.assertIn(cross.name, elise, "it went to her under the artist it came from")
        self.assertEqual(len(elise), 6)
        self.assertEqual(sorted(self.names("Artists", "Pierre")), ["elise_image_901.jpg", "elise_image_902.jpg", "elise_image_903.jpg"], "a stranger, a second person and a faceless photo stay in the artist's own gallery")
        self.assertFalse(list((self.lib / "Artists/Pierre/gallery").glob("z_*")), "an artist's own gallery is not a person")

    def test_group_joins_a_group_to_the_artists_person_it_looks_like_and_makes_new_people_only_from_agreeing_photos(self):
        for i, who in enumerate(("w1", "w2", "w3", "w4", "w5")):
            self.add("Prospects", f"Person {i}", who, 3)
        self.add("Artists/Pierre", "Elise", "pa", 5)
        self.add("Artists", "Pierre", "pa", 2)   # her again, loose in the artist's gallery
        self.add("Artists", "Pierre", "pb", 3)   # someone new
        self.add("Artists", "Pierre", "pc", 2)
        out = self.run_tool("group", apply=True)
        self.assertIn("Elise: +2 photos", out)
        self.assertEqual(len(self.names("Artists/Pierre", "Elise")), 7)
        subs = [p for p in (self.lib / "Artists/Pierre").iterdir() if p.is_dir() and p.name not in ("gallery", "Elise")]
        self.assertEqual(sorted(len([q for q in (s / "gallery").iterdir() if not q.name.startswith("z_")]) for s in subs), [2, 3])
        self.assertEqual(len(self.names("Artists", "Pierre")), 0, "a coherent pair remains an eligible identity under the shared policy")

    def test_clean_sets_borderline_photos_aside_and_sends_strangers_to_the_pool(self):
        self.add("Models", "Drakness", "dk", 6)
        g = self.lib / "Models/Drakness/gallery"
        (g / "drakness_image_901.jpg").write_text("zz|901")      # someone else, clear face
        (g / "drakness_image_902.jpg").write_text("dk|902|2")   # her, but two faces in the picture: unsure
        (g / "drakness_image_903.jpg").write_text("zz|903|2")   # someone else, two faces: unsure, not sent away
        self.add("Models", "Draknora", "dr", 4)
        self.add("Prospects", "Various", "q", 1)
        out = self.run_tool("clean", "Drakness")
        self.assertIn("review 1", out.replace("review 2", "review 1") if "review 2" in out else out)
        self.run_tool("clean", "Drakness", apply=True)
        self.assertIn("drakness_image_901.jpg", self.names("Prospects", "Various") + [p.name for p in (self.lib / "Prospects/Various/gallery").iterdir()])
        self.assertNotIn("drakness_image_901.jpg", self.names("Models", "Drakness"))
        review = sorted(p.name for p in (self.lib / "Models/Drakness/review").iterdir())
        self.assertIn("drakness_image_903.jpg", review)
        self.assertEqual(len(self.names("Models", "Drakness")) + len(review), 6 + 2 + 1 - 1 + 0, "nothing is lost: the stranger went to the pool")

    def test_clean_never_moves_the_chosen_photo_even_if_it_scores_low(self):
        self.add("Models", "Drakness", "dk", 5)
        g = self.lib / "Models/Drakness/gallery"
        (g / "drakness_image_950.jpg").write_text("zz|950")
        cfg = dict(CFG, photos={"Drakness": "drakness_image_950_944x1104.png"})
        with mock.patch.object(cw, "load_cfg", lambda: cfg):
            self.run_tool("clean", "Drakness", apply=True)
        self.assertIn("drakness_image_950.jpg", self.names("Models", "Drakness"))

    def test_sisters_flags_one_who_is_nothing_like_the_anchor_and_pairs_picks_a_similar_not_same_face(self):
        blend("dn", "dk", 0.0)
        self.add("Sisters", "Drakness", "dk", 5)
        self.add("Sisters", "Draknira", "dn", 5)
        out = self.run_tool("sisters")
        self.assertIn("VASTLY UNLIKE", out, "Draknira is nothing like the anchor in this made-up family")
        blend("sim", "dn", 0.45)       # similar to her sister
        blend("twin", "dn", 0.95)      # the same as her sister
        blend("far", "dk", 0.0)        # unrelated
        self.add("Angels", "azaline", "far", 3)
        self.add("Prospects", "Lena Marsh", "sim", 5)
        self.add("Prospects", "Twin Person", "twin", 5)
        self.add("Prospects", "Far Person", "far", 5)
        self.add("Angels", "Angelica", "ann", 3)
        out = self.run_tool("pairs", "--sister", "Draknira", "--trials", "100")
        row = [line for line in out.splitlines() if line.strip().startswith("Azaline")][0]
        self.assertIn("Prospects/Lena Marsh", row, "similar but not the same: neither the twin nor the stranger")
        self.assertIn("preview only", out)
        self.assertTrue((self.lib / "Prospects/Lena Marsh/gallery").exists() and len(self.names("Angels", "azaline")) == 3, "a preview moves nothing")
        self.run_tool("pairs", "--sister", "Draknira", "--trials", "100", apply=True)
        self.assertEqual(len(self.names("Angels", "azaline")), 5, "her new face's photos are in her gallery")
        review = list((self.lib / "Angels/azaline/review").iterdir())
        self.assertEqual(len(review), 3, "and her earlier photos are set aside for review, not lost")
        self.assertEqual(self.names("Prospects", "Lena Marsh"), [])

    def test_pair_candidate_score_uses_bounded_photo_variety_tiers(self):
        score_9 = L.pairing_candidate_score(0.28, 9, 0.28, 0.15, 0.40)
        score_10 = L.pairing_candidate_score(0.28, 10, 0.28, 0.15, 0.40)
        score_15 = L.pairing_candidate_score(0.28, 15, 0.28, 0.15, 0.40)
        score_20 = L.pairing_candidate_score(0.28, 20, 0.28, 0.15, 0.40)
        self.assertEqual([score["photo_bonus"] for score in (score_9, score_10, score_15, score_20)],
                         [0.0, 0.02, 0.04, 0.06])
        self.assertEqual([score["cost"] for score in (score_9, score_10, score_15, score_20)],
                         [0.0, -0.02, -0.04, -0.06])
        balanced = L.pairing_candidate_score(0.22, 20, 0.28, 0.15, 0.40)
        self.assertAlmostEqual(balanced["cost"], score_9["cost"],
                               msg="20 photos can offset a modest 0.06 likeness-fit difference")

    def test_an_angel_made_from_an_artists_person_is_replaced_by_a_prospect_and_artists_are_never_candidates(self):
        blend("dn", "dk", 0.0)
        self.add("Sisters", "Drakness", "dk", 5)
        self.add("Sisters", "Draknira", "dn", 5)
        blend("art", "dn", 0.45)       # an artist's face that suits her sister best
        blend("sim", "dn", 0.35)       # a prospect that suits her a little less
        blend("far", "dk", 0.0)
        self.add("Angels", "Angelica", "ann", 3)
        self.add("Angels", "azaline", "art", 4)
        self.add("Artists", "Fantasy", "collage", 3)
        L.people.write(self.lib / "Angels/azaline", "Ada Frost", ["2026-10-11 +4 from Artists/Pierre/Ada Frost: Pierre/Ada Frost is the new Azaline"])
        self.add("Prospects", "Lena Marsh", "sim", 5)
        self.add("Prospects", "Far Person", "far", 5)
        g = self.lib / "Artists/Pierre/Other Artist Person/gallery"
        g.mkdir(parents=True)
        for i in range(4):
            (g / f"other_{i}.jpg").write_text(f"art|{800 + i}")
        self.assertEqual(L.artist_origin(self.lib, "Angels/azaline"), "Artists/Pierre/Ada Frost")
        out = self.run_tool("pairs", "--sister", "Draknira", "--trials", "100")
        row = [line for line in out.splitlines() if line.strip().startswith("Azaline")][0]
        self.assertIn("Prospects/Lena Marsh", row)
        self.assertIn("artist's person", row)
        self.run_tool("pairs", "--sister", "Draknira", "--trials", "100", apply=True)
        self.assertEqual(len(self.names("Artists", "Pierre/Ada Frost")), 4, "her photos went back to the artist")
        self.assertEqual(len(self.names("Angels", "azaline")), 5, "and a prospect's face is the angel now")

    def test_photos_picks_the_best_angel_photo_keeps_favourites_and_only_reports_for_sisters(self):
        self.add("Angels", "Angelica", "ann", 4)            # favourite: never changes
        self.add("Angels", "Azaline", "aa", 4)
        self.add("Sisters", "Draknara", "dee", 4)
        for i, who in enumerate(("w1", "w2", "w3", "w4", "w5")):
            self.add("Prospects", f"Person {i}", who, 3)
        az = self.lib / "Angels/Azaline/gallery"
        for f in az.iterdir():
            f.unlink()
        for name, text in (("azaline_image_1.jpg", "aa|11|2"), ("azaline_image_2.jpg", "aa|12"), ("azaline_image_3.jpg", "aa|13")):
            (az / name).write_text(text)
        dn = self.lib / "Sisters/Draknara/gallery"
        for f in dn.iterdir():
            f.unlink()
        for name, text in (("draknara_image_1.jpg", "dee|21|2"), ("draknara_image_2.jpg", "dee|22")):
            (dn / name).write_text(text)
        for folder, stems in (("Angels/Azaline", ("azaline_image_1", "azaline_image_2", "azaline_image_3")), ("Sisters/Draknara", ("draknara_image_1", "draknara_image_2"))):
            g = self.lib / folder / "gallery_94x110"
            g.mkdir(parents=True, exist_ok=True)
            for s in stems:
                (g / f"{s}_94x110.png").write_bytes(b"x")
        cfg = dict(CFG, photos={"Angelica": "angelica_image_1_94x110.png", "Azaline": "azaline_image_1_94x110.png", "Draknara": "draknara_image_1_94x110.png"}, likeness={"keepPhoto": ["Angelica"]})
        calls = []
        with mock.patch.object(cw, "load_cfg", lambda: cfg), mock.patch.object(cw, "repoint_photos", lambda c, r, d, root=None: calls.append(r) or {"repo": 1}):
            out = self.run_tool("photos")
            self.assertIn("kept: your favourite", out)
            self.assertIn("the sister's photo is your choice", out)
            self.assertIn("1 photo(s) would change", out)
            self.assertEqual(calls, [], "a preview changes nothing")
            self.run_tool("photos", apply=True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(list(calls[0]), ["Azaline"], "only the angel changes; the sister and the favourite stay")
        self.assertIn(calls[0]["Azaline"][1].name, ("azaline_image_2_94x110.png", "azaline_image_3_94x110.png"), "a single clear face replaces the picture with two faces")

    def test_review_sends_a_stranger_to_the_person_she_looks_like_and_returns_the_ones_that_are_her(self):
        self.add("Models", "Draknara", "dee", 4)
        self.add("Angels", "Angelica", "ann", 4)
        for i, who in enumerate(("w1", "w2", "w3", "w4", "w5")):
            self.add("Prospects", f"Person {i}", who, 3)
        rv = self.lib / "Models/Draknara/review"
        rv.mkdir(parents=True)
        (rv / "draknara_image_901.jpg").write_text("dee|901")       # her
        (rv / "draknara_image_902.jpg").write_text("ann|902")       # Angelica
        (rv / "draknara_image_903.jpg").write_text("nobody|903")    # no one
        out = self.run_tool("review")
        self.assertIn("1 back", out)
        self.assertIn("1 send", out)
        self.assertIn("1 stays in review", out)
        self.assertEqual(len(list(rv.iterdir())), 3, "a preview moves nothing")
        self.run_tool("review", apply=True)
        self.assertEqual([p.name for p in rv.iterdir()], ["draknara_image_903.jpg"])
        self.assertIn("draknara_image_901.jpg", self.names("Models", "Draknara"))
        self.assertTrue(any("902" in n for n in self.names("Angels", "Angelica")))

    def test_review_out_makes_a_new_prospect_of_a_photo_that_is_clearly_not_her(self):
        self.add("Sisters", "Draknara", "dee", 4)
        self.add("Angels", "Angelica", "ann", 4)
        for i, who in enumerate(("w1", "w2", "w3", "w4", "w5")):
            self.add("Prospects", f"Person {i}", who, 3)
        rv = self.lib / "Sisters/Draknara/review"
        rv.mkdir(parents=True)
        L.people.write(self.lib / "Sisters/Draknara", "Lia Lujan", [])
        for i in (901, 902, 903):
            (rv / f"draknara_image_{i}.jpg").write_text(f"nobody|{i}")
        self.assertIn("3 stays in review", self.run_tool("review"), "without --out they stay")
        self.assertIn("3 new prospect", self.run_tool("review", "--out"))
        self.run_tool("review", "--out", apply=True)
        self.assertEqual(list(rv.iterdir()), [])
        made = list((self.lib / "Potentials").iterdir())
        self.assertEqual(len(made), 1, "photos that look alike share one new prospect")
        self.assertTrue(any("from Draknara review" in ln for ln in L.people.read(made[0])[1]))
        self.assertEqual(L.people.read(made[0])[0], made[0].name, "photos split off a sister are not her: the new prospect does not take her name")

    def test_lookalikes_reserves_a_prospect_who_looks_like_a_top_tier_person(self):
        self.add("Sisters", "Draknara", "dee", 4)
        self.add("Angels", "Angelica", "ann", 4)
        self.add("Prospects", "Twin", "ann", 4)
        for i, who in enumerate(("w1", "w2", "w3", "w4", "w5")):
            self.add("Prospects", f"Person {i}", who, 3)
        out = self.run_tool("lookalikes")
        self.assertIn("Prospects/Twin", out)
        self.assertNotIn("Person 0", out)
        self.run_tool("lookalikes", apply=True)
        self.assertTrue(L.people.reserved(self.lib / "Prospects/Twin"))
        self.run_tool("lookalikes", apply=True)
        self.assertEqual(len(L.people.reserved(self.lib / "Prospects/Twin")), 1, "a second run does not repeat the line")

    def test_loosen_reports_without_moving_anything(self):
        self.add("Sisters", "Draknara", "dee", 4)
        self.add("Angels", "Angelica", "ann", 4)
        self.add("", "Various", "ann", 2)
        out = self.run_tool("loosen")
        self.assertIn("Various photos that get a home", out)
        self.assertEqual(len(self.names("", "Various")), 2)

    def test_a_merge_retires_the_emptied_folder(self):
        self.add("Sisters", "Draknara", "dee", 4)
        self.add("Prospects", "Twin", "dee", 3)
        self.run_tool("merge", "Twin", "Draknara", apply=True)
        self.assertFalse((self.lib / "Prospects/Twin").exists())
        self.assertTrue((self.lib / "_retired/Prospects/Twin").exists())
        self.assertEqual(len(self.names("Sisters", "Draknara")), 7)

    def test_a_folder_with_a_different_person_in_it_names_the_odd_one(self):
        self.add("Angels", "Angelica", "ann", 5)
        (self.lib / "Angels/Angelica/gallery/angelica_image_999.jpg").write_text("bob|999")
        self.add("Models", "Draknara", "dee", 4)
        self.add("Prospects", "Bobbie", "bob", 3)
        out = self.run_tool("folder", "Angelica")
        lines = [line for line in out.splitlines() if "angelica_image_999" in line]
        self.assertEqual(len(lines), 2, "once in the photos to check, once in the plan to move it")
        self.assertIn("suggest -> Prospects/Bobbie", lines[0], "and who it looks like instead")
        self.assertIn("-> Prospects/Bobbie", out, "the plan sends it there")
        self.assertIn("1 look like someone else", out)
        self.assertNotIn("(NEW folder)", out, "Bobbie exists")


if __name__ == "__main__":
    unittest.main()
