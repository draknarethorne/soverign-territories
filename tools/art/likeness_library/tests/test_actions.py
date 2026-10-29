#!/usr/bin/env python3
"""Tests for non-mutating likeness action manifest validation and preview."""
import copy
import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
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

    def test_every_nonworkflow_photo_option_round_trips_through_json_apply_and_undo(self):
        action_types = {
            "anchor-added", "anchor-removed", "photo-protected", "photo-unprotected",
            "sent-to-review", "rejected-to-various", "match-rejected",
            "review-approved", "photo-retired", "photo-junked", "match-accepted",
        }
        schema = json.loads(actions.MANIFEST_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(
            action_types | {"workflow-photo-selected"},
            set(schema["definitions"]["action"]["properties"]["type"]["enum"]),
        )
        for action_type in sorted(action_types):
            with self.subTest(action=action_type), tempfile.TemporaryDirectory() as directory:
                root = pathlib.Path(directory)
                person_id, target_id = "person_" + "a" * 32, "person_" + "b" * 32
                bucket = "Review" if action_type == "review-approved" else "Gallery"
                source = root / "Prospects" / "Example" / bucket.lower() / "example_image_123456.jpg"
                source.parent.mkdir(parents=True)
                source.write_bytes(b"round-trip original")
                target = root / "Prospects" / "Other"
                target.mkdir(parents=True)
                digest = metadata.content_sha256(source)
                catalog = {
                    "schemaVersion": 1, "actions": [],
                    "photos": {self.photo_id: {
                        "contentSha256": digest, "protected": action_type == "photo-unprotected",
                    }},
                    "people": {
                        key: {
                            "id": key, "folder": folder, "displayName": folder.split("/")[-1],
                            "folderHistory": [],
                            "identityAnchors": [self.photo_id] if (
                                key == person_id and action_type == "anchor-removed"
                            ) else [],
                        }
                        for key, folder in ((person_id, "Prospects/Example"), (target_id, "Prospects/Other"))
                    },
                }
                initial = copy.deepcopy(catalog)
                decision = {
                    "type": action_type, "photoId": self.photo_id, "contentSha256": digest,
                    "sourceBucket": bucket, "personFolder": "Prospects/Example", "personId": person_id,
                }
                if action_type == "match-accepted":
                    decision.update(destinationFolder="Prospects/Other", destinationPersonId=target_id)
                document = {**self.manifest, "actions": [decision]}
                manifest_path = root / "downloaded-actions.json"
                manifest_path.write_text(json.dumps(document), encoding="utf-8")
                loaded = actions.load_manifest(manifest_path)
                errors, plans = actions.validate_manifest(loaded, root, catalog, "Various")
                self.assertEqual(errors, [])
                self.assertEqual(catalog, initial)
                self.assertTrue(source.is_file())
                backups = []

                def save(updated):
                    catalog.clear()
                    catalog.update(copy.deepcopy(updated))

                def backup(*args):
                    backups.append(args)
                    return "verified-test-backup"

                batch, _ = actions.apply_actions(
                    loaded, root, catalog, {}, "Various", backup_fn=backup, save_fn=save,
                )
                self.assertEqual(catalog["actions"][-1]["type"], action_type)
                if plans[0]["destination"] is not None:
                    self.assertFalse(source.exists())
                    self.assertEqual(plans[0]["destination"].read_bytes(), b"round-trip original")
                if action_type == "anchor-added":
                    self.assertIn(self.photo_id, catalog["people"][person_id]["identityAnchors"])
                if action_type == "anchor-removed":
                    self.assertEqual(catalog["people"][person_id]["identityAnchors"], [])
                if action_type in ("photo-protected", "photo-unprotected"):
                    self.assertEqual(catalog["photos"][self.photo_id]["protected"], action_type == "photo-protected")
                if action_type == "match-rejected":
                    self.assertEqual(catalog["photos"][self.photo_id]["rejectedPersonIds"], [person_id])
                actions.undo_actions(
                    catalog, root, {}, "Various", batch_id=batch, backup_fn=backup, save_fn=save,
                )
                self.assertEqual(len(backups), 2)
                self.assertEqual(source.read_bytes(), b"round-trip original")
                self.assertEqual(catalog["people"], initial["people"])
                self.assertEqual(catalog["photos"], initial["photos"])
                if plans[0]["destination"] is not None:
                    self.assertFalse(plans[0]["destination"].exists())

    def test_selected_workflow_photo_cannot_be_moved(self):
        errors, _plans = actions.validate_manifest(
            self.manifest,
            self.root,
            self.catalog,
            chosen_ids={self.photo_id},
        )
        self.assertTrue(any("selected by an active workspace workflow" in error for error in errors))

    def test_explicit_other_identity_move_uses_review_and_validates_protection(self):
        target = self.root / "Angels" / "Angelica"
        target.mkdir(parents=True)
        manifest = copy.deepcopy(self.manifest)
        manifest["actions"][0] = {
            **self.action("match-accepted"), **self.destination(),
        }
        errors, plans = self.inspect(manifest)
        self.assertEqual(errors, [])
        self.assertEqual(plans[0]["destination"], target / "review" / self.photo.name)
        self.assertTrue(self.photo.is_file())
        protected = copy.deepcopy(self.catalog)
        protected["photos"][self.photo_id] = {
            "contentSha256": self.photo_hash, "protected": True,
        }
        errors, _ = self.inspect(manifest, protected)
        self.assertTrue(any("remove photo protection" in error for error in errors))
        manifest["actions"][0]["destinationFolder"] = "Angels/Missing"
        errors, _ = self.inspect(manifest)
        self.assertTrue(any("existing, unambiguous identity" in error for error in errors))

    def test_other_identity_action_requires_destination_only_for_that_action(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["actions"][0] = self.action("match-accepted")
        errors, plans = self.inspect(manifest)
        self.assertTrue(errors)
        self.assertEqual(plans, [])
        manifest["actions"][0] = {
            **self.action("sent-to-review"), "destinationFolder": "Angels/Angelica",
        }
        errors, plans = self.inspect(manifest)
        self.assertTrue(errors)
        self.assertEqual(plans, [])

    def test_other_identity_reassignment_apply_and_undo(self):
        (self.root / "Angels" / "Angelica" / "gallery").mkdir(parents=True)
        manifest = copy.deepcopy(self.manifest)
        manifest["actions"][0] = {
            **self.action("match-accepted"), **self.destination(),
        }

        def save(updated):
            self.catalog.clear()
            self.catalog.update(copy.deepcopy(updated))

        batch, _ = actions.apply_actions(
            manifest, self.root, self.catalog, {}, "Various", backup_fn=lambda *_: "verified",
            save_fn=save,
        )
        target = self.root / "Angels" / "Angelica" / "review" / self.photo.name
        self.assertEqual(target.read_bytes(), b"photo bytes")
        self.assertFalse(self.photo.exists())
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        destination_id = manifest["actions"][0]["destinationPersonId"]
        self.assertEqual(self.catalog["actions"][-1]["destinationPersonId"], destination_id)
        changed = copy.deepcopy(self.catalog)
        changed["people"][destination_id]["folder"] = "Angels/Changed"
        errors, _, plans = actions.plan_undo(changed, self.root, batch_id=batch)
        self.assertTrue(any("destination identity changed" in error for error in errors))
        self.assertEqual(plans, [])
        actions.undo_actions(
            self.catalog, self.root, {}, "Various", batch_id=batch,
            backup_fn=lambda *_: "verified", save_fn=save,
        )
        self.assertEqual(self.photo.read_bytes(), b"photo bytes")
        self.assertFalse(target.exists())

    def destination(self):
        person_id = "person_" + "9" * 32
        self.catalog["people"][person_id] = {
            "id": person_id, "folder": "Angels/Angelica", "displayName": "Angelica",
            "folderHistory": [], "identityAnchors": [], "protected": True,
        }
        return {"destinationFolder": "Angels/Angelica", "destinationPersonId": person_id}

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


class PersonProtectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.person_id = "person_" + "7" * 32
        self.folder = self.root / "Models" / "Example"
        self.folder.mkdir(parents=True)
        self.note = self.folder / "z_example.txt"
        self.note.write_bytes(b"Example Name\n")
        self.catalog = {
            "schemaVersion": 1, "photos": {}, "actions": [],
            "people": {self.person_id: {
                "id": self.person_id, "folder": "Models/Example", "displayName": "Example Name",
                "folderHistory": ["Prospects/Example"], "identityAnchors": [],
            }},
        }
        self.path = self.root / ".likeness-library.json"
        metadata.save_catalog(self.catalog, self.path)
        self.manifest = {
            "manifestVersion": 1, "generatedAt": "2026-10-22T09:30:00-05:00",
            "source": "people-gallery-review", "actions": [{
                "type": "person-protected", "personId": self.person_id,
                "personFolder": "Models/Example", "expectedProtected": False,
            }],
        }

    def save(self, catalog):
        metadata.save_catalog(catalog, self.path)
        self.catalog.clear()
        self.catalog.update(copy.deepcopy(catalog))

    def apply(self, backup=None):
        return actions.apply_actions(
            self.manifest, self.root, self.catalog, {}, "Various",
            backup_fn=backup or (lambda *_: "verified"), save_fn=self.save,
        )

    def test_preview_is_photo_independent_and_read_only(self):
        before = self.path.read_bytes()
        errors, plans = actions.validate_manifest(self.manifest, self.root, self.catalog)
        self.assertEqual(errors, [])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            actions.print_preview(plans)
        self.assertIn(self.person_id, output.getvalue())
        self.assertIn("identity permission only", output.getvalue())
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.note.read_bytes(), b"Example Name\n")
        manifest_path = self.root / "actions.json"
        manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.assertEqual(actions.load_manifest(manifest_path), self.manifest)

    def test_protect_unprotect_and_undo_preserve_identity_and_no_photo_records(self):
        original = copy.deepcopy(self.catalog["people"][self.person_id])
        first, _ = self.apply()
        self.assertTrue(self.catalog["people"][self.person_id]["protected"])
        self.assertEqual(self.catalog["photos"], {})
        self.assertEqual(self.catalog["actions"][-1]["photoIds"], [])
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        self.manifest["actions"][0].update(type="person-unprotected", expectedProtected=True)
        second, _ = self.apply()
        self.assertFalse(self.catalog["people"][self.person_id]["protected"])
        actions.undo_actions(
            self.catalog, self.root, {}, "Various", batch_id=second,
            backup_fn=lambda *_: "verified", save_fn=self.save,
        )
        self.assertTrue(self.catalog["people"][self.person_id]["protected"])
        actions.undo_actions(
            self.catalog, self.root, {}, "Various", batch_id=first,
            backup_fn=lambda *_: "verified", save_fn=self.save,
        )
        self.assertEqual(self.catalog["people"][self.person_id], original)
        self.assertEqual(self.catalog["photos"], {})
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        self.assertEqual(self.note.read_bytes(), b"Example Name\n")

    def test_stale_or_replaced_identity_and_noop_are_rejected(self):
        for field, value in (
            ("expectedProtected", True), ("personId", "person_" + "6" * 32),
            ("personFolder", "Models/Missing"), ("type", "person-unprotected"),
        ):
            with self.subTest(field=field):
                document = copy.deepcopy(self.manifest)
                document["actions"][0][field] = value
                errors, _ = actions.validate_manifest(document, self.root, self.catalog)
                self.assertTrue(errors)

    def test_cast_potential_and_photo_shaped_identity_actions_are_rejected(self):
        for folder in ("Angels/Example", "Sisters/Example", "Potentials/Example", "Models/../Example"):
            document = copy.deepcopy(self.manifest)
            document["actions"][0]["personFolder"] = folder
            errors, _ = actions.validate_manifest(document, self.root, self.catalog)
            self.assertTrue(errors, folder)
        document = copy.deepcopy(self.manifest)
        document["actions"][0]["photoId"] = "photo:image_123456"
        self.assertTrue(actions.validate_manifest(document, self.root, self.catalog)[0])

    def test_duplicate_and_mixed_source_or_destination_actions_conflict(self):
        duplicate = copy.deepcopy(self.manifest)
        duplicate["actions"].append(copy.deepcopy(duplicate["actions"][0]))
        self.assertTrue(actions.validate_manifest(duplicate, self.root, self.catalog)[0])
        for source, destination in (("Models/Example", None), ("Prospects/Other", "Models/Example")):
            document = copy.deepcopy(self.manifest)
            photo_action = {
                "type": "sent-to-review" if destination is None else "match-accepted",
                "photoId": "photo:image_123456", "contentSha256": "a" * 64,
                "sourceBucket": "Gallery", "personFolder": source,
            }
            if destination:
                photo_action.update(destinationFolder=destination, destinationPersonId=self.person_id)
            document["actions"].append(photo_action)
            errors, plans = actions.validate_manifest(document, self.root, self.catalog)
            self.assertTrue(any("separately" in error for error in errors))
            self.assertEqual(plans, [])

    def test_merged_or_duplicate_folder_ownership_is_rejected(self):
        changed = copy.deepcopy(self.catalog)
        changed["people"][self.person_id]["mergedInto"] = "person_" + "6" * 32
        self.assertTrue(actions.validate_manifest(self.manifest, self.root, changed)[0])
        changed = copy.deepcopy(self.catalog)
        changed["people"]["person_" + "6" * 32] = copy.deepcopy(changed["people"][self.person_id])
        self.assertTrue(actions.validate_manifest(self.manifest, self.root, changed)[0])

    def test_catalogue_edit_during_apply_backup_is_not_overwritten(self):
        def backup(*_):
            changed = copy.deepcopy(self.catalog)
            changed["people"][self.person_id]["displayName"] = "Concurrent edit"
            metadata.save_catalog(changed, self.path)
            return "verified"

        with self.assertRaisesRegex(ValueError, "catalogue changed"):
            self.apply(backup)
        self.assertEqual(metadata.load_catalog(self.path)["people"][self.person_id]["displayName"], "Concurrent edit")
        self.assertEqual(self.catalog["actions"], [])

    def test_catalogue_edit_during_undo_backup_is_not_overwritten(self):
        batch, _ = self.apply()

        def backup(*_):
            changed = copy.deepcopy(self.catalog)
            changed["people"][self.person_id]["displayName"] = "Concurrent edit"
            metadata.save_catalog(changed, self.path)
            return "verified"

        with self.assertRaisesRegex(ValueError, "catalogue changed"):
            actions.undo_actions(
                self.catalog, self.root, {}, "Various", batch_id=batch,
                backup_fn=backup, save_fn=self.save,
            )
        self.assertTrue(metadata.load_catalog(self.path)["people"][self.person_id]["protected"])
        self.assertEqual(metadata.load_catalog(self.path)["people"][self.person_id]["displayName"], "Concurrent edit")

    def test_undo_refuses_later_person_change(self):
        batch, _ = self.apply()
        self.catalog["people"][self.person_id]["folder"] = "Prospects/Example"
        errors, _, plans = actions.plan_undo(self.catalog, self.root, batch)
        self.assertTrue(any("person state changed" in error for error in errors))
        self.assertEqual(plans, [])

    def test_save_failure_does_not_change_person_or_history_files(self):
        before = self.path.read_bytes()
        with self.assertRaisesRegex(OSError, "save failed"):
            actions.apply_actions(
                self.manifest, self.root, self.catalog, {}, "Various",
                backup_fn=lambda *_: "verified", save_fn=mock.Mock(side_effect=OSError("save failed")),
            )
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.catalog["actions"], [])
        self.assertEqual(self.note.read_bytes(), b"Example Name\n")

    def test_engine_respects_identity_toggle_without_changing_scores(self):
        import numpy as np
        from tools.art.likeness_library import identity_maintenance, reconciliation
        from tools.art.likeness_library.policy import evaluate_photo_route, load_policy

        policy = load_policy()
        gallery = self.folder / "gallery"
        gallery.mkdir()
        photos = []
        for index in range(5):
            path = gallery / f"example_image_{100000 + index}.jpg"
            path.write_bytes(str(index).encode())
            photos.append(SimpleNamespace(
                path=path, name=path.name, key="Models/Example", vec=np.array([1., 0.]),
                usable=lambda _: True,
            ))
        space = SimpleNamespace(
            photos=photos, by_key={"Models/Example": photos}, st=policy["runtimeSettings"],
        )

        def cores():
            return reconciliation.frozen_identity_cores(
                space, self.catalog, photo_id_fn=metadata.photo_id_from_name,
                content_sha256_fn=metadata.content_sha256, policy=policy,
            )[0]

        before = cores()
        self.apply()
        protected = cores()
        np.testing.assert_array_equal(before["Models/Example"]["vector"], protected["Models/Example"]["vector"])
        self.assertEqual(before["Models/Example"]["photoScores"], protected["Models/Example"]["photoScores"])
        self.assertTrue(protected["Models/Example"]["identityProtected"])
        transitions, _ = identity_maintenance.category_transitions(
            space, protected, {"moves": []}, self.catalog, set(), set(), policy, self.root,
        )
        self.assertEqual(transitions, [])
        route = evaluate_photo_route(
            "Models", score=.9, margin=.5, identity_protected=True, policy=policy, propose=True,
        )
        self.assertNotEqual(route["decision"], "auto-route")
        self.manifest["actions"][0].update(type="person-unprotected", expectedProtected=True)
        self.apply()
        transitions, _ = identity_maintenance.category_transitions(
            space, cores(), {"moves": []}, self.catalog, set(), set(), policy, self.root,
        )
        self.assertEqual(transitions[0]["destinationFolder"], "Prospects/Example")


if __name__ == "__main__":
    unittest.main()
