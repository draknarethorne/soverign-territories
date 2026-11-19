"""Refresh or replay the Sandbox baseline without inheriting Working history."""

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


def _paths(working, *, allow_missing=False):
    working = pathlib.Path(working).expanduser()
    if not working.is_absolute() or not sandbox.is_sandbox_working_path(working):
        raise ValueError("baseline requires an absolute Sovereign Territories Sandbox\\Working root")
    for path in (working, working.parent, working.parent / "Source",
                 working.parent / "source-manifest.json", working.parent / "_baseline-state"):
        if sandbox._is_reparse_point(path):
            raise ValueError(f"refusing linked baseline path: {path}")
    if not working.parent.is_dir() or (not working.is_dir() and (not allow_missing or working.exists())):
        raise ValueError(f"missing sandbox Working: {working}")
    working = working.resolve(strict=not allow_missing)
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


def _frozen_source(working, digest, *, allow_missing=False):
    manifest = working.parent / "source-manifest.json"
    if not re.fullmatch(r"[a-f0-9]{64}", digest) or sandbox._file_digest(manifest) != digest:
        raise ValueError("frozen Source manifest does not match the requested SHA-256")
    layout = sandbox.validate_sandbox(working, allow_missing_working=allow_missing)
    if not layout["manifest_files"] or sandbox._file_digest(manifest) != digest:
        raise ValueError("frozen Source is empty or its manifest changed")
    return layout


def _frozen_paths(state_root, run_id):
    receipt = _receipt_path(state_root, run_id)
    preserved = state_root.parent / f"Working-before-{run_id}"
    for path in (receipt, preserved):
        if sandbox._is_reparse_point(path):
            raise ValueError(f"unsafe frozen replay path: {path}")
    return receipt, preserved


def frozen_preview(working, run_id, digest):
    working, state_root = _paths(working)
    receipt, preserved = _frozen_paths(state_root, run_id)
    layout = _frozen_source(working, digest)
    return {
        "previewOnly": True, "resetReady": not (receipt.exists() or preserved.exists()),
        "runId": run_id, "workingRoot": str(working), "preservedWorking": str(preserved),
        "sourceRoot": str(layout["source_root"]), "sourceManifestSHA256": digest,
        "sourceFileCount": layout["file_count"], "sourceBytes": layout["total_bytes"],
        "sourceNeedsRefresh": False, "carryForwardCounts": {},
        "workingEntriesToPreserve": sorted(path.name for path in working.iterdir()),
    }


def _verify_frozen_copy(layout, target):
    expected = layout["manifest_files"]
    _verify_tree(target, expected)
    for relative in expected:
        source = layout["source_root"] / relative
        if (target / relative).stat().st_mtime_ns != source.stat().st_mtime_ns:
            raise ValueError(f"frozen copy did not preserve modification time: {relative}")


def frozen_check(working, run_id, digest):
    working, state_root = _paths(working)
    receipt, preserved = _frozen_paths(state_root, run_id)
    data = json.loads(receipt.read_text(encoding="utf-8"))
    if (data.get("workingRoot") != str(working) or data.get("preservedWorking") != str(preserved)
            or data.get("sourceManifestSHA256") != digest or data.get("runId") != run_id
            or data.get("implementationSHA256") != _implementation_hashes() or not preserved.is_dir()):
        raise ValueError("frozen replay receipt binding changed")
    _verify_frozen_copy(_frozen_source(working, digest), working)
    return {**data, "checked": True, "receipt": str(receipt)}


def frozen_apply(working, run_id, digest):
    working, state_root = _paths(working, allow_missing=True)
    receipt, preserved = _frozen_paths(state_root, run_id)
    with temporary_storage.resumable_staging_directory(state_root, "transaction") as state:
        journal_path, staged = state / "journal.json", state / "working-new"
        if any(sandbox._is_reparse_point(path) for path in (journal_path, staged)):
            raise ValueError("unsafe frozen replay staging")
        binding = {
            "kind": "frozen-source-replay", "runId": run_id, "workingRoot": str(working),
            "preservedWorking": str(preserved), "sourceManifestSHA256": digest,
            "implementationSHA256": _implementation_hashes(),
        }
        if journal_path.exists():
            saved = json.loads(journal_path.read_text(encoding="utf-8"))
            if any(saved.get(key) != value for key, value in binding.items()):
                raise ValueError("unfinished baseline transaction belongs to another operation")
        elif receipt.exists():
            if any(state.iterdir()):
                raise ValueError("unclassified baseline staging files")
            result = frozen_check(working, run_id, digest)
            state.rmdir()
            return result
        else:
            if any(state.iterdir()) or preserved.exists() or not working.is_dir():
                raise ValueError("frozen replay requires original Working and an unused preservation path")
            saved = {**binding, "phase": "copying"}
            sandbox._write_reset_journal(journal_path, saved)

        layout = _frozen_source(working, digest, allow_missing=preserved.is_dir())
        if saved["phase"] == "copying":
            if preserved.exists() or not working.is_dir():
                raise ValueError("original Working changed before frozen replay staging")
            if staged.exists():
                _discard_child(state, staged.name)
            staged.mkdir()
            for relative, (size, checksum) in sorted(layout["manifest_files"].items()):
                sandbox._copy_verified_file(layout["source_root"] / relative, staged / relative, size, checksum)
            saved["phase"] = "publishing"
            sandbox._write_reset_journal(journal_path, saved)
        if saved["phase"] != "publishing":
            raise ValueError("unknown frozen replay phase")
        if preserved.exists() and not preserved.is_dir():
            raise ValueError("invalid frozen replay preservation path")
        if staged.exists():
            _verify_frozen_copy(layout, staged)
            if not preserved.exists():
                working.rename(preserved)
            elif working.exists():
                raise ValueError("both original Working and its preservation path exist")
            try:
                staged.rename(working)
            except OSError:
                if not working.exists():
                    preserved.rename(working)
                raise
        if not preserved.is_dir():
            raise ValueError("frozen replay is missing its preserved Working")
        _verify_frozen_copy(layout, working)
        data = {
            **binding, "schemaVersion": 1, "sourceFileCount": layout["file_count"],
            "sourceBytes": layout["total_bytes"], "carryForwardCounts": {},
        }
        if not receipt.exists():
            receipt.parent.mkdir(parents=True, exist_ok=True)
            sandbox._write_reset_journal(receipt, data)
        elif json.loads(receipt.read_text(encoding="utf-8")) != data:
            raise ValueError("frozen replay receipt changed")
        journal_path.unlink()
        state.rmdir()
    return {**data, "applied": True, "checked": True, "receipt": str(receipt)}


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
            if (journal.get("kind") == "frozen-source-replay"
                    or journal["workingRoot"] != str(working) or journal["runId"] != run_id):
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
    parser.add_argument("--frozen-source-sha256", help="replay the exact existing Source; preserve old Working")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if (args.apply or args.check or args.frozen_source_sha256) and not args.run_id:
        parser.error("--apply/--check and frozen Source require --run-id")
    try:
        if args.frozen_source_sha256:
            action = frozen_apply if args.apply else frozen_check if args.check else frozen_preview
            result = action(args.root, args.run_id, args.frozen_source_sha256)
        elif args.apply:
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
