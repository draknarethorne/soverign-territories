"""Receipt-only scope, parity, repeatability and output-boundary contracts."""
import copy
import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest import mock

import numpy as np

from tools.art import likeness_shadow
from tools.art.likeness_library import shadow

ROOT = pathlib.Path(__file__).resolve().parents[4]


def photo(pid, folder, **extra):
    return {"photoId": pid, "destination": f"{folder}/gallery/{pid}.png",
            "oldFolder": folder, **extra}


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.run = {
            "photos": [
                photo("a", "Angels/angelica"), photo("v", "Models/Amira Vale"),
                photo("u", "Models/Uma Zane"), photo("g", "Models/Gaia Thorn"),
                photo("x", "Models/Outside"), photo("y", "Models/Remote"),
                photo("n", "Models/Notvalentine"),
            ],
            "finalMembershipAudit": {"rows": [
                {"photoId": "x", "rivals": [
                    {"folder": "Models/Amira Vale", "score": .54},
                    {"folder": "Models/Remote", "score": .36},
                ]},
            ]},
        }

    def test_all_seed_groups_and_reverse_rivals_without_recursive_explosion(self):
        result = shadow.select_scope(self.run)
        folders = {row["folder"] for row in result["identities"]}
        self.assertEqual(len(folders), 5)
        self.assertIn("Models/Outside", folders)
        self.assertNotIn("Models/Remote", folders)
        self.assertNotIn("Models/Notvalentine", folders)
        self.assertEqual(shadow.select_scope(self.run, hops=2)["photoCount"], 6)
        self.assertEqual(len(result["photos"]), 5)
        self.assertTrue(all(row["humanLabel"].startswith("unlabelled") for row in result["photos"]))

    def test_missing_seed_and_scope_overflow_refuse(self):
        with self.assertRaisesRegex(ValueError, "no saved identity"):
            shadow.select_scope(self.run, seeds=["missing"])
        with self.assertRaisesRegex(ValueError, "never silently truncate"):
            shadow.select_scope(self.run, max_photos=4)

    def test_no_scope_mutation_and_various_supported(self):
        original = copy.deepcopy(self.run)
        shadow.select_scope(self.run)
        self.assertEqual(self.run, original)
        self.assertEqual(shadow.folder_for({"destination": "Various/review/x.png"}), "Various")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            shadow.folder_for({"destination": "Models/Vale/series/gallery/x.png"})


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / "tmp")
        self.addCleanup(self.temporary.cleanup)
        self.path = pathlib.Path(self.temporary.name)
        mean = [0., 0.]
        model = {"recognizer": "fixture"}
        model_id = hashlib.sha256(
            json.dumps(model, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.cache = {"centeringMean": mean, "emb": {
            "cache-key": {"v": [1., 0.], "alignmentEvidence": {
                "sourceSha256": "content", "model": model, "modelId": model_id,
            }},
        }}
        self.run = {
            "status": "applied", "castSeedPolicy": "core", "policy": {},
            "workflowSelection": {"policy": {"mode": "all"}},
            "implementationHashes": {
                name: shadow.digest(pathlib.Path(shadow.__file__).parent / name)
                for name in shadow.REPLAY_MODULES if name != "scoring.py"
            }, "centeringMean": mean,
            "photos": [photo("a", "Angels/angelica", preparedSHA256="content", castSeedCore=True)],
        }
        self.write("policy.json", {})
        self.write("seed-catalog.json", {"photos": {}, "people": {}, "actions": []})
        self.write("config-snapshot.json", {})
        self.run["seedCatalogSHA256"] = shadow.digest(self.path / "seed-catalog.json")
        self.run["configSnapshotSHA256"] = shadow.digest(self.path / "config-snapshot.json")
        self.save()

    def write(self, name, value):
        (self.path / name).write_text(json.dumps(value), encoding="utf-8")

    def save(self):
        self.write("likeness-cache.json", self.cache)
        self.run["continuationCacheSHA256"] = shadow.digest(self.path / "likeness-cache.json")
        self.write("run.json", self.run)

    def test_receipt_only_vectors_keep_global_mean(self):
        self.run["centeringMean"] = [.2, .4]
        self.cache["centeringMean"] = [.2, .4]
        self.save()
        run, vectors, provenance = shadow.load_bundle(self.path)
        np.testing.assert_allclose(vectors["a"], shadow.nz(np.array([.8, -.4])))
        self.assertEqual(run["photos"][0]["photoId"], "a")
        self.assertEqual(provenance["imageReads"], 0)
        self.assertEqual(provenance["modelCalls"], 0)

    def test_missing_measurement_and_stale_center_refuse(self):
        self.run["photos"][0]["preparedSHA256"] = "missing"
        self.save()
        with self.assertRaisesRegex(ValueError, "missing content-bound"):
            shadow.load_bundle(self.path)
        self.cache["centeringMean"] = [1., 0.]
        self.save()
        with self.assertRaisesRegex(ValueError, "different centering"):
            shadow.load_bundle(self.path)

    def test_model_and_seed_content_bindings_refuse(self):
        self.cache["emb"]["cache-key"]["alignmentEvidence"]["modelId"] = "wrong"
        self.save()
        with self.assertRaisesRegex(ValueError, "invalid model provenance"):
            shadow.load_bundle(self.path)
        self.write("seed-catalog.json", {"photos": {"manual": {}}, "people": {}})
        with self.assertRaisesRegex(ValueError, "seedCatalogSHA256"):
            shadow.load_bundle(self.path)

    def test_cache_bytes_are_bound_to_continuation_receipt(self):
        self.write("likeness-cache.json", {})
        with self.assertRaisesRegex(ValueError, "cached measurements differ"):
            shadow.load_bundle(self.path)

    def test_json_input_limit_refuses_before_parsing(self):
        with self.assertRaisesRegex(ValueError, "input-byte limit"):
            shadow.load_bundle(self.path, max_json_bytes=1)

    def test_nonempty_manual_intent_cannot_be_silently_discarded(self):
        self.write("seed-catalog.json", {"photos": {"manual": {}}, "people": {}})
        self.run["seedCatalogSHA256"] = shadow.digest(self.path / "seed-catalog.json")
        self.save()
        with self.assertRaisesRegex(ValueError, "manual-intent seed"):
            shadow.load_bundle(self.path)

    def test_duplicate_ids_and_changed_implementation_refuse(self):
        self.run["photos"].append(copy.deepcopy(self.run["photos"][0]))
        self.save()
        with self.assertRaisesRegex(ValueError, "unique stable IDs"):
            shadow.load_bundle(self.path)
        self.run["implementationHashes"]["planner.py"] = "changed"
        self.save()
        with self.assertRaisesRegex(ValueError, "baseline implementation differs"):
            shadow.load_bundle(self.path)


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.run = {
            "photos": [
                photo("a", "Angels/angelica", castSeedCore=True),
                photo("b", "Models/Vale", initialBestCast="Angels/angelica", initialBestCastScore=.8),
            ],
            "candidateCount": 1, "policy": {},
            "membershipRefinement": {
                "passCount": 0, "stopReason": "stable", "moveCount": 0, "mergeCount": 0,
                "dissolvedCount": 0, "passes": [],
            },
        }
        self.vectors = {"a": np.array([1., 0.]), "b": np.array([.8, .6])}

    def test_exact_saved_cast_parity_and_count(self):
        candidates, cores = shadow.replay_inputs(self.run, self.vectors)
        self.assertEqual([row["photoId"] for row in candidates], ["b"])
        self.assertEqual(list(cores), ["Angels/angelica"])
        self.run["photos"][1]["initialBestCastScore"] = .9
        with self.assertRaisesRegex(ValueError, "parity failed"):
            shadow.replay_inputs(self.run, self.vectors)

    def test_repeat_and_order_trials_call_shared_engine_without_input_mutation(self):
        self.run["photos"].append(photo(
            "c", "Models/Other", initialBestCast="Angels/angelica", initialBestCastScore=.8,
        ))
        self.run["candidateCount"] = 2
        self.vectors["c"] = np.array([.8, .6])
        result = {"assignments": [{"photoId": "b", "clusterId": "group",
                                  "destination": "Models/Shadow group"},
                                 {"photoId": "c", "clusterId": "other",
                                  "destination": "Models/Shadow other"}], "held": []}
        before = copy.deepcopy(self.run)
        with mock.patch.object(shadow, "plan_candidates", return_value=result) as planner:
            with mock.patch.object(shadow.refinement, "refine",
                                   return_value=(result, self.run["membershipRefinement"])):
                trial = shadow.experiment(self.run, self.vectors, compare_order=True)
        self.assertEqual(planner.call_count, 3)
        self.assertEqual([row["photoId"] for row in planner.call_args_list[0].args[0]], ["b", "c"])
        self.assertEqual([row["photoId"] for row in planner.call_args_list[2].args[0]], ["c", "b"])
        self.assertEqual(len(trial["trials"]), 3)
        self.assertEqual(self.run, before)

    def test_saved_refinement_mismatch_is_not_success_shaped(self):
        wrong = {**self.run["membershipRefinement"], "moveCount": 1}
        with mock.patch.object(shadow, "plan_candidates", return_value={}):
            with mock.patch.object(shadow.refinement, "refine",
                                   return_value=({"assignments": [{"photoId": "b", "clusterId": "g"}],
                                                  "held": []}, wrong)):
                with self.assertRaisesRegex(ValueError, "provisional refinement parity failed"):
                    shadow.experiment(self.run, self.vectors)

    def test_repeat_drift_is_an_error(self):
        first = {"assignments": [{"photoId": "b", "clusterId": "g", "destination": "Models/One"}], "held": []}
        changed = {"assignments": [{"photoId": "b", "clusterId": "g", "destination": "Models/Two"}], "held": []}
        with mock.patch.object(shadow, "plan_candidates", side_effect=[first, changed]):
            with mock.patch.object(shadow.refinement, "refine",
                                   side_effect=lambda result, *args: (result, self.run["membershipRefinement"])):
                with self.assertRaisesRegex(ValueError, "identical-repeat changed"):
                    shadow.experiment(self.run, self.vectors, compare_order=True)

    def test_missing_and_duplicate_decisions_refuse(self):
        with mock.patch.object(shadow, "plan_candidates", return_value={}):
            with mock.patch.object(shadow.refinement, "refine",
                                   return_value=({"assignments": [], "held": []},
                                                 self.run["membershipRefinement"])):
                with self.assertRaisesRegex(ValueError, "conserve all photo IDs"):
                    shadow.experiment(self.run, self.vectors)
        row = {"photoId": "b", "clusterId": "g"}
        with self.assertRaisesRegex(ValueError, "duplicate photo IDs"):
            shadow.stage_fingerprint({"assignments": [row, row], "held": []})

    def test_dry_run_never_executes_planner_or_creates_output(self):
        out = ROOT / "tmp" / "shadow-dry-test-not-created"
        self.run["finalMembershipAudit"] = {"rows": []}
        with mock.patch.object(shadow, "load_bundle", return_value=(self.run, self.vectors, {})):
            with mock.patch.object(shadow, "experiment") as experiment:
                status = likeness_shadow.main([
                    "--run", str(ROOT), "--out", str(out), "--seed", "angelica", "--dry-run",
                ])
        self.assertEqual(status, 0)
        experiment.assert_not_called()
        self.assertFalse(out.exists())

    def test_global_candidate_cap_is_separate_from_photo_scope_cap(self):
        self.run["photos"].append(photo("c", "Models/Other", initialBestCast="Angels/angelica"))
        with mock.patch.object(shadow, "load_bundle", return_value=(self.run, self.vectors, {})):
            with mock.patch.object(shadow, "experiment") as experiment:
                status = likeness_shadow.main([
                    "--run", str(ROOT), "--out", str(ROOT / "tmp" / "shadow-cap-test-not-created"),
                    "--max-candidates", "1", "--dry-run",
                ])
        self.assertEqual(status, 1)
        experiment.assert_not_called()

    def test_output_must_be_named_ignored_repo_tmp_not_a_library_path(self):
        with self.assertRaisesRegex(ValueError, "absolute"):
            likeness_shadow.output_path("relative")
        with self.assertRaisesRegex(ValueError, "inside repository tmp"):
            likeness_shadow.output_path(str(ROOT / "reports" / "experiment"))
        with self.assertRaisesRegex(ValueError, "not tmp itself"):
            likeness_shadow.output_path(str(ROOT / "tmp"))
        output = ROOT / "tmp" / "shadow-test-not-created"
        self.assertEqual(likeness_shadow.output_path(str(output)), output)
        self.assertFalse(output.exists())

    def test_check_refuses_output_corruption_or_different_parameters(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as name:
            path = pathlib.Path(name)
            (path / "scope.json").write_text("{}", encoding="utf-8")
            receipt = {"provenance": {}, "parameters": {},
                       "outputs": {"scope.json": shadow.digest(path / "scope.json")}}
            (path / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
            likeness_shadow.check(path, {}, {})
            with self.assertRaisesRegex(ValueError, "parameters changed"):
                likeness_shadow.check(path, {}, {"hops": 2})
            (path / "scope.json").write_text("edited", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from receipt"):
                likeness_shadow.check(path, {}, {})


if __name__ == "__main__":
    unittest.main()
