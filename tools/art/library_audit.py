"""Where is the art library thin? Counts the pieces in every library folder and how many cards actually use them.

    python tools/art/library_audit.py              the report: thin folders, folders that few pieces serve, pieces nothing uses
    python tools/art/library_audit.py --thin 2     what counts as thin (pieces in a folder, default 3)
    python tools/art/library_audit.py --scope wardrobe   only one top-level scope (wardrobe, motion, backgrounds, races, cosmetics, studio)

A folder is a candidate to grow when it is thin AND many cards lean on it (one piece serving every hero is the signal: everyone ends up in the same robe).
Pieces nothing references are candidates to wire into scenes before new ones are written. Identity trees (heroes, pets, dragons) and themes are left out:
they are authored per character or per pack, not drawn from.
"""
import argparse
import collections
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data" / "art"
SKIP = {"_archive", "_sets", "_templates", "_kits", "_schema", "_settings", "heroes", "pets", "dragons", "themes"}
REF = re.compile(r'"((?:data/art/)?(?:wardrobe|motion|backgrounds|races|cosmetics|studio)/[^"]+?\.json)"')


def usage():
    refs, users = collections.Counter(), collections.defaultdict(set)
    sources = [p for d in ("_sets", "_kits", "heroes") for p in (ART / d).rglob("*.json") if "_archive" not in p.parts]
    for p in sources:
        for m in set(REF.findall(p.read_text(encoding="utf-8"))):
            key = m if m.startswith("data/art/") else "data/art/" + m
            refs[key] += 1
            users[key].add(p.stem.split("-")[0])
    return refs, users


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--thin", type=int, default=3, help="a folder with this many pieces or fewer is thin (default 3)")
    ap.add_argument("--scope", help="only this top-level scope")
    ap.add_argument("--min-cards", type=int, default=8, help="cards that must use a thin folder for it to be listed as leaned on (default 8)")
    args = ap.parse_args()
    refs, users = usage()
    rows = []
    for f, files in sorted(folders(args.scope).items()):
        keys = ["data/art/" + p.relative_to(ART).as_posix() for p in files]
        top = max(keys, key=lambda k: refs[k])
        rows.append({"folder": f, "pieces": len(keys), "used": sum(1 for k in keys if refs[k]), "refs": sum(refs[k] for k in keys),
                     "heroes": len(set().union(*[users[k] for k in keys])), "top": pathlib.Path(top).stem, "toprefs": refs[top]})

    print(f"THIN FOLDERS (<= {args.thin} pieces) THAT {args.min_cards}+ CARDS LEAN ON, busiest first:")
    for r in sorted(rows, key=lambda r: -r["refs"]):
        if r["pieces"] <= args.thin and r["refs"] >= args.min_cards:
            print(f"  {r['folder']:50} pieces={r['pieces']} cards={r['refs']:5} heroes={r['heroes']:3}  top: {r['top']} ({r['toprefs']})")
    print("\nTHIN FOLDERS NOTHING OR LITTLE USES (grow only when a scene needs them):")
    for r in sorted(rows, key=lambda r: r["folder"]):
        if r["pieces"] <= args.thin and r["refs"] < args.min_cards:
            print(f"  {r['folder']:50} pieces={r['pieces']} cards={r['refs']:5}")
    print("\nFOLDERS WITH 5+ PIECES THAT NO CARD USES (wire them in before writing new ones):")
    for r in sorted(rows, key=lambda r: -(r["pieces"] - r["used"])):
        if r["pieces"] - r["used"] >= 5:
            print(f"  {r['folder']:50} {r['pieces'] - r['used']} of {r['pieces']} unused")


if __name__ == "__main__":
    main()
