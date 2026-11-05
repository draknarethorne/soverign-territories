"""Approved Sisters admission is staged and never applies to Angels."""
import copy
import pathlib
import tempfile
import unittest
from types import SimpleNamespace

import numpy as np

from tools.art.likeness_library import clean_rebase, metadata
from tools.art.likeness_library.policy import evaluate_cast_admission, load_policy, validate_policy


class CastAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.policy = clean_rebase.core_protection_policy(load_policy())
        self.gates = {
            "score": .5, "margin": .1, "independent_support": 4,
            "quality_eligible": True, "policy": self.policy,
        }

    def test_boundary_and_all_independent_gates(self):
        self.assertEqual(evaluate_cast_admission("Sisters", **self.gates)["decision"], "admit")
        self.assertEqual(evaluate_cast_admission("Angels", **self.gates)["decision"], "hold")
        for override in (
            {"score": .499999}, {"margin": .099999}, {"independent_support": 3},
            {"quality_eligible": False}, {"rejection_history": True},
            {"metadata_stale": True}, {"protected": True},
        ):
            with self.subTest(override=override):
                self.assertEqual(evaluate_cast_admission("Sisters", **{**self.gates, **override})["decision"], "hold")
        invalid = copy.deepcopy(self.policy)
        invalid["categoryPolicies"]["Angels"]["galleryAdmissionEnabled"] = True
        with self.assertRaises(ValueError):
            validate_policy(invalid)

    def test_frozen_real_audit_admits_review_but_never_self_supports_or_bootstraps(self):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            photos, rows, paths = [], [], {}
            for index in range(7):
                bucket = "gallery" if index < 5 else "review"
                name = f"nyx_image_{123450 + index}.jpg"
                path = root / "Sisters" / "Nyx" / bucket / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(str(index).encode())
                vector = np.zeros(7)
                vector[0] = .8 if index < 5 else 1.
                if index < 5:
                    vector[index + 1] = .6
                photo = clean_rebase.Photo(path, "Sisters", "Nyx", "cache", {
                    "v": vector.tolist(), "faces": 1, "px": 100,
                })
                photo.vec = vector
                photos.append(photo)
                relative = path.relative_to(root).as_posix()
                paths[relative] = path
                rows.append({
                    "source": relative, "destination": relative, "oldFolder": "Sisters/Nyx",
                    "photoId": metadata.photo_id_from_name(name), "sha256": metadata.content_sha256(path),
                    "retainedCast": True, "releasedCast": False, "reason": "initial Review",
                })
            catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
            api = SimpleNamespace(cw=SimpleNamespace(photo_key=lambda name: pathlib.Path(name).stem))
            before = copy.deepcopy(rows)
            audit = clean_rebase._final_membership_outcomes(
                photos, rows, catalog, self.policy, {"minFace": 60, "multiFace": .3},
                root, set(), api, root, paths, acquire_protection=False,
            )
            self.assertEqual(audit["rows"][-1]["castAdmission"]["independentSupport"], 5)
            routed, receipt = clean_rebase._admit_cast(rows, audit, self.policy)
            self.assertEqual(receipt["admittedCount"], 2)
            self.assertTrue(all("/gallery/" in row["destination"] for row in routed))
            self.assertEqual(rows, before)
            plan = {"photos": routed[-2:], "castSeedPolicy": "core", "policy": self.policy}
            clean_rebase._verify_routes(plan, root)
            plan["photos"][0]["castAdmission"]["independentSupport"] = 0
            with self.assertRaisesRegex(ValueError, "every approved gate"):
                clean_rebase._verify_routes(plan, root)

    def test_non_cast_rival_margin_and_held_quality_are_enforced_by_audit(self):
        # A recorded decision cannot bypass the all-category rival gate.
        rows = [{"source": "Various/gallery/incoming_image_123456.jpg",
                 "destination": "Sisters/Nyx/review/incoming_image_123456.jpg", "reason": "review"}]
        decision = {
            "folder": "Sisters/Nyx", "score": .8, "margin": .05, "independentSupport": 5,
            "decision": "hold", "reason": "Models rival too close",
        }
        audit = {"reference": "frozen all-category", "rows": [{
            "source": rows[0]["source"], "photoId": "photo:image_123456", "castAdmission": decision,
        }]}
        routed, receipt = clean_rebase._admit_cast(rows, audit, self.policy)
        self.assertEqual(routed, rows)
        self.assertEqual(receipt["admittedCount"], 0)
