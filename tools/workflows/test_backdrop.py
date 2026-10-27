"""Tests for backdrop.py: exact phrase swaps, untouched non-backdrop creams, backups, preview and check."""
import contextlib
import io
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import backdrop  # noqa: E402

SHOT = ('{"nodes": [{"widgets_values": ["Background: a basic cream-coloured studio backdrop with even, soft, neutral '
        'frontal studio lighting.\\nKeep the pose, the cream studio background and the lighting."]}], "seed": 1234}')


class RewriteTest(unittest.TestCase):
    def test_backdrop_phrases_become_grey(self):
        text, counts = backdrop.rewrite(SHOT)
        self.assertNotIn("cream", text)
        self.assertIn("a plain neutral light-grey seamless studio backdrop with even, soft", text)
        self.assertIn("the light-grey studio background", text)
        self.assertEqual(sum(counts.values()), 2)

    def test_matches_generated_grey_piece(self):
        old = "a basic cream-coloured studio backdrop with even, soft, neutral frontal studio lighting - a flat, clean key light"
        grey = (backdrop.ROOT / "data/art/backgrounds/studio/grey-even.json").read_text(encoding="utf-8")
        self.assertIn(backdrop.rewrite(old)[0], grey)

    def test_other_creams_untouched(self):
        for text in ("soft cream wings", "a soft cream blush", "peaches-and-cream complexion",
                     "studio backdrop, cream backdrop, grey backdrop", "cream marble"):
            self.assertEqual(backdrop.rewrite(text), (text, {}))


class CommandTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = pathlib.Path(self.tmp.name)
        self.root = base / "ws"
        (self.root / "zz_Shots" / "Hero").mkdir(parents=True)
        (self.root / "_archive").mkdir()
        self.shot = self.root / "zz_Shots" / "Hero" / "shot.json"
        self.shot.write_bytes(SHOT.encode("utf-8"))
        self.archived = self.root / "_archive" / "old.json"
        self.archived.write_bytes(SHOT.encode("utf-8"))
        self.plain = self.root / "plain.txt"
        self.plain.write_text("cream wings only", encoding="utf-8")
        self.backups = base / "backup"
        patcher = mock.patch.object(backdrop, "BACKUPS", self.backups)
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = backdrop.main(["--root", str(self.root), *args])
        return code, out.getvalue()

    def test_dry_run_writes_nothing(self):
        code, out = self.run_main("--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("1 file(s) would change", out)
        self.assertEqual(self.shot.read_text(encoding="utf-8"), SHOT)
        self.assertFalse(self.backups.exists())

    def test_check_fails_then_passes_after_apply(self):
        self.assertEqual(self.run_main("--check")[0], 1)
        code, out = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("1 rewritten", out)
        after = self.shot.read_text(encoding="utf-8")
        self.assertNotIn("cream", after)
        self.assertIn('"seed": 1234', after)
        self.assertEqual(self.archived.read_text(encoding="utf-8"), SHOT, "_archive is left alone")
        self.assertEqual(self.plain.read_text(encoding="utf-8"), "cream wings only")
        saved = list(self.backups.rglob("shot.json"))
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].read_text(encoding="utf-8"), SHOT)
        self.assertEqual(self.run_main("--check")[0], 0)
        self.assertIn("0 file(s) with old backdrop wording", self.run_main()[1], "repeats safely")

    def test_changed_after_scan_is_skipped(self):
        changes = backdrop.scan("ws", self.root)
        self.shot.write_text(SHOT + " ", encoding="utf-8")
        written, skipped = backdrop.apply(changes, "stamp")
        self.assertEqual((written, skipped), (0, 1))
        self.assertIn("cream", self.shot.read_text(encoding="utf-8"))

    def test_needs_a_target(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            backdrop.main(["--check"])

    def test_locked_target_is_retried_then_cleaned_up(self):
        changes = backdrop.scan("ws", self.root)
        real = backdrop.os.replace
        calls = []

        def flaky(source, target):
            calls.append(1)
            if len(calls) < 3:
                raise PermissionError("held by a scanner")
            real(source, target)

        with mock.patch.object(backdrop.os, "replace", flaky), mock.patch.object(backdrop.time, "sleep"):
            self.assertEqual(backdrop.apply(changes, "stamp"), (1, 0))
        self.assertNotIn("cream", self.shot.read_text(encoding="utf-8"))
        self.shot.write_bytes(SHOT.encode("utf-8"))
        changes = backdrop.scan("ws", self.root)
        with mock.patch.object(backdrop.os, "replace", side_effect=PermissionError("locked")), \
                mock.patch.object(backdrop.time, "sleep"), self.assertRaises(PermissionError):
            backdrop.apply(changes, "stamp2")
        self.assertEqual(list(self.root.rglob("*.backdrop-pending")), [])
        self.assertEqual(self.shot.read_text(encoding="utf-8"), SHOT)


if __name__ == "__main__":
    unittest.main()
