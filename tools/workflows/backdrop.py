"""Rewrite the old cream studio-backdrop wording to the light-grey standard in hand-made workflows and prompts.

Generated prompts and workflows follow data/art (`backgrounds/studio/grey-even` since Oct 26, 2026) and are refreshed by
prompts.cmd, update.cmd and deploy. Hand-made items (zz_Shots, zz_Curated, captured shots, _candidates, prompts/_edit) and
stale copies in workspaces are never regenerated, so this tool swaps the exact known phrases in place, as text, leaving
everything else (seed, inputs, toggles, formatting) byte-for-byte unchanged. Non-backdrop creams (wings, marble, blush,
a peaches-and-cream complexion) and the showcase negative "cream backdrop" are not matched.

    backdrop.py [--repo] [-w WORKSPACE ...] [--workspaces] [--root DIR ...] [--dry-run | --check]

Default applies; every changed file is first copied to workflows/.sync/backup/<stamp>/backdrop/<label>/<path>. A file
that changes between the scan and the write is skipped. --check is read-only and exits 1 while any phrase remains.
"""
import argparse
import datetime
import hashlib
import os
import pathlib
import shutil
import sys
import time

if __package__:
    from . import comfy_workflows as cw
else:
    import comfy_workflows as cw

ROOT = pathlib.Path(__file__).resolve().parents[2]
WF = ROOT / "workflows"
PROMPTS = ROOT / "prompts"
BACKUPS = WF / ".sync" / "backup"
SKIP_PARTS = {"_archive", ".sync"}
SUFFIXES = {".json", ".txt"}

# Ordered, exact, case-sensitive. The first rule turns the old cream-even and cream-beauty-light descriptions into the
# grey-even and grey-beauty-light ones, so a rewritten workflow matches what the generator now writes.
RULES = [
    ("a basic cream-coloured studio backdrop", "a plain neutral light-grey seamless studio backdrop"),
    ("Adjust the background to a basic cream colored studio drop back",
     "Adjust the background to a plain neutral light-grey seamless studio backdrop"),
    ("a solid, seamless cream-coloured studio backdrop", "a solid, seamless neutral light-grey studio backdrop"),
    ("a solid, seamless cream color studio backdrop", "a solid, seamless neutral light-grey studio backdrop"),
    ("cream studio background", "light-grey studio background"),
    ("background is cream studio", "background is a light-grey studio"),
]


def rewrite(text):
    """Return (new_text, {rule_index: count})."""
    counts = {}
    for index, (old, new) in enumerate(RULES):
        n = text.count(old)
        if n:
            counts[index] = n
            text = text.replace(old, new)
    return text, counts


def iter_files(root):
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() in SUFFIXES and path.is_file() and not SKIP_PARTS.intersection(path.relative_to(root).parts):
            yield path


def targets(args):
    out = []
    if args.repo:
        out += [("repo workflows", WF), ("repo prompts", PROMPTS)]
    if args.w or args.workspaces:
        cfg = cw.load_cfg()
        installs = cw.installs_root(cfg)
        names = args.w or sorted(p.name for p in installs.iterdir() if p.is_dir())
        for name in names:
            folder = installs / name / cfg["workflowsSubpath"]
            if folder.is_dir():
                out.append((name, folder))
            elif args.w:
                sys.exit(f"{name}: no workflows folder at {folder}")
    for root in args.root or []:
        folder = pathlib.Path(root)
        if not folder.is_dir():
            sys.exit(f"Not a folder: {folder}")
        out.append((folder.name, folder))
    return out


def scan(label, root):
    changes = []
    for path in iter_files(root):
        data = path.read_bytes()
        if b"cream" not in data:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        new, counts = rewrite(text)
        if counts:
            changes.append({"label": label, "root": root, "path": path, "sha": hashlib.sha256(data).hexdigest(),
                            "after": new.encode("utf-8"), "counts": counts})
    return changes


def apply(changes, stamp):
    written = skipped = 0
    for item in changes:
        path = item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha"]:
            print(f"  skipped (changed since scan): {path}")
            skipped += 1
            continue
        backup = BACKUPS / stamp / "backdrop" / item["label"] / path.relative_to(item["root"])
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
        temporary = path.with_name(path.name + ".backdrop-pending")
        temporary.write_bytes(item["after"])
        try:
            replace(temporary, path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise
        written += 1
    return written, skipped


def replace(temporary, path, attempts=10):
    # A virus scanner or indexer briefly holds a just-written file on Windows, so the swap is retried.
    for attempt in range(attempts):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.2 * (attempt + 1))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Swap the old cream studio-backdrop wording for the light-grey standard.")
    parser.add_argument("--repo", action="store_true", help="workflows/ and prompts/ in the repo")
    parser.add_argument("-w", action="append", metavar="WORKSPACE", help="an installed workspace (repeatable)")
    parser.add_argument("--workspaces", action="store_true", help="every installed workspace")
    parser.add_argument("--root", action="append", metavar="DIR", help="any other folder (repeatable)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="preview: list what would change")
    mode.add_argument("--check", action="store_true", help="read-only; exit 1 while any old phrase remains")
    args = parser.parse_args(argv)
    roots = targets(args)
    if not roots:
        parser.error("give --repo, -w WORKSPACE, --workspaces or --root DIR")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    total_files = 0
    totals = [0] * len(RULES)
    for label, root in roots:
        changes = scan(label, root)
        total_files += len(changes)
        for item in changes:
            for index, n in item["counts"].items():
                totals[index] += n
        line = f"{label}: {len(changes)} file(s) with old backdrop wording"
        if changes and not (args.dry_run or args.check):
            written, skipped = apply(changes, stamp)
            line += f", {written} rewritten" + (f", {skipped} skipped" if skipped else "")
        print(line)
        if args.dry_run:
            for item in changes[:5]:
                print(f"    {item['path'].relative_to(root)}")
            if len(changes) > 5:
                print(f"    ... {len(changes) - 5} more")
    for index, count in enumerate(totals):
        if count:
            print(f"  {count:6d} x '{RULES[index][0]}'")
    if args.dry_run:
        print(f"{total_files} file(s) would change (dry run)")
    elif args.check:
        print(f"{total_files} file(s) still use the old wording" if total_files else "backdrop wording: all grey")
        return 1 if total_files else 0
    elif total_files:
        print(f"backups: {BACKUPS / stamp / 'backdrop'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
