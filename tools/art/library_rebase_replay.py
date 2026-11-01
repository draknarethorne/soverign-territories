#!/usr/bin/env python3
"""Replay the preserved FULL baseline in an isolated, fresh-cache LEAN sandbox.

Preview is read-only. Apply resumes successful stages, stops before installation
on any unexplained comparison, and never modifies or removes the supplied FULL
run. Completed apply is an independent check, not another reprocessing run.
"""
import argparse
import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
sys.path.insert(0, str(ROOT))
import image_preparation as prep
import library_backup
from library_storage_experiment import role_hashes
from likeness_library import metadata, retained_preparation as retained, sandbox, verification_reads
from likeness_library.policy import effective_settings

BASELINE = pathlib.Path(
    r"B:\Sovereign Territories Sandbox\Working\_sandbox-state\fresh-v23-20261029"
)
OUT = ROOT / "tmp" / "r4"
EXPECTED = {
    "run": "b08cfb0d5346297ed88bee836d77b91ed719eb7c3ed7adcb77ae7ca1450c50bf",
    "catalog": "9293fce4863cfdb2264cf48c6e06b8ef5bcb002538ef4a1d265eb53413a6efaa",
    "backup": "b73ced418f289a0109899dd8601b368b2b55fa6337bcbf9f327b4e27c8280ccf",
    "inherited": "0b2d782dc634b0390f4a2cbcc890c387d0cce1572a9bcb66691fdb8d81215c37",
}
MAX_INPUTS = 4000
MAX_BYTES = 2 * 1024**3
MAX_ENTRIES = 600000
RECEIPT = "replay.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    pending = path.with_suffix(path.suffix + ".pending")
    pending.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)


def no_links(path):
    path = pathlib.Path(path)
    for component in (path, *path.parents):
        if sandbox._is_reparse_point(component):
            raise ValueError(f"linked replay path: {component}")


def digest(path):
    no_links(path)
    return prep.sha_file(library_backup._snapshot_path(path))


def safe_path(root, relative):
    no_links(root)
    parts = sandbox._safe_source_path(relative)
    return prep.safe_path(root, root.joinpath(*parts))


def output_path(value):
    path = pathlib.Path(value).expanduser()
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("output must be an absolute path without traversal")
    prep.safe_path(ROOT, path)
    if path != OUT and OUT not in path.parents:
        raise ValueError("replay output must be tmp\\r4 or a named directory beneath it")
    if subprocess.run(["git", "check-ignore", str(path)], cwd=ROOT,
                      capture_output=True).returncode:
        raise ValueError("replay output must be git-ignored")
    evidence = path / "Sovereign Territories Sandbox" / "Working" / "_likeness" / "general" / "face-evidence"
    if os.name == "nt" and len(str(evidence / ("a" * 64 + "-" + "b" * 64 + ".png"))) >= 260:
        raise ValueError("output is too long for OpenCV evidence; use tmp\\r4")
    return path


def inventory(root, *, hashes=True):
    """Use the backup extended-path adapter, refusing links before traversal."""
    no_links(root)
    root = library_backup._snapshot_path(root)
    result = {}
    pending = [root]
    count = 0
    while pending:
        directory = pending.pop()
        if sandbox._is_reparse_point(directory):
            raise ValueError(f"linked replay directory: {directory}")
        for path in directory.iterdir():
            count += 1
            if count > MAX_ENTRIES:
                raise ValueError("replay inventory exceeds bounded entry count")
            if sandbox._is_reparse_point(path):
                raise ValueError(f"linked replay entry: {path}")
            if path.is_dir():
                pending.append(path)
            elif path.is_file():
                item = {"bytes": path.stat().st_size}
                if hashes:
                    item["sha256"] = prep.sha_file(path)
                result[path.relative_to(root).as_posix()] = item
                if hashes and len(result) % 8192 == 0:
                    print(f"inventory {len(result)} files: {root}", flush=True)
            else:
                raise ValueError(f"unsupported replay entry: {path}")
    return result


def categories(root):
    result = {}
    for category in prep.CATEGORIES:
        directory = root / category
        if directory.is_dir():
            result.update({category + "/" + key: item
                           for key, item in inventory(directory).items()})
    return result


def totals(root):
    entries = inventory(root, hashes=False)
    return {"files": len(entries), "bytes": sum(item["bytes"] for item in entries.values())}


def verify_inventory(root, expected):
    if inventory(root) != expected:
        raise ValueError(f"persisted exact inventory changed: {root}")


def require_hash(path, expected):
    if digest(path) != expected:
        raise ValueError(f"protected checksum mismatch: {path}")


def baseline_inputs(baseline, intake):
    inputs = intake.get("inputs")
    if intake.get("schemaVersion") != 1 or not isinstance(inputs, dict) or not 1 <= len(inputs) <= MAX_INPUTS:
        raise ValueError("baseline intake must contain 1..4000 unique original inputs")
    rows = []
    seen = set()
    total = 0
    for relative, expected in sorted(inputs.items()):
        path = safe_path(baseline / "inputs", relative)
        if relative.casefold() in seen or not re.fullmatch(r"[a-f0-9]{64}", str(expected)):
            raise ValueError("case-colliding input or invalid original checksum")
        seen.add(relative.casefold())
        require_hash(path, expected)
        size = path.stat().st_size
        total += size
        if total > MAX_BYTES:
            raise ValueError("baseline originals exceed the 2 GiB bound")
        rows.append({"path": relative, "bytes": size, "sha256": expected})
    return rows


def inspect_baseline(baseline):
    prep.safe_path(baseline.parent, baseline)
    run = load(baseline / "run.json")
    if run.get("status") != "applied" or run.get("previousLocalCatalog") is not False:
        raise ValueError("replay requires the applied baseline with an inherited catalogue")
    working = pathlib.Path(run["workingRoot"])
    if baseline.parent.parent != working:
        raise ValueError("baseline does not belong to its recorded Working root")
    backup = working / "_backup" / "library-20261029-235003"
    protected = {
        str(baseline / "run.json"): EXPECTED["run"],
        str(working / ".likeness-library.json"): EXPECTED["catalog"],
        str(backup / "manifest.json"): EXPECTED["backup"],
        str(metadata.CATALOG_PATH): EXPECTED["inherited"],
    }
    if run.get("sourceCatalogSHA256") != EXPECTED["inherited"]:
        raise ValueError("baseline inherited catalogue identity differs")
    for name, expected in protected.items():
        require_hash(pathlib.Path(name), expected)
    intake = load(baseline / "intake.json")
    report = baseline / "inputs" / "_reports" / "preparation" / "all"
    require_hash(report / "manifest.json", intake["preparationManifestSHA256"])
    rows = baseline_inputs(baseline, intake)
    if len(rows) != run["preparation"]["inputCount"] or len(rows) != 3072:
        raise ValueError("replay must account for all 3072 baseline inputs")
    if effective_settings(metadata.cw.load_cfg(), run["policy"]) != run["settings"]:
        raise ValueError("current effective settings differ from the preserved baseline")
    for path in (baseline / "intake.json", report / "manifest.json",
                 working.parent / "source-manifest.json"):
        protected[str(path)] = digest(path)
    return run, rows, protected, backup


def locations(out):
    working = out / "Sovereign Territories Sandbox" / "Working"
    return working, working.parent / "Source", working / "_sandbox-state" / "replay"


def environment(out, working):
    env = dict(os.environ)
    env["SOVEREIGN_TERRITORIES_SANDBOX_WORKING_ROOT"] = str(working)
    env["SOVEREIGN_TERRITORIES_PRODUCTION_ROOT"] = str(out / "Sovereign Territories")
    env["SOVEREIGN_TERRITORIES_INPUTS_ROOT"] = str(out / "empty-inputs")
    env["ST_INTAKE_THREADS"] = "4"
    return env


def reproducible_runtime(workers):
    cores = os.cpu_count() or 1
    if workers != 3 or cores // workers != 4:
        raise ValueError("verified replay requires three workers with four threads each on this 12-thread host")
    return {"workers": workers, "logicalProcessors": cores, "threadsPerWorker": 4}


def setup(out, state, rows, baseline):
    working, source, run = locations(out)
    for root in (working, source, out / "empty-inputs"):
        root.mkdir(parents=True, exist_ok=True)
    for index, row in enumerate(rows, 1):
        original = safe_path(baseline / "inputs", row["path"])
        for root in (source, working):
            target = safe_path(root, row["path"])
            if target.exists():
                require_hash(target, row["sha256"])
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, target)
                require_hash(target, row["sha256"])
        if index % 256 == 0:
            print(f"copy {index}/{len(rows)}", flush=True)
    require_hash(metadata.CATALOG_PATH, EXPECTED["inherited"])
    catalog = working / ".likeness-library.json"
    if catalog.exists():
        require_hash(catalog, EXPECTED["inherited"])
    else:
        shutil.copy2(metadata.CATALOG_PATH, catalog)
    manifest = {
        "schemaVersion": 1, "snapshotRoot": "Source", "workingRootAtCreation": "Working",
        "sourceRoot": str(out / "Sovereign Territories"), "fileCount": len(rows),
        "totalBytes": sum(row["bytes"] for row in rows), "files": rows,
    }
    manifest_path = working.parent / "source-manifest.json"
    if manifest_path.exists() and load(manifest_path) != manifest:
        raise ValueError("existing replay source manifest differs")
    if not manifest_path.exists():
        write(manifest_path, manifest)
    sandbox.validate_sandbox(working)
    run.mkdir(parents=True, exist_ok=True)
    policy_path = run / "policy.json"
    if policy_path.exists() and load(policy_path) != state["policy"]:
        raise ValueError("existing replay policy differs")
    if not policy_path.exists():
        write(policy_path, state["policy"])
    state["sourceManifestSHA256"] = digest(manifest_path)
    state["setupComplete"] = True
    write(out / RECEIPT, state)


def execute(out, state, env, label, command, *, repeat=False):
    if label in state["stages"] and not repeat:
        return
    started = time.perf_counter()
    log = out / f"{label}-{time.time_ns()}.log"
    print(f"phase {label}; log {log}", flush=True)
    record = {"command": command, "log": str(log), "startedAt": time.time(),
              "status": "running"}
    state["latestPhase"] = label
    state["attempts"].append(record)
    write(out / RECEIPT, state)
    try:
        with log.open("xb") as stream:
            result = subprocess.run(
                ["cmd", "/c", str(ROOT / "bin" / command[0]), *command[1:]],
                cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT,
            )
        record["exitCode"] = result.returncode
        record["seconds"] = round(time.perf_counter() - started, 6)
        record["status"] = "complete" if result.returncode == 0 else "failed"
        if result.returncode:
            raise RuntimeError(f"{label} exited {result.returncode}; inspect {log}")
        record["logSHA256"] = digest(log)
        state["stages"][label] = dict(record)
    finally:
        write(out / RECEIPT, state)
    print(f"complete {label}: {record['seconds']:.3f}s", flush=True)


def compare_roles(expected, actual):
    """Role hashes omit only FULL's alternative padded images, never native roles."""
    expected_roles, actual_roles = role_hashes(expected), role_hashes(actual)
    if expected_roles != actual_roles:
        keys = sorted(set(expected_roles) | set(actual_roles))
        differences = [key for key in keys if expected_roles.get(key) != actual_roles.get(key)]
        return {"equal": False, "differingSources": differences,
                "expected": {key: expected_roles.get(key) for key in differences},
                "actual": {key: actual_roles.get(key) for key in differences}}
    return {"equal": True, "sources": len(expected_roles),
            "rolesSHA256": hashlib.sha256(json.dumps(expected_roles, sort_keys=True).encode()).hexdigest()}


def selections(plan):
    rows = plan["photos"]
    result = {row["source"]: {"sha256": row["preparedSHA256"], "destination": row["destination"]}
              for row in rows}
    if len(result) != len(rows):
        raise ValueError("duplicate matching source")
    return result


def compare_matching(expected, actual):
    if actual["policy"] != expected["policy"] or actual["settings"] != expected["settings"]:
        raise ValueError("fresh matching policy/settings differ from FULL baseline")
    if actual.get("castSeedPolicy") != expected.get("castSeedPolicy"):
        raise ValueError("fresh matching seed mode differs")
    before, after = selections(expected), selections(actual)
    differences = [key for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)]
    return {"equal": not differences, "sources": len(after), "differingSources": differences,
            "expected": {key: before.get(key) for key in differences},
            "actual": {key: after.get(key) for key in differences}}


def record_preparation_block(out, state, expected, actual):
    """Keep the exact gate closed while recording the size of pixel differences."""
    import numpy as np
    from PIL import Image

    working, _, run = locations(out)
    before_root = pathlib.Path(state["baseline"]) / "inputs" / "_reports" / "preparation" / "all"
    after_root = run / "inputs" / "_reports" / "preparation" / "all"
    before = {row["source"]: row for row in expected["photos"]}
    after = {row["source"]: row for row in actual["photos"]}
    differences = []
    selected = []
    role_counts = {}
    for source in state["preparationComparison"]["differingSources"]:
        old, new = before[source], after[source]
        use = old["recommendation"]["use"]
        if (use not in ("original", "none") and use in old["variants"] and use in new["variants"]
                and old["variants"][use]["sha256"] != new["variants"][use]["sha256"]):
            selected.append(source)
        for role in sorted(set(old["variants"]) & set(new["variants"])):
            previous, current = old["variants"][role], new["variants"][role]
            if previous["sha256"] == current["sha256"]:
                continue
            with Image.open(safe_path(before_root, previous["path"])) as image:
                first = np.asarray(image.convert("RGB")).astype(np.int16)
            with Image.open(safe_path(after_root, current["path"])) as image:
                second = np.asarray(image.convert("RGB")).astype(np.int16)
            item = {"source": source, "role": role, "selected": role == use,
                    "expectedSHA256": previous["sha256"], "actualSHA256": current["sha256"]}
            if first.shape != second.shape:
                item["shapeChanged"] = True
            else:
                delta = np.abs(first - second)
                item.update({
                    "changedPixels": int(np.any(delta != 0, axis=2).sum()),
                    "totalPixels": int(first.shape[0] * first.shape[1]),
                    "maximumChannelDifference": int(delta.max()),
                    "meanAbsoluteChannelDifference": float(delta.mean()),
                })
            differences.append(item)
            role_counts[role] = role_counts.get(role, 0) + 1
    blocker = {
        "status": "blocked-preparation", "sources": len(before),
        "differingSources": len(state["preparationComparison"]["differingSources"]),
        "originalsEqual": {key: row["sourceSha256"] for key, row in before.items()} ==
                          {key: row["sourceSha256"] for key, row in after.items()},
        "recipesEqual": expected["recipe"] == actual["recipe"],
        "recommendationsEqual": {key: row["recommendation"]["use"] for key, row in before.items()} ==
                                {key: row["recommendation"]["use"] for key, row in after.items()},
        "outcomesEqual": {key: row["outcome"] for key, row in before.items()} ==
                         {key: row["outcome"] for key, row in after.items()},
        "selectedNativeDifferences": selected,
        "selectedPaddingDifferences": sum(
            state["preparationComparison"]["expected"][key]["selectedPadded"] !=
            state["preparationComparison"]["actual"][key]["selectedPadded"]
            for key in state["preparationComparison"]["differingSources"]
        ),
        "variantDifferenceCounts": role_counts, "variantPixelDifferences": differences,
        "interpretation": "Sparse low-amplitude reconstruction/eraser pixel differences propagate into "
                          "enhancement/preview/padding hashes. Numerical inference variation is a hypothesis, "
                          "not a verified cause. No gate tolerance, output replacement or installation allowed.",
        "matchingStarted": False, "installed": False,
    }
    write(out / "preparation-blocker.json", blocker)
    state["blockerSHA256"] = digest(out / "preparation-blocker.json")
    state["preparationManifestSHA256"] = digest(after_root / "manifest.json")
    state["status"] = "blocked-preparation"
    state["blockedAt"] = time.time()
    state["storageScopesAtBlock"] = {
        "baselineInstalledCategories": {
            "files": len(state["baselineInstalledInventory"]),
            "bytes": sum(row["bytes"] for row in state["baselineInstalledInventory"].values()),
        },
        "immutableReplaySource": totals(working.parent / "Source"),
        "preparationReport": totals(after_root), "inputMirrorIncludingPreparation": totals(run / "inputs"),
    }
    check_protected(state)
    state["protectedVerifiedAt"] = time.time()
    write(out / RECEIPT, state)
    summary = {key: value for key, value in blocker.items()
               if key not in ("selectedNativeDifferences", "variantPixelDifferences")}
    summary["selectedNativeDifferenceCount"] = len(selected)
    summary["stagesSeconds"] = {key: row["seconds"] for key, row in state["stages"].items()}
    summary["storageScopesOverlappingDoNotSum"] = state["storageScopesAtBlock"]
    (out / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Replay blocked before matching</title>'
        '<h1>Exact preparation comparison blocked installation</h1>'
        '<p>All 3072 preparation outcomes completed; matching, installation and recovery were NOT attempted. '
        'Protected FULL source, installed category and backup inventories verified unchanged. '
        'Observed wall time is not a causal speedup comparison; volumes and load differ.</p>'
        '<p><a href="preparation-blocker.json">Exact pixel-difference evidence</a> | '
        '<a href="replay.json">Replay receipt, all differing source roles and stage timings</a></p><pre>'
        + html.escape(json.dumps(summary, indent=2)) + "</pre>", encoding="utf-8")


def verify_lineage(root, plan):
    with verification_reads.session(root, label="replay lineage"):
        for row in plan["photos"]:
            current = safe_path(root, row["destination"])
            link = retained.verify_link(root, row["destination"])
            if link is None or link["currentSha256"] != row["preparedSHA256"]:
                raise ValueError(f"missing/exact retained lineage mismatch: {current}")


def verify_recovery(snapshot, recovery, *, rebuilt_reports=None):
    manifest = load(snapshot / "manifest.json")
    rows = [*manifest["entries"], *manifest.get("regenerable", [])]
    for row in rows:
        relative = row["backup"].replace("\\", "/")
        target = safe_path(recovery, relative)
        expected = {"bytes": row["size"], "sha256": row["sha256"]}
        report_prefix = "work-root/_reports/"
        if rebuilt_reports is not None and relative.startswith(report_prefix):
            report = relative[len(report_prefix):]
            if (report.startswith(("library/", "artists/"))
                    or report == "comparisons/pairings/angel-prospect-candidates.md"):
                if report not in rebuilt_reports:
                    raise ValueError(f"rebuilt report missing from sealed inventory: {report}")
                expected = rebuilt_reports[report]
        if target.stat().st_size != expected["bytes"]:
            raise ValueError(f"restored file size differs: {target}")
        require_hash(target, expected["sha256"])
    return {"manifestSHA256": digest(snapshot / "manifest.json"),
            "files": len(rows), "bytes": sum(row["size"] for row in rows),
            "originalReports": rebuilt_reports is None}


def viewers(root):
    required = [
        root / "_reports" / "library" / name
        for name in ("people_gallery.html", "people_gallery_review.html", "intake_runs.html")
    ]
    required += [root / "_reports" / "artists" / name
                 for name in ("artists_gallery.html", "artists_gallery_review.html", "intake_runs.html")]
    for path in required:
        prep.safe_path(root, path)
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"missing generated viewer: {path}")
    return {path.relative_to(root).as_posix(): digest(path) for path in required}


def check_protected(state):
    for path, expected in state["protected"].items():
        require_hash(pathlib.Path(path), expected)
    baseline = pathlib.Path(state["baseline"])
    baseline_inputs(baseline, load(baseline / "intake.json"))
    if categories(pathlib.Path(state["baselineWorking"])) != state["baselineInstalledInventory"]:
        raise ValueError("protected FULL installed category inventory changed")
    verify_inventory(pathlib.Path(state["baselineWorking"]).parent / "Source",
                     state["baselineSourceInventory"])
    verify_inventory(pathlib.Path(state["baselineBackup"]), state["baselineBackupInventory"])


def check(out):
    state = load(out / RECEIPT)
    if state.get("schemaVersion") != 1 or state.get("status") != "complete" or state.get("out") != str(out):
        raise ValueError("replay is incomplete or belongs to another output")
    baseline = pathlib.Path(state["baseline"])
    original, rows, protected, _ = inspect_baseline(baseline)
    if protected != state["protected"] or rows != state["inputs"] or len(rows) != 3072:
        raise ValueError("persisted baseline identity/input membership differs")
    check_protected(state)
    working, source, run = locations(out)
    sandbox.validate_sandbox(working)
    require_hash(working.parent / "source-manifest.json", state["sourceManifestSHA256"])
    for row in rows:
        require_hash(safe_path(source, row["path"]), row["sha256"])
    expected = prep.verify(baseline / "inputs", baseline / "inputs" / "_reports" / "preparation" / "all")
    prepared = prep.verify(run / "inputs", run / "inputs" / "_reports" / "preparation" / "all")
    if compare_roles(expected, prepared) != state["preparationComparison"]:
        raise ValueError("persisted preparation comparison differs")
    plan = load(run / "run.json")
    require_hash(run / "run.json", state["runSHA256"])
    if plan.get("status") != "applied" or compare_matching(original, plan) != state["matchingComparison"]:
        raise ValueError("persisted matching/publication comparison differs")
    verify_lineage(working, plan)
    if categories(working) != state["installedInventory"]:
        raise ValueError("installed category membership/content changed")
    if viewers(working) != state["viewers"]:
        raise ValueError("installed viewer outputs changed")
    verify_inventory(working / "_reports" / "library", state["installedReports"]["general"])
    verify_inventory(working / "_reports" / "artists", state["installedReports"]["artists"])
    snapshot = pathlib.Path(state["installedBackup"])
    prep.safe_path(working, snapshot)
    require_hash(snapshot / "manifest.json", state["backupManifestSHA256"])
    library_backup.verify_backup(snapshot)
    recovery = out / "Recovery"
    restored = recovery / "work-root"
    recovery_check = verify_recovery(snapshot, recovery, rebuilt_reports=state["restoredReports"])
    if state["ordinaryRestoreVerification"] != {**recovery_check, "originalReports": True}:
        raise ValueError("original exact-restore proof differs from the verified backup")
    verify_lineage(recovery / "work-root", plan)
    if viewers(recovery / "work-root") != state["restoredViewers"]:
        raise ValueError("rebuilt recovery viewers changed")
    if categories(recovery / "work-root") != state["restoredInventory"]:
        raise ValueError("restored category content changed")
    if state["restoredInventory"] != state["installedInventory"]:
        raise ValueError("recovery categories do not exactly reproduce installed categories")
    verify_inventory(restored / "_reports", state["restoredReports"])
    env = environment(out, working)
    command = common_command(working, run, state["workers"]) + ["--check"]
    result = subprocess.run(
        ["cmd", "/c", str(ROOT / "bin" / command[0]), *command[1:]], cwd=ROOT, env=env,
        capture_output=True, text=True,
    )
    if result.returncode:
        raise ValueError("independent installed --check failed: " + result.stdout[-8000:] + result.stderr[-8000:])
    print("Verified: 3072 input roles, fresh matching, publication, backup, ordinary restore and viewers.", flush=True)
    return state


def common_command(working, run, workers):
    return ["sandbox-rebase.cmd", str(working), str(run), "--baseline", "source",
            "--cast-seeds", "core", "--workers", str(workers), "--policy", str(run / "policy.json")]


def backup_stage(out, state, env, working, label):
    if label in state:
        snapshot = pathlib.Path(state[label])
        library_backup.verify_backup(snapshot)
        return snapshot
    before_key = label + "ExistingSnapshots"
    if before_key not in state:
        state[before_key] = [str(path) for path in (working / "_backup").glob("library-*")]
        write(out / RECEIPT, state)
    before = {pathlib.Path(path) for path in state[before_key]}
    command = ["library-backup.cmd", "--root", str(working), "--inputs", str(out / "empty-inputs"), "--full"]
    execute(out, state, env, label + "-preview", command)
    execute(out, state, env, label, command + ["--apply"])
    candidates = set((working / "_backup").glob("library-*")) - before
    if len(candidates) != 1:
        raise ValueError("cannot identify the one new default recovery backup; preserve evidence and inspect")
    snapshot = candidates.pop()
    library_backup.verify_backup(snapshot)
    state[label] = str(snapshot)
    write(out / RECEIPT, state)
    return snapshot


def rebuild_recovery_viewers(out, state, restored):
    run = restored / "_sandbox-state" / "replay"
    env = environment(out, restored)
    gallery = ["people-gallery.cmd", "--root", str(restored), "--cache", str(run / "likeness-cache.json"),
               "--policy", str(run / "policy.json"), "--reports-only"]
    execute(out, state, env, "restore-reports-preview", gallery + ["--dry-run"])
    execute(out, state, env, "restore-reports", gallery + ["--apply"])
    artists = ["artists-gallery.cmd", "--root", str(restored), "--cache", str(run / "likeness-cache.json")]
    execute(out, state, env, "restore-artists-preview", artists + ["--dry-run"])
    execute(out, state, env, "restore-artists-viewers", artists + ["--apply"])


def write_summary(out, state):
    working, _, _ = locations(out)
    rel = working.relative_to(out).as_posix()
    links = " | ".join(
        f'<a href="{html.escape(rel)}/_reports/library/{name}">{label}</a>'
        for label, name in (("Overview", "people_gallery.html"), ("Review", "people_gallery_review.html"),
                            ("History", "intake_runs.html"))
    )
    payload = {
        "status": state["status"], "preparationComparison": state["preparationComparison"],
        "matchingComparison": state["matchingComparison"],
        "stagesSeconds": {key: row["seconds"] for key, row in state["stages"].items()},
        "storageScopesOverlappingDoNotSum": state["storageScopes"],
    }
    (out / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Full baseline replay</title>'
        '<h1>Isolated optimized full baseline replay</h1>'
        '<p>FULL preserved unchanged. Timings are observed sequential wall times on different volumes '
        'and under shared machine load; no causal speedup versus undocumented old wall time is claimed. '
        'Storage scopes overlap: do not sum. Hot recovery backups explicitly retain FULL payloads: '
        'measured derivative omission saved space but regressed creation/restore speed. '
        'LEAN preparation evidence remains independent of the backup payload policy. '
        'Ordinary materialized restore is verified before explicit viewer rebuilds.</p>' + links +
        '<pre>' + html.escape(json.dumps(payload, indent=2)) + "</pre>", encoding="utf-8")


def apply(out, baseline, workers):
    runtime = reproducible_runtime(workers)
    original, rows, protected, baseline_backup = inspect_baseline(baseline)
    if out.exists() and (out / RECEIPT).is_file():
        state = load(out / RECEIPT)
        if (state.get("baseline") != str(baseline) or state.get("out") != str(out)
                or state.get("inputs") != rows or state.get("protected") != protected
                or state.get("policy") != original["policy"]):
            raise ValueError("existing replay belongs to a different baseline/output")
        if state.get("schemaVersion") != 1:
            raise ValueError("unsupported replay receipt schema")
        if state.get("preparationRuntime") != runtime:
            raise ValueError("saved replay runtime differs; preserve it and use a new isolated output")
        if state.get("status") == "complete":
            return check(out)
        if state["workers"] != workers:
            raise ValueError("resume requires the original worker count")
        check_protected(state)
    else:
        if out.exists() and any(out.iterdir()):
            raise ValueError("existing output has no replay receipt; preserve it and choose a new output")
        out.mkdir(parents=True, exist_ok=True)
        state = {
            "schemaVersion": 1, "status": "incomplete", "baseline": str(baseline), "out": str(out),
            "baselineWorking": original["workingRoot"], "policy": original["policy"], "workers": workers,
            "preparationRuntime": runtime,
            "inputs": rows, "protected": protected, "stages": {}, "attempts": [],
            "baselineInstalledInventory": categories(pathlib.Path(original["workingRoot"])),
            "baselineSourceInventory": inventory(pathlib.Path(original["workingRoot"]).parent / "Source"),
            "baselineBackupInventory": inventory(baseline_backup),
            "baselineBackup": str(baseline_backup),
            "startedAt": time.time(),
        }
        write(out / RECEIPT, state)
    working, source, run = locations(out)
    if not state.get("setupComplete"):
        setup(out, state, rows, baseline)
    env = environment(out, working)
    common = common_command(working, run, workers)
    execute(out, state, env, "inventory-preview", common + ["--dry-run"])
    if "intake" not in state["stages"] and (run / "likeness-cache.json").exists():
        raise ValueError("fresh replay unexpectedly contains an embedding cache before intake")
    execute(out, state, env, "intake", common + ["--intake-only", "--apply"])
    report = run / "inputs" / "_reports" / "preparation" / "all"
    prepared = prep.verify(run / "inputs", report)
    expected = prep.verify(baseline / "inputs", baseline / "inputs" / "_reports" / "preparation" / "all")
    state["preparationComparison"] = compare_roles(expected, prepared)
    write(out / RECEIPT, state)
    if not state["preparationComparison"]["equal"]:
        record_preparation_block(out, state, expected, prepared)
        raise ValueError("preparation roles differ; retained exact evidence in replay.json; installation prohibited")
    if prepared.get("storageMode", "full") != "lean":
        raise ValueError("new default did not select LEAN storage")
    execute(out, state, env, "matching-preview", common)
    plan = load(run / "run.json")
    state["matchingComparison"] = compare_matching(original, plan)
    write(out / RECEIPT, state)
    if not state["matchingComparison"]["equal"]:
        raise ValueError("fresh matching differs (possibly historical curation overlays); evidence retained; installation prohibited")
    if not plan.get("embeddingCacheStartedEmpty"):
        raise ValueError("matching did not start with a fresh embedding cache")
    backup_stage(out, state, env, working, "preinstallBackup")
    execute(out, state, env, "install", common + ["--apply"])
    execute(out, state, env, "installed-check", common + ["--check"])
    plan = load(run / "run.json")
    if plan.get("status") != "applied":
        raise ValueError("replay did not reach applied publication")
    verify_lineage(working, plan)
    artists = ["artists-gallery.cmd", "--root", str(working), "--cache", str(run / "likeness-cache.json")]
    execute(out, state, env, "artists-preview", artists + ["--dry-run"])
    execute(out, state, env, "artists-viewers", artists + ["--apply"])
    state["viewers"] = viewers(working)
    state["installedReports"] = {
        "general": inventory(working / "_reports" / "library"),
        "artists": inventory(working / "_reports" / "artists"),
    }
    state["installedInventory"] = categories(working)
    state["runSHA256"] = digest(run / "run.json")
    snapshot = backup_stage(out, state, env, working, "installedBackup")
    state["backupManifestSHA256"] = digest(snapshot / "manifest.json")
    recovery = out / "Recovery"
    restore = ["library-backup.cmd", "--restore", str(snapshot), "--destination", str(recovery)]
    execute(out, state, env, "restore-preview", restore)
    execute(out, state, env, "restore", restore + ["--apply"])
    restored = recovery / "work-root"
    if "ordinaryRestoreVerification" not in state:
        state["ordinaryRestoreVerification"] = verify_recovery(snapshot, recovery)
        write(out / RECEIPT, state)
    else:
        resumed = verify_recovery(snapshot, recovery, rebuilt_reports=inventory(restored / "_reports"))
        if state["ordinaryRestoreVerification"] != {**resumed, "originalReports": True}:
            raise ValueError("resumed recovery differs from the original exact-restore proof")
    verify_lineage(restored, plan)
    if categories(restored) != state["installedInventory"]:
        raise ValueError("ordinary restore did not exactly reproduce installed categories")
    rebuild_recovery_viewers(out, state, restored)
    verify_lineage(restored, plan)
    state["restoredViewers"] = viewers(restored)
    state["restoredInventory"] = categories(restored)
    if state["restoredInventory"] != state["installedInventory"]:
        raise ValueError("viewer rebuild changed restored category content")
    state["restoredReports"] = inventory(restored / "_reports")
    state["storageScopes"] = {
        "baselineInstalledCategories": {"files": len(state["baselineInstalledInventory"]),
                                       "bytes": sum(row["bytes"] for row in state["baselineInstalledInventory"].values())},
        "baselineFullBackup": totals(baseline_backup),
        "immutableSource": totals(source), "preparationReport": totals(report),
        "inputMirrorIncludingPreparation": totals(run / "inputs"),
        "installedCategories": {"files": len(state["installedInventory"]),
                                "bytes": sum(row["bytes"] for row in state["installedInventory"].values())},
        "preinstallFullHotBackup": totals(pathlib.Path(state["preinstallBackup"])),
        "installedFullHotBackup": totals(snapshot), "materializedRestoreIncludingRebuiltViewers": totals(recovery),
        "allReplayCopiesIncludingBackups": totals(out),
    }
    check_protected(state)
    state["status"] = "complete"
    state["completedAt"] = time.time()
    state["elapsedWallSeconds"] = state["completedAt"] - state["startedAt"]
    write(out / RECEIPT, state)
    write_summary(out, state)
    return check(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=pathlib.Path, default=BASELINE)
    parser.add_argument("--out", type=pathlib.Path, default=OUT)
    parser.add_argument("--workers", type=int, default=3)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        out = output_path(args.out)
        baseline = args.baseline
        if not baseline.is_absolute() or ".." in baseline.parts:
            raise ValueError("baseline must be an absolute path without traversal")
        if not 1 <= args.workers <= 3:
            raise ValueError("workers must be 1..3")
        reproducible_runtime(args.workers)
        if args.check:
            check(out)
        elif args.apply:
            apply(out, baseline, args.workers)
        else:
            original, rows, _, _ = inspect_baseline(baseline)
            print(f"Preview: {len(rows)} exact inputs, {sum(row['bytes'] for row in rows):,} bytes; "
                  f"{len(original['photos'])} general matches, core seeds, inherited catalogue verified.")
            print(f"New LEAN default, fresh embedding cache; isolated output: {out}")
            print("Compare all original/native/preview/selected-padding roles and routing BEFORE installation.")
            print("Then FULL hot backup, install/check, viewers, FULL installed hot backup, ordinary restore/viewer rebuild.")
            print("No files written; no models, matching or preparation started.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(f"Replay stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
