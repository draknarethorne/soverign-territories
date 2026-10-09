"""Do the roster documents in docs/codex/heroes still match the data? The JSON wins, so a difference means the document needs updating.

    python tools/art/codex_drift.py            the report
    python tools/art/codex_drift.py --check    exit 1 on any drift (validate.cmd runs this)

Checked:
  sovereign_dawn_codex.md        every SD-001..SD-030 row against its card (name, rarity, element, archetype, class, creature type, race, sex, companion)
  drakn_sisters_physique.md      each sister's palette and physique lines against her identity JSON
  drakn_bound_physique.md        the same for the Drakn Bound men
  elder_dragons_details.md       each dragon's identity fields against its JSON
  angel_primes_physique.md and angel_primes_codex.md   each angel's build, element and alignment rank against the identity
"""
import argparse
import glob
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/codex/heroes"
ART = ROOT / "data/art"


def read(name):
    return (DOCS / name).read_text(encoding="utf-8")


def cards():
    out = {}
    for f in glob.glob(str(ROOT / "data/cards/sovereign-dawn/**/*.json"), recursive=True):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except ValueError:
            continue
        for c in (d.get("cards") if isinstance(d, dict) and "cards" in d else [d]):
            n = c.get("collectionNumber") if isinstance(c, dict) else None
            if n and re.fullmatch(r"SD-0(0\d|1\d|2\d|30)", n):
                out[n] = c
    return out


def check_roster():
    problems = []
    by_no = cards()
    seen = 0
    for line in read("sovereign_dawn_codex.md").splitlines():
        m = re.match(r"\| (SD-\d+)\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        seen += 1
        c = by_no.get(m.group(1))
        if not c:
            problems.append(f"sovereign_dawn_codex.md: {m.group(1)} has no card")
            continue
        cells = [x.strip() for x in m.group(2).split("|")]
        want = [c["name"], f'{c["rarity"]["stars"]} - {c["rarity"]["tier"]}', c["element"], c["archetype"], c["class"], c["creatureType"], c["race"], c["sex"], c.get("companion") or "n/a"]
        for label, a, b in zip(("name", "rarity", "element", "archetype", "class", "creature type", "race", "sex", "companion"), cells, want):
            if a != b:
                problems.append(f"sovereign_dawn_codex.md: {m.group(1)} {label} is '{a}', the card says '{b}'")
    if seen != len(by_no):
        problems.append(f"sovereign_dawn_codex.md: {seen} roster rows, {len(by_no)} cards")
    return problems


def check_blocks(doc, pattern, keys_pal, keys_phy):
    problems = []
    text = read(doc)
    for p in sorted((ART / "heroes").glob(pattern)):
        art = json.loads(p.read_text(encoding="utf-8"))["art"]
        name = p.stem.replace("-", " ").title()
        m = re.search(r"### SD-\d+: " + re.escape(name) + r"\n(.*?)(?=\n### |\n## |\Z)", text, re.S)
        if not m:
            problems.append(f"{doc}: no section for {name}")
            continue
        for src, keys in ((art["palette"], keys_pal), (art["physique"], keys_phy)):
            for k in keys:
                mm = re.search(r"(?:^\s*\* |, )" + k + r": (\"(?:[^\"\\]|\\.)*\"|\[[^\]]*\])", m.group(1), re.M)
                if not mm:
                    if k in src:
                        problems.append(f"{doc}: {name} is missing {k}")
                    continue
                try:
                    got = json.loads(mm.group(1).split(" (the card")[0])
                except ValueError:
                    got = mm.group(1)
                if got != src.get(k, [] if k.endswith(("Negatives", "Marks")) else None):
                    problems.append(f"{doc}: {name} {k} differs from the identity JSON")
    return problems


def check_dragons():
    problems = []
    text = read("elder_dragons_details.md")
    for p in sorted((ART / "dragons/elder-dragons").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        name = p.stem.capitalize()
        m = re.search(r"### SD-\d+: " + name + r" .*?(?=\n### |\n## |\Z)", text, re.S)
        if not m:
            problems.append(f"elder_dragons_details.md: no section for {name}")
            continue
        for k in ("description", "silhouette", "scaleTexture", "wingMembrane", "hornsAndCrest", "elementalVenting", "notes"):
            if json.dumps(d[k], ensure_ascii=False) not in m.group(0):
                problems.append(f"elder_dragons_details.md: {name} {k} differs from the identity JSON")
    return problems


def check_angels():
    problems = []
    phys, codex = read("angel_primes_physique.md"), read("angel_primes_codex.md")
    for p in sorted((ART / "heroes/angel-primes").glob("*/*.json")):
        if p.parent.name == "alpha":
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        name = p.stem.capitalize()
        if d["art"]["physique"]["build"] not in phys:
            problems.append(f"angel_primes_physique.md: {name}'s build differs from the identity JSON")
        prof = d["profile"]
        row = re.search(r"^\| AP-\d+ \| " + name + r" \| (.*)$", codex, re.M)
        if not row or prof["element"] not in row.group(1) or f"({prof['alignmentRank']})" not in row.group(1):
            problems.append(f"angel_primes_codex.md: {name}'s element or alignment rank differs from the identity JSON")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    problems = (check_roster()
                + check_blocks("drakn_sisters_physique.md", "drakn-sisters/*-thorne.json", ("primaryColor", "accentColors", "metal", "eyeColor", "hairColor", "skinTone", "eyeColorNegatives", "skinColorNegatives", "hairColorNegatives"), ("build", "torso", "bust", "arms", "hips", "legs", "distinguishingMarks", "raceAlignment"))
                + check_blocks("drakn_bound_physique.md", "drakn-bound/*.json", ("primaryColor", "accentColors", "eyeColor", "hairColor", "skinTone", "eyeColorNegatives", "skinColorNegatives", "hairColorNegatives"), ("build", "chest", "arms", "waist", "legs", "distinguishingMarks", "raceAlignment"))
                + check_dragons() + check_angels())
    for p in problems:
        print(p)
    print(f"\n{len(problems)} drift problem(s) between docs/codex/heroes and the data" if problems else "docs/codex/heroes matches the data")
    return 1 if (problems and args.check) else 0


if __name__ == "__main__":
    sys.exit(main())
