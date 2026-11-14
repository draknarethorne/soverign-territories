"""Clean rebase must flatten old groups, isolate references, and stage reversibly."""
import contextlib
import copy
import hashlib
import io
import json
import os
import pathlib
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

from tools.art import likeness
from tools.art.likeness_library import clean_rebase, metadata, refinement
from tools.art.likeness_library.policy import load_policy
from tools.art.likeness_library.reconciliation import _average_linkage


class GroupLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)

    def fixture(self):
        from tools.art.likeness_library.engine import Photo
        rows, measured = [], {}
        people = {}
        for side, name in enumerate(("Mira Vale", "Elana Vale")):
            folder = "Models/" + name
            person = f"person_{side + 1:032x}"
            people[person] = {"id": person, "folder": folder, "displayName": name,
                              "folderHistory": [], "identityAnchors": [], "protected": False}
            for i in range(7):
                number = side * 7 + i
                pid = f"photo:image_{1000 + number}"
                relative = f"{folder}/gallery/mira_image_{1000 + number}.jpg"
                vector = np.zeros(16)
                vector[side] = .8
                vector[2 + number] = .6
                photo = Photo(pathlib.Path(relative), "Models", name, f"{number:064x}",
                              {"faces": 1, "px": 150, "v": vector.tolist()})
                photo.vec = vector
                measured[relative] = photo
                rows.append({"photoId": pid, "source": relative, "destination": relative,
                             "oldFolder": folder, "sha256": f"{number:064x}", "reason": "old placement"})
        return rows, measured, {"schemaVersion": 1, "people": people, "photos": {}, "actions": []}

    def build(self, fixture=None, **kwargs):
        from tools.art.likeness_library import group_lifecycle
        rows, measured, catalog = fixture or self.fixture()
        result = group_lifecycle.regroup(
            rows, measured, catalog, load_policy(), set(), "test",
            at="2026-11-11T12:37:00+00:00",
            name_factory=lambda seed, taken: "Nova " + seed[-8:], **kwargs,
        )
        return result, catalog

    def test_member_first_complete_cycle_and_schema(self):
        (rows, report), catalog = self.build()
        self.assertEqual(len(rows), 14)
        self.assertEqual(report["evaluation"]["supported"], 14)
        self.assertEqual(report["evaluation"]["tentativeReferences"], 0)
        self.assertEqual(report["evaluation"]["directConflictAdmissions"], 0)
        self.assertTrue({"input", "references", "membership", "growth", "residual", "appearances",
                         "refinement", "publication"} <= {stage["id"] for stage in report["stages"]})
        self.assertTrue(all(len(stage["rows"]) == 14 for stage in report["stages"]))
        metadata.validate_catalog(catalog)

    def test_directed_recipe_runs_inside_maintained_regroup_and_keeps_holds_home(self):
        from tools.art.likeness_library.engine import Photo

        fixture = self.fixture()
        rows, measured, catalog = fixture
        people = list(catalog["people"].values())
        for person in people:
            folder_rows = [row for row in rows if row["oldFolder"] == person["folder"]]
            person["identityAnchors"] = [row["photoId"] for row in folder_rows]
            for row in folder_rows:
                catalog["photos"][row["photoId"]] = {
                    "contentSha256": row["sha256"], "protected": False,
                }

        source_id = "person_" + "3" * 32
        catalog["people"][source_id] = {
            "id": source_id, "folder": "Potentials/Nova", "displayName": "Nova",
            "folderHistory": [], "identityAnchors": [], "protected": False,
        }
        source_vector = measured[rows[0]["source"]].vec.copy()
        for number, vector in ((1014, source_vector), (1015, np.eye(1, 16, 15)[0])):
            relative = f"Potentials/Nova/gallery/nova_image_{number}.jpg"
            pid = f"photo:image_{number}"
            photo = Photo(
                pathlib.Path(relative), "Potentials", "Nova", f"{number:064x}",
                {"faces": 1, "px": 150, "v": vector.tolist()},
            )
            photo.vec = vector
            measured[relative] = photo
            rows.append({
                "photoId": pid, "source": relative, "destination": relative,
                "oldFolder": "Potentials/Nova", "sha256": f"{number:064x}",
                "reason": "old placement",
            })

        for row in rows:
            row["destination"] = f'Potentials/Flattened/gallery/{pathlib.PurePosixPath(row["source"]).name}'
        (output, report), catalog = self.build(fixture, directed_recipe="directed-core-continuity")
        upward = next(row for row in output if row["photoId"] == "photo:image_1014")
        held = next(row for row in output if row["photoId"] == "photo:image_1015")
        self.assertEqual(report["mode"], "experimental-directed-sandbox")
        self.assertEqual(report["recipe"], "directed-core-continuity")
        self.assertEqual(upward["directedReformation"]["actionCategory"], "upward")
        self.assertTrue(upward["destination"].startswith("Models/Mira Vale/gallery/"))
        self.assertEqual(held["directedReformation"]["actionCategory"], "hold")
        self.assertEqual(held["destination"], held["source"])
        self.assertFalse(held["destination"].startswith("Various/review/"))
        for row in output:
            if row["directedReformation"]["actionCategory"] in ("hold", "same-home"):
                self.assertEqual(row["destination"], row["source"])
        self.assertEqual(report["evaluation"]["sameHomeAssignments"], 14)
        self.assertEqual(report["evaluation"]["upwardAssignments"], 1)
        self.assertEqual(report["evaluation"]["heldAssignments"], 1)
        for stage in report["stages"]:
            self.assertIsInstance(stage["rows"], list)
            self.assertEqual(len(stage["rows"]), len(output))
            self.assertEqual({row["photoId"] for row in stage["rows"]},
                             {row["photoId"] for row in output})
            for stage_row in stage["rows"]:
                self.assertNotIn("tentativeAssociations", stage_row)
                self.assertNotIn("sourceIncompatibility", stage_row)
        from tools.art.likeness_library.directed_reformation import unpack_runtime_decisions
        details = unpack_runtime_decisions(report["decisionEvidence"])
        self.assertIn("sourceIncompatibility", details[held["photoId"]])
        self.assertIn("tentativeAssociations", details[held["photoId"]])
        for field in ("sameHomeAssignments", "upwardAssignments", "sameRankAssignments",
                      "correctionAssignments", "heldAssignments"):
            self.assertIn(field, report["evaluation"])
        metadata.validate_catalog(catalog)

    def test_directed_cast_arrival_binds_frozen_admission_and_respects_disabled_gate(self):
        from tools.art.likeness_library import group_lifecycle
        from tools.art.likeness_library.engine import Photo

        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                rows, measured, catalog = self.fixture()
                old_folder, folder = "Models/Mira Vale", "Sisters/Mira Vale"
                for person in catalog["people"].values():
                    if person["folder"] == old_folder:
                        person["folder"] = folder
                    members = [row for row in rows if row["oldFolder"] == old_folder]
                    if person["folder"] == folder:
                        person["identityAnchors"] = [row["photoId"] for row in members]
                for row in rows:
                    if row["oldFolder"] == old_folder:
                        photo = measured.pop(row["source"])
                        row.update(source=row["source"].replace(old_folder, folder),
                                   destination=row["destination"].replace(old_folder, folder),
                                   oldFolder=folder)
                        measured[row["source"]] = photo
                relative = "Potentials/Nova/gallery/nova_image_9999.jpg"
                data = b"cast admission source"
                digest = hashlib.sha256(data).hexdigest()
                photo = Photo(pathlib.Path(relative), "Potentials", "Nova", digest,
                              {"faces": 1, "px": 150, "v": measured[rows[0]["source"]].vec.tolist()})
                photo.vec = measured[rows[0]["source"]].vec.copy()
                measured[relative] = photo
                rows.append({"photoId": "photo:image_9999", "source": relative,
                             "destination": relative, "oldFolder": "Potentials/Nova",
                             "sha256": digest, "reason": "old placement"})
                policy = load_policy()
                policy["categoryPolicies"]["Sisters"]["galleryAdmissionEnabled"] = enabled
                output, report = group_lifecycle.regroup(
                    rows, measured, catalog, policy, set(), "admission-test",
                    directed_recipe="directed-core-continuity")
                arrival = next(row for row in output if row["source"] == relative)
                if enabled:
                    self.assertTrue(arrival["destination"].startswith(folder + "/gallery/"))
                    self.assertEqual(arrival["castAdmission"]["decision"], "admit")
                    self.assertGreaterEqual(arrival["castAdmission"]["independentSupport"], 2)
                    source = pathlib.Path(self.temporary.name)
                    path = source / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                    clean_rebase._verify_routes({"photos": [arrival], "policy": policy}, source)
                else:
                    self.assertEqual(arrival["destination"], relative)
                    self.assertEqual(arrival["directedReformation"]["actionCategory"], "hold")
                    self.assertEqual(report["evaluation"]["proposedCrossFolderMoves"], 0)

    def test_core_selection_preview_marks_metadata_tiers_unmeasured(self):
        from tools.art.likeness_library import directed_reformation

        working = pathlib.Path(self.temporary.name) / "Working"
        folder = working / "Angels" / "Source" / "gallery"
        folder.mkdir(parents=True)
        ids = ("photo:image_2001", "photo:image_2002", "photo:image_2003")
        paths = [folder / f"source_image_{2001 + index}.jpg" for index in range(3)]
        for index, path in enumerate(paths):
            path.write_bytes(f"synthetic-photo-{index}".encode())
        derivative = working / "Angels" / "Source" / "gallery_944x1104"
        derivative.mkdir(parents=True)
        (derivative / "source_image_2001_944x1104.png").write_bytes(b"synthetic derivative")
        incoming = working / "Various" / "gallery"
        incoming.mkdir(parents=True)
        (incoming / "portrait_image_2001.jpg").write_bytes(b"separate incoming bytes")
        (incoming / "unresolved-photo.jpg").write_bytes(b"no stable filename id")
        nested_incoming = working / "Various" / "incoming"
        nested_incoming.mkdir(parents=True)
        for index in range(11):
            (nested_incoming / f"new_image_{4000 + index}.jpg").write_bytes(
                f"nested-incoming-{index}".encode(),
            )
        catalog = {
            "schemaVersion": 1,
            "people": {
                "person_" + "4" * 32: {
                    "id": "person_" + "4" * 32, "folder": "Angels/Source",
                    "displayName": "Source", "folderHistory": [], "identityAnchors": [ids[0]],
                    "protected": False,
                },
            },
            "photos": {
                ids[0]: {"contentSha256": metadata.content_sha256(paths[0]), "protected": False},
                ids[1]: {"contentSha256": metadata.content_sha256(paths[1]), "protected": True},
                ids[2]: {
                    "contentSha256": metadata.content_sha256(paths[2]), "protected": True,
                    "protectionProvenance": {
                        "recipeVersion": "independent-gallery-loo-v1", "frozenCorePhotoIds": [ids[2]],
                    },
                },
            },
            "actions": [],
        }
        report = clean_rebase.core_selection_preview(
            working, catalog, load_policy(), directed_reformation.recipe_named("directed-core-continuity"),
            catalog_source="synthetic Sandbox-local catalogue",
        )
        by_id = {row["photoId"]: row for row in report["photos"]}
        self.assertEqual(report["candidatePhotoCount"], 3)
        self.assertEqual(report["baselineInventory"]["imageFileCount"], 16)
        self.assertEqual(report["baselineInventory"]["sourcePhotoCount"], 16)
        self.assertEqual(report["baselineInventory"]["allImageFileCount"], 17)
        self.assertEqual(report["baselineInventory"]["uniqueStablePhotoIdCount"], 14)
        self.assertEqual(report["baselineInventory"]["unresolvedPhotoIdCount"], 1)
        self.assertEqual(report["baselineInventory"]["duplicateStablePhotoIdCount"], 1)
        self.assertEqual(report["baselineInventory"]["regenerableDerivatives"]["imageFileCount"], 1)
        self.assertEqual(report["incomingVarious"]["imageFileCount"], 13)
        self.assertEqual(report["incomingVarious"]["galleryReviewImageFileCount"], 2)
        self.assertEqual(report["incomingVarious"]["nestedIncomingImageFileCount"], 11)
        self.assertEqual(report["incomingVarious"]["duplicateStablePhotoIdCount"], 0)
        self.assertEqual(
            report["incomingVarious"]["role"],
            "incoming mixed intake; excluded from core/reference candidates",
        )
        self.assertEqual(by_id[ids[0]]["stableIdStatus"], "duplicate-stable-id")
        self.assertTrue(by_id[ids[0]]["authoredIdentityAnchor"])
        self.assertTrue(by_id[ids[1]]["legacyProtectedPlacementHold"])
        self.assertFalse(by_id[ids[1]]["protectionProvenanceCoreCandidate"])
        self.assertTrue(by_id[ids[2]]["protectionProvenanceCoreCandidate"])
        self.assertTrue(all("not measured" in row["measurementEligibility"] for row in report["photos"]))
        self.assertIn("not evaluated", report["measuredEligibility"])
        outputs = clean_rebase.write_core_selection_preview(
            report, pathlib.Path(self.temporary.name) / "preview",
        )
        self.assertTrue(pathlib.Path(outputs["json"]).is_file())
        page = pathlib.Path(outputs["html"]).read_text(encoding="utf-8")
        self.assertIn("incoming mixed intake", page)
        self.assertIn("file:///", page)
        self.assertIn("unresolved", page)
        self.assertIn("no cap or truncation", page)
        self.assertIn("Source-photo duplicate IDs", page)
        self.assertNotIn("gallery_944x1104/source_image_2001_944x1104.png", page)
        self.assertIn("Regenerable derivative image inventory (1)", page)

    def test_candidate_viewer_paginates_and_filters_complete_cast_source_set(self):
        from tools.art.likeness_library import directed_reformation

        working = pathlib.Path(self.temporary.name) / "PagedWorking"
        catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
        for index in range(27):
            category, name = ("Angels", "Ava") if index < 14 else ("Sisters", "Bella")
            gallery = working / category / name / "gallery"
            gallery.mkdir(parents=True, exist_ok=True)
            (gallery / f"photo_image_{5000 + index}.jpg").write_bytes(f"candidate-{index}".encode())
        duplicate_gallery = working / "Models" / "Diagnostics" / "gallery"
        duplicate_gallery.mkdir(parents=True)
        for index in range(51):
            for copy_index in range(2):
                (duplicate_gallery / f"copy{copy_index}_image_{7000 + index}.jpg").write_bytes(
                    f"duplicate-{index}-{copy_index}".encode(),
                )
        derivative = working / "Angels" / "Ava" / "944x1104" / "full"
        derivative.mkdir(parents=True)
        (derivative / "photo_image_5000_944x1104.png").write_bytes(b"not a source duplicate")

        report = clean_rebase.core_selection_preview(
            working, catalog, load_policy(),
            directed_reformation.recipe_named("directed-core-continuity"),
        )
        self.assertEqual(report["candidatePhotoCount"], 27)
        self.assertEqual(report["baselineInventory"]["duplicateStablePhotoIdCount"], 51)
        self.assertEqual(len(report["baselineInventory"]["duplicatePhotoIds"]), 51)
        self.assertEqual(report["baselineInventory"]["regenerableDerivatives"]["imageFileCount"], 1)
        outputs = clean_rebase.write_core_selection_preview(
            report, pathlib.Path(self.temporary.name) / "paged-preview",
        )
        page = pathlib.Path(outputs["html"]).read_text(encoding="utf-8")
        self.assertIn("value=\"Angels\">Angels</option>", page)
        self.assertIn("Angels/Ava (14)", page)
        self.assertIn("Sisters/Bella (13)", page)
        self.assertIn("Showing at most 50 of 51 source-photo duplicate IDs", page)
        self.assertEqual(page.count("<li>"), 50)
        self.assertIn("const pageSize = 24;", page)
        self.assertIn("selection.slice(start, start + pageSize)", page)
        self.assertIn("category.addEventListener", page)
        self.assertIn("identity.addEventListener", page)
        self.assertIn("auto-fit", page)
        self.assertIn("@media(max-width:480px)", page)
        self.assertIn("duplicate IDs among source photos", page)
        self.assertEqual(page.count("<img "), 0)
        self.assertEqual(len(json.loads(pathlib.Path(outputs["json"]).read_text(encoding="utf-8"))["photos"]), 27)

    def test_core_preview_never_falls_back_to_repository_catalogue(self):
        working = pathlib.Path(self.temporary.name) / "EmptyWorking"
        working.mkdir()
        catalog, source = clean_rebase._core_preview_catalog(working)
        self.assertEqual(catalog["people"], {})
        self.assertEqual(catalog["photos"], {})
        self.assertIn("repository catalogue deliberately not used", source)

    def test_reversed_sources_have_identical_state_and_no_mutation(self):
        fixture = self.fixture()
        before = copy.deepcopy(fixture[0])
        (rows, report), catalog = self.build(fixture)
        reverse = self.fixture()
        reverse[0].reverse()
        (other, second), _ = self.build(reverse)
        self.assertEqual(sorted(rows, key=lambda r: r["photoId"]), sorted(other, key=lambda r: r["photoId"]))
        self.assertEqual(report["evaluation"], second["evaluation"])
        self.assertEqual(fixture[0], before)
        self.assertEqual(catalog["photoGroups"], {})

    def test_known_conflict_is_never_certified_under_same_person(self):
        fixture = self.fixture()
        pairs = [{"photoIds": ["photo:image_1000", "photo:image_1001"], "label": "different"}]
        (rows, report), catalog = self.build(fixture, pairs=pairs)
        left, right = [catalog["photos"][pid]["membership"] for pid in pairs[0]["photoIds"]]
        self.assertFalse(left["status"] == right["status"] == "supported"
                         and left["personId"] == right["personId"])
        self.assertEqual(report["evaluation"]["directConflictAdmissions"], 0)
        metadata.validate_catalog(catalog)

    def test_cached_centroids_exclude_all_equal_content_witnesses(self):
        fixture = self.fixture()
        rows, measured, _ = fixture
        rows[1]["sha256"] = rows[0]["sha256"]
        (_, report), _ = self.build(fixture)
        final = next(stage for stage in report["stages"] if stage["id"] == "refinement")
        for result in final["rows"]:
            row = next(r for r in rows if r["photoId"] == result["photoId"])
            witnesses = [
                measured[r["source"]].vec for r in rows
                if r["oldFolder"] == row["oldFolder"] and r["sha256"] != row["sha256"]
            ]
            center = np.sum(witnesses, axis=0)
            expected = float(measured[row["source"]].vec @ center / np.linalg.norm(center))
            self.assertAlmostEqual(result["score"], expected)

    def test_staged_growth_reassesses_against_surviving_original_witnesses(self):
        fixture = self.fixture()
        rows, measured, _ = fixture
        for photo in measured.values():
            photo.vec = np.pad(photo.vec, (0, 1))
        row = copy.deepcopy(rows[0])
        row.update(photoId="photo:image_1014", source="Models/Mira Vale/gallery/mira_image_1014.jpg",
                   destination="Models/Mira Vale/gallery/mira_image_1014.jpg", sha256=f"{14:064x}")
        extra = copy.deepcopy(measured[rows[0]["source"]])
        extra.vec = np.zeros(17)
        extra.vec[0], extra.vec[16] = .55, np.sqrt(1 - .55 ** 2)
        rows.append(row)
        measured[row["source"]] = extra
        (_, report), catalog = self.build(fixture)
        evaluation = report["evaluation"]
        self.assertEqual(evaluation["stagedReferenceOccurrences"], 1)
        self.assertEqual({b["phase"] for b in evaluation["withdrawalBoundaries"]}, {"membership", "post-growth"})
        dependencies = evaluation["stagedDependencies"]
        self.assertEqual(dependencies[0]["photoId"], row["photoId"])
        self.assertEqual(len(dependencies[0]["originalWitnessPhotoIds"]), 7)
        self.assertNotIn(row["photoId"], dependencies[0]["originalWitnessPhotoIds"])
        self.assertTrue(catalog["photos"][row["photoId"]]["membership"]["coreUse"])
        member = rows[0]
        center = np.sum([
            measured[r["source"]].vec for r in rows
            if r["oldFolder"] == member["oldFolder"] and r["photoId"] != member["photoId"]
        ], axis=0)
        expected = float(measured[member["source"]].vec @ center / np.linalg.norm(center))
        final = next(stage for stage in report["stages"] if stage["id"] == "refinement")
        self.assertAlmostEqual(next(r for r in final["rows"] if r["photoId"] == member["photoId"])["score"], expected)
        metadata.validate_catalog(catalog)

    def test_quality_hold_and_manual_protection_are_explicit(self):
        fixture = self.fixture()
        rows, measured, catalog = fixture
        measured[rows[0]["source"]].faces = 2
        catalog["photos"][rows[1]["photoId"]] = {"contentSha256": rows[1]["sha256"], "protected": True}
        (output, _), catalog = self.build(fixture)
        self.assertEqual(output[0]["membership"]["status"], "quality-hold")
        self.assertEqual(output[1]["destination"], rows[1]["destination"])
        self.assertFalse(output[1]["membership"]["coreUse"])
        metadata.validate_catalog(catalog)

    def test_family_refresh_retires_stale_edges_without_losing_names_or_history(self):
        _, _, catalog = self.fixture()
        root, child = catalog["people"].values()
        old = {
            "id": "family_" + "1" * 32, "referencePersonId": root["id"], "surname": "Vale",
            "score": .8, "policyVersion": "old", "previousPersonName": "Mira Vale",
            "reason": "historical creative family",
        }
        for person in (root, child):
            person["family"] = copy.deepcopy(old)
            person["names"] = {
                "originalName": person["displayName"].split()[0] + " Original",
                "currentName": person["displayName"], "originalSource": "recorded-history",
            }
        before = copy.deepcopy({p["id"]: p["family"] for p in (root, child)})
        root["folder"], root["displayName"] = "Models/Mira Ember", "Mira Ember"
        evidence = {
            "linkBand": "yellow",
            "families": [{
                "id": "family_" + "2" * 32, "rootFolder": root["folder"], "rootKind": "identity",
                "surname": "Ember", "surnameSource": "creative test",
                "members": [{
                    "folder": root["folder"], "identity": "Models/Mira Vale", "parent": None,
                    "previousName": "Mira Vale", "name": "Mira Ember", "score": None,
                }],
            }],
        }
        clean_rebase._record_families(catalog, evidence, {}, {}, pathlib.Path(), load_policy(), replace=True)
        self.assertNotIn("family", child)
        self.assertEqual(root["names"]["originalName"], "Mira Original")
        self.assertEqual(child["names"]["currentName"], "Elana Vale")
        self.assertEqual(evidence["previousCatalogueFamilies"], before)
        self.assertEqual({r["decision"] for r in evidence["catalogueReconciliation"]}, {"refreshed", "retired"})
        metadata.validate_catalog(catalog)

    def test_bad_inventory_and_duplicate_ids_fail_explicitly(self):
        fixture = self.fixture()
        fixture[0].append(copy.deepcopy(fixture[0][0]))
        with self.assertRaisesRegex(ValueError, "unambiguous"):
            self.build(fixture)

    def test_tentative_reference_and_broken_group_links_fail_schema_validation(self):
        (_, _), catalog = self.build()
        person_id = next(iter(catalog["people"]))
        pid = next(iter(catalog["photos"]))
        group_id = "group_" + "1" * 32
        catalog["photoGroups"][group_id] = {
            "id": group_id, "personId": person_id, "name": "Evening", "status": "tentative",
            "memberPhotoIds": [pid], "referencePhotoIds": [pid], "sourcePersonIds": [],
            "history": [], "reason": "test",
        }
        with self.assertRaisesRegex(ValueError, "tentative groups|bidirectionally"):
            metadata.validate_catalog(catalog)

    def test_group_lineage_survives_singleton_shrink_without_stale_members(self):
        from tools.art.likeness_library.group_lifecycle import reconcile_history
        group_id = "group_" + "1" * 32
        previous = {group_id: {
            "id": group_id, "personId": "parent", "name": "Evening", "status": "tentative",
            "memberPhotoIds": ["one", "two"], "referencePhotoIds": [],
            "sourcePersonIds": [], "history": [], "reason": "original",
        }}
        states = {
            "one": {"personId": "parent", "status": "tentative", "coreUse": False},
            "two": {"personId": "other", "status": "supported", "coreUse": True},
        }
        groups = reconcile_history({}, previous, states, "next", "2026-11-11T13:00:00+00:00")
        self.assertEqual(groups[group_id]["memberPhotoIds"], ["one"])
        self.assertEqual(groups[group_id]["name"], "Evening")
        self.assertEqual(groups[group_id]["referencePhotoIds"], [])
        self.assertEqual(states["one"]["groupId"], group_id)
        self.assertNotIn("groupId", states["two"])

    def test_policy_and_exact_labels_bind_reference_version(self):
        (_, first), _ = self.build()
        (_, second), _ = self.build(pairs=[
            {"photoIds": ["photo:image_1000", "photo:image_1001"], "label": "same"},
        ])
        self.assertNotEqual(first["evaluation"]["referenceVersion"], second["evaluation"]["referenceVersion"])

    def test_runtime_policy_is_versioned_idempotent_and_preserves_general_approval(self):
        from tools.art.likeness_library.group_lifecycle import runtime_policy, ENTRANCE, CORE, MARGIN
        from tools.art.likeness_library.policy import validate_policy
        before = load_policy()
        policy = runtime_policy(before)
        validate_policy(policy)
        self.assertEqual(policy, runtime_policy(policy))
        self.assertNotEqual(before["version"], policy["version"])
        self.assertEqual(before["status"], policy["status"])
        for category in ENTRANCE:
            rules = policy["categoryPolicies"][category]
            self.assertEqual(rules["photoRouteMinimum"], ENTRANCE[category])
            self.assertEqual(rules["identityCoreMinimumSimilarity"], CORE[category])
            self.assertEqual(rules["photoRouteMargin"], MARGIN[category])

    def test_explicit_reference_withdrawal_cannot_regain_authority_through_growth(self):
        pid = "photo:image_1000"
        (rows, report), _ = self.build(reference_exclusions={pid})
        row = next(row for row in rows if row["photoId"] == pid)
        self.assertEqual(row["membership"]["status"], "supported")
        self.assertFalse(row["membership"]["coreUse"])
        self.assertEqual(report["evaluation"]["reviewedReferenceExclusions"], [pid])

    def test_small_coherent_residual_retains_named_candidate_without_reference_claim(self):
        rows, measured, catalog = self.fixture()
        rows = [row for row in rows if row["photoId"] not in {f"photo:image_{n}" for n in range(1002, 1007)}]
        (output, report), catalog = self.build((rows, measured, catalog))
        pair = [row for row in output if row["photoId"] in {"photo:image_1000", "photo:image_1001"}]
        self.assertEqual(report["evaluation"]["independentResidualCandidates"], 1)
        self.assertTrue(all(row["membership"]["status"] == "tentative" and not row["membership"]["coreUse"] for row in pair))
        self.assertTrue(all(row["destination"].startswith("Models/Mira Vale/review/") for row in pair))
        self.assertTrue(all(row["membership"]["groupId"] is None for row in pair))
        metadata.validate_catalog(catalog)


class CleanRebaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = pathlib.Path(self.temporary.name)
        self.source = self.base / "Source"
        self.working = self.base / "Working"
        self.run = self.working / "_sandbox-state" / "clean"
        self.run.mkdir(parents=True)
        self.relative = "Potentials/Fia/gallery/fia_image_123456.jpg"
        self.source_photo = self.source / pathlib.Path(self.relative)
        self.source_photo.parent.mkdir(parents=True)
        self.source_photo.write_bytes(b"photo bytes")
        self.digest = hashlib.sha256(b"photo bytes").hexdigest()
        self.layout = {
            "source_root": self.source, "working_root": self.working,
            "sandbox_root": self.base,
            "manifest_files": {self.relative: (11, self.digest)},
        }
        (self.base / "source-manifest.json").write_text("{}", encoding="utf-8")

    def test_quality_evidence_separates_measured_unusable_from_unknown_and_multiface(self):
        settings = {"minFace": 100, "multiFace": .3}
        cases = [
            (None, 0, 0, 0, "no face found", "missing-or-unusable-measurement", False),
            ([1, 0], 150, 2, .5, "2+ faces", "ambiguous-multiface", False),
            ([1, 0], 50, 1, 0, "face too small (50px)", "measured-face-too-small", True),
            ([1, 0], 150, 1, 0, "the app's bars cover her head (screenshot)",
             "measured-head-obstruction", True),
            ([1, 0], 150, 1, 0, "unknown quality", "unclassified-quality-hold", False),
        ]
        for vec, px, faces, f2, reason, classification, candidate in cases:
            with self.subTest(classification=classification):
                evidence = clean_rebase._quality_hold_evidence(
                    SimpleNamespace(vec=vec, px=px, faces=faces, f2=f2), settings, reason,
                )
                self.assertEqual(evidence["classification"], classification)
                self.assertEqual(evidence["recoverableJunkCandidate"], candidate)
                self.assertEqual(evidence["reason"], reason)

    def test_supported_launcher_generates_synthetic_directed_candidate_viewer(self):
        fixture_root = self.base / "launcher-fixture"
        sandbox_root = fixture_root / "Sovereign Territories Sandbox"
        working = sandbox_root / "Working"
        source = sandbox_root / "Source"
        production = fixture_root / "Sovereign Territories"
        source.mkdir(parents=True)
        working.mkdir()
        (sandbox_root / "source-manifest.json").write_text(json.dumps({
            "schemaVersion": 1, "snapshotRoot": "Source", "workingRootAtCreation": "Working",
            "sourceRoot": str(production), "fileCount": 0, "totalBytes": 0, "files": [],
        }), encoding="utf-8")
        cast = working / "Angels" / "Source" / "gallery" / "angel_image_765431.jpg"
        cast.parent.mkdir(parents=True)
        cast.write_bytes(b"synthetic candidate")
        incoming = working / "Various" / "gallery" / "incoming_image_765432.jpg"
        incoming.parent.mkdir(parents=True)
        incoming.write_bytes(b"synthetic incoming")
        input_hashes = {
            cast: hashlib.sha256(cast.read_bytes()).hexdigest(),
            incoming: hashlib.sha256(incoming.read_bytes()).hexdigest(),
        }
        run = working / "_sandbox-state" / "directed-preview"
        launcher = pathlib.Path(__file__).resolve().parents[4] / "bin" / "sandbox-rebase.cmd"
        result = subprocess.run(
            [
                "cmd", "/c", "call", str(launcher), str(working), str(run),
                "--baseline", "working", "--cast-seeds", "core", "--regroup", "--directed",
                "--directed-recipe", "directed-core-continuity", "--dry-run",
                "--core-selection-preview",
            ],
            cwd=pathlib.Path(__file__).resolve().parents[4],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("experimental-directed-sandbox; preview only", result.stdout)
        self.assertIn("directed-core-continuity", result.stdout)
        report_path = run / "core-selection-preview" / "core-selection-preview.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["candidatePhotoCount"], 1)
        self.assertEqual(report["incomingVarious"]["imageFileCount"], 1)
        self.assertEqual(report["baselineInventory"]["regenerableDerivatives"]["imageFileCount"], 0)
        self.assertIn("repository catalogue deliberately not used", report["catalogSource"])
        self.assertTrue((report_path.parent / "core-selection-preview.html").is_file())
        self.assertEqual(
            {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in input_hashes},
            input_hashes,
        )

    def image_inventory_mock(self):
        categories = {"Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various"}

        def inventory(root):
            root = pathlib.Path(root)
            return sorted(
                path for path in root.rglob("*")
                if path.is_file()
                and path.relative_to(root).parts[0] in categories
                and path.parent.name in ("gallery", "review")
                and not any(part.startswith((".", "_")) for part in path.relative_to(root).parts)
                and path.suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
            )

        return SimpleNamespace(inventory=inventory)

    def test_directed_fresh_create_plan_persists_people_references_routes_and_distinct_family_names(self):
        from tools.art.likeness_library import group_lifecycle
        from tools.art.likeness_library.tests.test_directed_reformation import DirectedReformationTests
        rows, measured, empty, cohorts, _add = DirectedReformationTests().fixture()
        empty_id = "person_" + "e" * 32
        empty["people"][empty_id] = {
            "id": empty_id, "folder": "Prospects/No Evidence", "folderHistory": [],
            "displayName": "No Evidence",
            "identityAnchors": [], "protected": False,
        }
        self.source_photo.unlink()
        folders, manifest, vectors = {}, {}, {}
        for row in rows:
            relative = row["source"]
            folder = row["oldFolder"]
            path = self.source / pathlib.PurePosixPath(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = row["photoId"].encode()
            path.write_bytes(payload)
            manifest[relative] = (len(payload), hashlib.sha256(payload).hexdigest())
            category, _, name = folder.partition("/")
            folders[folder] = (category, name or "Various", self.source / pathlib.PurePosixPath(folder))
            vector = measured[relative].vec.copy()
            if category == "Angels":
                vector[1] = np.sqrt(.75)
                vector[vector == np.sqrt(.36)] = np.sqrt(.25)
            if category == "Models":
                vector[1], vector[2] = .6, np.sqrt(.28)
            vectors[relative] = vector
        catalog_path = self.working / ".likeness-library.json"
        metadata.save_catalog(empty, catalog_path)
        api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: {}, storage_root=likeness.cw.storage_root,
                photo_folders=lambda _cfg, _root: list(folders.values()), photo_key=likeness.cw.photo_key,
            ),
            settings=likeness.settings, originals=likeness.originals, nz=likeness.nz,
            chosen_keys=lambda _cfg: set(), invent_name=likeness.invent_name,
            junk_reason=lambda photo, settings: "synthetic quality hold" if photo.name.endswith("800037.jpg") else None,
        )
        policy = load_policy()
        policy["familyNaming"] = {"enabled": True, "linkMinimumBand": "yellow",
                                  "castSurnameOverrides": {"Angels/Angel Source": "Hadley"}}
        pair = {"photoIds": [cohorts["Models/Model Source"][0], cohorts["Angels/Angel Source"][0]],
                "label": "different"}
        with mock.patch.object(metadata, "path_for_root", return_value=catalog_path), \
                mock.patch.object(group_lifecycle, "review_evidence", return_value=({"pairs": [pair]}, {})):
            plan = clean_rebase.create_plan(
                {**self.layout, "manifest_files": manifest}, self.run, policy, api,
                embedder=lambda path: {
                    "v": vectors[path.relative_to(self.source).as_posix()].tolist(),
                    "faces": 1, "s": .95, "px": 150,
                },
                seed_catalog=empty, regroup=True, cast_seeds="core", review_source=self.source,
                directed_recipe="directed-core-continuity",
            )
        saved = json.loads((self.run / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(len(saved["people"]), 8)
        self.assertTrue(saved["photoGroups"])
        self.assertEqual(plan["groupLifecycle"]["evaluation"]["independentResidualCandidates"], 1)
        self.assertTrue(plan["policy"]["categoryPolicies"]["Angels"]["galleryAdmissionEnabled"])
        family = next(f for f in plan["familyNaming"]["families"] if f["rootFolder"] == "Angels/Angel Source")
        self.assertEqual(family["surname"], "Hadley")
        relative = next(row["destination"] for row in plan["photos"]
                        if row["photoId"] == cohorts["Models/Model Source"][0])
        self.assertIn("Hadley/gallery/", relative)
        person_id = next(row["membership"]["personId"] for row in plan["photos"]
                         if row["photoId"] == cohorts["Models/Model Source"][0])
        self.assertNotEqual(person_id, next(p["id"] for p in saved["people"].values()
                                           if p["folder"] == "Angels/Angel Source"))
        assessments = {item["personId"]: item for item in plan["familyNaming"]["ownerAssessment"]}
        self.assertEqual(set(assessments), set(saved["people"]))
        self.assertEqual(assessments[empty_id]["status"], "insufficient-qualified-references")
        self.assertEqual(assessments[person_id]["status"], "qualified-owner-assessed")
        self.assertEqual(assessments[person_id]["folder"], saved["people"][person_id]["folder"])
        self.assertEqual(sum(item["qualifiedReferenceCount"] for item in assessments.values()),
                         sum(row["membership"]["coreUse"] for row in plan["photos"]))
        provisional = [item for item in assessments.values() if item["identityStatus"] == "provisional"]
        self.assertEqual(len(provisional), 1)
        self.assertEqual(provisional[0]["status"], "provisional-no-reference-authority")
        self.assertEqual(provisional[0]["qualifiedReferenceCount"], 0)
        from tools.art.likeness_library.directed_reformation import unpack_runtime_decisions
        decisions = unpack_runtime_decisions(plan["groupLifecycle"]["decisionEvidence"])
        for row in plan["photos"]:
            self.assertEqual(decisions[row["photoId"]]["proposedDestination"], row["destination"])
        metadata.validate_catalog(saved)
        clean_rebase._verify_routes(plan, self.source)

    def test_synthetic_directed_residual_preview_apply_and_publication_check(self):
        from tools.art.likeness_library import group_lifecycle
        from tools.art.likeness_library.tests.test_directed_reformation import DirectedReformationTests
        rows, measured, catalog, cohorts, _add = DirectedReformationTests().fixture()
        incoming = set(cohorts["Various"])
        rows = [row for row in rows if row["photoId"] in incoming]
        for row in rows:
            path = self.source / pathlib.PurePosixPath(row["source"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(row["photoId"].encode())
            row["sha256"] = metadata.content_sha256(path)
        output, lifecycle = group_lifecycle.regroup(
            rows, measured, catalog, load_policy(), set(), "synthetic",
            at="2026-11-13T18:00:00+00:00", directed_recipe="directed-core-continuity",
            name_factory=lambda seed, _taken: "Nova " + seed[-8:],
        )
        metadata.save_catalog(catalog, self.run / "catalog.json")
        plan = {
            "status": "preview", "photos": output, "policy": load_policy(),
            "groupLifecycle": lifecycle, "catalogSHA256": metadata.content_sha256(self.run / "catalog.json"),
        }
        clean_rebase._verify_routes(plan, self.source)
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            clean_rebase.install_plan(self.layout, self.run, plan)
        self.assertEqual(plan["status"], "applied")
        clean_rebase._check_publication(self.working, plan)
        self.assertEqual(sum(row["destination"].startswith("Prospects/") for row in output), 6)
        self.assertEqual(sum(row["destination"].startswith("Potentials/") for row in output), 1)
        self.assertEqual(sum(row["destination"].startswith("Various/") for row in output), 1)
        self.assertEqual(lifecycle["assignmentSummary"]["activeVarious"], 1)
        for row in output:
            self.assertEqual(metadata.content_sha256(self.working / row["destination"]), row["sha256"])
        installed = metadata.load_catalog(self.working / ".likeness-library.json")
        self.assertEqual(sum(row["membership"]["coreUse"] for row in installed["photos"].values()), 6)

    def test_external_inventory_reuses_and_seals_one_operation(self):
        from PIL import Image
        from tools.art.likeness_library import derivatives, retained_preparation, verification_reads

        gallery = self.working / "Angels" / "Reference" / "gallery"
        gallery.mkdir(parents=True)
        paths = []
        box = [.3, .2, .3, .3]
        for index in range(2):
            path = gallery / f"reference_image_{123450 + index}.jpg"
            Image.new("RGB", (400, 600), ("red", "blue")[index]).save(path)
            paths.append(path)
        plan = {
            "workingInputs": {p.relative_to(self.working).as_posix(): metadata.content_sha256(p) for p in paths},
            "photos": [{"destination": p.relative_to(self.working).as_posix()} for p in paths],
        }
        with mock.patch.object(retained_preparation, "source_is_prepared", return_value=False), \
                mock.patch.object(retained_preparation, "crop_guard", return_value=False):
            for path in paths:
                derivatives.maintain(path, box, 120, apply=True)
            actual_verified = derivatives.verified

            def require_shared_proof(*args, **kwargs):
                self.assertIsNotNone(verification_reads.active())
                return actual_verified(*args, **kwargs)

            manifest = derivatives.manifest_path(gallery.parent)
            actual_hash = metadata.content_sha256

            def no_direct_manifest_read(path):
                if pathlib.Path(path) == manifest:
                    raise AssertionError("manifest must reuse the session's verified digest")
                return actual_hash(path)

            with mock.patch.object(derivatives, "verified", side_effect=require_shared_proof), \
                    mock.patch.object(metadata, "content_sha256", side_effect=no_direct_manifest_read):
                inventory = clean_rebase._prior_external_files(self.working, plan)

            self.assertEqual(len(inventory), 9)
            for relative, expected in inventory.items():
                self.assertEqual(metadata.content_sha256(self.working / relative), expected)

            def mutate_after_verification(*args, **kwargs):
                result = actual_verified(*args, **kwargs)
                target = result[0]
                contents = target.read_bytes()
                target.write_bytes(bytes([contents[0] ^ 1]) + contents[1:])
                return result

            with mock.patch.object(derivatives, "verified", side_effect=mutate_after_verification), \
                    self.assertRaisesRegex(ValueError, "content changed"):
                clean_rebase._prior_external_files(self.working, plan)
        self.assertIsNone(verification_reads.active())

    def test_external_inventory_seal_rejects_manifest_edit_after_cached_read(self):
        from PIL import Image
        from tools.art.likeness_library import derivatives, retained_preparation

        source = self.working / "Angels" / "Reference" / "gallery" / "reference_image_123450.jpg"
        source.parent.mkdir(parents=True)
        Image.new("RGB", (400, 600), "red").save(source)
        relative = source.relative_to(self.working).as_posix()
        plan = {"workingInputs": {relative: metadata.content_sha256(source)}, "photos": []}
        with mock.patch.object(retained_preparation, "source_is_prepared", return_value=False), \
                mock.patch.object(retained_preparation, "crop_guard", return_value=False):
            derivatives.maintain(source, None, 0, apply=True, faces=0)
            manifest = derivatives.manifest_path(source.parent.parent)
            actual_verified = derivatives.verified

            def edit_after_manifest_load(*args, **kwargs):
                result = actual_verified(*args, **kwargs)
                before = manifest.stat()
                original = manifest.read_bytes()
                changed = original.replace(b"\n", b" ", 1)
                self.assertEqual(len(changed), len(original))
                self.assertNotEqual(changed, original)
                manifest.write_bytes(changed)
                os.utime(manifest, ns=(before.st_atime_ns, before.st_mtime_ns))
                return result

            with mock.patch.object(derivatives, "verified", side_effect=edit_after_manifest_load), \
                    self.assertRaisesRegex(ValueError, "content changed"):
                clean_rebase._prior_external_files(self.working, plan)

    def test_external_inventory_refuses_changed_unprepared_native_without_derivatives(self):
        source = self.working / "Angels" / "Reference" / "gallery" / "reference_image_123450.jpg"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"old")
        relative = source.relative_to(self.working).as_posix()
        plan = {"workingInputs": {relative: metadata.content_sha256(source)}, "photos": []}
        source.write_bytes(b"new")

        with mock.patch("tools.art.likeness_library.retained_preparation.crop_guard", return_value=False), \
                self.assertRaisesRegex(ValueError, "external inventory changed"):
            clean_rebase._prior_external_files(self.working, plan)

    def test_external_inventory_reuses_matching_outer_proof_and_seals_native(self):
        from tools.art.likeness_library import retained_preparation, verification_reads

        source = self.working / "Angels" / "Reference" / "gallery" / "reference_image_123450.jpg"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"native")
        relative = source.relative_to(self.working).as_posix()
        plan = {"workingInputs": {relative: metadata.content_sha256(source)}, "photos": []}

        with mock.patch.object(retained_preparation, "crop_guard", return_value=False), \
                verification_reads.session(self.working) as proof:
            inventory = clean_rebase._prior_external_files(self.working, plan)
        self.assertEqual(inventory, plan["workingInputs"])
        self.assertEqual(proof.stats["sealReads"], 1)
        with verification_reads.session(self.working, seal_content=False), \
                self.assertRaisesRegex(ValueError, "seal policy"):
            clean_rebase._prior_external_files(self.working, plan)

    def test_external_inventory_preserves_explicit_legacy_collision_policy(self):
        from tools.art.likeness_library import derivatives, retained_preparation

        source = self.working / "Angels" / "Reference" / "gallery" / "reference_image_123450.jpg"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"native")
        relative = source.relative_to(self.working).as_posix()
        legacy = source.parent.parent / derivatives.relative_target(source, "padded")
        legacy.parent.mkdir(parents=True)
        legacy.write_bytes(b"unowned")
        plan = {
            "workingInputs": {relative: metadata.content_sha256(source)},
            "photos": [{"destination": relative}],
        }

        with mock.patch.object(retained_preparation, "crop_guard", return_value=False):
            with self.assertRaisesRegex(ValueError, "unowned legacy derivative collisions"):
                clean_rebase._prior_external_files(self.working, plan)
            inventory = clean_rebase._prior_external_files(self.working, plan, preserve_legacy=True)
        self.assertEqual(inventory[legacy.relative_to(self.working).as_posix()],
                         metadata.content_sha256(legacy))

    def test_final_membership_records_recoverable_core_locks_and_honest_rival_audit(self):
        import copy
        import json
        photos, routed, paths = [], [], {}
        folder = "Prospects/Alex Cooper"
        person_id = "person_" + "1" * 32
        catalog = {
            "schemaVersion": 1, "photos": {}, "actions": [],
            "people": {person_id: {
                "id": person_id, "folder": folder, "displayName": "Alex Cooper",
                "folderHistory": [], "identityAnchors": [], "protected": False,
            }},
        }
        for index in range(5):
            path = self.source / folder / "gallery" / f"alex_cooper_image_{123450 + index}.jpg"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"source {index}".encode())
            vector = np.zeros(8)
            vector[0], vector[index + 1] = .8, .6
            photo = clean_rebase.Photo(path, "Prospects", "Alex Cooper", "cache-sha",
                                       {"v": vector.tolist(), "faces": 1, "px": 100})
            photo.vec = vector
            photos.append(photo)
            relative = path.relative_to(self.source).as_posix()
            paths[relative] = path
            routed.append({"source": relative, "destination": relative, "sha256": metadata.content_sha256(path)})
        original_catalog = copy.deepcopy(catalog)
        policy = clean_rebase.core_protection_policy(load_policy())
        api = SimpleNamespace(cw=SimpleNamespace(photo_key=lambda name: pathlib.Path(name).stem))
        settings = {"minFace": 60, "multiFace": .3}
        advisory = clean_rebase._final_membership_outcomes(
            photos, routed, catalog, policy, settings, self.base, set(), api, self.source, paths,
        )
        self.assertEqual(advisory["automaticPhotoProtectionCount"], 0)
        self.assertEqual(advisory["automaticIdentityProtectionCount"], 0)
        self.assertEqual(catalog, original_catalog)
        self.assertTrue(all(not row["protected"] and row["coreMember"] for row in advisory["rows"]))
        policy["groupCastReviewEnabled"] = True
        outcome = clean_rebase._final_membership_outcomes(
            photos, routed, catalog, policy, settings, self.base, set(), api, self.source, paths,
        )
        self.assertEqual(outcome["automaticPhotoProtectionCount"], 5)
        self.assertEqual(outcome["automaticIdentityProtectionCount"], 1)
        self.assertEqual(outcome["higherRivalCount"], 0)
        self.assertEqual([row["ownScore"] for row in advisory["rows"]],
                         [row["ownScore"] for row in outcome["rows"]])
        json.dumps(outcome, allow_nan=False)
        self.assertTrue(all(row["protected"] and not row["anchor"] for row in outcome["rows"]))
        metadata.validate_catalog(catalog)
        self.assertEqual(len(catalog["actions"]), 6)
        for action in catalog["actions"]:
            state = action["beforeState"]
            if action["type"] == "person-protected":
                catalog["people"][action["personId"]] = state["person"]
            elif state["photo"] is None:
                del catalog["photos"][action["photoIds"][0]]
            else:
                catalog["photos"][action["photoIds"][0]] = state["photo"]
        catalog["actions"] = []
        self.assertEqual(catalog, original_catalog)

        path = self.source / "Potentials/Bianca Elm/gallery/bianca_elm_image_654321.jpg"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"rival singleton")
        photo = clean_rebase.Photo(path, "Potentials", "Bianca Elm", "cache-rival",
                                   {"v": [1.] + [0.] * 7, "faces": 1, "px": 100})
        photo.vec = np.array([1.] + [0.] * 7)
        photos.append(photo)
        relative = path.relative_to(self.source).as_posix()
        paths[relative] = path
        routed.append({"source": relative, "destination": relative, "sha256": metadata.content_sha256(path)})
        cast_path = self.source / "Sisters/Nyxene/gallery/nyxene_image_654320.jpg"
        cast_path.parent.mkdir(parents=True)
        cast_path.write_bytes(b"cast singleton")
        cast_photo = clean_rebase.Photo(cast_path, "Sisters", "Nyxene", "cache-cast",
                                        {"v": [-1.] + [0.] * 7, "faces": 1, "px": 100})
        cast_photo.vec = np.array([-1.] + [0.] * 7)
        photos.append(cast_photo)
        cast_relative = cast_path.relative_to(self.source).as_posix()
        paths[cast_relative] = cast_path
        routed.append({"source": cast_relative, "destination": cast_relative,
                       "sha256": metadata.content_sha256(cast_path)})
        before = copy.deepcopy(routed)
        outcome = clean_rebase._final_membership_outcomes(
            photos, routed, catalog, load_policy(), settings, self.base, set(), api, self.source, paths,
        )
        self.assertEqual(outcome["higherRivalCount"], 5)
        self.assertTrue(all(row["rivals"][0]["folder"] == "Potentials/Bianca Elm"
                            for row in outcome["rows"][:5]))
        self.assertIsNone(outcome["rows"][-1]["ownScore"])
        self.assertEqual(outcome["rows"][0]["castReferences"],
                         [{"folder": "Sisters/Nyxene", "score": -.8}])
        self.assertEqual(outcome["rows"][-1]["castReferences"],
                         [{"folder": "Sisters/Nyxene", "score": None}])
        self.assertEqual(len(outcome["coreReferences"]["Sisters/Nyxene"]), 1)
        json.dumps(outcome, allow_nan=False)
        self.assertEqual(outcome["automaticMoves"], 0)
        self.assertEqual(routed, before)

    def test_installed_galleries_use_shared_report_state_publication(self):
        library = [self.working / "Angels" / "Angelica"]
        reports = self.working / "_reports"
        upkeep = SimpleNamespace(
            cw=SimpleNamespace(load_cfg=lambda: {}, storage_root=lambda *_args, **_kwargs: reports),
            folders=lambda *_args: library, refresh_reports=mock.Mock(),
        )
        with mock.patch.dict("sys.modules", {"gallery_maintenance": upkeep}):
            clean_rebase._refresh_galleries(self.working, self.run)
        upkeep.refresh_reports.assert_called_once_with(
            self.working, library, self.run / "likeness-cache.json",
            self.run / "policy.json", reports / "library",
        )

    def test_final_refinement_uses_rebuilt_audit_cores_for_models_and_retained_cast(self):
        for category in ("Models", "Sisters"):
            with self.subTest(category=category):
                photos, routed, paths = [], [], {}
                catalog = {"schemaVersion": 1, "photos": {}, "people": {}, "actions": []}
                for group, direction in ((f"{category}/Alpha Ann", 0), ("Models/Beta Bee", 1)):
                    for index in range(4):
                        vector = np.zeros(12)
                        vector[direction] = .85
                        vector[2 + direction * 4 + index] = np.sqrt(1 - .85 ** 2)
                        path = self.source / group / "gallery" / f"photo_image_{100000 + len(photos)}.jpg"
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(path.as_posix().encode())
                        photo = clean_rebase.Photo(
                            path, group.split("/")[0], group.split("/")[1], "measured",
                            {"v": vector.tolist(), "faces": 1, "px": 100},
                        )
                        photo.vec = vector
                        photos.append(photo)
                path = self.source / category / "Alpha Ann/gallery/photo_image_999999.jpg"
                path.write_bytes(b"misfit")
                vector = np.array([.6, .8] + [0.] * 10)
                photo = clean_rebase.Photo(
                    path, category, "Alpha Ann", "measured",
                    {"v": vector.tolist(), "faces": 1, "px": 100},
                )
                photo.vec = vector
                photos.append(photo)
                for photo in photos:
                    relative = photo.path.relative_to(self.source).as_posix()
                    paths[relative] = photo.path
                    routed.append({
                        "source": relative, "destination": relative, "sha256": metadata.content_sha256(photo.path),
                        "photoId": metadata.photo_id_from_name(photo.name), "reason": "first pass",
                        "retainedCast": category == "Sisters" and photo.group == "Sisters",
                        "castSeedReason": "member of the current configured identity core",
                    })
                policy = clean_rebase.core_protection_policy(load_policy())
                api = SimpleNamespace(cw=SimpleNamespace(photo_key=lambda name: pathlib.Path(name).stem))
                settings = {"minFace": 60, "multiFace": .3}

                def evaluate(rows):
                    return clean_rebase._final_membership_outcomes(
                        photos, rows, catalog, policy, settings, self.base, set(), api, self.source, paths,
                        acquire_protection=False,
                    )

                first = evaluate(routed)
                comparison = first["rows"][-1]
                self.assertGreaterEqual(comparison["ownScore"], .5)
                self.assertTrue(comparison["followupCandidate"])
                self.assertEqual(comparison["refinementDecision"]["decision"], "move")
                before = copy.deepcopy(catalog)
                rows, evidence = refinement.refine_membership(routed, evaluate)
                self.assertEqual(catalog, before, "comparison passes must not acquire protection")
                self.assertEqual(rows[-1]["destination"], "Models/Beta Bee/gallery/photo_image_999999.jpg")
                self.assertEqual(evidence["moveCount"], 1)
                last = evaluate(rows)
                self.assertNotEqual(first["rows"][-1]["ownScore"], last["rows"][-1]["ownScore"])
                self.assertFalse(last["rows"][-1]["higherRival"])
                self.assertEqual(last["rows"][-1]["refinementDecision"]["decision"], "hold")
                self.assertEqual(last["automaticPhotoProtectionCount"], 0)
                catalog["photos"][routed[-1]["photoId"]] = {
                    "contentSha256": routed[-1]["sha256"], "protected": True, "rejectedPersonIds": [],
                }
                locked = evaluate(routed)["rows"][-1]
                self.assertEqual(locked["refinementDecision"]["decision"], "hold")
                self.assertIn("protected", locked["refinementDecision"]["reason"])
                photos[-1].vec = np.zeros(12)
                unavailable = evaluate(routed)
                self.assertFalse(unavailable["rows"][-1]["qualityEligible"])
                json.dumps(unavailable, allow_nan=False)

    def test_install_refuses_post_continuity_qualifying_residual_before_writes(self):
        plan = {"finalMembershipAudit": {"postContinuityPendingCount": 1}}
        with self.assertRaisesRegex(ValueError, "still has qualifying moves"):
            clean_rebase.install_plan(self.layout, self.run, plan)
        self.assertFalse((self.run / "staged").exists())
        self.assertFalse((self.run / "previous").exists())

    def plan(self):
        return {
            "status": "preview",
            "photos": [{
                "source": self.relative,
                "destination": "Angels/Angelica/review/fia_image_123456.jpg",
                "sha256": self.digest,
            }],
        }

    def test_continuity_collision_remap_records_only_actual_moves(self):
        for earlier_history in ([], ["Potentials/Original Name"]):
            with self.subTest(earlier_history=earlier_history):
                first = {
                    "id": "person_a", "folder": "Potentials/Eloise",
                    "folderHistory": list(earlier_history),
                }
                second = {
                    "id": "person_b", "folder": "Potentials/Jade", "folderHistory": [],
                }
                moved = {
                    "id": "person_c", "folder": "Potentials/Moving Person",
                    "folderHistory": ["Potentials/Earlier Person"],
                }
                catalog = {
                    "people": {person["id"]: person for person in (first, second, moved)},
                    "photos": {},
                }
                rows = [
                    {"oldFolder": first["folder"], "photoId": "photo:image_654321",
                     "destination": "Potentials/Jade/gallery/one.jpg"},
                    {"oldFolder": second["folder"], "photoId": "photo:image_345678",
                     "destination": "Various/review/two.jpg", "bestMatch": "Potentials/Jade"},
                    {"oldFolder": moved["folder"], "photoId": "photo:image_456789",
                     "destination": "Prospects/Moved Person/gallery/three.jpg"},
                ]
                clean_rebase._migrate_continuity(
                    catalog, rows, self.working, lambda _folder: [],
                )
                self.assertEqual(first["folder"], "Potentials/Eloise")
                self.assertEqual(first["folderHistory"], earlier_history)
                self.assertEqual(rows[0]["destination"], "Potentials/Eloise/gallery/one.jpg")
                self.assertEqual(rows[1]["bestMatch"], "Potentials/Eloise")
                self.assertEqual(moved["folder"], "Prospects/Moved Person")
                self.assertEqual(
                    moved["folderHistory"],
                    ["Potentials/Earlier Person", "Potentials/Moving Person"],
                )

    def continuity_merge_fixture(self):
        import copy

        folders = ("Prospects/Oldest Person", "Potentials/Younger Person")
        people = {}
        photos = {}
        rows = []
        candidates = []
        anchor_ids = []
        survivor_id = "person_" + "1" * 32
        retired_id = "person_" + "2" * 32
        unrelated_id = "person_" + "3" * 32
        ids = (survivor_id, retired_id)
        for index, (folder, name, created, person_id) in enumerate(zip(
            folders, ("Oldest Person", "Younger Person"), ("2026-10-01", "2026-10-09"), ids,
        )):
            people[person_id] = {
                "id": person_id, "folder": folder, "displayName": name,
                "folderHistory": [], "identityAnchors": [],
                "names": {
                    "originalName": name, "currentName": name, "originalSource": "recorded-history",
                },
                "protected": index == 1,
                **({"automaticProtectionOverride": "disabled"} if index == 1 else {}),
            }
            candidates.append({
                "folder": folder, "personId": person_id, "supportPhotoCount": 2,
                "name": name, "nameSource": "recorded-history", "originalName": name,
                "ageEvidence": {
                    "date": created, "status": "verified",
                    "evidence": [{"date": created, "source": "z-history-new-person"}],
                },
            })
            for photo_index in range(2):
                photo_number = 900001 + index * 10 + photo_index
                photo_id = f"photo:image_{photo_number}"
                relative = f"{folder}/gallery/{name.lower().replace(' ', '_')}_image_{photo_number}.jpg"
                path = self.working / pathlib.Path(relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                data = f"photo-{photo_number}".encode()
                path.write_bytes(data)
                digest = hashlib.sha256(data).hexdigest()
                photos[photo_id] = {
                    "contentSha256": digest, "protected": photo_number == 900012,
                    **({"automaticProtectionOverride": "enabled"} if photo_number == 900012 else {}),
                    **({"rejectedPersonIds": [unrelated_id]} if photo_number == 900002 else {}),
                }
                if photo_number == 900012:
                    anchor_ids.append(photo_id)
                rows.append({
                    "photoId": photo_id, "oldFolder": folder, "source": relative,
                    "destination": f"Prospects/Oldest Person/gallery/{path.name}",
                    "sha256": digest, "preparedSHA256": digest,
                })
        people[unrelated_id] = {
            "id": unrelated_id, "folder": "Prospects/Unrelated Person",
            "displayName": "Unrelated Person", "folderHistory": [], "identityAnchors": [],
        }
        people[retired_id]["identityAnchors"] = list(anchor_ids)
        evidence = {
            "name": "Oldest Person", "decision": "retained original identity name",
            "reviewRequired": False, "originalCandidates": candidates,
            "survivorPersonId": survivor_id, "survivorFolder": folders[0],
        }
        for row in rows:
            row["identityNameEvidence"] = copy.deepcopy(evidence)
        catalog = {
            "schemaVersion": 1, "people": people, "photos": photos, "actions": [],
        }
        return catalog, rows, survivor_id, retired_id, anchor_ids

    def protected_core_split_fixture(self):
        import copy

        person_id = "person_" + "7" * 32
        folder = "Prospects/Legacy Person"
        name = "Core Survivor"
        core_ids = [f"photo:image_{number}" for number in (920001, 920002)]
        soft_id = "photo:image_920003"
        people = {
            person_id: {
                "id": person_id, "folder": folder, "displayName": "Legacy Person",
                "folderHistory": [], "identityAnchors": [],
                "names": {
                    "originalName": name, "currentName": name,
                    "originalSource": "recorded-history",
                },
            },
        }
        photos, rows = {}, []
        photo_ids = [*core_ids, soft_id]
        evidence = {
            "name": name, "decision": "retained original identity name",
            "reviewRequired": False,
            "originalCandidates": [{
                "folder": folder, "personId": person_id, "supportPhotoCount": 2,
                "name": name, "nameSource": "recorded-history", "originalName": name,
                "corePhotoIds": core_ids, "mandatoryPhotoIds": [],
                "preservesCore": True,
                "ageEvidence": {"status": "unavailable"},
            }],
            "survivorPersonId": person_id, "survivorFolder": folder,
        }
        for index, photo_id in enumerate(photo_ids):
            number = 920001 + index
            relative = f"{folder}/gallery/legacy_image_{number}.jpg"
            path = self.working / pathlib.Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = f"protected-core-test-{number}".encode()
            path.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            record = {"contentSha256": digest, "protected": index < 2}
            if index < 2:
                record["protectionProvenance"] = {
                    "recipeVersion": "independent-gallery-loo-v1",
                    "frozenCorePhotoIds": core_ids,
                }
            photos[photo_id] = record
            destination = (
                "Prospects/Core Survivor" if index < 2 else "Prospects/Outlier Person"
            )
            row = {
                "photoId": photo_id, "oldFolder": folder, "source": relative,
                "destination": f"{destination}/gallery/{path.name}",
                "sha256": digest, "preparedSHA256": digest,
            }
            if index < 2:
                row["identityNameEvidence"] = copy.deepcopy(evidence)
            rows.append(row)
        catalog = {
            "schemaVersion": 1, "people": people, "photos": photos, "actions": [],
        }
        return catalog, rows, person_id, core_ids

    def add_automatic_core_to_merge(self, catalog, rows):
        import copy

        evidence = rows[0]["identityNameEvidence"]
        for person_index, first_row_index in enumerate((0, 2)):
            row = rows[first_row_index]
            photo_id = row["photoId"]
            catalog["photos"][photo_id].update({
                "protected": True,
                "protectionProvenance": {
                    "recipeVersion": "independent-gallery-loo-v1",
                    "frozenCorePhotoIds": [photo_id],
                },
            })
            candidate = evidence["originalCandidates"][person_index]
            candidate["corePhotoIds"] = [photo_id]
            candidate["preservesCore"] = True
        for row in rows:
            row["identityNameEvidence"] = copy.deepcopy(evidence)

    def test_continuity_migrates_verified_protected_merge_without_losing_decisions(self):
        import copy

        catalog, rows, survivor_id, retired_id, anchor_ids = self.continuity_merge_fixture()
        photo_decisions = copy.deepcopy(catalog["photos"])
        clean_rebase._migrate_continuity(
            catalog, rows, self.working, self.image_inventory_mock().inventory,
        )
        survivor = catalog["people"][survivor_id]
        retired = catalog["people"][retired_id]
        self.assertEqual(survivor["folder"], "Prospects/Oldest Person")
        self.assertEqual(survivor["displayName"], "Oldest Person")
        self.assertTrue(survivor["protected"])
        self.assertEqual(survivor["automaticProtectionOverride"], "disabled")
        self.assertEqual(set(survivor["identityAnchors"]), set(anchor_ids))
        self.assertIn("Potentials/Younger Person", survivor["folderHistory"])
        self.assertEqual(retired["mergedInto"], survivor_id)
        self.assertEqual(retired["names"]["currentName"], "Younger Person")
        self.assertEqual(retired["identityAnchors"], [])
        self.assertEqual(catalog["photos"], photo_decisions)
        metadata.validate_catalog(catalog)

    def test_continuity_keeps_core_identity_when_soft_outlier_departs(self):
        import copy

        catalog, rows, person_id, core_ids = self.protected_core_split_fixture()
        original_photos = copy.deepcopy(catalog["photos"])
        clean_rebase._migrate_continuity(
            catalog, rows, self.working, self.image_inventory_mock().inventory,
            rebase_protection=True,
        )
        person = catalog["people"][person_id]
        self.assertEqual(person["folder"], "Prospects/Core Survivor")
        self.assertEqual(person["displayName"], "Core Survivor")
        self.assertEqual(person["names"]["currentName"], "Core Survivor")
        self.assertIn("Prospects/Legacy Person", person["folderHistory"])
        self.assertEqual(catalog["photos"], original_photos)
        self.assertTrue(all(catalog["photos"][photo_id]["protected"] for photo_id in core_ids))

    def test_continuity_refuses_divided_protected_core_without_mutation(self):
        import copy

        catalog, rows, _, _ = self.protected_core_split_fixture()
        rows[1]["destination"] = rows[1]["destination"].replace(
            "Prospects/Core Survivor", "Prospects/Second Core",
        )
        before = copy.deepcopy(catalog)
        with self.assertRaisesRegex(ValueError, "protected core or mandatory photos split"):
            clean_rebase._migrate_continuity(
                catalog, rows, self.working, self.image_inventory_mock().inventory,
                rebase_protection=True,
            )
        self.assertEqual(catalog, before)

    def test_continuity_full_merge_preserves_automatic_locks_and_rejects_destination(self):
        import copy

        catalog, rows, survivor_id, _, _ = self.continuity_merge_fixture()
        self.add_automatic_core_to_merge(catalog, rows)
        locked = {
            photo_id: copy.deepcopy(record)
            for photo_id, record in catalog["photos"].items()
            if record.get("protectionProvenance")
        }
        before = copy.deepcopy(catalog)
        photo_id = next(iter(locked))
        catalog["photos"][photo_id]["rejectedPersonIds"] = [survivor_id]
        rejected = copy.deepcopy(catalog)
        with self.assertRaisesRegex(ValueError, "destination identity was explicitly rejected"):
            clean_rebase._migrate_continuity(
                catalog, rows, self.working, self.image_inventory_mock().inventory,
                rebase_protection=True,
            )
        self.assertEqual(catalog, rejected)

        catalog = before
        clean_rebase._migrate_continuity(
            catalog, rows, self.working, self.image_inventory_mock().inventory,
            rebase_protection=True,
        )
        for photo_id, record in locked.items():
            self.assertEqual(catalog["photos"][photo_id], record)
        self.assertEqual(catalog["people"][survivor_id]["folder"], "Prospects/Oldest Person")

    def test_continuity_merge_refuses_exact_rejected_destination_without_mutation(self):
        import copy

        catalog, rows, survivor_id, _, _ = self.continuity_merge_fixture()
        photo_id = rows[0]["photoId"]
        catalog["photos"][photo_id]["rejectedPersonIds"] = [survivor_id]
        before = copy.deepcopy(catalog)
        with self.assertRaisesRegex(ValueError, "destination identity was explicitly rejected"):
            clean_rebase._migrate_continuity(
                catalog, rows, self.working, self.image_inventory_mock().inventory,
            )
        self.assertEqual(catalog, before)

    def test_continuity_ignores_cast_people_with_configured_anchors(self):
        catalog, rows, survivor_id, _, _ = self.continuity_merge_fixture()
        cast_id = "person_" + "9" * 32
        gallery = self.working / "Angels" / "Cast Angel" / "gallery"
        gallery.mkdir(parents=True)
        (gallery / "cast_angel_image_7508202904299473073.jpg").write_bytes(b"cast")
        catalog["people"][cast_id] = {
            "id": cast_id, "folder": "Angels/Cast Angel", "displayName": "Cast Angel",
            "folderHistory": [], "identityAnchors": ["photo:image_7508202904299473073"],
            "protected": False,
        }
        catalog["photos"]["photo:image_7508202904299473073"] = {
            "contentSha256": "0" * 64, "protected": False,
        }
        clean_rebase._migrate_continuity(
            catalog, rows, self.working, self.image_inventory_mock().inventory,
            rebase_protection=True,
        )
        self.assertEqual(catalog["people"][cast_id]["folder"], "Angels/Cast Angel")
        self.assertEqual(catalog["people"][survivor_id]["folder"], "Prospects/Oldest Person")

    def test_continuity_merge_refuses_when_mandatory_anchor_is_not_retained_in_gallery(self):
        catalog, rows, _, _, anchor_ids = self.continuity_merge_fixture()
        anchor = next(row for row in rows if row["photoId"] == anchor_ids[0])
        anchor["destination"] = anchor["destination"].replace("/gallery/", "/review/")
        with self.assertRaisesRegex(ValueError, "mandatory anchor"):
            clean_rebase._migrate_continuity(
                catalog, rows, self.working, self.image_inventory_mock().inventory,
            )

    def test_continuity_merge_keeps_split_and_ambiguous_provenance_as_refusals(self):
        import copy

        catalog, rows, _, _, _ = self.continuity_merge_fixture()
        rows[0]["destination"] = rows[0]["destination"].replace(
            "Prospects/Oldest Person", "Prospects/Alternate Person",
        )
        before = copy.deepcopy(catalog)
        with self.assertRaisesRegex(ValueError, "identity decisions cannot migrate unambiguously"):
            clean_rebase._migrate_continuity(
                catalog, rows, self.working, self.image_inventory_mock().inventory,
            )
        self.assertEqual(catalog, before)

        catalog, rows, _, _, _ = self.continuity_merge_fixture()
        for row in rows:
            row["identityNameEvidence"]["originalCandidates"][1]["ageEvidence"]["date"] = "2026-10-01"
        before = copy.deepcopy(catalog)
        with self.assertRaisesRegex(ValueError, "identity decisions cannot migrate unambiguously"):
            clean_rebase._migrate_continuity(
                catalog, rows, self.working, self.image_inventory_mock().inventory,
            )
        self.assertEqual(catalog, before)

    def test_create_plan_protected_prospect_merge_reaches_cluster_and_continuity(self):
        plan, migrated_catalog, ids = self._protected_merge_plan(clean_rebase.core_protection_policy(load_policy()))
        oldest_id, younger_id, expected_ids = ids
        self.assertEqual(plan["policy"]["rebaseProtection"]["enabled"], True)
        routed = [row for row in plan["photos"] if row.get("identityNameEvidence")]
        self.assertEqual({row["photoId"] for row in routed}, expected_ids)
        self.assertEqual(
            {"/".join(row["destination"].split("/")[:2]) for row in routed},
            {"Prospects/Oldest Person"},
        )
        working_catalog = copy.deepcopy(migrated_catalog)
        clean_rebase._migrate_continuity(
            working_catalog, plan["photos"], self.working, self.image_inventory_mock().inventory,
        )
        self.assertEqual(working_catalog["people"][oldest_id]["folder"], "Prospects/Oldest Person")
        self.assertEqual(working_catalog["people"][younger_id]["mergedInto"], oldest_id)

    def test_create_plan_family_tree_renames_lookalike_and_records_family(self):
        policy = clean_rebase.core_protection_policy(load_policy())
        policy["familyNaming"] = {"enabled": True, "linkMinimumBand": "yellow",
                                  "castSurnameOverrides": {"Angels/Angelica": "Hadley"}}
        plan, migrated_catalog, ids = self._protected_merge_plan(policy, embedder=lambda path: {
            # The fake cast core is fixed at [1, 0]; candidates stay on its side after space centring.
            "v": [0., 1.] if "angelica" in str(path).lower() else [1., 0.],
            "faces": 1, "s": .95, "px": 100,
        })
        oldest_id, _, expected_ids = ids
        routed = [row for row in plan["photos"] if row["photoId"] in expected_ids]
        self.assertEqual({"/".join(row["destination"].split("/")[:2]) for row in routed},
                         {"Prospects/Oldest Hadley"})
        family = plan["familyNaming"]["families"][0]
        self.assertEqual((family["rootFolder"], family["surname"], family["surnameSource"]),
                         ("Angels/Angelica", "Hadley", "configured"))
        member = family["members"][0]
        self.assertEqual((member["folder"], member["previousName"], member["status"], member["band"]),
                         ("Prospects/Oldest Hadley", "Oldest Person", "renamed", "green"))
        self.assertEqual(plan["familyNaming"]["cast"]["Angels/Angelica"]["currentPersonName"], "Angelica Hadley")
        recorded = {person["folder"]: person for person in migrated_catalog["people"].values()
                    if person.get("family")}
        self.assertEqual(recorded["Angels/Angelica"]["names"]["currentName"], "Angelica Hadley")
        self.assertEqual(recorded["Prospects/Oldest Hadley"]["names"]["currentName"], "Oldest Hadley")
        self.assertEqual(recorded["Prospects/Oldest Hadley"]["family"]["referencePersonId"],
                         recorded["Angels/Angelica"]["id"])
        metadata.validate_catalog(migrated_catalog)
        # Real runs migrate continuity before placeholder people exist; replay that order on the source catalogue.
        working_catalog = json.loads((self.working / ".likeness-library.json").read_text(encoding="utf-8"))
        clean_rebase._migrate_continuity(
            working_catalog, plan["photos"], self.working, self.image_inventory_mock().inventory,
        )
        self.assertEqual(working_catalog["people"][oldest_id]["folder"], "Prospects/Oldest Hadley")
        file_name, copied, payload = clean_rebase._reset_name_file(plan, self.source, "Prospects", "Oldest Hadley")
        self.assertEqual((file_name, copied), ("z_oldest_hadley.txt", None))
        lines = payload.splitlines()
        self.assertEqual(lines[0], "name: Oldest Hadley")
        self.assertIn("2026-10-01 +2 from Various: one new person (2 photos)", lines)
        self.assertEqual(lines[-1], f"{plan['createdAt'][:10]} renamed from Oldest Person (family Hadley)")

    def _protected_merge_plan(self, policy, embedder=None):
        import json

        oldest_id = "person_" + "4" * 32
        younger_id = "person_" + "5" * 32
        cast_id = "person_" + "6" * 32
        folders = ("Prospects/Oldest Person", "Potentials/Younger Person")
        people = {
            oldest_id: {
                "id": oldest_id, "folder": folders[0], "displayName": "Oldest Person",
                "folderHistory": [], "identityAnchors": [], "protected": True,
            },
            younger_id: {
                "id": younger_id, "folder": folders[1], "displayName": "Younger Person",
                "folderHistory": [], "identityAnchors": [], "protected": True,
            },
            cast_id: {
                "id": cast_id, "folder": "Angels/Angelica", "displayName": "Angelica",
                "folderHistory": [], "identityAnchors": [],
            },
        }
        source_folders = []
        candidates_by_folder = {}
        manifest_files = {}
        for index, (folder, name, created) in enumerate((
            (folders[0], "Oldest Person", "2026-10-01"),
            (folders[1], "Younger Person", "2026-10-09"),
        )):
            path = self.source / pathlib.Path(folder)
            gallery = path / "gallery"
            gallery.mkdir(parents=True)
            (gallery / f"z_{name.lower().replace(' ', '_')}.txt").write_text(
                f"name: {name}\n{created} +2 from Various: one new person (2 photos)\n",
                encoding="utf-8",
            )
            source_folders.append((folder.split("/", 1)[0], folder.split("/", 1)[1], path))
            candidates_by_folder[folder] = []
            for photo_index in range(2):
                number = 910000 + index * 10 + photo_index
                photo_name = f"{name.lower().replace(' ', '_')}_image_{number}.jpg"
                photo_path = gallery / photo_name
                payload = f"synthetic-photo-{number}".encode()
                photo_path.write_bytes(payload)
                relative = photo_path.relative_to(self.source).as_posix()
                digest = hashlib.sha256(payload).hexdigest()
                manifest_files[relative] = (len(payload), digest)
                candidates_by_folder[folder].append(metadata.photo_id_from_name(photo_name))

        cast_path = self.source / "Angels" / "Angelica"
        cast_photo = cast_path / "gallery" / "angelica_image_919999.jpg"
        cast_photo.parent.mkdir(parents=True)
        cast_photo.write_bytes(b"cast reference")
        cast_relative = cast_photo.relative_to(self.source).as_posix()
        cast_digest = metadata.content_sha256(cast_photo)
        manifest_files[cast_relative] = (cast_photo.stat().st_size, cast_digest)
        source_folders.append(("Angels", "Angelica", cast_path))
        catalog_path = self.working / ".likeness-library.json"
        metadata.save_catalog({
            "schemaVersion": 1, "people": people, "photos": {}, "actions": [],
        }, catalog_path)
        layout = {
            **self.layout,
            "manifest_files": manifest_files,
        }
        api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: {},
                storage_root=likeness.cw.storage_root,
                photo_folders=lambda _cfg, _root: source_folders,
                photo_key=likeness.cw.photo_key,
            ),
            settings=likeness.settings, originals=likeness.originals,
            nz=likeness.nz, chosen_keys=lambda _cfg: set(),
            invent_name=lambda *_: self.fail("protected identities lost name continuity"),
        )

        def fake_cores(space, _catalog, **_kwargs):
            self.assertEqual(set(space.by_key), {"Angels/Angelica"})
            return {"Angels/Angelica": {"vector": np.array([1., 0.])}}, set(), []

        expected_ids = set(candidates_by_folder[folders[0]] + candidates_by_folder[folders[1]])

        def fake_plan(candidates, cores, **_kwargs):
            self.assertEqual(set(cores), {"Angels/Angelica"})
            self.assertEqual({row["photoId"] for row in candidates}, expected_ids)
            self.assertEqual(len(candidates), 4)
            photo_ids = sorted(expected_ids)
            destination = "Prospects/Generated"
            return {
                "assignments": [
                    {"photoId": photo_id, "destination": destination, "reason": "synthetic complete merge"}
                    for photo_id in photo_ids
                ],
                "clusters": [{
                    "clusterId": "protected-merge", "destination": destination,
                    "photoIds": photo_ids,
                }],
                "held": [],
            }

        def fake_audit(_photos, rows, *_args, **_kwargs):
            return {
                "reference": "synthetic frozen final cores", "state": "audited", "automaticMoves": 0,
                "nextPassNeeded": False,
                "rows": [{
                    **row, "higherRival": False,
                    "refinementDecision": {"decision": "hold", "reason": "synthetic stable membership"},
                } for row in rows],
            }

        with mock.patch.object(clean_rebase.metadata, "path_for_root", return_value=catalog_path), \
                mock.patch.object(clean_rebase, "frozen_identity_cores", side_effect=fake_cores), \
                mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=fake_plan), \
                mock.patch.object(clean_rebase, "_final_membership_outcomes", side_effect=fake_audit) as final_audit:
            plan = clean_rebase.create_plan(
                layout, self.run, policy, api,
                embedder=embedder or (lambda _path: {
                    "v": [1., 0.], "faces": 1, "s": .95, "px": 100,
                }),
            )
        self.assertEqual(sum(call.kwargs.get("acquire_protection", True) for call in final_audit.call_args_list), 1)
        migrated_catalog = json.loads((self.run / "catalog.json").read_text(encoding="utf-8"))
        return plan, migrated_catalog, (oldest_id, younger_id, expected_ids)

    def test_undone_attempt_is_set_aside_before_replan(self):
        for name in ("staged", "previous", "withdrawn"):
            (self.run / name / "Prospects").mkdir(parents=True)
        (self.run / "previous-catalog.json").write_text("{}", encoding="utf-8")
        (self.run / "likeness-cache.json").write_text("{}", encoding="utf-8")
        clean_rebase._set_aside_undone_attempt(self.run, {"status": "undone"})
        attempts = list((self.run / "superseded").iterdir())
        self.assertEqual(len(attempts), 1)
        self.assertEqual(sorted(path.name for path in attempts[0].iterdir()),
                         ["previous", "previous-catalog.json", "run.json", "staged", "withdrawn"])
        for name in ("staged", "previous", "withdrawn", "previous-catalog.json"):
            self.assertFalse((self.run / name).exists())
        self.assertTrue((self.run / "likeness-cache.json").exists())

    def test_cluster_names_keep_supported_identity_despite_newcomer_majority(self):
        folder = "Prospects/Old Person"
        identity = "person_" + "1" * 32
        history_folder = self.source / pathlib.Path(folder) / "gallery"
        history_folder.mkdir(parents=True)
        (history_folder / "z_old_person.txt").write_text(
            "name: Old Person\n2026-10-01 +3 from Various: one new person (3 photos)\n",
            encoding="utf-8",
        )
        catalog = {"people": {identity: {
            "id": identity, "folder": folder, "displayName": "Old Person",
        }}, "actions": []}
        by_id = {
            **{f"photo:old{index}": {"oldFolder": folder} for index in range(3)},
            **{f"photo:new{index}": {"oldFolder": "Various"} for index in range(5)},
        }
        groups = [{
            "clusterId": "joined", "destination": "Prospects/Generated",
            "photoIds": list(by_id),
        }]
        api = SimpleNamespace(invent_name=lambda *_: self.fail("supported name was not retained"))
        names, evidence = clean_rebase._cluster_name_routes(
            groups, by_id, catalog, self.source, api, 3,
        )
        self.assertEqual(names["Prospects/Generated"], "Prospects/Old Person")
        self.assertEqual(evidence["Prospects/Generated"]["decision"], "retained original identity name")

    def test_cluster_name_follows_locked_core_not_larger_soft_split(self):
        folder = "Prospects/Legacy Person"
        identity = "person_" + "8" * 32
        history_folder = self.source / pathlib.Path(folder) / "gallery"
        history_folder.mkdir(parents=True)
        (history_folder / "z_legacy_person.txt").write_text(
            "name: Core Survivor\n2026-10-01 +2 from Various: one new person (2 photos)\n",
            encoding="utf-8",
        )
        core_ids = [f"photo:image_{number}" for number in (930001, 930002)]
        soft_ids = [f"photo:image_{number}" for number in range(930003, 930007)]
        newcomer_ids = [f"photo:new-{index}" for index in range(4)]
        all_ids = [*core_ids, *soft_ids, *newcomer_ids]
        digest = "a" * 64
        catalog = {
            "people": {identity: {
                "id": identity, "folder": folder, "displayName": "Core Survivor",
            }},
            "photos": {
                photo_id: {
                    "contentSha256": digest, "protected": True,
                    "protectionProvenance": {
                        "recipeVersion": "independent-gallery-loo-v1",
                        "frozenCorePhotoIds": core_ids,
                    },
                }
                for photo_id in core_ids
            },
            "actions": [],
        }
        by_id = {
            photo_id: {
                "oldFolder": folder if photo_id in core_ids + soft_ids else "Various",
                "sha256": digest,
            }
            for photo_id in all_ids
        }
        groups = [
            {"clusterId": "soft-majority", "destination": "Prospects/Soft Cluster",
             "photoIds": soft_ids + newcomer_ids},
            {"clusterId": "locked-core", "destination": "Prospects/Core Cluster",
             "photoIds": core_ids},
        ]
        names, evidence = clean_rebase._cluster_name_routes(
            groups, by_id, catalog, self.source,
            SimpleNamespace(invent_name=lambda *_: "Fresh Person"), 2,
            rebase_protection=True,
        )
        self.assertEqual(names["Prospects/Core Cluster"], "Prospects/Core Survivor")
        self.assertEqual(evidence["Prospects/Core Cluster"]["survivorPersonId"], identity)
        self.assertEqual(names["Prospects/Soft Cluster"], "Prospects/Fresh Person")
        self.assertNotIn(
            identity,
            {row.get("personId") for row in evidence["Prospects/Soft Cluster"]["originalCandidates"]},
        )

    def test_cluster_name_merge_uses_oldest_recorded_identity_age(self):
        folders = ("Prospects/First Person", "Potentials/Second Person")
        catalog = {"people": {}, "actions": []}
        by_id = {}
        photo_ids = []
        for index, (folder, name, created) in enumerate((
            (folders[0], "First Person", "2026-10-01"),
            (folders[1], "Second Person", "2026-10-09"),
        )):
            identity = "person_" + str(index + 1) * 32
            catalog["people"][identity] = {
                "id": identity, "folder": folder, "displayName": name,
            }
            history_folder = self.source / pathlib.Path(folder) / "gallery"
            history_folder.mkdir(parents=True)
            (history_folder / f"z_{name.lower().replace(' ', '_')}.txt").write_text(
                f"name: {name}\n{created} +3 from Various: one new person (3 photos)\n",
                encoding="utf-8",
            )
            for photo_index in range(3):
                photo_id = f"photo:{index}-{photo_index}"
                by_id[photo_id] = {"oldFolder": folder}
                photo_ids.append(photo_id)
        groups = [{
            "clusterId": "merged", "destination": "Prospects/Generated",
            "photoIds": photo_ids,
        }]
        api = SimpleNamespace(invent_name=lambda *_: self.fail("verified oldest name was not retained"))
        names, evidence = clean_rebase._cluster_name_routes(
            groups, by_id, catalog, self.source, api, 3,
        )
        self.assertEqual(names["Prospects/Generated"], "Prospects/First Person")
        winner = next(
            row for row in evidence["Prospects/Generated"]["originalCandidates"]
            if row["name"] == "First Person"
        )
        self.assertEqual(winner["ageEvidence"]["evidence"][0]["source"], "z-history-new-person")

    def test_cluster_names_use_camaris_bloom_record_and_hold_ambiguous_merge_age(self):
        folder = "Potentials/Camaris"
        identity = "person_" + "3" * 32
        history_folder = self.source / pathlib.Path(folder) / "gallery"
        history_folder.mkdir(parents=True)
        (history_folder / "z_camaris_bloom.txt").write_text(
            "name: Camaris Bloom\n2026-10-19 returned to Potentials\n", encoding="utf-8",
        )
        camaris_catalog = {"people": {
            identity: {"id": identity, "folder": folder, "displayName": "Camaris"},
            "person_cast": {"id": "person_cast", "folder": "Angels/Camaris", "displayName": "Camaris"},
        }, "actions": []}
        by_id = {f"photo:c{index}": {"oldFolder": folder} for index in range(2)}
        groups = [{
            "clusterId": "camaris", "destination": "Prospects/Camaris",
            "photoIds": list(by_id),
        }]
        names, _ = clean_rebase._cluster_name_routes(
            groups, by_id, camaris_catalog, self.source,
            SimpleNamespace(invent_name=lambda *_: "Fresh Person"), 2,
            cast_folders=("Angels/Camaris",),
        )
        self.assertEqual(names["Prospects/Camaris"], "Prospects/Camaris Bloom")

        folders = ("Prospects/Older Person", "Prospects/Newer Person")
        merged_catalog = {"people": {}, "actions": []}
        merged_by_id = {}
        ids = []
        for index, (source_folder, name) in enumerate(zip(folders, ("Older Person", "Newer Person"))):
            pid = "person_" + str(index + 4) * 32
            merged_catalog["people"][pid] = {
                "id": pid, "folder": source_folder, "displayName": name,
            }
            history_folder = self.source / pathlib.Path(source_folder) / "gallery"
            history_folder.mkdir(parents=True)
            (history_folder / f"z_{name.lower().replace(' ', '_')}.txt").write_text(
                f"name: {name}\n2026-10-19 renamed from Other Person (Prospects/Other Person)\n",
                encoding="utf-8",
            )
            for photo_index in range(2):
                photo_id = f"photo:a{index}-{photo_index}"
                merged_by_id[photo_id] = {"oldFolder": source_folder}
                ids.append(photo_id)
        merged_names, merged_evidence = clean_rebase._cluster_name_routes(
            [{
                "clusterId": "ambiguous", "destination": "Prospects/Combined",
                "photoIds": ids,
            }],
            merged_by_id, merged_catalog, self.source,
            SimpleNamespace(invent_name=lambda *_: "Fresh Person"), 2,
        )
        self.assertEqual(merged_names["Prospects/Combined"], "Prospects/Fresh Person")
        self.assertTrue(merged_evidence["Prospects/Combined"]["reviewRequired"])
        self.assertIn("review original-name age evidence",
                      merged_evidence["Prospects/Combined"]["decision"])

    def test_inventory_preview_explains_cast_seed_mode_without_evaluating_it(self):
        for mode in ("all", "core"):
            with self.subTest(mode=mode):
                args = SimpleNamespace(
                    root=str(self.working), run_dir=str(self.run), policy=None,
                    apply=False, check=False, dry_run=True, undo=False, replan=False,
                    cast_seeds=mode,
                )
                output = io.StringIO()
                with mock.patch.object(clean_rebase, "validate_sandbox", return_value=self.layout), \
                        mock.patch.object(clean_rebase, "require_sandbox_output", return_value=self.run), \
                        mock.patch.object(clean_rebase.clean_preparation, "inventory", return_value={
                            self.relative: self.digest,
                        }), \
                        mock.patch.object(clean_rebase, "create_plan") as matching, \
                        mock.patch.object(clean_rebase, "_cast_seed_outcomes") as seeds, \
                        contextlib.redirect_stdout(output):
                    result = clean_rebase.command(args, SimpleNamespace())
                self.assertEqual(result, {"status": "inventory", "inputCount": 1})
                matching.assert_not_called()
                seeds.assert_not_called()
                self.assertIn(f"Cast-seed policy: {mode}.", output.getvalue())
                self.assertIn("no cast retention/release decisions or matching were evaluated", output.getvalue())
                if mode == "core":
                    self.assertIn("eligible releases under configured thresholds", output.getvalue())
                    self.assertNotIn("retain existing cast membership", output.getvalue())
                else:
                    self.assertIn("retain existing cast membership", output.getvalue())

    def test_core_seed_policy_preserves_protection_and_releases_only_noncore_cast(self):
        folder = "Angels/Angelica"
        names = {
            "anchor": "angelica_image_111111.jpg",
            "core": "angelica_image_222222.jpg",
            "protected": "angelica_image_333333.jpg",
            "workflow": "angelica_image_444444.jpg",
            "low": "angelica_image_555555.jpg",
        }
        entries = []
        for key, name in names.items():
            path = self.source / folder / "gallery" / name
            entries.append((
                path.relative_to(self.source).as_posix(),
                clean_rebase.Photo(
                    path, "Angels", "Angelica", key,
                    {"v": [1., 0.], "faces": 1, "px": 100},
                ),
                "gallery",
                key,
            ))
        ids = {key: metadata.photo_id_from_name(name) for key, name in names.items()}
        catalog = {
            "people": {
                "angelica": {
                    "folder": folder, "identityAnchors": [ids["anchor"]], "protected": False,
                },
            },
            "photos": {ids["protected"]: {"protected": True}},
        }
        core = {
            "corePhotoIds": [ids["anchor"], ids["core"]],
            "photoScores": {
                names["anchor"]: .8, names["core"]: .7, names["protected"]: .6,
                names["workflow"]: .5, names["low"]: .1,
            },
        }
        api = SimpleNamespace(cw=SimpleNamespace(
            photo_key=lambda name: pathlib.Path(name).stem,
        ))
        retained, released, evidence = clean_rebase._cast_seed_outcomes(
            entries, {folder: core}, catalog,
            {pathlib.Path(names["workflow"]).stem}, load_policy(), api, "core", 60,
        )
        self.assertEqual(len(retained), 4)
        self.assertEqual(set(released), {f"{folder}/gallery/{names['low']}"})
        low = evidence[f"{folder}/gallery/{names['low']}"]
        self.assertFalse(low["retainedCast"])
        self.assertTrue(low["releasedCast"])
        self.assertEqual(low["castSeedScore"], .1)
        self.assertEqual(low["castSeedThreshold"], .3)
        self.assertTrue(any(row["castSeedAnchor"] for row in retained))
        self.assertTrue(any(row["castSeedProtectedPhoto"] for row in retained))
        self.assertTrue(any(row["castSeedWorkflowSelected"] for row in retained))
        catalog["people"]["angelica"]["protected"] = True
        retained_all, released_all, _ = clean_rebase._cast_seed_outcomes(
            entries, {folder: core}, catalog,
            {pathlib.Path(names["workflow"]).stem}, load_policy(), api, "core", 60,
        )
        self.assertEqual(len(retained_all), 5)
        self.assertEqual(released_all, {})
        trial = clean_rebase.core_protection_policy(load_policy())
        retained_core, released_core, _ = clean_rebase._cast_seed_outcomes(
            entries, {folder: core}, catalog,
            {pathlib.Path(names["workflow"]).stem}, trial, api, "core", 60,
        )
        self.assertEqual(len(retained_core), 4)
        self.assertEqual(set(released_core), {f"{folder}/gallery/{names['low']}"})
        self.assertTrue(all(row["castSeedProtectedIdentity"] for row in retained_core))
        self.assertTrue(all(row["castSeedThreshold"] == .40 for row in retained_core))

    def test_core_seed_policy_refuses_undersized_unprotected_identity(self):
        folder = "Sisters/Drakniss"
        name = "drakniss_image_123456.jpg"
        path = self.source / folder / "gallery" / name
        photo = clean_rebase.Photo(
            path, "Sisters", "Drakniss", "digest",
            {"v": [1., 0.], "faces": 1, "px": 100},
        )
        entry = (path.relative_to(self.source).as_posix(), photo, "gallery", "digest")
        core = {
            "corePhotoIds": [], "photoScores": {name: .1},
        }
        api = SimpleNamespace(cw=SimpleNamespace(photo_key=lambda value: value))
        with self.assertRaisesRegex(ValueError, "below the configured 4-photo"):
            clean_rebase._cast_seed_outcomes(
                [entry], {folder: core}, {"people": {}, "photos": {}},
                set(), load_policy(), api, "core", 60,
            )

    def test_released_cast_routes_require_core_policy_and_threshold_evidence(self):
        relative = "Angels/Angelica/gallery/angelica_image_123456.jpg"
        path = self.source / pathlib.Path(relative)
        path.parent.mkdir(parents=True)
        path.write_bytes(b"cast source")
        row = {
            "source": relative,
            "destination": "Various/review/angelica_image_123456.jpg",
            "sha256": hashlib.sha256(b"cast source").hexdigest(),
            "retainedCast": False,
            "releasedCast": True,
            "castSeedScore": .12,
            "castSeedThreshold": load_policy()["categoryPolicies"]["Angels"][
                "identityCoreMinimumSimilarity"
            ],
            "castSeedCore": False,
            "castSeedAnchor": False,
            "castSeedProtectedIdentity": False,
            "castSeedProtectedPhoto": False,
            "castSeedWorkflowSelected": False,
            "castSeedDecision": "released",
            "castSeedReason": "outside current core",
        }
        plan = {
            "photos": [row], "castSeedPolicy": "core", "policy": load_policy(),
        }
        clean_rebase._verify_routes(plan, self.source)
        retained = {
            **row, "destination": relative, "photoId": "photo:image_123456",
            "retainedCast": True, "releasedCast": False, "castSeedDecision": "retained",
            "castSeedReason": "member of the current configured identity core",
            "reason": "initially retained",
        }

        def evaluate(rows):
            moved = rows[0]["destination"] != relative
            return {"reference": "frozen final cores", "rows": [{
                **rows[0], "higherRival": not moved, "ownScore": .6,
                "rivals": [{"score": .8}],
                "refinementDecision": {
                    "decision": "hold" if moved else "move",
                    "destination": "Models/Other/gallery", "lead": .2,
                    "reason": "no higher rival" if moved else "qualifying comparison",
                },
            }]}

        refined, _ = refinement.refine_membership([retained], evaluate)
        refined_plan = {**plan, "photos": refined}
        clean_rebase._verify_routes(refined_plan, self.source)
        refined[0]["castSeedDecision"] = "retained"
        with self.assertRaisesRegex(ValueError, "complete policy evidence"):
            clean_rebase._verify_routes(refined_plan, self.source)
        plan["castSeedPolicy"] = "all"
        with self.assertRaisesRegex(ValueError, "cannot change cast membership"):
            clean_rebase._verify_routes(plan, self.source)

    def test_install_preserves_cast_core_and_old_categories_and_checks_every_copy(self):
        old = self.working / "Potentials" / "Old" / "gallery"
        old.mkdir(parents=True)
        (old / "old.jpg").write_bytes(b"old")
        cast = self.working / "Angels" / "Angelica" / "gallery"
        cast.mkdir(parents=True)
        (cast / "anchor.jpg").write_bytes(b"anchor")
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            plan = self.plan()
            clean_rebase.install_plan(self.layout, self.run, plan)
        self.assertEqual(plan["status"], "applied")
        self.assertEqual((cast / "anchor.jpg").read_bytes(), b"anchor")
        self.assertEqual(
            (cast.parent / "review" / self.source_photo.name).read_bytes(), b"photo bytes"
        )
        self.assertEqual(
            (self.run / "previous" / "Potentials" / "Old" / "gallery" / "old.jpg").read_bytes(),
            b"old",
        )
        self.assertEqual(self.source_photo.read_bytes(), b"photo bytes")
        clean_rebase.undo_plan(self.layout, self.run, plan)
        self.assertEqual(plan["status"], "undone")
        self.assertEqual((old / "old.jpg").read_bytes(), b"old")
        self.assertFalse((cast.parent / "review" / self.source_photo.name).exists())
        self.assertEqual((cast / "anchor.jpg").read_bytes(), b"anchor")

    def test_rejects_cast_gallery_destination_and_changed_source_before_install(self):
        plan = self.plan()
        plan["photos"][0]["destination"] = "Angels/Angelica/gallery/new.jpg"
        with self.assertRaisesRegex(ValueError, "never the cast core"):
            clean_rebase._verify_routes(plan, self.source)
        plan = self.plan()
        self.source_photo.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "source changed"):
            clean_rebase._verify_routes(plan, self.source)
        self.assertFalse((self.run / "previous").exists())

    def prepare_catalogue(self):
        catalog_path = self.run / "catalog.json"
        metadata.save_catalog(
            {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
            catalog_path,
        )
        plan = self.plan()
        plan["catalogSHA256"] = metadata.content_sha256(catalog_path)
        return plan

    def test_catalogue_and_various_hold_install_undo_preserve_previous_bytes(self):
        local = self.working / ".likeness-library.json"
        previous = b'{"schemaVersion":1,"people":{},"photos":{},"actions":[]}\n'
        local.write_bytes(previous)
        plan = self.prepare_catalogue()
        plan["photos"][0]["destination"] = f"Various/review/{self.source_photo.name}"
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            clean_rebase.install_plan(self.layout, self.run, plan)
        destination = self.working / plan["photos"][0]["destination"]
        self.assertEqual(destination.read_bytes(), b"photo bytes")
        self.assertEqual(metadata.load_catalog(local), metadata.load_catalog(self.run / "catalog.json"))
        self.assertEqual((self.run / "previous-catalog.json").read_bytes(), previous)
        clean_rebase.undo_plan(self.layout, self.run, plan)
        self.assertEqual(local.read_bytes(), previous)
        self.assertFalse(destination.exists())
        self.assertEqual(self.source_photo.read_bytes(), b"photo bytes")

    def test_current_various_overlay_replaces_by_id_and_preserves_raw_versions(self):
        import json

        for category in ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various"):
            (self.source / category).mkdir(parents=True, exist_ok=True)
            (self.working / category).mkdir(parents=True, exist_ok=True)
        current_gallery = self.working / "Various" / "gallery"
        current_gallery.mkdir(parents=True, exist_ok=True)
        changed = current_gallery / "incoming_image_123456.jpg"
        changed.write_bytes(b"new working bytes")
        added = current_gallery / "incoming_image_654321.jpg"
        added.write_bytes(b"new stable ID")
        no_id = current_gallery / "incoming_without_id.jpg"
        no_id.write_bytes(b"new unlabelled image")
        run = self.working / "_sandbox-state" / "overlay-run"
        run.mkdir(parents=True)

        layout = {
            **self.layout,
            "source_root": self.source,
            "working_root": self.working,
            "sandbox_root": self.base,
            "manifest_files": {self.relative: (11, self.digest)},
        }
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            rows, current = clean_rebase._current_various_overlay_rows(layout)
            self.assertEqual(len(rows), 1)
            self.assertEqual(len(current), 3)
            overlay_layout = clean_rebase._create_source_overlay(layout, run)
        manifest = json.loads((run / "source-overlay" / "overlay.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["immutableInputCount"], 1)
        self.assertEqual(manifest["replacementCount"], 1)
        self.assertEqual(manifest["newInputCount"], 2)
        overlay_path = overlay_layout["source_root"] / self.relative
        self.assertEqual(overlay_path.read_bytes(), b"new working bytes")
        self.assertEqual(self.source_photo.read_bytes(), b"photo bytes")
        recovery = manifest["rawRecovery"]
        self.assertEqual(len(recovery), 4)
        self.assertEqual(
            {record["role"] for record in recovery},
            {"immutable-original", "working-various"},
        )
        recovered = {
            record["role"]: (run / "source-overlay" / record["path"]).read_bytes()
            for record in recovery
            if record["role"] == "immutable-original"
            or record["source"].endswith("incoming_image_123456.jpg")
        }
        self.assertEqual(recovered["immutable-original"], b"photo bytes")
        self.assertEqual(recovered["working-various"], b"new working bytes")

        (run / "source-overlay").joinpath(*pathlib.PurePosixPath(recovery[0]["path"]).parts).write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "raw recovery copy changed"):
            clean_rebase._verify_source_overlay(layout, run)

    def test_working_baseline_covers_current_galleries_and_excludes_source_only_inputs(self):
        import json

        current = self.working / self.relative
        current.parent.mkdir(parents=True)
        current.write_bytes(b"current assigned bytes")
        historical_only = self.source / "Angels/Old/gallery/old_image_888888.jpg"
        historical_only.parent.mkdir(parents=True)
        historical_only.write_bytes(b"no longer active")
        added_relative = "Artists/Painter/New/gallery/new_image_777777.jpg"
        added = self.working / added_relative
        added.parent.mkdir(parents=True)
        added.write_bytes(b"new assigned artist")
        incoming = self.working / "Various/gallery/incoming_image_123456.jpg"
        incoming.parent.mkdir(parents=True)
        incoming.write_bytes(b"new incoming replacement")
        (self.working / "_reports").mkdir()
        (self.working / "_reports/not_an_input.jpg").write_bytes(b"generated")

        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            layout = clean_rebase._create_source_overlay(self.layout, self.run, current_working=True)
            rows = clean_rebase.clean_preparation.inventory(layout)
            curation = clean_rebase._curation_inventory(layout)

        self.assertEqual(set(rows), {self.relative, added_relative})
        self.assertEqual(rows[self.relative], metadata.content_sha256(incoming))
        self.assertEqual(curation[self.relative], metadata.content_sha256(current))
        self.assertNotIn(historical_only.relative_to(self.source).as_posix(), rows)
        self.assertEqual(self.source_photo.read_bytes(), b"photo bytes")
        receipt = json.loads((self.run / "source-overlay/overlay.json").read_text())
        self.assertEqual(receipt["baselineMode"], "working")
        self.assertEqual(receipt["baselineInputCount"], 2)
        self.assertEqual(receipt["immutableInputCount"], 0)
        self.assertEqual(list((self.working / "_tmp").iterdir()), [])

    def test_overlay_collapses_various_exact_bytes_before_preparation_across_id_styles(self):
        baseline = self.working / self.relative
        baseline.parent.mkdir(parents=True)
        baseline.write_bytes(b"photo bytes")
        various = self.working / "Various" / "gallery"
        various.mkdir(parents=True)
        names = [
            "facebook_1791422955236_123456.jpg", "various_image_654321.jpg",
            "odd incoming name.jpg",
        ]
        for name in names:
            (various / name).write_bytes(b"photo bytes")
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            layout = clean_rebase._create_source_overlay(self.layout, self.run, current_working=True)
            inputs = clean_rebase.clean_preparation.inventory(layout)
            current = clean_rebase._curation_inventory(layout)
        self.assertEqual(inputs, {self.relative: self.digest})
        self.assertEqual(len(current), 4)
        manifest = layout["source_overlay_manifest"]
        self.assertEqual(manifest["newInputCount"], 0)
        self.assertEqual(manifest["workingVariousCount"], 3)
        self.assertEqual({row["target"] for row in manifest["currentVarious"]}, {self.relative})
        self.assertEqual(len(manifest["rawRecovery"]), 2)
        self.assertTrue(all(path.is_file() for path in various.iterdir()))

    def test_overlay_does_not_deduplicate_replaced_old_bytes_or_artist_scope(self):
        baseline = self.working / self.relative
        baseline.parent.mkdir(parents=True)
        baseline.write_bytes(b"photo bytes")
        artist = self.working / "Artists/Painter/Person/gallery/person_image_999999.jpg"
        artist.parent.mkdir(parents=True)
        artist.write_bytes(b"artist bytes")
        various = self.working / "Various/gallery"
        various.mkdir(parents=True)
        for name, payload in (
            ("new_image_123456.jpg", b"changed bytes"),
            ("old_image_888888.jpg", b"photo bytes"),
            ("copy_image_777777.jpg", b"artist bytes"),
        ):
            (various / name).write_bytes(payload)
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            layout = clean_rebase._create_source_overlay(self.layout, self.run, current_working=True)
            inputs = clean_rebase.clean_preparation.inventory(layout)
        self.assertEqual(len(inputs), 4)
        self.assertEqual(inputs[self.relative], metadata.content_sha256(various / "new_image_123456.jpg"))
        self.assertEqual(layout["source_overlay_manifest"]["replacementCount"], 1)

    def test_raw_named_id_replacement_is_resolved_without_originals_renames(self):
        baseline = self.working / self.relative
        baseline.parent.mkdir(parents=True)
        baseline.write_bytes(b"photo bytes")
        incoming = self.working / "Various/gallery/facebook_1791422955236_123456.jpg"
        incoming.parent.mkdir(parents=True)
        incoming.write_bytes(b"updated raw bytes")
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            layout = clean_rebase._create_source_overlay(self.layout, self.run, current_working=True)
            inputs = clean_rebase.clean_preparation.inventory(layout)
        self.assertEqual(inputs, {self.relative: metadata.content_sha256(incoming)})
        self.assertEqual(layout["source_overlay_manifest"]["replacementCount"], 1)
        self.assertTrue(incoming.is_file())

    def test_explicit_various_identity_does_not_lose_naming_scope_to_byte_alias(self):
        baseline = self.working / self.relative
        baseline.parent.mkdir(parents=True)
        baseline.write_bytes(b"photo bytes")
        incoming = self.working / "Various/Named Person/gallery/person_image_654321.jpg"
        incoming.parent.mkdir(parents=True)
        incoming.write_bytes(b"photo bytes")
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            layout = clean_rebase._create_source_overlay(self.layout, self.run, current_working=True)
            inputs = clean_rebase.clean_preparation.inventory(layout)
        self.assertEqual(set(inputs), {self.relative, incoming.relative_to(self.working).as_posix()})

    def test_overlay_copy_failure_cleans_owner_locked_stage(self):
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}), \
                mock.patch.object(clean_rebase.shutil, "copy2", side_effect=OSError("copy failed")):
            with self.assertRaisesRegex(OSError, "copy failed"):
                clean_rebase._create_source_overlay(self.layout, self.run)

        self.assertFalse((self.run / "source-overlay").exists())
        self.assertEqual(list((self.working / "_tmp").iterdir()), [])

    def test_curation_retains_verified_original_beside_overlay_replacement(self):
        original = self.working / self.relative
        original.parent.mkdir(parents=True)
        original.write_bytes(self.source_photo.read_bytes())
        incoming = self.working / "Various" / "gallery" / "incoming_image_123456.jpg"
        incoming.parent.mkdir(parents=True)
        incoming.write_bytes(b"new working bytes")
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            layout = clean_rebase._create_source_overlay(self.layout, self.run)
            current = clean_rebase._curation_inventory(layout)
            self.assertEqual(current[self.relative], self.digest)
            self.assertEqual(
                current[incoming.relative_to(self.working).as_posix()],
                metadata.content_sha256(incoming),
            )
            self.assertEqual(len(current), 2)

            original.write_bytes(b"unverified original changes")
            with self.assertRaisesRegex(ValueError, "not safely isolated"):
                clean_rebase._curation_inventory(layout)
            original.write_bytes(self.source_photo.read_bytes())

            extra = self.working / "Models" / "Other" / "gallery" / original.name
            extra.parent.mkdir(parents=True)
            extra.write_bytes(original.read_bytes())
            with self.assertRaisesRegex(ValueError, "not safely isolated"):
                clean_rebase._curation_inventory(layout)
            extra.unlink()

            layout["source_overlay_manifest"]["currentVarious"][0]["target"] = "Various/gallery/other.jpg"
            with self.assertRaisesRegex(ValueError, "not safely isolated"):
                clean_rebase._curation_inventory(layout)
            layout["source_overlay_manifest"]["currentVarious"][0]["target"] = self.relative
            moved = self.working / "Angels" / "Angelica" / "review" / original.name
            moved.parent.mkdir(parents=True)
            original.rename(moved)
            current = clean_rebase._curation_inventory(layout)
            self.assertEqual(current[moved.relative_to(self.working).as_posix()], self.digest)
            self.assertEqual(len(current), 2)

    def test_overlay_isolates_timestamp_collisions_and_deduplicates_exact_copies(self):
        import json

        for category in ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various"):
            (self.source / category).mkdir(parents=True, exist_ok=True)
            (self.working / category).mkdir(parents=True, exist_ok=True)
        source = self.source / "Potentials" / "Lyra" / "gallery" / "lyra_caldwell_shot_20261010125400.jpg"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"immutable Lyra photo")
        various = self.working / "Various"
        (various / "gallery").mkdir(parents=True)
        (various / "review").mkdir(parents=True)
        screenshot = various / "gallery" / "Screenshot_20261010_125400_Facebook.jpg"
        screenshot.write_bytes(b"different screenshot sharing a timestamp")
        lyra = various / "review" / source.name
        lyra.write_bytes(source.read_bytes())
        duplicate_name = "Screenshot_20260902_203835_Facebook.jpg"
        duplicate_a = various / "gallery" / duplicate_name
        duplicate_b = various / "gallery" / "Screenshot_20260902_203835_Facebook (1).jpg"
        duplicate_a.write_bytes(b"same incoming image")
        duplicate_b.write_bytes(b"same incoming image")
        no_id = various / "gallery" / "local_image_without_id.jpg"
        no_id.write_bytes(b"unlabelled incoming image")

        run = self.working / "_sandbox-state" / "collision-run"
        run.mkdir(parents=True)
        relative = source.relative_to(self.source).as_posix()
        layout = {
            **self.layout,
            "source_root": self.source,
            "working_root": self.working,
            "sandbox_root": self.base,
            "manifest_files": {
                self.relative: (11, self.digest),
                relative: (source.stat().st_size, hashlib.sha256(source.read_bytes()).hexdigest()),
            },
        }
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            overlay_layout = clean_rebase._create_source_overlay(layout, run)
        manifest = json.loads((run / "source-overlay" / "overlay.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["immutableInputCount"], 2)
        self.assertEqual(manifest["newInputCount"], 3)
        self.assertEqual(manifest["workingVariousCount"], 5)
        self.assertTrue(any(row["sanitized"] for row in manifest["currentVarious"]))
        self.assertEqual(
            overlay_layout["manifest_files"][relative][1],
            hashlib.sha256(source.read_bytes()).hexdigest(),
        )
        self.assertEqual(source.read_bytes(), b"immutable Lyra photo")
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            current_inputs = clean_rebase._curation_inventory(overlay_layout)
        self.assertEqual(len(current_inputs), 5)
        self.assertTrue(any(record["role"] == "working-various-duplicate" for record in manifest["rawRecovery"]))

        # Production also keeps the person's own copy: two identical inputs plus the isolated screenshot.
        person_copy = self.working / relative
        person_copy.parent.mkdir(parents=True)
        person_copy.write_bytes(source.read_bytes())
        with mock.patch.dict("sys.modules", {"image_preparation": self.image_inventory_mock()}):
            current_inputs = clean_rebase._curation_inventory(overlay_layout)
            self.assertEqual(len(current_inputs), 6)
            self.assertIn(screenshot.relative_to(self.working).as_posix(), current_inputs)
            stranger = self.working / "Models" / "Other" / "gallery" / "other_shot_20261010125400.jpg"
            stranger.parent.mkdir(parents=True)
            stranger.write_bytes(b"unrelated photo with the same timestamp")
            with self.assertRaisesRegex(ValueError, "not safely isolated"):
                clean_rebase._curation_inventory(overlay_layout)

    def test_undo_removes_created_local_catalogue(self):
        plan = self.prepare_catalogue()
        local = self.working / ".likeness-library.json"
        self.assertFalse(local.exists())
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            clean_rebase.install_plan(self.layout, self.run, plan)
        self.assertTrue(local.is_file())
        clean_rebase.undo_plan(self.layout, self.run, plan)
        self.assertFalse(local.exists())

    def test_changed_local_catalogue_prevents_rebuild_undo(self):
        plan = self.prepare_catalogue()
        with mock.patch("library_backup.latest_work_root_backup", return_value=self.base), \
                mock.patch("library_backup.verify_backup"):
            clean_rebase.install_plan(self.layout, self.run, plan)
        local = self.working / ".likeness-library.json"
        local.write_bytes(local.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "catalogue changed"):
            clean_rebase.undo_plan(self.layout, self.run, plan)
        self.assertEqual(plan["status"], "applied")
        self.assertTrue((self.working / plan["photos"][0]["destination"]).is_file())

    def test_creation_uses_empty_cache_and_only_cast_references(self):
        cast_folder = self.source / "Angels" / "Angelica"
        (cast_folder / "gallery").mkdir(parents=True)
        (cast_folder / "gallery" / "angelica_image_654321.jpg").write_bytes(b"cast")
        api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: {},
                storage_root=likeness.cw.storage_root,
                photo_folders=lambda cfg, root: [
                    ("Potentials", "Fia", self.source_photo.parent.parent),
                    ("Angels", "Angelica", cast_folder),
                ],
                photo_key=likeness.cw.photo_key,
            ),
            settings=likeness.settings, originals=likeness.originals,
            nz=likeness.nz, chosen_keys=lambda cfg: set(),
            invent_name=lambda seed, taken: "New Person",
        )

        real_frozen_identity_cores = clean_rebase.frozen_identity_cores
        core_calls = 0

        def fake_cores(space, catalog, **kwargs):
            nonlocal core_calls
            core_calls += 1
            if core_calls > 1:
                return real_frozen_identity_cores(space, catalog, **kwargs)
            self.assertEqual(set(space.by_key), {"Angels/Angelica"})
            self.assertTrue(all(photo.group == "Angels" for photo in space.photos))
            return {"Angels/Angelica": {"vector": np.array([1., 0.])}}, set(), []

        def fake_plan(candidates, cores, **kwargs):
            self.assertEqual(len(candidates), 1)
            self.assertEqual(
                candidates[0]["photoId"],
                metadata.photo_id_from_name(
                    likeness.originals.standard_name(self.source_photo.name, "incoming"),
                ) or f"photo:pic_{likeness.originals.content_id(self.source_photo)}",
            )
            self.assertEqual(candidates[0]["sourceFolder"], "Various")
            self.assertEqual(candidates[0]["sourceBucket"], "Pool")
            self.assertEqual(set(cores), {"Angels/Angelica"})
            return {
                "assignments": [], "clusters": [],
                "held": [{
                    "photoId": candidates[0]["photoId"],
                    "reviewDestination": "Angels/Angelica/review",
                    "reason": "cast review",
                }],
            }

        with mock.patch.object(clean_rebase, "frozen_identity_cores", side_effect=fake_cores), \
                mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=fake_plan):
            class FixtureEmbedder:
                evidence_root = None

                def configure_evidence(self, root, library_root=None):
                    self.evidence_root = pathlib.Path(root)

                def __call__(self, path):
                    return {
                        "v": [1., 0.] if "fia" in path.name else [0., 1.],
                        "faces": 1, "s": .95, "px": 100,
                    }

            fixture_embedder = FixtureEmbedder()
            result = clean_rebase.create_plan(
                self.layout, self.run, load_policy(), api,
                embedder=fixture_embedder,
            )
            self.assertGreaterEqual(core_calls, 2)
            refinement_evidence = result["membershipRefinement"]
            self.assertIn(refinement_evidence["stopReason"], ("stable", "pass-limit"))
            self.assertEqual(result["finalMembershipAudit"]["automaticMoves"], refinement_evidence["moveCount"])
            self.assertEqual(result["finalMembershipAudit"]["state"], "refined-then-audited")
            self.assertIn("refinement.py", result["implementationHashes"])
            for row in result["photos"]:
                if row.get("photoIdOrigin") == "originals-content-id":
                    name = pathlib.PurePosixPath(row["destination"]).name
                    self.assertEqual(metadata.photo_id_from_name(name), row["photoId"])
                    self.assertTrue(name.startswith("angelica_pic_"))
            self.assertEqual(
                fixture_embedder.evidence_root,
                self.working / "_likeness" / "general" / "face-evidence",
            )
            unused_embedder = mock.Mock(
                side_effect=AssertionError("replan must reuse its own measurements"),
            )
            unused_embedder.needs_alignment_evidence.return_value = False
            with mock.patch.object(api, "Embedder", create=True, return_value=unused_embedder):
                replanned = clean_rebase.create_plan(
                    self.layout, self.run, load_policy(), api, reuse_measurements=True,
                )
            self.assertTrue(replanned["cacheMeasurementsReusedForReplan"])
            class EvidenceRefreshingEmbedder:
                def __init__(self):
                    self.calls = []
                    self.evidence_root = None

                def configure_evidence(self, root, library_root=None):
                    self.evidence_root = pathlib.Path(root)

                def needs_alignment_evidence(self, data, _path):
                    return data.get("alignmentEvidence") != {"state": "persisted"}

                def __call__(self, path):
                    self.calls.append(pathlib.Path(path))
                    return {
                        "v": [1., 0.] if "fia" in path.name else [0., 1.],
                        "faces": 1, "s": .95, "px": 100,
                        "alignmentEvidence": {"state": "persisted"},
                    }

            refreshing_embedder = EvidenceRefreshingEmbedder()
            clean_rebase.create_plan(
                self.layout, self.run, load_policy(), api, embedder=refreshing_embedder,
                reuse_measurements=True,
            )
            self.assertEqual(len(refreshing_embedder.calls), 2)
            self.assertEqual(
                refreshing_embedder.evidence_root,
                self.working / "_likeness" / "general" / "face-evidence",
            )
            import json
            saved_cache = json.loads((self.run / "likeness-cache.json").read_text(encoding="utf-8"))
            self.assertTrue(all(
                row["alignmentEvidence"] == {"state": "persisted"}
                for row in saved_cache["emb"].values()
            ))
        self.assertTrue(result["embeddingCacheStartedEmpty"])
        self.assertEqual(result["referenceFolders"], ["Angels/Angelica"])
        self.assertEqual(result["candidateCount"], 1)
        with self.assertRaisesRegex(ValueError, "empty embedding cache"):
            clean_rebase.create_plan(self.layout, self.run, load_policy(), api)

    def test_creation_accepts_raw_download_id_without_source_rename(self):
        relative = "Various/gallery/.facebook_1792598648554_7518703682028564674.jpg"
        path = self.source / pathlib.Path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.source_photo.rename(path)
        self.layout["manifest_files"] = {relative: (11, self.digest)}
        self.relative, self.source_photo = relative, path
        self.test_creation_uses_empty_cache_and_only_cast_references()
        self.assertTrue(path.is_file())
        import json
        plan = json.loads((self.run / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["actions"], [])

    def test_creation_accepts_content_id_without_preparation_or_source_rename(self):
        relative = "Various/gallery/fia download.jpg"
        path = self.source / pathlib.Path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.source_photo.rename(path)
        self.layout["manifest_files"] = {relative: (11, self.digest)}
        self.relative, self.source_photo = relative, path
        original = path.read_bytes()
        self.test_creation_uses_empty_cache_and_only_cast_references()
        self.assertEqual(path.read_bytes(), original)

    def test_incoming_ids_never_override_ambiguous_or_existing_ids(self):
        names = [
            ".facebook_123_654321.jpg", "incoming_image_654321.jpg",
            ".facebook_123_111111.jpg", "facebook_456_111111.jpg",
            ".facebook_123_222222.jpg", "unknown.jpg",
        ]
        photos = [
            SimpleNamespace(path=self.source / "Various" / "gallery" / name,
                            name=name, group="Various")
            for name in names
        ]
        for photo in photos:
            photo.path.parent.mkdir(parents=True, exist_ok=True)
            photo.path.write_bytes(photo.name.encode())
        unknown = photos[-1].path
        ids = clean_rebase._matching_photo_ids(photos, self.source, likeness)
        self.assertEqual(list(ids.values()), [
            None, "photo:image_654321", None, None, "photo:image_222222",
            f"photo:pic_{likeness.originals.content_id(unknown)}",
        ])

    def test_nonstandard_names_get_content_ids_and_byte_duplicates_are_held(self):
        files = {
            "Prospects/Brielle Carter/gallery/brielle_carter_pose_1.jpg": b"brielle pose",
            "Various/gallery/various_pose_1.jpg": b"brielle pose",
            "Various/gallery/Mia Base.jpg": b"mia base",
            "Various/gallery/incoming-d167.jpg": b"other picture",
        }
        photos = []
        for relative, payload in files.items():
            path = self.source / pathlib.Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            group = relative.split("/", 1)[0]
            photos.append(SimpleNamespace(path=path, name=path.name, group=group))
        duplicates = {}
        ids = clean_rebase._matching_photo_ids(photos, self.source, likeness, duplicates)
        content = {
            relative: f"photo:pic_{likeness.originals.content_id(self.source / relative)}"
            for relative in files
        }
        brielle = "Prospects/Brielle Carter/gallery/brielle_carter_pose_1.jpg"
        self.assertEqual(ids[brielle], content[brielle])
        self.assertIsNone(ids["Various/gallery/various_pose_1.jpg"])
        self.assertEqual(duplicates, {"Various/gallery/various_pose_1.jpg": brielle})
        for relative in ("Various/gallery/Mia Base.jpg", "Various/gallery/incoming-d167.jpg"):
            self.assertEqual(ids[relative], content[relative])

    def test_content_id_never_claims_an_existing_id_for_different_bytes(self):
        first = self.source / "Various" / "gallery" / "odd name.jpg"
        first.parent.mkdir(parents=True, exist_ok=True)
        first.write_bytes(b"first")
        key = likeness.originals.content_id(first)
        second = first.with_name(f"various_pic_{key}.jpg")
        second.write_bytes(b"second")
        photos = [
            SimpleNamespace(path=path, name=path.name, group="Various")
            for path in (first, second)
        ]
        duplicates = {}
        with self.assertRaisesRegex(ValueError, "content-derived photo ID collision"):
            clean_rebase._matching_photo_ids(photos, self.source, likeness, duplicates)
        self.assertEqual(duplicates, {})

    def test_inferred_id_normalizes_only_prepared_destination(self):
        selected = self.run / "selected.png"
        selected.write_bytes(b"selected pixels")
        source = "Various/gallery/.facebook_123_222222.jpg"
        row = {
            "source": source, "destination": "Prospects/New Person/gallery/.facebook_123_222222.jpg",
            "photoId": "photo:image_222222", "sha256": self.digest,
        }
        with mock.patch.object(clean_rebase.clean_preparation, "selected_path", return_value=selected):
            clean_rebase._bind_preparation(
                [row], {source: {"outcome": "compared", "source": source}}, self.run, likeness,
            )
        self.assertEqual(row["source"], source)
        self.assertEqual(
            row["destination"], "Prospects/New Person/gallery/new_person_image_222222.png",
        )
        self.assertEqual(row["preparedSHA256"], metadata.content_sha256(selected))

    def test_content_id_uses_manifest_digests_without_rehashing_other_photos(self):
        unknown = self.source / "Various" / "gallery" / "download.jpg"
        unknown.parent.mkdir(parents=True, exist_ok=True)
        unknown.write_bytes(b"download")
        existing = unknown.with_name("various_image_123456.jpg")
        existing.write_bytes(b"different")
        photos = [
            SimpleNamespace(path=path, name=path.name, group="Various")
            for path in (unknown, existing)
        ]
        digests = {
            path.relative_to(self.source).as_posix(): metadata.content_sha256(path)
            for path in (unknown, existing)
        }
        with mock.patch.object(metadata, "content_sha256", side_effect=AssertionError("rehash")):
            ids = clean_rebase._matching_photo_ids(photos, self.source, likeness, {}, digests)
        self.assertEqual(
            ids["Various/gallery/download.jpg"],
            f"photo:pic_{likeness.originals.content_id(unknown)}",
        )

    def test_creation_core_seed_policy_routes_released_cast_images_as_candidates(self):
        cast_folder = self.source / "Angels" / "Angelica"
        cast_names = [
            "angelica_image_111111.jpg", "angelica_image_222222.jpg",
            "angelica_image_333333.jpg", "angelica_image_444444.jpg",
            "angelica_image_555555.jpg", "angelica_image_666666.jpg",
        ]
        cast_digests = {}
        for index, name in enumerate(cast_names):
            path = cast_folder / "gallery" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            data = f"cast image {index}".encode()
            path.write_bytes(data)
            cast_digests[name] = hashlib.sha256(data).hexdigest()
            relative = path.relative_to(self.source).as_posix()
            self.layout["manifest_files"][relative] = (len(data), cast_digests[name])

        anchor_id = metadata.photo_id_from_name(cast_names[0])
        protected_id = metadata.photo_id_from_name(cast_names[4])
        person_id = "person_" + "a" * 32
        catalog_path = self.working / ".likeness-library.json"
        metadata.save_catalog({
            "schemaVersion": 1,
            "people": {
                person_id: {
                    "id": person_id, "folder": "Angels/Angelica",
                    "displayName": "Angelica", "folderHistory": [],
                    "identityAnchors": [anchor_id], "protected": False,
                },
            },
            "photos": {
                anchor_id: {
                    "contentSha256": cast_digests[cast_names[0]], "protected": False,
                },
                protected_id: {
                    "contentSha256": cast_digests[cast_names[4]], "protected": True,
                },
            },
            "actions": [],
        }, catalog_path)
        api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: {},
                photo_folders=lambda cfg, root: [
                    ("Potentials", "Fia", self.source_photo.parent.parent),
                    ("Angels", "Angelica", cast_folder),
                ],
                photo_key=likeness.cw.photo_key,
            ),
            settings=likeness.settings, originals=likeness.originals,
            nz=likeness.nz,
            junk_reason=lambda photo, _settings: (
                "synthetic unusable face" if photo.name == cast_names[3] else None
            ),
            chosen_keys=lambda cfg: {likeness.cw.photo_key(cast_names[5])},
            invent_name=lambda seed, taken: f"New Name-{seed[-6:]}",
        )

        def fake_cores(_space, _catalog, **_kwargs):
            ids = [metadata.photo_id_from_name(name) for name in cast_names]
            return {
                "Angels/Angelica": {
                    "vector": np.array([1., 0.]), "side": "Prospects",
                    "category": "Angels", "personIds": [person_id],
                    "identityProtected": False, "mode": "trusted",
                    "corePhotoIds": [ids[0], ids[1], ids[2], ids[4]],
                    "photoScores": {
                        name: (.1 if name == cast_names[3] else .8)
                        for name in cast_names
                    },
                },
            }, set(), []

        def fake_plan(candidates, cores, **_kwargs):
            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0]["photoId"], metadata.photo_id_from_name("fia_image_123456.jpg"))
            self.assertEqual(set(cores), {"Angels/Angelica"})
            return {
                "assignments": [], "clusters": [],
                "held": [{
                    "photoId": candidate["photoId"],
                    "reason": "review candidate",
                } for candidate in candidates],
            }

        with mock.patch.object(clean_rebase.metadata, "path_for_root", return_value=catalog_path), \
                mock.patch.object(clean_rebase, "frozen_identity_cores", side_effect=fake_cores), \
                mock.patch.object(clean_rebase, "plan_reconciliation", side_effect=fake_plan):
            result = clean_rebase.create_plan(
                self.layout, self.run, load_policy(), api,
                embedder=lambda _path: {
                    "v": [1., 0.], "faces": 1, "s": .95, "px": 100,
                },
                cast_seeds="core",
            )

        by_id = {row["photoId"]: row for row in result["photos"]}
        self.assertEqual(result["castSeedPolicy"], "core")
        self.assertTrue(by_id[anchor_id]["retainedCast"])
        self.assertTrue(by_id[protected_id]["retainedCast"])
        self.assertTrue(by_id[metadata.photo_id_from_name(cast_names[5])]["retainedCast"])
        released_id = metadata.photo_id_from_name(cast_names[3])
        self.assertTrue(by_id[released_id]["releasedCast"])
        self.assertFalse(by_id[released_id]["retainedCast"])
        self.assertIsNone(by_id[released_id]["castSeedScore"])
        self.assertEqual(by_id[released_id]["destination"].split("/")[0], "Various")
        self.assertEqual(by_id[released_id]["castSeedQualityReason"], "synthetic unusable face")
        self.assertIn("quality hold", by_id[released_id]["reason"])

    def test_unmatched_photos_do_not_recreate_their_old_shared_membership(self):
        other = self.source_photo.with_name("fia_image_987654.jpg")
        other.write_bytes(b"other photo")
        self.layout["manifest_files"][other.relative_to(self.source).as_posix()] = (
            len(b"other photo"), hashlib.sha256(b"other photo").hexdigest(),
        )
        api = SimpleNamespace(
            cw=SimpleNamespace(
                load_cfg=lambda: {},
                photo_folders=lambda cfg, root: [
                    ("Potentials", "Fia", self.source_photo.parent.parent),
                ],
                photo_key=likeness.cw.photo_key,
            ),
            settings=likeness.settings, originals=likeness.originals,
            nz=likeness.nz, chosen_keys=lambda cfg: set(),
            invent_name=lambda seed, taken: f"New Name-{seed[-6:]}",
        )
        with mock.patch.object(clean_rebase, "frozen_identity_cores", return_value=(
            {"Angels/Angelica": {
                "vector": np.array([0., 1.]), "side": "Prospects",
                "identityProtected": True, "corePhotoIds": [], "photoScores": {},
            }},
            set(), [],
        )):
            result = clean_rebase.create_plan(
                self.layout, self.run, load_policy(), api,
                embedder=lambda path: {
                    "v": [1., 0.] if path == self.source_photo else [-1., 0.],
                    "faces": 1, "s": .95, "px": 100,
                },
            )
        folders = {"/".join(row["destination"].split("/")[:2]) for row in result["photos"]}
        self.assertEqual(len(folders), 2)

    def test_heap_clustering_matches_brute_force_average_linkage(self):
        rng = np.random.default_rng(41)
        vectors = rng.normal(size=(30, 8))
        vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
        rows = [{"photoId": f"{i:03}", "vector": vector} for i, vector in enumerate(vectors)]
        scores = vectors @ vectors.T
        groups = [[i] for i in range(len(rows))]
        while len(groups) > 1:
            best = None
            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):
                    score = float(np.mean(scores[np.ix_(groups[i], groups[j])]))
                    if best is None or score > best[0]:
                        best = (score, i, j)
            score, i, j = best
            if score < .25:
                break
            groups[i] = sorted(groups[i] + groups.pop(j))
        expected = [[rows[i]["photoId"] for i in group] for group in groups]
        actual = [[row["photoId"] for row in group] for group in _average_linkage(rows, .25)]
        self.assertEqual(actual, expected)
