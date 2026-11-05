"""Cast resets never acquire shared-workspace publication authority."""
import copy
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

from tools.art import likeness
from tools.art.likeness_library import cast_workflow, clean_rebase, metadata
from tools.art.likeness_library.policy import load_policy


class CastWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.name = "nyx_image_123456.jpg"
        self.photo_id = metadata.photo_id_from_name(self.name)
        self.photo = SimpleNamespace(name=self.name, key="Sisters/Nyx")
        self.relative = f"Sisters/Nyx/gallery/{self.name}"
        self.entries = [(self.relative, self.photo, "gallery", "a" * 64)]
        self.catalog = {
            "photos": {self.photo_id: {"protected": False}},
            "people": {"nyx": {"identityAnchors": [self.photo_id]}},
        }
        self.cfg = {"photos": {"Nyx": self.name}, "flows": {
            "portrait": {"photos": {"Nyx": self.name}},
        }}
        self.cores = {"Sisters/Nyx": {"photoScores": {self.name: .4}}}
        self.api = SimpleNamespace(cw=SimpleNamespace())

    def test_default_reset_suppresses_anchor_and_automatic_protection_not_manual(self):
        for protection, expected in (
            ({"protected": False}, True),
            ({"protected": True, "protectionProvenance": {"recipeVersion": "independent-gallery-loo-v1"}}, True),
            ({"protected": True}, False),
            ({"protected": True, "automaticProtectionOverride": "enabled"}, False),
        ):
            with self.subTest(protection=protection):
                self.catalog["photos"][self.photo_id] = protection
                before = copy.deepcopy((self.catalog, self.cfg))
                local, ids, receipt = cast_workflow.reset_plan(
                    self.cfg, self.catalog, self.entries, self.cores, self.api,
                )
                self.assertEqual(self.photo_id in ids, expected)
                self.assertEqual(self.photo_id not in local["people"]["nyx"]["identityAnchors"], expected)
                self.assertEqual(len(receipt["decisions"]), 2)
                self.assertFalse(receipt["sharedPublicationAuthorized"])
                self.assertEqual((self.catalog, self.cfg), before)

    def test_scoped_low_score_none_and_invalid_cutoff(self):
        for spec, expected in (
            ({"mode": "scoped", "slots": ["Nyx"]}, True),
            ({"mode": "scoped", "slots": ["Other"]}, False),
            ({"mode": "low-score", "maximumOwnCoreSimilarity": .4}, False),
            ({"mode": "low-score", "maximumOwnCoreSimilarity": .401}, True),
            ({"mode": "none"}, False),
        ):
            _, ids, _ = cast_workflow.reset_plan(
                self.cfg, self.catalog, self.entries, self.cores, self.api, spec,
            )
            self.assertEqual(self.photo_id in ids, expected)
        for invalid in (None, float("nan"), True, -2):
            with self.assertRaises(ValueError):
                cast_workflow.reset_plan(self.cfg, self.catalog, self.entries, self.cores, self.api, {
                    "mode": "low-score", "maximumOwnCoreSimilarity": invalid,
                })

    def test_create_plan_excludes_old_selection_and_anchor_before_reference_matching(self):
        from .test_clean_rebase import CleanRebaseTests

        fixture = CleanRebaseTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        folder = fixture.source / "Sisters" / "Nyx"
        names = [f"nyx_image_{123450 + index}.jpg" for index in range(4)]
        for index, name in enumerate(names):
            path = folder / "gallery" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(str(index).encode())
            fixture.layout["manifest_files"][path.relative_to(fixture.source).as_posix()] = (
                path.stat().st_size, metadata.content_sha256(path),
            )
        selected_id = metadata.photo_id_from_name(names[0])
        catalog = {
            "schemaVersion": 1, "photos": {selected_id: {
                "protected": False, "contentSha256": metadata.content_sha256(folder / "gallery" / names[0]),
            }}, "actions": [],
            "people": {"person_" + "a" * 32: {
                "id": "person_" + "a" * 32, "folder": "Sisters/Nyx", "displayName": "Nyx",
                "folderHistory": [], "protected": True, "identityAnchors": [selected_id],
            }},
        }
        fixture.working.mkdir(parents=True, exist_ok=True)
        metadata.save_catalog(catalog, fixture.working / ".likeness-library.json")
        cfg = {"photos": {"Nyx": names[0]}}
        api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: cfg, photo_key=likeness.cw.photo_key,
                photo_folders=lambda *_args: [
                    ("Sisters", "Nyx", folder), ("Potentials", "Fia", fixture.source_photo.parent.parent),
                ],
            ),
            originals=likeness.originals, nz=likeness.nz, chosen_keys=likeness.chosen_keys,
            invent_name=lambda *_args: "New Person",
        )
        calls = []

        def cores(space, current, **_kwargs):
            present = [metadata.photo_id_from_name(photo.name) for photo in space.by_key["Sisters/Nyx"]]
            calls.append(present)
            if len(calls) == 2:
                self.assertNotIn(selected_id, present)
                self.assertEqual(next(iter(current["people"].values()))["identityAnchors"], [])
            return {"Sisters/Nyx": {
                "vector": np.array([1., 0.]), "side": "Prospects", "category": "Sisters",
                "corePhotoIds": present, "photoScores": {name: .8 for name in names if metadata.photo_id_from_name(name) in present},
            }}, set(), []

        def matching(candidates, *_args, **_kwargs):
            self.assertIn(selected_id, {row["photoId"] for row in candidates})
            return {"assignments": [], "clusters": [],
                    "held": [{"photoId": row["photoId"], "reason": "review"} for row in candidates]}

        def audit(_photos, rows, *_args, **_kwargs):
            return {"reference": "frozen", "rows": [{
                "source": row["source"], "destination": row["destination"], "photoId": row["photoId"],
                "ownScore": None, "qualityEligible": True,
            } for row in rows]}

        with mock.patch.object(clean_rebase, "frozen_identity_cores", side_effect=cores), \
                mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=matching), \
                mock.patch.object(clean_rebase, "_final_membership_outcomes", side_effect=audit):
            result = clean_rebase.create_plan(
                fixture.layout, fixture.run, load_policy(), api, cast_seeds="core",
                embedder=lambda _path: {"v": [1., 0.], "faces": 1, "px": 100},
            )
        selected = next(row for row in result["photos"] if row["photoId"] == selected_id)
        self.assertTrue(selected["releasedCast"])
        self.assertFalse(selected["castSeedAnchor"])
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["workflowSelection"]["decisions"][0]["state"], "hold")
        self.assertEqual(cfg, {"photos": {"Nyx": names[0]}})

    def test_selection_highest_eligible_score_stable_ties_no_singleton_self_score(self):
        _, _, receipt = cast_workflow.reset_plan(self.cfg, self.catalog, self.entries, self.cores, self.api)
        rows = []
        for photo_id, score, bucket in (("photo:image_100002", .6, "gallery"),
                                        ("photo:image_100001", .6, "gallery"),
                                        ("photo:image_100003", .99, "review"),
                                        ("photo:image_100004", None, "gallery")):
            rows.append({
                "source": photo_id, "photoId": photo_id, "ownScore": score,
                "destination": f"Sisters/Nyx/{bucket}/{photo_id[6:]}.jpg", "qualityEligible": True,
            })
        result = cast_workflow.finish_receipt(receipt, {"rows": rows}, [
            {"source": row["source"], "destination": row["destination"]} for row in rows
        ])
        self.assertEqual(result["decisions"][0]["newPhotoId"], "photo:image_100001")
        self.assertEqual(result["decisions"][0]["newOwnScore"], .6)
        held = cast_workflow.finish_receipt(receipt, {"rows": rows[2:]}, [])
        self.assertEqual(held["decisions"][0]["state"], "hold")

    def test_inventory_all_loadimages_handmade_and_input_bytes_without_mutation(self):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            workflow = root / "Nyx_Qwen_test.json"
            workflow.write_text(json.dumps({"nodes": [
                {"type": "LoadImage", "widgets_values": [self.name]},
                {"type": "LoadImage", "widgets_values": ["alternate.png"]},
            ]}), encoding="utf-8")
            inputs = root / "inputs"
            inputs.mkdir()
            (inputs / self.name).write_bytes(b"selected pixels")
            before = workflow.read_bytes()
            api = SimpleNamespace(cw=SimpleNamespace(
                install_files=lambda _cfg, _ws: {workflow.name: workflow},
                is_hand_made=lambda *_args: True, input_dir=lambda *_args: inputs,
            ))
            cfg = {**self.cfg, "workspaces": {"manual": {}}}
            _, _, receipt = cast_workflow.reset_plan(cfg, self.catalog, self.entries, self.cores, api)
            inventory = cast_workflow.publication_inventory(cfg, receipt, api)
            self.assertEqual(len(inventory), 2)
            self.assertTrue(all(row["manual"] for row in inventory))
            self.assertIsNotNone(inventory[0]["inputSHA256"])
            self.assertIsNone(inventory[1]["inputSHA256"])
            self.assertEqual(workflow.read_bytes(), before)
