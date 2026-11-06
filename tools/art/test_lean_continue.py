import contextlib
import copy
import io
import json
import pathlib
import unittest
from types import SimpleNamespace
from unittest import mock

from tools.art import lean_continue
from tools.art import test_clean_preparation as fixtures
from tools.art.likeness_library import clean_preparation, clean_rebase, metadata


class LeanContinuationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.CleanPreparationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.working, self.source = self.fixture.working, self.fixture.run
        self.target = self.source.parent / "continued"

    def prepare(self):
        catalog_path = self.working / ".likeness-library.json"
        catalog = metadata.load_catalog(catalog_path)
        cast_source = "Angels/Fixed/gallery/fixed_image_123456.jpg"
        catalog["photos"]["photo:image_123456"] = {
            "contentSha256": self.fixture.inputs[cast_source][1], "protected": True,
        }
        metadata.save_catalog(catalog, catalog_path)
        self.fixture.command(intake_only=True, apply=True, storage_mode="lean", recovery_mode="disposable")
        self.fixture.command()
        return json.loads((self.source / "run.json").read_text())

    def command(self, **flags):
        args = SimpleNamespace(
            root=str(self.working), source_run=self.source.name, run=self.target.name, policy=None,
            **{**dict(apply=False, check=False, install=False, dry_run=False), **flags},
        )
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.object(lean_continue, "_layout", return_value=self.fixture.layout), \
                mock.patch.object(lean_continue, "_api", return_value=self.fixture.api):
            return lean_continue.command(args)

    def test_inventory_preview_never_starts_matching_or_creates_run(self):
        self.prepare()
        with mock.patch.object(clean_rebase, "create_plan", side_effect=AssertionError("preview started matching")):
            self.assertEqual(self.command(dry_run=True)["status"], "inventory")
        self.assertFalse(self.target.exists())

    def test_verified_reuse_uses_original_pixels_not_copies_and_never_undo(self):
        self.prepare()
        before = (self.source / "run.json").read_bytes()
        self.command(apply=True)
        plan = json.loads((self.target / "run.json").read_text())
        self.assertEqual(plan["status"], "preview")
        self.assertEqual(plan["recoveryMode"], "disposable")
        self.assertFalse((self.target / "inputs").exists())
        self.assertFalse((self.target / "source-overlay").exists())
        self.assertFalse((self.target / "previous").exists())
        self.assertEqual(before, (self.source / "run.json").read_bytes())
        output, data = clean_preparation.verify(self.fixture.layout, self.target)
        self.assertTrue(output.is_relative_to(self.source))
        self.assertEqual(len(data["photos"]), 5)
        self.command(check=True)
        with mock.patch.object(clean_rebase, "_refresh_galleries"), \
                mock.patch("library_backup.latest_work_root_backup",
                           side_effect=AssertionError("no backup")):
            self.command(install=True)
        self.command(check=True)
        self.assertEqual(json.loads((self.target / "run.json").read_text())["status"], "applied")
        self.assertFalse((self.target / "previous").exists())
        self.assertFalse((self.target / "previous-catalog.json").exists())

    def test_source_check_does_not_create_target_and_tampered_receipt_refuses(self):
        self.prepare()
        self.assertEqual(self.command(check=True)["status"], "source-verified")
        self.assertFalse(self.target.exists())
        self.command(apply=True)
        path = self.source / "intake.json"
        path.write_text(path.read_text() + " ", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "source changed"):
            self.command(check=True)

    def test_existing_preview_apply_retries_recap_without_rematching_or_installing(self):
        self.prepare()
        with mock.patch.object(lean_continue.rebase_recap, "main", side_effect=ValueError("recap failed")):
            with self.assertRaisesRegex(ValueError, "recap failed"):
                self.command(apply=True)
        before = (self.target / "run.json").read_bytes()
        with mock.patch.object(clean_rebase, "create_plan", side_effect=AssertionError("must not rematch")), \
                mock.patch.object(clean_rebase, "install_plan", side_effect=AssertionError("must not install")), \
                mock.patch.object(lean_continue.rebase_recap, "main", return_value=0) as recap:
            result = self.command(apply=True)
            self.assertEqual(result["status"], "preview")
            recap.assert_called_once_with([str(self.target)])
        self.assertEqual((self.target / "run.json").read_bytes(), before)

    def test_run_scope_refuses_production_traversal_and_same_run(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, "plain folder"):
            lean_continue.inspect(self.working, "../prepared", "new")
        with self.assertRaisesRegex(ValueError, "separate run"):
            lean_continue.inspect(self.working, self.source.name, self.source.name)
        with self.assertRaisesRegex(ValueError, "absolute"):
            lean_continue.inspect(pathlib.Path("Working"), "prepared", "new")

    def test_manual_protection_rebound_to_original_not_generated_automatic_locks(self):
        seed = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
        digest, prepared = "a" * 64, "b" * 64
        current = copy.deepcopy(seed)
        photo_id = "photo:image_123456"
        current["photos"][photo_id] = {"contentSha256": prepared, "protected": True}
        source = {"photos": [{"photoId": photo_id, "sha256": digest, "preparedSHA256": prepared}]}
        result = lean_continue.seed_catalog(source, current, seed)
        self.assertEqual(result["photos"][photo_id]["contentSha256"], digest)
        self.assertTrue(result["photos"][photo_id]["protected"])
        current["photos"][photo_id]["contentSha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "manual decision"):
            lean_continue.seed_catalog(source, current, seed)

    def test_missing_cached_measurement_fails_instead_of_loading_models(self):
        with self.assertRaisesRegex(ValueError, "measurement unavailable"):
            lean_continue.CachedOnlyEmbedder()(pathlib.Path("image.jpg"))

    def test_incomplete_measurement_cache_cannot_silently_repeat_detection(self):
        self.prepare()
        path = self.source / "likeness-cache.json"
        cache = json.loads(path.read_text())
        cache["emb"] = {}
        path.write_text(json.dumps(cache), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "measurement unavailable"):
            self.command(apply=True)
        self.assertFalse((self.target / "run.json").exists())

    def test_intervening_manual_identity_protection_is_preserved(self):
        person_id = "person_" + "a" * 32
        seed = {
            "schemaVersion": 1, "photos": {}, "actions": [],
            "people": {person_id: {
                "id": person_id, "folder": "Angels/Fixed", "displayName": "Fixed",
                "folderHistory": [], "identityAnchors": [], "protected": False,
            }},
        }
        current = copy.deepcopy(seed)
        current["people"][person_id]["protected"] = True
        result = lean_continue.seed_catalog({"photos": []}, current, seed, installed=seed)
        self.assertTrue(result["people"][person_id]["protected"])
        self.assertFalse(seed["people"][person_id]["protected"])

    def test_generated_identity_metadata_changes_are_not_new_manual_decisions(self):
        person_id = "person_" + "b" * 32
        empty = {"schemaVersion": 1, "photos": {}, "actions": [], "people": {}}
        installed = copy.deepcopy(empty)
        installed["people"][person_id] = {
            "id": person_id, "folder": "Angels/Fixed", "displayName": "Fixed",
            "folderHistory": [], "identityAnchors": ["photo:image_123456"], "protected": True,
        }
        current = copy.deepcopy(installed)
        current["people"][person_id].update(
            names={"currentName": "New surname"}, family={"surname": "New surname"},
            protectionProvenance={"reason": "automatic core refreshed"},
        )
        self.assertEqual(lean_continue.seed_catalog({"photos": []}, current, empty, installed), empty)
        for field, value in (
                ("identityAnchors", ["photo:image_654321"]),
                ("automaticProtectionOverride", "manual-protect")):
            with self.subTest(field=field):
                edited = copy.deepcopy(current)
                edited["people"][person_id][field] = value
                with self.assertRaisesRegex(ValueError, "manual decisions"):
                    lean_continue.seed_catalog({"photos": []}, edited, empty, installed)
        new_manual = copy.deepcopy(empty)
        new_manual["people"][person_id] = copy.deepcopy(installed["people"][person_id])
        with self.assertRaisesRegex(ValueError, "manual decisions"):
            lean_continue.seed_catalog({"photos": []}, new_manual, empty, empty)
        prior_unprotected = copy.deepcopy(installed)
        prior_unprotected["people"][person_id]["protected"] = False
        with self.assertRaisesRegex(ValueError, "manual decisions"):
            lean_continue.seed_catalog({"photos": []}, new_manual, empty, prior_unprotected)

    def test_manual_migration_refusal_precedes_expensive_preparation_verification(self):
        self.prepare()
        with mock.patch.object(lean_continue, "seed_catalog", side_effect=ValueError("explicit migration")), \
                mock.patch.object(clean_preparation, "verify") as verify:
            with self.assertRaisesRegex(ValueError, "explicit migration"):
                self.command(apply=True)
        verify.assert_not_called()
        self.assertFalse(self.target.exists())

    def test_preview_check_refuses_engine_or_measurement_changes_without_installing(self):
        self.prepare()
        self.command(apply=True)
        cache = self.target / "likeness-cache.json"
        original_cache = cache.read_bytes()
        cache.write_bytes(original_cache + b" ")
        with self.assertRaisesRegex(ValueError, "measurements changed"):
            self.command(check=True)
        cache.write_bytes(original_cache)
        receipt = self.target / "run.json"
        plan = json.loads(receipt.read_text())
        plan["implementationHashes"]["clean_rebase.py"] = "0" * 64
        receipt.write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "engine changed"):
            self.command(check=True)
        self.assertEqual(json.loads(receipt.read_text())["status"], "preview")

    def test_preview_requires_bound_likeness_producer_before_check_or_install(self):
        self.prepare()
        self.command(apply=True)
        receipt = self.target / "run.json"
        plan = json.loads(receipt.read_text())
        digest = plan["implementationHashes"]["likeness.py"]
        self.assertEqual(digest, metadata.content_sha256(pathlib.Path(clean_rebase.__file__).parent.parent / "likeness.py"))
        for altered in (None, "0" * 64):
            if altered is None:
                del plan["implementationHashes"]["likeness.py"]
            else:
                plan["implementationHashes"]["likeness.py"] = altered
            receipt.write_text(json.dumps(plan), encoding="utf-8")
            for flag in ("check", "install"):
                with self.subTest(altered=altered, flag=flag), \
                        self.assertRaisesRegex(ValueError, "engine changed|engine binding missing"):
                    self.command(**{flag: True})
        self.assertEqual(json.loads(receipt.read_text())["status"], "preview")

    def test_seed_snapshot_uses_its_own_receipt_not_live_catalogue_serialization(self):
        original = self.prepare()
        snapshot = self.source / "seed-catalog.json"
        snapshot.write_text(json.dumps(json.loads(snapshot.read_text())), encoding="utf-8")
        original["seedCatalogSHA256"] = metadata.content_sha256(snapshot)
        self.assertNotEqual(original["seedCatalogSHA256"], original["sourceCatalogSHA256"])
        (self.source / "run.json").write_text(json.dumps(original), encoding="utf-8")
        self.assertEqual(self.command(apply=True)["status"], "preview")


if __name__ == "__main__":
    unittest.main()
