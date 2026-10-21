"""Tests for batch likeness calibration and folder diagnostics."""
import csv
import pathlib
import tempfile
import unittest

import numpy as np

from tools.art.likeness_library.diagnostics import collect_diagnostics, write_report


class Photo:
    def __init__(self, key, name, vec):
        self.key = key
        self.name = name
        self.vec = np.asarray(vec, dtype=float)


class Space:
    def __init__(self, folders):
        self.keys = sorted(folders)
        self.by_key = {
            key: [Photo(key, f"photo-{index}.jpg", vec) for index, vec in enumerate(vectors)]
            for key, vectors in folders.items()
        }
        self.person = [photo for photos in self.by_key.values() for photo in photos]

    def centroid(self, key, skip=None):
        vectors = [photo.vec for photo in self.by_key[key] if photo is not skip]
        if not vectors:
            return None
        mean = np.mean(vectors, axis=0)
        return mean / np.linalg.norm(mean)

    def ranking(self, vec, skip=None, own=None, source=None):
        return sorted(
            (
                (float(vec @ self.centroid(key, skip=skip if key == own else None)), key)
                for key in self.keys
                if self.centroid(key, skip=skip if key == own else None) is not None
            ),
            reverse=True,
        )

    def pair_matrix(self):
        centroids = {key: self.centroid(key) for key in self.keys}
        pairs = {
            (first, second): float(centroids[first] @ centroids[second])
            for index, first in enumerate(self.keys)
            for second in self.keys[index + 1:]
        }
        return centroids, pairs


class DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.space = Space({
            "Sisters/One": [[1, 0], [1, 0], [1, 0]],
            "Angels/Two": [[0, 1], [0, 1], [0, 1]],
            "Models/Three": [[-1, 0], [-1, 0], [-1, 0]],
            "Potentials/Four": [[0, -1], [0, -1]],
            "Artists/Hidden/Person": [[1, 0], [1, 0], [1, 0]],
        })
        self.settings = {"odd": 0.15, "assign": 0.4, "margin": 0.1}

    def test_calibration_and_active_folder_evidence_are_distinct(self):
        calibration, calibration_photos, folders, photos = collect_diagnostics(
            self.space, self.settings
        )

        self.assertEqual(calibration["eligible_photo_count"], 14)
        self.assertEqual(len(calibration_photos), 14)
        self.assertEqual(calibration["correct_top_rank"], 8)
        self.assertEqual([row["category"] for row in folders], [
            "Angels", "Models", "Potentials", "Sisters",
        ])
        self.assertEqual(sum(row["eligible"] for row in folders), 3)
        potential = next(row for row in folders if row["category"] == "Potentials")
        self.assertEqual(potential["verdict"], "not evaluated: fewer than 3 usable photos")
        self.assertEqual(len(photos), 9)
        self.assertTrue(all(row["folder_state"] == "agree" for row in photos))
        self.assertNotIn("Artists", {row["category"] for row in folders})

    def test_report_writes_linked_csv_evidence_and_refuses_overwrite(self):
        calibration, calibration_photos, folders, photos = collect_diagnostics(
            self.space, self.settings
        )
        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "diagnostics"
            paths = write_report(
                output, calibration, calibration_photos, folders, photos,
                {"load_seconds": 1.0, "score_seconds": 0.5, "total_seconds": 1.5},
            )
            self.assertEqual(set(paths), {
                "markdown", "folder_csv", "photo_csv", "calibration_csv",
                "calibration_photo_csv",
            })
            self.assertIn("folder-consistency-photos.csv", paths["markdown"].read_text(encoding="utf-8"))
            with paths["photo_csv"].open(encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 9)
            with paths["calibration_photo_csv"].open(encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 14)
            with self.assertRaises(FileExistsError):
                write_report(
                    output, calibration, calibration_photos, folders, photos,
                    {"load_seconds": 1.0, "score_seconds": 0.5, "total_seconds": 1.5},
                )


if __name__ == "__main__":
    unittest.main()
