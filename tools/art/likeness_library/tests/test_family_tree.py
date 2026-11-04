"""Score-band family trees give lookalike identities one surname, rooted at the cast where possible."""
import copy
import unittest

import numpy as np

from tools.art import likeness
from tools.art.likeness_library import family_tree
from tools.art.likeness_library.policy import load_policy, validate_policy


def unit(*values):
    vector = np.asarray(values, dtype=float)
    return vector / np.linalg.norm(vector)


def blend(a, b, score):
    """A unit vector whose similarity to unit vector a is exactly score (b orthogonal to a)."""
    return score * a + np.sqrt(1 - score ** 2) * b


E = [unit(*(1. if i == j else 0. for i in range(6))) for j in range(6)]


class FamilyTreeTests(unittest.TestCase):
    def setUp(self):
        self.policy = copy.deepcopy(load_policy())
        self.policy["familyNaming"] = {"enabled": True, "linkMinimumBand": "yellow", "castSurnameOverrides": {}}

    def identity(self, name, vector, **extra):
        return {"name": name, "vector": vector, "photoCount": extra.pop("photoCount", 5), "ageDate": None,
                "retained": False, **extra}

    def test_cast_tier_link_uses_recorded_person_surname(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Vale"}}
        identities = {"Prospects/Fia Hadley": self.identity("Fia Hadley", blend(E[0], E[1], .45))}
        renames, evidence = family_tree.plan(identities, cast, self.policy)
        self.assertEqual(renames, {"Prospects/Fia Hadley": "Fia Vale"})
        family = evidence["families"][0]
        self.assertEqual((family["root"], family["surname"], family["surnameSource"]),
                         ("Angels/angelica", "Vale", "recorded person name"))
        self.assertEqual(family["members"][0]["band"], "yellow")

    def test_configured_override_wins_and_renames_cast_presentation(self):
        self.policy["familyNaming"]["castSurnameOverrides"] = {"Angels/Angelica": "Hadley"}
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Vale"}}
        identities = {
            "Prospects/Fia Hadley": self.identity("Fia Hadley", blend(E[0], E[1], .45)),
            "Prospects/Jacinta Alden": self.identity("Jacinta Alden", blend(E[0], E[2], .35)),
        }
        renames, evidence = family_tree.plan(identities, cast, self.policy)
        self.assertEqual(renames, {"Prospects/Jacinta Alden": "Jacinta Hadley"})
        self.assertEqual(evidence["cast"]["Angels/angelica"]["currentPersonName"], "Angelica Hadley")
        self.assertEqual(evidence["cast"]["Angels/angelica"]["surnameSource"], "configured")

    def test_below_band_cast_falls_back_to_peer_chain(self):
        cast = {"Sisters/Draknara": {"vector": E[0], "personName": "Lia Lujan"}}
        peer = blend(E[1], E[2], .9)
        identities = {
            "Prospects/Harlow Chase": self.identity("Harlow Chase", E[1], ageDate="2026-01-01"),
            "Prospects/Faye Foxworth": self.identity("Faye Foxworth", peer),
            "Prospects/Lone Wolf": self.identity("Lone Wolf", E[3]),
        }
        renames, evidence = family_tree.plan(identities, cast, self.policy)
        self.assertEqual(renames, {"Prospects/Faye Foxworth": "Faye Chase"})
        peer_family = next(f for f in evidence["families"] if f["rootKind"] == "identity")
        self.assertEqual(peer_family["surnameSource"], "adopted from oldest family member Harlow Chase")
        self.assertNotIn("Prospects/Lone Wolf", {m["identity"] for f in evidence["families"] for m in f["members"]})

    def test_peer_chain_through_cast_member_shares_cast_surname(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Hadley"}}
        fia = blend(E[0], E[1], .5)
        identities = {
            "Prospects/Fia Hadley": self.identity("Fia Hadley", fia),
            # Below band to the cast, but close to Fia: joins through the peer tier.
            "Potentials/Arwen Preston": self.identity("Arwen Preston", unit(*(.2 * E[0] + .9 * E[1] + .1 * E[4]))),
        }
        renames, evidence = family_tree.plan(identities, cast, self.policy)
        self.assertEqual(renames, {"Potentials/Arwen Preston": "Arwen Hadley"})
        arwen = next(m for m in evidence["families"][0]["members"] if m["identity"] == "Potentials/Arwen Preston")
        self.assertEqual(arwen["tier"], "identity")
        self.assertEqual([step["to"] for step in arwen["path"]], ["Prospects/Fia Hadley", "Angels/angelica"])

    def test_cast_without_surname_adopts_oldest_member_upward(self):
        cast = {"Sisters/Draknisa": {"vector": E[0], "personName": None}}
        identities = {
            "Prospects/Ava Moss": self.identity("Ava Moss", blend(E[0], E[1], .6), ageDate="2025-03-01"),
            "Prospects/Bea Lark": self.identity("Bea Lark", blend(E[0], E[2], .6), ageDate="2026-03-01"),
        }
        renames, evidence = family_tree.plan(identities, cast, self.policy)
        self.assertEqual(renames, {"Prospects/Bea Lark": "Bea Moss"})
        self.assertEqual(evidence["cast"]["Sisters/Draknisa"]["currentPersonName"], "Draknisa Moss")

    def test_collision_keeps_previous_name(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Hadley"}}
        identities = {"Prospects/Fia Vale": self.identity("Fia Vale", blend(E[0], E[1], .5))}
        renames, evidence = family_tree.plan(identities, cast, self.policy, reserved={"Fia Hadley"})
        self.assertEqual(renames, {})
        self.assertEqual(evidence["families"][0]["members"][0]["status"], "collision kept previous name")

    def test_orange_band_does_not_link(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Hadley"}}
        identities = {"Prospects/Fia Vale": self.identity("Fia Vale", blend(E[0], E[1], .2))}
        renames, evidence = family_tree.plan(identities, cast, self.policy)
        self.assertEqual(renames, {})
        self.assertEqual(evidence["linkedIdentityCount"], 0)

    def test_deterministic(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Hadley"}}
        identities = {f"Prospects/P{i} Name{i}": self.identity(f"P{i} Name{i}", blend(E[0], E[1 + i % 4], .3 + i / 50))
                      for i in range(8)}
        self.assertEqual(family_tree.plan(identities, cast, self.policy),
                         family_tree.plan(dict(reversed(list(identities.items()))), cast, self.policy))

    def test_policy_validation_rejects_bad_family_config(self):
        policy = copy.deepcopy(load_policy())
        validate_policy(policy)
        for bad in ({"enabled": "yes"}, {"linkMinimumBand": "red"},
                    {"castSurnameOverrides": {"Prospects/X": "Y"}}, {"castSurnameOverrides": {"Angels/x": "Two Words"}},
                    {"surprise": True}):
            broken = copy.deepcopy(policy)
            broken["familyNaming"] = {**policy["familyNaming"], **bad}
            with self.assertRaises(ValueError, msg=str(bad)):
                validate_policy(broken)

    def test_production_policy_links_at_yellow_with_angelica_hadley(self):
        config = family_tree.settings(load_policy())
        self.assertTrue(config["enabled"])
        self.assertEqual(config["minimum"], load_policy()["scoreBands"]["yellow"]["minimum"])
        self.assertEqual(config["overrides"].get("Angels/angelica"), "Hadley")


class InventNameTests(unittest.TestCase):
    def test_prefers_unused_surname(self):
        first = likeness.invent_name("seed-1", [])
        surname = first.split()[-1]
        again = likeness.invent_name("seed-1", [f"Prospects/Someone {surname}"])
        self.assertNotEqual(again.split()[-1], surname)
        self.assertEqual(again, likeness.invent_name("seed-1", [f"Prospects/Someone {surname}"]))


if __name__ == "__main__":
    unittest.main()
