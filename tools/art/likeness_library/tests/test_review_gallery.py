#!/usr/bin/env python3
"""Tests for the local, read-only likeness review gallery."""
import pathlib
import copy
import tempfile
import unittest
import json
import hashlib
from types import SimpleNamespace
from unittest import mock

import numpy as np
from jsonschema import Draft7Validator
from PIL import Image

from tools.art import likeness
from tools.art.likeness_library.cross_reference import score_band
from tools.art.likeness_library import engine
from tools.art.likeness_library import review_gallery


class ReviewGalleryTests(unittest.TestCase):
    def test_report_output_is_validated_before_catalog_or_collection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory) / "library"
            cfg = {"storageRoots": {"reports": "operations/reports"}}
            with mock.patch.object(review_gallery.likeness, "build",
                                   return_value=(cfg, {}, root, None, None)), \
                    mock.patch.object(review_gallery.metadata, "load_catalog",
                                      side_effect=RuntimeError("catalog boundary")) as catalog:
                for output in (root / "Various" / "gallery", root.parent / "outside", "..\\outside"):
                    with self.subTest(output=output), self.assertRaises(ValueError):
                        review_gallery.main(["--out", str(output)])
                catalog.assert_not_called()
                with mock.patch.object(review_gallery.likeness.cw, "storage_output_path",
                                       wraps=review_gallery.likeness.cw.storage_output_path) as resolve:
                    with self.assertRaisesRegex(RuntimeError, "catalog boundary"):
                        review_gallery.main(["--out", "custom"])
                    resolve.assert_called_once_with(cfg, "reports", "custom", root=root)
            self.assertFalse(root.exists())

    def test_exact_alignment_is_the_lossless_crop_passed_to_sface(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            models = root / "model-cache" / "models"
            models.mkdir(parents=True)
            (models / "face_detection_yunet_2023mar.onnx").write_bytes(b"detector")
            (models / "face_recognition_sface_2021dec.onnx").write_bytes(b"recognizer")
            source = root / "prepared-final.png"
            source.write_bytes(b"final prepared source")
            aligned = np.arange(60, dtype=np.uint8).reshape((4, 5, 3))
            seen = {}

            class Detector:
                def setInputSize(self, _size):
                    pass

                def setScoreThreshold(self, _threshold):
                    pass

                def detect(self, _image):
                    row = [0, 0, 20, 20] + [0] * 10 + [0.99]
                    return None, np.asarray([row], dtype=float)

            class Recognizer:
                def alignCrop(self, _image, _face):
                    return aligned

                def feature(self, crop):
                    seen["feature"] = crop
                    return np.asarray([np.r_[1.0, np.zeros(127)]])

            def encode(_extension, crop):
                seen["encoded"] = crop.copy()
                return True, np.frombuffer(b"png" + crop.tobytes(), dtype=np.uint8)

            cv2 = SimpleNamespace(
                __version__="test-opencv",
                IMREAD_COLOR=1,
                imdecode=lambda _raw, _mode: np.zeros((100, 100, 3), dtype=np.uint8),
                imencode=encode,
            )
            embedder = engine.Embedder(root / "model-cache")
            embedder.configure_evidence(root / "library" / "_likeness" / "general" / "face-evidence")
            embedder.det, embedder.rec = Detector(), Recognizer()
            embedder.model_provenance, embedder.model_id = embedder._model_identity(cv2)
            with mock.patch.dict("sys.modules", {"cv2": cv2}):
                result = embedder(source)

            evidence = result["alignmentEvidence"]
            target = embedder.evidence_root / evidence["artifact"]
            self.assertIs(seen["feature"], aligned)
            np.testing.assert_array_equal(seen["encoded"], seen["feature"])
            self.assertEqual(target.read_bytes(), b"png" + aligned.tobytes())
            self.assertEqual(evidence["sourceSha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(evidence["alignmentSha256"], hashlib.sha256(target.read_bytes()).hexdigest())
            self.assertFalse(embedder.needs_alignment_evidence(result, source))

    def test_read_only_embedding_does_not_persist_exact_crop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = root / "source.png"
            source.write_bytes(b"source")
            evidence_root = root / "_likeness" / "general" / "face-evidence"
            embedder = engine.Embedder(root / "model-cache")
            embedder.configure_evidence(evidence_root)
            crop = np.ones((3, 3, 3), dtype=np.uint8)
            embedder.model_id = "a" * 64
            embedder.model_provenance = {"recognizer": {"name": "SFace"}}
            cv2 = SimpleNamespace(
                __version__="test-opencv",
                IMREAD_COLOR=1,
                imdecode=lambda _raw, _mode: np.zeros((100, 100, 3), dtype=np.uint8),
                imencode=lambda _extension, _image: (True, np.frombuffer(b"png", dtype=np.uint8)),
            )
            detector = SimpleNamespace(
                setInputSize=lambda _size: None,
                setScoreThreshold=lambda _threshold: None,
                detect=lambda _image: (None, np.asarray([[0, 0, 20, 20] + [0] * 10 + [0.99]])),
            )
            recognizer = SimpleNamespace(
                alignCrop=lambda _image, _face: crop,
                feature=lambda _aligned: np.asarray([np.r_[1.0, np.zeros(127)]]),
            )
            embedder.det, embedder.rec = detector, recognizer
            with likeness.domains.activate("general", read_only=True), mock.patch.dict("sys.modules", {"cv2": cv2}):
                result = embedder(source)
            self.assertEqual(result["alignmentEvidence"]["state"], "read-only-not-persisted")
            self.assertFalse(evidence_root.exists())

    def test_legacy_cache_entry_is_recomputed_and_saved_with_alignment_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = root / "Prospects" / "Example" / "gallery" / "photo.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"prepared source")
            cache = engine.Cache(root / "_likeness" / "general" / "cache.json")
            digest = cache.sha(source)
            cache.emb[digest] = {
                "faces": 1, "s": 0.95, "v": [1.0] * 128, "box": [0.2, 0.2, 0.4, 0.4], "px": 30,
            }

            class RefreshingEmbedder:
                calls = 0

                def needs_alignment_evidence(self, data, _path):
                    return "alignmentEvidence" not in data

                def __call__(self, _path):
                    self.calls += 1
                    return {
                        "faces": 1, "s": 0.95, "v": [0.5] * 128,
                        "box": [0.2, 0.2, 0.4, 0.4], "px": 30,
                        "alignmentEvidence": {"state": "persisted", "sourceSha256": "source-bound"},
                    }

            embedder = RefreshingEmbedder()
            with mock.patch.object(
                engine.cw, "photo_folders", return_value=[("Prospects", "Example", source.parent.parent)]
            ), likeness.domains.activate("general"):
                engine.read_library({}, root, cache, embedder, {"mixed": [], "pool": []}, progress=False)

            saved = json.loads(cache.path.read_text(encoding="utf-8"))
            self.assertEqual(embedder.calls, 1)
            self.assertEqual(saved["emb"][digest]["alignmentEvidence"]["state"], "persisted")
            self.assertEqual(saved["emb"][digest]["v"], [0.5] * 128)

    def test_gallery_links_only_verified_source_and_crop_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = root / "Prospects" / "Example" / "gallery" / "photo.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"source image")
            out = root / "_reports" / "library"
            evidence_root = root / "_likeness" / "general" / "face-evidence"
            evidence_root.mkdir(parents=True)
            source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
            model = {
                "detector": {
                    "name": "YuNet", "file": "yunet.onnx", "sha256": "b" * 64,
                },
                "recognizer": {
                    "name": "SFace", "file": "sface.onnx", "sha256": "c" * 64,
                },
                "opencv": "test",
                "alignment": "FaceRecognizerSF.alignCrop",
            }
            model_id = hashlib.sha256(
                json.dumps(model, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            crop = b"lossless aligned crop"
            artifact = f"{source_sha}-{model_id}.png"
            (evidence_root / artifact).write_bytes(crop)
            crop_sha = hashlib.sha256(crop).hexdigest()
            photo = likeness.Photo(source, "Prospects", "Example", "cache-key", {
                "faces": 1,
                "alignmentEvidence": {
                    "state": "persisted", "sourceSha256": source_sha, "modelId": model_id,
                    "artifact": artifact, "artifactSha256": crop_sha, "alignmentSha256": crop_sha,
                    "model": model,
                    "width": 5, "height": 4,
                },
            })
            evidence = review_gallery.alignment_evidence(photo, root, out)
            self.assertEqual(evidence["state"], "verified")
            self.assertEqual(evidence["sourceSha256"], source_sha)
            self.assertNotIn("base64", json.dumps(evidence).lower())
            (evidence_root / artifact).write_bytes(b"tampered")
            self.assertEqual(review_gallery.alignment_evidence(photo, root, out)["state"], "invalid")

    def test_render_navigation_and_exact_source_deep_link_are_available(self):
        page = review_gallery.render_html([], "now")
        self.assertIn('>Rendering</a>', page)
        self.assertIn('generate.href=generationIndex+"?source="+encodeURIComponent(r.generationSource)', page)
        self.assertIn('generate.textContent="Generate / Test"', page)
        self.assertIn('id="generation-index" type="application/json">"../../_generation/index.html"</script>', page)

    def test_render_deep_link_tracks_custom_report_depth(self):
        page = review_gallery.render_html([], "now", reports_prefix="../../../")
        self.assertIn('id="generation-index" type="application/json">"../../../../_generation/index.html"</script>', page)

    def test_identity_header_separates_evidence_and_existing_actions(self):
        page = review_gallery.render_html([], "now")
        for label, kind in (("Reference photo", "identity-reference"),
                            ("Identity details", "identity-details"),
                            ("Manual actions", "identity-actions")):
            self.assertIn(f'panel("{label}","{kind}")', page)
        self.assertIn('referencePanel.append(card(reference,true))', page)
        self.assertNotIn('if(!photos.some(item=>item.photoId===reference.photoId))', page)
        self.assertIn('label.append(select); actionsPanel.append(label)', page)
        self.assertIn('label.append(scope,input,stage,cancel,status);actionsPanel.append(label)', page)
        self.assertIn('detailsPanel.append(details)', page)
        self.assertIn('fact("Fixed cast slot"', page)
        self.assertIn('fact("Current person name"', page)
        self.assertIn('fact("Original person name"', page)
        self.assertIn('" (filters and page limit apply)"', page)
        self.assertIn('if(info.identityProtected&&!confirm(', page)
        self.assertIn('if(staged.size||others)', page)
        self.assertIn("No supported identity action is available", page)

    def test_card_use_guidance_is_shared_and_not_an_assignment_rule(self):
        page = review_gallery.render_html([], "now")
        guidance = json.loads(page.split(
            '<script id="card-use-guidance" type="application/json">'
        )[1].split("</script>")[0])
        self.assertEqual(guidance, review_gallery.gallery_chrome.CARD_USE_GUIDANCE)
        self.assertEqual(set(guidance), {"Potentials", "Prospects", "Models"})
        self.assertIn("Not a rarity rule or automatic assignment.", page)

    def test_location_grouping_is_separate_from_filtering_and_sorting(self):
        page = review_gallery.render_html([], "now")
        self.assertIn(
            '<label>Grouping <select id="grouping"><option value="mixed">Mixed</option>'
            '<option value="split">Split Gallery / Review</option></select></label>', page,
        )
        self.assertIn("function appendPhotoGroups(container,items)", page)
        self.assertIn('["Gallery","Review"].map(bucket=>[bucket,items.filter(item=>item.bucket===bucket)])', page)
        self.assertIn("appendPhotoGroups(section,photos)", page)
        self.assertIn("appendPhotoGroups(grid,page)", page)
        self.assertIn("const page=visible.slice(0,shown)", page)
        self.assertIn('article.classList.add("review-photo")', page)
        self.assertIn("scoreCeiling,grouping]", page)
        self.assertNotIn('grouping.addEventListener("change",()=>staged.clear()', page)

    def test_category_first_destinations_keep_folder_keys_and_staging_guards(self):
        page = review_gallery.render_html([], "now")
        self.assertIn('"Destination category for "+r.name', page)
        self.assertIn('"Destination identity for "+r.name', page)
        self.assertIn("folder!==r.folder&&item.personId", page)
        self.assertIn("folder.startsWith(destinationCategory.value", page)
        self.assertIn('new Option(folder.slice(folder.indexOf("/")+1),folder)', page)
        self.assertIn("destinationFolder:destination.value", page)
        self.assertIn("destinationPersonId:records.find(item=>item.folder===destination.value)?.personId", page)
        self.assertIn("destinationCategory.addEventListener", page)
        self.assertIn('restoreDestination();destinationControls.hidden=action.value!=="match-accepted"', page)
        self.assertIn("Apply or cancel the standalone identity rename before staging photo actions.", page)
        self.assertIn("Stage identity protection separately from photo actions for that identity.", page)

    def test_person_protection_export_is_separate_from_photo_decisions(self):
        person_id = "person_" + "a" * 32
        person = {"id": person_id, "protected": False}
        decision = review_gallery.person_protection_action("Models/Example", person_id, person)
        self.assertEqual(decision, {
            "type": "person-protected", "personId": person_id,
            "personFolder": "Models/Example", "expectedProtected": False,
        })
        schema = json.loads(
            (review_gallery.ROOT / "data" / "art" / "_schema" / "likeness-action-manifest.schema.json")
            .read_text(encoding="utf-8")
        )
        document = {
            "manifestVersion": 1, "generatedAt": "2026-10-22T09:30:00-05:00",
            "source": "people-gallery-review", "actions": [decision],
        }
        self.assertEqual(list(Draft7Validator(schema).iter_errors(document)), [])
        person["protected"] = True
        self.assertEqual(
            review_gallery.person_protection_action("Prospects/Example", person_id, person)["type"],
            "person-unprotected",
        )
        for folder in ("Angels/Example", "Sisters/Example", "Potentials/Example", "Various"):
            self.assertIsNone(review_gallery.person_protection_action(folder, person_id, person))
        self.assertIsNone(review_gallery.person_protection_action("Models/Example", None, None))
        person["mergedInto"] = "person_" + "b" * 32
        self.assertIsNone(review_gallery.person_protection_action("Models/Example", person_id, person))
        page = review_gallery.render_html([{
            "folder": "Models/Example", "group": "Models", "personProtectionAction": decision,
        }], "now")
        people_data = json.loads(page.split('<script id="people-data" type="application/json">')[1].split("</script>")[0])
        self.assertEqual(people_data["Models/Example"]["personProtectionAction"], decision)
        self.assertIn("actions.push(...stagedPeople.values())", page)
        self.assertIn("Identity protection (not photo protection)", page)

    def test_pool_root_is_not_a_person_and_holds_are_rendered_once(self):
        st = likeness.settings({})
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            with mock.patch.object(
                likeness.cw, "photo_folders",
                return_value=[("Various", "Various", root / "Various")],
            ):
                self.assertEqual(likeness.library_people({}, st, root), [])
            review = root / "Various" / "review"
            review.mkdir(parents=True)
            (review / "person_image_123456.jpg").write_bytes(b"photo")
            cache = likeness.Cache(root / "cache.json")
            space = likeness.Space([], st, mean=[0., 0.])
            with mock.patch.object(likeness, "library_people", return_value=[]), \
                    mock.patch.object(likeness, "cleanup_hold", return_value=set()):
                items, _ = review_gallery.collect_items(
                    {}, st, root, cache, space,
                    {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
                    embed=lambda _: {"v": [1., 0.], "px": 100, "faces": 1, "s": .95},
                )
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["folder"], "Various")
            self.assertEqual(items[0]["state"], "Hold")
            self.assertTrue(items[0]["stageable"])
            self.assertEqual(
                [kind for kind, _ in items[0]["stageOptions"]], ["photo-retired", "photo-junked"],
            )
            self.assertFalse(items[0]["scoreContext"]["coreMember"])
            page = review_gallery.render_html(
                [{key: value for key, value in item.items() if not key.startswith("_")} for item in items],
                "now",
            )
            self.assertIn('"Various"', page)
            self.assertIn('identityId.className="detail identity-id"', page)
            self.assertIn('"unassigned (Various hold)"', page)

    def test_closest_other_uses_each_photo_vector_and_skips_other_sides(self):
        photo = SimpleNamespace(
            usable=lambda min_face: min_face == 60,
            vec=np.array([1.0, 0.0]),
        )
        centroids = {
            "Prospects/Sophie": np.array([1.0, 0.0]),
            "Angels/Angelica": np.array([0.8, 0.6]),
            "Prospects/Ruby": np.array([0.6, 0.8]),
            "Artists/Studio/Person": np.array([1.0, 0.0]),
        }

        self.assertEqual(
            review_gallery.closest_other(photo, "Prospects/Sophie", centroids, 60),
            "Angels/Angelica (0.80)",
        )
        self.assertEqual(
            review_gallery.closest_other(photo, "Prospects/Sophie", centroids, 80),
            "",
        )

    def test_render_uses_supplied_category_policy(self):
        policy = copy.deepcopy(review_gallery.default_policy())
        policy["categoryOrder"].insert(3, "Demons")
        policy["categoryPolicies"]["Demons"] = copy.deepcopy(
            policy["categoryPolicies"]["Prospects"]
        )

        page = review_gallery.render_html([], "now", policy=policy)

        self.assertIn('"Demons"', page)
        self.assertIn('id="category-order"', page)

    def test_three_photo_matches_are_score_ranked_bounded_and_deterministic(self):
        photo = SimpleNamespace(usable=lambda minimum: minimum == 60, vec=np.array([1., 0.]))
        vectors = {
            "Prospects/Self": np.array([1., 0.]),
            "Models/Beth": np.array([.8, .6]),
            "Angels/Alice": np.array([.8, .6]),
            "Potentials/Cara": np.array([.7, np.sqrt(.51)]),
            "Sisters/Dana": np.array([.6, .8]),
            "Artists/Studio/Other": np.array([1., 0.]),
        }
        matches = review_gallery.closest_matches(photo, "Prospects/Self", vectors, 60)
        self.assertEqual([row["folder"] for row in matches], [
            "Angels/Alice", "Models/Beth", "Potentials/Cara",
        ])
        self.assertEqual(matches[0], {
            "folder": "Angels/Alice", "category": "Angels", "name": "Alice", "score": .8,
        })
        self.assertEqual(review_gallery.closest_matches(photo, "Prospects/Self", vectors, 80), [])
        page = review_gallery.render_html([{
            "folder": "Prospects/Self", "group": "Prospects", "bucket": "Review",
            "closestMatches": matches,
        }], "now")
        data = json.loads(page.split('<script id="review-data" type="application/json">')[1].split("</script>")[0])
        self.assertEqual(data[0]["closestMatches"], matches)
        self.assertIn("similarity evidence, not routing decisions", page)

    def test_review_explains_approval_protection_and_policy_core_eligibility(self):
        policy = review_gallery.default_policy()["categoryPolicies"]["Angels"]
        context = review_gallery.score_context(
            SimpleNamespace(usable=lambda _: True, px=100, faces=1),
            bucket="Review", core_size=4, core_mode="trusted", core_member=False,
            sufficient=True, min_face=60, group="Angels", keep=.3, odd=.15,
            category_policy=policy,
        )
        details = "\n".join(context["details"])
        self.assertIn("changes location only", details)
        self.assertIn("Protect photo does not approve a Review photo", details)
        self.assertIn("unless it is also a valid anchor", details)
        self.assertIn(f"{policy['identityCoreMinimumSimilarity']:.2f} similarity threshold", details)
        self.assertIn("not the displayed Review score alone", details)
        self.assertFalse(context["coreMember"])

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
            ["anchor-added", "photo-protected", "sent-to-review", "rejected-to-various", "match-accepted", "photo-retired", "photo-junked"],
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
        self.assertIn(
            ("workflow-photo-selected", "Select as workflow photo"),
            review_gallery.action_options(
                "Gallery", "photo:image_123", workflow_photo=True
            ),
        )
        self.assertTrue(review_gallery.action_folder_supported("Prospects/Sophie"))
        self.assertTrue(review_gallery.action_folder_supported("Artists/Example/Person"))
        self.assertTrue(review_gallery.action_folder_supported("Models/Legacy"))
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
                review_gallery,
                "closest_other",
                return_value="Angels/Camaris (0.46)",
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
            self.assertEqual(review_item["personId"], "person_test")
            self.assertEqual(review_item["scoreContext"]["facePixels"], 100)
            self.assertEqual(review_item["scoreContext"]["coreSize"], 3)
            self.assertFalse(review_item["scoreContext"]["coreMember"])
            self.assertEqual(review_item["best_other"], "Angels/Camaris (0.46)")
            self.assertEqual(gallery_item["best_other"], "Angels/Camaris (0.46)")
            self.assertTrue(any("Review photos are excluded from the core" in detail
                                for detail in review_item["scoreDetails"]))
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
                ["photo-protected", "rejected-to-various", "review-approved", "match-rejected", "match-accepted", "photo-retired", "photo-junked"],
            )
            self.assertEqual(cache.saved, 1)

    def test_closest_other_uses_each_photo_vector_and_excludes_ineligible_sources(self):
        photo = SimpleNamespace(
            usable=lambda min_face: min_face == 60,
            vec=np.array([1.0, 0.0]),
        )
        centroids = {
            "Prospects/Sophie": np.array([1.0, 0.0]),
            "Angels/Angelica": np.array([0.8, 0.6]),
            "Prospects/Ruby": np.array([0.6, 0.8]),
            "Artists/Studio/Person": np.array([1.0, 0.0]),
        }

        self.assertEqual(
            review_gallery.closest_other(photo, "Prospects/Sophie", centroids, 60),
            "Angels/Angelica (0.80)",
        )
        self.assertEqual(
            review_gallery.closest_other(photo, "Prospects/Sophie", centroids, 80),
            "",
        )

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
        self.assertIn('class="page-header"', page)
        self.assertIn('class="header-side"', page)
        self.assertIn('class="score-legend"', page)
        self.assertIn("205 photos", page)
        self.assertIn("pageSize=100", page)
        self.assertIn('image.loading="lazy"', page)
        self.assertIn('id="bucket"', page)
        self.assertIn('id="mode"', page)
        self.assertIn('id="person"', page)
        self.assertIn('id="group"', page)
        self.assertIn('id="card-size"', page)
        self.assertIn('id="framing"', page)
        self.assertIn('class="filter-controls"', page)
        self.assertIn('class="search-control"', page)
        self.assertIn('placeholder="folder, filename, reason"', page)
        self.assertIn('class="filter-options"', page)
        self.assertIn('class="sort-controls"', page)
        self.assertIn('<span class="count" id="count"></span>', page)
        self.assertLess(page.index('<span class="count" id="count"></span>'), page.index(">Order <select"))
        self.assertLess(page.index(">Order <select"), page.index("Low-score cutoff"))
        self.assertIn("function fillPeople()", page)
        self.assertIn('new URLSearchParams(location.search).get("person")', page)
        self.assertIn('option value="identity">Core identity first', page)
        self.assertIn('option value="high">Highest identity score', page)
        self.assertIn('fill(group,categoryOrder.filter', page)
        self.assertIn('new Map(categoryOrder.map', page)
        self.assertIn("const folderOrder=new Map()", page)
        self.assertIn("image.dataset.head=r.thumbnailHead", page)
        self.assertIn("photo-grid", page)
        self.assertIn('id="score-ceiling"', page)
        self.assertIn("function groupCards(items)", page)
        self.assertIn("function primaryFor(folder)", page)
        self.assertIn("if(reference) {", page)
        self.assertIn("referencePanel.append(card(reference,true))", page)
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

    def test_render_shows_deduplicated_person_classification_and_full_rankings(self):
        item = {
            "folder": "Models/Freya",
            "group": "Models",
            "bucket": "Gallery",
            "name": "freya.jpg",
            "photoId": "photo:image_123",
            "personId": "person_123",
            "identityProtected": True,
            "score": 0.8,
            "scoreContext": {
                "coreSize": 4,
                "coreMode": "provisional",
                "coreMember": True,
                "facePixels": 120,
                "faceCount": 1,
            },
            "scoreDetails": [
                "Face gate: 60px minimum; this image has a 120px face and 1 detected face(s).",
                "Score method: leave this photo out when it is a core member.",
            ],
            "state": "Core member",
            "comparison": "provisional core",
            "reason": "consistent",
            "best_other": "",
            "identityMatches": [
                {"key": "Angels/Camaris", "category": "Angels", "name": "Camaris", "score": 0.51},
            ],
            "thumbnail": "people_gallery_review_files/freya.jpg",
            "href": "file:///C:/library/freya.jpg",
        }

        page = review_gallery.render_html([item], "now")

        self.assertIn('id="people-data"', page)
        self.assertIn('"Models/Freya"', page)
        self.assertIn("category-models", page)
        self.assertIn("Full library likeness rankings", page)
        self.assertIn('"identityProtected": true', page)
        self.assertIn('badge-protected-identity', page)
        self.assertIn("score-yellow", page)
        self.assertIn("Closest by category:", page)
        self.assertIn('link.href="people_gallery_review.html?"+query.toString()', page)
        self.assertIn('["Sisters", "Angels", "Models", "Prospects", "Potentials", "Artists"]', page)
        self.assertIn('r.photoId.replace(/^photo:/,"").replace(/^image_/,"")', page)
        self.assertIn('r.personId||(r.folder==="Various"?"unassigned (Various hold)":"not catalogued")', page)
        self.assertIn("Core size: \"+r.scoreContext.coreSize+\" photos", page)
        self.assertIn('provisional · no trusted anchors', page)
        self.assertIn('r.folder.split("/").slice(1).join("/")', page)
        self.assertIn('r.bucket==="Gallery"?"Gallery photo":"Review photo"', page)
        self.assertIn('faceLink.title="Open face crop"', page)
        self.assertIn('summary.textContent="Scoring & action details"', page)
        self.assertIn('list.className="detail-list"', page)
        self.assertNotIn('r.scoreContext.coreMember?" · in core"', page)
        self.assertIn("Scoring & action details", page)

    def test_review_category_hierarchy_is_shared_by_sections_and_rankings(self):
        self.assertEqual(
            review_gallery.SECTIONS,
            ("Sisters", "Angels", "Models", "Prospects", "Potentials", "Artists"),
        )
        self.assertEqual(review_gallery.GROUP_ORDER, review_gallery.SECTIONS)
        self.assertEqual(score_band(0.55), "green")
        self.assertEqual(score_band(0.30), "yellow")
        self.assertEqual(score_band(0.15), "orange")
        self.assertEqual(score_band(0.149), "red")

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
            from likeness_library import derivatives, verification_reads
            source = pathlib.Path(tmp) / "Person" / "gallery" / "photo.jpg"
            source.parent.mkdir(parents=True)
            Image.new("RGB", (800, 1000), "white").save(source)
            photo = SimpleNamespace(sha="abc123", path=source, box=(0.3, 0.2, 0.25, 0.25))
            derivatives.maintain(source, photo.box, 250, apply=True)
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
            first, _ = review_gallery.write_thumbnails([item], out)
            before = {path.name: path.read_bytes()
                      for path in (out / "people_gallery_review_files").glob("*.jpg")}
            with verification_reads.session(pathlib.Path(tmp)):
                second, _ = review_gallery.write_thumbnails([item], out)
            self.assertEqual(first, second)
            self.assertEqual(before, {path.name: path.read_bytes()
                                     for path in (out / "people_gallery_review_files").glob("*.jpg")})
            self.assertEqual(first[0]["thumbnail"], second[0]["thumbnail"])
            self.assertEqual(first[0]["thumbnailHead"], second[0]["thumbnailHead"])
            self.assertEqual(first[0]["thumbnailFace"], second[0]["thumbnailFace"])
            self.assertIn("photo_chest_", first[0]["thumbnail"])
            self.assertIn("photo_head_", first[0]["thumbnailHead"])
            self.assertIn("photo_face_", first[0]["thumbnailFace"])
            self.assertEqual(first[0]["derivativeDiagnostics"], [])
            self.assertEqual(len(list((out / "people_gallery_review_files").glob("*.jpg"))), 3)
            with Image.open(out / first[0]["thumbnailFace"]) as face:
                self.assertEqual(face.size, (320, 320))

    def test_failed_content_seal_does_not_publish_review_or_history(self):
        from likeness_library import verification_reads
        scratch = pathlib.Path(__file__).resolve().parents[4] / "tmp"
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            root = pathlib.Path(tmp)
            out = root / "_reports" / "library"
            out.mkdir(parents=True)
            report = out / "people_gallery_review.html"
            history = out / "intake_runs.html"
            report.write_bytes(b"existing review")
            history.write_bytes(b"existing history")
            native = root / "source.bin"
            native.write_bytes(b"original")
            cfg = {"storageRoots": {"reports": "_reports"}}
            index = SimpleNamespace(history_html=lambda: "new history")

            def mutate(_items, _out, _work):
                verification_reads.sha256(native)
                native.write_bytes(b"modified")
                return [], out / "people_gallery_review_files"

            with mock.patch.object(review_gallery.likeness, "build",
                                   return_value=(cfg, {}, root, None, None)), \
                    mock.patch.object(review_gallery.metadata, "load_catalog", return_value={}), \
                    mock.patch.object(review_gallery, "collect_items", return_value=([], [])), \
                    mock.patch.object(review_gallery.preparation_provenance, "build_index", return_value=index), \
                    mock.patch.object(review_gallery, "write_thumbnails", side_effect=mutate), \
                    self.assertRaisesRegex(ValueError, "content changed"):
                review_gallery.main(["--root", str(root)])
            self.assertEqual(report.read_bytes(), b"existing review")
            self.assertEqual(history.read_bytes(), b"existing history")


if __name__ == "__main__":
    unittest.main()
