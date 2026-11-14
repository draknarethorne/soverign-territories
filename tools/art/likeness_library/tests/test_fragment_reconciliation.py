"""Reconciliation does not turn human pair evidence into whole-group authority."""
import copy
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art import likeness_reconcile_trial as cli
from tools.art.likeness_library import fragment_reconciliation as subject, fragment_review


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.run = {"photos": [{"photoId": p, "preparedSHA256": "hash-" + p} for p in ("q", "own", "yes", "no", "residual")]}
        self.candidate = {
            "identities": [
                {"folder": "Sisters/Source", "referencePhotoIds": ["own"]},
                {"folder": "Models/Target", "referencePhotoIds": ["yes", "no", "residual"]},
            ],
            "rows": [{"photoId": p["photoId"], "currentFolder": "Sisters/Source" if p["photoId"] in ("q", "own") else "Models/Target"}
                     for p in self.run["photos"]],
        }
        self.packet = {
            "candidateSHA256": fragment_review.digest(self.candidate), "packetSHA256": "fixture",
            "usedPhotoIds": ["q", "own", "yes", "no"], "cases": [{
                "id": "c1", "photoId": "q", "currentFolder": "Sisters/Source", "targetFolder": "Models/Target",
                "currentReferenceId": "own", "targetReferenceIds": ["yes", "no"],
            }],
        }
        self.answers = {"schemaVersion": 1, "kind": "identity-fragment-answers",
                        "packetSHA256": "fixture", "decisions": [{
                            "caseId": "c1", "currentMatch": "same", "targetMatch": "same", "context": "helpful",
                            "pairs": [{"referencePhotoId": p, "label": "different" if p == "no" else "same"}
                                      for p in ("own", "yes", "no")],
                        }]}

    def prepare(self, effective=None):
        return subject.prepare(self.candidate, self.packet, self.answers, effective or {"pairs": []}, self.run)

    def test_repairs_references_not_ownership_and_never_admits_residual(self):
        before = copy.deepcopy((self.candidate, self.packet, self.answers, self.run))
        repaired, ledger = self.prepare()
        self.assertEqual(repaired["identities"][1]["referencePhotoIds"], ["yes", "residual"])
        self.assertEqual(repaired["rows"], self.candidate["rows"])
        self.assertEqual(len(ledger["associations"]), 2)
        self.assertFalse(any("residual" in a["sameReferencePhotoIds"] for a in ledger["associations"]))
        self.assertEqual(ledger["referenceProposals"][0]["placement"], "unchanged")
        self.assertEqual(before, (self.candidate, self.packet, self.answers, self.run))
        self.assertEqual(self.prepare(), (repaired, ledger))

    def test_different_target_is_not_a_global_reference_withdrawal(self):
        self.answers["decisions"][0]["targetMatch"] = "different"
        repaired, ledger = self.prepare()
        self.assertEqual(repaired, self.candidate)
        self.assertEqual(ledger["referenceProposals"], [])
        self.assertEqual(len(ledger["associations"]), 1)

    def test_uncertainty_and_conflicting_old_label_never_become_positive_support(self):
        self.answers["decisions"][0]["pairs"][1]["label"] = "uncertain"
        repaired, ledger = self.prepare()
        self.assertEqual(repaired, self.candidate)
        self.assertEqual(len(ledger["associations"]), 1)
        self.answers["decisions"][0]["pairs"][1]["label"] = "same"
        repaired, ledger = self.prepare({"pairs": [{"photoIds": ["yes", "q"], "label": "different"}]})
        self.assertEqual(ledger["conflicts"][0]["effective"], "uncertain")
        self.assertEqual(repaired, self.candidate)
        self.assertEqual(len(ledger["associations"]), 1)

    def test_confirmed_reference_conflict_is_held_without_withdrawal(self):
        self.candidate["identities"][1]["referenceEvidence"] = {"construction": "confirmed-character-intent"}
        self.packet["candidateSHA256"] = fragment_review.digest(self.candidate)
        repaired, ledger = self.prepare()
        self.assertEqual(repaired, self.candidate)
        self.assertEqual(ledger["referenceProposals"][0]["referenceUse"], "conflict-hold")

    def test_later_reverse_pair_conflict_cannot_leave_early_association_or_repair(self):
        second = copy.deepcopy(self.packet["cases"][0])
        second.update(id="c2", photoId="yes", currentFolder="Models/Target",
                      targetFolder="Sisters/Source", currentReferenceId="residual",
                      targetReferenceIds=["q", "own"])
        self.packet["cases"].append(second)
        self.packet["usedPhotoIds"].append("residual")
        self.answers["decisions"].append({
            "caseId": "c2", "currentMatch": "uncertain", "targetMatch": "different", "context": "uncertain",
            "pairs": [{"referencePhotoId": p, "label": "different"} for p in ("residual", "q", "own")],
        })
        repaired, ledger = self.prepare()
        self.assertEqual(repaired, self.candidate)
        self.assertEqual(len(ledger["associations"]), 1)
        self.assertEqual(ledger["associations"][0]["folder"], "Sisters/Source")
        self.assertEqual(len(ledger["conflicts"]), 1)

    def test_neither_has_no_guessed_owner(self):
        self.answers["decisions"][0].update(currentMatch="different", targetMatch="different")
        repaired, ledger = self.prepare()
        self.assertEqual(ledger["associations"], [])
        self.assertIsNone(ledger["unresolved"][0]["owner"])
        self.assertEqual(repaired, self.candidate)

    def test_no_transitive_pairs_and_four_conserved_variants(self):
        _, ledger = self.prepare({"pairs": [{"photoIds": ["yes", "residual"], "label": "same"}]})
        self.assertFalse(any(set(p["photoIds"]) == {"q", "residual"} for p in ledger["pairs"]))
        rows = [{"photoId": p["photoId"], "currentFolder": "Models/Target", "suggestedFolder": "Sisters/Source",
                 "hold": None, "own": None, "topCandidates": []} for p in self.run["photos"]]
        original = {"rows": rows}
        repaired = copy.deepcopy(original)
        repaired["rows"][0]["suggestedFolder"] = None
        comparison = subject.compare(original, repaired, ledger)
        self.assertEqual(len(comparison["variants"]), 4)
        for variant in comparison["variants"].values():
            self.assertEqual(len(variant["rows"]), 5)
            self.assertEqual(variant["summary"]["executableMoves"], 0)
            self.assertEqual(variant["summary"]["automaticIdentityDiscoveries"], 0)
            self.assertTrue(all(r["reconsiderable"] for r in variant["rows"]))
        self.assertEqual(comparison["variants"]["combined"]["summary"]["suggestionChangesFromLabelControl"], 1)
        self.assertEqual(comparison["variants"]["association-only"]["summary"]["suggestionChangesFromLabelControl"], 0)
        self.assertEqual(comparison["variants"]["combined"]["summary"]["directAssociationQueryCount"], 1)

    def test_packet_binding_and_content_missing_fail_explicitly(self):
        self.packet["candidateSHA256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "candidate differs"):
            self.prepare()
        self.packet["candidateSHA256"] = fragment_review.digest(self.candidate)
        self.run["photos"][0].pop("preparedSHA256")
        with self.assertRaisesRegex(ValueError, "content binding"):
            self.prepare()

    def test_receipt_tampering_is_refused(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            root = pathlib.Path(name)
            outputs = {}
            for name in ("ledger.json", "comparison.json", "index.html"):
                (root / name).write_text("{}")
                outputs[name] = cli.shadow.digest(root / name)
            (root / "receipt.json").write_text(json.dumps({"inputs": {}, "code": {}, "outputs": outputs}))
            with mock.patch.object(cli, "codes", return_value={}):
                cli.check(root, {})
                (root / "ledger.json").write_text("changed")
                with self.assertRaisesRegex(ValueError, "output changed"):
                    cli.check(root, {})

    def test_source_receipt_normalizes_paths_without_weakening_hash_checks(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            root = pathlib.Path(name)
            code = root / "tool.py"
            code.write_text("fixture")
            source = root / "source"
            source.mkdir()
            packet = {"usedPhotoIds": []}
            packet["packetSHA256"] = fragment_review.digest(packet)
            outputs = {}
            for name in ("packet.json", "evidence.json", "context.json", "display.json",
                         "prior-feedback.json", "index.html"):
                (source / name).write_text(json.dumps(packet if name == "packet.json" else {}))
                outputs[name] = cli.shadow.digest(source / name)
            historical = str(root / "subdirectory" / ".." / "tool.py")
            receipt = {"inputs": {}, "code": {historical: cli.shadow.digest(code)}, "outputs": outputs}
            (source / "receipt.json").write_text(json.dumps(receipt))
            answers = root / "answers.json"
            answers.write_text("{}")
            with mock.patch.object(cli.source_cli, "code_bindings", return_value={str(code): cli.shadow.digest(code)}):
                cli.load_inputs(source, answers)
                (source / "evidence.json").write_text("changed")
                with self.assertRaisesRegex(ValueError, "source output changed"):
                    cli.load_inputs(source, answers)

    def test_prepare_repairs_frozen_engine_inputs_without_certifying_residuals(self):
        from tools.art.likeness_library.tests.test_fragment_evidence import FragmentEvidenceTests, angle
        from tools.art.likeness_library import fragment_evidence
        fixture = FragmentEvidenceTests()
        fixture.setUp()
        for pid, degrees, folder in (
            ("q", 0, "Sisters/Source"), ("own", 5, "Sisters/Source"),
            ("yes", 15, "Models/Target"), ("no", 80, "Models/Target"),
            ("residual", -15, "Models/Target"),
        ):
            fixture.add_photo(pid, angle(degrees), folder)
        fixture.add_identity("source", "Sisters/Source", ["own"])
        fixture.add_identity("target", "Models/Target", ["yes", "no", "residual"])
        self.candidate = fixture.candidate()
        self.run = fixture.receipt()
        self.packet["candidateSHA256"] = fragment_review.digest(self.candidate)
        repaired, ledger = self.prepare()
        result = fragment_evidence.evaluate(repaired, self.run, fixture.vectors, {"pairs": ledger["pairs"]})
        row = next(r for r in result["rows"] if r["photoId"] == "q")
        for target in row["topCandidates"]:
            self.assertNotIn("no", target["referencePhotoIds"])
        self.assertEqual(len(result["rows"]), 5)
        self.assertTrue(all(r["execution"] == "not-authorized" for r in result["rows"]))


if __name__ == "__main__":
    unittest.main()
