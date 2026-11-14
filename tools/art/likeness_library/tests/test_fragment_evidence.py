"""Acceptance tests for bounded, report-only coherent fragment evidence."""

import copy
import math
import unittest

import numpy as np

from tools.art.likeness_library import fragment_evidence, policy


def unit(values):
    value = np.asarray(values, dtype=float)
    return value / np.linalg.norm(value)


def angle(degrees, dimensions=4):
    radians = math.radians(degrees)
    return unit([math.cos(radians), math.sin(radians), *([0.] * (dimensions - 2))])


class FragmentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.settings = copy.deepcopy(policy.load_policy())
        self.settings["identityActions"]["identityClusterMinimumSimilarity"] = .8
        self.settings["identityActions"]["independentEvidenceMaximumSimilarity"] = .95
        self.settings["protection"]["automatic"]["minimumIndependentReferences"] = 2
        self.photos = {}
        self.vectors = {}
        self.identities = []
        self.rows = []

    def add_photo(self, photo_id, vector, folder="Models/Source", digest=None, bucket="gallery"):
        digest = digest or f"hash:{photo_id}"
        self.photos[photo_id] = {
            "photoId": photo_id,
            "preparedSHA256": digest,
            "destination": f"{folder}/{bucket}/{photo_id}.jpg",
        }
        self.vectors[photo_id] = np.asarray(vector, dtype=float)
        self.rows.append({
            "photoId": photo_id,
            "currentFolder": folder,
            "candidateFolder": None,
            "evidence": {"topCandidates": []},
        })
        return photo_id

    def add_identity(self, identity_id, folder, photo_ids):
        self.identities.append({
            "identityId": identity_id,
            "folder": folder,
            "referencePhotoIds": list(photo_ids),
        })

    def candidate(self):
        return {
            "identities": copy.deepcopy(self.identities),
            "appearances": [
                {
                    "identityId": identity["identityId"],
                    "photoIds": list(identity["referencePhotoIds"]),
                }
                for identity in self.identities
            ],
            "rows": copy.deepcopy(self.rows),
        }

    def receipt(self):
        return {"policy": self.settings, "photos": list(self.photos.values())}

    def evaluate(self, effective=None):
        return fragment_evidence.evaluate(
            self.candidate(), self.receipt(), self.vectors, effective or {"pairs": []},
        )

    @staticmethod
    def result_row(result, photo_id):
        return next(row for row in result["rows"] if row["photoId"] == photo_id)

    def test_contaminated_identity_scores_coherent_subgroup_separately(self):
        query = self.add_photo("query", angle(0))
        refs = [
            self.add_photo("ref-a", angle(-15), "Models/Target"),
            self.add_photo("ref-b", angle(15), "Models/Target"),
            self.add_photo("outlier", angle(80), "Models/Target"),
        ]
        self.add_identity("target-id", "Models/Target", refs)
        query_row = next(row for row in self.rows if row["photoId"] == query)
        query_row["candidateFolder"] = "Models/Legacy"
        query_row["evidence"]["topCandidates"] = [
            {"folder": "Models/Legacy", "score": .72},
        ]
        result = self.evaluate()
        row = self.result_row(result, query)
        target = row["topCandidates"][0]
        self.assertEqual(target["folder"], "Models/Target")
        self.assertEqual(target["referencePhotoIds"], refs[:2])
        self.assertGreater(target["subgroupScore"], target["wholeScore"])
        self.assertGreater(target["subgroupMeanScore"], target["wholeMeanScore"])
        self.assertAlmostEqual(
            target["subgroupMeanDelta"],
            target["subgroupMeanScore"] - target["wholeMeanScore"],
        )
        self.assertEqual(target["supportCount"], 2)
        self.assertEqual(target["supportCandidateCount"], 2)
        self.assertEqual(row["suggestedFolder"], "Models/Target")
        self.assertEqual(row["baselineTarget"], "Models/Legacy")
        self.assertEqual(row["baselineTop"], "Models/Legacy")
        self.assertEqual(row["baselineTopScore"], .72)
        self.assertEqual(target["status"], "tentative")
        self.assertFalse(target["identityEstablished"])

    def test_complete_link_does_not_chain_a_bridge_reference(self):
        self.settings["identityActions"]["identityClusterMinimumSimilarity"] = .7
        query = self.add_photo("query", angle(40))
        refs = [
            self.add_photo("a", angle(0), "Models/Target"),
            self.add_photo("b", angle(40), "Models/Target"),
            self.add_photo("c", angle(80), "Models/Target"),
        ]
        self.add_identity("target-id", "Models/Target", refs)
        target = self.result_row(self.evaluate(), query)["topCandidates"][0]
        self.assertEqual(target["referencePhotoIds"], ["a", "b"])
        self.assertNotIn("c", target["referencePhotoIds"])
        self.assertEqual(target["supportCount"], 2)

    def test_high_scoring_singleton_is_tentative_and_never_qualifies(self):
        query = self.add_photo("query", angle(0))
        singleton = self.add_photo("exact", angle(0), "Models/Target")
        self.add_identity("target-id", "Models/Target", [singleton])
        result = self.evaluate()
        target = self.result_row(result, query)["topCandidates"][0]
        self.assertEqual(target["subgroupScore"], 1.0)
        self.assertEqual(target["supportCount"], 1)
        self.assertIn("insufficient-independent-reference-support", target["blockers"])
        self.assertEqual(target["status"], "tentative")
        self.assertFalse(target["identityEstablished"])

    def test_self_and_equal_content_are_removed_from_scores_and_support(self):
        query = self.add_photo("query", angle(0), "Models/Target", digest="same-bytes")
        twin = self.add_photo("twin", angle(0), "Models/Target", digest="same-bytes")
        left = self.add_photo("left", angle(-15), "Models/Target")
        right = self.add_photo("right", angle(15), "Models/Target")
        self.add_identity("target-id", "Models/Target", [query, twin, left, right])
        row = self.result_row(self.evaluate(), query)
        self.assertEqual(row["own"]["referencePhotoIds"], [left, right])
        self.assertEqual(row["own"]["supportCount"], 2)
        self.assertAlmostEqual(row["own"]["wholeScore"], row["own"]["subgroupScore"], places=6)
        self.assertNotIn(query, row["own"]["referencePhotoIds"])
        self.assertNotIn(twin, row["own"]["referencePhotoIds"])

    def test_cached_shared_gate_does_not_count_equal_hashes_or_repeated_measurements(self):
        query = self.add_photo("query", angle(0))
        left = self.add_photo("left", angle(-15), "Models/Target", digest="repeated")
        right = self.add_photo("right", angle(15), "Models/Target", digest="repeated")
        self.add_identity("target-id", "Models/Target", [left, right])
        target = self.result_row(self.evaluate(), query)["topCandidates"][0]
        self.assertEqual(target["supportCandidateCount"], 2)
        self.assertEqual(target["supportCount"], 1)
        self.photos[right]["preparedSHA256"] = "different-bytes"
        self.vectors[right] = self.vectors[left].copy()
        target = self.result_row(self.evaluate(), query)["topCandidates"][0]
        self.assertEqual(target["supportCandidateCount"], 2)
        self.assertEqual(target["supportCount"], 1)
        self.assertIn("insufficient-independent-reference-support", target["blockers"])

    def test_direct_different_and_uncertain_veto_only_the_linked_subgroup(self):
        query = self.add_photo("query", angle(0))
        linked = self.add_photo("linked", angle(-15), "Models/Target")
        other = self.add_photo("other", angle(15), "Models/Target")
        unrelated = self.add_photo("unrelated", angle(90), "Models/Other")
        self.add_identity("target-id", "Models/Target", [linked, other])
        self.add_identity("other-id", "Models/Other", [unrelated])
        for label, blocker in (
            ("different", "direct-different-veto"),
            ("uncertain", "direct-uncertainty-veto"),
        ):
            result = self.evaluate({
                "pairs": [{"photoIds": [query, linked], "label": label}],
            })
            row = self.result_row(result, query)
            target = next(item for item in row["topCandidates"] if item["folder"] == "Models/Target")
            self.assertIn(blocker, target["blockers"])
            self.assertNotEqual(row["suggestedFolder"], "Models/Target")
            self.assertNotIn(
                blocker,
                next(item for item in row["topCandidates"] if item["folder"] == "Models/Other")["blockers"],
            )

    def test_unchanged_frozen_references_and_reordered_inputs_are_deterministic(self):
        query = self.add_photo("query", angle(0))
        refs = [
            self.add_photo("a", angle(-15), "Models/Target"),
            self.add_photo("b", angle(15), "Models/Target"),
            self.add_photo("outlier", angle(80), "Models/Target"),
        ]
        rival = self.add_photo("rival", angle(90), "Models/Other")
        self.add_identity("target-id", "Models/Target", refs)
        self.add_identity("other-id", "Models/Other", [rival])
        candidate = self.candidate()
        original_references = copy.deepcopy(candidate["identities"])
        vectors = dict(self.vectors)
        first = fragment_evidence.evaluate(candidate, self.receipt(), vectors, {"pairs": []})
        self.assertEqual(candidate["identities"], original_references)
        original_rows = copy.deepcopy(candidate["rows"])
        candidate["identities"].reverse()
        candidate["appearances"].reverse()
        candidate["rows"].reverse()
        run = self.receipt()
        run["photos"].reverse()
        reversed_vectors = dict(reversed(list(vectors.items())))
        second = fragment_evidence.evaluate(candidate, run, reversed_vectors, {"pairs": []})
        self.assertEqual(first, second)
        self.assertEqual(
            {row["identityId"]: row["referencePhotoIds"] for row in candidate["identities"]},
            {row["identityId"]: row["referencePhotoIds"] for row in original_references},
        )
        self.assertEqual(candidate["rows"], list(reversed(original_rows)))
        self.assertEqual(candidate["rows"][0]["photoId"], "rival")
        self.assertEqual(first["recipe"]["suggestionSemantics"], "tentative subgroup evidence; never an identity declaration")

    def test_artists_only_compete_with_artists_and_review_has_no_suggestion(self):
        model_query = self.add_photo("model-query", angle(0), "Models/Source")
        artist_query = self.add_photo("artist-query", angle(0), "Artists/Source")
        model_ref = self.add_photo("model-ref", angle(0), "Models/Target")
        artist_ref = self.add_photo("artist-ref", angle(0), "Artists/Target")
        review_query = self.add_photo("review-query", angle(0), "Models/Source", bucket="review")
        self.add_identity("model-target", "Models/Target", [model_ref])
        self.add_identity("artist-target", "Artists/Target", [artist_ref])
        result = self.evaluate()
        model_row = self.result_row(result, model_query)
        artist_row = self.result_row(result, artist_query)
        review_row = self.result_row(result, review_query)
        self.assertNotIn("Artists/Target", [row["folder"] for row in model_row["topCandidates"]])
        self.assertNotIn("Models/Target", [row["folder"] for row in artist_row["topCandidates"]])
        self.assertEqual(review_row["suggestedFolder"], None)
        self.assertEqual(review_row["hold"], "review-placement-hold")
        self.assertIsNone(review_row["baselineTarget"])

    def test_missing_query_vector_is_explicit_and_missing_reference_vector_refuses(self):
        query = self.add_photo("query", angle(0))
        reference = self.add_photo("reference", angle(0), "Models/Target")
        self.add_identity("target-id", "Models/Target", [reference])
        self.vectors.pop(query)
        row = self.result_row(self.evaluate(), query)
        self.assertIn("missing-query-vector", row["topCandidates"][0]["blockers"])
        self.assertIsNone(row["topCandidates"][0]["subgroupScore"])
        self.assertIsNone(row["suggestedFolder"])
        self.vectors.pop(reference)
        with self.assertRaisesRegex(ValueError, "missing saved vector for reference photo"):
            self.evaluate()

    def test_baseline_admission_holds_are_not_replayed_as_evidence_gates(self):
        query = self.add_photo("query", angle(0))
        references = [
            self.add_photo("a", angle(-15), "Models/Target"),
            self.add_photo("b", angle(15), "Models/Target"),
        ]
        self.add_identity("target-id", "Models/Target", references)
        row = next(row for row in self.rows if row["photoId"] == query)
        row.update(
            qualityEligible=False, referenceEligible=False, protected=True,
            state="unresolved", blockers=["manual-opt-out"],
        )
        row["evidence"]["manualOptOut"] = True
        result = self.evaluate()
        evidence = self.result_row(result, query)
        self.assertEqual(evidence["suggestedFolder"], "Models/Target")
        self.assertEqual(evidence["execution"], "not-authorized")
        self.assertEqual(evidence["topCandidates"][0]["status"], "tentative")
        self.assertEqual(result["summary"]["supportedCandidateCount"], 1)

    def test_non_scoring_baseline_identities_preserve_all_3290_queries_without_admission(self):
        query = self.add_photo("query", angle(0))
        target = self.add_photo("target", angle(15), "Models/Target")
        various = self.add_photo("various", angle(0), "Various")
        review = self.add_photo("review", angle(0), "Various", bucket="review")
        unknown = self.add_photo("unknown", angle(0), "Unconfigured/Person")
        self.add_identity("target-id", "Models/Target", [target])
        self.add_identity("various-id", "Various", [various])
        self.add_identity("unknown-id", "Unconfigured/Person", [unknown])
        self.vectors.pop(unknown)
        for index in range(3290 - len(self.photos)):
            self.add_photo(f"other-{index:04}", angle(0), "Various")
        candidate = self.candidate()
        original = copy.deepcopy(candidate)
        result = fragment_evidence.evaluate(
            candidate, self.receipt(), self.vectors, {"pairs": []},
        )
        self.assertEqual(candidate, original)
        self.assertEqual(result["summary"]["photoCount"], 3290)
        self.assertEqual(len(result["rows"]), 3290)
        self.assertEqual({row["photoId"] for row in result["rows"]}, set(self.photos))
        self.assertEqual(result["summary"]["nonScoringIdentityCount"], 2)
        self.assertEqual(result["summary"]["nonScoringCategoryHoldCount"], 3288)
        query_row = self.result_row(result, query)
        self.assertEqual(query_row["suggestedFolder"], "Models/Target")
        self.assertEqual(
            [row["folder"] for row in query_row["topCandidates"]], ["Models/Target"],
        )
        for photo_id, hold in (
            (various, "non-scoring-category-hold"),
            (review, "review-placement-hold"),
            (unknown, "non-scoring-category-hold"),
        ):
            row = self.result_row(result, photo_id)
            self.assertIsNone(row["own"])
            self.assertEqual(row["topCandidates"], [])
            self.assertIsNone(row["suggestedFolder"])
            self.assertEqual(row["hold"], hold)
            self.assertEqual(row["execution"], "not-authorized")
        candidate["identities"].reverse()
        candidate["appearances"].reverse()
        candidate["rows"].reverse()
        receipt = self.receipt()
        receipt["photos"].reverse()
        repeated = fragment_evidence.evaluate(
            candidate, receipt, dict(reversed(list(self.vectors.items()))), {"pairs": []},
        )
        self.assertEqual(result, repeated)

    def test_missing_query_rows_unknown_vectors_and_bad_direct_pairs_refuse(self):
        self.add_photo("query", angle(0))
        candidate = self.candidate()
        candidate["rows"].clear()
        with self.assertRaisesRegex(ValueError, "cover every receipt photo"):
            fragment_evidence.evaluate(candidate, self.receipt(), self.vectors, {"pairs": []})
        with self.assertRaisesRegex(ValueError, "unknown photo IDs"):
            fragment_evidence.evaluate(
                self.candidate(), self.receipt(), {**self.vectors, "unknown": angle(0)}, {"pairs": []},
            )
        with self.assertRaisesRegex(ValueError, "invalid effective direct pair"):
            self.evaluate({"pairs": [{"photoIds": ["query", "missing"], "label": "same"}]})

    def test_shared_reference_comparisons_fit_3290_queries_without_recharging_support(self):
        self.settings["identityActions"]["identityClusterMinimumSimilarity"] = .25
        references = []
        for index in range(120):
            radians = 2 * math.pi * index / 120
            references.append(self.add_photo(
                f"reference-{index:03}",
                [.8, .6 * math.cos(radians), .6 * math.sin(radians), 0.],
                "Models/Target",
            ))
        self.add_identity("target-id", "Models/Target", references)
        for index in range(3290 - len(references)):
            self.add_photo(f"query-{index:04}", angle(0))
        old_repeated_estimate = 120 * 119 // 2 + 3290 * (120 + 120 * 119 // 2)
        self.assertGreater(old_repeated_estimate, fragment_evidence.MAX_PAIR_OPERATIONS)
        result = self.evaluate()
        summary = result["summary"]
        self.assertEqual(summary["photoCount"], 3290)
        self.assertEqual(summary["referencePairOperationCount"], 7140)
        self.assertEqual(summary["queryReferencePairOperationCount"], 3290 * 120)
        self.assertEqual(summary["centroidPairOperationCount"], 3290 * 2)
        self.assertEqual(summary["pairOperationCount"], 408520)
        self.assertGreater(summary["independentSupportCacheHitCount"], 7140)
        query = self.result_row(result, "query-0000")
        self.assertGreaterEqual(query["topCandidates"][0]["supportCount"], 2)
        reference = self.result_row(result, references[0])
        self.assertNotIn(references[0], reference["own"]["referencePhotoIds"])
        self.assertNotIn(references[0], reference["own"]["supportPhotoIds"])

    def test_population_candidate_cell_and_pair_operation_caps_refuse_without_truncation(self):
        over_photos = {
            "policy": self.settings,
            "photos": [{"photoId": f"p{i}"} for i in range(fragment_evidence.MAX_PHOTOS + 1)],
        }
        with self.assertRaisesRegex(ValueError, "population exceeds"):
            fragment_evidence.evaluate(
                {"identities": [], "appearances": [], "rows": []},
                over_photos, {}, {"pairs": []},
            )

        photos = [
            {"photoId": f"p{i}", "sha256": f"h{i}"}
            for i in range(2000)
        ]
        identities = [
            {"identityId": f"i{i}", "folder": f"Models/I{i}", "referencePhotoIds": []}
            for i in range(fragment_evidence.MAX_IDENTITIES)
        ]
        rows = [
            {"photoId": photo["photoId"], "currentFolder": "Models/Source",
             "evidence": {"topCandidates": []}}
            for photo in photos
        ]
        with self.assertRaisesRegex(ValueError, "candidate cells exceed"):
            fragment_evidence.evaluate(
                {"identities": identities, "appearances": [], "rows": rows},
                {"policy": self.settings, "photos": photos}, {}, {"pairs": []},
            )

        too_many_identities = [
            {"identityId": f"i{i}", "folder": f"Models/I{i}", "referencePhotoIds": []}
            for i in range(fragment_evidence.MAX_IDENTITIES + 1)
        ]
        with self.assertRaisesRegex(ValueError, "identity count exceeds"):
            fragment_evidence.evaluate(
                {"identities": too_many_identities, "appearances": [], "rows": []},
                {"policy": self.settings, "photos": []}, {}, {"pairs": []},
            )

        refs = [f"r{i}" for i in range(5000)]
        photos = [{"photoId": pid, "sha256": pid} for pid in refs]
        vectors = {
            pid: unit([math.cos(i * 1e-5), math.sin(i * 1e-5), 0., 0.])
            for i, pid in enumerate(refs)
        }
        rows = [
            {"photoId": pid, "currentFolder": "Models/Target",
             "evidence": {"topCandidates": []}}
            for pid in refs
        ]
        with self.assertRaisesRegex(ValueError, "pair operations exceed"):
            fragment_evidence.evaluate(
                {"identities": [{
                    "identityId": "big", "folder": "Models/Target",
                    "referencePhotoIds": refs,
                }], "appearances": [], "rows": rows},
                {"policy": self.settings, "photos": photos},
                vectors, {"pairs": []},
            )


if __name__ == "__main__":
    unittest.main()
