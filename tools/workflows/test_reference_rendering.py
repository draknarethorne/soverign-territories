"""Offline request isolation and read-only launcher behavior."""
import contextlib
import copy
import io
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

from PIL import Image

from tools.workflows import reference_rendering as render


class ReferenceRenderingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.source = self.root / "Various" / "gallery" / "photo.png"
        self.source.parent.mkdir(parents=True)
        Image.new("RGB", (20, 30), "blue").save(self.source)
        self.request = {
            "schemaVersion": 1, "batchId": "first-test", "workspace": "Sovereign Females",
            "jobs": [{
                "id": "one", "source": {
                    "path": "Various/gallery/photo.png", "domain": "general",
                    "sha256": render.digest(self.source.read_bytes()),
                },
                "workflowMode": "reference", "recipe": "qwen-clothed-apose-v1",
                "profile": "reference-faithful", "seed": 42,
            }],
        }

    def test_preview_has_no_writes(self):
        before = set(self.root.rglob("*"))
        run, artifacts = render.request_plan(self.request, self.root)
        self.assertEqual(run["state"], "inputs-only-not-render-ready")
        self.assertEqual(set(self.root.rglob("*")), before)
        self.assertEqual(artifacts["jobs/one/input/source.png"], self.source.read_bytes())

    def test_prepare_repeat_check_after_source_move(self):
        run = render.prepare(self.request, self.root)
        self.assertEqual(render.prepare(self.request, self.root), run)
        self.source.rename(self.source.with_name("renamed.png"))
        self.assertEqual(render.check(self.root, "first-test"), run)

    def test_frozen_configuration_receipt_survives_later_configuration_changes(self):
        run = render.prepare(self.request, self.root)
        receipt = run["configurationReceipt"]
        self.assertEqual(receipt["resolvedPaths"]["libraryRoot"], str(self.root.resolve()))
        self.assertEqual(receipt["resolvedPaths"]["referenceRunDirectory"],
                         str(render.run_path(self.root, "first-test").resolve()))
        self.assertEqual(len(receipt["sourceConfigurationSha256"]), 64)
        self.assertEqual(len(receipt["effectiveConfigurationSha256"]), 64)
        cfg = copy.deepcopy(render.cw.load_cfg())
        cfg["storageRoots"]["reports"] = "_changed_reports"
        with mock.patch.object(render.cw, "load_cfg", return_value=cfg):
            self.assertEqual(render.check(self.root, "first-test"), run)
            self.assertEqual(render.prepare(self.request, self.root), run)

    def test_legacy_frozen_run_without_configuration_receipt_still_checks_and_repeats(self):
        run = render.prepare(self.request, self.root)
        run.pop("configurationReceipt")
        manifest = render.run_path(self.root, "first-test") / "run.json"
        manifest.write_bytes(render.encode(run))
        self.assertEqual(render.check(self.root, "first-test"), run)
        self.assertEqual(render.prepare(self.request, self.root), run)
        self.assertEqual(manifest.read_bytes(), render.encode(run))

    def test_malformed_frozen_configuration_receipt_is_not_treated_as_legacy(self):
        run = render.prepare(self.request, self.root)
        manifest = render.run_path(self.root, "first-test") / "run.json"
        for receipt in (None, {}, {**run["configurationReceipt"], "sourceConfigurationSha256": "bad"}):
            with self.subTest(receipt=receipt):
                manifest.write_bytes(render.encode({**run, "configurationReceipt": receipt}))
                with self.assertRaises(render.jsonschema.ValidationError):
                    render.check(self.root, "first-test")
        receipt = copy.deepcopy(run["configurationReceipt"])
        receipt["resolvedPaths"]["referenceRunDirectory"] = str(self.root)
        manifest.write_bytes(render.encode({**run, "configurationReceipt": receipt}))
        with self.assertRaisesRegex(ValueError, "receipt paths"):
            render.check(self.root, "first-test")

    def test_configured_generation_root_routes_frozen_batch(self):
        config = render.cw.load_cfg()
        config = {
            **config,
            "storageRoots": {
                **config["storageRoots"],
                "generation": "_generated",
            },
        }
        with mock.patch.object(render.cw, "load_cfg", return_value=config):
            run = render.prepare(self.request, self.root)
            destination = self.root / "_generated" / "reference" / "first-test"
            self.assertEqual(render.run_path(self.root, "first-test"), destination)
            self.assertTrue((destination / "request.json").is_file())
            self.assertEqual(render.check(self.root, "first-test"), run)

    def test_source_change_refused_before_writes(self):
        self.source.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "hash changed"):
            render.prepare(self.request, self.root)
        self.assertFalse((self.root / "_generation").exists())

    def test_duplicate_ids_refused(self):
        self.request["jobs"].append(copy.deepcopy(self.request["jobs"][0]))
        with self.assertRaisesRegex(ValueError, "unique"):
            render.prepare(self.request, self.root)

    def test_all_sources_validate_before_staging(self):
        job = copy.deepcopy(self.request["jobs"][0])
        job["id"] = "two"
        job["source"]["sha256"] = "0" * 64
        self.request["jobs"].append(job)
        with self.assertRaisesRegex(ValueError, "hash changed"):
            render.prepare(self.request, self.root)
        self.assertFalse((self.root / "_generation").exists())

    def test_paths_and_domain(self):
        for path in ("Various/gallery/../photo.png", "../photo.png",
                     "Various/gallery/CON.png", "Various/gallery/photo.png:stream",
                     "_generation/reference/photo.png"):
            with self.subTest(path=path):
                request = copy.deepcopy(self.request)
                request["jobs"][0]["source"]["path"] = path
                with self.assertRaises(ValueError):
                    render.prepare(request, self.root)
        self.request["jobs"][0]["source"]["domain"] = "artists"
        with self.assertRaisesRegex(ValueError, "domain mismatch"):
            render.prepare(self.request, self.root)

    def test_profile_mode_conflict(self):
        self.request["jobs"][0]["workflowMode"] = "character"
        with self.assertRaises(render.jsonschema.ValidationError):
            render.request_plan(self.request, self.root)
        self.request["jobs"][0]["profile"] = "character-defined"
        self.assertEqual(render.request_plan(self.request, self.root)[0]["jobs"][0]["profile"],
                         "character-defined")

    def test_tamper_and_extra_file(self):
        render.prepare(self.request, self.root)
        destination = render.run_path(self.root, "first-test")
        extra = destination / "unknown.txt"
        extra.write_text("keep me")
        with self.assertRaisesRegex(ValueError, "inventory"):
            render.check(self.root, "first-test")
        extra.unlink()
        source = destination / "jobs" / "one" / "input" / "source.png"
        source.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "hash changed"):
            render.check(self.root, "first-test")

    def test_changed_request_cannot_reuse_batch(self):
        render.prepare(self.request, self.root)
        self.request["jobs"][0]["seed"] = 99
        with self.assertRaisesRegex(ValueError, "different request"):
            render.prepare(self.request, self.root)

    def test_same_basename_isolated(self):
        second = self.root / "Prospects" / "Known" / "gallery" / "photo.png"
        second.parent.mkdir(parents=True)
        Image.new("RGB", (20, 30), "red").save(second)
        job = copy.deepcopy(self.request["jobs"][0])
        job["id"] = "two"
        job["source"].update(path="Prospects/Known/gallery/photo.png",
                             sha256=render.digest(second.read_bytes()))
        self.request["jobs"].append(job)
        run = render.prepare(self.request, self.root)
        self.assertNotEqual(run["jobs"][0]["sha256"], run["jobs"][1]["sha256"])

    def test_duplicate_json_keys_refused(self):
        path = self.root / "bad.json"
        path.write_text('{"jobs": [], "jobs": []}')
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            render.read_json(path)

    def test_probe_rejects_nonlocal_and_ambiguous_endpoints(self):
        for endpoint in ("http://example.com:8188", "http://127.0.0.1",
                         "http://user:pass@127.0.0.1:8188", "http://127.0.0.1:8188/prompt",
                         "http://127.0.0.1:8188/?token=hidden"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                render.probe_server(endpoint, r"B:\Inputs\Test", r"B:\Outputs\Test")

    def test_probe_reports_root_mismatch_and_capabilities_without_writes(self):
        stats = {"system": {"comfyui_version": "test", "argv": [
            "main.py", "--input-directory", r"B:\Inputs\Typo",
            "--output-directory", r"B:\Outputs\Test",
        ]}}
        objects = {"LoadImage": {}, "UNETLoader": {
            "input": {"required": {"unet_name": [["qwen-test.safetensors"]]}}}}
        with mock.patch.object(render, "server_json", side_effect=[stats, objects]) as reads:
            result = render.probe_server("http://127.0.0.1:8188",
                                         r"B:\Inputs\Test", r"B:\Outputs\Test",
                                         ["LoadImage", "MissingNode"])
        self.assertEqual(result["state"], "blocked")
        self.assertEqual(len(result["blockers"]), 2)
        self.assertEqual(result["modelChoices"]["UNETLoader"], ["qwen-test.safetensors"])
        self.assertEqual([call.args[2] for call in reads.call_args_list],
                         ["/system_stats", "/object_info"])

    def test_probe_readonly_success_and_missing_argv_refusal(self):
        stats = {"system": {"argv": [
            "main.py", "--input-directory=B:\\Inputs\\Test",
            "--output-directory=B:\\Outputs\\Test",
        ]}}
        with mock.patch.object(render, "server_json", side_effect=[stats, {"LoadImage": {}}]):
            result = render.probe_server("http://127.0.0.1:8188",
                                         r"B:\Inputs\Test", r"B:\Outputs\Test", ["LoadImage"])
        self.assertEqual(result["state"], "communications-checked-not-render-ready")
        with mock.patch.object(render, "server_json", return_value={"system": {}}):
            with self.assertRaisesRegex(ValueError, "argv"):
                render.probe_server("http://127.0.0.1:8188", r"B:\Inputs\Test", r"B:\Outputs\Test")

    def test_probe_http_client_uses_only_bounded_get(self):
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"system": {}}'
        opener = mock.Mock()
        opener.open.return_value = response
        self.assertEqual(render.server_json(opener, "http://127.0.0.1:8188", "/system_stats"),
                         {"system": {}})
        opener.open.assert_called_once_with("http://127.0.0.1:8188/system_stats", timeout=5)
        response.__enter__.return_value.read.assert_called_once_with(16 * 1024 * 1024 + 1)
        with self.assertRaisesRegex(ValueError, "redirects"):
            render.NoRedirect().redirect_request(None, None, 302, "", {}, "http://example.com")

    def test_probe_connection_failure_is_explicit(self):
        with mock.patch.object(render, "server_json", side_effect=TimeoutError("fixture timeout")):
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                result = render.main(["probe", "http://127.0.0.1:8188",
                                      "--input-root", r"B:\Inputs\Test",
                                      "--output-root", r"B:\Outputs\Test"])
        self.assertEqual(result, 1)
        self.assertIn("fixture timeout", errors.getvalue())

    def test_probe_malformed_loader_is_refused(self):
        stats = {"system": {"argv": []}}
        with mock.patch.object(render, "server_json", side_effect=[
                stats, {"UNETLoader": {"input": "invalid"}}]):
            with self.assertRaisesRegex(ValueError, "Malformed"):
                render.probe_server("http://127.0.0.1:8188", r"B:\Inputs\Test", r"B:\Outputs\Test")

    def test_preview_checks_windows_destination_names(self):
        self.request["jobs"][0]["id"] = "con"
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            render.request_plan(self.request, self.root)

    def test_failed_publication_removes_only_staging(self):
        with mock.patch.object(render.os, "rename", side_effect=PermissionError("fixture lock")):
            with self.assertRaisesRegex(PermissionError, "fixture lock"):
                render.prepare(self.request, self.root)
        self.assertEqual(list((self.root / "_generation" / "reference").iterdir()), [])
        temporary_root = render.cw.storage_root(render.cw.load_cfg(), "temporary", root=self.root)
        self.assertEqual(list(temporary_root.glob(".reference-*")), [])
        self.assertTrue(self.source.exists())

    def test_check_does_not_write(self):
        render.prepare(self.request, self.root)
        before = {str(path): (path.stat().st_mtime_ns, path.read_bytes())
                  for path in self.root.rglob("*") if path.is_file()}
        render.check(self.root, "first-test")
        after = {str(path): (path.stat().st_mtime_ns, path.read_bytes())
                 for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_manifest_tamper_refused(self):
        render.prepare(self.request, self.root)
        path = render.run_path(self.root, "first-test") / "run.json"
        evidence = render.read_json(path)
        evidence["jobs"][0]["seed"] = 99
        path.write_bytes(render.encode(evidence))
        with self.assertRaisesRegex(ValueError, "evidence changed"):
            render.check(self.root, "first-test")

    @unittest.skipUnless(__import__("os").name == "nt", "Windows junction")
    def test_junction_source_and_destination_refused(self):
        target = self.root / "Models" / "Known"
        target.mkdir(parents=True)
        junction = self.root / "Various" / "linked"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(target)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        try:
            with self.assertRaisesRegex(ValueError, "Linked"):
                render.safe_path(self.root, "Various/linked/gallery/photo.png")
        finally:
            junction.rmdir()

    def test_cli_preview_prepare_check(self):
        path = self.root / "batch.json"
        path.write_text(json.dumps(self.request))
        for args in (
            ["preview", str(path), "--dry-run"],
            ["prepare", str(path), "--apply"],
            ["check", "first-test", "--check"],
        ):
            with self.subTest(args=args), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(render.main([*args, "--root", str(self.root)]), 0)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(render.main(["preview", str(path), "--apply",
                                          "--root", str(self.root)]), 1)

    def test_cli_new_command_flags_are_scoped(self):
        comfy = self.root / "comfy-outputs"
        comfy.mkdir()
        refused = (
            ["status", "first-test", "--queue-depth", "2"],
            ["outputs", "--recipe", "manual-0c-cleanup-basic"],
            ["run", "first-test", "--workspace", "Sovereign Females"],
            ["cleanup-batch", "--endpoint", "http://127.0.0.1:8188"],
            ["outputs", "--apply", "--check", "--output-root", str(comfy)],
            ["pull", "--output-root", str(comfy)],
            ["outputs", "--sources", "scan.json"],
            ["cleanup-batch", "--inputs", str(self.root)],
            ["status", "first-test", "--id", "scan-x"],
            ["overlay-scan"],
            ["outputs", "--per-person", "2"],
            ["cleanup-batch", "--per-person", "2", "--hint", "needs-cleanup"],
            ["status", "first-test", "--batch", "other"],
            ["compare", "first-test", "--apply", "--check"],
        )
        for args in refused:
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()) as error:
                self.assertEqual(render.main([*args, "--root", str(self.root)]), 1)
                self.assertIn("refused", error.getvalue())
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(render.main(["outputs", "--dry-run", "--output-root", str(comfy),
                                          "--root", str(self.root)]), 0)
        self.assertEqual(json.loads(output.getvalue())["images"], 0)
        self.assertFalse((self.root / "_generation" / "outputs.html").exists())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(render.main(["outputs", "--check", "--output-root", str(comfy),
                                          "--root", str(self.root)]), 1)

    def test_cli_comparison_previews_applies_and_checks_frozen_sources(self):
        render.prepare(self.request, self.root)
        args = ["compare", "first-test", "--root", str(self.root)]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(render.main([*args, "--dry-run"]), 0)
            self.assertEqual(render.main([*args, "--check"]), 1)
            self.assertFalse((self.root / "_generation" / "comparison.html").exists())
            self.assertEqual(render.main([*args, "--apply"]), 0)
            self.assertEqual(render.main([*args, "--check"]), 0)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(render.main([*args, "--batch", "first-test"]), 1)

    @unittest.skipUnless(__import__("os").name == "nt", "Windows launcher")
    def test_actual_launcher_readonly(self):
        path = self.root / "batch.json"
        path.write_text(json.dumps(self.request))
        result = subprocess.run(
            ["cmd", "/c", str(render.ROOT / "bin" / "render-reference.cmd"),
             "preview", str(path), "--root", str(self.root), "--dry-run"],
            cwd=render.ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Inputs only", result.stdout)
        self.assertFalse((self.root / "_generation").exists())
        render.prepare(self.request, self.root)
        destination = render.run_path(self.root, self.request["batchId"])
        before = {item: item.read_bytes() for item in destination.rglob("*") if item.is_file()}
        result = subprocess.run(
            ["cmd", "/c", str(render.ROOT / "bin" / "render-reference.cmd"),
             "check", self.request["batchId"], "--root", str(self.root), "--check"],
            cwd=render.ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            {item: item.read_bytes() for item in destination.rglob("*") if item.is_file()}, before,
        )


if __name__ == "__main__":
    unittest.main()
