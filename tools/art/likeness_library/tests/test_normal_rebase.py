import contextvars
import contextlib
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

from tools.art import originals
from tools.art.likeness_library import metadata, normal_products, normal_rebase


ROOT = pathlib.Path(__file__).resolve().parents[4]


class NormalRebaseTests(unittest.TestCase):
    def setUp(self):
        self.scratch = ROOT / "tmp" / "normal-flow-restoration"
        self.scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=self.scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name) / "Working"
        self.root.mkdir()

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
            self.root, cfg, run, "lean", [source],
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
                    "sourceHashes": {relative: move["sha256"]},
                    "incomingUpdates": {}, "exactAliasTargets": {},
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

        def prepare_with_origin(_root, _cfg, _run, profile, paths):
            self.assertEqual(api.domains.CURRENT.get(), "general")
            self.assertTrue(api.domains.READ_ONLY.get())
            self.assertEqual(profile, "lean")
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


if __name__ == "__main__":
    unittest.main()
