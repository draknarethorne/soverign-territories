#!/usr/bin/env python3
"""Point the stage templates' resize-to-total-pixels nodes at the standard image size (workspaces.json `standardSize`, 944x1104 = 0.993896 MP, because ComfyUI counts a megapixel as 1024 x 1024), so an edit keeps the standard size until the final upscale.

    python tools/workflows/align_templates.py            preview
    python tools/workflows/align_templates.py --apply    write workflows/_templates/ST*.json

Left at 1 megapixel, FireRed and Flux turn a 944x1104 image into 947x1107, which is not a multiple of 16. Qwen needs nothing: its FluxKontextImageScale snaps 944x1104 to itself.
A pulled-back template that undoes this fails `test_templates.py`; run this again (then `make`, and `deploy` to bring the workspaces along: deploy also fixes the workflows they hold).
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import comfy_workflows as cw  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    cfg = cw.load_cfg()
    mp = cw.standard_megapixels(cfg)
    changed = 0
    for p in sorted((cw.WF / "_templates").glob("ST*.json")):
        wf = cw.read_wf(p)
        nodes = len(list(cw.size_nodes(wf)))
        if cw.align_size(wf, cfg):
            changed += 1
            print(f"  {'aligned' if args.apply else 'would align'}  {p.name}: {nodes} resize node(s) -> {mp} MP")
            if args.apply:
                cw.write_wf(p, wf)
    print(f"{changed} template(s) {'changed' if args.apply else 'to change'}; target {mp} MP" + ("" if args.apply else " (preview: add --apply)"))


if __name__ == "__main__":
    main()
