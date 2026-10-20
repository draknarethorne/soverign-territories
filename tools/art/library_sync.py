#!/usr/bin/env python3
"""The whole photo-library routine in one command: drop new photos into Various\\gallery, run this, and the library ends sorted, de-duplicated and in step.

  python tools/art/library_sync.py              do everything (bin\\library.cmd)
  python tools/art/library_sync.py --dry-run    preview every step, move nothing (bin\\library-preview.cmd)
  python tools/art/library_sync.py --check      read only: what is waiting, and is the library in step? exit 1 when work is waiting (bin\\library-check.cmd)

The steps, in order (each is the normal command; run one alone if you want to look closer):
  1  originals            name every original after its folder, make the scaled copy and headshot
  2  duplicates           the same picture kept twice (any folder, any name) is set aside in _archive, a chosen photo and the higher folder first
  3  likeness crop        every photo is cut down to the person: the app's bars, other people, animals and the background beside her go (all the body in the picture stays). The uncropped original is kept in _archive\\...\\gallery_uncropped
     likeness junk       photos that cannot feed a Prime (no usable face, a second person) go to _junk; usable ones in _junk come back to Various
  4  likeness review      photos set aside in review folders go back to their person when they score 0.20 or more against her
  5  likeness sort        Various is emptied: a photo of an artist goes back to that artist, a confident match moves to that person (an angel or a sister too), a new person gets a Prospects folder (single photos too)
     likeness group       the artists' own galleries are emptied the same way: into the artist's people, or a folder of their own (artists are never mixed)
  6  likeness singles     a one-photo prospect that matches a prospect confidently (default 0.45) is merged into her; likeness rematch merges prospects that are one person, and prospects that are the same person as an angel or a sister join her
  6  likeness retire-empty  prospects with no gallery or review photos are moved intact to _retired (previewed on --dry-run)
  7  duplicates, originals  again, because the moves create new names; then `originals --check` must say IN SYNC
  8  sync-inputs          the images the workflows load are copied into each workspace's input folder
  9  likeness crosscheck, crops, people gallery, index  look-alikes are reported; the people gallery adds sister-match and photo-readiness evidence
  --retry-junk puts everything in _junk back first (prospects to Various, an artist's photos to that artist), so the crop and the rules look at it again; what is still junk returns to _junk.
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

ART = "tools/art/"
# lines of the tools that say "nothing to do here": left out of the screen (the log keeps every line)
BORING = re.compile(r"^(-{5,}$|\s*0 (renamed, )?(to make|made), 0 (to prune|pruned)\s*$|\s*headshots: 0 (to make|made), \d+ skipped \(no usable face\), 0 (to prune|pruned)\s*$|\s*NO PHOTO |\s+NOT FOUND )")


def plan(args):
    """[(title, argv, required, info)] for the chosen mode. required: the run stops when this step fails. info: a non-zero exit only means 'something was found' (a preview that lists work)."""
    go = [] if args.dry_run else ["--apply"]
    steps = [("1 originals: names, scaled copies and headshots", [ART + "originals.py", *(["--dry-run"] if args.dry_run else ["--apply"])], True, False),
             ("2 duplicates (prefer updated incoming same-ID photo)", [ART + "duplicates.py", "--prefer-incoming", *go], False, args.dry_run)]
    if not args.no_likeness:
        if args.retry_junk:
            steps.append(("3 likeness junk --reset (everything in _junk back to be looked at again)", [ART + "likeness.py", "junk", "--reset", *go], False, False))
        steps += [("3 likeness crop (bars, other people, animals, background)", [ART + "likeness.py", "crop", *go], False, False),
                  ("3 likeness junk --recheck", [ART + "likeness.py", "junk", "--recheck", *go], False, False),
                  ("3 likeness junk", [ART + "likeness.py", "junk", *go], False, False),
                  ("4 likeness review", [ART + "likeness.py", "review", *go], False, False),
                  ("5 likeness sort --singles", [ART + "likeness.py", "sort", "--singles", *go], True, False),
                  ("5 likeness group --singles (the artists' own galleries)", [ART + "likeness.py", "group", "--singles", "--min-photos", "2", *go], False, False),
                  (f"6 likeness singles --min {args.min}", [ART + "likeness.py", "singles", "--min", str(args.min), *go], False, False),
                  ("6 likeness rematch", [ART + "likeness.py", "rematch", *go], False, False),
                  ("6 likeness retire-empty (empty prospect folders)", [ART + "likeness.py", "retire-empty", *go], True, False)]
    if not args.dry_run:
        steps += [("7 duplicates again", [ART + "duplicates.py", "--apply"], False, False),
                  ("7 originals again", [ART + "originals.py", "--apply"], True, False),
                  ("7 originals --check", [ART + "originals.py", "--check"], False, False),
                  ("8 sync-inputs", ["tools/workflows/sync_inputs.py", "--apply"], False, False)]
        if not args.no_likeness:
            steps += [("9 likeness crosscheck (look-alikes across the lines kept apart)", [ART + "likeness.py", "crosscheck"], False, False),
                      ("9 likeness crops (a page of every crop, before and after)", [ART + "likeness.py", "crops"], False, False),
                      ("9 people gallery (a page of every person)", [ART + "people_gallery.py", "--artists"], False, False),
                      ("9 likeness index", [ART + "likeness.py", "index"], False, False)]
    return steps


def check_plan():
    return [("originals --check (names, scaled copies and headshots)", [ART + "originals.py", "--check"], False, True),
            ("duplicates (report)", [ART + "duplicates.py"], False, True),
            ("the pool: what `likeness sort` would place", [ART + "likeness.py", "sort", "--singles"], False, False)]


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
    ap.add_argument("--min", type=float, default=0.45, help="score at which a one-photo prospect is merged into an existing prospect (default 0.45; 0.35 is the looser tool default)")
    args = ap.parse_args(argv)
    cfg = cw.load_cfg()
    work = cw.work_root(cfg)
    reports = work / "_reports"
    run_reports = reports / "runs"
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    if not args.check and not args.dry_run:
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
