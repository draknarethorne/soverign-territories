"""Whole-landscape reporting and answer-blind evaluation without library writes."""
import copy
import json
import unittest

from tools.art.likeness_library import realignment_evaluation, realignment_report


class RealignmentReportTests(unittest.TestCase):
    def setUp(self):
        self.run = {
            "workingRoot": r"B:\Sovereign Territories Sandbox\Working",
            "photos": [{"photoId": pid, "destination": f"Models/{folder}/gallery/{pid}.png",
                        "preparedSHA256": "hash-" + pid}
                       for pid, folder in (("a", "One"), ("b", "Two"), ("c", "Two"))],
            "finalMembershipAudit": {"rows": [
                {"photoId": pid, "workflowSelected": pid == "b"} for pid in ("a", "b", "c")
            ]},
        }
        self.candidate = {
            "summary": {"photoCount": 3}, "recipe": {"gate": .4}, "limits": ["<script>unsafe</script>"],
            "identities": [
                {"identityId": "one", "folder": "Models/One", "referencePhotoIds": ["a"],
                 "referenceStatus": "provisional", "referenceNeeded": False, "appearanceGroupIds": ["g1"]},
                {"identityId": "two", "folder": "Models/Two", "referencePhotoIds": [],
                 "referenceStatus": "insufficient", "referenceNeeded": True, "appearanceGroupIds": ["g2"]},
            ],
            "rows": [{
                "photoId": pid, "currentFolder": "Models/One" if pid == "a" else "Models/Two",
                "candidateFolder": "Models/One" if pid == "b" else None,
                "state": "candidate" if pid == "b" else "unresolved", "origin": "automatic-hypothesis",
                "referenceEligible": pid == "a", "blockers": [],
                "reason": "face hypothesis", "evidence": {
                    "ownScore": .3, "topCandidates": [{"folder": "Models/One", "referencePhotoIds": ["a"]}],
                },
                "reconsiderable": True, "execution": "not-authorized",
            } for pid in ("a", "b", "c")],
            "appearances": [{"groupId": "g1", "identityId": "one", "photoIds": ["a"],
                             "evidenceKind": "face-view hypothesis"}],
            "associations": [{"identityIds": ["one", "two"], "kind": "lookalike", "role": None}],
        }

    def test_selection_bounds_pixels_not_evaluated_population(self):
        before = copy.deepcopy(self.candidate)
        self.assertEqual(realignment_report.select_photos(self.candidate, maximum=2), ["a", "b"])
        self.assertEqual(before, self.candidate)
        with self.assertRaisesRegex(ValueError, "positive"):
            realignment_report.select_photos(self.candidate, maximum=0)

    def test_candidate_contract_refuses_locks_photo_loss_and_inferred_family(self):
        realignment_report.validate_candidate(self.candidate, self.run)
        for field in ("execution", "reconsiderable", "photoId"):
            with self.subTest(field=field):
                bad = copy.deepcopy(self.candidate)
                bad["rows"][0][field] = {
                    "execution": "install", "reconsiderable": False, "photoId": "unknown",
                }[field]
                with self.assertRaises(ValueError):
                    realignment_report.validate_candidate(bad, self.run)
        bad = copy.deepcopy(self.candidate)
        bad["associations"][0]["role"] = "mother"
        with self.assertRaisesRegex(ValueError, "family"):
            realignment_report.validate_candidate(bad, self.run)

    def test_assessment_sample_is_bounded_diverse_and_does_not_change_candidates(self):
        before = copy.deepcopy(self.candidate)
        self.assertEqual(realignment_report.assessment_sample(self.candidate), ["b"])
        self.assertEqual(self.candidate, before)
        rows = self.candidate["rows"]
        rows[0].update(currentFolder="Angels/Other", candidateFolder="Models/Two", blockers=["hold"])
        self.assertEqual(set(realignment_report.assessment_sample(self.candidate)), {"a", "b"})
        self.assertEqual(len(realignment_report.assessment_sample(self.candidate, maximum=1)), 1)
        rows[0]["origin"] = "explicit-intent"
        self.assertEqual(realignment_report.assessment_sample(self.candidate), ["b"])
        with self.assertRaisesRegex(ValueError, "positive"):
            realignment_report.assessment_sample(self.candidate, maximum=0)

    def test_impact_captures_selection_conflict_and_reference_needed_without_moves(self):
        result = realignment_report.impact_summary(self.candidate, self.run)
        self.assertEqual(result["crossFolderByOrigin"], {"automatic-hypothesis": 1})
        self.assertEqual(result["selectedPhotoConflicts"][0]["photoId"], "b")
        self.assertEqual(result["referenceNeededFolders"], ["Models/Two"])
        self.assertIn("zero installed", result["interpretation"])

    def test_render_has_whole_landscape_and_escapes_payload(self):
        page = realignment_report.render(self.candidate, {}, self.run, evaluation={"cases": []})
        for expected in ("Identity and reference landscape", "Too close to call", "Face-view",
                         "fictional", "family-import", "candidateSHA256", "realignment.json",
                         "assessment-export", "assessment-import", "clearing every safeguard"):
            self.assertIn(expected, page)
        for expected in ("Photo being checked", "Suggested identity examples", "Current identity examples",
                         "review-back", "review-next", "assessment-download", "data-judgment",
                         'id="advanced"', "Different person rejects only that match",
                         "No photos will move", "beforeunload"):
            self.assertIn(expected, page)
        self.assertNotIn('id="assessment-choice"', page)
        self.assertNotIn("<script>unsafe</script>", page)
        self.assertIn("\\u003cscript>", page)
        self.assertNotIn("{{DATA}}", page)

    def test_comparisons_separate_target_from_other_rivals_and_exclude_query_content(self):
        row = self.candidate["rows"][1]
        self.candidate["identities"][1]["referencePhotoIds"] = ["b", "c"]
        row["evidence"]["topCandidates"].insert(0, {
            "folder": "Models/Two", "referencePhotoIds": ["b", "c"],
        })
        before = copy.deepcopy((self.run, self.candidate))
        refs = realignment_report.comparison_photos(self.candidate, self.run)
        self.assertEqual(refs["b"], {"current": ["c"], "target": ["a"]})
        self.assertEqual(before, (self.run, self.candidate))
        self.run["photos"][2]["preparedSHA256"] = self.run["photos"][1]["preparedSHA256"]
        refs = realignment_report.comparison_photos(self.candidate, self.run)
        self.assertEqual(refs["b"]["current"], [])
        row["evidence"]["topCandidates"] = []
        self.assertEqual(realignment_report.comparison_photos(self.candidate, self.run)["b"]["target"], ["a"])
        row["candidateFolder"] = None
        self.assertEqual(realignment_report.comparison_photos(self.candidate, self.run)["b"]["target"], [])

    def test_unsafe_source_or_impact_conservation_refuses(self):
        self.run["photos"][0]["destination"] = "../outside.png"
        with self.assertRaisesRegex(ValueError, "unsafe"):
            realignment_report.render(self.candidate, {}, self.run, evaluation={})
        self.run["finalMembershipAudit"]["rows"].pop()
        with self.assertRaisesRegex(ValueError, "conservation"):
            realignment_report.impact_summary(self.candidate, self.run)

    def test_diagnostic_masks_answers_pairs_and_all_reference_influence(self):
        packet = {
            "characters": [{"folder": "Models/One", "cards": [{"photoId": pid} for pid in ("a", "b", "c")]}],
        }
        answers = {"characters": [{
            "folder": "Models/One", "decisions": [
                {"photoId": "a", "choice": "reference"},
                {"photoId": "b", "choice": "same-not-reference"},
                {"photoId": "c", "choice": "different"},
            ],
        }]}
        effective = {"pairs": [
            {"photoIds": ["a", "b"], "label": "same"},
            {"photoIds": ["a", "c"], "label": "different"},
        ], "observations": [{"photoId": "b", "rawLabel": "same"}]}
        before = copy.deepcopy((packet, answers, effective))

        def evaluator(run, vectors, masked_packet, masked_answers, labels, *, excluded_reference_ids):
            self.assertEqual(excluded_reference_ids, ["b", "c"])
            self.assertEqual(masked_packet["characters"][0]["cards"], [{"photoId": "a"}])
            self.assertEqual(len(masked_answers["characters"][0]["decisions"]), 1)
            self.assertEqual(labels["pairs"], [])
            self.assertNotIn("observations", labels)
            return self.candidate

        result = realignment_evaluation.evaluate(self.run, {}, packet, answers, effective, evaluator)
        self.assertEqual(before, (packet, answers, effective))
        self.assertEqual(result["maskedPhotoCount"], 2)
        self.assertEqual(result["removedIncidentPairCount"], 2)
        self.assertEqual(result["summary"]["positive-target-proposed"], 1)
        self.assertEqual(result["qualifiedPositiveCount"], 1)
        self.assertEqual(result["summary"]["negative-not-attracted"], 1)
        json.dumps(result, allow_nan=False)
        self.candidate["rows"][1]["blockers"] = [
            "diagnostic-reference-exclusion", "equal-content-diagnostic-exclusion",
        ]
        excluded = realignment_evaluation.evaluate(self.run, {}, packet, answers, effective, evaluator)
        self.assertEqual(excluded["qualifiedPositiveCount"], 1)
        self.candidate["rows"][1]["blockers"].append("insufficient-support")
        blocked = realignment_evaluation.evaluate(self.run, {}, packet, answers, effective, evaluator)
        self.assertEqual(blocked["summary"]["positive-target-proposed"], 1)
        self.assertEqual(blocked["qualifiedPositiveCount"], 0)
        contaminated = copy.deepcopy(self.candidate)
        contaminated["identities"][0]["referencePhotoIds"].append("b")
        with self.assertRaisesRegex(ValueError, "leaked"):
            realignment_evaluation.evaluate(
                self.run, {}, packet, answers, effective, lambda *args, **kwargs: contaminated,
            )


if __name__ == "__main__":
    unittest.main()
