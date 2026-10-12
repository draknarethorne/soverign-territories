# Prompt templates

The text templates the prompt generator (`tools/generators/gen_prompt.py`) fills from the art data. Generated prompts go to `prompts/` and are never edited by hand.

## Layout

| Folder | What it is for | Used by |
| --- | --- | --- |
| `heroes/` | The hero pipeline: photo to Prime to Bare to studies, wardrobe, scenes and the finish. Only the heroes (angels, sisters, bound heroes) get this level of care. Split by the stage folders the art sets use, see below | `data/art/_sets/**`, `heroes/**` |
| `cards/` | `card-art.txt`: the direct template for the lower-tier cards (one step from a card's art data to an image, no Prime/Bare chain) | `data/art/cards/**` |
| `dragons/` | The Elder Dragons: pose, head and lair | dragon companions |
| `brand/` | Logos, title lock-up, key art, element icons | brand art |
| `_hero-template.txt` | The skeleton a new hero template starts from | by hand |

A template that serves every stage (a general one) belongs at the top of its kind's folder; a special-purpose one belongs in the stage or purpose folder that uses it. File names are unique across `heroes/` (the generator looks up its per-template defaults by file name), and scripts find a template by name with `tools/generators/template_paths.py` (`template_path("bare-human.txt")`), so one can move between folders without touching them.

## `heroes/` by stage

The folders carry the numbers of the stage folders in `data/art/_sets/<group>/<hero>/`, so a template sits next to the art that uses it.

| Folder | Templates | Art stage |
| --- | --- | --- |
| `1_Alpha/` | `pose-female-human`, `pose-male-human` (the Prime: photo to clean head-to-toe A-pose), `bare-human`, `bare-male-human` (the Bare: set the build, bare skin), `firered-prime-face-lock` (not a template: a paragraph put in front of the FireRed Prime prompt, see `docs/art/prime-flows.md`) | `1_Alpha` (Prime, Bare, Barefoot, Heels); also `3_Layers`, which re-uses the pose templates for the underlayers |
| `1_Alpha/experiments/` | `base-bare-human` (P3: the bare figure straight from the photo), `base-neutral-human` (P2: a skin-tone base layer from the photo). Same labeled lines as the pose templates; the wearing comes from the `bare_base` / `base_layer` slots | `1_Alpha/1b_Experiments/<bare-base or neutral-base>`; see `docs/plans/2026-10-11-first-shot-flows.md` |
| `2_Studies/` | `hair-human`, `head-human` (close-up), `pose-view-human` (3/4, profile, back views) | `2_Studies` |
| `4_Wardrobe/` | `clothing-human`, `armor-human`, `showcase-human`, `showcase-photo-human` | `4_Wardrobe` |
| `5_Scenes/` | `scene-with-outfit`, `scene-with-companion`, `scene-glamour`, `scene-staged`, `scene-combat`, `scene-minimal` (all `-human`) | `5_Scenes` |
| `6_Finish/` | `polish-human` (light detail pass), `final-human` (the terminal look on a polished image) | `6_Finish` |
| `Bench/` | `motion-human` (hair in motion, poses) | `Bench` |

The first section of every template (above `prompt:`) says what image comes in and the denoise range; the denoise rule reads it from there.

Wording rule for the positive prompt: say what the picture shows, not what it lacks. A negation there ("no straps", "without changing it") can put the named thing into the picture, and FireRed has no separate negative prompt at all. What to avoid goes in the negative prompt, or comes from a piece's `negatives`. Static text lives in the template; anything that may differ per hero is a `{{TAG}}` filled from the art data, even when every hero has the same value today.

## When you add a template

1. Put it in the stage folder of the art that uses it (or the next `heroes/` sub-folder for a new purpose, such as a prototype), with a unique file name.
2. Add its default Critical-details keys in `gen_prompt.py` (`TEMPLATE_KEY_DEFAULTS`) if it runs at a high denoise.
3. Point art cards at it through `template_path` (scaffolds) or the path (by hand), regenerate with `bin\prompts.cmd`, and check `git status prompts/`.
