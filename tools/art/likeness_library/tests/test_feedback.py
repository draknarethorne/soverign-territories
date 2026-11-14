#!/usr/bin/env python3
"""Tests for strict human-feedback ingestion (synthetic data only)."""
import copy
import unittest

from tools.art.likeness_library import feedback


def make_packet():
    def case(index, photo, refs):
        return {"id": f"case-{index:03d}", "photoId": photo,
                "panels": [{"folder": "F", "references": [{"photoId": r} for r in refs]}]}
    packet = {"schemaVersion": 1, "binding": {"run": "x"}, "cases": [
        case(1, "p1", ["r1", "r2"]), case(2, "p2", ["r1", "p1"]), case(3, "p3", ["r3"])]}
    packet["packetSHA256"] = feedback.packet_digest(packet)
    return packet


def make_feedback(packet, labels=None):
    labels = labels or {}
    decisions = []
    for case in packet["cases"]:
        refs = [r["photoId"] for p in case["panels"] for r in p["references"]]
        decisions.append({"caseId": case["id"], "photoId": case["photoId"], "note": "",
                          "pairs": [{"referencePhotoId": r, "label": labels.get((case["id"], r), "uncertain")}
                                    for r in refs]})
    return {"schemaVersion": 1, "packetSHA256": packet["packetSHA256"], "binding": packet["binding"],
            "decisions": decisions}


def clar(packet, overrides=()):
    return {"schemaVersion": 1, "packetSHA256": packet["packetSHA256"], "overrides": list(overrides)}


def pair_of(result, a, b):
    return next(p for p in result["pairs"] if p["photoIds"] == sorted([a, b]))


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.packet = make_packet()
        self.fb = make_feedback(self.packet)

    def refuse(self, text, fb=None, packet=None, clarifications=None):
        with self.assertRaises(ValueError) as caught:
            feedback.ingest(packet or self.packet, fb or self.fb,
                            clarifications if clarifications is not None else clar(self.packet))
        self.assertIn(text, str(caught.exception))

    def test_basic_shape_and_no_mutation(self):
        packet, fb, cl = copy.deepcopy(self.packet), copy.deepcopy(self.fb), clar(self.packet)
        before = copy.deepcopy((packet, fb, cl))
        result = feedback.ingest(packet, fb, cl)
        self.assertEqual((packet, fb, cl), before)
        self.assertEqual(result, feedback.ingest(packet, fb, cl))
        self.assertEqual(result["packetSHA256"], packet["packetSHA256"])
        self.assertEqual(result["binding"], packet["binding"])
        self.assertEqual(result["summary"]["observationCount"], 5)
        self.assertEqual(result["summary"]["pairCount"], 5)
        self.assertEqual(result["observations"][0], {
            "caseId": "case-001", "photoId": "p1", "referencePhotoId": "r1",
            "rawLabel": "uncertain", "label": "uncertain"})
        result["pairs"][0]["observations"].clear()
        self.assertEqual(feedback.ingest(packet, fb, cl)["summary"]["pairCount"], 5)

    def test_empty_clarifications_allowed(self):
        self.assertEqual(feedback.ingest(self.packet, self.fb, {})["summary"]["overrideCount"], 0)

    def test_packet_digest_and_schema(self):
        bad = copy.deepcopy(self.packet)
        bad["cases"][0]["photoId"] = "zz"
        self.refuse("canonical content", packet=bad)
        bad = copy.deepcopy(self.packet)
        del bad["packetSHA256"]
        self.refuse("missing packetSHA256", packet=bad)
        bad = copy.deepcopy(self.packet)
        bad["schemaVersion"] = 2
        self.refuse("Packet schemaVersion", packet=bad)

    def test_feedback_binding_mismatches(self):
        for field, value, text in (("packetSHA256", "0" * 64, "different packet"),
                                   ("binding", {"run": "y"}, "binding differs"),
                                   ("schemaVersion", 2, "schemaVersion")):
            fb = copy.deepcopy(self.fb)
            fb[field] = value
            self.refuse(text, fb)

    def test_feedback_malformed_and_extra_fields(self):
        fb = copy.deepcopy(self.fb)
        del fb["decisions"]
        self.refuse("missing", fb)
        fb = copy.deepcopy(self.fb)
        fb["extra"] = 1
        self.refuse("unexpected", fb)
        fb = copy.deepcopy(self.fb)
        fb["decisions"] = {}
        self.refuse("must be a list", fb)

    def test_case_set_must_be_complete_and_unique(self):
        fb = copy.deepcopy(self.fb)
        fb["decisions"].pop()
        self.refuse("missing cases ['case-003']", fb)
        fb = copy.deepcopy(self.fb)
        fb["decisions"].append(copy.deepcopy(fb["decisions"][0]))
        self.refuse("repeats case case-001", fb)
        fb = copy.deepcopy(self.fb)
        fb["decisions"][0]["caseId"] = "case-999"
        self.refuse("unknown case", fb)

    def test_photo_and_reference_sets_strict(self):
        fb = copy.deepcopy(self.fb)
        fb["decisions"][0]["photoId"] = "other"
        self.refuse("photoId differs", fb)
        fb = copy.deepcopy(self.fb)
        fb["decisions"][0]["pairs"].pop()
        self.refuse("missing references ['r2']", fb)
        fb = copy.deepcopy(self.fb)
        fb["decisions"][0]["pairs"][1]["referencePhotoId"] = "r1"
        self.refuse("repeats reference r1", fb)
        fb = copy.deepcopy(self.fb)
        fb["decisions"][0]["pairs"][1]["referencePhotoId"] = "nope"
        self.refuse("unknown reference", fb)

    def test_labels_validated_and_unreviewed_rejected(self):
        fb = copy.deepcopy(self.fb)
        fb["decisions"][0]["pairs"][0]["label"] = "unreviewed"
        self.refuse("unreviewed", fb)
        fb["decisions"][0]["pairs"][0]["label"] = "maybe"
        self.refuse("invalid label", fb)
        fb["decisions"][0]["pairs"][0]["label"] = None
        self.refuse("invalid label", fb)

    def test_note_must_be_string(self):
        fb = copy.deepcopy(self.fb)
        fb["decisions"][0]["note"] = None
        self.refuse("note must be a string", fb)

    def test_notes_preserved_as_evidence_and_residue_excluded(self):
        fb = copy.deepcopy(self.fb)
        fb["decisions"][0]["note"] = "  looks like a sibling  "
        fb["decisions"][1]["note"] = "Temporary UI verification"
        fb["decisions"][2]["note"] = "   "
        result = feedback.ingest(self.packet, fb, clar(self.packet))
        self.assertEqual(result["notes"], [{"caseId": "case-001", "photoId": "p1", "note": "looks like a sibling"}])
        self.assertEqual(result["summary"]["excludedNoteCount"], 1)
        self.assertTrue(all(o["label"] == "uncertain" for o in result["observations"]))

    def test_repeated_pair_is_symmetric_and_not_independent(self):
        fb = make_feedback(self.packet, {("case-001", "r1"): "same", ("case-002", "r1"): "same"})
        result = feedback.ingest(self.packet, fb, clar(self.packet))
        pair = pair_of(result, "p1", "r1")
        self.assertEqual(pair["label"], "same")
        self.assertEqual(len(pair["observations"]), 1)
        fb = make_feedback(self.packet, {("case-001", "p2"): "same"})
        packet = copy.deepcopy(self.packet)
        packet["cases"][0]["panels"][0]["references"].append({"photoId": "p2"})
        packet["packetSHA256"] = feedback.packet_digest(packet)
        fb = make_feedback(packet, {("case-001", "p2"): "same", ("case-002", "p1"): "same"})
        result = feedback.ingest(packet, fb, clar(packet))
        pair = pair_of(result, "p1", "p2")
        self.assertEqual((pair["label"], len(pair["observations"])), ("same", 2))
        self.assertEqual(result["summary"]["repeatedPairCount"], 1)
        self.assertFalse(result["summary"]["independentEvidence"])

    def test_definite_versus_uncertain_is_uncertain(self):
        packet = copy.deepcopy(self.packet)
        packet["cases"][0]["panels"][0]["references"].append({"photoId": "p2"})
        packet["packetSHA256"] = feedback.packet_digest(packet)
        fb = make_feedback(packet, {("case-001", "p2"): "same", ("case-002", "p1"): "uncertain"})
        result = feedback.ingest(packet, fb, clar(packet))
        self.assertEqual(pair_of(result, "p1", "p2")["label"], "uncertain")
        self.assertEqual(result["summary"]["mixedUncertainPairCount"], 1)

    def test_uncertain_duplicates_stay_uncertain(self):
        result = feedback.ingest(self.packet, self.fb, clar(self.packet))
        self.assertEqual(result["summary"]["labelCounts"], {"same": 0, "different": 0, "uncertain": 5})

    def _conflict_packet(self):
        packet = copy.deepcopy(self.packet)
        packet["cases"][0]["panels"][0]["references"].append({"photoId": "p2"})
        packet["packetSHA256"] = feedback.packet_digest(packet)
        fb = make_feedback(packet, {("case-001", "p2"): "same", ("case-002", "p1"): "different"})
        return packet, fb

    def test_definite_conflict_refuses_and_override_resolves(self):
        packet, fb = self._conflict_packet()
        with self.assertRaises(ValueError) as caught:
            feedback.ingest(packet, fb, clar(packet))
        self.assertIn("['p1', 'p2']", str(caught.exception))
        self.assertIn("case-001=same", str(caught.exception))
        for ids in (["p1", "p2"], ["p2", "p1"]):
            cl = clar(packet, [{"photoIds": ids, "label": "uncertain", "source": "the user said so"}])
            result = feedback.ingest(packet, fb, cl)
            pair = pair_of(result, "p1", "p2")
            self.assertEqual(pair["label"], "uncertain")
            self.assertEqual(pair["override"], {"label": "uncertain", "source": "the user said so"})
            self.assertEqual(len(pair["observations"]), 2)
            self.assertEqual(result["summary"]["overriddenPairCount"], 1)

    def test_override_can_supply_definite_label(self):
        cl = clar(self.packet, [{"photoIds": ["r1", "p1"], "label": "same", "source": "q"}])
        result = feedback.ingest(self.packet, self.fb, cl)
        self.assertEqual(pair_of(result, "p1", "r1")["label"], "same")
        self.assertEqual(pair_of(result, "p1", "r1")["observations"][0]["rawLabel"], "uncertain")

    def test_override_validation(self):
        good = {"photoIds": ["p1", "r1"], "label": "same", "source": "q"}
        cases = [
            ({**good, "photoIds": ["p1", "p1"]}, "two distinct"),
            ({**good, "photoIds": ["p1"]}, "two distinct"),
            ({**good, "photoIds": ["p1", "r1", "r2"]}, "two distinct"),
            ({**good, "photoIds": ["p1", 3]}, "two distinct"),
            ({**good, "photoIds": ["r1", "r2"]}, "not a pair in the packet"),
            ({**good, "label": "unreviewed"}, "invalid label"),
            ({**good, "source": "  "}, "non-empty string"),
            ({**good, "extra": 1}, "unexpected"),
            ({"photoIds": ["p1", "r1"], "label": "same"}, "missing"),
        ]
        for item, text in cases:
            self.refuse(text, clarifications=clar(self.packet, [item]))
        self.refuse("repeat pair", clarifications=clar(self.packet, [good, {**good, "photoIds": ["r1", "p1"], "label": "different"}]))

    def test_clarification_binding(self):
        self.refuse("different packet", clarifications={**clar(self.packet), "packetSHA256": "0"})
        self.refuse("schemaVersion", clarifications={**clar(self.packet), "schemaVersion": 2})
        self.refuse("missing", clarifications={"schemaVersion": 1, "packetSHA256": self.packet["packetSHA256"]})
        self.refuse("must be a list", clarifications={**clar(self.packet), "overrides": {}})

    def test_transitive_same_chain_contradicts_different(self):
        fb = make_feedback(self.packet, {("case-001", "r1"): "same", ("case-002", "r1"): "same",
                                         ("case-002", "p1"): "different"})
        # p1-r1 same, p2-r1 same => p1~p2 via r1; p2-p1 different contradicts.
        with self.assertRaises(ValueError) as caught:
            feedback.ingest(self.packet, fb, clar(self.packet))
        message = str(caught.exception)
        self.assertIn("Contradiction", message)
        self.assertIn("['p1', 'r1', 'p2']", message)

    def test_same_and_different_on_distinct_pairs_without_path_is_allowed(self):
        fb = make_feedback(self.packet, {("case-001", "r1"): "same", ("case-002", "r1"): "different"})
        result = feedback.ingest(self.packet, fb, clar(self.packet))
        self.assertEqual(pair_of(result, "p2", "r1")["label"], "different")
    def test_different_across_unconnected_pairs_is_allowed(self):
        fb = make_feedback(self.packet, {("case-001", "r1"): "same", ("case-003", "r3"): "different"})
        result = feedback.ingest(self.packet, fb, clar(self.packet))
        self.assertEqual(result["summary"]["labelCounts"]["same"], 1)
        self.assertEqual(result["summary"]["labelCounts"]["different"], 1)

    def test_override_can_break_transitive_contradiction_only_on_stated_pair(self):
        fb = make_feedback(self.packet, {("case-001", "r1"): "same", ("case-002", "r1"): "same",
                                         ("case-002", "p1"): "different"})
        cl = clar(self.packet, [{"photoIds": ["p1", "p2"], "label": "uncertain", "source": "q"}])
        result = feedback.ingest(self.packet, fb, cl)
        self.assertEqual(pair_of(result, "p1", "p2")["label"], "uncertain")


if __name__ == "__main__":
    unittest.main()
