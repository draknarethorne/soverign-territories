"""Tests for photo/render identity composition and render embedding lookup."""

import pathlib
import sys
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools/art"))
sys.path.insert(0, str(ROOT / "tools/workflows"))

import comfy_workflows as cw
from likeness_library.engine import Photo
from likeness_library.identity import folder_core, identity, identity_vec, kind_of
from likeness_library.rendering import Renders


class IdentityTests(unittest.TestCase):
    def test_render_conflict_does_not_change_the_anchor_seed(self):
        photo = Photo(pathlib.Path("ari.jpg"), "Sisters", "Ari", "id", {"faces": 1})
        photo.vec = np.array([1.0, 0.0])
        space = types.SimpleNamespace(by_key={"Sisters/Ari": [photo]})
        renders = mock.Mock()
        renders.centroid.return_value = (np.array([0.0, 1.0]), 4)

        with mock.patch.object(cw, "photo_key", side_effect=lambda value: pathlib.Path(value).name):
            result = identity(
                space,
                {"photos": {"Ari": "ari.jpg"}},
                {},
                renders,
                "Sisters/Ari",
            )

        self.assertEqual(kind_of("Sisters/Ari"), "sister")
        self.assertTrue(result["conflict"])
        np.testing.assert_allclose(result["seed"], [1.0, 0.0])
        np.testing.assert_allclose(identity_vec(result["seed"], result), [1.0, 0.0])

    def test_folder_core_and_render_alignment(self):
        first = Photo(pathlib.Path("one.jpg"), "Angels", "Ari", "1", {"faces": 1})
        second = Photo(pathlib.Path("two.jpg"), "Angels", "Ari", "2", {"faces": 1})
        first.vec, second.vec = np.array([1.0, 0.0]), np.array([0.9, 0.1])
        space = types.SimpleNamespace(by_key={"Angels/Ari": [first, second]})

        photos, scores, core, centroid = folder_core(space, "Angels/Ari")

        self.assertEqual(photos, [first, second])
        self.assertEqual(len(scores), 2)
        self.assertEqual(len(core), 2)
        self.assertGreater(centroid[0], 0.9)
        np.testing.assert_allclose(identity_vec(centroid, {"r": centroid}), centroid)

    def test_render_embeddings_use_the_existing_face_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            (root / "Ari_Qwen_X_Pose_one.png").write_bytes(b"render")
            cache = types.SimpleNamespace(
                emb={"render-hash": {"v": [1.0, 0.0], "px": 100}},
                sha=mock.Mock(return_value="render-hash"),
                save=mock.Mock(),
            )
            space = types.SimpleNamespace(mean=np.zeros(2))
            with mock.patch.object(cw, "output_root", return_value=root):
                renders = Renders(
                    {"sharedOutput": str(root)},
                    cache,
                    mock.Mock(),
                    {"minFace": 60},
                    space,
                )

            centroid, core_size = renders.centroid("Ari", "sister")

        np.testing.assert_allclose(centroid, [1.0, 0.0])
        self.assertEqual(core_size, 1)
        cache.sha.assert_called_once()


if __name__ == "__main__":
    unittest.main()
