"""Fragment review semantics, bounded coverage and non-face crop safeguards."""
import copy
import json
import pathlib
import tempfile
import unittest
from unittest import mock
import argparse
import types

import numpy as np
from PIL import Image

from tools.art import likeness_fragment_trial as cli
from tools.art.likeness_library import appearance_context, fragment_report, fragment_review


class FragmentReviewTests(unittest.TestCase):
    def setUp(self):
        names = [
            "Prospects/Zoe Mallory", "Potentials/Viola Lujan", "Models/Ruby Vale",
            "Prospects/Xena Eden", "Prospects/Francesca Oakes",
            "Models/Quinn Duval", "Sisters/Drakness", "Models/Mara Savannah",
            "Sisters/Drakniss", "Models/Sabine Santos", "Sisters/Draknora",
            *[f"Models/Other{i}" for i in range(12)],
        ]
        rng = np.random.default_rng(42)
        self.candidate = {"rows": [], "identities": []}
        self.evidence = {"rows": []}
        self.run = {"photos": []}
        self.vectors = {}
        for i, folder in enumerate(names):
            ids = [f"p{i}-{j}" for j in range(4)]
            self.candidate["identities"].append({"folder": folder, "referencePhotoIds": ids})
            for pid in ids:
                target = names[(i + 1) % len(names)]
                v = rng.normal(size=8)
                self.vectors[pid] = v / np.linalg.norm(v)
                self.run["photos"].append({"photoId": pid, "preparedSHA256": pid})
                self.candidate["rows"].append({
                    "photoId": pid, "currentFolder": folder, "candidateFolder": target,
                })
                self.evidence["rows"].append({
                    "photoId": pid, "currentFolder": folder,
                    "topCandidates": [{"folder": target, "referencePhotoIds": []}],
                })
        self.prior = {"observations": []}
        self.packet = fragment_review.build(
            self.candidate, self.evidence, self.run, self.vectors, self.prior,
        )

    def test_packet_budget_order_and_independent_labels(self):
        before = copy.deepcopy((self.candidate, self.evidence, self.run, self.prior))
        self.assertTrue(30 <= len(self.packet["usedPhotoIds"]) <= 40)
        self.assertGreaterEqual(len(self.packet["cases"]), 6)
        for case in self.packet["cases"]:
            self.assertNotIn(case["photoId"], [case["currentReferenceId"], *case["targetReferenceIds"]])
            self.assertNotEqual(case["currentFolder"], case["targetFolder"])
            self.assertNotIn("decisions", case)
        self.assertEqual(before, (self.candidate, self.evidence, self.run, self.prior))
        reverse = copy.deepcopy(self.candidate)
        reverse["rows"].reverse()
        reverse["identities"].reverse()
        reversed_packet = fragment_review.build(reverse, self.evidence, self.run, self.vectors, self.prior)
        for key in ("cases", "usedPhotoIds", "summary", "limits"):
            self.assertEqual(self.packet[key], reversed_packet[key])
        with self.assertRaisesRegex(ValueError, "30-40"):
            fragment_review.build(self.candidate, self.evidence, self.run, self.vectors, self.prior, max_photos=41)

    def test_ingest_is_identity_only_and_strictly_bound(self):
        row = self.candidate["rows"][0]
        feedback = {
            "schemaVersion": 1, "kind": "realignment-hypothesis-assessments",
            "candidateSHA256": fragment_review.digest(self.candidate),
            "assessments": [{key: value for key, value in {
                "photoId": row["photoId"], "candidateFolder": row["candidateFolder"], "judgment": "support",
            }.items()}],
        }
        before = copy.deepcopy(feedback)
        result = fragment_review.ingest(self.candidate, feedback)
        self.assertEqual(result["counts"], {"support": 1})
        self.assertEqual(result["observations"], feedback["assessments"])
        self.assertNotIn("pairs", result)
        self.assertEqual(feedback, before)
        for change in (
            {"candidateSHA256": "wrong"}, {"schemaVersion": True},
            {"assessments": feedback["assessments"] * 2},
            {"assessments": [{**feedback["assessments"][0], "candidateFolder": "Wrong/Folder"}]},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                fragment_review.ingest(self.candidate, {**feedback, **change})

    def answer(self):
        case = self.packet["cases"][0]
        return {
            "schemaVersion": 1, "kind": "identity-fragment-answers",
            "packetSHA256": self.packet["packetSHA256"], "decisions": [{
                "caseId": case["id"], "currentMatch": "same", "targetMatch": "same",
                "context": "uncertain", "pairs": [
                    {"referencePhotoId": pid, "label": "different" if i else "same"}
                    for i, pid in enumerate(dict.fromkeys([case["currentReferenceId"], *case["targetReferenceIds"]]))
                ],
            }],
        }

    def test_both_identities_can_match_while_reference_exceptions_differ(self):
        export = self.answer()
        self.assertEqual(fragment_review.validate_answers(self.packet, export)["answered"], 1)
        self.assertEqual(fragment_review.validate_answers(self.packet, {**export, "decisions": []})["answered"], 0)
        for field in ("currentMatch", "targetMatch", "context"):
            bad = copy.deepcopy(export)
            bad["decisions"][0][field] = "unreviewed"
            with self.subTest(field=field), self.assertRaises(ValueError):
                fragment_review.validate_answers(self.packet, bad)
        for pairs in ([], export["decisions"][0]["pairs"] * 2,
                      [{"referencePhotoId": "unknown", "label": "same"}],
                      [{"referencePhotoId": [], "label": "same"}]):
            bad = copy.deepcopy(export)
            bad["decisions"][0]["pairs"] = pairs
            with self.assertRaises(ValueError):
                fragment_review.validate_answers(self.packet, bad)
        bad = {**export, "packetSHA256": "wrong"}
        with self.assertRaisesRegex(ValueError, "mismatch"):
            fragment_review.validate_answers(self.packet, bad)

    def test_context_crop_excludes_saved_face_and_refuses_missing_pixels(self):
        image = Image.new("RGB", (800, 1000))
        box = [.4, .1, .2, .2]
        crop = appearance_context.crop_region(image, box)
        self.assertGreater(crop[1], (box[1] + box[3]) * image.height)
        self.assertGreater(crop[2], crop[0])
        self.assertLessEqual(crop[3], image.height)
        self.assertIsNone(appearance_context.crop_region(image, [.4, .8, .2, .19]))
        for box in (None, [-.1, 0, .2, .2], [0, 0, 0, .2], [0, 0, float("nan"), .2]):
            with self.subTest(box=box), self.assertRaises(ValueError):
                appearance_context.crop_region(image, box)

    def test_context_requires_explicit_existing_checkpoint_before_loading_models(self):
        with self.assertRaisesRegex(ValueError, "local"):
            appearance_context.measure(self.packet, {}, {}, pathlib.Path("missing.safetensors"))

    def test_context_measures_only_bound_local_pixels_with_explicit_missingness(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            root = pathlib.Path(name)
            checkpoint = root / "local.safetensors"
            checkpoint.write_bytes(b"fixture-not-real-weights")
            run = {"workingRoot": str(root), "photos": [], "publishedFiles": []}
            cache = {"emb": {}}
            for pid, box in (("visible", [.4, .1, .2, .2]), ("missing", [.4, .8, .2, .19])):
                path = root / (pid + ".png")
                Image.new("RGB", (800, 1000), "blue").save(path)
                run["photos"].append({"photoId": pid, "destination": path.name, "preparedSHA256": pid})
                run["publishedFiles"].append({"path": path.name, "sha256": cli.shadow.digest(path)})
                cache["emb"][pid] = {"alignmentEvidence": {"sourceSha256": pid}, "box": box}
            packet = {"usedPhotoIds": ["visible", "missing"], "cases": [{
                "id": "test", "photoId": "visible", "currentReferenceId": "missing", "targetReferenceIds": [],
            }]}
            model, transform = mock.MagicMock(), mock.MagicMock()
            model.encode_image.return_value.float.return_value.cpu.return_value.numpy.return_value = np.array([[3., 4.]])
            factory = mock.Mock(return_value=(model, None, transform))
            torch = mock.MagicMock(__version__="fixture")
            torch.get_num_threads.return_value = 8
            with mock.patch.dict("sys.modules", {
                "open_clip": types.SimpleNamespace(create_model_and_transforms=factory), "torch": torch,
            }), mock.patch.object(appearance_context.importlib.metadata, "version", return_value="fixture"):
                result = appearance_context.measure(packet, run, cache, checkpoint)
            factory.assert_called_once_with("ViT-B-32", pretrained=str(checkpoint), device="cpu")
            self.assertEqual(model.encode_image.call_count, 1)
            self.assertEqual(result["summary"], {"photoCount": 2, "measuredCount": 1, "unavailableCount": 1})
            self.assertEqual(result["photos"]["visible"]["vector"], [.6, .8])
            self.assertEqual(result["photos"]["missing"]["status"], "unavailable")
            self.assertIsNone(result["pairs"][0]["similarity"])
            self.assertEqual(result["model"]["sha256"], cli.shadow.digest(checkpoint))

    def test_report_is_guided_explicit_and_escaped(self):
        page = fragment_report.render(self.packet, {}, {"limits": ["<script>unsafe</script>"], "model": {}})
        for item in ("Both — same person split", "Neither", "currentMatch", "targetMatch", "pairs",
                     "Label every pictured reference", "No group merges", "background", "Next / skip",
                     "packetSHA256", "Import refused", "unreviewed", "beforeunload"):
            self.assertIn(item, page)
        self.assertNotIn("<script>unsafe</script>", page)
        self.assertIn("\\u003cscript>", page)
        self.assertNotIn("{{DATA}}", page)

    def test_cli_rejects_bad_scope_and_answers_without_check(self):
        args = [
            "--experiment", str(pathlib.Path.cwd()), "--candidate", str(pathlib.Path.cwd()),
            "--feedback", str(pathlib.Path.cwd() / "feedback.json"),
            "--context-checkpoint", str(pathlib.Path.cwd() / "model.safetensors"),
            "--out", str(pathlib.Path.cwd() / "reports" / "test"),
        ]
        self.assertEqual(cli.main(args + ["--max-photos", "41"]), 1)
        self.assertEqual(cli.main(args + ["--answers", str(pathlib.Path.cwd() / "answers.json")]), 1)

    def test_receipt_detects_output_and_parameter_tampering(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            out = pathlib.Path(name)
            objects = {"packet.json": self.packet, "evidence.json": {}, "context.json": {},
                       "prior-feedback.json": {}, "display.json": {}}
            outputs = {}
            for file, value in objects.items():
                (out / file).write_text(json.dumps(value))
                outputs[file] = cli.shadow.digest(out / file)
            (out / "index.html").write_text("test")
            outputs["index.html"] = cli.shadow.digest(out / "index.html")
            (out / "receipt.json").write_text(json.dumps({
                "inputs": {}, "code": {}, "maxPhotos": 40, "outputs": outputs,
            }))
            with mock.patch.object(cli, "code_bindings", return_value={}):
                self.assertEqual(cli.check(out, {}, 40), self.packet)
                with self.assertRaisesRegex(ValueError, "parameters"):
                    cli.check(out, {}, 39)
                (out / "index.html").write_text("changed")
                with self.assertRaisesRegex(ValueError, "output changed"):
                    cli.check(out, {}, 40)

    def test_baseline_chain_is_rehashed_not_merely_trusted(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            root = pathlib.Path(name)
            experiment = root / "experiment"
            experiment.mkdir()
            candidate = root / "candidate"
            candidate.mkdir()
            label = root / "effective-labels.json"
            label.write_text("{}")
            for path in (experiment / "receipt.json", candidate / "realignment.json",
                         candidate / "evaluation.json", root / "feedback.json", root / "model.safetensors"):
                path.write_text("{}")
            bound = {str(path): cli.shadow.digest(path) for path in (label, experiment / "receipt.json")}
            (candidate / "receipt.json").write_text(json.dumps({"inputs": bound, "compareOrder": True}))
            args = argparse.Namespace(candidate=candidate, experiment=experiment,
                                      feedback=root / "feedback.json", context_checkpoint=root / "model.safetensors")
            with mock.patch.object(cli.baseline_cli, "check"):
                inputs, selected = cli.verify_inputs(args)
                self.assertEqual(selected, label)
                self.assertEqual(inputs[str(label)], bound[str(label)])
                label.write_text("changed")
                with self.assertRaisesRegex(ValueError, "baseline input changed"):
                    cli.verify_inputs(args)

    def test_launcher_preview_apply_repeat_check_and_answers_lifecycle(self):
        from tools.art.likeness_library import fragment_evidence
        with tempfile.TemporaryDirectory(dir=pathlib.Path.cwd() / "tmp") as name:
            root = pathlib.Path(name)
            candidate = {**self.candidate, "appearances": []}
            (root / "realignment.json").write_text(json.dumps(candidate))
            (root / "likeness-cache.json").write_text("{}")
            label = root / "effective-labels.json"
            label.write_text("{}")
            feedback = root / "feedback.json"
            feedback.write_text(json.dumps({
                "schemaVersion": 1, "kind": "realignment-hypothesis-assessments",
                "candidateSHA256": fragment_review.digest(candidate), "assessments": [],
            }))
            source = root / "source.png"
            Image.new("RGB", (100, 100)).save(source)
            images = {pid: {"path": str(source), "sha256": cli.shadow.digest(source)}
                      for pid in self.packet["usedPhotoIds"]}
            context = {"summary": {}, "photos": {}, "pairs": [], "limits": [], "model": {}}
            out = root / "report"
            args = ["--experiment", str(root), "--candidate", str(root), "--feedback", str(feedback),
                    "--context-checkpoint", str(root / "model.safetensors"), "--out", str(out)]
            with mock.patch.object(cli, "verify_inputs", return_value=({}, label)), \
                    mock.patch.object(cli, "code_bindings", return_value={}), \
                    mock.patch.object(cli, "output_path", return_value=out), \
                    mock.patch.object(cli.review_packet, "load_experiment",
                                      return_value=(self.run, self.vectors, {}, {"sourceRun": str(root)})), \
                    mock.patch.object(fragment_evidence, "evaluate", return_value={**self.evidence, "summary": {}}), \
                    mock.patch.object(cli.review_packet, "image_assets", return_value=(images, {})), \
                    mock.patch.object(cli.appearance_context, "measure", return_value=context) as measure, \
                    mock.patch.object(cli.importlib.metadata, "version", return_value="fixture"):
                self.assertEqual(cli.main(args + ["--dry-run"]), 0)
                self.assertFalse(out.exists())
                measure.assert_not_called()
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                self.assertEqual(measure.call_count, 1)
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                self.assertEqual(cli.main(args + ["--check"]), 0)
                self.assertEqual(measure.call_count, 1)
                packet = json.loads((out / "packet.json").read_bytes())
                answer_path = root / "answers.json"
                answer_path.write_text(json.dumps({
                    "schemaVersion": 1, "kind": "identity-fragment-answers",
                    "packetSHA256": packet["packetSHA256"], "decisions": [],
                }))
                self.assertEqual(cli.main(args + ["--check", "--answers", str(answer_path)]), 0)


if __name__ == "__main__":
    unittest.main()
