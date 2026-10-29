"""Change selection must fail closed at dependency and process boundaries."""
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.validators import quality_selection as quality


class QualitySelectionTests(unittest.TestCase):
    def test_docs_only_runs_no_unit_or_mutation_suites(self):
        plan = quality.select(["docs/STATUS.md", "CONTRIBUTING.md"])
        self.assertFalse(plan["full"])
        self.assertEqual(quality.commands_for(plan), [])

    def test_reference_workflow_skips_intake_library_and_mutations(self):
        plan = quality.select(["tools/workflows/reference_rendering.py"])
        self.assertEqual(plan["scopes"], ["workflow"])
        self.assertFalse(plan["mutations"])
        commands = quality.commands_for(plan)
        self.assertTrue(any("tools.workflows.test_reference_rendering" in c for c in commands))
        self.assertFalse(any("tools.art.test_image_preparation" in c for c in commands))
        self.assertFalse(any("--isolated" in c for c in commands))

    def test_shared_workflow_config_selects_consumers(self):
        plan = quality.select(["tools\\workflows\\comfy_workflows.py"])
        self.assertEqual(set(plan["scopes"]), {"workflow", "intake", "library", "data"})

    def test_intake_selects_rebase_and_retention_consumers(self):
        plan = quality.select(["tools/art/intake_library/overlays.py"])
        commands = quality.commands_for(plan)
        for module in ("tools.art.test_overlays", "tools.art.test_retained_preparation",
                       "tools.art.likeness_library.tests.test_sandbox_reset"):
            self.assertTrue(any(module in c for c in commands), module)
        self.assertFalse(plan["mutations"])

    def test_schema_or_unknown_change_is_full_with_mutations(self):
        for path in ("data/art/_schema/image-preparation-pilot.schema.json",
                     "tools/validators/quality_selection.py", "requirements.txt",
                     "bin/validate.cmd", ".github/workflows/quality.yml", "new-area/source.py"):
            with self.subTest(path=path):
                plan = quality.select([path])
                self.assertTrue(plan["full"])
                self.assertTrue(plan["mutations"])

    def test_scoped_union_accounts_for_every_active_non_mutation_test(self):
        plan = {"full": False, "scopes": list(quality.SCOPES), "mutations": False}
        commands = quality.commands_for(plan)
        actual = {c[-1] for c in commands if "-m" in c and "unittest" in c}
        expected = {
            ".".join(p.relative_to(quality.ROOT).with_suffix("").parts)
            for p in (quality.ROOT / "tools").rglob("test_*.py")
            if "_archive" not in p.parts and p.name != "test_validate_data.py"
        }
        self.assertEqual(actual, expected)

    def test_bad_base_fails_instead_of_reporting_no_tests(self):
        with mock.patch.object(quality.subprocess, "run",
                               side_effect=quality.subprocess.CalledProcessError(128, ["git"])):
            with self.assertRaises(quality.subprocess.CalledProcessError):
                quality.changed_paths("missing-base")

    def test_ci_pull_request_uses_merge_base_and_not_synthetic_merge_commit(self):
        scratch = quality.ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            event = pathlib.Path(directory) / "event.json"
            event.write_text(json.dumps({"pull_request": {
                "base": {"sha": "base-tip"}, "head": {"sha": "pr-head"},
            }}), encoding="utf-8")
            with mock.patch.object(quality.subprocess, "run",
                                   return_value=mock.Mock(stdout="common-ancestor\n")) as git:
                with mock.patch.object(quality, "changed_paths", return_value=[]) as changed:
                    quality.ci_selection({
                        "GITHUB_EVENT_PATH": str(event), "GITHUB_EVENT_NAME": "pull_request",
                    })
            self.assertEqual(git.call_args.args[0], ["git", "merge-base", "base-tip", "pr-head"])
            changed.assert_called_once_with("common-ancestor", "pr-head")

    def test_new_branch_uses_full_fallback(self):
        scratch = quality.ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            event = pathlib.Path(directory) / "event.json"
            event.write_text(json.dumps({"before": "0" * 40}), encoding="utf-8")
            self.assertTrue(quality.ci_selection({
                "GITHUB_EVENT_PATH": str(event), "GITHUB_EVENT_NAME": "push",
            })["full"])

    def test_full_selection_uses_one_mutation_and_one_regression_launcher(self):
        commands = quality.commands_for(quality.select(["requirements.txt"]))
        self.assertEqual(len(commands), 2)
        self.assertIn("--isolated", commands[0])
        self.assertEqual(commands[1][-1], "bin\\validate.cmd")

    def test_data_edits_do_not_test_validator_mutations(self):
        self.assertFalse(quality.select(["data/art/heroes/example.json"])["mutations"])

    def test_ci_main_and_dispatch_are_full(self):
        scratch = quality.ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            event = pathlib.Path(directory) / "event.json"
            event.write_text("{}", encoding="utf-8")
            for kind, ref in (("push", "refs/heads/main"), ("workflow_dispatch", "refs/heads/work")):
                plan = quality.ci_selection({
                    "GITHUB_EVENT_PATH": str(event), "GITHUB_EVENT_NAME": kind, "GITHUB_REF": ref,
                })
                self.assertTrue(plan["full"])

    def test_ci_push_uses_exact_before_and_after(self):
        scratch = quality.ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            event = pathlib.Path(directory) / "event.json"
            event.write_text(json.dumps({"before": "abc123"}), encoding="utf-8")
            with mock.patch.object(quality, "changed_paths", return_value=["docs/STATUS.md"]) as changed:
                plan = quality.ci_selection({
                    "GITHUB_EVENT_PATH": str(event), "GITHUB_EVENT_NAME": "push",
                    "GITHUB_REF": "refs/heads/work", "GITHUB_SHA": "def456",
                })
            changed.assert_called_once_with("abc123", "def456")
            self.assertEqual(plan["scopes"], [])

    def test_process_failure_stops_and_children_use_ignored_scratch(self):
        with mock.patch.object(quality.subprocess, "run", return_value=mock.Mock(returncode=7)) as child:
            self.assertEqual(quality.run([["first"], ["must-not-run"]]), 7)
        child.assert_called_once()
        env = child.call_args.kwargs["env"]
        self.assertEqual(env["TEMP"], str((quality.ROOT / "tmp").resolve()))
        self.assertEqual(env["TMP"], env["TEMP"])
        self.assertEqual(env["TMPDIR"], env["TEMP"])

    def test_real_child_tempfile_is_below_repository_tmp(self):
        code = (
            "import pathlib,tempfile; "
            f"expected=pathlib.Path({str(quality.ROOT / 'tmp')!r}).resolve(); "
            "assert pathlib.Path(tempfile.gettempdir()).resolve()==expected; "
            "fixture=tempfile.TemporaryDirectory(); "
            "assert pathlib.Path(fixture.name).parent.resolve()==expected; "
            "fixture.cleanup()"
        )
        self.assertEqual(quality.run([[quality.sys.executable, "-c", code]]), 0)

    def test_local_changes_include_untracked_files_but_do_not_disable_ignore_rules(self):
        with mock.patch.object(quality.subprocess, "run", side_effect=[
            mock.Mock(stdout=b"docs/STATUS.md\0"),
            mock.Mock(stdout=b"tools/new_module.py\0"),
        ]) as child:
            self.assertEqual(quality.changed_paths("HEAD"), ["docs/STATUS.md", "tools/new_module.py"])
        self.assertIn("--exclude-standard", child.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
