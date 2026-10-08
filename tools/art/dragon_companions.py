#!/usr/bin/env python3
"""Make the sisters' dragon companions come from the Elder Dragon definitions.

Each sister has an aligned Elder Dragon (data/art/dragons/elder-dragons/<slug>.json). Her scenes show it through companion pieces
(data/art/heroes/drakn-sisters/<sister>/companion/) and, on some cards, a sentence typed into the card. All of those copied the dragon's description by hand.
This tool writes, for every dragon, two *frames* (pieces with named gaps, see `vars` in data/art/README.md) and rewrites the sisters' companion text to extend them:

  dragons/elder-dragons/<slug>/companion/<slug>-companion.json          "her aligned Elder Dragon, <Name>, [[PLACEMENT]]<the identity description>[[DETAIL]]"
  dragons/elder-dragons/<slug>/companion/<slug>-companion-distant.json  "her aligned Elder Dragon, <Name>, [[PLACEMENT]]"   (for a silhouette or a scene that rewords the dragon)

A sister's companion piece then only says what is different in her scene (where the dragon is, what it is doing, a rewording): `extends` the frame and fills PLACEMENT (and DETAIL).
A text that contains the identity description word for word extends the full frame, so an edit to the dragon's description reaches it; any other text extends the distant frame and keeps its own
wording, and is listed in the report so you can decide whether it should use the identity's description instead. Sentences typed into scene cards become pieces too.

Every conversion is checked: the new piece must produce exactly the old text, so the generated prompts do not change.

Usage:  python tools/art/dragon_companions.py             preview and report
        python tools/art/dragon_companions.py --apply     write the frames and the pieces, point the cards at them
"""
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
DRAGONS = ROOT / "data/art/dragons/elder-dragons"
SISTERS = ROOT / "data/art/heroes/drakn-sisters"
SETS = ROOT / "data/art/_sets/drakn-sisters"
OPENING = re.compile(r"^her aligned Elder Dragon, ([A-Z][a-z]+), (.*)$", re.S)


def frame_paths(slug):
    base = f"data/art/dragons/elder-dragons/{slug}/companion"
    return f"{base}/{slug}-companion.json", f"{base}/{slug}-companion-distant.json"


def frames(slug, identity):
    """The two frames of a dragon: text with [[PLACEMENT]] (and [[DETAIL]]) gaps."""
    name = slug.capitalize()
    full_path, far_path = frame_paths(slug)
    note = ("A frame: the [[PLACEMENT]] gap is where this dragon is in a scene (it ends with ', ' when it is not empty) and [[DETAIL]] is anything after the description; "
            "a sister's companion piece extends it and fills the gaps with vars. Written by tools/art/dragon_companions.py from the dragon identity.")
    full = {"id": full_path[len("data/art/"):-len(".json")], "kind": "companion", "name": f"{name} as her companion",
            "description": f"her aligned Elder Dragon, {name}, [[PLACEMENT]]{identity['description']}[[DETAIL]]", "compatibleStages": ["scene", "showcase"], "tags": ["dragon", "companion"],
            "notes": note + " This frame shows the dragon as the identity describes it; the description is read from the identity file, so edit it there."}
    far = {"id": far_path[len("data/art/"):-len(".json")], "kind": "companion", "name": f"{name} as her companion (scene wording)",
           "description": f"her aligned Elder Dragon, {name}, [[PLACEMENT]]", "compatibleStages": ["scene", "showcase"], "tags": ["dragon", "companion"],
           "notes": "A frame for a scene that words the dragon itself (a distant silhouette, a close-up that rewords its traits): it gives the opening and the name, the sister's piece fills in the rest. Written by tools/art/dragon_companions.py."}
    return (full_path, full), (far_path, far)


def decompose(text, identities):
    """Split a typed companion sentence into (slug, frame kind, vars), or None when it does not open the standard way. Joining the parts back gives the text exactly."""
    m = OPENING.match(text)
    if not m:
        return None
    slug = m.group(1).lower()
    if slug not in identities:
        return None
    rest, desc = m.group(2), identities[slug]["description"]
    if desc in rest:
        pre, post = rest.split(desc, 1)
        if pre == "" or pre.endswith(", "):
            return slug, "full", {"PLACEMENT": pre, "DETAIL": post}  # the placement keeps its trailing ", "
    return slug, "far", {"PLACEMENT": rest}


def rebuild(slug, kind, vars_, identities):
    name = slug.capitalize()
    body = f"her aligned Elder Dragon, {name}, {vars_['PLACEMENT']}"  # for a full text the placement is followed straight by the description
    return f"{body}{identities[slug]['description']}{vars_['DETAIL']}" if kind == "full" else body


def colour_words(desc):
    first = desc.split(" scales")[0]
    return {w for w in re.findall(r"[a-z]+(?:-[a-z]+)*", first.lower()) if len(w) > 3 and w not in ("elder", "dragon", "deep", "vivid", "with", "veined", "and")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    identities = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(DRAGONS.glob("*.json"))}

    work = []  # (kind of source, path, text)
    for p in sorted(SISTERS.glob("*/companion/*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if "extends" not in d:
            work.append(("piece", p, d["description"]))
    for p in sorted(SETS.rglob("*.json")):
        v = json.loads(p.read_text(encoding="utf-8")).get("components", {}).get("companion")
        if v and not v.endswith(".json"):
            work.append(("card", p, v))

    plan, skipped, report = [], [], {"full": [], "far": []}
    for source, path, text in work:
        parts = decompose(text, identities)
        if not parts:
            skipped.append((path, text[:100]))
            continue
        slug, kind, vars_ = parts
        assert rebuild(slug, kind, vars_, identities) == text, f"{path}: the split does not give back the text"
        plan.append((source, path, text, slug, kind, vars_))
        report[kind].append((path, slug, text))

    print(f"{len(identities)} dragons, {len(work)} companion texts ({sum(1 for w in work if w[0] == 'piece')} sister pieces, {sum(1 for w in work if w[0] == 'card')} sentences typed on scene cards)")
    print(f"  {len(report['full'])} contain the dragon's identity description word for word -> extend the full frame (an edit to the dragon reaches them)")
    print(f"  {len(report['far'])} word the dragon themselves (a distant silhouette or a reworded close-up) -> extend the distant frame, wording kept")
    for path, text in skipped:
        print(f"  NOT CONVERTED (does not open 'her aligned Elder Dragon, <Name>, '): {path.name}: {text}")
    print("\nScene wordings to review against the identity (colour words of the identity that the text does not mention):")
    n = 0
    for path, slug, text in report["far"]:
        miss = sorted(w for w in colour_words(identities[slug]["description"]) if w not in text.lower())
        if miss and "scales" in text.lower() or "wings" in text.lower() and miss:
            n += 1
            print(f"  {path.name:58} {slug:9} missing: {', '.join(miss)}")
    print(f"  ({n} of {len(report['far'])} scene wordings differ from the identity's colours)")
    if not args.apply:
        print("\npreview only; add --apply to write the frames and the pieces")
        return

    for slug, ident in identities.items():
        for path, body in frames(slug, ident):
            p = ROOT / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    made, by_text = 0, {}
    for source, path, text, slug, kind, vars_ in plan:
        full_path, far_path = frame_paths(slug)
        extends = full_path if kind == "full" else far_path
        if source == "piece":
            d = json.loads(path.read_text(encoding="utf-8"))
            out = {"id": d["id"], "kind": "companion", "name": d["name"], "extends": extends, "vars": vars_,
                   "notes": f"Extends the {slug.capitalize()} companion frame; only the placement is this scene's. (Was a typed sentence that copied the dragon's description.)"}
            path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            made += 1
            continue
        card = json.loads(path.read_text(encoding="utf-8"))
        sister = path.relative_to(SETS).parts[0]
        scene = card["artId"].removeprefix(f"{sister}-scene-")
        key = text
        if key not in by_text:
            rel = f"data/art/heroes/drakn-sisters/{sister}/companion/{sister}-{scene}-dragon.json"
            piece = {"id": rel[len("data/art/"):-len(".json")], "kind": "companion", "name": f"{slug.capitalize()} in {sister.capitalize()}'s {scene.replace('-', ' ')} scene", "extends": extends, "vars": vars_,
                     "tags": ["dragon", "companion"], "notes": f"Extends the {slug.capitalize()} companion frame; only the placement is this scene's. (Was a sentence typed into the card.)"}
            (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / rel).write_text(json.dumps(piece, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            by_text[key] = rel
            made += 1
        needle = f'"companion": {json.dumps(text, ensure_ascii=False)}'
        body = path.read_text(encoding="utf-8")
        if body.count(needle) != 1:
            print(f"  SKIP {path.name}: the sentence is not written the expected way in the file")
            continue
        path.write_text(body.replace(needle, f'"companion": "{by_text[key]}"'), encoding="utf-8", newline="")
    print(f"wrote {len(identities) * 2} frames and {made} piece(s); now run gen_prompt.py: git status prompts/ must show nothing changed")


if __name__ == "__main__":
    main()
