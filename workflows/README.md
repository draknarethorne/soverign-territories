# Workflows

Workflows are generated from the prompts and stored by **set**, mirroring `prompts/`. ComfyUI workspaces are **deploy
targets tied to sets of cards**: each set has a *home* workspace, and which workspace serves which set is configuration
(`workspaces.json`), not folder structure. The repo copy is always the master.

```text
workflows/
  <set>/<Hero>/<Hero>_<Engine>_<Stage>_<Name>.json   generated: Qwen and MiniMax video (tracked in git); set = prompt group
  _templates/                                    the official ST0-ST6 stage templates; new workflows are cloned from them
  _curated/<set>/<Hero>/                         hand-tuned workflows; never regenerated (see Hand-curated workflows)
  .test/firered/<set>/<Hero>/                    generated FireRed test workflows (not in git)
  workspaces.json                                workspaces, homes (which workspace is home for which set), engines, defaults and excludes
  _archive/                                      old layouts and hand-made copies (ignored)
```

## Quick reference: the commands you will use most

Run the scripts from a terminal or double-click `bin\menu.cmd` (`bin\help.cmd` lists everything). Add `--dry-run` as the last
argument to preview. STAGE is optional: `poses`, `head`, `scene`, `hair`, `motion`, `armor`, `clothing`, `video`, or `studio` for
every studio stage.

| I want to | Run |
| --- | --- |
| Check the data is valid | `bin\validate.cmd` |
| Regenerate art prompts from the JSON | `bin\prompts.cmd` |
| Build and push a hero's Qwen workflows to her home workspace | `bin\refresh.cmd Draknora scene` |
| The same for FireRed (local test copies) | `bin\refresh-firered.cmd Draknora scene` |
| Animate: video prompts, workflows, deploy | `bin\animate.cmd Drakness` |
| Regenerate only the video prompts | `bin\videoprompts.cmd` |
| See what is where | `bin\status.cmd --hero Drakness`, `bin\workspaces.cmd` |
| Deploy a set to its home workspace | `python tools\workflows\comfy_workflows.py deploy --group sovereign-dawn` (goes to Sovereign Dawn Series; nothing else needed) |
| Deploy a sister to Drakn Sisters and to Drakness | `python tools\workflows\comfy_workflows.py deploy --hero Drakness` (every home workspace gets everything; add `--new-only` to protect work in progress) |
| Put a temporary copy of a set in another workspace (reels, feeds, a scene next to the art) | `bin\publish.cmd Drakness "Sovereign Territories"`, or `python tools\workflows\comfy_workflows.py deploy --group drakn-sisters -w "Sovereign Territories" --dry-run` |
| Remove what a workspace is not home for (clone leftovers, finished temporary copies), then its empty folders | `bin\cleanup.cmd "Angel Primes"` (preview), add `--apply` (moves to backup; keeps hand-made `zz_` items, edited and undelivered files) |
| Copy a workflow so I can hand-edit it | `bin\fork.cmd WORKFLOW Tag` |
| Keep what I made or changed in ComfyUI | `bin\pull.cmd Drakness` |
| Sort loose workflows in the workspaces into folders | `python tools\workflows\comfy_workflows.py tidy` (preview), add `--apply` |
| Add the staged scenes (held back by default) | `python tools\workflows\comfy_workflows.py deploy --group drakn-sisters --class scene --staged` |
| Put the ST templates in the templates workspace | `bin\deploy-templates.cmd` |
| Set a whole workspace up in one go: deploy its sets, tidy, clean leftovers, status (a preview until `--apply`) | `bin\setup-workspace.cmd "Angel Primes"` |
| Write or extend an angel's card set (and her signature items) | `bin\scaffold-angels.cmd [slug]`, `--coverage` for library use |
| Find or safely move an art piece and every reference to it (including `extends`) | `bin\art-refs.cmd where-used PATH` |
| Find art wording that leans illustrated (realism audit) | `bin\style-audit.cmd` (`--prompts` counts it in the generated prompts) |
| Turn text pasted into several cards into reusable pieces | `bin\extract-literals.cmd` (preview), add `--apply` |
| Run every commit hook | `bin\check.cmd` |

## Workspaces: one home per set

A workspace is tied to a set of cards. `homes` in `workspaces.json` says which workspace is home for which set; a deploy goes to those home workspaces and nowhere else, unless you name another
workspace with `-w` that **accepts** the set (see below).
There is no catch-all workspace and no fallback: a set with no home stops the command with a message instead of landing somewhere else (that silent fallback once filled the brand workspace with 174 card workflows).

| Workspace | Home of | Also accepts, on request |
| --- | --- | --- |
| `Drakn Sisters` | the ten sisters (`drakn-sisters`): the whole image pipeline, Alpha to Video; final art is made here; `zz_Shots`, `zz_Curated`, `zz_Test` are mastered here | |
| `Drakness` | Drakness, as a second copy beside Drakn Sisters, kept in sync on purpose (see below) | |
| `Sovereign Dawn Series` | the Sovereign Dawn cards (`sovereign-dawn`: units, pets, buildings, equipment, tactics, workers) | the Drakn sets |
| `Sovereign Territories` | the art and brand set (`sovereign-territories`: title, logo, icons, key art, plates) and the `ST?_` stage templates | **any set**: promotional videos for reels and feeds, a scene kept next to the art, media for posts |
| `Angel Primes` | the angel test bed (`angel-primes`); it never produces final artwork | |
| `Drakn Bound`, `Elder Dragons` | their own sets; `planned`, so skipped by every command until the install exists and the status is `active` | |

Home rules match on `groups` and/or `heroes`, and `{hero}` stands for the hero's name. A rule may also carry `"class": "studio"` or `"scene"` and then applies only to
stages of that class (the class of each stage folder is defined in `data/art/_schema/stages.json`; anything that is not a scene is studio). `list` shows the home of every hero and what each workspace accepts.

- **Homes and temporary copies.** Every set has a home (the default of every command). Any workspace whose `accepts` list names the set (or `"*"` for any set) may also be given a
  copy on request: `deploy --group G -w "Workspace"` (or `bin\publish.cmd`). A workspace that is neither home for nor accepts a set is refused, so a set can never land in the wrong place.
  The copy is temporary: when you are done, `cleanup -w "Workspace"` removes it. Nothing is ever published automatically.
- **Duplicates in Drakness and Drakn Sisters are intentional.** While we work on one sister, a deploy puts her in both workspaces (the `Drakness` rule has a `heroes` filter), so we can
  work through issues with `zz_Shots`, `zz_Curated` or test items in her own workspace without polluting Drakn Sisters. Any other sister can get a temporary workspace the same way
  (add a `homes` rule with `heroes`, create the install, set it `active`) and be discarded afterwards. `cleanup` never treats these as duplicates to remove.
- **Only active workspaces with an install are written to.** A workspace whose status is `planned`, or whose install folder does not exist, is skipped with a message by deploy, pull,
  cleanup, tidy, denoise and the input reset. Create the install, then set its `status` to `active`. Groups listed under `skipGroups` (today Drakn Bound and Elder Dragons) have no generated workflows yet.
- **Hand-made items are mastered in the workspace.** Anything under a `zz_` folder (`zz_Curated`, `zz_Test`, `zz_Shots`) or named `zz_Curated_...` / `test_...` is never replaced, moved or removed by `deploy` (even with
  `--overwrite`), `cleanup`, `cleanup --orphans`, `tidy` or the input and denoise resets. That is what lets you refine a prompt directly in ComfyUI, fix the art JSON afterwards and redeploy without
  losing the hand-tuned version. Bring one into the repo with `pull` (`pull --shots` for shots); delete one yourself if you want it gone.
- **`cleanup -w WORKSPACE`** removes the generated workflows that workspace is not home for (a clone's leftovers, or copies you published and are finished with), but only when their home workspace holds an
  identical copy and the repo has the master; everything goes to `workflows/.sync/backup/` and the empty folders are pruned afterwards (never a top-level `zz_` folder, never a folder with any file in it).
  Preview first. `status` shows `published` (a temporary copy of a set whose home is elsewhere) and `unrouted` (the workspace is neither home for it nor accepts it) next to the usual counts.

All workspaces that share an output project folder (see Where files live) write there, and the `SaveImage` prefix (`<set>/<Hero>/<phase>/...`) sorts renders into hero folders whichever workspace ran them.

### Stage templates

| Template | Stage | Used by `make --create` |
| --- | --- | --- |
| `ST0_Qwen_Text` | text to image, no reference image (4:5 portrait) | `templates.text` (title and key art; not yet automated) |
| `ST0_FireRed_Text` | the same with FireRed (more photoreal) | none yet |
| `ST1_Qwen_A_Pose` | A-pose from the source photo | `templates.poses` |
| `ST1_Qwen_B_Pose` | A-pose, Qwen 2.1 variant | none |
| `ST2_Qwen_Edit` | every edit after the A-pose: hair, motion, armor, scenes | `templates.default` |
| `ST2_MageFlow_Edit` | edit with Mage-Flow Turbo | none |
| `ST3_FireRed_Final` | FireRed final (the FireRed test engine) | `engines.firered.template` |
| `ST3_Flux_Final` | Flux final | none |
| `ST4_Qwen_Polish` | Qwen polish (int8) | none |
| `ST4_Flux_Polish` | Flux polish | none |
| `ST6_MiniMax_Video` | MiniMax H3 image to video (portrait, turbo) | `engines.minimax.template` |

### FireRed test engine (not in git)

Scenes can also be built for FireRed to compare with Qwen, and **every 1_Alpha step (Prime, Bare, Footwear, the 2b experiments) is built for FireRed too**, for every hero in every set, so the first images can be
compared engine against engine. The Angel Primes test sets `alpha/female` and `alpha/male` carry the **whole suite in both engines** (23 and 20 workflows each). They are generated into `workflows/.test/firered/` (ignored by
git), named `<Hero>_FireRed_<Stage>_<Name>.json`, from the template in `workspaces.json` under `engines`. They carry the
positive prompt only and read the same input images as their Qwen twins (so a FireRed Bare reads the Qwen Prime, until you pick another image in ComfyUI), and they deploy next to the Qwen ones by the same
routing. `--engine qwen|firered` limits any command to one engine. FireRed workflows default to **turbo** (`engines.firered.turbo`;
untick the switch on one workflow for a slow run) and the engine adds a real-then-magic effects instruction to the prompt
(`engines.firered.fx`, for the scenes in `fxScenes`, `"*"` meaning all).

```bash
python tools/workflows/comfy_workflows.py make --group drakn-sisters --engine firered --create
python tools/workflows/comfy_workflows.py deploy --hero Drakness --engine firered --dry-run
# FireRed for every 1_Alpha step of every hero (what `setup` then deploys):
python tools/workflows/comfy_workflows.py make --engine firered --stage alpha --create
# the whole suite of an alpha test set in FireRed (studio stages; its scenes are built by default):
python tools/workflows/comfy_workflows.py make --engine firered --group angel-primes --hero Female --class studio --create
# FireRed versions of just the bare study and celestial steps (a regex needs a trailing $):
python tools/workflows/comfy_workflows.py make --engine firered --group drakn-sisters --stage alpha --match "Alpha_2_Bare_(Figure|Chest)$|Alpha_2b_Celestial[A-Za-z]*$" --create
```

FireRed carries the positive prompt only, so the negative terms in a card do not apply to it; word the removal in the positive prompt. How the stages feed
each other (bare, A-pose with an underlayer, outfit, scene) is in [docs/art/tutorial-art.md](../docs/art/tutorial-art.md#the-image-chain-from-bare-skin-to-scene).

### Folders inside a workspace

A new workflow is saved in the workspace under its output folder, hero first and then the pipeline phase: `<Hero>/<phase>/...` in every shared workspace (`Draknara/1_Alpha/2_Bare/`, `Draknara/4_Wardrobe/armor/wardrobe/`, `Draknara/5_Scenes/themes/`), and `<phase>/...` in a single-hero workspace such as `Drakness`. The phases follow the pipeline in order:

| Phase folder | Holds |
| --- | --- |
| `1_Alpha` | `1_Prime`, `2_Bare` (Figure, Chest), `2b_Experiments/celestial` and `/coverings`, `3_Footwear` (Barefoot, Heels): creates her likeness and the three golden images |
| `2_Studies` | `head` (close-ups, views), `hair`, `body` (turnaround views): studies on the goldens |
| `3_Layers` | the underlayer tests: `base`, `bikini`, `lingerie`, `swimwear`, `athletic`, `one-piece`, `backless` |
| `4_Wardrobe` | `clothing`, `armor`, `showcase` |
| `5_Scenes` | `signature`, `glamour`, `story`, `themes` |
| `6_Finish` | `polish` (Qwen detail pass, input role `scene`), `final` (FireRed look, input role `polish`); upscale is not built yet |
| `7_Video` | animation of a finished image |
| `Bench` | `motion`: a point-in-time test run on any phase's image, not a phase |

The card folders, the prompts and the ComfyUI output all use these phase folders (`art_layout.phase_path` maps a stage and family to its phase, `parse_dirs` goes back); the SaveImage prefix is the prompt's folder.
ComfyUI shows these as folders.
`tidy` moves loose files into them (and removes folders it empties); curated files go to a `zz_Curated/` folder, test files to `zz_Test/` and shots to `zz_Shots/`, which sort after every stage folder (flat in a single-hero workspace, one folder per hero in a shared one). Staged scenes (`Scene_Staged_*`) are built and kept in the repo but only added to a workspace with `deploy --staged`, so the lists hold the scenes you are working on.

### Default incoming images

Every generated workflow opens with a default incoming image, chosen by its stage in `workspaces.json` (`inputRoles`, and the hero's images under `inputs`):
`alpha/` (Alpha 1 Prime) loads the original photo (`photos`); `alpha/bare/` (Alpha 2) loads the Prime image (`prime`); `head/` and `motion/` load the hero's
barefoot golden A-pose (`apose`); everything else (`alpha/footwear/`, `poses/<family>/`, armor, clothing, hair, scenes, showcase) loads her bare-skin image (`bare`). A hero without role inputs keeps the older
behaviour (the A-pose most of her workflows already read). Images are plain names, so each workspace needs the file in its own input folder.

```bash
python tools/workflows/comfy_workflows.py inputs --reset --hero Drakness --dry-run   # preview: repo and every workspace; copies missing images into each workspace's inputs
python tools/workflows/comfy_workflows.py deploy --hero Drakness --patch-only --reset-inputs   # deploy prompts and also reset the inputs
```

During a session you can point a workflow at any other image; a reset (or `--reset-inputs`) puts it back. To keep a custom input, save the workflow under
`zz_Shots/`.

**Choosing a default inside ComfyUI.** Open the generated workflow (for example `<Hero>_Qwen_Alpha_1_Prime`), pick the image in its Load Image node and save it; that is how you set a hero's photo
or golden image. Then bring the choice back into `workspaces.json` so it survives a rebuild or a reset:

```bash
python tools/workflows/comfy_workflows.py inputs --pull --dry-run -w "Angel Primes"   # preview: which defaults you changed in the workspace
python tools/workflows/comfy_workflows.py inputs --pull -w "Angel Primes"             # write them into photos / inputs in workspaces.json
python tools/workflows/comfy_workflows.py inputs --reset --hero Seraphine             # push them into the repo copies (and the rest of her workflows)
```

`--pull` reads only the generated Qwen workflows, ignores the tool's own `..._00001_` placeholders and images named for another hero, and takes a default only when all the workflows of that role agree
(otherwise it reports `MIXED` and leaves it to `inputs --set`). `status` shows `inputs-changed` for any default you set in a workspace that `workspaces.json` does not hold yet, `setup` pulls first, and
`inputs --reset` **stops** while such a choice is unpulled (`--force` overrides it, with a backup) so a reset can never silently undo your pick. The golden images are named by step with a `_00000` counter, so they sort above the numbered renders: `<Hero>_Qwen_Alpha_1_Prime_00000.png`,
`<Hero>_Qwen_Alpha_2_Bare_00000.png`, `<Hero>_Qwen_Alpha_3_Barefoot_00000.png` and `<Hero>_Qwen_Alpha_3_Heels_00000.png`. These are already the names in `inputs`, so
dropping a chosen render into a workspace's input folder under that name is all it takes; `inputs --reset` repoints every workflow (a missing file is reported, not copied).
Retire the temporary `Alpha_2_Bare_Skin` shots once `Alpha_2_Bare_Figure` is tuned.

**Angel Primes.** The `Angel Primes` workspace is one tree for a whole test deck: `female/<Hero>/<phase>/...`, `male/<Hero>/<phase>/...`, and later `pets/`, `units/`, `buildings/`, `equipment/`, `tactics/` and `workers/`
(the divisions in `data/art/_settings/groups.json`; the repo copies of the workflows stay flat per hero). The twenty angels use the same golden-image names. Their original photo is expected as `<slug>_photo_944x1104.png` (`seraphine_photo_944x1104.png`, `auriel_photo_944x1104.png` ...) in the
`Angel Primes` input folder, already padded to the standard size; change a name with `inputs --set --hero Seraphine --photo <file>`. The male angels have no Barefoot or Heels step, so their `apose`
role points at the Alpha 2 Bare image and their golden image is the Bare. The ten women's photos are the `various_image_...` files you chose in ComfyUI, pulled into `photos`.
Angelica and Angelo follow the same Phase 1 and Phase 2 as every other angel (Alpha 1 Prime, 2 Bare, 3 Footwear and the 2b experiments for her; Prime and Bare for him; heads, views, body views and hair for both);
their old single `X_Pose` workflow was retired (its photo went into `photos`, and the file is in `workflows/_archive/legacy-x-pose/`). The workspace is `active`; a clone of another install is cleaned with `cleanup -w "Angel Primes"` (preview first).

**Alpha test sets.** `alpha/Female` and `alpha/Male` in the `Angel Primes` workspace (`prompts/angel-primes/alpha/<Hero>/`, output `Angel Primes/alpha/<Hero>/...`) are two generic test heroes for trying a photo before giving it to an angel, in a short version
of the phases (the woman has 23 workflows, the man 20): Phase 1 (Prime, Bare, and for her Bare chest, Barefoot and Heels), Phase 2 (head, face close-up, two head views, three body views, two hairstyles), two layer tests, one outfit, one armor, a Glamour
and a Signature scene with generic white wings, and three motions. Nothing of them touches an angel's folders, images or `photos`. To use one: copy the photo into the `Angel Primes` input folder, open `alpha/Female/1_Alpha/1_Prime/Female_Qwen_Alpha_1_Prime`
and pick it in the Load Image node, run Phase 1 and 2 and compare with the angel you have. If the photo wins, pick it in that angel's Prime workflow instead and run `inputs --pull -w "Angel Primes"` (it then holds the new photo for her, and the test
set stays free for the next photo). `bin\scaffold-angels.cmd --alpha` rewrites the cards, then `refresh-group angel-primes` (or `setup-workspace "Angel Primes"`) builds and deploys them.

**Standard size (Oct 2026, provisional).** `standardSize` in `workspaces.json` is `[944, 1104]`: every original is scaled to fit and padded (not cropped) to that size
before the first X Pose, and the X Pose, Bare Skin and Barefoot images are expected at the same size. 944x1104 is one of the Kontext scaler's buckets, so the Qwen
templates pass it through unchanged; FireRed resizes to 1 MP (947x1107) and the VAE trims it back. The reset sequence for a hero:

```bash
python tools/workflows/comfy_workflows.py inputs --status                       # every hero's photo / A-pose / bare image: where found, size, ok or WRONG SIZE or MISSING
python tools/workflows/comfy_workflows.py inputs --set Draknara --photo Draknara_Photo_944x1104.png --prime Draknara_Alpha_Prime.png --bare Draknara_Qwen_Bare_Golden.png
python tools/workflows/comfy_workflows.py inputs --reset --hero Draknara --dry-run   # then without --dry-run; --reset also finds images under the output folders and copies them into each workspace's inputs
```

`--set` only needs the roles you give it (`--photo`, `--apose`, `--bare`); with `--dry-run` it prints and writes nothing. Workflows in `zz_Shots/` are never reset.

### Denoise defaults

New generated workflows start at the high end of the range in their stage template (`Denoise ~0.8-0.9.` in `data/art/_templates/heroes/*.txt`; 1.0 only for the Prime from the original photo), not at 1.0. Since Oct 2026 the edit stages run at 0.8 to 0.95
(0.7 held the pose too tight) and state the likeness in a Critical details block. `make --create` sets it, `comfy_workflows.py denoise` previews the plan and `denoise --reset` applies it to the repo and every workspace (backups first; `zz_Shots` and curated
workflows are never touched, and a denoise you set by hand in a workspace is listed as `KEPT`, not overwritten, unless you add `--force`).
The table and the tuning rules are in [docs/art/comfyui-art-pipeline.md](../docs/art/comfyui-art-pipeline.md#denoise-is-the-key-lever).

### Shots (zz_Shots)

A shot is a workflow you tuned for one render: a chosen seed, Turbo on or off, a changed input. Save it in the workspace under `zz_Shots/`, in any subfolders you like (`zz_Shots/armor/`, `zz_Shots/poses/` ...).
`pull --shots` (`bin\pull-shots.cmd HERO`) keeps it in the repo under `workflows/_shots/<set>/<Hero>/` with the same subfolders and captures later edits; its file name and output prefix stay as you set them.
`deploy --shots` (`bin\deploy-shots.cmd HERO`) copies kept shots to a workspace that lacks them and never overwrites a differing copy.
`status` shows `shots`, `shots-new` (pull it), `shots-changed` and `shots-missing`.
**Numbered saves count as shots too.** A workflow ComfyUI saves from a render keeps a counter in its name (`Azaline_Qwen_Alpha_1_Prime_00004_.json`) and the seed of that render, so one left loose in the workflow list (outside the `zz_` folders) is treated as a shot, not as an install-only or a curated workflow:
`status` lists it as `shots-new`, `pull --shots` keeps it in `workflows/_shots/<set>/<Hero>/` (the workspace copy stays where you saved it), and `cleanup` and `tidy` leave it alone. The name is the only test: a counter name that is already kept in `workflows/_curated` stays curated.
If two workspaces hold a different shot under one file name (another seed), `pull --shots` keeps the first one pulled and prints `CONFLICT` for the other; rename one of them to keep both.
Later, a seed worth keeping can move from a shot into the art data, so the Qwen and FireRed workflows are built with it (not built yet).
A shot is not a curated workflow: curated ones are the older hand-written workflows (and new ones written from scratch to test a concept), shots are the ones in use. Shots are captured even from a legacy workspace such as Drakness.

### Hand-curated workflows

Curated workflows write to their own output folder, `<set>/<Hero>/_curated/<name>` (for example `drakn-sisters/Drakness/_curated/`), so hand-tuned renders never mix with the generated families. `fork` and `pull` set this prefix for you (and patch the workspace copy to match); only the SaveImage prefix changes.
Curated files are named `zz_Curated_<Hero>_...` so they sort to the bottom of a workspace list and are never mistaken for generated ones; a workflow you captured from a render keeps its counter name (`..._00001`) and is left as it is.
Test workflows (experiments, A/B and bisect variants) are named `test_<Hero>_...` and live in `workflows/_test/<set>/<Hero>/`, writing renders to `<set>/<Hero>/_test/`. They are not kept in workspaces: put them there when needed with `deploy --tests --hero H --match test_`, and `pull` saves new or edited ones back to `_test` before you remove them from the workspace. Prefix summary: no prefix is generated, `zz_Curated_` is hand-tuned and kept, `test_` is temporary.

Generated workflows are rebuilt from prompts, so a hand edit to one would be overwritten. Anything you tune by hand lives in
`workflows/_curated/<set>/<Hero>/` instead. `make` and `deploy` never touch that folder.

| You want to | Run | What happens |
| --- | --- | --- |
| Start from a generated workflow and tune it | `fork NAME --as Tag` (`bin\fork.cmd`) | Copies it to `_curated` as `zz_Curated_NAME_Tag` (its output folder uses `NAME_Tag`, and it records what it came from), and puts it in the hero's home workspace(s) |
| Keep what you did in ComfyUI | `pull --hero H` (`bin\pull.cmd`) | A workflow that exists only in the workspace is kept as curated (and renamed `zz_Curated_...` in both places); edits to a curated one are captured |
| Put curated workflows in another workspace | `deploy --curated --hero H` (`bin\deploy-curated.cmd`) | Copies the ones the workspace lacks; a copy there that differs is skipped, never overwritten, unless you add `--overwrite` |
| See what is where | `status --hero H` | Shows `curated`, `curated-changed` (pull it) and `curated-missing` (deploy it) next to the generated counts, and `install-only` for anything not yet kept |

Name a curated workflow with the hero first (`Drakness_...`) so the tool can route it (the `zz_Curated_` prefix is added for you); the generated names are
`<Hero>_<Engine>_<Stage>_<Name>`, so adding a tag at the end never collides. If a curated idea turns out to be worth
automating, move what it does into a motion, transition, template or card piece, regenerate, and retire the curated copy.

### Video (MiniMax)

`data/animation/_sets/<group>/<hero>/*.json` cards turn a finished image into a short video prompt. A card names the hero,
the source (`artCard` for art we generated, so the intro is summarised from what we asked for, or `describe` for any outside
image), a look, and a list of `actions`. Each action becomes its own `Motion:` or `Scene:` block with a time range, joined to
the one before by a transition (`flow`, `blend`, `settle`, `hold`, `cut`, or any sentence you type). An action is a reusable
piece (`motion`, `scene`), literal text (a plain string or `beat`), and can carry `with` (things that happen together).

```bash
python tools/generators/gen_animation.py                                   # cards -> prompts/<group>/<Hero>/video/
python tools/workflows/comfy_workflows.py make --engine minimax --create   # prompts -> workflows/<set>/<Hero>/ (ST6 template, tracked in git)
python tools/workflows/comfy_workflows.py deploy --hero Drakness --engine minimax
```

Files are named `<Hero>_Video_<scene or pose it animates>_<Name>`, for example `Drakness_Video_Scene_Staged_EnchantedEvening_Awakening`.

### Working on one sister: Drakness beside Drakn Sisters

Every command takes `--class studio|scene` (all studio stages, or just scenes), `--stage`, `--match` and `--dry-run`. `deploy` **copies** to every home workspace of the hero, or to the workspace you name with `-w`.

```bash
# put one sister's scenes in her workspaces (Drakn Sisters and, for Drakness, her own), keeping what is there
python tools/workflows/comfy_workflows.py deploy --hero Drakness --class scene --new-only --dry-run
# put a temporary copy of her videos where promotional media is kept, then remove it when done
python tools/workflows/comfy_workflows.py deploy --hero Drakness --stage video -w "Sovereign Territories" --dry-run
python tools/workflows/comfy_workflows.py cleanup -w "Sovereign Territories"
```

## The loop

1. `bin\refresh.cmd HERO [STAGE]` regenerates prompts, creates or refreshes the repo workflows and deploys them to the hero's home workspace(s).
2. Run and refine there. Change the input image, seed or prompts as needed. Save a render-specific tuning under `zz_Shots/` or a hand-written one under `zz_Curated/`; both are guarded.
3. `bin\pull.cmd HERO` keeps what you made or edited in ComfyUI: new workflows become curated, edits to curated ones and shots are captured in the repo. Fix the art JSON, regenerate and redeploy: generated workflows follow
   the new prompts, and the hand-made ones stay as they are.
4. Need the set somewhere else for a while (reels, feeds, a scene next to the art)? `publish HERO "Workspace"` puts a copy there if that workspace accepts it; `cleanup "Workspace"` removes it when you are done.

If a destination workspace is not active or its install does not exist, the workflow is left where it is (skipped, with a message).

## Scripts

Run these from a terminal, or double-click `bin\menu.cmd`. `bin\help.cmd` lists them all.

```text
bin\refresh.cmd Draknara scene           prompts + workflows + deploy to the home workspace
bin\refresh-firered.cmd Draknora scene       the same for FireRed (local test workflows)
bin\animate.cmd Drakness                     video prompts + MiniMax workflows + deploy to the home workspace
bin\deploy.cmd HERO [STAGE]              deploy to the hero's home workspace(s)
bin\publish.cmd HERO "Workspace" [STAGE]     a temporary copy in a workspace that accepts the set
bin\cleanup.cmd "Workspace" [--apply]        remove what that workspace is not home for (preview unless --apply)
bin\setup-workspace.cmd "Workspace" [--apply]   deploy its sets, tidy, cleanup and status in one go
bin\fork.cmd | pull.cmd | deploy-curated.cmd      hand-curated workflows
bin\status.cmd | workspaces.cmd | inputs.cmd
bin\prompts.cmd | videoprompts.cmd | validate.cmd | check.cmd | style-audit.cmd | extract-literals.cmd
```

Add `--dry-run` as the last argument to preview. The tool behind them is `tools/workflows/comfy_workflows.py`; its tests (`python tools/workflows/test_comfy_workflows.py`) run in pre-commit and pin the homes, the `accepts` rule and the `zz_` guards.

## Rules worth knowing

- **Deploy needs a filter** (hero, group, stage or match), or `--all`. A set with no home workspace stops the command, and a workspace given with `-w` must be home for the set or accept it.
- **Deploy keeps your tuning.** An existing workflow only gets its positive prompt, negative prompt and filename prefix
  updated; input image, seed and toggles stay. `--overwrite` replaces the whole file. A `legacy` workspace (Drakness, which
  still holds hand-made experiments) always gets whole-file replacement. Hand-made `zz_` items are never touched either way.
- **Nothing is deleted;** anything changed, moved or cleaned out of a workspace is first copied to `workflows/.sync/backup/`.
- **Input images:** new workflows read the A-pose the hero's other workflows already use (`inputs`). Pin one in
  `workspaces.json` under `inputs` once you choose a golden pose.
- **Stage templates:** `deploy-templates` puts the `ST?_` templates in the workspace flagged `"templates": true` (Sovereign Territories). They are the only templates: `make --create` clones
  them (`templates` and `engines` in `workspaces.json`), so tune one there, `pull --templates` it back, and every new workflow follows.
- **`X_*` files are never mirrored** (`exclude` in `workspaces.json`, plus `.gitignore`).
- `pull -w <Workspace>` brings workflows that only exist in a workspace into the repo; it is off for `legacy` workspaces.
- **A new install is a clone, so clean it:** cloning a workspace copies everything it holds. Add its `homes` rule, set it `active`, deploy its set, then `cleanup -w "<Workspace>"` (preview, then `--apply`).

## Where files live

Folder locations are set once in `workspaces.json` under `paths`; the tools read them from there.

```text
B:\Sovereign Territories\Models        original reference photos: the source, never an upload target
B:\Sovereign Territories\Masters       hand-picked keepers copied from the output (what the backup script protects)
B:\Comfy-Desktop\ComfyUI-Installs      the workspaces (code and workflows)
B:\Comfy-Desktop\ComfyUI-Inputs\<Workspace>   that workspace's own input images: transient copies
B:\Comfy-Desktop\ComfyUI-Outputs\<Project>   raw output, one folder per project; the prefix sorts it by <set>/<Hero>/<phase>/...
```

Each workspace writes to the project folder named by its `output` setting in `workspaces.json` (set in ComfyUI as that install's
output directory), and the prefix inside it does not change:

| Output project folder | Written by | Sets inside |
| --- | --- | --- |
| `Sovereign Territories` | Drakn Sisters, Drakness, Drakn Bound, Elder Dragons and the Sovereign Territories brand workspace | `drakn-sisters`, `drakn-bound`, `elder-dragons`, `sovereign-territories` |
| `Angel Primes` | the Angel Primes workspace (a test bed; it never produces final artwork) | `angel-primes` |
| `Sovereign Dawn Series` | the Sovereign Dawn Series workspace: the card set, kept apart from experiments | `sovereign-dawn` |

Everything under `Comfy-Desktop` is a transient copy of something that lives in the repo or on the working drive.
`python tools\workflows\sync_inputs.py` copies, into each workspace's own folder, exactly the images that workspace's workflows load
(preview first, then `--apply`). `python tools\workflows\organize_outputs.py` moves images rendered earlier (the old shared output) into `<project>/<set>/<Hero>/...`. Set each install's input and output folders in ComfyUI (the `--input-directory` and
`--output-directory` launch arguments), then retire the old shared folders. Until a folder exists, the tools fall back to the
old shared one.
