#!/usr/bin/env python3
"""Tests for read-only likeness identity-core scoring."""
import contextlib
import io
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.art import likeness  # noqa: E402
from tools.art.likeness_library.audit import audit_person  # noqa: E402


class LikenessAuditTests(unittest.TestCase):
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

    def test_input_must_have_one_id_per_vector(self):
        with self.assertRaisesRegex(ValueError, "one entry per vector"):
            audit_person(np.array([[1.0, 0.0]]), [])

    def test_command_prints_lowest_score_first_without_moving_photos(self):
        class Photo:
            def __init__(self, name, vec):
                self.key = "Prospects/Sophie"
                self.name = name
                self.vec = vec
                self.path = pathlib.Path(name)

            def usable(self, _minimum):
                return True

        vectors = [[1.0, 0.0], [0.99, 0.01], [0.98, 0.02], [-1.0, 0.0]]
        photos = [
            Photo(f"sophie_image_{index}.jpg", np.asarray(vector))
            for index, vector in enumerate(vectors, 1)
        ]
        space = SimpleNamespace(photos=photos)
        args = SimpleNamespace(names=[], group=None, keep=0.25)
        output = io.StringIO()
        settings = {"odd": 0.15, "mixed": [], "minFace": 60}
        with mock.patch.object(likeness, "build", return_value=(None, settings, None, None, space)):
            with mock.patch.object(likeness.metadata, "load_catalog", return_value={"people": {}, "photos": {}}):
                with contextlib.redirect_stdout(output):
                    likeness.cmd_audit_core(args)
        rendered = output.getvalue()
        self.assertIn("No images are moved", rendered)
        self.assertIn("possible Prospect outlier; report only", rendered)
        rows = [line.strip() for line in rendered.splitlines() if "[" in line and "]" in line]
        self.assertIn("sophie_image_4.jpg", rows[0])


if __name__ == "__main__":
    unittest.main()
