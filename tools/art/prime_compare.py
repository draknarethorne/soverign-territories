#!/usr/bin/env python3
"""Compare the Prime renders of a hero side by side: Qwen and FireRed, through the normal flow and any configured alternate flow.

For each hero it finds the newest image each Prime workflow produced (Haniya_Qwen_Alpha_1_Prime_00007_.png ...) in the ComfyUI output folders, scores how close the face in it is to the face of the
photo the flow started from (the likeness tool's score: 0.55 and up is the same person, below 0.30 a different one), and writes one picture: the original, then each variant with its score.
The table at the end gives the average per variant over all heroes, which is the comparison that matters when the heroes differ.

  python tools/art/prime_compare.py                 every hero that has a render
  python tools/art/prime_compare.py Haniya Draknoxa
  python tools/art/prime_compare.py --all-renders   every render of each variant, not only the newest (to see the spread of a seed)
  python tools/art/prime_compare.py --shots all     also the first-shot experiments: P2 neutral base and P3 bare figure (1b_Experiments)
"""
import argparse
import pathlib
import re
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
sys.path.insert(0, str(ROOT / "tools/art"))
import comfy_workflows as cw  # noqa: E402
import likeness  # noqa: E402

ENGINE_NAMES = (("qwen", "Qwen"), ("firered", "FireRed"))
# the first shots: the Prime (P1, the swimsuit baseline) and the two experiment bases (1b_Experiments): P2 neutral base layer, P3 bare figure
SHOTS = {"prime": ("Alpha_1_Prime", ""), "neutral": ("Alpha_1b_NeutralBase", "P2 neutral"), "bare": ("Alpha_1b_BareBase", "P3 bare")}


def variants(cfg, hero, shots=("prime",)):
    """[(label, workflow name, flow or None, engine)] of every first-shot workflow of a hero (default: the Prime only)."""
    out = []
    for shot in shots:
        stem, tag = SHOTS[shot]
        for flow in [None] + sorted(cfg.get("flows", {})):
            if flow and not cw.flow_photo(cfg, flow, hero):
                continue
            for key, eng in ENGINE_NAMES:
                name = f"{hero}_{eng}_{stem}" + (f"_{cw.flow_suffix(flow)}" if flow else "")
                out.append((eng + (f" {tag}" if tag else "") + (f" / {flow}" if flow else ""), name, flow, key))
    return out


def renders(cfg, name, every=False):
    """The images a workflow saved (<name>_00001_.png, ...), newest first."""
    pat = re.compile(rf"^{re.escape(name)}_\d+_?\.png$")
    found = {}
    for root in cw.output_roots(cfg):
        if root.is_dir():
            for p in root.rglob(f"{name}_*.png"):
                if pat.match(p.name):
                    found[p] = p.stat().st_mtime
    ordered = sorted(found, key=lambda p: -found[p])
    return ordered if every else ordered[:1]


def source_photo(cfg, hero, flow):
    name = cw.flow_photo(cfg, flow, hero) if flow else cfg.get("photos", {}).get(hero)
    return cw.find_image(cfg, name) if name else None


class Scorer:
    """Face closeness of a picture to a reference picture, in the likeness tool's centred scores."""

    def __init__(self, embedder=None, cache=None):
        args = types.SimpleNamespace(root=None, cache=cache, embedder=embedder)
        self.cfg, self.st, self.work, self.cache, self.space = likeness.build(args)
        self.embed = embedder or likeness.Embedder()
        self.vecs = {}

    def vec(self, path):
        if path not in self.vecs:
            data = self.embed(path)
            self.vecs[path] = likeness.nz(likeness.np.array(data["v"], float) - self.space.mean) if data and data.get("v") else None
        return self.vecs[path]

    def score(self, a, b):
        va, vb = self.vec(a), self.vec(b)
        return None if va is None or vb is None else float(va @ vb)


def sheet(rows, out, size=(190, 222)):
    """rows: [(hero, [(label, path or None, score)])] -> a picture, one row per hero: the originals and renders left to right."""
    from PIL import Image, ImageDraw, ImageOps
    W, H = size
    cols = max(len(r[1]) for r in rows)
    canvas = Image.new("RGB", (90 + cols * W, len(rows) * (H + 30)), (250, 250, 250))
    d = ImageDraw.Draw(canvas)
    for r, (hero, cells) in enumerate(rows):
        y = r * (H + 30)
        d.text((6, y + H // 2), hero, fill=(0, 0, 0))
        for c, (label, path, score) in enumerate(cells):
            x = 90 + c * W
            if path:
                try:
                    canvas.paste(ImageOps.fit(Image.open(path).convert("RGB"), size), (x, y))
                except OSError:
                    pass
            d.text((x + 2, y + H + 2), label + (f"  {score:.2f}" if score is not None else ""), fill=(0, 0, 0))
    canvas.save(out)


def main(argv=None, embedder=None, cache=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("heroes", nargs="*", help="heroes (default: every hero with a render)")
    ap.add_argument("--all-renders", action="store_true", help="every render of each variant, not only the newest")
    ap.add_argument("--shots", default="prime", help="first shots to compare, comma separated or 'all': prime (P1 swimsuit), neutral (P2), bare (P3). Default: prime")
    ap.add_argument("--out", help="picture under the configured reports root (relative paths start there)")
    args = ap.parse_args(argv)
    shots = list(SHOTS) if args.shots == "all" else [s.strip() for s in args.shots.split(",") if s.strip()]
    bad = [s for s in shots if s not in SHOTS]
    if bad:
        sys.exit(f"unknown shot(s) {bad}; known: {list(SHOTS)}")
    cfg = cw.load_cfg()
    scorer = Scorer(embedder, cache)
    out = cw.storage_output_path(
        cfg, "reports", args.out or pathlib.Path("comparisons") / "primes" / "prime_compare.png",
        root=scorer.work,
    )
    heroes = [h for h in sorted(cfg.get("photos", {})) if not args.heroes or h.lower() in {x.lower() for x in args.heroes}]
    rows, totals = [], {}
    for hero in heroes:
        cells, any_render = [], False
        base = source_photo(cfg, hero, None)
        if base:
            cells.append(("original", base, None))
        for label, name, flow, _eng in variants(cfg, hero, shots):
            src = source_photo(cfg, hero, flow)
            for img in renders(cfg, name, args.all_renders):
                any_render = True
                s = scorer.score(src, img) if src else None
                cells.append((label, img, s))
                if s is not None:
                    totals.setdefault(label, []).append(s)
        if any_render:
            rows.append((hero, cells))
            print(f"{hero:10} " + "   ".join(f"{label} {('%.2f' % s) if s is not None else 'no face'}" for label, _p, s in cells[1:]))
    if not rows:
        print("no Prime renders found in the output folders yet")
        return rows, totals
    print("\naverage face score against the photo each flow started from (more is closer; 0.55 and up is the same person):")
    for label, vals in sorted(totals.items()):
        print(f"  {label:20} {sum(vals) / len(vals):.2f}   over {len(vals)} render(s)")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet(rows, out)
    print(f"picture: {out}")
    scorer.cache.save()
    return rows, totals


if __name__ == "__main__":
    main()
