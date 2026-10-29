"""Do the heroes' defined looks reach their prompts? Checks every hero identity (angels, sisters, bound heroes) so no prompt needs a hand edit.

    python tools/art/identity_audit.py            the report
    python tools/art/identity_audit.py --check    exit 1 on any problem (validate.cmd runs this)

For each hero:
  COLOURS   hair, eye and skin colour are defined (not left to the photo) and each has its negative list, so the Prime forces them onto the photo;
  PRIME     the generated Prime prompt (1_Alpha/1_Prime, or the older X_Pose) carries those exact colours;
  BARE      the generated Bare prompt (1_Alpha/2_Bare) applies her or his individual build, and the Prime does NOT (it uses the standard figure) where the card says so;
  BULK      female angels only: no bulk words (strong, muscular, sturdy, solid, powerful ...) in the build, so no woman reads as a body builder; toned abs, arms and legs are welcome, and height, leg length, softness and curve may vary freely (the men may range from lean to heavily built).
  NOTES     (information only) a woman's build that names bulk, even as a negation ("without bulk"), because a model reads it as the thing named.
The test heroes (alpha/female, alpha/male) are left to the photo on purpose: they exist to try a photo before it becomes an angel.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data/art"
STRONG = re.compile(r"\b(strong|muscul\w*|sturdy|solid|powerful|massive|heavily|thick|stocky|burly|brawny|wiry-strong)\b", re.I)
PHOTO = re.compile(r"reference|photo|unchanged", re.I)
NOTES = []


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 -]+", " ", (text or "").lower())).strip()


def positive(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    return norm(text.split("negative prompt:")[0].split("prompt:", 1)[-1])


def find(group, hero, names):
    for name in names:
        hits = sorted((ROOT / "prompts" / group).rglob(name))
        if hits:
            return hits[0]
    return None


def heroes():
    for group, pattern in (("angel-primes", "angel-primes/*/*.json"), ("drakn-sisters", "drakn-sisters/*-thorne.json"), ("drakn-bound", "drakn-bound/*.json")):
        for p in sorted((ART / "heroes").glob(pattern)):
            if p.parent.name == "alpha":
                continue
            yield group, p


def audit():
    rows = []
    for group, p in heroes():
        d = json.loads(p.read_text(encoding="utf-8"))
        art = d.get("art", {})
        pal, phy = art.get("palette", {}), art.get("physique", {})
        hero = p.stem.split("-")[0].capitalize()
        female = "bust" in phy
        problems = []
        eye = pal.get("eyeColorGlamour") or pal.get("eyeColor") or ""
        for label, key, neg in (("hair", "hairColor", "hairColorNegatives"), ("eyes", None, "eyeColorNegatives"), ("skin", "skinTone", "skinColorNegatives")):
            value = eye if key is None else pal.get(key, "")
            if not value:
                problems.append(f"{label} colour is not defined")
            elif PHOTO.search(value):
                problems.append(f"{label} colour is left to the photo ({value[:40]}...)")
            if not pal.get(neg):
                problems.append(f"no {neg}")
        prime = find(group, hero, (f"{hero}_Alpha_1_Prime.txt", f"{hero}_X_Pose.txt"))
        bare = find(group, hero, (f"{hero}_Alpha_2_Bare_Figure.txt",))
        if not prime:
            problems.append("no Prime prompt")
        else:
            text = positive(prime)
            for label, value in (("hair", pal.get("hairColor", "")), ("eyes", eye), ("skin", pal.get("skinTone", ""))):
                if value and norm(value) not in text and norm(value.split(",")[0]) not in text:
                    problems.append(f"the Prime prompt does not carry the {label} colour")
        if group == "angel-primes" and female and STRONG.search(phy.get("build", "") + " " + phy.get("arms", "") + " " + phy.get("legs", "")):
            problems.append("a female angel's build uses a strength word: " + ", ".join(sorted(set(m.group(0).lower() for m in STRONG.finditer(' '.join(str(v) for v in phy.values()))))))
        if group == "angel-primes" and bare:
            body = norm(phy.get("build", ""))
            if body and body not in positive(bare):
                problems.append("the Bare prompt does not apply the individual build")
            if prime and body and body in positive(prime):
                problems.append("the Prime prompt carries the individual build (it should use the standard figure)")
        if group in ("angel-primes", "drakn-sisters") and female:
            named = re.findall(r"\b(?:bulk\w*|bodybuild\w*|body-build\w*)\b", " ".join(str(phy.get(k, "")) for k in ("build", "torso", "arms", "hips", "legs")), re.I)
            if named:
                NOTES.append(f"{group:14} {hero:11} names bulk ({', '.join(sorted(set(n.lower() for n in named)))}); a model reads a negation as the thing named, so describe the toned look positively")
        rows.append((group, hero, problems))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    rows = audit()
    bad = 0
    for group, hero, problems in rows:
        if problems:
            bad += len(problems)
            print(f"{group:14} {hero:11} " + "; ".join(problems))
    for note in NOTES:
        print("NOTE  " + note)
    print(f"\n{len(rows)} heroes checked: " + ("all colours defined and carried by the Prime prompt" if not bad else f"{bad} problem(s)") + (f"; {len(NOTES)} note(s) (information only)" if NOTES else ""))
    return 1 if (bad and args.check) else 0


if __name__ == "__main__":
    sys.exit(main())
