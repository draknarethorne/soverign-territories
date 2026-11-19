import copy
import gzip
import json
import pathlib
import tempfile
import unittest
from collections import defaultdict
from unittest import mock

import numpy as np

from tools.art import likeness_entrance_trial as cli
from tools.art.likeness_library import directed_reformation as directed
from tools.art.likeness_library import metadata, shadow


class FakeCache:
    def __init__(self, photo_ids, pair_scores, duplicates):
        self.indices = {pid: index for index, pid in enumerate(sorted(photo_ids))}
        self.pair_scores = pair_scores
        self.duplicates = duplicates

    def get(self, a, b):
        if a == b:
            return 1.0
        return self.pair_scores.get(tuple(sorted((a, b))), .1)


class MatrixCache:
    def __init__(self, vectors):
        self.ids = tuple(sorted(vectors))
        self.indices = {pid: index for index, pid in enumerate(self.ids)}
        matrix = np.asarray([vectors[pid] for pid in self.ids])
        self.values = matrix @ matrix.T

    def get(self, a, b):
        return self.values[self.indices[a], self.indices[b]]


class MatrixEvidence:
    def __init__(self, vectors):
        self.vectors = vectors
        self.hashes = {pid: "hash-" + pid for pid in vectors}
        self.cache = MatrixCache(vectors)
        self.settings = {"identityActions": {"independentEvidenceMaximumSimilarity": .95}}
        self.negatives = defaultdict(set)
        self.independence = {}
        self.globally_independent = all(
            self.hashes[left] != self.hashes[right]
            and float(self.vectors[left] @ self.vectors[right]) <= .95
            for index, left in enumerate(self.cache.ids)
            for right in self.cache.ids[index + 1:]
        )

    def independent(self, ids):
        key = tuple(sorted(set(ids)))
        if self.globally_independent:
            return list(key)
        if key not in self.independence:
            chosen, hashes = [], set()
            for pid in key:
                if self.hashes[pid] in hashes:
                    continue
                if all(float(self.vectors[pid] @ self.vectors[other]) <= .95 for other in chosen):
                    chosen.append(pid)
                    hashes.add(self.hashes[pid])
            self.independence[key] = chosen
        return list(self.independence[key])

    def others(self, pid, refs):
        return [other for other in refs if pid != other and self.hashes[pid] != self.hashes[other]
                and self.cache.get(pid, other) <= .95]

    def support(self, pid, refs, floor):
        return self.independent([
            other for other in self.others(pid, refs) if self.cache.get(pid, other) >= floor
        ])

    def measure(self, pid, refs):
        refs = self.independent(self.others(pid, refs))
        if not refs:
            return None
        total = np.sum([self.vectors[other] for other in refs], axis=0)
        norm = np.linalg.norm(total)
        return float(self.vectors[pid] @ total / norm) if norm else None

    def qualify(self, view_row, refs, recipe):
        if view_row.get("explicitIntent"):
            return sorted(refs), True
        refs = sorted(set(refs))
        floor = recipe["core"][view_row["category"]]
        for _ in range(directed.entrance_trial.MAX_BOUNDARIES):
            kept = [
                pid for pid in refs if not self.negatives[pid].intersection(refs)
                and len(self.support(pid, refs, floor)) >= recipe["coreSupport"]
                and (self.measure(pid, refs) or -1) >= floor
            ]
            if kept == refs:
                return kept, True
            refs = kept
        return refs, False


class FakeEvidence:
    def __init__(self, *, identities, views, scores, supports, own_scores, labels=(),
                 stage_scores=None, duplicates=(), pair_scores=None):
        self.source = {}
        self.photos = {}
        self.views = copy.deepcopy(views)
        self.scores_map = scores
        self.supports = supports
        self.own_scores = own_scores
        self.stage_scores = stage_scores or {}
        self.duplicates = {tuple(sorted(pair)) for pair in duplicates}
        self.pair_scores = {
            tuple(sorted(pair)): score for pair, score in (pair_scores or {}).items()
        }
        self.labels = list(labels)
        self.negatives = defaultdict(set)
        for pair in self.labels:
            a, b = pair["photoIds"]
            if pair["label"] != "same":
                self.negatives[a].add(b)
                self.negatives[b].add(a)
        all_ids = set()
        for view in self.views:
            view.setdefault("frozenReferencePhotoIds", list(view["original"]))
            view.setdefault("referenceStable", True)
            all_ids.update(view["original"])
        for pid, row in identities.items():
            refs = list(row.get("refs", []))
            own = {
                "appearanceId": row.get("ownView"),
                "frozenReferencePhotoIds": refs,
                "frozenScore": own_scores.get(pid),
            }
            self.source[pid] = {
                "photoId": pid, "oldFolder": row["folder"], "oldPersonId": row["personId"],
                "membershipAssessment": {"own": own}, "placementBlocks": row.get("blocks", []),
                "explicitIntentFolder": row.get("intent"),
            }
            self.photos[pid] = {
                "photoId": pid, "destination": row["folder"] + "/gallery/" + pid + ".jpg",
                "preparedSHA256": "hash-" + pid, "castSeedCore": row.get("core", False),
                "castSeedScore": row.get("castScore"),
            }
            all_ids.add(pid)
        self.hashes = {pid: "hash-" + pid for pid in all_ids}
        self.vectors = {pid: np.asarray([1.0, float(index + 1)]) for index, pid in enumerate(sorted(all_ids))}
        self.cache = FakeCache(all_ids, self.pair_scores, self.duplicates)
        self.eligible = set(self.source)

    def others(self, pid, refs):
        return [ref for ref in refs if ref != pid and self.hashes[ref] != self.hashes[pid]]

    def independent(self, ids):
        result = []
        for pid in sorted(set(ids)):
            if all(tuple(sorted((pid, other))) not in self.duplicates for other in result):
                result.append(pid)
        return result

    def support(self, pid, refs, floor):
        trigger = self.stage_scores.get(pid, {}).get("__trigger__")
        if trigger and trigger in refs:
            scores = {**self.supports.get(pid, {}), **self.stage_scores.get(pid, {})}
        else:
            scores = self.supports.get(pid, {})
        found = [ref for ref in self.others(pid, refs) if scores.get(ref, 0) >= floor]
        return self.independent(found)

    def measure(self, pid, refs):
        return self.own_scores.get(pid)

    def qualify(self, view, refs, recipe):
        if view.get("explicitIntent"):
            return sorted(refs), True
        for _ in range(4):
            kept = [pid for pid in refs if not self.negatives[pid].intersection(refs)
                    and len(self.support(pid, refs, recipe["core"][view["category"]])) >= recipe["coreSupport"]
                    and (self.measure(pid, refs) or -1) >= recipe["core"][view["category"]]]
            if kept == refs:
                return kept, True
            refs = kept
        return refs, False

    def scores(self, inventory):
        ids = sorted(self.cache.indices, key=self.cache.indices.get)
        matrix = np.full((len(ids), len(self.views)), np.nan, dtype=float)
        for i, pid in enumerate(ids):
            for j, view in enumerate(self.views):
                refs = inventory[view["appearanceId"]]
                if not refs:
                    continue
                score = self.scores_map.get((pid, view["appearanceId"]))
                if refs != view["original"]:
                    score = self.stage_scores.get(pid, {}).get("__score__", score)
                if score is not None:
                    matrix[i, j] = score
        return matrix


def view(folder, category, person_id, appearance_id, refs):
    return {
        "folder": folder, "category": category, "personId": person_id,
        "appearanceId": appearance_id, "original": list(refs),
        "frozenReferencePhotoIds": list(refs), "referenceStable": True,
    }


class DirectedReformationTests(unittest.TestCase):
    def test_population_boundary_receipt_saves_actual_manifest_deficit_without_losing_stage_changes(self):
        lifecycle = {"stages": []}
        for boundary in range(10):
            rows = []
            for photo in range(3290):
                source = f"Potentials/Existing Person {photo % 194:03d}/gallery/original_long_source_image_{photo:08d}.jpg"
                destination = source if boundary < 5 else source.replace("Potentials", "Prospects")
                refs = [
                    f"photo:image_{(photo // 6 * 6 + offset):08d}"
                    for offset in range(32)
                ]
                rows.append({
                    "photoId": f"photo:image_{photo:08d}", "source": source, "sourceDestination": source,
                    "destination": destination, "proposedDestination": destination,
                    "personId": f"person_{photo % 194:032x}", "groupId": f"group_{photo % 776:032x}",
                    "status": "supported" if photo % 3 else "tentative", "coreUse": photo % 4 == 0,
                    "score": ((photo + boundary) % 1000) / 1000,
                    "rivalScore": (photo % 300) / 1000, "margin": (photo % 50) / 1000,
                    "qualifiedOwnReferenceViewIds": [f"view-{photo % 219:04d}"],
                    "independentSupportPhotoIds": [f"photo:image_{(photo // 6 * 6 + n):08d}" for n in range(4)],
                    "admissionBlockers": [] if photo % 3 else ["insufficient-independent-member-support"],
                    "reason": "actual frozen computational boundary; source routes unchanged until a qualified proposal is recorded",
                    "contentHash": f"{photo:064x}",
                    "sourceReferenceEvidence": {
                        "candidateReferencePhotoIds": refs,
                        "qualifiedReferencePhotoIds": refs,
                        "scoreBasis": "frozen independent-reference centroid",
                    },
                })
            lifecycle["stages"].append({
                "id": f"boundary-{boundary}", "title": f"Actual boundary {boundary}",
                "evidenceKind": "computational-boundary-snapshot", "rows": rows,
                "referenceInventory": {f"view-{v:04d}": [f"photo:image_{v * 6 + n:08d}" for n in range(6)]
                                       for v in range(219)},
                "witnessPolicy": {"boundary": boundary, "independentSupport": 4},
            })
        expected = copy.deepcopy(lifecycle)
        old_bytes = len(json.dumps(lifecycle["stages"], sort_keys=True, separators=(",", ":")).encode())
        self.assertGreater(old_bytes, 64 * 1024 * 1024)
        lifecycle["stages"] = [
            directed.pack_boundary_snapshot(stage) for stage in lifecycle["stages"]
        ]
        packed_bytes = sum(
            stage["boundaryEvidence"]["uncompressedBytes"] for stage in lifecycle["stages"]
        )
        expanded_bytes = sum(
            stage["boundaryEvidence"]["expandedBytes"] for stage in lifecycle["stages"]
        )
        self.assertGreater(expanded_bytes, 64 * 1024 * 1024)
        self.assertLess(packed_bytes, 64 * 1024 * 1024)
        self.assertEqual(
            [directed.unpack_boundary_snapshot(stage) for stage in lifecycle["stages"]],
            expected["stages"],
        )
        directed.pack_lifecycle_stages(lifecycle)
        new_bytes = len(json.dumps(lifecycle["stages"], sort_keys=True, separators=(",", ":")).encode())
        self.assertGreater(old_bytes - new_bytes, 79_192_840 - 64 * 1024 * 1024)
        self.assertLess(79_192_840 - 32_521_788 + new_bytes, 64 * 1024 * 1024)
        self.assertEqual([directed.lifecycle_stage(stage) for stage in lifecycle["stages"]],
                         expected["stages"])
        self.assertNotEqual(directed.lifecycle_stage(lifecycle["stages"][0])["rows"][0]["destination"],
                            directed.lifecycle_stage(lifecycle["stages"][9])["rows"][0]["destination"])
        lifecycle["stages"][0]["rows"][0]["coreUse"] = False
        with self.assertRaisesRegex(ValueError, "readable row index"):
            directed.lifecycle_stage(lifecycle["stages"][0])

    def test_packed_boundary_snapshot_roundtrip_rejects_bad_binding_index_and_size(self):
        snapshot = {
            "id": "references", "evidenceKind": "computational-boundary-snapshot",
            "rows": [{"photoId": "photo:one", "status": "supported", "coreUse": True}],
            "referenceInventory": {"view:one": ["photo:one", "photo:two"]},
            "witnessPolicy": {"configuredDistinctPersonPairs": [["person:a", "person:b"]]},
        }
        packed = directed.pack_boundary_snapshot(snapshot)
        self.assertEqual(directed.unpack_boundary_snapshot(packed), snapshot)
        lifecycle = {**packed, "title": "Validated references", "scope": "all inputs"}
        self.assertEqual(
            directed.lifecycle_stage(lifecycle)["title"], "Validated references",
        )
        self.assertEqual(directed.lifecycle_stage(lifecycle)["scope"], "all inputs")

        bad_binding = copy.deepcopy(packed)
        bad_binding["boundaryEvidence"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "content binding"):
            directed.unpack_boundary_snapshot(bad_binding)

        bad_index = copy.deepcopy(packed)
        bad_index["rows"][0]["coreUse"] = False
        with self.assertRaisesRegex(ValueError, "readable row index"):
            directed.unpack_boundary_snapshot(bad_index)

        oversized = copy.deepcopy(packed)
        oversized["boundaryEvidence"]["uncompressedBytes"] = directed.MAX_PACKED_EVIDENCE_BYTES + 1
        with self.assertRaisesRegex(ValueError, "invalid directed evidence size"):
            directed.unpack_boundary_snapshot(oversized)

        bad_version = copy.deepcopy(packed)
        bad_version["boundaryEvidenceVersion"] = 2
        with self.assertRaisesRegex(ValueError, "unsupported directed boundary evidence version"):
            directed.unpack_boundary_snapshot(bad_version)

        bounded_first = copy.deepcopy(packed)
        bounded_second = copy.deepcopy(packed)
        bounded_first["boundaryEvidence"]["uncompressedBytes"] = directed.MAX_PACKED_EVIDENCE_BYTES
        bounded_second["boundaryEvidence"]["uncompressedBytes"] = directed.MAX_PACKED_EVIDENCE_BYTES
        with self.assertRaisesRegex(ValueError, "exceeds 64 MiB after lifecycle repack"):
            directed.pack_lifecycle_stages({"stages": [bounded_first, bounded_second]})

    def test_legacy_receipt_and_interned_size_binding_remain_verified(self):
        import base64
        import hashlib
        expected = {"photo:one": {"rivals": [{"referencePhotoIds": ["one", "two"]}]}}
        payload = json.dumps(expected, separators=(",", ":"), sort_keys=True).encode()
        legacy = {
            "encoding": "gzip-base64-json", "uncompressedBytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "data": base64.b64encode(gzip.compress(payload, mtime=0)).decode(),
        }
        self.assertEqual(directed.unpack_runtime_decisions(legacy), expected)
        old_expected = {"photo:one": {"value": "unchanged"}}
        old_payload = json.dumps({
            "nodes": [["dict", [["value", "unchanged"]]],
                      ["dict", [["photo:one", {"$": 0}]]]],
            "root": {"$": 1},
        }, separators=(",", ":"), sort_keys=True).encode()
        old = {
            "encoding": "gzip-base64-interned-json-v1", "uncompressedBytes": len(old_payload),
            "expandedBytes": len(json.dumps(old_expected, separators=(",", ":"), sort_keys=True)),
            "sha256": hashlib.sha256(old_payload).hexdigest(),
            "data": base64.b64encode(gzip.compress(old_payload, mtime=0)).decode(),
        }
        self.assertEqual(directed.unpack_runtime_decisions(old), old_expected)
        packed = directed.pack_runtime_decisions([
            {"photoId": key, "directedReformation": value} for key, value in expected.items()
        ])
        packed["expandedBytes"] += 1
        with self.assertRaisesRegex(ValueError, "expanded byte count"):
            directed.unpack_runtime_decisions(packed)

    def test_v2_shared_table_corruption_is_rejected_after_valid_content_binding(self):
        import base64
        import hashlib
        packed = directed.pack_runtime_decisions([
            {"photoId": "photo:one", "directedReformation": {"reason": "independent witness"}},
        ])
        decoded = json.loads(gzip.decompress(base64.b64decode(packed["data"])))
        for field in ("schemas", "nodes"):
            broken = copy.deepcopy(decoded)
            if field == "schemas":
                broken[field][0] = [len(broken["strings"])]
            else:
                record = next(node for node in broken[field] if node[0] == "record")
                record[1][1][0] = {"s": len(broken["strings"])}
            payload = json.dumps(broken, separators=(",", ":"), sort_keys=True).encode()
            receipt = {
                **packed, "uncompressedBytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "data": base64.b64encode(gzip.compress(payload, mtime=0)).decode(),
            }
            with self.assertRaisesRegex(ValueError, "invalid interned evidence"):
                directed.unpack_runtime_decisions(receipt)

    def test_packed_runtime_evidence_is_lossless_bounded_and_content_bound(self):
        details = {"shadowAction": "retain-in-place", "rivals": [
            {"referencePhotoIds": [f"photo:{i}" for i in range(1000)]}
        ]}
        rows = [{"photoId": f"photo:{i}", "directedReformation": copy.deepcopy(details)}
                for i in range(40)]
        expected = {row["photoId"]: copy.deepcopy(row["directedReformation"]) for row in rows}
        packed = directed.pack_runtime_decisions(rows)
        self.assertEqual(directed.unpack_runtime_decisions(packed), expected)
        self.assertLess(len(json.dumps(packed)), packed["expandedBytes"] // 5)
        packed["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "content binding"):
            directed.unpack_runtime_decisions(packed)

    def fixture(self):
        from tools.art.likeness_library.engine import Photo
        rows, measured = [], {}
        cohorts = {}

        def add(folder, axis, count=6, pair=.64, *, quality=False):
            ids = []
            for _ in range(count):
                number = 800000 + len(rows)
                pid = f"photo:image_{number}"
                relative = f"{folder}/gallery/source_image_{number}.jpg"
                vector = np.zeros(192)
                vector[axis] = np.sqrt(pair)
                vector[32 + len(rows)] = np.sqrt(1 - pair)
                photo = Photo(pathlib.Path(relative), folder.split("/")[0], folder.split("/")[-1],
                              f"{number:064x}", {"faces": 1, "px": 150, "v": vector.tolist()})
                photo.vec = vector
                measured[relative] = photo
                rows.append({"photoId": pid, "source": relative, "destination": relative,
                             "oldFolder": folder, "sha256": f"{number:064x}", "reason": "source lineage",
                             **({"qualityHold": True} if quality else {})})
                ids.append(pid)
            cohorts.setdefault(folder, []).extend(ids)
            return ids

        add("Sisters/Sister Source", 0, pair=.75)
        add("Angels/Angel Source", 1)
        add("Models/Model Source", 2)
        add("Prospects/Prospect Source", 3)
        add("Potentials/Potential Source", 4)
        add("Various", 5)
        add("Various", 6, count=1)
        add("Various", 7, count=1, quality=True)
        return rows, measured, {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}, cohorts, add

    def test_population_sized_receipt_interns_repeated_views_losslessly_under_unchanged_cap(self):
        refs = [f"photo:reference_{i:06d}" for i in range(1000)]
        rows = [{
            "photoId": f"photo:image_{i:06d}",
            "directedReformation": {
                "sourcePersonId": f"person_{i % 21}",
                "rivals": [{
                    "appearanceId": f"view-{j}", "personId": f"person-{j}",
                    "score": (i % 100) / 100, "referencePhotoIds": refs,
                    "independentSupportPhotoIds": refs[:10],
                    "sharedOriginalReferencePhotoIds": refs,
                    "blockers": ["below-admission-floor"] if i % 2 else [],
                } for j in range(2)],
            },
        } for i in range(3290)]
        expected = copy.deepcopy({row["photoId"]: row["directedReformation"] for row in rows})
        packed = directed.pack_runtime_decisions(rows)
        self.assertGreater(packed["expandedBytes"], 64 * 1024 * 1024)
        self.assertLess(packed["uncompressedBytes"], 64 * 1024 * 1024)
        self.assertGreater(packed["expandedSectionBytes"]["rivals"], 64 * 1024 * 1024)
        decoded = directed.unpack_runtime_decisions(json.loads(json.dumps(packed)))
        self.assertEqual(decoded, expected)
        decoded["photo:image_000000"]["rivals"][0]["referencePhotoIds"].clear()
        self.assertEqual(len(decoded["photo:image_000001"]["rivals"][0]["referencePhotoIds"]), 1000)

    def test_population_varying_overlap_inventories_share_strings_and_record_schemas_losslessly(self):
        population = [f"photo:image_{i:019d}" for i in range(3290)]
        rows = []
        for i, pid in enumerate(population):
            rivals = []
            for view in range(18):
                refs = [population[(i * 17 + view * 31 + j * (7 + view * 2)) % 3290]
                        for j in range(45)]
                rivals.append({
                    "appearanceId": f"qualified-view:{view:032d}", "personId": f"person_{view % 7:032d}",
                    "folder": f"Prospects/Independent Owner {view % 7}", "category": "Prospects",
                    "score": (i + view) % 1000 / 1000, "sameIdentity": False,
                    "referencePhotoIds": refs, "sharedOriginalReferencePhotoIds": refs[:-1],
                    "independentSupportPhotoIds": refs[1:],
                    "blockers": ["insufficient-independent-member-support"] if i % 2 else [],
                })
            rows.append({"photoId": pid, "directedReformation": {"rivals": rivals}})
        expected = {row["photoId"]: row["directedReformation"] for row in rows}
        unique_inventories = {
            tuple(option[field])
            for decision in expected.values() for option in decision["rivals"]
            for field in ("referencePhotoIds", "sharedOriginalReferencePhotoIds",
                          "independentSupportPhotoIds")
        }
        v1_inventory_bytes = sum(len(json.dumps(list(refs), separators=(",", ":")))
                                 for refs in unique_inventories)
        self.assertGreater(v1_inventory_bytes, 64 * 1024 * 1024)
        del unique_inventories
        packed = directed.pack_runtime_decisions(rows)
        self.assertGreater(packed["expandedBytes"], 200_000_000)
        self.assertLess(packed["uncompressedBytes"], 64 * 1024 * 1024)
        self.assertEqual(packed["encoding"], "gzip-base64-interned-json-v2")
        self.assertGreater(packed["sharedStringCount"], 3290)
        self.assertLess(packed["sharedRecordSchemaCount"], 10)
        self.assertIn("strings", packed["storedSectionBytes"])
        decoded = directed.unpack_runtime_decisions(json.loads(json.dumps(packed)))
        self.assertEqual(decoded, expected)
        decoded[population[0]]["rivals"][0]["referencePhotoIds"].clear()
        self.assertEqual(len(decoded[population[1]]["rivals"][0]["referencePhotoIds"]), 45)

    def run_fixture(self, fixture, **kwargs):
        from tools.art.likeness_library import group_lifecycle
        from tools.art.likeness_library.policy import load_policy
        rows, measured, catalog = fixture[:3]
        directed_recipe = kwargs.pop("directed_recipe", "directed-core-continuity")
        name_factory = kwargs.pop(
            "name_factory", lambda seed, taken: "Nova " + seed,
        )
        return group_lifecycle.regroup(
            rows, measured, catalog, kwargs.pop("policy", load_policy()), set(), "repair",
            at="2026-11-13T10:28:00+00:00", directed_recipe=directed_recipe,
            name_factory=name_factory, **kwargs,
        )

    def assert_reference_exports(self, output, report, catalog):
        qualified = defaultdict(set)
        for view in report["qualifiedReferences"]:
            qualified[view["personId"]].update(view["qualifiedReferencePhotoIds"])
        for row in output:
            membership = row["membership"]
            if membership["coreUse"]:
                self.assertEqual(membership["status"], "supported")
                self.assertIn(row["photoId"], qualified[membership["personId"]])
            self.assertEqual(membership["coreUse"], row["directedReformation"]["referenceUseEligible"])
        withdrawn = {pid for item in report["initialReferenceValidation"] for pid in item["withdrawnPhotoIds"]}
        self.assertFalse(withdrawn & {row["photoId"] for row in output if row["membership"]["coreUse"]})
        for group in catalog["photoGroups"].values():
            for pid in group["referencePhotoIds"]:
                self.assertTrue(catalog["photos"][pid]["membership"]["coreUse"])
                self.assertIn(pid, qualified[group["personId"]])
        self.assertEqual(report["evaluation"]["referenceUseEligible"],
                         sum(row["membership"]["coreUse"] for row in output))
        restored = json.loads(json.dumps(catalog))
        metadata.validate_catalog(restored)
        decisions = directed.unpack_runtime_decisions(json.loads(json.dumps(report["decisionEvidence"])))
        self.assertEqual({row["photoId"]: row["membership"]["coreUse"] for row in output},
                         {pid: row["referenceUseEligible"] for pid, row in decisions.items()})

    def test_fresh_catalogue_reforms_all_source_categories_new_people_groups_and_holds(self):
        fixture = self.fixture()
        output, report = self.run_fixture(fixture)
        catalog, cohorts = fixture[2:4]
        existing_folders = set(cohorts) - {"Various"}
        self.assertTrue(existing_folders <= {p["folder"] for p in catalog["people"].values()})
        self.assertEqual(len(catalog["people"]), 7)
        self.assertEqual(report["evaluation"]["independentResidualCandidates"], 1)
        by_id = {row["photoId"]: row for row in output}
        for folder in existing_folders:
            for pid in cohorts[folder]:
                row = by_id[pid]
                self.assertIsNotNone(row["directedReformation"]["sourcePersonId"])
                self.assertEqual(row["membership"]["status"], "supported")
                self.assertTrue(row["membership"]["coreUse"])
                self.assertEqual(row["source"], row["destination"])
                self.assertIsNotNone(row["membership"]["groupId"])
        created = report["independentIdentities"][0]
        self.assertTrue(created["folder"].startswith("Prospects/Nova "))
        for pid in cohorts["Various"][:6]:
            self.assertEqual(by_id[pid]["membership"]["personId"], created["personId"])
            self.assertTrue(by_id[pid]["destination"].startswith(created["folder"] + "/gallery/"))
            self.assertTrue(by_id[pid]["membership"]["coreUse"])
        singleton, quality = (by_id[pid] for pid in cohorts["Various"][-2:])
        self.assertEqual(singleton["membership"]["status"], "tentative")
        self.assertEqual(singleton["membership"]["assignmentDisposition"], "provisional")
        self.assertTrue(singleton["destination"].startswith("Potentials/"))
        self.assertEqual(quality["membership"]["status"], "quality-hold")
        for row in (quality,):
            self.assertEqual(row["source"], row["destination"])
            self.assertFalse(row["membership"]["coreUse"])
        self.assertEqual(report["assignmentSummary"]["activeVarious"], 1)
        self.assertEqual(len(report["assignmentSummary"]["exceptions"]), 1)
        self.assertEqual(report["evaluation"]["verifiedStrongBaselineCount"], 6)
        self.assert_reference_exports(output, report, catalog)
        replay = self.fixture()
        replay[0].reverse()
        reversed_output, reversed_report = self.run_fixture(replay)
        self.assertEqual({row["photoId"]: row for row in output},
                         {row["photoId"]: row for row in reversed_output})
        self.assertEqual(report, reversed_report)
        stages = {stage["id"]: stage for stage in report["stages"]}
        self.assertEqual(stages["input"]["evidenceKind"], "source-snapshot")
        self.assertEqual(stages["references"]["evidenceKind"], "computational-boundary-snapshot")
        self.assertEqual(stages["references"]["rows"][0]["status"], "membership-not-yet-assessed")
        self.assertFalse(any(row["coreUse"] for row in stages["references"]["rows"]))
        self.assertTrue(any(row["coreUse"] for row in stages["publication"]["rows"]))

    def test_source_incompatible_cohort_gets_provisional_noncore_owner_without_weak_score_eviction(self):
        fixture = self.fixture()
        rows, measured, _catalog, cohorts, add = fixture
        weak = add("Sisters/Sister Source", 8, count=2, pair=.75)
        for index, photo_id in enumerate(weak):
            source = next(row["source"] for row in rows if row["photoId"] == photo_id)
            vector = np.zeros(192)
            vector[8] = np.sqrt(.75)
            vector[32 + index] = np.sqrt(.25)
            measured[source].vec = vector
        output, report = self.run_fixture(
            fixture, directed_recipe="directed-corrective-starting-050",
        )
        by_id = {row["photoId"]: row for row in output}
        weak_rows = [by_id[photo_id] for photo_id in weak]
        self.assertTrue(all(row["destination"].startswith("Potentials/Nova ") for row in weak_rows))
        self.assertTrue(all(row["destination"].endswith("/gallery/" + pathlib.PurePosixPath(row["source"]).name)
                            for row in weak_rows))
        self.assertTrue(all(row["membership"]["assignmentDisposition"] == "provisional"
                            and not row["membership"]["coreUse"]
                            for row in weak_rows))
        self.assertEqual(len({row["membership"]["personId"] for row in weak_rows}), 1)
        owner = next(person for person in fixture[2]["people"].values()
                     if person["id"] == weak_rows[0]["membership"]["personId"])
        self.assertEqual(owner["identityStatus"], "provisional")
        provenance = weak_rows[0]["membership"]["assignmentEvidence"]["sourceReferenceEvidence"]
        self.assertIsNotNone(provenance)
        self.assertEqual(provenance["requiredIndependentPairSupport"], 3)
        self.assertGreater(provenance["candidateReferenceCount"], 0)
        from tools.art.likeness_library import group_views, review_gallery
        self.assertIn("Frozen source-reference provenance:", review_gallery.SCRIPT)
        with tempfile.TemporaryDirectory() as temporary:
            pages = group_views.publish(fixture[2], [], pathlib.Path(temporary))
            group_id = weak_rows[0]["membership"]["groupId"]
            group_page = pages[f"photo-groups/{group_id}/index.html"].decode("utf-8")
            self.assertIn("Frozen source-reference provenance", group_page)
        self.assertEqual(report["evaluation"]["sourceIncompatibleProvisionalAssignments"], 2)
        source_candidates = next(item for item in report["residualClassifications"]
                                 if set(item["memberPhotoIds"]) == set(weak))
        self.assertEqual(set(source_candidates["sourceIncompatiblePhotoIds"]), set(weak))
        self.assertEqual(source_candidates["qualifiedReferencePhotoIds"], [])
        self.assertEqual(source_candidates["disposition"], "independent-reference-insufficient")
        self.assertTrue(all(row["source"] != row["destination"] for row in weak_rows))
        decisions = directed.unpack_runtime_decisions(report["decisionEvidence"])
        self.assertTrue(all(decisions[pid]["sourceIncompatibility"]["qualified"] for pid in weak))
        self.assert_reference_exports(output, report, fixture[2])
        locked_fixture = self.fixture()
        locked_rows, locked_measured, locked_catalog, _locked_cohorts, locked_add = locked_fixture
        locked_weak = locked_add("Sisters/Sister Source", 8, count=2, pair=.75)
        for index, photo_id in enumerate(locked_weak):
            source = next(row["source"] for row in locked_rows if row["photoId"] == photo_id)
            vector = np.zeros(192)
            vector[8] = np.sqrt(.75)
            vector[32 + index] = np.sqrt(.25)
            locked_measured[source].vec = vector
        locked_row = next(row for row in locked_rows if row["photoId"] == locked_weak[0])
        locked_catalog["photos"][locked_weak[0]] = {
            "contentSha256": locked_row["sha256"], "protected": True,
        }
        locked_output, _ = self.run_fixture(
            locked_fixture, directed_recipe="directed-corrective-starting-050",
        )
        locked_by_id = {row["photoId"]: row for row in locked_output}
        self.assertTrue(all(locked_by_id[photo_id]["source"] == locked_by_id[photo_id]["destination"]
                            for photo_id in locked_weak))

    def test_verified_point80_baseline_can_be_corrected_after_new_exact_contradiction_unless_locked(self):
        baseline = self.fixture()
        output, _ = self.run_fixture(baseline)
        candidate = baseline[3]["Sisters/Sister Source"][0]
        original = next(row for row in output if row["photoId"] == candidate)
        self.assertTrue(original["directedReformation"]["verifiedStrongBaseline"])
        self.assertGreaterEqual(original["directedReformation"]["currentOwnScore"], .8)
        for locked in (False, True):
            fixture = self.fixture()
            rows, measured, catalog, cohorts, add = fixture
            destination = add("Models/Contradictory Identity", 0, pair=.75)
            # New independent direct evidence contradicts the original source
            # identity, while the independent destination supports the member.
            pair = {"photoIds": [candidate, cohorts["Sisters/Sister Source"][1]], "label": "different"}
            if locked:
                catalog["photos"][candidate] = {
                    "contentSha256": next(row["sha256"] for row in rows if row["photoId"] == candidate),
                    "protected": True,
                }
            repaired, report = self.run_fixture(fixture, pairs=[pair])
            row = next(row for row in repaired if row["photoId"] == candidate)
            details = directed.unpack_runtime_decisions(report["decisionEvidence"])[candidate]
            self.assertTrue(details["sourceIncompatibility"]["qualified"])
            if locked:
                self.assertEqual(row["source"], row["destination"])
                self.assertEqual(details["shadowAction"], "physical-lock-preserved")
            else:
                self.assertEqual(details["shadowAction"], "strong-wrong-identity-correction")
                self.assertTrue(row["destination"].startswith("Models/Contradictory Identity/gallery/"))
                self.assertTrue(set(details["correctionAssociation"]["independentSupportPhotoIds"]) & set(destination))
            self.assert_reference_exports(repaired, report, catalog)

    def test_mixed_cast_inventory_recovers_independent_subviews_without_point80_cutoff(self):
        fixture = self.fixture()
        fixture[-1]("Angels/Angel Source", 8)
        output, report = self.run_fixture(fixture)
        angel = [row for row in output if row["oldFolder"] == "Angels/Angel Source"]
        self.assertEqual(len(angel), 12)
        self.assertTrue(all(row["membership"]["coreUse"] for row in angel))
        self.assertTrue(all(not row["directedReformation"]["verifiedStrongBaseline"] for row in angel))
        rescued = [view for view in report["qualifiedReferences"]
                   if view["folder"] == "Angels/Angel Source" and view.get("reconstructedFrom")]
        self.assertEqual(len(rescued), 2)
        self.assertEqual({len(view["qualifiedReferencePhotoIds"]) for view in rescued}, {6})
        self.assert_reference_exports(output, report, fixture[2])

    def test_corrective_recipe_keeps_historical_default_and_separates_three_cast_selection_candidates(self):
        historical = directed.recipe_named("directed-core-continuity")
        self.assertEqual(historical["core"], {
            "Sisters": .60, "Angels": .60, "Models": .50, "Prospects": .45, "Potentials": .40,
        })
        self.assertEqual(historical["coreSupport"], 4)
        self.assertNotIn("startingCastSelectionMinimum", historical)
        candidates = [
            recipe for recipe in directed.recipes()
            if recipe["name"].startswith("directed-corrective-starting-")
        ]
        self.assertEqual(
            [recipe["startingCastSelectionMinimum"] for recipe in candidates], [.45, .50, .60],
        )
        for recipe in candidates:
            self.assertEqual(recipe["core"], {
                "Sisters": .40, "Angels": .35, "Models": .30, "Prospects": .25, "Potentials": .25,
            })
            self.assertEqual(recipe["coreSupport"], 3)
            self.assertEqual(recipe["tentativeCastSupport"], 2)

    def test_starting_cast_selection_is_frozen_separate_and_reports_sparse_core_loss(self):
        refs = [f"cast-{index}" for index in range(7)]
        scores = dict(zip(refs, (.95, .75, .70, .65, .55, .48, .20)))
        identities = {
            pid: {"folder": "Sisters/Cast", "personId": "cast-owner", "refs": refs,
                  "ownView": "cast-view"}
            for pid in refs
        }
        supports = {
            pid: {other: .9 for other in refs if other != pid}
            for pid in refs
        }
        base = FakeEvidence(
            identities=identities,
            views=[view("Sisters/Cast", "Sisters", "cast-owner", "cast-view", refs)],
            scores={}, supports=supports, own_scores=scores,
        )
        base.configured_identity_negatives = set()
        original_population = set(base.source)
        results = {}
        for floor in (.45, .50, .60):
            recipe = copy.deepcopy(directed.recipe_named(
                f"directed-corrective-starting-{int(floor * 100):03d}",
            ))
            prepared, _withdrawals = directed.prepare_reference_views(copy.deepcopy(base), recipe)
            source_view = next(item for item in prepared.views if item["appearanceId"] == "cast-view")
            selection = source_view["startingCastSelection"]
            results[floor] = (set(selection["selectedPhotoIds"]), set(source_view["original"]))
            self.assertEqual(set(selection["candidatePhotoIds"]), set(refs))
            self.assertEqual(selection["minimumOwnScore"], floor)
            self.assertEqual(selection["scoreBasis"],
                             "content-bound independent own-core score against the complete original candidate inventory")
        observed = copy.deepcopy(base)
        qualified_inputs = []
        original_qualify = observed.qualify

        def count_qualification(view_row, refs, recipe):
            qualified_inputs.append(tuple(sorted(set(refs))))
            return original_qualify(view_row, refs, recipe)

        observed.qualify = count_qualification
        directed.prepare_reference_views(
            observed, directed.recipe_named("directed-corrective-starting-045"),
        )
        self.assertEqual(qualified_inputs.count(tuple(refs[:6])), 1)
        self.assertEqual(results[.45][0], set(refs[:6]))
        self.assertEqual(results[.50][0], set(refs[:5]))
        self.assertEqual(results[.60][0], set(refs[:4]))
        self.assertEqual(results[.45][1], set(refs[:6]))
        self.assertEqual(results[.50][1], set(refs[:5]))
        self.assertEqual(results[.60][1], set(refs[:4]))
        self.assertEqual(set(base.source), original_population)

    def test_withdrawn_stale_duplicate_and_no_reference_owners_do_not_self_certify(self):
        fixture = self.fixture()
        rows, measured, catalog, cohorts, add = fixture
        alone = add("Models/Only One", 9, count=1)[0]
        alone_cast = add("Angels/Only One", 14, count=1)[0]
        rows[-1].update(castSeedCore=True, castSeedScore=.99)
        duplicates = add("Potentials/Duplicate Source", 10)
        duplicate_vector = measured[rows[-1]["source"]].vec
        for row in rows:
            if row["photoId"] in duplicates:
                measured[row["source"]].vec = duplicate_vector
        stale = cohorts["Models/Model Source"][0]
        catalog["photos"][stale] = {"contentSha256": "f" * 64, "protected": False}
        withdrawn = cohorts["Sisters/Sister Source"][0]
        output, report = self.run_fixture(fixture, reference_exclusions={withdrawn})
        by_id = {row["photoId"]: row for row in output}
        for pid in [alone, alone_cast, stale, withdrawn, *duplicates]:
            self.assertFalse(by_id[pid]["membership"]["coreUse"], pid)
            self.assertEqual(by_id[pid]["source"], by_id[pid]["destination"])
        self.assertEqual(catalog["photos"][stale]["contentSha256"], "f" * 64)
        self.assertFalse(by_id[alone_cast]["directedReformation"]["verifiedStrongBaseline"])
        stages = {stage["id"]: stage for stage in report["stages"]}
        reference_stage = directed.lifecycle_stage(stages["references"])
        publication_stage = directed.lifecycle_stage(stages["publication"])
        self.assertTrue(reference_stage["referenceWithdrawals"])
        initial = next(row for row in reference_stage["rows"] if row["photoId"] == withdrawn)
        final = next(row for row in publication_stage["rows"] if row["photoId"] == withdrawn)
        self.assertFalse(initial["referenceEligibleAtBoundary"])
        self.assertEqual(initial["status"], "membership-not-yet-assessed")
        self.assertEqual(final["status"], "supported")
        self.assertFalse(final["coreUse"])
        unavailable = set(report["evaluation"]["sourceCoreSelection"]["referenceUnavailablePersonIds"])
        for folder in ("Models/Only One", "Angels/Only One", "Potentials/Duplicate Source"):
            owner = next(p["id"] for p in catalog["people"].values() if p["folder"] == folder)
            self.assertIn(owner, unavailable)
        alone_state = next(row for row in reference_stage["rows"] if row["photoId"] == alone_cast)
        qualification = alone_state["candidateReferenceQualification"]
        self.assertIsNone(qualification["independentOwnCentroidScore"])
        self.assertEqual(qualification["actualIndependentPairSupport"], 0)
        self.assertEqual(qualification["pairSupportMinimum"], .60)
        self.assert_reference_exports(output, report, catalog)

    def test_various_only_empty_catalogue_can_form_an_independent_identity(self):
        fixture = self.fixture()
        incoming = fixture[3]["Various"][:6]
        rows = [row for row in fixture[0] if row["photoId"] in incoming]
        reduced = (rows, *fixture[1:])
        output, report = self.run_fixture(reduced)
        self.assertEqual(len(fixture[2]["people"]), 1)
        self.assertEqual(report["evaluation"]["independentResidualCandidates"], 1)
        self.assertTrue(all(row["membership"]["status"] == "supported" for row in output))
        self.assertTrue(all(row["destination"].startswith("Prospects/Nova ") for row in output))
        self.assert_reference_exports(output, report, fixture[2])

    def test_new_residual_models_rule_receives_measured_qualified_cast_similarity(self):
        from tools.art.likeness_library.policy import load_policy
        fixture = self.fixture()
        rows, measured = fixture[:2]
        incoming = fixture[3]["Various"][:6]
        for row in rows:
            if row["photoId"] not in incoming:
                continue
            vector = measured[row["source"]].vec
            vector[5] = .8 * np.sqrt(1 - .43 ** 2)
            vector[0] = .8 * .43
        held_fixture = copy.deepcopy(fixture)
        held_output, held_report = self.run_fixture(held_fixture)
        held = held_report["residualClassifications"][0]
        self.assertEqual(held["classification"]["category"], "Models")
        self.assertTrue(held["classification"]["reviewRequired"])
        self.assertEqual(held["disposition"], "classification-review-hold")
        self.assertTrue(held["qualifiedReferencePhotoIds"])
        self.assertFalse(held_report["independentIdentities"])
        for row in held_output:
            if row["photoId"] in incoming:
                self.assertTrue(row["destination"].startswith("Potentials/"))
                self.assertEqual(row["membership"]["assignmentDisposition"], "provisional")
                self.assertFalse(row["membership"]["coreUse"])
                self.assertEqual(row["directedReformation"]["independentCandidateFolder"],
                                 held["candidateFolder"])
        policy = load_policy()
        policy["castReviewMinimum"] = .54
        output, report = self.run_fixture(fixture, policy=policy)
        independent = next(item for item in report["independentIdentities"]
                           if set(item["memberPhotoIds"]) == set(incoming))
        self.assertTrue(independent["folder"].startswith("Models/"))
        self.assertGreaterEqual(independent["classification"]["castSimilarity"], .4)
        self.assertLess(independent["classification"]["castSimilarity"], .55)
        self.assertTrue(all(row["destination"].startswith("Models/")
                            for row in output if row["photoId"] in incoming))
        measurement = next(item for item in report["residualClassifications"]
                           if set(item["memberPhotoIds"]) == set(incoming))
        self.assertFalse(measurement["castReferenceUnavailable"])
        self.assertTrue(measurement["rankedQualifiedCastScores"])
        self.assert_reference_exports(output, report, fixture[2])

    def test_small_residual_cohorts_receive_provisional_noncore_routes_without_bootstrap(self):
        for count in (1, 2, 3):
            fixture = self.fixture()
            incoming = set(fixture[3]["Various"][:count])
            rows = [row for row in fixture[0] if row["photoId"] in incoming]
            for row in rows:
                row["reason"] = "stale pre-directed approved cast admission"
                row["castAdmission"] = {"approved": True}
            output, report = self.run_fixture(
                (rows, *fixture[1:]),
                directed_recipe="directed-corrective-starting-050",
            )
            self.assertEqual(len(fixture[2]["people"]), 1)
            self.assertEqual(len(fixture[2]["photoGroups"]), 1)
            self.assertFalse(report["independentIdentities"])
            self.assertEqual(len(report["provisionalContainers"]), 1)
            self.assertEqual(report["assignmentSummary"]["activeVarious"], 0)
            if count == 1:
                for row in output:
                    self.assertEqual(row["membership"]["assignmentDisposition"], "provisional")
                    self.assertFalse(row["membership"]["coreUse"])
                self.assert_reference_exports(output, report, fixture[2])
                continue
            held = report["residualClassifications"][0]
            self.assertEqual(held["classification"]["category"], "Potentials")
            self.assertTrue(held["candidateFolder"].startswith("Potentials/Nova "))
            self.assertEqual(held["disposition"], "independent-reference-insufficient")
            self.assertEqual(held["qualifiedReferencePhotoIds"], [])
            self.assertEqual(held["coreSupportMinimum"], 3)
            self.assertTrue(all(item["independentPairSupport"] == count - 1
                                for item in held["candidateQualification"]))
            publication = next(stage for stage in report["stages"] if stage["id"] == "publication")
            self.assertTrue(all(row["independentCandidateFolder"] == held["candidateFolder"]
                                for row in publication["rows"]))
            for row in output:
                self.assertTrue(row["destination"].startswith("Potentials/"))
                self.assertEqual(row["membership"]["assignmentDisposition"], "provisional")
                self.assertFalse(row["membership"]["coreUse"])
                self.assertIn("independent-reference-insufficient", row["reason"])
                self.assertNotIn("stale pre-directed", row["reason"])
                self.assertNotIn("castAdmission", row)
            self.assert_reference_exports(output, report, fixture[2])

        fixture = self.fixture()
        incoming = set(fixture[3]["Various"][:4])
        rows = [row for row in fixture[0] if row["photoId"] in incoming]
        for row in rows:
            row["reason"] = "stale pre-directed approved cast admission"
            row["castAdmission"] = {"approved": True}
        output, report = self.run_fixture(
            (rows, *fixture[1:]),
            directed_recipe="directed-corrective-starting-050",
        )
        self.assertEqual(len(report["independentIdentities"]), 1)
        identity = report["independentIdentities"][0]
        self.assertEqual(set(identity["qualifiedReferencePhotoIds"]), incoming)
        self.assertTrue(all(not row["membership"]["coreUse"] for row in output))

    def test_provisional_export_reload_second_run_never_bootstraps_or_attracts(self):
        fixture = self.fixture()
        incoming = set(fixture[3]["Various"][:4])
        rows = [row for row in fixture[0] if row["photoId"] in incoming]
        output, report = self.run_fixture((rows, *fixture[1:]))
        container = report["provisionalContainers"][0]
        catalog = json.loads(json.dumps(fixture[2]))
        replay_rows, replay_measurements = [], {}
        for row in output:
            replay = {**row, "source": row["destination"], "oldFolder": container["folder"]}
            replay_rows.append(replay)
            replay_measurements[replay["source"]] = fixture[1][row["source"]]
        added = fixture[-1]("Various", 5, count=1)[0]
        replay_rows.append(fixture[0][-1])
        replay_measurements[fixture[0][-1]["source"]] = fixture[1][fixture[0][-1]["source"]]
        before = {(row["photoId"], row["sha256"]) for row in replay_rows}
        second, second_report = self.run_fixture((replay_rows, replay_measurements, catalog))
        self.assertEqual(before, {(row["photoId"], row["sha256"]) for row in second})
        self.assertFalse(any(row["membership"]["coreUse"] for row in second))
        self.assertFalse(any(view["qualifiedReferencePhotoIds"] for view in second_report["qualifiedReferences"]))
        new_row = next(row for row in second if row["photoId"] == added)
        self.assertNotEqual(new_row["membership"]["personId"], container["personId"])
        self.assertEqual(new_row["membership"]["assignmentDisposition"], "provisional")
        for row in second:
            if row["photoId"] in incoming:
                self.assertEqual(row["membership"]["personId"], container["personId"])
                self.assertEqual(row["membership"]["assignmentDisposition"], "provisional")
        self.assert_reference_exports(second, second_report, catalog)

    def test_credible_tentative_parent_assigns_gallery_but_never_core(self):
        fixture = self.fixture()
        rows, measured, catalog, cohorts, add = fixture
        pid = add("Various", 12, count=1)[0]
        model_rows = [row for row in rows if row["photoId"] in cohorts["Models/Model Source"]]
        vector = np.zeros(192)
        vector[2] = .45
        for row in model_rows[:2]:
            original = measured[row["source"]].vec
            vector[np.argmax(original[32:]) + 32] = .55
        vector[160] = np.sqrt(1 - .45 ** 2 - 2 * .55 ** 2)
        measured[rows[-1]["source"]].vec = vector
        output, report = self.run_fixture(fixture)
        row = next(row for row in output if row["photoId"] == pid)
        self.assertTrue(row["destination"].startswith("Models/Model Source/gallery/"))
        self.assertEqual(row["membership"]["assignmentDisposition"], "tentative-parent")
        self.assertFalse(row["membership"]["coreUse"])
        self.assertEqual(len(row["membership"]["assignmentEvidence"]["supportPhotoIds"]), 2)
        self.assert_reference_exports(output, report, catalog)
        for _ in range(2):
            replay, replay_measurements = [], {}
            for item in output:
                replay.append({**item, "source": item["destination"],
                               "oldFolder": str(pathlib.PurePosixPath(item["destination"]).parent.parent)})
                replay_measurements[item["destination"]] = measured[item["source"]]
            catalog = json.loads(json.dumps(catalog))
            output, report = self.run_fixture((replay, replay_measurements, catalog))
            row = next(item for item in output if item["photoId"] == pid)
            self.assertEqual(row["membership"]["assignmentDisposition"], "tentative-parent")
            self.assertFalse(row["membership"]["coreUse"])
            self.assert_reference_exports(output, report, catalog)
            measured = replay_measurements

    def test_two_supporter_cast_candidate_can_be_tentative_but_not_qualified_or_reference_eligible(self):
        from tools.art.likeness_library.policy import load_policy
        evidence = self.build(
            category="Potentials", person="lower-id", own=.1,
            targets=[{
                "id": "angel-view", "folder": "Angels/Angel", "category": "Angels",
                "personId": "angel-owner", "score": .55,
            }],
        )
        source = evidence.source["candidate"]
        source.update(oldFolder="Various", oldPersonId=None, membershipAssessment={"own": {}})
        source["runtimeCastAdmission"] = {
            "qualityEligible": True, "metadataStale": False,
            "rejectionHistory": False, "protected": False,
        }
        evidence.settings = load_policy()
        evidence.supports["candidate"] = {
            "angel-view-r0": .9, "angel-view-r1": .9,
        }
        recipe = directed.recipe_named("directed-corrective-starting-050")
        result = directed.run_variant(evidence, recipe)
        row = self.row(result)
        option = next(item for item in row["tentativeAssociations"]
                      if item["personId"] == "angel-owner")
        self.assertFalse(option["individuallyQualified"])
        self.assertIn("insufficient-independent-member-support", option["blockers"])
        self.assertEqual(len(option["independentSupportPhotoIds"]), 2)
        self.assertEqual(option["castAdmission"]["decision"], "hold")
        self.assertTrue(option["tentativeAssignmentEligible"])
        self.assertEqual(option["tentativeAssignmentBlockers"], [])
        self.assertFalse(row["referenceUseEligible"])
        self.assertIsNone(row["candidateDestination"])

    def test_tentative_cast_assignment_stays_nonreference_after_reload_and_new_arrival(self):
        fixture = self.fixture()
        rows, measured, catalog, cohorts, add = fixture
        cast_ids = cohorts["Angels/Angel Source"]
        for index, photo_id in enumerate(cast_ids):
            source = next(row["source"] for row in rows if row["photoId"] == photo_id)
            vector = np.zeros(192)
            if index < 2:
                vector[11], vector[12], vector[20 + index] = .9, .25, np.sqrt(.1275)
            else:
                vector[11], vector[12], vector[30 + index] = .35, .85, np.sqrt(.155)
            measured[source].vec = vector
        candidate = add("Various", 11, count=1)[0]
        measured[rows[-1]["source"]].vec = np.eye(1, 192, 11)[0]
        output, report = self.run_fixture(
            fixture, directed_recipe="directed-corrective-starting-050",
        )
        by_id = {row["photoId"]: row for row in output}
        assigned = by_id[candidate]
        self.assertTrue(assigned["destination"].startswith("Angels/Angel Source/gallery/"))
        self.assertEqual(assigned["membership"]["assignmentDisposition"], "tentative-parent")
        self.assertFalse(assigned["membership"]["coreUse"])
        decision = directed.unpack_runtime_decisions(report["decisionEvidence"])[candidate]
        option = next(item for item in decision["tentativeAssociations"]
                      if item["folder"] == "Angels/Angel Source")
        self.assertTrue(option["tentativeAssignmentEligible"])
        self.assertEqual(len(option["independentSupportPhotoIds"]), 2)
        self.assertFalse(option["individuallyQualified"])
        self.assertGreaterEqual(option["score"], option["admissionFloor"])
        self.assertGreaterEqual(option["signedDistinctRivalMargin"], .10)
        self.assertIn("insufficient independent frozen destination-core support",
                      option["castAdmission"]["reason"])
        self.assert_reference_exports(output, report, catalog)

        added = add("Various", 11, count=1)[0]
        measured[rows[-1]["source"]].vec = np.eye(1, 192, 11)[0]
        replay, replay_measurements = [], {}
        for item in output:
            replay.append({
                **item, "source": item["destination"],
                "oldFolder": str(pathlib.PurePosixPath(item["destination"]).parent.parent),
            })
            replay_measurements[item["destination"]] = measured[item["source"]]
        replay.append(rows[-1])
        replay_measurements[rows[-1]["source"]] = measured[rows[-1]["source"]]
        replay_catalog = json.loads(json.dumps(catalog))
        second, second_report = self.run_fixture(
            (replay, replay_measurements, replay_catalog),
            directed_recipe="directed-corrective-starting-050",
        )
        second_by_id = {row["photoId"]: row for row in second}
        for photo_id in (candidate, added):
            row = second_by_id[photo_id]
            self.assertTrue(row["destination"].startswith("Angels/Angel Source/gallery/"))
            self.assertEqual(row["membership"]["assignmentDisposition"], "tentative-parent")
            self.assertFalse(row["membership"]["coreUse"])
        self.assert_reference_exports(second, second_report, replay_catalog)

    def test_missing_source_score_reports_exact_reference_inventory_without_quality_fallback(self):
        evidence = self.build(category="Angels", person="angel-owner")
        source_view = evidence.views[0]
        source_view["original"].append("candidate")
        source_view["frozenReferencePhotoIds"].append("candidate")
        evidence.vectors.pop("candidate")
        evidence.cache.indices.pop("candidate")
        evidence.cache.indices = {
            pid: index for index, pid in enumerate(sorted(evidence.cache.indices))
        }
        evidence.eligible.discard("candidate")
        evidence.source["candidate"]["reasons"] = ["quality-ineligible"]
        result = directed.run_variant(
            evidence, directed.recipe_named("directed-corrective-starting-050"), reconcile=True,
        )
        boundary = directed.unpack_boundary_snapshot(
            next(stage for stage in result["boundarySnapshots"] if stage["id"] == "references")
        )
        row = next(item for item in boundary["rows"] if item["photoId"] == "candidate")
        provenance = row["sourceReferenceEvidence"]
        self.assertIsNone(provenance["frozenOwnScore"])
        self.assertEqual(provenance["candidateReferenceCount"], 5)
        self.assertEqual(set(provenance["candidateReferencePhotoIds"]),
                         {"candidate", "src0", "src1", "src2", "src3"})
        self.assertEqual(provenance["qualifiedReferencePhotoIds"], [])
        self.assertIn("quality-ineligible", provenance["qualityAndInputReasons"])
        self.assertIn("no quality-score substitution", provenance["reason"])
        self.assertIn("frozen-source-score-unavailable; no quality-score substitution",
                      provenance["blockers"])
        page = directed.summary_for_page({"variants": [result]})
        page_row = next(item for item in page["variants"][0]["rows"]
                        if item["photoId"] == "candidate")
        self.assertEqual(page_row["sourceReferenceEvidence"]["candidateReferenceCount"], 5)
        self.assertEqual(page_row["sourceReferenceEvidence"]["qualifiedReferenceCount"], 0)
        rendered = directed.render({
            "control": {
                "name": "control", "populationCount": 1, "proposalCount": 0,
                "logicalReleases": 0, "changedSourceDestinations": 0,
            },
            "variants": [result],
            "verification": {"reverseOrderVerified": True},
        }, {})
        self.assertIn("Frozen source-reference gate:", rendered)
        self.assertIn("Source-reference blockers:", rendered)
        self.assertIn("Family-semantic audit:", rendered)
        qualification = row["candidateReferenceQualification"]
        self.assertIsNone(qualification["independentOwnCentroidScore"])
        self.assertEqual(qualification["candidateReferencePhotoIds"],
                         provenance["candidateReferencePhotoIds"])
        self.assertEqual(qualification["requiredIndependentPairSupport"], 3)

    def test_intake_quality_and_physical_locks_are_explicit_exceptions_not_forced_junk(self):
        fixture = self.fixture()
        rows, measured, catalog, cohorts = fixture[:4]
        singleton, quality = cohorts["Various"][-2:]
        source = next(row for row in rows if row["photoId"] == singleton)
        catalog["photos"][singleton] = {"contentSha256": source["sha256"], "protected": True}
        output, report = self.run_fixture(fixture)
        for row in output:
            if row["photoId"] in (singleton, quality):
                self.assertEqual(row["source"], row["destination"])
                self.assertFalse(row["membership"]["coreUse"])
                self.assertIn("intake exception", row["reason"])
        self.assertEqual({row["photoId"] for row in report["assignmentSummary"]["exceptions"]},
                         {singleton, quality})
        self.assertEqual(report["assignmentSummary"]["junk"], 0)

    def test_assignment_metadata_rejects_reference_leakage_and_reader_labels_provisional(self):
        from tools.art.likeness_library import group_views, metadata
        fixture = self.fixture()
        output, report = self.run_fixture(fixture)
        row = next(row for row in output if row["membership"]["assignmentDisposition"] == "provisional")
        pid = row["photoId"]
        self.assertIn("not a certified identity", group_views.describe(fixture[2], pid)["label"])
        for disposition in ("provisional", "tentative-parent"):
            catalog = json.loads(json.dumps(fixture[2]))
            membership = catalog["photos"][pid]["membership"]
            membership.update(coreUse=True, assignmentDisposition=disposition)
            with self.assertRaisesRegex(ValueError, "assignment-only members cannot contribute references"):
                metadata.validate_catalog(catalog)
        catalog = json.loads(json.dumps(fixture[2]))
        catalog["photos"][pid]["membership"].pop("assignmentDisposition")
        catalog["photos"][pid]["membership"]["coreUse"] = True
        with self.assertRaisesRegex(ValueError, "provisional containers cannot contribute references"):
            metadata.validate_catalog(catalog)

    def test_quality_rejected_only_at_regroup_boundary_has_explicit_reason_and_complete_counts(self):
        fixture = self.fixture()
        rows, measured, catalog, cohorts, add = fixture
        cases = [
            (2, .1, 150, True, "ambiguous-multiface", False),
            (-1, 0, 150, True, "missing-or-unusable-measurement", False),
            (0, 0, 150, False, "missing-or-unusable-measurement", False),
            (1, 0, 50, True, "measured-face-too-small", True),
        ]
        created = {}
        for faces, f2, px, vector_present, classification, junk_candidate in cases:
            pid = add("Various", 12, count=1)[0]
            row = rows[-1]
            photo = measured[row["source"]]
            photo.faces, photo.f2, photo.px = faces, f2, px
            if not vector_present:
                photo.vec = photo.raw = None
            created[pid] = classification, junk_candidate
        missing = add("Various", 12, count=1)[0]
        measured.pop(rows[-1]["source"])
        created[missing] = "missing-measurement", False
        output, report = self.run_fixture(fixture)
        exceptions = {item["photoId"]: item for item in report["assignmentSummary"]["exceptions"]}
        for pid, (classification, junk_candidate) in created.items():
            item = exceptions[pid]
            quality = item["qualityEvidence"]
            self.assertEqual(quality["classification"], classification)
            self.assertEqual(quality["recoverableJunkCandidate"], junk_candidate)
            self.assertTrue(quality["qualityReason"])
            self.assertEqual(item["source"], item["destination"])
            self.assertEqual("recoverable-junk-publication-unavailable" in item["reason"], junk_candidate)
        self.assertEqual(sum(report["assignmentSummary"]["qualityExceptionCounts"].values()),
                         len(created) + 1)
        self.assert_reference_exports(output, report, catalog)

    def test_dominant_optin_only_provisional_never_reference_or_parent_and_survives_reload(self):
        baseline = self.fixture()
        rows, measured, catalog, cohorts = baseline[:4]
        dominant = set(cohorts["Various"][:6])
        for row in rows:
            if row["photoId"] in dominant:
                measured[row["source"]].faces = 2
                measured[row["source"]].f2 = .1
                measured[row["source"]].secondary_face_ratio_available = True
        output, report = self.run_fixture(copy.deepcopy(baseline))
        self.assertTrue(all(row["destination"].startswith("Various/")
                            for row in output if row["photoId"] in dominant))
        output, report = self.run_fixture(baseline, dominant_provisional=True)
        selected = [row for row in output if row["photoId"] in dominant]
        self.assertEqual(len({row["membership"]["personId"] for row in selected}), 1)
        self.assertTrue(all(row["destination"].startswith("Potentials/") for row in selected))
        self.assertTrue(all(row["membership"]["assignmentDisposition"] == "provisional"
                            and not row["membership"]["coreUse"] for row in selected))
        self.assertEqual(report["assignmentPolicy"]["assignedDominantPhotoIds"], sorted(dominant))
        self.assertEqual(selected[0]["membership"]["assignmentEvidence"]["dominantFace"]["secondaryFaceRatio"], .1)
        self.assert_reference_exports(output, report, catalog)
        parent = selected[0]["membership"]["personId"]
        replay, replay_measurements = [], {}
        for row in output:
            replay.append({**row, "source": row["destination"],
                           "oldFolder": str(pathlib.PurePosixPath(row["destination"]).parent.parent)})
            replay_measurements[row["destination"]] = measured[row["source"]]
        incoming_id = "photo:image_999001"
        incoming_source = "Various/gallery/incoming_image_999001.jpg"
        replay.append({
            "photoId": incoming_id, "source": incoming_source, "destination": incoming_source,
            "oldFolder": "Various", "sha256": "f" * 64,
        })
        incoming_photo = copy.deepcopy(measured[selected[0]["source"]])
        incoming_photo.faces, incoming_photo.f2 = 1, 0
        replay_measurements[incoming_source] = incoming_photo
        catalog = json.loads(json.dumps(catalog))
        output, report = self.run_fixture((replay, replay_measurements, catalog))
        self.assertTrue(all(not row["membership"]["coreUse"] for row in output
                            if row["photoId"] in dominant))
        self.assertFalse(any(view["qualifiedReferencePhotoIds"] for view in report["qualifiedReferences"]
                             if view["personId"] == parent))
        self.assertTrue(all(row["membership"]["assignmentEvidence"].get("dominantFace")
                            for row in output if row["photoId"] in dominant))
        self.assertNotEqual(next(row["membership"]["personId"] for row in output
                                 if row["photoId"] == incoming_id), parent)
        self.assert_reference_exports(output, report, catalog)

    def test_dominant_boundary_quality_and_lock_safeguards_are_not_relaxed(self):
        fixture = self.fixture()
        rows, measured, catalog, cohorts = fixture[:4]
        ids = cohorts["Various"][:6]
        for index, pid in enumerate(ids):
            row = next(item for item in rows if item["photoId"] == pid)
            photo = measured[row["source"]]
            photo.faces, photo.f2 = 2, [.3, .31, -.1, .1, .1, .1][index]
            photo.secondary_face_ratio_available = True
            if index == 3:
                photo.px = 20
            if index == 4:
                row["qualityHold"] = True
            if index == 5:
                catalog["photos"][pid] = {"contentSha256": row["sha256"], "protected": True}
        missing_ratio = cohorts["Various"][-2]
        row = next(item for item in rows if item["photoId"] == missing_ratio)
        measured[row["source"]].faces = 2
        measured[row["source"]].f2 = 0
        measured[row["source"]].secondary_face_ratio_available = False
        ids = [*ids, missing_ratio]
        output, report = self.run_fixture(fixture, dominant_provisional=True)
        self.assertFalse(report["assignmentPolicy"]["assignedDominantPhotoIds"])
        self.assertTrue(all(row["source"] == row["destination"] for row in output if row["photoId"] in ids))

    def test_selected_angel_and_sister_arrivals_and_wrong_cast_correction_use_shared_gates(self):
        from tools.art.likeness_library.policy import load_policy, validate_policy
        fixture = self.fixture()
        rows, measured, catalog, cohorts, add = fixture
        source_by_id = {row["photoId"]: row for row in rows}
        arrivals = {}
        for folder in ("Angels/Angel Source", "Sisters/Sister Source"):
            pid = add("Various", 11, count=1)[0]
            row = rows[-1]
            measured[row["source"]].vec = measured[source_by_id[cohorts[folder][0]]["source"]].vec.copy()
            arrivals[pid] = folder
        wrong = add("Angels/Angel Source", 12, count=1)[0]
        measured[rows[-1]["source"]].vec = measured[
            source_by_id[cohorts["Models/Model Source"][0]]["source"]
        ].vec.copy()
        policy = load_policy()
        policy["categoryPolicies"]["Angels"].pop("galleryAdmissionEnabled", None)
        original_policy = copy.deepcopy(policy)
        selected = directed.runtime_policy(policy, directed.recipe_named("directed-core-continuity"))
        validate_policy(selected)
        self.assertEqual(policy, original_policy)
        self.assertTrue(selected["categoryPolicies"]["Angels"]["galleryAdmissionEnabled"])
        self.assertEqual(selected, directed.runtime_policy(selected, directed.recipe_named("directed-core-continuity")))
        output, report = self.run_fixture(fixture, policy=policy)
        by_id = {row["photoId"]: row for row in output}
        for pid, folder in arrivals.items():
            row = by_id[pid]
            self.assertTrue(row["destination"].startswith(folder + "/gallery/"))
            self.assertEqual(row["castAdmission"]["decision"], "admit")
            self.assertGreaterEqual(row["castAdmission"]["independentSupport"], 2)
            self.assertTrue(row["castAdmission"]["referencePhotoIds"])
        self.assertEqual(by_id[wrong]["directedReformation"]["actionCategory"], "correction")
        self.assertTrue(by_id[wrong]["destination"].startswith("Models/Model Source/gallery/"))
        self.assert_reference_exports(output, report, catalog)

    def test_complete_distinct_rivals_negative_pair_and_ambiguous_intake_are_not_collapsed(self):
        fixture = self.fixture()
        rows, measured, catalog, cohorts, add = fixture
        pid = add("Various", 11, count=1)[0]
        candidate = rows[-1]
        vector = np.zeros(192)
        vector[2], vector[3], vector[160] = .6, .6, np.sqrt(.28)
        measured[candidate["source"]].vec = vector
        pairs = [{"photoIds": [pid, cohorts["Models/Model Source"][0]], "label": "different"}]
        output, report = self.run_fixture(fixture, pairs=pairs)
        row = next(row for row in output if row["photoId"] == pid)
        self.assertTrue(row["destination"].startswith("Potentials/"))
        self.assertEqual(row["membership"]["assignmentDisposition"], "provisional")
        self.assertFalse(row["membership"]["coreUse"])
        options = directed.unpack_runtime_decisions(report["decisionEvidence"])[pid]["rivals"]
        self.assertTrue({"Models/Model Source", "Prospects/Prospect Source"} <= {r["folder"] for r in options})
        model = next(option for option in options if option["folder"] == "Models/Model Source")
        self.assertIn("exact-different-or-uncertain-veto", model["blockers"])
        self.assertFalse(model["individuallyQualified"])
        self.assertEqual(len({p["id"] for p in catalog["people"].values()}), 8)
        self.assert_reference_exports(output, report, catalog)

    def test_configured_identity_negative_uses_case_history_and_incoming_source_lineage(self):
        from tools.art.likeness_library.policy import load_policy
        fixture = self.fixture()
        rows, measured, catalog, cohorts, add = fixture
        incoming = add("Various", 11, count=1)[0]
        measured[rows[-1]["source"]].vec = measured[rows[0]["source"]].vec.copy()
        prior_owner = "person_" + "a" * 32
        catalog["people"][prior_owner] = {
            "id": prior_owner, "folder": "Prospects/Renamed",
            "folderHistory": ["Prospects/Old Name"], "identityAnchors": [],
            "displayName": "Renamed", "protected": False,
        }
        catalog["photos"][incoming] = {
            "contentSha256": rows[-1]["sha256"], "protected": False,
            "membership": {"personId": prior_owner, "status": "tentative"},
        }
        policy = load_policy()
        policy["runtimeSettings"]["different"] = [
            ["prospects/OLD NAME", "sisters/SISTER SOURCE"],
        ]
        output, report = self.run_fixture(fixture, policy=policy)
        row = next(row for row in output if row["photoId"] == incoming)
        self.assertTrue(row["destination"].startswith("Potentials/"))
        rival = next(item for item in directed.unpack_runtime_decisions(
            report["decisionEvidence"])[incoming]["rivals"] if item["category"] == "Sisters")
        self.assertIn("configured-different-identity-veto", rival["blockers"])
        self.assertFalse(rival["individuallyQualified"])
        self.assertEqual(report["configuredIdentityNegatives"][0]["status"], "resolved")
        self.assertIn(prior_owner, report["configuredIdentityNegatives"][0]["personIds"])
        self.assert_reference_exports(output, report, catalog)

    def test_configured_negative_resolution_refuses_ambiguity_and_collapsed_owners(self):
        people = {
            "a": {"folder": "Models/A", "folderHistory": ["Models/Old"]},
            "b": {"folder": "Models/B", "folderHistory": ["models/OLD"]},
        }
        with self.assertRaisesRegex(ValueError, "ambiguous configured"):
            directed._configured_negative_bindings(people, [["Models/Old", "Models/B"]])
        with self.assertRaisesRegex(ValueError, "same owner"):
            directed._configured_negative_bindings(people, [["Models/A", "Models/A"]])
        pairs, diagnostics = directed._configured_negative_bindings(
            people, [["Models/Absent", "Models/B"]])
        self.assertFalse(pairs)
        self.assertEqual(diagnostics[0]["status"], "nonparticipating-absent-owner")
        self.assertEqual(diagnostics[0]["absentFolders"], ["Models/Absent"])

    def test_historical_source_alias_reuses_owner_and_conflicting_lineage_withdraws_core(self):
        from tools.art.likeness_library.policy import load_policy
        fixture = self.fixture()
        rows, measured, catalog, cohorts = fixture[:4]
        owner_id, other_id = "person_" + "a" * 32, "person_" + "b" * 32
        catalog["people"][owner_id] = {
            "id": owner_id, "folder": "Models/Renamed", "displayName": "Renamed",
            "folderHistory": ["Models/Model Source"], "identityAnchors": [], "protected": False,
        }
        catalog["people"][other_id] = {
            "id": other_id, "folder": "Prospects/Other", "displayName": "Other",
            "folderHistory": [], "identityAnchors": [], "protected": False,
        }
        pid = cohorts["Models/Model Source"][0]
        row = next(row for row in rows if row["photoId"] == pid)
        catalog["photos"][pid] = {
            "contentSha256": row["sha256"], "protected": False,
            "membership": {"personId": other_id, "status": "tentative"},
        }
        policy = load_policy()
        policy["runtimeSettings"]["different"] = [["Models/Model Source", "Prospects/Other"]]
        output, report = self.run_fixture(fixture, policy=policy)
        source = [row for row in output if row["photoId"] in cohorts["Models/Model Source"]]
        self.assertEqual({row["directedReformation"]["sourcePersonId"] for row in source}, {owner_id})
        self.assertFalse(any(person["folder"] == "Models/Model Source"
                             for person in catalog["people"].values()))
        self.assertFalse(any(row["membership"]["coreUse"] for row in source))
        self.assertTrue(any(item["referenceUnavailable"]
                            for item in report["initialReferenceValidation"]))
        self.assert_reference_exports(output, report, catalog)

    def test_parentless_residual_cannot_recombine_configured_distinct_source_owners(self):
        from tools.art.likeness_library.policy import load_policy
        fixture = self.fixture()
        rows, measured, catalog, cohorts = fixture[:4]
        incoming = cohorts["Various"][:6]
        for owner in ("A", "B"):
            owner_id = "person_" + owner.lower() * 32
            catalog["people"][owner_id] = {
                "id": owner_id, "folder": f"Prospects/{owner}", "displayName": owner,
                "folderHistory": [], "identityAnchors": [], "protected": False,
            }
        for i, pid in enumerate(incoming):
            row = next(row for row in rows if row["photoId"] == pid)
            catalog["photos"][pid] = {
                "contentSha256": row["sha256"], "protected": False,
                "membership": {"personId": "person_" + ("a" if i < 3 else "b") * 32,
                               "status": "tentative"},
            }
        policy = load_policy()
        policy["runtimeSettings"]["different"] = [["Prospects/A", "Prospects/B"]]
        output, report = self.run_fixture(fixture, policy=policy)
        self.assertFalse(report["independentIdentities"])
        containers = [item for item in report["provisionalContainers"]
                      if set(item["memberPhotoIds"]) & set(incoming)]
        self.assertEqual(len(containers), 2)
        self.assertTrue(all(len(item["memberPhotoIds"]) == 3 for item in containers))
        self.assertTrue(all(row["membership"]["assignmentDisposition"] == "provisional"
                            for row in output if row["photoId"] in incoming))

    def test_nonclique_reference_neighbourhood_recovers_without_union_or_bootstrap(self):
        fixture = self.fixture()
        rows, measured, catalog, cohorts, add = fixture
        core = add("Angels/Nonclique", 9, count=7)
        contamination = add("Angels/Nonclique", 10)
        gram = np.full((7, 7), .62)
        np.fill_diagonal(gram, 1.)
        for a, b in ((1, 2), (3, 4), (5, 6)):
            gram[a, b] = gram[b, a] = .5
        vectors = np.linalg.cholesky(gram)
        for i, pid in enumerate(core):
            row = next(row for row in rows if row["photoId"] == pid)
            vector = np.zeros(192)
            vector[12:19] = vectors[i]
            measured[row["source"]].vec = vector
        output, report = self.run_fixture(fixture)
        recovered = [view for view in report["qualifiedReferences"]
                     if view.get("referenceConstruction") == "independent-anchor-neighbourhood"
                     and view["folder"] == "Angels/Nonclique"]
        self.assertTrue(any(set(view["qualifiedReferencePhotoIds"]) == set(core) for view in recovered))
        self.assertGreater(len(recovered), 1)
        self.assertTrue(all(not set(view["qualifiedReferencePhotoIds"]) & set(contamination)
                            for view in recovered))
        self.assertTrue(all(view["referenceStable"] for view in recovered))
        self.assert_reference_exports(output, report, catalog)
        # Reordering the measured fixture cannot change selected neighbourhoods.
        replay = (list(reversed(rows)), measured, {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
                  cohorts, add)
        _, second = self.run_fixture(replay)
        self.assertEqual(report["qualifiedReferences"], second["qualifiedReferences"])

    def test_constrained_average_link_reduces_fragmentation_without_bridges_or_cannot_link_merges(self):
        evidence = self.build()
        ids = ["cohort-a", "cohort-b", "cohort-c", "cohort-d"]
        for index, pid in enumerate(ids):
            evidence.source[pid] = {
                "photoId": pid, "oldFolder": "Various", "oldPersonId": None,
                "sourceIdentityIds": [],
            }
            evidence.hashes[pid] = f"content-{index}"
            evidence.cache.indices[pid] = len(evidence.cache.indices)
        high = {
            ("cohort-a", "cohort-b"), ("cohort-a", "cohort-c"),
            ("cohort-b", "cohort-c"), ("cohort-b", "cohort-d"),
            ("cohort-c", "cohort-d"),
        }
        for left_index, left in enumerate(ids):
            for right in ids[left_index + 1:]:
                evidence.cache.pair_scores[tuple(sorted((left, right)))] = (
                    .8 if (left, right) in high else .1
                )
        strict = directed._complete_link_clusters(ids, evidence, .45, directed.MAX_CLUSTER_OPERATIONS)
        bounded = directed._constrained_average_link_clusters(
            ids, evidence, threshold=.25, minimum_member_support=2,
            max_operations=directed.MAX_CLUSTER_OPERATIONS,
        )
        self.assertIn(ids, bounded)
        self.assertEqual(strict, [["cohort-a", "cohort-b", "cohort-c"], ["cohort-d"]])
        evidence.negatives["cohort-a"].add("cohort-c")
        evidence.negatives["cohort-c"].add("cohort-a")
        vetoed = directed._constrained_average_link_clusters(
            ids, evidence, threshold=.25, minimum_member_support=2,
            max_operations=directed.MAX_CLUSTER_OPERATIONS,
        )
        self.assertFalse(any({"cohort-a", "cohort-c"} <= set(cluster) for cluster in vetoed))
        evidence.source["cohort-a"].update(oldFolder="Sisters/A", oldPersonId="cast-a")
        evidence.source["cohort-d"].update(oldFolder="Sisters/D", oldPersonId="cast-d")
        self.assertTrue(directed._cohort_conflict(evidence, "cohort-a", "cohort-d"))

    def test_serialized_resume_never_restores_withdrawn_core_or_self_only_references(self):
        fixture = self.fixture()
        excluded = fixture[3]["Models/Model Source"][0]
        self.run_fixture(fixture, reference_exclusions={excluded})
        restored = self.fixture()
        restored_catalog = json.loads(json.dumps(fixture[2]))
        resumed_fixture = (*restored[:2], restored_catalog, *restored[3:])
        output, report = self.run_fixture(resumed_fixture, reference_exclusions={excluded})
        row = next(row for row in output if row["photoId"] == excluded)
        self.assertFalse(row["membership"]["coreUse"])
        self.assert_reference_exports(output, report, restored_catalog)

    def test_exact_cannot_link_inside_source_owner_cannot_hide_in_two_appearance_views(self):
        fixture = self.fixture()
        second_view = fixture[-1]("Angels/Angel Source", 8)
        first_view = fixture[3]["Angels/Angel Source"][:6]
        output, report = self.run_fixture(fixture, pairs=[
            {"photoIds": [first_view[0], second_view[0]], "label": "different"},
        ])
        angel = [row for row in output if row["oldFolder"] == "Angels/Angel Source"]
        self.assertTrue(all(not row["membership"]["coreUse"] for row in angel))
        self.assertTrue(all(row["source"] == row["destination"] for row in angel))
        self.assertTrue(any("contradicts shared source ownership" in item["reason"]
                            for item in report["initialReferenceValidation"]))
        self.assert_reference_exports(output, report, fixture[2])

    def test_original_backed_group_view_labels_quality_and_unavailable_references(self):
        from tools.art.likeness_library import group_views
        fixture = self.fixture()
        pair = fixture[-1]("Potentials/Small Source", 12, count=2)
        output, report = self.run_fixture(fixture)
        catalog = fixture[2]
        quality = next(row["photoId"] for row in output if row["membership"]["status"] == "quality-hold")
        self.assertIn("Quality hold", group_views.describe(catalog, quality)["label"])
        group_id = next(row["membership"]["groupId"] for row in output if row["photoId"] == pair[0])
        self.assertFalse(catalog["photoGroups"][group_id]["referencePhotoIds"])
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            generated = group_views.publish(catalog, [], root)
            page = generated[f"photo-groups/{group_id}/index.html"].decode()
            self.assertIn("reference unavailable in this appearance", page)
            self.assertIn("Missing, ambiguous, inconsistent, or unverified original", page)
        self.assert_reference_exports(output, report, catalog)

    def reconciliable(self, *, mixed=False):
        evidence = self.build(
            targets=[{"id": "angel-view", "folder": "Angels/Owner", "category": "Angels",
                      "personId": "angel-owner", "score": .8}],
        )
        lower, owner = evidence.views
        for v in evidence.views:
            pid = v["original"][0][:-1] + "4"
            v["original"].append(pid)
            v["frozenReferencePhotoIds"].append(pid)
            evidence.source[pid] = {
                "photoId": pid, "oldFolder": v["folder"], "oldPersonId": v["personId"],
                "membershipAssessment": {"own": {"appearanceId": v["appearanceId"],
                                                "frozenReferencePhotoIds": list(v["original"]),
                                                "frozenScore": .8}},
                "placementBlocks": [],
            }
            evidence.photos[pid] = {"photoId": pid, "preparedSHA256": "hash-" + pid}
            evidence.hashes[pid] = "hash-" + pid
            evidence.own_scores[pid] = .8
            evidence.scores_map[(pid, v["appearanceId"])] = .8
            evidence.vectors[pid] = np.asarray([1., 0.])
            evidence.eligible.add(pid)
        evidence.cache = FakeCache(set(evidence.source), evidence.pair_scores, evidence.duplicates)
        for members, refs, target in ((lower["original"], owner["original"], owner),
                                      (owner["original"], lower["original"], lower)):
            for pid in members:
                evidence.scores_map[(pid, target["appearanceId"])] = .8
                evidence.supports[pid] = {ref: .9 for ref in [*refs, *members] if ref != pid}
        if mixed:
            lower["original"].append("candidate")
            lower["frozenReferencePhotoIds"].append("candidate")
            evidence.scores_map[("candidate", "angel-view")] = .2
            evidence.supports["candidate"] = {}
        return evidence

    def test_duplicate_core_rival_is_removed_only_after_mutual_subset_evidence(self):
        evidence = self.reconciliable()
        before = self.row(directed.run_variant(evidence, self.recipe()), "src0")
        self.assertIsNone(before["candidateDestination"])
        after = directed.run_variant(evidence, self.recipe(), reconcile=True)
        self.assertEqual(len(after["viewReconciliation"]), 1)
        self.assertEqual(self.row(after)["candidateDestination"], "Angels/Owner")
        self.assertTrue(all(self.row(after, pid)["shadowAction"] == "supported-upward-appearance"
                            for pid in evidence.views[0]["original"]))
        self.assertEqual(evidence.views[0]["original"], ["src0", "src1", "src2", "src3", "src4"])

    def test_mixed_core_exception_is_not_transported_or_deleted(self):
        evidence = self.reconciliable(mixed=True)
        rebuilt, edges = directed.reconcile_views(evidence, self.recipe())
        self.assertEqual(edges[0]["exceptionPhotoIds"], ["candidate"])
        residual = next(v for v in rebuilt.views if v["appearanceId"] == "lower-id-view")
        self.assertEqual(residual["original"], ["candidate"])
        result = directed.run_variant(evidence, self.recipe(), reconcile=True)
        self.assertIsNone(self.row(result)["candidateDestination"])

    def test_mutual_subset_needs_four_independent_witnesses(self):
        evidence = self.reconciliable()
        evidence.duplicates.add(tuple(sorted(("src0", "src1"))))
        evidence.duplicates.add(tuple(sorted(("src2", "src3"))))
        _, edges = directed.reconcile_views(evidence, self.recipe())
        self.assertEqual(edges, [])

    def test_one_way_resemblance_never_coalesces_views(self):
        evidence = self.reconciliable()
        for pid in evidence.views[1]["original"]:
            evidence.supports[pid] = {}
        _, edges = directed.reconcile_views(evidence, self.recipe())
        self.assertEqual(edges, [])

    def test_reconciliation_preserves_distinct_cast_slots_and_exact_conflicts(self):
        evidence = self.reconciliable()
        evidence.views[0].update(category="Sisters", folder="Sisters/Other")
        _, edges = directed.reconcile_views(evidence, self.recipe())
        self.assertEqual(edges, [])
        evidence = self.reconciliable()
        evidence.negatives["src0"].add("angel-view-r0")
        evidence.negatives["angel-view-r0"].add("src0")
        _, edges = directed.reconcile_views(evidence, self.recipe())
        self.assertEqual(edges, [])

    def test_configured_identity_negative_blocks_canonical_reconciliation(self):
        evidence = self.reconciliable()
        evidence.configured_identity_negatives = {
            frozenset(view["personId"] for view in evidence.views),
        }
        _, edges = directed.reconcile_views(evidence, self.recipe())
        self.assertFalse(edges)
        result = directed.run_variant(evidence, self.recipe(), reconcile=True)
        self.assertFalse(result["viewReconciliation"])
        self.assertTrue(any("configured-different-identity-veto" in option["blockers"]
                            for option in self.row(result)["rivals"]))

    def test_anchor_neighbourhoods_do_not_union_bridges_or_bypass_duplicates_negatives_caps(self):
        evidence = self.reconciliable()
        left, right = [list(view["original"]) for view in evidence.views]
        for members in (left, right):
            for pid in members:
                evidence.supports[pid] = {other: .8 for other in members if other != pid}
        evidence.supports[left[0]][right[0]] = .8
        evidence.supports[right[0]][left[0]] = .8
        view = evidence.views[0]
        candidates = sorted(left + right)
        hypotheses = list(directed._anchor_reference_hypotheses(
            evidence, view, candidates, self.recipe()))
        self.assertEqual({frozenset(qualified) for qualified, _ in hypotheses},
                         {frozenset(left), frozenset(right)})
        evidence.negatives[left[0]].add(left[1])
        evidence.negatives[left[1]].add(left[0])
        evidence.duplicates.add(tuple(sorted(right[:2])))
        self.assertFalse(list(directed._anchor_reference_hypotheses(
            evidence, view, candidates, self.recipe())))
        with mock.patch.object(directed, "MAX_CLUSTER_OPERATIONS", 1):
            with self.assertRaisesRegex(ValueError, "operation cap"):
                list(directed._anchor_reference_hypotheses(
                    evidence, view, candidates, self.recipe()))

    def test_independent_anchor_reference_masks_match_exact_qualification_and_order(self):
        rng = np.random.default_rng(411)
        residual = rng.normal(size=(28, 63))
        residual /= np.linalg.norm(residual, axis=1)[:, None]
        vectors = {
            f"photo:{index:03d}": np.concatenate(([np.sqrt(.61)], np.sqrt(.39) * residual[index]))
            for index in range(len(residual))
        }
        evidence = MatrixEvidence(vectors)
        self.assertTrue(evidence.globally_independent)
        evidence.negatives["photo:000"].add("photo:001")
        evidence.negatives["photo:001"].add("photo:000")
        candidates = sorted(vectors)
        view_row = {"category": "Sisters"}
        recipe = directed.recipe_named("directed-corrective-starting-045")

        def exact_hypotheses(order):
            output, seen = [], set()
            for anchor in sorted(order):
                refs = sorted({anchor, *evidence.support(anchor, order, recipe["core"]["Sisters"])})
                signature = tuple(refs)
                if signature in seen or len(refs) <= recipe["coreSupport"]:
                    continue
                seen.add(signature)
                qualified, stable = evidence.qualify(view_row, refs, recipe)
                if stable and anchor in qualified:
                    output.append((qualified, refs))
            return output

        expected = exact_hypotheses(candidates)
        forward = list(directed._anchor_reference_hypotheses(
            evidence, view_row, candidates, recipe,
        ))
        reverse = list(directed._anchor_reference_hypotheses(
            evidence, view_row, list(reversed(candidates)), recipe,
        ))
        self.assertEqual(forward, expected)
        self.assertEqual(reverse, expected)

    def test_dense_independent_neighborhood_stress_stays_within_unchanged_cap(self):
        rng = np.random.default_rng(20261115)
        residual = rng.normal(size=(321, 127))
        residual /= np.linalg.norm(residual, axis=1)[:, None]
        vectors = {
            f"photo:{index:04d}": np.concatenate(([np.sqrt(.40)], np.sqrt(.60) * residual[index]))
            for index in range(len(residual))
        }
        evidence = MatrixEvidence(vectors)
        self.assertTrue(evidence.globally_independent)
        candidates = sorted(vectors)
        view_row = {"category": "Sisters"}
        recipe = directed.recipe_named("directed-corrective-starting-045")

        def legacy_bounded_producer():
            floor = recipe["core"]["Sisters"]
            operations = len(candidates) ** 2
            seen = set()
            for anchor in candidates:
                refs = sorted({anchor, *evidence.support(anchor, candidates, floor)})
                signature = tuple(refs)
                if signature in seen or len(refs) <= recipe["coreSupport"]:
                    continue
                seen.add(signature)
                operations += len(refs) ** 2
                if operations > directed.MAX_CLUSTER_OPERATIONS:
                    raise ValueError("directed reference-neighbourhood qualification cap exceeded")
                evidence.qualify(view_row, refs, recipe)

        original_qualify = evidence.qualify
        evidence.qualify = lambda _view, refs, _recipe: (list(refs), True)
        try:
            with self.assertRaisesRegex(ValueError, "qualification cap"):
                legacy_bounded_producer()
        finally:
            evidence.qualify = original_qualify

        stats = {}
        hypotheses = list(directed._anchor_reference_hypotheses(
            evidence, view_row, candidates, recipe, stats=stats,
        ))
        self.assertEqual(stats["mode"], "independent-reference-mask")
        self.assertGreater(stats["uniqueNeighborhoods"], 20)
        self.assertGreater(stats["legacyQuadraticOperations"], directed.MAX_CLUSTER_OPERATIONS)
        self.assertLessEqual(stats["operations"], directed.MAX_CLUSTER_OPERATIONS)
        self.assertEqual(len(hypotheses), stats["uniqueNeighborhoods"])
        self.assertTrue(all(qualified == cohort for qualified, cohort in hypotheses))

    def test_reconciliation_and_rival_scores_are_order_invariant(self):
        evidence = self.reconciliable()
        first = directed.run_variant(evidence, self.recipe(), reconcile=True)
        reverse = copy.deepcopy(evidence)
        reverse.views.reverse()
        reverse.source = dict(reversed(list(reverse.source.items())))
        second = directed.run_variant(reverse, self.recipe(), reconcile=True)
        self.assertEqual(directed._semantic(first), directed._semantic(second))

    def test_appearance_reference_core_is_not_certified_by_cross_support_alone(self):
        evidence = self.reconciliable()
        for v in evidence.views:
            for pid in v["original"]:
                for ref in v["original"]:
                    evidence.supports[pid].pop(ref, None)
        _, edges = directed.reconcile_views(evidence, self.recipe())
        self.assertEqual(edges, [])

    def test_full_outside_rival_margin_and_explicit_intent_prevent_union(self):
        evidence = self.reconciliable()
        outsider = copy.deepcopy(evidence.views[1])
        outsider.update(appearanceId="distinct-rival", personId="distinct-person", folder="Models/Rival")
        evidence.views.append(outsider)
        for pid in evidence.source:
            evidence.scores_map[(pid, "distinct-rival")] = .79
        _, edges = directed.reconcile_views(evidence, self.recipe())
        self.assertEqual(edges, [])
        evidence = self.reconciliable()
        evidence.views[0]["explicitIntent"] = True
        _, edges = directed.reconcile_views(evidence, self.recipe())
        self.assertEqual(edges, [])

    def test_reconciled_appearance_never_overrides_member_placement_lock(self):
        evidence = self.reconciliable()
        evidence.source["src0"]["placementBlocks"] = ["protected"]
        result = directed.run_variant(evidence, self.recipe(), reconcile=True)
        self.assertEqual(self.row(result, "src0")["shadowAction"], "physical-lock-preserved")
        self.assertIsNone(self.row(result, "src0")["candidateDestination"])
        self.assertEqual(len(result["viewReconciliation"]), 1)

    def test_reference_validation_withdraws_influence_not_source_placement_or_frozen_core(self):
        evidence = self.build(category="Angels", person="cast-a", own=.8, core=True, cast_score=.8)
        result = directed.run_variant(evidence, self.recipe(), reconcile=True)
        row = self.row(result)
        self.assertEqual(row["shadowAction"], "retain-in-place")
        self.assertTrue(row["strongInitialCastCoreDiagnostic"])
        self.assertEqual(row["frozenSourceScore"], .8)
        self.assertFalse(row["referenceUseEligible"])
        self.assertTrue(result["initialReferenceValidation"][0]["referenceUnavailable"])

    def test_pooled_hypothesis_is_not_a_named_destination(self):
        evidence = self.reconciliable()
        evidence.views[1]["pooled"] = True
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertIsNone(row["candidateDestination"])
        self.assertIn("unestablished-pooled-destination", row["rivals"][0]["blockers"])

    def test_qualified_same_rank_subset_uses_deterministic_owner_not_category_promotion(self):
        evidence = self.reconciliable()
        evidence.views[1].update(category="Prospects", folder="Prospects/A")
        for pid in evidence.views[1]["original"]:
            evidence.source[pid]["oldFolder"] = "Prospects/A"
        first = directed.run_variant(evidence, self.recipe(), reconcile=True)
        self.assertEqual(first["viewReconciliation"][0]["ownerFolder"], "Prospects/A")
        self.assertEqual(self.row(first, "src0")["shadowAction"], "supported-same-rank-appearance")
        self.assertEqual(self.row(first, "src0")["candidateDestination"], "Prospects/A")
        reverse = copy.deepcopy(evidence)
        reverse.views.reverse()
        self.assertEqual(directed._semantic(first), directed._semantic(
            directed.run_variant(reverse, self.recipe(), reconcile=True)))

    def test_joint_growth_cannot_withdraw_frozen_base_or_repeat_rejected_additions(self):
        evidence = self.reconciliable()
        base = {v["appearanceId"]: list(v["original"]) for v in evidence.views}
        staged = {"angel-view": ["candidate"]}
        rejected = set()
        with mock.patch.object(evidence, "qualify", return_value=(base["angel-view"][1:], True)):
            holds = directed.validate_growth(evidence, self.recipe(), base, staged, rejected, 2)
        self.assertEqual(staged["angel-view"], [])
        self.assertEqual(rejected, {("candidate", "angel-view")})
        self.assertFalse(holds[0]["physicalPlacementChanged"])
        self.assertEqual(base["angel-view"], evidence.views[1]["original"])

    def test_current_image_resolution_preserves_ids_rejects_ambiguity_and_stale_catalog(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            filename = "owner_image_7514005968487944619.jpg"
            pid = metadata.photo_id_from_name(filename)
            self.assertIsNotNone(pid)
            image = root / "Angels" / "Owner" / "gallery" / filename
            image.parent.mkdir(parents=True)
            image.write_bytes(b"test")
            source = {"rows": [{"photoId": pid, "oldFolder": "Models/Old"}]}
            run = {"workingRoot": str(root), "photos": [
                {"photoId": pid, "destination": "Models/Old/gallery/" + filename,
                 "preparedSHA256": "expected"},
            ]}
            catalog = root / ".likeness-library.json"
            catalog.write_text(json.dumps({"photos": {pid: {"contentSha256": "expected"}}}))
            item = directed.resolve_photo_locations(source, run)[pid]
            self.assertEqual(item["status"], "available")
            self.assertEqual(item["href"], image.as_uri())
            catalog.write_text(json.dumps({"photos": {pid: {"contentSha256": "changed"}}}))
            self.assertIsNone(directed.resolve_photo_locations(source, run)[pid]["href"])
            catalog.write_text(json.dumps({"photos": {pid: {"contentSha256": "expected"}}}))
            other = root / "Models" / "Other" / "gallery" / filename
            other.parent.mkdir(parents=True)
            other.write_bytes(b"test")
            self.assertEqual(directed.resolve_photo_locations(source, run)[pid]["status"],
                             "ambiguous-current-photo-id")

    def recipe(self):
        return copy.deepcopy(directed.recipes()[0])

    def build(self, *, category="Prospects", person="lower-id", folder=None, own=.7,
              core=False, cast_score=None, blocks=(), targets=None, supports=None,
              labels=(), duplicates=(), pair_scores=None, stage_scores=None):
        folder = folder or f"{category}/Source"
        refs = [f"src{i}" for i in range(4)]
        target_views = []
        scores = {}
        support_map = defaultdict(dict)
        own_scores = {}
        identities = {}
        for i, pid in enumerate(refs):
            identities[pid] = {"folder": folder, "personId": person, "refs": refs,
                               "ownView": f"{person}-view"}
            own_scores[pid] = .8
        target_views.append(view(folder, category, person, f"{person}-view", refs))
        target_specs = targets or []
        all_target_refs = {}
        for spec in target_specs:
            target_refs = [f'{spec["id"]}-r{i}' for i in range(4)]
            target_views.append(view(spec["folder"], spec["category"], spec["personId"],
                                     spec["id"], target_refs))
            all_target_refs[spec["id"]] = target_refs
            for ref in target_refs:
                identities[ref] = {
                    "folder": spec["folder"], "personId": spec["personId"], "refs": target_refs,
                    "ownView": spec["id"],
                }
                own_scores[ref] = .8
        for spec in target_specs:
            for pid in spec.get("members", ["candidate"]):
                if pid not in identities:
                    identities[pid] = {
                        "folder": folder, "personId": person,
                        "refs": refs, "ownView": f"{person}-view",
                        "blocks": list(blocks) if pid == "candidate" else [],
                        "core": core if pid == "candidate" else False,
                        "castScore": cast_score if pid == "candidate" else None,
                    }
                    own_scores[pid] = own if pid == "candidate" else .7
                scores[(pid, spec["id"])] = spec.get("score", .8)
                for ref in all_target_refs[spec["id"]]:
                    support_map[pid][ref] = spec.get("supportScore", .9)
        if "candidate" not in identities:
            identities["candidate"] = {
                "folder": folder, "personId": person, "refs": refs,
                "ownView": f"{person}-view", "blocks": list(blocks),
                "core": core, "castScore": cast_score,
            }
            own_scores["candidate"] = own
        for pid, value in (supports or {}).items():
            support_map[pid].update(value)
        # A source view score is also a full rival witness for signed margins.
        for pid in identities:
            scores.setdefault((pid, f"{person}-view"), own_scores.get(pid, .7))
        return FakeEvidence(
            identities=identities, views=target_views, scores=scores, supports=support_map,
            own_scores=own_scores, labels=labels, duplicates=duplicates,
            pair_scores=pair_scores, stage_scores=stage_scores,
        )

    def row(self, result, pid="candidate"):
        return next(row for row in result["rows"] if row["photoId"] == pid)

    def test_cast_core_stays_when_rival_is_tentative_and_reference_can_withdraw(self):
        evidence = self.build(
            category="Angels", person="cast-a", own=.1, core=True, cast_score=.8,
            targets=[{"id": "model-view", "folder": "Models/B", "category": "Models",
                      "personId": "model-b", "score": .55, "supportScore": .3}],
        )
        result = directed.run_variant(evidence, self.recipe())
        row = self.row(result)
        self.assertEqual(row["shadowAction"], "retain-in-place")
        self.assertTrue(row["strongInitialCastCoreDiagnostic"])
        self.assertFalse(row["referenceUseEligible"])
        self.assertTrue(row["tentativeAssociations"])
        self.assertIsNone(row["candidateDestination"])
        tentative = next(group for group in result["clusters"] if group["state"] == "tentative")
        self.assertTrue(tentative["physicalHomeRemainsSource"])
        self.assertEqual(tentative["referenceAuthority"], "none; reference recovery is separately staged and evidenced")

    def test_missing_own_core_support_does_not_release_to_rival(self):
        evidence = self.build(
            category="Angels", person="cast-a", own=.8, core=True, cast_score=.8,
            supports={"candidate": {"src0": .9}},
            targets=[{"id": "model-view", "folder": "Models/B", "category": "Models",
                      "personId": "model-b", "score": .8}],
            duplicates=[("src0", "src1"), ("src2", "src3")],
        )
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertEqual(row["shadowAction"], "retain-in-place")
        self.assertEqual(row["referenceUseDisposition"],
                         "withdrawn-or-unqualified-independent-of-placement")
        self.assertFalse(row["sourceIncompatibility"]["qualified"])

    def test_unmeasured_cast_member_is_held_without_scoring_missing_vector(self):
        evidence = self.build(category="Angels", person="cast-a", own=.8)
        del evidence.vectors["candidate"]
        del evidence.cache.indices["candidate"]
        evidence.cache.indices = {
            pid: index for index, pid in enumerate(sorted(evidence.cache.indices))
        }
        evidence.eligible.discard("candidate")
        original_support = evidence.support

        def support(pid, refs, floor):
            self.assertIn(pid, evidence.cache.indices)
            return original_support(pid, refs, floor)

        evidence.support = support
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertEqual(row["shadowAction"], "retain-in-place")
        self.assertEqual(row["membershipState"], "uncertain-retained-in-place")
        self.assertIsNone(row["candidateDestination"])
        self.assertFalse(row["referenceUseEligible"])

    def test_individually_supported_lower_candidate_flows_up_after_identity_evidence(self):
        evidence = self.build(
            targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                      "personId": "model-owner", "score": .8}],
        )
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertEqual(row["shadowAction"], "supported-upward-appearance")
        self.assertEqual(row["candidateDestination"], "Models/Owner")
        self.assertEqual(row["supportedAssociation"]["canonicalOwnerFolder"], "Models/Owner")
        self.assertEqual(row["supportedAssociation"]["relationshipStatus"],
                         "individually-supported-same-identity")

    def test_incoming_various_requires_qualified_destination_and_full_margin(self):
        for score, expected in ((.8, "supported-upward-appearance"), (.3, "retain-in-place")):
            with self.subTest(score=score):
                evidence = self.build(
                    targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                              "personId": "model-owner", "score": score}])
                source = evidence.source["candidate"]
                source.update(oldFolder="Various", oldPersonId=None)
                source["membershipAssessment"] = {"own": {}}
                evidence.own_scores["candidate"] = None
                evidence.scores_map[("candidate", "lower-id-view")] = .1
                row = self.row(directed.run_variant(evidence, self.recipe()))
                self.assertEqual(row["shadowAction"], expected)
                self.assertEqual(row["candidateDestination"],
                                 "Models/Owner" if score == .8 else None)

    def test_close_distinct_rival_is_kept_and_not_collapsed_by_shared_references(self):
        evidence = self.build(
            category="Angels", person="cast-a", own=.8, core=True, cast_score=.8,
            targets=[
                {"id": "rival-a", "folder": "Models/A", "category": "Models", "personId": "rival-a",
                 "score": .58, "supportScore": .3},
                {"id": "rival-b", "folder": "Models/B", "category": "Models", "personId": "rival-b",
                 "score": .57, "supportScore": .3},
            ],
        )
        evidence.views[2]["original"] = list(evidence.views[1]["original"])
        evidence.views[2]["frozenReferencePhotoIds"] = list(evidence.views[1]["original"])
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertEqual(row["shadowAction"], "retain-in-place")
        self.assertEqual({r["personId"] for r in row["rivals"]} & {"rival-a", "rival-b"},
                         {"rival-a", "rival-b"})
        rival_rows = [item for item in row["rivals"] if item["personId"] in ("rival-a", "rival-b")]
        self.assertEqual(rival_rows[0]["sharedOriginalReferencePhotoIds"],
                         rival_rows[1]["sharedOriginalReferencePhotoIds"])

    def test_contaminant_does_not_join_supported_cluster_wholesale(self):
        evidence = self.build(
            targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                      "personId": "model-owner", "score": .8, "members": ["candidate", "weak", "conflict"]}],
        )
        evidence.scores_map[("weak", "model-view")] = .2
        evidence.supports["weak"] = {}
        evidence.scores_map[("conflict", "model-view")] = .8
        evidence.supports["conflict"] = {ref: .9 for ref in evidence.views[1]["original"]}
        evidence.labels.append({"photoIds": ["conflict", "model-view-r0"], "label": "uncertain"})
        evidence.negatives["conflict"].add("model-view-r0")
        evidence.negatives["model-view-r0"].add("conflict")
        result = directed.run_variant(evidence, self.recipe())
        group = next(group for group in result["clusters"]
                     if group["state"] == "supported" and group["candidateParentId"] == "model-owner")
        self.assertEqual(group["memberPhotoIds"], ["candidate"])
        self.assertNotIn("weak", group["memberPhotoIds"])
        self.assertNotIn("conflict", group["memberPhotoIds"])

    def test_same_rank_ties_are_deterministic_and_do_not_create_an_owner(self):
        evidence = self.build(
            targets=[
                {"id": "model-b", "folder": "Models/B", "category": "Models", "personId": "model-b",
                 "score": .8},
                {"id": "model-c", "folder": "Models/C", "category": "Models", "personId": "model-c",
                 "score": .8},
            ],
        )
        recipe = self.recipe()
        first = directed.run_variant(evidence, recipe)
        reverse = copy.deepcopy(evidence)
        reverse.views.reverse()
        reverse.source = dict(reversed(list(reverse.source.items())))
        second = directed.run_variant(reverse, recipe)
        self.assertEqual(directed._semantic(first), directed._semantic(second))
        row = self.row(first)
        self.assertEqual(row["shadowAction"], "retain-in-place")
        self.assertEqual([o["appearanceId"] for o in row["tentativeAssociations"]],
                         sorted(o["appearanceId"] for o in row["tentativeAssociations"]))

    def test_distinct_authored_cast_slots_are_never_consolidated(self):
        evidence = self.build(
            category="Angels", person="angel-a", own=.8, core=True, cast_score=.8,
            targets=[{"id": "sister-view", "folder": "Sisters/B", "category": "Sisters",
                      "personId": "sister-b", "score": .9}],
        )
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertIsNone(row["candidateDestination"])
        rival = next(item for item in row["rivals"] if item["personId"] == "sister-b")
        self.assertIn("distinct-authored-cast-slot", rival["blockers"])

    def test_group_protection_does_not_lock_each_member(self):
        evidence = self.build(
            targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                      "personId": "model-owner", "score": .8}],
        )
        evidence.source["candidate"]["placementBlocks"] = ["identityProtected"]
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertEqual(row["shadowAction"], "supported-upward-appearance")
        self.assertEqual(row["placementBlocks"], [])
        self.assertEqual(row["groupProtectionMetadata"], ["identityProtected"])

    def test_reference_withdrawal_does_not_rewrite_initial_core_or_placement(self):
        evidence = self.build(
            category="Angels", person="cast-a", own=.1, core=True, cast_score=.8,
            targets=[{"id": "model-view", "folder": "Models/B", "category": "Models",
                      "personId": "model-b", "score": .7}],
        )
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertEqual(row["frozenSourceScore"], .8)
        self.assertEqual(row["currentOwnScore"], .1)
        self.assertTrue(row["strongInitialCastCoreDiagnostic"])
        self.assertFalse(row["referenceUseEligible"])
        self.assertEqual(row["shadowAction"], "retain-in-place")

    def test_strong_downward_correction_requires_source_and_destination_and_margin(self):
        evidence = self.build(
            category="Sisters", person="sister-a", own=.2, core=True, cast_score=.2,
            targets=[{"id": "model-view", "folder": "Models/B", "category": "Models",
                      "personId": "model-b", "score": .85}],
        )
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertEqual(row["shadowAction"], "strong-wrong-identity-correction")
        self.assertEqual(row["candidateDestination"], "Models/B")
        self.assertTrue(row["sourceIncompatibility"]["qualified"])
        self.assertGreaterEqual(
            row["correctionAssociation"]["signedDistinctRivalMargin"], .30,
        )
        no_support = self.build(
            category="Sisters", person="sister-a", own=.2, core=True, cast_score=.2,
            targets=[{"id": "model-view", "folder": "Models/B", "category": "Models",
                      "personId": "model-b", "score": .85, "supportScore": .1}],
        )
        self.assertNotEqual(self.row(directed.run_variant(no_support, self.recipe()))["shadowAction"],
                            "strong-wrong-identity-correction")

    def test_source_score_above_evidence_floor_cannot_trigger_release_or_new_owner_evaluation(self):
        evidence = self.build(
            category="Sisters", person="sister-a", own=.369, core=True, cast_score=.369,
            targets=[{"id": "model-view", "folder": "Models/B", "category": "Models",
                      "personId": "model-b", "score": .85}],
        )
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertFalse(row["sourceIncompatibility"]["qualified"])
        self.assertEqual(row["shadowAction"], "retain-in-place")
        self.assertNotIn("sourceIncompatibleCohortEvidence", row)
        self.assertIsNone(row["candidateDestination"])

    def test_strong_release_requires_stricter_signed_margin(self):
        evidence = self.build(
            category="Sisters", person="sister-a", own=.7, core=True, cast_score=.2,
            targets=[{"id": "model-view", "folder": "Models/B", "category": "Models",
                      "personId": "model-b", "score": .85}],
        )
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertTrue(row["sourceIncompatibility"]["qualified"])
        self.assertIsNone(row["correctionAssociation"])
        self.assertNotEqual(row["shadowAction"], "strong-wrong-identity-correction")

    def test_corrective_release_uses_qualified_category_floor_and_margin(self):
        recipe = directed.recipe_named("directed-corrective-starting-050")
        self.assertEqual(recipe["strongRelease"], {
            "sourceMaximum": .30, "destinationGate": "qualified-category",
        })
        evidence = self.build(
            category="Models", person="model-a", own=.2,
            targets=[
                {"id": "model-b", "folder": "Models/B", "category": "Models",
                 "personId": "model-b", "score": .45},
                {"id": "model-c", "folder": "Models/C", "category": "Models",
                 "personId": "model-c", "score": .34},
            ],
        )
        row = self.row(directed.run_variant(evidence, recipe))
        correction = row["correctionAssociation"]
        self.assertEqual(row["shadowAction"], "strong-wrong-identity-correction")
        self.assertEqual(correction["folder"], "Models/B")
        self.assertGreaterEqual(
            len(row["sourceIncompatibility"]["independentSourceReferenceIds"]), 2,
        )
        self.assertLess(correction["score"], .60)
        self.assertLess(correction["signedDistinctRivalMargin"], .30)
        self.assertGreaterEqual(
            correction["score"], recipe["admission"]["Models"],
        )
        self.assertGreaterEqual(
            correction["signedDistinctRivalMargin"], recipe["sameIdentityMargin"]["Models"],
        )
        self.assertGreaterEqual(len(correction["independentSupportPhotoIds"]), recipe["joinSupport"])

    def test_corrective_release_rejects_ambiguous_two_support_locked_and_negative_targets(self):
        recipe = directed.recipe_named("directed-corrective-starting-050")
        target = {"id": "model-b", "folder": "Models/B", "category": "Models",
                  "personId": "model-b", "score": .45}

        two_support = self.build(
            category="Models", person="model-a", own=.2, targets=[target],
            supports={"candidate": {
                "model-b-r0": .9, "model-b-r1": .9,
                "model-b-r2": .1, "model-b-r3": .1,
            }},
        )
        self.assertNotEqual(
            self.row(directed.run_variant(two_support, recipe))["shadowAction"],
            "strong-wrong-identity-correction",
        )

        ambiguous = self.build(
            category="Models", person="model-a", own=.2,
            targets=[
                target,
                {"id": "model-c", "folder": "Models/C", "category": "Models",
                 "personId": "model-c", "score": .40},
            ],
        )
        self.assertNotEqual(
            self.row(directed.run_variant(ambiguous, recipe))["shadowAction"],
            "strong-wrong-identity-correction",
        )

        locked = self.build(
            category="Models", person="model-a", own=.2, blocks=("protected",),
            targets=[target],
        )
        self.assertEqual(
            self.row(directed.run_variant(locked, recipe))["shadowAction"],
            "physical-lock-preserved",
        )

        negative = self.build(
            category="Models", person="model-a", own=.2, targets=[target],
            labels=[{"photoIds": ["candidate", "model-b-r0"], "label": "different"}],
        )
        self.assertNotEqual(
            self.row(directed.run_variant(negative, recipe))["shadowAction"],
            "strong-wrong-identity-correction",
        )

    def test_corrective_release_never_uses_missing_source_score_alone(self):
        recipe = directed.recipe_named("directed-corrective-starting-050")
        evidence = self.build(
            category="Models", person="model-a", own=None,
            targets=[{"id": "model-b", "folder": "Models/B", "category": "Models",
                      "personId": "model-b", "score": .45}],
        )
        row = self.row(directed.run_variant(evidence, recipe))
        self.assertIsNone(row["sourceIncompatibility"]["frozenSourceScore"])
        self.assertFalse(row["sourceIncompatibility"]["qualified"])
        self.assertNotEqual(row["shadowAction"], "strong-wrong-identity-correction")

    def test_corrective_release_accepts_exact_different_source_evidence(self):
        recipe = directed.recipe_named("directed-corrective-starting-050")
        evidence = self.build(
            category="Models", person="model-a", own=.7,
            targets=[
                {"id": "model-b", "folder": "Models/B", "category": "Models",
                 "personId": "model-b", "score": .85},
                {"id": "model-c", "folder": "Models/C", "category": "Models",
                 "personId": "model-c", "score": .34},
            ],
            labels=[{"photoIds": ["candidate", "src0"], "label": "different"}],
        )
        row = self.row(directed.run_variant(evidence, recipe))
        self.assertEqual(row["sourceIncompatibility"]["basis"], "exact human different-pair")
        self.assertEqual(row["shadowAction"], "strong-wrong-identity-correction")
        self.assertEqual(row["correctionAssociation"]["folder"], "Models/B")

    def test_exact_different_and_uncertain_pair_veto_association(self):
        for label in ("different", "uncertain"):
            evidence = self.build(
                targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                          "personId": "model-owner", "score": .8}],
                labels=[{"photoIds": ["candidate", "model-view-r0"], "label": label}],
            )
            row = self.row(directed.run_variant(evidence, self.recipe()))
            self.assertNotEqual(row["shadowAction"], "supported-upward-appearance")
            option = next(item for item in row["rivals"] if item["personId"] == "model-owner")
            self.assertTrue(option["veto"])
            self.assertEqual(row["fictionalFamilyAssessment"]["eligible"], label == "different")

    def test_hard_placement_lock_blocks_even_qualified_strong_release(self):
        evidence = self.build(
            category="Sisters", person="sister-a", own=.2, core=True, cast_score=.2,
            blocks=("protected",),
            targets=[{"id": "model-view", "folder": "Models/B", "category": "Models",
                      "personId": "model-b", "score": .85}],
        )
        row = self.row(directed.run_variant(evidence, self.recipe()))
        self.assertEqual(row["shadowAction"], "physical-lock-preserved")
        self.assertIsNone(row["candidateDestination"])

    def test_near_duplicate_support_cannot_qualify_destination(self):
        duplicate_refs = [("model-view-r0", "model-view-r1")]
        evidence = self.build(
            targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                      "personId": "model-owner", "score": .8}],
            duplicates=duplicate_refs,
        )
        row = self.row(directed.run_variant(evidence, self.recipe()))
        option = next(item for item in row["rivals"] if item["personId"] == "model-owner")
        self.assertLess(len(option["independentSupportPhotoIds"]), self.recipe()["joinSupport"])
        self.assertNotEqual(row["shadowAction"], "supported-upward-appearance")

    def test_staged_reference_recovery_converges_without_chain_certification(self):
        evidence = self.build(
            targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                      "personId": "model-owner", "score": .9, "members": ["candidate", "later"]}],
            stage_scores={
                "candidate": {"__score__": .9},
                "later": {"__score__": .9, "__trigger__": "candidate", "model-view-r0": .9},
            },
        )
        evidence.scores_map[("later", "model-view")] = .2
        evidence.supports["later"] = {}
        evidence.stage_scores["later"].update({
            ref: .9 for ref in evidence.views[1]["original"]
        })
        result = directed.run_variant(evidence, self.recipe())
        recovery = next(item for item in result["referenceRecovery"]
                        if item["appearanceId"] == "model-view")
        self.assertEqual(recovery["stagedReferencePhotoIds"], ["candidate"])
        later = self.row(result, "later")
        self.assertIn("no-independent-original-boundary-support",
                      next(item for item in later["rivals"] if item["personId"] == "model-owner")["blockers"])
        self.assertFalse(later["stagedReferenceCandidates"])
        self.assertEqual(result["summary"]["referenceBoundaries"], 3)
        self.assertEqual(result["recoveryBoundaries"][-1]["addedPhotoIds"], [])
        snapshots = {
            stage["id"]: directed.unpack_boundary_snapshot(stage)
            for stage in result["boundarySnapshots"]
        }
        self.assertNotIn("candidate", snapshots["membership"]["referenceInventory"]["model-view"])
        self.assertIn("candidate", snapshots["growth-1"]["referenceInventory"]["model-view"])
        self.assertNotEqual(snapshots["membership"]["referenceInventory"],
                            snapshots["growth-1"]["referenceInventory"])
        before = copy.deepcopy(snapshots["membership"])
        evidence.views[1]["original"].clear()
        self.assertEqual(snapshots["membership"], before)

    def test_two_core_witnesses_cannot_stage_member_below_admission_join_support(self):
        evidence = self.build(
            category="Potentials", person="lower-id", own=.1,
            targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                      "personId": "model-owner", "score": .55}],
            supports={"candidate": {
                "model-view-r0": .9, "model-view-r1": .9,
                "model-view-r2": .1, "model-view-r3": .1,
            }},
        )
        result = directed.run_variant(evidence, self.recipe())
        recovery = next(item for item in result["referenceRecovery"]
                        if item["appearanceId"] == "model-view")
        self.assertEqual(recovery["stagedReferencePhotoIds"], [])
        row = self.row(result)
        rival = next(item for item in row["rivals"] if item["appearanceId"] == "model-view")
        self.assertGreaterEqual(rival["score"], self.recipe()["core"]["Models"])
        self.assertEqual(len(rival["independentSupportPhotoIds"]), 2)
        self.assertIn("insufficient-independent-member-support", rival["blockers"])
        self.assertFalse(row["stagedReferenceCandidates"])

    def test_nonqualifying_appearance_remains_rival_beside_admitted_view(self):
        evidence = self.build(
            category="Potentials", person="lower-id", own=.7,
            targets=[
                {"id": "model-a", "folder": "Models/A", "category": "Models",
                 "personId": "model-a", "score": .9},
                {"id": "model-b", "folder": "Models/B", "category": "Models",
                 "personId": "model-b", "score": .39},
            ],
        )
        result = directed.run_variant(evidence, self.recipe())
        recovery_a = next(item for item in result["referenceRecovery"]
                          if item["appearanceId"] == "model-a")
        recovery_b = next(item for item in result["referenceRecovery"]
                          if item["appearanceId"] == "model-b")
        self.assertEqual(recovery_a["stagedReferencePhotoIds"], ["candidate"])
        self.assertEqual(recovery_b["stagedReferencePhotoIds"], [])
        row = self.row(result)
        self.assertEqual(row["supportedAssociation"]["appearanceId"], "model-a")
        rival_b = next(item for item in row["rivals"] if item["appearanceId"] == "model-b")
        self.assertIn("below-admission-floor", rival_b["blockers"])
        self.assertFalse(rival_b["individuallyQualified"])

    def test_order_repeat_and_population_conservation(self):
        evidence = self.build(
            targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                      "personId": "model-owner", "score": .8}],
        )
        recipe = self.recipe()
        first = directed.run_variant(evidence, recipe)
        repeated = directed.run_variant(evidence, recipe)
        reverse = copy.deepcopy(evidence)
        reverse.views.reverse()
        reverse.source = dict(reversed(list(reverse.source.items())))
        reversed_result = directed.run_variant(reverse, recipe)
        self.assertEqual(directed._semantic(first), directed._semantic(repeated))
        self.assertEqual(directed._semantic(first), directed._semantic(reversed_result))
        self.assertEqual({row["photoId"] for row in first["rows"]}, set(evidence.source))
        self.assertTrue(all(row["clusterIds"] for row in first["rows"]))
        corrective = directed.recipe_named("directed-corrective-starting-050")
        corrected = directed.run_variant(evidence, corrective)
        corrected_repeat = directed.run_variant(evidence, corrective)
        corrected_reverse = copy.deepcopy(evidence)
        corrected_reverse.views.reverse()
        corrected_reverse.source = dict(reversed(list(corrected_reverse.source.items())))
        corrected_reversed_result = directed.run_variant(corrected_reverse, corrective)
        self.assertEqual(directed._semantic(corrected), directed._semantic(corrected_repeat))
        self.assertEqual(directed._semantic(corrected), directed._semantic(corrected_reversed_result))

    def test_report_compaction_preserves_rivals_support_and_conflicts(self):
        evidence = self.build(
            targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                      "personId": "model-owner", "score": .8}],
            labels=[{"photoIds": ["candidate", "model-view-r0"], "label": "different"}],
        )
        full = directed.run_variant(evidence, self.recipe())
        compact = directed.compact_for_report({
            "kind": "directed-reformation-shadow",
            "control": {"populationCount": len(full["rows"])},
            "variants": [full],
        })
        full_row = self.row(full)
        compact_row = self.row(compact["variants"][0])
        full_rival = next(item for item in full_row["rivals"] if item["appearanceId"] == "model-view")
        compact_rival = next(item for item in compact_row["rivals"] if item["appearanceId"] == "model-view")
        self.assertEqual(len(compact_row["rivals"]), len(full_row["rivals"]))
        self.assertEqual(compact_rival["exactConflicts"], full_rival["exactConflicts"])
        self.assertEqual(
            compact_rival["independentSupportPhotoIds"], full_rival["independentSupportPhotoIds"],
        )
        self.assertEqual(
            compact_rival["sharedOriginalReferenceCount"],
            len(full_rival["sharedOriginalReferencePhotoIds"]),
        )
        self.assertEqual(compact_rival["referencePhotoCount"], len(full_rival["referencePhotoIds"]))
        self.assertNotIn("referencePhotoIds", compact_rival)
        self.assertEqual(
            compact_row["tentativeAssociations"],
            [option["appearanceId"] for option in full_row["tentativeAssociations"]],
        )

    def test_launcher_preview_apply_repeat_check_and_source_output_tamper(self):
        evidence = self.build(
            targets=[{"id": "model-view", "folder": "Models/Owner", "category": "Models",
                      "personId": "model-owner", "score": .8}],
        )
        variant = directed.run_variant(evidence, self.recipe())
        report = {
            "control": {"name": "current ordered-middle control", "populationCount": len(variant["rows"]),
                        "proposalCount": 0, "logicalReleases": 0, "changedSourceDestinations": 0},
            "variants": [variant], "verification": {"reverseOrderVerified": True},
        }
        with tempfile.TemporaryDirectory(dir=cli.ROOT / "tmp") as name:
            root = pathlib.Path(name)
            source, out = root / "source", root / "report"
            source.mkdir()
            source_file = source / "saved-evidence.json"
            source_file.write_text('{"saved":true}\n', encoding="utf-8")
            bindings = {str(source_file): shadow.digest(source_file)}
            loaded = (
                {"rows": [{"photoId": "candidate"}]},
                {"photos": [{"photoId": "candidate", "destination": "missing/candidate.jpg"}],
                 "workingRoot": str(root)}, {}, [], bindings,
                {"historicalImplementationDrift": []},
            )
            args = ["--source", str(source), "--out", str(out), "--directed"]
            with mock.patch.object(cli, "output_path", side_effect=lambda path: path), \
                    mock.patch.object(directed, "load_saved_source", return_value=loaded), \
                    mock.patch.object(directed, "run_sweep", return_value=report):
                self.assertEqual(cli.main(args + ["--dry-run"]), 0)
                self.assertFalse(out.exists())
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                receipt = json.loads((out / "receipt.json").read_bytes())
                self.assertTrue(receipt["reverseVerified"])
                self.assertEqual(receipt["installedMoves"], 0)
                detail_path = out / "directed-details.json.gz"
                details = json.loads(gzip.decompress(detail_path.read_bytes()))
                self.assertEqual(
                    len(details["variants"][0]["rows"][0]["rivals"]),
                    len(variant["rows"][0]["rivals"]),
                )
                page = json.loads((out / "directed.json").read_bytes())
                self.assertNotIn("rivals", page["variants"][0]["rows"][0])
                self.assertEqual(page["imageAvailability"]["destinationCount"], 1)
                self.assertEqual(page["imageAvailability"]["missingOrUnsafePhotoIds"], ["candidate"])
                self.assertIn("pageSize=24", (out / "index.html").read_text(encoding="utf-8"))
                self.assertIn('id="cards" class="cards"></div>', (out / "index.html").read_text(encoding="utf-8"))
                self.assertIn('id="source"', (out / "index.html").read_text(encoding="utf-8"))
                self.assertIn("table-layout:fixed", (out / "index.html").read_text(encoding="utf-8"))
                self.assertEqual(cli.main(args + ["--check"]), 0)
                self.assertEqual(cli.main(args + ["--apply"]), 0)
                source_file.write_text('{"saved":false}\n', encoding="utf-8")
                self.assertEqual(cli.main(args + ["--check"]), 2)
                source_file.write_text('{"saved":true}\n', encoding="utf-8")
                output = out / "directed.json"
                original = output.read_bytes()
                output.write_bytes(b"tampered")
                self.assertEqual(cli.main(args + ["--check"]), 2)
                output.write_bytes(original)
                original_details = detail_path.read_bytes()
                detail_path.write_bytes(b"tampered")
                self.assertEqual(cli.main(args + ["--check"]), 2)
                detail_path.write_bytes(original_details)
                self.assertEqual(cli.main(args + ["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
