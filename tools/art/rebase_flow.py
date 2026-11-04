"""Run the fresh sandbox rebase end to end with live progress, step timings and disk space.

The flow calls the same bin launchers a person would, in order: full reset, originals,
backup of the fresh baseline, intake, matching plan, install, checks. The read-only reset
preview, intake inventory and separate intake check are optional (--with-previews): the
reset apply, matching plan and install repeat those guards themselves. Each step's full
output goes to its own log; the console shows a start/finish line per step, sub-phase
timings, a heartbeat with progress and ETA, and a running process-flow recap (flow.md)
that is rewritten after every event. Completed steps are recorded in flow.json, so a
rerun resumes where it stopped.

  rebase_flow.py --root WORKING --run NAME            preview the plan (no writes)
  rebase_flow.py --root WORKING --run NAME --apply    run or resume
  rebase_flow.py --root WORKING --run NAME --check    read-only status of a flow
"""

import argparse
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import time

REPO = pathlib.Path(__file__).resolve().parents[2]
FLOW_ROOT = REPO / "tmp" / "session-logs" / "rebase-flow"
REBASE_FLAGS = ("--baseline", "working", "--cast-seeds", "core", "--record-core-protection")
RUN_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
PHASE_LINE = re.compile(r"^(Install|Plan|Apply): (.+) in ([\d.]+)s$")
WORKER_LINE = re.compile(r"Completed worker (\d+)/(\d+)")
RECOVERED_LINE = re.compile(r"Recovered complete image checkpoints: (\d+)/(\d+)")
ALERT_LINE = re.compile(r"ERROR|Traceback|blocked|Access is denied|OUT OF SYNC", re.IGNORECASE)
SILENCE_WARNING_SECONDS = 600
# Wall-clock minutes of the Nov 3 fresh-20261103-core run (from its log timestamps).
# They are estimates for "what remains", not targets; the LEAN trim should beat intake.
NOV3_MINUTES = {
    "reset-preview": 10, "reset-apply": 35, "originals": 5, "originals-check": 3,
    "backup": 13, "intake-preview": 3, "intake": 197, "intake-check": 4,
    "match-preview": 12, "install": 311, "install-check": 23, "gallery-check": 5,
}
SPACE_COLUMNS = (
    ("Working", "working"), ("run state", "run"), ("run inputs", "inputs"),
    ("_backup", "_backup"), ("_processing", "_processing"), ("people", "people"),
)
PEOPLE = ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Various")


def steps(working, run, workers):
    """The ordered flow; every command is a bin launcher run from the repository root."""
    w, r = str(working), str(run)
    rebase = ["bin\\sandbox-rebase.cmd", w, r, *REBASE_FLAGS]
    return [
        {"id": "reset-preview", "title": "Full reset preview (blockers, Production baseline)",
         "argv": ["bin\\likeness.cmd", "--root", w, "sandbox-reset", "--full"],
         "expect": r'"resetReady": true', "optional": True},
        {"id": "reset-apply", "title": "Full reset of Working to Production",
         "argv": ["bin\\likeness.cmd", "--root", w, "sandbox-reset", "--full", "--apply"],
         "expect": r'"applied": true'},
        {"id": "originals", "title": "Originals: names, 944x1104 copies, headshots",
         "argv": ["bin\\originals.cmd", "--root", w, "--no-repoint"]},
        {"id": "originals-check", "title": "Originals in sync",
         "argv": ["bin\\originals.cmd", "--root", w, "--no-repoint", "--check"],
         "expect": r"IN SYNC"},
        {"id": "backup", "title": "Backup of the fresh baseline (install requires it)",
         "argv": ["bin\\library-backup.cmd", "--root", w, "--apply"],
         "expect": r"snapshot complete"},
        {"id": "intake-preview", "title": "Intake inventory (dry run)", "argv": [*rebase, "--dry-run"],
         "optional": True},
        {"id": "intake", "title": f"Intake preparation ({workers} workers)",
         "argv": [*rebase, "--intake-only", "--apply", "--workers", str(workers)]},
        {"id": "intake-check", "title": "Intake verification",
         "argv": [*rebase, "--intake-only", "--check"], "expect": r"Intake verified", "optional": True},
        {"id": "match-preview", "title": "Matching plan (likeness, cast, refinement; install needs it)",
         "argv": rebase},
        {"id": "install", "title": "Install, galleries, Overview and Review",
         "argv": [*rebase, "--apply", "--preserve-legacy-derivatives"]},
        {"id": "install-check", "title": "Installed run check", "argv": [*rebase, "--check"]},
        {"id": "gallery-check", "title": "People gallery check",
         "argv": ["bin\\people-gallery.cmd", "--root", w, "--cache", str(run / "likeness-cache.json"),
                  "--policy", str(run / "policy.json"), "--check"]},
    ]


def flow_paths(run_name):
    folder = FLOW_ROOT / run_name
    return folder, folder / "flow.json", folder / "flow.md"


def _now():
    return datetime.datetime.now().replace(microsecond=0)


def _duration(seconds):
    if seconds is None:
        return ""
    seconds = int(round(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h{minutes:02d}m"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def _gb(value):
    return "" if value is None else f"{value / 1024 ** 3:.2f} GB"


def _tree_bytes(path):
    total = count = 0
    stack = [path]
    while stack:
        try:
            entries = list(os.scandir(stack.pop()))
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_dir(follow_symlinks=False):
                    stack.append(entry.path)
                else:
                    total += entry.stat(follow_symlinks=False).st_size
                    count += 1
            except OSError:
                continue
    return total, count


def measure_space(working, run):
    """Bytes and file counts for the parts of Working the LEAN trim and LY14 decisions affect."""
    working, run = pathlib.Path(working), pathlib.Path(run)
    started = time.perf_counter()
    space = {"working": 0, "people": 0}
    files = 0
    if working.is_dir():
        for entry in os.scandir(working):
            if entry.is_dir(follow_symlinks=False):
                size, count = _tree_bytes(entry.path)
            else:
                size, count = entry.stat().st_size, 1
            space["working"] += size
            files += count
            if entry.name in ("_backup", "_processing"):
                space[entry.name] = size
            if entry.name in PEOPLE:
                space["people"] += size
    space["run"] = _tree_bytes(run)[0] if run.is_dir() else 0
    space["inputs"] = _tree_bytes(run / "inputs")[0] if (run / "inputs").is_dir() else 0
    space["files"] = files
    space["seconds"] = round(time.perf_counter() - started, 1)
    return space


def load_state(state_path, working, run, workers, flow):
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state["working"] != str(working) or state["run"] != str(run):
            raise ValueError("this flow name belongs to another Working/run; use a new --run name")
    else:
        state = {"schemaVersion": 1, "working": str(working), "run": str(run), "workers": workers,
                 "created": _now().isoformat(), "steps": {}, "history": []}
    for step in flow:
        state["steps"].setdefault(step["id"], {"status": "pending"})
    return state


def apply_optional(state, flow, with_previews):
    """Skip read-only previews and duplicate checks unless asked; the apply steps repeat their guards."""
    for step in flow:
        if not step.get("optional"):
            continue
        record = state["steps"][step["id"]]
        if with_previews and record["status"] == "skipped":
            state["steps"][step["id"]] = {"status": "pending"}
        elif not with_previews and record["status"] != "done":
            state["steps"][step["id"]] = {"status": "skipped", "note": "optional; --with-previews runs it"}


def _write_atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def save(state, state_path, md_path, flow, live=None):
    _write_atomic(state_path, json.dumps(state, indent=2))
    _write_atomic(md_path, render_markdown(state, flow, live))


def estimate_remaining(state, flow, live=None, now=None):
    """Minutes left: Nov 3 times for pending steps plus what remains of the running one."""
    now = now or time.time()
    remaining = 0.0
    for step in flow:
        record = state["steps"][step["id"]]
        estimate = NOV3_MINUTES.get(step["id"], 5) * 60
        if record["status"] == "running" and live is not None:
            eta = progress(live, now).get("eta")
            remaining += eta if eta is not None else max(estimate - (now - live["started"]), 0)
        elif record["status"] in ("pending", "failed", "interrupted"):
            remaining += estimate
    return remaining


def progress(live, now=None):
    """Photo progress from worker lines: done/total, rate per minute and seconds left."""
    now = now or time.time()
    result = {}
    if live.get("total"):
        done = live["done"]
        result.update(done=done, total=live["total"], percent=100.0 * done / live["total"])
        first = live.get("first_worker")
        rendered = done - live.get("first_done", 0)
        if first is not None and rendered > 0 and now > first:
            rate = rendered / (now - first)
            result["rate"] = rate * 60
            result["eta"] = (live["total"] - done) / rate
    return result


def heartbeat_line(step_index, flow, live, state, now=None):
    now = now or time.time()
    step = flow[step_index]
    parts = [f"[{time.strftime('%H:%M', time.localtime(now))}] {step['id']} "
             f"{step_index + 1}/{len(flow)} running {_duration(now - live['started'])}"]
    info = progress(live, now)
    if info:
        text = f"{info['done']:,}/{info['total']:,} photos ({info['percent']:.0f}%)"
        if "rate" in info:
            text += f", {info['rate']:.1f}/min, ETA {_duration(info['eta'])}"
        parts.append(text)
    elif step["id"] in NOV3_MINUTES:
        parts.append(f"Nov 3 took {NOV3_MINUTES[step['id']]}m")
    if live.get("phases"):
        last = live["phases"][-1]
        parts.append(f"last phase {last['phase']} {_duration(last['seconds'])}")
    silent = now - live["last_output"]
    parts.append(f"last output {_duration(silent)} ago")
    if silent > SILENCE_WARNING_SECONDS:
        parts.append("QUIET: a long silent phase, or the process is suspended (check Task Manager)")
    parts.append(f"flow remaining ~{_duration(estimate_remaining(state, flow, live, now))}")
    return "; ".join(parts)


def render_markdown(state, flow, live=None):
    now = time.time()
    lines = [f"# Rebase flow `{pathlib.Path(state['run']).name}`", "",
             f"- Working: `{state['working']}`",
             f"- Run state: `{state['run']}`",
             f"- Created {state['created']}; updated {_now().isoformat()}",
             f"- Estimated remaining: {_duration(estimate_remaining(state, flow, live, now))} "
             "(Nov 3 step times; intake uses its live ETA)", "",
             "| # | Step | Status | Started | Took | Nov 3 | Note |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for index, step in enumerate(flow, 1):
        record = state["steps"][step["id"]]
        took = record.get("seconds")
        note = record.get("note", "")
        if record["status"] == "running" and live is not None:
            took = now - live["started"]
            info = progress(live, now)
            if info:
                note = f"{info['done']:,}/{info['total']:,} photos ({info['percent']:.0f}%)"
                if "eta" in info:
                    note += f", ETA {_duration(info['eta'])}"
        lines.append(f"| {index} | {step['id']} | {record['status']} | {record.get('started', '')[11:16]} | "
                     f"{_duration(took)} | {NOV3_MINUTES.get(step['id'], '')}m | {note} |")
    phase_rows = [(step["id"], phase) for step in flow
                  for phase in state["steps"][step["id"]].get("phases", [])]
    if live is not None:
        phase_rows += [(live["id"], phase) for phase in live.get("phases", [])]
    if phase_rows:
        lines += ["", "## Phase timings", "", "| Step | Phase | Took |", "| --- | --- | --- |"]
        lines += [f"| {step_id} | {phase['phase']} | {_duration(phase['seconds'])} |"
                  for step_id, phase in phase_rows]
    snapshots = [("start", state.get("spaceStart"))] + [
        (step["id"], state["steps"][step["id"]].get("space")) for step in flow]
    snapshots = [(label, space) for label, space in snapshots if space]
    if snapshots:
        lines += ["", "## Space after each step", "",
                  "| After | " + " | ".join(title for title, _ in SPACE_COLUMNS) + " | files |",
                  "| --- |" + " --- |" * (len(SPACE_COLUMNS) + 1)]
        lines += [f"| {label} | " + " | ".join(_gb(space.get(key)) for _, key in SPACE_COLUMNS)
                  + f" | {space.get('files', 0):,} |" for label, space in snapshots]
    lines += ["", "Logs: one file per step next to this page (`NN-step.log`)."]
    return "\n".join(lines) + "\n"


def _reader(process, log_path, live, echo):
    with log_path.open("a", encoding="utf-8") as log:
        for raw in process.stdout:
            line = raw.rstrip("\r\n")
            now = time.time()
            log.write(f"{time.strftime('%H:%M:%S', time.localtime(now))} {line}\n")
            log.flush()
            live["last_output"] = now
            if line.strip():
                live["last_line"] = line.strip()[:200]
            if live["expect"] and re.search(live["expect"], line):
                live["expected_seen"] = True
            match = WORKER_LINE.search(line)
            if match:
                live["done"], live["total"] = int(match.group(1)), int(match.group(2))
                if live.get("first_worker") is None:
                    live["first_worker"], live["first_done"] = now, live["done"] - 1
                continue
            match = RECOVERED_LINE.search(line)
            if match:
                live["done"], live["total"] = int(match.group(1)), int(match.group(2))
                echo(f"    {line.strip()}")
                continue
            match = PHASE_LINE.match(line.strip())
            if match:
                live["phases"].append({"phase": f"{match.group(1)}: {match.group(2)}",
                                       "seconds": float(match.group(3))})
                echo(f"    {match.group(1)}: {match.group(2)} took {_duration(float(match.group(3)))}")
            elif ALERT_LINE.search(line):
                echo(f"    ! {line.strip()[:240]}")


def run_step(index, step, state, paths, flow, *, heartbeat, measure, echo, launcher):
    folder, state_path, md_path = paths
    record = state["steps"][step["id"]]
    log_path = folder / f"{index + 1:02d}-{step['id']}.log"
    command = launcher(step["argv"])
    started = time.time()
    record.clear()
    record.update(status="running", started=_now().isoformat(), log=log_path.name,
                  command=subprocess.list2cmdline(command))
    live = {"id": step["id"], "started": started, "last_output": started, "phases": [],
            "expect": step.get("expect"), "expected_seen": False, "done": 0, "total": 0}
    remaining = _duration(estimate_remaining(state, flow, live))
    echo(f"\n=== [{index + 1}/{len(flow)}] {step['id']}: {step['title']} "
         f"(started {_now().strftime('%H:%M')}; Nov 3 {NOV3_MINUTES.get(step['id'], '?')}m; "
         f"flow remaining ~{remaining})")
    echo(f"    log: {log_path}")
    save(state, state_path, md_path, flow, live)
    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"# {record['command']}\n")
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    process = subprocess.Popen(command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               env=env, text=True, encoding="utf-8", errors="replace")
    reader = threading.Thread(target=_reader, args=(process, log_path, live, echo), daemon=True)
    reader.start()
    next_beat = started + heartbeat
    try:
        while reader.is_alive():
            reader.join(timeout=1)
            if time.time() >= next_beat and reader.is_alive():
                echo("    " + heartbeat_line(index, flow, live, state))
                save(state, state_path, md_path, flow, live)
                next_beat = time.time() + heartbeat
        code = process.wait()
        process.stdout.close()
    except KeyboardInterrupt:
        process.terminate()
        record.update(status="interrupted", seconds=round(time.time() - started, 1),
                      phases=live["phases"], note="stopped by Ctrl+C; rerun --apply to resume")
        save(state, state_path, md_path, flow)
        raise
    seconds = round(time.time() - started, 1)
    record.update(seconds=seconds, exit=code, phases=live["phases"], ended=_now().isoformat())
    if live.get("total"):
        record["photos"] = {"done": live["done"], "total": live["total"]}
    failed = code != 0 or (step.get("expect") and not live["expected_seen"])
    if failed:
        reason = f"exit {code}" if code else f"did not report '{step['expect']}'"
        record.update(status="failed", note=f"{reason}; last: {live.get('last_line', '')[:120]}")
        save(state, state_path, md_path, flow)
        echo(f"--- {step['id']} FAILED after {_duration(seconds)} ({reason}). Last log lines:")
        for line in log_path.read_text(encoding="utf-8").splitlines()[-15:]:
            echo(f"    {line}")
        echo("    Fix the cause, then rerun the same --apply command to resume at this step.")
        return False
    echo("    measuring space...")
    record["space"] = measure()
    record["status"] = "done"
    nov3 = NOV3_MINUTES.get(step["id"])
    compare = f" (Nov 3 {nov3}m)" if nov3 else ""
    space = record["space"]
    echo(f"--- {step['id']} done in {_duration(seconds)}{compare}; Working {_gb(space['working'])}, "
         f"run state {_gb(space['run'])}; flow remaining ~{_duration(estimate_remaining(state, flow))}")
    save(state, state_path, md_path, flow)
    return True


def _launcher(argv):
    return ["cmd", "/c", *argv]


def run_flow(flow, state, paths, *, start=None, until=None, heartbeat=120, measure,
             echo=print, launcher=_launcher):
    folder, state_path, md_path = paths
    ids = [step["id"] for step in flow]
    if start is not None:
        position = ids.index(start)
        for step_id in ids[position:]:
            record = state["steps"][step_id]
            if record["status"] != "pending":
                state["history"].append({"step": step_id, **record})
            state["steps"][step_id] = {"status": "pending"}
    if "spaceStart" not in state:
        echo("Measuring starting space...")
        state["spaceStart"] = measure()
    flow_started = time.time()
    echo(f"Live process-flow recap: {md_path}")
    for index, step in enumerate(flow):
        if state["steps"][step["id"]]["status"] in ("done", "skipped"):
            continue
        if not run_step(index, step, state, paths, flow, heartbeat=heartbeat, measure=measure,
                        echo=echo, launcher=launcher):
            return 1
        if until is not None and step["id"] == until:
            echo(f"Stopped after {until} as requested.")
            break
    echo(f"\nFlow finished this session in {_duration(time.time() - flow_started)}. Recap: {md_path}")
    echo(render_markdown(state, flow))
    return 0


def preview(flow, state, md_path, echo=print):
    echo(f"Preview only; add --apply to run. Live recap will be {md_path}")
    total = 0
    for index, step in enumerate(flow, 1):
        record = state["steps"][step["id"]]
        minutes = NOV3_MINUTES.get(step["id"], 5)
        if record["status"] not in ("done", "skipped"):
            total += minutes
        echo(f"{index:2}. {step['id']:<15} {record['status']:<11} Nov 3 ~{minutes:>3}m  "
             f"{subprocess.list2cmdline(step['argv'])}")
    echo(f"Estimated time for steps not done: ~{_duration(total * 60)} (Nov 3 times; LEAN intake should be faster)")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, help="the sandbox Working folder")
    parser.add_argument("--run", required=True, help="new run name under Working\\_sandbox-state")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--heartbeat", type=int, default=120, help="seconds between progress lines")
    parser.add_argument("--from", dest="start", help="redo from this step (earlier records kept in history)")
    parser.add_argument("--until", help="stop after this step")
    parser.add_argument("--with-previews", action="store_true",
                        help="also run the optional reset preview, intake inventory and separate intake check")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="run or resume the flow")
    mode.add_argument("--dry-run", action="store_true", help="preview only (the default)")
    mode.add_argument("--check", action="store_true", help="read-only status of this flow")
    args = parser.parse_args(argv)
    # Progress must reach a redirected console log immediately, not when the buffer fills.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    working = pathlib.Path(args.root).resolve()
    if working.name != "Working" or not (working.parent / "Source").is_dir():
        raise ValueError("--root must be a sandbox Working folder next to its Source snapshot")
    if not RUN_NAME.match(args.run):
        raise ValueError("--run must be a plain folder name such as fresh-20261104-lean")
    run = working / "_sandbox-state" / args.run
    flow = steps(working, run, args.workers)
    ids = [step["id"] for step in flow]
    for name in (args.start, args.until):
        if name is not None and name not in ids:
            raise ValueError(f"unknown step {name}; steps: {', '.join(ids)}")
    paths = flow_paths(args.run)
    if args.check:
        if not paths[1].is_file():
            print(f"No flow recorded for {args.run} ({paths[1]}).")
            return 1
        state = load_state(paths[1], working, run, args.workers, flow)
        print(render_markdown(state, flow))
        failed = [step_id for step_id, record in state["steps"].items() if record["status"] == "failed"]
        return 1 if failed else 0
    state = load_state(paths[1], working, run, args.workers, flow)
    apply_optional(state, flow, args.with_previews)
    if not args.apply:
        return preview(flow, state, paths[2])
    if state.get("workers") != args.workers and state["steps"]["intake"]["status"] != "done":
        state["workers"] = args.workers
    return run_flow(flow, state, paths, start=args.start, until=args.until,
                    heartbeat=args.heartbeat, measure=lambda: measure_space(working, run))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nInterrupted; rerun with --apply to resume at the interrupted step.", file=sys.stderr)
        sys.exit(130)
