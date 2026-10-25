"""Gallery-facing verification of source-preserving preparation evidence."""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import image_preparation  # noqa: E402
import artists_gallery  # noqa: E402
import people_gallery  # noqa: E402
from likeness_library import preparation_provenance, review_gallery  # noqa: E402


class PreparationProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name) / "Sovereign Territories Sandbox" / "Working"
        self.photo = self.root / "Angels" / "Fixed Slot" / "gallery" / "image_123.jpg"
        self.photo.parent.mkdir(parents=True)
        Image.new("RGB", (160, 240), (90, 40, 20)).save(self.photo)
        self.output = self.root / "_reports" / "preparation" / "pilot-v7"
        detector = mock.patch.object(
            image_preparation.preparation_geometry,
            "detect_faces",
            return_value=([[50.0, 40.0, 60.0, 70.0]], "Usable test face."),
        )
        detector.start()
        self.addCleanup(detector.stop)
        for patch in (mock.patch.object(image_preparation.pipeline.subjects, "detect", return_value=None),
                      mock.patch.object(image_preparation.pipeline.fill, "fill",
                                        side_effect=RuntimeError("no LaMa in tests"))):
            patch.start()
            self.addCleanup(patch.stop)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = image_preparation.main([
                "--root", str(self.root), "--out", str(self.output), "--apply",
            ])
        self.assertEqual(result, 0)
        self.page_dir = self.root / "_reports" / "library"
        self.page_dir.mkdir(parents=True)
        self.photo_id = json.loads((self.output / "manifest.json").read_text())["photos"][0]["photoId"]

    def index(self, photo=None, photo_id=None, domain="general"):
        photo = photo or self.photo
        return preparation_provenance.build_index(
            self.root,
            self.page_dir,
            [(photo, self.photo_id if photo_id is None else photo_id)],
            domain,
        )

    def test_exact_source_and_scope_link_only_to_verified_trace(self):
        evidence = self.index().evidence(self.photo, self.photo_id)
        self.assertEqual(evidence["state"], "verified")
        self.assertEqual(len(evidence["matches"]), 1)
        match = evidence["matches"][0]
        self.assertEqual(match["scope"], "general")
        self.assertEqual(match["sourceSha256"], image_preparation.sha(self.photo.read_bytes()))
        self.assertIn("pilot-v7/photos/", match["href"])
        self.assertIn("not rename proof", preparation_provenance.render_evidence(evidence))

    def test_changed_source_is_stale_and_has_no_published_link(self):
        self.photo.write_bytes(self.photo.read_bytes() + b"changed")
        evidence = self.index().evidence(self.photo, self.photo_id)
        self.assertEqual(evidence["state"], "stale")
        self.assertEqual(evidence["matches"], [])
        self.assertNotIn("<a ", preparation_provenance.render_evidence(evidence))

    def test_multiple_verified_runs_are_listed_without_latest_run_guess(self):
        second = self.root / "_reports" / "preparation" / "pilot-v8"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = image_preparation.main([
                "--root", str(self.root), "--out", str(second), "--apply",
            ])
        self.assertEqual(result, 0)
        legacy_manifest = self.output / "manifest.json"
        legacy = json.loads(legacy_manifest.read_text(encoding="utf-8"))
        legacy["recipe"]["id"] = "preparation-comparison-v6"
        legacy["photos"][0].pop("sourceScope", None)
        processing = legacy["photos"][0]["processing"]
        order = image_preparation.legacy.OLD_STEPS
        processing["steps"] = sorted(
            (s for s in processing["steps"] if s["name"] in order), key=lambda s: order.index(s["name"]))
        legacy_manifest.write_text(json.dumps(legacy), encoding="utf-8")
        evidence = self.index().evidence(self.photo, self.photo_id)
        self.assertEqual(evidence["state"], "ambiguous")
        self.assertEqual(len(evidence["matches"]), 2)
        self.assertIn("without choosing a latest run", evidence["summary"])
        self.assertTrue(any(
            "derived from verified original path" in match["scope"]
            for match in evidence["matches"]
        ))
        rendered = preparation_provenance.render_evidence(evidence)
        self.assertIn("2 intake runs", rendered)
        self.assertIn("intake_runs.html?source=", rendered)
        self.assertNotIn("<details", rendered)
        self.assertNotIn("preventDefault();details.open", preparation_provenance.EVIDENCE_SCRIPT)
        history = self.index().history_html()
        self.assertIn("pilot-v7", history)
        self.assertIn("pilot-v8", history)
        self.assertIn("Find runs", history)
        self.assertIn("Find photos", history)
        self.assertIn("Requested run is unavailable", history)

    def test_history_checks_runs_beyond_continuity_budget_without_extending_evidence(self):
        second = self.root / "_reports" / "preparation" / "pilot-v8"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = image_preparation.main([
                "--root", str(self.root), "--out", str(second), "--apply",
            ])
        self.assertEqual(result, 0)
        with mock.patch.object(preparation_provenance, "MAX_RUNS", 1):
            index = self.index()
            evidence = index.evidence(self.photo, self.photo_id)
            history = index.history_html()
        self.assertTrue(index.incomplete)
        self.assertEqual(evidence["matches"], [])
        self.assertEqual(len(index.history_runs), 2)
        self.assertTrue(all(len(run["photos"]) == 1 for run in index.history_runs))
        self.assertIn("does not extend source-continuity claims", history)

    def test_history_never_links_tampered_runs_and_keeps_diagnostic(self):
        (self.output / "index.html").write_bytes(b"tampered")
        index = self.index()
        history = index.history_html()
        self.assertIn("unverified:", history)
        self.assertIn("hash mismatch", history)
        self.assertEqual(index.history_runs[0]["href"], "")
        self.assertEqual(index.history_runs[0]["photos"], [])

    def test_history_excludes_other_matching_domains(self):
        index = self.index(domain="artists")
        history = index.history_html()
        self.assertEqual(index.history_runs[0]["photos"], [])
        self.assertEqual(index.history_runs[0]["href"], "")
        self.assertNotIn("image_123.jpg", history)

    def test_history_payload_escapes_script_content_and_includes_empty_state(self):
        index = self.index()
        index.history_runs[0]["name"] = "</script><script>alert(1)</script>"
        history = index.history_html()
        self.assertNotIn("</script><script>alert", history)
        self.assertIn("No runs match these filters.", history)
        self.assertIn("Show next 60 photos", history)

    def test_renamed_source_with_filename_id_is_unverified_not_followed(self):
        renamed = self.photo.with_name("renamed_image_123.jpg")
        self.photo.rename(renamed)
        evidence = self.index(renamed, self.photo_id).evidence(renamed, self.photo_id)
        self.assertEqual(evidence["state"], "unverified")
        self.assertIn("rename continuity is not verified", evidence["summary"])
        self.assertEqual(evidence["matches"], [])

    def test_missing_trace_is_explicit(self):
        other = self.root / "Angels" / "Fixed Slot" / "gallery" / "photo_456.jpg"
        other.write_bytes(self.photo.read_bytes())
        evidence = self.index(other, "photo:photo_456").evidence(other, "photo:photo_456")
        self.assertEqual(evidence["state"], "missing")
        self.assertIn("exact source path and hash", evidence["summary"])

    def test_scope_mismatch_is_unverified(self):
        manifest_path = self.output / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["photos"][0]["sourceScope"]["matchingDomain"] = "Artists/Studio"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        evidence = self.index().evidence(self.photo, self.photo_id)
        self.assertEqual(evidence["state"], "unverified")
        self.assertEqual(evidence["matches"], [])

    def test_artist_scope_is_bound_to_exact_artist_folder_not_filename_or_hash(self):
        row = {"sourceScope": {
            "category": "Artists",
            "artist": "Studio A",
            "matchingDomain": "Artists/Studio A",
            "reason": "artist-origin source path",
        }}
        self.assertTrue(preparation_provenance._scope_matches(
            row, "Artists/Studio A/Aster/gallery/image_123.jpg", "artists",
        ))
        self.assertFalse(preparation_provenance._scope_matches(
            row, "Artists/Studio B/Aster/gallery/image_123.jpg", "artists",
        ))
        self.assertFalse(preparation_provenance._scope_matches(
            row, "Artists/Studio A/Aster/gallery/image_123.jpg", "general",
        ))

    def test_tampered_report_is_unverified_and_never_linked(self):
        report = self.output / "index.html"
        report.write_bytes(report.read_bytes() + b"tampered")
        evidence = self.index().evidence(self.photo, self.photo_id)
        self.assertEqual(evidence["state"], "unverified")
        self.assertIn("could not be verified", evidence["summary"])
        self.assertEqual(evidence["matches"], [])

    def test_row_budget_refuses_before_expensive_report_verification(self):
        with (
            mock.patch.object(preparation_provenance, "MAX_ROWS", 0),
            mock.patch.object(image_preparation, "verify") as verify,
        ):
            index = self.index()
            evidence = index.evidence(self.photo, self.photo_id)
        verify.assert_not_called()
        self.assertTrue(index.incomplete)
        self.assertEqual(evidence["state"], "unverified")
        self.assertEqual(evidence["matches"], [])

    def test_current_source_hash_is_cached_per_index(self):
        index = self.index()
        with mock.patch.object(
            preparation_provenance.hashlib, "sha256",
            wraps=preparation_provenance.hashlib.sha256,
        ) as digest:
            index.evidence(self.photo, self.photo_id)
            index.evidence(self.photo, self.photo_id)
        self.assertEqual(digest.call_count, 1)

    def test_single_trace_has_direct_intake_entry_and_both_viewers_share_renderer(self):
        evidence = self.index().evidence(self.photo, self.photo_id)
        rendered = preparation_provenance.render_evidence(evidence)
        self.assertIn('class="intake-detail-link"', rendered)
        self.assertIn("Open intake detail", rendered)
        self.assertIn(evidence["matches"][0]["href"], rendered)
        self.assertIn("not proof of publication", rendered)
        for script in (review_gallery.SCRIPT, artists_gallery.SCRIPT):
            self.assertTrue(script.startswith(preparation_provenance.EVIDENCE_SCRIPT))
            self.assertEqual(script.count("function appendPreparationEvidence("), 1)
        self.assertIn("appendPreparationEvidence(card,r.preparationEvidence)", artists_gallery.SCRIPT)

    def test_unavailable_trace_never_gets_direct_intake_entry(self):
        for state in ("missing", "stale", "unverified"):
            with self.subTest(state=state):
                rendered = preparation_provenance.render_evidence({
                    "state": state, "summary": "links withheld", "matches": [],
                })
                self.assertNotIn("<a ", rendered)
                self.assertIn("links withheld", rendered)

    def test_gallery_payloads_escape_html_and_build_provenance_dom_without_inner_html(self):
        unsafe = {
            "state": "verified",
            "summary": "</script><script>alert(1)</script>",
            "matches": [{
                "href": "../preparation/pilot/photos/detail.html",
                "recipe": "</script>",
                "outcome": "compared",
                "scope": "general",
                "treatment": "original-unassessed",
                "decision": "original",
                "reason": "</script><script>alert(1)</script>",
                "photoId": "photo:123",
                "sourceSha256": "a" * 64,
            }],
        }
        review = review_gallery.render_html([{
            "folder": "Prospects/Test", "group": "Prospects",
            "preparationEvidence": unsafe,
        }], "now")
        artist = artists_gallery.page([{
            "artist": "</script><script>alert(1)</script>",
            "preparationEvidence": unsafe,
        }], detail=True, stats="test").decode("utf-8")
        overview = people_gallery.render_html([{
            "status": "Prospects", "folder": "Test", "photos": 1, "review": 0,
            "chosen": False, "score": None, "source": "", "tags": {},
            "gallery_photos": [{
                "name": "image.jpg", "path": self.photo, "thumb": b"image",
                "preparationEvidence": unsafe,
            }],
        }], "now", {"Prospects": 1})
        for page in (review, artist, overview):
            self.assertNotIn("</script><script>alert", page)
        self.assertIn("appendPreparationEvidence", review)
        self.assertIn("textContent", review)
        self.assertNotIn("innerHTML", review)
        self.assertIn("Open verified trace", artist)
        self.assertIn("Open verified trace", overview)


if __name__ == "__main__":
    unittest.main()
