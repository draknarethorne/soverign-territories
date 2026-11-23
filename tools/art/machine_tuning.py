"""Per-machine parallelism settings.

Resolution order for image-preparation workers (every parallel pool in the
pipeline goes through image preparation):

1. an explicit command-line value;
2. ``ST_INTAKE_WORKERS`` (legacy environment override);
3. ``preparation.workers`` in the git-ignored ``data/config/machine-tuning.local.json``;
4. capacity: ``min(maxWorkers, logical cores // logicalCoresPerWorker,
   free memory // workerMemoryGiB)``, at least 1, from the tracked baseline
   ``data/config/machine-tuning.json``.

Native threads per worker follow ``preparation.threadsPerWorker`` in the local
file, otherwise ``logical cores // workers``. The local file is never synced,
so one machine's measured choice cannot change another machine.
"""
import argparse
import datetime
import json
import os
import pathlib
import platform
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASELINE = ROOT / "data" / "config" / "machine-tuning.json"
LOCAL = ROOT / "data" / "config" / "machine-tuning.local.json"
LOCAL_KEYS = {"workers", "threadsPerWorker", "workerMemoryGiB"}


def _read(path):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        raise ValueError(f"unreadable machine tuning file {path}: {exc}") from exc


def baseline(path=None):
    path = BASELINE if path is None else path
    data = _read(path)
    if not isinstance(data, dict) or not isinstance(data.get("preparation"), dict):
        raise ValueError(f"machine tuning baseline is missing or has no preparation section: {path}")
    prep = data["preparation"]
    for key in ("maxWorkers", "logicalCoresPerWorker"):
        if isinstance(prep.get(key), bool) or not isinstance(prep.get(key), int) or prep[key] < 1:
            raise ValueError(f"machine tuning baseline preparation.{key} must be a positive integer")
    memory = prep.get("workerMemoryGiB")
    if isinstance(memory, bool) or not isinstance(memory, (int, float)) or memory <= 0:
        raise ValueError("machine tuning baseline preparation.workerMemoryGiB must be positive")
    return prep


def local(path=None, maximum=None):
    path = LOCAL if path is None else path
    data = _read(path)
    if data is None:
        return {}
    prep = data.get("preparation") if isinstance(data, dict) else None
    if not isinstance(prep, dict):
        raise ValueError(f"machine-local tuning has no preparation section: {path}")
    unknown = set(prep) - LOCAL_KEYS
    if unknown:
        raise ValueError(f"machine-local tuning has unknown preparation keys {sorted(unknown)}: {path}")
    for key, value in prep.items():
        if key == "workerMemoryGiB":
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f"machine-local preparation.workerMemoryGiB must be positive: {path}")
        elif isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"machine-local preparation.{key} must be a positive integer: {path}")
    if maximum is not None and prep.get("workers", 1) > maximum:
        raise ValueError(f"machine-local preparation.workers exceeds the baseline maximum {maximum}: {path}")
    return prep


def available_memory_gib():
    try:
        import ctypes

        class Status(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                        ("total", ctypes.c_ulonglong), ("available", ctypes.c_ulonglong),
                        ("pageTotal", ctypes.c_ulonglong), ("pageAvailable", ctypes.c_ulonglong),
                        ("virtualTotal", ctypes.c_ulonglong), ("virtualAvailable", ctypes.c_ulonglong),
                        ("extended", ctypes.c_ulonglong)]

        status = Status(length=ctypes.sizeof(Status))
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return status.available / 2 ** 30
    except (AttributeError, OSError):
        pass
    try:
        return os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") / 2 ** 30
    except (AttributeError, ValueError, OSError):
        return None


def max_workers(base_path=None):
    return baseline(base_path)["maxWorkers"]


def worker_memory_gib(base_path=None, local_path=None):
    """Preflight memory per worker: the machine-local measurement, else the shared baseline."""
    measured = local(local_path).get("workerMemoryGiB")
    return float(measured if measured else baseline(base_path)["workerMemoryGiB"])


def capacity_workers(prep, cores=None, free_gib=None):
    cores = (os.cpu_count() or 1) if cores is None else cores
    by_cores = max(1, cores // prep["logicalCoresPerWorker"])
    by_memory = int(free_gib // prep["workerMemoryGiB"]) if free_gib is not None else 1
    return max(1, min(prep["maxWorkers"], by_cores, by_memory))


def preparation_workers(requested=None, *, base_path=None, local_path=None, environ=None,
                        cores=None, free_gib="measure"):
    """Return ``(workers, source)`` for this machine."""
    prep = baseline(base_path)
    maximum = prep["maxWorkers"]
    if requested is not None:
        if isinstance(requested, bool) or not isinstance(requested, int) or not 1 <= requested <= maximum:
            raise ValueError(f"preparation workers must be an integer from 1 to {maximum}")
        return requested, "command line"
    environ = os.environ if environ is None else environ
    try:
        wanted = int(environ.get("ST_INTAKE_WORKERS", "0"))
    except ValueError:
        wanted = 0
    if wanted > 0:
        return min(wanted, maximum), "ST_INTAKE_WORKERS"
    configured = local(local_path, maximum).get("workers")
    if configured:
        return configured, f"machine-local {pathlib.Path(LOCAL if local_path is None else local_path).name}"
    free = available_memory_gib() if free_gib == "measure" else free_gib
    prep = {**prep, "workerMemoryGiB": worker_memory_gib(base_path, local_path)}
    return capacity_workers(prep, cores, free), "machine capacity"


def threads_per_worker(workers, *, local_path=None, cores=None):
    configured = local(local_path).get("threadsPerWorker")
    if configured:
        return configured
    cores = (os.cpu_count() or 2) if cores is None else cores
    return max(1, cores // max(1, workers))


def describe(base_path=None, local_path=None):
    base_path = BASELINE if base_path is None else base_path
    local_path = LOCAL if local_path is None else local_path
    prep = baseline(base_path)
    workers, source = preparation_workers(base_path=base_path, local_path=local_path)
    free = available_memory_gib()
    return {
        "machine": platform.node(),
        "processor": platform.processor(),
        "logicalCores": os.cpu_count(),
        "availableMemoryGiB": None if free is None else round(free, 1),
        "baseline": {"path": str(base_path), "preparation": prep},
        "local": {"path": str(local_path), "exists": pathlib.Path(local_path).is_file(),
                  "preparation": local(local_path, prep["maxWorkers"])},
        "capacityWorkers": capacity_workers(prep, None, free),
        "preparationWorkers": workers,
        "preparationWorkersSource": source,
        "threadsPerWorker": threads_per_worker(workers, local_path=local_path),
    }


def _main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show", help="print this machine's resolved settings (read-only)")
    set_parser = sub.add_parser("set", help="preview or write this machine's local settings")
    set_parser.add_argument("--preparation-workers", type=int, required=True)
    set_parser.add_argument("--threads-per-worker", type=int)
    set_parser.add_argument("--worker-memory-gib", type=float, help="measured preflight memory per worker")
    set_parser.add_argument("--evidence", required=True, help="measurement run/plan that justifies the choice")
    set_parser.add_argument("--apply", action="store_true", help="write the git-ignored local file")
    clear_parser = sub.add_parser("clear", help="preview or remove the local file (back to capacity defaults)")
    clear_parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "show":
            print(json.dumps(describe(), indent=1))
            return 0
        if args.command == "clear":
            print(f"would remove {LOCAL}" if not args.apply else f"removed {LOCAL}")
            if args.apply and LOCAL.is_file():
                LOCAL.unlink()
            return 0
        maximum = max_workers()
        if not 1 <= args.preparation_workers <= maximum:
            parser.error(f"--preparation-workers must be from 1 to {maximum}")
        if args.threads_per_worker is not None and args.threads_per_worker < 1:
            parser.error("--threads-per-worker must be positive")
        if args.worker_memory_gib is not None and args.worker_memory_gib <= 0:
            parser.error("--worker-memory-gib must be positive")
        prep = {"workers": args.preparation_workers}
        if args.threads_per_worker:
            prep["threadsPerWorker"] = args.threads_per_worker
        if args.worker_memory_gib:
            prep["workerMemoryGiB"] = args.worker_memory_gib
        data = {
            "machine": platform.node(), "logicalCores": os.cpu_count(),
            "recordedAt": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "evidence": args.evidence, "preparation": prep,
        }
        print(json.dumps(data, indent=1))
        if not args.apply:
            print(f"preview only; add --apply to write {LOCAL}")
            return 0
        LOCAL.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {LOCAL}")
        return 0
    except ValueError as exc:
        print(f"machine tuning stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_main())
