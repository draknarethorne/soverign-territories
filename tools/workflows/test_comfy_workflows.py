#!/usr/bin/env python3
"""Tests for the homes, the accepts rule and the guards of comfy_workflows.py, run against throwaway workspaces (nothing real is touched).

They pin down what must never regress: a set with no home workspace stops a deploy instead of landing somewhere else, a workspace that neither homes nor accepts a set
is refused, planned or missing workspaces are skipped, hand-made workflows (zz_ folders, zz_Curated_/test_ names) are never replaced, moved or removed, cleanup only
removes what a workspace is not home for and only when the home workspace has an identical copy, and empty folders are pruned (never the zz_ ones).

Run: python tools/workflows/test_comfy_workflows.py
"""
import contextlib
import io
import json
import pathlib
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402

SUBPATH = "ComfyUI/user/default/workflows"
MASTER = {"nodes": [], "id": "master"}


class World:
    """Heroes Alice (set-a: homes A-Home and Alice-Own), Bob (set-b: B-Home), Cleo (set-orphan: no home), Dana (set-planned: Planned workspace, status planned)
    and Eve (set-ghost: Ghost, active but not installed). Series accepts set-a on request, Brand accepts any set, Guest accepts nothing."""

    HEROES = {"Alice": "set-a", "Bob": "set-b", "Cleo": "set-orphan", "Dana": "set-planned", "Eve": "set-ghost"}

    def __enter__(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.cfg = {
            "installsRoot": str(self.tmp / "installs"),
            "workflowsSubpath": SUBPATH,
            "exclude": ["X_*.json"],
            "stageTemplates": "ST?_*.json",
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
        }
        for ws in self.cfg["workspaces"]:
            if ws != "Ghost":
                self.dir(ws).mkdir(parents=True)
        self.masters = {}
        self.patches = [
            mock.patch.object(cw, "load_cfg", lambda: self.cfg),
            mock.patch.object(cw, "hero_groups", lambda: dict(self.HEROES)),
            mock.patch.object(cw, "repo_files", lambda cfg: dict(self.masters)),
            mock.patch.object(cw, "curated_files", lambda folder=None: {}),
            mock.patch.object(cw, "shot_files", lambda: {}),
            mock.patch.object(cw, "BACKUPS", self.tmp / "backup"),
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
        self.assertEqual(cw.flow_suffix("frame"), "Frame")
        self.assertEqual(cw.flow_suffix("tight-crop"), "TightCrop")
        cfg = {"photos": {"Alice": "alice_image_1_944x1104.png"}}
        self.assertEqual([i["name"] for i in cw.prompt_index(cfg)], ["Alice_Qwen_Alpha_1_Prime", "Alice_Qwen_Alpha_2_Bare"], "no flows, no variants")
        cfg["flows"] = {"frame": {"photos": {"Alice": "alice_image_1_frame_944x1104.png"}}, "other": {"photos": {}}}
        names = {i["name"]: i for i in cw.prompt_index(cfg)}
        self.assertEqual(sorted(names), ["Alice_Qwen_Alpha_1_Prime", "Alice_Qwen_Alpha_1_Prime_Frame", "Alice_Qwen_Alpha_2_Bare"], "only the Prime has flows")
        v = names["Alice_Qwen_Alpha_1_Prime_Frame"]
        self.assertEqual((v["flow"], v["path"], v["prefix"].rsplit("/", 1)[-1]), ("frame", names["Alice_Qwen_Alpha_1_Prime"]["path"], "Alice_Qwen_Alpha_1_Prime_Frame"), "the same prompt, its own output prefix")
        self.assertNotIn("flow", names["Alice_Qwen_Alpha_1_Prime"])
        self.assertEqual(cw.flow_index(cfg), {"Alice_Qwen_Alpha_1_Prime_Frame": "frame", "Alice_FireRed_Alpha_1_Prime_Frame": "frame"})
        self.assertEqual(cw.flow_photo(cfg, "frame", "Alice"), "alice_image_1_frame_944x1104.png")
        self.assertIsNone(cw.flow_photo(cfg, "frame", "Bob"))

    def test_firered_gets_an_identity_lock_in_front_of_the_prime_and_nothing_else_changes(self):
        tmp = self.world()
        face = tmp / "lock.txt"
        face.write_text("Identity lock: use the face.\n")
        with mock.patch.object(cw, "ROOT", tmp):
            cfg = {"engines": {"firered": {"primeFace": "lock.txt"}}}
            prime = {"engine": "firered", "stage": "alpha", "family": None, "stem": "Alice_Alpha_1_Prime"}
            self.assertEqual(cw.engine_prompt(cfg, prime, "hello"), "Identity lock: use the face.\n\nhello")
            self.assertEqual(cw.engine_prompt(cfg, {**prime, "stem": "Alice_Alpha_1_Prime_Frame"}, "hello"), "Identity lock: use the face.\n\nhello", "the flow's Prime too")
            self.assertEqual(cw.engine_prompt(cfg, {**prime, "engine": "qwen"}, "hello"), "hello", "Qwen is not touched")
            self.assertEqual(cw.engine_prompt(cfg, {**prime, "stem": "Alice_Alpha_2_Bare"}, "hello"), "hello", "nor is any later stage")
            self.assertEqual(cw.engine_prompt({"engines": {"firered": {}}}, prime, "hello"), "hello", "off unless configured")

    def test_set_inputs_with_a_flow_writes_the_flow_and_leaves_the_normal_photo(self):
        cfg = {"photos": {"Alice": "alice_image_1_944x1104.png"}, "inputs": {}}
        args = types.SimpleNamespace(set="alice", flow="frame", photo="alice_image_1_frame_944x1104.png", dry_run=True, prime=None, bare=None, apose=None, heels=None, scene=None, polish=None)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cw.set_inputs(cfg, args)
        self.assertEqual(cfg["flows"]["frame"]["photos"], {"Alice": "alice_image_1_frame_944x1104.png"})
        self.assertEqual(cfg["photos"]["Alice"], "alice_image_1_944x1104.png", "the normal flow is untouched")
        self.assertIn("flow frame", out.getvalue())
        args.photo = None
        with self.assertRaises(SystemExit):
            cw.set_inputs(cfg, args)


class FirstShotTests(unittest.TestCase):
    """The first-shot experiments (1_Alpha/1b_Experiments/<family>): P3 bare figure and P2 neutral base layer start from the photo like the Prime, in folders of their own."""

    def test_the_experiment_folders_and_the_family_round_trip(self):
        lay = cw.art_layout
        card = {"stage": "alpha", "artId": "angelica-alpha-1b-bare-base", "components": {}}
        self.assertEqual(lay.family(card, "angel-primes"), ["base", "bare-base"])
        dirs = lay.dirs_for("alpha", ["base", "bare-base"])
        self.assertEqual(dirs, ["1_Alpha", "1b_Experiments", "bare-base"])
        self.assertEqual(lay.parse_dirs(dirs), ("alpha", ["base", "bare-base"]))
        self.assertEqual(lay.dirs_for("alpha", ["base", "neutral-base"]), ["1_Alpha", "1b_Experiments", "neutral-base"], "P2 and P3 never share a folder")
        self.assertEqual(lay.parse_dirs(["1_Alpha", "1_Prime"]), ("alpha", []), "the Prime is untouched")

    def test_only_the_first_shots_take_the_photo(self):
        def item(stem, family=()):
            return {"stage": "alpha", "family": list(family), "stem": stem}
        for stem, fam in (("Alice_Alpha_1_Prime", ()), ("Alice_Alpha_1b_BareBase", ("base", "bare-base")), ("Alice_Alpha_1b_NeutralBase", ("base", "neutral-base"))):
            self.assertTrue(cw.takes_photo(item(stem, fam)), stem)
        self.assertFalse(cw.takes_photo(item("Alice_Alpha_2_Bare", ("bare",))))
        self.assertFalse(cw.takes_photo(item("Alice_Alpha_2b_CelestialSuit", ("bare", "celestial"))))
        self.assertFalse(cw.takes_photo({"stage": "poses", "family": [], "stem": "Alice_X_Pose"}))

    def test_a_flow_gives_the_experiment_bases_their_own_frame_variants(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        for sub, stem in (("1_Prime", "Alice_Alpha_1_Prime"), ("1b_Experiments/bare-base", "Alice_Alpha_1b_BareBase"), ("1b_Experiments/neutral-base", "Alice_Alpha_1b_NeutralBase")):
            d = tmp / "set-a" / "Alice" / "1_Alpha" / sub
            d.mkdir(parents=True)
            (d / f"{stem}.txt").write_text("=== x ===\n\nprompt:\n\nhello\n\n----------\nnegative prompt:\n\nbad\n")
        cfg = {"photos": {"Alice": "a.png"}, "flows": {"frame": {"photos": {"Alice": "a_frame.png"}}}}
        with mock.patch.object(cw, "PROMPTS", tmp):
            names = {i["name"]: i for i in cw.prompt_index(cfg)}
        self.assertEqual(sorted(names), ["Alice_Qwen_Alpha_1_Prime", "Alice_Qwen_Alpha_1_Prime_Frame", "Alice_Qwen_Alpha_1b_BareBase", "Alice_Qwen_Alpha_1b_BareBase_Frame",
                                         "Alice_Qwen_Alpha_1b_NeutralBase", "Alice_Qwen_Alpha_1b_NeutralBase_Frame"])
        self.assertIn("1_Alpha/1b_Experiments/bare-base/", names["Alice_Qwen_Alpha_1b_BareBase_Frame"]["prefix"], "output folders keep P2 and P3 apart")
        self.assertIn("1_Alpha/1b_Experiments/neutral-base/", names["Alice_Qwen_Alpha_1b_NeutralBase"]["prefix"])
        self.assertEqual(cw.input_role({"inputs": {"Alice": {}}, "inputRoles": {"alpha/base": "photo", "default": "bare"}}, "Alice", "alpha", ["base", "bare-base"]), "photo")


class RoutingTests(unittest.TestCase):
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

    def test_orphan_cleanup_skips_hand_made_and_prunes(self):
        with World() as w:
            w.put("A-Home", "scene/gone/Alice_Qwen_Scene_Old.json")
            hand = w.put("A-Home", "zz_Curated/Alice/Alice_Qwen_Scene_Mine.json")
            w.run("cleanup", "--orphans", "--match", "Alice_Qwen_Scene_", "-w", "A-Home", "--apply")
            self.assertTrue(hand.exists())
            self.assertFalse((w.dir("A-Home") / "scene").exists(), "the emptied folders are pruned")
            moved = list((w.tmp / "backup").rglob("Alice_Qwen_Scene_Old.json"))
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
            self.assertFalse((w.tmp / "backup").exists())

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
            backed = sorted(p.name for p in (w.tmp / "backup").rglob("*.json"))
            self.assertEqual(backed, ["Alice_Qwen_Scene_One.json", "Bob_Qwen_Scene_One.json"], "removed files are moved to backup, not deleted")

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


class PhotoRepointTests(unittest.TestCase):
    """A chosen original photo that was renamed or moved (the originals tool) is found again by its id and re-pointed in workspaces.json, the workflows and the input folders."""

    OLD, NEW = "various_image_123_944x1104.png", "alice_image_123_944x1104.png"
    PRIME = "Alice_Qwen_Alpha_1_Prime.json"

    def world(self, folder="Alice", new_name=None):
        w = World().__enter__()
        lib = w.tmp / "lib"
        (lib / "Angels" / folder / "gallery_944x1104").mkdir(parents=True)
        (lib / "Angels" / folder / "gallery_944x1104_org").mkdir()
        (lib / "Angels" / folder / "gallery_944x1104" / (new_name or self.NEW)).write_bytes(b"png")
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
            self.assertTrue(list((w.tmp / "backup").rglob(self.PRIME)), "the changed workspace file is backed up")
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
        m = re.search(r"Denoise ~(\d(?:\.\d+)?)(?:-(\d(?:\.\d+)?))?", path.read_text(encoding="utf-8").split("\nprompt:", 1)[0])
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
            if "{{KEY_BLOCK}}" in text and self.high(p.name) >= 0.7 and p.name not in ("pose-female-human.txt", "pose-male-human.txt"):
                self.assertTrue(self.gp.TEMPLATE_KEY_DEFAULTS.get(p.name), f"{p.name} runs at a high denoise but states no Critical details")


if __name__ == "__main__":
    unittest.main(verbosity=1)
