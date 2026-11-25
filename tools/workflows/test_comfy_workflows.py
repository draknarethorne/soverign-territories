#!/usr/bin/env python3
"""Tests for the homes, the accepts rule and the guards of comfy_workflows.py, run against throwaway workspaces (nothing real is touched).

They pin down what must never regress: a set with no home workspace stops a deploy instead of landing somewhere else, a workspace that neither homes nor accepts a set
is refused, planned or missing workspaces are skipped, hand-made workflows (zz_ folders, zz_Curated_/test_ names) are never replaced, moved or removed, cleanup only
removes what a workspace is not home for and only when the home workspace has an identical copy, and empty folders are pruned (never the zz_ ones).

Run: python tools/workflows/test_comfy_workflows.py
"""
import contextlib
import copy
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402

SUBPATH = "ComfyUI/user/default/workflows"
MASTER = {"nodes": [], "id": "master"}


def setUpModule():
    environment = mock.patch.dict(os.environ)
    environment.start()
    unittest.addModuleCleanup(environment.stop)
    for name in cw.CONFIG_ROOT_OVERRIDES:
        os.environ.pop(name, None)


class World:
    """Heroes Alice (set-a: homes A-Home and Alice-Own), Bob (set-b: B-Home), Cleo (set-orphan: no home), Dana (set-planned: Planned workspace, status planned)
    and Eve (set-ghost: Ghost, active but not installed). Series accepts set-a on request, Brand accepts any set, Guest accepts nothing."""

    HEROES = {"Alice": "set-a", "Bob": "set-b", "Cleo": "set-orphan", "Dana": "set-planned", "Eve": "set-ghost"}

    def __enter__(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.cfg = copy.deepcopy(cw.load_cfg())
        self.cfg.update({
            "installsRoot": str(self.tmp / "installs"),
            "workflowsSubpath": SUBPATH,
            "exclude": ["X_*.json"],
            "stageTemplates": "ST?_*.json",
            "outputNamespaces": {},
            "workspaces": {
                "A-Home": {"status": "active", "role": "x"},
                "Alice-Own": {"status": "active", "role": "x"},
                "B-Home": {"status": "active", "role": "x"},
                "Series": {"status": "active", "role": "x", "accepts": ["set-a"]},
                "Brand": {"status": "active", "role": "x", "templates": True, "accepts": ["*"]},
                "Guest": {"status": "active", "role": "x"},
                "Planned": {"status": "planned", "role": "x"},
                "Ghost": {"status": "active", "role": "x"},
            },
            "homes": [
                {"groups": ["set-a"], "workspace": "A-Home"},
                {"groups": ["set-a"], "heroes": ["Alice"], "workspace": "Alice-Own"},
                {"groups": ["set-b"], "workspace": "B-Home"},
                {"groups": ["set-planned"], "workspace": "Planned"},
                {"groups": ["set-ghost"], "workspace": "Ghost"},
            ],
        })
        self.cfg["paths"].update({
            "productionRoot": str(self.tmp / "production"),
            "sandboxWorkingRoot": str(self.tmp / "sandbox" / "Working"),
            "modelCacheRoot": str(self.tmp / "models"),
            "inputsRoot": str(self.tmp / "inputs"),
            "outputRoot": str(self.tmp / "outputs"),
        })
        self.cfg["sharedInput"] = str(self.tmp / "shared-input")
        self.cfg["sharedOutput"] = str(self.tmp / "shared-output")
        for ws in self.cfg["workspaces"]:
            if ws != "Ghost":
                self.dir(ws).mkdir(parents=True)
        self.masters = {}
        self.cfg["storageRoots"]["backup"] = "_backup"
        self.patches = [
            mock.patch.object(cw, "load_cfg", lambda: self.cfg),
            mock.patch.object(cw, "hero_groups", lambda: dict(self.HEROES)),
            mock.patch.object(cw, "repo_files", lambda cfg: dict(self.masters)),
            mock.patch.object(cw, "curated_files", lambda folder=None: {}),
            mock.patch.object(cw, "shot_files", lambda: {}),
            mock.patch.object(cw, "WF", self.repo),
        ]
        for p in self.patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def dir(self, ws):
        return self.tmp / "installs" / ws / SUBPATH

    def master(self, name, content=None):
        hero = name.split("_", 1)[0]
        path = self.repo / self.HEROES[hero] / hero / name
        cw.write_wf(path, content or MASTER)
        self.masters[name] = (self.HEROES[hero], hero, path)

    def put(self, ws, rel, content=None):
        path = self.dir(ws) / rel
        cw.write_wf(path, content or MASTER)
        return path

    def run(self, *argv):
        out = io.StringIO()
        code = None
        argv = list(argv)
        if argv and argv[0] in cw.WRITES and "--dry-run" not in argv and "--apply" not in argv and "--preview" not in argv:
            argv.append("--apply")  # the commands preview unless --apply; these tests are about what they do when applying
        argv = [a for a in argv if a != "--preview"]
        with contextlib.redirect_stdout(out):
            try:
                cw.main(list(argv))
            except SystemExit as e:
                code = e.code
        return out.getvalue(), code

    def names(self, ws):
        return sorted(p.name for p in self.dir(ws).rglob("*.json"))

    def folders(self, ws):
        return sorted(p.relative_to(self.dir(ws)).as_posix() for p in self.dir(ws).rglob("*") if p.is_dir())


class StorageRootTests(unittest.TestCase):
    def test_workflow_fixtures_ignore_machine_root_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            installs = root / "machine-installs"
            for name in ("A-Home", "Alice-Own"):
                (installs / name / SUBPATH).mkdir(parents=True)
            env = os.environ.copy()
            env.update({name: str(root / name) for name in cw.CONFIG_ROOT_OVERRIDES})
            env["SOVEREIGN_TERRITORIES_INSTALLS_ROOT"] = str(installs)
            scripts = (
                (__file__, "RoutingTests.test_default_deploy_goes_to_every_home_only"),
                (str(pathlib.Path(__file__).with_name("test_finals_commands.py")),
                 "FinalsTests.test_loose_save_is_filed_by_its_name_and_the_tree_is_mirrored"),
                (str(pathlib.Path(__file__).with_name("test_cli_surface.py")),
                 "PreviewByDefaultTests.test_pull_and_deploy_preview_unless_apply"),
            )
            for script, test in scripts:
                with self.subTest(script=script):
                    result = subprocess.run(
                        [sys.executable, script, test], env=env, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(list(installs.rglob("*.json")), [])

    def test_storage_output_paths_are_relative_to_configured_root_and_refuse_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            cfg = {"storageRoots": {"reports": "operations/reports"}}
            reports = root / "operations" / "reports"
            for output in ("library", reports / "custom" / "page.html"):
                expected = reports / output if not pathlib.Path(output).is_absolute() else output
                self.assertEqual(cw.storage_output_path(cfg, "reports", output, root), expected)
            for output in ("../outside", root / "Various" / "gallery",
                           reports / ".." / "reports" / "page.html", root / "operations" / "reports-other"):
                with self.subTest(output=output), self.assertRaises(ValueError):
                    cw.storage_output_path(cfg, "reports", output, root)
            self.assertFalse(reports.exists())

    def test_storage_output_paths_refuse_reparse_points_even_inside_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            output = root / "_reports" / "linked" / "page.html"
            real = cw.is_reparse_point
            with mock.patch.object(cw, "is_reparse_point",
                                   side_effect=lambda path: path == output.parent or real(path)):
                with self.assertRaisesRegex(ValueError, "reparse point"):
                    cw.storage_output_path({}, "reports", output, root)

    def test_workspace_config_matches_versioned_schema(self):
        config = cw.load_cfg()
        self.assertEqual(config["schemaVersion"], 1)
        invalid = dict(config)
        invalid["storageRoots"] = {
            key: value for key, value in config["storageRoots"].items() if key != "backup"
        }
        with self.assertRaisesRegex(ValueError, "storageRoots"):
            cw.validate_config(invalid)
        invalid = dict(config)
        invalid["workflowsSubpath"] = "../outside"
        with self.assertRaisesRegex(ValueError, "contained relative path"):
            cw.validate_config(invalid)
        invalid["workflowsSubpath"] = "C:outside"
        with self.assertRaisesRegex(ValueError, "contained relative path"):
            cw.validate_config(invalid)
        invalid = dict(config)
        invalid["referenceWorkspace"] = "../outside"
        with self.assertRaisesRegex(ValueError, "single folder name"):
            cw.validate_config(invalid)
        invalid = copy.deepcopy(config)
        invalid["homes"][2]["excludeHeroes"] = "Female"
        with self.assertRaisesRegex(ValueError, "excludeHeroes"):
            cw.validate_config(invalid)
        invalid = copy.deepcopy(config)
        invalid["paths"]["outputRoot"] = invalid["paths"]["inputsRoot"]
        with self.assertRaisesRegex(ValueError, "inputsRoot and outputRoot must not overlap"):
            cw.validate_config(invalid)
        invalid = copy.deepcopy(config)
        invalid["sharedOutput"] = invalid["paths"]["productionRoot"]
        with self.assertRaisesRegex(ValueError, "sharedOutput must not overlap productionRoot"):
            cw.validate_config(invalid)
        invalid = copy.deepcopy(config)
        invalid["outputNamespaces"]["angel-primes"] = {"Female": "../outside"}
        with self.assertRaisesRegex(ValueError, "outputNamespaces"):
            cw.validate_config(invalid)
        invalid["outputNamespaces"]["angel-primes"]["Female"] = "missing"
        with self.assertRaisesRegex(ValueError, "no outputFolders mapping"):
            cw.validate_config(invalid)

    def test_environment_root_overrides_and_model_cache_expansion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            cfg = {"paths": {
                "productionRoot": "B:/production",
                "sandboxWorkingRoot": "B:/sandbox/Working",
                "modelCacheRoot": "%LOCALAPPDATA%/sovereign-territories",
            }}
            with mock.patch.dict(os.environ, {
                "SOVEREIGN_TERRITORIES_PRODUCTION_ROOT": str(root / "production"),
                "SOVEREIGN_TERRITORIES_SANDBOX_WORKING_ROOT": str(root / "sandbox" / "Working"),
                "SOVEREIGN_TERRITORIES_MODEL_CACHE_ROOT": str(root / "models"),
            }):
                self.assertEqual(cw.production_root(cfg), root / "production")
                self.assertEqual(cw.sandbox_work_root(cfg), root / "sandbox" / "Working")
                self.assertEqual(cw.model_cache_root(cfg), root / "models")
            with mock.patch.dict(os.environ, {
                "LOCALAPPDATA": str(root / "local"),
                "SOVEREIGN_TERRITORIES_MODEL_CACHE_ROOT": "",
            }, clear=False):
                self.assertEqual(
                    cw.model_cache_root({"paths": {"modelCacheRoot": "%LOCALAPPDATA%/sovereign-territories"}}),
                    root / "local" / "sovereign-territories",
                )
            config = cw.load_cfg()
            overrides = {
                "SOVEREIGN_TERRITORIES_INSTALLS_ROOT": str(root / "installs"),
                "SOVEREIGN_TERRITORIES_INPUTS_ROOT": str(root / "inputs"),
                "SOVEREIGN_TERRITORIES_OUTPUT_ROOT": str(root / "outputs"),
                "SOVEREIGN_TERRITORIES_SHARED_INPUT_ROOT": str(root / "shared-input"),
                "SOVEREIGN_TERRITORIES_SHARED_OUTPUT_ROOT": str(root / "shared-output"),
            }
            with mock.patch.dict(os.environ, overrides):
                self.assertEqual(cw.installs_root(config), root / "installs")
                self.assertEqual(cw.comfy_input_root(config), root / "inputs")
                self.assertEqual(cw.comfy_output_root(config), root / "outputs")
                self.assertEqual(cw.shared_input_root(config), root / "shared-input")
                self.assertEqual(cw.shared_output_root(config), root / "shared-output")
            with self.assertRaisesRegex(ValueError, "must be absolute"):
                cw.install_dir(config, "Sovereign Females", root="relative/installs")

    def test_configured_environment_roots_must_be_absolute(self):
        with self.assertRaisesRegex(ValueError, "must be absolute"):
            cw.production_root({"paths": {"productionRoot": "relative/production"}})
        with self.assertRaisesRegex(ValueError, "unset environment variable"):
            cw.model_cache_root({"paths": {"modelCacheRoot": "%MISSING_MODEL_ROOT%/models"}})

    def test_configuration_receipt_fingerprints_effective_roots(self):
        config = cw.load_cfg()
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            overrides = {name: "" for name in cw.CONFIG_ROOT_OVERRIDES}
            with mock.patch.dict(os.environ, overrides, clear=False):
                first_paths = {
                    "productionRoot": cw.production_root(config),
                    "sandboxWorkingRoot": cw.sandbox_work_root(config),
                    "inputsRoot": root / "inputs-a",
                }
                first = cw.configuration_receipt(config, first_paths)
                reordered = cw.configuration_receipt(
                    config, dict(reversed(list(first_paths.items())))
                )
                self.assertEqual(
                    first["effectiveConfigurationSha256"],
                    reordered["effectiveConfigurationSha256"],
                )
                self.assertEqual(
                    first["sourceConfigurationSha256"],
                    reordered["sourceConfigurationSha256"],
                )
                self.assertEqual(len(first["effectiveConfigurationSha256"]), 64)
                self.assertEqual(
                    first["resolvedPaths"]["inputsRoot"],
                    str((root / "inputs-a").resolve()),
                )
                storage = cw.storage_configuration_receipt(
                    config,
                    root / "sandbox" / "Working",
                    {"runOutput": root / "sandbox" / "Working" / "_reports" / "run"},
                )
                self.assertEqual(
                    storage["resolvedPaths"]["libraryRoot"],
                    str((root / "sandbox" / "Working").resolve()),
                )
                self.assertEqual(
                    {
                        name.removeprefix("storageRoots.")
                        for name in storage["resolvedPaths"]
                        if name.startswith("storageRoots.")
                    },
                    set(cw.STORAGE_ROOT_DEFAULTS),
                )

                with mock.patch.dict(os.environ, {
                    "SOVEREIGN_TERRITORIES_INPUTS_ROOT": str(root / "inputs-b"),
                }):
                    second_paths = dict(first_paths)
                    second_paths["inputsRoot"] = cw.comfy_input_root(config)
                    second = cw.configuration_receipt(config, second_paths)

                self.assertEqual(
                    first["sourceConfigurationSha256"],
                    second["sourceConfigurationSha256"],
                )
                self.assertNotEqual(
                    first["effectiveConfigurationSha256"],
                    second["effectiveConfigurationSha256"],
                )
                self.assertEqual(
                    second["environmentOverrides"][
                        "SOVEREIGN_TERRITORIES_INPUTS_ROOT"
                    ],
                    str(root / "inputs-b"),
                )

    def test_config_writes_validate_and_publish_atomically(self):
        config = cw.load_cfg()
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory) / "workspaces.json"
            target.write_text("previous configuration\n", encoding="utf-8")
            original_storage_root = cw.storage_root
            with mock.patch.object(cw, "CFG_PATH", target), mock.patch.object(
                cw,
                "storage_root",
                side_effect=lambda cfg, name, root=None: (
                    pathlib.Path(directory) / "staging"
                    if name == "temporary"
                    else original_storage_root(cfg, name, root)
                ),
            ):
                cw.write_cfg_text(json.dumps(config) + "\n")
                saved = target.read_text(encoding="utf-8")
                self.assertEqual(json.loads(saved), config)
                invalid = dict(config)
                invalid["storageRoots"] = {}
                with self.assertRaisesRegex(ValueError, "storageRoots"):
                    cw.write_cfg_text(json.dumps(invalid) + "\n")
                self.assertEqual(target.read_text(encoding="utf-8"), saved)
                with mock.patch.object(cw.os, "replace", side_effect=PermissionError("locked")):
                    with self.assertRaisesRegex(PermissionError, "locked"):
                        cw.write_cfg_text(saved)
                self.assertEqual(target.read_text(encoding="utf-8"), saved)
            self.assertEqual(
                list((pathlib.Path(directory) / "staging" / "config-staging").iterdir()),
                [],
            )

    def test_defaults_and_relative_overrides_resolve_beneath_working_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            cfg = {"paths": {"workRoot": str(root)}}
            self.assertEqual(cw.storage_root(cfg, "reports"), root / "_reports")
            cfg["storageRoots"] = {"reports": "operations/reports"}
            self.assertEqual(cw.storage_root(cfg, "reports"), root / "operations" / "reports")
            self.assertEqual(cw.storage_root(cfg, "backup", root=root / "sandbox"),
                             root / "sandbox" / "_backup")

    def test_absolute_override_must_stay_beneath_working_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            cfg = {"storageRoots": {"reports": str(root / "custom-reports")}}
            self.assertEqual(cw.storage_root(cfg, "reports", root=root),
                             root / "custom-reports")
            cfg["storageRoots"]["reports"] = str(root.parent / "outside")
            with self.assertRaisesRegex(ValueError, "must remain under"):
                cw.storage_root(cfg, "reports", root=root)

    def test_invalid_names_and_configuration_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            with self.assertRaisesRegex(ValueError, "unknown storage root"):
                cw.storage_root({}, "unknown", root=root)
            with self.assertRaisesRegex(ValueError, "must be an object"):
                cw.storage_root({"storageRoots": []}, "reports", root=root)
            with self.assertRaisesRegex(ValueError, "non-empty path"):
                cw.storage_root({"storageRoots": {"reports": ""}}, "reports", root=root)
            with self.assertRaisesRegex(ValueError, "must remain under"):
                cw.storage_root({"storageRoots": {"reports": "../outside"}}, "reports", root=root)
            with self.assertRaisesRegex(ValueError, "cannot be the working root"):
                cw.storage_root({"storageRoots": {"reports": "."}}, "reports", root=root)

    def test_storage_roots_must_not_overlap(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            cfg = {"storageRoots": {
                "reports": "operations",
                "backup": "operations/backups",
            }}
            with self.assertRaisesRegex(ValueError, "overlap"):
                cw.storage_root(cfg, "reports", root=root)

    def test_storage_roots_cannot_overlap_active_photo_categories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for value in ("Prospects", "Prospects/Seed"):
                cfg = {"storageRoots": {"reports": value}}
                with self.subTest(value=value):
                    with self.assertRaisesRegex(ValueError, "overlap active photo category"):
                        cw.storage_root(cfg, "reports", root=root)

    def test_storage_roots_cannot_overlap_reserved_photo_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for value in ("_archive", "_archive/junk"):
                cfg = {"storageRoots": {"junk": value}}
                with self.subTest(value=value):
                    with self.assertRaisesRegex(ValueError, "reserved photo archive"):
                        cw.storage_root(cfg, "junk", root=root)

    def test_storage_roots_reject_unknown_configuration_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            cfg = {"storageRoots": {"report": "reports"}}
            with self.assertRaisesRegex(ValueError, "unknown storageRoots entries"):
                cw.storage_root(cfg, "reports", root=root)

    def test_storage_roots_reject_reparse_points(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            target = root / "target"
            target.mkdir()
            junction = root / "alias"
            if os.name == "nt":
                result = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode:
                    self.skipTest(f"directory junctions are unavailable: {result.stderr}")
            else:
                try:
                    os.symlink(target, junction, target_is_directory=True)
                except (OSError, NotImplementedError) as exc:
                    self.skipTest(f"directory symlinks are unavailable: {exc}")
            cfg = {"storageRoots": {"reports": "alias/reports"}}
            with self.assertRaisesRegex(ValueError, "junction or reparse point"):
                cw.storage_root(cfg, "reports", root=root)


class FlowTests(unittest.TestCase):
    """A flow is a second way to run the Prime: the same prompt, another incoming image, its own workflows beside the normal ones."""

    def world(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        d = tmp / "set-a" / "Alice" / "1_Alpha" / "1_Prime"
        d.mkdir(parents=True)
        (d / "Alice_Alpha_1_Prime.txt").write_text("=== x ===\n\nprompt:\n\nhello\n\n----------\nnegative prompt:\n\nbad\n")
        b = tmp / "set-a" / "Alice" / "1_Alpha" / "2_Bare"
        b.mkdir(parents=True)
        (b / "Alice_Alpha_2_Bare.txt").write_text("=== x ===\n\nprompt:\n\nbare\n\n----------\nnegative prompt:\n\nbad\n")
        p = mock.patch.object(cw, "PROMPTS", tmp)
        p.start()
        self.addCleanup(p.stop)
        return tmp

    def test_flow_workflows_sit_beside_the_normal_ones_and_only_for_heroes_with_a_flow_image(self):
        self.world()
        self.assertEqual(cw.flow_suffix("alternate"), "Alternate")
        self.assertEqual(cw.flow_suffix("tight-crop"), "TightCrop")
        cfg = {"photos": {"Alice": "alice_image_1_944x1104.png"}}
        self.assertEqual([i["name"] for i in cw.prompt_index(cfg)], ["Alice_Qwen_Alpha_1_Prime", "Alice_Qwen_Alpha_2_Bare"], "no flows, no variants")
        cfg["flows"] = {"alternate": {"photos": {"Alice": "alice_image_1_alt_944x1104.png"}}, "other": {"photos": {}}}
        names = {i["name"]: i for i in cw.prompt_index(cfg)}
        self.assertEqual(sorted(names), ["Alice_Qwen_Alpha_1_Prime", "Alice_Qwen_Alpha_1_Prime_Alternate", "Alice_Qwen_Alpha_2_Bare"], "only the Prime has flows")
        v = names["Alice_Qwen_Alpha_1_Prime_Alternate"]
        self.assertEqual((v["flow"], v["path"], v["prefix"].rsplit("/", 1)[-1]), ("alternate", names["Alice_Qwen_Alpha_1_Prime"]["path"], "Alice_Qwen_Alpha_1_Prime_Alternate"), "the same prompt, its own output prefix")
        self.assertNotIn("flow", names["Alice_Qwen_Alpha_1_Prime"])
        self.assertEqual(cw.flow_index(cfg), {"Alice_Qwen_Alpha_1_Prime_Alternate": "alternate", "Alice_FireRed_Alpha_1_Prime_Alternate": "alternate"})
        self.assertEqual(cw.flow_photo(cfg, "alternate", "Alice"), "alice_image_1_alt_944x1104.png")
        self.assertIsNone(cw.flow_photo(cfg, "alternate", "Bob"))

    def test_firered_gets_an_identity_lock_in_front_of_the_prime_and_nothing_else_changes(self):
        tmp = self.world()
        face = tmp / "lock.txt"
        face.write_text("Identity lock: use the face.\n")
        with mock.patch.object(cw, "ROOT", tmp):
            cfg = {"engines": {"firered": {"primeFace": "lock.txt"}}}
            prime = {"engine": "firered", "stage": "alpha", "family": None, "stem": "Alice_Alpha_1_Prime"}
            self.assertEqual(cw.engine_prompt(cfg, prime, "hello"), "Identity lock: use the face.\n\nhello")
            self.assertEqual(cw.engine_prompt(cfg, {**prime, "stem": "Alice_Alpha_1_Prime_Alternate"}, "hello"), "Identity lock: use the face.\n\nhello", "the flow's Prime too")
            self.assertEqual(cw.engine_prompt(cfg, {**prime, "engine": "qwen"}, "hello"), "hello", "Qwen is not touched")
            self.assertEqual(cw.engine_prompt(cfg, {**prime, "stem": "Alice_Alpha_2_Bare"}, "hello"), "hello", "nor is any later stage")
            self.assertEqual(cw.engine_prompt({"engines": {"firered": {}}}, prime, "hello"), "hello", "off unless configured")

    def test_set_inputs_with_an_alternate_flow_keeps_the_normal_photo(self):
        cfg = {"photos": {"Alice": "alice_image_1_944x1104.png"}, "inputs": {}}
        args = types.SimpleNamespace(set="alice", flow="alternate", photo="alice_image_1_alt_944x1104.png", dry_run=True, prime=None, bare=None, apose=None, heels=None, scene=None, polish=None)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cw.set_inputs(cfg, args)
        self.assertEqual(cfg["flows"]["alternate"]["photos"], {"Alice": "alice_image_1_alt_944x1104.png"})
        self.assertEqual(cfg["photos"]["Alice"], "alice_image_1_944x1104.png", "the normal flow is untouched")
        self.assertIn("flow alternate", out.getvalue())
        args.photo = None
        with self.assertRaises(SystemExit):
            cw.set_inputs(cfg, args)


class FirstShotTests(unittest.TestCase):
    """First-shot experiments in 2_Bare still start from the photo like the Prime."""

    def test_generic_male_home_is_planned_not_angel_primes(self):
        cfg = cw.load_cfg()
        self.assertEqual(cw.home_workspaces(cfg, "angel-primes", "Male"), [])
        self.assertEqual(cw.home_workspaces(cfg, "sovereign-males", "Male"), ["Sovereign Males"])
        ready, reason = cw.workspace_ready(cfg, "Sovereign Males")
        self.assertFalse(ready)
        self.assertIn("planned", reason)

    def test_reference_only_prompts_are_not_generic_workflows(self):
        cfg = cw.load_cfg()
        with tempfile.TemporaryDirectory(dir=cw.ROOT / "tmp") as tmp:
            prompts = pathlib.Path(tmp)
            root = prompts / "sovereign-females" / "Female"
            for path in cw.reference_prompt_bindings.SHARED_PROMPTS.values():
                target = root.joinpath(*pathlib.PurePosixPath(path).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture", encoding="utf-8")
            for path in ("0_Edit/cleanup/Female_Edit_Cleanup_Audition.txt",
                         "1_Alpha/1_Prime/Female_Alpha_1_Prime.txt"):
                target = root.joinpath(*pathlib.PurePosixPath(path).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture", encoding="utf-8")
            with mock.patch.object(cw, "PROMPTS", prompts):
                items = cw.prompt_index(cfg)
            self.assertEqual({item["stem"] for item in items},
                             {"Female_Edit_Cleanup_Audition", "Female_Alpha_1_Prime"})

    def test_generic_namespace_routes_without_an_alpha_division(self):
        cfg = cw.load_cfg()
        with tempfile.TemporaryDirectory(dir=cw.ROOT / "tmp") as tmp:
            prompts = pathlib.Path(tmp)
            for parts, hero in (
                (("sovereign-females", "Female"), "Female"),
                (("sovereign-males", "Male"), "Male"),
                (("angel-primes", "female", "Angelica"), "Angelica"),
            ):
                folder = prompts.joinpath(*parts) / "0_Edit" / "cleanup"
                folder.mkdir(parents=True)
                (folder / f"{hero}_Edit_Cleanup.txt").write_text("fixture", encoding="utf-8")
            with mock.patch.object(cw, "PROMPTS", prompts):
                items = cw.prompt_index(cfg)
                indexed = {item["hero"]: item for item in items}
                self.assertEqual(len(items), 3)
                self.assertEqual(cw.hero_homes()["Female"], ("sovereign-females", None))
        female = indexed["Female"]
        self.assertEqual(female["group"], "sovereign-females")
        self.assertEqual(female["prefix"], "sovereign-females/Female/0_Edit/cleanup/Female_Qwen_Edit_Cleanup")
        self.assertEqual(indexed["Male"]["prefix"], "sovereign-males/Male/0_Edit/cleanup/Male_Qwen_Edit_Cleanup")
        self.assertEqual(indexed["Angelica"]["prefix"], "angel-primes/female/Angelica/0_Edit/cleanup/Angelica_Qwen_Edit_Cleanup")
        wf = {"nodes": [{"type": "SaveImage", "widgets_values": [female["prefix"]]}]}
        with mock.patch.object(cw, "load_cfg", return_value=cfg):
            self.assertEqual(cw.workspace_subdir("Sovereign Females", wf),
                             pathlib.Path("Female", "0_Edit", "cleanup"))
        self.assertEqual(cfg["paths"]["outputFolders"]["sovereign-females"], "Sovereign Females")
        parsed = {"hero": "Female", "stem": "Female_Qwen_Edit_Cleanup"}
        with mock.patch.object(cw, "hero_groups", return_value={"Female": "sovereign-females"}):
            self.assertEqual(cw.final_image_dest(cfg, parsed, wf),
                             cw.ASSETS / "sovereign-females" / "Female" / "0_Edit" / "cleanup" / "Female_Qwen_Edit_Cleanup.png")
        with tempfile.TemporaryDirectory(dir=cw.ROOT / "tmp") as tmp:
            root = pathlib.Path(tmp)
            image = root / "Sovereign Females" / (female["prefix"] + "_00001_.png")
            image.parent.mkdir(parents=True)
            image.write_bytes(b"fixture")
            with mock.patch.object(cw, "output_root", return_value=root):
                self.assertEqual(cw.final_image_source(cfg, wf, "00001"), image)

    def test_output_organizer_keeps_legacy_and_sorts_new_namespace(self):
        import organize_outputs

        cfg = cw.load_cfg()
        with tempfile.TemporaryDirectory(dir=cw.ROOT / "tmp") as tmp:
            root = pathlib.Path(tmp)
            legacy = root / "Angel Primes" / "angel-primes" / "alpha" / "Female" / "0_Edit" / "Female_Qwen_Edit_Cleanup_00001_.png"
            unscoped = root / "Female" / "0_Edit" / "Female_Qwen_Edit_Cleanup_00003_.png"
            source = root / "Sovereign Females" / "sovereign-females" / "Female" / "0_Edit" / "Female_Qwen_Edit_Cleanup_00002_.png"
            for path in (legacy, unscoped, source):
                path.parent.mkdir(parents=True)
                path.write_bytes(b"fixture")
            item = {"stem": "Female_Edit_Cleanup", "prefix": "sovereign-females/Female/0_Edit/cleanup/Female_Qwen_Edit_Cleanup"}
            args = ["organize_outputs.py", "--hero", "Female", "--output", str(root)]
            with mock.patch.object(cw, "load_cfg", return_value=cfg), \
                 mock.patch.object(cw, "hero_groups", return_value={"Female": "sovereign-females"}), \
                 mock.patch.object(cw, "hero_dir", return_value="Female"), \
                 mock.patch.object(cw, "output_roots", return_value=[root]), \
                 mock.patch.object(cw, "prompt_index", side_effect=lambda _cfg, engine: [item] if engine == "qwen" else []), \
                 mock.patch.object(sys, "argv", args), \
                 contextlib.redirect_stdout(io.StringIO()):
                organize_outputs.main()
                self.assertTrue(source.exists())
                sys.argv.append("--apply")
                organize_outputs.main()
            destination = root / "Sovereign Females" / "sovereign-females" / "Female" / "0_Edit" / "cleanup" / source.name
            self.assertEqual(destination.read_bytes(), b"fixture")
            self.assertFalse(source.exists())
            self.assertEqual(legacy.read_bytes(), b"fixture")
            self.assertEqual(unscoped.read_bytes(), b"fixture")

    def test_output_organizer_preserves_unmapped_hero_behavior(self):
        import organize_outputs

        cfg = cw.load_cfg()
        with tempfile.TemporaryDirectory(dir=cw.ROOT / "tmp") as tmp:
            root = pathlib.Path(tmp)
            source = root / "Angelica" / "0_Edit" / "Angelica_Qwen_Edit_Cleanup_00001_.png"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"fixture")
            item = {"stem": "Angelica_Edit_Cleanup", "prefix": "angel-primes/female/Angelica/0_Edit/cleanup/Angelica_Qwen_Edit_Cleanup"}
            args = ["organize_outputs.py", "--hero", "Angelica", "--output", str(root), "--apply"]
            with mock.patch.object(cw, "load_cfg", return_value=cfg), \
                 mock.patch.object(cw, "hero_groups", return_value={"Angelica": "angel-primes"}), \
                 mock.patch.object(cw, "hero_dir", return_value="female/Angelica"), \
                 mock.patch.object(cw, "output_roots", return_value=[root]), \
                 mock.patch.object(cw, "prompt_index", side_effect=lambda _cfg, engine: [item] if engine == "qwen" else []), \
                 mock.patch.object(sys, "argv", args), \
                 contextlib.redirect_stdout(io.StringIO()):
                organize_outputs.main()
            destination = root / "Angel Primes" / "angel-primes" / "female" / "Angelica" / "0_Edit" / "cleanup" / source.name
            self.assertEqual(destination.read_bytes(), b"fixture")
            self.assertFalse(source.exists())

    def test_the_experiment_folders_and_the_family_round_trip(self):
        lay = cw.art_layout
        card = {"stage": "alpha", "artId": "angelica-alpha-bare-base", "components": {}}
        self.assertEqual(lay.family(card, "angel-primes"), ["base", "bare-base"])
        card["artId"] = "angelica-alpha-neutral-base"
        self.assertEqual(lay.family(card, "angel-primes"), ["base", "neutral-base"])
        card["artId"] = "angelica-alpha-1b-bare-base"
        self.assertEqual(lay.family(card, "angel-primes"), ["base", "bare-base"])
        dirs = lay.dirs_for("alpha", ["base", "bare-base"])
        self.assertEqual(dirs, ["1_Alpha", "2_Bare", "bare-base"])
        self.assertEqual(lay.parse_dirs(dirs), ("alpha", ["base", "bare-base"]))
        self.assertEqual(lay.dirs_for("alpha", ["base", "neutral-base"]), ["1_Alpha", "2_Bare", "neutral-base"], "P2 and P3 never share a folder")
        self.assertEqual(lay.parse_dirs(["1_Alpha", "1b_Experiments", "bare-base"]), ("alpha", ["base", "bare-base"]))
        self.assertEqual(lay.parse_dirs(["1_Alpha", "2_Bare"]), ("alpha", ["bare"]))
        self.assertEqual(lay.parse_dirs(["1_Alpha", "2_Bare", "other"]), ("alpha", ["bare", "other"]))
        self.assertEqual(lay.parse_dirs(["1_Alpha", "1_Prime"]), ("alpha", []), "the Prime is untouched")

    def test_motion_studies_round_trip_and_keep_legacy_paths_readable(self):
        lay = cw.art_layout
        self.assertEqual(lay.dirs_for("motion", ["standing"]), ["2_Studies", "motions", "standing"])
        self.assertEqual(lay.parse_dirs(["2_Studies", "motions", "standing"]), ("motion", ["standing"]))
        self.assertEqual(lay.parse_dirs(["Bench", "motion", "standing"]), ("motion", ["standing"]))

    def test_celestial_edits_keep_prime_input_under_outfits(self):
        lay = cw.art_layout
        cfg = cw.load_cfg()
        card = {"stage": "alpha", "artId": "angelica-alpha-outfit-celestial-core"}
        family = lay.family(card, "angel-primes")
        self.assertEqual(family, ["outfits", "celestial"])
        dirs = lay.dirs_for("alpha", family)
        self.assertEqual(dirs, ["1_Alpha", "4_Outfits", "celestial"])
        self.assertEqual(lay.parse_dirs(dirs), ("alpha", family))
        self.assertEqual(cw.input_role(cfg, "Angelica", "alpha", family, "Angelica_Qwen_Alpha_2b_CelestialCore"), "prime")
        self.assertEqual(cw.default_input(cfg, "Angelica", "alpha", family, "Angelica_Qwen_Alpha_4_Outfits_CelestialCore"), cfg["inputs"]["Angelica"]["prime"])
        self.assertEqual(cw.input_role(cfg, "Female", "alpha", family, "Female_Qwen_Alpha_4_Outfits_Covered_Celestial"), "photo")

    def test_outfit_family_routes_prompt_workflow_output_and_photo_input(self):
        lay = cw.art_layout
        cfg = cw.load_cfg()
        for group, division, hero in (
            ("sovereign-females", None, "Female"),
            ("drakn-sisters", None, "Drakness"),
        ):
            with self.subTest(hero=hero):
                card = {"stage": "alpha", "artId": f"{hero.lower()}-alpha-outfit-source-apose"}
                family = lay.family(card, group)
                self.assertEqual(family, ["outfits"])
                dirs = lay.dirs_for("alpha", family)
                self.assertEqual(dirs, ["1_Alpha", "4_Outfits"])
                self.assertEqual(lay.parse_dirs(dirs), ("alpha", family))
                output = lay.output_for(card, group, hero, f"{hero}_Alpha_4_Outfits_Source_APose", cw.ROOT, division)
                self.assertEqual(lay.split_output(output)[3], dirs)
                self.assertEqual(cw.input_role(cfg, hero, "alpha", family), "photo")
                self.assertEqual(cw.default_input(cfg, hero, "alpha", family), cfg["photos"][hero])

        with tempfile.TemporaryDirectory(dir=cw.ROOT / "tmp") as tmp:
            prompts = pathlib.Path(tmp)
            for sub, stem in (
                ("1_Prime", "Female_Alpha_1_Prime"),
                ("1_Prime", "Female_Alpha_1_Prime_Outfit_Relaxed"),
                ("4_Outfits", "Female_Alpha_4_Outfits_Source_APose"),
            ):
                folder = prompts / "sovereign-females" / "Female" / "1_Alpha" / sub
                folder.mkdir(parents=True, exist_ok=True)
                (folder / f"{stem}.txt").write_text("fixture", encoding="utf-8")
            with mock.patch.object(cw, "PROMPTS", prompts):
                indexed = cw.prompt_index(cfg)
            items = {item["name"]: item for item in indexed}
            prime = items["Female_Qwen_Alpha_1_Prime"]
            outfit = items["Female_Qwen_Alpha_4_Outfits_Source_APose"]
            self.assertEqual(prime["family"], [])
            self.assertNotIn("Female_Qwen_Alpha_1_Prime_Outfit_Relaxed", items)
            self.assertEqual(outfit["family"], ["outfits"])
            self.assertEqual(outfit["prefix"], "sovereign-females/Female/1_Alpha/4_Outfits/Female_Qwen_Alpha_4_Outfits_Source_APose")
            self.assertFalse(cw.takes_photo(outfit))
            self.assertEqual(len(items), len(indexed))
            wf = {"nodes": [{"type": "SaveImage", "widgets_values": [outfit["prefix"]]}]}
            with mock.patch.object(cw, "load_cfg", return_value=cfg):
                subdir = cw.workspace_subdir("Sovereign Females", wf)
            self.assertEqual(subdir, pathlib.Path("Female", "1_Alpha", "4_Outfits"))
            wf["nodes"][0]["widgets_values"][0] = (
                "drakn-sisters/Drakness/1_Alpha/4_Outfits/Drakness_Qwen_Alpha_4_Outfits_Source_APose"
            )
            with mock.patch.object(cw, "load_cfg", return_value=cfg):
                subdir = cw.workspace_subdir("Drakness", wf)
            self.assertEqual(subdir, pathlib.Path("1_Alpha", "4_Outfits"))

    def test_0_edit_card_routes_to_studio_edit_workflow_and_photo_input(self):
        lay = cw.art_layout
        card = {
            "stage": "edit",
            "artId": "female-edit-cleanup-basic",
            "components": {"edit_task": "data/art/edits/cleanup/basic.json"},
        }
        family = lay.family(card, "angel-primes", cw.ROOT)
        dirs = lay.dirs_for(lay.stage_folder("edit"), family)
        self.assertEqual(family, ["cleanup"])
        self.assertEqual(dirs, ["0_Edit", "cleanup"])
        self.assertEqual(lay.parse_dirs(dirs), ("edit", ["cleanup"]))
        self.assertEqual(cw.stage_of("Female_Qwen_Edit_Cleanup_Basic.json"), "edit")
        self.assertEqual(cw.class_of("edit"), "studio")
        self.assertEqual(cw.input_role(
            {"inputs": {"Female": {}}, "inputRoles": {"edit": "photo"}},
            "Female", "edit", family), "photo")

    def test_footwear_auditions_use_prime_without_changing_legacy_footwear(self):
        cfg = cw.load_cfg()
        indexed = {item["name"]: item for item in cw.prompt_index(cfg)}
        plan = cw.denoise_plan(cfg)
        for variant in ("Barefoot", "Heels"):
            name = f"Female_Qwen_Alpha_3_{variant}_Prime_Audition"
            item = indexed[name]
            with self.subTest(workflow=name):
                card_path = cw.ROOT / "data/art/_sets/sovereign-females/female/1_Alpha/3_Footwear" / f"female-alpha-{variant.lower()}-prime-input-audition.json"
                card = json.loads(card_path.read_text(encoding="utf-8"))
                self.assertEqual(cw.art_layout.family(card, "sovereign-females"), ["footwear"])
                self.assertEqual(item["family"], ["footwear"])
                self.assertEqual(cw.default_input(cfg, item["hero"], item["stage"], item["family"], name),
                                 cfg["inputs"]["Female"]["prime"])
                self.assertEqual(plan[name][3:], ("prime", 0.7))
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"]), "bare")
                firered = name.replace("_Qwen_", "_FireRed_")
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"], firered), "prime")

    def test_layer_preservation_workflows_use_prime_without_changing_legacy_layers(self):
        cfg = cw.load_cfg()
        indexed = {item["name"]: item for item in cw.prompt_index(cfg)}
        plan = cw.denoise_plan(cfg)
        for outfit in ("OnePiece", "TwoPiece"):
            name = f"Female_Qwen_Layer_{outfit}_Preserve_Audition"
            item = indexed[name]
            with self.subTest(workflow=name):
                self.assertEqual(cw.stage_of(name + ".json"), "poses")
                self.assertEqual(cw.default_input(cfg, item["hero"], item["stage"], item["family"], name),
                                 cfg["inputs"]["Female"]["prime"])
                self.assertEqual(plan[name][3:], ("prime", 0.7))
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"]), "bare")
                firered = name.replace("_Qwen_", "_FireRed_")
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"], firered), "prime")
        broken = copy.deepcopy(cfg)
        broken["inputs"]["Female"].pop("prime")
        with self.assertRaisesRegex(ValueError, "no prime input is configured"):
            cw.default_input(broken, "Female", item["stage"], item["family"], name)
        for invalid_role in ("unknown", "heels"):
            with self.subTest(invalid_role=invalid_role):
                broken = copy.deepcopy(cfg)
                broken["inputRoleOverrides"][name] = invalid_role
                with self.assertRaisesRegex(ValueError, "inputRoleOverrides"):
                    cw.validate_config(broken)

    def test_layer_preservation_new_workflow_preview_uses_prime(self):
        cfg = cw.load_cfg()
        with tempfile.TemporaryDirectory(dir=cw.ROOT / "tmp") as tmp:
            output = io.StringIO()
            with mock.patch.object(cw, "engine_roots", return_value={"qwen": pathlib.Path(tmp)}), \
                    contextlib.redirect_stdout(output):
                cw.main(["make", "--hero", "Female", "--create", "--dry-run",
                         "--match", r"^Female_Layer_(OnePiece|TwoPiece)_Preserve_Audition$"])
            self.assertEqual(output.getvalue().count(f"(input: {cfg['inputs']['Female']['prime']})"), 2)

    def test_hair_preservation_workflows_use_prime_instead_of_legacy_bare(self):
        cfg = cw.load_cfg()
        indexed = {item["name"]: item for item in cw.prompt_index(cfg)}
        plan = cw.denoise_plan(cfg)
        for variant in ("Updo_HighBun", "Down_BeachWaves"):
            name = f"Female_Qwen_Hair_{variant}_Preserve_Audition"
            item = indexed[name]
            with self.subTest(workflow=name):
                self.assertEqual(cw.default_input(cfg, item["hero"], item["stage"], item["family"], name),
                                 cfg["inputs"]["Female"]["prime"])
                self.assertEqual(plan[name][3:], ("prime", 0.6))
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"]), "bare")
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"],
                                               name.replace("_Qwen_", "_FireRed_")), "prime")

    def test_wardrobe_replacement_workflows_use_photo_instead_of_legacy_bare(self):
        cfg = cw.load_cfg()
        indexed = {item["name"]: item for item in cw.prompt_index(cfg)}
        plan = cw.denoise_plan(cfg)
        for variant in ("Armor_HalfPlate", "Clothing_LongEveningGown"):
            name = f"Female_Qwen_{variant}_Replace_Audition"
            item = indexed[name]
            with self.subTest(workflow=name):
                self.assertEqual(cw.default_input(cfg, item["hero"], item["stage"], item["family"], name),
                                 cfg["photos"]["Female"])
                self.assertEqual(plan[name][3:], ("photo", 0.7))
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"]), "bare")
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"],
                                               name.replace("_Qwen_", "_FireRed_")), "photo")

    def test_scene_replacement_workflows_use_photo_instead_of_legacy_bare(self):
        cfg = cw.load_cfg()
        indexed = {item["name"]: item for item in cw.prompt_index(cfg)}
        plan = cw.denoise_plan(cfg)
        for variant in ("Glamour", "Signature"):
            name = f"Female_Qwen_Scene_{variant}_Replace_Audition"
            item = indexed[name]
            with self.subTest(workflow=name):
                self.assertEqual(cw.default_input(cfg, item["hero"], item["stage"], item["family"], name),
                                 cfg["photos"]["Female"])
                self.assertEqual(plan[name][3:], ("photo", 0.7))
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"]), "bare")
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"],
                                               name.replace("_Qwen_", "_FireRed_")), "photo")

    def test_motion_preservation_workflows_use_prime_instead_of_legacy_apose(self):
        cfg = cw.load_cfg()
        indexed = {item["name"]: item for item in cw.prompt_index(cfg)}
        plan = cw.denoise_plan(cfg)
        for variant in ("Walking_CatwalkConfident", "Standing_HandOnHipPower", "Dynamic_TwirlSpin"):
            name = f"Female_Qwen_Motion_{variant}_Preserve_Audition"
            item = indexed[name]
            with self.subTest(workflow=name):
                self.assertEqual(cw.default_input(cfg, item["hero"], item["stage"], item["family"], name),
                                 cfg["inputs"]["Female"]["prime"])
                self.assertEqual(plan[name][3:], ("prime", 0.6))
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"]), "apose")
                self.assertEqual(cw.input_role(cfg, item["hero"], item["stage"], item["family"],
                                               name.replace("_Qwen_", "_FireRed_")), "prime")

    def test_only_the_first_shots_take_the_photo(self):
        def item(stem, family=()):
            return {"stage": "alpha", "family": list(family), "stem": stem}
        for stem, fam in (("Alice_Alpha_1_Prime", ()), ("Alice_Alpha_1_Prime_Audition", ()),
                          ("Alice_Alpha_2_BareBase", ("base", "bare-base")), ("Alice_Alpha_2_NeutralBase", ("base", "neutral-base")),
                          ("Alice_Alpha_1b_BareBase", ("base", "bare-base")), ("Alice_Alpha_1b_NeutralBase", ("base", "neutral-base"))):
            self.assertTrue(cw.takes_photo(item(stem, fam)), stem)
        self.assertFalse(cw.takes_photo(item("Alice_Alpha_2_Bare", ("bare",))))
        self.assertFalse(cw.takes_photo(item("Alice_Alpha_2b_CelestialSuit", ("bare", "celestial"))))
        self.assertFalse(cw.takes_photo({"stage": "poses", "family": [], "stem": "Alice_X_Pose"}))

    def test_an_alternate_flow_gives_the_experiment_bases_own_variants(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        for sub, stem in (("1_Prime", "Alice_Alpha_1_Prime"), ("2_Bare/bare-base", "Alice_Alpha_2_BareBase"), ("2_Bare/neutral-base", "Alice_Alpha_2_NeutralBase")):
            d = tmp / "set-a" / "Alice" / "1_Alpha" / sub
            d.mkdir(parents=True)
            (d / f"{stem}.txt").write_text("=== x ===\n\nprompt:\n\nhello\n\n----------\nnegative prompt:\n\nbad\n")
        cfg = {"photos": {"Alice": "a.png"}, "flows": {"alternate": {"photos": {"Alice": "a_alt.png"}}}}
        with mock.patch.object(cw, "PROMPTS", tmp):
            names = {i["name"]: i for i in cw.prompt_index(cfg)}
        self.assertEqual(sorted(names), ["Alice_Qwen_Alpha_1_Prime", "Alice_Qwen_Alpha_1_Prime_Alternate", "Alice_Qwen_Alpha_2_BareBase", "Alice_Qwen_Alpha_2_BareBase_Alternate",
                                         "Alice_Qwen_Alpha_2_NeutralBase", "Alice_Qwen_Alpha_2_NeutralBase_Alternate"])
        self.assertIn("1_Alpha/2_Bare/bare-base/", names["Alice_Qwen_Alpha_2_BareBase_Alternate"]["prefix"], "output folders keep P2 and P3 apart")
        self.assertIn("1_Alpha/2_Bare/neutral-base/", names["Alice_Qwen_Alpha_2_NeutralBase"]["prefix"])
        self.assertEqual(names["Alice_Qwen_Alpha_2_BareBase"]["family"], ["base", "bare-base"])
        self.assertTrue(cw.takes_photo(names["Alice_Qwen_Alpha_2_BareBase"]))
        self.assertEqual(cw.input_role({"inputs": {"Alice": {}}, "inputRoles": {"alpha/base": "photo", "default": "bare"}}, "Alice", "alpha", ["base", "bare-base"]), "photo")


class SeedTests(unittest.TestCase):
    """A generated workflow draws a new seed each run; only finals fix one."""

    @staticmethod
    def wf(control):
        return {"nodes": [], "definitions": {"subgraphs": [{"nodes": [
            {"type": "KSampler", "widgets_values": [43, control, 8, 1, "euler", "simple", 1], "widgets_values_named": {"seed": 43, "control_after_generate": control}},
            {"type": "RandomNoise", "widgets_values": [1, control], "widgets_values_named": {"noise_seed": 1, "control_after_generate": control}},
            {"type": "CLIPTextEncode", "widgets_values": ["fixed", "fixed"]}]}]}}

    def test_fixed_controls_become_randomize_and_a_random_one_is_left_alone(self):
        wf = self.wf("fixed")
        self.assertTrue(cw.randomize_seed(wf))
        nodes = wf["definitions"]["subgraphs"][0]["nodes"]
        self.assertEqual([nodes[0]["widgets_values"][1], nodes[1]["widgets_values"][1]], ["randomize", "randomize"])
        self.assertEqual((nodes[0]["widgets_values_named"]["control_after_generate"], nodes[0]["widgets_values"][0]), ("randomize", 43), "the seed value is kept")
        self.assertEqual(nodes[2]["widgets_values"], ["fixed", "fixed"], "other nodes are not touched")
        self.assertFalse(cw.randomize_seed(wf))

    def test_every_template_draws_a_new_seed(self):
        for p in sorted(cw.ROOT.glob("workflows/_templates/ST*.json")):
            self.assertFalse(cw.randomize_seed(cw.read_wf(p)), f"{p.name} has a fixed seed control")


class RoutingTests(unittest.TestCase):
    def test_generic_homes_are_separate_from_angel_characters(self):
        cfg = cw.load_cfg()
        for stage in ("edit", "alpha", "scene"):
            with self.subTest(stage=stage):
                self.assertEqual(cw.home_workspaces(cfg, "angel-primes", "Female", stage),
                                 [])
                self.assertEqual(cw.home_workspaces(cfg, "sovereign-females", "Female", stage),
                                 ["Sovereign Females"])
                self.assertEqual(cw.home_workspaces(cfg, "angel-primes", "Angelica", stage),
                                 ["Angel Primes"])
                self.assertEqual(cw.home_workspaces(cfg, "angel-primes", "Male", stage),
                                 [])
                self.assertEqual(cw.home_workspaces(cfg, "sovereign-males", "Male", stage),
                                 ["Sovereign Males"])

    def test_home_and_accepts(self):
        with World() as w:
            self.assertTrue(cw.is_home(w.cfg, "A-Home", "set-a", "Alice"))
            self.assertFalse(cw.is_home(w.cfg, "Brand", "set-a", "Alice"), "accepting a set is not being its home")
            self.assertTrue(cw.holds(w.cfg, "Brand", "set-a", "Alice"), "Brand accepts any set")
            self.assertTrue(cw.holds(w.cfg, "Series", "set-a", "Alice"))
            self.assertFalse(cw.holds(w.cfg, "Series", "set-b", "Bob"), "Series accepts only set-a")
            self.assertFalse(cw.holds(w.cfg, "Guest", "set-a", "Alice"), "nothing is held by default")
            self.assertFalse(cw.holds(w.cfg, "Alice-Own", "set-a", "Bob"))

    def test_default_deploy_goes_to_every_home_only(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            w.run("deploy", "--hero", "Alice")
            self.assertEqual(w.names("A-Home"), ["Alice_Qwen_Scene_One.json"])
            self.assertEqual(w.names("Alice-Own"), ["Alice_Qwen_Scene_One.json"])
            for other in ("Series", "Brand", "Guest"):
                self.assertEqual(w.names(other), [], other)

    def test_explicit_workspace_that_accepts_the_set(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            w.run("deploy", "--hero", "Alice", "-w", "Series")
            self.assertEqual(w.names("Series"), ["Alice_Qwen_Scene_One.json"])
            self.assertEqual(w.names("A-Home"), [], "an explicit target gets the copy and nothing else does")

    def test_workspace_that_accepts_any_set(self):
        with World() as w:
            w.master("Bob_Qwen_Scene_One.json")
            w.run("deploy", "--hero", "Bob", "-w", "Brand")
            self.assertEqual(w.names("Brand"), ["Bob_Qwen_Scene_One.json"])

    def test_a_workspace_that_neither_homes_nor_accepts_is_refused(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            _out, code = w.run("deploy", "--hero", "Alice", "-w", "Guest")
            self.assertIn("neither home for nor accepts: set-a", str(code))
            self.assertEqual(w.names("Guest"), [])
            w.master("Bob_Qwen_Scene_One.json")
            _out, code = w.run("deploy", "--hero", "Bob", "-w", "Series")
            self.assertIn("neither home for nor accepts: set-b", str(code))
            self.assertEqual(w.names("Series"), [])

    def test_a_filterless_deploy_to_one_workspace_is_refused_when_some_set_is_not_welcome(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            w.master("Bob_Qwen_Scene_One.json")
            _out, code = w.run("deploy", "--all", "-w", "Series")
            self.assertIn("neither home for nor accepts", str(code))
            self.assertEqual(w.names("Series"), [])

    def test_a_set_without_a_home_stops_the_command(self):
        with World() as w:
            w.master("Cleo_Qwen_Scene_One.json")
            _out, code = w.run("deploy", "--group", "set-orphan")
            self.assertIn("No workspace is home for: set-orphan", str(code))
            for ws in w.cfg["workspaces"]:
                if ws != "Ghost":
                    self.assertEqual(w.names(ws), [], f"{ws} must stay empty")

    def test_deploy_all_fails_loudly_when_any_set_has_no_home(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            w.master("Cleo_Qwen_Scene_One.json")
            _out, code = w.run("deploy", "--all")
            self.assertIn("set-orphan", str(code))
            self.assertEqual(w.names("A-Home"), [])

    def test_the_old_tier_flag_is_gone(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                cw.main(["deploy", "--hero", "Alice", "--to", "prod"])
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                cw.main(["promote", "--to", "prod", "--hero", "Alice"])

    def test_planned_workspace_is_skipped(self):
        with World() as w:
            w.master("Dana_Qwen_Scene_One.json")
            out, _ = w.run("deploy", "--hero", "Dana")
            self.assertIn("status is 'planned', not active", out)
            self.assertEqual(w.names("Planned"), [])

    def test_missing_install_is_skipped(self):
        with World() as w:
            w.master("Eve_Qwen_Scene_One.json")
            out, _ = w.run("deploy", "--hero", "Eve")
            self.assertIn("workspace not created yet", out)
            self.assertFalse(w.dir("Ghost").exists())

    def test_workspace_ready(self):
        with World() as w:
            self.assertEqual(cw.workspace_ready(w.cfg, "A-Home"), (True, ""))
            self.assertFalse(cw.workspace_ready(w.cfg, "Planned")[0])
            self.assertFalse(cw.workspace_ready(w.cfg, "Ghost")[0])
            self.assertFalse(cw.workspace_ready(w.cfg, "Nope")[0])

    def test_templates_go_to_the_templates_workspace(self):
        with World() as w:
            tpl = w.repo / "_templates"
            cw.write_wf(tpl / "ST1_Test.json", MASTER)
            with mock.patch.object(cw, "template_files", lambda cfg: {"ST1_Test.json": tpl / "ST1_Test.json"}):
                w.run("deploy", "--templates")
            self.assertEqual(w.names("Brand"), ["ST1_Test.json"])
            self.assertEqual(w.names("A-Home"), [])


class HandMadeGuardTests(unittest.TestCase):
    def test_reference_jobs_do_not_shadow_or_get_patched_by_deployment(self):
        with World() as w:
            w.cfg["referenceWorkspace"] = "A-Home"
            w.master("Alice_Qwen_Scene_One.json")
            hand = {"nodes": [], "id": "reference job"}
            reference = w.put("A-Home", "Reference/job/Alice_Qwen_Scene_One.json", hand)
            self.assertNotIn(reference.name, cw.install_files(w.cfg, "A-Home"))
            _out, code = w.run("deploy", "--hero", "Alice", "-w", "A-Home")
            self.assertIsNone(code)
            self.assertEqual(json.loads(reference.read_text()), hand)
            self.assertTrue((w.dir("A-Home") / reference.name).is_file())

    def test_is_hand_made(self):
        with World() as w:
            d = w.dir("A-Home")
            self.assertTrue(cw.is_hand_made(w.cfg, "A-Home", d / "zz_Curated" / "Alice" / "x.json"))
            self.assertTrue(cw.is_hand_made(w.cfg, "A-Home", d / "zz_Shots" / "x.json"))
            self.assertTrue(cw.is_hand_made(w.cfg, "A-Home", d / "zz_Test" / "x.json"))
            self.assertTrue(cw.is_hand_made(w.cfg, "A-Home", d / "armor" / "zz_Curated_Alice_x.json"))
            self.assertTrue(cw.is_hand_made(w.cfg, "A-Home", d / "armor" / "test_Alice_x.json"))
            self.assertFalse(cw.is_hand_made(w.cfg, "A-Home", d / "armor" / "Alice_Qwen_Armor_x.json"))

    def test_deploy_never_changes_a_hand_made_copy_even_with_overwrite(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            hand = {"nodes": [], "id": "mine"}
            path = w.put("A-Home", "zz_Curated/Alice/Alice_Qwen_Scene_One.json", hand)
            out, _ = w.run("deploy", "--hero", "Alice", "--mode", "overwrite")
            self.assertEqual(json.loads(path.read_text()), hand)
            self.assertIn("hand-made", out)
            self.assertEqual(w.names("A-Home"), ["Alice_Qwen_Scene_One.json"], "no second copy is created beside it")

    def test_workspace_deploy_backups_are_incremental_and_separate(self):
        with World() as w:
            name = "Alice_Qwen_Scene_One.json"
            w.master(name)
            originals = {}
            for ws in ("A-Home", "Alice-Own"):
                path = w.put(ws, "scene/" + name, {"nodes": [], "id": ws})
                originals[ws] = path.read_bytes()
            out, code = w.run("deploy", "--hero", "Alice", "--mode", "overwrite",
                              "--workspace-backups", "--preview")
            self.assertIsNone(code)
            self.assertIn("workspace backups", out)
            for ws in originals:
                root = w.tmp / "installs" / ws / ".sovereign" / "workflow-backups"
                self.assertFalse(root.exists())
            _out, code = w.run("deploy", "--hero", "Alice", "--mode", "overwrite",
                               "--workspace-backups")
            self.assertIsNone(code)
            for ws, before in originals.items():
                root = w.tmp / "installs" / ws / ".sovereign" / "workflow-backups"
                saved = list(root.rglob(name))
                self.assertEqual(len(saved), 1)
                self.assertEqual(saved[0].read_bytes(), before)
                receipt = json.loads(next(root.rglob("storage-configuration-receipt.json")).read_text())
                self.assertEqual(receipt["backups"][0]["backupPath"], str(saved[0].resolve()))
                out, code = w.run("backup-check", ws, next(root.iterdir()).name)
                self.assertIsNone(code)
                self.assertIn("verified 1 workspace backup", out)
            self.assertFalse((w.tmp / "production").exists())
            w.run("deploy", "--hero", "Alice", "--mode", "overwrite", "--workspace-backups")
            for ws in originals:
                root = w.tmp / "installs" / ws / ".sovereign" / "workflow-backups"
                self.assertEqual(len(list(root.rglob(name))), 1)
            root = w.tmp / "installs" / "A-Home" / ".sovereign" / "workflow-backups"
            saved = next(root.rglob(name))
            receipt_path = next(root.rglob("storage-configuration-receipt.json"))
            receipt = json.loads(receipt_path.read_text())
            original_receipt = receipt_path.read_bytes()
            receipt["backups"][0]["source"] = str(w.tmp / "wrong-source.json")
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            run = next(root.iterdir()).name
            with self.assertRaisesRegex(ValueError, "source does not match"):
                w.run("backup-check", "A-Home", run)
            receipt_path.write_bytes(original_receipt)
            saved.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                w.run("backup-check", "A-Home", run)

    def test_workspace_backup_receipt_failure_leaves_workflow_untouched(self):
        with World() as w:
            name = "Alice_Qwen_Scene_One.json"
            w.master(name)
            target = w.put("A-Home", "scene/" + name, {"nodes": [], "id": "original"})
            before = target.read_bytes()
            with mock.patch.object(cw, "record_backup_receipt", side_effect=OSError("receipt failed")):
                with self.assertRaisesRegex(OSError, "receipt failed"):
                    w.run("deploy", "--hero", "Alice", "-w", "A-Home",
                          "--mode", "overwrite", "--workspace-backups")
            self.assertEqual(target.read_bytes(), before)

    def test_workspace_backup_copy_failure_leaves_workflow_untouched(self):
        with World() as w:
            name = "Alice_Qwen_Scene_One.json"
            w.master(name)
            target = w.put("A-Home", "scene/" + name, {"nodes": [], "id": "original"})
            before = target.read_bytes()
            with mock.patch.object(cw.shutil, "copyfileobj", side_effect=OSError("copy failed")):
                with self.assertRaisesRegex(OSError, "copy failed"):
                    w.run("deploy", "--hero", "Alice", "-w", "A-Home",
                          "--mode", "overwrite", "--workspace-backups")
            self.assertEqual(target.read_bytes(), before)
            root = w.tmp / "installs" / "A-Home" / ".sovereign" / "workflow-backups"
            self.assertEqual(list(root.rglob(name)), [])

    def test_workspace_backup_refuses_collisions_and_reparse_points(self):
        with World() as w:
            target = w.put("A-Home", "scene/Alice_Qwen_Scene_One.json")
            root = cw.workspace_backup_root(w.cfg, "A-Home")
            cw.workspace_backup(w.cfg, "same-run", root, w.dir("A-Home"), target)
            saved = next(root.rglob(target.name))
            before = saved.read_bytes()
            target.write_text('{"nodes": [], "id": "changed"}', encoding="utf-8")
            with self.assertRaises(FileExistsError):
                cw.workspace_backup(w.cfg, "same-run", root, w.dir("A-Home"), target)
            self.assertEqual(saved.read_bytes(), before)
            actual_reparse = cw.is_reparse_point
            with mock.patch.object(cw, "is_reparse_point",
                                   side_effect=lambda path: path == root or actual_reparse(path)):
                with self.assertRaisesRegex(ValueError, "reparse point"):
                    cw.workspace_backup_root(w.cfg, "A-Home")

    def test_tidy_keeps_generated_name_inside_zz_folder_and_prunes_empty_folders(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            hand = w.put("A-Home", "zz_Curated/Alice/Alice_Qwen_Scene_One.json")
            (w.dir("A-Home") / "old" / "layout").mkdir(parents=True)
            (w.dir("A-Home") / "zz_Test" / "empty").mkdir(parents=True)
            keep = w.dir("A-Home") / "notes"
            keep.mkdir()
            (keep / "readme.txt").write_text("not a workflow")
            out, _ = w.run("tidy", "-w", "A-Home")
            self.assertIn("would remove empty folder", out)
            self.assertTrue((w.dir("A-Home") / "old").exists(), "preview removes nothing")
            w.run("tidy", "-w", "A-Home", "--apply")
            self.assertTrue(hand.exists())
            self.assertFalse((w.dir("A-Home") / "old").exists())
            self.assertTrue((w.dir("A-Home") / "zz_Test" / "empty").exists(), "zz_ folders are never pruned")
            self.assertTrue((keep / "readme.txt").exists(), "a folder with any file stays")

    def test_tidy_refuses_to_overwrite_a_duplicate_destination(self):
        for folder in ("0_old", "z_old"):
            with self.subTest(folder=folder), World() as w:
                name = "Alice_Qwen_Motion_Standing_One.json"
                prefix = "set-a/Alice/2_Studies/motions/standing/Alice_Qwen_Motion_Standing_One"
                graph = {"nodes": [{"type": "SaveImage", "widgets_values": [prefix]}]}
                w.master(name, graph)
                source = w.put("A-Home", f"{folder}/{name}", graph)
                destination = w.put("A-Home", f"Alice/2_Studies/motions/standing/{name}", {"nodes": [], "id": "keep"})
                source_bytes, destination_bytes = source.read_bytes(), destination.read_bytes()
                with self.assertRaisesRegex(ValueError, "refusing to move"):
                    w.run("tidy", "-w", "A-Home", "--apply")
                self.assertEqual(source.read_bytes(), source_bytes)
                self.assertEqual(destination.read_bytes(), destination_bytes)

    def test_tidy_motion_filter_leaves_other_workflows_and_empty_folders(self):
        with World() as w:
            motion = "Alice_Qwen_Motion_Standing_One.json"
            scene = "Alice_Qwen_Scene_One.json"
            motion_graph = {"nodes": [{"type": "SaveImage", "widgets_values": [
                "set-a/Alice/2_Studies/motions/standing/Alice_Qwen_Motion_Standing_One"]}]}
            scene_graph = {"nodes": [{"type": "SaveImage", "widgets_values": [
                "set-a/Alice/5_Scenes/Alice_Qwen_Scene_One"]}]}
            w.master(motion, motion_graph)
            w.master(scene, scene_graph)
            other_motion = "Bob_Qwen_Motion_Standing_One.json"
            w.master(other_motion, {"nodes": [{"type": "SaveImage", "widgets_values": [
                "set-b/Bob/2_Studies/motions/standing/Bob_Qwen_Motion_Standing_One"]}]})
            old_motion = w.put("A-Home", f"Alice/Bench/motion/standing/{motion}", motion_graph)
            old_scene = w.put("A-Home", f"old/{scene}", scene_graph)
            other = w.put("A-Home", f"Bob/Bench/motion/standing/{other_motion}")
            empty = w.dir("A-Home") / "unrelated-empty"
            empty.mkdir()
            w.run("tidy", "-w", "A-Home", "--stage", "motion", "--group", "set-a", "--apply")
            self.assertFalse(old_motion.exists())
            self.assertTrue((w.dir("A-Home") / "Alice/2_Studies/motions/standing" / motion).exists())
            self.assertTrue(old_scene.exists())
            self.assertTrue(other.exists())
            self.assertTrue(empty.is_dir())

    def test_orphan_cleanup_skips_hand_made_and_prunes(self):
        with World() as w:
            w.put("A-Home", "scene/gone/Alice_Qwen_Scene_Old.json")
            hand = w.put("A-Home", "zz_Curated/Alice/Alice_Qwen_Scene_Mine.json")
            w.run("cleanup", "--orphans", "--match", "Alice_Qwen_Scene_", "-w", "A-Home", "--apply")
            self.assertTrue(hand.exists())
            self.assertFalse((w.dir("A-Home") / "scene").exists(), "the emptied folders are pruned")
            moved = list(cw.storage_root(w.cfg, "backup").rglob("Alice_Qwen_Scene_Old.json"))
            self.assertEqual(len(moved), 1)


class SavedShotTests(unittest.TestCase):
    """A workflow ComfyUI saved from a render (Hero_Qwen_..._00004_) keeps the seed of that render. Left loose in the list it is a candidate (not a shot, not install-only);
    `pull` keeps it in workflows/_candidates and `finals sort` files it into zz_Candidates."""

    def test_numbered_save_is_a_candidate_not_an_install_only_workflow(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            w.master("Alice_Qwen_Alpha_1_Prime.json")
            w.put("A-Home", "scene/Alice_Qwen_Scene_One.json")
            w.put("A-Home", "Alice_Qwen_Alpha_1_Prime_00004_.json")
            self.assertNotIn("Alice_Qwen_Alpha_1_Prime_00004_.json", cw.install_files(w.cfg, "A-Home"))
            self.assertIn("Alice_Qwen_Scene_One.json", cw.install_files(w.cfg, "A-Home"))
            self.assertEqual(list(cw.workspace_shots(w.cfg, "A-Home")), [])
            entries = cw.finals_entries(w.cfg, "A-Home")
            self.assertEqual([(e["kind"], e["loose"]) for e in entries], [("candidate", True)])
            out, _ = w.run("status", "-w", "A-Home")
            self.assertIn("0 install-only", out)

    def test_pull_keeps_the_save_in_the_repo_as_a_candidate_and_leaves_the_workspace_copy(self):
        with World() as w, mock.patch.object(cw, "CANDIDATES", w.repo / "_candidates"), mock.patch.object(cw, "FINALS", w.repo / "_final"), mock.patch.object(cw, "ROOT", w.tmp):
            w.master("Alice_Qwen_Alpha_1_Prime.json")
            save = w.put("A-Home", "Alice_Qwen_Alpha_1_Prime_00004_.json", {"nodes": [], "id": "seed-4"})
            w.run("pull", "-w", "A-Home")
            kept = w.repo / "_candidates" / "set-a" / "Alice" / "Alice_Qwen_Alpha_1_Prime_00004_.json"
            self.assertEqual(json.loads(kept.read_text())["id"], "seed-4")
            self.assertTrue(save.exists())

    def test_two_workspaces_with_different_shots_of_one_name_do_not_overwrite_each_other(self):
        with World() as w, mock.patch.object(cw, "SHOTS", w.repo / "_shots"), mock.patch.object(cw, "ROOT", w.tmp):
            w.put("A-Home", "zz_Shots/Alice_Qwen_Alpha_2_Bare_Skin.json", {"nodes": [], "id": "seed-1"})
            w.put("Alice-Own", "zz_Shots/Alice_Qwen_Alpha_2_Bare_Skin.json", {"nodes": [], "id": "seed-2"})
            out, _ = w.run("pull", "--only", "shots", "--hero", "Alice")
            kept = w.repo / "_shots" / "set-a" / "Alice" / "Alice_Qwen_Alpha_2_Bare_Skin.json"
            self.assertEqual(json.loads(kept.read_text())["id"], "seed-1", "the first pulled copy stays")
            self.assertIn("CONFLICT", out)

    def test_a_generated_workflow_is_never_a_save(self):
        self.assertFalse(cw.is_capture("scene/Alice_Qwen_Scene_One.json", "Alice_Qwen_Scene_One.json"))
        self.assertFalse(cw.is_capture("zz_Shots/Alice_Qwen_Scene_One_00001_.json", "Alice_Qwen_Scene_One_00001_.json"))
        self.assertTrue(cw.is_capture("Alice_Qwen_Scene_One_00001_.json", "Alice_Qwen_Scene_One_00001_.json"))


class CleanupTests(unittest.TestCase):
    def test_retire_planned_home_backs_up_scoped_generated_files(self):
        with World() as w:
            name = "Dana_Qwen_Scene_One.json"
            w.master(name)
            source = w.put("Guest", f"alpha/Dana/{name}", {"nodes": [], "id": "edited"})
            manual = w.put("Guest", f"zz_Shots/{name}")
            before = source.read_bytes()
            flags = ("--group", "set-planned", "--hero", "Dana", "--workspace-backups",
                     "--retire-planned-home")
            normal, _ = w.run("cleanup", "-w", "Guest", "--group", "set-planned",
                              "--hero", "Dana", "--workspace-backups", "--dry-run")
            self.assertIn("not an active workspace", normal)
            preview, _ = w.run("cleanup", "-w", "Guest", *flags, "--dry-run")
            self.assertIn("planned homes: Planned", preview)
            self.assertTrue(source.exists())
            self.assertFalse(cw.workspace_backup_root(w.cfg, "Guest").exists())
            w.run("cleanup", "-w", "Guest", *flags, "--apply")
            self.assertFalse(source.exists())
            self.assertTrue(manual.exists())
            run = next(cw.workspace_backup_root(w.cfg, "Guest").iterdir())
            self.assertEqual((run / "alpha" / "Dana" / name).read_bytes(), before)
            checked, code = w.run("backup-check", "Guest", run.name)
            self.assertIsNone(code)
            self.assertIn("verified 1 workspace backup", checked)

    def test_retire_planned_home_refuses_missing_scope_and_active_homes(self):
        with World() as w:
            name = "Eve_Qwen_Scene_One.json"
            w.master(name)
            source = w.put("Guest", name)
            _, code = w.run("cleanup", "-w", "Guest", "--retire-planned-home",
                            "--workspace-backups", "--apply")
            self.assertIn("requires --workspace-backups, --group and --hero", code)
            out, _ = w.run("cleanup", "-w", "Guest", "--group", "set-ghost",
                           "--hero", "Eve", "--workspace-backups",
                           "--retire-planned-home", "--apply")
            self.assertIn("not all destination homes are planned", out)
            self.assertTrue(source.exists())

    def test_retire_planned_home_keeps_source_when_backup_fails(self):
        with World() as w:
            name = "Dana_Qwen_Scene_One.json"
            w.master(name)
            source = w.put("Guest", name)
            with mock.patch.object(cw, "workspace_backup", side_effect=OSError("backup failed")):
                with self.assertRaisesRegex(OSError, "backup failed"):
                    w.run("cleanup", "-w", "Guest", "--group", "set-planned",
                          "--hero", "Dana", "--workspace-backups",
                          "--retire-planned-home", "--apply")
            self.assertTrue(source.is_file())

    def test_scoped_prefix_migration_uses_verified_workspace_backups(self):
        with World() as w:
            w.cfg["homes"] = [{"groups": ["set-a"], "workspace": "A-Home"}]
            old = {"nodes": [
                {"type": "SaveImage", "widgets_values": ["angel-primes/alpha/Female/test"],
                 "widgets_values_named": {"filename_prefix": "angel-primes/alpha/Female/test"}},
                {"type": "LoadImage", "widgets_values": ["photo.png"]},
            ]}
            new = copy.deepcopy(old)
            new["nodes"][0]["widgets_values"][0] = "reference/manual/alpha/Female/test"
            different = copy.deepcopy(new)
            different["nodes"][1]["widgets_values"][0] = "other.png"
            for name in ("One", "Two"):
                w.master(f"Alice_Qwen_Scene_{name}.json", old)
                w.put("Guest", f"alpha/Female/Alice_Qwen_Scene_{name}.json", old)
            w.put("A-Home", "alpha/Female/Alice_Qwen_Scene_One.json", new)
            w.put("A-Home", "alpha/Female/Alice_Qwen_Scene_Two.json", different)
            flags = ("--group", "set-a", "--hero", "Alice", "--workspace-backups",
                     "--prefix-map", "angel-primes=reference/manual")
            before = (w.dir("Guest") / "alpha/Female/Alice_Qwen_Scene_One.json").read_bytes()
            preview, _ = w.run("cleanup", "-w", "Guest", *flags, "--dry-run")
            self.assertIn("would remove  Alice_Qwen_Scene_One.json", preview)
            self.assertIn("differs from the copy", preview)
            self.assertFalse(cw.workspace_backup_root(w.cfg, "Guest").exists())
            out, _ = w.run("cleanup", "-w", "Guest", *flags, "--apply")
            self.assertIn("moved to backup", out)
            self.assertFalse((w.dir("Guest") / "alpha/Female/Alice_Qwen_Scene_One.json").exists())
            self.assertTrue((w.dir("Guest") / "alpha/Female/Alice_Qwen_Scene_Two.json").exists())
            backup = cw.workspace_backup_root(w.cfg, "Guest")
            run = next(backup.iterdir())
            self.assertEqual((run / "alpha/Female/Alice_Qwen_Scene_One.json").read_bytes(), before)
            checked, code = w.run("backup-check", "Guest", run.name)
            self.assertIsNone(code)
            self.assertIn("verified 1 workspace backup", checked)
            self.assertFalse(cw.storage_root(w.cfg, "backup").exists())

    def test_workspace_backup_failure_preserves_cleanup_source(self):
        with World() as w:
            w.cfg["homes"] = [{"groups": ["set-a"], "workspace": "A-Home"}]
            w.master("Alice_Qwen_Scene_One.json")
            w.put("A-Home", "Alice_Qwen_Scene_One.json")
            source = w.put("Guest", "Alice_Qwen_Scene_One.json")
            with mock.patch.object(cw, "workspace_backup", side_effect=OSError("backup failed")):
                with self.assertRaisesRegex(OSError, "backup failed"):
                    w.run("cleanup", "-w", "Guest", "--workspace-backups", "--apply")
            self.assertTrue(source.is_file())

    def build(self, w):
        """Guest is home for nothing here; each case below is one reason to remove or keep."""
        for n in ("One", "Two", "Three", "Four", "Five"):
            w.master(f"Alice_Qwen_Scene_{n}.json")
        w.master("Bob_Qwen_Scene_One.json")
        w.master("Cleo_Qwen_Scene_One.json")
        for ws in ("A-Home", "Alice-Own"):
            w.put(ws, "scene/Alice_Qwen_Scene_One.json")
            w.put(ws, "scene/Alice_Qwen_Scene_Four.json")
        w.put("A-Home", "scene/Alice_Qwen_Scene_Two.json")
        w.put("Alice-Own", "scene/Alice_Qwen_Scene_Two.json")
        w.put("A-Home", "scene/Alice_Qwen_Scene_Five.json")  # missing from Alice-Own: only one of two homes holds it
        w.put("B-Home", "scene/Bob_Qwen_Scene_One.json")
        w.put("Guest", "old/layout/Alice_Qwen_Scene_One.json")                    # identical in both homes: removed
        w.put("Guest", "Alice_Qwen_Scene_Two.json", {"nodes": [], "id": "edited"})  # differs from the homes: kept
        w.put("Guest", "Alice_Qwen_Scene_Three.json")                             # delivered nowhere: kept
        w.put("Guest", "zz_Curated/Alice_Qwen_Scene_Four.json")                   # hand-made: kept
        w.put("Guest", "Alice_Qwen_Scene_Five.json")                              # one home lacks it: kept
        w.put("Guest", "Bob/Bob_Qwen_Scene_One.json")                             # removed
        w.put("Guest", "Cleo_Qwen_Scene_One.json")                                # no home at all: kept
        w.put("Guest", "ST1_Template.json")                                       # not a hero workflow: untouched
        (w.dir("Guest") / "zz_Curated" / "empty").mkdir()
        (w.dir("Guest") / "Bob" / "later").mkdir()
        (w.dir("Guest") / "notes").mkdir()
        (w.dir("Guest") / "notes" / "readme.txt").write_text("keep me")

    def test_preview_changes_nothing(self):
        with World() as w:
            self.build(w)
            before = (w.names("Guest"), w.folders("Guest"))
            out, _ = w.run("cleanup", "-w", "Guest")
            self.assertIn("would remove  Alice_Qwen_Scene_One.json", out)
            self.assertIn("would remove  Bob_Qwen_Scene_One.json", out)
            self.assertIn("preview; use --apply", out)
            self.assertEqual((w.names("Guest"), w.folders("Guest")), before)
            self.assertFalse(cw.storage_root(w.cfg, "backup").exists())

    def test_apply_removes_only_what_is_safe(self):
        with World() as w:
            self.build(w)
            out, _ = w.run("cleanup", "-w", "Guest", "--apply")
            self.assertEqual(w.names("Guest"), sorted([
                "Alice_Qwen_Scene_Two.json", "Alice_Qwen_Scene_Three.json", "Alice_Qwen_Scene_Four.json",
                "Alice_Qwen_Scene_Five.json", "Cleo_Qwen_Scene_One.json", "ST1_Template.json"]))
            self.assertIn("differs from the copy in", out)
            self.assertIn("not delivered to", out)
            self.assertIn("hand-made", out)
            self.assertIn("no home workspace is configured for it", out)
            self.assertTrue((w.dir("Guest") / "zz_Curated" / "Alice_Qwen_Scene_Four.json").exists())
            backed = sorted(
                p.name
                for p in cw.storage_root(w.cfg, "backup").rglob("*.json")
                if p.name != "storage-configuration-receipt.json"
            )
            self.assertEqual(backed, ["Alice_Qwen_Scene_One.json", "Bob_Qwen_Scene_One.json"], "removed files are moved to backup, not deleted")
            receipt_paths = list(
                cw.storage_root(w.cfg, "backup").rglob("storage-configuration-receipt.json")
            )
            self.assertEqual(len(receipt_paths), 1)
            receipt = json.loads(receipt_paths[0].read_text(encoding="utf-8"))
            self.assertEqual(
                {pathlib.Path(item["source"]).name for item in receipt["backups"]},
                {"Alice_Qwen_Scene_One.json", "Bob_Qwen_Scene_One.json"},
            )
            self.assertTrue(
                all(pathlib.Path(item["backupPath"]).is_file() for item in receipt["backups"])
            )

    def test_apply_prunes_emptied_folders_but_not_zz_or_folders_with_files(self):
        with World() as w:
            self.build(w)
            w.run("cleanup", "-w", "Guest", "--apply")
            folders = w.folders("Guest")
            self.assertNotIn("old", folders)
            self.assertNotIn("old/layout", folders)
            self.assertNotIn("Bob", folders)
            self.assertIn("zz_Curated/empty", folders)
            self.assertIn("notes", folders)

    def test_a_home_workspace_is_left_alone(self):
        with World() as w:
            self.build(w)
            before = w.names("A-Home")
            out, _ = w.run("cleanup", "-w", "A-Home", "--apply")
            self.assertEqual(w.names("A-Home"), before)
            self.assertIn("home here and left alone", out)

    def test_a_temporary_publish_is_removed_when_you_are_done(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            w.run("deploy", "--hero", "Alice")
            w.run("deploy", "--hero", "Alice", "-w", "Brand")
            w.run("deploy", "--hero", "Alice", "-w", "Series")
            self.assertEqual(w.names("Brand"), ["Alice_Qwen_Scene_One.json"])
            out, _ = w.run("status", "-w", "Brand")
            self.assertIn("1 published", out)
            w.run("cleanup", "-w", "Series", "--apply")
            self.assertEqual(w.names("Series"), [])
            w.run("cleanup", "-w", "Brand", "--apply")
            self.assertEqual(w.names("Brand"), [])
            self.assertEqual(w.names("A-Home"), ["Alice_Qwen_Scene_One.json"], "the home copy is never touched")
            self.assertEqual(w.names("Alice-Own"), ["Alice_Qwen_Scene_One.json"])

    def test_a_publish_is_kept_when_the_home_copy_is_missing(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            w.put("Brand", "Alice_Qwen_Scene_One.json")
            out, _ = w.run("cleanup", "-w", "Brand", "--apply")
            self.assertEqual(w.names("Brand"), ["Alice_Qwen_Scene_One.json"])
            self.assertIn("not delivered to", out)

    def test_needs_a_workspace(self):
        with World() as w:
            _out, code = w.run("cleanup")
            self.assertIn("needs -w WORKSPACE", str(code))

    def test_refuses_a_planned_workspace(self):
        with World() as w:
            _out, code = w.run("cleanup", "-w", "Planned")
            self.assertIn("not active", str(code))

    def test_apply_with_dry_run_changes_nothing(self):
        with World() as w:
            self.build(w)
            before = w.names("Guest")
            w.run("cleanup", "-w", "Guest", "--apply", "--dry-run")
            self.assertEqual(w.names("Guest"), before)

    def test_status_reports_unrouted(self):
        with World() as w:
            self.build(w)
            out, _ = w.run("status", "-w", "Guest")
            self.assertRegex(out, r"\d+ unrouted")

    def test_status_compares_only_the_homes(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            out, _ = w.run("status", "-w", "Series")
            self.assertIn("0 missing", out)
            out, _ = w.run("status", "-w", "Brand")
            self.assertIn("0 missing", out)
            out, _ = w.run("status", "-w", "A-Home")
            self.assertIn("1 missing", out)


class SetupTests(unittest.TestCase):
    def test_setup_previews_then_applies(self):
        with World() as w:
            w.master("Alice_Qwen_Scene_One.json")
            w.master("Bob_Qwen_Scene_One.json")
            w.put("A-Home", "old/Bob_Qwen_Scene_One.json")      # a clone's leftover: B-Home must hold it first
            w.put("B-Home", "scene/Bob_Qwen_Scene_One.json")
            out, _ = w.run("setup", "-w", "A-Home")
            self.assertIn("preview", out)
            self.assertEqual(w.names("A-Home"), ["Bob_Qwen_Scene_One.json"], "a preview changes nothing")
            out, _ = w.run("setup", "-w", "A-Home", "--apply")
            self.assertEqual(w.names("A-Home"), ["Alice_Qwen_Scene_One.json"], "deployed its own set, removed the leftover")
            self.assertEqual(w.names("B-Home"), ["Bob_Qwen_Scene_One.json"], "the other home is untouched")
            self.assertNotIn("old", w.folders("A-Home"))

    def test_setup_refuses_a_planned_workspace(self):
        with World() as w:
            _out, code = w.run("setup", "-w", "Planned")
            self.assertIn("not active", str(code))


class EmptyDirTests(unittest.TestCase):
    def test_empty_dirs_counts_ignored_files_as_gone(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        try:
            (tmp / "a" / "b").mkdir(parents=True)
            f = tmp / "a" / "b" / "x.json"
            f.write_text("{}")
            (tmp / "zz_Keep" / "e").mkdir(parents=True)
            (tmp / ".hidden" / "e").mkdir(parents=True)
            self.assertEqual(cw.empty_dirs(tmp), [])
            self.assertEqual([p.relative_to(tmp).as_posix() for p in cw.empty_dirs(tmp, [f])], ["a/b", "a"])
            f.unlink()
            cw.prune_empty_dirs(tmp, True)
            self.assertFalse((tmp / "a").exists())
            self.assertTrue((tmp / "zz_Keep" / "e").exists())
            self.assertTrue((tmp / ".hidden" / "e").exists())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def image_wf(image):
    """A workflow whose only node is a LoadImage reading `image`."""
    return {"nodes": [{"type": "LoadImage", "widgets_values": [image, "image"]}], "id": image}


class InputPullTests(unittest.TestCase):
    """The default images you choose inside a workspace are read back into workspaces.json (inputs pull), flagged by status, and never overwritten by a reset."""

    PRIME, BARE = "Alice_Qwen_Alpha_1_Prime.json", "Alice_Qwen_Alpha_2_Bare_Figure.json"

    def world(self):
        w = World().__enter__()
        w.cfg["inputRoles"] = {"alpha/": "photo", "alpha/bare": "prime", "default": "bare"}
        w.cfg["sharedInput"] = str(w.tmp / "shared-input")
        w.cfg["sharedOutput"] = str(w.tmp / "shared-output")
        (w.tmp / "shared-input").mkdir()
        (w.tmp / "shared-input" / "alice_photo.png").write_bytes(b"x")
        (w.tmp / "shared-input" / "my_photo.png").write_bytes(b"x")
        w.cfg["photos"] = {"Alice": "alice_photo.png"}
        w.cfg["inputs"] = {"Alice": {"prime": "alice_prime.png", "bare": "alice_bare.png", "apose": "alice_bare.png"}}
        w.index = {"Alice_Qwen_Alpha_1_Prime": ("Alice", "alpha", []), "Alice_Qwen_Alpha_2_Bare_Figure": ("Alice", "alpha", ["bare"])}
        patches = [mock.patch.object(cw, "input_index", lambda cfg: dict(w.index)), mock.patch.object(cw, "CFG_PATH", w.tmp / "workspaces.json")]
        for p in patches:
            p.start()
        w.patches += patches
        for name in (self.PRIME, self.BARE):
            w.master(name, image_wf("placeholder.png"))
        return w

    def test_a_chosen_photo_is_pulled_into_the_config(self):
        w = self.world()
        try:
            w.put("A-Home", "alpha/" + self.PRIME, image_wf("my_photo.png"))
            w.put("A-Home", "alpha/" + self.BARE, image_wf("alice_prime.png"))
            out, _ = w.run("inputs", "pull", "--dry-run", "-w", "A-Home")
            self.assertIn("alice_photo.png -> my_photo.png", out)
            self.assertEqual(w.cfg["photos"]["Alice"], "alice_photo.png", "a dry run changes nothing")
            out, _ = w.run("inputs", "pull", "-w", "A-Home")
            self.assertEqual(w.cfg["photos"]["Alice"], "my_photo.png")
            self.assertEqual(w.cfg["inputs"]["Alice"]["prime"], "alice_prime.png", "an image that already matches is not touched")
            self.assertEqual(json.loads((w.tmp / "workspaces.json").read_text(encoding="utf-8"))["photos"]["Alice"], "my_photo.png")
            out, _ = w.run("inputs", "pull", "-w", "A-Home")
            self.assertIn("0 default image", out)
        finally:
            w.__exit__()

    def test_placeholders_and_other_heroes_images_are_not_a_choice(self):
        w = self.world()
        try:
            w.put("A-Home", "alpha/" + self.PRIME, image_wf("Alice_Qwen_X_Pose_00001_.png"))
            w.put("A-Home", "alpha/" + self.BARE, image_wf("bob_image_123.png"))
            out, _ = w.run("inputs", "pull", "-w", "A-Home")
            self.assertIn("0 default image", out)
            self.assertEqual(w.cfg["photos"]["Alice"], "alice_photo.png")
        finally:
            w.__exit__()

    def test_the_old_x_pose_workflow_counts_as_the_photo_workflow(self):
        w = self.world()
        try:
            w.put("A-Home", "alpha/Alice_Qwen_X_Pose.json", image_wf("legacy_choice.png"))
            w.run("inputs", "pull", "-w", "A-Home")
            self.assertEqual(w.cfg["photos"]["Alice"], "legacy_choice.png")
        finally:
            w.__exit__()

    def test_workflows_that_disagree_are_reported_not_pulled(self):
        w = self.world()
        try:
            w.index["Alice_Qwen_Alpha_3_Extra"] = ("Alice", "alpha", ["bare"])
            w.master("Alice_Qwen_Alpha_3_Extra.json", image_wf("placeholder.png"))
            w.put("A-Home", "alpha/" + self.BARE, image_wf("one.png"))
            w.put("A-Home", "alpha/Alice_Qwen_Alpha_3_Extra.json", image_wf("two.png"))
            out, _ = w.run("inputs", "pull", "-w", "A-Home")
            self.assertIn("MIXED", out)
            self.assertEqual(w.cfg["inputs"]["Alice"]["prime"], "alice_prime.png")
        finally:
            w.__exit__()

    def test_status_flags_a_choice_that_is_not_in_the_config(self):
        w = self.world()
        try:
            w.put("A-Home", "alpha/" + self.PRIME, image_wf("my_photo.png"))
            out, _ = w.run("status", "-w", "A-Home")
            self.assertIn("inputs-changed", out)
            self.assertIn("Alice photo", out)
            w.run("inputs", "pull", "-w", "A-Home")
            out, _ = w.run("status", "-w", "A-Home")
            self.assertNotIn("inputs-changed", out)
        finally:
            w.__exit__()

    def test_reset_stops_until_the_choice_is_pulled(self):
        w = self.world()
        try:
            w.cfg["homes"][0]["workspace"] = "A-Home"
            path = w.put("A-Home", "alpha/" + self.PRIME, image_wf("my_photo.png"))
            out, _ = w.run("inputs", "reset", "--hero", "Alice")
            self.assertIn("STOPPED", out)
            self.assertEqual(cw.input_image(cw.read_wf(path)), "my_photo.png", "your choice survives")
            w.run("inputs", "pull", "-w", "A-Home")
            out, _ = w.run("inputs", "reset", "--hero", "Alice")
            self.assertNotIn("STOPPED", out)
            self.assertEqual(cw.input_image(cw.read_wf(path)), "my_photo.png", "the pulled photo is now the default, so the reset keeps it")
        finally:
            w.__exit__()

    def test_dump_cfg_round_trips(self):
        cfg = {"a": {"x": 1, "y": [1, 2]}, "inputs": {"H": {"prime": "p.png"}}, "list": ["x" * 200, "y" * 200]}
        self.assertEqual(json.loads(cw.dump_cfg(cfg)), cfg)

    def test_role_override_groups_choices_and_survives_reset(self):
        name = "Alice_Qwen_X_Pose_Layer_OnePiece_Preserve_Audition"
        legacy = "Alice_Qwen_X_Pose_Layer_Legacy"
        cfg = {
            "inputs": {"Alice": {"prime": "alice_prime.png", "bare": "alice_bare.png"}},
            "inputRoles": {"default": "bare"},
            "inputRoleOverrides": {name: "prime"},
        }
        with tempfile.TemporaryDirectory(dir=cw.ROOT / "tmp") as tmp:
            root = pathlib.Path(tmp)
            paths = {}
            for stem, image in ((name, "alice_prime.png"), (legacy, "alice_bare.png")):
                path = root / (stem + ".json")
                cw.write_wf(path, image_wf(image))
                paths[stem + ".json"] = path
            repo = {n: ("set-a", "Alice", p) for n, p in paths.items()}
            index = {n[:-5]: ("Alice", "poses", ["one-piece"]) for n in paths}
            patches = (
                mock.patch.object(cw, "input_index", return_value=index),
                mock.patch.object(cw, "repo_files", return_value=repo),
                mock.patch.object(cw, "hero_groups", return_value={"Alice": "set-a"}),
                mock.patch.object(cw, "flow_index", return_value={}),
                mock.patch.object(cw, "workspace_ready", return_value=(True, "")),
                mock.patch.object(cw, "install_files", return_value=paths),
                mock.patch.object(cw, "is_hand_made", return_value=False),
            )
            with contextlib.ExitStack() as stack:
                for patch in patches:
                    stack.enter_context(patch)
                choices = cw.input_choices(cfg, ["fixture"])
                self.assertEqual({c["role"]: c["state"] for c in choices}, {"bare": "same", "prime": "same"})
                cw.write_wf(paths[name + ".json"], image_wf("wrong.png"))
                args = types.SimpleNamespace(root=None, hero="Alice", stage=None, match=None, dry_run=False, force=True)
                with contextlib.redirect_stdout(io.StringIO()):
                    cw.reset_inputs(cfg, args, workspaces=[])
                self.assertEqual(cw.input_image(cw.read_wf(paths[name + ".json"])), "alice_prime.png")
                self.assertEqual(cw.input_image(cw.read_wf(paths[legacy + ".json"])), "alice_bare.png")


class PhotoRepointTests(unittest.TestCase):
    """A chosen original photo that was renamed or moved (the originals tool) is found again by its id and re-pointed in workspaces.json, the workflows and the input folders."""

    OLD, NEW = "various_image_123_944x1104.png", "alice_image_123_944x1104.png"
    PRIME = "Alice_Qwen_Alpha_1_Prime.json"

    def world(self, folder="Alice", new_name=None):
        w = World().__enter__()
        lib = w.tmp / "lib"
        (lib / "Angels" / folder / "944x1104" / "full").mkdir(parents=True)
        (lib / "Angels" / folder / "gallery_944x1104_org").mkdir()
        (lib / "Angels" / folder / "944x1104" / "full" / (new_name or self.NEW)).write_bytes(b"png")
        (lib / "Angels" / folder / "gallery_944x1104_org" / self.OLD).write_bytes(b"old")
        w.cfg.update({"standardSize": [944, 1104], "photos": {"Alice": self.OLD}, "inputs": {}, "sharedInput": str(w.tmp / "shared-input"), "sharedOutput": str(w.tmp / "shared-output")})
        (w.tmp / "shared-input").mkdir()
        patches = [mock.patch.object(cw, "work_root", lambda cfg: lib), mock.patch.object(cw, "CFG_PATH", w.tmp / "workspaces.json")]
        for p in patches:
            p.start()
        w.patches += patches
        w.master(self.PRIME, image_wf(self.OLD))
        w.path = w.put("A-Home", "alpha/" + self.PRIME, image_wf(self.OLD))
        return w

    def test_a_renamed_photo_is_repointed_everywhere(self):
        w = self.world()
        try:
            out, _ = w.run("inputs", "photos", "--dry-run")
            self.assertIn(f"{self.OLD} -> {self.NEW}", out)
            self.assertEqual(w.cfg["photos"]["Alice"], self.OLD, "a dry run changes nothing")
            self.assertEqual(cw.input_image(cw.read_wf(w.path)), self.OLD)
            out, _ = w.run("inputs", "photos")
            self.assertEqual(w.cfg["photos"]["Alice"], self.NEW)
            self.assertEqual(json.loads((w.tmp / "workspaces.json").read_text(encoding="utf-8"))["photos"]["Alice"], self.NEW)
            self.assertEqual(cw.input_image(cw.read_wf(w.path)), self.NEW)
            self.assertEqual(cw.input_image(cw.read_wf(w.masters[self.PRIME][2])), self.NEW)
            self.assertTrue((w.tmp / "shared-input" / self.NEW).exists(), "the scaled photo is copied to the input folder")
            self.assertTrue(
                list(cw.storage_root(w.cfg, "backup").rglob(self.PRIME)),
                "the changed workspace file is backed up",
            )
            out, _ = w.run("inputs", "photos")
            self.assertIn("every chosen photo is where", out)
        finally:
            w.__exit__()

    def test_a_workflow_that_loads_something_else_is_left_alone(self):
        w = self.world()
        try:
            other = w.put("A-Home", "alpha/Alice_Qwen_Alpha_2_Bare.json", image_wf("my_own_choice.png"))
            w.master("Alice_Qwen_Alpha_2_Bare.json", image_wf("placeholder.png"))
            w.run("inputs", "photos")
            self.assertEqual(cw.input_image(cw.read_wf(other)), "my_own_choice.png")
        finally:
            w.__exit__()

    def test_a_photo_in_another_heros_folder_is_reported_not_guessed(self):
        w = self.world(folder="Various")
        try:
            out, _ = w.run("inputs", "photos")
            self.assertIn("ELSEWHERE", out)
            self.assertEqual(w.cfg["photos"]["Alice"], self.OLD)
        finally:
            w.__exit__()

    def test_a_photo_whose_original_is_gone_is_reported(self):
        w = self.world(new_name="alice_image_999_944x1104.png")
        try:
            out, _ = w.run("inputs", "photos")
            self.assertIn("MISSING", out)
            self.assertEqual(w.cfg["photos"]["Alice"], self.OLD)
        finally:
            w.__exit__()

    def test_a_photo_already_in_the_heros_folder_is_left_alone(self):
        w = self.world()
        try:
            w.cfg["photos"]["Alice"] = self.NEW
            out, _ = w.run("inputs", "photos")
            self.assertIn("every chosen photo is where", out)
        finally:
            w.__exit__()

    def test_a_chosen_headshot_is_found_and_not_swapped_back_for_the_full_photo(self):
        w = self.world()
        try:
            head = "alice_image_123_head_944x1104.png"
            # still in the former headshot_944x1104 folder: found until originals.cmd moves it to 944x1104/head
            (w.tmp / "lib" / "Angels" / "Alice" / "headshot_944x1104").mkdir()
            (w.tmp / "lib" / "Angels" / "Alice" / "headshot_944x1104" / head).write_bytes(b"png")
            w.cfg["photos"]["Alice"] = head
            self.assertEqual(cw.find_image(w.cfg, head).name, head)
            out, _ = w.run("inputs", "photos")
            self.assertIn("every chosen photo is where", out)
            self.assertEqual(w.cfg["photos"]["Alice"], head)
        finally:
            w.__exit__()

    def test_a_photo_renamed_to_the_shot_convention_is_found_by_its_date_and_time(self):
        w = self.world(new_name="alice_shot_20260101120000_944x1104.png")
        try:
            w.cfg["photos"]["Alice"] = "various_screenshot_20260101_120000_facebook_944x1104.png"
            self.assertEqual(cw.photo_key("various_screenshot_20260101_120000_facebook_944x1104.png"), cw.photo_key("alice_shot_20260101120000_944x1104.png"))
            out, _ = w.run("inputs", "photos")
            self.assertEqual(w.cfg["photos"]["Alice"], "alice_shot_20260101120000_944x1104.png")
            self.assertEqual(cw.photo_key("alice_pic_1234abcd_944x1104.png"), "pic_1234abcd")
            self.assertEqual(cw.photo_key("alice_image_77_944x1104.png"), "image_77")
            self.assertIsNone(cw.photo_key("angelo_photo_944x1104.png"))
        finally:
            w.__exit__()

    def test_find_image_looks_in_the_library(self):
        w = self.world()
        try:
            self.assertEqual(cw.find_image(w.cfg, self.NEW).name, self.NEW)
            self.assertIsNone(cw.find_image(w.cfg, self.OLD), "the _org archive is not part of the library")
        finally:
            w.__exit__()


def denoise_wf(value):
    """A workflow with the outer subgraph node that exposes a denoise widget, as the generated ones do."""
    return {"nodes": [{"type": "sg", "widgets_values": ["pos", "neg", value], "widgets_values_named": {"positive": "pos", "negative": "neg", "denoise": value}}],
            "definitions": {"subgraphs": [{"id": "sg"}]}}


class DenoiseTests(unittest.TestCase):
    """denoise --reset sets the denoise every generated workflow should start at, but never overwrites one you set by hand in a workspace."""

    STEM = "Alice_Qwen_Armor_Plate"

    def world(self):
        w = World().__enter__()
        w.cfg["templates"] = {"poses": "workflows/_templates/ST1_Qwen_A_Pose.json", "default": "workflows/_templates/ST2_Qwen_Edit.json"}
        w.cfg["engines"] = {"firered": {"template": "workflows/_templates/ST3_FireRed_Final.json"}}
        w.cfg["denoise"] = {"pick": "high", "golden": 0.9}
        patch = mock.patch.object(cw, "denoise_plan", lambda cfg: {self.STEM: ("Alice", "armor", ["wardrobe"], "bare", 0.9)})
        patch.start()
        w.patches.append(patch)
        w.master(self.STEM + ".json", denoise_wf(0.7))
        return w

    def value(self, path):
        return cw.get_denoise(cw.read_wf(path))

    def test_reset_sets_the_repo_and_the_workspace_copies(self):
        w = self.world()
        try:
            path = w.put("A-Home", "armor/" + self.STEM + ".json", denoise_wf(0.7))
            out, _ = w.run("denoise", "--reset", "--hero", "Alice")
            self.assertEqual(self.value(w.masters[self.STEM + ".json"][2]), 0.9)
            self.assertEqual(self.value(path), 0.9)
            self.assertIn("1 in repo", out)
        finally:
            w.__exit__()

    def test_a_value_set_by_hand_in_a_workspace_is_kept(self):
        w = self.world()
        try:
            path = w.put("A-Home", "armor/" + self.STEM + ".json", denoise_wf(1.0))
            out, _ = w.run("denoise", "--reset", "--hero", "Alice")
            self.assertIn("KEPT", out)
            self.assertEqual(self.value(path), 1.0, "your 1.0 survives")
            self.assertEqual(self.value(w.masters[self.STEM + ".json"][2]), 0.9, "the repo copy still follows the tool")
            out, _ = w.run("denoise", "--reset", "--hero", "Alice", "--force")
            self.assertEqual(self.value(path), 0.9, "--force overwrites it")
        finally:
            w.__exit__()

    def test_a_dry_run_changes_nothing(self):
        w = self.world()
        try:
            path = w.put("A-Home", "armor/" + self.STEM + ".json", denoise_wf(0.7))
            w.run("denoise", "--reset", "--hero", "Alice", "--dry-run")
            self.assertEqual(self.value(path), 0.7)
            self.assertEqual(self.value(w.masters[self.STEM + ".json"][2]), 0.7)
        finally:
            w.__exit__()


class TemplateRangeTests(unittest.TestCase):
    """The stage templates carry the denoise ranges (the high end is used) and the edit stages state the likeness (Critical details)."""

    def setUp(self):
        self.tpl = pathlib.Path(cw.__file__).resolve().parents[2] / "data/art/_templates/heroes"
        sys.path.insert(0, str(pathlib.Path(cw.__file__).resolve().parents[1] / "generators"))
        import gen_prompt
        self.gp = gen_prompt

    def high(self, name):
        import re
        path = next(self.tpl.rglob(name))
        header = path.read_text(encoding="utf-8").split("\nprompt:", 1)[0]
        if "{{DENOISE_HINT}}" in header:
            relative = path.relative_to(pathlib.Path(cw.__file__).resolve().parents[2]).as_posix()
            header = header.replace("{{DENOISE_HINT}}", self.gp.DENOISE_HINT_DEFAULTS[relative])
        m = re.search(r"Denoise ~(\d(?:\.\d+)?)(?:-(\d(?:\.\d+)?))?", header)
        return float(m.group(2) or m.group(1))

    def test_edits_that_change_a_lot_run_high(self):
        for name in ("bare-human.txt", "bare-male-human.txt", "armor-human.txt", "clothing-human.txt", "scene-glamour-human.txt", "scene-with-outfit-human.txt", "pose-view-human.txt", "showcase-human.txt"):
            self.assertGreaterEqual(self.high(name), 0.9, name)
        self.assertGreaterEqual(self.high("motion-human.txt"), 0.95)
        for name in ("head-human.txt", "hair-human.txt", "scene-staged-human.txt"):
            self.assertGreaterEqual(self.high(name), 0.8, name)
        self.assertLessEqual(self.high("polish-human.txt"), 0.4, "the polish pass stays light")

    def test_every_edit_template_with_a_key_block_slot_switches_it_on(self):
        for p in sorted(self.tpl.rglob("*.txt")):
            text = p.read_text(encoding="utf-8")
            if "{{DENOISE}}" in text.split("\nprompt:", 1)[0]:
                continue  # These templates select denoise and key details per card.
            if "{{KEY_BLOCK}}" in text and self.high(p.name) >= 0.7 and p.name not in ("pose-female-human.txt", "pose-male-human.txt"):
                self.assertTrue(self.gp.TEMPLATE_KEY_DEFAULTS.get(p.name), f"{p.name} runs at a high denoise but states no Critical details")


if __name__ == "__main__":
    unittest.main(verbosity=1)
