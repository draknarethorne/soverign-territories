import copy
import json
import pathlib
import tempfile
import unittest
from unittest import mock

import numpy as np

from tools.art import likeness_diagnostics as cli
from tools.art.likeness_library import membership_diagnostics as diagnostic
from tools.art.likeness_library.tests import test_membership_reassessment as fixtures


class MembershipDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.MembershipReassessmentTests()
        fixture.setUp()
        self.fixture = fixture
        self.run, self.vectors = fixture.run, fixture.vectors
        self.run["policy"]["categoryPolicies"]["Angels"].update(
            galleryAdmissionMinimumSimilarity=.45, galleryAdmissionEnabled=True,
        )
        self.run["policy"]["categoryPolicies"]["Sisters"]["identityCoreMinimumSimilarity"] = .4
        self.state = fixture.build()

    def build(self):
        return diagnostic.build(self.state, self.run, self.vectors)

    def row(self, result, pid="p5"):
        return next(r for r in result["rows"] if r["photoId"] == pid)

    def low_score(self):
        self.vectors["p5"] = np.zeros(9)
        self.vectors["p5"][0] = .37
        self.vectors["p5"][8] = np.sqrt(1-.37**2)
        self.state = self.fixture.build()

    def test_existing_retention_is_not_new_join_or_core(self):
        self.low_score()
        row = self.row(self.build())
        sister = row["categoryComparisons"][0]
        self.assertGreater(row["activeOwnScore"], .3)
        self.assertLess(row["activeOwnScore"], .4)
        self.assertEqual(sister["existingMemberConsistencyIgnoringLocks"]["decision"], "keep")
        self.assertFalse(sister["categoryCoreEligible"])
        self.assertFalse(sister["numericJoinPass"])
        self.assertIn("score-below-new-join-floor", sister["numericJoinBlockers"])
        self.assertEqual({c["sameActiveOwnScore"] for c in row["categoryComparisons"]}, {row["activeOwnScore"]})

    def test_saved_angel_override_and_prospect_floor_do_not_change_evidence(self):
        row = self.row(self.build())
        self.assertEqual([c["joinFloor"] for c in row["categoryComparisons"]], [.5, .45, .5, .4])
        self.assertTrue(all(c["sameActiveOwnScore"] == row["activeOwnScore"] for c in row["categoryComparisons"]))

    def test_signed_negative_lead_fails_separation(self):
        target = self.row(self.state)
        own = target["membershipAssessment"]["own"]
        target["membershipAssessment"]["rivals"] = [{"score": own["activeScore"]+.1}]
        row = self.row(self.build())
        self.assertLess(row["ownLeadOverAllHypotheses"], 0)
        self.assertTrue(all("rival-separation-insufficient" in c["numericJoinBlockers"]
                            for c in row["categoryComparisons"]))

    def test_exact_veto_survives_every_category_counterfactual(self):
        target = self.row(self.state)
        target["membershipAssessment"]["own"]["blockers"].append("direct-different-or-uncertain-veto")
        for item in self.row(self.build())["categoryComparisons"]:
            self.assertFalse(item["numericJoinPass"])
            self.assertIn("direct-different-or-uncertain-veto", item["numericJoinBlockers"])

    def test_correlated_references_do_not_supply_four_independent_supporters(self):
        for pid in ("p1", "p2", "p3", "p4"):
            self.vectors[pid] = self.vectors["p0"].copy()
        self.state = self.fixture.build()
        row = self.row(self.build())
        self.assertTrue(all(len(item["supportPhotoIds"]) < 4 and not item["numericJoinPass"]
                            for item in row["categoryComparisons"]))

    def test_no_active_reference_is_unmeasured_not_confirmed(self):
        own = self.row(self.state)["membershipAssessment"]["own"]
        own.update(activeScore=None, referencePhotoIds=[])
        row = self.row(self.build())
        self.assertIsNone(row["activeOwnScore"])
        self.assertIsNotNone(row["bestOriginalViewScore"])
        self.assertTrue(all(c["categoryCoreEligible"] is None and not c["numericJoinPass"]
                            for c in row["categoryComparisons"]))

    def test_query_and_equal_content_excluded_and_state_unchanged(self):
        result = self.build()
        self.assertNotIn("p5", self.row(result)["activeOwnReferencePhotoIds"])
        self.assertNotIn("p5", self.row(result)["bestOriginalViewReferences"])
        original = copy.deepcopy(self.state)
        self.run["photos"][0]["preparedSHA256"] = self.run["photos"][1]["preparedSHA256"]
        # A stale saved score is rejected, not silently published.
        with self.assertRaisesRegex(ValueError, "does not reproduce"):
            self.build()
        self.assertEqual(self.state, original)

    def test_html_safe_inline_and_all_category_scores(self):
        result = self.build()
        self.run["workingRoot"] = str(pathlib.Path.cwd())
        text = cli.render(result, {"pairs": []}, {}, self.run)
        self.assertIn("img.src=r.href", text)
        self.assertIn('a.append(img,', text)
        self.assertIn("categoryCoreEligible===null", text)
        self.assertIn("Image unavailable at installed path", text)
        self.assertIn("original/unqualified view, NOT an eligible receiving identity", text)
        self.assertIn("Existing-member handling", text)
        self.assertIn('type="application/json"', text)

    def test_auc_excludes_uncertain_and_handles_missing(self):
        pairs = [{"label": "same", "x": .8}, {"label": "different", "x": .2},
                 {"label": "uncertain", "x": 1.0}, {"label": "different", "x": None}]
        self.assertEqual(cli.auc(pairs, "x"), 1.)
        self.assertIsNone(cli.auc(pairs[:1], "x"))

    def test_small_selection_caps_and_no_auto_labels(self):
        ledger = {"pairs": [{"photoIds": ["p0", "p1"], "label": "same"},
                            {"photoIds": ["p0", "p2"], "label": "different"},
                            {"photoIds": ["p0", "p3"], "label": "uncertain"}]}
        selected, ids = cli.sample_pairs(ledger, {r["photoId"]: r for r in self.state["rows"]},
                                        self.vectors, max_photos=3)
        self.assertEqual([p["label"] for p in selected], ["same", "different"])
        self.assertEqual(len(ids), 3)

    def test_head_context_is_explicitly_face_confounded(self):
        from PIL import Image
        crops = cli.regions(Image.new("RGB", (1000, 1000)), [.4, .2, .15, .15])
        self.assertLess(crops["head-context"][1], 200)
        self.assertGreater(crops["below-face"][1], 350)

    def test_tampered_receipt_does_not_verify(self):
        with mock.patch.object(cli.shadow, "digest", return_value="changed"):
            with self.assertRaisesRegex(ValueError, "changed"):
                cli.verify({str(pathlib.Path.cwd() / "source.json"): "expected"})

    def test_persistent_cue_cache_roundtrip_and_invalidations(self):
        import torch
        from PIL import Image
        with tempfile.TemporaryDirectory(dir=cli.ROOT / "tmp") as name:
            root = pathlib.Path(name)
            source, checkpoint = root / "source.png", root / "model.safetensors"
            Image.new("RGB", (500, 500)).save(source)
            checkpoint.write_bytes(b"fixture local model")
            run = {"workingRoot": str(root), "photos": [
                {"photoId": "p0", "destination": "source.png", "preparedSHA256": "face"}],
                "publishedFiles": [{"path": "source.png", "sha256": cli.shadow.digest(source)}]}
            face_cache = {"emb": {"a": {"box": [.4, .2, .15, .15],
                                      "alignmentEvidence": {"sourceSha256": "face"}}}}
            model = mock.Mock()
            model.encode_image.return_value = torch.tensor([[1., 0.]])
            with mock.patch("open_clip.create_model_and_transforms", return_value=(
                model, None, lambda crop: torch.zeros(3, 224, 224),
            )):
                cold, stats = cli.descriptors(["p0"], run, face_cache, checkpoint, root)
                self.assertEqual(stats["extractions"], 2)
                restored = json.loads(json.dumps(cold))
                warm, stats = cli.descriptors(["p0"], run, face_cache, checkpoint, root, restored)
                self.assertEqual(warm, cold)
                self.assertEqual(stats["extractions"], 0)
                self.assertEqual(stats["decodedImages"], 0)
                face_cache["emb"]["a"]["box"][0] = .3
                _, stats = cli.descriptors(["p0"], run, face_cache, checkpoint, root, restored)
                self.assertEqual(stats["extractions"], 2)
                face_cache["emb"]["a"]["box"][0] = .4
                checkpoint.write_bytes(b"different local model")
                _, stats = cli.descriptors(["p0"], run, face_cache, checkpoint, root, restored)
                self.assertEqual(stats["extractions"], 2)
                Image.new("RGB", (500, 500), "red").save(source)
                with self.assertRaisesRegex(ValueError, "original changed"):
                    cli.descriptors(["p0"], run, face_cache, checkpoint, root, restored)
                run["publishedFiles"][0]["sha256"] = cli.shadow.digest(source)
                _, stats = cli.descriptors(["p0"], run, face_cache, checkpoint, root, restored)
                self.assertEqual(stats["extractions"], 2)


if __name__ == "__main__":
    unittest.main()
