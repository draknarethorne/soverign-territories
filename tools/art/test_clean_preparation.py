"""Prepared clean-start stop/resume, publication and exact recovery."""
import contextlib
import io
import json
import pathlib
import shutil
import os
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np
from PIL import Image, ImageDraw

from tools.art import image_preparation, likeness
from tools.art.likeness_library import clean_preparation, clean_rebase, derivatives, metadata, retained_preparation, review_gallery, storage_retention
from tools.art.likeness_library.policy import load_policy
from tools.art.likeness_library.reconciliation import frozen_identity_cores


class CleanPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = pathlib.Path(self.temp.name) / "Sovereign Territories Sandbox"
        self.source, self.working = self.base / "Source", self.base / "Working"
        self.run = self.working / "_sandbox-state" / "prepared"
        self.run.mkdir(parents=True)
        self.inputs = {}
        for relative in (
            "Angels/Fixed/gallery/fixed_image_123456.jpg",
            "Potentials/Fia/gallery/fia_image_654321.jpg",
            "Various/gallery/incoming_image_345678.jpg",
            "Various/Known Person/gallery/known_image_456789.jpg",
            "Artists/Artist/gallery/art_image_567890.jpg",
        ):
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            image = Image.new("RGB", (640, 960), "black")
            ImageDraw.Draw(image).rectangle((12, 12, 627, 947), fill=(95, 65, 35))
            image.save(path)
            self.inputs[relative] = (path.stat().st_size, metadata.content_sha256(path))
            target = self.working / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        self.layout = {
            "source_root": self.source, "working_root": self.working, "sandbox_root": self.base,
            "manifest_files": self.inputs,
        }
        (self.base / "source-manifest.json").write_text(json.dumps({
            "schemaVersion": 1, "snapshotRoot": "Source", "workingRootAtCreation": "Working",
            "sourceRoot": str(self.base.parent / "Sovereign Territories"),
            "fileCount": len(self.inputs), "totalBytes": sum(value[0] for value in self.inputs.values()),
            "files": [{"path": path, "bytes": value[0], "sha256": value[1]}
                      for path, value in self.inputs.items()],
        }), encoding="utf-8")
        metadata.save_catalog(
            {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
            self.working / ".likeness-library.json",
        )
        self.api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: {}, storage_root=likeness.cw.storage_root,
                photo_key=likeness.cw.photo_key,
                photo_folders=likeness.cw.photo_folders,
            ),
            originals=likeness.originals, nz=likeness.nz, chosen_keys=lambda cfg: set(),
            invent_name=lambda seed, taken: "New Person",
        )
        self.measured = []

        def embed(path):
            self.measured.append(path)
            return {"v": [1., 0.], "faces": 1, "s": .95, "px": 100, "box": [.25, .1, .3, .3]}

        self.embed = embed
        for patch in (
            mock.patch.object(likeness, "Embedder", return_value=self.embed),
            mock.patch.object(review_gallery.likeness, "Embedder", return_value=self.embed),
            mock.patch.object(likeness._Embedder, "load",
                              side_effect=AssertionError("Offline fixtures must never load face models")),
            mock.patch.object(image_preparation.preparation_geometry, "detect_faces",
                              return_value=([[50., 40., 60., 70.]], "Test face")),
            mock.patch.object(image_preparation.pipeline.subjects, "detect",
                              side_effect=self.subject),
            mock.patch.object(image_preparation.pipeline.fill, "fill",
                              side_effect=AssertionError("No clutter in fixture; do not load eraser")),
            mock.patch.object(clean_rebase, "validate_sandbox", return_value=self.layout),
            mock.patch.object(clean_rebase, "frozen_identity_cores", side_effect=self.frozen_cores),
            mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=self.matches),
        ):
            patch.start()
            self.addCleanup(patch.stop)

    @staticmethod
    def frozen_cores(space, catalog, **kwargs):
        if all(not hasattr(photo, "bucket") for photo in space.photos):
            return {"Angels/Fixed": {"vector": np.array([1., 0.]), "side": "Prospects"}}, set(), []
        return frozen_identity_cores(space, catalog, **kwargs)

    @staticmethod
    def subject(image):
        mask = np.zeros((image.height, image.width), dtype=bool)
        mask[35:850, 35:600] = True
        return {"box": [35, 35, 600, 850], "mask": mask, "people": 1, "dropped": 0}

    @staticmethod
    def matches(candidates, cores, **kwargs):
        return {
            "assignments": [], "clusters": [],
            "held": [{"photoId": row["photoId"], "reason": "Synthetic unmatched candidate"}
                     for row in candidates],
        }

    def args(self, **flags):
        return SimpleNamespace(
            root=str(self.working), run_dir=str(self.run), policy=None, embedder=self.embed,
            **{**dict(apply=False, check=False, dry_run=False, undo=False,
                      replan=False, intake_only=False), **flags},
        )

    def command(self, **flags):
        with contextlib.redirect_stdout(io.StringIO()):
            return clean_rebase.command(self.args(**flags), self.api)

    def test_curation_inventory_recognizes_ids_assigned_from_raw_download_names(self):
        relative = "Various/gallery/facebook_1791423017739_7513772728997485362.jpg"
        source = self.source / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.source / "Various/gallery/incoming_image_345678.jpg", source)
        self.inputs[relative] = (source.stat().st_size, metadata.content_sha256(source))
        published = self.working / "Angels/Fixed/review/fixed_image_7513772728997485362.png"
        published.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (160, 240), "blue").save(published)
        inventory = clean_rebase._curation_inventory(self.layout)
        self.assertEqual(inventory[published.relative_to(self.working).as_posix()],
                         metadata.content_sha256(published))

    def test_inventory_preview_is_read_only_and_apply_requires_matching_preview(self):
        result = self.command(dry_run=True)
        self.assertEqual(result["inputCount"], 5)
        self.assertFalse((self.run / "inputs").exists())
        with self.assertRaisesRegex(ValueError, "review.*preview"):
            self.command(apply=True)
        self.assertFalse(self.measured)

    def test_fast_raw_intake_install_viewers_check_and_exact_undo(self):
        from tools.art.likeness_library import fast_preparation, preparation_provenance

        before = {relative: (self.working / relative).read_bytes() for relative in self.inputs}
        with mock.patch.object(image_preparation, "publish", side_effect=AssertionError("FAST must not edit")), \
                mock.patch.object(derivatives, "render", side_effect=AssertionError("FAST must not render")), \
                mock.patch.object(derivatives, "maintain", side_effect=AssertionError("FAST install must skip derivatives")):
            self.command(intake_only=True, apply=True, profile="fast")
            output, intake = clean_preparation.verify(self.layout, self.run)
            self.assertEqual(intake["processingProfile"], "fast")
            self.assertEqual(len(intake["photos"]), 5)
            self.assertFalse(self.measured)
            self.assertIn('loading="lazy"', (output / "index.html").read_text())
            for row in intake["photos"]:
                self.assertEqual(row["outcome"], "analysis-only")
                self.assertEqual(clean_preparation.selected_path(output, row).read_bytes(), before[row["source"]])
                self.assertEqual(row["variants"], {})
                self.assertNotIn("recommendedPadded", row)
            with self.assertRaisesRegex(ValueError, "processing profile differs"):
                self.command(profile="lean")
            self.command()  # Omission must resume FAST, not start standard LEAN.
            with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                    mock.patch("library_backup.verify_backup"):
                self.command(apply=True)
            self.command(check=True)
        plan = json.loads((self.run / "run.json").read_text())
        self.assertEqual(plan["preparation"]["processingProfile"], "fast")
        self.assertEqual(plan["recoveryMode"], "full")
        self.assertIn("fast_preparation.py", plan["implementationHashes"])
        self.assertEqual(len(plan["photos"]), 4)  # Artist is intentionally outside general matching.
        self.assertFalse(list(self.working.rglob(derivatives.MANIFEST)))
        for row in plan["photos"]:
            native = self.working / row["destination"]
            self.assertEqual(native.read_bytes(), before[row["source"]])
            self.assertTrue(fast_preparation.deferred(native))
            link = retained_preparation.verify_link(self.working, native)
            self.assertTrue(link)
            self.assertIn('aria-label="Retained intake navigation"',
                          (self.working / link["detail"]).read_text())
            with mock.patch.object(derivatives, "render", side_effect=AssertionError("no backfill")):
                changes, messages = derivatives.maintain(native, [.25, .1, .3, .3], 100, apply=True)
            self.assertEqual(changes, [])
            self.assertIn("deferred", messages[0])
        faces = mock.Mock()
        faces.of.side_effect = AssertionError("FAST originals maintenance must not detect faces")
        with mock.patch.object(likeness.originals, "fit", side_effect=AssertionError("no scaled writer")), \
                mock.patch.object(likeness.originals, "headshot", side_effect=AssertionError("no headshot writer")), \
                contextlib.redirect_stdout(io.StringIO()):
            likeness.originals.main(
                ["--root", str(self.working), "--only", "Known Person",
                 "--apply", "--force", "--no-repoint"], faces=faces)
        faces.of.assert_not_called()
        self.assertFalse(list(self.working.rglob(derivatives.MANIFEST)))
        report_root = self.working / "_reports" / "library"
        index = preparation_provenance.build_index(self.working, report_root, [], "general")
        staged = [run for run in index.history_runs if run.get("staged")]
        self.assertEqual(len(staged), 1)
        self.assertTrue(staged[0]["status"].startswith("verified staged"), staged)
        self.assertEqual(len(staged[0]["photos"]), 4)
        self.assertTrue(all(photo["thumbnail"] for photo in staged[0]["photos"]))
        self.command(undo=True)
        for relative, expected in before.items():
            self.assertEqual((self.working / relative).read_bytes(), expected)

    def test_fast_disposable_profile_remains_separate_from_recovery(self):
        self.command(intake_only=True, apply=True, profile="fast", recovery_mode="disposable")
        self.command()
        with mock.patch("library_backup.latest_work_root_backup", side_effect=AssertionError("no backup")):
            self.command(apply=True)
        self.command(check=True)
        self.assertFalse((self.run / "previous").exists())
        with self.assertRaisesRegex(ValueError, "no undo contract"):
            self.command(undo=True)
        with self.assertRaisesRegex(ValueError, "processing profile differs"):
            self.command(profile="full", check=True)

    def test_fast_profile_preserves_actual_assignment_move_and_stable_name(self):
        def assign(candidates, cores, **kwargs):
            return {
                "assignments": [{"photoId": row["photoId"], "destination": "Potentials/Generated",
                                 "reason": "Test assignment"} for row in candidates],
                "held": [],
                "clusters": [{"clusterId": "test", "destination": "Potentials/Generated",
                              "photoIds": [row["photoId"] for row in candidates]}],
            }
        with mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=assign):
            self.command(profile="fast")
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True, profile="fast")
        self.command(check=True)
        plan = json.loads((self.run / "run.json").read_text())
        incoming = next(row for row in plan["photos"] if row["source"].startswith("Various/gallery/"))
        # Placeholder destinations receive the normal character-facing name.
        self.assertTrue(incoming["destination"].startswith("Potentials/New Person/gallery/"))
        self.assertIn("image_345678", incoming["destination"])
        self.assertEqual((self.working / incoming["destination"]).read_bytes(),
                         (self.source / incoming["source"]).read_bytes())
        known = next(row for row in plan["photos"] if "Known Person" in row["source"])
        self.assertTrue(known["destination"].startswith("Potentials/Known Person/gallery/"))
        self.assertEqual({row["photoId"] for row in plan["photos"]},
                         {"photo:image_123456", "photo:image_345678",
                          "photo:image_456789", "photo:image_654321"})

    def test_fast_resume_and_tamper_refusal(self):
        from tools.art.likeness_library import fast_preparation

        self.command(intake_only=True, apply=True, profile="fast", storage_mode="full")
        output, data = clean_preparation.verify(self.layout, self.run)
        saved = (output / "manifest.json").read_bytes()
        with mock.patch.object(fast_preparation, "publish", side_effect=AssertionError("do not rerender")):
            self.command(intake_only=True, apply=True)
        self.assertEqual((output / "manifest.json").read_bytes(), saved)
        with self.assertRaisesRegex(ValueError, "storage mode differs"):
            self.command(profile="fast", storage_mode="lean", check=True)
        original = clean_preparation.selected_path(output, data["photos"][0])
        original.write_bytes(b"edited")
        with self.assertRaisesRegex(ValueError, "FAST input changed"):
            self.command(check=True)

    def test_fast_complete_intake_stage_resumes_but_refuses_extra_products(self):
        self.command(intake_only=True, apply=True, profile="fast")
        output, data = clean_preparation.verify(self.layout, self.run)
        original = (output / "manifest.json").read_bytes()
        (self.run / "intake.json").unlink()
        stage = output.with_name(output.name + ".partial")
        output.rename(stage)
        with mock.patch.object(image_preparation, "decode_file", side_effect=AssertionError("no repeat decode")):
            self.command(intake_only=True, apply=True, profile="fast")
        self.assertEqual((output / "manifest.json").read_bytes(), original)
        extra = output / "unexpected-944x1104.png"
        extra.write_bytes(b"undeclared")
        with self.assertRaisesRegex(ValueError, "FAST artifact inventory differs"):
            self.command(check=True)
        self.assertEqual(len(data["photos"]), 5)

    def test_fast_refuses_linked_output_ancestor_before_writing(self):
        from tools.art.likeness_library import fast_preparation

        output = self.source / "_reports" / "preparation" / "fast"
        with mock.patch("image_preparation.sandbox._is_reparse_point",
                        side_effect=lambda path: pathlib.Path(path).name == "preparation"):
            with self.assertRaisesRegex(ValueError, "refusing linked path"):
                fast_preparation.publish(self.source, output, {}, "lean")
        self.assertFalse(output.parent.exists())

    def test_fast_completed_install_stage_resumes_without_derivatives(self):
        self.command(intake_only=True, apply=True, profile="fast")
        plan = self.completed_stage()
        self.assertEqual(self.command(check=True, resume_install=True)["status"], "staged-verified")
        staged = self.run / "staged"
        extra = staged / "unexpected-944x1104.png"
        extra.write_bytes(b"undeclared")
        with self.assertRaisesRegex(ValueError, "staged inventory changed"):
            self.command(check=True, resume_install=True)
        extra.unlink()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"), \
                mock.patch.object(derivatives, "maintain", side_effect=AssertionError("no derivatives")), \
                mock.patch.object(retained_preparation, "stage_photo", side_effect=AssertionError("no recopy")):
            self.command(apply=True, resume_install=True)
        self.command(check=True)
        self.command(undo=True)
        self.assertEqual(len(plan["photos"]), 4)

    def test_fast_decode_error_is_explicit_not_a_clean_photo(self):
        from tools.art.likeness_library import fast_preparation

        source = self.source / "Various/gallery/bad_image_999999.jpg"
        source.write_bytes(b"broken jpeg")
        self.inputs[source.relative_to(self.source).as_posix()] = (
            source.stat().st_size, metadata.content_sha256(source))
        self.command(intake_only=True, apply=True, profile="fast")
        output, data = clean_preparation.verify(self.layout, self.run)
        failed = next(row for row in data["photos"] if row["source"].endswith(source.name))
        self.assertEqual(failed["outcome"], "unprocessable")
        self.assertIn("Decode failed", failed["diagnostics"][-1])
        self.assertEqual(clean_preparation.selected_path(output, failed).read_bytes(), b"broken jpeg")
        self.assertTrue(json.loads((self.run / "intake.json").read_text())["assessmentErrors"])
        native = self.working / "Various" / "review" / source.name
        native.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, native)
        retained_preparation.stage_photo(
            self.working, native.relative_to(self.working), output, failed,
            recipe=data["recipe"], storage_mode="lean")
        preview, _key, diagnostic = derivatives.thumbnail(native, "chest", faces=0, px=0)
        self.assertTrue(preview.startswith(b"\xff\xd8"))
        self.assertIn("cannot identify image file", diagnostic)
        with mock.patch.object(fast_preparation, "RECIPE", {"id": "incompatible"}):
            with self.assertRaisesRegex(ValueError, "recipe/profile/storage/implementation changed"):
                self.command(check=True)

    def test_profiles_share_input_population_and_bind_different_pixel_recipes(self):
        populations = []
        for profile in ("fast", "lean", "full"):
            with self.subTest(profile=profile):
                self.run = self.working / "_sandbox-state" / profile
                self.command(intake_only=True, apply=True, profile=profile)
                output, data = clean_preparation.verify(self.layout, self.run)
                populations.append({row["source"]: row["sourceSha256"] for row in data["photos"]})
                self.assertEqual(data.get("storageMode", "full"), "full" if profile == "full" else "lean")
                self.assertEqual(data.get("processingProfile", "standard"), "fast" if profile == "fast" else "standard")
                if profile != "fast":
                    self.assertTrue(any(clean_preparation.selected_path(output, row).read_bytes()
                                        != (self.source / row["source"]).read_bytes() for row in data["photos"]))
        self.assertEqual(populations[0], populations[1])
        self.assertEqual(populations[0], populations[2])
        with self.assertRaisesRegex(ValueError, "processing profile differs"):
            self.command(profile="fast")
        with self.assertRaisesRegex(ValueError, "--profile and --storage-mode differ"):
            self.command(profile="full", storage_mode="lean")

    def test_all_profiles_publish_check_and_undo_the_same_photo_ids(self):
        populations = []
        for profile in ("fast", "lean", "full"):
            with self.subTest(profile=profile):
                self.run = self.working / "_sandbox-state" / ("installed-" + profile)
                self.command(profile=profile)
                with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                        mock.patch("library_backup.verify_backup"):
                    self.command(apply=True, profile=profile)
                self.command(check=True, profile=profile)
                plan = json.loads((self.run / "run.json").read_text())
                populations.append({row["photoId"] for row in plan["photos"]})
                self.assertEqual(plan["preparation"]["storageMode"], "full" if profile == "full" else "lean")
                manifests = list(self.working.rglob(derivatives.MANIFEST))
                # Inputs keep prior runs' evidence, but only installed native owners count here.
                installed = [path for path in manifests if "_sandbox-state" not in path.relative_to(self.working).parts]
                self.assertEqual(bool(installed), profile != "fast")
                for row in plan["photos"]:
                    native = self.working / row["destination"]
                    self.assertTrue(native.is_file())
                    self.assertTrue(retained_preparation.verify_link(self.working, native))
                    if profile == "fast":
                        self.assertEqual(native.read_bytes(), (self.source / row["source"]).read_bytes())
                self.command(undo=True, profile=profile)
        self.assertEqual(populations[0], populations[1])
        self.assertEqual(populations[0], populations[2])

    def test_regroup_profiles_publish_membership_and_exact_undo(self):
        manifest_path = self.base / "source-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        for index, row in enumerate(manifest["files"]):
            source = self.source / row["path"]
            image = Image.new("RGB", (640, 960), "black")
            ImageDraw.Draw(image).rectangle((12, 12, 627, 947), fill=(65 + index * 25, 65, 35))
            image.save(source)
            shutil.copy2(source, self.working / row["path"])
            row["bytes"], row["sha256"] = source.stat().st_size, metadata.content_sha256(source)
            self.inputs[row["path"]] = row["bytes"], row["sha256"]
        manifest["totalBytes"] = sum(row["bytes"] for row in manifest["files"])
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        def varied_embedding(path):
            angle = int(metadata.content_sha256(path)[:8], 16) / (2 ** 32) * np.pi * 2
            return {"v": [float(np.cos(angle)), float(np.sin(angle))], "faces": 1,
                    "s": .95, "px": 100, "box": [.25, .1, .3, .3]}

        self.embed = varied_embedding
        populations = []
        for profile in ("fast", "lean", "full"):
            with self.subTest(profile=profile):
                self.run = self.working / "_sandbox-state" / ("grouped-" + profile)
                flags = dict(profile=profile, cast_seeds="core", regroup=True)
                self.command(**flags)
                with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                        mock.patch("library_backup.verify_backup"):
                    self.command(apply=True, **flags)
                self.command(check=True, **flags)
                plan = json.loads((self.run / "run.json").read_text())
                catalog = json.loads((self.run / "catalog.json").read_text())
                metadata.validate_catalog(catalog)
                populations.append({row["photoId"] for row in plan["photos"]})
                self.assertEqual(plan["groupLifecycle"]["evaluation"]["identifiedPhotos"], 4)
                for row in plan["photos"]:
                    self.assertIn("membership", row)
                    self.assertTrue((self.working / row["destination"]).is_file())
                    self.assertEqual(catalog["photos"][row["photoId"]]["membership"], row["membership"])
                self.command(undo=True, **flags)
        self.assertEqual(populations[0], populations[1])
        self.assertEqual(populations[0], populations[2])

    def test_lean_new_run_install_check_and_exact_undo(self):
        self.command(intake_only=True, apply=True, storage_mode="lean")
        with self.assertRaisesRegex(ValueError, "storage mode differs"):
            self.command(intake_only=True, apply=True, storage_mode="full")
        self.command(storage_mode="lean")
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True, storage_mode="lean")
        self.command(check=True)
        plan = json.loads((self.run / "run.json").read_text())
        for row in plan["photos"]:
            link = retained_preparation.verify_link(self.working, row["destination"])
            self.assertIsNotNone(link)
            self.assertEqual(link["formatVersion"], retained_preparation.LEAN_VERSION)
            self.assertTrue(link["manifest"].startswith("_processing/"))
            self.assertNotIn(row["destination"], [entry["path"] for entry in link["artifacts"]])
        self.command(undo=True)
        for relative, expected in self.inputs.items():
            self.assertEqual(metadata.content_sha256(self.working / relative), expected[1])

    def test_disposable_lean_installs_without_creating_backup_or_rollback_and_still_checks(self):
        self.command(intake_only=True, apply=True, storage_mode="lean", recovery_mode="disposable")
        with self.assertRaisesRegex(ValueError, "recovery mode differs"):
            self.command(recovery_mode="full")
        self.command()
        with mock.patch("library_backup.latest_work_root_backup",
                        side_effect=AssertionError("disposable must not require backup")), \
                mock.patch("library_backup.verify_backup",
                           side_effect=AssertionError("disposable must not verify backup")), \
                mock.patch.object(clean_rebase, "retire_disposable_rollback",
                                  side_effect=AssertionError("disposable creates no rollback to retire")):
            self.command(apply=True, recovery_mode="disposable")
        self.command(check=True, recovery_mode="disposable")
        plan = json.loads((self.run / "run.json").read_text())
        self.assertTrue(plan["rollbackRetired"])
        self.assertFalse(plan["rollbackCreated"])
        self.assertFalse((self.run / "previous").exists())
        self.assertFalse((self.run / "previous-catalog.json").exists())
        self.assertNotIn("previousCategoryFiles", plan)
        self.assertNotIn("previousExternalHashes", plan)
        self.assertFalse((self.working / "_backup").exists())
        with self.assertRaisesRegex(ValueError, "no undo contract"):
            self.command(undo=True)
        with self.assertRaisesRegex(ValueError, "recovery mode differs"):
            self.command(check=True, recovery_mode="full")

    def test_disposable_refuses_full_storage_and_non_sandbox(self):
        with self.assertRaisesRegex(ValueError, "requires LEAN"):
            self.command(intake_only=True, apply=True, storage_mode="full", recovery_mode="disposable")
        with self.assertRaisesRegex(ValueError, "sandbox-local LEAN"):
            clean_rebase._require_disposable_sandbox(
                {**self.layout, "working_root": self.base.parent / "Sovereign Territories"},
                self.run, {"preparation": {"storageMode": "lean"}},
            )

    def test_disposable_publication_failure_requires_reset_without_restoring_originals(self):
        self.command(intake_only=True, apply=True, storage_mode="lean", recovery_mode="disposable")
        self.command()
        catalog = (self.working / ".likeness-library.json").read_bytes()
        with mock.patch.object(metadata, "save_catalog", side_effect=OSError("publication failed")), \
                mock.patch.object(clean_rebase, "retire_disposable_rollback",
                                  side_effect=AssertionError("not yet verified")):
            with self.assertRaisesRegex(RuntimeError, "no rollback exists"):
                self.command(apply=True)
        self.assertEqual((self.working / ".likeness-library.json").read_bytes(), catalog)
        failed = json.loads((self.run / "run.json").read_text())
        self.assertEqual(failed["status"], "reset-required")
        self.assertIn("publication failed", failed["publicationError"])
        self.assertFalse((self.run / "previous").exists())
        self.assertFalse((self.run / "previous-catalog.json").exists())

    def test_intake_preview_and_missing_run_checks_do_not_create_a_directory(self):
        self.run = self.working / "_sandbox-state" / "not-created"
        self.assertEqual(self.command(intake_only=True)["inputCount"], 5)
        self.assertFalse(self.run.exists())
        for flag in ("check", "undo", "replan"):
            with self.assertRaisesRegex(ValueError, "no saved clean-start run"):
                self.command(**{flag: True})
            self.assertFalse(self.run.exists())

    def test_run_cannot_live_under_various_which_the_rebuild_replaces(self):
        self.run = self.working / "Various" / "_reports" / "prepared"
        with self.assertRaisesRegex(ValueError, "outside identity category roots"):
            self.command(dry_run=True)
        self.assertFalse(self.run.exists())

    @unittest.skipUnless(os.name == "nt", "Windows launcher")
    def test_launcher_inventory_preview_uses_immutable_sources_without_a_cache(self):
        result = subprocess.run(
            ["cmd", "/c", str(pathlib.Path(__file__).resolve().parents[2] / "bin" / "sandbox-rebase.cmd"),
             str(self.working), str(self.run), "--dry-run"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("5 immutable images", result.stdout)
        self.assertFalse((self.run / "inputs").exists())
        self.assertFalse((self.run / "likeness-cache.json").exists())

    @unittest.skipUnless(os.name == "nt", "Windows launcher")
    def test_launcher_forwards_more_than_nine_arguments_including_dry_run(self):
        result = subprocess.run(
            ["cmd", "/c", str(pathlib.Path(__file__).resolve().parents[2] / "bin" / "sandbox-rebase.cmd"),
             str(self.working), str(self.run), "--baseline", "working", "--cast-seeds", "core",
             "--workers", "1", "--include-current-various", "--dry-run"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("current Working assigned images", result.stdout)
        self.assertIn("Cast-seed policy: core.", result.stdout)
        self.assertFalse((self.run / "source-overlay").exists())
        self.assertFalse((self.run / "inputs").exists())

    def test_input_copy_failure_removes_stage_without_publishing_partial_mirror(self):
        with mock.patch.object(clean_preparation.shutil, "copy2", side_effect=OSError("copy failed")):
            with self.assertRaisesRegex(OSError, "copy failed"):
                clean_preparation.prepare(self.layout, self.run)
        self.assertFalse((self.run / "inputs").exists())
        self.assertEqual(list((self.working / "_tmp").iterdir()), [])

    def test_input_mirror_publication_retries_transient_lock(self):
        original = os.rename
        attempts = []

        def rename(source, target):
            if pathlib.Path(target) == self.run / "inputs":
                attempts.append(target)
                if len(attempts) == 1:
                    raise PermissionError("scanner lock")
            return original(source, target)

        with mock.patch.object(metadata.report_assets.os, "rename", side_effect=rename), \
                mock.patch.object(metadata.report_assets.time, "sleep"):
            output, data = clean_preparation.prepare(self.layout, self.run)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(len(data["photos"]), 5)
        self.assertTrue(output.is_dir())

    def test_persistent_mirror_publication_lock_never_publishes_receipt(self):
        with mock.patch.object(metadata.report_assets.os, "rename", side_effect=PermissionError("locked")), \
                mock.patch.object(metadata.report_assets.time, "sleep"):
            with self.assertRaises(PermissionError):
                clean_preparation.prepare(self.layout, self.run)
        self.assertFalse((self.run / "inputs").exists())
        self.assertFalse((self.run / "intake.json").exists())

    def test_resume_after_receipt_interruption_reuses_verified_artifacts(self):
        self.command(intake_only=True, apply=True)
        (self.run / "intake.json").unlink()
        with mock.patch.object(
            image_preparation, "rendered_rows",
            side_effect=AssertionError("verified published intake must not render again"),
        ):
            result = self.command(intake_only=True, apply=True)
        self.assertEqual(result["inputCount"], 5)
        self.assertTrue((self.run / "intake.json").is_file())
        self.assertEqual(list((self.working / "_tmp").iterdir()), [])

    def test_candidate_quality_reads_selected_pixels_without_changing_source_identity(self):
        self.command(intake_only=True, apply=True)
        output, data = clean_preparation.verify(self.layout, self.run)
        selected = {
            pathlib.PurePosixPath(row["source"]).name:
            clean_preparation.selected_path(output, row)
            for row in data["photos"]
        }
        source_folders = {
            pathlib.PurePosixPath(row["source"]).name:
            pathlib.PurePosixPath(row["source"]).parent.parent.as_posix()
            for row in data["photos"]
        }
        checked = []

        def quality_reason(photo, settings):
            checked.append(photo.name)
            self.assertEqual(photo.path, selected[photo.name])
            self.assertEqual(photo.key, source_folders[photo.name])
            return None

        self.api.junk_reason = quality_reason
        self.command()
        self.assertEqual(checked, ["fia_image_654321.jpg", "incoming_image_345678.jpg"])
        plan = json.loads((self.run / "run.json").read_text(encoding="utf-8"))
        row = next(row for row in plan["photos"] if row["photoId"] == "photo:image_654321")
        self.assertEqual(row["source"], "Potentials/Fia/gallery/fia_image_654321.jpg")
        self.assertEqual(row["oldFolder"], "Potentials/Fia")

    def test_intake_stop_check_resume_uses_selected_bytes_and_includes_named_pool_and_artists(self):
        self.assertEqual(self.command(intake_only=True, apply=True)["status"], "intake")
        self.assertFalse(self.measured)
        self.assertFalse((self.run / "run.json").exists())
        self.assertEqual(self.command(check=True)["inputCount"], 5)
        manifest = clean_preparation.verify(self.layout, self.run)[0] / "manifest.json"
        unchanged = manifest.read_bytes()
        with mock.patch.object(image_preparation, "publish", side_effect=AssertionError("Do not repeat intake")):
            self.command()
        plan = json.loads((self.run / "run.json").read_text(encoding="utf-8"))
        retention = json.loads(
            (self.working / "_sandbox-state" / "retention-manifest.json").read_text(encoding="utf-8")
        )
        registered = retention["runs"][self.run.name]
        self.assertEqual(registered["retentionClass"], "review")
        self.assertIn("intake.json", registered["manifestHashes"])
        self.assertIn("run.json", registered["manifestHashes"])
        self.assertEqual(plan["preparation"]["inputCount"], 5)
        self.assertEqual(plan["preparation"]["artistCount"], 1)
        helper = pathlib.Path(derivatives.__file__).with_name("verification_reads.py")
        self.assertEqual(plan["implementationHashes"]["verification_reads.py"], metadata.content_sha256(helper))
        self.assertEqual(len(plan["photos"]), 4)
        self.assertTrue(all(self.run in path.parents for path in self.measured))
        self.assertTrue(any(row["preparedSHA256"] != row["sha256"] for row in plan["photos"]))
        named = next(row for row in plan["photos"] if "Known Person" in row["source"])
        self.assertTrue(named["destination"].startswith("Potentials/Known Person/gallery/"))
        self.assertEqual(manifest.read_bytes(), unchanged)

    def test_content_duplicates_preserve_both_sources_and_recover_exactly(self):
        originals = {}
        for relative in ("Potentials/Fia/gallery/legacy.jpg", "Various/gallery/LEGACY.JPG"):
            source = self.source / relative
            shutil.copy2(self.source / "Potentials/Fia/gallery/fia_image_654321.jpg", source)
            shutil.copy2(source, self.working / relative)
            self.inputs[relative] = (source.stat().st_size, metadata.content_sha256(source))
            originals[relative] = source.read_bytes()
        self.command()
        plan = json.loads((self.run / "run.json").read_text(encoding="utf-8"))
        held = [row for row in plan["photos"] if row["source"] in originals]
        self.assertEqual(len(held), 2)
        destinations = {row["source"]: row["destination"] for row in held}
        self.assertEqual(len({value.casefold() for value in destinations.values()}), 2)
        for row in held:
            self.assertTrue(row["destination"].startswith("Various/review/"))
            self.assertIsNone(metadata.photo_id_from_name(row["destination"]))
            self.assertIn("exact byte duplicate", row["reason"])
            self.assertTrue(pathlib.PurePosixPath(row["destination"]).name.startswith("various_duplicate_"))
        self.command(replan=True)
        replanned = json.loads((self.run / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(destinations, {
            row["source"]: row["destination"] for row in replanned["photos"] if row["source"] in originals
        })
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        for destination in destinations.values():
            native = self.working / destination
            self.assertTrue(native.is_file())
            self.assertIsNotNone(retained_preparation.verify_link(self.working, native))
        self.command(check=True)
        self.command(undo=True)
        for relative, content in originals.items():
            self.assertEqual((self.working / relative).read_bytes(), content)

    def test_nonstandard_intake_name_has_stable_id_and_reversible_standard_destination(self):
        relative = "Various/gallery/Mia Base.jpg"
        source = self.source / relative
        Image.new("RGB", (640, 960), (120, 100, 80)).save(source)
        target = self.working / relative
        shutil.copy2(source, target)
        self.inputs[relative] = (source.stat().st_size, metadata.content_sha256(source))
        original = source.read_bytes()
        key = f"pic_{likeness.originals.content_id(source)}"
        self.command()
        plan = json.loads((self.run / "run.json").read_text(encoding="utf-8"))
        row = next(item for item in plan["photos"] if item["source"] == relative)
        self.assertEqual(row["photoId"], f"photo:{key}")
        self.assertEqual(row["photoIdOrigin"], "originals-content-id")
        self.assertEqual(pathlib.PurePosixPath(row["destination"]).stem, f"various_{key}")
        self.assertNotIn("missing stable photo ID", row["reason"])
        self.assertEqual(source.read_bytes(), original)
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        native = self.working / row["destination"]
        self.assertTrue(native.is_file())
        self.assertEqual(metadata.photo_id_from_name(native.name), f"photo:{key}")
        self.assertIsNotNone(retained_preparation.verify_link(self.working, native))
        self.command(check=True)
        self.command(undo=True)
        self.assertEqual(target.read_bytes(), original)

    def test_apply_retains_versions_and_originals_and_undo_restores_cast_and_pool(self):
        before = {path.relative_to(self.working).as_posix(): path.read_bytes()
                  for path in self.working.rglob("*") if path.is_file()}
        self.command()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        plan = json.loads((self.run / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["status"], "applied")
        self.assertTrue(any(row["path"].startswith("_processing/") and "/original." in row["path"]
                            for row in plan["publishedFiles"]))
        self.assertTrue(any(row["path"].startswith("_processing/") and row["path"].endswith("/detail.html")
                            for row in plan["publishedFiles"]))
        self.assertFalse(any(name in row["path"] for row in plan["publishedFiles"]
                             for name in retained_preparation.LEGACY_FOLDERS))
        for row in plan["photos"]:
            self.assertEqual(metadata.content_sha256(self.working / row["destination"]), row["preparedSHA256"])
            link = retained_preparation.verify_link(
                self.working, self.working / row["destination"], photo_id=row["photoId"],
            )
            self.assertEqual(link["current"], row["destination"])
            self.assertEqual(link["sourceSha256"], row["sha256"])
            self.assertEqual(link["currentSha256"], row["preparedSHA256"])
            self.assertTrue((self.working / link["detail"]).is_file())
        self.assertTrue((self.working / "_reports" / "library" / "people_gallery.html").is_file())
        self.assertTrue((self.working / "_reports" / "library" / "people_gallery_review.html").is_file())
        self.command(check=True)
        with mock.patch("screens.is_reel_ui", return_value=True), \
                mock.patch("screens.clean_box", side_effect=AssertionError("Never strip prepared native twice")):
            source = self.working / plan["photos"][0]["destination"]
            for framing in ("padded", "head", "chest"):
                payload = derivatives.render(source, framing, [.25, .1, .3, .3])
                with Image.open(io.BytesIO(payload)) as image:
                    self.assertEqual(image.size, (944, 1104))
        photo = SimpleNamespace(path=source, name=source.name, key="Angels/Fixed")
        output = io.StringIO()
        with mock.patch.object(likeness, "build", return_value=(
                {}, {}, self.working, None, SimpleNamespace(photos=[photo]))), \
                mock.patch.object(likeness, "person_box", side_effect=AssertionError("Never crop prepared native twice")), \
                contextlib.redirect_stdout(output):
            likeness.cmd_crop(SimpleNamespace(embedder=object(), undo=False, apply=False))
        self.assertIn("prepared source: skip legacy crop", output.getvalue())
        self.command(undo=True)
        for relative, payload in before.items():
            self.assertEqual((self.working / relative).read_bytes(), payload)
        self.assertTrue(all(metadata.content_sha256(self.source / path) == value[1]
                            for path, value in self.inputs.items()))

    def test_changed_preparation_or_source_refuses_resume(self):
        self.command(intake_only=True, apply=True)
        output, data = clean_preparation.verify(self.layout, self.run)
        selected = clean_preparation.selected_path(output, data["photos"][0])
        selected.write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.command()

    def test_every_published_artifact_is_checked_before_undo(self):
        self.command()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        plan = json.loads((self.run / "run.json").read_text(encoding="utf-8"))
        item = next(item for item in plan["publishedFiles"] if item["path"].startswith("_processing/"))
        (self.working / item["path"]).write_bytes(b"edited")
        with self.assertRaisesRegex(ValueError, "output changed"):
            self.command(undo=True)
        self.assertEqual(json.loads((self.run / "run.json").read_text())["status"], "applied")

    def test_stable_identity_and_names_migrate_only_for_one_to_one_membership(self):
        pid = "person_" + "a" * 32
        person = {
            "id": pid, "folder": "Potentials/Fia", "displayName": "Fia",
            "folderHistory": [], "identityAnchors": [], "protected": False,
            "automaticProtectionOverride": "disabled",
            "names": {"originalName": "Fia Stone", "currentName": "Fia Vale",
                      "originalSource": "catalogue-registration"},
        }
        catalog = {"people": {pid: person}, "photos": {}}
        rows = [{
            "oldFolder": "Potentials/Fia", "photoId": "photo:image_654321",
            "destination": "Prospects/Fia/gallery/fia_image_654321.png",
            "sha256": self.inputs["Potentials/Fia/gallery/fia_image_654321.jpg"][1],
            "preparedSHA256": "e" * 64,
        }]
        clean_rebase._migrate_continuity(catalog, rows, self.working, self.api.originals.images)
        self.assertEqual(person["folder"], "Prospects/Fia")
        self.assertEqual(person["folderHistory"], ["Potentials/Fia"])
        self.assertEqual(person["names"]["originalName"], "Fia Stone")
        self.assertEqual(person["automaticProtectionOverride"], "disabled")
        rows += [{**rows[0], "destination": "Potentials/Other/gallery/fia_image_654321.png"}]
        person["folder"] = "Potentials/Fia"
        with self.assertRaisesRegex(ValueError, "cannot migrate unambiguously"):
            clean_rebase._migrate_continuity(catalog, rows, self.working, self.api.originals.images)

    def test_one_to_one_identity_keeps_current_label_when_historical_label_is_occupied(self):
        first = {"id": "person_a", "folder": "Potentials/Eloise", "folderHistory": []}
        second = {"id": "person_b", "folder": "Potentials/Jade", "folderHistory": []}
        catalog = {"people": {"person_a": first, "person_b": second}, "photos": {}}
        rows = [
            {"oldFolder": first["folder"], "photoId": "photo:image_654321",
             "destination": "Potentials/Jade/gallery/one.jpg"},
            {"oldFolder": second["folder"], "photoId": "photo:image_345678",
             "destination": "Various/review/two.jpg", "bestMatch": "Potentials/Jade"},
        ]
        clean_rebase._migrate_continuity(catalog, rows, self.working, lambda folder: [])
        self.assertEqual(first["folder"], "Potentials/Eloise")
        self.assertEqual(second["folder"], "Potentials/Jade")
        self.assertEqual(rows[0]["destination"], "Potentials/Eloise/gallery/one.jpg")
        self.assertEqual(rows[1]["destination"], "Various/review/two.jpg")
        self.assertEqual(rows[1]["bestMatch"], "Potentials/Eloise")
        self.assertEqual(first["folderHistory"], [])

    def test_replan_resumes_failed_matching_only_after_verified_preparation(self):
        with mock.patch.object(clean_rebase, "_migrate_continuity",
                               side_effect=ValueError("test: stop after measurements")):
            with self.assertRaisesRegex(ValueError, "stop after measurements"):
                self.command()
        self.assertTrue((self.run / "intake.json").exists())
        intake = json.loads((self.run / "intake.json").read_text(encoding="utf-8"))
        receipt = intake["configurationReceipt"]
        self.assertEqual(len(receipt["sourceConfigurationSha256"]), 64)
        self.assertEqual(len(receipt["effectiveConfigurationSha256"]), 64)
        self.assertEqual(receipt["resolvedPaths"]["runDirectory"], str(self.run.resolve()))
        self.assertEqual(
            receipt["resolvedPaths"]["preparationOutput"],
            str((self.run / "inputs" / "_reports" / "preparation" / "all").resolve()),
        )
        self.assertTrue((self.run / "likeness-cache.json").exists())
        self.assertFalse((self.run / "run.json").exists())
        self.measured.clear()
        self.command(replan=True)
        plan = json.loads((self.run / "run.json").read_text())
        self.assertEqual(plan["status"], "preview")
        self.assertEqual(len(plan["configurationReceipt"]["effectiveConfigurationSha256"]), 64)
        self.assertEqual(
            plan["configurationReceipt"]["resolvedPaths"]["runDirectory"],
            str(self.run.resolve()),
        )
        self.assertTrue(plan["cacheMeasurementsReusedForReplan"])
        self.assertEqual(self.measured, [])
        selected = self.run / "inputs" / "_reports" / "preparation" / "all" / "manifest.json"
        selected.write_text("{}")
        (self.run / "run.json").unlink()
        with self.assertRaises(ValueError):
            self.command(replan=True)

    def test_unknown_current_inputs_refuse_matching_instead_of_disappearing(self):
        photo = self.working / "Various" / "gallery" / "extra_image_999999.jpg"
        Image.new("RGB", (640, 960), "green").save(photo)
        with self.assertRaisesRegex(ValueError, "outside immutable inputs"):
            self.command()
        self.assertFalse(self.measured)

    def test_missing_catalogued_input_requires_curation_review(self):
        relative = "Potentials/Fia/gallery/fia_image_654321.jpg"
        catalog_path = self.working / ".likeness-library.json"
        catalog = metadata.load_catalog(catalog_path)
        catalog["photos"]["photo:image_654321"] = {
            "contentSha256": self.inputs[relative][1], "protected": False,
        }
        metadata.save_catalog(catalog, catalog_path)
        (self.working / relative).unlink()
        with self.assertRaisesRegex(ValueError, "absent from active Working"):
            self.command()
        self.assertFalse(self.measured)

    def test_working_input_changes_after_preview_refuse_before_staging(self):
        self.command()
        photo = self.working / "Various" / "gallery" / "incoming_image_345678.jpg"
        photo.write_bytes(photo.read_bytes() + b"current edit")
        with self.assertRaisesRegex(ValueError, "Working inputs changed since"):
            self.command(apply=True)
        self.assertFalse((self.run / "staged").exists())

    def test_working_input_changes_during_staging_do_not_install(self):
        self.command()
        photo = self.working / "Various" / "gallery" / "incoming_image_345678.jpg"
        maintain = derivatives.maintain
        changed = False

        def during_staging(*args, **kwargs):
            nonlocal changed
            if not changed:
                photo.write_bytes(photo.read_bytes() + b"concurrent edit")
                changed = True
            return maintain(*args, **kwargs)

        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"), \
                mock.patch.object(derivatives, "maintain", side_effect=during_staging):
            with self.assertRaisesRegex(ValueError, "Working inputs changed during"):
                self.command(apply=True)
        self.assertTrue(photo.is_file())
        self.assertFalse(list((self.run / "previous").iterdir()))
        self.assertEqual(json.loads((self.run / "run.json").read_text())["status"], "preview")

    def test_existing_cast_derivatives_are_replaced_and_restored_exactly(self):
        source = self.working / "Angels/Fixed/gallery/fixed_image_123456.jpg"
        derivatives.maintain(source, [.25, .1, .3, .3], 100, apply=True)
        folder = source.parent.parent
        before = {path.relative_to(folder).as_posix(): path.read_bytes()
                  for path in folder.rglob("*") if path.is_file()}
        self.command()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        plan = json.loads((self.run / "run.json").read_text())
        self.assertIn("Angels/Fixed/944x1104/.photo-derivatives.json", plan["previousExternalHashes"])
        self.command(undo=True)
        after = {path.relative_to(folder).as_posix(): path.read_bytes()
                 for path in folder.rglob("*") if path.is_file()}
        self.assertEqual(after, before)

    def test_edited_existing_cast_derivative_is_never_overwritten(self):
        source = self.working / "Angels/Fixed/gallery/fixed_image_123456.jpg"
        derivatives.maintain(source, [.25, .1, .3, .3], 100, apply=True)
        target, _ = derivatives.verified(source, "padded")
        target.write_bytes(target.read_bytes() + b"manual edit")
        self.command()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            for preserve in (False, True):
                with self.assertRaisesRegex(ValueError, "Stale or edited"):
                    self.command(apply=True, preserve_legacy_derivatives=preserve)
        self.assertTrue(target.read_bytes().endswith(b"manual edit"))
        self.assertFalse((self.run / "staged").exists())

    def test_legacy_cast_collision_requires_opt_in_and_restores_exact_bytes(self):
        source = self.working / "Angels/Fixed/gallery/fixed_image_123456.jpg"
        target = source.parent.parent / derivatives.relative_target(source, "padded")
        target.parent.mkdir(parents=True)
        target.write_bytes(b"unowned legacy bytes, not claimed reproducible")
        original = target.read_bytes()
        self.command()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            with self.assertRaisesRegex(ValueError, "legacy.*preserve-legacy"):
                self.command(apply=True)
            self.assertFalse((self.run / "staged").exists())
            self.command(apply=True, preserve_legacy_derivatives=True)
        plan = json.loads((self.run / "run.json").read_text())
        relative = target.relative_to(self.working).as_posix()
        self.assertIn(relative, plan["previousExternalHashes"])
        self.assertEqual((self.run / "previous/external" / relative).read_bytes(), original)
        self.command(undo=True)
        self.assertEqual(target.read_bytes(), original)

    def completed_stage(self):
        self.command()
        verify_routes = clean_rebase._verify_routes

        def stop_after_staging(*args):
            verify_routes(*args)
            if (self.run / "staged").exists():
                raise ValueError("fixture pre-publication interruption")

        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"), \
                mock.patch.object(clean_rebase, "_verify_routes", side_effect=stop_after_staging):
            with self.assertRaisesRegex(ValueError, "fixture pre-publication"):
                self.command(apply=True)
        return json.loads((self.run / "run.json").read_text())

    def test_completed_stage_resume_checks_then_publishes_without_rebuilding_and_undoes(self):
        plan = self.completed_stage()
        # A rolled-back external-file swap leaves its directory-only skeleton.
        (self.run / "previous" / "external" / "Angels" / "Fixed" / "gallery").mkdir(parents=True)
        staged = self.run / "staged"
        before = {path.relative_to(staged).as_posix(): metadata.content_sha256(path)
                  for path in staged.rglob("*") if path.is_file()}
        result = self.command(check=True, resume_install=True)
        self.assertEqual(result["status"], "staged-verified")
        self.assertEqual(before, {path.relative_to(staged).as_posix(): metadata.content_sha256(path)
                                 for path in staged.rglob("*") if path.is_file()})
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"), \
                mock.patch.object(derivatives, "maintain", side_effect=AssertionError("no rebuild")), \
                mock.patch.object(retained_preparation, "stage_photo", side_effect=AssertionError("no copy")):
            self.command(apply=True, resume_install=True)
        self.command(check=True)
        self.command(undo=True)
        for row in plan["photos"]:
            self.assertEqual(metadata.content_sha256(self.working / row["source"]), row["sha256"])

    def test_completed_stage_resume_refuses_tampering_and_unpublished_state_changes(self):
        plan = self.completed_stage()
        staged = self.run / "staged"
        native = staged / plan["photos"][0]["destination"]
        original = native.read_bytes()
        native.write_bytes(original + b"edit")
        with self.assertRaisesRegex(ValueError, "staged native checksum"):
            self.command(check=True, resume_install=True)
        native.write_bytes(original)
        extra = staged / "unexpected.txt"
        extra.write_text("unaccounted", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "staged inventory"):
            self.command(check=True, resume_install=True)
        extra.unlink()
        marker = self.run / "previous" / "unknown.txt"
        marker.write_text("prior transaction evidence", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "empty previous"):
            self.command(check=True, resume_install=True)
        marker.unlink()
        folder = native.parent.parent
        manifest_path = derivatives.manifest_path(folder)
        manifest_bytes = manifest_path.read_bytes()
        target = folder / derivatives.relative_target(native, "padded")
        target_bytes = target.read_bytes()
        Image.new("RGB", derivatives.SIZE, "magenta").save(target)
        manifest = derivatives.load(folder)
        manifest["entries"][derivatives.relative_target(native, "padded").as_posix()]["sha256"] = (
            metadata.content_sha256(target)
        )
        derivatives.save(folder, manifest)
        with self.assertRaisesRegex(ValueError, "pixels differ"):
            self.command(check=True, resume_install=True)
        target.write_bytes(target_bytes)
        manifest_path.write_bytes(manifest_bytes)
        row = plan["photos"][0]
        link = retained_preparation.verify_link(staged, native, row["photoId"])
        artifact = staged / link["original"]
        artifact.write_bytes(artifact.read_bytes() + b"edit")
        with self.assertRaisesRegex(ValueError, "staged retained preparation"):
            self.command(check=True, resume_install=True)

    def test_retention_failure_restores_preview_and_exact_library_before_resume(self):
        self.completed_stage()
        journal = self.run / "run.json"
        preview = journal.read_bytes()
        original_catalog = (self.working / ".likeness-library.json").read_bytes()
        original_sources = {
            relative: (self.working / relative).read_bytes() for relative in self.inputs
        }
        staged = self.run / "staged"
        staged_hashes = {
            path.relative_to(staged).as_posix(): metadata.content_sha256(path)
            for path in staged.rglob("*") if path.is_file()
        }
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"), \
                mock.patch.object(storage_retention, "register_runs",
                                  side_effect=ValueError("fixture retention write failure")):
            with self.assertRaisesRegex(ValueError, "fixture retention write failure"):
                self.command(apply=True, resume_install=True)
        self.assertEqual(journal.read_bytes(), preview)
        self.assertEqual((self.working / ".likeness-library.json").read_bytes(), original_catalog)
        for relative, expected in original_sources.items():
            self.assertEqual((self.working / relative).read_bytes(), expected)
        self.assertEqual(staged_hashes, {
            path.relative_to(staged).as_posix(): metadata.content_sha256(path)
            for path in staged.rglob("*") if path.is_file()
        })
        self.command(check=True, resume_install=True)
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True, resume_install=True)
        self.command(check=True)
        self.command(undo=True)

    def test_oversized_run_write_preserves_existing_preview(self):
        self.command()
        journal = self.run / "run.json"
        before = journal.read_bytes()
        with mock.patch.object(storage_retention, "MAX_RUN_MANIFEST_BYTES", 1):
            with self.assertRaisesRegex(ValueError, "run manifest exceeds"):
                clean_rebase._write_json(journal, json.loads(before))
        self.assertEqual(journal.read_bytes(), before)

    def test_atomic_json_writer_preserves_existing_platform_serialization(self):
        value = {"schemaVersion": 1, "photos": [{"path": "example"}]}
        expected = self.run / "expected.json"
        expected.write_text(json.dumps(value, indent=2), encoding="utf-8")
        actual = self.run / "actual.json"
        clean_rebase._write_json(actual, value)
        self.assertEqual(actual.read_bytes(), expected.read_bytes())

    def test_grouped_run_retains_all_evidence_compactly_with_the_same_byte_bound(self):
        self.command()
        journal = self.run / "run.json"
        plan = json.loads(journal.read_text(encoding="utf-8"))
        plan["groupLifecycle"] = {"stages": [{
            "id": "test", "rows": [{"photoId": f"photo:image_{i}", "reason": "exact evidence"} for i in range(256)],
        }]}
        compact = json.dumps(plan, separators=(",", ":")).encode("utf-8")
        self.assertGreater(len(json.dumps(plan, indent=2).encode("utf-8")), len(compact) + 1)
        with mock.patch.object(storage_retention, "MAX_RUN_MANIFEST_BYTES", len(compact) + 1):
            clean_rebase._write_json(journal, plan)
        self.assertEqual(journal.read_bytes(), compact)
        self.assertEqual(storage_retention._read_json(journal), plan)
        with mock.patch.object(storage_retention, "MAX_RUN_MANIFEST_BYTES", len(compact) - 1):
            with self.assertRaisesRegex(ValueError, "run manifest exceeds"):
                clean_rebase._write_json(journal, plan)
        self.assertEqual(journal.read_bytes(), compact)

    def test_another_clean_start_preserves_prior_prepared_lineage_and_exact_undo(self):
        catalog_path = self.working / ".likeness-library.json"
        catalog = metadata.load_catalog(catalog_path)
        for relative, (_, digest) in self.inputs.items():
            if not relative.startswith("Artists/"):
                catalog["photos"][metadata.photo_id_from_name(pathlib.PurePosixPath(relative).name)] = {
                    "contentSha256": digest, "protected": False,
                }
        metadata.save_catalog(catalog, catalog_path)
        self.command()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        original_run = self.run
        first_plan = json.loads((original_run / "run.json").read_text())
        hashes = {row["path"]: row["sha256"] for row in first_plan["publishedFiles"]}
        first_catalog = catalog_path.read_bytes()
        self.run = self.working / "_sandbox-state" / "again"
        self.run.mkdir()
        with mock.patch.object(
            clean_rebase, "frozen_identity_cores", wraps=clean_rebase.frozen_identity_cores,
        ) as freeze:
            self.command()
        core_catalog = freeze.call_args_list[0].args[1]
        self.assertEqual(
            core_catalog["photos"]["photo:image_123456"]["contentSha256"],
            self.inputs["Angels/Fixed/gallery/fixed_image_123456.jpg"][1],
        )
        final_catalog = freeze.call_args_list[-1].args[1]
        plan = json.loads((self.run / "run.json").read_text())
        cast_row = next(row for row in plan["photos"] if row["photoId"] == "photo:image_123456")
        self.assertEqual(
            final_catalog["photos"]["photo:image_123456"]["contentSha256"],
            cast_row["preparedSHA256"],
        )
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        self.command(undo=True)
        self.assertEqual(catalog_path.read_bytes(), first_catalog)
        for relative, digest in hashes.items():
            self.assertEqual(metadata.content_sha256(self.working / relative), digest)
        self.run = original_run
        self.command(check=True)

    def test_loose_various_can_cluster_into_a_new_identity_and_publish(self):
        def cluster(candidates, cores, **kwargs):
            return {
                "assignments": [
                    {"photoId": row["photoId"], "destination": "Potentials/Generated", "reason": "Test cluster"}
                    for row in candidates
                ], "held": [],
                "clusters": [{
                    "clusterId": "test-cluster", "destination": "Potentials/Generated",
                    "photoIds": [row["photoId"] for row in candidates],
                }],
            }
        with mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=cluster):
            self.command()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        plan = json.loads((self.run / "run.json").read_text())
        incoming = next(row for row in plan["photos"] if row["source"].startswith("Various/gallery/"))
        self.assertTrue((self.working / incoming["destination"]).is_file())
        self.assertTrue(retained_preparation.verify_link(
            self.working, self.working / incoming["destination"],
        ))

    def test_name_reuse_cannot_reassign_a_photo_to_its_rejected_stable_identity(self):
        person_id = "person_" + "b" * 32
        relative = "Potentials/Fia/gallery/fia_image_654321.jpg"
        photo_id = "photo:image_654321"
        catalog_path = self.working / ".likeness-library.json"
        catalog = metadata.load_catalog(catalog_path)
        catalog["people"][person_id] = {
            "id": person_id, "folder": "Potentials/Fia", "displayName": "Fia",
            "folderHistory": [], "identityAnchors": [], "protected": False,
        }
        catalog["photos"][photo_id] = {
            "contentSha256": self.inputs[relative][1], "protected": False,
            "rejectedPersonIds": [person_id],
        }
        metadata.save_catalog(catalog, catalog_path)
        (self.working / relative).rename(self.working / "Various/gallery/fia_image_654321.jpg")

        def cluster(candidates, cores, **kwargs):
            return {
                "assignments": [{"photoId": photo_id, "destination": "Potentials/Generated",
                                 "reason": "Test historical-name reuse"}],
                "clusters": [{"clusterId": "test-rejected", "destination": "Potentials/Generated",
                              "photoIds": [photo_id]}],
                "held": [{"photoId": row["photoId"], "reason": "Other candidate held"}
                         for row in candidates if row["photoId"] != photo_id],
            }
        with mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=cluster):
            with self.assertRaisesRegex(ValueError, "destination identity was explicitly rejected"):
                self.command()
        self.assertEqual(metadata.load_catalog(catalog_path), catalog)
        self.assertFalse((self.run / "run.json").exists())

    def test_added_current_photos_block_undo_instead_of_disappearing(self):
        self.command()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        for relative in ("Various/gallery/new_image_999999.jpg", "Angels/Fixed/gallery/new_image_999999.jpg"):
            with self.subTest(relative=relative):
                path = self.working / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                Image.new("RGB", (640, 960), "green").save(path)
                with self.assertRaisesRegex(ValueError, "inventory changed"):
                    self.command(undo=True)
                self.assertTrue(path.is_file())
                self.assertEqual(json.loads((self.run / "run.json").read_text())["status"], "applied")
                path.unlink()


if __name__ == "__main__":
    unittest.main()
