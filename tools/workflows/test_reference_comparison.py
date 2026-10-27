"""Synthetic frozen-image/receipt fixtures; no real photos or server access."""
import copy
import pathlib
import shutil
import unittest
import uuid
from unittest import mock

from PIL import Image

from tools.workflows import reference_comparison as comparison
from tools.workflows import reference_execution as execution
from tools.workflows import reference_rendering as base


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(__file__).resolve().parents[2] / (
            ".test-reference-comparison-" + uuid.uuid4().hex)
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)
        self.source = self.root / "Various" / "gallery" / "source.png"
        self.source.parent.mkdir(parents=True)
        Image.new("RGB", (16, 24), "blue").save(self.source)
        self.inputs = self.root / "inputs"
        self.outputs = self.root / "outputs"
        self.inputs.mkdir()
        self.outputs.mkdir()
        self.batch("alpha", states=("completed", "queued", "failed"))

    def batch(self, batch_id, states=("completed",), person_id="person-one",
              name="Synthetic Person", source=None, source_kind=None):
        source = source or self.source
        jobs = []
        for index, state in enumerate(states):
            job = {
                "id": f"job-{index}", "personId": person_id, "displayName": name,
                "recipe": "manual-0c-cleanup-basic", "workflowMode": "reference",
                "profile": "reference-faithful", "seed": index + 10,
                "source": {"path": source.relative_to(self.root).as_posix(),
                           "sha256": base.digest(source.read_bytes()), "domain": "general"},
            }
            if source_kind:
                job["source"]["kind"] = source_kind
            jobs.append(job)
        request = {"schemaVersion": 1, "batchId": batch_id, "workspace": "Sovereign Females",
                   "jobs": jobs}
        run = base.prepare(request, self.root)
        destination = base.run_path(self.root, batch_id)
        if all(state == "input-prepared" for state in states):
            return
        compiled_jobs = {}
        for job, prepared in zip(jobs, run["jobs"]):
            input_relative = f"reference/{batch_id}/{job['id']}/source.png"
            staged = base.safe_path(self.inputs, input_relative)
            staged.parent.mkdir(parents=True)
            staged.write_bytes(source.read_bytes())
            artifact = f"jobs/{job['id']}/workflow-api.json"
            graph = base.encode({"save": {"class_type": "SaveImage", "inputs": {}}})
            base.safe_path(destination, artifact).write_bytes(graph)
            compiled_jobs[job["id"]] = {
                "state": "compiled", "recipe": job["recipe"], "seed": job["seed"],
                "displayName": name, "input": input_relative, "inputSha256": prepared["sha256"],
                "prefix": f"reference/{batch_id}/{job['id']}/synthetic",
                "artifacts": {artifact: base.digest(graph)}, "outputs": [],
            }
        compiled = {"schemaVersion": 1, "batchId": batch_id, "endpoint": "http://127.0.0.1:8188",
                    "inputRoot": str(self.inputs), "outputRoot": str(self.outputs), "jobs": compiled_jobs}
        record = copy.deepcopy(compiled)
        for job, state in zip(record["jobs"].values(), states):
            job["state"] = state
            if state == "completed":
                output = base.safe_path(self.outputs, job["prefix"] + "_00001_.png")
                output.parent.mkdir(parents=True)
                Image.new("RGB", (20, 32), "green").save(output)
                job["outputs"] = [{
                    "filename": output.name,
                    "subfolder": output.parent.relative_to(self.outputs).as_posix(),
                    "type": "output", "path": str(output), "sha256": base.digest(output.read_bytes()),
                }]
            elif state == "failed":
                job["error"] = "Synthetic failure <unsafe>"
        (destination / "compiled.json").write_bytes(base.encode(compiled))
        (destination / "execution.json").write_bytes(base.encode(record))

    def record(self, batch="alpha"):
        return base.read_json(base.run_path(self.root, batch) / "execution.json")

    def save_record(self, record, batch="alpha"):
        (base.run_path(self.root, batch) / "execution.json").write_bytes(base.encode(record))

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.root.rglob("*") if path.is_file()}

    def test_preview_and_check_do_not_write_or_contact_server(self):
        before = self.snapshot()
        with mock.patch.object(base, "server_json", side_effect=AssertionError("network")), \
                mock.patch.object(execution, "connection", side_effect=AssertionError("network")), \
                mock.patch.object(execution, "post_json", side_effect=AssertionError("queue")):
            result = comparison.publish(self.root, ["alpha"])
            checked = comparison.publish(self.root, ["alpha"], check=True)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(result["current"])
        self.assertFalse(result["applied"])
        self.assertEqual(checked, result)
        self.assertEqual((result["sources"], result["outputs"], result["jobs"]), (1, 1, 3))
        self.assertEqual(result["states"], {"completed": 1, "failed": 1, "queued": 1})

    def test_apply_atomic_idempotent_and_currency_read_only(self):
        before = self.snapshot()
        with mock.patch.object(base.report_assets, "replace_file",
                               wraps=base.report_assets.replace_file) as replace:
            result = comparison.publish(self.root, ["alpha"], apply=True)
        self.assertEqual(replace.call_count, 1)
        self.assertTrue(result["current"])
        self.assertTrue(result["applied"])
        after = self.snapshot()
        self.assertEqual(set(after) - set(before), {comparison.PAGE_RELATIVE})
        for name, value in before.items():
            self.assertEqual(after[name], value)
        self.assertTrue(comparison.publish(self.root, ["alpha"], check=True)["current"])
        comparison.publish(self.root, ["alpha"], apply=True)
        self.assertEqual(self.snapshot(), after)
        record = self.record()
        record["jobs"]["job-1"]["state"] = "running"
        self.save_record(record)
        stale = self.snapshot()
        self.assertFalse(comparison.publish(self.root, ["alpha"], check=True)["current"])
        self.assertEqual(self.snapshot(), stale)

    def test_page_has_exact_frozen_lineage_labels_filters_and_no_scores(self):
        result = comparison.publish(self.root, ["alpha"], apply=True)
        page = pathlib.Path(result["page"]).read_text(encoding="utf-8")
        for text in ("Original photo input (frozen copy)", "Synthetic completed render",
                     "Various/gallery/source.png", base.digest(self.source.read_bytes()),
                     "personId: person-one", "job-0", "job-1", "job-2", "alpha",
                     "manual-0c-cleanup-basic", "reference-faithful", "seed: 10",
                     'id="person"', 'id="recipe"', 'id="state"', "Matched recipe across people",
                     "Resemblance is not evidence of identity or kinship",
                     "No completed output. State: queued", "No completed output. State: failed",
                     "Synthetic failure &lt;unsafe&gt;", "site-masthead", "library-footer"):
            self.assertIn(text, page)
        self.assertNotIn("Synthetic failure <unsafe>", page)
        self.assertIn((base.run_path(self.root, "alpha") /
                       "jobs/job-0/input/source.png").as_uri(), page)
        self.assertNotIn(self.source.as_uri(), page)
        self.assertIn(pathlib.Path(self.record()["jobs"]["job-0"]["outputs"][0]["path"]).as_uri(), page)
        self.assertNotIn("fetch(", page)
        self.assertNotIn("<canvas", page)
        self.assertNotIn("faceScore", page)

    def test_history_survives_original_source_move(self):
        self.source.unlink()
        result = comparison.publish(self.root, ["alpha"], apply=True)
        self.assertEqual(result["outputs"], 1)

    def test_footer_is_main_sibling_inside_shared_page_wrapper(self):
        page = comparison._page(self.root, [], ["alpha"])
        footer = comparison.gallery_chrome.footer(
            "Read-only human comparison; no source, identity, family or queue changes.")
        self.assertIn('<div class="site-page"><main>', page)
        self.assertIn(f"</main>\n{footer}\n</div><script>", page)
        self.assertNotIn('<main class="site-page">', page)

    def test_multiple_batches_share_only_exact_person_source_hash_groups(self):
        self.batch("beta", name="Renamed Synthetic Person")
        self.batch("gamma", person_id="person-two", name="Synthetic Person")
        other = self.source.with_name("another-path.png")
        other.write_bytes(self.source.read_bytes())
        self.batch("delta", source=other)
        Image.new("RGB", (16, 24), "red").save(self.source)
        self.batch("epsilon")
        result = comparison.publish(self.root, ["epsilon", "delta", "gamma", "beta", "alpha"], apply=True)
        self.assertEqual((result["people"], result["sources"], result["outputs"], result["jobs"]),
                         (2, 4, 5, 7))
        self.assertTrue(comparison.publish(
            self.root, ["alpha", "beta", "gamma", "delta", "epsilon"], check=True)["current"])

    def test_uncompiled_pending_and_synthetic_sources_are_explicit(self):
        self.batch("pending", states=("input-prepared",))
        selected = self.root / "_generation" / "selected" / "origin" / "one" / "render.png"
        selected.parent.mkdir(parents=True)
        selected.write_bytes(self.source.read_bytes())
        sidecar = {"synthetic": True, "identityCoreEligible": False, "sha256": base.digest(selected.read_bytes()),
                   "batchId": "origin", "jobId": "one"}
        pathlib.Path(str(selected) + ".json").write_bytes(base.encode(sidecar))
        self.batch("synthetic", source=selected, source_kind="selected-render")
        result = comparison.publish(self.root, ["pending", "synthetic"], apply=True)
        self.assertEqual(result["states"], {"completed": 1, "input-prepared": 1})
        page = pathlib.Path(result["page"]).read_text(encoding="utf-8")
        self.assertIn("Synthetic source — selected-render (frozen copy)", page)
        self.assertIn("No completed output. State: input-prepared", page)

    def test_missing_and_tampered_output_refuse_even_preview_preserving_old_page(self):
        comparison.publish(self.root, ["alpha"], apply=True)
        target = self.root / comparison.PAGE_RELATIVE
        previous = target.read_bytes()
        output = pathlib.Path(self.record()["jobs"]["job-0"]["outputs"][0]["path"])
        data = output.read_bytes()
        for missing in (True, False):
            if missing:
                output.unlink()
            else:
                output.write_bytes(data + b"tampered")
            for kwargs in ({}, {"check": True}, {"apply": True}):
                with self.subTest(missing=missing, kwargs=kwargs), self.assertRaisesRegex(
                        ValueError, "missing/unreadable output|output hash changed"):
                    comparison.publish(self.root, ["alpha"], **kwargs)
            self.assertEqual(target.read_bytes(), previous)

    def test_frozen_and_staged_and_artifact_tampering_fail(self):
        destination = base.run_path(self.root, "alpha")
        paths = [
            destination / "jobs/job-0/input/source.png",
            destination / "jobs/job-0/workflow-api.json",
            self.inputs / "reference/alpha/job-0/source.png",
        ]
        for path in paths:
            original = path.read_bytes()
            path.write_bytes(original + b"tampered")
            with self.subTest(path=path), self.assertRaisesRegex(
                    ValueError, "Frozen input hash changed|Compiled artifact changed|Staged ComfyUI input changed"):
                comparison.publish(self.root, ["alpha"])
            path.write_bytes(original)

    def test_output_namespace_path_type_and_duplicate_inventory_fail(self):
        original = self.record()
        for field, value in (("subfolder", "../outside"), ("filename", "foreign.png"),
                             ("filename", "../synthetic_00001_.png"), ("type", "temp"),
                             ("path", str(self.source))):
            record = copy.deepcopy(original)
            record["jobs"]["job-0"]["outputs"][0][field] = value
            self.save_record(record)
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "namespace|path changed"):
                comparison.publish(self.root, ["alpha"])
        record = copy.deepcopy(original)
        record["jobs"]["job-0"]["outputs"] *= 2
        self.save_record(record)
        with self.assertRaisesRegex(ValueError, "duplicated"):
            comparison.publish(self.root, ["alpha"])

    def test_completed_without_outputs_and_wrong_job_inventory_fail(self):
        record = self.record()
        record["jobs"]["job-0"]["outputs"] = []
        self.save_record(record)
        with self.assertRaisesRegex(ValueError, "no output evidence"):
            comparison.publish(self.root, ["alpha"])
        record["jobs"].pop("job-0")
        self.save_record(record)
        with self.assertRaisesRegex(ValueError, "job inventory"):
            comparison.publish(self.root, ["alpha"])

    def test_active_writer_refuses_read_only_and_apply(self):
        lock = base.run_path(self.root, "alpha") / "submission.lock"
        lock.write_text("synthetic writer", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "writer is active"):
            comparison.publish(self.root, ["alpha"])

    def test_compiled_metadata_must_match_frozen_request(self):
        destination = base.run_path(self.root, "alpha")
        compiled_path = destination / "compiled.json"
        original = base.read_json(compiled_path)
        for field, value in (("recipe", "different-recipe"), ("seed", 999),
                             ("displayName", "Different Person")):
            compiled = copy.deepcopy(original)
            compiled["jobs"]["job-0"][field] = value
            compiled_path.write_bytes(base.encode(compiled))
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "differs from request"):
                comparison.publish(self.root, ["alpha"])
        compiled = copy.deepcopy(original)
        compiled["jobs"]["extra-job"] = copy.deepcopy(compiled["jobs"]["job-0"])
        compiled_path.write_bytes(base.encode(compiled))
        record = self.record()
        record["jobs"]["extra-job"] = copy.deepcopy(record["jobs"]["job-0"])
        self.save_record(record)
        with self.assertRaisesRegex(ValueError, "compiled/frozen job inventory"):
            comparison.publish(self.root, ["alpha"])

    def test_invalid_scope_conflicting_flags_and_bounds_fail_without_writes(self):
        before = self.snapshot()
        for batches in ([], ["alpha", "alpha"], ["../alpha"], ["alpha/beta"], ["ALPHA"],
                        ["alpha"] * (comparison.MAX_BATCHES + 1), "alpha", [None]):
            with self.subTest(batches=batches), self.assertRaisesRegex(ValueError, "explicit batch IDs"):
                comparison.publish(self.root, batches)
        with self.assertRaisesRegex(ValueError, "not both"):
            comparison.publish(self.root, ["alpha"], apply=True, check=True)
        with mock.patch.object(comparison, "MAX_JOBS", 1), self.assertRaisesRegex(ValueError, "limit"):
            comparison.publish(self.root, ["alpha"])
        with mock.patch.object(comparison, "MAX_OUTPUTS", 0), self.assertRaisesRegex(ValueError, "limit"):
            comparison.publish(self.root, ["alpha"])
        self.assertEqual(self.snapshot(), before)

    def test_failed_replace_preserves_page_and_cleans_pending_file(self):
        comparison.publish(self.root, ["alpha"], apply=True)
        target = self.root / comparison.PAGE_RELATIVE
        previous = target.read_bytes()
        record = self.record()
        record["jobs"]["job-1"]["state"] = "running"
        self.save_record(record)
        with mock.patch.object(base.report_assets, "replace_file", side_effect=PermissionError("locked")), \
                self.assertRaises(PermissionError):
            comparison.publish(self.root, ["alpha"], apply=True)
        self.assertEqual(target.read_bytes(), previous)
        self.assertFalse(list(target.parent.glob(".comparison-*.pending")))

    def test_evidence_changing_before_publish_refuses(self):
        original = comparison._collect
        count = 0

        def changed(root, batches):
            nonlocal count
            count += 1
            if count == 2:
                record = self.record()
                record["jobs"]["job-1"]["state"] = "running"
                self.save_record(record)
            return original(root, batches)

        with mock.patch.object(comparison, "_collect", side_effect=changed), \
                self.assertRaisesRegex(ValueError, "evidence changed"):
            comparison.publish(self.root, ["alpha"], apply=True)
        self.assertFalse((self.root / comparison.PAGE_RELATIVE).exists())

    def test_html_escapes_request_names_and_no_identity_inference_for_missing_ids(self):
        request = base.read_json(base.run_path(self.root, "alpha") / "request.json")
        for job in request["jobs"]:
            job.pop("personId")
            job["displayName"] = '<script>alert("synthetic")</script>'
        # A distinct frozen batch uses valid schema fields, not forged prior evidence.
        request["batchId"] = "name-only"
        base.prepare(request, self.root)
        result = comparison.publish(self.root, ["name-only"], apply=True)
        page = pathlib.Path(result["page"]).read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;alert(&quot;synthetic&quot;)&lt;/script&gt;", page)
        self.assertNotIn('<script>alert("synthetic")</script>', page)
        self.assertIn("no personId (name-only/unassigned)", page)
        self.assertEqual(result["people"], 1)


if __name__ == "__main__":
    unittest.main()
