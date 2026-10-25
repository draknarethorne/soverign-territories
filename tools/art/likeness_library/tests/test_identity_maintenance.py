"""Established identity updates preserve evidence, IDs, sidecars and rollback."""
import copy
import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

from tools.art.likeness_library import identity_maintenance as identities
from tools.art.likeness_library import maintenance, metadata
from tools.art.likeness_library.policy import load_policy
from tools.art import likeness


class IdentityMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.policy = load_policy()
        self.policy["status"] = "approved"
        self.person_id = "person_" + "1" * 32
        self.folder = "Potentials/Test Person"
        self.catalog = {
            "schemaVersion": 1, "photos": {}, "actions": [],
            "people": {self.person_id: {
                "id": self.person_id, "folder": self.folder, "displayName": "Test Person",
                "folderHistory": [], "identityAnchors": [], "protected": False,
            }},
        }
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")

    def photo(self, number, folder=None, vector=(1., 0.), bucket="gallery"):
        folder = folder or self.folder
        path = self.root / folder / bucket / f"test_image_{number}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(str(number).encode())
        return SimpleNamespace(
            path=path, name=path.name, vec=np.array(vector), key=folder,
            usable=lambda _: True,
        )

    def fixture(self, count=4):
        photos = [self.photo(100000 + i) for i in range(count)]
        space = SimpleNamespace(
            photos=list(photos), by_key={self.folder: photos}, st=self.policy["runtimeSettings"],
        )
        cores = {self.folder: {
            "category": "Potentials", "side": "Prospects", "identityProtected": False,
            "vector": np.array([1., 0.]), "photoScores": {p.name: 1. for p in photos},
        }}
        return photos, space, cores

    def test_final_membership_promotes_existing_four_to_five_and_undo_preserves_id(self):
        photos, space, cores = self.fixture()
        incoming = self.photo(200000, "Various")
        move = {
            "photoId": metadata.photo_id_from_name(incoming.name),
            "source": incoming.path.relative_to(self.root).as_posix(),
            "destination": f"{self.folder}/gallery/{incoming.name}",
            "sha256": metadata.content_sha256(incoming.path), "reason": "incoming match",
        }
        sidecar = self.root / self.folder / "z_test_person.txt"
        sidecar.write_bytes(b"Original history\n")
        derived = self.root / self.folder / "gallery_944x1104" / "scaled.png"
        derived.parent.mkdir()
        derived.write_bytes(b"derived bytes")
        transitions, evidence = identities.category_transitions(
            space, cores, {"moves": [move]}, self.catalog, set(), set(),
            self.policy, self.root, measured_photos=photos + [incoming],
        )
        self.assertEqual(evidence, [])
        self.assertEqual(transitions[0]["destinationFolder"], "Prospects/Test Person")
        self.assertEqual(transitions[0]["usablePhotos"], 5)
        moves = identities.relocate_files(self.root, [move], transitions)
        journal = maintenance.apply_moves(
            self.root, moves, self.policy, {}, identity_actions=transitions,
            backup_fn=lambda *_: "verified",
        )
        updated = metadata.load_catalog(self.root / ".likeness-library.json")
        self.assertEqual(set(updated["people"]), {self.person_id})
        self.assertEqual(updated["people"][self.person_id]["folder"], "Prospects/Test Person")
        self.assertEqual(updated["people"][self.person_id]["folderHistory"], [self.folder])
        self.assertEqual(
            (self.root / "Prospects/Test Person/z_test_person.txt").read_bytes(), b"Original history\n",
        )
        self.assertEqual(
            (self.root / "Prospects/Test Person/gallery_944x1104/scaled.png").read_bytes(), b"derived bytes",
        )
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")
        self.assertEqual(metadata.load_catalog(self.root / ".likeness-library.json"), self.catalog)
        self.assertEqual(sidecar.read_bytes(), b"Original history\n")
        self.assertEqual(derived.read_bytes(), b"derived bytes")
        self.assertTrue(incoming.path.is_file())
        self.assertTrue(all(p.path.is_file() for p in photos))

    def test_protected_photo_prevents_category_transition(self):
        photos, space, cores = self.fixture(5)
        transitions, evidence = identities.category_transitions(
            space, cores, {"moves": []}, self.catalog,
            {metadata.photo_id_from_name(photos[0].name)}, set(), self.policy, self.root,
        )
        self.assertEqual(transitions, [])
        self.assertIn("protected", evidence[0]["reason"])

    def test_retained_identity_transition_holds_without_blocking_unrelated_photo_move(self):
        photos, space, cores = self.fixture(5)
        auxiliary = self.root / self.folder / "gallery_intake" / ("a" * 64) / "manifest.json"
        auxiliary.parent.mkdir(parents=True)
        auxiliary.write_bytes(b"retained set; planner must not alter even stale evidence")
        original = self.root / self.folder / "gallery_org" / ("a" * 64) / "original.jpg"
        original.parent.mkdir(parents=True)
        original.write_bytes(b"exact retained original")
        before = {path: path.read_bytes() for path in (auxiliary, original, *(photo.path for photo in photos))}
        incoming = self.photo(200000, "Various")
        move = {
            "photoId": metadata.photo_id_from_name(incoming.name),
            "source": incoming.path.relative_to(self.root).as_posix(),
            "destination": f"Potentials/Unrelated/gallery/{incoming.name}",
            "sha256": metadata.content_sha256(incoming.path), "reason": "unrelated admission",
        }
        transitions, evidence = identities.category_transitions(
            space, cores, {"moves": [move]}, self.catalog, set(), set(),
            self.policy, self.root, measured_photos=photos + [incoming],
        )
        self.assertEqual(transitions, [])
        self.assertEqual(evidence[0]["decision"], "hold")
        self.assertIn("retained preparation", evidence[0]["reason"])
        moves = identities.relocate_files(self.root, [move], transitions)
        self.assertEqual(moves, [move])
        journal = maintenance.apply_moves(
            self.root, moves, self.policy, {}, identity_actions=transitions,
            backup_fn=lambda *_: "verified",
        )
        self.assertIsNotNone(journal)
        self.assertTrue((self.root / move["destination"]).is_file())
        for path, payload in before.items():
            self.assertEqual(path.read_bytes(), payload)
        self.assertEqual(metadata.load_catalog(self.root / ".likeness-library.json")["people"][self.person_id]["folder"],
                         self.folder)

    def test_empty_directory_shell_allows_later_category_transition_without_deletion(self):
        photos, space, cores = self.fixture(5)
        shell = self.root / "Prospects" / "Test Person" / "gallery" / "empty"
        shell.mkdir(parents=True)
        transitions, evidence = identities.category_transitions(
            space, cores, {"moves": []}, self.catalog, set(), set(), self.policy, self.root,
        )
        self.assertEqual(evidence, [])
        moves = identities.relocate_files(self.root, [], transitions)
        journal = maintenance.apply_moves(
            self.root, moves, self.policy, {}, identity_actions=transitions,
            backup_fn=lambda *_: "verified",
        )
        self.assertTrue(shell.is_dir())
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")
        self.assertTrue(shell.is_dir())
        self.assertTrue(all(photo.path.is_file() for photo in photos))
        (shell / "unexpected.txt").write_bytes(b"not empty")
        transitions, evidence = identities.category_transitions(
            space, cores, {"moves": []}, self.catalog, set(), set(), self.policy, self.root,
        )
        self.assertEqual(transitions, [])
        self.assertIn("destination already exists", evidence[0]["reason"])

    def test_file_added_during_backup_prevents_transition(self):
        _, space, cores = self.fixture(5)
        transitions, _ = identities.category_transitions(
            space, cores, {"moves": []}, self.catalog, set(), set(), self.policy, self.root,
        )
        moves = identities.relocate_files(self.root, [], transitions)

        def backup(*_):
            (self.root / self.folder / "new-note.txt").write_bytes(b"concurrent")
            return "verified"

        with self.assertRaisesRegex(ValueError, "inventory changed"):
            maintenance.apply_moves(
                self.root, moves, self.policy, {}, identity_actions=transitions, backup_fn=backup,
            )
        self.assertTrue(all((self.root / row["source"]).exists() for row in moves))

    def test_auxiliary_file_move_without_identity_action_is_rejected(self):
        self.fixture(5)
        note = self.root / self.folder / "z_test.txt"
        note.write_bytes(b"history")
        with self.assertRaisesRegex(ValueError, "validated folder transition"):
            maintenance.validate_moves(self.root, [{
                "kind": "identity-file", "personId": self.person_id,
                "source": f"{self.folder}/z_test.txt",
                "destination": "Prospects/Test Person/z_test.txt",
                "sha256": metadata.content_sha256(note),
            }])

    def test_outlier_route_requires_support_and_respects_protection(self):
        photos, space, cores = self.fixture(4)
        cores[self.folder]["photoScores"] = {p.name: .05 for p in photos}
        for index, photo in enumerate(photos):
            angle = (-.3 if index % 2 else .3)
            photo.vec = np.array([angle, (1. - angle ** 2) ** .5])
        cores["Prospects/Other"] = {
            "category": "Prospects", "side": "Prospects", "identityProtected": False,
            "vector": np.array([0., 1.]), "photoScores": {},
        }
        space.by_key["Prospects/Other"] = []
        candidates, evidence = identities.split_candidates(
            space, cores, set(), set(), self.policy,
        )
        self.assertEqual(len(candidates), 4)
        self.assertEqual(len(evidence), 4)
        locked = {metadata.photo_id_from_name(p.name) for p in photos[:3]}
        candidates, _ = identities.split_candidates(space, cores, locked, set(), self.policy)
        self.assertEqual(candidates, [])
        protected = copy.deepcopy(cores)
        protected[self.folder]["identityProtected"] = True
        candidates, _ = identities.split_candidates(space, protected, set(), set(), self.policy)
        self.assertEqual(candidates, [])

    def test_near_duplicate_shots_do_not_supply_independent_evidence(self):
        rows = [
            {"photoId": f"photo:image_{index}", "vector": np.array([0., 1.])}
            for index in range(4)
        ]
        self.assertEqual(identities.independent_count(rows, self.policy), 1)
        old_policy = copy.deepcopy(self.policy)
        del old_policy["identityActions"]["independentEvidenceMaximumSimilarity"]
        self.assertEqual(identities.independent_count(rows, old_policy), 0)

    def test_single_unmatched_red_outlier_can_form_a_potential_without_rebase(self):
        photos, space, cores = self.fixture(4)
        for index, photo in enumerate(photos[:3]):
            y = -.3 if index % 2 else .3
            photo.vec = np.array([(1. - y * y) ** .5, y])
        photos[-1].vec = np.array([-1., 0.])
        cores[self.folder]["photoScores"][photos[-1].name] = -1.
        candidates, evidence = identities.split_candidates(
            space, cores, set(), set(), self.policy,
        )
        self.assertEqual(len(candidates), 1)
        self.assertTrue(candidates[0]["detachedOutlier"])
        self.assertEqual(evidence[0]["decision"], "split-new-identity")
        report = likeness.plan_reconciliation(
            candidates, cores, policy=self.policy, minimum_cluster=1,
            name_factory=lambda *_: "New Person",
        )
        self.assertEqual(report["assignments"][0]["destination"], "Potentials/New Person")
        moves = maintenance.proposed_moves(report, photos, self.root)
        self.policy["categoryPolicies"]["Potentials"]["automaticSplitEnabled"] = False
        with self.assertRaisesRegex(ValueError, "Gallery removal is disabled"):
            maintenance.apply_moves(
                self.root, moves, self.policy, {},
                backup_fn=lambda *_: self.fail("must refuse before backup"),
            )
        self.policy["categoryPolicies"]["Potentials"]["automaticSplitEnabled"] = True
        journal = maintenance.apply_moves(
            self.root, moves, self.policy, {}, backup_fn=lambda *_: "verified",
        )
        updated = metadata.load_catalog(self.root / ".likeness-library.json")
        self.assertEqual(updated["people"][self.person_id], self.catalog["people"][self.person_id])
        self.assertEqual(len(updated["people"]), 2)
        self.assertFalse(photos[-1].path.exists())
        self.assertTrue((self.root / moves[0]["destination"]).is_file())
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")
        self.assertTrue(all(photo.path.is_file() for photo in photos))
        self.assertEqual(metadata.load_catalog(self.root / ".likeness-library.json"), self.catalog)
        locked = {metadata.photo_id_from_name(photos[-1].name)}
        self.assertEqual(identities.split_candidates(space, cores, locked, set(), self.policy)[0], [])
        original = photos[1].vec
        photos[1].vec = photos[0].vec
        self.assertEqual(identities.split_candidates(space, cores, set(), set(), self.policy)[0], [])
        photos[1].vec = original
        cores[self.folder]["corePhotoIds"] = [metadata.photo_id_from_name(photos[0].name)]
        self.assertEqual(identities.split_candidates(space, cores, set(), set(), self.policy)[0], [])
        del cores[self.folder]["corePhotoIds"]
        split_maximum = self.policy["identityActions"]["splitReviewMaximum"]
        self.policy["identityActions"]["splitReviewMaximum"] = -1.
        self.assertEqual(identities.split_candidates(space, cores, set(), set(), self.policy)[0], [])
        self.policy["identityActions"]["splitReviewMaximum"] = split_maximum
        del self.policy["categoryPolicies"]["Potentials"]["unmatchedOutlierSplitEnabled"]
        candidates, _ = identities.split_candidates(space, cores, set(), set(), self.policy)
        self.assertEqual(candidates, [])

    def test_final_core_check_reports_residual_work_without_cascading_moves(self):
        photos, space, _ = self.fixture(4)
        for index, photo in enumerate(photos[:3]):
            y = -.3 if index % 2 else .3
            photo.vec = np.array([(1. - y * y) ** .5, y])
        photos[-1].vec = np.array([-1., 0.])
        incoming = self.photo(200000, "Various")
        move = {
            "photoId": metadata.photo_id_from_name(incoming.name),
            "source": incoming.path.relative_to(self.root).as_posix(),
            "destination": f"{self.folder}/gallery/{incoming.name}",
            "sha256": metadata.content_sha256(incoming.path), "reason": "incoming match",
        }
        maintenance.apply_moves(
            self.root, [move], self.policy, {}, backup_fn=lambda *_: "verified",
        )
        staged = self.photo(200001, "Various")
        check = identities.check_applied_membership(
            self.root, photos + [incoming, staged], [move], [], space.st,
            {metadata.photo_id_from_name(staged.name)}, self.policy,
        )
        self.assertEqual(check["status"], "further-maintenance-candidates")
        self.assertIn(metadata.photo_id_from_name(photos[-1].name), check["outlierPhotoIds"])
        self.assertFalse(check["automaticFollowupApplied"])
        self.assertTrue(photos[-1].path.is_file())
        self.assertFalse(incoming.path.exists())
        self.assertTrue(staged.path.is_file())

    def merge_fixture(self):
        photos, space, cores = self.fixture(2)
        target = "Prospects/Other"
        target_id = "person_" + "2" * 32
        others = [self.photo(300000 + i, target) for i in range(2)]
        for rows in (photos, others):
            for index, photo in enumerate(rows):
                x = -.3 if index else .3
                photo.vec = np.array([(1. - x * x) ** .5, x])
        space.photos.extend(others)
        space.by_key[target] = others
        cores[target] = {
            "category": "Prospects", "side": "Prospects", "identityProtected": False,
            "vector": np.array([1., 0.]), "photoScores": {p.name: .8 for p in others},
        }
        self.catalog["people"][target_id] = {
            "id": target_id, "folder": target, "displayName": "Other",
            "folderHistory": [], "identityAnchors": [], "protected": False,
        }
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        return photos, space, cores, target, target_id

    def test_reciprocal_merge_preserves_both_ids_history_and_exact_undo(self):
        photos, space, cores, target, target_id = self.merge_fixture()
        sidecar = self.root / self.folder / "z_test_person.txt"
        sidecar.write_bytes(b"Original name history\n")
        target_note = self.root / target / "z_other.txt"
        target_note.write_bytes(b"Other\n")
        actions, evidence = identities.merge_actions(
            space, cores, self.catalog, set(), set(), self.policy, self.root, [],
        )
        self.assertEqual(evidence, [])
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["destinationFolder"], target)
        moves = identities.relocate_files(self.root, [], actions)
        journal = maintenance.apply_moves(
            self.root, moves, self.policy, {}, identity_actions=actions, backup_fn=lambda *_: "verified",
        )
        updated = metadata.load_catalog(self.root / ".likeness-library.json")
        self.assertEqual(updated["people"][self.person_id]["mergedInto"], target_id)
        self.assertEqual(set(updated["people"]), {self.person_id, target_id})
        self.assertEqual(target_note.read_bytes(), b"Other\n")
        archived_note = self.root / target / "_identity-history" / self.person_id / sidecar.name
        self.assertEqual(archived_note.read_bytes(), b"Original name history\n")
        self.assertTrue(all((self.root / target / "gallery" / p.name).is_file() for p in photos[:2]))
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")
        self.assertEqual(metadata.load_catalog(self.root / ".likeness-library.json"), self.catalog)
        self.assertEqual(sidecar.read_bytes(), b"Original name history\n")
        self.assertTrue(all(p.path.is_file() for p in photos))

    def test_near_duplicate_only_identity_and_protected_identity_cannot_merge(self):
        photos, space, cores, _, _ = self.merge_fixture()
        for photo in photos:
            photo.vec = np.array([1., 0.])
        actions, _ = identities.merge_actions(
            space, cores, self.catalog, set(), set(), self.policy, self.root, [],
        )
        self.assertEqual(actions, [])
        cores[self.folder]["identityProtected"] = True
        actions, _ = identities.merge_actions(
            space, cores, self.catalog, set(), set(), self.policy, self.root, [],
        )
        self.assertEqual(actions, [])

    def test_persistent_review_rejection_blocks_merge_proposal_and_forged_apply(self):
        _, space, cores, target, target_id = self.merge_fixture()
        planned, _ = identities.merge_actions(
            space, cores, self.catalog, set(), set(), self.policy, self.root, [],
        )
        self.assertEqual(len(planned), 1)
        review = self.photo(888888, bucket="review")
        photo_id = metadata.photo_id_from_name(review.name)
        self.catalog["photos"][photo_id] = {
            "contentSha256": metadata.content_sha256(review.path), "protected": False,
            "rejectedPersonIds": [target_id],
        }
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        proposed, evidence = identities.merge_actions(
            space, cores, self.catalog, set(), set(), self.policy, self.root, [],
        )
        self.assertEqual(proposed, [])
        self.assertIn("explicitly rejected", evidence[0]["reason"])
        moves = identities.relocate_files(self.root, [], planned)
        with self.assertRaisesRegex(ValueError, "explicitly rejected"):
            maintenance.apply_moves(
                self.root, moves, self.policy, {}, identity_actions=planned,
                backup_fn=lambda *_: self.fail("merge must stop before backup"),
            )
        self.assertTrue(review.path.is_file())
        self.assertEqual(self.catalog["people"][target_id]["folder"], target)

    def test_merge_revalidates_target_after_backup(self):
        _, space, cores, target, _ = self.merge_fixture()
        actions, _ = identities.merge_actions(
            space, cores, self.catalog, set(), set(), self.policy, self.root, [],
        )
        moves = identities.relocate_files(self.root, [], actions)

        def backup(*_):
            (self.root / target / "concurrent.txt").write_bytes(b"new target evidence")
            return "verified"

        with self.assertRaisesRegex(ValueError, "merge destination changed"):
            maintenance.apply_moves(
                self.root, moves, self.policy, {}, identity_actions=actions, backup_fn=backup,
            )
        self.assertTrue(all((self.root / row["source"]).is_file() for row in moves))

    def test_draft_merge_proposals_equal_approved_proposals_but_apply_is_blocked(self):
        _, space, cores, _, _ = self.merge_fixture()
        approved, _ = identities.merge_actions(
            space, cores, self.catalog, set(), set(), self.policy, self.root, [],
        )
        self.policy["status"] = "draft"
        draft, _ = identities.merge_actions(
            space, cores, self.catalog, set(), set(), self.policy, self.root, [],
        )
        self.assertEqual(approved, draft)
        moves = identities.relocate_files(self.root, [], draft)
        with self.assertRaisesRegex(ValueError, "approved policy"):
            maintenance.apply_moves(
                self.root, moves, self.policy, {}, identity_actions=draft,
                backup_fn=lambda *_: self.fail("must refuse before backup"),
            )

    def test_real_reconcile_command_promotes_after_intake_and_undoes(self):
        photos, space, cores = self.fixture(4)
        incoming = self.photo(200000, "Various")
        space.photos.append(incoming)
        space.by_key["Various"] = [incoming]
        policy_path = self.root / "policy.json"
        policy_path.write_text(json.dumps(self.policy), encoding="utf-8")
        args = SimpleNamespace(
            root=str(self.root), cache=None, policy=str(policy_path), apply=False,
            sandbox_apply_draft=False, undo=None, embedder=mock.Mock(),
            out=str(self.root / "preview.json"),
        )
        settings = {
            **self.policy["runtimeSettings"], "assign": .4, "margin": .1,
        }
        with (
            mock.patch.object(likeness.cw, "load_cfg", return_value={}),
            mock.patch.object(likeness, "build", return_value=({}, settings, self.root, None, space)),
            mock.patch.object(likeness, "load_review", return_value=[]),
            mock.patch.object(likeness, "frozen_identity_cores", return_value=(cores, set(), [])),
            mock.patch.object(likeness, "junk_reason", return_value=None),
            mock.patch.object(likeness.cw, "photo_folders", return_value=[]),
            mock.patch("likeness_library.maintenance._backup", return_value="verified"),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            likeness.cmd_reconcile(args)
            preview = json.loads(pathlib.Path(args.out).read_text(encoding="utf-8"))
            self.assertEqual(preview["identityActions"][0]["destinationFolder"], "Prospects/Test Person")
            self.assertTrue(incoming.path.is_file())
            args.apply = True
            likeness.cmd_reconcile(args)
            receipt = json.loads(pathlib.Path(args.out).read_text(encoding="utf-8"))
            self.assertEqual(
                receipt["postApplyCheck"]["status"], "no-further-maintenance-candidates",
            )
            self.assertEqual(receipt["postApplyCheck"]["passes"], 1)
            self.assertFalse(receipt["postApplyCheck"]["automaticFollowupApplied"])
        applied = metadata.load_catalog(self.root / ".likeness-library.json")
        self.assertEqual(applied["people"][self.person_id]["folder"], "Prospects/Test Person")
        self.assertTrue(all(
            (self.root / "Prospects/Test Person/gallery" / photo.name).is_file()
            for photo in photos + [incoming]
        ))
        journal = pathlib.Path(receipt["journal"])
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")
        self.assertTrue(incoming.path.is_file())
        self.assertEqual(metadata.load_catalog(self.root / ".likeness-library.json"), self.catalog)

    def test_complete_outlier_split_and_demotion_is_stable_without_a_rebase(self):
        self.folder = "Prospects/Test Person"
        self.catalog["people"][self.person_id]["folder"] = self.folder
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        photos, _, _ = self.fixture(5)
        for index, photo in enumerate(photos[:4]):
            y = -.3 if index % 2 else .3
            photo.vec = np.array([(1. - y * y) ** .5, y])
        photos[-1].vec = np.array([-1., 0.])
        first = self.run_two_measured_passes(photos)
        self.assertEqual(first["assignedCount"], 1)
        self.assertEqual(first["identityActions"][0]["destinationFolder"], "Potentials/Test Person")
        catalog_path = self.root / ".likeness-library.json"
        updated = metadata.load_catalog(catalog_path)
        self.assertEqual(updated["people"][self.person_id]["folder"], "Potentials/Test Person")
        self.assertEqual(len(updated["people"]), 2)
        self.assertTrue((self.root / "Potentials/Detached Person/gallery" / photos[-1].name).is_file())
        maintenance.undo_moves(
            self.root, first["journal"], {}, apply=True, backup_fn=lambda *_: "verified",
        )
        self.assertTrue(all(photo.path.is_file() for photo in photos))
        self.assertEqual(metadata.load_catalog(catalog_path), self.catalog)

    def test_complete_four_to_five_promotion_is_stable_without_a_rebase(self):
        photos, _, _ = self.fixture(4)
        incoming = self.photo(200000, "Various")
        first = self.run_two_measured_passes(photos + [incoming])
        self.assertEqual(first["assignedCount"], 1)
        self.assertEqual(first["identityActions"][0]["destinationFolder"], "Prospects/Test Person")

    def test_complete_reciprocal_merge_is_stable_without_a_rebase(self):
        self.folder = "Prospects/Test Person"
        self.catalog["people"][self.person_id]["folder"] = self.folder
        photos, _, _ = self.fixture(5)
        target, target_id = "Prospects/Other", "person_" + "2" * 32
        others = [self.photo(300000 + index, target) for index in range(5)]
        for rows in (photos, others):
            for index, photo in enumerate(rows):
                y = -.3 if index % 2 else .3
                photo.vec = np.array([(1. - y * y) ** .5, y])
        self.catalog["people"][target_id] = {
            "id": target_id, "folder": target, "displayName": "Other",
            "folderHistory": [], "identityAnchors": [], "protected": False,
        }
        catalog_path = self.root / ".likeness-library.json"
        metadata.save_catalog(self.catalog, catalog_path)
        first = self.run_two_measured_passes(photos + others)
        self.assertEqual(first["assignedCount"], 0)
        self.assertEqual(len(first["identityActions"]), 1)
        self.assertEqual(first["identityActions"][0]["type"], "identity-merge")
        updated = metadata.load_catalog(catalog_path)
        self.assertEqual(updated["people"][self.person_id]["mergedInto"], target_id)
        self.assertEqual(len(list((self.root / target / "gallery").glob("*.jpg"))), 10)
        maintenance.undo_moves(
            self.root, first["journal"], {}, apply=True, backup_fn=lambda *_: "verified",
        )
        self.assertTrue(all(photo.path.is_file() for photo in photos + others))
        self.assertEqual(metadata.load_catalog(catalog_path), self.catalog)

    def run_two_measured_passes(self, photos):
        originals = {photo.name: photo for photo in photos}
        settings = {**self.policy["runtimeSettings"], "assign": .4, "margin": .1}

        def build(_args):
            measured, by_key = [], {}
            for path in self.root.rglob("*.jpg"):
                photo = copy.copy(originals[path.name])
                photo.path = path
                photo.key = path.parent.parent.relative_to(self.root).as_posix()
                measured.append(photo)
                if not likeness.matches(photo.key, settings["mixed"]):
                    by_key.setdefault(photo.key, []).append(photo)
            space = SimpleNamespace(photos=measured, by_key=by_key, st=settings)
            return {}, settings, self.root, None, space

        policy_path = self.root / "policy.json"
        policy_path.write_text(json.dumps(self.policy), encoding="utf-8")
        args = SimpleNamespace(
            root=str(self.root), cache=None, policy=str(policy_path), apply=True,
            sandbox_apply_draft=False, undo=None, embedder=mock.Mock(),
            out=str(self.root / "preview.json"),
        )
        with (
            mock.patch.object(likeness.cw, "load_cfg", return_value={}),
            mock.patch.object(likeness, "build", side_effect=build),
            mock.patch.object(likeness, "load_review", return_value=[]),
            mock.patch.object(likeness, "junk_reason", return_value=None),
            mock.patch.object(likeness, "invent_name", return_value="Detached Person"),
            mock.patch.object(likeness.cw, "photo_folders", return_value=[]),
            mock.patch("likeness_library.maintenance._backup", return_value="verified"),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            likeness.cmd_reconcile(args)
            first = json.loads(pathlib.Path(args.out).read_text(encoding="utf-8"))
            self.assertTrue(first["moves"])
            self.assertEqual(first["postApplyCheck"]["status"], "no-further-maintenance-candidates")
            catalog_path = self.root / ".likeness-library.json"
            after = catalog_path.read_bytes()
            args.apply = False
            likeness.cmd_reconcile(args)
            second = json.loads(pathlib.Path(args.out).read_text(encoding="utf-8"))
            self.assertEqual(second["candidateCount"], 0)
            self.assertEqual(second["moves"], [])
            self.assertEqual(second["identityActions"], [])
            self.assertEqual(catalog_path.read_bytes(), after)
        return first


if __name__ == "__main__":
    unittest.main()
