"""Where is the art library thin, over-used, or built from shortcuts? Re-run it as the library grows; it walks whatever folders exist.

    python tools/art/library_audit.py                 the report
    python tools/art/library_audit.py --scope wardrobe     only one top-level scope (wardrobe, motion, backgrounds, races, cosmetics, studio)
    python tools/art/library_audit.py --unused        also list pieces no card uses (information only: pieces are written ahead of the scenes that need them)
    python tools/art/library_audit.py --thin 2 --heroes 10     tune what counts as thin, and how many heroes make a piece "shared"

What it reports
  OVER-USED   one piece does most of a folder's work for many heroes (everyone in the same robe). That is a sign the folder needs more variation, unless the sharing is on purpose:
              list those in data/art/_settings/library-audit.json under "intentional" (a studio default, a base robe all ten sisters wear) and they are shown as intentional, not as gaps.
  THIN        folders with few pieces that are not over-used: growth candidates for when a scene needs them.
  SHORTCUTS   pieces that paste several items into one sentence (a necklace, earrings and rings in one jewellery piece), or hard-code a metal instead of {{METAL}}: write the real pieces and
              compose them with a set (`includes`).
Identity trees (heroes, pets, dragons), themes and the per-set card folders are left out: they are authored per character or pack, not drawn from.
"""
import argparse
import collections
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data" / "art"
ALLOW = ART / "_settings" / "library-audit.json"
SKIP = {"_archive", "_sets", "_templates", "_kits", "_schema", "_settings", "heroes", "pets", "dragons", "themes"}
REF = re.compile(r'"((?:data/art/)?(?:wardrobe|motion|backgrounds|races|cosmetics|studio)/[^"]+?\.json)"')
JEWEL = {"necklace": r"necklace|pendant|choker|locket", "earrings": r"earring", "rings": r"\brings?\b", "bracelet": r"bracelet|bangle|\bcuff\b",
         "anklet": r"anklet", "belly": r"belly"}
METALS = re.compile(r"\b(gold|golden|silver|bronze|copper|platinum)\b", re.I)


def load_allow():
    return json.loads(ALLOW.read_text(encoding="utf-8")).get("intentional", {}) if ALLOW.exists() else {}


def load_ignored_groups():
    """Groups whose cards share pieces on purpose (ten sisters in one scene or robe for a unified picture); their use is not counted as over-use."""
    return json.loads(ALLOW.read_text(encoding="utf-8")).get("ignoreGroups", {}) if ALLOW.exists() else {}


def usage():
    refs, users, indirect = collections.Counter(), collections.defaultdict(set), set()
    ignored = load_ignored_groups()
    for d in ("_sets", "_kits", "heroes"):
        for p in (ART / d).rglob("*.json"):
            if "_archive" in p.parts or p.relative_to(ART / d).parts[0] in ignored:
                continue
            for m in set(REF.findall(p.read_text(encoding="utf-8"))):
                key = m if m.startswith("data/art/") else "data/art/" + m
                refs[key] += 1
                users[key].add(p.stem.split("-")[0])
    for p in ART.rglob("*.json"):  # a piece that another piece extends or includes is in use through it
        if any(x in p.parts for x in SKIP):
            continue
        for m in set(REF.findall(p.read_text(encoding="utf-8"))):
            indirect.add(m if m.startswith("data/art/") else "data/art/" + m)
    return refs, users, indirect


def folders(scope):
    out = collections.defaultdict(list)
    for p in ART.rglob("*.json"):
        rel = p.relative_to(ART)
        if any(part in SKIP or part.startswith(".") for part in rel.parts) or len(rel.parts) < 3:
            continue
        if scope and rel.parts[0] != scope:
            continue
        out[rel.parent.as_posix()].append(p)
    return out


def allowed(folder, allow):
    return next((why for key, why in allow.items() if folder == key or folder.startswith(key + "/")), None)


def shortcuts(files):
    """Jewellery and arm pieces that bundle several items, stand in for one ('matching ...'), or hard-code a metal."""
    found = []
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        text = d.get("description")
        if not isinstance(text, str) or d.get("kind") not in ("jewelry", "arms") or d.get("includes"):
            continue
        plain = re.sub(r"belly[- ]button (ring|hoop)|belly ring", "belly", text, flags=re.I)  # a belly ring is one item, not a ring
        plain = re.sub(r"ear cuffs?", "earring", plain, flags=re.I)
        kinds = [k for k, rx in JEWEL.items() if re.search(rx, plain, re.I)]
        rel = p.relative_to(ART).as_posix()
        if len(kinds) >= 2:
            found.append((rel, "bundles " + ", ".join(kinds)))
        elif "matching" in text.lower():
            found.append((rel, "a stand-in ('matching ...') rather than a real item"))
        elif METALS.search(text) and "{{METAL}}" not in text:
            found.append((rel, f"hard-codes a metal ({METALS.search(text).group(1)}) instead of {{{{METAL}}}}"))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--thin", type=int, default=3, help="a folder with this many pieces or fewer is thin (default 3)")
    ap.add_argument("--heroes", type=int, default=8, help="a piece used by this many heroes is shared (default 8)")
    ap.add_argument("--share", type=float, default=0.4, help="a piece is over-used when it does this share of its folder's work (default 0.4)")
    ap.add_argument("--scope", help="only this top-level scope")
    ap.add_argument("--unused", action="store_true", help="also list folders with 5+ pieces no card uses")
    args = ap.parse_args()
    allow = load_allow()
    ignored = load_ignored_groups()
    refs, users, indirect = usage()
    rows, bundles = [], []
    for f, files in sorted(folders(args.scope).items()):
        keys = ["data/art/" + p.relative_to(ART).as_posix() for p in files]
        top = max(keys, key=lambda k: refs[k])
        total = sum(refs[k] for k in keys)
        rows.append({"folder": f, "pieces": len(keys), "used": sum(1 for k in keys if refs[k] or k in indirect), "refs": total, "top": pathlib.Path(top).stem, "toprefs": refs[top],
                     "topheroes": len(users[top]), "share": (refs[top] / total) if total else 0})
        if f.startswith(("wardrobe/jewelry", "wardrobe/accessories")):
            bundles += shortcuts(files)

    over = [r for r in rows if r["topheroes"] >= args.heroes and r["share"] >= args.share]
    # an allowlist entry can be a whole folder, or one piece (folder/piece) that is that piece's job by design
    def why_allowed(r):
        return allowed(r["folder"], allow) or allowed(r["folder"] + "/" + r["top"], allow)

    flagged = [r for r in over if not why_allowed(r)]
    intended = [r for r in over if why_allowed(r)]
    print(f"OVER-USED: one piece does {int(args.share * 100)}%+ of its folder's work for {args.heroes}+ heroes (add a folder to data/art/_settings/library-audit.json if it is on purpose):")
    if ignored:
        print("  (not counted, shared on purpose: " + "; ".join(f"{g}: {why}" for g, why in ignored.items()) + ")")
    for r in sorted(flagged, key=lambda r: -r["topheroes"]):
        print(f"  {r['folder']:48} {r['pieces']:2} pieces   {r['top']} in {r['toprefs']} cards for {r['topheroes']} heroes ({int(r['share'] * 100)}%)")
    if not flagged:
        print("  none")
    if intended:
        print("  intentional (allowlist): " + ", ".join(r["folder"] for r in sorted(intended, key=lambda r: r["folder"])))

    print(f"\nTHIN (<= {args.thin} pieces) AND NOT OVER-USED: growth candidates, add when a scene needs them:")
    for r in rows:
        if r["pieces"] <= args.thin and r not in over:
            print(f"  {r['folder']:48} {r['pieces']} pieces, {r['refs']} card uses")

    print("\nSHORTCUTS (write real pieces, compose them with a set):")
    for path, why in bundles:
        print(f"  {path:60} {why}")
    if not bundles:
        print("  none")

    if args.unused:
        print("\nUNUSED (information only):")
        for r in sorted(rows, key=lambda r: -(r["pieces"] - r["used"])):
            if r["pieces"] - r["used"] >= 5:
                print(f"  {r['folder']:48} {r['pieces'] - r['used']} of {r['pieces']} unused")


if __name__ == "__main__":
    main()
