#!/usr/bin/env python3
"""Smoke tests for todo_report.py: the tables list every top-tier card, the open work comes from the active plans, and the notes section survives a regeneration.
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

    def test_open_work_comes_from_the_active_plans(self):
        text = tr.build()
        self.assertIn("## Open work from the active plans", text)
        self.assertIn("- [ ]", text)

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
