#!/usr/bin/env python3
"""Tests for the read-only sandbox rebase recap page."""
import json
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser

from tools.art.likeness_library import rebase_recap


def _plan(working):
    return {
        "status": "applied", "workingRoot": str(working), "createdAt": "2026-11-02T21:00:00",
        "policy": {"version": "test"}, "castSeedPolicy": "all", "referenceFolders": ["Angels/Ava", "Prospects/Old"],
        "photos": [
            {"source": "Angels/Ava/gallery/ava_a.jpg", "destination": "Angels/Ava/gallery/ava_a.jpg",
             "oldFolder": "Angels/Ava", "photoId": "photo:a", "reason": "Cast membership retained",
             "sha256": hashlib.sha256(b"source-a").hexdigest(),
             "preparedSHA256": hashlib.sha256(b"source-a").hexdigest(),
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
        source = self.working / "Angels" / "Ava" / "gallery" / "ava_a.jpg"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"source-a")

    def test_family_coverage_and_provisional_authority_are_not_reported_as_confirmed_identity(self):
        data = {"familyNaming": {
            "families": [], "ownerAssessment": [{
                "personId": "owner", "folder": "Potentials/Una Vale", "identityStatus": "provisional",
                "qualifiedReferenceCount": 0, "status": "provisional-no-reference-authority",
            }],
        }}
        page = rebase_recap._family_section(data)
        self.assertIn("All-category owner assessment", page)
        self.assertIn("Potentials/Una Vale", page)
        self.assertIn("provisional-no-reference-authority", page)
        self.assertIn("not certified identities", page)
        data["groupLifecycle"] = {
            "assignmentSummary": {"supported": 1, "provisional": 6, "activeVarious": 0, "junk": 0,
                                  "confirmedIndependentIdentities": 0, "provisionalContainers": 1},
            "stages": [{"id": "publication", "rows": [{
                "destination": "Potentials/Una Vale/gallery/u.jpg",
                "status": "tentative", "actionCategory": "provisional",
            }]}],
        }
        page = rebase_recap._lifecycle_placement_summary(data)
        self.assertIn("6 provisional", page)
        self.assertIn("0 activeVarious", page)
        self.assertIn("0 confirmedIndependentIdentities", page)
        self.assertIn("not certified distinct identities", page)

    def test_final_projection_is_not_presented_as_an_intermediate_snapshot(self):
        plan = _plan(self.working)
        plan["status"] = "preview"
        plan["groupLifecycle"] = {
            "recipe": "directed-core-continuity", "evaluation": {},
            "stages": [{
                "id": "references", "title": "References", "evidenceKind": "final-projection",
                "rows": [{
                    **plan["photos"][0], "sourceReferenceHold": True,
                    "referenceUseDisposition": "withdrawn-or-unqualified-independent-of-placement",
                    "referenceWithdrawalReason": "independent validation failed",
                    "admissionReason": "insufficient-independent-member-support",
                }],
            }],
        }
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        out = self.working / "report.html"
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out)]), 0)
        page = next((self.run / "group-lifecycle").glob("*.html")).read_text(encoding="utf-8")
        self.assertIn("Final projection only: no intermediate state was saved", page)
        self.assertIn("Source has no qualified reference view: True", page)
        self.assertIn("independent validation failed", page)
        self.assertIn("insufficient-independent-member-support", page)
        self.assertIn("final-projection", page)

    def test_packed_boundary_pages_match_full_rows_without_changing_snapshot_meaning(self):
        from tools.art.likeness_library.directed_reformation import pack_lifecycle_stages
        plan = _plan(self.working)
        plan["status"] = "preview"
        plan["groupLifecycle"] = {"recipe": "directed", "evaluation": {}, "stages": [{
            "id": "publication", "title": "Final", "evidenceKind": "proposal-snapshot",
            "rows": [{**plan["photos"][0], "status": "supported", "coreUse": True,
                      "personId": "person:one", "reason": "independent admission passed",
                      "independentCandidateFolder": "Potentials/Nova Candidate",
                      "independentCandidateDisposition": "independent-reference-insufficient"}],
            "referenceInventory": {"view-one": ["photo:a"]},
        }]}
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        out = self.working / "report.html"
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out)]), 0)
        page = next((self.run / "group-lifecycle").glob("*.html"))
        original = page.read_bytes()
        self.assertIn(b"Potentials/Nova Candidate", original)
        self.assertIn(b"independent-reference-insufficient", original)
        pack_lifecycle_stages(plan["groupLifecycle"])
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out)]), 0)
        self.assertEqual(page.read_bytes(), original)
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out), "--check"]), 0)

    def test_group_lifecycle_pages_are_bounded_verified_and_checked(self):
        plan = _plan(self.working)
        plan["status"] = "preview"
        overlay = self.run / "source-overlay"
        source = overlay / "Angels" / "Ava" / "gallery" / "ava_a.jpg"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"source-a")
        payload = json.dumps({"currentVarious": [], "inputs": {}}).encode()
        (overlay / "overlay.json").write_bytes(payload)
        plan["sourceOverlaySHA256"] = hashlib.sha256(payload).hexdigest()
        row = {"photoId": "photo:a", "source": "Angels/Ava/gallery/ava_a.jpg",
               "destination": "Angels/Ava/gallery/ava_a.jpg", "personId": "person:1",
               "groupId": "group_1", "status": "tentative", "coreUse": False,
               "reason": "<unsafe>", "score": 0.7, "rivalScore": 0.6, "margin": 0.1}
        plan["groupLifecycle"] = {"recipe": "test", "evaluation": {"kept": 101},
                                  "stages": [{"id": "test", "title": "Stage", "at": "then",
                                              "rows": [row] * 101, "summary": {"count": 101}}]}
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        out = self.working / "report.html"
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out)]), 0)
        pages = sorted((self.run / "group-lifecycle").glob("*.html"))
        self.assertEqual(len(pages), 2)
        first = pages[0].read_text(encoding="utf-8")
        self.assertEqual(first.count("<article>"), 100)
        self.assertIn("nothing installed", first)
        self.assertIn("ava_a.jpg", first)
        self.assertIn("&lt;unsafe&gt;", first)
        self.assertNotIn("<unsafe>", first)
        self.assertIn("Image load error", first)
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out), "--check"]), 0)
        before = [page.read_bytes() for page in pages]
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out)]), 0)
        self.assertEqual(before, [page.read_bytes() for page in pages])
        plan["status"] = "applied"
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out)]), 0)
        applied = pages[0].read_text(encoding="utf-8")
        self.assertIn("Installed destination", applied)
        self.assertIn("current applied files", applied)
        self.assertIn("source-overlay", applied)
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out), "--check"]), 0)
        source.write_bytes(b"changed")
        self.assertEqual(rebase_recap.main([str(self.run), "--out", str(out), "--check"]), 1)

    def test_group_stage_summarizes_large_evidence_and_explains_population_scope(self):
        data = rebase_recap.collect(self.run)
        row = {"photoId": "photo:a", "source": "Angels/Ava/gallery/ava_a.jpg",
               "destination": "Angels/Ava/gallery/ava_a.jpg", "reason": "reason"}
        evidence = [{"secret": "LARGE-EVIDENCE-MARKER" * 100}] * 10000
        data["groupLifecycle"] = {
            "recipe": "test", "evaluation": {
                "photoCount": 3290, "supported": 2000, "referenceVersion": "<version>",
                "stagedDependencies": evidence, "referenceQualificationBoundaries": evidence,
                "withdrawalBoundaries": evidence,
            },
            "stages": [
                {"id": "withdrawal", "title": "Withdrawal", "at": "then", "rows": [row],
                 "scope": "withdrawn references", "populationCount": 3290, "summary": {"withdrawn": 1}},
                {"id": "all", "title": "All inputs", "at": "later", "rows": [row] * 101,
                 "scope": "all inputs", "populationCount": 101, "summary": {"supported": 101}},
            ],
        }
        rendered = rebase_recap._stage_pages(data)
        self.assertEqual(len(rendered), 3)
        withdrawal, full, last = rendered.values()
        self.assertLess(max(len(page) for page in rendered.values()), 150000)
        self.assertNotIn("LARGE-EVIDENCE-MARKER", withdrawal)
        self.assertIn("stagedDependencies: 10000 entries", withdrawal)
        self.assertIn("referenceQualificationBoundaries: 10000 entries", withdrawal)
        self.assertIn("withdrawalBoundaries: 10000 entries", withdrawal)
        self.assertIn("photoCount: 3290", withdrawal)
        self.assertIn("&lt;version&gt;", withdrawal)
        self.assertIn("Scope: withdrawn references · snapshot rows: 1 · input population: 3290", withdrawal)
        self.assertIn("Scope: all inputs · snapshot rows: 101 · input population: 101", full)
        self.assertIn("Full saved run evidence", withdrawal)
        self.assertIn("run.json", withdrawal)
        self.assertIn('aria-label="Lifecycle stages"', withdrawal)
        self.assertIn('aria-label="Stage pages"', last)
        self.assertIn("minmax(min(100%,230px),1fr)", full)
        self.assertEqual(full.count("<article>"), 100)
        self.assertEqual(last.count("<article>"), 1)

    def test_directed_stage_and_recap_keep_decision_classes_distinct(self):
        data = rebase_recap.collect(self.run)
        rows = [
            {"photoId": f"photo:{index}", "source": f"Angels/Ava/gallery/{index}.jpg",
             "sourceDestination": f"Angels/Ava/gallery/{index}.jpg",
             "destination": f"{destination}/gallery/{index}.jpg",
             "proposedDestination": f"{destination}/gallery/{index}.jpg",
             "actionCategory": action, "status": "supported", "coreUse": False,
             "personId": "person:1", "groupId": None, "reason": action}
            for index, (action, destination) in enumerate((
                ("same-home", "Angels/Ava"), ("upward", "Sisters/Parent"),
                ("same-rank", "Angels/Other"), ("correction", "Models/Corrected"),
                ("hold", "Angels/Ava"),
            ))
        ]
        data["groupLifecycle"] = {
            "evaluation": {
                "sameHomeAssignments": 1, "upwardAssignments": 1, "sameRankAssignments": 1,
                "correctionAssignments": 1, "heldAssignments": 1,
            },
            "stages": [{"id": "publication", "title": "Publication", "rows": rows}],
        }
        summary = rebase_recap._lifecycle_placement_summary(data)
        self.assertIn("Directed decisions: 1 same-home · 1 upward · 1 same-rank · 1 correction · 1 hold", summary)
        stage = next(iter(rebase_recap._stage_pages(data).values()))
        for action in ("same-home", "upward", "same-rank", "correction", "hold"):
            self.assertIn(f"Directed decision: {action}", stage)
        self.assertIn("Inherited home", stage)
        self.assertIn("Directed proposal", stage)

    def test_family_reconciliation_and_placement_keep_history_and_status_distinct(self):
        data = rebase_recap.collect(self.run)
        data["familyNaming"] = {
            "families": [], "linkBand": "test", "linkMinimum": 0.3,
            "previousCatalogueFamilies": {"person_a": {"surname": "Old"}},
            "catalogueReconciliation": [
                {"personId": "person_a", "previousFamily": {"surname": "Old"},
                 "currentFamily": {"surname": "<New>"}, "decision": "refreshed", "reason": "recomputed"},
                {"personId": "person_b", "previousFamily": {"surname": "Former", "previousPersonName": "Prior Name"},
                 "currentFamily": None, "decision": "retired", "reason": "<retired>"},
            ],
        }
        data["groupLifecycle"] = {"stages": [{"id": "publication", "rows": [
            {"personId": "person_a", "destination": "Models/Current/gallery/a.jpg", "status": "supported"},
            {"destination": "Models/Other/gallery/b.jpg", "status": "tentative"},
            {"destination": "Models/Other/gallery/c.jpg", "status": "quality-hold"},
            {"destination": "Various/review/d.jpg", "status": "unresolved"},
        ]}]}
        out = self.working / "report.html"
        page = rebase_recap.render(data, out)
        self.assertIn("Prior creative family records reconciled: 2 (1 refreshed, 1 retired)", page)
        self.assertIn("Models/Current<br>person_a", page)
        self.assertIn("Prior Name<br>person_b", page)
        self.assertIn("&lt;New&gt;", page)
        self.assertIn("&lt;retired&gt;", page)
        self.assertNotIn("<retired>", page)
        self.assertIn("none (retired or not recorded)", page)
        self.assertIn("not claims of biological kinship", page)
        self.assertIn("saved run evidence", page)
        self.assertIn("Gallery: 1 quality-hold, 1 supported, 1 tentative", page)
        self.assertIn("Review: 1 unresolved", page)
        self.assertIn("Physical Gallery placement is distinct", page)
        self.assertIn("do not guarantee", page)

    def test_direct_script_entry_point_supports_launcher(self):
        result = subprocess.run(
            [sys.executable, str(pathlib.Path(rebase_recap.__file__).resolve()), "--help"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--dry-run", result.stdout)

    def test_review_explains_saved_multiface_labels_are_detector_observations(self):
        data = rebase_recap.collect(self.run)
        row = next(row for row in data["rows"] if row["newBucket"] == "review")
        original = "quality hold: 2+ faces: someone else is in the picture; excluded from matching"
        out = self.working / "_reports" / "library" / "rebase-recap" / "run1.html"
        self.assertNotIn("Detector observations are not confirmed people counts", rebase_recap.render(data, out))
        row["reason"] = original
        page = rebase_recap.render(data, out)
        self.assertIn(original, page)
        self.assertEqual(page.count("Detector observations are not confirmed people counts"), 2)
        self.assertEqual(row["reason"], original)

    def test_preview_review_destination_links_to_exact_expanded_photo(self):
        data = rebase_recap.collect(self.run)
        data["status"] = "preview"
        out = self.working / "_reports" / "library" / "rebase-recap" / "preview.html"
        row = next(row for row in data["rows"] if row["newBucket"] == "review")
        anchor = rebase_recap._anchor("review-photo", row["source"])
        page = rebase_recap.render(data, out)
        self.assertIn(f'href="#{anchor}" target="_blank" rel="noopener noreferrer"', page)
        self.assertEqual(page.count(f'id="{anchor}"'), 1)
        self.assertRegex(page, rf'<details data-review-group><summary>[^<]+</summary><div class=grid>.*id="{anchor}"')
        self.assertIn("if(node.tagName==='DETAILS')node.open=true", page)
        self.assertIn("image.loading='eager'", page)
        unmatched = {"destination": "Various/review/missing.jpg", "newPerson": "Various",
                     "newBucket": "review"}
        self.assertNotIn("review-photo-", rebase_recap._destination_links(unmatched, data, out.parent))
        data["finalMembershipAudit"] = {"rows": [
            {"source": row["source"], "destination": row["destination"], "rivals": []},
            {"source": "not-in-plan.jpg", "destination": "Various/review/missing.jpg", "rivals": []},
        ]}
        audit = rebase_recap._audit_section(data, out.parent)
        self.assertIn(f'href="#{anchor}"', audit)
        self.assertNotIn(rebase_recap._anchor("review-photo", "not-in-plan.jpg"), audit)
        self.assertIn("source evidence unavailable (photo not recorded in run)", audit)

    def test_review_cards_show_only_their_own_final_cast_evidence(self):
        data = rebase_recap.collect(self.run)
        data["status"] = "preview"
        rows = [row for row in data["rows"] if row["newBucket"] == "review"]
        data["finalMembershipAudit"] = {"rows": [{
            "source": rows[0]["source"],
            "castReferences": [{"folder": "Angels/Ava", "score": 0.471198},
                               {"folder": "Models/<untrusted>", "score": None}],
        }]}
        page = rebase_recap._review_section(data, self.working)
        first = re.search(
            rf'<figure id="{rebase_recap._anchor("review-photo", rows[0]["source"])}"[^>]*>(.*?)</figure>', page,
        ).group(1)
        second = re.search(
            rf'<figure id="{rebase_recap._anchor("review-photo", rows[1]["source"])}"[^>]*>(.*?)</figure>', page,
        ).group(1)
        self.assertIn("Final photo-to-cast similarity (not an identity decision)", first)
        self.assertIn("0.471", first)
        self.assertIn('href="#' + rebase_recap._anchor("cast", "Angels/Ava") + '" target="_blank"', first)
        self.assertIn("Models/&lt;untrusted&gt;", first)
        self.assertNotIn("0.471", second)
        self.assertIn("unavailable (not recorded)", second)

    def test_review_filter_exposes_paths_and_keeps_photo_deep_links_reachable(self):
        data = rebase_recap.collect(self.run)
        row = next(row for row in data["rows"] if row["newBucket"] == "review")
        row["source"] = 'Various/gallery/photo_"<&.jpg'
        page = rebase_recap.render(data, self.working / "report.html")
        self.assertIn('id="review-filter" type="search"', page)
        self.assertIn('id="review-filter-count" role="status">2 of 2 photos', page)
        self.assertIn('data-review-paths="Various/gallery/photo_&quot;&lt;&amp;.jpg ', page)
        self.assertIn("card.dataset.reviewPaths+' '+card.textContent", page)
        self.assertIn("if(id.startsWith('review-photo-')&&target.hidden)", page)

    def test_review_filter_executes_filename_evidence_and_empty_search(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required to exercise the generated Review filter")
        script = rebase_recap.SCRIPT
        start = script.index("function filterReview()")
        end = script.index("reviewFilter.addEventListener", start)
        program = """
const reviewFilter={value:''},reviewCount={textContent:''};
const reviewCards=[
  {dataset:{reviewPaths:'Various/gallery/image_123.jpg Various/review/image_123.jpg'},
   textContent:'quality hold Angels/Sammara 0.471',hidden:false},
  {dataset:{reviewPaths:'Various/gallery/image_456.jpg Various/review/image_456.jpg'},
   textContent:'unmeasured detector observation',hidden:false}
];
const reviewGroups=reviewCards.map(card=>({
  hidden:false,open:false,querySelectorAll:()=>[card]
}));
""" + script[start:end] + """
function run(value){reviewFilter.value=value;filterReview();return {
  count:reviewCount.textContent, cards:reviewCards.map(c=>c.hidden),
  groups:reviewGroups.map(g=>g.hidden),open:reviewGroups.map(g=>g.open)}}
console.log(JSON.stringify(['image_123','SAMMARA','no match',''].map(run)));
"""
        result = subprocess.run([node, "-e", program], capture_output=True, text=True, check=True)
        cases = json.loads(result.stdout)
        self.assertEqual([case["count"] for case in cases],
                         ["1 of 2 photos", "1 of 2 photos", "0 of 2 photos", "2 of 2 photos"])
        self.assertEqual(cases[0]["cards"], [False, True])
        self.assertEqual(cases[1]["groups"], [False, True])
        self.assertEqual(cases[0]["open"], [True, False])
        self.assertEqual(cases[2]["groups"], [True, True])
        self.assertEqual(cases[3]["cards"], [False, False])

    def test_person_links_filter_current_review_and_preserve_old_identity_continuity(self):
        data = rebase_recap.collect(self.run)
        out = self.working / "_reports" / "library" / "rebase-recap" / "run1.html"
        review = out.parent.parent / "people_gallery_review.html"
        review.parent.mkdir(parents=True, exist_ok=True)
        review.write_text("review", encoding="utf-8")
        page = rebase_recap.render(data, out)
        self.assertIn('people_gallery_review.html?person=Models%2FNia%20Vale', page)
        self.assertIn('people_gallery_review.html?person=Angels%2FAva&amp;bucket=Review', page)
        old_anchor = rebase_recap._anchor("continuity", "Prospects/Old")
        self.assertIn(f'href="#{old_anchor}" target="_blank" rel="noopener noreferrer"', page)
        self.assertIn(f'id="{old_anchor}"', page)
        self.assertNotIn('?person=Prospects%2FOld', page)
        anchor = rebase_recap._anchor("id", "Models/Nia Vale")
        self.assertIn(f'href="#{anchor}" target="_blank" rel="noopener noreferrer"', page)
        self.assertIn("target.open=true", page)
        self.assertIn("scrollIntoView", page)
        self.assertIn("requestAnimationFrame", page)
        self.assertIn("window.addEventListener('load',openTarget", page)

        data["historical"] = True
        self.assertNotIn("people_gallery_review.html?person=", rebase_recap.render(data, out))
        data["historical"] = False
        self.assertNotIn("<a ", rebase_recap._person_link("../outside", data, out.parent))
        self.assertNotIn("<a ", rebase_recap._person_link("Models/Unknown", data, out.parent))
        review.unlink()
        data.pop("_review_page", None)
        self.assertIn("Photo review unavailable", rebase_recap._person_link("Angels/Ava", data, out.parent))

    def test_continuity_counts_distinguish_gallery_arrivals_and_review_departures(self):
        data = rebase_recap.collect(self.run)
        page = rebase_recap._continuity_section(data, self.working)
        for person, expected in {
            "Angels/Ava": ["1", "1", "0", "0", "1", "1"],
            "Prospects/Old": ["1", "0", "0", "1", "0", "0"],
            "Various": ["2", "0", "0", "2", "0", "1"],
        }.items():
            anchor = rebase_recap._anchor("continuity", person)
            row = re.search(rf'<tr id="{anchor}">(.*?)</tr>', page).group(1)
            self.assertEqual(re.findall(r"<td>(\d+)</td>", row), expected)

    def test_preview_links_use_planned_sections_and_verified_prepared_photos(self):
        data = rebase_recap.collect(self.run)
        data["status"] = "preview"
        out = self.working / "_reports" / "library" / "rebase-recap" / "preview.html"
        out.parent.mkdir(parents=True)
        (out.parent.parent / "people_gallery_review.html").write_text("installed review", encoding="utf-8")
        row = data["rows"][0]
        row["preparedPath"] = "candidates/a/control.png"
        prepared = pathlib.Path(data["preparationIndex"]).parent / row["preparedPath"]
        prepared.parent.mkdir(parents=True, exist_ok=True)
        prepared.write_bytes(b"source-a")
        page = rebase_recap.render(data, out)
        self.assertNotIn("people_gallery_review.html?person=", page)
        for prefix, person in (("cast", "Angels/Ava"), ("id", "Models/Nia Vale")):
            anchor = rebase_recap._anchor(prefix, person)
            self.assertIn(f'href="#{anchor}" target="_blank"', page)
            self.assertIn(f'id="{anchor}"', page)
        self.assertIn("not installed", rebase_recap._destination_links(row, data, out.parent))
        thumb = rebase_recap._thumb(row, data, out.parent)
        self.assertIn("candidates/a/control.png", thumb)
        self.assertNotIn("Angels/Ava/gallery/ava_a.jpg", thumb.split('title="')[0])
        self.assertIn("candidates/a/control.png", rebase_recap._source_link(row["source"], row, data, out.parent))
        row["preparedPath"] = "../outside.jpg"
        self.assertNotIn("<a ", rebase_recap._thumb(row, data, out.parent))
        row["preparedPath"] = "candidates/a/control.png"
        prepared.write_bytes(b"edited")
        data.pop("_sha256_cache", None)
        self.assertNotIn("<img", rebase_recap._thumb(row, data, out.parent))

    def test_applied_thumbnail_requires_verified_final_photo(self):
        data = rebase_recap.collect(self.run)
        row = data["rows"][0]
        final = self.working / row["destination"]
        preview = self.working / "preview.jpg"
        preview.write_bytes(b"preview")
        row["preview"] = str(preview)
        verified = rebase_recap._thumb(row, data, self.working)
        self.assertIn('<img ', verified)
        self.assertIn('href="Angels/Ava/gallery/ava_a.jpg"', verified)

        for payload, expected in ((b"tampered", "photo bytes differ from recorded SHA-256"),
                                  (None, "photo missing")):
            if payload is None:
                final.unlink()
            else:
                final.write_bytes(payload)
            data.pop("_sha256_cache", None)
            result = rebase_recap._thumb(row, data, self.working)
            self.assertIn(expected, result)
            self.assertNotIn("<a ", result)
            self.assertNotIn("<img", result)

        row["preparedSHA256"] = None
        row["sha256"] = None
        final.write_bytes(b"source-a")
        data.pop("_sha256_cache", None)
        self.assertIn("expected SHA-256 not recorded", rebase_recap._thumb(row, data, self.working))

    def test_direct_only_family_prose_does_not_claim_secondary_links_enabled(self):
        data = rebase_recap.collect(self.run)
        data["familyNaming"] = {
            "families": [], "directCastMinimumSimilarity": .4,
            "secondaryMinimumSimilarityExclusive": .35, "secondarySurnameLinksEnabled": False,
        }
        page = rebase_recap._family_section(data)
        self.assertIn("secondary surname links disabled", page)
        self.assertNotIn("secondary minimum similarity", page)
        data["familyNaming"].pop("secondarySurnameLinksEnabled")
        self.assertIn("secondary minimum similarity", rebase_recap._family_section(data))

    def test_family_comparisons_are_collapsed_bounded_and_linked(self):
        data = rebase_recap.collect(self.run)
        row = next(r for r in data["rows"] if r["newPerson"] == "Models/Nia Vale")
        data["rows"].extend({**row, "source": f"Various/gallery/sample_{i}.jpg",
                             "destination": f"Models/Nia Vale/gallery/sample_{i}.png"} for i in range(7))
        for item in data["rows"]:
            if item["newPerson"] != "Models/Nia Vale":
                continue
            target = self.working / item["destination"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"fixture")
            item["preparedSHA256"] = hashlib.sha256(b"fixture").hexdigest()
        data["familyNaming"] = {"families": [{
            "rootFolder": "Angels/Ava", "surname": "Hadley", "members": [
                {"folder": "Angels/Ava", "status": "cast", "score": None, "path": []},
                {"folder": "Models/Nia Vale", "status": "renamed", "previousName": "Nia Moss",
                 "parentFolder": "Angels/Ava", "score": .41, "path": []},
            ]}]}
        out_dir = self.working / "_reports" / "library" / "rebase-recap"
        out_dir.mkdir(parents=True)
        (out_dir.parent / "people_gallery_review.html").write_text("review", encoding="utf-8")
        page = rebase_recap._family_section(data, out_dir)

        class Images(HTMLParser):
            def __init__(self):
                super().__init__()
                self.images = []
                self.comparisons = []

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "img":
                    self.images.append(attrs)
                if tag == "details":
                    self.comparisons.append(attrs)

        parsed = Images()
        parsed.feed(page)
        self.assertEqual(len(parsed.images), 6)  # One root, at most five member samples.
        self.assertTrue(all(i.get("loading") == "lazy" for i in parsed.images))
        self.assertTrue(parsed.comparisons)
        self.assertTrue(all("open" not in d for d in parsed.comparisons))
        self.assertIn("up to five", page)
        self.assertIn("<template class=family-samples>", page)
        self.assertIn("?person=Models%2FNia%20Vale", page)
        self.assertEqual(page, rebase_recap._family_section(data, out_dir))
        data["historical"] = True
        historical = rebase_recap._family_section(data, out_dir)
        self.assertNotIn("<img", historical)
        self.assertNotIn("people_gallery_review.html?person=", historical)

    def test_missing_supplementary_reports_are_not_dead_links(self):
        data = rebase_recap.collect(self.run)
        out = self.working / "report.html"
        page = rebase_recap.render(data, out)
        self.assertNotIn('href="_sandbox-state/run1/report.md"', page)
        self.assertIn("Run report unavailable", page)
        (self.run / "report.md").write_text("report", encoding="utf-8")
        self.assertIn('href="_sandbox-state/run1/report.md"', rebase_recap.render(data, out))

    def test_audit_distinguishes_blocked_followups_from_eligible_moves(self):
        data = rebase_recap.collect(self.run)
        base = {"source": data["rows"][0]["source"], "higherRival": True, "followupCandidate": True,
                "refinementDecision": {"decision": "hold", "reason": "margin gate"},
                "refinementHoldReason": "margin gate"}
        data["finalMembershipAudit"] = {"state": "audited", "automaticMoves": 0, "nextPassNeeded": True,
                                        "rows": [dict(base) for _ in range(29)]}
        page = rebase_recap._audit_section(data, self.working)
        self.assertIn("Eligible automatic moves remaining: 0", page)
        self.assertIn("margin gate: 29", page)
        self.assertIn("nextPassNeeded: True", page)
        self.assertIn("does not by itself mean another automatic pass", page)
        self.assertNotIn("no convergence or extra moves were performed", page)
        data["finalMembershipAudit"]["rows"].append(
            {**base, "refinementDecision": {"decision": "move"}, "refinementHoldReason": None})
        self.assertIn("Eligible automatic moves remaining: 1", rebase_recap._audit_section(data, self.working))
        data["finalMembershipAudit"]["rows"].append({"source": base["source"]})
        self.assertIn("Eligible automatic moves remaining: unavailable",
                      rebase_recap._audit_section(data, self.working))

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

    def test_exact_arrival_aliases_show_canonical_routes_without_extra_votes_or_undo(self):
        overlay_path = self.run / "source-overlay/overlay.json"
        overlay_path.parent.mkdir()
        source = "Angels/Ava/gallery/ava_a.jpg"
        checksum = "a" * 64
        overlay_path.write_text(json.dumps({
            "inputs": {source: {"sha256": checksum}},
            "currentVarious": [{
                "current": "Various/gallery/copy<&>.jpg", "target": source,
                "sha256": checksum, "duplicateOf": "Various/gallery/canonical.jpg",
            }],
        }), encoding="utf-8")
        plan = _plan(self.working)
        plan["photos"][0]["sha256"] = checksum
        plan["sourceOverlaySHA256"] = hashlib.sha256(overlay_path.read_bytes()).hexdigest()
        plan["recoveryMode"] = "disposable"
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        data = rebase_recap.collect(self.run)
        self.assertEqual(len(data["incomingAliases"]), 1)
        self.assertEqual(rebase_recap.summarize(data)["photos"], 4)
        page = rebase_recap.render(data, self.run / "recap.html")
        self.assertIn("Exact incoming aliases: 1", page)
        self.assertIn("copy&lt;&amp;&gt;.jpg", page)
        self.assertIn(source, page)
        self.assertIn("no undo; recover by full sandbox reset", page)
        self.assertNotIn("Undo only through", page)
        overlay_path.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "overlay differs"):
            rebase_recap.collect(self.run)

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
        self.assertIn("Photo review", page)
        self.assertIn("count conservation", page.lower())
        self.assertNotIn("file:///", page)
        self.assertIn("run1.html", (out.parent / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(rebase_recap.main([str(self.run), "--check"]), 0)
        data = rebase_recap.collect(self.run)
        unsafe = dict(data["rows"][1], destination="../../outside.jpg")
        self.assertIn("unsafe destination link unavailable",
                      rebase_recap._destination_links(unsafe, data, out.parent))

    def test_continuation_aliases_use_bound_original_overlay_without_copying(self):
        original = self.run.parent / "original"
        overlay_path = original / "source-overlay" / "overlay.json"
        overlay_path.parent.mkdir(parents=True)
        source = "Angels/Ava/gallery/ava_a.jpg"
        checksum = "a" * 64
        overlay_path.write_text(json.dumps({
            "inputs": {source: {"sha256": checksum}},
            "currentVarious": [{
                "current": "Various/gallery/copy.jpg", "target": source,
                "sha256": checksum, "duplicateOf": source,
            }],
        }), encoding="utf-8")
        plan = _plan(self.working)
        plan.update(
            reusedPreparationFrom=str(original), sourceRoot=str(original / "source-overlay"),
            sourceOverlaySHA256=hashlib.sha256(overlay_path.read_bytes()).hexdigest(),
        )
        plan["photos"][0]["sha256"] = checksum
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        self.assertEqual(len(rebase_recap.collect(self.run)["incomingAliases"]), 1)
        self.assertFalse((self.run / "source-overlay").exists())
        overlay_path.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "overlay differs"):
            rebase_recap.collect(self.run)
        plan["sourceRoot"] = str(self.run / "source-overlay")
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "overlay root"):
            rebase_recap.collect(self.run)

    def test_family_section_shows_tree_links_and_renames(self):
        plan = _plan(self.working)
        plan["familyNaming"] = {
            "enabled": True, "linkBand": "yellow", "linkMinimum": 0.3, "rule": "closest cast, then peer",
            "linkedIdentityCount": 1, "renamedIdentityCount": 1, "unlinkedIdentityCount": 0,
            "cast": {"Angels/Ava": {"recordedPersonName": "Ava Vale", "currentPersonName": "Ava Hadley",
                                    "surname": "Hadley", "surnameSource": "configured"}},
            "families": [{
                "id": "family_" + "0" * 32, "root": "Angels/Ava", "rootFolder": "Angels/Ava", "rootKind": "cast",
                "surname": "Hadley", "surnameSource": "configured",
                "members": [{
                    "identity": "Models/Generated", "folder": "Models/Nia Vale", "previousName": "Nia Moss",
                    "name": "Nia Vale", "status": "renamed", "parent": "Angels/Ava", "parentFolder": "Angels/Ava",
                    "tier": "cast", "score": 0.41, "band": "yellow",
                    "path": [{"from": "Models/Generated", "to": "Angels/Ava", "toFolder": "Angels/Ava",
                              "score": 0.41, "band": "yellow", "tier": "cast"}],
                }],
            }],
        }
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        out = self.working / "_reports" / "library" / "rebase-recap" / "run1.html"
        self.assertEqual(rebase_recap.main([str(self.run)]), 0)
        page = out.read_text(encoding="utf-8")
        self.assertIn('id=families', page)
        self.assertIn('href="#families"', page)
        self.assertIn("Angels/Ava", page)
        self.assertIn(": Hadley", re.sub("<[^>]+>", "", page))
        self.assertIn("Ava Vale &rarr; <b>Ava Hadley</b>", page)
        self.assertIn("was Nia Moss", page)
        self.assertIn("0.410 yellow", page)
        self.assertIn("family Hadley", page)
        self.assertIn("Link band <b>yellow</b> (score at least 0.300)", page)

    def test_family_section_prefers_new_distinct_thresholds_when_saved(self):
        evidence = {
            "linkBand": "yellow", "linkMinimum": 0.4,
            "directCastMinimumSimilarity": 0.4,
            "secondaryMinimumSimilarityExclusive": 0.35,
            "families": [], "linkedIdentityCount": 0, "renamedIdentityCount": 0,
            "displacedFamilyCount": 0, "unlinkedIdentityCount": 0, "rule": "",
        }
        page = rebase_recap._family_section({"familyNaming": evidence})
        self.assertIn("Direct-cast minimum similarity &ge; 0.400", page)
        self.assertIn("secondary minimum similarity &gt; 0.350", page)
        self.assertNotIn("Link band <b>", page)

    def test_family_section_reports_older_runs_without_family_naming(self):
        out = self.working / "_reports" / "library" / "rebase-recap" / "run1.html"
        self.assertEqual(rebase_recap.main([str(self.run)]), 0)
        self.assertIn("predates score-band family naming", out.read_text(encoding="utf-8"))

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

    def test_audit_source_link_falls_back_after_the_source_moved(self):
        plan = _plan(self.working)
        plan["photos"][0]["sha256"] = hashlib.sha256(b"kept").hexdigest()
        plan["photos"][2]["sha256"] = hashlib.sha256(b"moved-final").hexdigest()
        plan["photos"][2]["preparedSHA256"] = hashlib.sha256(b"moved-final").hexdigest()
        plan["finalMembershipAudit"] = {"state": "audited", "rows": [
            {"source": "Angels/Ava/gallery/ava_a.jpg", "destination": "Angels/Ava/gallery/ava_a.jpg",
             "reason": "kept"},
            {"source": "Various/gallery/c.jpg", "destination": "Models/Nia Vale/gallery/nia_vale_c.png",
             "reason": "moved"},
        ]}
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        kept = self.working / "Angels" / "Ava" / "gallery" / "ava_a.jpg"
        kept.parent.mkdir(parents=True, exist_ok=True)
        kept.write_bytes(b"kept")
        final = self.working / "Models" / "Nia Vale" / "gallery" / "nia_vale_c.png"
        final.parent.mkdir(parents=True)
        final.write_bytes(b"moved-final")
        data = rebase_recap.collect(self.run)
        page = rebase_recap.render(data, self.working / "report.html")
        self.assertIn('href="Angels/Ava/gallery/ava_a.jpg" target="_blank" rel="noopener noreferrer">Source photo (bytes verified)',
                      page)
        self.assertNotIn('href="Various/gallery/c.jpg"', page)
        self.assertIn("previous location absent from this working tree", page)
        self.assertIn('>Verified final photo</a>', page)
        self.assertNotIn("moved (original path no longer exists)", page)
        final.write_bytes(b"tampered")
        changed = rebase_recap.render(rebase_recap.collect(self.run), self.working / "report.html")
        self.assertIn("photo bytes differ from recorded SHA-256", changed)
        final.unlink()
        missing = rebase_recap.render(rebase_recap.collect(self.run), self.working / "report.html")
        self.assertIn("photo missing", missing)

    def test_reused_preparation_provenance_links_original_intake_and_verified_destination(self):
        source = "Various/gallery/c.jpg"
        digest = hashlib.sha256(b"prepared-c").hexdigest()
        original_run = self.run.parent / "source-run"
        preparation = original_run / "inputs" / "_reports" / "preparation" / "all"
        (preparation / "photos").mkdir(parents=True)
        (preparation / "index.html").write_text("index", encoding="utf-8")
        (preparation / "photos" / "case.html").write_text("intake", encoding="utf-8")
        source_payload = json.dumps({"photos": [{
            "source": source, "detail": "photos/case.html", "sourceSha256": digest,
        }]}).encode()
        (preparation / "manifest.json").write_bytes(source_payload)
        original_receipt = original_run / "intake-receipt.json"
        original_receipt.write_text("unchanged", encoding="utf-8")
        local_manifest = self.run / "inputs" / "_reports" / "preparation" / "all" / "manifest.json"
        local_manifest.unlink()

        plan = _plan(self.working)
        plan["reusedPreparationFrom"] = str(original_run)
        plan["photos"] = [{
            "source": source, "destination": "Various/review/c.jpg", "sha256": digest,
            "preparedSHA256": digest, "photoId": "photo:c", "reason": "quality hold",
        }]
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        final = self.working / "Various" / "review" / "c.jpg"
        final.parent.mkdir(parents=True)
        final.write_bytes(b"prepared-c")
        data = rebase_recap.collect(self.run)
        source_cell = rebase_recap._source_link(
            data["rows"][0]["source"], data["rows"][0], data, self.working,
        )

        self.assertEqual(pathlib.Path(data["preparationIndex"]), preparation / "index.html")
        self.assertIn("previous location absent from this working tree", source_cell)
        self.assertIn("Verified final photo", source_cell)
        self.assertIn("Intake comparison", source_cell)
        self.assertEqual(original_receipt.read_text(encoding="utf-8"), "unchanged")
        self.assertEqual((preparation / "manifest.json").read_bytes(), source_payload)

    def test_final_audit_core_references_override_initial_seed_and_legacy_references(self):
        plan = _plan(self.working)
        plan["photos"][0]["castSeedCore"] = True
        plan["coreReferences"] = {"Angels/Ava": [{
            "source": plan["photos"][0]["source"], "destination": plan["photos"][0]["destination"],
            "photoId": "photo:a", "score": 0.6,
        }]}
        arrival = plan["photos"][1]
        arrival["destination"] = "Angels/Ava/gallery/ava_b.png"
        arrival["preparedPath"] = "candidates/b/control.png"
        arrival["preparedSHA256"] = "saved-prepared-digest"
        plan["finalMembershipAudit"] = {"coreReferences": {"Angels/Ava": [{
            "source": arrival["source"], "destination": arrival["destination"],
            "photoId": "photo:b", "score": 0.87,
        }]}}
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")

        data = rebase_recap.collect(self.run)
        references = rebase_recap._core_reference_rows(data, "Angels/Ava")

        self.assertEqual([row["photoId"] for row in references], ["photo:b"])
        self.assertEqual(references[0]["castSeedScore"], 0.87)
        self.assertEqual(references[0]["preparedPath"], arrival["preparedPath"])
        self.assertEqual(references[0]["preparedSHA256"], arrival["preparedSHA256"])

    def test_explicit_empty_final_core_does_not_restore_initial_seed_references(self):
        plan = _plan(self.working)
        plan["photos"][0]["castSeedCore"] = True
        plan["finalMembershipAudit"] = {"coreReferences": {"Angels/Ava": []}}
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")

        data = rebase_recap.collect(self.run)

        self.assertEqual(rebase_recap._core_reference_rows(data, "Angels/Ava"), [])

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
                "refinementHoldReason": "remains held: <manual review>",
            }],
        }
        plan["finalMembershipAudit"]["rows"].append({
            "source": "Various/gallery/d.jpg", "destination": "Various/review/d.png",
            "higherRival": False, "followupCandidate": True, "reason": "follow-up only",
        })
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        data = rebase_recap.collect(self.run)
        references = rebase_recap._core_reference_rows(data, "Angels/Ava")
        self.assertEqual([row["photoId"] for row in references], ["photo:a", "photo:extra"])
        self.assertIsNone(references[0]["castSeedScore"])
        page = rebase_recap.render(data, self.working / "report.html")
        self.assertIn("Audit state: <b>audited</b>", page)
        self.assertIn("1 photo(s) with a higher rival; 1 additional follow-up-only photo(s), not counted above", page)
        self.assertNotIn("Audit state: <b>passed</b>", page)
        self.assertIn("pass: 1", page)
        self.assertIn("reference: final frozen core &lt;snapshot&gt;", page)
        self.assertIn("The audit itself is read-only; it performs no extra moves.", page)
        for field in ("higherRivalCount", "followupCandidateCount", "nextPassNeeded", "automaticMoves",
                      "automaticPhotoProtectionCount", "automaticIdentityProtectionCount",
                      "protectionEvidence", "diagnostics", "protected", "anchor", "workflowSelected",
                      "followupCandidate"):
            self.assertIn(field, page)
        self.assertNotIn('href="Angels/Ava/gallery/extra.png" target="_blank"', page)
        self.assertIn("link withheld (expected SHA-256 not recorded)", page)
        self.assertIn("Eligible core reference; score unavailable (not recorded)", page)
        self.assertIn("Eligible core reference; score 0.810", page)
        self.assertIn(f'data-cast-filter="{rebase_recap._anchor("cast", "Angels/Ava")}"', page)
        for field in ("coreMember", "automaticProtection", "manualOptOut", "rivalMargin",
                      "independentProtectionSupport", "protectionReason"):
            self.assertIn(field, page)
        self.assertIn("protectionReason: manual &lt;opt-out&gt;", page)
        self.assertIn("refinementHoldReason: remains held: &lt;manual review&gt;", page)
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
        plan["finalMembershipRefinement"] = {
            "passCount": 1, "stopReason": "stable", "moveCount": 0, "passes": [],
            "residuals": [{"source": "a.jpg", "reason": "manual <lock>"}],
        }
        (self.run / "run.json").write_text(json.dumps(plan), encoding="utf-8")
        page = rebase_recap.render(rebase_recap.collect(self.run), self.working / "report.html")
        self.assertIn("id=refinement", page)
        self.assertIn("stop reason <b>stable</b>", page)
        self.assertIn("Models/Bea &lt;Kay&gt;", page)
        self.assertIn("<td>identity-merge</td><td>2 photo(s)</td><td>Potentials/Cy Dee</td>", page)
        self.assertIn("<td>locked</td><td>photo:z</td><td>anchored</td>", page)
        self.assertIn("Audit-aligned final-membership refinement", page)
        self.assertIn("manual &lt;lock&gt;", page)
        self.assertIn("Stable means no further admitted moves", page)
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
