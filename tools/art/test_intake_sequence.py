"""Offline bounded erase-before-residual comparisons; no model or filesystem access."""
import copy
import json
import pathlib
import sys
import unittest
from unittest import mock

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "workflows"))
from intake_library import pipeline  # noqa: E402


class SequenceTests(unittest.TestCase):
    def setUp(self):
        self.size = (400, 800)
        self.image = Image.new("RGB", self.size, (60, 80, 100))
        self.body = pipeline.clutter.solid((800, 400), [100, 100, 300, 800])
        self.person = {"mask": self.body, "box": [100, 100, 300, 800], "people": 1, "dropped": 0}
        self.row = {
            "eligibility": {"status": "usable", "faces": [[170., 100., 60., 70.]], "reason": "Test face."},
            "geometry": {"box": [0, 0, *self.size], "changed": False, "overlayDetected": True,
                         "reason": "No border.", "uiCropBox": None},
            "processing": {"final": "frozen-v16", "steps": [{"frozen": True}]},
        }
        for target, value in ((pipeline.subjects, self.person),):
            patcher = mock.patch.object(target, "detect", return_value=value)
            self.subject_detector = patcher.start()
            self.addCleanup(patcher.stop)
        panel = mock.patch.object(pipeline.geometry, "panel_box",
                                  side_effect=lambda image, faces, box: (box, "No panel."))
        panel.start()
        self.addCleanup(panel.stop)
        detector = mock.patch.object(pipeline.clutter, "detect", return_value=([], []))
        self.detector = detector.start()
        self.addCleanup(detector.stop)
        filler = mock.patch.object(pipeline.fill, "fill", side_effect=self.paint)
        self.filler = filler.start()
        self.addCleanup(filler.stop)

    @staticmethod
    def paint(image, mask):
        # Deliberately touches everything: the sequence must enforce the mask boundary.
        return Image.new("RGB", image.size, (128, 128, 128))

    def part(self, kind, box):
        return pipeline.clutter.part(kind, pipeline.clutter.solid((800, 400), box), "test uncertain shape")

    def run_sequence(self):
        before = copy.deepcopy(self.row)
        images = dict(pipeline.experimental_candidates(self.image, self.row))
        self.assertEqual({k: v for k, v in self.row.items() if k != "experiment"}, before)
        evidence = self.row["experiment"]
        json.dumps(evidence)
        self.assertIn(evidence["final"], images)
        self.assertEqual(evidence["policy"], pipeline.EXPERIMENT_POLICY)
        self.assertLessEqual(self.detector.call_count, 2)
        self.assertLessEqual(self.filler.call_count, 1)
        return images, evidence

    def test_screenshot_preserves_legs_and_default_v16_stays_lossy(self):
        bar = self.part("ui-card", [0, 700, 400, 780])
        faces = self.row["eligibility"]["faces"]
        default, _, notes = pipeline.second_crop(self.size, [bar], self.person, faces, (0, 0), screenshot=True)
        self.assertLess(default[3], 700)
        self.assertIn("app bar", notes[0])
        self.detector.return_value = ([bar], [])
        images, evidence = self.run_sequence()
        self.assertNotIn("residual-crop", images)
        self.assertEqual(images[evidence["final"]].height, 800)
        self.assertFalse(self.filler.called)
        self.assertEqual(evidence["detections"][0]["parts"][0]["action"], "refused-body")
        # Existing generator still crops first and uses the same exception.
        baseline = copy.deepcopy(self.row)
        baseline.pop("experiment")
        outputs = dict(pipeline.processing_candidates(self.image, baseline))
        self.assertEqual(outputs["second-crop"].size, (400, default[3]))
        self.assertIn("app bar", baseline["processing"]["steps"][1]["reason"])

    def test_successful_fill_has_one_redetection_and_residual_lineage(self):
        icon = self.part("glyph", [360, 300, 390, 330])
        self.detector.side_effect = [([icon], []), ([icon], [])]
        images, evidence = self.run_sequence()
        self.assertIn("eraser", images)
        self.assertIn("residual-crop", images)
        self.assertEqual(evidence["redetections"], 1)
        self.assertEqual(self.subject_detector.call_count, 1)
        self.assertEqual(evidence["candidates"]["residual-crop"]["input"], "eraser")
        self.assertEqual(images["eraser"].getpixel((200, 400)), self.image.getpixel((200, 400)))
        self.assertEqual(images["eraser"].getpixel((370, 310)), (128, 128, 128))
        for step in evidence["steps"]:
            if step["status"] == "attempted-selected" and step["name"] != "eraser":
                self.assertLessEqual(step["subjectLoss"], .005)
        self.assertIn("no further", evidence["stopReason"])

    def test_face_body_unknown_and_refused_masks_stay_unchanged(self):
        face = self.part("glyph", [170, 110, 190, 130])
        garment = self.part("logo", [110, 400, 140, 430])
        unknown = self.part("garment-unknown", [360, 300, 390, 330])
        refused = self.part("logo", [5, 600, 25, 630])
        self.detector.return_value = ([face, garment, unknown], [refused])
        images, evidence = self.run_sequence()
        self.assertFalse(self.filler.called)
        self.assertEqual(np.asarray(images[evidence["final"]]).tolist(), np.asarray(self.image).tolist())
        actions = {i["action"] for i in evidence["detections"][0]["parts"]}
        self.assertEqual(actions, {"refused-face-or-region", "refused-body", "refused-uncertain", "refused-face"})
        self.assertNotIn("face boxes are never", json.dumps(evidence))

    def test_coverage_refusal_is_explicit_with_mask_but_no_fill(self):
        large = self.part("ui-card", [0, 0, 99, 800])
        self.detector.return_value = ([large], [])
        images, evidence = self.run_sequence()
        self.assertIn("eraser-mask", images)
        self.assertNotIn("eraser", images)
        self.assertFalse(self.filler.called)
        eraser = next(s for s in evidence["steps"] if s["name"] == "eraser")
        self.assertEqual(eraser["status"], "refused")
        self.assertIn("coverage", eraser["reason"])
        self.assertEqual(evidence["redetections"], 0)

    def test_failed_fill_keeps_pixels_and_never_redetects(self):
        self.detector.return_value = ([self.part("glyph", [360, 300, 390, 330])], [])
        self.filler.side_effect = RuntimeError("offline fill failure")
        images, evidence = self.run_sequence()
        self.assertNotIn("eraser", images)
        self.assertEqual(self.detector.call_count, 1)
        self.assertEqual(evidence["redetections"], 0)
        self.assertTrue(any(s["status"] == "failed" and "offline fill failure" in s["reason"]
                            for s in evidence["steps"]))

    def test_no_clutter_does_not_claim_clean_or_redetect(self):
        images, evidence = self.run_sequence()
        self.assertNotIn("eraser-mask", images)
        self.assertFalse(self.filler.called)
        self.assertEqual(self.detector.call_count, 1)
        self.assertIn("do not establish clean", evidence["steps"][1]["reason"])

    def test_initial_crop_does_not_reuse_panel_geometry_that_loses_unsegmented_hair(self):
        self.row["geometry"]["box"] = [0, 90, 400, 800]
        self.row["geometry"]["changed"] = True
        # The detector misses hair above the mask; neither a zero-loss score nor
        # the frozen screenshot geometry establishes that it is safe to remove.
        self.image.paste((180, 90, 40), (160, 30, 240, 90))
        with mock.patch.object(pipeline.geometry, "panel_box",
                               return_value=((0, 90, 400, 800), "Face-margin panel proposal.")):
            images, evidence = self.run_sequence()
        self.assertNotIn("first-crop", images)
        self.assertEqual(images[evidence["final"]].size, self.size)
        self.assertEqual(images[evidence["final"]].getpixel((190, 50)), (180, 90, 40))
        self.assertIn("comparison-only", evidence["panelAssessment"])

    def test_detector_errors_are_explicit_not_clean_results(self):
        self.detector.side_effect = cv2.error("detector offline")
        _, evidence = self.run_sequence()
        self.assertEqual(evidence["detectorErrors"][0]["stage"], "initial")
        self.assertIn("offline", evidence["detectorErrors"][0]["message"])
        self.assertTrue(any("state unknown" in s["reason"] for s in evidence["steps"]))

    def test_person_failure_preserves_pixels_and_is_explicit(self):
        self.subject_detector.side_effect = RuntimeError("person offline")
        images, evidence = self.run_sequence()
        self.assertEqual(list(images), ["control"])
        self.assertEqual(evidence["detectorErrors"][0]["detector"], "person")
        self.assertFalse(self.detector.called)

    def test_residual_detection_failure_never_runs_again(self):
        self.detector.side_effect = [
            ([self.part("glyph", [360, 300, 390, 330])], []), RuntimeError("residual offline")]
        images, evidence = self.run_sequence()
        self.assertIn("eraser", images)
        self.assertNotIn("residual-crop", images)
        self.assertEqual(evidence["detectorErrors"][0]["stage"], "post-fill")
        self.assertEqual(self.detector.call_count, 2)

    def test_first_crop_with_subject_loss_is_refused(self):
        with mock.patch.object(pipeline.geometry, "border_box", return_value=(0, 0, 400, 690)):
            images, evidence = self.run_sequence()
        self.assertNotIn("first-crop", images)
        self.assertEqual(evidence["steps"][0]["status"], "refused")
        self.assertGreater(evidence["steps"][0]["subjectLoss"], .005)

    def test_face_assessment_failure_stops_before_models(self):
        self.row["eligibility"]["status"] = "assessment-failed"
        self.row["eligibility"]["faces"] = []
        images, evidence = self.run_sequence()
        self.assertEqual(list(images), ["control"])
        self.assertFalse(self.subject_detector.called)
        self.assertEqual(evidence["detectorErrors"][0]["detector"], "face")

    def test_selected_first_crop_records_original_coordinate_lineage(self):
        with mock.patch.object(pipeline.geometry, "border_box", return_value=(20, 0, 400, 800)):
            images, evidence = self.run_sequence()
        self.assertEqual(images["first-crop"].size, (380, 800))
        self.assertEqual(evidence["candidates"]["first-crop"]["sourceBox"], [20, 0, 400, 800])
        self.assertEqual(evidence["steps"][0]["subjectLoss"], 0)
        self.assertEqual(self.detector.call_args.args[2], (20, 0))

    def test_cumulative_subject_budget_cannot_reset_after_first_crop(self):
        with mock.patch.object(pipeline.geometry, "border_box", return_value=(0, 0, 400, 798)), \
                mock.patch.object(pipeline, "second_crop", return_value=([0, 0, 400, 796], [], [])):
            images, evidence = self.run_sequence()
        self.assertIn("first-crop", images)
        self.assertNotIn("residual-crop", images)
        residual = next(s for s in evidence["steps"] if s["name"] == "residual-crop")
        self.assertEqual(residual["status"], "refused")
        self.assertGreater(residual["subjectLoss"], .005)

    def test_composition_cannot_discard_refused_region(self):
        refused = self.part("garment-unknown", [5, 600, 25, 630])
        self.detector.return_value = ([refused], [])
        with mock.patch.object(pipeline, "composition_box", return_value=[80, 80, 320, 800]):
            images, evidence = self.run_sequence()
        self.assertIn("composition", images)
        composition = evidence["steps"][-1]
        self.assertEqual(composition["status"], "attempted-rejected")
        self.assertIn("refused region", composition["reason"])
        self.assertEqual(evidence["final"], "control")

    def test_zero_mask_loss_does_not_prove_labelled_hair_or_feet_preserved(self):
        self.person["mask"] = pipeline.clutter.solid((800, 400), [100, 150, 300, 650])
        self.person["box"] = [100, 150, 300, 650]
        self.image.putpixel((200, 30), (255, 0, 0))   # labelled bun missed by the detector
        self.image.putpixel((200, 790), (0, 255, 0))  # labelled toes missed by the detector
        icon = self.part("glyph", [360, 300, 390, 330])
        self.detector.side_effect = [([icon], []), ([], [])]
        frame = [80, 80, 320, 700]
        with mock.patch.object(pipeline, "composition_box", return_value=frame):
            images, evidence = self.run_sequence()
        composition = evidence["steps"][-1]
        self.assertEqual(composition["subjectLoss"], 0.0)
        self.assertEqual(composition["status"], "attempted-rejected")
        self.assertEqual(composition["candidate"], "composition")
        self.assertEqual(composition["selected"], "eraser")
        self.assertIn("Missing hair/feet completeness proof", composition["reason"])
        self.assertEqual(images["composition"].size, (240, 620))
        self.assertEqual(evidence["final"], "eraser")
        self.assertEqual(images["eraser"].getpixel((200, 30)), (255, 0, 0))
        self.assertEqual(images["eraser"].getpixel((200, 790)), (0, 255, 0))
        self.assertEqual(evidence["candidates"]["composition"]["status"], "comparison")
        self.assertFalse(evidence["candidates"]["composition"]["diagnostic"])
        self.assertEqual(evidence["candidates"]["composition"]["input"], "eraser")
        self.assertEqual(evidence["candidates"]["composition"]["sourceBox"], frame)
        self.assertEqual([name for name, item in evidence["candidates"].items()
                          if item["status"] == "selected"], ["eraser"])


if __name__ == "__main__":
    unittest.main()
