#!/usr/bin/env python3
"""The rest of an Angel Primes angel's standard set, built like a Drakn sister's (called by scaffold_angel_set.py; re-runnable, existing cards are kept).

The sisters are the model: a standard sister has about 160 cards across the pipeline phases and Drakness has the whole library on top. Each angel gets the same structure,
and the library pieces are ROTATED across the twenty angels (by alignment rank) so that, together, they exercise every family of the library instead of repeating one set.

  1_Alpha      Bare Figure and Chest (scaffold_angel_set), 4 covering and 4 celestial experiments (female)
  2_Studies    body views, head views, close-ups and expressions (scaffold_studio_library), 8 hairstyles from the 46-style library, a hair card per theme
  3_Layers     the skin base variants (female) and a rotating mix of bikini, lingerie, one-piece, backless and athletic underlayers
  4_Wardrobe   clothing (dresses, gowns, sets), armor, themed outfits, and the showcases: celestial, editorial, elemental, studio and 13 photo locations (female)
  5_Scenes     signature, glamour (glamour, evening, casting, robe), story (battle, bond, the dawn) and six themes, complete and staged (female)
  6_Finish     the polish and final skeletons          Bench/motion  a rotating mix of the motion library

Generic families are cloned from a standard sister (Draknava) so the angels follow her; every sister-specific path is replaced or the clone is refused.
The male angels get everything that needs no male wardrobe (studies, hair, layers, bench motions, finish) until the male wardrobe pack exists: only pieces tagged male or unisex
are ever given to a male angel, and only pieces not tagged male to a female one. A kit may override any pick (keys: layers, clothing, armor, themes, hair, motions).
"""
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import art_layout  # noqa: E402
from scaffold_sister_studio import STUDIO, TPL, camel, norm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "data/art"
GROUP = "angel-primes"
SISTER = ART / "_sets/drakn-sisters/draknava"  # the standard sister the generic families are cloned from
BIKINI = "data/art/wardrobe/swimwear/bikini/metallic-triangle-bikini.json"
BRIEF = "data/art/wardrobe/swimwear/trunks/swim-brief.json"
EYES = "data/art/wardrobe/effects/eyes/"
HAIR_LIB = "data/art/races/human/cosmetics/hair"

# What each element's magic is made of, for effect lines; the realm itself comes from the angel's kit.
ELEMENT_MAT = {
    "Light": "golden light and drifting motes",
    "Water": "flowing water and drifting spray",
    "Grass": "living vines, leaves and petals",
    "Wind": "racing wind, feathers and leaves",
    "Earth": "stone shards, dust and glowing crystals",
    "Lightning": "crackling arcs of lightning and sparks",
    "Ice": "swirling frost, snowflakes and ice crystals",
    "Fire": "dancing flame, embers and sparks",
    "Poison": "curling green venom mist and falling drops",
    "Darkness": "drifting shadow, smoke and pale starlight",
    "Neutral": "soft white light, drifting pale feathers and motes",
}
EXPRESSIONS = [
    "a serene, knowing smile, eyes calm and bright.",
    "a playful, knowing smile, eyes bright with mischief.",
    "a composed, quietly commanding look, eyes steady on the camera.",
    "a soft, wondering smile, eyes lifted and glowing.",
    "a fierce, focused gaze, chin raised.",
    "a warm, radiant smile, eyes full of light.",
]
# Fantasy backgrounds by purpose: folders of data/art/backgrounds/fantasy.
BG = {
    "evening": ["evening", "interiors", "coast", "cityscape", "ruins", "farmland", "ships", "desert"],
    "casting": ["highlands", "mountains", "canyon", "library", "temple", "caves", "volcano", "jungle", "frozen", "tundra"],
    "sanctum": ["temple", "interiors", "library", "forests", "swamp", "tavern", "camp"],
    "battle": ["battlefield", "castle", "mountains", "ruins", "highlands", "dungeons", "swamp", "ships"],
}
_cache = {}
ELEMENT_MOTION = {"Light": "light-blooms", "Water": "water-swirls", "Grass": "vines-unfurl", "Wind": "winds-stream", "Earth": "stones-lift", "Lightning": "lightning-crackles",
                  "Ice": "frost-blooms", "Fire": "fire-surges", "Poison": "venom-coils", "Darkness": "shadow-rolls", "Neutral": "feathers-drift"}

# Shared studio pieces (extracted from the literals the cards used to carry; see tools/art/extract_literals.py).
NECKLACE = "data/art/wardrobe/jewelry/studio/simple-necklace-and-earrings.json"
CHAIN = "data/art/wardrobe/jewelry/studio/simple-chain-with-pendant.json"
ANKLETS = "data/art/wardrobe/footwear/studio/barefoot-fine-anklets.json"
BAREFOOT = "data/art/wardrobe/footwear/barefoot/barefoot.json"

# Signature items: each angel gets her or his own weapon, armor, gown, headwear, jewelry and element aura. They are NOT written from scratch: each one `extends` a library piece
# and adds only what is theirs (their element's motif and the tone of their alignment), the way a hero's necklace should be the library necklace plus details.
MOTIF = {
    "Light": "a radiant sunburst",
    "Water": "a scallop shell over curling waves",
    "Grass": "twining leaves and a budding vine",
    "Wind": "a spiral of swept feathers",
    "Earth": "a faceted crystal set in carved stone",
    "Lightning": "a forked lightning bolt inside a ring of cloud",
    "Ice": "a six-pointed snowflake of frost",
    "Fire": "a rising flame with scattered embers",
    "Poison": "a coiled serpent beside a nightshade bloom",
    "Neutral": "a single white feather within a plain ring",
    "Darkness": "a crescent moon pierced by a single star",
}
WEAPON_FAMILY = {"Light": "swords", "Water": "polearms", "Grass": "bows", "Wind": "staves", "Earth": "blunt", "Lightning": "axes", "Ice": "wands", "Fire": "swords",
                 "Poison": "daggers", "Darkness": "crossbows", "Neutral": "polearms"}
TONES = [(3, "pristine, luminous and unmarked"), (5, "clean, with a quiet shine"), (7, "plain, severe and unornamented"),
         (9, "worn, scorched at the edges and trimmed with dark feathers"), (10, "tattered, shadow-edged and trimmed with black feathers")]


def cap(text):
    return text[:1].upper() + text[1:]


def cinematic():
    """True when Angel Primes renders in the cinematic (realistic) realm, set in _settings/studio.json realmByGroup."""
    settings = json.loads((ROOT / "data/art/_settings/studio.json").read_text(encoding="utf-8"))
    return "cinematic" in settings.get("realmByGroup", {}).get(GROUP, "")


def grounded(background):
    """The realistic counterpart of an elemental realm background (backgrounds/fantasy/elemental/grounded/<same name>), when the realm is cinematic and one exists."""
    twin = str(pathlib.PurePosixPath(background).parent / "grounded" / pathlib.PurePosixPath(background).name)
    return twin if cinematic() and (ROOT / twin).exists() else background


def tags_of(path):
    try:
        return set(json.loads(path.read_text(encoding="utf-8")).get("tags", []))
    except (OSError, ValueError):
        return set()


def lib(rel, sex, skip=(), neutral=False, skip_tags=()):
    """Repo-relative paths of the pieces under data/art/<rel>, sorted; a female angel gets nothing tagged male, a male angel only pieces tagged male or unisex
    (or, with neutral=True for sex-neutral material such as motions, anything not tagged female). skip_tags drops pieces carrying any of those tags."""
    key = (rel, sex, tuple(skip), neutral, tuple(skip_tags))
    if key not in _cache:
        out = []
        for p in sorted((ART / rel).rglob("*.json")):
            t = tags_of(p)
            if t & set(skip_tags):
                continue
            if sex == "female" and "male" in t:
                continue
            if sex == "male" and (("female" in t) if neutral else not (t & {"male", "unisex"})):
                continue
            r = p.relative_to(ROOT).as_posix()
            if not any(s in r for s in skip):
                out.append(r)
        _cache[key] = out
    return _cache[key]


def rot(pool, i, n):
    """n distinct pieces of a pool, starting where angel i's turn begins (so neighbouring angels differ and ten angels sweep the pool)."""
    if not pool:
        return []
    out = []
    for k in range(min(n, len(pool))):
        out.append(pool[(i * n + k) % len(pool)])
    return out


def interleave(paths):
    """Reorder pieces so consecutive picks come from different family folders (down, braided, framed ...), so a rotation gives each angel a mix."""
    fams = {}
    for p in paths:
        fams.setdefault(pathlib.PurePosixPath(p).parent.name, []).append(p)
    out = []
    while any(fams.values()):
        for f in sorted(fams):
            if fams[f]:
                out.append(fams[f].pop(0))
    return out


def pick(pool, i, k=0):
    return pool[(i + k) % len(pool)] if pool else None


def themes(sex="female"):
    """{pack: {category: [paths]}} for every theme pack that has an outfit for this sex. A female angel never gets a piece tagged male; a male angel gets outfits, armor, headwear and
    jewelry only when tagged male or unisex, and footwear, props and weapons unless tagged female (the packs' other pieces are written for women)."""
    ckey = f"themes-{sex}"
    if ckey not in _cache:
        out = {}
        for tj in sorted((ART / "themes").rglob("theme.json")):
            pack = tj.parent
            cats = {}
            for key, rel in (("clothing", "wardrobe/clothing"), ("armor", "wardrobe/armor"), ("headwear", "wardrobe/headwear"), ("jewelry", "wardrobe/jewelry"),
                             ("footwear", "wardrobe/footwear"), ("props", "wardrobe/props"), ("weapons", "wardrobe/weapons"), ("makeup", "cosmetics/makeup"),
                             ("hair", "cosmetics/hair"), ("background", "backgrounds")):
                found = sorted((pack / rel).rglob("*.json")) if (pack / rel).is_dir() else []
                if sex == "female":
                    found = [p for p in found if "male" not in tags_of(p)]
                elif key in ("background",):
                    pass
                elif key in ("footwear", "props", "weapons", "hair", "makeup"):
                    found = [p for p in found if "female" not in tags_of(p) and (key not in ("hair", "makeup") or tags_of(p) & {"male", "unisex"})]
                else:
                    found = [p for p in found if tags_of(p) & {"male", "unisex"}]
                cats[key] = [p.relative_to(ROOT).as_posix() for p in found]
            if cats["clothing"] and cats["background"]:
                try:
                    name = json.loads(tj.read_text(encoding="utf-8")).get("name") or pack.name
                except ValueError:
                    name = pack.name
                out[pack.name] = {**cats, "name": name}
        _cache[ckey] = out
    return _cache[ckey]


class Angel:
    def __init__(self, slug, kit, ident, sex, division, wr, out):
        self.slug, self.kit, self.ident, self.sex, self.division, self.wr, self.out = slug, kit, ident, sex, division, wr, out
        self.hero, self.element, self.female = kit["hero"], kit["element"], sex == "female"
        self.i = kit.get("rotation", kit["alignmentRank"] - 1)  # which slice of each library pool this angel takes; a pair shares a rank, an extra pair sets its own rotation
        self.mat = ELEMENT_MAT[self.element]
        self.scene = {k: (norm(v) if k in ("back", "companion", "background", "wearing", "pose", "expression") else v) for k, v in kit["scene"].items()}
        self.made = 0
        self.illustrated_background = self.scene["background"]
        self.scene["background"] = grounded(self.scene["background"])
        self.sig = self.signature()

    # ----- signature items

    def signature(self):
        """Write this angel's own pieces under heroes/angel-primes/<division>/<slug>/ and return their paths. Each extends a library piece (see load_piece in gen_prompt.py)."""
        motif = MOTIF[self.element]
        tone = next(t for limit, t in TONES if self.kit["alignmentRank"] <= limit)
        her = "her" if self.female else "him"
        base_dir = f"data/art/heroes/{GROUP}/{self.division}/{self.slug}"
        out = {}

        def piece(folder, name, kind, stages, display, description, extends=None):
            rel = f"{base_dir}/{folder}/{self.slug}-{name}.json"
            path = ROOT / rel
            if not path.exists():
                body = {"id": rel[len("data/art/"):-len(".json")], "kind": kind, "name": display}
                if extends:
                    body["extends"] = extends
                body.update({"description": description, "compatibleStages": stages,
                             "notes": f"Signature item of {self.hero}: " + (f"the library piece {extends.removeprefix('data/art/')} plus {self.element.lower()} and alignment details." if extends else "written for this angel.")})
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return rel

        ov = {k: norm(v) for k, v in self.kit.get("signature", {}).items()}  # a kit may name the base pieces of her or his signature items instead of the rotation picking them
        fam = WEAPON_FAMILY[self.element]
        dark = ("vertebra", "skull", "bone", "demon", "infernal", "blood", "horn", "fang", "talon", "necrotic", "shadow", "umbral", "raven", "vampir")

        def pure(paths):
            """Angels of the lawful half do not wear bone and blood: drop library pieces whose text says so (the fallen keep them)."""
            if self.kit["alignmentRank"] > 6:
                return paths
            keep = [p for p in paths if not any(w in json.loads((ROOT / p).read_text(encoding="utf-8")).get("description", "").lower() for w in dark)]
            return keep or paths

        weapons = pure(lib(f"wardrobe/weapons/{fam}", self.sex, neutral=True))
        out["weapon"] = piece("weapons", "signature-weapon", "holding", ["armor", "showcase", "scene"], f"{self.hero}'s signature weapon",
                              f"+, its metal worked with {motif} in {{{{ACCENT_SOFT}}}}, {self.mat} gathering along it when it is raised; {tone}", ov.get("weapon") or pick(weapons, self.i))
        armors = pure(lib("wardrobe/armor", self.sex, skip=("/celestial/",), skip_tags=("bikini",), neutral=True))
        out["armor"] = piece("armor", "signature-armor", "wearing", ["armor", "showcase", "scene"], f"{self.hero}'s signature armor",
                             f"+, every plate and trim engraved with {motif} in {{{{ACCENT_SOFT}}}}; {tone}", ov.get("armor") or pick(armors, self.i * 5 + 2))
        gowns = pure(lib("wardrobe/clothing/gowns", "female") if self.female else lib("wardrobe/clothing/sets", "male"))
        out["gown"] = piece("clothing", "signature-gown" if self.female else "signature-attire", "wearing", ["clothing", "showcase", "scene"],
                            f"{self.hero}'s signature {'gown' if self.female else 'attire'}",
                            f"+, the neckline, cuffs and hem embroidered with {motif} in {{{{ACCENT_SOFT}}}}; {tone}", ov.get("gown") or pick(gowns, self.i * 2 + 1))
        crowns = pure(lib("wardrobe/headwear/circlets", self.sex, neutral=True) + lib("wardrobe/headwear/crowns", self.sex, neutral=True))
        out["headwear"] = piece("headwear", "signature-circlet", "headwear", ["armor", "clothing", "showcase", "scene"], f"{self.hero}'s signature circlet",
                                f"+, {motif} rising at the centre of the brow, set with a {{{{GEM}}}} gem; {tone}", ov.get("circlet") or pick(crowns, self.i * 2))
        out["jewelry"] = piece("jewelry", "signature-jewelry", "jewelry", ["armor", "clothing", "showcase", "scene"], f"{self.hero}'s signature jewelry",
                               (f"+, the pendant and the earrings echoing {motif}, each set with a small {{{{GEM}}}} gem" if self.female
                                else f"+, the pendant formed as {motif} and set with a small {{{{GEM}}}} gem"), NECKLACE if self.female else CHAIN)
        out["effects"] = piece("effects", "elemental-drift", "effects", ["armor", "showcase", "scene"], f"{self.hero}'s elemental drift",
                               f"A drift of {self.mat} circles {her}, {{{{MAGIC}}}} light glinting within it.")
        return out

    # ----- plumbing

    def card(self, art_id, stage, folder, stem, template, comps=None, denoise="~0.5-0.7", note=None, **extra):
        body = {"artId": art_id, "kind": "base-set", "stage": stage, "heroArt": self.ident, "template": f"{TPL}/{template}",
                "output": self.out(folder, stem), "denoise": denoise, **extra}
        if comps:
            body["components"] = comps
        if note:
            body["notes"] = note
        return body

    def write(self, sub, art_id, card):
        before = self.wr.made
        self.wr.write(sub, art_id, card)
        self.made += self.wr.made - before

    def clone(self, rel, replace=None):
        """A card of the standard sister, rebuilt for this angel. Sister-specific paths are mapped by `replace` or the clone is refused."""
        src = json.loads((SISTER / rel).read_text(encoding="utf-8"))
        pairs = [(r"data/art/heroes/drakn-sisters/draknava/armor/celestial-", "data/art/wardrobe/armor/celestial/angelic-"),
                 (r"data/art/heroes/drakn-sisters/draknava/weapons/[a-z0-9-]+\.json", self.weapon(7)),
                 (r"Draknava", self.hero), (r"draknava", self.slug)] + list((replace or {}).items())

        def sub(v):
            if isinstance(v, str):
                for pat, new in pairs:
                    v = re.sub(pat, new, v)
                return v
            if isinstance(v, list):
                return [sub(x) for x in v]
            if isinstance(v, dict):
                return {k: sub(x) for k, x in v.items()}
            return v

        card = sub(src)
        card["heroArt"] = self.ident
        stem = pathlib.PurePosixPath(src["output"]).stem.replace("Draknava", self.hero)
        card["output"] = self.out("x", stem)
        if re.search(r"drakn-sisters|[Dd]raknava|Elder Dragon", json.dumps(card)):
            raise SystemExit(f"{self.slug}: the clone of {rel} still names a sister: {json.dumps(card)[:200]}")
        return card

    def weapon(self, k=0):
        pool = lib("wardrobe/weapons", self.sex, skip=("/shields/", "/firearms/", "/whips/", "/slings/"))
        return pick(pool, self.i * 3 + k) or ""

    def jewel(self, n):
        """A piece of jewelry for the n-th scene of this angel; the whole library is rotated through, not just the two sets."""
        return pick(lib("wardrobe/jewelry", self.sex, skip=("/anklets/", "/belts/")), self.i * 4 + n) or self.sig["jewelry"]

    def pool(self, rel, **kw):
        return lib(rel, self.sex, **kw)

    def npool(self, rel, **kw):
        """Like pool(), but a male angel also gets pieces that are not tagged at all (weapons, boots and motions are mostly untagged); only female-tagged ones are left out."""
        return lib(rel, self.sex, neutral=not self.female, **kw)

    def poses(self, family):
        """Motion pieces of a family for this angel; for a male angel the ones that are plainly feminine (seductive, sensual, kiss, hair flip ...) are left out."""
        out = self.npool(f"motion/{family}")
        if not self.female:
            out = [p for p in out if not any(w in p for w in ("seductive", "sensual", "kiss", "hair-flip", "embrace", "collarbone", "sultry", "wink", "glamour", "elegant", "dreamy", "kneeling"))]
        return out

    def effect(self, text):
        return text.replace("{mat}", self.mat)

    def bg(self, purpose, k=0):
        pool = [p for d in BG[purpose] for p in lib(f"backgrounds/fantasy/{d}", "female")]
        return pick(pool, self.i * 7 + k)

    def lair(self):
        return next((p for p in lib("backgrounds/fantasy/lairs", "female") if pathlib.PurePosixPath(p).stem.startswith(self.element.lower() + "-")), self.scene["background"])

    # ----- phases

    def alpha_experiments(self):
        if not self.female:
            return
        for name in ("contoured", "paint", "paint-colour", "pasties"):
            self.write("alpha", f"{self.slug}-alpha-2b-{name}", self.clone(f"1_Alpha/2b_Experiments/coverings/draknava-alpha-2b-{name}.json"))
        for name in ("core", "plate", "plate-fitted", "suit"):
            self.write("alpha", f"{self.slug}-alpha-2b-celestial-{name}", self.clone(f"1_Alpha/2b_Experiments/celestial/draknava-alpha-2b-celestial-{name}.json"))

    def studies(self):
        own = json.loads((ROOT / self.ident).read_text(encoding="utf-8")).get("art", {}).get("defaultUnderlayer")
        under = getattr(self, "underlayer", None) or own or (BIKINI if self.female else BRIEF)
        small = getattr(self, "small", False)
        subprocess.run([sys.executable, str(ROOT / "tools/generators/scaffold_studio_library.py"), "--group", GROUP, "--slug", self.slug, "--hero", self.hero,
                        "--identity", self.ident, "--division", self.division, "--underlayer", under, *(["--small"] if small else [])], check=True, stdout=subprocess.DEVNULL)
        hair = self.kit.get("hair") or rot(interleave(lib(HAIR_LIB.removeprefix("data/art/"), self.sex, neutral=True)), self.i, 2 if small else 8)
        for path in hair:
            path = norm(path)
            fam, stem = pathlib.Path(path).parent.name, pathlib.Path(path).stem
            folder = "/".join(art_layout.dirs_for("hair", [fam]))
            self.write("hair", f"{self.slug}-hair-{stem}", {
                "artId": f"{self.slug}-hair-{stem}", "kind": "base-set", "stage": "hair", "heroArt": self.ident, "component": path,
                "template": f"{TPL}/hair-human.txt", "output": self.out(folder, f"{self.hero}_Hair_{camel(fam)}_{camel(stem)}"), "denoise": "~0.4-0.6"})

    def layers(self):
        sex = self.sex
        tpl = f"pose-{sex}-human.txt"
        if self.female:
            for p in sorted((SISTER / "3_Layers/base").glob("*.json")):
                self.write("pose", f"{self.slug}-{p.stem.removeprefix('draknava-')}", self.clone(f"3_Layers/base/{p.name}"))
            plan = [("bikini", 3), ("lingerie", 3), ("one-piece", 2), ("backless", 2), ("athletic", 2)]
            picks = self.kit.get("layers") or [x for fam, n in plan for x in rot(lib(f"wardrobe/swimwear/{fam}", sex), self.i, n)]
        else:
            picks = self.kit.get("layers") or rot(lib("wardrobe/swimwear", sex, skip=("/base/",)), self.i, 4)
        for path in picks:
            path = norm(path)
            short = pathlib.Path(path).stem
            art_id = f"{self.slug}-x-pose-{short}"
            self.write("pose", art_id, self.card(art_id, "pose", "poses", f"{self.hero}_X_Pose_{camel(short)}", tpl, {"underlayer": path}, denoise="~1.0",
                       note="UNDERLAYER TEST: fed the Bare image; only the underlayer piece differs."))

    def wardrobe_card(self, stage, path, art_id, stem, name, subject=None):
        studio = dict(STUDIO)
        if not self.female:
            studio["jewelry"] = CHAIN
        comps = {"wearing": path, **{k: v for k, v in studio.items() if stage == "armor" or k not in ("back", "holding")}}
        self.write(stage, art_id, self.card(art_id, stage, stage, stem, f"{stage}-human.txt", comps, name=name,
                   aesthetic=f"a clean studio presentation of {subject or name.lower()}", note="WARDROBE TEST: same hero, only the piece differs."))

    def signature_cards(self):
        """The angel's own armor and gown (or attire) on the studio backdrop, for both sexes: the first wardrobe the male angels have beyond their kit."""
        for stage, key, label in (("armor", "armor", "armor"), ("clothing", "gown", "gown" if self.female else "attire")):
            name = json.loads((ROOT / self.sig[key]).read_text(encoding="utf-8"))["name"]
            self.wardrobe_card(stage, self.sig[key], f"{self.slug}-{stage}-signature-{label}", f"{self.hero}_{stage.capitalize()}_Signature{label.capitalize()}", name, subject=name)

    def wardrobe(self):
        self.signature_cards()
        if self.female:
            default_clothing = rot(self.pool("wardrobe/clothing/dresses"), self.i, 6) + rot(self.pool("wardrobe/clothing/gowns"), self.i, 6) + rot(self.pool("wardrobe/clothing/sets"), self.i, 5)
        else:
            default_clothing = rot(self.pool("wardrobe/clothing/sets"), self.i, 8)
        clothing = self.kit.get("clothing_more") or default_clothing
        armor = self.kit.get("armor_more") or rot(self.pool("wardrobe/armor", skip=("/celestial/",)), self.i, 12 if self.female else 8)
        for stage, paths in (("clothing", clothing), ("armor", armor)):
            for path in paths:
                piece = json.loads((ROOT / path).read_text(encoding="utf-8"))
                short = pathlib.Path(path).stem
                self.wardrobe_card(stage, path, f"{self.slug}-{stage}-{short}", f"{self.hero}_{stage.capitalize()}_{camel(short)}", piece["name"])

    def chosen_themes(self):
        packs = sorted(themes(self.sex))
        return self.kit.get("themes") or rot(packs, self.i, 6)

    def theme_pieces(self, pack):
        t = themes(self.sex)[pack]

        def one(key, k=0):
            return pick(t[key], self.i + k)
        return t, one

    def theme_cards(self):
        for pack in self.chosen_themes():
            t, one = self.theme_pieces(pack)
            title = t["name"]
            wear = one("clothing")
            studio_comps = {"wearing": wear, "arms": "bare arms", **{k: v for k, v in (("jewelry", one("jewelry")), ("legs_feet", one("footwear")), ("headwear", one("headwear"))) if v}}
            for slot, default in (("jewelry", NECKLACE if self.female else CHAIN), ("legs_feet", BAREFOOT)):
                studio_comps.setdefault(slot, default)
            self.write("clothing", f"{self.slug}-clothing-{pack}", self.card(
                f"{self.slug}-clothing-{pack}", "clothing", "clothing", f"{self.hero}_Clothing_{camel(pack)}", "clothing-human.txt", studio_comps, name=title,
                aesthetic=f"a clean studio presentation of the {title.lower()} outfit", note=f"Pre-staged {title} outfit: render it from the A-pose, then feed the image to the staged scene. Every item is a library piece."))
            if t["armor"]:
                piece = json.loads((ROOT / one("armor")).read_text(encoding="utf-8"))
                self.wardrobe_card("armor", one("armor"), f"{self.slug}-armor-{pack}", f"{self.hero}_Armor_{camel(pack)}", piece["name"])
            if t["hair"]:
                folder = "/".join(art_layout.dirs_for("hair", ["themes"]))
                self.write("hair", f"{self.slug}-hair-{pack}", {
                    "artId": f"{self.slug}-hair-{pack}", "kind": "base-set", "stage": "hair", "heroArt": self.ident, "component": one("hair"),
                    "template": f"{TPL}/hair-human.txt", "output": self.out(folder, f"{self.hero}_Hair_{camel(pack)}"), "denoise": "~0.4-0.6", "notes": f"{title} theme hairstyle."})

    def male_showcases(self):
        """Four studio showcases for a male angel from his own signature pieces (the sisters' showcase cards are written for women and cannot be cloned)."""
        studio = lib("backgrounds/studio", "female")
        wings = self.scene["back"]
        armor = self.pool("wardrobe/armor", skip=("/celestial/",), skip_tags=("bikini",))
        sets = self.pool("wardrobe/clothing/sets")
        specs = [
            ("spell-calling", "Spell Calling", "motion/standing/commanding-cast", self.sig["armor"], self.sig["weapon"],
             "Swirling {mat} rise and circle him, {{MAGIC}} light streaming from the weapon in his hand."),
            ("elemental-casting", "Elemental Casting", "motion/action/guard-stance", self.sig["gown"], None,
             "A swirl of {mat} lifts around his raised hand, small whirlwinds orbiting in a slow ring, small sparks of {{MAGIC}} light within it."),
            ("armor-stand", "Armor Stand", "motion/standing/hand-on-hip-power", self.sig["armor"], None,
             "A curtain of {mat} hangs in the air behind him in a protective arc, {{MAGIC}} light running through it."),
            ("runway-flair", "Runway Flair", "motion/walking/strut-runway", pick(armor or sets, self.i * 3 + 2), None,
             "Gusts of {mat} stream along the floor either side of him, rising around him."),
        ]
        for n, (name, title, pose, wear, hold, fx) in enumerate(specs):
            comps = {"jewelry": self.sig["jewelry"], "legs_feet": "data/art/wardrobe/footwear/barefoot/barefoot.json", "pose": norm(pose), "wearing": wear, "back": wings,
                     "effects": self.effect(fx), "background": pick(studio, self.i * 6 + n)}
            if hold:
                comps["holding"] = hold
            art_id = f"{self.slug}-showcase-{name}"
            self.write("showcase", art_id, self.card(art_id, "showcase", "showcase", f"{self.hero}_Showcase_{camel(name)}", "showcase-human.txt", comps, name=title,
                       note="SHOWCASE: a studio shot on a coloured backdrop with magic and flair, before it becomes a scene."))

    def showcases(self):
        if not self.female:
            return self.male_showcases()
        gowns, dresses, sets = (self.pool(f"wardrobe/clothing/{f}") for f in ("gowns", "dresses", "sets"))
        mood = {"glamour": gowns, "romantic": dresses + sets, "daily": dresses + sets}
        k = 0
        for fam in ("editorial", "celestial", "photo/glamour", "photo/romantic", "photo/daily"):
            for p in sorted((SISTER / f"4_Wardrobe/showcase/{fam}").glob("*.json")):
                replace = {}
                src = json.loads(p.read_text(encoding="utf-8"))
                wear = src.get("components", {}).get("wearing", "")
                if wear.startswith("data/art/wardrobe/clothing/"):
                    pool = mood.get(fam.split("/")[-1], gowns + dresses)
                    replace = {re.escape(wear): pick(pool, self.i * 5 + k)}
                    k += 1
                self.write("showcase", f"{self.slug}-{p.stem.removeprefix('draknava-')}", self.clone(f"4_Wardrobe/showcase/{fam}/{p.name}", replace))
        armor = self.pool("wardrobe/armor", skip=("/celestial/",), skip_tags=("bikini",))
        robe = pick(self.pool("wardrobe/clothing/gowns"), self.i * 2)
        studio = self.pool("backgrounds/studio")
        wings = self.scene["back"]
        specs = [
            ("elemental", "spell-calling", "Spell Calling", "motion/standing/commanding-cast", self.sig["armor"], self.sig["weapon"],
             "Swirling {mat} rise and circle around her, {{MAGIC}} light streaming from the weapon in her hand."),
            ("elemental", "elemental-casting", "Elemental Casting", "motion/standing/three-quarter-glamour", robe, None,
             "A swirl of {mat} lifts around her raised hand, small whirlwinds orbiting in a slow ring, small sparks of {{MAGIC}} light within it."),
            ("elemental", "elemental-dance", "Elemental Dance", "motion/dynamic/twirl-spin", pick(self.pool("wardrobe/clothing/dresses"), self.i * 2), None,
             "Ribbons of {{MAGIC}} light trail from her hands and her hem as she spins, {mat} swirling in the air around her."),
            ("elemental", "mirror-spirit", "Mirror Spirit", "motion/dynamic/kneeling-glamour", pick(gowns, self.i * 2 + 1), None,
             "A pale spirit double of her rises from her reflection in the floor, {mat} drifting between them."),
            ("studio", "armor-stand", "Armor Stand", "motion/standing/hand-on-hip-power", self.sig["armor"], None,
             "A curtain of {mat} hangs in the air behind her in a protective arc, {{MAGIC}} light running through it."),
            ("studio", "runway-flair", "Runway Flair", "motion/walking/catwalk-confident", pick(armor, self.i * 3 + 2), None,
             "Gusts of {mat} stream along the floor either side of her, rising around her."),
        ]
        for n, (fam, name, title, pose, wear, hold, fx) in enumerate(specs):
            comps = {"jewelry": self.sig["jewelry"], "legs_feet": "data/art/wardrobe/footwear/barefoot/barefoot-anklets.json",
                     "pose": norm(pose), "wearing": wear, "back": wings, "effects": self.effect(fx), "background": pick(studio, self.i * 6 + n)}
            if hold:
                comps["holding"] = hold
            art_id = f"{self.slug}-showcase-{name}"
            self.write("showcase", art_id, self.card(art_id, "showcase", "showcase", f"{self.hero}_Showcase_{camel(name)}", "showcase-human.txt", comps, name=title,
                       note="SHOWCASE: a studio shot on a coloured backdrop with magic and flair, before it becomes a scene."))

    def scenes(self):
        i, sc, hero, slug = self.i, self.scene, self.hero, self.slug
        if self.female:
            gowns, dresses = self.pool("wardrobe/clothing/gowns"), self.pool("wardrobe/clothing/dresses")
            robes = self.pool("wardrobe/clothing/robes") or gowns
            feet = self.pool("wardrobe/footwear/heels") + self.pool("wardrobe/footwear/sandals")
        else:
            gowns = dresses = self.pool("wardrobe/clothing/sets")
            robes = self.pool("wardrobe/armor/robes") or gowns
            feet = self.npool("wardrobe/footwear/flats") + self.npool("wardrobe/footwear/sandals")
        heads = self.pool("wardrobe/headwear", skip=("/helms/",))
        helms = self.pool("wardrobe/headwear/helms")
        boots = self.npool("wardrobe/footwear/boots")
        sets = self.pool("wardrobe/jewelry/sets")
        armor = self.pool("wardrobe/armor", skip=("/celestial/",), skip_tags=("bikini",))
        wings, pet, realm = sc["back"], sc["companion"], sc["background"]
        common = {"back": wings}

        def scene(name, art, template, comps, title, note, stem=None, **extra):
            stem = stem or f"{hero}_Scene_{camel(art)}"
            comps = {k: v for k, v in comps.items() if v}
            self.write("scene", f"{slug}-scene-{art}", self.card(f"{slug}-scene-{art}", "scene", "scene", stem, template, comps, name=title, note=note, **extra))

        # glamour
        scene("glamour", "glamour", "scene-glamour-human.txt", {
            "pose": norm(pick(self.poses("romantic") if self.female else self.poses("standing"), i)), "wearing": pick(dresses, i * 3), "jewelry": self.jewel(0), "legs_feet": pick(feet, i), **common,
            "effects": self.effect("A gentle drift of {mat} lifts her hair and hem, faint {{MAGIC}} light glinting within it - understated."),
            "eye_effect": EYES + "iris-kindling.json", "background": realm}, "Glamour", "GLAMOUR: a relaxed, beautiful portrait in her element's realm.")
        evening_bg = self.bg("evening")
        scene("enchanted-evening", "enchanted-evening", "scene-with-companion-human.txt", {
            "pose": "data/art/motion/standing/three-quarter-glamour.json" if self.female else "data/art/motion/walking/strut-runway.json", "wearing": pick(gowns, i * 3 + 1), "jewelry": self.jewel(1), "legs_feet": pick(feet, i + 3),
            "effects": "data/art/wardrobe/effects/ambient/soft-ambient-glow.json", "companion": pet, **common, "background": evening_bg},
            "Enchanted Evening", "ENCHANTED EVENING: an evening gown, her bonded pet beside her, an evening setting.")
        scene("staged-enchanted-evening", "staged-enchanted-evening", "scene-staged-human.txt", {
            "pose": "data/art/motion/standing/three-quarter-glamour.json", "effects": "data/art/wardrobe/effects/ambient/soft-ambient-glow.json", "companion": pet,
            "background": evening_bg}, "Enchanted Evening", "STAGED scene: the incoming image already carries hair, makeup and outfit; this pass adds only the evening scene, glow and her pet.",
            stem=f"{hero}_Scene_Staged_EnchantedEvening",
            base_description="{{HERO}} already staged with her chosen hair, makeup and outfit (an outfit render, or just the metallic bikini A-pose to start)")
        scene("elegant-casting", "elegant-casting", "scene-with-outfit-human.txt", {
            "pose": self.effect("She is caught mid-turn in a spinning cast, one leg lifted behind her, both arms sweeping upward in a spiral gesture that draws a column of {mat} around her, her head turned back to the camera with a bright, serene gaze. Casting with her bare hands only."),
            "wearing": self.sig["gown"], "jewelry": self.sig["jewelry"], "legs_feet": pick(feet, i + 5), **common,
            "effects": self.effect("A shimmering column of {mat}, visible as streaming ribbons and {{MAGIC}} light, spirals around her."), "background": self.bg("casting")},
            "Elegant Casting", "ELEGANT CASTING: a hands-only complex casting stance in her element.")
        scene("robe", "robe", "scene-with-outfit-human.txt", {
            "pose": "data/art/motion/walking/slow-sensual-walk.json" if self.female else "data/art/motion/walking/relaxed-stroll.json", "wearing": pick(robes, i), "headwear": pick(heads, i), "jewelry": self.jewel(3), "legs_feet": pick(feet, i + 7), **common,
            "holding": pick(self.npool("wardrobe/weapons/staves") + self.npool("wardrobe/weapons/wands"), i),
            "effects": self.effect("The hem of the robe and her scarves lift gently in a passing breeze, faint {{MAGIC}} light and drifting {mat} around her."), "background": self.bg("sanctum")},
            "Robe", "ROBE: a flowing robe, a staff and a quiet sanctum.")
        # story
        scene("battle", "battle", "scene-with-outfit-human.txt", {
            "pose": "She leaps mid-air with her weapon swept behind her and her free hand flung forward, wings spread wide, a calm, fierce gaze straight to the camera; full figure visible.",
            "wearing": self.sig["armor"], "headwear": self.sig["headwear"], "jewelry": self.sig["jewelry"], "legs_feet": pick(boots, i), "holding": self.sig["weapon"], **common,
            "effects": self.effect("A surge of {mat} bursts out from her free hand, tearing banners and debris sideways, {{MAGIC}} light marking the currents."),
            "eye_effect": EYES + "partial-glow.json", "background": self.bg("battle")}, "Battle", "BATTLE: war gear and a weapon in a battlefield setting, commanding her element.")
        scene("bond", "bond", "scene-with-companion-human.txt", {
            "pose": "She stands close to her bonded companion, one hand raised and gently resting against it, her other hand relaxed at her side, her face turned toward the camera with wonder and quiet certainty; the companion turns toward her and both are fully in frame.",
            "wearing": pick(gowns, i * 3 + 3), "jewelry": self.jewel(5), "legs_feet": ANKLETS if self.female else BAREFOOT, **common,
            "effects": self.effect("A thread of {{MAGIC}} light runs from her hand to her companion where they touch, the bond glowing, motes of {mat} rising between them."),
            "eye_effect": EYES + "iris-kindling.json", "companion": pet, "background": self.lair()}, "Bond", "BOND: the angel and her bonded pet in the lair of her element.")
        scene("the-dawn", "the-dawn", "scene-with-outfit-human.txt", {
            "pose": self.effect("Fast, graceful ascent: she rises upright through the centre of a great column of {mat} with her wings half open and her body turning gently, arms out and lifted, head lifted and gaze to the camera, joyful and free; full figure from head to toe visible."),
            "wearing": pick(dresses, i * 3 + 1), "jewelry": self.jewel(6), "legs_feet": ANKLETS if self.female else BAREFOOT, **common,
            "effects": self.effect("A great spiral of {mat} rises in a swirling column around her, streaks of {{MAGIC}} light tracing the air, clouds swept back."),
            "eye_effect": EYES + "iris-kindling.json", "background": realm}, "TheDawn", "THE DAWN: the angel rising through her element's realm.", stem=f"{hero}_Scene_TheDawn")
        # themes: complete and staged
        for n, pack in enumerate(self.chosen_themes()):
            t, one = self.theme_pieces(pack)
            title = t["name"]
            bg = one("background")
            realm_name = bg.split("/backgrounds/")[1].split("/")[0]
            comps = {"pose": norm(pick(self.poses("standing") or self.poses("walking"), i + n)), "expression": pick(EXPRESSIONS, i + n), "wearing": one("clothing"), **common,
                     "effects": self.sig["effects"], "background": bg}
            for key, cat in (("headwear", "headwear"), ("jewelry", "jewelry"), ("legs_feet", "footwear"), ("holding", "props"), ("makeup", "makeup")):
                if one(cat):
                    comps[key] = one(cat)
            comps.setdefault("jewelry", self.sig["jewelry"])
            if "holding" not in comps and one("weapons"):
                comps["holding"] = one("weapons")
            if realm_name != "fantasy":
                comps["realm"] = f"data/art/realms/{realm_name}.json"
            scene(pack, pack, "scene-with-outfit-human.txt", comps, title, f"{title} theme scene: every item is a library piece.")
            staged = {"pose": comps["pose"], "effects": comps["effects"], "background": bg, "expression": comps["expression"]}
            if "realm" in comps:
                staged["realm"] = comps["realm"]
            scene(f"staged-{pack}", f"staged-{pack}", "scene-staged-human.txt", staged, title, f"STAGED path: feed the {slug}-clothing-{pack} studio render; only the scene, effects and pose are added.",
                  stem=f"{hero}_Scene_Staged_{camel(pack)}", base_description=f"{{{{HERO}}}} already staged in the {title.lower()} outfit render")

    # ----- character scenes: what she is doing follows who she is (recipes in data/art/_settings/scene-recipes.json)

    def character(self):
        """The Lineup (a shared-backdrop cut-out, like the sisters'), a duty and a quiet scene from her alignment, a domain scene from her element and, when the element has a theme pack,
        one celebration scene. Existing cards are kept, so this is safe to re-run."""
        recipes = json.loads((ART / "_settings/scene-recipes.json").read_text(encoding="utf-8"))
        i, hero, slug, rank = self.i, self.hero, self.slug, self.kit["alignmentRank"]
        wings = self.scene["back"]
        if self.female:
            robes = self.pool("wardrobe/clothing/robes") or self.pool("wardrobe/clothing/gowns")
        else:
            robes = self.pool("wardrobe/armor/robes") or self.pool("wardrobe/clothing/sets")
        boots = self.npool("wardrobe/footwear/boots")
        bare = ANKLETS if self.female else BAREFOOT

        def write(art, title, comps, note, template="scene-with-outfit-human.txt"):
            comps = {k: v for k, v in comps.items() if v}
            self.write("scene", f"{slug}-scene-{art}", self.card(f"{slug}-scene-{art}", "scene", "scene", f"{hero}_Scene_{camel(art)}", template, comps, name=title, note=note))

        write("lineup", "Lineup", {
            "pose": "data/art/motion/scene/lineup-square-stance.json", "wearing": self.sig["gown"], "headwear": self.sig["headwear"], "jewelry": self.sig["jewelry"], "legs_feet": bare, "back": wings,
            "effects": self.effect("{mat} orbit her hands in a small, close ring and a little {{MAGIC}} light rises at her feet."), "eye_effect": EYES + "iris-kindling.json",
            "background": "data/art/backgrounds/studio/dawn-rim-grey.json", "realm": "data/art/realms/studio.json"},
            "GROUP SHOT cut-out: her signature outfit on the flat grey backdrop with the shared dawn lighting, full figure, effects kept close, to be composited with the other angels (the sisters' Lineup is the same).")

        def recipe_card(r, k):
            wear = {"armor": self.sig["armor"], "gown": self.sig["gown"], "robe": pick(robes, i)}[r["wearing"]]
            hold = {"weapon": self.sig["weapon"], "staff": pick(self.npool("wardrobe/weapons/staves"), i), "none": ""}.get(r.get("holding", "none"), r.get("holding"))
            pool = [p for d in r["background"] for p in lib(f"backgrounds/fantasy/{d}", "female")] if r.get("background") else []
            bg = pick(pool, i * 7 + k) if pool else self.scene["background"]
            comps = {"pose": self.effect(r["pose"]), "wearing": wear, "headwear": self.sig["headwear"] if r["wearing"] != "robe" else "", "jewelry": self.sig["jewelry"],
                     "legs_feet": pick(boots, i) if r["wearing"] == "armor" and boots else bare, "back": wings, "holding": hold, "effects": cap(self.effect(r["effects"])),
                     "eye_effect": EYES + r["eyes"] + ".json" if r.get("eyes") else "", "background": bg, "realm": r.get("realm", "")}
            return comps

        for kind, label in (("duty", "DUTY"), ("quiet", "QUIET")):
            r = next(x for x in recipes[kind] if x["ranks"][0] <= rank <= x["ranks"][1])
            write(r["id"], r["name"], recipe_card(r, 0), f"{label}: {r['name']}, for her alignment (rank {rank}); from data/art/_settings/scene-recipes.json.")
        r = next(x for x in recipes["domain"] if x["element"] == self.element)
        write("domain", "Domain", recipe_card(dict(r, background=None), 0), f"DOMAIN: her {self.element} element at work in its realm; from data/art/_settings/scene-recipes.json.")

        pack = recipes["celebration"].get(self.element)
        t = themes(self.sex).get(pack) if pack else None
        if t:
            def one(key, k=0):
                return pick(t[key], i + k)
            wear = one("armor") if t.get("armor") and pack == "siege-defense" else one("clothing")
            bg = one("background")
            comps = {"pose": norm(pick(self.poses("standing") or self.poses("walking"), i)), "expression": pick(EXPRESSIONS, i), "wearing": wear, "back": wings, "headwear": one("headwear"),
                     "jewelry": one("jewelry") or self.sig["jewelry"], "legs_feet": one("footwear") or (pick(boots, i) if "armor" in wear else bare), "makeup": one("makeup"), "effects": self.sig["effects"], "background": bg}
            write(pack, t["name"], comps, f"{t['name']} celebration scene for her element: every item is a library or theme-pack piece.")

    def realm_series(self):
        """Opt-in (scaffold_angel_set.py --realm): her element's homeland as a place, scene by scene, in the realistic element realm (no class, so no haunt). Existing cards are kept."""
        recipes = json.loads((ART / "_settings/scene-recipes.json").read_text(encoding="utf-8"))
        realm = f"data/art/realms/{self.element.lower()}-lands.json"
        country = ART / "backgrounds/fantasy/country" / self.element.lower()
        if not (ROOT / realm).exists() or not country.is_dir():
            return
        robes = (self.pool("wardrobe/clothing/robes") or self.pool("wardrobe/clothing/gowns")) if self.female else (self.pool("wardrobe/armor/robes") or self.pool("wardrobe/clothing/sets"))
        boots = self.npool("wardrobe/footwear/boots")
        bare = ANKLETS if self.female else BAREFOOT
        for r in recipes.get("realm", []):
            pool = [p.relative_to(ROOT).as_posix() for p in sorted(country.glob("*.json")) if r["role"] in tags_of(p)]
            if not pool:
                continue
            kind = r["wearing"]
            wear = {"armor": self.sig["armor"], "gown": self.sig["gown"], "robe": self.sig["gown"]}[kind]
            hold = {"weapon": self.sig["weapon"], "none": ""}.get(r.get("holding", "none"), r.get("holding"))
            comps = {"pose": self.effect(r["pose"]), "wearing": wear, "headwear": self.sig["headwear"] if kind != "robe" else "", "jewelry": self.sig["jewelry"],
                     "legs_feet": pick(boots, self.i) if kind == "armor" and boots else bare, "back": self.scene["back"], "holding": hold, "effects": cap(self.effect(r["effects"])),
                     "eye_effect": EYES + r["eyes"] + ".json" if r.get("eyes") else "", "background": pool[0], "realm": realm}
            art = r["id"]
            self.write("scene", f"{self.slug}-scene-{art}", self.card(f"{self.slug}-scene-{art}", "scene", "scene", f"{self.hero}_Scene_{camel(art)}", "scene-with-outfit-human.txt",
                       {k: v for k, v in comps.items() if v}, name=r["name"], note=f"REALM SERIES: {r['name']} in her {self.element.lower()} homeland ({r['role']}); realistic."))

    def finish(self):
        for stage, name, tpl, denoise, note in (
                ("polish", "Detail", "polish-human.txt", "~0.2-0.4", "SKELETON: a detail-only pass on her chosen finished image (input role scene); tune the wording once there are scenes to polish."),
                ("final", "Look", "final-human.txt", "~0.6-0.8", "SKELETON: the terminal look on her polished image (input role polish, FireRed); tune the wording once there are polished images.")):
            art_id = f"{self.slug}-{stage}-{name.lower()}"
            self.write(stage, art_id, self.card(art_id, stage, stage, f"{self.hero}_{stage.capitalize()}_{name}", tpl, denoise=denoise, name={"polish": "Detail pass", "final": "Final look"}[stage], note=note))

    def motions(self):
        fams = ("standing", "dynamic", "walking", "romantic", "action") if self.female else ("standing", "walking", "action")
        pool = [p for f in fams for p in lib(f"motion/{f}", self.sex, neutral=True)]
        for path in (self.kit.get("motions_more") or rot(pool, self.i, 12 if self.female else 10)):
            path = norm(path)
            fam, short = pathlib.Path(path).parent.name, pathlib.Path(path).stem
            art_id = f"{self.slug}-motion-{short}"
            self.write(f"motion/{fam}", art_id, self.card(art_id, "motion", "/".join(art_layout.dirs_for("motion", [fam])), f"{self.hero}_Motion_{camel(fam)}_{camel(short)}",
                       "motion-human.txt", denoise="~0.4-0.6", component=path))

    def video(self):
        """7_Video: animation cards (data/animation/_sets/angel-primes/<division>/<slug>/) built from reusable motion pieces, like the sisters' three per hero.
        Every angel gets the signature video; the theme-motion video needs a theme scene card of her or his own."""
        anim = ROOT / "data/animation"
        base = anim / "_sets" / GROUP / self.division / self.slug
        element_motion = f"data/animation/motions/elements/{ELEMENT_MOTION[self.element]}.json"
        pet = ""
        try:
            pet = json.loads((ROOT / json.loads((ROOT / self.ident).read_text(encoding="utf-8"))["profile"]["pet"]).read_text(encoding="utf-8")).get("name", "")
        except (OSError, ValueError, KeyError):
            pass
        pet = pet or "{{her}} bonded companion"

        def scene_card(name):
            return next(((p, json.loads(p.read_text(encoding="utf-8"))) for p in (ART / "_sets" / GROUP / self.division / self.slug).rglob(f"{self.slug}-scene-{name}.json")), (None, None))

        def write(anim_id, name, scene, cfg):
            path, art = scene_card(scene)
            target = base / f"{anim_id}.json"
            if art is None or target.exists():
                return
            stem = pathlib.PurePosixPath(art["output"]).stem  # <Hero>_Scene_<Name>
            card = {"animId": anim_id, "kind": "animation", "name": name, "heroArt": self.ident,
                    "source": {"artCard": path.relative_to(ROOT).as_posix(), "image": stem.replace("_Scene_", "_Qwen_Scene_") + "_00001_.png"}, **cfg,
                    "size": [640, 960], "template": "data/animation/_templates/video-minimax.txt"}
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            self.made += 1

        ambient = "data/animation/motions/ambient/"
        world = f"The realm is alive: {self.mat} stream and swirl through the air, feathers drift down and clouds sweep past."
        write(f"{self.slug}-anim-scene-the-dawn-rising", "Rising", "the-dawn", {
            "look": "data/animation/looks/cinematic-photoreal.json", "camera": "data/animation/cameras/orbit-reveal.json",
            "audio": "a soaring choral and string melody; no speech", "world": world,
            "actions": [
                {"motion": element_motion, "seconds": 2.5, "transition": "flow", "with": [{"motion": ambient + "clouds-race.json"}]},
                {"beat": "{{She}} rises upright through the centre of the great column, {{her}} wings opening wide and {{her}} arms lifted, turning gently in the light.", "seconds": 3, "transition": "blend"},
                {"beat": "{{She}} turns a joyful, radiant look to the camera as the light settles and feathers drift down around {{her}}.", "seconds": 2.5, "transition": "settle"}],
            "notes": "THE DAWN, in motion: the angel rises through her element's realm."})
        write(f"{self.slug}-anim-scene-signature-ascension", "Ascension", "signature", {
            "look": "data/animation/looks/cinematic-photoreal.json", "camera": "data/animation/cameras/crane-rise.json",
            "audio": "a soaring choral and string melody and the call of her bonded companion; no speech", "world": world,
            "actions": [
                {"motion": element_motion, "seconds": 2.5, "transition": "flow", "with": [{"motion": ambient + "god-rays-shift.json"}]},
                {"beat": f"{{{{She}}}} spreads {{{{her}}}} wings wide as {{{{her}}}} halo ignites, and {pet} rises beside {{{{her}}}}.", "seconds": 3, "transition": "blend",
                 "with": [{"motion": ambient + "companion-stirs.json"}]},
                {"beat": "{{She}} turns a calm, radiant look to the camera as the light and the feathers settle.", "seconds": 2.5, "transition": "settle"}],
            "notes": "The signature scene in motion: wings, element light and the bonded pet."})
        pack, motions = None, []
        for cand in self.chosen_themes():
            cat = next((p.parts[-3] for p in (ART / "themes").rglob("theme.json") if p.parent.name == cand), "")
            folder = next((d for d in (cand, cat) if (anim / "motions/themes" / d).is_dir()), None)
            if folder and scene_card(cand)[1]:
                pack, motions = cand, sorted((anim / "motions/themes" / folder).glob("*.json"))
                break
        if pack and motions:
            write(f"{self.slug}-anim-scene-{pack}-motion", f"{camel(pack)}Motion", pack, {
                "look": "data/animation/looks/card-art.json",
                "actions": [
                    {"motion": motions[0].relative_to(ROOT).as_posix(), "seconds": 2.5, "transition": "flow", "with": [{"motion": ambient + "dust-motes-glow.json"}]},
                    {"motion": element_motion, "transition": "blend", "with": [{"motion": ambient + "sparkles-shimmer.json"}]},
                    {"motion": ambient + "clouds-race.json", "transition": "settle"}],
                "notes": "The theme scene in motion, built only from reusable pieces: a theme effect, her element and ambient world effects."})

    @classmethod
    def older(cls, slug, hero, ident, sex, division, wr, out, underlayer):
        """The older pair (Angelica, Angelo) has no kit: only the parts every angel shares, the Alpha experiments and the studies (heads, views, body views, hair), are built for them."""
        self = object.__new__(cls)
        self.slug, self.kit, self.ident, self.sex, self.division, self.wr, self.out = slug, {}, ident, sex, division, wr, out
        self.hero, self.female, self.i, self.made, self.underlayer = hero, sex == "female", 10, 0, underlayer
        return self

    @classmethod
    def alpha(cls, slug, hero, ident, sex, wr, out):
        """An alpha test hero: the same studies as the others but the short version (see scaffold_studio_library --small), with two hairstyles."""
        self = cls.older(slug, hero, ident, sex, "alpha", wr, out, None)
        self.underlayer, self.small = ("data/art/wardrobe/swimwear/bikini/triangle-bikini.json" if sex == "female" else BRIEF), True
        hair = {"female": ["down/beach-waves", "updo/high-bun"], "male": ["short/textured-crop", "pulled-back/low-ponytail-sleek"]}[sex]
        self.kit = {"hair": [f"{HAIR_LIB}/{h}.json" for h in hair]}
        return self

    def extend_older(self):
        for step in (self.alpha_experiments, self.studies):
            step()

    def extend(self):
        for step in (self.alpha_experiments, self.studies, self.layers, self.wardrobe, self.theme_cards, self.showcases, self.scenes, self.finish, self.motions, self.video):
            step()


def coverage():
    """How often each library family is exercised by the angels' cards (counts distinct pieces used against the pieces that exist)."""
    used = {}
    for p in (ART / "_sets" / GROUP).rglob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        for v in [d.get("component", "")] + list(d.get("components", {}).values()):
            if isinstance(v, str) and v.startswith("data/art/") and v.endswith(".json"):
                used.setdefault(v, set()).add(p.relative_to(ART / "_sets" / GROUP).parts[1])
    rows = []
    families = [("swimwear/" + f, f"data/art/wardrobe/swimwear/{f}") for f in ("bikini", "lingerie", "one-piece", "backless", "athletic", "trunks", "base")] + [
        ("clothing/" + f, f"data/art/wardrobe/clothing/{f}") for f in ("dresses", "gowns", "sets")] + [
        ("armor", "data/art/wardrobe/armor"), ("footwear", "data/art/wardrobe/footwear"), ("headwear", "data/art/wardrobe/headwear"), ("jewelry", "data/art/wardrobe/jewelry"),
        ("weapons", "data/art/wardrobe/weapons"), ("hair", HAIR_LIB), ("motion", "data/art/motion"), ("backgrounds/fantasy", "data/art/backgrounds/fantasy"),
        ("backgrounds/studio", "data/art/backgrounds/studio"), ("backgrounds/modern", "data/art/backgrounds/modern"), ("themes (packs)", "data/art/themes")]
    for label, root in families:
        total = [p.relative_to(ROOT).as_posix() for p in (ROOT / root).rglob("*.json") if p.name != "theme.json" and "/motion/scene/" not in p.as_posix() and "/expressions/scene/" not in p.as_posix()]
        hit = [p for p in total if p in used]
        extra = ""
        if label == "themes (packs)":
            packs = {p.split("/")[4] for p in total}  # data/art/themes/<category>/<pack>/...
            hit_packs = {p.split("/")[4] for p in hit}
            total, hit, extra = list(packs), list(hit_packs), "  unused: " + ", ".join(sorted(packs - hit_packs))
        rows.append(f"  {label:24} {len(hit):4} of {len(total):4} used{extra}")
    print("library coverage by the angel cards:\n" + "\n".join(rows))
