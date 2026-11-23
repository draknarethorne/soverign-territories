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

    def cast_seed_plan(self, *, top=3, below=.60, **kwargs):
        """Sisters/Seed: three identical-direction seeds and one yellow (0.40) member."""
        from tools.art.likeness_library.policy import load_policy

        f = self.fixture
        names = {}
        for index, payload in enumerate((b"seed one", b"seed two", b"seed three", b"seed low"), 301):
            names[payload] = f.photo(f"Sisters/Seed/gallery/seed_image_{index}.jpg", payload)
        self.api.cw.photo_folders(None, None).append(("Sisters", "Seed", f.root / "Sisters" / "Seed"))
        self.vectors.update({
            "seed one": [0., 0., 1.], "seed two": [0., .1, np.sqrt(.99)],
            "seed three": [0., -.1, np.sqrt(.99)], "seed low": [0., -np.sqrt(.84), .4],
        })
        policy = load_policy()
        policy["castAdmission"].update(seedTopCount=top, seedReleaseBelow=below)
        path = f.root.parent / "seed-policy.json"
        path.write_text(json.dumps(policy), encoding="utf-8")
        return names, self.plan(policy_path=path, **kwargs)

    def test_cast_seed_releases_outside_seed_and_binds_outcomes(self):
        names, report = self.cast_seed_plan()
        low = metadata.photo_id_from_name(names[b"seed low"].name)
        seeds = {metadata.photo_id_from_name(names[key].name) for key in (b"seed one", b"seed two", b"seed three")}
        assessment = {row["photoId"]: row for row in report["freshSourceAssessment"]["assessment"]}
        self.assertEqual(assessment[low]["band"], "yellow")
        self.assertEqual(assessment[low]["selectionReasons"], ["cast-seed-release"])
        self.assertIn(low, {row["photoId"] for row in report["releasedPhotoBindings"]})
        # Released before the post-release cores formed: it never votes for the seed.
        self.assertNotIn(low, {
            pid for snapshot in report["referenceSnapshots"].values()
            for ids in snapshot["photoIds"].values() for pid in ids
        })
        self.assertTrue(seeds <= set(report["referenceSnapshots"]["1"]["photoIds"]["Sisters/Seed"]))
        # Non-cast identities are unaffected by the cast seed.
        self.assertTrue(all(row["castSeed"] is None for row in assessment.values()
                            if not row["owner"].startswith("Sisters/")))
        seed = report["freshCastSeed"]
        self.assertEqual((seed["topCount"], seed["releaseBelow"]), (3, .60))
        identity = next(item for item in seed["identities"] if item["identity"] == "Sisters/Seed")
        self.assertEqual((identity["seedSize"], identity["releasedCount"], identity["seedReleaseCount"]), (3, 1, 1))
        released = identity["released"][0]
        self.assertEqual(released["photoId"], low)
        self.assertAlmostEqual(released["beforeScore"], .4, places=2)
        self.assertEqual(released["outcome"], "own-review")
        self.assertTrue(released["finalPath"].startswith("Sisters/Seed/review/"))
        self.assertAlmostEqual(released["afterScore"], .4, places=2)
        self.assertEqual(seed["workflowReplacementProposals"], [])
        self.assertEqual((report["freshCastSeedReleaseCount"], report["freshCastSeedKeptCount"],
                          report["freshCastSeedReturnedCount"]), (1, 3, 0))
        replay = self.plan(for_apply=True, reuse_plan=report,
                           policy_path=self.fixture.root.parent / "seed-policy.json")
        self.assertEqual(replay["freshCastSeed"], report["freshCastSeed"])
        changed = copy.deepcopy(report)
        changed["freshCastSeed"]["identities"][0]["released"][0]["outcome"] = "returned-gallery"
        with self.assertRaisesRegex(ValueError, "cast seed outcomes differ"):
            self.plan(for_apply=True, reuse_plan=changed,
                      policy_path=self.fixture.root.parent / "seed-policy.json")

    def test_cast_seed_top_count_keeps_low_member_when_large_enough(self):
        names, report = self.cast_seed_plan(top=4)
        low = metadata.photo_id_from_name(names[b"seed low"].name)
        self.assertNotIn(low, {row["photoId"] for row in report["releasedPhotoBindings"]})
        row = next(row for row in report["freshSourceAssessment"]["assessment"] if row["photoId"] == low)
        self.assertEqual(row["castSeed"], {"rank": 4, "seedMember": True, "basis": "top-count",
                                           "exemptedSelectionReasons": []})

    def test_released_workflow_photo_that_does_not_return_gets_replacement_proposal(self):
        low_name = "seed_image_304.jpg"
        self.api.configuration = lambda: {"photos": {"hero": low_name}}
        names, report = self.cast_seed_plan()
        low = metadata.photo_id_from_name(low_name)
        decision = next(row for row in report["releasedDecisionEvidence"] if row["photoId"] == low)
        self.assertTrue(decision["workflowSelected"])
        self.assertTrue(decision["sourceProtectionOverride"])
        proposals = report["freshCastSeed"]["workflowReplacementProposals"]
        self.assertEqual(len(proposals), 1)
        proposal = proposals[0]
        self.assertEqual((proposal["identity"], proposal["photoId"], proposal["outcome"]),
                         ("Sisters/Seed", low, "own-review"))
        seeds = {metadata.photo_id_from_name(names[key].name): key for key in (b"seed one", b"seed two", b"seed three")}
        scores = {row["photoId"]: row["score"] for row in report["freshSourceAssessment"]["assessment"]}
        best = max(seeds, key=lambda pid: (scores[pid], pid))
        self.assertEqual(proposal["replacement"]["photoId"], best)
        self.assertEqual(proposal["replacement"]["ownScore"], scores[best])
        self.assertEqual(report["freshCastWorkflowReplacementCount"], 1)
        self.assertFalse(report["freshCastSeed"]["configurationChanged"])

    def settle_plan(self, **kwargs):
        """Owner gains three admitted arrivals; its yellow edge member then drops to orange."""
        f = self.fixture
        self.api.cw.photo_folders(None, None).append(("Various", "Various", f.root / "Various"))
        names = {b"owner edge": f.photo("Prospects/Owner/gallery/owner_image_106.jpg", b"owner edge")}
        for index, payload in enumerate((b"arrival one", b"arrival two", b"arrival three"), 401):
            names[payload] = f.photo(f"Various/gallery/various_image_{index}.jpg", payload)
        self.vectors.update({
            "owner edge": [.4, 0., np.sqrt(.84)], "arrival one": [.6, .8, 0.],
            "arrival two": [.5, np.sqrt(.75), 0.], "arrival three": [.4, np.sqrt(.84), 0.],
        })
        return names, self.plan(**kwargs)

    def test_settle_releases_member_that_drops_to_orange_after_admission(self):
        names, report = self.settle_plan()
        edge = metadata.photo_id_from_name(names[b"owner edge"].name)
        initial = next(row for row in report["freshSourceAssessment"]["assessment"] if row["photoId"] == edge)
        self.assertEqual(initial["band"], "yellow")
        self.assertFalse(initial["selected"])
        arrivals = {metadata.photo_id_from_name(names[key].name)
                    for key in (b"arrival one", b"arrival two", b"arrival three")}
        admitted = {row["photoId"] for row in report["assignments"] if row["destination"] == "Prospects/Owner"}
        self.assertTrue(arrivals <= admitted)
        settle = report["settle"]
        released = {item["photoId"]: item for item in settle["passes"][0]["released"]}
        self.assertEqual(released[edge]["band"], "orange")
        self.assertEqual(released[edge]["identity"], "Prospects/Owner")
        self.assertTrue(released[edge]["moved"])
        # Fresh release only: the original member joins the bound release cohort.
        self.assertIn(edge, {row["photoId"] for row in report["settleReleasedBindings"]})
        binding = next(row for row in report["releasedPhotoBindings"] if row["photoId"] == edge)
        self.assertEqual((binding["currentPath"], binding["sha256"]), (
            names[b"owner edge"].relative_to(self.fixture.root).as_posix(),
            metadata.content_sha256(names[b"owner edge"]),
        ))
        self.assertIn(binding, self.permissions.call_args.kwargs["released_bindings"])
        evidence = next(row for row in report["releasedDecisionEvidence"] if row["photoId"] == edge)
        self.assertTrue(evidence["sourceProtectionOverride"])
        self.assertEqual(evidence["role"], "candidate")
        move = next(row for row in report["moves"] if row["photoId"] == edge)
        self.assertEqual(move["source"], names[b"owner edge"].relative_to(self.fixture.root).as_posix())
        self.assertTrue(move["destination"].startswith("Potentials/"))
        self.assertTrue(move["normalAdmission"])
        self.assertEqual(move["releasedPhotoId"], edge)
        decision = next(row for row in report["assignments"] + report["held"] if row["photoId"] == edge)
        self.assertEqual(decision["settle"]["releasedFrom"], "Prospects/Owner")
        # Below yellow against every existing identity: a labelled single-photo Potential (c).
        self.assertTrue(decision["singlePhoto"])
        self.assertEqual(decision["singlePhotoGate"]["bestRival"], "Prospects/Owner")
        self.assertLess(decision["singlePhotoGate"]["bestRivalScore"], .30)
        self.assertEqual(settle["didNotSettle"], [])
        phases = [row["phase"] for row in report["phaseLog"]]
        self.assertEqual(phases.index("settle-pass-1"), phases.index("bounded-two-round-admission") + 1)
        record = next(row for row in report["phaseLog"] if row["phase"] == "settle-pass-1")
        self.assertGreaterEqual(record["durationSeconds"], 0)
        self.assertEqual(record["releasedCount"], settle["passes"][0]["releasedCount"])
        self.assertEqual(record["movedCount"], settle["passes"][0]["movedCount"])
        self.assertLessEqual(report["settlePassCount"], 3)
        # Every source row stays bound, and no photo has more than one planned move.
        self.assertEqual(len(report["sourceHashes"]), len(report["sourceRows"]))
        moved = [row["photoId"] for row in report["moves"]]
        self.assertEqual(len(moved), len(set(moved)))
        replay = self.plan(for_apply=True, reuse_plan=report)
        self.assertEqual(replay["settle"], report["settle"])
        self.assertEqual(replay["settleFingerprint"], report["settleFingerprint"])
        self.assertEqual(replay["moves"], report["moves"])
        changed = copy.deepcopy(report)
        changed["settleFingerprint"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "settle pass decisions differ from preview"):
            self.plan(for_apply=True, reuse_plan=changed)
        # A different pass limit at apply cannot reuse the preview's settled plan.
        from tools.art.likeness_library.policy import load_policy

        policy = load_policy()
        policy["identityActions"]["settlePassMaximum"] = 0
        path = self.fixture.root.parent / "apply-no-settle-policy.json"
        path.write_text(json.dumps(policy), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differ from preview"):
            self.plan(for_apply=True, reuse_plan=report, policy_path=path)
        # The preview's bound settle release cannot be dropped at apply.
        changed = copy.deepcopy(report)
        changed["settleReleasedBindings"] = []
        with self.assertRaisesRegex(ValueError, "differ from preview"):
            self.plan(for_apply=True, reuse_plan=changed)

    def test_settle_released_anchor_is_retired_with_its_binding(self):
        names, _ = self.settle_plan()
        edge = metadata.photo_id_from_name(names[b"owner edge"].name)
        catalog = self.fixture.empty_catalog()
        person_id = "person_" + "b" * 32
        catalog["people"][person_id] = {
            "id": person_id, "displayName": "Owner", "folder": "Prospects/Owner",
            "folderHistory": [], "identityAnchors": [edge],
        }
        catalog["photos"][edge] = {"contentSha256": metadata.content_sha256(names[b"owner edge"]), "protected": False}
        metadata.save_catalog(catalog, self.fixture.root / ".likeness-library.json")
        report = self.plan()
        self.assertIn(edge, {row["photoId"] for row in report["settleReleasedBindings"]})
        self.assertIn({"photoId": edge, "personId": person_id}, report["releasedSourceRetirement"]["retiredAnchors"])
        # The anchor's own protection did not exempt it: the fresh release override covers it.
        evidence = next(row for row in report["releasedDecisionEvidence"] if row["photoId"] == edge)
        self.assertTrue(evidence["protected"])
        self.assertTrue(evidence["sourceProtectionOverride"])

    def test_original_member_slipping_to_orange_is_only_reported_in_normal_rebase(self):
        names, _report = self.settle_plan()
        report = normal_rebase._plan(self.fixture.root, "fast", "normal-fixture", api=self.api)[0]
        edge = metadata.photo_id_from_name(names[b"owner edge"].name)
        self.assertNotIn("freshSourceRelease", report)
        unsettled = {row["photoId"]: row for row in report["settle"]["didNotSettle"]}
        self.assertEqual(unsettled[edge]["band"], "orange")
        self.assertEqual(unsettled[edge]["identity"], "Prospects/Owner")
        self.assertIn("outside a release cohort", unsettled[edge]["reason"])
        self.assertNotIn(edge, {item["photoId"] for item in report["settle"]["passes"][0]["released"]})
        self.assertEqual(report["settleReleasedBindings"], [])
        self.assertNotIn("releasedPhotoBindings", report)
        self.assertFalse([row for row in report["moves"]
                          if row["photoId"] == edge and row["source"] != row["destination"]])

    def test_settle_passes_can_be_disabled_by_policy(self):
        from tools.art.likeness_library.policy import load_policy

        policy = load_policy()
        policy["identityActions"]["settlePassMaximum"] = 0
        path = self.fixture.root.parent / "no-settle-policy.json"
        path.write_text(json.dumps(policy), encoding="utf-8")
        names, report = self.settle_plan(policy_path=path)
        self.assertNotIn("settle", report)
        self.assertNotIn("settle-pass-1", [row["phase"] for row in report["phaseLog"]])
        edge = metadata.photo_id_from_name(names[b"owner edge"].name)
        self.assertNotIn(edge, {row["photoId"] for row in report["moves"] if not row.get("preparationOnly")})

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
