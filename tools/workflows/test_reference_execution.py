"""Scoped execution state, graph binding and selected-output retention tests."""
import copy
import pathlib
import tempfile
import unittest
from unittest import mock

from PIL import Image

from tools.workflows import reference_execution as execution
from tools.workflows import reference_rendering as base


def tiny_ui():
    return {
        "nodes": [
            {"id": 1, "type": "LoadImage", "widgets_values": ["old.png", "image"], "inputs": []},
            {"id": 2, "type": "sub", "widgets_values": ["preserve clothing", 1],
             "inputs": [{"name": "image", "link": 1},
                        {"name": "prompt", "widget": {"name": "prompt"}, "link": None},
                        {"name": "seed", "widget": {"name": "seed"}, "link": None}]},
            {"id": 3, "type": "SaveImage", "widgets_values": ["old"],
             "inputs": [{"name": "images", "link": 2},
                        {"name": "filename_prefix", "widget": {"name": "filename_prefix"}, "link": None}]},
        ],
        "links": [[1, 1, 0, 2, 0, "IMAGE"], [2, 2, 0, 3, 0, "IMAGE"]],
        "definitions": {"subgraphs": [{
            "id": "sub", "outputs": [{"linkIds": [11]}],
            "nodes": [{"id": 10, "type": "FluxKontextImageScale", "widgets_values": [],
                       "inputs": [{"name": "image", "link": 10}]}],
            "links": [{"id": 10, "origin_id": -10, "origin_slot": 0, "target_id": 10, "target_slot": 0},
                      {"id": 11, "origin_id": 10, "origin_slot": 0, "target_id": -20, "target_slot": 0}],
        }]},
    }


class GraphTests(unittest.TestCase):
    def test_catalog_distinguishes_cleanup_basic_and_cleanup(self):
        with mock.patch.object(execution, "recipe_path", side_effect=ValueError("not installed")):
            entries = {entry["id"]: entry for entry in execution.catalog()}
        self.assertNotEqual(entries["manual-0c-cleanup-basic"]["label"],
                            entries["manual-0c-cleanup"]["label"])
        self.assertIn("Basic", entries["manual-0c-cleanup-basic"]["label"])

    def test_one_level_binding_and_source_immutability(self):
        original = tiny_ui()
        snapshot = copy.deepcopy(original)
        ui, graph = execution.compile_ui(original, "reference/run/one/source.png", "reference/Person/one", 42)
        self.assertEqual(original, snapshot)
        self.assertEqual(ui["nodes"][1]["widgets_values"][1], 42)
        self.assertEqual(graph["input"]["inputs"]["image"], "reference/run/one/source.png")
        self.assertEqual(graph["save"]["inputs"]["filename_prefix"], "reference/Person/one")
        self.assertEqual(graph["10"]["inputs"]["image"], ["input", 0])

    def test_unknown_nested_bypass_and_shapes_refuse(self):
        for change in ("unknown", "bypass", "nested"):
            workflow = tiny_ui()
            if change == "unknown":
                workflow["definitions"]["subgraphs"][0]["nodes"][0]["type"] = "ExecShell"
            elif change == "bypass":
                workflow["definitions"]["subgraphs"][0]["nodes"][0]["mode"] = 4
            else:
                workflow["definitions"]["subgraphs"].append({"id": "other"})
            with self.subTest(change=change), self.assertRaises(ValueError):
                execution.compile_ui(workflow, "source.png", "reference/one", 42)

    def test_sampler_widget_control_not_server_input(self):
        fields = ("seed", "steps", "cfg", "sampler_name", "scheduler", "denoise")
        node = {"type": "KSampler", "inputs": [
            {"name": name, "widget": {"name": name}} for name in fields],
            "widgets_values": [1, "randomize", 4, 1, "euler", "simple", .9]}
        values = execution.widget_values(node)
        self.assertEqual(values["steps"], 4)
        self.assertEqual(values["denoise"], .9)
        self.assertNotIn("control_after_generate", values)

    def test_model_choice_and_missing_required_are_explicit(self):
        info = {"UNETLoader": {"input": {"required": {"unet_name": [["known"]]}}}}
        graph = {"a": {"class_type": "UNETLoader", "inputs": {"unet_name": "missing"}}}
        with self.assertRaisesRegex(ValueError, "Unavailable"):
            execution.validate_graph(graph, info)
        graph["a"]["inputs"] = {}
        with self.assertRaisesRegex(ValueError, "Missing required"):
            execution.validate_graph(graph, info)

    def test_loopback_only(self):
        for url in ("https://example.com", "http://localhost:8188", "http://127.0.0.1:8188/path"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                execution.connection(url)


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        self.batch = "pilot"
        self.destination = base.run_path(self.root, self.batch)
        self.destination.mkdir(parents=True)
        self.inputs = self.root / "inputs"
        self.outputs = self.root / "outputs"
        self.inputs.mkdir()
        self.outputs.mkdir()
        self.input_path = self.inputs / "reference" / "pilot" / "one" / "source.png"
        self.input_path.parent.mkdir(parents=True)
        Image.new("RGB", (20, 30), "blue").save(self.input_path)
        self.api_path = self.destination / "jobs" / "one" / "workflow-api.json"
        self.api_path.parent.mkdir(parents=True)
        self.api_path.write_bytes(base.encode({"save": {"class_type": "SaveImage", "inputs": {}}}))
        self.job = {
            "state": "compiled", "displayName": "A Person", "recipe": "manual-0c-cleanup",
            "input": "reference/pilot/one/source.png", "inputSha256": base.digest(self.input_path.read_bytes()),
            "prefix": "reference/A_Person/pilot/one/0_Edit/0c_Cleanup/A_Person_0c_Cleanup",
            "artifacts": {"jobs/one/workflow-api.json": base.digest(self.api_path.read_bytes())},
            "outputs": [],
        }
        self.record = {"schemaVersion": 1, "batchId": self.batch, "endpoint": "http://127.0.0.1:8188",
                       "inputRoot": str(self.inputs), "outputRoot": str(self.outputs),
                       "jobs": {"one": self.job}}
        (self.destination / "compiled.json").write_bytes(base.encode(self.record))
        self.save()

    def save(self):
        (self.destination / "execution.json").write_bytes(base.encode(self.record))

    def test_uncertain_post_is_not_retried(self):
        with mock.patch.object(base, "probe_server", return_value={"blockers": []}), \
                mock.patch.object(base, "server_json", side_effect=[
                    {"queue_running": [], "queue_pending": []}, {"SaveImage": {"input": {}}}]), \
                mock.patch.object(execution, "post_json", side_effect=TimeoutError("late reply")) as post:
            with self.assertRaises(TimeoutError):
                execution.submit(self.root, self.batch, "one", True)
            self.assertEqual(post.call_count, 1)
        saved = base.read_json(self.destination / "execution.json")
        self.assertEqual(saved["jobs"]["one"]["state"], "submission-uncertain")
        with self.assertRaisesRegex(ValueError, "never blindly resubmit"):
            execution.submit(self.root, self.batch, "one", True)
        self.assertFalse((self.destination / "submission.lock").exists())

    def test_busy_queue_does_not_post(self):
        with mock.patch.object(base, "probe_server", return_value={"blockers": []}), \
                mock.patch.object(base, "server_json", return_value={"queue_running": [[1, "other"]]}), \
                mock.patch.object(execution, "post_json") as post:
            with self.assertRaisesRegex(ValueError, "occupied"):
                execution.submit(self.root, self.batch, "one", True)
            post.assert_not_called()
        self.assertEqual(base.read_json(self.destination / "execution.json")["jobs"]["one"]["state"], "compiled")

    def test_status_refresh_lock_prevents_overwriting_new_submission(self):
        atomic = execution.atomic_json
        attempted = False
        blocked = False

        def interleave_submit(path, value):
            nonlocal attempted, blocked
            if not attempted:
                attempted = True
                try:
                    execution.submit(self.root, self.batch, "one", True)
                except ValueError as error:
                    if "locked" not in str(error):
                        raise
                    blocked = True
            atomic(path, value)

        with mock.patch.object(base, "probe_server", return_value={"blockers": []}), \
                mock.patch.object(base, "server_json", return_value={
                    "SaveImage": {"input": {"required": {}}}}), \
                mock.patch.object(execution, "post_json", return_value={"prompt_id": "new-prompt"}) as post, \
                mock.patch.object(execution, "atomic_json", side_effect=interleave_submit):
            execution.status(self.root, self.batch, True)
        self.assertTrue(blocked)
        post.assert_not_called()

    def test_status_timeout_releases_lock_without_changing_prompt_id(self):
        self.job.update(state="queued", promptId="existing-prompt")
        self.save()
        with mock.patch.object(base, "server_json", side_effect=TimeoutError("slow history")):
            with self.assertRaises(TimeoutError):
                execution.status(self.root, self.batch, True)
        self.assertFalse((self.destination / "submission.lock").exists())
        saved = base.read_json(self.destination / "execution.json")["jobs"]["one"]
        self.assertEqual(saved["state"], "queued")
        self.assertEqual(saved["promptId"], "existing-prompt")

    def test_receipt_publish_retries_transient_windows_lock(self):
        path = self.root / "atomic.json"
        path.write_bytes(base.encode({"old": True}))
        replace = base.report_assets.os.replace
        attempts = 0

        def temporarily_locked(stage, target):
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise PermissionError("Windows scanner owns the destination briefly")
            replace(stage, target)

        with mock.patch.object(base.report_assets.os, "replace", side_effect=temporarily_locked), \
                mock.patch.object(base.report_assets.time, "sleep") as sleep:
            execution.atomic_json(path, {"new": True})
        self.assertEqual(attempts, 3)
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(base.read_json(path), {"new": True})
        self.assertFalse(path.with_name("atomic.json.pending").exists())

    def test_permanent_receipt_publish_failure_preserves_prior_receipt_and_pending_evidence(self):
        path = self.root / "atomic.json"
        path.write_bytes(base.encode({"old": True}))
        with mock.patch.object(base.report_assets.os, "replace", side_effect=PermissionError("locked")), \
                mock.patch.object(base.report_assets.time, "sleep"):
            with self.assertRaises(PermissionError):
                execution.atomic_json(path, {"new": True})
        self.assertEqual(base.read_json(path), {"old": True})
        self.assertEqual(base.read_json(path.with_name("atomic.json.pending")), {"new": True})

    def test_busy_queue_explicitly_appends_one_without_priority_or_cancellation(self):
        with mock.patch.object(base, "probe_server", return_value={"blockers": []}), \
                mock.patch.object(base, "server_json", side_effect=[
                    {"queue_running": [[1, "other"]], "queue_pending": [[2, "also-other"]]},
                    {"SaveImage": {"input": {"required": {}}}}]), \
                mock.patch.object(execution, "post_json", return_value={"prompt_id": "one-prompt"}) as post:
            result = execution.submit(self.root, self.batch, "one", True, allow_busy_queue=True)
        self.assertEqual(result["queuePolicy"], "append-one")
        self.assertEqual(result["state"], "queued")
        self.assertEqual(post.call_count, 1)
        self.assertEqual(post.call_args.args[2], "/prompt")
        self.assertNotIn("front", post.call_args.args[3])
        self.assertNotIn("number", post.call_args.args[3])

    def test_run_busy_queue_opt_in_keeps_only_one_selected_job_outstanding(self):
        compiled = copy.deepcopy(self.record)
        queued = copy.deepcopy(self.record)
        queued["jobs"]["one"]["state"] = "queued"
        completed = copy.deepcopy(self.record)
        completed["jobs"]["one"]["state"] = "completed"
        with mock.patch.object(execution, "status", side_effect=[
                compiled, queued, completed, completed]), \
                mock.patch.object(base, "server_json", return_value={"queue_pending": [[1, "other"]]}), \
                mock.patch.object(execution, "submit") as submit, \
                mock.patch.object(execution.time, "sleep"):
            execution.run_batch(self.root, self.batch, True, allow_busy_queue=True)
        submit.assert_called_once_with(self.root, self.batch, "one", True, allow_busy_queue=True)

    def test_stale_staged_input_refuses(self):
        self.input_path.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "input changed"):
            execution.status(self.root, self.batch)

    def test_status_actual_owned_output_and_explicit_retention(self):
        relative = self.job["prefix"] + "_00001_.png"
        image_path = self.outputs.joinpath(*relative.split("/"))
        image_path.parent.mkdir(parents=True)
        Image.new("RGB", (20, 30), "red").save(image_path)
        output = {"filename": image_path.name, "subfolder": image_path.parent.relative_to(self.outputs).as_posix(),
                  "type": "output"}
        self.job.update(state="queued", promptId="prompt-one")
        self.save()
        history = {"prompt-one": {"status": {"completed": True}, "outputs": {"save": {"images": [output]}}}}
        with mock.patch.object(base, "server_json", return_value=history):
            result = execution.status(self.root, self.batch, True)
        self.assertEqual(result["jobs"]["one"]["state"], "completed")
        self.assertFalse((self.root / "_generation" / "selected").exists())
        sha = result["jobs"]["one"]["outputs"][0]["sha256"]
        preview = execution.retain(self.root, self.batch, "one", sha)
        self.assertFalse(pathlib.Path(preview["destination"]).exists())
        saved = execution.retain(self.root, self.batch, "one", sha, True)
        self.assertEqual(pathlib.Path(saved["destination"]).read_bytes(), image_path.read_bytes())
        self.assertFalse(saved["identityCoreEligible"])
        self.assertTrue(saved["synthetic"])
        relative_selected = pathlib.Path(saved["destination"]).relative_to(self.root).as_posix()
        selection = {"source": {"path": relative_selected, "sha256": sha,
                                "domain": "general", "kind": "selected-render"}}
        data, size, image_format = base.inspect_source(self.root, selection)
        self.assertEqual(data, image_path.read_bytes())
        self.assertEqual(size, [20, 30])
        self.assertEqual(image_format, "PNG")
        request = {"schemaVersion": 1, "batchId": "selected-next",
                   "workspace": "Sovereign Females", "jobs": [{
                       "id": "next", "source": selection["source"],
                       "workflowMode": "reference", "recipe": "manual-0c-cleanup",
                       "profile": "reference-faithful", "seed": 13,
                       "displayName": "A Person"}]}
        base.prepare(request, self.root)
        checked = base.check(self.root, "selected-next")
        self.assertEqual(checked["jobs"][0]["sha256"], sha)
        selection["source"]["kind"] = "photo"
        with self.assertRaisesRegex(ValueError, "outside active"):
            base.inspect_source(self.root, selection)

    def test_history_output_outside_job_refuses(self):
        self.job.update(state="queued", promptId="prompt-one")
        self.save()
        history = {"prompt-one": {"status": {"completed": True}, "outputs": {"save": {
            "images": [{"filename": "other.png", "subfolder": "../other", "type": "output"}]}}}}
        with mock.patch.object(base, "server_json", return_value=history):
            with self.assertRaisesRegex(ValueError, "outside"):
                execution.status(self.root, self.batch, True)

    def test_lost_history_holds_instead_of_success(self):
        self.job.update(state="queued", promptId="prompt-one")
        self.save()
        with mock.patch.object(base, "server_json", side_effect=[{}, {"queue_running": [], "queue_pending": []}]):
            result = execution.status(self.root, self.batch, True)
        self.assertEqual(result["jobs"]["one"]["state"], "history-missing")

    def test_compiled_artifact_tamper_refuses(self):
        self.api_path.write_text("{}")
        with self.assertRaisesRegex(ValueError, "artifact changed"):
            execution.status(self.root, self.batch)

    def test_run_preview_and_explicit_limit(self):
        preview = execution.run_batch(self.root, self.batch)
        self.assertEqual(preview["jobs"], ["one"])
        with self.assertRaisesRegex(ValueError, "limit"):
            execution.run_batch(self.root, self.batch, limit=0)
        with mock.patch.object(execution, "post_json") as post:
            execution.run_batch(self.root, self.batch)
            post.assert_not_called()

    def test_run_waits_other_queue_then_submits_once(self):
        compiled = copy.deepcopy(self.record)
        completed = copy.deepcopy(self.record)
        completed["jobs"]["one"]["state"] = "completed"
        with mock.patch.object(execution, "status", side_effect=[compiled, compiled, completed, completed]), \
                mock.patch.object(base, "server_json", side_effect=[
                    {"queue_running": [[1, "unrelated"]]}, {"queue_running": [], "queue_pending": []}]), \
                mock.patch.object(execution, "submit") as submit, \
                mock.patch.object(execution.time, "sleep"):
            result = execution.run_batch(self.root, self.batch, True)
        submit.assert_called_once_with(self.root, self.batch, "one", True)
        self.assertEqual(result["jobs"]["one"]["state"], "completed")

    def test_run_uncertain_state_holds(self):
        self.job["state"] = "submission-uncertain"
        self.save()
        with self.assertRaisesRegex(ValueError, "review receipt"):
            execution.run_batch(self.root, self.batch, True)

    def test_run_retries_only_read_only_poll_timeout(self):
        completed = copy.deepcopy(self.record)
        completed["jobs"]["one"]["state"] = "completed"
        with mock.patch.object(execution, "status", side_effect=[
                self.record, self.record, completed, completed]), \
                mock.patch.object(base, "server_json", side_effect=[TimeoutError("slow GET"), {}]), \
                mock.patch.object(execution, "submit") as submit, \
                mock.patch.object(execution.time, "sleep"):
            result = execution.run_batch(self.root, self.batch, True)
        self.assertEqual(result["jobs"]["one"]["state"], "completed")
        submit.assert_called_once_with(self.root, self.batch, "one", True)

    def test_run_never_retries_submission_timeout(self):
        with mock.patch.object(execution, "status", return_value=self.record), \
                mock.patch.object(base, "server_json", return_value={}), \
                mock.patch.object(execution, "submit", side_effect=TimeoutError("uncertain POST")) as submit:
            with self.assertRaisesRegex(TimeoutError, "uncertain POST"):
                execution.run_batch(self.root, self.batch, True)
        submit.assert_called_once_with(self.root, self.batch, "one", True)

    def test_run_does_not_submit_when_reads_cross_deadline(self):
        with mock.patch.object(execution, "status", return_value=self.record), \
                mock.patch.object(base, "server_json", return_value={}), \
                mock.patch.object(execution.time, "monotonic", side_effect=[0, 0, 2]), \
                mock.patch.object(execution, "submit") as submit:
            with self.assertRaisesRegex(TimeoutError, "before submission"):
                execution.run_batch(self.root, self.batch, True, timeout=1)
        submit.assert_not_called()

    def test_submit_refuses_at_queue_capacity_even_when_busy_queue_allowed(self):
        full = {"queue_running": [], "queue_pending": [[i, f"p{i}"] for i in range(execution.QUEUE_CAPACITY)]}
        with mock.patch.object(base, "probe_server", return_value={"blockers": []}), \
                mock.patch.object(base, "server_json", return_value=full), \
                mock.patch.object(execution, "post_json") as post:
            with self.assertRaisesRegex(ValueError, "200-job capacity"):
                execution.submit(self.root, self.batch, "one", True, allow_busy_queue=True)
            post.assert_not_called()

    def test_submit_ignores_its_own_batch_prompts_when_checking_busy(self):
        queue = {"queue_running": [[1, "mine"]], "queue_pending": []}
        with mock.patch.object(base, "probe_server", return_value={"blockers": []}), \
                mock.patch.object(base, "server_json", side_effect=[queue, {"SaveImage": {"input": {}}}]):
            preview = execution.submit(self.root, self.batch, "one", False, owned_prompts={"mine"})
        self.assertEqual(preview["state"], "submission-preview")

    def test_run_depth_and_limit_ranges(self):
        preview = execution.run_batch(self.root, self.batch, queue_depth=4, limit=64)
        self.assertEqual((preview["queueDepth"], preview["queueCapacity"]), (4, 200))
        for kwargs in ({"queue_depth": 0}, {"queue_depth": 17}, {"limit": 65}):
            with self.assertRaisesRegex(ValueError, "queue depth"):
                execution.run_batch(self.root, self.batch, **kwargs)

    def _two_jobs(self, *states):
        record = copy.deepcopy(self.record)
        record["jobs"]["two"] = copy.deepcopy(self.job)
        for (job_id, job), state in zip(record["jobs"].items(), states):
            job["state"] = state
            if state in {"queued", "running"}:
                job["promptId"] = "prompt-" + job_id
        return record

    def test_pipelined_run_keeps_depth_jobs_queued_without_waiting_for_its_own(self):
        with mock.patch.object(execution, "status", side_effect=[
                self._two_jobs("compiled", "compiled"), self._two_jobs("completed", "completed"),
                self._two_jobs("completed", "completed")]), \
                mock.patch.object(base, "server_json", return_value={}), \
                mock.patch.object(execution, "submit", side_effect=[
                    {"promptId": "p1"}, {"promptId": "p2"}]) as submit, \
                mock.patch.object(execution.time, "sleep"):
            result = execution.run_batch(self.root, self.batch, True, queue_depth=2)
        self.assertEqual([call.args[2] for call in submit.call_args_list], ["one", "two"])
        self.assertEqual(submit.call_args_list[1].kwargs["allow_busy_queue"], False)
        self.assertEqual(result["jobs"]["two"]["state"], "completed")

    def test_pipelined_run_waits_for_foreign_jobs_and_holds_bad_states(self):
        with mock.patch.object(execution, "status", side_effect=[
                self._two_jobs("compiled", "compiled"), self._two_jobs("rejected", "compiled")]), \
                mock.patch.object(base, "server_json", return_value={"queue_running": [[1, "other"]]}), \
                mock.patch.object(execution, "submit") as submit, \
                mock.patch.object(execution.time, "sleep"):
            with self.assertRaisesRegex(ValueError, "held"):
                execution.run_batch(self.root, self.batch, True, queue_depth=2)
        submit.assert_not_called()

    def test_cleanup_hint_prefers_repaint_then_overlay_then_failure(self):
        def evidence(*matches, state="verified"):
            return {"state": state, "matches": [dict(zip(("treatment", "decision"), match)) for match in matches]}
        self.assertEqual(execution.cleanup_hint(evidence(
            ("tight-crop-overlay-unremoved", "eraser; cleanup lama; final x"))), "repainted")
        self.assertEqual(execution.cleanup_hint(evidence(
            ("tight-crop-overlay-unremoved", "keep; cleanup none; final x"),
            ("original-enhancement-failed", "keep"))), "needs-cleanup")
        self.assertEqual(execution.cleanup_hint(evidence(("original-enhancement-failed", "keep"))),
                         "enhancement-failed")
        self.assertIsNone(execution.cleanup_hint(evidence(("tight-crop", "keep"))))
        self.assertIsNone(execution.cleanup_hint(evidence(
            ("tight-crop-overlay-unremoved", "keep"), state="pending")))

    def test_cleanup_batch_previews_then_writes_chunked_requests_once(self):
        sources = []
        for index in range(5):
            photo = self.root / "Various" / f"P{index}" / "gallery" / "image.png"
            photo.parent.mkdir(parents=True)
            Image.new("RGB", (20 + index, 30)).save(photo)
            sources.append({"path": photo.relative_to(self.root).as_posix(), "domain": "general",
                            "sha256": base.digest(photo.read_bytes()), "displayName": f"P {index}",
                            "cleanup": "needs-cleanup" if index < 5 else None})
        sources.append({**sources[0], "path": "Various/other.png", "cleanup": "repainted"})
        with mock.patch.object(execution, "gallery_sources", return_value=sources):
            preview = execution.cleanup_batch(self.root, samples=16, proposal_id="cleanup-test",
                                              seeds=list(range(80)))
            self.assertFalse(preview["applied"])
            self.assertEqual((preview["sourceCount"], preview["jobCount"]), (5, 80))
            self.assertEqual([item["jobs"] for item in preview["batches"]], [64, 16])
            self.assertFalse((self.root / "_generation" / "proposals").exists())
            applied = execution.cleanup_batch(self.root, samples=16, apply=True, proposal_id="cleanup-test",
                                              seeds=list(range(80)))
            folder = self.root / "_generation" / "proposals" / "cleanup-test"
            first = base.read_json(folder / "cleanup-test-01.json")
            self.assertEqual(first["batchId"], "cleanup-test-01")
            self.assertEqual(len(first["jobs"]), 64)
            self.assertEqual(base.read_json(folder / "proposal.json")["jobCount"], applied["jobCount"])
            with self.assertRaisesRegex(ValueError, "already exists"):
                execution.cleanup_batch(self.root, samples=16, apply=True, proposal_id="cleanup-test",
                                        seeds=list(range(80)))
            with self.assertRaisesRegex(ValueError, "hints"):
                execution.cleanup_batch(self.root, hints=("bogus",))
            with self.assertRaisesRegex(ValueError, "not available"):
                execution.cleanup_batch(self.root, recipes=("pending-0d-deluxe",))

    def test_manual_prefix_backup_and_repeat(self):
        workflows = self.root / "workflows"
        manual = workflows / "zz_shots" / "Angelica" / "edit.json"
        manual.parent.mkdir(parents=True)
        workflow = {"nodes": [{"type": "SaveImage", "widgets_values": [
            "angel-primes/shots/Angelica/0_Edit/0c_Cleanup/Angelica_cleanup"]},
            {"type": "Other", "widgets_values": ["preserve this exact text"]}]}
        before = base.encode(workflow)
        manual.write_bytes(before)
        with mock.patch.object(execution, "WORKFLOWS", workflows):
            preview = execution.manual_prefixes(self.root)
            self.assertFalse(preview["applied"])
            self.assertEqual(manual.read_bytes(), before)
            result = execution.manual_prefixes(self.root, True)
            saved = base.read_json(manual)
            self.assertEqual(saved["nodes"][1], workflow["nodes"][1])
            self.assertEqual(saved["nodes"][0]["widgets_values"][0],
                             "reference/manual/Angelica/0_Edit/0c_Cleanup/Angelica_cleanup")
            self.assertEqual((pathlib.Path(result["backup"]) / "zz_shots" / "Angelica" / "edit.json").read_bytes(), before)
            self.assertEqual(execution.manual_prefixes(self.root, True)["changedFiles"], 0)

    def test_source_discovery_uses_recorded_display_name_and_actual_path(self):
        photo = self.root / "Various" / "Known" / "gallery" / "image.png"
        photo.parent.mkdir(parents=True)
        Image.new("RGB", (20, 30)).save(photo)
        report = self.root / "_reports" / "library" / "people_gallery_review.html"
        report.parent.mkdir(parents=True)
        record = {"bucket": "Review", "folder": "Various/Known", "name": "image.png",
                  "contentSha256": base.digest(photo.read_bytes()),
                  "generationSource": "Various/Known/gallery/image.png",
                  "identityNames": {"characterName": None, "currentPersonName": "Recorded Person"},
                  "personId": "person-known"}
        import json
        report.write_text('<script id="review-data" type="application/json">' +
                          json.dumps([record]) + "</script>")
        sources = execution.gallery_sources(self.root)
        self.assertEqual(sources[0]["displayName"], "Recorded Person")
        self.assertEqual(sources[0]["path"], "Various/Known/gallery/image.png")
        photo.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "stale"):
            execution.gallery_sources(self.root)

    def test_pilot_prompts_preserve_clothing_and_do_not_copy_manual_body_controls(self):
        for recipe in execution.RECIPES:
            positive, negative = execution.pilot_prompts(recipe)
            self.assertIn("fully clothed", positive)
            self.assertIn("visible body proportions", positive)
            self.assertNotIn("Angelica", positive)
            self.assertIn("changed identity", negative)

    def test_selected_render_requires_provenance_not_just_matching_bytes(self):
        path = self.root / "_generation" / "selected" / "pilot" / "one" / "fake.png"
        path.parent.mkdir(parents=True)
        Image.new("RGB", (20, 30)).save(path)
        sha = base.digest(path.read_bytes())
        source = {"source": {"path": path.relative_to(self.root).as_posix(),
                              "sha256": sha, "domain": "general", "kind": "selected-render"}}
        with self.assertRaises(FileNotFoundError):
            base.inspect_source(self.root, source)
        path.with_suffix(".png.json").write_bytes(base.encode({
            "synthetic": True, "identityCoreEligible": True, "sha256": sha,
            "batchId": "pilot", "jobId": "one"}))
        with self.assertRaisesRegex(ValueError, "provenance"):
            base.inspect_source(self.root, source)

    def test_reconcile_matches_exact_intent_graph_without_post(self):
        self.job.update(state="submission-uncertain", clientId="one-client")
        self.save()
        graph = base.read_json(self.api_path)
        candidate = [1, "found-prompt", graph, {
            "client_id": "one-client",
            "extra_pnginfo": {"reference_batch": self.batch, "reference_job": "one"}}]
        with mock.patch.object(base, "server_json", side_effect=[
                {"queue_running": [candidate], "queue_pending": []}, {}]), \
                mock.patch.object(execution, "post_json") as post:
            result = execution.reconcile(self.root, self.batch, "one", True)
        self.assertEqual(result["promptId"], "found-prompt")
        self.assertFalse(result["submittedAgain"])
        post.assert_not_called()
        self.assertEqual(base.read_json(self.destination / "execution.json")["jobs"]["one"]["state"], "queued")

    def test_reconcile_no_match_keeps_uncertain_hold(self):
        self.job.update(state="submission-uncertain", clientId="one-client")
        self.save()
        with mock.patch.object(base, "server_json", side_effect=[{}, {}]):
            with self.assertRaisesRegex(ValueError, "0 exact scoped matches"):
                execution.reconcile(self.root, self.batch, "one", True)
        self.assertEqual(base.read_json(self.destination / "execution.json")["jobs"]["one"]["state"],
                         "submission-uncertain")


if __name__ == "__main__":
    unittest.main()
