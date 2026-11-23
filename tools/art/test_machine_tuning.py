import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
import machine_tuning as mt  # noqa: E402


class MachineTuningTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "tmp" / "machine-tuning-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temp.cleanup)
        self.base = pathlib.Path(temp.name)
        self.baseline = self.base / "machine-tuning.json"
        self.baseline.write_text(json.dumps({"preparation": {
            "maxWorkers": 8, "logicalCoresPerWorker": 4, "workerMemoryGiB": 3.5}}), encoding="utf-8")
        self.local = self.base / "machine-tuning.local.json"

    def resolve(self, requested=None, environ=None, cores=24, free=31.0):
        return mt.preparation_workers(requested, base_path=self.baseline, local_path=self.local,
                                      environ=environ or {}, cores=cores, free_gib=free)

    def test_capacity_differs_by_machine_without_a_local_file(self):
        self.assertEqual(self.resolve(cores=24, free=31.0), (6, "machine capacity"))
        self.assertEqual(self.resolve(cores=12, free=20.0), (3, "machine capacity"))
        self.assertEqual(self.resolve(cores=24, free=8.0), (2, "machine capacity"))
        self.assertEqual(self.resolve(cores=64, free=None), (1, "machine capacity"))
        self.assertEqual(self.resolve(cores=64, free=200.0), (8, "machine capacity"))

    def test_precedence_command_line_environment_local_capacity(self):
        self.local.write_text(json.dumps({"preparation": {"workers": 4, "threadsPerWorker": 5}}), encoding="utf-8")
        self.assertEqual(self.resolve(), (4, "machine-local machine-tuning.local.json"))
        self.assertEqual(self.resolve(environ={"ST_INTAKE_WORKERS": "2"}), (2, "ST_INTAKE_WORKERS"))
        self.assertEqual(self.resolve(5, environ={"ST_INTAKE_WORKERS": "2"}), (5, "command line"))
        self.assertEqual(mt.threads_per_worker(4, local_path=self.local, cores=24), 5)
        self.local.write_text(json.dumps({"preparation": {"workerMemoryGiB": 2.5}}), encoding="utf-8")
        self.assertEqual(mt.worker_memory_gib(self.baseline, self.local), 2.5)
        self.assertEqual(self.resolve(free=14.0), (5, "machine capacity"))
        self.local.unlink()
        self.assertEqual(mt.worker_memory_gib(self.baseline, self.local), 3.5)
        self.assertEqual(self.resolve(free=14.0), (4, "machine capacity"))
        self.assertEqual(mt.threads_per_worker(4, local_path=self.local, cores=24), 6)

    def test_invalid_values_refuse_instead_of_falling_back(self):
        with self.assertRaisesRegex(ValueError, "from 1 to 8"):
            self.resolve(9)
        for bad in ({"preparation": {"workers": 0}}, {"preparation": {"workers": 9}},
                    {"preparation": {"cores": 2}}, {"other": 1}):
            with self.subTest(bad=bad):
                self.local.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.resolve()

    def test_set_preview_and_apply_write_only_the_local_file(self):
        with mock.patch.object(mt, "BASELINE", self.baseline), mock.patch.object(mt, "LOCAL", self.local):
            self.assertEqual(mt._main(["set", "--preparation-workers", "6", "--evidence", "trial"]), 0)
            self.assertFalse(self.local.exists())
            self.assertEqual(mt._main(["set", "--preparation-workers", "6", "--threads-per-worker", "4",
                                       "--evidence", "trial", "--apply"]), 0)
            saved = json.loads(self.local.read_text(encoding="utf-8"))
            self.assertEqual(saved["preparation"], {"workers": 6, "threadsPerWorker": 4})
            self.assertEqual(saved["evidence"], "trial")
            self.assertEqual(mt._main(["clear", "--apply"]), 0)
            self.assertFalse(self.local.exists())
            with self.assertRaises(SystemExit):
                mt._main(["set", "--preparation-workers", "9", "--evidence", "x"])

    def test_tracked_baseline_is_valid_and_local_file_is_ignored(self):
        mt.baseline()
        self.assertIn("data/config/machine-tuning.local.json",
                      (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    unittest.main()
