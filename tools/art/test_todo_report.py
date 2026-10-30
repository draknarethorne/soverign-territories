#!/usr/bin/env python3
"""Smoke tests for todo_report.py: the tables list every top-tier card, the open work comes from the active plans as one queue, and the notes section survives a regeneration.
Run: python tools/art/test_todo_report.py"""
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import todo_report as tr  # noqa: E402


class TodoReportTests(unittest.TestCase):
    def test_every_top_tier_card_has_a_row(self):
        text = tr.build()
        for heading, count in (("Angel women", 11), ("Angel men", 11), ("Drakn sisters", 10), ("Drakn Bound men", 10), ("Elder Dragons", 10)):
            self.assertIn(f"### {heading} ({count})", text)
        for hero in ("Seraphine", "Luzariel", "Draknara", "Pyraxis"):
            self.assertIn(f"| {hero} |", text)

    def test_open_work_comes_from_the_active_plans_as_one_queue_with_the_user_first(self):
        text = tr.build()
        self.assertIn("## Open work, by priority", text)
        self.assertIn("- [ ]", text)
        self.assertLess(text.index("Your queue"), text.index("For the assistant"))
        self.assertLess(text.index("## Open work, by priority"), text.index("## Where each card stands"))

    def test_status_is_read_in_bold_and_plain_form(self):
        self.assertEqual(tr.plan_status("# x\n\n**Status:** active (waiting)\n"), "active")
        self.assertEqual(tr.plan_status("# x\n\nStatus: Active, Oct 10\n"), "active")
        self.assertEqual(tr.plan_status("# x\n\n**Status:** done\n"), "done")
        self.assertEqual(tr.plan_status("# x\n\nno status here\n"), "")

    def test_tags_give_priority_and_owner(self):
        m = tr.TAG.match("**P1 you** T3 test the thing")
        self.assertEqual((m.group(1), m.group(2)), ("1", "you"))
        self.assertIsNone(tr.TAG.match("T3 test the thing"))
        self.assertEqual(tr.TAG.sub("", "**P3 ai** R2 later"), "R2 later")

    def test_focus_and_holding_preserve_backlog_without_flooding_queue(self):
        with tempfile.TemporaryDirectory(dir=tr.ROOT / "tmp") as directory:
            root = pathlib.Path(directory)
            plans = root / "docs" / "plans"
            plans.mkdir(parents=True)
            (plans / "2026-10-30-now.md").write_text(
                "# Now\n\n**Status:** active\n**Queue focus:** T1\n\n"
                "- [ ] **P1 ai** T1 Publish verified baseline\n"
                "- [ ] **P1 ai** T2 Later optimization\n", encoding="utf-8")
            (plans / "2026-10-30-later.md").write_text(
                "# Later\n\n**Status:** holding\n\n"
                "- [ ] **P1 you** L1 Future review\n", encoding="utf-8")
            with mock.patch.object(tr, "ROOT", root):
                text = "\n".join(tr.open_work())
            self.assertIn("T1 Publish verified baseline", text)
            self.assertNotIn("T2 Later optimization", text)
            self.assertNotIn("L1 Future review", text)
            self.assertIn("Scheduled backlog", text)
            self.assertIn("| active | 1 |", text)
            self.assertIn("| holding | 1 |", text)

    def test_invalid_or_stale_focus_fails_instead_of_silently_losing_tasks(self):
        with tempfile.TemporaryDirectory(dir=tr.ROOT / "tmp") as directory:
            root = pathlib.Path(directory)
            plans = root / "docs" / "plans"
            plans.mkdir(parents=True)
            for focus in ("T2", "T1, T1", "anything"):
                with self.subTest(focus=focus):
                    (plans / "2026-10-30-focus.md").write_text(
                        f"# Focus\n\n**Status:** active\n**Queue focus:** {focus}\n\n"
                        "- [ ] **P1 ai** T1 Existing task\n", encoding="utf-8")
                    with mock.patch.object(tr, "ROOT", root), self.assertRaises(ValueError):
                        tr.open_work()

    def test_active_plan_without_focus_keeps_all_tasks_and_other_states_stay_excluded(self):
        with tempfile.TemporaryDirectory(dir=tr.ROOT / "tmp") as directory:
            root = pathlib.Path(directory)
            plans = root / "docs" / "plans"
            plans.mkdir(parents=True)
            for status, task in (("active", "A1 Both owners"),
                                 ("proposed", "P1 Not agreed"),
                                 ("done", "D1 Already completed")):
                (plans / f"2026-10-30-{status}.md").write_text(
                    f"# {status}\n\n**Status:** {status}\n\n"
                    f"- [ ] **P2 either** {task}\n", encoding="utf-8")
            with mock.patch.object(tr, "ROOT", root):
                text = "\n".join(tr.open_work())
            self.assertIn("A1 Both owners", text)
            self.assertNotIn("P1 Not agreed", text)
            self.assertNotIn("D1 Already completed", text)

    def test_focus_order_keeps_prerequisite_before_followup_within_same_priority_owner(self):
        with tempfile.TemporaryDirectory(dir=tr.ROOT / "tmp") as directory:
            root = pathlib.Path(directory)
            plans = root / "docs" / "plans"
            plans.mkdir(parents=True)
            (plans / "2026-10-30-focus.md").write_text(
                "# Focus\n\n**Status:** active\n**Queue focus:** T2, T1\n\n"
                "- [ ] **P1 ai** T1 Next backup review\n"
                "- [ ] **P1 ai** T2 Current baseline\n", encoding="utf-8")
            with mock.patch.object(tr, "ROOT", root):
                text = "\n".join(tr.open_work())
            self.assertLess(text.index("T2 Current baseline"), text.index("T1 Next backup review"))

    def test_the_notes_section_is_kept_when_regenerated(self):
        with tempfile.TemporaryDirectory() as d:
            out = pathlib.Path(d) / "todo.md"
            with mock.patch.object(tr, "OUT", out):
                out.write_text(f"x\n{tr.NOTES_START}\nmy own note\n{tr.NOTES_END}\n", encoding="utf-8")
                self.assertIn("my own note", tr.build())

    def test_multiline_summaries_exclude_preserved_fenced_feedback(self):
        with tempfile.TemporaryDirectory(dir=tr.ROOT / "tmp") as directory:
            root = pathlib.Path(directory)
            plans = root / "docs" / "plans"
            plans.mkdir(parents=True)
            (plans / "2026-10-30-readable-plan.md").write_text(
                "# Readable\n\n**Status:** active\n\n"
                "- [ ] **P1 ai** T1 Verify the installed\n"
                "  gallery and exact face evidence.\n\n"
                "````text\n- [ ] **P1 ai** T2 Raw user example\n````\n",
                encoding="utf-8")
            with mock.patch.object(tr, "ROOT", root):
                text = "\n".join(tr.open_work())
            self.assertIn("T1 Verify the installed gallery and exact face evidence.", text)
            self.assertIn("[readable plan]", text)
            self.assertNotIn("T2 Raw user example", text)

    def test_supporting_inventories_are_collapsed_and_archive_status_is_honest(self):
        text = tr.build()
        self.assertEqual(text.count("<details>"), 3)
        self.assertEqual(text.count("</details>"), 3)
        self.assertIn("**dropped**:", text)
        self.assertIn("**done**:", text)
        self.assertNotIn("### Completed plans", text)

    def test_cells_use_final_candidate_or_nothing(self):
        stems = ["Remiah_Qwen_Alpha_1_Prime", "Remiah_FireRed_Alpha_1_Prime"]
        self.assertEqual(tr.state({"Remiah_Qwen_Alpha_1_Prime": 2}, {"Remiah_FireRed_Alpha_1_Prime": 3}, "Remiah", stems), "Q FINAL +1 · F c3")
        self.assertEqual(tr.state({}, {}, "Remiah", stems), "-")


if __name__ == "__main__":
    unittest.main()
