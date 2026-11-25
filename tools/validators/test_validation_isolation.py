"""Isolation ownership, cleanup and reusable Alpha component contracts."""
import copy
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from jsonschema import Draft7Validator

from tools.validators import test_validate_data as mutation


class IsolationTests(unittest.TestCase):
    def test_generic_cards_require_their_own_prompt_group(self):
        validator = mutation.vd
        root = pathlib.Path(__file__).resolve().parents[2]
        original_load = validator.load

        def validate(card_path, card, output):
            changed = copy.deepcopy(card)
            changed["output"] = output
            report = validator.Report()
            with mock.patch.object(validator, "rglob", return_value=[card_path]), \
                    mock.patch.object(validator, "load", side_effect=lambda path: changed if path == card_path else original_load(path)):
                validator.check_art_cards(report)
            return report.errors

        for group, slug, phase in (
            ("sovereign-females", "female", "0_Edit/background/female-edit-background-basic.json"),
            ("sovereign-males", "male", "1_Alpha/1_Prime/male-alpha-prime.json"),
        ):
            card_path = root / "data/art/_sets" / group / slug / phase
            card = json.loads(card_path.read_text(encoding="utf-8"))
            output = card["output"]
            with self.subTest(group=group):
                self.assertEqual(validate(card_path, card, output), [])
                self.assertTrue(validate(card_path, card, output.replace(f"prompts/{group}/", "prompts/angel-primes/alpha/")))
                self.assertTrue(validate(card_path, card, output.replace(f"prompts/{group}/", "prompts/drakn-sisters/")))

    def test_isolated_copy_has_private_journal_and_never_mutates_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = pathlib.Path(directory)
            for name in ("data", "tools"):
                (source / name).mkdir()
            original = source / "data" / "piece.json"
            original.write_text('{"value": "original"}', encoding="utf-8")
            calls = []

            def child(command, *, cwd, env, check):
                root = pathlib.Path(cwd)
                self.assertNotEqual(root, source)
                self.assertEqual(command[-1], "--quick")
                self.assertFalse(check)
                journal = mutation.journal_path(root, env)
                self.assertTrue(journal.is_relative_to(root))
                (root / "data" / "piece.json").write_text("mutated copy", encoding="utf-8")
                self.assertEqual(original.read_text(encoding="utf-8"), '{"value": "original"}')
                calls.append(root)
                return mock.Mock(returncode=7)

            with mock.patch.object(mutation, "REAL_ROOT", source), \
                    mock.patch.dict(mutation.os.environ, {}, clear=True), \
                    mock.patch.object(mutation.subprocess, "run", side_effect=child):
                self.assertEqual(mutation.isolated_run(quick=True), 7)
            self.assertEqual(len(calls), 1)
            self.assertFalse(calls[0].exists())
            self.assertEqual(original.read_text(encoding="utf-8"), '{"value": "original"}')

    def test_worker_refuses_mismatched_or_unowned_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory).resolve()
            environment = {mutation.ISOLATED_ROOT_ENV: str(root)}
            with self.assertRaisesRegex(ValueError, "ownership marker"):
                mutation.journal_path(root, environment)
            (root / ".isolated-validator").write_text(str(root), encoding="utf-8")
            self.assertTrue(mutation.journal_path(root, environment).is_relative_to(root))
            with self.assertRaisesRegex(ValueError, "mismatch"):
                mutation.journal_path(root, {mutation.ISOLATED_ROOT_ENV: str(root / "other")})

    def test_alpha_is_a_declared_piece_stage_but_unknown_stages_still_fail(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        schema = json.loads((root / "data/art/_schema/art-piece.schema.json").read_text(encoding="utf-8"))
        validator = Draft7Validator(schema)
        piece = {"id": "test-stage", "kind": "view", "name": "Test",
                 "compatibleStages": ["alpha"], "description": "Test view"}
        self.assertEqual(list(validator.iter_errors(piece)), [])
        piece["compatibleStages"] = ["unknown-stage"]
        self.assertTrue(list(validator.iter_errors(piece)))

    def test_shared_piece_kinds_require_description(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        schema = json.loads((root / "data/art/_schema/art-piece.schema.json").read_text(encoding="utf-8"))
        validator = Draft7Validator(schema)
        for kind in ("reference", "lighting", "photography", "figure"):
            with self.subTest(kind=kind):
                piece = {"id": "test-piece", "kind": kind, "name": "Test",
                         "compatibleStages": ["alpha"], "description": "Test instruction"}
                self.assertEqual(list(validator.iter_errors(piece)), [])
                del piece["description"]
                self.assertTrue(list(validator.iter_errors(piece)))


if __name__ == "__main__":
    unittest.main()
