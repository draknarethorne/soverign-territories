#!/usr/bin/env python3
"""Tests for the read-only sandbox rebase recap page."""
import json
import pathlib
import subprocess
import sys
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

    def test_direct_script_entry_point_supports_launcher(self):
        result = subprocess.run(
            [sys.executable, str(pathlib.Path(rebase_recap.__file__).resolve()), "--help"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--dry-run", result.stdout)

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
        self.assertIn(".site-masthead", page)
        self.assertIn('aria-label="Filter to an Angel or Sister"', page)
        self.assertIn('target="_blank" rel="noopener noreferrer"', page)
        self.assertIn("unavailable (not recorded)", page)
        self.assertIn("Final photo", page)
        self.assertIn("Review page", page)
        self.assertIn("count conservation", page.lower())
        self.assertNotIn("file:///", page)
        self.assertIn("run1.html", (out.parent / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(rebase_recap.main([str(self.run), "--check"]), 0)
        data = rebase_recap.collect(self.run)
        unsafe = dict(data["rows"][1], destination="../../outside.jpg")
        self.assertIn("unsafe destination link unavailable",
                      rebase_recap._destination_links(unsafe, data, out.parent))

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

    def test_saved_evidence_audit_links_escaping_and_deterministic_render(self):
        plan = _plan(self.working)
        plan["photos"][1]["topCastReferences"] = [
            {"folder": "Angels/Ava", "score": 0.58},
            {"folder": "Sisters/Bea", "score": 0.41},
            {"folder": "Angels/Cara", "score": 0.33},
        ]
        plan["photos"][1]["clusterId"] = "cluster-1"
        plan["photos"][2]["clusterId"] = "cluster-1"
        plan["finalMembershipAudit"] = {
            "status": "checked",
            "summary": {"passed": False, "higherRivals": 1},
            "rows": [{
                "source": "Prospects/Old/gallery/old_b.jpg",
                "destination": "Angels/Ava/review/ava_b.png",
                "ownScore": 0.61,
                "rivals": [{"folder": 'Models/<Nia & Co>', "score": 0.72}],
                "higherRival": True,
                "reason": "</td><script>alert(1)</script>",
            }],
        }
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        data = rebase_recap.collect(self.run)
        self.assertEqual(data["rows"][1]["groupSize"], 2)
        self.assertEqual(len(data["rows"][1]["topCast"]), 3)
        self.assertTrue(rebase_recap.summarize(data)["countConserved"])
        first = rebase_recap.render(data, self.working / "report.html")
        second = rebase_recap.render(data, self.working / "report.html")
        self.assertEqual(first, second)
        self.assertIn("higherRivals: 1", first)
        self.assertIn("Models/&lt;Nia &amp; Co&gt;", first)
        self.assertIn("Audit state: <b>failed</b>", first)
        self.assertIn("&lt;/td&gt;&lt;script&gt;alert(1)&lt;/script&gt;", first)
        self.assertNotIn("</td><script>alert(1)</script>", first)
        self.assertIn("Prospects/Old/gallery/old_b.jpg", first)
        self.assertIn("Angels/Ava/review/ava_b.png", first)
        self.assertIn("Top three per-photo cast references", first)

    def test_actual_audit_contract_and_ordered_core_references(self):
        plan = _plan(self.working)
        plan["coreReferences"] = {"Angels/Ava": [
            {"source": "Angels/Ava/gallery/ava_a.jpg",
             "destination": "Angels/Ava/gallery/ava_a.jpg", "photoId": "photo:a", "score": None},
            {"source": "Angels/Ava/gallery/extra.jpg",
             "destination": "Angels/Ava/gallery/extra.png", "photoId": "photo:extra", "score": 0.81},
        ]}
        plan["finalMembershipAudit"] = {
            "reference": "final frozen core <snapshot>", "pass": 1, "state": "audited",
            "higherRivalCount": 1, "followupCandidateCount": 1, "nextPassNeeded": True,
            "automaticMoves": 0, "automaticPhotoProtectionCount": 2, "automaticIdentityProtectionCount": 1,
            "protectionEvidence": [{"photoId": "photo:a", "protected": True}],
            "diagnostics": ["recomparison pending"],
            "rows": [{
                "source": "Prospects/Old/gallery/old_b.jpg", "destination": "Angels/Ava/review/ava_b.png",
                "ownScore": None, "rivals": [{"folder": "Sisters/Bea", "score": 0.7}],
                "higherRival": True, "reason": "rival requires follow-up", "protected": False,
                "anchor": True, "workflowSelected": False, "followupCandidate": True,
                "castReferences": [{"folder": "Angels/Ava", "score": None},
                                   {"folder": "Sisters/Bea", "score": 0.73}],
                "coreMember": True, "automaticProtection": False, "manualOptOut": True,
                "rivalMargin": -0.03, "independentProtectionSupport": 2,
                "protectionReason": "manual <opt-out>",
            }],
        }
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        data = rebase_recap.collect(self.run)
        references = rebase_recap._core_reference_rows(data, "Angels/Ava")
        self.assertEqual([row["photoId"] for row in references], ["photo:a", "photo:extra"])
        self.assertIsNone(references[0]["castSeedScore"])
        page = rebase_recap.render(data, self.working / "report.html")
        self.assertIn("Audit state: <b>audited</b>", page)
        self.assertNotIn("Audit state: <b>passed</b>", page)
        self.assertIn("pass: 1", page)
        self.assertIn("reference: final frozen core &lt;snapshot&gt;", page)
        self.assertIn("Audit-only: no convergence or extra moves were performed.", page)
        for field in ("higherRivalCount", "followupCandidateCount", "nextPassNeeded", "automaticMoves",
                      "automaticPhotoProtectionCount", "automaticIdentityProtectionCount",
                      "protectionEvidence", "diagnostics", "protected", "anchor", "workflowSelected",
                      "followupCandidate"):
            self.assertIn(field, page)
        self.assertIn('href="Angels/Ava/gallery/extra.png" target="_blank"', page)
        self.assertIn("Eligible core reference; score unavailable (not recorded)", page)
        self.assertIn("Eligible core reference; score 0.810", page)
        self.assertIn(f'data-cast-filter="{rebase_recap._anchor("cast", "Angels/Ava")}"', page)
        for field in ("coreMember", "automaticProtection", "manualOptOut", "rivalMargin",
                      "independentProtectionSupport", "protectionReason"):
            self.assertIn(field, page)
        self.assertIn("protectionReason: manual &lt;opt-out&gt;", page)
        self.assertIn("predates in-place refinement", page)
        plan["membershipRefinement"] = {
            "schemaVersion": 1, "maxPasses": 4, "passCount": 2, "stopReason": "stable",
            "moveCount": 1, "mergeCount": 1, "dissolvedCount": 0,
            "passes": [{
                "pass": 1,
                "moves": [{"photoId": "photo:m", "kind": "photo-move", "from": "Models/Ann Lee",
                           "to": "Models/Bea <Kay>", "ownScore": 0.2, "rivalScore": 0.7, "lead": 0.5}],
                "merges": [{"kind": "identity-merge", "survivor": "Models/Bea <Kay>",
                            "loser": "Potentials/Cy Dee", "similarity": 0.81, "lead": 0.3, "photoCount": 2}],
                "dissolved": [], "reclassified": [],
            }, {"pass": 2, "moves": [], "merges": [], "dissolved": [], "reclassified": []}],
            "unresolved": [{"pass": 1, "photoId": "photo:z", "kind": "locked", "detail": "anchored"}],
        }
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        page = rebase_recap.render(rebase_recap.collect(self.run), self.working / "report.html")
        self.assertIn("id=refinement", page)
        self.assertIn("stop reason <b>stable</b>", page)
        self.assertIn("Models/Bea &lt;Kay&gt;", page)
        self.assertIn("<td>identity-merge</td><td>2 photo(s)</td><td>Potentials/Cy Dee</td>", page)
        self.assertIn("<td>locked</td><td>photo:z</td><td>anchored</td>", page)
        table = page.split("<table id=photos>", 1)[1]
        self.assertIn("<b>FINAL photo-to-cast references</b>", table)
        self.assertIn("0.730", table)
        self.assertIn("FINAL references unavailable in this run.", table)
        self.assertIn("singleton own scores unavailable", page)

    def test_preserved_reset_history_compared_and_regenerated_repeatably(self):
        historical = self.working / "_reports" / "reset-review-bundle" / "rebase-runs" / "prior"
        historical.mkdir(parents=True)
        prior = _plan(self.working)
        prior["sourceManifestSHA256"] = "same-sources"
        prior["photos"][2]["destination"] = "Prospects/Nia/gallery/nia_c.jpg"
        prior["createdAt"] = "2026-11-01T10:00:00"
        payload = json.dumps(prior).encode("utf-8")
        (historical / "run.json").write_bytes(payload)
        current = _plan(self.working)
        current["sourceManifestSHA256"] = "same-sources"
        (self.run / "run.json").write_text(json.dumps(current), encoding="utf-8")
        self.assertIn(historical, rebase_recap.sibling_runs(self.run, self.working))
        preserved = rebase_recap.collect(historical)
        self.assertTrue(preserved["historical"])
        self.assertIsNone(preserved["preparationIndex"])
        self.assertEqual(len(rebase_recap.compare_runs(rebase_recap.collect(self.run), preserved)), 1)
        self.assertEqual(rebase_recap.main([str(self.run)]), 0)
        out = rebase_recap.default_out(rebase_recap.collect(self.run))
        history_page = out.parent / rebase_recap._run_page_name(preserved)
        content = history_page.read_text(encoding="utf-8")
        current_content = out.read_text(encoding="utf-8")
        index_content = (out.parent / "index.html").read_text(encoding="utf-8")
        self.assertIn("prior (applied, cast seeds all): 1 photos placed differently", current_content)
        self.assertIn("Historical reset evidence.", content)
        self.assertIn("Historical image unavailable", content)
        self.assertIn("Historical destination only", content)
        self.assertNotIn("<img ", content)
        self.assertNotIn('href="../../../Prospects/Nia/gallery/nia_c.jpg"', content)
        self.assertIn("prior (historical; images unavailable)", index_content)
        self.assertEqual(rebase_recap.main([str(self.run)]), 0)
        self.assertEqual(content, history_page.read_text(encoding="utf-8"))
        self.assertEqual(current_content, out.read_text(encoding="utf-8"))
        self.assertEqual(index_content, (out.parent / "index.html").read_text(encoding="utf-8"))
        self.assertEqual((historical / "run.json").read_bytes(), payload)

    def test_shared_source_manifest_does_not_hide_working_overlay_changes(self):
        other_run = self.run.parent / "prior-overlay"
        other_run.mkdir()
        previous = _plan(self.working)
        current = _plan(self.working)
        for plan in (previous, current):
            plan["sourceManifestSHA256"] = "unchanged-source"
            for index, row in enumerate(plan["photos"]):
                row["sha256"] = f"hash-{index}"
        previous["photos"][1]["sha256"] = "prior-bytes"
        previous["photos"][2]["source"] = "Production/gallery/c.jpg"
        previous["photos"][3]["source"] = "Various/gallery/removed.jpg"
        previous["photos"][3]["photoId"] = "photo:removed"
        current["photos"][3]["photoId"] = "photo:added"
        (other_run / "run.json").write_text(json.dumps(previous), encoding="utf-8")
        (self.run / "run.json").write_text(json.dumps(current), encoding="utf-8")
        data, other = rebase_recap.collect(self.run), rebase_recap.collect(other_run)
        self.assertFalse(rebase_recap._same_inputs(data, other))
        self.assertTrue(rebase_recap._same_inputs(data, rebase_recap.collect(self.run)))
        pairs, added, removed = rebase_recap._comparison_rows(data, other)
        self.assertEqual((len(pairs), len(added), len(removed)), (3, 1, 1))
        page = rebase_recap.render(data, self.working / "report.html", [other])
        self.assertIn("Partial source/photo-ID comparison", page)
        self.assertNotIn("Identical inputs verified", page)
        self.assertIn("1 added in this run; 1 removed from this run; 2 paired source/byte signatures changed", page)
        self.assertIn("prior-bytes", page)
        self.assertIn("Production/gallery/c.jpg", page)
        self.assertIn("Various/gallery/removed.jpg", page)
        self.assertIn("Various/gallery/d.jpg", page)
        self.assertEqual(rebase_recap.main([str(self.run)]), 0)
        self.assertIn("Partial source/photo-ID comparison",
                      rebase_recap.default_out(data).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
