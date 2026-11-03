#!/usr/bin/env python3
"""Tests for the read-only sandbox rebase recap page."""
import json
import pathlib
import tempfile
import unittest

from tools.art.likeness_library import rebase_recap


def _plan(working):
    return {
        "status": "applied", "workingRoot": str(working), "createdAt": "2026-11-02T21:00:00",
        "policy": {"version": "test"}, "castSeedPolicy": "all", "referenceFolders": ["Angels/Ava", "Prospects/Old"],
        "photos": [
            {"source": "Angels/Ava/gallery/ava_a.jpg", "destination": "Angels/Ava/gallery/ava_a.jpg",
             "oldFolder": "Angels/Ava", "photoId": "photo:a", "reason": "Cast membership retained",
             "retainedCast": True, "preparationSource": "Angels/Ava/gallery/ava_a.jpg"},
            {"source": "Prospects/Old/gallery/old_b.jpg", "destination": "Angels/Ava/review/ava_b.png",
             "oldFolder": "Prospects/Old", "sourceFolder": "Various", "photoId": "photo:b",
             "reason": "high cast similarity may indicate a same-person match", "score": 0.61,
             "initialBestCast": "Angels/Ava", "initialBestCastScore": 0.58},
            {"source": "Various/gallery/c.jpg", "destination": "Models/Nia Vale/gallery/nia_vale_c.png",
             "oldFolder": "Various", "photoId": "photo:c", "reason": "new coherent 2-photo identity",
             "score": 0.42, "initialBestCast": "Angels/Ava", "initialBestCastScore": 0.31},
            {"source": "Various/gallery/d.jpg", "destination": "Various/review/d.png",
             "oldFolder": "Various", "photoId": None, "reason": "missing stable photo ID; held in Review"},
        ],
    }


class RebaseRecapTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.working = pathlib.Path(self.directory.name) / "Working"
        self.run = self.working / "_sandbox-state" / "run1"
        self.run.mkdir(parents=True)
        (self.run / "run.json").write_text(json.dumps(_plan(self.working)), encoding="utf-8")
        preparation = self.run / "inputs" / "_reports" / "preparation" / "all"
        preparation.mkdir(parents=True)
        (preparation / "manifest.json").write_text(json.dumps({"photos": [
            {"source": "Angels/Ava/gallery/ava_a.jpg", "detail": "photos/abc.html",
             "variants": {"control": {"path": "candidates/a/control.png", "thumbnail": "candidates/a/control-preview.jpg"}}},
        ]}), encoding="utf-8")

    def test_collect_classifies_moves_renames_review_and_identity_changes(self):
        data = rebase_recap.collect(self.run)
        kinds = {row["source"]: row["kind"] for row in data["rows"]}
        self.assertEqual(kinds, {
            "Angels/Ava/gallery/ava_a.jpg": "stayed",
            "Prospects/Old/gallery/old_b.jpg": "moved-to-review",
            "Various/gallery/c.jpg": "moved",
            "Various/gallery/d.jpg": "to-review",
        })
        self.assertEqual(data["newIdentities"], ["Models/Nia Vale"])
        self.assertEqual(data["emptiedIdentities"], ["Prospects/Old"])
        summary = rebase_recap.summarize(data)
        self.assertEqual((summary["renamed"], summary["converted"], summary["review"]), (2, 3, 2))
        first = data["rows"][0]
        self.assertTrue(first["preview"].endswith("control-preview.jpg"))
        self.assertTrue(first["detail"].endswith("abc.html"))

    def test_page_lists_cast_gains_identities_review_and_relative_links(self):
        out = self.working / "_reports" / "library" / "rebase-recap" / "run1.html"
        self.assertEqual(rebase_recap.main([str(self.run)]), 0)
        page = out.read_text(encoding="utf-8")
        self.assertIn("Angels/Ava", page)
        self.assertIn("Prospects/Old (first intake Various)", page)
        self.assertIn("Models/Nia Vale", page)
        self.assertIn("missing stable photo ID: 1", page)
        self.assertIn('href="../../../Angels/Ava/gallery/ava_a.jpg"', page)
        self.assertIn('data-identity="Models/Nia Vale"', page)
        self.assertNotIn("file:///", page)
        self.assertIn("run1.html", (out.parent / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(rebase_recap.main([str(self.run), "--check"]), 0)

    def test_expectations_beside_working_are_scored_and_stale_pages_fail_check(self):
        expectations = self.working.parent / "rebase-expectations.json"
        expectations.write_text(json.dumps({
            "identities": {"Models/Nia Vale": "Angels/Ava"},
            "photos": {"old_b": "Angels/Ava", "c.jpg": "Models/Nia Vale", "ghost": "Angels/Ava"},
        }), encoding="utf-8")
        data = rebase_recap.collect(self.run)
        data["expectations"] = rebase_recap.load_expectations(rebase_recap.expectations_path(data))
        states = sorted((item["key"], item["state"]) for item in rebase_recap.expectation_results(data))
        self.assertEqual(states, [("Models/Nia Vale", "identity-not-merged"), ("c.jpg", "placed"),
                                  ("ghost", "missing"), ("old_b", "in-review")])
        self.assertEqual(rebase_recap.main([str(self.run)]), 0)
        page = (self.working / "_reports" / "library" / "rebase-recap" / "run1.html").read_text(encoding="utf-8")
        self.assertIn('<option value="Angels/Ava" selected>', page)
        later = expectations.stat().st_mtime + 5
        import os
        os.utime(expectations, (later, later))
        self.assertEqual(rebase_recap.main([str(self.run), "--check"]), 1)

    def test_other_runs_of_the_same_inputs_are_compared(self):
        other = self.run.parent / "run2-core"
        other.mkdir()
        plan = _plan(self.working)
        plan["status"], plan["castSeedPolicy"] = "preview", "core"
        plan["photos"][0]["destination"] = "Prospects/Ava Two/gallery/ava_two_a.jpg"
        (other / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        differences = rebase_recap.compare_runs(rebase_recap.collect(self.run), rebase_recap.collect(other))
        self.assertEqual([(a["newPerson"], b["newPerson"]) for a, b in differences],
                         [("Angels/Ava", "Prospects/Ava Two")])
        self.assertEqual(rebase_recap.main([str(self.run)]), 0)
        page = (self.working / "_reports" / "library" / "rebase-recap" / "run1.html").read_text(encoding="utf-8")
        self.assertIn("run2-core (preview, cast seeds core): 1 photos placed differently", page)

    def test_dry_run_and_check_write_nothing(self):
        out = self.working / "_reports" / "library" / "rebase-recap" / "run1.html"
        self.assertEqual(rebase_recap.main([str(self.run), "--dry-run"]), 0)
        self.assertEqual(rebase_recap.main([str(self.run), "--check"]), 1)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
