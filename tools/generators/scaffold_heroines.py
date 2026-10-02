#!/usr/bin/env python3
"""One-time scaffold: generate art-hero defs + base-set X_Pose/X_Head cards for the
9 remaining Drak sisters, mirroring the Drakness pattern. Run once, then regenerate
prompts with gen_prompt.py. Safe to delete after running (kept only if reused later).
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

# slug -> (CapName for paths, hairColor, skinTone, raceAlignment, eyeColorGlamour)
HEROINES = {
    "draknora": dict(
        cap="Draknora",
        race="Human",
        hairColor="Rich auburn-brown hair with warm copper and burnished-gold all-over highlights, full dimensional colour like a fashion editorial",
        skinTone="Warm sun-bronzed olive tan complexion, evenly tanned, no pale areas",
        raceAlignment="Human — standard human presentation",
        eyeColorGlamour="Molten amber irises with radiating crimson striations and a dark charcoal limbal ring",
    ),
    "drakniya": dict(
        cap="Drakniya",
        race="Wood Elf",
        hairColor="Rich chestnut-brown hair with warm honey and moss-gold all-over highlights, full dimensional colour like a fashion editorial",
        skinTone="Warm sun-kissed golden-olive tan complexion, evenly tanned, no pale areas",
        raceAlignment="Human presentation aligned to wood-elf characteristics (slender, nature-toned) — no pointed ears in glamour shots",
        eyeColorGlamour="Deep forest-emerald irises with radiating sage striations and a dark pine limbal ring",
    ),
    "draknira": dict(
        cap="Draknira",
        race="High Elf",
        hairColor="Icy platinum-ash blonde hair, sleek and sultry with a subtle silver-frost sheen",
        skinTone="Cool fair porcelain complexion, evenly toned, smooth and blemish-free",
        negativeRemove=["pale skin"],
        raceAlignment="Human presentation aligned to high-elf characteristics (slender, elegant) — no pointed ears in glamour shots",
        eyeColorGlamour="Glacial cyan irises with radiating frost-silver striations and a deep navy limbal ring",
    ),
    "draknisa": dict(
        cap="Draknisa",
        race="Human",
        hairColor="Deep blue-black hair with glossy aquamarine-sheened all-over highlights, full dimensional colour like a fashion editorial",
        skinTone="Warm sun-kissed medium tan complexion, evenly tanned, no pale areas",
        raceAlignment="Human — standard human presentation",
        eyeColorGlamour="Deep sapphire irises with radiating aquamarine striations and an oceanic indigo limbal ring",
    ),
    "drakniss": dict(
        cap="Drakniss",
        race="Human",
        hairColor="Luminous golden-blonde hair, soft and sultry with a gentle radiant sheen",
        skinTone="Warm radiant fair-golden tan complexion, evenly tanned, no pale areas",
        raceAlignment="Human — standard human presentation",
        eyeColorGlamour="Radiant topaz-gold irises with radiating solar champagne striations and a warm bronze limbal ring",
    ),
    "draknara": dict(
        cap="Draknara",
        race="Barbarian",
        hairColor="Rich bronze-brown hair with warm terracotta and caramel all-over highlights, full dimensional colour like a fashion editorial",
        skinTone="Deep sun-weathered terracotta tan complexion, evenly tanned, no pale areas",
        raceAlignment="Human presentation aligned to barbarian characteristics (strong, grounded) — glamour build stays family-standard for now",
        eyeColorGlamour="Rich malachite-hazel irises with radiating terracotta striations and a dark umber limbal ring",
    ),
    "drakneta": dict(
        cap="Drakneta",
        race="Celestial",
        hairColor="Electric golden-blonde hair, sultry and sleek with subtle silvery-white crackling highlights",
        skinTone="Warm golden tan complexion, evenly tanned, no pale areas",
        raceAlignment="Human presentation aligned to celestial characteristics (luminous, ethereal) — glamour build stays family-standard for now",
        eyeColorGlamour="Electric cobalt-topaz irises with radiating arc-cyan striations and a midnight indigo limbal ring",
    ),
    "draknava": dict(
        cap="Draknava",
        race="Wood Elf",
        hairColor="Silvery ash-blonde hair, soft and sultry with a breezy, airy sheen",
        skinTone="Light sun-kissed fair tan complexion, evenly tanned, no pale areas",
        raceAlignment="Human presentation aligned to wood-elf characteristics (slender, nature-toned) — no pointed ears in glamour shots",
        eyeColorGlamour="Sky cerulean irises with radiating gossamer silver striations and a slate blue limbal ring",
    ),
    "draknoxa": dict(
        cap="Draknoxa",
        race="Dark Elf",
        hairColor="Rich black hair with cool espresso depth and noticeable, vibrant deep acid-lime bold face-framing streaks that catch the light",
        skinTone="Pale olive complexion with a faint cool-grey cast, evenly toned, smooth and blemish-free",
        negativeRemove=["pale skin"],
        raceAlignment="Human presentation aligned to dark-elf characteristics (slender, elongated) — no pointed ears in glamour shots",
        eyeColorGlamour="Acid lime-emerald irises with radiating toxic violet striations and a blackened moss limbal ring",
    ),
}

# Default A-pose hairstyle is now a component reference (data/art/hair/center-part-wavy.json),
# not an inline string — see hairStyleComponent below. A hero can get a unique/signature
# A-pose hairstyle by pointing at a different data/art/hair/*.json component instead.

PHYSIQUE = {
    "build": "Lithe, slender, long-limbed build",
    "bust": "Full, voluptuous bust, emphasized and enhanced - breasts lifted and pressed closely together at the centre with a push-up-bra style contour, forming a narrow, well-defined décolletage (not a wide gap); soft, naturally rounded, full shape throughout (not flattened, reduced, or smaller than described)",
    "hips": "Shapely feminine hips, gently curved (not wide)",
    "legs": "Very long, slender legs",
    "distinguishingMarks": [],
}


def load_json(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8-sig"))


for slug, h in HEROINES.items():
    card = load_json(f"data/cards/sovereign-dawn/heroes/hero-{slug}-thorne.json")
    pal = card["art"]["palette"]

    art_hero = {
        "heroId": card["cardId"],
        "name": card["name"],
        "art": {
            "palette": {
                "primaryColor": pal["primaryColor"],
                "accentColors": pal["accentColors"],
                "eyeColor": pal["eyeColor"],
                "eyeColorGlamour": h["eyeColorGlamour"],
                "hairColor": h["hairColor"],
                "hairStyleComponent": "data/art/hair/center-part-wavy.json",
                "skinTone": h["skinTone"],
            },
            "physique": {**PHYSIQUE, "raceAlignment": h["raceAlignment"]},
        },
        "notes": f"Core ART hero definition for {card['name']} ({card['element']}, {h['race']}). "
                 "Mirrors data/art/heroes/drakness-thorne.json's structure. Base-set cards reference this.",
    }

    art_hero_path = ROOT / f"data/art/heroes/{slug}-thorne.json"
    art_hero_path.write_text(json.dumps(art_hero, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for stage, tmpl, outdir, outname in [
        ("pose", "pose-female-human.txt", "poses", "X_Pose"),
        ("head", "head-human.txt", "head", "X_Head"),
    ]:
        base_set_card = {
            "artId": f"{slug}-x-{stage}",
            "kind": "base-set",
            "stage": stage,
            "heroArt": f"data/art/heroes/{slug}-thorne.json",
            "template": f"data/art/base-set/_templates/heroes/{tmpl}",
            "output": f"prompts/art/base-set/{h['cap']}/{outdir}/{h['cap']}_{outname}.txt",
            "denoise": "~1.0" if stage == "pose" else "~0.4-0.6",
            "notes": f"{card['name']} {stage} — generated alongside Drakness as the initial baseline for all 10 female heroes.",
        }
        if stage == "pose" and h.get("negativeRemove"):
            base_set_card["overrides"] = {"negativeRemove": h["negativeRemove"]}
        card_path = ROOT / f"data/art/base-set/{slug}/{stage}/{slug}-x-{stage}.json"
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(json.dumps(base_set_card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"Scaffolded {len(HEROINES)} heroines: {len(HEROINES)} art-hero defs + {len(HEROINES) * 2} base-set cards")
