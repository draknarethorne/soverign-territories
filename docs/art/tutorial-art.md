# Tutorial: creating art JSON (by hand or with AI)

This is the practical guide for adding to the art pipeline: a new outfit, background or weapon, a new scene, an A-pose
test, or a new hero. It assumes nothing. The reference for *why* the folders are laid out as they are is
[data/art/README.md](../../data/art/README.md); this page is the *how*. For animation see
[tutorial-video.md](tutorial-video.md).

## The model in one minute

You never write a prompt. You write small JSON files that the generator turns into prompts.

| Kind of file | Where | What it is | Example |
| --- | --- | --- | --- |
| Identity | `data/art/heroes/<group>/<slug>-thorne.json` | Who she is: colours, eyes, skin, build | `draknisa-thorne.json` |
| Piece | `data/art/wardrobe`, `cosmetics`, `themes`, `races`, `backgrounds`, `heroes/.../<slug>/` | One reusable chunk of description | a bikini, a gown, a throne room |
| Card | `data/art/_sets/<group>/<slug>/<stage>/<family>/` | A recipe: which pieces to use, in which template | `draknisa-scene-robe.json` |
| Template | `data/art/_templates/heroes/*.txt` | Static prompt scaffolding with `{{TOKENS}}` | `scene-with-outfit-human.txt` |

```text
piece + piece + identity --(card + template)--> prompt .txt --> workflow .json --> ComfyUI --> image
                           gen_prompt.py          comfy_workflows.py
```

Files under `prompts/` are generated: never edit them. Fix the piece, card or identity and regenerate.

## The image chain: from bare skin to scene

What the incoming image wears shows through into every later image. A low-cut dress over a bikini A-pose is not low cut, and
celestial armor over a swimsuit keeps the straps. So the chain is built from the bottom up, and each stage picks its incoming image
on purpose. Prompts only describe what to *add* or *change*; the incoming image supplies the rest.

The original photos are varied shots (different framing, clothing, pose) and are not good enough to feed straight into the later stages.
The very first step is therefore always the **standard X Pose** workflow: it takes an original photo and builds the one clean, full-length A-pose
in her metallic bikini (barefoot), and it is also where the bust and the pose are brought into proper shape. Everything else starts from that
image. You can intercept the X Pose workflow and use your own forceful wording to get the A-pose you want (keep that workflow as a shot).

| Stage | Folder | Incoming image | Produces |
| --- | --- | --- | --- |
| 1. Standard X Pose | `poses/` | an original photo (any shot you like) | the golden A-pose: full length, metallic bikini, barefoot, bust and proportions set; the base for everything |
| 2. Bare | `bare/` | the golden A-pose from stage 1 | the body with the bikini removed, in one of several looks (below) |
| 3. Other poses | `motion/`, `poses/` and any workflow that takes an incoming A-pose | the bare image from stage 2, with the body contour line on | poses that keep her real form and do not carry the bikini |
| 4. Outfit, armor, showcase | `clothing/`, `armor/`, `showcase/` | the bare image, or a pose from stage 3 | her in the outfit, armor or a styled shot |
| 5. Scene | `scenes/` | a complete image from stage 4, or an A-pose | the final scene |

The bikini A-pose from stage 1 stays useful as an input on its own: feed it (or any A-pose in a bikini, lingerie or a bodysuit) when you want that
layer to show under the outfit on purpose. The underlayer A-pose cards (`poses/<family>/`) are built from the original photo like stage 1 and
are for choosing which bikini or lingerie reads best.

**Choose the incoming image for the effect you want:**

| Incoming image | Result |
| --- | --- |
| Bare (`Bare_SkinStudy`, `Bare_ChestStudy`) | cleanest outfits: nothing underneath bleeds through, and low-cut or sheer pieces are really low cut or sheer |
| Bikini, lingerie or bodysuit A-pose | that layer shows under the outfit on purpose |
| Celestial (`Bare_CelestialCore`, `Bare_CelestialSuit`, `Bare_CelestialPlate`, `Bare_CelestialPlateFitted`) | her celestial form carries into the scene or the next outfit |
| Pasties, contoured or paint (`Bare_Pasties`, `Bare_Contoured`, `Bare_Paint`) | minimal coverage; check for bleed, and add the `remove-coverings` strip line on the next card if it shows |

**The bare looks** (all edit-only prompts in `data/art/_templates/heroes/bare-human.txt`, one short removal instruction plus a result paragraph
with each area on its own semicolon-separated clause, and "change nothing else"):
`Bare_Pasties`, `Bare_Contoured` (sheer, nylon-like), `Bare_Paint` and `Bare_PaintColour` (small painted areas), `Bare_SkinStudy` and
`Bare_ChestStudy` (figure-study wording, model-chosen rendering), and the celestial ones. The celestial core paints only the three small
designs; the suit forks it into an open-filigree design over the whole body; the plate versions are the original small plates, and
`Bare_CelestialPlateFitted` shapes them to the body. Your own hand-written bare workflows are kept as shots (see below) and stay your own.

**Switches that apply to the whole chain** (`data/art/_settings/studio.json`, then regenerate):

| Switch | Effect |
| --- | --- |
| `aPoseFootwear` | `barefoot` (default): no shoes in any A-pose; each outfit adds its own. `signature`: her heels again. `x-pose-heels` cards keep the heeled pose |
| `bodyContour` | on by default (`fitted-contour`, `armor-contour` for armor): outfits follow the body in the incoming image, so her form shows through the fit. A card sets `components.body_contour` to `sheer-contour` (real body through thin fabric) or `"off"` |
| `components.strip` on a card | an optional line that removes what the incoming image wears first (`remove-original`, `replace-original`, `remove-coverings`) |

**Scenes, two ways.** A *complete* scene (`<hero>-scene-<name>`) describes the outfit and everything else, and takes an A-pose as input, so
you choose how much of the A-pose shows through. A *staged* scene (`-staged-` in the name) takes an already-dressed image from stage 4 and
only adds the scene, effects and pose, so the outfit comes from the image, not the prompt. Between the two, a *semi-staged* scene is a
complete scene fed an A-pose that already wears a chosen layer (bikini, lingerie, celestial): the scene describes the pieces to add and the
A-pose supplies the layer under them. Fully pre-staged scenes (a finished bone-armor image forced into the scene) come later, if at all.

**Render and keep.** Qwen is the default engine; FireRed (local, not in git) is the photoreal comparison and takes the positive prompt only, so the
negatives in a card do not apply to it. Run the A-pose and bare stages in non-Turbo mode overnight when you want the most realistic base, since
everything after them inherits it. Save a workflow you tuned for one render (seed, Turbo or not) in the workspace under `zz_Shots/` and run
`pull --shots`; see [workflows/README.md](../../workflows/README.md#shots-zz_shots). Cards, pieces and templates are the permanent record; shots
are the tuned renders.

## The loop you will run every time

```bash
python tools/validators/validate_data.py            # 1. is the data valid? (or bin\validate.cmd)
python tools/generators/gen_prompt.py               # 2. cards -> prompts   (or bin\prompts.cmd)
python tools/workflows/comfy_workflows.py make --create --hero Draknisa --stage scene   # 3. prompts -> workflows
python tools/workflows/comfy_workflows.py deploy --hero Draknisa --stage scene          # 4. workflows -> ComfyUI dev
```

`bin\refresh-dev.cmd Draknisa scene` runs steps 2 to 4. Then open the workflow in ComfyUI, pick the A-pose input
image, render, and review against [output-qa-checklist.md](output-qa-checklist.md).

## Recipe 1: add a piece

A piece is a tiny JSON file. Decide where it lives with one question: how widely can it be reused?

| Scope | Folder | Use it for |
| --- | --- | --- |
| Core | `wardrobe/<kind>/<family>/`, `cosmetics/`, `backgrounds/<realm>/<family>/` | Anything any hero could wear or stand in |
| Theme | `themes/<theme>/...` | A culture or event pack (Greek, Thanksgiving) |
| Race | `races/<race>/...` | Things that exist because of anatomy (hair texture, ears) |
| Hero | `heroes/<group>/<slug>/<kind>/` | One named hero's signature item |

When unsure, start in the narrowest scope and promote it the second time it is reused.

Real example, `data/art/wardrobe/swimwear/lingerie/lace-bralette-set.json`:

```json
{
  "id": "wardrobe/swimwear/lingerie/lace-bralette-set",
  "kind": "wearing",
  "name": "Lace Lingerie Set",
  "description": "only a {{PRIMARY}} lace lingerie set in fine floral lace with scalloped edges and a hairline {{METAL}} thread edging: a plunging balconette bra ... matching {{PRIMARY}} open-toed high heels with {{METAL}} accents",
  "compatibleStages": ["pose"],
  "tags": ["lingerie", "lace", "female"],
  "notes": "Cut and fabric test: floral lace in the signature colour."
}
```

Rules that trip people up:

- **`id` equals the path** under `wardrobe/`, `cosmetics/` and `themes/` (without `data/art/` and `.json`). Hero pieces use
  `heroes/<group>/<slug>/...`. The validator enforces it.
- **`kind` says what the piece is; the card slot it is plugged into decides where its text appears** (`wearing`, `jewelry`,
  `legs_feet`, `holding`, `effects`, `background`, `headwear`, `makeup` ...). The full table is in
  [data/art/README.md](../../data/art/README.md).
- **Write so the template sentence reads.** The scene template says `Wearing {{WEARING}}.`, so the description starts
  with "a ..." and has no leading "She wears".
- **Use tokens instead of colours.** `{{PRIMARY}}`, `{{ACCENT_SOFT}}`, `{{METAL}}`, `{{MAGIC}}`, `{{GEM}}` become each hero's own
  colours, which is what makes one piece reusable by all ten sisters. Hard-code a colour only for a deliberate one-off.
- **Describe what is there, not what is not.** Models latch onto the thing you negate ("no knots" draws knots). Put bans in
  the template's negative prompt or the card's `overrides.negativeAdd`, and describe the positive picture instead
  ("fastening hidden behind her at the back").
- **Backgrounds live under a realm folder** (`backgrounds/fantasy/...`). The folder is the realm. A hero's own scenery goes in
  `heroes/<group>/<slug>/backgrounds/fantasy/<family>/` and usually carries a `mood`.
- **`compatibleStages`** is `["pose"]` for an A-pose underlayer, `["scene"]` for scene pieces, `["clothing"]` and so on.

## Recipe 2: add a scene card

A card chooses a template and fills its slots. Real example, `draknisa-scene-robe.json` (shortened):

```json
{
  "artId": "draknisa-scene-robe",
  "kind": "base-set",
  "stage": "scene",
  "heroArt": "data/art/heroes/drakn-sisters/draknisa-thorne.json",
  "name": "Robe",
  "components": {
    "pose": "data/art/motion/romantic/hand-to-collarbone.json",
    "wearing": "data/art/heroes/drakn-sisters/draknisa/clothing/signature-robe.json",
    "headwear": "a delicate {{METAL}} tiara of pearls and shell",
    "effects": "Soft beads of water hang in the air near her ... {{MAGIC}} light rippling across the walls.",
    "background": "data/art/heroes/drakn-sisters/draknisa/backgrounds/fantasy/sanctum/enchanted-tide-pool-atrium.json",
    "holding": "data/art/heroes/drakn-sisters/draknisa/weapons/tidepearl-staff.json"
  },
  "template": "data/art/_templates/heroes/scene-with-outfit-human.txt",
  "output": "prompts/drakn-sisters/Draknisa/scene/Draknisa_Scene_Robe.txt",
  "denoise": "~0.5-0.7"
}
```

**A slot value is either a path to a piece or plain text.** If it ends in `.json` and the file exists it is a piece;
otherwise it is used as literal text. That means you can build a whole card from nothing but text, reuse proven pieces
where they exist, or mix both (as above: `wearing` is a piece, `headwear` is typed in). Prefix a literal with `+` to
extend the default instead of replacing it (`"expression": "+a faint, knowing smile."`).

**Naming is enforced** (it keeps filenames and render folders predictable):

- file name = `artId` = `<hero>-scene-<name>.json`, where `<hero>` is the first word of the folder (`draknisa`);
- `output` = `prompts/<group>/<Hero>/scene/<Hero>_Scene_<Name>.txt`, and `<Name>` is CamelCase (`TheDawn`, `Robe`);
- a **staged** scene (it edits an already finished render) adds `staged` after `scene` in the id and `_Staged_` in the output,
  and must use `scene-staged-human.txt`; every other scene is **complete** and starts from the A-pose.

Pick the template by the job:

| Template | Use it for |
| --- | --- |
| `scene-with-outfit-human.txt` | Default: A-pose in, outfit and scene out |
| `scene-with-companion-human.txt` | The same plus a bonded dragon or pet (`components.companion`) |
| `scene-glamour-human.txt` | Daily-post glamour shots, understated magic |
| `scene-combat-human.txt` | Martial heroes, no eye-glow line |
| `scene-minimal-human.txt` | Quick, simple scenes |
| `scene-staged-human.txt` | Edits a finished render; only adds atmosphere |

House rules for scenes: keep the face toward the camera on signature art, give every scene a real `effects` line, and keep
the full head-to-toe figure in frame. The scene's background folder must match its realm (canon is `fantasy`).

## Recipe 3: add an A-pose test (swap the underlayer)

An A-pose card is one line of difference from the base card. This is the whole of `drakness-x-pose-lace.json`:

```json
{
  "artId": "drakness-x-pose-lace",
  "kind": "base-set",
  "stage": "pose",
  "heroArt": "data/art/heroes/drakn-sisters/drakness-thorne.json",
  "template": "data/art/_templates/heroes/pose-female-human.txt",
  "output": "prompts/drakn-sisters/Drakness/poses/Drakness_X_Pose_Lace.txt",
  "denoise": "~1.0",
  "components": { "underlayer": "data/art/wardrobe/swimwear/lingerie/lace-bralette-set.json" }
}
```

The same trick works for hair (`overrides.palette.hairStyleComponent`), makeup (`components.makeup`) and eye glow
(`components.eye_effect`). One-off changes to a hero for a single render go in `overrides.palette` or `overrides.physique`.

**Test a whole family at once.** `scaffold_wardrobe_tests.py` writes one card per wearing piece in a folder (A-pose underlayers,
clothing or armor, chosen from each piece's `compatibleStages`) and skips pieces tagged for the other sex or already carded:

```bash
python tools/generators/scaffold_wardrobe_tests.py --group drakn-sisters --slug drakness --hero Drakness wardrobe/clothing/gowns
python tools/generators/gen_prompt.py --group drakn-sisters --slug drakness
python tools/workflows/comfy_workflows.py make --hero Drakness --stage clothing --create
```

The golden A-pose is the incoming image for scenes. The underlayer pieces are for generating alternatives to it: pick the base that
blends best (for example the second-skin bodysuit for full-coverage looks, a backless base for bare-back gowns).

## Recipe 3b: build a sister's studio kit

A kit file lists what to test for one sister, suited to her class and element (A-pose underlayers, outfits, armor, motions and
showcase shots). The scaffold writes the cards; the workflow tool then sends her studio work to her own workspace:

```bash
python tools/generators/scaffold_sister_studio.py --slug draknara
python tools/generators/gen_prompt.py --group drakn-sisters --slug draknara
python tools/workflows/comfy_workflows.py make --hero Draknara --class studio --create
python tools/workflows/comfy_workflows.py deploy --to uat --hero Draknara --class studio
```

Copy `data/art/_kits/draknara.json` for the next sister and change the pieces. A **showcase** card is a studio shot on a coloured
backdrop (`backgrounds/studio/*`) with an effects line; use it to see magic and flair before building the full scene.

## Recipe 4: add a hero

1. Add the gameplay card under `data/cards/sovereign-dawn/...` (the codex owns name, element, sex, race, class, rarity).
2. Add the identity `data/art/heroes/<group>/<slug>.json` with the same `cardId`. Colours and build live here and nowhere else.
   Every female card hero needs `lipColor`, `eyeshadowColor`, `blushColor`, `nailColor`, `lashColor`, `browColor`,
   `magicColor` and `gemColor`.
3. Set the card's `art.artIdentity` to the identity's path. The link must point both ways or the validator fails.
4. Add cards under `data/art/_sets/<group>/<slug>/` for the stages you need (pose, head, then scenes).
5. Run the loop above.

Each fact has one home: if the card owns it (name, element, sex, class), do not repeat it in the identity.

## Common validator messages

| Message | Fix |
| --- | --- |
| `... looks like a path but ... does not exist` | A typo in a piece path. Left alone it would print the path into the prompt. |
| `scene artId must look like '<hero>-scene-<name>'` | Rename the file and `artId` together. |
| `output ... must sit in the 'scene' folder` | Fix the folder in `output`. |
| `scene realm is 'fantasy' but background ... is under backgrounds/modern/` | Use a fantasy background, or set `components.realm` on purpose. |
| `... is also produced by ...` | Two cards write the same prompt file; rename one. |
| `art.artIdentity ... does not link back` | Make the card and identity point at each other. |
| `template needs tokens with no value` (generator) | A slot the template requires is missing from `components`. |

## Group shots: bringing several characters into one image

A model cannot keep ten faces if you give it ten references. The Qwen edit encoder takes at most three images, and ten
full-length figures in one frame leave each face only a few dozen pixels wide. So build the shot in layers: render each
character large, on her own, in the same light; place them onto a shared background; then let one gentle pass blend it.

```text
plate (empty ridge)  +  10 cut-outs (one per character)  -->  collage  -->  harmonise pass  -->  final
```

### Step 1: the plate

Run `SovereignTerritories_Plate_Qwen_Text` in ComfyUI (a text-to-image workflow, no input image, 1280x1600). It makes an empty
ridge in three terraces with dawn light from the right. Keep the best one. Its prompt, and the harmonise prompt below, are
stored in the workflows themselves under `workflows/_curated/key-art/SovereignTerritories/`.

### Step 2: one cut-out render per character

Each sister has a `Lineup` scene card (`<hero>-scene-lineup.json`): her dawn gown on a flat grey backdrop, lit from the right
by the same dawn light, full figure, effects kept within arm's reach so she cuts out cleanly. Refresh and run them:

```bash
bin\refresh-dev.cmd Draknora scene     # or run the whole set; the workflows are named <Hero>_Qwen_Scene_Lineup
```

Pick the best render for each. Check that the light comes from the **right** in all ten; a render lit from the left will not
match, so rerun it.

### Step 3: cut out and place

Cut each figure out of the grey. Two ways:

- **In an image editor (Krita, GIMP, Photopea):** the flat grey makes "select subject" or a colour-range selection easy. Feather the
  edge by about 1 to 2 pixels and remove any grey fringe.
- **In ComfyUI:** `Load Background Removal Model` then `Remove Background` give an image with a mask. You need to download a
  background-removal model into `models/background_removal` first (the folder is empty today). Then `ImageCompositeMasked`
  places each figure on the plate.

Work on a canvas the size of the plate (1280x1600) and place **back to front**: the single top figure first, then the middle row,
then the front row. This is the layout, in pixels, with the colours spread so no two neighbours look alike:

| Row | Who, left to right | Feet at y | Height | Centres at x |
| --- | --- | --- | --- | --- |
| Top | Drakness | 1056 | 670 | 640 |
| Middle | Draknisa, Draknara, Draknava, Drakniss | 1280 | 830 | 275, 518, 762, 1005 |
| Front | Draknora, Draknira, Drakniya, Drakneta, Draknoxa | 1552 | 990 | 154, 397, 640, 883, 1126 |

Back figures are smaller and sit higher on the terraces. Give the farther rows a little haze: slightly lower contrast and
saturation, and a soft pale-blue mist layer at 10 to 20 percent between the rows. Add a soft dark shadow under every pair of
feet. Save the flattened result as a PNG named `SovereignTerritories_Collage_00001_.png` in ComfyUI's `input` folder.

### Step 4: harmonise

Run `SovereignTerritories_Harmonize_Qwen_Edit`. It reads the collage and re-lights it at a low strength (denoise 0.4). Its prompt
says the ten women must not change, and asks for matching light, shadows, mist and softened edges. Check:

- exactly ten women, the same faces and gowns;
- the edges no longer look pasted on.

If a face drifts, lower the strength to 0.25 to 0.3. If it still looks pasted, raise it toward 0.5. The strength is the
`denoise` value on the workflow.

### Why this works, and what to expect

Every face is rendered at full size from her own A-pose, so identity is as good as a single portrait. The harmonise pass is the
only step that sees all ten at once, and at low strength it has little room to change anyone. If one face does drift, redo only
that sister's cut-out and recomposite.

This has not been run end to end yet; treat the numbers (positions, strength) as a starting point.

## Working with an AI assistant

An assistant can write all of this, provided it works from the repo and not from memory. Give it this brief and the file
paths, and check its work with the validator.

```text
You are helping with the Sovereign Territories art pipeline. Read data/art/README.md and docs/art/tutorial-art.md first.
Rules: never edit anything under prompts/ (generated). Pieces go in the narrowest sensible scope under data/art. A piece's id
equals its path. Use {{PRIMARY}}, {{ACCENT_SOFT}}, {{METAL}}, {{MAGIC}}, {{GEM}} tokens instead of hard-coded colours. Describe what
is present, never what is absent. Copy the shape of an existing file of the same kind rather than inventing fields.
Task: <what you want, e.g. "a Roman-theme scene for Draknora: bronze armour dress, a forum at sunset, golden dust in the air">.
When done run python tools/validators/validate_data.py and python tools/generators/gen_prompt.py and show me the generated prompt.
```

Review what comes back: does the generated `.txt` read like something you would be happy to paste into ComfyUI, are the colours
her colours, and did the assistant touch only data files?

## By hand, for fine tuning

1. Find the card for the image you are unhappy with, then the piece that carries the phrase you want to change.
2. Edit the piece (to change it for every hero) or the card's literal text (to change it for this scene only).
3. Run the loop. Compare the new prompt with the old one in `git diff prompts/`.
4. If the fix has to live in the workflow itself (a node, a setting), use `fork` and pull it back (see
   [workflows/README.md](../../workflows/README.md)).

## Checklist before you commit

- [ ] `python tools/validators/validate_data.py` passes (and `test_validate_data.py` if you changed the validator).
- [ ] Prompts regenerated and the diff under `prompts/` is only what you meant.
- [ ] No hard-coded hero colours in a shared piece; no negations in positive text.
- [ ] Workflows refreshed (`bin\refresh-dev.cmd`) if you want to render it.
