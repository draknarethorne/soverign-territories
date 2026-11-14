"""Local observations are private diagnostic inputs, never human identity labels."""
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art import likeness_observe as subject


class LocalObserverTests(unittest.TestCase):
    def state(self):
        rows = []
        for i, disposition in enumerate(("released-to-reassessment-pool", "membership-ambiguous",
                                         "current-membership-supported")):
            rows.extend([{
                "photoId": f"p{i}", "disposition": disposition,
                "membershipAssessment": {"own": {"supportPhotoIds": [f"r{i}"], "frozenReferencePhotoIds": []}},
            }, {"photoId": f"r{i}", "disposition": "reference-needed", "membershipAssessment": {"own": None}}])
        return {"rows": rows}

    def test_selection_is_bounded_and_not_human_labelled(self):
        selected, cases = subject.selection(self.state())
        self.assertEqual(len(selected), 6)
        self.assertEqual(len(cases), 3)
        self.assertTrue(all(c["humanReview"] == "not-performed" for c in cases))
        self.assertTrue(all(c["contextInterpretation"] == "unevaluated" for c in cases))

    def test_missing_references_do_not_invent_observations(self):
        state = self.state()
        for row in state["rows"]:
            row["membershipAssessment"]["own"] = None
        with self.assertRaisesRegex(ValueError, "no eligible"):
            subject.selection(state)

    def test_preview_setup_does_not_install_or_download(self):
        with mock.patch.object(subject.subprocess, "run") as run:
            subject.setup(False)
        run.assert_not_called()

    def test_setup_without_apply_and_missing_runtime_are_explicit(self):
        self.assertEqual(subject.main(["--setup", "--check"]), 2)

    def test_html_escapes_model_output_and_shows_inline_image_and_filename(self):
        result = {"records": [{
            "photoId": "p0", "source": str(pathlib.Path.cwd() / "a.jpg"), "crop": "crop-00.png",
            "observation": "<script>unsafe</script>", "orderStable": False,
        }]}
        page = subject.render(result)
        self.assertIn('<img src="crop-00.png"', page)
        self.assertIn("Open original filename: a.jpg", page)
        self.assertIn("&lt;script&gt;unsafe&lt;/script&gt;", page)
        self.assertNotIn("<script>unsafe</script>", page)
        self.assertIn("Human review: not performed", page)

    def test_changed_bound_output_fails_not_silently_reused(self):
        with tempfile.TemporaryDirectory(dir=subject.ROOT / "tmp") as directory:
            root = pathlib.Path(directory)
            (root / "observations.json").write_text(json.dumps({}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bound output changed"):
                subject.verify_files(root, {"observations.json": "wrong-digest"})

    def test_receipt_transitively_binds_candidate_state_inputs_and_code(self):
        with tempfile.TemporaryDirectory(dir=subject.ROOT / "tmp") as directory:
            root = pathlib.Path(directory)
            (root / "receipt.json").write_text("{}", encoding="utf-8")
            receipt = {"inputs": {"saved-run": "run-hash"}, "code": {"builder": "code-hash"},
                       "outputs": {"state.json": "state-hash", "index.html": "page-hash"}}
            result = subject.source_bindings(root, receipt)
            self.assertEqual(result[str(root / "state.json")], "state-hash")
            self.assertEqual(result["saved-run"], "run-hash")
            self.assertEqual(result["builder"], "code-hash")
            self.assertIn(str(root / "receipt.json"), result)


if __name__ == "__main__":
    unittest.main()
