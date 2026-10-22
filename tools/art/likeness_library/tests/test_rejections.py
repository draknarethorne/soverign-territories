"""Persistent negative matches survive scoring, moves, aliases and undo."""
import copy
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace

import numpy as np

from tools.art.likeness_library import actions, clean_rebase, maintenance, metadata, rejections, review_gallery
from tools.art.likeness_library.policy import load_policy
from tools.art.likeness_library.reconciliation import plan_reconciliation


class RejectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.ids = ["person_" + letter * 32 for letter in ("a", "b", "c")]
        self.catalog = {
            "schemaVersion": 1, "photos": {}, "actions": [],
            "people": {
                person_id: {"id": person_id, "folder": f"Prospects/{name}",
                            "displayName": name, "folderHistory": [], "identityAnchors": []}
                for person_id, name in zip(self.ids, ("Alice", "Beth", "Former"))
            },
        }
        self.source = self.root / "Prospects" / "Alice" / "review" / "alice_image_123456.jpg"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"photo bytes")
        self.photo_id = "photo:image_123456"
        self.digest = metadata.content_sha256(self.source)
        self.manifest = {
            "manifestVersion": 1, "generatedAt": "2026-10-22T11:30:00-05:00",
            "source": "people-gallery-review", "actions": [{
                "type": "match-rejected", "photoId": self.photo_id, "contentSha256": self.digest,
                "personFolder": "Prospects/Alice", "personId": self.ids[0], "sourceBucket": "Review",
            }],
        }
        self.policy = load_policy()
        self.policy["status"] = "approved"

    def save(self, updated):
        self.catalog.clear()
        self.catalog.update(copy.deepcopy(updated))

    def reject(self):
        batch, _ = actions.apply_actions(
            self.manifest, self.root, self.catalog, {}, "Various",
            backup_fn=lambda *_: "verified", save_fn=self.save,
        )
        return batch

    def plan(self, *, cast=False, group=1):
        candidate = {
            "photoId": self.photo_id, "sourceFolder": "Various", "sourceBucket": "Pool",
            "side": "Prospects", "vector": np.array([1., 0.]),
            **rejections.candidate_state(self.catalog, self.photo_id, self.digest),
        }
        first = "Angels/Alice" if cast else "Prospects/Alice"
        cores = {first: {
            "vector": np.array([1., 0.]), "side": "Prospects",
            "category": "Angels" if cast else "Prospects", "personIds": [self.ids[0]],
        }}
        if not cast:
            cores["Prospects/Beth"] = {
                "vector": np.array([.7, np.sqrt(1 - .7 ** 2)]),
                "side": "Prospects", "category": "Prospects", "personIds": [self.ids[1]],
            }
        rows = [dict(candidate, photoId=self.photo_id if index == 0 else f"photo:image_{200000 + index}",
                     rejectedPersonIds=candidate.get("rejectedPersonIds", []) if index == 0 else [])
                for index in range(group)]
        return plan_reconciliation(rows, cores, policy=self.policy, name_factory=lambda *_: "New Person")

    def test_apply_persists_stable_id_and_undo_restores_photo_and_exclusion_state(self):
        batch = self.reject()
        archived = self.root / "Various" / "gallery" / self.source.name
        self.assertEqual(archived.read_bytes(), b"photo bytes")
        self.assertEqual(self.catalog["photos"][self.photo_id]["rejectedPersonIds"], [self.ids[0]])
        self.assertEqual(self.catalog["actions"][-1]["type"], "match-rejected")
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        actions.undo_actions(
            self.catalog, self.root, {}, "Various", batch_id=batch,
            backup_fn=lambda *_: "verified", save_fn=self.save,
        )
        self.assertTrue(self.source.exists())
        self.assertNotIn("rejectedPersonIds", self.catalog["photos"][self.photo_id])

    def test_rejected_closest_identity_is_excluded_but_other_identity_can_qualify(self):
        self.assertEqual(self.plan()["assignments"][0]["destination"], "Prospects/Alice")
        self.reject()
        result = self.plan()
        self.assertEqual(result["assignments"][0]["destination"], "Prospects/Beth")
        self.assertEqual(result["assignments"][0]["excludedIdentityIds"], [self.ids[0]])

    def test_cast_group_routing_cannot_bypass_any_members_rejection(self):
        self.reject()
        for count in (1, 2, 5):
            result = self.plan(cast=True, group=count)
            for row in result["assignments"] + result["held"]:
                self.assertNotEqual(row.get("destination"), "Angels/Alice")
                self.assertNotEqual(row.get("reviewDestination"), "Angels/Alice/review")

    def test_merged_successors_and_stable_category_rename_cannot_bypass_exclusion(self):
        self.catalog["people"][self.ids[2]]["mergedInto"] = self.ids[0]
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.digest, "protected": False, "rejectedPersonIds": [self.ids[2]],
        }
        with self.assertRaisesRegex(ValueError, "explicitly rejected"):
            rejections.require_destination(self.catalog, self.photo_id, self.digest, self.ids[0])
        self.catalog["people"][self.ids[0]]["folder"] = "Models/New Name"
        with self.assertRaisesRegex(ValueError, "explicitly rejected"):
            rejections.require_destination(self.catalog, self.photo_id, self.digest, self.ids[0])

    def test_stale_exclusion_holds_candidate_and_prevents_explicit_move(self):
        self.reject()
        state = rejections.candidate_state(self.catalog, self.photo_id, "f" * 64)
        self.assertEqual(state, {"rejectionMetadataStale": True})
        candidate = {
            "photoId": self.photo_id, "sourceFolder": "Various", "sourceBucket": "Pool",
            "side": "Prospects", "vector": np.array([1., 0.]), **state,
        }
        result = plan_reconciliation([candidate], {}, policy=self.policy, name_factory=lambda *_: "New Person")
        self.assertEqual(result["assignedCount"], 0)
        self.assertIn("stale", result["held"][0]["reason"])
        with self.assertRaisesRegex(ValueError, "stale"):
            rejections.require_destination(self.catalog, self.photo_id, "f" * 64, self.ids[1])

    def test_maintenance_preserves_rejections_and_refuses_forged_rejected_destination(self):
        self.reject()
        source = self.root / "Various" / "gallery" / self.source.name
        move = {
            "photoId": self.photo_id, "sha256": self.digest, "reason": "test",
            "source": source.relative_to(self.root).as_posix(),
            "destination": "Prospects/Alice/gallery/" + self.source.name,
        }
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        with self.assertRaisesRegex(ValueError, "explicitly rejected"):
            maintenance.apply_moves(
                self.root, [move], self.policy, {}, backup_fn=lambda *_: self.fail("must stop before backup"),
            )
        move["destination"] = "Prospects/Beth/gallery/" + self.source.name
        journal = maintenance.apply_moves(
            self.root, [move], self.policy, {}, backup_fn=lambda *_: "verified",
        )
        updated = metadata.load_catalog(self.root / ".likeness-library.json")
        self.assertEqual(updated["photos"][self.photo_id]["rejectedPersonIds"], [self.ids[0]])
        maintenance.undo_moves(self.root, journal, {}, apply=True, backup_fn=lambda *_: "verified")

    def test_manual_move_into_rejected_identity_refused_and_other_metadata_changes_preserve_decision(self):
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.digest, "protected": False, "rejectedPersonIds": [self.ids[1]],
        }
        (self.root / "Prospects" / "Beth").mkdir(parents=True)
        document = copy.deepcopy(self.manifest)
        document["actions"][0].update({
            "type": "match-accepted", "destinationPersonId": self.ids[1],
            "destinationFolder": "Prospects/Beth",
        })
        errors, _ = actions.validate_manifest(document, self.root, self.catalog, "Various")
        self.assertIn("explicitly rejected", "\n".join(errors))
        document["actions"][0] = {**self.manifest["actions"][0], "type": "photo-protected"}
        actions.apply_actions(
            document, self.root, self.catalog, {}, "Various",
            backup_fn=lambda *_: "verified", save_fn=self.save,
        )
        self.assertEqual(self.catalog["photos"][self.photo_id]["rejectedPersonIds"], [self.ids[1]])

    def test_schema_reference_integrity_registered_ui_and_legacy_refusal(self):
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.digest, "protected": False, "rejectedPersonIds": ["person_" + "d" * 32],
        }
        self.assertIn("has no person record", "\n".join(metadata.validation_errors(self.catalog)))
        self.assertNotIn("match-rejected", dict(review_gallery.action_options("Review", self.photo_id)))
        self.assertIn("match-rejected", dict(review_gallery.action_options(
            "Review", self.photo_id, registered=True,
        )))
        self.assertNotIn("match-rejected", dict(review_gallery.action_options(
            "Review", self.photo_id, registered=True, protected=True,
        )))
        with self.assertRaisesRegex(ValueError, "policy-driven planner"):
            plan_reconciliation([{
                "photoId": self.photo_id, "sourceFolder": "Various", "sourceBucket": "Pool",
                "side": "Prospects", "vector": np.array([1., 0.]), "rejectedPersonIds": [self.ids[0]],
            }], {}, name_factory=lambda *_: "New Person")

    def test_review_approval_cannot_readmit_photo_to_rejected_identity(self):
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.digest, "protected": False, "rejectedPersonIds": [self.ids[0]],
        }
        self.manifest["actions"][0]["type"] = "review-approved"
        errors, _ = actions.validate_manifest(self.manifest, self.root, self.catalog, "Various")
        self.assertIn("explicitly rejected", "\n".join(errors))
        self.assertTrue(self.source.is_file())

    def test_stale_rejections_cannot_be_rebound_by_protection_or_new_identity_moves(self):
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": "f" * 64, "protected": False, "rejectedPersonIds": [self.ids[0]],
        }
        self.manifest["actions"][0]["type"] = "photo-protected"
        errors, _ = actions.validate_manifest(self.manifest, self.root, self.catalog, "Various")
        self.assertIn("rejected-identity metadata is stale", "\n".join(errors))
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        move = {
            "photoId": self.photo_id, "sha256": self.digest, "reason": "test",
            "source": self.source.relative_to(self.root).as_posix(),
            "destination": "Prospects/New/gallery/" + self.source.name,
        }
        with self.assertRaisesRegex(ValueError, "rejected-identity metadata is stale"):
            maintenance.apply_moves(
                self.root, [move], self.policy, {}, backup_fn=lambda *_: self.fail("must stop before backup"),
            )
        self.assertTrue(self.source.is_file())

    def test_rebuild_install_cannot_overwrite_rejections_added_after_preview(self):
        path = self.root / ".likeness-library.json"
        metadata.save_catalog(self.catalog, path)
        plan = {"sourceCatalogSHA256": metadata.content_sha256(path)}
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.digest, "protected": False, "rejectedPersonIds": [self.ids[0]],
        }
        metadata.save_catalog(self.catalog, path)
        with self.assertRaisesRegex(ValueError, "catalogue changed since"):
            clean_rebase.install_plan(
                {"working_root": self.root, "source_root": self.root}, self.root, plan,
            )
        with self.assertRaisesRegex(ValueError, "predates persistent rejections"):
            clean_rebase.install_plan(
                {"working_root": self.root, "source_root": self.root}, self.root, {},
            )

    def test_rebuild_refuses_to_discard_noncast_rejection_before_measuring(self):
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.digest, "protected": False, "rejectedPersonIds": [self.ids[0]],
        }
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        api = SimpleNamespace(cw=SimpleNamespace(load_cfg=lambda: {}))
        with self.assertRaisesRegex(ValueError, "stable-ID migration"):
            clean_rebase.create_plan(
                {"working_root": self.root, "source_root": self.root}, self.root, self.policy, api,
            )

    def test_photo_hash_check_uses_sha256_not_embedding_cache_sha1(self):
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.digest, "protected": False, "rejectedPersonIds": [self.ids[0]],
        }
        photo = SimpleNamespace(path=self.source, name=self.source.name, sha="embedding-sha1")
        self.assertEqual(rejections.photo_state(self.catalog, photo), {"rejectedPersonIds": [self.ids[0]]})
        self.source.write_bytes(b"changed bytes")
        self.assertTrue(rejections.photo_state(self.catalog, photo).get("rejectionMetadataStale"))

    def test_folder_merge_check_includes_review_and_ignores_derived_files(self):
        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.digest, "protected": False, "rejectedPersonIds": [self.ids[1]],
        }
        conflict = rejections.folder_conflict(
            self.root, "Prospects/Alice", self.catalog, self.ids[1],
        )
        assert conflict is not None
        self.assertIn("explicitly rejected", conflict)
        self.assertIsNone(rejections.folder_conflict(
            self.root, "Prospects/Alice", self.catalog, self.ids[0],
        ))

    def test_pool_reject_without_permanent_action_does_not_invent_exclusion(self):
        self.manifest["actions"][0]["type"] = "rejected-to-various"
        self.reject()
        self.assertNotIn("rejectedPersonIds", self.catalog["photos"][self.photo_id])

    def test_legacy_mutation_boundary_refuses_persistent_rejections_before_moving(self):
        from tools.art import likeness

        self.catalog["photos"][self.photo_id] = {
            "contentSha256": self.digest, "protected": False, "rejectedPersonIds": [self.ids[0]],
        }
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        photo = SimpleNamespace(name=self.source.name, path=self.source)
        with self.assertRaisesRegex(ValueError, "policy-driven reconcile"):
            likeness.execute(
                [likeness.Move(photo, "Prospects/Beth", "legacy")], self.root, True, None,
            )
        self.assertTrue(self.source.is_file())

    def test_full_reconcile_command_loads_content_bound_exclusions(self):
        from tools.art import test_likeness as legacy

        fixture = legacy.LikenessTests()
        fixture.setUp()
        try:
            fixture.add("Prospects", "Alice", "ann", 4)
            fixture.add("Prospects", "Beth", "bob", 4)
            fixture.add("Prospects", "Various", "ann", 1)
            incoming = next((fixture.lib / "Prospects" / "Various" / "gallery").glob("*.jpg"))
            photo_id = metadata.photo_id_from_name(incoming.name)
            catalog = copy.deepcopy(self.catalog)
            catalog["photos"][photo_id] = {
                "contentSha256": metadata.content_sha256(incoming), "protected": False,
                "rejectedPersonIds": [self.ids[0]],
            }
            metadata.save_catalog(catalog, fixture.lib / ".likeness-library.json")
            output = fixture.tmp / "preview.json"
            before = incoming.read_bytes()
            result = fixture.run_tool("reconcile", "--out", str(output))
            self.assertNotIn("EXIT", result)
            report = json.loads(output.read_text(encoding="utf-8"))
            row = next(row for row in report["assignments"] + report["held"] if row["photoId"] == photo_id)
            self.assertNotEqual(row.get("destination"), "Prospects/Alice")
            self.assertNotEqual(row.get("reviewDestination"), "Prospects/Alice/review")
            self.assertEqual(row["excludedIdentityIds"], [self.ids[0]])
            self.assertEqual(incoming.read_bytes(), before)
        finally:
            fixture.tearDown()


if __name__ == "__main__":
    unittest.main()
