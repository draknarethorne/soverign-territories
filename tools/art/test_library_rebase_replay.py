"""Focused replay safety/comparison tests; all disposable files stay in tmp\\r3."""
import json
import pathlib
import shutil
import sys
import unittest
import uuid
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import library_rebase_replay as replay


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.root = replay.OUT / ("test-" + uuid.uuid4().hex)
        self.root.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(replay.library_backup._snapshot_path(self.root))

    def test_output_is_bounded_to_named_ignored_scratch(self):
        self.assertEqual(replay.output_path(replay.OUT), replay.OUT)
        for path in (replay.ROOT, replay.ROOT / "tmp", replay.ROOT / "tmp" / "r4",
                     replay.OUT / ".." / "outside", pathlib.Path("tmp\\r3")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                replay.output_path(path)

    def test_source_paths_refuse_traversal_drive_and_aliases(self):
        for relative in ("../escape.jpg", "/escape.jpg", "Various\\a.jpg", "C:/a.jpg",
                         "Various//a.jpg", "Various/./a.jpg"):
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                replay.safe_path(self.root, relative)
        self.assertEqual(replay.safe_path(self.root, "Various/gallery/a__2.jpg"),
                         self.root / "Various" / "gallery" / "a__2.jpg")

    def test_original_inputs_keep_exact_names_and_hashes(self):
        inputs = self.root / "inputs"
        inputs.mkdir()
        for name in ("same.jpg", "same__2.jpg"):
            path = inputs / "Various" / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(name.encode())
        receipt = {"schemaVersion": 1, "inputs": {
            "Various/" + path.name: replay.digest(path) for path in (inputs / "Various").iterdir()
        }}
        rows = replay.baseline_inputs(self.root, receipt)
        self.assertEqual([row["path"] for row in rows], ["Various/same.jpg", "Various/same__2.jpg"])
        (inputs / "Various" / "same__2.jpg").write_bytes(b"edited")
        with self.assertRaisesRegex(ValueError, "checksum"):
            replay.baseline_inputs(self.root, receipt)

    def test_input_count_and_bytes_bounds(self):
        with self.assertRaises(ValueError):
            replay.baseline_inputs(self.root, {"schemaVersion": 1, "inputs": {}})
        with self.assertRaises(ValueError):
            replay.baseline_inputs(self.root, {"schemaVersion": 1, "inputs": {
                str(index): "a" * 64 for index in range(4001)
            }})
        inputs = self.root / "inputs"
        inputs.mkdir()
        (inputs / "a.jpg").write_bytes(b"xx")
        with mock.patch.object(replay, "MAX_BYTES", 1), self.assertRaises(ValueError):
            replay.baseline_inputs(self.root, {"schemaVersion": 1, "inputs": {
                "a.jpg": replay.digest(inputs / "a.jpg")
            }})

    def test_inventory_detects_edits_and_extra_files(self):
        (self.root / "a").write_bytes(b"native")
        expected = replay.inventory(self.root)
        replay.verify_inventory(self.root, expected)
        (self.root / "b").write_bytes(b"extra")
        with self.assertRaises(ValueError):
            replay.verify_inventory(self.root, expected)

    def test_common_roles_allow_only_unselected_padding_removal(self):
        row = {"source": "Various/a.jpg", "sourceSha256": "a", "outcome": "compared",
               "recommendation": {"use": "control"}, "variants": {
                   "control": {"sha256": "b", "thumbnailSha256": "c", "paddedSha256": "d"},
                   "tone": {"sha256": "e", "thumbnailSha256": "f", "paddedSha256": "g"}}}
        before = {"photos": [row]}
        after = json.loads(json.dumps(before))
        del after["photos"][0]["variants"]["tone"]["paddedSha256"]
        self.assertTrue(replay.compare_roles(before, after)["equal"])
        after["photos"][0]["variants"]["control"]["paddedSha256"] = "edited"
        self.assertFalse(replay.compare_roles(before, after)["equal"])
        after = json.loads(json.dumps(before))
        after["photos"][0]["variants"]["tone"]["thumbnailSha256"] = "edited"
        self.assertFalse(replay.compare_roles(before, after)["equal"])

    def test_matching_hash_destination_and_settings_gate(self):
        before = {"photos": [{"source": "Various/a.jpg", "preparedSHA256": "a",
                              "destination": "Models/X/gallery/a.jpg"}],
                  "policy": {}, "settings": {}, "castSeedPolicy": "core"}
        after = json.loads(json.dumps(before))
        self.assertTrue(replay.compare_matching(before, after)["equal"])
        after["photos"][0]["destination"] = "Potentials/X/gallery/a.jpg"
        self.assertFalse(replay.compare_matching(before, after)["equal"])
        after["settings"] = {"minFace": 20}
        with self.assertRaises(ValueError):
            replay.compare_matching(before, after)

    def test_pixel_blocker_records_difference_without_installing(self):
        from PIL import Image

        baseline = self.root / "baseline"
        working, source, run = replay.locations(self.root)
        reports = [baseline / "inputs" / "_reports" / "preparation" / "all",
                   run / "inputs" / "_reports" / "preparation" / "all"]
        rows = []
        for index, report in enumerate(reports):
            report.mkdir(parents=True)
            image = report / "native.png"
            Image.new("RGB", (2, 2), (index, 0, 0)).save(image)
            row = {"source": "Various/gallery/a.jpg", "sourceSha256": "original",
                   "outcome": "compared", "recommendation": {"use": "control"},
                   "variants": {"control": {"path": "native.png", "sha256": replay.digest(image),
                                             "paddedSha256": str(index)}}}
            rows.append({"recipe": {}, "photos": [row]})
            replay.write(report / "manifest.json", {})
        state = {"baseline": str(baseline), "preparationComparison": replay.compare_roles(*rows),
                 "baselineInstalledInventory": {}, "stages": {}}
        with mock.patch.object(replay, "check_protected"), \
                mock.patch.object(replay, "totals", return_value={"files": 1, "bytes": 1}), \
                mock.patch.object(replay, "execute") as execute:
            replay.record_preparation_block(self.root, state, *rows)
        report = replay.load(self.root / "preparation-blocker.json")
        self.assertEqual(report["variantPixelDifferences"][0]["maximumChannelDifference"], 1)
        self.assertEqual(report["selectedNativeDifferences"], ["Various/gallery/a.jpg"])
        self.assertEqual(state["status"], "blocked-preparation")
        self.assertFalse(report["matchingStarted"])
        execute.assert_not_called()

    def test_completed_apply_only_checks(self):
        state = {"schemaVersion": 1, "status": "complete", "baseline": str(self.root),
                 "out": str(self.root), "inputs": []}
        replay.write(self.root / replay.RECEIPT, state)
        state["protected"] = {}
        state["policy"] = {}
        replay.write(self.root / replay.RECEIPT, state)
        with mock.patch.object(replay, "inspect_baseline", return_value=({"policy": {}}, [], {}, None)), \
                mock.patch.object(replay, "check", return_value=state) as checked, \
                mock.patch.object(replay, "execute") as execute:
            self.assertEqual(replay.apply(self.root, self.root, 2), state)
        checked.assert_called_once_with(self.root)
        execute.assert_not_called()

    def test_failed_subprocess_preserves_attempt_log_and_receipt(self):
        state = {"stages": {}, "attempts": []}
        with mock.patch.object(replay.subprocess, "run", return_value=mock.Mock(returncode=7)):
            with self.assertRaisesRegex(RuntimeError, "exited 7"):
                replay.execute(self.root, state, {}, "intake", ["sandbox-rebase.cmd"])
        saved = replay.load(self.root / replay.RECEIPT)
        self.assertEqual(saved["attempts"][0]["status"], "failed")
        self.assertTrue(pathlib.Path(saved["attempts"][0]["log"]).is_absolute())
        self.assertTrue(pathlib.Path(saved["attempts"][0]["log"]).is_file())
        self.assertNotIn("intake", saved["stages"])

    def test_successful_stage_resumes_without_subprocess(self):
        state = {"stages": {"intake": {}}, "attempts": []}
        with mock.patch.object(replay.subprocess, "run") as run:
            replay.execute(self.root, state, {}, "intake", ["sandbox-rebase.cmd"])
        run.assert_not_called()

    def test_setup_preserves_sanitized_duplicate_paths_and_inherited_catalogue(self):
        baseline = self.root / "baseline"
        baseline.mkdir()
        rows = []
        for name in ("Various/gallery/same.jpg", "Various/review/same__2.jpg"):
            path = baseline / "inputs" / pathlib.Path(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode())
            rows.append({"path": name, "bytes": path.stat().st_size, "sha256": replay.digest(path)})
        catalogue = self.root / "inherited.json"
        catalogue.write_bytes(b'{"schemaVersion":1,"people":{},"photos":{},"actions":[]}')
        out = self.root / "copy"
        with mock.patch.object(replay.metadata, "CATALOG_PATH", catalogue), \
                mock.patch.dict(replay.EXPECTED, {"inherited": replay.digest(catalogue)}):
            replay.setup(out, {"policy": {}}, rows, baseline)
        working, source, run = replay.locations(out)
        self.assertEqual(replay.load(working.parent / "source-manifest.json")["files"], rows)
        for root in (working, source):
            for row in rows:
                replay.require_hash(replay.safe_path(root, row["path"]), row["sha256"])
        self.assertEqual((working / ".likeness-library.json").read_bytes(), catalogue.read_bytes())
        self.assertFalse((run / "likeness-cache.json").exists())

    def test_new_replay_does_not_override_lean_default(self):
        working, _, run = replay.locations(self.root)
        command = replay.common_command(working, run, 2)
        self.assertNotIn("--storage-mode", command)
        self.assertEqual(command[command.index("--cast-seeds") + 1], "core")
        self.assertEqual(command[command.index("--baseline") + 1], "source")

    def test_failed_intake_resume_uses_normal_launcher_ownership(self):
        state = {"schemaVersion": 1, "status": "incomplete", "baseline": str(self.root),
                 "out": str(self.root), "inputs": [], "protected": {}, "policy": {},
                 "workers": 2, "setupComplete": True, "stages": {"inventory-preview": {}},
                 "attempts": [{"status": "failed"}]}
        replay.write(self.root / replay.RECEIPT, state)
        original = {"policy": {}}
        commands = []

        def execute(out, saved, env, label, command, **kwargs):
            commands.append((label, command))
            if label == "intake":
                raise RuntimeError("normal launcher owns mirror and resume")

        with mock.patch.object(replay, "inspect_baseline", return_value=(original, [], {}, None)), \
                mock.patch.object(replay, "check_protected"), \
                mock.patch.object(replay, "execute", side_effect=execute), \
                mock.patch.object(replay.shutil, "copy2") as copy:
            with self.assertRaisesRegex(RuntimeError, "normal launcher"):
                replay.apply(self.root, self.root, 2)
        label, command = commands[-1]
        self.assertEqual(label, "intake")
        self.assertEqual(command[0], "sandbox-rebase.cmd")
        self.assertEqual(command[-2:], ["--intake-only", "--apply"])
        copy.assert_not_called()
        working, source, run = replay.locations(self.root)
        self.assertFalse((run / "inputs").exists())

    def test_inventory_refuses_link_before_resolving_root(self):
        with mock.patch.object(replay.sandbox, "_is_reparse_point", return_value=True), \
                mock.patch.object(replay.library_backup, "_snapshot_path") as snapshot:
            with self.assertRaisesRegex(ValueError, "linked"):
                replay.inventory(self.root)
        snapshot.assert_not_called()

    def test_incomplete_check_refuses_before_subprocess(self):
        replay.write(self.root / replay.RECEIPT, {"schemaVersion": 1, "status": "incomplete"})
        with mock.patch.object(replay.subprocess, "run") as run, self.assertRaises(ValueError):
            replay.check(self.root)
        run.assert_not_called()

    def test_wrong_inherited_catalogue_stops_before_copying(self):
        with mock.patch.object(replay, "load", return_value={
            "status": "applied", "previousLocalCatalog": False,
            "workingRoot": str(self.root.parent.parent), "sourceCatalogSHA256": replay.EXPECTED["inherited"],
        }), mock.patch.object(replay, "require_hash", side_effect=ValueError("checksum")), \
                mock.patch.object(replay.shutil, "copy2") as copy:
            with self.assertRaisesRegex(ValueError, "checksum"):
                replay.inspect_baseline(self.root)
        copy.assert_not_called()


if __name__ == "__main__":
    unittest.main()
