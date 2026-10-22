"""Recoverable photo retirement uses the common staged transaction boundary."""
import contextlib
import copy
import io
import json
import pathlib
import tempfile
import unittest

from tools.art.likeness_library import actions, metadata, review_gallery


class PhotoRetirementTests(unittest.TestCase):
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
                "type": "photo-retired", "photoId": self.photo_id, "personId": self.person_id,
                "personFolder": "Prospects/Example", "sourceBucket": "Review",
                "contentSha256": metadata.content_sha256(self.source),
            }],
        }
        self.destination = (
            self.root / "_retired" / "photos" / "Prospects" / "Example"
            / "review" / self.source.name
        )
        self.backups = []

    def save(self, updated):
        self.catalog.clear()
        self.catalog.update(copy.deepcopy(updated))

    def backup(self, *_):
        self.backups.append(copy.deepcopy(self.catalog))
        return "verified-backup"

    def apply(self, **kwargs):
        return actions.apply_actions(
            self.manifest, self.root, self.catalog, {}, "Various",
            backup_fn=self.backup, save_fn=self.save, **kwargs,
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
        self.assertEqual(record["type"], "photo-retired")
        self.assertEqual(record["photoIds"], [self.photo_id])
        self.assertEqual(record["destination"], "_retired/photos/Prospects/Example/review/" + self.source.name)
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
        self.assertIn("before retirement", "\n".join(errors))
        self.catalog["photos"].clear()
        self.catalog["people"][self.person_id]["identityAnchors"] = [self.photo_id]
        errors, _ = actions.validate_manifest(self.manifest, self.root, self.catalog)
        self.assertIn("before retirement", "\n".join(errors))
        self.catalog["people"][self.person_id]["identityAnchors"] = []
        errors, _ = actions.validate_manifest(
            self.manifest, self.root, self.catalog, chosen_ids={self.photo_id},
        )
        self.assertIn("active workspace workflow", "\n".join(errors))
        self.assertEqual(self.backups, [])

    def test_duplicate_conflicting_and_protection_actions_refused_in_both_orders(self):
        for action_type in ("photo-retired", "sent-to-review", "photo-protected", "photo-unprotected"):
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
            self.assertIn("photo-retired", dict(options))
            self.assertIn("_retired/photos", dict(options)["photo-retired"])
            for restrictions in (
                {"protected": True}, {"anchor": True}, {"workflow_selected": True},
                {"stageable": False},
            ):
                self.assertNotIn("photo-retired", dict(review_gallery.action_options(
                    bucket, self.photo_id, **restrictions,
                )))


if __name__ == "__main__":
    unittest.main()
