"""Destination-owned retained preparation and shared browser continuity."""
import contextlib
import hashlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
import library_backup  # noqa: E402
import originals  # noqa: E402
from likeness_library import maintenance, preparation_provenance, retained_preparation as retained  # noqa: E402
from likeness_library import metadata  # noqa: E402
from likeness_library.policy import load_policy  # noqa: E402


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


class RetainedPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.base = pathlib.Path(self.temp.name)
        self.root = self.base / "library"
        self.prep = self.base / "preparation"
        self.root.mkdir()
        self.prep.mkdir()
        self.destination = "Various/review/incoming_image_123.jpg"
        self.original = b"exact original bytes"
        self.selected = b"native prepared bytes"
        self.source_sha = sha(self.original)
        self.row = {
            "source": "Various/gallery/incoming_image_123.jpg", "photoId": "photo:image_123",
            "sourceSha256": self.source_sha, "retained": "originals/original.jpg",
            "detail": "photos/detail.html",
            "processing": {"final": "composition", "cleanup": "composition"},
            "sourceScope": {"matchingDomain": "general"},
            "outcome": "compared", "variants": {},
        }
        self.put(self.prep, self.row["retained"], self.original)
        detail = b'<a href="../originals/original.jpg">Original</a><img src="../candidates/tone.png">'
        self.put(self.prep, self.row["detail"], detail)
        self.row["detailSha256"] = sha(detail)
        for name in ("composition", "denoise", "tone", "eraser-mask"):
            record = {}
            for field, checksum, suffix in (
                    ("path", "sha256", ".png"),
                    ("thumbnail", "thumbnailSha256", "-preview.jpg"),
                    ("padded", "paddedSha256", "-944x1104.png")):
                payload = self.selected if name == "composition" and field == "path" else (name + field).encode()
                relative = f"candidates/{name}{suffix}"
                self.put(self.prep, relative, payload)
                record.update({field: relative, checksum: sha(payload)})
            self.row["variants"][name] = record
        self.put(self.prep, "candidates/discarded.png", b"not a declared retained variant")
        self.put(self.root, self.destination, self.selected)

    def put(self, root, relative, payload):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return path

    def stage(self):
        return retained.stage_photo(
            self.root, self.destination, self.prep, self.row, recipe={"id": "test-v16"})

    def test_retains_exact_original_all_actual_variants_detail_and_no_unlisted_extras(self):
        published = self.stage()
        self.assertEqual(len(published), 15)
        self.assertNotIn(self.destination, [entry["path"] for entry in published])
        for entry in published:
            self.assertEqual(sha((self.root / entry["path"]).read_bytes()), entry["sha256"])
        data = retained.verify_link(self.root, self.destination, "photo:image_123")
        self.assertIsNotNone(data)
        self.assertEqual((self.root / data["original"]).read_bytes(), self.original)
        self.assertNotIn("discarded", json.dumps(published))
        self.assertIn("gallery_org", (self.root / data["detail"]).read_text())
        tone_path = data["artifactMap"][self.row["variants"]["tone"]["path"]]
        self.assertIn(pathlib.PurePosixPath(tone_path).name, (self.root / data["detail"]).read_text())
        self.assertNotIn("../candidates/", (self.root / data["detail"]).read_text())
        with self.assertRaises(ValueError):
            self.stage()

    def test_post_name_rename_keeps_link_for_matching_move(self):
        self.stage()
        before = self.root / self.destination
        after = before.with_name("various_image_123.jpg")
        retained.rename_photo(self.root, before, after)
        self.assertIsNone(retained.verify_link(self.root, before))
        self.assertIsNotNone(retained.verify_link(self.root, after, "photo:image_123"))
        destination = "Angels/Assigned/gallery/assigned_image_123.jpg"
        maintenance.validate_moves(self.root, [{
            "source": after.relative_to(self.root).as_posix(),
            "destination": destination, "sha256": sha(self.selected), "photoId": "photo:image_123",
        }])
        self.assertTrue(after.is_file())
        self.assertFalse((self.root / destination).exists())

    def test_digest_nested_input_artifacts_are_flattened_with_exact_hashes(self):
        for record in self.row["variants"].values():
            for field in ("path", "thumbnail", "padded"):
                old = record[field]
                new = f"candidates/{self.source_sha}/{pathlib.PurePosixPath(old).name}"
                payload = (self.prep / old).read_bytes()
                self.put(self.prep, new, payload)
                record[field] = new
        detail = ('<img src="../' + self.row["variants"]["tone"]["path"] + '">').encode()
        self.put(self.prep, self.row["detail"], detail)
        self.row["detailSha256"] = sha(detail)
        published = self.stage()
        data = retained.verify_link(self.root, self.destination)
        self.assertIsNotNone(data)
        for original_path, retained_path in data["artifactMap"].items():
            self.assertEqual(pathlib.PurePosixPath(retained_path).parts[-2], data["setKey"])
            self.assertEqual((self.root / retained_path).read_bytes(), (self.prep / original_path).read_bytes())
        self.assertFalse(any("/candidates/" in item["path"] for item in published))
        self.assertNotIn("candidates/", (self.root / data["detail"]).read_text())

    def maintenance_setup(self):
        metadata.save_catalog(
            {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
            self.root / ".likeness-library.json",
        )
        policy = load_policy()
        policy["status"] = "approved"
        move = {
            "source": self.destination,
            "destination": "Potentials/Assigned/gallery/assigned_image_123.jpg",
            "sha256": sha(self.selected), "photoId": "photo:image_123",
            "reason": "retained preparation transfer test",
        }
        return policy, move

    def test_cross_owner_move_and_undo_restore_exact_set_manifest_and_hashes(self):
        published = self.stage()
        before = {entry["path"]: (self.root / entry["path"]).read_bytes() for entry in published}
        policy, move = self.maintenance_setup()
        journal = maintenance.apply_moves(
            self.root, [move], policy, {}, backup_fn=lambda *_: "verified")
        data = retained.verify_link(self.root, move["destination"], "photo:image_123")
        self.assertIsNotNone(data)
        self.assertEqual(data["sourceSha256"], self.source_sha)
        self.assertEqual(data["currentSha256"], sha(self.selected))
        self.assertEqual(len(json.loads(journal.read_text())["retainedTransfers"]), 1)
        for relative in before:
            self.assertFalse((self.root / relative).exists())
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")
        self.assertEqual((self.root / move["source"]).read_bytes(), self.selected)
        self.assertIsNotNone(retained.verify_link(self.root, move["source"]))
        for relative, payload in before.items():
            self.assertEqual((self.root / relative).read_bytes(), payload)
        self.assertFalse((self.root / move["destination"]).exists())

    def test_transfer_source_changes_during_backup_and_target_collisions_stop_mutation(self):
        self.stage()
        policy, move = self.maintenance_setup()
        data = retained.verify_link(self.root, move["source"])
        target = self.root / f"Potentials/Assigned/gallery_intake/{data['setKey']}"
        target.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "target set exists"):
            maintenance.apply_moves(self.root, [move], policy, {}, backup_fn=lambda *_: "verified")
        target.rmdir()
        data = retained.verify_link(self.root, move["source"])
        artifact = self.root / data["original"]
        def stale_backup(*_):
            artifact.write_bytes(b"changed during backup")
            return "verified"
        with self.assertRaisesRegex(ValueError, "stale|version"):
            maintenance.apply_moves(self.root, [move], policy, {}, backup_fn=stale_backup)
        self.assertTrue((self.root / move["source"]).exists())
        self.assertFalse((self.root / move["destination"]).exists())

    def test_identical_original_bytes_keep_distinct_photo_records_under_same_owner(self):
        self.stage()
        first = retained.verify_link(self.root, self.destination, "photo:image_123")
        second_row = json.loads(json.dumps(self.row))
        second_row["source"] = "Various/gallery/incoming_image_456.jpg"
        second_row["photoId"] = "photo:image_456"
        second_destination = "Various/review/incoming_image_456.jpg"
        self.put(self.root, second_destination, self.selected)
        retained.stage_photo(self.root, second_destination, self.prep, second_row, recipe={"id": "test-v16"})
        second = retained.verify_link(self.root, second_destination, "photo:image_456")
        self.assertIsNotNone(second)
        self.assertNotEqual(first["setKey"], second["setKey"])
        self.assertNotEqual(first["detail"], second["detail"])
        self.assertEqual(first["sourceSha256"], second["sourceSha256"])
        self.assertIsNotNone(retained.verify_link(self.root, self.destination, "photo:image_123"))
        self.assertIsNone(retained.verify_link(self.root, second_destination, "photo:image_123"))
        self.assertNotEqual(
            retained._set_key(self.source_sha, self.row["source"], self.row["photoId"], "general", {"id": "test-v17"}),
            first["setKey"],
        )

    def test_undo_rejects_changed_target_manifest_and_artifacts(self):
        self.stage()
        policy, move = self.maintenance_setup()
        journal = maintenance.apply_moves(
            self.root, [move], policy, {}, backup_fn=lambda *_: "verified")
        data = retained.verify_link(self.root, move["destination"])
        manifest = self.root / data["manifest"]
        before = manifest.read_bytes()
        changed = json.loads(before)
        changed["recipe"] = {"id": "different recipe"}
        manifest.write_bytes(json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "cannot transfer stale or invalid retained preparation"):
            maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")
        manifest.write_bytes(before)
        (self.root / data["original"]).write_bytes(b"changed target bytes")
        with self.assertRaisesRegex(ValueError, "stale|version"):
            maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")
        self.assertTrue((self.root / move["destination"]).exists())

    def test_failed_catalogue_save_rolls_back_native_and_full_retained_set(self):
        published = self.stage()
        before = {entry["path"]: (self.root / entry["path"]).read_bytes() for entry in published}
        policy, move = self.maintenance_setup()
        save = metadata.save_catalog
        calls = []
        def fail_once(*args, **kwargs):
            calls.append(True)
            if len(calls) == 1:
                raise OSError("simulated catalogue write failure")
            return save(*args, **kwargs)
        with mock.patch.object(metadata, "save_catalog", side_effect=fail_once):
            with self.assertRaisesRegex(OSError, "simulated catalogue"):
                maintenance.apply_moves(self.root, [move], policy, {}, backup_fn=lambda *_: "verified")
        self.assertTrue((self.root / move["source"]).exists())
        self.assertFalse((self.root / move["destination"]).exists())
        self.assertIsNotNone(retained.verify_link(self.root, move["source"]))
        for relative, payload in before.items():
            self.assertEqual((self.root / relative).read_bytes(), payload)
        journal = next((self.root / "_reports/runs").glob("reconcile_*.json"))
        self.assertEqual(json.loads(journal.read_text())["status"], "rolled-back")

    def test_stale_native_and_tampered_retained_variant_withhold_links(self):
        self.stage()
        native = self.root / self.destination
        native.write_bytes(b"changed")
        self.assertIsNone(retained.verify_link(self.root, native))
        native.write_bytes(self.selected)
        data = retained.verify_link(self.root, native)
        tone = data["artifactMap"][self.row["variants"]["tone"]["path"]]
        (self.root / tone).write_bytes(b"tampered")
        self.assertIsNone(retained.verify_link(self.root, native))
        with self.assertRaisesRegex(ValueError, "invalid"):
            retained.rename_photo(self.root, native, native.with_name("various_image_123.jpg"))
        self.assertTrue(native.is_file())

    def test_crop_guard_skips_verified_refuses_stale_and_allows_never_prepared(self):
        self.assertFalse(retained.crop_guard(self.root, self.destination, "photo:image_123"))
        self.stage()
        native = self.root / self.destination
        self.assertTrue(retained.crop_guard(self.root, native, "photo:image_123"))
        self.assertTrue(retained.crop_guard(self.root, native))
        native.write_bytes(b"stale prepared bytes")
        with self.assertRaisesRegex(ValueError, "legacy crop refused.*stale"):
            retained.crop_guard(self.root, native, "photo:image_123")
        native.write_bytes(self.selected)
        with self.assertRaisesRegex(ValueError, "legacy crop refused"):
            retained.crop_guard(self.root, native, "photo:image_999")
        other = native.with_name("never_prepared_image_999.jpg")
        other.write_bytes(b"unprepared")
        self.assertFalse(retained.crop_guard(self.root, other, "photo:image_999"))
        with self.assertRaisesRegex(ValueError, "conflicting"):
            retained.crop_guard(self.root, other, "photo:image_123")
        self.assertTrue(retained.source_is_prepared(native))
        self.assertFalse(retained.source_is_prepared(other))
        native.write_bytes(b"changed native")
        with self.assertRaisesRegex(ValueError, "legacy crop refused"):
            retained.source_is_prepared(native)

    def test_manual_review_reject_retire_and_junk_roundtrip_complete_retained_set(self):
        from likeness_library import actions

        (self.root / self.destination).unlink()
        self.destination = "Prospects/Sophie/gallery/sophie_image_123.jpg"
        self.put(self.root, self.destination, self.selected)
        published = self.stage()
        before = {entry["path"]: (self.root / entry["path"]).read_bytes() for entry in published}
        person_id = "person_" + "a" * 32
        initial = {
            "schemaVersion": 1, "actions": [],
            "people": {person_id: {
                "id": person_id, "folder": "Prospects/Sophie", "displayName": "Sophie",
                "folderHistory": [], "identityAnchors": [], "protected": False,
            }},
            "photos": {"photo:image_123": {"contentSha256": sha(self.selected), "protected": False}},
        }
        for action_type in ("sent-to-review", "rejected-to-various", "photo-retired", "photo-junked"):
            with self.subTest(action=action_type):
                catalog = json.loads(json.dumps(initial))
                document = {
                    "manifestVersion": 1, "generatedAt": "2026-10-20T12:00:00Z",
                    "source": "people-gallery-review",
                    "actions": [{
                        "type": action_type, "photoId": "photo:image_123",
                        "contentSha256": sha(self.selected), "sourceBucket": "Gallery",
                        "personFolder": "Prospects/Sophie",
                    }],
                }
                saved = []
                batch, _ = actions.apply_actions(
                    document, self.root, catalog, {}, "Various",
                    backup_fn=lambda *_: "verified", save_fn=lambda value: saved.append(value))
                updated = saved[-1]
                record = updated["actions"][-1]
                self.assertIsNotNone(retained.verify_link(self.root, record["destination"], "photo:image_123"))
                actions.undo_actions(
                    updated, self.root, {}, "Various", batch_id=batch,
                    backup_fn=lambda *_: "verified", save_fn=lambda value: saved.append(value))
                self.assertIsNotNone(retained.verify_link(self.root, self.destination))
                for relative, payload in before.items():
                    self.assertEqual((self.root / relative).read_bytes(), payload)

    def test_manual_photo_save_failure_restores_native_and_retained_bytes(self):
        from likeness_library import actions

        (self.root / self.destination).unlink()
        self.destination = "Prospects/Sophie/gallery/sophie_image_123.jpg"
        self.put(self.root, self.destination, self.selected)
        published = self.stage()
        before = {entry["path"]: (self.root / entry["path"]).read_bytes() for entry in published}
        document = {
            "manifestVersion": 1, "generatedAt": "2026-10-20T12:00:00Z",
            "source": "people-gallery-review", "actions": [{
                "type": "rejected-to-various", "photoId": "photo:image_123",
                "contentSha256": sha(self.selected), "sourceBucket": "Gallery",
                "personFolder": "Prospects/Sophie",
            }],
        }
        catalog = {"schemaVersion": 1, "actions": [], "people": {}, "photos": {}}
        with self.assertRaisesRegex(OSError, "manual catalogue failure"):
            actions.apply_actions(
                document, self.root, catalog, {}, "Various", backup_fn=lambda *_: "verified",
                save_fn=mock.Mock(side_effect=OSError("manual catalogue failure")))
        self.assertTrue((self.root / self.destination).is_file())
        self.assertIsNotNone(retained.verify_link(self.root, self.destination))
        for relative, payload in before.items():
            self.assertEqual((self.root / relative).read_bytes(), payload)

    def test_missing_declared_artifact_and_path_escape_are_refused_before_publication(self):
        self.row["variants"]["tone"]["path"] = "../escape.png"
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse((self.root / "Various/gallery_intake").exists())

    def test_reparse_refusal_and_rename_failure_preserve_original_mapping(self):
        with mock.patch.object(pathlib.Path, "is_symlink", return_value=True):
            with self.assertRaisesRegex(ValueError, "linked"):
                self.stage()
        self.stage()
        before = self.root / self.destination
        after = before.with_name("various_image_123.jpg")
        with mock.patch.object(pathlib.Path, "replace", side_effect=OSError("test replacement failure")):
            with self.assertRaisesRegex(OSError, "test replacement"):
                retained.rename_photo(self.root, before, after)
        self.assertTrue(before.is_file())
        self.assertFalse(after.exists())
        self.assertIsNotNone(retained.verify_link(self.root, before))
        self.assertEqual(list(self.root.rglob("manifest.rename-pending.json")), [])

    def test_artist_general_and_other_artist_isolation(self):
        self.row["source"] = "Artists/Artist A/gallery/incoming_image_123.jpg"
        self.row["sourceScope"]["matchingDomain"] = "Artists/Artist A"
        with self.assertRaises(ValueError):
            self.stage()
        self.destination = "Artists/Artist B/gallery/incoming_image_123.jpg"
        self.put(self.root, self.destination, self.selected)
        with self.assertRaises(ValueError):
            self.stage()
        self.destination = "Artists/Artist A/gallery/incoming_image_123.jpg"
        self.put(self.root, self.destination, self.selected)
        self.stage()
        page = self.root / "_reports/artists"
        index = preparation_provenance.build_index(
            self.root, page, [(self.root / self.destination, "photo:image_123")], "artists")
        self.assertEqual(index.evidence(self.root / self.destination, "photo:image_123")["state"], "verified")
        general = preparation_provenance.build_index(
            self.root, page, [(self.root / self.destination, "photo:image_123")], "general")
        self.assertEqual(general.evidence(self.root / self.destination, "photo:image_123")["matches"], [])

    def test_shared_gallery_index_prioritizes_retained_detail_despite_bad_historical_run(self):
        self.stage()
        self.put(self.root, "_reports/preparation/stale/manifest.json", b"not JSON")
        index = preparation_provenance.build_index(
            self.root, self.root / "_reports/library",
            [(self.root / self.destination, "photo:image_123")])
        evidence = index.evidence(self.root / self.destination, "photo:image_123")
        self.assertEqual(evidence["state"], "verified")
        self.assertIn("gallery_intake", evidence["matches"][0]["href"])
        self.assertIn("Open intake detail", preparation_provenance.render_evidence(evidence))

    def test_housekeeping_keeps_gallery_org_and_backup_retains_all_auxiliary_files(self):
        published = self.stage()
        self.put(self.root, "Various/gallery_944x1104_org/stale.png", b"old derivative")
        with contextlib.redirect_stdout(io.StringIO()):
            originals.archive_old(self.root, [self.root / "Various"], True)
            snapshot = library_backup.create_backup(self.root, stamp="retained-test", apply=True)
        self.assertFalse((self.root / "Various/gallery_944x1104_org").exists())
        self.assertTrue(library_backup.verify_backup(snapshot))
        for entry in published:
            self.assertEqual((snapshot / "work-root" / entry["path"]).read_bytes(),
                             (self.root / entry["path"]).read_bytes())


if __name__ == "__main__":
    unittest.main()
