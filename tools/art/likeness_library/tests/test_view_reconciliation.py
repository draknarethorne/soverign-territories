import collections
import copy
import types
import unittest

from tools.art.likeness_library import entrance_trial, view_reconciliation
from tools.art.likeness_library.tests import test_membership_reassessment as fixtures


class ViewReconciliationTests(unittest.TestCase):
    def fake(self, links):
        views = [
            {"appearanceId": name, "personId": "person-"+name, "folder": "Models/"+name,
             "category": "Models", "pooled": False, "original": [name+"0", name+"1"],
             "explicitIntent": False} for name in "ABC"
        ]
        def support(pid, refs, floor):
            return refs if frozenset((pid[0], refs[0][0])) in links else []
        return types.SimpleNamespace(
            views=views, negatives=collections.defaultdict(set), support=support,
            qualify=lambda view, refs, recipe: (refs, True), scores=lambda inventory: inventory,
            source={name+"0": {"oldPersonId": "person-"+name} for name in "ABC"},
        )

    def test_complete_link_prevents_bridge_union(self):
        e = self.fake({frozenset("AB"), frozenset("BC")})
        _, report = view_reconciliation.build(e, entrance_trial.recipes()[1])
        self.assertEqual(len(report["qualifyingEdges"]), 2)
        self.assertEqual(len(report["unions"]), 1)
        self.assertEqual(len(report["unions"][0]["originalPersonIds"]), 2)

    def test_every_reference_requires_opposite_support(self):
        e = self.fake({frozenset("AB")})
        support = e.support
        e.support = lambda pid, refs, floor: [] if pid == "A1" else support(pid, refs, floor)
        _, report = view_reconciliation.build(e, entrance_trial.recipes()[1])
        self.assertEqual(report["unions"], [])

    def test_negative_or_uncertain_pairs_prevent_union(self):
        e = self.fake({frozenset("AB")})
        e.negatives["A0"].add("B0")
        _, report = view_reconciliation.build(e, entrance_trial.recipes()[1])
        self.assertEqual(report["unions"], [])

    def test_separate_character_slots_do_not_merge(self):
        e = self.fake({frozenset("AB")})
        for view in e.views[:2]:
            view.update(folder="Sisters/"+view["appearanceId"], category="Sisters")
        _, report = view_reconciliation.build(e, entrance_trial.recipes()[1])
        self.assertEqual(report["unions"], [])

    def test_existing_character_name_preserved_and_no_new_family_facts(self):
        e = self.fake({frozenset("AB")})
        e.views[0].update(folder="Angels/Chosen Name", category="Angels")
        original = copy.deepcopy(e.views)
        candidate, report = view_reconciliation.build(e, entrance_trial.recipes()[1])
        self.assertEqual(report["unions"][0]["provisionalDisplayOwner"], "Angels/Chosen Name")
        self.assertEqual(report["newNames"], 0)
        self.assertEqual(report["fictionalRelationshipAssignments"], 0)
        self.assertEqual(e.views, original)
        self.assertGreater(len(candidate.views), len(e.views))

    def test_union_can_qualify_sparse_views_without_relaxing_per_photo_admission(self):
        fixture = fixtures.MembershipReassessmentTests()
        fixture.setUp()
        state = fixture.build()
        e = entrance_trial.Evidence(state, fixture.run, fixture.vectors, fixture.ledger)
        template = next(v for v in e.views if v["folder"] == "Models/A")
        e.views = [
            {**template, "appearanceId": "a", "personId": "old-a", "original": ["p0", "p1", "p2"]},
            {**template, "appearanceId": "b", "personId": "old-b", "folder": "Models/B",
             "original": ["p3", "p4", "p5"]},
        ]
        for pid, row in e.source.items():
            row["oldPersonId"] = "old-a" if pid in ("p0", "p1", "p2") else "old-b"
        candidate, report = view_reconciliation.build(e, entrance_trial.recipes()[1])
        self.assertEqual(len(report["unions"]), 1)
        merged = next(v for v in candidate.views if v["appearanceId"].startswith("reconciled-art-view:"))
        refs, stable = candidate.qualify(merged, merged["original"], entrance_trial.recipes()[1])
        self.assertTrue(stable)
        self.assertEqual(len(refs), 6)
        self.assertEqual(report["positivePairLabelsUsed"], 0)
        self.assertTrue(candidate.own_people["p0"] & candidate.own_people["p5"])
        self.assertIn("old-a", candidate.own_people["p0"])
        result = entrance_trial.run_variant(candidate, entrance_trial.recipes()[1])
        selected = [r for r in result["rows"] if r["photoId"].startswith("p")]
        self.assertEqual(len(selected), 6)
        self.assertTrue(all(r["proposalPersonId"] for r in selected))
        self.assertEqual(len({r["proposalPersonId"] for r in selected}), 1)
        outsider = next(r for r in result["rows"] if r["photoId"] == "outlier")
        self.assertIsNone(outsider["proposalPersonId"])
        self.assertEqual(result["summary"]["installedMoves"], 0)

    def test_unrelated_views_of_old_person_do_not_lose_competitor_status(self):
        e = self.fake({frozenset("AB")})
        unrelated = {**copy.deepcopy(e.views[2]), "appearanceId": "Z", "personId": "person-A"}
        e.views.append(unrelated)
        candidate, report = view_reconciliation.build(e, entrance_trial.recipes()[1])
        self.assertTrue(report["unions"])
        retained = next(v for v in candidate.views if v["appearanceId"] == "Z")
        self.assertEqual(retained["personId"], "person-A")


if __name__ == "__main__":
    unittest.main()
