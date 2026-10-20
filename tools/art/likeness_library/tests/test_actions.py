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
        self.catalog = {"people": {}, "photos": {}, "actions": []}
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


if __name__ == "__main__":
    unittest.main()
