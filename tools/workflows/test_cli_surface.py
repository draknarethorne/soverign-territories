#!/usr/bin/env python3
"""Tests for the command-line surface of comfy_workflows.py: every command that changes files previews unless --apply, the readable options (--include, --mode, --only, inputs actions) map onto what the commands read, the old switches are gone,
and `status` shows candidates and finals. Run: python tools/workflows/test_cli_surface.py"""
import os
import pathlib
import subprocess
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402
from test_comfy_workflows import SUBPATH, World, setUpModule  # noqa: E402,F401

PRIME = {"nodes": [{"type": "SaveImage", "widgets_values": ["set-a/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime"]}], "id": "master"}


def deploy_args(**kw):
    base = dict(cmd="deploy", include=None, mode=None, curated=False, tests=False, shots=False, staged=False, existing=False, patch_only=False, new_only=False,
                overwrite=False, apply=False, dry_run=False)
    base.update(kw)
    return types.SimpleNamespace(**base)


class PreviewByDefaultTests(unittest.TestCase):
    def test_publish_launcher_previews_workspace_backup_option(self):
        with World() as w:
            target = w.tmp / "installs" / "Sovereign Females" / "ComfyUI" / "user" / "default" / "workflows"
            target.mkdir(parents=True)
            env = os.environ.copy()
            env["SOVEREIGN_TERRITORIES_INSTALLS_ROOT"] = str(w.tmp / "installs")
            for options in (["--workspace-backups", "--dry-run"],
                            ["alpha", "--workspace-backups", "--dry-run"],
                            ["motion", "--mode", "patch", "--workspace-backups", "--dry-run"]):
                with self.subTest(options=options):
                    result = subprocess.run(
                        ["cmd", "/c", "bin\\publish.cmd", "Female", "Sovereign Females", *options],
                        cwd=cw.ROOT, env=env, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("workspace backups:", result.stdout)
                    self.assertIn("(dry run)", result.stdout)
            self.assertFalse((w.tmp / "installs" / "Sovereign Females" / ".sovereign").exists())

    def test_workspace_backup_check_launcher_verifies_fixture(self):
        with World() as w:
            ws = "Sovereign Females"
            w.cfg["workspaces"][ws] = {"status": "active", "role": "x"}
            target = w.put(ws, "scene/Alice_Qwen_Scene_One.json")
            root = cw.workspace_backup_root(w.cfg, ws)
            run = "20261124-123456-000001"
            cw.workspace_backup(w.cfg, run, root, w.dir(ws), target)
            env = os.environ.copy()
            env["SOVEREIGN_TERRITORIES_INSTALLS_ROOT"] = str(w.tmp / "installs")
            result = subprocess.run(
                ["cmd", "/c", "bin\\workspace-backup-check.cmd", ws, run],
                cwd=cw.ROOT, env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("verified 1 workspace backup", result.stdout)

    def test_group_launcher_previews_scoped_backed_up_patch(self):
        with World() as w:
            target = w.tmp / "installs" / "Sovereign Females" / "ComfyUI" / "user" / "default" / "workflows"
            target.mkdir(parents=True)
            env = os.environ.copy()
            env["SOVEREIGN_TERRITORIES_INSTALLS_ROOT"] = str(w.tmp / "installs")
            result = subprocess.run(
                ["cmd", "/c", "bin\\deploy-group.cmd", "sovereign-females",
                 "--stage", "motion", "--mode", "patch", "--match", "Motion",
                 "--workspace-backups", "--dry-run"],
                cwd=cw.ROOT, env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("workspace backups:", result.stdout)
            self.assertIn("(dry run)", result.stdout)
            self.assertFalse((w.tmp / "installs" / "Sovereign Females" / ".sovereign").exists())

    def test_tidy_launcher_applies_scoped_motion_move(self):
        with World() as w:
            ws = w.tmp / "installs" / "Sovereign Females" / SUBPATH
            name = "Female_Qwen_Motion_Standing_HandOnHipPower.json"
            source = ws / "Female" / "Bench" / "motion" / "standing" / name
            source.parent.mkdir(parents=True)
            source.write_bytes((cw.ROOT / "workflows" / "sovereign-females" / "Female" / name).read_bytes())
            expected = source.read_bytes()
            env = os.environ.copy()
            env["SOVEREIGN_TERRITORIES_INSTALLS_ROOT"] = str(w.tmp / "installs")
            result = subprocess.run(
                ["cmd", "/c", "bin\\tidy.cmd", "Sovereign Females", "--stage", "motion",
                 "--group", "sovereign-females", "--apply"],
                cwd=cw.ROOT, env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(source.exists())
            self.assertEqual((ws / "Female" / "2_Studies" / "motions" / "standing" / name).read_bytes(),
                             expected)

    def test_pull_and_deploy_preview_unless_apply(self):
        with World() as w, mock.patch.object(cw, "CANDIDATES", w.repo / "_candidates"), mock.patch.object(cw, "FINALS", w.repo / "_final"), mock.patch.object(cw, "ROOT", w.tmp):
            w.master("Alice_Qwen_Alpha_1_Prime.json", PRIME)
            w.put("A-Home", "Alice_Qwen_Alpha_1_Prime_00004_.json", {"nodes": [], "id": "seed"})
            out, _ = w.run("pull", "-w", "A-Home", "--preview")
            self.assertFalse((w.repo / "_candidates").exists(), "a preview writes nothing")
            self.assertIn("Preview only: add --apply", out)
            w.run("pull", "-w", "A-Home", "--apply")
            self.assertTrue(list((w.repo / "_candidates").rglob("*.json")))
            out, _ = w.run("deploy", "--hero", "Alice", "-w", "A-Home", "--preview")
            self.assertIn("Preview only", out)

    def test_dry_run_still_works_and_needs_no_footer(self):
        with World() as w:
            out, _ = w.run("deploy", "--hero", "Alice", "-w", "A-Home", "--dry-run")
            self.assertNotIn("Preview only", out)

    def test_read_only_calls_never_say_preview(self):
        with World() as w, mock.patch.object(cw, "inputs_status") as shown:
            out, _ = w.run("inputs", "status", "--preview")
            self.assertNotIn("Preview only", out)
            shown.assert_called_once()


class SimplerOptionsTests(unittest.TestCase):
    def test_deploy_include_and_mode_set_the_switches_the_command_reads(self):
        a = deploy_args(include="shots,curated", mode="patch")
        cw.normalise(a)
        self.assertTrue(a.shots and a.curated and a.patch_only)
        self.assertFalse(a.tests or a.staged or a.finals)

    def test_unknown_include_is_refused(self):
        with self.assertRaises(SystemExit):
            cw.normalise(deploy_args(include="curated,nonsense"))

    def test_the_old_switches_are_gone(self):
        with World() as w:
            for argv in (("deploy", "--hero", "Alice", "--curated"), ("deploy", "--hero", "Alice", "--overwrite"), ("pull", "--shots"), ("inputs", "--pull"), ("inputs", "--reset")):
                out, code = w.run(*argv)
                self.assertEqual(code, 2, argv)

    def test_inputs_actions_map_to_the_switches(self):
        for action in ("pull", "reset", "fix", "status", "photos"):
            a = types.SimpleNamespace(cmd="inputs", action=action, target=None, status=False, pull=False, reset=False, fix=False, photos=False, set=None, apply=True, dry_run=False)
            cw.normalise(a)
            self.assertTrue(getattr(a, action), action)
        a = types.SimpleNamespace(cmd="inputs", action="set", target="Remiah", status=False, pull=False, reset=False, fix=False, photos=False, set=None, apply=True, dry_run=False)
        cw.normalise(a)
        self.assertEqual(a.set, "Remiah")
        with self.assertRaises(SystemExit):
            cw.normalise(types.SimpleNamespace(cmd="inputs", action="set", target=None, status=False, pull=False, reset=False, fix=False, photos=False, set=None, apply=True, dry_run=False))

    def test_pull_only_maps_to_the_kinds(self):
        for only, attr in (("shots", "shots"), ("templates", "templates"), ("finals", "only_finals")):
            a = types.SimpleNamespace(cmd="pull", only=only, apply=True, dry_run=False)
            cw.normalise(a)
            self.assertTrue(getattr(a, attr), only)
        a = types.SimpleNamespace(cmd="pull", only=None, apply=True, dry_run=False)
        cw.normalise(a)
        self.assertFalse(a.shots or a.templates or a.only_finals)

    def test_pull_only_shots_does_not_pull_candidates_or_finals(self):
        with World() as w, mock.patch.object(cw, "finals_pull") as pull_finals:
            w.put("A-Home", "zz_Shots/Alice/1_Alpha/Alice_Qwen_Alpha_1_Prime.json", {"nodes": [], "id": "shot"})
            w.put("A-Home", "zz_Candidates/set-a/Alice/Alice_Qwen_Alpha_1_Prime_00004_.json", {"nodes": [], "id": "candidate"})
            out, _ = w.run("pull", "-w", "A-Home", "--only", "shots", "--dry-run")
            pull_finals.assert_not_called()
            self.assertIn("zz_Shots/Alice/1_Alpha/Alice_Qwen_Alpha_1_Prime.json", out)
            self.assertNotIn("zz_Candidates", out)


class StatusShowsFinalsTests(unittest.TestCase):
    def test_status_lists_candidates_and_finals_by_default(self):
        with World() as w:
            w.master("Alice_Qwen_Alpha_1_Prime.json", PRIME)
            w.put("A-Home", "Alice_Qwen_Alpha_1_Prime_00004_.json")
            out, _ = w.run("status", "-w", "A-Home")
            self.assertIn("candidates and finals: 1 candidates (1 loose), 0 finals", out)


if __name__ == "__main__":
    unittest.main()
