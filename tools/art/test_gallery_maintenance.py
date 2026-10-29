"""Local maintenance and derivative provenance integration regressions."""
import contextlib
import hashlib
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
from PIL import Image  # noqa: E402
import gallery_maintenance as upkeep  # noqa: E402
from likeness_library import actions, derivatives, metadata, person_rename, review_gallery  # noqa: E402


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="maintenance-", dir=ROOT / "tmp")
        base = pathlib.Path(self.temporary.name)
        self.root = base / "library"
        self.folder = self.root / "Angels" / "Fixed Slot"
        self.gallery = self.folder / "gallery"
        self.gallery.mkdir(parents=True)
        self.photo = self.gallery / "other_image_123.jpg"
        Image.new("RGB", (400, 600), "red").save(self.photo)
        self.original = self.photo.read_bytes()
        self.box = [0.35, 0.2, 0.3, 0.25]
        self.cache = self.root / "cache.json"
        self.cache.write_text(json.dumps({"emb": {
            hashlib.sha1(self.original).hexdigest(): {"box": self.box, "px": 120}
        }}), encoding="utf-8")
        self.catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
        (self.root / ".likeness-library.json").write_text(json.dumps(self.catalog), encoding="utf-8")
        self.cfg = upkeep.cw.load_cfg()
        self.cfg["paths"].update({
            "productionRoot": str(self.root),
            "sandboxWorkingRoot": str(base / "Sovereign Territories Sandbox" / "Working"),
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

    def tearDown(self):
        self.temporary.cleanup()

    def call(self, *args):
        with mock.patch.object(upkeep.cw, "load_cfg", return_value=self.cfg), contextlib.redirect_stdout(io.StringIO()):
            return upkeep.main(["--root", str(self.root), "--cache", str(self.cache), "--no-reports", *args])

    def tree(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def test_preview_and_check_are_read_only_and_apply_is_repeat_safe(self):
        before = self.tree()
        self.assertEqual(self.call("--dry-run"), 0)
        self.assertEqual(self.call("--check"), 1)
        self.assertEqual(before, self.tree())
        self.assertEqual(self.call("--apply"), 0)
        source = self.gallery / "fixed_slot_image_123.jpg"
        self.assertEqual(source.read_bytes(), self.original)
        self.assertFalse(self.photo.exists())
        for framing in ("padded", "head", "chest"):
            target, _ = derivatives.verified(source, framing, self.box)
            with Image.open(target) as image:
                self.assertEqual(image.size, derivatives.SIZE)
        self.assertEqual(self.call("--check"), 0)
        target, _ = derivatives.verified(source, "chest", self.box)
        timestamp = target.stat().st_mtime_ns
        self.assertEqual(self.call("--apply"), 0)
        self.assertEqual(target.stat().st_mtime_ns, timestamp)
        self.assertEqual(self.cache.read_text(encoding="utf-8"), before["cache.json"].decode())

    def test_review_only_and_artist_nested_folders_are_maintained(self):
        review = self.root / "Artists" / "Painter" / "Person" / "review"
        review.mkdir(parents=True)
        photo = review / "different_image_987.jpg"
        photo.write_bytes(self.original)
        self.assertEqual(self.call("--apply"), 0)
        source = review / "person_image_987.jpg"
        self.assertTrue(source.exists())
        target, _ = derivatives.verified(source, "chest", self.box)
        self.assertEqual(target.parent.name, "review_chest_944x1104")

    def test_thumbnail_changes_with_recipe_box_or_derivative_and_never_recrops_original(self):
        self.call("--apply")
        source = self.gallery / "fixed_slot_image_123.jpg"
        data, first, diagnostic = derivatives.thumbnail(source, "chest", self.box)
        self.assertIsNone(diagnostic)
        altered = [0.2, 0.2, 0.3, 0.25]
        _, second, diagnostic = derivatives.thumbnail(source, "chest", altered)
        self.assertNotEqual(first, second)
        self.assertIn("Stale", diagnostic)
        photo = type("Photo", (), {"path": source, "box": self.box, "sha": "not-used"})()
        with mock.patch.object(derivatives, "crop_thumbnail", side_effect=AssertionError("original crop")):
            items, _ = review_gallery.write_thumbnails([{"_photo": photo}], self.root)
        self.assertEqual(items[0]["derivativeDiagnostics"], [])
        self.assertEqual((self.root / items[0]["thumbnail"]).read_bytes(), data)

    def test_hand_edited_and_unowned_derivatives_are_preserved_and_backed_up(self):
        target = self.folder / derivatives.relative_target(self.photo, "chest")
        target.parent.mkdir()
        target.write_bytes(b"manual image")
        before = target.read_bytes()
        changes, messages = derivatives.maintain(self.photo, self.box, 120, apply=True)
        self.assertTrue(messages)
        self.assertEqual(target.read_bytes(), before)
        backup = upkeep.library_backup.create_backup(self.root, stamp="manual-test")
        self.assertTrue((backup / "work-root" / target.relative_to(self.root)).is_file())
        self.assertTrue(upkeep.library_backup.verify_backup(backup))

    def test_missing_and_unprocessable_faces_are_explicit(self):
        _, messages = derivatives.maintain(self.photo, None, 0, apply=True)
        self.assertEqual(len(messages), 2)
        _, _, diagnostic = derivatives.thumbnail(self.photo, "head", None)
        self.assertIn("Missing maintained head", diagnostic)

    def test_adopts_only_exact_regeneration_and_preserves_changed_owned_files(self):
        self.assertEqual(self.call("--apply"), 0)
        source = self.gallery / "fixed_slot_image_123.jpg"
        target, _ = derivatives.verified(source, "chest", self.box)
        manifest = self.folder / derivatives.MANIFEST
        manifest.unlink()
        timestamp = target.stat().st_mtime_ns
        changes, messages = derivatives.maintain(source, self.box, 120, apply=True)
        self.assertEqual(len(changes), 3)
        self.assertEqual(messages, [])
        self.assertEqual(target.stat().st_mtime_ns, timestamp)
        target.write_bytes(b"hand edited")
        _, messages = derivatives.maintain(source, self.box, 120, apply=True)
        self.assertIn("Preserved unowned/edited asset", messages[0])
        self.assertEqual(target.read_bytes(), b"hand edited")

    def test_orphan_pruning_is_exact_and_respects_workflow_choices(self):
        self.call("--apply")
        source = self.gallery / "fixed_slot_image_123.jpg"
        target, _ = derivatives.verified(source, "chest", self.box)
        manual = target.parent / "manual_944x1104.png"
        manual.write_bytes(b"manual")
        source.unlink()
        changes, messages = derivatives.prune(
            self.folder, self.root, apply=True, protected_names={target.name.casefold()})
        self.assertEqual(len(changes), 2)
        self.assertIn("workflow-selected", messages[0])
        self.assertTrue(target.is_file())
        self.assertEqual(manual.read_bytes(), b"manual")

    def test_backup_failure_does_not_settle_actions_or_rename(self):
        record = {"type": "person-renamed", "id": "a1", "batchId": "b1"}
        catalog = {**self.catalog, "actions": [record]}
        before = self.tree()
        with mock.patch.object(upkeep.metadata, "load_catalog", return_value=catalog), \
                mock.patch.object(upkeep.library_backup, "create_backup", side_effect=OSError("failed backup")):
            self.assertEqual(self.call("--apply", "--settle-actions"), 2)
        self.assertEqual(self.tree(), before)

    def test_isolated_cache_and_output_must_stay_inside_root(self):
        self.cfg["paths"]["productionRoot"] = str(self.root / "configured-production")
        with mock.patch.object(upkeep.cw, "load_cfg", return_value=self.cfg):
            self.assertEqual(upkeep.main([
                "--root", str(self.root), "--cache", str(self.root.parent / "cache.json"), "--check"]), 2)
            self.assertEqual(upkeep.main([
                "--root", str(self.root), "--cache", str(self.cache),
                "--out", str(self.root.parent / "reports"), "--check"]), 2)

    def test_actual_launcher_preview_apply_check_and_missing_reports(self):
        import subprocess
        command = [str(ROOT / "bin" / "people-gallery.cmd"), "--root", str(self.root),
                   "--cache", str(self.cache), "--no-reports"]
        before = self.tree()
        preview = subprocess.run([*command, "--dry-run"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertEqual(before, self.tree())
        applied = subprocess.run([*command, "--apply"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        checked = subprocess.run([*command, "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        with mock.patch.object(upkeep.cw, "load_cfg", return_value=self.cfg), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(upkeep.main(["--root", str(self.root), "--cache", str(self.cache), "--check"]), 1)

    def test_full_reports_refresh_and_check_share_provenance_without_matching(self):
        import likeness
        cache = json.loads(self.cache.read_text(encoding="utf-8"))
        for face in cache["emb"].values():
            face.update({"faces": 1, "v": [1.0, 0.0, 0.0], "s": 0.9, "t": 1})
        self.cache.write_text(json.dumps(cache), encoding="utf-8")
        arguments = ["--root", str(self.root), "--cache", str(self.cache)]
        with mock.patch.object(upkeep.cw, "load_cfg", return_value=self.cfg), \
                mock.patch.object(likeness, "Embedder", return_value=mock.Mock(spec=[],
                    side_effect=AssertionError("must use the cached detector result"))), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(upkeep.main([*arguments, "--apply"]), 0)
            self.assertEqual(upkeep.main([*arguments, "--check"]), 0)
        report = self.root / "_reports" / "library" / "people_gallery_review.html"
        self.assertIn("thumbnailProvenance", report.read_text(encoding="utf-8"))
        self.assertIn("chest_944x1104", report.read_text(encoding="utf-8"))

    def test_collision_holds_original_names_but_maintains_both_derivatives(self):
        other = self.gallery / "fixed_slot_image_123.jpg"
        other.write_bytes(self.original)
        self.assertEqual(self.call("--dry-run"), 0)
        self.assertEqual(self.call("--apply"), 1)
        self.assertEqual(other.read_bytes(), self.original)
        self.assertEqual(self.photo.read_bytes(), self.original)
        derivatives.verified(self.photo, "chest", self.box)
        derivatives.verified(other, "chest", self.box)
        self.assertEqual(self.call("--check"), 1)
        self.assertEqual(self.call("--apply"), 1)

    def test_non_id_base_collisions_are_explicit_holds_not_destructive_renames(self):
        first, second = self.gallery / "mia_wolfe_base.jpg", self.gallery / "other_person_base.jpg"
        first.write_bytes(self.original)
        second.write_bytes(self.original)
        (self.root / "Prospects" / "Mia Wolfe" / "gallery").mkdir(parents=True)
        (self.root / "Prospects" / "Other Person" / "gallery").mkdir(parents=True)
        self.assertEqual(self.call("--apply"), 1)
        self.assertEqual(first.read_bytes(), self.original)
        self.assertEqual(second.read_bytes(), self.original)
        derivatives.verified(first, "padded")
        derivatives.verified(second, "padded")

    def test_active_action_requires_explicit_settlement_and_undo_points_to_backup(self):
        record = {"type": "person-renamed", "id": "a1", "batchId": "b1"}
        catalog = {**self.catalog, "actions": [record]}
        with mock.patch.object(upkeep.metadata, "load_catalog", return_value=catalog):
            before = self.tree()
            self.assertEqual(self.call("--apply"), 2)
            self.assertEqual(self.tree(), before)
            self.assertEqual(self.call("--apply", "--settle-actions"), 0)
        errors, _, _ = actions.plan_undo(catalog, self.root)
        self.assertIn("explicitly settled", errors[0])
        settlement = upkeep.settled(self.root)["b1"]
        backup = pathlib.Path(settlement["backup"])
        self.assertTrue(upkeep.library_backup.verify_backup(backup))
        self.assertEqual(
            (backup / "work-root" / self.photo.relative_to(self.root)).read_bytes(), self.original)

    def test_real_cast_rename_full_restore_then_exact_action_undo(self):
        history = self.gallery / "z_fixed_slot.txt"
        history.write_text("name: Original Person\n", encoding="utf-8")
        person_id = "person_" + "a" * 32
        self.catalog["people"][person_id] = {
            "id": person_id, "folder": "Angels/Fixed Slot", "displayName": "Fixed Slot",
            "folderHistory": [], "identityAnchors": [], "protected": True,
        }
        path = self.root / ".likeness-library.json"
        path.write_text(json.dumps(self.catalog), encoding="utf-8")
        original_tree = person_rename.tree_hash(self.folder)
        decision, reason = person_rename.decision(
            self.root, "Angels/Fixed Slot", person_id, self.catalog["people"][person_id], self.cfg)
        self.assertEqual(reason, "")
        document = {"manifestVersion": 1, "generatedAt": "2026-10-23T14:00:00Z",
                    "source": "people-gallery-review", "actions": [{**decision, "newName": "New Person"}]}
        batch, _ = actions.apply_actions(
            document, self.root, self.catalog, self.cfg, "Various",
            backup_fn=lambda *_: "verified-test-backup",
            save_fn=lambda value: path.write_text(json.dumps(value), encoding="utf-8"))
        self.assertEqual(self.call("--apply"), 2)
        before_held = person_rename.tree_hash(self.folder)
        unaffected = self.root / "Prospects" / "Unaffected" / "gallery"
        unaffected.mkdir(parents=True)
        (unaffected / "other_image_456.jpg").write_bytes(self.original)
        self.assertEqual(self.call("--apply", "--preserve-action-undo"), 1)
        self.assertEqual(person_rename.tree_hash(self.folder), before_held)
        self.assertTrue((unaffected / "unaffected_image_456.jpg").is_file())
        self.assertFalse((self.root / upkeep.SETTLEMENT).exists())
        errors, selected, _ = actions.plan_undo(metadata.load_catalog(path), self.root, cfg=self.cfg)
        self.assertEqual(errors, [])
        self.assertEqual(selected, batch)
        self.assertEqual(self.call("--apply", "--settle-actions"), 0)
        recovery = pathlib.Path(upkeep.settled(self.root)[batch]["backup"]) / "work-root"
        restored = self.root.parent / "restored"
        try:
            materialized = restored.with_name(restored.name + "-snapshot")
            upkeep.library_backup.restore_backup(recovery.parent, materialized, apply=True)
            shutil.move(str(materialized / "work-root"), str(restored))
            shutil.rmtree(materialized)
            restored_catalog = metadata.load_catalog(restored / ".likeness-library.json")
            actions.undo_actions(
                restored_catalog, restored, self.cfg, "Various", batch_id=batch,
                backup_fn=lambda *_: "verified-test-backup",
                save_fn=lambda value: (restored / ".likeness-library.json").write_text(
                    json.dumps(value), encoding="utf-8"))
            self.assertEqual(person_rename.tree_hash(restored / "Angels" / "Fixed Slot"), original_tree)
            self.assertEqual(
                (restored / "Angels" / "Fixed Slot" / "gallery" / self.photo.name).read_bytes(), self.original)
        finally:
            shutil.rmtree(restored, ignore_errors=True)

    def test_backup_omits_only_proven_derivatives_and_restores_exact_tree(self):
        self.assertEqual(self.call("--apply"), 0)
        source = self.gallery / "fixed_slot_image_123.jpg"
        chest, _ = derivatives.verified(source, "chest", self.box)
        chest.write_bytes(b"hand edited")
        manual = chest.parent / "manual_944x1104.png"
        manual.write_bytes(b"manual")
        expected = {p.relative_to(self.root).as_posix(): p.read_bytes()
                    for p in self.root.rglob("*") if p.is_file() and "_backup" not in p.parts}
        backup = upkeep.library_backup.create_backup(self.root, stamp="omission-proof")
        manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["regenerable"]), 2)
        self.assertTrue((backup / "work-root" / chest.relative_to(self.root)).is_file())
        self.assertTrue((backup / "work-root" / manual.relative_to(self.root)).is_file())
        destination = self.root / "restored"
        upkeep.library_backup.restore_backup(backup, destination)
        self.assertFalse(destination.exists())
        upkeep.library_backup.restore_backup(backup, destination, apply=True)
        actual = {p.relative_to(destination / "work-root").as_posix(): p.read_bytes()
                  for p in (destination / "work-root").rglob("*") if p.is_file()}
        self.assertEqual(actual, expected)
        with self.assertRaises(ValueError):
            upkeep.library_backup.restore_backup(backup, destination, apply=True)

    def test_backup_keeps_unknown_recipe_and_fails_if_regeneration_recipe_changes(self):
        self.call("--apply")
        backup = upkeep.library_backup.create_backup(self.root, stamp="recipe-proof")
        with mock.patch.object(derivatives, "RECIPE", "unsupported-next-version"):
            with self.assertRaises(OSError):
                upkeep.library_backup.verify_backup(backup)
            self.assertEqual(upkeep.library_backup.derivative_omissions(self.root), {})

    def test_omitted_source_tampering_refuses_restore_without_publishing_destination(self):
        self.call("--apply")
        backup = upkeep.library_backup.create_backup(self.root, stamp="tampered-source")
        source = backup / "work-root" / "Angels" / "Fixed Slot" / "gallery" / "fixed_slot_image_123.jpg"
        source.write_bytes(b"tampered original")
        destination = self.root / "must-not-exist"
        with self.assertRaises(OSError):
            upkeep.library_backup.restore_backup(backup, destination, apply=True)
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
