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
from tools.art.likeness_library import clean_preparation, clean_rebase, derivatives, metadata, retained_preparation
from tools.art.likeness_library.policy import load_policy


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
                load_cfg=lambda: {}, photo_key=likeness.cw.photo_key,
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
            mock.patch.object(image_preparation.preparation_geometry, "detect_faces",
                              return_value=([[50., 40., 60., 70.]], "Test face")),
            mock.patch.object(image_preparation.pipeline.subjects, "detect", return_value=None),
            mock.patch.object(image_preparation.pipeline.fill, "fill",
                              side_effect=AssertionError("No clutter in fixture; do not load eraser")),
            mock.patch.object(clean_rebase, "validate_sandbox", return_value=self.layout),
            mock.patch.object(clean_rebase, "frozen_identity_cores", return_value=(
                {"Angels/Fixed": {"vector": np.array([1., 0.]), "side": "Prospects"}}, set(), [],
            )),
            mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=self.matches),
        ):
            patch.start()
            self.addCleanup(patch.stop)

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

    def test_inventory_preview_is_read_only_and_apply_requires_matching_preview(self):
        result = self.command(dry_run=True)
        self.assertEqual(result["inputCount"], 5)
        self.assertFalse((self.run / "inputs").exists())
        with self.assertRaisesRegex(ValueError, "review.*preview"):
            self.command(apply=True)
        self.assertFalse(self.measured)

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
        self.assertEqual(plan["preparation"]["inputCount"], 5)
        self.assertEqual(plan["preparation"]["artistCount"], 1)
        self.assertEqual(len(plan["photos"]), 4)
        self.assertTrue(all(self.run in path.parents for path in self.measured))
        self.assertTrue(any(row["preparedSHA256"] != row["sha256"] for row in plan["photos"]))
        named = next(row for row in plan["photos"] if "Known Person" in row["source"])
        self.assertTrue(named["destination"].startswith("Potentials/Known Person/gallery/"))
        self.assertEqual(manifest.read_bytes(), unchanged)

    def test_missing_id_review_collisions_preserve_both_sources_and_recover_exactly(self):
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
            self.assertIn("filename disambiguated", row["reason"])
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

    def test_apply_retains_versions_and_originals_and_undo_restores_cast_and_pool(self):
        before = {path.relative_to(self.working).as_posix(): path.read_bytes()
                  for path in self.working.rglob("*") if path.is_file()}
        self.command()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            self.command(apply=True)
        plan = json.loads((self.run / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["status"], "applied")
        self.assertTrue(any("/gallery_org/" in row["path"] for row in plan["publishedFiles"]))
        self.assertTrue(any("/gallery_intake/" in row["path"] for row in plan["publishedFiles"]))
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
        item = next(item for item in plan["publishedFiles"] if "gallery_intake" in item["path"])
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
        self.assertTrue((self.run / "likeness-cache.json").exists())
        self.assertFalse((self.run / "run.json").exists())
        self.measured.clear()
        self.command(replan=True)
        plan = json.loads((self.run / "run.json").read_text())
        self.assertEqual(plan["status"], "preview")
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
        self.assertIn("Angels/Fixed/.photo-derivatives.json", plan["previousExternalHashes"])
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
            with self.assertRaisesRegex(ValueError, "Stale or edited"):
                self.command(apply=True)
        self.assertTrue(target.read_bytes().endswith(b"manual edit"))
        self.assertFalse((self.run / "staged").exists())

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
        core_catalog = freeze.call_args.args[1]
        self.assertEqual(
            core_catalog["photos"]["photo:image_123456"]["contentSha256"],
            self.inputs["Angels/Fixed/gallery/fixed_image_123456.jpg"][1],
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
