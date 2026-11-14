"""Frozen RA2 arithmetic, conservation and real shared policy safeguards."""
import copy
import json
import unittest
from unittest import mock

import numpy as np

from tools.art.likeness_library import policy, protection, reference_trial, refinement, shadow


class ReferenceTrialTests(unittest.TestCase):
    def setUp(self):
        self.a, self.b, self.outside = "Angels/A", "Sisters/B", "Models/Outside"
        self.vectors = {
            "a0": np.array([1., 0., 0.]),
            "a1": shadow.nz(np.array([1., .4, 0.])),
            "a2": shadow.nz(np.array([.1, 1., 0.])),
            "b0": np.array([0., 1., 0.]),
            "b1": shadow.nz(np.array([0., 1., .4])),
            "b2": shadow.nz(np.array([.2, 1., -.4])),
            "x": np.array([0., 0., 1.]),
            "c0": shadow.nz(np.array([-1., 0., .2])),
            "c1": shadow.nz(np.array([-1., .3, 0.])),
            "d0": shadow.nz(np.array([.4, -.8, .2])),
            "d1": shadow.nz(np.array([.3, -.9, .1])),
        }
        groups = {
            self.a: ["a0", "a1", "a2"], self.b: ["b0", "b1", "b2"],
            self.outside: ["x"], "Models/C": ["c0", "c1"], "Models/D": ["d0", "d1"],
        }
        settings = policy.load_policy()
        settings["protection"]["automatic"]["minimumIndependentReferences"] = 1
        settings["photoRouting"]["minimumOwnCoreLead"] = .01
        self.run = {"photos": [], "finalMembershipAudit": {"rows": []}, "policy": settings}
        for folder, ids in groups.items():
            for pid in ids:
                others = [self.vectors[other] for other in ids if other != pid]
                own = float(self.vectors[pid] @ shadow.nz(np.sum(others, axis=0))) if others else None
                rivals = sorted(
                    ({"folder": rival, "score": float(self.vectors[pid] @ shadow.nz(
                        np.mean([self.vectors[other] for other in refs], axis=0),
                    ))} for rival, refs in groups.items() if rival != folder),
                    key=lambda row: (-row["score"], row["folder"]),
                )[:3]
                photo = {
                    "photoId": pid, "destination": f"{folder}/gallery/{pid}.png",
                    "preparedSHA256": "hash-" + pid,
                }
                self.run["photos"].append(photo)
                self.run["finalMembershipAudit"]["rows"].append({
                    **photo, "ownScore": round(own, 6) if own is not None else None,
                    "rivals": [{**rival, "score": round(rival["score"], 6)} for rival in rivals],
                    "coreMember": True, "qualityEligible": True, "ambiguousPhotoId": False,
                    "metadataStale": False, "protected": False, "anchor": False,
                    "workflowSelected": False, "identityProtected": False,
                    "rejectionHistory": False, "bucket": "gallery",
                    "higherRival": True, "refinementTarget": None,
                })
        self.run["photos"].append({
            "photoId": "hold", "destination": "Various/review/hold.png",
            "preparedSHA256": "hash-hold",
        })
        self.run["finalMembershipAudit"]["rows"].append({
            **self.run["photos"][-1], "coreMember": False, "qualityEligible": False,
            "ownScore": None, "rivals": [], "ambiguousPhotoId": False,
            "metadataStale": False, "protected": False, "anchor": False,
            "workflowSelected": False, "identityProtected": False,
            "rejectionHistory": False, "bucket": "review",
        })
        decisions = {
            self.a: {"a0": "reference", "a1": "reference", "x": "reference",
                     "a2": "same-not-reference", "b0": "different", "hold": "uncertain"},
            self.b: {"b1": "reference", "b2": "reference", "b0": "different",
                     "a2": "uncertain"},
        }
        self.packet = {
            "packetSHA256": "bound", "binding": {"run": "frozen"},
            "characters": [
                {"folder": folder, "cards": [{"photoId": pid} for pid in values]}
                for folder, values in decisions.items()
            ],
        }
        self.answers = {
            "schemaVersion": 1, "kind": "character-reference-answers",
            "packetSHA256": "bound", "binding": {"run": "frozen"},
            "characters": [
                {"folder": folder, "decisions": [
                    {"photoId": pid, "choice": choice} for pid, choice in values.items()
                ]} for folder, values in decisions.items()
            ],
        }
        self.labels = {"pairs": [
            {"photoIds": ["a0", "a2"], "label": "different"},
            {"photoIds": ["a1", "b0"], "label": "same"},
            {"photoIds": ["b1", "b2"], "label": "uncertain"},
        ]}

    def evaluate(self):
        return reference_trial.evaluate(
            self.run, self.vectors, self.packet, self.answers, self.labels,
        )

    def test_self_excluded_even_from_different_folder_destination(self):
        result = self.evaluate()
        row = next(row for row in result["rows"] if row["photoId"] == "x")
        # x belongs to Models/Outside but is a confirmed A reference.
        score = float(self.vectors["x"] @ shadow.nz(self.vectors["a0"] + self.vectors["a1"]))
        self.assertEqual(row["characterScores"][self.a]["confirmed"], round(score, 6))
        self.assertEqual(row["characterScores"][self.a]["confirmedReferenceCount"], 2)
        self.assertLess(score, float(self.vectors["x"] @ shadow.nz(
            self.vectors["a0"] + self.vectors["a1"] + self.vectors["x"],
        )))
        self.assertIsNone(row["confirmed"]["ownScore"])
        self.assertTrue(all(rival["folder"] != self.outside for rival in row["confirmed"]["rivals"]))

    def test_reference_withdrawal_empty_competitor_no_fallback(self):
        result = self.evaluate()
        self.assertEqual(result["referenceTransfers"], [{
            "photoId": "x", "fromFolder": self.outside, "toFolder": self.a,
            "reason": "withdraw confirmed reference from another frozen core",
        }])
        self.assertEqual(result["unavailableCompetitors"][0]["folder"], self.outside)
        for row in result["rows"]:
            self.assertNotIn(self.outside, [item["folder"] for item in row["confirmed"]["rivals"]])
        self.assertEqual(result["summary"]["confirmedReferenceCount"], 5)

    def test_all_photos_and_quality_holds_conserved_no_input_changes(self):
        before = copy.deepcopy((self.run, self.packet, self.answers, self.labels))
        vectors = {pid: value.copy() for pid, value in self.vectors.items()}
        result = self.evaluate()
        self.assertEqual(len(result["rows"]), len(self.run["photos"]))
        self.assertEqual(result["summary"]["eligibleCount"], len(self.vectors))
        hold = next(row for row in result["rows"] if row["photoId"] == "hold")
        self.assertFalse(hold["qualityEligible"])
        self.assertIsNone(hold["confirmed"]["ownScore"])
        self.assertIn("quality gate", hold["confirmed"]["policyDecision"]["reason"])
        self.assertEqual(before, (self.run, self.packet, self.answers, self.labels))
        for pid in vectors:
            np.testing.assert_array_equal(vectors[pid], self.vectors[pid])
        json.dumps(result, allow_nan=False)

    def test_uncertain_and_nonreference_positives_are_not_confirmed_core_or_negatives(self):
        result = self.evaluate()
        a = next(item for item in result["characters"] if item["folder"] == self.a)
        self.assertEqual(a["referenceIds"], ["a0", "a1", "x"])
        by_id = {(row["folder"], row["photoId"]): row for row in result["knownCharacterEvidence"]}
        self.assertEqual(by_id[self.a, "hold"]["evaluationRole"], "not a positive or negative")
        self.assertEqual(by_id[self.a, "a2"]["evaluationRole"], "explicit non-reference positive")
        self.assertEqual(by_id[self.a, "b0"]["evaluationRole"], "explicit negative")
        self.assertEqual(by_id[self.a, "a0"]["evaluationRole"], "training leave-one-out diagnostic")

    def test_reverse_every_input_is_deterministic(self):
        first = self.evaluate()
        self.run["photos"].reverse()
        self.run["finalMembershipAudit"]["rows"].reverse()
        self.answers["characters"].reverse()
        self.packet["characters"].reverse()
        for group in self.answers["characters"]:
            group["decisions"].reverse()
        for group in self.packet["characters"]:
            group["cards"].reverse()
        self.vectors = dict(reversed(list(self.vectors.items())))
        self.labels["pairs"].reverse()
        for pair in self.labels["pairs"]:
            pair["photoIds"].reverse()
        self.assertEqual(first, self.evaluate())

    def test_baseline_parity_drift_refuses(self):
        self.run["finalMembershipAudit"]["rows"][0]["ownScore"] += .001
        with self.assertRaisesRegex(ValueError, "final own arithmetic differs"):
            self.evaluate()
        self.run["finalMembershipAudit"]["rows"][0]["ownScore"] -= .001
        self.run["finalMembershipAudit"]["rows"][0]["rivals"][0]["score"] += .001
        with self.assertRaisesRegex(ValueError, "final rival arithmetic differs"):
            self.evaluate()

    def test_actual_shared_membership_probe_keeps_saved_safeguards(self):
        guards = ("protected", "anchor", "workflowSelected", "identityProtected",
                  "rejectionHistory", "metadataStale", "ambiguousPhotoId")
        # A2 strongly prefers B; ensure this is a genuine policy-move probe.
        self.run["policy"]["categoryPolicies"]["Sisters"]["photoRouteMargin"] = .01
        self.run["policy"]["categoryPolicies"]["Sisters"]["photoRouteMinimum"] = .1
        self.run["policy"]["photoRouting"]["reviewMinimum"] = .1
        before = self.evaluate()
        candidate = next(row for row in before["rows"] if row["photoId"] == "a2")
        self.assertEqual(candidate["confirmed"]["policyDecision"]["decision"], "move")
        self.assertEqual(candidate["confirmed"]["policyDecision"]["destination"], "Sisters/B/review")
        for guard in guards:
            with self.subTest(guard=guard):
                source = next(row for row in self.run["finalMembershipAudit"]["rows"]
                              if row["photoId"] == "a2")
                source[guard] = True
                with mock.patch.object(
                    refinement, "membership_decision", wraps=refinement.membership_decision,
                ) as shared:
                    result = self.evaluate()
                    self.assertEqual(shared.call_count, 2 * len(result["rows"]))
                    calls = [call.args[0] for call in shared.call_args_list
                             if call.args[0]["photoId"] == "a2"]
                    self.assertTrue(all(call[guard] for call in calls))
                candidate = next(row for row in result["rows"] if row["photoId"] == "a2")
                self.assertEqual(candidate["confirmed"]["policyDecision"]["decision"], "hold")
                source[guard] = False

    def test_confirmation_does_not_add_placement_protection(self):
        with mock.patch.object(
            refinement, "membership_decision", wraps=refinement.membership_decision,
        ) as shared:
            self.evaluate()
        calls = [call.args[0] for call in shared.call_args_list if call.args[0]["photoId"] == "x"]
        self.assertTrue(all(not call["protected"] and not call["anchor"] for call in calls))

    def test_full_sets_rank_before_top_three(self):
        result = self.evaluate()
        row = next(row for row in result["rows"] if row["photoId"] == "a0")
        self.assertEqual(len(row["baseline"]["rivals"]), 3)
        self.assertEqual(result["summary"]["baselineParity"]["coreCount"], 5)
        self.assertEqual(result["summary"]["policyProbePasses"], 1)
        self.assertIn("not an independent final routing replay", " ".join(result["limits"]))

    def test_direct_pair_conflicts_preserved_without_transitive_spread(self):
        result = self.evaluate()
        self.assertEqual(len(result["pairEvidence"]), 3)
        self.assertEqual(len(result["intentConflicts"]), 2)
        self.assertEqual(result["summary"]["intentConflictCount"], 2)
        self.assertTrue(all(conflict["resolution"].startswith("none") for conflict in result["intentConflicts"]))
        self.assertEqual(result["pairEvidence"][0]["score"], round(
            float(self.vectors["a0"] @ self.vectors["a2"]), 6,
        ))

    def test_malformed_answers_and_insufficient_references_refuse(self):
        good = copy.deepcopy(self.answers)
        for mutate in (
            lambda answer: answer.update(packetSHA256="other"),
            lambda answer: answer["characters"][0]["decisions"][0].update(choice="invented"),
            lambda answer: answer["characters"][0]["decisions"].pop(),
        ):
            self.answers = copy.deepcopy(good)
            mutate(self.answers)
            with self.assertRaises(ValueError):
                self.evaluate()
        self.answers = copy.deepcopy(good)
        for item in self.answers["characters"][0]["decisions"]:
            if item["choice"] == "reference" and item["photoId"] != "a0":
                item["choice"] = "uncertain"
        with self.assertRaisesRegex(ValueError, "insufficient confirmed references"):
            self.evaluate()

    def test_missing_audit_hash_or_measurement_refuses_explicitly(self):
        self.run["photos"].pop()
        with self.assertRaisesRegex(ValueError, "conservation"):
            self.evaluate()
        self.setUp()
        self.run["photos"][0].pop("preparedSHA256")
        with self.assertRaisesRegex(ValueError, "content hash"):
            self.evaluate()
        self.setUp()
        self.vectors.pop("a0")
        with self.assertRaisesRegex(ValueError, "missing eligible/core vector"):
            self.evaluate()

    def test_frozen_independence_reused_for_unchanged_core_sets(self):
        with mock.patch.object(
            protection, "_independent", wraps=protection._independent,
        ) as independent:
            self.evaluate()
        # Five baseline cores, only two reviewed sets differ in the variant.
        self.assertEqual(independent.call_count, 7)
        keys = [tuple(row["photoId"] for row in call.args[0])
                for call in independent.call_args_list]
        self.assertEqual(len(keys), len(set(keys)))

    def test_cached_scores_and_support_match_full_scalar_reconstruction(self):
        result = self.evaluate()
        audit = {row["photoId"]: row for row in self.run["finalMembershipAudit"]["rows"]}
        baseline = {}
        for pid, row in audit.items():
            if row["coreMember"]:
                baseline.setdefault(shadow.folder_for(row), []).append(pid)
        confirmed = {
            **baseline, self.a: ["a0", "a1", "x"], self.b: ["b1", "b2"],
            self.outside: [],
        }
        maximum = self.run["policy"]["identityActions"]["independentEvidenceMaximumSimilarity"]
        for row in result["rows"]:
            if not row["qualityEligible"]:
                continue
            pid = row["photoId"]
            for name, groups in (("baseline", baseline), ("confirmed", confirmed)):
                scores = {}
                for folder, refs in groups.items():
                    others = [other for other in sorted(refs) if other != pid]
                    if others:
                        scores[folder] = float(self.vectors[pid] @ shadow.nz(
                            np.sum([self.vectors[other] for other in others], axis=0),
                        ))
                folder = row["currentFolder"]
                expected_own = round(scores[folder], 6) if folder in scores else None
                self.assertEqual(row[name]["ownScore"], expected_own)
                expected_rivals = sorted(
                    ({"folder": char, "score": value} for char, value in scores.items()
                     if char != folder),
                    key=lambda item: (-item["score"], item["folder"]),
                )[:3]
                self.assertEqual(row[name]["rivals"], [
                    {**item, "score": round(item["score"], 6)} for item in expected_rivals
                ])
                for char in (self.a, self.b):
                    refs = protection._independent([
                        {"photoId": other, "vector": self.vectors[other], "sha256": "hash-" + other}
                        for other in groups[char]
                    ], self.run["policy"])
                    expected = sum(other["photoId"] != pid
                                   and float(self.vectors[pid] @ other["vector"]) <= maximum
                                   for other in refs)
                    self.assertEqual(row["characterScores"][char][name + "Support"], expected)

    def test_duplicate_confirmed_reference_across_characters_refuses(self):
        self.packet["characters"][1]["cards"].append({"photoId": "a0"})
        self.answers["characters"][1]["decisions"].append({
            "photoId": "a0", "choice": "reference",
        })
        with self.assertRaisesRegex(ValueError, "reference assigned to multiple characters"):
            self.evaluate()

    def test_confirmed_profile_matches_direct_scores_and_keeps_negative_labels(self):
        result = self.evaluate()
        refs = {item["folder"]: item["referenceIds"] for item in result["characters"]}
        for row in result["rows"]:
            for folder, ids in refs.items():
                profile = row["characterScores"][folder]["confirmedProfile"]
                if not row["qualityEligible"]:
                    self.assertEqual(profile, {
                        "nearestScore": None, "secondScore": None, "topTwoMean": None,
                        "nearestReferencePhotoId": None, "referenceCount": 0,
                    })
                    continue
                pid = row["photoId"]
                ranked = sorted(
                    ((float(self.vectors[pid] @ self.vectors[other]), other)
                     for other in ids if other != pid),
                    key=lambda item: (-item[0], item[1]),
                )
                self.assertEqual(profile["referenceCount"], len(ranked))
                self.assertEqual(profile["nearestScore"], round(ranked[0][0], 6))
                self.assertEqual(profile["nearestReferencePhotoId"], ranked[0][1])
                self.assertEqual(profile["secondScore"],
                                 round(ranked[1][0], 6) if len(ranked) > 1 else None)
                self.assertEqual(profile["topTwoMean"],
                                 round((ranked[0][0] + ranked[1][0]) / 2, 6)
                                 if len(ranked) > 1 else None)
        row = next(item for item in result["rows"] if item["photoId"] == "b0")
        self.assertEqual(row["characterScores"][self.a]["choice"], "different")
        evidence = next(item for item in result["knownCharacterEvidence"]
                        if item["photoId"] == "b0" and item["folder"] == self.a)
        self.assertEqual(evidence["evaluationRole"], "explicit negative")
        self.assertEqual(evidence["confirmedProfile"],
                         row["characterScores"][self.a]["confirmedProfile"])

    def test_profile_excludes_equal_content_and_has_no_zero_padding(self):
        before = self.evaluate()
        next(photo for photo in self.run["photos"] if photo["photoId"] == "b1")[
            "preparedSHA256"] = "hash-b2"
        result = self.evaluate()
        row = next(item for item in result["rows"] if item["photoId"] == "b1")
        self.assertEqual(row["characterScores"][self.b]["confirmedProfile"], {
            "nearestScore": None, "secondScore": None, "topTwoMean": None,
            "nearestReferencePhotoId": None, "referenceCount": 0,
        })
        old_row = next(item for item in before["rows"] if item["photoId"] == "b1")
        profile = old_row["characterScores"][self.b]["confirmedProfile"]
        self.assertEqual(profile["referenceCount"], 1)
        self.assertEqual(profile["nearestReferencePhotoId"], "b2")
        self.assertIsNone(profile["secondScore"])
        self.assertIsNone(profile["topTwoMean"])
        # Profile content exclusion does not redefine the mean-score experiment.
        self.assertEqual(row["characterScores"][self.b]["confirmed"],
                         old_row["characterScores"][self.b]["confirmed"])

    def test_profile_ties_use_stable_photo_id_not_input_order(self):
        # x has exactly zero dot with both a0 and a1.
        first = self.evaluate()
        row = next(item for item in first["rows"] if item["photoId"] == "x")
        profile = row["characterScores"][self.a]["confirmedProfile"]
        self.assertEqual(profile["nearestReferencePhotoId"], "a0")
        self.assertEqual(profile["nearestScore"], 0.)
        self.assertEqual(profile["secondScore"], 0.)
        self.answers["characters"][0]["decisions"].reverse()
        self.assertEqual(first, self.evaluate())

    def test_profile_generation_never_changes_mean_or_shared_policy_inputs(self):
        with mock.patch.object(
            refinement, "membership_decision", wraps=refinement.membership_decision,
        ) as shared:
            result = self.evaluate()
        self.assertEqual(shared.call_count, len(result["rows"]) * 2)
        self.assertTrue(all("confirmedProfile" not in call.args[0]
                            for call in shared.call_args_list))
        for row in result["rows"]:
            for name in ("baseline", "confirmed"):
                matching = [call.args[0] for call in shared.call_args_list
                            if call.args[0]["photoId"] == row["photoId"]]
                probe = matching[0 if name == "baseline" else 1]
                self.assertEqual(row[name]["policyDecision"],
                                 refinement.membership_decision(probe, self.run["policy"]))


if __name__ == "__main__":
    unittest.main()
