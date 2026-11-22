"""Focused report-only movement-history tests using isolated fake evidence."""
import contextlib
import hashlib
import io
import json
import os
import pathlib
import tempfile
import time
import unittest
from unittest import mock

from tools.art.likeness_library import movement_history as history

ROOT = pathlib.Path(__file__).resolve().parents[4]
REAL_LINEAGE = history.sandbox_red_release.verified_current_lineage
REAL_CHAIN = history.sandbox_red_release.verified_release_chain
REAL_RECAP = history.normal_recap.collect
REAL_RELEASE_RECAP = history.sandbox_red_release.normal_recap.collect
REAL_BIND_FIRST = history._bind_first_moves


def digest(content):
    return hashlib.sha256(content).hexdigest()


class MovementHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "tmp")
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name).resolve() / "Sovereign Territories Sandbox" / "Working"
        self.root.mkdir(parents=True)
        self.receipt = self.root / "receipt.json"
        self.receipt.write_text("receipt", encoding="utf-8")
        self.audit = self.root / "audit.html"
        self.manifest = self.root / "audit.report.json"
        self.manifest.write_text("audit binding", encoding="utf-8")
        self.review_dir = self.root / "review"
        self.review_dir.mkdir()
        self.review = self.review_dir / "people_gallery_review.html"
        self.review.write_text("final review", encoding="utf-8")
        self.photo_hash = digest(b"image")
        self.row = {
            "photoId": "p<1>", "source": "Old/gallery/a.jpg", "destination": "One/gallery/a.jpg",
            "sha256": self.photo_hash, "preparedSHA256": self.photo_hash,
        }
        self.archive = {
            "photoId": "p<1>", "source": "Old/gallery/c.jpg", "destination": "_duplicates/c.jpg",
            "sha256": self.photo_hash, "preparedSHA256": self.photo_hash,
        }
        self.original = {
            "runId": "base", "status": "applied", "snapshotDiagnostics": [], "snapshotIdUnavailable": 0,
            "physicalSources": 2, "workingRoot": str(self.root),
            "inputs": {str(self.receipt): history._sha(self.receipt)},
            "rows": [self.row, self.archive], "auditRecords": [{"row": self.row}],
        }
        self.publications = [
            {"moves": [{"photoId": "p<1>", "source": "One/gallery/a.jpg",
                        "destination": "Two/review/a.jpg", "sha256": self.photo_hash}]},
            {"moves": [{"photoId": "p<1>", "source": "Two/review/a.jpg",
                        "destination": "Final/review/a.jpg", "sha256": self.photo_hash}],
             "lineageJournalSHA256": ["first-hash"]},
        ]
        self.lineage = {
            "receiptSHA256": history._sha(self.receipt), "priorManifestSHA256": history._sha(self.manifest),
            "currentReviewSHA256": history._sha(self.review), "priorJournalSHA256": "first-hash",
            "continuationJournalSHA256": ["second-hash"], "conservedCount": 1,
        }
        for run in ("first", "second"):
            directory = self.root / "_reports" / "library" / run
            directory.mkdir(parents=True)
            (directory / "report.json").write_text(json.dumps({
                "kind": "sandbox-red-release-experiment", "root": str(self.root), "runId": run,
                "snapshotReportManifestSHA256": history._sha(self.manifest),
            }), encoding="utf-8")
            journal = self.root / "_reports" / "runs" / run / "publication-journal.json"
            journal.parent.mkdir(parents=True)
            journal.write_text("journal", encoding="utf-8")
        final = self.root / "Final" / "review" / "a.jpg"
        final.parent.mkdir(parents=True)
        final.write_bytes(b"image")
        middle = self.root / "Two" / "review" / "a.jpg"
        middle.parent.mkdir(parents=True)
        middle.write_bytes(b"other")
        for patcher in (
            mock.patch.object(history.normal_recap, "collect", return_value=self.original),
            mock.patch.object(history.sandbox_red_release, "verified_current_lineage", return_value=self.lineage),
            mock.patch.object(history.sandbox_red_release, "verified_release_chain",
                              return_value=(self.publications, ["first-hash", "second-hash"])),
            mock.patch.object(history, "_bind_first_moves"),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def publish(self, runs=None, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return history.publish(self.root, self.receipt, self.audit, self.review_dir,
                                   runs or ["first", "second"], "_reports", "history1", **kwargs)

    def test_preview_write_repeat_check_and_missing_image_states(self):
        out = self.root / "_reports" / "library" / "movement-history" / "history1" / "index.html"
        self.publish()
        self.assertFalse(out.parent.exists())
        self.publish(apply=True)
        before = out.read_bytes()
        page = before.decode()
        self.assertIn("p&lt;1&gt;", page)
        self.assertIn("Old/gallery/a.jpg", page)
        self.assertIn("One/gallery/a.jpg", page)
        self.assertIn("Two/review/a.jpg", page)
        self.assertIn("Final/review/a.jpg", page)
        self.assertIn("Image missing; no substitute", page)
        self.assertIn("Image mismatch; no substitute", page)
        self.assertIn("<img", page)
        self.assertIn("not a separate current Review member", page)
        archive_article = page.split("<article>")[2]
        self.assertIn("_duplicates/c.jpg", archive_article)
        self.assertNotIn("Two/review/a.jpg", archive_article)
        self.assertIn("historical outcomes only, not intended routing", page)
        self.assertIn("Physical source rows: 2; current Review members: 1; other physical source dispositions: 1", page)
        self.assertLess(page.index("Two/review/a.jpg"), page.index("Final/review/a.jpg"))
        self.publish(apply=True)
        self.publish(check=True)
        self.assertEqual(out.read_bytes(), before)
        out.write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            self.publish(check=True)
        with self.assertRaisesRegex(ValueError, "different or incomplete"):
            self.publish(apply=True)
        self.assertEqual(out.read_text(encoding="utf-8"), "tampered")

    def test_omission_repetition_order_and_tampered_moves_fail(self):
        with self.assertRaisesRegex(ValueError, "cover all"):
            self.publish(["first"])
        with self.assertRaisesRegex(ValueError, "exactly once"):
            self.publish(["first", "first"])
        self.publications.reverse()
        with self.assertRaisesRegex(ValueError, "ordered journal lineage"):
            self.publish()
        self.publications.reverse()
        self.publications[1]["moves"][0]["source"] = "One/gallery/a.jpg"
        with self.assertRaisesRegex(ValueError, "preceding photo state"):
            self.publish()
        self.assertFalse((self.root / "_reports" / "library" / "movement-history").exists())

    def test_incomplete_census_and_missing_order_binding_fail(self):
        self.original["physicalSources"] = 3
        with self.assertRaisesRegex(ValueError, "source census is incomplete"):
            self.publish()
        self.original["physicalSources"] = 2
        del self.publications[1]["lineageJournalSHA256"]
        with self.assertRaisesRegex(ValueError, "missing or ambiguous ordered"):
            self.publish()

    def test_orphan_and_unsafe_paths_refused(self):
        (self.root / "_reports" / "runs" / "second" / "publication-journal.json").unlink()
        with self.assertRaisesRegex(ValueError, "journal missing"):
            self.publish()
        with self.assertRaisesRegex(ValueError, "unsafe"):
            self.publish(["first", "../second"])

    def test_chain_failure_including_retired_derivative_is_not_bypassed(self):
        with mock.patch.object(history.sandbox_red_release, "verified_current_lineage",
                               side_effect=ValueError("release lineage published content changed: derivative")):
            with self.assertRaisesRegex(ValueError, "derivative"):
                self.publish(check=True)
        self.assertFalse((self.root / "_reports" / "library" / "movement-history").exists())

    def test_changed_image_invalidates_check_and_cannot_overwrite_report(self):
        self.publish(apply=True)
        (self.root / "Final" / "review" / "a.jpg").unlink()
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            self.publish(check=True)
        with self.assertRaisesRegex(ValueError, "different or incomplete"):
            self.publish(apply=True)

    def corrected_fixture(self):
        from tools.art.likeness_library import normal_rebase

        old = "Final/review/a.jpg"
        final = "Corrected/gallery/a.jpg"
        (self.root / pathlib.PurePosixPath(old)).unlink()
        target = self.root / pathlib.PurePosixPath(final)
        target.parent.mkdir(parents=True)
        target.write_bytes(b"corrected")
        backup = self.root / "_backup" / "corrected"
        backup.mkdir(parents=True)
        (backup / "saved.jpg").write_bytes(b"image")
        manifest = backup / "manifest.json"
        manifest.write_text(json.dumps({"entries": [
            {"source": str(self.root / pathlib.PurePosixPath(old)), "backup": "saved.jpg", "sha256": self.photo_hash},
        ]}), encoding="utf-8")
        journal = self.root / "corrected-journal.json"
        journal.write_text(json.dumps({
            "kind": "normal-publication", "status": "applied", "root": str(self.root), "runId": "corrected",
            "backup": str(backup), "backupManifestSHA256": history._sha(manifest), "bindings": {},
            "after": {final: digest(b"corrected")}, "removed": [old],
        }), encoding="utf-8")
        receipt = self.root / "corrected-receipt.json"
        corrected_review = self.root / "_reports" / "library" / "corrected-snapshot" / "people_gallery_review.html"
        corrected_review.parent.mkdir(parents=True)
        corrected_review.write_text('<script id="review-data">' + json.dumps([{
            "folder": "Corrected", "bucket": "Gallery", "name": "a.jpg", "photoId": "p<1>",
            "contentSha256": digest(b"corrected"),
        }]) + '</script>', encoding="utf-8")
        move = {"source": old, "destination": final, "photoId": "p<1>", "sha256": self.photo_hash}
        receipt.write_text(json.dumps({
            "kind": "normal-rebase-receipt", "schemaVersion": 1, "status": "applied", "root": str(self.root),
            "runId": "corrected", "bindings": {}, "journal": str(journal),
            "implementationSHA256": history._sha(pathlib.Path(normal_rebase.__file__)),
            "viewerPaths": [str(corrected_review)], "moves": [move],
            "publishedNative": [{"native": final, "sha256": digest(b"corrected")}],
            "plan": {"sourceRows": [{"source": old, "sourceHash": self.photo_hash, "photoId": "p<1>"}],
                     "sourceHashes": {old: self.photo_hash}, "moves": [move]},
        }), encoding="utf-8")
        data = REAL_RECAP(receipt)
        corrected_row = data["rows"][0]
        return receipt, corrected_row, data

    def test_corrected_successor_chains_multi_move_and_keeps_archive_row(self):
        receipt, _, _ = self.corrected_fixture()
        with mock.patch.object(history.normal_recap, "collect",
                               side_effect=lambda path, **kwargs: REAL_RECAP(path) if pathlib.Path(path) == receipt else self.original):
            self.publish(corrected_receipt=receipt, apply=True)
            self.publish(corrected_receipt=receipt, check=True)
            self.publish(corrected_receipt=receipt, expected_cohort=1)
            page = (self.root / "_reports" / "library" / "movement-history" / "history1" / "index.html").read_text(
                encoding="utf-8")
            self.assertIn("1 of 1 released photos chained through corrected rebase corrected", page)
            self.assertLess(page.index("Two/review/a.jpg"), page.index("Final/review/a.jpg"))
            self.assertLess(page.index("Final/review/a.jpg"), page.index("Corrected/gallery/a.jpg"))
            self.assertIn("Historical release cohort", page)
            archive = page.split("<article>")[2]
            self.assertIn("_duplicates/c.jpg", archive)
            self.assertIn("Corrected lineage not established", archive)
            self.assertNotIn("Corrected/gallery/a.jpg", archive)

    def test_corrected_refuses_wrong_cohort_ambiguous_id_and_changed_hash(self):
        receipt, corrected_row, corrected = self.corrected_fixture()
        with mock.patch.object(history.normal_recap, "collect",
                               side_effect=lambda path, **kwargs: corrected if pathlib.Path(path) == receipt else self.original):
            with self.assertRaisesRegex(ValueError, "cohort count 1 differs from required 219"):
                self.publish(corrected_receipt=receipt, expected_cohort=219)
            corrected_row["sha256"] = digest(b"changed")
            with self.assertRaisesRegex(ValueError, "changed-hash corrected lineage"):
                self.publish(corrected_receipt=receipt, expected_cohort=1)
            corrected_row["sha256"] = self.photo_hash
            corrected["rows"].append({**corrected_row, "source": "Different/gallery/a.jpg"})
            corrected["physicalSources"] = 2
            with self.assertRaisesRegex(ValueError, "ambiguous or changed-hash"):
                self.publish(corrected_receipt=receipt, expected_cohort=1)

    def test_optional_guard_also_checks_historical_preview(self):
        self.publish(expected_cohort=1)
        with self.assertRaisesRegex(ValueError, "cohort count 1 differs from required 219"):
            self.publish(expected_cohort=219)
        self.assertFalse((self.root / "_reports" / "library" / "movement-history").exists())

    def test_retirement_requires_explicit_complete_arguments(self):
        for kwargs in (
            {"retirement_journal": "_reports/runs/retirement.json"},
            {"retirement_digest": "0" * 64},
            {"retirement_journal": "_reports/runs/retirement.json", "retirement_digest": "0" * 64},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, "requires a corrected receipt"):
                self.publish(**kwargs)
        self.assertFalse((self.root / "_reports/library/movement-history").exists())

    def test_cli_passes_explicit_retirement_arguments(self):
        cw = history.sandbox_red_release.likeness.cw
        with mock.patch.object(cw, "load_cfg", return_value={}), \
             mock.patch.object(cw, "sandbox_work_root", return_value=self.root), \
             mock.patch.object(cw, "storage_root", return_value=self.root / "_reports"), \
             mock.patch.object(history, "publish") as publish:
            result = history.main([
                "--root", str(self.root), "--receipt", str(self.receipt), "--audit", str(self.audit),
                "--current-review", str(self.review_dir), "--report-id", "new", "--release", "first",
                "--corrected-receipt", str(self.root / "corrected.json"),
                "--retirement-journal", "_reports/runs/retirement.json", "--retirement-digest", "a" * 64,
                "--check",
            ])
        self.assertEqual(result, 0)
        self.assertEqual(publish.call_args.kwargs["retirement_journal"], "_reports/runs/retirement.json")
        self.assertEqual(publish.call_args.kwargs["retirement_digest"], "a" * 64)
        self.assertTrue(publish.call_args.kwargs["check"])

    def test_old_producer_hash_cannot_be_rewritten_or_accepted(self):
        self.publish(apply=True)
        directory = self.root / "_reports/library/movement-history/history1"
        report = directory / "report.json"
        state = json.loads(report.read_bytes())
        state["producers"][str(pathlib.Path(history.__file__).absolute())] = "0" * 64
        report.write_text(json.dumps(state), encoding="utf-8")
        before = {path: path.read_bytes() for path in directory.iterdir()}
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            self.publish(check=True)
        with self.assertRaisesRegex(ValueError, "different or incomplete"):
            self.publish(apply=True)
        self.assertEqual(before, {path: path.read_bytes() for path in directory.iterdir()})

    def test_empty_derived_cohort_and_zero_guard_are_supported(self):
        self.publications[0]["moves"] = []
        self.publications[1]["moves"] = []
        receipt, _, corrected = self.corrected_fixture()
        with mock.patch.object(history.normal_recap, "collect",
                               side_effect=lambda path, **kwargs: corrected if pathlib.Path(path) == receipt else self.original):
            self.publish(corrected_receipt=receipt)
            self.publish(corrected_receipt=receipt, expected_cohort=0, apply=True)
            self.publish(corrected_receipt=receipt, expected_cohort=0, check=True)
            page = (self.root / "_reports" / "library" / "movement-history" / "history1" / "index.html").read_text(
                encoding="utf-8")
            self.assertIn("0 of 0 released photos chained", page)
            with self.assertRaisesRegex(ValueError, "cohort count 0 differs from required 1"):
                self.publish(corrected_receipt=receipt, expected_cohort=1)

    def test_corrected_refuses_tampered_recovery_and_never_bypasses_chain_failure(self):
        receipt, _, corrected = self.corrected_fixture()
        with mock.patch.object(history.normal_recap, "collect",
                               side_effect=lambda path, **kwargs: corrected if pathlib.Path(path) == receipt else self.original):
            (self.root / "_backup" / "corrected" / "saved.jpg").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "recovery bytes changed"):
                self.publish(corrected_receipt=receipt, expected_cohort=1)
            with mock.patch.object(history.sandbox_red_release, "verified_current_lineage",
                                   side_effect=ValueError("historical chain failed")), \
                 mock.patch.object(history, "_corrected") as successor:
                with self.assertRaisesRegex(ValueError, "historical chain failed"):
                    self.publish(corrected_receipt=receipt, expected_cohort=1)
                successor.assert_not_called()
        self.assertFalse((self.root / "_reports" / "library" / "movement-history").exists())

    def test_later_verified_report_can_bind_legacy_missing_order(self):
        history._ordered_lineage([{}, {}, {"lineageJournalSHA256": ["a", "b"]}],
                                 ["a", "b", "c"], ["one", "two", "three"])
        with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
            history._ordered_lineage([{}, {}, {}], ["a", "b", "c"], ["one", "two", "three"])
        with self.assertRaisesRegex(ValueError, "changed ordered"):
            history._ordered_lineage([{}, {}, {"lineageJournalSHA256": ["b", "a"]}],
                                     ["a", "b", "c"], ["one", "two", "three"])

    def test_successor_view_distinguishes_overwritten_removed_new_and_untouched(self):
        receipt, _, _ = self.corrected_fixture()
        backup = self.root / "_backup" / "corrected"
        manifest_path = backup / "manifest.json"
        manifest = json.loads(manifest_path.read_bytes())
        journal_path = self.root / "corrected-journal.json"
        journal = json.loads(journal_path.read_bytes())
        for relative, old, current in (
            ("in-place.jpg", b"before", b"after"),
            ("removed.jpg", b"removed-before", None),
        ):
            saved = backup / (relative + ".backup")
            saved.write_bytes(old)
            manifest["entries"].append({"source": str(self.root / relative), "backup": saved.name,
                                        "sha256": digest(old)})
            if current is None:
                journal["removed"].append(relative)
            else:
                (self.root / relative).write_bytes(current)
                journal["after"][relative] = digest(current)
        (self.root / "new.jpg").write_bytes(b"new")
        journal["after"]["new.jpg"] = digest(b"new")
        (self.root / "untouched.jpg").write_bytes(b"untouched")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        journal["backupManifestSHA256"] = history._sha(manifest_path)
        journal_path.write_text(json.dumps(journal), encoding="utf-8")
        view = history.sandbox_red_release.VerifiedRebaseSuccessor(self.root, receipt)
        self.assertEqual(view.read(self.root / "in-place.jpg"), b"before")
        self.assertEqual(view.read(self.root / "removed.jpg"), b"removed-before")
        self.assertIsNone(view.read(self.root / "new.jpg"))
        self.assertEqual(view.read(self.root / "untouched.jpg"), b"untouched")
        view.verify_unchanged()
        (self.root / "untouched.jpg").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "changed during verification"):
            view.verify_unchanged()

    def test_real_chain_check_blocks_retired_final_journal_derivative(self):
        (self.root / "Two" / "review" / "a.jpg").unlink()
        self.receipt.write_text(json.dumps({"plan": {"sourceRows": []}}), encoding="utf-8")
        self.original["inputs"] = {str(self.receipt): history._sha(self.receipt)}
        self.manifest.write_text(json.dumps({
            "receipt": str(self.receipt), "inputs": self.original["inputs"],
            "redCandidates": [{"photoId": "p<1>", "currentPath": self.row["destination"],
                               "nativeSha256": self.photo_hash}],
        }), encoding="utf-8")
        manifest_hash = history._sha(self.manifest)
        self.review.write_text('<script id="review-data">' + json.dumps([{
            "photoId": "p<1>", "generationSource": "Final/review/a.jpg", "contentSha256": self.photo_hash,
        }]) + '</script>', encoding="utf-8")
        derivative = self.root / "derivative.jpg"
        derivative.write_bytes(b"derivative")
        first_hash = None
        for index, run in enumerate(("first", "second")):
            backup = self.root / "_backup" / run
            backup.mkdir(parents=True)
            entries = []
            if index:
                saved = backup / "saved.jpg"
                saved.write_bytes(b"image")
                entries.append({"source": str(self.root / "Two" / "review" / "a.jpg"),
                                "backup": "saved.jpg", "sha256": self.photo_hash})
            else:
                saved = backup / "saved.jpg"
                saved.write_bytes(b"image")
                entries.append({"source": str(self.root / "One" / "gallery" / "a.jpg"),
                                "backup": "saved.jpg", "sha256": self.photo_hash})
            backup_manifest = backup / "manifest.json"
            backup_manifest.write_text(json.dumps({"entries": entries}), encoding="utf-8")
            report = self.root / "_reports" / "library" / run / "report.json"
            publication = {
                "kind": "sandbox-red-release-experiment", "root": str(self.root), "runId": run,
                "snapshotReportManifestSHA256": manifest_hash, "moves": self.publications[index]["moves"],
                "unaffectedNativeSHA256": {},
            }
            if index:
                publication.update(planSHA256="plan", lineageJournalSHA256=[first_hash])
            report.write_text(json.dumps(publication), encoding="utf-8")
            after = {report.relative_to(self.root).as_posix(): history._sha(report),
                     ("Final/review/a.jpg" if index else "Two/review/a.jpg"): self.photo_hash}
            if index:
                after["derivative.jpg"] = history._sha(derivative)
            journal = self.root / "_reports" / "runs" / run / "publication-journal.json"
            journal.write_text(json.dumps({
                "kind": "normal-publication", "status": "applied", "root": str(self.root), "runId": run,
                "backup": str(backup), "backupManifestSHA256": history._sha(backup_manifest),
                "bindings": {"planSHA256": "plan"} if index else {"snapshotReportManifestSHA256": manifest_hash},
                "after": after, "removed": ["Two/review/a.jpg"] if index else ["One/gallery/a.jpg"],
            }), encoding="utf-8")
            if not index:
                first_hash = history._sha(journal)
        with mock.patch.object(history.sandbox_red_release, "verified_current_lineage", REAL_LINEAGE), \
             mock.patch.object(history.sandbox_red_release, "verified_release_chain", REAL_CHAIN), \
             mock.patch.object(history, "_bind_first_moves", REAL_BIND_FIRST), \
             mock.patch.object(history.sandbox_red_release.normal_recap, "collect", return_value=self.original), \
             mock.patch.object(history.sandbox_red_release.likeness.cw, "load_cfg", return_value={}), \
             mock.patch.object(history.sandbox_red_release.likeness.cw, "storage_root",
                               return_value=self.root / "_reports"):
            self.publish(apply=True)
            self.publish(check=True)
            derivative.rename(self.root / "retired-derivative.jpg")
            with self.assertRaisesRegex(ValueError, "published content changed: derivative.jpg"):
                self.publish(check=True)

    def test_real_applied_receipt_through_real_single_release(self):
        source = self.row["destination"]
        final = "Final/review/a.jpg"
        original_review = self.root / "_reports" / "library" / "people_gallery_review.html"
        original_review.write_text('<script id="review-data">' + json.dumps([{
            "folder": "One", "bucket": "Gallery", "name": "a.jpg", "photoId": "p<1>",
            "contentSha256": self.photo_hash,
        }]) + '</script>', encoding="utf-8")
        rows = [{"source": source, "sourceHash": self.photo_hash, "photoId": "p<1>"}]
        self.receipt.write_text(json.dumps({
            "kind": "normal-rebase-receipt", "schemaVersion": 1, "status": "applied",
            "root": str(self.root), "runId": "base", "viewerPaths": [str(original_review)],
            "plan": {"sourceRows": rows, "sourceHashes": {source: self.photo_hash}, "moves": []},
        }), encoding="utf-8")
        self.review.write_text('<script id="review-data">' + json.dumps([{
            "photoId": "p<1>", "generationSource": final, "contentSha256": self.photo_hash,
        }]) + '</script>', encoding="utf-8")
        self.manifest.write_text(json.dumps({
            "receipt": str(self.receipt),
            "inputs": {str(self.receipt): history._sha(self.receipt),
                       str(original_review): history._sha(original_review)},
            "redCandidates": [{"photoId": "p<1>", "currentPath": source, "nativeSha256": self.photo_hash}],
        }), encoding="utf-8")
        manifest_hash = history._sha(self.manifest)
        backup = self.root / "_backup" / "single"
        backup.mkdir(parents=True)
        (backup / "saved.jpg").write_bytes(b"image")
        backup_manifest = backup / "manifest.json"
        backup_manifest.write_text(json.dumps({"entries": [
            {"source": str(self.root / pathlib.PurePosixPath(source)), "backup": "saved.jpg",
             "sha256": self.photo_hash},
        ]}), encoding="utf-8")
        report = self.root / "_reports" / "library" / "first" / "report.json"
        report.write_text(json.dumps({
            "kind": "sandbox-red-release-experiment", "root": str(self.root), "runId": "first",
            "snapshotReportManifestSHA256": manifest_hash, "unaffectedNativeSHA256": {},
            "moves": [{"photoId": "p<1>", "source": source, "destination": final, "sha256": self.photo_hash}],
        }), encoding="utf-8")
        journal = self.root / "_reports" / "runs" / "first" / "publication-journal.json"
        journal.write_text(json.dumps({
            "kind": "normal-publication", "status": "applied", "root": str(self.root), "runId": "first",
            "backup": str(backup), "backupManifestSHA256": history._sha(backup_manifest),
            "bindings": {"snapshotReportManifestSHA256": manifest_hash},
            "after": {report.relative_to(self.root).as_posix(): history._sha(report), final: self.photo_hash},
            "removed": [source],
        }), encoding="utf-8")
        with mock.patch.object(history.normal_recap, "collect", REAL_RECAP), \
             mock.patch.object(history.sandbox_red_release.normal_recap, "collect", REAL_RELEASE_RECAP), \
             mock.patch.object(history.sandbox_red_release, "verified_current_lineage", REAL_LINEAGE), \
             mock.patch.object(history.sandbox_red_release, "verified_release_chain", REAL_CHAIN), \
             mock.patch.object(history, "_bind_first_moves", REAL_BIND_FIRST), \
             mock.patch.object(history.sandbox_red_release.likeness.cw, "load_cfg", return_value={}), \
             mock.patch.object(history.sandbox_red_release.likeness.cw, "storage_root",
                               return_value=self.root / "_reports"):
            self.publish(["first"], apply=True)
            self.publish(["first"], check=True)
            page = (self.root / "_reports" / "library" / "movement-history" / "history1" / "index.html").read_text(
                encoding="utf-8")
            self.assertIn("Physical source rows: 1; current Review members: 1", page)
            self.assertIn("unchanged path", page)
            self.assertIn(final, page)
            (backup / "saved.jpg").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "first release recovery photo changed"):
                self.publish(["first"], check=True)

    @unittest.skipUnless(os.name == "nt", "exclusive Windows directory rename")
    def test_real_successor_preserves_historical_chain_after_overwrites_and_retirement(self):
        from tools.art.likeness_library import empty_retirement, normal_rebase

        def write(path, content):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        initial = "One/gallery/a.jpg"
        original_source = "Potentials/Alpha/gallery/a.jpg"
        middle = "Middle/review/a.jpg"
        released = "Final/review/a.jpg"
        final = "Corrected/gallery/a.jpg"
        unchanged = "Other/gallery/b.jpg"
        derivative = "Potentials/Alpha/gallery_944x1104/old.jpg"
        untouched_derivative = "Potentials/Alpha/gallery_944x1104/untouched.jpg"
        new_derivative = "Potentials/Alpha/gallery_944x1104/new.jpg"
        write(self.root / unchanged, b"untouched")
        write(self.root / released, b"image")
        write(self.root / untouched_derivative, b"retired untouched derivative")
        original_review = self.root / "_reports" / "library" / "people_gallery_review.html"
        old_review = ('<script id="review-data">' + json.dumps([{
            "folder": "One", "bucket": "Gallery", "name": "a.jpg", "photoId": "p<1>",
            "contentSha256": self.photo_hash,
        }]) + '</script>').encode()
        write(original_review, old_review)
        first_move = {"source": original_source, "destination": initial,
                      "photoId": "p<1>", "sha256": self.photo_hash}
        self.receipt.write_text(json.dumps({
            "kind": "normal-rebase-receipt", "schemaVersion": 1, "status": "applied",
            "root": str(self.root), "runId": "base", "viewerPaths": [str(original_review)],
            "sourceHashes": {original_source: self.photo_hash},
            "moves": [first_move], "publishedNative": [{"native": initial, "sha256": self.photo_hash}],
            "plan": {"sourceRows": [{"owner": "Potentials/Alpha", "source": original_source,
                                      "sourceHash": self.photo_hash, "photoId": "p<1>"}],
                     "sourceHashes": {original_source: self.photo_hash}, "moves": [first_move]},
        }), encoding="utf-8")
        historical_review = ('<script id="review-data">' + json.dumps([{
            "photoId": "p<1>", "generationSource": released, "contentSha256": self.photo_hash,
        }]) + '</script>').encode()
        write(self.review, historical_review)
        historical_review_hash = history._sha(self.review)
        self.manifest.write_text(json.dumps({
            "receipt": str(self.receipt), "inputs": {
                str(self.receipt): history._sha(self.receipt), str(original_review): history._sha(original_review),
            },
            "redCandidates": [{"photoId": "p<1>", "currentPath": initial, "nativeSha256": self.photo_hash}],
        }), encoding="utf-8")
        first_manifest_hash = history._sha(self.manifest)
        first_backup = self.root / "_backup" / "first-real"
        write(first_backup / "saved.jpg", b"image")
        first_manifest = first_backup / "manifest.json"
        first_manifest.write_text(json.dumps({"entries": [
            {"source": str(self.root / initial), "backup": "saved.jpg", "sha256": self.photo_hash},
        ]}), encoding="utf-8")
        report = self.root / "_reports" / "library" / "first" / "report.json"
        report.write_text(json.dumps({
            "kind": "sandbox-red-release-experiment", "root": str(self.root), "runId": "first",
            "snapshotReportManifestSHA256": first_manifest_hash,
            "unaffectedNativeSHA256": {unchanged: digest(b"untouched")},
            "moves": [{"photoId": "p<1>", "source": initial, "destination": middle, "sha256": self.photo_hash}],
        }), encoding="utf-8")
        first_journal = self.root / "_reports" / "runs" / "first" / "publication-journal.json"
        first_journal.write_text(json.dumps({
            "kind": "normal-publication", "status": "applied", "root": str(self.root), "runId": "first",
            "backup": str(first_backup), "backupManifestSHA256": history._sha(first_manifest),
            "bindings": {"snapshotReportManifestSHA256": first_manifest_hash},
            "after": {report.relative_to(self.root).as_posix(): history._sha(report),
                      middle: self.photo_hash, derivative: digest(b"old derivative"),
                      untouched_derivative: digest(b"retired untouched derivative")},
            "removed": [initial],
        }), encoding="utf-8")
        second_backup = self.root / "_backup" / "second-real"
        write(second_backup / "native.jpg", b"image")
        write(second_backup / "derivative.jpg", b"old derivative")
        second_manifest = second_backup / "manifest.json"
        second_manifest.write_text(json.dumps({"entries": [
            {"source": str(self.root / middle), "backup": "native.jpg", "sha256": self.photo_hash},
            {"source": str(self.root / derivative), "backup": "derivative.jpg", "sha256": digest(b"old derivative")},
        ]}), encoding="utf-8")
        second_report = self.root / "_reports" / "library" / "second" / "report.json"
        second_report.write_text(json.dumps({
            "kind": "sandbox-red-release-experiment", "root": str(self.root), "runId": "second",
            "snapshotReportManifestSHA256": first_manifest_hash, "planSHA256": "plan",
            "lineageJournalSHA256": [history._sha(first_journal)], "unaffectedNativeSHA256": {},
            "moves": [{"photoId": "p<1>", "source": middle, "destination": released, "sha256": self.photo_hash}],
        }), encoding="utf-8")
        second_journal = self.root / "_reports" / "runs" / "second" / "publication-journal.json"
        second_journal.write_text(json.dumps({
            "kind": "normal-publication", "status": "applied", "root": str(self.root), "runId": "second",
            "backup": str(second_backup), "backupManifestSHA256": history._sha(second_manifest),
            "bindings": {"planSHA256": "plan"}, "removed": [middle, new_derivative],
            "after": {second_report.relative_to(self.root).as_posix(): history._sha(second_report),
                      released: self.photo_hash, derivative: digest(b"old derivative")},
        }), encoding="utf-8")
        # A successor legitimately overwrites a derivative, both Reviews, the
        # audit manifest and the release report, and removes the released native.
        old_files = {
            released: b"image",
            derivative: b"old derivative",
            report.relative_to(self.root).as_posix(): report.read_bytes(),
            second_report.relative_to(self.root).as_posix(): second_report.read_bytes(),
            original_review.relative_to(self.root).as_posix(): old_review,
            self.review.relative_to(self.root).as_posix(): historical_review,
            self.manifest.relative_to(self.root).as_posix(): self.manifest.read_bytes(),
        }
        backup = self.root / "_backup" / "corrected-real"
        backup.mkdir(parents=True)
        entries = []
        for index, (relative, content) in enumerate(old_files.items()):
            name = f"saved-{index}.bin"
            write(backup / name, content)
            entries.append({"source": str(self.root / pathlib.PurePosixPath(relative)),
                            "backup": name, "sha256": digest(content)})
        backup_manifest = backup / "manifest.json"
        backup_manifest.write_text(json.dumps({"entries": entries}), encoding="utf-8")
        (self.root / pathlib.PurePosixPath(released)).unlink()
        write(self.root / derivative, b"new derivative")
        write(self.root / new_derivative, b"created by rebase")
        write(report, b'{"replaced":true}')
        write(second_report, b'{"replaced":true}')
        write(self.review, b"new review")
        write(self.manifest, b"new audit")
        corrected_review = ('<script id="review-data">' + json.dumps([{
            "folder": "Corrected", "bucket": "Gallery", "name": "a.jpg", "photoId": "p<1>",
            "contentSha256": digest(b"corrected"),
        }]) + '</script>').encode()
        write(original_review, corrected_review)
        write(self.root / final, b"corrected")
        journal = self.root / "corrected-journal.json"
        after = {relative: history._sha(self.root / pathlib.PurePosixPath(relative))
                 for relative in (derivative, new_derivative, final, report.relative_to(self.root).as_posix(),
                                  second_report.relative_to(self.root).as_posix(),
                                  original_review.relative_to(self.root).as_posix(),
                                  self.review.relative_to(self.root).as_posix(),
                                  self.manifest.relative_to(self.root).as_posix())}
        journal_data = {
            "kind": "normal-publication", "status": "applied", "root": str(self.root), "runId": "corrected",
            "bindings": {}, "backup": str(backup), "backupManifestSHA256": history._sha(backup_manifest),
            "after": after, "removed": [released],
        }
        journal.write_text(json.dumps(journal_data), encoding="utf-8")
        corrected_receipt = self.root / "corrected-receipt.json"
        move = {"source": released, "destination": final, "photoId": "p<1>", "sha256": self.photo_hash}
        corrected_data = {
            "kind": "normal-rebase-receipt", "schemaVersion": 1, "status": "applied", "root": str(self.root),
            "runId": "corrected", "bindings": {}, "journal": str(journal),
            "implementationSHA256": history._sha(pathlib.Path(normal_rebase.__file__)),
            "viewerPaths": [str(original_review)], "moves": [move],
            "sourceHashes": {released: self.photo_hash},
            "publishedNative": [{"native": final, "sha256": digest(b"corrected")}],
            "plan": {"sourceRows": [{"owner": "Final", "source": released,
                                      "sourceHash": self.photo_hash, "photoId": "p<1>"}],
                     "sourceHashes": {released: self.photo_hash}, "moves": [move],
                     "releaseLineage": {
                         "receipt": str(self.receipt), "audit": str(self.audit), "review": str(self.review_dir),
                         "runs": ["first", "second"],
                         "journalSHA256": [history._sha(first_journal), history._sha(second_journal)],
                         "inputs": {"receiptSHA256": history._sha(self.receipt),
                                    "priorManifestSHA256": first_manifest_hash,
                                    "currentReviewSHA256": historical_review_hash},
                         "producers": {},
                     }},
        }
        corrected_receipt.write_text(json.dumps(corrected_data), encoding="utf-8")
        with mock.patch.object(history.normal_recap, "collect", REAL_RECAP), \
             mock.patch.object(history.sandbox_red_release.normal_recap, "collect", REAL_RELEASE_RECAP), \
             mock.patch.object(history.sandbox_red_release, "verified_current_lineage", REAL_LINEAGE), \
             mock.patch.object(history.sandbox_red_release, "verified_release_chain", REAL_CHAIN), \
             mock.patch.object(history, "_bind_first_moves", REAL_BIND_FIRST), \
             mock.patch.object(history.sandbox_red_release.likeness.cw, "load_cfg", return_value={}), \
             mock.patch.object(history.sandbox_red_release.likeness.cw, "storage_root",
                               return_value=self.root / "_reports"):
            runs = ["first", "second"]
            with self.assertRaisesRegex(ValueError, "cover all"):
                self.publish(runs)
            self.publish(runs, corrected_receipt=corrected_receipt)
            self.publish(runs, corrected_receipt=corrected_receipt, apply=True)
            self.publish(runs, corrected_receipt=corrected_receipt, check=True)
            existing = self.root / "_reports/library/movement-history/history1"
            existing_bytes = {path: path.read_bytes() for path in existing.iterdir()}
            page = (self.root / "_reports" / "library" / "movement-history" / "history1" / "index.html").read_text(
                encoding="utf-8")
            self.assertIn("1 of 1 released photos chained through corrected rebase", page)
            self.assertIn("Image missing; no substitute", page)
            self.assertLess(page.index(middle), page.index(released))
            self.assertLess(page.index(released), page.index(final))
            self.assertIn(final, page)

            saved = backup / entries[0]["backup"]
            saved.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "recovery file changed"):
                self.publish(runs, corrected_receipt=corrected_receipt, check=True)
            saved.unlink()
            with self.assertRaisesRegex(ValueError, "recovery file missing"):
                self.publish(runs, corrected_receipt=corrected_receipt, check=True)
            saved.write_bytes(b"image")
            original_manifest = backup_manifest.read_bytes()
            backup_manifest.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "recovery manifest changed"):
                self.publish(runs, corrected_receipt=corrected_receipt, check=True)
            backup_manifest.write_bytes(original_manifest)
            duplicate = json.loads(original_manifest)
            duplicate["entries"].append(duplicate["entries"][0])
            backup_manifest.write_text(json.dumps(duplicate), encoding="utf-8")
            journal_data["backupManifestSHA256"] = history._sha(backup_manifest)
            journal.write_text(json.dumps(journal_data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "snapshot is ambiguous"):
                self.publish(runs, corrected_receipt=corrected_receipt, check=True)
            missing = json.loads(original_manifest)
            missing["entries"] = missing["entries"][1:]
            backup_manifest.write_text(json.dumps(missing), encoding="utf-8")
            journal_data["backupManifestSHA256"] = history._sha(backup_manifest)
            journal.write_text(json.dumps(journal_data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "published content changed"):
                self.publish(runs, corrected_receipt=corrected_receipt, check=True)
            backup_manifest.write_bytes(original_manifest)
            journal_data["backupManifestSHA256"] = history._sha(backup_manifest)
            journal.write_text(json.dumps(journal_data), encoding="utf-8")
            write(self.root / unchanged, b"changed")
            with self.assertRaisesRegex(ValueError, "unaffected native changed"):
                self.publish(runs, corrected_receipt=corrected_receipt, check=True)
            write(self.root / unchanged, b"untouched")
            corrected_data["plan"]["sourceRows"][0]["photoId"] = "unrelated"
            corrected_receipt.write_text(json.dumps(corrected_data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unrelated or ambiguous"):
                self.publish(runs, corrected_receipt=corrected_receipt, check=True)
            corrected_data["plan"]["sourceRows"][0]["photoId"] = "p<1>"
            corrected_receipt.write_text(json.dumps(corrected_data), encoding="utf-8")

            # Retire only the now-empty identity in this disposable fixture.
            (self.root / "_retired/Potentials").mkdir(parents=True)
            (self.root / "Potentials/Alpha/gallery").mkdir()
            relative_receipt = self.receipt.relative_to(self.root).as_posix()
            corrected_relative = corrected_receipt.relative_to(self.root).as_posix()
            relative_journal = journal.relative_to(self.root).as_posix()
            def retirement_preview():
                for attempt in range(5):
                    try:
                        return empty_retirement.preview(
                            self.root, ["Potentials/Alpha"], relative_receipt, relative_journal, cfg={},
                            corrected_receipt=corrected_relative,
                        )
                    except ValueError as exc:
                        if "attributes=268435472/16" not in str(exc) or attempt == 4:
                            raise
                        time.sleep(0.1)

            # Even a separately hash-bound corrected receipt cannot substitute
            # a different ordered release lineage.
            corrected_data["plan"]["releaseLineage"]["runs"] = ["second", "first"]
            corrected_receipt.write_text(json.dumps(corrected_data), encoding="utf-8")
            bad_plan, bad_digest = retirement_preview()
            bad_journal = "_reports/runs/retirement-bad.json"
            empty_retirement.apply(self.root, bad_plan, bad_digest, bad_journal, cfg={})
            with self.assertRaisesRegex(ValueError, "complete retirement source lineage"):
                self.publish(runs, corrected_receipt=corrected_receipt,
                             retirement_journal=bad_journal, retirement_digest=bad_digest)
            empty_retirement.recover(self.root, bad_journal, bad_digest, apply=True)
            corrected_data["plan"]["releaseLineage"]["runs"] = runs
            corrected_receipt.write_text(json.dumps(corrected_data), encoding="utf-8")
            retirement_plan, retirement_digest = retirement_preview()
            retirement_journal = "_reports/runs/retirement.json"
            empty_retirement.apply(self.root, retirement_plan, retirement_digest, retirement_journal, cfg={})
            with self.assertRaisesRegex(ValueError, "published content changed"):
                self.publish(runs, corrected_receipt=corrected_receipt)
            # A new report ID is required; the earlier report is immutable evidence.
            kwargs = {"corrected_receipt": corrected_receipt, "retirement_journal": retirement_journal,
                      "retirement_digest": retirement_digest}
            with contextlib.redirect_stdout(io.StringIO()):
                history.publish(self.root, self.receipt, self.audit, self.review_dir, runs,
                                "_reports", "with-retirement", **kwargs, apply=True)
                history.publish(self.root, self.receipt, self.audit, self.review_dir, runs,
                                "_reports", "with-retirement", **kwargs, check=True)
            state = json.loads((self.root / "_reports/library/movement-history/with-retirement/report.json").read_bytes())
            self.assertEqual(state["corrected"]["retirement"]["planSHA256"], retirement_digest)
            self.assertEqual(state["corrected"]["retirement"]["sourceReceipt"], str(self.receipt))
            self.assertEqual(state["corrected"]["retirement"]["sourceReceiptSHA256"], history._sha(self.receipt))
            self.assertEqual(state["corrected"]["retirement"]["journalSHA256"],
                             history._sha(self.root / retirement_journal))
            self.assertIn("retirement does not establish additional photo movements",
                          (self.root / "_reports/library/movement-history/with-retirement/index.html").read_text(
                              encoding="utf-8"))
            self.assertEqual(existing_bytes, {path: path.read_bytes() for path in existing.iterdir()})
            with self.assertRaisesRegex(ValueError, "different or incomplete"):
                self.publish(runs, **kwargs, apply=True)
            self.assertEqual(existing_bytes, {path: path.read_bytes() for path in existing.iterdir()})
            with self.assertRaisesRegex(ValueError, "preview digest"):
                self.publish(runs, corrected_receipt=corrected_receipt, retirement_journal=retirement_journal,
                             retirement_digest="0" * 64)
            with self.assertRaisesRegex(ValueError, "invalid retirement preview digest"):
                self.publish(runs, corrected_receipt=corrected_receipt, retirement_journal=retirement_journal,
                             retirement_digest="bad")
            source_bytes = self.receipt.read_bytes()
            self.receipt.write_bytes(source_bytes + b" ")
            with self.assertRaisesRegex(ValueError, "source receipt changed"):
                self.publish(runs, **kwargs)
            self.receipt.write_bytes(source_bytes)
            corrected_bytes = corrected_receipt.read_bytes()
            corrected_receipt.write_bytes(corrected_bytes + b" ")
            with self.assertRaisesRegex(ValueError, "corrected rebase receipt changed"):
                self.publish(runs, **kwargs)
            corrected_receipt.write_bytes(corrected_bytes)
            first_saved = first_backup / "saved.jpg"
            first_saved.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "first release recovery photo changed"):
                self.publish(runs, **kwargs)
            first_saved.write_bytes(b"image")
            corrected_saved = backup / entries[0]["backup"]
            corrected_saved.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "recovery file changed"):
                self.publish(runs, **kwargs)
            corrected_saved.write_bytes(b"image")
            view = history.sandbox_red_release.VerifiedRebaseSuccessor(
                self.root, corrected_receipt, retirement_journal=retirement_journal,
                retirement_digest=retirement_digest,
            )
            # Touched paths come from the earlier recovery snapshot, not the retired current bytes.
            self.assertEqual(view.required(self.root / derivative), b"old derivative")
            self.assertEqual(view.required(self.root / untouched_derivative), b"retired untouched derivative")
            self.assertIsNone(view.read(self.root / "Potentials/Alpha/gallery/missing.jpg"))
            self.assertIsNone(view.read(self.root / new_derivative))
            self.assertEqual(view.required(self.root / released), b"image")
            corrected_native = self.root / final
            corrected_native.unlink()
            with self.assertRaisesRegex(ValueError, "predecessor published content changed"):
                view.verify_unchanged()
            corrected_native.write_bytes(b"corrected")
            original_sha = history.sandbox_red_release.metadata.content_sha256
            with mock.patch.object(history.sandbox_red_release.metadata, "content_sha256",
                                   wraps=original_sha) as content_sha:
                content_sha.side_effect = lambda path: (
                    "0" * 64 if pathlib.Path(path) == pathlib.Path(normal_rebase.__file__) else original_sha(path)
                )
                with self.assertRaisesRegex(ValueError, "implementation changed"):
                    view.verify_unchanged()
            journal_path = self.root / retirement_journal
            journal_bytes = journal_path.read_bytes()
            interrupted = json.loads(journal_bytes)
            interrupted["status"] = "recovering"
            journal_path.write_text(json.dumps(interrupted), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not fully applied"):
                self.publish(runs, **kwargs)
            journal_path.write_bytes(journal_bytes)
            archived = self.root / "_retired" / untouched_derivative
            archived.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "inventory changed"):
                with contextlib.redirect_stdout(io.StringIO()):
                    history.publish(self.root, self.receipt, self.audit, self.review_dir, runs,
                                    "_reports", "with-retirement", **kwargs, check=True)
            archived.unlink()
            with self.assertRaisesRegex(ValueError, "inventory changed"):
                self.publish(runs, **kwargs)


if __name__ == "__main__":
    unittest.main()
