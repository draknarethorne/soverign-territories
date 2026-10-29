"""Synthetic direct-reference previews: no family or naming writes."""
import contextlib
import copy
import io
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
from typing import NotRequired, TypedDict
from unittest import mock

import numpy as np

from tools.art.likeness_library import family_preview, policy


class Identity(TypedDict):
    folder: str
    recordedName: str | None
    personId: str | None
    category: str
    mergedInto: NotRequired[str]


def identity(folder: str, name: str | None, person_id: str | None = None) -> Identity:
    return {
        "folder": folder, "recordedName": name,
        "personId": person_id or folder, "category": folder.split("/")[0],
    }


def core(x, y, side="Prospects"):
    return {"vector": np.array([x, y]), "side": side, "corePhotoIds": ["photo:example"]}


class FamilyPreviewTests(unittest.TestCase):
    def setUp(self):
        self.policy = policy.load_policy()
        self.people = [
            identity("Angels/Angelica", "Angelica Vale"),
            identity("Models/Mara", "Mara Carrington"),
            identity("Prospects/Fia", "Fia Hadley"),
        ]
        self.cores = {
            "Angels/Angelica": core(1, 0),
            "Models/Mara": core(0.8, 0.6),
            "Prospects/Fia": core(0.28, 0.96),
        }

    def test_reference_scores_are_direct_not_transitive(self):
        report = family_preview.build_preview(self.people, self.cores, self.policy)
        rows = {row["folder"]: row for row in report["suggestions"]}
        self.assertEqual(rows["Prospects/Fia"]["referenceFolder"], "Models/Mara")
        self.assertNotIn("Angels/Angelica", [
            row["folder"] for row in rows["Prospects/Fia"]["alternatives"]
        ])
        self.assertFalse(report["transitiveMembership"])
        self.assertTrue(all(row["state"] == "suggested" for row in rows.values()))
        self.assertEqual(
            report["coreEvidence"]["Models/Mara"]["corePhotoIds"], ["photo:example"],
        )

    def test_cast_names_preserved_and_possible_same_person_flagged(self):
        self.policy["categoryPolicies"]["Models"]["identityProtectedByDefault"] = True
        report = family_preview.build_preview(self.people, self.cores, self.policy)
        rows = {row["folder"]: row for row in report["suggestions"]}
        self.assertIsNone(rows["Angels/Angelica"]["proposedName"])
        self.assertEqual(rows["Models/Mara"]["proposedName"], "Mara Vale")
        self.assertTrue(rows["Models/Mara"]["samePersonReviewRequired"])
        self.assertAlmostEqual(rows["Models/Mara"]["margin"], 0)
        self.assertFalse(report["automaticChanges"])

    def test_existing_and_proposed_name_collisions_are_case_insensitive(self):
        self.people.extend([
            identity("Prospects/Mara Vale", "MARA VALE"),
            identity("Prospects/Other Mara", "Mara Other"),
        ])
        self.cores["Prospects/Other Mara"] = core(1, 0)
        report = family_preview.build_preview(self.people, self.cores, self.policy)
        row = next(row for row in report["suggestions"] if row["folder"] == "Models/Mara")
        self.assertEqual(row["nameCollisions"], ["Prospects/Mara Vale"])
        self.assertIn("Prospects/Other Mara", row["proposalCollisions"])
        self.assertEqual(report["surnameReuse"][0]["state"], "unresolved")

    def test_missing_cores_unregistered_merged_and_artists_cannot_be_references(self):
        for folder in (
            "Artists/Owner/Person", "Prospects/No ID", "Prospects/Merged", "Prospects/No Core",
        ):
            person = identity(folder, "A Person")
            if folder == "Prospects/No ID":
                person["personId"] = None
            if folder == "Prospects/Merged":
                person["mergedInto"] = "Angels/Angelica"
            self.people.append(person)
            if folder != "Prospects/No Core":
                self.cores[folder] = core(1, 0)
        report = family_preview.build_preview(self.people, self.cores, self.policy)
        self.assertEqual(len(report["excluded"]), 4)
        self.assertEqual(len(report["suggestions"]), 3)

    def test_policy_threshold_and_side_exclusion(self):
        self.policy["lookalikeGroups"]["suggestionMinimumSimilarity"] = 0.9
        self.assertEqual(family_preview.build_preview(
            self.people, self.cores, self.policy,
        )["suggestions"], [])
        self.policy["lookalikeGroups"]["suggestionMinimumSimilarity"] = 0.3
        self.cores["Models/Mara"]["side"] = "Artists"
        self.assertEqual(family_preview.build_preview(
            self.people, self.cores, self.policy,
        )["suggestions"], [])

    def test_determinism_input_immutability_missing_names_and_folder_collisions(self):
        self.people[1]["recordedName"] = None
        self.people.append(identity("models/MARA", None))
        before = copy.deepcopy(self.people)
        first = family_preview.build_preview(self.people, self.cores, self.policy)
        second = family_preview.build_preview(self.people[::-1], self.cores, self.policy)
        self.assertEqual(first, second)
        self.assertEqual(self.people, before)
        self.assertEqual(len(first["folderCollisions"]), 1)
        row = next(row for row in first["suggestions"] if row["folder"] == "Models/Mara")
        self.assertIsNone(row["proposedName"])

    def test_static_html_escapes_names_and_links_to_existing_review_filter(self):
        self.people[1]["recordedName"] = "<script>alert(1)</script> Carrington"
        report = family_preview.build_preview(self.people, self.cores, self.policy)
        page = family_preview.render_html(report, pathlib.Path(__file__).resolve())
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("?person=Angels%2FAngelica", page)
        self.assertIn("No changes are authorized", page)
        json.dumps(report)

    def test_command_writes_reports_but_never_saves_catalogue_or_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            out = root / "reports"
            sentinel = root / ".likeness-library.json"
            sentinel.write_bytes(b"catalogue unchanged")
            api = SimpleNamespace(
                cw=SimpleNamespace(storage_root=mock.Mock(return_value=root / "_reports")),
                load_policy=mock.Mock(return_value=self.policy),
                build=mock.Mock(return_value=({}, {}, root, None, SimpleNamespace(
                    photos=[], by_key={},
                ))),
                metadata=SimpleNamespace(
                    with_configured_anchors=mock.Mock(side_effect=lambda catalog, *_: catalog),
                    load_catalog=mock.Mock(return_value={
                        "people": {row["personId"]: {
                            "folder": row["folder"], "displayName": row["folder"].split("/")[-1],
                            "names": {
                                "originalName": row["recordedName"], "currentName": row["recordedName"],
                                "originalSource": "recorded-history",
                            },
                        } for row in self.people},
                    }),
                    path_for_root=mock.Mock(return_value=sentinel),
                    photo_id_from_name=mock.Mock(), content_sha256=mock.Mock(),
                ),
                frozen_identity_cores=mock.Mock(return_value=(self.cores, set(), [])),
                library_people=mock.Mock(return_value=[(row["folder"], root / row["folder"]) for row in self.people]),
                people=SimpleNamespace(name_of=mock.Mock(side_effect=[row["recordedName"] for row in self.people])),
                status_of=lambda folder: folder.split("/")[0],
            )
            args = SimpleNamespace(root=None, cache=None, policy=None, out=str(out))
            with contextlib.redirect_stdout(io.StringIO()):
                family_preview.run(args, api)
            self.assertEqual(sentinel.read_bytes(), b"catalogue unchanged")
            self.assertEqual(sorted(path.name for path in out.iterdir()), [
                "family-preview.html", "family-preview.json",
            ])
            saved = json.loads((out / "family-preview.json").read_text())
            self.assertEqual(saved["identityCount"], 3)

    def test_sandbox_guards_precede_loading_or_writing(self):
        api = mock.Mock()
        api.is_sandbox_working_path.return_value = True
        api.require_sandbox_cache.side_effect = ValueError("explicit sandbox cache required")
        args = SimpleNamespace(root="sandbox", cache=None, policy=None, out="elsewhere")
        with self.assertRaisesRegex(ValueError, "sandbox cache"):
            family_preview.run(args, api)
        api.build.assert_not_called()
        api.require_sandbox_cache.side_effect = None
        api.require_sandbox_output.side_effect = ValueError("sandbox output required")
        with self.assertRaisesRegex(ValueError, "sandbox output"):
            family_preview.run(args, api)
        api.build.assert_not_called()

    def test_actual_cli_uses_catalogue_and_records_without_library_mutation(self):
        from tools.art import test_likeness as legacy

        fixture = legacy.LikenessTests()
        fixture.setUp()
        try:
            catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
            for category, name, face in (
                ("Angels", "Angelica Vale", "ann"), ("Models", "Mara Carrington", "ann"),
                ("Prospects", "Bobbie Jones", "bob"), ("Potentials", "Dee Smith", "dee"),
            ):
                fixture.add(category, name, face, 4)
                folder = f"{category}/{name}"
                legacy.L.people.write(fixture.lib / folder, name, ["existing history"])
                person_id = legacy.L.metadata.new_person_id()
                catalog["people"][person_id] = {
                    "id": person_id, "displayName": name, "folder": folder,
                    "folderHistory": [folder], "identityAnchors": [],
                }
            legacy.L.metadata.save_catalog(catalog, fixture.lib / ".likeness-library.json")
            before = {
                path: path.read_bytes() for path in fixture.lib.rglob("*") if path.is_file()
            }
            out = fixture.tmp / "reports"
            result = fixture.run_tool("family-preview", "--out", str(out))
            self.assertNotIn("EXIT", result)
            report = json.loads((out / "family-preview.json").read_text(encoding="utf-8"))
            self.assertEqual(report["identityCount"], 4)
            self.assertEqual(report["excluded"], [])
            self.assertTrue(report["suggestions"])
            self.assertEqual(
                {row["personId"] for row in report["identities"]}, set(catalog["people"]),
            )
            self.assertEqual(before, {
                path: path.read_bytes() for path in fixture.lib.rglob("*") if path.is_file()
            })
        finally:
            fixture.tearDown()


if __name__ == "__main__":
    unittest.main()
