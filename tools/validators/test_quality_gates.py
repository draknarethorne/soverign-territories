"""Guard validation coverage, lightweight CI and repository skill contracts."""
import json
import pathlib
import re
import unittest

from tools.validators.quality_selection import COLLABORATION_SKILLS

ROOT = pathlib.Path(__file__).resolve().parents[2]
LIBRARY_TESTS = pathlib.Path("tools", "art", "likeness_library", "tests")


def skill_metadata(text):
    """Local procedural skills use only a plain name and JSON-quoted YAML description."""
    match = re.fullmatch(
        r'---\nname: ([a-z0-9]+(?:-[a-z0-9]+)*)\ndescription: ("[^\n]+")\n---\n(.+)',
        text, re.DOTALL,
    )
    if not match:
        raise ValueError("expected name and quoted description only; no executable frontmatter")
    name, description, body = match.groups()
    description = json.loads(description)
    if len(name) > 64 or not description.strip() or len(description) > 1024 or not body.strip():
        raise ValueError("invalid skill name, description or body")
    return name, description, body


def uncovered_tests(root, launcher):
    commands = "\n".join(
        line.strip() for line in launcher.splitlines() if line.lstrip().startswith("%PY% ")
    )
    references = {
        token.replace("\\", ".").replace("/", ".").removesuffix(".py")
        for token in re.findall(r"tools(?:[\\/]|\.)[\w.\\/-]*test_\w+(?:\.py)?", commands)
    }
    discovery = re.search(
        r"(?m)^%PY% -m unittest discover -s tools[\\/]art[\\/]likeness_library[\\/]tests -p test_\*\.py$",
        commands,
    )
    missing = []
    for path in (root / "tools").rglob("test_*.py"):
        relative = path.relative_to(root)
        if "_archive" in relative.parts or "__pycache__" in relative.parts:
            continue
        if discovery and relative.parent == LIBRARY_TESTS:
            continue
        module = ".".join(relative.with_suffix("").parts)
        if module not in references:
            missing.append(relative.as_posix())
    return sorted(missing)


class QualityGateTests(unittest.TestCase):
    def test_collaboration_skills_have_valid_metadata_and_resolving_local_links(self):
        entry = (ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
        for name in COLLABORATION_SKILLS:
            with self.subTest(skill=name):
                path = ROOT / ".github" / "skills" / name / "SKILL.md"
                text = path.read_text(encoding="utf-8")
                actual, description, body = skill_metadata(text)
                self.assertEqual(actual, name)
                self.assertIn("Use ", description)
                self.assertLess(len(text.encode("utf-8")), 12000)
                self.assertIn(f"skills/{name}/SKILL.md", entry)
                links = re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", body)
                self.assertTrue(links)
                for link in links:
                    self.assertNotIn("://", link, "Skills must not depend on external procedures")
                    target = (path.parent / link).resolve()
                    target.relative_to(ROOT)
                    self.assertTrue(target.is_file(), link)

    def test_skill_contract_rejects_malformed_or_executable_frontmatter(self):
        good = '---\nname: example\ndescription: "Use for handoff."\n---\n# Procedure\n'
        self.assertEqual(skill_metadata(good)[0], "example")
        for bad in (
            good.replace('description: "Use for handoff."', 'description: Use: invalid YAML'),
            good.replace("name: example", "name: Wrong_Name"),
            good.replace('description: "Use for handoff."', 'description: ""'),
            good.replace("\n---\n# Procedure", "\nhooks: {}\n---\n# Procedure"),
            good.replace("\n---\n# Procedure", "\nmodel: other\n---\n# Procedure"),
            good.replace('description: "Use for handoff."', 'description: "' + "x" * 1025 + '"'),
        ):
            with self.subTest(frontmatter=bad[:100]):
                with self.assertRaises(ValueError):
                    skill_metadata(bad)

    def test_every_active_test_module_is_selected_by_validation(self):
        launcher = (ROOT / "bin" / "validate.cmd").read_text(encoding="utf-8")
        self.assertEqual(
            uncovered_tests(ROOT, launcher), [],
            "Add new offline tests to bin\\validate.cmd; CI must not silently omit them.",
        )

    def test_guard_detects_a_missing_module(self):
        launcher = (ROOT / "bin" / "validate.cmd").read_text(encoding="utf-8")
        launcher = launcher.replace("tools.art.test_overlays", "")
        self.assertIn("tools/art/test_overlays.py", uncovered_tests(ROOT, launcher))

    def test_commented_module_does_not_count_as_execution(self):
        launcher = (ROOT / "bin" / "validate.cmd").read_text(encoding="utf-8")
        launcher = launcher.replace("tools.art.test_overlays", "")
        launcher += "\nrem python -m unittest tools.art.test_overlays\n"
        self.assertIn("tools/art/test_overlays.py", uncovered_tests(ROOT, launcher))

    def test_library_discovery_is_required_for_unnamed_library_tests(self):
        launcher = (ROOT / "bin" / "validate.cmd").read_text(encoding="utf-8")
        launcher = launcher.replace("unittest discover", "unittest")
        self.assertIn(
            "tools/art/likeness_library/tests/test_sandbox_reset.py",
            uncovered_tests(ROOT, launcher),
        )

    def test_ci_uses_shared_selector_instead_of_duplicate_suites(self):
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        commands = re.findall(r"(?m)^\s+run: (.+)$", workflow)
        self.assertIn("bin\\validate.cmd --ci", commands)
        self.assertNotIn("bin\\validate.cmd --isolated", commands)
        self.assertEqual(commands.count("bin\\validate.cmd --ci"), 1)
        self.assertFalse(any("--hook-stage manual" in command for command in commands))
        self.assertFalse(any("bin\\validate.cmd --quick" in command for command in commands))
        self.assertIn('branches: [ main ]', workflow)
        self.assertIn("fromJSON(inputs.compatibility", workflow)
        self.assertIn("""'["3.12","3.13","3.14"]' || '["3.14"]'""", workflow)

    def test_launchers_route_default_test_scratch_and_retained_fixture_is_not_root(self):
        setup = (ROOT / "bin" / "_test-env.cmd").read_text(encoding="utf-8")
        self.assertIn('set "TEMP=%%~fI"', setup)
        self.assertIn('set "TMP=%TEMP%"', setup)
        for name in ("validate", "test", "check"):
            launcher = (ROOT / "bin" / f"{name}.cmd").read_text(encoding="utf-8")
            self.assertIn('call "%~dp0_test-env.cmd"', launcher)
            self.assertIn("setlocal", launcher)
        fixture = (ROOT / "tools" / "art" / "test_retained_preparation.py").read_text(encoding="utf-8")
        self.assertNotIn("TemporaryDirectory(dir=ROOT)", fixture)

    def test_people_failure_is_checked_before_the_next_suite(self):
        launcher = (ROOT / "bin" / "validate.cmd").read_text(encoding="utf-8")
        self.assertRegex(
            launcher,
            r"%PY% tools\\art\\test_people\.py\s+if errorlevel 1 \(\s+"
            r'call "%~dp0_end\.cmd" 1\s+exit /b 1\s+\)\s+'
            r"%PY% tools\\art\\test_people_gallery\.py",
        )


if __name__ == "__main__":
    unittest.main()
