"""Explicit cast admission uses frozen evidence and independent Gallery minima."""
import copy
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace

import numpy as np
import jsonschema

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
        for category in set(self.policy["categoryPolicies"]) - {"Sisters", "Angels"}:
            invalid = copy.deepcopy(self.policy)
            invalid["categoryPolicies"][category]["galleryAdmissionEnabled"] = True
            with self.subTest(category=category), self.assertRaises(ValueError):
                validate_policy(invalid)

    def test_explicit_angel_gate_preserves_review_routes_and_all_other_holds(self):
        policy = copy.deepcopy(self.policy)
        rules = policy["categoryPolicies"]["Angels"]
        before = rules["photoRouteMinimum"]
        rules.update(galleryAdmissionEnabled=True, galleryAdmissionMinimumSimilarity=.45)
        validate_policy(policy)
        gates = {**self.gates, "policy": policy, "score": .45}
        self.assertEqual(evaluate_cast_admission("Angels", **gates)["decision"], "admit")
        self.assertIn("Angels Gallery admission", evaluate_cast_admission("Angels", **gates)["reason"])
        self.assertEqual(evaluate_cast_admission("Sisters", **gates)["decision"], "hold")
        self.assertEqual(rules["photoRouteMinimum"], before)
        for override in (
            {"score": .449999}, {"margin": .099999}, {"independent_support": 3},
            {"quality_eligible": False}, {"rejection_history": True},
            {"metadata_stale": True}, {"protected": True},
        ):
            with self.subTest(override=override):
                self.assertEqual(evaluate_cast_admission("Angels", **{**gates, **override})["decision"], "hold")
        rules["galleryAdmissionMinimumSimilarity"] = .50
        validate_policy(policy)
        self.assertEqual(evaluate_cast_admission("Angels", **gates)["decision"], "hold")
        self.assertEqual(evaluate_cast_admission("Angels", **{**gates, "score": .50})["decision"], "admit")

    def test_shared_admission_schema_and_minimum_validation(self):
        schema = json.loads((
            pathlib.Path(__file__).resolve().parents[4] / "data" / "art" / "_schema"
            / "likeness-engine-policy.schema.json"
        ).read_text(encoding="utf-8"))
        validator = jsonschema.Draft7Validator(schema)
        policy = copy.deepcopy(self.policy)
        rules = policy["categoryPolicies"]["Angels"]
        rules.update(galleryAdmissionEnabled=True, galleryAdmissionMinimumSimilarity=.45)
        validate_policy(policy)
        self.assertEqual(list(validator.iter_errors(policy)), [])
        for value in (True, None, -.01, 1.01, "0.45"):
            rules["galleryAdmissionMinimumSimilarity"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_policy(policy)
            self.assertTrue(list(validator.iter_errors(policy)))
        rules["galleryAdmissionMinimumSimilarity"] = .51
        with self.assertRaisesRegex(ValueError, "must not be lower"):
            validate_policy(policy)
        rules["galleryAdmissionMinimumSimilarity"] = .45
        policy["categoryPolicies"]["Models"]["galleryAdmissionEnabled"] = True
        self.assertTrue(list(validator.iter_errors(policy)))

    def test_frozen_real_audit_admits_review_but_never_self_supports_or_bootstraps(self):
        self._assert_frozen_admission("Sisters")

    def test_angel_audit_routing_and_saved_route_verification_use_shared_gates(self):
        self.policy["categoryPolicies"]["Angels"].update(
            galleryAdmissionEnabled=True, galleryAdmissionMinimumSimilarity=.45,
        )
        validate_policy(self.policy)
        self._assert_frozen_admission("Angels")

    def _assert_frozen_admission(self, category):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            photos, rows, paths = [], [], {}
            for index in range(7):
                bucket = "gallery" if index < 5 else "review"
                name = f"nyx_image_{123450 + index}.jpg"
                path = root / category / "Nyx" / bucket / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(str(index).encode())
                vector = np.zeros(7)
                vector[0] = .8 if index < 5 else 1.
                if index < 5:
                    vector[index + 1] = .6
                photo = clean_rebase.Photo(path, category, "Nyx", "cache", {
                    "v": vector.tolist(), "faces": 1, "px": 100,
                })
                photo.vec = vector
                photos.append(photo)
                relative = path.relative_to(root).as_posix()
                paths[relative] = path
                rows.append({
                    "source": relative, "destination": relative, "oldFolder": f"{category}/Nyx",
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
