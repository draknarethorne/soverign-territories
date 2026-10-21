#!/usr/bin/env python3
"""Tests for non-mutating likeness action manifest validation and preview."""
import copy
import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art.likeness_library import actions, metadata


class LikenessActionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.gallery = self.root / "Prospects" / "Sophie" / "gallery"
        self.gallery.mkdir(parents=True)
        self.photo = self.gallery / "sophie_image_123456.jpg"
        self.photo.write_bytes(b"photo bytes")
        self.photo_id = "photo:image_123456"
        self.photo_hash = metadata.content_sha256(self.photo)
        self.catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
        self.manifest = {
            "manifestVersion": 1,
            "generatedAt": "2026-10-20T12:00:00Z",
            "source": "people-gallery-review",
            "actions": [self.action("sent-to-review")],
        }

    def tearDown(self):
        self.temp.cleanup()

    def action(self, action_type, *, source="Gallery", photo_id=None, photo_hash=None):
        return {
            "type": action_type,
            "photoId": photo_id or self.photo_id,
            "contentSha256": photo_hash or self.photo_hash,
            "sourceBucket": source,
            "personFolder": "Prospects/Sophie",
        }

    def inspect(self, manifest=None, catalog=None, pool_folder="Prospects/Various"):
        return actions.validate_manifest(
            manifest or self.manifest,
            self.root,
            catalog or self.catalog,
            pool_folder,
        )

    def test_valid_manifest_plans_review_move_without_changing_files(self):
        before = self.photo.read_bytes()
        errors, plans = self.inspect()
        self.assertEqual(errors, [])
        self.assertEqual(plans[0]["source"], self.photo)
        self.assertEqual(
            plans[0]["destination"],
            self.root / "Prospects" / "Sophie" / "review" / self.photo.name,
        )
        self.assertEqual(self.photo.read_bytes(), before)
        self.assertFalse((self.gallery.parent / "review").exists())

    def test_selected_workflow_photo_cannot_be_moved(self):
        errors, _plans = actions.validate_manifest(
            self.manifest,
            self.root,
            self.catalog,
            chosen_ids={self.photo_id},
        )
        self.assertTrue(any("selected by an active workspace workflow" in error for error in errors))

    def test_stale_missing_and_ambiguous_photos_are_rejected(self):
        self.photo.write_bytes(b"changed photo")
        errors, _plans = self.inspect()
        self.assertTrue(any("content hash is stale" in error for error in errors))

        missing = copy.deepcopy(self.manifest)
        missing["actions"][0]["photoId"] = "photo:image_999999"
        errors, _plans = self.inspect(missing)
        self.assertTrue(any("is missing from the active library" in error for error in errors))

        duplicate = self.root / "Potentials" / "Another" / "gallery"
        duplicate.mkdir(parents=True)
        (duplicate / "another_image_123456.jpg").write_bytes(b"copy")
        errors, _plans = self.inspect()
        self.assertTrue(any("is ambiguous (2 active copies)" in error for error in errors))

    def test_manifest_must_match_current_folder_and_bucket(self):
        wrong_bucket = copy.deepcopy(self.manifest)
        wrong_bucket["actions"][0]["type"] = "review-approved"
        wrong_bucket["actions"][0]["sourceBucket"] = "Review"
        errors, _plans = self.inspect(wrong_bucket)
        self.assertTrue(any("not Prospects/Sophie/review" in error for error in errors))

        other_folder = copy.deepcopy(self.manifest)
        other_folder["actions"][0]["personFolder"] = "Potentials/Sophie"
        errors, _plans = self.inspect(other_folder)
        self.assertTrue(any("not Potentials/Sophie/gallery" in error for error in errors))

    def test_manifest_rejects_folder_paths_that_escape_the_library(self):
        escaped = copy.deepcopy(self.manifest)
        escaped["actions"][0]["personFolder"] = "Prospects/..\\..\\outside"
        errors, plans = self.inspect(escaped)
        self.assertTrue(errors)
        self.assertEqual(plans, [])
        with self.assertRaisesRegex(ValueError, "invalid likeness action manifest"):
            with tempfile.TemporaryDirectory() as tmp:
                path = pathlib.Path(tmp) / "unsafe.json"
                path.write_text(json.dumps(escaped), encoding="utf-8")
                actions.load_manifest(path)
        with self.assertRaisesRegex(ValueError, "unsafe action history path"):
            actions._safe_relative_path(self.root, "../outside/photo.jpg")

    def test_pool_folder_cannot_be_treated_as_a_person(self):
        pool = self.root / "Prospects" / "Various" / "gallery"
        pool.mkdir(parents=True)
        pool_photo = pool / "sophie_image_123456.jpg"
        pool_photo.write_bytes(b"photo bytes")
        self.photo.unlink()
        manifest = copy.deepcopy(self.manifest)
        manifest["actions"][0] = self.action("rejected-to-various")
        manifest["actions"][0]["personFolder"] = "Prospects/Various"
        errors, _plans = self.inspect(manifest)
        self.assertTrue(any("pool is not a person identity folder" in error for error in errors))

    def test_conflicting_moves_and_anchor_changes_are_rejected(self):
        conflict = copy.deepcopy(self.manifest)
        conflict["actions"].append(self.action("rejected-to-various"))
        errors, _plans = self.inspect(conflict)
        self.assertTrue(any("conflicts with actions/0" in error for error in errors))

        person_id = "person_" + "1" * 32
        self.catalog["people"][person_id] = {
            "id": person_id,
            "displayName": "Sophie",
            "folder": "Prospects/Sophie",
            "folderHistory": [],
            "identityAnchors": [self.photo_id],
        }
        anchor_move = copy.deepcopy(self.manifest)
        anchor_move["actions"].insert(0, self.action("anchor-removed"))
        errors, _plans = self.inspect(anchor_move)
        self.assertTrue(any("identity anchor state" in error and "move" in error for error in errors))

    def test_catalogue_person_mismatch_and_redundant_decisions_fail(self):
        person_id = "person_" + "1" * 32
        self.catalog["people"][person_id] = {
            "id": person_id,
            "displayName": "Sophie",
            "folder": "Prospects/Sophie",
            "folderHistory": [],
            "identityAnchors": [],
        }
        wrong_person = copy.deepcopy(self.manifest)
        wrong_person["actions"][0]["personId"] = "person_" + "2" * 32
        errors, _plans = self.inspect(wrong_person)
        self.assertTrue(any("personId does not own folder" in error for error in errors))

        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.photo_hash,
            "protected": True,
        }
        protect = copy.deepcopy(self.manifest)
        protect["actions"][0] = self.action("photo-protected")
        errors, _plans = self.inspect(protect)
        self.assertTrue(any("already protected" in error for error in errors))

    def test_anchor_cannot_be_reassigned_from_another_person(self):
        other_id = "person_" + "2" * 32
        self.catalog["people"][other_id] = {
            "id": other_id,
            "displayName": "Other person",
            "folder": "Potentials/Other",
            "folderHistory": [],
            "identityAnchors": [self.photo_id],
        }
        add_anchor = copy.deepcopy(self.manifest)
        add_anchor["actions"][0] = self.action("anchor-added")
        errors, _plans = self.inspect(add_anchor)
        self.assertTrue(any("already anchored to another person" in error for error in errors))

    def test_load_manifest_enforces_schema_and_preview_destination_is_configurable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "actions.json"
            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            self.assertEqual(actions.load_manifest(path), self.manifest)
            invalid = copy.deepcopy(self.manifest)
            invalid["actions"][0]["sourceBucket"] = "Review"
            path.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid likeness action manifest"):
                actions.load_manifest(path)

        rejected = copy.deepcopy(self.manifest)
        rejected["actions"][0] = self.action("rejected-to-various")
        errors, plans = self.inspect(rejected, pool_folder="Various")
        self.assertEqual(errors, [])
        self.assertEqual(plans[0]["destination"], self.root / "Various" / "gallery" / self.photo.name)

    def test_workflow_photo_selection_is_staged_applied_and_undoable(self):
        folder = self.root / "Angels" / "Sophie"
        gallery = folder / "gallery"
        scaled = folder / "gallery_944x1104"
        gallery.mkdir(parents=True)
        scaled.mkdir()
        old_photo = gallery / "sophie_image_111111.jpg"
        new_photo = gallery / "sophie_image_222222.jpg"
        old_photo.write_bytes(b"old photo")
        new_photo.write_bytes(b"new photo")
        old_scaled = scaled / "sophie_image_111111_944x1104.png"
        new_scaled = scaled / "sophie_image_222222_944x1104.png"
        old_scaled.write_bytes(b"old scaled")
        new_scaled.write_bytes(b"new scaled")
        cfg = {
            "standardSize": [944, 1104],
            "paths": {"workRoot": str(self.root)},
            "photos": {"Sophie": old_scaled.name},
            "flows": {},
        }
        manifest = copy.deepcopy(self.manifest)
        manifest["actions"] = [{
            "type": "workflow-photo-selected",
            "photoId": "photo:image_222222",
            "contentSha256": metadata.content_sha256(new_photo),
            "sourceBucket": "Gallery",
            "personFolder": "Angels/Sophie",
        }]
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = pathlib.Path(tmp) / "workflow.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(actions.load_manifest(manifest_path), manifest)

        errors, plans = actions.validate_manifest(
            manifest, self.root, self.catalog, cfg=cfg
        )
        self.assertEqual(errors, [])
        self.assertEqual(plans[0]["workflow"]["workflowPhotoBefore"], old_scaled.name)
        self.assertEqual(plans[0]["workflow"]["workflowPhotoAfter"], new_scaled.name)
        sandbox_cfg = copy.deepcopy(cfg)
        sandbox_cfg["paths"]["workRoot"] = str(self.root / "source-snapshot")
        with self.assertRaisesRegex(ValueError, "isolated sandbox"):
            actions.apply_actions(
                manifest, self.root, self.catalog, sandbox_cfg, "Prospects/Various"
            )

        backups = []

        def backup(root, _cfg, batch):
            result = root / "_backup" / batch
            backups.append(result)
            return result

        def save_catalog(updated):
            self.catalog.clear()
            self.catalog.update(copy.deepcopy(updated))

        def repoint(config, selections, _dry_run):
            for hero, (old_name, new_path) in selections.items():
                self.assertEqual(config["photos"][hero], old_name)
                config["photos"][hero] = pathlib.Path(new_path).name

        with mock.patch.object(actions.cw, "repoint_photos", side_effect=repoint):
            batch_id, _ = actions.apply_actions(
                manifest, self.root, self.catalog, cfg, "Prospects/Various",
                backup_fn=backup, save_fn=save_catalog,
            )
            self.assertEqual(cfg["photos"]["Sophie"], new_scaled.name)
            self.assertEqual(self.catalog["actions"][0]["type"], "workflow-photo-selected")
            self.assertEqual(metadata.validation_errors(self.catalog), [])

            errors, undo_batch, undo_plans = actions.plan_undo(
                self.catalog, self.root, batch_id, actions.selected_photo_ids(cfg), cfg
            )
            self.assertEqual(errors, [])
            self.assertEqual(undo_batch, batch_id)
            self.assertTrue(undo_plans[0]["workflow"])

            actions.undo_actions(
                self.catalog, self.root, cfg, "Prospects/Various",
                batch_id=batch_id, backup_fn=backup, save_fn=save_catalog,
            )
        self.assertEqual(cfg["photos"]["Sophie"], old_scaled.name)
        self.assertEqual(self.catalog["actions"][-1]["type"], "action-undone")
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        self.assertEqual(len(backups), 2)

    def test_workflow_photo_apply_rejects_an_isolated_sandbox_root(self):
        with self.assertRaisesRegex(ValueError, "isolated sandbox"):
            actions._require_configured_work_root(
                self.root,
                {"paths": {"workRoot": str(self.root / "configured-library")}},
            )

    def test_cli_preview_loads_config_and_reports_without_mutating(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "actions.json"
            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            before = self.photo.read_bytes()
            output = io.StringIO()
            with (
                mock.patch.object(actions.likeness.cw, "load_cfg", return_value={}),
                mock.patch.object(actions.likeness.cw, "work_root", return_value=str(self.root)),
                mock.patch.object(actions.likeness, "pool_home", return_value="Prospects/Various"),
                mock.patch.object(actions.metadata, "load_catalog", return_value=self.catalog),
                contextlib.redirect_stdout(output),
            ):
                result = actions.main(["preview", str(path)])
            self.assertEqual(result, 0)
            self.assertIn("sent-to-review:", output.getvalue())
            self.assertIn("preview only; no files or catalogue data were changed", output.getvalue())
            self.assertEqual(self.photo.read_bytes(), before)

    def test_cli_apply_requires_explicit_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "actions.json"
            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            batch_id = "batch_" + "1" * 32
            output = io.StringIO()
            with (
                mock.patch.object(actions.likeness.cw, "load_cfg", return_value={}),
                mock.patch.object(actions.likeness.cw, "work_root", return_value=str(self.root)),
                mock.patch.object(actions.likeness, "pool_home", return_value="Prospects/Various"),
                mock.patch.object(actions.metadata, "load_catalog", return_value=self.catalog),
                mock.patch.object(actions, "apply_actions", return_value=(batch_id, self.root / "_backup")) as apply,
                contextlib.redirect_stdout(output),
            ):
                result = actions.main(["apply", str(path)])
                self.assertEqual(result, 0)
                apply.assert_not_called()
                self.assertIn("preview only; add --apply", output.getvalue())

                output.seek(0)
                output.truncate()
                result = actions.main(["apply", str(path), "--apply"])
                self.assertEqual(result, 0)
                apply.assert_called_once()
                self.assertIn(f"applied batch {batch_id}", output.getvalue())

    def test_cli_undo_requires_explicit_flag(self):
        batch_id = "batch_" + "1" * 32
        undo_batch = "batch_" + "2" * 32
        with (
            mock.patch.object(actions.likeness.cw, "load_cfg", return_value={}),
            mock.patch.object(actions.likeness.cw, "work_root", return_value=str(self.root)),
            mock.patch.object(actions.likeness, "pool_home", return_value="Prospects/Various"),
            mock.patch.object(actions.metadata, "load_catalog", return_value=self.catalog),
            mock.patch.object(actions, "plan_undo", return_value=([], batch_id, [])),
            mock.patch.object(
                actions, "undo_actions",
                return_value=(undo_batch, self.root / "_backup", batch_id),
            ) as undo,
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = actions.main(["undo", batch_id])
            self.assertEqual(result, 0)
            undo.assert_not_called()
            self.assertIn("preview only; add --apply", output.getvalue())

            output.seek(0)
            output.truncate()
            with contextlib.redirect_stdout(output):
                result = actions.main(["undo", batch_id, "--apply"])
            self.assertEqual(result, 0)
            undo.assert_called_once()
            self.assertIn(f"undid {batch_id}", output.getvalue())

    def test_apply_and_undo_move_photo_with_auditable_metadata_and_verified_backups(self):
        backups = []

        def save_catalog(updated):
            self.catalog.clear()
            self.catalog.update(copy.deepcopy(updated))

        def backup(root, _cfg, batch):
            path = root / "_backup" / batch
            backups.append(path)
            return path

        batch_id, backup_path = actions.apply_actions(
            self.manifest, self.root, self.catalog, {}, "Prospects/Various",
            backup_fn=backup, save_fn=save_catalog,
        )
        review_path = self.gallery.parent / "review" / self.photo.name
        self.assertFalse(self.photo.exists())
        self.assertEqual(review_path.read_bytes(), b"photo bytes")
        self.assertEqual(backup_path, backups[0])
        self.assertEqual(self.catalog["actions"][0]["batchId"], batch_id)
        self.assertEqual(self.catalog["actions"][0]["source"], "Prospects/Sophie/gallery/sophie_image_123456.jpg")
        self.assertEqual(self.catalog["actions"][0]["destination"], "Prospects/Sophie/review/sophie_image_123456.jpg")
        self.assertEqual(metadata.validation_errors(self.catalog), [])

        undo_batch, undo_backup, undone_batch = actions.undo_actions(
            self.catalog, self.root, {}, "Prospects/Various", batch_id=batch_id,
            backup_fn=backup, save_fn=save_catalog,
        )
        self.assertEqual(undone_batch, batch_id)
        self.assertEqual(undo_backup, backups[1])
        self.assertTrue(undo_batch.startswith("batch_"))
        self.assertTrue(self.photo.is_file())
        self.assertFalse(review_path.exists())
        self.assertEqual(self.catalog["people"][self.catalog["actions"][0]["personId"]]["identityAnchors"], [])
        self.assertEqual(self.catalog["photos"][self.photo_id]["protected"], False)
        self.assertEqual(self.catalog["actions"][-1]["type"], "action-undone")
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        errors, batch, plans = actions.plan_undo(self.catalog, self.root)
        self.assertTrue(errors)
        self.assertIsNone(batch)
        self.assertEqual(plans, [])

    def test_explicit_review_removes_anchor_once_and_undo_restores_anchor_and_protection(self):
        person_id = "person_" + "1" * 32
        self.catalog["people"][person_id] = {
            "id": person_id,
            "displayName": "Sophie",
            "folder": "Prospects/Sophie",
            "folderHistory": [],
            "identityAnchors": [self.photo_id],
        }
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.photo_hash,
            "protected": True,
        }

        def save_catalog(updated):
            self.catalog.clear()
            self.catalog.update(copy.deepcopy(updated))

        def backup(root, _cfg, batch):
            return root / "_backup" / batch

        batch_id, _backup_path = actions.apply_actions(
            self.manifest, self.root, self.catalog, {}, "Prospects/Various",
            backup_fn=backup, save_fn=save_catalog,
        )
        self.assertEqual(self.catalog["people"][person_id]["identityAnchors"], [])
        self.assertTrue(self.catalog["photos"][self.photo_id]["protected"])

        actions.undo_actions(
            self.catalog, self.root, {}, "Prospects/Various", batch_id=batch_id,
            backup_fn=backup, save_fn=save_catalog,
        )
        self.assertEqual(self.catalog["people"][person_id]["identityAnchors"], [self.photo_id])
        self.assertTrue(self.catalog["photos"][self.photo_id]["protected"])

    def test_metadata_only_protection_action_can_be_applied_and_undone(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["actions"][0] = self.action("photo-protected")

        def save_catalog(updated):
            self.catalog.clear()
            self.catalog.update(copy.deepcopy(updated))

        def backup(root, _cfg, batch):
            return root / "_backup" / batch

        batch_id, _backup_path = actions.apply_actions(
            manifest, self.root, self.catalog, {}, "Prospects/Various",
            backup_fn=backup, save_fn=save_catalog,
        )
        self.assertTrue(self.photo.is_file())
        self.assertTrue(self.catalog["photos"][self.photo_id]["protected"])

        actions.undo_actions(
            self.catalog, self.root, {}, "Prospects/Various", batch_id=batch_id,
            backup_fn=backup, save_fn=save_catalog,
        )
        self.assertTrue(self.photo.is_file())
        self.assertFalse(self.catalog["photos"][self.photo_id]["protected"])

    def test_apply_rolls_back_moved_photos_when_catalogue_save_fails(self):
        def backup(root, _cfg, _batch):
            return root / "_backup" / "verified"

        def fail_save(_updated):
            raise OSError("simulated catalogue failure")

        with self.assertRaisesRegex(OSError, "simulated catalogue failure"):
            actions.apply_actions(
                self.manifest, self.root, self.catalog, {}, "Prospects/Various",
                backup_fn=backup, save_fn=fail_save,
            )
        self.assertTrue(self.photo.is_file())
        self.assertFalse((self.gallery.parent / "review" / self.photo.name).exists())
        self.assertFalse((self.gallery.parent / "review").exists())
        self.assertEqual(
            self.catalog,
            {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
        )

    def test_apply_rolls_back_earlier_moves_when_a_later_move_fails(self):
        second_photo = self.gallery / "sophie_image_654321.jpg"
        second_photo.write_bytes(b"second photo")
        second_id = "photo:image_654321"
        manifest = copy.deepcopy(self.manifest)
        manifest["actions"].append(
            self.action(
                "sent-to-review",
                photo_id=second_id,
                photo_hash=metadata.content_sha256(second_photo),
            )
        )
        original_move = actions.shutil.move
        call_count = 0

        def fail_second_move(source, destination):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise OSError("simulated move failure")
            return original_move(source, destination)

        with mock.patch.object(actions.shutil, "move", side_effect=fail_second_move):
            with self.assertRaisesRegex(OSError, "simulated move failure"):
                actions.apply_actions(
                    manifest, self.root, self.catalog, {}, "Prospects/Various",
                    backup_fn=lambda root, _cfg, batch: root / "_backup" / batch,
                )

        self.assertTrue(self.photo.is_file())
        self.assertTrue(second_photo.is_file())
        self.assertFalse((self.gallery.parent / "review").exists())
        self.assertEqual(self.catalog["actions"], [])

    def test_apply_revalidates_photo_after_creating_backup(self):
        def backup(_root, _cfg, _batch):
            self.photo.write_bytes(b"changed during backup")
            return self.root / "_backup" / "verified"

        with self.assertRaisesRegex(ValueError, "library changed after backup"):
            actions.apply_actions(
                self.manifest, self.root, self.catalog, {}, "Prospects/Various",
                backup_fn=backup, save_fn=lambda _updated: self.fail("catalogue should not be saved"),
            )
        self.assertEqual(self.photo.read_bytes(), b"changed during backup")
        self.assertEqual(self.catalog["actions"], [])

    def test_undo_rolls_back_file_move_when_catalogue_save_fails(self):
        def save_catalog(updated):
            self.catalog.clear()
            self.catalog.update(copy.deepcopy(updated))

        def backup(root, _cfg, batch):
            return root / "_backup" / batch

        batch_id, _backup_path = actions.apply_actions(
            self.manifest, self.root, self.catalog, {}, "Prospects/Various",
            backup_fn=backup, save_fn=save_catalog,
        )
        review_path = self.gallery.parent / "review" / self.photo.name
        applied_catalog = copy.deepcopy(self.catalog)

        def fail_save(_updated):
            raise OSError("simulated undo catalogue failure")

        with self.assertRaisesRegex(OSError, "simulated undo catalogue failure"):
            actions.undo_actions(
                self.catalog, self.root, {}, "Prospects/Various", batch_id=batch_id,
                backup_fn=backup, save_fn=fail_save,
            )
        self.assertTrue(review_path.is_file())
        self.assertFalse(self.photo.exists())
        self.assertEqual(self.catalog, applied_catalog)


if __name__ == "__main__":
    unittest.main()
