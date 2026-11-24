"""Fixture-only tests for pre-formation fresh-baseline selection."""
import copy
import hashlib
import math
import pathlib
import unittest

import numpy as np

from tools.art.likeness_library import normal_admission
from tools.art.likeness_library.policy import load_policy
from tools.art.likeness_library.tests import test_reconciliation as fixtures


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def row(number, vector, *, owner="Sisters/Example", reference=False, **changes):
    result = {
        "photoId": f"photo:image_{number}",
        "owner": owner,
        "currentPath": f"{owner}/gallery/example_image_{number}.jpg",
        "sha256": digest(f"source:{number}"),
        "measurementSha256": digest(f"measurement:{number}") if vector is not None else None,
        "vector": vector,
        "qualityEligible": vector is not None,
        "referenceEligible": reference,
        "identityAnchor": False,
        "identityAmbiguous": False,
        "sourceAmbiguous": False,
        "rejectionMetadataStale": False,
        "ownerPersonIds": ["person_example"],
        "rejectedPersonIds": [],
        "sourceStatus": "eligible",
    }
    result.update(changes)
    return result


def angle(score):
    return [score, math.sqrt(1 - score * score)]


class FreshBaselineReleaseTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_policy()

    def assess(self, rows):
        return normal_admission.fresh_baseline_release_candidates(rows, self.policy)

    def test_exact_display_band_boundaries_and_no_review_floor_substitution(self):
        # Non-cast owner: Sisters/Angels top-count seeds are exempt from band release.
        ref = row(1, [1., 0.], owner="Models/Example", reference=True)
        rows = [ref] + [row(i, angle(s), owner="Models/Example") for i, s in
                        ((2, .149), (3, .15), (4, .299), (5, .30), (6, .349))]
        result = self.assess(rows)
        evidence = {item["photoId"]: item for item in result["assessment"]}
        self.assertEqual([evidence[f"photo:image_{i}"]["band"] for i in range(2, 7)],
                         ["red", "orange", "orange", "yellow", "yellow"])
        self.assertEqual({item["photoId"] for item in result["bindings"]},
                         {"photo:image_1", "photo:image_2", "photo:image_3", "photo:image_4"})
        self.assertIsNone(evidence["photo:image_1"]["score"])
        self.assertEqual(evidence["photo:image_2"]["comparisonReferences"][0]["photoId"], ref["photoId"])
        self.assertEqual(self.assess(list(reversed(rows))), result)
        self.assertTrue(result["planningOnly"])
        self.assertEqual(result["policyEvidence"]["castReviewMinimum"],
                         self.policy["castAdmission"]["reviewMinimum"])

    def test_custom_bands_are_used_without_rounding(self):
        self.policy["scoreBands"]["yellow"]["minimum"] = .4
        self.policy["scoreBands"]["orange"]["minimum"] = .2
        self.policy["scoreBands"]["red"]["maximumExclusive"] = .2
        result = self.assess([row(1, [1., 0.], owner="Models/Example", reference=True),
                              row(2, angle(.3), owner="Models/Example")])
        self.assertEqual(result["assessment"][1]["band"], "orange")
        self.assertTrue(result["assessment"][1]["selected"])

    def test_source_and_prepared_duplicates_never_self_score_or_vote_twice(self):
        first = row(1, [1., 0.], reference=True)
        same_source = row(2, [1., 0.], sha256=first["sha256"])
        same_measurement = row(3, [1., 0.], measurementSha256=first["measurementSha256"])
        result = self.assess([first, same_source, same_measurement])
        self.assertTrue(all(item["score"] is None for item in result["assessment"]))
        for duplicate in (same_source, same_measurement):
            duplicate["referenceEligible"] = True
            with self.assertRaisesRegex(ValueError, "multiple reference votes"):
                self.assess([first, duplicate])
            duplicate["referenceEligible"] = False

    def test_candidate_excluded_before_core_selection(self):
        rows = [row(1, [1., 0.], reference=True),
                row(2, [0., 1.], reference=True),
                row(3, [0., 1.], reference=True)]
        result = self.assess(rows)
        target = result["assessment"][0]
        self.assertEqual(target["score"], 0.)
        self.assertEqual([ref["photoId"] for ref in target["comparisonReferences"]],
                         ["photo:image_2", "photo:image_3"])

    def test_explicit_eligible_anchor_shapes_the_independent_core(self):
        rows = [row(1, [1., 0.]),
                row(2, [1., 0.], reference=True, identityAnchor=True),
                row(3, [0., 1.], reference=True),
                row(4, [0., 1.], reference=True)]
        target = self.assess(rows)["assessment"][0]
        self.assertEqual(target["comparisonCoreMode"], "trusted")
        self.assertEqual(target["score"], 1.)
        self.assertEqual([ref["photoId"] for ref in target["comparisonReferences"]], ["photo:image_2"])

    def test_unavailable_quality_rejections_and_ambiguity_are_visible(self):
        rows = [row(1, None),
                row(2, [1., 0.], qualityEligible=False),
                row(3, [1., 0.], rejectedPersonIds=["person_example"]),
                row(4, [1., 0.], rejectionMetadataStale=True, rejectedPersonIds=["old_person"]),
                row(5, [1., 0.], owner="Models/Ambiguous", identityAmbiguous=True),
                row(6, [1., 0.], sourceAmbiguous=True)]
        result = self.assess(rows)
        evidence = {item["photoId"]: item for item in result["assessment"]}
        self.assertTrue(all(item["score"] is None and item["selected"] for item in evidence.values()))
        self.assertEqual(evidence["photo:image_3"]["rejectedPersonIds"], ["person_example"])
        self.assertEqual(evidence["photo:image_4"]["rejectedPersonIds"], ["old_person"])
        self.assertEqual({item["photoId"] for item in result["blockedBindings"]},
                         {"photo:image_4", "photo:image_5", "photo:image_6"})
        self.assertEqual({item["photoId"] for item in result["bindings"]},
                         {"photo:image_1", "photo:image_2", "photo:image_3"})

    def test_named_identity_keeps_evidence_less_unscored_members_but_not_rejected_ones(self):
        owner = "Potentials/Fia"
        rows = [row(1, [1., 0.], owner=owner),
                row(2, None, owner=owner),
                row(3, [1., 0.], owner=owner, rejectedPersonIds=["person_example"]),
                row(4, angle(.1), owner=owner),
                row(5, [1., 0.], owner=owner, reference=True)]
        named = normal_admission.fresh_baseline_release_candidates(rows, self.policy, {owner})
        plain = self.assess(rows)
        evidence = {item["photoId"]: item for item in named["assessment"]}
        self.assertTrue(evidence["photo:image_2"]["namedRetained"])
        self.assertEqual({item["photoId"] for item in named["bindings"]}, {"photo:image_3", "photo:image_4"})
        self.assertEqual({item["photoId"] for item in plain["bindings"]},
                         {"photo:image_2", "photo:image_3", "photo:image_4", "photo:image_5"})
        orange = [row(6, angle(.2), owner=owner)]
        self.assertEqual({item["photoId"] for item in normal_admission.fresh_baseline_release_candidates(
            rows + orange, self.policy, {owner})["bindings"]}, {"photo:image_3", "photo:image_4"})
        self.assertIn("photo:image_6", {item["photoId"] for item in self.assess(rows + orange)["bindings"]})

    def test_invalid_inputs_fail_closed_and_input_remains_unchanged(self):
        original = [row(1, [1., 0.], reference=True), row(2, [0., 1.])]
        saved = copy.deepcopy(original)
        self.assess(original)
        self.assertEqual(original, saved)
        for key, value in (("qualityEligible", None), ("sourceStatus", ""),
                           ("sha256", "bad"), ("measurementSha256", None),
                           ("vector", [float("nan"), 0.])):
            broken = copy.deepcopy(original)
            broken[1][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.assess(broken)
        with self.assertRaisesRegex(ValueError, "ambiguous IDs or paths"):
            self.assess(original + [copy.deepcopy(original[0])])
        broken = copy.deepcopy(original)
        broken[0]["rejectedPersonIds"] = ["person_example"]
        with self.assertRaisesRegex(ValueError, "unsafe reference"):
            self.assess(broken)
        broken = copy.deepcopy(original)
        broken[0]["sourceStatus"] = "same-content-nonvoting"
        with self.assertRaisesRegex(ValueError, "unsafe reference"):
            self.assess(broken)
        broken = copy.deepcopy(original)
        broken[1]["vector"] = np.array([1., 0., 0.])
        with self.assertRaisesRegex(ValueError, "dimensions"):
            self.assess(broken)

    def test_unencoded_original_filename_blocks_retirement_binding(self):
        item = row(1, None, currentPath="Sisters/Example/gallery/original.jpg")
        result = self.assess([item])
        self.assertEqual(result["bindings"], [])
        self.assertEqual(result["blockedBindings"][0]["photoId"], item["photoId"])
        self.assertIn("standard filename", result["assessment"][0]["bindingBlockReasons"][0])

    def test_verified_standard_name_binds_descriptive_source(self):
        item = row(1, None, currentPath="Sisters/Example/gallery/original.jpg")
        standard = row(1, None)["currentPath"].rsplit("/", 1)[1]
        result = self.assess([{**item, "standardName": standard}])
        self.assertEqual(result["blockedBindings"], [])
        self.assertEqual(result["bindings"][0]["currentPath"], item["currentPath"])


class CastSeedSelectionTests(unittest.TestCase):
    """Item (i): Sisters/Angels keep a seed; other scored members are released."""

    SCORES = {5: .65, 8: .62, 6: .45, 3: .40, 4: .35, 7: .10}

    def setUp(self):
        self.policy = load_policy()

    def rows(self, owner):
        # Only the anchors vote, so every other member's own score is exact.
        anchors = [row(i, [1., 0.], owner=owner, reference=True, identityAnchor=True) for i in (1, 2)]
        return anchors + [row(i, angle(score), owner=owner) for i, score in self.SCORES.items()]

    def assess(self, rows, top, below):
        self.policy["castAdmission"].update(seedEnabled=True, seedTopCount=top, seedReleaseBelow=below)
        return normal_admission.fresh_baseline_release_candidates(rows, self.policy)

    @staticmethod
    def selected(result):
        return {item["photoId"].removeprefix("photo:image_") for item in result["bindings"]}

    def test_threshold_members_beyond_top_count_are_kept_and_others_released(self):
        result = self.assess(self.rows("Sisters/Example"), 2, .60)
        evidence = {item["photoId"].removeprefix("photo:image_"): item for item in result["assessment"]}
        self.assertEqual([evidence[i]["score"] for i in ("1", "2")], [1., 1.])
        self.assertEqual(self.selected(result), {"6", "3", "4", "7"})
        self.assertEqual(evidence["5"]["castSeed"], {"rank": 3, "seedMember": True, "basis": "threshold",
                                                     "exemptedSelectionReasons": []})
        self.assertFalse(evidence["8"]["selected"])
        self.assertEqual(evidence["6"]["selectionReasons"], ["cast-seed-release"])
        self.assertEqual(evidence["7"]["selectionReasons"], ["band:red"])
        seed = result["castSeed"]["identities"]["Sisters/Example"]
        self.assertEqual(len(seed["seedPhotoIds"]), 4)
        self.assertEqual(seed["seedBandExemptPhotoIds"], [])
        self.assertEqual(len(seed["seedReleasedPhotoIds"]), 3)
        self.assertEqual(seed["bandReleasedPhotoIds"], ["photo:image_7"])
        self.assertEqual((result["castSeed"]["seedKeptCount"], result["castSeed"]["seedReleaseCount"]), (4, 3))
        self.assertEqual(result["policyEvidence"]["castSeed"], {"enabled": True, "topCount": 2, "releaseBelow": .60})

    def test_top_count_keeps_low_scores_including_red_but_not_unscored(self):
        result = self.assess(self.rows("Angels/Example"), 5, .60)
        evidence = {item["photoId"].removeprefix("photo:image_"): item for item in result["assessment"]}
        # Rank 5 is a 0.45 yellow member: kept by the top count despite the threshold.
        self.assertEqual(evidence["6"]["castSeed"], {"rank": 5, "seedMember": True, "basis": "top-count",
                                                     "exemptedSelectionReasons": []})
        self.assertEqual(self.selected(result), {"3", "4", "7"})
        # A red member inside the top count is kept "no matter what its score is";
        # an unscored member cannot be ranked and stays released.
        rows = self.rows("Angels/Example") + [row(9, None, owner="Angels/Example")]
        small = self.assess(rows, 8, .60)
        evidence = {item["photoId"].removeprefix("photo:image_"): item for item in small["assessment"]}
        self.assertEqual(self.selected(small), {"9"})
        self.assertEqual(evidence["7"]["band"], "red")
        self.assertFalse(evidence["7"]["selected"])
        self.assertEqual(evidence["7"]["selectionReasons"], [])
        self.assertEqual(evidence["7"]["castSeed"], {"rank": 8, "seedMember": True, "basis": "top-count",
                                                     "exemptedSelectionReasons": ["band:red"]})
        self.assertEqual((evidence["9"]["castSeed"], evidence["9"]["selectionReasons"]), (None, ["unscored"]))
        seed = small["castSeed"]["identities"]["Angels/Example"]
        self.assertEqual(len(seed["seedPhotoIds"]), 8)
        self.assertEqual(seed["seedBandExemptPhotoIds"], ["photo:image_7"])
        self.assertEqual((seed["seedReleasedPhotoIds"], seed["bandReleasedPhotoIds"]), ([], []))
        self.assertEqual(seed["unscoredReleasedPhotoIds"], ["photo:image_9"])
        # The identity keeps min(N, scored members) seeds.
        self.assertEqual(len(self.assess(rows, 20, .99)["castSeed"]["identities"]["Angels/Example"]["seedPhotoIds"]), 8)

    def test_default_seed_and_non_cast_categories_are_unaffected(self):
        for owner in ("Models/Example", "Prospects/Example", "Potentials/Example"):
            with self.subTest(owner=owner):
                result = self.assess(self.rows(owner), 1, .99)
                self.assertEqual(self.selected(result), {"7"})
                self.assertTrue(all(item["castSeed"] is None for item in result["assessment"]))
                self.assertEqual(result["castSeed"]["identities"], {})
        self.policy = load_policy()
        result = normal_admission.fresh_baseline_release_candidates(self.rows("Sisters/Example"), self.policy)
        # Seeding is off by default: cast members use only red/orange/unscored release.
        self.assertIsNone(result["castSeed"])
        self.assertEqual(self.selected(result), {"7"})
        self.assertTrue(all(item["castSeed"] is None for item in result["assessment"]))
        rows = self.rows("Sisters/Example")
        self.assertEqual(self.assess(list(reversed(rows)), 2, .6), self.assess(rows, 2, .6))
        self.policy["castAdmission"]["seedTopCount"] = 0
        with self.assertRaisesRegex(ValueError, "seedTopCount"):
            normal_admission.fresh_baseline_release_candidates(rows, self.policy)


class NamedGalleryNonvotingTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.NormalAdmissionTests(methodName="runTest")
        self.fixture.setUp()
        self.candidate, self.canonical = self.fixture.nonvoting_fixture(folder="Potentials/Former", bucket="Gallery")
        self.candidate["measurementSha256"] = digest("prepared duplicate")
        self.report = self.fixture.empty_voting_report()

    def reconsider(self, candidate, **kwargs):
        f = self.fixture
        return f.admission.reconsider_nonvoting_holds(
            f.api, [candidate], f.cores, f.references, f.settings, f.policy,
            self.canonical, [], self.report, **kwargs,
        )["results"][0]

    def test_explicit_opt_in_scores_independently_without_votes(self):
        with self.assertRaisesRegex(ValueError, "Review or Various"):
            self.reconsider(self.candidate)
        result = self.reconsider(self.candidate, include_named_gallery=True)
        self.assertEqual(result["scoreStatus"], "available")
        self.assertEqual(result["decision"]["sourceFolder"], "Potentials/Former")
        self.assertEqual(result["decision"]["sourceBucket"], "Gallery")
        self.assertFalse(result["decision"]["referenceEligible"])
        self.assertTrue(result["decision"]["preserveStaged"])
        self.assertIsNone(result["decision"]["destination"])
        self.assertEqual(result["routingProposal"]["destination"], "Sisters/Drakness")
        self.assertEqual(self.report["clusters"], [])

    def test_descriptive_source_binds_through_verified_standard_name(self):
        standard = pathlib.PurePosixPath(self.candidate["source"]).name
        descriptive = {
            **self.candidate, "source": "Potentials/Former/gallery/former_pose_7.jpg", "standardName": standard,
        }
        result = self.reconsider(descriptive, include_named_gallery=True)
        self.assertEqual(result["scoreStatus"], "available")
        with self.assertRaisesRegex(ValueError, "Review or Various"):
            self.reconsider({**descriptive, "standardName": "former_pose_7.jpg"}, include_named_gallery=True)

    def test_protections_and_rejections_are_never_overridden(self):
        for change in (
            {"protected": True}, {"workflowSelected": True}, {"identityProtected": True},
            {"qualityEligible": False}, {"rejectionMetadataStale": True},
            {"rejectedPersonIds": ["Sisters/Drakness"]},
        ):
            with self.subTest(change=change):
                result = self.reconsider({**self.candidate, **change}, include_named_gallery=True)
                self.assertTrue(result["decision"]["preserveStaged"])
                self.assertFalse(result["decision"].get("destination"))
                self.assertFalse(result["decision"]["referenceEligible"])
                if change.get("qualityEligible") is False or change.get("rejectionMetadataStale"):
                    self.assertEqual(result["scoreStatus"], "unavailable")

    def test_unavailable_and_bad_bindings_remain_explicit(self):
        candidate = {**self.candidate, "vector": None, "qualityEligible": False}
        result = self.reconsider(candidate, include_named_gallery=True)
        self.assertEqual(result["scoreStatus"], "unavailable")
        self.assertEqual(result["comparisons"], [])
        self.assertTrue(result["decision"]["preserveStaged"])
        candidate["qualityEligible"] = True
        result = self.reconsider(candidate, include_named_gallery=True)
        self.assertEqual(result["scoreStatus"], "unavailable")
        self.assertTrue(result["decision"]["preserveStaged"])
        with self.assertRaisesRegex(ValueError, "measurement is not bound"):
            self.reconsider({**self.candidate, "measurementSha256": None}, include_named_gallery=True)
        with self.assertRaisesRegex(ValueError, "ambiguous or stale"):
            self.reconsider({**self.candidate, "sourceHash": "b" * 64}, include_named_gallery=True)
        with self.assertRaisesRegex(ValueError, "source owner or bucket differs"):
            self.reconsider({**self.candidate, "sourceFolder": "Potentials/Other"}, include_named_gallery=True)
        with self.assertRaisesRegex(ValueError, "must be explicit"):
            self.reconsider(self.candidate, include_named_gallery=1)


if __name__ == "__main__":
    unittest.main()
