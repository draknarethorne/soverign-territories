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
from likeness_library import (
    domains, maintenance, preparation_provenance, retained_preparation as retained,
)  # noqa: E402
from likeness_library import metadata  # noqa: E402
from likeness_library import verification_reads  # noqa: E402
from likeness_library.policy import load_policy  # noqa: E402


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


class RetainedPreparationTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
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
        if getattr(self, "storage_mode", "full") == "lean":
            detail = (self.prep / self.row["detail"]).read_bytes()
            detail += ('<img src="../' + self.row["variants"]["composition"]["path"] + '">').encode()
            self.put(self.prep, self.row["detail"], detail)
            self.row["detailSha256"] = sha(detail)
        return retained.stage_photo(
            self.root, self.destination, self.prep, self.row, recipe={"id": "test-v16"},
            storage_mode=getattr(self, "storage_mode", "full"))

    def test_lean_selected_native_has_no_retained_copy_and_original_differs(self):
        self.storage_mode = "lean"
        published = self.stage()
        data = retained.verify_link(self.root, self.destination)
        self.assertEqual(data["formatVersion"], 2)
        self.assertEqual(data["artifactMap"][self.row["variants"]["composition"]["path"]], self.destination)
        self.assertNotIn(self.destination, [entry["path"] for entry in published])
        self.assertNotEqual(data["original"], self.destination)
        self.assertEqual(sum(entry["sha256"] == sha(self.selected) for entry in published), 0)
        self.assertTrue(retained.source_is_prepared(self.root / self.destination))
        self.test_native_lean_links_survive_rename(data)

    def test_native_lean_links_survive_rename(self, data=None):
        if data is None:
            self.storage_mode = "lean"
            self.stage()
            data = retained.verify_link(self.root, self.destination)
        before = self.root / self.destination
        after = before.with_name("renamed_image_123.jpg")
        retained.rename_photo(self.root, before, after)
        link = retained.verify_link(self.root, after)
        self.assertIsNotNone(link)
        self.assertEqual(link["artifactMap"][self.row["variants"]["composition"]["path"]],
                         after.relative_to(self.root).as_posix())
        self.assertIn("renamed_image_123.jpg", (self.root / link["detail"]).read_text())

    def test_lean_unchanged_original_creates_no_gallery_org_and_undo_is_exact(self):
        self.storage_mode = "lean"
        self.row["processing"].update(final="control", cleanup="control")
        self.row["recommendation"] = {"use": "original"}
        self.selected = self.original
        self.put(self.root, self.destination, self.original)
        self.row["variants"]["composition"]["path"] = self.row["retained"]
        self.row["variants"]["composition"]["sha256"] = self.source_sha
        self.test_cross_owner_move_and_undo_restore_exact_set_manifest_and_hashes()
        data = retained.verify_link(self.root, self.destination)
        self.assertEqual(data["original"], self.destination)
        self.assertFalse((self.root / "Various/gallery_org").exists())

    def test_lean_cross_owner_native_alias_move_and_undo(self):
        self.storage_mode = "lean"
        self.test_cross_owner_move_and_undo_restore_exact_set_manifest_and_hashes()

    def test_lean_native_alias_cannot_escape_to_another_photo(self):
        self.storage_mode = "lean"
        self.stage()
        data = retained.verify_link(self.root, self.destination)
        other = self.put(self.root, "Various/review/other_image_456.jpg", self.selected)
        manifest = self.root / data["manifest"]
        data["artifactMap"][self.row["variants"]["composition"]["path"]] = other.relative_to(self.root).as_posix()
        manifest.write_text(json.dumps({key: value for key, value in data.items() if key != "manifest"}))
        self.assertIsNone(retained.verify_link(self.root, self.destination))

    def test_exact_role_aliases_publish_once_and_keep_all_role_links(self):
        self.row["variants"]["tone"] = dict(self.row["variants"]["denoise"])
        self.stage()
        data = retained.verify_link(self.root, self.destination)
        self.assertIsNotNone(data)
        artifact = self.row["variants"]["denoise"]["path"]
        published = data["artifactMap"][artifact]
        self.assertEqual(sum(entry["path"] == published for entry in data["artifacts"]), 1)
        self.assertEqual(data["row"]["variants"]["tone"], data["row"]["variants"]["denoise"])
        (self.root / published).write_bytes(b"modified shared role")
        self.assertIsNone(retained.verify_link(self.root, self.destination))

    def test_role_aliases_to_original_keep_one_retained_original(self):
        record = self.row["variants"]["tone"]
        record["path"], record["sha256"] = self.row["retained"], self.source_sha
        self.stage()
        data = retained.verify_link(self.root, self.destination)
        self.assertIsNotNone(data)
        self.assertEqual(data["artifactMap"][self.row["retained"]], data["original"])
        self.assertEqual(sum(entry["sha256"] == self.source_sha for entry in data["artifacts"]), 1)

    def test_conflicting_checksums_for_shared_path_refuse_publication(self):
        self.row["variants"]["tone"] = dict(self.row["variants"]["denoise"])
        self.row["variants"]["tone"]["sha256"] = sha(b"different bytes")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            self.stage()
        self.assertFalse(any(self.root.rglob(retained.MANIFEST)))

    def test_exact_aliases_survive_cross_owner_move_and_undo(self):
        self.row["variants"]["tone"] = dict(self.row["variants"]["denoise"])
        self.test_cross_owner_move_and_undo_restore_exact_set_manifest_and_hashes()

    def test_operation_reuse_preserves_lineage_and_reduces_real_content_reads(self):
        self.stage()
        native = self.root / self.destination
        with mock.patch.object(
                verification_reads, "_digest", wraps=verification_reads._digest) as digest:
            expected = []
            for _ in range(7):
                expected.append(retained.verify_link(self.root, native, "photo:image_123"))
                self.assertTrue(retained.source_is_prepared(native))
            strict_reads = digest.call_count
        with mock.patch.object(
                verification_reads, "_digest", wraps=verification_reads._digest) as digest:
            with verification_reads.session(self.root) as proof:
                actual = []
                for _ in range(7):
                    actual.append(retained.verify_link(self.root, native, "photo:image_123"))
                    self.assertTrue(retained.source_is_prepared(native))
            reused_reads = digest.call_count
        self.assertEqual(expected, actual)
        self.assertLess(reused_reads, strict_reads // 3)
        self.assertEqual(proof.stats["directoryScans"], 1)
        self.assertEqual(proof.stats["jsonLoads"], 1)
        self.assertGreater(proof.stats["sealReads"], 0)

    def test_operation_reuse_rejects_artifact_manifest_native_and_new_claim_mutation(self):
        self.stage()
        data = retained.verify_link(self.root, self.destination)
        manifest = self.root / data["manifest"]
        targets = [self.root / self.destination, self.root / data["original"], manifest]
        for target in targets:
            original = target.read_bytes()
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "content changed"):
                with verification_reads.session(self.root):
                    self.assertTrue(retained.source_is_prepared(self.root / self.destination))
                    target.write_bytes(original + b"changed")
                    self.assertTrue(retained.source_is_prepared(self.root / self.destination))
            target.write_bytes(original)
        new_set = manifest.parent.with_name("f" * 32)
        with self.assertRaisesRegex(ValueError, "directory changed"):
            with verification_reads.session(self.root):
                self.assertTrue(retained.source_is_prepared(self.root / self.destination))
                new_set.mkdir()

    def test_operation_reuse_keeps_artist_domain_and_photo_id_checks_separate(self):
        self.stage()
        artist_row = json.loads(json.dumps(self.row))
        artist_row["source"] = "Artists/Example/gallery/incoming_image_123.jpg"
        artist_row["sourceScope"]["matchingDomain"] = "Artists/Example"
        destination = "Artists/Example/review/incoming_image_123.jpg"
        self.put(self.root, destination, self.selected)
        retained.stage_photo(self.root, destination, self.prep, artist_row, recipe={"id": "test-v16"})
        with verification_reads.session(self.root):
            general = retained.verify_link(self.root, self.destination, "photo:image_123")
            artist = retained.verify_link(self.root, destination, "photo:image_123")
            self.assertEqual(general["domain"], "general")
            self.assertEqual(artist["domain"], "Artists/Example")
            self.assertIsNone(retained.verify_link(self.root, destination, "photo:different"))
            self.assertTrue(retained.source_is_prepared(self.root / destination))
            self.assertTrue(retained.source_is_prepared(self.root / self.destination))

    def test_configured_junk_and_retired_roots_preserve_domain_classification(self):
        config = retained.cw.load_cfg()
        config = {
            **config,
            "storageRoots": {
                **config["storageRoots"],
                "junk": "_quarantine",
                "retired": "_retired_custom",
            },
        }
        with mock.patch.object(retained.cw, "load_cfg", return_value=config) as load_config:
            self.assertEqual(
                retained._domain(
                    "_quarantine/Prospects/Example/gallery/image.jpg", self.root
                ),
                "general",
            )
            self.assertEqual(
                retained._domain(
                    "_retired_custom/photos/Artists/Example/gallery/image.jpg", self.root
                ),
                "Artists/Example",
            )
            self.assertEqual(load_config.call_count, 2)
        with mock.patch.object(domains.cw, "load_cfg", return_value=config):
            with domains.activate("artists"):
                self.assertTrue(domains.includes(
                    "_retired_custom/photos/Artists/Example/gallery/image.jpg", self.root
                ))
                self.assertFalse(domains.includes(
                    "_retired_custom/photos/Prospects/Example/gallery/image.jpg", self.root
                ))

    def test_native_domains_do_not_reload_or_resolve_operational_configuration(self):
        with mock.patch.object(
                retained.cw, "load_cfg",
                side_effect=AssertionError("native owner classification must not load configuration")):
            for category in ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Various"):
                with self.subTest(category=category):
                    source = f"{category}/Example/gallery/image.jpg"
                    self.assertEqual(retained._domain(source, self.root), "general")
                    self.assertEqual(retained._owner(source, self.root), f"{category}/Example")
            source = "Artists/Example/gallery/image.jpg"
            self.assertEqual(retained._domain(source, self.root), "Artists/Example")
            self.assertEqual(retained._owner(source, self.root), "Artists/Example")

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

    def test_selective_padding_retains_only_actual_artifacts_and_checks_tampering(self):
        record = self.row["variants"]["eraser-mask"]
        record.pop("padded")
        record.pop("paddedSha256")
        self.stage()
        data = retained.verify_link(self.root, self.destination)
        self.assertIsNotNone(data)
        self.assertEqual(len(data["artifacts"]), 13)
        padded = data["artifactMap"][self.row["variants"]["composition"]["padded"]]
        (self.root / padded).write_bytes(b"tampered padded pixels")
        self.assertIsNone(retained.verify_link(self.root, self.destination))

    def test_original_recommendation_retains_padded_output_and_rewrites_detail_link(self):
        for record in self.row["variants"].values():
            record.pop("padded")
            record.pop("paddedSha256")
        self.row["processing"].update(final="control", cleanup="control")
        self.row["recommendation"] = {"use": "original"}
        self.put(self.root, self.destination, self.original)
        relative = "recommended/original-944x1104.png"
        payload = b"exact padded original bytes"
        self.put(self.prep, relative, payload)
        self.row["recommendedPadded"] = {
            "path": relative, "sha256": sha(payload), "source": self.row["retained"]}
        detail = f'<img src="../{relative}">'.encode()
        self.put(self.prep, self.row["detail"], detail)
        self.row["detailSha256"] = sha(detail)
        self.stage()
        data = retained.verify_link(self.root, self.destination)
        self.assertIsNotNone(data)
        padded = data["artifactMap"][relative]
        self.assertEqual((self.root / padded).read_bytes(), payload)
        self.assertIn(pathlib.PurePosixPath(padded).name, (self.root / data["detail"]).read_text())
        self.assertNotIn("../recommended/", (self.root / data["detail"]).read_text())
        (self.root / padded).write_bytes(b"tampered original padding")
        self.assertIsNone(retained.verify_link(self.root, self.destination))

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
            with self.assertRaisesRegex(ValueError, "linked|reparse point"):
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

    def test_lean_real_snapshot_restore_preserves_native_alias_without_gallery_org(self):
        self.storage_mode = "lean"
        self.row["processing"].update(final="control", cleanup="control")
        self.row["recommendation"] = {"use": "original"}
        self.selected = self.original
        self.put(self.root, self.destination, self.original)
        self.row["variants"]["composition"]["path"] = self.row["retained"]
        self.row["variants"]["composition"]["sha256"] = self.source_sha
        self.stage()
        with contextlib.redirect_stdout(io.StringIO()):
            snapshot = library_backup.create_backup(self.root, stamp="lean-restore", apply=True)
            recovery = library_backup.restore_backup(snapshot, self.base / "restored", apply=True)
        restored = recovery / "work-root"
        self.assertFalse((restored / "Various" / "gallery_org").exists())
        data = retained.verify_link(restored, self.destination)
        self.assertIsNotNone(data)
        self.assertEqual(data["formatVersion"], 2)
        self.assertEqual(data["original"], self.destination)
        self.assertEqual(data["artifactMap"][self.row["variants"]["composition"]["path"]], self.destination)


if __name__ == "__main__":
    unittest.main()
