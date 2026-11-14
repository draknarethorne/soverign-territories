"""Own-core evidence must decide membership separately from placement and reference use."""
import copy
import unittest

import numpy as np

from tools.art.likeness_library import reformation, reformation_report
from tools.art.likeness_library.tests import test_reformation as fixtures


class MembershipReassessmentTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.ReformationTests()
        fixture.setUp()
        self.run, self.candidate, self.vectors, self.ledger = (
            fixture.run, fixture.candidate, fixture.vectors, fixture.ledger,
        )
        # A sufficient five-photo own core; p5 is a supported non-core view.
        for i in range(6):
            pid = f"p{i}"
            self.run["photos"][i]["destination"] = f"Models/A/gallery/{pid}.jpg"
            self.run["finalMembershipAudit"]["rows"][i]["destination"] = f"Models/A/gallery/{pid}.jpg"
            self.candidate["rows"][i]["currentFolder"] = "Models/A"
        self.candidate["identities"][0]["referencePhotoIds"] = [f"p{i}" for i in range(5)]
        self.candidate["identities"][1]["referencePhotoIds"] = ["outlier"]

    def build(self):
        return reformation.build(
            self.candidate, self.run, self.vectors, self.ledger, assess_membership=True,
        )

    def row(self, state, pid):
        return next(r for r in state["rows"] if r["photoId"] == pid)

    def add_group(self, count=6, *, folder="Models/B", start=0, protected=False):
        for i in range(count):
            pid = f"x{start+i}"
            vector = np.zeros(20)
            vector[9], vector[10 + i] = .8, .6
            self.vectors[pid] = vector
            photo = {"photoId": pid, "preparedSHA256": "hash-" + pid,
                     "destination": f"{folder}/gallery/{pid}.jpg"}
            self.run["photos"].append(photo)
            self.run["finalMembershipAudit"]["rows"].append({
                **self.run["finalMembershipAudit"]["rows"][0], **photo, "protected": protected,
            })
            self.candidate["rows"].append({"photoId": pid, "currentFolder": folder})
        for pid in list(self.vectors):
            self.vectors[pid] = np.pad(self.vectors[pid], (0, 20-len(self.vectors[pid])))

    def test_supported_noncore_member_is_not_evicted_or_promoted_into_reference(self):
        state = self.build()
        row = self.row(state, "p5")
        self.assertEqual(row["disposition"], "current-membership-supported")
        self.assertEqual(row["membershipAssessment"]["status"], "supported")
        self.assertFalse(row["referenceEligible"])
        self.assertFalse(row["releasedFromSupportedMembership"])
        own = row["membershipAssessment"]["own"]
        self.assertGreaterEqual(len(own["supportPhotoIds"]), 4)
        self.assertGreater(own["activeScore"], own["routeMinimum"])

    def test_bad_member_is_released_and_reassignment_uses_full_competitors(self):
        self.add_group()
        # Put a foreign photo in A, but B has independently qualified references.
        self.vectors["p5"] = self.vectors["x0"].copy()
        self.candidate["identities"][1]["referencePhotoIds"] = [f"x{i}" for i in range(6)]
        state = self.build()
        row = self.row(state, "p5")
        self.assertEqual(row["membershipAssessment"]["status"], "questionable")
        self.assertTrue(row["releasedFromSupportedMembership"])
        self.assertEqual(row["disposition"], "reassignment-proposed")
        self.assertEqual(row["proposedPersonId"], self.row(state, "x1")["proposedPersonId"])
        self.assertEqual(row["installedDestination"], "Models/A/gallery/p5.jpg")
        self.assertFalse(row["referenceEligible"])

    def test_released_photos_form_a_supported_group_across_old_folders(self):
        self.add_group()
        self.candidate["identities"][1]["referencePhotoIds"] = ["outlier"]
        for i in range(3):
            pid = f"x{i}"
            self.candidate["rows"][7+i]["currentFolder"] = "Models/A"
            self.run["photos"][7+i]["destination"] = f"Models/A/gallery/{pid}.jpg"
            self.run["finalMembershipAudit"]["rows"][7+i]["destination"] = f"Models/A/gallery/{pid}.jpg"
        state = self.build()
        selected = [self.row(state, f"x{i}") for i in range(6)]
        self.assertTrue(all(r["inReassessmentPool"] for r in selected))
        self.assertTrue(all(r["disposition"] == "pooled-group-proposed" for r in selected))
        self.assertEqual(len({r["proposedPersonId"] for r in selected}), 1)
        person = next(p for p in state["people"] if p["personId"] == selected[0]["proposedPersonId"])
        self.assertIsNone(person["canonicalOwner"])
        self.assertEqual(len(person["lineage"]), 2)
        views = [v for v in state["appearances"] if v["personId"] == person["personId"]]
        self.assertEqual(len(views[0]["nextBoundaryReferencePhotoIds"]), 6)

    def test_singleton_is_provisional_not_a_named_potential(self):
        state = self.build()
        row = self.row(state, "outlier")
        self.assertIsNone(row["proposedPersonId"])
        group = next(g for g in state["reassessmentGroups"] if "outlier" in g["photoIds"])
        self.assertIsNone(group["personId"])
        self.assertEqual(state["summary"]["newNamedIdentities"], 0)

    def test_lock_does_not_certify_wrong_membership_or_keep_reference_influence(self):
        self.add_group(protected=True)
        self.vectors["p5"] = self.vectors["x0"].copy()
        self.run["finalMembershipAudit"]["rows"][5]["protected"] = True
        state = self.build()
        row = self.row(state, "p5")
        self.assertEqual(row["membershipAssessment"]["status"], "questionable")
        self.assertEqual(row["disposition"], "change-blocked")
        self.assertIn("protected", row["placementBlocks"])
        self.assertIsNone(row["proposedPersonId"])
        self.assertFalse(row["referenceEligible"])
        self.assertFalse(row["releasedFromSupportedMembership"])
        self.assertTrue(row["currentMembershipQuestionable"])

    def test_starved_references_not_a_definite_identity_rejection(self):
        self.candidate["identities"][0]["referencePhotoIds"] = ["p0"]
        row = self.row(self.build(), "p5")
        self.assertEqual(row["membershipAssessment"]["status"], "reference-needed")
        self.assertFalse(row["releasedFromSupportedMembership"])
        self.assertTrue(row["inReassessmentPool"])

    def test_own_core_is_leave_one_out_and_equal_content_is_not_support(self):
        row = self.row(self.build(), "p0")
        self.assertNotIn("p0", row["membershipAssessment"]["own"]["referencePhotoIds"])
        self.run["photos"][1]["preparedSHA256"] = self.run["photos"][0]["preparedSHA256"]
        row = self.row(self.build(), "p0")
        if row["membershipAssessment"]["own"]:
            self.assertNotIn("p1", row["membershipAssessment"]["own"]["referencePhotoIds"])
        self.assertNotEqual(row["membershipAssessment"]["status"], "supported")

    def test_category_specific_admission_floors_are_used(self):
        state = self.build()
        self.assertEqual(self.row(state, "p5")["membershipAssessment"]["own"]["routeMinimum"], .5)
        for photo, saved, row in zip(self.run["photos"], self.run["finalMembershipAudit"]["rows"], self.candidate["rows"]):
            photo["destination"] = photo["destination"].replace("Models/A", "Prospects/A")
            saved["destination"] = photo["destination"]
            row["currentFolder"] = row["currentFolder"].replace("Models/A", "Prospects/A")
        self.candidate["identities"][0]["folder"] = "Prospects/A"
        row = self.row(self.build(), "p5")
        self.assertEqual(row["membershipAssessment"]["own"]["routeMinimum"], .4)

    def test_conservation_order_and_positive_labels_cannot_create_destinations(self):
        before = copy.deepcopy((self.run, self.candidate, self.ledger))
        state = self.build()
        members = [pid for p in state["people"] + state["retainedPeople"] for pid in p["memberPhotoIds"]]
        self.assertEqual(sorted(members), sorted(self.vectors))
        self.assertEqual(before, (self.run, self.candidate, self.ledger))
        self.run["photos"].reverse()
        self.run["finalMembershipAudit"]["rows"].reverse()
        self.candidate["rows"].reverse()
        self.candidate["identities"].reverse()
        self.ledger["pairs"] = [{"photoIds": ["p0", "p5"], "label": "same"}]
        self.assertEqual(state, self.build())

    def test_viewer_explains_own_assessment_and_pool_not_retained_correctness(self):
        state = self.build()
        people = {p["personId"]: p for p in state["people"]}
        text = reformation_report.presentation(self.row(state, "p5"), people)
        self.assertEqual(text["actionLabel"], "CURRENT MEMBERSHIP SUPPORTED")
        self.assertIn("Own score", text["assessmentText"])
        text = reformation_report.presentation(self.row(state, "outlier"), people)
        self.assertIn("POOL", text["actionLabel"])

    def test_direct_uncertainty_veto_is_not_overridden_by_high_similarity(self):
        self.ledger["pairs"] = [{"photoIds": ["p0", "p5"], "label": "uncertain"}]
        state = self.build()
        row = self.row(state, "p5")
        self.assertIsNone(row["proposedPersonId"])
        self.assertIn("direct-different-or-uncertain-veto", row["membershipAssessment"]["own"]["blockers"])
        self.assertEqual(self.row(state, "p0")["disposition"], "current-membership-supported")

    def test_invalid_frozen_references_cannot_silently_leave_supported_dependents(self):
        self.add_group()
        self.candidate["identities"][1]["referencePhotoIds"] = [f"x{i}" for i in range(6)]
        # A foreign reference attributed to A must not contaminate its members.
        self.candidate["identities"][0]["referencePhotoIds"].append("x0")
        self.vectors["p5"] = self.vectors["x1"].copy()
        state = self.build()
        invalid = set(state["pendingReferenceWithdrawals"])
        for row in state["rows"]:
            if row["origin"] == "automatic":
                self.assertNotIn(row["appearanceId"], invalid)
        for view in state["appearances"]:
            if view["appearanceId"] in invalid:
                self.assertFalse(view["nextBoundaryReferencePhotoIds"])
        # Independently qualified views of A remain available; the alien view
        # cannot turn the rest of the folder into B.
        self.assertEqual(self.row(state, "p1")["disposition"], "current-membership-supported")

    def test_shared_reference_inventory_does_not_alias_two_person_views(self):
        self.candidate["identities"].append({
            "folder": "Models/C", "referencePhotoIds": [f"p{i}" for i in range(5)],
        })
        state = self.build()
        views = [v for v in state["appearances"] if v["folder"] in ("Models/A", "Models/C")]
        self.assertEqual(len({v["appearanceId"] for v in views}), len(views))
        row = self.row(state, "p5")
        self.assertEqual(row["membershipAssessment"]["status"], "ambiguous")
        self.assertIsNone(row["proposedPersonId"])


if __name__ == "__main__":
    unittest.main()
