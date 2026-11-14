import copy
import base64
import gzip
import json
import pathlib
import tempfile
import unittest
from unittest import mock

import numpy as np

from tools.art import likeness_entrance_trial as cli
from tools.art.likeness_library import entrance_trial as trial
from tools.art.likeness_library.tests import test_membership_reassessment as fixtures


class EntranceTrialTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.MembershipReassessmentTests()
        fixture.setUp()
        self.run, self.vectors, self.ledger = fixture.run, fixture.vectors, fixture.ledger
        self.state = fixture.build()
        for view in self.state["appearances"]:
            view["frozenReferencePhotoIds"] = [p for p in view["frozenReferencePhotoIds"] if p != "p5"]
        self.recipe = copy.deepcopy(trial.recipes()[1])

    def evidence(self):
        return trial.Evidence(self.state, self.run, self.vectors, self.ledger)

    def build(self):
        return trial.run_variant(self.evidence(), self.recipe)

    def row(self, result, pid="p5"):
        return next(r for r in result["rows"] if r["photoId"] == pid)

    def test_all_recipes_follow_each_axis_of_ladder(self):
        for recipe in trial.recipes():
            trial.validate_recipe(recipe)
            for axis in ("admission", "core", "retain", "margin"):
                self.assertGreaterEqual(recipe[axis]["Angels"], recipe[axis]["Models"])
        self.recipe["admission"]["Models"] = .9
        with self.assertRaisesRegex(ValueError, "ladder inverted"):
            self.build()

    def test_nonfinite_or_too_weak_support_rejected(self):
        for key in ("joinSupport", "coreSupport", "retainSupport"):
            invalid = copy.deepcopy(self.recipe)
            invalid[key] = 1
            with self.assertRaises(ValueError):
                trial.validate_recipe(invalid)
        self.recipe["core"]["Models"] = float("nan")
        with self.assertRaises(ValueError):
            trial.validate_recipe(self.recipe)

    def test_reference_floor_does_not_inherit_automatic_protection(self):
        for i in range(6):
            vector = np.zeros(9)
            vector[0], vector[i+1] = .65, np.sqrt(1-.65**2)
            self.vectors[f"p{i}"] = vector
        strict = trial.run_variant(self.evidence(), trial.recipes()[0])
        ordinary = self.build()
        self.assertIsNone(self.row(strict)["own"]["activeScore"])
        self.assertIsNotNone(self.row(ordinary)["own"]["activeScore"])
        self.assertEqual(self.run["policy"]["protection"]["automatic"]["minimumOwnCoreSimilarity"], .55)

    def test_low_noncore_can_be_retained_without_new_join_or_promotion(self):
        vector = np.zeros(9)
        vector[0], vector[8] = .35, np.sqrt(1-.35**2)
        self.vectors["p5"] = vector
        self.recipe["growth"] = True
        row = self.row(self.build())
        self.assertEqual(row["membership"], "retention-compatible-not-identity-confirmation")
        self.assertLess(row["own"]["activeScore"], self.recipe["admission"]["Models"])
        self.assertIsNone(row["proposalPersonId"])
        self.assertFalse(row["corePromotionStaged"])
        self.assertFalse(row["logicalRelease"])

    def test_reference_starvation_is_not_a_release(self):
        self.recipe["core"] = dict.fromkeys(trial.LADDER, .99)
        row = self.row(self.build())
        self.assertEqual(row["membership"], "comparison-unavailable")
        self.assertFalse(row["logicalRelease"])
        self.assertFalse(row["releaseCandidate"])

    def test_incomplete_qualification_suppresses_all_automatic_proposals(self):
        evidence = self.evidence()
        with mock.patch.object(evidence, "qualify", side_effect=lambda view, refs, recipe: (refs, False)):
            result = trial.run_variant(evidence, self.recipe)
        self.assertFalse(result["summary"]["stable"])
        self.assertEqual(result["summary"]["proposals"], 0)
        self.assertFalse(any(row["logicalRelease"] for row in result["rows"]))

    def test_vectorized_scores_match_leave_one_out_measurement(self):
        evidence = self.evidence()
        inventory = {v["appearanceId"]: v["original"] for v in evidence.views}
        scores = evidence.scores(inventory)
        for i, pid in enumerate(evidence.ids):
            for j, view in enumerate(evidence.views):
                direct = evidence.measure(pid, inventory[view["appearanceId"]])
                if direct is None:
                    self.assertTrue(np.isnan(scores[i, j]))
                else:
                    self.assertAlmostEqual(scores[i, j], direct, places=12)

    def test_measured_low_membership_released_without_physical_move(self):
        self.vectors["p5"] = self.vectors["outlier"].copy()
        row = self.row(self.build())
        self.assertEqual(row["membership"], "below-retention-range")
        self.assertTrue(row["logicalRelease"])
        self.assertEqual(self.build()["summary"]["installedMoves"], 0)

    def test_locked_low_reference_can_lose_influence_without_moving(self):
        row = next(r for r in self.state["rows"] if r["photoId"] == "p5")
        row["placementBlocks"] = ["protected"]
        self.vectors["p5"] = self.vectors["outlier"].copy()
        result = self.row(self.build())
        self.assertTrue(result["releaseCandidate"])
        self.assertFalse(result["logicalRelease"])
        self.assertIn("physical-action-locked", result["entranceBlockers"])

    def test_growth_uses_original_frozen_witnesses_at_next_boundary(self):
        self.recipe["growth"] = True
        e = self.evidence()
        result = trial.run_variant(e, self.recipe)
        first = result["boundaries"][0]
        self.assertTrue(first["corePromotionWitnesses"])
        witness = next(r for r in first["corePromotionWitnesses"] if r["photoId"] == "p5")
        self.assertNotIn("p5", witness["originalBaseWitnessPhotoIds"])
        view = next(v for v in e.views if v["appearanceId"] == witness["appearanceId"])
        self.assertTrue(set(witness["originalBaseWitnessPhotoIds"]) <= set(view["original"]))
        self.assertGreater(first["nextReferenceCount"], first["referenceCount"])
        self.assertGreaterEqual(len(result["boundaries"]), 2)
        self.assertEqual(result["summary"]["automaticProtectionAcquired"], 0)
        self.assertEqual(result["summary"]["addedReferenceOccurrences"], 1)

    def test_duplicate_content_and_correlated_views_cannot_certify_reference(self):
        for photo in self.run["photos"][:4]:
            photo["preparedSHA256"] = "equal-content"
        result = self.row(self.build())
        self.assertIsNone(result["own"]["activeScore"])
        self.setUp()
        for pid in ("p1", "p2", "p3", "p4"):
            self.vectors[pid] = self.vectors["p0"].copy()
        self.assertIsNone(self.row(self.build())["own"]["activeScore"])

    def test_negative_and_uncertain_veto_without_positive_discovery(self):
        for label in ("different", "uncertain"):
            self.ledger["pairs"] = [{"photoIds": ["p0", "p5"], "label": label}]
            result = self.build()
            self.assertIsNone(self.row(result)["proposalPersonId"])
            self.assertEqual(result["summary"]["exactPairControls"][label+"Coassigned"], 0)
        self.ledger["pairs"] = []
        control = self.build()
        self.ledger["pairs"] = [{"photoIds": ["p0", "p5"], "label": "same"}]
        positive = self.build()
        self.assertEqual(control["references"], positive["references"])
        self.assertEqual(control["rows"], positive["rows"])

    def test_inactive_original_hypothesis_remains_a_competitor(self):
        evidence = self.evidence()
        original = evidence.original_scores.copy()
        result = trial.run_variant(evidence, self.recipe)
        self.assertTrue(np.array_equal(original, evidence.original_scores, equal_nan=True))
        # A reference-starved outlier view remains in the original matrix,
        # not removed to make the other view win more easily.
        index = evidence.cache.indices["p5"]
        self.assertTrue(any(np.isfinite(value) for value in evidence.original_scores[index]))
        self.assertEqual(len(result["references"]), len(evidence.views))

    def test_reverse_order_and_no_source_mutation(self):
        original = copy.deepcopy(self.state)
        output = trial.run_sweep(self.state, self.run, self.vectors, self.ledger, variants=[self.recipe])
        self.state["rows"].reverse()
        self.state["appearances"].reverse()
        reverse = trial.run_sweep(self.state, self.run, dict(reversed(list(self.vectors.items()))),
                                  self.ledger, variants=[self.recipe])
        self.assertEqual(cli.semantic(output), cli.semantic(reverse))
        self.state["rows"].reverse()
        self.state["appearances"].reverse()
        self.assertEqual(original, self.state)
        self.assertEqual(len(output["variants"][0]["rows"]), len(self.state["rows"]))

    def test_report_contains_explanations_and_inline_filename_links(self):
        self.run["workingRoot"] = str(pathlib.Path.cwd())
        result = trial.run_sweep(self.state, self.run, self.vectors, self.ledger, variants=[self.recipe])
        text = cli.render(result, self.state, self.run)
        self.assertIn("Comparison unavailable means the experiment needs better evidence.", text)
        self.assertIn("No installed photos or settings changed. No review required now.", text)
        self.assertIn('img.src=src.href', text)
        self.assertIn("original filename link retained", text)
        self.assertIn('type="application/octet-stream"', text)
        self.assertIn('el("variant").value=result.defaultVariant', text)
        self.assertIn("Unable to load experiment display", text)
        self.assertIn('id="regressions"', text)
        self.assertIn("Preserved original names", text)
        payload = cli.display_payload(result, {"p0": {"filename": "fixture.jpg"}})
        decoded = json.loads(gzip.decompress(base64.b64decode(payload)))
        self.assertEqual(decoded["result"]["defaultVariant"], "ordered-middle")
        self.assertEqual(decoded["sources"]["p0"]["filename"], "fixture.jpg")
        for projected, original in zip(decoded["result"]["variants"][0]["rows"], result["variants"][0]["rows"]):
            self.assertEqual(projected["photoId"], original["photoId"])
            self.assertEqual(projected["membership"], original["membership"])
            self.assertEqual(projected["proposalPersonId"], original["proposalPersonId"])
            if projected["own"]:
                self.assertEqual(projected["own"]["activeScore"], original["own"]["activeScore"])
                self.assertEqual(projected["own"]["originalScore"], original["own"]["originalScore"])
                self.assertLessEqual(len(projected["own"]["referencePhotoIds"]), 4)

    def test_launcher_preview_apply_repeat_check_and_tamper(self):
        with tempfile.TemporaryDirectory(dir=cli.ROOT / "tmp") as name:
            root = pathlib.Path(name)
            source, out = root / "source", root / "report"
            source.mkdir()
            self.run["workingRoot"] = str(root)
            self.run["publishedFiles"] = []
            for photo in self.run["photos"]:
                path = cli.review_packet.safe_path(root, photo["destination"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture image bytes, not decoded")
                self.run["publishedFiles"].append({
                    "path": photo["destination"], "sha256": cli.shadow.digest(path),
                })
            loaded = (self.state, self.run, self.vectors, {}, self.ledger, root / "unused-model", {})
            args = ["--source", str(source), "--out", str(out)]
            with mock.patch.object(cli, "output_path", side_effect=lambda path: path), \
                    mock.patch.object(cli.diagnostics, "load", return_value=loaded), \
                    mock.patch.object(trial, "recipes", return_value=[self.recipe]):
                self.assertEqual(cli.main(args+["--dry-run"]), 0)
                self.assertFalse(out.exists())
                self.assertEqual(cli.main(args+["--apply"]), 0)
                self.assertTrue(json.loads((out / "receipt.json").read_bytes())["reverseVerified"])
                reuse_out = root / "republished"
                reuse_args = ["--source", str(source), "--out", str(reuse_out),
                              "--reuse-result", str(out)]
                with mock.patch.object(trial, "run_sweep", side_effect=AssertionError("unexpected rescoring")):
                    self.assertEqual(cli.main(args+["--apply"]), 0)
                    self.assertEqual(cli.main(args+["--check"]), 0)
                    self.assertEqual(cli.main(reuse_args+["--dry-run"]), 0)
                    self.assertEqual(cli.main(reuse_args+["--apply"]), 0)
                    self.assertEqual(cli.main(reuse_args+["--check"]), 0)
                self.assertEqual((out / "trial.json").read_bytes(), (reuse_out / "trial.json").read_bytes())
                original_receipt = json.loads((out / "receipt.json").read_bytes())
                original_code = copy.deepcopy(original_receipt["code"])
                original_receipt["code"][str(pathlib.Path(trial.__file__).resolve())] = "analysis-drift"
                (out / "receipt.json").write_text(json.dumps(original_receipt), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "analysis"):
                    cli.load_reuse(out, source, False)
                original_receipt["code"] = original_code
                (out / "receipt.json").write_text(json.dumps(original_receipt), encoding="utf-8")
                index = out / "index.html"
                original = index.read_bytes()
                index.write_bytes(b"changed")
                self.assertEqual(cli.main(args+["--check"]), 2)
                index.write_bytes(original)
                first_photo = self.run["photos"][0]
                cli.review_packet.safe_path(root, first_photo["destination"]).write_bytes(b"source drift")
                self.assertEqual(cli.main(args+["--check"]), 2)

    def test_menu_preserves_lean_and_exposes_distinct_experiment_choices(self):
        menu = (cli.ROOT / "bin" / "menu.cmd").read_text(encoding="utf-8")
        for key, label in (("LC", "leancontinue"), ("LG", "categorydiagnostics"), ("LE", "entrancetrial")):
            lines = [line for line in menu.splitlines() if line.startswith(f'if /i "%CH%"=="{key}"')]
            self.assertEqual(lines, [f'if /i "%CH%"=="{key}" goto {label}'])
        self.assertIn('--coalesce --dry-run', menu)


if __name__ == "__main__":
    unittest.main()
