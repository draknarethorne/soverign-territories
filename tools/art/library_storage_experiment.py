#!/usr/bin/env python3
"""Preview/run isolated mixed-photo storage experiments; never mutate the supplied library."""
import argparse
import collections
import html
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
sys.path.insert(0, str(ROOT))
import image_preparation as prep
import library_backup
from likeness_library import metadata, retained_preparation as retained

RECEIPT = "experiment.json"
MODE_DIRECTORY = {"full": "f", "lean": "l"}


def selection(root, count, sources=None):
    if not 20 <= count <= 30:
        raise ValueError("experiment requires 20..30 images")
    if sources is not None:
        if pathlib.Path(sources).stat().st_size > 64 * 1024:
            raise ValueError("explicit sample list exceeds 64 KiB")
        names = json.loads(pathlib.Path(sources).read_text(encoding="utf-8"))
        if not isinstance(names, list) or len(names) != count:
            raise ValueError("--sources must list exactly --limit relative active photo paths")
        allowed = set(prep.inventory(root))
        paths = []
        for name in names:
            if not isinstance(name, str) or "\\" in name or ":" in name or ".." in name.split("/"):
                raise ValueError("unsafe explicit sample path")
            path = prep.safe_path(root, root.joinpath(*name.split("/")))
            if path not in allowed or path in paths:
                raise ValueError("explicit sample contains an unknown or duplicate active photo")
            category = path.relative_to(root).parts[0]
            if category != "Various" and (category not in ("Angels", "Sisters", "Models", "Prospects", "Potentials")
                                          or path.parent.name != "gallery"):
                raise ValueError("assigned sample photos must come from general Galleries")
            paths.append(path)
        if sum(path.relative_to(root).parts[0] == "Various" for path in paths) != count // 2:
            raise ValueError("explicit sample must balance Various and assigned Galleries")
        for category in ("Angels", "Sisters"):
            if sum(path.relative_to(root).parts[0] == category for path in paths) < 3:
                raise ValueError("explicit sample needs three Angel and three Sister core candidates")
        return paths
    various = [path for path in prep.inventory(root) if path.relative_to(root).parts[0] == "Various"]
    assigned = [path for path in prep.inventory(root)
                if path.relative_to(root).parts[0] in ("Angels", "Sisters", "Models", "Prospects", "Potentials")
                and path.parent.name == "gallery"]
    # Keep several photos of each cast identity so real core matching is exercised.
    by_owner = collections.defaultdict(list)
    for path in assigned:
        by_owner[path.parent.parent].append(path)
    chosen = []
    for category in ("Angels", "Sisters"):
        owner = next((owner for owner in sorted(by_owner) if owner.parent.name == category
                      and len(by_owner[owner]) >= 3), None)
        if owner is None:
            raise ValueError(f"experiment needs a {category} Gallery with at least three photos")
        chosen.extend(sorted(by_owner[owner])[:3])
    target = count - count // 2
    for path in sorted(assigned):
        if len(chosen) == target:
            break
        if path not in chosen and path.relative_to(root).parts[0] not in ("Angels", "Sisters"):
            chosen.append(path)
    pool = sorted(various)[:count // 2]
    if len(chosen) != target or len(pool) != count // 2:
        raise ValueError("not enough assigned/Various images for the requested balanced experiment")
    return chosen + pool


def safe_output(value):
    path = pathlib.Path(value).expanduser()
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("experiment output must be an absolute path without parent traversal")
    scratch = ROOT / "tmp"
    if scratch not in path.parents or path == scratch:
        raise ValueError("experiment output must be a named directory strictly under repository tmp")
    prep.safe_path(ROOT, path)
    result = subprocess.run(["git", "check-ignore", str(path)], cwd=ROOT, capture_output=True)
    if result.returncode:
        raise ValueError("experiment output must be git-ignored")
    evidence = (path / "f" / "Sovereign Territories Sandbox" / "Working" /
                "_likeness" / "general" / "face-evidence" / ("a" * 64 + "-" + "b" * 64 + ".png"))
    if os.name == "nt" and len(str(evidence)) >= 260:
        raise ValueError("experiment path exceeds OpenCV's Windows evidence limit; use a short output such as tmp\\s1")
    return path


def digest(path):
    return prep.sha_file(path)


def files_below(root):
    root = library_backup._snapshot_path(root)
    pending = [root]
    entries = 0
    while pending:
        for path in pending.pop().iterdir():
            entries += 1
            if entries > 32000:
                raise ValueError("experiment inventory exceeds 32,000 entries")
            prep.safe_path(root, path)
            if path.is_dir():
                pending.append(path)
            elif path.is_file():
                yield path
            else:
                raise ValueError(f"unsupported experiment entry: {path}")


def payload_inventory(root):
    root = library_backup._snapshot_path(root)
    return {path.relative_to(root).as_posix(): {"sha256": digest(path), "bytes": path.stat().st_size}
            for path in files_below(root)}


def active_inventory(root):
    result = {}
    for category in prep.CATEGORIES:
        directory = root / category
        if directory.is_dir():
            result.update({f"{category}/{name}": item for name, item in payload_inventory(directory).items()})
    return result


def tree_totals(root):
    sizes = [path.stat().st_size for path in files_below(root)]
    return {"files": len(sizes), "bytes": sum(sizes)}


def role_hashes(prepared):
    result = {}
    for row in prepared["photos"]:
        selected = row["recommendation"]["use"]
        padded = (row.get("recommendedPadded", {}).get("sha256") if selected == "original"
                  else row["variants"].get(selected, {}).get("paddedSha256"))
        result[row["source"]] = {
            "original": row["sourceSha256"], "outcome": row["outcome"], "recommendation": selected,
            "selectedPadded": padded,
            "nativeAndPreview": {name: {key: value for key, value in variant.items()
                                       if key in ("sha256", "thumbnailSha256")}
                                 for name, variant in row["variants"].items()},
        }
    return result


def execute(out, mode, command, env, phases, label):
    start = time.perf_counter()
    log = out / f"{mode}-{label}.log"
    if log.exists():
        log = out / f"{mode}-{label}-{time.time_ns()}.log"
    with log.open("xb") as stream:
        result = subprocess.run(["cmd", "/c", str(ROOT / "bin" / command[0]), *command[1:]],
                                cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    elapsed = time.perf_counter() - start
    if result.returncode:
        raise RuntimeError(f"{label} exited {result.returncode}; inspect {log}")
    phases[label] = round(elapsed, 6)


def setup(out, mode, source_root, rows):
    base = out / MODE_DIRECTORY[mode]
    sandbox_root = base / "Sovereign Territories Sandbox"
    working = sandbox_root / "Working"
    snapshot = sandbox_root / "Source"
    working.mkdir(parents=True)
    snapshot.mkdir()
    entries = []
    for path in rows:
        relative = path.relative_to(source_root)
        # Loose Review inputs emulate incoming Gallery only in this isolated experiment.
        if relative.parts[0] == "Various":
            relative = pathlib.Path("Various", "gallery", path.name)
        for root in (working, snapshot):
            target = root / relative
            prep.safe_path(root, target)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError(f"sample filename collision: {target}")
            shutil.copy2(path, target)
        entries.append({"path": relative.as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)})
    metadata.save_catalog({"schemaVersion": 1, "people": {}, "photos": {}, "actions": []},
                          working / ".likeness-library.json")
    (sandbox_root / "source-manifest.json").write_text(json.dumps({
        "schemaVersion": 1, "snapshotRoot": "Source", "workingRootAtCreation": "Working",
        "sourceRoot": str(base / "Sovereign Territories"),
        "fileCount": len(entries), "totalBytes": sum(entry["bytes"] for entry in entries), "files": entries,
    }, indent=2) + "\n", encoding="utf-8")
    inputs = base / "empty-inputs"
    inputs.mkdir()
    env = dict(os.environ)
    env["SOVEREIGN_TERRITORIES_SANDBOX_WORKING_ROOT"] = str(working)
    env["SOVEREIGN_TERRITORIES_PRODUCTION_ROOT"] = str(base / "Sovereign Territories")
    env["SOVEREIGN_TERRITORIES_INPUTS_ROOT"] = str(inputs)
    return working, env


def measure(out, mode, root, rows):
    working, env = setup(out, mode, root, rows)
    run = working / "_sandbox-state" / "trial"
    phases = {}
    common = ["sandbox-rebase.cmd", str(working), str(run), "--baseline", "working",
              "--cast-seeds", "all", "--storage-mode", mode, "--workers", "2"]
    execute(out, mode, [*common, "--dry-run"], env, phases, "preview")
    execute(out, mode, [*common, "--intake-only", "--apply"], env, phases, "intake")
    execute(out, mode, common, env, phases, "matching-preview")
    execute(out, mode, ["library-backup.cmd", "--root", str(working),
                       "--inputs", str(out / MODE_DIRECTORY[mode] / "empty-inputs"), "--full", "--apply"],
            env, phases, "preinstall-backup")
    execute(out, mode, [*common, "--apply"], env, phases, "install")
    execute(out, mode, [*common, "--check"], env, phases, "installed-check")
    plan = json.loads((run / "run.json").read_text(encoding="utf-8"))
    if plan["status"] != "applied" or len(plan["photos"]) != len(rows):
        raise ValueError("not every mixed sample reached installed publication")
    report = run / "inputs" / "_reports" / "preparation" / "all"
    prepared = prep.verify(run / "inputs", report)
    for row in plan["photos"]:
        data = retained.verify_link(working, row["destination"])
        if data is None or data["currentSha256"] != row["preparedSHA256"]:
            raise ValueError("installed retained lineage differs from selected native")
        if mode == "lean":
            if data["formatVersion"] != 2 or (data["sourceSha256"] == data["currentSha256"]
                                            and data["original"] != data["current"]):
                raise ValueError("LEAN failed to reference an unchanged native original")
    gallery_files = active_inventory(working)
    execute(out, mode, ["library-backup.cmd", "--root", str(working),
                       "--inputs", str(out / MODE_DIRECTORY[mode] / "empty-inputs"), "--full", "--apply"],
            env, phases, "installed-backup")
    backups = sorted((working / "_backup").glob("library-*"))
    snapshot = backups[-1]
    recovery = out / MODE_DIRECTORY[mode] / "Recovery"
    execute(out, mode, ["library-backup.cmd", "--restore", str(snapshot), "--destination", str(recovery)],
            env, phases, "restore-preview")
    execute(out, mode, ["library-backup.cmd", "--restore", str(snapshot), "--destination", str(recovery), "--apply"],
            env, phases, "restore")
    for row in plan["photos"]:
        if retained.verify_link(recovery / "work-root", row["destination"]) is None:
            raise ValueError("restored native/reference lineage failed verification")
    exact = {row["source"]: {"sha256": row["preparedSHA256"], "destination": row["destination"]}
             for row in plan["photos"]}
    return {
        "working": str(working), "preparation": str(report), "phases": phases,
        "preparationStatistics": prepared["statistics"], "installedFiles": len(gallery_files),
        "installedBytes": sum(item["bytes"] for item in gallery_files.values()),
        "installedInventory": gallery_files, "selected": exact,
        "restoreVerified": True, "recipe": prepared["recipe"],
        "preparationManifestSha256": digest(report / "manifest.json"),
        "runReceiptSha256": digest(run / "run.json"),
        "backupManifestSha256": digest(snapshot / "manifest.json"),
        "backup": str(snapshot), "recovery": str(recovery),
    }


def check(out):
    receipt = json.loads((out / RECEIPT).read_text(encoding="utf-8"))
    if (set(receipt["modes"]) != {"full", "lean"} or not 20 <= receipt["photos"] <= 30
            or len(receipt["sources"]) != receipt["photos"]):
        raise ValueError("experiment receipt is not a complete bounded FULL/LEAN mixed sample")
    if receipt["modes"]["full"]["selected"] != receipt["modes"]["lean"]["selected"]:
        raise ValueError("FULL/LEAN selection or routing evidence differs")
    for source, expected in {**receipt["sources"], **receipt["protected"]}.items():
        if digest(pathlib.Path(source)) != expected:
            raise ValueError(f"original experiment input changed: {source}")
    roles = {}
    for mode, value in receipt["modes"].items():
        working = pathlib.Path(value["working"])
        if working != out / MODE_DIRECTORY[mode] / "Sovereign Territories Sandbox" / "Working":
            raise ValueError("experiment receipt root differs")
        for relative, item in value["installedInventory"].items():
            path = prep.safe_path(working, working / relative)
            if digest(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
                raise ValueError(f"installed experiment artifact changed: {path}")
        if active_inventory(working) != value["installedInventory"]:
            raise ValueError("installed experiment membership changed")
        report = pathlib.Path(value["preparation"])
        if digest(report / "manifest.json") != value["preparationManifestSha256"]:
            raise ValueError("preparation receipt changed")
        prepared = prep.verify(report.parents[2], report)
        roles[mode] = role_hashes(prepared)
        if "roleHashes" in value and value["roleHashes"] != roles[mode]:
            raise ValueError("experiment role hashes differ from verified preparation")
        if (prepared["statistics"] != value["preparationStatistics"]
                or value["installedFiles"] != len(value["installedInventory"])
                or value["installedBytes"] != sum(item["bytes"] for item in value["installedInventory"].values())):
            raise ValueError("experiment statistics differ from verified artifacts")
        if digest(working / "_sandbox-state" / "trial" / "run.json") != value["runReceiptSha256"]:
            raise ValueError("installed run receipt changed")
        for source, item in value["selected"].items():
            data = retained.verify_link(working, item["destination"])
            if data is None or data["currentSha256"] != item["sha256"]:
                raise ValueError(f"installed lineage changed for {source}")
        snapshots = sorted((working / "_backup").glob("library-*"))
        if not snapshots:
            raise ValueError("experiment recovery snapshot is missing")
        snapshot = pathlib.Path(value["backup"]) if "backup" in value else snapshots[-1]
        recovery = out / MODE_DIRECTORY[mode] / "Recovery"
        prep.safe_path(working, snapshot)
        if digest(snapshot / "manifest.json") != value["backupManifestSha256"]:
            raise ValueError("experiment backup receipt changed")
        library_backup.verify_backup(snapshot)
        for item in value["selected"].values():
            if retained.verify_link(recovery / "work-root", item["destination"]) is None:
                raise ValueError("experiment materialized restore lineage changed")
        for mode_name, history in value.get("histories", {}).items():
            if mode_name not in ("compact", "collage"):
                raise ValueError("unknown history mode in experiment")
            output = working / "_reports" / "preparation-history" / mode_name
            if str(output) != history["output"] or digest(output / "manifest.json") != history["manifestSha256"]:
                raise ValueError("history experiment path/receipt changed")
            from preparation_history_bundle import check as verify_bundle
            verify_bundle(working, output)
    if roles["full"] != roles["lean"]:
        raise ValueError("FULL/LEAN native/preview/padding hashes or decisions differ")
    print("Verified both installed mixed batches and original sample hashes.")
    return receipt


def complete_history(out, receipt):
    for mode, value in receipt["modes"].items():
        working = pathlib.Path(value["working"])
        report = pathlib.Path(value["preparation"])
        value["roleHashes"] = role_hashes(prep.verify(report.parents[2], report))
        env = dict(os.environ)
        env["SOVEREIGN_TERRITORIES_SANDBOX_WORKING_ROOT"] = str(working)
        env["SOVEREIGN_TERRITORIES_PRODUCTION_ROOT"] = str(working.parent.parent / "Sovereign Territories")
        histories = value.setdefault("histories", {})
        for history_mode in ("compact", "collage"):
            output = working / "_reports" / "preparation-history" / history_mode
            command = ["preparation-history.cmd", "--root", str(working), "--report", value["preparation"],
                       "--out", str(output), "--mode", history_mode]
            if history_mode not in histories:
                reused = output.exists()
                execute(out, mode, [*command, "--dry-run"], env, value["phases"], history_mode + "-preview")
                execute(out, mode, [*command, "--apply"], env, value["phases"], history_mode + "-convert")
                manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
                histories[history_mode] = {
                    "output": str(output), "statistics": manifest["statistics"],
                    "persistedTotals": manifest["persistedTotals"], "timings": manifest["timings"],
                    "manifestSha256": digest(output / "manifest.json"),
                    "sourceReportsDeleted": 0,
                    "reusedExistingBundle": reused,
                }
            if digest(output / "manifest.json") != histories[history_mode]["manifestSha256"]:
                raise ValueError("history experiment manifest changed")
            label = history_mode + "-check"
            if not (out / f"{mode}-{label}.log").exists():
                execute(out, mode, [*command, "--check"], env, value["phases"], label)
            else:
                from preparation_history_bundle import check as verify_bundle
                verify_bundle(working, output)
        snapshot = sorted((working / "_backup").glob("library-*"))[-1]
        value["backup"] = str(snapshot)
        value["recovery"] = str(out / MODE_DIRECTORY[mode] / "Recovery")
        value["storageScopes"] = {
            "immutableSource": tree_totals(working.parent / "Source"),
            "preparationReport": tree_totals(pathlib.Path(value["preparation"])),
            "inputMirrorIncludingPreparation": tree_totals(working / "_sandbox-state" / "trial" / "inputs"),
            "installedCategories": {"files": value["installedFiles"], "bytes": value["installedBytes"]},
            "installedBackup": tree_totals(snapshot),
            "materializedRestore": tree_totals(pathlib.Path(value["recovery"])),
            "allExperimentCopiesIncludingBackupsAndHistory": tree_totals(out / MODE_DIRECTORY[mode]),
        }
    (out / RECEIPT).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    write_summary(out, receipt)


def write_summary(out, receipt):
    summary = ""
    for mode, value in receipt["modes"].items():
        relative = MODE_DIRECTORY[mode] + "/Sovereign%20Territories%20Sandbox/Working"
        summary += (
            f"<h2>{html.escape(mode.upper())}</h2><p>{value['installedFiles']} installed files; "
            f"{value['installedBytes']:,} bytes (active categories, including retained diagnostics/derivatives).</p>"
            f"<pre>{html.escape(json.dumps(value['phases'], indent=2))}</pre>"
            f"<h3>Storage scopes (overlapping, do not sum)</h3><pre>{html.escape(json.dumps(value.get('storageScopes', {}), indent=2))}</pre>"
            f'<p><a href="{relative}/_reports/library/people_gallery.html">Overview</a> | '
            f'<a href="{relative}/_reports/library/people_gallery_review.html">Review</a> | '
            f'<a href="{relative}/_reports/library/intake_runs.html">History</a></p>')
        for mode_name, history in value.get("histories", {}).items():
            summary += (
                f'<h3><a href="{relative}/_reports/preparation-history/{mode_name}/index.html">'
                f"{html.escape(mode_name.upper())}</a></h3>"
                f"<pre>{html.escape(json.dumps({key: history[key] for key in ('statistics', 'persistedTotals', 'timings')}, indent=2))}</pre>")
    (out / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Mixed storage experiment</title>'
        '<h1>Isolated mixed-photo FULL/LEAN experiment</h1>'
        '<p>Both modes use real matching on the same copied photos. No source library changes. '
        'Timings are observed sequential wall times, not an isolated causal speedup. '
        'COMPACT/COLLAGE are additional independent history copies: source reports remain, zero bytes reclaimed. '
        'Exact originals, selected native and selected padding remain lossless; diagnostics are lossy.</p>' + summary,
        encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="read-only source Working library")
    parser.add_argument("--out", required=True, help="new ignored repository tmp directory")
    parser.add_argument("--limit", type=int, default=24)
    parser.add_argument("--sources", help="optional JSON list of exactly --limit relative active source paths")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        root = pathlib.Path(args.root).resolve(strict=True)
        out = safe_output(args.out)
        if args.check:
            check(out)
            return 0
        rows = selection(root, args.limit, args.sources)
        print(f"Mixed sample: {len(rows)} photos; Various {args.limit // 2}, assigned {args.limit - args.limit // 2}.")
        for path in rows:
            print(path.relative_to(root))
        if not args.apply:
            print(f"Preview only: isolated FULL/LEAN rebase, reports, installed backup and restore under {out}.")
            return 0
        if out.exists():
            if (out / RECEIPT).exists():
                receipt = check(out)
                if set(receipt["sources"]) != {str(path) for path in rows}:
                    raise ValueError("existing experiment belongs to a different source sample; choose a new output")
                complete_history(out, receipt)
                return 0
            raise ValueError("incomplete/existing experiment output; inspect it and choose a new output")
        out.mkdir(parents=True)
        before = {str(path): digest(path) for path in rows}
        protected = {}
        for path in (root / ".likeness-library.json", *sorted((root / "_reports" / "library").glob("*.html")),
                     *sorted((root / "_sandbox-state").glob("*/run.json")),
                     *sorted((root / "_backup").glob("*/manifest.json"))):
            if path.is_file():
                protected[str(path)] = digest(path)
        values = {mode: measure(out, mode, root, rows) for mode in ("full", "lean")}
        if any(digest(pathlib.Path(path)) != expected for path, expected in {**before, **protected}.items()):
            raise ValueError("sample source changed during experiment")
        if values["full"]["selected"] != values["lean"]["selected"]:
            raise ValueError("FULL/LEAN matching destinations or selected bytes differ")
        result = {"schemaVersion": 1, "sourceRoot": str(root), "photos": len(rows),
                  "sources": before, "protected": protected, "modes": values,
                  "caveats": ["Isolated copies on the repository volume, not full B: library timing.",
                              "FULL first; shared warm model/cache and external load affect timing.",
                              "FULL/LEAN storage only; no FAST recipe, auto-prune or default adoption."]}
        (out / RECEIPT).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        complete_history(out, result)
        check(out)
        print(f"Measured end-to-end experiment: {out / 'index.html'}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(f"storage experiment failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
