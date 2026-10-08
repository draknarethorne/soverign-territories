#!/usr/bin/env python3
"""Rank the art pieces that pull a render toward an illustrated look, and say where the realistic wording is.

Image models read vocabulary as style: "ethereal", "magical", "towering", "Dungeons & Dragons" push toward painted, game-box art;
"weathered stone", "overcast", "dust", "natural light" push toward photography. This does not change anything: it scores each background, effect and
realm piece by those words so you can decide which to rewrite, and which realm (realms/fantasy illustrated, realms/fantasy-cinematic realistic) a set should use.

Usage:  python tools/art/style_audit.py                 top 25 most illustrated pieces and a summary per folder
        python tools/art/style_audit.py --top 60 --kind backgrounds
        python tools/art/style_audit.py --prompts       also count the words in the generated scene/showcase prompts, per group
"""
import argparse
import collections
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
ILLUSTRATED = {
    "dungeons": 3, "storybook": 3, "fairy": 2, "dreamlike": 2, "surreal": 2, "magical": 2, "mystical": 2, "ethereal": 2, "enchanted": 2, "otherworldly": 2, "majestic": 2, "epic": 2,
    "glowing": 1, "radiant": 1, "shimmering": 1, "sparkling": 1, "swirling": 1, "luminous": 1, "towering": 1, "ornate": 1, "floating": 1, "vivid": 1, "saturated": 1,
    "dramatic": 1, "colossal": 1, "giant": 1, "gigantic": 1, "cascading": 1, "iridescent": 1, "prismatic": 1,
}
REALISTIC = ["weathered", "natural light", "overcast", "dust", "worn", "moss", "damp", "wet", "candlelight", "torchlight", "film", "photograph", "realistic", "real ", "soft light", "haze", "mist"]
ROOTS = {
    "backgrounds": ["data/art/backgrounds/**/*.json", "data/art/heroes/**/backgrounds/**/*.json"],
    "effects": ["data/art/wardrobe/effects/**/*.json", "data/art/heroes/**/effects/*.json"],
    "realms": ["data/art/realms/*.json"],
}


def score(text):
    low = text.lower()
    ill = sum(w * len(re.findall(rf"\b{re.escape(k)}", low)) for k, w in ILLUSTRATED.items())
    real = sum(low.count(k) for k in REALISTIC)
    return ill, real


def pieces(kind):
    seen = set()
    for pattern in ROOTS[kind]:
        for p in sorted(ROOT.glob(pattern)):
            if p in seen:
                continue
            seen.add(p)
            try:
                d = json.loads(p.read_text(encoding="utf-8-sig"))
            except ValueError:
                continue
            text = d.get("description") if isinstance(d, dict) else None
            if isinstance(text, str):
                yield p.relative_to(ROOT).as_posix(), text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--kind", choices=sorted(ROOTS), help="only backgrounds, effects or realms (default: all three)")
    ap.add_argument("--prompts", action="store_true", help="also count the style words in generated scene and showcase prompts, per group")
    args = ap.parse_args()

    rows, folder = [], collections.defaultdict(lambda: [0, 0, 0])
    for kind in ([args.kind] if args.kind else ROOTS):
        for rel, text in pieces(kind):
            ill, real = score(text)
            per100 = 100 * ill / max(len(text), 1)
            rows.append((per100, ill, real, rel, text))
            key = "/".join(rel.split("/")[:5]) if kind == "backgrounds" else "/".join(rel.split("/")[:4])
            folder[key][0] += 1
            folder[key][1] += ill
            folder[key][2] += real
    rows.sort(reverse=True)
    print(f"{len(rows)} pieces scored. Most illustrated first (points per 100 characters; ill = illustrated-lean points, real = realistic words):\n")
    for per100, ill, real, rel, text in rows[:args.top]:
        print(f"  {per100:5.2f}  ill {ill:2} real {real:2}  {rel}\n          {text[:130]}")
    print("\nPer folder (pieces, illustrated points per piece, realistic words per piece):")
    for key, (n, ill, real) in sorted(folder.items(), key=lambda kv: -kv[1][1] / kv[1][0]):
        if n >= 3:
            print(f"  {key:60} {n:4}  {ill / n:5.2f}  {real / n:5.2f}")
    if args.prompts:
        groups = collections.defaultdict(lambda: [0, 0, 0])
        for p in (ROOT / "prompts").rglob("*.txt"):
            if "_archive" in p.parts or not re.search(r"Scene|Showcase", p.name):
                continue
            ill, real = score(p.read_text(encoding="utf-8", errors="ignore"))
            g = groups[p.relative_to(ROOT / "prompts").parts[0]]
            g[0] += 1
            g[1] += ill
            g[2] += real
        print("\nGenerated scene and showcase prompts per group (prompts, illustrated points per prompt, realistic words per prompt):")
        for g, (n, ill, real) in sorted(groups.items()):
            print(f"  {g:24} {n:5}  {ill / n:6.2f}  {real / n:6.2f}")


if __name__ == "__main__":
    main()
