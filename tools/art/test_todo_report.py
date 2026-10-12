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

    def test_the_notes_section_is_kept_when_regenerated(self):
        with tempfile.TemporaryDirectory() as d:
            out = pathlib.Path(d) / "todo.md"
            with mock.patch.object(tr, "OUT", out):
                out.write_text(f"x\n{tr.NOTES_START}\nmy own note\n{tr.NOTES_END}\n", encoding="utf-8")
                self.assertIn("my own note", tr.build())

    def test_cells_use_final_candidate_or_nothing(self):
        stems = ["Remiah_Qwen_Alpha_1_Prime", "Remiah_FireRed_Alpha_1_Prime"]
        self.assertEqual(tr.state({"Remiah_Qwen_Alpha_1_Prime": 2}, {"Remiah_FireRed_Alpha_1_Prime": 3}, "Remiah", stems), "Q FINAL +1 · F c3")
        self.assertEqual(tr.state({}, {}, "Remiah", stems), "-")


if __name__ == "__main__":
    unittest.main()
