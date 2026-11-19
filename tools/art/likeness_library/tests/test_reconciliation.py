#!/usr/bin/env python3
"""Tests for frozen-core, deterministic Review and pool reconciliation."""
import contextlib
import copy
import io
import json
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.art.likeness_library.reconciliation import (  # noqa: E402
    frozen_identity_cores,
    fragment_proposals,
    plan_reconciliation,
)
from tools.art import likeness  # noqa: E402
from tools.art.likeness import apply_category_changes  # noqa: E402


def candidate(photo_id, vector, *, folder="Various", bucket="Pool", side="Prospects", **values):
    return {
        "photoId": photo_id,
        "sourceFolder": folder,
        "sourceBucket": bucket,
        "side": side,
        "vector": np.asarray(vector, dtype=float),
        **values,
    }


def stable_name(seed, taken):
    name = f"New-{seed[:8]}"
    return f"Other-{seed[:8]}" if name.casefold() in taken else name


class NormalAdmissionTests(unittest.TestCase):
    def setUp(self):
        from tools.art.likeness_library import normal_admission
        from tools.art.likeness_library.policy import load_policy, effective_settings

        self.admission = normal_admission
        self.policy = load_policy()
        self.settings = effective_settings({}, self.policy)
        self.axes = np.eye(7)
        self.cores, self.references = {}, {}
        self.identity("Sisters/Drakness", self.axes[0], self.axes[3])
        self.api = SimpleNamespace(plan_reconciliation=plan_reconciliation, invent_name=stable_name)

    def identity(self, folder, center, axis):
        rows = [
            {"photoId": f"{folder}:{index}", "sha256": f"{folder}:{index}",
             "vector": .8 * center + sign * .6 * axis, "qualityEligible": True}
            for index, sign in enumerate((1, -1))
        ]
        self.references[folder] = rows
        self.cores[folder] = {
            "vector": center.copy(), "side": "Prospects", "category": folder.split("/")[0],
            "corePhotoIds": [row["photoId"] for row in rows], "personIds": [folder],
            "identityProtected": folder.startswith(("Sisters/", "Angels/")),
            "photoScores": {}, "mode": "fixture",
        }

    def photo(self, vector, photo_id="photo:image_123", **kwargs):
        return candidate(
            photo_id, vector, qualityEligible=True, sha256=f"bytes:{photo_id}", **kwargs,
        )

    def route(self, rows, **kwargs):
        ctx = self.admission.context(self.cores, self.references, self.policy, **kwargs)
        return plan_reconciliation(
            rows, self.cores, policy=self.policy, name_factory=stable_name, admission_context=ctx,
        )

    def paired(self):
        self.identity("Angels/Nyxene", .995 * self.axes[0] + np.sqrt(1 - .995 ** 2) * self.axes[1], self.axes[4])

    def test_exact_gallery_floor_ignores_higher_lower_rival_without_a_per_reference_floor(self):
        vector = .5 * self.axes[0] + np.sqrt(.75) * self.axes[2]
        self.identity("Models/Fragment", vector, self.axes[4])
        row = self.photo(vector, folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True)
        report = self.route([row])
        result = report["assignments"][0]
        self.assertEqual(result["destination"], "Sisters/Drakness")
        self.assertAlmostEqual(result["castAdmission"]["score"], .5)
        self.assertAlmostEqual(result["lowerCategoryEvidence"][0]["score"], 1.)
        self.assertEqual(result["independentSupportCount"], 2)
        self.assertTrue(all(float(vector @ ref["vector"]) < .5 for ref in self.references["Sisters/Drakness"]))

    def test_approved_pair_is_optimistic_but_every_blocking_rival_must_be_approved(self):
        self.paired()
        result = self.route([self.photo(self.axes[0])])["assignments"][0]
        self.assertEqual(result["castAdmission"]["mode"], "optimistic-gallery")
        self.assertFalse(result["referenceEligible"])
        self.identity("Angels/Unrelated", .999 * self.axes[0] + np.sqrt(1 - .999 ** 2) * self.axes[2], self.axes[5])
        report = self.route([self.photo(self.axes[0])])
        self.assertEqual(report["assignments"], [])
        self.assertEqual(report["held"][0]["castAdmission"]["mode"], "ambiguous-review")
        self.assertEqual(report["held"][0]["reviewDestination"], "Sisters/Drakness/review")
        self.assertEqual(len(report["held"][0]["castAdmission"]["alternatives"]), 2)
        self.assertEqual(report["clusters"], [])

    def test_review_floor_and_below_floor_lower_routing(self):
        self.identity("Models/Existing", self.axes[2], self.axes[4])
        for score in (.35, .349):
            with self.subTest(score=score):
                vector = score * self.axes[0] + np.sqrt(1 - score ** 2) * self.axes[2]
                report = self.route([self.photo(vector)])
                if score == .35:
                    self.assertEqual(report["held"][0]["reviewDestination"], "Sisters/Drakness/review")
                    self.assertFalse(report["held"][0]["referenceEligible"])
                else:
                    self.assertEqual(report["assignments"][0]["destination"], "Models/Existing")

    def test_correlated_duplicate_and_self_references_do_not_supply_two_votes(self):
        refs = self.references["Sisters/Drakness"]
        for mutate in (
            lambda: refs[1].update(sha256=refs[0]["sha256"]),
            lambda: refs[1].update(vector=refs[0]["vector"]),
            lambda: refs[1].update(photoId="photo:image_123"),
        ):
            saved = copy.deepcopy(refs)
            mutate()
            report = self.route([self.photo(self.axes[0])])
            self.assertEqual(report["assignments"], [])
            self.assertLess(report["held"][0]["independentSupportCount"], 2)
            refs[:] = saved

    def test_exact_tie_is_disclosed_and_deterministic(self):
        self.identity("Angels/Nyxene", self.axes[0], self.axes[4])
        first = self.route([self.photo(self.axes[0])])["assignments"][0]
        self.cores = dict(reversed(list(self.cores.items())))
        second = self.route([self.photo(self.axes[0])])["assignments"][0]
        self.assertEqual(first, second)
        self.assertEqual(first["destination"], "Angels/Nyxene")
        self.assertIn("storage-only", first["reason"])

    def test_source_quality_negative_evidence_and_receiving_locks(self):
        for kwargs in ({"protected": True}, {"workflowSelected": True}, {"rejectedPersonIds": ["Sisters/Drakness"]}):
            with self.subTest(kwargs=kwargs):
                report = self.route([self.photo(
                    self.axes[0], folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True, **kwargs,
                )])
                self.assertEqual(report["assignments"], [])
                self.assertEqual(report["clusters"], [])
        invalid = self.photo(self.axes[0])
        invalid["qualityEligible"] = False
        self.assertTrue(self.route([invalid])["held"][0]["preserveStaged"])
        locked = self.route([self.photo(self.axes[0])], locked=True)
        self.assertTrue(locked["held"][0]["preserveStaged"])
        self.assertEqual(locked["held"][0]["bestMatch"], "Sisters/Drakness")

    def test_unmatched_existing_gallery_is_retained_and_never_forms_a_fragment(self):
        report = self.route([self.photo(
            self.axes[6], folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True,
        )])
        self.assertEqual(report["assignments"], [])
        self.assertEqual(report["clusters"], [])
        self.assertTrue(report["held"][0]["preserveStaged"])
        review = self.route([self.photo(self.axes[6], folder="Sisters/Drakness", bucket="Review")])
        self.assertEqual(review["assignments"], [])
        self.assertEqual(review["clusters"], [])
        self.assertTrue(review["held"][0]["preserveStaged"])

    def test_one_boundary_allows_existing_or_various_seed_to_recover_other_member(self):
        for arrival_seed in (False, True):
            with self.subTest(arrival_seed=arrival_seed):
                seed = self.photo(.8 * self.axes[0] + .6 * self.axes[1], "photo:image_124")
                recovered = self.photo(.48 * self.axes[0] + np.sqrt(1 - .48 ** 2) * self.axes[1])
                existing = recovered if arrival_seed else seed
                existing.update(sourceFolder="Models/Fragment", sourceBucket="Gallery", rebaseCandidate=True)
                report = self.admission.two_round_plan(
                    self.api, [recovered, seed], self.cores, self.references,
                    self.settings, self.policy, set(),
                )
                self.assertEqual({row["photoId"] for row in report["assignments"]}, {seed["photoId"], recovered["photoId"]})
                self.assertEqual(report["referenceRefreshCount"], 1)
                self.assertEqual(len(report["matchingRounds"]), 2)
                boundary = report["referenceSnapshots"]["2"]["photoIds"]["Sisters/Drakness"]
                self.assertIn(seed["photoId"], boundary)
                self.assertNotIn(recovered["photoId"], boundary)
                self.assertNotIn(seed["photoId"], self.cores["Sisters/Drakness"]["corePhotoIds"])
                json.dumps(report, allow_nan=False)

    def test_review_cannot_bootstrap_other_review_and_old_source_votes_retire(self):
        rows = [
            self.photo(.48 * self.axes[0] + np.sqrt(1 - .48 ** 2) * self.axes[1], f"photo:image_{number}",
                       folder="Models/Fragment", bucket="Gallery", rebaseCandidate=True)
            for number in (123, 124)
        ]
        self.identity("Models/Fragment", rows[0]["vector"], self.axes[4])
        self.references["Models/Fragment"] = [
            {**row, "sha256": row["sha256"]} for row in rows
        ]
        self.cores["Models/Fragment"]["corePhotoIds"] = [row["photoId"] for row in rows]
        report = self.admission.two_round_plan(
            self.api, rows, self.cores, self.references, self.settings, self.policy, set(),
        )
        self.assertEqual(report["assignments"], [])
        self.assertEqual(len(report["held"]), 2)
        self.assertNotIn("Models/Fragment", report["referenceSnapshots"]["2"]["photoIds"])
        self.assertEqual(
            report["referenceSnapshots"]["1"]["photoIds"]["Sisters/Drakness"],
            report["referenceSnapshots"]["2"]["photoIds"]["Sisters/Drakness"],
        )
        self.assertTrue(report["passCapReached"])

    def test_optimistic_gallery_is_not_reconsidered_or_promoted_at_the_boundary(self):
        self.paired()
        photo = self.photo(self.axes[0])
        report = self.admission.two_round_plan(
            self.api, [photo], self.cores, self.references, self.settings, self.policy, set(),
        )
        self.assertEqual(report["matchingRounds"][1]["candidateCount"], 0)
        row = report["assignments"][0]
        self.assertEqual(row["castAdmission"]["mode"], "optimistic-gallery")
        self.assertFalse(row["referenceEligible"])
        self.assertTrue(all(
            photo["photoId"] not in ids for ids in report["referenceSnapshots"]["2"]["photoIds"].values()
        ))

    def test_optimistic_membership_detaches_old_reference_and_stays_unprotected_next_run(self):
        from tools.art.likeness_library import audit, maintenance, metadata, protection

        self.paired()
        decision = self.route([self.photo(self.axes[0])])["assignments"][0]
        person_id, source_id = metadata.new_person_id(), metadata.new_person_id()
        group_id = "group_" + "a" * 32
        photo_id = decision["photoId"]
        catalog = {
            "schemaVersion": 1, "people": {
                pid: {"id": pid, "folder": folder, "displayName": folder.split("/")[1],
                      "folderHistory": [], "identityAnchors": [], "protected": False}
                for pid, folder in ((person_id, decision["destination"]), (source_id, "Models/Fragment"))
            },
            "photos": {photo_id: {"contentSha256": "a" * 64, "protected": False, "membership": {
                "personId": source_id, "groupId": group_id, "status": "supported", "coreUse": True,
                "reason": "old source reference", "referenceVersion": "a" * 64,
            }}},
            "photoGroups": {group_id: {
                "id": group_id, "personId": source_id, "name": "Original group", "status": "supported",
                "memberPhotoIds": [photo_id], "referencePhotoIds": [photo_id],
                "sourcePersonIds": [source_id], "history": [], "reason": "source history",
            }}, "actions": [],
        }
        move = {
            **decision, "source": "Models/Fragment/gallery/fragment_image_123.jpg",
            "destination": decision["destination"] + "/gallery/drakness_image_123.jpg", "sha256": "a" * 64,
        }
        updated = maintenance._updated_catalog(catalog, [move], self.policy)
        member = updated["photos"][photo_id]["membership"]
        self.assertEqual((member["personId"], member["status"], member["coreUse"]), (person_id, "tentative", False))
        self.assertFalse(updated["photos"][photo_id]["protected"])
        self.assertEqual(updated["photoGroups"][group_id]["memberPhotoIds"], [])
        self.assertEqual(updated["photoGroups"][group_id]["referencePhotoIds"], [])
        self.assertIn(photo_id, audit.membership_excluded(updated, [photo_id]))
        for field in ("protected", "coreUse", "anchor"):
            broken = copy.deepcopy(updated)
            if field == "protected":
                broken["photos"][photo_id]["protected"] = True
            elif field == "coreUse":
                broken["photos"][photo_id]["membership"]["coreUse"] = True
            else:
                broken["people"][person_id]["identityAnchors"] = [photo_id]
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "unconfirmed Gallery"):
                metadata.validate_catalog(broken)
        scratch = ROOT / "tmp" / "normal-flow-restoration"
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            root = pathlib.Path(temporary)
            native = root / pathlib.PurePosixPath(move["destination"])
            native.parent.mkdir(parents=True)
            native.write_bytes(b"same unconfirmed pixels")
            updated["photos"][photo_id]["contentSha256"] = metadata.content_sha256(native)
            photo = SimpleNamespace(
                path=native, name=native.name, key=decision["destination"],
                vec=self.axes[0], sha=metadata.content_sha256(native), faces=1, f2=0.,
                usable=lambda _minimum: True,
            )
            space = SimpleNamespace(photos=[photo], st=self.settings)
            actions, evidence = protection.plan_protection(space, {}, updated, self.policy, root=root)
        self.assertEqual(actions, [])
        self.assertTrue(any("unconfirmed assignment-only" in row["reason"] for row in evidence))
        self.assertTrue(catalog["photos"][photo_id]["membership"]["coreUse"])

    def test_cast_receiving_permission_does_not_unlock_outgoing_cast_gallery(self):
        from tools.art.likeness_library import maintenance, metadata, normal_finish

        self.paired()
        decision = self.route([self.photo(self.axes[0])])["assignments"][0]
        scratch = ROOT / "tmp" / "normal-flow-restoration"
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            root = pathlib.Path(temporary)
            source = root / "Models" / "Fragment" / "gallery" / "fragment_image_123.jpg"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"eligible original")
            move = {**decision, "source": source.relative_to(root).as_posix(),
                    "destination": decision["destination"] + "/gallery/drakness_image_123.jpg",
                    "sha256": metadata.content_sha256(source)}
            catalog = maintenance._updated_catalog(
                {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}, [move], self.policy,
            )
            metadata.save_catalog(catalog, root / ".likeness-library.json")
            maintenance._validate_permissions(root, [move], self.policy, {})
            with mock.patch.object(normal_finish, "cores", return_value=({}, [])):
                checked, evidence = normal_finish.check_batch(
                    None, SimpleNamespace(photos=[]), catalog, self.policy, [move],
                )
            self.assertEqual(checked, [move])
            self.assertEqual(evidence["corrections"], [])
            outgoing = {**move, "source": "Angels/Other/gallery/other_image_123.jpg"}
            with self.assertRaisesRegex(ValueError, "protected Gallery"):
                maintenance._validate_permissions(root, [outgoing], self.policy, {})
            disabled = copy.deepcopy(self.policy)
            disabled["categoryPolicies"]["Sisters"]["galleryAdmissionEnabled"] = False
            with self.assertRaises(ValueError):
                maintenance._validate_permissions(root, [move], disabled, {})


class FragmentProposalTests(unittest.TestCase):
    def setUp(self):
        from tools.art.likeness_library.policy import load_policy

        self.policy = load_policy()
        self.cores, self.references = {}, {}
        self.basis = np.eye(7)
        self.add_identity("Sisters/Canonical", self.basis[0], self.basis[2])
        self.add_identity("Models/Fragment", self.basis[0], self.basis[1])

    def add_identity(self, folder, center, axis):
        members = [
            {"photoId": f"{folder}:{index}", "sha256": f"{folder}:hash:{index}",
             "vector": .8 * center + sign * .6 * axis, "qualityEligible": True}
            for index, sign in enumerate((1, -1))
        ]
        self.references[folder] = members
        self.cores[folder] = {
            "vector": center.copy(), "side": "Prospects", "category": folder.split("/")[0],
            "corePhotoIds": [row["photoId"] for row in members], "personIds": [folder],
            "identityProtected": False,
        }

    def result(self, **kwargs):
        return fragment_proposals(self.cores, self.references, self.policy, **kwargs)

    def test_supported_direct_fragment_is_evidence_only_and_order_independent(self):
        before = copy.deepcopy((self.cores, self.references))
        report = self.result()
        self.assertEqual(len(report["candidateLinks"]), 1)
        link = report["candidateLinks"][0]
        self.assertEqual((link["sourceFolder"], link["targetFolder"]),
                         ("Models/Fragment", "Sisters/Canonical"))
        self.assertEqual(link["identityMinimum"], .65)
        self.assertEqual(link["minimumIndependentReferences"], 2)
        self.assertTrue(all(row["qualified"] and row["independentSupportCount"] == 2
                            for row in link["members"]))
        self.assertEqual(report["activation"], "diagnostic-only")
        reverse = fragment_proposals(
            dict(reversed(list(self.cores.items()))),
            {key: list(reversed(rows)) for key, rows in self.references.items()}, self.policy,
        )
        self.assertEqual(report, reverse)
        json.dumps(report, allow_nan=False)
        for folder in self.cores:
            np.testing.assert_array_equal(self.cores[folder]["vector"], before[0][folder]["vector"])
            self.assertEqual(self.cores[folder]["corePhotoIds"], before[0][folder]["corePhotoIds"])
            self.assertEqual(len(self.references[folder]), len(before[1][folder]))

    def test_core_average_cannot_carry_an_unsupported_member(self):
        bad = {
            "photoId": "outlier", "sha256": "outlier-bytes", "qualityEligible": True,
            "vector": .1 * self.basis[0] + np.sqrt(.99) * self.basis[4],
        }
        source = "Models/Fragment"
        self.references[source].append(bad)
        self.cores[source]["corePhotoIds"].append(bad["photoId"])
        total = sum(row["vector"] for row in self.references[source])
        self.cores[source]["vector"] = total / np.linalg.norm(total)
        report = self.result()
        self.assertEqual(report["candidateLinks"], [])
        row = report["comparisons"][0]
        self.assertGreater(row["score"], row["identityMinimum"])
        self.assertIn("not every source core member", row["reason"])
        self.assertEqual([member["photoId"] for member in row["members"] if not member["qualified"]],
                         ["outlier"])

    def test_entry_level_resemblance_is_not_identity_equivalence(self):
        center = .6 * self.basis[0] + .8 * self.basis[3]
        self.add_identity("Models/Fragment", center, self.basis[1])
        report = self.result()
        self.assertEqual(report["candidateLinks"], [])
        self.assertIn("identity-merge threshold", report["comparisons"][0]["reason"])

    def test_content_correlation_and_ambiguity_do_not_supply_independent_support(self):
        for folder in ("Models/Fragment", "Sisters/Canonical"):
            for correlated in (False, True):
                with self.subTest(folder=folder, correlated=correlated):
                    references = copy.deepcopy(self.references)
                    if correlated:
                        references[folder][1]["vector"] = references[folder][0]["vector"].copy()
                    else:
                        references[folder][1]["sha256"] = references[folder][0]["sha256"]
                    report = fragment_proposals(self.cores, references, self.policy)
                    self.assertEqual(report["candidateLinks"], [])
                    self.assertIn("insufficient independent", report["comparisons"][0]["reason"])
        references = copy.deepcopy(self.references)
        references["Models/Fragment"][0]["sha256"] = references["Sisters/Canonical"][0]["sha256"]
        report = fragment_proposals(self.cores, references, self.policy)
        self.assertEqual(report["candidateLinks"], [])
        self.assertIn("shared source/target content", report["comparisons"][0]["reason"])
        cores, references = copy.deepcopy((self.cores, self.references))
        shared_id = references["Models/Fragment"][0]["photoId"]
        references["Sisters/Canonical"][0]["photoId"] = shared_id
        cores["Sisters/Canonical"]["corePhotoIds"][0] = shared_id
        report = fragment_proposals(cores, references, self.policy)
        self.assertEqual(report["candidateLinks"], [])
        self.assertIn("ambiguous reference photo ID", report["comparisons"][0]["reason"])

    def test_locks_negative_evidence_and_incomplete_references_hold(self):
        source, target = "Models/Fragment", "Sisters/Canonical"
        report = self.result(blocked_ids=[self.references[source][0]["photoId"]])
        self.assertIn("protected", report["comparisons"][0]["reason"])
        for mutate in ("source-protected", "different", "source-rejects", "target-rejects",
                       "stale", "quality", "missing"):
            with self.subTest(mutate=mutate):
                cores, references, policy = copy.deepcopy((self.cores, self.references, self.policy))
                if mutate == "source-protected":
                    cores[source]["identityProtected"] = True
                elif mutate == "different":
                    policy["runtimeSettings"]["different"].append([source, target])
                elif mutate == "source-rejects":
                    references[source][0]["rejectedPersonIds"] = [target]
                elif mutate == "target-rejects":
                    references[target][0]["rejectedPersonIds"] = [source]
                elif mutate == "stale":
                    references[target][0]["rejectionMetadataStale"] = True
                elif mutate == "quality":
                    references[source][0]["qualityEligible"] = False
                else:
                    references[target].pop()
                report = fragment_proposals(cores, references, policy)
                self.assertEqual(report["candidateLinks"], [])
                self.assertEqual(report["comparisons"][0]["decision"], "hold")

    def test_multiple_canonical_hypotheses_stay_ambiguous(self):
        self.add_identity("Angels/Other", self.basis[0], self.basis[3])
        report = self.result()
        self.assertEqual(report["candidateLinks"], [])
        rows = [row for row in report["comparisons"] if row["sourceFolder"] == "Models/Fragment"]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all("multiple higher" in row["reason"] for row in rows))

    def test_direct_chain_never_invents_a_transitive_identity_link(self):
        middle = .8 * self.basis[0] + .6 * self.basis[3]
        lower = .8 * middle + .6 * self.basis[4]
        self.add_identity("Models/Fragment", middle, self.basis[1])
        self.add_identity("Prospects/Lower", lower, self.basis[5])
        report = self.result()
        pairs = {(row["sourceFolder"], row["targetFolder"]) for row in report["candidateLinks"]}
        self.assertIn(("Models/Fragment", "Sisters/Canonical"), pairs)
        self.assertIn(("Prospects/Lower", "Models/Fragment"), pairs)
        self.assertNotIn(("Prospects/Lower", "Sisters/Canonical"), pairs)
        self.assertFalse(any(row["sourceFolder"].startswith("Sisters/") for row in report["comparisons"]))

    def test_invalid_frozen_vectors_fail_explicitly(self):
        self.references["Models/Fragment"][0]["vector"] = np.array([np.nan] * 7)
        with self.assertRaisesRegex(ValueError, "invalid fragment reference"):
            self.result()

    def test_zero_centered_core_is_a_visible_hold_not_an_equivalence(self):
        self.cores["Models/Fragment"]["vector"] = np.zeros(7)
        for row in self.references["Models/Fragment"]:
            row["vector"] = np.zeros(7)
        report = self.result()
        self.assertEqual(report["candidateLinks"], [])
        self.assertIn("zero-norm frozen core", report["comparisons"][0]["reason"])


class ReconciliationTests(unittest.TestCase):
    def test_high_group_cast_resemblance_does_not_consume_a_competing_identity(self):
        from tools.art.likeness_library.policy import load_policy

        rows = []
        for index in range(6):
            vector = np.zeros(8)
            vector[0], vector[1] = .395, .4
            vector[index + 2] = np.sqrt(1 - .395**2 - .4**2)
            rows.append(candidate(f"photo:image_{910000 + index}", vector))
        centroid = np.mean([row["vector"] for row in rows], axis=0)
        self.assertGreater(centroid[0] / np.linalg.norm(centroid), .55)
        self.assertTrue(all(row["vector"][0] < .4 for row in rows))
        cores = {"Angels/Angelica": {
            "vector": np.eye(8)[0], "side": "Prospects", "category": "Angels",
        }}
        policy = load_policy()
        result = plan_reconciliation(rows, cores, policy=policy, name_factory=stable_name)
        self.assertEqual(result["assignedCount"], 6)
        self.assertEqual(result["heldCount"], 0)
        self.assertTrue(result["clusters"][0]["destination"].startswith("Models/"))
        self.assertEqual(result["clusters"][0]["photoIds"], sorted(row["photoId"] for row in rows))
        reverse = plan_reconciliation(list(reversed(rows)), cores, policy=policy, name_factory=stable_name)
        self.assertEqual(result["assignments"], reverse["assignments"])
        self.assertEqual(result["clusters"], reverse["clusters"])
        policy["groupCastReviewEnabled"] = True
        legacy = plan_reconciliation(rows, cores, policy=policy, name_factory=stable_name)
        self.assertEqual(legacy["assignedCount"], 0)
        self.assertTrue(all(row["reviewDestination"] == "Angels/Angelica/review"
                            and row["automaticReviewAssociation"] for row in legacy["held"]))

    def test_individually_yellow_cast_matches_can_build_a_model_cluster(self):
        from tools.art.likeness_library.policy import load_policy

        result = plan_reconciliation(
            [
                candidate(f"photo:image_{900000 + index}", [.45, np.sqrt(1 - .45**2)])
                for index in range(6)
            ],
            {
                "Angels/Angelica": {
                    "vector": np.array([1., 0.]), "side": "Prospects", "category": "Angels",
                },
            },
            cluster=.55, policy=load_policy(), name_factory=stable_name,
        )
        self.assertEqual(result["assignedCount"], 6)
        self.assertEqual(result["held"], [])
        self.assertTrue(result["clusters"][0]["destination"].startswith("Models/"))

    def test_category_moves_create_missing_configured_destination_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = root / "Prospects" / "Sophie"
            source.mkdir(parents=True)
            photo = source / "gallery" / "sophie.jpg"
            photo.parent.mkdir()
            photo.write_bytes(b"photo")

            moved = apply_category_changes(
                root,
                [("Prospects/Sophie", "Models/Sophie", 1, False)],
                {"Prospects", "Models"},
            )

            self.assertEqual(moved, 1)
            self.assertFalse(source.exists())
            self.assertEqual(
                (root / "Models" / "Sophie" / "gallery" / "sophie.jpg").read_bytes(),
                b"photo",
            )

    def test_workflow_selected_photos_are_collected_across_all_flows(self):
        config = {
            "photos": {"Sophie": "sophie_image_500001.jpg"},
            "flows": {
                "alpha": {"photos": {"Sophie": "sophie_image_500002.jpg"}},
            },
        }

        selected = likeness.chosen_keys(config)

        self.assertEqual(
            selected,
            {
                likeness.cw.photo_key("sophie_image_500001.jpg"),
                likeness.cw.photo_key("sophie_image_500002.jpg"),
            },
        )

    def test_review_and_pool_candidates_form_one_order_independent_cluster(self):
        rows = [
            candidate("photo:image_100001", [1, 0], folder="Various"),
            candidate("photo:image_100002", [0.99, 0.01], folder="Prospects/Sophie", bucket="Review"),
            candidate("photo:image_100003", [0.98, 0.02], folder="Various"),
        ]
        first = plan_reconciliation(rows, {}, name_factory=stable_name)
        second = plan_reconciliation(list(reversed(rows)), {}, name_factory=stable_name)

        self.assertEqual(first["clusters"], second["clusters"])
        self.assertEqual(first["assignments"], second["assignments"])
        self.assertEqual(first["held"], [])
        self.assertEqual(first["clusters"][0]["destinationType"], "provisional")
        self.assertTrue(first["clusters"][0]["destination"].startswith("Potentials/"))
        self.assertEqual(first["assignedCount"], 3)

    def test_confident_existing_match_respects_margin_and_artist_boundary(self):
        cores = {
            "Prospects/A": {"vector": np.array([1.0, 0.0]), "side": "Prospects"},
            "Prospects/B": {"vector": np.array([0.0, 1.0]), "side": "Prospects"},
            "Artists/One/Person": {"vector": np.array([1.0, 0.0]), "side": "Artists"},
        }
        rows = [
            candidate("photo:image_200001", [0.99, 0.01]),
            candidate("photo:image_200002", [0.71, 0.70]),
            candidate("photo:image_200003", [0.99, 0.01], side="Artists"),
        ]

        result = plan_reconciliation(rows, cores, name_factory=stable_name)

        assigned = {row["photoId"]: row["destination"] for row in result["assignments"]}
        self.assertEqual(assigned["photo:image_200001"], "Prospects/A")
        self.assertEqual(assigned["photo:image_200003"], "Artists/One/Person")
        self.assertIn("photo:image_200002", {row["photoId"] for row in result["held"]})

    def test_policy_protects_target_identity_from_photo_routing(self):
        from tools.art.likeness_library.policy import load_policy

        cores = {
            "Prospects/Protected": {
                "vector": np.array([1.0, 0.0]),
                "side": "Prospects",
                "category": "Prospects",
                "identityProtected": True,
            }
        }
        result = plan_reconciliation(
            [candidate("photo:image_200004", [1.0, 0.0])],
            cores,
            minimum_cluster=3,
            cluster=0.55,
            policy=load_policy(),
            name_factory=stable_name,
        )

        self.assertEqual(result["assignments"], [])
        self.assertEqual(result["held"][0]["reviewDestination"], "Prospects/Protected/review")
        self.assertIn("protected Gallery", result["held"][0]["reason"])

    def test_small_incoming_cast_like_cluster_remains_provisional_under_individual_policy(self):
        from tools.art.likeness_library.policy import load_policy

        vectors = []
        for score in (0.315, 0.464, 0.411, 0.455):
            vectors.append([score, np.sqrt(1 - score**2)])
        cores = {
            "Angels/angelica": {
                "vector": np.array([1.0, 0.0]),
                "side": "Prospects",
                "category": "Angels",
                "identityProtected": True,
            },
            "Sisters/Draknara": {
                "vector": np.array([-1.0, 0.0]),
                "side": "Prospects",
                "category": "Sisters",
                "identityProtected": True,
            },
        }
        rows = [
            candidate(f"photo:image_{210001 + index}", vector)
            for index, vector in enumerate(vectors)
        ]

        result = plan_reconciliation(
            rows,
            cores,
            assign=0.40,
            margin=0.10,
            cluster=0.25,
            minimum_cluster=3,
            policy=load_policy(),
            name_factory=stable_name,
        )

        self.assertEqual(result["assignedCount"], 4)
        self.assertEqual(result["heldCount"], 0)
        self.assertTrue(result["clusters"][0]["destination"].startswith("Potentials/"))
        legacy_policy = load_policy()
        legacy_policy["groupCastReviewEnabled"] = True
        result = plan_reconciliation(rows, cores, policy=legacy_policy, name_factory=stable_name)
        self.assertEqual(result["heldCount"], 4)
        self.assertEqual(
            {row["reviewDestination"] for row in result["held"]},
            {"Angels/angelica/review"},
        )
        self.assertTrue(
            all(row["bestMatch"] == "Angels/angelica" for row in result["held"])
        )

    def test_draft_proposal_reports_qualified_destination_without_authorizing_apply(self):
        from tools.art.likeness_library.policy import load_policy

        result = plan_reconciliation(
            [candidate("photo:image_200005", [1.0, 0.0])],
            {
                "Potentials/Amara Madison": {
                    "vector": np.array([1.0, 0.0]),
                    "side": "Prospects",
                    "category": "Potentials",
                }
            },
            minimum_cluster=3,
            cluster=0.55,
            policy=load_policy(),
            name_factory=stable_name,
        )

        self.assertTrue(result["authorizationRequired"])
        self.assertEqual(result["held"], [])
        self.assertEqual(result["assignments"][0]["destination"], "Potentials/Amara Madison")
        self.assertEqual(result["assignments"][0]["score"], 1.0)

    def test_policy_preserves_a_perfect_pair_without_cast_assignment_gate(self):
        from tools.art.likeness_library.policy import load_policy

        result = plan_reconciliation(
            [candidate("p1", [0, 1]), candidate("p2", [0, 1])],
            {"Angels/A": {"vector": np.array([1., 0.]), "side": "Prospects"}},
            minimum_cluster=3, cluster=.55, policy=load_policy(), name_factory=stable_name,
        )
        self.assertEqual(result["assignedCount"], 2)
        self.assertEqual(len(result["clusters"]), 1)
        self.assertEqual(result["clusters"][0]["photoIds"], ["p1", "p2"])

    def test_cast_protection_does_not_change_unrelated_grouping(self):
        from tools.art.likeness_library.policy import load_policy

        rows = [candidate("p1", [0, 1]), candidate("p2", [0, 1])]
        policy = load_policy()
        first = plan_reconciliation(rows, {}, policy=policy, name_factory=stable_name)
        second = plan_reconciliation(
            rows, {"Angels/A": {"vector": np.array([1., 0.]), "side": "Prospects", "identityProtected": True}},
            policy=policy, name_factory=stable_name,
        )
        self.assertEqual(first["clusters"][0]["photoIds"], second["clusters"][0]["photoIds"])

    def test_provisional_followup_reclassifies_final_five_photo_membership(self):
        from tools.art.likeness_library.policy import load_policy

        policy = load_policy()
        policy["identityActions"]["identityClusterMinimumSimilarity"] = .8
        rows = [
            candidate(str(index), [np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))])
            for index, angle in enumerate((-10, 0, 10, 15, 60))
        ]
        result = plan_reconciliation(rows, {}, policy=policy, name_factory=stable_name)
        self.assertEqual(len(result["clusters"]), 1)
        self.assertEqual(len(result["clusters"][0]["photoIds"]), 5)
        self.assertTrue(result["clusters"][0]["destination"].startswith("Prospects/"))

    def test_remaining_candidate_can_join_fixed_provisional_cluster(self):
        angles = [-10, 0, 10, 60]
        rows = [
            candidate(
                f"photo:image_{300001 + index}",
                [np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))],
                bucket="Review" if index == 1 else "Pool",
            )
            for index, angle in enumerate(angles)
        ]

        result = plan_reconciliation(
            rows,
            {},
            assign=0.48,
            margin=0.10,
            cluster=0.80,
            minimum_cluster=3,
            name_factory=stable_name,
        )

        self.assertEqual(len(result["clusters"]), 1)
        destination = result["clusters"][0]["destination"]
        joined = next(row for row in result["assignments"] if row["photoId"] == "photo:image_300004")
        self.assertEqual(joined["destination"], destination)
        self.assertEqual(joined["destinationType"], "provisional")
        self.assertIn("frozen provisional cluster", joined["reason"])

    def test_ambiguous_candidate_cluster_does_not_create_a_new_identity(self):
        cores = {
            "Prospects/A": {"vector": np.array([0.99, 0.10]), "side": "Prospects"},
            "Prospects/B": {"vector": np.array([0.99, -0.10]), "side": "Prospects"},
        }
        rows = [candidate(f"photo:image_{350001 + index}", [1, 0]) for index in range(3)]

        result = plan_reconciliation(rows, cores, name_factory=stable_name)

        self.assertEqual(result["assignments"], [])
        self.assertEqual(result["clusters"], [])
        self.assertEqual(result["heldCount"], 3)
        self.assertTrue(all("ambiguous destination" in row["reason"] for row in result["held"]))

    def test_protected_duplicate_and_missing_ids_stay_staged(self):
        rows = [
            candidate("photo:image_400001", [1, 0], protected=True),
            candidate("photo:image_400002", [1, 0], protected=True),
            candidate("photo:image_400002", [0.99, 0.01]),
            candidate(None, [1, 0]),
        ]

        result = plan_reconciliation(rows, {}, name_factory=stable_name)

        reasons = [row["reason"] for row in result["held"]]
        self.assertEqual(result["assignments"], [])
        self.assertIn("protected photo; remains staged", reasons)
        self.assertIn("duplicate stable photo ID; remains staged", reasons)
        self.assertIn("missing stable photo ID", reasons)

    def test_frozen_core_uses_anchors_and_excludes_protected_photos(self):
        photos = [
            FakePhoto("anchor", [1, 0]),
            FakePhoto("b", [0, 1]),
            FakePhoto("c", [0.01, 1]),
            FakePhoto("protected", [-1, 0]),
        ]
        space = SimpleNamespace(
            photos=photos,
            by_key={"Prospects/Sophie": photos},
            st={"minFace": 60},
        )
        catalog = {
            "people": {
                "person_1": {
                    "folder": "Prospects/Sophie",
                    "identityAnchors": ["anchor"],
                }
            },
            "photos": {
                "anchor": {"contentSha256": "anchor-hash", "protected": False},
                "protected": {"contentSha256": "protected-hash", "protected": True},
            },
        }

        cores, locked, diagnostics = frozen_identity_cores(
            space,
            catalog,
            photo_id_fn=lambda name: name,
            content_sha256_fn=lambda path: f"{path}-hash",
        )

        np.testing.assert_allclose(cores["Prospects/Sophie"]["vector"], [1, 0])
        self.assertEqual(cores["Prospects/Sophie"]["mode"], "trusted")
        self.assertIn("protected", locked)
        self.assertEqual(diagnostics, [])

    def test_stale_anchor_is_ignored_for_core_construction(self):
        photos = [
            FakePhoto("anchor", [1, 0]),
            FakePhoto("b", [0, 1]),
            FakePhoto("c", [0.01, 1]),
            FakePhoto("d", [0.02, 1]),
        ]
        space = SimpleNamespace(
            photos=photos,
            by_key={"Prospects/Sophie": photos},
            st={"minFace": 60},
        )
        catalog = {
            "people": {
                "person_1": {
                    "folder": "Prospects/Sophie",
                    "identityAnchors": ["anchor"],
                }
            },
            "photos": {"anchor": {"contentSha256": "old-hash", "protected": True}},
        }

        cores, locked, _ = frozen_identity_cores(
            space,
            catalog,
            photo_id_fn=lambda name: name,
            content_sha256_fn=lambda _path: "new-hash",
        )

        self.assertEqual(cores["Prospects/Sophie"]["mode"], "provisional")
        self.assertNotIn("anchor", locked)
        self.assertGreater(cores["Prospects/Sophie"]["vector"][1], 0.99)

    def test_reconcile_command_writes_report_without_changing_source_photo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            photo_path = root / "sophie_image_500001.jpg"
            photo_path.write_bytes(b"unchanged source")
            photo = FakePhoto(photo_path.name, [1, 0])
            photo.path = photo_path
            photo.key = "Various"
            report_path = root / "reconciliation.json"
            settings = {
                "pool": ["Various"],
                "minFace": 60,
                "assign": 0.40,
                "margin": 0.10,
                "cluster": 0.25,
                "minCluster": 3,
                "castMerge": 0.55,
            }
            args = SimpleNamespace(root=None, embedder=None, out=str(report_path), policy=None)
            output = io.StringIO()
            with mock.patch.object(
                likeness,
                "build",
                return_value=(
                    {"photos": {"Sophie": photo_path.name}, "flows": {}},
                    settings,
                    root,
                    None,
                    SimpleNamespace(photos=[photo], by_key={}, st=settings),
                ),
            ), mock.patch.object(likeness, "load_review", return_value=[]), mock.patch.object(
                likeness.metadata, "load_catalog", return_value={"people": {}, "photos": {}}
            ), mock.patch.object(likeness.cw, "photo_folders", return_value=[]), mock.patch.object(
                likeness, "junk_reason", return_value=False
            ), contextlib.redirect_stdout(output):
                likeness.cmd_reconcile(args)

            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["candidateCount"], 1)
            self.assertEqual(report["heldCount"], 1)
            self.assertEqual(report["held"][0]["reason"], "workflow-selected photo; remains staged")
            self.assertEqual(report["source"], "likeness-reconcile")
            self.assertIn("No images or catalogue data are changed", output.getvalue())
            self.assertEqual(photo_path.read_bytes(), b"unchanged source")


class FakePhoto:
    def __init__(self, name, vector):
        self.name = name
        self.path = name
        self.vec = np.asarray(vector, dtype=float)

    def usable(self, _minimum):
        return True


if __name__ == "__main__":
    unittest.main()
