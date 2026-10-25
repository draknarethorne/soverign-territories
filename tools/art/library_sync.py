#!/usr/bin/env python3
"""The whole photo-library routine in one command: drop new photos into Various\\gallery, run this, and the library ends sorted, de-duplicated and in step.

  python tools/art/library_sync.py              do everything (bin\\library.cmd)
  python tools/art/library_sync.py --dry-run    preview every step, move nothing (bin\\library-preview.cmd)
  python tools/art/library_sync.py --check      read only: what is waiting, and is the library in step? exit 1 when work is waiting (bin\\library-check.cmd)

The steps, in order (each is the normal command; run one alone if you want to look closer):
  0  likeness seed        Various\\<Name>\\gallery holds photos of one known person: the whole folder moves to <Name> first
  1  originals            name every original after its folder, make the scaled copy and headshot
  2  duplicates           the same picture kept twice (any folder, any name) is set aside in _archive, a chosen photo and the higher folder first
  3  likeness crop        general photos use the legacy crop; likeness_artists crop/junk runs the same code on Artists separately. The uncropped original is kept in _archive\\...\\gallery_uncropped
     likeness junk       active photos that cannot feed a Prime go to _junk; existing Junk is not implicitly reconsidered
  4  likeness reconcile   one shared policy-driven plan for incoming and Review candidates, with verified backup and a reversible move journal
  5  likeness_artists group  shared grouping with artist-only discovery/cache/history; artists are never mixed with the general identity pool
  6  likeness retire-empty  prospects with no gallery or review photos are moved intact to _retired (previewed on --dry-run)
  7  duplicates, originals  again, because the moves create new names; then `originals --check` must say IN SYNC
  8  sync-inputs          the images the workflows load are copied into each workspace's input folder
  9  likeness crosscheck, crops, people gallery, index  look-alikes are reported; the people gallery adds sister-match and photo-readiness evidence
  --retry-junk explicitly retries legacy flat _junk buckets (prospects to Various, artists to their own gallery); nested manual/preparation Junk has its own guarded undo.
Nothing is deleted: moved files keep their place in _archive, _junk, _retired or a person's review folder, and `likeness undo` reverses the last batch of sorted moves.
Reports are grouped under <work>\\_reports\\library, comparisons and runs; a log of the run is saved in <work>\\_reports\\runs\\library_sync_<time>.log.
"""
import argparse
import datetime
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
sys.path.insert(0, str(ROOT / "tools/art"))
import comfy_workflows as cw  # noqa: E402
import library_backup  # noqa: E402
from likeness_library.maintenance import require_authorization  # noqa: E402
from likeness_library.policy import load_policy  # noqa: E402

ART = "tools/art/"
# lines of the tools that say "nothing to do here": left out of the screen (the log keeps every line)
BORING = re.compile(r"^(-{5,}$|\s*0 (renamed, )?(to make|made), 0 (to prune|pruned)\s*$|\s*headshots: 0 (to make|made), \d+ skipped \(no usable face\), 0 (to prune|pruned)\s*$|\s*NO PHOTO |\s+NOT FOUND )")


def plan(args):
    """[(title, argv, required, info)] for the chosen mode. required: the run stops when this step fails. info: a non-zero exit only means 'something was found' (a preview that lists work)."""
    go = [] if args.dry_run else ["--apply"]
    steps = []
    if not args.no_likeness:
        steps.append(("0 likeness seed (Various\\<Name> folders of one known person)", [ART + "likeness.py", "--no-originals", "seed", *go], True, False))
    steps += [("1 originals: names, scaled copies and headshots", [ART + "originals.py", *(["--dry-run"] if args.dry_run else ["--apply"])], True, False),
              ("2 duplicates (prefer updated incoming same-ID photo)", [ART + "duplicates.py", "--prefer-incoming", *go], False, args.dry_run)]
    if not args.no_likeness:
        if args.retry_junk:
            steps += [("3 likeness junk --reset (legacy general Junk only)", [ART + "likeness.py", "junk", "--reset", *go], False, False),
                      ("3 artist junk --reset (legacy artist Junk only)", [ART + "likeness_artists.py", "junk", "--reset", *go], False, False)]
        steps += [("3 likeness crop (bars, other people, animals, background)", [ART + "likeness.py", "crop", *go], False, False),
                  ("3 likeness junk", [ART + "likeness.py", "junk", *go], False, False),
                  ("3 artist crop (shared cleanup, artist scope only)", [ART + "likeness_artists.py", "crop", *go], False, False),
                  ("3 artist junk", [ART + "likeness_artists.py", "junk", *go], False, False),
                  ("4 unified likeness reconciliation", [ART + "likeness.py", "reconcile", *go], True, False),
                  ("5 artist group --singles (the artists' own galleries)", [ART + "likeness_artists.py", "group", "--singles", "--min-photos", "2", *go], False, False),
                  ("6 likeness retire-empty (empty prospect folders)", [ART + "likeness.py", "retire-empty", *go], True, False)]
    if not args.dry_run:
        steps += [("7 duplicates again", [ART + "duplicates.py", "--apply"], False, False),
                  ("7 originals again", [ART + "originals.py", "--apply"], True, False),
                  ("7 originals --check", [ART + "originals.py", "--check"], False, False),
                  ("8 sync-inputs", ["tools/workflows/sync_inputs.py", "--apply"], False, False)]
        if not args.no_likeness:
            steps += [("9 likeness crosscheck (look-alikes across the lines kept apart)", [ART + "likeness.py", "crosscheck"], False, False),
                      ("9 likeness crops (a page of every crop, before and after)", [ART + "likeness.py", "crops"], False, False),
                      ("9 people gallery review (full Gallery and Review photos)", [ART + "likeness_library/review_gallery.py"], False, False),
                      ("9 people gallery (a page of every person)", [ART + "people_gallery.py"], False, False),
                      ("9 artist gallery (separate read-only pages)", [ART + "artists_gallery.py", "--apply"], False, False),
                      ("9 artist index", [ART + "likeness_artists.py", "index"], False, False),
                      ("9 likeness index", [ART + "likeness.py", "index"], False, False)]
    return steps


def check_plan():
    return [("named Various\\<Name> folders waiting (preview)", [ART + "likeness.py", "seed"], False, False),
            ("originals --check (names, scaled copies and headshots)", [ART + "originals.py", "--check"], False, True),
            ("duplicates (report)", [ART + "duplicates.py"], False, True),
            ("artist-only usable-face check", [ART + "likeness_artists.py", "--check"], False, True),
            ("shared reconciliation preview (incoming and Review)", [ART + "likeness.py", "reconcile"], False, False)]


def snapshot(cfg):
    """What the library holds now: pool size, people per root, originals in galleries."""
    import originals
    folders = cw.photo_folders(cfg)
    count = {"pool": 0, "galleries": 0, "review": 0}
    people = {}
    for group, _name, folder in folders:
        n = len(originals.images(folder / "gallery"))
        count["galleries"] += n
        count["review"] += len(originals.images(folder / "review"))
        if group == "Various":
            count["pool"] += n
        else:
            people[group] = people.get(group, 0) + 1
    return count, people, {f"{g}/{n}" for g, n, _ in folders}


def run_step(title, argv, log):
    """Run one tool, show and log its output; returns (exit code, output lines)."""
    bar = "=" * 78
    head = f"\n{bar}\n== {title}\n{bar}"
    print(head)
    log.write(head + "\n")
    proc = subprocess.Popen([sys.executable, *argv], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    lines, pending = [], None
    for line in proc.stdout:
        line = line.rstrip("\n")
        log.write(line + "\n")
        lines.append(line)
        if line.startswith(">>> "):
            pending = line  # a folder header is shown only when something under it is news
        elif not BORING.match(line):
            if pending:
                print(pending)
                pending = None
            print(line)
    proc.wait()
    return proc.returncode, lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="preview every step and move nothing")
    ap.add_argument("--check", action="store_true", help="read only: is the library in step and is anything waiting? exit 1 when it is not")
    ap.add_argument("--no-likeness", action="store_true", help="only the file housekeeping (names, copies, duplicates, check); skip the likeness sorting")
    ap.add_argument("--retry-junk", action="store_true", help="first send everything in _junk back (prospects to Various, an artist's photos to that artist) so the cropping and the rules look at it again")
    ap.add_argument("--min", type=float, help="obsolete; configure tier thresholds in likeness-engine-policy.json")
    args = ap.parse_args(argv)
    if args.min is not None:
        ap.error("--min is obsolete; configure tier thresholds in likeness-engine-policy.json")
    cfg = cw.load_cfg()
    work = cw.work_root(cfg)
    reports = work / "_reports"
    run_reports = reports / "runs"
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    if not args.check and not args.dry_run:
        if not args.no_likeness:
            try:
                require_authorization(work, load_policy())
            except ValueError as exc:
                print(f"stopped before housekeeping or library changes: {exc}", file=sys.stderr)
                return 1
        try:
            backup = library_backup.create_backup(
                work,
                cfg.get("paths", {}).get("inputsRoot"),
                ROOT / "workflows" / "workspaces.json",
                stamp=stamp,
                apply=True,
            )
        except (OSError, ValueError) as exc:
            print(f"stopped before library changes: full backup failed: {exc}", file=sys.stderr)
            return 1
        print(f"full pre-run snapshot: {backup}")
    run_reports.mkdir(parents=True, exist_ok=True)
    mode = "check" if args.check else "preview" if args.dry_run else "run"
    steps = check_plan() if args.check else plan(args)
    before = snapshot(cfg)
    failed, waiting = [], False
    log_path = run_reports / f"library_sync_{stamp}.log"
    with open(log_path, "w", encoding="utf-8") as log:
        for title, step, required, info in steps:
            rc, lines = run_step(title, step, log)
            if args.check and any(re.search(r"\b[1-9]\d* would move\b|; [1-9]\d* would move", ln) for ln in lines if "photo(s) in the pool" in ln):
                waiting = True  # the pool holds photos that `sort` would place
            if args.check and any(re.search(r"\b[1-9]\d* file move\(s\) proposed", line) for line in lines):
                waiting = True
            if args.check and any(re.match(r"[1-9]\d* named-folder photo\(s\) would move", line) for line in lines):
                waiting = True
            if rc and (args.check or info):
                waiting = waiting or args.check
            elif rc:
                failed.append(title)
                if required:
                    print(f"\nstopped: '{title}' failed; nothing after it was run.")
                    break
        after = snapshot(cfg)
        summary = [f"\nlibrary {mode} finished ({stamp})",
                   f"  pool (Various): {before[0]['pool']} -> {after[0]['pool']}   galleries: {before[0]['galleries']} -> {after[0]['galleries']}   review photos: {before[0]['review']} -> {after[0]['review']}"]
        new, gone = sorted(after[2] - before[2]), sorted(before[2] - after[2])
        if new:
            summary.append(f"  new folders ({len(new)}): " + ", ".join(new))
        if gone:
            summary.append(f"  folders gone ({len(gone)}): " + ", ".join(gone))
        if failed:
            summary.append("  FAILED: " + "; ".join(failed))
        if args.check:
            summary.append("  WORK WAITING: run bin\\library.cmd" if waiting else "  NOTHING WAITING: the library is in step")
        elif args.dry_run:
            summary.append("  preview only: run bin\\library.cmd to do it")
        else:
            summary.append("  IN SYNC" if not failed else "  see the FAILED step above, fix it and run bin\\library.cmd again (it is safe to repeat)")
        text = "\n".join(summary)
        print(text)
        log.write(text + "\n")
    print(f"  log: {log_path}")
    return 1 if (failed or waiting) else 0


if __name__ == "__main__":
    sys.exit(main())
