"""Fixture-only integration of initial Gallery release and preview binding."""
import copy
import contextlib
import hashlib
import io
import json
import pathlib
import unittest
from unittest import mock

import numpy as np

from tools.art.likeness_library import metadata, normal_rebase
from tools.art.likeness_library.reconciliation import plan_reconciliation
from tools.art.likeness_library.tests import test_normal_rebase as fixtures


class SingleVotePerContentTests(unittest.TestCase):
    def test_unresolved_release_goes_to_highest_rival_review_or_various(self):
        from tools.art.likeness_library import normal_admission

        held = {"photoId": "photo:x", "reason": "held", "preserveStaged": True}
        rivals = [{"folder": "Sisters/Drakness", "score": .34}, {"folder": "Potentials/A", "score": .3}]
        placed = normal_admission.unresolved_release_review(held, rivals)
        self.assertEqual(placed["reviewDestination"], "Sisters/Drakness/review")
        self.assertFalse(placed["preserveStaged"])
        self.assertFalse(placed["referenceEligible"])
        self.assertIsNone(placed["destination"])
        locked = normal_admission.unresolved_release_review(held, rivals, locked=True)
        self.assertEqual(locked["reviewDestination"], "Potentials/A/review")
        none = normal_admission.unresolved_release_review(held, [])
        self.assertEqual(none["reviewDestination"], "Various/review")
        self.assertIsNone(none["unresolvedReleaseReview"]["score"])
        self.assertTrue(held["preserveStaged"])

    def test_distinct_sources_with_identical_prepared_measurement_keep_one_vote(self):
        rows = [
            {"photoId": pid, "currentPath": path, "sha256": source, "measurementSha256": measured,
             "referenceEligible": eligible}
            for pid, path, source, measured, eligible in (
                ("photo:b", "Sisters/A/gallery/b.jpg", "1" * 64, "a" * 64, True),
                ("photo:a", "Sisters/A/gallery/a.jpg", "2" * 64, "a" * 64, True),
                ("photo:c", "Sisters/A/gallery/c.jpg", "3" * 64, "c" * 64, True),
                ("photo:d", "Sisters/A/gallery/d.jpg", "3" * 64, "d" * 64, False),
            )
        ]
        records = normal_rebase._single_vote_per_content(rows)
        self.assertEqual([row["referenceEligible"] for row in rows], [False, True, True, False])
        self.assertEqual(records, [{
            "keeper": "photo:a", "nonVoting": ["photo:b"],
            "paths": ["Sisters/A/gallery/a.jpg", "Sisters/A/gallery/b.jpg"],
        }])


class FreshRebaseIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.NormalRebaseTests(methodName="runTest")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        f = self.fixture
        self.paths = [
            f.photo("Prospects/Owner/gallery/owner_image_101.jpg", b"owner one"),
            f.photo("Prospects/Owner/gallery/owner_image_102.jpg", b"owner two"),
            f.photo("Prospects/Owner/gallery/owner_image_103.jpg", b"outlier"),
            f.photo("Prospects/Owner/gallery/owner_image_104.jpg", b"owner one"),
            f.photo("Models/Rival/gallery/rival_image_201.jpg", b"rival one"),
            f.photo("Models/Rival/gallery/rival_image_202.jpg", b"rival two"),
            f.photo("Prospects/Owner/gallery/owner_image_105.jpg", b"owner three"),
        ]
        folders = [
            ("Prospects", "Owner", f.root / "Prospects" / "Owner"),
            ("Models", "Rival", f.root / "Models" / "Rival"),
        ]
        self.api = f.stub_api(folders)
        base_space = self.api.Space

        class FixtureSpace(base_space):
            def __init__(self, photos, settings, mean=None):
                super().__init__(photos, settings, mean=np.zeros(3))

        self.api.Space = FixtureSpace
        self.model = {"fixture": "local-model"}
        self.model_id = hashlib.sha256(
            json.dumps(self.model, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.api.Embedder._model_identity = lambda _self, _cv2: (self.model, self.model_id)
        self.api.plan_reconciliation = plan_reconciliation
        self.api.invent_name = lambda seed, _taken: "Fixture-" + seed[:8]
        metadata.save_catalog(f.empty_catalog(), f.root / ".likeness-library.json")
        target = np.array([-.5, np.sqrt(.75), 0.])
        self.vectors = {
            "owner one": [1., 0., 0.],
            "owner two": [.8, .6, 0.],
            "owner three": [.7, np.sqrt(.51), 0.],
            "outlier": [-.55, np.sqrt(1 - .55 ** 2), 0.],
            "rival one": (np.sqrt(.84) * target + np.array([0., 0., .4])).tolist(),
            "rival two": (np.sqrt(.84) * target - np.array([0., 0., .4])).tolist(),
        }
        self.stack = self.enterContext(mock.patch.object(normal_rebase, "is_sandbox_working_path", return_value=True))
        self.enterContext(mock.patch.object(normal_rebase, "_infer", side_effect=self.infer))
        self.enterContext(mock.patch.object(normal_rebase, "_bindings", return_value={"fixture": "bound"}))
        self.enterContext(mock.patch.object(normal_rebase, "_fragment_evidence", return_value={}))
        self.enterContext(mock.patch.object(
            normal_rebase.normal_finish, "check_batch",
            side_effect=lambda _api, _space, _catalog, _policy, moves, **_kw: (
                list(moves), {"passCount": 1, "frozenRivals": {}, "corrections": []},
            ),
        ))
        self.permissions = self.enterContext(mock.patch.object(normal_rebase.maintenance, "_validate_permissions"))

    def infer(self, _api, _cache, _embed, path, **_kwargs):
        vector = self.vectors[pathlib.Path(path).read_bytes().decode()]
        checksum = metadata.content_sha256(path)
        return checksum, {
            "v": vector, "faces": 1, "px": 1000, "t": "fixture",
            "alignmentEvidence": {
                "state": "read-only-not-persisted", "sourceSha256": checksum,
                "model": self.model, "modelId": self.model_id,
            },
        }

    def plan(self, **kwargs):
        return normal_rebase._plan(
            self.fixture.root, "fast", "fresh-fixture", api=self.api,
            fresh_source_release=True, **kwargs,
        )[0]

    def test_pre_retirement_selection_archives_identical_copies_and_bound_apply(self):
        report = self.plan()
        assessment = report["freshSourceAssessment"]["assessment"]
        # Item (a): owner_image_101/104 are byte-identical; one is archived before selection.
        self.assertEqual(len(assessment), 6)
        archived = set(report["duplicateArchives"])
        self.assertEqual(len(archived), 1)
        self.assertTrue(archived <= {path.relative_to(self.fixture.root).as_posix() for path in (self.paths[0], self.paths[3])})
        archived_id = next(iter(report["duplicateArchives"].values()))["photoId"]
        self.assertNotIn(archived_id, {row["photoId"] for row in assessment})
        outlier = metadata.photo_id_from_name(self.paths[2].name)
        self.assertIn(outlier, {row["photoId"] for row in report["releasedPhotoBindings"]})
        selected = next(row for row in assessment if row["photoId"] == outlier)
        self.assertEqual(selected["band"], "red")
        self.assertNotIn(outlier, {
            pid for ids in report["referenceSnapshots"]["1"]["photoIds"].values() for pid in ids
        })
        self.assertFalse([row for row in assessment if row["sourceStatus"] == "same-content-nonvoting"])
        self.assertNotIn("reconsideredNonVotingEvidence", report)
        self.assertNotIn(archived_id, {row["photoId"] for row in report["moves"]})
        self.assertEqual(self.permissions.call_args.kwargs["released_bindings"], report["releasedPhotoBindings"])
        phase = next(row for row in report["phaseLog"] if row["phase"] == "fresh-source-release-selection")
        self.assertGreaterEqual(phase["durationSeconds"], 0)
        self.assertEqual((report["freshGalleryCount"], report["freshNonVotingCount"]), (6, 0))
        phases = [item["phase"] for item in report["phaseLog"]]
        self.assertLess(phases.index("fresh-source-measurement"), phases.index("fresh-source-release-selection"))
        self.assertLess(phases.index("fresh-source-release-selection"), phases.index("fresh-post-release-frozen-cores"))
        replay = self.plan(for_apply=True, reuse_plan=report)
        self.assertEqual(replay["freshSourceAssessment"], report["freshSourceAssessment"])
        self.assertEqual(replay["releasedPlanFingerprint"], report["releasedPlanFingerprint"])
        changed = copy.deepcopy(report)
        changed["freshSourceAssessment"]["assessment"][0]["score"] = -1.
        with self.assertRaisesRegex(ValueError, "assessment differs"):
            self.plan(for_apply=True, reuse_plan=changed)
        changed = copy.deepcopy(report)
        changed["freshMeasurementProof"]["modelId"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "measurement proof differs"):
            self.plan(for_apply=True, reuse_plan=changed)
        with self.assertRaisesRegex(ValueError, "requires its bound preview"):
            self.plan(for_apply=True)

    def test_quality_ineligible_release_is_held_unassigned_not_kept_or_scored(self):
        real_infer = self.infer

        def multi_face(*args, **kwargs):
            checksum, data = real_infer(*args, **kwargs)
            if pathlib.Path(args[3]).read_bytes() == b"outlier":
                data = {**data, "faces": 2, "f2": .9}
            return checksum, data

        with mock.patch.object(normal_rebase, "_infer", side_effect=multi_face):
            report = self.plan()
        outlier = metadata.photo_id_from_name(self.paths[2].name)
        selected = next(row for row in report["freshSourceAssessment"]["assessment"] if row["photoId"] == outlier)
        self.assertIsNone(selected["score"])
        self.assertTrue(selected["selected"])
        decision = next(row["decision"] for row in report["releasedDecisionEvidence"] if row["photoId"] == outlier)
        self.assertEqual(decision["reviewDestination"], "Various/review")
        self.assertFalse(decision["preserveStaged"])
        self.assertIsNone(decision["unresolvedReleaseReview"]["score"])
        self.assertIn("single-face quality gate", decision["reason"])

    def test_conflicting_lineage_and_non_sandbox_refuse_before_measurement(self):
        with self.assertRaisesRegex(ValueError, "cannot replay release lineage"):
            self.plan(released_bindings=[{"photoId": "x"}])
        with mock.patch.object(normal_rebase, "is_sandbox_working_path", return_value=False):
            with self.assertRaisesRegex(ValueError, "requires Sandbox"):
                self.plan()

    def test_identical_copy_is_archived_before_selection_and_never_votes(self):
        self.paths[6].unlink()
        report = self.plan()
        self.assertFalse([row for row in report["freshSourceAssessment"]["assessment"]
                          if row["sourceStatus"] == "same-content-nonvoting"])
        archive = next(iter(report["duplicateArchives"].values()))
        self.assertEqual(len(report["duplicateArchives"]), 1)
        self.assertNotIn("releasedNonVotingEvidence", report)
        self.assertNotIn(archive["photoId"], {row["photoId"] for row in report["releasedPhotoBindings"]})
        self.assertNotIn(archive["photoId"], {
            pid for snapshot in report["referenceSnapshots"].values()
            for ids in snapshot["photoIds"].values() for pid in ids
        })
        self.assertEqual(archive["selectedPhotoId"], next(
            row["photoId"] for row in report["sourceRows"] if row["source"] == archive["selectedSource"]
        ))

    def test_stale_catalogue_and_model_provenance_refuse(self):
        catalog = self.fixture.empty_catalog()
        photo_id = metadata.photo_id_from_name(self.paths[2].name)
        catalog["photos"][photo_id] = {"contentSha256": "0" * 64, "protected": False}
        metadata.save_catalog(catalog, self.fixture.root / ".likeness-library.json")
        with self.assertRaisesRegex(ValueError, "ambiguous, stale or unbindable"):
            self.plan()
        metadata.save_catalog(self.fixture.empty_catalog(), self.fixture.root / ".likeness-library.json")

        def stale_model(*args, **kwargs):
            digest, data = self.infer(*args, **kwargs)
            data["alignmentEvidence"]["sourceSha256"] = "0" * 64
            return digest, data

        with mock.patch.object(normal_rebase, "_infer", side_effect=stale_model):
            with self.assertRaisesRegex(ValueError, "current source/model provenance"):
                self.plan()

    def test_cli_refuses_lineage_mix_and_non_sandbox(self):
        lineage = ["--release-receipt", "receipt", "--release-audit", "audit",
                   "--release-review", "review", "--release-run", "run"]
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                normal_rebase.main(["--root", str(self.fixture.root), "--fresh-source-release", *lineage])
            with mock.patch.object(normal_rebase, "is_sandbox_working_path", return_value=False):
                with self.assertRaises(SystemExit):
                    normal_rebase.main(["--root", str(self.fixture.root), "--fresh-source-release"])

    def test_preparation_reuse_requests_nonvoting_gallery_before_selection(self):
        archived = set(self.plan()["duplicateArchives"])
        with mock.patch.object(
            normal_rebase.normal_products, "reuse_prepared", side_effect=ValueError("captured reuse"),
        ) as reuse:
            with self.assertRaisesRegex(ValueError, "captured reuse"):
                normal_rebase._plan(
                    self.fixture.root, "lean", "fresh-fixture", api=self.api,
                    fresh_source_release=True, reuse_preparation="sealed-output",
                    reuse_preparation_sha256="a" * 64,
                )
        # Archived identical copies are not prepared; every other Gallery source is.
        self.assertEqual(
            set(reuse.call_args.args[2]),
            {path for path in self.paths if path.relative_to(self.fixture.root).as_posix() not in archived},
        )
        self.assertTrue(reuse.call_args.kwargs["allow_subset"])
        self.assertTrue(reuse.call_args.kwargs["allow_subset"])

    def test_selected_anchor_retires_before_post_selection_core_freeze(self):
        catalog = self.fixture.empty_catalog()
        photo_id = metadata.photo_id_from_name(self.paths[2].name)
        person_id = "person_" + "a" * 32
        catalog["people"][person_id] = {
            "id": person_id, "displayName": "Owner", "folder": "Prospects/Owner",
            "folderHistory": [], "identityAnchors": [photo_id],
        }
        catalog["photos"][photo_id] = {
            "contentSha256": metadata.content_sha256(self.paths[2]), "protected": False,
        }
        metadata.save_catalog(catalog, self.fixture.root / ".likeness-library.json")
        with mock.patch.object(
            normal_rebase.reconciliation, "frozen_identity_cores",
            wraps=normal_rebase.reconciliation.frozen_identity_cores,
        ) as freeze:
            report = self.plan()
        self.assertIn({"photoId": photo_id, "personId": person_id},
                      report["releasedSourceRetirement"]["retiredAnchors"])
        self.assertNotIn(photo_id, freeze.call_args.args[1]["people"][person_id]["identityAnchors"])
        selected = {row["photoId"] for row in report["releasedPhotoBindings"]}
        self.assertFalse(selected.intersection(
            metadata.photo_id_from_name(photo.name) for photo in freeze.call_args.args[0].photos
        ))


if __name__ == "__main__":
    unittest.main()
