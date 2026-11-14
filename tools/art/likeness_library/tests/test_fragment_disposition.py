"""Disposition handoffs cannot turn resemblance or uncertainty into family truth."""
import copy
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art import likeness_disposition_trial as cli
from tools.art.likeness_library import fragment_disposition, fragment_review
from tools.art.likeness_library.tests import test_fragment_reconciliation as fixtures


class DispositionTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.ReconciliationTests()
        fixture.setUp()
        self.fixture = fixture
        _, self.ledger = fixture.prepare()
        rows = [{"photoId": p["photoId"], "currentFolder": p["currentFolder"], "execution": "not-authorized",
                 "placement": "unchanged", "reconsiderable": True}
                for p in fixture.candidate["rows"]]
        self.comparison = {"variants": {
            key: {"rows": copy.deepcopy(rows)} for key in ("control", "combined")
        }}

    def build(self):
        return fragment_disposition.build(self.fixture.packet, self.fixture.answers, self.ledger, self.comparison)

    def test_same_person_proposes_direct_appearances_not_union_or_core_growth(self):
        before = copy.deepcopy((self.fixture.packet, self.fixture.answers, self.ledger, self.comparison))
        result = self.build()
        case = result["cases"][0]
        self.assertEqual(case["disposition"], "same-person-appearance-candidate")
        self.assertEqual(len(case["appearanceGroups"]), 2)
        self.assertEqual(case["differentReferencePhotoIds"], ["no"])
        self.assertEqual(case["family"]["status"], "not-eligible")
        members = {p for g in case["appearanceGroups"] for p in g["memberPhotoIds"]}
        self.assertEqual(members, {"q", "own", "yes"})
        self.assertNotIn("residual", members)
        self.assertNotIn("no", members)
        self.assertTrue(all(g["coreAdmission"] == "not-proposed" for g in case["appearanceGroups"]))
        self.assertEqual(before, (self.fixture.packet, self.fixture.answers, self.ledger, self.comparison))
        self.assertEqual(result, self.build())

    def test_different_lookalike_is_only_a_conditional_fictional_family_handoff(self):
        answer = self.fixture.answers["decisions"][0]
        answer["targetMatch"] = "different"
        answer["pairs"][1]["label"] = "different"
        _, self.ledger = self.fixture.prepare()
        case = self.build()["cases"][0]
        self.assertEqual(case["disposition"], "distinct-lookalike-candidate")
        self.assertEqual(case["appearanceGroups"], [])
        self.assertEqual(case["family"]["status"], "eligible-after-distinct-identity-validation")
        self.assertIsNone(case["family"]["relationship"])
        self.assertFalse(case["family"]["samePersonAuthority"])
        self.assertFalse(case["family"]["surnameChange"])

    def test_neither_or_uncertain_never_gets_family_fallback(self):
        for current, target in (("different", "different"), ("uncertain", "same"), ("same", "uncertain")):
            with self.subTest(current=current, target=target):
                self.fixture.answers["decisions"][0].update(currentMatch=current, targetMatch=target)
                _, self.ledger = self.fixture.prepare()
                case = self.build()["cases"][0]
                self.assertEqual(case["disposition"], "unresolved-identity")
                self.assertEqual(case["family"]["status"], "not-eligible")
                self.assertEqual(case["appearanceGroups"], [])
                self.assertTrue(case["reconsiderable"])

    def test_conflicted_positive_cannot_establish_appearance(self):
        _, self.ledger = self.fixture.prepare({"pairs": [{"photoIds": ["yes", "q"], "label": "different"}]})
        case = self.build()["cases"][0]
        self.assertEqual(case["disposition"], "unresolved-identity")
        self.assertEqual(case["uncertainReferencePhotoIds"], ["yes"])
        self.assertEqual(case["appearanceGroups"], [])

    def test_missing_pair_or_wrong_binding_fails_explicitly(self):
        self.ledger["packetSHA256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "binding differs"):
            self.build()
        self.ledger["packetSHA256"] = self.fixture.packet["packetSHA256"]
        self.ledger["pairs"] = []
        with self.assertRaisesRegex(ValueError, "missing reviewed direct evidence"):
            self.build()

    def test_population_and_execution_contracts_are_checked(self):
        self.comparison["variants"]["control"]["rows"].pop()
        with self.assertRaisesRegex(ValueError, "conservation"):
            self.build()
        self.setUp()
        self.comparison["variants"]["combined"]["rows"][0]["execution"] = "move"
        with self.assertRaisesRegex(ValueError, "executable or locked"):
            self.build()

    def test_order_independence_preserves_unreviewed_photos(self):
        before = self.build()
        for variant in self.comparison["variants"].values():
            variant["rows"].reverse()
        self.fixture.packet["cases"].reverse()
        self.fixture.answers["decisions"].reverse()
        self.assertEqual(before, self.build())
        self.assertEqual(len(before["rows"]), len(self.fixture.run["photos"]))
        self.assertEqual(sum(bool(r["dispositionCaseIds"]) for r in before["rows"]), 1)

    def test_multiple_cases_never_extend_members_transitively(self):
        extra = copy.deepcopy(self.fixture.packet["cases"][0])
        extra.update(id="case2", photoId="yes", currentReferenceId="q", targetReferenceIds=["residual", "no"])
        self.fixture.packet["cases"].append(extra)
        answer = copy.deepcopy(self.fixture.answers["decisions"][0])
        answer.update(caseId="case2", pairs=[
            {"referencePhotoId": "q", "label": "same"},
            {"referencePhotoId": "residual", "label": "same"},
            {"referencePhotoId": "no", "label": "different"},
        ])
        self.fixture.answers["decisions"].append(answer)
        self.ledger.update(packetSHA256=self.fixture.packet["packetSHA256"],
                           answersSHA256=fragment_review.digest(self.fixture.answers))
        self.ledger["pairs"].extend([
            {"photoIds": ["yes", "residual"], "label": "same"},
            {"photoIds": ["yes", "no"], "label": "different"},
        ])
        before = self.build()
        original = before["cases"][0]
        self.assertNotIn("residual", {p for g in original["appearanceGroups"] for p in g["memberPhotoIds"]})
        self.fixture.packet["cases"].reverse()
        for variant in self.comparison["variants"].values():
            variant["rows"].reverse()
        self.assertEqual(before, self.build())

    def test_source_receipt_chain_and_input_output_corruption(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            root = pathlib.Path(name)
            source = root / "source"
            packet_dir = root / "packet"
            source.mkdir()
            packet_dir.mkdir()
            answers = root / "renamed-answers.json"
            answers.write_text(json.dumps({**self.fixture.answers, "kind": "identity-fragment-answers"}))
            packet = packet_dir / "packet.json"
            packet.write_text(json.dumps(self.fixture.packet))
            fragment_receipt = packet_dir / "receipt.json"
            fragment_receipt.write_text(json.dumps({"kind": "fragment-experiment-receipt"}))
            inputs = {str(p): cli.shadow.digest(p) for p in (answers, packet, fragment_receipt)}
            for name, value in (("ledger.json", self.ledger), ("comparison.json", self.comparison)):
                (source / name).write_text(json.dumps(value))
            (source / "index.html").write_text("frozen")
            receipt = {"inputs": inputs, "code": {}, "outputs": {
                name: cli.shadow.digest(source / name) for name in ("ledger.json", "comparison.json", "index.html")
            }}
            (source / "receipt.json").write_text(json.dumps(receipt))
            with mock.patch.object(cli.parent, "codes", return_value={}), \
                    mock.patch.object(cli.parent, "load_inputs", return_value=(None, inputs)):
                self.assertEqual(cli.load(source)[0], self.fixture.packet)
                (source / "index.html").write_text("tampered")
                with self.assertRaisesRegex(ValueError, "source output changed"):
                    cli.load(source)
                packet.write_text("{}")
                with self.assertRaisesRegex(ValueError, "source input changed"):
                    cli.load(source)

    def test_launcher_preview_apply_repeat_check_and_output_tampering(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            root = pathlib.Path(name)
            source = root / "source"
            out = root / "report"
            args = ["--source", str(source), "--out", str(out)]
            with mock.patch.object(cli, "load", return_value=(
                self.fixture.packet, self.fixture.answers, self.ledger, self.comparison, {},
            )), mock.patch.object(cli, "codes", return_value={}), \
                    mock.patch.object(cli, "output_path", return_value=out):
                self.assertEqual(cli.main(args + ["--dry-run"]), 0)
                self.assertFalse(out.exists())
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                original = (out / "receipt.json").read_bytes()
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                self.assertEqual(cli.main(args + ["--check"]), 0)
                self.assertEqual(original, (out / "receipt.json").read_bytes())
                (out / "dispositions.json").write_text("{}")
                self.assertEqual(cli.main(args + ["--check"]), 1)


if __name__ == "__main__":
    unittest.main()
