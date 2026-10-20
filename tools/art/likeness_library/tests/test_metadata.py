#!/usr/bin/env python3
"""Tests for the tracked likeness metadata catalogue."""
import copy
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.art.likeness_library import metadata  # noqa: E402


class LikenessMetadataTests(unittest.TestCase):
    def setUp(self):
        self.valid = {
            "schemaVersion": 1,
            "people": {},
            "photos": {},
            "actions": [],
        }

    def test_checked_in_catalogue_loads(self):
        catalogue = metadata.load_catalog()
        self.assertEqual(catalogue["schemaVersion"], 1)
        self.assertEqual(catalogue["people"], {})

    def test_person_ids_are_opaque_and_unique(self):
        first = metadata.new_person_id()
        second = metadata.new_person_id()
        self.assertRegex(first, r"^person_[0-9a-f]{32}$")
        self.assertNotEqual(first, second)

    def test_photo_id_ignores_folder_prefix_and_scaled_suffix(self):
        first = metadata.photo_id_from_name("sophie_image_123456.jpg")
        second = metadata.photo_id_from_name("other_image_123456_944x1104.png")
        self.assertEqual(first, "photo:image_123456")
        self.assertEqual(first, second)
        self.assertIsNone(metadata.photo_id_from_name("not-an-original.png"))

    def test_content_hash_is_a_separate_stale_file_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "image.jpg"
            path.write_bytes(b"first")
            first = metadata.content_sha256(path)
            path.write_bytes(b"second")
            self.assertNotEqual(first, metadata.content_sha256(path))

    def test_person_and_photo_decisions_validate(self):
        photo_id = "photo:image_123456"
        person_id = "person_0123456789abcdef0123456789abcdef"
        self.valid["photos"][photo_id] = {"contentSha256": "a" * 64, "protected": True}
        self.valid["people"][person_id] = {
            "id": person_id,
            "displayName": "Sophie Lloyd",
            "folder": "Prospects/Sophie Lloyd",
            "folderHistory": [],
            "identityAnchors": [photo_id],
        }
        metadata.validate_catalog(self.valid)

    def test_anchor_must_resolve_to_registered_photo(self):
        person_id = "person_0123456789abcdef0123456789abcdef"
        self.valid["people"][person_id] = {
            "id": person_id,
            "displayName": "Sophie Lloyd",
            "folder": "Prospects/Sophie Lloyd",
            "folderHistory": [],
            "identityAnchors": ["photo:image_123456"],
        }
        with self.assertRaisesRegex(ValueError, "has no photo record"):
            metadata.validate_catalog(self.valid)

    def test_action_must_resolve_photo_and_person_references(self):
        self.valid["actions"].append({
            "id": "action_0123456789abcdef0123456789abcdef",
            "timestamp": "2026-10-20T10:00:00Z",
            "actor": "user",
            "type": "sent-to-review",
            "photoIds": ["photo:shot_20261020100000"],
            "personId": "person_0123456789abcdef0123456789abcdef",
        })
        with self.assertRaisesRegex(ValueError, "has no photo record"):
            metadata.validate_catalog(self.valid)

    def test_duplicate_action_ids_are_rejected(self):
        self.valid["photos"]["photo:image_123456"] = {
            "contentSha256": "a" * 64,
            "protected": False,
        }
        action = {
            "id": "action_0123456789abcdef0123456789abcdef",
            "timestamp": "2026-10-20T10:00:00Z",
            "actor": "user",
            "type": "sent-to-review",
            "photoIds": ["photo:image_123456"],
        }
        self.valid["actions"] = [action, copy.deepcopy(action)]
        with self.assertRaisesRegex(ValueError, "duplicate action id"):
            metadata.validate_catalog(self.valid)

    def test_action_timestamp_must_be_valid_datetime(self):
        self.valid["photos"]["photo:image_123456"] = {
            "contentSha256": "a" * 64,
            "protected": False,
        }
        self.valid["actions"].append({
            "id": "action_0123456789abcdef0123456789abcdef",
            "timestamp": "not-a-timestamp",
            "actor": "user",
            "type": "sent-to-review",
            "photoIds": ["photo:image_123456"],
        })
        with self.assertRaisesRegex(ValueError, "timestamp"):
            metadata.validate_catalog(self.valid)

    def test_photo_retirement_is_a_distinct_audited_action(self):
        self.valid["photos"]["photo:image_123456"] = {
            "contentSha256": "a" * 64,
            "protected": False,
        }
        self.valid["actions"].append({
            "id": "action_0123456789abcdef0123456789abcdef",
            "timestamp": "2026-10-20T10:00:00Z",
            "actor": "user",
            "type": "photo-retired",
            "photoIds": ["photo:image_123456"],
            "personId": "person_0123456789abcdef0123456789abcdef",
            "source": "Prospects/Sophie Lloyd/gallery",
            "destination": "_retired/photos/person_0123456789abcdef0123456789abcdef",
            "reason": "unusable photo",
        })
        self.valid["people"]["person_0123456789abcdef0123456789abcdef"] = {
            "id": "person_0123456789abcdef0123456789abcdef",
            "displayName": "Sophie Lloyd",
            "folder": "Prospects/Sophie Lloyd",
            "folderHistory": [],
            "identityAnchors": [],
        }
        metadata.validate_catalog(self.valid)

    def test_invalid_schema_shape_is_rejected(self):
        broken = copy.deepcopy(self.valid)
        del broken["photos"]
        with self.assertRaisesRegex(ValueError, "required property"):
            metadata.validate_catalog(broken)


if __name__ == "__main__":
    unittest.main()
