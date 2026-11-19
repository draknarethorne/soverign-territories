import contextlib
import hashlib
import io
import json
import pathlib
import re
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from tools.art.likeness_library import metadata, rebase_manifest


ROOT = pathlib.Path(__file__).resolve().parents[4]
SCRATCH = ROOT / "tmp" / "normal-flow-restoration"


class RebaseManifestTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.root = pathlib.Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def write(path, content=b"test source"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def public_measurement_report(self, run_id):
        from tools.art import likeness as api

        production = self.root / "Production"
        working = self.root / "Working"
        source = self.write(
            production / "Angels" / "A" / "gallery" / "photo_1.jpg",
            b"bounded fixture image bytes",
        )
        working.mkdir(parents=True, exist_ok=True)
        cache_path, _cache = rebase_manifest._settings_and_cache(working)
        source_sha, cache_key_sha1, size = rebase_manifest._hash_source(source)
        row = {
            "rowId": rebase_manifest._row_id({
                "origin": "Production",
                "sourcePath": "Angels/A/gallery/photo_1.jpg",
                "sourceSha256": source_sha,
            }),
            "origin": "Production",
            "sourceRoot": str(production),
            "sourcePath": "Angels/A/gallery/photo_1.jpg",
            "absolutePath": str(source),
            "sourceSha256": source_sha,
            "cacheKeySha1": cache_key_sha1,
            "byteLength": size,
            "photoId": "photo:photo_1",
            "category": "Angels",
            "ownerFolder": "Angels/A",
            "bucket": "Gallery",
            "sourceName": "A",
            "workingCurrentOwner": "Angels/A",
            "workingCurrentName": "A",
            "scopeIntegrity": "unique",
            "canonical": True,
            "role": "hold",
            "proposedRole": "reference-or-noncore-gallery-candidate",
            "roleReason": "awaiting source-bound measurement",
            "measurementReady": False,
            "measurement": {
                "status": "needs-source-bound-measurement",
                "cacheKeySha1": cache_key_sha1,
                "sourceSha256": source_sha,
                "data": None,
            },
            "decisions": {
                "truePhotoLock": {"locked": False, "origin": None},
                "workflowSelected": False,
                "configuredIdentityAnchor": [],
                "sandboxIdentityAnchors": [],
                "sandboxActionHistory": [],
                "sandboxProtection": None,
                "sandboxRejections": None,
                "sandboxMembership": None,
            },
            "reviewFlags": [],
        }
        row.pop("absolutePath")
        manifest = {
            "runId": run_id,
            "status": "manifest proposal; human review required",
            "roots": {"production": str(production), "sandboxWorking": str(working)},
            "configuration": {
                "cachePath": str(cache_path),
                "cacheSha256": None,
                "models": [],
            },
            "sourceMetadata": {"metadataFiles": {}, "identityNames": {}},
            "implementationHashes": rebase_manifest._implementation_hashes(),
            "sourceInventory": {
                "sourceHashComplete": True,
                "scopeIntegrityComplete": True,
                "scopeIssues": [],
                "collisions": {},
            },
            "coreProposal": {
                "centeringMeanSha256": None,
                "qualifiedCores": {},
                "diagnostics": [],
            },
            "rows": [row],
            "sourceMeasurementStatus": {},
            "measurementPlan": {"currentWorkingIdentityGalleryRows": 1},
        }
        report_root = working / "_reports" / "library" / "rebase-manifests" / run_id
        payload = json.dumps(rebase_manifest._public_manifest(manifest), indent=2).encode("utf-8")
        rebase_manifest._write_report(manifest, payload, rebase_manifest._csv_bytes([row]), report_root)
        return api, production, working, source, manifest, report_root

    @staticmethod
    def row(origin, source_path, photo_id, checksum, category="Angels", bucket="Gallery", owner=None):
        owner = owner or f"{category}/A"
        return {
            "origin": origin,
            "sourceRoot": "root",
            "sourcePath": source_path,
            "photoId": photo_id,
            "sourceSha256": checksum,
            "category": category,
            "ownerFolder": owner,
            "bucket": bucket,
        }

    def test_scan_is_category_scoped_and_excludes_archive_artists_and_nested_files(self):
        root = self.root / "library"
        self.write(root / "Angels" / "A" / "gallery" / "photo_1.jpg")
        self.write(root / "Angels" / "_archive" / "A" / "gallery" / "old_2.jpg")
        self.write(root / "Various" / "review" / "loose_3.png")
        self.write(root / "Artists" / "B" / "gallery" / "artist_4.jpg")
        self.write(root / "Angels" / "A" / "gallery" / "nested" / "ignored_5.jpg")

        rows, issues, missing = rebase_manifest._scan_root(root, "Production")
        artists = rebase_manifest._count_excluded_artists(root)

        self.assertEqual(
            {(row["sourcePath"], row["category"], row["bucket"]) for row in rows},
            {
                ("Angels/A/gallery/photo_1.jpg", "Angels", "Gallery"),
                ("Various/review/loose_3.png", "Various", "Pool"),
            },
        )
        self.assertEqual(issues, [])
        self.assertNotIn("Angels", missing)
        self.assertNotIn("Various", missing)
        self.assertEqual(artists["files"], 1)
        self.assertEqual(artists["byBucket"]["Gallery"], 1)

    def test_exact_production_id_and_content_duplicates_propose_one_keeper_and_retain_all_paths(self):
        from tools.art.likeness_library import retained_preparation

        production_root = self.root / "Production"
        working_root = self.root / "Working"
        photo_id = "photo:image_7508202904299473073"
        source_bytes = b"exact original shared by two Production locations"
        current_bytes = b"prepared Working version"
        source_hash = hashlib.sha256(source_bytes).hexdigest()
        current_hash = hashlib.sha256(current_bytes).hexdigest()
        angel_path = self.write(
            production_root / "Angels" / "angelica" / "gallery" / "angelica_image_7508202904299473073.jpg",
            source_bytes,
        )
        various_path = self.write(
            production_root / "Various" / "gallery" / "facebook_1790095068049_7508202904299473073.jpg",
            source_bytes,
        )
        current_path = self.write(
            working_root / "Angels" / "angelica" / "gallery" / "angelica_image_7508202904299473073.png",
            current_bytes,
        )

        def source_row(path, root, origin, owner, category, bucket, checksum, length):
            row = self.row(origin, path.relative_to(root).as_posix(), photo_id, checksum,
                           category=category, bucket=bucket, owner=owner)
            row.update(
                sourceRoot=str(root),
                absolutePath=str(path),
                byteLength=length,
            )
            row["rowId"] = rebase_manifest._row_id(row)
            return row

        angel = source_row(
            angel_path, production_root, "Production", "Angels/angelica", "Angels", "Gallery",
            source_hash, len(source_bytes),
        )
        various = source_row(
            various_path, production_root, "Production", "Various", "Various", "Pool",
            source_hash, len(source_bytes),
        )
        prepared = source_row(
            current_path, working_root, "Sandbox", "Angels/angelica", "Angels", "Gallery",
            current_hash, len(current_bytes),
        )
        link = {
            "photoId": photo_id,
            "sourceSha256": source_hash,
            "currentSha256": current_hash,
            "manifest": "_processing/Angels/angelica/set/manifest.json",
            "original": "_processing/Angels/angelica/set/original.jpg",
            "selected": "prepared-final",
            "row": {"source": "Angels/angelica/gallery/angelica_image_7508202904299473073.jpg"},
            "artifacts": [],
        }

        config = {
            "likeness": {"anchors": {"angelica": ["7508202904299473073"]}},
            "photos": {},
            "flows": {},
        }
        anchor_map = rebase_manifest._decision_maps(
            config, [angel, various, prepared], None,
        )
        self.assertEqual(len(anchor_map[photo_id]), 1)
        self.assertEqual(anchor_map[photo_id][0]["ownerFolder"], "Angels/angelica")
        self.assertEqual(anchor_map[photo_id][0]["configuredOwner"], "angelica")
        self.assertEqual(various["decisions"]["configuredIdentityAnchor"], ["7508202904299473073"])
        self.assertEqual(
            various["decisions"]["configuredIdentityAnchorOwners"][0]["ownerFolder"],
            "Angels/angelica",
        )

        with mock.patch.object(retained_preparation, "claims_photo", return_value=True), \
                mock.patch.object(retained_preparation, "verify_link", return_value=link) as verify:
            collisions = rebase_manifest._classify_unique_sources(
                [angel, various, prepared], config,
            )

        self.assertEqual(
            [row["scopeIntegrity"] for row in (angel, various)],
            ["production-exact-id-content-canonical", "production-exact-id-content-alias"],
        )
        keeper, alias = angel, various
        self.assertTrue(keeper["canonical"])
        self.assertFalse(alias["canonical"])
        self.assertEqual(alias["aliasOf"], keeper["rowId"])
        for row in (keeper, alias):
            self.assertEqual(row["exactSourceAliasEvidence"]["canonicalRowId"], keeper["rowId"])
            self.assertEqual(row["exactSourceAliasEvidence"]["proposedKeeperSourcePath"], keeper["sourcePath"])
            self.assertEqual(row["exactSourceAliasEvidence"]["sourceSha256"], source_hash)
        self.assertEqual(alias["aliasType"], "production-exact-id-content")
        self.assertEqual(collisions["productionExactIdContentAliasGroups"], 1)
        self.assertEqual(collisions["productionExactIdContentAliasRows"], 1)
        self.assertEqual(collisions["crossRootVerifiedProductionAliasRows"], 0)
        self.assertEqual(prepared["scopeIntegrity"], "verified-retained-prepared-version")
        self.assertEqual(prepared["retainedVersionOf"], keeper["rowId"])
        verify.assert_called_once_with(working_root.resolve(), current_path.resolve(), photo_id)
        self.assertEqual(angel_path.read_bytes(), source_bytes)
        self.assertEqual(various_path.read_bytes(), source_bytes)
        self.assertEqual(current_path.read_bytes(), current_bytes)

        rebase_manifest._apply_roles(
            [alias], complete=False, cores={}, core_ids=set(), diagnostics=[],
        )
        self.assertEqual(alias["role"], "production-exact-alias")
        self.assertIn(keeper["rowId"], alias["roleReason"])
        alias_csv = rebase_manifest._csv_bytes([alias]).decode("utf-8")
        self.assertIn("production-exact-id-content-alias", alias_csv)
        self.assertIn(keeper["rowId"], alias_csv)

    def test_different_production_versions_and_different_ids_with_same_bytes_stay_unresolved(self):
        production_root = self.root / "Production"
        bytes_one, bytes_two = b"original v1", b"resaved v2"
        hash_one = hashlib.sha256(bytes_one).hexdigest()
        hash_two = hashlib.sha256(bytes_two).hexdigest()
        same_id_rows = []
        for name, content, checksum in (
            ("one", bytes_one, hash_one),
            ("two", bytes_two, hash_two),
        ):
            path = self.write(
                production_root / "Angels" / "A" / "gallery" / f"angel_image_77_{name}.jpg",
                content,
            )
            row = self.row(
                "Production", path.relative_to(production_root).as_posix(), "photo:image_77",
                checksum, owner="Angels/A",
            )
            row.update(sourceRoot=str(production_root), absolutePath=str(path))
            row["rowId"] = rebase_manifest._row_id(row)
            same_id_rows.append(row)

        different_id_a = self.row(
            "Production", "Angels/A/gallery/one.jpg", "photo:image_81", hash_one,
            owner="Angels/A",
        )
        different_id_b = self.row(
            "Production", "Sisters/B/gallery/two.jpg", "photo:image_82", hash_one,
            category="Sisters", owner="Sisters/B",
        )
        unknown = self.row(
            "Production", "Models/C/gallery/future.jpg", "photo:image_83",
            hashlib.sha256(b"future row").hexdigest(), category="Models", owner="Models/C",
        )
        unknown.update(scopeIntegrity="unrecognized-future-status", rowId="future-row")
        rows = [*same_id_rows, different_id_a, different_id_b]

        collisions = rebase_manifest._classify_unique_sources(rows)
        complete, blockers, diagnostics = rebase_manifest._scope_integrity_report([*rows, unknown])

        self.assertEqual(
            [row["scopeIntegrity"] for row in same_id_rows],
            ["duplicate-production-photo-id", "duplicate-production-photo-id"],
        )
        self.assertTrue(all(not row["canonical"] and row["aliasOf"] is None for row in same_id_rows))
        self.assertEqual(different_id_a["scopeIntegrity"], "duplicate-production-content")
        self.assertEqual(different_id_b["scopeIntegrity"], "duplicate-production-content")
        self.assertTrue(all(not row["canonical"] and row["aliasOf"] is None for row in (different_id_a, different_id_b)))
        self.assertFalse(complete)
        self.assertEqual(len(blockers), 5)
        self.assertEqual(
            {item["status"] for item in diagnostics},
            {
                "duplicate-production-photo-id",
                "duplicate-production-content",
                "unrecognized-future-status",
            },
        )
        self.assertEqual(collisions["productionSameIdDifferentContentGroups"], 1)
        self.assertEqual(collisions["productionDifferentIdSameContentHashes"], 1)

    def test_ambiguous_chosen_or_conflicting_lock_copies_remain_holds(self):
        production_root = self.root / "Production"
        source_bytes = b"same bytes, conflicting source decisions"
        checksum = hashlib.sha256(source_bytes).hexdigest()

        for case, config in (
            (
                "chosen",
                {
                    "photos": {
                        "Angelica": "angelica_image_91_944x1104.png",
                        "Various": "various_image_91_944x1104.png",
                    },
                    "flows": {},
                },
            ),
            (
                "locks",
                {
                    "likeness": {"keepPhoto": ["Angelica", "Various"]},
                    "photos": {
                        "Angelica": "angelica_image_91.jpg",
                        "Various": "various_image_91.jpg",
                    },
                    "flows": {},
                },
            ),
        ):
            with self.subTest(case=case):
                angel_path = self.write(
                    production_root / case / "Angels" / "angelica" / "gallery" / "angelica_image_91.jpg",
                    source_bytes,
                )
                various_path = self.write(
                    production_root / case / "Various" / "gallery" / "various_image_91.jpg",
                    source_bytes,
                )

                def row(path, owner, category, bucket):
                    item = self.row(
                        "Production", path.relative_to(production_root / case).as_posix(),
                        "photo:image_91", checksum, category=category, bucket=bucket, owner=owner,
                    )
                    item.update(sourceRoot=str(production_root / case), absolutePath=str(path))
                    item["rowId"] = rebase_manifest._row_id(item)
                    return item

                angel = row(angel_path, "Angels/angelica", "Angels", "Gallery")
                various = row(various_path, "Various", "Various", "Pool")
                if case == "locks":
                    rebase_manifest._decision_maps(config, [angel, various], None)
                    self.assertEqual(
                        len(angel["decisions"]["truePhotoLock"]["origins"]), 2,
                    )
                    classifier_config = {"photos": {}, "flows": {}}
                else:
                    classifier_config = config
                rebase_manifest._classify_unique_sources([angel, various], classifier_config)

                for item in (angel, various):
                    self.assertFalse(item["canonical"])
                    self.assertIsNone(item["aliasOf"])
                    self.assertEqual(item["scopeIntegrity"], "ambiguous-production-exact-alias-decisions")
                    self.assertIsNone(item["exactSourceAliasEvidence"]["canonicalRowId"])
                    self.assertTrue(item["exactSourceAliasEvidence"]["decisionConflicts"])
                if case == "locks":
                    self.assertTrue(any(
                        "true photo locks" in reason
                        for reason in angel["exactSourceAliasEvidence"]["decisionConflicts"]
                    ))
                rebase_manifest._apply_roles(
                    [angel, various], complete=True, cores={}, core_ids=set(), diagnostics=[],
                )
                self.assertEqual({item["role"] for item in (angel, various)}, {"hold"})
                complete, blockers, _diagnostics = rebase_manifest._scope_integrity_report([angel, various])
                self.assertFalse(complete)
                self.assertEqual(len(blockers), 2)

    def test_configured_anchor_conflict_uses_authoritative_anchor_owners(self):
        production_root = self.root / "Production"
        source_bytes = b"same ID and bytes with two explicit owner anchors"
        checksum = hashlib.sha256(source_bytes).hexdigest()
        photo_id = "photo:image_7508202904299473073"
        owners = (
            ("Angels/angelica", "Angels", "angelica_image_7508202904299473073.jpg"),
            ("Sisters/rhea", "Sisters", "rhea_image_7508202904299473073.jpg"),
        )
        rows = []
        for owner, category, filename in owners:
            path = self.write(
                production_root / owner / "gallery" / filename,
                source_bytes,
            )
            row = self.row(
                "Production", path.relative_to(production_root).as_posix(), photo_id,
                checksum, category=category, owner=owner,
            )
            row.update(sourceRoot=str(production_root), absolutePath=str(path))
            row["rowId"] = rebase_manifest._row_id(row)
            rows.append(row)
        config = {
            "likeness": {
                "anchors": {
                    "angelica": ["7508202904299473073"],
                    "rhea": ["7508202904299473073"],
                },
            },
            "photos": {},
            "flows": {},
        }

        anchors = rebase_manifest._decision_maps(config, rows, None)
        collisions = rebase_manifest._classify_unique_sources(rows, config)

        self.assertEqual(
            {record["ownerFolder"] for record in anchors[photo_id]},
            {"Angels/angelica", "Sisters/rhea"},
        )
        self.assertEqual(
            [row["scopeIntegrity"] for row in rows],
            [
                "ambiguous-production-exact-alias-decisions",
                "ambiguous-production-exact-alias-decisions",
            ],
        )
        reasons = rows[0]["exactSourceAliasEvidence"]["decisionConflicts"]
        self.assertIn("explicit configured anchors name multiple owners for the same source", reasons)
        self.assertEqual(collisions["productionExactIdContentAmbiguousGroups"], 1)

    def test_only_exact_content_and_photo_id_pair_is_a_sandbox_alias(self):
        checksum_a = hashlib.sha256(b"a").hexdigest()
        checksum_b = hashlib.sha256(b"b").hexdigest()
        production = self.row("Production", "Angels/A/gallery/photo_1.jpg", "photo:1", checksum_a)
        exact = self.row("Sandbox", "Angels/A/gallery/photo_1.jpg", "photo:1", checksum_a)
        arrival = self.row(
            "Sandbox", "Various/gallery/photo_2.jpg", "photo:2", checksum_b,
            category="Various", bucket="Pool", owner="Various",
        )

        rebase_manifest._classify_unique_sources([production, exact, arrival])

        self.assertEqual(exact["scopeIntegrity"], "verified-production-alias")
        self.assertFalse(exact["canonical"])
        self.assertEqual(exact["aliasType"], "cross-root-production-exact-id-content")
        self.assertEqual(exact["crossRootAliasEvidence"]["canonicalRowId"], production.get("rowId") or rebase_manifest._row_id(production))
        self.assertEqual(arrival["scopeIntegrity"], "verified-unique-sandbox-arrival")
        self.assertTrue(arrival["canonical"])

    def test_id_or_byte_collisions_are_holds_not_arrivals(self):
        checksum_a = hashlib.sha256(b"a").hexdigest()
        checksum_b = hashlib.sha256(b"b").hexdigest()
        production = self.row("Production", "Angels/A/gallery/photo_1.jpg", "photo:1", checksum_a)
        changed = self.row("Sandbox", "Angels/A/gallery/photo_1.jpg", "photo:1", checksum_b)
        duplicate_bytes = self.row(
            "Sandbox", "Various/gallery/photo_2.jpg", "photo:2", checksum_a,
            category="Various", bucket="Pool", owner="Various",
        )

        rebase_manifest._classify_unique_sources([production, changed, duplicate_bytes])

        self.assertEqual(changed["scopeIntegrity"], "photo-id-content-conflict")
        self.assertEqual(duplicate_bytes["scopeIntegrity"], "duplicate-content-different-photo-id")
        self.assertFalse(changed["canonical"])
        self.assertFalse(duplicate_bytes["canonical"])

    def test_role_assignment_holds_unknown_decisions_and_does_not_use_membership(self):
        gallery = self.row("Production", "Angels/A/gallery/photo_1.jpg", "photo:1", "a" * 64)
        gallery.update(
            canonical=True,
            scopeIntegrity="unique",
            measurement={"status": "cached-vector"},
            decisions={
                "truePhotoLock": {"locked": False},
                "workflowSelected": False,
                "configuredIdentityAnchor": [],
                "sandboxProtection": None,
                "sandboxRejections": None,
                "sandboxMembership": {
                    "value": {"status": "supported", "coreUse": True},
                    "usedForCoreOrRole": False,
                },
            },
        )
        protected_arrival = self.row(
            "Sandbox", "Various/gallery/photo_2.jpg", "photo:2", "b" * 64,
            category="Various", bucket="Pool", owner="Various",
        )
        protected_arrival.update(
            canonical=True,
            scopeIntegrity="verified-unique-sandbox-arrival",
            measurement={"status": "cached-vector"},
            decisions={
                "truePhotoLock": {"locked": False},
                "workflowSelected": False,
                "configuredIdentityAnchor": [],
                "sandboxProtection": {"value": True},
                "sandboxRejections": None,
                "sandboxMembership": {"value": {"status": "supported"}, "usedForCoreOrRole": False},
            },
        )

        rebase_manifest._apply_roles(
            [gallery, protected_arrival],
            complete=True,
            cores={},
            core_ids=set(),
            diagnostics=[],
        )

        self.assertEqual(gallery["role"], "candidate")
        self.assertEqual(protected_arrival["role"], "hold")
        self.assertIn("unverified Sandbox protection", protected_arrival["roleReason"])
        self.assertFalse(gallery["decisions"]["sandboxMembership"]["usedForCoreOrRole"])

    def test_working_catalog_anchor_and_undo_history_are_disclosed_but_not_seed_authority(self):
        source = self.row("Sandbox", "Angels/A/gallery/photo_1.jpg", "photo:1", "a" * 64)
        person = {
            "id": "person:1",
            "folder": "Angels/A",
            "displayName": "A",
            "identityAnchors": ["photo:1"],
        }
        catalog = {
            "people": {"person:1": person},
            "photos": {"photo:1": {}},
            "actions": [
                {
                    "id": "action:1",
                    "type": "photo-junked",
                    "photoIds": ["photo:1"],
                    "contentSha256": "a" * 64,
                    "source": "Various/gallery/photo_1.jpg",
                    "timestamp": "2026-11-14T00:00:00Z",
                },
                {
                    "id": "action:2",
                    "type": "action-undone",
                    "photoIds": ["photo:1"],
                    "undoes": "action:1",
                    "timestamp": "2026-11-15T00:00:00Z",
                },
            ],
        }
        cfg = {"likeness": {}, "photos": {}, "flows": {}}

        rebase_manifest._decision_maps(cfg, [source], catalog)
        decisions = source["decisions"]

        self.assertEqual(decisions["sandboxIdentityAnchors"][0]["folder"], "Angels/A")
        self.assertFalse(decisions["sandboxIdentityAnchors"][0]["usedForCoreOrRole"])
        self.assertEqual(
            [action["disposition"] for action in decisions["sandboxActionHistory"]],
            ["undone", "undo-record"],
        )
        self.assertEqual(
            rebase_manifest._working_catalog_summary(catalog)["identityAnchorCount"],
            1,
        )

        source.update(
            canonical=True,
            scopeIntegrity="verified-unique-sandbox-arrival",
            measurement={"status": "cached-vector"},
        )
        rebase_manifest._apply_roles(
            [source],
            complete=True,
            cores={},
            core_ids=set(),
            diagnostics=[],
        )
        self.assertEqual(source["role"], "hold")
        self.assertIn("identity anchor is disclosed", source["roleReason"])
        self.assertIn("photo:1", rebase_manifest._csv_bytes([source]).decode("utf-8"))

    def test_incomplete_measurements_never_assign_a_gallery_reference(self):
        row = self.row("Production", "Angels/A/gallery/photo_1.jpg", "photo:1", "a" * 64)
        row.update(
            canonical=True,
            scopeIntegrity="unique",
            measurement={"status": "needs-source-bound-measurement"},
            decisions={
                "truePhotoLock": {"locked": False},
                "workflowSelected": False,
                "configuredIdentityAnchor": [],
                "sandboxProtection": None,
                "sandboxRejections": None,
                "sandboxMembership": None,
            },
        )

        rebase_manifest._apply_roles(
            [row],
            complete=False,
            cores={},
            core_ids=set(),
            diagnostics=[],
        )

        self.assertEqual(row["role"], "hold")
        self.assertEqual(row["proposedRole"], "reference-or-noncore-gallery-candidate")
        self.assertIn("awaits complete source-bound measurements", row["roleReason"])

    def test_cache_path_uses_api_domain_context_and_never_global_fallback(self):
        from tools.art import likeness as api
        from tools.art.likeness_library import domains as package_domains

        working = self.root / "Working"
        working.mkdir()
        api_domain_before = api.domains.CURRENT.get()
        package_domain_before = package_domains.CURRENT.get()
        api_read_only_before = api.domains.READ_ONLY.get()

        cache_path, cache = rebase_manifest._settings_and_cache(working)

        expected = (
            pathlib.Path(api.cw.storage_root(api.cw.load_cfg(), "likeness", root=working))
            / "general" / "cache.json"
        ).resolve()
        self.assertEqual(cache_path, expected)
        self.assertNotEqual(cache_path, pathlib.Path(api.DATA) / "likeness_cache.json")
        self.assertFalse(cache["cacheFilePresent"])
        self.assertEqual(cache["evidenceSource"], "api.Cache accepted embedding map")
        self.assertEqual(api.domains.CURRENT.get(), api_domain_before)
        self.assertEqual(package_domains.CURRENT.get(), package_domain_before)
        self.assertEqual(api.domains.READ_ONLY.get(), api_read_only_before)
        with mock.patch.object(api, "cache_path", return_value=pathlib.Path(api.DATA) / "likeness_cache.json"):
            with self.assertRaisesRegex(ValueError, "unexpected general-domain likeness cache path"):
                rebase_manifest._settings_and_cache(working)
        self.assertEqual(api.domains.CURRENT.get(), api_domain_before)
        self.assertEqual(api.domains.READ_ONLY.get(), api_read_only_before)

    def test_api_cache_filters_incomplete_vector_before_measurement_classification(self):
        working = self.root / "Working"
        working.mkdir()
        source = self.write(
            working / "Angels" / "A" / "gallery" / "photo_1.jpg",
            b"fixture image bytes",
        )
        cache_path, _empty_cache = rebase_manifest._settings_and_cache(working)
        digest = hashlib.sha1(source.read_bytes()).hexdigest()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps({
            "stat": {},
            "emb": {
                digest: {"faces": 1, "px": 120, "v": [0.1, 0.2]},
                "zero-face-without-t": {"faces": 0},
                "multi-face-without-f2": {"faces": 2, "t": 0.5},
            },
        }), encoding="utf-8")

        bound_path, accepted_cache = rebase_manifest._settings_and_cache(working)
        row = {
            "absolutePath": str(source),
            "sourcePath": "Angels/A/gallery/photo_1.jpg",
            "ownerFolder": "Angels/A",
        }
        rebase_manifest._record_hashes([row], accepted_cache)

        self.assertEqual(bound_path, cache_path)
        self.assertEqual(accepted_cache["emb"], {})
        self.assertEqual(row["measurement"]["status"], "needs-source-bound-measurement")

    def test_existing_standard_name_rules_propose_only_supported_photo_ids(self):
        working = self.root / "Working"
        names = (
            "facebook_1792529292252_7518412780610529536.jpg",
            "facebook_1792529344319_7518412998995795656.jpg",
            "facebook_1792529351596_7518413029518325141.jpg",
            "unmanaged preserved source.jpeg",
        )
        rows = []
        for name in names:
            path = self.write(working / "Various" / "gallery" / name, name.encode("ascii"))
            rows.append({
                "origin": "Production",
                "sourceRoot": str(working),
                "sourcePath": f"Various/gallery/{name}",
                "absolutePath": str(path),
                "ownerFolder": "Various",
            })

        rebase_manifest._record_hashes(rows, {"emb": {}})

        self.assertEqual(
            [row["photoId"] for row in rows],
            [
                "photo:image_7518412780610529536",
                "photo:image_7518412998995795656",
                "photo:image_7518413029518325141",
                None,
            ],
        )
        for row, original_name in zip(rows, names):
            evidence = row["photoIdEvidence"]
            self.assertEqual(evidence["originalName"], original_name)
            self.assertFalse(evidence["sourceRenamed"])
        self.assertEqual(rows[0]["photoIdEvidence"]["normalizedName"], "various_image_7518412780610529536.jpg")
        self.assertEqual(rows[0]["photoIdEvidence"]["status"], "standard-name-derived-stable-photo-id")
        self.assertEqual(rows[-1]["photoIdEvidence"]["status"], "unresolved-preserved-filename")
        self.assertIsNone(rows[-1]["photoIdEvidence"]["proposedPhotoId"])
        manifest_csv = rebase_manifest._csv_bytes(rows).decode("utf-8")
        self.assertIn("sourceOriginalName,normalizedSourceName,photoIdEvidenceStatus,photoIdBasis", manifest_csv.splitlines()[0])
        self.assertIn("facebook_1792529292252_7518412780610529536.jpg", manifest_csv)
        self.assertIn("standard-name-derived-stable-photo-id", manifest_csv)
        self.assertTrue((working / "Various" / "gallery" / names[0]).is_file())
        self.assertTrue((working / "Various" / "gallery" / names[-1]).is_file())

    def test_existing_valid_photo_id_is_not_overwritten_by_normalized_name(self):
        path = self.write(
            self.root / "Working" / "Angels" / "A" / "gallery" / "sister_image_99.jpg",
            b"existing ID fixture",
        )
        row = {
            "origin": "Production",
            "sourceRoot": str(self.root / "Working"),
            "sourcePath": "Angels/A/gallery/sister_image_99.jpg",
            "absolutePath": str(path),
            "ownerFolder": "Angels/A",
        }

        rebase_manifest._record_hashes([row], {"emb": {}})

        self.assertEqual(row["photoId"], "photo:image_99")
        self.assertEqual(row["photoIdEvidence"]["originalPhotoId"], "photo:image_99")
        self.assertEqual(row["photoIdEvidence"]["normalizedName"], "a_image_99.jpg")
        self.assertEqual(row["photoIdEvidence"]["status"], "existing-stable-photo-id")

    def test_retained_preparation_verification_separates_a_prepared_version_from_conflicts(self):
        from tools.art.likeness_library import retained_preparation

        production_bytes = b"unique Production original"
        current_bytes = b"prepared Sandbox version"
        production_hash = hashlib.sha256(production_bytes).hexdigest()
        current_hash = hashlib.sha256(current_bytes).hexdigest()
        expected = {
            "photoId": "photo:image_7508202904299473073",
            "sourceSha256": production_hash,
            "currentSha256": current_hash,
            "manifest": "_processing/Angels/A/set/manifest.json",
            "original": "_processing/Angels/A/set/original.jpg",
            "selected": "prepared-final",
            "recipe": {"version": 1},
            "artifactMap": {"source.jpg": "_processing/Angels/A/set/source.jpg"},
            "artifacts": [{"path": "_processing/Angels/A/set/source.jpg", "sha256": production_hash}],
            "row": {"source": "Various/gallery/facebook_1_7508202904299473073.jpg"},
        }
        cases = (
            ("valid", True, expected, "verified-retained-prepared-version"),
            (
                "source-mismatch", True,
                {**expected, "sourceSha256": "f" * 64},
                "retained-source-does-not-match-production",
            ),
            (
                "current-mismatch", True,
                {**expected, "currentSha256": "e" * 64},
                "retained-current-does-not-match-sandbox",
            ),
            ("missing", False, None, "no-retained-preparation-claim"),
            ("invalid", True, None, "invalid-or-stale-retained-preparation"),
        )

        for case, has_claim, link, expected_status in cases:
            with self.subTest(case=case):
                working = self.root / case
                current = self.write(
                    working / "Angels" / "A" / "gallery" / "angelica_image_7508202904299473073.png",
                    current_bytes,
                )
                production = self.row(
                    "Production", "Angels/A/gallery/angelica_image_7508202904299473073.jpg",
                    expected["photoId"], production_hash,
                )
                production.update(
                    sourceRoot=str(self.root / "Production"),
                    rowId="production-row",
                )
                sandbox = self.row(
                    "Sandbox", "Angels/A/gallery/angelica_image_7508202904299473073.png",
                    expected["photoId"], current_hash,
                )
                sandbox.update(sourceRoot=str(working), rowId="sandbox-row")

                with mock.patch.object(
                    retained_preparation, "claims_photo", return_value=has_claim,
                ) as claims, mock.patch.object(
                    retained_preparation, "verify_link", return_value=link,
                ) as verify:
                    rebase_manifest._classify_unique_sources([production, sandbox])

                self.assertEqual(sandbox["retainedPreparationEvidence"]["status"], expected_status)
                self.assertEqual(sandbox["canonical"], False)
                if has_claim:
                    claims.assert_called_once()
                    verify.assert_called_once_with(working.resolve(), current.resolve(), expected["photoId"])
                else:
                    verify.assert_not_called()
                if case == "valid":
                    self.assertEqual(sandbox["scopeIntegrity"], "verified-retained-prepared-version")
                    evidence = sandbox["retainedPreparationEvidence"]
                    self.assertEqual(evidence["productionRowId"], "production-row")
                    self.assertEqual(evidence["productionSource"]["sha256"], production_hash)
                    self.assertEqual(evidence["sandboxCurrent"]["path"], sandbox["sourcePath"])
                    self.assertEqual(evidence["retainedOriginal"], expected["original"])
                    self.assertEqual(evidence["retainedSelected"], expected["selected"])
                    self.assertEqual(evidence["artifacts"], expected["artifacts"])
                    lineage_csv = rebase_manifest._csv_bytes([sandbox]).decode("utf-8")
                    self.assertIn("verified-retained-prepared-version", lineage_csv)
                    self.assertIn(expected["original"], lineage_csv)
                    self.assertIn(production_hash, lineage_csv)
                    self.assertEqual(
                        evidence["linkage"],
                        "verified prepared version; not a new arrival, duplicate alias, or additional identity vote",
                    )
                    rebase_manifest._apply_roles(
                        [sandbox], complete=True, cores={}, core_ids=set(), diagnostics=[],
                    )
                    self.assertEqual(sandbox["role"], "hold")
                    self.assertIn("not a new candidate or identity vote", sandbox["roleReason"])
                else:
                    self.assertEqual(sandbox["scopeIntegrity"], "photo-id-content-conflict")
                    rebase_manifest._apply_roles(
                        [sandbox], complete=True, cores={}, core_ids=set(), diagnostics=[],
                    )
                    self.assertEqual(sandbox["role"], "hold")
                    self.assertIn(expected_status, sandbox["roleReason"])

    def test_report_measurement_uses_api_read_only_context_and_resets_it_on_failure(self):
        from tools.art import likeness as api

        working = self.root / "Working"
        report_root = self.root / "report"
        working.mkdir()
        report_root.mkdir()
        manifest = {
            "configuration": {"models": []},
            "rows": [],
            "measurementPlan": {},
        }

        def fail_before_model_load():
            self.assertTrue(api.domains.READ_ONLY.get())
            self.assertEqual(api.domains.CURRENT.get(), "general")
            raise RuntimeError("fixture stop before model load")

        with mock.patch.object(
            rebase_manifest, "_verify_report",
            return_value=(manifest, {}, report_root),
        ), mock.patch.object(rebase_manifest, "MODEL_FILES", ()), mock.patch.object(
            api, "Embedder", side_effect=fail_before_model_load,
        ):
            with self.assertRaisesRegex(RuntimeError, "fixture stop"):
                rebase_manifest._measure_missing(working, "fixture-run")

        self.assertFalse(api.domains.READ_ONLY.get())
        self.assertIsNone(api.domains.CURRENT.get())

    def test_public_measurement_row_reaches_core_qualification_by_bound_source_path(self):
        from tools.art.likeness_library import normal_finish

        run_id = "fixture-measurement"
        api, _production, working, source, _manifest, report_root = self.public_measurement_report(run_id)
        photo_paths = []
        core_calls = []

        class FakeMean(list):
            def tolist(self):
                return list(self)

        class FakeSpace:
            def __init__(self, photos, _settings, mean=None):
                self.photos = photos
                self.mean = mean if mean is not None else FakeMean([0.0])

        class FakeEmbedder:
            def configure_evidence(self, *_args, **_kwargs):
                self.assert_read_only_context()

            def assert_read_only_context(self):
                if not api.domains.READ_ONLY.get() or api.domains.CURRENT.get() != "general":
                    raise AssertionError("API read-only measurement context was not active")

            def load(self):
                self.assert_read_only_context()

            def __call__(self, path):
                self.assert_read_only_context()
                if pathlib.Path(path).resolve() != source.resolve():
                    raise AssertionError("inference used an unbound source path")
                return {
                    "faces": 1,
                    "an": 0,
                    "s": 0.96,
                    "f2": 0,
                    "v": [0.1, 0.2],
                    "box": [0.1, 0.1, 0.5, 0.5],
                    "px": 120,
                }

        def fake_photo(path, group, name, digest, data):
            path = pathlib.Path(path)
            photo_paths.append(path.resolve())
            return SimpleNamespace(path=path, group=group, folder=name, digest=digest, data=data)

        def fake_cores(_api, core_space, _catalog, _policy):
            core_calls.append([photo.path.resolve() for photo in core_space.photos])
            return {}, []

        with mock.patch.object(api, "Embedder", return_value=FakeEmbedder()), \
                mock.patch.object(api, "Photo", side_effect=fake_photo), \
                mock.patch.object(api, "Space", side_effect=FakeSpace), \
                mock.patch.object(normal_finish, "cores", side_effect=fake_cores), \
                mock.patch.object(rebase_manifest, "MODEL_FILES", ()), \
                contextlib.redirect_stdout(io.StringIO()):
            result = rebase_manifest._measure_missing(working, run_id)

        self.assertEqual(result, 0)
        self.assertEqual(photo_paths, [source.resolve()])
        self.assertEqual(core_calls, [[source.resolve()]])
        measured = json.loads((report_root / rebase_manifest.MEASURED_MANIFEST_NAME).read_text(encoding="utf-8"))
        row = measured["rows"][0]
        self.assertNotIn("absolutePath", row)
        self.assertEqual(row["measurement"]["status"], "report-measured-vector")
        self.assertEqual(measured["coreProposal"]["status"], "qualified")
        measurement_receipt = json.loads(
            (report_root / rebase_manifest.MEASUREMENT_RECEIPT_NAME).read_text(encoding="utf-8")
        )
        self.assertTrue(measurement_receipt["complete"])
        self.assertEqual(measurement_receipt["errorCount"], 0)

    def test_recoverable_image_error_writes_incomplete_receipt_and_nonzero_exit(self):
        from tools.art.likeness_library import normal_finish

        run_id = "fixture-measurement-error"
        api, _production, working, _source, _manifest, report_root = self.public_measurement_report(run_id)

        class FailingEmbedder:
            def configure_evidence(self, *_args, **_kwargs):
                pass

            def load(self):
                pass

            def __call__(self, _path):
                raise OSError("fixture image could not be read")

        output = io.StringIO()
        with mock.patch.object(api, "Embedder", return_value=FailingEmbedder()), \
                mock.patch.object(normal_finish, "cores") as qualify_cores, \
                mock.patch.object(rebase_manifest, "MODEL_FILES", ()), \
                contextlib.redirect_stdout(output):
            result = rebase_manifest._measure_missing(working, run_id)

        self.assertEqual(result, 2)
        printed = output.getvalue()
        final_json = printed[printed.rfind("{\n"):]
        self.assertEqual(json.loads(final_json)["status"], "report-only measurement incomplete")
        qualify_cores.assert_not_called()
        self.assertFalse(api.domains.READ_ONLY.get())
        self.assertIsNone(api.domains.CURRENT.get())
        evidence = json.loads((report_root / rebase_manifest.MEASUREMENTS_NAME).read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"], "incomplete")
        self.assertFalse(evidence["complete"])
        self.assertEqual(evidence["errorCount"], 1)
        self.assertTrue(evidence["errors"][0]["recoverable"])
        measured = json.loads((report_root / rebase_manifest.MEASURED_MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertEqual(measured["status"], "incomplete measurement report; 1 recoverable per-image failure(s) recorded")
        self.assertEqual(measured["rows"][0]["measurement"]["status"], "measurement-error")
        self.assertTrue(measured["rows"][0]["measurement"]["recoverable"])
        self.assertEqual(measured["coreProposal"]["status"], "measurement-errors-recorded")
        receipt = json.loads(
            (report_root / rebase_manifest.MEASUREMENT_RECEIPT_NAME).read_text(encoding="utf-8")
        )
        self.assertEqual(receipt["status"], "incomplete")
        self.assertFalse(receipt["complete"])
        self.assertEqual(receipt["errorCount"], 1)

    def test_unexpected_per_image_programming_error_propagates_without_success_artifacts(self):
        run_id = "fixture-programming-error"
        api, _production, working, _source, _manifest, report_root = self.public_measurement_report(run_id)

        class ProgrammingErrorEmbedder:
            def configure_evidence(self, *_args, **_kwargs):
                pass

            def load(self):
                pass

            def __call__(self, _path):
                raise RuntimeError("fixture programming error")

        with mock.patch.object(api, "Embedder", return_value=ProgrammingErrorEmbedder()), \
                mock.patch.object(rebase_manifest, "MODEL_FILES", ()), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "fixture programming error"):
                rebase_manifest._measure_missing(working, run_id)

        self.assertFalse((report_root / rebase_manifest.MEASUREMENTS_NAME).exists())
        self.assertFalse((report_root / rebase_manifest.MEASUREMENT_RECEIPT_NAME).exists())
        self.assertFalse(api.domains.READ_ONLY.get())
        self.assertIsNone(api.domains.CURRENT.get())

    def test_measurement_coverage_counts_current_working_identity_rows_and_unique_missing_bytes(self):
        rows = [
            {
                "origin": "Sandbox", "category": "Angels", "bucket": "Gallery",
                "canonical": False, "sourceSha256": "a",
                "measurement": {"status": "cached-vector"},
            },
            {
                "origin": "Sandbox", "category": "Sisters", "bucket": "Gallery",
                "canonical": True, "sourceSha256": "b",
                "measurement": {"status": "needs-source-bound-measurement"},
            },
            {
                "origin": "Sandbox", "category": "Various", "bucket": "Pool",
                "canonical": True, "sourceSha256": "b",
                "measurement": {"status": "needs-source-bound-measurement"},
            },
        ]

        coverage = rebase_manifest._measurement_coverage(rows)

        self.assertEqual(coverage["currentSandboxIdentityGalleryRows"], 2)
        self.assertEqual(
            coverage["currentSandboxIdentityGalleryByMeasurementStatus"],
            {"cached-vector": 1, "needs-source-bound-measurement": 1},
        )
        self.assertEqual(coverage["needsSourceBoundMeasurementRows"], 2)
        self.assertEqual(coverage["needsSourceBoundMeasurementUniqueRawContents"], 1)

    def test_core_composition_uses_only_unique_production_gallery_rows_and_shared_helper(self):
        from tools.art import likeness as api
        from tools.art.likeness_library import normal_finish
        from tools.art.likeness_library.policy import load_policy

        def make_row(row_id, origin, integrity, bucket="Gallery", owner="Angels/A"):
            source = self.write(self.root / f"{row_id}.jpg", row_id.encode("utf-8"))
            return {
                "rowId": row_id,
                "origin": origin,
                "scopeIntegrity": integrity,
                "canonical": integrity in (
                    "unique", "production-exact-id-content-canonical",
                    "verified-unique-sandbox-arrival",
                ),
                "category": "Angels" if owner.startswith("Angels") else "Various",
                "bucket": bucket,
                "ownerFolder": owner,
                "sourceRoot": str(self.root),
                "sourcePath": source.name,
                "absolutePath": str(source),
                "photoId": f"photo:{row_id}",
                "sourceSha256": row_id,
                "cacheKeySha1": row_id,
                "measurement": {"status": "cached-vector", "data": {"v": [1.0], "faces": 1, "px": 100}},
                "sourceName": "A" if owner.startswith("Angels") else None,
                "decisions": {
                    "truePhotoLock": {"locked": False},
                    "workflowSelected": False,
                    "configuredIdentityAnchor": [],
                    "sandboxProtection": None,
                    "sandboxRejections": None,
                },
            }

        rows = [
            make_row("unique", "Production", "unique"),
            make_row("duplicate", "Production", "duplicate-production-content"),
            make_row("exact-canonical", "Production", "production-exact-id-content-canonical"),
            make_row("exact-alias", "Production", "production-exact-id-content-alias"),
            make_row("arrival", "Sandbox", "verified-unique-sandbox-arrival", owner="Various"),
        ]
        rows[3]["photoId"] = rows[2]["photoId"]
        def make_photo(path, group, name, digest, data):
            return SimpleNamespace(path=path, group=group, name=name, digest=digest, data=data)

        spaces = []

        class FakeSpace:
            def __init__(self, photos, _settings, mean=None):
                self.photos = photos
                self.mean = [0.0] if mean is None else mean
                spaces.append(self)

        policy = load_policy()
        with mock.patch.object(api, "Photo", side_effect=make_photo), \
                mock.patch.object(api, "Space", side_effect=FakeSpace), \
                mock.patch.object(api, "configuration", return_value={}), \
                mock.patch.object(normal_finish, "cores", return_value=({}, [])) as shared_cores:
            rebase_manifest._qualify_cores(rows, {}, policy, None)

        self.assertEqual(len(spaces[0].photos), 3)
        self.assertEqual(
            {photo.path.name for photo in spaces[1].photos},
            {"unique.jpg", "exact-canonical.jpg"},
        )
        self.assertEqual(
            {photo_id for photo_id in shared_cores.call_args.args[2]["photos"]},
            {"photo:unique", "photo:exact-canonical"},
        )
        self.assertNotIn("membership", shared_cores.call_args.args[2]["photos"]["photo:unique"])

    def test_catalogue_lookup_never_falls_back_to_repository_catalogue(self):
        working = self.root / "Working"
        working.mkdir()
        with mock.patch.object(metadata, "CATALOG_PATH", self.root / "forbidden-global.json"), \
                mock.patch.object(metadata, "load_catalog", side_effect=AssertionError("global fallback used")):
            catalog, evidence = rebase_manifest._load_local_catalog(working)

        self.assertIsNone(catalog)
        self.assertEqual(evidence["status"], "absent; no global fallback used")

    def test_decision_map_records_source_scope_without_a_working_catalogue(self):
        row = self.row(
            "Sandbox", "Various/gallery/photo_2.jpg", "photo:2", "b" * 64,
            category="Various", bucket="Pool", owner="Various",
        )
        row["sourceRoot"] = str(self.root)

        anchors = rebase_manifest._decision_maps({"likeness": {}, "photos": {}, "flows": {}}, [row], None)

        self.assertEqual(anchors, {})
        self.assertEqual(row["workingCurrentOwner"], "Various")
        self.assertEqual(row["decisions"]["sandboxMembership"], None)

    def test_report_is_exclusive_and_check_detects_source_drift(self):
        production = self.root / "Production"
        working = self.root / "Working"
        source = self.write(production / "Angels" / "A" / "gallery" / "photo_1.jpg", b"before")
        checksum = hashlib.sha256(source.read_bytes()).hexdigest()
        report_root = working / "_reports" / "library" / "rebase-manifests" / "test-run"
        manifest = {
            "runId": "test-run",
            "roots": {"production": str(production), "sandboxWorking": str(working)},
            "configuration": {"cachePath": str(self.root / "missing-cache.json"), "cacheSha256": None},
            "sourceMetadata": {"metadataFiles": {}},
            "implementationHashes": rebase_manifest._implementation_hashes(),
            "rows": [{
                "origin": "Production",
                "sourceRoot": str(production),
                "sourcePath": "Angels/A/gallery/photo_1.jpg",
                "sourceSha256": checksum,
            }],
        }
        payload = json.dumps(manifest).encode("utf-8")
        csv_payload = b"rowId,role\n1,candidate\n"

        rebase_manifest._write_report(manifest, payload, csv_payload, report_root)
        checked, _receipt, _path = rebase_manifest._verify_report(working, "test-run")
        self.assertEqual(checked["runId"], "test-run")
        with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
            rebase_manifest._write_report(manifest, payload, csv_payload, report_root)

        measurement_files = {
            rebase_manifest.MEASUREMENTS_NAME: b'{"measurementCount":0}\n',
            rebase_manifest.MEASURED_MANIFEST_NAME: b'{"rows":[]}\n',
            rebase_manifest.MEASURED_CSV_NAME: b"rowId,role\n",
        }
        for name, content in measurement_files.items():
            rebase_manifest._atomic_exclusive(report_root / name, content)
        measurement_receipt = {
            "kind": "report-only-measurement-receipt",
            "runId": "test-run",
            "root": str(working.resolve()),
            "sourceManifestSha256": rebase_manifest._sha256(report_root / rebase_manifest.MANIFEST_NAME),
            "measurementsSha256": rebase_manifest._sha256(report_root / rebase_manifest.MEASUREMENTS_NAME),
            "measuredManifestSha256": rebase_manifest._sha256(report_root / rebase_manifest.MEASURED_MANIFEST_NAME),
            "measuredCsvSha256": rebase_manifest._sha256(report_root / rebase_manifest.MEASURED_CSV_NAME),
        }
        rebase_manifest._atomic_exclusive(
            report_root / rebase_manifest.MEASUREMENT_RECEIPT_NAME,
            json.dumps(measurement_receipt).encode("utf-8"),
        )
        rebase_manifest._verify_report(working, "test-run")
        (report_root / rebase_manifest.MEASUREMENTS_NAME).write_bytes(b"tampered\n")
        with self.assertRaisesRegex(ValueError, "measurement artifact changed"):
            rebase_manifest._verify_report(working, "test-run")

        (report_root / rebase_manifest.MEASUREMENTS_NAME).write_bytes(
            measurement_files[rebase_manifest.MEASUREMENTS_NAME]
        )
        source.write_bytes(b"after")
        with self.assertRaisesRegex(ValueError, "source content changed"):
            rebase_manifest._verify_report(working, "test-run")

    def test_implementation_binding_uses_accepted_normal_primitives_not_legacy_plan(self):
        hashes = rebase_manifest._implementation_hashes()

        for name in ("normalImport", "normalProducts", "normalFinish", "normalHistory", "normalTransaction"):
            self.assertIn(name, hashes)
        library = ROOT / "tools" / "art" / "likeness_library"
        self.assertEqual(
            hashes["retainedPreparation"],
            metadata.content_sha256(library / "retained_preparation.py"),
        )
        self.assertEqual(
            hashes["verificationReads"],
            metadata.content_sha256(library / "verification_reads.py"),
        )
        self.assertEqual(
            hashes["duplicates"],
            metadata.content_sha256(ROOT / "tools" / "art" / "duplicates.py"),
        )
        self.assertNotIn("cleanRebase", hashes)

    def test_launcher_and_runbook_keep_incremental_library_flow_separate(self):
        launcher = (ROOT / "bin" / "rebase-manifest.cmd").read_text(encoding="utf-8")
        help_text = (ROOT / "bin" / "help.cmd").read_text(encoding="utf-8")
        menu = (ROOT / "bin" / "menu.cmd").read_text(encoding="utf-8")
        runbook = (ROOT / "docs" / "art" / "original-photos.md").read_text(encoding="utf-8")

        self.assertIn("rebase_manifest.py %*", launcher)
        self.assertIn("rebase-manifest.cmd --run-id ID", help_text)
        self.assertIn("--measure-missing", help_text)
        self.assertNotIn("--acknowledge-measurement-coverage", help_text)
        self.assertNotIn(
            "--acknowledge-measurement-coverage",
            rebase_manifest._parser().format_help(),
        )
        self.assertIn('if /i "%CH%"=="LM" goto rebasemanifest', menu)
        self.assertIn(
            "The ordinary `library.cmd` incremental flow remains unchanged",
            re.sub(r"\s+", " ", runbook),
        )


if __name__ == "__main__":
    unittest.main()
