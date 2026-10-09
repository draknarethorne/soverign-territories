#!/usr/bin/env python3
"""Character scenes for the Drakn Sisters: what she is doing follows who she is (data/art/_settings/scene-recipes.json).

Per sister (re-runnable; existing cards are kept):
  domain        her element at work, in the same realm as her Dawn scene
  craft         what her class does (Shaman, Necromancer, Bard, Alchemist ...)
  <theme pack>  one celebration scene for her element: coronation, masquerade ball, midwinter festival, siege defense or victory feast
(her Lineup, Dawn, Bond, Battle, Robe, Casting and Signature already exist; the Angel Primes get the same Lineup from scaffold_angel_set.py --character.)

Then:  python tools/generators/gen_prompt.py --group drakn-sisters ; python tools/workflows/comfy_workflows.py make --create --group drakn-sisters

Example:  python tools/generators/scaffold_sister_character.py            (all ten sisters)
          python tools/generators/scaffold_sister_character.py --slug drakness
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import scaffold_angel_library as library  # noqa: E402
from scaffold_sister_studio import TPL, Writer, camel, norm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data/art"
GROUP = "drakn-sisters"
EYES = library.EYES


def exists(rel):
    return rel if (ROOT / rel).exists() else ""


def sister_info(slug):
    ident = f"data/art/heroes/{GROUP}/{slug}-thorne.json"
    card = json.loads((ROOT / f"data/cards/sovereign-dawn/heroes/hero-{slug}-thorne.json").read_text(encoding="utf-8"))
    return ident, card["element"], card["class"]


def build(slug, index):
    recipes = json.loads((ART / "_settings/scene-recipes.json").read_text(encoding="utf-8"))
    ident, element, klass = sister_info(slug)
    hero = slug.capitalize()
    mat = library.ELEMENT_MAT[element]
    base = f"data/art/heroes/{GROUP}/{slug}"
    wr = Writer(ART / "_sets" / GROUP / slug, GROUP)
    out = lambda folder, name: f"prompts/{GROUP}/{hero}/{folder}/{name}.txt"

    wearing = {"armor": exists(f"{base}/clothing/battle-gear.json"), "gown": exists(f"{base}/clothing/elegant-casting-gown.json"),
               "robe": exists(f"{base}/clothing/signature-robe.json"), "regalia": exists(f"{base}/clothing/dawn-regalia.json")}
    fallback = wearing["robe"] or wearing["gown"] or wearing["armor"]
    weapons = sorted(p for p in (ROOT / base / "weapons").glob("*.json") if "ascended" not in p.name) if (ROOT / base / "weapons").is_dir() else []
    weapon = weapons[0].relative_to(ROOT).as_posix() if weapons else ""
    dawn = json.loads((ART / "_sets" / GROUP / slug / "5_Scenes/story" / f"{slug}-scene-the-dawn.json").read_text(encoding="utf-8"))["components"]["background"]
    aura = exists(f"{base}/effects/elemental-aura.json")

    def card(art, title, comps, note, template="scene-with-outfit-human.txt"):
        comps = {k: v for k, v in comps.items() if v}
        body = {"artId": f"{slug}-scene-{art}", "kind": "base-set", "stage": "scene", "heroArt": ident, "name": title, "components": comps, "template": f"{TPL}/{template}",
                "output": out("scene", f"{hero}_Scene_{camel(art)}"), "denoise": "~0.5-0.7", "notes": note}
        wr.write("scene", f"{slug}-scene-{art}", body)

    def piece(kind, name):
        return exists(f"{base}/{kind}/{name}.json")

    def build_comps(r, background):
        kind = r["wearing"]
        wear = wearing.get(kind) or fallback
        armor = kind == "armor"
        hold = {"weapon": weapon, "none": ""}.get(r.get("holding", "none"), r.get("holding"))
        return {"pose": r["pose"].replace("{mat}", mat), "wearing": wear,
                "headwear": piece("headwear", "scene-battle-headwear" if armor else "scene-robe-headwear"), "jewelry": piece("jewelry", "scene-battle-jewelry" if armor else "scene-robe-jewelry"),
                "legs_feet": piece("footwear", "scene-battle-legs-feet" if armor else "scene-robe-legs-feet"), "holding": hold, "effects": library.cap(r["effects"].replace("{mat}", mat)),
                "eye_effect": EYES + r["eyes"] + ".json" if r.get("eyes") else "", "background": background}

    realm_piece = exists(f"data/art/realms/{element.lower()}-lands.json")
    country = ROOT / "data/art/backgrounds/fantasy/country" / element.lower()

    def country_pool(role):
        return [p.relative_to(ROOT).as_posix() for p in sorted(country.glob("*.json")) if role in library.tags_of(p)]

    d = next(x for x in recipes["domain"] if x["element"] == element)
    card("domain", "Domain", build_comps(d, dawn), f"DOMAIN: her {element} element at work in her homeland; from data/art/_settings/scene-recipes.json.")
    c = next(x for x in recipes["craft"] if x["class"] == klass)
    haunts = library.lib(f"backgrounds/fantasy/haunts/{klass.lower().replace(' ', '-')}", "female")
    pool = haunts or [p for f in c["background"] for p in library.lib(f"backgrounds/fantasy/{f}", "female")]
    craft = build_comps(c, library.pick(pool, index))
    card("craft", "Craft", dict(craft, realm=realm_piece), f"CRAFT: what a {klass} does, in her class's own place and her element's realm; from data/art/_settings/scene-recipes.json.")

    # the realm series: her homeland as a place, scene by scene, and her haunt
    for r in recipes.get("realm", []):
        pool = country_pool(r["role"])
        if pool:
            card(r["id"], r["name"], dict(build_comps(r, library.pick(pool, 0)), realm=realm_piece),
                 f"REALM SERIES: {r['name']} in her {element.lower()} homeland ({r['role']}); realistic, from realms/{element.lower()}-lands and backgrounds/fantasy/country/{element.lower()}.")
    if recipes.get("haunt") and haunts:
        h = recipes["haunt"]
        card(h["id"], h["name"], dict(build_comps(h, library.pick(haunts, index + 1)), realm=realm_piece), f"HAUNT: the place a {klass} spends her time, in her element's realm.")

    pack = recipes["celebration"].get(element)
    t = library.themes("female").get(pack) if pack else None
    if t:
        one = lambda key, k=0: library.pick(t[key], index + k)
        poses = library.lib("motion/standing", "female")
        wear = one("armor") if t.get("armor") and pack == "siege-defense" else one("clothing")
        comps = {"pose": norm(library.pick(poses, index)), "expression": library.pick(library.EXPRESSIONS, index), "wearing": wear, "headwear": one("headwear"),
                 "jewelry": one("jewelry") or piece("jewelry", "scene-robe-jewelry"), "legs_feet": one("footwear") or piece("footwear", "scene-robe-legs-feet"), "makeup": one("makeup"),
                 "effects": aura, "background": one("background")}
        card(pack, t["name"], comps, f"{t['name']} celebration scene for her element: every item is a library or theme-pack piece.")
    print(f"{slug}: made {wr.made} character cards, {wr.skipped} already existed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug")
    args = ap.parse_args()
    slugs = sorted(p.stem.split("-")[0] for p in (ART / "heroes" / GROUP).glob("*-thorne.json"))
    for n, slug in enumerate(slugs):
        if not args.slug or slug == args.slug:
            build(slug, n)


if __name__ == "__main__":
    main()
