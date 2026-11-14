"""Reference follow-through changes evidence only at a bounded frozen boundary."""
import copy
import unittest
from unittest import mock

from tools.art.likeness_library import membership_reassessment as subject, reformation


def boundary(refs, next_refs, *, stable):
    return {
        "appearances": [{"appearanceId": "view", "referencePhotoIds": refs,
                         "nextBoundaryReferencePhotoIds": next_refs}],
        "reassessmentGroups": [{"photoIds": ["p0", "p1"]}],
        "pendingReferenceWithdrawals": [] if stable else ["view"],
        "summary": {"stable": stable, "membershipDispositions": {"reference-needed": 2}},
        "recipe": {}, "limits": [], "passes": [],
    }


class ReferenceContinuationTests(unittest.TestCase):
    def build(self):
        return subject.build(*([None] * 13))

    def test_followup_uses_withdrawn_inventory_and_fixed_pool_then_stops(self):
        first = boundary(["p0", "p1"], ["p0"], stable=False)
        final = boundary(["p0"], ["p0"], stable=True)
        before = copy.deepcopy(first)
        with mock.patch.object(subject, "_build_boundary", side_effect=[first, final]) as run:
            result = self.build()
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.kwargs["reference_limits"], {"view": ["p0"]})
        self.assertEqual(run.call_args.kwargs["pool_inventory"], [["p0", "p1"]])
        self.assertEqual(result["summary"]["referenceBoundaryCount"], 2)
        self.assertEqual(result["summary"]["referenceWithdrawals"], 1)
        self.assertEqual(result["referenceBoundaries"][0]["withdrawals"], {"view": ["p1"]})
        self.assertEqual(first, before)

    def test_reference_growth_is_an_error_not_an_implicit_recovery(self):
        first = boundary(["p0", "p1"], ["p0"], stable=False)
        illegal = boundary(["p0", "p1"], ["p0", "p1"], stable=True)
        with mock.patch.object(subject, "_build_boundary", side_effect=[first, illegal]):
            with self.assertRaisesRegex(ValueError, "grew references"):
                self.build()

    def test_new_competitor_inventory_is_an_error(self):
        first = boundary(["p0", "p1"], ["p0"], stable=False)
        illegal = boundary(["p0"], ["p0"], stable=True)
        illegal["appearances"][0]["appearanceId"] = "new-view"
        with mock.patch.object(subject, "_build_boundary", side_effect=[first, illegal]):
            with self.assertRaisesRegex(ValueError, "changed frozen hypotheses"):
                self.build()

    def test_bounded_incomplete_not_reported_as_converged(self):
        incomplete = boundary(["p0"], ["p0"], stable=False)
        with mock.patch.object(reformation, "MAX_PASSES", 2), \
                mock.patch.object(subject, "_build_boundary", side_effect=lambda *a, **k: copy.deepcopy(incomplete)):
            result = self.build()
        self.assertFalse(result["summary"]["stable"])
        self.assertEqual(len(result["referenceBoundaries"]), 2)
        self.assertEqual(result["pendingReferenceWithdrawals"], ["view"])


if __name__ == "__main__":
    unittest.main()
