"""Final-score precision, bounded comparison selection and report-only safety."""
import copy
import json
import math
import pathlib
import tempfile
import unittest
from unittest import mock

import numpy as np
from PIL import Image

from tools.art import likeness_review_packet as cli
from tools.art.likeness_library import review_packet, shadow

ROOT = pathlib.Path(__file__).resolve().parents[4]


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / "tmp")
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        self.folders = ["Angels/angelica"] * 3 + ["Models/Mira Vale"] * 3 + ["Models/Outside"] * 2
        self.vectors = {
            str(index): np.array([math.cos(angle), math.sin(angle)])
            for index, angle in enumerate(np.linspace(0, 1.5, 8))
        }
        self.photos, self.audit, published = [], [], []
        self.cache = {"emb": {}}
        for index, folder in enumerate(self.folders):
            pid = str(index)
            relative = f"{folder}/gallery/{pid}.png"
            source = self.root / pathlib.PurePosixPath(relative)
            source.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (120, 180), (index * 30, 50, 100)).save(source)
            published.append({"path": relative, "sha256": shadow.digest(source)})
            self.photos.append({
                "photoId": pid, "destination": relative, "source": relative,
                "preparedSHA256": pid,
            })
            self.cache["emb"][pid] = {
                "box": [.3, .2, .3, .2], "alignmentEvidence": {"sourceSha256": pid},
            }
        for pid, vector in self.vectors.items():
            folder = self.folders[int(pid)]
            same = [other for other in self.vectors if self.folders[int(other)] == folder and other != pid]
            own = float(vector @ shadow.nz(np.sum([self.vectors[other] for other in same], axis=0)))
            rivals = []
            for rival in sorted(set(self.folders) - {folder}):
                values = [value for other, value in self.vectors.items() if self.folders[int(other)] == rival]
                rivals.append({"folder": rival, "score": round(float(vector @ shadow.nz(np.mean(values, axis=0))), 6)})
            rivals.sort(key=lambda row: (-row["score"], row["folder"]))
            self.audit.append({
                **self.photos[int(pid)], "ownScore": round(own, 6), "rivals": rivals,
                "coreMember": True, "qualityEligible": True, "reason": "saved baseline",
                "protected": False, "anchor": False,
            })
        self.run = {
            "photos": self.photos, "finalMembershipAudit": {"rows": self.audit},
            "workingRoot": str(self.root), "publishedFiles": published,
        }
        self.scope = {
            "seeds": {"angelica": ["Angels/angelica"], "vale": ["Models/Mira Vale"]},
            "photos": self.photos, "identityCount": 3, "photoCount": 8,
        }
        self.binding = {"runSHA256": "frozen", "sourceRun": str(self.root),
                        "shadowReceiptSHA256": "shadow", "scopeSHA256": "scope"}

    def packet(self):
        return review_packet.build_packet(self.run, self.vectors, self.scope, self.binding)

    def test_exact_six_decimal_own_and_rival_arithmetic(self):
        parity, groups = review_packet.final_score_parity(self.run, self.vectors)
        self.assertEqual(parity["ownScores"], 8)
        self.assertEqual(parity["rivalScores"], 16)
        self.assertEqual(parity["coreCount"], 3)
        self.assertEqual(groups["Models/Outside"], ["6", "7"])
        self.assertIn("NOT independently replayed", parity["boundary"])
        self.audit[0]["ownScore"] += .001
        with self.assertRaisesRegex(ValueError, "final own arithmetic differs"):
            review_packet.final_score_parity(self.run, self.vectors)

    def test_rival_score_drift_refuses(self):
        self.audit[0]["rivals"][0]["score"] += .001
        with self.assertRaisesRegex(ValueError, "final rival arithmetic differs"):
            review_packet.final_score_parity(self.run, self.vectors)

    def test_all_seed_identities_have_bounded_cases_and_no_self_references(self):
        packet = self.packet()
        self.assertEqual(len(packet["seedIdentities"]), 2)
        self.assertTrue(all(row["caseIds"] for row in packet["seedIdentities"]))
        self.assertLessEqual(len(packet["cases"]), 7)
        for case in packet["cases"]:
            for panel in case["panels"]:
                self.assertNotIn(case["photoId"], [ref["photoId"] for ref in panel["references"]])
                self.assertLessEqual(len(panel["references"]), 3)
        self.assertIn("Unallocated", packet["heldOut"])
        self.assertIn("unreviewed", packet["labels"])

    def test_selection_reproducible_without_input_mutation(self):
        before = copy.deepcopy(self.run)
        first = self.packet()
        self.run["photos"].reverse()
        self.run["finalMembershipAudit"]["rows"].reverse()
        second = self.packet()
        self.assertEqual(first, second)
        self.run["photos"].reverse()
        self.run["finalMembershipAudit"]["rows"].reverse()
        self.assertEqual(self.run, before)

    def test_neighbour_count_is_not_reference_competition_limit(self):
        packet = review_packet.build_packet(self.run, self.vectors, self.scope, self.binding, neighbours=0)
        self.assertTrue(all(case["folder"] != "Models/Outside" for case in packet["cases"]))
        self.assertEqual(packet["finalScoreParity"]["coreCount"], 3)

    def test_reference_choice_uses_distinct_core_ids_and_anchor(self):
        rows = {row["photoId"]: row for row in self.audit}
        rows["1"]["anchor"] = True
        selected = review_packet.choose_references(
            "Angels/angelica", {"Angels/angelica": ["0", "1", "2"]},
            rows, self.vectors, exclude="2",
        )
        self.assertEqual(selected[0], "1")
        self.assertEqual(len(selected), len(set(selected)))
        self.assertEqual(review_packet.choose_references(
            "singleton", {"singleton": ["2"]}, rows, self.vectors, exclude="2"), [])

    def test_safe_paths_refuse_escape_and_absolute_paths(self):
        for value in ("../outside", "/absolute", "C:/outside", "Models\\other.png"):
            with self.assertRaises(ValueError):
                review_packet.safe_path(self.root, value)

    def test_preview_hashes_sources_but_creates_nothing(self):
        packet = self.packet()
        out = self.root / "not-created"
        images, outputs = review_packet.image_assets(packet, self.run, self.cache, out)
        self.assertEqual(len(images), len(packet["usedPhotoIds"]))
        self.assertEqual(outputs, {})
        self.assertFalse(out.exists())

    def test_write_only_bounded_report_images_and_html_escapes(self):
        packet = self.packet()
        out = self.root / "report"
        images, outputs = review_packet.image_assets(packet, self.run, self.cache, out, write=True)
        self.assertEqual(len(outputs), len(images) * 2)
        for name, digest in outputs.items():
            self.assertEqual(shadow.digest(out / name), digest)
            with Image.open(out / name) as image:
                self.assertLessEqual(image.width, 360)
                self.assertLessEqual(image.height, 480)
        packet["images"], packet["packetSHA256"] = images, "packet"
        packet["cases"][0]["reason"] = "<script>unsafe</script>"
        page = review_packet.render(packet)
        self.assertIn("&lt;script&gt;unsafe&lt;/script&gt;", page)
        self.assertNotIn("<script>unsafe</script>", page)
        self.assertIn("No photos have moved", page)
        self.assertIn("Export labels", page)
        self.assertIn('id="export-json"', page)
        self.assertIn("Downloads may be blocked", page)
        self.assertIn('"unreviewed"', page)

    def test_changed_source_or_unbound_face_box_refuses(self):
        packet = self.packet()
        source = self.root / pathlib.PurePosixPath(self.photos[0]["destination"])
        source.write_bytes(b"edited")
        with self.assertRaisesRegex(ValueError, "changed since baseline"):
            review_packet.image_assets(packet, self.run, self.cache, self.root / "report")

    def test_load_experiment_refuses_corrupt_output(self):
        experiment = self.root / "shadow"
        experiment.mkdir()
        (experiment / "receipt.json").write_text(json.dumps({
            "outputs": {"scope.json": "wrong", "experiment.json": "wrong"},
        }), encoding="utf-8")
        (experiment / "scope.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "shadow evidence changed"):
            review_packet.load_experiment(experiment)

    def test_report_output_cannot_be_library_or_tmp_or_reports_root(self):
        for path in (str(self.root), str(ROOT / "reports" / "likeness-reassessment"), "relative"):
            with self.assertRaises(ValueError):
                cli.output_path(path)
        expected = ROOT / "reports" / "likeness-reassessment" / "unit-output-not-created"
        self.assertEqual(cli.output_path(str(expected)), expected)
        self.assertFalse(expected.exists())

    def test_cli_preview_does_not_create_report_or_decode_thumbnails(self):
        out = self.root / "not-created"
        (self.root / "likeness-cache.json").write_text(json.dumps(self.cache), encoding="utf-8")
        with mock.patch.object(cli, "output_path", return_value=out):
            with mock.patch.object(review_packet, "load_experiment",
                                   return_value=(self.run, self.vectors, self.scope, self.binding)):
                with mock.patch.object(review_packet, "face_thumbnail") as thumb:
                    result = cli.main(["--experiment", str(self.root), "--out", str(out), "--dry-run"])
        self.assertEqual(result, 0)
        thumb.assert_not_called()
        self.assertFalse(out.exists())

    def test_cli_apply_check_repeat_and_corruption_without_source_writes(self):
        experiment = self.root / "experiment"
        experiment.mkdir()
        outputs = {}
        for name in ("scope.json", "experiment.json"):
            (experiment / name).write_text("{}", encoding="utf-8")
            outputs[name] = shadow.digest(experiment / name)
        (experiment / "receipt.json").write_text(json.dumps({
            "provenance": {"inputs": {}}, "outputs": outputs,
        }), encoding="utf-8")
        self.binding["shadowReceiptSHA256"] = shadow.digest(experiment / "receipt.json")
        (self.root / "likeness-cache.json").write_text(json.dumps(self.cache), encoding="utf-8")
        out = self.root / "report"
        arguments = ["--experiment", str(experiment), "--out", str(out)]
        before = {row["path"]: shadow.digest(self.root / pathlib.PurePosixPath(row["path"]))
                  for row in self.run["publishedFiles"]}
        with mock.patch.object(cli, "output_path", return_value=out):
            with mock.patch.object(review_packet, "load_experiment",
                                   return_value=(self.run, self.vectors, self.scope, self.binding)):
                self.assertEqual(cli.main([*arguments, "--apply"]), 0)
                self.assertEqual(cli.main([*arguments, "--check"]), 0)
                with mock.patch.object(review_packet, "image_assets") as images:
                    self.assertEqual(cli.main([*arguments, "--apply"]), 0)
                    images.assert_not_called()
                (out / "index.html").write_text("edited", encoding="utf-8")
                self.assertEqual(cli.main([*arguments, "--check"]), 1)
        self.assertEqual(before, {
            row["path"]: shadow.digest(self.root / pathlib.PurePosixPath(row["path"]))
            for row in self.run["publishedFiles"]
        })


if __name__ == "__main__":
    unittest.main()
