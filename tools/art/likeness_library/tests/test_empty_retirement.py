"""Synthetic-only tests for explicit, journalled whole-folder retirement."""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from tools.art.likeness_library import empty_retirement as retirement, normal_transaction


ROOT = pathlib.Path(__file__).resolve().parents[4]


@unittest.skipUnless(os.name == "nt", "exclusive Windows directory rename")
class EmptyRetirementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "tmp")
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name) / "Sovereign Territories Sandbox" / "Working"
        self.root.mkdir(parents=True)
        self.predecessor = "_reports/runs/previous.json"
        self.source_receipt = "_reports/runs/rebase.json"
        self.journal = "_reports/runs/retirement.json"
        (self.root / "_reports/runs").mkdir(parents=True)
        (self.root / "_retired/Potentials").mkdir(parents=True)
        self.folders = ["Potentials/Alpha", "Potentials/Beta"]
        self.rows = []
        after = {}
        for folder in self.folders:
            path = self.root / folder
            (path / "gallery").mkdir(parents=True)
            (path / "review").mkdir()
            (path / "gallery_944x1104" / "empty").mkdir(parents=True)
            (path / "gallery" / "z_identity.txt").write_bytes(b"identity history\r\n")
            derivative = path / "gallery_944x1104" / "derivative.jpg"
            derivative.write_bytes(folder.encode())
            after[derivative.relative_to(self.root).as_posix()] = hashlib.sha256(derivative.read_bytes()).hexdigest()
            self.rows.append({"owner": folder, "source": folder + "/gallery/old.jpg",
                              "sourceHash": "1" * 64})
        unrelated = self.root / "Potentials/Unrelated"
        (unrelated / "gallery").mkdir(parents=True)
        self.unrelated = unrelated
        untouched = self.root / "untouched.txt"
        untouched.write_bytes(b"previous output")
        after["untouched.txt"] = hashlib.sha256(untouched.read_bytes()).hexdigest()
        (self.root / self.predecessor).write_text(json.dumps({
            "kind": "normal-publication", "status": "applied", "root": str(self.root),
            "after": after, "removed": ["old-removed.jpg"],
        }), encoding="utf-8")
        hashes = {row["source"]: row["sourceHash"] for row in self.rows}
        (self.root / self.source_receipt).write_text(json.dumps({
            "kind": "normal-rebase-receipt", "schemaVersion": 1, "status": "applied",
            "root": str(self.root), "sourceHashes": hashes,
            "plan": {"sourceRows": self.rows, "sourceHashes": hashes},
        }), encoding="utf-8")
        self.cfg = {}
        # Windows can briefly report transient attributes immediately after mkdir.
        time.sleep(0.1)

    def preview(self):
        # A newly-created Windows directory can briefly expose a changing
        # internal attribute; the transaction must refuse it rather than hide it.
        for attempt in range(5):
            try:
                return retirement.preview(self.root, self.folders, self.source_receipt, self.predecessor, cfg=self.cfg)
            except ValueError as exc:
                if "attributes=268435472/16" not in str(exc) or attempt == 4:
                    raise
                time.sleep(0.1)

    def publish(self):
        plan, digest = self.preview()
        retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        return plan, digest

    def test_explicit_preview_binds_sources_and_excludes_unrelated(self):
        plan, digest = self.preview()
        self.assertEqual(len(plan["moves"]), 2)
        self.assertEqual(len(plan["predecessorMapping"]), 2)
        self.assertTrue(self.unrelated.is_dir())
        self.assertFalse((self.root / self.journal).exists())
        self.assertEqual(len(digest), 64)
        with self.assertRaisesRegex(ValueError, "source row"):
            retirement.preview(self.root, self.folders + ["Potentials/Unrelated"], self.source_receipt,
                               self.predecessor, cfg=self.cfg)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            retirement.preview(self.root, [self.folders[0], self.folders[0]], self.source_receipt,
                               self.predecessor, cfg=self.cfg)

    def test_successor_check_and_exact_recovery(self):
        plan, digest = self.publish()
        self.assertEqual(retirement.check(self.root, self.journal, digest)["status"], "applied")
        with self.assertRaisesRegex(ValueError, "published content changed"):
            normal_transaction.verify(self.root, self.root / self.predecessor)
        self.assertTrue(self.unrelated.is_dir())
        for move in plan["moves"]:
            self.assertFalse((self.root / move["source"]).exists())
            self.assertTrue((self.root / move["destination"] / "gallery_944x1104" / "empty").is_dir())
            self.assertEqual((self.root / move["destination"] / "gallery/z_identity.txt").read_bytes(),
                             b"identity history\r\n")
        self.assertEqual(retirement.recover(self.root, self.journal, digest), ["destination"] * 2)
        self.assertEqual(retirement.recover(self.root, self.journal, digest, apply=True), ["source"] * 2)
        normal_transaction.verify(self.root, self.root / self.predecessor)
        with self.assertRaisesRegex(ValueError, "already recovered"):
            retirement.recover(self.root, self.journal, digest)

    def successor_fixture(self):
        from tools.art.likeness_library import normal_rebase

        predecessor_path = self.root / self.predecessor
        previous = json.loads(predecessor_path.read_bytes())
        previous.update(runId="corrected", bindings={"policy": "bound"})
        predecessor_path.write_text(json.dumps(previous), encoding="utf-8")
        rows, moves, native, review = [], [], [], []
        for index, row in enumerate(self.rows):
            payload = f"original-{index}".encode()
            source_hash = hashlib.sha256(payload).hexdigest()
            destination = f"Various/review/{index}.jpg"
            target = self.root / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            rows.append({**row, "sourceHash": source_hash, "photoId": f"p{index}"})
            moves.append({"source": row["source"], "destination": destination,
                          "sha256": source_hash, "photoId": f"p{index}"})
            native.append({"native": destination, "sha256": source_hash})
            review.append({"folder": "Various", "bucket": "Review", "name": f"{index}.jpg",
                           "photoId": f"p{index}", "contentSha256": source_hash})
        unchanged = self.root / "Various/gallery/unchanged.jpg"
        unchanged.parent.mkdir(parents=True)
        unchanged.write_bytes(b"untouched original")
        unchanged_hash = hashlib.sha256(unchanged.read_bytes()).hexdigest()
        rows.append({"owner": "Various", "source": "Various/gallery/unchanged.jpg",
                     "sourceHash": unchanged_hash, "photoId": "unchanged"})
        review.append({"folder": "Various", "bucket": "Gallery", "name": "unchanged.jpg",
                       "photoId": "unchanged", "contentSha256": unchanged_hash})
        viewer = self.root / "_reports/library/corrected/people_gallery_review.html"
        viewer.parent.mkdir(parents=True)
        viewer.write_text('<script id="review-data">' + json.dumps(review) + "</script>", encoding="utf-8")
        hashes = {row["source"]: row["sourceHash"] for row in rows}
        receipt = self.root / self.source_receipt
        receipt.write_text(json.dumps({
            "kind": "normal-rebase-receipt", "schemaVersion": 1, "status": "applied",
            "root": str(self.root), "runId": "corrected", "bindings": previous["bindings"],
            "journal": str(predecessor_path), "sourceHashes": hashes,
            "implementationSHA256": hashlib.sha256(pathlib.Path(normal_rebase.__file__).read_bytes()).hexdigest(),
            "viewerPaths": [str(viewer)], "moves": moves, "publishedNative": native,
            "plan": {"sourceRows": rows, "sourceHashes": hashes, "moves": moves},
        }), encoding="utf-8")
        return receipt, unchanged

    def test_explicit_successor_verifies_originals_and_recovery(self):
        receipt, unchanged = self.successor_fixture()
        plan, digest = self.publish()
        retirement.verify_successor(self.root, self.journal, digest, receipt)
        unchanged.write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "original missing or changed"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)
        unchanged.unlink()
        with self.assertRaisesRegex(ValueError, "original missing or changed"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)
        unchanged.write_bytes(b"untouched original")
        target = self.root / plan["moves"][0]["destination"] / "gallery_944x1104/derivative.jpg"
        target.unlink()
        with self.assertRaisesRegex(ValueError, "inventory changed"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)

    def test_successor_refuses_unbound_receipt_and_recovered_journal(self):
        receipt, _ = self.successor_fixture()
        _, digest = self.publish()
        other = self.root / "_reports/runs/other.json"
        other.write_bytes(receipt.read_bytes())
        with self.assertRaisesRegex(ValueError, "another rebase receipt"):
            retirement.verify_successor(self.root, self.journal, digest, other)
        retirement.recover(self.root, self.journal, digest, apply=True)
        with self.assertRaisesRegex(ValueError, "not fully applied"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)

    def distinct_receipts(self):
        source, _ = self.successor_fixture()
        corrected = self.root / "_reports/runs/corrected.json"
        data = json.loads(source.read_bytes())
        data["plan"]["releaseLineage"] = {
            "receipt": str(source), "inputs": {"receiptSHA256": hashlib.sha256(source.read_bytes()).hexdigest()},
        }
        corrected.write_text(json.dumps(data), encoding="utf-8")
        return source, corrected

    def test_distinct_source_and_corrected_receipts_bind_preview_apply_check_and_recovery(self):
        source, corrected = self.distinct_receipts()
        corrected_relative = corrected.relative_to(self.root).as_posix()
        plan, digest = retirement.preview(
            self.root, self.folders, self.source_receipt, self.predecessor,
            cfg=self.cfg, corrected_receipt=corrected_relative,
        )
        self.assertEqual(plan["sourceReceiptSha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(plan["correctedReceiptSha256"], hashlib.sha256(corrected.read_bytes()).hexdigest())
        before_corrected = corrected.read_bytes()
        corrected.write_bytes(before_corrected + b" ")
        with self.assertRaisesRegex(ValueError, "preview is stale"):
            retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertFalse((self.root / self.journal).exists())
        corrected.write_bytes(before_corrected)
        retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        retirement.verify_successor(self.root, self.journal, digest, corrected)
        with self.assertRaisesRegex(ValueError, "another rebase receipt"):
            retirement.verify_successor(self.root, self.journal, digest, source)
        source_bytes, corrected_bytes = source.read_bytes(), corrected.read_bytes()
        source.write_bytes(source_bytes + b" ")
        with self.assertRaisesRegex(ValueError, "source receipt changed"):
            retirement.verify_successor(self.root, self.journal, digest, corrected)
        source.write_bytes(source_bytes)
        corrected.write_bytes(corrected_bytes + b" ")
        with self.assertRaisesRegex(ValueError, "corrected rebase receipt changed"):
            retirement.verify_successor(self.root, self.journal, digest, corrected)
        with self.assertRaisesRegex(ValueError, "corrected rebase receipt changed"):
            retirement.recover(self.root, self.journal, digest)
        corrected.write_bytes(corrected_bytes)
        retirement.verify_successor(self.root, self.journal, digest, corrected)
        retirement.recover(self.root, self.journal, digest, apply=True)
        normal_transaction.verify(self.root, self.root / self.predecessor)
        with self.assertRaisesRegex(ValueError, "not fully applied"):
            retirement.verify_successor(self.root, self.journal, digest, corrected)

    def test_distinct_receipt_preview_requires_source_and_predecessor_bindings(self):
        source, corrected = self.distinct_receipts()
        relative = corrected.relative_to(self.root).as_posix()
        original = json.loads(corrected.read_bytes())
        for field in ("receipt", "receiptSHA256", "journal", "implementationSHA256"):
            data = json.loads(json.dumps(original))
            if field == "receipt":
                data["plan"]["releaseLineage"]["receipt"] = str(corrected)
            elif field == "receiptSHA256":
                data["plan"]["releaseLineage"]["inputs"][field] = "0" * 64
            elif field == "journal":
                data[field] = str(self.root / "_reports/runs/other.json")
            else:
                data[field] = "0" * 64
            corrected.write_text(json.dumps(data), encoding="utf-8")
            with self.subTest(field=field), self.assertRaises(ValueError):
                retirement.preview(self.root, self.folders, self.source_receipt, self.predecessor,
                                   cfg=self.cfg, corrected_receipt=relative)
        corrected.write_text(json.dumps(original), encoding="utf-8")
        source.unlink()
        with self.assertRaises(FileNotFoundError):
            retirement.preview(self.root, self.folders, self.source_receipt, self.predecessor,
                               cfg=self.cfg, corrected_receipt=relative)

    def test_successor_refuses_inexact_mapping_even_with_new_digest(self):
        receipt, _ = self.successor_fixture()
        plan, _ = self.publish()
        journal = self.root / self.journal
        data = json.loads(journal.read_bytes())
        data["plan"]["predecessorMapping"]["untouched.txt"] = "untouched.txt"
        digest = retirement._digest(data["plan"])
        data["planSha256"] = digest
        journal.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "mapping is not exact"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)

    def test_successor_refuses_changed_rebase_code_and_predecessor(self):
        receipt, _ = self.successor_fixture()
        _, digest = self.publish()
        original = retirement.metadata.content_sha256
        with mock.patch.object(retirement.metadata, "content_sha256",
                               wraps=original) as content_sha:
            from tools.art.likeness_library import normal_rebase
            content_sha.side_effect = lambda path: (
                "0" * 64 if pathlib.Path(path) == pathlib.Path(normal_rebase.__file__) else original(path)
            )
            with self.assertRaisesRegex(ValueError, "implementation changed"):
                retirement.verify_successor(self.root, self.journal, digest, receipt)
        (self.root / "untouched.txt").unlink()
        with self.assertRaisesRegex(ValueError, "predecessor published content changed"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)

    def test_successor_refuses_unbound_rebase_and_journal_tampering(self):
        receipt, _ = self.successor_fixture()
        saved = json.loads(receipt.read_bytes())
        saved["bindings"] = {"policy": "different"}
        receipt.write_text(json.dumps(saved), encoding="utf-8")
        _, digest = self.publish()
        with self.assertRaisesRegex(ValueError, "not bound to rebase receipt"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)
        journal = self.root / self.journal
        data = json.loads(journal.read_bytes())
        data["status"] = "publishing"
        journal.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not fully applied"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)
        with self.assertRaisesRegex(ValueError, "preview digest"):
            retirement.verify_successor(self.root, self.journal, "0" * 64, receipt)

    def test_successor_refuses_changed_receipt_and_reappeared_removed_file(self):
        receipt, _ = self.successor_fixture()
        _, digest = self.publish()
        removed = self.root / "old-removed.jpg"
        removed.write_bytes(b"reappeared")
        with self.assertRaisesRegex(ValueError, "removed content reappeared"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)
        removed.unlink()
        receipt.write_bytes(receipt.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "source receipt changed"):
            retirement.verify_successor(self.root, self.journal, digest, receipt)

    def test_collision_nonempty_and_stale_preview_refused(self):
        plan, digest = self.preview()
        (self.root / self.folders[0] / "review/new.JPG").write_bytes(b"new")
        with self.assertRaises(ValueError):
            retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertFalse((self.root / self.journal).exists())
        with self.assertRaisesRegex(ValueError, "original"):
            self.preview()
        (self.root / self.folders[0] / "review/new.JPG").unlink()
        (self.root / "_retired" / self.folders[0]).mkdir()
        with self.assertRaisesRegex(ValueError, "collision"):
            self.preview()

    def test_nested_identity_and_non_sandbox_refused(self):
        nested = self.root / self.folders[0] / "nested/gallery"
        nested.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "nested identity"):
            self.preview()
        with self.assertRaisesRegex(ValueError, "Sandbox/Working"):
            retirement.preview(self.root.parent, self.folders, self.source_receipt,
                               self.predecessor, cfg=self.cfg)

    def test_configured_retired_root(self):
        (self.root / "custom/archive/Potentials").mkdir(parents=True)
        self.cfg = {"storageRoots": {"retired": "custom/archive"}}
        plan, digest = self.publish()
        self.assertTrue(plan["moves"][0]["destination"].startswith("custom/archive/"))
        retirement.check(self.root, self.journal, digest)
        retirement.recover(self.root, self.journal, digest, apply=True)

    def test_missing_category_preview_apply_check_and_recovery(self):
        parent = self.root / "_retired/Potentials"
        parent.rmdir()
        plan, digest = self.preview()
        self.assertIsNone(plan["categoryParents"]["_retired/Potentials"])
        self.assertFalse(parent.exists())
        self.assertFalse((self.root / self.journal).exists())
        retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        data = retirement.check(self.root, self.journal, digest)
        self.assertIn("_retired/Potentials", data["createdParents"])
        self.assertEqual({path.name for path in (self.root / "_retired").iterdir()}, {"Potentials"})
        (parent / "other-writer.txt").write_bytes(b"preserve")
        self.assertEqual(retirement.recover(self.root, self.journal, digest), ["destination"] * 2)
        retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertEqual((parent / "other-writer.txt").read_bytes(), b"preserve")
        self.assertTrue(all((self.root / folder).is_dir() for folder in self.folders))
        normal_transaction.verify(self.root, self.root / self.predecessor)

    def test_category_parent_conflicting_type_and_link_refused(self):
        parent = self.root / "_retired/Potentials"
        parent.rmdir()
        parent.write_bytes(b"not a directory")
        with self.assertRaises((ValueError, OSError)):
            self.preview()
        self.assertEqual(parent.read_bytes(), b"not a directory")
        parent.unlink()
        parent.mkdir()
        original = retirement.sandbox._is_reparse_point
        with mock.patch.object(retirement.sandbox, "_is_reparse_point",
                               side_effect=lambda p: pathlib.Path(p) == parent or original(p)):
            with self.assertRaisesRegex(ValueError, "linked|reparse"):
                self.preview()

    def test_existing_category_replacement_refused(self):
        plan, digest = self.preview()
        parent = self.root / "_retired/Potentials"
        old = parent.with_name("Potentials-old")
        parent.rename(old)
        parent.mkdir()
        with self.assertRaisesRegex(ValueError, "stale"):
            retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertTrue(old.is_dir())
        self.assertTrue(parent.is_dir())
        self.assertFalse((self.root / self.journal).exists())

    def test_created_category_replacement_refuses_check_and_recovery(self):
        parent = self.root / "_retired/Potentials"
        parent.rmdir()
        plan, digest = self.publish()
        old = parent.with_name("Potentials-old")
        parent.rename(old)
        parent.mkdir()
        for move in plan["moves"]:
            name = pathlib.PurePosixPath(move["destination"]).name
            (old / name).rename(parent / name)
        with self.assertRaisesRegex(ValueError, "category parent changed"):
            retirement.check(self.root, self.journal, digest)
        with self.assertRaisesRegex(OSError, "category parent changed"):
            retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertTrue(old.is_dir())
        self.assertTrue(parent.is_dir())
        for move in plan["moves"]:
            name = pathlib.PurePosixPath(move["destination"]).name
            (parent / name).rename(old / name)
        parent.rmdir()
        old.rename(parent)
        retirement.recover(self.root, self.journal, digest, apply=True)
        normal_transaction.verify(self.root, self.root / self.predecessor)

    def test_missing_category_cannot_reappear_if_predecessor_removed_it(self):
        parent = self.root / "_retired/Potentials"
        parent.rmdir()
        predecessor = self.root / self.predecessor
        data = json.loads(predecessor.read_bytes())
        data["removed"].append("_retired/Potentials")
        predecessor.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "conflicts with predecessor removal"):
            self.preview()
        self.assertFalse(parent.exists())

    def test_conflicting_category_creation_preserved_and_recovery_refuses(self):
        parent = self.root / "_retired/Potentials"
        parent.rmdir()
        plan, digest = self.preview()
        mkdir = pathlib.Path.mkdir

        def race(path, *args, **kwargs):
            if path == parent:
                path.write_bytes(b"other writer")
            return mkdir(path, *args, **kwargs)

        with mock.patch.object(pathlib.Path, "mkdir", race):
            with self.assertRaisesRegex(OSError, "recovery required"):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertEqual(parent.read_bytes(), b"other writer")
        data = json.loads((self.root / self.journal).read_bytes())
        self.assertEqual(data["pendingParent"], "_retired/Potentials")
        with self.assertRaises(OSError):
            retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertEqual(parent.read_bytes(), b"other writer")
        parent.unlink()
        retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertFalse(parent.exists())

    def test_process_exit_after_category_mkdir_preserves_uncertain_parent(self):
        parent = self.root / "_retired/Potentials"
        parent.rmdir()
        plan, digest = self.preview()
        script = """
import json, os, pathlib, sys
from tools.art.likeness_library import empty_retirement as retirement
payload = json.load(sys.stdin)
mkdir = pathlib.Path.mkdir
def crash(path, *args, **kwargs):
    result = mkdir(path, *args, **kwargs)
    if str(path) == payload['parent']:
        os._exit(74)
    return result
pathlib.Path.mkdir = crash
retirement.apply(payload['root'], payload['plan'], payload['digest'],
                 payload['journal'], cfg={})
"""
        child = subprocess.run(
            [sys.executable, "-c", script],
            input=json.dumps({"root": str(self.root), "plan": plan, "digest": digest,
                              "journal": self.journal, "parent": str(parent)}),
            text=True, capture_output=True, cwd=ROOT, timeout=30,
        )
        self.assertEqual(child.returncode, 74, child.stderr)
        self.assertTrue(parent.is_dir())
        data = json.loads((self.root / self.journal).read_bytes())
        self.assertEqual(data["pendingParent"], "_retired/Potentials")
        self.assertEqual(retirement.recover(self.root, self.journal, digest), ["source"] * 2)
        retirement.recover(self.root, self.journal, digest, apply=True)
        data = json.loads((self.root / self.journal).read_bytes())
        self.assertEqual(data["preservedPendingParent"]["ownership"], "unknown")
        self.assertTrue(parent.is_dir())
        normal_transaction.verify(self.root, self.root / self.predecessor)

    def test_interruption_before_category_mkdir_recovers_without_creating_it(self):
        parent = self.root / "_retired/Potentials"
        parent.rmdir()
        plan, digest = self.preview()
        mkdir = pathlib.Path.mkdir

        class SimulatedCrash(BaseException):
            pass

        def crash(path, *args, **kwargs):
            if path == parent:
                raise SimulatedCrash()
            return mkdir(path, *args, **kwargs)

        with mock.patch.object(pathlib.Path, "mkdir", crash):
            with self.assertRaises(SimulatedCrash):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertFalse(parent.exists())
        self.assertEqual(retirement.recover(self.root, self.journal, digest), ["source"] * 2)
        retirement.recover(self.root, self.journal, digest, apply=True)
        data = json.loads((self.root / self.journal).read_bytes())
        self.assertIsNone(data["preservedPendingParent"]["identity"])
        self.assertFalse(parent.exists())

    def test_crash_after_move_in_new_category_recovers_without_removing_parent(self):
        parent = self.root / "_retired/Potentials"
        parent.rmdir()
        plan, digest = self.preview()
        rename = pathlib.Path.rename

        class SimulatedCrash(BaseException):
            pass

        def crash(path, target):
            rename(path, target)
            raise SimulatedCrash()

        with mock.patch.object(pathlib.Path, "rename", crash):
            with self.assertRaises(SimulatedCrash):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertEqual(retirement.recover(self.root, self.journal, digest),
                         ["destination", "source"])
        retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertTrue(parent.is_dir())
        normal_transaction.verify(self.root, self.root / self.predecessor)

    def test_cooperating_transactions_share_one_lock(self):
        plan, digest = self.preview()
        with retirement._locked(self.root, plan):
            with self.assertRaisesRegex(ValueError, "locked by another cooperating writer"):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertFalse((self.root / self.journal).exists())
        self.assertTrue(all((self.root / folder).is_dir() for folder in self.folders))

    def test_link_and_hard_link_refused(self):
        path = self.root / self.folders[0] / "gallery/z_identity.txt"
        original = retirement.sandbox._is_reparse_point
        with mock.patch.object(retirement.sandbox, "_is_reparse_point",
                               side_effect=lambda p: pathlib.Path(p) == path or original(p)):
            with self.assertRaisesRegex(ValueError, "linked"):
                self.preview()
        sibling = path.with_name("hardlink.txt")
        os.link(path, sibling)
        with self.assertRaisesRegex(ValueError, "hard-linked"):
            self.preview()

    def test_crash_after_move_before_journal_update_recovers(self):
        plan, digest = self.preview()
        rename = pathlib.Path.rename

        class SimulatedCrash(BaseException):
            pass

        def crash(path, target):
            rename(path, target)
            raise SimulatedCrash()

        with mock.patch.object(pathlib.Path, "rename", crash):
            with self.assertRaises(SimulatedCrash):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        data = json.loads((self.root / self.journal).read_bytes())
        self.assertEqual(data["status"], "publishing")
        self.assertEqual(data["pending"], 0)
        self.assertEqual(retirement.recover(self.root, self.journal, digest),
                         ["destination", "source"])
        retirement.recover(self.root, self.journal, digest, apply=True)
        normal_transaction.verify(self.root, self.root / self.predecessor)

    def test_process_exit_after_rename_releases_lock_and_recovers(self):
        plan, digest = self.preview()
        script = """
import json, os, pathlib, sys
from tools.art.likeness_library import empty_retirement as retirement
payload = json.load(sys.stdin)
rename = pathlib.Path.rename
def crash(path, target):
    rename(path, target)
    os._exit(73)
pathlib.Path.rename = crash
retirement.apply(payload['root'], payload['plan'], payload['digest'],
                 payload['journal'], cfg={})
"""
        child = subprocess.run(
            [sys.executable, "-c", script],
            input=json.dumps({"root": str(self.root), "plan": plan, "digest": digest,
                              "journal": self.journal}),
            text=True, capture_output=True, cwd=ROOT, timeout=30,
        )
        self.assertEqual(child.returncode, 73, child.stderr)
        self.assertEqual(retirement.recover(self.root, self.journal, digest),
                         ["destination", "source"])
        retirement.recover(self.root, self.journal, digest, apply=True)
        normal_transaction.verify(self.root, self.root / self.predecessor)

    def test_partial_initial_journal_preserved_without_moving_folder(self):
        plan, digest = self.preview()
        write = normal_transaction.write

        def partial(path, data, *, exclusive=False):
            if exclusive:
                path.write_bytes(b'{"incomplete":')
                raise OSError("injected partial journal")
            return write(path, data)

        with mock.patch.object(normal_transaction, "write", partial):
            with self.assertRaisesRegex(OSError, "partial journal"):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertEqual((self.root / self.journal).read_bytes(), b'{"incomplete":')
        self.assertTrue(all((self.root / folder).is_dir() for folder in self.folders))
        with self.assertRaisesRegex(ValueError, "incomplete retirement journal"):
            retirement.recover(self.root, self.journal, digest)

    def test_partial_failure_retains_recovery_required(self):
        plan, digest = self.preview()
        rename = pathlib.Path.rename
        calls = []

        def fail_second(path, target):
            calls.append(path)
            if len(calls) == 2:
                raise OSError("injected move failure")
            return rename(path, target)

        with mock.patch.object(pathlib.Path, "rename", fail_second):
            with self.assertRaisesRegex(OSError, "recovery required"):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertEqual(json.loads((self.root / self.journal).read_bytes())["status"], "recovery-required")
        self.assertEqual(retirement.recover(self.root, self.journal, digest), ["destination", "source"])
        retirement.recover(self.root, self.journal, digest, apply=True)
        normal_transaction.verify(self.root, self.root / self.predecessor)

    def test_racing_destination_is_not_overwritten(self):
        plan, digest = self.preview()
        rename = pathlib.Path.rename

        def collide(path, target):
            pathlib.Path(target).mkdir()
            (pathlib.Path(target) / "new.txt").write_bytes(b"other writer")
            return rename(path, target)

        with mock.patch.object(pathlib.Path, "rename", collide):
            with self.assertRaisesRegex(OSError, "recovery required"):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        destination = self.root / plan["moves"][0]["destination"]
        self.assertEqual((destination / "new.txt").read_bytes(), b"other writer")
        self.assertTrue((self.root / plan["moves"][0]["source"]).is_dir())
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            retirement.recover(self.root, self.journal, digest)

    def test_racing_empty_destination_is_not_overwritten(self):
        plan, digest = self.preview()
        rename = pathlib.Path.rename

        def collide(path, target):
            pathlib.Path(target).mkdir()
            return rename(path, target)

        with mock.patch.object(pathlib.Path, "rename", collide):
            with self.assertRaisesRegex(OSError, "recovery required"):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertTrue((self.root / plan["moves"][0]["source"]).is_dir())
        self.assertEqual(list((self.root / plan["moves"][0]["destination"]).iterdir()), [])
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            retirement.recover(self.root, self.journal, digest)

    def test_changed_tree_after_move_preserved_and_recovery_refused(self):
        plan, digest = self.preview()
        rename = pathlib.Path.rename

        def modify(path, target):
            result = rename(path, target)
            (pathlib.Path(target) / "new.txt").write_bytes(b"concurrent")
            return result

        with mock.patch.object(pathlib.Path, "rename", modify):
            with self.assertRaisesRegex(OSError, "recovery required"):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        target = self.root / plan["moves"][0]["destination"] / "new.txt"
        self.assertEqual(target.read_bytes(), b"concurrent")
        with self.assertRaisesRegex(OSError, "inventory changed"):
            retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertEqual(target.read_bytes(), b"concurrent")

    def test_journal_concurrent_edit_is_not_overwritten(self):
        plan, digest = self.preview()
        rename = pathlib.Path.rename
        journal = self.root / self.journal

        def edit_journal(path, target):
            result = rename(path, target)
            journal.write_bytes(b"other writer")
            return result

        with mock.patch.object(pathlib.Path, "rename", edit_journal):
            with self.assertRaisesRegex(OSError, "journal update also failed"):
                retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        self.assertEqual(journal.read_bytes(), b"other writer")
        self.assertTrue((self.root / plan["moves"][0]["destination"]).is_dir())

    def test_recovery_refuses_new_content_and_collision_without_overwrite(self):
        plan, digest = self.publish()
        destination = self.root / plan["moves"][0]["destination"]
        (destination / "new.txt").write_bytes(b"new concurrent content")
        with self.assertRaisesRegex(OSError, "inventory changed"):
            retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertEqual(json.loads((self.root / self.journal).read_bytes())["status"], "recovery-required")
        self.assertEqual((destination / "new.txt").read_bytes(), b"new concurrent content")
        (destination / "new.txt").unlink()
        source = self.root / plan["moves"][0]["source"]
        source.mkdir()
        with self.assertRaisesRegex(OSError, "ambiguous"):
            retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertTrue(source.is_dir())
        self.assertTrue(destination.is_dir())

    def test_recovery_refuses_changed_predecessor_and_untouched_output(self):
        _, digest = self.publish()
        (self.root / "untouched.txt").write_bytes(b"new")
        with self.assertRaisesRegex(OSError, "predecessor published"):
            retirement.recover(self.root, self.journal, digest, apply=True)
        (self.root / "untouched.txt").write_bytes(b"previous output")
        (self.root / self.predecessor).write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(OSError, "predecessor journal changed"):
            retirement.recover(self.root, self.journal, digest, apply=True)

    def test_receipt_source_rows_are_bound_and_must_not_change(self):
        source = self.root / self.source_receipt
        receipt = json.loads(source.read_bytes())
        receipt["plan"]["sourceRows"][0]["sourceHash"] = "2" * 64
        source.write_text(json.dumps(receipt), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs from receipt source hashes"):
            self.preview()
        receipt["plan"]["sourceRows"][0]["sourceHash"] = "1" * 64
        source.write_text(json.dumps(receipt), encoding="utf-8")
        _, digest = self.publish()
        source.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "rebase source receipt changed"):
            retirement.check(self.root, self.journal, digest)
        with self.assertRaisesRegex(OSError, "rebase source receipt changed"):
            retirement.recover(self.root, self.journal, digest, apply=True)

    def test_interrupted_recovery_can_resume(self):
        _, digest = self.publish()
        rename = pathlib.Path.rename

        class SimulatedCrash(BaseException):
            pass

        def crash(path, target):
            rename(path, target)
            raise SimulatedCrash()

        with mock.patch.object(pathlib.Path, "rename", crash):
            with self.assertRaises(SimulatedCrash):
                retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertEqual(retirement.recover(self.root, self.journal, digest), ["source", "destination"])
        retirement.recover(self.root, self.journal, digest, apply=True)
        normal_transaction.verify(self.root, self.root / self.predecessor)

    def test_recovery_failure_keeps_required_state(self):
        _, digest = self.publish()
        with mock.patch.object(pathlib.Path, "rename", side_effect=OSError("injected")):
            with self.assertRaisesRegex(OSError, "recovery required"):
                retirement.recover(self.root, self.journal, digest, apply=True)
        self.assertEqual(json.loads((self.root / self.journal).read_bytes())["status"], "recovery-required")
        retirement.recover(self.root, self.journal, digest, apply=True)

    def test_changed_journal_or_digest_refused(self):
        plan, digest = self.preview()
        plan["moves"][0]["source"] = "Potentials/Unrelated"
        with self.assertRaisesRegex(ValueError, "preview digest"):
            retirement.apply(self.root, plan, digest, self.journal, cfg=self.cfg)
        _, digest = self.publish()
        journal = self.root / self.journal
        data = json.loads(journal.read_bytes())
        data["plan"]["moves"][0]["destination"] = "_retired/Potentials/Else"
        journal.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "preview digest"):
            retirement.recover(self.root, self.journal, digest)


if __name__ == "__main__":
    unittest.main()
