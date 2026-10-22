#!/usr/bin/env python3
"""Tests for read-only likeness identity-core scoring."""
import contextlib
import io
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.art import likeness  # noqa: E402
from tools.art.likeness_library.audit import audit_person  # noqa: E402


class AuditPhoto:
    def __init__(self, key, name, vec, path=None):
        self.key = key
        self.name = name
        self.vec = np.asarray(vec)
        self.path = pathlib.Path(path or name)

    def usable(self, _minimum):
        return True


class LikenessAuditTests(unittest.TestCase):
    def run_command(self, photos, catalog):
        space = SimpleNamespace(photos=photos)
        args = SimpleNamespace(names=[], group=None, keep=0.25)
        settings = {"odd": 0.15, "mixed": [], "minFace": 60}
        output = io.StringIO()
        with mock.patch.object(likeness, "build", return_value=(None, settings, None, None, space)):
            with mock.patch.object(likeness.metadata, "load_catalog", return_value=catalog):
                with contextlib.redirect_stdout(output):
                    likeness.cmd_audit_core(args)
        return output.getvalue()

    def test_provisional_core_orders_clear_outlier_below_core(self):
        vectors = np.array([[1.0, 0.0], [0.99, 0.01], [0.98, 0.02], [-1.0, 0.0]])
        result = audit_person(vectors, ["a", "b", "c", "d"])
        self.assertEqual(result["mode"], "provisional")
        self.assertEqual(set(result["core_indices"]), {0, 1, 2})
        self.assertLess(result["scores"][3], min(result["scores"][i] for i in result["core_indices"]))
        self.assertTrue(result["sufficient"])

    def test_anchor_is_trusted_and_seeds_the_provisional_core(self):
        vectors = np.array([[1.0, 0.0], [0.99, 0.01], [0.98, 0.02], [-1.0, 0.0]])
        result = audit_person(vectors, ["anchor", "b", "c", "d"], anchor_ids={"anchor"})
        self.assertEqual(result["mode"], "trusted")
        self.assertIn(0, result["anchor_indices"])
        self.assertIn(0, result["core_indices"])
        self.assertNotIn(3, result["core_indices"])

    def test_protected_only_photo_does_not_influence_core(self):
        vectors = np.array([[1.0, 0.0], [0.99, 0.01], [0.98, 0.02], [0.0, 1.0]])
        result = audit_person(vectors, ["a", "b", "c", "protected"], protected_ids={"protected"})
        self.assertEqual(set(result["core_indices"]), {0, 1, 2})
        self.assertEqual(result["protected_indices"], [3])
        self.assertLess(result["scores"][3], 0.1)

    def test_stale_and_ambiguous_metadata_decisions_are_not_applied(self):
        vectors = np.array([
            [1.0, 0.0],
            [0.99, 0.01],
            [1.0, 0.02],
            [0.98, 0.02],
            [0.97, 0.03],
        ])
        result = audit_person(
            vectors,
            ["stale", "ambiguous", "c", "d", "e"],
            anchor_ids={"stale", "ambiguous"},
            protected_ids={"stale", "ambiguous"},
            stale_ids={"stale"},
            ambiguous_ids={"ambiguous"},
        )
        self.assertEqual(result["anchor_indices"], [])
        self.assertEqual(result["protected_indices"], [])
        self.assertEqual(set(result["blocked_indices"]), {0, 1})
        self.assertEqual(set(result["core_indices"]), {2, 3, 4})

    def test_small_core_is_reported_as_insufficient(self):
        result = audit_person(np.array([[1.0, 0.0], [0.99, 0.01]]), ["a", "b"])
        self.assertFalse(result["sufficient"])

    def test_category_core_threshold_uses_leave_one_out_scores_and_keeps_singletons(self):
        vectors = np.array([[1.0, 0.0], [0.2, np.sqrt(0.96)]])
        lower = audit_person(
            vectors,
            ["a", "b"],
            minimum_core=1,
            core_minimum=0.15,
            seed_floor=0.15,
        )
        self.assertEqual(set(lower["core_indices"]), {0, 1})
        self.assertAlmostEqual(lower["scores"][0], 0.20, places=2)
        self.assertAlmostEqual(lower["scores"][1], 0.20, places=2)

        upper = audit_person(
            vectors,
            ["a", "b"],
            minimum_core=1,
            core_minimum=0.30,
            seed_floor=0.30,
        )
        self.assertEqual(len(upper["core_indices"]), 1)

        single = audit_person(
            np.array([[0.0, 1.0]]),
            ["single"],
            core_minimum=0.30,
        )
        self.assertEqual(single["core_indices"], [0])
        self.assertIsNone(single["scores"][0])

    def test_input_must_have_one_id_per_vector(self):
        with self.assertRaisesRegex(ValueError, "one entry per vector"):
            audit_person(np.array([[1.0, 0.0]]), [])

    def test_command_prints_lowest_score_first_without_moving_photos(self):
        vectors = [[1.0, 0.0], [0.99, 0.01], [0.98, 0.02], [-1.0, 0.0]]
        photos = [
            AuditPhoto("Prospects/Sophie", f"sophie_image_{index}.jpg", vector)
            for index, vector in enumerate(vectors, 1)
        ]
        rendered = self.run_command(photos, {"people": {}, "photos": {}})
        self.assertIn("No images are moved", rendered)
        self.assertIn("possible Prospect outlier; report only", rendered)
        rows = [line.strip() for line in rendered.splitlines() if "[" in line and "]" in line]
        self.assertIn("sophie_image_4.jpg", rows[0])

    def test_cropped_file_keeps_photo_id_but_stales_anchor_and_protection(self):
        person_id = "person_0123456789abcdef0123456789abcdef"
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "sophie_image_123456.jpg"
            path.write_bytes(b"uncropped photo")
            photo_id = likeness.metadata.photo_id_from_name(path.name)
            original_hash = likeness.metadata.content_sha256(path)
            path.write_bytes(b"cropped photo")
            self.assertEqual(likeness.metadata.photo_id_from_name(path.name), photo_id)
            self.assertNotEqual(likeness.metadata.content_sha256(path), original_hash)

            photos = [
                AuditPhoto("Prospects/Sophie", path.name, [-1.0, 0.0], path),
                AuditPhoto("Prospects/Sophie", "sophie_image_234567.jpg", [1.0, 0.0]),
                AuditPhoto("Prospects/Sophie", "sophie_image_345678.jpg", [0.99, 0.01]),
                AuditPhoto("Prospects/Sophie", "sophie_image_456789.jpg", [0.98, 0.02]),
            ]
            catalog = {
                "people": {
                    person_id: {
                        "id": person_id,
                        "displayName": "Sophie",
                        "folder": "Prospects/Sophie",
                        "folderHistory": [],
                        "identityAnchors": [photo_id],
                    }
                },
                "photos": {
                    photo_id: {"contentSha256": original_hash, "protected": True}
                },
            }
            rendered = self.run_command(photos, catalog)
            self.assertIn("stale metadata; anchor/protection ignored", rendered)
            self.assertIn("provisional core", rendered)
            self.assertTrue(path.is_file())
            self.assertEqual(path.read_bytes(), b"cropped photo")

    def test_changed_catalogue_folder_does_not_seed_the_old_folder(self):
        person_id = "person_0123456789abcdef0123456789abcdef"
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "sophie_image_123456.jpg"
            path.write_bytes(b"photo")
            photo_id = likeness.metadata.photo_id_from_name(path.name)
            photos = [
                AuditPhoto("Prospects/Sophie", path.name, [1.0, 0.0], path),
                AuditPhoto("Prospects/Sophie", "sophie_image_234567.jpg", [0.99, 0.01]),
                AuditPhoto("Prospects/Sophie", "sophie_image_345678.jpg", [0.98, 0.02]),
            ]
            catalog = {
                "people": {
                    person_id: {
                        "id": person_id,
                        "displayName": "Sophie",
                        "folder": "Prospects/Sophie New",
                        "folderHistory": ["Prospects/Sophie"],
                        "identityAnchors": [photo_id],
                    }
                },
                "photos": {
                    photo_id: {
                        "contentSha256": likeness.metadata.content_sha256(path),
                        "protected": False,
                    }
                },
            }
            rendered = self.run_command(photos, catalog)
        self.assertIn("Catalogue folder not found: Sophie -> Prospects/Sophie New", rendered)
        self.assertIn("no catalogue person record; this is a provisional audit", rendered)
        self.assertNotIn("trusted identity anchor", rendered)

    def test_duplicate_source_ids_are_ambiguous_in_the_full_command(self):
        person_id = "person_0123456789abcdef0123456789abcdef"
        photo_id = "photo:image_123456"
        photos = [
            AuditPhoto("Prospects/Sophie", "sophie_image_123456.jpg", [1.0, 0.0]),
            AuditPhoto("Prospects/Sophie", "renamed_image_123456.png", [0.99, 0.01]),
            AuditPhoto("Prospects/Sophie", "sophie_image_234567.jpg", [1.0, 0.01]),
            AuditPhoto("Prospects/Sophie", "sophie_image_345678.jpg", [0.99, 0.02]),
            AuditPhoto("Prospects/Sophie", "sophie_image_456789.jpg", [0.98, 0.02]),
        ]
        catalog = {
            "people": {
                person_id: {
                    "id": person_id,
                    "displayName": "Sophie",
                    "folder": "Prospects/Sophie",
                    "folderHistory": [],
                    "identityAnchors": [photo_id],
                }
            },
            "photos": {photo_id: {"contentSha256": "a" * 64, "protected": False}},
        }
        rendered = self.run_command(photos, catalog)
        self.assertIn("duplicate stable photo ID; excluded from core and catalogue decisions", rendered)
        self.assertNotIn("trusted identity anchor", rendered)


if __name__ == "__main__":
    unittest.main()
