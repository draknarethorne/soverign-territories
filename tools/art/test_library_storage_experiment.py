import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art import library_storage_experiment as experiment


class StorageExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=experiment.ROOT / "tmp")
        self.addCleanup(self.temporary.cleanup)
        self.base = pathlib.Path(self.temporary.name)
        self.source = self.base / "source"
        for folder, count in (("Angels/A/gallery", 3), ("Sisters/S/gallery", 3),
                              ("Models/M/gallery", 9), ("Various/review", 15)):
            directory = self.source.joinpath(*folder.split("/"))
            directory.mkdir(parents=True)
            for number in range(count):
                (directory / f"photo_image_{number}.jpg").write_bytes(f"{folder}-{number}".encode())

    def test_balanced_real_path_selection_and_minimum(self):
        paths = experiment.selection(self.source, 24)
        self.assertEqual(len(paths), 24)
        self.assertEqual(sum(p.relative_to(self.source).parts[0] == "Various" for p in paths), 12)
        self.assertEqual(sum(p.relative_to(self.source).parts[0] == "Angels" for p in paths), 3)
        self.assertEqual(sum(p.relative_to(self.source).parts[0] == "Sisters" for p in paths), 3)
        for count in (0, 19, 31):
            with self.assertRaisesRegex(ValueError, "20..30"):
                experiment.selection(self.source, count)

    def test_source_copy_snapshot_is_valid_and_source_unchanged(self):
        rows = experiment.selection(self.source, 20)
        original = experiment.payload_inventory(self.source)
        out = self.base / "experiment"
        working, env = experiment.setup(out, "lean", self.source, rows)
        self.assertEqual(experiment.payload_inventory(self.source), original)
        self.assertEqual(len(list((working / "Various" / "gallery").glob("*.jpg"))), 10)
        self.assertEqual(env["SOVEREIGN_TERRITORIES_SANDBOX_WORKING_ROOT"], str(working))
        from likeness_library import sandbox
        layout = sandbox.validate_sandbox(working)
        self.assertEqual(layout["working_root"], working)
        self.assertTrue((working / ".likeness-library.json").is_file())

    def test_preview_does_not_create_output(self):
        output = experiment.ROOT / "tmp" / "t0"
        self.assertFalse(output.exists())
        with contextlib.redirect_stdout(io.StringIO()):
            result = experiment.main(["--root", str(self.source), "--out", str(output), "--dry-run"])
        self.assertEqual(result, 0)
        self.assertFalse(output.exists())

    def test_output_rejects_escape_and_active_library(self):
        for value in (str(self.source.parent.parent.parent / "outside"),
                      str(self.base / ".." / "elsewhere"), "relative"):
            with self.assertRaises(ValueError):
                experiment.safe_output(value)

    def test_explicit_mixed_sample_rejects_duplicates_escape_and_imbalance(self):
        paths = experiment.selection(self.source, 24)
        names = [path.relative_to(self.source).as_posix() for path in paths]
        listing = self.base / "sources.json"
        listing.write_text(json.dumps(names), encoding="utf-8")
        self.assertEqual(experiment.selection(self.source, 24, listing), paths)
        for invalid in ([*names[:-1], names[0]], [*names[:-1], "../source.jpg"],
                        [*names[:-1], "Models/M/gallery/photo_image_8.jpg"]):
            listing.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaises(ValueError):
                experiment.selection(self.source, 24, listing)

    def test_command_error_keeps_explanatory_log(self):
        phases = {}
        with mock.patch.object(experiment.subprocess, "run", return_value=mock.Mock(returncode=7)):
            with self.assertRaisesRegex(RuntimeError, "intake exited 7"):
                experiment.execute(self.base, "lean", ["sandbox-rebase.cmd"], {}, phases, "intake")
        self.assertTrue((self.base / "lean-intake.log").is_file())
        self.assertEqual(phases, {})

    def test_inventory_and_totals_cover_long_backup_paths(self):
        relative = pathlib.Path("x" * 100, "y" * 100, "payload.bin")
        target = experiment.library_backup._snapshot_path(self.base / relative)
        target.parent.mkdir(parents=True)
        self.addCleanup(experiment.library_backup.shutil.rmtree, target.parent.parent)
        target.write_bytes(b"long path evidence")
        self.assertIn(relative.as_posix(), experiment.payload_inventory(self.base))
        total = experiment.tree_totals(self.base)
        self.assertEqual(total["files"], len(experiment.payload_inventory(self.base)))
        self.assertEqual(total["bytes"], sum(item["bytes"] for item in experiment.payload_inventory(self.base).values()))

    def test_role_hashes_compare_bytes_not_storage_paths(self):
        row = {"source": "Various/gallery/photo.jpg", "sourceSha256": "source",
               "outcome": "compared", "recommendation": {"use": "original"},
               "recommendedPadded": {"path": "full/pad.png", "sha256": "pad"},
               "variants": {"control": {"path": "full/control.png", "sha256": "native",
                                        "thumbnailSha256": "preview"}}}
        before = experiment.role_hashes({"photos": [row]})
        row["recommendedPadded"]["path"] = "lean/pad.png"
        row["variants"]["control"]["path"] = "lean/shared.png"
        self.assertEqual(experiment.role_hashes({"photos": [row]}), before)
        row["recommendedPadded"]["sha256"] = "changed"
        self.assertNotEqual(experiment.role_hashes({"photos": [row]}), before)


if __name__ == "__main__":
    unittest.main()
