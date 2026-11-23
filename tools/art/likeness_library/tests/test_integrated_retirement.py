"""Item (g): emptied identity folders retire inside the rebase and intake transactions."""
import contextlib
import hashlib
import io
import json
import pathlib
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from tools.art.likeness_library import empty_retirement, metadata, normal_transaction

ROOT = pathlib.Path(__file__).resolve().parents[4]
GONE = "Potentials/Gone"
RETIRED = "_retired/Potentials/Gone"


def _write(root, relative, data):
    path = root / pathlib.PurePosixPath(relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _tree(folder):
    return {path.relative_to(folder).as_posix(): path.read_bytes()
            for path in folder.rglob("*") if path.is_file()}


class PlanEmptiedTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="plan-emptied-")
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name).resolve()
        _write(self.root, f"{GONE}/gallery/gone_image_1.jpg", b"one")
        _write(self.root, f"{GONE}/944x1104/gallery_gone_image_1.jpg", b"crop")
        self.move = {"source": f"{GONE}/gallery/gone_image_1.jpg",
                     "destination": "Models/Alpha/gallery/alpha_image_1.jpg"}

    def test_derivatives_do_not_keep_a_folder_and_photos_are_listed(self):
        rows = empty_retirement.plan_emptied(self.root, {}, [self.move])
        self.assertEqual(rows, [{"source": GONE, "destination": RETIRED, "photos": [self.move]}])
        configured = empty_retirement.plan_emptied(self.root, {"storageRoots": {"retired": "old"}}, [self.move])
        self.assertEqual(configured[0]["destination"], "old/Potentials/Gone")

    def test_remaining_original_arrival_or_nested_identity_keeps_folder(self):
        arrival = {"source": "Various/gallery/x.jpg", "destination": f"{GONE}/review/gone_image_2.jpg"}
        self.assertEqual(empty_retirement.plan_emptied(self.root, {}, [self.move, arrival]), [])
        review = _write(self.root, f"{GONE}/review/gone_image_3.jpg", b"three")
        self.assertEqual(empty_retirement.plan_emptied(self.root, {}, [self.move]), [])
        review.unlink()
        nested = _write(self.root, f"{GONE}/Sub/gallery/sub_image_4.jpg", b"four")
        self.assertEqual(empty_retirement.plan_emptied(self.root, {}, [self.move]), [])
        nested.unlink()
        self.assertEqual(len(empty_retirement.plan_emptied(self.root, {}, [], [self.move])), 1)

    def test_cast_folder_stops_with_report_and_collision_is_refused(self):
        _write(self.root, "Sisters/Lost/gallery/lost_image_5.jpg", b"five")
        cast = {"source": "Sisters/Lost/gallery/lost_image_5.jpg", "destination": "Various/review/lost_image_5.jpg"}
        with self.assertRaises(empty_retirement.CastEmptied) as stop:
            empty_retirement.plan_emptied(self.root, {}, [self.move, cast])
        self.assertIn("Sisters/Lost: Sisters/Lost/gallery/lost_image_5.jpg -> Various/review/lost_image_5.jpg",
                      str(stop.exception))
        (self.root / RETIRED).mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "already exists"):
            empty_retirement.plan_emptied(self.root, {}, [self.move])


class TransactionRetirementTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="txn-retire-")
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name).resolve() / "Working"
        self.source = f"{GONE}/gallery/gone_image_1.jpg"
        self.photo = _write(self.root, self.source, b"gone photo")
        self.crop = _write(self.root, f"{GONE}/944x1104/gallery_gone_image_1.jpg", b"crop")
        self.before = _tree(self.root / GONE)
        self.run = self.root / "_reports" / "runs" / "proof"
        self.stage = self.run / "publication"
        self.destination = "Models/Alpha/gallery/alpha_image_1.jpg"
        _write(self.stage, self.destination, b"gone photo")
        _write(self.stage, f"{GONE}/derivatives.json", b"{}")  # an after-target that moves with the folder
        self.journal = self.run / "journal.json"

    def publish(self, folders=None, **kwargs):
        return normal_transaction.publish(
            self.root, self.stage, [self.source], journal=self.journal, bindings={}, profile="fast",
            run_id="proof", expected_sources={self.source: metadata.content_sha256(self.photo)},
            retire_folders=[{"source": GONE, "destination": RETIRED}] if folders is None else folders, **kwargs,
        )

    def test_publish_retires_after_moves_and_recovery_restores_folder(self):
        seen = {}

        def finalizer():
            seen["gone"] = (self.root / GONE).exists()
            seen["retired"] = (self.root / RETIRED / "944x1104").is_dir()
            return []

        self.publish(finalizer=finalizer)
        self.assertEqual(seen, {"gone": False, "retired": True})
        self.assertFalse((self.root / GONE).exists())
        retired = self.root / RETIRED
        self.assertEqual((retired / "944x1104/gallery_gone_image_1.jpg").read_bytes(), b"crop")
        self.assertEqual((retired / "derivatives.json").read_bytes(), b"{}")
        self.assertEqual(list((retired / "gallery").iterdir()), [])
        self.assertEqual((self.root / self.destination).read_bytes(), b"gone photo")
        data = normal_transaction.verify(self.root, self.journal)
        row, = data["retiredFolders"]
        self.assertEqual((row["source"], row["destination"], row["state"]), (GONE, RETIRED, "retired"))
        self.assertIn("_retired", data["createdFolderParents"])
        # The standalone catch-up tool still accepts this journal as a predecessor.
        empty_retirement._previous_check(self.root, data, {})
        normal_transaction.recover(self.root, self.journal)
        self.assertFalse((self.root / GONE).exists())
        normal_transaction.recover(self.root, self.journal, apply=True)
        self.assertEqual(_tree(self.root / GONE), self.before)
        self.assertFalse(retired.exists())
        self.assertFalse((self.root / self.destination).exists())
        self.assertEqual(json.loads(self.journal.read_bytes())["status"], "undone")

    def test_check_detects_reappeared_source_or_missing_retired_folder(self):
        self.publish()
        (self.root / GONE).mkdir()
        with self.assertRaisesRegex(ValueError, "ambiguous retired folder"):
            normal_transaction.verify(self.root, self.journal)
        (self.root / GONE).rmdir()
        (self.root / RETIRED).rename(self.root / "_retired" / "moved")
        with self.assertRaisesRegex(ValueError, "ambiguous retired folder"):
            normal_transaction.verify(self.root, self.journal)
        (self.root / "_retired" / "moved").rename(self.root / RETIRED)
        normal_transaction.verify(self.root, self.journal)

    def test_changed_retired_folder_blocks_recovery(self):
        self.publish()
        extra = self.root / RETIRED / "note.txt"
        extra.write_bytes(b"later edit")
        with self.assertRaisesRegex(ValueError, "retired folder content changed"):
            normal_transaction.recover(self.root, self.journal, apply=True)
        self.assertTrue(extra.is_file())
        self.assertFalse((self.root / GONE).exists())
        self.assertEqual(json.loads(self.journal.read_bytes())["status"], "applied")
        # Removing the edit still changes the folder's recorded timestamp: preserve and inspect.
        extra.unlink()
        with self.assertRaisesRegex(ValueError, "retired folder content changed"):
            normal_transaction.recover(self.root, self.journal)
        self.assertTrue((self.root / RETIRED / "944x1104").is_dir())

    def test_interrupted_rename_is_recovered_from_its_pending_marker(self):
        self.publish()
        data = json.loads(self.journal.read_bytes())
        data["status"] = "publishing"
        data["retiredFolders"][0]["state"] = "planned"
        data["pendingFolderRetirement"] = 0
        self.journal.write_text(json.dumps(data), encoding="utf-8")
        normal_transaction.recover(self.root, self.journal, apply=True)
        self.assertEqual(_tree(self.root / GONE), self.before)
        self.assertFalse((self.root / RETIRED).exists())

    def test_collision_remaining_original_and_cast_are_refused_without_loss(self):
        (self.root / RETIRED).mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.publish()
        self.assertFalse(self.journal.exists())
        (self.root / RETIRED).rmdir()
        with self.assertRaisesRegex(ValueError, "non-cast"):
            self.publish([{"source": "Sisters/Gone", "destination": "_retired/Sisters/Gone"}])
        remaining = _write(self.root, f"{GONE}/review/gone_image_2.jpg", b"still here")
        with self.assertRaisesRegex(OSError, "rolled-back"):
            self.publish()
        self.assertEqual(json.loads(self.journal.read_bytes())["status"], "rolled-back")
        self.assertEqual(self.photo.read_bytes(), b"gone photo")
        self.assertEqual(remaining.read_bytes(), b"still here")
        self.assertFalse((self.root / RETIRED).exists())
        self.assertFalse((self.root / self.destination).exists())


class RebaseRetirementTests(unittest.TestCase):
    """CLI fixture: a cross-ID identical copy is archived, emptying its Potential."""

    def setUp(self):
        proof = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="p")
        self.addCleanup(proof.cleanup)
        self.root = (pathlib.Path(proof.name).resolve() / "Sovereign Territories Sandbox" / "Working"
                     / "_sandbox-state" / "normal-flow-proof-p")
        metadata.save_catalog({"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
                              _write(self.root, ".likeness-library.json", b"{}"))

    def run_cli(self, run_id, *mode, viewers=None):
        from tools.art import likeness
        from tools.art.likeness_library import normal_rebase

        def measure(_api, _cache, _embedder, path, **_kwargs):
            return hashlib.sha1(path.read_bytes()).hexdigest(), {"faces": 0, "t": 0.5}

        def default_viewers(*_args, **_kwargs):
            report_dir = self.root / "_reports" / "library"
            report_dir.mkdir(parents=True, exist_ok=True)
            for name in normal_rebase.REQUIRED_VIEWERS:
                (report_dir / name).write_text("<html>fixture</html>", encoding="utf-8")
            return [str(report_dir / name) for name in normal_rebase.REQUIRED_VIEWERS]

        errors = io.StringIO()
        output = io.StringIO()
        with (
            mock.patch.object(likeness, "configuration", return_value={}),
            mock.patch.object(likeness, "Embedder"),
            mock.patch.object(normal_rebase, "_infer", side_effect=measure),
            mock.patch.object(normal_rebase.normal_finish, "viewers", side_effect=viewers or default_viewers),
            contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors),
        ):
            result = normal_rebase.main(["--root", str(self.root), "--cache", str(self.root / "cache.json"),
                                         "--profile", "fast", "--run-id", run_id, *mode])
        return result, output.getvalue() + errors.getvalue()

    def test_rebase_apply_retires_checks_recaps_and_recovers(self):
        from tools.art.likeness_library import normal_rebase
        from tools.workflows import comfy_workflows as cw

        _write(self.root, "Prospects/Owner/gallery/owner_image_932.jpg", b"shared copy")
        copy = _write(self.root, f"{GONE}/gallery/gone_image_932.jpg", b"shared copy")
        _write(self.root, f"{GONE}/944x1104/gallery_gone_image_932.jpg", b"crop")
        before = _tree(self.root / GONE)
        listed = {}

        def viewers(*_args, **_kwargs):
            listed["folders"] = [f"{group}/{name}" for group, name, _ in cw.photo_folders({}, self.root)]
            report_dir = self.root / "_reports" / "library"
            report_dir.mkdir(parents=True, exist_ok=True)
            for name in normal_rebase.REQUIRED_VIEWERS:
                (report_dir / name).write_text("<html>fixture</html>", encoding="utf-8")
            return [str(report_dir / name) for name in normal_rebase.REQUIRED_VIEWERS]

        result, text = self.run_cli("p", "--dry-run")
        self.assertEqual(result, 0, text)
        self.assertIn(f"RETIRE {GONE} -> {RETIRED}", text)
        runs = self.root / "_reports" / "runs"
        plan = json.loads((runs / "normal-rebase-p-preview.json").read_bytes())["plan"]
        archive, = plan["duplicateArchives"].values()
        self.assertEqual(archive["source"], copy.relative_to(self.root).as_posix())
        retirement = plan["emptiedIdentityRetirement"]
        self.assertEqual(retirement["retiredRoot"], "_retired")
        self.assertEqual([(row["source"], row["destination"]) for row in retirement["folders"]], [(GONE, RETIRED)])
        self.assertEqual(retirement["folders"][0]["photos"],
                         [{"source": archive["source"], "destination": archive["destination"]}])
        self.assertTrue((self.root / GONE).is_dir())

        result, text = self.run_cli("p", "--apply", "--sandbox-apply-draft", viewers=viewers)
        self.assertEqual(result, 0, text)
        self.assertIn("1 emptied identity folder(s) retired", text)
        self.assertNotIn(GONE, listed["folders"])
        self.assertIn("Prospects/Owner", listed["folders"])
        self.assertFalse((self.root / GONE).exists())
        self.assertEqual((self.root / RETIRED / "944x1104/gallery_gone_image_932.jpg").read_bytes(), b"crop")
        applied = runs / "normal-rebase-p.json"
        receipt = json.loads(applied.read_bytes())
        self.assertEqual(receipt["retiredIdentityFolders"], retirement["folders"])
        journal = json.loads(pathlib.Path(receipt["journal"]).read_bytes())
        self.assertEqual(journal["retiredFolders"][0]["state"], "retired")

        result, text = self.run_cli("p", "--check")
        self.assertEqual(result, 0, text)
        self.assertIn(f"retired {GONE} -> {RETIRED} (verified present; source absent)", text)
        (self.root / GONE).mkdir()
        self.assertEqual(self.run_cli("p", "--check")[0], 1)
        (self.root / GONE).rmdir()
        tampered = dict(receipt, retiredIdentityFolders=[])
        applied.write_text(json.dumps(tampered), encoding="utf-8")
        result, text = self.run_cli("p", "--check")
        self.assertEqual(result, 1)
        self.assertIn("differ from the publication journal", text)
        applied.write_text(json.dumps(receipt), encoding="utf-8")

        recap = normal_rebase.normal_recap.collect(applied)
        page = normal_rebase.normal_recap.render(recap, self.root / "_reports" / "library" / "recap.html")
        self.assertIn('<h2 id="retired-identities">Emptied identities retired</h2>', page)
        self.assertIn(f'<a href="../../{RETIRED}">{RETIRED}</a>', page)
        self.assertIn(f"{archive['source']} → {archive['destination']}", page)
        preview_page = normal_rebase.normal_recap.render(
            normal_rebase.normal_recap.collect(runs / "normal-rebase-p-preview.json"),
            self.root / "_reports" / "library" / "preview.html",
        )
        self.assertIn(f"Proposed: {RETIRED}", preview_page)

        result, text = self.run_cli("p", "--recover-apply")
        self.assertEqual(result, 0, text)
        self.assertEqual(_tree(self.root / GONE), before)
        self.assertFalse((self.root / RETIRED).exists())

    def test_preview_binding_refuses_changed_retirement_list(self):
        _write(self.root, "Prospects/Owner/gallery/owner_image_932.jpg", b"shared copy")
        _write(self.root, f"{GONE}/gallery/gone_image_932.jpg", b"shared copy")
        self.assertEqual(self.run_cli("t", "--dry-run")[0], 0)
        preview = self.root / "_reports" / "runs" / "normal-rebase-t-preview.json"
        saved = json.loads(preview.read_bytes())
        saved["plan"]["emptiedIdentityFingerprint"] = "0" * 64
        preview.write_text(json.dumps(saved), encoding="utf-8")
        result, text = self.run_cli("t", "--apply", "--sandbox-apply-draft")
        self.assertEqual(result, 1)
        self.assertIn("emptied identity folders to retire differ from preview", text)
        self.assertTrue((self.root / GONE / "gallery" / "gone_image_932.jpg").is_file())

    def test_emptied_cast_folder_stops_preview_with_report(self):
        _write(self.root, "Angels/Keep/gallery/keep_image_942.jpg", b"cast copy")
        lost = _write(self.root, "Sisters/Lost/gallery/lost_image_942.jpg", b"cast copy")
        result, text = self.run_cli("c", "--dry-run")
        self.assertEqual(result, 1)
        self.assertIn("Sisters/Angels folder(s) would be emptied", text)
        self.assertIn("Sisters/Lost: Sisters/Lost/gallery/lost_image_942.jpg -> _duplicates/", text)
        self.assertFalse((self.root / "_reports" / "runs" / "normal-rebase-c-preview.json").exists())
        self.assertTrue(lost.is_file())


class IntakeRetirementTests(unittest.TestCase):
    """Intake apply retires a released small Potential emptied by its upward move."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="intake-retire-")
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name).resolve() / "Working"
        self.arrival = _write(self.root, "Various/gallery/plain.jpg", b"held original")
        _write(self.root, "Models/Alpha/gallery/alpha_image_1.jpg", b"alpha")

    def run_cli(self, mode, moves, catalog, viewers=lambda *_a, **_k: []):
        from tools.art import likeness, originals
        from tools.art.likeness_library import maintenance, normal_finish, normal_import
        from tools.art.likeness_library.policy import load_policy

        name = normal_import._arrival_name(self.arrival, originals, metadata)
        photo_id = metadata.photo_id_from_name(name)
        report = {
            "assignments": [], "held": [{"photoId": photo_id, "reason": "unassigned"}],
            "clusters": [], "updateTargets": {}, "updateTargetHashes": {}, "olderArrivals": [],
            "sourceHashes": {photo_id: metadata.content_sha256(self.arrival)},
            "selectedPhotoIds": [photo_id], "eligibleIdentityCount": 1,
            "policyVersion": "test", "policyStatus": "draft",
            "coreDiagnostics": [], "membershipDiagnostics": [],
            "implementationSHA256": metadata.content_sha256(pathlib.Path(normal_import.__file__)),
            "bindings": {},
        }
        catalog_path = self.root.parent / "fallback-catalogue.json"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        photo = SimpleNamespace(path=self.arrival, name=name)
        cache = SimpleNamespace(stat={}, save=lambda: None)
        plan = lambda *_args, **_kwargs: (
            dict(report), [{}], [photo], SimpleNamespace(photos=[]), catalog, {}, load_policy(), cache,
        )

        def backup(_root, *, apply, scoped_sources):
            folder = self.root / "_backup" / "proof"
            folder.mkdir(parents=True)
            entries = []
            for index, (_label, path) in enumerate(scoped_sources):
                shutil.copyfile(path, folder / f"{index}.original")
                entries.append({"source": str(path), "backup": f"{index}.original",
                                "sha256": metadata.content_sha256(path)})
            (folder / "manifest.json").write_text(json.dumps({"entries": entries}), encoding="utf-8")
            return folder

        output = io.StringIO()
        with (
            mock.patch.object(likeness.cw, "load_cfg", return_value={}),
            mock.patch.object(likeness.cw, "storage_root", side_effect=lambda _cfg, key, root: pathlib.Path(root) / (
                "_retired" if key == "retired" else "_reports")),
            mock.patch.object(metadata, "CATALOG_PATH", catalog_path),
            mock.patch.object(normal_import, "_plan", side_effect=plan),
            mock.patch.object(normal_import, "_policy_permitted_moves", side_effect=lambda rows, _p: (rows, [])),
            mock.patch.object(maintenance, "proposed_moves", side_effect=lambda *_a: [dict(row) for row in moves]),
            mock.patch.object(maintenance, "require_authorization"),
            mock.patch.object(maintenance, "_validate_permissions"),
            mock.patch.object(normal_finish, "check_batch", side_effect=lambda *_a, **_k: (list(_a[4]), {})),
            mock.patch.object(normal_finish, "projected", return_value=SimpleNamespace()),
            mock.patch.object(normal_finish, "family_and_final", return_value={}),
            mock.patch.object(normal_finish, "viewers", side_effect=viewers),
            mock.patch("tools.art.library_backup.create_backup", side_effect=backup),
            contextlib.redirect_stdout(output), contextlib.redirect_stderr(output),
        ):
            result = normal_import.main(["--root", str(self.root), "--profile", "fast",
                                         "--run-id", "retire-proof", mode])
        return result, output.getvalue()

    def test_intake_apply_retires_emptied_potential_catalogue_and_recovery(self):
        from tools.art.likeness_library import normal_import
        from tools.workflows import comfy_workflows as cw

        lone = _write(self.root, "Potentials/Lone/gallery/lone_image_10.jpg", b"lone")
        _write(self.root, "Potentials/Lone/944x1104/gallery_lone_image_10.jpg", b"lone crop")
        before = _tree(self.root / "Potentials/Lone")
        lone_id = metadata.photo_id_from_name(lone.name)
        lone_person, alpha_person = "person_" + "a" * 32, "person_" + "b" * 32
        catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {
                lone_person: {"id": lone_person, "displayName": "Lone", "folder": "Potentials/Lone",
                              "folderHistory": [], "identityAnchors": []},
                alpha_person: {"id": alpha_person, "displayName": "Alpha", "folder": "Models/Alpha",
                               "folderHistory": [], "identityAnchors": []},
            },
            "photos": {lone_id: {"contentSha256": metadata.content_sha256(lone), "protected": False, "membership": {
                "personId": lone_person, "groupId": None, "status": "supported", "coreUse": True,
                "reason": "fixture", "referenceVersion": "1" * 64,
            }}},
        }
        destination = "Models/Alpha/gallery/alpha_image_10.jpg"
        moves = [{"photoId": lone_id, "source": "Potentials/Lone/gallery/lone_image_10.jpg",
                  "destination": destination, "sha256": metadata.content_sha256(lone),
                  "reason": "released small Potential moves upward", "normalAdmission": True,
                  "referenceVersion": "2" * 64, "referenceEligible": False, "intakeReleasedPotential": True}]
        listed = {}

        def viewers(*_args, **_kwargs):
            listed["folders"] = [f"{group}/{name}" for group, name, _ in cw.photo_folders({}, self.root)]
            return []

        result, text = self.run_cli("--dry-run", moves, catalog)
        self.assertEqual(result, 0, text)
        self.assertIn("RETIRE Potentials/Lone -> _retired/Potentials/Lone (1 photo(s) leave it)", text)
        self.assertTrue(lone.is_file())
        result, text = self.run_cli("--apply", moves, catalog, viewers)
        self.assertEqual(result, 0, text)
        self.assertIn("retired emptied identity: Potentials/Lone -> _retired/Potentials/Lone", text)
        self.assertNotIn("Potentials/Lone", listed["folders"])
        self.assertFalse((self.root / "Potentials/Lone").exists())
        self.assertEqual((self.root / "_retired/Potentials/Lone/944x1104/gallery_lone_image_10.jpg").read_bytes(),
                         b"lone crop")
        self.assertEqual((self.root / destination).read_bytes(), b"lone")
        receipt_path = self.root / "_reports" / "runs" / "normal-import-retire-proof.json"
        receipt = json.loads(receipt_path.read_bytes())
        self.assertEqual([(row["source"], row["destination"]) for row in receipt["retiredIdentityFolders"]],
                         [("Potentials/Lone", "_retired/Potentials/Lone")])
        normal_import._check_receipt(self.root, receipt_path)
        # Catalogue: like the rebase, the emptied person keeps no member; history records the source.
        updated = metadata.load_catalog(self.root / ".likeness-library.json")
        self.assertFalse([pid for pid, record in updated["photos"].items()
                          if record.get("membership", {}).get("personId") == lone_person])
        membership = updated["photos"][lone_id]["membership"]
        self.assertEqual(membership["personId"], alpha_person)
        self.assertEqual(membership["sourcePersonIds"], [lone_person])
        (self.root / "Potentials/Lone").mkdir()
        with self.assertRaisesRegex(ValueError, "ambiguous retired folder"):
            normal_import._check_receipt(self.root, receipt_path)
        (self.root / "Potentials/Lone").rmdir()
        normal_transaction.recover(self.root, receipt["journal"], apply=True)
        self.assertEqual(_tree(self.root / "Potentials/Lone"), before)
        self.assertFalse((self.root / "_retired/Potentials/Lone").exists())
        self.assertFalse((self.root / destination).exists())
        # The fixture started from the fallback catalogue, so recovery removes the published local one.
        self.assertFalse((self.root / ".likeness-library.json").exists())
        self.assertEqual(metadata.load_catalog(self.root.parent / "fallback-catalogue.json")["photos"][lone_id]
                         ["membership"]["personId"], lone_person)

    def test_intake_stops_when_a_cast_folder_would_be_emptied(self):
        solo = _write(self.root, "Sisters/Solo/gallery/solo_image_11.jpg", b"solo")
        moves = [{"photoId": metadata.photo_id_from_name(solo.name),
                  "source": "Sisters/Solo/gallery/solo_image_11.jpg",
                  "destination": "Models/Alpha/gallery/alpha_image_11.jpg",
                  "sha256": metadata.content_sha256(solo), "reason": "fixture"}]
        catalog = {"schemaVersion": 1, "people": {}, "photos": {}, "actions": []}
        for mode in ("--dry-run", "--apply"):
            result, text = self.run_cli(mode, moves, catalog)
            self.assertEqual(result, 1, text)
            self.assertIn("Sisters/Solo: Sisters/Solo/gallery/solo_image_11.jpg -> Models/Alpha/gallery", text)
        self.assertTrue(solo.is_file())
        self.assertFalse((self.root / "_reports" / "runs" / "normal-import-retire-proof.json").exists())


if __name__ == "__main__":
    unittest.main()
