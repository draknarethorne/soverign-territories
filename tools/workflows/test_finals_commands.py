#!/usr/bin/env python3
"""Tests for `finals` (candidates and finals) in comfy_workflows.py, against throwaway workspaces.

They pin down: a file is placed from its NAME (misspelling, wrong folder, a drop into the zz_Final root), nothing is ever deleted (a duplicate goes to backup, a different
file is a conflict and stays), tidy and cleanup never touch these folders, promote keeps one final per slot and archives the old one, pull keeps both kinds in the repo
arranged like the main tree, and deploy puts back what a workspace lacks without duplicating what it holds elsewhere.

Run: python tools/workflows/test_finals_commands.py
"""
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402
from test_comfy_workflows import World  # noqa: E402

PRIME = {"nodes": [{"type": "SaveImage", "widgets_values": ["set-a/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime"]}], "id": "master"}
BARE = {"nodes": [{"type": "SaveImage", "widgets_values": ["set-a/Alice/1_Alpha/2_Bare/Alice_Qwen_Alpha_2_Bare_Figure"]}], "id": "master"}


def patched(w):
    return (mock.patch.object(cw, "CANDIDATES", w.repo / "_candidates"), mock.patch.object(cw, "FINALS", w.repo / "_final"), mock.patch.object(cw, "ROOT", w.tmp))


def world():
    w = World()
    return w


class FinalsTests(unittest.TestCase):
    def setUp(self):
        self.w = World().__enter__()
        for p in patched(self.w):
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.w.__exit__, None, None, None)
        self.w.master("Alice_Qwen_Alpha_1_Prime.json", PRIME)
        self.w.master("Alice_Qwen_Alpha_2_Bare_Figure.json", BARE)
        self.d = self.w.dir("A-Home")

    def names(self):
        return sorted(p.relative_to(self.d).as_posix() for p in self.d.rglob("*.json"))

    def test_loose_save_is_filed_by_its_name_and_the_tree_is_mirrored(self):
        self.w.put("A-Home", "Alice_Qwen_Alpha_1_Prime_00004_.json")
        self.w.run("finals", "sort", "-w", "A-Home", "--apply")
        self.assertEqual(self.names(), ["zz_Candidates/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00004_.json"])

    def test_a_shot_saved_straight_into_zz_shots_is_filed_by_phase_but_one_in_your_own_subfolder_stays(self):
        self.w.put("A-Home", "zz_Shots/Alice_Qwen_Alpha_2_Bare_Figure.json")
        self.w.put("A-Home", "zz_Shots/armor/Alice_Qwen_Alpha_1_Prime.json")
        self.w.run("finals", "sort", "-w", "A-Home", "--apply")
        self.assertEqual(self.names(), ["zz_Shots/Alice/1_Alpha/2_Bare/Alice_Qwen_Alpha_2_Bare_Figure.json", "zz_Shots/armor/Alice_Qwen_Alpha_1_Prime.json"])

    def test_an_old_x_pose_save_is_filed_as_the_prime_and_keeps_its_name(self):
        self.w.put("A-Home", "Alice_Qwen_X_Pose_00004_.json")
        self.w.run("finals", "sort", "-w", "A-Home", "--apply")
        self.assertEqual(self.names(), ["zz_Candidates/Alice/1_Alpha/1_Prime/Alice_Qwen_X_Pose_00004_.json"])

    def test_preview_changes_nothing(self):
        self.w.put("A-Home", "Alice_Qwen_Alpha_1_Prime_00004_.json")
        out, _ = self.w.run("finals", "sort", "-w", "A-Home")
        self.assertEqual(self.names(), ["Alice_Qwen_Alpha_1_Prime_00004_.json"])
        self.assertIn("would move", out)

    def test_misspelling_wrong_folder_and_a_drop_in_the_final_root_are_corrected(self):
        self.w.put("A-Home", "zz_Final/alice_qwn_alpha_1_prim_00007_.json")
        self.w.put("A-Home", "zz_Candidates/random/Alice_Qwen_Alpha_2_Bare_Figure_00002_.json")
        self.w.run("finals", "sort", "-w", "A-Home", "--apply")
        self.assertEqual(self.names(), ["zz_Candidates/Alice/1_Alpha/2_Bare/Alice_Qwen_Alpha_2_Bare_Figure_00002_.json",
                                        "zz_Final/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00007_.json"])
        self.assertFalse((self.d / "zz_Candidates" / "random").exists(), "the emptied folder is removed")

    def test_a_file_that_cannot_be_placed_is_left_exactly_where_it_is_in_every_zz_folder(self):
        for rel in ("zz_Final/Nobody_Qwen_Whatever_00001_.json", "zz_Candidates/Nobody_Qwen_Whatever_00002_.json", "zz_Shots/Nobody_Qwen_Whatever.json",
                    "zz_Curated/zz_Curated_Alice_Qwen_Hand_Made.json", "Nobody_Qwen_Whatever_00003_.json"):
            self.w.put("A-Home", rel)
        before = self.names()
        out, _ = self.w.run("finals", "sort", "-w", "A-Home", "--apply")
        self.assertEqual(self.names(), before)
        self.assertIn("not placeable", out)

    def test_identical_duplicate_goes_to_backup_and_a_different_one_is_a_conflict(self):
        proper = "zz_Final/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00001_.json"
        self.w.put("A-Home", proper, {"nodes": [], "id": "a"})
        self.w.put("A-Home", "zz_Final/Alice_Qwen_Alpha_1_Prime_00001_.json", {"nodes": [], "id": "a"})
        self.w.run("finals", "sort", "-w", "A-Home", "--apply")
        self.assertEqual(self.names(), [proper])
        self.assertTrue(list((self.w.tmp / "backup").rglob("Alice_Qwen_Alpha_1_Prime_00001_.json")))
        self.w.put("A-Home", "zz_Final/Alice_Qwen_Alpha_1_Prime_00001_.json", {"nodes": [], "id": "b"})
        out, _ = self.w.run("finals", "sort", "-w", "A-Home", "--apply")
        self.assertIn("CONFLICT", out)
        self.assertEqual(len(self.names()), 2, "the different file stays where it was")

    def test_tidy_and_cleanup_never_touch_candidates_or_finals(self):
        self.w.put("A-Home", "zz_Final/Anywhere/Alice_Qwen_Alpha_1_Prime_00001_.json")
        self.w.put("A-Home", "zz_Candidates/Alice_Qwen_Alpha_2_Bare_Figure_00002_.json")
        before = self.names()
        self.w.run("tidy", "-w", "A-Home", "--apply")
        self.w.run("cleanup", "-w", "A-Home", "--apply")
        self.assertEqual(self.names(), before)

    def test_promote_makes_one_final_per_slot_and_archives_the_old_one(self):
        self.w.put("A-Home", "zz_Candidates/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00001_.json", {"nodes": [], "id": "one"})
        self.w.put("A-Home", "zz_Candidates/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00002_.json", {"nodes": [], "id": "two"})
        self.w.run("finals", "promote", "Alice_Qwen_Alpha_1_Prime_00001", "-w", "A-Home", "--apply")
        self.w.run("finals", "promote", "Alice_Qwen_Alpha_1_Prime_00002", "-w", "A-Home", "--apply")
        finals = [n for n in self.names() if n.startswith("zz_Final/")]
        self.assertEqual([n for n in finals if "_previous" not in n], ["zz_Final/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00002_.json"])
        self.assertEqual(len([n for n in finals if "_previous" in n]), 1)
        self.assertEqual(len([n for n in self.names() if n.startswith("zz_Candidates/")]), 2, "promoting copies; the candidates stay")

    def test_promote_asks_for_more_of_the_name_when_it_is_ambiguous(self):
        self.w.put("A-Home", "zz_Candidates/Alice_Qwen_Alpha_1_Prime_00001_.json")
        self.w.put("A-Home", "zz_Candidates/Alice_Qwen_Alpha_1_Prime_00002_.json")
        out, _ = self.w.run("finals", "promote", "Alpha_1_Prime", "-w", "A-Home", "--apply")
        self.assertIn("matches 2 files", out)
        self.assertFalse(any(n.startswith("zz_Final/") for n in self.names()))

    def test_pull_keeps_candidates_and_finals_in_the_repo_arranged_like_the_main_tree(self):
        self.w.put("A-Home", "Alice_Qwen_Alpha_1_Prime_00004_.json", {"nodes": [], "id": "c"})
        self.w.put("A-Home", "zz_Final/Alice_Qwen_Alpha_2_Bare_Figure_00009_.json", {"nodes": [], "id": "f"})
        self.w.run("pull", "-w", "A-Home")
        self.assertEqual(json.loads((self.w.repo / "_candidates/set-a/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00004_.json").read_text())["id"], "c")
        self.assertEqual(json.loads((self.w.repo / "_final/set-a/Alice/1_Alpha/2_Bare/Alice_Qwen_Alpha_2_Bare_Figure_00009_.json").read_text())["id"], "f")

    def test_deploy_restores_what_is_missing_but_not_what_the_workspace_holds_elsewhere(self):
        cw.write_wf(self.w.repo / "_final/set-a/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00001_.json", {"nodes": [], "id": "f1"})
        cw.write_wf(self.w.repo / "_final/set-a/Alice/1_Alpha/2_Bare/Alice_Qwen_Alpha_2_Bare_Figure_00002_.json", {"nodes": [], "id": "f2"})
        self.w.put("A-Home", "zz_Final/misfiled/Alice_Qwen_Alpha_2_Bare_Figure_00002_.json", {"nodes": [], "id": "f2"})
        self.w.run("finals", "deploy", "-w", "A-Home", "--apply")
        self.assertEqual(self.names(), ["zz_Final/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00001_.json", "zz_Final/misfiled/Alice_Qwen_Alpha_2_Bare_Figure_00002_.json"])
        self.w.run("finals", "sort", "-w", "A-Home", "--apply")
        self.assertIn("zz_Final/Alice/1_Alpha/2_Bare/Alice_Qwen_Alpha_2_Bare_Figure_00002_.json", self.names())

    def test_status_counts_and_slots(self):
        self.w.put("A-Home", "Alice_Qwen_Alpha_1_Prime_00004_.json")
        self.w.put("A-Home", "zz_Final/Alice_Qwen_Alpha_2_Bare_Figure_00009_.json")
        out, _ = self.w.run("finals", "status", "-w", "A-Home")
        self.assertIn("1 candidates (1 loose), 1 finals", out)
        self.assertIn("prime c1", out)
        self.assertIn("bare FINAL", out)

    def test_reclassify_cleans_the_repo_moves_dedupes_and_leaves_what_it_cannot_place(self):
        cw.write_wf(self.w.repo / "_shots/set-a/Alice/Alice_Qwen_Alpha_1_Prime_00003_.json", {"nodes": [], "id": "s"})
        cw.write_wf(self.w.repo / "_shots/set-a/Alice/armor/Alice_Qwen_Alpha_1_Prime_00005_.json", {"nodes": [], "id": "kept"})
        cw.write_wf(self.w.repo / "_candidates/set-a/Alice/Alice_Qwen_Alpha_2_Bare_Figure_00006_.json", {"nodes": [], "id": "dup"})
        cw.write_wf(self.w.repo / "_candidates/set-a/Alice/1_Alpha/2_Bare/Alice_Qwen_Alpha_2_Bare_Figure_00006_.json", {"nodes": [], "id": "dup"})
        cw.write_wf(self.w.repo / "_final/set-a/Alice/alice_qwn_alpha_1_prim_00008_.json", {"nodes": [], "id": "typo"})
        cw.write_wf(self.w.repo / "_candidates/set-a/Alice/Mystery_Qwen_Nothing_00001_.json", {"nodes": [], "id": "odd"})
        cw.write_wf(self.w.repo / "_shots/set-a/Alice/Alice_Qwen_Alpha_2_Bare_Figure.json", {"nodes": [], "id": "plain-shot"})
        with mock.patch.object(cw, "SHOTS", self.w.repo / "_shots"), mock.patch.object(cw, "shot_files", self._shots):
            out, _ = self.w.run("finals", "reclassify")
            self.assertIn("would move", out)
            self.assertTrue((self.w.repo / "_shots/set-a/Alice/Alice_Qwen_Alpha_1_Prime_00003_.json").exists(), "a preview changes nothing")
            self.w.run("finals", "reclassify", "--apply")
        r = self.w.repo
        self.assertTrue((r / "_candidates/set-a/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00003_.json").exists())
        self.assertTrue((r / "_shots/set-a/Alice/armor/Alice_Qwen_Alpha_1_Prime_00005_.json").exists(), "a shot in a subfolder was deliberate and stays")
        self.assertTrue((r / "_candidates/set-a/Alice/1_Alpha/2_Bare/Alice_Qwen_Alpha_2_Bare_Figure_00006_.json").exists())
        self.assertFalse((r / "_candidates/set-a/Alice/Alice_Qwen_Alpha_2_Bare_Figure_00006_.json").exists())
        self.assertTrue(list((self.w.tmp / "backup").rglob("Alice_Qwen_Alpha_2_Bare_Figure_00006_.json")), "the duplicate went to backup, not away")
        self.assertTrue((r / "_final/set-a/Alice/1_Alpha/1_Prime/Alice_Qwen_Alpha_1_Prime_00008_.json").exists(), "typo corrected")
        self.assertTrue((r / "_candidates/set-a/Alice/Mystery_Qwen_Nothing_00001_.json").exists(), "an unplaceable name stays exactly where it is")
        self.assertTrue((r / "_shots/set-a/Alice/1_Alpha/2_Bare/Alice_Qwen_Alpha_2_Bare_Figure.json").exists(), "a plain top-level shot is filed by phase and keeps its name")

    def _shots(self):
        out = {}
        root = self.w.repo / "_shots"
        for g in sorted(root.iterdir()):
            for h in sorted(g.iterdir()):
                for p in sorted(h.rglob("*.json")):
                    out[(h.name, p.relative_to(h).as_posix())] = (g.name, p)
        return out


if __name__ == "__main__":
    unittest.main()
