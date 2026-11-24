import contextvars
import contextlib
import copy
import hashlib
import io
import json
import os
import pathlib
import runpy
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np
from PIL import Image

from tools.art import machine_tuning, originals
from tools.art.likeness_library import metadata, normal_products, normal_rebase


ROOT = pathlib.Path(__file__).resolve().parents[4]


class ReleasedPhotoBindingsTests(unittest.TestCase):
    def setUp(self):
        self.a = "a" * 64
        self.b = "b" * 64
        self.c = "c" * 64
        self.reports = [
            {"moves": [
                {"photoId": "photo:a", "source": "Sisters/A/gallery/a.jpg",
                 "destination": "Various/review/a.jpg", "sha256": self.a},
                {"photoId": "photo:b", "source": "Models/B/gallery/b.jpg",
                 "destination": "Angels/C/review/b.jpg", "sha256": self.b},
            ]},
            {"moves": [
                {"photoId": "photo:a", "source": "Various/review/a.jpg",
                 "destination": "Potentials/D/gallery/a.jpg", "sha256": self.a},
                {"photoId": "photo:c", "source": "Models/E/gallery/c.jpg",
                 "destination": "Various/review/c.jpg", "sha256": self.c},
            ]},
        ]
        self.inventory = [
            {"photoId": "photo:c", "source": "Various/review/c.jpg", "sourceHash": self.c},
            {"photoId": "photo:a", "source": "Potentials/D/gallery/a.jpg", "sourceHash": self.a},
            {"photoId": "photo:b", "source": "Angels/C/review/b.jpg", "sourceHash": self.b},
            {"photoId": "photo:other", "source": "Various/gallery/other.jpg", "sourceHash": self.a},
        ]

    def bindings(self, reports=None, inventory=None):
        return normal_rebase._released_photo_bindings(
            self.reports if reports is None else reports,
            self.inventory if inventory is None else inventory,
        )

    def test_conserves_distinct_ids_and_latest_named_and_various_locations(self):
        expected = [
            {"photoId": "photo:a", "currentPath": "Potentials/D/gallery/a.jpg", "sha256": self.a},
            {"photoId": "photo:b", "currentPath": "Angels/C/review/b.jpg", "sha256": self.b},
            {"photoId": "photo:c", "currentPath": "Various/review/c.jpg", "sha256": self.c},
        ]
        before = copy.deepcopy((self.reports, self.inventory))
        self.assertEqual(self.bindings(), expected)
        self.assertEqual(self.bindings(inventory=list(reversed(self.inventory))), expected)
        self.assertEqual((self.reports, self.inventory), before)

    def test_release_roles_preserve_nonvoting_duplicates(self):
        bindings = self.bindings()
        active = [{**row, "sourceStatus": "eligible"} for row in self.inventory[1:3]]
        held = [{**self.inventory[0], "sourceStatus": "same-content-nonvoting"}]
        self.assertEqual(normal_rebase._released_candidate_roles(bindings, active, held), {
            "photo:a": "candidate",
            "photo:b": "candidate",
            "photo:c": "nonvoting-candidate",
        })

    def test_release_roles_refuse_missing_conflicting_or_blocked_rows(self):
        bindings = self.bindings()
        active = [{**row, "sourceStatus": "eligible"} for row in self.inventory[:3]]
        with self.assertRaisesRegex(ValueError, "missing"):
            normal_rebase._released_candidate_roles(bindings, active[:-1], [])
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            normal_rebase._released_candidate_roles(bindings, active, [active[0]])
        blocked = copy.deepcopy(active)
        blocked[0]["sourceStatus"] = "held"
        with self.assertRaisesRegex(ValueError, "unresolved"):
            normal_rebase._released_candidate_roles(bindings, blocked, [])

    def test_rejects_discontinuous_or_changed_later_move(self):
        for field, value in (("source", "Various/review/wrong.jpg"), ("sha256", self.b)):
            reports = copy.deepcopy(self.reports)
            reports[1]["moves"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "discontinuous"):
                self.bindings(reports=reports)

    def test_five_reports_can_return_to_a_former_location(self):
        reports = copy.deepcopy(self.reports) + [
            {"moves": []},
            {"moves": [{"photoId": "photo:a", "source": "Potentials/D/gallery/a.jpg",
                        "destination": "Sisters/A/gallery/a.jpg", "sha256": self.a}]},
            {"moves": []},
        ]
        inventory = copy.deepcopy(self.inventory)
        inventory[1]["source"] = "Sisters/A/gallery/a.jpg"
        result = self.bindings(reports=reports, inventory=inventory)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["currentPath"], "Sisters/A/gallery/a.jpg")

    def test_larger_five_report_cohort_retains_every_distinct_id(self):
        reports = [{"moves": []} for _ in range(5)]
        inventory = []
        for index in range(37):
            photo_id = f"photo:{index:03d}"
            checksum = hashlib.sha256(photo_id.encode()).hexdigest()
            source = f"Models/Former/gallery/{index}.jpg"
            destination = (f"Various/review/{index}.jpg" if index % 2
                           else f"Potentials/Target/gallery/{index}.jpg")
            reports[index % 3]["moves"].append({
                "photoId": photo_id, "source": source, "destination": destination, "sha256": checksum,
            })
            if index % 3 == 0:
                final = f"Angels/Target/review/{index}.jpg"
                reports[4]["moves"].append({
                    "photoId": photo_id, "source": destination, "destination": final, "sha256": checksum,
                })
                destination = final
            inventory.append({"photoId": photo_id, "source": destination, "sourceHash": checksum})
        result = self.bindings(reports=reports, inventory=inventory)
        self.assertEqual(len(result), len(inventory))
        self.assertEqual({row["photoId"] for row in result}, {row["photoId"] for row in inventory})

    def test_rejects_missing_stale_or_ambiguous_inventory(self):
        for replacement in (None, {"photoId": "photo:a", "source": "wrong/a.jpg", "sourceHash": self.a},
                            {"photoId": "photo:a", "source": "Potentials/D/gallery/a.jpg", "sourceHash": self.b},
                            {"photoId": "photo:a", "source": "potentials/d/gallery/a.jpg", "sourceHash": self.a},
                            {"photoId": None, "source": "Potentials/D/gallery/a.jpg", "sourceHash": self.a}):
            inventory = [row for row in self.inventory if row["photoId"] != "photo:a"]
            if replacement is not None:
                inventory.append(replacement)
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                self.bindings(inventory=inventory)
        for duplicate in (
            self.inventory[1],
            {"photoId": "photo:a", "source": "Various/gallery/another.jpg", "sourceHash": self.a},
            {"photoId": "photo:other", "source": "potentials/d/gallery/a.jpg", "sourceHash": self.a},
        ):
            with self.subTest(duplicate=duplicate), self.assertRaisesRegex(ValueError, "ambiguous"):
                self.bindings(inventory=[*self.inventory, duplicate])

    def test_rejects_duplicate_and_conflicting_moves(self):
        reports = copy.deepcopy(self.reports)
        reports[0]["moves"].append(copy.deepcopy(reports[0]["moves"][0]))
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.bindings(reports=reports)
        reports = copy.deepcopy(self.reports)
        reports[1]["moves"][1]["destination"] = "Angels/C/review/b.jpg"
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.bindings(reports=reports)
        reports = copy.deepcopy(self.reports)
        reports[1]["moves"][1]["source"] = "Angels/C/review/b.jpg"
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.bindings(reports=reports)

    def test_rejects_incomplete_or_unsafe_evidence(self):
        for reports in ([], [{}], [{"moves": []}], [{"moves": [{}]}]):
            with self.subTest(reports=reports), self.assertRaises(ValueError):
                self.bindings(reports=reports)
        for field, value in (("photoId", ""), ("sha256", "z" * 64),
                             ("source", "../escape.jpg"), ("destination", "Various\\review\\a.jpg")):
            reports = copy.deepcopy(self.reports)
            reports[0]["moves"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.bindings(reports=reports)


class NormalRebaseTests(unittest.TestCase):
    def setUp(self):
        self.scratch = ROOT / "tmp" / "normal-flow-restoration"
        self.scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=self.scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name) / "Working"
        self.root.mkdir()
        # Fixtures must not depend on the host machine's capacity or local tuning file.
        machine_default = mock.patch.object(normal_products, "default_workers", return_value=(1, "test fixture"))
        machine_default.start()
        self.addCleanup(machine_default.stop)
        no_local_file = mock.patch.object(machine_tuning, "LOCAL", self.root / "no-machine-tuning.local.json")
        no_local_file.start()
        self.addCleanup(no_local_file.stop)

    def photo(self, relative, data):
        path = self.root / pathlib.PurePosixPath(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def folders(self, *rows):
        return list(rows)

    def stub_api(self, folders):
        class FakePhoto:
            def __init__(self, path, group, folder, digest, data):
                self.path = pathlib.Path(path)
                self.group, self.folder = group, folder
                self.key = group if group == folder else f"{group}/{folder}"
                self.sha = digest
                self.name = self.path.name
                self.faces = (data or {}).get("faces", -1)
                self.f2 = (data or {}).get("f2", 0)
                self.px = (data or {}).get("px", 0)
                self.raw = np.asarray((data or {}).get("v"), dtype=float) if (data or {}).get("v") else None
                self.vec = None
                self.box = (data or {}).get("box")

            def usable(self, minimum):
                return self.raw is not None and self.px >= minimum

        class FakeSpace:
            def __init__(self, photos, settings, mean=None):
                self.photos = list(photos)
                self.st = settings
                self.mean = np.asarray(mean, dtype=float) if mean is not None else np.zeros(2)
                self.person = self.photos
                self.by_key = {}
                for photo in self.photos:
                    if photo.raw is not None:
                        centered = photo.raw - self.mean
                        norm = np.linalg.norm(centered)
                        photo.vec = centered / (norm if norm else 1)
                    self.by_key.setdefault(photo.key, []).append(photo)

        class Token:
            def __init__(self):
                self.value = contextvars.ContextVar("fake-domain", default=False)

            def set(self, value):
                return self.value.set(value)

            def reset(self, token):
                self.value.reset(token)

            def get(self):
                return self.value.get()

        class FakeCache:
            def __init__(self, _path):
                self.stat, self.emb = {}, {}
                self.centering_mean = None
                self.centering_domain = None

        class FakeEmbedder:
            det = object()

            def configure_evidence(self, *_args, **_kwargs):
                return None

        class FakeCW:
            @staticmethod
            def photo_folders(_cfg, _root):
                return folders

            @staticmethod
            def storage_root(_cfg, _kind, root):
                return pathlib.Path(root) / "reports"

        return SimpleNamespace(
            Photo=FakePhoto,
            Space=FakeSpace,
            Cache=FakeCache,
            Embedder=FakeEmbedder,
            configuration=lambda: {},
            cache_path=lambda _args, root: pathlib.Path(root) / "cache.json",
            metadata=metadata,
            cw=FakeCW(),
            domains=SimpleNamespace(CURRENT=Token(), READ_ONLY=Token()),
        )

    def source_rows(self, cfg=None):
        cfg = cfg or {}
        folders = []
        for group in sorted(path for path in self.root.iterdir() if path.is_dir()):
            if group.name == "Various":
                folders.append(("Various", "Various", group))
                continue
            for owner in sorted(path for path in group.iterdir() if path.is_dir()):
                folders.append((group.name, owner.name, owner))
        api = self.stub_api(folders)
        return normal_rebase._hash_sources(self.root, cfg, api)[0]

    def empty_catalog(self):
        return {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}

    def retain_original(self, keeper, data):
        from tools.art.likeness_library import retained_preparation

        relative = keeper.relative_to(self.root).as_posix()
        photo_id = metadata.photo_id_from_name(keeper.name)
        original = self.photo(f"recipe/{photo_id.removeprefix('photo:')}/original.jpg", data)
        native = original.with_name("native.jpg")
        native.write_bytes(keeper.read_bytes())
        detail = original.with_name("detail.html")
        detail.write_bytes(b"<html><body></body></html>")
        thumbnail = original.with_name("thumbnail.jpg")
        thumbnail.write_bytes(b"thumbnail")
        retained_preparation.stage_photo(
            self.root, relative, original.parent, {
                "source": relative, "photoId": photo_id,
                "sourceSha256": metadata.content_sha256(original), "retained": original.name,
                "detail": detail.name, "detailSha256": metadata.content_sha256(detail),
                "sourceScope": {"matchingDomain": "general"},
                "processing": {"final": "composition"},
                "variants": {"composition": {
                    "path": native.name, "sha256": metadata.content_sha256(native),
                    "thumbnail": thumbnail.name, "thumbnailSha256": metadata.content_sha256(thumbnail),
                }},
            }, recipe={"id": "test"}, storage_mode="lean",
        )
        return retained_preparation.verify_link(self.root, keeper, photo_id)

    def test_retained_duplicate_sources_in_direct_script_context(self):
        script = runpy.run_path(str(ROOT / "tools" / "art" / "likeness_library" / "normal_rebase.py"))
        self.assertEqual(script["_retained_duplicate_sources"](self.root, {}), {})

    def test_red_hold_lean_stages_verified_retained_lineage(self):
        from tools.art.likeness_library import derivatives, normal_transaction, retained_preparation
        from tools.art.likeness_library.policy import load_policy

        payload = io.BytesIO()
        Image.new("RGB", (800, 1100), (20, 40, 60)).save(payload, format="JPEG")
        source = self.photo("Sisters/Owner/gallery/owner_image_901.jpg", payload.getvalue())
        self.retain_original(source, b"preserved raw source")
        box = [.35, .2, .25, .25]
        _, diagnostics = derivatives.maintain(source, box, 200, apply=True, faces=1)
        self.assertFalse([row for row in diagnostics if not row.startswith("INFO:")])
        old_products = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for kind in ("padded", "head", "chest")
            for path, _ in [derivatives.verified(source, kind, box)]
        }
        old_manifest = derivatives.manifest_path(source.parent.parent).read_bytes()
        photo_id = "photo:image_901"
        checksum = metadata.content_sha256(source)
        person_id = "person_" + "a" * 32
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {person_id: {
                "id": person_id, "displayName": "Owner", "folder": "Sisters/Owner",
                "folderHistory": [], "identityAnchors": [photo_id],
            }},
            "photos": {photo_id: {"contentSha256": checksum, "protected": True}},
        }
        catalog_path = self.root / ".likeness-library.json"
        metadata.save_catalog(catalog, catalog_path)
        before_catalog = catalog_path.read_bytes()
        move = {
            "photoId": photo_id, "source": source.relative_to(self.root).as_posix(),
            "destination": "Various/review/owner_image_901.jpg", "sha256": checksum, "reason": "red hold",
        }
        snapshot = [{
            "photoId": photo_id, "owner": "Sisters/Owner", "bucket": "gallery",
            "currentPath": move["source"], "nativeSha256": checksum, "score": .1,
        }]
        photo = SimpleNamespace(name=source.name, box=box, px=200, faces=1)
        stage = self.root / "_reports" / "runs" / "red-fixture" / "publication"
        published, updated, removed = normal_products.stage(
            self.root, stage, [move], None, profile="lean", photos=[photo], cfg={},
            catalog=catalog, policy=load_policy(), red_snapshot_candidates=snapshot,
        )
        self.assertEqual(published[0]["sha256"], checksum)
        self.assertEqual(updated["people"][person_id]["identityAnchors"], [])
        self.assertEqual(set(removed), set(old_products))
        self.assertIsNotNone(retained_preparation.verify_link(stage, move["destination"], photo_id))
        journal = self.root / "_reports" / "runs" / "red-fixture" / "journal.json"
        normal_transaction.publish(
            self.root, stage, [move["source"], *removed], journal=journal, bindings={}, profile="lean",
            run_id="red-fixture", expected_sources={
                move["source"]: checksum, ".likeness-library.json": hashlib.sha256(before_catalog).hexdigest(),
                **removed,
            }, exclusive_targets=[move["destination"]],
        )
        normal_transaction.verify(self.root, journal)
        self.assertIsNotNone(retained_preparation.verify_link(self.root, move["destination"], photo_id))
        for kind in ("padded", "head", "chest"):
            derivatives.verified(self.root / move["destination"], kind, box)
        self.assertTrue(all(not (self.root / relative).exists() for relative in old_products))
        normal_transaction.recover(self.root, journal, apply=True)
        self.assertEqual(source.read_bytes(), payload.getvalue())
        self.assertEqual(catalog_path.read_bytes(), before_catalog)
        self.assertIsNotNone(retained_preparation.verify_link(self.root, move["source"], photo_id))
        self.assertEqual(derivatives.manifest_path(source.parent.parent).read_bytes(), old_manifest)
        for relative, content in old_products.items():
            self.assertEqual((self.root / relative).read_bytes(), content)
        self.assertFalse((self.root / move["destination"]).exists())

    def test_red_routed_lean_preserves_lineage_and_destination_derivatives(self):
        from tools.art.likeness_library import derivatives, retained_preparation
        from tools.art.likeness_library.policy import load_policy

        payload = io.BytesIO()
        Image.new("RGB", (800, 1100), (20, 40, 60)).save(payload, format="JPEG")
        source = self.photo("Sisters/Owner/gallery/owner_image_901.jpg", payload.getvalue())
        existing = self.photo("Angels/Target/gallery/target_image_902.jpg", payload.getvalue())
        self.retain_original(source, b"preserved raw source")
        box = [.35, .2, .25, .25]
        for path in (source, existing):
            _, diagnostics = derivatives.maintain(path, box, 200, apply=True, faces=1)
            self.assertFalse([row for row in diagnostics if not row.startswith("INFO:")])
        target_entries = derivatives.load(existing.parent.parent)["entries"]
        owner_id, target_id = "person_" + "a" * 32, "person_" + "b" * 32
        photo_id = "photo:image_901"
        checksum = metadata.content_sha256(source)
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {
                owner_id: {"id": owner_id, "displayName": "Owner", "folder": "Sisters/Owner",
                           "folderHistory": [], "identityAnchors": [photo_id]},
                target_id: {"id": target_id, "displayName": "Target", "folder": "Angels/Target",
                            "folderHistory": [], "identityAnchors": []},
            },
            "photos": {photo_id: {"contentSha256": checksum, "protected": True}},
        }
        metadata.save_catalog(catalog, self.root / ".likeness-library.json")
        move = {"photoId": photo_id, "source": source.relative_to(self.root).as_posix(),
                "destination": "Angels/Target/gallery/owner_image_901.jpg", "sha256": checksum,
                "reason": "qualified"}
        snapshot = [{"photoId": photo_id, "owner": "Sisters/Owner", "bucket": "gallery",
                     "currentPath": move["source"], "nativeSha256": checksum, "score": .1}]
        plan = {"assignments": [{"photoId": photo_id, "sourceFolder": "Sisters/Owner",
                                 "sourceBucket": "Gallery", "destination": "Angels/Target",
                                 "reason": "qualified", "referenceEligible": True}],
                "held": [], "referenceVersion": "5" * 64, "planningOnly": True,
                "candidateCount": 1, "retiredReferenceIds": [photo_id],
                "retiredReferenceSHA256": [checksum]}
        stage = self.root / "_reports" / "runs" / "red-routed" / "publication"
        _, updated, removed = normal_products.stage(
            self.root, stage, [move], None, profile="lean",
            photos=[SimpleNamespace(name=source.name, box=box, px=200, faces=1)], cfg={},
            catalog=catalog, policy=load_policy(), red_snapshot_candidates=snapshot, red_routing_plan=plan,
        )
        self.assertIsNotNone(retained_preparation.verify_link(stage, move["destination"], photo_id))
        for kind in ("padded", "head", "chest"):
            derivatives.verified(stage / move["destination"], kind, box)
        staged_entries = derivatives.load(stage / "Angels" / "Target")["entries"]
        for key, entry in target_entries.items():
            self.assertEqual(staged_entries[key], entry)
        self.assertEqual(updated["photos"][photo_id]["membership"]["personId"], target_id)
        self.assertTrue(removed)
        self.assertEqual(source.read_bytes(), payload.getvalue())
        self.assertEqual(derivatives.load(existing.parent.parent)["entries"], target_entries)

    def test_retained_original_duplicate_respects_distinct_ids_and_provenance(self):
        keeper = self.photo("Angels/Ava/review/ava_image_901.jpg", b"prepared")
        proof = self.retain_original(keeper, b"raw")
        alias = self.photo("Various/gallery/image_902.jpg", b"raw")
        other_copy = self.photo("Various/gallery/image_903.jpg", b"raw")
        edit = self.photo("Various/gallery/image_904.jpg", b"hand edit")
        catalog = self.empty_catalog()
        catalog["photos"]["photo:image_901"] = {
            "contentSha256": metadata.content_sha256(keeper), "protected": True,
        }

        def archives():
            rows = self.source_rows()
            normal_rebase._classify_sources(self.root, rows, {}, catalog, None, archive_collisions=True)
            return {self.root / path: entry for path, entry in normal_rebase._duplicate_archives(
                self.root, rows, "f",
            ).items() if entry.get("retainedOriginalProof")}

        selected = archives()
        self.assertEqual(set(selected), {alias, other_copy})
        self.assertEqual(selected[alias]["retainedOriginalProof"]["path"], proof["original"])
        self.assertIn(proof["manifest"], normal_rebase._retained_duplicate_sources(self.root, selected))
        script = runpy.run_path(str(ROOT / "tools" / "art" / "likeness_library" / "normal_rebase.py"))
        self.assertIn(proof["manifest"], script["_retained_duplicate_sources"](self.root, selected))
        self.assertTrue(edit.is_file())
        catalog["actions"].append({"actor": "user", "photoIds": ["photo:image_902"]})
        self.assertEqual(set(archives()), {other_copy})
        catalog["actions"].clear()
        conflicting_keeper = self.photo("Sisters/Other/gallery/other_image_905.jpg", b"other prepared")
        self.retain_original(conflicting_keeper, b"raw")
        self.assertEqual(archives(), {})
        conflicting_keeper.unlink()
        (self.root / proof["original"]).write_bytes(b"corrupted retained original")
        self.assertEqual(archives(), {})
        with self.assertRaisesRegex(ValueError, "retained original changed"):
            normal_rebase._retained_duplicate_sources(self.root, selected)

    def test_inventory_bounds_retained_manifest_reads_and_seals_content(self):
        from tools.art.likeness_library import retained_preparation

        folder = self.root / "Models" / "Fragment"
        for index in range(3):
            self.photo(f"Models/Fragment/gallery/fragment_image_{123 + index}.jpg", b"source")
        manifests = {
            self.photo(
                f"_processing/Models/Fragment/{index:032x}/manifest.json",
                json.dumps({
                    "formatVersion": retained_preparation.FULL_VERSION,
                    "current": f"Models/Fragment/gallery/other_image_{900 + index}.jpg",
                }).encode(),
            )
            for index in range(3)
        }
        api = self.stub_api([("Models", "Fragment", folder)])
        opened = []
        original_open = pathlib.Path.open

        def open_file(path, *args, **kwargs):
            if path in manifests:
                opened.append(path)
            return original_open(path, *args, **kwargs)

        class InventoryComplete(Exception):
            pass

        with mock.patch.object(pathlib.Path, "open", autospec=True, side_effect=open_file), \
                mock.patch.object(normal_rebase, "_classify_sources", side_effect=InventoryComplete):
            with self.assertRaises(InventoryComplete):
                normal_rebase._plan(self.root, "lean", "inventory-read-proof", api=api)
        self.assertEqual(set(opened), manifests)
        self.assertLessEqual(len(opened), 2 * len(manifests))
        self.assertTrue(all(opened.count(path) == 2 for path in manifests))

    def test_fragment_preview_uses_only_frozen_members_and_content_bound_rejections(self):
        from tools.art.likeness_library.policy import load_policy

        photos = [
            SimpleNamespace(
                key="Models/Fragment", name=f"model_image_{index}.jpg",
                sha=f"measured-{index}", vec=np.array([1., 0.]),
                path=self.photo(f"Models/Fragment/gallery/model_image_{index}.jpg", f"bytes-{index}".encode()),
                faces=1, f2=0., usable=lambda _minimum: True,
            )
            for index in (123, 124)
        ]
        space = SimpleNamespace(photos=photos, st={"minFace": 60, "multiFace": .3})
        cores = {"Models/Fragment": {"corePhotoIds": ["photo:image_123"]}}
        catalog = self.empty_catalog()
        catalog["photos"]["photo:image_123"] = {
            "contentSha256": "old-bytes", "rejectedPersonIds": ["rejected-person"],
        }
        expected = {"activation": "diagnostic-only", "candidateLinks": []}
        with mock.patch.object(
            normal_rebase.reconciliation, "fragment_proposals", return_value=expected,
        ) as proposals:
            result = normal_rebase._fragment_evidence(
                space, cores, catalog, load_policy(), {"locked-reference"},
            )
        self.assertEqual(result, expected)
        members = proposals.call_args.args[1]["Models/Fragment"]
        self.assertEqual([row["photoId"] for row in members], ["photo:image_123"])
        self.assertTrue(members[0]["rejectionMetadataStale"])
        self.assertEqual(members[0]["sha256"], metadata.content_sha256(photos[0].path))
        self.assertEqual(proposals.call_args.kwargs["blocked_ids"], {"locked-reference"})

    def test_launcher_empty_preview_records_fragment_evidence_without_library_mutation(self):
        catalog = self.root / ".likeness-library.json"
        catalog.write_text(json.dumps(self.empty_catalog()), encoding="utf-8")
        before = catalog.read_bytes()
        receipt = self.root / "_reports" / "runs" / "normal-rebase-fragment-fixture-preview.json"
        cache = self.root / "fixture-cache.json"
        result = subprocess.run(
            [os.environ["COMSPEC"], "/d", "/c", str(ROOT / "bin" / "normal-rebase.cmd"),
             "--root", str(self.root), "--cache", str(cache), "--profile", "fast",
             "--run-id", "fragment-fixture", "--receipt", str(receipt), "--dry-run"],
            cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        plan = json.loads(receipt.read_text(encoding="utf-8"))["plan"]
        self.assertEqual(plan["fragmentQualification"]["activation"], "diagnostic-only")
        self.assertEqual(plan["fragmentQualification"]["comparisons"], [])
        self.assertEqual(
            plan["bindings"]["sharedImplementation"]["protection.py"],
            metadata.content_sha256(pathlib.Path(normal_rebase.reconciliation.protection.__file__)),
        )
        self.assertEqual(plan["moves"], [])
        self.assertEqual(catalog.read_bytes(), before)
        self.assertFalse(cache.exists())

    def test_cast_receiving_lock_mismatch_refuses_before_measuring_or_reading_sources(self):
        api = SimpleNamespace(configuration=lambda: {})
        with self.assertRaisesRegex(ValueError, "cast receiving lock differs"):
            normal_rebase._plan(
                self.root, "fast", "locked-fixture", api=api,
                reuse_plan={"lockCastAdmission": True}, lock_cast_admission=False,
            )

    def test_released_cohort_uses_independent_former_core_and_nonvoting_score(self):
        from tools.art.likeness_library.reconciliation import plan_reconciliation

        paths = [
            self.photo("Prospects/Owner/gallery/owner_image_101.jpg", b"reference 1"),
            self.photo("Prospects/Owner/gallery/owner_image_102.jpg", b"reference 2"),
            self.photo("Prospects/Owner/gallery/owner_image_103.jpg", b"released"),
            self.photo("Prospects/Owner/gallery/owner_image_104.jpg", b"duplicate content"),
            self.photo("Various/review/various_image_105.jpg", b"duplicate content"),
        ]
        folders = [
            ("Prospects", "Owner", self.root / "Prospects" / "Owner"),
            ("Various", "Various", self.root / "Various"),
        ]
        api = self.stub_api(folders)
        original_space = api.Space

        class FixtureSpace(original_space):
            def __init__(self, photos, settings, mean=None):
                super().__init__(photos, settings, mean=np.zeros(2))

        api.Space = FixtureSpace
        api.plan_reconciliation = plan_reconciliation
        api.invent_name = lambda seed, _taken: "Fixture-" + seed[:8]
        catalog = self.empty_catalog()
        duplicate_id = metadata.photo_id_from_name(paths[4].name)
        catalog["photos"][duplicate_id] = {
            "contentSha256": metadata.content_sha256(paths[4]), "protected": False,
        }
        metadata.save_catalog(catalog, self.root / ".likeness-library.json")
        bindings = [
            {"photoId": metadata.photo_id_from_name(path.name),
             "currentPath": path.relative_to(self.root).as_posix(),
             "sha256": metadata.content_sha256(path)}
            for path in (paths[2], paths[4])
        ]
        observed = []

        def frozen(space, _catalog, **_kwargs):
            observed.append([photo.path for photo in space.photos])
            refs = [photo for photo in space.photos if photo.key == "Prospects/Owner"]
            return {"Prospects/Owner": {
                "vector": np.array([1., 0.]), "side": "Prospects",
                "category": "Prospects", "personIds": [], "identityProtected": False,
                "mode": "fixture",
                "corePhotoIds": [metadata.photo_id_from_name(photo.name) for photo in refs],
                "photoScores": {photo.name: 1. for photo in refs},
            }}, set(), []

        with mock.patch.object(normal_rebase, "_infer", side_effect=lambda _api, _cache, _embed, path, **_kw: (
                metadata.content_sha256(path),
                {"v": [1., 0.], "faces": 1, "px": 1000, "t": "fixture"},
        )), mock.patch.object(normal_rebase.reconciliation, "frozen_identity_cores", side_effect=frozen), \
                mock.patch.object(normal_rebase, "_fragment_evidence", return_value={}), \
                mock.patch.object(normal_rebase, "_bindings", return_value={"fixture": "bound"}), \
                mock.patch.object(normal_rebase.normal_finish, "check_batch",
                                  side_effect=lambda _api, _space, _catalog, _policy, moves, **_kw: (
                                      list(moves), {"passCount": 1, "frozenRivals": {}, "corrections": []},
                                  )), \
                mock.patch.object(normal_rebase.maintenance, "_validate_permissions") as permissions:
            report, _stage_photos, publication_space, *_ = normal_rebase._plan(
                self.root, "fast", "release-fixture", api=api, released_bindings=bindings,
            )
            applied, *_ = normal_rebase._plan(
                self.root, "fast", "release-fixture", api=api, released_bindings=bindings,
                for_apply=True, reuse_plan=report,
            )
            changed = copy.deepcopy(report)
            changed["releasedPlanFingerprint"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "differ from preview"):
                normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api, released_bindings=bindings,
                    for_apply=True, reuse_plan=changed,
                )
            with self.assertRaisesRegex(ValueError, "bindings differ"):
                normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api,
                    released_bindings=bindings[:1], for_apply=True, reuse_plan=report,
                )
            stale = copy.deepcopy(bindings)
            stale[0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "stale or ambiguous"):
                normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api, released_bindings=stale,
                )
            with self.assertRaisesRegex(ValueError, "requires its bound preview"):
                normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api,
                    released_bindings=bindings, for_apply=True,
                )
            with mock.patch.object(
                normal_rebase, "_prepare_with_origin", side_effect=ValueError("captured preparation inputs"),
            ) as prepare:
                with self.assertRaisesRegex(ValueError, "captured preparation inputs"):
                    normal_rebase._plan(
                        self.root, "lean", "release-fixture", api=api, released_bindings=bindings,
                    )
                self.assertEqual(set(prepare.call_args.args[4]), set(paths[:4]))
            with mock.patch.object(normal_rebase, "_decision_ids", return_value={bindings[0]["photoId"]}):
                overridden, *_ = normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api, released_bindings=bindings,
                )
            overridden_evidence = next(
                row for row in overridden["releasedDecisionEvidence"] if row["photoId"] == bindings[0]["photoId"]
            )
            # IU7: a workflow selection no longer protects or overrides; the photo routes normally.
            self.assertFalse(overridden_evidence["workflowSelected"])
            self.assertEqual(overridden_evidence["decision"]["destination"], "Prospects/Owner")
            real_two_round = normal_rebase.normal_admission.two_round_plan

            def with_cluster(*args, **kwargs):
                result = real_two_round(*args, **kwargs)
                result["clusters"].append({"destination": "Prospects/New"})
                return result

            with mock.patch.object(normal_rebase.normal_admission, "two_round_plan", side_effect=with_cluster):
                unrelated, *_ = normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api, released_bindings=bindings,
                )
                self.assertEqual(len(unrelated["clusters"]), 1)

            reconsidered, *_ = normal_rebase._plan(
                self.root, "fast", "release-fixture", api=api,
                released_bindings=bindings, reconsider_holds=True,
            )
            # The released identical copy is archived before scoring, so it never
            # becomes a prior explicit Review placement or a non-voting candidate.
            self.assertEqual(reconsidered["priorExplicitReviewPlacements"], [])
            self.assertNotIn("reconsideredNonVotingEvidence", reconsidered)
            with self.assertRaisesRegex(ValueError, "hold reassessment differs"):
                normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api, released_bindings=bindings,
                    for_apply=True, reuse_plan=reconsidered,
                )
            ordinary_review = self.photo("Various/review/various_image_106.jpg", b"ordinary review")
            ordinary_id = metadata.photo_id_from_name(ordinary_review.name)
            ordinary_path = ordinary_review.relative_to(self.root).as_posix()
            with mock.patch.object(
                normal_rebase, "_explicit_review_placements",
                side_effect=lambda _catalog, **kwargs: (
                    set() if kwargs.get("action_types") else {(ordinary_id, ordinary_path)}
                ),
            ), mock.patch.object(
                normal_rebase.normal_admission, "two_round_plan", wraps=real_two_round,
            ) as planner:
                default, *_ = normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api, released_bindings=bindings,
                )
                default_candidate = next(
                    row for row in planner.call_args.args[1] if row["photoId"] == ordinary_id
                )
                self.assertTrue(default_candidate["explicitReviewPlacement"])
                self.assertFalse(default_candidate["regroupReview"])
                reconsidered, *_ = normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api,
                    released_bindings=bindings, reconsider_holds=True,
                )
                candidate = next(row for row in planner.call_args.args[1] if row["photoId"] == ordinary_id)
                self.assertFalse(candidate["explicitReviewPlacement"])
                self.assertTrue(candidate["regroupReview"])
                self.assertTrue(candidate["priorExplicitReviewPlacement"])
                self.assertEqual(default["priorExplicitReviewPlacements"], reconsidered["priorExplicitReviewPlacements"])
            with mock.patch.object(
                normal_rebase, "_explicit_review_placements", return_value={(ordinary_id, ordinary_path)},
            ), mock.patch.object(
                normal_rebase.normal_admission, "two_round_plan", wraps=real_two_round,
            ) as planner:
                normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api,
                    released_bindings=bindings, reconsider_holds=True,
                )
                accepted = next(row for row in planner.call_args.args[1] if row["photoId"] == ordinary_id)
                self.assertTrue(accepted["explicitReviewPlacement"])
                self.assertFalse(accepted["regroupReview"])
            ordinary_duplicate = self.photo(
                "Various/review/various_image_107.jpg", b"duplicate content",
            )
            ordinary_duplicate_id = metadata.photo_id_from_name(ordinary_duplicate.name)
            catalog["photos"][ordinary_duplicate_id] = {
                "contentSha256": metadata.content_sha256(ordinary_duplicate), "protected": False,
            }
            metadata.save_catalog(catalog, self.root / ".likeness-library.json")
            reconsidered, *_ = normal_rebase._plan(
                self.root, "fast", "release-fixture", api=api,
                released_bindings=bindings, reconsider_holds=True,
            )
            # Every identical copy is archived, including an unreleased Review copy.
            ordinary_relative = ordinary_duplicate.relative_to(self.root).as_posix()
            self.assertEqual(
                reconsidered["duplicateArchives"][ordinary_relative]["photoId"], ordinary_duplicate_id,
            )
            self.assertNotIn(ordinary_duplicate_id, {row["photoId"] for row in reconsidered["moves"]})
            self.assertNotIn(
                ordinary_duplicate_id,
                {photo_id for ids in reconsidered["referenceSnapshots"]["2"]["photoIds"].values()
                 for photo_id in ids},
            )
            replay, *_ = normal_rebase._plan(
                self.root, "fast", "release-fixture", api=api, released_bindings=bindings,
                reconsider_holds=True, for_apply=True, reuse_plan=reconsidered,
            )
            self.assertEqual(replay["reconsiderHoldsFingerprint"], reconsidered["reconsiderHoldsFingerprint"])
            changed = copy.deepcopy(reconsidered)
            changed["reconsiderHoldsFingerprint"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "hold reassessment decisions differ"):
                normal_rebase._plan(
                    self.root, "fast", "release-fixture", api=api, released_bindings=bindings,
                    reconsider_holds=True, for_apply=True, reuse_plan=changed,
                )
        # The archived released copy's keeper (paths[3]) is an ordinary single vote.
        self.assertTrue(all(set(items) == {*paths[:2], paths[3]} for items in observed))
        decisions = {row["photoId"]: row for row in report["releasedDecisionEvidence"]}
        voting = decisions[bindings[0]["photoId"]]
        duplicate = decisions[duplicate_id]
        self.assertEqual(voting["decision"]["destination"], "Prospects/Owner")
        self.assertEqual(voting["decision"]["sourceBucket"], "Pool")
        self.assertEqual(voting["actualSourceFolder"], "Prospects/Owner")
        # Item (a): the released identical copy is archived; its keeper stays with matching.
        archive = report["duplicateArchives"][bindings[1]["currentPath"]]
        self.assertEqual(duplicate["role"], "archived-duplicate")
        self.assertEqual(duplicate["decision"]["duplicateArchive"], archive["destination"])
        self.assertEqual(archive["selectedSource"], paths[3].relative_to(self.root).as_posix())
        self.assertFalse(duplicate["decision"]["referenceEligible"])
        self.assertNotIn("releasedNonVotingEvidence", report)
        self.assertNotIn(duplicate_id, {row["photoId"] for row in report["sourceHolds"]})
        self.assertEqual(report["candidateCount"], 4)
        self.assertEqual(report["releasedPlanFingerprint"], applied["releasedPlanFingerprint"])
        self.assertEqual(
            sum(metadata.photo_id_from_name(photo.name) == duplicate_id for photo in publication_space.photos), 0,
        )
        moves = {row["photoId"]: row for row in report["moves"]}
        self.assertNotIn(duplicate_id, moves)
        self.assertEqual(moves[bindings[0]["photoId"]]["source"], bindings[0]["currentPath"])
        self.assertEqual(moves[bindings[0]["photoId"]]["destination"], bindings[0]["currentPath"])
        self.assertTrue(moves[bindings[0]["photoId"]]["membershipOnly"])
        self.assertEqual(moves[bindings[0]["photoId"]]["releasedPhotoId"], bindings[0]["photoId"])
        self.assertTrue(moves[bindings[0]["photoId"]]["normalAdmission"])
        self.assertEqual(permissions.call_args.kwargs["released_bindings"], bindings)
        self.assertTrue(all(path.exists() for path in paths))

    def test_released_identical_copy_is_archived_and_keeper_joins_provisional_cluster(self):
        from tools.art.likeness_library.reconciliation import plan_reconciliation

        canonical = self.photo("Various/gallery/various_image_201.jpg", b"duplicate content")
        independent = self.photo("Various/gallery/various_image_202.jpg", b"independent content")
        duplicate = self.photo("Various/review/various_image_203.jpg", b"duplicate content")
        api = self.stub_api([("Various", "Various", self.root / "Various")])
        base_space = api.Space

        class FixtureSpace(base_space):
            def __init__(self, photos, settings, mean=None):
                super().__init__(photos, settings, mean=np.zeros(2))

        api.Space = FixtureSpace
        api.plan_reconciliation = plan_reconciliation
        api.invent_name = lambda seed, _taken: "Fixture-" + seed[:8]
        duplicate_id = metadata.photo_id_from_name(duplicate.name)
        canonical_id = metadata.photo_id_from_name(canonical.name)
        independent_id = metadata.photo_id_from_name(independent.name)
        catalog = self.empty_catalog()
        catalog["photos"][duplicate_id] = {
            "contentSha256": metadata.content_sha256(duplicate), "protected": False,
        }
        metadata.save_catalog(catalog, self.root / ".likeness-library.json")
        bindings = [{
            "photoId": duplicate_id, "currentPath": duplicate.relative_to(self.root).as_posix(),
            "sha256": metadata.content_sha256(duplicate),
        }]
        with mock.patch.object(normal_rebase, "_infer", side_effect=lambda _api, _cache, _embed, path, **_kw: (
                metadata.content_sha256(path), {"v": [1., 0.], "faces": 1, "px": 1000, "t": "fixture"},
        )), mock.patch.object(normal_rebase, "_fragment_evidence", return_value={}), \
                mock.patch.object(normal_rebase, "_bindings", return_value={"fixture": "bound"}), \
                mock.patch.object(normal_rebase.maintenance, "_validate_permissions"):
            report, _stage, space, _catalog, _cfg, policy, *_ = normal_rebase._plan(
                self.root, "fast", "cluster-fixture", api=api, released_bindings=bindings,
            )
            applied, *_ = normal_rebase._plan(
                self.root, "fast", "cluster-fixture", api=api, released_bindings=bindings,
                for_apply=True, reuse_plan=report,
            )
        self.assertEqual(len(report["clusters"]), 1)
        self.assertEqual(applied["releasedPlanFingerprint"], report["releasedPlanFingerprint"])
        cluster = report["clusters"][0]
        self.assertEqual(set(cluster["photoIds"]), {canonical_id, independent_id})
        self.assertNotIn(duplicate_id, cluster["corePhotoIds"])
        # Item (a): a released byte-identical copy is archived like any duplicate;
        # only its keeper is placed by matching, and it is never scored separately.
        duplicate_relative = duplicate.relative_to(self.root).as_posix()
        archive = report["duplicateArchives"][duplicate_relative]
        self.assertEqual(archive["selectedPhotoId"], canonical_id)
        self.assertTrue(archive["destination"].startswith("_duplicates/cluster-fixture/"))
        self.assertNotIn("releasedNonVotingEvidence", report)
        evidence = next(row for row in report["releasedDecisionEvidence"] if row["photoId"] == duplicate_id)
        self.assertEqual(evidence["role"], "archived-duplicate")
        self.assertEqual(evidence["decision"]["duplicateArchive"], archive["destination"])
        self.assertEqual(evidence["decision"]["keeperPhotoId"], canonical_id)
        self.assertFalse(evidence["decision"]["referenceEligible"])
        self.assertNotIn(duplicate_id, {row["photoId"] for row in report["moves"]})
        self.assertEqual(
            sum(metadata.photo_id_from_name(photo.name) == duplicate_id for photo in space.photos), 0,
        )
        keeper_move = next(row for row in report["moves"] if row["photoId"] == canonical_id)
        self.assertTrue(keeper_move["destination"].startswith(cluster["destination"] + "/gallery/"))
        self.assertTrue(all(path.exists() for path in (canonical, independent, duplicate)))

    def test_selected_policy_reassesses_lower_core_and_retained_members_without_publishing(self):
        from tools.art.likeness_library.reconciliation import plan_reconciliation

        axes = np.eye(4)
        paths = [
            self.photo("Sisters/Drakness/gallery/drakness_image_201.jpg", b"first reference"),
            self.photo("Sisters/Drakness/gallery/drakness_image_202.jpg", b"second reference"),
            self.photo("Models/Fragment/gallery/fragment_image_203.jpg", b"existing member"),
            self.photo("Various/gallery/various_image_204.jpg", b"new arrival"),
        ]
        vectors = [.8 * axes[0] + .6 * axes[3], .8 * axes[0] - .6 * axes[3], axes[0], -axes[0]]
        folders = [
            ("Sisters", "Drakness", self.root / "Sisters" / "Drakness"),
            ("Models", "Fragment", self.root / "Models" / "Fragment"),
            ("Various", "Various", self.root / "Various"),
        ]
        api = self.stub_api(folders)
        api.plan_reconciliation = plan_reconciliation
        api.__file__ = str(ROOT / "tools" / "art" / "likeness.py")
        api.invent_name = lambda seed, _taken: "Fixture-" + seed[:8]
        metadata.save_catalog(self.empty_catalog(), self.root / ".likeness-library.json")
        source_rows, _folders, prefixes = normal_rebase._hash_sources(self.root, {}, api)
        next(row for row in source_rows if row["source"] == paths[2].relative_to(self.root).as_posix())["retainedManifest"] = "verified-fixture"
        cores = {
            folder: {
                "vector": axes[0], "side": "Prospects", "category": folder.split("/")[0],
                "personIds": [], "identityProtected": folder.startswith("Sisters/"),
                "mode": "fixture", "corePhotoIds": [metadata.photo_id_from_name(path.name) for path in members],
                "photoScores": {path.name: 1. for path in members},
            }
            for folder, members in (("Sisters/Drakness", paths[:2]), ("Models/Fragment", paths[2:3]))
        }
        measured = dict(zip(paths, vectors))
        with mock.patch.object(normal_rebase, "_hash_sources", return_value=(source_rows, folders, prefixes)), \
                mock.patch.object(normal_rebase, "_infer", side_effect=lambda _api, _cache, _embed, path, **_kwargs: (
                    hashlib.sha1(path.read_bytes()).hexdigest(),
                    {"v": measured[path].tolist(), "faces": 1, "px": 100, "t": "fixture"},
                )), \
                mock.patch.object(normal_rebase.reconciliation, "frozen_identity_cores", return_value=(cores, set(), [])), \
                mock.patch.object(normal_rebase.normal_products, "prepare", side_effect=AssertionError("FAST must not prepare")):
            report, *_rest = normal_rebase._plan(self.root, "fast", "upward-fixture", api=api)
        recovery = next(row for row in report["moves"] if row["photoId"] == "photo:image_203")
        self.assertEqual(recovery["destination"], "Sisters/Drakness/gallery/drakness_image_203.jpg")
        self.assertEqual(recovery["castAdmission"]["mode"], "supported-gallery")
        self.assertEqual(report["referenceRefreshCount"], 1)
        self.assertEqual(len(report["matchingRounds"]), 2)
        self.assertFalse(any(row["photoId"] == "photo:image_203" for row in report["sourceHolds"]))
        self.assertTrue(all(path.exists() for path in paths))

    def test_primary_inventory_counts_physical_images_and_excludes_derivatives(self):
        gallery = self.photo("Prospects/Owner/gallery/owner_image_101.jpg", b"one")
        various = self.photo("Various/review/various_image_202.jpg", b"two")
        artist = self.photo("Artists/Model/gallery/model_image_303.jpg", b"three")
        self.photo("Prospects/Owner/944x1104/head/owner_image_101.png", b"derivative")
        folders = [
            ("Prospects", "Owner", self.root / "Prospects" / "Owner"),
            ("Various", "Various", self.root / "Various"),
            ("Artists", "Model", self.root / "Artists" / "Model"),
        ]
        rows = normal_rebase._hash_sources(
            self.root, {}, self.stub_api(folders),
        )[0]
        self.assertEqual({row["source"] for row in rows}, {
            gallery.relative_to(self.root).as_posix(),
            various.relative_to(self.root).as_posix(),
            artist.relative_to(self.root).as_posix(),
        })
        self.assertEqual(
            sum(row["group"] == "Artists" and row["sourceStatus"] == "excluded-separate-domain" for row in rows),
            1,
        )

    def test_stricter_starting_cores_exclude_borderline_members_without_changing_cast_permissions(self):
        from tools.art.likeness_library.reconciliation import frozen_identity_cores

        policy = normal_rebase.load_policy()
        api = self.stub_api([])
        for tier, borderline, old_floor in (("Angels", .34, .30), ("Prospects", .175, .15)):
            with self.subTest(tier=tier):
                settings = {"minFace": 1, "multiFace": .2}
                paths = [self.photo(f"{tier}/Owner/gallery/owner_image_{i}.jpg", bytes([i])) for i in range(1, 7)]
                vectors = [[1., 0.]] * 5 + [[borderline, (1. - borderline ** 2) ** .5]]
                photos = [
                    api.Photo(path, tier, "Owner", metadata.content_sha256(path), {"faces": 1, "px": 100, "v": v})
                    for path, v in zip(paths, vectors)
                ]
                space = api.Space(photos, settings)
                catalogue = self.empty_catalog()
                old_rules = {"categoryPolicies": {tier: {**policy["categoryPolicies"][tier],
                                                        "identityCoreMinimumSimilarity": old_floor}}}
                for rules, stays in ((old_rules, True), (policy, False)):
                    cores, _, _ = frozen_identity_cores(
                        space, catalogue, photo_id_fn=metadata.photo_id_from_name,
                        content_sha256_fn=metadata.content_sha256, policy=rules, require_single_face=True,
                    )
                    self.assertEqual("photo:image_6" in cores[f"{tier}/Owner"]["corePhotoIds"], stays)
                self.assertTrue(paths[-1].exists())
        self.assertFalse(policy["categoryPolicies"]["Angels"]["automaticSplitEnabled"])
        self.assertFalse(policy["categoryPolicies"]["Sisters"]["automaticSplitEnabled"])

    def test_release_lineage_cli_real_staging_check_and_recovery(self):
        from tools.art import library_backup, likeness
        from tools.art.likeness_library import normal_transaction
        from tools.workflows import comfy_workflows as cw

        temp = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="release-cli-")
        self.addCleanup(temp.cleanup)
        self.root = pathlib.Path(temp.name).resolve() / "Sovereign Territories Sandbox" / "Working"
        self.root.mkdir(parents=True)
        old = "Models/Former/gallery/former_image_103.jpg"
        intermediate = "Various/review/various_image_103.jpg"
        current = "Prospects/Owner/gallery/owner_image_103.jpg"
        old_path = self.photo(old, b"released fixture")
        digest = metadata.content_sha256(old_path)
        photo_id = metadata.photo_id_from_name(old_path.name)
        refs = [
            self.photo(f"Prospects/Owner/gallery/owner_image_{number}.jpg", f"ref {number}".encode())
            for number in (101, 102, 104)
        ]
        reports = self.root / "_reports"
        original_review = reports / "library" / "initial" / "people_gallery_review.html"
        original_review.parent.mkdir(parents=True)
        original_review.write_text(
            '<script id="review-data">' + json.dumps([{
                "folder": "Models/Former", "bucket": "Gallery", "name": old_path.name,
                "photoId": photo_id, "contentSha256": digest,
            }]) + "</script>", encoding="utf-8",
        )
        receipt = reports / "runs" / "original.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({
            "kind": "normal-rebase-receipt", "schemaVersion": 1, "status": "applied",
            "root": str(self.root), "runId": "original", "viewerPaths": [str(original_review)],
            "plan": {"sourceRows": [{"source": old, "sourceHash": digest, "photoId": photo_id}],
                     "sourceHashes": {old: digest}, "moves": []},
        }), encoding="utf-8")
        audit = reports / "library" / "audit" / "snapshot.html"
        audit.parent.mkdir(parents=True)
        audit.write_text("<html>fixture</html>", encoding="utf-8")
        manifest = audit.with_suffix(".report.json")
        manifest.write_text(json.dumps({
            "receipt": str(receipt),
            "inputs": {str(receipt): metadata.content_sha256(receipt),
                       str(original_review): metadata.content_sha256(original_review)},
            "redCandidates": [{"photoId": photo_id, "currentPath": old, "nativeSha256": digest}],
        }), encoding="utf-8")
        manifest_hash = metadata.content_sha256(manifest)
        release_run = "release-fixture"
        release = {
            "kind": "sandbox-red-release-experiment", "root": str(self.root), "runId": release_run,
            "snapshotReportManifestSHA256": manifest_hash, "unaffectedNativeSHA256": {},
            "moves": [{"photoId": photo_id, "source": old, "destination": intermediate, "sha256": digest}],
        }
        release_stage = reports / "runs" / release_run / "publication"
        staged_native = release_stage / pathlib.PurePosixPath(intermediate)
        staged_native.parent.mkdir(parents=True)
        staged_native.write_bytes(old_path.read_bytes())
        staged_report = release_stage / "_reports" / "library" / release_run / "report.json"
        staged_report.parent.mkdir(parents=True)
        staged_report.write_text(json.dumps(release), encoding="utf-8")
        release_journal = reports / "runs" / release_run / "publication-journal.json"
        real_backup = library_backup.create_backup
        with mock.patch.object(
            library_backup, "create_backup",
            side_effect=lambda *args, **kwargs: real_backup(*args, stamp="20990101-000001", **kwargs),
        ):
            normal_transaction.publish(
                self.root, release_stage, [old], journal=release_journal,
                bindings={"snapshotReportManifestSHA256": manifest_hash}, profile="fast",
                run_id=release_run, expected_sources={old: digest},
            )
        continuation_run = "release-continuation"
        continuation_stage = reports / "runs" / continuation_run / "publication"
        continuation_native = continuation_stage / pathlib.PurePosixPath(current)
        continuation_native.parent.mkdir(parents=True)
        continuation_native.write_bytes((self.root / pathlib.PurePosixPath(intermediate)).read_bytes())
        continuation_report = continuation_stage / "_reports" / "library" / continuation_run / "report.json"
        continuation_report.parent.mkdir(parents=True)
        continuation_report.write_text(json.dumps({
            "kind": "sandbox-red-release-experiment", "root": str(self.root),
            "runId": continuation_run, "snapshotReportManifestSHA256": manifest_hash,
            "unaffectedNativeSHA256": {}, "planSHA256": "c" * 64,
            "lineageJournalSHA256": [metadata.content_sha256(release_journal)],
            "moves": [{"photoId": photo_id, "source": intermediate,
                       "destination": current, "sha256": digest}],
        }), encoding="utf-8")
        continuation_journal = reports / "runs" / continuation_run / "publication-journal.json"
        with mock.patch.object(
            library_backup, "create_backup",
            side_effect=lambda *args, **kwargs: real_backup(*args, stamp="20990101-000003", **kwargs),
        ):
            normal_transaction.publish(
                self.root, continuation_stage, [intermediate], journal=continuation_journal,
                bindings={"planSHA256": "c" * 64}, profile="fast", run_id=continuation_run,
                expected_sources={intermediate: digest},
            )
        current_path = self.root / pathlib.PurePosixPath(current)
        review_dir = reports / "library" / "current"
        review_dir.mkdir(parents=True)
        review_path = review_dir / "people_gallery_review.html"
        review_path.write_text(
            '<script id="review-data">' + json.dumps([{
                "photoId": photo_id, "generationSource": current, "contentSha256": digest,
            }]) + "</script>", encoding="utf-8",
        )
        person_id, group_id = "person_" + "a" * 32, "group_" + "b" * 32
        ref_ids = [metadata.photo_id_from_name(path.name) for path in refs]
        membership = {
            "personId": person_id, "groupId": group_id, "status": "supported", "coreUse": True,
            "reason": "fixture", "referenceVersion": "1" * 64,
        }
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {person_id: {
                "id": person_id, "displayName": "Owner", "folder": "Prospects/Owner",
                "folderHistory": [], "identityAnchors": [photo_id],
            }},
            "photos": {
                metadata.photo_id_from_name(path.name): {
                    "contentSha256": metadata.content_sha256(path), "protected": False,
                    "membership": copy.deepcopy(membership),
                } for path in [current_path, *refs]
            },
            "photoGroups": {group_id: {
                "id": group_id, "personId": person_id, "name": "core", "status": "supported",
                "memberPhotoIds": [photo_id, *ref_ids], "referencePhotoIds": [photo_id, *ref_ids],
                "sourcePersonIds": [], "history": [], "reason": "fixture",
            }},
        }
        catalog_path = self.root / ".likeness-library.json"
        metadata.save_catalog(catalog, catalog_path)
        before_catalog, before_native = catalog_path.read_bytes(), current_path.read_bytes()
        base = ["--root", str(self.root), "--cache", str(self.root / "fixture-cache.json"),
                "--profile", "fast", "--run-id", "corrected"]
        lineage = ["--release-receipt", str(receipt), "--release-audit", str(audit),
                   "--release-review", str(review_dir), "--release-run", release_run,
                   "--release-run", continuation_run]
        preview = reports / "runs" / "normal-rebase-corrected-preview.json"
        applied = reports / "runs" / "normal-rebase-corrected.json"
        fake_space = self.stub_api([]).Space

        class FixtureSpace(fake_space):
            def __init__(self, photos, settings, mean=None):
                super().__init__(photos, settings, mean=np.zeros(2))

        def measure(_api, cache, _embedder, path, **_kwargs):
            checksum = cache.sha(path)
            data = {"v": [1., 0.], "faces": 1, "px": 1000, "f2": 0., "s": 1., "t": .5}
            cache.emb[checksum] = data
            return checksum, data

        def viewers(*_args, **_kwargs):
            library = reports / "library"
            for name in normal_rebase.REQUIRED_VIEWERS:
                (library / name).write_text("<html>fixture</html>", encoding="utf-8")
            return [str(library / name) for name in normal_rebase.REQUIRED_VIEWERS]

        errors = io.StringIO()
        with mock.patch.object(likeness, "configuration", return_value={}), \
                mock.patch.object(cw, "load_cfg", return_value={}), \
                mock.patch.object(likeness, "Embedder"), \
                mock.patch.object(likeness, "Space", FixtureSpace), \
                mock.patch.object(normal_rebase, "_infer", side_effect=measure), \
                mock.patch.object(normal_rebase.normal_finish, "family_and_final", return_value={}), \
                mock.patch.object(normal_rebase.normal_finish, "viewers", side_effect=viewers), \
                mock.patch.object(normal_rebase.normal_recap, "publish", return_value=None), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors):
            for partial in (
                lineage[:6], lineage[:2], lineage[2:4], lineage[4:6], lineage[6:],
            ):
                with self.subTest(partial=partial), self.assertRaises(SystemExit) as exc:
                    normal_rebase.main([*base, *partial, "--dry-run"])
                self.assertEqual(exc.exception.code, 2)
            self.assertFalse(preview.exists())
            self.assertEqual(normal_rebase.main([*base, *lineage[:-2], "--dry-run"]), 1)
            self.assertFalse(preview.exists())
            ordinary = [*base[:-1], "ordinary"]
            self.assertEqual(normal_rebase.main([*ordinary, "--dry-run"]), 0, errors.getvalue())
            ordinary_plan = json.loads(
                (reports / "runs" / "normal-rebase-ordinary-preview.json").read_bytes()
            )["plan"]
            self.assertNotIn("releasedPhotoBindings", ordinary_plan)
            self.assertNotIn("releaseLineage", ordinary_plan)
            self.assertEqual(normal_rebase.main([*base, *lineage, "--dry-run"]), 0, errors.getvalue())
            preview_data = json.loads(preview.read_bytes())
            self.assertEqual(preview_data["plan"]["releaseLineage"]["runs"], [release_run, continuation_run])
            self.assertEqual(len(preview_data["plan"]["releaseLineage"]["journalSHA256"]), 2)
            self.assertEqual(preview_data["plan"]["releasedPhotoBindings"], [{
                "photoId": photo_id, "currentPath": current, "sha256": digest,
            }])
            selected = next(move for move in preview_data["plan"]["moves"] if move["photoId"] == photo_id)
            self.assertEqual((selected["source"], selected["destination"]), (current, current))
            self.assertTrue(selected["membershipOnly"])
            self.assertEqual(selected["releasedPhotoId"], photo_id)
            self.assertEqual(normal_rebase.main([*base, "--apply", "--sandbox-apply-draft"]), 1)
            self.assertIn("released lineage differs from preview", errors.getvalue())
            self.assertFalse(applied.exists())
            alternate = reports / "library" / "audit-alternate" / "snapshot.html"
            alternate.parent.mkdir(parents=True)
            alternate.write_bytes(audit.read_bytes())
            alternate.with_suffix(".report.json").write_bytes(manifest.read_bytes())
            changed_options = list(lineage)
            changed_options[3] = str(alternate)
            errors.seek(0)
            errors.truncate()
            self.assertEqual(normal_rebase.main([*base, *changed_options, "--apply", "--sandbox-apply-draft"]), 1)
            self.assertIn("released lineage differs from preview", errors.getvalue())
            stale = current_path.read_bytes()
            current_path.write_bytes(b"tampered")
            errors.seek(0)
            errors.truncate()
            self.assertEqual(normal_rebase.main([*base, *lineage, "--apply", "--sandbox-apply-draft"]), 1)
            self.assertIn("published content changed", errors.getvalue())
            current_path.write_bytes(stale)
            review_bytes = review_path.read_bytes()
            review_path.write_text(
                '<script id="review-data">' + json.dumps([{
                    "photoId": photo_id, "generationSource": "Various/review/wrong.jpg",
                    "contentSha256": digest,
                }]) + "</script>", encoding="utf-8",
            )
            errors.seek(0)
            errors.truncate()
            self.assertEqual(normal_rebase.main([*base, *lineage, "--apply", "--sandbox-apply-draft"]), 1)
            self.assertIn("current Review does not conserve", errors.getvalue())
            review_path.write_bytes(review_bytes)
            original_manifest = manifest.read_bytes()
            manifest.write_bytes(original_manifest + b" ")
            self.assertEqual(normal_rebase.main([*base, *lineage, "--apply", "--sandbox-apply-draft"]), 1)
            manifest.write_bytes(original_manifest)
            wrong = [*lineage[:-1], "another-release"]
            self.assertEqual(normal_rebase.main([*base, *wrong, "--apply", "--sandbox-apply-draft"]), 1)
            reversed_lineage = [*lineage[:6], "--release-run", continuation_run, "--release-run", release_run]
            self.assertEqual(normal_rebase.main([*base, *reversed_lineage, "--apply", "--sandbox-apply-draft"]), 1)
            self.assertFalse(applied.exists())
            self.assertEqual(catalog_path.read_bytes(), before_catalog)
            self.assertEqual(current_path.read_bytes(), before_native)
            self.assertEqual(normal_rebase.main([*base, *lineage, "--apply", "--sandbox-apply-draft"]), 0, errors.getvalue())
            saved = json.loads(applied.read_bytes())
            self.assertEqual(saved["plan"]["releaseLineage"], preview_data["plan"]["releaseLineage"])
            updated = metadata.load_catalog(catalog_path)
            self.assertNotIn(photo_id, updated["people"][person_id]["identityAnchors"])
            self.assertNotIn(photo_id, updated["photoGroups"][group_id]["memberPhotoIds"])
            self.assertEqual(updated["photos"][photo_id]["membership"]["personId"], person_id)
            self.assertFalse(updated["photos"][photo_id]["membership"]["coreUse"])
            self.assertEqual(updated["photos"][photo_id]["membership"]["sourcePersonIds"], [person_id])
            self.assertEqual(normal_rebase.main([*base, "--check"]), 0, errors.getvalue())
            with self.assertRaises(SystemExit) as exc:
                normal_rebase.main([*base, *lineage, "--check"])
            self.assertEqual(exc.exception.code, 2)
            with self.assertRaises(SystemExit) as exc:
                normal_rebase.main([*base, *lineage, "--recover"])
            self.assertEqual(exc.exception.code, 2)
            published_native = current_path.read_bytes()
            current_path.write_bytes(b"changed after publication")
            self.assertEqual(normal_rebase.main([*base, "--check"]), 1)
            current_path.write_bytes(published_native)
            self.assertEqual(normal_rebase.main([*base, "--check"]), 0, errors.getvalue())
            before_recovery_preview = catalog_path.read_bytes()
            self.assertEqual(normal_rebase.main([*base, "--recover"]), 0, errors.getvalue())
            self.assertEqual(catalog_path.read_bytes(), before_recovery_preview)
            self.assertEqual(current_path.read_bytes(), published_native)
            journal = json.loads(pathlib.Path(saved["journal"]).read_bytes())
            backup = pathlib.Path(journal["backup"])
            backup_manifest = json.loads((backup / "manifest.json").read_bytes())
            catalog_entry = next(
                row for row in backup_manifest["entries"] if pathlib.Path(row["source"]) == catalog_path
            )
            backup_catalog = backup / catalog_entry["backup"]
            backup_bytes = backup_catalog.read_bytes()
            backup_catalog.write_bytes(b"damaged recovery")
            applied_catalog = catalog_path.read_bytes()
            self.assertEqual(normal_rebase.main([*base, "--recover-apply"]), 1)
            self.assertEqual(catalog_path.read_bytes(), applied_catalog)
            self.assertEqual(current_path.read_bytes(), published_native)
            backup_catalog.write_bytes(backup_bytes)
            self.assertEqual(normal_rebase.main([*base, "--recover-apply"]), 0, errors.getvalue())
            self.assertEqual(catalog_path.read_bytes(), before_catalog)
            self.assertEqual(current_path.read_bytes(), before_native)
            self.assertEqual(json.loads(applied.read_bytes())["status"], "recovered")
            rebound, evidence = normal_rebase._verified_released_lineage(
                self.root, {}, str(receipt), str(audit), str(review_dir), [release_run, continuation_run],
            )
            self.assertEqual(rebound, preview_data["plan"]["releasedPhotoBindings"])
            self.assertEqual(evidence, preview_data["plan"]["releaseLineage"])
            failed = [*base[:-1], "failed"]
            self.assertEqual(normal_rebase.main([*failed, *lineage, "--dry-run"]), 0, errors.getvalue())
            with mock.patch.object(
                library_backup, "create_backup",
                side_effect=lambda *args, **kwargs: real_backup(*args, stamp="20990101-000002", **kwargs),
            ), mock.patch.object(
                normal_rebase.normal_finish, "viewers", side_effect=ValueError("injected finalizer failure"),
            ):
                self.assertEqual(
                    normal_rebase.main([*failed, *lineage, "--apply", "--sandbox-apply-draft"]), 1,
                )
            failed_receipt = reports / "runs" / "normal-rebase-failed.json"
            failed_data = json.loads(failed_receipt.read_bytes())
            self.assertEqual(failed_data["status"], "recovery-required")
            self.assertIn("injected finalizer failure", failed_data["error"])
            self.assertEqual(catalog_path.read_bytes(), before_catalog)
            self.assertEqual(current_path.read_bytes(), before_native)
            self.assertEqual(normal_rebase.main([*failed, "--check"]), 1)
            self.assertEqual(normal_rebase.main([*failed, "--recover"]), 0, errors.getvalue())
            self.assertEqual(normal_rebase.main([*failed, "--recover-apply"]), 0, errors.getvalue())
            self.assertEqual(catalog_path.read_bytes(), before_catalog)
            self.assertEqual(current_path.read_bytes(), before_native)

    def test_released_stage_preserves_catalogue_source_person_history(self):
        from tools.art.likeness_library import normal_admission
        from tools.art.likeness_library.policy import load_policy

        source = self.photo("Prospects/Owner/gallery/owner_image_123.jpg", b"fixture")
        photo_id = metadata.photo_id_from_name(source.name)
        checksum = metadata.content_sha256(source)
        owner, former, target = ("person_" + value * 32 for value in "abc")
        group_id = "group_" + "d" * 32
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {
                owner: {"id": owner, "displayName": "Owner", "folder": "Prospects/Owner",
                        "folderHistory": [], "identityAnchors": [photo_id]},
                former: {"id": former, "displayName": "Former", "folder": "Models/Former",
                         "folderHistory": [], "identityAnchors": []},
                target: {"id": target, "displayName": "Target", "folder": "Prospects/Target",
                         "folderHistory": [], "identityAnchors": []},
            },
            "photos": {photo_id: {
                "contentSha256": checksum, "protected": False,
                "membership": {
                    "personId": owner, "groupId": group_id, "status": "supported", "coreUse": True,
                    "reason": "fixture", "referenceVersion": "1" * 64, "sourcePersonIds": [former],
                },
            }},
            "photoGroups": {group_id: {
                "id": group_id, "personId": owner, "name": "core", "status": "supported",
                "memberPhotoIds": [photo_id], "referencePhotoIds": [photo_id],
                "sourcePersonIds": [], "history": [], "reason": "fixture",
            }},
        }
        relative = source.relative_to(self.root).as_posix()
        binding = {"photoId": photo_id, "currentPath": relative, "sha256": checksum}
        original = copy.deepcopy(catalog)
        retired = normal_admission.retire_released_catalog(catalog, [binding])["catalog"]
        retired_before = copy.deepcopy(retired)
        destinations = (
            (relative, owner, "supported"),
            ("Prospects/Target/gallery/owner_image_123.jpg", target, "supported"),
            ("Prospects/Target/review/owner_image_123.jpg", target, "tentative"),
            ("Various/review/owner_image_123.jpg", None, "tentative"),
        )
        for index, (destination, person_id, status) in enumerate(destinations):
            with self.subTest(destination=destination):
                move = {
                    "photoId": photo_id, "releasedPhotoId": photo_id, "source": relative,
                    "destination": destination, "sha256": checksum, "reason": "fixture",
                    "normalAdmission": True, "referenceVersion": "2" * 64,
                    "referenceEligible": False,
                    **({"membershipOnly": True} if destination == relative else {}),
                }
                stage = self.root / "_reports" / f"fixture-stage-{index}"
                _published, updated, _removed = normal_products.stage(
                    self.root, stage, [move], None, profile="fast", photos=[], cfg={},
                    catalog=retired, policy=load_policy(), released_source_catalog=catalog,
                )
                member = updated["photos"][photo_id]["membership"]
                self.assertEqual(member["sourcePersonIds"], sorted([owner, former]))
                self.assertEqual((member["personId"], member["status"], member["coreUse"]),
                                 (person_id, status, False))
                self.assertIsNone(member["groupId"])
                self.assertNotIn(photo_id, updated["people"][owner]["identityAnchors"])
                self.assertEqual(updated["photoGroups"][group_id]["memberPhotoIds"], [])
                self.assertEqual(updated["photoGroups"][group_id]["referencePhotoIds"], [])
                self.assertEqual(metadata.load_catalog(stage / ".likeness-library.json"), updated)
        self.assertEqual(catalog, original)
        self.assertEqual(retired, retired_before)

    def test_released_stage_rejects_unbound_or_unretired_source_catalogue(self):
        from tools.art.likeness_library import normal_admission
        from tools.art.likeness_library.policy import load_policy

        source = self.photo("Prospects/Owner/gallery/owner_image_123.jpg", b"fixture")
        photo_id = metadata.photo_id_from_name(source.name)
        checksum = metadata.content_sha256(source)
        owner = "person_" + "a" * 32
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {owner: {
                "id": owner, "displayName": "Owner", "folder": "Prospects/Owner",
                "folderHistory": [], "identityAnchors": [photo_id],
            }},
            "photos": {photo_id: {
                "contentSha256": checksum, "protected": False,
                "membership": {"personId": owner, "groupId": None, "status": "supported",
                               "coreUse": True, "reason": "fixture", "referenceVersion": "1" * 64},
            }},
        }
        relative = source.relative_to(self.root).as_posix()
        binding = {"photoId": photo_id, "currentPath": relative, "sha256": checksum}
        retired = normal_admission.retire_released_catalog(catalog, [binding])["catalog"]
        move = {
            "photoId": photo_id, "releasedPhotoId": photo_id, "source": relative,
            "destination": relative, "sha256": checksum, "reason": "fixture",
            "normalAdmission": True, "referenceVersion": "2" * 64,
            "referenceEligible": False, "membershipOnly": True,
        }
        altered = copy.deepcopy(retired)
        altered["people"][owner]["displayName"] = "Changed"
        invalid = (
            ([{key: value for key, value in move.items() if key != "releasedPhotoId"}], retired, {}, "marked"),
            ([{**move, "releasedPhotoId": "photo:image_999"}], retired, {}, "unique marked"),
            ([{**move, "normalAdmission": False}], retired, {}, "unique marked"),
            ([move, move], retired, {}, "unique marked"),
            ([move, {key: value for key, value in move.items() if key != "releasedPhotoId"}],
             retired, {}, "ambiguous"),
            ([{**move, "sha256": "f" * 64}], retired, {}, "stale"),
            ([move], catalog, {}, "does not match"),
            ([move], altered, {}, "does not match"),
            ([move], retired, {"red_snapshot_candidates": []}, "cannot be combined"),
        )
        for index, (moves, staging_catalog, options, message) in enumerate(invalid):
            with self.subTest(index=index):
                stage = self.root / "_reports" / f"refused-{index}"
                with self.assertRaisesRegex(ValueError, message):
                    normal_products.stage(
                        self.root, stage, moves, None, profile="fast", photos=[], cfg={},
                        catalog=staging_catalog, policy=load_policy(), released_source_catalog=catalog, **options,
                    )
                self.assertFalse(stage.exists())

    def test_released_stage_handles_absent_membership_and_unselected_moves(self):
        from tools.art.likeness_library import normal_admission
        from tools.art.likeness_library.policy import load_policy

        source = self.photo("Various/review/various_image_123.jpg", b"nonvoter")
        other = self.photo("Prospects/Owner/gallery/owner_image_124.jpg", b"ordinary")
        selected_id, other_id = (metadata.photo_id_from_name(path.name) for path in (source, other))
        owner = "person_" + "a" * 32
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {owner: {"id": owner, "displayName": "Owner", "folder": "Prospects/Owner",
                               "folderHistory": [], "identityAnchors": []}},
            "photos": {other_id: {
                "contentSha256": metadata.content_sha256(other), "protected": False,
                "membership": {"personId": owner, "groupId": None, "status": "supported", "coreUse": True,
                               "reason": "original", "referenceVersion": "1" * 64},
            }},
        }
        source_relative = source.relative_to(self.root).as_posix()
        other_relative = other.relative_to(self.root).as_posix()
        binding = {"photoId": selected_id, "currentPath": source_relative,
                   "sha256": metadata.content_sha256(source)}
        retired = normal_admission.retire_released_catalog(catalog, [binding])["catalog"]
        moves = [{
            "photoId": selected_id, "releasedPhotoId": selected_id, "source": source_relative,
            "destination": source_relative, "sha256": binding["sha256"], "reason": "nonvoting review",
            "normalAdmission": True, "referenceVersion": "2" * 64, "referenceEligible": False,
            "membershipOnly": True,
        }, {
            "photoId": other_id, "source": other_relative, "destination": other_relative,
            "sha256": metadata.content_sha256(other), "reason": "ordinary requalification",
            "normalAdmission": True, "referenceVersion": "3" * 64, "referenceEligible": True,
            "membershipOnly": True,
        }]
        _published, updated, _removed = normal_products.stage(
            self.root, self.root / "_reports" / "mixed-stage", moves, None, profile="fast",
            photos=[], cfg={}, catalog=retired, policy=load_policy(), released_source_catalog=catalog,
        )
        member = updated["photos"][selected_id]["membership"]
        self.assertEqual(member["sourcePersonIds"], [])
        self.assertIsNone(member["personId"])
        self.assertFalse(member["coreUse"])
        self.assertEqual(updated["photos"][other_id]["membership"]["sourcePersonIds"], [owner])
        self.assertTrue(updated["photos"][other_id]["membership"]["coreUse"])
        self.assertNotIn(selected_id, catalog["photos"])

    def test_released_source_lineage_publication_and_recovery(self):
        from tools.art.likeness_library import normal_admission, normal_transaction
        from tools.art.likeness_library.policy import load_policy

        source = self.photo("Prospects/Owner/gallery/owner_image_123.jpg", b"fixture")
        photo_id = metadata.photo_id_from_name(source.name)
        checksum = metadata.content_sha256(source)
        owner, former = ("person_" + value * 32 for value in "ab")
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {
                owner: {"id": owner, "displayName": "Owner", "folder": "Prospects/Owner",
                        "folderHistory": [], "identityAnchors": [photo_id]},
                former: {"id": former, "displayName": "Former", "folder": "Models/Former",
                         "folderHistory": [], "identityAnchors": []},
            },
            "photos": {photo_id: {"contentSha256": checksum, "protected": False, "membership": {
                "personId": owner, "groupId": None, "status": "supported", "coreUse": True,
                "reason": "original", "referenceVersion": "1" * 64, "sourcePersonIds": [former],
            }}},
        }
        catalog_path = self.root / ".likeness-library.json"
        metadata.save_catalog(catalog, catalog_path)
        before_catalog, before_source = catalog_path.read_bytes(), source.read_bytes()
        relative = source.relative_to(self.root).as_posix()
        binding = {"photoId": photo_id, "currentPath": relative, "sha256": checksum}
        retired = normal_admission.retire_released_catalog(catalog, [binding])["catalog"]
        move = {
            "photoId": photo_id, "releasedPhotoId": photo_id, "source": relative,
            "destination": relative, "sha256": checksum, "reason": "fixture",
            "normalAdmission": True, "referenceVersion": "2" * 64,
            "referenceEligible": False, "membershipOnly": True,
        }
        run = self.root / "_reports" / "runs" / "released-provenance"
        stage, journal = run / "publication", run / "publication-journal.json"
        normal_products.stage(
            self.root, stage, [move], None, profile="fast", photos=[], cfg={},
            catalog=retired, policy=load_policy(), released_source_catalog=catalog,
        )
        normal_transaction.publish(
            self.root, stage, [relative], journal=journal, bindings={}, profile="fast",
            run_id="released-provenance", expected_sources={relative: checksum},
        )
        published = metadata.load_catalog(catalog_path)
        self.assertEqual(published["photos"][photo_id]["membership"]["sourcePersonIds"], sorted([owner, former]))
        self.assertNotIn(photo_id, published["people"][owner]["identityAnchors"])
        self.assertFalse(published["photos"][photo_id]["membership"]["coreUse"])
        normal_transaction.verify(self.root, journal)
        normal_transaction.recover(self.root, journal, apply=False)
        self.assertEqual(metadata.load_catalog(catalog_path), published)
        normal_transaction.recover(self.root, journal, apply=True)
        self.assertEqual(catalog_path.read_bytes(), before_catalog)
        self.assertEqual(source.read_bytes(), before_source)

    def test_released_stage_preserves_lineage_when_preparation_changes_native_hash(self):
        from tools.art.likeness_library import derivatives, normal_admission, normal_history, retained_preparation
        from tools.art.likeness_library.policy import load_policy

        source = self.photo("Prospects/Owner/gallery/owner_image_123.jpg", b"source")
        prepared_native = self.photo("_scratch/owner_image_123.jpg", b"prepared")
        photo_id = metadata.photo_id_from_name(source.name)
        checksum = metadata.content_sha256(source)
        owner = "person_" + "a" * 32
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {owner: {"id": owner, "displayName": "Owner", "folder": "Prospects/Owner",
                               "folderHistory": [], "identityAnchors": []}},
            "photos": {photo_id: {"contentSha256": checksum, "protected": False, "membership": {
                "personId": owner, "groupId": None, "status": "supported", "coreUse": True,
                "reason": "original", "referenceVersion": "1" * 64,
            }}},
        }
        relative = source.relative_to(self.root).as_posix()
        binding = {"photoId": photo_id, "currentPath": relative, "sha256": checksum}
        retired = normal_admission.retire_released_catalog(catalog, [binding])["catalog"]
        move = {
            "photoId": photo_id, "releasedPhotoId": photo_id, "source": relative,
            "destination": relative, "sha256": checksum, "reason": "fixture",
            "normalAdmission": True, "referenceVersion": "2" * 64, "referenceEligible": False,
        }
        prepared = (self.root / "_scratch", {"photos": [{"source": relative}], "recipe": {}},
                    {relative: prepared_native})
        photo = SimpleNamespace(name=source.name, box=None, px=0, faces=0)
        with mock.patch.object(retained_preparation, "stage_photo"), \
                mock.patch.object(normal_history, "stage"), \
                mock.patch.object(derivatives, "maintain", return_value=([], [])), \
                mock.patch.object(derivatives, "verified", side_effect=ValueError("fixture unavailable")), \
                mock.patch.object(derivatives, "expected_unavailability", return_value="fixture unavailable"):
            for profile in ("lean", "full"):
                with self.subTest(profile=profile):
                    _published, updated, _removed = normal_products.stage(
                        self.root, self.root / "_reports" / f"prepared-{profile}", [move], prepared,
                        profile=profile, photos=[photo], cfg={}, catalog=retired, policy=load_policy(),
                        released_source_catalog=catalog,
                    )
                    self.assertEqual(updated["photos"][photo_id]["contentSha256"],
                                     metadata.content_sha256(prepared_native))
                    self.assertEqual(updated["photos"][photo_id]["membership"]["sourcePersonIds"], [owner])
                    self.assertFalse(updated["photos"][photo_id]["membership"]["coreUse"])
        self.assertEqual(source.read_bytes(), b"source")

    def test_exact_content_alias_gets_its_own_retained_set_in_the_same_owner(self):
        from tools.art.likeness_library import derivatives, normal_history, retained_preparation
        from tools.art.likeness_library.policy import load_policy

        keeper = self.photo("Various/gallery/various_image_771.jpg", b"same bytes")
        alias = self.photo("Various/gallery/various_image_772.jpg", b"same bytes")
        native = self.photo("_scratch/selected_771.jpg", b"prepared")
        keeper_relative = keeper.relative_to(self.root).as_posix()
        alias_relative = alias.relative_to(self.root).as_posix()
        checksum = metadata.content_sha256(keeper)
        moves = [
            {"photoId": metadata.photo_id_from_name(path.name), "source": relative,
             "destination": f"Various/review/{path.name}", "sha256": checksum, "reason": "fixture"}
            for path, relative in ((keeper, keeper_relative), (alias, alias_relative))
        ]
        keeper_row = {"source": keeper_relative, "photoId": moves[0]["photoId"], "sourceSha256": checksum}
        prepared = (self.root / "_scratch", {
            "photos": [keeper_row], "recipe": {},
            "reuseSourceAliases": {alias_relative: {"preparedSource": keeper_relative, "sourceSha256": checksum}},
        }, {keeper_relative: native, alias_relative: native})
        photos = [SimpleNamespace(name=path.name, box=None, px=0, faces=0) for path in (keeper, alias)]
        with mock.patch.object(retained_preparation, "stage_photo") as retain, \
                mock.patch.object(normal_history, "stage"), \
                mock.patch.object(derivatives, "maintain", return_value=([], [])), \
                mock.patch.object(derivatives, "verified", side_effect=ValueError("fixture unavailable")), \
                mock.patch.object(derivatives, "expected_unavailability", return_value="fixture unavailable"):
            normal_products.stage(
                self.root, self.root / "_reports" / "alias-stage", moves, prepared, profile="lean",
                photos=photos, cfg={}, catalog=self.empty_catalog(), policy=load_policy(),
            )
        rows = [call.args[3] for call in retain.call_args_list]
        self.assertEqual([row["photoId"] for row in rows], [move["photoId"] for move in moves])
        self.assertEqual({row["source"] for row in rows}, {keeper_relative})
        self.assertEqual(keeper_row["photoId"], moves[0]["photoId"])

    def test_preview_and_apply_fail_closed_when_local_face_models_are_missing(self):
        from tools.art import likeness as api
        from likeness_library.engine import Embedder

        source = self.photo("Various/gallery/various_image_901.jpg", b"source pixels")
        cache = SimpleNamespace(stat={}, emb={})
        for persist_evidence in (False, True):
            with self.subTest(persist_evidence=persist_evidence), \
                    mock.patch("urllib.request.urlretrieve") as download:
                embedder = Embedder(self.root / f"missing-models-{persist_evidence}")
                with self.assertRaisesRegex(
                    ValueError, "read-only likeness requires an existing local model",
                ):
                    normal_rebase._infer(
                        api, cache, embedder, source,
                        persist_evidence=persist_evidence,
                    )
                download.assert_not_called()

    def test_apply_loads_local_face_models_read_only_then_persists_measurement(self):
        from tools.art import likeness as api

        source = self.photo("Various/gallery/various_image_902.jpg", b"source pixels")
        observations = {}

        class FakeEmbedder:
            det = None

            def load(self):
                observations["load_read_only"] = api.domains.READ_ONLY.get()
                self.det = object()

            def __call__(self, _path):
                observations["infer_read_only"] = api.domains.READ_ONLY.get()
                return {"v": [1.0, 0.0], "faces": 1, "px": 100, "t": "fixture"}

        cache = SimpleNamespace(stat={}, emb={})
        digest, data = normal_rebase._infer(
            api, cache, FakeEmbedder(), source,
            persist_evidence=True,
        )
        self.assertTrue(observations["load_read_only"])
        self.assertFalse(observations["infer_read_only"])
        self.assertEqual(cache.emb[digest], data)

    def test_various_pool_review_move_skips_identity_category_policy_audit(self):
        pool_move = {
            "photoId": "photo:image_903", "source": "Various/gallery/various_image_903.jpg",
            "destination": "Various/review/various_image_903.jpg", "sha256": "a" * 64,
            "reason": "unmatched pool candidate",
        }
        identity_move = {
            "photoId": "photo:image_904", "source": "Various/gallery/various_image_904.jpg",
            "destination": "Prospects/Owner/gallery/various_image_904.jpg",
            "sha256": "b" * 64, "reason": "matched candidate",
        }
        observed = {}

        def check_batch(_api, _space, _catalog, _policy, moves, *, update_ids=()):
            observed["moves"] = list(moves)
            observed["updateIds"] = set(update_ids)
            return list(moves), {"passCount": 1}

        with mock.patch.object(normal_rebase.normal_finish, "check_batch", side_effect=check_batch):
            checked, audit = normal_rebase._check_frozen_consistency(
                None, None, {}, {}, [pool_move, identity_move],
            )
        self.assertEqual(observed["moves"], [identity_move])
        self.assertEqual(checked, [identity_move, pool_move])
        self.assertEqual(audit["poolRetention"], [{
            "photoId": "photo:image_903",
            "destination": "Various/review/various_image_903.jpg",
            "decision": "retain-in-Various-pool",
            "reason": (
                "Various pool destinations are not identity categories; preserve the candidate role "
                "without applying identity-category consistency policy"
            ),
        }])

    def test_reused_preparation_requires_exact_recipe_configuration_profile_and_sources(self):
        from tools.art import image_preparation
        from tools.workflows import comfy_workflows as cw

        source = self.photo("Angels/Owner/gallery/owner_image_905.jpg", b"prepared source")
        source_relative = source.relative_to(self.root).as_posix()
        cfg = cw.load_cfg()
        output = (
            cw.storage_root(cfg, "reports", root=self.root) / "runs"
            / "normal-rebase-prior-preview" / "preparation" / "inputs"
            / "_reports" / "preparation" / "selected"
        )
        output.mkdir(parents=True)
        manifest = output / "manifest.json"
        manifest.write_text("fixture manifest", encoding="utf-8")
        mirror = output.parents[2]
        configuration = cw.storage_configuration_receipt(
            cfg, mirror,
            {
                "runOutput": output,
                "temporaryRoot": cw.storage_root(cfg, "temporary", root=mirror),
            },
        )
        data = {
            "recipe": image_preparation.RECIPE,
            "storageMode": "lean",
            "configurationReceipt": configuration,
            "photos": [{
                "source": source_relative,
                "sourceSha256": metadata.content_sha256(source),
            }],
        }
        prepared = (output, data, {source_relative: output / "native.png"})
        binding = normal_rebase._validate_preparation_reuse(
            self.root, cfg, "lean", prepared, [source],
        )
        self.assertEqual(binding["manifestSHA256"], metadata.content_sha256(manifest))
        self.assertEqual(binding["inputCount"], 1)
        self.assertEqual(binding["selectedInputCount"], 1)
        self.assertEqual(binding["unusedVerifiedInputCount"], 0)
        self.assertEqual(binding["recipeId"], image_preparation.CURRENT)
        self.assertIsNone(binding["generationProducerSHA256"])
        self.assertEqual(binding["generationProvenance"], "legacy-generation-hash-unrecorded")
        self.assertEqual(
            binding["validationProducerSHA256"],
            metadata.content_sha256(pathlib.Path(image_preparation.__file__)),
        )
        self.assertIn("does not record its historical", binding["provenanceWarning"])

        changed_configuration = dict(data)
        changed_configuration["configurationReceipt"] = dict(configuration)
        changed_configuration["configurationReceipt"]["sourceConfigurationSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "configuration differs"):
            normal_rebase._validate_preparation_reuse(
                self.root, cfg, "lean",
                (output, changed_configuration, prepared[2]), [source],
            )
        with self.assertRaisesRegex(ValueError, "profile differs"):
            normal_rebase._validate_preparation_reuse(
                self.root, cfg, "full", prepared, [source],
            )
        with self.assertRaisesRegex(ValueError, "source bindings differ"):
            normal_rebase._validate_preparation_reuse(
                self.root, cfg, "lean", prepared, [],
            )
        unused = self.photo("Various/gallery/various_image_906.jpg", b"no longer selected")
        subset_data = {
            **data, "photos": data["photos"] + [{
                "source": unused.relative_to(self.root).as_posix(),
                "sourceSha256": metadata.content_sha256(unused),
            }],
        }
        subset = normal_rebase._validate_preparation_reuse(
            self.root, cfg, "lean", (output, subset_data, prepared[2]), [source],
        )
        self.assertEqual(subset["inputCount"], 2)
        self.assertEqual(subset["selectedInputCount"], 1)
        self.assertEqual(subset["unusedVerifiedInputCount"], 1)
        self.assertEqual(subset["selectedInputSetSHA256"], binding["selectedInputSetSHA256"])
        self.assertNotEqual(subset["inputSetSHA256"], binding["inputSetSHA256"])
        alias = self.photo("Various/gallery/various_image_905.jpg", source.read_bytes())
        alias_source = alias.relative_to(self.root).as_posix()
        alias_data = {
            **data, "reuseSourceAliases": {
                alias_source: {"preparedSource": source_relative, "sourceSha256": metadata.content_sha256(alias)},
            },
        }
        alias_binding = normal_rebase._validate_preparation_reuse(
            self.root, cfg, "lean", (output, alias_data, {alias_source: prepared[2][source_relative]}), [alias],
        )
        self.assertEqual(alias_binding["selectedSourceAliases"], alias_data["reuseSourceAliases"])
        self.assertEqual(alias_binding["inputSetSHA256"], binding["inputSetSHA256"])

    def test_new_preparation_generation_seals_producer_before_and_after(self):
        from tools.art import image_preparation
        from tools.workflows import comfy_workflows as cw

        source = self.photo("Angels/Owner/gallery/owner_image_906.jpg", b"sealed source")
        cfg = cw.load_cfg()
        run = self.root / "_reports" / "runs" / "normal-rebase-origin-preview"
        start, start_path, start_hash = normal_rebase._write_preparation_origin_start(
            self.root, cfg, run, "lean", [source], workers=6,
        )
        output = run / "preparation" / "inputs" / "_reports" / "preparation" / "selected"
        output.mkdir(parents=True)
        (output / "manifest.json").write_text("sealed fixture manifest", encoding="utf-8")
        mirror = output.parents[2]
        configuration = cw.storage_configuration_receipt(
            cfg, mirror,
            {
                "runOutput": output,
                "temporaryRoot": cw.storage_root(cfg, "temporary", root=mirror),
            },
        )
        source_relative = source.relative_to(self.root).as_posix()
        data = {
            "recipe": image_preparation.RECIPE,
            "storageMode": "lean",
            "configurationReceipt": configuration,
            "photos": [{
                "source": source_relative,
                "sourceSha256": metadata.content_sha256(source),
            }],
        }
        prepared = (output, data, {source_relative: output / "native.png"})
        producer_path = pathlib.Path(image_preparation.__file__)
        original_hash = metadata.content_sha256

        def changed_producer(path):
            return "e" * 64 if pathlib.Path(path) == producer_path else original_hash(path)

        with mock.patch.object(metadata, "content_sha256", side_effect=changed_producer):
            with self.assertRaisesRegex(ValueError, "changed while selected preparation"):
                normal_rebase._write_preparation_origin_complete(
                    self.root, cfg, "lean", [source], prepared, start, start_hash,
                )
        with self.assertRaisesRegex(ValueError, "incomplete generation-origin seal"):
            normal_rebase._validate_preparation_reuse(
                self.root, cfg, "lean", prepared, [source],
            )
        complete = normal_rebase._write_preparation_origin_complete(
            self.root, cfg, "lean", [source], prepared, start, start_hash,
        )
        validated = normal_rebase._validate_preparation_reuse(
            self.root, cfg, "lean", prepared, [source],
        )
        self.assertTrue(start_path.is_file())
        self.assertEqual(start["workers"], 6)
        self.assertEqual(complete["workers"], 6)
        self.assertEqual(complete["generationProducerSHA256"], start["generationProducerSHA256"])
        self.assertEqual(
            complete["producerAfterGenerationSHA256"],
            start["generationProducerSHA256"],
        )
        self.assertTrue(complete["producerUnchangedDuringGeneration"])
        self.assertEqual(validated["generationProvenance"], "origin-sealed")
        self.assertEqual(validated["generationProducerSHA256"], start["generationProducerSHA256"])
        self.assertEqual(validated["validationProducerSHA256"], start["generationProducerSHA256"])
        self.assertIsNone(validated["provenanceWarning"])
        complete_path = normal_rebase._preparation_origin_paths(output)[1]
        complete_path.write_text(json.dumps({**complete, "workers": 2}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "origin seal does not match"):
            normal_rebase._validate_preparation_reuse(self.root, cfg, "lean", prepared, [source])

    def test_idless_original_uses_existing_content_id_and_keeps_source_identity_evidence(self):
        source = self.photo("Various/gallery/Brielle Carter.jpg", b"original photo bytes")
        row = self.source_rows()[0]
        expected = "photo:pic_" + originals.content_id(source)
        self.assertEqual(row["photoId"], expected)
        self.assertEqual(row["standardName"], "various_pic_" + originals.content_id(source) + ".jpg")
        self.assertEqual(row["originalName"], "Brielle Carter.jpg")
        self.assertEqual(row["source"], "Various/gallery/Brielle Carter.jpg")
        self.assertEqual(row["idBasis"], "raw-content-sha1-8")

    def test_exact_id_and_sha_aliases_have_one_keeper_and_one_vote(self):
        angel = self.photo("Angels/angelica/gallery/angelica_image_123.jpg", b"same original")
        alias = self.photo("Various/gallery/various_image_123.jpg", b"same original")
        rows = self.source_rows()
        active, held, aliases, _updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, self.empty_catalog(), None,
        )
        self.assertEqual([row["source"] for row in active], [angel.relative_to(self.root).as_posix()])
        self.assertEqual(len(aliases), 1)
        self.assertEqual(aliases[0]["source"], alias.relative_to(self.root).as_posix())
        self.assertEqual(aliases[0]["canonicalSource"], angel.relative_to(self.root).as_posix())
        self.assertEqual(held, [])

    def test_download_filename_uses_same_platform_id_as_normal_import_before_classification(self):
        owner = self.photo("Potentials/Owner/gallery/owner_image_7513773271576418822.jpg", b"same original")
        incoming = self.photo(
            "Various/gallery/.facebook_1791423147099_7513773271576418822.jpg", b"same original",
        )
        rows = self.source_rows()
        incoming_row = next(row for row in rows if row["source"] == incoming.relative_to(self.root).as_posix())
        self.assertEqual(incoming_row["photoId"], "photo:image_7513773271576418822")
        self.assertEqual(incoming_row["standardName"], "various_image_7513773271576418822.jpg")
        self.assertEqual(incoming_row["idBasis"], "normalized-source-filename")
        active, held, aliases, updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, self.empty_catalog(), None,
        )
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["photoId"], incoming_row["photoId"])
        self.assertIn(active[0]["source"], {
            owner.relative_to(self.root).as_posix(), incoming.relative_to(self.root).as_posix(),
        })
        self.assertEqual(len(aliases), 1)
        self.assertEqual(held, [])
        self.assertEqual(updates, {})

    def test_move_validation_rejects_changed_ids_and_case_insensitive_destination_collisions(self):
        move = {
            "photoId": "photo:image_123", "source": "Various/gallery/various_image_123.jpg",
            "destination": "Potentials/Owner/gallery/owner_image_123.jpg",
        }
        normal_rebase._validate_move_destinations([move])
        with self.assertRaisesRegex(ValueError, "destination changes the stable photo ID"):
            normal_rebase._validate_move_destinations([{**move, "photoId": "photo:pic_12345678"}])
        with self.assertRaisesRegex(ValueError, "destination collision"):
            normal_rebase._validate_move_destinations([
                move, {**move, "source": "Various/review/other_image_123.jpg",
                       "destination": move["destination"].upper()},
            ])

    def test_existing_exact_alias_target_requires_bound_evidence_and_unchanged_bytes(self):
        source = self.photo("Various/gallery/various_image_123.jpg", b"same original")
        destination = self.photo("Potentials/Owner/gallery/owner_image_123.jpg", b"same original")
        move = {
            "photoId": "photo:image_123", "source": source.relative_to(self.root).as_posix(),
            "destination": destination.relative_to(self.root).as_posix(),
            "sha256": metadata.content_sha256(source),
        }
        target = {
            "source": move["destination"], "sourceStatus": "exact-byte-alias",
            "canonicalSource": move["source"], "photoId": move["photoId"],
            "sourceHash": move["sha256"],
        }
        aliases = normal_rebase._exact_alias_targets([target], [move])
        with self.assertRaisesRegex(ValueError, "destination already exists"):
            normal_rebase.maintenance.validate_moves(self.root, [move])
        normal_rebase.maintenance.validate_moves(
            self.root, [move], exact_alias_targets=aliases,
        )
        stage = self.root / "_reports" / "alias-publication"
        selected = stage / pathlib.PurePosixPath(move["destination"])
        selected.parent.mkdir(parents=True)
        selected.write_bytes(b"selected prepared native")
        journal = stage.parent / "alias-journal.json"
        normal_rebase.normal_transaction.publish(
            self.root, stage, [move["source"]], journal=journal,
            bindings={}, profile="lean", run_id="alias-proof",
            expected_sources={move["source"]: move["sha256"], move["destination"]: move["sha256"]},
        )
        self.assertFalse(source.exists())
        self.assertEqual(destination.read_bytes(), selected.read_bytes())
        normal_rebase.normal_transaction.recover(self.root, journal, apply=True)
        self.assertEqual(source.read_bytes(), b"same original")
        self.assertEqual(destination.read_bytes(), b"same original")
        destination.write_bytes(b"changed target")
        with self.assertRaisesRegex(ValueError, "destination already exists"):
            normal_rebase.maintenance.validate_moves(
                self.root, [move], exact_alias_targets=aliases,
            )
        for field, value in (
            ("sourceStatus", "held"), ("canonicalSource", "Various/gallery/other.jpg"),
            ("photoId", "photo:image_999"), ("sourceHash", "0" * 64),
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "verified exact alias"):
                normal_rebase._exact_alias_targets([{**target, field: value}], [move])

    def test_low_member_audit_recommends_without_removing_protected_or_unsplittable_gallery(self):
        from tools.art.likeness_library.policy import load_policy

        for category, person_protected, split_enabled, expected_move in (
            ("Sisters", False, False, False),
            ("Prospects", True, True, False),
            ("Prospects", False, False, False),
            ("Prospects", False, True, True),
        ):
            with self.subTest(category=category, protected=person_protected, split=split_enabled):
                policy = load_policy()
                policy["categoryPolicies"][category]["automaticSplitEnabled"] = split_enabled
                folder = f"{category}/Owner"
                source = folder + "/gallery/owner_image_123.jpg"
                move = {
                    "photoId": "photo:image_123", "source": source, "destination": source,
                    "reason": "single existing low-member audit", "auditOnly": True,
                }
                catalog = self.empty_catalog()
                catalog["people"]["owner"] = {"folder": folder, "protected": person_protected}
                photo = SimpleNamespace(name="owner_image_123.jpg", vec=np.array([0.0, 1.0]))
                space = SimpleNamespace(photos=[photo])
                core = {
                    "vector": np.array([1.0, 0.0]), "photoScores": {},
                    "corePhotoIds": [], "identityProtected": person_protected,
                }
                with mock.patch.object(
                    normal_rebase.normal_finish, "cores", return_value=({folder: core}, []),
                ), mock.patch.object(
                    normal_rebase.normal_finish, "evaluate_photo_consistency",
                    return_value={"decision": "review"},
                ):
                    checked, audit = normal_rebase.normal_finish.check_batch(
                        None, space, catalog, policy, [move],
                    )
                self.assertEqual(
                    checked[0]["destination"],
                    source.replace("/gallery/", "/review/") if expected_move else source,
                )
                self.assertEqual(len(audit["corrections"]), int(expected_move))
                self.assertEqual(len(audit["recommendations"]), int(not expected_move))

    def test_same_bytes_under_different_ids_preserve_ids_but_cast_one_core_vote(self):
        first = self.photo("Prospects/Owner/gallery/owner_image_124.jpg", b"one physical image")
        second = self.photo("Prospects/Owner/gallery/owner_image_125.jpg", b"one physical image")
        rows = self.source_rows()
        active, held, _aliases, _updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, self.empty_catalog(), None,
        )
        self.assertEqual(len(active), 1)
        self.assertEqual(
            {row["photoId"] for row in active + held},
            {"photo:image_124", "photo:image_125"},
        )
        self.assertEqual(active[0]["photoId"], "photo:image_124")
        self.assertEqual(held[0]["photoId"], "photo:image_125")
        self.assertIn("different stable ID", held[0]["reason"])
        self.assertEqual(held[0]["contentVoteCanonicalId"], active[0]["photoId"])
        api = self.stub_api([("Prospects", "Owner", first.parent.parent)])
        photo = api.Photo(
            self.root / pathlib.PurePosixPath(active[0]["source"]),
            "Prospects", "Owner", active[0]["sourceHash"],
            {"v": [1.0, 0.0], "faces": 1, "px": 100},
        )
        photo.name = active[0]["standardName"]
        space = api.Space([photo], {"minFace": 1})
        cores, _locked, _diagnostics = normal_rebase.reconciliation.frozen_identity_cores(
            space, self.empty_catalog(),
            photo_id_fn=metadata.photo_id_from_name,
            content_sha256_fn=metadata.content_sha256,
            policy={"categoryPolicies": {"Prospects": {
                "minimumUsablePhotosForOutlierActions": 3,
                "identityCoreMinimumSimilarity": 0.3,
            }}},
        )
        self.assertEqual(cores["Prospects/Owner"]["corePhotoIds"], ["photo:image_124"])
        self.assertEqual(first.read_bytes(), second.read_bytes())

        owner_a = self.photo("Angels/angelica/gallery/angelica_image_126.jpg", b"owner conflict")
        owner_b = self.photo("Sisters/SisterA/gallery/sistera_image_127.jpg", b"owner conflict")
        rows = self.source_rows()
        active, held, _aliases, _updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, self.empty_catalog(), None,
        )
        self.assertEqual(
            {row["photoId"] for row in held if row["photoId"] in {"photo:image_126", "photo:image_127"}},
            {"photo:image_126", "photo:image_127"},
        )
        self.assertTrue(all(
            "conflicting named-owner" in row["reason"]
            for row in held if row["photoId"] in {"photo:image_126", "photo:image_127"}
        ))

        anchored = self.photo("Angels/angelica/gallery/angelica_image_128.jpg", b"anchored conflict")
        selected = self.photo("Various/gallery/various_image_129.jpg", b"anchored conflict")
        catalog = self.empty_catalog()
        catalog["people"]["angelica"] = {
            "folder": "Angels/angelica", "identityAnchors": ["photo:image_128"],
        }
        cfg = {"photos": {"selected": "various_image_129_944x1104.png"}}
        active, held, _aliases, _updates, _workflow = normal_rebase._classify_sources(
            self.root, self.source_rows(cfg), cfg, catalog, None,
        )
        self.assertFalse(any(
            row["photoId"] in {"photo:image_128", "photo:image_129"} for row in active
        ))
        self.assertEqual(
            {row["photoId"] for row in held if row["photoId"] in {"photo:image_128", "photo:image_129"}},
            {"photo:image_128", "photo:image_129"},
        )
        self.assertEqual(anchored.read_bytes(), selected.read_bytes())

    def test_conflicting_chosen_aliases_and_multiple_anchors_are_held(self):
        first = self.photo("Angels/angelica/gallery/angelica_image_555.jpg", b"same")
        second = self.photo("Prospects/Owner/gallery/owner_image_555.jpg", b"same")
        rows = self.source_rows()
        cfg = {"photos": {"first": "angelica_image_555_944x1104.png", "second": "owner_image_555_944x1104.png"}}
        active, held, _aliases, _updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, cfg, self.empty_catalog(), None,
        )
        self.assertEqual(active, [])
        self.assertEqual({row["source"] for row in held}, {
            first.relative_to(self.root).as_posix(), second.relative_to(self.root).as_posix(),
        })
        rows = self.source_rows()
        catalog = self.empty_catalog()
        catalog["people"] = {
            "a": {"folder": "Angels/angelica", "identityAnchors": ["photo:image_555"]},
            "b": {"folder": "Prospects/Owner", "identityAnchors": ["photo:image_555"]},
        }
        active, held, _aliases, _updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None,
        )
        self.assertEqual(active, [])
        self.assertEqual(len(held), 2)

    def test_unique_newest_incoming_replaces_one_catalog_bound_owner(self):
        current = self.photo("Angels/angelica/gallery/angelica_image_777.jpg", b"old native")
        incoming = self.photo("Various/gallery/various_image_777.jpg", b"replacement original")
        old_time = 1_700_000_000_000_000_000
        current.touch()
        incoming.touch()
        current_stat, incoming_stat = current.stat(), incoming.stat()
        import os
        os.utime(current, ns=(old_time, old_time))
        os.utime(incoming, ns=(old_time + 2_000_000, old_time + 2_000_000))
        catalog = self.empty_catalog()
        catalog["photos"]["photo:image_777"] = {
            "contentSha256": metadata.content_sha256(current), "protected": False,
        }
        rows = self.source_rows()
        active, held, _aliases, updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None,
        )
        self.assertEqual(set(updates), {"photo:image_777"})
        self.assertEqual(active[0]["source"], incoming.relative_to(self.root).as_posix())
        self.assertEqual(active[0]["updateOwner"], "Angels/angelica")
        self.assertEqual(active[0]["previousHash"], metadata.content_sha256(current))
        self.assertIn(current.relative_to(self.root).as_posix(), {row["source"] for row in held})

    def test_retained_original_in_various_is_not_a_new_replacement_or_voter(self):
        current = self.photo("Angels/angelica/gallery/angelica_image_777.jpg", b"prepared native")
        incoming = self.photo("Various/gallery/various_image_777.jpg", b"retained original")
        for protected in (False, True):
            with self.subTest(protected=protected):
                catalog = self.empty_catalog()
                catalog["photos"]["photo:image_777"] = {
                    "contentSha256": metadata.content_sha256(current), "protected": protected,
                }
                rows = self.source_rows()
                current_row = next(row for row in rows if row["group"] == "Angels")
                current_row.update({
                    "retainedManifest": "verified-retained-manifest.json",
                    "retainedSourceHash": metadata.content_sha256(incoming),
                })
                active, held, aliases, updates, _workflow = normal_rebase._classify_sources(
                    self.root, rows, {}, catalog, None,
                )
                self.assertEqual([row["source"] for row in active], [current.relative_to(self.root).as_posix()])
                self.assertEqual(len(held), 1)
                self.assertTrue(held[0]["retainedOriginalAlias"])
                self.assertEqual(held[0]["selectedSource"], current_row["source"])
                self.assertEqual(aliases, [])
                self.assertEqual(updates, {})
                self.assertEqual(incoming.read_bytes(), b"retained original")

    def test_prepared_greta_style_alias_in_another_owner_is_archived_before_scoring(self):
        current = self.photo("Models/Greta/gallery/greta_image_777.jpg", b"prepared")
        raw = self.photo("Potentials/Florence/gallery/florence_image_777.jpg", b"raw")
        os.utime(raw, ns=(1_800_000_000_000_000_000,) * 2)
        rows = self.source_rows()
        current_row = next(row for row in rows if row["group"] == "Models")
        current_row.update(retainedManifest="verified-fixture", retainedSourceHash=metadata.content_sha256(raw))
        active, held, _aliases, updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, self.empty_catalog(), None, archive_collisions=True,
        )
        self.assertEqual([row["source"] for row in active], [current.relative_to(self.root).as_posix()])
        self.assertEqual((held, updates), ([], {}))
        archives = normal_rebase._duplicate_archives(self.root, rows, "fixture")
        self.assertEqual(archives[raw.relative_to(self.root).as_posix()]["reason"], "verified retained raw original")
        self.assertTrue(raw.exists())

    def test_newest_generic_edit_routes_to_vacated_path_and_archive_undo_preserves_dates(self):
        from tools.art.likeness_library import maintenance, normal_transaction
        from tools.workflows import comfy_workflows as cw

        old = self.photo("Models/Owner/gallery/owner_image_777.jpg", b"old owner")
        copy = self.photo("Prospects/Other/gallery/other_image_777.jpg", b"old owner")
        edit = self.photo("Various/gallery/image_777.jpg", b"new edit")
        for i, path in enumerate((old, copy, edit)):
            os.utime(path, ns=(1_700_000_000_000_000_000 + i * 1_000_000_000,) * 2)
        def relative(path):
            return path.relative_to(self.root).as_posix()
        rows = self.source_rows()
        catalog = self.empty_catalog()
        active, held, _aliases, updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None, archive_collisions=True,
        )
        self.assertEqual((held, updates), ([], {}))
        self.assertEqual([row["source"] for row in active], [relative(edit)])
        archives = normal_rebase._duplicate_archives(self.root, rows, "fixture")
        self.assertEqual(set(archives), {relative(old), relative(copy)})
        self.assertEqual(len({row["destination"] for row in archives.values()}), 2)
        move = {
            "photoId": "photo:image_777", "source": relative(edit),
            "destination": relative(old), "sha256": metadata.content_sha256(edit),
        }
        with self.assertRaisesRegex(ValueError, "destination already exists"):
            maintenance.validate_moves(self.root, [move])
        maintenance.validate_moves(self.root, [move], duplicate_archives=archives)
        stage = self.root / "_reports" / "fixture" / "publication"
        published, _, removed = normal_products.stage(
            self.root, stage, [move], None, profile="fast", photos=[], cfg={}, catalog=catalog,
            policy=normal_rebase.load_policy(), archives=archives,
        )
        self.assertEqual(sum(bool(row.get("duplicateArchive")) for row in published), 2)
        journal = stage.parent / "journal.json"
        sources = {row["source"]: row["sourceHash"] for row in rows}
        dates = {row["source"]: row["collisionModifiedNs"] for row in rows}
        os.utime(edit, ns=(dates[relative(edit)] + 2_000_000_000,) * 2)
        with self.assertRaisesRegex(ValueError, "collision date changed"):
            normal_transaction.publish(
                self.root, stage, sorted(set(sources) | set(removed)), journal=journal,
                bindings={}, profile="fast", run_id="fixture", expected_sources={**sources, **removed},
                expected_modified_ns=dates,
            )
        os.utime(edit, ns=(dates[relative(edit)],) * 2)
        normal_transaction.publish(
            self.root, stage, sorted(set(sources) | set(removed)), journal=journal,
            bindings={}, profile="fast", run_id="fixture", expected_sources={**sources, **removed},
            expected_modified_ns=dates,
        )
        self.assertEqual(old.read_bytes(), b"new edit")
        self.assertFalse(edit.exists())
        self.assertFalse(copy.exists())
        for row in archives.values():
            saved = self.root / row["destination"]
            self.assertEqual(saved.read_bytes(), b"old owner")
            self.assertEqual(saved.stat().st_mtime_ns, dates[row["source"]])
        self.assertEqual([group for group, *_ in cw.photo_folders({}, self.root) if group == "_duplicates"], [])
        normal_transaction.recover(self.root, journal, apply=True)
        for source, digest in sources.items():
            self.assertEqual(metadata.content_sha256(self.root / source), digest)
            self.assertEqual((self.root / source).stat().st_mtime_ns, dates[source])
        self.assertTrue(all(not (self.root / row["destination"]).exists() for row in archives.values()))

    def test_pool_duplicates_and_measured_no_face_publish_as_distinct_recoverable_dispositions(self):
        from tools.art.likeness_library import normal_transaction, retained_preparation

        keeper = self.photo("Angels/Ava/gallery/ava_image_901.jpg", b"existing cast original")
        copy = self.photo("Various/gallery/image_902.jpg", keeper.read_bytes())
        no_face = self.photo("Various/gallery/image_903.jpg", b"decoded without a face")
        unknown = self.photo("Various/gallery/image_904.jpg", b"read or cache failure")
        workflow = self.photo("Various/review/image_905.jpg", b"workflow-selected no face")
        relative = lambda path: path.relative_to(self.root).as_posix()
        retained = self.photo("fixture-recipe/original.jpg", no_face.read_bytes())
        detail = self.photo("fixture-recipe/detail.html", b"<html><body></body></html>")
        thumb = self.photo("fixture-recipe/thumb.jpg", b"thumbnail")
        retained_preparation.stage_photo(
            self.root, relative(no_face), retained.parent, {
                "source": relative(no_face), "photoId": "photo:image_903",
                "sourceSha256": metadata.content_sha256(retained), "retained": retained.name,
                "detail": detail.name, "detailSha256": metadata.content_sha256(detail),
                "sourceScope": {"matchingDomain": "general"},
                "processing": {"final": "control"},
                "variants": {"control": {
                    "path": retained.name, "sha256": metadata.content_sha256(retained),
                    "thumbnail": thumb.name, "thumbnailSha256": metadata.content_sha256(thumb),
                }},
            }, recipe={"id": "test"}, storage_mode="lean",
        )
        catalog = self.empty_catalog()
        catalog["photos"]["photo:image_903"] = {"contentSha256": metadata.content_sha256(no_face), "protected": False}
        rows = self.source_rows()
        active, _held, _aliases, _updates, _workflow_ids = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None, archive_collisions=True,
        )
        for row in active:
            row.setdefault("sourceStatus", "eligible")
        archives = normal_rebase._duplicate_archives(self.root, rows, "fixture")
        self.assertEqual(list(archives), [relative(copy)])
        self.assertEqual(archives[relative(copy)]["selectedPhotoId"], "photo:image_901")
        measurement = {
            relative(path): ("unused", data) for path, data in (
                (no_face, {"faces": 0, "t": 0.5}), (unknown, {"faces": 0}),
                (workflow, {"faces": 0, "t": 0.5}),
            )
        }
        junk = normal_rebase._no_face_dispositions(
            self.root, active, measurement, catalog, {"photo:image_905"}, "_junk",
        )
        self.assertEqual(list(junk), [relative(no_face)])
        self.assertTrue(all(path.is_file() for path in (keeper, copy, no_face, unknown, workflow)))
        stage = self.root / "_reports" / "fixture" / "publication"
        published, _, removed = normal_products.stage(
            self.root, stage, [], None, profile="fast", photos=[], cfg={}, catalog=catalog,
            policy=normal_rebase.load_policy(), archives=archives, junk=junk,
        )
        journal = stage.parent / "journal.json"
        normal_transaction.publish(
            self.root, stage, sorted(set(archives) | set(junk) | set(removed)), journal=journal,
            bindings={}, profile="fast", run_id="fixture",
            expected_sources={row["source"]: row["sourceHash"] for row in rows},
        )
        normal_transaction.verify(self.root, journal)
        self.assertEqual(sum(bool(row.get("duplicateArchive")) for row in published), 1)
        self.assertEqual(sum(bool(row.get("junkDisposition")) for row in published), 1)
        for path, record, prefix in ((copy, archives[relative(copy)], "_duplicates"), (no_face, junk[relative(no_face)], "_junk")):
            self.assertFalse(path.exists())
            archived = self.root / record["destination"]
            self.assertTrue(archived.is_relative_to(self.root / prefix))
            self.assertEqual(metadata.content_sha256(archived), record["sha256"])
        self.assertTrue(all(path.is_file() for path in (keeper, unknown, workflow)))
        self.assertIsNotNone(retained_preparation.verify_link(self.root, self.root / junk[relative(no_face)]["destination"]))
        normal_transaction.recover(self.root, journal, apply=True)
        self.assertTrue(all(path.is_file() for path in (keeper, copy, no_face, unknown, workflow)))
        self.assertIsNotNone(retained_preparation.verify_link(self.root, no_face))
        for disposition in (archives[relative(copy)], junk[relative(no_face)]):
            self.assertFalse((self.root / disposition["destination"]).exists())

    def test_every_identical_copy_is_archived_and_its_catalogue_membership_retires(self):
        from tools.art.likeness_library import normal_transaction

        keeper = self.photo("Potentials/Florence/gallery/florence_image_801.jpg", b"same bytes")
        named_copy = self.photo("Potentials/Florence/gallery/florence_image_802.jpg", b"same bytes")
        review_copy = self.photo("Various/review/various_image_803.jpg", b"same bytes")
        relative = lambda path: path.relative_to(self.root).as_posix()  # noqa: E731
        owner = "person_" + "f" * 32
        catalog = self.empty_catalog()
        catalog["people"][owner] = {
            "id": owner, "displayName": "Florence", "folder": "Potentials/Florence",
            "folderHistory": [], "identityAnchors": [],
        }
        for path in (keeper, named_copy, review_copy):
            catalog["photos"][metadata.photo_id_from_name(path.name)] = {
                "contentSha256": metadata.content_sha256(path), "protected": False,
                **({"membership": {"personId": owner, "groupId": None, "status": "supported",
                                   "coreUse": True, "reason": "fixture", "referenceVersion": "1" * 64}}
                   if path is not review_copy else {}),
            }
        catalog["actions"].append({"id": "action_" + "b" * 32, "timestamp": "2026-11-22T00:00:00Z",
                                   "actor": "user", "type": "sent-to-review",
                                   "destination": relative(review_copy),
                                   "photoIds": [metadata.photo_id_from_name(review_copy.name)]})
        metadata.validate_catalog(catalog)
        rows = self.source_rows()
        active, held, *_ = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None, archive_collisions=True,
        )
        # Item (a): catalogued, user-touched and named-Gallery copies are all archived.
        self.assertEqual([row["source"] for row in active], [relative(keeper)])
        self.assertEqual(held, [])
        archives = normal_rebase._duplicate_archives(self.root, rows, "fixture")
        self.assertEqual(set(archives), {relative(named_copy), relative(review_copy)})
        self.assertTrue(all(row["selectedSource"] == relative(keeper) for row in archives.values()))
        legacy, legacy_held, *_ = normal_rebase._classify_sources(
            self.root, self.source_rows(), {}, catalog, None, archive_collisions=False,
        )
        self.assertEqual(len(legacy_held), 2)
        stage = self.root / "_reports" / "fixture" / "publication"
        published, updated, removed = normal_products.stage(
            self.root, stage, [], None, profile="fast", photos=[], cfg={}, catalog=catalog,
            policy=normal_rebase.load_policy(), archives=archives,
        )
        self.assertEqual(sum(bool(row.get("duplicateArchive")) for row in published), 2)
        copy_id = metadata.photo_id_from_name(named_copy.name)
        self.assertNotIn("membership", updated["photos"][copy_id])
        self.assertIn("membership", updated["photos"][metadata.photo_id_from_name(keeper.name)])
        journal = stage.parent / "journal.json"
        normal_transaction.publish(
            self.root, stage, sorted(set(archives) | set(removed)), journal=journal,
            bindings={}, profile="fast", run_id="fixture",
            expected_sources={row["source"]: row["sourceHash"] for row in rows},
        )
        self.assertTrue(keeper.is_file())
        self.assertFalse(named_copy.exists() or review_copy.exists())
        normal_transaction.recover(self.root, journal, apply=True)
        self.assertTrue(named_copy.is_file() and review_copy.is_file())

    def test_anchored_or_protected_only_copies_stay_held_non_voters(self):
        keeper = self.photo("Various/gallery/various_image_811.jpg", b"cast bytes")
        cast_copy = self.photo("Angels/Ava/gallery/ava_image_812.jpg", b"cast bytes")
        relative = lambda path: path.relative_to(self.root).as_posix()  # noqa: E731
        cfg = {"photos": {"Ava": keeper.name}}
        rows = self.source_rows(cfg)
        active, held, *_ = normal_rebase._classify_sources(
            self.root, rows, cfg, self.empty_catalog(), None, archive_collisions=True,
        )
        # A chosen Various keeper cannot strip the only copy from a protected cast Gallery.
        self.assertEqual([row["source"] for row in active], [relative(keeper)])
        self.assertEqual([row["source"] for row in held], [relative(cast_copy)])
        self.assertEqual(held[0]["sourceStatus"], "same-content-nonvoting")
        self.assertEqual(normal_rebase._duplicate_archives(self.root, rows, "fixture"), {})
        keeper.unlink()
        cast_copy.unlink()
        first = self.photo("Potentials/Gwen/gallery/gwen_image_821.jpg", b"anchored bytes")
        anchored = self.photo("Potentials/Gwen/gallery/gwen_image_822.jpg", b"anchored bytes")
        person = "person_" + "a" * 32
        catalog = self.empty_catalog()
        catalog["people"][person] = {
            "id": person, "displayName": "Gwen", "folder": "Potentials/Gwen",
            "folderHistory": [], "identityAnchors": [metadata.photo_id_from_name(anchored.name)],
        }
        rows = self.source_rows()
        active, held, *_ = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None, archive_collisions=True,
        )
        self.assertEqual([row["source"] for row in active], [relative(first)])
        self.assertEqual([(row["source"], row["sourceStatus"]) for row in held],
                         [(relative(anchored), "same-content-nonvoting")])
        self.assertEqual(normal_rebase._duplicate_archives(self.root, rows, "fixture"), {})

    def test_dominant_face_photo_matches_without_reference_vote_and_ambiguous_face_is_held(self):
        from tools.art.likeness_library.reconciliation import plan_reconciliation

        paths = [
            self.photo("Prospects/Owner/gallery/owner_image_301.jpg", b"reference 1"),
            self.photo("Prospects/Owner/gallery/owner_image_302.jpg", b"reference 2"),
            self.photo("Various/gallery/various_image_303.jpg", b"dominant"),
            self.photo("Various/gallery/various_image_304.jpg", b"two people"),
        ]
        measurements = {
            b"reference 1": {"v": [1., .1], "faces": 1, "px": 1000},
            b"reference 2": {"v": [1., -.1], "faces": 1, "px": 1000},
            b"dominant": {"v": [1., 0.], "faces": 2, "f2": .4, "px": 900, "box": [.3, .2, .2, .25]},
            b"two people": {"v": [1., 0.], "faces": 2, "f2": .7, "px": 900, "box": [.3, .2, .2, .25]},
        }
        api = self.stub_api([
            ("Prospects", "Owner", self.root / "Prospects" / "Owner"), ("Various", "Various", self.root / "Various"),
        ])
        base_space = api.Space

        class FixtureSpace(base_space):
            def __init__(self, photos, settings, mean=None):
                super().__init__(photos, settings, mean=np.zeros(2))

        api.Space = FixtureSpace
        api.plan_reconciliation = plan_reconciliation
        api.invent_name = lambda seed, _taken: "Fixture-" + seed[:8]
        metadata.save_catalog(self.empty_catalog(), self.root / ".likeness-library.json")
        dominant_id, ambiguous_id = (metadata.photo_id_from_name(path.name) for path in paths[2:])
        with mock.patch.object(normal_rebase, "_infer", side_effect=lambda _api, _cache, _embed, path, **_kw: (
                metadata.content_sha256(path), {**measurements[pathlib.Path(path).read_bytes()], "t": "fixture"},
        )), mock.patch.object(normal_rebase, "_fragment_evidence", return_value={}), \
                mock.patch.object(normal_rebase, "_bindings", return_value={"fixture": "bound"}), \
                mock.patch.object(normal_rebase.normal_finish, "check_batch",
                                  side_effect=lambda _api, _space, _catalog, _policy, moves, **_kw: (
                                      list(moves), {"passCount": 1, "frozenRivals": {}, "corrections": []},
                                  )), \
                mock.patch.object(normal_rebase.maintenance, "_validate_permissions"):
            report, *_ = normal_rebase._plan(self.root, "fast", "dominant-fixture", api=api)
        decisions = {row["photoId"]: row for row in report["assignments"] + report["held"]}
        dominant = decisions[dominant_id]
        self.assertEqual(dominant["destination"], "Prospects/Owner")
        self.assertFalse(dominant["referenceEligible"])
        self.assertEqual(dominant["faceQuality"]["class"], "dominant-face")
        self.assertNotIn(dominant_id, {
            pid for snapshot in report["referenceSnapshots"].values()
            for ids in snapshot["photoIds"].values() for pid in ids
        })
        move = next(row for row in report["moves"] if row["photoId"] == dominant_id)
        self.assertEqual(move["faceQuality"]["class"], "dominant-face")
        self.assertFalse(move["referenceEligible"])
        ambiguous = decisions[ambiguous_id]
        self.assertTrue(ambiguous["preserveStaged"])
        self.assertIn("second face is at least 50%", ambiguous["reason"])
        self.assertEqual(ambiguous["faceQuality"]["class"], "multi-face-held")

    def test_explicit_review_action_is_bound_to_its_path_and_respects_undo(self):
        action = {"id": "set-review", "actor": "user", "type": "sent-to-review",
                  "destination": "Sisters/Owner/review/owner_image_901.jpg", "photoIds": ["photo:image_901"]}
        self.assertEqual(
            normal_rebase._explicit_review_placements({"actions": [action]}),
            {("photo:image_901", action["destination"])},
        )
        self.assertEqual(
            normal_rebase._explicit_review_placements(
                {"actions": [action, {"type": "action-undone", "undoes": action["id"]}]},
            ), set(),
        )

    def test_time_tie_is_resolved_and_a_new_edit_does_not_displace_protected_gallery(self):
        old = self.photo("Angels/Ava/gallery/ava_image_777.jpg", b"cast original")
        edit = self.photo("Various/gallery/image_777.jpg", b"edited bytes")
        lower = self.photo("Models/Other/gallery/other_image_888.jpg", b"lower original")
        new_lower = self.photo("Various/gallery/image_888.jpg", b"other edit")
        base = 1_700_000_000_000_000_000
        for path in (old, lower, new_lower):
            os.utime(path, ns=(base, base))
        os.utime(edit, ns=(base + 1_000_000_000,) * 2)
        rows = self.source_rows()
        active, held, *_ = normal_rebase._classify_sources(
            self.root, rows, {}, self.empty_catalog(), None, archive_collisions=True,
        )
        self.assertEqual(held, [])
        self.assertEqual({row["source"] for row in active}, {
            old.relative_to(self.root).as_posix(), lower.relative_to(self.root).as_posix(),
        })
        self.assertIn("tied", active[1]["collisionRule"])
        self.assertEqual(len(normal_rebase._duplicate_archives(self.root, rows, "fixture")), 2)

    def test_two_protected_owners_keep_the_bound_photo_and_archive_the_other(self):
        old = self.photo("Angels/Ava/gallery/ava_image_777.jpg", b"cast original")
        winner = self.photo("Sisters/Bea/gallery/bea_image_777.jpg", b"different cast original")
        catalog = self.empty_catalog()
        catalog["photos"]["photo:image_777"] = {
            "contentSha256": metadata.content_sha256(winner), "protected": False,
        }
        rows = self.source_rows()
        active, held, *_ = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None, archive_collisions=True,
        )
        self.assertEqual([row["source"] for row in active], [winner.relative_to(self.root).as_posix()])
        self.assertEqual(held, [])
        self.assertIn("protected Gallery keeper", active[0]["collisionRule"])
        archives = normal_rebase._duplicate_archives(self.root, rows, "fixture")
        self.assertEqual(set(archives), {old.relative_to(self.root).as_posix()})
        self.assertEqual(normal_rebase._unresolved_duplicate_ids(rows, archives), [])

    def test_archived_prepared_loser_keeps_verified_lineage_when_winner_reuses_path(self):
        from tools.art.likeness_library import normal_history, normal_transaction, retained_preparation

        old = self.photo("Models/Owner/gallery/owner_image_777.jpg", b"prepared")
        edit = self.photo("Various/gallery/image_777.jpg", b"edited bytes")
        os.utime(old, ns=(1_700_000_000_000_000_000,) * 2)
        os.utime(edit, ns=(1_700_000_001_000_000_000,) * 2)
        old_relative = old.relative_to(self.root).as_posix()
        edit_relative = edit.relative_to(self.root).as_posix()
        original = self.photo("recipe/original.jpg", b"original")
        native = self.photo("recipe/native.png", b"prepared")
        detail = self.photo("recipe/detail.html", b"<html><body></body></html>")
        thumb = self.photo("recipe/thumb.jpg", b"thumbnail")
        retained_preparation.stage_photo(
            self.root, old_relative, native.parent, {
                "source": old_relative, "photoId": "photo:image_777",
                "sourceSha256": metadata.content_sha256(original), "retained": original.name,
                "detail": detail.name, "detailSha256": metadata.content_sha256(detail),
                "sourceScope": {"matchingDomain": "general"},
                "processing": {"final": "composition"},
                "variants": {"composition": {
                    "path": native.name, "sha256": metadata.content_sha256(native),
                    "thumbnail": thumb.name, "thumbnailSha256": metadata.content_sha256(thumb),
                }},
            }, recipe={"id": "test"}, storage_mode="lean",
        )
        self.assertIsNotNone(retained_preparation.verify_link(self.root, old))
        rows = self.source_rows()
        catalog = self.empty_catalog()
        normal_rebase._classify_sources(self.root, rows, {}, catalog, None, archive_collisions=True)
        archives = normal_rebase._duplicate_archives(self.root, rows, "fixture")
        stage = self.root / "_reports" / "fixture" / "publication"
        _published, _, removed = normal_products.stage(
            self.root, stage, [{
                "photoId": "photo:image_777", "source": edit_relative,
                "destination": old_relative, "sha256": metadata.content_sha256(edit),
            }], None, profile="fast", photos=[], cfg={}, catalog=catalog,
            policy=normal_rebase.load_policy(), archives=archives,
        )
        journal = stage.parent / "journal.json"
        normal_transaction.publish(
            self.root, stage, [old_relative, edit_relative, *removed], journal=journal,
            bindings={}, profile="fast", run_id="fixture",
        )
        archived = self.root / archives[old_relative]["destination"]
        link = retained_preparation.verify_link(self.root, archived, "photo:image_777")
        self.assertIsNotNone(link)
        self.assertEqual(link["sourceSha256"], metadata.content_sha256(original))
        self.assertIsNone(retained_preparation.verify_link(self.root, old))
        self.assertIn(archived.as_uri(), normal_history.render(self.root))
        normal_transaction.recover(self.root, journal, apply=True)
        self.assertIsNotNone(retained_preparation.verify_link(self.root, old))
        self.assertFalse(archived.exists())

    def test_bound_incoming_replacement_is_not_an_exact_alias(self):
        current = self.photo("Angels/angelica/gallery/angelica_image_777.jpg", b"old native")
        incoming = self.photo("Various/gallery/various_image_777.jpg", b"replacement original")
        catalog = self.empty_catalog()
        catalog["photos"]["photo:image_777"] = {
            "contentSha256": metadata.content_sha256(current), "protected": False,
        }
        rows = self.source_rows()
        current_row = next(row for row in rows if row["group"] == "Angels")
        current_row.update({
            "retainedManifest": "verified-retained-manifest.json",
            "retainedSourceHash": "0" * 64,
        })
        _active, _held, _aliases, updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None,
        )
        selected = updates["photo:image_777"]
        move = {
            "photoId": selected["photoId"], "source": selected["source"],
            "destination": selected["previousSource"], "sha256": selected["sourceHash"],
        }
        self.assertEqual(normal_rebase._exact_alias_targets(rows, [move], updates=updates), {})
        for field, value in (
            ("source", "Various/gallery/unbound_image_777.jpg"),
            ("destination", "Angels/other/gallery/other_image_777.jpg"),
            ("sha256", "0" * 64),
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "bound incoming replacement"):
                normal_rebase._exact_alias_targets(rows, [{**move, field: value}], updates=updates)
        with self.assertRaisesRegex(ValueError, "bound incoming replacement"):
            normal_rebase._exact_alias_targets(
                rows, [move], updates={move["photoId"]: {**selected, "previousHash": "0" * 64}},
            )

    def test_incoming_time_tie_and_true_photo_lock_block_version_choice(self):
        current = self.photo("Angels/angelica/gallery/angelica_image_888.jpg", b"current")
        first = self.photo("Various/gallery/various-a_image_888.jpg", b"replacement-a")
        second = self.photo("Various/gallery/various-b_image_888.jpg", b"replacement-b")
        import os
        stamp = 1_700_000_000_000_000_000
        os.utime(first, ns=(stamp, stamp))
        os.utime(second, ns=(stamp, stamp))
        catalog = self.empty_catalog()
        catalog["photos"]["photo:image_888"] = {
            "contentSha256": metadata.content_sha256(current), "protected": False,
        }
        rows = self.source_rows()
        active, held, _aliases, updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None,
        )
        self.assertEqual(active, [])
        self.assertEqual(updates, {})
        self.assertTrue(all("tie" in row["reason"] for row in held))
        os.utime(second, ns=(stamp + 2_000_000, stamp + 2_000_000))
        catalog["photos"]["photo:image_888"]["protected"] = True
        rows = self.source_rows()
        active, held, _aliases, updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, catalog, None,
        )
        self.assertEqual(active, [])
        self.assertEqual(updates, {})
        self.assertTrue(all("lock" in row["reason"] for row in held))

    def test_short_generated_id_collision_stays_held(self):
        first = self.photo("Various/gallery/first custom.jpg", b"first")
        second = self.photo("Various/gallery/second custom.jpg", b"second")
        with mock.patch.object(originals, "content_id", return_value="deadbeef"):
            rows = self.source_rows()
        self.assertNotEqual(metadata.content_sha256(first), metadata.content_sha256(second))
        active, held, _aliases, _updates, _workflow = normal_rebase._classify_sources(
            self.root, rows, {}, self.empty_catalog(), None,
        )
        self.assertEqual(active, [])
        self.assertEqual(len(held), 2)
        self.assertTrue(all("short content-derived ID collision" in row["reason"] for row in held))

    def test_stable_viewer_gate_requires_only_normal_gallery_overview_review_history(self):
        paths = []
        for name in sorted(normal_rebase.REQUIRED_VIEWERS):
            path = self.root / name
            path.write_text("<html><body>stable page</body></html>", encoding="utf-8")
            paths.append(path)
        self.assertEqual(set(normal_rebase._validate_stable_viewers(paths)), {str(path) for path in paths})
        paths[0].unlink()
        with self.assertRaisesRegex(ValueError, "incomplete"):
            normal_rebase._validate_stable_viewers(paths)

    def test_receipt_binds_lazy_preparation_and_transaction_helpers(self):
        from tools.art import library_backup, likeness
        from tools.art.likeness_library import clean_preparation

        bindings = normal_rebase._bindings(likeness, {}, {"version": "fixture"})
        self.assertEqual(
            bindings["clean_preparation.py"],
            metadata.content_sha256(pathlib.Path(clean_preparation.__file__)),
        )
        self.assertEqual(
            bindings["library_backup.py"],
            metadata.content_sha256(pathlib.Path(library_backup.__file__)),
        )

    def test_receipt_uses_configured_root_local_reports_directory(self):
        default_receipt = normal_rebase._receipt_path(
            self.root, "default", {}, preview=True,
        )
        self.assertEqual(default_receipt, self.root / "_reports" / "runs" / "normal-rebase-default-preview.json")
        receipt = normal_rebase._receipt_path(
            self.root, "fixture", {"storageRoots": {"reports": "run-reports"}},
            preview=True,
        )
        self.assertEqual(
            receipt,
            self.root / "run-reports" / "runs" / "normal-rebase-fixture-preview.json",
        )
        self.assertEqual(
            receipt.relative_to(self.root).parts[:1],
            ("run-reports",),
        )

    def test_apply_requires_matching_preview_receipt_and_bindings(self):
        receipt_path = self.root / "preview.json"
        preview = {
            "kind": "normal-rebase-preview", "schemaVersion": 1, "status": "preview",
            "root": str(self.root), "runId": "fixture", "profile": "lean",
            "implementationSHA256": metadata.content_sha256(
                pathlib.Path(normal_rebase.__file__),
            ),
            "bindings": {"policy": "fixture"}, "plan": {"sourceHashes": {}},
        }
        receipt_path.write_text(json.dumps(preview), encoding="utf-8")
        plan = normal_rebase._preview_for_apply(
            self.root, receipt_path, "fixture", "lean", {"policy": "fixture"},
        )
        self.assertEqual(plan, preview["plan"])
        with self.assertRaisesRegex(ValueError, "run-id/profile"):
            normal_rebase._preview_for_apply(
                self.root, receipt_path, "fixture", "fast", {"policy": "fixture"},
            )

    def test_preparation_workers_are_passed_and_failures_propagate(self):
        source = self.photo("Various/gallery/image_4.jpg", b"fixture")
        row = {"source": source.relative_to(self.root).as_posix()}
        native = self.root / "native.jpg"
        preparation = SimpleNamespace(
            models=SimpleNamespace(offline=contextlib.nullcontext),
            machine_tuning=machine_tuning,
            available_memory_gb=mock.Mock(return_value=12),
            publish=mock.Mock(return_value=0),
            verify=mock.Mock(return_value={"photos": [row]}),
        )
        with mock.patch.dict("sys.modules", {"image_preparation": preparation}), \
                mock.patch("tools.art.likeness_library.clean_preparation.selected_path", return_value=native):
            normal_products.prepare(self.root, self.root / "run", [source], "lean", workers=3)
            self.assertEqual(preparation.publish.call_args.kwargs["workers"], 3)
            preparation.publish.side_effect = OSError("worker failed")
            with self.assertRaisesRegex(OSError, "worker failed"):
                normal_products.prepare(self.root, self.root / "other", [source], "lean", workers=2)
            with self.assertRaisesRegex(ValueError, "workers must be"):
                normal_products.prepare(self.root, self.root / "invalid", [source], "lean", workers=0)
            preparation.available_memory_gb.return_value = 4
            with self.assertRaisesRegex(ValueError, "require at least 7 GiB"):
                normal_products.prepare(self.root, self.root / "low-memory", [source], "lean", workers=2)
            preparation.available_memory_gb.return_value = None
            with self.assertRaisesRegex(ValueError, "observed unavailable"):
                normal_products.prepare(self.root, self.root / "unknown-memory", [source], "lean", workers=2)

    def test_apply_rejects_changed_preparation_worker_request(self):
        api = self.stub_api([])
        with self.assertRaisesRegex(ValueError, "worker request differs from preview"):
            normal_rebase._plan(
                self.root, "lean", "fixture", api=api,
                reuse_plan={"preparationWorkersRequested": 3}, preparation_workers=2,
            )
        self.assertIsNone(normal_rebase._parser().parse_args([]).preparation_workers)
        self.assertEqual(
            normal_rebase._parser().parse_args(["--preparation-workers", "3"]).preparation_workers, 3,
        )

    def test_named_cohesion_flags_red_members_and_registry_round_trips(self):
        from tools.art.likeness_library import named_intake

        def photo(*vector):
            return SimpleNamespace(vec=np.asarray(vector, dtype=float) / np.linalg.norm(vector))

        raw = {f"Prospects/Fia/gallery/fia_image_{i}.jpg": photo(*v)
               for i, v in enumerate(((1, 0, 0), (1, .1, 0), (1, 0, .1), (0, 0, 1)), start=1)}
        active = [{"photoId": f"photo:image_{i}", "source": s} for i, s in enumerate(raw, start=1)]
        report = normal_rebase._named_cohesion({"Fia"}, active, [], raw, normal_rebase.load_policy())
        self.assertEqual(report[0]["identity"], "Prospects/Fia")
        self.assertEqual([row["photoId"] for row in report[0]["possibleMixups"]], ["photo:image_4"])
        self.assertEqual(normal_rebase._named_cohesion(set(), active, [], raw, normal_rebase.load_policy()), [])
        cfg = {}
        named_intake.record(self.root, cfg, [{"source": "Various/Fia", "destination": "Potentials/Fia",
                                              "photos": [1, 2]}])
        named_intake.record(self.root, cfg, [{"source": "Various/Fia", "destination": "Prospects/Fia",
                                              "photos": [3]}])
        identities = named_intake.load(self.root, cfg)
        self.assertEqual((identities["Fia"]["photoCount"], identities["Fia"]["folder"]), (3, "Prospects/Fia"))
        self.assertEqual(named_intake.named_folders(identities, ["Prospects/Fia", "Prospects/Gwen"]), {"Prospects/Fia"})

    def test_moved_workflow_photo_proposes_best_remaining_gallery_photo(self):
        def photo(*vector):
            return SimpleNamespace(vec=np.asarray(vector, dtype=float) / np.linalg.norm(vector))

        raw = {
            "Angels/A/gallery/a_image_1.jpg": photo(1, 0, 0),
            "Angels/A/gallery/a_image_2.jpg": photo(1, .1, 0),
            "Angels/A/gallery/a_image_3.jpg": photo(1, .6, 0),
            "Various/gallery/x_image_4.jpg": photo(0, 1, 0),
        }
        active = [{"photoId": f"photo:image_{index}", "source": source}
                  for index, source in enumerate(raw, start=1)]
        moves = [{"photoId": "photo:image_1", "source": "Angels/A/gallery/a_image_1.jpg",
                  "destination": "Potentials/P/review/p_image_1.jpg"}]
        proposals = normal_rebase._workflow_replacement_proposals(
            {"photo:image_1", "photo:image_4"}, active, moves, raw,
        )
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0]["identity"], "Angels/A")
        self.assertEqual(proposals[0]["replacement"]["photoId"], "photo:image_2")
        self.assertFalse(proposals[0]["configurationChanged"])
        renamed = [{**moves[0], "destination": "Angels/A/gallery/a_image_1_new.jpg"}]
        self.assertEqual(normal_rebase._workflow_replacement_proposals({"photo:image_1"}, active, renamed, raw), [])

    def test_unrequested_workers_follow_preview_or_this_machine(self):
        api = self.stub_api([])
        seen = []

        def stop(*args, **kwargs):
            seen.append(args[0])
            raise RuntimeError("stop after worker resolution")

        with mock.patch.object(normal_products, "validate_workers", side_effect=stop), \
                mock.patch.object(normal_products, "default_workers", return_value=(6, "machine capacity")):
            for reuse_plan in ({"preparationWorkersRequested": 3}, None):
                with self.subTest(reuse_plan=reuse_plan), self.assertRaisesRegex(RuntimeError, "stop after"):
                    normal_rebase._plan(self.root, "lean", "fixture", api=api, reuse_plan=reuse_plan)
        self.assertEqual(seen, [3, 6])

    def test_preview_apply_and_recovery_bind_pool_dispositions(self):
        from tools.art import likeness

        proof = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="p")
        self.addCleanup(proof.cleanup)
        self.root = (pathlib.Path(proof.name) / "Sovereign Territories Sandbox" / "Working"
                     / "_sandbox-state" / "normal-flow-proof-p")
        keeper = self.photo("Prospects/Owner/gallery/owner_image_921.jpg", b"prepared keeper")
        evidence = self.retain_original(keeper, b"shared")
        copy = self.photo("Various/gallery/image_922.jpg", b"shared")
        unusable = self.photo("Various/gallery/image_923.jpg", b"no face")
        metadata.save_catalog(self.empty_catalog(), self.root / ".likeness-library.json")
        run = self.root / "_reports" / "runs" / "normal-rebase-p"
        preview = run.with_name(run.name + "-preview.json")
        applied = run.with_suffix(".json")
        args = ["--root", str(self.root), "--cache", str(self.root / "fixture-cache.json"),
                "--profile", "fast", "--run-id", "p"]

        def measure(_api, _cache, _embedder, path, **_kwargs):
            return hashlib.sha1(path.read_bytes()).hexdigest(), {"faces": 0, "t": 0.5}

        def viewers(*_args, **_kwargs):
            report_dir = self.root / "_reports" / "library"
            report_dir.mkdir(parents=True, exist_ok=True)
            for name in normal_rebase.REQUIRED_VIEWERS:
                (report_dir / name).write_text("<html>fixture</html>", encoding="utf-8")
            return [str(report_dir / name) for name in normal_rebase.REQUIRED_VIEWERS]

        with (
            mock.patch.object(likeness, "configuration", return_value={}),
            mock.patch.object(likeness, "Embedder"),
            mock.patch.object(normal_rebase, "_infer", side_effect=measure),
            mock.patch.object(normal_rebase.normal_finish, "viewers", side_effect=viewers),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()) as errors,
        ):
            self.assertEqual(normal_rebase.main([*args, "--dry-run"]), 0, errors.getvalue())
            preview_bytes = preview.read_bytes()
            plan = json.loads(preview_bytes)["plan"]
            archive, = plan["duplicateArchives"].values()
            junk, = plan["junkDispositions"].values()
            self.assertEqual(archive["selectedSource"], keeper.relative_to(self.root).as_posix())
            self.assertEqual(archive["retainedOriginalProof"]["path"], evidence["original"])
            self.assertEqual(junk["destination"], "_junk/Various/gallery/image_923.jpg")
            self.assertTrue(all(path.is_file() for path in (keeper, copy, unusable)))
            self.assertEqual(normal_rebase.main([*args, "--apply", "--sandbox-apply-draft"]), 0, errors.getvalue())
            self.assertEqual(normal_rebase.main([*args, "--check"]), 0, errors.getvalue())
            self.assertEqual(normal_rebase.main([*args, "--repeat"]), 0, errors.getvalue())
            self.assertEqual(preview.read_bytes(), preview_bytes)
            recap = normal_rebase.normal_recap.collect(applied)
            self.assertEqual(recap["physicalSources"], 3)
            self.assertEqual(recap["physicalDestinations"], 3)
            page = normal_rebase.normal_recap.render(recap, self.root / "recap.html")
            self.assertIn("Verified retained original", page)
            saved = json.loads(applied.read_bytes())
            entry, = saved["plan"]["duplicateArchives"].values()
            entry["retainedOriginalProof"]["path"] = "_processing/unrelated.jpg"
            tampered = applied.with_name("tampered.json")
            tampered.write_text(json.dumps(saved), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unbound duplicate archive evidence"):
                normal_rebase.normal_recap.collect(tampered)
            self.assertEqual(keeper.read_bytes(), b"prepared keeper")
            self.assertFalse(copy.exists())
            self.assertFalse(unusable.exists())
            self.assertEqual((self.root / archive["destination"]).read_bytes(), b"shared")
            self.assertEqual((self.root / junk["destination"]).read_bytes(), b"no face")
            self.assertEqual(normal_rebase.main([*args, "--recover-apply"]), 0, errors.getvalue())
            self.assertEqual(copy.read_bytes(), b"shared")
            self.assertEqual(unusable.read_bytes(), b"no face")

    def test_apply_accepts_new_preview_bound_to_external_verified_preparation(self):
        receipt_path = self.root / "preview-with-reused-preparation.json"
        preparation_root = (
            self.root / "_reports" / "runs" / "normal-rebase-prior-preview"
            / "preparation" / "inputs" / "_reports" / "preparation" / "selected"
        )
        reuse = {
            "kind": "verified-existing-selected-preparation",
            "path": str(preparation_root),
            "manifestSHA256": "a" * 64,
            "profile": "lean",
        }
        plan = {
            "preparationRoot": str(preparation_root),
            "preparationManifestSHA256": "a" * 64,
            "preparationReuse": reuse,
        }
        preview = {
            "kind": "normal-rebase-preview", "schemaVersion": 1, "status": "preview",
            "root": str(self.root), "runId": "new-run", "profile": "lean",
            "implementationSHA256": metadata.content_sha256(pathlib.Path(normal_rebase.__file__)),
            "bindings": {"policy": "current"}, "plan": plan,
        }
        receipt_path.write_text(json.dumps(preview), encoding="utf-8")
        self.assertEqual(
            normal_rebase._preview_for_apply(
                self.root, receipt_path, "new-run", "lean", {"policy": "current"},
            ),
            plan,
        )
        plan["preparationReuse"]["manifestSHA256"] = "b" * 64
        receipt_path.write_text(json.dumps(preview), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "reused preparation binding"):
            normal_rebase._preview_for_apply(
                self.root, receipt_path, "new-run", "lean", {"policy": "current"},
            )

    def test_apply_accepts_relocated_preparation_generation_seal_at_its_original_path(self):
        receipt_path = self.root / "preview-with-relocated-preparation.json"
        tail = ("_reports", "runs", "normal-rebase-prior-preview", "preparation", "inputs",
                "_reports", "preparation", "selected")
        preparation_root = self.root.joinpath(*tail)
        original = pathlib.Path(self.temp.name) / "main" / "Working"
        relocation = {"originalRoot": str(original),
                      "originalPreparationRoot": str(original.joinpath(*tail)),
                      "originalMirror": str(original.joinpath(*tail[:5]))}
        generation = {"preparationRoot": str(original.joinpath(*tail)), "manifestSHA256": "a" * 64,
                      "profile": "lean", "producerUnchangedDuringGeneration": True}
        plan = {
            "preparationRoot": str(preparation_root), "preparationManifestSHA256": "a" * 64,
            "preparationReuse": {"kind": "verified-existing-selected-preparation", "path": str(preparation_root),
                                 "manifestSHA256": "a" * 64, "profile": "lean", "relocatedFrom": relocation},
            "preparationGeneration": generation,
        }
        preview = {
            "kind": "normal-rebase-preview", "schemaVersion": 1, "status": "preview",
            "root": str(self.root), "runId": "new-run", "profile": "lean",
            "implementationSHA256": metadata.content_sha256(pathlib.Path(normal_rebase.__file__)),
            "bindings": {"policy": "current"}, "plan": plan,
        }
        receipt_path.write_text(json.dumps(preview), encoding="utf-8")
        self.assertEqual(normal_rebase._preview_for_apply(
            self.root, receipt_path, "new-run", "lean", {"policy": "current"}), plan)
        del plan["preparationReuse"]["relocatedFrom"]
        receipt_path.write_text(json.dumps(preview), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "generation seal is incomplete"):
            normal_rebase._preview_for_apply(self.root, receipt_path, "new-run", "lean", {"policy": "current"})

    def test_apply_preparation_reuse_verifies_exact_source_set_and_profile(self):
        source = self.photo("Prospects/Owner/gallery/owner_image_130.jpg", b"raw source")
        output = (
            self.root / "_reports" / "runs" / "preview" / "preparation" / "inputs"
            / "_reports" / "preparation" / "selected"
        )
        output.mkdir(parents=True)
        manifest = output / "manifest.json"
        manifest.write_text("fixture manifest", encoding="utf-8")
        native = output / "native.jpg"
        native.write_bytes(b"prepared native")
        relative = source.relative_to(self.root).as_posix()
        row = {"source": relative, "sourceSha256": metadata.content_sha256(source)}
        fake_module = SimpleNamespace(verify=mock.Mock(return_value={
            "storageMode": "lean", "photos": [row],
        }))
        with mock.patch.dict("sys.modules", {"image_preparation": fake_module}), \
                mock.patch(
                    "tools.art.likeness_library.clean_preparation.selected_path",
                    return_value=native,
                ):
            prepared = normal_products.reuse_prepared(
                self.root, output, [source], "lean", metadata.content_sha256(manifest),
            )
        self.assertEqual(prepared[0], output)
        self.assertEqual(prepared[2], {relative: native})
        fake_module.verify.assert_called_once_with(output.parents[2], output)

        fake_module.verify.return_value = {
            "storageMode": "lean",
            "photos": [{"source": relative, "sourceSha256": "stale-source-hash"}],
        }
        with mock.patch.dict("sys.modules", {"image_preparation": fake_module}), \
                mock.patch(
                    "tools.art.likeness_library.clean_preparation.selected_path",
                    return_value=native,
                ), self.assertRaisesRegex(ValueError, "exact current selected source set"):
            normal_products.reuse_prepared(
                self.root, output, [source], "lean", metadata.content_sha256(manifest),
            )

    def test_subset_reuse_verifies_unused_sources_and_filters_selected_natives(self):
        selected = self.photo("Various/gallery/various_image_901.jpg", b"selected")
        unused = self.photo("Various/gallery/various_image_902.jpg", b"now held by classification")
        output = self.root / "_reports" / "preparation" / "selected"
        output.mkdir(parents=True)
        manifest = output / "manifest.json"
        manifest.write_text("unchanged parent preparation", encoding="utf-8")
        manifest_hash = metadata.content_sha256(manifest)
        native = output / "native.jpg"
        native.write_bytes(b"prepared native")
        data = {"storageMode": "lean", "photos": [
            {"source": path.relative_to(self.root).as_posix(), "sourceSha256": metadata.content_sha256(path)}
            for path in (selected, unused)
        ]}
        fake_module = SimpleNamespace(verify=mock.Mock(return_value=data))
        with mock.patch.dict("sys.modules", {"image_preparation": fake_module}), \
                mock.patch(
                    "tools.art.likeness_library.clean_preparation.selected_path",
                    return_value=native,
                ):
            with self.assertRaisesRegex(ValueError, "exact current selected source set"):
                normal_products.reuse_prepared(self.root, output, [selected], "lean", manifest_hash)
            prepared = normal_products.reuse_prepared(
                self.root, output, [selected], "lean", manifest_hash, allow_subset=True,
            )
            self.assertEqual(set(prepared[2]), {selected.relative_to(self.root).as_posix()})
            self.assertEqual(prepared[1]["photos"], data["photos"])
            self.assertEqual(prepared[1]["reuseSourceAliases"], {})
            self.assertEqual(metadata.content_sha256(manifest), manifest_hash)
            alias = self.photo("Various/gallery/copy_image_901.jpg", selected.read_bytes())
            aliased = normal_products.reuse_prepared(
                self.root, output, [alias], "lean", manifest_hash, allow_subset=True,
            )
            alias_source = alias.relative_to(self.root).as_posix()
            self.assertEqual(aliased[2], {alias_source: native})
            self.assertEqual(aliased[1]["reuseSourceAliases"], {
                alias_source: {
                    "preparedSource": selected.relative_to(self.root).as_posix(),
                    "sourceSha256": metadata.content_sha256(alias),
                },
            })
            self.assertEqual(aliased[1]["photos"], data["photos"])
            missing = self.photo("Various/gallery/various_image_903.jpg", b"not prepared")
            with self.assertRaisesRegex(ValueError, "does not cover"):
                normal_products.reuse_prepared(
                    self.root, output, [missing], "lean", manifest_hash, allow_subset=True,
                )
            unused.write_bytes(b"edited unused original")
            with self.assertRaisesRegex(ValueError, "source changed"):
                normal_products.reuse_prepared(
                    self.root, output, [selected], "lean", manifest_hash, allow_subset=True,
                )

    def test_missing_intake_viewer_is_truthful_for_fast_and_preserves_existing_history(self):
        from tools.workflows import comfy_workflows

        with mock.patch.object(
            comfy_workflows, "storage_root",
            side_effect=lambda _cfg, _kind, root: pathlib.Path(root) / "reports",
        ):
            path = normal_rebase._ensure_intake_viewer(self.root, {}, "fast", None)
            text = path.read_text(encoding="utf-8")
            self.assertIn("FAST used original-byte matching", text)
            self.assertIn("deferred", text)
            self.assertNotIn("experimental", text.casefold())
            original = b"existing run history"
            path.write_bytes(original)
            self.assertEqual(normal_rebase._ensure_intake_viewer(self.root, {}, "lean", None), path)
            self.assertEqual(path.read_bytes(), original)

    def test_fixture_cli_default_is_preview_and_writes_a_hash_bound_receipt(self):
        from tools.art import likeness
        from tools.workflows import comfy_workflows

        receipt = self.root / "reports" / "runs" / "fixture-preview.json"
        report = {
            "sourceRowCount": 1, "coreCount": 1, "moves": [],
            "heldCount": 0, "bindings": {"fixture": "sha256"},
            "sourceRows": [{
                "source": "Various/gallery/various_image_123.jpg",
                "sourceHash": "0" * 64, "photoId": "photo:image_123",
            }],
            "sourceHashes": {"Various/gallery/various_image_123.jpg": "0" * 64},
        }
        fake_plan = (
            report, [], None, self.empty_catalog(), {}, {"version": "fixture"},
            None, None, self.root / "reports" / "runs" / "fixture", [],
        )
        with mock.patch.object(likeness, "configuration", return_value={}), \
                mock.patch.object(comfy_workflows, "work_root", return_value=self.root), \
                mock.patch.object(
                    comfy_workflows, "storage_root",
                    side_effect=lambda _cfg, _kind, root: pathlib.Path(root) / "reports",
                ), \
                mock.patch.object(normal_rebase, "_plan", return_value=fake_plan), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            result = normal_rebase.main([
                "--root", str(self.root), "--profile", "fast",
                "--run-id", "fixture", "--receipt", str(receipt),
            ])
        self.assertEqual(result, 0)
        saved = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "preview")
        self.assertEqual(saved["plan"]["sourceRowCount"], 1)
        self.assertTrue(saved["implementationSHA256"])
        self.assertIn("preview only", output.getvalue())

    def test_apply_publishes_local_catalogue_and_undo_preserves_fallback(self):
        from tools.art import likeness
        from tools.workflows import comfy_workflows

        policy = normal_rebase.load_policy()
        for has_local, report_fails in ((False, False), (True, False), (False, True)):
            with self.subTest(has_local=has_local, report_fails=report_fails):
                root = self.root / f"{has_local}-{report_fails}"
                source = root / "Various" / "gallery" / "various_image_912.jpg"
                source.parent.mkdir(parents=True)
                source.write_bytes(b"selected original")
                catalog = self.empty_catalog()
                fallback = self.root / f"fallback-{has_local}-{report_fails}.json"
                fallback.write_text(json.dumps(catalog, indent=3), encoding="utf-8")
                fallback_bytes = fallback.read_bytes()
                local = root / ".likeness-library.json"
                if has_local:
                    local.write_bytes(fallback_bytes)
                relative = source.relative_to(root).as_posix()
                move = {
                    "photoId": "photo:image_912", "source": relative,
                    "destination": "Various/review/various_image_912.jpg",
                    "sha256": metadata.content_sha256(source), "reason": "review",
                }
                report = {
                    "sourceRowCount": 1, "bindings": {}, "moves": [move],
                    "phaseLog": [{"phase": "final-rival-family-viewer-publication", "status": "apply-only"}],
                    "sourceHashes": {relative: move["sha256"]},
                    "incomingUpdates": {}, "exactAliasTargets": {},
                    "emptiedIdentityRetirement": {"retiredRoot": "_retired", "folders": []},
                    "sourceRows": [{
                        "source": relative, "sourceHash": move["sha256"],
                        "photoId": move["photoId"],
                    }],
                }
                cache = SimpleNamespace(stat={}, save=lambda: None)
                run = root / "reports" / "runs" / "normal-rebase-catalogue-proof"
                plan = (
                    report, [SimpleNamespace(path=source, name=source.name)],
                    None, catalog, {}, policy, cache, None, run, [],
                )

                def viewers(*_args, **_kwargs):
                    self.assertEqual(report["phaseLog"][-1]["status"], "apply-only")
                    self.assertNotIn("durationSeconds", report["phaseLog"][-1])
                    folder = root / "reports" / "library"
                    folder.mkdir(parents=True, exist_ok=True)
                    for name in normal_rebase.REQUIRED_VIEWERS:
                        (folder / name).write_text("<html>fixture</html>", encoding="utf-8")
                    return [str(folder / name) for name in normal_rebase.REQUIRED_VIEWERS]

                with (
                    mock.patch.object(metadata, "CATALOG_PATH", fallback),
                    mock.patch.object(likeness, "configuration", return_value={}),
                    mock.patch.object(comfy_workflows, "load_cfg", return_value={}),
                    mock.patch.object(
                        comfy_workflows, "storage_root",
                        side_effect=lambda _cfg, _kind, root: pathlib.Path(root) / "reports",
                    ),
                    mock.patch.object(normal_rebase, "is_sandbox_working_path", return_value=True),
                    mock.patch.object(normal_rebase.maintenance, "require_authorization"),
                    mock.patch.object(normal_rebase, "_bindings", return_value={}),
                    mock.patch.object(normal_rebase, "_preview_for_apply", return_value={}),
                    mock.patch.object(normal_rebase, "_plan", return_value=plan),
                    mock.patch.object(normal_rebase.normal_finish, "projected", return_value=None),
                    mock.patch.object(normal_rebase.normal_finish, "family_and_final", return_value={}),
                    mock.patch.object(normal_rebase.normal_finish, "viewers", side_effect=viewers),
                    mock.patch.object(
                        normal_rebase.normal_recap, "publish",
                        wraps=normal_rebase.normal_recap.publish,
                        side_effect=OSError("report disk failure") if report_fails else None,
                    ),
                    contextlib.redirect_stdout(io.StringIO()),
                    contextlib.redirect_stderr(io.StringIO()) as errors,
                ):
                    result = normal_rebase.main([
                        "--root", str(root), "--profile", "fast",
                        "--run-id", "catalogue-proof", "--apply", "--sandbox-apply-draft",
                    ])
                self.assertEqual(result, int(report_fails), errors.getvalue())
                receipt = root / "reports" / "runs" / "normal-rebase-catalogue-proof.json"
                saved_phase = json.loads(receipt.read_text(encoding="utf-8"))["plan"]["phaseLog"][-1]
                self.assertEqual(saved_phase["status"], "complete")
                self.assertGreaterEqual(saved_phase["durationSeconds"], 0)
                self.assertIn("excludes receipt and recap", saved_phase["timingScope"])
                if report_fails:
                    self.assertIn("applied receipt saved", errors.getvalue())
                    self.assertIn("do not repeat publication", errors.getvalue())
                    receipt = root / "reports" / "runs" / "normal-rebase-catalogue-proof.json"
                    self.assertEqual(json.loads(receipt.read_text(encoding="utf-8"))["status"], "applied")
                self.assertTrue(local.is_file())
                self.assertEqual(fallback.read_bytes(), fallback_bytes)
                journal = run / "publication-journal.json"
                normal_rebase.normal_transaction.verify(root, journal)
                normal_rebase.normal_transaction.recover(root, journal, apply=True)
                self.assertEqual(source.read_bytes(), b"selected original")
                self.assertEqual(local.exists(), has_local)
                if has_local:
                    self.assertEqual(local.read_bytes(), fallback_bytes)
                self.assertEqual(fallback.read_bytes(), fallback_bytes)

    def test_fast_composition_uses_one_frozen_audit_and_separates_physical_from_logical_counts(self):
        core = self.photo("Prospects/Owner/gallery/owner_image_911.jpg", b"core")
        candidate = self.photo("Various/gallery/various_image_912.jpg", b"candidate")
        folders = [
            ("Prospects", "Owner", self.root / "Prospects" / "Owner"),
            ("Various", "Various", self.root / "Various"),
        ]
        api = self.stub_api(folders)
        catalog = self.empty_catalog()
        catalog_path = self.root / ".likeness-library.json"
        catalog_path.write_text("{}", encoding="utf-8")
        core_id = metadata.photo_id_from_name(core.name)
        fake_policy = {"version": "fixture", "status": "approved"}
        core_record = {
            "vector": np.array([1.0, 0.0]), "side": "Prospects",
            "category": "Prospects", "personIds": [], "identityProtected": False,
            "mode": "fixture", "corePhotoIds": [core_id], "photoScores": {core.name: 1.0},
        }
        with mock.patch.object(metadata, "load_catalog", return_value=catalog), \
                mock.patch.object(metadata, "path_for_root", return_value=catalog_path), \
                mock.patch.object(normal_rebase, "load_policy", return_value=fake_policy), \
                mock.patch.object(normal_rebase, "effective_settings", return_value={"minFace": 1}), \
                mock.patch.object(normal_rebase, "_fragment_evidence", return_value={
                    "activation": "diagnostic-only", "candidateLinks": [], "comparisons": [],
                }), \
                mock.patch.object(normal_rebase, "_infer", side_effect=lambda _api, _cache, _embedder, path, **_kwargs: (
                    hashlib.sha1(pathlib.Path(path).read_bytes()).hexdigest(),
                    {"v": [1.0, 0.0], "faces": 1, "px": 100, "t": "fixture"},
                )), \
                mock.patch.object(
                    normal_rebase.reconciliation, "frozen_identity_cores",
                    return_value=({"Prospects/Owner": core_record}, set(), []),
                ), \
                mock.patch.object(
                    normal_rebase.normal_import, "_route_plan",
                    side_effect=lambda *_args: {"assignments": [], "held": [], "clusters": []},
                ) as route, \
                mock.patch.object(normal_rebase.normal_products, "prepare", side_effect=AssertionError("FAST must defer preparation")), \
                mock.patch.object(normal_rebase.maintenance, "proposed_moves", return_value=[]), \
                mock.patch.object(
                    normal_rebase.normal_finish, "check_batch",
                    return_value=([], {"passCount": 1, "frozenRivals": {}, "corrections": []}),
                ) as audit, \
                mock.patch.object(normal_rebase, "_bindings", return_value={"fixture": "bound"}):
            result = normal_rebase._plan(
                self.root, "fast", "fixture-run", api=api,
            )
        report = result[0]
        self.assertEqual(report["sourceRowCount"], 2)
        self.assertEqual(report["primaryPhysicalPhotoRows"], 2)
        self.assertEqual(report["distinctPrimaryContentSHA256Count"], 2)
        self.assertEqual(report["uniqueLogicalPhotoIdCount"], 2)
        self.assertEqual(report["sourceConservation"]["physicalRows"], 2)
        self.assertEqual(report["phaseLog"][2]["status"], "deferred")
        self.assertNotIn("durationSeconds", report["phaseLog"][2])
        self.assertEqual(report["phaseLog"][-1]["status"], "apply-only")
        self.assertNotIn("durationSeconds", report["phaseLog"][-1])
        self.assertEqual(report["frozenConsistencyCheck"]["passCount"], 1)
        self.assertEqual(report["fragmentQualification"]["activation"], "diagnostic-only")
        route.assert_called_once()
        audit.assert_called_once()

    def test_lean_prepares_named_references_and_candidates_before_core_measurement(self):
        self._check_lean_preparation("Various/gallery/various_image_922.jpg")

    def test_prepared_same_path_review_admission_stages_native_and_lineage(self):
        self._check_lean_preparation(
            "Prospects/Owner/review/owner_image_922.jpg", membership_only=True,
        )

    def _check_lean_preparation(self, candidate_source, *, membership_only=False):
        core = self.photo("Prospects/Owner/gallery/owner_image_921.jpg", b"core")
        candidate = self.photo(candidate_source, b"candidate")
        folders = [
            ("Prospects", "Owner", self.root / "Prospects" / "Owner"),
            ("Various", "Various", self.root / "Various"),
        ]
        api = self.stub_api(folders)
        catalog = self.empty_catalog()
        catalog_path = self.root / ".likeness-library.json"
        catalog_path.write_text("{}", encoding="utf-8")
        core_id = metadata.photo_id_from_name(core.name)
        candidate_id = metadata.photo_id_from_name(candidate.name)
        catalog["photos"][candidate_id] = {
            "contentSha256": metadata.content_sha256(candidate),
            "rejectedPersonIds": ["person:explicit-rejection"],
        }
        core_record = {
            "vector": np.array([1.0, 0.0]), "side": "Prospects",
            "category": "Prospects", "personIds": [], "identityProtected": False,
            "mode": "fixture", "corePhotoIds": [core_id], "photoScores": {core.name: 1.0},
        }
        prepared_root = self.root / "reports" / "runs" / "prep"
        (prepared_root / "manifest.json").parent.mkdir(parents=True, exist_ok=True)
        (prepared_root / "manifest.json").write_text("{}", encoding="utf-8")
        core_native = prepared_root / "core-native.jpg"
        core_native.write_bytes(b"prepared core")
        prepared_native = self.root / "reports" / "runs" / "prep" / "candidate-native.jpg"
        prepared_native.write_bytes(b"prepared candidate")
        candidate_relative = candidate.relative_to(self.root).as_posix()
        core_relative = core.relative_to(self.root).as_posix()
        prep_result = (
            prepared_root, {"recipe": {"id": "fixture"}, "photos": [
                {"source": candidate_relative},
            ]},
            {core_relative: core_native, candidate_relative: prepared_native},
        )
        inferred_paths, measured_references = [], {}

        def infer(_api, _cache, _embedder, path, **_kwargs):
            path = pathlib.Path(path)
            inferred_paths.append(path)
            return metadata.content_sha256(path), {
                "v": [1.0, 0.0] if path == core_native else [0.0, 1.0],
                "faces": 1, "px": 100, "t": "fixture",
            }

        def frozen_cores(space, *_args, **_kwargs):
            measured_references["photos"] = [
                (photo.path, photo.vec.tolist()) for photo in space.photos
            ]
            return {"Prospects/Owner": core_record}, set(), []

        generation_seal = {
            "kind": "normal-rebase-preparation-origin-complete",
            "preparationRoot": str(prepared_root),
            "manifestSHA256": metadata.content_sha256(prepared_root / "manifest.json"),
            "profile": "lean",
            "generationProducerSHA256": "c" * 64,
            "producerAfterGenerationSHA256": "c" * 64,
            "producerUnchangedDuringGeneration": True,
        }

        def prepare_with_origin(_root, _cfg, _run, profile, paths, *, workers):
            self.assertEqual(api.domains.CURRENT.get(), "general")
            self.assertTrue(api.domains.READ_ONLY.get())
            self.assertEqual(profile, "lean")
            self.assertEqual(workers, 1)
            self.assertEqual(paths, [core, candidate])
            return prep_result, generation_seal

        def reuse_selected(*_args, **_kwargs):
            self.assertEqual(api.domains.CURRENT.get(), "general")
            self.assertTrue(api.domains.READ_ONLY.get())
            return prep_result

        fake_policy = {"version": "fixture", "status": "approved"}
        with mock.patch.object(metadata, "load_catalog", return_value=catalog), \
                mock.patch.object(metadata, "path_for_root", return_value=catalog_path), \
                mock.patch.object(normal_rebase, "load_policy", return_value=fake_policy), \
                mock.patch.object(normal_rebase, "effective_settings", return_value={"minFace": 1}), \
                mock.patch.object(normal_rebase, "_fragment_evidence", return_value={
                    "activation": "diagnostic-only", "candidateLinks": [], "comparisons": [],
                }), \
                mock.patch.object(normal_rebase, "_infer", side_effect=infer), \
                mock.patch.object(
                    normal_rebase.reconciliation, "frozen_identity_cores",
                    side_effect=frozen_cores,
                ), \
                mock.patch.object(
                    normal_rebase.normal_import, "_route_plan",
                    side_effect=lambda *_args: {"assignments": [], "held": [], "clusters": []},
                ) as route, \
                mock.patch.object(
                    normal_rebase, "_prepare_with_origin", side_effect=prepare_with_origin,
                ) as prepare, \
                mock.patch.object(normal_rebase.maintenance, "proposed_moves", side_effect=lambda *_args: [{
                    "photoId": candidate_id, "source": candidate_relative,
                    "destination": candidate_relative, "sha256": metadata.content_sha256(candidate),
                    "membershipOnly": True, "preparationOnly": True,
                    "reason": "same-owner provisional Review admission",
                }] if membership_only else []), \
                mock.patch.object(
                    normal_rebase.normal_finish, "check_batch",
                    side_effect=lambda _api, _space, _catalog, _policy, moves, **_kwargs: (
                        list(moves), {"passCount": 1, "frozenRivals": {}, "corrections": []},
                    ),
                ) as audit, \
                mock.patch.object(normal_rebase, "_bindings", return_value={"fixture": "bound"}):
            report, _photos, *_rest = normal_rebase._plan(
                self.root, "lean", "fixture-lean", api=api,
            )
            reuse_plan = {
                "sourceHashes": report["sourceHashes"],
                "catalogueSHA256": report["catalogueSHA256"],
                "preparationRoot": report["preparationRoot"],
                "preparationManifestSHA256": report["preparationManifestSHA256"],
                "preparationGeneration": report["preparationGeneration"],
                "emptiedIdentityFingerprint": report["emptiedIdentityFingerprint"],
            }
            reuse_binding = {
                "kind": "verified-existing-selected-preparation",
                "path": str(prepared_root),
                "manifestSHA256": metadata.content_sha256(prepared_root / "manifest.json"),
                "profile": "lean", "inputCount": 2,
                "generationSeal": generation_seal,
            }
            with mock.patch.object(
                normal_rebase.normal_products, "prepare",
                side_effect=AssertionError("reused preparation must not be rerun"),
            ) as reuse_prepare, mock.patch.object(
                normal_rebase.normal_products, "reuse_prepared",
                side_effect=reuse_selected,
            ) as reuse, mock.patch.object(
                normal_rebase, "_validate_preparation_reuse",
                return_value=reuse_binding,
            ) as validate_reuse:
                applied_plan, *_rest = normal_rebase._plan(
                    self.root, "lean", "fixture-lean", api=api, for_apply=True,
                    reuse_plan=reuse_plan,
                )
                reused_preview, *_rest = normal_rebase._plan(
                    self.root, "lean", "fixture-reuse", api=api,
                    reuse_preparation=prepared_root,
                    reuse_preparation_sha256=reuse_binding["manifestSHA256"],
                )
        self.assertEqual(report["profileMatchingPolicy"], "shared frozen-core and candidate rules")
        for item in report["phaseLog"][:-1]:
            self.assertGreaterEqual(item["durationSeconds"], 0)
        self.assertEqual(report["phaseLog"][-1]["status"], "apply-only")
        self.assertNotIn("durationSeconds", report["phaseLog"][-1])
        self.assertEqual(report["phaseLog"][2]["timingScope"], "current preparation and verification")
        self.assertEqual(applied_plan["phaseLog"][2]["timingScope"], "current reuse verification")
        self.assertEqual(reused_preview["phaseLog"][2]["timingScope"], "current reuse verification")
        self.assertIn("accepted native recipe", report["preparation"])
        self.assertEqual(report["sourceRowCount"], 2)
        self.assertEqual(report["preparedReferenceCount"], 1)
        self.assertEqual(report["preparedCandidateCount"], 1)
        self.assertFalse(report["preparationReusedFromPreview"])
        prepare.assert_called_once()
        self.assertEqual(report["preparationGeneration"], generation_seal)
        self.assertEqual(inferred_paths[:2], [core_native, prepared_native])
        self.assertEqual(len(inferred_paths), 6)
        self.assertEqual(measured_references["photos"][0][0], core)
        np.testing.assert_allclose(
            measured_references["photos"][0][1],
            [2 ** -0.5, -(2 ** -0.5)],
        )
        candidate_plan = route.call_args_list[0].args[1][0]
        self.assertEqual(candidate_plan["rejectedPersonIds"], ["person:explicit-rejection"])
        self.assertFalse(candidate_plan.get("rejectionMetadataStale"))
        np.testing.assert_allclose(
            candidate_plan["vector"].tolist(), [-(2 ** -0.5), 2 ** -0.5],
        )
        self.assertEqual(
            {row["photoId"] for row in report["moves"] if row.get("preparationOnly")},
            {"photo:image_921", "photo:image_922"},
        )
        self.assertEqual(applied_plan["preparationManifestSHA256"], report["preparationManifestSHA256"])
        self.assertTrue(applied_plan["preparationReusedFromPreview"])
        self.assertEqual(reuse.call_args.args[2], [core, candidate])
        self.assertEqual(reuse.call_count, 2)
        self.assertEqual(reuse_prepare.call_count, 0)
        self.assertEqual(validate_reuse.call_count, 2)
        self.assertEqual(reused_preview["preparationReuse"], reuse_binding)
        self.assertEqual(reused_preview["preparationManifestSHA256"], reuse_binding["manifestSHA256"])
        self.assertEqual(reused_preview["preparationGeneration"], generation_seal)
        self.assertEqual(route.call_count, 3)
        self.assertEqual(audit.call_count, 3)
        if membership_only:
            from tools.art.likeness_library import derivatives, maintenance, normal_history, retained_preparation

            move = next(row for row in report["moves"] if row["photoId"] == candidate_id)
            self.assertNotIn("membershipOnly", move)
            stage = self.root / "reports" / "runs" / "publication-proof"
            with mock.patch.object(retained_preparation, "stage_photo") as retain, \
                    mock.patch.object(normal_history, "stage") as history, \
                    mock.patch.object(maintenance, "_updated_catalog", return_value=self.empty_catalog()), \
                    mock.patch.object(derivatives, "maintain", return_value=([], [])), \
                    mock.patch.object(derivatives, "verified", side_effect=ValueError("fixture framing unavailable")), \
                    mock.patch.object(derivatives, "expected_unavailability", return_value="fixture framing unavailable"):
                published, _updated, _removed = normal_products.stage(
                    self.root, stage, [move], prep_result, profile="lean",
                    photos=[self.stub_api([]).Photo(
                        candidate, "Prospects", "Owner", "fixture",
                        {"v": [0.0, 1.0], "faces": 1, "px": 100},
                    )],
                    cfg={}, catalog=catalog, policy=fake_policy,
                )
            self.assertEqual((stage / candidate_relative).read_bytes(), prepared_native.read_bytes())
            self.assertEqual(published[0]["sha256"], metadata.content_sha256(prepared_native))
            retain.assert_called_once()
            self.assertEqual(history.call_args.args[2][0]["source"], candidate_relative)
            self.assertNotIn("membershipOnly", history.call_args.args[2][0])
            self.assertEqual(candidate.read_bytes(), b"candidate")

    def test_verified_retained_noncore_native_is_held_without_repreparation(self):
        core = self.photo("Prospects/Owner/gallery/owner_image_931.jpg", b"core")
        candidate = self.photo("Various/gallery/various_image_932.jpg", b"prepared native")
        folders = [
            ("Prospects", "Owner", self.root / "Prospects" / "Owner"),
            ("Various", "Various", self.root / "Various"),
        ]
        api = self.stub_api(folders)
        catalog = self.empty_catalog()
        catalog_path = self.root / ".likeness-library.json"
        catalog_path.write_text("{}", encoding="utf-8")
        core_id = metadata.photo_id_from_name(core.name)
        candidate_id = metadata.photo_id_from_name(candidate.name)
        core_record = {
            "vector": np.array([1.0, 0.0]), "side": "Prospects",
            "category": "Prospects", "personIds": [], "identityProtected": False,
            "mode": "fixture", "corePhotoIds": [core_id], "photoScores": {core.name: 1.0},
        }
        source_rows = [
            {
                "source": core.relative_to(self.root).as_posix(),
                "sourceHash": metadata.content_sha256(core), "originalName": core.name,
                "standardName": core.name, "owner": "Prospects/Owner", "group": "Prospects",
                "folderName": "Owner", "bucket": "gallery", "photoId": core_id,
                "idBasis": "filename", "sourceStatus": "eligible",
            },
            {
                "source": candidate.relative_to(self.root).as_posix(),
                "sourceHash": metadata.content_sha256(candidate), "originalName": candidate.name,
                "standardName": candidate.name, "owner": "Various", "group": "Various",
                "folderName": "Various", "bucket": "gallery", "photoId": candidate_id,
                "idBasis": "filename", "sourceStatus": "eligible",
                "retainedManifest": "verified-retained-manifest.json",
                "retainedSourceHash": "verified-original-hash",
            },
        ]
        prepared_root = self.root / "reports" / "runs" / "prep"
        prepared_root.mkdir(parents=True, exist_ok=True)
        (prepared_root / "manifest.json").write_text("{}", encoding="utf-8")
        core_native = prepared_root / "core-native.jpg"
        core_native.write_bytes(b"prepared core")
        prep_result = (
            prepared_root, {"recipe": {"id": "fixture"}, "photos": []},
            {core.relative_to(self.root).as_posix(): core_native},
        )
        generation_seal = {
            "kind": "normal-rebase-preparation-origin-complete",
            "profile": "lean",
            "generationProducerSHA256": "c" * 64,
        }
        fake_policy = {"version": "fixture", "status": "approved"}
        with mock.patch.object(metadata, "load_catalog", return_value=catalog), \
                mock.patch.object(metadata, "path_for_root", return_value=catalog_path), \
                mock.patch.object(normal_rebase, "_hash_sources", return_value=(source_rows, folders, [])), \
                mock.patch.object(normal_rebase, "load_policy", return_value=fake_policy), \
                mock.patch.object(normal_rebase, "effective_settings", return_value={"minFace": 1}), \
                mock.patch.object(normal_rebase, "_fragment_evidence", return_value={
                    "activation": "diagnostic-only", "candidateLinks": [], "comparisons": [],
                }), \
                mock.patch.object(normal_rebase, "_infer", return_value=(
                    "fixture-digest", {"v": [1.0, 0.0], "faces": 1, "px": 100, "t": "fixture"},
                )), \
                mock.patch.object(
                    normal_rebase.reconciliation, "frozen_identity_cores",
                    return_value=({"Prospects/Owner": core_record}, set(), []),
                ), \
                mock.patch.object(normal_rebase.normal_import, "_route_plan", return_value={
                    "assignments": [], "held": [], "clusters": [],
                }) as route, \
                mock.patch.object(
                    normal_rebase, "_prepare_with_origin",
                    return_value=(prep_result, generation_seal),
                ) as prepare, \
                mock.patch.object(normal_rebase.maintenance, "proposed_moves", return_value=[]), \
                mock.patch.object(
                    normal_rebase.normal_finish, "check_batch",
                    return_value=([], {"passCount": 1, "frozenRivals": {}, "corrections": []}),
                ) as audit, \
                mock.patch.object(normal_rebase, "_bindings", return_value={"fixture": "bound"}):
            report, _photos, publication_space, *_rest = normal_rebase._plan(
                self.root, "lean", "fixture-retained", api=api,
            )
        self.assertEqual(report["canonicalInputCount"], 1)
        self.assertEqual([photo.name for photo in publication_space.photos], [core.name])
        retained_hold = next(row for row in report["sourceHolds"] if row["photoId"] == candidate_id)
        self.assertEqual(retained_hold["rebaseRole"], "verified-retained-native-held")
        self.assertEqual(retained_hold["retainedSourceHash"], "verified-original-hash")
        self.assertEqual(prepare.call_args.args[4], [core])
        self.assertEqual(route.call_args.args[1], [])
        audit.assert_called_once()


class SettlePassTests(unittest.TestCase):
    """Item (d): bounded settle passes over planned identities (pure planning)."""

    def setUp(self):
        from tools.art.likeness_library import normal_admission, policy, reconciliation

        self.admission = normal_admission
        self.policy = policy.load_policy()
        self.settings = policy.effective_settings({}, self.policy)
        self.api = SimpleNamespace(
            plan_reconciliation=reconciliation.plan_reconciliation,
            invent_name=lambda seed, _taken: "Fixture-" + seed[:8],
        )

    @staticmethod
    def unit(*values):
        vector = np.asarray(values, dtype=float)
        return vector / np.linalg.norm(vector)

    def entry(self, photo_id, folder, vector, **extra):
        return {
            "photoId": photo_id, "sha256": hashlib.sha256(photo_id.encode()).hexdigest(),
            "vector": self.unit(*vector), "sourceFolder": folder,
            "sourceLocation": (folder, "gallery"), "voter": True, "scorable": True,
            "exemptReason": None, "stayExemptReason": None, "seedOf": None,
            "candidateState": {"rejectedPersonIds": []},
            "candidate": {"qualityEligible": True, "referenceQualityEligible": True, "rejectedPersonIds": []},
            **extra,
        }

    @staticmethod
    def admitted(photo_id, folder, provisional=None):
        return {
            "photoId": photo_id, "sourceFolder": "Various", "sourceBucket": "Pool",
            "destination": folder, "destinationType": "provisional" if provisional else "existing",
            "normalAdmission": True, "reason": "fixture admission",
            **({"clusterId": provisional} if provisional else {}),
        }

    def settle(self, entries, decisions, clusters=None, *, passes=3):
        clusters = [] if clusters is None else clusters
        result, timings = self.admission.settle_passes(
            self.api, entries, decisions, clusters, {}, self.settings, self.policy, set(),
            max_passes=passes,
        )
        self.assertEqual(len(timings), result["passCount"])
        self.assertTrue(all(seconds >= 0 for seconds in timings))
        return result, clusters

    def chain(self):
        """z (red) holds w up; once z leaves, w drops to orange."""
        entries = [
            self.entry("g1", "Models/Gamma", (1, 0, 0)),
            self.entry("g2", "Models/Gamma", (1, .01, 0)),
            self.entry("w", "Models/Gamma", (.2, .98, 0)),
            self.entry("z", "Models/Gamma", (-.3, .954, 0)),
        ]
        decisions = {"z": self.admitted("z", "Models/Gamma"), "w": self.admitted("w", "Models/Gamma")}
        return entries, decisions

    def test_member_orange_after_admission_is_released_and_rematched(self):
        entries = [
            self.entry("a1", "Models/Alpha", (1, 0, 0)),
            self.entry("a2", "Models/Alpha", (1, .05, 0)),
            self.entry("a3", "Models/Alpha", (1, -.05, 0)),
            self.entry("b1", "Models/Beta", (0, 1, .05)),
            self.entry("b2", "Models/Beta", (0, 1, -.05)),
            self.entry("x", "Various", (.25, .97, 0), sourceLocation=("Various", "gallery")),
        ]
        decisions = {"x": self.admitted("x", "Models/Alpha")}
        result, _clusters = self.settle(entries, decisions)
        first = result["passes"][0]
        self.assertEqual((first["flaggedCount"], first["releasedCount"], first["movedCount"]), (1, 1, 1))
        self.assertEqual(first["released"][0]["band"], "orange")
        self.assertEqual(first["released"][0]["outcome"], "Models/Beta/gallery")
        self.assertEqual(decisions["x"]["destination"], "Models/Beta")
        self.assertEqual(decisions["x"]["settle"]["releasedFrom"], "Models/Alpha")
        self.assertTrue(decisions["x"]["normalAdmission"])
        self.assertFalse(decisions["x"]["referenceEligible"])
        self.assertTrue(decisions["x"]["referenceVersion"])
        self.assertEqual(result["passCount"], 2)
        self.assertEqual(result["passes"][1]["releasedCount"], 0)
        self.assertTrue(result["converged"])
        self.assertEqual(result["didNotSettle"], [])

    def test_pass_limit_reports_did_not_settle_and_more_passes_settle_it(self):
        entries, decisions = self.chain()
        limited, _clusters = self.settle(copy.deepcopy(entries), copy.deepcopy(decisions), passes=1)
        self.assertEqual(limited["passCount"], 1)
        self.assertEqual(limited["passes"][0]["released"][0]["photoId"], "z")
        self.assertEqual(limited["passes"][0]["remainingFlaggedCount"], 1)
        self.assertFalse(limited["converged"])
        self.assertEqual([(row["photoId"], row["band"], row["reason"]) for row in limited["didNotSettle"]],
                         [("w", "orange", "flagged after the final settle pass")])
        settled, _clusters = self.settle(entries, decisions, passes=3)
        self.assertEqual([item["releasedCount"] for item in settled["passes"]], [1, 1, 0])
        self.assertEqual(settled["didNotSettle"], [])
        # z left as a single-photo Potential (c); once w is released it scores well there and joins it.
        self.assertEqual(decisions["z"]["destination"], decisions["w"]["destination"])
        self.assertEqual(decisions["w"]["destinationType"], "provisional")
        self.assertEqual(settled["passes"][0]["newIdentities"][0]["singlePhoto"], True)
        self.assertEqual(_clusters[0]["photoIds"], ["w", "z"])
        self.assertNotIn("singlePhoto", _clusters[0])
        self.assertNotIn("singlePhoto", decisions["z"])

    def test_disabled_and_deterministic(self):
        entries, decisions = self.chain()
        first, _ = self.settle(copy.deepcopy(entries), copy.deepcopy(decisions))
        second, _ = self.settle(copy.deepcopy(entries), copy.deepcopy(decisions))
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        reordered = list(reversed(copy.deepcopy(entries)))
        third, _ = self.settle(reordered, copy.deepcopy(decisions))
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(third, sort_keys=True))

    def test_cast_seed_and_protected_members_are_exempt(self):
        entries = [
            self.entry("s1", "Sisters/Cast", (1, 0, 0)),
            self.entry("s2", "Sisters/Cast", (1, .05, 0)),
            self.entry("s3", "Sisters/Cast", (1, .05, .05)),
            self.entry("seed", "Sisters/Cast", (.2, 0, .98), seedOf="Sisters/Cast"),
            self.entry("kept", "Sisters/Cast", (.2, .98, 0), exemptReason="protected photo"),
            self.entry("stay", "Sisters/Cast", (.2, -.98, 0), stayExemptReason="existing member outside a release cohort"),
            self.entry("loose", "Sisters/Cast", (.25, 0, -.97)),
        ]
        result, clusters = self.settle(entries, {})
        released = [item["photoId"] for item in result["passes"][0]["released"]]
        self.assertEqual(released, ["loose"])
        reasons = {row["photoId"]: row["reason"] for row in result["didNotSettle"]}
        self.assertEqual(reasons["seed"], "cast seed member (exempt)")
        self.assertEqual(reasons["kept"], "protected photo")
        self.assertEqual(reasons["stay"], "existing member outside a release cohort")
        # The released cast member matches nothing at yellow: (c) single-photo Potential.
        self.assertEqual(len(clusters), 1)
        self.assertTrue(clusters[0]["singlePhoto"])
        self.assertTrue(clusters[0]["destination"].startswith("Potentials/"))
        self.assertEqual(clusters[0]["photoIds"], ["loose"])

    def reduced(self, rival):
        entries = [
            self.entry("p1", "Various", (1, 0, 0), sourceLocation=("Various", "gallery")),
            self.entry("p2", "Various", (.2, .98, 0), sourceLocation=("Various", "gallery")),
            self.entry("p3", "Various", (.2, -.98, 0), sourceLocation=("Various", "gallery")),
            self.entry("r1", "Models/Rival", rival),
            self.entry("r2", "Models/Rival", tuple(value + .01 for value in rival)),
        ]
        decisions = {pid: self.admitted(pid, "Potentials/Pair", "pair") for pid in ("p1", "p2", "p3")}
        clusters = [{"clusterId": "pair", "destination": "Potentials/Pair", "destinationType": "provisional",
                     "photoIds": ["p1", "p2", "p3"], "corePhotoIds": ["p1", "p2", "p3"]}]
        result, clusters = self.settle(entries, decisions, clusters)
        return result, decisions, clusters

    def test_identity_reduced_to_one_photo_follows_single_photo_rule(self):
        result, decisions, clusters = self.reduced((0, 0, 1))
        self.assertEqual(sorted(item["photoId"] for item in result["passes"][0]["released"]), ["p2", "p3"])
        pair = next(cluster for cluster in clusters if cluster["destination"] == "Potentials/Pair")
        self.assertEqual(pair["photoIds"], ["p1"])
        self.assertTrue(pair["singlePhoto"])
        self.assertTrue(decisions["p1"]["singlePhoto"])
        reduction = result["passes"][0]["singlePhotoReductions"][0]
        self.assertEqual((reduction["photoId"], reduction["outcome"]), ("p1", "single-photo Potential"))
        # Released members that match nothing at yellow become labelled single-photo Potentials.
        singles = [cluster for cluster in clusters if cluster["destination"] != "Potentials/Pair"]
        self.assertEqual(sorted(cluster["photoIds"][0] for cluster in singles), ["p2", "p3"])
        self.assertTrue(all(cluster["singlePhoto"] for cluster in singles))

        result, decisions, clusters = self.reduced((.5, 0, .866))
        self.assertEqual(decisions["p1"]["reviewDestination"], "Models/Rival/review")
        self.assertIsNone(decisions["p1"]["destination"])
        self.assertNotIn("Potentials/Pair", [cluster["destination"] for cluster in clusters])
        reduction = result["passes"][0]["singlePhotoReductions"][0]
        self.assertEqual(reduction["outcome"], "Models/Rival/review")
        self.assertGreaterEqual(reduction["singlePhotoGate"]["bestRivalScore"], .30)


class RelocatedPreparationTests(unittest.TestCase):
    """A sealed preparation copied byte-for-byte into another Sandbox Working."""

    RUN = ("_reports", "runs", "normal-rebase-sealed-preview")

    def setUp(self):
        scratch = ROOT / "tmp" / "normal-flow-restoration"
        scratch.mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temp.cleanup)
        base = pathlib.Path(temp.name).resolve()
        self.original = base / "main" / "Sovereign Territories Sandbox" / "Working"
        self.copy = base / "universe" / "Sovereign Territories Sandbox" / "Working"
        self.original.mkdir(parents=True)
        self.copy.mkdir(parents=True)

    @staticmethod
    def output_for(root):
        return root.joinpath(*RelocatedPreparationTests.RUN, "preparation", "inputs",
                             "_reports", "preparation", "selected")

    def seal(self):
        """Seal a fixture preparation in the original Working and copy it unchanged."""
        import shutil

        from tools.art import image_preparation
        from tools.workflows import comfy_workflows as cw

        cfg = cw.load_cfg()
        source = self.original / "Angels" / "Owner" / "gallery" / "owner_image_907.jpg"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"sealed original bytes")
        run = self.original.joinpath(*self.RUN)
        start, _start_path, start_hash = normal_rebase._write_preparation_origin_start(
            self.original, cfg, run, "lean", [source],
        )
        output = self.output_for(self.original)
        output.mkdir(parents=True)
        (output / "manifest.json").write_text("sealed relocation manifest", encoding="utf-8")
        mirror = output.parents[2]
        relative = source.relative_to(self.original).as_posix()
        mirrored = mirror / pathlib.PurePosixPath(relative)
        mirrored.parent.mkdir(parents=True)
        mirrored.write_bytes(source.read_bytes())
        data = {
            "recipe": image_preparation.RECIPE, "storageMode": "lean",
            "configurationReceipt": cw.storage_configuration_receipt(cfg, mirror, {
                "runOutput": output, "temporaryRoot": cw.storage_root(cfg, "temporary", root=mirror),
            }),
            "photos": [{"source": relative, "sourceSha256": metadata.content_sha256(source)}],
        }
        normal_rebase._write_preparation_origin_complete(
            self.original, cfg, "lean", [source], (output, data, {}), start, start_hash,
        )
        shutil.copytree(run, self.copy.joinpath(*self.RUN))
        arrival = self.copy / "Various" / "gallery" / "owner_image_907.jpg"
        arrival.parent.mkdir(parents=True)
        arrival.write_bytes(source.read_bytes())
        return cfg, data, relative, arrival

    def test_relocated_origin_binds_only_the_exact_sealed_relative_path(self):
        _cfg, _data, _relative, _arrival = self.seal()
        manifest_hash = metadata.content_sha256(self.output_for(self.copy) / "manifest.json")
        self.assertIsNone(normal_products.relocated_origin(
            self.original, self.output_for(self.original), manifest_hash))
        relocation = normal_products.relocated_origin(self.copy, self.output_for(self.copy), manifest_hash)
        self.assertEqual(relocation, {
            "originalRoot": str(self.original),
            "originalPreparationRoot": str(self.output_for(self.original)),
            "originalMirror": str(self.output_for(self.original).parents[2]),
        })
        with self.assertRaisesRegex(ValueError, "does not bind this manifest"):
            normal_products.relocated_origin(self.copy, self.output_for(self.copy), "0" * 64)
        moved = self.copy / "_reports" / "runs" / "elsewhere"
        moved.mkdir(parents=True)
        nested = moved / "normal-rebase-sealed-preview"
        import shutil
        shutil.copytree(self.copy.joinpath(*self.RUN), nested)
        nested_output = nested.joinpath("preparation", "inputs", "_reports", "preparation", "selected")
        with self.assertRaisesRegex(ValueError, "keep its sealed path"):
            normal_products.relocated_origin(self.copy, nested_output, manifest_hash)
        outside = self.copy.parents[1] / "Not A Sandbox" / "Working"
        shutil.copytree(self.copy.joinpath(*self.RUN), outside.joinpath(*self.RUN))
        with self.assertRaisesRegex(ValueError, "restricted to Sandbox Working"):
            normal_products.relocated_origin(outside, self.output_for(outside), manifest_hash)

    def test_relocated_reuse_verifies_with_recorded_mirror_and_binds_by_content(self):
        cfg, data, relative, arrival = self.seal()
        output = self.output_for(self.copy)
        manifest_hash = metadata.content_sha256(output / "manifest.json")
        native = output / "native.jpg"
        native.write_bytes(b"prepared native")
        fake_module = SimpleNamespace(verify=mock.Mock(return_value=data))
        with mock.patch.dict("sys.modules", {"image_preparation": fake_module}), \
                mock.patch("tools.art.likeness_library.clean_preparation.selected_path", return_value=native):
            with self.assertRaisesRegex(ValueError, "exact current selected source set"):
                normal_products.reuse_prepared(self.copy, output, [arrival], "lean", manifest_hash)
            prepared = normal_products.reuse_prepared(
                self.copy, output, [arrival], "lean", manifest_hash, allow_subset=True,
            )
        fake_module.verify.assert_called_with(
            output.parents[2], output, recorded_root=str(self.output_for(self.original).parents[2]),
        )
        self.assertEqual(fake_module.verify.call_args_list[0], mock.call(output.parents[2], output))
        arrival_relative = arrival.relative_to(self.copy).as_posix()
        self.assertEqual(prepared[2], {arrival_relative: native})
        self.assertEqual(prepared[1]["reuseSourceAliases"], {
            arrival_relative: {"preparedSource": relative, "sourceSha256": metadata.content_sha256(arrival)},
        })
        binding = normal_rebase._validate_preparation_reuse(self.copy, cfg, "lean", prepared, [arrival])
        self.assertEqual(binding["generationProvenance"], "origin-sealed")
        self.assertEqual(binding["relocatedFrom"], prepared[1]["reuseRelocation"])
        self.assertEqual(binding["path"], str(output))

        forged = {**prepared[1], "reuseRelocation": {**prepared[1]["reuseRelocation"], "originalRoot": "C:\\Other"}}
        with self.assertRaisesRegex(ValueError, "relocation differs from its origin seal"):
            normal_rebase._validate_preparation_reuse(self.copy, cfg, "lean", (output, forged, prepared[2]), [arrival])
        unrelated = self.copy / "Various" / "gallery" / "other_image_1.jpg"
        unrelated.write_bytes(b"not sealed")
        with mock.patch.dict("sys.modules", {"image_preparation": fake_module}), \
                mock.patch("tools.art.likeness_library.clean_preparation.selected_path", return_value=native), \
                self.assertRaisesRegex(ValueError, "does not cover"):
            normal_products.reuse_prepared(self.copy, output, [unrelated], "lean", manifest_hash, allow_subset=True)


if __name__ == "__main__":
    unittest.main()
