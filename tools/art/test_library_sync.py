#!/usr/bin/env python3
"""library_sync: the steps of each mode, and the quiet filter. Run: python tools/art/test_library_sync.py"""
import pathlib
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import library_sync as ls  # noqa: E402


def args(**kw):
    return types.SimpleNamespace(**{"dry_run": False, "check": False, "no_likeness": False, "retry_junk": False, "min": 0.45, **kw})


class LibrarySyncTests(unittest.TestCase):
    def titles(self, steps):
        return [t for t, *_ in steps]

    def test_a_run_applies_every_step_in_order_and_ends_with_the_check_sync_and_index(self):
        steps = ls.plan(args())
        flat = [" ".join(argv) for _t, argv, *_r in steps]
        self.assertTrue(flat[0].endswith("likeness.py --no-originals seed --apply"), "named folders move before originals renames them")
        self.assertTrue(flat[1].endswith("originals.py --apply"))
        self.assertIn("tools/art/likeness.py reconcile --apply", flat)
        self.assertFalse(any(" review " in step or " sort " in step or " singles " in step or " rematch " in step for step in flat))
        self.assertIn("tools/art/likeness.py retire-empty --apply", flat)
        self.assertIn("tools/art/duplicates.py --prefer-incoming --apply", flat)
        self.assertIn("tools/art/duplicates.py --apply", flat)
        i_apply = max(i for i, f in enumerate(flat) if f.endswith("originals.py --apply"))
        i_check = [i for i, f in enumerate(flat) if f.endswith("originals.py --check")]
        self.assertEqual(len(i_check), 1)
        self.assertGreater(i_check[0], i_apply, "the check comes after the last pass of originals")
        self.assertTrue(any("sync_inputs.py --apply" in f for f in flat))
        self.assertTrue(flat[-1].endswith("likeness.py index"))

    def test_a_preview_never_applies_and_skips_the_second_pass(self):
        flat = [" ".join(argv) for _t, argv, *_r in ls.plan(args(dry_run=True))]
        self.assertFalse(any("--apply" in f for f in flat), flat)
        self.assertTrue(any("likeness.py retire-empty" in f for f in flat))
        self.assertTrue(flat[0].endswith("likeness.py --no-originals seed"))
        self.assertTrue(flat[1].endswith("originals.py --dry-run"))
        self.assertFalse(any("sync_inputs" in f or "index" in f for f in flat))

    def test_no_likeness_leaves_the_sorting_out(self):
        flat = [" ".join(argv) for _t, argv, *_r in ls.plan(args(no_likeness=True))]
        self.assertFalse(any("likeness.py" in f or "likeness_artists.py" in f for f in flat))
        self.assertTrue(any("duplicates.py" in f for f in flat) and any("originals.py --check" in f for f in flat))

    def test_legacy_threshold_override_is_explicitly_rejected(self):
        with self.assertRaises(SystemExit):
            ls.main(["--min", "0.4"])

    def test_sorting_is_required_and_the_loose_ends_are_not(self):
        req = {t: r for t, _a, r, _i in ls.plan(args())}
        duplicate_step = next(t for t in req if t.startswith("2 duplicates"))
        self.assertTrue(req["0 likeness seed (Various\\<Name> folders of one known person)"])
        self.assertTrue(req["1 originals: names, scaled copies and headshots"] and req["4 unified likeness reconciliation"])
        self.assertFalse(req[duplicate_step] or req["9 likeness index"])

    def test_the_check_only_reads(self):
        flat = [" ".join(argv) for _t, argv, *_r in ls.check_plan()]
        self.assertFalse(any("--apply" in f for f in flat), flat)
        self.assertIn("tools/art/likeness.py seed", flat)

    def test_junk_is_not_automatically_reconsidered_by_ordinary_runs(self):
        for mode in (args(), args(dry_run=True)):
            flat = [" ".join(argv) for _t, argv, *_r in ls.plan(mode)]
            self.assertFalse(any("junk --recheck" in f or "junk --reset" in f for f in flat))
            self.assertTrue(any("likeness.py junk" in f for f in flat), "retain active-photo safety check")
        flat = [" ".join(argv) for _t, argv, *_r in ls.plan(args(retry_junk=True))]
        self.assertTrue(any("junk --reset" in f for f in flat), "retry remains explicitly requested")

    def test_artist_steps_use_separate_entry_and_both_domains_keep_shared_housekeeping(self):
        for dry_run in (False, True):
            flat = [" ".join(argv) for _t, argv, *_r in ls.plan(args(dry_run=dry_run))]
            self.assertFalse(any("likeness.py group" in row for row in flat))
            for command in ("crop", "junk", "group"):
                self.assertTrue(any(f"likeness_artists.py {command}" in row for row in flat), command)
            self.assertTrue(any("likeness.py reconcile" in row for row in flat))
            self.assertTrue(any("originals.py" in row for row in flat))
        retry = [" ".join(argv) for _t, argv, *_r in ls.plan(args(retry_junk=True))]
        self.assertTrue(any("likeness.py junk --reset" in row for row in retry))
        self.assertTrue(any("likeness_artists.py junk --reset" in row for row in retry))
        apply = [" ".join(argv) for _t, argv, *_r in ls.plan(args())]
        self.assertIn("tools/art/artists_gallery.py --apply", apply)
        self.assertFalse(any("--artists" in row for row in apply))

    def test_real_run_snapshots_before_first_mutating_step(self):
        work = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, work, True)
        cfg = {"paths": {"inputsRoot": str(work / "inputs")}}
        snapshot = ({"pool": 0, "galleries": 0, "review": 0}, {}, set())
        events = []

        def backup(*_args, **_kwargs):
            events.append("backup")
            return work / "_backup" / "snapshot"

        def step(*_args, **_kwargs):
            events.append("step")
            return 0, []

        with mock.patch.object(ls.cw, "load_cfg", return_value=cfg), \
                mock.patch.object(ls.cw, "work_root", return_value=work), \
                mock.patch.object(ls, "snapshot", return_value=snapshot), \
                mock.patch.object(ls, "load_policy", return_value={"status": "approved"}), \
                mock.patch.object(ls.library_backup, "create_backup", side_effect=backup), \
                mock.patch.object(ls, "run_step", side_effect=step):
            self.assertEqual(ls.main([]), 0)
        self.assertEqual(events[0], "backup")
        self.assertIn("step", events[1:])

    def test_failed_backup_stops_before_any_library_step(self):
        work = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, work, True)
        with mock.patch.object(ls.cw, "load_cfg", return_value={"paths": {}}), \
                mock.patch.object(ls.cw, "work_root", return_value=work), \
                mock.patch.object(ls, "load_policy", return_value={"status": "approved"}), \
                mock.patch.object(ls.library_backup, "create_backup", side_effect=OSError("disk full")), \
                mock.patch.object(ls, "run_step") as run_step:
            self.assertEqual(ls.main([]), 1)
        run_step.assert_not_called()

    def test_draft_policy_stops_before_backup_and_housekeeping(self):
        with tempfile.TemporaryDirectory() as directory:
            work = pathlib.Path(directory)
            with mock.patch.object(ls.cw, "load_cfg", return_value={"paths": {}}), \
                    mock.patch.object(ls.cw, "work_root", return_value=work), \
                    mock.patch.object(ls, "load_policy", return_value={"status": "draft"}), \
                    mock.patch.object(ls.library_backup, "create_backup") as backup, \
                    mock.patch.object(ls, "run_step") as step:
                self.assertEqual(ls.main([]), 1)
            backup.assert_not_called()
            step.assert_not_called()
            self.assertFalse((work / "_reports").exists())

    def test_lines_that_say_nothing_to_do_are_left_off_the_screen(self):
        for line in ("-" * 40, "  0 to make, 0 to prune", "  headshots: 0 to make, 2 skipped (no usable face), 0 to prune", "  NO PHOTO Metrael: placeholder"):
            self.assertTrue(ls.BORING.match(line), line)
        for line in ("  convert a.jpg -> a_944x1104.png", "  1 to make, 0 to prune", "OUT OF SYNC: 1 renamed", "  PRUNED x.png"):
            self.assertFalse(ls.BORING.match(line), line)


if __name__ == "__main__":
    unittest.main()
