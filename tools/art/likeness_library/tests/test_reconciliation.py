#!/usr/bin/env python3
"""Tests for frozen-core, deterministic Review and pool reconciliation."""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.art.likeness_library.reconciliation import (  # noqa: E402
    frozen_identity_cores,
    plan_reconciliation,
)
from tools.art import likeness  # noqa: E402
from tools.art.likeness import apply_category_changes  # noqa: E402


def candidate(photo_id, vector, *, folder="Various", bucket="Pool", side="Prospects", **values):
    return {
        "photoId": photo_id,
        "sourceFolder": folder,
        "sourceBucket": bucket,
        "side": side,
        "vector": np.asarray(vector, dtype=float),
        **values,
    }


def stable_name(seed, taken):
    name = f"New-{seed[:8]}"
    return f"Other-{seed[:8]}" if name.casefold() in taken else name


class ReconciliationTests(unittest.TestCase):
    def test_individually_yellow_cast_matches_can_build_a_model_cluster(self):
        from tools.art.likeness_library.policy import load_policy

        result = plan_reconciliation(
            [
                candidate(f"photo:image_{900000 + index}", [.45, np.sqrt(1 - .45**2)])
                for index in range(6)
            ],
            {
                "Angels/Angelica": {
                    "vector": np.array([1., 0.]), "side": "Prospects", "category": "Angels",
                },
            },
            cluster=.55, policy=load_policy(), name_factory=stable_name,
        )
        self.assertEqual(result["assignedCount"], 6)
        self.assertEqual(result["held"], [])
        self.assertTrue(result["clusters"][0]["destination"].startswith("Models/"))

    def test_category_moves_create_missing_configured_destination_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = root / "Prospects" / "Sophie"
            source.mkdir(parents=True)
            photo = source / "gallery" / "sophie.jpg"
            photo.parent.mkdir()
            photo.write_bytes(b"photo")

            moved = apply_category_changes(
                root,
                [("Prospects/Sophie", "Models/Sophie", 1, False)],
                {"Prospects", "Models"},
            )

            self.assertEqual(moved, 1)
            self.assertFalse(source.exists())
            self.assertEqual(
                (root / "Models" / "Sophie" / "gallery" / "sophie.jpg").read_bytes(),
                b"photo",
            )

    def test_workflow_selected_photos_are_collected_across_all_flows(self):
        config = {
            "photos": {"Sophie": "sophie_image_500001.jpg"},
            "flows": {
                "alpha": {"photos": {"Sophie": "sophie_image_500002.jpg"}},
            },
        }

        selected = likeness.chosen_keys(config)

        self.assertEqual(
            selected,
            {
                likeness.cw.photo_key("sophie_image_500001.jpg"),
                likeness.cw.photo_key("sophie_image_500002.jpg"),
            },
        )

    def test_review_and_pool_candidates_form_one_order_independent_cluster(self):
        rows = [
            candidate("photo:image_100001", [1, 0], folder="Various"),
            candidate("photo:image_100002", [0.99, 0.01], folder="Prospects/Sophie", bucket="Review"),
            candidate("photo:image_100003", [0.98, 0.02], folder="Various"),
        ]
        first = plan_reconciliation(rows, {}, name_factory=stable_name)
        second = plan_reconciliation(list(reversed(rows)), {}, name_factory=stable_name)

        self.assertEqual(first["clusters"], second["clusters"])
        self.assertEqual(first["assignments"], second["assignments"])
        self.assertEqual(first["held"], [])
        self.assertEqual(first["clusters"][0]["destinationType"], "provisional")
        self.assertTrue(first["clusters"][0]["destination"].startswith("Potentials/"))
        self.assertEqual(first["assignedCount"], 3)

    def test_confident_existing_match_respects_margin_and_artist_boundary(self):
        cores = {
            "Prospects/A": {"vector": np.array([1.0, 0.0]), "side": "Prospects"},
            "Prospects/B": {"vector": np.array([0.0, 1.0]), "side": "Prospects"},
            "Artists/One/Person": {"vector": np.array([1.0, 0.0]), "side": "Artists"},
        }
        rows = [
            candidate("photo:image_200001", [0.99, 0.01]),
            candidate("photo:image_200002", [0.71, 0.70]),
            candidate("photo:image_200003", [0.99, 0.01], side="Artists"),
        ]

        result = plan_reconciliation(rows, cores, name_factory=stable_name)

        assigned = {row["photoId"]: row["destination"] for row in result["assignments"]}
        self.assertEqual(assigned["photo:image_200001"], "Prospects/A")
        self.assertEqual(assigned["photo:image_200003"], "Artists/One/Person")
        self.assertIn("photo:image_200002", {row["photoId"] for row in result["held"]})

    def test_policy_protects_target_identity_from_photo_routing(self):
        from tools.art.likeness_library.policy import load_policy

        cores = {
            "Prospects/Protected": {
                "vector": np.array([1.0, 0.0]),
                "side": "Prospects",
                "category": "Prospects",
                "identityProtected": True,
            }
        }
        result = plan_reconciliation(
            [candidate("photo:image_200004", [1.0, 0.0])],
            cores,
            minimum_cluster=3,
            cluster=0.55,
            policy=load_policy(),
            name_factory=stable_name,
        )

        self.assertEqual(result["assignments"], [])
        self.assertEqual(result["held"][0]["reviewDestination"], "Prospects/Protected/review")
        self.assertIn("protected Gallery", result["held"][0]["reason"])

    def test_small_incoming_cast_like_cluster_is_held_for_the_best_cast_review(self):
        from tools.art.likeness_library.policy import load_policy

        vectors = []
        for score in (0.315, 0.464, 0.411, 0.455):
            vectors.append([score, np.sqrt(1 - score**2)])
        cores = {
            "Angels/angelica": {
                "vector": np.array([1.0, 0.0]),
                "side": "Prospects",
                "category": "Angels",
                "identityProtected": True,
            },
            "Sisters/Draknara": {
                "vector": np.array([-1.0, 0.0]),
                "side": "Prospects",
                "category": "Sisters",
                "identityProtected": True,
            },
        }
        rows = [
            candidate(f"photo:image_{210001 + index}", vector)
            for index, vector in enumerate(vectors)
        ]

        result = plan_reconciliation(
            rows,
            cores,
            assign=0.40,
            margin=0.10,
            cluster=0.25,
            minimum_cluster=3,
            policy=load_policy(),
            name_factory=stable_name,
        )

        self.assertEqual(result["assignments"], [])
        self.assertEqual(result["heldCount"], 4)
        self.assertEqual(
            {row["reviewDestination"] for row in result["held"]},
            {"Angels/angelica/review"},
        )
        self.assertTrue(
            all(row["bestMatch"] == "Angels/angelica" for row in result["held"])
        )

    def test_draft_proposal_reports_qualified_destination_without_authorizing_apply(self):
        from tools.art.likeness_library.policy import load_policy

        result = plan_reconciliation(
            [candidate("photo:image_200005", [1.0, 0.0])],
            {
                "Potentials/Amara Madison": {
                    "vector": np.array([1.0, 0.0]),
                    "side": "Prospects",
                    "category": "Potentials",
                }
            },
            minimum_cluster=3,
            cluster=0.55,
            policy=load_policy(),
            name_factory=stable_name,
        )

        self.assertTrue(result["authorizationRequired"])
        self.assertEqual(result["held"], [])
        self.assertEqual(result["assignments"][0]["destination"], "Potentials/Amara Madison")
        self.assertEqual(result["assignments"][0]["score"], 1.0)

    def test_policy_preserves_a_perfect_pair_without_cast_assignment_gate(self):
        from tools.art.likeness_library.policy import load_policy

        result = plan_reconciliation(
            [candidate("p1", [0, 1]), candidate("p2", [0, 1])],
            {"Angels/A": {"vector": np.array([1., 0.]), "side": "Prospects"}},
            minimum_cluster=3, cluster=.55, policy=load_policy(), name_factory=stable_name,
        )
        self.assertEqual(result["assignedCount"], 2)
        self.assertEqual(len(result["clusters"]), 1)
        self.assertEqual(result["clusters"][0]["photoIds"], ["p1", "p2"])

    def test_cast_protection_does_not_change_unrelated_grouping(self):
        from tools.art.likeness_library.policy import load_policy

        rows = [candidate("p1", [0, 1]), candidate("p2", [0, 1])]
        policy = load_policy()
        first = plan_reconciliation(rows, {}, policy=policy, name_factory=stable_name)
        second = plan_reconciliation(
            rows, {"Angels/A": {"vector": np.array([1., 0.]), "side": "Prospects", "identityProtected": True}},
            policy=policy, name_factory=stable_name,
        )
        self.assertEqual(first["clusters"][0]["photoIds"], second["clusters"][0]["photoIds"])

    def test_provisional_followup_reclassifies_final_five_photo_membership(self):
        from tools.art.likeness_library.policy import load_policy

        policy = load_policy()
        policy["identityActions"]["identityClusterMinimumSimilarity"] = .8
        rows = [
            candidate(str(index), [np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))])
            for index, angle in enumerate((-10, 0, 10, 15, 60))
        ]
        result = plan_reconciliation(rows, {}, policy=policy, name_factory=stable_name)
        self.assertEqual(len(result["clusters"]), 1)
        self.assertEqual(len(result["clusters"][0]["photoIds"]), 5)
        self.assertTrue(result["clusters"][0]["destination"].startswith("Prospects/"))

    def test_remaining_candidate_can_join_fixed_provisional_cluster(self):
        angles = [-10, 0, 10, 60]
        rows = [
            candidate(
                f"photo:image_{300001 + index}",
                [np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))],
                bucket="Review" if index == 1 else "Pool",
            )
            for index, angle in enumerate(angles)
        ]

        result = plan_reconciliation(
            rows,
            {},
            assign=0.48,
            margin=0.10,
            cluster=0.80,
            minimum_cluster=3,
            name_factory=stable_name,
        )

        self.assertEqual(len(result["clusters"]), 1)
        destination = result["clusters"][0]["destination"]
        joined = next(row for row in result["assignments"] if row["photoId"] == "photo:image_300004")
        self.assertEqual(joined["destination"], destination)
        self.assertEqual(joined["destinationType"], "provisional")
        self.assertIn("frozen provisional cluster", joined["reason"])

    def test_ambiguous_candidate_cluster_does_not_create_a_new_identity(self):
        cores = {
            "Prospects/A": {"vector": np.array([0.99, 0.10]), "side": "Prospects"},
            "Prospects/B": {"vector": np.array([0.99, -0.10]), "side": "Prospects"},
        }
        rows = [candidate(f"photo:image_{350001 + index}", [1, 0]) for index in range(3)]

        result = plan_reconciliation(rows, cores, name_factory=stable_name)

        self.assertEqual(result["assignments"], [])
        self.assertEqual(result["clusters"], [])
        self.assertEqual(result["heldCount"], 3)
        self.assertTrue(all("ambiguous destination" in row["reason"] for row in result["held"]))

    def test_protected_duplicate_and_missing_ids_stay_staged(self):
        rows = [
            candidate("photo:image_400001", [1, 0], protected=True),
            candidate("photo:image_400002", [1, 0], protected=True),
            candidate("photo:image_400002", [0.99, 0.01]),
            candidate(None, [1, 0]),
        ]

        result = plan_reconciliation(rows, {}, name_factory=stable_name)

        reasons = [row["reason"] for row in result["held"]]
        self.assertEqual(result["assignments"], [])
        self.assertIn("protected photo; remains staged", reasons)
        self.assertIn("duplicate stable photo ID; remains staged", reasons)
        self.assertIn("missing stable photo ID", reasons)

    def test_frozen_core_uses_anchors_and_excludes_protected_photos(self):
        photos = [
            FakePhoto("anchor", [1, 0]),
            FakePhoto("b", [0, 1]),
            FakePhoto("c", [0.01, 1]),
            FakePhoto("protected", [-1, 0]),
        ]
        space = SimpleNamespace(
            photos=photos,
            by_key={"Prospects/Sophie": photos},
            st={"minFace": 60},
        )
        catalog = {
            "people": {
                "person_1": {
                    "folder": "Prospects/Sophie",
                    "identityAnchors": ["anchor"],
                }
            },
            "photos": {
                "anchor": {"contentSha256": "anchor-hash", "protected": False},
                "protected": {"contentSha256": "protected-hash", "protected": True},
            },
        }

        cores, locked, diagnostics = frozen_identity_cores(
            space,
            catalog,
            photo_id_fn=lambda name: name,
            content_sha256_fn=lambda path: f"{path}-hash",
        )

        np.testing.assert_allclose(cores["Prospects/Sophie"]["vector"], [1, 0])
        self.assertEqual(cores["Prospects/Sophie"]["mode"], "trusted")
        self.assertIn("protected", locked)
        self.assertEqual(diagnostics, [])

    def test_stale_anchor_is_ignored_for_core_construction(self):
        photos = [
            FakePhoto("anchor", [1, 0]),
            FakePhoto("b", [0, 1]),
            FakePhoto("c", [0.01, 1]),
            FakePhoto("d", [0.02, 1]),
        ]
        space = SimpleNamespace(
            photos=photos,
            by_key={"Prospects/Sophie": photos},
            st={"minFace": 60},
        )
        catalog = {
            "people": {
                "person_1": {
                    "folder": "Prospects/Sophie",
                    "identityAnchors": ["anchor"],
                }
            },
            "photos": {"anchor": {"contentSha256": "old-hash", "protected": True}},
        }

        cores, locked, _ = frozen_identity_cores(
            space,
            catalog,
            photo_id_fn=lambda name: name,
            content_sha256_fn=lambda _path: "new-hash",
        )

        self.assertEqual(cores["Prospects/Sophie"]["mode"], "provisional")
        self.assertNotIn("anchor", locked)
        self.assertGreater(cores["Prospects/Sophie"]["vector"][1], 0.99)

    def test_reconcile_command_writes_report_without_changing_source_photo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            photo_path = root / "sophie_image_500001.jpg"
            photo_path.write_bytes(b"unchanged source")
            photo = FakePhoto(photo_path.name, [1, 0])
            photo.path = photo_path
            photo.key = "Various"
            report_path = root / "reconciliation.json"
            settings = {
                "pool": ["Various"],
                "minFace": 60,
                "assign": 0.40,
                "margin": 0.10,
                "cluster": 0.25,
                "minCluster": 3,
                "castMerge": 0.55,
            }
            args = SimpleNamespace(root=None, embedder=None, out=str(report_path), policy=None)
            output = io.StringIO()
            with mock.patch.object(
                likeness,
                "build",
                return_value=(
                    {"photos": {"Sophie": photo_path.name}, "flows": {}},
                    settings,
                    root,
                    None,
                    SimpleNamespace(photos=[photo], by_key={}, st=settings),
                ),
            ), mock.patch.object(likeness, "load_review", return_value=[]), mock.patch.object(
                likeness.metadata, "load_catalog", return_value={"people": {}, "photos": {}}
            ), mock.patch.object(likeness.cw, "photo_folders", return_value=[]), mock.patch.object(
                likeness, "junk_reason", return_value=False
            ), contextlib.redirect_stdout(output):
                likeness.cmd_reconcile(args)

            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["candidateCount"], 1)
            self.assertEqual(report["heldCount"], 1)
            self.assertEqual(report["held"][0]["reason"], "workflow-selected photo; remains staged")
            self.assertEqual(report["source"], "likeness-reconcile")
            self.assertIn("No images or catalogue data are changed", output.getvalue())
            self.assertEqual(photo_path.read_bytes(), b"unchanged source")


class FakePhoto:
    def __init__(self, name, vector):
        self.name = name
        self.path = name
        self.vec = np.asarray(vector, dtype=float)

    def usable(self, _minimum):
        return True


if __name__ == "__main__":
    unittest.main()
