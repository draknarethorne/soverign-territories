"""Tests for the shared, declarative likeness policy."""
import copy
import pathlib
import sys
import unittest

from jsonschema import Draft7Validator

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.art.likeness_library.policy import (  # noqa: E402
    DEFAULT_POLICY_PATH,
    classify_category,
    evaluate_identity_action,
    evaluate_photo_consistency,
    evaluate_photo_route,
    load_policy,
    render_policy_panel,
    score_band,
    validate_policy,
)


class LikenessPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_policy()

    def test_versioned_policy_matches_its_schema(self):
        schema_path = ROOT / "data" / "art" / "_schema" / "likeness-engine-policy.schema.json"
        schema = __import__("json").loads(schema_path.read_text(encoding="utf-8"))
        errors = list(Draft7Validator(schema).iter_errors(self.policy))
        self.assertEqual(errors, [])
        self.assertEqual(DEFAULT_POLICY_PATH, ROOT / "data" / "art" / "likeness-engine-policy.json")

    def test_score_bands_use_existing_gallery_boundaries(self):
        self.assertEqual(score_band(0.55, self.policy), "green")
        self.assertEqual(score_band(0.5499, self.policy), "yellow")
        self.assertEqual(score_band(0.30, self.policy), "yellow")
        self.assertEqual(score_band(0.2999, self.policy), "orange")
        self.assertEqual(score_band(0.15, self.policy), "orange")
        self.assertEqual(score_band(0.1499, self.policy), "red")

    def test_classification_preserves_potential_and_model_boundaries(self):
        self.assertEqual(classify_category(4, 0.50, self.policy)["category"], "Potentials")
        self.assertEqual(classify_category(5, 0.39, self.policy)["category"], "Prospects")
        self.assertEqual(classify_category(5, 0.40, self.policy)["category"], "Models")
        self.assertEqual(classify_category(5, 0.5499, self.policy)["category"], "Models")
        high_cast = classify_category(5, 0.55, self.policy)
        self.assertEqual(high_cast["category"], "Review")
        self.assertTrue(high_cast["reviewRequired"])

    def test_potential_similarity_at_yellow_prompts_visual_review(self):
        self.assertEqual(
            self.policy["lookalikeGroups"]["suggestionMinimumSimilarity"],
            0.30,
        )
        self.assertFalse(self.policy["lookalikeGroups"]["automaticAssociationEnabled"])
        self.assertEqual(
            self.policy["identityActions"]["identityClusterMinimumSimilarity"],
            0.55,
        )
        result = evaluate_identity_action(
            "merge",
            "Potentials",
            score=0.30,
            margin=0.0,
            evidence_count=1,
            policy=self.policy,
        )
        self.assertEqual(result["decision"], "review")

    def test_category_rules_distinguish_core_membership_from_review_actions(self):
        orange_potential = evaluate_photo_consistency(
            "Prospects",
            score=0.20,
            usable_photo_count=4,
            policy=self.policy,
        )
        self.assertTrue(orange_potential["coreMember"])
        self.assertEqual(orange_potential["decision"], "review")

        red_potential = evaluate_photo_consistency(
            "Potentials",
            score=0.10,
            usable_photo_count=4,
            policy=self.policy,
        )
        self.assertFalse(red_potential["coreMember"])
        self.assertEqual(red_potential["decision"], "split-review")

        red_single = evaluate_photo_consistency(
            "Potentials",
            score=None,
            usable_photo_count=1,
            policy=self.policy,
        )
        self.assertTrue(red_single["coreMember"])
        self.assertEqual(red_single["decision"], "keep")

        orange_sister = evaluate_photo_consistency(
            "Sisters",
            score=0.20,
            usable_photo_count=4,
            policy=self.policy,
        )
        self.assertFalse(orange_sister["coreMember"])
        self.assertEqual(orange_sister["decision"], "keep")

        red_sister = evaluate_photo_consistency(
            "Sisters",
            score=0.10,
            usable_photo_count=4,
            policy=self.policy,
        )
        self.assertEqual(red_sister["decision"], "review")

        workflow_photo = evaluate_photo_consistency(
            "Sisters",
            score=0.10,
            usable_photo_count=4,
            workflow_selected=True,
            policy=self.policy,
        )
        self.assertEqual(workflow_photo["decision"], "keep")

    def test_draft_never_automates_and_approval_requires_all_merge_evidence(self):
        args = {
            "action": "merge",
            "category": "Potentials",
            "score": 0.60,
            "margin": 0.15,
            "evidence_count": 2,
        }
        self.assertEqual(evaluate_identity_action(**args, policy=self.policy)["decision"], "review")

        approved = copy.deepcopy(self.policy)
        approved["status"] = "approved"
        self.assertEqual(
            evaluate_identity_action(**args, policy=approved)["decision"],
            "auto-merge",
        )
        self.assertEqual(
            evaluate_identity_action(
                **{**args, "margin": 0.05}, policy=approved
            )["decision"],
            "review",
        )
        self.assertEqual(
            evaluate_identity_action(
                **{**args, "evidence_count": 1}, policy=approved
            )["decision"],
            "review",
        )

    def test_protection_blocks_automatic_actions(self):
        approved = copy.deepcopy(self.policy)
        approved["status"] = "approved"
        decision = evaluate_identity_action(
            "merge",
            "Prospects",
            score=0.80,
            margin=0.20,
            evidence_count=3,
            identity_protected=True,
            policy=approved,
        )
        self.assertEqual(decision["decision"], "blocked")
        photo_decision = evaluate_identity_action(
            "merge",
            "Prospects",
            score=0.80,
            margin=0.20,
            evidence_count=3,
            photo_protected=True,
            policy=approved,
        )
        self.assertEqual(photo_decision["decision"], "keep")
        self.assertEqual(
            evaluate_identity_action(
                "merge",
                "Sisters",
                score=0.80,
                margin=0.20,
                evidence_count=3,
                policy=approved,
            )["decision"],
            "blocked",
        )

    def test_split_requires_low_score_alternative_evidence_and_approval(self):
        args = {
            "action": "split",
            "category": "Potentials",
            "score": 0.10,
            "margin": 0.25,
            "evidence_count": 2,
        }
        self.assertEqual(evaluate_identity_action(**args, policy=self.policy)["decision"], "review")
        approved = copy.deepcopy(self.policy)
        approved["status"] = "approved"
        self.assertEqual(
            evaluate_identity_action(**args, policy=approved)["decision"],
            "auto-split",
        )
        self.assertEqual(
            evaluate_identity_action(
                **{**args, "margin": 0.05}, policy=approved
            )["decision"],
            "review",
        )

    def test_invalid_category_or_band_configuration_is_rejected(self):
        invalid = copy.deepcopy(self.policy)
        invalid["categoryPolicies"].pop("Potentials")
        with self.assertRaisesRegex(ValueError, "categoryPolicies"):
            validate_policy(invalid)
        invalid = copy.deepcopy(self.policy)
        invalid["scoreBands"]["yellow"]["minimum"] = 0.60
        with self.assertRaisesRegex(ValueError, "score band minima"):
            validate_policy(invalid)

    def test_gallery_panel_discloses_all_policy_values(self):
        panel = render_policy_panel(self.policy)
        self.assertIn("Draft - review only", panel)
        self.assertIn("&quot;autoMergeMinimum&quot;: 0.55", panel)
        self.assertIn("&quot;identityBlocksAutomaticMoves&quot;: true", panel)

    def test_photo_routing_uses_draft_review_and_protection_boundaries(self):
        self.assertEqual(
            evaluate_photo_route(
                "Prospects", score=0.40, margin=0.15, policy=self.policy
            )["decision"],
            "review",
        )
        approved = copy.deepcopy(self.policy)
        approved["status"] = "approved"
        self.assertEqual(
            evaluate_photo_route(
                "Prospects", score=0.60, margin=0.15, policy=approved
            )["decision"],
            "auto-route",
        )
        self.assertEqual(
            evaluate_photo_route(
                "Prospects", score=0.60, margin=0.15, identity_protected=True,
                policy=approved,
            )["decision"],
            "blocked",
        )
        self.assertEqual(
            evaluate_photo_route(
                "Prospects", score=0.60, margin=0.15, photo_protected=True,
                policy=approved,
            )["decision"],
            "keep",
        )


if __name__ == "__main__":
    unittest.main()
