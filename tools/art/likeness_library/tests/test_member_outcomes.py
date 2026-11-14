"""Member/reference proposals conserve evidence without authorizing library changes."""
import copy
import json
import unittest

from tools.art.likeness_library import member_outcomes
from tools.art.likeness_library.tests import test_reference_trial


class MemberOutcomeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_reference_trial.ReferenceTrialTests()
        self.fixture.setUp()
        self.fixture.labels = {"pairs": []}
        self.result = self.fixture.evaluate()
        self.run = self.fixture.run

    def build(self):
        return member_outcomes.build(self.result, self.run)

    def row(self, pid):
        return next(row for row in self.build()["rows"] if row["photoId"] == pid)

    def test_conservation_order_and_inputs_unchanged(self):
        before = copy.deepcopy((self.result, self.run))
        value = self.build()
        self.assertEqual(value["summary"]["photoCount"], len(self.run["photos"]))
        self.assertEqual(value["summary"]["executableMoves"], 0)
        self.assertTrue(all(row["placement"]["execution"] == "not-authorized" for row in value["rows"]))
        self.assertEqual(before, (self.result, self.run))
        self.result["rows"].reverse()
        self.result["characters"].reverse()
        self.run["photos"].reverse()
        self.run["finalMembershipAudit"]["rows"].reverse()
        self.assertEqual(value, self.build())
        json.dumps(value, allow_nan=False)

    def test_reference_recovery_withdraws_old_influence_without_moving(self):
        row = self.row("x")
        self.assertEqual(row["currentFolder"], self.fixture.outside)
        self.assertEqual(row["reference"]["baselineFolders"], [self.fixture.outside])
        self.assertEqual(row["reference"]["proposedFolders"], [self.fixture.a])
        self.assertEqual(row["placement"]["action"], "recover")
        self.assertEqual(row["placement"]["targetFolder"], self.fixture.a)
        self.assertEqual(row["placement"]["policyAgreement"], "policy-holds")

    def test_reference_withdrawal_does_not_override_protected_placement(self):
        saved = next(row for row in self.run["finalMembershipAudit"]["rows"] if row["photoId"] == "b0")
        saved.update(protected=True, workflowSelected=True)
        row = self.row("b0")
        self.assertEqual(row["placement"]["action"], "reassess")
        self.assertIsNone(row["placement"]["targetFolder"])
        self.assertIn("protected", row["placement"]["blockers"])
        self.assertIn("workflowSelected", row["placement"]["blockers"])
        self.assertEqual(row["reference"]["proposedFolders"], [])
        self.assertTrue(any(not change["after"] for change in row["reference"]["changes"]))

    def test_same_not_reference_can_recover_without_reference_promotion(self):
        saved = next(row for row in self.run["finalMembershipAudit"]["rows"] if row["photoId"] == "a2")
        photo = next(row for row in self.run["photos"] if row["photoId"] == "a2")
        photo["destination"] = saved["destination"] = "Models/Other/gallery/a2.png"
        next(row for row in self.result["rows"] if row["photoId"] == "a2")["currentFolder"] = "Models/Other"
        row = self.row("a2")
        self.assertEqual(row["placement"]["action"], "recover")
        self.assertEqual(row["placement"]["targetFolder"], self.fixture.a)
        self.assertEqual(row["reference"]["proposedFolders"], [])
        self.assertEqual(row["reference"]["changes"][0]["folder"], "Models/Other")
        self.assertFalse(row["reference"]["changes"][0]["after"])

    def test_uncertainty_is_not_negative_and_unknowns_abstain(self):
        hold = self.row("hold")
        self.assertEqual(hold["characterIntent"][self.fixture.a], "uncertain")
        self.assertEqual(hold["placement"]["action"], "hold")
        self.assertIsNone(hold["placement"]["targetFolder"])
        self.assertIn("quality-ineligible", hold["placement"]["blockers"])
        row = next(row for row in self.result["rows"] if row["photoId"] == "c0")
        row["confirmed"]["policyDecision"] = {"decision": "hold", "reason": "no higher rival"}
        self.assertEqual(self.row("c0")["placement"]["action"], "hold")
        self.assertEqual(self.row("c0")["reference"]["status"], "provisional")

    def test_direct_pairs_are_not_character_labels_or_reference_growth(self):
        self.result["pairEvidence"] = [
            {"photoIds": ["c0", "a0"], "label": "same"},
            {"photoIds": ["c1", "c0"], "label": "same"},
        ]
        for row in self.result["rows"]:
            row["confirmed"]["policyDecision"] = {"decision": "hold", "reason": "test gate"}
        c0 = self.row("c0")
        self.assertEqual(c0["placement"]["action"], "hold")
        self.assertEqual(c0["characterIntent"], {})
        self.assertNotIn(self.fixture.a, c0["reference"]["proposedFolders"])
        self.assertEqual(c0["directReferenceEvidence"][0]["samePhotoIds"], ["a0"])
        self.assertEqual(self.row("c1")["directReferenceEvidence"], [])

    def test_query_content_cannot_certify_reference_evidence(self):
        self.result["pairEvidence"] = [{"photoIds": ["c0", "a0"], "label": "same"}]
        for photo in self.run["photos"]:
            if photo["photoId"] == "c0":
                photo["preparedSHA256"] = "hash-a0"
        evidence = self.row("c0")["directReferenceEvidence"][0]
        self.assertEqual(evidence["samePhotoIds"], [])
        self.assertEqual(evidence["excludedSameContentPhotoIds"], ["a0"])
        self.assertEqual(evidence["state"], "no-independent-pair-evidence")

    def test_conflicting_pair_and_character_intent_abstains_and_blocks_reference(self):
        self.result["pairEvidence"] = [{"photoIds": ["a0", "a1"], "label": "different"}]
        for pid in ("a0", "a1"):
            row = self.row(pid)
            self.assertEqual(row["placement"]["action"], "hold")
            self.assertIsNone(row["placement"]["targetFolder"])
            self.assertEqual(row["reference"]["proposedFolders"], [])
            self.assertIn("human-evidence-conflict", row["placement"]["blockers"])
            self.assertIn(self.fixture.a, row["reference"]["blockedAdmissions"])

    def test_multiple_positive_characters_are_not_silently_resolved(self):
        next(row for row in self.result["rows"] if row["photoId"] == "x")[
            "choiceByCharacter"
        ][self.fixture.b] = "same-not-reference"
        row = self.row("x")
        self.assertEqual(row["placement"]["action"], "hold")
        self.assertIsNone(row["placement"]["targetFolder"])
        self.assertEqual(row["reference"]["proposedFolders"], [])

    def test_reference_protection_is_not_reference_eligibility(self):
        saved = next(row for row in self.run["finalMembershipAudit"]["rows"] if row["photoId"] == "a0")
        saved.update(protected=True, anchor=True, identityProtected=True)
        self.assertEqual(self.row("a0")["reference"]["proposedFolders"], [self.fixture.a])
        saved["metadataStale"] = True
        self.assertEqual(self.row("a0")["reference"]["proposedFolders"], [])
        self.assertIn("metadataStale", self.row("a0")["placement"]["blockers"])

    def test_cross_character_recovery_surfaces_ownership_even_without_lock(self):
        saved = next(row for row in self.run["finalMembershipAudit"]["rows"] if row["photoId"] == "x")
        photo = next(row for row in self.run["photos"] if row["photoId"] == "x")
        photo["destination"] = saved["destination"] = f"{self.fixture.b}/gallery/x.png"
        next(row for row in self.result["rows"] if row["photoId"] == "x")["currentFolder"] = self.fixture.b
        row = self.row("x")
        self.assertFalse(row["safeguards"]["identityProtected"])
        self.assertEqual(row["placement"]["action"], "recover")
        self.assertIn("source-character-ownership", row["placement"]["blockers"])

    def test_evidence_keeps_scores_support_and_missingness_separate_from_intent(self):
        row = self.row("x")
        source = next(row for row in self.result["rows"] if row["photoId"] == "x")
        self.assertEqual(row["frozenComparison"], source["confirmed"])
        self.assertEqual(row["characterEvidence"][self.fixture.a], source["characterScores"][self.fixture.a])
        self.assertIn("no-direct-reference-pair-evidence", row["evidenceGaps"])
        self.assertNotIn("no-explicit-positive-character-intent", row["evidenceGaps"])
        self.assertIn("no-quality-eligible-measurement", self.row("hold")["evidenceGaps"])

    def test_policy_proposal_cannot_override_negative_or_uncertain_intent(self):
        row = next(row for row in self.result["rows"] if row["photoId"] == "c0")
        row["confirmed"]["policyDecision"] = {
            "decision": "move", "destination": f"{self.fixture.a}/review", "reason": "test",
        }
        self.assertEqual(self.row("c0")["placement"]["action"], "policy-proposal")
        for choice in ("different", "uncertain"):
            row["choiceByCharacter"] = {self.fixture.a: choice}
            actual = self.row("c0")
            self.assertEqual(actual["placement"]["action"], "hold")
            self.assertIsNone(actual["placement"]["targetFolder"])

    def test_binding_errors_refuse_instead_of_dropping_rows(self):
        for change in ("missing-row", "duplicate-row", "destination", "quality", "choice", "reference-ids"):
            with self.subTest(change=change):
                result, run = copy.deepcopy((self.result, self.run))
                if change == "missing-row":
                    result["rows"].pop()
                elif change == "duplicate-row":
                    result["rows"].append(copy.deepcopy(result["rows"][0]))
                elif change == "destination":
                    run["photos"][0]["destination"] = "Models/Else/gallery/a0.png"
                elif change == "quality":
                    result["rows"][0]["qualityEligible"] = not result["rows"][0]["qualityEligible"]
                elif change == "choice":
                    result["rows"][0]["choiceByCharacter"] = {"unknown": "different"}
                else:
                    result["characters"][0]["referenceIds"].append("unknown")
                with self.assertRaises(ValueError):
                    member_outcomes.build(result, run)

    def test_policy_proposal_abstains_on_direct_negative_reference_evidence(self):
        self.result["pairEvidence"] = [{"photoIds": ["c0", "a0"], "label": "different"}]
        next(row for row in self.result["rows"] if row["photoId"] == "c0")["confirmed"]["policyDecision"] = {
            "decision": "move", "destination": f"{self.fixture.a}/review", "reason": "test",
        }
        row = self.row("c0")
        self.assertEqual(row["placement"]["action"], "hold")
        self.assertIsNone(row["placement"]["targetFolder"])
        self.assertEqual(row["characterIntent"], {})


if __name__ == "__main__":
    unittest.main()
