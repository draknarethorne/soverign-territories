"""Clean rebase must flatten old groups, isolate references, and stage reversibly."""
import contextlib
import hashlib
import io
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

from tools.art import likeness
from tools.art.likeness_library import clean_rebase, metadata
from tools.art.likeness_library.policy import load_policy
from tools.art.likeness_library.reconciliation import _average_linkage


class CleanRebaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = pathlib.Path(self.temporary.name)
        self.source = self.base / "Source"
        self.working = self.base / "Working"
        self.run = self.working / "_sandbox-state" / "clean"
        self.run.mkdir(parents=True)
        self.relative = "Potentials/Fia/gallery/fia_image_123456.jpg"
        self.source_photo = self.source / pathlib.Path(self.relative)
        self.source_photo.parent.mkdir(parents=True)
        self.source_photo.write_bytes(b"photo bytes")
        self.digest = hashlib.sha256(b"photo bytes").hexdigest()
        self.layout = {
            "source_root": self.source, "working_root": self.working,
            "sandbox_root": self.base,
            "manifest_files": {self.relative: (11, self.digest)},
        }
        (self.base / "source-manifest.json").write_text("{}", encoding="utf-8")

    def image_inventory_mock(self):
        categories = {"Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various"}

        def inventory(root):
            root = pathlib.Path(root)
            return sorted(
                path for path in root.rglob("*")
                if path.is_file()
                and path.relative_to(root).parts[0] in categories
                and path.parent.name in ("gallery", "review")
                and not any(part.startswith((".", "_")) for part in path.relative_to(root).parts)
                and path.suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
            )

        return SimpleNamespace(inventory=inventory)

    def plan(self):
        return {
            "status": "preview",
            "photos": [{
                "source": self.relative,
                "destination": "Angels/Angelica/review/fia_image_123456.jpg",
                "sha256": self.digest,
            }],
        }

    def test_inventory_preview_explains_cast_seed_mode_without_evaluating_it(self):
        for mode in ("all", "core"):
            with self.subTest(mode=mode):
                args = SimpleNamespace(
                    root=str(self.working), run_dir=str(self.run), policy=None,
                    apply=False, check=False, dry_run=True, undo=False, replan=False,
                    cast_seeds=mode,
                )
                output = io.StringIO()
                with mock.patch.object(clean_rebase, "validate_sandbox", return_value=self.layout), \
                        mock.patch.object(clean_rebase, "require_sandbox_output", return_value=self.run), \
                        mock.patch.object(clean_rebase.clean_preparation, "inventory", return_value={
                            self.relative: self.digest,
                        }), \
                        mock.patch.object(clean_rebase, "create_plan") as matching, \
                        mock.patch.object(clean_rebase, "_cast_seed_outcomes") as seeds, \
                        contextlib.redirect_stdout(output):
                    result = clean_rebase.command(args, SimpleNamespace())
                self.assertEqual(result, {"status": "inventory", "inputCount": 1})
                matching.assert_not_called()
                seeds.assert_not_called()
                self.assertIn(f"Cast-seed policy: {mode}.", output.getvalue())
                self.assertIn("no cast retention/release decisions or matching were evaluated", output.getvalue())
                if mode == "core":
                    self.assertIn("eligible releases under configured thresholds", output.getvalue())
                    self.assertNotIn("retain existing cast membership", output.getvalue())
                else:
                    self.assertIn("retain existing cast membership", output.getvalue())

    def test_core_seed_policy_preserves_protection_and_releases_only_noncore_cast(self):
        folder = "Angels/Angelica"
        names = {
            "anchor": "angelica_image_111111.jpg",
            "core": "angelica_image_222222.jpg",
            "protected": "angelica_image_333333.jpg",
            "workflow": "angelica_image_444444.jpg",
            "low": "angelica_image_555555.jpg",
        }
        entries = []
        for key, name in names.items():
            path = self.source / folder / "gallery" / name
            entries.append((
                path.relative_to(self.source).as_posix(),
                clean_rebase.Photo(
                    path, "Angels", "Angelica", key,
                    {"v": [1., 0.], "faces": 1, "px": 100},
                ),
                "gallery",
                key,
            ))
        ids = {key: metadata.photo_id_from_name(name) for key, name in names.items()}
        catalog = {
            "people": {
                "angelica": {
                    "folder": folder, "identityAnchors": [ids["anchor"]], "protected": False,
                },
            },
            "photos": {ids["protected"]: {"protected": True}},
        }
        core = {
            "corePhotoIds": [ids["anchor"], ids["core"]],
            "photoScores": {
                names["anchor"]: .8, names["core"]: .7, names["protected"]: .6,
                names["workflow"]: .5, names["low"]: .1,
            },
        }
        api = SimpleNamespace(cw=SimpleNamespace(
            photo_key=lambda name: pathlib.Path(name).stem,
        ))
        retained, released, evidence = clean_rebase._cast_seed_outcomes(
            entries, {folder: core}, catalog,
            {pathlib.Path(names["workflow"]).stem}, load_policy(), api, "core", 60,
        )
        self.assertEqual(len(retained), 4)
        self.assertEqual(set(released), {f"{folder}/gallery/{names['low']}"})
        low = evidence[f"{folder}/gallery/{names['low']}"]
        self.assertFalse(low["retainedCast"])
        self.assertTrue(low["releasedCast"])
        self.assertEqual(low["castSeedScore"], .1)
        self.assertEqual(low["castSeedThreshold"], .3)
        self.assertTrue(any(row["castSeedAnchor"] for row in retained))
        self.assertTrue(any(row["castSeedProtectedPhoto"] for row in retained))
        self.assertTrue(any(row["castSeedWorkflowSelected"] for row in retained))

    def test_core_seed_policy_refuses_undersized_unprotected_identity(self):
        folder = "Sisters/Drakniss"
        name = "drakniss_image_123456.jpg"
        path = self.source / folder / "gallery" / name
        photo = clean_rebase.Photo(
            path, "Sisters", "Drakniss", "digest",
            {"v": [1., 0.], "faces": 1, "px": 100},
        )
        entry = (path.relative_to(self.source).as_posix(), photo, "gallery", "digest")
        core = {
            "corePhotoIds": [], "photoScores": {name: .1},
        }
        api = SimpleNamespace(cw=SimpleNamespace(photo_key=lambda value: value))
        with self.assertRaisesRegex(ValueError, "below the configured 4-photo"):
            clean_rebase._cast_seed_outcomes(
                [entry], {folder: core}, {"people": {}, "photos": {}},
                set(), load_policy(), api, "core", 60,
            )

    def test_released_cast_routes_require_core_policy_and_threshold_evidence(self):
        relative = "Angels/Angelica/gallery/angelica_image_123456.jpg"
        path = self.source / pathlib.Path(relative)
        path.parent.mkdir(parents=True)
        path.write_bytes(b"cast source")
        row = {
            "source": relative,
            "destination": "Various/review/angelica_image_123456.jpg",
            "sha256": hashlib.sha256(b"cast source").hexdigest(),
            "retainedCast": False,
            "releasedCast": True,
            "castSeedScore": .12,
            "castSeedThreshold": load_policy()["categoryPolicies"]["Angels"][
                "identityCoreMinimumSimilarity"
            ],
            "castSeedCore": False,
            "castSeedAnchor": False,
            "castSeedProtectedIdentity": False,
            "castSeedProtectedPhoto": False,
            "castSeedWorkflowSelected": False,
            "castSeedDecision": "released",
            "castSeedReason": "outside current core",
        }
        plan = {
            "photos": [row], "castSeedPolicy": "core", "policy": load_policy(),
        }
        clean_rebase._verify_routes(plan, self.source)
        plan["castSeedPolicy"] = "all"
        with self.assertRaisesRegex(ValueError, "cannot change cast membership"):
            clean_rebase._verify_routes(plan, self.source)

    def test_install_preserves_cast_core_and_old_categories_and_checks_every_copy(self):
        old = self.working / "Potentials" / "Old" / "gallery"
        old.mkdir(parents=True)
        (old / "old.jpg").write_bytes(b"old")
        cast = self.working / "Angels" / "Angelica" / "gallery"
        cast.mkdir(parents=True)
        (cast / "anchor.jpg").write_bytes(b"anchor")
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            plan = self.plan()
            clean_rebase.install_plan(self.layout, self.run, plan)
        self.assertEqual(plan["status"], "applied")
        self.assertEqual((cast / "anchor.jpg").read_bytes(), b"anchor")
        self.assertEqual(
            (cast.parent / "review" / self.source_photo.name).read_bytes(), b"photo bytes"
        )
        self.assertEqual(
            (self.run / "previous" / "Potentials" / "Old" / "gallery" / "old.jpg").read_bytes(),
            b"old",
        )
        self.assertEqual(self.source_photo.read_bytes(), b"photo bytes")
        clean_rebase.undo_plan(self.layout, self.run, plan)
        self.assertEqual(plan["status"], "undone")
        self.assertEqual((old / "old.jpg").read_bytes(), b"old")
        self.assertFalse((cast.parent / "review" / self.source_photo.name).exists())
        self.assertEqual((cast / "anchor.jpg").read_bytes(), b"anchor")

    def test_rejects_cast_gallery_destination_and_changed_source_before_install(self):
        plan = self.plan()
        plan["photos"][0]["destination"] = "Angels/Angelica/gallery/new.jpg"
        with self.assertRaisesRegex(ValueError, "never the cast core"):
            clean_rebase._verify_routes(plan, self.source)
        plan = self.plan()
        self.source_photo.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "source changed"):
            clean_rebase._verify_routes(plan, self.source)
        self.assertFalse((self.run / "previous").exists())

    def prepare_catalogue(self):
        catalog_path = self.run / "catalog.json"
        metadata.save_catalog(
            {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
            catalog_path,
        )
        plan = self.plan()
        plan["catalogSHA256"] = metadata.content_sha256(catalog_path)
        return plan

    def test_catalogue_and_various_hold_install_undo_preserve_previous_bytes(self):
        local = self.working / ".likeness-library.json"
        previous = b'{"schemaVersion":1,"people":{},"photos":{},"actions":[]}\n'
        local.write_bytes(previous)
        plan = self.prepare_catalogue()
        plan["photos"][0]["destination"] = f"Various/review/{self.source_photo.name}"
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            clean_rebase.install_plan(self.layout, self.run, plan)
        destination = self.working / plan["photos"][0]["destination"]
        self.assertEqual(destination.read_bytes(), b"photo bytes")
        self.assertEqual(metadata.load_catalog(local), metadata.load_catalog(self.run / "catalog.json"))
        self.assertEqual((self.run / "previous-catalog.json").read_bytes(), previous)
        clean_rebase.undo_plan(self.layout, self.run, plan)
        self.assertEqual(local.read_bytes(), previous)
        self.assertFalse(destination.exists())
        self.assertEqual(self.source_photo.read_bytes(), b"photo bytes")

    def test_current_various_overlay_replaces_by_id_and_preserves_raw_versions(self):
        import json

        for category in ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various"):
            (self.source / category).mkdir(parents=True, exist_ok=True)
            (self.working / category).mkdir(parents=True, exist_ok=True)
        current_gallery = self.working / "Various" / "gallery"
        current_gallery.mkdir(parents=True, exist_ok=True)
        changed = current_gallery / "incoming_image_123456.jpg"
        changed.write_bytes(b"new working bytes")
        added = current_gallery / "incoming_image_654321.jpg"
        added.write_bytes(b"new stable ID")
        no_id = current_gallery / "incoming_without_id.jpg"
        no_id.write_bytes(b"new unlabelled image")
        run = self.working / "_sandbox-state" / "overlay-run"
        run.mkdir(parents=True)

        layout = {
            **self.layout,
            "source_root": self.source,
            "working_root": self.working,
            "sandbox_root": self.base,
            "manifest_files": {self.relative: (11, self.digest)},
        }
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            rows, current = clean_rebase._current_various_overlay_rows(layout)
            self.assertEqual(len(rows), 1)
            self.assertEqual(len(current), 3)
            overlay_layout = clean_rebase._create_source_overlay(layout, run)
        manifest = json.loads((run / "source-overlay" / "overlay.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["immutableInputCount"], 1)
        self.assertEqual(manifest["replacementCount"], 1)
        self.assertEqual(manifest["newInputCount"], 2)
        overlay_path = overlay_layout["source_root"] / self.relative
        self.assertEqual(overlay_path.read_bytes(), b"new working bytes")
        self.assertEqual(self.source_photo.read_bytes(), b"photo bytes")
        recovery = manifest["rawRecovery"]
        self.assertEqual(len(recovery), 4)
        self.assertEqual(
            {record["role"] for record in recovery},
            {"immutable-original", "working-various"},
        )
        recovered = {
            record["role"]: (run / "source-overlay" / record["path"]).read_bytes()
            for record in recovery
            if record["role"] == "immutable-original"
            or record["source"].endswith("incoming_image_123456.jpg")
        }
        self.assertEqual(recovered["immutable-original"], b"photo bytes")
        self.assertEqual(recovered["working-various"], b"new working bytes")

        (run / "source-overlay").joinpath(*pathlib.PurePosixPath(recovery[0]["path"]).parts).write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "raw recovery copy changed"):
            clean_rebase._verify_source_overlay(layout, run)

    def test_working_baseline_covers_current_galleries_and_excludes_source_only_inputs(self):
        import json

        current = self.working / self.relative
        current.parent.mkdir(parents=True)
        current.write_bytes(b"current assigned bytes")
        historical_only = self.source / "Angels/Old/gallery/old_image_888888.jpg"
        historical_only.parent.mkdir(parents=True)
        historical_only.write_bytes(b"no longer active")
        added_relative = "Artists/Painter/New/gallery/new_image_777777.jpg"
        added = self.working / added_relative
        added.parent.mkdir(parents=True)
        added.write_bytes(b"new assigned artist")
        incoming = self.working / "Various/gallery/incoming_image_123456.jpg"
        incoming.parent.mkdir(parents=True)
        incoming.write_bytes(b"new incoming replacement")
        (self.working / "_reports").mkdir()
        (self.working / "_reports/not_an_input.jpg").write_bytes(b"generated")

        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            layout = clean_rebase._create_source_overlay(self.layout, self.run, current_working=True)
            rows = clean_rebase.clean_preparation.inventory(layout)
            curation = clean_rebase._curation_inventory(layout)

        self.assertEqual(set(rows), {self.relative, added_relative})
        self.assertEqual(rows[self.relative], metadata.content_sha256(incoming))
        self.assertEqual(curation[self.relative], metadata.content_sha256(current))
        self.assertNotIn(historical_only.relative_to(self.source).as_posix(), rows)
        self.assertEqual(self.source_photo.read_bytes(), b"photo bytes")
        receipt = json.loads((self.run / "source-overlay/overlay.json").read_text())
        self.assertEqual(receipt["baselineMode"], "working")
        self.assertEqual(receipt["baselineInputCount"], 2)
        self.assertEqual(receipt["immutableInputCount"], 0)
        self.assertEqual(list((self.working / "_tmp").iterdir()), [])

    def test_overlay_copy_failure_cleans_owner_locked_stage(self):
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}), \
                mock.patch.object(clean_rebase.shutil, "copy2", side_effect=OSError("copy failed")):
            with self.assertRaisesRegex(OSError, "copy failed"):
                clean_rebase._create_source_overlay(self.layout, self.run)

        self.assertFalse((self.run / "source-overlay").exists())
        self.assertEqual(list((self.working / "_tmp").iterdir()), [])

    def test_curation_retains_verified_original_beside_overlay_replacement(self):
        original = self.working / self.relative
        original.parent.mkdir(parents=True)
        original.write_bytes(self.source_photo.read_bytes())
        incoming = self.working / "Various" / "gallery" / "incoming_image_123456.jpg"
        incoming.parent.mkdir(parents=True)
        incoming.write_bytes(b"new working bytes")
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            layout = clean_rebase._create_source_overlay(self.layout, self.run)
            current = clean_rebase._curation_inventory(layout)
            self.assertEqual(current[self.relative], self.digest)
            self.assertEqual(
                current[incoming.relative_to(self.working).as_posix()],
                metadata.content_sha256(incoming),
            )
            self.assertEqual(len(current), 2)

            original.write_bytes(b"unverified original changes")
            with self.assertRaisesRegex(ValueError, "not safely isolated"):
                clean_rebase._curation_inventory(layout)
            original.write_bytes(self.source_photo.read_bytes())

            extra = self.working / "Models" / "Other" / "gallery" / original.name
            extra.parent.mkdir(parents=True)
            extra.write_bytes(original.read_bytes())
            with self.assertRaisesRegex(ValueError, "not safely isolated"):
                clean_rebase._curation_inventory(layout)
            extra.unlink()

            layout["source_overlay_manifest"]["currentVarious"][0]["target"] = "Various/gallery/other.jpg"
            with self.assertRaisesRegex(ValueError, "not safely isolated"):
                clean_rebase._curation_inventory(layout)
            layout["source_overlay_manifest"]["currentVarious"][0]["target"] = self.relative
            moved = self.working / "Angels" / "Angelica" / "review" / original.name
            moved.parent.mkdir(parents=True)
            original.rename(moved)
            current = clean_rebase._curation_inventory(layout)
            self.assertEqual(current[moved.relative_to(self.working).as_posix()], self.digest)
            self.assertEqual(len(current), 2)

    def test_overlay_isolates_timestamp_collisions_and_deduplicates_exact_copies(self):
        import json

        for category in ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various"):
            (self.source / category).mkdir(parents=True, exist_ok=True)
            (self.working / category).mkdir(parents=True, exist_ok=True)
        source = self.source / "Potentials" / "Lyra" / "gallery" / "lyra_caldwell_shot_20261010125400.jpg"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"immutable Lyra photo")
        various = self.working / "Various"
        (various / "gallery").mkdir(parents=True)
        (various / "review").mkdir(parents=True)
        screenshot = various / "gallery" / "Screenshot_20261010_125400_Facebook.jpg"
        screenshot.write_bytes(b"different screenshot sharing a timestamp")
        lyra = various / "review" / source.name
        lyra.write_bytes(source.read_bytes())
        duplicate_name = "Screenshot_20260902_203835_Facebook.jpg"
        duplicate_a = various / "gallery" / duplicate_name
        duplicate_b = various / "gallery" / "Screenshot_20260902_203835_Facebook (1).jpg"
        duplicate_a.write_bytes(b"same incoming image")
        duplicate_b.write_bytes(b"same incoming image")
        no_id = various / "gallery" / "local_image_without_id.jpg"
        no_id.write_bytes(b"unlabelled incoming image")

        run = self.working / "_sandbox-state" / "collision-run"
        run.mkdir(parents=True)
        relative = source.relative_to(self.source).as_posix()
        layout = {
            **self.layout,
            "source_root": self.source,
            "working_root": self.working,
            "sandbox_root": self.base,
            "manifest_files": {
                self.relative: (11, self.digest),
                relative: (source.stat().st_size, hashlib.sha256(source.read_bytes()).hexdigest()),
            },
        }
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            overlay_layout = clean_rebase._create_source_overlay(layout, run)
        manifest = json.loads((run / "source-overlay" / "overlay.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["immutableInputCount"], 2)
        self.assertEqual(manifest["newInputCount"], 3)
        self.assertEqual(manifest["workingVariousCount"], 5)
        self.assertTrue(any(row["sanitized"] for row in manifest["currentVarious"]))
        self.assertEqual(
            overlay_layout["manifest_files"][relative][1],
            hashlib.sha256(source.read_bytes()).hexdigest(),
        )
        self.assertEqual(source.read_bytes(), b"immutable Lyra photo")
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            current_inputs = clean_rebase._curation_inventory(overlay_layout)
        self.assertEqual(len(current_inputs), 5)
        self.assertTrue(any(record["role"] == "working-various-duplicate" for record in manifest["rawRecovery"]))

    def test_undo_removes_created_local_catalogue(self):
        plan = self.prepare_catalogue()
        local = self.working / ".likeness-library.json"
        self.assertFalse(local.exists())
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            clean_rebase.install_plan(self.layout, self.run, plan)
        self.assertTrue(local.is_file())
        clean_rebase.undo_plan(self.layout, self.run, plan)
        self.assertFalse(local.exists())

    def test_changed_local_catalogue_prevents_rebuild_undo(self):
        plan = self.prepare_catalogue()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            clean_rebase.install_plan(self.layout, self.run, plan)
        local = self.working / ".likeness-library.json"
        local.write_bytes(local.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "catalogue changed"):
            clean_rebase.undo_plan(self.layout, self.run, plan)
        self.assertEqual(plan["status"], "applied")
        self.assertTrue((self.working / plan["photos"][0]["destination"]).is_file())

    def test_creation_uses_empty_cache_and_only_cast_references(self):
        cast_folder = self.source / "Angels" / "Angelica"
        (cast_folder / "gallery").mkdir(parents=True)
        (cast_folder / "gallery" / "angelica_image_654321.jpg").write_bytes(b"cast")
        api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: {},
                storage_root=likeness.cw.storage_root,
                photo_folders=lambda cfg, root: [
                    ("Potentials", "Fia", self.source_photo.parent.parent),
                    ("Angels", "Angelica", cast_folder),
                ],
                photo_key=likeness.cw.photo_key,
            ),
            settings=likeness.settings, originals=likeness.originals,
            nz=likeness.nz, chosen_keys=lambda cfg: set(),
            invent_name=lambda seed, taken: "New Person",
        )

        def fake_cores(space, catalog, **kwargs):
            self.assertEqual(set(space.by_key), {"Angels/Angelica"})
            self.assertTrue(all(photo.group == "Angels" for photo in space.photos))
            return {"Angels/Angelica": {"vector": np.array([1., 0.])}}, set(), []

        def fake_plan(candidates, cores, **kwargs):
            self.assertEqual(len(candidates), 1)
            self.assertEqual(
                candidates[0]["photoId"],
                metadata.photo_id_from_name(
                    likeness.originals.standard_name(self.source_photo.name, "incoming"),
                ),
            )
            self.assertEqual(candidates[0]["sourceFolder"], "Various")
            self.assertEqual(candidates[0]["sourceBucket"], "Pool")
            self.assertEqual(set(cores), {"Angels/Angelica"})
            return {
                "assignments": [], "clusters": [],
                "held": [{
                    "photoId": candidates[0]["photoId"],
                    "reviewDestination": "Angels/Angelica/review",
                    "reason": "cast review",
                }],
            }

        with mock.patch.object(clean_rebase, "frozen_identity_cores", side_effect=fake_cores), \
                mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=fake_plan):
            class FixtureEmbedder:
                evidence_root = None

                def configure_evidence(self, root, library_root=None):
                    self.evidence_root = pathlib.Path(root)

                def __call__(self, path):
                    return {
                        "v": [1., 0.] if "fia" in path.name else [0., 1.],
                        "faces": 1, "s": .95, "px": 100,
                    }

            fixture_embedder = FixtureEmbedder()
            result = clean_rebase.create_plan(
                self.layout, self.run, load_policy(), api,
                embedder=fixture_embedder,
            )
            self.assertEqual(
                fixture_embedder.evidence_root,
                self.working / "_likeness" / "general" / "face-evidence",
            )
            unused_embedder = mock.Mock(
                side_effect=AssertionError("replan must reuse its own measurements"),
            )
            unused_embedder.needs_alignment_evidence.return_value = False
            with mock.patch.object(api, "Embedder", create=True, return_value=unused_embedder):
                replanned = clean_rebase.create_plan(
                    self.layout, self.run, load_policy(), api, reuse_measurements=True,
                )
            self.assertTrue(replanned["cacheMeasurementsReusedForReplan"])
            class EvidenceRefreshingEmbedder:
                def __init__(self):
                    self.calls = []
                    self.evidence_root = None

                def configure_evidence(self, root, library_root=None):
                    self.evidence_root = pathlib.Path(root)

                def needs_alignment_evidence(self, data, _path):
                    return data.get("alignmentEvidence") != {"state": "persisted"}

                def __call__(self, path):
                    self.calls.append(pathlib.Path(path))
                    return {
                        "v": [1., 0.] if "fia" in path.name else [0., 1.],
                        "faces": 1, "s": .95, "px": 100,
                        "alignmentEvidence": {"state": "persisted"},
                    }

            refreshing_embedder = EvidenceRefreshingEmbedder()
            clean_rebase.create_plan(
                self.layout, self.run, load_policy(), api, embedder=refreshing_embedder,
                reuse_measurements=True,
            )
            self.assertEqual(len(refreshing_embedder.calls), 2)
            self.assertEqual(
                refreshing_embedder.evidence_root,
                self.working / "_likeness" / "general" / "face-evidence",
            )
            import json
            saved_cache = json.loads((self.run / "likeness-cache.json").read_text(encoding="utf-8"))
            self.assertTrue(all(
                row["alignmentEvidence"] == {"state": "persisted"}
                for row in saved_cache["emb"].values()
            ))
        self.assertTrue(result["embeddingCacheStartedEmpty"])
        self.assertEqual(result["referenceFolders"], ["Angels/Angelica"])
        self.assertEqual(result["candidateCount"], 1)
        with self.assertRaisesRegex(ValueError, "empty embedding cache"):
            clean_rebase.create_plan(self.layout, self.run, load_policy(), api)

    def test_creation_accepts_raw_download_id_without_source_rename(self):
        relative = "Various/gallery/.facebook_1792598648554_7518703682028564674.jpg"
        path = self.source / pathlib.Path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.source_photo.rename(path)
        self.layout["manifest_files"] = {relative: (11, self.digest)}
        self.relative, self.source_photo = relative, path
        self.test_creation_uses_empty_cache_and_only_cast_references()
        self.assertTrue(path.is_file())
        import json
        plan = json.loads((self.run / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["actions"], [])

    def test_incoming_ids_never_override_ambiguous_or_existing_ids(self):
        names = [
            ".facebook_123_654321.jpg", "incoming_image_654321.jpg",
            ".facebook_123_111111.jpg", "facebook_456_111111.jpg",
            ".facebook_123_222222.jpg", "unknown.jpg",
        ]
        photos = [
            SimpleNamespace(path=self.source / "Various" / "gallery" / name,
                            name=name, group="Various")
            for name in names
        ]
        ids = clean_rebase._matching_photo_ids(photos, self.source, likeness)
        self.assertEqual(list(ids.values()), [
            None, "photo:image_654321", None, None, "photo:image_222222", None,
        ])

    def test_inferred_id_normalizes_only_prepared_destination(self):
        selected = self.run / "selected.png"
        selected.write_bytes(b"selected pixels")
        source = "Various/gallery/.facebook_123_222222.jpg"
        row = {
            "source": source, "destination": "Prospects/New Person/gallery/.facebook_123_222222.jpg",
            "photoId": "photo:image_222222", "sha256": self.digest,
        }
        with mock.patch.object(clean_rebase.clean_preparation, "selected_path", return_value=selected):
            clean_rebase._bind_preparation(
                [row], {source: {"outcome": "compared", "source": source}}, self.run, likeness,
            )
        self.assertEqual(row["source"], source)
        self.assertEqual(
            row["destination"], "Prospects/New Person/gallery/new_person_image_222222.png",
        )
        self.assertEqual(row["preparedSHA256"], metadata.content_sha256(selected))

    def test_creation_core_seed_policy_routes_released_cast_images_as_candidates(self):
        cast_folder = self.source / "Angels" / "Angelica"
        cast_names = [
            "angelica_image_111111.jpg", "angelica_image_222222.jpg",
            "angelica_image_333333.jpg", "angelica_image_444444.jpg",
            "angelica_image_555555.jpg", "angelica_image_666666.jpg",
        ]
        cast_digests = {}
        for index, name in enumerate(cast_names):
            path = cast_folder / "gallery" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            data = f"cast image {index}".encode()
            path.write_bytes(data)
            cast_digests[name] = hashlib.sha256(data).hexdigest()
            relative = path.relative_to(self.source).as_posix()
            self.layout["manifest_files"][relative] = (len(data), cast_digests[name])

        anchor_id = metadata.photo_id_from_name(cast_names[0])
        protected_id = metadata.photo_id_from_name(cast_names[4])
        person_id = "person_" + "a" * 32
        catalog_path = self.working / ".likeness-library.json"
        metadata.save_catalog({
            "schemaVersion": 1,
            "people": {
                person_id: {
                    "id": person_id, "folder": "Angels/Angelica",
                    "displayName": "Angelica", "folderHistory": [],
                    "identityAnchors": [anchor_id], "protected": False,
                },
            },
            "photos": {
                anchor_id: {
                    "contentSha256": cast_digests[cast_names[0]], "protected": False,
                },
                protected_id: {
                    "contentSha256": cast_digests[cast_names[4]], "protected": True,
                },
            },
            "actions": [],
        }, catalog_path)
        api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: {},
                photo_folders=lambda cfg, root: [
                    ("Potentials", "Fia", self.source_photo.parent.parent),
                    ("Angels", "Angelica", cast_folder),
                ],
                photo_key=likeness.cw.photo_key,
            ),
            settings=likeness.settings, originals=likeness.originals,
            nz=likeness.nz,
            junk_reason=lambda photo, _settings: (
                "synthetic unusable face" if photo.name == cast_names[3] else None
            ),
            chosen_keys=lambda cfg: {likeness.cw.photo_key(cast_names[5])},
            invent_name=lambda seed, taken: f"New-{seed[-6:]}",
        )

        def fake_cores(_space, _catalog, **_kwargs):
            ids = [metadata.photo_id_from_name(name) for name in cast_names]
            return {
                "Angels/Angelica": {
                    "vector": np.array([1., 0.]), "side": "Prospects",
                    "category": "Angels", "personIds": [person_id],
                    "identityProtected": False, "mode": "trusted",
                    "corePhotoIds": [ids[0], ids[1], ids[2], ids[4]],
                    "photoScores": {
                        name: (.1 if name == cast_names[3] else .8)
                        for name in cast_names
                    },
                },
            }, set(), []

        def fake_plan(candidates, cores, **_kwargs):
            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0]["photoId"], metadata.photo_id_from_name("fia_image_123456.jpg"))
            self.assertEqual(set(cores), {"Angels/Angelica"})
            return {
                "assignments": [], "clusters": [],
                "held": [{
                    "photoId": candidate["photoId"],
                    "reason": "review candidate",
                } for candidate in candidates],
            }

        with mock.patch.object(clean_rebase.metadata, "path_for_root", return_value=catalog_path), \
                mock.patch.object(clean_rebase, "frozen_identity_cores", side_effect=fake_cores), \
                mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=fake_plan):
            result = clean_rebase.create_plan(
                self.layout, self.run, load_policy(), api,
                embedder=lambda _path: {
                    "v": [1., 0.], "faces": 1, "s": .95, "px": 100,
                },
                cast_seeds="core",
            )

        by_id = {row["photoId"]: row for row in result["photos"]}
        self.assertEqual(result["castSeedPolicy"], "core")
        self.assertTrue(by_id[anchor_id]["retainedCast"])
        self.assertTrue(by_id[protected_id]["retainedCast"])
        self.assertTrue(by_id[metadata.photo_id_from_name(cast_names[5])]["retainedCast"])
        released_id = metadata.photo_id_from_name(cast_names[3])
        self.assertTrue(by_id[released_id]["releasedCast"])
        self.assertFalse(by_id[released_id]["retainedCast"])
        self.assertIsNone(by_id[released_id]["castSeedScore"])
        self.assertEqual(by_id[released_id]["destination"].split("/")[0], "Various")
        self.assertEqual(by_id[released_id]["castSeedQualityReason"], "synthetic unusable face")
        self.assertIn("quality hold", by_id[released_id]["reason"])

    def test_unmatched_photos_do_not_recreate_their_old_shared_membership(self):
        other = self.source_photo.with_name("fia_image_987654.jpg")
        other.write_bytes(b"other photo")
        self.layout["manifest_files"][other.relative_to(self.source).as_posix()] = (
            len(b"other photo"), hashlib.sha256(b"other photo").hexdigest(),
        )
        api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: {},
                photo_folders=lambda cfg, root: [
                    ("Potentials", "Fia", self.source_photo.parent.parent),
                ],
                photo_key=likeness.cw.photo_key,
            ),
            settings=likeness.settings, originals=likeness.originals,
            nz=likeness.nz, chosen_keys=lambda cfg: set(),
            invent_name=lambda seed, taken: f"New-{seed[-6:]}",
        )
        with mock.patch.object(clean_rebase, "frozen_identity_cores", return_value=(
            {"Angels/Angelica": {"vector": np.array([0., 1.]), "side": "Prospects"}},
            set(), [],
        )):
            result = clean_rebase.create_plan(
                self.layout, self.run, load_policy(), api,
                embedder=lambda path: {
                    "v": [1., 0.] if path == self.source_photo else [-1., 0.],
                    "faces": 1, "s": .95, "px": 100,
                },
            )
        folders = {"/".join(row["destination"].split("/")[:2]) for row in result["photos"]}
        self.assertEqual(len(folders), 2)

    def test_heap_clustering_matches_brute_force_average_linkage(self):
        rng = np.random.default_rng(41)
        vectors = rng.normal(size=(30, 8))
        vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
        rows = [{"photoId": f"{i:03}", "vector": vector} for i, vector in enumerate(vectors)]
        scores = vectors @ vectors.T
        groups = [[i] for i in range(len(rows))]
        while len(groups) > 1:
            best = None
            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):
                    score = float(np.mean(scores[np.ix_(groups[i], groups[j])]))
                    if best is None or score > best[0]:
                        best = (score, i, j)
            score, i, j = best
            if score < .25:
                break
            groups[i] = sorted(groups[i] + groups.pop(j))
        expected = [[rows[i]["photoId"] for i in group] for group in groups]
        actual = [[row["photoId"] for row in group] for group in _average_linkage(rows, .25)]
        self.assertEqual(actual, expected)
