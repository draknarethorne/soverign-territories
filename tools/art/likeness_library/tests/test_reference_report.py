"""Reproducible reference-results presentation and report-only CLI receipts."""
import copy
import json
import unittest
from unittest import mock

from tools.art import likeness_reference_trial as cli
from tools.art.likeness_library import reference_report, shadow
from tools.art.likeness_library.tests import test_review_packet


class ReferenceReportTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_review_packet.PacketTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.result = {
            "characters": [{
                "folder": "Angels/angelica", "baselineReferenceCount": 3,
                "confirmedReferenceCount": 2,
            }],
            "rows": [{
                "photoId": str(i), "currentFolder": self.fixture.folders[i],
                "qualityEligible": True,
                "choiceByCharacter": {"Angels/angelica": "reference"} if i == 0 else {},
                "characterScores": {"Angels/angelica": {
                    "baseline": .4, "confirmed": .3 + i / 20,
                    "baselineSupport": 2, "confirmedSupport": 1,
                }},
                **{name: {
                    "ownScore": .3, "rivals": [{"folder": "Models/Other", "score": .4}],
                    "policyDecision": {"decision": "hold", "reason": "protected"},
                } for name in ("baseline", "confirmed")},
            } for i in range(8)],
            "referenceTransfers": [], "summary": {"photoCount": 8},
            "limits": ["Not held-out accuracy."],
        }
        self.outcomes = {
            "rows": [{
                "photoId": row["photoId"],
                "placement": {
                    "action": "hold", "targetFolder": None, "targetBucket": None,
                    "reason": "<unknown>", "blockers": ["protected"], "policyAgreement": "policy-holds",
                },
                "reference": {"status": "provisional"},
                "policyProbe": {"decision": "hold", "reason": "protected"},
            } for row in self.result["rows"]],
            "summary": {
                "placementActions": {"hold": 8}, "referenceAdditions": 0,
                "referenceWithdrawals": 0, "conflictPhotoCount": 0,
            },
        }

    def test_selection_bounded_deterministic_and_does_not_mutate(self):
        before = copy.deepcopy(self.result)
        ids = reference_report.select_photos(self.result)
        self.assertIn("0", ids)
        self.assertLessEqual(len(ids), 4)
        self.result["rows"].reverse()
        self.assertEqual(ids, reference_report.select_photos(self.result))
        self.result["rows"].reverse()
        self.assertEqual(before, self.result)
        with self.assertRaisesRegex(ValueError, "budget"):
            reference_report.select_photos(self.result, maximum=1)

    def test_render_escapes_text_and_labels_uncertainty_and_policy_boundary(self):
        ids = reference_report.select_photos(self.result)
        display, _ = cli.review_packet.image_assets(
            {"usedPhotoIds": ids}, self.fixture.run, self.fixture.cache, self.root / "no-write",
        )
        self.result["limits"] = ["<script>unsafe</script>"]
        page = reference_report.render(self.result, display)
        self.assertIn("&lt;script&gt;unsafe&lt;/script&gt;", page)
        self.assertNotIn("<script>unsafe</script>", page)
        for expected in ("not another assessment", "NOT held-out", "not a proposed move",
                         "not a completed routing replay", "protected", "self excluded"):
            self.assertIn(expected, page)

    def test_render_member_proposals_escape_and_link_full_ledger(self):
        ids = reference_report.select_photos(self.result)
        display, _ = cli.review_packet.image_assets(
            {"usedPhotoIds": ids}, self.fixture.run, self.fixture.cache, self.root / "no-write",
        )
        page = reference_report.render(self.result, display, outcomes=self.outcomes)
        for expected in ("member-outcomes.json", "Placement proposal: hold", "&lt;unknown&gt;",
                         "not authorized", "not newly inferred identity", "Executable moves: zero"):
            self.assertIn(expected, page)
        self.assertNotIn("<unknown>", page)

    def test_overlap_diagnostics_preserve_unknown_coverage(self):
        baseline = reference_report.evidence_diagnostics(self.result)
        self.assertIsNone(baseline[0]["variants"]["confirmed"]["positiveNegativeRangeOverlap"])
        self.result["rows"][1]["choiceByCharacter"] = {"Angels/angelica": "different"}
        self.result["rows"][2]["choiceByCharacter"] = {"Angels/angelica": "uncertain"}
        diagnostic = reference_report.evidence_diagnostics(self.result)[0]["variants"]["confirmed"]
        self.assertTrue(diagnostic["positiveNegativeRangeOverlap"])
        self.assertEqual(len(diagnostic["different"]), 1)
        self.assertEqual(len(diagnostic["uncertain"]), 1)
        self.assertEqual(diagnostic["sameNonReference"], [])

    def test_profile_diagnostics_do_not_convert_missing_support_to_zero(self):
        self.result["rows"][0]["characterScores"]["Angels/angelica"]["confirmedProfile"] = {
            "nearestScore": .7, "secondScore": None, "topTwoMean": None,
        }
        self.result["rows"][1]["choiceByCharacter"] = {"Angels/angelica": "different"}
        self.result["rows"][1]["characterScores"]["Angels/angelica"]["confirmedProfile"] = {
            "nearestScore": .8, "secondScore": None, "topTwoMean": None,
        }
        profiles = reference_report.evidence_diagnostics(self.result)[0]["confirmedProfiles"]
        self.assertTrue(profiles["nearestScore"]["positiveNegativeRangeOverlap"])
        self.assertIsNone(profiles["secondScore"]["positiveNegativeRangeOverlap"])
        self.assertEqual(profiles["topTwoMean"]["referenceLOO"], [])

    def test_cli_preview_apply_check_repeat_population_guard_and_corruption(self):
        experiment = self.root / "experiment"
        experiment.mkdir()
        (self.root / "likeness-cache.json").write_text(json.dumps(self.fixture.cache))
        answers = {"characters": [{
            "folder": "Angels/angelica", "decisions": [{"photoId": "0", "choice": "reference"}],
        }]}
        packet = self.root / "packet"
        packet.mkdir()
        (packet / "effective-labels.json").write_text("{}")
        input_path = self.root / "answers.json"
        input_path.write_text(json.dumps(answers))
        bindings = {str(input_path): shadow.digest(input_path)}
        out = self.root / "report"
        args = ["--experiment", str(experiment), "--character-packet", str(packet),
                "--answers", str(input_path), "--out", str(out), "--compare-order"]
        before = {path: shadow.digest(path) for path in self.root.rglob("*.png")}
        with (
            mock.patch.object(cli, "verify_inputs", return_value=({}, answers, bindings)),
            mock.patch.object(cli, "output_path", return_value=out),
            mock.patch.object(cli.review_packet, "load_experiment", return_value=(
                self.fixture.run, self.fixture.vectors, {}, self.fixture.binding,
            )),
            mock.patch.object(cli.reference_trial, "evaluate", return_value=self.result),
            mock.patch.object(cli.member_outcomes, "build", return_value=self.outcomes),
        ):
            self.assertEqual(cli.main(args + ["--max-photos", "1"]), 1)
            self.assertFalse(out.exists())
            self.assertEqual(cli.main(args + ["--dry-run"]), 0)
            self.assertFalse(out.exists())
            self.assertEqual(cli.main(args + ["--apply"]), 0)
            self.assertEqual(cli.main(args + ["--check"]), 0)
            original_receipt = shadow.digest(out / "receipt.json")
            self.assertEqual(cli.main(args + ["--apply"]), 0)
            self.assertEqual(shadow.digest(out / "receipt.json"), original_receipt)
            seed = json.loads((out / "reference-seed.json").read_bytes())
            self.assertEqual(seed["characters"][0]["referencePhotoIds"], ["0"])
            self.assertIn("no placement", seed["boundary"])
            ledger = json.loads((out / "member-outcomes.json").read_bytes())
            self.assertEqual(ledger, self.outcomes)
            (out / "member-outcomes.json").write_text("{}")
            self.assertEqual(cli.main(args + ["--check"]), 1)
            (out / "member-outcomes.json").write_text(json.dumps(self.outcomes, indent=2) + "\n")
            (out / "result.json").write_text("{}")
            self.assertEqual(cli.main(args + ["--check"]), 1)
        self.assertEqual(before, {path: shadow.digest(path) for path in before})

    def test_order_mismatch_refuses_before_writing(self):
        packet = self.root / "packet"
        packet.mkdir()
        (packet / "effective-labels.json").write_text("{}")
        out = self.root / "out"
        args = ["--experiment", str(self.root), "--character-packet", str(packet),
                "--answers", str(self.root / "answer.json"), "--out", str(out), "--compare-order", "--apply"]
        with (
            mock.patch.object(cli, "verify_inputs", return_value=({}, {}, {})),
            mock.patch.object(cli, "output_path", return_value=out),
            mock.patch.object(cli.review_packet, "load_experiment", return_value=(
                self.fixture.run, self.fixture.vectors, {}, self.fixture.binding,
            )),
            mock.patch.object(cli.reference_trial, "evaluate", side_effect=[
                self.result, {**copy.deepcopy(self.result), "changed": True},
            ]),
            mock.patch.object(cli.member_outcomes, "build", return_value=self.outcomes),
        ):
            self.assertEqual(cli.main(args), 1)
            self.assertFalse(out.exists())

    def test_relative_inputs_and_nonpositive_population_limit_refuse(self):
        args = ["--experiment", "relative", "--character-packet", str(self.root),
                "--answers", str(self.root / "answer.json"), "--out", str(self.root / "out")]
        self.assertEqual(cli.main(args), 1)
        args[1] = str(self.root)
        self.assertEqual(cli.main(args + ["--max-photos", "0"]), 1)

    def test_opt_in_realignment_receipts_mode_and_corruption(self):
        from tools.art.likeness_library import realignment

        packet = self.root / "candidate-packet"
        packet.mkdir()
        (packet / "effective-labels.json").write_text("{}")
        (self.root / "likeness-cache.json").write_text(json.dumps(self.fixture.cache))
        out = self.root / "candidate-out"
        answers = {"characters": [{
            "folder": "Angels/angelica", "decisions": [{"photoId": "0", "choice": "reference"}],
        }]}
        candidate = {
            "summary": {"photoCount": 8}, "recipe": {}, "limits": [],
            "identities": [{
                "identityId": folder, "folder": folder,
                "referencePhotoIds": ["0"] if folder == "Angels/angelica" else [],
                "referenceStatus": "provisional", "referenceNeeded": folder != "Angels/angelica",
                "appearanceGroupIds": [],
            } for folder in sorted({row["currentFolder"] for row in self.result["rows"]})],
            "appearances": [], "associations": [],
            "rows": [{
                "photoId": row["photoId"], "currentFolder": row["currentFolder"], "candidateFolder": None,
                "state": "unresolved", "origin": "baseline", "referenceEligible": False,
                "reason": "missing evidence", "blockers": [],
                "evidence": {"ownScore": None, "topCandidates": []},
                "reconsiderable": True, "execution": "not-authorized",
            } for row in self.result["rows"]],
        }
        diagnostic = {"summary": {}, "cases": []}
        args = ["--experiment", str(self.root), "--character-packet", str(packet),
                "--answers", str(self.root / "answers.json"), "--out", str(out), "--compare-order"]
        with (
            mock.patch.object(cli, "verify_inputs", return_value=({}, answers, {})),
            mock.patch.object(cli, "output_path", return_value=out),
            mock.patch.object(cli.review_packet, "load_experiment", return_value=(
                self.fixture.run, self.fixture.vectors, {}, self.fixture.binding,
            )),
            mock.patch.object(cli.reference_trial, "evaluate", return_value=self.result),
            mock.patch.object(cli.member_outcomes, "build", return_value=self.outcomes),
            mock.patch.object(realignment, "evaluate", return_value=candidate),
            mock.patch.object(cli.realignment_evaluation, "evaluate", return_value=diagnostic),
            mock.patch.object(cli.realignment_report, "validate_candidate"),
        ):
            self.assertEqual(cli.main(args + ["--realign", "--dry-run"]), 0)
            self.assertFalse(out.exists())
            self.assertEqual(cli.main(args + ["--realign", "--apply"]), 0)
            receipt = (out / "receipt.json").read_bytes()
            self.assertEqual(cli.main(args + ["--realign", "--apply"]), 0)
            self.assertEqual((out / "receipt.json").read_bytes(), receipt)
            self.assertEqual(cli.main(args + ["--realign", "--check"]), 0)
            self.assertEqual(cli.main(args + ["--check"]), 1)
            self.assertEqual(json.loads((out / "realignment.json").read_bytes()), candidate)
            self.assertEqual(json.loads((out / "evaluation.json").read_bytes()), diagnostic)
            (out / "realignment.html").write_text("corrupt")
            self.assertEqual(cli.main(args + ["--realign", "--check"]), 1)


if __name__ == "__main__":
    unittest.main()
