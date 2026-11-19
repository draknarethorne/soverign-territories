"""Saved SIMPLE reports preserve source accounting without rerunning the pipeline."""
import contextlib
import copy
import hashlib
import io
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art.likeness_library import normal_recap, normal_transaction, rebase_recap


ROOT = pathlib.Path(__file__).resolve().parents[4]


class NormalRecapTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="normal-recap-", dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name)
        self.library = self.root / "_reports" / "library"
        self.library.mkdir(parents=True)
        self.report = self.root / "_reports" / "runs" / "run.json"
        self.report.parent.mkdir()
        self.a = "Angels/Ava/gallery/ava_image_1.jpg"
        self.b = "Various/gallery/image_2.jpg"
        self.target = "Models/Bea/gallery/bea_image_2.jpg"
        self.held = "Various/review/image_3.jpg"
        self.h1 = hashlib.sha256(b"original1").hexdigest()
        self.h2 = hashlib.sha256(b"original2").hexdigest()
        self.h3 = hashlib.sha256(b"original3").hexdigest()
        self.native = hashlib.sha256(b"prepared2").hexdigest()
        for name in (self.a, self.target, self.held):
            path = self.root / pathlib.PurePosixPath(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"not read by report rendering")
        for name in ("people_gallery.html",):
            (self.library / name).write_text("<html></html>", encoding="utf-8")
        self.thumb = self.library / "people_gallery_review_files" / "thumb.jpg"
        self.thumb.parent.mkdir()
        self.thumb.write_bytes(b"existing thumbnail")
        sources = [
            {"source": self.a, "sourceHash": self.h1, "photoId": "photo:image_1"},
            {"source": self.b, "sourceHash": self.h2, "photoId": "photo:image_2"},
            {"source": self.target, "sourceHash": self.h2, "photoId": "photo:image_2"},
            {"source": self.held, "sourceHash": self.h3, "photoId": "photo:image_3"},
        ]
        move = {"source": self.b, "destination": self.target, "sha256": self.h2,
                "photoId": "photo:image_2", "reason": "qualified admission"}
        self.receipt = {
            "kind": "normal-rebase-receipt", "schemaVersion": 1, "status": "applied",
            "root": str(self.root), "runId": "run1", "profile": "lean",
            "moves": [move], "sourceHashes": {r["source"]: r["sourceHash"] for r in sources},
            "publishedNative": [{"native": self.target, "sha256": self.native}],
            "plan": {
                "sourceRows": sources, "sourceHashes": {r["source"]: r["sourceHash"] for r in sources},
                "moves": [move], "exactAliasTargets": {self.target: {"source": self.b, "sha256": self.h2}},
                "frozenConsistencyCheck": {"passCount": 1, "lowMemberChecks": [{}, {}],
                                          "recommendations": [{"photoId": "photo:image_1",
                                                               "reason": "protected recommendation only"}]},
            },
        }
        self.records = [self.record(self.a, "photo:image_1", self.h1),
                        self.record(self.target, "photo:image_2", self.native),
                        self.record(self.held, "photo:image_3", self.h3)]
        self.save()

    def record(self, path, identifier, checksum):
        person, bucket = rebase_recap.person_and_bucket(path)
        return {
            "folder": person, "bucket": bucket.title(), "name": pathlib.PurePosixPath(path).name,
            "photoId": identifier, "contentSha256": checksum, "score": .1,
            "scoreContext": {"coreMember": False}, "identityProtected": True,
            "workflowSelected": True, "identityAnchor": False, "reason": "saved explanation",
            "comparison": "saved own core", "closestMatches": [{"folder": "Sisters/Sia", "score": .7}],
            "thumbnail": "people_gallery_review_files/thumb.jpg",
        }

    def save(self):
        self.report.write_text(json.dumps(self.receipt), encoding="utf-8")
        self.review = self.library / "people_gallery_review.html"
        self.review.write_text('<html><script id="review-data" type="application/json">'
                               + json.dumps(self.records) + "</script></html>", encoding="utf-8")

    def run_report(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return rebase_recap.main([str(self.report), *args])

    def test_archived_copies_are_accounted_for_without_borrowing_keeper_scores(self):
        destination = "_duplicates/run1/0123456789abcdef01234567/" + self.target
        plan = self.receipt["plan"]
        plan.pop("exactAliasTargets")
        for row in plan["sourceRows"]:
            if row["source"] == self.b:
                row["collisionRule"] = "exact-byte keeper"
            if row["source"] == self.target:
                row.update(sourceStatus="duplicate-archive", reason="exact-byte copy")
        plan["duplicateArchives"] = {self.target: {
            "source": self.target, "destination": destination, "sha256": self.h2,
            "photoId": "photo:image_2", "reason": "exact-byte copy", "selectedSource": self.b,
        }}
        self.receipt["publishedNative"].append({"native": destination, "sha256": self.h2})
        self.save()
        data = normal_recap.collect(self.report)
        archived = next(row for row in data["rows"] if row["duplicateArchive"])
        self.assertEqual(archived["destination"], destination)
        self.assertIsNone(archived["score"])
        self.assertNotIn("_duplicates", data["newIdentities"])
        self.assertEqual(data["snapshotMatched"], 3)
        page = normal_recap.render(data, self.library / "recap.html")
        self.assertIn('id="collisions"', page)
        self.assertIn("exact-byte keeper", page)
        self.assertIn(destination, page)
        self.assertIn('href="#collisions"', page)
        self.assertIn("1 duplicate archive(s)", page)
        self.assertIn("duplicate archives only; no identity rename", page)
        self.receipt["publishedNative"][-1]["sha256"] = self.h3
        self.save()
        with self.assertRaisesRegex(ValueError, "unbound duplicate archive"):
            normal_recap.collect(self.report)

    def test_applied_report_preserves_transaction_bound_preview_reports(self):
        self.receipt["status"] = "preview"
        self.receipt["kind"] = "normal-rebase-preview"
        self.save()
        self.assertEqual(self.run_report("--apply"), 0)
        folder = self.library / "rebase-recap"
        before = {path: path.read_bytes() for path in folder.iterdir() if path.is_file()}
        journal = self.report.parent / "publication-journal.json"
        journal.write_text(json.dumps({
            "kind": "normal-publication", "status": "applied", "root": str(self.root),
            "after": {path.relative_to(self.root).as_posix(): hashlib.sha256(payload).hexdigest()
                      for path, payload in before.items()},
            "removed": [],
        }), encoding="utf-8")
        self.receipt["status"] = "applied"
        self.receipt["kind"] = "normal-rebase-receipt"
        self.save()
        self.assertEqual(self.run_report("--apply"), 0)
        normal_transaction.verify(self.root, journal)
        self.assertEqual({path: path.read_bytes() for path in before}, before)
        self.assertTrue((folder / "applied" / "run1.html").is_file())
        self.assertEqual(self.run_report("--check"), 0)

    def test_preview_apply_check_conserve_aliases_and_use_existing_navigation_without_hashing_photos(self):
        before = self.report.read_bytes()
        out = self.library / "rebase-recap" / "applied" / "run1.html"
        with mock.patch.object(rebase_recap, "_file_verification",
                               side_effect=AssertionError("no native hash campaign")):
            self.assertEqual(self.run_report("--dry-run"), 0)
            self.assertFalse(out.exists())
            self.assertEqual(self.run_report("--apply"), 0)
            self.assertEqual(self.run_report("--check"), 0)
        self.assertEqual(self.report.read_bytes(), before)
        page = out.read_text(encoding="utf-8")
        audit = out.with_name("run1-audit.html").read_text(encoding="utf-8")
        self.assertIn("4 physical source rows", page)
        self.assertIn("3 distinct destinations + 1", page)
        self.assertIn('href="#flows"', page)
        self.assertNotRegex(page, r'href="#[^"]+" target="_blank"')
        self.assertIn('target="_blank" rel="noopener noreferrer"', page)
        self.assertIn("people_gallery_review.html?person=", page)
        self.assertIn("Current photo (not rehashed)", page)
        self.assertIn("protected recommendation only", audit)
        self.assertIn("workflow reference outside active core", audit)
        self.assertIn('href="run1.html#flows"', audit)

    def test_unbound_moves_and_unproven_alias_coalescence_refuse(self):
        original = copy.deepcopy(self.receipt)
        for change in ("move", "alias", "hash"):
            self.receipt = copy.deepcopy(original)
            if change == "move":
                self.receipt["plan"]["moves"][0]["photoId"] = "photo:wrong"
            elif change == "alias":
                self.receipt["plan"]["exactAliasTargets"] = {}
            else:
                self.receipt["plan"]["sourceRows"][0]["sourceHash"] = self.h2
            self.save()
            self.assertEqual(self.run_report("--apply"), 1)
            self.assertFalse((self.library / "rebase-recap").exists())

    def replacement(self):
        previous = hashlib.sha256(b"previous native").hexdigest()
        target = self.receipt["plan"]["sourceRows"][2]
        target.update(
            sourceHash=previous, sourceStatus="preserved-version", selectedSource=self.b,
        )
        self.receipt["plan"]["sourceRows"][1]["sourceStatus"] = "incoming-update"
        self.receipt["sourceHashes"][self.target] = previous
        self.receipt["plan"]["sourceHashes"][self.target] = previous
        self.receipt["plan"]["exactAliasTargets"] = {}
        self.receipt["plan"]["incomingUpdates"] = {"photo:image_2": {
            "source": self.b, "owner": "Models/Bea", "previousSource": self.target,
            "previousHash": previous, "sourceHash": self.h2,
        }}

    def test_bound_replacement_preserves_prior_version_without_an_extra_current_vote(self):
        self.replacement()
        self.save()
        before = self.report.read_bytes()
        data = normal_recap.collect(self.report)
        self.assertEqual(data["physicalSources"], 4)
        self.assertEqual(data["physicalDestinations"], 3)
        self.assertEqual(data["coalescedAliases"], 0)
        self.assertEqual(data["supersededVersions"], 1)
        previous = next(row for row in data["rows"] if row["source"] == self.target)
        self.assertEqual(previous["kind"], "superseded-version")
        self.assertEqual(previous["preparedSHA256"], previous["sha256"])
        self.assertIsNone(previous["preview"])
        current = next(item for item in data["auditRecords"] if item["row"]["photoId"] == "photo:image_2")
        self.assertEqual(current["row"]["source"], self.b)
        self.assertEqual(data["snapshotMatched"], 3)
        self.assertEqual(self.run_report("--apply"), 0)
        self.assertEqual(self.run_report("--check"), 0)
        page = (self.library / "rebase-recap" / "applied" / "run1.html").read_text(encoding="utf-8")
        self.assertIn("1 superseded native versions", page)
        self.assertEqual(self.report.read_bytes(), before)

    def test_replacement_requires_exact_old_new_and_classification_bindings(self):
        self.replacement()
        original = copy.deepcopy(self.receipt)
        for field in ("source", "owner", "previousSource", "previousHash", "sourceHash", "sourceStatus", "selectedSource"):
            with self.subTest(field=field):
                self.receipt = copy.deepcopy(original)
                if field in ("sourceStatus", "selectedSource"):
                    self.receipt["plan"]["sourceRows"][2][field] = "wrong"
                else:
                    self.receipt["plan"]["incomingUpdates"]["photo:image_2"][field] = "wrong"
                self.save()
                with self.assertRaises(ValueError):
                    normal_recap.collect(self.report)

    def test_stale_review_hash_or_id_is_not_presented_as_current_score_evidence(self):
        self.records[0]["contentSha256"] = self.h2
        self.records[1]["photoId"] = "photo:wrong"
        self.save()
        data = normal_recap.collect(self.report)
        self.assertEqual(data["snapshotMatched"], 1)
        self.assertEqual(len(data["snapshotDiagnostics"]), 2)
        self.assertEqual(len(data["auditRecords"]), 1)

    def test_missing_review_id_pairs_only_by_exact_physical_path_and_native_hash(self):
        self.records[0]["photoId"] = None
        self.save()
        data = normal_recap.collect(self.report)
        self.assertEqual(data["snapshotMatched"], 3)
        self.assertEqual(data["snapshotIdUnavailable"], 1)
        self.assertEqual(len(data["auditRecords"]), 3)

    def test_check_refuses_output_tampering_and_changed_review_input(self):
        self.assertEqual(self.run_report("--apply"), 0)
        out = self.library / "rebase-recap" / "applied" / "run1-audit.html"
        out.write_text("changed", encoding="utf-8")
        self.assertEqual(self.run_report("--check"), 1)
        self.assertEqual(self.run_report("--apply"), 0)
        out.with_name("index.html").unlink()
        self.assertEqual(self.run_report("--check"), 1)
        self.assertEqual(self.run_report("--apply"), 0)
        self.records[0]["reason"] = "later evidence"
        self.save()
        self.assertEqual(self.run_report("--check"), 1)

    def test_same_source_run_comparison_and_different_source_refusal(self):
        other = self.report.with_name("other.json")
        value = copy.deepcopy(self.receipt)
        value["runId"] = "other"
        other.write_text(json.dumps(value), encoding="utf-8")
        self.assertEqual(self.run_report("--compare", str(other), "--apply"), 0)
        page = (self.library / "rebase-recap" / "applied" / "run1.html").read_text(encoding="utf-8")
        self.assertIn("0 photos placed differently", page)
        value["sourceHashes"][self.a] = self.h2
        value["plan"]["sourceHashes"][self.a] = self.h2
        value["plan"]["sourceRows"][0]["sourceHash"] = self.h2
        other.write_text(json.dumps(value), encoding="utf-8")
        self.assertEqual(self.run_report("--compare", str(other), "--apply"), 1)


if __name__ == "__main__":
    unittest.main()
