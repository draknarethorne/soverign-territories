import pathlib
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import temporary_storage  # noqa: E402


class TemporaryStorageTests(unittest.TestCase):
    def test_normal_exit_removes_staging_and_lock(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = pathlib.Path(temporary)
            with temporary_storage.staging_directory(parent, ".preparation-") as stage:
                marker = stage / "output.bin"
                marker.write_bytes(b"partial output")
                self.assertTrue(stage.exists())
                self.assertTrue(stage.with_name(stage.name + ".lock").exists())
            self.assertFalse(stage.exists())
            self.assertFalse(stage.with_name(stage.name + ".lock").exists())

    def test_exception_removes_staging_and_lock(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = pathlib.Path(temporary)
            for exception in (RuntimeError, KeyboardInterrupt):
                with self.subTest(exception=exception.__name__):
                    with self.assertRaises(exception):
                        with temporary_storage.staging_directory(parent, ".preparation-") as stage:
                            stage.joinpath("partial.bin").write_bytes(b"partial")
                            raise exception("render failed")
            self.assertFalse(stage.exists())
            self.assertFalse(stage.with_name(stage.name + ".lock").exists())

    def test_preserve_on_error_leaves_owned_stage_for_recovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = pathlib.Path(temporary)
            with self.assertRaisesRegex(RuntimeError, "rollback required"):
                with temporary_storage.staging_directory(
                    parent, ".reset-", preserve_on_error=True
                ) as stage:
                    (stage / "journal.json").write_text("recover me", encoding="utf-8")
                    raise RuntimeError("rollback required")
            self.assertTrue(stage.is_dir())
            self.assertTrue(stage.with_name(stage.name + ".lock").is_file())
            self.assertEqual(
                temporary_storage.clean_orphaned_staging(parent, ".reset-"), [stage]
            )
            self.assertFalse(stage.exists())

    def test_orphan_with_released_lock_is_removed(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = pathlib.Path(temporary)
            orphan = parent / ".preparation-abandoned"
            orphan.mkdir()
            orphan.joinpath("partial.bin").write_bytes(b"partial")
            lock_path = orphan.with_name(orphan.name + ".lock")
            lock_path.write_bytes(b"\0")
            self.assertEqual(temporary_storage.clean_orphaned_staging(parent, ".preparation-"), [orphan])
            self.assertFalse(orphan.exists())
            self.assertFalse(lock_path.exists())

    def test_orphaned_lock_without_stage_is_removed(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = pathlib.Path(temporary)
            lock_path = parent / ".preparation-abandoned.lock"
            lock_path.write_bytes(b"\0")
            self.assertEqual(
                temporary_storage.clean_orphaned_staging(parent, ".preparation-"), []
            )
            self.assertFalse(lock_path.exists())

    def test_cleanup_failure_is_explicit_and_recoverable(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = pathlib.Path(temporary)
            with mock.patch.object(
                temporary_storage.shutil, "rmtree", side_effect=OSError("cleanup blocked")
            ):
                with self.assertRaisesRegex(OSError, "failed to clean owned staging directory"):
                    with temporary_storage.staging_directory(parent, ".preparation-") as stage:
                        (stage / "partial.bin").write_bytes(b"partial")
            self.assertTrue(stage.is_dir())
            self.assertTrue(stage.with_name(stage.name + ".lock").is_file())
            self.assertEqual(
                temporary_storage.clean_orphaned_staging(parent, ".preparation-"), [stage]
            )
            self.assertFalse(stage.exists())
            self.assertFalse(stage.with_name(stage.name + ".lock").exists())

    def test_unknown_staging_without_lock_is_preserved_and_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = pathlib.Path(temporary)
            unknown = parent / ".preparation-unknown"
            unknown.mkdir()
            with self.assertRaisesRegex(ValueError, "no ownership lock"):
                temporary_storage.clean_orphaned_staging(parent, ".preparation-")
            self.assertTrue(unknown.is_dir())

    def test_unrelated_and_locked_directories_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = pathlib.Path(temporary)
            unrelated = parent / ".other-temp"
            unrelated.mkdir()
            with temporary_storage.staging_directory(parent, ".preparation-") as active:
                self.assertEqual(temporary_storage.clean_orphaned_staging(parent, ".preparation-"), [])
                self.assertTrue(active.is_dir())
            self.assertTrue(unrelated.is_dir())

    def test_other_process_lock_prevents_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = pathlib.Path(temporary)
            script = (
                "import sys, time\n"
                f"sys.path.insert(0, {str(ROOT / 'tools/art')!r})\n"
                "import temporary_storage\n"
                "with temporary_storage.staging_directory(sys.argv[1], '.preparation-') as stage:\n"
                "    stage.joinpath('ready').write_text('yes')\n"
                "    time.sleep(3)\n"
            )
            process = subprocess.Popen(
                [sys.executable, "-c", script, str(parent)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            try:
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    ready = list(parent.glob(".preparation-*/ready"))
                    if ready:
                        break
                    if process.poll() is not None:
                        stdout, stderr = process.communicate()
                        self.fail(f"staging owner exited early: {stdout}\n{stderr}")
                    time.sleep(0.05)
                self.assertTrue(ready, "child did not create its staging directory")
                stage = ready[0].parent
                self.assertEqual(temporary_storage.clean_orphaned_staging(parent, ".preparation-"), [])
                self.assertTrue(ready[0].is_file())
            finally:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                    raise
            self.assertEqual(temporary_storage.clean_orphaned_staging(parent, ".preparation-"), [stage])
            self.assertFalse(stage.exists())


if __name__ == "__main__":
    unittest.main()
