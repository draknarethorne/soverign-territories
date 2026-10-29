"""Candidates and finals: tolerant name parsing and slots. Pure helpers; the commands that use them live in comfy_workflows.py (`finals`).

A saved ComfyUI workflow is named  <Hero>_<Engine>_<Stage...>[_00015_].json  (the counter is the render it was saved from). The name is enough to say where it belongs,
so a misspelled hero, engine or stage, a wrong folder, or a drop straight into zz_Final can be placed without asking: the parts are matched to what exists and an
ambiguous match is refused (never guessed).
"""
import difflib
import re

ENGINES = ("Qwen", "FireRed", "MiniMax")
COUNTER = re.compile(r"_(\d{3,6})_?$")


def _ratio(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def close(word, options, cutoff):
    """The one option `word` means: exact, then the same ignoring case, then the single clearly closest one (None when two are about as close)."""
    options = list(options)
    if word in options:
        return word
    lower = {}
    for o in options:
        lower.setdefault(o.lower(), o)
    if word.lower() in lower:
        return lower[word.lower()]
    hits = difflib.get_close_matches(word.lower(), list(lower), n=2, cutoff=cutoff)
    if not hits:
        return None
    if len(hits) > 1 and _ratio(word.lower(), hits[0]) - _ratio(word.lower(), hits[1]) < 0.05:
        return None
    return lower[hits[0]]


def parse_name(name, heroes, stems=(), aliases=None):
    """{hero, engine, rest, counter, stem, exact} for a saved workflow name, or None when the hero, engine or stage cannot be told.

    heroes: the known hero names. stems: the generated workflow names without .json (Hero_Qwen_Alpha_1_Prime); the stage is matched against those of that hero and engine.
    `exact` is False when anything had to be corrected (case, a typo). aliases: {old stage name: current one} for a stage that was renamed (X_Pose -> Alpha_1_Prime): the save is placed
    by the current stage but keeps its own file name (`file_stem`)."""
    base = name[:-5] if name.lower().endswith(".json") else name
    counter = None
    m = COUNTER.search(base)
    if m:
        counter, base = m.group(1), base[:m.start()]
    parts = base.split("_", 2)
    if len(parts) < 3:
        return None
    hero = close(parts[0], heroes, 0.75)
    engine = close(parts[1], ENGINES, 0.7)
    if not hero or not engine:
        return None
    pool = [s for s in stems if s.startswith(f"{hero}_{engine}_")]
    stem = close(f"{hero}_{engine}_{parts[2]}", pool, 0.85) if pool else None
    file_stem = stem
    if not stem:
        old = close(parts[2], list(aliases or {}), 0.9)
        stem = f"{hero}_{engine}_{aliases[old]}" if old and f"{hero}_{engine}_{aliases[old]}" in pool else None
        if not stem:
            return None
        file_stem = f"{hero}_{engine}_{old}"
    return {"hero": hero, "engine": engine, "rest": stem.split("_", 2)[2], "counter": counter, "stem": stem, "file_stem": file_stem,
            "exact": file_stem == f"{parts[0]}_{parts[1]}_{parts[2]}"}


def slot_of(stem, slots):
    """The slot label a generated stem fills (prime, bare, golden ...), or None. slots: {label: [stage names after Hero_Engine_]}."""
    rest = stem.split("_", 2)[2] if stem.count("_") >= 2 else stem
    for label, names in slots.items():
        if rest in names:
            return label
    return None
