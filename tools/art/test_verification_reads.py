"""Operation-scoped reuse must finish with full, non-timestamp content checks."""
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
from likeness_library import verification_reads as reads  # noqa: E402


class VerificationReadsTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.source = self.root / "source.bin"
        self.source.write_bytes(b"original")

    def test_hash_reuse_has_one_initial_and_one_final_full_read(self):
        with mock.patch.object(reads, "_digest", wraps=reads._digest) as digest:
            with reads.session(self.root) as proof:
                results = [reads.sha256(self.source) for _ in range(7)]
                self.assertEqual(digest.call_count, 1)
            self.assertEqual(digest.call_count, 2)
        self.assertEqual(len(set(results)), 1)
        self.assertEqual(proof.stats["reusedHashes"], 6)
        self.assertEqual(proof.stats["sealBytes"], len(b"original"))
        self.assertIsNone(reads.active())

    def test_explicit_disposable_staging_skips_second_content_seal_only(self):
        with mock.patch.object(reads, "_digest", wraps=reads._digest) as digest:
            with reads.session(self.root, seal_content=False) as proof:
                reads.sha256(self.source)
                reads.sha256(self.source)
            self.assertEqual(digest.call_count, 1)
            self.assertEqual(proof.stats["sealReads"], 0)
        with self.assertRaisesRegex(ValueError, "unverified write"):
            with reads.session(self.root, seal_content=False):
                reads.sha256(self.source)
                reads.before_write(self.source)
                self.source.write_bytes(b"modified")
        with self.assertRaisesRegex(ValueError, "directory changed"):
            with reads.session(self.root, seal_content=False) as proof:
                proof.children(self.root)
                (self.root / "new.bin").write_bytes(b"new")

    def test_same_size_edit_with_restored_mtime_fails_seal_and_next_operation_is_fresh(self):
        before = self.source.stat()
        with self.assertRaisesRegex(ValueError, "content changed"):
            with reads.session(self.root):
                original = reads.sha256(self.source)
                self.source.write_bytes(b"modified")
                os.utime(self.source, ns=(before.st_atime_ns, before.st_mtime_ns))
                self.assertEqual(reads.sha256(self.source), original)
        with reads.session(self.root):
            self.assertNotEqual(reads.sha256(self.source), original)
        self.assertIsNone(reads.active())

    def test_explicit_write_invalidates_document_and_prepared_then_seals_new_bytes(self):
        self.source.write_text('{"value":1}', encoding="utf-8")
        with reads.session(self.root) as proof:
            reads.document(self.source, 100)
            proof.prepared[self.source] = True
            reads.before_write(self.source)
            self.assertEqual(proof.prepared, {})
            self.source.write_text('{"value":2}', encoding="utf-8")
            self.assertEqual(reads.document(self.source, 100), {"value": 2})
        self.assertEqual(proof.stats["sealReads"], 1)

    def test_write_invalidation_refuses_preexisting_tamper(self):
        with reads.session(self.root):
            reads.sha256(self.source)
            self.source.write_bytes(b"modified")
            with self.assertRaisesRegex(ValueError, "changed before write"):
                reads.before_write(self.source)
            self.source.write_bytes(b"original")

    def test_invalidated_write_requires_new_content_proof_before_seal(self):
        with self.assertRaisesRegex(ValueError, "unverified write"):
            with reads.session(self.root):
                reads.sha256(self.source)
                reads.before_write(self.source)
                self.source.write_bytes(b"modified")

    def test_derivative_mutations_match_uncached_pixels_and_manifest_exactly(self):
        from PIL import Image, ImageDraw
        from likeness_library import derivatives, retained_preparation

        source = self.root / "Prospects/Person/gallery/person_image_123456.png"
        source.parent.mkdir(parents=True)
        image = Image.new("RGB", (900, 1350), "navy")
        ImageDraw.Draw(image).rectangle((270, 150, 540, 1200), fill="orange")
        image.save(source)

        def contents():
            return {path: path.read_bytes() for path in source.parent.parent.rglob("*") if path.is_file()}

        with mock.patch.object(retained_preparation, "_source_is_prepared", return_value=False):
            derivatives.maintain(source, [.2, .1, .2, .2], 100, apply=True)
            baseline = contents()
            derivatives.maintain(source, [.3, .2, .2, .2], 100, apply=True)
            expected = contents()
            for path, payload in baseline.items():
                path.write_bytes(payload)
            with reads.session(self.root) as proof:
                changes, diagnostics = derivatives.maintain(source, [.3, .2, .2, .2], 100, apply=True)
            self.assertTrue(changes)
            self.assertEqual(diagnostics, [])
            self.assertGreater(proof.stats["reusedHashes"], 0)
            self.assertEqual(contents(), expected)

    def test_parsed_manifest_changes_fail_even_if_mtime_is_restored(self):
        self.source.write_text('{"value":1}', encoding="utf-8")
        before = self.source.stat()
        with self.assertRaisesRegex(ValueError, "content changed"):
            with reads.session(self.root):
                self.assertEqual(reads.document(self.source, 100), {"value": 1})
                self.source.write_text('{"value":2}', encoding="utf-8")
                os.utime(self.source, ns=(before.st_atime_ns, before.st_mtime_ns))
                self.assertEqual(reads.document(self.source, 100), {"value": 1})

    def test_added_removed_and_new_empty_owner_directory_fail_seal(self):
        for change in ("add", "remove", "empty"):
            folder = self.root / change
            if change != "empty":
                folder.mkdir()
                (folder / "known").write_bytes(b"known")
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "directory changed"):
                with reads.session(self.root) as proof:
                    proof.children(folder)
                    if change == "add":
                        (folder / "new").write_bytes(b"new")
                    elif change == "remove":
                        (folder / "known").unlink()
                    else:
                        folder.mkdir()

    def test_outside_root_traversal_nested_scope_and_manifest_limit_refused(self):
        with reads.session(self.root):
            for path in (self.root.parent / "outside", self.root / ".." / "outside"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    reads.sha256(path)
            with self.assertRaisesRegex(ValueError, "nested"):
                with reads.session(self.root):
                    pass
            with self.assertRaisesRegex(ValueError, "exceeds"):
                reads.document(self.source, 1)
            self.source.write_text('{"value":1}', encoding="utf-8")
            reads.document(self.source, 100)
            with self.assertRaisesRegex(ValueError, "exceeds"):
                reads.document(self.source, 2)

    def test_owner_entry_type_replacement_with_same_name_fails_seal(self):
        with self.assertRaisesRegex(ValueError, "directory changed"):
            with reads.session(self.root) as proof:
                proof.children(self.root)
                self.source.unlink()
                self.source.mkdir()

    def test_link_at_start_or_inserted_during_operation_is_rejected(self):
        link = self.root / "link"
        try:
            link.symlink_to(self.source)
        except OSError as exc:
            self.skipTest(f"symlink privilege unavailable: {exc}")
        with self.assertRaisesRegex(ValueError, "linked"):
            with reads.session(self.root):
                reads.sha256(link)
        link.unlink()
        with self.assertRaisesRegex(ValueError, "linked"):
            with reads.session(self.root):
                reads.sha256(self.source)
                self.source.unlink()
                self.source.symlink_to(link)

    def test_exception_discards_scope_and_standalone_reads_remain_strict(self):
        with self.assertRaisesRegex(RuntimeError, "stop"):
            with reads.session(self.root):
                reads.sha256(self.source)
                raise RuntimeError("stop")
        self.assertIsNone(reads.active())
        before = reads.sha256(self.source)
        self.source.write_bytes(b"changed")
        self.assertNotEqual(reads.sha256(self.source), before)

    def test_reparse_attribute_is_refused_without_symlink_privilege(self):
        original = pathlib.Path.lstat

        def reparse(path, *args, **kwargs):
            info = original(path, *args, **kwargs)
            if path == self.source:
                return mock.Mock(st_mode=info.st_mode, st_file_attributes=0x400)
            return info

        with mock.patch.object(pathlib.Path, "lstat", reparse):
            with self.assertRaisesRegex(ValueError, "linked"):
                with reads.session(self.root):
                    reads.sha256(self.source)

    def test_json_is_parsed_once_and_rechecked_as_bytes_at_exit(self):
        self.source.write_text('{"value":1}', encoding="utf-8")
        with mock.patch.object(reads.json, "loads", wraps=json.loads) as parse:
            with reads.session(self.root):
                for _ in range(7):
                    self.assertEqual(reads.document(self.source, 100), {"value": 1})
            self.assertEqual(parse.call_count, 1)


if __name__ == "__main__":
    unittest.main()
