import io
import json
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import rebase_flow  # noqa: E402


def python_step(step_id, code, expect=None):
    step = {"id": step_id, "title": step_id, "argv": [sys.executable, "-c", code]}
    if expect:
        step["expect"] = expect
    return step


class RebaseFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = pathlib.Path(self.tmp.name)
        self.working = base / "Sandbox" / "Working"
        self.run = self.working / "_sandbox-state" / "trial"
        folder = base / "flow"
        folder.mkdir()
        self.paths = (folder, folder / "flow.json", folder / "flow.md")
        self.lines = []

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, flow, **kwargs):
        state = rebase_flow.load_state(self.paths[1], self.working, self.run, 4, flow)
        return rebase_flow.run_flow(
            flow, state, self.paths, measure=lambda: {"working": 2 * 1024 ** 3, "run": 0, "files": 3},
            echo=self.lines.append, launcher=list, heartbeat=3600, **kwargs)

    def test_real_flow_uses_launchers_with_core_flags_and_applied_backup(self):
        flow = rebase_flow.steps(self.working, self.run, 6)
        ids = [step["id"] for step in flow]
        self.assertEqual(ids, list(rebase_flow.NOV3_MINUTES))
        by_id = {step["id"]: step for step in flow}
        self.assertIn("--apply", by_id["backup"]["argv"])
        self.assertIn("--check", by_id["originals-check"]["argv"])
        self.assertEqual(by_id["reset-preview"]["expect"], '"resetReady": true')
        for step_id in ("intake-preview", "intake", "intake-check", "match-preview", "install", "install-check"):
            argv = by_id[step_id]["argv"]
            self.assertEqual(argv[0], "bin\\sandbox-rebase.cmd")
            self.assertEqual(argv[3:8], list(rebase_flow.REBASE_FLAGS))
        self.assertEqual(by_id["intake"]["argv"][-2:], ["--workers", "6"])
        self.assertIn("--preserve-legacy-derivatives", by_id["install"]["argv"])
        self.assertIn(str(self.run / "policy.json"), by_id["gallery-check"]["argv"])

    def test_flow_records_phases_photos_space_and_recap(self):
        flow = [
            python_step("one", "print('Install: staging copies in 12.5s')"),
            python_step("two", "print('Completed worker 1/2 (input 1): ok (a)'); "
                               "print('Completed worker 2/2 (input 2): ok (b)')"),
        ]
        self.assertEqual(self._run(flow), 0)
        state = json.loads(self.paths[1].read_text(encoding="utf-8"))
        self.assertEqual(state["steps"]["one"]["status"], "done")
        self.assertEqual(state["steps"]["one"]["phases"],
                         [{"phase": "Install: staging copies", "seconds": 12.5}])
        self.assertEqual(state["steps"]["two"]["photos"], {"done": 2, "total": 2})
        self.assertEqual(state["steps"]["two"]["space"]["working"], 2 * 1024 ** 3)
        recap = self.paths[2].read_text(encoding="utf-8")
        self.assertIn("| 1 | one | done |", recap)
        self.assertIn("Install: staging copies", recap)
        self.assertIn("2.00 GB", recap)
        self.assertTrue(any("one done in" in line for line in self.lines))
        log_lines = (self.paths[0] / "02-two.log").read_text(encoding="utf-8").splitlines()
        self.assertEqual(sum("Completed worker" in line for line in log_lines[1:]), 2)

    def test_missing_expected_text_fails_and_rerun_resumes_at_that_step(self):
        flow = [python_step("first", "print('fine')"),
                python_step("second", "print('OUT OF SYNC')", expect="IN SYNC")]
        self.assertEqual(self._run(flow), 1)
        state = json.loads(self.paths[1].read_text(encoding="utf-8"))
        self.assertEqual(state["steps"]["second"]["status"], "failed")
        self.assertIn("did not report", state["steps"]["second"]["note"])
        self.assertTrue(any("! OUT OF SYNC" in line for line in self.lines))

        fixed = [flow[0], python_step("second", "print('IN SYNC')", expect="IN SYNC")]
        self.lines.clear()
        self.assertEqual(self._run(fixed), 0)
        self.assertFalse(any("first:" in line and "===" in line for line in self.lines))
        state = json.loads(self.paths[1].read_text(encoding="utf-8"))
        self.assertEqual(state["steps"]["second"]["status"], "done")

    def test_nonzero_exit_fails_and_from_redoes_with_history(self):
        flow = [python_step("only", "import sys; sys.exit(3)")]
        self.assertEqual(self._run(flow), 1)
        self.assertIn("exit 3", json.loads(self.paths[1].read_text(encoding="utf-8"))["steps"]["only"]["note"])
        good = [python_step("only", "print('ok')")]
        self.assertEqual(self._run(good), 0)
        self.assertEqual(self._run(good, start="only"), 0)
        state = json.loads(self.paths[1].read_text(encoding="utf-8"))
        self.assertEqual([item["status"] for item in state["history"]], ["failed", "done"])
        self.assertEqual(
            [item["log"] for item in state["history"]],
            ["01-only.attempt-1.log", "01-only.attempt-2.log"],
        )

    def test_until_stops_after_named_step(self):
        flow = [python_step("a", "print(1)"), python_step("b", "print(2)")]
        self.assertEqual(self._run(flow, until="a"), 0)
        state = json.loads(self.paths[1].read_text(encoding="utf-8"))
        self.assertEqual(state["steps"]["b"]["status"], "pending")

    def test_installed_run_recovers_reports_without_reapplying_and_keeps_attempts(self):
        receipt = pathlib.Path(self.tmp.name) / "run.json"
        receipt.write_text('{"status": "applied"}', encoding="utf-8")
        step = python_step("install", "raise RuntimeError('must not reapply')")
        step["runReceipt"] = str(receipt)
        step["reportsArgv"] = [sys.executable, "-c", "print('reports refreshed')"]
        flow = [step]
        self.assertEqual(self._run(flow), 0)
        self.assertEqual(self._run(flow, start="install"), 0)
        log = (self.paths[0] / "01-install.log").read_text(encoding="utf-8")
        self.assertIn("reports refreshed", log)
        self.assertNotIn("must not reapply", log)
        self.assertTrue((self.paths[0] / "01-install.attempt-1.log").is_file())
        state = json.loads(self.paths[1].read_text(encoding="utf-8"))
        self.assertEqual(state["history"][0]["log"], "01-install.attempt-1.log")
        self.assertTrue(any("refreshing reports only" in line for line in self.lines))

    def test_recap_includes_failed_attempt_time_and_phases(self):
        flow = [python_step("install", "print('ok')")]
        state = rebase_flow.load_state(self.paths[1], self.working, self.run, 4, flow)
        state["history"] = [{
            "step": "install", "status": "failed", "seconds": 7200,
            "phases": [{"phase": "derivatives", "seconds": 6000}],
        }]
        state["steps"]["install"] = {"status": "done", "seconds": 600}
        recap = rebase_flow.render_markdown(state, flow)
        self.assertIn("2h10m", recap)
        self.assertIn("2 attempts", recap)
        self.assertIn("install (prior attempt) | derivatives | 1h40m", recap)

    def test_recap_flags_interrupted_attempt_without_recorded_duration(self):
        flow = [python_step("install", "print('ok')")]
        state = rebase_flow.load_state(self.paths[1], self.working, self.run, 4, flow)
        state["history"] = [{"step": "install", "status": "running"}]
        state["steps"]["install"] = {"status": "done", "seconds": 600}
        recap = rebase_flow.render_markdown(state, flow)
        self.assertIn("Took (recorded attempts)", recap)
        self.assertIn("2 attempts; 1 earlier attempt(s) untimed", recap)
        self.assertIn("10m00s", recap)

    def test_optional_previews_are_skipped_unless_requested(self):
        flow = [python_step("look", "print('preview')"), python_step("act", "print('apply')")]
        flow[0]["optional"] = True
        state = rebase_flow.load_state(self.paths[1], self.working, self.run, 4, flow)
        rebase_flow.apply_optional(state, flow, False)
        self.assertEqual(state["steps"]["look"]["status"], "skipped")
        self.assertEqual(rebase_flow.run_flow(flow, state, self.paths,
                                              measure=lambda: {"working": 0, "run": 0, "files": 0},
                                              echo=self.lines.append, launcher=list, heartbeat=3600), 0)
        self.assertFalse((self.paths[0] / "01-look.log").exists())
        self.assertEqual(state["steps"]["act"]["status"], "done")
        rebase_flow.apply_optional(state, flow, True)
        self.assertEqual(state["steps"]["look"]["status"], "pending")
        real = rebase_flow.steps(self.working, self.run, 4)
        self.assertEqual([step["id"] for step in real if step.get("optional")],
                         ["reset-preview", "intake-preview", "intake-check"])

    def test_progress_eta_and_heartbeat(self):
        live = {"id": "intake", "started": 0.0, "last_output": 700.0, "phases": [],
                "done": 11, "total": 101, "first_worker": 100.0, "first_done": 0}
        info = rebase_flow.progress(live, now=200.0)
        self.assertAlmostEqual(info["rate"], 6.6)
        self.assertAlmostEqual(info["eta"], 90 / 0.11)
        flow = rebase_flow.steps(self.working, self.run, 4)
        state = rebase_flow.load_state(self.paths[1], self.working, self.run, 4, flow)
        state["steps"]["intake"]["status"] = "running"
        line = rebase_flow.heartbeat_line(6, flow, live, state, now=1400.0)
        self.assertIn("11/101 photos (11%)", line)
        self.assertIn("QUIET", line)
        self.assertIn("flow remaining", line)

    def test_measure_space_groups_people_backup_and_run(self):
        for relative, size in (("Angels/a.png", 10), ("_backup/x", 5), ("_sandbox-state/trial/inputs/i", 7),
                               ("_sandbox-state/trial/run.json", 1)):
            path = self.working / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"x" * size)
        space = rebase_flow.measure_space(self.working, self.run)
        self.assertEqual((space["working"], space["people"], space["_backup"], space["run"], space["inputs"],
                          space["files"]), (23, 10, 5, 8, 7, 4))

    def test_redirected_console_is_line_buffered(self):
        (self.working.parent / "Source").mkdir(parents=True)
        self.working.mkdir()
        log = pathlib.Path(self.tmp.name) / "console.log"
        code = ("import sys; sys.path.insert(0, %r); import rebase_flow; import time; "
                "rebase_flow.FLOW_ROOT = rebase_flow.pathlib.Path(%r); "
                "rebase_flow.main(['--root', %r, '--run', 'trial']); time.sleep(30)"
                % (str(pathlib.Path(rebase_flow.__file__).parent), str(self.paths[0] / "f"), str(self.working)))
        import subprocess
        import time
        with log.open("w") as stream:
            process = subprocess.Popen([sys.executable, "-c", code], stdout=stream, stderr=subprocess.STDOUT)
            try:
                deadline = time.time() + 20
                while time.time() < deadline and "Preview only" not in log.read_text():
                    time.sleep(0.2)
                self.assertIn("Preview only", log.read_text())
            finally:
                process.kill()
                process.wait()

    def test_main_preview_and_check_write_nothing(self):
        (self.working.parent / "Source").mkdir(parents=True)
        self.working.mkdir()
        original = rebase_flow.FLOW_ROOT
        rebase_flow.FLOW_ROOT = self.paths[0] / "flows"
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(rebase_flow.main(["--root", str(self.working), "--run", "trial"]), 0)
                self.assertEqual(rebase_flow.main(["--root", str(self.working), "--run", "trial", "--check"]), 1)
            self.assertIn("Preview only", output.getvalue())
            self.assertIn("--apply", output.getvalue())
            self.assertFalse((self.paths[0] / "flows").exists())
            with self.assertRaisesRegex(ValueError, "plain folder name"):
                rebase_flow.main(["--root", str(self.working), "--run", "..\\x"])
            with self.assertRaisesRegex(ValueError, "unknown step"):
                rebase_flow.main(["--root", str(self.working), "--run", "t", "--from", "nope"])
        finally:
            rebase_flow.FLOW_ROOT = original


if __name__ == "__main__":
    unittest.main()
