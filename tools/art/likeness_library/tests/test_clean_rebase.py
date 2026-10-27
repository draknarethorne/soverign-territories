"""Clean rebase must flatten old groups, isolate references, and stage reversibly."""
import hashlib
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
            result = clean_rebase.create_plan(
                self.layout, self.run, load_policy(), api,
                embedder=lambda path: {
                    "v": [1., 0.] if "fia" in path.name else [0., 1.],
                    "faces": 1, "s": .95, "px": 100,
                },
            )
            with mock.patch.object(api, "Embedder", create=True, return_value=mock.Mock(
                side_effect=AssertionError("replan must reuse its own measurements"),
            )):
                replanned = clean_rebase.create_plan(
                    self.layout, self.run, load_policy(), api, reuse_measurements=True,
                )
            self.assertTrue(replanned["cacheMeasurementsReusedForReplan"])
        self.assertTrue(result["embeddingCacheStartedEmpty"])
        self.assertEqual(result["referenceFolders"], ["Angels/Angelica"])
        self.assertEqual(result["candidateCount"], 1)
        with self.assertRaisesRegex(ValueError, "empty embedding cache"):
            clean_rebase.create_plan(self.layout, self.run, load_policy(), api)

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
