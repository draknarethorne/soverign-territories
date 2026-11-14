import base64
import copy
import gzip
import json
import pathlib
import re
import tempfile
import unittest
from unittest import mock

from tools.art import likeness_hypothesis_trial, likeness_view_associations as cli
from tools.art.likeness_library import entrance_trial, view_associations
from tools.art.likeness_library.tests import test_view_hypotheses as fixtures


class ViewAssociationTests(unittest.TestCase):
    def setUp(self):
        self.fixture, self.state = fixtures.ViewHypothesisTests().real()
        view = next(v for v in self.state["appearances"] if v["appearanceId"] == "z")
        view["frozenReferencePhotoIds"] = ["x0"]

    def baseline(self):
        f = self.fixture
        initial = entrance_trial.run_sweep(
            self.state, f.run, f.vectors, f.ledger, variants=[entrance_trial.recipes()[1]], coalesce=True,
        )
        return likeness_hypothesis_trial.construct(self.state, f.run, f.vectors, f.ledger, initial)

    def build(self, baseline=None):
        f = self.fixture
        return view_associations.build(self.state, f.run, f.vectors, f.ledger, baseline or self.baseline())

    def row(self, result, pid="x0"):
        return next(r for r in result["rows"] if r["photoId"] == pid)

    def test_singleton_can_associate_without_becoming_a_reference_or_merged_view(self):
        baseline = self.baseline()
        before = copy.deepcopy(baseline)
        result = self.build(baseline)
        row = self.row(result)
        self.assertEqual(row["status"], "already-qualified-membership")
        self.assertEqual(row["coreUse"], "forbidden")
        self.assertFalse(row["supportBlockers"])
        self.assertEqual(len(row["anchorEvidence"]), 2)
        self.assertTrue(all(len(a["supportPhotoIds"]) >= 2 for a in row["anchorEvidence"]))
        self.assertGreaterEqual(len(row["entranceSupportPhotoIds"]), 4)
        self.assertEqual(baseline, before)
        self.assertEqual(result["summary"]["referenceAdditions"], 0)
        self.assertEqual(result["summary"]["removedRivals"], 0)
        self.assertEqual(result["groups"][0]["appearanceStatus"], "not-certified")

    def test_new_noncore_proposal_requires_full_margin_and_original_witnesses(self):
        baseline = self.baseline()
        variant = next(v for v in baseline["variants"] if v["recipe"]["name"] == "ordered-middle-reconciled")
        row = next(r for r in variant["rows"] if r["photoId"] == "x0")
        row["proposalPersonId"] = None
        result = self.build(baseline)
        member = self.row(result)
        self.assertEqual(member["status"], "qualified-non-core-proposal")
        self.assertGreaterEqual(member["lead"], member["target"]["marginRequired"])
        self.assertNotIn("x0", member["entranceSupportPhotoIds"])
        self.assertTrue(set(member["entranceSupportPhotoIds"]) <= {f"p{i}" for i in range(6)})
        photo = next(r for r in result["photoStates"] if r["photoId"] == "x0")
        self.assertEqual(photo["qualifiedNonCorePersonIds"], [member["targetPersonId"]])
        self.assertFalse(photo["newCoreUse"])

    def test_strong_outside_fallback_remains_a_competitor(self):
        self.fixture.vectors["outlier"] = self.fixture.vectors["x0"].copy()
        result = self.build()
        row = self.row(result)
        self.assertEqual(row["status"], "tentative-non-core")
        self.assertIn("unresolved-outside-hypothesis", row["actionBlockers"])
        self.assertFalse(row["outsideRival"]["active"])
        self.assertEqual(row["outsideRival"]["appearanceId"], "outside")
        self.assertLess(row["lead"], 0)
        self.assertEqual(result["summary"]["newQualifiedPhotos"], 0)

    def test_action_locks_preserve_supported_but_tentative_state(self):
        for field, value, blocker in (
            ("placementBlocks", ["protected"], "physical-action-locked"),
            ("explicitIntentFolder", "Models/A", "explicit-intent-preserved"),
        ):
            with self.subTest(field=field):
                self.setUp()
                next(r for r in self.state["rows"] if r["photoId"] == "x0")[field] = value
                result = self.build()
                row = self.row(result)
                self.assertEqual(row["status"], "tentative-non-core")
                self.assertIn(blocker, row["actionBlockers"])
                self.assertFalse(row["installedMove"])

    def test_exact_different_and_uncertain_veto_without_positive_seeding(self):
        for label in ("different", "uncertain"):
            self.setUp()
            self.fixture.ledger["pairs"] = [{"photoIds": ["x0", "p0"], "label": label}]
            row = self.row(self.build())
            self.assertEqual(row["status"], "unsupported-association")
            self.assertIn("exact-different-or-uncertain-veto", row["supportBlockers"])
        self.setUp()
        without = self.build()
        self.fixture.ledger["pairs"] = [{"photoIds": ["x0", "p0"], "label": "same"}]
        self.assertEqual(without, self.build())

    def test_equal_content_and_correlated_witnesses_do_not_count(self):
        for photo in self.fixture.run["photos"]:
            if photo["photoId"] == "x0":
                photo["preparedSHA256"] = self.fixture.run["photos"][0]["preparedSHA256"]
        row = self.row(self.build())
        self.assertNotIn("p0", row["entranceSupportPhotoIds"])
        self.assertTrue(all("p0" not in a["supportPhotoIds"] for a in row["anchorEvidence"]))
        self.setUp()
        baseline = self.baseline()
        from tools.art.likeness_library import protection
        with mock.patch.object(protection, "_independent", side_effect=lambda rows, settings: rows[:1]):
            with self.assertRaisesRegex(ValueError, "original-anchor construction"):
                self.build(baseline)

    def test_unavailable_or_incomplete_baseline_refuses(self):
        baseline = self.baseline()
        variant = next(v for v in baseline["variants"] if v["recipe"]["name"] == "ordered-middle-reconciled")
        variant["summary"]["stable"] = False
        with self.assertRaisesRegex(ValueError, "stable reference"):
            self.build(baseline)
        baseline = self.baseline()
        baseline["viewReconciliation"]["unions"][0]["referencePhotoIds"].append("tamper")
        with self.assertRaisesRegex(ValueError, "original-anchor construction"):
            self.build(baseline)

    def test_exact_conflict_between_new_members_suppresses_both_proposals(self):
        baseline = self.baseline()
        variant = next(v for v in baseline["variants"] if v["recipe"]["name"] == "ordered-middle-reconciled")
        for row in variant["rows"]:
            if row["photoId"] in ("x0", "x1"):
                row["proposalPersonId"] = None
                row["own"] = {**row["own"], "appearanceId": "z"}
        from tools.art.likeness_library import view_hypotheses
        build = view_hypotheses.build
        def inject(*args):
            evidence, report = build(*args)
            evidence.negatives["x0"].add("x1")
            evidence.negatives["x1"].add("x0")
            return evidence, report
        with mock.patch.object(view_hypotheses, "build", side_effect=inject):
            result = self.build(baseline)
        for pid in ("x0", "x1"):
            row = self.row(result, pid)
            self.assertEqual(row["status"], "tentative-non-core")
            self.assertIn("exact-member-conflict-between-new-associations", row["actionBlockers"])
        self.assertEqual(result["summary"]["newQualifiedPhotos"], 0)

    def test_ineligible_candidate_is_not_a_release_or_association(self):
        baseline = self.baseline()
        from tools.art.likeness_library import view_hypotheses
        build = view_hypotheses.build
        def exclude(*args):
            evidence, report = build(*args)
            evidence.eligible.remove("x0")
            return evidence, report
        with mock.patch.object(view_hypotheses, "build", side_effect=exclude):
            row = self.row(self.build(baseline))
        self.assertEqual(row["status"], "unsupported-association")
        self.assertEqual(row["supportBlockers"], ["scope-or-measurement-ineligible"])
        self.assertFalse(row["installedMove"])

    def test_source_conservation_reverse_order_and_nonmutation(self):
        f = self.fixture
        baseline = self.baseline()
        state = copy.deepcopy(self.state)
        result = self.build(baseline)
        reverse = view_associations.build(
            {**self.state, "rows": self.state["rows"][::-1], "appearances": self.state["appearances"][::-1]},
            f.run, dict(reversed(list(f.vectors.items()))), f.ledger, baseline,
        )
        self.assertEqual(result, reverse)
        self.assertEqual(self.state, state)
        self.assertEqual(len(result["photoStates"]), len(self.state["rows"]))
        self.assertEqual(len({r["photoId"] for r in result["photoStates"]}), len(result["photoStates"]))
        self.assertTrue(all(r["placement"] == "unchanged" for r in result["photoStates"]))

    def evidence(self):
        f = self.fixture
        return entrance_trial.Evidence(self.state, f.run, f.vectors, f.ledger)

    def test_overlap_partitions_preserve_shared_and_exclusive_references(self):
        comparison = view_associations._reference_comparison(
            self.evidence(), "x0", ["p0", "p1", "p2", "x0"], ["p1", "p2", "outlier", "x0"], .4,
        )
        self.assertEqual(comparison["kind"], "partial-overlap")
        self.assertEqual(comparison["exactSharedPhotoIds"], ["p1", "p2"])
        self.assertEqual(comparison["exclusiveRival"]["referencePhotoIds"], ["outlier"])
        self.assertEqual(comparison["exclusiveOriginalAnchors"]["referencePhotoIds"], ["p0"])
        self.assertNotIn("x0", comparison["originalAnchors"]["referencePhotoIds"])
        self.assertIn("full signed rival margin remains unchanged", comparison["decisionUse"])
        self.assertEqual(comparison, view_associations._reference_comparison(
            self.evidence(), "x0", ["x0", "p2", "p1", "p0"], ["x0", "outlier", "p2", "p1"], .4,
        ))

    def test_overlap_distinguishes_containment_disjoint_and_missing_references(self):
        for anchors, rival, expected in (
            (["p0"], ["p0"], "same-reference-content"),
            (["p0", "p1"], ["p0"], "rival-contained-in-original-anchors"),
            (["p0"], ["p0", "p1"], "original-anchors-contained-in-rival"),
            (["p0"], ["p1"], "disjoint"),
            (["x0"], ["p0"], "insufficient-reference-coverage"),
            (["p0"], [], "insufficient-reference-coverage"),
        ):
            with self.subTest(expected=expected):
                result = view_associations._reference_comparison(self.evidence(), "x0", anchors, rival, .4)
                self.assertEqual(result["kind"], expected)
                if not result["exclusiveRival"]["referencePhotoIds"]:
                    self.assertIsNone(result["exclusiveRival"]["centroidScore"])

    def test_equal_content_is_shared_not_exclusive_and_query_copies_are_excluded(self):
        evidence = self.evidence()
        evidence.hashes["p1"] = evidence.hashes["p0"]
        evidence.reference_rows["p1"]["sha256"] = evidence.hashes["p0"]
        comparison = view_associations._reference_comparison(evidence, "x0", ["p0"], ["p1"], .4)
        self.assertEqual(comparison["kind"], "same-reference-content")
        self.assertEqual(comparison["exactSharedPhotoIds"], [])
        self.assertEqual(comparison["equalContentSharedRivalPhotoIds"], ["p1"])
        self.assertEqual(comparison["exclusiveRival"]["referencePhotoIds"], [])
        for pid in ("p0", "p1"):
            evidence.hashes[pid] = evidence.hashes["x0"]
            evidence.reference_rows[pid]["sha256"] = evidence.hashes["x0"]
        comparison = view_associations._reference_comparison(evidence, "x0", ["p0"], ["p1"], .4)
        self.assertEqual(comparison["kind"], "insufficient-reference-coverage")
        self.assertIsNone(comparison["originalAnchors"]["centroidScore"])

    def test_correlated_subset_references_do_not_inflate_support(self):
        self.fixture.vectors["p1"] = self.fixture.vectors["p0"].copy()
        evidence = self.evidence()
        comparison = view_associations._reference_comparison(evidence, "x0", ["p0", "p1"], ["p0", "p1"], .4)
        record = comparison["sharedRival"]
        self.assertEqual(len(record["referencePhotoIds"]), 2)
        self.assertEqual(len(record["independentReferencePhotoIds"]), 1)
        self.assertLessEqual(len(record["independentSupportPhotoIds"]), 1)

    def test_diagnostics_do_not_change_membership_margins_or_references(self):
        self.fixture.vectors["outlier"] = self.fixture.vectors["x0"].copy()
        baseline = self.baseline()
        result = self.build(baseline)
        with mock.patch.object(view_associations, "_reference_comparison", return_value=None):
            without = self.build(baseline)
        for row in result["rows"]:
            row["rivalReferenceComparison"] = None
        for value in (result, without):
            value["summary"].pop("tentativeReferenceOverlap")
        self.assertEqual(result, without)
        self.assertIn("unresolved-outside-hypothesis", self.row(result)["actionBlockers"])
        self.assertEqual(result["summary"]["newQualifiedPhotos"], 0)

    def test_viewer_projection_keeps_full_counts_and_binds_every_subset_example(self):
        result = self.build()
        run = {"workingRoot": str(cli.ROOT), "photos": list(self.evidence().photos.values())}
        text = cli.render(result, run)
        match = re.search(r'<script id="data" type="application/octet-stream">([^<]+)</script>', text)
        assert match is not None
        encoded = match.group(1)
        data = json.loads(gzip.decompress(base64.b64decode(encoded)))
        self.assertEqual(len(data["groups"]), len(result["groups"]))
        for full, shown in zip(result["rows"], data["rows"]):
            if full["rivalReferenceComparison"]:
                for key in ("sharedRival", "exclusiveRival", "exclusiveOriginalAnchors"):
                    before = full["rivalReferenceComparison"][key]
                    after = shown["rivalReferenceComparison"][key]
                    self.assertEqual(after["referenceCount"], len(before["referencePhotoIds"]))
                    self.assertLessEqual(len(after["examplePhotoIds"]), 3)
                    self.assertTrue(set(after["examplePhotoIds"]) <= data["sources"].keys())
        self.assertIn('id="group"', text)
        self.assertIn("not certified appearances", text)
        self.assertIn("Equal-content copies count as shared content", text)
        self.assertIn("not additive across subsets", text)

    def test_no_scope_invents_new_singleton_identity(self):
        self.state["appearances"] = [v for v in self.state["appearances"] if v["appearanceId"] != "z"]
        result = self.build()
        self.assertFalse(result["groups"])
        self.assertFalse(result["rows"])
        self.assertEqual(result["summary"]["uniqueSupportedPhotos"], 0)
        self.assertEqual(result["summary"]["photoCount"], 10)

    def test_viewer_explains_tentative_without_claiming_an_appearance(self):
        result = self.build()
        self.fixture.run["workingRoot"] = str(cli.ROOT)
        text = cli.render(result, self.fixture.run)
        for phrase in ("not a certified appearance", "Core use: forbidden", "A rival is not a recommended destination",
                       "original filename link retained", "Unable to load association viewer",
                       "Original-anchor witnesses and outside rival images", "Saved own-core score"):
            self.assertIn(phrase, text)
        self.assertIn('img.src=src.href', text)

    def test_launcher_preview_apply_repeat_check_and_tamper(self):
        baseline = self.baseline()
        f = self.fixture
        with tempfile.TemporaryDirectory(dir=cli.ROOT / "tmp") as name:
            root = pathlib.Path(name)
            source, saved, out = root / "source", root / "baseline", root / "report"
            source.mkdir()
            saved.mkdir()
            f.run["workingRoot"] = str(root)
            f.run["publishedFiles"] = []
            for photo in f.run["photos"]:
                path = cli.publisher.review_packet.safe_path(root, photo["destination"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture bytes")
                f.run["publishedFiles"].append({"path": photo["destination"], "sha256": cli.shadow.digest(path)})
            loaded = (self.state, f.run, f.vectors, {}, f.ledger, root / "unused", {})
            args = ["--source", str(source), "--baseline", str(saved), "--out", str(out)]
            with mock.patch.object(cli.publisher, "output_path", side_effect=lambda path: path), \
                    mock.patch.object(cli, "load_baseline", return_value=(baseline, {})), \
                    mock.patch.object(cli.publisher.diagnostics, "load", return_value=loaded):
                self.assertEqual(cli.main(args+["--dry-run"]), 0)
                self.assertFalse(out.exists())
                self.assertEqual(cli.main(args+["--apply"]), 0)
                receipt = json.loads((out / "receipt.json").read_bytes())
                self.assertTrue(receipt["reverseVerified"])
                with mock.patch.object(view_associations, "build", side_effect=AssertionError("unexpected scoring")):
                    self.assertEqual(cli.main(args+["--apply"]), 0)
                    self.assertEqual(cli.main(args+["--check"]), 0)
                data = out / "associations.json"
                original = data.read_bytes()
                data.write_bytes(b"tamper")
                self.assertEqual(cli.main(args+["--check"]), 2)
                data.write_bytes(original)
                path = cli.publisher.review_packet.safe_path(root, f.run["photos"][0]["destination"])
                path.write_bytes(b"source drift")
                self.assertEqual(cli.main(args+["--check"]), 2)

    def test_baseline_code_and_output_drift_are_refused(self):
        with tempfile.TemporaryDirectory(dir=cli.ROOT / "tmp") as name:
            root = pathlib.Path(name)
            receipt = {
                "kind": "original-anchor-hypothesis-receipt", "source": str(root),
                "code": {}, "reverseVerified": True, "installedMoves": 0,
                "recipe": entrance_trial.recipes()[1],
            }
            (root / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unchanged verified"):
                cli.load_baseline(root, root)
            receipt["code"] = cli.previous.codes()
            receipt["inputs"] = {}
            receipt["outputs"] = {"trial.json": "incorrect-hash"}
            (root / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
            (root / "trial.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "evidence changed"):
                cli.load_baseline(root, root)

    def test_menu_help_and_launcher_exist_without_route_collision(self):
        menu = (cli.ROOT / "bin" / "menu.cmd").read_text(encoding="utf-8")
        self.assertEqual(menu.count('if /i "%CH%"=="LA"'), 1)
        self.assertIn('if /i "%CH%"=="LA" goto viewassociations', menu)
        self.assertIn("likeness-view-associations.cmd", (cli.ROOT / "bin" / "help.cmd").read_text(encoding="utf-8"))
        self.assertIn("likeness_view_associations.py", (cli.ROOT / "bin" / "likeness-view-associations.cmd").read_text())


if __name__ == "__main__":
    unittest.main()
