"""Automatic locks need independent current Gallery evidence and reversible writes."""
import copy
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

from tools.art.likeness_library import maintenance, metadata, person_actions, protection
from tools.art.likeness_library.policy import load_policy, validate_policy
from tools.art.likeness_library.reconciliation import frozen_identity_cores


class ProtectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name).resolve()
        self.policy = load_policy()
        self.person_id = "person_" + "1" * 32
        self.folder = "Prospects/A"
        self.catalog = {
            "schemaVersion": 1, "photos": {}, "actions": [],
            "people": {self.person_id: {
                "id": self.person_id, "folder": self.folder, "displayName": "A",
                "folderHistory": [], "identityAnchors": [], "protected": False,
            }},
        }
        self.photos = []
        for index in range(5):
            vector = np.zeros(8)
            vector[0], vector[index + 1] = .8, .6
            self.photo(index, vector)
        self.space = SimpleNamespace(
            photos=self.photos, by_key={self.folder: self.photos},
            st={"minFace": 60, "multiFace": .3},
        )
        self.core = {
            self.folder: {
                "corePhotoIds": [metadata.photo_id_from_name(photo.name) for photo in self.photos],
                "category": "Prospects", "side": "Prospects", "identityProtected": False,
                "vector": np.array([1., 0., 0., 0., 0., 0., 0., 0.]),
            },
        }

    def photo(self, index, vector, bucket="gallery"):
        path = self.root / "Prospects" / "A" / bucket / f"a_image_{123450 + index}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"source {index}".encode())
        photo = SimpleNamespace(
            path=path, name=path.name, key=self.folder, vec=vector,
            sha=metadata.content_sha256(path), faces=1, f2=0,
            usable=lambda _: True,
        )
        self.photos.append(photo)
        return photo

    def plan(self, **kwargs):
        return protection.plan_protection(self.space, self.core, self.catalog, self.policy, root=self.root, **kwargs)

    def test_five_independent_photos_establish_identity_and_only_qualified_photos(self):
        outlier = self.photo(8, np.array([-1., 0., 0., 0., 0., 0., 0., 0.]))
        actions, evidence = self.plan()
        self.assertEqual(len(actions), 6)
        self.assertEqual(sum(len(action.get("sourceChecks", [])) for action in actions), 6)
        self.assertFalse(any("sources" in action["after"]["protectionProvenance"] for action in actions))
        self.assertEqual(len([row for row in actions if "personId" in row]), 1)
        self.assertNotIn(metadata.photo_id_from_name(outlier.name), [row.get("photoId") for row in actions])
        self.assertTrue(any(row.get("photoId") == metadata.photo_id_from_name(outlier.name) and row["decision"] == "hold" for row in evidence))
        for action in actions:
            self.catalog["people" if "personId" in action else "photos"][action.get("personId", action.get("photoId"))] = action["after"]
        metadata.validate_catalog(self.catalog)
        self.assertEqual(self.plan()[0], [])

    def test_protection_does_not_remove_preexisting_core_eligibility(self):
        for action in self.plan()[0]:
            self.catalog["people" if "personId" in action else "photos"][action.get("personId", action.get("photoId"))] = action["after"]
        cores, _, _ = frozen_identity_cores(
            self.space, self.catalog, photo_id_fn=metadata.photo_id_from_name,
            content_sha256_fn=metadata.content_sha256, policy=self.policy,
        )
        self.assertEqual(len(cores[self.folder]["corePhotoIds"]), 5)
        self.assertEqual(protection.plan_protection(self.space, cores, self.catalog, self.policy, root=self.root)[0], [])
        self.photo(9, np.array([.8, 0, 0, 0, 0, 0, .6, 0]))
        actions, _ = protection.plan_protection(self.space, cores, self.catalog, self.policy, root=self.root)
        self.assertEqual(len(actions), 1)
        self.assertIn("photoId", actions[0])

    def test_self_and_duplicate_evidence_cannot_establish_identity(self):
        for photo in self.photos:
            photo.vec = self.photos[0].vec.copy()
        actions, evidence = self.plan()
        self.assertFalse(actions)
        self.assertTrue(any("independent" in row["reason"] for row in evidence))

    def test_review_stale_rejected_ambiguous_and_moving_evidence_are_held(self):
        for mode in ("review", "stale", "rejected", "ambiguous", "moving"):
            with self.subTest(mode=mode):
                photo = self.photos[0]
                old_path, old_sha = photo.path, photo.sha
                old_photos = list(self.photos)
                old_catalog = copy.deepcopy(self.catalog)
                photo_id = metadata.photo_id_from_name(photo.name)
                kwargs = {}
                if mode == "review":
                    photo.path = photo.path.parent.parent / "review" / photo.name
                elif mode == "stale":
                    photo.sha = "0" * 64
                elif mode == "rejected":
                    self.catalog["photos"][photo_id] = {
                        "contentSha256": photo.sha, "protected": False, "rejectedPersonIds": [self.person_id],
                    }
                elif mode == "ambiguous":
                    self.photos.append(photo)
                else:
                    kwargs["moving_photo_ids"] = [photo_id]
                self.assertFalse(self.plan(**kwargs)[0])
                photo.path, photo.sha = old_path, old_sha
                self.photos[:] = old_photos
                self.catalog = old_catalog

    def test_manual_person_optout_suppresses_new_photo_locks_but_clears_nothing(self):
        person = self.catalog["people"][self.person_id]
        person.update({"protected": True, "automaticProtectionOverride": "disabled"})
        photo_id = metadata.photo_id_from_name(self.photos[0].name)
        self.catalog["photos"][photo_id] = {"protected": True, "contentSha256": self.photos[0].sha}
        before = copy.deepcopy(self.catalog)
        self.assertEqual(self.plan()[0], [])
        self.assertEqual(self.catalog, before)
        person["automaticProtectionOverride"] = "enabled"
        self.assertTrue(self.plan()[0])

    def test_photo_optout_is_not_default_false(self):
        photo_id = metadata.photo_id_from_name(self.photos[0].name)
        self.catalog["people"][self.person_id]["protected"] = True
        self.catalog["photos"][photo_id] = {
            "protected": False, "contentSha256": self.photos[0].sha,
            "automaticProtectionOverride": "disabled",
        }
        actions, _ = self.plan()
        self.assertEqual(len(actions), 4)
        self.assertNotIn(photo_id, [row.get("photoId") for row in actions])

    def test_exact_score_and_margin_boundaries(self):
        _, evidence = self.plan()
        score = next(row["score"] for row in evidence if row.get("score") is not None)
        settings = self.policy["protection"]["automatic"]
        settings["minimumOwnCoreSimilarity"] = score
        self.assertEqual(len(self.plan()[0]), 6)
        settings["minimumOwnCoreSimilarity"] = score + 1e-8
        self.assertFalse(self.plan()[0])
        settings["minimumOwnCoreSimilarity"] = .55
        self.core["Prospects/Rival"] = copy.deepcopy(self.core[self.folder])
        # The same frozen references are never attributed to a different folder.
        self.core["Prospects/Rival"]["corePhotoIds"] = []
        settings["minimumRivalMargin"] = score + 1.
        self.assertEqual(len(self.plan()[0]), 6)
        settings["minimumRivalMargin"] += 1e-8
        self.assertFalse(self.plan()[0])

    def test_metadata_only_apply_undo_and_stale_evidence_refusal(self):
        self.policy["status"] = "approved"
        catalog_path = self.root / ".likeness-library.json"
        metadata.save_catalog(self.catalog, catalog_path)
        actions, _ = self.plan()
        backup = mock.Mock(return_value="verified")
        journal = maintenance.apply_moves(
            self.root, [], self.policy, {}, metadata_actions=actions, backup_fn=backup,
        )
        self.assertTrue(metadata.load_catalog(catalog_path)["people"][self.person_id]["protected"])
        self.assertEqual(len(json.loads(journal.read_text())["metadataActions"]), 6)
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=backup)
        self.assertEqual(metadata.load_catalog(catalog_path), self.catalog)
        self.photos[0].path.write_bytes(b"changed")
        backup.reset_mock()
        with self.assertRaisesRegex(ValueError, "evidence source changed"):
            maintenance.apply_moves(self.root, [], self.policy, {}, metadata_actions=actions, backup_fn=backup)
        backup.assert_not_called()

    def test_person_unprotect_persists_override_and_protect_reenables(self):
        for action_type in ("person-unprotected", "person-protected"):
            person_actions.apply_action(
                self.catalog, {"personId": self.person_id, "type": action_type}, "batch_" + "2" * 32,
            )
            person = self.catalog["people"][self.person_id]
            self.assertEqual(person["automaticProtectionOverride"], "enabled" if person["protected"] else "disabled")
        metadata.validate_catalog(self.catalog)

    def test_invalid_policy_and_disabled_automation(self):
        self.policy["protection"]["automatic"]["minimumEstablishedPhotos"] = 4
        with self.assertRaisesRegex(ValueError, "establishment"):
            validate_policy(self.policy)
        self.policy["protection"]["automatic"]["enabled"] = False
        self.assertEqual(self.plan(), ([], []))


if __name__ == "__main__":
    unittest.main()
