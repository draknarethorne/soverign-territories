import contextlib
import hashlib
import io
import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

import numpy as np

from tools.art.likeness_library import universe_sandbox as us
from tools.art.likeness_library.scoring import nz

ROOT = pathlib.Path(__file__).resolve().parents[4]
POLICY = {"scoreBands": {"green": {"minimum": 0.55}, "yellow": {"minimum": 0.30}, "orange": {"minimum": 0.15}}}


def row(source, owner, digest, photo_id, status="eligible"):
    parts = source.split("/")
    return {"source": source, "owner": owner, "group": parts[0], "bucket": parts[-2],
            "sourceHash": digest, "photoId": photo_id, "sourceStatus": status}


class FakeVectors:
    mean_source = "fixture"

    def __init__(self, values):
        self.values = {key: nz(np.asarray(value, float)) for key, value in values.items()}

    def get(self, source):
        return self.values.get(source)


class SelectionTests(unittest.TestCase):
    def world(self):
        rows = [
            row("Angels/A/gallery/a_image_1.jpg", "Angels/A", "h-a1", "photo:image_1"),
            row("Angels/A/gallery/a_image_2.jpg", "Angels/A", "h-a2", "photo:image_2"),
            row("Potentials/Moved/gallery/m_image_3.jpg", "Potentials/Moved", "h-m1", "photo:image_3"),
            row("Potentials/Moved/gallery/m_image_4.jpg", "Potentials/Moved", "h-m2", "photo:image_4"),
            row("Potentials/Near/gallery/n_image_5.jpg", "Potentials/Near", "h-n1", "photo:image_5"),
            row("Potentials/Near/gallery/n_image_6.jpg", "Potentials/Near", "h-nocov", "photo:image_6"),
            row("Potentials/Far/gallery/f_image_7.jpg", "Potentials/Far", "h-f1", "photo:image_7"),
            row("Prospects/Inc/gallery/i_image_8.jpg", "Prospects/Inc", "h-i1", "photo:image_8"),
            row("Various/gallery/v_image_9.jpg", "Various", "h-v1", "photo:image_9"),
            row("Various/gallery/v_image_10.jpg", "Various", "h-v2", "photo:image_10"),
            row("Various/gallery/copy_image_1.jpg", "Various", "h-a1", "photo:image_1", "same-content-nonvoting"),
            row("Various/gallery/junk_image_11.jpg", "Various", "h-j", "photo:image_11", "unsupported"),
        ]
        vectors = FakeVectors({
            "Angels/A/gallery/a_image_1.jpg": [1, 0, 0, 0],
            "Angels/A/gallery/a_image_2.jpg": [1, .1, 0, 0],
            "Potentials/Moved/gallery/m_image_3.jpg": [0, 0, 1, 0],
            "Potentials/Moved/gallery/m_image_4.jpg": [0, 0, 0, 1],
            "Potentials/Near/gallery/n_image_5.jpg": [1, 1.7, 0, 0],
            "Potentials/Near/gallery/n_image_6.jpg": [1, 1.7, 0, 0],
            "Potentials/Far/gallery/f_image_7.jpg": [.2, 0, 0, .98],
            "Prospects/Inc/gallery/i_image_8.jpg": [0, 0, 0, 1],
            "Various/gallery/v_image_9.jpg": [1, 0, .5, 0],
            "Various/gallery/v_image_10.jpg": [0, 1, 0, 0],
            "Various/gallery/copy_image_1.jpg": [1, 0, 0, 0],
        })
        placements = {"photo:image_3": {"folder": "Angels/A", "bucket": "Review", "score": .41,
                                        "closest": [], "evidence": "review-data"}}
        prep = {digest: [{"source": "x"}] for digest in
                ("h-a1", "h-a2", "h-m1", "h-m2", "h-n1", "h-f1", "h-i1", "h-v1", "h-v2")}
        return rows, placements, prep, vectors

    def select(self, **overrides):
        rows, placements, prep, vectors = self.world()
        options = {"seeds": ["A"], "includes": ["Inc", "Nobody"], "hops": 1}
        options.update(overrides)
        return us.select_universe(rows, placements, prep, lambda _sources: vectors, POLICY, **options)

    def test_selection_records_reasons_scores_and_exclusions(self):
        plan = self.select()
        self.assertEqual(plan["seeds"], {"A": ["Angels/A"]})
        self.assertEqual(plan["includes"], {"Inc": ["Prospects/Inc"]})
        self.assertEqual(plan["notFound"], ["Nobody"])
        identities = {item["identity"]: item for item in plan["identities"]}
        self.assertEqual(identities["Angels/A"]["hop"], 0)
        self.assertEqual(identities["Prospects/Inc"]["reason"], "user-include")
        self.assertEqual(identities["Potentials/Near"]["hop"], 1)
        self.assertGreaterEqual(identities["Potentials/Near"]["bestScore"], .30)
        self.assertLess(identities["Potentials/Near"]["bestScore"], .99)
        # The moved photo is not scored against itself: its distinct member is orthogonal.
        moved = identities["Potentials/Moved"]
        self.assertEqual(moved["scoreBasis"], "shares-1-seed-photo(s)")
        self.assertEqual(moved["sharedSeedPhotos"], 1)
        self.assertAlmostEqual(moved["bestScore"], 0.0, places=4)
        self.assertNotIn("Potentials/Far", identities)
        self.assertEqual([item["identity"] for item in plan["interestingNotIncluded"]], ["Potentials/Far"])
        self.assertEqual(plan["interestingNotIncluded"][0]["band"], "orange")

        photos = {photo["preSource"]: photo for photo in plan["photos"]}
        self.assertIn("Various/gallery/v_image_9.jpg", photos)
        self.assertNotIn("Various/gallery/v_image_10.jpg", photos)
        self.assertNotIn("Various/gallery/junk_image_11.jpg", photos)
        self.assertNotIn("Potentials/Far/gallery/f_image_7.jpg", photos)
        moved_photo = photos["Potentials/Moved/gallery/m_image_3.jpg"]
        self.assertEqual(moved_photo["hop"], 0)
        self.assertEqual(moved_photo["currentFolder"], "Angels/A")
        self.assertIn("seed-current-placement:Angels/A/Review", moved_photo["reasons"])
        excluded = {item["source"]: item["reason"] for item in plan["excluded"]}
        self.assertIn("identical content", excluded["Various/gallery/copy_image_1.jpg"])
        self.assertIn("no sealed-preparation row", excluded["Potentials/Near/gallery/n_image_6.jpg"])
        self.assertEqual(len({photo["sourceSha256"] for photo in plan["photos"]}), len(plan["photos"]))

    def test_hops_zero_and_photo_bound(self):
        plan = self.select(hops=0)
        self.assertEqual({item["hop"] for item in plan["identities"]}, {0})
        self.assertEqual(plan["interestingNotIncluded"], [])
        bounded = self.select(max_photos=5)
        self.assertLessEqual(len(bounded["photos"]), 5)
        self.assertTrue(bounded["boundedOut"])
        with self.assertRaises(us.UniverseError):
            self.select(hops=3)
        with self.assertRaisesRegex(us.UniverseError, "no seed identity"):
            self.select(seeds=["Nobody"])

    def test_hop_two_uses_its_own_band(self):
        one = self.select(hops=1)
        green = self.select(hops=2)
        orange = self.select(hops=2, hop2_band="orange")
        self.assertNotIn("Potentials/Far", {item["identity"] for item in one["identities"]})
        self.assertEqual((green["hop2Band"], green["hop2Minimum"]), ("green", .55))
        self.assertEqual((orange["hop2Band"], orange["hop2Minimum"]), ("orange", .15))
        far = {item["identity"]: item for item in green["identities"]}["Potentials/Far"]
        self.assertEqual((far["hop"], far["via"]), (2, "Potentials/Moved"))
        self.assertGreaterEqual(far["bestScore"], .55)

    def test_resolve_names_case_and_category(self):
        resolved, missing = us.resolve_names(
            ["angels/a", "Potentials/Inc", "Ghost"], ["Angels/A", "Prospects/Inc"])
        self.assertEqual(resolved, {"angels/a": ["Angels/A"], "Potentials/Inc": ["Prospects/Inc"]})
        self.assertEqual(missing, ["Ghost"])

    def test_destinations_keep_names_and_ids(self):
        photos = [{"originalName": "Brielle.jpg", "photoId": "photo:content-1"},
                  {"originalName": "brielle.jpg", "photoId": "photo:content-2"},
                  {"originalName": "a_image_7.jpg", "photoId": "photo:image_7"}]
        staging = us.assign_destinations(photos, "named", ["A"])
        self.assertEqual([photo["destination"] for photo in photos],
                         ["Various/gallery/Brielle.jpg", "Various/gallery/brielle_u2.jpg",
                          "Various/gallery/a_image_7.jpg"])
        self.assertEqual(staging, ["Various/A/gallery"])
        self.assertEqual(us.assign_destinations(photos[:0], "blank", ["A"]), [])
        with self.assertRaisesRegex(us.UniverseError, "photo ID"):
            us.assign_destinations([{"originalName": "a_image_7.jpg", "photoId": "photo:image_8"}], "blank")

    def test_current_placements_prefer_review_data(self):
        html = ('<script type="application/json" id="review-data">'
                + json.dumps([{"photoId": "photo:image_1", "folder": "Angels/A", "bucket": "Gallery", "score": .7,
                               "closestMatches": [{"folder": "Potentials/B", "score": .5}]}]) + "</script>")
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as temp:
            page = pathlib.Path(temp) / "review.html"
            page.write_text(html, encoding="utf-8")
            records = us.load_review_records(page)
        moves = [{"photoId": "photo:image_1", "destination": "Various/gallery/x_image_1.jpg"},
                 {"photoId": "photo:image_2", "destination": "Potentials/B/review/b_image_2.jpg"}]
        placements = us.current_placements(records, moves)
        self.assertEqual(placements["photo:image_1"]["folder"], "Angels/A")
        self.assertEqual(placements["photo:image_1"]["closest"], [{"folder": "Potentials/B", "score": .5}])
        self.assertEqual(placements["photo:image_2"], {
            "folder": "Potentials/B", "bucket": "Review", "score": None, "closest": [],
            "evidence": "latest-receipt-move"})


class FileTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "tmp" / "universe-sandbox-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temp.cleanup)
        self.base = pathlib.Path(temp.name).resolve()

    def test_copy_verified_refuses_mismatch_and_overwrite(self):
        source = self.base / "a.jpg"
        source.write_bytes(b"original")
        os.utime(source, ns=(1_600_000_000_000_000_000, 1_600_000_000_000_000_000))
        digest = hashlib.sha256(b"original").hexdigest()
        target = self.base / "out" / "a.jpg"
        self.assertEqual(us._copy_verified(source, target, digest), (digest, 8))
        self.assertEqual(target.stat().st_mtime_ns, source.stat().st_mtime_ns)
        with self.assertRaisesRegex(us.UniverseError, "overwrite"):
            us._copy_verified(source, target, digest)
        with self.assertRaisesRegex(us.UniverseError, "differ from the recorded"):
            us._copy_verified(source, self.base / "out" / "b.jpg", "0" * 64)
        with self.assertRaisesRegex(us.UniverseError, "missing"):
            us._copy_verified(self.base / "none.jpg", self.base / "out" / "c.jpg")

    def test_out_root_must_be_a_separate_sandbox_working(self):
        main = self.base / "Sovereign Territories Sandbox"
        production = self.base / "Prod" / "Sovereign Territories"
        good = self.base / "Universes" / "u1" / "Sovereign Territories Sandbox" / "Working"
        with mock.patch.object(us.cw, "production_root", return_value=production):
            self.assertEqual(us.validate_out_root(good, {}, main_sandbox=main), good)
            for bad, message in (
                ("relative/Sovereign Territories Sandbox/Working", "absolute"),
                (self.base / "Universes" / "u1" / "Working", "must end with"),
                (main / "Working" / "Sovereign Territories Sandbox" / "Working", "outside the main Sandbox"),
                (production / "x" / "Sovereign Territories Sandbox" / "Working", "outside Production"),
            ):
                with self.subTest(bad=bad), self.assertRaisesRegex(us.UniverseError, message):
                    us.validate_out_root(bad, {}, main_sandbox=main)

    def test_originals_lookup_verifies_bytes(self):
        output = self.base / "prep" / "inputs" / "_reports" / "preparation" / "selected"
        (output / "retained").mkdir(parents=True)
        good = b"good bytes"
        (output / "retained" / "a.jpg").write_bytes(b"tampered")
        source_root = self.base / "Source"
        (source_root / "Angels" / "A" / "gallery").mkdir(parents=True)
        (source_root / "Angels" / "A" / "gallery" / "a_image_1.jpg").write_bytes(good)
        photo = {"sourceSha256": hashlib.sha256(good).hexdigest(), "preSource": "Angels/A/gallery/a_image_1.jpg"}
        by_hash = {photo["sourceSha256"]: [{"retained": "retained/a.jpg", "source": "Angels/A/gallery/a_image_1.jpg"}]}
        lookup = us.Originals(output, {}, by_hash, [source_root])
        origin, path = lookup.find(photo)
        self.assertEqual(origin, f"source:{source_root}")
        self.assertEqual(path, source_root / "Angels" / "A" / "gallery" / "a_image_1.jpg")
        self.assertEqual(us.Originals(output, {}, by_hash, []).find(photo), (None, None))

    def run_main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = us.main(list(argv))
        return code, out.getvalue()

    def test_empty_mode_copies_source_folder_and_check_rehashes(self):
        source = self.base / "Most Wanted"
        source.mkdir()
        (source / "one_image_1.jpg").write_bytes(b"one")
        (source / "Two.PNG").write_bytes(b"two")
        (source / "notes.txt").write_text("not a photo", encoding="utf-8")
        (source / "nested").mkdir()
        os.utime(source / "one_image_1.jpg", ns=(1_500_000_000_000_000_000, 1_500_000_000_000_000_000))
        before = {path.name: path.read_bytes() for path in source.iterdir() if path.is_file()}
        out_root = self.base / "u" / "Sovereign Territories Sandbox" / "Working"
        common = ("--name", "mw", "--mode", "empty", "--out-root", str(out_root))
        code, text = self.run_main(*common, "--source-folder", str(source))
        self.assertEqual(code, 0, text)
        self.assertIn("images to copy: 2", text)
        self.assertFalse(out_root.parent.exists())
        code, text = self.run_main(*common, "--source-folder", str(source), "--apply")
        self.assertEqual(code, 0, text)
        gallery = out_root / "Various" / "gallery"
        self.assertEqual(sorted(path.name for path in gallery.iterdir()), ["Two.PNG", "one_image_1.jpg"])
        self.assertEqual((gallery / "one_image_1.jpg").stat().st_mtime_ns, 1_500_000_000_000_000_000)
        self.assertEqual({path.name: path.read_bytes() for path in source.iterdir() if path.is_file()}, before)
        manifest = json.loads((out_root / "_reports" / "library" / "universe" / "universe-manifest.json")
                              .read_text("utf-8"))
        self.assertEqual(manifest["mode"], "empty")
        self.assertEqual(manifest["counts"]["photos"], 2)
        self.assertEqual({row["name"] for row in manifest["skipped"]}, {"notes.txt", "nested"})
        self.assertEqual(len(manifest["files"]), 4)
        self.assertTrue((out_root / "README-universe.md").is_file())
        self.assertNotIn("seed --apply", (out_root / "README-universe.md").read_text("utf-8"))
        self.assertFalse((out_root.parent / "Working.universe-staging").exists())

        code, text = self.run_main(*common, "--check")
        self.assertEqual(code, 0, text)
        self.assertIn("working-photo:verified: 2", text)
        self.assertIn("universe-source:verified: 2", text)
        code, text = self.run_main(*common, "--source-folder", str(source), "--apply")
        self.assertEqual(code, 1)
        self.assertIn("refusing to reuse", text)

        (gallery / "Two.PNG").write_bytes(b"edited")
        code, text = self.run_main(*common, "--check")
        self.assertEqual(code, 1, text)
        self.assertIn("working-photo:FAILED: 1", text)
        runs = out_root / "_reports" / "runs"
        runs.mkdir(parents=True)
        (runs / "normal-rebase-x.json").write_text(json.dumps({"status": "applied"}), encoding="utf-8")
        code, text = self.run_main(*common, "--check")
        self.assertEqual(code, 0, text)
        self.assertIn("working-photo:moved-by-applied-rebase: 1", text)
        (out_root.parent / "Universe-Source" / "Various" / "gallery" / "Two.PNG").write_bytes(b"edited")
        code, text = self.run_main(*common, "--check")
        self.assertEqual(code, 1, text)
        self.assertIn("universe-source:FAILED: 1", text)

    def test_source_various_keeps_named_folders_as_named_intake(self):
        source = self.base / "Various"
        (source / "gallery").mkdir(parents=True)
        (source / "gallery" / "u1.jpg").write_bytes(b"u1")
        (source / "Ada Vale").mkdir()
        (source / "Ada Vale" / "a1.jpg").write_bytes(b"a1")
        (source / "Ada Vale" / "gallery").mkdir()
        (source / "Ada Vale" / "gallery" / "a2.png").write_bytes(b"a2")
        (source / "Ada Vale" / "deep").mkdir()
        (source / "_hold").mkdir()
        (source / "loose.jpg").write_bytes(b"loose")
        out_root = self.base / "w" / "Sovereign Territories Sandbox" / "Working"
        common = ("--name", "mw", "--mode", "empty", "--out-root", str(out_root), "--source-various", str(source))
        code, text = self.run_main(*common, "--apply")
        self.assertEqual(code, 0, text)
        self.assertIn("Various/Ada Vale/gallery: 2", text)
        self.assertTrue((out_root / "Various" / "gallery" / "u1.jpg").is_file())
        self.assertEqual(sorted(path.name for path in (out_root / "Various" / "Ada Vale" / "gallery").iterdir()),
                         ["a1.jpg", "a2.png"])
        manifest = json.loads((out_root / "_reports" / "library" / "universe" / "universe-manifest.json")
                              .read_text("utf-8"))
        self.assertEqual(manifest["foldersCopied"], {"Various/Ada Vale/gallery": 2, "Various/gallery": 1})
        self.assertEqual({row["name"] for row in manifest["skipped"]}, {"Ada Vale/deep", "_hold", "loose.jpg"})
        self.assertIn("seed --apply", (out_root / "README-universe.md").read_text("utf-8"))
        code, text = self.run_main("--name", "mw", "--mode", "empty", "--out-root", str(out_root), "--check")
        self.assertEqual(code, 0, text)
        self.assertIn("working-photo:verified: 3", text)

        (source / "Ada Vale" / "gallery" / "a1.jpg").write_bytes(b"clash")
        code, text = self.run_main("--name", "mw2", "--mode", "empty", "--source-various", str(source),
                                   "--out-root", str(self.base / "x" / "Sovereign Territories Sandbox" / "Working"))
        self.assertEqual(code, 1)
        self.assertIn("same file name at both levels", text)

    def test_workflow_selected_arrival_is_reported_not_changed(self):
        folder = self.base / "drop"
        folder.mkdir()
        (folder / "facebook_111_7513773530805044436.jpg").write_bytes(b"selected photo")
        (folder / "angelica_image_7513773530805044436.jpg").write_bytes(b"already id-bearing")
        (folder / "facebook_222_42.jpg").write_bytes(b"other")
        cfg = {"photos": {"hero": "angelica_image_7513773530805044436_944x1104.png"},
               "flows": {"f": {"photos": {"x": 7}}}}
        found = us.workflow_selected_arrivals(sorted(folder.iterdir()), cfg)
        self.assertEqual(found, [{"name": "facebook_111_7513773530805044436.jpg",
                                  "photoId": "photo:image_7513773530805044436",
                                  "workflowPhoto": "angelica_image_7513773530805044436_944x1104.png"}])
        self.assertEqual(us.workflow_selected_arrivals(sorted(folder.iterdir()), {}), [])

    def test_cli_argument_guards(self):
        out_root = str(self.base / "v" / "Sovereign Territories Sandbox" / "Working")
        for argv, message in (
            (("--name", "x", "--out-root", out_root), "--seed is required"),
            (("--name", "x", "--mode", "empty", "--seed", "A", "--out-root", out_root), "no --seed"),
            (("--name", "x", "--seed", "A", "--source-folder", str(self.base), "--out-root", out_root),
             "requires --mode empty"),
            (("--name", "x", "--seed", "A", "--source-various", str(self.base), "--out-root", out_root),
             "requires --mode empty"),
            (("--name", "x", "--mode", "empty", "--source-folder", str(self.base), "--source-various",
              str(self.base), "--out-root", out_root), "either"),
            (("--name", "bad name", "--mode", "empty"), "--name must be"),
        ):
            with self.subTest(argv=argv), self.assertRaises(SystemExit):
                self.run_main(*argv)
        code, text = self.run_main("--name", "x", "--mode", "empty", "--out-root", out_root,
                                   "--source-folder", str(self.base / "missing"))
        self.assertEqual(code, 1)
        self.assertIn("not a plain folder", text)

    def test_membership_report_escapes_and_embeds_thumbnails(self):
        selection = {"photos": [{"photoId": "photo:image_1", "preSource": "A/<b>.jpg", "originalOwner": "Angels/<A>",
                                 "currentFolder": "Angels/A", "currentBucket": "Gallery", "seedScore": .5, "hop": 0}],
                     "centering": "fixture", "band": "yellow", "bandMinimum": .3, "hop2Band": "green",
                     "hop2Minimum": .55, "notFound": ["Ghost"], "identities": [], "interestingNotIncluded": [],
                     "boundedOut": [], "excluded": []}
        manifest = {"name": "u", "mode": "blank", "selection": selection, "counts": {"photos": 1},
                    "parameters": {"seeds": ["A"]}}
        page = us.membership_html(manifest, {"photo:image_1": "data:image/jpeg;base64,AAAA"})
        self.assertIn("Angels/&lt;A&gt; (1)", page)
        self.assertIn("Angels/A / Gallery (1)", page)
        self.assertIn("data:image/jpeg;base64,AAAA", page)
        self.assertIn("Ghost", page)
        self.assertNotIn("<b>.jpg", page)


if __name__ == "__main__":
    unittest.main()
