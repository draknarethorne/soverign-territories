"""Reviewed group resemblance cannot certify unreviewed members or execute moves."""
import copy
import json
import math
import pathlib
import tempfile
import unittest
from unittest import mock

import numpy as np

from tools.art import likeness_candidate_replay as cli
from tools.art.likeness_library import fragment_review, split_diagnostics as subject
from tools.art.likeness_library.tests import test_candidate_replay as fixtures


class SplitDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.CandidateReplayTests()
        fixture.setUp()
        self.candidate, self.run, self.ledger = fixture.candidate, fixture.run, fixture.ledger
        self.result = {"rows": fixture.rows()}
        for identity in self.candidate["identities"]:
            identity["referenceEvidence"] = {"construction": "fixture"}
        self.vectors = {
            pid: np.array([math.cos(math.radians(angle)), math.sin(math.radians(angle))])
            for pid, angle in zip(fixture.ids, [0, 40, -20, 10, 40, 170])
        }
        self.packet = {"cases": [{
            "id": "test", "photoId": "q", "currentFolder": "Models/Source",
            "targetFolder": "Models/Target", "currentReferenceId": "own", "targetReferenceIds": ["a", "b"],
        }]}
        self.packet["packetSHA256"] = fragment_review.digest(self.packet)
        self.evaluation = {
            "schemaVersion": 1, "kind": "candidate-recommendation-evaluation",
            "packetSHA256": self.packet["packetSHA256"],
            "candidateSHA256": fragment_review.digest(self.result),
            "identityAnswers": {
                "schemaVersion": 1, "kind": "identity-fragment-answers",
                "packetSHA256": self.packet["packetSHA256"],
                "decisions": [{
                    "caseId": "test", "currentMatch": "same", "targetMatch": "same", "context": "uncertain",
                    "pairs": [{"referencePhotoId": pid, "label": "same"} for pid in ("own", "a", "b")],
                }],
            },
            "recommendations": [{"caseId": "test", "judgment": "agree", "reason": "A split, not every unseen image."}],
        }

    def build(self):
        return subject.build(self.candidate, self.run, self.vectors, self.packet, self.evaluation,
                             self.result, self.ledger)

    def test_complete_members_and_contaminant_visible_despite_high_centroid(self):
        result = self.build()
        pair = result["pairs"][0]
        self.assertEqual(result["summary"]["uniqueMemberCount"], 6)
        self.assertEqual(result["summary"]["directedMemberRows"], 6)
        self.assertGreater(pair["allMemberCentroidScore"], .7)
        self.assertLess(pair["crossMemberPairDistribution"]["minimum"], -.6)
        residual = next(row for direction in pair["directions"] for row in direction["members"] if row["photoId"] == "d")
        self.assertIn("insufficient-independent-opposite-references", residual["diagnosticBlockers"])
        self.assertEqual(residual["directPairEvidence"], [])
        self.assertEqual(pair["wholeGroupCombination"], "not-established")
        self.assertEqual(result["summary"]["executedMoves"], 0)

    def test_member_support_is_directional_not_centroid_threshold(self):
        directions = self.build()["pairs"][0]["directions"]
        self.assertNotEqual(directions[0]["referenceCount"], directions[1]["referenceCount"])
        for direction in directions:
            for row in direction["members"]:
                self.assertEqual(row["execution"], "not-authorized")
                self.assertIn("candidateDecisionAppliesToThisPair", row)
                self.assertEqual(row["requiredSupport"], 4)

    def test_duplicate_content_and_self_do_not_supply_support(self):
        # A confirmed intent reference may reside in another current folder.
        self.candidate["identities"][1]["referencePhotoIds"].append("q")
        self.run["photos"][2]["preparedSHA256"] = self.run["photos"][0]["preparedSHA256"]
        result = self.build()
        row = next(r for r in result["pairs"][0]["directions"][0]["members"] if r["photoId"] == "q")
        self.assertNotEqual(row["bestOppositePhotoId"], "q")
        self.assertNotEqual(row["bestOppositePhotoId"], "a")
        self.assertEqual(result["summary"]["crossPairCount"], 7)
        external = result["pairs"][0]["referenceLocations"]["Models/Target"][-1]
        self.assertEqual(external["photoId"], "q")
        self.assertEqual(external["currentFolder"], "Models/Source")

    def test_negative_or_conflicting_evidence_retains_veto(self):
        self.ledger["pairs"] = [{"photoIds": ["q", "a"], "label": "different"}]
        result = self.build()
        self.assertEqual(result["conflicts"][0]["previous"], "different")
        self.assertEqual(result["pairs"][0]["knownCrossPairs"][0]["label"], "uncertain")
        row = result["pairs"][0]["directions"][0]["members"][1]
        self.assertEqual(row["photoId"], "q")
        self.assertIn("direct-different-or-uncertain-pair", row["diagnosticBlockers"])

    def test_absent_and_invalid_measurements_and_quality_are_explicit(self):
        del self.vectors["q"]
        with self.assertRaisesRegex(ValueError, "missing measurement"):
            self.build()
        self.run["finalMembershipAudit"]["rows"][0]["qualityEligible"] = False
        result = self.build()
        row = result["pairs"][0]["directions"][0]["members"][1]
        self.assertIsNone(row["crossReferenceCentroidScore"])
        self.assertIn("saved-quality-gate", row["diagnosticBlockers"])
        self.vectors["q"] = np.array([float("nan"), 1.])
        with self.assertRaisesRegex(ValueError, "invalid normalized"):
            self.build()

    def test_no_transitive_group_or_pair_inference(self):
        self.evaluation["identityAnswers"]["decisions"][0]["targetMatch"] = "different"
        with self.assertRaisesRegex(ValueError, "explicitly supported"):
            self.build()
        self.setUp()
        # Repeated/direct matches do not create any additional group or pair union.
        result = self.build()
        self.assertEqual(result["summary"]["groupPairCount"], 1)
        self.assertEqual(len(result["pairs"][0]["knownCrossPairs"]), 2)
        third = "Models/Third"
        photo = {**self.run["photos"][0], "photoId": "z", "preparedSHA256": "hash-z",
                 "destination": third + "/gallery/z.jpg"}
        self.run["photos"].append(photo)
        self.run["finalMembershipAudit"]["rows"].append({
            **self.run["finalMembershipAudit"]["rows"][0], **photo,
        })
        self.candidate["rows"].append({"photoId": "z", "currentFolder": third})
        self.candidate["identities"].append({
            "folder": third, "referencePhotoIds": ["z"], "referenceEvidence": {"construction": "fixture"},
        })
        self.result["rows"].append({**self.result["rows"][0], "photoId": "z"})
        self.vectors["z"] = self.vectors["a"].copy()
        self.packet["cases"].append({
            "id": "second", "photoId": "a", "currentFolder": "Models/Target", "targetFolder": third,
            "currentReferenceId": "b", "targetReferenceIds": ["z"],
        })
        self.evaluation["identityAnswers"]["decisions"].append({
            **self.evaluation["identityAnswers"]["decisions"][0], "caseId": "second",
            "pairs": [{"referencePhotoId": "z", "label": "same"}, {"referencePhotoId": "b", "label": "same"}],
        })
        result = self.build()
        self.assertEqual(result["summary"]["groupPairCount"], 2)
        self.assertNotIn(["Models/Source", third], [pair["folders"] for pair in result["pairs"]])
        self.assertFalse(any(item["photoIds"] == ["q", "z"]
                             for pair in result["pairs"] for item in pair["knownCrossPairs"]))

    def test_order_and_inputs_preserved_and_budget_guarded(self):
        original = copy.deepcopy((self.candidate, self.run, self.evaluation))
        result = self.build()
        self.assertEqual(original, (self.candidate, self.run, self.evaluation))
        self.candidate["rows"].reverse()
        self.candidate["identities"].reverse()
        self.run["photos"].reverse()
        self.result["rows"].reverse()
        for identity in self.candidate["identities"]:
            identity["referencePhotoIds"].reverse()
        self.assertEqual(result, self.build())
        with mock.patch.object(subject, "MAX_MEMBERS", 1):
            with self.assertRaisesRegex(ValueError, "member cap"):
                self.build()
        with mock.patch.object(subject, "MAX_PAIRS", 1):
            with self.assertRaisesRegex(ValueError, "cross-pair cap"):
                self.build()

    def test_stale_population_and_missing_reference_fail_explicitly(self):
        self.result["rows"].pop()
        with self.assertRaisesRegex(ValueError, "conservation"):
            self.build()
        self.setUp()
        self.candidate["identities"][0]["referencePhotoIds"].append("unknown")
        with self.assertRaisesRegex(ValueError, "absent from frozen"):
            self.build()

    def test_render_escapes_notes_and_explains_metrics_and_scope(self):
        self.evaluation["recommendations"][0]["reason"] = "<script>unsafe</script>"
        page = subject.render(self.build(), {})
        self.assertNotIn("<script>unsafe</script>", page)
        self.assertIn("&lt;script&gt;unsafe&lt;/script&gt;", page)
        for text in ("No whole-group combination", "not probabilities", "Every member",
                     "What the saved run actually recorded", "NOT a count approved to move"):
            self.assertIn(text, page)

    def test_cli_preview_apply_repeat_check_and_corruption(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            root = pathlib.Path(name)
            out = root / "report"
            evaluation = root / "evaluation.json"
            evaluation.write_text(json.dumps(self.evaluation), encoding="utf-8")
            loaded = (self.packet, self.ledger, self.candidate, self.run, self.vectors, {}, root / "model", {})
            reused = (self.result, self.packet, {}, {})
            args = ["--source", str(root), "--reuse-result", str(root / "old"),
                    "--out", str(out), "--split-evaluation", str(evaluation)]
            with mock.patch.object(cli, "load", return_value=loaded), \
                    mock.patch.object(cli, "reuse", return_value=reused), \
                    mock.patch.object(cli, "output_path", return_value=out), \
                    mock.patch.object(cli, "codes", return_value={}), \
                    mock.patch.object(cli.review_packet, "image_assets", return_value=({}, {})), \
                    mock.patch.object(cli.fragment_evidence, "evaluate") as score, \
                    mock.patch.object(cli.appearance_context, "measure") as model:
                self.assertEqual(cli.main(args + ["--dry-run"]), 0)
                self.assertFalse(out.exists())
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                saved = (out / "receipt.json").read_bytes()
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                self.assertEqual(cli.main(args + ["--check"]), 0)
                self.assertEqual(saved, (out / "receipt.json").read_bytes())
                score.assert_not_called()
                model.assert_not_called()
                (out / "index.html").write_text("corrupted", encoding="utf-8")
                self.assertEqual(cli.main(args + ["--check"]), 1)
                evaluation.write_text("{}", encoding="utf-8")
                self.assertEqual(cli.main(args + ["--check"]), 1)


if __name__ == "__main__":
    unittest.main()
