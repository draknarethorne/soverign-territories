"""Synthetic acceptance for bounded, report-only full-population realignment."""
import copy
import json
import math
import unittest

import numpy as np

from tools.art.likeness_library import policy
from tools.art.likeness_library import realignment


def unit(values):
    vector = np.asarray(values, dtype=float)
    return vector / np.linalg.norm(vector)


class RealignmentTests(unittest.TestCase):
    def setUp(self):
        self.settings = copy.deepcopy(policy.load_policy())
        self.settings["protection"]["automatic"]["minimumIndependentReferences"] = 2
        self.settings["photoRouting"]["minimumOwnCoreLead"] = .1
        for category in self.settings["categoryPolicies"].values():
            category["minimumUsablePhotosForOutlierActions"] = 3
            category["automaticPhotoRoutingEnabled"] = True
        self.settings["categoryPolicies"]["Models"]["identityCoreMinimumSimilarity"] = .3
        self.settings["categoryPolicies"]["Models"]["photoRouteMinimum"] = .5
        self.settings["categoryPolicies"]["Models"]["photoRouteMargin"] = .1
        self.settings["identityActions"]["identityClusterMinimumSimilarity"] = .25
        self.run = {
            "photos": [], "finalMembershipAudit": {"rows": []},
            "policy": self.settings,
        }
        self.vectors = {}
        self.target_ids = []
        self.source_ids = []
        for index, angle in enumerate((0., math.pi / 2, math.pi, 3 * math.pi / 2)):
            self.target_ids.append(self.add_photo(
                f"target-{index}", "Models/Target",
                unit([1., .32 * math.cos(angle), .32 * math.sin(angle), 0.,
                      0., 0., 0., 0.]),
                core=False,
            ))
        for index, angle in enumerate((0., math.pi / 2, math.pi)):
            self.source_ids.append(self.add_photo(
                f"source-{index}", "Models/Source",
                unit([0., 1., 0., 0., .3 * math.cos(angle), .3 * math.sin(angle), 0., 0.]),
                core=False,
            ))
        self.query_id = self.add_photo(
            "query", "Models/Source", unit([1., 0., 0., 0., 0., 0., 0., 0.]), core=False,
        )
        self.empty_packet = {
            "packetSHA256": "packet-bound", "binding": {"run": "receipt"},
            "characters": [],
        }
        self.empty_answers = {
            "schemaVersion": 1, "kind": "character-reference-answers",
            "packetSHA256": "packet-bound", "binding": {"run": "receipt"},
            "characters": [],
        }
        self.labels = {"pairs": []}

    def add_photo(self, photo_id, folder, vector, *, sha=None, bucket="gallery", core=False,
                  quality=True, identity_ids=None, category=None):
        suffix = "gallery" if bucket == "gallery" else "review"
        destination = f"{folder}/{suffix}/{photo_id}.png"
        digest = sha or f"sha-{photo_id}"
        category = category or folder.split("/", 1)[0]
        photo = {
            "photoId": photo_id, "destination": destination, "preparedSHA256": digest,
        }
        saved = {
            **photo, "qualityEligible": quality, "coreMember": core,
            "bucket": bucket, "identityIds": identity_ids or [f"person:{folder}"],
            "protected": False, "anchor": False, "workflowSelected": False,
            "identityProtected": False, "metadataStale": False,
            "ambiguousPhotoId": False, "rejectionHistory": False,
            "category": category,
        }
        self.run["photos"].append(photo)
        self.run["finalMembershipAudit"]["rows"].append(saved)
        self.vectors[photo_id] = np.asarray(vector, dtype=float)
        return photo_id

    def evaluate(self, *, packet=None, answers=None, labels=None, **kwargs):
        return realignment.evaluate(
            self.run, self.vectors, packet or self.empty_packet,
            answers or self.empty_answers, labels or self.labels, **kwargs,
        )

    def row(self, result, photo_id):
        return next(row for row in result["rows"] if row["photoId"] == photo_id)

    def test_unlabelled_member_generates_separate_automatic_hypothesis(self):
        result = self.evaluate()
        row = self.row(result, self.query_id)
        self.assertEqual(row["origin"], "automatic-hypothesis")
        self.assertEqual(row["candidateFolder"], "Models/Target")
        self.assertEqual(row["state"], "tentative")
        self.assertEqual(row["execution"], "not-authorized")
        self.assertGreaterEqual(
            row["evidence"]["topCandidates"][0]["support"],
            self.settings["protection"]["automatic"]["minimumIndependentReferences"],
        )
        self.assertEqual(result["summary"]["automaticHypothesisCount"], 1)
        self.assertEqual(result["summary"]["explicitIntentCandidateCount"], 0)
        self.assertFalse(any("identityProtected" in row for row in result["rows"]))

    def test_all_current_groups_rebuild_from_members_not_saved_core_flags(self):
        result = self.evaluate()
        by_folder = {item["folder"]: item for item in result["identities"]}
        self.assertEqual(by_folder["Models/Target"]["referencePhotoIds"], self.target_ids)
        self.assertEqual(by_folder["Models/Target"]["referenceStatus"], "provisional")
        self.assertEqual(by_folder["Models/Source"]["referencePhotoIds"], self.source_ids)
        self.assertEqual(
            by_folder["Models/Target"]["referenceEvidence"]["construction"],
            "audit-person-provisional",
        )

    def test_confirmed_reference_intent_replaces_baseline_and_excludes_other_answers(self):
        packet = copy.deepcopy(self.empty_packet)
        answers = copy.deepcopy(self.empty_answers)
        packet["characters"] = [{
            "folder": "Models/Target",
            "cards": [{"photoId": pid} for pid in self.target_ids[:2]],
        }]
        answers["characters"] = [{
            "folder": "Models/Target",
            "decisions": [
                {"photoId": self.target_ids[0], "choice": "reference"},
                {"photoId": self.target_ids[1], "choice": "same-not-reference"},
            ],
        }]
        result = self.evaluate(packet=packet, answers=answers)
        target = next(item for item in result["identities"] if item["folder"] == "Models/Target")
        self.assertEqual(target["referencePhotoIds"], [self.target_ids[0]])
        self.assertEqual(
            target["referenceEvidence"]["construction"], "confirmed-character-intent",
        )
        self.assertEqual(result["summary"]["explicitIntentCandidateCount"], 2)
        self.assertNotIn(self.target_ids[1], target["referencePhotoIds"])
        intent_row = self.row(result, self.target_ids[1])
        self.assertEqual(
            intent_row["evidence"]["explicitIntentByFolder"]["Models/Target"],
            "same-not-reference",
        )

    def test_confirmed_character_with_no_references_is_not_filled_from_baseline(self):
        packet = copy.deepcopy(self.empty_packet)
        answers = copy.deepcopy(self.empty_answers)
        packet["characters"] = [{
            "folder": "Models/Target",
            "cards": [{"photoId": pid} for pid in self.target_ids[:2]],
        }]
        answers["characters"] = [{
            "folder": "Models/Target",
            "decisions": [
                {"photoId": self.target_ids[0], "choice": "different"},
                {"photoId": self.target_ids[1], "choice": "uncertain"},
            ],
        }]
        result = self.evaluate(packet=packet, answers=answers)
        target = next(item for item in result["identities"] if item["folder"] == "Models/Target")
        self.assertEqual(target["referencePhotoIds"], [])
        self.assertEqual(target["referenceStatus"], "reference-needed")
        self.assertEqual(target["referenceNeeded"], 3)

    def test_direct_different_pair_vetoes_candidate_without_transitive_spread(self):
        bridge = self.add_photo(
            "bridge", "Models/Source", self.vectors[self.query_id], core=False,
        )
        result = self.evaluate(labels={"pairs": [
            {"photoIds": [self.query_id, bridge], "label": "same"},
            {"photoIds": [bridge, self.target_ids[0]], "label": "different"},
        ]})
        query = self.row(result, self.query_id)
        bridge_row = self.row(result, bridge)
        self.assertEqual(query["candidateFolder"], "Models/Target")
        self.assertNotIn("direct-human-different-veto", query["blockers"])
        self.assertIn("direct-human-different-veto", bridge_row["blockers"])
        self.assertEqual(bridge_row["state"], "unresolved")

    def test_direct_different_pair_vetoes_explicit_intent(self):
        packet = copy.deepcopy(self.empty_packet)
        answers = copy.deepcopy(self.empty_answers)
        packet["characters"] = [{
            "folder": "Models/Target",
            "cards": [{"photoId": self.query_id}, {"photoId": self.target_ids[0]}],
        }]
        answers["characters"] = [{
            "folder": "Models/Target",
            "decisions": [
                {"photoId": self.query_id, "choice": "same-not-reference"},
                {"photoId": self.target_ids[0], "choice": "reference"},
            ],
        }]
        result = self.evaluate(
            packet=packet, answers=answers,
            labels={"pairs": [
                {"photoIds": [self.query_id, self.target_ids[0]], "label": "different"},
            ]},
        )
        row = self.row(result, self.query_id)
        self.assertEqual(row["candidateFolder"], "Models/Target")
        self.assertEqual(row["state"], "unresolved")
        self.assertIn("direct-human-different-veto", row["blockers"])

    def test_uncertain_pair_is_not_a_negative_veto(self):
        result = self.evaluate(labels={"pairs": [
            {"photoIds": [self.query_id, self.target_ids[0]], "label": "uncertain"},
        ]})
        row = self.row(result, self.query_id)
        self.assertEqual(row["candidateFolder"], "Models/Target")
        self.assertEqual(row["state"], "tentative")
        self.assertIn("direct-human-uncertainty", row["blockers"])
        self.assertNotIn("direct-human-different-veto", row["blockers"])

    def test_equal_content_reference_is_not_independent_support(self):
        self.run["photos"][0]["preparedSHA256"] = "same-content"
        self.run["finalMembershipAudit"]["rows"][0]["preparedSHA256"] = "same-content"
        self.run["photos"][-1]["preparedSHA256"] = "same-content"
        self.run["finalMembershipAudit"]["rows"][-1]["preparedSHA256"] = "same-content"
        result = self.evaluate()
        candidate = self.row(result, self.query_id)["evidence"]["topCandidates"][0]
        self.assertNotIn(self.target_ids[0], candidate["supportingReferencePhotoIds"])
        self.assertNotIn(self.target_ids[0], candidate["referencePhotoIds"])
        self.assertNotIn(self.query_id, candidate["supportingReferencePhotoIds"])
        self.assertEqual(candidate["support"], len(candidate["supportingReferencePhotoIds"]))

    def test_equal_sha_copy_is_removed_from_every_rival_centroid_before_ranking(self):
        self.settings["categoryPolicies"]["Models"]["photoRouteMinimum"] = .3
        self.run["photos"] = []
        self.run["finalMembershipAudit"]["rows"] = []
        self.vectors = {}
        query = self.add_photo(
            "query-shared", "Models/Source", unit([1., 0., 0.]), sha="shared-query",
        )
        a = [
            self.add_photo("a-shared", "Models/TargetA", unit([1., 0., 0.]), sha="shared-query"),
            self.add_photo("a-y", "Models/TargetA", unit([0., 1., 0.])),
            self.add_photo("a-z", "Models/TargetA", unit([0., 0., 1.])),
        ]
        b = [
            self.add_photo("b-plus", "Models/TargetB", unit([.4, .8, math.sqrt(.2)])),
            self.add_photo("b-minus", "Models/TargetB", unit([.4, .2, math.sqrt(.8)])),
        ]
        source_refs = [
            self.add_photo("s-y", "Models/Source", unit([0., 1., 0.])),
            self.add_photo("s-z", "Models/Source", unit([0., 0., 1.])),
        ]
        packet = copy.deepcopy(self.empty_packet)
        answers = copy.deepcopy(self.empty_answers)
        packet["characters"] = [
            {"folder": "Models/TargetA", "cards": [{"photoId": pid} for pid in a]},
            {"folder": "Models/TargetB", "cards": [{"photoId": pid} for pid in b]},
        ]
        answers["characters"] = [
            {"folder": "Models/TargetA", "decisions": [
                {"photoId": pid, "choice": "reference"} for pid in a
            ]},
            {"folder": "Models/TargetB", "decisions": [
                {"photoId": pid, "choice": "reference"} for pid in b
            ]},
        ]
        result = self.evaluate(packet=packet, answers=answers)
        row = self.row(result, query)
        candidates = {
            candidate["folder"]: candidate
            for candidate in row["evidence"]["topCandidates"]
        }
        # Without content exclusion, A's copied query reference would win:
        # Q·normalize(Q + Y + Z) > Q·normalize(B+ + B-).
        unfiltered_a = float(
            self.vectors[query] @ unit(
                self.vectors[a[0]] + self.vectors[a[1]] + self.vectors[a[2]],
            )
        )
        self.assertGreater(unfiltered_a, .4)
        self.assertEqual(row["candidateFolder"], "Models/TargetB")
        self.assertNotIn(a[0], candidates["Models/TargetA"]["referencePhotoIds"])
        self.assertEqual(candidates["Models/TargetA"]["score"], 0.0)
        expected_b = float(
            self.vectors[query] @ unit(self.vectors[b[0]] + self.vectors[b[1]])
        )
        self.assertAlmostEqual(candidates["Models/TargetB"]["score"], expected_b, places=6)
        self.assertNotIn(query, candidates["Models/TargetA"]["referencePhotoIds"])
        self.assertEqual(source_refs, ["s-y", "s-z"])
        self.run["photos"].reverse()
        self.run["finalMembershipAudit"]["rows"].reverse()
        self.assertEqual(result, self.evaluate(packet=packet, answers=answers))

    def test_diagnostic_exclusion_removes_ids_and_equal_hashes_but_keeps_queries(self):
        twin = self.target_ids[1]
        self.run["photos"][0]["preparedSHA256"] = "held-hash"
        self.run["finalMembershipAudit"]["rows"][0]["preparedSHA256"] = "held-hash"
        self.run["photos"][1]["preparedSHA256"] = "held-hash"
        self.run["finalMembershipAudit"]["rows"][1]["preparedSHA256"] = "held-hash"
        result = self.evaluate(excluded_reference_ids={self.target_ids[0]})
        target = next(item for item in result["identities"] if item["folder"] == "Models/Target")
        self.assertNotIn(self.target_ids[0], target["referencePhotoIds"])
        self.assertNotIn(twin, target["referencePhotoIds"])
        self.assertIn(self.target_ids[0], {row["photoId"] for row in result["rows"]})
        self.assertEqual(result["summary"]["excludedReferenceIdCount"], 1)
        self.assertEqual(result["summary"]["excludedReferencePhotoCount"], 2)

    def test_query_local_exclusion_never_becomes_a_diagnostic_exclusion(self):
        result = self.evaluate()
        for field in (
            "excludedReferenceIdCount", "excludedReferenceContentHashCount",
            "excludedReferencePhotoCount",
        ):
            self.assertEqual(result["summary"][field], 0)
        self.assertTrue(all(
            "diagnostic-reference-exclusion" not in row["blockers"]
            and "equal-content-diagnostic-exclusion" not in row["blockers"]
            for row in result["rows"]
        ))

    def test_diagnostic_exclusions_survive_all_query_local_centroid_exclusions(self):
        excluded = {self.target_ids[0], self.target_ids[1]}
        result = self.evaluate(excluded_reference_ids=excluded)
        self.assertEqual(result["summary"]["excludedReferenceIdCount"], 2)
        self.assertEqual(result["summary"]["excludedReferenceContentHashCount"], 2)
        self.assertEqual(result["summary"]["excludedReferencePhotoCount"], 2)
        self.assertEqual({
            row["photoId"] for row in result["rows"]
            if "diagnostic-reference-exclusion" in row["blockers"]
        }, excluded)
        self.assertTrue(all(
            row["evidence"]["topCandidates"]
            for row in result["rows"] if row["photoId"] in excluded
        ))
        self.run["photos"].reverse()
        self.run["finalMembershipAudit"]["rows"].reverse()
        self.assertEqual(result, self.evaluate(excluded_reference_ids=excluded))

    def test_unknown_diagnostic_exclusion_refuses(self):
        with self.assertRaisesRegex(ValueError, "unknown excluded reference"):
            self.evaluate(excluded_reference_ids={"not-a-photo"})

    def test_insufficient_reference_support_keeps_identity_and_appearance(self):
        self.settings["protection"]["automatic"]["minimumIndependentReferences"] = 4
        self.run["photos"] = [
            photo for photo in self.run["photos"] if photo["photoId"] != self.target_ids[1]
        ]
        self.run["finalMembershipAudit"]["rows"] = [
            row for row in self.run["finalMembershipAudit"]["rows"]
            if row["photoId"] != self.target_ids[1]
        ]
        self.vectors.pop(self.target_ids[1])
        result = self.evaluate()
        target = next(item for item in result["identities"] if item["folder"] == "Models/Target")
        self.assertEqual(target["referenceStatus"], "reference-needed")
        self.assertEqual(target["referenceNeeded"], 1)
        self.assertTrue(target["appearanceGroupIds"])
        self.assertIn("Models/Target", {item["folder"] for item in result["identities"]})

    def test_safeguards_are_visible_and_never_turned_into_locks(self):
        saved = next(
            row for row in self.run["finalMembershipAudit"]["rows"]
            if row["photoId"] == self.query_id
        )
        saved.update(protected=True, workflowSelected=True)
        result = self.evaluate()
        row = self.row(result, self.query_id)
        self.assertEqual(row["candidateFolder"], "Models/Target")
        self.assertIn("protected", row["blockers"])
        self.assertIn("workflowSelected", row["blockers"])
        self.assertEqual(row["execution"], "not-authorized")
        self.assertTrue(row["reconsiderable"])
        self.assertFalse(any("locked" in item for item in result["rows"]))

    def test_manual_opt_out_blocks_admission_and_auto_protection_is_only_context(self):
        target = next(
            row for row in self.run["finalMembershipAudit"]["rows"]
            if row["photoId"] == self.target_ids[0]
        )
        target["manualOptOut"] = True
        query = next(
            row for row in self.run["finalMembershipAudit"]["rows"]
            if row["photoId"] == self.query_id
        )
        query["automaticProtection"] = {
            "active": True, "recipeVersion": "independent-gallery-loo-v1",
        }
        opted_out_id = self.add_photo(
            "opted-out", "Models/Source", self.vectors[self.query_id], core=False,
        )
        opted_out = next(
            row for row in self.run["finalMembershipAudit"]["rows"]
            if row["photoId"] == opted_out_id
        )
        opted_out["manualOptOut"] = True
        result = self.evaluate()
        target_identity = next(
            item for item in result["identities"] if item["folder"] == "Models/Target"
        )
        row = self.row(result, self.query_id)
        target_row = self.row(result, self.target_ids[0])
        self.assertNotIn(self.target_ids[0], target_identity["referencePhotoIds"])
        self.assertEqual(row["candidateFolder"], "Models/Target")
        self.assertEqual(row["state"], "tentative")
        self.assertEqual(
            row["evidence"]["automaticProtection"]["recipeVersion"],
            "independent-gallery-loo-v1",
        )
        self.assertIn("manualOptOut", target_row["blockers"])
        self.assertFalse(target_row["referenceEligible"])
        opted_out_row = self.row(result, opted_out_id)
        self.assertIsNone(opted_out_row["candidateFolder"])
        self.assertIn("manualOptOut", opted_out_row["blockers"])

    def test_stale_ambiguous_and_rejected_members_cannot_seed_or_route(self):
        marked = {
            self.target_ids[0]: {"metadataStale": True},
            self.target_ids[1]: {"ambiguousPhotoId": True},
            self.query_id: {"rejectionHistory": True},
        }
        for saved in self.run["finalMembershipAudit"]["rows"]:
            saved.update(marked.get(saved["photoId"], {}))
        result = self.evaluate()
        target = next(item for item in result["identities"] if item["folder"] == "Models/Target")
        for photo_id in self.target_ids[:2]:
            self.assertNotIn(photo_id, target["referencePhotoIds"])
            self.assertFalse(self.row(result, photo_id)["referenceEligible"])
        rejected = self.row(result, self.query_id)
        self.assertIsNone(rejected["candidateFolder"])
        self.assertIn("rejectionHistory", rejected["blockers"])
        self.assertEqual(rejected["state"], "unresolved")

    def test_cast_ownership_and_artists_are_separate(self):
        artist = self.add_photo(
            "artist", "Artists/One", unit([1., 0., 0., 0., 0., 0., 0., 0.]),
            category="Artists",
        )
        self.settings["categoryPolicies"]["Angels"]["minimumUsablePhotosForOutlierActions"] = 2
        self.settings["categoryPolicies"]["Angels"]["photoRouteMinimum"] = .5
        angel_ids = []
        for index, angle in enumerate((0., math.pi / 2, math.pi)):
            angel_ids.append(self.add_photo(
                f"angel-{index}", "Angels/Alpha",
                unit([1., .2 * math.cos(angle), .2 * math.sin(angle), 0.,
                      0., 0., 0., 0.]),
                category="Angels",
            ))
        self.settings["categoryPolicies"]["Sisters"]["minimumUsablePhotosForOutlierActions"] = 2
        sisters_id = self.add_photo(
            "sister", "Sisters/Beta", self.vectors[self.query_id], category="Sisters",
        )
        packet = copy.deepcopy(self.empty_packet)
        answers = copy.deepcopy(self.empty_answers)
        packet["characters"] = [{
            "folder": "Angels/Alpha", "cards": [{"photoId": sisters_id}],
        }]
        answers["characters"] = [{
            "folder": "Angels/Alpha",
            "decisions": [{"photoId": sisters_id, "choice": "reference"}],
        }]
        result = self.evaluate(packet=packet, answers=answers)
        artist_row = self.row(result, artist)
        self.assertNotIn("Models/Target", [
            item["folder"] for item in artist_row["evidence"]["topCandidates"]
        ])
        sister_row = self.row(result, sisters_id)
        self.assertIn("cross-character-ownership-conflict", sister_row["blockers"])
        sister_identity = next(
            item for item in result["identities"] if item["folder"] == "Sisters/Beta"
        )
        self.assertNotIn(sisters_id, sister_identity["referencePhotoIds"])
        self.assertTrue(all(
            not (
                {ident["identityId"] for ident in result["identities"]
                 if ident["folder"].startswith("Artists/")}
                & set(association["identityIds"])
                & {ident["identityId"] for ident in result["identities"]
                   if not ident["folder"].startswith("Artists/")}
            )
            for association in result["associations"]
        ))

    def test_face_view_groups_are_complete_link_hypotheses_not_person_merges(self):
        self.settings["identityActions"]["identityClusterMinimumSimilarity"] = .6
        self.run["photos"] = []
        self.run["finalMembershipAudit"]["rows"] = []
        self.vectors = {}
        for photo_id, vector in (
            ("view-a", [1., 0.]), ("view-b", [1., 1.]), ("view-c", [0., 1.]),
        ):
            self.add_photo(photo_id, "Models/Views", unit(vector))
        result = self.evaluate()
        identity = next(item for item in result["identities"] if item["folder"] == "Models/Views")
        groups = [item for item in result["appearances"] if item["identityId"] == identity["identityId"]]
        self.assertEqual(len(groups), 2)
        self.assertTrue(all(group["evidenceKind"] == "face-view hypothesis" for group in groups))
        self.assertEqual(len(result["identities"]), 1)
        self.assertFalse(any(
            item["kind"] != "lookalike" or item["role"] is not None
            for item in result["associations"]
        ))

    def test_lookalike_links_require_shared_diversity_and_margin_gates(self):
        self.run["photos"] = []
        self.run["finalMembershipAudit"]["rows"] = []
        self.vectors = {}
        self.settings["protection"]["automatic"]["minimumIndependentReferences"] = 4
        self.settings["categoryPolicies"]["Models"]["minimumUsablePhotosForOutlierActions"] = 5
        for folder, offset in (("Models/Lookalike-A", 0.), ("Models/Lookalike-B", math.pi / 3)):
            for index, angle in enumerate((0., 2 * math.pi / 5, 4 * math.pi / 5,
                                           6 * math.pi / 5, 8 * math.pi / 5)):
                self.add_photo(
                    f"{folder[-1]}-{index}", folder,
                    unit([
                        math.cos(offset), math.sin(offset),
                        .3 * math.cos(angle), .3 * math.sin(angle),
                        .2 * math.cos(2 * angle), .2 * math.sin(2 * angle),
                        0., 0.,
                    ]),
                )
        result = self.evaluate()
        self.assertEqual(len(result["associations"]), 1)
        association = result["associations"][0]
        self.assertEqual(association["kind"], "lookalike")
        self.assertIsNone(association["role"])
        self.assertEqual(association["relationshipState"], "unassigned")
        self.assertIn("authored fictional roles only", association["provenance"])

    def test_repeated_reversed_input_is_stable_and_finite_json(self):
        first = self.evaluate()
        second = self.evaluate()
        self.assertEqual(first, second)
        self.run["photos"].reverse()
        self.run["finalMembershipAudit"]["rows"].reverse()
        reverse = self.evaluate()
        self.assertEqual(first, reverse)
        json.dumps(reverse, allow_nan=False)

    def test_parent_candidate_contract_and_no_overlapping_appearance_groups(self):
        result = self.evaluate()
        identity_folders = {item["folder"] for item in result["identities"]}
        self.assertEqual(result["schemaVersion"], 1)
        self.assertEqual(result["kind"], "bounded-realignment-candidates")
        for row in result["rows"]:
            self.assertIn(row["currentFolder"], identity_folders)
            if row["candidateFolder"] is not None:
                self.assertIn(row["candidateFolder"], identity_folders)
            self.assertIn(row["origin"], {
                "explicit-intent", "automatic-hypothesis", "baseline",
            })
            self.assertTrue(row["reconsiderable"])
            self.assertEqual(row["execution"], "not-authorized")
            for candidate in row["evidence"]["topCandidates"]:
                self.assertIn("referencePhotoIds", candidate)
                self.assertIn("support", candidate)
        membership = [
            photo_id for group in result["appearances"] for photo_id in group["photoIds"]
        ]
        self.assertEqual(len(membership), len(set(membership)))
        for association in result["associations"]:
            self.assertEqual(association["kind"], "lookalike")
            self.assertIsNone(association["role"])
            self.assertEqual(len(association["identityIds"]), 2)

    def test_receipt_content_quality_and_missing_vector_failures_are_explicit(self):
        self.run["finalMembershipAudit"]["rows"][0]["preparedSHA256"] = "other-hash"
        with self.assertRaisesRegex(ValueError, "content binding differs"):
            self.evaluate()
        self.setUp()
        self.run["photos"][0].pop("preparedSHA256")
        self.run["finalMembershipAudit"]["rows"][0].pop("preparedSHA256")
        with self.assertRaisesRegex(ValueError, "missing content hash"):
            self.evaluate()
        self.setUp()
        self.vectors.pop(self.query_id)
        with self.assertRaisesRegex(ValueError, "missing eligible saved vector"):
            self.evaluate()
        self.setUp()
        saved = next(
            row for row in self.run["finalMembershipAudit"]["rows"]
            if row["photoId"] == self.query_id
        )
        saved["qualityEligible"] = False
        result = self.evaluate()
        row = self.row(result, self.query_id)
        self.assertEqual(row["state"], "unresolved")
        self.assertIn("quality-ineligible", row["blockers"])
        self.assertIsNone(row["candidateFolder"])


if __name__ == "__main__":
    unittest.main()
