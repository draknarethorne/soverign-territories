#!/usr/bin/env python3
"""Give each ComfyUI workspace its own input folder holding exactly the images its workflows load (preview unless --apply).

Inputs are transient copies: the sources stay where they live (Models originals, Masters, rendered outputs). For each workspace this
  1. lists every image its workflows load (LoadImage nodes, including inside subgraphs),
  2. finds each one by name in the source folders, in this order: Models (originals), Masters, the old shared input folder, outputs,
  3. copies what is missing into <inputsRoot>/<Workspace>/ (created on --apply) and lists anything it cannot find.
Nothing is moved or deleted, so the shared folder stays as a fallback until you retire it.

  python tools/workflows/sync_inputs.py                  # preview, every workspace
  python tools/workflows/sync_inputs.py -w Drakness      # one workspace
  python tools/workflows/sync_inputs.py --apply
"""
import argparse
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}


def referenced(wf):
    names = set()

    def nodes(w):
        yield from w.get("nodes", [])
        for sg in w.get("definitions", {}).get("subgraphs", []):
            yield from sg.get("nodes", [])

    for n in nodes(wf):
        wv = n.get("widgets_values")
        if n.get("type") == "LoadImage" and isinstance(wv, list) and wv and isinstance(wv[0], str):
            names.add(wv[0])
    return names


def source_index(cfg):
    """{file name: path}, first folder wins."""
    new_out = cw.output_root(cfg)
    legacy = [pathlib.Path(cfg["sharedInput"]), pathlib.Path(cfg["sharedOutput"])]  # last: old renders must never shadow new ones
    roots = [cw.work_root(cfg) / "Models", cw.work_root(cfg) / "Masters", new_out, *legacy]
    index = {}
    for root in roots:
        if root.is_dir():
            for p in root.rglob("*"):
                if p.suffix.lower() in IMAGE_EXT and p.name not in index:
                    index[p.name] = p
    return index


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-w", "--workspace", action="append", help="a workspace (repeatable; default: every installed one)")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    cfg = cw.load_cfg()
    inputs_root = pathlib.Path(cfg["paths"]["inputsRoot"])
    index = source_index(cfg)
    total_missing = {}
    for ws in args.workspace or list(cfg["workspaces"]):
        if not cw.install_exists(cfg, ws, None):
            continue
        need = set()
        for name, p in cw.install_files(cfg, ws, None).items():
            try:
                need |= referenced(cw.read_wf(p))
            except ValueError:
                continue
        dest = inputs_root / ws
        have = {p.name for p in dest.iterdir()} if dest.is_dir() else set()
        todo = sorted(n for n in need if n not in have and n in index)
        missing = sorted(n for n in need if n not in have and n not in index)
        print(f"{ws}: loads {len(need)} image(s); {len(need & have)} already in its folder, {len(todo)} to copy, {len(missing)} not found")
        for n in missing:
            print(f"    NOT FOUND  {n}")
            total_missing[n] = total_missing.get(n, 0) + 1
        if args.apply and todo:
            dest.mkdir(parents=True, exist_ok=True)
            for n in todo:
                shutil.copy2(index[n], dest / n)
    print("copied" if args.apply else "preview only; use --apply")


if __name__ == "__main__":
    main()
