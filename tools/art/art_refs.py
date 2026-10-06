#!/usr/bin/env python3
"""Find and safely move art pieces: the building block a future art-management UI needs.

  where-used <piece>          list every file that references the piece
  move <old> <new>            git mv the piece, then rewrite every reference (and the piece's own id)
  regroup <map.json>          move many pieces in one pass (used to sub-organize a crowded folder)

A <piece> is a path under data/art/ with or without the leading 'data/art/' and '.json', e.g.
  wardrobe/weapons/greatsword   or   data/art/wardrobe/weapons/swords/greatsword.json

References are plain path strings, so the rewrite is a text replace in data/, docs/ (not _archive),
tools/, .github/ and README files. Generated prompts are not touched: regenerate them afterwards
(a pure move must leave prompts byte-identical).
"""
import argparse
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCAN_DIRS = ["data", "docs", "tools", ".github"]
SCAN_ROOT_FILES = ["README.md", "CONTRIBUTING.md"]
SCAN_SUFFIXES = {".json", ".md", ".py", ".txt"}


def norm(piece):
    p = piece.replace("\\", "/")
    if p.startswith("data/art/"):
        p = p[len("data/art/"):]
    if p.endswith(".json"):
        p = p[:-5]
    return p


def scan_files():
    files = [ROOT / f for f in SCAN_ROOT_FILES if (ROOT / f).exists()]
    for d in SCAN_DIRS:
        for p in (ROOT / d).rglob("*"):
            if p.is_file() and p.suffix in SCAN_SUFFIXES and "_archive" not in p.parts:
                files.append(p)
    return files


def refs_of(piece):
    """Files containing the piece's path (data/art/<piece>.json) or its id (\"<piece>\")."""
    path_ref = f"data/art/{piece}.json"
    id_ref = f'"{piece}"'
    hits = []
    for f in scan_files():
        text = f.read_text(encoding="utf-8")
        if path_ref in text or id_ref in text:
            hits.append(f)
    return hits


def cmd_where_used(piece):
    piece = norm(piece)
    if not (ROOT / f"data/art/{piece}.json").exists():
        sys.exit(f"no such piece: data/art/{piece}.json")
    hits = [f for f in refs_of(piece) if f != ROOT / f"data/art/{piece}.json"]
    for f in hits:
        print(f.relative_to(ROOT).as_posix())
    print(f"{len(hits)} file(s) reference {piece}", file=sys.stderr)


def cmd_move(old, new, dry_run):
    old, new = norm(old), norm(new)
    src, dst = ROOT / f"data/art/{old}.json", ROOT / f"data/art/{new}.json"
    if not src.exists():
        sys.exit(f"no such piece: {src}")
    if dst.exists():
        sys.exit(f"destination exists: {dst}")
    hits = refs_of(old)
    print(f"{old} -> {new}: {len(hits)} file(s) to update{' (dry run)' if dry_run else ''}")
    if dry_run:
        for f in hits:
            print("  " + f.relative_to(ROOT).as_posix())
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    # git mv keeps history for tracked files; a brand-new untracked piece just gets moved.
    if subprocess.run(["git", "mv", str(src), str(dst)], cwd=ROOT, capture_output=True).returncode != 0:
        shutil.move(str(src), str(dst))
    for f in hits:
        target = dst if f == src else f
        text = target.read_text(encoding="utf-8")
        text = text.replace(f"data/art/{old}.json", f"data/art/{new}.json").replace(f'"{old}"', f'"{new}"')
        target.write_text(text, encoding="utf-8")


def cmd_regroup(map_file, dry_run):
    """Move many pieces at once. The map file is JSON: {"pairs": [[old, new], ...], "extra": {"literal": "replacement"}}.
    Every path reference and quoted id is rewritten in one pass over the repo; 'extra' covers ids that are not a piece path (a theme manifest)."""
    import json
    import re
    spec = json.loads(pathlib.Path(map_file).read_text(encoding="utf-8"))
    pairs = [(norm(a), norm(b)) for a, b in spec["pairs"]]
    for old, new in pairs:
        if not (ROOT / f"data/art/{old}.json").exists():
            sys.exit(f"no such piece: data/art/{old}.json")
        if (ROOT / f"data/art/{new}.json").exists():
            sys.exit(f"destination exists: data/art/{new}.json")
    rewrite = {}
    for old, new in pairs:
        rewrite[f"data/art/{old}.json"] = f"data/art/{new}.json"
        rewrite[f'"{old}"'] = f'"{new}"'
    rewrite.update(spec.get("extra", {}))
    print(f"{len(pairs)} piece(s) to move, {len(rewrite)} reference forms{' (dry run)' if dry_run else ''}")
    if dry_run:
        return
    for old, new in pairs:
        src, dst = ROOT / f"data/art/{old}.json", ROOT / f"data/art/{new}.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if subprocess.run(["git", "mv", str(src), str(dst)], cwd=ROOT, capture_output=True).returncode != 0:
            shutil.move(str(src), str(dst))
    pattern = re.compile("|".join(re.escape(k) for k in sorted(rewrite, key=len, reverse=True)))
    changed = 0
    for f in scan_files():
        text = f.read_text(encoding="utf-8")
        new_text = pattern.sub(lambda m: rewrite[m.group(0)], text)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8", newline="")
            changed += 1
    print(f"rewrote references in {changed} file(s); regenerate prompts and check that they are unchanged")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("where-used")
    w.add_argument("piece")
    m = sub.add_parser("move")
    m.add_argument("old")
    m.add_argument("new")
    m.add_argument("--dry-run", action="store_true")
    r = sub.add_parser("regroup")
    r.add_argument("map_file")
    r.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd == "where-used":
        cmd_where_used(args.piece)
    elif args.cmd == "regroup":
        cmd_regroup(args.map_file, args.dry_run)
    else:
        cmd_move(args.old, args.new, args.dry_run)


if __name__ == "__main__":
    main()
