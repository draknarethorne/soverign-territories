"""Reformation changes state across partitions without moving whole groups or files."""
import copy
import json
import pathlib
import tempfile
import unittest
from unittest import mock

import numpy as np

from tools.art import likeness_candidate_replay as cli
from tools.art.likeness_library import fragment_review, policy, reformation, reformation_report


class ReformationTests(unittest.TestCase):
    def setUp(self):
        self.settings = copy.deepcopy(policy.load_policy())
        self.ids = [f"p{i}" for i in range(6)] + ["outlier"]
        self.vectors = {}
        for i, pid in enumerate(self.ids):
            vector = np.zeros(9)
            if pid == "outlier":
                vector[8] = 1.
            else:
                vector[0], vector[i + 1] = .8, .6
            self.vectors[pid] = vector
        self.photos = [{
            "photoId": pid, "preparedSHA256": "hash-" + pid,
            "destination": f"Models/{'A' if i < 3 else 'B'}/gallery/{pid}.jpg",
        } for i, pid in enumerate(self.ids)]
        self.audit = [{
            **photo, "bucket": "gallery", "qualityEligible": True,
            **{field: False for field in reformation.SAFETY_FIELDS},
        } for photo in self.photos]
        self.run = {"photos": self.photos, "finalMembershipAudit": {"rows": self.audit},
                    "policy": self.settings}
        self.candidate = {
            "rows": [{"photoId": p["photoId"], "currentFolder": "/".join(p["destination"].split("/")[:2])}
                     for p in self.photos],
            "identities": [{"folder": "Models/A", "referencePhotoIds": self.ids[:3]},
                           {"folder": "Models/B", "referencePhotoIds": self.ids[3:]}],
            "appearances": [],
        }
        self.ledger = {"pairs": [], "referenceProposals": [], "unresolved": []}

    def build(self):
        return reformation.build(self.candidate, self.run, self.vectors, self.ledger)

    def test_actual_cross_folder_membership_and_independent_residual(self):
        state = self.build()
        self.assertEqual(state["summary"]["automaticMembers"], 6)
        self.assertEqual(state["summary"]["crossFolderPeople"], 1)
        self.assertEqual(state["summary"]["unresolvedPhotos"], 1)
        person = state["people"][0]
        self.assertEqual(person["memberPhotoIds"], self.ids[:6])
        self.assertEqual(person["ownerStatus"], "cross-folder-owner-unresolved")
        self.assertIsNone(person["canonicalOwner"])
        self.assertEqual(state["residuals"][1]["residualPhotoIds"], ["outlier"])
        self.assertTrue(state["summary"]["stable"])
        self.assertEqual(state["summary"]["executedMoves"], 0)
        self.assertTrue(all(r["placement"] == "unchanged" for r in state["rows"]))
        represented = [pid for p in state["people"] + state["retainedPeople"] for pid in p["memberPhotoIds"]]
        self.assertEqual(sorted(represented), sorted(self.ids))
        self.assertEqual(len(represented), len(set(represented)))

    def test_no_self_equal_content_or_correlated_support(self):
        state = self.build()
        for row in state["rows"][:6]:
            self.assertNotIn(row["photoId"], row["topCandidates"][0]["referencePhotoIds"])
        for photo in self.photos[:4]:
            photo["preparedSHA256"] = "same-content"
        state = self.build()
        self.assertEqual(state["summary"]["automaticMembers"], 0)
        self.setUp()
        for pid in self.ids[:6]:
            self.vectors[pid] = self.vectors["p0"].copy()
        self.assertEqual(self.build()["summary"]["automaticMembers"], 0)

    def test_saved_placement_safeguards_are_not_overridden(self):
        for field in reformation.SAFETY_FIELDS:
            with self.subTest(field=field):
                self.setUp()
                self.audit[0][field] = True
                row = next(r for r in self.build()["rows"] if r["photoId"] == "p0")
                self.assertEqual(row["origin"], "held")
                self.assertIsNone(row["proposedPersonId"])
                self.assertIn(field, row["reasons"])
        for kind in ("review", "Artists", "quality", "neither"):
            with self.subTest(kind=kind):
                self.setUp()
                if kind == "review":
                    self.audit[0]["bucket"] = "review"
                elif kind == "Artists":
                    self.photos[0]["destination"] = "Artists/A/gallery/p0.jpg"
                    self.audit[0]["destination"] = self.photos[0]["destination"]
                    self.candidate["rows"][0]["currentFolder"] = "Artists/A"
                elif kind == "quality":
                    self.audit[0]["qualityEligible"] = False
                else:
                    self.ledger["unresolved"] = [{"photoId": "p0"}]
                row = next(r for r in self.build()["rows"] if r["photoId"] == "p0")
                self.assertEqual(row["origin"], "held")

    def test_positive_labels_do_not_create_membership_and_negative_veto_prevents_bridge(self):
        before = self.build()
        self.ledger["pairs"] = [{"photoIds": ["p0", "p5"], "label": "same"}]
        self.assertEqual(before, self.build())
        for label in ("different", "uncertain"):
            self.ledger["pairs"][0]["label"] = label
            state = self.build()
            person_of = {row["photoId"]: row["proposedPersonId"] for row in state["rows"]}
            self.assertFalse(person_of["p0"] and person_of["p0"] == person_of["p5"])

    def test_all_competitors_including_insufficient_ones_can_block_ambiguous_admission(self):
        # A mutually incoherent two-photo rival can have a flattering centroid,
        # but insufficient support must not make it disappear as competition.
        for index, sign in ((7, 1), (8, -1)):
            pid = f"r{index}"
            vector = np.zeros(9)
            vector[0], vector[7] = .8, sign * .6
            self.vectors[pid] = vector
            photo = {"photoId": pid, "preparedSHA256": "hash-" + pid,
                     "destination": f"Prospects/Rival/gallery/{pid}.jpg"}
            self.photos.append(photo)
            self.audit.append({**self.audit[0], **photo})
            self.candidate["rows"].append({"photoId": pid, "currentFolder": "Prospects/Rival"})
        # Raise only the fixture's discovery floor to isolate the rival; production
        # gates are unchanged and exact recipe settings remain in output.
        self.settings["identityActions"]["identityClusterMinimumSimilarity"] = .5
        state = self.build()
        self.assertGreater(state["rows"][1]["competitorPersonCount"], 1)
        self.assertIn("ambiguous-full-competitor-margin", state["rows"][1]["reasons"])
        self.assertIsNone(state["rows"][1]["proposedPersonId"])

    def test_source_history_names_order_and_noop_do_not_change_person_discovery(self):
        before_inputs = copy.deepcopy((self.run, self.candidate, self.ledger))
        first = self.build()
        self.assertEqual(first, self.build())
        self.assertEqual(before_inputs, (self.run, self.candidate, self.ledger))
        self.photos.reverse()
        self.audit.reverse()
        self.candidate["rows"].reverse()
        self.candidate["identities"].reverse()
        self.assertEqual(first, self.build())
        for row in self.photos:
            row["destination"] = row["destination"].replace("Models/A", "Models/Renamed")
        for row in self.audit:
            row["destination"] = row["destination"].replace("Models/A", "Models/Renamed")
        for row in self.candidate["rows"]:
            row["currentFolder"] = row["currentFolder"].replace("Models/A", "Models/Renamed")
        changed = self.build()
        self.assertEqual([r["proposedPersonId"] for r in first["rows"]],
                         [r["proposedPersonId"] for r in changed["rows"]])

    def test_invalid_missing_and_duplicate_inputs_stop(self):
        del self.vectors["p0"]
        with self.assertRaisesRegex(ValueError, "missing vector"):
            self.build()
        self.setUp()
        self.vectors["p0"][0] = float("nan")
        with self.assertRaisesRegex(ValueError, "invalid saved vector"):
            self.build()
        self.setUp()
        del self.audit[0]["protected"]
        with self.assertRaisesRegex(ValueError, "missing saved safeguards"):
            self.build()
        self.setUp()
        self.photos.append(copy.deepcopy(self.photos[0]))
        with self.assertRaisesRegex(ValueError, "unique stable"):
            self.build()

    def test_confirmed_reference_intent_is_separate_from_automatic_recovery(self):
        self.candidate["identities"][0].update(
            referencePhotoIds=self.ids[:2],
            referenceEvidence={"construction": "confirmed-character-intent"},
        )
        state = self.build()
        rows = {r["photoId"]: r for r in state["rows"]}
        self.assertEqual(rows["p0"]["origin"], "confirmed-character-reference")
        self.assertEqual(rows["p1"]["origin"], "confirmed-character-reference")
        person = next(p for p in state["people"] if p["intentFolder"])
        self.assertEqual(person["canonicalOwner"], "Models/A")
        self.assertEqual(state["summary"]["explicitIntentMembers"], 2)

    def test_conflicting_nonreference_members_cannot_both_join_one_character(self):
        self.settings["categoryPolicies"]["Models"]["photoRouteMargin"] = .1
        self.candidate["identities"][0].update(
            referencePhotoIds=self.ids[:5],
            referenceEvidence={"construction": "confirmed-character-intent"},
        )
        self.vectors["outlier"] = np.zeros(9)
        self.vectors["outlier"][0], self.vectors["outlier"][7] = .8, .6
        self.ledger["pairs"] = [{"photoIds": ["p5", "outlier"], "label": "different"}]
        state = self.build()
        rows = {r["photoId"]: r for r in state["rows"]}
        self.assertIsNone(rows["p5"]["proposedPersonId"])
        self.assertIsNone(rows["outlier"]["proposedPersonId"])
        self.assertIn("direct-member-conflict", rows["p5"]["reasons"])

    def test_inconsistent_confirmed_intent_stops_explicitly(self):
        self.candidate["identities"][0].update(
            referencePhotoIds=self.ids[:2],
            referenceEvidence={"construction": "confirmed-character-intent"},
        )
        self.ledger["pairs"] = [{"photoIds": ["p0", "p1"], "label": "different"}]
        with self.assertRaisesRegex(ValueError, "conflicting confirmed"):
            self.build()

    def test_withdrawal_boundaries_never_grow_references_or_transport_outliers(self):
        state = self.build()
        original = {p["appearanceId"]: set(p["frozenReferencePhotoIds"]) for p in state["appearances"]}
        for appearance in state["appearances"]:
            self.assertLessEqual(set(appearance["referencePhotoIds"]), original[appearance["appearanceId"]])
        self.assertTrue(any(p["referenceWithdrawals"] for p in state["passes"]))
        self.assertIsNone(next(r for r in state["rows"] if r["photoId"] == "outlier")["proposedPersonId"])
        with mock.patch.object(reformation, "MAX_PASSES", 1):
            incomplete = self.build()
            self.assertFalse(incomplete["summary"]["stable"])
            self.assertEqual(incomplete["status"], "bounded-incomplete")
            self.assertTrue(incomplete["pendingReferenceWithdrawals"])

    def test_viewer_binds_complete_state_and_escapes_text(self):
        state = self.build()
        packet = {"cases": [{"id": "case1", "photoId": "p0"}]}
        selection = reformation_report.select(state, packet)
        images = {pid: {"full": "images/" + pid + ".jpg", "href": "file:///test/" + pid}
                  for pid in selection["usedPhotoIds"]}
        self.run["workingRoot"] = str(pathlib.Path.cwd())
        page = reformation_report.render(state, selection, images, self.run)
        self.assertIn("actual proposed membership", page)
        self.assertIn(fragment_review.digest(state), page)
        self.assertIn("Before / after for every photo", page)
        self.assertIn("Export sample feedback", page)
        self.assertIn('image.src=row.href', page)
        self.assertIn('a.textContent=row.filename', page)
        self.assertIn('image.loading="lazy"', page)
        self.assertIn("Image unavailable at installed path", page)
        self.assertNotIn("Install candidate", page)
        self.assertLessEqual(len(images), 40)

    def test_report_preview_apply_repeat_check_and_output_corruption(self):
        packet = {"cases": [{"id": "case1", "photoId": "p0"}]}
        reused = ({}, packet, {}, {})
        self.run["workingRoot"] = str(pathlib.Path.cwd())
        with tempfile.TemporaryDirectory(dir=cli.ROOT / "tmp") as directory:
            out = pathlib.Path(directory) / "report"
            args = mock.Mock(prior_answers=None, answers=None, evaluation=None, split_evaluation=None,
                             reform_view=None,
                             reuse_result=pathlib.Path(directory) / "source", check=False, apply=False)
            publish = lambda: reformation_report.publish(
                args, out, reused, self.candidate, self.run, self.vectors, {}, self.ledger, lambda: {}, mock.Mock(),
            )
            with mock.patch.object(reformation_report.review_packet, "image_assets", return_value=({}, {})), \
                    mock.patch.object(reformation_report, "render", return_value="<html>fixture</html>"):
                self.assertEqual(publish(), 0)
                self.assertFalse(out.exists())
                args.apply = True
                self.assertEqual(publish(), 0)
                self.assertEqual(publish(), 0)
                replacement = pathlib.Path(directory) / "clarified"
                args.reform_view = out
                with mock.patch.object(reformation, "build", side_effect=AssertionError("must not rescore")):
                    self.assertEqual(reformation_report.publish(
                        args, replacement, reused, self.candidate, self.run, self.vectors, {}, self.ledger,
                        lambda: {}, mock.Mock(),
                    ), 0)
                self.assertEqual((out / "state.json").read_bytes(), (replacement / "state.json").read_bytes())
                args.reform_view = None
                args.apply, args.check = False, True
                self.assertEqual(publish(), 0)
                state = json.loads((out / "state.json").read_bytes())
                self.assertEqual(state["summary"]["crossFolderPeople"], 1)
                (out / "state.json").write_text("{}", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "output changed"):
                    publish()

    def test_returned_labels_preserve_conflict_without_automatic_positive_union(self):
        packet = {"cases": [{"id": "case1", "photoId": "p0"}]}
        ledger = copy.deepcopy(self.ledger)
        ledger["pairs"] = [{"photoIds": ["p0", "p1"], "label": "different"}]
        evaluation = {"identityAnswers": {"decisions": [{
            "caseId": "case1", "currentMatch": "same", "targetMatch": "same",
            "pairs": [{"referencePhotoId": "p1", "label": "same"}],
        }]}}
        combined = reformation_report.effective_ledger(ledger, packet, evaluation)
        self.assertEqual(combined["pairs"][0]["label"], "uncertain")
        self.assertEqual(ledger["pairs"][0]["label"], "different")
        self.assertEqual(combined["unresolved"], [])

    def test_presentation_separates_retained_membership_from_confirmation_and_holds(self):
        state = self.build()
        people = {p["personId"]: p for p in state["people"]}
        row = next(r for r in state["rows"] if r["photoId"] == "outlier")
        text = reformation_report.presentation(row, people)
        self.assertIn("NO QUALIFIED REGROUPING", text["actionLabel"])
        self.assertEqual(text["retainedIdentity"], "Models/B")
        self.assertIn("not newly confirmed or rejected", text["actionMeaning"])
        self.assertIn("No manual placement", text["feedbackPrompt"])
        row.update(origin="held", reasons=["protected"])
        text = reformation_report.presentation(row, people)
        self.assertIn("CHANGE BLOCKED (HOLD)", text["actionLabel"])
        self.assertIn("not an identity verdict", text["actionMeaning"])
        self.assertIn("protected", text["reasonText"][0])
        row["origin"] = "unexpected"
        with self.assertRaisesRegex(ValueError, "unknown"):
            reformation_report.presentation(row, people)

    def test_cli_reformation_uses_shared_launcher_loader_not_new_inference(self):
        with tempfile.TemporaryDirectory(dir=cli.ROOT / "tmp") as directory:
            root = pathlib.Path(directory)
            load = ({}, self.ledger, self.candidate, self.run, self.vectors, {}, root / "cached", {})
            reused = ({}, {"cases": []}, {}, {})
            with mock.patch.object(cli, "load", return_value=load), \
                    mock.patch.object(cli, "reuse", return_value=reused), \
                    mock.patch.object(reformation_report, "publish", return_value=0) as publish:
                self.assertEqual(cli.main([
                    "--source", str(root / "source"), "--reuse-result", str(root / "existing"),
                    "--reform", "--out", str(cli.ROOT / "reports" / "likeness-reassessment" / root.name),
                    "--dry-run",
                ]), 0)
                self.assertEqual(publish.call_count, 1)

    def test_loose_pool_can_form_new_people_without_preexisting_identity(self):
        for photo, saved, row in zip(self.photos, self.audit, self.candidate["rows"]):
            photo["destination"] = "Various/gallery/" + photo["photoId"] + ".jpg"
            saved["destination"] = photo["destination"]
            row["currentFolder"] = "Various"
        state = self.build()
        self.assertEqual(state["summary"]["automaticMembers"], 6)
        self.assertEqual(state["people"][0]["lineage"], {"Various": 6})


if __name__ == "__main__":
    unittest.main()
