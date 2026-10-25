"""Original-name continuity and direct-family proposals without matching by name."""
import copy
import pathlib
import sys
import tempfile
import types
import unittest

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from likeness_library import identity_families, identity_names, maintenance, metadata, protection  # noqa: E402
from likeness_library.policy import default_policy  # noqa: E402


class IdentityNameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.person = {
            "id": "person_" + "a" * 32, "displayName": "Draknara", "folder": "Sisters/Draknara",
            "folderHistory": [], "identityAnchors": [],
        }
        self.folder = self.root / self.person["folder"]
        (self.folder / "gallery").mkdir(parents=True)

    def test_missing_cast_history_never_becomes_original_person_name(self):
        self.assertIsNone(identity_names.snapshot(self.person, self.folder))
        names = identity_names.renamed(self.person, "New Person", self.folder)
        self.assertIsNone(names["originalName"])
        self.assertEqual(names["originalSource"], "unavailable")
        self.assertEqual(names["currentName"], "New Person")

    def test_earliest_explicit_rename_history_survives_subsequent_rename(self):
        (self.folder / "gallery" / "z_new_person.txt").write_text(
            "name: New Person\n2026-10-01 renamed from First Person (Models/First Person)\n"
            "2026-10-02 renamed from Later Person (Models/Later Person)\n", encoding="utf-8",
        )
        names = identity_names.renamed(self.person, "Family Person", self.folder)
        self.assertEqual(names["originalName"], "First Person")
        self.person["names"] = names
        result = identity_names.presentation(self.person, self.folder)
        self.assertEqual(result["characterName"], "Draknara")
        self.assertEqual(result["currentPersonName"], "Family Person")
        self.assertEqual(result["originalPersonName"], "First Person")
        self.assertEqual(identity_names.renamed(self.person, "Again Person", self.folder)["originalName"], "First Person")

    def test_schema_rejects_missing_family_reference(self):
        self.person["names"] = {"originalName": "A Person", "currentName": "A Family", "originalSource": "recorded-history"}
        self.person["family"] = {
            "id": "family_" + "b" * 32, "referencePersonId": "person_" + "c" * 32,
            "surname": "Family", "score": .4, "policyVersion": "test",
            "previousPersonName": "A Person", "reason": "test",
        }
        data = {"schemaVersion": 1, "people": {self.person["id"]: self.person}, "photos": {}, "actions": []}
        self.assertTrue(any("family reference" in error for error in metadata.validation_errors(data)))


class FamilyProposalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.policy = copy.deepcopy(default_policy())
        self.catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
        self.space = types.SimpleNamespace(photos=[], by_key={}, st={"minFace": 60})
        self.cores = {}
        for index, (name, vector) in enumerate((
            ("Alice Vale", [1., 0., 0., 0., 0., 0., 0., 0.]),
            ("Beth Stone", [.4, np.sqrt(.84), 0., 0., 0., 0., 0., 0.]),
        )):
            self.add_person(index, name, np.array(vector))

    def add_person(self, index, name, vector):
        pid = "person_" + format(index + 1, "032x")
        folder = "Prospects/" + name
        self.catalog["people"][pid] = {
            "id": pid, "folder": folder, "displayName": name, "folderHistory": [],
            "identityAnchors": [], "protected": True,
        }
        location = self.root / folder / "gallery"
        location.mkdir(parents=True)
        (location / "z_person.txt").write_text(f"name: {name}\n", encoding="utf-8")
        photos = []
        for photo_index in range(5):
            photo_id = "photo:image_" + str(index * 100 + photo_index + 1000)
            path = location / (photo_id.removeprefix("photo:") + ".jpg")
            path.write_bytes(f"source-{index}-{photo_index}".encode())
            feature = .85 * vector
            feature[3 + photo_index] += np.sqrt(1 - .85 ** 2)
            photo = types.SimpleNamespace(
                path=path, name=path.name, key=folder, vec=feature, usable=lambda minimum: True,
                sha=metadata.content_sha256(path), faces=1, f2=0,
            )
            photos.append(photo)
            self.catalog["photos"][photo_id] = {"contentSha256": metadata.content_sha256(path), "protected": False}
        self.space.photos.extend(photos)
        self.space.by_key[folder] = photos
        self.cores[folder] = {
            "vector": vector, "corePhotoIds": [metadata.photo_id_from_name(photo.name) for photo in photos],
            "category": "Prospects", "side": "Prospects",
        }

    def test_family_names_preserve_originals_no_files_change_and_repeat_is_empty(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        changes, diagnostics = identity_families.plan(self.space, self.cores, self.catalog, self.policy, self.root)
        self.assertEqual(len(changes), 2, diagnostics)
        for change in changes:
            self.assertIn("family", change["after"])
            self.assertEqual(change["after"]["names"]["originalName"], change["before"]["displayName"])
            self.catalog["people"][change["personId"]] = change["after"]
        self.assertEqual({path: path.read_bytes() for path in before}, before)
        self.assertEqual(len({person["family"]["id"] for person in self.catalog["people"].values()}), 1)
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        repeated, _ = identity_families.plan(self.space, self.cores, self.catalog, self.policy, self.root)
        self.assertEqual(repeated, [])

    def test_combined_protection_family_metadata_apply_and_exact_undo(self):
        for person in self.catalog["people"].values():
            person["protected"] = False
        self.policy["status"] = "approved"
        before = copy.deepcopy(self.catalog)
        locks, _ = protection.plan_protection(self.space, self.cores, self.catalog, self.policy, root=self.root)
        combined, diagnostics = identity_families.augment_actions(
            locks, self.space, self.cores, self.catalog, self.policy, self.root,
        )
        self.assertEqual(len([row for row in combined if "personId" in row]), 2, diagnostics)
        self.assertTrue(all("family" in row["after"] for row in combined if "personId" in row))
        local = self.root / ".likeness-library.json"
        metadata.save_catalog(self.catalog, local)
        journal = maintenance.apply_moves(
            self.root, [], self.policy, {}, metadata_actions=combined, backup_fn=lambda *_: "verified",
        )
        applied = metadata.load_catalog(local)
        self.assertTrue(all(person["protected"] for person in applied["people"].values()))
        self.assertTrue(all(photo["protected"] for photo in applied["photos"].values()))
        self.assertEqual(len({person["family"]["id"] for person in applied["people"].values()}), 1)
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")
        self.assertEqual(metadata.load_catalog(local), before)

    def test_family_metadata_rechecks_history_after_backup(self):
        self.policy["status"] = "approved"
        combined, _ = identity_families.plan(self.space, self.cores, self.catalog, self.policy, self.root)
        local = self.root / ".likeness-library.json"
        metadata.save_catalog(self.catalog, local)
        before = local.read_bytes()
        def backup(*_):
            (self.root / "Prospects/Alice Vale/gallery/z_person.txt").write_text("name: Hand Edited\n", encoding="utf-8")
            return "verified"
        with self.assertRaisesRegex(ValueError, "evidence source changed"):
            maintenance.apply_moves(self.root, [], self.policy, {}, metadata_actions=combined, backup_fn=backup)
        self.assertEqual(local.read_bytes(), before)

    def test_same_person_scores_and_duplicate_support_never_assign_family(self):
        self.cores["Prospects/Beth Stone"]["vector"] = self.cores["Prospects/Alice Vale"]["vector"]
        changes, _ = identity_families.plan(self.space, self.cores, self.catalog, self.policy, self.root)
        self.assertFalse(any("family" in change["after"] for change in changes))
        self.cores["Prospects/Beth Stone"]["vector"] = np.array([.4, np.sqrt(.84), 0, 0, 0, 0, 0, 0])
        for photo in self.space.by_key["Prospects/Beth Stone"]:
            photo.vec = self.space.by_key["Prospects/Beth Stone"][0].vec
        changes, _ = identity_families.plan(self.space, self.cores, self.catalog, self.policy, self.root)
        self.assertFalse(any("family" in change["after"] for change in changes))

    def test_stale_source_holds_family_assignment(self):
        self.space.photos[0].path.write_bytes(b"changed")
        changes, _ = identity_families.plan(self.space, self.cores, self.catalog, self.policy, self.root)
        self.assertFalse(any("family" in change["after"] for change in changes))

    def test_changed_membership_stale_source_and_collisions_hold(self):
        changes, _ = identity_families.plan(
            self.space, self.cores, self.catalog, self.policy, self.root,
            changed_folders={"Prospects/Alice Vale"},
        )
        self.assertFalse(any("family" in change["after"] for change in changes))

    def test_existing_family_join_uses_direct_reference_and_preserves_original(self):
        changes, _ = identity_families.plan(self.space, self.cores, self.catalog, self.policy, self.root)
        for change in changes:
            self.catalog["people"][change["personId"]] = change["after"]
        # A third established identity resembles the family founder, not the other member.
        self.add_person(2, "Cara Flint", np.array([.42, -.10, np.sqrt(1 - .42 ** 2 - .10 ** 2), 0, 0, 0, 0, 0]))
        changes, diagnostics = identity_families.plan(self.space, self.cores, self.catalog, self.policy, self.root)
        cara = next(change for change in changes if change["personId"].endswith("3"))
        self.assertIn("family", cara["after"], diagnostics)
        self.assertEqual(cara["after"]["names"]["originalName"], "Cara Flint")
        self.assertEqual(cara["after"]["names"]["currentName"], "Cara Vale")
        self.assertGreater(len(cara["sourceChecks"]), 5)

    def test_name_collision_keeps_family_as_diagnostic_only(self):
        self.add_person(2, "Beth Vale", np.array([0., 0., 1., 0., 0., 0., 0., 0.]))
        changes, diagnostics = identity_families.plan(self.space, self.cores, self.catalog, self.policy, self.root)
        self.assertFalse(any("family" in change["after"] for change in changes))
        self.assertTrue(any("collision" in row["reason"] for row in diagnostics))


if __name__ == "__main__":
    unittest.main()
