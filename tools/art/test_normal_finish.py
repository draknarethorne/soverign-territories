"""SIMPLE viewers reuse canonical proof readers without measuring new faces."""
import contextlib
import datetime
import hashlib
import io
import json
import pathlib
import sys
import tempfile
import time
import unittest
from unittest import mock

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
import likeness as api  # noqa: E402
from tools.art import people_gallery  # noqa: E402
from tools.art.likeness_library import normal_finish  # noqa: E402
from likeness_library import (  # noqa: E402
    domains, fast_preparation, preparation_provenance, retained_preparation as retained,
    review_gallery, verification_reads as reads,
)


class FixedDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 11, 17, 12, 0, tzinfo=tz)


class NormalFinishTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="normal-finish-", dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.base = pathlib.Path(temporary.name)
        self.root = self.base / "library"
        self.native = self.root / "Prospects" / "Person" / "gallery" / "person_image_123.jpg"
        self.native.parent.mkdir(parents=True)
        Image.new("RGB", (400, 600), "navy").save(self.native)
        self.cfg = api.cw.load_cfg()
        self.cfg["paths"].update({
            "productionRoot": str(self.root),
            "sandboxWorkingRoot": str(self.base / "Sandbox" / "Working"),
            "inputsRoot": str(self.base / "inputs"),
            "outputRoot": str(self.base / "outputs"),
            "modelCacheRoot": str(self.base / "models"),
        })
        self.cfg.update({
            "installsRoot": str(self.base / "installs"),
            "sharedInput": str(self.base / "shared-input"),
            "sharedOutput": str(self.base / "shared-output"),
            "photos": {},
        })
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        for cw in {api.cw, retained.cw, preparation_provenance.cw}:
            self.stack.enter_context(mock.patch.object(cw, "load_cfg", return_value=self.cfg))
        self.stack.enter_context(mock.patch.object(datetime, "datetime", FixedDateTime))
        self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.stack.enter_context(mock.patch.object(
            api.Embedder, "__call__", side_effect=AssertionError("new face measurement")))
        (self.root / ".likeness-library.json").write_text(json.dumps({
            "schemaVersion": 1, "people": {}, "photos": {}, "actions": [],
        }), encoding="utf-8")
        preparation = self.base / "preparation"
        preparation.mkdir()
        payload = self.native.read_bytes()
        (preparation / "original.jpg").write_bytes(payload)
        detail = b'<a href="original.jpg">Original</a>'
        (preparation / "detail.html").write_bytes(detail)
        row = {
            "source": "Various/gallery/incoming_image_123.jpg", "photoId": "photo:image_123",
            "sourceSha256": hashlib.sha256(payload).hexdigest(),
            "retained": "original.jpg", "detail": "detail.html",
            "detailSha256": hashlib.sha256(detail).hexdigest(),
            "processingProfile": "fast", "processing": {"final": "original", "cleanup": "original"},
            "sourceScope": {"matchingDomain": "general"},
            "outcome": "analysis-only", "variants": {},
        }
        artifacts = retained.stage_photo(
            self.root, self.native.relative_to(self.root).as_posix(), preparation, row,
            recipe=fast_preparation.RECIPE,
        )
        self.retained_original = next(
            self.root / item["path"] for item in artifacts
            if pathlib.PurePosixPath(item["path"]).name == "original.jpg"
        )
        self.cache = api.Cache(self.root / "cache.json")
        digest = self.cache.sha(self.native)
        self.cache.emb[digest] = {"faces": -1, "normalDeferredMeasurement": True}
        self.space = api.Space([
            api.Photo(self.native, "Prospects", "Person", digest, self.cache.emb[digest]),
        ], api.settings(self.cfg))
        self.out = api.cw.storage_root(self.cfg, "reports", root=self.root) / "library"

    def publish(self):
        return normal_finish.viewers(api, self.root, self.cfg, self.space, self.cache, [])

    def test_qualified_entrypoint_shares_session_with_actual_nested_retained_reader(self):
        # Observe both import spellings so the old qualified FAST branch cannot hide.
        from tools.art.likeness_library import retained_preparation as qualified_retained

        observed = []
        sessions = []
        with contextlib.ExitStack() as stack:
            for module in {retained, qualified_retained}:
                original = module._manifests

                def observe(*args, module=module, original=original):
                    observed.append(module.verification_reads.active())
                    return original(*args)

                stack.enter_context(mock.patch.object(module, "_manifests", side_effect=observe))
            validate = reads.ReadSession.validate

            def seal(proof):
                sessions.append(proof)
                return validate(proof)

            stack.enter_context(mock.patch.object(reads.ReadSession, "validate", new=seal))
            paths = self.publish()
        self.assertTrue(observed)
        self.assertTrue(all(proof is not None for proof in observed))
        self.assertEqual(len(sessions), 1)
        self.assertTrue(all(proof is sessions[0] for proof in observed))
        self.assertGreater(sessions[0].stats["reusedHashes"], 0)
        self.assertEqual(sessions[0].stats["sealReads"], len(sessions[0].hashes))
        self.assertEqual(len(paths), 5)
        self.assertTrue(all(pathlib.Path(path).is_file() for path in paths))
        self.assertIsNone(reads.active())

    def test_shared_index_matches_separate_scopes_on_same_input(self):
        context = (self.cfg, self.space.st, self.root, self.cache, self.space)
        arguments = ["--root", str(self.root), "--no-renders"]
        counts = []
        for shared in (False, True):
            with mock.patch.object(
                    preparation_provenance, "build_index",
                    wraps=preparation_provenance.build_index) as index, \
                    mock.patch.object(reads, "_digest", wraps=reads._digest) as digest:
                started = time.perf_counter()
                if shared:
                    self.publish()
                else:
                    self.assertEqual(people_gallery.main(arguments, context=context), 0)
                    self.assertEqual(review_gallery.main(
                        arguments, context=context,
                        embed=lambda _path: {"faces": -1, "normalDeferredMeasurement": True},
                    ), 0)
                counts.append((index.call_count, digest.call_count, time.perf_counter() - started))
            if not shared:
                baseline = {path: path.read_bytes() for path in self.out.rglob("*") if path.is_file()}
        self.assertEqual([row[0] for row in counts], [2, 1])
        self.assertLess(counts[1][1], counts[0][1])
        for path, payload in baseline.items():
            self.assertEqual(path.read_bytes(), payload, str(path))
        # The command-line test runner exposes this bounded, synthetic measurement.
        print(f"normal-finish same-input (indexes, digest calls, seconds): {counts}", file=sys.__stdout__)

    def test_mutation_after_review_is_refused_by_final_independent_seal(self):
        original = review_gallery.main

        def mutate(*args, **kwargs):
            result = original(*args, **kwargs)
            self.retained_original.write_bytes(b"tampered retained original")
            return result

        with mock.patch.object(review_gallery, "main", side_effect=mutate), \
                self.assertRaisesRegex(ValueError, "verification content changed"):
            self.publish()
        self.assertFalse((self.out / "gallery.html").exists())
        self.assertIsNone(reads.active())

    def test_writer_failure_propagates_without_success_fallback(self):
        with mock.patch.object(people_gallery, "main", return_value=1), \
                mock.patch.object(review_gallery, "main") as review, \
                self.assertRaisesRegex(ValueError, "viewer publication failed"):
            self.publish()
        review.assert_not_called()
        self.assertFalse((self.out / "gallery.html").exists())
        with mock.patch.object(people_gallery, "main", side_effect=OSError("report write failed")), \
                self.assertRaisesRegex(OSError, "report write failed"):
            self.publish()
        self.assertIsNone(reads.active())

    def test_held_alias_keeps_diagnostic_and_does_not_inherit_prepared_pixels(self):
        alias = self.native.parent.parent / "review" / "incoming_copy_image_123.jpg"
        alias.parent.mkdir(parents=True)
        Image.new("RGB", (400, 600), "red").save(alias)
        before = alias.read_bytes()
        self.space.photos.append(api.Photo(alias, "Prospects", "Person", self.cache.sha(alias), None))
        self.publish()
        page = (self.out / "people_gallery_review.html").read_text(encoding="utf-8")
        self.assertIn("legacy crop refused:", page)
        self.assertEqual(alias.read_bytes(), before)
        with self.assertRaisesRegex(ValueError, "legacy crop refused:"):
            retained.source_is_prepared(alias)
        self.assertIsNone(reads.active())


if __name__ == "__main__":
    unittest.main()
