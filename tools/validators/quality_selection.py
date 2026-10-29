"""Conservative change-based offline test selection shared by local launchers and CI."""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCOPES = ("workflow", "intake", "library", "data", "quality")
INTAKE = {
    "test_image_preparation", "test_overlays", "test_intake_sequence",
    "test_eraser_benchmark", "test_overlay_reference_review",
}


def module_scope(path):
    parts = path.parts
    if "validators" in parts:
        return "quality"
    if "workflows" in parts or "generators" in parts:
        return "workflow"
    if path.stem in INTAKE:
        return "intake"
    if "audits" in parts or path.stem in {
        "test_dragon_companions", "test_identity_audit", "test_negation_audit", "test_todo_report",
    }:
        return "data"
    return "library"


def select(paths):
    scopes, mutations, reasons = set(), False, []
    full = False
    for raw in paths:
        path = raw.replace("\\", "/")
        name = pathlib.PurePosixPath(path).name
        if path.startswith(("docs/", "feedback/")) or name in {"README.md", "CONTRIBUTING.md", "LICENSE"}:
            reasons.append(f"{path}: documentation; routine lint only")
        elif path.startswith(("tools/validators/", "data/schemas/", "data/art/_schema/")):
            full = True
            mutations = True
            reasons.append(f"{path}: validator/schema dependency; full coverage")
        elif path.startswith(("tools/workflows/", "tools/generators/", "workflows/", "prompts/")):
            scopes.add("workflow")
            if name in {"comfy_workflows.py", "workspaces.json", "gen_prompt.py"}:
                scopes.update(("intake", "library", "data"))
            reasons.append(f"{path}: workflow; shared configuration includes its consumers")
        elif path.startswith("tools/art/intake_library/") or name in {
            "image_preparation.py", "eraser_benchmark.py", "intake_sequence_benchmark.py",
            "overlay_reference_review.py",
        } or (path.startswith("tools/art/") and pathlib.PurePosixPath(path).stem in INTAKE):
            scopes.update(("intake", "library", "workflow", "data"))
            reasons.append(f"{path}: intake, retained/rebase and exported-workflow consumers")
        elif path.startswith(("tools/art/likeness_library/", "tools/art/")):
            scopes.update(("library", "intake", "data", "workflow"))
            reasons.append(f"{path}: shared art/library consumers")
        elif path.startswith("data/"):
            scopes.update(("data", "workflow", "library", "intake"))
            reasons.append(f"{path}: data and art consumers; no validator mutations")
        else:
            full = True
            mutations = True
            reasons.append(f"{path}: unclassified/infrastructure dependency; full fallback")
    return {"full": full, "scopes": sorted(scopes), "mutations": mutations, "reasons": reasons}


def changed_paths(base, head=None):
    command = ["git", "diff", "--name-only", "-z", "--no-renames", base]
    if head:
        command.append(head)
    command.append("--")
    output = subprocess.run(command, cwd=ROOT, check=True, stdout=subprocess.PIPE).stdout
    paths = output.decode("utf-8").split("\0")
    if head is None:
        extra = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=ROOT, check=True, stdout=subprocess.PIPE,
        ).stdout
        paths.extend(extra.decode("utf-8").split("\0"))
    return sorted({path for path in paths if path})


def ci_selection(environ):
    event = json.loads(pathlib.Path(environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    kind = environ["GITHUB_EVENT_NAME"]
    if kind == "workflow_dispatch":
        return {"full": True, "scopes": list(SCOPES), "mutations": True,
                "reasons": ["explicit dispatch: full regression and mutation gate"]}
    if kind == "pull_request":
        pr = event["pull_request"]
        base = subprocess.run(
            ["git", "merge-base", pr["base"]["sha"], pr["head"]["sha"]],
            cwd=ROOT, check=True, stdout=subprocess.PIPE, text=True,
        ).stdout.strip()
        return routine_ci_plan(select(changed_paths(base, pr["head"]["sha"])))
    if kind == "push":
        base = event["before"]
        if not base or set(base) == {"0"}:
            return routine_ci_plan({"full": True, "scopes": list(SCOPES), "mutations": True,
                                    "reasons": ["new branch: no trustworthy previous commit; full fallback"]})
        return routine_ci_plan(select(changed_paths(base, environ["GITHUB_SHA"])))
    raise ValueError(f"Unsupported CI event: {kind}")


def routine_ci_plan(plan):
    """Run only lightweight gate guards; leave subsystem regressions explicit."""
    return {
        "full": False, "scopes": ["quality"], "mutations": False,
        "reasons": [
            *plan["reasons"],
            "routine CI: quality/isolation guards only; subsystem/full regressions require an explicit request",
        ],
    }


def commands_for(plan):
    commands = []
    if plan["mutations"]:
        commands.append([sys.executable, str(pathlib.Path("tools", "validators", "test_validate_data.py")), "--isolated"])
    if plan["full"]:
        commands.append([os.environ.get("ComSpec", "cmd.exe"), "/c", "bin\\validate.cmd"])
        return commands
    scopes = set(plan["scopes"])
    if not scopes:
        return commands
    scopes.add("quality")
    if "data" in scopes:
        commands.append([sys.executable, str(pathlib.Path("tools", "validators", "validate_data.py"))])
    for path in sorted((ROOT / "tools").rglob("test_*.py")):
        if "_archive" in path.parts or path.name == "test_validate_data.py":
            continue
        relative = path.relative_to(ROOT)
        if module_scope(relative) in scopes:
            commands.append([sys.executable, "-m", "unittest", ".".join(relative.with_suffix("").parts)])
    if "data" in scopes:
        for script, arguments in (
            ("tools/art/negation_audit.py", ["--no-sources", "--check"]),
            ("tools/art/identity_audit.py", ["--check"]),
            ("tools/art/audits/codex_drift.py", ["--check"]),
        ):
            commands.append([sys.executable, str(pathlib.Path(script)), *arguments])
    return commands


def run(commands):
    scratch = (ROOT / "tmp").resolve()
    scratch.mkdir(exist_ok=True)
    environment = {**os.environ, "TEMP": str(scratch), "TMP": str(scratch), "TMPDIR": str(scratch)}
    for command in commands:
        started = time.monotonic()
        print("RUN", subprocess.list2cmdline(command), flush=True)
        result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
        print(f"EXIT {result.returncode} after {time.monotonic() - started:.2f}s", flush=True)
        if result.returncode:
            return result.returncode
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scope", choices=(*SCOPES, "full"))
    group.add_argument("--changed", metavar="BASE", help="Tracked and untracked changes against BASE")
    group.add_argument("--ci", action="store_true")
    group.add_argument("--full", action="store_true", help="All regressions and full isolated mutations")
    parser.add_argument("--dry-run", action="store_true", help="Print selection without running tests")
    parser.add_argument("--check", action="store_true", help="Execute selected read-only checks/tests")
    args = parser.parse_args(argv)
    if args.dry_run and args.check:
        parser.error("--dry-run and --check are mutually exclusive")
    if args.ci:
        plan = ci_selection(os.environ)
    elif args.changed:
        plan = select(changed_paths(args.changed))
    elif args.full:
        plan = {"full": True, "scopes": list(SCOPES), "mutations": True, "reasons": ["explicit full gate"]}
    else:
        plan = {"full": args.scope == "full", "scopes": [args.scope],
                "mutations": args.scope == "full", "reasons": ["explicit scope"]}
    commands = commands_for(plan)
    print(json.dumps({**plan, "commands": commands}, indent=2), flush=True)
    return 0 if args.dry_run else run(commands)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"ERROR: quality selection failed: {error}", file=sys.stderr)
        sys.exit(1)
