"""Recoverable photo retirement uses the common staged transaction boundary."""
import contextlib
import copy
import io
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art.likeness_library import actions, metadata, retained_preparation, review_gallery


class PhotoRetirementTests(unittest.TestCase):
    action_type = "photo-retired"
    destination_root = "_retired/photos"
    operation = "retirement"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.person_id = "person_" + "a" * 32
        self.photo_id = "photo:image_123456"
        self.catalog = {
            "schemaVersion": 1, "photos": {}, "actions": [],
            "people": {self.person_id: {
                "id": self.person_id, "displayName": "Example Person",
                "folder": "Prospects/Example", "folderHistory": [], "identityAnchors": [],
            }},
        }
        self.source = self.root / "Prospects" / "Example" / "review" / "example_image_123456.jpg"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"original photo bytes")
        self.manifest = {
            "manifestVersion": 1, "generatedAt": "2026-10-22T10:36:00-05:00",
            "source": "people-gallery-review", "actions": [{
                "type": self.action_type, "photoId": self.photo_id, "personId": self.person_id,
                "personFolder": "Prospects/Example", "sourceBucket": "Review",
                "contentSha256": metadata.content_sha256(self.source),
            }],
        }
        self.destination = (
            self.root / self.destination_root / "Prospects" / "Example"
            / "review" / self.source.name
        )
        self.backups = []

    def save(self, updated):
        self.catalog.clear()
        self.catalog.update(copy.deepcopy(updated))

    def backup(self, *_):
        self.backups.append(copy.deepcopy(self.catalog))
        return "verified-backup"

    def apply(self, cfg=None, **kwargs):
        return actions.apply_actions(
            self.manifest, self.root, self.catalog,
            cfg if cfg is not None else {}, "Various",
            backup_fn=self.backup, save_fn=self.save, **kwargs,
        )

    def test_configured_retired_root_round_trips(self):
        name = "retired" if self.action_type == "photo-retired" else "junk"
        root_name = "_retired_custom" if name == "retired" else "_quarantine"
        prefix = root_name + ("/photos" if name == "retired" else "")
        cfg = {"storageRoots": {name: root_name}}
        self.destination = (
            self.root.joinpath(*prefix.split("/"), "Prospects", "Example", "review", self.source.name)
        )
        with mock.patch.object(actions.cw, "load_cfg", return_value=cfg), \
                mock.patch.object(retained_preparation.cw, "load_cfg", return_value=cfg):
            batch, _ = self.apply(cfg=cfg)
            self.assertEqual(self.destination.read_bytes(), b"original photo bytes")
            self.assertEqual(
                self.catalog["actions"][-1]["destination"],
                f"{prefix}/Prospects/Example/review/{self.source.name}",
            )
            actions.undo_actions(
                self.catalog, self.root, cfg, "Various", batch_id=batch,
                backup_fn=self.backup, save_fn=self.save,
            )
        self.assertTrue(self.source.is_file())
        self.assertFalse(self.destination.exists())

    def test_retained_journal_uses_configured_reports_root(self):
        cfg = {"storageRoots": {"reports": "operations/reports"}}
        batch = "batch_" + "a" * 32

        journal = actions._retained_journal(self.root, batch, cfg)

        self.assertEqual(
            journal,
            self.root / "operations" / "reports" / "runs"
            / f"manual-retained-{batch}.json",
        )

    def test_schema_preview_and_cancel_are_nonmutating_and_show_archive_destination(self):
        path = self.root / "staged.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.assertEqual(actions.load_manifest(path), self.manifest)
        before = copy.deepcopy(self.catalog)
        errors, plans = actions.validate_manifest(self.manifest, self.root, self.catalog, "Various")
        self.assertEqual(errors, [])
        self.assertEqual(plans[0]["destination"], self.destination)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            actions.print_preview(plans)
        self.assertIn(str(self.destination), output.getvalue())
        self.assertEqual(self.catalog, before)
        self.assertTrue(self.source.is_file())
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.backups, [])

    def test_apply_archives_only_photo_excludes_it_from_active_index_and_undo_restores(self):
        before = copy.deepcopy(self.catalog)
        sibling = self.source.with_name("example_image_999999.jpg")
        sibling.write_bytes(b"keep active")
        batch, backup = self.apply()
        self.assertEqual(backup, "verified-backup")
        self.assertEqual(self.backups, [before])
        self.assertFalse(self.source.exists())
        self.assertEqual(self.destination.read_bytes(), b"original photo bytes")
        self.assertEqual(sibling.read_bytes(), b"keep active")
        self.assertNotIn(self.photo_id, actions._index_photos(self.root))
        record = self.catalog["actions"][-1]
        self.assertEqual(record["type"], self.action_type)
        self.assertEqual(record["photoIds"], [self.photo_id])
        self.assertEqual(record["destination"], self.destination_root + "/Prospects/Example/review/" + self.source.name)
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        actions.undo_actions(
            self.catalog, self.root, {}, "Various", batch_id=batch,
            backup_fn=self.backup, save_fn=self.save,
        )
        self.assertEqual(len(self.backups), 2)
        self.assertEqual(self.source.read_bytes(), b"original photo bytes")
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.catalog["people"], before["people"])
        self.assertEqual(self.catalog["photos"], {
            self.photo_id: {"contentSha256": metadata.content_sha256(self.source), "protected": False},
        })
        self.assertEqual(metadata.validation_errors(self.catalog), [])

    def test_gallery_photo_retirement_preserves_bucket_in_archive_and_restore(self):
        gallery_source = self.source.parent.parent / "gallery" / self.source.name
        gallery_source.parent.mkdir()
        self.source.replace(gallery_source)
        self.source = gallery_source
        self.manifest["actions"][0]["sourceBucket"] = "Gallery"
        self.destination = self.destination.parent.parent / "gallery" / self.source.name
        batch, _ = self.apply()
        self.assertEqual(self.destination.read_bytes(), b"original photo bytes")
        actions.undo_actions(
            self.catalog, self.root, {}, "Various", batch_id=batch,
            backup_fn=self.backup, save_fn=self.save,
        )
        self.assertTrue(self.source.exists())

    def test_protected_anchored_and_workflow_selected_photos_refused(self):
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": metadata.content_sha256(self.source), "protected": True,
        }
        errors, _ = actions.validate_manifest(self.manifest, self.root, self.catalog)
        self.assertIn("before " + self.operation, "\n".join(errors))
        self.catalog["photos"].clear()
        self.catalog["people"][self.person_id]["identityAnchors"] = [self.photo_id]
        errors, _ = actions.validate_manifest(self.manifest, self.root, self.catalog)
        self.assertIn("before " + self.operation, "\n".join(errors))
        self.catalog["people"][self.person_id]["identityAnchors"] = []
        errors, _ = actions.validate_manifest(
            self.manifest, self.root, self.catalog, chosen_ids={self.photo_id},
        )
        self.assertIn("active workspace workflow", "\n".join(errors))
        self.assertEqual(self.backups, [])

    def test_duplicate_conflicting_and_protection_actions_refused_in_both_orders(self):
        for action_type in ("photo-retired", "photo-junked", "sent-to-review", "photo-protected", "photo-unprotected"):
            for reverse in (False, True):
                with self.subTest(action_type=action_type, reverse=reverse):
                    other = {**self.manifest["actions"][0], "type": action_type}
                    if action_type == "sent-to-review":
                        other["type"] = "review-approved"
                    document = copy.deepcopy(self.manifest)
                    document["actions"].append(other)
                    if reverse:
                        document["actions"].reverse()
                    errors, _ = actions.validate_manifest(document, self.root, self.catalog)
                    self.assertTrue(errors)

    def test_stale_content_wrong_identity_and_occupied_archive_refused(self):
        self.source.write_bytes(b"changed")
        errors, _ = actions.validate_manifest(self.manifest, self.root, self.catalog)
        self.assertIn("hash is stale", "\n".join(errors))
        self.source.write_bytes(b"original photo bytes")
        self.manifest["actions"][0]["personId"] = "person_" + "b" * 32
        errors, _ = actions.validate_manifest(self.manifest, self.root, self.catalog)
        self.assertIn("does not own folder", "\n".join(errors))
        self.manifest["actions"][0]["personId"] = self.person_id
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(b"previous archive")
        errors, _ = actions.validate_manifest(self.manifest, self.root, self.catalog)
        self.assertIn("destination already exists", "\n".join(errors))
        self.assertEqual(self.destination.read_bytes(), b"previous archive")

    def test_save_failure_rolls_back_and_backup_race_prevents_archive(self):
        before = copy.deepcopy(self.catalog)

        def fail_save(_):
            raise OSError("save failed")

        with self.assertRaisesRegex(OSError, "save failed"):
            actions.apply_actions(
                self.manifest, self.root, self.catalog, {}, "Various",
                backup_fn=self.backup, save_fn=fail_save,
            )
        self.assertTrue(self.source.exists())
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.catalog, before)

        def change_during_backup(*_):
            self.source.write_bytes(b"changed after backup")
            return "verified-backup"

        with self.assertRaisesRegex(ValueError, "library changed after backup"):
            actions.apply_actions(
                self.manifest, self.root, self.catalog, {}, "Various",
                backup_fn=change_during_backup, save_fn=self.save,
            )
        self.assertFalse(self.destination.exists())

    def test_undo_refuses_changed_archive_or_replaced_original(self):
        batch, _ = self.apply()
        self.destination.write_bytes(b"changed archive")
        errors, _, _ = actions.plan_undo(self.catalog, self.root, batch)
        self.assertTrue(errors)
        self.destination.write_bytes(b"original photo bytes")
        self.source.write_bytes(b"new occupant")
        errors, _, _ = actions.plan_undo(self.catalog, self.root, batch)
        self.assertTrue(errors)

    def test_ui_offers_retirement_only_for_movable_gallery_or_review_photos(self):
        for bucket in ("Gallery", "Review"):
            options = review_gallery.action_options(bucket, self.photo_id)
            self.assertIn(self.action_type, dict(options))
            self.assertIn("configured", dict(options)[self.action_type])
            for restrictions in (
                {"protected": True}, {"anchor": True}, {"workflow_selected": True},
                {"stageable": False},
            ):
                self.assertNotIn(self.action_type, dict(review_gallery.action_options(
                    bucket, self.photo_id, **restrictions,
                )))


class PhotoJunkTests(PhotoRetirementTests):
    action_type = "photo-junked"
    destination_root = "_junk"
    operation = "junking"

    def test_all_category_destinations_preserve_hierarchy_bytes_and_unregistered_state(self):
        for action_type, destination_root in (
            ("photo-junked", "_junk"), ("photo-retired", "_retired/photos"),
        ):
            with self.subTest(action_type=action_type):
                self.manifest["actions"][0]["type"] = action_type
                self.destination_root = destination_root
                self._assert_unregistered_round_trips()

    def _assert_unregistered_round_trips(self):
        for folder in (
            "Angels/Example", "Sisters/Example", "Models/Example", "Prospects/Example",
            "Potentials/Example", "Artists/Studio", "Artists/Studio/Example",
            "Various", "Various/Example",
        ):
            for bucket in ("Gallery", "Review"):
                with self.subTest(folder=folder, bucket=bucket):
                    source = self.root / folder / bucket.lower() / self.source.name
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_bytes(b"original photo bytes")
                    if self.source != source and self.source.exists():
                        self.source.unlink()
                    self.source = source
                    self.catalog.update(people={}, photos={}, actions=[])
                    action = self.manifest["actions"][0]
                    action.update(personFolder=folder, sourceBucket=bucket)
                    action.pop("personId", None)
                    self.destination = self.root / self.destination_root / folder / bucket.lower() / source.name
                    errors, plans = actions.validate_manifest(
                        self.manifest, self.root, self.catalog, pool_folder=folder,
                    )
                    self.assertEqual(errors, [])
                    self.assertEqual(plans[0]["destination"], self.destination)
                    batch, _ = self.apply()
                    self.assertEqual(self.destination.read_bytes(), b"original photo bytes")
                    record = self.catalog["actions"][-1]
                    self.assertEqual(record["contentSha256"], action["contentSha256"])
                    self.assertNotIn("personId", record)
                    self.assertEqual(self.catalog["people"], {})
                    self.assertEqual(metadata.validation_errors(self.catalog), [])
                    actions.undo_actions(
                        self.catalog, self.root, {}, "Various", batch_id=batch,
                        backup_fn=self.backup, save_fn=self.save,
                    )
                    self.assertEqual(self.catalog["people"], {})
                    self.assertTrue(source.is_file())
                    source.unlink()

    def test_artist_junk_cannot_reassign_to_another_artist_or_general_identity(self):
        action = self.manifest["actions"][0]
        action.update(personFolder="Artists/Studio")
        action.pop("personId")
        source = self.root / "Artists" / "Studio" / "review" / self.source.name
        source.parent.mkdir(parents=True)
        self.source.replace(source)
        for folder in ("Artists/Other", "Prospects/Other"):
            for action_type in ("photo-junked", "photo-retired", "match-accepted", "rejected-to-various"):
                with self.subTest(folder=folder, action_type=action_type):
                    decision = {
                        **action, "type": action_type, "destinationFolder": folder,
                        "destinationPersonId": "person_" + "b" * 32,
                    }
                    document = {**self.manifest, "actions": [decision]}
                    errors, _ = actions.validate_manifest(document, self.root, self.catalog)
                    self.assertTrue(errors)
                    self.assertTrue(source.exists())
        self.assertEqual(
            [kind for kind, _ in review_gallery.action_options(
                "Gallery", self.photo_id, folder="Artists/Studio",
            )],
            ["photo-retired", "photo-junked"],
        )

    def test_terminal_artist_and_various_options_keep_guards_and_reject_unsupported_ids(self):
        for folder in ("Artists/Studio", "Artists/Studio/Example", "Various"):
            for bucket in ("Gallery", "Review"):
                for restrictions in (
                    {"protected": True}, {"anchor": True}, {"workflow_selected": True},
                    {"stageable": False},
                ):
                    with self.subTest(folder=folder, bucket=bucket, restrictions=restrictions):
                        self.assertEqual(review_gallery.action_options(
                            bucket, self.photo_id, folder=folder, **restrictions,
                        ), [])
            self.assertEqual(review_gallery.action_options("Gallery", None, folder=folder), [])
            for action_type in ("photo-junked", "photo-retired"):
                for photo_id in (None, "", "photo:unsupported", "image_123456"):
                    with self.subTest(folder=folder, action_type=action_type, photo_id=photo_id):
                        decision = {
                            **self.manifest["actions"][0], "type": action_type,
                            "personFolder": folder, "photoId": photo_id,
                        }
                        decision.pop("personId")
                        errors, plans = actions.validate_manifest(
                            {**self.manifest, "actions": [decision]}, self.root, self.catalog,
                        )
                        self.assertTrue(errors)
                        self.assertEqual(plans, [])
        self.assertEqual(self.backups, [])
        self.assertTrue(self.source.exists())

    def test_base_and_flow_workflow_selections_refuse_apply_before_backup(self):
        for cfg in (
            {"photos": {"Example": self.source.name}},
            {"flows": {"ExampleFlow": {"photos": {"Example": self.source.name}}}},
        ):
            with self.subTest(cfg=cfg), self.assertRaisesRegex(ValueError, "active workspace workflow"):
                actions.apply_actions(
                    self.manifest, self.root, self.catalog, cfg, "Various",
                    backup_fn=self.backup, save_fn=self.save,
                )
        self.assertEqual(self.backups, [])
        self.assertTrue(self.source.exists())

    def test_gallery_anchor_and_workflow_conflicts_refused_in_both_orders(self):
        source = self.source.parent.parent / "gallery" / self.source.name
        source.parent.mkdir()
        self.source.replace(source)
        decision = {**self.manifest["actions"][0], "sourceBucket": "Gallery"}
        for action_type in ("anchor-added", "workflow-photo-selected"):
            for reverse in (False, True):
                with self.subTest(action_type=action_type, reverse=reverse):
                    choices = [decision, {**decision, "type": action_type}]
                    if reverse:
                        choices.reverse()
                    errors, _ = actions.validate_manifest(
                        {**self.manifest, "actions": choices}, self.root, self.catalog,
                    )
                    self.assertIn("same manifest", "\n".join(errors))
                    self.assertTrue(source.exists())

    def test_people_report_refuses_artists_but_explicit_artist_junk_manifest_remains_supported(self):
        likeness = review_gallery.likeness
        folder = self.root / "Artists" / "Studio"
        source = folder / "review" / self.source.name
        source.parent.mkdir(parents=True)
        self.source.replace(source)
        settings = likeness.settings({})
        cache = likeness.Cache(self.root / "cache.json")
        space = likeness.Space([], settings, mean=[0., 0.])
        catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
        before = copy.deepcopy(catalog)
        with mock.patch.object(
            likeness, "library_people", return_value=[("Artists/Studio", folder)]
        ), mock.patch.object(
            likeness, "status_of", return_value="Artists"
        ), mock.patch.object(likeness, "cleanup_hold", return_value=set()):
            with self.assertRaisesRegex(ValueError, "separate browser"):
                review_gallery.collect_items(
                    {}, settings, self.root, cache, space, catalog, include_artists=True,
                    embed=lambda _: {"v": [1., 0.], "px": 100, "faces": 1, "s": .95},
                )
        decision = {
            "type": "photo-junked", "photoId": metadata.photo_id_from_name(source.name),
            "contentSha256": metadata.content_sha256(source),
            "sourceBucket": "Review", "personFolder": "Artists/Studio",
        }
        errors, plans = actions.validate_manifest(
            {**self.manifest, "actions": [decision]}, self.root, catalog,
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            plans[0]["destination"], self.root / "_junk" / "Artists" / "Studio" / "review" / source.name,
        )
        self.assertEqual(catalog, before)
        self.assertEqual(source.read_bytes(), b"original photo bytes")
        self.assertFalse((self.root / "_junk").exists())


if __name__ == "__main__":
    unittest.main()
