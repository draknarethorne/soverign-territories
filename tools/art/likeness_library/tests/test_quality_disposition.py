import copy
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

from tools.art.likeness_library import metadata, quality_disposition as quality


class QualityDispositionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name) / "Sovereign Territories Sandbox" / "Working"
        self.run = self.root / "_sandbox-state" / "directed"
        self.run.mkdir(parents=True)
        self.cfg = quality.actions.cw.load_cfg()
        self.catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
        self.rows = []
        cases = [
            ("measured-face-too-small", 1, 50, "face too small (50px)"),
            ("ambiguous-multiface", 2, 150, "possible additional face"),
            ("missing-or-unusable-measurement", 0, 0, "no face measurement"),
            ("identity-only", 1, 150, "low similarity"),
            ("measured-head-obstruction", 1, 150, "the app's bars cover her head (screenshot)"),
        ]
        for index, (classification, faces, px, reason) in enumerate(cases):
            pid = f"photo:image_{123450 + index}"
            relative = f"Various/gallery/intake_image_{123450 + index}.jpg"
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"original-{index}".encode())
            digest = metadata.content_sha256(path)
            self.catalog["photos"][pid] = {"contentSha256": digest, "protected": False}
            self.rows.append({
                "photoId": pid, "source": relative, "destination": relative, "sha256": digest,
                "preparedSHA256": digest,
                "qualityEvidence": {"classification": classification, "faces": faces, "facePixels": px,
                                    "minimumFacePixels": 100, "reason": reason},
            })
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        self.plan = {
            "status": "applied", "workingRoot": str(self.root), "photos": self.rows,
            "installedCatalogSHA256": metadata.content_sha256(self.root / ".likeness-library.json"),
            "groupLifecycle": {"assignmentSummary": {"activeVarious": len(self.rows)}},
        }
        self.write_plan()

    def write_plan(self):
        (self.run / "run.json").write_text(json.dumps(self.plan), encoding="utf-8")

    def execute(self, **kwargs):
        with mock.patch.object(quality.actions.cw, "load_cfg", return_value=self.cfg), \
                mock.patch.object(quality.actions.retained_preparation.cw, "load_cfg", return_value=self.cfg):
            return quality.execute(self.run, self.cfg, **kwargs)

    def test_preview_apply_idempotent_check_and_exact_undo_preserve_run_and_all_content(self):
        baseline = (self.run / "run.json").read_bytes()
        before = (self.root / ".likeness-library.json").read_bytes()
        document = self.execute()
        self.assertEqual(len(document["actions"]), 2)
        self.assertEqual((self.root / ".likeness-library.json").read_bytes(), before)
        self.assertFalse((self.run / "quality-disposition.json").exists())
        receipt = self.execute(apply=True)
        self.assertEqual(receipt["conservation"]["active"], 3)
        self.assertEqual(receipt["conservation"]["quarantined"], 2)
        self.assertEqual(len(receipt["held"]), 3)
        self.assertEqual(self.execute(check=True), receipt)
        self.assertEqual(self.execute(apply=True), receipt)
        backup = json.loads((pathlib.Path(receipt["backup"]) / "manifest.json").read_bytes())
        self.assertEqual(backup["scope"], "transaction")
        self.assertEqual(backup["files"], 3)
        for move in receipt["moves"]:
            self.assertEqual(metadata.content_sha256(self.root / move["destination"]), move["contentSha256"])
            self.assertFalse((self.root / move["source"]).exists())
        self.assertEqual(self.execute(undo=True)["status"], "applied")
        undone = self.execute(undo=True, apply=True)
        self.assertEqual(undone["conservation"]["active"], 5)
        self.assertEqual(undone["conservation"]["quarantined"], 0)
        self.assertEqual(self.execute(check=True), undone)
        self.assertEqual(self.execute(undo=True, apply=True), undone)
        self.assertEqual((self.run / "run.json").read_bytes(), baseline)
        for row in self.rows:
            self.assertEqual(metadata.content_sha256(self.root / row["destination"]), row["sha256"])

    def test_changed_run_catalogue_content_collisions_and_unknown_quality_fail_explicitly(self):
        self.execute(apply=True)
        baseline = (self.run / "run.json").read_bytes()
        (self.run / "run.json").write_bytes(baseline + b" ")
        with self.assertRaisesRegex(ValueError, "changed disposition binding"):
            self.execute(check=True)
        (self.run / "run.json").write_bytes(baseline)
        receipt = self.execute(check=True)
        move = receipt["moves"][0]
        (self.root / move["destination"]).write_bytes(b"changed")
        with self.assertRaises((ValueError, OSError)):
            self.execute(check=True)

    def test_protection_and_no_unusable_evidence_refuse_without_transaction(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["photos"][self.rows[0]["photoId"]]["protected"] = True
        metadata.save_catalog(catalog, self.root / ".likeness-library.json")
        self.plan["installedCatalogSHA256"] = metadata.content_sha256(self.root / ".likeness-library.json")
        self.write_plan()
        with self.assertRaisesRegex(ValueError, "quality action refused"):
            self.execute(apply=True)
        self.assertFalse((self.run / "quality-disposition.json").exists())
        for row in self.rows:
            row["qualityEvidence"]["faces"] = 0
        self.write_plan()
        with self.assertRaisesRegex(ValueError, "no unequivocal measured unusable"):
            self.execute()

    def test_failure_retains_prepared_receipt_and_never_blindly_repeats(self):
        with mock.patch.object(quality.actions, "apply_actions", side_effect=ValueError("injected")):
            with self.assertRaisesRegex(ValueError, "injected"):
                self.execute(apply=True)
        receipt = json.loads((self.run / "quality-disposition.json").read_bytes())
        self.assertEqual(receipt["status"], "prepared")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.execute(apply=True)
        self.assertTrue(all((self.root / row["destination"]).is_file() for row in self.rows))

    def test_existing_destination_or_new_active_input_cannot_silently_break_conservation(self):
        destination = quality.actions._destination(
            {"type": "photo-junked", "personFolder": "Various", "sourceBucket": "Gallery"},
            self.root, "Various", self.cfg,
        ) / pathlib.PurePosixPath(self.rows[0]["destination"]).name
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"existing")
        with self.assertRaisesRegex(ValueError, "quality action refused"):
            self.execute(apply=True)
        self.assertEqual(destination.read_bytes(), b"existing")
        self.assertFalse((self.run / "quality-disposition.json").exists())
        destination.unlink()
        self.execute(apply=True)
        (self.root / "Various" / "gallery" / "new_image_999999.jpg").write_bytes(b"new")
        with self.assertRaisesRegex(ValueError, "inventory differs"):
            self.execute(check=True)

    def test_current_catalogue_drift_and_backup_manifest_drift_are_detected(self):
        receipt = self.execute(apply=True)
        catalog_path = self.root / ".likeness-library.json"
        baseline = catalog_path.read_bytes()
        catalog_path.write_bytes(baseline + b" ")
        with self.assertRaisesRegex(ValueError, "catalogue changed"):
            self.execute(check=True)
        catalog_path.write_bytes(baseline)
        manifest = pathlib.Path(receipt["backup"]) / "manifest.json"
        manifest.write_bytes(manifest.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "recovery manifest changed"):
            self.execute(check=True)

    def test_sandbox_guard_and_configured_junk_root_are_not_bypassed(self):
        baseline = copy.deepcopy(self.plan)
        self.plan["workingRoot"] = str(self.root.parent.parent / "Production")
        self.write_plan()
        with self.assertRaisesRegex(ValueError, "Sandbox Working-local only"):
            self.execute()
        self.plan = baseline
        self.write_plan()
        self.cfg = copy.deepcopy(self.cfg)
        self.cfg.setdefault("storageRoots", {})["junk"] = "operations/quarantine"
        receipt = self.execute(apply=True)
        self.assertTrue(all(item["destination"].startswith("operations/quarantine/")
                            for item in receipt["moves"]))
        self.execute(check=True)
        self.execute(undo=True, apply=True)

    def test_supported_launcher_preview_apply_check_and_undo(self):
        repo = pathlib.Path(__file__).resolve().parents[4]
        launcher = repo / "bin" / "likeness-actions.cmd"
        for flags in (["--dry-run"], ["--apply"], ["--check"], ["--undo", "--dry-run"],
                      ["--undo", "--apply"], ["--check"]):
            with self.subTest(flags=flags):
                result = subprocess.run(
                    ["cmd", "/c", "call", str(launcher), "quality", str(self.run), *flags],
                    cwd=repo, capture_output=True, text=True, timeout=90,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(all((self.root / row["destination"]).is_file() for row in self.rows))

    def test_retained_preparation_moves_checks_and_undoes_with_existing_action_journal(self):
        from tools.art.test_retained_preparation import RetainedPreparationTests
        fixture = RetainedPreparationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.root = self.root
        fixture.destination = self.rows[0]["destination"]
        fixture.put(self.root, fixture.destination, fixture.selected)
        fixture.row["photoId"] = self.rows[0]["photoId"]
        fixture.row["source"] = fixture.destination
        published = fixture.stage()
        originals = {item["path"]: (self.root / item["path"]).read_bytes() for item in published}
        digest = metadata.content_sha256(self.root / fixture.destination)
        self.rows[0].update(sha256=fixture.source_sha, preparedSHA256=digest)
        self.catalog["photos"][self.rows[0]["photoId"]]["contentSha256"] = digest
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        self.plan["installedCatalogSHA256"] = metadata.content_sha256(self.root / ".likeness-library.json")
        self.write_plan()
        receipt = self.execute(apply=True)
        self.execute(check=True)
        self.assertTrue(quality.actions._retained_journal(self.root, receipt["batchId"], self.cfg).is_file())
        self.execute(undo=True, apply=True)
        self.execute(check=True)
        for relative, content in originals.items():
            self.assertEqual((self.root / relative).read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
