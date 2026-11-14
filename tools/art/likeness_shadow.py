"""Bounded saved-evidence likeness experiments; never writes to the photo library."""
import argparse
import ctypes
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.art.likeness_library import shadow  # noqa: E402


def peak_working_set():
    if sys.platform != "win32":
        return {"available": False, "reason": "Windows process counter only"}

    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong), ("faults", ctypes.c_ulong),
            *[(name, ctypes.c_size_t) for name in (
                "peakWorkingSet", "workingSet", "peakPaged", "paged",
                "peakNonPaged", "nonPaged", "pagefile", "peakPagefile",
            )],
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    api = ctypes.WinDLL("psapi", use_last_error=True)
    if not api.GetProcessMemoryInfo(
        ctypes.c_void_p(-1), ctypes.byref(counters), ctypes.sizeof(counters),
    ):
        raise OSError(ctypes.get_last_error(), "cannot read process peak working set")
    return {"available": True, "bytes": counters.peakWorkingSet,
            "scope": "whole process including JSON loading; Windows peak working set, not incremental heap"}


def output_path(value):
    path = pathlib.Path(value)
    if not path.is_absolute():
        raise ValueError("--out must be an absolute path under repository tmp")
    path = path.resolve()
    try:
        path.relative_to((ROOT / "tmp").resolve())
    except ValueError as error:
        raise ValueError("--out must be inside repository tmp") from error
    if path == (ROOT / "tmp").resolve():
        raise ValueError("--out must be a named experiment directory, not tmp itself")
    ignored = subprocess.run(
        ["git", "check-ignore", "--quiet", str(path / "receipt.json")], cwd=ROOT, check=False,
    )
    if ignored.returncode != 0:
        raise ValueError("experiment output must be verified git-ignored")
    return path


def check(path, provenance, parameters):
    receipt = json.loads((path / "receipt.json").read_bytes())
    if receipt["provenance"] != provenance or receipt["parameters"] != parameters:
        raise ValueError("experiment inputs, code or parameters changed; use a new --out")
    for name, expected in receipt["outputs"].items():
        if name not in {"scope.json", "experiment.json"} or shadow.digest(path / name) != expected:
            raise ValueError(f"experiment output differs from receipt: {name}")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=pathlib.Path, help="Absolute saved baseline run directory")
    parser.add_argument("--out", required=True, help="New absolute git-ignored repo tmp experiment directory")
    parser.add_argument("--seed", action="append", help="Name scope seed; repeated; defaults to all Vales, Angelica, Uma and Gaia")
    parser.add_argument("--hops", type=int, choices=range(4), default=1)
    parser.add_argument("--minimum-score", type=float, default=0.3, help="Scope screening only, not a matching threshold")
    parser.add_argument("--max-photos", type=int, default=1500, help="Whole-identity scope cap; refuses rather than truncates")
    parser.add_argument("--max-candidates", type=int, default=2500, help="Global planner cap, independent of scoped-photo cap")
    parser.add_argument("--max-json-mib", type=int, default=128, help="Total saved JSON input size cap before parsing")
    parser.add_argument("--compare-order", action="store_true", help="Also test identical repeat and reversed candidate order")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true", help="Inspect receipt/cache/scope without planner or writes (default)")
    modes.add_argument("--apply", action="store_true", help="Write experiment evidence only, never install")
    modes.add_argument("--check", action="store_true", help="Verify existing evidence read-only, without rerunning planner")
    args = parser.parse_args(argv)
    try:
        if (not args.run.is_absolute() or not 0 <= args.minimum_score <= 1
                or min(args.max_photos, args.max_candidates, args.max_json_mib) < 1):
            raise ValueError("require absolute --run, minimum score in [0,1] and positive resource limits")
        out = output_path(args.out)
        started = time.perf_counter()
        cpu_started = time.process_time()
        run, vectors, provenance = shadow.load_bundle(
            args.run.resolve(), max_json_bytes=args.max_json_mib * 1024 * 1024,
        )
        if sum("initialBestCast" in row for row in run["photos"]) > args.max_candidates:
            raise ValueError(f"full planner population exceeds --max-candidates {args.max_candidates}")
        provenance["entrypointSHA256"] = shadow.digest(pathlib.Path(__file__))
        scope = shadow.select_scope(
            run, args.seed or shadow.SEEDS, hops=args.hops, minimum_score=args.minimum_score,
            max_photos=args.max_photos,
        )
        parameters = {
            "seeds": args.seed or list(shadow.SEEDS), "hops": args.hops,
            "minimumScore": args.minimum_score, "maxPhotos": args.max_photos,
            "maxCandidates": args.max_candidates, "maxJsonMiB": args.max_json_mib,
            "compareOrder": args.compare_order,
        }
        if args.check or args.apply and out.exists():
            receipt = check(out, provenance, parameters)
            print(f"Verified existing evidence: {out} ({receipt['seconds']:.3f}s original run)")
            return 0
        candidates, cores = shadow.replay_inputs(run, vectors)
        print(f"Scope: {scope['identityCount']} identities / {scope['photoCount']} photos")
        print(f"Full replay context: {len(run['photos'])} receipt rows, {len(candidates)} candidates, {len(cores)} cast cores")
        print("Original cast scores: exact parity; no PNG reads, model calls, intake, installation or library writes.")
        if not args.apply:
            print(f"Preview only; scoped evidence would be written to: {out}")
            return 0
        result = shadow.experiment(run, vectors, compare_order=args.compare_order)
        receipt = {"schemaVersion": 1, "provenance": provenance, "parameters": parameters,
                   "seconds": time.perf_counter() - started,
                   "cpuSeconds": time.process_time() - cpu_started,
                   "peakWorkingSet": peak_working_set(), "outputs": {}}
        out.mkdir(parents=True, exist_ok=False)
        for name, value in (("scope.json", scope), ("experiment.json", result)):
            (out / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            receipt["outputs"][name] = shadow.digest(out / name)
        temporary = out / "receipt.json.partial"
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, out / "receipt.json")
        check(out, provenance, parameters)
        for trial in result["trials"]:
            print(f"{trial['name']}: {trial['seconds']:.3f}s; {trial['photoCount']} decisions; parity passed")
        print(f"Evidence verified: {out}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"likeness-shadow: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
