#!/usr/bin/env python3
"""Tests for frozen-core, deterministic Review and pool reconciliation."""
import contextlib
import copy
import hashlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.art.likeness_library.reconciliation import (  # noqa: E402
    frozen_identity_cores,
    fragment_proposals,
    plan_reconciliation,
)
from tools.art import likeness  # noqa: E402
from tools.art.likeness import apply_category_changes  # noqa: E402


def candidate(photo_id, vector, *, folder="Various", bucket="Pool", side="Prospects", **values):
    return {
        "photoId": photo_id,
        "sourceFolder": folder,
        "sourceBucket": bucket,
        "side": side,
        "vector": np.asarray(vector, dtype=float),
        **values,
    }


def stable_name(seed, taken):
    name = f"New-{seed[:8]}"
    return f"Other-{seed[:8]}" if name.casefold() in taken else name


class NormalAdmissionTests(unittest.TestCase):
    def setUp(self):
        from tools.art.likeness_library import normal_admission
        from tools.art.likeness_library.policy import load_policy, effective_settings

        self.admission = normal_admission
        self.policy = load_policy()
        self.settings = effective_settings({}, self.policy)
        self.axes = np.eye(7)
        self.cores, self.references = {}, {}
        self.identity("Sisters/Drakness", self.axes[0], self.axes[3])
        self.api = SimpleNamespace(plan_reconciliation=plan_reconciliation, invent_name=stable_name)

    def without_home_lead(self):
        # Round/release mechanics fixtures move members their own core also matches;
        # IU13a's beat-home rule is covered by its own tests.
        self.policy["photoRouting"]["minimumOwnCoreLead"] = -2.

    def identity(self, folder, center, axis):
        rows = [
            {"photoId": f"{folder}:{index}",
             "sha256": hashlib.sha256(f"{folder}:{index}".encode()).hexdigest(),
             "vector": .8 * center + sign * .6 * axis, "qualityEligible": True}
            for index, sign in enumerate((1, -1))
        ]
        self.references[folder] = rows
        self.cores[folder] = {
            "vector": center.copy(), "side": "Prospects", "category": folder.split("/")[0],
            "corePhotoIds": [row["photoId"] for row in rows], "personIds": [folder],
            "identityProtected": folder.startswith(("Sisters/", "Angels/")),
            "photoScores": {}, "mode": "fixture",
        }

    def photo(self, vector, photo_id="photo:image_123", **kwargs):
        return candidate(
            photo_id, vector, qualityEligible=True, sha256=f"bytes:{photo_id}", **kwargs,
        )

    def red_evidence(self, rows):
        result = []
        for row in rows:
            row.setdefault(
                "currentPath",
                f'{row["sourceFolder"]}/{row["sourceBucket"].lower()}/{row["photoId"].replace(":", "_")}.jpg',
            )
            result.append({
                "photoId": row["photoId"], "owner": row["sourceFolder"],
                "bucket": row["sourceBucket"].lower(), "currentPath": row["currentPath"],
                "nativeSha256": row["sha256"], "score": row.get("redScore"),
            })
        return result

    def route(self, rows, **kwargs):
        ctx = self.admission.context(self.cores, self.references, self.policy, **kwargs)
        return plan_reconciliation(
            rows, self.cores, policy=self.policy, name_factory=stable_name, admission_context=ctx,
        )

    def paired(self):
        self.identity("Angels/Nyxene", .995 * self.axes[0] + np.sqrt(1 - .995 ** 2) * self.axes[1], self.axes[4])

    def nonvoting_fixture(self, *, folder="Various", bucket="Review", number=123):
        digest = "a" * 64
        row = self.photo(
            self.axes[0], photo_id=f"photo:image_{number}", folder=folder, bucket=bucket,
        )
        row.update({
            "source": f"{folder}/{bucket.lower()}/owner_image_{number}.jpg",
            "sourceHash": digest, "sha256": digest, "sourceStatus": "same-content-nonvoting",
            "contentVoteStatus": "nonvoting-duplicate-content",
            "contentVoteCanonicalId": "photo:image_900",
            "contentVoteCanonicalSource": "Models/Canonical/gallery/owner_image_900.jpg",
            "protected": False, "workflowSelected": False, "identityProtected": False,
            "explicitReviewPlacement": False, "rejectedPersonIds": [],
        })
        canonical = [{
            "photoId": "photo:image_900", "source": row["contentVoteCanonicalSource"],
            "sourceHash": digest,
        }]
        return row, canonical

    def nonvoting_route(self, candidates, canonical, *, cores=None, references=None, locked=False):
        return self.admission.score_nonvoting_duplicates(
            self.api, candidates, self.cores if cores is None else cores,
            self.references if references is None else references, self.settings, self.policy, canonical,
            locked=locked,
        )

    def test_nonvoting_duplicates_score_independently_without_votes_or_grouping(self):
        first, canonical = self.nonvoting_fixture()
        second, _ = self.nonvoting_fixture(number=124)
        original_references = copy.deepcopy(self.references)
        original_candidates = copy.deepcopy([first, second])
        report = self.nonvoting_route([first, second], canonical)
        self.assertEqual(len(report["results"]), 2)
        self.assertEqual(report["clusters"], [])
        for result in report["results"]:
            self.assertEqual(result["decision"]["bestMatch"], "Sisters/Drakness")
            self.assertAlmostEqual(result["decision"]["bestScore"], 1.)
            self.assertFalse(result["decision"]["referenceEligible"])
            self.assertEqual(result["decision"]["sourceBucket"], "Review")
            self.assertEqual(result["canonicalPhotoId"], "photo:image_900")
        for folder in self.references:
            for after, before in zip(self.references[folder], original_references[folder]):
                np.testing.assert_array_equal(after["vector"], before["vector"])
                self.assertEqual(after["photoId"], before["photoId"])
        for after, before in zip((first, second), original_candidates):
            np.testing.assert_array_equal(after["vector"], before["vector"])
            self.assertEqual(after["sourceBucket"], before["sourceBucket"])

    def test_nonvoting_self_content_removed_before_scoring_former_owner(self):
        row, canonical = self.nonvoting_fixture(folder="Sisters/Drakness", bucket="Gallery")
        source = "Sisters/Drakness"
        self.references[source][0]["sha256"] = row["sha256"]
        report = self.nonvoting_route([row], canonical)
        result = report["results"][0]
        self.assertAlmostEqual(result["decision"]["bestScore"], .8)
        self.assertEqual(result["decision"]["bestMatch"], source)
        self.assertEqual(result["decision"]["sourceBucket"], "Gallery")
        self.assertEqual(result["excludedReferencePhotoIds"], [self.references[source][0]["photoId"]])
        self.assertFalse(result["decision"]["referenceEligible"])

    def test_nonvoting_guards_and_unavailable_scores_are_explicit(self):
        row, canonical = self.nonvoting_fixture()
        for changes, reason in (
            ({"qualityEligible": False}, "quality"),
            ({"protected": True}, "protected"),
            ({"workflowSelected": True}, "workflow"),
            ({"identityProtected": True}, "protected"),
            ({"rejectionMetadataStale": True}, "stale"),
            ({"explicitReviewPlacement": True}, "explicit Review"),
            ({"vector": None}, "vector"),
            ({"vector": "not-a-vector"}, "vector"),
            ({"vector": np.full(7, 1e308)}, "vector"),
        ):
            with self.subTest(changes=changes):
                result = self.nonvoting_route([{**row, **changes}], canonical)["results"][0]
                self.assertIn(reason, result["decision"]["reason"])
                self.assertIsNone(result["decision"].get("bestScore"))
                self.assertFalse(result["decision"]["referenceEligible"])
        result = self.nonvoting_route([row], canonical, cores={}, references={})["results"][0]
        self.assertIsNone(result["decision"].get("bestScore"))
        self.assertIsNone(result["decision"].get("destination"))
        self.assertEqual(result["scoreStatus"], "unavailable")

    def test_nonvoting_respects_rejections_and_cast_receiving_lock(self):
        row, canonical = self.nonvoting_fixture()
        rejected = self.nonvoting_route(
            [{**row, "rejectedPersonIds": ["Sisters/Drakness"]}], canonical,
        )["results"][0]
        self.assertIsNone(rejected["decision"].get("bestMatch"))
        self.assertIsNone(rejected["decision"].get("bestScore"))
        self.assertEqual(rejected["scoreStatus"], "unavailable")
        locked = self.nonvoting_route([row], canonical, locked=True)["results"][0]
        self.assertTrue(locked["decision"]["preserveStaged"])
        self.assertIn("locked", locked["decision"]["reason"])
        self.assertFalse(locked["decision"]["referenceEligible"])

    def test_nonvoting_matching_content_cannot_be_its_only_reference(self):
        row, canonical = self.nonvoting_fixture()
        folder = "Sisters/Drakness"
        ref = {**self.references[folder][0], "sha256": row["sha256"]}
        cores = {folder: {**self.cores[folder], "vector": ref["vector"],
                          "corePhotoIds": [ref["photoId"]]}}
        result = self.nonvoting_route(
            [row], canonical, cores=cores, references={folder: [ref]},
        )["results"][0]
        self.assertEqual(result["excludedReferencePhotoIds"], [ref["photoId"]])
        self.assertEqual(result["scoreStatus"], "unavailable")
        self.assertIsNone(result["decision"]["bestScore"])
        self.assertIsNone(result["decision"].get("destination"))

    def test_nonvoter_follows_bound_voting_cluster_without_self_vote(self):
        row, canonical = self.nonvoting_fixture()
        row["measurementSha256"] = row["sha256"]
        second = "photo:image_901"
        ids = sorted([canonical[0]["photoId"], second])
        cluster_id = hashlib.sha256("\n".join(ids).encode()).hexdigest()[:16]
        voters = [
            {"photoId": ids[0], "source": canonical[0]["source"], "sha256": row["sha256"],
             "measurementSha256": row["sha256"], "sourceFolder": "Models/Canonical",
             "sourceBucket": "Gallery", "vector": self.axes[0], "qualityEligible": True},
            {"photoId": ids[1], "source": "Various/gallery/image_901.jpg", "sha256": "b" * 64,
             "measurementSha256": "b" * 64, "sourceFolder": "Various",
             "sourceBucket": "Pool", "vector": self.axes[3], "qualityEligible": True},
        ]
        decisions = [
            {"photoId": voter["photoId"], "sourceFolder": voter["sourceFolder"],
             "sourceBucket": voter["sourceBucket"], "destination": "Potentials/New",
             "destinationType": "provisional", "clusterId": cluster_id,
             "referenceVersion": "final-round", "normalAdmission": True}
            for voter in voters
        ]
        cluster = {"clusterId": cluster_id, "destination": "Potentials/New",
                   "destinationType": "provisional", "photoIds": ids, "corePhotoIds": ids}
        scored = self.nonvoting_route([row], canonical)
        before = copy.deepcopy((decisions, cluster))
        result = self.admission.follow_nonvoting_provisional(
            scored, [row], voters, decisions, [cluster],
        )["results"][0]
        self.assertEqual(result["decision"]["destination"], "Potentials/New")
        self.assertFalse(result["decision"]["referenceEligible"])
        self.assertEqual(result["provisionalEvidence"]["independentReferencePhotoIds"], [second])
        self.assertEqual(result["provisionalEvidence"]["score"], 0.)
        self.assertEqual((decisions, cluster), before)
        only_self = {**cluster, "corePhotoIds": [ids[0]]}
        unavailable = self.admission.follow_nonvoting_provisional(
            scored, [row], voters, decisions, [only_self],
        )["results"][0]
        self.assertEqual(unavailable["provisionalEvidence"]["scoreStatus"], "unavailable")
        self.assertIsNone(unavailable["decision"]["bestScore"])
        self.assertEqual(unavailable["decision"]["destination"], "Potentials/New")
        rejected = self.admission.follow_nonvoting_provisional(
            scored, [{**row, "rejectedPersonIds": ["person:rejected"]}],
            voters, decisions, [cluster],
        )["results"][0]
        self.assertTrue(rejected["decision"]["preserveStaged"])
        self.assertIsNone(rejected["decision"]["destination"])
        for changes in ({"qualityEligible": False}, {"rejectionMetadataStale": True},
                        {"explicitReviewPlacement": True}, {"vector": None}):
            held = self.admission.follow_nonvoting_provisional(
                scored, [{**row, **changes}], voters, decisions, [cluster],
            )["results"][0]
            self.assertTrue(held["decision"]["preserveStaged"])
            self.assertIsNone(held["decision"]["destination"])
            if changes.get("qualityEligible") is False or changes.get("rejectionMetadataStale") or "vector" in changes:
                self.assertEqual(held["scoreStatus"], "unavailable")
        for bad_voters, bad_decisions, bad_clusters in (
            (voters, decisions + [decisions[0]], [cluster]),
            (voters, decisions, [cluster, cluster]),
            ([{**voters[0], "source": "Models/Wrong/gallery/image_900.jpg"}, voters[1]], decisions, [cluster]),
            ([{**voters[0], "measurementSha256": "c" * 64}, voters[1]], decisions, [cluster]),
            ([{**voters[0], "vector": self.axes[4]}, voters[1]], decisions, [cluster]),
            (voters, decisions, [{**cluster, "corePhotoIds": ["photo:unknown"]}]),
        ):
            with self.subTest(bad_clusters=bad_clusters), self.assertRaises(ValueError):
                self.admission.follow_nonvoting_provisional(
                    scored, [row], bad_voters, bad_decisions, bad_clusters,
                )

    def test_nonvoting_reports_measured_comparisons_below_routing_threshold(self):
        row, canonical = self.nonvoting_fixture()
        row["vector"] = self.axes[6]
        result = self.nonvoting_route([row], canonical)["results"][0]
        self.assertTrue(result["decision"]["preserveStaged"])
        self.assertIsNone(result["decision"]["bestScore"])
        self.assertEqual(result["scoreStatus"], "available")
        self.assertEqual(result["comparisons"], [{"folder": "Sisters/Drakness", "score": 0.}])
        blocked = self.nonvoting_route([{**row, "protected": True}], canonical)["results"][0]
        self.assertIsNone(blocked["decision"].get("destination"))
        self.assertEqual(blocked["comparisons"], result["comparisons"])

    def test_nonvoting_rejects_provisional_cluster_results(self):
        row, canonical = self.nonvoting_fixture()
        decision = {
            "photoId": row["photoId"], "sourceFolder": row["sourceFolder"],
            "sourceBucket": "Pool", "destination": "Potentials/New",
            "destinationType": "provisional",
        }
        for clusters, candidate_decision in (([], decision),
                                             ([{"clusterId": "unexpected"}],
                                              {**decision, "destinationType": "existing"})):
            with self.subTest(clusters=clusters), mock.patch.object(
                self.api, "plan_reconciliation", return_value={
                    "assignments": [candidate_decision], "held": [], "clusters": clusters,
                },
            ), self.assertRaisesRegex(ValueError, "did not conserve"):
                self.nonvoting_route([row], canonical)

    def test_nonvoting_scoring_refuses_bad_bindings_and_reference_evidence(self):
        row, canonical = self.nonvoting_fixture()
        for changes in ({"sourceHash": "b" * 64}, {"contentVoteCanonicalId": "photo:wrong"},
                        {"sourceStatus": "eligible"}, {"sourceFolder": "Models/Wrong"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.nonvoting_route([{**row, **changes}], canonical)
        with self.assertRaises(ValueError):
            self.nonvoting_route([row, row], canonical)
        with self.assertRaises(ValueError):
            self.nonvoting_route([row], [*canonical, canonical[0]])
        for field in ("protected", "workflowSelected", "identityProtected",
                      "explicitReviewPlacement", "rejectedPersonIds"):
            incomplete = dict(row)
            del incomplete[field]
            with self.subTest(missing=field), self.assertRaisesRegex(ValueError, "guard"):
                self.nonvoting_route([incomplete], canonical)
        with self.assertRaisesRegex(ValueError, "guard"):
            self.nonvoting_route([{**row, "workflowSelected": "false"}], canonical)
        refs = copy.deepcopy(self.references)
        refs["Sisters/Drakness"][0]["qualityEligible"] = False
        with self.assertRaises(ValueError):
            self.nonvoting_route([row], canonical, references=refs)
        refs = copy.deepcopy(self.references)
        refs["Sisters/Drakness"][1]["sha256"] = refs["Sisters/Drakness"][0]["sha256"]
        with self.assertRaisesRegex(ValueError, "duplicate reference content"):
            self.nonvoting_route([row], canonical, references=refs)
        other = {**row, "photoId": "photo:image_900",
                 "source": "Various/review/owner_image_900.jpg",
                 "contentVoteCanonicalId": row["photoId"],
                 "contentVoteCanonicalSource": row["source"]}
        more_canonical = [*canonical, {
            "photoId": row["photoId"], "source": row["source"], "sourceHash": row["sourceHash"],
        }]
        with self.assertRaisesRegex(ValueError, "canonical.*candidate"):
            self.nonvoting_route([row, other], more_canonical)

    def empty_voting_report(self):
        return self.admission.two_round_plan(
            self.api, [], self.cores, self.references, self.settings, self.policy, set(),
        )

    def test_existing_nonvoting_review_and_various_holds_are_independently_reconsidered(self):
        review, canonical = self.nonvoting_fixture(folder="Models/Former")
        various, _ = self.nonvoting_fixture(bucket="Gallery", number=124)
        various["sourceBucket"] = "Pool"
        report = self.empty_voting_report()
        original = copy.deepcopy(report)
        result = self.admission.reconsider_nonvoting_holds(
            self.api, [review, various], self.cores, self.references, self.settings, self.policy,
            canonical, [], report,
        )
        self.assertEqual(result["clusters"], [])
        self.assertEqual(report, original)
        for item in result["results"]:
            self.assertEqual(item["decision"]["destination"], "Sisters/Drakness")
            self.assertFalse(item["decision"]["referenceEligible"])
            self.assertEqual(item["scoreStatus"], "available")
        self.assertEqual(result["retiredReferenceIds"], [])

    def test_existing_nonvoting_holds_keep_quality_protection_and_rejection_gates(self):
        row, canonical = self.nonvoting_fixture()
        report = self.empty_voting_report()
        for changes in (
            {"qualityEligible": False}, {"protected": True}, {"workflowSelected": True},
            {"identityProtected": True}, {"explicitReviewPlacement": True},
            {"rejectionMetadataStale": True}, {"vector": None},
            {"rejectedPersonIds": ["Sisters/Drakness"]},
        ):
            with self.subTest(changes=changes):
                result = self.admission.reconsider_nonvoting_holds(
                    self.api, [{**row, **changes}], self.cores, self.references, self.settings,
                    self.policy, canonical, [], report,
                )["results"][0]["decision"]
                self.assertTrue(result["preserveStaged"])
                self.assertFalse(result["referenceEligible"])
                self.assertFalse(result.get("destination"))
                self.assertFalse(result.get("reviewDestination"))
        with self.assertRaisesRegex(ValueError, "Review or Various"):
            gallery, other_canonical = self.nonvoting_fixture(folder="Models/Former", bucket="Gallery")
            self.admission.reconsider_nonvoting_holds(
                self.api, [gallery], self.cores, self.references, self.settings, self.policy,
                other_canonical, [], report,
            )

    def test_existing_nonvoting_no_reference_and_stale_bindings_hold_or_fail(self):
        row, canonical = self.nonvoting_fixture()
        self.cores, self.references = {}, {}
        report = self.empty_voting_report()
        result = self.admission.reconsider_nonvoting_holds(
            self.api, [row], self.cores, self.references, self.settings, self.policy,
            canonical, [], report,
        )["results"][0]
        self.assertTrue(result["decision"]["preserveStaged"])
        self.assertEqual(result["scoreStatus"], "unavailable")
        self.assertEqual(result["comparisons"], [])
        self.assertIsNone(result["decision"]["bestScore"])
        for changes in (
            {"sourceHash": "b" * 64}, {"contentVoteCanonicalId": "photo:wrong"},
            {"source": "Various/review/owner_image_999.jpg"},
            {"source": "../Various/review/owner_image_123.jpg"}, {"side": "Artists"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.admission.reconsider_nonvoting_holds(
                    self.api, [{**row, **changes}], self.cores, self.references, self.settings,
                    self.policy, canonical, [], report,
                )

    def test_final_nonvoting_references_remove_second_round_departures(self):
        self.without_home_lead()
        seed, second, survivor, released, _ = self.residual_integration_fixture()
        candidates = [seed, second, released]
        report = self.admission.two_round_plan(
            self.api, candidates, self.cores, self.references, self.settings, self.policy, set(),
        )
        final = self.admission.final_nonvoting_references(
            self.cores, self.references, candidates, report, self.policy,
        )
        self.assertEqual(final["retiredReferenceIds"], [second["photoId"]])
        self.assertIn(second["sha256"], final["retiredReferenceSHA256"])
        self.assertEqual(final["cores"]["Models/Fragment"]["corePhotoIds"], [survivor["photoId"]])
        self.assertNotEqual(final["referenceVersion"], report["referenceSnapshots"]["2"]["referenceVersion"])
        stale = copy.deepcopy(report)
        stale["referenceSnapshots"]["2"]["referenceVersion"] = "stale"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.admission.final_nonvoting_references(
                self.cores, self.references, candidates, stale, self.policy,
            )
        stale = copy.deepcopy(report)
        stale["matchingRounds"][1]["retiredReferenceIds"].append("photo:missing")
        with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
            self.admission.final_nonvoting_references(
                self.cores, self.references, candidates, stale, self.policy,
            )

    def provisional_nonvoting_fixture(self):
        row, canonical = self.nonvoting_fixture()
        row["measurementSha256"] = row["sha256"]
        second = "photo:image_901"
        ids = sorted([canonical[0]["photoId"], second])
        cluster_id = hashlib.sha256("\n".join(ids).encode()).hexdigest()[:16]
        voters = [
            {"photoId": ids[0], "source": canonical[0]["source"], "sha256": row["sha256"],
             "measurementSha256": row["sha256"], "sourceFolder": "Models/Canonical",
             "sourceBucket": "Gallery", "vector": self.axes[0], "qualityEligible": True},
            {"photoId": ids[1], "source": "Various/gallery/image_901.jpg", "sha256": "b" * 64,
             "measurementSha256": "b" * 64, "sourceFolder": "Various", "sourceBucket": "Pool",
             "vector": .8 * self.axes[0] + .6 * self.axes[3], "qualityEligible": True},
        ]
        decisions = [
            {"photoId": voter["photoId"], "sourceFolder": voter["sourceFolder"],
             "sourceBucket": voter["sourceBucket"], "destination": "Potentials/New",
             "destinationType": "provisional", "clusterId": cluster_id,
             "referenceVersion": "final-round", "normalAdmission": True}
            for voter in voters
        ]
        cluster = {"clusterId": cluster_id, "destination": "Potentials/New",
                   "destinationType": "provisional", "photoIds": ids, "corePhotoIds": ids}
        self.cores, self.references = {}, {}
        report = self.empty_voting_report()
        for decision in decisions:
            decision["referenceVersion"] = report["referenceSnapshots"]["2"]["referenceVersion"]
        report["assignments"] = decisions
        report["clusters"] = [cluster]
        return row, canonical, voters, report

    def test_existing_nonvoter_follows_only_independently_supported_provisional_group(self):
        row, canonical, voters, report = self.provisional_nonvoting_fixture()
        result = self.admission.reconsider_nonvoting_holds(
            self.api, [row], self.cores, self.references, self.settings, self.policy,
            canonical, voters, report,
        )["results"][0]
        self.assertEqual(result["decision"]["destination"], "Potentials/New")
        self.assertEqual(result["provisionalEvidence"]["independentReferencePhotoIds"], ["photo:image_901"])
        self.assertAlmostEqual(result["decision"]["bestScore"], .8)
        self.assertFalse(result["decision"]["referenceEligible"])
        self.assertNotIn(row["photoId"], report["clusters"][0]["photoIds"])
        stale = copy.deepcopy(report)
        for decision in stale["assignments"]:
            decision["referenceVersion"] = "stale"
        with self.assertRaisesRegex(ValueError, "cluster reference version differs"):
            self.admission.reconsider_nonvoting_holds(
                self.api, [row], self.cores, self.references, self.settings, self.policy,
                canonical, voters, stale,
            )
        voters[1]["vector"] = self.axes[3]
        result = self.admission.reconsider_nonvoting_holds(
            self.api, [row], self.cores, self.references, self.settings, self.policy,
            canonical, voters, report,
        )["results"][0]
        self.assertTrue(result["decision"]["preserveStaged"])
        self.assertIsNone(result["decision"].get("destination"))
        self.assertEqual(result["provisionalEvidence"]["score"], 0.)
        voters[1]["vector"] = self.axes[0]
        result = self.admission.reconsider_nonvoting_holds(
            self.api, [row], self.cores, self.references, self.settings, self.policy,
            canonical, voters, report,
        )["results"][0]
        self.assertTrue(result["decision"]["preserveStaged"])
        self.assertEqual(result["provisionalEvidence"]["independentReferencePhotoIds"], [])
        report["clusters"][0]["corePhotoIds"] = [voters[0]["photoId"]]
        result = self.admission.reconsider_nonvoting_holds(
            self.api, [row], self.cores, self.references, self.settings, self.policy,
            canonical, voters, report,
        )["results"][0]
        self.assertTrue(result["decision"]["preserveStaged"])
        self.assertEqual(result["provisionalEvidence"]["scoreStatus"], "unavailable")

    def test_existing_nonvoter_keeps_normal_existing_identity_over_provisional_follow(self):
        row, canonical, voters, report = self.provisional_nonvoting_fixture()
        self.identity("Sisters/Drakness", self.axes[0], self.axes[4])
        voting = self.empty_voting_report()
        voting["assignments"] = report["assignments"]
        voting["clusters"] = report["clusters"]
        result = self.admission.reconsider_nonvoting_holds(
            self.api, [row], self.cores, self.references, self.settings, self.policy,
            canonical, voters, voting,
        )["results"][0]
        self.assertEqual(result["decision"]["destination"], "Sisters/Drakness")
        self.assertNotIn("provisionalEvidence", result)

    def test_existing_nonvoter_provisional_follow_cannot_bypass_cast_lock_or_ambiguity(self):
        row, canonical, voters, report = self.provisional_nonvoting_fixture()
        self.identity("Sisters/Drakness", self.axes[0], self.axes[4])
        report["referenceSnapshots"] = self.empty_voting_report()["referenceSnapshots"]
        report["matchingRounds"] = self.empty_voting_report()["matchingRounds"]
        result = self.admission.reconsider_nonvoting_holds(
            self.api, [row], self.cores, self.references, self.settings, self.policy,
            canonical, voters, report, locked=True,
        )["results"][0]
        self.assertTrue(result["decision"]["preserveStaged"])
        self.assertIn("locked", result["decision"]["reason"])
        self.assertNotIn("provisionalEvidence", result)
        self.cores, self.references = {}, {}
        self.identity("Models/One", .7 * self.axes[0] + np.sqrt(.51) * self.axes[1], self.axes[4])
        self.identity("Models/Two", .69 * self.axes[0] + np.sqrt(1 - .69 ** 2) * self.axes[1], self.axes[5])
        report["referenceSnapshots"] = self.empty_voting_report()["referenceSnapshots"]
        report["matchingRounds"] = self.empty_voting_report()["matchingRounds"]
        result = self.admission.reconsider_nonvoting_holds(
            self.api, [row], self.cores, self.references, self.settings, self.policy,
            canonical, voters, report,
        )["results"][0]
        self.assertTrue(result["decision"]["preserveStaged"])
        self.assertIn("needs review", result["decision"]["reason"])
        self.assertNotIn("provisionalEvidence", result)

    def test_retired_reference_is_removed_before_rebuilding_without_mutating_sources(self):
        folder = "Sisters/Drakness"
        ids = list(self.cores[folder]["corePhotoIds"])
        cores, refs = self.admission.refresh_references(self.cores, self.references, retire_ids=[ids[0]])
        self.assertEqual(cores[folder]["corePhotoIds"], [ids[1]])
        np.testing.assert_allclose(cores[folder]["vector"], self.references[folder][1]["vector"])
        self.assertEqual([row["photoId"] for row in refs[folder]], [ids[1]])
        self.assertEqual(self.cores[folder]["corePhotoIds"], ids)
        self.assertEqual(len(self.references[folder]), 2)
        empty_cores, empty_refs = self.admission.refresh_references(self.cores, self.references, retire_ids=ids)
        self.assertNotIn(folder, empty_cores)
        self.assertNotIn(folder, empty_refs)
        cancelling = copy.deepcopy(self.references)
        cancelling[folder][1]["vector"] = -cancelling[folder][0]["vector"]
        zero_cores, zero_refs = self.admission.refresh_references(self.cores, cancelling)
        self.assertNotIn(folder, zero_cores)
        self.assertNotIn(folder, zero_refs)

    def test_retired_reference_content_cannot_vote_under_another_id(self):
        source = "Sisters/Drakness"
        self.identity("Angels/Other", self.axes[1], self.axes[4])
        duplicate = copy.deepcopy(self.references)
        duplicate["Angels/Other"][0]["sha256"] = duplicate[source][0]["sha256"]
        cores, refs = self.admission.refresh_references(
            self.cores, duplicate,
            retire_ids=[duplicate[source][0]["photoId"]],
            retire_sha256=[duplicate[source][0]["sha256"]],
        )
        self.assertEqual(len(refs[source]), 1)
        self.assertEqual(len(refs["Angels/Other"]), 1)
        self.assertNotIn(duplicate["Angels/Other"][0]["photoId"], cores["Angels/Other"]["corePhotoIds"])
        self.assertEqual(len(duplicate[source]), 2)
        self.assertEqual(len(duplicate["Angels/Other"]), 2)

    def test_red_refresh_census_reports_new_red_and_unavailable_scores(self):
        red, one, two, survivor = "r", "a", "b", "c"
        vectors = {red: np.array([0., 1.]), one: np.array([1., 0.]),
                   two: np.array([1., 0.]), survivor: np.array([-.2, np.sqrt(.96)])}
        prior_center = np.array([2., 1.]) / np.sqrt(5.)
        rows = [
            {"photoId": red, "owner": "Sisters/Owner", "sha256": red, "score": 0.,
             "coreMember": True, "coreSize": 3},
            *[{"photoId": item, "owner": "Sisters/Owner", "sha256": item, "score": float(1. / np.sqrt(2.)),
               "coreMember": True, "coreSize": 3} for item in (one, two)],
            {"photoId": survivor, "owner": "Sisters/Owner", "sha256": survivor,
             "score": float(vectors[survivor] @ prior_center), "coreMember": False, "coreSize": 3},
            {"photoId": "unscored", "owner": "Sisters/Owner", "sha256": "unscored", "score": None},
        ]
        result = self.admission.red_refresh_score_census(rows, {red}, vectors, self.policy["scoreBands"])
        self.assertEqual([row["photoId"] for row in result["newlyRed"]], [survivor])
        self.assertAlmostEqual(result["newlyRed"][0]["refreshedScore"], -.2)
        self.assertEqual(result["checkedCount"], 3)
        self.assertEqual(result["unavailable"][0]["photoId"], "unscored")
        stale = copy.deepcopy(rows)
        stale[1]["score"] = .9
        with self.assertRaisesRegex(ValueError, "not reproducible"):
            self.admission.red_refresh_score_census(stale, {red}, vectors, self.policy["scoreBands"])

    def test_rebuilt_review_census_finds_red_created_by_removing_noncore_members(self):
        vectors = np.array([
            [.6883224297497105, -.29416615321126327, .6630825793280521],
            [.13720175166576093, .9842629434522524, .11136488444099024],
            [-.15024461443903436, -.7987659237234364, -.5825800845637547],
            [-.6024423663068798, .7889159153980171, .12113989314125974],
            [-.6273078530859915, -.5422537111548693, .5589684876586656],
            [-.21185814674292425, -.09541615365648222, .9726314221122285],
            [-.8296027915595102, -.36434708961541085, -.4230962142650859],
            [.7441403320967994, .6680218261100546, -.0014163288647542657],
        ])
        scores = [.3364574467365479, -.3077687936112286, -.13815115107267137,
                  .10112908868580629, .7283103576838011, .7283103576838011,
                  .15086792763665183, -.5661599075225604]
        rows = [{
            "photoId": f"photo:{i}", "owner": "Sisters/Owner", "bucket": "gallery",
            "sha256": str(i), "score": score, "coreMember": i in (4, 5),
            "coreSize": 2, "coreMode": "provisional", "usable": True,
            "identityAnchor": False, "membershipExcluded": False, "protected": False,
            "state": "Core member" if i in (4, 5) else "Excluded from core",
        } for i, score in enumerate(scores)]
        rows.append({
            "photoId": "photo:review", "owner": "Sisters/Owner", "bucket": "review",
            "sha256": "6", "score": scores[6], "coreMember": False,
            "coreSize": 2, "coreMode": "provisional", "usable": True,
            "identityAnchor": False, "membershipExcluded": True, "protected": False, "state": "Review",
        })
        vector_map = {str(i): vector for i, vector in enumerate(vectors)}
        retiring = {f"photo:{i}" for i in (1, 2, 3, 7)}
        rules = copy.deepcopy(self.policy)
        rules["categoryPolicies"]["Sisters"]["identityCoreMinimumSimilarity"] = .3
        result = self.admission.rebuilt_red_review_census(rows, retiring, vector_map, rules)
        self.assertEqual([row["photoId"] for row in result["newlyRed"]], ["photo:6", "photo:review"])
        self.assertAlmostEqual(result["newlyRed"][0]["refreshedScore"], -.19417929053464925)
        self.assertEqual(result["checkedCount"], 5)
        self.assertTrue(result["planningOnly"])
        changed = copy.deepcopy(rows)
        changed[0]["score"] = .9
        with self.assertRaisesRegex(ValueError, "saved Review score"):
            self.admission.rebuilt_red_review_census(changed, retiring, vector_map, rules)
        changed = copy.deepcopy(rows)
        changed[0]["protected"] = True
        with self.assertRaisesRegex(ValueError, "unsupported"):
            self.admission.rebuilt_red_review_census(changed, retiring, vector_map, rules)

        destination_rows = [{
            "photoId": f"photo:target{i}", "owner": "Angels/Target", "bucket": "gallery",
            "sha256": "target", "score": 1., "coreMember": True,
            "coreSize": 3, "coreMode": "provisional", "usable": True,
            "identityAnchor": False, "membershipExcluded": False, "protected": False,
            "state": "Core member",
        } for i in range(3)]
        vector_map["target"] = np.array([1., 0., 0.])
        destinations = {photo_id: "Various" for photo_id in retiring}
        destinations["photo:1"] = "Angels/Target"
        result = self.admission.rebuilt_red_review_census(
            rows + destination_rows, retiring, vector_map, rules, destinations=destinations,
        )
        moved = {row["photoId"]: row for row in result["movedScores"]}
        self.assertAlmostEqual(moved["photo:1"]["score"], vectors[1][0])
        self.assertEqual(moved["photo:1"]["band"], "red")
        self.assertIsNone(moved["photo:2"]["score"])
        self.assertEqual(moved["photo:2"]["reason"], "unassigned Review has no identity score")
        with self.assertRaisesRegex(ValueError, "destination"):
            self.admission.rebuilt_red_review_census(
                rows + destination_rows, retiring, vector_map, rules, destinations={"photo:1": "Angels/Target"},
            )
        destination_review = {
            **destination_rows[0], "bucket": "review", "score": None, "coreMember": False,
            "coreSize": 0, "coreMode": "none", "state": "Review",
        }
        result = self.admission.rebuilt_red_review_census(
            rows + [destination_review], retiring, vector_map, rules, destinations=destinations,
        )
        moved = {row["photoId"]: row for row in result["movedScores"]}
        self.assertIsNone(moved["photo:1"]["score"])
        self.assertEqual(moved["photo:1"]["reason"], "destination comparison core unavailable")

    def test_checked_red_refresh_census_binds_affected_native_bytes(self):
        from tools.art.likeness_library import normal_recap

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            cache = root / "cache.json"
            cache.write_bytes(b"cache")
            cache_hash = hashlib.sha256(cache.read_bytes()).hexdigest()
            vectors, records = {}, []
            raw = {
                "r": (np.array([0., 1.]), 0., True),
                "a": (np.array([1., 0.]), float(1. / np.sqrt(2.)), True),
                "b": (np.array([1., 0.]), float(1. / np.sqrt(2.)), True),
                "c": (np.array([-.2, np.sqrt(.96)]),
                      float(np.array([-.2, np.sqrt(.96)]) @ (np.array([2., 1.]) / np.sqrt(5.))), False),
            }
            for name, (vector, score, member) in raw.items():
                path = root / f"{name}.jpg"
                path.write_bytes(name.encode())
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                vectors[digest] = vector
                records.append({
                    "row": {"photoId": name, "newPerson": "Sisters/Owner", "destination": path.name},
                    "record": {"contentSha256": digest, "scoreContext": {"coreMember": member, "coreSize": 3}},
                    "score": score,
                })
            first = records[0]
            snapshot = {
                "inputBindings": {}, "snapshotBands": self.policy["scoreBands"],
                "snapshotCandidates": [{"photoId": "r", "owner": "Sisters/Owner", "currentPath": "r.jpg",
                                        "nativeSha256": first["record"]["contentSha256"], "score": 0.}],
            }
            data = {"snapshotDiagnostics": [], "snapshotIdUnavailable": 0, "inputs": {}, "auditRecords": records}
            with mock.patch.object(normal_recap, "collect", return_value=data), \
                 mock.patch.object(self.admission, "_red_cache_vectors",
                                   return_value=(cache, cache_hash, vectors, set(), {})):
                result = self.admission.verified_red_refresh_census(root, root / "receipt.json", cache,
                                                                    snapshot, cache_hash)
                self.assertEqual([row["photoId"] for row in result["newlyRed"]], ["c"])
                (root / "c.jpg").write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "native changed"):
                    self.admission.verified_red_refresh_census(root, root / "receipt.json", cache,
                                                               snapshot, cache_hash)

    def test_red_gallery_inventory_rebuilds_all_rivals_and_refuses_missing_measurements(self):
        model = {
            "detector": {"name": "YuNet", "file": "face_detection_yunet_2023mar.onnx", "sha256": "1" * 64},
            "recognizer": {"name": "SFace", "file": "face_recognition_sface_2021dec.onnx", "sha256": "2" * 64},
            "opencv": "fixture", "alignment": "FaceRecognizerSF.alignCrop",
        }
        model_id = hashlib.sha256(
            json.dumps(model, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            (root / ".likeness-library.json").write_text("{}", encoding="utf-8")
            measurements = {}
            for group, person, vector, first in (
                ("Sisters", "Owner", [1., 0.], 100),
                ("Angels", "Rival", [0., 1.], 200),
            ):
                gallery = root / group / person / "gallery"
                gallery.mkdir(parents=True)
                for number in (first, first + 1):
                    payload = f"photo-{number}".encode()
                    (gallery / f"owner_image_{number}.jpg").write_bytes(payload)
                    measurements[hashlib.sha1(payload).hexdigest()] = {
                        "v": vector, "faces": 1, "px": 1000, "f2": 0.,
                        "alignmentEvidence": {
                            "state": "persisted", "sourceSha256": hashlib.sha256(payload).hexdigest(),
                            "model": model, "modelId": model_id,
                        },
                    }
            cache_path = root / "cache.json"
            cache_path.write_text(json.dumps({
                "centeringDomain": "general", "centeringMean": [0., 0.], "emb": measurements,
            }), encoding="utf-8")
            with mock.patch.object(self.admission.metadata, "load_catalog", return_value={"people": {}, "photos": {}}):
                result = self.admission.frozen_red_gallery_inventory(
                    likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                )
                self.assertEqual(set(result["cores"]), {"Sisters/Owner", "Angels/Rival"})
                self.assertEqual(len(result["nativeBindings"]), 4)
                self.assertEqual(len(result["referencePaths"]), 4)
                self.assertFalse(result["centeringPopulationVerified"])
                changed_path = root / "Sisters" / "Owner" / "gallery" / "owner_image_100.jpg"
                real_vectors = self.admission._red_cache_vectors

                def change_native(*args):
                    proof = real_vectors(*args)
                    changed_path.write_bytes(b"edited")
                    return proof

                with mock.patch.object(self.admission, "_red_cache_vectors", side_effect=change_native):
                    with self.assertRaisesRegex(ValueError, "native changed during collection"):
                        self.admission.frozen_red_gallery_inventory(
                            likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                        )
                changed_path.write_bytes(b"photo-100")
                with self.assertRaisesRegex(ValueError, "omits identity roots"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, {"paths": {"photoRoots": ["Sisters"]}}, self.policy, cache_path,
                        nonvoting_paths={},
                    )
                invalid = copy.deepcopy(measurements)
                first = next(iter(invalid))
                invalid[first] = {"faces": -1, "t": .5}
                cache_path.write_text(json.dumps({
                    "centeringDomain": "general", "centeringMean": [0., 0.], "emb": invalid,
                }), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "missing a current Gallery measurement"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                    )
                invalid = copy.deepcopy(measurements)
                invalid[first]["alignmentEvidence"]["sourceSha256"] = "0" * 64
                cache_path.write_text(json.dumps({
                    "centeringDomain": "general", "centeringMean": [0., 0.], "emb": invalid,
                }), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "not bound to native bytes"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                    )
                cache_path.write_text(json.dumps({
                    "centeringDomain": "general", "centeringMean": [0., 0.], "emb": measurements,
                }), encoding="utf-8")
                extra = root / "Angels" / "Rival" / "gallery" / "owner_image_202.jpg"
                extra.write_bytes(b"unmeasured")
                with self.assertRaisesRegex(ValueError, "missing a current Gallery measurement"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                    )
                cache_before = cache_path.read_bytes()

                class FakeEmbedder:
                    def __init__(self):
                        self.model_id = model_id

                    def load(self):
                        if not likeness.domains.READ_ONLY.get():
                            raise AssertionError("inference must remain read-only")

                    def __call__(self, path):
                        return {
                            "v": [0., 1.], "faces": 1, "px": 1000, "f2": 0.,
                            "alignmentEvidence": {
                                "state": "read-only-not-persisted",
                                "sourceSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                "modelId": self.model_id,
                            },
                        }

                    def _model_identity(self, _cv2):
                        return model, self.model_id

                with mock.patch.object(likeness, "Embedder", FakeEmbedder):
                    inferred = self.admission.frozen_red_gallery_inventory(
                        likeness, root, {}, self.policy, cache_path, nonvoting_paths={}, measure_missing=True,
                    )
                self.assertEqual(len(inferred["nativeBindings"]), 5)
                self.assertEqual(len(inferred["supplementalMeasurements"]), 1)
                self.assertTrue(inferred["currentModelBytesVerified"])
                self.assertFalse(inferred["supplementalMeasurementsPersisted"])
                self.assertEqual(cache_path.read_bytes(), cache_before)
                self.assertEqual(extra.read_bytes(), b"unmeasured")
                wrong_model = mock.Mock(model_id="wrong-model")
                with mock.patch.object(likeness, "Embedder", return_value=wrong_model):
                    with self.assertRaisesRegex(ValueError, "models differ"):
                        self.admission.frozen_red_gallery_inventory(
                            likeness, root, {}, self.policy, cache_path, nonvoting_paths={}, measure_missing=True,
                        )
                wrong_model.assert_not_called()
                extra.write_bytes(b"photo-100")
                with self.assertRaisesRegex(ValueError, "ambiguous voting authority"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                    )
                nonvoting = {extra.relative_to(root).as_posix(): hashlib.sha256(b"photo-100").hexdigest()}
                inventory = self.admission.frozen_red_gallery_inventory(
                    likeness, root, {}, self.policy, cache_path, nonvoting_paths=nonvoting,
                )
                self.assertEqual(inventory["nonvotingBindings"], nonvoting)
                self.assertNotIn("photo:image_202", inventory["referencePaths"])
                missing = {"Sisters/Owner/gallery/missing_image_999.jpg": "0" * 64}
                with self.assertRaisesRegex(ValueError, "missing or out-of-scope paths"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, {}, self.policy, cache_path, nonvoting_paths={**nonvoting, **missing},
                    )
                extra.write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "non-voting Gallery native changed"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, {}, self.policy, cache_path, nonvoting_paths=nonvoting,
                    )
                extra.write_bytes(b"photo-200")
                collapsed = self.admission.frozen_red_gallery_inventory(
                    likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                    collapse_identical_same_owner=True,
                )
                relative = extra.relative_to(root).as_posix()
                self.assertEqual(collapsed["derivedNonvotingBindings"][relative], {
                    "sha256": hashlib.sha256(b"photo-200").hexdigest(),
                    "keeper": "Angels/Rival/gallery/owner_image_200.jpg",
                })
                self.assertNotIn("photo:image_202", collapsed["referencePaths"])
                self.assertEqual(extra.read_bytes(), b"photo-200")
                config = {"photos": {"Rival": "owner_image_202_944x1104.png"}}
                with self.assertRaisesRegex(ValueError, "ambiguous voting authority"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, config, self.policy, cache_path, nonvoting_paths={},
                        collapse_identical_same_owner=True,
                    )
                config = {"photos": {"Rival": "unidentified.png"}}
                with self.assertRaisesRegex(ValueError, "ambiguous voting authority"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, config, self.policy, cache_path, nonvoting_paths={},
                        collapse_identical_same_owner=True,
                    )
                record = {"contentSha256": hashlib.sha256(b"photo-200").hexdigest(), "protected": True}
                with mock.patch.object(
                    self.admission.metadata, "load_catalog",
                    return_value={"people": {}, "photos": {"photo:image_200": record}},
                ):
                    with self.assertRaisesRegex(ValueError, "ambiguous voting authority"):
                        self.admission.frozen_red_gallery_inventory(
                            likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                            collapse_identical_same_owner=True,
                        )
                anchor_catalog = {
                    "people": {"owner": {"identityAnchors": ["photo:image_200"]}}, "photos": {},
                }
                with mock.patch.object(self.admission.metadata, "load_catalog", return_value=anchor_catalog):
                    with self.assertRaisesRegex(ValueError, "ambiguous voting authority"):
                        self.admission.frozen_red_gallery_inventory(
                            likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                            collapse_identical_same_owner=True,
                        )
                extra.write_bytes(b"photo-100")
                with self.assertRaisesRegex(ValueError, "ambiguous voting authority"):
                    self.admission.frozen_red_gallery_inventory(
                        likeness, root, {}, self.policy, cache_path, nonvoting_paths={},
                        collapse_identical_same_owner=True,
                    )

    def test_detached_cast_outlier_does_not_route_back_to_former_owner(self):
        red = self.photo(
            self.axes[0], folder="Sisters/Drakness", bucket="Gallery",
            detachedOutlier=True, redRelease=True,
        )
        context = self.admission.context(self.cores, self.references, self.policy)
        context["redRelease"] = True
        self.assertIsNone(self.admission.cast_route(red, self.cores, self.policy, context))
        red["redRelease"] = False
        self.assertEqual(
            self.admission.cast_route(red, self.cores, self.policy, context)[1]["destination"],
            "Sisters/Drakness",
        )
        self.identity("Angels/Other", self.axes[0], self.axes[4])
        red["redRelease"] = True
        context = self.admission.context(self.cores, self.references, self.policy)
        context["redRelease"] = True
        self.assertEqual(
            self.admission.cast_route(red, self.cores, self.policy, context)[1]["destination"],
            "Angels/Other",
        )

    def test_current_release_candidates_selects_exact_bands_and_review_cores(self):
        def row(number, score, *, bucket="Gallery", core=False):
            name = f"owner_image_{number}.jpg"
            return {
                "photoId": f"photo:image_{number}", "folder": "Sisters/Owner", "bucket": bucket,
                "name": name, "contentSha256": str(number) * 64, "score": score,
                "generationSource": f"Sisters/Owner/{bucket.lower()}/{name}",
                "scoreContext": {"coreMember": core, "coreSize": 2},
            }

        rows = [row(1, .149999, core=True), row(2, .15, core=True),
                row(3, .299999, bucket="Review"), row(4, .30), row(5, None)]
        red = self.admission.current_release_candidates(rows, self.policy)
        self.assertEqual([item["photoId"] for item in red["snapshotCandidates"]], ["photo:image_1"])
        selected = self.admission.current_release_candidates(rows, self.policy, release_bands=("red", "orange"))
        self.assertEqual({item["photoId"] for item in selected["snapshotCandidates"]},
                         {"photo:image_1", "photo:image_2", "photo:image_3"})
        self.assertEqual(selected["unavailableIds"], ["photo:image_5"])
        including_unscored = self.admission.current_release_candidates(
            rows, self.policy, release_bands=("red", "orange"), include_unscored=True,
        )
        self.assertEqual({item["photoId"] for item in including_unscored["snapshotCandidates"]},
                         {"photo:image_1", "photo:image_2", "photo:image_3", "photo:image_5"})
        self.assertIsNone(next(item for item in including_unscored["snapshotCandidates"]
                               if item["photoId"] == "photo:image_5")["score"])
        self.assertEqual(including_unscored["unavailableIds"], ["photo:image_5"])
        self.assertEqual({member["photoId"] for member in selected["snapshotCandidates"][0]["reviewCore"]},
                         {"photo:image_1", "photo:image_2"})
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.admission.current_release_candidates(rows + [copy.deepcopy(rows[0])], self.policy)
        bad = copy.deepcopy(rows)
        bad[2]["scoreContext"]["coreSize"] = 3
        with self.assertRaisesRegex(ValueError, "incomplete or inconsistent"):
            self.admission.current_release_candidates(bad, self.policy, release_bands=("red", "orange"))
        bad = copy.deepcopy(rows)
        bad[0]["generationSource"] = "Sisters/Owner/gallery/another.jpg"
        with self.assertRaisesRegex(ValueError, "invalid current Review path"):
            self.admission.current_release_candidates(bad, self.policy)

    def test_unscored_measurements_bind_cache_and_read_only_inference(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            cached_path, missing_path = root / "cached.jpg", root / "missing.jpg"
            cached_path.write_bytes(b"cached")
            missing_path.write_bytes(b"missing")
            cached_hash = hashlib.sha256(b"cached").hexdigest()
            missing_hash = hashlib.sha256(b"missing").hexdigest()
            data = {
                "faces": 1, "px": 100, "f2": 0, "v": [1., 0.],
                "alignmentEvidence": {"state": "persisted"},
            }
            cache_path = root / "cache.json"
            cache_path.write_text(json.dumps({
                "centeringMean": [0., 0.],
                "emb": {hashlib.sha1(b"cached").hexdigest(): data},
            }), encoding="utf-8")
            cache_hash = hashlib.sha256(cache_path.read_bytes()).hexdigest()
            candidates = [
                {"photoId": "cached", "nativeSha256": cached_hash, "currentPath": "cached.jpg", "score": None},
                {"photoId": "missing", "nativeSha256": missing_hash, "currentPath": "missing.jpg", "score": None},
            ]

            class Embedder:
                model_id = "saved-model"

                def load(self):
                    self.read_only = likeness.domains.READ_ONLY.get()

                def __call__(self, path):
                    self.assert_path = path
                    return {
                        "faces": 1, "px": 100, "f2": 0, "v": [0., 1.],
                        "alignmentEvidence": {
                            "state": "read-only-not-persisted",
                            "sourceSha256": missing_hash, "modelId": self.model_id,
                        },
                    }

                def _model_identity(self, _cv2):
                    return {}, self.model_id

            embedder = Embedder()
            api = SimpleNamespace(domains=likeness.domains, Embedder=lambda: embedder)
            proof = (cache_path, cache_hash, {cached_hash: np.array([1., 0.])},
                     {"saved-model"}, {cached_hash: data})
            with mock.patch.object(self.admission, "_red_cache_vectors", return_value=proof):
                result = self.admission.measure_unscored_release_candidates(
                    api, root, cache_path, candidates, self.settings,
                )
                self.assertEqual(result["remeasuredCount"], 1)
                self.assertFalse(result["measurementsPersisted"])
                self.assertTrue(embedder.read_only)
                self.assertEqual(embedder.assert_path, missing_path)
                np.testing.assert_allclose(result["candidates"][1]["vector"], [0., 1.])
                self.assertTrue(all(row["qualityEligible"] for row in result["candidates"]))
                embedder.model_id = "different-model"
                with self.assertRaisesRegex(ValueError, "models differ"):
                    self.admission.measure_unscored_release_candidates(
                        api, root, cache_path, candidates, self.settings,
                    )
                missing_path.write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "native changed"):
                    self.admission.measure_unscored_release_candidates(
                        api, root, cache_path, candidates, self.settings,
                    )

    def test_current_release_snapshot_refuses_stale_policy_and_native(self):
        from tools.art import gallery_maintenance

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            native = root / "Sisters" / "Owner" / "gallery" / "owner_image_123.jpg"
            native.parent.mkdir(parents=True)
            native.write_bytes(b"fixture")
            unscored = native.parent / "owner_image_124.jpg"
            unscored.write_bytes(b"unscored fixture")
            output = root / "report"
            output.mkdir()
            cache = root / "cache.json"
            cache.write_text("{}", encoding="utf-8")
            (output / ".gallery-maintenance-report-state.json").write_text("{}", encoding="utf-8")
            record = {
                "photoId": "photo:image_123", "folder": "Sisters/Owner", "bucket": "Gallery",
                "name": native.name, "generationSource": native.relative_to(root).as_posix(),
                "contentSha256": hashlib.sha256(b"fixture").hexdigest(), "score": .2,
                "scoreContext": {"coreMember": True, "coreSize": 1},
            }
            missing = {
                "photoId": "photo:image_124", "folder": "Sisters/Owner", "bucket": "Gallery",
                "name": unscored.name, "generationSource": unscored.relative_to(root).as_posix(),
                "contentSha256": hashlib.sha256(b"unscored fixture").hexdigest(), "score": None,
                "scoreContext": {"coreMember": False, "coreSize": 1},
            }
            review = output / "people_gallery_review.html"

            def write_review(policy):
                review.write_text(
                    '<script id="review-data">' + json.dumps([record, missing]) + '</script>'
                    '<script id="likeness-policy-data">' + json.dumps(policy) + '</script>',
                    encoding="utf-8",
                )

            write_review(self.policy)
            with mock.patch.object(gallery_maintenance, "folders", return_value=[]), \
                 mock.patch.object(gallery_maintenance, "reports_pending", return_value=False) as pending, \
                 mock.patch.object(self.admission, "verify_red_review_measurements",
                                   return_value={"scoreCount": 1}) as verify:
                snapshot = self.admission.verified_current_release_snapshot(
                    root, output, cache, {}, self.policy, release_bands=("red", "orange"),
                )
                self.assertEqual(len(snapshot["snapshotCandidates"]), 1)
                self.assertEqual(snapshot["nativeBindings"][record["generationSource"]], record["contentSha256"])
                snapshot = self.admission.verified_current_release_snapshot(
                    root, output, cache, {}, self.policy,
                    release_bands=("red", "orange"), include_unscored=True,
                )
                self.assertEqual(len(snapshot["snapshotCandidates"]), 2)
                self.assertEqual(snapshot["nativeBindings"][missing["generationSource"]], missing["contentSha256"])
                self.assertEqual(len(verify.call_args.args[2]), 1)
                pending.return_value = True
                with self.assertRaisesRegex(ValueError, "source bindings are stale"):
                    self.admission.verified_current_release_snapshot(root, output, cache, {}, self.policy)
                pending.return_value = False
                other_policy = copy.deepcopy(self.policy)
                other_policy["version"] = "different"
                write_review(other_policy)
                with self.assertRaisesRegex(ValueError, "policy differs"):
                    self.admission.verified_current_release_snapshot(root, output, cache, {}, self.policy)
                write_review(self.policy)
                native.write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "native differs"):
                    self.admission.verified_current_release_snapshot(
                        root, output, cache, {}, self.policy, release_bands=("red", "orange"),
                    )

    def test_current_release_census_never_applies(self):
        from tools.art.likeness_library import sandbox_red_release

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            snapshot = {
                "snapshotCandidates": [{"bucket": "gallery", "workflowSelected": True, "score": .1}],
                "unavailableIds": [], "releaseBands": ["orange", "red"],
                "reviewMeasurementProof": {"scoreCount": 1}, "reviewSHA256": "1" * 64,
            }
            args = ["--root", str(root), "--run-id", "census", "--current-review", str(root),
                    "--cache", str(root / "cache"), "--release-band", "red", "--release-band", "orange"]
            with mock.patch.object(sandbox_red_release.likeness.cw, "sandbox_work_root", return_value=root), \
                 mock.patch.object(sandbox_red_release.normal_admission, "verified_current_release_snapshot",
                                   return_value=snapshot) as verify, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(sandbox_red_release.main(args + ["--dry-run"]), 0)
                self.assertEqual(verify.call_args.kwargs["release_bands"], ["red", "orange"])
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    sandbox_red_release.main(args + ["--apply"])
                self.assertEqual(verify.call_count, 1)

    def test_current_lineage_conserves_moves_and_nonvoting_members(self):
        from tools.art.likeness_library import sandbox_red_release

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            reports = root / "_reports"
            journal = reports / "runs" / "prior" / "publication-journal.json"
            journal.parent.mkdir(parents=True)
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps({"plan": {"sourceRows": [{
                "source": "Sisters/Owner/gallery/owner_image_124.jpg",
                "sourceStatus": "same-content-nonvoting", "sourceHash": hashlib.sha256(b"same").hexdigest(),
            }]}}), encoding="utf-8")
            native = root / "Sisters" / "Owner" / "gallery" / "owner_image_124.jpg"
            native.parent.mkdir(parents=True)
            native.write_bytes(b"same")
            audit = root / "snapshot.html"
            prior_source = "Sisters/Owner/gallery/owner_image_123.jpg"
            destination = "Various/review/owner_image_123.jpg"
            digest = "1" * 64
            manifest = {
                "receipt": str(receipt), "inputs": {str(receipt): hashlib.sha256(receipt.read_bytes()).hexdigest()},
                "redCandidates": [{"photoId": "photo:image_123", "currentPath": prior_source, "nativeSha256": digest}],
            }
            manifest_path = audit.with_suffix(".report.json")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            journal.write_text(json.dumps({"runId": "prior", "bindings": {
                "snapshotReportManifestSHA256": manifest_hash}}), encoding="utf-8")
            prior = {"runId": "prior", "snapshotReportManifestSHA256": manifest_hash, "moves": [{
                "photoId": "photo:image_123", "source": prior_source, "destination": destination, "sha256": digest,
            }]}
            original = {
                "status": "applied", "workingRoot": str(root), "snapshotDiagnostics": [],
                "snapshotIdUnavailable": 0, "inputs": manifest["inputs"], "auditRecords": [
                    {"row": {"photoId": "photo:image_123", "source": prior_source,
                             "destination": prior_source, "preparedSHA256": digest}},
                    {"row": {"photoId": "photo:image_124", "source": native.relative_to(root).as_posix(),
                             "destination": native.relative_to(root).as_posix(), "newPerson": "Sisters/Owner",
                             "newBucket": "gallery", "preparedSHA256": hashlib.sha256(b"same").hexdigest()}},
                ],
            }
            review_dir = root / "review"
            review_dir.mkdir()
            review = review_dir / "people_gallery_review.html"
            records = [
                {"photoId": "photo:image_123", "generationSource": destination, "contentSha256": digest},
                {"photoId": "photo:image_124", "generationSource": native.relative_to(root).as_posix(),
                 "contentSha256": hashlib.sha256(b"same").hexdigest()},
            ]
            review.write_text('<script id="review-data">' + json.dumps(records) + '</script>', encoding="utf-8")
            snapshot = {"reviewSHA256": hashlib.sha256(review.read_bytes()).hexdigest()}
            with mock.patch.object(sandbox_red_release.likeness.cw, "storage_root", return_value=reports), \
                 mock.patch.object(sandbox_red_release, "check_publication", return_value=prior), \
                 mock.patch.object(sandbox_red_release.normal_recap, "collect", return_value=original):
                result = sandbox_red_release.verified_current_lineage(
                    root, receipt, audit, "prior", review_dir, snapshot,
                )
                self.assertEqual(result["conservedCount"], 2)
                self.assertEqual(result["nonvotingBindings"], {
                    native.relative_to(root).as_posix(): hashlib.sha256(b"same").hexdigest(),
                })
                moved = {
                    "photoId": "photo:image_124", "source": native.relative_to(root).as_posix(),
                    "destination": "Various/review/owner_image_124.jpg",
                    "sha256": hashlib.sha256(b"same").hexdigest(),
                }
                continuation = {"snapshotReportManifestSHA256": manifest_hash, "moves": [moved]}
                records[1]["generationSource"] = moved["destination"]
                review.write_text('<script id="review-data">' + json.dumps(records) + '</script>', encoding="utf-8")
                snapshot["reviewSHA256"] = hashlib.sha256(review.read_bytes()).hexdigest()
                with mock.patch.object(sandbox_red_release, "verified_release_chain",
                                       return_value=([prior, continuation], ["first", "second"])):
                    result = sandbox_red_release.verified_current_lineage(
                        root, receipt, audit, "prior", review_dir, snapshot, ("later",),
                    )
                    self.assertEqual(result["nonvotingBindings"], {})
                    moved["destination"] = "Sisters/Other/gallery/owner_image_124.jpg"
                    records[1]["generationSource"] = moved["destination"]
                    review.write_text('<script id="review-data">' + json.dumps(records) + '</script>',
                                      encoding="utf-8")
                    snapshot["reviewSHA256"] = hashlib.sha256(review.read_bytes()).hexdigest()
                    with self.assertRaisesRegex(ValueError, "not in an unassigned hold"):
                        sandbox_red_release.verified_current_lineage(
                            root, receipt, audit, "prior", review_dir, snapshot, ("later",),
                        )
                records[1]["generationSource"] = native.relative_to(root).as_posix()
                records[0]["generationSource"] = prior_source
                review.write_text('<script id="review-data">' + json.dumps(records) + '</script>', encoding="utf-8")
                snapshot["reviewSHA256"] = hashlib.sha256(review.read_bytes()).hexdigest()
                with self.assertRaisesRegex(ValueError, "does not conserve"):
                    sandbox_red_release.verified_current_lineage(root, receipt, audit, "prior", review_dir, snapshot)
                manifest_path.write_text("{}", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "not bound"):
                    sandbox_red_release.verified_current_lineage(root, receipt, audit, "prior", review_dir, snapshot)

    def test_release_chain_verifies_historical_sources_and_refuses_tampering(self):
        from tools.art.likeness_library import sandbox_red_release

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            reports = root / "_reports"
            digest = hashlib.sha256(b"photo").hexdigest()
            current = root / "b.jpg"
            current.write_bytes(b"photo")
            for index, run_id in enumerate(("first", "second")):
                backup = root / "_backup" / run_id
                backup.mkdir(parents=True)
                entries = []
                if index:
                    saved = backup / "saved.jpg"
                    saved.write_bytes(b"photo")
                    entries.append({"source": str(root / "a.jpg"), "backup": "saved.jpg", "sha256": digest})
                manifest = backup / "manifest.json"
                manifest.write_text(json.dumps({"entries": entries}), encoding="utf-8")
                report = reports / "library" / run_id / "report.json"
                report.parent.mkdir(parents=True)
                publication = {
                    "kind": "sandbox-red-release-experiment", "root": str(root), "runId": run_id,
                    "moves": [] if not index else [{"source": "a.jpg", "destination": "b.jpg", "sha256": digest}],
                    "unaffectedNativeSHA256": {},
                }
                if index:
                    publication["planSHA256"] = "bound-plan"
                report.write_text(json.dumps(publication), encoding="utf-8")
                journal = reports / "runs" / run_id / "publication-journal.json"
                journal.parent.mkdir(parents=True)
                journal.write_text(json.dumps({
                    "kind": "normal-publication", "status": "applied", "root": str(root), "runId": run_id,
                    "backup": str(backup), "backupManifestSHA256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                    "bindings": {"planSHA256": "bound-plan"} if index else {},
                    "after": {report.relative_to(root).as_posix(): hashlib.sha256(report.read_bytes()).hexdigest(),
                              "b.jpg" if index else "a.jpg": digest},
                    "removed": ["a.jpg"] if index else [],
                }), encoding="utf-8")
            results, hashes = sandbox_red_release.verified_release_chain(root, "_reports", "first", ["second"])
            self.assertEqual(len(results), 2)
            self.assertEqual(len(hashes), 2)
            saved.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "snapshot changed"):
                sandbox_red_release.verified_release_chain(root, "_reports", "first", ["second"])
            saved.write_bytes(b"photo")
            current.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "published content changed"):
                sandbox_red_release.verified_release_chain(root, "_reports", "first", ["second"])
            with self.assertRaisesRegex(ValueError, "repeats"):
                sandbox_red_release.verified_release_chain(root, "_reports", "first", ["first"])

    def test_current_release_apply_requires_matching_preview(self):
        from tools.art.likeness_library import sandbox_red_release

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            snapshot = {
                "snapshotCandidates": [{"bucket": "gallery", "workflowSelected": False, "score": .2}],
                "unavailableIds": [], "releaseBands": ["orange", "red"],
                "reviewMeasurementProof": {"scoreCount": 1}, "reviewSHA256": "1" * 64,
            }
            plan = {"moves": [{"photoId": "photo:image_123", "source": "a", "destination": "b", "reason": "hold"}],
                    "routing": {"emptySourceCores": [], "assignments": [],
                                "held": [{"photoId": "photo:image_123"}]}, "workflowSelected": []}
            args = ["--root", str(root), "--run-id", "release", "--current-review", str(root),
                    "--cache", str(root / "cache"), "--receipt", str(root / "receipt"),
                    "--report", str(root / "report"), "--prior-run", "previous",
                    "--release-band", "red", "--release-band", "orange"]
            with mock.patch.object(sandbox_red_release.likeness.cw, "sandbox_work_root", return_value=root), \
                 mock.patch.object(sandbox_red_release.normal_admission, "verified_current_release_snapshot",
                                   return_value=snapshot), \
                 mock.patch.object(sandbox_red_release, "verified_current_lineage", return_value={"conservedCount": 1}), \
                 mock.patch.object(sandbox_red_release, "checked_current_routing", return_value=plan), \
                 mock.patch.object(sandbox_red_release, "current_plan_binding", return_value=({}, "a" * 64)), \
                 mock.patch.object(sandbox_red_release, "publish_current_release") as publish, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(sandbox_red_release.main(args + ["--dry-run"]), 0)
                with self.assertRaisesRegex(ValueError, "differs from the authorized preview"):
                    sandbox_red_release.main(args + ["--apply", "--expected-plan-sha256", "b" * 64])
                self.assertFalse(publish.called)
                self.assertEqual(sandbox_red_release.main(
                    args + ["--apply", "--expected-plan-sha256", "a" * 64],
                ), 0)
                self.assertEqual(publish.call_count, 1)

    def test_current_release_publishes_and_recovers_orange_cohort(self):
        self._check_release_publishes_and_recovers(score=.2)

    def test_current_release_publishes_and_recovers_unscored_hold(self):
        self._check_release_publishes_and_recovers(score=None)

    def _check_release_publishes_and_recovers(self, *, score):
        from tools.art.likeness_library import metadata, normal_transaction, sandbox_red_release

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            source = root / "Sisters" / "Owner" / "gallery" / "owner_image_123.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"orange")
            other = root / "Sisters" / "Owner" / "gallery" / "owner_image_124.jpg"
            other.write_bytes(b"unaffected")
            cache = root / "cache.json"
            cache.write_bytes(b"cache")
            catalog = root / ".likeness-library.json"
            metadata.save_catalog({"schemaVersion": 1, "actions": [], "people": {}, "photos": {}}, catalog)
            before_catalog = catalog.read_bytes()
            digest = metadata.content_sha256(source)
            move = {"photoId": "photo:image_123", "source": source.relative_to(root).as_posix(),
                    "destination": "Various/review/owner_image_123.jpg", "sha256": digest, "reason": "hold"}
            snapshot = {
                "releaseBands": ["orange", "red"],
                "snapshotCandidates": [{"photoId": move["photoId"], "score": score,
                                        "scoreContext": {}, "comparison": None}],
                "allNativeBindings": {move["source"]: digest, other.relative_to(root).as_posix():
                                      metadata.content_sha256(other)},
                "nativeBindings": {move["source"]: digest},
            }
            lineage = {"receiptSHA256": "1", "priorJournalSHA256": "2", "continuationJournalSHA256": [],
                       "priorManifestSHA256": "3",
                       "currentReviewSHA256": "4", "nonvotingBindings": {}}
            plan = {
                "moves": [move], "cacheSHA256": metadata.content_sha256(cache), "catalog": {},
                "inventory": {"nativeBindings": {move["source"]: digest},
                              "catalogSHA256": metadata.content_sha256(catalog)},
                "routing": {"emptySourceCores": ["Sisters/Owner"], "assignments": [],
                            "held": [{"photoId": move["photoId"], **(
                                {"unscoredAssessment": {"bestRival": "Angels/Other",
                                                         "bestRivalScore": .7,
                                                         "qualityEligible": False,
                                                         "basis": "independent rival core"}}
                                if score is None else {}
                            )}]},
                "measurements": {digest: {}}, "workflowSelected": [move["photoId"]],
            }
            args = SimpleNamespace(
                run_id="orange-fixture", cache=str(cache), current_review="review", receipt="receipt",
                report="report", prior_run="prior",
            )

            def stage(_root, stage_root, moves, *_args, **_kwargs):
                stage_root.mkdir(parents=True)
                target = stage_root / pathlib.PurePosixPath(moves[0]["destination"])
                target.parent.mkdir(parents=True)
                target.write_bytes(source.read_bytes())
                (stage_root / ".likeness-library.json").write_bytes(before_catalog)
                return ([{"native": moves[0]["destination"], "sha256": digest}], {}, {})

            with mock.patch.object(sandbox_red_release.likeness.cw, "storage_root", return_value=root / "_reports"), \
                 mock.patch.object(sandbox_red_release.normal_admission, "_red_cache_vectors",
                                   return_value=(cache, plan["cacheSHA256"], {}, set(), {digest: {}})), \
                 mock.patch.object(sandbox_red_release.normal_products, "stage", side_effect=stage), \
                 mock.patch.object(sandbox_red_release.normal_admission, "verified_current_release_snapshot",
                                   return_value=snapshot), \
                 mock.patch.object(sandbox_red_release, "verified_current_lineage", return_value=lineage), \
                 mock.patch.object(sandbox_red_release, "current_plan_binding", return_value=({"bound": True}, "hash")), \
                 contextlib.redirect_stdout(io.StringIO()):
                sandbox_red_release.publish_current_release(
                    root, {}, self.policy, args, snapshot, lineage, plan, {"bound": True}, "hash",
                )
                target = root / pathlib.PurePosixPath(move["destination"])
                self.assertEqual(target.read_bytes(), b"orange")
                self.assertFalse(source.exists())
                report = json.loads((root / "_reports" / "library" / "orange-fixture" / "report.json").read_bytes())
                self.assertEqual(report["moves"][0]["band"], "unscored" if score is None else "orange")
                if score is None:
                    self.assertIsNone(report["moves"][0]["score"])
                    self.assertEqual(report["moves"][0]["unscoredAssessment"]["bestRivalScore"], .7)
                self.assertTrue(report["moves"][0]["workflowSelected"])
                self.assertFalse(report["workflowChangesApplied"])
                journal = root / "_reports" / "runs" / "orange-fixture" / "publication-journal.json"
                normal_transaction.recover(root, journal, apply=True)
                self.assertEqual(source.read_bytes(), b"orange")
                self.assertFalse(target.exists())
                self.assertEqual(catalog.read_bytes(), before_catalog)

    def test_red_hold_retires_anchor_and_group_without_changing_protection_or_other_photos(self):
        person_id, group_id = "person_" + "a" * 32, "group_" + "b" * 32
        red_id, other_id = "photo:image_123", "photo:image_124"
        red_hash, other_hash = "1" * 64, "2" * 64
        membership = {
            "personId": person_id, "groupId": group_id, "status": "supported", "coreUse": True,
            "reason": "supported", "referenceVersion": "3" * 64,
        }
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {person_id: {
                "id": person_id, "displayName": "Owner", "folder": "Sisters/Owner",
                "folderHistory": [], "identityAnchors": [red_id, other_id],
            }},
            "photos": {
                red_id: {"contentSha256": red_hash, "protected": True, "membership": copy.deepcopy(membership)},
                other_id: {"contentSha256": other_hash, "protected": False, "membership": copy.deepcopy(membership)},
            },
            "photoGroups": {group_id: {
                "id": group_id, "personId": person_id, "name": "core", "status": "supported",
                "memberPhotoIds": [red_id, other_id], "referencePhotoIds": [red_id, other_id],
                "sourcePersonIds": [], "history": [], "reason": "supported",
            }},
        }
        source = "Sisters/Owner/gallery/owner_image_123.jpg"
        move = {
            "photoId": red_id, "source": source, "destination": "Various/review/owner_image_123.jpg",
            "sha256": red_hash,
        }
        snapshot = [{
            "photoId": red_id, "owner": "Sisters/Owner", "bucket": "gallery",
            "currentPath": source, "nativeSha256": red_hash, "score": .1,
        }]
        original = copy.deepcopy(catalog)
        result = self.admission.red_release_hold_catalog(catalog, [move], snapshot, self.policy)
        updated = result["catalog"]
        self.assertEqual(catalog, original)
        self.assertTrue(updated["photos"][red_id]["protected"])
        self.assertNotIn("membership", updated["photos"][red_id])
        self.assertEqual(updated["photos"][other_id], catalog["photos"][other_id])
        self.assertEqual(updated["people"][person_id]["identityAnchors"], [other_id])
        self.assertEqual(updated["photoGroups"][group_id]["memberPhotoIds"], [other_id])
        self.assertEqual(updated["photoGroups"][group_id]["referencePhotoIds"], [other_id])
        self.assertEqual(result["retiredAnchors"], [{"photoId": red_id, "personId": person_id}])
        self.assertEqual(result["retiredGroups"], [{"photoId": red_id, "groupId": group_id}])
        binding = {"photoId": red_id, "currentPath": source, "sha256": red_hash}
        self.assertEqual(self.admission.retire_released_catalog(catalog, [binding]), result)
        for change in (
            {"currentPath": "Various/review/owner_image_123.jpg"},
            {"sha256": other_hash},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.admission.retire_released_catalog(catalog, [{**binding, **change}])
        with self.assertRaisesRegex(ValueError, "invalid released source"):
            self.admission.retire_released_catalog(catalog, [binding, binding])
        descriptive = {**binding, "currentPath": "Sisters/Owner/gallery/owner_pose_7.jpg"}
        with self.assertRaisesRegex(ValueError, "invalid released source"):
            self.admission.retire_released_catalog(catalog, [descriptive])
        with self.assertRaisesRegex(ValueError, "invalid released source"):
            self.admission.retire_released_catalog(catalog, [descriptive], {red_id: "owner_pose_7.jpg"})
        self.assertEqual(
            self.admission.retire_released_catalog(catalog, [descriptive], {red_id: "owner_image_123.jpg"}),
            result,
        )
        altered = copy.deepcopy(snapshot)
        altered[0]["score"] = .15
        with self.assertRaisesRegex(ValueError, "differs from checked red evidence"):
            self.admission.red_release_hold_catalog(catalog, [move], altered, self.policy)
        orange = self.admission.red_release_hold_catalog(
            catalog, [move], altered, self.policy, release_bands=("red", "orange"),
        )
        self.assertNotIn("membership", orange["catalog"]["photos"][red_id])
        for score in (.30, None):
            outside = copy.deepcopy(snapshot)
            outside[0]["score"] = score
            with self.assertRaises(ValueError):
                self.admission.red_release_hold_catalog(
                    catalog, [move], outside, self.policy, release_bands=("red", "orange"),
                )
        outside[0]["score"] = None
        unscored = self.admission.red_release_hold_catalog(
            catalog, [move], outside, self.policy, include_unscored=True,
        )
        self.assertNotIn("membership", unscored["catalog"]["photos"][red_id])
        with self.assertRaises(ValueError):
            self.admission.red_release_hold_catalog(
                catalog, [move], snapshot, self.policy, release_bands=("red", "yellow"),
            )
        changed = {**move, "destination": "Various/gallery/owner_image_123.jpg"}
        with self.assertRaisesRegex(ValueError, "differs from checked red evidence"):
            self.admission.red_release_hold_catalog(catalog, [changed], snapshot, self.policy)
        stale = copy.deepcopy(catalog)
        stale["photos"][red_id]["contentSha256"] = "4" * 64
        with self.assertRaisesRegex(ValueError, "catalogue content is stale"):
            self.admission.red_release_hold_catalog(stale, [move], snapshot, self.policy)

        destination_id = "person_" + "c" * 32
        catalog["people"][destination_id] = {
            "id": destination_id, "displayName": "Target", "folder": "Angels/Target",
            "folderHistory": [], "identityAnchors": [],
        }
        routed = {**move, "destination": "Angels/Target/gallery/owner_image_123.jpg", "reason": "qualified"}
        decision = {
            "photoId": red_id, "sourceFolder": "Sisters/Owner", "sourceBucket": "Gallery",
            "destination": "Angels/Target", "reason": "qualified", "referenceEligible": True,
        }
        plan = {"assignments": [decision], "held": [], "referenceVersion": "5" * 64, "planningOnly": True,
                "candidateCount": 1, "retiredReferenceIds": [red_id], "retiredReferenceSHA256": [red_hash]}
        with self.assertRaisesRegex(ValueError, "complete retired snapshot candidate set"):
            self.admission.red_release_routed_catalog(
                catalog, [routed], snapshot, self.policy, {**plan, "retiredReferenceSHA256": []},
            )
        result = self.admission.red_release_routed_catalog(catalog, [routed], snapshot, self.policy, plan)
        updated = result["catalog"]
        self.assertTrue(updated["photos"][red_id]["protected"])
        self.assertEqual(updated["photos"][red_id]["membership"]["personId"], destination_id)
        self.assertEqual(updated["photos"][red_id]["membership"]["sourcePersonIds"], [person_id])
        self.assertTrue(updated["photos"][red_id]["membership"]["coreUse"])
        self.assertEqual(updated["people"][person_id]["identityAnchors"], [other_id])
        self.assertEqual(updated["photos"][other_id], catalog["photos"][other_id])
        orange_plan = {**plan, "releaseBands": ["orange", "red"]}
        orange_snapshot = copy.deepcopy(snapshot)
        orange_snapshot[0]["score"] = .29
        with self.assertRaises(ValueError):
            self.admission.red_release_routed_catalog(catalog, [routed], orange_snapshot, self.policy, plan)
        orange_result = self.admission.red_release_routed_catalog(
            catalog, [routed], orange_snapshot, self.policy, orange_plan,
        )
        self.assertEqual(orange_result["catalog"]["photos"][red_id]["membership"]["personId"], destination_id)
        admission = {"mode": "optimistic-gallery", "winner": "Angels/Target", "score": .8,
                     "margin": .2, "alternatives": [], "closePairs": []}
        optimistic = {**plan, "assignments": [{**decision, "castAdmission": admission}]}
        with self.assertRaisesRegex(ValueError, "protected optimistic Gallery"):
            self.admission.red_release_routed_catalog(catalog, [routed], snapshot, self.policy, optimistic)
        unprotected = copy.deepcopy(catalog)
        unprotected["photos"][red_id]["protected"] = False
        optimistic_catalog = self.admission.red_release_routed_catalog(
            unprotected, [routed], snapshot, self.policy, optimistic,
        )["catalog"]
        optimistic_membership = optimistic_catalog["photos"][red_id]["membership"]
        self.assertEqual(optimistic_membership["status"], "tentative")
        self.assertFalse(optimistic_membership["coreUse"])
        self.assertEqual(optimistic_membership["assignmentEvidence"]["castAdmission"], admission)
        rejected = copy.deepcopy(catalog)
        rejected["photos"][red_id]["rejectedPersonIds"] = [destination_id]
        with self.assertRaisesRegex(ValueError, "explicitly rejected"):
            self.admission.red_release_routed_catalog(rejected, [routed], snapshot, self.policy, plan)
        with self.assertRaisesRegex(ValueError, "differs from red routing decision"):
            self.admission.red_release_routed_catalog(
                catalog, [{**routed, "destination": "Angels/Target/review/owner_image_123.jpg"}],
                snapshot, self.policy, plan,
            )
        review_decision = {**decision, "destination": None, "reviewDestination": "Angels/Target/review"}
        review_plan = {**plan, "assignments": [], "held": [review_decision]}
        review_move = {**routed, "destination": "Angels/Target/review/owner_image_123.jpg"}
        review = self.admission.red_release_routed_catalog(catalog, [review_move], snapshot, self.policy, review_plan)
        self.assertEqual(review["catalog"]["photos"][red_id]["membership"]["status"], "tentative")
        self.assertFalse(review["catalog"]["photos"][red_id]["membership"]["coreUse"])
        self.assertTrue(review["catalog"]["photos"][red_id]["protected"])

    def test_incomplete_rival_cores_force_unassigned_holds(self):
        from tools.art.likeness_library import sandbox_red_release

        routing = {
            "assignments": [{"photoId": "a", "destination": "Angels/Target", "reason": "match",
                             "unscoredAssessment": {"basis": "independent rival"}}],
            "held": [{"photoId": "b", "reviewDestination": "Potentials/Target/review", "reason": "review"}],
        }
        sandbox_red_release.hold_for_incomplete_rivals(
            routing, ["Potentials/Unknown: no eligible identity core; skipped"],
        )
        self.assertEqual(routing["assignments"], [])
        self.assertEqual([row["reviewDestination"] for row in routing["held"]],
                         ["Various/review", "Various/review"])
        self.assertIn("available rivals only", routing["held"][0]["unscoredAssessment"]["basis"])
        self.assertFalse(routing["held"][0]["referenceEligible"])
        with self.assertRaisesRegex(ValueError, "conflicting catalogue"):
            sandbox_red_release.hold_for_incomplete_rivals(
                routing, ["Potentials/Unknown: conflicting catalogue records; skipped"],
            )

    def test_sandbox_red_moves_conserve_candidates_and_refuse_blocked_routes(self):
        from tools.art.likeness_library import sandbox_red_release

        snapshot = [{
            "photoId": "photo:image_123", "currentPath": "Sisters/Owner/gallery/owner_image_123.jpg",
            "nativeSha256": "1" * 64,
        }]
        decision = {
            "photoId": "photo:image_123", "sourceFolder": "Sisters/Owner", "sourceBucket": "Gallery",
            "reviewDestination": "Various/review", "reason": "unassigned",
        }
        routing = {"assignments": [], "held": [decision]}
        moves = sandbox_red_release.moves_from_plan(snapshot, routing)
        self.assertEqual(moves[0]["destination"], "Various/review/owner_image_123.jpg")
        self.assertEqual(moves[0]["sha256"], "1" * 64)
        with self.assertRaisesRegex(ValueError, "conserve"):
            sandbox_red_release.moves_from_plan(snapshot, {"assignments": [], "held": []})
        with self.assertRaisesRegex(ValueError, "blocked"):
            sandbox_red_release.moves_from_plan(
                snapshot, {"assignments": [], "held": [{**decision, "releaseBlocked": True}]},
            )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            sandbox_red_release.moves_from_plan(
                snapshot, {"assignments": [{**decision, "destination": "Angels/Target"}], "held": []},
            )
        with self.assertRaisesRegex(ValueError, "no progress"):
            sandbox_red_release.moves_from_plan(
                snapshot, {"assignments": [{**decision, "reviewDestination": None,
                                             "destination": "Sisters/Owner"}], "held": []},
            )
        with self.assertRaisesRegex(ValueError, "no progress"):
            sandbox_red_release.moves_from_plan(
                snapshot, {"assignments": [{**decision, "reviewDestination": None,
                                             "destination": "sisters/owner"}], "held": []},
            )

    def test_current_release_does_not_publish_an_empty_plan(self):
        from tools.art.likeness_library import sandbox_red_release

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = pathlib.Path(directory).resolve()
            args = SimpleNamespace(run_id="empty")
            with self.assertRaisesRegex(ValueError, "no progress"):
                sandbox_red_release.publish_current_release(
                    root, {}, self.policy, args, {}, {}, {"moves": []}, {}, "hash",
                )
            self.assertEqual(list(root.iterdir()), [])

    def test_sandbox_red_command_previews_applies_checks_and_recovers(self):
        from tools.art.likeness_library import metadata, sandbox_red_release

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as temporary:
            root = pathlib.Path(temporary).resolve()
            source = root / "Sisters" / "Owner" / "gallery" / "owner_image_123.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"red")
            other = source.parent / "owner_image_456.jpg"
            other.write_bytes(b"unaffected")
            cache = root / "cache.json"
            cache.write_bytes(b"cache")
            catalog = root / ".likeness-library.json"
            metadata.save_catalog({"schemaVersion": 1, "actions": [], "people": {}, "photos": {}}, catalog)
            saved_catalog = catalog.read_bytes()
            checksum = metadata.content_sha256(source)
            row = {
                "photoId": "photo:image_123", "currentPath": source.relative_to(root).as_posix(),
                "nativeSha256": checksum,
            }
            decision = {
                "photoId": row["photoId"], "sourceFolder": "Sisters/Owner", "sourceBucket": "Gallery",
                "reviewDestination": "Various/review", "reason": "unassigned",
            }
            routing = {"assignments": [], "held": [decision]}
            snapshot = {"snapshotCandidates": [row], "inputBindings": {}, "reportManifestSHA256": "1" * 64}
            result = {
                "hypotheticalRouting": routing,
                "hypotheticalReviewCensus": {"newlyRed": [], "unavailable": []},
                "workflowReplacementProposals": [],
                "galleryInventoryProof": {
                    "cacheSHA256": metadata.content_sha256(cache), "catalogSHA256": metadata.content_sha256(catalog),
                    "nativeBindings": {row["currentPath"]: checksum,
                                       other.relative_to(root).as_posix(): metadata.content_sha256(other)},
                },
            }

            def stage(_root, stage_root, moves, *_args, **_kwargs):
                stage_root.mkdir(parents=True)
                target = stage_root / pathlib.PurePosixPath(moves[0]["destination"])
                target.parent.mkdir(parents=True)
                target.write_bytes(source.read_bytes())
                (stage_root / ".likeness-library.json").write_bytes(saved_catalog)
                return ([{"native": moves[0]["destination"], "sha256": checksum}], {}, {})

            args = ["--root", str(root), "--run-id", "red-fixture", "--receipt", "receipt",
                    "--report", "report", "--cache", str(cache)]
            short_args = ["--root", str(root), "--run-id", "red-fixture"]
            cfg = sandbox_red_release.likeness.cw.load_cfg()
            with mock.patch.object(sandbox_red_release.likeness.cw, "load_cfg", return_value=cfg), \
                 mock.patch.object(sandbox_red_release.likeness.cw, "sandbox_work_root", return_value=root), \
                 mock.patch.object(sandbox_red_release.normal_admission, "checked_red_release_diagnostic",
                                   return_value=result), \
                 mock.patch.object(sandbox_red_release.normal_admission, "verified_red_snapshot",
                                   return_value=snapshot), \
                 mock.patch.object(sandbox_red_release.normal_admission, "red_release_routed_catalog"), \
                 mock.patch.object(sandbox_red_release.normal_admission, "_red_cache_vectors",
                                   return_value=(cache, metadata.content_sha256(cache), {}, set(), {checksum: {}})), \
                 mock.patch.object(sandbox_red_release.normal_products, "stage", side_effect=stage), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(sandbox_red_release.main(args), 0)
                self.assertTrue(source.exists())
                self.assertEqual(sandbox_red_release.main(args + ["--apply"]), 0)
                target = root / "Various" / "review" / source.name
                self.assertFalse(source.exists())
                self.assertEqual(target.read_bytes(), b"red")
                self.assertEqual(sandbox_red_release.main(short_args + ["--check"]), 0)
                other.write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "unaffected Sandbox Gallery photo changed"):
                    sandbox_red_release.main(short_args + ["--check"])
                other.write_bytes(b"unaffected")
                self.assertEqual(sandbox_red_release.main(short_args + ["--recover"]), 0)
                self.assertEqual(sandbox_red_release.main(short_args + ["--recover-apply"]), 0)
                self.assertEqual(source.read_bytes(), b"red")
                self.assertFalse(target.exists())
                self.assertEqual(catalog.read_bytes(), saved_catalog)

    def test_red_hold_staging_uses_checked_metadata_and_refuses_changed_source(self):
        from tools.art import library_backup
        from tools.art.likeness_library import (
            metadata, normal_history, normal_products, normal_transaction, red_release_diagnostic, retained_preparation,
        )

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            base = pathlib.Path(directory).resolve()
            root = base / "Working"
            root.mkdir()
            source = root / "Sisters" / "Owner" / "gallery" / "owner_image_123.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"red fixture")
            checksum = hashlib.sha256(source.read_bytes()).hexdigest()
            photo_id = "photo:image_123"
            person_id = "person_" + "a" * 32
            catalog = {
                "schemaVersion": 1, "actions": [],
                "people": {person_id: {
                    "id": person_id, "displayName": "Owner", "folder": "Sisters/Owner",
                    "folderHistory": [], "identityAnchors": [photo_id],
                }},
                "photos": {photo_id: {"contentSha256": checksum, "protected": True}},
            }
            move = {
                "photoId": photo_id, "source": source.relative_to(root).as_posix(),
                "destination": "Various/review/owner_image_123.jpg", "sha256": checksum, "reason": "red hold",
            }
            snapshot = [{
                "photoId": photo_id, "owner": "Sisters/Owner", "bucket": "gallery",
                "currentPath": move["source"], "nativeSha256": checksum, "score": .1,
            }]
            catalog_path = root / ".likeness-library.json"
            metadata.save_catalog(catalog, catalog_path)
            catalog_before = catalog_path.read_bytes()
            stage = root / "stage"
            with mock.patch.object(retained_preparation, "plan_transfer", return_value=None), \
                 mock.patch.object(normal_history, "stage"):
                published, updated, _ = normal_products.stage(
                    root, stage, [move], None, profile="fast", photos=[], cfg={}, catalog=catalog,
                    policy=self.policy, red_snapshot_candidates=snapshot,
                )
                self.assertEqual(published[0]["sha256"], checksum)
                self.assertEqual((stage / move["destination"]).read_bytes(), b"red fixture")
                self.assertEqual(source.read_bytes(), b"red fixture")
                self.assertEqual(updated["people"][person_id]["identityAnchors"], [])
                self.assertTrue(updated["photos"][photo_id]["protected"])
                journal = root / "journal.json"
                normal_transaction.publish(
                    root, stage, [move["source"]], journal=journal, bindings={}, profile="fast",
                    run_id="red-fixture", expected_sources={
                        move["source"]: checksum,
                        ".likeness-library.json": hashlib.sha256(catalog_before).hexdigest(),
                    }, exclusive_targets=[move["destination"]],
                )
                normal_transaction.verify(root, journal)
                self.assertFalse(source.exists())
                self.assertEqual((root / move["destination"]).read_bytes(), b"red fixture")
                self.assertEqual(metadata.load_catalog(catalog_path)["people"][person_id]["identityAnchors"], [])
                normal_transaction.recover(root, journal, apply=True)
                self.assertEqual(source.read_bytes(), b"red fixture")
                self.assertFalse((root / move["destination"]).exists())
                self.assertEqual(catalog_path.read_bytes(), catalog_before)
                target_id = "person_" + "b" * 32
                routed_catalog = copy.deepcopy(catalog)
                routed_catalog["people"][target_id] = {
                    "id": target_id, "displayName": "Target", "folder": "Angels/Target",
                    "folderHistory": [], "identityAnchors": [],
                }
                metadata.save_catalog(routed_catalog, catalog_path)
                routed_before = catalog_path.read_bytes()
                routed = {**move, "destination": "Angels/Target/gallery/owner_image_123.jpg", "reason": "qualified"}
                plan = {
                    "assignments": [{"photoId": photo_id, "sourceFolder": "Sisters/Owner",
                                     "sourceBucket": "Gallery", "destination": "Angels/Target",
                                     "reason": "qualified", "referenceEligible": True}],
                    "held": [], "referenceVersion": "5" * 64, "planningOnly": True,
                    "candidateCount": 1, "retiredReferenceIds": [photo_id],
                    "retiredReferenceSHA256": [checksum],
                }
                routed_stage = root / "routed-stage"
                normal_products.stage(
                    root, routed_stage, [routed], None, profile="fast", photos=[], cfg={},
                    catalog=routed_catalog, policy=self.policy, red_snapshot_candidates=snapshot,
                    red_routing_plan=plan,
                )
                external = base / "workflow"
                external.mkdir()
                config, workflow = external / "workspaces.json", external / "workflow.json"
                old_input, new_input = external / "owner_image_123.png", external / "owner_image_456.png"
                config.write_text(json.dumps({"photos": {"Owner": old_input.name}}), encoding="utf-8")
                workflow.write_text(json.dumps({"class_type": "LoadImage", "inputs": {"image": old_input.name}}),
                                    encoding="utf-8")
                old_input.write_bytes(b"old input")
                original_config, original_workflow = config.read_bytes(), workflow.read_bytes()
                proposal = {
                    "state": "proposed", "photoId": photo_id, "beforeDerivative": str(old_input),
                    "afterDerivative": str(new_input),
                    "selectionChanges": [{"hero": "Owner", "flow": None, "before": old_input.name,
                                          "after": new_input.name}],
                }
                inventory = red_release_diagnostic.inspect_consumers({"workflow": external}, [photo_id])
                retargets = red_release_diagnostic.plan_consumer_retargets(inventory, [proposal], config)
                self.assertFalse(retargets["blocked"])
                external_stage = root / "external-stage"
                external_stage.mkdir()
                updates = []
                for item in retargets["plans"]:
                    staged = external_stage / pathlib.Path(item["path"]).name
                    staged.write_bytes(item["afterBytes"])
                    updates.append({"target": item["path"], "staged": staged, "beforeSha256": item["beforeSHA256"]})
                staged_input = external_stage / new_input.name
                staged_input.write_bytes(b"new input")
                updates.extend([
                    {"target": old_input, "delete": True, "beforeSha256": metadata.content_sha256(old_input)},
                    {"target": new_input, "staged": staged_input, "beforeSha256": None},
                ])
                routed_journal = root / "routed-journal.json"
                create_backup = library_backup.create_backup
                with mock.patch.object(library_backup, "create_backup",
                                       side_effect=lambda *args, **kwargs: create_backup(
                                           *args, stamp="20990101-000000", **kwargs,
                                       )):
                    normal_transaction.publish(
                        root, routed_stage, [routed["source"]], journal=routed_journal, bindings={}, profile="fast",
                        run_id="red-routed-fixture", expected_sources={
                            routed["source"]: checksum,
                            ".likeness-library.json": hashlib.sha256(routed_before).hexdigest(),
                        }, exclusive_targets=[routed["destination"]],
                        external_updates=updates, allowed_external_roots=[external],
                    )
                normal_transaction.verify(root, routed_journal, allowed_external_roots=[external])
                self.assertEqual(metadata.load_catalog(catalog_path)["photos"][photo_id]["membership"]["personId"],
                                 target_id)
                self.assertEqual(json.loads(config.read_bytes())["photos"]["Owner"], new_input.name)
                self.assertEqual(json.loads(workflow.read_bytes())["inputs"]["image"], new_input.name)
                self.assertFalse(old_input.exists())
                self.assertEqual(new_input.read_bytes(), b"new input")
                normal_transaction.recover(root, routed_journal, apply=True, allowed_external_roots=[external])
                self.assertEqual(source.read_bytes(), b"red fixture")
                self.assertFalse((root / routed["destination"]).exists())
                self.assertEqual(catalog_path.read_bytes(), routed_before)
                self.assertEqual(config.read_bytes(), original_config)
                self.assertEqual(workflow.read_bytes(), original_workflow)
                self.assertEqual(old_input.read_bytes(), b"old input")
                self.assertFalse(new_input.exists())
                catalog_path.write_bytes(catalog_before)
                destination = root / move["destination"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                for existing in (b"other photo", b"red fixture"):
                    with self.subTest(existing=existing):
                        destination.write_bytes(existing)
                        collision_stage = root / "collision-stage"
                        with self.assertRaisesRegex(ValueError, "hold destination already exists"):
                            normal_products.stage(
                                root, collision_stage, [move], None, profile="fast", photos=[], cfg={},
                                catalog=catalog, policy=self.policy, red_snapshot_candidates=snapshot,
                            )
                        self.assertEqual(destination.read_bytes(), existing)
                        self.assertFalse(collision_stage.exists())
                        destination.unlink()
                source.write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "source changed during staging"):
                    normal_products.stage(
                        root, root / "other-stage", [move], None, profile="fast", photos=[], cfg={},
                        catalog=catalog, policy=self.policy, red_snapshot_candidates=snapshot,
                    )

    def test_red_plan_retires_core_vote_and_routes_protected_member_to_qualified_rival(self):
        source, target = "Sisters/Drakness", "Angels/Other"
        self.identity(target, self.axes[1], self.axes[4])
        red = self.photo(
            self.axes[1], folder=source, bucket="Gallery", photo_id="photo:image_123",
            protected=True, identityProtected=True, redScore=.149999,
        )
        red["sha256"] = "1" * 64
        self.references[source][0].update(photoId=red["photoId"], sha256=red["sha256"])
        self.cores[source]["corePhotoIds"][0] = red["photoId"]
        report = self.admission.red_release_plan(
            self.api, [red], self.cores, self.references, self.settings, self.policy, set(),
            snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
        )
        self.assertEqual(report["assignments"][0]["destination"], target)
        self.assertEqual(report["retiredReferenceIds"], [red["photoId"]])
        self.assertEqual(report["retiredReferenceSHA256"], [red["sha256"]])
        self.assertTrue(report["planningOnly"])
        self.assertEqual(len(self.references[source]), 2)

    def test_red_plan_refuses_nonred_and_blocks_current_workflow_selection(self):
        red = self.photo(self.axes[0], folder="Sisters/Drakness", bucket="Gallery", redScore=.15)
        red["sha256"] = "2" * 64
        args = (self.api, [red], self.cores, self.references, self.settings, self.policy, set())
        with self.assertRaisesRegex(ValueError, "not red"):
            self.admission.red_release_plan(
                *args, snapshot_bands=self.policy["scoreBands"],
                snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
            )
        orange = self.admission.red_release_plan(
            *args, snapshot_bands=self.policy["scoreBands"],
            snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
            release_bands=("red", "orange"),
        )
        self.assertEqual(orange["releaseBands"], ["orange", "red"])
        red["redScore"] = .30
        with self.assertRaises(ValueError):
            self.admission.red_release_plan(
                *args, snapshot_bands=self.policy["scoreBands"],
                snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
                release_bands=("red", "orange"),
            )
        red["redScore"] = .1
        report = self.admission.red_release_plan(
            *args, snapshot_bands=self.policy["scoreBands"],
            snapshot_candidates=self.red_evidence([red]), selected_ids={red["photoId"]},
        )
        self.assertEqual(report["assignments"], [])
        self.assertTrue(report["held"][0]["releaseBlocked"])
        self.assertIn("workflow replacement", report["held"][0]["reason"])
        self.assertEqual(report["retiredReferenceIds"], [])

    def test_protected_red_optimistic_cast_route_becomes_nonvoting_review(self):
        self.paired()
        self.identity("Models/Owner", self.axes[6], self.axes[5])
        red = self.photo(
            self.axes[0], folder="Models/Owner", bucket="Gallery", photo_id="photo:image_123",
            protected=True, redScore=.1,
        )
        red["sha256"] = "9" * 64
        report = self.admission.red_release_plan(
            self.api, [red], self.cores, self.references, self.settings, self.policy, set(),
            snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
        )
        self.assertEqual(report["assignments"], [])
        self.assertEqual(report["held"][0]["reviewDestination"], "Sisters/Drakness/review")
        self.assertEqual(report["held"][0]["castAdmission"]["mode"], "ambiguous-review")
        self.assertFalse(report["held"][0]["referenceEligible"])
        self.assertIn("protected red", report["held"][0]["reason"])
        policy = copy.deepcopy(self.policy)
        policy["categoryPolicies"]["Sisters"]["reviewAdmissionEnabled"] = False
        no_review = self.admission.red_release_plan(
            self.api, [red], self.cores, self.references, self.settings, policy, set(),
            snapshot_bands=policy["scoreBands"], snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
        )
        self.assertEqual(no_review["held"][0]["reviewDestination"], "Various/review")
        unprotected = {**red, "protected": False}
        ordinary = self.admission.red_release_plan(
            self.api, [unprotected], self.cores, self.references, self.settings, self.policy, set(),
            snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([unprotected]),
            selected_ids=set(),
        )
        self.assertEqual(ordinary["assignments"][0]["castAdmission"]["mode"], "optimistic-gallery")

    def test_red_plan_holds_unmatched_and_honors_negative_rival_evidence(self):
        source, target = "Sisters/Drakness", "Angels/Other"
        self.identity(target, self.axes[1], self.axes[4])
        red = self.photo(
            self.axes[1], folder=source, bucket="Gallery", redScore=.1,
            rejectedPersonIds=[target],
        )
        red["sha256"] = "3" * 64
        report = self.admission.red_release_plan(
            self.api, [red], self.cores, self.references, self.settings, self.policy, set(),
            snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
        )
        self.assertEqual(report["assignments"], [])
        self.assertTrue(report["held"][0]["releaseHold"])
        self.assertEqual(report["held"][0]["reviewDestination"], "Various/review")
        self.assertFalse(report["held"][0]["preserveStaged"])
        self.assertIn("unassigned hold", report["held"][0]["reason"])
        self.assertEqual(report["held"][0]["excludedIdentityIds"], [target])

    def test_red_plan_does_not_return_to_former_owner_and_ordinary_protection_remains(self):
        red = self.photo(
            self.axes[0], folder="Sisters/Drakness", bucket="Gallery",
            redScore=.1, protected=True, redRelease=True, detachedOutlier=True,
        )
        red["sha256"] = "4" * 64
        ordinary = self.route([red])
        self.assertEqual(ordinary["assignments"], [])
        self.assertIn("protected", ordinary["held"][0]["reason"])
        report = self.admission.red_release_plan(
            self.api, [red], self.cores, self.references, self.settings, self.policy, set(),
            snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
        )
        self.assertEqual(report["assignments"], [])
        self.assertTrue(report["held"][0]["releaseHold"])

    def test_red_review_without_rival_requires_unassigned_hold(self):
        red = self.photo(
            self.axes[0], folder="Sisters/Drakness", bucket="Review",
            redScore=.1, explicitReviewPlacement=True, identityProtected=True,
        )
        red["sha256"] = "6" * 64
        report = self.admission.red_release_plan(
            self.api, [red], self.cores, self.references, self.settings, self.policy, set(),
            snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
        )
        self.assertEqual(report["assignments"], [])
        self.assertTrue(report["held"][0]["releaseHold"])
        self.assertNotIn("explicit Review placement", report["held"][0]["reason"])

    def test_unmatched_red_proposes_unassigned_move_but_selected_red_stays_blocked(self):
        from tools.art.likeness_library import maintenance, metadata

        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as temporary:
            root = pathlib.Path(temporary).resolve()
            source = root / "Sisters" / "Drakness" / "gallery" / "owner_image_123.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"fixture native")
            red = self.photo(
                self.axes[0], folder="Sisters/Drakness", bucket="Gallery", redScore=.1,
                currentPath=source.relative_to(root).as_posix(),
            )
            red["sha256"] = metadata.content_sha256(source)
            args = (self.api, [red], self.cores, self.references, self.settings, self.policy, set())
            kwargs = dict(
                snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([red]),
            )
            photo = SimpleNamespace(path=source, name=source.name)
            report = self.admission.red_release_plan(*args, **kwargs, selected_ids=set())
            moves = maintenance.proposed_moves(report, [photo], root)
            self.assertEqual(len(moves), 1)
            self.assertEqual(moves[0]["destination"], "Various/review/owner_image_123.jpg")
            self.assertEqual(moves[0]["sha256"], red["sha256"])
            blocked = self.admission.red_release_plan(*args, **kwargs, selected_ids={red["photoId"]})
            self.assertEqual(maintenance.proposed_moves(blocked, [photo], root), [])
            self.assertEqual(source.read_bytes(), b"fixture native")

    def test_red_plan_refuses_invalid_score_and_changed_snapshot_bands(self):
        red = self.photo(self.axes[0], folder="Sisters/Drakness", bucket="Gallery")
        red["sha256"] = "5" * 64
        args = (self.api, [red], self.cores, self.references, self.settings, self.policy, set())
        for score in (None, float("nan"), True, .15):
            with self.subTest(score=score), self.assertRaises(ValueError):
                red["redScore"] = score
                self.admission.red_release_plan(
                    *args, snapshot_bands=self.policy["scoreBands"],
                    snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
                )
        bands = copy.deepcopy(self.policy["scoreBands"])
        bands["red"]["maximumExclusive"] = .2
        bands["orange"]["minimum"] = .2
        red["redScore"] = .1
        with self.assertRaisesRegex(ValueError, "differ"):
            self.admission.red_release_plan(
                *args, snapshot_bands=bands, snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
            )

    def test_red_plan_refuses_mismatched_or_incomplete_saved_candidates(self):
        red = self.photo(self.axes[0], folder="Sisters/Drakness", bucket="Gallery", redScore=.1)
        red["sha256"] = "7" * 64
        evidence = self.red_evidence([red])
        args = (self.api, [red], self.cores, self.references, self.settings, self.policy, set())
        for field, value in (("currentPath", "other.jpg"), ("nativeSha256", "8" * 64), ("owner", "Angels/Other")):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "saved Review evidence"):
                altered = [{**evidence[0], field: value}]
                self.admission.red_release_plan(
                    *args, snapshot_bands=self.policy["scoreBands"], snapshot_candidates=altered, selected_ids=set(),
                )
        with self.assertRaisesRegex(ValueError, "saved evidence set"):
            self.admission.red_release_plan(
                self.api, [], self.cores, self.references, self.settings, self.policy, set(),
                snapshot_bands=self.policy["scoreBands"], snapshot_candidates=evidence, selected_ids=set(),
            )

    def test_red_plan_refuses_stale_or_ambiguous_frozen_reference(self):
        source = "Sisters/Drakness"
        red = self.photo(self.axes[0], folder=source, bucket="Gallery", redScore=.1)
        red["sha256"] = "9" * 64
        self.references[source][0]["photoId"] = red["photoId"]
        args = (self.api, [red], self.cores, self.references, self.settings, self.policy, set())
        with self.assertRaisesRegex(ValueError, "frozen reference differs"):
            self.admission.red_release_plan(
                *args, snapshot_bands=self.policy["scoreBands"],
                snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
            )
        self.references[source][0]["sha256"] = red["sha256"]
        self.references[source][1].update(photoId=red["photoId"], sha256=red["sha256"])
        with self.assertRaisesRegex(ValueError, "frozen reference differs"):
            self.admission.red_release_plan(
                *args, snapshot_bands=self.policy["scoreBands"],
                snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
            )

    def test_red_plan_refuses_ineligible_reference_votes(self):
        red = self.photo(self.axes[1], folder="Sisters/Drakness", bucket="Gallery", redScore=.1)
        red["sha256"] = "a" * 64
        args = (self.api, [red], self.cores, self.references, self.settings, self.policy, set())
        self.references["Sisters/Drakness"][0]["rejectionMetadataStale"] = True
        with self.assertRaisesRegex(ValueError, "reference is not eligible"):
            self.admission.red_release_plan(
                *args, snapshot_bands=self.policy["scoreBands"],
                snapshot_candidates=self.red_evidence([red]), selected_ids=set(),
            )

    def test_unscored_plan_releases_missing_core_and_holds_nonvoting_or_low_quality(self):
        rows = []
        for number, extra in ((1, {"nonVoting": True}), (2, {"qualityEligible": False})):
            row = self.photo(
                self.axes[0], folder="Potentials/Former", bucket="Gallery",
                photo_id=f"photo:image_{number}", redScore=None,
            )
            row["sha256"] = str(number) * 64
            row.update(extra)
            rows.append(row)
        snapshot = self.red_evidence(rows)

        def fake_plan(candidates, *_args, **_kwargs):
            decisions = [
                {"photoId": row["photoId"], "sourceFolder": row["sourceFolder"],
                 "sourceBucket": row["sourceBucket"], "reason": "fixture"}
                for row in candidates
            ]
            return {"assignments": [{**decisions[0], "destination": "Sisters/Drakness"}],
                    "held": [{**decisions[1], "preserveStaged": True}]}

        api = SimpleNamespace(plan_reconciliation=fake_plan, invent_name=stable_name)
        args = (api, rows, self.cores, self.references, self.settings, self.policy, set())
        kwargs = dict(snapshot_bands=self.policy["scoreBands"], snapshot_candidates=snapshot, selected_ids=set())
        with self.assertRaisesRegex(ValueError, "saved own-core score"):
            self.admission.red_release_plan(*args, **kwargs)
        result = self.admission.red_release_plan(*args, **kwargs, include_unscored=True)
        self.assertTrue(result["includeUnscored"])
        self.assertFalse(result["assignments"])
        self.assertEqual(len(result["held"]), 2)
        for decision in result["held"]:
            self.assertEqual(decision["reviewDestination"], "Various/review")
            self.assertFalse(decision["preserveStaged"])
            self.assertAlmostEqual(decision["unscoredAssessment"]["bestRivalScore"], 1.)
        self.assertFalse(result["held"][1]["unscoredAssessment"]["qualityEligible"])

    def test_red_plan_rejects_incomplete_or_inconsistent_rival_references(self):
        source, rival = "Sisters/Drakness", "Angels/Other"
        self.identity(rival, self.axes[1], self.axes[4])
        red = self.photo(self.axes[1], folder=source, bucket="Gallery", redScore=.1)
        red["sha256"] = "b" * 64
        args = (self.api, [red], self.cores, self.references, self.settings, self.policy, set())
        kwargs = dict(
            snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([red]),
            selected_ids=set(),
        )
        original = copy.deepcopy(self.references)
        self.references[rival].pop()
        with self.assertRaisesRegex(ValueError, "incomplete or ambiguous frozen references"):
            self.admission.red_release_plan(*args, **kwargs)
        self.references[rival] = copy.deepcopy(original[rival])
        self.references[rival][0]["vector"] = self.axes[2].copy()
        with self.assertRaisesRegex(ValueError, "frozen core differs"):
            self.admission.red_release_plan(*args, **kwargs)
        self.references[rival] = copy.deepcopy(original[rival])
        self.references[rival][0]["sha256"] = "not-a-hash"
        with self.assertRaisesRegex(ValueError, "invalid frozen reference"):
            self.admission.red_release_plan(*args, **kwargs)
        self.references[rival] = copy.deepcopy(original[rival])
        red["vector"] = np.full(7, np.nan)
        with self.assertRaisesRegex(ValueError, "invalid red candidate vector"):
            self.admission.red_release_plan(*args, **kwargs)

    def test_red_plan_rejects_lost_duplicate_or_self_returning_decisions(self):
        red = self.photo(self.axes[0], folder="Sisters/Drakness", bucket="Gallery", redScore=.1)
        red["sha256"] = "c" * 64
        kwargs = dict(
            snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([red]),
            selected_ids=set(),
        )
        decision = {
            "photoId": red["photoId"], "sourceFolder": red["sourceFolder"],
            "sourceBucket": red["sourceBucket"], "reason": "fixture",
        }
        cases = (
            ({"assignments": [], "held": []}, "conserve"),
            ({"assignments": [], "held": [decision, decision]}, "conserve"),
            ({"assignments": [{**decision, "destination": red["sourceFolder"]}], "held": []},
             "invalid destination"),
        )
        for result, message in cases:
            with self.subTest(message=message):
                api = SimpleNamespace(plan_reconciliation=lambda *args, **options: copy.deepcopy(result),
                                      invent_name=stable_name)
                with self.assertRaisesRegex(ValueError, message):
                    self.admission.red_release_plan(
                        api, [red], self.cores, self.references, self.settings, self.policy, set(), **kwargs,
                    )

    def test_red_plan_refuses_artist_domain(self):
        red = self.photo(self.axes[0], folder="Artists/Source", bucket="Gallery", redScore=.1, side="Artists")
        red["sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "restricted to people identities"):
            self.admission.red_release_plan(
                self.api, [red], self.cores, self.references, self.settings, self.policy, set(),
                snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence([red]),
                selected_ids=set(),
            )

    def test_red_plan_refuses_retirement_that_empties_a_core(self):
        source = "Sisters/Drakness"
        rows = []
        for index, reference in enumerate(self.references[source]):
            reference["photoId"] = f"photo:image_{index + 1}"
            reference["sha256"] = str(index + 1) * 64
            self.cores[source]["corePhotoIds"][index] = reference["photoId"]
            red = self.photo(
                self.axes[1], folder=source, bucket="Gallery",
                photo_id=reference["photoId"], redScore=.1,
            )
            red["sha256"] = reference["sha256"]
            rows.append(red)
        with self.assertRaisesRegex(ValueError, "unusable cores"):
            self.admission.red_release_plan(
                self.api, rows, self.cores, self.references, self.settings, self.policy, set(),
                snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence(rows), selected_ids=set(),
            )
        self.identity("Angels/Other", self.axes[1], self.axes[4])
        report = self.admission.red_release_plan(
            self.api, rows, self.cores, self.references, self.settings, self.policy, set(),
            snapshot_bands=self.policy["scoreBands"], snapshot_candidates=self.red_evidence(rows),
            selected_ids=set(), allow_empty_source_cores=True,
        )
        self.assertEqual(report["emptySourceCores"], [source])
        self.assertEqual(len(report["assignments"]) + len(report["held"]), 2)
        self.assertTrue(all(row.get("destination") != source for row in report["assignments"]))

    def test_home_identity_retains_member_unless_beaten_by_own_core_lead(self):
        # IU13a (Nov 23): an existing member's own core outscoring the cast rival keeps it home.
        vector = .5 * self.axes[0] + np.sqrt(.75) * self.axes[2]
        self.identity("Models/Fragment", vector, self.axes[4])
        row = self.photo(vector, folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True)
        report = self.route([row])
        self.assertEqual(report["assignments"], [])
        self.assertTrue(report["held"][0]["preserveStaged"])
        self.policy["photoRouting"]["minimumOwnCoreLead"] = -2.
        self.assertEqual(self.route([row])["assignments"][0]["destination"], "Sisters/Drakness")

    def test_named_intake_near_miss_and_tie_go_to_named_review(self):
        self.identity("Potentials/Fia", self.axes[5], self.axes[6])
        self.identity("Potentials/Gwen", self.axes[3], self.axes[6])

        def route(score_fia, score_gwen, named=True, **extra):
            rest = np.sqrt(1 - score_fia ** 2 - score_gwen ** 2)
            row = self.photo(score_fia * self.axes[5] + score_gwen * self.axes[3] + rest * self.axes[4],
                             folder="Various", bucket="Pool", **extra)
            ctx = self.admission.context(self.cores, self.references, self.policy)
            ctx["namedFolders"] = {"Potentials/Fia", "Potentials/Gwen"} if named else set()
            return plan_reconciliation([row], self.cores, policy=self.policy, name_factory=stable_name,
                                       admission_context=ctx)

        def named_reviews(report):
            return [row for row in report["held"] + report["assignments"] if row.get("namedIntakeReview")]

        held = route(.27, .1)["held"][0]
        self.assertEqual((held["reviewDestination"], held["namedIntakeReview"]), ("Potentials/Fia/review", "near-miss"))
        self.assertEqual(named_reviews(route(.27, .1, named=False)), [])
        self.assertEqual(named_reviews(route(.27, .2)), [])
        tie = route(.34, .32)["held"][0]
        self.assertEqual((tie["reviewDestination"], tie["namedIntakeReview"]), ("Potentials/Fia/review", "tie"))
        self.assertEqual(tie["runnerUp"]["folder"], "Potentials/Gwen")
        member = route(.27, .1, sourceFolder="Potentials/Gwen", sourceBucket="Gallery", rebaseCandidate=True)
        self.assertEqual(named_reviews(member), [])

    def test_lower_upward_move_needs_to_beat_home_by_own_core_lead(self):
        # IU13a (Nov 23): Fia-like Potential members stay unless a Prospect beats home by 0.10.
        home, rival = self.axes[5], self.axes[3]
        self.identity("Potentials/Fia", home, self.axes[6])
        self.identity("Prospects/Jacinta", rival, self.axes[4])
        for rival_score, home_score, expected in ((.65, .6, None), (.75, .5, "Prospects/Jacinta")):
            with self.subTest(rival_score=rival_score, home_score=home_score):
                rest = np.sqrt(1 - rival_score ** 2 - home_score ** 2)
                row = self.photo(
                    rival_score * rival + home_score * home + rest * self.axes[6],
                    folder="Potentials/Fia", bucket="Gallery", rebaseCandidate=True,
                )
                report = self.route([row])
                if expected is None:
                    held = report["held"][0]
                    self.assertIn("home identity retained", held["reason"])
                    self.assertAlmostEqual(held["homeScore"], home_score, places=3)
                    self.assertFalse(held.get("reviewDestination"))
                else:
                    self.assertEqual(report["assignments"][0]["destination"], expected)

    def test_exact_gallery_floor_ignores_higher_non_home_lower_rival(self):
        vector = .5 * self.axes[0] + np.sqrt(.75) * self.axes[2]
        self.identity("Models/Fragment", self.axes[3], self.axes[4])
        self.identity("Models/Rival", vector, self.axes[4])
        row = self.photo(vector, folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True)
        report = self.route([row])
        result = report["assignments"][0]
        self.assertEqual(result["destination"], "Sisters/Drakness")
        self.assertAlmostEqual(result["castAdmission"]["score"], .5)
        self.assertEqual(result["lowerCategoryEvidence"][0]["folder"], "Models/Rival")
        self.assertAlmostEqual(result["lowerCategoryEvidence"][0]["score"], 1.)
        self.assertEqual(result["independentSupportCount"], 2)
        self.assertTrue(all(float(vector @ ref["vector"]) < .5 for ref in self.references["Sisters/Drakness"]))

    def test_approved_pair_is_optimistic_but_every_blocking_rival_must_be_approved(self):
        self.paired()
        result = self.route([self.photo(self.axes[0])])["assignments"][0]
        self.assertEqual(result["castAdmission"]["mode"], "optimistic-gallery")
        self.assertFalse(result["referenceEligible"])
        self.identity("Angels/Unrelated", .999 * self.axes[0] + np.sqrt(1 - .999 ** 2) * self.axes[2], self.axes[5])
        report = self.route([self.photo(self.axes[0])])
        self.assertEqual(report["assignments"], [])
        self.assertEqual(report["held"][0]["castAdmission"]["mode"], "ambiguous-review")
        self.assertEqual(report["held"][0]["reviewDestination"], "Sisters/Drakness/review")
        self.assertEqual(len(report["held"][0]["castAdmission"]["alternatives"]), 2)
        self.assertEqual(report["clusters"], [])

    def test_review_floor_and_below_floor_lower_routing(self):
        self.identity("Models/Existing", self.axes[2], self.axes[4])
        for score in (.35, .349):
            with self.subTest(score=score):
                vector = score * self.axes[0] + np.sqrt(1 - score ** 2) * self.axes[2]
                report = self.route([self.photo(vector)])
                if score == .35:
                    self.assertEqual(report["held"][0]["reviewDestination"], "Sisters/Drakness/review")
                    self.assertFalse(report["held"][0]["referenceEligible"])
                else:
                    self.assertEqual(report["assignments"][0]["destination"], "Models/Existing")

    def test_correlated_duplicate_and_self_references_do_not_supply_two_votes(self):
        refs = self.references["Sisters/Drakness"]
        for mutate in (
            lambda: refs[1].update(sha256=refs[0]["sha256"]),
            lambda: refs[1].update(vector=refs[0]["vector"]),
            lambda: refs[1].update(photoId="photo:image_123"),
        ):
            saved = copy.deepcopy(refs)
            mutate()
            report = self.route([self.photo(self.axes[0])])
            self.assertEqual(report["assignments"], [])
            self.assertLess(report["held"][0]["independentSupportCount"], 2)
            refs[:] = saved

    def test_exact_tie_is_disclosed_and_deterministic(self):
        self.identity("Angels/Nyxene", self.axes[0], self.axes[4])
        first = self.route([self.photo(self.axes[0])])["assignments"][0]
        self.cores = dict(reversed(list(self.cores.items())))
        second = self.route([self.photo(self.axes[0])])["assignments"][0]
        self.assertEqual(first, second)
        self.assertEqual(first["destination"], "Angels/Nyxene")
        self.assertIn("storage-only", first["reason"])

    def test_source_quality_negative_evidence_and_receiving_locks(self):
        for kwargs in ({"protected": True}, {"workflowSelected": True}, {"rejectedPersonIds": ["Sisters/Drakness"]}):
            with self.subTest(kwargs=kwargs):
                report = self.route([self.photo(
                    self.axes[0], folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True, **kwargs,
                )])
                self.assertEqual(report["assignments"], [])
                self.assertEqual(report["clusters"], [])
        invalid = self.photo(self.axes[0])
        invalid["qualityEligible"] = False
        self.assertTrue(self.route([invalid])["held"][0]["preserveStaged"])
        locked = self.route([self.photo(self.axes[0])], locked=True)
        self.assertTrue(locked["held"][0]["preserveStaged"])
        self.assertEqual(locked["held"][0]["bestMatch"], "Sisters/Drakness")

    def test_unmatched_existing_gallery_is_retained_and_never_forms_a_fragment(self):
        report = self.route([self.photo(
            self.axes[6], folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True,
        )])
        self.assertEqual(report["assignments"], [])
        self.assertEqual(report["clusters"], [])
        self.assertTrue(report["held"][0]["preserveStaged"])
        review = self.route([self.photo(self.axes[6], folder="Sisters/Drakness", bucket="Review")])
        self.assertEqual(review["assignments"], [])
        self.assertEqual(review["clusters"], [])
        self.assertTrue(review["held"][0]["preserveStaged"])

    def test_untouched_review_groups_with_new_arrivals_without_voting_for_old_owner(self):
        reviewed = self.photo(
            self.axes[6], folder="Sisters/Drakness", bucket="Review", regroupReview=True,
        )
        arrivals = [
            self.photo(self.axes[6], f"photo:image_{number}") for number in (124, 125)
        ]
        result = self.admission.two_round_plan(
            self.api, [reviewed, *arrivals], self.cores, self.references,
            self.settings, self.policy, set(),
        )
        self.assertEqual(len(result["clusters"]), 1)
        self.assertEqual(
            set(result["clusters"][0]["photoIds"]),
            {row["photoId"] for row in [reviewed, *arrivals]},
        )
        self.assertNotIn(
            reviewed["photoId"], result["referenceSnapshots"]["2"]["photoIds"]["Sisters/Drakness"],
        )

    def test_explicit_review_placement_is_not_reassigned_even_to_strong_cast_gallery(self):
        row = self.photo(
            self.axes[0], folder="Sisters/Other", bucket="Review", explicitReviewPlacement=True,
        )
        self.assertEqual(self.route([row])["assignments"], [])
        self.assertTrue(self.route([row])["held"][0]["preserveStaged"])

    def test_one_boundary_allows_existing_or_various_seed_to_recover_other_member(self):
        for arrival_seed in (False, True):
            with self.subTest(arrival_seed=arrival_seed):
                seed = self.photo(.8 * self.axes[0] + .6 * self.axes[1], "photo:image_124")
                recovered = self.photo(.48 * self.axes[0] + np.sqrt(1 - .48 ** 2) * self.axes[1])
                existing = recovered if arrival_seed else seed
                existing.update(sourceFolder="Models/Fragment", sourceBucket="Gallery", rebaseCandidate=True)
                report = self.admission.two_round_plan(
                    self.api, [recovered, seed], self.cores, self.references,
                    self.settings, self.policy, set(),
                )
                self.assertEqual({row["photoId"] for row in report["assignments"]}, {seed["photoId"], recovered["photoId"]})
                self.assertEqual(report["referenceRefreshCount"], 1)
                self.assertEqual(len(report["matchingRounds"]), 2)
                boundary = report["referenceSnapshots"]["2"]["photoIds"]["Sisters/Drakness"]
                self.assertIn(seed["photoId"], boundary)
                self.assertNotIn(recovered["photoId"], boundary)
                self.assertNotIn(seed["photoId"], self.cores["Sisters/Drakness"]["corePhotoIds"])
                json.dumps(report, allow_nan=False)

    def test_review_cannot_bootstrap_other_review_and_old_source_votes_retire(self):
        self.without_home_lead()
        rows = [
            self.photo(.48 * self.axes[0] + np.sqrt(1 - .48 ** 2) * self.axes[1], f"photo:image_{number}",
                       folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True)
            for number in (123, 124)
        ]
        self.identity("Models/Fragment", rows[0]["vector"], self.axes[4])
        self.references["Models/Fragment"] = [
            {**row, "sha256": row["sha256"]} for row in rows
        ]
        self.cores["Models/Fragment"]["corePhotoIds"] = [row["photoId"] for row in rows]
        report = self.admission.two_round_plan(
            self.api, rows, self.cores, self.references, self.settings, self.policy, set(),
        )
        self.assertEqual(report["assignments"], [])
        self.assertEqual(len(report["held"]), 2)
        self.assertNotIn("Models/Fragment", report["referenceSnapshots"]["2"]["photoIds"])
        self.assertEqual(
            report["referenceSnapshots"]["1"]["photoIds"]["Sisters/Drakness"],
            report["referenceSnapshots"]["2"]["photoIds"]["Sisters/Drakness"],
        )
        self.assertTrue(report["passCapReached"])

    def test_pool_candidate_joins_recomputed_lower_core_after_members_leave(self):
        self.without_home_lead()
        seed = self.photo(
            .8 * self.axes[0] + .6 * self.axes[1], "seed",
            folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True,
        )
        second = self.photo(
            .28 * self.axes[0] + np.sqrt(1 - .28 ** 2) * self.axes[1], "second",
            folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True,
        )
        survivor = self.photo(self.axes[1], "survivor")
        released = self.photo(
            self.axes[1], "released", folder="Various", bucket="Pool",
            rebaseCandidate=True, regroupReview=True,
        )
        self.identity("Models/Fragment", self.axes[1], self.axes[4])
        refs = [seed, second, survivor]
        self.references["Models/Fragment"] = refs
        self.cores["Models/Fragment"]["corePhotoIds"] = [row["photoId"] for row in refs]
        vector = np.mean([row["vector"] for row in refs], axis=0)
        self.cores["Models/Fragment"]["vector"] = vector / np.linalg.norm(vector)

        report = self.admission.two_round_plan(
            self.api, [seed, second, released], self.cores, self.references,
            self.settings, self.policy, set(),
        )
        self.assertEqual(
            {row["photoId"]: row["destination"] for row in report["assignments"]},
            {"seed": "Sisters/Drakness", "second": "Sisters/Drakness", "released": "Models/Fragment"},
        )
        self.assertEqual(
            [row["retiredReferenceIds"] for row in report["matchingRounds"]], [["released", "seed"], ["second"]],
        )
        self.assertEqual([row["retiredLowerCores"] for row in report["matchingRounds"]], [[], []])
        self.assertEqual([row["recomputedCores"] for row in report["matchingRounds"]],
                         [["Models/Fragment"], ["Models/Fragment"]])
        self.assertEqual(
            report["referenceSnapshots"]["2"]["photoIds"]["Models/Fragment"], ["second", "survivor"],
        )
        self.assertEqual(report["clusters"], [])
        self.assertEqual(report["held"], [])
        self.assertFalse(report["passCapReached"])

    def residual_integration_fixture(self):
        seed = self.photo(
            .8 * self.axes[0] + .6 * self.axes[1], "photo:image_123",
            folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True,
        )
        second = self.photo(
            .28 * self.axes[0] + np.sqrt(1 - .28 ** 2) * self.axes[1], "photo:image_124",
            folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True,
        )
        survivor = self.photo(self.axes[1], "photo:image_125")
        released = self.photo(
            self.axes[1], "photo:image_126", folder="Various", bucket="Pool",
            rebaseCandidate=True, regroupReview=True,
        )
        for row in (seed, second, survivor, released):
            row["sha256"] = hashlib.sha256(row["photoId"].encode()).hexdigest()
        self.identity("Models/Fragment", self.axes[1], self.axes[4])
        refs = [seed, second, survivor]
        self.references["Models/Fragment"] = refs
        self.cores["Models/Fragment"]["corePhotoIds"] = [row["photoId"] for row in refs]
        vector = np.mean([row["vector"] for row in refs], axis=0)
        self.cores["Models/Fragment"]["vector"] = vector / np.linalg.norm(vector)
        binding = {
            "photoId": released["photoId"], "currentPath": "Various/gallery/owner_image_126.jpg",
            "sha256": released["sha256"],
        }
        return seed, second, survivor, released, binding

    def test_bound_release_scores_final_residual_without_stale_votes_or_growth(self):
        self.without_home_lead()
        seed, second, survivor, released, binding = self.residual_integration_fixture()
        original = copy.deepcopy(self.references)
        report = self.admission.two_round_plan(
            self.api, [seed, second, released], self.cores, self.references,
            self.settings, self.policy, set(), released_bindings=[binding],
        )
        result = next(row for row in report["assignments"] if row["photoId"] == released["photoId"])
        self.assertEqual(result["destination"], "Models/Fragment")
        self.assertFalse(result["referenceEligible"])
        self.assertEqual(report["clusters"], [])
        self.assertEqual(report["referenceRefreshCount"], 1)
        evidence = result["residualScoring"]
        self.assertEqual(evidence["binding"], binding)
        residual = next(row for row in evidence["comparisons"] if row["folder"] == "Models/Fragment")
        self.assertEqual(residual["referencePhotoIds"], [survivor["photoId"]])
        self.assertEqual(residual["referenceSHA256"], [survivor["sha256"]])
        self.assertAlmostEqual(residual["score"], 1.)
        self.assertIn(second["photoId"], evidence["excludedReferenceIds"])
        self.assertIn(second["sha256"], evidence["excludedReferenceSHA256"])
        self.assertNotEqual(result["referenceVersion"], report["referenceSnapshots"]["2"]["referenceVersion"])
        self.assertNotIn(released["photoId"], report["referenceSnapshots"]["2"]["photoIds"]["Models/Fragment"])
        for folder in original:
            for before, after in zip(original[folder], self.references[folder]):
                np.testing.assert_array_equal(before["vector"], after["vector"])
                self.assertEqual(before["photoId"], after["photoId"])

    def test_bound_release_excludes_duplicate_content_and_preserves_no_match(self):
        self.without_home_lead()
        seed, second, survivor, released, binding = self.residual_integration_fixture()
        survivor["sha256"] = released["sha256"]
        report = self.admission.two_round_plan(
            self.api, [seed, second, released], self.cores, self.references,
            self.settings, self.policy, set(), released_bindings=[binding],
        )
        result = next(row for row in report["held"] if row["photoId"] == released["photoId"])
        self.assertFalse(result["preserveStaged"])
        self.assertIsNone(result["destination"])
        self.assertIn("unresolvedReleaseReview", result)
        self.assertFalse(result["referenceEligible"])
        self.assertEqual(report["clusters"], [])
        self.assertNotIn("Models/Fragment", [
            row["folder"] for row in result["residualScoring"]["comparisons"]
        ])
        self.assertIn(released["sha256"], result["residualScoring"]["excludedReferenceSHA256"])

    def test_multiple_guarded_releases_do_not_vote_for_each_other(self):
        self.without_home_lead()
        seed, second, survivor, first, binding = self.residual_integration_fixture()
        other = self.photo(
            self.axes[1], "photo:image_127", folder="Various", bucket="Pool",
            rebaseCandidate=True, regroupReview=True,
        )
        other["sha256"] = hashlib.sha256(other["photoId"].encode()).hexdigest()
        other_binding = {
            "photoId": other["photoId"], "currentPath": "Various/gallery/owner_image_127.jpg",
            "sha256": other["sha256"],
        }
        inputs = [seed, second, first, other]
        reports = [
            self.admission.two_round_plan(
                self.api, order, self.cores, self.references, self.settings, self.policy, set(),
                released_bindings=[binding, other_binding],
            )
            for order in (inputs, list(reversed(inputs)))
        ]
        self.assertEqual(reports[0], reports[1])
        self.assertEqual(reports[0]["clusters"], [])
        for candidate in (first, other):
            decision = next(row for row in reports[0]["assignments"] if row["photoId"] == candidate["photoId"])
            self.assertFalse(decision["referenceEligible"])
            comparison = next(
                row for row in decision["residualScoring"]["comparisons"] if row["folder"] == "Models/Fragment"
            )
            self.assertEqual(comparison["referencePhotoIds"], [survivor["photoId"]])
            self.assertTrue({first["photoId"], other["photoId"]}.issubset(
                decision["residualScoring"]["excludedReferenceIds"]
            ))

    def test_unbound_guarded_candidate_keeps_original_decision(self):
        self.without_home_lead()
        seed, second, _, released, binding = self.residual_integration_fixture()
        ordinary = self.photo(
            self.axes[1], "photo:image_127", folder="Various", bucket="Pool",
            rebaseCandidate=True, regroupReview=True,
        )
        ordinary["sha256"] = hashlib.sha256(ordinary["photoId"].encode()).hexdigest()
        candidates = [seed, second, released, ordinary]
        baseline = self.admission.two_round_plan(
            self.api, candidates, self.cores, self.references, self.settings, self.policy, set(),
        )
        selected = self.admission.two_round_plan(
            self.api, candidates, self.cores, self.references, self.settings, self.policy, set(),
            released_bindings=[binding],
        )
        old = next(row for row in baseline["assignments"] + baseline["held"] if row["photoId"] == ordinary["photoId"])
        current = next(row for row in selected["assignments"] + selected["held"] if row["photoId"] == ordinary["photoId"])
        self.assertEqual(old, current)
        # IU13: an unbound arrival joins the recomputed lower core instead of being held.
        self.assertEqual(current["destination"], "Models/Fragment")

    def test_bound_release_does_not_override_quality_or_stale_rejection(self):
        for change in ({"qualityEligible": False}, {"rejectionMetadataStale": True}):
            with self.subTest(change=change):
                seed, second, _, released, binding = self.residual_integration_fixture()
                released.update(change)
                report = self.admission.two_round_plan(
                    self.api, [seed, second, released], self.cores, self.references,
                    self.settings, self.policy, set(), released_bindings=[binding],
                )
                result = next(row for row in report["held"] if row["photoId"] == released["photoId"])
                self.assertTrue(result["preserveStaged"])
                self.assertNotIn("residualScoring", result)

    def test_released_binding_must_match_source_identity_and_content(self):
        seed, second, _, released, binding = self.residual_integration_fixture()
        for changes in (
            {"sha256": "a" * 64}, {"currentPath": "Various/gallery/owner_image_999.jpg"},
            {"currentPath": "Models/Fragment/gallery/owner_image_126.jpg"},
            {"currentPath": "../Various/gallery/owner_image_126.jpg"},
            {"photoId": "photo:image_999"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.admission.two_round_plan(
                        self.api, [seed, second, released], self.cores, self.references,
                        self.settings, self.policy, set(), released_bindings=[{**binding, **changes}],
                    )
        with self.assertRaises(ValueError):
            self.admission.two_round_plan(
                self.api, [seed, second, released], self.cores, self.references,
                self.settings, self.policy, set(), released_bindings=[binding, binding],
            )

    def residual_single_assessment(self, released, binding, *, retired_ids=()):
        held = {
            released["photoId"]: {
                "photoId": released["photoId"], "sourceFolder": released["sourceFolder"],
                "sourceBucket": released["sourceBucket"], "preserveStaged": True,
                "reason": "old lower core lost reference authority; hold instead of creating another fragment",
            }
        }
        self.admission._rescore_released_holds(
            self.api, [released], held, self.cores, self.references, set(retired_ids),
            {released["photoId"]: binding}, self.settings, self.policy, set(), False,
        )
        return held[released["photoId"]]

    def test_residual_threshold_ambiguity_and_rejection_gates(self):
        _, _, _, released, binding = self.residual_integration_fixture()
        released["vector"] = self.axes[6]
        for score, expected in ((.299, None), (.3, "review"), (.399, "review"), (.4, "gallery")):
            with self.subTest(score=score):
                self.cores, self.references = {}, {}
                center = score * self.axes[6] + np.sqrt(1 - score ** 2) * self.axes[5]
                self.identity("Models/Survivor", center, self.axes[4])
                row = self.residual_single_assessment(released, binding)
                if expected == "gallery":
                    self.assertEqual(row.get("destination"), "Models/Survivor")
                elif expected == "review":
                    self.assertEqual(row.get("reviewDestination"), "Models/Survivor/review")
                else:
                    self.assertEqual(row.get("reviewDestination"), "Models/Survivor/review")
                    self.assertEqual(row["unresolvedReleaseReview"]["basis"], "highest-scoring rival")
                self.assertFalse(row.get("referenceEligible", False))
        self.cores, self.references = {}, {}
        self.identity("Models/One", .6 * self.axes[6] + .8 * self.axes[5], self.axes[3])
        self.identity("Models/Two", .59 * self.axes[6] + np.sqrt(1 - .59 ** 2) * self.axes[5], self.axes[4])
        row = self.residual_single_assessment(released, binding)
        self.assertEqual(row["reviewDestination"], "Models/One/review")
        self.assertIn("unresolvedReleaseReview", row)
        self.assertEqual(len(row["residualScoring"]["comparisons"]), 2)
        rejected = {**released, "rejectedPersonIds": ["Models/One"]}
        row = self.residual_single_assessment(rejected, binding)
        self.assertEqual(row.get("destination"), "Models/Two")
        self.assertEqual([x["folder"] for x in row["residualScoring"]["comparisons"]], ["Models/Two"])

    def test_residual_no_reference_and_no_candidate_self_vote(self):
        _, _, _, released, binding = self.residual_integration_fixture()
        self.cores, self.references = {}, {}
        row = self.residual_single_assessment(released, binding)
        self.assertEqual(row["reviewDestination"], "Various/review")
        self.assertEqual(row["residualScoring"]["comparisons"], [])
        self.identity("Models/Self", released["vector"], self.axes[4])
        self.references["Models/Self"] = [{
            "photoId": released["photoId"], "sha256": released["sha256"],
            "vector": released["vector"], "qualityEligible": True,
        }]
        self.cores["Models/Self"]["corePhotoIds"] = [released["photoId"]]
        row = self.residual_single_assessment(released, binding)
        self.assertEqual(row["reviewDestination"], "Various/review")
        self.assertIsNone(row["unresolvedReleaseReview"]["score"])
        self.assertEqual(row["residualScoring"]["comparisons"], [])

    def test_residual_cast_gallery_threshold_and_ambiguity(self):
        _, _, _, released, binding = self.residual_integration_fixture()
        released["vector"] = self.axes[0]
        self.cores, self.references = {}, {}
        self.identity(
            "Sisters/Drakness", .5 * self.axes[0] + np.sqrt(.75) * self.axes[1], self.axes[3],
        )
        row = self.residual_single_assessment(released, binding)
        self.assertEqual(row.get("destination"), "Sisters/Drakness")
        self.assertAlmostEqual(row["castAdmission"]["score"], .5)
        self.assertFalse(row["referenceEligible"])
        self.identity(
            "Angels/Other", .49 * self.axes[0] + np.sqrt(1 - .49 ** 2) * self.axes[1], self.axes[4],
        )
        row = self.residual_single_assessment(released, binding)
        self.assertEqual(row["reviewDestination"], "Sisters/Drakness/review")
        self.assertIsNone(row["destination"])
        self.assertEqual(len(row["residualScoring"]["comparisons"]), 2)

    def test_residual_rejects_incomplete_or_duplicate_reference_evidence(self):
        _, _, _, released, binding = self.residual_integration_fixture()
        self.cores, self.references = {}, {}
        self.identity("Models/One", self.axes[1], self.axes[3])
        self.references["Models/One"].pop()
        with self.assertRaisesRegex(ValueError, "incomplete or ambiguous frozen references"):
            self.residual_single_assessment(released, binding)
        self.identity("Models/One", self.axes[1], self.axes[3])
        self.identity("Models/Two", self.axes[1], self.axes[4])
        self.references["Models/Two"][0]["sha256"] = self.references["Models/One"][0]["sha256"]
        with self.assertRaisesRegex(ValueError, "ambiguous reference IDs or content"):
            self.residual_single_assessment(released, binding)

    def test_release_residual_never_uses_an_earlier_departing_reference_hash(self):
        self.without_home_lead()
        seed, second, survivor, released, binding = self.residual_integration_fixture()
        # A distinct ID retaining the first departure's bytes must not vote.
        survivor["sha256"] = seed["sha256"]
        report = self.admission.two_round_plan(
            self.api, [seed, second, released], self.cores, self.references,
            self.settings, self.policy, set(), released_bindings=[binding],
        )
        row = next(row for row in report["held"] if row["photoId"] == released["photoId"])
        self.assertIn(seed["sha256"], row["residualScoring"]["excludedReferenceSHA256"])
        self.assertNotIn("Models/Fragment", [
            item["folder"] for item in row["residualScoring"]["comparisons"]
        ])

    def test_optimistic_gallery_is_not_reconsidered_or_promoted_at_the_boundary(self):
        self.paired()
        photo = self.photo(self.axes[0])
        report = self.admission.two_round_plan(
            self.api, [photo], self.cores, self.references, self.settings, self.policy, set(),
        )
        self.assertEqual(report["matchingRounds"][1]["candidateCount"], 0)
        row = report["assignments"][0]
        self.assertEqual(row["castAdmission"]["mode"], "optimistic-gallery")
        self.assertFalse(row["referenceEligible"])
        self.assertTrue(all(
            photo["photoId"] not in ids for ids in report["referenceSnapshots"]["2"]["photoIds"].values()
        ))

    def test_optimistic_membership_detaches_old_reference_and_stays_unprotected_next_run(self):
        from tools.art.likeness_library import audit, maintenance, metadata, protection

        self.paired()
        decision = self.route([self.photo(self.axes[0])])["assignments"][0]
        person_id, source_id = metadata.new_person_id(), metadata.new_person_id()
        group_id = "group_" + "a" * 32
        photo_id = decision["photoId"]
        catalog = {
            "schemaVersion": 1, "people": {
                pid: {"id": pid, "folder": folder, "displayName": folder.split("/")[1],
                      "folderHistory": [], "identityAnchors": [], "protected": False}
                for pid, folder in ((person_id, decision["destination"]), (source_id, "Models/Fragment"))
            },
            "photos": {photo_id: {"contentSha256": "a" * 64, "protected": False, "membership": {
                "personId": source_id, "groupId": group_id, "status": "supported", "coreUse": True,
                "reason": "old source reference", "referenceVersion": "a" * 64,
            }}},
            "photoGroups": {group_id: {
                "id": group_id, "personId": source_id, "name": "Original group", "status": "supported",
                "memberPhotoIds": [photo_id], "referencePhotoIds": [photo_id],
                "sourcePersonIds": [source_id], "history": [], "reason": "source history",
            }}, "actions": [],
        }
        move = {
            **decision, "source": "Models/Fragment/gallery/fragment_image_123.jpg",
            "destination": decision["destination"] + "/gallery/drakness_image_123.jpg", "sha256": "a" * 64,
        }
        updated = maintenance._updated_catalog(catalog, [move], self.policy)
        member = updated["photos"][photo_id]["membership"]
        self.assertEqual((member["personId"], member["status"], member["coreUse"]), (person_id, "tentative", False))
        self.assertFalse(updated["photos"][photo_id]["protected"])
        self.assertEqual(updated["photoGroups"][group_id]["memberPhotoIds"], [])
        self.assertEqual(updated["photoGroups"][group_id]["referencePhotoIds"], [])
        self.assertIn(photo_id, audit.membership_excluded(updated, [photo_id]))
        for field in ("protected", "coreUse", "anchor"):
            broken = copy.deepcopy(updated)
            if field == "protected":
                broken["photos"][photo_id]["protected"] = True
            elif field == "coreUse":
                broken["photos"][photo_id]["membership"]["coreUse"] = True
            else:
                broken["people"][person_id]["identityAnchors"] = [photo_id]
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "unconfirmed Gallery"):
                metadata.validate_catalog(broken)
        scratch = ROOT / "tmp" / "normal-flow-restoration"
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            root = pathlib.Path(temporary)
            native = root / pathlib.PurePosixPath(move["destination"])
            native.parent.mkdir(parents=True)
            native.write_bytes(b"same unconfirmed pixels")
            updated["photos"][photo_id]["contentSha256"] = metadata.content_sha256(native)
            photo = SimpleNamespace(
                path=native, name=native.name, key=decision["destination"],
                vec=self.axes[0], sha=metadata.content_sha256(native), faces=1, f2=0.,
                usable=lambda _minimum: True,
            )
            space = SimpleNamespace(photos=[photo], st=self.settings)
            actions, evidence = protection.plan_protection(space, {}, updated, self.policy, root=root)
        self.assertEqual(actions, [])
        self.assertTrue(any("unconfirmed assignment-only" in row["reason"] for row in evidence))
        self.assertTrue(catalog["photos"][photo_id]["membership"]["coreUse"])

    def test_cast_receiving_permission_does_not_unlock_outgoing_cast_gallery(self):
        from tools.art.likeness_library import maintenance, metadata, normal_finish

        self.paired()
        decision = self.route([self.photo(self.axes[0])])["assignments"][0]
        scratch = ROOT / "tmp" / "normal-flow-restoration"
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            root = pathlib.Path(temporary)
            source = root / "Models" / "Fragment" / "gallery" / "fragment_image_123.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"eligible original")
            move = {**decision, "source": source.relative_to(root).as_posix(),
                    "destination": decision["destination"] + "/gallery/drakness_image_123.jpg",
                    "sha256": metadata.content_sha256(source)}
            catalog = maintenance._updated_catalog(
                {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}, [move], self.policy,
            )
            metadata.save_catalog(catalog, root / ".likeness-library.json")
            maintenance._validate_permissions(root, [move], self.policy, {})
            with mock.patch.object(normal_finish, "cores", return_value=({}, [])):
                checked, evidence = normal_finish.check_batch(
                    None, SimpleNamespace(photos=[]), catalog, self.policy, [move],
                )
            self.assertEqual(checked, [move])
            self.assertEqual(evidence["corrections"], [])
            outgoing = {**move, "source": "Angels/Other/gallery/other_image_123.jpg"}
            with self.assertRaisesRegex(ValueError, "protected Gallery"):
                maintenance._validate_permissions(root, [outgoing], self.policy, {})
            disabled = copy.deepcopy(self.policy)
            disabled["categoryPolicies"]["Sisters"]["galleryAdmissionEnabled"] = False
            with self.assertRaises(ValueError):
                maintenance._validate_permissions(root, [move], disabled, {})

    def test_release_permission_override_is_source_bound_and_sandbox_only(self):
        from tools.art.likeness_library import maintenance, metadata

        scratch = ROOT / "tmp" / "normal-flow-restoration"
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            root = pathlib.Path(temporary)
            photo_id, digest = "photo:image_123", "a" * 64
            metadata.save_catalog({
                "schemaVersion": 1, "people": {}, "actions": [],
                "photos": {photo_id: {"contentSha256": digest, "protected": True}},
            }, root / ".likeness-library.json")
            move = {"photoId": photo_id, "source": "Sisters/Owner/gallery/owner_image_123.jpg",
                    "destination": "Various/review/owner_image_123.jpg", "sha256": digest}
            binding = {"photoId": photo_id, "currentPath": move["source"], "sha256": digest}
            with self.assertRaisesRegex(ValueError, "protected"):
                maintenance._validate_permissions(root, [move], self.policy, {})
            with self.assertRaisesRegex(ValueError, "Sandbox"):
                maintenance._validate_permissions(root, [move], self.policy, {}, released_bindings=[binding])
            with mock.patch.object(maintenance, "is_sandbox_working_path", return_value=True):
                maintenance._validate_permissions(root, [move], self.policy, {}, released_bindings=[binding])
                with self.assertRaisesRegex(ValueError, "binding changed"):
                    maintenance._validate_permissions(
                        root, [{**move, "sha256": "b" * 64}], self.policy, {}, released_bindings=[binding],
                    )
                with self.assertRaisesRegex(ValueError, "protected Gallery"):
                    maintenance._validate_permissions(
                        root, [{**move, "destination": "Angels/Other/gallery/other_image_123.jpg"}],
                        self.policy, {}, released_bindings=[binding],
                    )


class FragmentProposalTests(unittest.TestCase):
    def setUp(self):
        from tools.art.likeness_library.policy import load_policy

        self.policy = load_policy()
        self.cores, self.references = {}, {}
        self.basis = np.eye(7)
        self.add_identity("Sisters/Canonical", self.basis[0], self.basis[2])
        self.add_identity("Models/Fragment", self.basis[0], self.basis[1])

    def add_identity(self, folder, center, axis):
        members = [
            {"photoId": f"{folder}:{index}", "sha256": f"{folder}:hash:{index}",
             "vector": .8 * center + sign * .6 * axis, "qualityEligible": True}
            for index, sign in enumerate((1, -1))
        ]
        self.references[folder] = members
        self.cores[folder] = {
            "vector": center.copy(), "side": "Prospects", "category": folder.split("/")[0],
            "corePhotoIds": [row["photoId"] for row in members], "personIds": [folder],
            "identityProtected": False,
        }

    def result(self, **kwargs):
        return fragment_proposals(self.cores, self.references, self.policy, **kwargs)

    def test_supported_direct_fragment_is_evidence_only_and_order_independent(self):
        before = copy.deepcopy((self.cores, self.references))
        report = self.result()
        self.assertEqual(len(report["candidateLinks"]), 1)
        link = report["candidateLinks"][0]
        self.assertEqual((link["sourceFolder"], link["targetFolder"]),
                         ("Models/Fragment", "Sisters/Canonical"))
        self.assertEqual(link["identityMinimum"], .65)
        self.assertEqual(link["minimumIndependentReferences"], 2)
        self.assertTrue(all(row["qualified"] and row["independentSupportCount"] == 2
                            for row in link["members"]))
        self.assertEqual(report["activation"], "diagnostic-only")
        reverse = fragment_proposals(
            dict(reversed(list(self.cores.items()))),
            {key: list(reversed(rows)) for key, rows in self.references.items()}, self.policy,
        )
        self.assertEqual(report, reverse)
        json.dumps(report, allow_nan=False)
        for folder in self.cores:
            np.testing.assert_array_equal(self.cores[folder]["vector"], before[0][folder]["vector"])
            self.assertEqual(self.cores[folder]["corePhotoIds"], before[0][folder]["corePhotoIds"])
            self.assertEqual(len(self.references[folder]), len(before[1][folder]))

    def test_core_average_cannot_carry_an_unsupported_member(self):
        bad = {
            "photoId": "outlier", "sha256": "outlier-bytes", "qualityEligible": True,
            "vector": .1 * self.basis[0] + np.sqrt(.99) * self.basis[4],
        }
        source = "Models/Fragment"
        self.references[source].append(bad)
        self.cores[source]["corePhotoIds"].append(bad["photoId"])
        total = sum(row["vector"] for row in self.references[source])
        self.cores[source]["vector"] = total / np.linalg.norm(total)
        report = self.result()
        self.assertEqual(report["candidateLinks"], [])
        row = report["comparisons"][0]
        self.assertGreater(row["score"], row["identityMinimum"])
        self.assertIn("not every source core member", row["reason"])
        self.assertEqual([member["photoId"] for member in row["members"] if not member["qualified"]],
                         ["outlier"])

    def test_entry_level_resemblance_is_not_identity_equivalence(self):
        center = .6 * self.basis[0] + .8 * self.basis[3]
        self.add_identity("Models/Fragment", center, self.basis[1])
        report = self.result()
        self.assertEqual(report["candidateLinks"], [])
        self.assertIn("identity-merge threshold", report["comparisons"][0]["reason"])

    def test_content_correlation_and_ambiguity_do_not_supply_independent_support(self):
        for folder in ("Models/Fragment", "Sisters/Canonical"):
            for correlated in (False, True):
                with self.subTest(folder=folder, correlated=correlated):
                    references = copy.deepcopy(self.references)
                    if correlated:
                        references[folder][1]["vector"] = references[folder][0]["vector"].copy()
                    else:
                        references[folder][1]["sha256"] = references[folder][0]["sha256"]
                    report = fragment_proposals(self.cores, references, self.policy)
                    self.assertEqual(report["candidateLinks"], [])
                    self.assertIn("insufficient independent", report["comparisons"][0]["reason"])
        references = copy.deepcopy(self.references)
        references["Models/Fragment"][0]["sha256"] = references["Sisters/Canonical"][0]["sha256"]
        report = fragment_proposals(self.cores, references, self.policy)
        self.assertEqual(report["candidateLinks"], [])
        self.assertIn("shared source/target content", report["comparisons"][0]["reason"])
        cores, references = copy.deepcopy((self.cores, self.references))
        shared_id = references["Models/Fragment"][0]["photoId"]
        references["Sisters/Canonical"][0]["photoId"] = shared_id
        cores["Sisters/Canonical"]["corePhotoIds"][0] = shared_id
        report = fragment_proposals(cores, references, self.policy)
        self.assertEqual(report["candidateLinks"], [])
        self.assertIn("ambiguous reference photo ID", report["comparisons"][0]["reason"])

    def test_locks_negative_evidence_and_incomplete_references_hold(self):
        source, target = "Models/Fragment", "Sisters/Canonical"
        report = self.result(blocked_ids=[self.references[source][0]["photoId"]])
        self.assertIn("protected", report["comparisons"][0]["reason"])
        for mutate in ("source-protected", "different", "source-rejects", "target-rejects",
                       "stale", "quality", "missing"):
            with self.subTest(mutate=mutate):
                cores, references, policy = copy.deepcopy((self.cores, self.references, self.policy))
                if mutate == "source-protected":
                    cores[source]["identityProtected"] = True
                elif mutate == "different":
                    policy["runtimeSettings"]["different"].append([source, target])
                elif mutate == "source-rejects":
                    references[source][0]["rejectedPersonIds"] = [target]
                elif mutate == "target-rejects":
                    references[target][0]["rejectedPersonIds"] = [source]
                elif mutate == "stale":
                    references[target][0]["rejectionMetadataStale"] = True
                elif mutate == "quality":
                    references[source][0]["qualityEligible"] = False
                else:
                    references[target].pop()
                report = fragment_proposals(cores, references, policy)
                self.assertEqual(report["candidateLinks"], [])
                self.assertEqual(report["comparisons"][0]["decision"], "hold")

    def test_multiple_canonical_hypotheses_stay_ambiguous(self):
        self.add_identity("Angels/Other", self.basis[0], self.basis[3])
        report = self.result()
        self.assertEqual(report["candidateLinks"], [])
        rows = [row for row in report["comparisons"] if row["sourceFolder"] == "Models/Fragment"]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all("multiple higher" in row["reason"] for row in rows))

    def test_direct_chain_never_invents_a_transitive_identity_link(self):
        middle = .8 * self.basis[0] + .6 * self.basis[3]
        lower = .8 * middle + .6 * self.basis[4]
        self.add_identity("Models/Fragment", middle, self.basis[1])
        self.add_identity("Prospects/Lower", lower, self.basis[5])
        report = self.result()
        pairs = {(row["sourceFolder"], row["targetFolder"]) for row in report["candidateLinks"]}
        self.assertIn(("Models/Fragment", "Sisters/Canonical"), pairs)
        self.assertIn(("Prospects/Lower", "Models/Fragment"), pairs)
        self.assertNotIn(("Prospects/Lower", "Sisters/Canonical"), pairs)
        self.assertFalse(any(row["sourceFolder"].startswith("Sisters/") for row in report["comparisons"]))

    def test_invalid_frozen_vectors_fail_explicitly(self):
        self.references["Models/Fragment"][0]["vector"] = np.array([np.nan] * 7)
        with self.assertRaisesRegex(ValueError, "invalid fragment reference"):
            self.result()

    def test_zero_centered_core_is_a_visible_hold_not_an_equivalence(self):
        self.cores["Models/Fragment"]["vector"] = np.zeros(7)
        for row in self.references["Models/Fragment"]:
            row["vector"] = np.zeros(7)
        report = self.result()
        self.assertEqual(report["candidateLinks"], [])
        self.assertIn("zero-norm frozen core", report["comparisons"][0]["reason"])


class ReconciliationTests(unittest.TestCase):
    def test_high_group_cast_resemblance_does_not_consume_a_competing_identity(self):
        from tools.art.likeness_library.policy import load_policy

        rows = []
        for index in range(6):
            vector = np.zeros(8)
            vector[0], vector[1] = .395, .4
            vector[index + 2] = np.sqrt(1 - .395**2 - .4**2)
            rows.append(candidate(f"photo:image_{910000 + index}", vector))
        centroid = np.mean([row["vector"] for row in rows], axis=0)
        self.assertGreater(centroid[0] / np.linalg.norm(centroid), .55)
        self.assertTrue(all(row["vector"][0] < .4 for row in rows))
        cores = {"Angels/Angelica": {
            "vector": np.eye(8)[0], "side": "Prospects", "category": "Angels",
        }}
        policy = load_policy()
        result = plan_reconciliation(rows, cores, policy=policy, name_factory=stable_name)
        self.assertEqual(result["assignedCount"], 6)
        self.assertEqual(result["heldCount"], 0)
        # Item (b): a five-plus group that is yellow but not green forms as a Potential.
        self.assertTrue(result["clusters"][0]["destination"].startswith("Potentials/"))
        self.assertEqual(result["clusters"][0]["formation"]["band"], "yellow")
        self.assertTrue(all(.30 <= score < .55 for score in result["clusters"][0]["formation"]["memberScores"].values()))
        self.assertIn("yellow but not green", result["clusters"][0]["reason"])
        self.assertEqual(result["clusters"][0]["photoIds"], sorted(row["photoId"] for row in rows))
        reverse = plan_reconciliation(list(reversed(rows)), cores, policy=policy, name_factory=stable_name)
        self.assertEqual(result["assignments"], reverse["assignments"])
        self.assertEqual(result["clusters"], reverse["clusters"])
        policy["groupCastReviewEnabled"] = True
        legacy = plan_reconciliation(rows, cores, policy=policy, name_factory=stable_name)
        self.assertEqual(legacy["assignedCount"], 0)
        self.assertTrue(all(row["reviewDestination"] == "Angels/Angelica/review"
                            and row["automaticReviewAssociation"] for row in legacy["held"]))

    def test_individually_yellow_cast_matches_can_build_a_model_cluster(self):
        from tools.art.likeness_library.policy import load_policy

        result = plan_reconciliation(
            [
                candidate(f"photo:image_{900000 + index}", [.45, np.sqrt(1 - .45**2)])
                for index in range(6)
            ],
            {
                "Angels/Angelica": {
                    "vector": np.array([1., 0.]), "side": "Prospects", "category": "Angels",
                },
            },
            cluster=.55, policy=load_policy(), name_factory=stable_name,
        )
        self.assertEqual(result["assignedCount"], 6)
        self.assertEqual(result["held"], [])
        self.assertTrue(result["clusters"][0]["destination"].startswith("Models/"))

    def test_category_moves_create_missing_configured_destination_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = root / "Prospects" / "Sophie"
            source.mkdir(parents=True)
            photo = source / "gallery" / "sophie.jpg"
            photo.parent.mkdir()
            photo.write_bytes(b"photo")

            moved = apply_category_changes(
                root,
                [("Prospects/Sophie", "Models/Sophie", 1, False)],
                {"Prospects", "Models"},
            )

            self.assertEqual(moved, 1)
            self.assertFalse(source.exists())
            self.assertEqual(
                (root / "Models" / "Sophie" / "gallery" / "sophie.jpg").read_bytes(),
                b"photo",
            )

    def test_workflow_selected_photos_are_collected_across_all_flows(self):
        config = {
            "photos": {"Sophie": "sophie_image_500001.jpg"},
            "flows": {
                "alpha": {"photos": {"Sophie": "sophie_image_500002.jpg"}},
            },
        }

        selected = likeness.chosen_keys(config)

        self.assertEqual(
            selected,
            {
                likeness.cw.photo_key("sophie_image_500001.jpg"),
                likeness.cw.photo_key("sophie_image_500002.jpg"),
            },
        )

    def test_review_and_pool_candidates_form_one_order_independent_cluster(self):
        rows = [
            candidate("photo:image_100001", [1, 0], folder="Various"),
            candidate("photo:image_100002", [0.99, 0.01], folder="Prospects/Sophie", bucket="Review"),
            candidate("photo:image_100003", [0.98, 0.02], folder="Various"),
        ]
        first = plan_reconciliation(rows, {}, name_factory=stable_name)
        second = plan_reconciliation(list(reversed(rows)), {}, name_factory=stable_name)

        self.assertEqual(first["clusters"], second["clusters"])
        self.assertEqual(first["assignments"], second["assignments"])
        self.assertEqual(first["held"], [])
        self.assertEqual(first["clusters"][0]["destinationType"], "provisional")
        self.assertTrue(first["clusters"][0]["destination"].startswith("Potentials/"))
        self.assertEqual(first["assignedCount"], 3)

    def test_confident_existing_match_respects_margin_and_artist_boundary(self):
        cores = {
            "Prospects/A": {"vector": np.array([1.0, 0.0]), "side": "Prospects"},
            "Prospects/B": {"vector": np.array([0.0, 1.0]), "side": "Prospects"},
            "Artists/One/Person": {"vector": np.array([1.0, 0.0]), "side": "Artists"},
        }
        rows = [
            candidate("photo:image_200001", [0.99, 0.01]),
            candidate("photo:image_200002", [0.71, 0.70]),
            candidate("photo:image_200003", [0.99, 0.01], side="Artists"),
        ]

        result = plan_reconciliation(rows, cores, name_factory=stable_name)

        assigned = {row["photoId"]: row["destination"] for row in result["assignments"]}
        self.assertEqual(assigned["photo:image_200001"], "Prospects/A")
        self.assertEqual(assigned["photo:image_200003"], "Artists/One/Person")
        self.assertIn("photo:image_200002", {row["photoId"] for row in result["held"]})

    def test_policy_protects_target_identity_from_photo_routing(self):
        from tools.art.likeness_library.policy import load_policy

        cores = {
            "Prospects/Protected": {
                "vector": np.array([1.0, 0.0]),
                "side": "Prospects",
                "category": "Prospects",
                "identityProtected": True,
            }
        }
        result = plan_reconciliation(
            [candidate("photo:image_200004", [1.0, 0.0])],
            cores,
            minimum_cluster=3,
            cluster=0.55,
            policy=load_policy(),
            name_factory=stable_name,
        )

        self.assertEqual(result["assignments"], [])
        self.assertEqual(result["held"][0]["reviewDestination"], "Prospects/Protected/review")
        self.assertIn("protected Gallery", result["held"][0]["reason"])

    def test_small_incoming_cast_like_cluster_remains_provisional_under_individual_policy(self):
        from tools.art.likeness_library.policy import load_policy

        vectors = []
        for score in (0.315, 0.464, 0.411, 0.455):
            vectors.append([score, np.sqrt(1 - score**2)])
        cores = {
            "Angels/angelica": {
                "vector": np.array([1.0, 0.0]),
                "side": "Prospects",
                "category": "Angels",
                "identityProtected": True,
            },
            "Sisters/Draknara": {
                "vector": np.array([-1.0, 0.0]),
                "side": "Prospects",
                "category": "Sisters",
                "identityProtected": True,
            },
        }
        rows = [
            candidate(f"photo:image_{210001 + index}", vector)
            for index, vector in enumerate(vectors)
        ]

        result = plan_reconciliation(
            rows,
            cores,
            assign=0.40,
            margin=0.10,
            cluster=0.25,
            minimum_cluster=3,
            policy=load_policy(),
            name_factory=stable_name,
        )

        self.assertEqual(result["assignedCount"], 4)
        self.assertEqual(result["heldCount"], 0)
        self.assertTrue(result["clusters"][0]["destination"].startswith("Potentials/"))
        legacy_policy = load_policy()
        legacy_policy["groupCastReviewEnabled"] = True
        result = plan_reconciliation(rows, cores, policy=legacy_policy, name_factory=stable_name)
        self.assertEqual(result["heldCount"], 4)
        self.assertEqual(
            {row["reviewDestination"] for row in result["held"]},
            {"Angels/angelica/review"},
        )
        self.assertTrue(
            all(row["bestMatch"] == "Angels/angelica" for row in result["held"])
        )

    def test_draft_proposal_reports_qualified_destination_without_authorizing_apply(self):
        from tools.art.likeness_library.policy import load_policy

        result = plan_reconciliation(
            [candidate("photo:image_200005", [1.0, 0.0])],
            {
                "Potentials/Amara Madison": {
                    "vector": np.array([1.0, 0.0]),
                    "side": "Prospects",
                    "category": "Potentials",
                }
            },
            minimum_cluster=3,
            cluster=0.55,
            policy=load_policy(),
            name_factory=stable_name,
        )

        self.assertTrue(result["authorizationRequired"])
        self.assertEqual(result["held"], [])
        self.assertEqual(result["assignments"][0]["destination"], "Potentials/Amara Madison")
        self.assertEqual(result["assignments"][0]["score"], 1.0)

    def test_policy_preserves_a_perfect_pair_without_cast_assignment_gate(self):
        from tools.art.likeness_library.policy import load_policy

        result = plan_reconciliation(
            [candidate("p1", [0, 1]), candidate("p2", [0, 1])],
            {"Angels/A": {"vector": np.array([1., 0.]), "side": "Prospects"}},
            minimum_cluster=3, cluster=.55, policy=load_policy(), name_factory=stable_name,
        )
        self.assertEqual(result["assignedCount"], 2)
        self.assertEqual(len(result["clusters"]), 1)
        self.assertEqual(result["clusters"][0]["photoIds"], ["p1", "p2"])

    def test_cast_protection_does_not_change_unrelated_grouping(self):
        from tools.art.likeness_library.policy import load_policy

        rows = [candidate("p1", [0, 1]), candidate("p2", [0, 1])]
        policy = load_policy()
        first = plan_reconciliation(rows, {}, policy=policy, name_factory=stable_name)
        second = plan_reconciliation(
            rows, {"Angels/A": {"vector": np.array([1., 0.]), "side": "Prospects", "identityProtected": True}},
            policy=policy, name_factory=stable_name,
        )
        self.assertEqual(first["clusters"][0]["photoIds"], second["clusters"][0]["photoIds"])

    def test_provisional_followup_reclassifies_final_five_photo_membership(self):
        from tools.art.likeness_library.policy import load_policy

        policy = load_policy()
        policy["identityActions"]["identityClusterMinimumSimilarity"] = .8
        rows = [
            candidate(str(index), [np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))])
            for index, angle in enumerate((-10, 0, 10, 15, 60))
        ]
        result = plan_reconciliation(rows, {}, policy=policy, name_factory=stable_name)
        self.assertEqual(len(result["clusters"]), 1)
        self.assertEqual(len(result["clusters"][0]["photoIds"]), 5)
        self.assertTrue(result["clusters"][0]["destination"].startswith("Prospects/"))

    def test_remaining_candidate_can_join_fixed_provisional_cluster(self):
        angles = [-10, 0, 10, 60]
        rows = [
            candidate(
                f"photo:image_{300001 + index}",
                [np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))],
                bucket="Review" if index == 1 else "Pool",
            )
            for index, angle in enumerate(angles)
        ]

        result = plan_reconciliation(
            rows,
            {},
            assign=0.48,
            margin=0.10,
            cluster=0.80,
            minimum_cluster=3,
            name_factory=stable_name,
        )

        self.assertEqual(len(result["clusters"]), 1)
        destination = result["clusters"][0]["destination"]
        joined = next(row for row in result["assignments"] if row["photoId"] == "photo:image_300004")
        self.assertEqual(joined["destination"], destination)
        self.assertEqual(joined["destinationType"], "provisional")
        self.assertIn("frozen provisional cluster", joined["reason"])

    def test_ambiguous_candidate_cluster_does_not_create_a_new_identity(self):
        cores = {
            "Prospects/A": {"vector": np.array([0.99, 0.10]), "side": "Prospects"},
            "Prospects/B": {"vector": np.array([0.99, -0.10]), "side": "Prospects"},
        }
        rows = [candidate(f"photo:image_{350001 + index}", [1, 0]) for index in range(3)]

        result = plan_reconciliation(rows, cores, name_factory=stable_name)

        self.assertEqual(result["assignments"], [])
        self.assertEqual(result["clusters"], [])
        self.assertEqual(result["heldCount"], 3)
        self.assertTrue(all("ambiguous destination" in row["reason"] for row in result["held"]))

    def test_protected_duplicate_and_missing_ids_stay_staged(self):
        rows = [
            candidate("photo:image_400001", [1, 0], protected=True),
            candidate("photo:image_400002", [1, 0], protected=True),
            candidate("photo:image_400002", [0.99, 0.01]),
            candidate(None, [1, 0]),
        ]

        result = plan_reconciliation(rows, {}, name_factory=stable_name)

        reasons = [row["reason"] for row in result["held"]]
        self.assertEqual(result["assignments"], [])
        self.assertIn("protected photo; remains staged", reasons)
        self.assertIn("duplicate stable photo ID; remains staged", reasons)
        self.assertIn("missing stable photo ID", reasons)

    def test_frozen_core_uses_anchors_and_excludes_protected_photos(self):
        photos = [
            FakePhoto("anchor", [1, 0]),
            FakePhoto("b", [0, 1]),
            FakePhoto("c", [0.01, 1]),
            FakePhoto("protected", [-1, 0]),
        ]
        space = SimpleNamespace(
            photos=photos,
            by_key={"Prospects/Sophie": photos},
            st={"minFace": 60},
        )
        catalog = {
            "people": {
                "person_1": {
                    "folder": "Prospects/Sophie",
                    "identityAnchors": ["anchor"],
                }
            },
            "photos": {
                "anchor": {"contentSha256": "anchor-hash", "protected": False},
                "protected": {"contentSha256": "protected-hash", "protected": True},
            },
        }

        cores, locked, diagnostics = frozen_identity_cores(
            space,
            catalog,
            photo_id_fn=lambda name: name,
            content_sha256_fn=lambda path: f"{path}-hash",
        )

        np.testing.assert_allclose(cores["Prospects/Sophie"]["vector"], [1, 0])
        self.assertEqual(cores["Prospects/Sophie"]["mode"], "trusted")
        self.assertIn("protected", locked)
        self.assertEqual(diagnostics, [])

    def test_stale_anchor_is_ignored_for_core_construction(self):
        photos = [
            FakePhoto("anchor", [1, 0]),
            FakePhoto("b", [0, 1]),
            FakePhoto("c", [0.01, 1]),
            FakePhoto("d", [0.02, 1]),
        ]
        space = SimpleNamespace(
            photos=photos,
            by_key={"Prospects/Sophie": photos},
            st={"minFace": 60},
        )
        catalog = {
            "people": {
                "person_1": {
                    "folder": "Prospects/Sophie",
                    "identityAnchors": ["anchor"],
                }
            },
            "photos": {"anchor": {"contentSha256": "old-hash", "protected": True}},
        }

        cores, locked, _ = frozen_identity_cores(
            space,
            catalog,
            photo_id_fn=lambda name: name,
            content_sha256_fn=lambda _path: "new-hash",
        )

        self.assertEqual(cores["Prospects/Sophie"]["mode"], "provisional")
        self.assertNotIn("anchor", locked)
        self.assertGreater(cores["Prospects/Sophie"]["vector"][1], 0.99)

    def test_reconcile_command_writes_report_without_changing_source_photo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            photo_path = root / "sophie_image_500001.jpg"
            photo_path.write_bytes(b"unchanged source")
            photo = FakePhoto(photo_path.name, [1, 0])
            photo.path = photo_path
            photo.key = "Various"
            report_path = root / "reconciliation.json"
            settings = {
                "pool": ["Various"],
                "minFace": 60,
                "assign": 0.40,
                "margin": 0.10,
                "cluster": 0.25,
                "minCluster": 3,
                "castMerge": 0.55,
            }
            args = SimpleNamespace(root=None, embedder=None, out=str(report_path), policy=None)
            output = io.StringIO()
            with mock.patch.object(
                likeness,
                "build",
                return_value=(
                    {"photos": {"Sophie": photo_path.name}, "flows": {}},
                    settings,
                    root,
                    None,
                    SimpleNamespace(photos=[photo], by_key={}, st=settings),
                ),
            ), mock.patch.object(likeness, "load_review", return_value=[]), mock.patch.object(
                likeness.metadata, "load_catalog", return_value={"people": {}, "photos": {}}
            ), mock.patch.object(likeness.cw, "photo_folders", return_value=[]), mock.patch.object(
                likeness, "junk_reason", return_value=False
            ), contextlib.redirect_stdout(output):
                likeness.cmd_reconcile(args)

            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["candidateCount"], 1)
            self.assertEqual(report["heldCount"], 1)
            self.assertEqual(report["held"][0]["reason"], "workflow-selected photo; remains staged")
            self.assertEqual(report["source"], "likeness-reconcile")
            self.assertIn("No images or catalogue data are changed", output.getvalue())
            self.assertEqual(photo_path.read_bytes(), b"unchanged source")


class BandFormationAndSinglePhotoTests(unittest.TestCase):
    """Items (b), (c, e) and (f): band-aligned formation and match-only quality."""

    def setUp(self):
        from tools.art.likeness_library import normal_admission
        from tools.art.likeness_library.policy import effective_settings, load_policy

        self.admission = normal_admission
        self.policy = load_policy()
        self.settings = effective_settings({}, self.policy)
        self.axes = np.eye(8)

    @staticmethod
    def at(score, first, second):
        return score * first + np.sqrt(1 - score ** 2) * second

    def plan(self, rows, cores=None, **kwargs):
        return plan_reconciliation(rows, cores or {}, policy=self.policy, name_factory=stable_name, **kwargs)

    def test_orange_pair_no_longer_forms_a_two_photo_identity(self):
        rows = [
            candidate("photo:image_1", self.axes[0]),
            candidate("photo:image_2", self.at(.27, self.axes[0], self.axes[1])),
        ]
        result = self.plan(rows)
        self.assertEqual(len(result["clusters"]), 2)
        for cluster in result["clusters"]:
            self.assertTrue(cluster["singlePhoto"])
            self.assertEqual(cluster["formation"]["band"], "single-photo")
            self.assertIn("single photo – not yet scoreable", cluster["reason"])
            self.assertTrue(cluster["destination"].startswith("Potentials/"))
        self.assertTrue(all(row["singlePhoto"] for row in result["assignments"]))

    def test_yellow_pair_forms_potential_and_green_five_forms_prospect(self):
        pair = self.plan([
            candidate("photo:image_1", self.axes[0]),
            candidate("photo:image_2", self.at(.4, self.axes[0], self.axes[1])),
        ])
        self.assertEqual(len(pair["clusters"]), 1)
        self.assertEqual(pair["clusters"][0]["formation"]["band"], "yellow")
        self.assertTrue(pair["clusters"][0]["destination"].startswith("Potentials/"))
        five = self.plan([
            candidate(f"photo:image_{10 + index}", self.at(.9, self.axes[0], self.axes[index + 1]))
            for index in range(5)
        ])
        self.assertEqual(len(five["clusters"]), 1)
        self.assertEqual(five["clusters"][0]["formation"]["band"], "green")
        self.assertTrue(five["clusters"][0]["destination"].startswith("Prospects/"))
        self.assertTrue(all(score >= .55 for score in five["clusters"][0]["formation"]["memberScores"].values()))

    def test_band_trim_drops_below_yellow_members(self):
        from tools.art.likeness_library import planner

        rows = [
            {"photoId": "a", "vector": self.axes[0]},
            {"photoId": "b", "vector": self.at(.9, self.axes[0], self.axes[1])},
            {"photoId": "c", "vector": self.at(.1, self.axes[0], self.axes[2])},
        ]
        kept, removed, scores = planner._band_trim(rows, .30)
        self.assertEqual([row["photoId"] for row in kept], ["a", "b"])
        self.assertEqual([row["photoId"] for row in removed], ["c"])
        self.assertTrue(all(value >= .30 for value in scores.values()))

    def test_leftover_reaching_yellow_goes_to_rival_review_not_new_identity(self):
        cores = {"Angels/Ava": {"vector": self.axes[0], "side": "Prospects", "category": "Angels",
                                "personIds": ["person_ava"]}}
        row = candidate("photo:image_1", self.at(.33, self.axes[0], self.axes[1]))
        result = self.plan([row], cores)
        self.assertEqual(result["clusters"], [])
        self.assertEqual(result["held"][0]["reviewDestination"], "Angels/Ava/review")
        self.assertEqual(result["held"][0]["singlePhotoGate"]["bestRival"], "Angels/Ava")
        rejected = self.plan([{**row, "rejectedPersonIds": ["person_ava"]}], cores)
        self.assertEqual(len(rejected["clusters"]), 1)
        self.assertTrue(rejected["clusters"][0]["singlePhoto"])
        below = self.plan([candidate("photo:image_1", self.at(.2, self.axes[0], self.axes[1]))], cores)
        self.assertTrue(below["clusters"][0]["singlePhoto"])
        self.assertAlmostEqual(below["assignments"][0]["singlePhotoGate"]["bestRivalScore"], .2, places=4)

    def test_cast_lock_excludes_cast_rival_from_single_photo_review(self):
        refs = [{"photoId": f"ref:{index}", "sha256": f"{index}" * 64,
                 "vector": .8 * self.axes[0] + sign * .6 * self.axes[3], "qualityEligible": True}
                for index, sign in enumerate((1, -1))]
        cores = {"Sisters/Drakness": {
            "vector": self.axes[0], "side": "Prospects", "category": "Sisters",
            "corePhotoIds": [row["photoId"] for row in refs], "personIds": ["person_d"],
            "identityProtected": True,
        }}
        row = candidate("photo:image_1", self.at(.33, self.axes[0], self.axes[1]),
                        qualityEligible=True, sha256="b" * 64)
        for locked, expected in ((False, "Sisters/Drakness/review"), (True, None)):
            ctx = self.admission.context(cores, {"Sisters/Drakness": refs}, self.policy, locked=locked)
            result = self.plan([row], cores, admission_context=ctx)
            if expected:
                self.assertEqual(result["held"][0]["reviewDestination"], expected)
            else:
                self.assertTrue(result["clusters"][0]["singlePhoto"])

    def test_match_only_photo_matches_existing_but_never_founds_or_votes(self):
        cores = {"Potentials/Amara": {"vector": self.axes[0], "side": "Prospects", "category": "Potentials"}}
        quality = {"class": "dominant-face", "matchEligible": True, "referenceEligible": False,
                   "reason": "dominant main face"}
        matched = self.plan([candidate("photo:image_1", self.axes[0], referenceQualityEligible=False,
                                       faceQuality=quality)], cores)
        self.assertEqual(matched["assignments"][0]["destination"], "Potentials/Amara")
        self.assertFalse(matched["assignments"][0]["referenceEligible"])
        self.assertEqual(matched["assignments"][0]["faceQuality"]["class"], "dominant-face")
        alone = self.plan([candidate("photo:image_2", self.axes[5], referenceQualityEligible=False)], cores)
        self.assertEqual(alone["clusters"], [])
        self.assertTrue(alone["held"][0]["preserveStaged"])
        self.assertIn("cannot found a new identity", alone["held"][0]["reason"])

    def test_match_only_admissions_never_become_reference_votes(self):
        refs = [{"photoId": f"ref:{index}", "sha256": f"{index}" * 64,
                 "vector": .8 * self.axes[1] + sign * .6 * self.axes[4], "qualityEligible": True}
                for index, sign in enumerate((1, -1))]
        cores = {"Models/Lower": {
            "vector": self.axes[1], "side": "Prospects", "category": "Models",
            "corePhotoIds": [row["photoId"] for row in refs], "personIds": ["person_l"],
            "identityProtected": False,
        }}
        api = SimpleNamespace(plan_reconciliation=plan_reconciliation, invent_name=stable_name)
        for reference_quality, expected in ((True, True), (False, False)):
            row = candidate("photo:image_9", self.axes[1], qualityEligible=True, sha256="c" * 64,
                            referenceQualityEligible=reference_quality)
            report = self.admission.two_round_plan(
                api, [row], cores, {"Models/Lower": refs}, self.settings, self.policy, set(),
            )
            decision = report["assignments"][0]
            self.assertEqual(decision["destination"], "Models/Lower")
            self.assertIs(decision["referenceEligible"], expected)

    def test_match_only_cast_gallery_admission_is_not_reference_eligible(self):
        refs = [{"photoId": f"ref:{index}", "sha256": f"{index}" * 64,
                 "vector": .8 * self.axes[0] + sign * .6 * self.axes[3], "qualityEligible": True}
                for index, sign in enumerate((1, -1))]
        cores = {"Sisters/Drakness": {
            "vector": self.axes[0], "side": "Prospects", "category": "Sisters",
            "corePhotoIds": [row["photoId"] for row in refs], "personIds": ["person_d"],
            "identityProtected": True,
        }}
        ctx = self.admission.context(cores, {"Sisters/Drakness": refs}, self.policy)
        for reference_quality in (True, False):
            row = candidate("photo:image_8", self.axes[0], qualityEligible=True, sha256="d" * 64,
                            referenceQualityEligible=reference_quality)
            kind, decision = self.admission.cast_route(row, cores, self.policy, ctx)
            self.assertEqual((kind, decision["castAdmission"]["mode"]), ("assignments", "supported-gallery"))
            self.assertIs(decision["referenceEligible"], reference_quality)


class FaceQualityTests(unittest.TestCase):
    """Item (f): dominant-face matching, overlap re-detection and framing."""

    settings = {"minFace": 60, "multiFace": .3, "dominantFaceSecondaryMaximum": .5}

    @staticmethod
    def photo(faces, f2, px=200, box=(.3, .2, .2, .25)):
        return SimpleNamespace(faces=faces, f2=f2, px=px, box=list(box),
                               usable=lambda minimum: px >= minimum)

    def assess(self, photo, **kwargs):
        from tools.art.likeness_library import face_quality

        return face_quality.assess(photo, self.settings, path="image.jpg", **kwargs)

    def test_single_dominant_and_held_classes(self):
        single = self.assess(self.photo(1, 0))
        self.assertEqual((single["class"], single["matchEligible"], single["referenceEligible"]),
                         ("single-face", True, True))
        for ratio in (.1, .3, .49):
            dominant = self.assess(self.photo(3, ratio))
            self.assertEqual((dominant["class"], dominant["matchEligible"], dominant["referenceEligible"]),
                             ("dominant-face", True, False))
        self.assertEqual(self.assess(self.photo(2, .5))["class"], "multi-face-held")
        self.assertFalse(self.assess(self.photo(2, .7))["matchEligible"])
        self.assertEqual(self.assess(self.photo(2, .4, px=40))["class"], "unusable")
        self.assertIn("framing", self.assess(self.photo(2, .4, box=(0, 0, 0, 0)))["reason"])
        framing = self.assess(self.photo(2, .4), framing=lambda _path, _photo: "head crop too small")
        self.assertFalse(framing["matchEligible"])
        self.assertIn("head crop too small", framing["reason"])

    def test_near_equal_second_box_requires_overlap_redetection(self):
        main = (100., 100., 80., 100.)
        overlapping = (104., 102., 78., 98.)
        separate = (400., 100., 80., 100.)
        self.assertEqual(self.assess(self.photo(2, .96))["class"], "multi-face-held")
        merged = self.assess(self.photo(2, .96), redetect=lambda _path: [main, overlapping])
        self.assertEqual((merged["class"], merged["matchEligible"], merged["referenceEligible"]),
                         ("overlapping-duplicate-box", True, False))
        self.assertGreater(merged["secondBoxIoU"], .5)
        apart = self.assess(self.photo(2, 1.), redetect=lambda _path: [main, separate])
        self.assertEqual(apart["class"], "multi-face-held")
        self.assertIn("separate", apart["reason"])
        disagree = self.assess(self.photo(2, .96), redetect=lambda _path: [main])
        self.assertIn("does not reproduce", disagree["reason"])

        def broken(_path):
            raise OSError("unreadable")

        self.assertIn("re-detection failed", self.assess(self.photo(2, .96), redetect=broken)["reason"])

    def test_policy_accepts_optional_dominant_setting(self):
        from tools.art.likeness_library.policy import load_policy, validate_policy

        policy = load_policy()
        self.assertEqual(policy["runtimeSettings"]["dominantFaceSecondaryMaximum"], .5)
        broken = copy.deepcopy(policy)
        broken["runtimeSettings"]["dominantFaceSecondaryMaximum"] = .2
        with self.assertRaisesRegex(ValueError, "at least multiFace"):
            validate_policy(broken)
        del broken["runtimeSettings"]["dominantFaceSecondaryMaximum"]
        validate_policy(broken)


class FakePhoto:
    def __init__(self, name, vector):
        self.name = name
        self.path = name
        self.vec = np.asarray(vector, dtype=float)

    def usable(self, _minimum):
        return True


if __name__ == "__main__":
    unittest.main()
