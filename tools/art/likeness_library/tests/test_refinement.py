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
        refined, evidence = self.run_refine()
        self.assertEqual(self.destination_of(refined, "photo:x"), "Prospects/Alpha Ann")
        self.assertEqual(evidence["moveCount"], 0)

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


if __name__ == "__main__":
    unittest.main()
