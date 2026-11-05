"""Numeric family links give lookalike identities one surname, rooted at the cast where possible."""
import copy
import json
import unittest

import jsonschema
import numpy as np

from tools.art import likeness
from tools.art.likeness_library import family_tree
from tools.art.likeness_library.policy import ROOT, load_policy, validate_policy


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
        self.policy["familyNaming"] = {
            "enabled": True, "directCastMinimumSimilarity": .4,
            "secondaryMinimumSimilarityExclusive": .35, "castSurnameOverrides": {},
        }

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
            "Prospects/Jacinta Alden": self.identity("Jacinta Alden", blend(E[0], E[2], .4)),
        }
        renames, evidence = family_tree.plan(identities, cast, self.policy)
        self.assertEqual(renames, {"Prospects/Jacinta Alden": "Jacinta Hadley"})
        self.assertEqual(evidence["cast"]["Angels/angelica"]["currentPersonName"], "Angelica Hadley")
        self.assertEqual(evidence["cast"]["Angels/angelica"]["surnameSource"], "configured")

    def test_below_direct_minimum_cast_falls_back_to_peer_chain(self):
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
            # Below the direct minimum, but close to Fia: joins through the peer tier.
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
        for bad in ({"enabled": "yes"}, {"linkMinimumBand": "yellow"},
                    {"directCastMinimumSimilarity": -.01}, {"directCastMinimumSimilarity": 1.01},
                    {"directCastMinimumSimilarity": True}, {"directCastMinimumSimilarity": "0.4"},
                    {"directCastMinimumSimilarity": float("nan")},
                    {"secondaryMinimumSimilarityExclusive": -.01},
                    {"secondaryMinimumSimilarityExclusive": 1.01},
                    {"secondaryMinimumSimilarityExclusive": False},
                    {"secondaryMinimumSimilarityExclusive": "0.35"},
                    {"secondaryMinimumSimilarityExclusive": float("inf")},
                    {"castSurnameOverrides": {"Prospects/X": "Y"}}, {"castSurnameOverrides": {"Angels/x": "Two Words"}},
                    {"surprise": True}):
            broken = copy.deepcopy(policy)
            broken["familyNaming"] = {**policy["familyNaming"], **bad}
            with self.assertRaises(ValueError, msg=str(bad)):
                validate_policy(broken)

    def test_production_policy_has_separate_numeric_thresholds(self):
        config = family_tree.settings(load_policy())
        self.assertTrue(config["enabled"])
        self.assertEqual(config["directCastMinimumSimilarity"], .4)
        self.assertEqual(config["secondaryMinimumSimilarityExclusive"], .35)
        self.assertEqual(config["overrides"], {})

    def test_direct_cast_boundary_and_original_name_evidence(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Vale"}}
        for score, qualifies in ((.399999, False), (.4, True), (.400001, True)):
            with self.subTest(score=score):
                identities = {"Prospects/Fia Hadley": self.identity("Fia Hadley", blend(E[0], E[1], score))}
                before = copy.deepcopy(identities["Prospects/Fia Hadley"])
                renames, evidence = family_tree.plan(identities, cast, self.policy)
                self.assertEqual(evidence["linkedIdentityCount"], int(qualifies))
                self.assertEqual(renames, {"Prospects/Fia Hadley": "Fia Vale"} if qualifies else {})
                self.assertEqual(identities["Prospects/Fia Hadley"]["name"], before["name"])
                if qualifies:
                    member = evidence["families"][0]["members"][0]
                    self.assertEqual(member["previousName"], "Fia Hadley")
                    self.assertEqual(member["band"], "yellow")
                    self.assertEqual(evidence["cast"]["Angels/angelica"]["recordedPersonName"], "Angelica Vale")

    def test_secondary_boundary_is_strict(self):
        for score, qualifies in ((.349999, False), (.35, False), (np.nextafter(.35, 1), True), (.350001, True)):
            with self.subTest(score=score):
                identities = {
                    "Prospects/Ava Moss": self.identity("Ava Moss", E[0], ageDate="2025-01-01"),
                    "Prospects/Bea Lark": self.identity("Bea Lark", blend(E[0], E[1], score)),
                }
                renames, evidence = family_tree.plan(identities, {}, self.policy)
                self.assertEqual(evidence["linkedIdentityCount"], 2 if qualifies else 0)
                self.assertEqual(renames, {"Prospects/Bea Lark": "Bea Moss"} if qualifies else {})
                self.assertEqual(len(evidence["families"]), int(qualifies))
                if qualifies:
                    self.assertGreater(evidence["families"][0]["members"][0]["score"], .35)
                    self.assertGreater(evidence["families"][0]["members"][0]["path"][0]["score"], .35)

    def test_qualifying_direct_cast_preferred_over_stronger_peer(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Vale"}}
        vector = blend(E[0], E[1], .4)
        identities = {
            "Prospects/Ava Moss": self.identity("Ava Moss", vector),
            "Prospects/Bea Lark": self.identity("Bea Lark", vector),
        }
        _, evidence = family_tree.plan(identities, cast, self.policy)
        self.assertTrue(all(member["tier"] == "cast" for member in evidence["families"][0]["members"]))

    def test_cast_chain_requires_every_edge_to_qualify(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Vale"}}
        for direct_score in (.399999, .4):
            for secondary_score in (.35, .350001):
                with self.subTest(direct=direct_score, secondary=secondary_score):
                    anchor = blend(E[0], E[1], direct_score)
                    middle = blend(anchor, E[2], secondary_score)
                    leaf = blend(middle, E[3], .3500004)
                    identities = {
                        "Prospects/Ava Moss": self.identity("Ava Moss", anchor, ageDate="2025-01-01"),
                        "Prospects/Bea Lark": self.identity("Bea Lark", middle),
                        "Prospects/Cora Quill": self.identity("Cora Quill", leaf),
                        "Prospects/Lone Wolf": self.identity("Lone Wolf", E[4]),
                    }
                    _, evidence = family_tree.plan(identities, cast, self.policy)
                    members = [member for family in evidence["families"] for member in family["members"]]
                    cast_family = next(f for f in evidence["families"] if f["root"] == "Angels/angelica")
                    expected = 3 if direct_score >= .4 and secondary_score > .35 else int(direct_score >= .4)
                    self.assertEqual(len(cast_family["members"]), expected)
                    self.assertNotIn("Prospects/Lone Wolf", {member["identity"] for member in members})
                    for member in members:
                        for edge in member["path"]:
                            if edge["tier"] == "cast":
                                self.assertGreaterEqual(edge["score"], .4)
                            else:
                                self.assertGreater(edge["score"], .35)
                    if expected == 3:
                        leaf_row = next(row for row in members if row["identity"] == "Prospects/Cora Quill")
                        self.assertEqual([edge["tier"] for edge in leaf_row["path"]], ["identity", "identity", "cast"])

    def test_family_thresholds_do_not_depend_on_score_colours(self):
        self.policy["scoreBands"]["yellow"]["minimum"] = .2
        validate_policy(self.policy)
        identities = {"Prospects/Fia Hadley": self.identity("Fia Hadley", blend(E[0], E[1], .399999))}
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Vale"}}
        _, evidence = family_tree.plan(identities, cast, self.policy)
        self.assertEqual(evidence["linkedIdentityCount"], 0)
        self.assertEqual(family_tree.band_of(.399999, self.policy), "yellow")
        self.assertEqual(evidence["directCastMinimumSimilarity"], .4)
        self.assertEqual(evidence["secondaryMinimumSimilarityExclusive"], .35)

    def test_policy_schema_checks_numeric_thresholds(self):
        schema = json.loads((ROOT / "data" / "art" / "_schema" / "likeness-engine-policy.schema.json").read_text(
            encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema["properties"]["familyNaming"])
        config = self.policy["familyNaming"]
        self.assertEqual(list(validator.iter_errors(config)), [])
        for field in ("directCastMinimumSimilarity", "secondaryMinimumSimilarityExclusive"):
            for value in (-.01, 1.01, True, "0.4"):
                with self.subTest(field=field, value=value):
                    self.assertTrue(list(validator.iter_errors({**config, field: value})))

    def test_collision_with_name_pool_changes_first_name(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Hadley"}}
        identities = {"Prospects/Fia Vale": self.identity("Fia Vale", blend(E[0], E[1], .5))}
        renames, evidence = family_tree.plan(identities, cast, self.policy, reserved={"Fia Hadley"},
                                             first_names=["Fia", "Gia"])
        self.assertEqual(renames, {"Prospects/Fia Vale": "Gia Hadley"})
        self.assertTrue(evidence["families"][0]["members"][0]["status"].startswith("renamed"))

    def test_unrelated_holder_of_cast_surname_gets_fresh_surname(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Vale"}}
        identities = {
            "Prospects/Fia Hadley": self.identity("Fia Hadley", blend(E[0], E[1], .45)),
            "Models/Amira Vale": self.identity("Amira Vale", E[2], ageDate="2024-01-01"),
        }
        renames, evidence = family_tree.plan(identities, cast, self.policy, surnames=["Vale", "Hadley", "Quill"])
        self.assertEqual(renames, {"Prospects/Fia Hadley": "Fia Vale", "Models/Amira Vale": "Amira Quill"})
        amira = next(f for f in evidence["families"] if f["root"] == "Models/Amira Vale")
        self.assertEqual(amira["displacedFrom"], {"surname": "Vale", "owner": "Angels/angelica"})
        self.assertEqual(evidence["displacedFamilyCount"], 1)

    def test_unrelated_lone_identities_sharing_a_surname_oldest_keeps_it(self):
        identities = {
            "Prospects/Opal Vale": self.identity("Opal Vale", E[1], ageDate="2026-02-01"),
            "Potentials/Yvette Vale": self.identity("Yvette Vale", E[2], ageDate="2026-06-01"),
        }
        renames, evidence = family_tree.plan(identities, {}, self.policy, surnames=["Vale", "Marsh"])
        self.assertEqual(renames, {"Potentials/Yvette Vale": "Yvette Marsh"})
        self.assertEqual([f["root"] for f in evidence["families"]], ["Potentials/Yvette Vale"])

    def test_linked_family_keeps_surname_its_members_share(self):
        cast = {"Angels/angelica": {"vector": E[0], "personName": "Angelica Vale"}}
        identities = {"Models/Amira Vale": self.identity("Amira Vale", blend(E[0], E[1], .4))}
        renames, evidence = family_tree.plan(identities, cast, self.policy, surnames=["Quill"])
        self.assertEqual(renames, {})
        self.assertEqual(evidence["displacedFamilyCount"], 0)


class InventNameTests(unittest.TestCase):
    def test_prefers_unused_surname(self):
        first = likeness.invent_name("seed-1", [])
        surname = first.split()[-1]
        again = likeness.invent_name("seed-1", [f"Prospects/Someone {surname}"])
        self.assertNotEqual(again.split()[-1], surname)
        self.assertEqual(again, likeness.invent_name("seed-1", [f"Prospects/Someone {surname}"]))


if __name__ == "__main__":
    unittest.main()
