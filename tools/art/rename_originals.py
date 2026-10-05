#!/usr/bin/env python3
"""Rename the original reference photos to <hero>_image_<id> / <hero>_screenshot_<date>_<time>_<app> (preview unless --apply).

The library has one folder per hero (Draknara/, Drakness/ ...) with an optional gallery/ inside. Files keep their folder; only the
name changes, so a photo is never confused with another hero's once it is uploaded to ComfyUI:

  facebook_<timestamp>_<id>.jpg                  ->  <hero>_image_<id>.jpg
  Screenshot_<date>_<time>_<app>.jpg             ->  <hero>_screenshot_<date>_<time>_<app>.jpg   (app in lower case)
  z_*.txt and anything already renamed           ->  left alone

If two files of one hero would get the same name, the later ones get __2, __3 ... (the oldest facebook timestamp keeps the plain name).
Every rename is recorded in a map (old name -> new name) so later steps can fix references; --undo reverses it.

  python tools/art/rename_originals.py              # preview
  python tools/art/rename_originals.py --apply
  python tools/art/rename_originals.py --undo --apply
"""
import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
import comfy_workflows as cw  # noqa: E402

DEFAULT_MODELS = cw.work_root(cw.load_cfg()) / "Models"
MAP = ROOT / "tools/art/originals_rename_map.json"
FACEBOOK = re.compile(r"^facebook_(?P<ts>\d+)_(?P<id>\d+)(?P<ext>\.\w+)$")
SCREENSHOT = re.compile(r"^Screenshot_(?P<date>\d{8})_(?P<time>\d{6})_(?P<app>.+?)(?P<ext>\.\w+)$", re.I)


def plan(models):
    """[(hero, folder, old name, new name)] for every file that needs renaming."""
    out = []
    taken = collections.defaultdict(set)  # hero -> names that will exist
    for hero_dir in sorted(p for p in models.iterdir() if p.is_dir()):
        hero = hero_dir.name.lower()
        files = sorted(p for p in hero_dir.rglob("*") if p.is_file())
        taken[hero] |= {p.name.lower() for p in files}
        wanted = []
        for p in files:
            m = FACEBOOK.match(p.name)
            if m:
                wanted.append((int(m["ts"]), p, f"{hero}_image_{m['id']}{m['ext'].lower()}"))
                continue
            m = SCREENSHOT.match(p.name)
            if m:
                app = re.sub(r"[^a-z0-9]+", "", m["app"].lower())
                wanted.append((0, p, f"{hero}_screenshot_{m['date']}_{m['time']}_{app}{m['ext'].lower()}"))
        wanted.sort(key=lambda w: (w[2], w[0], str(w[1])))  # the oldest timestamp takes the plain name
        used = set()
        for _, p, new in wanted:
            base, ext = new.rsplit(".", 1)
            candidate, n = new, 1
            while candidate.lower() in used or (candidate.lower() in taken[hero] and candidate.lower() != p.name.lower()):
                n += 1
                candidate = f"{base}__{n}.{ext}"
            used.add(candidate.lower())
            out.append((hero_dir.name, p.parent, p.name, candidate))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default=str(DEFAULT_MODELS), help="original photo library (default: %(default)s)")
    ap.add_argument("--apply", action="store_true", help="really rename (default: preview)")
    ap.add_argument("--undo", action="store_true", help="reverse the renames recorded in the map")
    ap.add_argument("--show", type=int, default=3)
    args = ap.parse_args()
    models = pathlib.Path(args.models)
    rec = json.loads(MAP.read_text(encoding="utf-8")) if MAP.exists() else {"renames": []}
    if args.undo:
        done = 0
        for r in reversed(rec["renames"]):
            src = models / r["folder"] / r["new"]
            if src.exists() and not (models / r["folder"] / r["old"]).exists():
                print(f"  undo {r['folder']}/{r['new']} -> {r['old']}")
                if args.apply:
                    src.rename(models / r["folder"] / r["old"])
                done += 1
        if args.apply:
            rec["renames"] = []
            MAP.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(f"{done} file(s) " + ("restored" if args.apply else "would be restored"))
        return
    todo = plan(models)
    by = collections.Counter((h, "gallery" if f.name == "gallery" else "root") for h, f, o, n in todo)
    for (hero, where), n in sorted(by.items()):
        ex = [f"{o} -> {nn}" for h, f, o, nn in todo if h == hero and (f.name == "gallery") == (where == "gallery")][: args.show]
        print(f"  {hero:10} {where:8} {n:4}  e.g. {'; '.join(ex)}")
    dup = [(h, o, n) for h, f, o, n in todo if "__" in n]
    for h, o, n in dup:
        print(f"  NOTE {h}: {o} -> {n} (name already taken by another copy of the same photo)")
    print(f"{len(todo)} file(s) " + ("renamed" if args.apply else "would be renamed (preview; use --apply)"))
    if args.apply:
        for hero, folder, old, new in todo:
            (folder / old).rename(folder / new)
            rec["renames"].append({"hero": hero, "folder": str(folder.relative_to(models)).replace("\\", "/"), "old": old, "new": new})
        MAP.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(f"map saved: {MAP.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
