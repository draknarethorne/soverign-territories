"""Where an art card lives and where its image ends up: one rule, shared by the generators and the validator.

Every card is filed under the pipeline PHASE its prompt belongs to (phase_path), then a FAMILY; the card file, the prompt and the
ComfyUI output folder all use the same folders:

  data/art/_sets/<group>/<slug>/<phase folders...>/<artId>.json
  prompts/<group>/<Hero>/<phase folders...>/<Hero>_<Stage>_<Name>.txt
  ComfyUI output: <group>/<Hero>/<phase folders...>/<Hero>_<Engine>_<Stage>_<Name>_00001_.png

(1_Alpha, 2_Studies, 3_Layers, 4_Wardrobe, 5_Scenes, 6_Finish, 7_Video, Bench; brand and card art keep <stage>/<family>.)

The family comes from the card, never from a hand-typed folder, so a new card cannot end up in the wrong place.
Hair and motion cards already carry their own family folders and are left as they are.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

THEMES = {p.parent.name for p in (ROOT / "data/art/themes").rglob("theme.json")}
LAYOUT_STAGES = {"scene", "pose", "head", "clothing", "armor", "showcase", "brand", "card", "alpha", "polish", "final"}
STAGE_FOLDER = {"pose": "poses"}
BRAND_FAMILIES = {"key-art": "key-art", "title": "title", "plate": "plate", "logo": "logo", "icon": "icon", "harmonize": "edit"}
# Sister scenes are grouped into a few broad buckets. A folder only exists to hold closely related cards: a shiny or
# holo edition sits beside its signature card, and one-card groups stay flat in the stage folder.
SCENE_BUCKETS = {
    "signature": ["signature", "lineup"],
    "glamour": ["glamour", "glamour-test", "elegant-casting", "robe"],
    "story": ["the-dawn", "battle", "bond"],
}


# Real-world photo showcases group by mood; showcases on a studio backdrop group by kind (celestial armor, elemental magic, studio display, editorial).
SHOWCASE_STUDIO = {"armor-stand", "runway-flair"}
SHOWCASE_ELEMENTAL = {"elemental-casting", "elemental-dance", "spell-calling", "mirror-spirit", "ancestral-fire", "earthen-casting",
                      "spirit-dance", "stone-ward", "totem-calling"}
PHOTO_MOODS = {
    "glamour": ["catwalk", "grand-staircase", "rooftop-sunset", "portrait-closeup"],
    "romantic": ["bed-sitting", "bed-lying", "window-light", "beach-sunset"],
    "daily": ["beach-walk", "city-street", "bathroom-selfie", "cafe-table", "poolside"],
}


def showcase_family(art_id):
    rest = art_id.split("-showcase-", 1)[1] if "-showcase-" in art_id else art_id
    if rest.startswith("photo-"):
        name = rest[len("photo-"):]
        return next((["photo", mood] for mood, names in PHOTO_MOODS.items() if name in names), ["photo"])
    if rest.startswith("celestial-"):
        return ["celestial"]
    if rest.startswith("editorial-"):
        return ["editorial"]
    if rest in SHOWCASE_STUDIO:
        return ["studio"]
    return ["elemental"] if rest in SHOWCASE_ELEMENTAL else []


def scene_family(art_id, group):
    rest = art_id.split("-scene-", 1)[1] if "-scene-" in art_id else art_id
    if group != "drakn-sisters":
        return ["modern"] if rest.startswith("modern-") else []
    if rest.removeprefix("staged-") in THEMES:
        return ["themes"]
    if rest.startswith("signature-"):
        return ["signature"]
    if "enchanted-evening" in rest:
        return ["glamour"]
    for bucket, names in SCENE_BUCKETS.items():
        if rest in names:
            return [bucket]
    return []


def brand_family(art_id):
    """Brand art (title, key art, plate, logo, icons) groups by what it is: <slug>-brand-<family>-<name>."""
    rest = art_id.split("-brand-", 1)[1] if "-brand-" in art_id else art_id
    for prefix, fam in BRAND_FAMILIES.items():
        if rest == prefix or rest.startswith(prefix + "-"):
            return [fam]
    return []


def wearing_family(card):
    """Library clothing groups by its family (dresses, gowns, sets) and library armor shares one folder; signature items stay flat."""
    wear = card.get("components", {}).get("wearing", "")
    if wear.startswith("data/art/themes/"):
        return ["themes"]
    parts = wear.split("/")
    if not (wear.startswith("data/art/wardrobe/") and len(parts) >= 6):
        return []
    return ["wardrobe"] if card["stage"] == "armor" else [parts[4]]


# A-pose underlayer tests group by what the piece is (its tags, first match wins).
UNDERLAYER_FAMILIES = [
    ("base", {"base"}),
    ("backless", {"backless"}),
    ("lingerie", {"lingerie", "sleepwear"}),
    ("athletic", {"athletic", "sporty", "dance"}),
    ("one-piece", {"one-piece", "bodysuit", "leotard"}),
    ("bikini", {"bikini", "sarong"}),
    ("swimwear", {"swimwear"}),
]


def underlayer_family(card, root):
    path = card.get("components", {}).get("underlayer", "")
    try:
        tags = set(json.loads((pathlib.Path(root) / path).read_text(encoding="utf-8")).get("tags", []))
    except (OSError, ValueError):
        return []
    return next(([name] for name, wanted in UNDERLAYER_FAMILIES if tags & wanted), [])


def family(card, group, root=None):
    """Folders below the stage for this card, or None when the stage keeps its own layout (hair, motion)."""
    stage, art_id, comps = card["stage"], card["artId"], card.get("components", {})
    if stage not in LAYOUT_STAGES:
        return None
    if stage == "scene":
        return scene_family(art_id, group)
    if stage == "brand":
        return brand_family(art_id)
    if stage == "card":
        return []  # mass card art sits flat in its stage folder
    if stage == "alpha":
        # The creation chain of a hero: 1 Prime (from the original photo) at the root, 2 Bare (the figure and chest looks flat in bare/; the experiments
        # 2b nested in bare/celestial and bare/coverings), 3 Barefoot and Heels.
        if art_id.endswith(("-alpha-barefoot", "-alpha-heels")):
            return ["footwear"]
        if "-alpha-2b-celestial" in art_id:
            return ["bare", "celestial"]
        return ["bare", "coverings"] if "-alpha-2b-" in art_id else ["bare"] if "-alpha-bare-" in art_id else []
    if stage == "pose":
        if "view" in comps:
            return ["views"]
        return underlayer_family(card, root or ROOT) if "underlayer" in comps and not art_id.endswith("-x-pose") else []
    if stage == "showcase":
        return showcase_family(art_id)
    if stage == "head":
        return [] if art_id.endswith("-x-head") else ["views"] if "view" in comps else ["closeups"]
    if stage in ("clothing", "armor"):
        return wearing_family(card)
    return []


def stage_folder(stage):
    return STAGE_FOLDER.get(stage, stage)


# The pipeline, in order: a card file, its prompt, a workflow and its ComfyUI output all sit under <Hero>/<phase>/..., so the folders read like the
# process. Motion is a bench, not a phase: a point-in-time test run on any phase's image.
LAYER_TYPES = {"base", "backless", "lingerie", "athletic", "one-piece", "bikini", "swimwear"}


def phase_path(stage, family):
    """Folders below the hero for a workflow and its output, from the prompt's stage folder and family folders; None for stages outside the hero chain."""
    fam = list(family)
    if stage == "alpha":
        if fam[:1] == ["bare"]:
            return ["1_Alpha", "2b_Experiments", fam[1]] if len(fam) > 1 else ["1_Alpha", "2_Bare"]
        return ["1_Alpha", "3_Footwear"] if fam[:1] == ["footwear"] else ["1_Alpha", "1_Prime"]
    if stage == "poses":
        if not fam:
            return ["1_Alpha"]
        return ["2_Studies", "body"] if fam == ["views"] else ["3_Layers", *fam]
    if stage in ("head", "hair"):
        return ["2_Studies", stage, *fam]
    if stage in ("clothing", "armor", "showcase"):
        return ["4_Wardrobe", stage, *fam]
    if stage == "scene":
        return ["5_Scenes", *fam]
    if stage in ("polish", "final"):
        return ["6_Finish", stage]
    if stage == "video":
        return ["7_Video", *fam]
    if stage == "motion":
        return ["Bench", "motion", *fam]
    return None


def dirs_for(stage_folder_name, fam):
    """Folders below the hero for a prompt stage folder and its family: the pipeline phase path, or <stage>/<family> outside the hero chain."""
    phased = phase_path(stage_folder_name, fam)
    return phased if phased is not None else [stage_folder_name, *fam]


def parse_dirs(dirs):
    """Inverse of dirs_for: (prompt stage folder, family) from the folders below the hero."""
    d = list(dirs)
    if not d:
        return "", []
    p, rest = d[0], d[1:]
    if p == "1_Alpha":
        if not rest:
            return "poses", []
        sub, tail = rest[0], rest[1:]
        if sub == "1_Prime":
            return "alpha", []
        if sub == "2_Bare":
            return "alpha", ["bare"]
        if sub == "2b_Experiments":
            return "alpha", ["bare", *tail]
        if sub == "3_Footwear":
            return "alpha", ["footwear"]
    elif p == "2_Studies" and rest:
        if rest[0] == "body":
            return "poses", ["views"]
        if rest[0] in ("head", "hair"):
            return rest[0], rest[1:]
    elif p == "3_Layers":
        return "poses", rest
    elif p == "4_Wardrobe" and rest:
        return rest[0], rest[1:]
    elif p == "5_Scenes":
        return "scene", rest
    elif p == "6_Finish" and rest:
        return rest[0], rest[1:]
    elif p == "7_Video":
        return "video", rest
    elif p == "Bench" and rest[:1] == ["motion"]:
        return "motion", rest[1:]
    return p, rest


def output_for(card, group, hero, stem, root=None):
    return "/".join(["prompts", group, hero, *dirs_for(stage_folder(card["stage"]), family(card, group, root) or []), stem + ".txt"])


def card_dirs(card, group, root=None):
    """Folders below <slug>/ for a card file: the same as its prompt's folders below <Hero>/. Hair and motion cards keep the family their output names."""
    fam = family(card, group, root)
    if fam is None:
        return list(pathlib.PurePosixPath(card["output"]).parts[3:-1])
    return dirs_for(stage_folder(card["stage"]), fam)


def video_family(source_output):
    """Video prompts mirror the family of the picture they animate (the golden pose becomes 'poses')."""
    parts = pathlib.PurePosixPath(source_output).parts  # prompts/<group>/<Hero>/<phase folders...>/<file>
    stage, fam = parse_dirs(parts[3:-1])
    return fam or [stage]
