#!/usr/bin/env python3
"""Point every workflow at the renamed original photos (preview unless --apply).

After tools/art/rename_originals.py renamed the originals, the copies in the shared ComfyUI input folder and every workflow that loads
them still use the old facebook_/Screenshot_ names. This tool:
  1. renames those copies in the shared input folder (old name -> new name, from tools/art/originals_rename_map.json),
  2. updates every LoadImage in the repo workflows (generated, curated, templates, local test copies) and in every ComfyUI install,
  3. sends a workflow that loads ANOTHER hero's original photo to its own hero's photo (workspaces.json "photos"; the Angel Primes
     test beds and curated copies are left as they are),
  4. keeps the named copy of the image value (widgets_values_named.image) equal to the real one.
Files whose old name is not in the map (photos that were never in the library) are left alone and listed.

To change which photo is "the" original for a sister, once you have settled on it:
  python tools/workflows/rename_inputs.py --photo Draknara=draknara_image_7500642754476958031.jpg --apply
That edits "photos" in workspaces.json and moves her workflows (repo and every install) from her old photo to the new one.

  python tools/workflows/rename_inputs.py            # preview
  python tools/workflows/rename_inputs.py --apply
"""
import argparse
import collections
import datetime
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402

MAP = cw.ROOT / "tools/art/originals_rename_map.json"
ORIGINAL = re.compile(r"^(?P<owner>[a-z]+)_(image|screenshot)_")
KEEP_AS_IS_GROUPS = {"angel-primes"}


def old_to_new():
    """{old name: new name}; a photo kept in two hero folders belongs to the hero whose copy is in its root folder."""
    out, rank = {}, {}
    for r in json.loads(MAP.read_text(encoding="utf-8"))["renames"]:
        r_rank = 0 if "/" not in r["folder"] else 1
        if r["old"] not in out or r_rank < rank[r["old"]]:
            out[r["old"]], rank[r["old"]] = r["new"], r_rank
    return out


def load_nodes(wf):
    yield from (n for n in wf.get("nodes", []) if n.get("type") == "LoadImage")
    for sg in wf.get("definitions", {}).get("subgraphs", []):
        yield from (n for n in sg.get("nodes", []) if n.get("type") == "LoadImage")


def set_image(node, value):
    node["widgets_values"][0] = value
    named = node.get("widgets_values_named")
    if isinstance(named, dict) and "image" in named:
        named["image"] = value


def fix_workflow(wf, hero, group, mapping, photos, wrong_photo_fix, retarget=None):
    """Edit one workflow in place; return (renamed, rerouted, synced)."""
    renamed = rerouted = synced = 0
    for node in load_nodes(wf):
        if not isinstance(node.get("widgets_values"), list) or not node["widgets_values"]:
            continue
        cur = node["widgets_values"][0]
        new = mapping.get(cur, cur)
        if retarget and hero in retarget and new == retarget[hero][0]:
            new = retarget[hero][1]
            rerouted += 1
        if new != cur:
            renamed += 1
        m = ORIGINAL.match(new)
        if wrong_photo_fix and hero and group not in KEEP_AS_IS_GROUPS and m and m["owner"] != hero.lower() and hero in photos:
            new = photos[hero]
            rerouted += 1
        if new != cur:
            set_image(node, new)
        else:
            named = node.get("widgets_values_named")
            if isinstance(named, dict) and named.get("image") not in (None, cur):
                set_image(node, cur)
                synced += 1
    return renamed, rerouted, synced


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--input", help="one input folder to process (default: the shared one and every workspace input folder)")
    ap.add_argument("--photo", action="append", default=[], metavar="HERO=FILE", help="make FILE the original photo for HERO (repeatable)")
    args = ap.parse_args()
    cfg = cw.load_cfg()
    mapping, photos = old_to_new(), dict(cfg.get("photos", {}))
    retarget = {}
    for spec in args.photo:
        hero, _, new = spec.partition("=")
        if hero not in photos or not new:
            sys.exit(f"--photo needs HERO=FILE for one of: {', '.join(photos)}")
        if not any((d / new).exists() for d in cw.input_dirs(cfg)):
            print(f"note: {new} is not in any input folder yet; copy it there before running the workflows")
        retarget[hero] = (photos[hero], new)
        photos[hero] = new
        print(f"photo for {hero}: {retarget[hero][0]} -> {new}")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    groups = cw.hero_groups()

    # 1. the copies in every input folder (the shared one and each workspace's own)
    for inp in ([pathlib.Path(args.input)] if args.input else cw.input_dirs(cfg)):
        ren, skipped, unmapped = [], [], []
        for p in sorted(inp.iterdir()):
            if not p.is_file() or not re.match(r"^(facebook_|screenshot_)", p.name, re.I):
                continue
            new = mapping.get(p.name)
            if not new:
                unmapped.append(p.name)
            elif (inp / new).exists():
                skipped.append((p.name, new))
            else:
                ren.append((p, new))
        print(f"input folder {inp}: {len(ren)} to rename, {len(skipped)} already have the new name, {len(unmapped)} not in the map")
        for p, new in ren[:4]:
            print(f"    {p.name} -> {new}")
        for n in unmapped:
            print(f"    LEFT  {n} (never in the library)")
        if args.apply:
            for p, new in ren:
                p.rename(inp / new)

    # 2-4. workflows: repo and every install
    targets = []
    for root in (cw.WF, ):
        for p in sorted(root.rglob("*.json")):
            if ".sync" in p.parts or "_archive" in p.parts or p.name == "workspaces.json":
                continue
            rel = p.relative_to(cw.WF).parts
            curated = rel[0] == "_curated"
            hero = cw.hero_of(p.name)
            targets.append(("repo", p, hero, groups.get(hero), not curated and rel[0] not in ("_templates",)))
    installs_root = pathlib.Path(cfg["installsRoot"])
    for d in sorted(installs_root.iterdir()):
        sub = d / cfg["workflowsSubpath"]
        if d.is_dir() and d.name != "ComfyUI" and sub.is_dir():
            for p in sorted(sub.glob("*.json")):
                hero = cw.hero_of(p.name)
                targets.append((d.name, p, hero, groups.get(hero), True))
    tally = collections.Counter()
    per_hero = collections.Counter()
    for where, p, hero, group, wrong_fix in targets:
        try:
            wf = cw.read_wf(p)
        except ValueError:
            continue
        before = json.dumps(wf, sort_keys=True)
        r, f, s = fix_workflow(wf, hero, group, mapping, photos, wrong_fix, retarget)
        if json.dumps(wf, sort_keys=True) == before:
            continue
        tally[(where, "renamed")] += r > 0
        tally[(where, "rerouted to her own photo")] += f > 0
        tally[(where, "named value synced")] += (r == 0 and f == 0 and s > 0)
        if f and hero:
            per_hero[hero] += 1
        if args.apply:
            if where != "repo":
                cw.backup(stamp, where, p.name, p)
            cw.write_wf(p, wf)
    for (where, what), n in sorted(tally.items()):
        if n:
            print(f"  {where:24} {n:5} workflow(s): {what}")
    if per_hero:
        print("  sent to their own photo:", ", ".join(f"{h} {n}" for h, n in sorted(per_hero.items())))
    if args.apply and retarget:
        text = cw.CFG_PATH.read_text(encoding="utf-8")
        for hero, (old, new) in retarget.items():
            text = text.replace(f'"{hero}": "{old}"', f'"{hero}": "{new}"')
        cw.CFG_PATH.write_text(text, encoding="utf-8")
    print("done" if args.apply else "preview only; use --apply")


if __name__ == "__main__":
    main()
