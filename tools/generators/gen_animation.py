#!/usr/bin/env python3
"""Generate video (animation) prompts from data/animation/_sets/**/*.json cards.

A card animates one finished image. It names the hero, the source (an art card we generated, so the intro can be
summarised from what we asked for, or a plain description for any outside image), a look, a timeline of reusable
motion pieces and/or literal beats, camera and audio. Output is a prompt file under prompts/<group>/<Hero>/video/
that tools/workflows/comfy_workflows.py turns into a MiniMax workflow.

    python tools/generators/gen_animation.py                  # every card
    python tools/generators/gen_animation.py <card.json> ...  # specific cards
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "generators"))
import gen_prompt  # noqa: E402

CARDS = ROOT / "data" / "animation" / "_sets"
DEFAULT_CAMERA = "data/animation/cameras/follow-pan.json"
DEFAULT_WORLD = ("Everything in the scene is alive, not only her: whatever is in the setting moves naturally - flames, candles, smoke, mist, "
                 "water, foliage, banners, birds and creatures - while cloth and hair respond to the air.")
DEFAULT_CONSTRAINTS = ("Keep her face, hair, outfit, body proportions and the setting exactly as in the first frame; "
                       "no new people, no cuts, smooth natural motion, no text, no subtitles, no logos.")
PRONOUNS = {
    "female": {"she": "she", "She": "She", "her": "her", "Her": "Her", "him": "her", "herself": "herself"},
    "male": {"she": "he", "She": "He", "her": "his", "Her": "His", "him": "him", "herself": "himself"},
}


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def clip(text, limit):
    """Shorten to at most `limit` characters at a clause boundary (never mid-word), so the intro stays a summary."""
    text = text.strip().rstrip(".")
    if len(text) <= limit:
        return text
    cut = max(text.rfind(", ", 0, limit), text.rfind("; ", 0, limit), text.rfind(" - ", 0, limit), text.rfind(": ", 0, limit))
    if cut < 15:
        cut = text.rfind(" ", 0, limit)
    return text[:cut].rstrip(" ,;:-")


def fill(text, toks):
    for key, val in toks.items():
        text = text.replace("{{" + key + "}}", val)
    return text


def seconds_label(n):
    return f"{n:g}s"


def hero_tokens(card):
    hero = gen_prompt.load_identity(card["heroArt"])
    toks = gen_prompt.tokens_for(hero)
    sex = "female" if "bust" in hero["art"]["physique"] else "male"
    art = card.get("source", {}).get("artCard")
    art_toks = gen_prompt.generate(art, tokens_only=True) if art else {}
    toks = {**toks, **PRONOUNS[sex]}
    return toks, art_toks


def subject(card, toks, art_toks):
    """The short intro: what the first frame shows. From the art card when we have it, else the card's own description."""
    src = card.get("source", {})
    if card.get("subject"):
        return "Scene: " + fill(card["subject"], toks)
    if src.get("describe"):
        return "Scene: The first frame shows " + fill(src["describe"], toks).rstrip(".") + "."
    parts = [f"The first frame shows {toks['HERO']}"]
    worn = art_toks.get("WEARING") or art_toks.get("UNDERLAYER")
    if worn:
        parts.append("wearing " + clip(worn, 110))
    where = art_toks.get("BACKGROUND")
    sentence = ", ".join(parts)
    if where:
        sentence += ", in " + clip(where, 130)
    if art_toks.get("COMPANION"):
        sentence += "; " + clip(art_toks["COMPANION"], 110)
    return "Scene: " + sentence + "."


def lower_first(text):
    return text[:1].lower() + text[1:]


def transition(spec):
    """A named transition (data/animation/transitions/<name>.json) or a literal lead-in sentence."""
    if re.fullmatch(r"[a-z-]+", spec):
        return load(f"data/animation/transitions/{spec}.json")
    return {"lead": spec if spec.endswith(" ") else spec + " ", "label": ""}


def parse(item, card, toks):
    """One action -> (kind, beat, seconds, audio list). An action is a motion piece, a scene piece or literal text."""
    default = card.get("defaultSeconds", 2)
    if isinstance(item, str):
        return "Motion", fill(item, toks), default, []
    kind = "Scene" if "scene" in item else "Motion"
    ref = item.get("motion") or item.get("scene")
    if ref and ref.endswith(".json"):
        piece = load(ref)
        beat, secs, audio = piece["beat"], piece["seconds"], [piece["audio"]] if piece.get("audio") else []
    else:
        beat, secs, audio = ref or item["beat"], default, []
    beat = fill(beat, toks)
    for other in item.get("with", []):  # actions that happen together in the same moment
        _, ob, _, oa = parse(other, card, toks)
        beat = beat.rstrip(".") + "; at the same time, " + lower_first(ob)
        audio += oa
    return kind, beat, item.get("seconds", item.get("duration", secs)), audio


def timeline(card, toks):
    """[start-end] Motion:/Scene: blocks, each joined to the one before by its transition (default: the card's, else 'flow')."""
    t, lines, audio = 0.0, [], []
    for i, item in enumerate(card["actions"]):
        kind, beat, secs, a = parse(item, card, toks)
        audio += a
        label = kind + ":"
        if i:
            spec = (item.get("transition") if isinstance(item, dict) else None) or ("cut" if kind == "Scene" else card.get("transition", "flow"))
            tr = transition(spec)
            label = kind + tr.get("label", "") + ":"
            if tr["lead"]:
                beat = tr["lead"] + lower_first(beat)
        lines.append(f"[{seconds_label(t)}-{seconds_label(t + secs)}] {label} {beat}")
        t += secs
    return "\n".join(lines), t, audio


def output_path(card, toks):
    """prompts/<group>/<Hero>/video/<Hero>_Video_<source stem>_<Name>.txt, so the video is named after the scene it animates."""
    if card.get("output"):
        return card["output"]
    hero = toks["HERO"].split()[0]
    group = pathlib.PurePosixPath(card["heroArt"]).parts[3]
    art = card.get("source", {}).get("artCard")
    source = ""
    if art:
        stem = pathlib.PurePosixPath(load(art)["output"]).stem
        source = stem[len(hero) + 1:] + "_" if stem.startswith(hero + "_") else stem + "_"
    return f"prompts/{group}/{hero}/video/{hero}_Video_{source}{card['name']}.txt"


def camera_text(card, toks):
    """A camera piece (data/animation/cameras/*.json) or literal text; every video moves the camera unless a card says static."""
    spec = card.get("camera", DEFAULT_CAMERA)
    return fill(load(spec)["description"] if spec.endswith(".json") else spec, toks)


def world_text(card, toks, art_toks):
    if "world" in card:
        return fill(card["world"], toks)
    extra = " Her companion in the background moves too: it banks, beats its wings and turns its head." if art_toks.get("COMPANION") else ""
    return DEFAULT_WORLD + extra


def generate(card_path):
    card = load(card_path)
    toks, art_toks = hero_tokens(card)
    card["output"] = output_path(card, toks)
    look = load(card["look"])
    tl, total, motion_audio = timeline(card, toks)
    width, height = card.get("size", [640, 960])
    values = {
        "HERO": toks["HERO"], "NAME": card["name"],
        "SOURCE_IMAGE": card.get("source", {}).get("image", "(choose the image to animate)"),
        "WIDTH": str(width), "HEIGHT": str(height), "SECONDS": f"{total:g}",
        "LOOK": fill(look["description"], toks), "SUBJECT": subject(card, toks, art_toks), "TIMELINE": tl,
        "CAMERA": camera_text(card, toks), "WORLD": world_text(card, toks, art_toks),
        "AUDIO": card.get("audio") or "; ".join(motion_audio) or "soft ambient score, no speech",
        "CONSTRAINTS": fill(card.get("constraints", DEFAULT_CONSTRAINTS), toks),
        "NEGATIVE": ", ".join(look.get("negatives", [])),
    }
    out = (ROOT / card["template"]).read_text(encoding="utf-8")
    for key, val in values.items():
        out = out.replace("{{" + key + "}}", val)
    left = re.findall(r"{{\w+}}", out)
    if left:
        sys.exit(f"ERROR {card_path}: unresolved tokens {left}")
    dst = ROOT / card["output"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(f"wrote {card['output']}  ({total:g}s)")
    return card["output"]


def main(argv):
    paths = argv or [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted(CARDS.glob("**/*.json"))]
    for p in paths:
        generate(p)


if __name__ == "__main__":
    main(sys.argv[1:])
