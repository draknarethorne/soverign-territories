"""Find negations in positive prompts. An image model reads "do not recolour" as "recolour", "no squint" as squint, "not glowing" as glowing: say the positive instead.

    python tools/art/negation_audit.py                 summary and the worst phrases, each with where its text comes from
    python tools/art/negation_audit.py --check         exit 1 if any command or flip-risk phrase is left (for a pre-commit or CI step)
    python tools/art/negation_audit.py --review        also list the generic no/not/nothing/without phrases (information only)
    python tools/art/negation_audit.py --path "prompts/drakn-sisters/*"      only prompts under that pattern (* matches folders too)
    python tools/art/negation_audit.py --no-sources    skip the source lookup (faster)

The rules are in data/art/_settings/negation-audit.json: `command` (do not, never ...), `flip` (qualifiers known to name the unwanted thing), `review` (everything else, counted only) and `allow`
(paths where a negative is the only tool, with the reason). Only the positive part of a prompt is scanned: the text after `prompt:` and before `negative prompt:`; a negative belongs in the
negative prompt (the Qwen workflows have one; FireRed does not) or, better, becomes a positive: "natural studio eyes" instead of "eyes, not glowing".
Where a phrase comes from is found by looking its text up in data/ and tools/generators/, so the fix goes to the source and not to the generated prompt.
"""
import argparse
import collections
import fnmatch
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SETTINGS = ROOT / "data/art/_settings/negation-audit.json"
SOURCES = [ROOT / "data", ROOT / "tools/generators"]
SOURCE_SUFFIXES = {".json", ".txt", ".py"}


def phrase_of(line, m):
    """The negation and the rest of its clause, for grouping: 'no squint', 'do not recolour', 'rather than drooping'."""
    tail = re.split(r"[,;.)]", line[m.end():])[0][:26]
    return re.sub(r"\s+", " ", (m.group(0) + tail).strip().lower())


def positive_part(text):
    """The part of a prompt file the model reads as the positive prompt (the header above `prompt:` and the negative prompt are left out)."""
    if "prompt:" not in text:
        return ""
    body = text.split("prompt:", 1)[1]
    return body.split("negative prompt:")[0]


def allowed_by(rel, rules):
    return next((r["why"] for r in rules if fnmatch.fnmatch(rel, r["paths"])), None)


def scan(rules, pattern):
    """{class: {phrase: [count, {prompt files}]}} and the allowed counts, over every prompt that matches `pattern`."""
    rx = {"command": [re.compile(p, re.I) for p in rules["command"]], "flip": [re.compile(p, re.I) for p in rules["flip"]]}
    review = re.compile(rules["review"], re.I)
    found = {k: collections.defaultdict(lambda: [0, set()]) for k in ("command", "flip", "review")}
    allowed = collections.Counter()
    scanned = 0
    for p in sorted((ROOT / "prompts").rglob("*.txt")):
        rel = p.relative_to(ROOT).as_posix()
        if "_archive" in p.parts or p.name.startswith("_") or not fnmatch.fnmatch(rel, pattern):
            continue
        body = positive_part(p.read_text(encoding="utf-8", errors="ignore"))
        if not body:
            continue
        scanned += 1
        why = allowed_by(rel, rules["allow"])
        for line in body.splitlines():
            for kind in ("command", "flip"):
                for r in rx[kind]:
                    for m in r.finditer(line):
                        phrase = phrase_of(line, m)
                        if why:
                            allowed[kind] += 1
                        else:
                            found[kind][phrase][0] += 1
                            found[kind][phrase][1].add(rel)
            for m in review.finditer(line):
                phrase = phrase_of(line, m)
                if why:
                    allowed["review"] += 1
                else:
                    found["review"][phrase][0] += 1
                    found["review"][phrase][1].add(rel)
    return found, allowed, scanned


def source_files():
    out = {}
    for root in SOURCES:
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in SOURCE_SUFFIXES and "_archive" not in p.parts and not p.name.startswith("test_"):
                out[p] = p.read_text(encoding="utf-8", errors="ignore").lower()
    return out


def where_from(phrase, sources):
    """The data and generator files whose text holds the start of the phrase (a few words, so a rewording still finds it)."""
    key = " ".join(phrase.split()[:4])
    hits = collections.Counter()
    for p, t in sources.items():
        n = t.count(key)
        if n:
            rel = p.relative_to(ROOT).as_posix()
            hits["/".join(rel.split("/")[:4]) if rel.startswith("data/art/heroes") or rel.startswith("data/art/_sets") else rel] += n
    return [f"{k} ({n})" for k, n in hits.most_common(3)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if a command or flip-risk phrase is left")
    ap.add_argument("--review", action="store_true", help="also list the generic no/not/nothing/without phrases")
    ap.add_argument("--path", default="prompts/*", help="only prompts matching this pattern (default all)")
    ap.add_argument("--no-sources", action="store_true", help="do not look up where each phrase comes from")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()
    rules = json.loads(SETTINGS.read_text(encoding="utf-8"))
    found, allowed, scanned = scan(rules, args.path)
    sources = None if args.no_sources else source_files()
    print(f"{scanned} prompts scanned (positive part only)")
    bad = 0
    for kind, label in (("command", "COMMAND (do not / never ...): an instruction not to, read as an instruction to"), ("flip", "FLIP-RISK (qualifiers that name the unwanted thing)"), ("review", "REVIEW (any other negation; information only)")):
        data = found[kind]
        total = sum(v[0] for v in data.values())
        files = len(set().union(*[v[1] for v in data.values()])) if data else 0
        print(f"\n{label}: {total} hits in {files} prompts" + (f"   [{allowed[kind]} more in allowlisted prompts]" if allowed[kind] else ""))
        if kind != "review":
            bad += total
        if kind == "review" and not args.review:
            continue
        for phrase, (n, fs) in sorted(data.items(), key=lambda kv: -kv[1][0])[:args.top if kind != "review" else 40]:
            src = "" if sources is None else "   <- " + "; ".join(where_from(phrase, sources))
            print(f"  {n:6}  {phrase}{src}")
    if args.check:
        print("\n" + ("FAILED: say it as a positive (see data/art/_settings/negation-audit.json)" if bad else "OK: no command or flip-risk negations"))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
