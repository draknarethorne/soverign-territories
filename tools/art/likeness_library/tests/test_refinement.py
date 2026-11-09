"""Bounded refinement moves misfit photos and merges converging identities, deterministically."""
import copy
import json
import unittest

import numpy as np

from tools.art.likeness_library import refinement
from tools.art.likeness_library.policy import load_policy

DIM = 32


def basis(index):
    vector = np.zeros(DIM)
    vector[index] = 1.
    return vector


def near(direction, seed, noise=.05):
    rng = np.random.default_rng(seed)
    vector = direction + rng.normal(0, noise, DIM)
    return vector / np.linalg.norm(vector)


A, B, C, X = basis(0), basis(1), basis(2), basis(3)


class RefinementTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_policy()
        self.candidates, self.assignments, self.clusters, self.held = [], [], [], []
        self.cores = {"Angels/Xena": {"vector": X, "side": "Prospects", "category": "Angels", "personIds": []}}

    def photo(self, photo_id, vector, **extra):
        self.candidates.append({
            "photoId": photo_id, "sourceFolder": "Various", "sourceBucket": "Pool",
            "side": "Prospects", "vector": vector, "rejectedPersonIds": [], **extra,
        })

    def cluster(self, destination, members):
        for photo_id, vector in members:
            self.photo(photo_id, vector)
            self.assignments.append({
                "photoId": photo_id, "sourceFolder": "Various", "sourceBucket": "Pool",
                "clusterId": destination, "reason": "new coherent identity",
                "destination": destination, "destinationType": "provisional",
            })
        self.clusters.append({
            "clusterId": destination.replace("/", "-"), "destination": destination,
            "destinationType": "provisional", "photoIds": sorted(photo_id for photo_id, _ in members),
            "corePhotoIds": sorted(photo_id for photo_id, _ in members), "reason": "new coherent identity",
        })

    def run_refine(self, **kwargs):
        result = {"assignments": self.assignments, "held": self.held, "clusters": self.clusters}
        before = copy.deepcopy(result)
        refined, evidence = refinement.refine(result, self.candidates, self.cores, self.policy, **kwargs)
        self.assertEqual(result, before, "refine must not mutate its inputs")
        return refined, evidence

    @staticmethod
    def destination_of(result, photo_id):
        for row in result["assignments"]:
            if row["photoId"] == photo_id:
                return row["destination"]
        for row in result["held"]:
            if row["photoId"] == photo_id:
                return row.get("reviewDestination") or "Various/review"
        raise AssertionError(photo_id)

    def two_identities_with_misfit(self):
        self.cluster("Potentials/Alpha Ann", [
            ("photo:a1", near(A, 1)), ("photo:a2", near(A, 2)), ("photo:a3", near(A, 3)),
            ("photo:m", near(B, 4)),
        ])
        self.cluster("Potentials/Beta Bee", [
            ("photo:b1", near(B, 5)), ("photo:b2", near(B, 6)), ("photo:b3", near(B, 7)),
        ])

    def test_misfit_photo_moves_to_identity_it_fits(self):
        self.two_identities_with_misfit()
        refined, evidence = self.run_refine()
        self.assertEqual(self.destination_of(refined, "photo:m"), "Potentials/Beta Bee")
        self.assertEqual(evidence["moveCount"], 1)
        self.assertEqual(evidence["mergeCount"], 0)
        self.assertEqual(evidence["stopReason"], "stable")
        move = evidence["passes"][0]["moves"][0]
        self.assertEqual((move["from"], move["to"], move["kind"]),
                         ("Potentials/Alpha Ann", "Potentials/Beta Bee", "photo-move"))
        row = next(row for row in refined["assignments"] if row["photoId"] == "photo:m")
        self.assertEqual(row["refinement"][0]["pass"], 1)
        clusters = {group["destination"]: group for group in refined["clusters"]}
        self.assertIn("photo:m", clusters["Potentials/Beta Bee"]["photoIds"])
        self.assertNotIn("photo:m", clusters["Potentials/Alpha Ann"]["photoIds"])
        self.assertEqual(len(refined["assignments"]) + len(refined["held"]), len(self.candidates))

    def test_pass_limit_is_reported_and_output_is_deterministic(self):
        self.two_identities_with_misfit()
        first = self.run_refine(max_passes=1)
        second = self.run_refine(max_passes=1)
        self.assertEqual(first[1]["stopReason"], "pass-limit")
        self.assertEqual(json.dumps(first, default=str, sort_keys=True),
                         json.dumps(second, default=str, sort_keys=True))
        json.dumps(first[1])

    def test_converging_identities_merge_into_larger_survivor(self):
        self.cluster("Potentials/Alpha Ann", [
            ("photo:a1", near(A, 1)), ("photo:a2", near(A, 2)), ("photo:a3", near(A, 3)),
        ])
        self.cluster("Potentials/Alpha Two", [("photo:a4", near(A, 4)), ("photo:a5", near(A, 5))])
        self.cluster("Potentials/Gamma Gee", [
            ("photo:c1", near(C, 6)), ("photo:c2", near(C, 7)), ("photo:c3", near(C, 8)),
        ])
        refined, evidence = self.run_refine()
        self.assertEqual(evidence["mergeCount"], 1)
        merge = evidence["passes"][0]["merges"][0]
        self.assertEqual((merge["survivor"], merge["loser"]), ("Potentials/Alpha Ann", "Potentials/Alpha Two"))
        # Five photos now classify as Prospects; the survivor's identity follows its final membership.
        destinations = {self.destination_of(refined, f"photo:a{n}") for n in range(1, 6)}
        self.assertEqual(destinations, {"Prospects/Alpha Ann"})
        clusters = {group["destination"]: group for group in refined["clusters"]}
        self.assertEqual(set(clusters), {"Prospects/Alpha Ann", "Potentials/Gamma Gee"})
        self.assertEqual(clusters["Prospects/Alpha Ann"]["mergedClusterIds"], ["Potentials-Alpha Two"])
        self.assertEqual(evidence["passes"][0]["reclassified"],
                         [{"from": "Potentials/Alpha Ann", "to": "Prospects/Alpha Ann"}])

    def test_rejection_history_refuses_merge(self):
        self.cluster("Potentials/Alpha Ann", [
            ("photo:a1", near(A, 1)), ("photo:a2", near(A, 2)), ("photo:a3", near(A, 3)),
        ])
        self.cluster("Potentials/Alpha Two", [("photo:a4", near(A, 4)), ("photo:a5", near(A, 5))])
        self.candidates[3]["rejectedPersonIds"] = ["person_" + "9" * 32]
        refined, evidence = self.run_refine()
        self.assertEqual(evidence["mergeCount"], 0)
        self.assertEqual(evidence["unresolved"][0]["kind"], "merge-refused")
        self.assertEqual(self.destination_of(refined, "photo:a4"), "Potentials/Alpha Two")

    def test_locked_photo_stays_and_is_reported(self):
        self.two_identities_with_misfit()
        refined, evidence = self.run_refine(locked_ids={"photo:m"})
        self.assertEqual(self.destination_of(refined, "photo:m"), "Potentials/Alpha Ann")
        self.assertEqual(evidence["moveCount"], 0)
        self.assertEqual([row["kind"] for row in evidence["unresolved"]], ["locked"])

    def test_protected_core_member_stays_under_rebase_minimum(self):
        lookalike = A + 1.2 * B
        members = [(f"photo:a{n}", near(A, n, .02)) for n in range(1, 6)]
        members.append(("photo:x", lookalike / np.linalg.norm(lookalike)))
        self.cluster("Prospects/Alpha Ann", members)
        self.cluster("Potentials/Beta Bee", [
            ("photo:b1", near(B, 11)), ("photo:b2", near(B, 12)), ("photo:b3", near(B, 13)),
        ])
        refined, _ = self.run_refine()
        self.assertEqual(self.destination_of(refined, "photo:x"), "Potentials/Beta Bee")
        self.policy = copy.deepcopy(self.policy)
        self.policy["rebaseProtection"] = {
            "enabled": True, "minimumOwnCoreSimilarities": {"Prospects": .60, "Potentials": None},
        }
        self.policy["groupCastReviewEnabled"] = True
        refined, evidence = self.run_refine()
        self.assertEqual(self.destination_of(refined, "photo:x"), "Prospects/Alpha Ann")
        self.assertEqual(evidence["moveCount"], 0)
        self.policy["groupCastReviewEnabled"] = False
        refined, evidence = self.run_refine()
        self.assertEqual(self.destination_of(refined, "photo:x"), "Potentials/Beta Bee")
        self.assertEqual(evidence["moveCount"], 1)

    def test_cast_lookalike_moves_to_cast_review_not_gallery(self):
        self.cluster("Potentials/Alpha Ann", [
            ("photo:a1", near(A, 1)), ("photo:a2", near(A, 2)), ("photo:a3", near(A, 3)),
            ("photo:x", near(X, 4)),
        ])
        refined, evidence = self.run_refine()
        self.assertEqual(self.destination_of(refined, "photo:x"), "Angels/Xena/review")
        self.assertEqual(evidence["passes"][0]["moves"][0]["to"], "Angels/Xena/review")

    def test_held_review_photo_attaches_when_it_qualifies(self):
        self.two_identities_with_misfit()
        self.photo("photo:h", near(A, 21))
        self.held.append({
            "photoId": "photo:h", "sourceFolder": "Various", "sourceBucket": "Pool",
            "reason": "existing identity match needs review",
        })
        refined, evidence = self.run_refine()
        self.assertEqual(self.destination_of(refined, "photo:h"), "Potentials/Alpha Ann")
        self.assertIn("review-attach", {move["kind"] for item in evidence["passes"] for move in item["moves"]})

    def test_rename_evidence_uses_final_identity_names(self):
        self.two_identities_with_misfit()
        refined, evidence = self.run_refine()
        names = {"Potentials/Beta Bee": "Potentials/Bianca Bell"}
        refinement.rename_evidence(evidence, names)
        refinement.rename_steps(refined["assignments"], names)
        self.assertEqual(evidence["passes"][0]["moves"][0]["to"], "Potentials/Bianca Bell")
        row = next(row for row in refined["assignments"] if row["photoId"] == "photo:m")
        self.assertEqual(row["refinement"][0]["to"], "Potentials/Bianca Bell")

    def test_automatic_cast_review_keeps_recovery_path_but_manual_review_does_not(self):
        self.two_identities_with_misfit()
        for photo_id in ("photo:auto", "photo:manual"):
            self.photo(photo_id, near(A, 21))
            self.held.append({
                "photoId": photo_id, "sourceFolder": "Various", "sourceBucket": "Pool",
                "reason": "cast resemblance", "reviewDestination": "Angels/Xena/review",
                "automaticReviewAssociation": photo_id == "photo:auto",
            })
        refined, evidence = self.run_refine()
        self.assertEqual(self.destination_of(refined, "photo:auto"), "Potentials/Alpha Ann")
        self.assertEqual(self.destination_of(refined, "photo:manual"), "Angels/Xena/review")
        moves = [move for item in evidence["passes"] for move in item["moves"]
                 if move["photoId"] == "photo:auto"]
        self.assertEqual(moves[0]["from"], "Angels/Xena/review")


class FinalMembershipRefinementTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_policy()
        self.comparison = {
            "photoId": "photo:123456", "ambiguousPhotoId": False,
            "qualityEligible": True, "metadataStale": False, "protected": False, "anchor": False,
            "workflowSelected": False, "identityProtected": False, "rejectionHistory": False,
            "bucket": "gallery", "ownScore": .6, "higherRival": True,
            "rivals": [{"folder": "Models/Beta Bee", "score": .8}],
            "refinementTarget": {
                "folder": "Models/Beta Bee", "score": .8, "independentSupport": 4,
                "identityProtected": False,
            },
        }

    def test_stronger_rival_is_not_skipped_when_own_model_minimum_is_met(self):
        decision = refinement.membership_decision(self.comparison, self.policy)
        self.assertEqual(decision["decision"], "move")
        self.assertEqual(decision["destination"], "Models/Beta Bee/gallery")

    def test_only_automatic_review_association_can_be_reconsidered(self):
        row = {**self.comparison, "bucket": "review", "automaticReviewAssociation": True}
        decision = refinement.membership_decision(row, self.policy)
        self.assertEqual(decision["destination"], "Models/Beta Bee/gallery")
        for overrides in (
            {"automaticReviewAssociation": False}, {"protected": True}, {"anchor": True},
            {"workflowSelected": True}, {"rejectionHistory": True}, {"qualityEligible": False},
            {"metadataStale": True}, {"identityProtected": True},
            {"refinementTarget": {**row["refinementTarget"], "independentSupport": 1}},
        ):
            with self.subTest(overrides=overrides):
                self.assertEqual(refinement.membership_decision(
                    {**row, **overrides}, self.policy,
                )["decision"], "hold")
        legacy = copy.deepcopy(self.policy)
        legacy.pop("groupCastReviewEnabled")
        self.assertEqual(refinement.membership_decision(row, legacy)["decision"], "hold")

    def test_locks_quality_staleness_and_independent_support_hold(self):
        for field in ("protected", "anchor", "workflowSelected", "identityProtected",
                      "rejectionHistory", "metadataStale", "ambiguousPhotoId"):
            with self.subTest(field=field):
                row = {**self.comparison, field: True}
                self.assertEqual(refinement.membership_decision(row, self.policy)["decision"], "hold")
        for row in (
            {**self.comparison, "photoId": None},
            {**self.comparison, "qualityEligible": False},
            {**self.comparison, "bucket": "review"},
            {**self.comparison, "ownScore": None},
            {**self.comparison, "refinementTarget": {
                **self.comparison["refinementTarget"], "independentSupport": 1,
            }},
            {**self.comparison, "rivals": [
                self.comparison["rivals"][0], {"folder": "Models/Gamma Gee", "score": .75},
            ]},
        ):
            with self.subTest(row=row):
                decision = refinement.membership_decision(row, self.policy)
                self.assertEqual(decision["decision"], "hold")
                self.assertTrue(decision["reason"])

    def test_cast_destination_is_review_not_gallery(self):
        self.comparison["refinementTarget"]["folder"] = "Angels/Xena"
        decision = refinement.membership_decision(self.comparison, self.policy)
        self.assertEqual(decision["destination"], "Angels/Xena/review")

    def test_admission_boundary_is_not_rounded_into_acceptance(self):
        self.comparison["ownScore"] = .1
        self.comparison["refinementTarget"].update(folder="Angels/Xena", score=.55 - 1e-8)
        decision = refinement.membership_decision(self.comparison, self.policy)
        self.assertEqual(decision["decision"], "hold")
        self.comparison["refinementTarget"]["score"] = .55
        self.assertEqual(refinement.membership_decision(self.comparison, self.policy)["decision"], "move")

    def rows(self):
        return [{"source": "old.jpg", "destination": "Models/Alpha Ann/gallery/photo.jpg",
                 "photoId": "photo:123456", "reason": "first pass"}]

    def evaluator(self, rows):
        row = rows[0]
        move = row["destination"].startswith("Models/Alpha Ann/")
        return {"reference": "frozen final cores", "rows": [{
            **row, "higherRival": move, "ownScore": .6, "rivals": [{"score": .8}],
            "refinementDecision": {
                "decision": "move" if move else "hold", "reason": "qualifying comparison" if move else "no higher rival",
                "destination": "Models/Beta Bee/gallery", "lead": .2,
            },
        }]}

    def test_rebuilds_after_each_frozen_pass_and_does_not_mutate_input(self):
        rows = self.rows()
        before = copy.deepcopy(rows)
        from unittest import mock
        evaluate = mock.Mock(side_effect=self.evaluator)
        result, evidence = refinement.refine_membership(rows, evaluate)
        self.assertEqual(rows, before)
        self.assertEqual(result[0]["destination"], "Models/Beta Bee/gallery/photo.jpg")
        self.assertEqual(evidence["moveCount"], 1)
        self.assertEqual(evidence["stopReason"], "stable")
        self.assertEqual(evidence["residuals"], [])
        self.assertEqual(evaluate.call_count, 3)

    def test_retained_cast_move_keeps_release_flags_and_policy_decision_consistent(self):
        rows = self.rows()
        rows[0].update(
            source="Angels/Camaris/gallery/camaris_image_7514747981804668439.jpg",
            retainedCast=True, releasedCast=False, castSeedDecision="retained",
            castSeedReason="member of the current configured identity core",
            castSeedScore=.72, castSeedThreshold=.6, castSeedCore=True,
        )
        before = copy.deepcopy(rows)
        result, evidence = refinement.refine_membership(rows, self.evaluator)
        row = result[0]
        self.assertEqual(row["castSeedDecision"], "released")
        self.assertFalse(row["retainedCast"])
        self.assertTrue(row["releasedCast"])
        self.assertIn("member of the current configured identity core", row["castSeedReason"])
        self.assertIn("final-membership pass 1", row["castSeedReason"])
        self.assertEqual((row["castSeedScore"], row["castSeedThreshold"], row["castSeedCore"]),
                         (.72, .6, True))
        self.assertEqual(evidence["moveCount"], 1)
        self.assertEqual(rows, before)

    def test_pass_cap_and_oscillation_are_explicit(self):
        def alternating(rows):
            audit = self.evaluator(rows)
            audit["rows"][0]["higherRival"] = True
            audit["rows"][0]["refinementDecision"].update(
                decision="move",
                destination=("Models/Beta Bee/gallery" if "Alpha" in rows[0]["destination"]
                             else "Models/Alpha Ann/gallery"),
            )
            return audit

        _, capped = refinement.refine_membership(self.rows(), alternating, max_passes=1)
        self.assertEqual(capped["stopReason"], "pass-limit")
        self.assertIn("pass limit", capped["residuals"][0]["reason"])
        _, stopped = refinement.refine_membership(self.rows(), alternating)
        self.assertEqual(stopped["moveCount"], 1)
        self.assertIn("oscillation", stopped["residuals"][0]["reason"])

    def test_post_admission_refinement_rechecks_changed_cores_and_preserves_history(self):
        def before_admission(rows):
            audit = self.evaluator(rows)
            audit["rows"][0].update(higherRival=False)
            audit["rows"][0]["refinementDecision"].update(decision="hold", reason="no higher rival")
            return audit

        rows, first = refinement.refine_membership(self.rows(), before_admission)
        self.assertEqual(first["moveCount"], 0)
        rows, after = refinement.refine_membership(rows, self.evaluator, prior_evidence=first)
        self.assertEqual(rows[0]["destination"], "Models/Beta Bee/gallery/photo.jpg")
        self.assertEqual(after["moveCount"], 1)
        self.assertEqual(after["passCount"], 3)
        self.assertEqual(after["maxPasses"], 8)
        self.assertEqual(after["residuals"], [])
        self.assertEqual(rows[0]["refinement"][-1]["pass"], 2)

        def reverse_after_more_evidence(rows):
            audit = self.evaluator(rows)
            audit["rows"][0].update(higherRival=True)
            audit["rows"][0]["refinementDecision"].update(
                decision="move", destination="Models/Alpha Ann/gallery",
            )
            return audit

        rows, stopped = refinement.refine_membership(rows, reverse_after_more_evidence, prior_evidence=after)
        self.assertEqual(rows[0]["destination"], "Models/Beta Bee/gallery/photo.jpg")
        self.assertEqual(stopped["moveCount"], 1)
        self.assertIn("oscillation:", stopped["residuals"][0]["reason"])

    def test_invalid_pass_limit_and_incomplete_evaluation_fail(self):
        for limit in (0, -1, True):
            with self.assertRaisesRegex(ValueError, "positive integer"):
                refinement.refine_membership(self.rows(), self.evaluator, max_passes=limit)
        with self.assertRaisesRegex(ValueError, "every source"):
            refinement.refine_membership(self.rows(), lambda rows: {"rows": []})

    def test_destination_collision_refuses_before_changing_inputs(self):
        rows = self.rows() + [{
            "source": "other.jpg", "destination": "Models/Beta Bee/gallery/photo.jpg",
            "photoId": "photo:654321", "reason": "already there",
        }]
        original = copy.deepcopy(rows)

        def evaluate(current):
            audit = self.evaluator(current)
            audit["rows"].append({
                **current[1], "higherRival": False,
                "refinementDecision": {"decision": "hold", "reason": "no higher rival"},
            })
            return audit

        with self.assertRaisesRegex(ValueError, "collide destination"):
            refinement.refine_membership(rows, evaluate)
        self.assertEqual(rows, original)

    def test_renames_full_paths_in_membership_steps_and_evidence(self):
        rows, evidence = refinement.refine_membership(self.rows(), self.evaluator)
        names = {"Models/Beta Bee": "Models/Bianca Bell"}
        refinement.rename_membership_evidence(evidence, names)
        refinement.rename_steps(rows, names)
        self.assertEqual(evidence["passes"][0]["moves"][0]["to"], "Models/Bianca Bell/gallery")
        self.assertEqual(rows[0]["refinement"][0]["to"], "Models/Bianca Bell/gallery")


if __name__ == "__main__":
    unittest.main()
