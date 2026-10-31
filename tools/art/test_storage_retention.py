"""Explicit sandbox run-retention policy and deletion safeguards."""
import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art.likeness_library import report_assets, storage_retention
from tools.workflows import comfy_workflows as cw


class StorageRetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name) / "Sovereign Territories Sandbox" / "Working"
        self.root.mkdir(parents=True)
        self.cfg = cw.load_cfg()
        self.state, self.reports = storage_retention._roots(self.root, self.cfg)
        self.state.mkdir(parents=True)

    def add_run(self, name):
        run = self.state / name
        run.mkdir()
        (run / "run.json").write_text(json.dumps({
            "runId": name,
            "mode": "sandbox-rebase",
            "status": "applied",
            "workingRoot": str(self.root),
        }), encoding="utf-8")
        (run / "evidence.bin").write_bytes(name.encode("ascii"))
        return run

    def register_pair(self):
        self.add_run("a-historical")
        self.add_run("z-current")
        storage_retention.register_runs(
            self.root, self.cfg, register_all=True
        )
        storage_retention.accept_run(
            self.root, self.cfg, "a-historical", "Reviewed; superseded by current run."
        )
        storage_retention.accept_run(
            self.root, self.cfg, "z-current", "Reviewed and selected as current."
        )

    def test_preview_keeps_unregistered_runs_and_does_not_write_manifest(self):
        run = self.add_run("untracked")

        result = storage_retention.preview(self.root, self.cfg)

        self.assertEqual(result["unregisteredRunCount"], 1)
        self.assertEqual(result["runs"][0]["disposition"], "keep")
        self.assertTrue(run.is_dir())
        self.assertFalse((self.state / storage_retention.MANIFEST_NAME).exists())

    def test_full_scale_install_receipt_is_supported_but_limit_remains_bounded(self):
        run = self.add_run("full-scale")
        path = run / "run.json"
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["installationEvidence"] = "x" * 19_623_486
        path.write_text(json.dumps(receipt), encoding="utf-8")
        self.assertGreater(path.stat().st_size, 16 * 1024 * 1024)
        self.assertEqual(storage_retention.MAX_RUN_MANIFEST_BYTES, 64 * 1024 * 1024)
        result = storage_retention.register_runs(self.root, self.cfg, run_names=["full-scale"])
        self.assertIsNotNone(result)
        self.assertEqual(storage_retention._read_json(path)["status"], "applied")
        self.assertIn("run.json", storage_retention._manifest_hashes(run))
        with mock.patch.object(storage_retention, "MAX_RUN_MANIFEST_BYTES", 16 * 1024 * 1024):
            with self.assertRaisesRegex(ValueError, "run manifest exceeds"):
                storage_retention._manifest_hashes(run)
        with self.assertRaisesRegex(ValueError, "run manifest exceeds"):
            storage_retention._read_json(path, limit=16 * 1024 * 1024)

    def test_only_approved_nonlatest_run_can_be_pruned(self):
        self.register_pair()
        with self.assertRaisesRegex(ValueError, "latest accepted"):
            storage_retention.approve_prune(
                self.root, self.cfg, "z-current", "Not eligible.",
                review_cleared=True, undo_cleared=True, audit_cleared=True,
            )

        storage_retention.approve_prune(
            self.root, self.cfg, "a-historical", "Reviewed; no undo or report dependencies.",
            review_cleared=True, undo_cleared=True, audit_cleared=True,
        )
        result = storage_retention.preview(self.root, self.cfg)
        old = next(run for run in result["runs"] if run["runId"] == "a-historical")
        self.assertEqual(old["disposition"], "candidate")

        receipt = storage_retention.delete_run(self.root, self.cfg, "a-historical")

        self.assertFalse((self.state / "a-historical").exists())
        self.assertEqual(receipt["status"], "complete")
        self.assertTrue(pathlib.Path(receipt["receiptPath"]).is_file())
        manifest = json.loads((self.state / storage_retention.MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertEqual(manifest["runs"]["a-historical"]["retentionClass"], "pruned")

    def test_report_dependency_and_postapproval_change_block_pruning(self):
        self.register_pair()
        self.reports.mkdir(parents=True)
        dependency = self.reports / "historical-review.txt"
        dependency.write_text("Evidence for a-historical remains linked.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "referenced by non-regenerable reports"):
            storage_retention.approve_prune(
                self.root, self.cfg, "a-historical", "Reviewed.",
                review_cleared=True, undo_cleared=True, audit_cleared=True,
            )

        dependency.unlink()
        storage_retention.approve_prune(
            self.root, self.cfg, "a-historical", "Reviewed; dependency removed.",
            review_cleared=True, undo_cleared=True, audit_cleared=True,
        )
        (self.state / "a-historical" / "evidence.bin").write_bytes(b"changed")
        result = storage_retention.preview(self.root, self.cfg)
        old = next(run for run in result["runs"] if run["runId"] == "a-historical")
        self.assertEqual(old["disposition"], "blocked")
        with self.assertRaisesRegex(ValueError, "not safe to prune"):
            storage_retention.delete_run(self.root, self.cfg, "a-historical")
        self.assertTrue((self.state / "a-historical").is_dir())

    def test_delete_refreshes_regenerable_history_and_its_ownership_manifest(self):
        self.register_pair()
        history = self.reports / "library"
        history.mkdir(parents=True)
        page = history / "intake_runs.html"
        page.write_text("old history page", encoding="utf-8")
        (history / report_assets.MANIFEST).write_text(json.dumps({
            "formatVersion": 1,
            "recipe": report_assets.RECIPE,
            "files": {},
        }), encoding="utf-8")
        storage_retention.approve_prune(
            self.root, self.cfg, "a-historical", "Reviewed; history is regenerable.",
            review_cleared=True, undo_cleared=True, audit_cleared=True,
        )

        def publish_history(root, output_dir, *, domain, cfg):
            self.assertEqual(root, self.root)
            self.assertEqual(output_dir, history)
            self.assertEqual(domain, "general")
            self.assertIs(cfg, self.cfg)
            page.write_text("refreshed history page", encoding="utf-8")
            return page

        with mock.patch.object(
            storage_retention.preparation_history, "publish_staged", side_effect=publish_history
        ) as publish:
            receipt = storage_retention.delete_run(self.root, self.cfg, "a-historical")

        publish.assert_called_once()
        self.assertEqual(page.read_text(encoding="utf-8"), "refreshed history page")
        ownership = json.loads((history / report_assets.MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(
            ownership["files"]["intake_runs.html"],
            hashlib.sha256(page.read_bytes()).hexdigest(),
        )
        self.assertEqual(receipt["status"], "complete")

    def test_partial_history_publication_can_be_repaired_without_restoring_run_data(self):
        self.register_pair()
        history = self.reports / "library"
        history.mkdir(parents=True)
        (history / "intake_runs.html").write_text("old page", encoding="utf-8")
        storage_retention.approve_prune(
            self.root, self.cfg, "a-historical", "Reviewed; history is regenerable.",
            review_cleared=True, undo_cleared=True, audit_cleared=True,
        )
        with mock.patch.object(
            storage_retention.preparation_history, "publish_staged",
            side_effect=ValueError("temporary publication failure"),
        ):
            with self.assertRaisesRegex(ValueError, "temporary publication failure"):
                storage_retention.delete_run(self.root, self.cfg, "a-historical")

        self.assertFalse((self.state / "a-historical").exists())

        def publish_history(root, output_dir, *, domain, cfg):
            self.assertEqual(root, self.root)
            self.assertEqual(output_dir, history)
            self.assertEqual(domain, "general")
            self.assertIs(cfg, self.cfg)
            page = output_dir / "intake_runs.html"
            page.write_text("repaired page", encoding="utf-8")
            return page

        with mock.patch.object(
            storage_retention.preparation_history, "publish_staged", side_effect=publish_history
        ):
            receipt = storage_retention.repair_history(
                self.root, self.cfg, "a-historical"
            )

        self.assertEqual(receipt["status"], "complete")
        self.assertEqual((history / "intake_runs.html").read_text(encoding="utf-8"), "repaired page")
        preview = storage_retention.preview(self.root, self.cfg)
        self.assertEqual(preview["blockedRunCount"], 0)


if __name__ == "__main__":
    unittest.main()
