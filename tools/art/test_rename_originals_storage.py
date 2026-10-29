import copy
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tools.art import rename_originals
from tools.workflows import comfy_workflows as cw


class RenameActionMapStorageTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temporary_directory.name)
        self.cfg = copy.deepcopy(cw.load_cfg())
        self.cfg["paths"]["productionRoot"] = str(self.root / "production")
        self.cfg["storageRoots"]["actions"] = "_actions"
        self.record = {
            "hero": "Test Hero",
            "folder": "Test Folder",
            "old": "old-name.jpg",
            "new": "new-name.jpg",
        }

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_action_map_writes_and_reads_under_configured_actions_root(self):
        path = rename_originals.action_map_path(self.cfg)
        record = {"renames": [self.record]}
        rename_originals.write_action_map(self.cfg, path, record)

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["renames"], [self.record])
        self.assertIn("storageConfigurationReceipt", payload)
        loaded_path, loaded_record = rename_originals.load_action_map(self.cfg)
        self.assertEqual(loaded_path, path)
        self.assertEqual(loaded_record["renames"], [self.record])
        self.assertEqual(path.parent, cw.storage_root(self.cfg, "actions"))

    def test_legacy_map_is_read_when_configured_map_is_absent(self):
        legacy_path = self.root / "legacy-map.json"
        legacy_path.write_text(
            json.dumps({"renames": [self.record]}),
            encoding="utf-8",
        )

        with mock.patch.object(rename_originals, "LEGACY_MAP", legacy_path):
            configured_path, payload = rename_originals.load_action_map(self.cfg)

        self.assertEqual(configured_path, rename_originals.action_map_path(self.cfg))
        self.assertEqual(payload["renames"], [self.record])
