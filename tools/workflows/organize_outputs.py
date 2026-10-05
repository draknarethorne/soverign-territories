#!/usr/bin/env python3
"""Move rendered images into the folders the workflows now write to (preview unless --apply).

New renders land in <output>/<group>/<Hero>/<stage>/<family>/ because each workflow's SaveImage prefix follows its prompt's path
(the same <group>/<Hero>/<stage>/<family> as under prompts/). Older work sits in <output>/<Hero>/<stage>/ or loose in a stage
folder. This tool:
  1. sorts images whose name matches a prompt into their family folder,
  2. carries everything else (archive folders, hand-made files) along to the same place under <group>/<Hero>/.
File names are kept (a file whose name is already taken in its destination gets a __2 suffix) and nothing is deleted. Folders that are not a hero's (Base, ST, Experimental ...) are left alone.

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
    out_root = pathlib.Path(args.output) if args.output else cw.output_root(cfg)
    if not out_root.is_dir():
        sys.exit(f"output folder not found: {out_root}")
    groups = cw.hero_groups()
    where = {}
    for engine in ("qwen", "minimax"):
        for item in cw.prompt_index(cfg, engine):
            where[item["stem"]] = item["prefix"].rsplit("/", 1)[0]  # <group>/<Hero>/<folder>/<family...>

    moves = []  # (source file, destination folder, how)
    sources = []  # (hero, group, folder to scan)
    for hero, group in sorted(groups.items()):
        if args.hero and hero.lower() != args.hero.lower():
            continue
        for folder in (out_root / hero, out_root / group / hero):
            if folder.is_dir():
                sources.append((hero, group, folder))
    for hero, group, folder in sources:
        new_home = out_root / group / hero
        for f in sorted(p for p in folder.rglob("*") if p.is_file()):
            rel = f.relative_to(folder)
            m = NAME.match(f.name)
            sortable = len(rel.parts) in (1, 2) and m and m["hero"] == hero  # loose in the hero folder or a stage folder, not in a subfolder
            dest, how = new_home / rel.parent, "carried"
            if sortable:
                target = where.get(f"{hero}_{RENAMED.get(m['rest'], m['rest'])}")
                if target:
                    dest, how = out_root / target, "sorted"
            if f.parent != dest:
                moves.append((f, dest, how))

    tally = collections.Counter((d.relative_to(out_root).as_posix(), how) for _, d, how in moves)
    for (dest, how), n in sorted(tally.items()):
        ex = [f.name for f, d, h in moves if d.relative_to(out_root).as_posix() == dest and h == how][: args.show]
        print(f"  {n:5} {how:7} -> {dest}/   e.g. {', '.join(ex)}")
    print(f"{len(moves)} file(s) " + ("moved" if args.apply else "would move (preview; use --apply)"))
    if args.apply:
        for f, dest, _ in moves:
            dest.mkdir(parents=True, exist_ok=True)
            target = dest / f.name
            n = 1
            while target.exists():  # a different image already has this name there: keep both
                n += 1
                target = dest / f"{f.stem}__{n}{f.suffix}"
                print(f"  RENAMED {f.name} -> {target.name} (the name was taken in {dest.relative_to(out_root).as_posix()}/)")
            shutil.move(str(f), str(target))
        for hero, group, folder in sources:  # tidy emptied old folders (only empty ones)
            for d in sorted((p for p in folder.rglob("*") if p.is_dir()), reverse=True) + [folder]:
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()


if __name__ == "__main__":
    main()
