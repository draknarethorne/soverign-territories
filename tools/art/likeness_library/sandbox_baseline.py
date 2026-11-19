"""Refresh the disposable Sandbox baseline without inheriting Working history."""

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if not __package__:
    __package__ = "tools.art.likeness_library"

from tools.art import temporary_storage
from tools.art.likeness_library import sandbox
from tools.workflows import comfy_workflows as cw


def _implementation_hashes():
    return {
        path.name: sandbox._file_digest(path)
        for path in (pathlib.Path(__file__), pathlib.Path(sandbox.__file__))
    }


def _paths(working):
    working = pathlib.Path(working).expanduser()
    if not working.is_absolute() or not sandbox.is_sandbox_working_path(working):
        raise ValueError("baseline requires an absolute Sovereign Territories Sandbox\\Working root")
    for path in (working, working.parent, working.parent / "Source",
                 working.parent / "source-manifest.json", working.parent / "_baseline-state"):
        if sandbox._is_reparse_point(path):
            raise ValueError(f"refusing linked baseline path: {path}")
    if not working.is_dir() or not working.parent.is_dir():
        raise ValueError(f"missing sandbox Working: {working}")
    working = working.resolve(strict=True)
    if any(parent.name.casefold() == "sovereign territories" for parent in working.parents):
        raise ValueError("sandbox baseline must not be inside Production")
    return working, working.parent / "_baseline-state"


def _expected(files):
    return {name: (row["bytes"], row["sha256"]) for name, row in files.items()}


def _verify_tree(root, expected, *, excluded=()):
    actual, *_ = sandbox._tree_inventory(root, hash_files=True, excluded_roots=excluded)
    if _expected(actual) != expected:
        raise ValueError(f"baseline contents differ from the bound snapshot: {root}")


def preview(working, *, cfg=None):
    working, _ = _paths(working)
    result, plan = sandbox._full_reset_analysis(
        working, cfg=cfg, discard_working_history=True,
    )
    return {
        "schemaVersion": 1,
        "previewOnly": True,
        "resetReady": result["resetReady"],
        "resetBlockers": result["resetBlockers"],
        "workingRoot": str(working),
        "productionRoot": str(plan["production"]),
        "sourceRoot": str(plan["layout"]["source_root"]),
        "sourceNeedsRefresh": plan["layout"]["manifest_files"] != _expected(plan["production_files"]),
        "sourceFileCount": len(plan["production_files"]),
        "sourceBytes": sum(row["bytes"] for row in plan["production_files"].values()),
        "excludedCategories": list(sandbox.SANDBOX_EXCLUDED_CATEGORIES),
        "excludedStorageRoots": result["currentProduction"]["excludedStorageRoots"],
        "discardWorkingHistory": True,
        "workingBeforeReset": result["workingBeforeReset"],
        "workingEntriesToReplace": sorted(path.name for path in working.iterdir()),
        "carryForwardCounts": {},
    }


def _discard_child(state, name):
    path = state / name
    if path.parent != state or sandbox._is_reparse_point(path):
        raise ValueError(f"unsafe baseline staging child: {path}")
    if path.exists():
        # Walk before recursive removal so junctions cannot redirect cleanup.
        list(sandbox._source_files(path))
        sandbox._remove_tree(path)


def _recover_source(working, state, journal):
    if journal["phase"] != "source-publishing":
        return
    source = working.parent / "Source"
    manifest = working.parent / "source-manifest.json"
    previous = state / "source-old"
    previous_manifest = state / "manifest-old.json"
    for path in (source, manifest, previous, previous_manifest):
        if sandbox._is_reparse_point(path):
            raise ValueError(f"unsafe Source recovery path: {path}")
    if previous.exists():
        if source.exists():
            source.rename(state / "source-failed")
        previous.rename(source)
    if previous_manifest.exists():
        if manifest.exists():
            manifest.unlink()
        previous_manifest.rename(manifest)
    sandbox.validate_sandbox(working)
    journal["phase"] = "copying"
    sandbox._write_reset_journal(state / "journal.json", journal)


def _refresh_source(working, state, journal, cfg):
    _, plan = sandbox._full_reset_analysis(
        working, cfg=cfg, discard_working_history=True,
    )
    if not plan["production_files"]:
        raise ValueError("refusing an empty Production baseline")
    expected = _expected(plan["production_files"])
    if plan["layout"]["manifest_files"] == expected:
        journal["phase"] = "source-ready"
        sandbox._write_reset_journal(state / "journal.json", journal)
        return
    for name in ("source-new", "source-failed"):
        _discard_child(state, name)
    staged = state / "source-new"
    staged.mkdir()
    for relative, row in sorted(plan["production_files"].items()):
        parts = sandbox._safe_source_path(relative)
        sandbox._copy_verified_file(
            plan["production"].joinpath(*parts), staged.joinpath(*parts),
            row["bytes"], row["sha256"],
        )
    _verify_tree(staged, expected)
    latest, latest_plan = sandbox._full_reset_analysis(
        working, cfg=cfg, discard_working_history=True,
    )
    if not latest["resetReady"] or _expected(latest_plan["production_files"]) != expected:
        raise ValueError("Production/reset readiness changed during Source staging")
    manifest = {
        "schemaVersion": 1,
        "sourceRoot": str(plan["production"]),
        "snapshotRoot": "Source",
        "workingRootAtCreation": "Working",
        "excludedDirectories": latest["currentProduction"]["excludedStorageRoots"],
        "excludedCategories": list(sandbox.SANDBOX_EXCLUDED_CATEGORIES),
        "fileCount": len(expected),
        "totalBytes": sum(row["bytes"] for row in plan["production_files"].values()),
        "files": [
            {"path": relative, **row}
            for relative, row in sorted(plan["production_files"].items())
        ],
    }
    sandbox._write_json_file(state / "manifest-new.json", manifest)
    journal["phase"] = "source-publishing"
    sandbox._write_reset_journal(state / "journal.json", journal)
    try:
        (working.parent / "Source").rename(state / "source-old")
        (working.parent / "source-manifest.json").rename(state / "manifest-old.json")
        staged.rename(working.parent / "Source")
        (state / "manifest-new.json").rename(working.parent / "source-manifest.json")
        layout = sandbox.validate_sandbox(working)
        if layout["manifest_files"] != expected:
            raise ValueError("published Source differs from staged Production baseline")
    except BaseException:
        _recover_source(working, state, journal)
        raise
    journal["phase"] = "source-ready"
    sandbox._write_reset_journal(state / "journal.json", journal)


def _check_baseline(working, cfg):
    layout = sandbox.validate_sandbox(working)
    receipt_relative = (
        cw.storage_root(cfg, "reports", root=working).relative_to(working)
        / "reset-review-bundle" / "full-reset-receipt.json"
    )
    _verify_tree(working, layout["manifest_files"], excluded=(receipt_relative.as_posix(),))
    receipt = json.loads((working / receipt_relative).read_text(encoding="utf-8"))
    if receipt.get("discardWorkingHistory") is not True or receipt["carryForwardCounts"]:
        raise ValueError("Working reset receipt does not certify no-history mode")
    return layout


def check(working, run_id, *, cfg=None):
    working, state_root = _paths(working)
    cfg = cw.load_cfg() if cfg is None else cfg
    receipt_path = _receipt_path(state_root, run_id)
    if sandbox._is_reparse_point(receipt_path):
        raise ValueError(f"unsafe baseline receipt: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt["implementationSHA256"] != _implementation_hashes():
        raise ValueError("baseline implementation binding changed")
    manifest = working.parent / "source-manifest.json"
    if receipt["workingRoot"] != str(working) or receipt["sourceManifestSHA256"] != sandbox._file_digest(manifest):
        raise ValueError("baseline receipt/source binding changed")
    layout = _check_baseline(working, cfg)
    return {"checked": True, "runId": run_id, "sourceFileCount": layout["file_count"],
            "sourceBytes": layout["total_bytes"], "receipt": str(receipt_path)}


def _receipt_path(state_root, run_id):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", run_id):
        raise ValueError("invalid baseline run ID")
    path = state_root / "receipts"
    if sandbox._is_reparse_point(path):
        raise ValueError(f"unsafe baseline receipt directory: {path}")
    return path / f"{run_id}.json"


def apply(working, run_id, *, cfg=None):
    working, state_root = _paths(working)
    cfg = cw.load_cfg() if cfg is None else cfg
    receipt_path = _receipt_path(state_root, run_id)
    if receipt_path.exists() and not (state_root / "transaction").exists():
        return check(working, run_id, cfg=cfg)
    with temporary_storage.resumable_staging_directory(state_root, "transaction") as state:
        journal_path = state / "journal.json"
        list(sandbox._source_files(state))
        if receipt_path.exists() and not journal_path.exists():
            result = check(working, run_id, cfg=cfg)
            if {path.name for path in state.iterdir()} - {"manifest-old.json", "manifest-new.json"}:
                raise ValueError(f"unclassified committed baseline staging files: {state}")
            for path in state.iterdir():
                path.unlink()
            state.rmdir()
            return result
        if journal_path.exists():
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
            if journal["workingRoot"] != str(working) or journal["runId"] != run_id:
                raise ValueError("unfinished baseline transaction belongs to another root/run")
            _recover_source(working, state, journal)
        else:
            if any(state.iterdir()):
                raise ValueError(f"unclassified baseline transaction files: {state}")
            journal = {"schemaVersion": 1, "workingRoot": str(working),
                       "runId": run_id, "phase": "copying",
                       "previousSourceManifestSHA256": sandbox._file_digest(
                           working.parent / "source-manifest.json"
                       )}
            sandbox._write_reset_journal(journal_path, journal)
        if journal["phase"] == "copying":
            ready = preview(working, cfg=cfg)
            if not ready["resetReady"]:
                raise ValueError(f"baseline reset blocked: {ready['resetBlockers']}")
            journal["preview"] = ready
            sandbox._write_reset_journal(journal_path, journal)
            _refresh_source(working, state, journal, cfg)
        if journal["phase"] == "source-ready":
            temporary = cw.storage_root(cfg, "temporary", root=working)
            if temporary.parent != working or sandbox._is_reparse_point(temporary):
                raise ValueError("strict reset requires direct Working-local temporary storage")
            if temporary.exists():
                list(sandbox._source_files(temporary))
                discarded = state / "discarded-temporary"
                discarded.mkdir(exist_ok=True)
                for path in temporary.iterdir():
                    path.rename(discarded / path.name)
            journal["phase"] = "working-reset"
            sandbox._write_reset_journal(journal_path, journal)
        if journal["phase"] == "working-reset":
            sandbox.full_reset_apply(working, cfg=cfg, discard_working_history=True)
            journal["phase"] = "working-installed"
            sandbox._write_reset_journal(journal_path, journal)
        if journal["phase"] != "working-installed":
            raise ValueError(f"unknown baseline transaction phase: {journal['phase']}")
        layout = _check_baseline(working, cfg)
        if receipt_path.exists():
            check(working, run_id, cfg=cfg)
        for name in ("source-old", "source-failed", "source-new", "discarded-temporary"):
            _discard_child(state, name)
        receipt = {
            "schemaVersion": 1, "runId": run_id, "workingRoot": str(working),
            "sourceManifestSHA256": sandbox._file_digest(working.parent / "source-manifest.json"),
            "sourceFileCount": layout["file_count"], "sourceBytes": layout["total_bytes"],
            "discardWorkingHistory": True, "carryForwardCounts": {},
            "previousSourceManifestSHA256": journal["previousSourceManifestSHA256"],
            "workingBeforeReset": journal["preview"]["workingBeforeReset"],
            "replacedWorkingEntries": journal["preview"]["workingEntriesToReplace"],
            "implementationSHA256": _implementation_hashes(),
        }
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        if not receipt_path.exists():
            sandbox._write_reset_journal(receipt_path, receipt)
        for name in ("journal.json", "manifest-old.json", "manifest-new.json"):
            (state / name).unlink(missing_ok=True)
        state.rmdir()
    return {"applied": True, **check(working, run_id, cfg=cfg)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=pathlib.Path)
    parser.add_argument("--run-id")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if (args.apply or args.check) and not args.run_id:
        parser.error("--apply/--check require --run-id")
    try:
        if args.apply:
            result = apply(args.root, args.run_id)
        elif args.check:
            result = check(args.root, args.run_id)
        else:
            result = preview(args.root)
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(2, f"sandbox baseline: {error}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
