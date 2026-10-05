"""Where an art card lives and where its image ends up: one rule, shared by the generators and the validator.

Every card is filed under a FAMILY below its stage, and the prompt (hence the ComfyUI output folder) mirrors it:

  data/art/_sets/<group>/<slug>/<stage>/<family...>/<artId>.json
  prompts/<group>/<Hero>/<stage folder>/<family...>/<Hero>_<Stage>_<Name>.txt
  ComfyUI output: <group>/<Hero>/<stage folder>/<family...>/<Hero>_<Engine>_<Stage>_<Name>_00001_.png

The family comes from the card, never from a hand-typed folder, so a new card cannot end up in the wrong place.
Hair and motion cards already carry their own family folders and are left as they are.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

THEMES = {"celtic", "danish", "egyptian", "greek", "norse", "roman", "thanksgiving"}
LAYOUT_STAGES = {"scene", "pose", "head", "clothing", "armor", "showcase"}
STAGE_FOLDER = {"pose": "poses"}
# Sister scenes are grouped into a few broad buckets. A folder only exists to hold closely related cards: a shiny or
# holo edition sits beside its signature card, and one-card groups stay flat in the stage folder.
SCENE_BUCKETS = {
    "signature": ["signature", "lineup"],
    "glamour": ["glamour", "glamour-test", "elegant-casting", "robe"],
    "story": ["the-dawn", "battle", "bond"],
}


def scene_family(art_id, group):
    rest = art_id.split("-scene-", 1)[1] if "-scene-" in art_id else art_id
    if group != "drakn-sisters":
        return ["modern"] if rest.startswith("modern-") else []
    if rest in THEMES:
        return ["themes"]
    if rest.startswith("signature-"):
        return ["signature"]
    if "enchanted-evening" in rest:
        return ["glamour"]
    for bucket, names in SCENE_BUCKETS.items():
        if rest in names:
            return [bucket]
    return []


def wearing_family(card):
    """Library clothing groups by its family (dresses, gowns, sets) and library armor shares one folder; signature items stay flat."""
    wear = card.get("components", {}).get("wearing", "")
    parts = wear.split("/")
    if not (wear.startswith("data/art/wardrobe/") and len(parts) >= 6):
        return []
    return ["wardrobe"] if card["stage"] == "armor" else [parts[4]]


# A-pose underlayer tests group by what the piece is (its tags, first match wins).
UNDERLAYER_FAMILIES = [
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
    if stage == "pose":
        if "view" in comps:
            return ["views"]
        return underlayer_family(card, root or ROOT) if "underlayer" in comps and not art_id.endswith("-x-pose") else []
    if stage == "head":
        return [] if art_id.endswith("-x-head") else ["views"] if "view" in comps else ["closeups"]
    if stage in ("clothing", "armor"):
        return wearing_family(card)
    return []


def stage_folder(stage):
    return STAGE_FOLDER.get(stage, stage)


def output_for(card, group, hero, stem, root=None):
    return "/".join(["prompts", group, hero, stage_folder(card["stage"]), *(family(card, group, root) or []), stem + ".txt"])


def video_family(source_output):
    """Video prompts mirror the family of the picture they animate (the golden pose becomes 'poses')."""
    parts = pathlib.PurePosixPath(source_output).parts  # prompts/<group>/<Hero>/<folder>/<family...>/<file>
    fam = list(parts[4:-1])
    return fam or [parts[3]]
