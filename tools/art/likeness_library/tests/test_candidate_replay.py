"""Connected candidate proposals retain shared policy gates and do not consume positive labels."""
import copy
import json
import pathlib
import tempfile
import unittest
from unittest import mock

import numpy as np

from tools.art import likeness_candidate_replay as cli
from tools.art.likeness_library import candidate_replay as subject, fragment_review, policy


class CandidateReplayTests(unittest.TestCase):
    def setUp(self):
        self.settings = copy.deepcopy(policy.load_policy())
        self.ids = ["q", "own", "a", "b", "c", "d"]
        self.photos = [{
            "photoId": pid, "preparedSHA256": "hash-" + pid,
            "destination": f"Models/{'Source' if pid in ('q', 'own') else 'Target'}/gallery/{pid}.jpg",
        } for pid in self.ids]
        self.audit = [{
            **photo, "bucket": "gallery", "qualityEligible": True,
            "ambiguousPhotoId": False, "metadataStale": False, "protected": False,
            "anchor": False, "workflowSelected": False, "identityProtected": False,
            "rejectionHistory": False, "ownScore": .3, "rivals": [], "higherRival": False,
            "refinementTarget": None, "refinementDecision": {"decision": "hold", "reason": "old"},
        } for photo in self.photos]
        self.run = {"photos": self.photos, "finalMembershipAudit": {"rows": self.audit}, "policy": self.settings}
        self.candidate = {
            "rows": [{"photoId": p["photoId"], "currentFolder": "/".join(p["destination"].split("/")[:2])}
                     for p in self.photos],
            "identities": [{"folder": "Models/Source", "referencePhotoIds": ["own"]},
                           {"folder": "Models/Target", "referencePhotoIds": ["a", "b", "c", "d"]}],
            "appearances": [],
        }
        self.evidence = {"rows": [{
            **row, "own": {"subgroupScore": .3}, "hold": None,
            "topCandidates": [{
                "folder": "Models/Target" if row["currentFolder"] == "Models/Source" else "Models/Source",
                "subgroupScore": .9, "supportCount": 4,
                "referencePhotoIds": ["a", "b", "c", "d"] if row["currentFolder"] == "Models/Source" else ["own"],
                "blockers": [],
            }],
        } for row in self.candidate["rows"]]}
        self.ledger = {"pairs": [], "referenceProposals": [], "unresolved": []}

    def rows(self):
        return subject.policy_rows(self.candidate, self.evidence, self.run, self.ledger)

    def query(self):
        return next(r for r in self.rows() if r["photoId"] == "q")

    def test_existing_policy_proposes_destination_not_execution(self):
        result = self.query()
        self.assertEqual(result["candidateDecision"]["decision"], "move")
        self.assertEqual(result["proposedDestination"], "Models/Target/gallery")
        self.assertEqual(result["execution"], "not-authorized")
        self.assertEqual(result["placement"], "unchanged")
        self.assertEqual(result["family"], "unassigned-identity-assessment-first")

    def test_saved_protection_quality_workflow_rejection_gates_survive(self):
        for field in ("protected", "anchor", "workflowSelected", "identityProtected",
                      "rejectionHistory", "metadataStale", "ambiguousPhotoId", "qualityEligible"):
            with self.subTest(field=field):
                old = self.audit[0][field]
                self.audit[0][field] = field != "qualityEligible"
                self.assertEqual(self.query()["candidateDecision"]["decision"], "hold")
                self.audit[0][field] = old

    def test_pair_labels_never_supply_positive_destination_and_negative_is_a_veto(self):
        before = self.query()
        self.ledger["pairs"] = [{"photoIds": ["q", "a"], "label": "same"}]
        self.assertEqual(self.query(), before)
        for label in ("different", "uncertain"):
            self.ledger["pairs"][0]["label"] = label
            row = self.query()
            self.assertEqual(row["candidateDecision"]["decision"], "hold")
            self.assertIn(label, row["candidateDecision"]["reason"])
            self.assertEqual(row["candidateDecision"]["sharedPolicyDecision"]["decision"], "move")

    def test_neither_review_and_subgroup_blockers_cannot_move(self):
        for kind in ("neither", "review", "support"):
            with self.subTest(kind=kind):
                self.setUp()
                if kind == "neither":
                    self.ledger["unresolved"] = [{"photoId": "q"}]
                elif kind == "review":
                    self.evidence["rows"][0]["hold"] = "review-placement-hold"
                else:
                    self.evidence["rows"][0]["topCandidates"][0]["blockers"] = ["insufficient-independent-reference-support"]
                self.assertEqual(self.query()["candidateDecision"]["decision"], "hold")

    def test_reference_repair_is_copy_only_and_confirmed_intent_cannot_be_removed(self):
        before = copy.deepcopy(self.candidate)
        self.ledger["referenceProposals"] = [{
            "folder": "Models/Target", "photoId": "a", "wasReference": True, "referenceUse": "withdraw-in-shadow",
        }]
        repaired = subject.repaired_references(self.candidate, self.ledger)
        self.assertEqual(repaired["identities"][1]["referencePhotoIds"], ["b", "c", "d"])
        self.assertEqual(self.candidate, before)
        self.candidate["identities"][1]["referenceEvidence"] = {"construction": "confirmed-character-intent"}
        with self.assertRaisesRegex(ValueError, "confirmed-character"):
            subject.repaired_references(self.candidate, self.ledger)

    def test_conservation_placement_and_duplicate_checks(self):
        self.evidence["rows"].pop()
        with self.assertRaisesRegex(ValueError, "population differs"):
            self.rows()
        self.setUp()
        self.audit[0]["destination"] = "Models/Other/gallery/q.jpg"
        with self.assertRaisesRegex(ValueError, "placement binding"):
            self.rows()
        self.setUp()
        self.evidence["rows"].append(self.evidence["rows"][0])
        with self.assertRaisesRegex(ValueError, "unique stable"):
            self.rows()

    def test_reference_effects_order_and_inputs_preserved(self):
        before = copy.deepcopy((self.run, self.candidate, self.evidence))
        repaired = copy.deepcopy(self.evidence)
        repaired["rows"][0]["topCandidates"][0]["subgroupScore"] = .2
        result = subject.compare(self.candidate, self.evidence, repaired, self.run, self.ledger)
        self.assertEqual(result["summary"]["referenceRepairChangedOutcomes"], 1)
        self.assertEqual(before, (self.run, self.candidate, self.evidence))
        self.evidence["rows"].reverse()
        repaired["rows"].reverse()
        self.run["photos"].reverse()
        self.run["finalMembershipAudit"]["rows"].reverse()
        self.assertEqual(result, subject.compare(self.candidate, self.evidence, repaired, self.run, self.ledger))

    def test_render_is_photo_review_and_describes_incomplete_rebase(self):
        page = cli.render({"cases": [], "summary": {}}, {}, {}, {"summary": {"photoCount": 6}})
        self.assertIn("Automation actions and comparison evidence", page)
        self.assertIn("not a finished rebase", page)
        self.assertIn('id="query"', page)
        self.assertIn('id="export"', page)
        self.assertIn('href="candidate.json"', page)
        self.assertIn("Local Qwen/InternVL is not installed", page)
        self.assertIn("p,h1,h2,summary{overflow-wrap:anywhere}", page)
        self.assertIn("HOLD — KEEP CURRENT LOCATION", page)
        self.assertIn("Outside identity for comparison", page)
        self.assertNotIn("Suggested identity —", page)
        self.assertIn('id="action-scores"', page)
        self.assertIn('id="action-agreement"', page)
        self.assertIn('id="action-explanation"', page)
        self.assertIn("candidate-recommendation-evaluation", page)
        self.assertIn("not probabilities", page)

    def test_action_evaluation_is_bound_and_separate_from_identity_labels(self):
        packet = {
            "schemaVersion": 1, "packetSHA256": "fixture",
            "cases": [{"id": "c1", "photoId": "q", "currentReferenceId": "own",
                       "targetReferenceIds": ["a", "b"]}],
        }
        result = subject.compare(self.candidate, self.evidence, self.evidence, self.run, self.ledger)
        identity = {"schemaVersion": 1, "kind": "identity-fragment-answers", "packetSHA256": "fixture",
                    "decisions": [{"caseId": "c1", "currentMatch": "same", "targetMatch": "same",
                                   "pairs": [{"referencePhotoId": r, "label": "same"} for r in ("own", "a", "b")],
                                   "context": "helpful"}]}
        value = {
            "schemaVersion": 1, "kind": "candidate-recommendation-evaluation", "packetSHA256": "fixture",
            "candidateSHA256": fragment_review.digest(result), "identityAnswers": identity,
            "recommendations": [{"caseId": "c1", "judgment": "disagree",
                                 "reason": "Same person but retain current canonical folder."}],
        }
        self.assertEqual(cli.validate_evaluation(packet, result, value)["recommendations"], 1)
        self.assertEqual(value["identityAnswers"], identity)
        mutations = [
            {"packetSHA256": "wrong"}, {"candidateSHA256": "wrong"}, {"schemaVersion": True},
            {"recommendations": [{"caseId": "c1", "judgment": "disagree", "reason": " "}]},
            {"recommendations": value["recommendations"] * 2},
            {"recommendations": [{"caseId": "unknown", "judgment": "agree", "reason": ""}]},
            {"identityAnswers": {**identity, "packetSHA256": "other"}},
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                cli.validate_evaluation(packet, result, {**value, **mutation})
        self.assertEqual(cli.validate_evaluation(packet, result, {
            **value, "recommendations": [], "identityAnswers": {**identity, "decisions": []},
        })["recommendations"], 0)

    def test_prior_labels_render_without_prefilling_action_agreement_or_changing_packet(self):
        packet = {"cases": [], "summary": {}}
        prior = {"decisions": []}
        before = copy.deepcopy((packet, prior))
        page = cli.render(packet, {}, {}, {"summary": {}}, prior)
        self.assertIn('"priorAnswers": {"decisions": []}', page)
        self.assertIn("Action agreement is new and starts unevaluated", page)
        self.assertIn("let actionAnswers=new Map()", page)
        self.assertEqual((packet, prior), before)

    def test_packet_uses_fresh_queries_has_exact_cap_and_stable_selection(self):
        run = {"photos": []}
        candidate = {"identities": []}
        vectors, rows = {}, []
        for i in range(12):
            ids = [f"{i}-{kind}" for kind in ("query", "own", "near", "edge")]
            for n, pid in enumerate(ids):
                run["photos"].append({"photoId": pid, "preparedSHA256": pid})
                vectors[pid] = np.asarray([1., n * .1])
                vectors[pid] /= np.linalg.norm(vectors[pid])
            current, target = f"Models/Source-{i}", f"Models/Target-{i}"
            candidate["identities"].extend([
                {"folder": current, "referencePhotoIds": [ids[1]]},
                {"folder": target, "referencePhotoIds": ids[2:]},
            ])
            rows.append({
                "photoId": ids[0], "currentFolder": current,
                "currentDestination": current + "/gallery/" + ids[0] + ".jpg",
                "tentativeAssociationFolder": target, "changedByReferenceRepair": False,
                "referenceControlAssociation": target,
                "candidateDecision": {"decision": "hold", "reason": "test"},
                "topCandidates": [{"folder": target, "referencePhotoIds": ids[2:]}],
            })
        ledger = {"pairs": [{"photoIds": ["0-query", "0-near"], "label": "same"}]}
        result = {"rows": rows, "limits": []}
        old_packet = {"cases": [{"currentFolder": "Models/Source-1", "targetFolder": "Models/Target-1"}]}
        packet = subject.packet(result, candidate, run, vectors, ledger, old_packet)
        self.assertEqual(len(packet["cases"]), 10)
        self.assertEqual(len(packet["usedPhotoIds"]), 40)
        self.assertFalse(any(c["photoId"] == "0-query" for c in packet["cases"]))
        self.assertFalse(any(c["currentFolder"] == "Models/Source-1" for c in packet["cases"]))
        rows.reverse()
        run["photos"].reverse()
        reversed_packet = subject.packet(result, candidate, run, vectors, ledger, old_packet)
        self.assertEqual(packet["cases"], reversed_packet["cases"])
        self.assertEqual(packet["usedPhotoIds"], reversed_packet["usedPhotoIds"])
        self.assertEqual(reversed_packet["evidenceSHA256"], fragment_review.digest(result))
        with self.assertRaisesRegex(ValueError, "insufficient new visual coverage"):
            subject.packet(result, candidate, run, vectors, ledger, old_packet, max_photos=20)

    def test_real_scorer_to_shared_policy_without_positive_answers(self):
        from tools.art.likeness_library.tests import test_fragment_evidence as fixtures
        fixture = fixtures.FragmentEvidenceTests()
        fixture.setUp()
        fixture.add_photo("q", fixtures.angle(0))
        fixture.add_photo("own", fixtures.angle(90))
        fixture.add_photo("r1", fixtures.angle(-15), "Models/Target")
        fixture.add_photo("r2", fixtures.angle(15), "Models/Target")
        fixture.add_identity("source", "Models/Source", ["own"])
        fixture.add_identity("target", "Models/Target", ["r1", "r2"])
        candidate, run = fixture.candidate(), fixture.receipt()
        audit = []
        for photo in run["photos"]:
            row = copy.deepcopy(self.audit[0])
            row.update(photo)
            audit.append(row)
        run["finalMembershipAudit"] = {"rows": audit}
        evidence = cli.fragment_evidence.evaluate(candidate, run, fixture.vectors, {"pairs": []})
        result = subject.compare(candidate, evidence, evidence, run, self.ledger)
        query = next(r for r in result["rows"] if r["photoId"] == "q")
        self.assertEqual(query["candidateDecision"]["decision"], "move")
        self.assertEqual(query["proposedDestination"], "Models/Target/gallery")
        self.assertEqual(query["execution"], "not-authorized")
        self.assertEqual(result["summary"]["executedMoves"], 0)

    def test_preview_has_no_scoring_and_apply_repeat_check_preserve_receipt(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            root = pathlib.Path(name)
            out = root / "report"
            original = root / "original.jpg"
            original.write_bytes(b"fixture-source")
            packet = {
                "cases": [], "usedPhotoIds": [], "summary": {}, "kind": "identity-fragment-review",
                "evidenceSHA256": fragment_review.digest(subject.compare(
                    self.candidate, self.evidence, self.evidence, self.run, self.ledger,
                )),
            }
            packet["packetSHA256"] = fragment_review.digest(packet)
            loaded = (packet, self.ledger, self.candidate, self.run, {}, {}, root / "local.safetensors", {})
            args = ["--source", str(root), "--out", str(out)]
            images = {"q": {"path": str(original), "sha256": cli.shadow.digest(original)}}
            with mock.patch.object(cli, "load", return_value=loaded), \
                    mock.patch.object(cli, "output_path", return_value=out), \
                    mock.patch.object(cli, "codes", return_value={}), \
                    mock.patch.object(cli.fragment_evidence, "evaluate", return_value=self.evidence) as score, \
                    mock.patch.object(cli.candidate_replay, "packet", return_value=packet), \
                    mock.patch.object(cli.appearance_context, "measure", return_value={"photos": {}}), \
                    mock.patch.object(cli.review_packet, "image_assets", return_value=(images, {})):
                self.assertEqual(cli.main(args + ["--dry-run"]), 0)
                self.assertFalse(out.exists())
                score.assert_not_called()
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                self.assertEqual(score.call_count, 3)
                self.assertTrue(all(call.args[-1] == {"pairs": []} for call in score.call_args_list))
                receipt = (out / "receipt.json").read_bytes()
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                self.assertEqual(cli.main(args + ["--check"]), 0)
                self.assertEqual(score.call_count, 3)
                self.assertEqual(receipt, (out / "receipt.json").read_bytes())
                data = json.loads(receipt)
                self.assertEqual(data["directPairLabelsInScoring"], 0)
                republished = root / "republished"
                with mock.patch.object(cli, "output_path", return_value=republished), \
                        mock.patch.object(cli.appearance_context, "measure") as inference:
                    publish_args = ["--source", str(root), "--out", str(republished),
                                    "--reuse-result", str(out)]
                    self.assertEqual(cli.main(publish_args + ["--dry-run"]), 0)
                    self.assertFalse(republished.exists())
                    self.assertEqual(cli.main(publish_args + ["--apply"]), 0)
                    self.assertEqual(cli.main(publish_args[:4] + ["--check"]), 0)
                    self.assertEqual(score.call_count, 3)
                    inference.assert_not_called()
                    fresh = json.loads((republished / "receipt.json").read_bytes())
                    self.assertEqual(fresh["scoringPasses"], 0)
                    self.assertEqual((out / "candidate.json").read_bytes(),
                                     (republished / "candidate.json").read_bytes())
                    evaluation = root / "evaluation.json"
                    identity = {
                        "schemaVersion": 1, "kind": "identity-fragment-answers",
                        "packetSHA256": packet["packetSHA256"], "decisions": [],
                    }
                    evaluation.write_text(json.dumps({
                        "schemaVersion": 1, "kind": "candidate-recommendation-evaluation",
                        "packetSHA256": packet["packetSHA256"],
                        "candidateSHA256": fragment_review.digest(json.loads((republished / "candidate.json").read_bytes())),
                        "identityAnswers": identity, "recommendations": [],
                    }))
                    self.assertEqual(cli.main(publish_args[:4] + ["--check", "--evaluation", str(evaluation)]), 0)
                    prior = root / "prior.json"
                    prior.write_text(json.dumps(identity))
                    with_prior = root / "with-prior"
                    with mock.patch.object(cli, "output_path", return_value=with_prior):
                        prior_args = [
                            "--source", str(root), "--out", str(with_prior), "--reuse-result", str(out),
                            "--prior-answers", str(prior),
                        ]
                        self.assertEqual(cli.main(prior_args + ["--apply"]), 0)
                        self.assertEqual(cli.main(prior_args[:4] + ["--check"]), 0)
                        self.assertIn(str(prior), json.loads((with_prior / "receipt.json").read_bytes())["inputs"])
                        prior.write_text("{}")
                        self.assertEqual(cli.main(prior_args[:4] + ["--check"]), 1)
                    self.assertEqual(score.call_count, 3)
                    inference.assert_not_called()
                with mock.patch.object(cli, "codes", return_value={"analysis.py": "changed"}):
                    with self.assertRaisesRegex(ValueError, "helper code changes"):
                        cli.reuse(out, {})
                (out / "candidate.json").write_text("{}")
                self.assertEqual(cli.main(args + ["--check"]), 1)


if __name__ == "__main__":
    unittest.main()
