"""Saved SIMPLE reports preserve source accounting without rerunning the pipeline."""
import contextlib
import copy
import hashlib
import io
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

from tools.art.likeness_library import (
    actions, derivatives, metadata, normal_admission, normal_recap, normal_transaction, policy, rebase_recap,
)


ROOT = pathlib.Path(__file__).resolve().parents[4]


class NormalRecapTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="normal-recap-", dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name)
        self.library = self.root / "_reports" / "library"
        self.library.mkdir(parents=True)
        self.report = self.root / "_reports" / "runs" / "run.json"
        self.report.parent.mkdir()
        self.a = "Angels/Ava/gallery/ava_image_1.jpg"
        self.b = "Various/gallery/image_2.jpg"
        self.target = "Models/Bea/gallery/bea_image_2.jpg"
        self.held = "Various/review/image_3.jpg"
        self.h1 = hashlib.sha256(b"original1").hexdigest()
        self.h2 = hashlib.sha256(b"original2").hexdigest()
        self.h3 = hashlib.sha256(b"original3").hexdigest()
        self.native = hashlib.sha256(b"prepared2").hexdigest()
        for name in (self.a, self.target, self.held):
            path = self.root / pathlib.PurePosixPath(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"not read by report rendering")
        for name in ("people_gallery.html",):
            (self.library / name).write_text("<html></html>", encoding="utf-8")
        self.thumb = self.library / "people_gallery_review_files" / "thumb.jpg"
        self.thumb.parent.mkdir()
        self.thumb.write_bytes(b"existing thumbnail")
        sources = [
            {"source": self.a, "sourceHash": self.h1, "photoId": "photo:image_1"},
            {"source": self.b, "sourceHash": self.h2, "photoId": "photo:image_2"},
            {"source": self.target, "sourceHash": self.h2, "photoId": "photo:image_2"},
            {"source": self.held, "sourceHash": self.h3, "photoId": "photo:image_3"},
        ]
        move = {"source": self.b, "destination": self.target, "sha256": self.h2,
                "photoId": "photo:image_2", "reason": "qualified admission"}
        self.receipt = {
            "kind": "normal-rebase-receipt", "schemaVersion": 1, "status": "applied",
            "root": str(self.root), "runId": "run1", "profile": "lean",
            "moves": [move], "sourceHashes": {r["source"]: r["sourceHash"] for r in sources},
            "publishedNative": [{"native": self.target, "sha256": self.native}],
            "plan": {
                "sourceRows": sources, "sourceHashes": {r["source"]: r["sourceHash"] for r in sources},
                "moves": [move], "exactAliasTargets": {self.target: {"source": self.b, "sha256": self.h2}},
                "frozenConsistencyCheck": {"passCount": 1, "lowMemberChecks": [{}, {}],
                                          "recommendations": [{"photoId": "photo:image_1",
                                                               "reason": "protected recommendation only"}]},
            },
        }
        self.records = [self.record(self.a, "photo:image_1", self.h1),
                        self.record(self.target, "photo:image_2", self.native),
                        self.record(self.held, "photo:image_3", self.h3)]
        self.save()

    def record(self, path, identifier, checksum):
        person, bucket = rebase_recap.person_and_bucket(path)
        return {
            "folder": person, "bucket": bucket.title(), "name": pathlib.PurePosixPath(path).name,
            "photoId": identifier, "contentSha256": checksum, "score": .1,
            "scoreContext": {"coreMember": False}, "identityProtected": True,
            "workflowSelected": True, "identityAnchor": False, "reason": "saved explanation",
            "comparison": "saved own core", "closestMatches": [{"folder": "Sisters/Sia", "score": .7}],
            "thumbnail": "people_gallery_review_files/thumb.jpg",
        }

    def save(self):
        self.report.write_text(json.dumps(self.receipt), encoding="utf-8")
        self.review = self.library / "people_gallery_review.html"
        self.review.write_text('<html><script id="review-data" type="application/json">'
                               + json.dumps(self.records) + "</script></html>", encoding="utf-8")

    def run_report(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return rebase_recap.main([str(self.report), *args])

    def test_ordered_steps_show_measured_current_reuse_and_publication(self):
        names = [
            "source-inventory-and-sha256",
            "stable-id-normalization-and-version-selection",
            "accepted-profile-preparation",
            "source-bound-measurement-and-frozen-cores",
            "bounded-two-round-admission",
            "bound-admission-and-retained-member-check",
            "final-rival-family-viewer-publication",
        ]
        plan = self.receipt["plan"]
        plan["phaseLog"] = [
            {"phase": name, "status": "complete", "durationSeconds": index + .125}
            for index, name in enumerate(names)
        ]
        plan["phaseLog"][2]["timingScope"] = "current reuse verification"
        plan["phaseLog"][-1]["timingScope"] = "current transaction; excludes receipt and recap"
        plan.update(sourceRowCount=4, preparationInputCount=3, candidateCount=2,
                    assignedCount=1, heldCount=1, preparationReusedFromPreview=True)
        self.save()
        data = normal_recap.collect(self.report)
        page = normal_recap.render(data, self.library / "recap.html")
        summary = page[page.index("Ordered processing summary"):page.index("Processing step details")]
        self.assertEqual([summary.index(name) for name in names], sorted(summary.index(name) for name in names))
        self.assertLess(page.index("Ordered processing summary"), page.index("<h2 id=flows>"))
        self.assertIn("6.125 seconds measured", page)
        self.assertIn("current reuse verification", page)
        self.assertIn("Historical preparation was reused; its duration is not measured by this run", page)
        self.assertIn("preparationInputCount: 3", page)
        self.assertIn("published moves: 1", page)
        self.assertIn("excludes receipt and recap", page)

    def test_legacy_and_incomplete_steps_never_invent_duration_or_publication(self):
        self.receipt["plan"]["phaseLog"] = [
            {"phase": "accepted-profile-preparation", "status": "complete"},
            {"phase": "final-rival-family-viewer-publication", "status": "apply-only",
             "durationSeconds": 123},
        ]
        self.save()
        page = normal_recap.render(normal_recap.collect(self.report), self.library / "recap.html")
        self.assertIn("apply-only; duration unavailable", page)
        self.assertIn("applied receipt records publication", page)
        self.assertNotIn("123.000 seconds", page)
        self.assertNotIn("published moves", page)
        self.receipt["plan"]["phaseLog"][0]["durationSeconds"] = float("nan")
        self.save()
        page = normal_recap.render(normal_recap.collect(self.report), self.library / "recap.html")
        self.assertNotIn("nan seconds", page)
        self.receipt["plan"].pop("phaseLog")
        self.save()
        page = normal_recap.render(normal_recap.collect(self.report), self.library / "recap.html")
        self.assertIn("Phase records and timings unavailable", page)

    def test_fresh_selection_counts_and_timing_in_ordered_summary_and_detail(self):
        plan = self.receipt["plan"]
        plan["phaseLog"] = [
            {"phase": "fresh-source-measurement", "status": "complete", "durationSeconds": 1.},
            {"phase": "fresh-source-release-selection", "status": "complete", "durationSeconds": 2.125},
            {"phase": "fresh-post-release-frozen-cores", "status": "complete", "durationSeconds": 3.},
        ]
        plan.update(freshGalleryCount=30, freshSelectedCount=7, freshBlockedCount=0,
                    freshUnavailableCount=2, freshNonVotingCount=4)
        self.save()
        data = normal_recap.collect(self.report)
        page = normal_recap.render(data, self.library / "recap.html")
        summary = page[page.index("Ordered processing summary"):page.index("Processing step details")]
        detail = page[page.index("Processing step details"):page.index("<h2 id=flows>")]
        self.assertLess(summary.index("fresh-source-measurement"), summary.index("fresh-source-release-selection"))
        self.assertLess(summary.index("fresh-source-release-selection"), summary.index("fresh-post-release-frozen-cores"))
        for section in (summary, detail):
            self.assertIn("2.125 seconds measured", section)
            self.assertIn("freshSelectedCount: 7", section)
            self.assertIn("freshBlockedCount: 0", section)
            self.assertIn("freshUnavailableCount: 2", section)
        self.assertIn("assess initial Gallery own-core release", detail)
        del plan["freshBlockedCount"]
        plan["phaseLog"][1].pop("durationSeconds")
        self.save()
        page = normal_recap.render(normal_recap.collect(self.report), self.library / "recap.html")
        self.assertIn("freshBlockedCount: unavailable", page)
        self.assertIn("fresh-source-release-selection</a> — complete; duration unavailable", page)

    def test_red_diagnostic_cli_is_read_only_in_default_and_check_modes(self):
        from tools.art.likeness_library import red_release_diagnostic

        result = {
            "candidateCount": 1, "assignments": [], "workflowGaps": ["unidentified workflow selections"],
            "redRefreshCensus": {"affectedOwners": [], "checkedCount": 0, "newlyRed": [], "unavailable": []},
            "workflowReplacementProposals": [
                {"state": "proposed", "photoId": "photo:image_1",
                 "replacementPhotoId": "photo:image_4", "replacementScore": .7},
                {"state": "blocked", "photoId": "photo:image_2", "reason": "stale metadata"},
            ],
            "held": [{"photoId": "photo:image_1", "releaseBlocked": True, "reason": "workflow gap"}],
        }
        args = ["--root", str(self.root), "--receipt", str(self.report), "--report", "saved.html", "--cache", "cache.json"]
        with mock.patch.object(red_release_diagnostic.likeness.cw, "load_cfg", return_value={}), \
             mock.patch.object(red_release_diagnostic.policy, "load_policy", return_value={}), \
             mock.patch.object(red_release_diagnostic.normal_admission, "checked_red_release_diagnostic",
                               return_value=result) as checked:
            for extra in ([], ["--check"]):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(red_release_diagnostic.main(args + extra), 0)
                self.assertIn("does not approve or apply a release", output.getvalue())
                self.assertIn("blocked: 1", output.getvalue())
                self.assertIn("0 scores checked, 0 newly red among those checked", output.getvalue())
                self.assertIn("does not rebuild cores", output.getvalue())
                self.assertIn("photo:image_1 -> photo:image_4", output.getvalue())
                self.assertIn("stale metadata", output.getvalue())
            self.assertEqual(checked.call_count, 2)

    def test_red_diagnostic_simulation_keeps_blocked_results_and_labels_routes(self):
        from tools.art.likeness_library import red_release_diagnostic

        result = {
            "candidateCount": 1, "assignments": [],
            "redRefreshCensus": {"affectedOwners": [], "checkedCount": 0, "newlyRed": [], "unavailable": []},
            "workflowGaps": ["workflow not isolated"], "workflowReplacementProposals": [],
            "held": [{"photoId": "photo:image_1", "releaseBlocked": True, "reason": "workflow gap"}],
            "hypotheticalRouting": {"assignments": [],
                                    "held": [{"photoId": "photo:image_1", "sourceFolder": "Sisters/Owner",
                                              "reviewDestination": "Various/review", "reason": "unassigned"}]},
            "hypotheticalReviewCensus": {
                "affectedOwners": ["Sisters/Owner"], "checkedCount": 1,
                "newlyRed": [], "unavailable": [{"photoId": "photo:image_2", "owner": "Sisters/Owner",
                                                 "reason": "saved or rebuilt score unavailable"}],
            },
        }
        args = ["--root", str(self.root), "--receipt", str(self.report), "--report", "saved.html",
                "--cache", "cache.json", "--simulate-routes"]
        with mock.patch.object(red_release_diagnostic.likeness.cw, "load_cfg", return_value={}), \
             mock.patch.object(red_release_diagnostic.policy, "load_policy", return_value={}), \
             mock.patch.object(red_release_diagnostic.normal_admission, "checked_red_release_diagnostic",
                               return_value=result) as checked:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(red_release_diagnostic.main(args), 0)
            self.assertTrue(checked.call_args.kwargs["simulate_all"])
            self.assertIn("blocked: 1", output.getvalue())
            self.assertIn("HYPOTHETICAL ONLY", output.getvalue())
            self.assertIn("Sisters/Owner -> Various/review", output.getvalue())
            self.assertIn("not an executable preview", output.getvalue())
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(red_release_diagnostic.main(args + ["--simulate-core-refresh"]), 0)
            self.assertTrue(checked.call_args.kwargs["simulate_core_refresh"])
            self.assertIn("1 unmoved scores checked, 0 newly red, 1 unavailable", output.getvalue())
            self.assertIn("moved photos are not rescored", output.getvalue())
            self.assertIn("Hypothetical score unavailable: photo:image_2", output.getvalue())
            result["hypotheticalReviewCensus"]["movedScores"] = [
                {"photoId": "photo:image_1", "owner": "Angels/Target", "score": .12, "band": "red"},
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(red_release_diagnostic.main(
                    args + ["--simulate-core-refresh", "--simulate-destination-scores"],
                ), 0)
            self.assertTrue(checked.call_args.kwargs["simulate_destination_scores"])
            self.assertIn("Hypothetical destination score: photo:image_1 in Angels/Target: 0.12 (red)",
                          output.getvalue())
            self.assertIn("not an executable preview", output.getvalue())
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                red_release_diagnostic.main(args[:-1] + ["--simulate-core-refresh"])
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                red_release_diagnostic.main(args + ["--simulate-destination-scores"])

    def test_rebuilt_review_census_checks_inventory_and_native_bindings(self):
        bands = policy.load_policy()
        owner = "Angels/Ava"
        originals = (
            ("ava_image_1.jpg", b"red", [0., 1.], 0., False),
            ("ava_image_2.jpg", b"core two", [1., 0.], 1., True),
            ("ava_image_4.jpg", b"core four", [1., 0.], 1., True),
        )
        gallery = self.root / "Angels" / "Ava" / "gallery"
        gallery.mkdir(parents=True, exist_ok=True)
        (gallery / "ava_image_1.jpg").unlink()
        records, audit_records, vectors, measurements = [], [], {}, {}
        for name, payload, vector, score, core_member in originals:
            path = gallery / name
            path.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            photo_id = metadata.photo_id_from_name(name)
            relative = path.relative_to(self.root).as_posix()
            record = {
                "folder": owner, "bucket": "Gallery", "name": name, "photoId": photo_id,
                "contentSha256": digest, "score": score, "identityAnchor": False, "membershipExcluded": False,
                "scoreContext": {"coreMember": core_member, "coreSize": 2, "coreMode": "provisional",
                                 "usable": True, "minFace": 60},
                "state": "Core member" if core_member else "Review suggested",
            }
            records.append(record)
            audit_records.append({
                "record": record, "row": {"newPerson": owner, "newBucket": "gallery",
                                           "destination": relative, "photoId": photo_id},
                "score": score,
            })
            vectors[digest], measurements[digest] = np.asarray(vector), {"px": 100}
        self.review.write_text(
            '<script id="review-data" type="application/json">' + json.dumps(records)
            + '</script><script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script>", encoding="utf-8",
        )
        catalog_path = self.root / ".likeness-library.json"
        metadata.save_catalog({"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}, catalog_path)
        cache = self.root / "cache.json"
        cache.write_bytes(b"cache")
        cache_hash = metadata.content_sha256(cache)
        review_hash = metadata.content_sha256(self.review)
        data = {
            "snapshotDiagnostics": [], "snapshotIdUnavailable": 0, "libraryRoot": str(self.library),
            "inputs": {str(self.review): review_hash}, "auditRecords": audit_records,
        }
        snapshot = {
            "snapshotCandidates": [{"photoId": "photo:image_1", "owner": owner, "bucket": "gallery",
                                    "nativeSha256": hashlib.sha256(b"red").hexdigest(), "score": 0.,
                                    "currentPath": "Angels/Ava/gallery/ava_image_1.jpg"}],
            "inputBindings": data["inputs"],
        }
        inventory = {"catalogSHA256": metadata.content_sha256(catalog_path),
                     "cacheSHA256": cache_hash, "modelIds": ["model"],
                     "nativeBindings": {item["row"]["destination"]: item["record"]["contentSha256"]
                                        for item in audit_records}}
        routing = {"assignments": [], "held": [{"photoId": "photo:image_1",
                                               "reviewDestination": "Various/review"}]}
        args = (self.root, self.report, cache, {}, bands, snapshot, inventory, routing)
        with mock.patch.object(normal_recap, "collect", return_value=data), \
             mock.patch.object(normal_admission, "_red_cache_vectors",
                               return_value=(cache, cache_hash, vectors, {"model"}, measurements)):
            result = normal_admission.verified_rebuilt_red_review_census(*args)
            self.assertEqual(result["checkedCount"], 2)
            self.assertEqual(result["newlyRed"], [])
            (gallery / "ava_image_1.jpg").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "native changed"):
                normal_admission.verified_rebuilt_red_review_census(*args)
            (gallery / "ava_image_1.jpg").write_bytes(b"red")
            (gallery / "unexpected.jpg").write_bytes(b"new")
            with self.assertRaisesRegex(ValueError, "inventory changed"):
                normal_admission.verified_rebuilt_red_review_census(*args)
            (gallery / "unexpected.jpg").unlink()
            inventory["nativeBindings"]["Prospects/Other/gallery/alias.jpg"] = hashlib.sha256(b"red").hexdigest()
            with self.assertRaisesRegex(ValueError, "surviving Gallery content alias"):
                normal_admission.verified_rebuilt_red_review_census(*args)
            del inventory["nativeBindings"]["Prospects/Other/gallery/alias.jpg"]
            routing["held"].clear()
            with self.assertRaisesRegex(ValueError, "does not conserve"):
                normal_admission.verified_rebuilt_red_review_census(*args)

    def test_red_consumer_inventory_includes_unconfigured_local_installations(self):
        from tools.art.likeness_library import red_release_diagnostic

        installs = self.root / "installs"
        workflows = installs / "Extra" / "ComfyUI" / "user" / "default" / "workflows"
        workflows.mkdir(parents=True)
        (workflows / "manual.json").write_text('{"image":"image_123.png"}', encoding="utf-8")
        (installs / "Unrelated").mkdir()
        cfg = {"workspaces": {"Known": {}}, "workflowsSubpath": r"ComfyUI\user\default\workflows"}
        with mock.patch.object(red_release_diagnostic.likeness.cw, "installs_root", return_value=installs):
            scopes = red_release_diagnostic.workspace_consumer_scopes(cfg)
            self.assertEqual(set(scopes), {"workspace:Known", "unconfigured-workspace:Extra"})
            result = red_release_diagnostic.inspect_consumers(scopes, ["photo:image_123"])
            with mock.patch.object(
                red_release_diagnostic.likeness.cw, "is_reparse_point",
                side_effect=lambda path: path == installs / "Extra",
            ):
                with self.assertRaisesRegex(ValueError, "linked installation"):
                    red_release_diagnostic.workspace_consumer_scopes(cfg)
        self.assertEqual(result["matches"][0]["scope"], "unconfigured-workspace:Extra")
        self.assertEqual(result["unavailable"][0]["scope"], "workspace:Known")
        self.assertFalse(result["consumerCoverageVerified"])

    def test_red_consumer_inventory_preserves_duplicate_and_nested_references(self):
        from tools.art.likeness_library import red_release_diagnostic

        repo = self.root / "workflows"
        repo.mkdir()
        workspace = self.root / "workspace"
        workspace.mkdir()
        for path, data in (
            (repo / "first" / "same.json", {"nested": [{"class_type": "LoadImage",
                                                       "inputs": {"image": "foo_image_123.png"}}]}),
            (repo / "second" / "same.json", {"note": "image_123 is referenced manually"}),
            (repo / "workspaces.json", {"photos": {"Owner": "foo_image_123.png"}}),
            (workspace / "array.json", [{"image": "image_123.png"}]),
            (repo / "_archive" / "ignored.json", {"image": "image_123.png"}),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data), encoding="utf-8")
        result = red_release_diagnostic.inspect_consumers(
            {"repo": repo, "workspace": workspace, "offline": self.root / "missing"},
            ["photo:image_123"],
        )
        self.assertEqual(result["files"], 4)
        self.assertEqual(len(result["matches"]), 4)
        self.assertEqual(len(result["unavailable"]), 1)
        self.assertFalse(result["consumerCoverageVerified"])
        self.assertEqual(len(result["fileHashes"]), 4)
        proposal = {
            "state": "proposed", "photoId": "photo:image_123",
            "beforeDerivative": str(self.root / "foo_image_123.png"),
            "afterDerivative": str(self.root / "foo_image_456.png"),
            "selectionChanges": [{"hero": "Owner", "flow": None, "before": "foo_image_123.png",
                                  "after": "foo_image_456.png"}],
        }
        config = repo / "workspaces.json"
        plans = red_release_diagnostic.plan_consumer_retargets(result, [proposal], config)
        self.assertEqual(len(plans["plans"]), 2)
        self.assertEqual(len(plans["blocked"]), 2)
        self.assertTrue(any(row["kind"] == "configuration" for row in plans["plans"]))
        config_plan = next(row for row in plans["plans"] if row["kind"] == "configuration")
        self.assertEqual(json.loads(config_plan["afterBytes"])["photos"]["Owner"], "foo_image_456.png")
        self.assertEqual(json.loads(config.read_text(encoding="utf-8"))["photos"]["Owner"], "foo_image_123.png")
        without_config = {**result, "matches": [row for row in result["matches"] if row["path"] != str(config)]}
        missing_config = red_release_diagnostic.plan_consumer_retargets(without_config, [proposal], config)
        self.assertTrue(any("configuration is missing" in row["reason"] for row in missing_config["blocked"]))
        ambiguous = {
            **proposal, "selectionChanges": proposal["selectionChanges"] + [
                {"hero": "Owner", "flow": "portrait", "before": "foo_image_123.png", "after": "foo_image_456.png"},
            ],
        }
        plans_with_missing_flow = red_release_diagnostic.plan_consumer_retargets(result, [ambiguous], config)
        self.assertTrue(any("configuration has an unclassified" in row["reason"]
                            for row in plans_with_missing_flow["blocked"]))
        planned = next(row for row in plans["plans"] if row["kind"] == "workflow")
        self.assertEqual(json.loads(planned["afterBytes"])["nested"][0]["inputs"]["image"], "foo_image_456.png")
        original = pathlib.Path(planned["path"])
        self.assertEqual(json.loads(original.read_text(encoding="utf-8"))["nested"][0]["inputs"]["image"],
                         "foo_image_123.png")
        original.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed before retarget planning"):
            red_release_diagnostic.plan_consumer_retargets(result, [proposal], config)
        with mock.patch.object(red_release_diagnostic, "MAX_CONSUMER_BYTES", 10):
            with self.assertRaisesRegex(ValueError, "exceeds 512 MiB"):
                red_release_diagnostic.inspect_consumers({"repo": repo}, ["photo:image_123"])
        (workspace / "bad.json").write_text("{", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            red_release_diagnostic.inspect_consumers({"workspace": workspace}, ["photo:image_123"])

    def test_unidentified_inputs_report_exact_red_bytes_without_claiming_coverage(self):
        from tools.art.likeness_library import red_release_diagnostic

        inputs = self.root / "inputs"
        inputs.mkdir()
        (inputs / "legacy.png").write_bytes(b"red derivative")
        (inputs / "native.png").write_bytes(b"red native")
        (inputs / "unrelated.png").write_bytes(b"different")
        (inputs / "unregistered").mkdir()
        (inputs / "unregistered" / "legacy.png").write_bytes(b"red derivative")
        cfg = {"photos": {"A": "legacy.png", "B": "unrelated.png", "C": "missing.png",
                          "D": "known_image_123.png", "E": "native.png"},
               "workspaces": {"one": {}, "offline": {}}}
        candidates = [{"photoId": "photo:image_1", "sha256": hashlib.sha256(b"red native").hexdigest()}]
        proposals = [{"state": "proposed", "photoId": "photo:image_1",
                      "beforeDerivativeSHA256": hashlib.sha256(b"red derivative").hexdigest()}]
        with mock.patch.object(red_release_diagnostic.likeness.cw, "shared_input_root", return_value=inputs), \
             mock.patch.object(red_release_diagnostic.likeness.cw, "comfy_input_root", return_value=inputs), \
             mock.patch.object(red_release_diagnostic.likeness.cw, "input_dir",
                               side_effect=lambda cfg, ws: inputs if ws == "one" else self.root / "offline"):
            result = red_release_diagnostic.inspect_unidentified_inputs(cfg, candidates, proposals)
            self.assertEqual(result["checkedFiles"], 4)
            self.assertEqual({match["photoId"] for match in result["exactMatches"]}, {"photo:image_1"})
            self.assertEqual({pathlib.Path(match["path"]).name for match in result["exactMatches"]},
                             {"legacy.png", "native.png"})
            self.assertEqual(len(result["exactMatches"]), 5)
            self.assertTrue(any(match["scope"] == "unconfigured-input:unregistered"
                                for match in result["exactMatches"]))
            self.assertTrue(any(row["reason"] == "input root unavailable" for row in result["missing"]))
            self.assertTrue(any(row["reason"] == "configured input missing" for row in result["missing"]))
            self.assertFalse(result["consumerCoverageVerified"])
            cfg["photos"]["A"] = "..\\escape.png"
            with self.assertRaisesRegex(ValueError, "simple input filename"):
                red_release_diagnostic.inspect_unidentified_inputs(cfg, candidates, proposals)

    def test_unidentified_input_inventory_refuses_new_workspace_during_scan(self):
        from tools.art.likeness_library import red_release_diagnostic

        inputs = self.root / "inputs"
        inputs.mkdir()
        (inputs / "legacy.png").write_bytes(b"selected input")
        cfg = {"photos": {"A": "legacy.png"}, "workspaces": {}}
        original_hash = metadata.content_sha256

        def add_input_root(path):
            (inputs / "appeared").mkdir(exist_ok=True)
            return original_hash(path)

        with mock.patch.object(red_release_diagnostic.likeness.cw, "shared_input_root", return_value=inputs), \
             mock.patch.object(red_release_diagnostic.likeness.cw, "comfy_input_root", return_value=inputs), \
             mock.patch.object(red_release_diagnostic.actions.metadata, "content_sha256",
                               side_effect=add_input_root):
            with self.assertRaisesRegex(ValueError, "input inventory changed"):
                red_release_diagnostic.inspect_unidentified_inputs(cfg, [], [])

    def test_red_retarget_plans_base_and_flow_selections_together(self):
        from tools.art.likeness_library import red_release_diagnostic

        config = self.root / "workspaces.json"
        original = {"photos": {"Owner": "foo_image_123.png", "Other": "untouched.png"},
                    "flows": {"portrait": {"photos": {"Owner": "foo_image_123.png"}}}}
        config.write_text(json.dumps(original), encoding="utf-8")
        proposal = {
            "state": "proposed", "photoId": "photo:image_123",
            "beforeDerivative": str(self.root / "foo_image_123.png"),
            "afterDerivative": str(self.root / "foo_image_456.png"),
            "selectionChanges": [
                {"hero": "Owner", "flow": None, "before": "foo_image_123.png", "after": "foo_image_456.png"},
                {"hero": "Owner", "flow": "portrait", "before": "foo_image_123.png", "after": "foo_image_456.png"},
            ],
        }
        inventory = red_release_diagnostic.inspect_consumers({"repo": self.root}, ["photo:image_123"])
        result = red_release_diagnostic.plan_consumer_retargets(inventory, [proposal], config)
        self.assertFalse(result["blocked"])
        planned = json.loads(result["plans"][0]["afterBytes"])
        self.assertEqual(planned["photos"]["Owner"], "foo_image_456.png")
        self.assertEqual(planned["flows"]["portrait"]["photos"]["Owner"], "foo_image_456.png")
        self.assertEqual(planned["photos"]["Other"], "untouched.png")
        self.assertEqual(json.loads(config.read_text(encoding="utf-8")), original)
        proposal["selectionChanges"][1]["after"] = "wrong_image_999.png"
        self.assertTrue(red_release_diagnostic.plan_consumer_retargets(inventory, [proposal], config)["blocked"])

    def test_unidentified_input_inventory_refuses_changed_bytes(self):
        from tools.art.likeness_library import red_release_diagnostic

        inputs = self.root / "inputs"
        inputs.mkdir()
        (inputs / "legacy.png").write_bytes(b"before")
        cfg = {"photos": {"A": "legacy.png"}, "workspaces": {}}
        with mock.patch.object(red_release_diagnostic.likeness.cw, "shared_input_root", return_value=inputs), \
             mock.patch.object(red_release_diagnostic.likeness.cw, "comfy_input_root", return_value=inputs), \
             mock.patch.object(red_release_diagnostic.actions.metadata, "content_sha256",
                               side_effect=["before", "after"]):
            with self.assertRaisesRegex(ValueError, "changed during inspection"):
                red_release_diagnostic.inspect_unidentified_inputs(cfg, [], [])

    def test_nonvoting_gallery_is_bound_to_saved_disposition_and_current_bytes(self):
        source = self.root / pathlib.PurePosixPath(self.a)
        source.write_bytes(b"original1")
        self.receipt["plan"]["sourceRows"][0]["sourceStatus"] = "same-content-nonvoting"
        self.save()
        manifest = {"inputs": {str(self.report): hashlib.sha256(self.report.read_bytes()).hexdigest()}}
        with mock.patch.object(normal_recap, "publish", return_value=manifest):
            bindings = normal_admission.verified_red_nonvoting_gallery(self.report, self.library / "out.html", self.root)
            self.assertEqual(bindings, {self.a: self.h1})
            source.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "non-voting Gallery native changed"):
                normal_admission.verified_red_nonvoting_gallery(self.report, self.library / "out.html", self.root)
            source.write_bytes(b"original1")
            self.report.write_text(self.report.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "receipt changed"):
                normal_admission.verified_red_nonvoting_gallery(self.report, self.library / "out.html", self.root)

    def test_nonvoting_gallery_refuses_unchecked_report_and_wrong_root(self):
        source = self.root / pathlib.PurePosixPath(self.a)
        source.write_bytes(b"original1")
        self.receipt["plan"]["sourceRows"][0]["sourceStatus"] = "same-content-nonvoting"
        self.save()
        with mock.patch.object(normal_recap, "publish", side_effect=ValueError("report input mismatch")):
            with self.assertRaisesRegex(ValueError, "report input mismatch"):
                normal_admission.verified_red_nonvoting_gallery(self.report, self.library / "out.html", self.root)
        manifest = {"inputs": {str(self.report): hashlib.sha256(self.report.read_bytes()).hexdigest()}}
        with mock.patch.object(normal_recap, "publish", return_value=manifest):
            with self.assertRaisesRegex(ValueError, "applied receipt for this library"):
                normal_admission.verified_red_nonvoting_gallery(
                    self.report, self.library / "out.html", self.root / "other",
                )
            data = normal_recap.collect(self.report)
            for field, value in (("destination", self.target), ("preparedSHA256", self.native)):
                altered = copy.deepcopy(data)
                next(row for row in altered["rows"] if row["source"] == self.a)[field] = value
                with self.subTest(field=field), mock.patch.object(normal_recap, "collect", return_value=altered):
                    with self.assertRaisesRegex(ValueError, "disposition changed"):
                        normal_admission.verified_red_nonvoting_gallery(
                            self.report, self.library / "out.html", self.root,
                        )

    def test_centering_population_reconstructs_bound_preparation_and_refuses_drift(self):
        cfg, rules = {}, policy.load_policy()

        def digest_json(value):
            return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

        model = {
            "detector": {"name": "YuNet", "file": "face_detection_yunet_2023mar.onnx", "sha256": "1" * 64},
            "recognizer": {"name": "SFace", "file": "face_recognition_sface_2021dec.onnx", "sha256": "2" * 64},
            "opencv": "fixture", "alignment": "FaceRecognizerSF.alignCrop",
        }
        prepared = self.root / "prepared"
        prepared.mkdir()
        rows, measurements = [], {}
        for name, payload, vector in (("one.jpg", b"one", [1., 0.]), ("two.jpg", b"two", [0., 1.])):
            (prepared / name).write_bytes(payload)
            sha256 = hashlib.sha256(payload).hexdigest()
            rows.append({"source": name, "sourceSha256": sha256, "retained": name})
            measurements[hashlib.sha1(payload).hexdigest()] = {
                "v": vector, "faces": 1, "px": 1000, "f2": 0.,
                "alignmentEvidence": {
                    "state": "persisted", "sourceSha256": sha256, "model": model,
                    "modelId": digest_json(model),
                },
            }
        manifest_path = prepared / "manifest.json"
        manifest_path.write_text(json.dumps({"photos": rows}), encoding="utf-8")
        receipt = {
            "status": "applied", "root": str(self.root), "profile": "lean",
            "plan": {
                "bindings": {"configurationSHA256": digest_json(cfg), "policySHA256": digest_json(rules)},
                "preparationRoot": str(prepared),
                "preparationManifestSHA256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                "sourceRows": [
                    {"source": row["source"], "sourceHash": row["sourceSha256"], "sourceStatus": "eligible"}
                    for row in rows
                ],
            },
        }
        self.report.write_text(json.dumps(receipt), encoding="utf-8")
        cache_path = self.root / "cache.json"
        cache = {"centeringDomain": "general", "centeringMean": [.5, .5], "emb": measurements}
        cache_path.write_text(json.dumps(cache), encoding="utf-8")

        def checked_report(*_args, **_kwargs):
            return {"inputs": {str(self.report): hashlib.sha256(self.report.read_bytes()).hexdigest()}}

        args = (self.report, self.library / "out.html", self.root, cache_path, cfg, rules)
        with mock.patch.object(normal_recap, "publish", side_effect=checked_report):
            result = normal_admission.verify_red_centering_population(*args)
            self.assertEqual((result["activeCount"], result["usableCount"]), (2, 2))
            self.assertTrue(result["centeringPopulationVerified"])
            cache["centeringMean"] = [.4, .5]
            cache_path.write_text(json.dumps(cache), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from the reconstructed population"):
                normal_admission.verify_red_centering_population(*args)
            cache["centeringMean"] = [.5, .5]
            cache_path.write_text(json.dumps(cache), encoding="utf-8")
            (prepared / "one.jpg").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "selected preparation bytes changed"):
                normal_admission.verify_red_centering_population(*args)
            (prepared / "one.jpg").write_bytes(b"one")
            measurements[hashlib.sha1(b"one").hexdigest()]["alignmentEvidence"]["sourceSha256"] = "0" * 64
            cache_path.write_text(json.dumps(cache), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not content-bound"):
                normal_admission.verify_red_centering_population(*args)
            measurements[hashlib.sha1(b"one").hexdigest()]["alignmentEvidence"]["sourceSha256"] = rows[0]["sourceSha256"]
            cache_path.write_text(json.dumps(cache), encoding="utf-8")
            receipt["plan"]["sourceRows"].pop()
            self.report.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not match the saved active sources"):
                normal_admission.verify_red_centering_population(*args)
            receipt["plan"]["sourceRows"].append({
                "source": rows[1]["source"], "sourceHash": rows[1]["sourceSha256"], "sourceStatus": "eligible",
            })
            receipt["plan"]["sourceRows"][0]["sourceStatus"] = "held"
            self.report.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "disposition is not supported"):
                normal_admission.verify_red_centering_population(*args)

    def test_workflow_replacement_proposal_requires_reproducible_scores_and_owned_derivatives(self):
        root = self.root
        folder = root / "Angels" / "Ava" / "gallery"
        red = folder / "ava_image_1.jpg"
        sources = {
            "photo:image_1": (red, b"red", [0., 1., 0.]),
            "photo:image_4": (folder / "ava_image_4.jpg", b"first", [1., 0., 0.]),
            "photo:image_5": (folder / "ava_image_5.jpg", b"core", [1., 0., 0.]),
            "photo:image_6": (folder / "ava_image_6.jpg", b"second", [.8, 0., .6]),
        }
        model = {
            "detector": {"name": "YuNet", "file": "face_detection_yunet_2023mar.onnx", "sha256": "1" * 64},
            "recognizer": {"name": "SFace", "file": "face_recognition_sface_2021dec.onnx", "sha256": "2" * 64},
            "opencv": "fixture", "alignment": "FaceRecognizerSF.alignCrop",
        }
        model_id = hashlib.sha256(json.dumps(model, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        measurements, rows = {}, {}
        for photo_id, (path, payload, vector) in sources.items():
            path.write_bytes(payload)
            checksum = hashlib.sha256(payload).hexdigest()
            rows[photo_id] = {"photoId": photo_id, "currentPath": path.relative_to(root).as_posix(),
                              "nativeSha256": checksum}
            measurements[hashlib.sha1(payload).hexdigest()] = {
                "v": vector, "faces": 1, "px": 1000, "f2": 0.,
                "alignmentEvidence": {
                    "state": "persisted", "sourceSha256": checksum, "model": model, "modelId": model_id,
                },
            }
        core = [{"photoId": pid, "path": rows[pid]["currentPath"], "sha256": rows[pid]["nativeSha256"]}
                for pid in ("photo:image_4", "photo:image_5")]
        candidate = {
            **rows["photo:image_1"], "owner": "Angels/Ava", "bucket": "gallery", "score": 0.,
            "scoreContext": {"coreSize": 2, "coreMember": False}, "reviewCore": core,
            "workflowReplacementCandidates": [
                {**rows["photo:image_4"], "score": 1., "scoreContext": {"coreSize": 2, "coreMember": True}},
                {**rows["photo:image_6"], "score": .8, "scoreContext": {"coreSize": 2, "coreMember": False}},
            ],
        }
        cache = root / "cache.json"
        cache.write_text(json.dumps({"centeringDomain": "general", "centeringMean": [0., 0., 0.],
                                     "emb": measurements}), encoding="utf-8")
        (root / ".likeness-library.json").write_text("{}", encoding="utf-8")
        derivative_dir = root / "derivatives"
        derivative_dir.mkdir()
        before, after = derivative_dir / "ava_image_1_944x1104.png", derivative_dir / "ava_image_4_944x1104.png"
        before.write_bytes(b"old scaled")
        after.write_bytes(b"new scaled")
        derivative_manifest = derivatives.manifest_path(folder.parent)
        derivative_manifest.parent.mkdir(parents=True)
        derivative_manifest.write_text("{}", encoding="utf-8")
        cfg = {"photos": {"Ava": before.name}}

        def verified(path, framing):
            self.assertEqual(framing, "padded")
            derivative = before if path == red else after
            return derivative, {"sha256": hashlib.sha256(derivative.read_bytes()).hexdigest()}

        args = (root, cache, candidate, cfg, policy.load_policy())
        with mock.patch.object(normal_admission.metadata, "load_catalog", return_value={"photos": {}, "people": {}}), \
             mock.patch.object(derivatives, "verified", side_effect=verified):
            result = normal_admission.red_workflow_replacement_proposal(*args, retired_ids={"photo:image_1"})
            self.assertEqual(result["replacementPhotoId"], "photo:image_4")
            self.assertEqual(result["replacementScore"], 1.)
            self.assertTrue(result["planningOnly"])
            self.assertFalse(result["consumerCoverageVerified"])
            with self.assertRaisesRegex(ValueError, "newly scored core"):
                normal_admission.red_workflow_replacement_proposal(
                    *args, retired_ids={"photo:image_1", "photo:image_5"},
                )
            candidate["workflowReplacementCandidates"][0]["score"] = .9
            with self.assertRaisesRegex(ValueError, "does not reproduce"):
                normal_admission.red_workflow_replacement_proposal(*args, retired_ids={"photo:image_1"})
            candidate["workflowReplacementCandidates"][0]["score"] = 1.
            sources["photo:image_4"][0].write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "changed or ambiguous"):
                normal_admission.red_workflow_replacement_proposal(*args, retired_ids={"photo:image_1"})

    def test_red_candidates_use_snapshot_policy_and_unrounded_own_scores(self):
        bands = copy.deepcopy(policy.load_policy())
        bands["scoreBands"]["red"]["maximumExclusive"] = .2
        bands["scoreBands"]["orange"]["minimum"] = .2
        self.records[0]["score"] = .199999
        self.records[0]["photoProtectionInfo"] = "Explicitly protected"
        self.records[1]["score"] = .2
        self.records[2]["score"] = None
        self.receipt["plan"]["referenceSnapshots"] = {
            "1": {"referenceVersion": "first-version", "photoIds": {"Angels/Ava": ["photo:image_1"]}},
            "2": {"referenceVersion": "second-version", "photoIds": {"Angels/Ava": []}},
        }
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")

        data = normal_recap.collect(self.report)
        self.assertEqual(data["redScoreCount"], 1)
        self.assertEqual(data["unscoredCount"], 1)
        self.assertEqual(data["redScoreCutoff"], .2)
        self.assertIn("red own-core similarity", data["auditRecords"][0]["flags"])
        self.assertNotIn("red own-core similarity", data["auditRecords"][1]["flags"])
        self.assertNotIn("red own-core similarity", data["auditRecords"][2]["flags"])
        audit = normal_recap.render(data, self.library / "recap-audit.html", audit=True)
        self.assertIn("1 red own-core score", audit)
        self.assertIn("1 unscored", audit)
        self.assertIn("0.2", audit)
        self.assertIn("Unrounded: 0.199999", audit)
        self.assertIn("Receipt source: " + self.a, audit)
        self.assertIn("Recorded native SHA-256: " + self.h1, audit)
        self.assertIn("This saved audit does not propose or apply a release destination", audit)
        self.assertIn("photo protection: Explicitly protected", audit)
        self.assertIn("not the separate Artist domain", audit)
        self.assertIn("Round 1 (first-version): Angels/Ava", audit)
        self.assertIn("Round 2 (second-version): not listed", audit)

    def test_missing_snapshot_policy_does_not_infer_red_scores(self):
        data = normal_recap.collect(self.report)
        self.assertIsNone(data["redScoreCutoff"])
        self.assertIsNone(data["redScoreCount"])
        self.assertFalse(any("red own-core similarity" in item["flags"] for item in data["auditRecords"]))
        audit = normal_recap.render(data, self.library / "recap-audit.html", audit=True)
        self.assertIn("red score band unavailable", audit)

    def test_red_audit_discloses_incomplete_matched_review_core(self):
        bands = policy.load_policy()
        self.records[0]["scoreContext"]["coreSize"] = 2
        path = "Angels/Ava/gallery/ava_image_4.jpg"
        digest = hashlib.sha256(path.encode()).hexdigest()
        source = {"source": path, "sourceHash": digest, "photoId": "photo:image_4"}
        self.receipt["plan"]["sourceRows"].append(source)
        self.receipt["plan"]["sourceHashes"][path] = digest
        self.receipt["sourceHashes"][path] = digest
        member = self.record(path, "photo:image_4", digest)
        member["scoreContext"]["coreMember"] = True
        member["score"] = .5
        self.records.append(member)
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        audit = normal_recap.render(normal_recap.collect(self.report), self.library / "recap-audit.html", audit=True)
        self.assertIn("Saved Review core: 1 matched of 2 reported", audit)
        self.assertIn(path + " / photo:image_4 / recorded SHA-256: " + digest, audit)
        self.assertIn("current bytes and reference eligibility were not verified", audit)

    def test_opt_in_red_native_binding_refuses_changed_photo_or_missing_core(self):
        bands = policy.load_policy()
        self.records[0]["scoreContext"]["coreSize"] = 1
        self.records[1]["score"] = .5
        self.records[2]["score"] = .5
        path = "Angels/Ava/gallery/ava_image_4.jpg"
        payload = b"core native"
        digest = hashlib.sha256(payload).hexdigest()
        source = {"source": path, "sourceHash": digest, "photoId": "photo:image_4"}
        self.receipt["plan"]["sourceRows"].append(source)
        self.receipt["plan"]["sourceHashes"][path] = digest
        self.receipt["sourceHashes"][path] = digest
        member = self.record(path, "photo:image_4", digest)
        member["scoreContext"]["coreMember"] = True
        member["score"] = .5
        self.records.append(member)
        replacement_path = "Angels/Ava/gallery/ava_image_5.jpg"
        replacement_payload = b"replacement native"
        replacement_hash = hashlib.sha256(replacement_payload).hexdigest()
        replacement_source = {
            "source": replacement_path, "sourceHash": replacement_hash, "photoId": "photo:image_5",
        }
        self.receipt["plan"]["sourceRows"].append(replacement_source)
        self.receipt["plan"]["sourceHashes"][replacement_path] = replacement_hash
        self.receipt["sourceHashes"][replacement_path] = replacement_hash
        replacement = self.record(replacement_path, "photo:image_5", replacement_hash)
        replacement["score"] = .6
        replacement["workflowSelected"] = False
        self.records.append(replacement)
        (self.root / pathlib.PurePosixPath(self.a)).write_bytes(b"original1")
        (self.root / pathlib.PurePosixPath(path)).write_bytes(payload)
        (self.root / pathlib.PurePosixPath(replacement_path)).write_bytes(replacement_payload)
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        out = self.library / "bound.html"
        manifest = normal_recap.publish(self.report, out=out, apply=True, bind_red_natives=True)
        self.assertEqual(manifest["redNativeBindings"], 3)
        candidate, = manifest["redCandidates"]
        self.assertEqual(candidate["photoId"], "photo:image_1")
        self.assertEqual(candidate["currentPath"], self.a)
        self.assertEqual(candidate["nativeSha256"], self.h1)
        self.assertEqual(candidate["score"], .1)
        self.assertEqual(candidate["reviewCore"], [{"photoId": "photo:image_4", "path": path, "sha256": digest}])
        self.assertEqual(candidate["workflowReplacementCandidates"], [
            {"photoId": "photo:image_5", "currentPath": replacement_path,
             "nativeSha256": replacement_hash, "score": .6, "scoreContext": {"coreMember": False}},
            {"photoId": "photo:image_4", "currentPath": path,
             "nativeSha256": digest, "score": .5, "scoreContext": {"coreMember": True}},
        ])
        normal_recap.publish(self.report, out=out, check=True, bind_red_natives=True)
        (self.root / pathlib.PurePosixPath(replacement_path)).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "current native differs"):
            normal_recap.publish(self.report, out=out, check=True, bind_red_natives=True)
        (self.root / pathlib.PurePosixPath(replacement_path)).write_bytes(replacement_payload)
        (self.root / pathlib.PurePosixPath(path)).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "current native differs"):
            normal_recap.publish(self.report, out=out, check=True, bind_red_natives=True)
        member["scoreContext"]["coreMember"] = False
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "incomplete Review core"):
            normal_recap.publish(self.report, out=out, bind_red_natives=True)
        member["scoreContext"]["coreMember"] = True
        self.records[0]["photoId"] = None
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unbound Review photo ID"):
            normal_recap.publish(self.report, out=out, bind_red_natives=True)

    def test_workflow_selection_audit_binds_config_but_does_not_claim_consumers(self):
        bands = policy.load_policy()
        self.records[1]["score"] = .5
        self.records[2]["score"] = .5
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        cfg = {
            "photos": {"Ava": "ava_image_1_944x1104.png", "Other": "unknown.png"},
            "flows": {"portrait": {"photos": {"Ava": "ava_image_1_944x1104.png"}}},
        }
        config_path = self.root / "workspaces.json"
        schema_path = self.root / "workspaces.schema.json"
        config_path.write_text(json.dumps(cfg), encoding="utf-8")
        schema_path.write_text("{}", encoding="utf-8")
        out = self.library / "workflow.html"
        with mock.patch.object(actions.cw, "CFG_PATH", config_path), \
             mock.patch.object(actions.cw, "CFG_SCHEMA_PATH", schema_path), \
             mock.patch.object(actions.cw, "validate_config", side_effect=lambda value: value), \
             mock.patch.object(actions.cw, "work_root", return_value=self.root / "production"):
            manifest = normal_recap.publish(self.report, out=out, apply=True, inspect_workflow_selections=True)
            self.assertIn(str(config_path), manifest["inputs"])
            audit = out.with_name("workflow-audit.html").read_text(encoding="utf-8")
            self.assertIn("does not match this receipt root", audit)
            self.assertIn("1 selection(s) have no identifiable photo ID", audit)
            self.assertIn("base / Ava / ava_image_1_944x1104.png", audit)
            self.assertIn("flow portrait / Ava / ava_image_1_944x1104.png", audit)
            self.assertIn("not the actual workflow files or workspace consumers", audit)
            normal_recap.publish(self.report, out=out, check=True, inspect_workflow_selections=True)
            cfg["photos"]["Ava"] = "ava_image_999_944x1104.png"
            config_path.write_text(json.dumps(cfg), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bindings are missing or stale"):
                normal_recap.publish(self.report, out=out, check=True, inspect_workflow_selections=True)

    def test_workflow_selection_audit_can_bind_alternate_config_without_changing_default(self):
        default = self.root / "workspaces.json"
        alternate = self.root / "sandbox-workspaces.json"
        schema = self.root / "workspaces.schema.json"
        default_bytes = b'{"photos":{"Ava":"ava_image_1.png"}}'
        default.write_bytes(default_bytes)
        alternate.write_text('{"photos":{"Ava":"ava_image_2.png"}}', encoding="utf-8")
        schema.write_text("{}", encoding="utf-8")
        out = self.library / "alternate-workflow.html"
        with mock.patch.object(actions.cw, "CFG_PATH", default), \
             mock.patch.object(actions.cw, "CFG_SCHEMA_PATH", schema), \
             mock.patch.object(actions.cw, "validate_config", side_effect=lambda value: value), \
             mock.patch.object(actions.cw, "work_root", return_value=self.root / "production"):
            with self.assertRaisesRegex(ValueError, "requires workflow selection inspection"):
                normal_recap.publish(self.report, out=out, workflow_configuration_path=alternate)
            manifest = normal_recap.publish(
                self.report, out=out, apply=True, inspect_workflow_selections=True,
                workflow_configuration_path=alternate,
            )
            self.assertIn(str(alternate), manifest["inputs"])
            self.assertNotIn(str(default), manifest["inputs"])
            self.assertEqual(default.read_bytes(), default_bytes)
            data = normal_recap.collect(self.report)
            normal_recap._attach_workflow_selection_bindings(data, configuration_path=alternate)
            self.assertEqual(data["workflowConfig"]["bindings"][0]["filename"], "ava_image_2.png")
            audit = out.with_name("alternate-workflow-audit.html").read_text(encoding="utf-8")
            self.assertIn(str(alternate), audit)
            self.assertIn("not the actual workflow files or workspace consumers", audit)
            normal_recap.publish(
                self.report, out=out, check=True, inspect_workflow_selections=True,
                workflow_configuration_path=alternate,
            )
            alternate.write_text('{"photos":{"Ava":"ava_image_3.png"}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bindings are missing or stale"):
                normal_recap.publish(
                    self.report, out=out, check=True, inspect_workflow_selections=True,
                    workflow_configuration_path=alternate,
                )

    def test_planning_snapshot_rechecks_native_policy_and_isolated_selections(self):
        bands = policy.load_policy()
        self.records[0]["score"] = 0.
        self.records[0]["scoreContext"].update(coreSize=1, coreMember=False)
        self.records[1]["score"] = .5
        self.records[2]["score"] = .5
        (self.root / pathlib.PurePosixPath(self.a)).write_bytes(b"original1")
        core_path = "Angels/Ava/gallery/ava_image_4.jpg"
        core_hash = hashlib.sha256(b"core native").hexdigest()
        (self.root / pathlib.PurePosixPath(core_path)).write_bytes(b"core native")
        source = {"source": core_path, "sourceHash": core_hash, "photoId": "photo:image_4"}
        self.receipt["plan"]["sourceRows"].append(source)
        self.receipt["plan"]["sourceHashes"][core_path] = core_hash
        self.receipt["sourceHashes"][core_path] = core_hash
        core_record = self.record(core_path, "photo:image_4", core_hash)
        core_record["score"] = .5
        core_record["scoreContext"]["coreMember"] = True
        self.records.append(core_record)
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        cfg = {"photos": {"Ava": "ava_image_1_944x1104.png"}, "flows": {}}
        config_path = self.root / "workspaces.json"
        schema_path = self.root / "workspaces.schema.json"
        config_path.write_text(json.dumps(cfg), encoding="utf-8")
        schema_path.write_text("{}", encoding="utf-8")
        out = self.library / "planning.html"
        model = {
            "detector": {"name": "YuNet", "file": "face_detection_yunet_2023mar.onnx", "sha256": "1" * 64},
            "recognizer": {"name": "SFace", "file": "face_recognition_sface_2021dec.onnx", "sha256": "2" * 64},
            "opencv": "fixture", "alignment": "FaceRecognizerSF.alignCrop",
        }
        model_id = hashlib.sha256(
            json.dumps(model, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        cache_path = self.root / "cache.json"
        cache_path.write_text(json.dumps({
            "centeringDomain": "general", "centeringMean": [0., 0.],
            "emb": {
                name: {"v": vector, "faces": 1, "px": 1000, "f2": 0., "alignmentEvidence": {
                    "state": "persisted", "sourceSha256": digest, "model": model, "modelId": model_id,
                }}
                for name, digest, vector in (("red", self.h1, [0., 1.]), ("core", core_hash, [1., 0.]))
            },
        }), encoding="utf-8")
        with mock.patch.object(actions.cw, "CFG_PATH", config_path), \
             mock.patch.object(actions.cw, "CFG_SCHEMA_PATH", schema_path), \
             mock.patch.object(actions.cw, "validate_config", side_effect=lambda value: value), \
             mock.patch.object(actions.cw, "work_root", return_value=self.root):
            normal_recap.publish(
                self.report, out=out, apply=True, bind_red_natives=True, inspect_workflow_selections=True,
            )
            checked = normal_admission.verified_red_snapshot(self.report, out, self.root, bands)
            self.assertEqual([row["photoId"] for row in checked["snapshotCandidates"]], ["photo:image_1"])
            self.assertEqual(checked["selectedIds"], ["photo:image_1"])
            self.assertFalse(checked["consumerCoverageVerified"])
            vector = np.array([1., 0.])
            candidate = {
                "photoId": "photo:image_1", "sourceFolder": "Angels/Ava", "sourceBucket": "Gallery",
                "currentPath": self.a, "sha256": self.h1, "redScore": 0., "side": "Prospects",
                "vector": np.array([0., 1.]), "qualityEligible": True,
            }
            cores = {"Angels/Ava": {"vector": vector, "corePhotoIds": ["photo:image_4"]}}
            references = {"Angels/Ava": [{
                "photoId": "photo:image_4", "sha256": core_hash, "vector": vector, "qualityEligible": True,
            }]}
            api = SimpleNamespace(
                plan_reconciliation=lambda *args, **kwargs: {"assignments": [], "held": []},
                invent_name=lambda *args: "unused",
            )
            planned = normal_admission.red_release_from_snapshot(
                api, [candidate], cores, references, policy.effective_settings({}, bands), bands, set(),
                receipt=self.report, report=out, root=self.root, cache_path=cache_path,
                reference_paths={"photo:image_4": core_path},
            )
            self.assertTrue(planned["held"][0]["releaseBlocked"])
            self.assertEqual(planned["reviewMeasurementProof"]["scoreCount"], 1)
            self.assertEqual(len(planned["routingMeasurementProof"]["nativeBindings"]), 2)
            self.assertFalse(planned["workflowConsumerCoverageVerified"])
            self.assertFalse(planned["measurementEvidenceVerified"])
            routing_args = (
                self.root, cache_path, [candidate], references, {"photo:image_4": core_path},
                policy.effective_settings({}, bands),
            )
            references["Angels/Ava"][0]["vector"] = np.array([0., 1.])
            with self.assertRaisesRegex(ValueError, "vector differs"):
                normal_admission.verify_red_routing_measurements(*routing_args)
            references["Angels/Ava"][0]["vector"] = vector
            references["Angels/Ava"][0]["qualityEligible"] = False
            with self.assertRaisesRegex(ValueError, "quality differs"):
                normal_admission.verify_red_routing_measurements(*routing_args)
            references["Angels/Ava"][0]["qualityEligible"] = True
            (self.root / pathlib.PurePosixPath(core_path)).write_bytes(b"edited core")
            with self.assertRaisesRegex(ValueError, "native changed"):
                normal_admission.verify_red_routing_measurements(*routing_args)
            (self.root / pathlib.PurePosixPath(core_path)).write_bytes(b"core native")
            altered = copy.deepcopy(bands)
            altered["scoreBands"]["red"]["maximumExclusive"] = .14
            with self.assertRaisesRegex(ValueError, "score bands differ"):
                normal_admission.verified_red_snapshot(self.report, out, self.root, altered)
            (self.root / pathlib.PurePosixPath(self.a)).write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "current native differs"):
                normal_admission.verified_red_snapshot(self.report, out, self.root, bands)
            (self.root / pathlib.PurePosixPath(self.a)).write_bytes(b"original1")
            cfg["photos"]["Other"] = "unknown.png"
            cfg["photos"]["Ava"] = "ava_image_4_944x1104.png"
            config_path.write_text(json.dumps(cfg), encoding="utf-8")
            normal_recap.publish(
                self.report, out=out, apply=True, bind_red_natives=True, inspect_workflow_selections=True,
            )
            with self.assertRaisesRegex(ValueError, "unidentified workflow selections"):
                normal_admission.verified_red_snapshot(self.report, out, self.root, bands)
            diagnostic = normal_admission.red_release_from_snapshot(
                api, [candidate], cores, references, policy.effective_settings({}, bands), bands, set(),
                receipt=self.report, report=out, root=self.root, cache_path=cache_path,
                reference_paths={"photo:image_4": core_path}, diagnostic_workflow_gaps=True,
            )
            self.assertEqual(diagnostic["assignments"], [])
            self.assertTrue(diagnostic["held"][0]["releaseBlocked"])
            self.assertIn("unidentified workflow selections", diagnostic["workflowGaps"])
            self.assertTrue(diagnostic["planningOnly"])
            catalog_path = self.root / ".likeness-library.json"
            metadata.save_catalog({"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}, catalog_path)
            cache_hash = metadata.content_sha256(cache_path)
            inventory = {
                "cores": cores, "references": references, "referencePaths": {"photo:image_4": core_path},
                "nativeBindings": {self.a: self.h1, core_path: core_hash}, "nonvotingBindings": {},
                "derivedNonvotingBindings": {}, "catalogSHA256": metadata.content_sha256(catalog_path),
                "cacheSHA256": cache_hash, "modelIds": [model_id], "diagnostics": [],
            }
            api.cw = SimpleNamespace(
                photo_folders=lambda _cfg, _root: [("Angels", "Ava", self.root / "Angels" / "Ava")],
                validate_config=actions.cw.validate_config,
            )
            with mock.patch.object(normal_admission, "verify_red_centering_population",
                                   return_value={"cacheSHA256": cache_hash, "modelIds": [model_id]}) as centering, \
                 mock.patch.object(normal_admission, "frozen_red_gallery_inventory", return_value=inventory):
                checked_diagnostic = normal_admission.checked_red_release_diagnostic(
                    api, self.root, cfg, bands, cache_path, receipt=self.report, report=out,
                )
                self.assertEqual(checked_diagnostic["candidateCount"], 1)
                self.assertTrue(checked_diagnostic["held"][0]["releaseBlocked"])
                self.assertFalse(checked_diagnostic["releaseAuthorized"])
                self.assertEqual(checked_diagnostic["galleryInventoryProof"]["nativeBindings"], inventory["nativeBindings"])
                def unassigned(rows, *_args, **_kwargs):
                    return {"assignments": [],
                            "held": [{"photoId": row["photoId"], "sourceFolder": row["sourceFolder"],
                                      "sourceBucket": row["sourceBucket"],
                                      "reason": "unassigned"} for row in rows]}

                with mock.patch.object(api, "plan_reconciliation", side_effect=unassigned):
                    simulated = normal_admission.checked_red_release_diagnostic(
                        api, self.root, cfg, bands, cache_path, receipt=self.report, report=out,
                        simulate_all=True,
                    )
                self.assertTrue(simulated["held"][0]["releaseBlocked"])
                self.assertFalse(simulated["releaseAuthorized"])
                self.assertTrue(simulated["hypotheticalRouting"]["planningOnly"])
                self.assertEqual(simulated["hypotheticalRouting"]["held"][0]["reviewDestination"], "Various/review")
                extra = self.root / "Angels" / "Ava" / "gallery" / "extra.jpg"

                def change_gallery(*_args, **_kwargs):
                    extra.write_bytes(b"new")
                    return {"checkedCount": 0}

                with mock.patch.object(api, "plan_reconciliation", side_effect=unassigned), \
                     mock.patch.object(normal_admission, "verified_rebuilt_red_review_census",
                                       side_effect=change_gallery):
                    with self.assertRaisesRegex(ValueError, "inventory changed during rebuilt"):
                        normal_admission.checked_red_release_diagnostic(
                            api, self.root, cfg, bands, cache_path, receipt=self.report, report=out,
                            simulate_all=True, simulate_core_refresh=True,
                        )
                extra.unlink()
                inventory["catalogSHA256"] = "0" * 64
                with self.assertRaisesRegex(ValueError, "catalogue changed"):
                    normal_admission.checked_red_release_diagnostic(
                        api, self.root, cfg, bands, cache_path, receipt=self.report, report=out,
                    )
                inventory["catalogSHA256"] = metadata.content_sha256(catalog_path)
                cfg["photos"]["Ava"] = "ava_image_1_944x1104.png"
                config_path.write_text(json.dumps(cfg), encoding="utf-8")
                normal_recap.publish(
                    self.report, out=out, apply=True, bind_red_natives=True, inspect_workflow_selections=True,
                )
                with mock.patch.object(normal_admission, "red_workflow_replacement_proposal",
                                       return_value={"photoId": "photo:image_1", "replacementPhotoId": "photo:image_4",
                                                     "replacementScore": .7}) as proposal:
                    checked_diagnostic = normal_admission.checked_red_release_diagnostic(
                        api, self.root, cfg, bands, cache_path, receipt=self.report, report=out,
                    )
                    self.assertEqual(checked_diagnostic["workflowReplacementProposals"][0]["state"], "proposed")
                    self.assertEqual(proposal.call_args.kwargs["retired_ids"], {"photo:image_1"})
                alternate = self.root / "sandbox-workspaces.json"
                alternate_cfg = {"photos": {"Ava": "ava_image_1_944x1104.png"}, "flows": {}}
                alternate.write_text(json.dumps(alternate_cfg), encoding="utf-8")
                alternate_out = self.library / "alternate-planning.html"
                normal_recap.publish(
                    self.report, out=alternate_out, apply=True, bind_red_natives=True,
                    inspect_workflow_selections=True, workflow_configuration_path=alternate,
                )
                with mock.patch.object(normal_admission, "red_workflow_replacement_proposal",
                                       return_value={"photoId": "photo:image_1",
                                                     "replacementPhotoId": "photo:image_4",
                                                     "replacementScore": .7}) as proposal:
                    alternate_result = normal_admission.checked_red_release_diagnostic(
                        api, self.root, cfg, bands, cache_path, receipt=self.report, report=alternate_out,
                        workflow_configuration_path=alternate,
                    )
                    self.assertEqual(proposal.call_args.args[3], alternate_cfg)
                    self.assertIs(centering.call_args.args[4], cfg)
                    self.assertFalse(alternate_result["releaseAuthorized"])
                alternate.write_text('{"photos":{},"flows":{}}', encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "bindings are missing or stale"):
                    normal_admission.checked_red_release_diagnostic(
                        api, self.root, cfg, bands, cache_path, receipt=self.report, report=alternate_out,
                        workflow_configuration_path=alternate,
                    )
                with mock.patch.object(normal_admission, "red_workflow_replacement_proposal",
                                       side_effect=ValueError("stale replacement")):
                    checked_diagnostic = normal_admission.checked_red_release_diagnostic(
                        api, self.root, cfg, bands, cache_path, receipt=self.report, report=out,
                    )
                    self.assertEqual(checked_diagnostic["workflowReplacementProposals"][0]["reason"],
                                     "stale replacement")
                    self.assertFalse(checked_diagnostic["releaseAuthorized"])
            del cfg["photos"]["Other"]
            cfg["photos"]["Ava"] = "ava_image_1_944x1104.png"
            config_path.write_text(json.dumps(cfg), encoding="utf-8")
            with mock.patch.object(actions.cw, "work_root", return_value=self.root / "production"):
                cfg["photos"]["Ava"] = "ava_image_4_944x1104.png"
                config_path.write_text(json.dumps(cfg), encoding="utf-8")
                normal_recap.publish(
                    self.report, out=out, apply=True, bind_red_natives=True, inspect_workflow_selections=True,
                )
                with self.assertRaisesRegex(ValueError, "not isolated"):
                    normal_admission.verified_red_snapshot(self.report, out, self.root, bands)
                diagnostic = normal_admission.red_release_from_snapshot(
                    api, [candidate], cores, references, policy.effective_settings({}, bands), bands, set(),
                    receipt=self.report, report=out, root=self.root, cache_path=cache_path,
                    reference_paths={"photo:image_4": core_path}, diagnostic_workflow_gaps=True,
                )
                self.assertTrue(diagnostic["held"][0]["releaseBlocked"])
                self.assertEqual(diagnostic["assignments"], [])

    def test_red_measurement_proof_reproduces_saved_core_scores(self):
        model = {
            "detector": {"name": "YuNet", "file": "face_detection_yunet_2023mar.onnx", "sha256": "1" * 64},
            "recognizer": {"name": "SFace", "file": "face_recognition_sface_2021dec.onnx", "sha256": "2" * 64},
            "opencv": "fixture", "alignment": "FaceRecognizerSF.alignCrop",
        }
        model_id = hashlib.sha256(
            json.dumps(model, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        def measurement(digest, vector):
            return {
                "v": vector, "alignmentEvidence": {
                    "state": "persisted", "sourceSha256": digest, "model": model, "modelId": model_id,
                },
            }

        red_hash, core_hash = "a" * 64, "b" * 64
        cache = {
            "centeringDomain": "general", "centeringMean": [0., 0.],
            "emb": {"red": measurement(red_hash, [0., 1.]), "core": measurement(core_hash, [1., 0.])},
        }
        saved = [{
            "photoId": "photo:image_1", "nativeSha256": red_hash, "score": 0.,
            "scoreContext": {"coreMember": False, "coreSize": 1},
            "reviewCore": [{"photoId": "photo:image_4", "sha256": core_hash}],
        }]
        cache_path = self.root / "cache.json"
        cache_path.write_text(json.dumps(cache), encoding="utf-8")
        proof = normal_admission.verify_red_review_measurements(self.root, cache_path, saved)
        self.assertEqual(proof["scoreCount"], 1)
        self.assertEqual(proof["maxScoreDifference"], 0.)
        self.assertFalse(proof["rivalInventoryVerified"])
        saved[0]["score"] = .1
        with self.assertRaisesRegex(ValueError, "does not reproduce"):
            normal_admission.verify_red_review_measurements(self.root, cache_path, saved)
        saved[0]["score"] = 0.
        cache["emb"]["core"]["alignmentEvidence"]["modelId"] = "invalid"
        cache_path.write_text(json.dumps(cache), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "model provenance"):
            normal_admission.verify_red_review_measurements(self.root, cache_path, saved)

    def test_stale_snapshot_score_is_not_classified(self):
        bands = policy.load_policy()
        self.records[0]["contentSha256"] = self.h3
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        data = normal_recap.collect(self.report)
        self.assertEqual(data["snapshotMatched"], 2)
        self.assertEqual(data["redScoreCount"], 2)
        self.assertTrue(any("Missing/stale Review evidence" in item for item in data["snapshotDiagnostics"]))
        self.assertFalse(any(item["row"]["destination"] == self.a for item in data["auditRecords"]))

    def test_workflow_red_replacement_is_a_non_red_same_owner_gallery_candidate(self):
        bands = policy.load_policy()
        self.records[0]["workflowSelected"] = False
        replacements = (
            ("Angels/Ava/gallery/ava_image_4.jpg", "photo:image_4", .21),
            ("Angels/Ava/gallery/ava_image_5.jpg", "photo:image_5", .12),
            ("Angels/Ava/review/ava_image_6.jpg", "photo:image_6", .8),
        )
        for path, photo_id, score in replacements:
            digest = hashlib.sha256(path.encode()).hexdigest()
            source = {"source": path, "sourceHash": digest, "photoId": photo_id}
            self.receipt["plan"]["sourceRows"].append(source)
            self.receipt["plan"]["sourceHashes"][path] = digest
            self.receipt["sourceHashes"][path] = digest
            record = self.record(path, photo_id, digest)
            record["score"] = score
            record["workflowSelected"] = False
            self.records.append(record)
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        data = normal_recap.collect(self.report)
        red = next(item for item in data["auditRecords"] if item["row"]["destination"] == self.a)
        self.assertEqual(red["workflowReplacementCandidates"], [])
        cfg = {"photos": {}, "flows": {"portrait": {"photos": {"Ava": "ava_image_1_944x1104.png"}}}}
        config_path = self.root / "workspaces.json"
        schema_path = self.root / "workspaces.schema.json"
        config_path.write_text(json.dumps(cfg), encoding="utf-8")
        schema_path.write_text("{}", encoding="utf-8")
        with mock.patch.object(actions.cw, "CFG_PATH", config_path), \
             mock.patch.object(actions.cw, "CFG_SCHEMA_PATH", schema_path), \
             mock.patch.object(actions.cw, "validate_config", side_effect=lambda value: value), \
             mock.patch.object(actions.cw, "work_root", return_value=self.root):
            normal_recap._attach_workflow_selection_bindings(data)
            def observe_binding(current):
                selected = next(item for item in current["auditRecords"] if item["row"]["destination"] == self.a)
                self.assertEqual(
                    [item["row"]["destination"] for item in selected["workflowReplacementCandidates"]],
                    [replacements[0][0]],
                )
                current["redNativeBindings"] = 0

            with mock.patch.object(normal_recap, "_bind_red_native_evidence", side_effect=observe_binding):
                manifest = normal_recap.publish(
                    self.report, out=self.library / "configured.html",
                    bind_red_natives=True, inspect_workflow_selections=True,
                )
            configured_red = next(item for item in manifest["redCandidates"] if item["currentPath"] == self.a)
            self.assertEqual(configured_red["workflowReplacementCandidates"][0]["photoId"], "photo:image_4")
        self.assertEqual(
            [item["row"]["destination"] for item in red["workflowReplacementCandidates"]],
            [replacements[0][0]],
        )
        audit = normal_recap.render(data, self.library / "recap-audit.html", audit=True)
        self.assertIn("workflow eligibility not verified", audit)
        self.assertIn("ava_image_4.jpg", audit)

    def test_invalid_snapshot_score_or_band_fails_explicitly(self):
        bands = copy.deepcopy(policy.load_policy())
        bands["scoreBands"]["red"]["maximumExclusive"] = .14
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "red maximum must equal the orange minimum"):
            normal_recap.collect(self.report)

        bands["scoreBands"]["red"]["maximumExclusive"] = .15
        self.records[0]["score"] = float("nan")
        self.save()
        page = self.review.read_text(encoding="utf-8").replace(
            "</html>", '<script id="likeness-policy-data" type="application/json">'
            + json.dumps(bands) + "</script></html>",
        )
        self.review.write_text(page, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "similarity score must be between"):
            normal_recap.collect(self.report)

    def test_archived_copies_are_accounted_for_without_borrowing_keeper_scores(self):
        destination = "_duplicates/run1/0123456789abcdef01234567/" + self.target
        plan = self.receipt["plan"]
        plan.pop("exactAliasTargets")
        for row in plan["sourceRows"]:
            if row["source"] == self.b:
                row["collisionRule"] = "exact-byte keeper"
            if row["source"] == self.target:
                row.update(sourceStatus="duplicate-archive", reason="exact-byte copy")
        plan["duplicateArchives"] = {self.target: {
            "source": self.target, "destination": destination, "sha256": self.h2,
            "photoId": "photo:image_2", "reason": "exact-byte copy", "selectedSource": self.b,
        }}
        self.receipt["publishedNative"].append({"native": destination, "sha256": self.h2})
        self.save()
        data = normal_recap.collect(self.report)
        archived = next(row for row in data["rows"] if row["duplicateArchive"])
        self.assertEqual(archived["destination"], destination)
        self.assertIsNone(archived["score"])
        self.assertNotIn("_duplicates", data["newIdentities"])
        self.assertEqual(data["snapshotMatched"], 3)
        page = normal_recap.render(data, self.library / "recap.html")
        self.assertIn('id="collisions"', page)
        self.assertIn("exact-byte keeper", page)
        self.assertIn(destination, page)
        self.assertIn('href="#collisions"', page)
        self.assertIn("1 duplicate archive(s)", page)
        self.assertIn("duplicate archives only; no identity rename", page)
        self.receipt["publishedNative"][-1]["sha256"] = self.h3
        self.save()
        with self.assertRaisesRegex(ValueError, "unbound duplicate archive"):
            normal_recap.collect(self.report)

    def test_content_duplicate_and_junk_destinations_have_distinct_verified_recap_rows(self):
        plan = self.receipt["plan"]
        extra, junk_path = "Various/gallery/image_4.jpg", "_junk/" + self.held
        archived_path = "_duplicates/run1/" + extra
        keeper, _incoming, _target, junked = plan["sourceRows"]
        keeper["contentVoteCanonical"] = True
        junked.update(group="Various", sourceStatus="confirmed-no-face-junk")
        plan["sourceRows"].append({
            "source": extra, "sourceHash": self.h1, "photoId": "photo:image_4", "group": "Various",
            "sourceStatus": "duplicate-archive", "crossIdExactArchive": True,
        })
        plan["sourceHashes"][extra] = self.receipt["sourceHashes"][extra] = self.h1
        plan["duplicateArchives"] = {extra: {
            "source": extra, "destination": archived_path, "sha256": self.h1,
            "photoId": "photo:image_4", "reason": "exact-byte copy under another ID",
            "selectedSource": self.a, "selectedPhotoId": "photo:image_1",
        }}
        plan["junkStorage"] = "_junk"
        plan["junkDispositions"] = {self.held: {
            "source": self.held, "destination": junk_path, "sha256": self.h3,
            "photoId": "photo:image_3", "faces": 0, "reason": "confirmed no detected face",
        }}
        self.receipt["publishedNative"] += [
            {"native": archived_path, "sha256": self.h1}, {"native": junk_path, "sha256": self.h3},
        ]
        self.records.pop()
        self.save()
        data = normal_recap.collect(self.report)
        self.assertEqual(data["collisionGroups"], {})
        self.assertEqual(data["snapshotMatched"], 2)
        self.assertEqual(data["snapshotDiagnostics"], [])
        self.assertNotIn("_junk", data["newIdentities"])
        page = normal_recap.render(data, self.library / "recap.html")
        for expected in ("Identical bytes under different photo IDs", archived_path, junk_path,
                         "1 duplicate archive(s) + 1 recoverable junk disposition(s)"):
            self.assertIn(expected, page)
        plan["duplicateArchives"][extra]["selectedPhotoId"] = "photo:image_5"
        self.save()
        with self.assertRaisesRegex(ValueError, "unbound duplicate archive evidence"):
            normal_recap.collect(self.report)

    def test_applied_report_preserves_transaction_bound_preview_reports(self):
        self.receipt["status"] = "preview"
        self.receipt["kind"] = "normal-rebase-preview"
        self.save()
        self.assertEqual(self.run_report("--apply"), 0)
        folder = self.library / "rebase-recap"
        preview = (folder / "run1.html").read_text(encoding="utf-8")
        self.assertIn('href="../../library/people_gallery.html"', preview)
        self.assertIn("../../_assets/gallery-banner.jpg", preview)
        before = {path: path.read_bytes() for path in folder.iterdir() if path.is_file()}
        journal = self.report.parent / "publication-journal.json"
        journal.write_text(json.dumps({
            "kind": "normal-publication", "status": "applied", "root": str(self.root),
            "after": {path.relative_to(self.root).as_posix(): hashlib.sha256(payload).hexdigest()
                      for path, payload in before.items()},
            "removed": [],
        }), encoding="utf-8")
        self.receipt["status"] = "applied"
        self.receipt["kind"] = "normal-rebase-receipt"
        self.save()
        self.assertEqual(self.run_report("--apply"), 0)
        normal_transaction.verify(self.root, journal)
        self.assertEqual({path: path.read_bytes() for path in before}, before)
        applied = (folder / "applied" / "run1.html").read_text(encoding="utf-8")
        self.assertIn('href="../../../library/people_gallery.html"', applied)
        self.assertIn("../../../_assets/gallery-banner.jpg", applied)
        self.assertEqual(self.run_report("--check"), 0)

    def test_preview_apply_check_conserve_aliases_and_use_existing_navigation_without_hashing_photos(self):
        before = self.report.read_bytes()
        out = self.library / "rebase-recap" / "applied" / "run1.html"
        with mock.patch.object(rebase_recap, "_file_verification",
                               side_effect=AssertionError("no native hash campaign")):
            self.assertEqual(self.run_report("--dry-run"), 0)
            self.assertFalse(out.exists())
            self.assertEqual(self.run_report("--apply"), 0)
            self.assertEqual(self.run_report("--check"), 0)
        self.assertEqual(self.report.read_bytes(), before)
        page = out.read_text(encoding="utf-8")
        audit = out.with_name("run1-audit.html").read_text(encoding="utf-8")
        self.assertIn("4 physical source rows", page)
        self.assertIn("3 distinct destinations + 1", page)
        self.assertIn('href="#flows"', page)
        self.assertNotRegex(page, r'href="#[^"]+" target="_blank"')
        self.assertIn('target="_blank" rel="noopener noreferrer"', page)
        self.assertIn("people_gallery_review.html?person=", page)
        self.assertIn("Current photo (not rehashed)", page)
        self.assertIn("protected recommendation only", audit)
        self.assertIn("workflow reference outside active core", audit)
        self.assertIn('href="run1.html#flows"', audit)

    def test_unbound_moves_and_unproven_alias_coalescence_refuse(self):
        original = copy.deepcopy(self.receipt)
        for change in ("move", "alias", "hash"):
            self.receipt = copy.deepcopy(original)
            if change == "move":
                self.receipt["plan"]["moves"][0]["photoId"] = "photo:wrong"
            elif change == "alias":
                self.receipt["plan"]["exactAliasTargets"] = {}
            else:
                self.receipt["plan"]["sourceRows"][0]["sourceHash"] = self.h2
            self.save()
            self.assertEqual(self.run_report("--apply"), 1)
            self.assertFalse((self.library / "rebase-recap").exists())

    def replacement(self):
        previous = hashlib.sha256(b"previous native").hexdigest()
        target = self.receipt["plan"]["sourceRows"][2]
        target.update(
            sourceHash=previous, sourceStatus="preserved-version", selectedSource=self.b,
        )
        self.receipt["plan"]["sourceRows"][1]["sourceStatus"] = "incoming-update"
        self.receipt["sourceHashes"][self.target] = previous
        self.receipt["plan"]["sourceHashes"][self.target] = previous
        self.receipt["plan"]["exactAliasTargets"] = {}
        self.receipt["plan"]["incomingUpdates"] = {"photo:image_2": {
            "source": self.b, "owner": "Models/Bea", "previousSource": self.target,
            "previousHash": previous, "sourceHash": self.h2,
        }}

    def test_bound_replacement_preserves_prior_version_without_an_extra_current_vote(self):
        self.replacement()
        self.save()
        before = self.report.read_bytes()
        data = normal_recap.collect(self.report)
        self.assertEqual(data["physicalSources"], 4)
        self.assertEqual(data["physicalDestinations"], 3)
        self.assertEqual(data["coalescedAliases"], 0)
        self.assertEqual(data["supersededVersions"], 1)
        previous = next(row for row in data["rows"] if row["source"] == self.target)
        self.assertEqual(previous["kind"], "superseded-version")
        self.assertEqual(previous["preparedSHA256"], previous["sha256"])
        self.assertIsNone(previous["preview"])
        current = next(item for item in data["auditRecords"] if item["row"]["photoId"] == "photo:image_2")
        self.assertEqual(current["row"]["source"], self.b)
        self.assertEqual(data["snapshotMatched"], 3)
        self.assertEqual(self.run_report("--apply"), 0)
        self.assertEqual(self.run_report("--check"), 0)
        page = (self.library / "rebase-recap" / "applied" / "run1.html").read_text(encoding="utf-8")
        self.assertIn("1 superseded native versions", page)
        self.assertEqual(self.report.read_bytes(), before)

    def test_replacement_requires_exact_old_new_and_classification_bindings(self):
        self.replacement()
        original = copy.deepcopy(self.receipt)
        for field in ("source", "owner", "previousSource", "previousHash", "sourceHash", "sourceStatus", "selectedSource"):
            with self.subTest(field=field):
                self.receipt = copy.deepcopy(original)
                if field in ("sourceStatus", "selectedSource"):
                    self.receipt["plan"]["sourceRows"][2][field] = "wrong"
                else:
                    self.receipt["plan"]["incomingUpdates"]["photo:image_2"][field] = "wrong"
                self.save()
                with self.assertRaises(ValueError):
                    normal_recap.collect(self.report)

    def test_stale_review_hash_or_id_is_not_presented_as_current_score_evidence(self):
        self.records[0]["contentSha256"] = self.h2
        self.records[1]["photoId"] = "photo:wrong"
        self.save()
        data = normal_recap.collect(self.report)
        self.assertEqual(data["snapshotMatched"], 1)
        self.assertEqual(len(data["snapshotDiagnostics"]), 2)
        self.assertEqual(len(data["auditRecords"]), 1)

    def test_missing_review_id_pairs_only_by_exact_physical_path_and_native_hash(self):
        self.records[0]["photoId"] = None
        self.save()
        data = normal_recap.collect(self.report)
        self.assertEqual(data["snapshotMatched"], 3)
        self.assertEqual(data["snapshotIdUnavailable"], 1)
        self.assertEqual(len(data["auditRecords"]), 3)

    def test_check_refuses_output_tampering_and_changed_review_input(self):
        self.assertEqual(self.run_report("--apply"), 0)
        out = self.library / "rebase-recap" / "applied" / "run1-audit.html"
        out.write_text("changed", encoding="utf-8")
        self.assertEqual(self.run_report("--check"), 1)
        self.assertEqual(self.run_report("--apply"), 0)
        out.with_name("index.html").unlink()
        self.assertEqual(self.run_report("--check"), 1)
        self.assertEqual(self.run_report("--apply"), 0)
        self.records[0]["reason"] = "later evidence"
        self.save()
        self.assertEqual(self.run_report("--check"), 1)

    def test_same_source_run_comparison_and_different_source_refusal(self):
        other = self.report.with_name("other.json")
        value = copy.deepcopy(self.receipt)
        value["runId"] = "other"
        other.write_text(json.dumps(value), encoding="utf-8")
        self.assertEqual(self.run_report("--compare", str(other), "--apply"), 0)
        page = (self.library / "rebase-recap" / "applied" / "run1.html").read_text(encoding="utf-8")
        self.assertIn("0 photos placed differently", page)
        value["sourceHashes"][self.a] = self.h2
        value["plan"]["sourceHashes"][self.a] = self.h2
        value["plan"]["sourceRows"][0]["sourceHash"] = self.h2
        other.write_text(json.dumps(value), encoding="utf-8")
        self.assertEqual(self.run_report("--compare", str(other), "--apply"), 1)


if __name__ == "__main__":
    unittest.main()
