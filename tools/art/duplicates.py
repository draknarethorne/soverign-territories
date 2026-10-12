#!/usr/bin/env python3
"""Find the same photo kept twice in the original-photo library, and set the extra copies aside (preview unless --apply).

A photo that moves between an angel, a prospect and Various changes its name but keeps its id, and a photo can be dropped in twice, so the same picture can end up in two folders.
Two kinds are looked for in every gallery and review folder:

  SAME PICTURE   identical bytes under two names or in two folders. One copy is kept, the others move to
                 <work>\\_archive\\<their folder>\\gallery_duplicates (never deleted; the scaled copies, headshots and frames of a moved copy are pruned by `originals`).
                 The copy kept is the first of: a chosen photo (workspaces.json photos and flows), a gallery photo over a review photo, Angels, Sisters, Prospects, Artists, Various,
                 a name that already carries its folder's prefix, the shorter name.
  SAME ID        the same photo id (image_<id>, shot_<date>, pic_<hex>) in two files whose bytes differ (a resaved or resized copy). Listed only: you pick which to keep.

  python tools/art/duplicates.py            report
  python tools/art/duplicates.py --apply    move the extra copies of identical pictures to _archive
"""
import argparse
import collections
import hashlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "workflows"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402
import originals  # noqa: E402

RANK = {"angels": 0, "sisters": 1, "models": 1, "prospects": 2, "artists": 3, "various": 4}
SCALED = re.compile(r"(?:_frame|_head)?_\d+x\d+\.(?:png|jpg|jpeg)$", re.I)


def chosen_stems(cfg):
    """Stems of the photos a hero uses (the normal photo and every flow's): the scaled name without its size and kind, so it matches the original in the gallery."""
    names = list(cfg.get("photos", {}).values())
    for flow in cfg.get("flows", {}).values():
        names += list(flow.get("photos", {}).values())
    return {SCALED.sub("", n).lower() for n in names if isinstance(n, str)}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def scan(folders):
    """[(path, group, folder, bucket)] of every original in the gallery and review folders of the library."""
    out = []
    for group, _name, folder in folders:
        for bucket in ("gallery", "review"):
            out += [(p, group, folder, bucket) for p in originals.images(folder / bucket)]
    return out


def same_pictures(files):
    """[[entries]] of two or more with identical bytes (grouped by size first, so only possible twins are read)."""
    by_size = collections.defaultdict(list)
    for e in files:
        by_size[e[0].stat().st_size].append(e)
    groups = collections.defaultdict(list)
    for entries in by_size.values():
        if len(entries) > 1:
            for e in entries:
                groups[sha(e[0])].append(e)
    return [g for g in groups.values() if len(g) > 1]


def same_ids(files):
    """[(key, [entries])] of one photo id in files whose bytes differ (a resaved or resized copy of the same photo)."""
    by_key = collections.defaultdict(list)
    for e in files:
        key = cw.photo_key(e[0].name)
        if key:
            by_key[key].append(e)
    return [(key, entries) for key, entries in by_key.items() if len(entries) > 1 and len({sha(e[0]) for e in entries}) > 1]


def keeper(entries, chosen):
    """The copy to keep: chosen first, then gallery, then the folder rank, then a name that carries its folder's prefix, then the shorter name."""
    def order(e):
        path, group, folder, bucket = e
        carries = path.name.lower().startswith(originals.prefix_of(folder.name) + "_")
        return (path.stem.lower() not in chosen, bucket != "gallery", RANK.get(group.lower(), 9), not carries, len(path.name), str(path).lower())
    return sorted(entries, key=order)[0]


def resolve(groups, work, chosen, apply):
    """Move the extra copies of each identical group into _archive. A group in which two copies are both chosen is left alone. Returns [(moved path, kept path)]."""
    moved = []
    for entries in groups:
        if sum(e[0].stem.lower() in chosen for e in entries) > 1:
            print(f"  both copies are chosen photos, left alone: {', '.join(e[0].name for e in entries)}")
            continue
        keep = keeper(entries, chosen)
        for e in entries:
            if e is keep:
                continue
            dest_dir = originals.archive_dir(e[2], work, "gallery_duplicates")
            dest = dest_dir / e[0].name
            print(f"  {'MOVED' if apply else 'would move'}  {e[0].relative_to(work).as_posix()}  (same picture as {keep[0].relative_to(work).as_posix()}; to _archive)")
            if apply:
                dest_dir.mkdir(parents=True, exist_ok=True)
                n = 1
                while dest.exists():
                    dest = dest_dir / f"{e[0].stem}_{n}{e[0].suffix}"
                    n += 1
                e[0].replace(dest)
            moved.append((e[0], keep[0]))
    return moved


def run(cfg, work, folders, apply):
    """Scan, report and (with apply) resolve. Returns (identical groups found, same-id lists)."""
    files = scan(folders)
    identical = same_pictures(files)
    ids = same_ids(files)
    print(f"duplicates: {len(files)} original(s) read; {len(identical)} picture(s) kept twice, {len(ids)} id(s) shared by different files")
    resolve(identical, work, chosen_stems(cfg), apply)
    for key, entries in ids:
        print(f"  same id {key}, different files (yours to pick): " + ", ".join(e[0].relative_to(work).as_posix() for e in entries))
    return identical, ids


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="move the extra copies of identical pictures to _archive (default: report only)")
    ap.add_argument("--root", help="the folder that holds Angels, Sisters, Prospects, Artists and Various (default: workspaces.json paths.workRoot)")
    args = ap.parse_args(argv)
    cfg = cw.load_cfg()
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    identical, ids = run(cfg, work, cw.photo_folders(cfg, args.root), args.apply)
    if identical and not args.apply:
        print("preview only; add --apply to move the extra copies")
    return 1 if (identical and not args.apply) else 0


if __name__ == "__main__":
    sys.exit(main())
