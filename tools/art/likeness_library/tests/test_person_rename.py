"""Staged identity rename is stable, isolated, and exactly recoverable."""
import copy
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art.likeness_library import actions, metadata, person_rename, review_gallery


class PersonRenameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.folder = self.root / "Prospects" / "Old Name"
        (self.folder / "gallery").mkdir(parents=True)
        (self.folder / "review").mkdir()
        (self.folder / "head").mkdir()
        (self.folder / "empty").mkdir()
        self.photo = self.folder / "gallery" / "old_image_123456.jpg"
        self.photo.write_bytes(b"unchanged original")
        (self.folder / "review" / "old_image_654321.jpg").write_bytes(b"review")
        (self.folder / "head" / "derived.jpg").write_bytes(b"derived")
        self.history = self.folder / "gallery" / "z_old_name.txt"
        self.history.write_bytes(b"name: Old Name\r\nroles: hero\r\n2026-10-10 arrived\r\n")
        self.person_id = "person_" + "a" * 32
        self.catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {self.person_id: {
                "id": self.person_id, "folder": "Prospects/Old Name", "displayName": "Old Name",
                "folderHistory": [], "identityAnchors": [], "protected": True,
            }},
            "photos": {"photo:image_123456": {
                "contentSha256": metadata.content_sha256(self.photo), "protected": True,
                "rejectedPersonIds": [self.person_id],
            }},
        }
        self.original = copy.deepcopy(self.catalog)
        self.original_tree = person_rename.tree_hash(self.folder)
        decision, reason = person_rename.decision(
            self.root, "Prospects/Old Name", self.person_id, self.catalog["people"][self.person_id], {},
        )
        self.assertEqual(reason, "")
        self.document = {
            "manifestVersion": 1, "generatedAt": "2026-10-22T14:00:00Z",
            "source": "people-gallery-review", "actions": [{**decision, "newName": "New Name"}],
        }
        self.destination = self.root / "Prospects" / "New Name"

    def save(self, updated):
        self.catalog.clear()
        self.catalog.update(copy.deepcopy(updated))

    def apply(self, **kwargs):
        return actions.apply_actions(
            self.document, self.root, self.catalog, {}, "Various",
            backup_fn=kwargs.get("backup_fn", lambda *_: "verified"),
            save_fn=kwargs.get("save_fn", self.save),
        )

    def undo(self, **kwargs):
        return actions.undo_actions(
            self.catalog, self.root, {}, "Various",
            backup_fn=kwargs.get("backup_fn", lambda *_: "verified"),
            save_fn=kwargs.get("save_fn", self.save),
        )

    def test_saved_json_apply_and_undo_preserve_ids_bytes_history_and_empty_directories(self):
        path = self.root / "actions.json"
        path.write_text(json.dumps(self.document), encoding="utf-8")
        document = actions.load_manifest(path)
        errors, plans = actions.validate_manifest(document, self.root, self.catalog, "Various", cfg={})
        self.assertEqual(errors, [])
        self.assertEqual(plans[0]["destination"], self.destination)
        self.assertEqual(self.catalog, self.original)
        self.apply()
        self.assertFalse(self.folder.exists())
        self.assertTrue((self.destination / "empty").is_dir())
        self.assertEqual((self.destination / "gallery" / self.photo.name).read_bytes(), b"unchanged original")
        history = (self.destination / "gallery" / "z_new_name.txt").read_bytes()
        self.assertIn(b"roles: hero\r\n2026-10-10 arrived\r\n", history)
        self.assertIn(b"renamed from Old Name (Prospects/Old Name)", history)
        person = self.catalog["people"][self.person_id]
        self.assertEqual(person["folder"], "Prospects/New Name")
        self.assertEqual(person["folderHistory"], ["Prospects/Old Name"])
        self.assertTrue(person["protected"])
        self.assertEqual(self.catalog["photos"], self.original["photos"])
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        self.undo()
        self.assertEqual(person_rename.tree_hash(self.folder), self.original_tree)
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.catalog["people"], self.original["people"])
        self.assertEqual(self.catalog["photos"], self.original["photos"])

    def test_protected_cast_person_name_changes_without_renaming_slot_or_workflow_files(self):
        for category in ("Sisters", "Angels"):
            with self.subTest(category=category):
                cast = self.root / category / "Drakinsa"
                cast.parent.mkdir(exist_ok=True)
                self.folder.rename(cast)
                person = self.catalog["people"][self.person_id]
                person.update(folder=f"{category}/Drakinsa", displayName="Drakinsa")
                history = cast / "gallery" / "z_old_name.txt"
                history.write_bytes(b"name: Sweet Beauty\r\n2026-10-10 old history\r\n")
                before_hash = person_rename.tree_hash(cast)
                original = copy.deepcopy(self.catalog)
                cfg = {
                    "photos": {"Drakinsa": self.photo.name},
                    "likeness": {"different": [[f"{category}/Drakinsa", "Angels/Other"]]},
                }
                decision, reason = person_rename.decision(
                    self.root, f"{category}/Drakinsa", self.person_id, person, cfg,
                )
                self.assertEqual(reason, "")
                self.assertEqual(decision["expectedRecordedName"], "Sweet Beauty")
                self.document["actions"] = [{**decision, "newName": "Amelia Morgan"}]
                errors, plans = actions.validate_manifest(self.document, self.root, self.catalog, cfg=cfg)
                self.assertEqual(errors, [])
                self.assertEqual(plans[0]["source"], plans[0]["destination"])
                actions.apply_actions(
                    self.document, self.root, self.catalog, cfg, "Various",
                    backup_fn=lambda *_: "verified", save_fn=self.save,
                )
                self.assertTrue(cast.is_dir())
                self.assertEqual(self.catalog["people"][self.person_id]["folder"], f"{category}/Drakinsa")
                self.assertEqual(self.catalog["people"][self.person_id]["displayName"], "Drakinsa")
                self.assertTrue(self.catalog["people"][self.person_id]["protected"])
                self.assertEqual(self.catalog["people"][self.person_id]["folderHistory"], [])
                self.assertEqual(self.catalog["photos"], original["photos"])
                self.assertEqual(cfg["photos"]["Drakinsa"], self.photo.name)
                self.assertTrue((cast / "gallery" / "z_amelia_morgan.txt").is_file())
                actions.undo_actions(
                    self.catalog, self.root, cfg, "Various",
                    backup_fn=lambda *_: "verified", save_fn=self.save,
                )
                self.assertEqual(person_rename.tree_hash(cast), before_hash)
                self.assertEqual(self.catalog["people"], original["people"])
                cast.rename(self.folder)
                self.catalog = copy.deepcopy(self.original)

    def test_cast_recorded_name_staleness_noop_and_recorded_name_collision_refused(self):
        cast = self.root / "Sisters" / "Draknisa"
        cast.parent.mkdir()
        self.folder.rename(cast)
        person = self.catalog["people"][self.person_id]
        person.update(folder="Sisters/Draknisa", displayName="Draknisa")
        history = cast / "gallery" / self.history.name
        history.write_text("name: Sweet Beauty\n", encoding="utf-8")
        decision, reason = person_rename.decision(
            self.root, person["folder"], self.person_id, person, {},
        )
        self.assertEqual(reason, "")
        self.document["actions"] = [{**decision, "newName": "sweet beauty"}]
        errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("case-only", "\n".join(errors))
        self.document["actions"][0]["newName"] = "Amelia Morgan"
        other = self.root / "Angels" / "Other Slot" / "gallery"
        other.mkdir(parents=True)
        (other / "z_amelia_morgan.txt").write_text("name: Amelia Morgan\n", encoding="utf-8")
        errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("collides", "\n".join(errors))
        (other / "z_amelia_morgan.txt").unlink()
        history.write_text("name: Corrected elsewhere\n", encoding="utf-8")
        errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("recorded person name is stale", "\n".join(errors))
        self.assertEqual(self.catalog["actions"], [])
        self.assertTrue(cast.is_dir())

    def test_cast_history_save_failure_rolls_back_in_place(self):
        cast = self.root / "Sisters" / "Drakinsa"
        cast.parent.mkdir()
        self.folder.rename(cast)
        person = self.catalog["people"][self.person_id]
        person["folder"] = "Sisters/Drakinsa"
        decision, _ = person_rename.decision(self.root, person["folder"], self.person_id, person, {})
        self.document["actions"] = [{**decision, "newName": "Amelia Morgan"}]
        digest = person_rename.tree_hash(cast)
        with self.assertRaisesRegex(OSError, "cannot save"):
            self.apply(save_fn=mock.Mock(side_effect=OSError("cannot save")))
        self.assertEqual(person_rename.tree_hash(cast), digest)
        self.assertEqual(self.catalog["people"][self.person_id]["displayName"], "Old Name")

    def test_invalid_names_cast_stale_name_and_collisions_are_refused(self):
        for name in ("", "../escape", "CON", "nul.txt", "LPT1", "trailing.", " leading", "bad:name", "Old Name"):
            with self.subTest(name=name):
                self.document["actions"][0]["newName"] = name
                errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
                self.assertTrue(errors)
        self.document["actions"][0]["newName"] = "New Name"
        self.destination.mkdir()
        errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("collides", "\n".join(errors))
        self.destination.rmdir()
        self.document["actions"][0]["expectedDisplayName"] = "Stale"
        self.assertIn("stale", "\n".join(actions.validate_manifest(
            self.document, self.root, self.catalog, cfg={},
        )[0]))
        self.document["actions"][0]["personFolder"] = "Angels/Old Name"
        self.assertTrue(actions.validate_manifest(self.document, self.root, self.catalog, cfg={})[0])

    def test_changed_inventory_and_backup_race_refuse_before_moves(self):
        self.photo.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "files changed"):
            self.apply()
        self.photo.write_bytes(b"unchanged original")

        def backup(*_):
            self.photo.write_bytes(b"changed during backup")
            return "verified"

        with self.assertRaisesRegex(ValueError, "changed after backup"):
            self.apply(backup_fn=backup)
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.catalog, self.original)

    def test_save_failure_rolls_back_exact_original_files(self):
        with self.assertRaisesRegex(OSError, "cannot save"):
            self.apply(save_fn=mock.Mock(side_effect=OSError("cannot save")))
        self.assertEqual(person_rename.tree_hash(self.folder), self.original_tree)
        self.assertEqual(self.catalog, self.original)

    def test_undo_save_failure_restores_renamed_state_and_stale_undo_refuses(self):
        self.apply()
        renamed_hash = person_rename.tree_hash(self.destination)
        with self.assertRaisesRegex(OSError, "cannot save"):
            self.undo(save_fn=mock.Mock(side_effect=OSError("cannot save")))
        self.assertEqual(person_rename.tree_hash(self.destination), renamed_hash)
        (self.destination / "head" / "derived.jpg").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "files changed"):
            self.undo()

    def test_workflow_references_and_mixed_batches_refused(self):
        for cfg in (
            {"photos": {"Hero": self.photo.name}},
            {"likeness": {"different": [["Prospects/Old Name", "Angels/Other"]]}},
        ):
            errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg=cfg)
            self.assertTrue(errors)
        self.document["actions"].append({
            "type": "person-unprotected", "personId": self.person_id,
            "personFolder": "Prospects/Old Name", "expectedProtected": True,
        })
        self.assertIn("alone", "\n".join(actions.validate_manifest(
            self.document, self.root, self.catalog, cfg={},
        )[0]))

    def test_missing_history_created_and_undo_removes_it(self):
        self.history.unlink()
        self.document["actions"][0]["expectedTreeSha256"] = person_rename.tree_hash(self.folder)
        self.apply()
        self.assertTrue((self.destination / "gallery" / "z_new_name.txt").is_file())
        self.undo()
        self.assertFalse(self.history.exists())
        self.assertEqual(list((self.folder / "gallery").glob("z_*.txt")), [])

    def test_multiple_history_files_and_case_insensitive_catalogue_collision_refused(self):
        extra = self.folder / "z_extra.txt"
        extra.write_bytes(b"name: Extra\n")
        self.document["actions"][0]["expectedTreeSha256"] = person_rename.tree_hash(self.folder)
        self.assertIn("multiple", "\n".join(actions.validate_manifest(
            self.document, self.root, self.catalog, cfg={},
        )[0]))
        extra.unlink()
        self.document["actions"][0]["expectedTreeSha256"] = person_rename.tree_hash(self.folder)
        key = "person_" + "b" * 32
        self.catalog["people"][key] = {
            "id": key, "folder": "Potentials/new name", "displayName": "Other",
            "folderHistory": [], "identityAnchors": [],
        }
        self.assertIn("collides", "\n".join(actions.validate_manifest(
            self.document, self.root, self.catalog, cfg={},
        )[0]))

    def test_empty_directory_changes_and_target_appearing_during_backup_are_stale(self):
        (self.folder / "empty").rmdir()
        with self.assertRaisesRegex(ValueError, "files changed"):
            self.apply()
        (self.folder / "empty").mkdir()

        def backup(*_):
            self.destination.mkdir()
            return "verified"

        with self.assertRaisesRegex(ValueError, "changed after backup"):
            self.apply(backup_fn=backup)
        self.assertEqual(person_rename.tree_hash(self.folder), self.original_tree)

    def test_history_write_failure_rolls_back_before_catalogue_save(self):
        with mock.patch.object(actions.person_rename, "_write_history", side_effect=[OSError("write failed"), None]):
            with self.assertRaisesRegex(OSError, "write failed"):
                self.apply()
        self.assertTrue(self.folder.is_dir())
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.catalog, self.original)

    def test_undo_refuses_destination_and_workflow_changes_during_backup(self):
        self.apply()

        def backup(*_):
            self.folder.mkdir()
            return "verified"

        with self.assertRaisesRegex(ValueError, "changed after backup"):
            self.undo(backup_fn=backup)
        self.assertTrue(self.destination.is_dir())
        self.folder.rmdir()
        with self.assertRaisesRegex(ValueError, "workflow-selected"):
            actions.undo_actions(
                self.catalog, self.root, {"photos": {"Hero": self.photo.name}}, "Various",
                backup_fn=lambda *_: self.fail("should refuse before backup"), save_fn=self.save,
            )

    def test_catalogue_changes_during_backup_are_not_overwritten(self):
        def backup(*_):
            self.catalog["people"][self.person_id]["protected"] = False
            return "verified"

        with self.assertRaisesRegex(ValueError, "catalogue changed during backup"):
            self.apply(backup_fn=backup)
        self.assertFalse(self.catalog["people"][self.person_id]["protected"])
        self.assertTrue(self.folder.is_dir())
        self.assertFalse(self.destination.exists())

    def test_rollback_failure_is_explicit_and_reports_verified_backup(self):
        real_change = actions.person_rename.change_files

        def change(plan, *, reverse=False):
            if reverse:
                raise OSError("rollback blocked")
            return real_change(plan)

        with mock.patch.object(actions.person_rename, "change_files", side_effect=change):
            with self.assertRaisesRegex(OSError, "rename rollback failed.*verified backup: verified"):
                self.apply(save_fn=mock.Mock(side_effect=OSError("cannot save")))
        self.assertTrue(self.destination.is_dir())
        self.assertEqual(self.catalog, self.original)

    def test_linked_identity_is_not_exported_or_applied(self):
        real_hash = actions.person_rename.tree_hash

        def linked(folder):
            if pathlib.Path(folder) == self.folder:
                raise ValueError("rename cannot traverse a link or junction")
            return real_hash(folder)

        with mock.patch.object(actions.person_rename, "tree_hash", side_effect=linked):
            errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("link or junction", "\n".join(errors))

    def test_cli_preview_loads_downloaded_rename_and_keeps_files_unchanged(self):
        import contextlib
        import io

        path = self.root / "rename.json"
        path.write_text(json.dumps(self.document), encoding="utf-8")
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        output = io.StringIO()
        with mock.patch.object(actions.likeness.cw, "load_cfg", return_value={}), \
                contextlib.redirect_stdout(output):
            result = actions.main(["preview", str(path), "--root", str(self.root)])
        self.assertEqual(result, 0, output.getvalue())
        self.assertIn("rename identity", output.getvalue())
        self.assertIn("New Name", output.getvalue())
        self.assertEqual(person_rename.tree_hash(self.folder), self.original_tree)

    def test_render_exports_person_only_rename_snapshot_and_controls(self):
        decision = {key: value for key, value in self.document["actions"][0].items() if key != "newName"}
        page = review_gallery.render_html([{
            "folder": "Prospects/Old Name", "group": "Prospects",
            "personRenameAction": decision,
        }], "now")
        people = json.loads(page.split('<script id="people-data" type="application/json">')[1].split("</script>")[0])
        self.assertEqual(people["Prospects/Old Name"]["personRenameAction"], decision)
        self.assertIn("Stage rename", page)
        self.assertIn("Cancel rename", page)
        self.assertIn("actions.push(...stagedPeople.values())", page)


if __name__ == "__main__":
    unittest.main()
