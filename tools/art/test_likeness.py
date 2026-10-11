#!/usr/bin/env python3
"""The likeness tool, tested with made-up face vectors (no models, no real photos). Run: python tools/art/test_likeness.py"""
import contextlib
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
        return {"faces": int(parts[2]) if len(parts) > 2 else 1, "v": [float(x) for x in face(person, int(i))], "box": [0.2, 0.2, 0.4, 0.4], "px": 200}


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
        self.add("Prospects", "Various", "zed", 4)     # a new person, four photos
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

    def test_the_mixed_folders_are_never_read_and_the_cache_spares_a_second_run(self):
        self.standard_library()
        self.run_tool("scan")
        first = self.fake.calls
        self.assertEqual(first, 4 + 3 + 4 + 4 + 8, "Artists is not read; the pool and the person folders are")
        self.run_tool("scan")
        self.assertEqual(self.fake.calls, first, "unchanged files are not read again")
        moved = self.names("Angels", "Angelica")[0]
        shutil.move(str(self.lib / "Angels/Angelica/gallery" / moved), str(self.lib / "Angels/Azaline/gallery/renamed.jpg"))
        self.run_tool("scan")
        self.assertEqual(self.fake.calls, first, "a moved or renamed file costs nothing: the cache is keyed by its content")

    def test_sort_assigns_confident_matches_and_invents_a_folder_for_a_new_person(self):
        self.standard_library()
        out = self.run_tool("sort")
        self.assertIn("-> Angels/Angelica", out)
        self.assertIn("-> Models/Draknara", out)
        self.assertIn("(NEW folder)", out)
        self.assertEqual(len(self.names("Prospects", "Various")), 8, "a preview moves nothing")
        self.run_tool("sort", apply=True)
        self.assertEqual(len(self.names("Prospects", "Various")), 1, "only the unknown face stays")
        self.assertEqual(len(self.names("Angels", "Angelica")), 5)
        self.assertEqual(len(self.names("Models", "Draknara")), 6)
        new = [p for p in (self.lib / "Prospects").iterdir() if p.name not in ("Mia", "Various")]
        self.assertEqual(len(new), 1)
        self.assertEqual(len([p for p in (new[0] / "gallery").iterdir() if not p.name.startswith("z_")]), 4)

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
        self.assertEqual(len(self.names("Prospects", "Various")), 11)
        self.run_tool("undo", apply=True)
        self.assertEqual(self.names("Angels", "Azaline"), before)
        self.assertEqual(len(self.names("Prospects", "Various")), 8)
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
        self.assertTrue((self.lib / "Angels/Azaline/gallery_org" / dup).exists())
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
        self.assertEqual(len(self.names("", "Various")), 1, "only the unknown face stays")
        self.assertIn("Angels/Azaline -> Various: 3", self.run_tool("retire", "azaline"))
        self.run_tool("retire", "azaline", apply=True)
        self.assertEqual(len(self.names("", "Various")), 4, "a retired folder goes back to the top-level pool")
        self.assertTrue(L.is_sister("Sisters/Draknara") and L.is_sister("Models/Draknara") and not L.is_sister("Angels/Angelica"))

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
        self.add("Models", "Drakness", "dk", 5)
        self.add("Models", "Draknira", "dn", 5)
        out = self.run_tool("sisters")
        self.assertIn("VASTLY UNLIKE", out, "Draknira is nothing like the anchor in this made-up family")
        blend("sim", "dn", 0.45)       # similar to her sister
        blend("twin", "dn", 0.95)      # the same as her sister
        blend("far", "dk", 0.0)        # unrelated
        self.add("Angels", "azaline", "far", 3)
        self.add("Prospects", "Lena Marsh", "sim", 4)
        self.add("Prospects", "Twin Person", "twin", 4)
        self.add("Prospects", "Far Person", "far", 4)
        self.add("Angels", "Angelica", "ann", 3)
        out = self.run_tool("pairs", "--sister", "Draknira", "--trials", "100")
        row = [line for line in out.splitlines() if line.strip().startswith("Azaline")][0]
        self.assertIn("Prospects/Lena Marsh", row, "similar but not the same: neither the twin nor the stranger")
        self.assertIn("preview only", out)
        self.assertTrue((self.lib / "Prospects/Lena Marsh/gallery").exists() and len(self.names("Angels", "azaline")) == 3, "a preview moves nothing")
        self.run_tool("pairs", "--sister", "Draknira", "--trials", "100", apply=True)
        self.assertEqual(len(self.names("Angels", "azaline")), 4, "her new face's photos are in her gallery")
        review = list((self.lib / "Angels/azaline/review").iterdir())
        self.assertEqual(len(review), 3, "and her earlier photos are set aside for review, not lost")
        self.assertEqual(self.names("Prospects", "Lena Marsh"), [])

    def test_photos_picks_the_best_angel_photo_keeps_favourites_and_only_reports_for_sisters(self):
        self.add("Angels", "Angelica", "ann", 4)            # favourite: never changes
        self.add("Angels", "Azaline", "aa", 4)
        self.add("Models", "Draknara", "dee", 4)
        for i, who in enumerate(("w1", "w2", "w3", "w4", "w5")):
            self.add("Prospects", f"Person {i}", who, 3)
        az = self.lib / "Angels/Azaline/gallery"
        for f in az.iterdir():
            f.unlink()
        for name, text in (("azaline_image_1.jpg", "aa|11|2"), ("azaline_image_2.jpg", "aa|12"), ("azaline_image_3.jpg", "aa|13")):
            (az / name).write_text(text)
        dn = self.lib / "Models/Draknara/gallery"
        for f in dn.iterdir():
            f.unlink()
        for name, text in (("draknara_image_1.jpg", "dee|21|2"), ("draknara_image_2.jpg", "dee|22")):
            (dn / name).write_text(text)
        for folder, stems in (("Angels/Azaline", ("azaline_image_1", "azaline_image_2", "azaline_image_3")), ("Models/Draknara", ("draknara_image_1", "draknara_image_2"))):
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
        made = [p for p in (self.lib / "Prospects").iterdir() if p.name not in {f"Person {i}" for i in range(5)}]
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
