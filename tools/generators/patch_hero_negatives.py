#!/usr/bin/env python3
"""Patch each hero's art definition with HER OWN curated eye/skin negatives.

This replaces the old model (universal template negative + per-card 'negativeRemove'
override) with hero-driven negatives: each hero's data explicitly states which colors
are WRONG for her, omitting whatever matches her own family. Fixes live collisions
like Drakniya's own 'forest-emerald' eyes being banned by a universal 'green eyes'
negative.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

ALL_EYE_COLORS = ["blue eyes", "green eyes", "brown eyes", "grey eyes",
                   "hazel eyes", "amber eyes", "red eyes", "violet eyes"]

# slug -> set of eye-colour negatives to OMIT (they collide with her own iris family)
OMIT_EYE = {
    "drakness":  {"violet eyes"},
    "draknora":  {"amber eyes", "red eyes"},        # molten amber iris, crimson striations
    "drakniya":  {"green eyes"},                     # forest-emerald iris
    "draknira":  {"blue eyes"},                      # glacial cyan iris
    "draknisa":  {"blue eyes"},                      # deep sapphire iris
    "drakniss":  {"amber eyes"},                     # topaz-gold iris
    "draknara":  {"hazel eyes", "amber eyes", "green eyes"},  # malachite-hazel iris, warm amber flecks
    "drakneta":  {"blue eyes", "amber eyes"},        # cobalt-topaz iris
    "draknava":  {"blue eyes", "green eyes"},        # sky cerulean / breeze teal
    "draknoxa":  {"green eyes", "violet eyes"},      # acid lime-emerald iris, toxic violet striations
}

# slug -> skin-tone family; tan heroines guard against drifting pale, pale heroines
# guard against drifting ruddy/overly-tanned.
SKIN_FAMILY = {
    "drakness": "tan", "draknora": "tan", "drakniya": "tan", "draknisa": "tan",
    "drakniss": "tan", "draknara": "tan", "drakneta": "tan", "draknava": "tan",
    "draknira": "pale", "draknoxa": "pale",
}
SKIN_NEGATIVES = {
    "tan": ["pale skin", "fair skin", "washed-out skin"],
    "pale": ["ruddy skin", "sunburnt skin", "overly tanned skin"],
}

for slug in OMIT_EYE:
    path = ROOT / f"data/art/heroes/{slug}-thorne.json"
    hero = json.loads(path.read_text(encoding="utf-8-sig"))
    pal = hero["art"]["palette"]
    pal["eyeColorNegatives"] = [c for c in ALL_EYE_COLORS if c not in OMIT_EYE[slug]]
    pal["skinColorNegatives"] = SKIN_NEGATIVES[SKIN_FAMILY[slug]]
    path.write_text(json.dumps(hero, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"patched {slug}: omit {sorted(OMIT_EYE[slug])}, skin={SKIN_FAMILY[slug]}")
