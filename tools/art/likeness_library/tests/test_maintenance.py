"""Shared proposal execution must protect sources and remain reversible."""
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from tools.art.likeness_library import maintenance, metadata
from tools.art.likeness_library.policy import load_policy


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        self.policy = load_policy()
        self.policy["status"] = "approved"
        metadata.save_catalog(
            {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
            self.root / ".likeness-library.json",
        )

    def move(self, number=123456):
        relative = f"Various/gallery/person_image_{number}.jpg"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"photo {number}".encode())
        return {
            "photoId": f"photo:image_{number}", "source": relative,
            "destination": f"Potentials/New/gallery/{path.name}",
            "sha256": metadata.content_sha256(path), "reason": "qualified test proposal",
        }

    def test_apply_and_undo_restore_exact_bytes(self):
        row = self.move()
        backup = mock.Mock(return_value=self.root / "verified-backup")
        journal = maintenance.apply_moves(self.root, [row], self.policy, {}, backup_fn=backup)
        self.assertEqual(backup.call_count, 1)
        self.assertFalse((self.root / row["source"]).exists())
        self.assertEqual(metadata.content_sha256(self.root / row["destination"]), row["sha256"])
        self.assertEqual(json.loads(journal.read_text())["status"], "applied")
        maintenance.undo_moves(self.root, journal, {}, apply=False)
        self.assertTrue((self.root / row["destination"]).exists())
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=backup)
        self.assertEqual(metadata.content_sha256(self.root / row["source"]), row["sha256"])
        self.assertEqual(json.loads(journal.read_text())["status"], "undone")

    def test_journal_uses_configured_reports_root(self):
        row = self.move()
        cfg = {"storageRoots": {"reports": "operations/reports"}}

        journal = maintenance.apply_moves(
            self.root, [row], self.policy, cfg, backup_fn=lambda *_: "verified",
        )

        self.assertEqual(
            journal.parent.parent,
            self.root / "operations" / "reports",
        )
        maintenance.undo_moves(self.root, journal, cfg, apply=True, backup_fn=lambda *_: "verified")
        self.assertTrue((self.root / row["source"]).is_file())

    def test_draft_gate_precedes_backup_or_writes(self):
        row = self.move()
        self.policy["status"] = "draft"
        backup = mock.Mock()
        with self.assertRaisesRegex(ValueError, "approved policy"):
            maintenance.apply_moves(self.root, [row], self.policy, {}, backup_fn=backup)
        with self.assertRaisesRegex(ValueError, "restricted to sandbox"):
            maintenance.apply_moves(
                self.root, [row], self.policy, {}, sandbox_override=True, backup_fn=backup,
            )
        backup.assert_not_called()
        self.assertFalse((self.root / "_reports").exists())

    def test_failed_move_rolls_back_completed_moves(self):
        rows = [self.move(), self.move(654321)]
        original = pathlib.Path.rename

        def rename(path, destination):
            if path == self.root / rows[1]["source"]:
                raise OSError("simulated disk failure")
            return original(path, destination)

        with mock.patch.object(pathlib.Path, "rename", rename):
            with self.assertRaisesRegex(OSError, "simulated disk failure"):
                maintenance.apply_moves(
                    self.root, rows, self.policy, {}, backup_fn=lambda *_: "verified",
                )
        for row in rows:
            self.assertEqual(metadata.content_sha256(self.root / row["source"]), row["sha256"])
            self.assertFalse((self.root / row["destination"]).exists())
        journal = next((self.root / "_reports" / "runs").glob("reconcile_*.json"))
        self.assertEqual(json.loads(journal.read_text())["status"], "rolled-back")

    def test_cast_gallery_admission_is_blocked_but_review_is_allowed(self):
        row = self.move()
        row["destination"] = row["destination"].replace("Potentials/New/gallery", "Angels/A/review")
        journal = maintenance.apply_moves(
            self.root, [row], self.policy, {}, backup_fn=lambda *_: "verified",
        )
        self.assertIsNotNone(journal)
        other = self.move(654321)
        other["destination"] = other["destination"].replace("Potentials/New", "Angels/A")
        with self.assertRaisesRegex(ValueError, "protected Gallery"):
            maintenance.apply_moves(
                self.root, [other], self.policy, {}, backup_fn=lambda *_: "verified",
            )
        self.assertTrue((self.root / other["source"]).is_file())

    def test_changed_source_and_collision_stop_before_backup(self):
        row = self.move()
        backup = mock.Mock()
        (self.root / row["source"]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "source changed"):
            maintenance.apply_moves(self.root, [row], self.policy, {}, backup_fn=backup)
        backup.assert_not_called()

    def test_ambiguous_existing_review_stays_with_its_identity(self):
        path = self.root / "Angels" / "Angelica" / "review" / "fia_image_123456.jpg"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"held expression")
        report = {
            "assignments": [],
            "held": [{
                "photoId": "photo:image_123456", "sourceFolder": "Angels/Angelica",
                "sourceBucket": "Review", "clusterId": "expression-group",
                "reviewDestination": None, "reason": "existing identity match needs review",
            }],
        }
        moves = maintenance.proposed_moves(
            report, [SimpleNamespace(path=path, name=path.name)], self.root,
        )
        self.assertEqual(moves, [])
        self.assertEqual(path.read_bytes(), b"held expression")

    def test_undo_rechecks_catalogue_after_backup(self):
        row = self.move()
        journal = maintenance.apply_moves(
            self.root, [row], self.policy, {}, backup_fn=lambda *_: "verified",
        )
        catalog_path = self.root / ".likeness-library.json"

        def concurrent_edit(*_):
            catalog = metadata.load_catalog(catalog_path)
            next(iter(catalog["people"].values()))["protected"] = True
            metadata.save_catalog(catalog, catalog_path)
            return "verified"

        with self.assertRaisesRegex(ValueError, "catalogue changed after backup"):
            maintenance.undo_moves(
                self.root, journal, {}, apply=True, backup_fn=concurrent_edit,
            )
        self.assertTrue((self.root / row["destination"]).is_file())
        self.assertFalse((self.root / row["source"]).exists())
        self.assertTrue(next(iter(metadata.load_catalog(catalog_path)["people"].values()))["protected"])
        self.assertEqual(json.loads(journal.read_text())["status"], "applied")

    def test_rollback_attempts_remaining_files_and_catalogue_after_failure(self):
        first = (self.root / "first", self.root / "moved-first")
        second = (self.root / "second", self.root / "moved-second")
        first[1].write_bytes(b"first")
        second[1].write_bytes(b"second")
        original = pathlib.Path.rename

        def rename(path, destination):
            if path == second[1]:
                raise OSError("rollback disk failure")
            return original(path, destination)

        catalog = metadata.load_catalog(self.root / ".likeness-library.json")
        with mock.patch.object(pathlib.Path, "rename", rename), \
                mock.patch.object(metadata, "save_catalog") as save:
            errors = maintenance._rollback(
                [first, second], catalog, self.root / ".likeness-library.json",
            )
        self.assertEqual(len(errors), 1)
        self.assertIn("rollback disk failure", errors[0])
        self.assertEqual(first[0].read_bytes(), b"first")
        self.assertEqual(second[1].read_bytes(), b"second")
        save.assert_called_once_with(catalog, self.root / ".likeness-library.json")


if __name__ == "__main__":
    unittest.main()
