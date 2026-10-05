# Tutorial: creating video JSON (by hand or with AI)

How to turn a finished image into a short animated clip (a reel or teaser) with the same data-driven approach as the art. It
assumes you have read [tutorial-art.md](tutorial-art.md) or at least know that prompts are generated from small JSON files.

> The pipeline is built and the example workflows deploy cleanly, but the first renders are still to come. Treat the settings
> below as a starting point and expect to tune them.

## The model in one minute

```text
finished image (art card or any picture) + a list of actions --(animation card)--> video prompt .txt --> MiniMax workflow --> clip
                                                                 gen_animation.py                      comfy_workflows.py
```

You write a card that lists what should happen, in order. The generator turns each action into its own timed block, joins them
with transitions, adds a short summary of the image so the model knows what it is looking at, and writes a prompt. The workflow
tool puts that prompt (and the size and length) into the `ST6_MiniMax_Video` template.

| File | Where | What it is |
| --- | --- | --- |
| Card | `data/animation/_sets/<group>/<slug>/*.json` | One animation: source, look, actions |
| Motion | `data/animation/motions/<family>/*.json` | A reusable action (blow a kiss, eyes glow) |
| Transition | `data/animation/transitions/*.json` | How one action hands off to the next |
| Look | `data/animation/looks/*.json` | The film style line (photoreal, card art) |
| Camera | `data/animation/cameras/*.json` | How the camera moves (follow pan, orbit, push in, rise, static) |
| Template | `data/animation/_templates/video-minimax.txt` | The prompt layout the video model expects |

## The loop

```bash
python tools/generators/gen_animation.py                                            # cards -> prompts/<group>/<Hero>/video/
python tools/workflows/comfy_workflows.py make --engine minimax --create --hero Drakness   # prompts -> workflows (tracked in git)
python tools/workflows/comfy_workflows.py deploy --engine minimax --hero Drakness          # workflows -> ComfyUI dev
```

`bin\animate.cmd Drakness` does all three. In ComfyUI: open the workflow, check the image in the loader (it must exist in the
shared `input` folder, so copy the render there from `output` if needed), and run it.

## What the prompt looks like

The video model reads a structured prompt: a look line, a scene summary, a timestamped timeline, camera, audio and constraints.
The generator writes exactly that:

```text
Live-action cinematic fantasy film footage: photorealistic skin ...

Scene: The first frame shows Drakness Thorne, in an elegant gothic stone balcony ...

Timeline:
[0s-2s] Motion: Her eyes ignite with a steady amethyst glow ...
[2s-5s] Motion: Without pausing, she raises one hand, palm up ...
[5s-7s] Motion: Blending seamlessly out of the previous action, the amethyst smoke and radiant light swirl into ...

World: Everything in the scene is alive, not only her: whatever is in the setting moves naturally ...

The camera glides in a slow arc from left to right, following her movement and keeping her full figure in frame ...

Audio: a low, rising shimmer ...

Keep her face, hair, outfit, body proportions and the setting exactly as in the first frame; no new people, no cuts ...
```

## Recipe 1: add a motion piece

A motion is one reusable action. Real example, `data/animation/motions/magic/eyes-glow.json`:

```json
{
  "id": "motions/magic/eyes-glow",
  "kind": "motion",
  "name": "Eyes ignite",
  "seconds": 2,
  "beat": "{{Her}} eyes ignite with a steady {{MAGIC}} glow, the light brightening from the irises outward while {{she}} holds the camera's gaze.",
  "audio": "a low, rising shimmer",
  "tags": ["magic", "eyes"]
}
```

- **`beat`** is the action as one or two sentences: what starts, what changes, where it ends.
- **Tokens:** hero colours (`{{MAGIC}}`, `{{PRIMARY}}`, `{{METAL}}`) and pronouns (`{{she}}`, `{{She}}`, `{{her}}`, `{{Her}}`,
  `{{him}}`, `{{herself}}`) so the same motion works for any hero, female or male.
- **`seconds`** is its natural length; a card can override it per use.
- **`audio`** is optional and is joined into the card's audio line.
- Folders are families: `magic/`, `romantic/`, `candid/`. Add your own.

Good beats do one thing, say where it ends (so the next action can start from there), and avoid camera changes (the card owns
the camera).

## Recipe 2: add a card for art we made

Real example, `drakness-anim-staged-enchanted-evening-awakening.json` (shortened). It takes the plain Enchanted Evening render
and adds the magic the still left out:

```json
{
  "animId": "drakness-anim-staged-enchanted-evening-awakening",
  "kind": "animation",
  "name": "Awakening",
  "heroArt": "data/art/heroes/drakn-sisters/drakness-thorne.json",
  "source": {
    "artCard": "data/art/_sets/drakn-sisters/drakness/scene/drakness-scene-staged-enchanted-evening.json",
    "image": "Drakness_FireRed_Scene_Staged_EnchantedEvening_00001_.png"
  },
  "look": "data/animation/looks/cinematic-photoreal.json",
  "audio": "a low, rising shimmer, a soft swell of energy, then a gentle chime; no speech",
  "size": [640, 960],
  "template": "data/animation/_templates/video-minimax.txt",
  "actions": [
    { "motion": "data/animation/motions/magic/eyes-glow.json" },
    { "motion": "data/animation/motions/magic/raise-hand-cast.json", "transition": "flow" },
    { "beat": "The {{MAGIC}} smoke and radiant light swirl into a ring of glowing spectral moths circling {{her}} raised hand.",
      "seconds": 2, "transition": "blend" },
    { "motion": "data/animation/motions/magic/ambient-awaken.json", "seconds": 1, "transition": "settle" }
  ]
}
```

- **`source.artCard`** points at the art card the image came from. The generator reads it and writes the short "Scene:"
  summary (outfit, setting, companion) from what we asked for, so you never retype it. **`source.image`** is only the file the
  workflow opens first.
- **`name`** is CamelCase and ends up in file names. The output is named after the scene it animates, automatically:
  `Drakness_Video_Scene_Staged_EnchantedEvening_Awakening`. (You can still set `output` by hand to override.)
- **`animId`** equals the file name; the validator checks it.
- **`camera`** is optional: a camera piece (`"data/animation/cameras/orbit-reveal.json"`) or your own sentence. The default is a slow
  follow pan so the whole scene stays active; use `cameras/static.json` only when you want it locked off.
- **`world`** is optional text for the "World:" line, which tells the model the whole scene moves, not just her. The default covers
  flames, candles, smoke, water, foliage and creatures, and adds a moving companion when the art has one. For a plain studio
  image set `world` yourself (the studio examples do).

### The actions list

Each entry in `actions` can be any of these, in any mix:

| Form | Example | Notes |
| --- | --- | --- |
| Reusable motion | `{ "motion": "data/animation/motions/..." }` | Uses the motion's `seconds` unless you set `seconds` |
| Typed action | `"She gives the camera a playful wink."` | A plain string; lasts `defaultSeconds` (2) |
| Literal beat | `{ "beat": "...", "seconds": 3 }` | Typed text with its own length |
| Scene change | `{ "scene": "<piece path or literal text>" }` | Labelled `Scene:` and joined by a hard cut by default |
| Together | `{ "motion": "...laugh.json", "with": [ { "motion": "...eyes-glow.json" } ] }` | Things that happen in the same moment: "...; at the same time, her eyes ignite" |

Each becomes its own `[start-end] Motion:` or `Scene:` line, with times added up for you.

### Transitions, so the clip does not skip

Each action after the first starts with a lead-in that tells the model to continue from where the last one ended. Set a
card-wide default with `"transition": "flow"` and override any single action.

| Name | Reads as | Use it when |
| --- | --- | --- |
| `flow` (default) | "Without pausing, ..." | One action runs straight into the next |
| `blend` | "Blending seamlessly out of the previous action, ..." | A softer, slower hand-off |
| `settle` | "As the previous motion settles, ..." | The last action should finish and rest first |
| `hold` | "After a brief held beat, ..." | A short pause on the final pose |
| `cut` | the line is marked `(hard cut)` | A deliberate new moment or setting |

You can also type your own: `"transition": "As her laugh fades, "`. If a join still looks like a jump, change that one
transition, or lengthen the action before it. To change what a named transition says, edit its file in
`data/animation/transitions/`.

## Recipe 3: animate an image we did not generate

When there is no art card (a photo, an image from elsewhere), describe the first frame yourself:

```json
{
  "animId": "drakness-anim-rooftop-wave",
  "kind": "animation",
  "name": "RooftopWave",
  "heroArt": "data/art/heroes/drakn-sisters/drakness-thorne.json",
  "source": { "describe": "{{HERO}} on a rooftop at sunset in a long black coat, hair blowing in the wind", "image": "rooftop_photo.png" },
  "look": "data/animation/looks/cinematic-photoreal.json",
  "size": [640, 960],
  "template": "data/animation/_templates/video-minimax.txt",
  "actions": [ "{{She}} turns toward the camera and lifts a hand in a slow wave.", { "motion": "data/animation/motions/candid/hair-toss.json" } ]
}
```

`describe` becomes the "Scene:" line; use `subject` instead if you want to write the whole sentence yourself. A card always
needs a `heroArt`, which supplies pronouns and colour tokens and decides where the files are filed, so pick the closest hero.
Keep the description short: the video model sees the image, so you are only orienting it.

## Size, length and what this machine can do

- Cards default to **640×960 portrait** (2:3, the shape of our art) and the workflow runs in **turbo** (8-step LoRA), which is what
  this machine can manage. The examples run 7 to 9 seconds. Length is the sum of the actions; change it by adding or
  trimming actions, or by editing the length value in the workflow.
- Size and length are applied when a workflow is **created**. Changing them in a card later does not rewrite a workflow you
  already have; delete it (or `fork` it) and run `make --create` again.
- The model also makes audio. Use the `audio` line (or the motions' audio) to say what you want, and `no speech` if you do not.

## Hand tuning without losing it

- To tweak one clip freely in ComfyUI, run `bin\fork.cmd WORKFLOW Tag` (or `comfy_workflows.py fork NAME --as Tag`), edit it in
  ComfyUI, save, then `bin\pull-dev.cmd HERO` to keep your changes. It lives in `workflows/_curated/` and is never regenerated.
- If you keep making the same tweak, that is a motion, transition or look waiting to be written. Add it, regenerate, and retire
  the curated copy.

## Working with an AI assistant

```text
You are helping with the Sovereign Territories video pipeline. Read docs/art/tutorial-video.md and the files in data/animation first.
Rules: never edit prompts/ (generated). Reuse motions and transitions from data/animation where one fits; write a new motion piece
only for an action we will reuse. Beats are one or two sentences, state where the action ends, and never change the camera.
Use {{MAGIC}}-style tokens and {{she}}/{{her}} pronoun tokens, not names or fixed colours. Copy the shape of an existing card.
Task: <e.g. "animate Draknora's Signature scene: she raises the sword, the flame wraps the blade, she looks to camera and smiles; 8 seconds">.
Then run python tools/validators/validate_data.py and python tools/generators/gen_animation.py and show me the generated prompt.
```

Check the generated timeline reads in the order you want, that each action ends where the next begins, and that the intro line matches the image.

## Troubleshooting

| Symptom | Try |
| --- | --- |
| Motion jumps between actions | `blend` or `settle` on that join, a `hold`, or a longer action before it |
| Face or outfit drifts | Shorter clip, fewer simultaneous actions, keep the constraints line, a source image with a clear face |
| Magic looks flat | A stronger beat ("glowing runes, arcs of light"), or use the `card-art` look instead of `cinematic-photoreal` |
| It ignores part of the timeline | Too much for the length: fewer actions or more seconds |
| Wrong file name | Names come from the source art card and the card's `name`; fix those |

## Checklist before you commit

- [ ] `python tools/validators/validate_data.py` passes (it checks every file the card names and every transition).
- [ ] `python tools/generators/gen_animation.py` ran and you read the generated prompt.
- [ ] `source.image` exists in the ComfyUI `input` folder.
- [ ] Workflows rebuilt with `make --engine minimax --create` (or `bin\animate.cmd`), then committed; they are tracked in git.
