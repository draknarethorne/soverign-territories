#!/usr/bin/env python3
"""Find and safely move art pieces: the building block a future art-management UI needs.

  where-used <piece>          list every file that references the piece
  move <old> <new>            git mv the piece, then rewrite every reference (and the piece's own id)

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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("where-used")
    w.add_argument("piece")
    m = sub.add_parser("move")
    m.add_argument("old")
    m.add_argument("new")
    m.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd == "where-used":
        cmd_where_used(args.piece)
    else:
        cmd_move(args.old, args.new, args.dry_run)


if __name__ == "__main__":
    main()
