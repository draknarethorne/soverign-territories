#!/usr/bin/env python3
"""Tests for the command-line surface of comfy_workflows.py: every command that changes files previews unless --apply, the old spellings still work and map onto the new ones,
and `status` shows candidates and finals. Run: python tools/workflows/test_cli_surface.py"""
import io
import contextlib
import pathlib
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402
from test_comfy_workflows import World  # noqa: E402

PRIME = {"nodes": [{"type": "SaveImage", "widgets_values": ["set-a/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime"]}], "id": "master"}


def deploy_args(**kw):
    base = dict(cmd="deploy", include=None, mode=None, curated=False, tests=False, shots=False, staged=False, existing=False, patch_only=False, new_only=False,
                overwrite=False, reset_inputs=False, apply=False, dry_run=False)
    base.update(kw)
    return types.SimpleNamespace(**base)


class PreviewByDefaultTests(unittest.TestCase):
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


class OldSpellingsTests(unittest.TestCase):
    def test_deploy_include_and_mode_set_the_old_switches(self):
        a = deploy_args(include="shots,curated", mode="patch")
        cw.normalise(a)
        self.assertTrue(a.shots and a.curated and a.patch_only)
        self.assertFalse(a.tests or a.staged or a.finals)

    def test_old_deploy_switches_still_work_and_say_what_replaces_them(self):
        a = deploy_args(curated=True, overwrite=True)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            cw.normalise(a)
        self.assertTrue(a.curated and a.overwrite)
        self.assertIn("--curated is now --include curated", err.getvalue())
        self.assertIn("--overwrite is now --mode overwrite", err.getvalue())

    def test_unknown_include_is_refused(self):
        with self.assertRaises(SystemExit):
            cw.normalise(deploy_args(include="curated,nonsense"))

    def test_inputs_actions_map_to_the_old_flags(self):
        for action in ("pull", "reset", "fix", "status"):
            a = types.SimpleNamespace(cmd="inputs", action=action, target=None, status=False, pull=False, reset=False, fix=False, set=None, apply=True, dry_run=False)
            cw.normalise(a)
            self.assertTrue(getattr(a, action), action)
        a = types.SimpleNamespace(cmd="inputs", action="set", target="Remiah", status=False, pull=False, reset=False, fix=False, set=None, apply=True, dry_run=False)
        cw.normalise(a)
        self.assertEqual(a.set, "Remiah")
        with self.assertRaises(SystemExit):
            cw.normalise(types.SimpleNamespace(cmd="inputs", action="set", target=None, status=False, pull=False, reset=False, fix=False, set=None, apply=True, dry_run=False))

    def test_pull_only_maps_to_the_old_kinds(self):
        for only, attr in (("shots", "shots"), ("templates", "templates"), ("finals", "only_finals")):
            a = types.SimpleNamespace(cmd="pull", only=only, shots=False, templates=False, apply=True, dry_run=False)
            cw.normalise(a)
            self.assertTrue(getattr(a, attr), only)


class StatusShowsFinalsTests(unittest.TestCase):
    def test_status_lists_candidates_and_finals_by_default(self):
        with World() as w:
            w.master("Alice_Qwen_Alpha_1_Prime.json", PRIME)
            w.put("A-Home", "Alice_Qwen_Alpha_1_Prime_00004_.json")
            out, _ = w.run("status", "-w", "A-Home")
            self.assertIn("candidates and finals: 1 candidates (1 loose), 0 finals", out)


if __name__ == "__main__":
    unittest.main()
