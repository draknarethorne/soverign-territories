#!/usr/bin/env python3
"""Tests for the local, read-only likeness review gallery."""
import pathlib
import tempfile
import unittest
import json
import hashlib
from types import SimpleNamespace
from unittest import mock

import numpy as np
from jsonschema import Draft7Validator

from tools.art import likeness
from tools.art.likeness_library import review_gallery


class ReviewGalleryTests(unittest.TestCase):
    def test_primary_reference_prefers_workflow_anchor_core_then_best_scored(self):
        def item(folder, name, *, score, bucket="Gallery", selected=False, anchor=False, state="Consistent"):
            return {
                "folder": folder,
                "name": name,
                "score": score,
                "bucket": bucket,
                "workflowSelected": selected,
                "identityAnchor": anchor,
                "state": state,
                "primaryReference": False,
                "referenceLabel": "",
            }

        items = [
            item("Prospects/Workflow", "gallery.jpg", score=0.9),
            item("Prospects/Workflow", "workflow.jpg", score=-0.5, bucket="Review", selected=True),
            item("Prospects/Anchor", "anchor-low.jpg", score=0.3, anchor=True),
            item("Prospects/Anchor", "anchor-high.jpg", score=0.7, anchor=True),
            item("Prospects/Core", "core-low.jpg", score=0.2, state="Core member"),
            item("Prospects/Core", "core-high.jpg", score=0.8, state="Core member"),
            item("Prospects/Provisional", "best.jpg", score=0.1),
            item("Prospects/Provisional", "outlier.jpg", score=-0.5),
            item("Prospects/Unscored", "unknown.jpg", score=None),
        ]
        review_gallery.assign_primary_references(items)
        references = [entry for entry in items if entry["primaryReference"]]
        self.assertEqual(
            {entry["folder"]: entry["name"] for entry in references},
            {
                "Prospects/Workflow": "workflow.jpg",
                "Prospects/Anchor": "anchor-high.jpg",
                "Prospects/Core": "core-high.jpg",
                "Prospects/Provisional": "best.jpg",
            },
        )
        self.assertEqual(
            {entry["referenceLabel"] for entry in references},
            {
                "Workflow-selected photo",
                "User-confirmed identity anchor",
                "Score-ranked provisional core member",
                "Score-ranked reference · provisional, not confirmed",
            },
        )

    def test_actions_are_location_aware_and_manifest_schema_is_versioned(self):
        gallery = review_gallery.action_options("Gallery", "photo:image_123")
        self.assertEqual(
            [action for action, _label in gallery],
            ["anchor-added", "photo-protected", "sent-to-review", "rejected-to-various"],
        )
        review = review_gallery.action_options("Review", "photo:image_123", protected=True)
        self.assertEqual(
            [action for action, _label in review],
            ["photo-unprotected", "rejected-to-various", "review-approved"],
        )
        self.assertEqual(
            review_gallery.action_options("Gallery", "photo:image_123", stageable=False),
            [],
        )
        self.assertTrue(review_gallery.action_folder_supported("Prospects/Sophie"))
        self.assertFalse(review_gallery.action_folder_supported("Artists/Example/Person"))
        self.assertFalse(review_gallery.action_folder_supported("Models/Legacy"))
        schema_path = review_gallery.ROOT / "data/art/_schema/likeness-action-manifest.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft7Validator(schema)
        manifest = {
            "manifestVersion": 1,
            "generatedAt": "2026-10-20T12:00:00Z",
            "source": "people-gallery-review",
            "actions": [{
                "type": "sent-to-review",
                "photoId": "photo:image_123",
                "contentSha256": "a" * 64,
                "sourceBucket": "Gallery",
                "personFolder": "Prospects/Sophie",
                "personId": "person_" + "b" * 32,
            }],
        }
        self.assertEqual(list(validator.iter_errors(manifest)), [])
        manifest["actions"][0]["sourceBucket"] = "Review"
        self.assertTrue(list(validator.iter_errors(manifest)))
        manifest["actions"][0]["sourceBucket"] = "Gallery"
        manifest["actions"][0]["contentSha256"] = "stale"
        self.assertTrue(list(validator.iter_errors(manifest)))

    def test_collection_scores_review_against_gallery_without_including_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp) / "Prospects" / "Sophie"
            gallery_dir, review_dir = folder / "gallery", folder / "review"
            gallery_dir.mkdir(parents=True)
            review_dir.mkdir()
            gallery_paths = [gallery_dir / f"sophie_image_{n}.jpg" for n in (111111, 222222, 333333)]
            review_path = review_dir / "sophie_image_444444.jpg"
            for path in gallery_paths + [review_path]:
                path.write_bytes(b"test photo")

            def photo(path, vector):
                record = {"faces": 1, "px": 100, "v": vector}
                return likeness.Photo(path, "Prospects", "Sophie", path.name, record)

            active = [
                photo(gallery_paths[0], [1.0, 0.0]),
                photo(gallery_paths[1], [0.99, 0.01]),
                photo(gallery_paths[2], [0.98, 0.02]),
            ]
            for item in active:
                item.vec = likeness.nz(item.raw)

            class Cache:
                def __init__(self):
                    self.emb = {}
                    self.saved = 0

                def sha(self, _path):
                    return "review-content"

                def save(self):
                    self.saved += 1

            cache = Cache()
            space = SimpleNamespace(
                photos=active,
                mean=np.zeros(2),
                ranking=lambda *_args, **_kwargs: [],
            )
            cfg = {"photos": {"Sophie": gallery_paths[0].name}}
            settings = {"minFace": 60, "odd": 0.15, "mixed": []}
            anchor_id = "photo:image_222222"
            data = {
                "people": {
                    "person_test": {
                        "id": "person_test",
                        "folder": "Prospects/Sophie",
                        "displayName": "Sophie",
                        "identityAnchors": [anchor_id],
                    }
                },
                "photos": {
                    anchor_id: {
                        "contentSha256": hashlib.sha256(gallery_paths[1].read_bytes()).hexdigest(),
                        "protected": False,
                    }
                },
            }
            original_data = json.loads(json.dumps(data))
            embedding = lambda _path: {"faces": 1, "px": 100, "v": [-1.0, 0.0]}
            with mock.patch.object(
                likeness, "library_people", return_value=[("Prospects/Sophie", folder)]
            ), mock.patch.object(
                likeness, "status_of", return_value="Prospects"
            ), mock.patch.object(
                likeness, "cleanup_hold", return_value=set()
            ), mock.patch.object(
                review_gallery.originals,
                "images",
                side_effect=lambda path: gallery_paths if path == gallery_dir else [review_path],
            ):
                items, _warnings = review_gallery.collect_items(
                    cfg, settings, pathlib.Path(tmp), cache, space, data, embed=embedding
                )

            review_item = next(item for item in items if item["bucket"] == "Review")
            gallery_item = next(item for item in items if item["bucket"] == "Gallery")
            selected_item = next(item for item in items if item["name"] == gallery_paths[0].name)
            anchor_item = next(item for item in items if item["name"] == gallery_paths[1].name)
            self.assertEqual(review_item["state"], "Review")
            self.assertLess(review_item["score"], 0)
            self.assertIn("never enters its core", review_item["reason"])
            self.assertEqual(review_item["photoId"], "photo:image_444444")
            self.assertEqual(
                review_item["contentSha256"],
                hashlib.sha256(review_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(len(gallery_item["contentSha256"]), 64)
            self.assertTrue(selected_item["workflowSelected"])
            self.assertTrue(selected_item["primaryReference"])
            self.assertEqual(selected_item["referenceLabel"], "Workflow-selected photo")
            self.assertTrue(anchor_item["identityAnchor"])
            self.assertFalse(anchor_item["primaryReference"])
            self.assertFalse(review_item["identityAnchor"])
            self.assertEqual(data, original_data)
            self.assertTrue(all(path.read_bytes() == b"test photo" for path in gallery_paths + [review_path]))
            self.assertTrue(review_item["stageable"])
            self.assertEqual(
                [action for action, _label in review_item["stageOptions"]],
                ["photo-protected", "rejected-to-various", "review-approved"],
            )
            self.assertEqual(cache.saved, 1)

    def test_render_is_local_lazy_filtered_and_bounded(self):
        items = [
            {
                "folder": f"Prospects/Person {index}",
                "group": "Prospects",
                "bucket": "Review" if index % 2 else "Gallery",
                "name": f"photo_{index}.jpg",
                "score": index / 1000,
                "state": "Review" if index % 2 else "Core member",
                "comparison": "provisional core",
                "reason": "report only",
                "best_other": "",
                "thumbnail": f"people_gallery_review_files/{index}.jpg",
                "href": f"file:///C:/library/photo_{index}.jpg",
            }
            for index in range(205)
        ]
        page = review_gallery.render_html(items, "now")
        self.assertIn("pageSize=100", page)
        self.assertIn('image.loading="lazy"', page)
        self.assertIn('id="bucket"', page)
        self.assertIn('id="mode"', page)
        self.assertIn('id="person"', page)
        self.assertIn('id="score-ceiling"', page)
        self.assertIn("function groupCards(items)", page)
        self.assertIn("function primaryFor(folder)", page)
        self.assertIn("if(reference) {", page)
        self.assertIn("if(!photos.some(item=>item.photoId===reference.photoId))", page)
        self.assertIn('sort.value==="high" ? b.score-a.score : a.score-b.score', page)
        self.assertIn('mode.value==="review"', page)
        self.assertIn('mode.value==="low"', page)
        self.assertIn('option value="review">Review queue', page)
        self.assertIn('option value="low">Low scores', page)
        self.assertIn('id="download"', page)
        self.assertIn("manifestVersion:1", page)
        self.assertIn("contentSha256:record.contentSha256", page)
        self.assertIn("file:///C:/library/photo_0.jpg", page)
        self.assertNotIn("https://", page)
        self.assertNotIn("data:image", page)
        self.assertIn("205", page)

    def test_render_escapes_untrusted_photo_and_warning_text(self):
        item = {
            "folder": "Prospects/Sophie",
            "group": "Prospects",
            "bucket": "Gallery",
            "name": "</script><script>alert(1)</script>",
            "score": None,
            "state": "Unscored",
            "comparison": "none",
            "reason": "safe",
            "best_other": "",
            "thumbnail": "people_gallery_review_files/photo.jpg",
            "href": "file:///C:/photo.jpg",
        }
        page = review_gallery.render_html([item], "now", ["<img src=x onerror=alert(1)>"])
        self.assertNotIn("</script><script>alert(1)", page)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)

    def test_thumbnail_cache_reuses_derivative_by_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = pathlib.Path(tmp) / "photo.jpg"
            source.write_bytes(b"photo")
            photo = SimpleNamespace(sha="abc123", path=source)
            item = {
                "folder": "Prospects/Sophie",
                "group": "Prospects",
                "bucket": "Gallery",
                "name": source.name,
                "score": 0.9,
                "state": "Core member",
                "comparison": "provisional core",
                "reason": "consistent",
                "best_other": "",
                "_photo": photo,
            }
            out = pathlib.Path(tmp) / "report"
            with mock.patch.object(review_gallery.people_gallery, "thumb_bytes", return_value=b"thumbnail") as thumb:
                first, _ = review_gallery.write_thumbnails([item], out)
                second, _ = review_gallery.write_thumbnails([item], out)
            self.assertEqual(thumb.call_count, 1)
            self.assertEqual(first[0]["thumbnail"], second[0]["thumbnail"])
            self.assertEqual(
                (out / first[0]["thumbnail"]).read_bytes(),
                b"thumbnail",
            )


if __name__ == "__main__":
    unittest.main()
