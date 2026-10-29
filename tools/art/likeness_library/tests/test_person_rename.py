"""Staged identity rename is stable, isolated, and exactly recoverable."""
import copy
import json
import pathlib
import tempfile
import unittest
import subprocess
import shutil
import os
from unittest import mock

from tools.art.likeness_library import actions, metadata, person_rename, review_gallery


class PersonSwapTests(unittest.TestCase):
    def save(self, updated):
        PersonRenameTests.save(self, updated)

    def apply(self, **kwargs):
        return PersonRenameTests.apply(self, **kwargs)

    def undo(self, **kwargs):
        return PersonRenameTests.undo(self, **kwargs)

    def setUp(self):
        PersonRenameTests.setUp(self)
        self.other_id = "person_" + "b" * 32
        self.other = self.root / "Prospects" / "New Name"
        (self.other / "gallery").mkdir(parents=True)
        (self.other / "gallery" / "new_image_234567.jpg").write_bytes(b"second original")
        (self.other / "gallery" / "z_new_name.txt").write_bytes(b"name: New Name\r\nsecond history\r\n")
        self.catalog["people"][self.other_id] = {
            "id": self.other_id, "folder": "Prospects/New Name", "displayName": "New Name",
            "folderHistory": [], "identityAnchors": [], "protected": False,
        }
        self.refresh()

    def refresh(self):
        snapshots = []
        for pid in (self.person_id, self.other_id):
            person = self.catalog["people"][pid]
            snapshot, reason = person_rename.decision(self.root, person["folder"], pid, person, {})
            self.assertEqual(reason, "")
            snapshots.append(snapshot)
        first, second = snapshots
        self.document["actions"] = [{
            **first, "newName": second["expectedRecordedName"], "swapConfirmed": True,
            "swapWith": {key: value for key, value in second.items() if key != "type"},
        }]
        self.original = copy.deepcopy(self.catalog)
        self.trees = {
            person["folder"]: person_rename.tree_hash(self.root / person["folder"])
            for person in self.catalog["people"].values()
        }

    def assert_original(self):
        self.assertEqual(self.catalog["people"], self.original["people"])
        self.assertEqual(self.catalog["photos"], self.original["photos"])
        for folder, digest in self.trees.items():
            self.assertEqual(person_rename.tree_hash(self.root / folder), digest)
        self.assertFalse(list(self.root.glob(".name-swap-*")))

    def configure(self, first_category, second_category):
        for pid, category, slot in (
            (self.person_id, first_category, "FixedOne"),
            (self.other_id, second_category, "FixedTwo"),
        ):
            person = self.catalog["people"][pid]
            source = self.root / person["folder"]
            cast = category in person_rename.CAST_CATEGORIES
            destination = self.root / category / (slot if cast else source.name)
            if source != destination:
                destination.parent.mkdir(exist_ok=True)
                source.rename(destination)
            person["folder"] = destination.relative_to(self.root).as_posix()
            if cast:
                person["displayName"] = slot
        self.refresh()

    def test_saved_json_crossed_directories_apply_history_and_exact_undo(self):
        path = self.root / "swap.json"
        path.write_text(json.dumps(self.document), encoding="utf-8")
        self.document = actions.load_manifest(path)
        errors, plans = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertEqual(errors, [])
        self.assertIn("partner", plans[0])
        self.apply()
        self.assertEqual((self.other / "gallery" / self.photo.name).read_bytes(), b"unchanged original")
        self.assertEqual((self.folder / "gallery" / "new_image_234567.jpg").read_bytes(), b"second original")
        record = self.catalog["actions"][-1]
        self.assertEqual(record["swapPartner"]["personId"], self.other_id)
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        for member in (record, record["swapPartner"]):
            folder = self.root / member["destination"]
            history = (folder / member["renameState"]["newHistoryPath"]).read_text(encoding="utf-8")
            self.assertIn("name swap with person_", history)
        self.undo()
        self.assert_original()

    def test_all_cast_noncast_combinations_preserve_fixed_slots_and_protection(self):
        for categories in (("Angels", "Sisters"), ("Sisters", "Prospects"),
                           ("Models", "Angels"), ("Models", "Potentials"),
                           ("Angels", "Angels")):
            with self.subTest(categories=categories):
                self.configure(*categories)
                self.apply()
                for pid, before in self.original["people"].items():
                    after = self.catalog["people"][pid]
                    self.assertEqual(after["protected"], before["protected"])
                    if before["folder"].split("/")[0] in person_rename.CAST_CATEGORIES:
                        self.assertEqual({key: value for key, value in after.items() if key != "names"}, before)
                        self.assertIn("names", after)
                        self.assertNotEqual(after["names"]["currentName"], after["names"]["originalName"])
                self.undo()
                self.assert_original()

    def test_scoped_recovery_copies_only_histories_catalogue_and_maps_both_trees(self):
        path = self.root / ".likeness-library.json"
        metadata.save_catalog(self.catalog, path)
        _, backup = actions.apply_actions(
            self.document, self.root, self.catalog, {}, "Various", save_fn=self.save,
        )
        manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["scope"], "transaction")
        self.assertEqual(manifest["files"], 3)
        self.assertEqual(len(manifest["recovery"]["members"]), 2)
        self.assertTrue(actions.library_backup.verify_backup(backup))
        self.assertEqual(manifest["recovery"]["members"][0]["source"], str(self.folder))
        self.assertEqual(manifest["recovery"]["members"][0]["destination"], str(self.other))
        self.assertIn(".name-swap-", manifest["recovery"]["members"][0]["privateStaging"])
        self.undo()
        self.assert_original()

    def test_cli_saved_json_validate_preview_apply_and_exact_undo(self):
        import contextlib
        import io

        path = self.root / "swap.json"
        path.write_text(json.dumps(self.document), encoding="utf-8")
        catalogue = self.root / ".likeness-library.json"
        metadata.save_catalog(self.catalog, catalogue)
        if os.name == "nt":
            for command in ("validate", "preview"):
                launched = subprocess.run(
                    [os.environ.get("COMSPEC", "cmd.exe"), "/c", "bin\\likeness-actions.cmd",
                     command, str(path), "--root", str(self.root)],
                    cwd=actions.ROOT, text=True, capture_output=True,
                )
                self.assertEqual(launched.returncode, 0, launched.stdout + launched.stderr)
        output = io.StringIO()
        config = actions.likeness.cw.load_cfg()
        base = pathlib.Path(self.temp.name)
        config["paths"].update({
            "productionRoot": str(self.root),
            "sandboxWorkingRoot": str(base / "sandbox" / "Working"),
            "inputsRoot": str(base / "inputs"),
            "outputRoot": str(base / "outputs"),
            "modelCacheRoot": str(base / "models"),
        })
        config.update({
            "installsRoot": str(base / "installs"),
            "sharedInput": str(base / "shared-input"),
            "sharedOutput": str(base / "shared-output"),
            "photos": {},
        })
        with mock.patch.object(actions.likeness.cw, "load_cfg", return_value=config), \
                contextlib.redirect_stdout(output):
            for command in ("validate", "preview"):
                self.assertEqual(actions.main([command, str(path), "--root", str(self.root)]), 0)
            self.assertEqual(actions.main(["apply", str(path), "--root", str(self.root), "--apply"]), 0)
            swapped = metadata.load_catalog(catalogue)
            self.assertEqual(swapped["people"][self.person_id]["folder"], "Prospects/New Name")
            self.assertEqual(actions.main(["undo", "--root", str(self.root)]), 0)
            self.assertEqual(actions.main(["undo", "--root", str(self.root), "--apply"]), 0)
        self.catalog = metadata.load_catalog(catalogue)
        self.assert_original()
        for phrase in ("two-person name swap", self.person_id, self.other_id, "restore both identities"):
            self.assertIn(phrase, output.getvalue())
        backups = list((self.root / "_backup").iterdir())
        self.assertEqual(len(backups), 2)
        for backup in backups:
            manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["scope"], "transaction")
            self.assertEqual(manifest["files"], 3)

    def test_missing_history_exact_undo(self):
        for folder in (self.folder, self.other):
            for history in (folder / "gallery").glob("z_*.txt"):
                history.unlink()
        self.refresh()
        self.apply()
        self.undo()
        self.assert_original()

    def test_mid_history_failure_and_catalogue_save_failure_restore_both(self):
        original_write = actions.person_rename._write_history
        count = 0
        def fail_second(*args):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("second history failed")
            return original_write(*args)
        with mock.patch.object(actions.person_rename, "_write_history", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "second history failed"):
                self.apply()
        self.assert_original()
        with self.assertRaisesRegex(OSError, "save failed"):
            self.apply(save_fn=mock.Mock(side_effect=OSError("save failed")))
        self.assert_original()

    def test_mid_install_failure_restores_crossed_directories(self):
        original_rename = pathlib.Path.rename
        failed = False
        def fail_install(path, destination):
            nonlocal failed
            if path.name == "1" and path.parent.name.startswith(".name-swap-") and not failed:
                failed = True
                raise OSError("install failed")
            return original_rename(path, destination)
        with mock.patch.object(pathlib.Path, "rename", fail_install):
            with self.assertRaisesRegex(OSError, "install failed"):
                self.apply()
        self.assert_original()

    def test_undo_save_failure_restores_swapped_inventory_and_can_retry(self):
        self.apply()
        after = {str(path): person_rename.tree_hash(path) for path in (self.folder, self.other)}
        with self.assertRaisesRegex(OSError, "save failed"):
            self.undo(save_fn=mock.Mock(side_effect=OSError("save failed")))
        for folder, digest in after.items():
            self.assertEqual(person_rename.tree_hash(folder), digest)
        self.undo()
        self.assert_original()

    def test_unconfirmed_mixed_stale_ambiguous_and_third_party_refused(self):
        original = copy.deepcopy(self.document)
        for update in (
            lambda row: row.pop("swapConfirmed"),
            lambda row: row["swapWith"].update(expectedRecordedName="Stale"),
            lambda row: row["swapWith"].update(expectedProtected=True),
            lambda row: row.update(expectedProtected=False),
            lambda row: row["swapWith"].update(expectedTreeSha256="0" * 64),
            lambda row: row["swapWith"].update(personId=self.person_id),
        ):
            self.document = copy.deepcopy(original)
            update(self.document["actions"][0])
            self.assertTrue(actions.validate_manifest(self.document, self.root, self.catalog, cfg={})[0])
        self.document = copy.deepcopy(original)
        self.document["actions"].append(copy.deepcopy(self.document["actions"][0]))
        self.assertTrue(actions.validate_manifest(self.document, self.root, self.catalog, cfg={})[0])
        self.document = original
        third = "person_" + "c" * 32
        self.catalog["people"][third] = {
            **self.catalog["people"][self.other_id], "id": third, "folder": "Models/New Name",
        }
        self.assertTrue(actions.validate_manifest(self.document, self.root, self.catalog, cfg={})[0])
        del self.catalog["people"][third]
        third_folder = self.root / "Models" / "New Name"
        third_folder.mkdir(parents=True)
        self.assertTrue(actions.validate_manifest(self.document, self.root, self.catalog, cfg={})[0])

    def test_partner_workflow_exclusion_inventory_and_backup_race_guards(self):
        for cfg in (
            {"photos": {"Hero": "new_image_234567.jpg"}},
            {"likeness": {"different": [["Prospects/New Name", "Angels/Other"]]}},
        ):
            self.assertTrue(actions.validate_manifest(self.document, self.root, self.catalog, cfg=cfg)[0])
        def backup(*_):
            (self.other / "empty").mkdir()
            return "verified"
        with self.assertRaisesRegex(ValueError, "changed after backup"):
            self.apply(backup_fn=backup)
        self.assertEqual(self.catalog, self.original)
        (self.other / "empty").rmdir()
        self.assert_original()

    def test_undo_refuses_changed_partner_and_third_party_original_path(self):
        self.configure("Models", "Potentials")
        self.apply()
        partner_folder = self.root / self.catalog["people"][self.other_id]["folder"]
        (partner_folder / "changed").mkdir()
        with self.assertRaisesRegex(ValueError, "files changed"):
            self.undo()
        (partner_folder / "changed").rmdir()
        original_folder = self.root / self.original["people"][self.person_id]["folder"]
        original_folder.mkdir()
        with self.assertRaisesRegex(ValueError, "occupied"):
            self.undo()
        original_folder.rmdir()
        self.undo()
        self.assert_original()

    def test_cast_swap_undo_refuses_new_third_party_recorded_name_collision(self):
        self.configure("Angels", "Sisters")
        self.apply()
        third = self.root / "Models" / "Third Person"
        (third / "gallery").mkdir(parents=True)
        (third / "gallery" / "z_third.txt").write_text("name: Old Name\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "collides"):
            self.undo()
        shutil.rmtree(third)
        self.undo()
        self.assert_original()

    def test_swap_scoped_backup_failure_and_race_do_not_mutate_either_identity(self):
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        with mock.patch.object(actions.library_backup, "create_backup", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                actions.apply_actions(
                    self.document, self.root, self.catalog, {}, "Various", save_fn=self.save,
                )
        self.assert_original()

        real_backup = actions.library_backup.create_backup
        def race(*args, **kwargs):
            result = real_backup(*args, **kwargs)
            (self.other / "changed").mkdir()
            return result
        with mock.patch.object(actions.library_backup, "create_backup", side_effect=race):
            with self.assertRaisesRegex(ValueError, "changed after backup"):
                actions.apply_actions(
                    self.document, self.root, self.catalog, {}, "Various", save_fn=self.save,
                )
        (self.other / "changed").rmdir()
        self.assert_original()

    def test_existing_private_staging_refuses_overwrite_and_keeps_recovery_files(self):
        errors, plans = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertEqual(errors, [])
        stage = actions.person_rename.swap_staging(plans[0])
        stage.mkdir()
        marker = stage / "recovery.txt"
        marker.write_bytes(b"do not touch")
        with self.assertRaisesRegex(ValueError, "recovery staging already exists"):
            self.apply()
        self.assertEqual(marker.read_bytes(), b"do not touch")
        marker.unlink()
        stage.rmdir()
        self.assert_original()

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for actual Review JavaScript export coverage")
    def test_actual_gui_confirmation_export_decline_cancel_and_plain_rename(self):
        script = review_gallery.SCRIPT
        controls = script[script.index("    if(info.personRenameAction) {"):
                          script.index("    const reference=primaryFor(folder);")]
        download = script[script.index('download.addEventListener("click",()=>{'):
                          script.index("\nupdateStagedCount();\ngrid.style")]
        first = {key: value for key, value in self.document["actions"][0].items()
                 if key not in ("newName", "swapWith", "swapConfirmed")}
        second = {"type": person_rename.ACTION, **self.document["actions"][0]["swapWith"]}
        people_data = {
            first["personFolder"]: {"personRenameAction": first, "identityProtected": True},
            second["personFolder"]: {"personRenameAction": second, "identityProtected": False},
        }
        harness = r"""
const assert=require("node:assert/strict");
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.events={};this.value="";}
  append(...nodes){this.children.push(...nodes);}
  setAttribute(){}
  addEventListener(name,callback){this.events[name]=callback;}
  click(){this.events.click?.();}
}
const document={createElement:tag=>new Element(tag),createTextNode:text=>text};
const staged=new Map(),stagedPeople=new Map(),records=[];
const confirmations=[],alerts=[];
let accepted=false,exported="";
function confirm(text){confirmations.push(text);return accepted;}
function alert(text){alerts.push(text);}
function updateStagedCount(){}
class Blob {constructor(parts){exported=parts.join("");}}
const URL={createObjectURL:()=>"blob:local",revokeObjectURL:()=>{}};
const download=new Element("button");
"""
        harness += "\nconst peopleData=" + json.dumps(people_data) + ";\n"
        harness += "const folder=" + json.dumps(first["personFolder"]) + ";\n"
        harness += "const secondFolder=" + json.dumps(second["personFolder"]) + ";\n"
        harness += "const info=peopleData[folder],actionsPanel=new Element('section');\n"
        harness += controls + "\n" + download + r"""
const label=actionsPanel.children[0];
const input=label.children.find(node=>node.tag==="input");
const stage=label.children.find(node=>node.textContent==="Stage rename");
const cancel=label.children.find(node=>node.textContent==="Cancel rename");
input.value="New Name";
stage.click();
assert.equal(stagedPeople.size,0);
assert.match(confirmations[0],/TWO-PERSON NAME SWAP/);
assert.match(confirmations[0],/Protection stays ON/);
assert.match(confirmations[0],/Protection stays OFF/);
if(folder.startsWith("Sisters/"))
  assert.match(confirmations[0],/Fixed cast slot, folder, display label and workflow references stay unchanged/);
accepted=true;stage.click();download.click();
const confirmed=JSON.parse(exported);
assert.equal(confirmed.actions.length,1);
assert.equal(confirmed.actions[0].swapConfirmed,true);
cancel.click();assert.equal(stagedPeople.size,0);
input.value="Another Name";stage.click();download.click();
assert.equal(JSON.parse(exported).actions[0].swapWith,undefined);
cancel.click();
input.value="New Name";staged.set("photo:test",{type:"photo-protected"});stage.click();
assert.equal(stagedPeople.size,0);staged.clear();
peopleData["Potentials/New Name"]={personRenameAction:{...peopleData[secondFolder].personRenameAction}};
stage.click();assert.match(alerts.at(-1),/ambiguous/);
process.stdout.write(JSON.stringify(confirmed));
"""
        result = subprocess.run(
            [shutil.which("node")], input=harness, text=True, capture_output=True, check=True,
        )
        path = self.root / "gui-swap.json"
        path.write_text(result.stdout, encoding="utf-8")
        self.document = actions.load_manifest(path)
        self.apply()
        self.undo()
        self.assert_original()

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for Review JavaScript coverage")
    def test_actual_gui_cast_noncast_confirmation_exports_fixed_slot_effects(self):
        self.configure("Sisters", "Models")
        self.test_actual_gui_confirmation_export_decline_cancel_and_plain_rename()


class PersonRenameTests(unittest.TestCase):
    def setUp(self):
        scratch = actions.ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="person-rename-", dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name) / "library"
        self.folder = self.root / "Prospects" / "Old Name"
        (self.folder / "gallery").mkdir(parents=True)
        (self.folder / "review").mkdir()
        (self.folder / "head").mkdir()
        (self.folder / "empty").mkdir()
        self.photo = self.folder / "gallery" / "old_image_123456.jpg"
        self.photo.write_bytes(b"unchanged original")
        (self.folder / "review" / "old_image_654321.jpg").write_bytes(b"review")
        (self.folder / "head" / "derived.jpg").write_bytes(b"derived")
        self.history = self.folder / "gallery" / "z_old_name.txt"
        self.history.write_bytes(b"name: Old Name\r\nroles: hero\r\n2026-10-10 arrived\r\n")
        self.person_id = "person_" + "a" * 32
        self.catalog = {
            "schemaVersion": 1, "actions": [],
            "people": {self.person_id: {
                "id": self.person_id, "folder": "Prospects/Old Name", "displayName": "Old Name",
                "folderHistory": [], "identityAnchors": [], "protected": True,
            }},
            "photos": {"photo:image_123456": {
                "contentSha256": metadata.content_sha256(self.photo), "protected": True,
                "rejectedPersonIds": [self.person_id],
            }},
        }
        self.original = copy.deepcopy(self.catalog)
        self.original_tree = person_rename.tree_hash(self.folder)
        decision, reason = person_rename.decision(
            self.root, "Prospects/Old Name", self.person_id, self.catalog["people"][self.person_id], {},
        )
        self.assertEqual(reason, "")
        self.document = {
            "manifestVersion": 1, "generatedAt": "2026-10-22T14:00:00Z",
            "source": "people-gallery-review", "actions": [{**decision, "newName": "New Name"}],
        }
        self.destination = self.root / "Prospects" / "New Name"

    def save(self, updated):
        self.catalog.clear()
        self.catalog.update(copy.deepcopy(updated))

    def prepare_cast_snapshot(self):
        cast = self.root / "Sisters" / "Draknisa"
        cast.parent.mkdir()
        self.folder.rename(cast)
        person = self.catalog["people"][self.person_id]
        person.update(folder="Sisters/Draknisa", displayName="Draknisa")
        self.folder = cast
        self.history = cast / "gallery" / self.history.name
        decision, reason = person_rename.decision(
            self.root, person["folder"], self.person_id, person, {},
        )
        self.assertEqual(reason, "")
        self.document["actions"] = [{**decision, "newName": "Amelia Morgan"}]
        self.catalogue_path = self.root / ".likeness-library.json"
        metadata.save_catalog(self.catalog, self.catalogue_path)

    def test_default_cast_backup_copies_only_write_set_and_supports_exact_undo(self):
        self.prepare_cast_snapshot()
        before_catalogue = self.catalogue_path.read_bytes()
        before_history = self.history.read_bytes()
        before_tree = person_rename.tree_hash(self.folder)
        def save(updated):
            metadata.save_catalog(updated, self.catalogue_path)
            self.save(updated)
        _, backup = actions.apply_actions(
            self.document, self.root, self.catalog, {}, "Various", save_fn=save,
        )
        manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["scope"], "transaction")
        self.assertEqual(manifest["files"], 2)
        self.assertLess(manifest["bytes"], 10000)
        self.assertEqual(
            {entry["name"] for entry in manifest["sources"]},
            {"identity-history", "likeness-catalogue"},
        )
        self.assertEqual((backup / "likeness-catalogue" / self.catalogue_path.name).read_bytes(), before_catalogue)
        self.assertEqual((backup / "identity-history" / self.history.name).read_bytes(), before_history)
        self.assertEqual(manifest["recovery"]["unchangedIdentityTreeSha256"], before_tree)
        self.assertTrue(actions.library_backup.verify_backup(backup))
        with self.assertRaisesRegex(OSError, "no complete backup"):
            actions.library_backup.latest_work_root_backup(self.root)
        _, undo_backup, _ = actions.undo_actions(
            self.catalog, self.root, {}, "Various", save_fn=save,
        )
        undo_manifest = json.loads((undo_backup / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(undo_manifest["recovery"]["reverse"])
        self.assertEqual(undo_manifest["files"], 2)
        self.assertEqual(person_rename.tree_hash(self.folder), before_tree)
        self.assertEqual(self.history.read_bytes(), before_history)
        self.assertEqual(self.catalog["people"][self.person_id]["folder"], "Sisters/Draknisa")

    def test_scoped_backup_failure_does_not_rename_or_save(self):
        self.prepare_cast_snapshot()
        before = person_rename.tree_hash(self.folder)
        with mock.patch.object(actions.library_backup, "create_backup", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                actions.apply_actions(self.document, self.root, self.catalog, {}, "Various", save_fn=self.save)
        self.assertEqual(person_rename.tree_hash(self.folder), before)
        self.assertEqual(self.catalog["actions"], [])

    def test_cast_catalogue_race_after_scoped_backup_refuses_mutation(self):
        self.prepare_cast_snapshot()
        before = person_rename.tree_hash(self.folder)
        original_backup = actions.library_backup.create_backup
        def race(*args, **kwargs):
            result = original_backup(*args, **kwargs)
            self.catalogue_path.write_bytes(self.catalogue_path.read_bytes() + b" ")
            return result
        with mock.patch.object(actions.library_backup, "create_backup", side_effect=race):
            with self.assertRaisesRegex(ValueError, "catalogue changed during backup"):
                actions.apply_actions(self.document, self.root, self.catalog, {}, "Various", save_fn=self.save)
        self.assertEqual(person_rename.tree_hash(self.folder), before)
        self.assertEqual(self.catalog["actions"], [])

    def test_cast_save_failure_with_real_scoped_snapshot_rolls_back(self):
        self.prepare_cast_snapshot()
        before = person_rename.tree_hash(self.folder)
        with self.assertRaisesRegex(OSError, "cannot save"):
            actions.apply_actions(
                self.document, self.root, self.catalog, {}, "Various",
                save_fn=mock.Mock(side_effect=OSError("cannot save")),
            )
        self.assertEqual(person_rename.tree_hash(self.folder), before)
        self.assertEqual(self.catalog["actions"], [])
        backup = next((self.root / "_backup").iterdir())
        self.assertTrue(actions.library_backup.verify_backup(backup))

    def test_cast_without_history_snapshots_catalogue_without_traversing_library(self):
        self.prepare_cast_snapshot()
        self.history.unlink()
        decision, reason = person_rename.decision(
            self.root, "Sisters/Draknisa", self.person_id, self.catalog["people"][self.person_id], {},
        )
        self.assertEqual(reason, "")
        self.document["actions"] = [{**decision, "newName": "Amelia Morgan"}]
        original_files = actions.library_backup._files
        def files(source, exclude=False):
            self.assertNotEqual(pathlib.Path(source), self.root, "scoped backup must not traverse library")
            return original_files(source, exclude)
        with mock.patch.object(actions.library_backup, "_files", side_effect=files):
            _, backup = actions.apply_actions(
                self.document, self.root, self.catalog, {}, "Various", save_fn=self.save,
            )
        manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["files"], 1)
        self.assertIsNone(manifest["recovery"]["renameState"]["oldHistoryPath"])

    def apply(self, **kwargs):
        return actions.apply_actions(
            self.document, self.root, self.catalog, {}, "Various",
            backup_fn=kwargs.get("backup_fn", lambda *_: "verified"),
            save_fn=kwargs.get("save_fn", self.save),
        )

    def undo(self, **kwargs):
        return actions.undo_actions(
            self.catalog, self.root, {}, "Various",
            backup_fn=kwargs.get("backup_fn", lambda *_: "verified"),
            save_fn=kwargs.get("save_fn", self.save),
        )

    def test_saved_json_apply_and_undo_preserve_ids_bytes_history_and_empty_directories(self):
        path = self.root / "actions.json"
        path.write_text(json.dumps(self.document), encoding="utf-8")
        document = actions.load_manifest(path)
        errors, plans = actions.validate_manifest(document, self.root, self.catalog, "Various", cfg={})
        self.assertEqual(errors, [])
        self.assertEqual(plans[0]["destination"], self.destination)
        self.assertEqual(self.catalog, self.original)
        self.apply()
        self.assertFalse(self.folder.exists())
        self.assertTrue((self.destination / "empty").is_dir())
        self.assertEqual((self.destination / "gallery" / self.photo.name).read_bytes(), b"unchanged original")
        history = (self.destination / "gallery" / "z_new_name.txt").read_bytes()
        self.assertIn(b"roles: hero\r\n2026-10-10 arrived\r\n", history)
        self.assertIn(b"renamed from Old Name (Prospects/Old Name)", history)
        person = self.catalog["people"][self.person_id]
        self.assertEqual(person["folder"], "Prospects/New Name")
        self.assertEqual(person["folderHistory"], ["Prospects/Old Name"])
        self.assertTrue(person["protected"])
        self.assertEqual(self.catalog["photos"], self.original["photos"])
        self.assertEqual(metadata.validation_errors(self.catalog), [])
        self.undo()
        self.assertEqual(person_rename.tree_hash(self.folder), self.original_tree)
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.catalog["people"], self.original["people"])
        self.assertEqual(self.catalog["photos"], self.original["photos"])

    def test_protected_cast_person_name_changes_without_renaming_slot_or_workflow_files(self):
        for category in ("Sisters", "Angels"):
            with self.subTest(category=category):
                cast = self.root / category / "Drakinsa"
                cast.parent.mkdir(exist_ok=True)
                self.folder.rename(cast)
                person = self.catalog["people"][self.person_id]
                person.update(folder=f"{category}/Drakinsa", displayName="Drakinsa")
                history = cast / "gallery" / "z_old_name.txt"
                history.write_bytes(b"name: Sweet Beauty\r\n2026-10-10 old history\r\n")
                before_hash = person_rename.tree_hash(cast)
                original = copy.deepcopy(self.catalog)
                cfg = {
                    "photos": {"Drakinsa": self.photo.name},
                    "likeness": {"different": [[f"{category}/Drakinsa", "Angels/Other"]]},
                }
                decision, reason = person_rename.decision(
                    self.root, f"{category}/Drakinsa", self.person_id, person, cfg,
                )
                self.assertEqual(reason, "")
                self.assertEqual(decision["expectedRecordedName"], "Sweet Beauty")
                self.document["actions"] = [{**decision, "newName": "Amelia Morgan"}]
                errors, plans = actions.validate_manifest(self.document, self.root, self.catalog, cfg=cfg)
                self.assertEqual(errors, [])
                self.assertEqual(plans[0]["source"], plans[0]["destination"])
                actions.apply_actions(
                    self.document, self.root, self.catalog, cfg, "Various",
                    backup_fn=lambda *_: "verified", save_fn=self.save,
                )
                self.assertTrue(cast.is_dir())
                self.assertEqual(self.catalog["people"][self.person_id]["folder"], f"{category}/Drakinsa")
                self.assertEqual(self.catalog["people"][self.person_id]["displayName"], "Drakinsa")
                self.assertTrue(self.catalog["people"][self.person_id]["protected"])
                self.assertEqual(self.catalog["people"][self.person_id]["folderHistory"], [])
                self.assertEqual(self.catalog["photos"], original["photos"])
                self.assertEqual(cfg["photos"]["Drakinsa"], self.photo.name)
                self.assertTrue((cast / "gallery" / "z_amelia_morgan.txt").is_file())
                actions.undo_actions(
                    self.catalog, self.root, cfg, "Various",
                    backup_fn=lambda *_: "verified", save_fn=self.save,
                )
                self.assertEqual(person_rename.tree_hash(cast), before_hash)
                self.assertEqual(self.catalog["people"], original["people"])
                cast.rename(self.folder)
                self.catalog = copy.deepcopy(self.original)

    def test_cast_recorded_name_staleness_noop_and_recorded_name_collision_refused(self):
        cast = self.root / "Sisters" / "Draknisa"
        cast.parent.mkdir()
        self.folder.rename(cast)
        person = self.catalog["people"][self.person_id]
        person.update(folder="Sisters/Draknisa", displayName="Draknisa")
        history = cast / "gallery" / self.history.name
        history.write_text("name: Sweet Beauty\n", encoding="utf-8")
        decision, reason = person_rename.decision(
            self.root, person["folder"], self.person_id, person, {},
        )
        self.assertEqual(reason, "")
        self.document["actions"] = [{**decision, "newName": "sweet beauty"}]
        errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("case-only", "\n".join(errors))
        self.document["actions"][0]["newName"] = "Amelia Morgan"
        other = self.root / "Angels" / "Other Slot" / "gallery"
        other.mkdir(parents=True)
        (other / "z_amelia_morgan.txt").write_text("name: Amelia Morgan\n", encoding="utf-8")
        errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("collides", "\n".join(errors))
        (other / "z_amelia_morgan.txt").unlink()
        history.write_text("name: Corrected elsewhere\n", encoding="utf-8")
        errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("recorded person name is stale", "\n".join(errors))
        self.assertEqual(self.catalog["actions"], [])
        self.assertTrue(cast.is_dir())

    def test_cast_history_save_failure_rolls_back_in_place(self):
        cast = self.root / "Sisters" / "Drakinsa"
        cast.parent.mkdir()
        self.folder.rename(cast)
        person = self.catalog["people"][self.person_id]
        person["folder"] = "Sisters/Drakinsa"
        decision, _ = person_rename.decision(self.root, person["folder"], self.person_id, person, {})
        self.document["actions"] = [{**decision, "newName": "Amelia Morgan"}]
        digest = person_rename.tree_hash(cast)
        with self.assertRaisesRegex(OSError, "cannot save"):
            self.apply(save_fn=mock.Mock(side_effect=OSError("cannot save")))
        self.assertEqual(person_rename.tree_hash(cast), digest)
        self.assertEqual(self.catalog["people"][self.person_id]["displayName"], "Old Name")

    def test_invalid_names_cast_stale_name_and_collisions_are_refused(self):
        for name in ("", "../escape", "CON", "nul.txt", "LPT1", "trailing.", " leading", "bad:name", "Old Name"):
            with self.subTest(name=name):
                self.document["actions"][0]["newName"] = name
                errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
                self.assertTrue(errors)
        self.document["actions"][0]["newName"] = "New Name"
        self.destination.mkdir()
        errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("collides", "\n".join(errors))
        self.destination.rmdir()
        self.document["actions"][0]["expectedDisplayName"] = "Stale"
        self.assertIn("stale", "\n".join(actions.validate_manifest(
            self.document, self.root, self.catalog, cfg={},
        )[0]))
        self.document["actions"][0]["personFolder"] = "Angels/Old Name"
        self.assertTrue(actions.validate_manifest(self.document, self.root, self.catalog, cfg={})[0])

    def test_changed_inventory_and_backup_race_refuse_before_moves(self):
        self.photo.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "files changed"):
            self.apply()
        self.photo.write_bytes(b"unchanged original")

        def backup(*_):
            self.photo.write_bytes(b"changed during backup")
            return "verified"

        with self.assertRaisesRegex(ValueError, "changed after backup"):
            self.apply(backup_fn=backup)
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.catalog, self.original)

    def test_save_failure_rolls_back_exact_original_files(self):
        with self.assertRaisesRegex(OSError, "cannot save"):
            self.apply(save_fn=mock.Mock(side_effect=OSError("cannot save")))
        self.assertEqual(person_rename.tree_hash(self.folder), self.original_tree)
        self.assertEqual(self.catalog, self.original)

    def test_undo_save_failure_restores_renamed_state_and_stale_undo_refuses(self):
        self.apply()
        renamed_hash = person_rename.tree_hash(self.destination)
        with self.assertRaisesRegex(OSError, "cannot save"):
            self.undo(save_fn=mock.Mock(side_effect=OSError("cannot save")))
        self.assertEqual(person_rename.tree_hash(self.destination), renamed_hash)
        (self.destination / "head" / "derived.jpg").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "files changed"):
            self.undo()

    def test_workflow_references_and_mixed_batches_refused(self):
        for cfg in (
            {"photos": {"Hero": self.photo.name}},
            {"likeness": {"different": [["Prospects/Old Name", "Angels/Other"]]}},
        ):
            errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg=cfg)
            self.assertTrue(errors)
        self.document["actions"].append({
            "type": "person-unprotected", "personId": self.person_id,
            "personFolder": "Prospects/Old Name", "expectedProtected": True,
        })
        self.assertIn("alone", "\n".join(actions.validate_manifest(
            self.document, self.root, self.catalog, cfg={},
        )[0]))

    def test_missing_history_created_and_undo_removes_it(self):
        self.history.unlink()
        self.document["actions"][0]["expectedTreeSha256"] = person_rename.tree_hash(self.folder)
        self.apply()
        self.assertTrue((self.destination / "gallery" / "z_new_name.txt").is_file())
        self.undo()
        self.assertFalse(self.history.exists())
        self.assertEqual(list((self.folder / "gallery").glob("z_*.txt")), [])

    def test_multiple_history_files_and_case_insensitive_catalogue_collision_refused(self):
        extra = self.folder / "z_extra.txt"
        extra.write_bytes(b"name: Extra\n")
        self.document["actions"][0]["expectedTreeSha256"] = person_rename.tree_hash(self.folder)
        self.assertIn("multiple", "\n".join(actions.validate_manifest(
            self.document, self.root, self.catalog, cfg={},
        )[0]))
        extra.unlink()
        self.document["actions"][0]["expectedTreeSha256"] = person_rename.tree_hash(self.folder)
        key = "person_" + "b" * 32
        self.catalog["people"][key] = {
            "id": key, "folder": "Potentials/new name", "displayName": "Other",
            "folderHistory": [], "identityAnchors": [],
        }
        self.assertIn("collides", "\n".join(actions.validate_manifest(
            self.document, self.root, self.catalog, cfg={},
        )[0]))

    def test_empty_directory_changes_and_target_appearing_during_backup_are_stale(self):
        (self.folder / "empty").rmdir()
        with self.assertRaisesRegex(ValueError, "files changed"):
            self.apply()
        (self.folder / "empty").mkdir()

        def backup(*_):
            self.destination.mkdir()
            return "verified"

        with self.assertRaisesRegex(ValueError, "changed after backup"):
            self.apply(backup_fn=backup)
        self.assertEqual(person_rename.tree_hash(self.folder), self.original_tree)

    def test_history_write_failure_rolls_back_before_catalogue_save(self):
        with mock.patch.object(actions.person_rename, "_write_history", side_effect=[OSError("write failed"), None]):
            with self.assertRaisesRegex(OSError, "write failed"):
                self.apply()
        self.assertTrue(self.folder.is_dir())
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.catalog, self.original)

    def test_undo_refuses_destination_and_workflow_changes_during_backup(self):
        self.apply()

        def backup(*_):
            self.folder.mkdir()
            return "verified"

        with self.assertRaisesRegex(ValueError, "changed after backup"):
            self.undo(backup_fn=backup)
        self.assertTrue(self.destination.is_dir())
        self.folder.rmdir()
        with self.assertRaisesRegex(ValueError, "workflow-selected"):
            actions.undo_actions(
                self.catalog, self.root, {"photos": {"Hero": self.photo.name}}, "Various",
                backup_fn=lambda *_: self.fail("should refuse before backup"), save_fn=self.save,
            )

    def test_catalogue_changes_during_backup_are_not_overwritten(self):
        def backup(*_):
            self.catalog["people"][self.person_id]["protected"] = False
            return "verified"

        with self.assertRaisesRegex(ValueError, "catalogue changed during backup"):
            self.apply(backup_fn=backup)
        self.assertFalse(self.catalog["people"][self.person_id]["protected"])
        self.assertTrue(self.folder.is_dir())
        self.assertFalse(self.destination.exists())

    def test_rollback_failure_is_explicit_and_reports_verified_backup(self):
        real_change = actions.person_rename.change_files

        def change(plan, *, reverse=False):
            if reverse:
                raise OSError("rollback blocked")
            return real_change(plan)

        with mock.patch.object(actions.person_rename, "change_files", side_effect=change):
            with self.assertRaisesRegex(OSError, "rename rollback failed.*verified backup: verified"):
                self.apply(save_fn=mock.Mock(side_effect=OSError("cannot save")))
        self.assertTrue(self.destination.is_dir())
        self.assertEqual(self.catalog, self.original)

    def test_linked_identity_is_not_exported_or_applied(self):
        real_hash = actions.person_rename.tree_hash

        def linked(folder):
            if pathlib.Path(folder) == self.folder:
                raise ValueError("rename cannot traverse a link or junction")
            return real_hash(folder)

        with mock.patch.object(actions.person_rename, "tree_hash", side_effect=linked):
            errors, _ = actions.validate_manifest(self.document, self.root, self.catalog, cfg={})
        self.assertIn("link or junction", "\n".join(errors))

    def test_cli_preview_loads_downloaded_rename_and_keeps_files_unchanged(self):
        import contextlib
        import io

        path = self.root / "rename.json"
        path.write_text(json.dumps(self.document), encoding="utf-8")
        metadata.save_catalog(self.catalog, self.root / ".likeness-library.json")
        output = io.StringIO()
        with mock.patch.object(actions.likeness.cw, "load_cfg", return_value={}), \
                contextlib.redirect_stdout(output):
            result = actions.main(["preview", str(path), "--root", str(self.root)])
        self.assertEqual(result, 0, output.getvalue())
        self.assertIn("rename identity", output.getvalue())
        self.assertIn("New Name", output.getvalue())
        self.assertEqual(person_rename.tree_hash(self.folder), self.original_tree)

    def test_render_exports_person_only_rename_snapshot_and_controls(self):
        decision = {key: value for key, value in self.document["actions"][0].items() if key != "newName"}
        page = review_gallery.render_html([{
            "folder": "Prospects/Old Name", "group": "Prospects",
            "personRenameAction": decision,
        }], "now")
        people = json.loads(page.split('<script id="people-data" type="application/json">')[1].split("</script>")[0])
        self.assertEqual(people["Prospects/Old Name"]["personRenameAction"], decision)
        self.assertIn("Stage rename", page)
        self.assertIn("Cancel rename", page)
        self.assertIn("actions.push(...stagedPeople.values())", page)


if __name__ == "__main__":
    unittest.main()
