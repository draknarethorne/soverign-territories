import copy
import pathlib
import tempfile
import types
import unittest
from unittest import mock

from tools.art import likeness
from tools.workflows import comfy_workflows as cw


class DiagnosticsOutputRoutingTests(unittest.TestCase):
    def test_explicit_output_outside_reports_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            work = root / "Working"
            work.mkdir()
            cfg = copy.deepcopy(cw.load_cfg())
            cfg["paths"]["productionRoot"] = str(root / "Production")
            cfg["storageRoots"]["reports"] = "_reports"
            args = types.SimpleNamespace(
                root=None,
                cache=None,
                out=str(root / "outside-reports"),
                policy=None,
            )

            with (
                mock.patch.object(
                    likeness,
                    "build",
                    return_value=(cfg, {}, work, root / "cache", {}),
                ),
                mock.patch.object(likeness, "load_policy", return_value={"categoryOrder": []}),
                mock.patch.object(
                    likeness,
                    "collect_diagnostics",
                    return_value=(None, [], [], [], {}),
                ),
                mock.patch.object(likeness, "write_report") as write_report,
            ):
                with self.assertRaises(ValueError):
                    likeness.cmd_diagnostics(args)

            write_report.assert_not_called()
