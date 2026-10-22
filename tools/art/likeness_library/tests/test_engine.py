"""Focused tests for cached face data and identity-space operations."""

import pathlib
import sys
import tempfile
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools/art"))
sys.path.insert(0, str(ROOT / "tools/workflows"))

from likeness_library.engine import Cache, Photo, Space, cluster, human_rows, settings


class LikenessEngineTests(unittest.TestCase):
    def test_cache_reuses_content_hash_and_round_trips_embeddings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            photo = root / "photo.jpg"
            cache_path = root / "cache.json"
            photo.write_bytes(b"first")

            cache = Cache(cache_path)
            first_hash = cache.sha(photo)
            self.assertEqual(cache.sha(photo), first_hash)
            cache.emb[first_hash] = {"faces": 1, "v": [1.0, 0.0], "s": 0.95}
            cache.save()

            loaded = Cache(cache_path)
            self.assertEqual(
                loaded.emb[first_hash],
                {"faces": 1, "v": [1.0, 0.0], "s": 0.95},
            )
            photo.write_bytes(b"other")
            self.assertNotEqual(loaded.sha(photo), first_hash)

    def test_space_centers_vectors_and_excludes_source_side(self):
        photos = [
            Photo(pathlib.Path("prospect.jpg"), "Prospects", "One", "a", {
                "faces": 1, "v": [1.0, 0.0], "px": 100
            }),
            Photo(pathlib.Path("artist.jpg"), "Artists/Studio", "Person", "b", {
                "faces": 1, "v": [0.0, 1.0], "px": 100
            }),
            Photo(pathlib.Path("angel.jpg"), "Angels", "Ari", "c", {
                "faces": 1, "v": [0.8, 0.2], "px": 100
            }),
        ]
        configuration = settings({"likeness": {"minFace": 60}})
        space = Space(photos, configuration)

        self.assertEqual(
            space.keys,
            ["Angels/Ari", "Artists/Studio/Person", "Prospects/One"],
        )
        self.assertEqual(
            space.ranking(
                photos[0].vec,
                skip=photos[0],
                own="Prospects/One",
                source="Prospects/One",
            )[0][1],
            "Angels/Ari",
        )
        self.assertNotIn(
            "Artists/Studio/Person",
            [
                key
                for _, key in space.ranking(
                    photos[0].vec,
                    skip=photos[0],
                    own="Prospects/One",
                    source="Prospects/One",
                )
            ],
        )

    def test_average_linkage_and_human_face_filtering(self):
        vectors = np.array([[1.0, 0.0], [0.99, 0.01], [-1.0, 0.0]])
        self.assertEqual(len(cluster(vectors, 0.9)), 2)

        rows = [[0, 0, 1, 1, 0.95], [0, 0, 1, 1, 0.80]]
        self.assertEqual(human_rows(rows), [rows[0]])


if __name__ == "__main__":
    unittest.main()
