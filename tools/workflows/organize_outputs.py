#!/usr/bin/env python3
"""Sort rendered images into the family folders the workflows now write to (preview unless --apply).

New renders land in <output>/<Hero>/<stage>/<family>/ because each workflow's SaveImage prefix follows its prompt's folder.
Images made before that sit loose in <output>/<Hero>/<stage>/. This moves them to the folder their name belongs in, so old and
new work line up. File names are never changed, nothing is deleted, and subfolders such as archive/ are left alone.

  python tools/workflows/organize_outputs.py                 # preview, all heroes
  python tools/workflows/organize_outputs.py --hero Drakness # preview one hero
  python tools/workflows/organize_outputs.py --apply         # move
"""
import argparse
import collections
import pathlib
import re
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402

# Names that were renamed when the layout changed: old name part -> new name part.
RENAMED = {"Scene_TestGlamour": "Scene_Glamour_Test"}
NAME = re.compile(r"^(?P<hero>[A-Za-z]+)_(?P<engine>Qwen|FireRed|MiniMax)_(?P<rest>.+?)_\d{5}_\.[A-Za-z0-9]+$")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero")
    ap.add_argument("--output", help="ComfyUI output folder (default: sharedOutput in workspaces.json)")
    ap.add_argument("--apply", action="store_true", help="really move the files (default: preview)")
    ap.add_argument("--show", type=int, default=3, help="example moves to list per destination")
    args = ap.parse_args()
    cfg = cw.load_cfg()
    out_root = pathlib.Path(args.output or cfg["sharedOutput"])
    if not out_root.is_dir():
        sys.exit(f"output folder not found: {out_root}")
    where = {}
    for engine in ("qwen", "minimax"):
        for item in cw.prompt_index(cfg, engine):
            where[item["stem"]] = (item["hero"], item["prefix"].rsplit("/", 1)[0])  # <Hero>/<folder>/<family...>
    moves, tally, unknown = [], collections.Counter(), collections.Counter()
    for hero_dir in sorted(p for p in out_root.iterdir() if p.is_dir()):
        if args.hero and hero_dir.name.lower() != args.hero.lower():
            continue
        for stage_dir in sorted(p for p in hero_dir.iterdir() if p.is_dir() and p.name != "archive"):
            for f in sorted(stage_dir.iterdir()):
                m = NAME.match(f.name) if f.is_file() else None
                if not m or m["hero"] != hero_dir.name:
                    continue
                rest = RENAMED.get(m["rest"], m["rest"])
                target = where.get(f"{m['hero']}_{rest}")
                if target is None:
                    unknown[stage_dir.relative_to(out_root).as_posix()] += 1
                    continue
                dest = out_root / target[1]
                if dest != stage_dir:
                    moves.append((f, dest))
                    tally[dest.relative_to(out_root).as_posix()] += 1
    for dest, n in sorted(tally.items()):
        ex = [f.name for f, d in moves if d.relative_to(out_root).as_posix() == dest][: args.show]
        print(f"  {n:5} -> {dest}/   e.g. {', '.join(ex)}")
    for folder, n in sorted(unknown.items()):
        print(f"  {n:5} left in {folder}/ (no matching prompt: hand-made or renamed)")
    print(f"{len(moves)} image(s) " + ("moved" if args.apply else "would move (preview; use --apply)"))
    if args.apply:
        for f, dest in moves:
            dest.mkdir(parents=True, exist_ok=True)
            if (dest / f.name).exists():
                print(f"  SKIP {f.name}: already in {dest}")
                continue
            shutil.move(str(f), str(dest / f.name))


if __name__ == "__main__":
    main()
