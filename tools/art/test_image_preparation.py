"""Source-preserving, sandbox-only preparation comparison regressions."""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock
from urllib.parse import unquote
from html.parser import HTMLParser

import numpy as np
from PIL import Image, ImageCms, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import image_preparation as preparation  # noqa: E402
import preparation_junk  # noqa: E402


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        self.targets += [value for key, value in attrs if key in ("href", "src")]


class PreparationTests(unittest.TestCase):
    def setUp(self):
        # Published v16 reports must remain verifiable after the recipe changes.
        for patch in (
            mock.patch.object(preparation, "CURRENT", "preparation-comparison-v16"),
            mock.patch.object(preparation, "STEPS", preparation.pipeline.STEPS),
            mock.patch.dict(preparation.RECIPE, {"id": "preparation-comparison-v16"}),
            mock.patch.object(preparation.pipeline, "recommended_candidates",
                              preparation.pipeline.processing_candidates),
        ):
            patch.start()
            self.addCleanup(patch.stop)
        (ROOT / "tmp").mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="preparation-tests-", dir=ROOT / "tmp")
        self.root = pathlib.Path(self.tmp.name) / "Sovereign Territories Sandbox" / "Working"
        base = pathlib.Path(self.tmp.name)
        self.cfg = preparation.cw.load_cfg()
        self.cfg["paths"].update({
            "productionRoot": str(base / "production"),
            "sandboxWorkingRoot": str(self.root),
            "inputsRoot": str(base / "inputs"),
            "outputRoot": str(base / "outputs"),
            "modelCacheRoot": str(base / "models"),
        })
        self.cfg.update({
            "installsRoot": str(base / "installs"),
            "sharedInput": str(base / "shared-input"),
            "sharedOutput": str(base / "shared-output"),
            "photos": {},
        })
        config = mock.patch.object(preparation.cw, "load_cfg", return_value=self.cfg)
        config.start()
        self.addCleanup(config.stop)
        self.output = self.root / "_reports" / "preparation" / "pilot"
        self.photo = self.put("Angels/Fixed Slot/gallery/old_name_image_123.jpg")
        (self.root / ".likeness-library.json").write_text('{"curation":"unchanged"}', encoding="utf-8")
        self.before = self.source_tree()
        self.real_detect_faces = preparation.preparation_geometry.detect_faces
        detector = mock.patch.object(preparation.preparation_geometry, "detect_faces",
                                     return_value=([[50., 40., 60., 70.]], "Usable test face."))
        detector.start()
        self.addCleanup(detector.stop)
        # The v16 models (Mask R-CNN, LaMa) never load in tests: no person by default, a flat deterministic fill.
        subjects = mock.patch.object(preparation.pipeline.subjects, "detect", return_value=None)
        self.subjects = subjects.start()
        self.addCleanup(subjects.stop)
        filler = mock.patch.object(preparation.pipeline.fill, "fill", side_effect=self.flat_fill)
        self.fill = filler.start()
        self.addCleanup(filler.stop)

    @staticmethod
    def flat_fill(image, mask):
        array = np.array(image)
        array[mask] = (128, 120, 110)
        return Image.fromarray(array)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, relative, image=None):
        photo = self.root / relative
        photo.parent.mkdir(parents=True, exist_ok=True)
        (image or Image.new("RGB", (160, 240), (90, 40, 20))).save(photo)
        return photo

    def source_tree(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file() and "_reports" not in p.parts}

    def call(self, *flags):
        errors = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors):
            code = preparation.main(["--root", str(self.root), "--out", str(self.output), *flags])
        self.errors = errors.getvalue()
        return code

    def manifest(self):
        return json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))

    def test_preview_and_missing_check_write_nothing(self):
        self.assertEqual(self.call("--dry-run"), 0)
        self.assertEqual(self.call(), 0)
        self.assertFalse(self.output.parent.exists())
        self.assertEqual(self.call("--check"), 1)
        self.assertFalse(self.output.parent.exists())
        self.assertEqual(self.source_tree(), self.before)

    def test_apply_retains_exact_bytes_and_never_changes_cast_or_catalogue(self):
        self.assertEqual(self.call("--apply"), 0)
        data = self.manifest()
        row = data["photos"][0]
        self.assertEqual(row["photoId"], "photo:image_123")
        self.assertEqual((self.output / row["retained"]).read_bytes(), self.photo.read_bytes())
        self.assertEqual(set(row["variants"]), {"control", "geometry", "denoise", "tone"})
        for variant in row["variants"].values():
            with Image.open(self.output / variant["path"]) as image:
                self.assertEqual(image.size, (160, 240))
            with Image.open(self.output / variant["padded"]) as image:
                self.assertEqual(image.size, (944, 1104))
                self.assertEqual(image.getpixel((0, 0)), preparation.originals.STUDIO_GREY)
        self.assertEqual(self.source_tree(), self.before)
        self.assertEqual(self.call("--check"), 0)

    def test_apply_repeat_and_check_do_not_rewrite_any_artifact(self):
        self.assertEqual(self.call("--apply"), 0)
        times = {p: p.stat().st_mtime_ns for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(self.call("--apply"), 0)
        self.assertEqual(self.call("--check"), 0)
        self.assertEqual(times, {p: p.stat().st_mtime_ns for p in self.output.rglob("*") if p.is_file()})

    def test_full_inventory_includes_cast_review_artists_and_excludes_generated(self):
        self.put("Sisters/Drakn/gallery/drakn_image_234.jpg")
        self.put("Artists/Painter/Person/review/person_image_345.png")
        self.put("Various/review/various_image_456.jpg")
        self.put("Potentials/Person/gallery_944x1104/generated.png")
        self.put("_archive/Sisters/Drakn/gallery/historical.png")
        paths = preparation.inventory(self.root)
        self.assertEqual(len(paths), 4)
        selected = preparation.sample(self.root, paths, 3)
        self.assertEqual([p.relative_to(self.root).parts[0] for p in selected],
                         ["Angels", "Sisters", "Artists"])
        self.assertEqual(set(preparation.sample(self.root, paths, 0)), set(paths))

    def test_source_folder_processes_only_direct_inputs_and_retains_them(self):
        first = self.put("Various/gallery/Screenshot_20261010_123318_Facebook.jpg")
        second = self.put("Various/gallery/photo.jpg")
        self.put("Various/review/not_selected.jpg")
        self.put("Various/gallery/nested/not_selected.jpg")
        before = self.source_tree()
        self.assertEqual(self.call("--source-folder", "Various\\gallery", "--limit", "0", "--dry-run"), 0)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.call("--source-folder", "Various\\gallery", "--limit", "0", "--apply"), 0)
        data = self.manifest()
        self.assertEqual(data["sourceFolder"], "Various/gallery")
        self.assertEqual({row["source"] for row in data["photos"]},
                         {p.relative_to(self.root).as_posix() for p in (first, second)})
        self.assertEqual(self.source_tree(), before)
        self.assertTrue(all(row["recommendation"]["use"] == "original" for row in data["photos"]))
        self.assertEqual(self.call("--source-folder", str(first.parent), "--limit", "0", "--apply"), 0)
        self.assertEqual(self.call("--check"), 0)
        self.assertEqual(self.call("--limit", "0", "--apply"), 1, "a different scope needs a new run")
        page = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn("What each image means", page)
        self.assertIn("Original (recommended)", page)
        self.assertIn("can remove part of the person", page)
        self.assertNotIn("a second crop that never cuts the person", page)

    def test_source_folder_rejects_escape_archive_and_generated_directories(self):
        for folder in ("..", "_archive/Angels/gallery", "Angels/Fixed Slot/gallery_944x1104",
                       "Various", "Various/missing/gallery"):
            self.assertEqual(self.call("--source-folder", folder, "--apply"), 1, folder)
        self.assertFalse(self.output.parent.exists())

    def test_round_robin_spreads_identity_folders_and_prefers_screenshots(self):
        self.put("Angels/Fixed Slot/gallery/fixed_shot_20261023120000.png")
        second = self.put("Angels/Second/gallery/second_image_567.jpg")
        selected = preparation.sample(self.root, preparation.inventory(self.root), 2)
        self.assertIn("_shot_", selected[0].name)
        self.assertEqual(selected[1], second)

    def test_rejects_production_relative_and_wrong_output_locations(self):
        with self.assertRaisesRegex(ValueError, "absolute"):
            preparation.locations(pathlib.Path("Working"), self.output)
        with self.assertRaisesRegex(ValueError, "sandbox"):
            preparation.locations(self.root.parent / "Source", self.output)
        with self.assertRaisesRegex(ValueError, "named run"):
            preparation.locations(self.root, self.photo.parent / "pilot")
        with self.assertRaisesRegex(ValueError, "named run"):
            preparation.locations(self.root, self.root / "_reports" / "preparation")

    def test_preparation_reports_follow_configured_reports_root(self):
        cfg = {"storageRoots": {"reports": "operations/reports"}}
        output = self.root / "operations" / "reports" / "preparation" / "configured-run"
        with mock.patch.object(preparation.cw, "load_cfg", return_value=cfg):
            self.assertEqual(preparation.locations(self.root, output), (self.root, output))
            with self.assertRaisesRegex(ValueError, "named run"):
                preparation.locations(self.root, self.output)

    def test_model_cache_paths_follow_workspace_configuration(self):
        cache = pathlib.Path(self.tmp.name) / "configured-model-cache"
        cfg = {"paths": {"modelCacheRoot": str(cache)}}
        with mock.patch.object(preparation.cw, "load_cfg", return_value=cfg):
            self.assertEqual(preparation.models.folder(), cache / "models")
            self.assertEqual(
                preparation.preparation_geometry.local_model(),
                cache / "models" / "face_detection_yunet_2023mar.onnx",
            )

    def test_failed_model_download_removes_partial_file(self):
        cache = pathlib.Path(self.tmp.name) / "configured-model-cache"
        cfg = {"paths": {"modelCacheRoot": str(cache)}}

        def partial_download(_url, target):
            pathlib.Path(target).write_bytes(b"partial")
            raise OSError("network interrupted")

        with mock.patch.object(preparation.cw, "load_cfg", return_value=cfg), \
                mock.patch.object(preparation.models.urllib.request, "urlretrieve",
                                  side_effect=partial_download):
            with self.assertRaisesRegex(OSError, "network interrupted"):
                preparation.models.path("person")
        self.assertFalse((cache / "models" /
                          (preparation.models.MODELS["person"]["file"] + ".part")).exists())

    def test_reparse_path_rejected_before_writes(self):
        actual = preparation.sandbox._is_reparse_point
        with mock.patch.object(preparation.sandbox, "_is_reparse_point",
                               side_effect=lambda p: p == self.root / "_reports" or actual(p)):
            self.assertEqual(self.call("--apply"), 1)
        self.assertFalse(self.output.parent.exists())
        self.assertEqual(self.source_tree(), self.before)

    def test_corrupt_input_is_archived_before_decode_and_error_is_explicit(self):
        self.photo.write_bytes(b"not a picture")
        original_decode = preparation.decode

        def checked_decode(payload):
            temporary_root = preparation.cw.storage_root(
                preparation.cw.load_cfg(), "temporary", root=self.root
            )
            preserved = list(temporary_root.glob(".preparation-*/run/originals/*"))
            self.assertEqual(preserved[0].read_bytes(), payload)
            return original_decode(payload)

        with mock.patch.object(preparation, "decode", side_effect=checked_decode):
            self.assertEqual(self.call("--apply"), 1)
        row = self.manifest()["photos"][0]
        self.assertEqual(row["outcome"], "unprocessable")
        self.assertEqual(row["variants"], {})
        self.assertGreater(len(row["diagnostics"]), 1)
        self.assertEqual((self.output / row["retained"]).read_bytes(), b"not a picture")
        self.assertEqual(self.call("--check"), 1)

    def test_render_failure_cleans_owned_staging_before_publication(self):
        with mock.patch.object(preparation, "rendered_rows", side_effect=OSError("render stopped")):
            self.assertEqual(self.call("--apply"), 1)
        temporary_root = preparation.cw.storage_root(
            preparation.cw.load_cfg(), "temporary", root=self.root
        )
        self.assertEqual(list(temporary_root.glob(".preparation-*")), [])
        self.assertFalse(self.output.exists())
        self.assertEqual(self.source_tree(), self.before)

    def test_publish_failure_cleans_owned_staging_without_replacing_output(self):
        with mock.patch.object(preparation.os, "rename", side_effect=OSError("publish stopped")):
            self.assertEqual(self.call("--apply"), 1)
        temporary_root = preparation.cw.storage_root(
            preparation.cw.load_cfg(), "temporary", root=self.root
        )
        self.assertEqual(list(temporary_root.glob(".preparation-*")), [])
        self.assertFalse(self.output.exists())

    def test_transparency_is_held_not_silently_composited(self):
        self.photo.unlink()
        self.put("Angels/Fixed Slot/gallery/transparent.png", Image.new("RGBA", (50, 50), (255, 0, 0, 20)))
        self.assertEqual(self.call("--apply"), 1)
        self.assertIn("transparent", self.manifest()["photos"][0]["diagnostics"][-1])

    def test_retained_bytes_survive_source_change_and_old_run_refuses_reuse(self):
        before = self.photo.read_bytes()
        self.assertEqual(self.call("--apply"), 0)
        retained = self.output / self.manifest()["photos"][0]["retained"]
        self.photo.write_bytes(b"changed")
        self.assertEqual(self.call("--check"), 1)
        self.assertEqual(self.call("--apply"), 1)
        self.assertEqual(retained.read_bytes(), before)
        self.assertEqual(self.photo.read_bytes(), b"changed")

    def test_edited_artifacts_never_overwritten_or_blessed(self):
        self.assertEqual(self.call("--apply"), 0)
        row = self.manifest()["photos"][0]
        for key in ("retained", "detail"):
            path = self.output / row[key]
            original = path.read_bytes()
            path.write_bytes(b"user-edited")
            self.assertEqual(self.call("--check"), 1)
            self.assertEqual(self.call("--apply"), 1)
            self.assertEqual(path.read_bytes(), b"user-edited")
            path.write_bytes(original)
        path = self.output / row["variants"]["tone"]["padded"]
        path.write_bytes(b"user-padded")
        self.assertEqual(self.call("--check"), 1)
        self.assertEqual(path.read_bytes(), b"user-padded")

    def test_recipe_inventory_and_selection_changes_require_new_run(self):
        self.assertEqual(self.call("--apply"), 0)
        with mock.patch.dict(preparation.RECIPE, {"id": "v2"}):
            self.assertEqual(self.call("--apply"), 1)
        self.assertEqual(self.call("--apply", "--limit", "1"), 1)
        self.put("Sisters/Drakn/gallery/new_image_789.jpg")
        self.assertEqual(self.call("--apply"), 1)

    def test_failure_cannot_publish_partial_run_or_change_sources(self):
        with mock.patch.object(preparation, "candidates", side_effect=OSError("render failed")):
            self.assertEqual(self.call("--apply"), 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.output.parent.iterdir()), [])
        self.assertEqual(self.source_tree(), self.before)

    def test_filter_failure_retains_original_and_reports_reason_without_blocking(self):
        with mock.patch.object(preparation.cv2, "bilateralFilter",
                               side_effect=preparation.cv2.error("filter failed")):
            self.assertEqual(self.call("--apply"), 0)
        row = self.manifest()["photos"][0]
        self.assertEqual(row["outcome"], "enhancement-failed")
        self.assertEqual(row["sourceTreatment"], "original-enhancement-failed")
        self.assertEqual(row["recommendation"]["use"], "original")
        self.assertIn("failed", row["recommendation"]["reason"])
        self.assertEqual(set(row["variants"]), {"control", "geometry"})
        self.assertIn("filter failed", " ".join(row["diagnostics"]))
        self.assertEqual(self.source_tree(), self.before)
        self.assertEqual(self.call("--check"), 0)
        self.assertIn("original-enhancement-failed",
                      (self.output / "index.html").read_text(encoding="utf-8"))

    def test_source_race_is_detected_before_publication(self):
        render = preparation.render_photo

        def changed(*args):
            result = render(*args)
            self.photo.write_bytes(b"concurrent change")
            return result

        with mock.patch.object(preparation, "render_photo", side_effect=changed):
            self.assertEqual(self.call("--apply"), 1)
        self.assertFalse(self.output.exists())

    def test_exif_orientation_and_icc_control_are_explicit(self):
        image = Image.new("RGB", (40, 60), (90, 50, 20))
        exif = Image.Exif()
        exif[274] = 6
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", exif=exif)
        self.assertEqual(preparation.decode(buffer.getvalue()).size, (60, 40))
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", icc_profile=profile)
        result = preparation.decode(buffer.getvalue())
        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.info, {}, "do not leak generated ICC timestamps or copied EXIF into candidates")
        for _, candidate in preparation.candidates(result):
            self.assertEqual(candidate.info, {})

    def test_file_decode_and_streamed_image_writes_preserve_exact_evidence(self):
        image = Image.new("RGB", (80, 120), (24, 48, 96))
        source_bytes = io.BytesIO()
        image.save(source_bytes, format="PNG")
        source = self.root / "source.png"
        source.write_bytes(source_bytes.getvalue())
        self.assertEqual(preparation.decode_file(source).tobytes(),
                         preparation.decode(source_bytes.getvalue()).tobytes())

        output = self.root / "streamed.png"
        with mock.patch.object(preparation.io, "BytesIO",
                               side_effect=AssertionError("image output must stream to disk")):
            output_hash = preparation.save_image(output, image, "PNG")
        self.assertEqual(output_hash, preparation.sha_file(output))
        self.assertEqual(output_hash, preparation.sha(output.read_bytes()))

    def test_pixel_change_metric_is_chunked_and_channel_averaged(self):
        control = Image.new("RGB", (2, 2), (0, 0, 0))
        changed = control.copy()
        changed.putpixel((0, 0), (3, 3, 3))
        self.assertEqual(preparation.mean_absolute_pixel_change(control, changed), 0.75)
        self.assertIsNone(preparation.mean_absolute_pixel_change(control, Image.new("RGB", (1, 1))))

    def test_profiled_controls_are_byte_reproducible_without_metadata(self):
        image = Image.new("RGB", (40, 60), (90, 50, 20))
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", icc_profile=profile)
        payload = buffer.getvalue()
        outputs = []
        for _ in range(2):
            control = preparation.decode(payload)
            result = io.BytesIO()
            control.save(result, format="PNG")
            outputs.append(result.getvalue())
        self.assertEqual(outputs[0], outputs[1])

    def test_reel_overlay_fixed_crop_is_proposal_only_and_control_never_changes(self):
        self.photo.unlink()
        image = Image.new("RGB", (400, 900), (90, 40, 20))
        image.paste((0, 0, 0), (0, 830, 400, 853))
        image.paste((255, 255, 255), (0, 868, 400, 900))
        source = self.put("Sisters/Drakn/gallery/drakn_shot_20261023120000.png", image)
        self.assertTrue(preparation.screens.is_reel_ui(image))
        self.assertEqual(self.call("--apply"), 0)
        row = self.manifest()["photos"][0]
        self.assertEqual(row["outcome"], "compared-overlay")
        self.assertEqual(row["sourceTreatment"], "cropped-border-overlay-unremoved")
        self.assertEqual(row["recommendation"]["use"], "second-crop", "the screen-wide app bar is cropped, not filled")
        self.assertIn("No pixels are invented", row["recommendation"]["reason"])
        self.assertEqual(row["processing"]["clutter"][0]["action"], "cropped")
        self.assertIn("does not block", " ".join(row["diagnostics"]))
        page = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn("cropped-border-overlay-unremoved", page)
        self.assertNotIn("overlay-held", page)
        with Image.open(self.output / row["variants"]["control"]["path"]) as result:
            self.assertEqual(result.size, image.size)
            self.assertEqual(result.tobytes(), image.tobytes())
        self.assertEqual(source.read_bytes(), (self.output / row["retained"]).read_bytes())
        self.assertEqual(row["geometry"]["box"], [0, 0, 400, 870])
        self.assertEqual(row["geometry"]["uiCropBox"], list(preparation.screens.clean_box(image.size)))
        self.assertIn("ui-crop-proposal", row["variants"])
        self.assertIn("may remove hair", row["geometry"]["uiCropAssessment"])

    def test_upstream_geometry_filters_use_border_crop_and_recommend_actual_asset(self):
        image = Image.new("RGB", (160, 240), "black")
        image.paste((90, 40, 20), (10, 20, 148, 216))
        self.photo.unlink()
        self.put("Angels/Fixed Slot/gallery/bordered.png", image)
        actual = preparation.candidates
        sizes = []

        def filtered(prepared):
            sizes.append(prepared.size)
            yield from actual(prepared)

        with mock.patch.object(preparation, "candidates", side_effect=filtered):
            self.assertEqual(self.call("--apply"), 0)
        row = self.manifest()["photos"][0]
        self.assertEqual(row["geometry"]["box"], [8, 18, 150, 218])
        self.assertEqual(sizes, [(142, 200)])
        self.assertEqual(row["sourceTreatment"], "cropped-border")
        self.assertEqual(row["recommendation"]["use"], "geometry")
        self.assertEqual(row["variants"]["geometry"]["size"], [142, 200])
        self.assertIsNone(row["variants"]["geometry"]["meanAbsolutePixelChange"])
        self.assertEqual(self.call("--check"), 0)
        page = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn(row["variants"]["geometry"]["path"], page)

    def test_border_detection_noop_on_flat_images_hair_edge_text_and_thin_strips(self):
        geometry = preparation.preparation_geometry
        for color in ("black", "white", (90, 40, 20)):
            image = Image.new("RGB", (100, 150), color)
            self.assertEqual(geometry.border_box(image), (0, 0, 100, 150))
        image = Image.new("RGB", (100, 150), (90, 40, 20))
        draw = ImageDraw.Draw(image)
        draw.ellipse((20, -30, 80, 60), fill="black")
        draw.text((5, 2), "overlay", fill="white")
        self.assertEqual(geometry.border_box(image), (0, 0, 100, 150))
        image.paste("white", (0, 0, 100, 4))
        self.assertEqual(geometry.border_box(image), (0, 0, 100, 150))
        image.paste("black", (0, 0, 100, 40))
        self.assertEqual(geometry.border_box(image), (0, 0, 100, 150), "broad flat areas are ambiguous")

    def test_border_detection_accepts_jpeg_noise_and_preserves_inner_pixels(self):
        image = Image.new("RGB", (200, 300), (4, 4, 4))
        image.paste((90, 40, 20), (0, 24, 200, 300))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)
        decoded = preparation.decode(buffer.getvalue())
        box = preparation.preparation_geometry.border_box(decoded)
        self.assertTrue(18 <= box[1] <= 22, box)
        self.assertEqual((box[0], box[2], box[3]), (0, 200, 300))
        self.assertEqual(decoded.crop(box).getpixel((100, 30)), decoded.getpixel((100, 30 + box[1])))

    def test_overlay_over_hair_is_not_cropped_away_or_claimed_repaired(self):
        image = Image.new("RGB", (400, 900), (90, 40, 20))
        draw = ImageDraw.Draw(image)
        draw.ellipse((80, 0, 320, 200), fill="black")
        draw.text((130, 10), "overlay over hair", fill="white")
        image.paste("black", (0, 830, 400, 853))
        image.paste("white", (0, 868, 400, 900))
        draw.point((0, 899), fill=(90, 40, 20))
        row = {"geometry": preparation.preparation_geometry.plan(image), "diagnostics": [], "outcome": "compared",
               "eligibility": {"faces": [], "reason": "No guarded face for this isolated geometry test"}}
        variants = dict(preparation.prepared_candidates(image, row))
        self.assertEqual(row["geometry"]["box"], [0, 0, 400, 900])
        self.assertEqual(variants["geometry"].tobytes(), image.tobytes())
        self.assertEqual(variants["ui-crop-proposal"].size,
                         (352, round(900 * .71) - round(900 * .105)))
        self.assertIn("Overlaid graphics remain", row["geometry"]["uiCropAssessment"])

    def test_v4_manifest_remains_valid_but_v5_requires_geometry(self):
        self.assertEqual(self.call("--apply"), 0)
        data = self.manifest()
        row = data["photos"][0]
        del row["geometry"]
        del row["variants"]["geometry"]
        with self.assertRaisesRegex(ValueError, "missing geometry"):
            preparation.validate(data)
        data["recipe"]["id"] = "preparation-comparison-v4"
        preparation.validate(data)

    def test_border_crop_filter_failure_retains_last_safe_cleanup(self):
        image = Image.new("RGB", (160, 240), "white")
        image.paste((90, 40, 20), (0, 20, 160, 240))
        self.photo.unlink()
        self.put("Angels/Fixed Slot/gallery/bordered.png", image)
        with mock.patch.object(preparation.cv2, "bilateralFilter",
                               side_effect=preparation.cv2.error("filter failed")):
            self.assertEqual(self.call("--apply"), 0)
        row = self.manifest()["photos"][0]
        self.assertTrue(row["geometry"]["changed"])
        self.assertEqual(row["recommendation"]["use"], "geometry")
        self.assertEqual(row["processing"]["final"], "geometry")
        self.assertEqual(self.call("--check"), 0)

    def test_processing_trace_has_three_summary_views_and_skipped_reasons(self):
        self.assertEqual(self.call("--apply"), 0)
        row = self.manifest()["photos"][0]
        processing = row["processing"]
        self.assertEqual(processing["cleanup"], "control")
        self.assertEqual(processing["final"], "control")
        self.assertEqual([s["name"] for s in processing["steps"]], list(preparation.STEPS))
        self.assertEqual([s["status"] for s in processing["steps"]],
                         ["skipped", "skipped", "skipped", "skipped", "attempted-rejected", "attempted-rejected"])
        self.assertTrue(all(s["reason"] for s in processing["steps"]))
        page = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn("1. Original", page)
        self.assertIn("2. Recommended after crop / eraser", page)
        self.assertIn("3. Final recommended source for 944x1104", page)
        self.assertIn("Processing trace", page)

    def person(self, size, box):
        width, height = size
        mask = np.zeros((height, width), dtype=bool)
        mask[box[1]:box[3], box[0]:box[2]] = True
        return {"box": list(box), "mask": mask, "people": 1, "dropped": 0}

    def test_options_table_lists_unselected_ui_proposal_and_mask_without_changing_trace(self):
        self.assertEqual(self.call("--apply"), 0)
        data = self.manifest()
        row = data["photos"][0]
        row["variants"]["ui-crop-proposal"] = dict(row["variants"]["control"])
        row["variants"]["eraser-mask"] = dict(row["variants"]["control"])
        before = json.dumps(row["processing"], sort_keys=True)
        page = preparation.report(data).decode("utf-8")
        trace = page.split("<tbody>", 1)[1].split("</tbody>", 1)[0]
        self.assertIn(">ui-crop-proposal</a>", trace)
        self.assertIn(">eraser-mask</a>", trace)
        self.assertIn("comparison-only", trace)
        self.assertIn("diagnostic", trace)
        self.assertIn("not a quality score", page)
        self.assertEqual(json.dumps(row["processing"], sort_keys=True), before)
        self.assertEqual(row["processing"]["final"], "control")

    def test_composition_frames_person_mask_and_feeds_enhancements(self):
        self.photo.unlink()
        self.put("Various/gallery/wide.png", Image.new("RGB", (1200, 800), "#8899aa"))
        self.subjects.side_effect = lambda image: self.person(image.size, (500, 60, 700, 800))
        with mock.patch.object(preparation.preparation_geometry, "detect_faces",
                               return_value=([[570., 80., 60., 70.]], "Test face")):
            self.assertEqual(self.call("--apply"), 0)
        row = self.manifest()["photos"][0]
        steps = {s["name"]: s for s in row["processing"]["steps"]}
        self.assertEqual(row["processing"]["subject"]["method"], "mask-rcnn")
        self.assertEqual(steps["composition"]["status"], "attempted-selected")
        self.assertEqual(row["recommendation"]["use"], "composition")
        self.assertEqual(steps["denoise"]["input"], "composition")
        width, height = row["variants"]["composition"]["size"]
        self.assertLess(width, 1200)
        self.assertAlmostEqual(width / height, 944 / 1104, delta=.02)
        self.assertEqual(self.call("--check"), 0)

    def test_composition_box_keeps_margin_and_skips_when_little_gained(self):
        box = preparation.pipeline.composition_box((1200, 800), [500, 60, 700, 800])
        self.assertLessEqual(box[0], 500 - 12)
        self.assertGreaterEqual(box[2], 700 + 12)
        self.assertEqual(box[3], 800, "the whole body below is kept")
        self.assertIsNone(preparation.pipeline.composition_box((400, 800), [10, 10, 390, 790]))

    def test_mask_that_stops_mid_leg_is_told_apart_from_feet(self):
        legs = np.zeros((800, 400), dtype=bool)
        legs[100:400, 100:300] = True
        legs[400:600, 150:250] = True  # two shins side by side, cut off by the detector
        feet = legs.copy()
        feet[600:640, 190:210] = True  # tapering to the feet
        self.assertTrue(preparation.pipeline.cut_off_below(legs))
        self.assertFalse(preparation.pipeline.cut_off_below(feet))
        self.assertFalse(preparation.pipeline.cut_off_below(np.zeros((10, 10), dtype=bool)))

    def clutter_part(self, kind, size, box):
        return preparation.pipeline.clutter.part(kind, self.person(size, box)["mask"], "test")

    def test_second_crop_trims_a_side_only_where_the_person_allows(self):
        size = (400, 800)
        person = self.person(size, (100, 100, 300, 780))
        icon = self.clutter_part("glyph", size, (360, 300, 390, 330))
        caption = self.clutter_part("glyph", size, (150, 700, 250, 730))
        box, removed, notes = preparation.pipeline.second_crop(
            size, [icon, caption], person, [[170., 120., 60., 70.]], (0, 0), screenshot=False)
        self.assertLess(box[2], 360)
        self.assertGreaterEqual(box[2], 300, "the person and its margin stay")
        self.assertEqual(box[3], 800, "a caption over the legs is left for the eraser, not cropped")
        self.assertEqual([id(i) for i in removed], [id(icon)])
        self.assertTrue(any(n.startswith("right") for n in notes))

    def test_screen_wide_app_bar_may_cut_legs_only_well_below_the_face(self):
        size = (400, 800)
        person = self.person(size, (100, 100, 300, 800))
        bar = self.clutter_part("ui-card", size, (0, 700, 400, 780))
        box, _, notes = preparation.pipeline.second_crop(
            size, [bar], person, [[170., 100., 60., 50.]], (0, 0), screenshot=True)
        self.assertLess(box[3], 700)
        self.assertIn("app bar", notes[0])
        box, _, _ = preparation.pipeline.second_crop(
            size, [bar], person, [[170., 500., 60., 50.]], (0, 0), screenshot=True)
        self.assertIsNone(box, "the bar is above 4.5 face heights under this face: never cut")
        box, _, _ = preparation.pipeline.second_crop(
            size, [bar], person, [[170., 100., 60., 50.]], (0, 0), screenshot=False)
        self.assertIsNone(box, "only screenshots have app bars")

    def test_clutter_finds_white_icon_and_corner_badge_and_spares_the_face(self):
        image = Image.new("RGB", (400, 800), (60, 80, 100))
        draw = ImageDraw.Draw(image)
        draw.rectangle((350, 300, 380, 330), fill="black")
        draw.rectangle((354, 304, 376, 326), fill="white")
        draw.ellipse((20, 650, 110, 740), fill=(230, 40, 170))
        draw.rectangle((180, 40, 220, 60), fill="black")
        draw.rectangle((184, 44, 216, 56), fill="white")
        parts, refused = preparation.pipeline.clutter.detect(image, [[170., 30., 60., 40.]], (0, 0))
        kinds = sorted(p["kind"] for p in parts)
        self.assertEqual(kinds, ["glyph", "logo"])
        logo = next(p for p in parts if p["kind"] == "logo")
        self.assertLessEqual(logo["box"][0], 20)
        self.assertGreaterEqual(logo["box"][2], 110, "the whole badge, not only its saturated core")
        self.assertEqual([p["kind"] for p in refused], ["glyph"], "a shape covering the face is refused")

    def test_badge_crossing_the_middle_is_found_whole(self):
        image = Image.new("RGB", (400, 800), (60, 80, 100))
        ImageDraw.Draw(image).ellipse((80, 620, 180, 720), fill=(230, 40, 170))
        logos = preparation.pipeline.clutter.emblems(np.asarray(image))
        self.assertEqual(len(logos), 1)
        self.assertGreaterEqual(logos[0]["box"][2], 180)

    def test_rendered_caption_over_the_body_is_clutter_on_screenshots_only(self):
        image = Image.new("RGB", (400, 800), (60, 80, 100))
        draw = ImageDraw.Draw(image)
        draw.rectangle((60, 640, 110, 670), fill="black")
        for x in range(64, 100, 12):
            draw.rectangle((x, 644, x + 6, 666), fill="white")
        body = np.zeros((800, 400), dtype=bool)
        body[100:800, 40:360] = True
        array = np.asarray(image)
        self.assertTrue(preparation.pipeline.clutter.glyphs(array, body, screenshot=True))
        self.assertFalse(preparation.pipeline.clutter.glyphs(array, body, screenshot=False))

    def test_earlier_recipes_keep_their_traced_step_order(self):
        legacy = preparation.legacy
        self.assertEqual(preparation.step_names("preparation-comparison-v14"), list(legacy.OLD_STEPS))
        self.assertEqual(preparation.step_names("preparation-comparison-v15"), list(legacy.V15_STEPS))
        traced_steps = ["first-crop", "eraser", "residual-crop", "reconstruction",
                        "composition", "denoise", "tone"]
        for version in range(17, 21):
            recipe_id = f"preparation-comparison-v{version}"
            self.assertEqual(preparation.step_names(recipe_id), traced_steps)
        self.assertEqual(preparation.step_names(preparation.RECIPE["id"]), list(preparation.STEPS))
        self.assertEqual(preparation.STEPS[:3], ("first-crop", "second-crop", "eraser"), "crop before any fill")

    def screenshot(self):
        image = Image.new("RGB", (400, 900), (90, 110, 150))
        image.paste("black", (0, 0, 400, 120))
        image.paste("black", (0, 700, 400, 869))
        image.paste("white", (0, 869, 400, 900))
        draw = ImageDraw.Draw(image)
        draw.rectangle((350, 440, 370, 460), fill="black")
        draw.rectangle((354, 444, 366, 456), fill="white")
        return image

    def run_screenshot(self, person_box):
        self.photo.unlink()
        self.put("Various/gallery/panels.png", self.screenshot())
        self.subjects.side_effect = lambda image: self.person(image.size, person_box)
        with mock.patch.object(preparation.preparation_geometry, "detect_faces",
                               return_value=([[140., 180., 60., 70.]], "One local test face")):
            code = self.call("--apply")
        return code, self.manifest()["photos"][0]

    def test_panel_crop_then_second_crop_removes_edge_icon_without_fill(self):
        code, row = self.run_screenshot((100, 20, 300, 580))
        self.assertEqual(code, 0)
        self.assertEqual(row["geometry"]["box"], [0, 120, 400, 700])
        steps = {s["name"]: s for s in row["processing"]["steps"]}
        self.assertEqual(steps["second-crop"]["status"], "attempted-selected")
        self.assertEqual(steps["second-crop"]["input"], "geometry")
        self.assertEqual(steps["eraser"]["status"], "skipped", "the crop removed the icon; nothing to repaint")
        self.assertEqual(steps["eraser"]["input"], "second-crop")
        self.fill.assert_not_called()
        self.assertLess(row["variants"]["second-crop"]["size"][0], 350)
        self.assertEqual(row["processing"]["clutter"][0]["action"], "cropped")
        self.assertEqual(self.call("--check"), 0)

    def test_icon_on_a_full_width_person_is_erased_and_recommended(self):
        code, row = self.run_screenshot((0, 0, 400, 580))
        self.assertEqual(code, 0)
        steps = {s["name"]: s for s in row["processing"]["steps"]}
        self.assertEqual(steps["second-crop"]["status"], "skipped")
        self.assertEqual(steps["eraser"]["status"], "attempted-selected")
        self.assertEqual(steps["eraser"]["input"], "geometry")
        self.assertEqual(row["recommendation"]["use"], "eraser")
        self.assertEqual(row["processing"]["final"], "eraser")
        self.assertEqual(row["variants"]["eraser-mask"]["size"], row["variants"]["geometry"]["size"])
        with Image.open(self.output / row["variants"]["eraser"]["path"]) as erased:
            self.assertNotEqual(erased.getpixel((360, 330)), (255, 255, 255), "the icon is repainted")
        self.assertIn("Cleaned (crop + LaMa eraser)", (self.output / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(self.call("--check"), 0)

    def test_fill_failure_keeps_the_last_crop_visibly(self):
        self.fill.side_effect = RuntimeError("no model")
        code, row = self.run_screenshot((0, 0, 400, 580))
        self.assertEqual(code, 0)
        steps = {s["name"]: s for s in row["processing"]["steps"]}
        self.assertEqual(steps["eraser"]["status"], "failed")
        self.assertIn("no model", steps["eraser"]["reason"])
        self.assertNotIn("eraser", row["variants"])
        self.assertEqual(row["recommendation"]["use"], "geometry")
        self.assertEqual(self.call("--check"), 0)

    def test_missing_person_detector_falls_back_to_face_frame_without_composition(self):
        self.subjects.side_effect = OSError("model download refused")
        self.assertEqual(self.call("--apply"), 0)
        row = self.manifest()["photos"][0]
        self.assertEqual(row["processing"]["subject"]["method"], "face-frame")
        self.assertIn("model download refused", row["processing"]["subject"]["note"])
        steps = {s["name"]: s for s in row["processing"]["steps"]}
        self.assertEqual(steps["composition"]["status"], "skipped")
        self.assertEqual(self.call("--check"), 0)

    def test_v16_manifest_rejects_eraser_without_its_mask(self):
        code, row = self.run_screenshot((0, 0, 400, 580))
        data = self.manifest()
        del data["photos"][0]["variants"]["eraser-mask"]
        with self.assertRaisesRegex(ValueError, "traced variants"):
            preparation.validate(data)

    def test_panel_crop_does_not_cut_into_detected_face_and_missing_model_is_explicit(self):
        module = preparation.preparation_geometry
        image = self.screenshot()
        base = module.border_box(image)
        box, _ = module.panel_box(image, [[140., 100., 60., 70.]], base)
        self.assertEqual(box[1], base[1], "top panel intersects guarded head region")
        with mock.patch.object(module, "local_model", return_value=pathlib.Path(self.tmp.name) / "absent.onnx"):
            with mock.patch.object(module.cv2, "FaceDetectorYN") as detector:
                faces, reason = self.real_detect_faces(image)
                self.assertIsNone(faces)
                self.assertIn("No download", reason)
                detector.create.assert_not_called()

    def test_trace_validation_rejects_wrong_lineage_order_and_final(self):
        self.assertEqual(self.call("--apply"), 0)
        data = self.manifest()
        processing = data["photos"][0]["processing"]
        processing["steps"][3]["input"] = "tone"
        with self.assertRaisesRegex(ValueError, "lineage"):
            preparation.validate(data)
        processing["steps"][3]["input"] = "control"
        processing["final"] = "tone"
        with self.assertRaisesRegex(ValueError, "final selection"):
            preparation.validate(data)

    def test_no_face_and_tiny_face_skip_all_work_and_remain_report_only(self):
        for faces in ([], [[20., 20., 59., 100.]]):
            with self.subTest(faces=faces):
                out = self.output.with_name("noface" if not faces else "tiny")
                self.output = out
                with mock.patch.object(preparation.preparation_geometry, "detect_faces",
                                       return_value=(faces, "Detector completed")):
                    with mock.patch.object(preparation, "prepared_candidates") as transforms:
                        self.assertEqual(self.call("--apply"), 0)
                        transforms.assert_not_called()
                row = self.manifest()["photos"][0]
                self.assertEqual(row["outcome"], "junk-candidate")
                self.assertEqual(row["variants"], {})
                self.assertEqual(row["recommendation"]["use"], "none")
                self.assertTrue(all(s["status"] == "skipped" for s in row["processing"]["steps"]))
                self.assertEqual(self.source_tree(), self.before)
                self.assertEqual(self.call("--check"), 0)
                page = (self.output / "index.html").read_text(encoding="utf-8")
                self.assertIn("No source recommended for generation", page)

    def test_detector_failure_is_error_not_junk_or_clean_success(self):
        with mock.patch.object(preparation.preparation_geometry, "detect_faces",
                               return_value=(None, "Local detector failed")):
            self.assertEqual(self.call("--apply"), 1)
        row = self.manifest()["photos"][0]
        self.assertEqual(row["outcome"], "assessment-failed")
        self.assertEqual(row["recommendation"]["use"], "none")
        self.assertEqual(self.call("--check"), 1)
        self.assertEqual(self.source_tree(), self.before)

    def loose_junk_run(self, category="Various", second=False):
        self.photo.unlink()
        folder = "Artists/Test Painter/gallery" if category == "Artists" else "Various/gallery"
        self.photo = self.put(folder + "/incoming_image_123.jpg")
        if second:
            self.put(folder + "/incoming_image_456.jpg")
        catalog = preparation.metadata.load_catalog()
        catalog.update(people={}, photos={}, actions=[])
        (self.root / ".likeness-library.json").write_text(json.dumps(catalog), encoding="utf-8")
        with mock.patch.object(preparation.preparation_geometry, "detect_faces",
                               return_value=([], "No detected human face; animal-only or other face-free content.")):
            self.assertEqual(self.call("--apply"), 0)
        return catalog

    def test_loose_intake_junk_preview_apply_repeat_check_and_exact_undo(self):
        self.loose_junk_run()
        original = self.photo.read_bytes()
        mtime = self.photo.stat().st_mtime_ns
        catalog = (self.root / ".likeness-library.json").read_bytes()
        with mock.patch.object(preparation_junk.metadata.cw, "load_cfg", return_value=self.cfg):
            self.assertEqual(self.call("--quarantine-junk", "--dry-run"), 0)
            self.assertTrue(self.photo.exists())
            self.assertFalse((self.output / preparation_junk.JOURNAL).exists())
            self.assertEqual(self.call("--quarantine-junk", "--apply"), 0)
            target = self.root / "_junk/Various/gallery" / self.photo.name
            self.assertFalse(self.photo.exists())
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(target.stat().st_mtime_ns, mtime)
            self.assertEqual(self.call("--check"), 0)
            journal_before = (self.output / preparation_junk.JOURNAL).read_bytes()
            self.assertEqual(self.call("--quarantine-junk", "--apply"), 0)
            self.assertEqual((self.output / preparation_junk.JOURNAL).read_bytes(), journal_before)
            self.assertEqual(self.call("--undo-junk", "--dry-run"), 0)
            self.assertFalse(self.photo.exists())
            self.assertEqual(self.call("--undo-junk", "--apply"), 0)
            self.assertEqual(self.photo.read_bytes(), original)
            self.assertEqual(self.photo.stat().st_mtime_ns, mtime)
            self.assertFalse(target.exists())
            self.assertEqual(self.call("--check"), 0)
            self.assertEqual(self.call("--undo-junk", "--apply"), 0)
        self.assertEqual((self.root / ".likeness-library.json").read_bytes(), catalog)

    def test_artist_intake_uses_shared_gate_and_preserves_artist_quarantine_scope(self):
        self.loose_junk_run(category="Artists")
        row = self.manifest()["photos"][0]
        self.assertEqual(row["sourceScope"]["matchingDomain"], "Artists/Test Painter")
        self.assertEqual(row["outcome"], "junk-candidate")
        with mock.patch.object(preparation_junk.metadata.cw, "load_cfg", return_value=self.cfg):
            self.assertEqual(self.call("--quarantine-junk", "--apply"), 0)
            target = self.root / "_junk/Artists/Test Painter/gallery" / self.photo.name
            self.assertTrue(target.is_file())
            self.assertFalse((self.root / "Various").exists())
            self.assertEqual(self.call("--undo-junk", "--apply"), 0)
        self.assertTrue(self.photo.is_file())

    def test_configured_junk_root_routes_quarantine_and_undo(self):
        config = {**self.cfg, "storageRoots": {**self.cfg["storageRoots"], "junk": "_quarantine"}}
        with mock.patch.object(preparation_junk.cw, "load_cfg", return_value=config):
            self.loose_junk_run()
            self.assertEqual(self.call("--quarantine-junk", "--apply"), 0)
            target = self.root / "_quarantine" / "Various" / "gallery" / self.photo.name
            self.assertTrue(target.is_file())
            self.assertFalse(self.photo.exists())
            journal = json.loads((self.output / preparation_junk.JOURNAL).read_text())
            self.assertEqual(journal["moves"][0]["target"],
                             "_quarantine/Various/gallery/" + self.photo.name)
            self.assertEqual(self.call("--undo-junk", "--apply"), 0)
        self.assertTrue(self.photo.is_file())
        self.assertFalse(target.exists())

    def test_source_artist_scope_cannot_be_forged_into_general_pool(self):
        self.loose_junk_run(category="Artists")
        data = self.manifest()
        data["photos"][0]["sourceScope"]["matchingDomain"] = "general"
        with self.assertRaisesRegex(ValueError, "source/artist scope"):
            preparation.validate(data)

    def test_junk_refuses_collision_stale_source_failed_backup_and_workflow_choice(self):
        self.loose_junk_run()
        target = self.root / "_junk/Various/gallery" / self.photo.name
        with mock.patch.object(preparation_junk.metadata.cw, "load_cfg", return_value=self.cfg):
            target.parent.mkdir(parents=True)
            target.write_bytes(b"existing")
            self.assertEqual(self.call("--quarantine-junk", "--apply"), 1)
            self.assertEqual(target.read_bytes(), b"existing")
            target.unlink()
            with mock.patch.object(preparation_junk.library_backup, "create_backup", side_effect=OSError("disk full")):
                self.assertEqual(self.call("--quarantine-junk", "--apply"), 1)
                self.assertIn("disk full", self.errors)
            self.assertTrue(self.photo.is_file())
            self.assertFalse((self.output / preparation_junk.JOURNAL).exists())
        with mock.patch.object(preparation_junk.metadata.cw, "load_cfg",
                               return_value={**self.cfg, "photos": {"Test": "incoming_image_123_944x1104.png"}}):
            self.assertEqual(self.call("--quarantine-junk", "--apply"), 1)
            self.assertTrue(self.photo.is_file())
        self.photo.write_bytes(b"changed")
        self.assertEqual(self.call("--quarantine-junk", "--apply"), 1)

    def test_junk_registered_cast_and_catalogue_decisions_remain_guarded(self):
        self.loose_junk_run()
        incoming_catalog = preparation.metadata.load_catalog(self.root / ".likeness-library.json")
        incoming_catalog["people"] = {"test-person": {"folder": "Various", "identityAnchors": []}}
        # This guard is independent of catalogue schema rules for eligible identity categories.
        reason = preparation_junk.protected(self.root, self.photo, incoming_catalog, {})
        self.assertIn("Registered", reason)
        incoming_catalog["people"] = {}
        incoming_catalog["photos"] = {"photo:image_123": {}}
        self.assertIn("catalogue", preparation_junk.protected(self.root, self.photo, incoming_catalog, {}))
        cast = self.root / "Sisters/Fixed/gallery/incoming_image_123.jpg"
        self.assertIn("Not loose", preparation_junk.protected(self.root, cast, incoming_catalog, {}))

    def test_junk_mid_batch_failure_rolls_back_and_keeps_incomplete_journal(self):
        self.loose_junk_run(second=True)
        original = preparation_junk.move_exact
        calls = []

        def fail_second(source, target, expected):
            calls.append((source, target))
            if len(calls) == 2:
                raise OSError("simulated second move failure")
            return original(source, target, expected)

        with mock.patch.object(preparation_junk.metadata.cw, "load_cfg", return_value=self.cfg):
            with mock.patch.object(preparation_junk, "move_exact", side_effect=fail_second):
                self.assertEqual(self.call("--quarantine-junk", "--apply"), 1)
        self.assertTrue(self.photo.exists())
        self.assertTrue(self.photo.with_name("incoming_image_456.jpg").exists())
        journal = json.loads((self.output / preparation_junk.JOURNAL).read_text())
        self.assertEqual(journal["status"], "planned")
        self.assertEqual(len(calls), 3, "first move rolled back")

    def test_junk_changed_quarantined_bytes_or_backup_block_check_and_undo(self):
        self.loose_junk_run()
        with mock.patch.object(preparation_junk.metadata.cw, "load_cfg", return_value=self.cfg):
            self.assertEqual(self.call("--quarantine-junk", "--apply"), 0)
            target = self.root / "_junk/Various/gallery" / self.photo.name
            raw = target.read_bytes()
            target.write_bytes(b"tampered")
            self.assertEqual(self.call("--check"), 1)
            self.assertEqual(self.call("--undo-junk", "--apply"), 1)
            self.assertFalse(self.photo.exists())
            target.write_bytes(raw)
            journal = json.loads((self.output / preparation_junk.JOURNAL).read_text())
            snapshot = self.root / journal["snapshot"]
            manifest = json.loads((snapshot / "manifest.json").read_text())
            (snapshot / manifest["entries"][0]["backup"]).write_bytes(b"damaged backup")
            self.assertEqual(self.call("--check"), 1)
            self.assertEqual(self.call("--undo-junk", "--apply"), 1)
            self.assertFalse(self.photo.exists())

    def test_artist_and_general_usable_inputs_share_recipe_and_padding_not_identity_assignment(self):
        self.put("Artists/First Painter/gallery/first_image_456.jpg")
        self.put("Artists/Second Painter/gallery/second_image_789.jpg")
        self.assertEqual(self.call("--apply"), 0)
        rows = self.manifest()["photos"]
        self.assertEqual({r["sourceScope"]["matchingDomain"] for r in rows},
                         {"general", "Artists/First Painter", "Artists/Second Painter"})
        for row in rows:
            self.assertEqual(row["processing"]["cleanup"], "control")
            for variant in row["variants"].values():
                with Image.open(self.output / variant["padded"]) as image:
                    self.assertEqual(image.size, (944, 1104))
        self.assertFalse(self.manifest()["recipe"]["matching"])

    def test_junk_workflow_configuration_race_after_backup_refuses_before_moves(self):
        self.loose_junk_run()
        changed = {**self.cfg, "photos": {"Test": "incoming_image_123_944x1104.png"}}
        current = [self.cfg]
        create_backup = preparation_junk.library_backup.create_backup

        def change_after_backup(*args, **kwargs):
            snapshot = create_backup(*args, **kwargs)
            current[0] = changed
            return snapshot

        with mock.patch.object(preparation_junk.cw, "load_cfg", side_effect=lambda: current[0]), \
                mock.patch.object(preparation_junk.library_backup, "create_backup",
                                  side_effect=change_after_backup) as backup:
            self.assertEqual(self.call("--quarantine-junk", "--apply"), 1)
            backup.assert_called_once()
            self.assertIn("workflow configuration changed during Junk backup", self.errors)
        self.assertTrue(self.photo.exists())
        self.assertFalse((self.output / preparation_junk.JOURNAL).exists())

    def test_invalid_geometry_or_missing_candidate_is_explicitly_rejected(self):
        self.assertEqual(self.call("--apply"), 0)
        data = self.manifest()
        row = data["photos"][0]
        row["geometry"]["box"][2] += 1
        with self.assertRaisesRegex(ValueError, "crop box outside"):
            preparation.validate(data)
        row["geometry"]["box"][2] -= 1
        row["variants"]["geometry"]["size"][0] -= 1
        with self.assertRaisesRegex(ValueError, "dimensions disagree"):
            preparation.validate(data)
        del row["variants"]["control"]
        with self.assertRaisesRegex(ValueError, "missing geometry/control"):
            preparation.validate(data)

    def test_detail_links_are_local_valid_and_source_text_is_escaped(self):
        self.photo.rename(self.photo.with_name("name&other_image_123.jpg"))
        self.assertEqual(self.call("--apply"), 0)
        page = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn("name&amp;other", page)
        self.assertIn("Denoise/tone are never accepted automatically", page)
        for file in [self.output / "index.html", *self.output.glob("photos/*.html")]:
            links = Links()
            text = file.read_text(encoding="utf-8")
            links.feed(text)
            self.assertTrue(links.targets)
            fragments = [target for target in links.targets if target.startswith("#")]
            self.assertTrue(all(f'id="{target[1:]}"' in text for target in fragments))
            self.assertTrue(all((file.parent / unquote(target)).is_file()
                                for target in links.targets if not target.startswith("#")))

    def test_manifest_path_escape_is_rejected(self):
        self.assertEqual(self.call("--apply"), 0)
        data = self.manifest()
        data["photos"][0]["retained"] = "../../../../../outside.jpg"
        (self.output / "manifest.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(self.call("--check"), 1)

    def test_empty_or_noncanonical_source_manifest_refuses_explicitly(self):
        self.assertEqual(self.call("--apply"), 0)
        data = self.manifest()
        for invalid in (".", "../Angels/gallery/a.jpg", "Angels\\gallery\\a.jpg"):
            modified = {**data, "photos": [{**data["photos"][0], "source": invalid}]}
            (self.output / "manifest.json").write_text(json.dumps(modified), encoding="utf-8")
            self.assertEqual(self.call("--check"), 1)
        (self.output / "manifest.json").write_text(json.dumps({**data, "photos": []}), encoding="utf-8")
        self.assertEqual(self.call("--check"), 1)


def slow_fake_render(root, stage, source):
    """Picklable stand-in for render_photo; early inputs finish last."""
    import os
    import time

    time.sleep(0.05 * (5 - int(source.stem[-1])))
    return {"source": source.name, "pid": os.getpid()}


class ParallelPreparationTests(unittest.TestCase):
    def test_parallel_rows_keep_input_order_and_render_duplicates_in_one_task(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            sources = []
            for index, payload in enumerate((b"a", b"b", b"a", b"c", b"d")):
                path = root / f"p{index}.jpg"
                path.write_bytes(payload)
                sources.append(path)
            rows = list(preparation.rendered_rows(root, root, sources, 2, render=slow_fake_render))
        self.assertEqual([index for index, _ in rows], [0, 1, 2, 3, 4])
        self.assertEqual([row["source"] for _, row in rows], [p.name for p in sources])
        self.assertEqual(rows[0][1]["pid"], rows[2][1]["pid"])

    def test_worker_count_honours_override_and_free_memory(self):
        with mock.patch.dict("os.environ", {"ST_INTAKE_WORKERS": "5"}):
            self.assertEqual(preparation.default_workers(), 5)
        with mock.patch.dict("os.environ", {"ST_INTAKE_WORKERS": ""}), mock.patch("os.cpu_count", return_value=12):
            with mock.patch.object(preparation, "available_memory_gb", return_value=3.0):
                self.assertEqual(preparation.default_workers(), 1)
            with mock.patch.object(preparation, "available_memory_gb", return_value=16.0):
                self.assertEqual(preparation.default_workers(), preparation.MAX_WORKERS)


if __name__ == "__main__":
    unittest.main()
