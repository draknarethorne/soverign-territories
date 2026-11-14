import base64
import collections
import copy
import gzip
import json
import pathlib
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

from tools.art import likeness_hypothesis_trial as cli
from tools.art.likeness_library import entrance_trial, view_hypotheses, view_reconciliation
from tools.art.likeness_library.tests import test_membership_reassessment as fixtures


class ViewHypothesisTests(unittest.TestCase):
    def fake(self, links=None):
        def view(name, person):
            return {
                "appearanceId": name, "personId": person, "folder": "Models/"+name,
                "category": "Models", "pooled": False, "original": [name+"0", name+"1"],
                "frozenReferencePhotoIds": [name+"0", name+"1"], "explicitIntent": False,
            }
        a, b = view("a", "joint"), view("b", "joint")
        joint = {**view("j", "joint"), "original": a["original"] + b["original"]}
        c, d = view("c", "old-a"), view("d", "old-b")
        allowed = links if links is not None else {frozenset(p) for p in ("ac", "bc", "ad", "bd", "cd")}
        def support(pid, refs, floor):
            return refs if refs and frozenset((pid[0], refs[0][0])) in allowed else []
        e = types.SimpleNamespace(
            views=[a, b, joint, c, d], own_people={}, negatives=collections.defaultdict(set),
            support=support, qualify=lambda view, refs, recipe: (refs, True),
            scores=lambda inventory: inventory,
        )
        report = {"unions": [{
            "personId": "joint", "jointViewId": "j", "originalPersonIds": ["old-a", "old-b"],
            "originalFolders": ["Models/a", "Models/b"], "referencePhotoIds": joint["original"],
            "provisionalDisplayOwner": "Models/a",
        }]}
        return e, report

    def build(self, e, report):
        return view_hypotheses.build(e, report, entrance_trial.recipes()[1])

    def test_complete_views_join_but_originals_and_names_remain(self):
        e, original = self.fake()
        before = copy.deepcopy(e.views)
        candidate, report = self.build(e, original)
        checks = report["hypothesisReconciliation"]["checks"]
        self.assertTrue(all(c["accepted"] for c in checks))
        self.assertEqual(len(report["hypothesisReconciliation"]["extensions"]), 1)
        self.assertEqual(next(v for v in candidate.views if v["appearanceId"] == "c")["personId"], "joint")
        self.assertEqual(e.views, before)
        self.assertEqual(original["unions"][0]["referencePhotoIds"], ["a0", "a1", "b0", "b1"])
        self.assertEqual(report["unions"][0]["provisionalDisplayOwner"], "Models/a")
        self.assertTrue({v["appearanceId"] for v in e.views} <= {v["appearanceId"] for v in candidate.views})

    def test_one_failed_reference_keeps_entire_view_as_rival(self):
        e, report = self.fake()
        support = e.support
        e.support = lambda pid, refs, floor: [] if pid == "c1" else support(pid, refs, floor)
        candidate, report = self.build(e, report)
        check = next(c for c in report["hypothesisReconciliation"]["checks"] if c["candidateViewId"] == "c")
        self.assertFalse(check["accepted"])
        self.assertEqual(next(v for v in candidate.views if v["appearanceId"] == "c")["personId"], "old-a")
        failures = [r["photoId"] for c in check["comparisons"] for r in c["unsupportedReferences"]]
        self.assertIn("c1", failures)
        self.assertNotIn("c0", report["unions"][0]["referencePhotoIds"])

    def test_every_original_anchor_required_not_just_expanded_center(self):
        e, report = self.fake({frozenset("ac")})
        _, report = self.build(e, report)
        self.assertFalse(any(c["accepted"] for c in report["hypothesisReconciliation"]["checks"]))

    def test_bridge_and_chained_candidates_do_not_certify(self):
        e, report = self.fake({frozenset(p) for p in ("ac", "bc", "cd")})
        _, report = self.build(e, report)
        checks = report["hypothesisReconciliation"]["checks"]
        self.assertTrue(checks[0]["accepted"])
        self.assertFalse(checks[1]["accepted"])

    def test_candidates_require_pairwise_complete_link(self):
        e, report = self.fake({frozenset(p) for p in ("ac", "bc", "ad", "bd")})
        _, report = self.build(e, report)
        checks = report["hypothesisReconciliation"]["checks"]
        self.assertTrue(checks[0]["accepted"])
        self.assertIn("candidate-peer-complete-link-not-qualified", checks[1]["reasons"])

    def test_negative_or_uncertain_pairs_block_complete_view(self):
        e, report = self.fake()
        e.negatives["c0"].add("a0")
        _, report = self.build(e, report)
        check = report["hypothesisReconciliation"]["checks"][0]
        self.assertFalse(check["accepted"])
        self.assertIn(["a0", "c0"], check["comparisons"][0]["exactConflicts"])

    def test_joint_core_must_keep_every_reference_and_converge(self):
        for incomplete in (False, True):
            e, report = self.fake()
            e.qualify = lambda view, refs, recipe: (refs, False) if incomplete else (refs[:-1], True)
            _, report = self.build(e, report)
            self.assertFalse(any(c["accepted"] for c in report["hypothesisReconciliation"]["checks"]))

    def test_distinct_cast_slot_not_aliased(self):
        e, report = self.fake()
        e.views[0].update(folder="Sisters/A", category="Sisters")
        e.views[3].update(folder="Sisters/C", category="Sisters")
        _, report = self.build(e, report)
        self.assertFalse(report["hypothesisReconciliation"]["checks"][0]["accepted"])

    def test_outside_lineage_and_pooled_views_unchanged(self):
        e, report = self.fake()
        e.views[3]["personId"] = "outside"
        e.views[4]["pooled"] = True
        candidate, report = self.build(e, report)
        self.assertEqual(report["hypothesisReconciliation"]["checks"], [])
        self.assertEqual({v["appearanceId"]: v for v in e.views},
                         {v["appearanceId"]: v for v in candidate.views})

    def real(self):
        fixture = fixtures.MembershipReassessmentTests()
        fixture.setUp()
        fixture.add_group(count=3, folder="Models/A")
        for i in range(3):
            vector = np.zeros(20)
            vector[0], vector[10+i] = .8, .6
            fixture.vectors[f"x{i}"] = vector
        state = fixture.build()
        template = state["appearances"][0]
        state["appearances"] = [
            {**template, "appearanceId": key, "personId": person, "folder": folder,
             "category": "Models", "pooled": False, "explicitIntent": False,
             "frozenReferencePhotoIds": refs}
            for key, person, folder, refs in (
                ("a", "old-a", "Models/A", ["p0", "p1", "p2"]),
                ("b", "old-b", "Models/B", ["p3", "p4", "p5"]),
                ("z", "old-a", "Models/A", ["x0", "x1", "x2"]),
                ("outside", "outside", "Models/Other", ["outlier"]),
            )
        ]
        return fixture, state

    def test_real_per_photo_admission_and_outside_rival_are_preserved(self):
        fixture, state = self.real()
        e = entrance_trial.Evidence(state, fixture.run, fixture.vectors, fixture.ledger)
        coalesced, initial = view_reconciliation.build(e, entrance_trial.recipes()[1])
        candidate, report = self.build(coalesced, initial)
        self.assertEqual(len(report["hypothesisReconciliation"]["extensions"]), 1)
        result = entrance_trial.run_variant(candidate, entrance_trial.recipes()[1])
        view_hypotheses.annotate(result, candidate, report)
        self.assertEqual(result["summary"]["photoCount"], 10)
        outsider = next(r for r in result["rows"] if r["photoId"] == "outlier")
        self.assertIsNone(outsider["proposalPersonId"])
        row = next(r for r in result["rows"] if r["photoId"] == "x0")
        self.assertIsNotNone(row["proposalPersonId"])
        self.assertTrue(row["reconciledViewIds"])
        self.assertIsNotNone(row["competingView"])
        self.assertAlmostEqual(row["lead"], row["best"]["activeScore"] - row["competingView"]["score"], places=5)
        self.assertEqual(result["summary"]["installedMoves"], 0)
        self.assertEqual(result["summary"]["automaticProtectionAcquired"], 0)

    def test_self_equal_content_and_correlated_support_cannot_qualify_view(self):
        fixture, state = self.real()
        for pid in ("x0", "x1", "x2"):
            fixture.vectors[pid] = fixture.vectors["p0"].copy()
        for photo in fixture.run["photos"]:
            if photo["photoId"].startswith("x"):
                photo["preparedSHA256"] = fixture.run["photos"][0]["preparedSHA256"]
        e = entrance_trial.Evidence(state, fixture.run, fixture.vectors, fixture.ledger)
        coalesced, report = view_reconciliation.build(e, entrance_trial.recipes()[1])
        _, report = self.build(coalesced, report)
        checks = report["hypothesisReconciliation"]["checks"]
        self.assertTrue(checks)
        self.assertFalse(any(c["accepted"] for c in checks))

    def test_exact_member_veto_and_physical_locks_survive_reconciliation(self):
        fixture, state = self.real()
        e = entrance_trial.Evidence(state, fixture.run, fixture.vectors, fixture.ledger)
        coalesced, report = view_reconciliation.build(e, entrance_trial.recipes()[1])
        candidate, _ = self.build(coalesced, report)
        candidate.source["x0"]["placementBlocks"] = ["protected"]
        candidate.negatives["x1"].add("p0")
        candidate.negatives["p0"].add("x1")
        result = entrance_trial.run_variant(candidate, entrance_trial.recipes()[1])
        locked = next(r for r in result["rows"] if r["photoId"] == "x0")
        vetoed = next(r for r in result["rows"] if r["photoId"] == "x1")
        self.assertIsNone(locked["proposalPersonId"])
        self.assertIn("physical-action-locked", locked["entranceBlockers"])
        self.assertIsNone(vetoed["proposalPersonId"])

    def test_changed_original_anchor_control_refuses_continuation(self):
        fixture, state = self.real()
        baseline = entrance_trial.run_sweep(
            state, fixture.run, fixture.vectors, fixture.ledger,
            variants=[entrance_trial.recipes()[1]], coalesce=True,
        )
        baseline["viewReconciliation"]["unions"][0]["referencePhotoIds"].append("tamper")
        with self.assertRaisesRegex(ValueError, "original anchors"):
            cli.construct(state, fixture.run, fixture.vectors, fixture.ledger, baseline)

    def test_reverse_parity_and_controls_reused_without_mutation(self):
        fixture, state = self.real()
        baseline = entrance_trial.run_sweep(
            state, fixture.run, fixture.vectors, fixture.ledger,
            variants=[entrance_trial.recipes()[1]], coalesce=True,
        )
        before = copy.deepcopy(baseline)
        result = cli.construct(state, fixture.run, fixture.vectors, fixture.ledger, baseline)
        reverse = cli.construct(
            {**state, "rows": state["rows"][::-1], "appearances": state["appearances"][::-1]},
            fixture.run, dict(reversed(list(fixture.vectors.items()))), fixture.ledger, baseline,
        )
        self.assertEqual(cli.publisher.semantic(result), cli.publisher.semantic(reverse))
        self.assertEqual(baseline, before)
        self.assertEqual(result["variants"][0]["rows"], baseline["variants"][0]["rows"])
        self.assertEqual(result["variants"][1]["rows"], baseline["variants"][1]["rows"])
        self.assertEqual(result["variants"][2]["rows"], baseline["variants"][2]["rows"])
        fixture.run["workingRoot"] = str(cli.ROOT)
        html = cli.publisher.render(result, state, fixture.run)
        self.assertIn("One unsupported reference", html)
        self.assertIn("Strongest outside rival", html)
        display = json.loads(gzip.decompress(base64.b64decode(cli.publisher.display_payload(result, {}))))["result"]
        self.assertEqual(display["defaultVariant"], "ordered-middle-reconciled")
        self.assertIn("competingView", display["variants"][3]["rows"][0])
        self.assertEqual(display["variants"][3]["rows"][0]["comparisonControlName"], "ordered-middle-coalesced")
        self.assertEqual(display["variants"][4]["rows"][0]["comparisonControlName"], "ordered-middle-coalesced-growth")

    def test_launcher_preview_apply_repeat_check_and_tamper(self):
        fixture, state = self.real()
        baseline = entrance_trial.run_sweep(
            state, fixture.run, fixture.vectors, fixture.ledger,
            variants=[entrance_trial.recipes()[1]], coalesce=True,
        )
        with tempfile.TemporaryDirectory(dir=cli.ROOT / "tmp") as name:
            root = pathlib.Path(name)
            source, saved, out = root / "source", root / "saved", root / "report"
            source.mkdir()
            saved.mkdir()
            fixture.run["workingRoot"] = str(root)
            fixture.run["publishedFiles"] = []
            for photo in fixture.run["photos"]:
                path = cli.publisher.review_packet.safe_path(root, photo["destination"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture bytes")
                fixture.run["publishedFiles"].append({
                    "path": photo["destination"], "sha256": cli.shadow.digest(path),
                })
            loaded = (state, fixture.run, fixture.vectors, {}, fixture.ledger, root / "unused", {})
            args = ["--source", str(source), "--baseline", str(saved), "--out", str(out)]
            with mock.patch.object(cli.publisher, "output_path", side_effect=lambda path: path), \
                    mock.patch.object(cli.publisher, "load_reuse", return_value=(baseline, {})), \
                    mock.patch.object(cli.publisher.diagnostics, "load", return_value=loaded):
                self.assertEqual(cli.main(args+["--dry-run"]), 0)
                self.assertFalse(out.exists())
                self.assertEqual(cli.main(args+["--apply"]), 0)
                with mock.patch.object(cli, "construct", side_effect=AssertionError("unexpected scoring")):
                    self.assertEqual(cli.main(args+["--apply"]), 0)
                    self.assertEqual(cli.main(args+["--check"]), 0)
                index = out / "index.html"
                original = index.read_bytes()
                index.write_bytes(b"tamper")
                self.assertEqual(cli.main(args+["--check"]), 2)
                index.write_bytes(original)
                path = cli.publisher.review_packet.safe_path(root, fixture.run["photos"][0]["destination"])
                path.write_bytes(b"source drift")
                self.assertEqual(cli.main(args+["--check"]), 2)

    def test_menu_and_help_expose_launcher_without_collision(self):
        menu = (cli.ROOT / "bin" / "menu.cmd").read_text(encoding="utf-8")
        self.assertEqual(menu.count('if /i "%CH%"=="LH"'), 1)
        self.assertIn('if /i "%CH%"=="LH" goto hypothesistrial', menu)
        self.assertIn('likeness-hypothesis-trial.cmd" --source', menu)
        self.assertIn("likeness-hypothesis-trial.cmd", (cli.ROOT / "bin" / "help.cmd").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
