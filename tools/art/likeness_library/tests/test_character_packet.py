"""Character-intent selection, answer validation and report-only launcher checks."""
import copy
import functools
import json
import unittest
from unittest import mock

from tools.art import likeness_character_packet as cli
from tools.art.likeness_library import character_packet, shadow
from tools.art.likeness_library.tests import test_review_packet


class CharacterTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_review_packet.PacketTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.characters = (
            ("Angels/angelica", "Disputed identity", 6),
            ("Models/Mira Vale", "Contrast", 6),
        )
        self.effective = {
            "pairs": [{"photoIds": ["0", "1"], "label": "different"}],
            "summary": {"pairCount": 1},
        }

    def packet(self):
        return character_packet.build_packet(
            self.fixture.run, self.fixture.vectors, self.effective,
            self.fixture.binding, characters=self.characters,
        )

    def answers(self, packet):
        return {
            "schemaVersion": 1, "kind": "character-reference-answers",
            "packetSHA256": packet["packetSHA256"], "binding": packet["binding"],
            "characters": [
                {"folder": group["folder"], "decisions": [
                    {"photoId": card["photoId"], "choice": "unreviewed"} for card in group["cards"]
                ]} for group in packet["characters"]
            ],
        }

    def test_selection_preserves_disputed_and_anchor_evidence_without_prefilling(self):
        self.fixture.photos[2]["castSeedAnchor"] = True
        packet = self.packet()
        cards = packet["characters"][0]["cards"]
        self.assertTrue({"0", "1", "2"} <= {card["photoId"] for card in cards})
        self.assertTrue(all(card["selection"] == "unreviewed" for card in cards))
        self.assertTrue(any(card["currentFolder"] != "Angels/angelica" for card in cards))
        self.assertEqual(len(packet["characters"]), 2)

    def test_selection_is_order_independent_and_does_not_mutate_inputs(self):
        before = copy.deepcopy(self.fixture.run)
        first = self.packet()
        self.fixture.run["photos"].reverse()
        self.fixture.run["finalMembershipAudit"]["rows"].reverse()
        self.assertEqual(first, self.packet())
        self.fixture.run["photos"].reverse()
        self.fixture.run["finalMembershipAudit"]["rows"].reverse()
        self.assertEqual(before, self.fixture.run)

    def test_missing_character_and_mandatory_evidence_overflow_refuse(self):
        with self.assertRaisesRegex(ValueError, "no eligible"):
            character_packet.build_packet(
                self.fixture.run, self.fixture.vectors, self.effective, {},
                characters=(("Sisters/missing", "Missing", 8),),
            )
        with self.assertRaisesRegex(ValueError, "budget"):
            character_packet.build_packet(
                self.fixture.run, self.fixture.vectors, self.effective, {},
                characters=(("Angels/angelica", "Too narrow", 3),),
            )

    def test_answers_require_exact_binding_character_photo_coverage_and_choices(self):
        packet = self.packet()
        packet["packetSHA256"] = "bound"
        answers = self.answers(packet)
        self.assertEqual(character_packet.validate_answers(packet, answers), answers)
        for mutate in (
            lambda value: value.update(schemaVersion=True),
            lambda value: value.update(packetSHA256="other"),
            lambda value: value["characters"].pop(),
            lambda value: value["characters"].append(value["characters"][0]),
            lambda value: value["characters"][0]["decisions"].pop(),
            lambda value: value["characters"][0]["decisions"][0].update(choice="automatic"),
            lambda value: value["characters"][0]["decisions"][0].update(photoId="not-displayed"),
            lambda value: value["characters"][0].update(decisions=None),
            lambda value: value["characters"].__setitem__(0, None),
        ):
            bad = copy.deepcopy(answers)
            mutate(bad)
            with self.assertRaises(ValueError):
                character_packet.validate_answers(packet, bad)
        with self.assertRaises(ValueError):
            character_packet.validate_answers(packet, [])

    def test_renderer_escapes_text_and_has_separate_full_photo_reference_workflow(self):
        packet = self.packet()
        packet["packetSHA256"] = "bound"
        packet["images"], _ = cli.review_packet.image_assets(
            packet, self.fixture.run, self.fixture.cache, self.root / "preview",
        )
        packet["characters"][0]["reason"] = "<script>unsafe</script>"
        page = character_packet.render(packet)
        self.assertIn("&lt;script&gt;unsafe&lt;/script&gt;", page)
        self.assertNotIn("<script>unsafe</script>", page)
        for expected in (
            "full + face", "Export all answers", "localStorage", "Same character - not a reference",
            "Import rejected; answers unchanged", "all characters", "no required 2-3 photo quota",
        ):
            self.assertIn(expected, page)

    def test_cli_preview_apply_check_repeat_and_corruption(self):
        experiment = self.root / "experiment"
        experiment.mkdir()
        source = self.root / "run.json"
        source.write_text("{}")
        for name in ("scope.json", "experiment.json"):
            (experiment / name).write_text("{}")
        (experiment / "receipt.json").write_text(json.dumps({
            "provenance": {"inputs": {"run.json": {
                "path": str(source), "sha256": shadow.digest(source),
            }}},
        }))
        baseline = self.root / "baseline"
        baseline.mkdir()
        (baseline / "packet.json").write_text(json.dumps({
            "binding": self.fixture.binding, "packetSHA256": "pair",
        }))
        (baseline / "receipt.json").write_text(json.dumps({
            "outputs": {"packet.json": shadow.digest(baseline / "packet.json")},
        }))
        raw, clarifications = self.root / "feedback.json", self.root / "clarifications.json"
        raw.write_text("{}")
        clarifications.write_text("{}")
        (self.root / "likeness-cache.json").write_text(json.dumps(self.fixture.cache))
        out = self.root / "out"
        args = [
            "--experiment", str(experiment), "--review-packet", str(baseline),
            "--feedback", str(raw), "--clarifications", str(clarifications), "--out", str(out),
        ]
        bounded = functools.partial(character_packet.build_packet, characters=self.characters)
        before = {path: shadow.digest(path) for path in self.root.rglob("*.png")}
        with (
            mock.patch.object(cli, "output_path", return_value=out),
            mock.patch.object(cli.review_packet, "load_experiment", return_value=(
                self.fixture.run, self.fixture.vectors, self.fixture.scope, self.fixture.binding,
            )),
            mock.patch.object(cli.feedback, "ingest", return_value=self.effective),
            mock.patch.object(cli.character_packet, "build_packet", side_effect=bounded),
        ):
            self.assertEqual(cli.main(args + ["--dry-run"]), 0)
            self.assertFalse(out.exists())
            self.assertEqual(cli.main(args + ["--apply"]), 0)
            self.assertEqual(cli.main(args + ["--check"]), 0)
            receipt_hash = shadow.digest(out / "receipt.json")
            self.assertEqual(cli.main(args + ["--apply"]), 0)
            self.assertEqual(receipt_hash, shadow.digest(out / "receipt.json"))
            packet = json.loads((out / "packet.json").read_bytes())
            answers = self.root / "answers.json"
            answers.write_text(json.dumps(self.answers(packet)))
            self.assertEqual(cli.main(args + ["--check", "--answers", str(answers)]), 0)
            (out / "effective-labels.json").write_text("{}")
            self.assertEqual(cli.main(args + ["--check"]), 1)
        self.assertEqual(before, {path: shadow.digest(path) for path in before})

    def test_output_guard_refuses_library_and_relative_paths(self):
        for path in ("relative", str(self.root / "library")):
            with self.assertRaises(ValueError):
                cli.output_path(path)


if __name__ == "__main__":
    unittest.main()
