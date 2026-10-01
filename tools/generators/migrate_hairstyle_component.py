#!/usr/bin/env python3
"""Migrate all hero art defs from an inline 'hairStyle' string to a
'hairStyleComponent' reference (data/art/hair/center-part-wavy.json — today's shared
default). Lossless: the component holds the exact text that was inline before.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_COMPONENT = "data/art/hair/center-part-wavy.json"

for path in sorted((ROOT / "data/art/heroes").glob("*.json")):
    hero = json.loads(path.read_text(encoding="utf-8-sig"))
    pal = hero["art"]["palette"]
    if "hairStyle" in pal:
        del pal["hairStyle"]
        pal["hairStyleComponent"] = DEFAULT_COMPONENT
        path.write_text(json.dumps(hero, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"migrated {path.name}")
