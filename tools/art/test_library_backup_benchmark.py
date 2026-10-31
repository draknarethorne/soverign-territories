"""Bounded format benchmark: measured restore and fail-closed persistence."""
import contextlib
import hashlib
import io
import json
import os
import pathlib
import shutil
import stat
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import library_backup
import library_backup_benchmark as benchmark


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        scratch = benchmark.ROOT / "tmp" / "backup-benchmark-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        self.root = pathlib.Path(tempfile.mkdtemp(dir=scratch))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.snapshot = self.root / "snapshot"
        self.snapshot.mkdir()
        entries = []
        for index, name in enumerate(("work-root/a/photo.jpg", "work-root/b/data.json",
                                      "comfy-inputs/picture.png")):
            path = self.snapshot / name
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = (bytes([index]) + b"synthetic pixels and metadata\n") * 4096
            path.write_bytes(payload)
            os.utime(path, ns=(1700000000123456700 + index * 100,
                               1700000000123456700 + index * 100))
            entries.append({"backup": name, "size": len(payload),
                            "sha256": hashlib.sha256(payload).hexdigest()})
        self.manifest = self.snapshot / "manifest.json"
        self.manifest.write_text(json.dumps({"status": "complete", "entries": entries}),
                                 encoding="utf-8")
        self.out = self.root / "result"
        self.quiet = contextlib.redirect_stdout(io.StringIO())
        self.quiet.__enter__()
        self.addCleanup(self.quiet.__exit__, None, None, None)

    def run_benchmark(self, **kwargs):
        return benchmark.run(self.snapshot, self.out, **kwargs)

    def test_preview_has_no_writes_and_deterministic_bounds(self):
        first = self.run_benchmark(limit=2, max_bytes=300000)
        self.assertEqual(first, self.run_benchmark(limit=2, max_bytes=300000))
        self.assertEqual(first["sampleFiles"], 2)
        self.assertLessEqual(first["sampleBytes"], 300000)
        self.assertFalse(self.out.exists())
        for limit, size in ((65, 1), (0, 1), (1, 129 * 1024 * 1024)):
            with self.assertRaises(ValueError):
                self.run_benchmark(limit=limit, max_bytes=size)

    def test_measures_all_formats_exact_hashes_mtimes_and_idempotent_check(self):
        receipt = self.run_benchmark(apply=True)
        before = (self.out / "receipt.json").stat().st_mtime_ns
        self.assertEqual(receipt, self.run_benchmark(check=True))
        self.assertEqual(receipt, self.run_benchmark(apply=True))
        self.assertEqual(before, (self.out / "receipt.json").stat().st_mtime_ns)
        for result in receipt["results"]:
            self.assertEqual(result["restoreFiles"], 3)
            self.assertGreater(result["buildSeconds"], 0)
        self.assertLess(receipt["results"][2]["outputBytes"],
                        receipt["results"][0]["outputBytes"])

    def test_changed_sample_rejected_even_same_size_and_mtime(self):
        receipt = self.run_benchmark(apply=True)
        row = receipt["selection"]["entries"][0]
        source = self.snapshot / row["path"]
        source.write_bytes(b"x" * row["size"])
        os.utime(source, ns=(row["mtimeNs"], row["mtimeNs"]))
        with self.assertRaisesRegex(ValueError, "content/mtime changed"):
            self.run_benchmark(check=True)

    def test_modified_restore_and_directory_payload_rejected(self):
        receipt = self.run_benchmark(apply=True)
        row = receipt["selection"]["entries"][0]
        for name in ("restored", "payload"):
            target = self.out / "directory" / name / row["path"]
            original = target.read_bytes()
            target.write_bytes(b"x" * len(original))
            with self.assertRaises(ValueError):
                self.run_benchmark(check=True)
            target.write_bytes(original)
            os.utime(target, ns=(row["mtimeNs"], row["mtimeNs"]))

    def test_truncated_archive_and_incomplete_run_rejected(self):
        receipt = self.run_benchmark(apply=True)
        archive = self.out / "zip64-stored" / "payload.zip"
        archive.write_bytes(archive.read_bytes()[:-16])
        with self.assertRaises(zipfile.BadZipFile):
            benchmark.verify_archive(archive, receipt["selection"]["entries"])
        with self.assertRaises(ValueError):
            self.run_benchmark(check=True)
        (self.out / "receipt.json").unlink()
        with self.assertRaises(OSError):
            self.run_benchmark(apply=True)

    def test_interrupted_build_never_publishes_receipt_or_overwrites(self):
        with mock.patch.object(benchmark, "build_format", side_effect=OSError("interrupted")):
            with self.assertRaises(OSError):
                self.run_benchmark(apply=True)
        self.assertFalse((self.out / "receipt.json").exists())
        with self.assertRaises(OSError):
            self.run_benchmark(apply=True)

    def test_modified_manifest_and_settings_refused(self):
        self.run_benchmark(apply=True)
        with self.assertRaises(ValueError):
            self.run_benchmark(limit=2, apply=True)
        self.manifest.write_text(self.manifest.read_text() + " ", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.run_benchmark(check=True)

    def test_traversal_absolute_duplicate_and_link_archive_members_rejected(self):
        for name in ("../escape", "/absolute", "C:/escape", "a\\escape", "a//b"):
            with self.assertRaises(ValueError):
                benchmark.relative_name(name)
        malicious = self.root / "malicious.zip"
        with zipfile.ZipFile(malicious, "w") as archive:
            info = zipfile.ZipInfo("safe")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, b"target")
        with self.assertRaisesRegex(ValueError, "unsafe"):
            benchmark.verify_archive(malicious, [{
                "path": "safe", "size": 6, "sha256": hashlib.sha256(b"target").hexdigest()}])
        data = json.loads(self.manifest.read_text())
        data["entries"].append(data["entries"][0])
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.run_benchmark()

    def test_output_outside_ignored_tmp_and_reparse_components_refused(self):
        with self.assertRaises(ValueError):
            benchmark.output_path(benchmark.ROOT / "reports" / "benchmark")
        original = pathlib.Path.lstat

        def reparse(path, *args, **kwargs):
            value = original(path, *args, **kwargs)
            if path == self.snapshot:
                return mock.Mock(st_mode=value.st_mode, st_file_attributes=0x400)
            return value

        with mock.patch.object(pathlib.Path, "lstat", reparse):
            with self.assertRaisesRegex(ValueError, "reparse"):
                self.run_benchmark()

    def test_long_output_paths_and_snapshot_overlap(self):
        self.out = self.root / ("long-output-" + "x" * 140) / "result"
        self.run_benchmark(apply=True)
        self.run_benchmark(check=True)
        self.out = self.snapshot / "nested-benchmark"
        with self.assertRaisesRegex(ValueError, "overlap"):
            self.run_benchmark(apply=True)

    def test_cli_preview_apply_check_and_truncated_error(self):
        args = ["--benchmark", str(self.snapshot), "--out", str(self.out)]
        self.assertEqual(library_backup.main(args + ["--apply", "--dry-run"]), 0)
        self.assertFalse(self.out.exists())
        self.assertEqual(library_backup.main(args + ["--apply"]), 0)
        self.assertEqual(library_backup.main(args + ["--check"]), 0)
        (self.out / "zip64-stored" / "payload.zip").write_bytes(b"interrupted")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(library_backup.main(args + ["--check"]), 1)


if __name__ == "__main__":
    unittest.main()
