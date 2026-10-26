import json
import pathlib
import tempfile
import unittest

from PIL import Image, PngImagePlugin

from tools.workflows import reference_execution as execution
from tools.workflows import reference_gallery as gallery
from tools.workflows import reference_outputs as outputs
from tools.workflows import reference_rendering as base


class ParseTests(unittest.TestCase):
    def test_manual_reference_and_unknown_layouts(self):
        manual = outputs.parse("Angel Primes/angel-primes/shots/Angelica/0_Edit/0d_Deluxe/Angelica_x_00001_.png")
        self.assertEqual((manual["workspace"], manual["stage"], manual["variant"], manual["subject"]),
                         ("Angel Primes", "0_Edit", "0d_Deluxe", "Angelica"))
        automated = outputs.parse(
            "Sovereign Females/reference/Ava_Stone/pilot-1/job-02/0_Edit/0c_Cleanup/Ava_Stone_0c_00001_.png")
        self.assertEqual((automated["subject"], automated["batch"], automated["job"], automated["variant"]),
                         ("Ava_Stone", "pilot-1", "job-02", "0c_Cleanup"))
        prefixed = outputs.parse("Sovereign Females/reference/manual/Angelica/1_Alpha/A_Pose/Angelica_00001_.png")
        self.assertEqual((prefixed["subject"], prefixed["stage"], prefixed["batch"]), ("Angelica", "1_Alpha", ""))
        loose = outputs.parse("Sovereign Territories/ComfyUI_00012_.png")
        self.assertEqual((loose["stage"], loose["subject"]), ("", "ComfyUI"))
        legacy = outputs.parse("Sovereign Territories/drakn-sisters/Draknara/poses/Draknara_Qwen_00006_.png")
        self.assertEqual((legacy["stage"], legacy["variant"], legacy["subject"]), ("", "poses", "Draknara"))


class PullTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base_dir = pathlib.Path(temporary.name)
        self.root = base_dir / "library"
        self.comfy = base_dir / "outputs"
        self.root.mkdir()
        relative = "Sovereign Females/reference/Ava_Stone/pilot-1/job-02/0_Edit/0c_Cleanup/Ava_Stone_00001_.png"
        self.output = self.comfy / pathlib.Path(relative)
        self.output.parent.mkdir(parents=True)
        info = PngImagePlugin.PngInfo()
        info.add_text("prompt", json.dumps({"9": {"class_type": "SaveImage",
                                                  "inputs": {"filename_prefix": "reference/Ava_Stone/x"}}}))
        info.add_text("reference_batch", '"pilot-1"')
        Image.new("RGBA", (400, 600), (10, 20, 30, 255)).save(self.output, pnginfo=info)
        self.relative = relative
        self.comfy = self.comfy.resolve()

    def manifest(self, **extra):
        stat = self.output.stat()
        path = self.root.parent / "pull.json"
        path.write_text(json.dumps({"schemaVersion": 1, "outputRoot": str(self.comfy), "items": [
            {"output": self.relative, "size": stat.st_size, "mtime": int(stat.st_mtime), **extra}]}))
        return path

    def test_preview_writes_nothing_then_apply_pads_names_and_records_lineage(self):
        manifest = self.manifest(displayName="Ava Stone", personId="person-ava")
        preview = outputs.pull(self.root, manifest, self.comfy)
        self.assertEqual(preview["items"][0]["state"], "pull-preview")
        self.assertFalse((self.root / "_generation").exists())
        result = outputs.pull(self.root, manifest, self.comfy, apply=True)
        destination = self.root / result["items"][0]["destination"]
        self.assertRegex(destination.name, r"^ava_stone_comfy_0c_cleanup_[0-9a-f]{8}\.png$")
        self.assertEqual(destination.parent.relative_to(self.root).as_posix(), "_generation/library/0_Edit/0c_Cleanup")
        self.assertEqual(destination.read_bytes(), self.output.read_bytes())
        sidecar = base.read_json(destination.with_suffix(".png.json"))
        self.assertEqual((sidecar["kind"], sidecar["synthetic"], sidecar["identityCoreEligible"]),
                         ("pulled-render", True, False))
        self.assertEqual((sidecar["personId"], sidecar["comfy"]["batchId"]), ("person-ava", "pilot-1"))
        self.assertEqual(sidecar["comfy"]["filenamePrefixes"], ["reference/Ava_Stone/x"])
        with Image.open(destination.with_name(sidecar["padded"]["file"])) as padded:
            self.assertEqual(padded.size, (944, 1104))
            self.assertEqual(padded.getpixel((0, 0)), outputs.CREAM)
        again = outputs.pull(self.root, manifest, self.comfy, apply=True)
        self.assertEqual(again["items"][0]["state"], "already-pulled")
        source = {"path": destination.relative_to(self.root).as_posix(), "kind": "pulled-render",
                  "sha256": sidecar["sha256"], "domain": "general"}
        base.inspect_source(self.root, {"source": source})
        cleaned = gallery._validate_sources(self.root, [{**source, "displayName": "Ava Stone"}])
        self.assertEqual(cleaned[0]["kind"], "pulled-render")

    def test_pulled_render_is_listed_as_a_rendering_source(self):
        outputs.pull(self.root, self.manifest(displayName="Ava Stone"), self.comfy, apply=True)
        report = self.root / "_reports" / "library" / "people_gallery_review.html"
        report.parent.mkdir(parents=True)
        report.write_text('<script id="review-data" type="application/json">[]</script>')
        listed = execution.gallery_sources(self.root)
        self.assertEqual([(item["kind"], item["displayName"]) for item in listed], [("pulled-render", "Ava Stone")])

    def test_changed_output_manifest_root_and_tampered_sidecar_refuse(self):
        manifest = self.manifest()
        self.output.write_bytes(self.output.read_bytes() + b"\0")
        with self.assertRaisesRegex(ValueError, "changed since"):
            outputs.pull(self.root, manifest, self.comfy)
        with self.assertRaisesRegex(ValueError, "output root differs"):
            outputs.pull(self.root, self.manifest(), self.root.resolve())
        result = outputs.pull(self.root, self.manifest(), self.comfy, apply=True)
        destination = self.root / result["items"][0]["destination"]
        sidecar = destination.with_suffix(".png.json")
        record = base.read_json(sidecar)
        sidecar.write_bytes(base.encode({**record, "identityCoreEligible": True}))
        with self.assertRaisesRegex(ValueError, "provenance"):
            base.inspect_source(self.root, {"source": {
                "path": destination.relative_to(self.root).as_posix(), "kind": "pulled-render",
                "sha256": record["sha256"], "domain": "general"}})

    def test_unsafe_manifest_paths_refuse(self):
        stat = self.output.stat()
        path = self.root.parent / "bad.json"
        for output in ("../escape.png", "Sovereign Females/notes.txt"):
            path.write_text(json.dumps({"schemaVersion": 1, "outputRoot": str(self.comfy), "items": [
                {"output": output, "size": stat.st_size, "mtime": int(stat.st_mtime)}]}))
            with self.assertRaises(ValueError):
                outputs.pull(self.root, path, self.comfy)

    def test_outputs_page_preview_apply_and_check(self):
        preview = outputs.publish(self.root, self.comfy)
        self.assertEqual((preview["images"], preview["applied"]), (1, False))
        self.assertFalse((self.root / "_generation" / "outputs.html").exists())
        outputs.publish(self.root, self.comfy, apply=True)
        page = (self.root / "_generation" / "outputs.html").read_text(encoding="utf-8")
        self.assertIn('aria-current="page">Outputs</a>', page)
        self.assertIn("Export pull manifest", page)
        self.assertNotIn("<script>alert", page)
        self.assertTrue(outputs.publish(self.root, self.comfy, check=True)["current"])
        self.assertEqual(outputs.publish(self.root, self.comfy, ["Missing"])["images"], 0)


if __name__ == "__main__":
    unittest.main()
