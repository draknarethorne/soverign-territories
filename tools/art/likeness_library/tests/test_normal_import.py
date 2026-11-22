import ast
import pathlib
import tempfile
import unittest
import contextlib
import contextvars
import hashlib
import io
import json
import os
import sys
import shutil
from types import SimpleNamespace
from unittest import mock

from tools.art import originals
from tools.art.likeness_library import metadata, normal_import, retained_preparation


ROOT = pathlib.Path(__file__).resolve().parents[4]


class NormalImportTests(unittest.TestCase):
    def setUp(self):
        self.scratch = ROOT / "tmp" / "normal-flow-restoration"
        self.scratch.mkdir(parents=True, exist_ok=True)

    def test_receipt_replacement_retries_transient_lock_and_surfaces_persistent_lock(self):
        from tools.art.likeness_library import report_assets

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            path = pathlib.Path(temporary) / "journal.json"
            path.write_text('{"status": "before"}', encoding="utf-8")
            replace = os.replace
            attempts = []

            def locked_once(source, target):
                attempts.append(source)
                if len(attempts) == 1:
                    raise PermissionError("locked")
                return replace(source, target)

            with mock.patch.object(report_assets.os, "replace", side_effect=locked_once) as attempted, \
                    mock.patch.object(report_assets.time, "sleep"):
                normal_import._write_receipt(path, {"status": "after"})
            self.assertEqual(attempted.call_count, 2)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"status": "after"})
            with mock.patch.object(report_assets.os, "replace", side_effect=PermissionError("locked")), \
                    mock.patch.object(report_assets.time, "sleep"):
                with self.assertRaises(PermissionError):
                    normal_import._write_receipt(path, {"status": "failed"})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"status": "after"})
            self.assertEqual(list(path.parent.glob("*.tmp")), [])

    def test_unprepared_nonvoting_release_stages_native_only_with_bound_hold(self):
        from PIL import Image
        from tools.art.likeness_library import normal_admission, normal_products

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary)
            source = root / "Potentials" / "Former" / "gallery" / "former_image_123.jpg"
            source.parent.mkdir(parents=True)
            Image.new("RGB", (120, 120), "white").save(source)
            digest = metadata.content_sha256(source)
            move = {
                "photoId": "photo:image_123", "source": source.relative_to(root).as_posix(),
                "destination": "Various/review/former_image_123.jpg", "sha256": digest,
                "unpreparedNonVoting": True,
            }
            catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
            photo = SimpleNamespace(name=source.name, box=None, px=0, faces=0)
            routing = {"nonVotingIds": [move["photoId"]]}
            with mock.patch.object(normal_admission, "red_release_routed_catalog",
                                   return_value={"catalog": catalog}):
                normal_products.stage(
                    root, root / "stage", [move], None, profile="lean", photos=[photo],
                    cfg={}, catalog=catalog, policy={}, red_snapshot_candidates=[{}], red_routing_plan=routing,
                )
                target = root / "stage" / pathlib.PurePosixPath(move["destination"])
                self.assertEqual(metadata.content_sha256(target), digest)
                self.assertEqual(metadata.content_sha256(source), digest)
                with self.assertRaisesRegex(ValueError, "neither new preparation nor verified retained lineage"):
                    normal_products.stage(
                        root, root / "refused", [move], None, profile="lean", photos=[photo],
                        cfg={}, catalog=catalog, policy={}, red_snapshot_candidates=[{}],
                        red_routing_plan={"nonVotingIds": []},
                    )

    def test_prepared_history_staging_resolves_lean_alias_without_rewriting_old_detail(self):
        from tools.art.likeness_library import normal_history, retained_preparation, metadata

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary) / "root"
            relative = "Potentials/Owner/gallery/owner_image_123.png"
            native = root / pathlib.PurePosixPath(relative)
            original = root / "_processing" / "Potentials" / "Owner" / ("a" * 32)
            manifest, detail = original / "manifest.json", original / "detail.html"
            native.parent.mkdir(parents=True, exist_ok=True)
            original.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"previous prepared pixels")
            href = os.path.relpath(native, detail.parent).replace(os.sep, "/")
            text = f'<img src="{href}"><script>const old="{href}";</script>'
            detail.write_text(text, encoding="utf-8")
            old = {"current": relative, "detail": detail.relative_to(root).as_posix(), "artifacts": []}
            manifest.write_text(json.dumps(old), encoding="utf-8")
            before = manifest.read_bytes()
            stage = root / "_reports" / "runs" / "normal-batch-prepared-replacement-long-scope" / "publication"
            target = stage / pathlib.PurePosixPath(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"new prepared pixels")
            with mock.patch.object(retained_preparation, "claims_photo", return_value=True), \
                    mock.patch.object(retained_preparation, "verify_link", return_value=old), \
                    mock.patch.object(retained_preparation, "_manifests", return_value=[manifest]), \
                    mock.patch.object(retained_preparation, "_load", return_value=old):
                normal_history.stage(root, stage, [{"photoId": "photo:image_123", "source": "Various/gallery/owner_image_123.png",
                                                  "destination": relative}])
            index = next(stage.rglob(normal_history.INDEX))
            entry = next(iter(json.loads(index.read_text(encoding="utf-8"))["entries"].values()))
            generation = stage / pathlib.PurePosixPath(entry["generations"][0]["native"])
            view = stage / pathlib.PurePosixPath(next(iter(entry["historyViews"].values()))["path"])
            self.assertEqual(generation.read_bytes(), b"previous prepared pixels")
            self.assertNotIn('"' + href + '"', view.read_text(encoding="utf-8"))
            self.assertEqual(detail.read_text(encoding="utf-8"), text)
            self.assertEqual(manifest.read_bytes(), before)
            self.assertEqual(entry["generations"][0]["sha256"], metadata.content_sha256(native))

    def test_fast_prepared_update_retires_only_owned_selected_framings(self):
        from tools.art.likeness_library import normal_products, derivatives, metadata, maintenance

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary)
            owner = root / "Prospects" / "Known"
            native = owner / "gallery" / "known_image_123.png"
            arrival = root / "Various" / "gallery" / "incoming_image_123.png"
            selected = owner / "944x1104" / "head" / "known.png"
            unrelated = owner / "944x1104" / "head" / "other.png"
            for path, payload in ((native, b"old native"), (arrival, b"raw replacement"),
                                  (selected, b"old selected framing"), (unrelated, b"other framing")):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            records = {
                path.relative_to(owner).as_posix(): {
                    "source": source, "sha256": metadata.content_sha256(path),
                }
                for path, source in ((selected, "gallery/known_image_123.png"), (unrelated, "gallery/other_image_456.png"))
            }
            derivatives.save(owner, {"entries": records})
            move = {"photoId": "photo:image_123", "source": arrival.relative_to(root).as_posix(),
                    "destination": native.relative_to(root).as_posix(), "sha256": metadata.content_sha256(arrival)}
            catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
            stage = root / "_reports" / "run" / "publication"
            sentinel = root / "tracked-catalogue-sentinel.json"
            sentinel.write_bytes(b"must never be replaced by publication staging")
            with mock.patch.object(maintenance, "_updated_catalog", return_value=catalog), \
                    mock.patch.object(metadata, "CATALOG_PATH", sentinel):
                _published, _catalog, removed = normal_products.stage(
                    root, stage, [move], None, profile="fast", photos=[], cfg={}, catalog=catalog, policy={},
                )
            self.assertEqual(removed, {selected.relative_to(root).as_posix(): records[selected.relative_to(owner).as_posix()]["sha256"]})
            staged_manifest = derivatives.load(stage / owner.relative_to(root))
            self.assertEqual(set(staged_manifest["entries"]), {unrelated.relative_to(owner).as_posix()})
            self.assertEqual(native.read_bytes(), b"old native")
            self.assertEqual(selected.read_bytes(), b"old selected framing")
            self.assertEqual(sentinel.read_bytes(), b"must never be replaced by publication staging")
            self.assertEqual(metadata.load_catalog(stage / ".likeness-library.json"), catalog)

    def test_history_retirement_preserves_manifests_aliases_and_detects_tampering(self):
        from tools.art.likeness_library import normal_history, metadata

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary)
            owner = root / "_processing" / "Prospects" / "Known"
            native = root / "Prospects" / "Known" / "gallery" / "known_image_123.png"
            previous = owner / "normal-history" / "native-prior.png"
            manifest = owner / ("a" * 64) / "manifest.json"
            detail = manifest.parent / "detail.html"
            history_view = manifest.parent / "history.html"
            for path, payload in (
                (native, b"new"), (previous, b"old"), (detail, b"immutable old detail"),
                (history_view, b"resolved old alias"),
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            manifest.write_text(json.dumps({"artifacts": [{
                "path": detail.relative_to(root).as_posix(), "sha256": metadata.content_sha256(detail),
            }]}), encoding="utf-8")
            index = owner / normal_history.INDEX
            index.write_text(json.dumps({"formatVersion": 1, "entries": {"photo:image_123": {
                "current": native.relative_to(root).as_posix(), "currentSha256": metadata.content_sha256(native),
                "generations": [{"native": previous.relative_to(root).as_posix(), "sha256": metadata.content_sha256(previous)}],
                "retiredManifests": {manifest.relative_to(root).as_posix(): metadata.content_sha256(manifest)},
                "historyViews": {"old": {"path": history_view.relative_to(root).as_posix(), "sha256": metadata.content_sha256(history_view)}},
            }}}), encoding="utf-8")
            self.assertEqual(normal_history.retired(root, owner), {manifest})
            detail.write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "artifact changed"):
                normal_history.retired(root, owner)
            detail.write_bytes(b"immutable old detail")
            native.write_bytes(b"unapproved next generation")
            with self.assertRaisesRegex(ValueError, "current content binding"):
                normal_history.retired(root, owner)

    def test_viewer_out_of_scope_measurement_is_deferred_without_cache_poisoning(self):
        from tools.art.likeness_library import review_gallery

        cache = SimpleNamespace(sha=lambda _path: "unknown", emb={})
        with mock.patch.object(review_gallery.likeness, "Photo") as photo_type:
            result, added = review_gallery._load_photo(
                pathlib.Path("unselected_image_123.png"), "Various", cache,
                lambda _path: {"faces": -1, "normalDeferredMeasurement": True}, {}, None,
            )
        self.assertFalse(added)
        self.assertEqual(cache.emb, {})
        self.assertTrue(result.measurementDeferred)
        photo_type.assert_called_once()

    def test_scoped_consistency_correction_never_moves_existing_or_explicit_update(self):
        import numpy as np
        from tools.art.likeness_library import normal_finish
        from tools.art.likeness_library.policy import load_policy

        vector = np.array([1.0, 0.0])
        source = SimpleNamespace(name="incoming_image_123.png", vec=-vector)
        space = SimpleNamespace(photos=[source], by_key={"Prospects/Known": [None] * 3})
        core = {"vector": vector, "side": "woman", "identityProtected": False,
                "photoScores": {f"existing_image_{i}.png": -0.5 for i in (456, 457, 458)}, "corePhotoIds": set()}
        move = {"photoId": "photo:image_123", "destination": "Prospects/Known/gallery/incoming_image_123.png", "reason": "match"}
        with mock.patch.object(normal_finish, "cores", return_value=({"Prospects/Known": core}, [])):
            checked, audit = normal_finish.check_batch(None, space, {"photos": {}}, load_policy(), [move])
            retained, _audit = normal_finish.check_batch(
                None, space, {"photos": {}}, load_policy(), [move], update_ids=["photo:image_123"],
            )
        self.assertIn("/review/", checked[0]["destination"])
        self.assertEqual(retained, [move])
        self.assertEqual(len(audit["corrections"]), 1)
        self.assertEqual(audit["passCount"], 1)

    def test_offline_preparation_never_attempts_model_download(self):
        from tools.art import image_preparation

        with tempfile.TemporaryDirectory() as temporary:
            with (
                mock.patch.object(image_preparation.models, "folder", return_value=pathlib.Path(temporary)),
                mock.patch.object(image_preparation.models.urllib.request, "urlretrieve") as download,
                image_preparation.models.offline(),
            ):
                with self.assertRaisesRegex(OSError, "offline preparation requires"):
                    image_preparation.models.path("person")
                download.assert_not_called()

    def test_native_replacement_transaction_restores_arrival_owner_and_exact_metadata(self):
        from tools.art.likeness_library import normal_transaction, metadata

        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary).resolve()
            arrival = root / "Various" / "gallery" / "various_image_123456.png"
            owner = root / "Prospects" / "Retained Name" / "gallery" / "owner_image_123456.png"
            catalogue = root / ".likeness-library.json"
            for path, payload in ((arrival, b"new raw"), (owner, b"old original"), (catalogue, b'{"prior":true}\n')):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            stage = root / "_reports" / "run" / "stage"
            target = stage / owner.relative_to(root)
            target.parent.mkdir(parents=True)
            target.write_bytes(b"prepared native")
            (stage / ".likeness-library.json").write_bytes(b'{"updated":true}\n')
            journal = stage.parent / "journal.json"

            def backup(_root, *, apply, scoped_sources):
                folder = root / "_backup" / "proof"
                folder.mkdir(parents=True, exist_ok=True)
                entries = []
                for index, (_label, path) in enumerate(scoped_sources):
                    name = f"{index}.original"
                    shutil.copyfile(path, folder / name)
                    entries.append({
                        "source": str(path), "backup": name, "sha256": metadata.content_sha256(path),
                    })
                (folder / "manifest.json").write_text(json.dumps({"entries": entries}), encoding="utf-8")
                return folder

            with mock.patch("tools.art.library_backup.create_backup", side_effect=backup):
                normal_transaction.publish(
                    root, stage, [arrival.relative_to(root).as_posix(), catalogue.name],
                    journal=journal, bindings={}, profile="lean", run_id="native-proof",
                )
            self.assertEqual(owner.read_bytes(), b"prepared native")
            self.assertFalse(arrival.exists())
            normal_transaction.verify(root, journal)
            normal_transaction.recover(root, journal, apply=False)
            self.assertEqual(owner.read_bytes(), b"prepared native")
            normal_transaction.recover(root, journal, apply=True)
            self.assertEqual(owner.read_bytes(), b"old original")
            self.assertEqual(arrival.read_bytes(), b"new raw")
            self.assertEqual(catalogue.read_bytes(), b'{"prior":true}\n')
            report = root / "_reports" / "library" / "index.html"
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_bytes(b"prior viewer")
            partial_viewer = report.parent / "partial.html"

            def fail_viewer():
                report.write_bytes(b"new viewer")
                partial_viewer.write_bytes(b"partial")
                raise ValueError("injected viewer failure")

            with mock.patch("tools.art.library_backup.create_backup", side_effect=backup):
                with self.assertRaisesRegex(OSError, "rolled-back"):
                    normal_transaction.publish(
                        root, stage, [arrival.relative_to(root).as_posix(), catalogue.name],
                        journal=stage.parent / "viewer-failure.json", bindings={}, profile="lean",
                        run_id="viewer-failure", finalizer=fail_viewer,
                        report_directories=("_reports/library",),
                    )
            self.assertEqual(owner.read_bytes(), b"old original")
            self.assertEqual(arrival.read_bytes(), b"new raw")
            self.assertEqual(report.read_bytes(), b"prior viewer")
            self.assertFalse(partial_viewer.exists())
            original_replace = normal_transaction._replace
            calls = 0

            def fail_second_copy(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected publication failure")
                return original_replace(*args, **kwargs)

            failed_journal = stage.parent / "failed-journal.json"
            with (
                mock.patch("tools.art.library_backup.create_backup", side_effect=backup),
                mock.patch.object(normal_transaction, "_replace", side_effect=fail_second_copy),
            ):
                with self.assertRaisesRegex(OSError, "rolled-back"):
                    normal_transaction.publish(
                        root, stage, [arrival.relative_to(root).as_posix(), catalogue.name],
                        journal=failed_journal, bindings={}, profile="full", run_id="failure-proof",
                    )
            self.assertEqual(owner.read_bytes(), b"old original")
            self.assertEqual(arrival.read_bytes(), b"new raw")
            self.assertEqual(catalogue.read_bytes(), b'{"prior":true}\n')

    def test_recovery_preserves_file_appearing_at_removed_source(self):
        from tools.art.likeness_library import normal_transaction

        for scenario in ("different", "same", "interrupted-created", "interrupted-absent"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
                root = pathlib.Path(temporary).resolve()
                source = root / "source.jpg"
                source.write_bytes(b"original")
                stage = root / "_reports" / "run" / "publication"
                stage.mkdir(parents=True)
                (stage / "hold.jpg").write_bytes(b"original")
                journal = stage.parent / "journal.json"
                normal_transaction.publish(
                    root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                    run_id="recovery-race", exclusive_targets=["hold.jpg"],
                )
                real_replace = normal_transaction._replace

                def race_restore(saved, target, checksum, token=None, *, exclusive=False):
                    if target == source:
                        if scenario in ("different", "same"):
                            source.write_bytes(b"competing file" if scenario == "different" else b"original")
                        elif scenario == "interrupted-absent":
                            raise KeyboardInterrupt("before restoration")
                    real_replace(saved, target, checksum, token, exclusive=exclusive)
                    if target == source and scenario == "interrupted-created":
                        raise KeyboardInterrupt("after restoration")

                error = FileExistsError if scenario in ("different", "same") else KeyboardInterrupt
                with mock.patch.object(normal_transaction, "_replace", side_effect=race_restore):
                    with self.assertRaises(error):
                        normal_transaction.recover(root, journal, apply=True)
                self.assertEqual((root / "hold.jpg").read_bytes(), b"original")
                if scenario == "interrupted-absent":
                    normal_transaction.recover(root, journal, apply=True)
                    self.assertEqual(source.read_bytes(), b"original")
                    self.assertFalse((root / "hold.jpg").exists())
                else:
                    content = b"competing file" if scenario == "different" else b"original"
                    self.assertEqual(source.read_bytes(), content)
                    for apply in (False, True):
                        with self.assertRaisesRegex(ValueError, "ambiguous restored target"):
                            normal_transaction.recover(root, journal, apply=apply)
                        self.assertEqual(source.read_bytes(), content)

    def test_repeat_apply_rejects_different_scope_profile_and_bindings(self):
        receipt = {
            "profile": "lean", "selectedPhotoIds": ["photo:one"],
            "bindings": {"policySHA256": "approved"},
        }
        args = SimpleNamespace(profile="lean", photo_id=["photo:one"])
        normal_import._validate_requested_receipt(receipt, args, receipt["bindings"])
        for changed_args, bindings, message in (
            (SimpleNamespace(profile="full", photo_id=["photo:one"]), receipt["bindings"], "profile"),
            (SimpleNamespace(profile="lean", photo_id=["photo:two"]), receipt["bindings"], "scope"),
            (args, {"policySHA256": "changed"}, "policy"),
        ):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                normal_import._validate_requested_receipt(receipt, changed_args, bindings)

    def test_recovery_refuses_changed_snapshot_manifest(self):
        from tools.art.likeness_library import normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary).resolve()
            source = root / "source.jpg"
            source.write_bytes(b"original")
            other = root / "other.jpg"
            other.write_bytes(b"original")
            stage = root / "_reports" / "run" / "publication"
            stage.mkdir(parents=True)
            (stage / "hold.jpg").write_bytes(b"original")
            journal = stage.parent / "journal.json"
            normal_transaction.publish(
                root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                run_id="manifest-binding", exclusive_targets=["hold.jpg"],
            )
            data = json.loads(journal.read_text(encoding="utf-8"))
            manifest_path = pathlib.Path(data["backup"]) / "manifest.json"
            original_manifest = manifest_path.read_bytes()
            manifest = json.loads(original_manifest)
            manifest["entries"][0]["source"] = str(other)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            for apply in (False, True):
                with self.assertRaisesRegex(ValueError, "snapshot manifest changed"):
                    normal_transaction.recover(root, journal, apply=apply)
                self.assertFalse(source.exists())
                self.assertEqual(other.read_bytes(), b"original")
                self.assertEqual((root / "hold.jpg").read_bytes(), b"original")
            manifest_path.write_bytes(original_manifest)
            normal_transaction.recover(root, journal, apply=True)
            self.assertEqual(source.read_bytes(), b"original")
            self.assertFalse((root / "hold.jpg").exists())

    def test_exclusive_publication_preserves_a_racing_destination(self):
        from tools.art.likeness_library import normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary).resolve()
            source = root / "source.jpg"
            source.write_bytes(b"source")
            stage = root / "_reports" / "run" / "publication"
            stage.mkdir(parents=True)
            (stage / "hold.jpg").write_bytes(b"same bytes")
            destination = root / "hold.jpg"
            journal = stage.parent / "journal.json"
            real_write = normal_transaction.write

            destination.write_bytes(b"existing")
            with self.assertRaisesRegex(ValueError, "exclusive publication target already exists"):
                normal_transaction.publish(
                    root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                    run_id="exclusive-existing", exclusive_targets=["hold.jpg"],
                )
            self.assertEqual(destination.read_bytes(), b"existing")
            destination.unlink()
            with self.assertRaisesRegex(ValueError, "must be staged files"):
                normal_transaction.publish(
                    root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                    run_id="exclusive-invalid", exclusive_targets=["other.jpg"],
                )

            def race(path, data, *, exclusive=False):
                real_write(path, data, exclusive=exclusive)
                if data.get("pendingExclusive") == "hold.jpg" and not destination.exists():
                    destination.write_bytes(b"same bytes")

            with mock.patch.object(normal_transaction, "write", side_effect=race):
                with self.assertRaisesRegex(OSError, "rollback-failed"):
                    normal_transaction.publish(
                        root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                        run_id="exclusive-race", exclusive_targets=["hold.jpg"],
                    )
            self.assertEqual(source.read_bytes(), b"source")
            self.assertEqual(destination.read_bytes(), b"same bytes")
            for apply in (False, True):
                with self.assertRaisesRegex(ValueError, "ambiguous exclusive target"):
                    normal_transaction.recover(root, journal, apply=apply)
                self.assertEqual(destination.read_bytes(), b"same bytes")
            destination.unlink()
            normal_transaction.recover(root, journal, apply=True)
            self.assertEqual(source.read_bytes(), b"source")
            self.assertFalse(destination.exists())

    def test_interrupted_exclusive_publication_requires_inspection(self):
        from tools.art.likeness_library import normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary).resolve()
            source = root / "source.jpg"
            source.write_bytes(b"source")
            stage = root / "_reports" / "run" / "publication"
            stage.mkdir(parents=True)
            (stage / "hold.jpg").write_bytes(b"staged")
            destination = root / "hold.jpg"
            journal = stage.parent / "journal.json"
            real_replace = normal_transaction._replace

            def interrupt(*args, **kwargs):
                real_replace(*args, **kwargs)
                raise KeyboardInterrupt("injected crash after exclusive creation")

            with mock.patch.object(normal_transaction, "_replace", side_effect=interrupt):
                with self.assertRaises(KeyboardInterrupt):
                    normal_transaction.publish(
                        root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                        run_id="exclusive-interruption", exclusive_targets=["hold.jpg"],
                    )
            self.assertEqual(destination.read_bytes(), b"staged")
            with self.assertRaisesRegex(ValueError, "ambiguous exclusive target"):
                normal_transaction.recover(root, journal, apply=True)
            self.assertEqual(destination.read_bytes(), b"staged")
            destination.unlink()
            normal_transaction.recover(root, journal, apply=True)
            self.assertEqual(source.read_bytes(), b"source")

    def test_interrupted_finalizer_preserves_unrecorded_report_outputs(self):
        from tools.art.likeness_library import normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary).resolve()
            source = root / "source.jpg"
            source.write_bytes(b"source")
            stage = root / "_reports" / "run" / "publication"
            stage.mkdir(parents=True)
            (stage / "published.jpg").write_bytes(b"published")
            report = root / "_reports" / "library" / "viewer.html"
            report.parent.mkdir(parents=True)
            report.write_bytes(b"prior viewer")
            journal = stage.parent / "journal.json"
            real_write = normal_transaction.write

            def finish():
                report.write_bytes(b"new viewer")
                return [str(report)]

            def interrupt(path, data, *, exclusive=False):
                if data.get("viewerPaths") and "pendingFinalizer" not in data:
                    raise KeyboardInterrupt("injected crash before finalizer journal update")
                real_write(path, data, exclusive=exclusive)

            with mock.patch.object(normal_transaction, "write", side_effect=interrupt):
                with self.assertRaises(KeyboardInterrupt):
                    normal_transaction.publish(
                        root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                        run_id="viewer-interruption", finalizer=finish,
                        report_directories=("_reports/library",),
                    )
            self.assertEqual(report.read_bytes(), b"new viewer")
            self.assertEqual(json.loads(journal.read_text(encoding="utf-8"))["pendingFinalizer"],
                             ["_reports/library"])
            for apply in (False, True):
                with self.assertRaisesRegex(ValueError, "interrupted viewer finalization"):
                    normal_transaction.recover(root, journal, apply=apply)
                self.assertEqual(report.read_bytes(), b"new viewer")

    def test_external_transaction_rolls_back_and_recovers_exact_bytes(self):
        from tools.art.likeness_library import normal_transaction

        for scenario in (
            "success", "failure", "external-race", "external-interrupted", "external-uncreated",
            "recovery-race", "delete-interrupted", "partial", "newer",
            "removed-reappeared",
            "library-swap", "external-swap",
            "interrupted-recovery", "legacy-journal",
        ):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
                base = pathlib.Path(temporary).resolve()
                root, external = base / "library", base / "workflow"
                stage = root / "_reports" / "run" / "publication"
                staged_external = stage.parent / "external"
                stage.mkdir(parents=True)
                staged_external.mkdir()
                external.mkdir()
                source, destination = root / "original.png", root / "moved.png"
                source.write_bytes(b"native original")
                (stage / destination.name).write_bytes(b"native moved")
                old, new = external / "workflow.json", external / "input.png"
                removed = external / "old-input.png"
                old.write_bytes(b"original workflow")
                removed.write_bytes(b"original input")
                staged_old, staged_new = staged_external / "workflow.json", staged_external / "input.png"
                staged_old.write_bytes(b"updated workflow")
                staged_new.write_bytes(b"new input")
                updates = [
                    {"target": old, "staged": staged_old, "beforeSha256": metadata.content_sha256(old)},
                    {"target": removed, "delete": True, "beforeSha256": metadata.content_sha256(removed)},
                    {"target": new, "staged": staged_new, "beforeSha256": None},
                ]
                journal = stage.parent / "journal.json"
                kwargs = dict(
                    journal=journal, bindings={}, profile="lean", run_id=scenario,
                    external_updates=updates, allowed_external_roots=[external],
                )
                if scenario == "failure":
                    real_replace = normal_transaction._replace

                    def fail_new(source_path, target_path, checksum, token=None, *, exclusive=False):
                        if target_path == new:
                            raise OSError("injected external failure")
                        return real_replace(source_path, target_path, checksum, token, exclusive=exclusive)

                    with mock.patch.object(normal_transaction, "_replace", side_effect=fail_new):
                        with self.assertRaisesRegex(OSError, "rolled-back"):
                            normal_transaction.publish(root, stage, [source.name], **kwargs)
                elif scenario == "external-race":
                    real_replace = normal_transaction._replace

                    def race_new(source_path, target_path, checksum, token=None, *, exclusive=False):
                        if target_path == new:
                            new.write_bytes(b"competing input")
                        return real_replace(source_path, target_path, checksum, token, exclusive=exclusive)

                    with mock.patch.object(normal_transaction, "_replace", side_effect=race_new):
                        with self.assertRaisesRegex(OSError, "rollback-failed"):
                            normal_transaction.publish(root, stage, [source.name], **kwargs)
                    self.assertEqual(new.read_bytes(), b"competing input")
                    for apply in (False, True):
                        with self.assertRaisesRegex(ValueError, "ambiguous external target"):
                            normal_transaction.recover(root, journal, apply=apply, allowed_external_roots=[external])
                    self.assertEqual(new.read_bytes(), b"competing input")
                    continue
                elif scenario in ("external-interrupted", "external-uncreated"):
                    real_replace = normal_transaction._replace

                    def interrupt_new(source_path, target_path, checksum, token=None, *, exclusive=False):
                        if target_path == new and scenario == "external-uncreated":
                            raise KeyboardInterrupt("injected crash before external creation")
                        real_replace(source_path, target_path, checksum, token, exclusive=exclusive)
                        if target_path == new:
                            raise KeyboardInterrupt("injected crash after external creation")

                    with mock.patch.object(normal_transaction, "_replace", side_effect=interrupt_new):
                        with self.assertRaises(KeyboardInterrupt):
                            normal_transaction.publish(root, stage, [source.name], **kwargs)
                    self.assertEqual(json.loads(journal.read_text(encoding="utf-8"))["pendingExternalExclusive"],
                                     str(new))
                    if scenario == "external-interrupted":
                        self.assertEqual(new.read_bytes(), b"new input")
                        with self.assertRaisesRegex(ValueError, "ambiguous external target"):
                            normal_transaction.recover(root, journal, apply=True, allowed_external_roots=[external])
                        self.assertEqual(new.read_bytes(), b"new input")
                        continue
                    self.assertFalse(new.exists())
                    normal_transaction.recover(root, journal, apply=True, allowed_external_roots=[external])
                elif scenario == "delete-interrupted":
                    real_unlink = pathlib.Path.unlink

                    def interrupt_deletion(path, *args, **kwargs):
                        real_unlink(path, *args, **kwargs)
                        if path == removed:
                            raise KeyboardInterrupt("injected crash after external deletion")

                    with mock.patch.object(pathlib.Path, "unlink", interrupt_deletion):
                        with self.assertRaises(KeyboardInterrupt):
                            normal_transaction.publish(root, stage, [source.name], **kwargs)
                    self.assertFalse(removed.exists())
                    self.assertEqual(json.loads(journal.read_text(encoding="utf-8"))["status"], "publishing")
                    normal_transaction.recover(root, journal, apply=False, allowed_external_roots=[external])
                    normal_transaction.recover(root, journal, apply=True, allowed_external_roots=[external])
                else:
                    normal_transaction.publish(root, stage, [source.name], **kwargs)
                    with self.assertRaisesRegex(ValueError, "approved roots"):
                        normal_transaction.verify(root, journal)
                    normal_transaction.verify(root, journal, allowed_external_roots=[external])
                    self.assertEqual(old.read_bytes(), b"updated workflow")
                    self.assertEqual(new.read_bytes(), b"new input")
                    self.assertFalse(removed.exists())
                    if scenario == "removed-reappeared":
                        removed.write_bytes(b"newer input")
                        with self.assertRaisesRegex(ValueError, "removed file reappeared"):
                            normal_transaction.verify(root, journal, allowed_external_roots=[external])
                        with self.assertRaisesRegex(ValueError, "removed file reappeared"):
                            normal_transaction.recover(root, journal, apply=True, allowed_external_roots=[external])
                        self.assertEqual(removed.read_bytes(), b"newer input")
                        continue
                    if scenario == "recovery-race":
                        real_replace = normal_transaction._replace

                        def race_restore(source_path, target_path, checksum, token=None, *, exclusive=False):
                            if target_path == removed:
                                removed.write_bytes(b"competing input")
                            return real_replace(source_path, target_path, checksum, token, exclusive=exclusive)

                        with mock.patch.object(normal_transaction, "_replace", side_effect=race_restore):
                            with self.assertRaises(FileExistsError):
                                normal_transaction.recover(
                                    root, journal, apply=True, allowed_external_roots=[external],
                                )
                        self.assertEqual(removed.read_bytes(), b"competing input")
                        with self.assertRaisesRegex(ValueError, "ambiguous restored target"):
                            normal_transaction.recover(root, journal, apply=True, allowed_external_roots=[external])
                        self.assertEqual(removed.read_bytes(), b"competing input")
                        continue
                    if scenario == "legacy-journal":
                        data = json.loads(journal.read_text(encoding="utf-8"))
                        del data["swapToken"]
                        journal.write_text(json.dumps(data), encoding="utf-8")
                    if scenario in ("partial", "newer"):
                        data = json.loads(journal.read_text(encoding="utf-8"))
                        data["status"] = "publishing"
                        journal.write_text(json.dumps(data), encoding="utf-8")
                        old.write_bytes(b"original workflow" if scenario == "partial" else b"newer edits")
                    if scenario in ("library-swap", "external-swap"):
                        data = json.loads(journal.read_text(encoding="utf-8"))
                        data["status"] = "publishing"
                        journal.write_text(json.dumps(data), encoding="utf-8")
                        target = destination if scenario == "library-swap" else old
                        swap = normal_transaction._swap_path(target, data["swapToken"])
                        swap.write_bytes(b"interrupted partial copy")
                        for apply in (False, True):
                            with self.assertRaisesRegex(ValueError, "interrupted swap"):
                                normal_transaction.recover(
                                    root, journal, apply=apply, allowed_external_roots=[external],
                                )
                        self.assertEqual(swap.read_bytes(), b"interrupted partial copy")
                        self.assertEqual(destination.read_bytes(), b"native moved")
                        self.assertEqual(old.read_bytes(), b"updated workflow")
                        continue
                    if scenario == "newer":
                        for apply in (False, True):
                            with self.assertRaisesRegex(ValueError, "unexpected newer content"):
                                normal_transaction.recover(
                                    root, journal, apply=apply, allowed_external_roots=[external],
                                )
                        self.assertEqual(old.read_bytes(), b"newer edits")
                        self.assertEqual(destination.read_bytes(), b"native moved")
                        continue
                    normal_transaction.recover(root, journal, apply=False, allowed_external_roots=[external])
                    self.assertEqual(destination.read_bytes(), b"native moved")
                    if scenario == "interrupted-recovery":
                        real_replace = normal_transaction._replace
                        calls = 0

                        def interrupt_recovery(*args, **kwargs):
                            nonlocal calls
                            calls += 1
                            if calls == 2:
                                raise OSError("injected recovery interruption")
                            return real_replace(*args, **kwargs)

                        with mock.patch.object(normal_transaction, "_replace", side_effect=interrupt_recovery):
                            with self.assertRaisesRegex(OSError, "injected recovery interruption"):
                                normal_transaction.recover(
                                    root, journal, apply=True, allowed_external_roots=[external],
                                )
                        self.assertEqual(json.loads(journal.read_text(encoding="utf-8"))["status"], "recovering")
                    normal_transaction.recover(root, journal, apply=True, allowed_external_roots=[external])
                self.assertEqual(source.read_bytes(), b"native original")
                self.assertFalse(destination.exists())
                self.assertEqual(old.read_bytes(), b"original workflow")
                self.assertFalse(new.exists())
                self.assertEqual(removed.read_bytes(), b"original input")

    def test_transaction_swap_collision_preserves_existing_file(self):
        from tools.art.likeness_library import normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary)
            source, target = root / "source", root / "target"
            source.write_bytes(b"source")
            swap = normal_transaction._swap_path(target, "a" * 32)
            swap.write_bytes(b"existing")
            with self.assertRaises(FileExistsError):
                normal_transaction._replace(source, target, metadata.content_sha256(source), "a" * 32)
            self.assertEqual(swap.read_bytes(), b"existing")

    def test_publication_preserves_existing_or_racing_journal(self):
        from tools.art.likeness_library import normal_transaction

        for racing in (False, True):
            with self.subTest(racing=racing), tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
                root = pathlib.Path(temporary).resolve()
                stage = root / "_reports" / "run" / "publication"
                stage.mkdir(parents=True)
                source, target = root / "source.png", root / "target.png"
                source.write_bytes(b"source")
                (stage / target.name).write_bytes(b"planned")
                journal = stage.parent / "journal.json"
                existing = b"existing recovery evidence"
                if not racing:
                    journal.write_bytes(existing)
                real_write = normal_transaction.write

                def competing_write(path, data, *, exclusive=False):
                    if exclusive:
                        journal.write_bytes(existing)
                    real_write(path, data, exclusive=exclusive)

                with mock.patch.object(normal_transaction, "write", side_effect=competing_write):
                    with self.assertRaises((ValueError, FileExistsError)):
                        normal_transaction.publish(
                            root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                            run_id="journal-race",
                        )
                self.assertEqual(journal.read_bytes(), existing)
                self.assertEqual(source.read_bytes(), b"source")
                self.assertFalse(target.exists())

    def test_interrupted_initial_journal_preserves_source_and_partial_evidence(self):
        from tools.art.likeness_library import normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary).resolve()
            stage = root / "_reports" / "run" / "publication"
            stage.mkdir(parents=True)
            source, target = root / "source.png", root / "target.png"
            source.write_bytes(b"source")
            (stage / target.name).write_bytes(b"planned")
            journal = stage.parent / "journal.json"

            def interrupted_write(path, data, *, exclusive=False):
                self.assertTrue(exclusive)
                pathlib.Path(path).write_bytes(b'{"kind":')
                raise OSError("interrupted journal write")

            with mock.patch.object(normal_transaction, "write", side_effect=interrupted_write):
                with self.assertRaisesRegex(OSError, "interrupted journal write"):
                    normal_transaction.publish(
                        root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                        run_id="journal-interrupted",
                    )
            self.assertEqual(journal.read_bytes(), b'{"kind":')
            self.assertEqual(source.read_bytes(), b"source")
            self.assertFalse(target.exists())
            with self.assertRaisesRegex(ValueError, "journal is incomplete or invalid"):
                normal_transaction.recover(root, journal, apply=True)
            self.assertEqual(journal.read_bytes(), b'{"kind":')
            with self.assertRaisesRegex(ValueError, "journal already exists"):
                normal_transaction.publish(
                    root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                    run_id="journal-retry",
                )

    def test_publication_refuses_journal_inside_report_outputs(self):
        from tools.art.likeness_library import normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary).resolve()
            stage = root / "_reports" / "run" / "publication"
            stage.mkdir(parents=True)
            source = root / "source.png"
            source.write_bytes(b"source")
            (stage / "target.png").write_bytes(b"planned")
            journal = root / "_reports" / "library" / "journal.json"
            with self.assertRaisesRegex(ValueError, "journal overlaps"):
                normal_transaction.publish(
                    root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                    run_id="overlapping-journal", report_directories=["_reports/library"],
                )
            self.assertEqual(source.read_bytes(), b"source")
            self.assertFalse(journal.exists())
            self.assertFalse((root / "target.png").exists())

    def test_recovery_refuses_file_changed_during_other_file_restoration(self):
        from tools.art.likeness_library import normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary).resolve()
            stage = root / "_reports" / "run" / "publication"
            stage.mkdir(parents=True)
            first, second = root / "a.png", root / "b.png"
            first.write_bytes(b"first before")
            second.write_bytes(b"second before")
            (stage / first.name).write_bytes(b"first after")
            (stage / second.name).write_bytes(b"second after")
            journal = stage.parent / "journal.json"
            normal_transaction.publish(root, stage, [], journal=journal, bindings={}, profile="lean",
                                       run_id="recovery-race")
            real_replace = normal_transaction._replace

            def change_second(source, destination, *args, **kwargs):
                real_replace(source, destination, *args, **kwargs)
                if destination == first:
                    second.write_bytes(b"newer content")

            with mock.patch.object(normal_transaction, "_replace", side_effect=change_second):
                with self.assertRaisesRegex(ValueError, "changed content during restoration"):
                    normal_transaction.recover(root, journal, apply=True)
            self.assertEqual(first.read_bytes(), b"first before")
            self.assertEqual(second.read_bytes(), b"newer content")
            self.assertEqual(json.loads(journal.read_text(encoding="utf-8"))["status"], "recovering")

    def test_publication_refuses_target_changed_after_snapshot(self):
        from tools.art.likeness_library import normal_transaction

        for existed in (False, True):
            with self.subTest(existed=existed), tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
                root = pathlib.Path(temporary).resolve()
                stage = root / "_reports" / "run" / "publication"
                stage.mkdir(parents=True)
                source, target = root / "source.png", root / "target.png"
                source.write_bytes(b"source")
                if existed:
                    target.write_bytes(b"before")
                (stage / target.name).write_bytes(b"planned")
                journal = stage.parent / "journal.json"
                real_write = normal_transaction.write
                injected = False

                def change_target(path, data, *, exclusive=False):
                    nonlocal injected
                    real_write(path, data, exclusive=exclusive)
                    if not injected and data["status"] == "publishing":
                        target.write_bytes(b"newer")
                        injected = True

                with mock.patch.object(normal_transaction, "write", side_effect=change_target):
                    with self.assertRaisesRegex(OSError, "rollback-failed"):
                        normal_transaction.publish(
                            root, stage, [source.name], journal=journal, bindings={}, profile="lean",
                            run_id="target-race",
                        )
                self.assertEqual(target.read_bytes(), b"newer")
                self.assertEqual(source.read_bytes(), b"source")
                self.assertIn("normal target changed during publication",
                              json.loads(journal.read_text(encoding="utf-8"))["error"])
            self.assertFalse(target.exists())

    def test_external_transaction_refuses_stale_or_unapproved_targets_before_publication(self):
        from tools.art.likeness_library import normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            base = pathlib.Path(temporary).resolve()
            root, external = base / "library", base / "workflow"
            stage = root / "_reports" / "run" / "publication"
            staged_external = stage.parent / "external"
            stage.mkdir(parents=True)
            staged_external.mkdir()
            external.mkdir()
            source, target = root / "original.png", external / "workflow.json"
            source.write_bytes(b"native original")
            target.write_bytes(b"current workflow")
            staged = staged_external / "workflow.json"
            staged.write_bytes(b"updated workflow")
            update = {"target": target, "staged": staged, "beforeSha256": "stale"}
            kwargs = dict(
                journal=stage.parent / "journal.json", bindings={}, profile="lean", run_id="stale",
                external_updates=[update], allowed_external_roots=[external],
            )
            with self.assertRaisesRegex(ValueError, "differs from preview"):
                normal_transaction.publish(root, stage, [source.name], **kwargs)
            update["beforeSha256"] = metadata.content_sha256(target)
            kwargs["allowed_external_roots"] = [base / "other"]
            with self.assertRaisesRegex(ValueError, "outside approved roots"):
                normal_transaction.publish(root, stage, [source.name], **kwargs)
            kwargs["allowed_external_roots"] = [external]
            from tools.art import library_backup
            create_backup = library_backup.create_backup

            def change_before_snapshot(*args, **backup_kwargs):
                target.write_bytes(b"edited while snapshot started")
                return create_backup(*args, **backup_kwargs)

            with mock.patch.object(library_backup, "create_backup", side_effect=change_before_snapshot):
                with self.assertRaisesRegex(ValueError, "snapshot differs from preview"):
                    normal_transaction.publish(root, stage, [source.name], **kwargs)
            self.assertEqual(source.read_bytes(), b"native original")
            self.assertEqual(target.read_bytes(), b"edited while snapshot started")
            self.assertFalse(kwargs["journal"].exists())

    def test_current_zero_face_evidence_is_not_missing_inference(self):
        self.assertTrue(normal_import._current_measurement({"faces": 0, "t": 0.1}))
        self.assertTrue(normal_import._current_measurement({"faces": -1, "t": 0.1}))
        self.assertTrue(normal_import._current_measurement({"faces": 1, "v": [0.2, 0.8]}))
        self.assertFalse(normal_import._current_measurement({"faces": 0}))
        self.assertFalse(normal_import._current_measurement(None))

    def test_plan_reuses_unusable_identity_measurement_without_calling_embedder(self):
        from tools.art.likeness_library import metadata

        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            identity = root / "Prospects" / "Existing" / "gallery"
            identity.mkdir(parents=True)
            identity_path = identity / "existing_image_123456.png"
            identity_path.write_bytes(b"cached-zero-face")
            arrival = root / "Various" / "gallery"
            arrival.mkdir(parents=True)
            arrival_path = arrival / "various_unidentified.png"
            arrival_path.write_bytes(b"cached-arrival")
            measurements = {
                hashlib.sha1(identity_path.read_bytes()).hexdigest(): {"faces": 0, "t": 0.1},
                hashlib.sha1(arrival_path.read_bytes()).hexdigest(): {
                    "faces": 1, "v": [0.2, 0.8], "s": 0.5,
                },
            }
            embedder = mock.Mock()
            embedder.side_effect = AssertionError("cached evidence must not infer")
            api = SimpleNamespace(
                domains=SimpleNamespace(
                    CURRENT=contextvars.ContextVar("test-domain", default=None),
                    READ_ONLY=contextvars.ContextVar("test-readonly", default=False),
                ),
                metadata=SimpleNamespace(
                    load_catalog=lambda _path: {"people": {}, "photos": {}},
                    path_for_root=lambda _root: root / ".likeness-library.json",
                    photo_id_from_name=metadata.photo_id_from_name,
                    content_sha256=metadata.content_sha256,
                ),
                rejections=SimpleNamespace(photo_state=lambda *_args: {}),
                configuration=lambda: {},
                cw=SimpleNamespace(
                    photo_folders=lambda *_args: [("Prospects", "Existing", identity.parent)],
                    storage_root=lambda *_args, **_kwargs: root / "_cache",
                ),
                Cache=lambda _path: SimpleNamespace(
                    stat={}, emb=measurements, centering_mean=None,
                ),
                Embedder=lambda: embedder,
                Photo=lambda path, group, name, digest, data: SimpleNamespace(
                    path=path, group=group, name=path.name, key=f"{group}/{name}",
                    vec=data.get("v"),
                ),
                Space=lambda photos, *_args, **_kwargs: SimpleNamespace(photos=photos),
                plan_reconciliation=lambda *_args, **_kwargs: {
                    "assignments": [], "held": [], "clusters": [],
                },
                invent_name=lambda *_args: "unused",
            )
            policy = {"version": "test", "status": "draft", "identityActions": {
                "identityClusterMinimumSimilarity": 0.25, "autoMergeMinimum": 0.55,
            }}
            with (
                mock.patch("tools.art.likeness_library.policy.load_policy", return_value=policy),
                mock.patch("tools.art.likeness_library.policy.effective_settings", return_value={
                    "assign": 0.4, "margin": 0.1, "minCluster": 2,
                }),
                mock.patch(
                    "tools.art.likeness_library.reconciliation.frozen_identity_cores",
                    return_value=({}, set(), []),
                ),
            ):
                report, *_rest = normal_import._plan(
                    api, root, "lean", [], cache_path=root / "cache.json",
                )
            self.assertEqual(report["selectedPhotoIds"], [
                "photo:pic_" + hashlib.sha1(b"cached-arrival").hexdigest()[:8],
            ])
            self.assertEqual(arrival_path.read_bytes(), b"cached-arrival")
            embedder.assert_not_called()

    def test_plain_arrivals_use_original_content_id_and_supported_names_stay_unchanged(self):
        from tools.art import originals
        from tools.art.likeness_library import metadata

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            pool = pathlib.Path(temporary) / "Various" / "gallery"
            pool.mkdir(parents=True)
            plain = pool / "plain.jpg"
            known = pool / "existing_image_123.jpg"
            legacy = pool / "facebook_person_456.jpg"
            plain.write_bytes(b"plain")
            known.write_bytes(b"known")
            legacy.write_bytes(b"legacy")
            rows, older = normal_import._arrival_versions(temporary, [], originals, metadata)
            names = dict(rows)
            self.assertEqual(names[known], known.name)
            self.assertEqual(names[legacy], "various_image_456.jpg")
            self.assertEqual(names[plain], f"various_pic_{hashlib.sha1(b'plain').hexdigest()[:8]}.jpg")
            self.assertEqual(older, [])
            self.assertEqual(plain.read_bytes(), b"plain")
            self.assertFalse((pool / names[plain]).exists())

    def test_incoming_versions_use_unique_newest_original_and_ties_hold(self):
        from tools.art import originals
        from tools.art.likeness_library import metadata

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            pool = pathlib.Path(temporary) / "Various" / "gallery"
            pool.mkdir(parents=True)
            old, new = pool / "old_image_123.jpg", pool / "new_image_123.png"
            old.write_bytes(b"old")
            new.write_bytes(b"new")
            os.utime(old, ns=(1000000000, 1000000000))
            os.utime(new, ns=(2000000000, 2000000000))
            rows, older = normal_import._arrival_versions(temporary, [], originals, metadata)
            self.assertEqual(rows, [(new, new.name)])
            self.assertEqual(older, [("photo:image_123", old, "original", None)])
            os.utime(old, ns=(2000000000, 2000000000))
            with self.assertRaisesRegex(ValueError, "newest-time tie"):
                normal_import._arrival_versions(temporary, [], originals, metadata)
            self.assertTrue(old.exists() and new.exists())

    def test_invalid_prepared_incoming_lineage_holds_without_mutation(self):
        from tools.art import originals
        from tools.art.likeness_library import metadata, retained_preparation

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            pool = pathlib.Path(temporary) / "Various" / "gallery"
            pool.mkdir(parents=True)
            photo = pool / "one_image_123.jpg"
            photo.write_bytes(b"claimed")
            with mock.patch.object(retained_preparation, "claims_photo", return_value=True), \
                    mock.patch.object(retained_preparation, "verify_link", return_value=None):
                with self.assertRaisesRegex(ValueError, "invalid or ambiguous retained incoming lineage"):
                    normal_import._arrival_versions(temporary, [], originals, metadata)
            self.assertEqual(photo.read_bytes(), b"claimed")

    def test_prepared_prior_never_beats_original_and_lineage_recovers(self):
        from tools.art import originals
        from tools.art.likeness_library import metadata, normal_history, normal_transaction, retained_preparation

        for storage_mode in ("full", "lean"):
            with self.subTest(storage_mode=storage_mode), tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
                root = pathlib.Path(temporary).resolve() / "root"
                prep = pathlib.Path(temporary) / "prep"
                old = root / "Various" / "gallery" / "old_image_123.jpg"
                incoming = old.with_name("new_image_123.jpg")
                old.parent.mkdir(parents=True)
                prep.mkdir()
                old.write_bytes(b"old prepared pixels")
                incoming.write_bytes(b"new genuine original")
                os.utime(old, ns=(3000000000, 3000000000))
                os.utime(incoming, ns=(1000000000, 1000000000))
                payloads = {
                    "original.jpg": b"old genuine original",
                    "native.png": b"old prepared pixels",
                    "thumb.jpg": b"thumbnail",
                    "detail.html": b'<html><body><img src="../native.png"></body></html>',
                }
                for name, payload in payloads.items():
                    (prep / name).write_bytes(payload)
                sha = lambda data: hashlib.sha256(data).hexdigest()
                row = {
                    "source": "Various/gallery/old_image_123.jpg", "photoId": "photo:image_123",
                    "sourceSha256": sha(payloads["original.jpg"]), "retained": "original.jpg",
                    "detail": "detail.html", "detailSha256": sha(payloads["detail.html"]),
                    "sourceScope": {"matchingDomain": "general"},
                    "processing": {"final": "composition"},
                    "variants": {"composition": {
                        "path": "native.png", "sha256": sha(payloads["native.png"]),
                        "thumbnail": "thumb.jpg", "thumbnailSha256": sha(payloads["thumb.jpg"]),
                    }},
                }
                retained_preparation.stage_photo(
                    root, old.relative_to(root).as_posix(), prep, row,
                    recipe={"id": "test"}, storage_mode=storage_mode,
                )
                link = retained_preparation.verify_link(root, old, "photo:image_123")
                self.assertIsNotNone(link)
                history_dir = root / "_processing" / "Various"
                generation = history_dir / "normal-history" / "native-before.jpg"
                generation.parent.mkdir(parents=True, exist_ok=True)
                generation.write_bytes(b"even older native")
                index = history_dir / normal_history.INDEX
                index.write_text(json.dumps({"formatVersion": 1, "entries": {"previous": {
                    "current": old.relative_to(root).as_posix(), "currentSha256": metadata.content_sha256(old),
                    "photoId": "photo:image_123",
                    "generations": [{"native": generation.relative_to(root).as_posix(),
                                     "sha256": metadata.content_sha256(generation)}],
                    "retiredManifests": {},
                }}}), encoding="utf-8")
                original_index = index.read_bytes()
                rows, older = normal_import._arrival_versions(root, [], originals, metadata)
                self.assertEqual(rows, [(incoming, incoming.name)])
                self.assertEqual(older[0][:3], ("photo:image_123", old, "prepared"))
                lineage = older[0][3]
                incoming.write_bytes(b"old genuine original")
                rows, _older = normal_import._arrival_versions(root, [], originals, metadata)
                self.assertEqual(rows, [(incoming, incoming.name)])
                incoming.write_bytes(b"new genuine original")

                stage = root / "_reports" / "proof" / "publication"
                stage.mkdir(parents=True)
                prior = {
                    "photoId": "photo:image_123", "source": old.relative_to(root).as_posix(),
                    "sha256": metadata.content_sha256(old), "kind": "prepared", "lineage": lineage,
                }
                manifest = root / pathlib.PurePosixPath(lineage["manifest"])
                manifest_before = manifest.read_bytes()
                manifest.write_bytes(manifest_before + b" ")
                with self.assertRaisesRegex(ValueError, "lineage changed"):
                    normal_import._stage_prepared_prior(root, stage, prior)
                self.assertFalse(any(stage.rglob("*")))
                manifest.write_bytes(manifest_before)
                archived, sources, preserved = normal_import._stage_prepared_prior(root, stage, prior)
                destination = root / pathlib.PurePosixPath(archived["destination"])
                new_relative = "Prospects/Owner/gallery/owner_image_123.jpg"
                new_target = stage / pathlib.PurePosixPath(new_relative)
                new_target.parent.mkdir(parents=True)
                new_target.write_bytes(incoming.read_bytes())
                self.assertTrue(old.exists())
                self.assertTrue(incoming.exists())

                def backup(_root, *, apply, scoped_sources):
                    folder = root / "_backup" / "proof"
                    folder.mkdir(parents=True)
                    entries = []
                    for number, (_label, path) in enumerate(scoped_sources):
                        name = f"{number}.original"
                        shutil.copyfile(path, folder / name)
                        entries.append({"source": str(path), "backup": name, "sha256": metadata.content_sha256(path)})
                    (folder / "manifest.json").write_text(json.dumps({"entries": entries}), encoding="utf-8")
                    return folder

                journal = stage.parent / "journal.json"
                with mock.patch("tools.art.library_backup.create_backup", side_effect=backup):
                    normal_transaction.publish(
                        root, stage, [incoming.relative_to(root).as_posix(), *sources],
                        journal=journal, bindings={}, profile=storage_mode, run_id="proof",
                        expected_sources={**sources, incoming.relative_to(root).as_posix(): metadata.content_sha256(incoming)},
                        preserved_sources=preserved,
                    )
                self.assertEqual((root / pathlib.PurePosixPath(new_relative)).read_bytes(), b"new genuine original")
                self.assertFalse(old.exists())
                verified = retained_preparation.verify_link(root, destination, "photo:image_123")
                self.assertIsNotNone(verified)
                self.assertEqual(verified["sourceSha256"], sha(b"old genuine original"))
                normal_history.retired(root, history_dir)
                self.assertEqual(generation.read_bytes(), b"even older native")
                normal_transaction.recover(root, journal, apply=True)
                self.assertEqual(old.read_bytes(), b"old prepared pixels")
                self.assertEqual(incoming.read_bytes(), b"new genuine original")
                self.assertEqual(index.read_bytes(), original_index)
                self.assertIsNotNone(retained_preparation.verify_link(root, old, "photo:image_123"))
                self.assertFalse(destination.exists())

                from tools.art import likeness
                from tools.art.likeness_library import maintenance, normal_finish

                owner = root / "Prospects" / "Owner" / "gallery" / "owner_image_123.jpg"
                owner.parent.mkdir(parents=True, exist_ok=True)
                owner.write_bytes(b"old owner native")
                catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
                catalog_path = root / ".likeness-library.json"
                catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
                old_row = {
                    "photoId": "photo:image_123", "source": old.relative_to(root).as_posix(),
                    "sha256": metadata.content_sha256(old), "kind": "prepared", "lineage": lineage,
                }
                report = {
                    "assignments": [{"photoId": "photo:image_123", "destination": "Prospects/Owner",
                                     "reason": "content-bound same-photo update"}],
                    "held": [], "clusters": [],
                    "updateTargets": {"photo:image_123": owner.relative_to(root).as_posix()},
                    "updateTargetHashes": {owner.relative_to(root).as_posix(): metadata.content_sha256(owner)},
                    "olderArrivals": [old_row], "sourceHashes": {"photo:image_123": metadata.content_sha256(incoming)},
                    "selectedPhotoIds": ["photo:image_123"], "eligibleIdentityCount": 0,
                    "policyVersion": "test", "policyStatus": "draft", "coreDiagnostics": [],
                    "membershipDiagnostics": [], "implementationSHA256": metadata.content_sha256(pathlib.Path(normal_import.__file__)),
                    "bindings": {},
                }
                cache = SimpleNamespace(stat={}, save=lambda: None)
                photo = SimpleNamespace(path=incoming, name=incoming.name)
                plan = lambda *_args, **_kwargs: (
                    dict(report), [{}], [photo], SimpleNamespace(), catalog,
                    likeness.cw.load_cfg(), {}, cache,
                )

                def backup_main(_root, *, apply, scoped_sources):
                    folder = root / "_backup" / "main-proof"
                    folder.mkdir(parents=True)
                    entries = []
                    for number, (_label, path) in enumerate(scoped_sources):
                        name = f"{number}.original"
                        shutil.copyfile(path, folder / name)
                        entries.append({"source": str(path), "backup": name, "sha256": metadata.content_sha256(path)})
                    (folder / "manifest.json").write_text(json.dumps({"entries": entries}), encoding="utf-8")
                    return folder

                with (
                    mock.patch.object(metadata, "path_for_root", return_value=catalog_path),
                    mock.patch.object(normal_import, "_plan", side_effect=plan),
                    mock.patch.object(maintenance, "require_authorization"),
                    mock.patch.object(maintenance, "_validate_permissions"),
                    mock.patch.object(maintenance, "_updated_catalog", return_value=catalog),
                    mock.patch.object(normal_finish, "check_batch", side_effect=lambda *args, **_kwargs: (args[4], {})),
                    mock.patch.object(normal_finish, "projected", return_value=SimpleNamespace()),
                    mock.patch.object(normal_finish, "family_and_final", return_value={}),
                    mock.patch.object(normal_finish, "viewers", return_value=[]),
                    mock.patch("tools.art.library_backup.create_backup", side_effect=backup_main),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    self.assertEqual(normal_import.main([
                        "--root", str(root), "--profile", "fast", "--run-id", "replace-proof", "--apply",
                    ]), 0)
                    receipt_path = normal_import._receipt_path(root, "replace-proof", likeness.cw.load_cfg())
                    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                    self.assertEqual(owner.read_bytes(), b"new genuine original")
                    archived_path = root / pathlib.PurePosixPath(receipt["olderIncomingVersions"][0]["destination"])
                    self.assertIsNotNone(retained_preparation.verify_link(root, archived_path, "photo:image_123"))
                    normal_transaction.recover(root, receipt["journal"], apply=True)
                self.assertEqual(owner.read_bytes(), b"old owner native")
                self.assertEqual(incoming.read_bytes(), b"new genuine original")
                self.assertEqual(old.read_bytes(), b"old prepared pixels")
                self.assertEqual(index.read_bytes(), original_index)

    def test_auto_update_keeps_owner_and_rejects_short_content_collisions(self):
        from tools.art import originals
        from tools.art.likeness_library import metadata, retained_preparation

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary)
            pool = root / "Various" / "gallery"
            owner_folder = root / "Prospects" / "Owner"
            gallery = owner_folder / "gallery"
            pool.mkdir(parents=True)
            gallery.mkdir(parents=True)
            incoming = pool / "incoming_image_123.jpg"
            owner = gallery / "owner_image_123.jpg"
            incoming.write_bytes(b"new original")
            owner.write_bytes(b"old prepared native")
            os.utime(owner, ns=(3000000000, 3000000000))
            os.utime(incoming, ns=(1000000000, 1000000000))
            measurements = {hashlib.sha1(incoming.read_bytes()).hexdigest(): {"faces": 0, "t": 0.1}}
            api = SimpleNamespace(
                domains=SimpleNamespace(
                    CURRENT=contextvars.ContextVar("test-domain", default=None),
                    READ_ONLY=contextvars.ContextVar("test-readonly", default=False),
                ),
                metadata=SimpleNamespace(
                    load_catalog=lambda _path: {"people": {}, "photos": {}},
                    path_for_root=lambda _root: root / ".likeness-library.json",
                    photo_id_from_name=metadata.photo_id_from_name,
                    content_sha256=metadata.content_sha256,
                ),
                rejections=SimpleNamespace(photo_state=lambda *_args: {}),
                configuration=lambda: {},
                cw=SimpleNamespace(
                    photo_folders=lambda *_args: [("Prospects", "Owner", owner_folder)],
                    storage_root=lambda *_args, **_kwargs: root / "_cache",
                ),
                Cache=lambda _path: SimpleNamespace(stat={}, emb=measurements, centering_mean=None),
                Embedder=lambda: SimpleNamespace(
                    configure_evidence=lambda *_args, **_kwargs: None,
                ),
                Photo=lambda path, group, name, digest, data: SimpleNamespace(
                    path=path, group=group, name=path.name, key=f"{group}/{name}", vec=None,
                ),
                Space=lambda photos, *_args, **_kwargs: SimpleNamespace(photos=photos),
                plan_reconciliation=lambda *_args, **_kwargs: {"assignments": [], "held": [], "clusters": []},
                invent_name=lambda *_args: "unused",
            )
            policy = {"version": "test", "status": "draft", "identityActions": {
                "identityClusterMinimumSimilarity": 0.25, "autoMergeMinimum": 0.55,
            }}
            with (
                mock.patch("tools.art.likeness_library.policy.load_policy", return_value=policy),
                mock.patch("tools.art.likeness_library.policy.effective_settings", return_value={
                    "assign": 0.4, "margin": 0.1, "minCluster": 2,
                }),
                mock.patch("tools.art.likeness_library.reconciliation.frozen_identity_cores",
                           return_value=({}, set(), [])),
                mock.patch.object(retained_preparation, "claims_photo", side_effect=lambda _root, path: path == owner),
                mock.patch.object(retained_preparation, "verify_link", return_value={
                    "sourceSha256": hashlib.sha256(b"old original").hexdigest(),
                }),
            ):
                report, *_ = normal_import._plan(api, root, "fast", [], cache_path=root / "cache")
                self.assertEqual(report["updateTargets"], {
                    "photo:image_123": owner.relative_to(root).as_posix(),
                })
                self.assertEqual(report["sourceHashes"]["photo:image_123"], metadata.content_sha256(incoming))
                protected_catalog = {
                    "people": {}, "photos": {"photo:image_123": {
                        "protected": True, "contentSha256": metadata.content_sha256(owner),
                    }},
                }
                with mock.patch.object(api.metadata, "load_catalog", return_value=protected_catalog):
                    with self.assertRaisesRegex(ValueError, "true photo lock"):
                        normal_import._plan(api, root, "fast", [], cache_path=root / "cache")
                with mock.patch.object(retained_preparation, "verify_link", return_value=None):
                    with self.assertRaisesRegex(ValueError, "invalid retained history"):
                        normal_import._plan(api, root, "fast", [], cache_path=root / "cache")
                with mock.patch.object(api, "configuration", return_value={"photos": {"selected": owner.name}}):
                    with self.assertRaisesRegex(ValueError, "workflow-selected"):
                        normal_import._plan(api, root, "fast", [], cache_path=root / "cache")
                    explicit, *_ = normal_import._plan(
                        api, root, "fast", [], cache_path=root / "cache", update_ids=["photo:image_123"],
                    )
                    self.assertIn("photo:image_123", explicit["updateTargets"])
                owner.rename(gallery / "owner_pic_12345678.jpg")
                incoming.rename(pool / "raw.jpg")
                with mock.patch.object(originals, "content_id", return_value="12345678"):
                    with self.assertRaisesRegex(ValueError, "short content ID collision"):
                        normal_import._plan(api, root, "fast", [], cache_path=root / "cache")

    def test_plain_name_publication_uses_original_bytes_and_recovers(self):
        from tools.art import originals
        from tools.art.likeness_library import maintenance, metadata, normal_products, normal_transaction

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary).resolve()
            source = root / "Various" / "gallery" / "plain.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"original input")
            name = normal_import._arrival_name(source, originals, metadata)
            photo_id = metadata.photo_id_from_name(name)
            photo = SimpleNamespace(path=source, name=name)
            report = {"assignments": [{"photoId": photo_id, "destination": "Potentials/Owner", "reason": "test"}],
                      "held": []}
            moves = maintenance.proposed_moves(report, [photo], root)
            self.assertEqual(moves[0]["destination"], "Potentials/Owner/gallery/" + name)
            stage = root / "_reports" / "proof" / "publication"
            catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
            (root / ".likeness-library.json").write_text(json.dumps(catalog), encoding="utf-8")
            with mock.patch.object(maintenance, "_updated_catalog", return_value=catalog):
                normal_products.stage(root, stage, moves, None, profile="fast",
                                      photos=[photo], cfg={}, catalog=catalog, policy={})
            self.assertTrue(source.exists())
            self.assertEqual((stage / pathlib.PurePosixPath(moves[0]["destination"])).read_bytes(), source.read_bytes())

            def backup(_root, *, apply, scoped_sources):
                folder = root / "_backup" / "proof"
                folder.mkdir(parents=True)
                entries = []
                for index, (_label, path) in enumerate(scoped_sources):
                    name = f"{index}.original"
                    shutil.copyfile(path, folder / name)
                    entries.append({"source": str(path), "backup": name, "sha256": metadata.content_sha256(path)})
                (folder / "manifest.json").write_text(json.dumps({"entries": entries}), encoding="utf-8")
                return folder

            journal = stage.parent / "journal.json"
            with mock.patch("tools.art.library_backup.create_backup", side_effect=backup):
                normal_transaction.publish(root, stage, [moves[0]["source"], ".likeness-library.json"],
                                           journal=journal, bindings={}, profile="fast", run_id="proof")
            self.assertFalse(source.exists())
            self.assertEqual((root / pathlib.PurePosixPath(moves[0]["destination"])).read_bytes(), b"original input")
            normal_transaction.recover(root, journal, apply=True)
            self.assertEqual(source.read_bytes(), b"original input")
            self.assertFalse((root / pathlib.PurePosixPath(moves[0]["destination"])).exists())

    def test_main_normalizes_held_plain_original_transactionally(self):
        from tools.art import likeness, originals
        from tools.art.likeness_library import maintenance, metadata, normal_finish

        with tempfile.TemporaryDirectory(dir=self.scratch) as temporary:
            root = pathlib.Path(temporary).resolve() / "Working"
            source = root / "Various" / "gallery" / "plain.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"held original")
            name = normal_import._arrival_name(source, originals, metadata)
            photo_id = metadata.photo_id_from_name(name)
            target = source.with_name(name)
            catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
            catalog_path = root.parent / "fallback-catalogue.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            fallback_bytes = catalog_path.read_bytes()
            photo = SimpleNamespace(path=source, name=name)
            report = {
                "assignments": [], "held": [{"photoId": photo_id, "reason": "unassigned"}],
                "clusters": [], "updateTargets": {}, "updateTargetHashes": {}, "olderArrivals": [],
                "sourceHashes": {photo_id: metadata.content_sha256(source)},
                "selectedPhotoIds": [photo_id], "eligibleIdentityCount": 0,
                "policyVersion": "test", "policyStatus": "draft",
                "coreDiagnostics": [], "membershipDiagnostics": [],
                "implementationSHA256": metadata.content_sha256(pathlib.Path(normal_import.__file__)),
                "bindings": {},
            }
            cache = SimpleNamespace(save=lambda: None)
            plan = lambda *_args, **_kwargs: (
                dict(report), [{}], [photo], SimpleNamespace(), catalog, {}, {}, cache,
            )

            def backup(_root, *, apply, scoped_sources):
                folder = root / "_backup" / "proof"
                folder.mkdir(parents=True)
                entries = []
                for index, (_label, path) in enumerate(scoped_sources):
                    name = f"{index}.original"
                    shutil.copyfile(path, folder / name)
                    entries.append({"source": str(path), "backup": name, "sha256": metadata.content_sha256(path)})
                (folder / "manifest.json").write_text(json.dumps({"entries": entries}), encoding="utf-8")
                return folder

            with (
                mock.patch.object(likeness.cw, "load_cfg", return_value={}),
                mock.patch.object(likeness.cw, "storage_root", side_effect=lambda _cfg, _key, root: root / "_reports"),
                mock.patch.object(metadata, "CATALOG_PATH", catalog_path),
                mock.patch.object(normal_import, "_plan", side_effect=plan),
                mock.patch.object(maintenance, "require_authorization"),
                mock.patch.object(maintenance, "_validate_permissions"),
                mock.patch.object(normal_finish, "check_batch", return_value=([], {})),
                mock.patch.object(normal_finish, "projected", return_value=SimpleNamespace()),
                mock.patch.object(normal_finish, "family_and_final", return_value={}),
                mock.patch.object(normal_finish, "viewers", return_value=[]),
                mock.patch("tools.art.library_backup.create_backup", side_effect=backup),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                args = ["--root", str(root), "--profile", "fast", "--run-id", "plain-proof"]
                self.assertEqual(normal_import.main(args + ["--dry-run"]), 0)
                self.assertTrue(source.exists())
                self.assertFalse(target.exists())
                self.assertEqual(normal_import.main(args + ["--apply"]), 0)
                self.assertTrue((root / ".likeness-library.json").is_file())
                self.assertEqual(catalog_path.read_bytes(), fallback_bytes)
                self.assertFalse(source.exists())
                self.assertEqual(target.read_bytes(), b"held original")
                receipt = json.loads((root / "_reports" / "runs" / "normal-import-plain-proof.json").read_text())
                self.assertEqual(receipt["normalizations"][0]["photoId"], photo_id)
                from tools.art.likeness_library import normal_transaction
                normal_transaction.recover(root, receipt["journal"], apply=True)
                self.assertEqual(source.read_bytes(), b"held original")
                self.assertFalse(target.exists())
                self.assertFalse((root / ".likeness-library.json").exists())
                self.assertEqual(catalog_path.read_bytes(), fallback_bytes)

    def test_authorization_precedes_persistent_measurement(self):
        api = SimpleNamespace(
            domains=SimpleNamespace(), metadata=SimpleNamespace(), rejections=SimpleNamespace(),
            configuration=lambda: {},
        )
        with (
            mock.patch("tools.art.likeness_library.policy.load_policy", return_value={}),
            mock.patch(
                "tools.art.likeness_library.maintenance.require_authorization",
                side_effect=ValueError("not authorized"),
            ) as authorization,
        ):
            with self.assertRaisesRegex(ValueError, "not authorized"):
                normal_import._plan(api, ROOT, "lean", [], persist_evidence=True)
        authorization.assert_called_once()

    def test_explicit_arrivals_limit_candidates_without_limiting_rivals(self):
        with tempfile.TemporaryDirectory() as temporary:
            pool = pathlib.Path(temporary) / "Various" / "gallery"
            pool.mkdir(parents=True)
            (pool / "one.jpg").write_bytes(b"one")
            (pool / "two.jpg").write_bytes(b"two")

            class Originals:
                @staticmethod
                def images(folder):
                    return sorted(pathlib.Path(folder).glob("*.jpg"))

            class Metadata:
                content_sha256 = staticmethod(lambda source: hashlib.sha256(source.read_bytes()).hexdigest())

                @staticmethod
                def photo_id_from_name(name):
                    return {"one.jpg": "photo:one", "two.jpg": "photo:two"}.get(pathlib.Path(name).name)

            selected = normal_import._selected_arrivals(
                temporary, ["photo:two"], Originals, Metadata,
            )
            self.assertEqual([path.name for path in selected], ["two.jpg"])

    def test_every_profile_passes_the_full_identity_map_to_the_shared_matcher(self):
        calls = []

        class Api:
            @staticmethod
            def plan_reconciliation(candidates, cores, **kwargs):
                calls.append((list(candidates), set(cores), kwargs))
                return {"assignments": [], "held": [], "clusters": []}

            @staticmethod
            def invent_name(seed, taken):
                return seed

        candidates = [{"photoId": "photo:new", "sourceFolder": "Various"}]
        cores = {f"Prospects/person-{index}": {"vector": [1.0]} for index in range(75)}
        settings = {"assign": 0.4, "margin": 0.1, "minCluster": 2}
        policy = {"identityActions": {
            "identityClusterMinimumSimilarity": 0.25,
            "autoMergeMinimum": 0.55,
        }}

        for _profile in ("full", "lean", "fast"):
            normal_import._route_plan(Api, candidates, cores, settings, policy, {"existing"})

        self.assertEqual(len(calls), 3)
        self.assertTrue(all(call[1] == set(cores) for call in calls))
        self.assertTrue(all(call[0] == candidates for call in calls))
        self.assertTrue(all(call[2]["assign"] == 0.4 for call in calls))
        self.assertTrue(all(call[2]["margin"] == 0.1 for call in calls))

    def test_profiles_emit_distinct_evidence_products(self):
        cores = {
            "Prospects/person-1": {
                "corePhotoIds": ["photo:anchor"],
                "mode": "trusted",
                "photoScores": {"photo:anchor": 0.91},
            },
        }
        reports = {}
        for profile in ("full", "lean", "fast"):
            reports[profile] = normal_import._add_profile_evidence({}, cores, profile)

        self.assertIn("fullEvidence", reports["full"])
        self.assertNotIn("evidenceProduct", reports["full"])
        self.assertEqual(
            reports["full"]["fullEvidence"]["Prospects/person-1"]["photoScores"]["photo:anchor"],
            0.91,
        )
        self.assertEqual(
            reports["lean"]["evidenceProduct"],
            "compact selected-arrival plan; unchanged identity evidence reused",
        )
        self.assertIn("current native inputs", reports["lean"]["preparation"])
        self.assertEqual(
            reports["fast"]["evidenceProduct"],
            "original-byte selected-arrival plan; image editing and 944 framing deferred",
        )
        self.assertIn("not certified clean", reports["fast"]["preparation"])

    def test_disabled_gallery_admission_is_held_not_silently_overridden(self):
        moves = [
            {"photoId": "photo:cast", "destination": "Angels/Named/gallery/a.jpg"},
            {"photoId": "photo:new", "destination": "Prospects/New Person/gallery/b.jpg"},
        ]
        policy = {"categoryPolicies": {
            "Angels": {"automaticPhotoRoutingEnabled": False},
            "Prospects": {"automaticPhotoRoutingEnabled": True},
        }}
        permitted, held = normal_import._policy_permitted_moves(moves, policy)
        self.assertEqual([row["photoId"] for row in permitted], ["photo:new"])
        self.assertEqual([row["photoId"] for row in held], ["photo:cast"])

    def test_selected_arrival_refreshes_content_digest_even_when_stat_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "arrival.jpg"
            path.write_bytes(b"first")
            stat = path.stat()
            cache = SimpleNamespace(stat={
                str(path): [stat.st_size, stat.st_mtime_ns, hashlib.sha1(b"first").hexdigest()],
            })
            path.write_bytes(b"other")
            os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))

            digest = normal_import._refresh_content_digest(cache, path)

            self.assertEqual(digest, hashlib.sha1(b"other").hexdigest())
            self.assertEqual(cache.stat[str(path)][2], digest)

    def test_candidate_rows_resolve_measured_photos_by_their_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "various_image_123456.jpg"
            path.write_bytes(b"fixture")
            photo = SimpleNamespace(
                path=path, name=path.name, key="Various/Various", vec=[0.1, 0.9],
            )

            class Metadata:
                @staticmethod
                def photo_id_from_name(_name):
                    return "photo:image_123456"

                @staticmethod
                def content_sha256(source):
                    return hashlib.sha256(source.read_bytes()).hexdigest()

            class Rejections:
                @staticmethod
                def photo_state(_catalog, _photo):
                    return {"rejectedPersonIds": []}

            rows = normal_import._candidate_rows(
                [path], [photo], {}, set(), set(), Metadata, Rejections,
            )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["photoId"], "photo:image_123456")
        self.assertEqual(rows[0]["vector"], [0.1, 0.9])

    def test_batch_backup_is_scoped_to_arrivals_retained_prep_and_catalogue(self):
        root = pathlib.Path("C:/accepted-mini").resolve()
        moves = [{
            "source": "Various/gallery/photo.jpg",
            "destination": "Prospects/New Person/gallery/photo.jpg",
        }]
        transfer = {
            "files": [{"source": "_processing/set/manifest.json"}],
        }
        with (
            mock.patch(
                "tools.art.likeness_library.retained_preparation.plan_transfer",
                return_value=transfer,
            ),
            mock.patch("tools.art.library_backup.create_backup", return_value="verified") as backup,
            mock.patch(
                "tools.art.likeness_library.metadata.path_for_root",
                return_value=root / ".likeness-library.json",
            ),
        ):
            result = normal_import._transaction_backup(root, {}, moves)

        self.assertEqual(result, "verified")
        scoped = backup.call_args.kwargs["scoped_sources"]
        self.assertEqual([label for label, _path in scoped], [
            "arrival-0000", "retained-0000-0000", "likeness-catalogue",
        ])
        self.assertEqual(
            [path for _label, path in scoped],
            [
                root / "Various" / "gallery" / "photo.jpg",
                root / "_processing" / "set" / "manifest.json",
                root / ".likeness-library.json",
            ],
        )

    def test_nonreference_flags_are_reported_without_rewriting_them(self):
        class Metadata:
            @staticmethod
            def photo_id_from_name(_name):
                return "photo:held"

        photo = SimpleNamespace(name="held.jpg", key="Prospects/Example")
        catalog = {"photos": {"photo:held": {
            "membership": {
                "status": "tentative", "coreUse": False, "reason": "experimental withdrawal",
                "referenceVersion": "a" * 64,
            },
            "protected": False,
            "rejectedPersonIds": ["person_human_negative"],
        }}}
        space = SimpleNamespace(photos=[photo])
        before = repr(catalog)
        diagnostic = normal_import._diagnose_membership(catalog, space, Metadata)
        self.assertEqual(len(diagnostic), 1)
        self.assertEqual(diagnostic[0]["status"], "tentative")
        self.assertFalse(diagnostic[0]["coreUse"])
        self.assertIn("person_human_negative", diagnostic[0]["rejectedPersonIds"])
        self.assertIn("not migrated", diagnostic[0]["action"])
        self.assertEqual(repr(catalog), before)

    def test_registered_anchor_without_membership_is_not_a_photo_hard_lock(self):
        photo_id = "photo:image_123456"
        catalog = {"people": {
            "person_0123456789abcdef0123456789abcdef": {
                "identityAnchors": [photo_id],
            },
        }}

        diagnostic = normal_import._membership_details(
            catalog, photo_id, "Angels/Example", {},
        )

        self.assertFalse(diagnostic["membershipHold"])
        self.assertEqual(
            diagnostic["action"],
            "registered identity anchor; content-bound core audit decides eligibility; no blanket photo hard lock",
        )
        self.assertEqual(
            diagnostic["provenanceClassification"],
            "registered identity anchor; no membership provenance",
        )

    def test_normal_module_has_no_experimental_imports(self):
        source = (ROOT / "tools" / "art" / "likeness_library" / "normal_import.py").read_text(
            encoding="utf-8",
        )
        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
        self.assertFalse(any("likeness_experiments" in module for module in imports))
        self.assertFalse(any("directed_reformation" in module for module in imports))

    def test_help_is_available_without_loading_likeness_runtime(self):
        help_text = normal_import._parser().format_help()
        self.assertIn("--profile", help_text)
        self.assertIn("--dry-run", help_text)
        self.assertIn("--check", help_text)

    def test_legacy_help_does_not_import_experimental_reformation(self):
        from tools.art import likeness

        with mock.patch.dict(sys.modules, {"likeness_library.directed_reformation": None}):
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    likeness.main(["--help"])
        self.assertEqual(result.exception.code, 0)

    def test_default_likeness_import_does_not_load_legacy_reconciliation(self):
        import subprocess

        subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; import tools.art.likeness; "
                "assert 'tools.art.likeness_experiments.reconcile_command' not in sys.modules",
            ],
            cwd=ROOT,
            check=True,
        )


PHOTO_ID = "photo:image_123"


class RetainedOriginalIntakeTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name).resolve()
        self.owner = self.root / "Prospects" / "Owner" / "gallery" / "owner_image_123.jpg"
        self.alias = self.root / "Various" / "gallery" / "raw_image_123.jpg"
        for path, data in ((self.owner, b"prepared native"), (self.alias, b"retained raw")):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.catalog = {
            "people": {}, "photos": {PHOTO_ID: {"contentSha256": metadata.content_sha256(self.owner)}},
            "actions": [],
        }
        self.manifest = self.root / "_processing" / "owner-manifest.json"
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_bytes(b"verified manifest")
        self.link = {
            "sourceSha256": metadata.content_sha256(self.alias),
            "manifest": self.manifest.relative_to(self.root).as_posix(),
        }
        self.measurements = {
            hashlib.sha1(self.owner.read_bytes()).hexdigest(): {"faces": 0, "t": 0.1},
            hashlib.sha1(self.alias.read_bytes()).hexdigest(): {"faces": 0, "t": 0.1},
        }
        self.cache = SimpleNamespace(stat={}, emb=self.measurements, centering_mean=None, save=lambda: None)
        self.api = SimpleNamespace(
            domains=SimpleNamespace(
                CURRENT=contextvars.ContextVar("domain", default=None),
                READ_ONLY=contextvars.ContextVar("readonly", default=False),
            ),
            metadata=metadata,
            rejections=SimpleNamespace(photo_state=lambda *_args: {}),
            configuration=lambda: {},
            cw=SimpleNamespace(
                photo_folders=lambda *_args: [("Prospects", "Owner", self.owner.parent.parent)],
                storage_root=lambda *_args, **_kwargs: self.root / "_reports",
                load_cfg=lambda: {},
            ),
            Cache=lambda _path: self.cache,
            cache_path=lambda _args, root: root / "cache",
            Embedder=lambda: SimpleNamespace(configure_evidence=lambda *_args, **_kwargs: None),
            Photo=lambda path, group, name, digest, data: SimpleNamespace(
                path=path, group=group, name=path.name, key=f"{group}/{name}", vec=None,
            ),
            Space=lambda photos, *_args, **_kwargs: SimpleNamespace(photos=photos),
            plan_reconciliation=lambda *_args, **_kwargs: {"assignments": [], "held": [], "clusters": []},
            invent_name=lambda *_args: "unused",
        )
        self.policy = {"version": "test", "status": "draft", "identityActions": {
            "identityClusterMinimumSimilarity": 0.25, "autoMergeMinimum": 0.55,
        }}
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.object(metadata, "load_catalog", side_effect=lambda _path: self.catalog))
        self.stack.enter_context(mock.patch.object(metadata, "path_for_root", side_effect=lambda root: root / ".likeness-library.json"))
        self.stack.enter_context(mock.patch.object(retained_preparation, "claims_photo", side_effect=lambda _root, path: path == self.owner))
        self.stack.enter_context(mock.patch.object(retained_preparation, "verify_link", return_value=self.link))
        self.stack.enter_context(mock.patch("tools.art.likeness_library.policy.load_policy", return_value=self.policy))
        self.stack.enter_context(mock.patch("tools.art.likeness_library.policy.effective_settings", return_value={
            "assign": 0.4, "margin": 0.1, "minCluster": 2,
        }))
        self.stack.enter_context(mock.patch(
            "tools.art.likeness_library.reconciliation.frozen_identity_cores",
            return_value=({}, set(), []),
        ))

    def plan(self, update_ids=()):
        return normal_import._plan(
            self.api, self.root, "fast", [PHOTO_ID], cache_path=self.root / "cache",
            update_ids=update_ids,
        )

    def add_new(self):
        new = self.alias.with_name("new_image_123.png")
        new.write_bytes(b"new genuine original")
        self.measurements[hashlib.sha1(new.read_bytes()).hexdigest()] = {"faces": 0, "t": 0.1}
        return new

    def test_alias_alone_keeps_owner_and_casts_no_vote_even_for_explicit_update(self):
        self.catalog["photos"][PHOTO_ID]["protected"] = True
        report, candidates, photos, space, *_ = self.plan([PHOTO_ID])
        self.assertEqual(report["selectedPhotoIds"], [PHOTO_ID])
        self.assertEqual(report["sourceHashes"], {})
        self.assertEqual(report["updateTargets"], {})
        self.assertEqual(report["olderArrivals"], [])
        self.assertEqual(report["retainedOriginalAliases"], [{
            "photoId": PHOTO_ID, "source": self.alias.relative_to(self.root).as_posix(),
            "sha256": metadata.content_sha256(self.alias),
            "owner": self.owner.relative_to(self.root).as_posix(),
            "ownerSha256": metadata.content_sha256(self.owner),
            "manifest": self.manifest.relative_to(self.root).as_posix(),
            "manifestSha256": metadata.content_sha256(self.manifest),
        }])
        self.assertEqual(candidates, [])
        self.assertEqual(photos, [])
        self.assertEqual([photo.path for photo in space.photos], [self.owner])

    def test_alias_is_not_an_older_arrival_and_genuine_update_still_applies(self):
        import os

        new = self.add_new()
        os.utime(new, ns=(1000000000, 1000000000))
        os.utime(self.alias, ns=(2000000000, 2000000000))
        report, _candidates, photos, *_ = self.plan()
        self.assertEqual([photo.path for photo in photos], [new])
        self.assertEqual(report["updateTargets"], {PHOTO_ID: self.owner.relative_to(self.root).as_posix()})
        self.assertEqual(report["sourceHashes"], {PHOTO_ID: metadata.content_sha256(new)})
        self.assertEqual(report["olderArrivals"], [])
        self.assertEqual(report["retainedOriginalAliases"][0]["source"], self.alias.relative_to(self.root).as_posix())
        self.catalog["photos"][PHOTO_ID]["protected"] = True
        with self.assertRaisesRegex(ValueError, "true photo lock"):
            self.plan()

    def test_invalid_or_stale_owner_binding_never_exempts_original(self):
        with mock.patch.object(retained_preparation, "verify_link", return_value=None):
            with self.assertRaisesRegex(ValueError, "invalid retained history"):
                self.plan()
        self.catalog["photos"][PHOTO_ID]["contentSha256"] = "stale"
        with self.assertRaisesRegex(ValueError, "stale content binding"):
            self.plan()
        self.catalog["photos"][PHOTO_ID]["contentSha256"] = metadata.content_sha256(self.owner)
        self.catalog["people"] = {"other": {"folder": "Prospects/Other", "identityAnchors": [PHOTO_ID]}}
        report, *_ = self.plan()
        self.assertEqual(report["retainedOriginalAliases"], [])
        self.assertIn(PHOTO_ID, report["updateTargets"])

    def test_selection_revalidates_alias_hash_before_publication(self):
        selected, older, aliases, _owners = normal_import._intake_selection(
            self.api, self.root, [PHOTO_ID], originals, metadata, {}, self.catalog,
        )
        self.assertEqual((selected, older), ([], []))
        self.alias.write_bytes(b"changed")
        selected2, older2, aliases2, _owners = normal_import._intake_selection(
            self.api, self.root, [PHOTO_ID], originals, metadata, {}, self.catalog,
        )
        self.assertEqual(selected2, [(self.alias, self.alias.name)])
        self.assertEqual(older2, [])
        self.assertNotEqual(aliases, aliases2)

    def run_apply(self, *, changed_before_publication=False):
        from tools.art import likeness
        import tools.art as art
        from tools.art.likeness_library import maintenance, normal_finish, normal_products, normal_transaction

        preparation = self.root / "preparation"
        preparation.mkdir()
        (preparation / "manifest.json").write_text("{}", encoding="utf-8")
        captured = {}

        def prepare(_root, _run, paths, _profile):
            captured["prepared"] = list(paths)
            return preparation, {"recipe": {}, "photos": [
                {"source": path.relative_to(self.root).as_posix(), "sourceSha256": metadata.content_sha256(path)}
                for path in paths
            ]}, {path.relative_to(self.root).as_posix(): path for path in paths}

        def check_batch(_api, _space, _catalog, _policy, moves, **_kwargs):
            if changed_before_publication:
                self.alias.write_bytes(b"changed")
            return moves, {}

        def publish(_root, _stage, sources, **kwargs):
            captured["sources"] = sources
            captured["preserved"] = kwargs["preserved_sources"]
            captured["expected"] = kwargs["expected_sources"]
            kwargs["finalizer"]()
            return self.root / "journal.json"

        def receipt(_path, data):
            captured["receipt"] = data

        with (
            mock.patch.object(art, "likeness", self.api),
            mock.patch.object(normal_import, "_receipt_path", return_value=self.root / "receipt.json"),
            mock.patch.object(normal_import, "_write_receipt", side_effect=receipt),
            mock.patch.object(normal_import, "_bindings", return_value={}),
            mock.patch.object(maintenance, "require_authorization"),
            mock.patch.object(maintenance, "proposed_moves", return_value=[]),
            mock.patch.object(maintenance, "validate_moves"),
            mock.patch.object(maintenance, "_validate_permissions"),
            mock.patch.object(normal_products, "prepare", side_effect=prepare) as prep,
            mock.patch.object(normal_products, "stage", return_value=([], self.catalog, {})) as stage,
            mock.patch.object(normal_finish, "check_batch", side_effect=check_batch),
            mock.patch.object(normal_finish, "projected", return_value=SimpleNamespace()),
            mock.patch.object(normal_finish, "family_and_final", return_value={}),
            mock.patch.object(normal_finish, "viewers", return_value=[]),
            mock.patch.object(normal_transaction, "publish", side_effect=publish),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            result = normal_import.main([
                "--root", str(self.root), "--profile", "lean", "--run-id", "proof",
                "--photo-id", PHOTO_ID, "--apply",
            ])
        return result, captured, prep, stage

    def test_apply_alias_only_binds_preservation_without_preparing(self):
        result, captured, prep, _stage = self.run_apply()
        self.assertEqual(result, 0)
        prep.assert_not_called()
        relative = self.alias.relative_to(self.root).as_posix()
        self.assertNotIn(relative, captured["sources"])
        self.assertEqual(captured["preserved"], {relative: metadata.content_sha256(self.alias)})
        self.assertEqual(captured["expected"][relative], metadata.content_sha256(self.alias))
        self.assertEqual(captured["expected"][self.owner.relative_to(self.root).as_posix()], metadata.content_sha256(self.owner))
        self.assertEqual(captured["expected"][self.manifest.relative_to(self.root).as_posix()], metadata.content_sha256(self.manifest))
        self.assertEqual(captured["receipt"]["selectedPhotoIds"], [PHOTO_ID])
        self.assertEqual(captured["receipt"]["moves"], [])

    def test_apply_prepares_only_genuine_update_and_preserves_alias(self):
        new = self.add_new()
        result, captured, _prep, _stage = self.run_apply()
        self.assertEqual(result, 0)
        self.assertEqual(captured["prepared"], [new])
        relative = self.alias.relative_to(self.root).as_posix()
        self.assertNotIn(relative, captured["sources"])
        self.assertEqual(captured["preserved"][relative], metadata.content_sha256(self.alias))
        self.assertEqual(captured["receipt"]["olderIncomingVersions"], [])
        self.assertEqual(captured["receipt"]["moves"][0]["source"], new.relative_to(self.root).as_posix())

    def test_apply_stops_if_preserved_alias_changes_after_plan(self):
        self.add_new()
        result, _captured, _prep, stage = self.run_apply(changed_before_publication=True)
        self.assertEqual(result, 1)
        stage.assert_not_called()

    def test_published_alias_is_checked_against_receipt_and_detects_tampering(self):
        from tools.art.likeness_library import normal_transaction

        result, captured, _prep, _stage = self.run_apply()
        self.assertEqual(result, 0)
        stage = self.root / "transaction" / "stage"
        stage.mkdir(parents=True)

        def backup(_root, *, apply, scoped_sources):
            folder = self.root / "backup"
            folder.mkdir()
            entries = []
            for number, (_label, path) in enumerate(scoped_sources):
                name = str(number)
                shutil.copyfile(path, folder / name)
                entries.append({"source": str(path), "backup": name, "sha256": metadata.content_sha256(path)})
            (folder / "manifest.json").write_text(json.dumps({"entries": entries}), encoding="utf-8")
            return folder

        journal = self.root / "transaction" / "journal.json"
        with mock.patch("tools.art.library_backup.create_backup", side_effect=backup):
            normal_transaction.publish(
                self.root, stage, [], journal=journal, bindings={}, profile="lean", run_id="proof",
                expected_sources=captured["expected"], preserved_sources=captured["preserved"],
            )
        receipt = captured["receipt"]
        receipt["journal"] = str(journal)
        path = self.root / "actual-receipt.json"
        normal_import._write_receipt(path, receipt)
        normal_import._check_receipt(self.root, path)
        import tools.art as art

        with (
            mock.patch.object(art, "likeness", self.api),
            mock.patch.object(normal_import, "_receipt_path", return_value=path),
            mock.patch.object(normal_import, "_bindings", return_value={}),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            args = ["--root", str(self.root), "--profile", "lean", "--run-id", "proof", "--apply"]
            self.assertEqual(normal_import.main(args), 0)
            self.assertEqual(normal_import.main(args + ["--photo-id", PHOTO_ID]), 0)
        self.alias.write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "published content changed"):
            normal_import._check_receipt(self.root, path)


class VerifiedRetainedOriginalTests(unittest.TestCase):
    def test_real_retained_link_is_required_for_alias_classification(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            root = pathlib.Path(temporary).resolve() / "root"
            prep = pathlib.Path(temporary) / "prep"
            prep.mkdir()
            owner = root / "Prospects" / "Owner" / "gallery" / "owner_image_123.jpg"
            alias = root / "Various" / "gallery" / "raw_image_123.jpg"
            for path, data in ((owner, b"native pixels"), (alias, b"raw original")):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            payloads = {
                "original.jpg": b"raw original", "native.png": b"native pixels",
                "thumb.jpg": b"thumbnail", "detail.html": b"<html>detail</html>",
            }
            for name, data in payloads.items():
                (prep / name).write_bytes(data)
            sha = lambda data: hashlib.sha256(data).hexdigest()
            row = {
                "source": "Various/gallery/raw_image_123.jpg", "photoId": PHOTO_ID,
                "sourceSha256": sha(payloads["original.jpg"]), "retained": "original.jpg",
                "detail": "detail.html", "detailSha256": sha(payloads["detail.html"]),
                "sourceScope": {"matchingDomain": "general"},
                "processing": {"final": "composition"},
                "variants": {"composition": {
                    "path": "native.png", "sha256": sha(payloads["native.png"]),
                    "thumbnail": "thumb.jpg", "thumbnailSha256": sha(payloads["thumb.jpg"]),
                }},
            }
            retained_preparation.stage_photo(
                root, owner.relative_to(root).as_posix(), prep, row,
                recipe={"id": "test"}, storage_mode="lean",
            )
            link = retained_preparation.verify_link(root, owner, PHOTO_ID)
            self.assertIsNotNone(link)
            catalog = {"people": {}, "photos": {PHOTO_ID: {"contentSha256": metadata.content_sha256(owner)}}}
            api = SimpleNamespace(cw=SimpleNamespace(
                photo_folders=lambda *_args: [("Prospects", "Owner", owner.parent.parent)],
            ))
            selected, older, aliases, _owners = normal_import._intake_selection(
                api, root, [PHOTO_ID], originals, metadata, {}, catalog,
            )
            self.assertEqual((selected, older), ([], []))
            self.assertEqual(aliases[0]["sha256"], metadata.content_sha256(alias))
            (root / pathlib.PurePosixPath(link["original"])).write_bytes(b"tampered history")
            with self.assertRaisesRegex(ValueError, "invalid retained history"):
                normal_import._intake_selection(api, root, [PHOTO_ID], originals, metadata, {}, catalog)
            self.assertEqual(alias.read_bytes(), b"raw original")
            self.assertEqual(owner.read_bytes(), b"native pixels")


if __name__ == "__main__":
    unittest.main()
