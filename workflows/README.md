# Workflows

Workflows are generated from the prompts and stored by **set**, mirroring `prompts/`. ComfyUI workspaces are **deploy
targets**; which workspace is dev, which is acceptance and which makes the final art is configuration
(`workspaces.json`), not folder structure. The repo copy is always the master.

```text
workflows/
  <set>/<Hero>/<Hero>_Qwen_<Stage>_<Name>.json   set = prompt group (drakn-sisters, angel-primes, ...)
  _templates/                                    the official ST0-ST4 stage templates; new workflows are cloned from them
  workspaces.json                                workspaces, routes (dev, uat, prod), defaults and excludes
  _archive/                                      old layouts and hand-made copies (ignored)
```

## Dev, UAT, Prod

| Tier | Flag | Workspaces | Purpose |
| --- | --- | --- | --- |
| **dev** (default) | none | `Soverign Territories`; later themed ones such as `Soverign Territories Halloween` | build and prove workflows, ideation, mass changes |
| **uat** | `--to uat` | a hero's own workspace (`Drakness`), a group's (`Angel Primes`, `Drakn Bound`) or a shared scene workspace (`Drakn Sisters`) | acceptance: pick the A-pose, curate, generate 8-16 images |
| **prod** | `--to prod` | `<Series> Series`, such as `Soverign Dawn Series` | final art and polish for the actual cards of that series |

UAT and prod targets come from the `production` rules in `workspaces.json`: they match on `groups` and/or `heroes`, and
`{hero}` stands for the hero's name. A rule may also carry `"class": "studio"` or `"scene"` and then applies only to
stages of that class (the class of each stage folder is defined in `data/art/_schema/stages.json`; anything that is not a
scene is studio). The first matching UAT rule wins, so class rules go first: sister scenes route to `Drakn Sisters`, sister
studio work to the sister's own workspace. `list` shows the studio and scene routes per hero. A workspace that does not
exist yet is skipped.

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

### FireRed test engine (not in git)

Scenes can also be built for FireRed to compare with Qwen. They are generated into `workflows/.test/firered/` (ignored by
git), named `<Hero>_FireRed_Scene_<Name>.json`, from the template in `workspaces.json` under `engines`. They carry the
positive prompt only and read the same A-pose as the Qwen scene, and they deploy next to the Qwen ones by the same
routing. `--engine qwen|firered` limits any command to one engine.

```bash
python tools/workflows/comfy_workflows.py make --group drakn-sisters --engine firered --create
python tools/workflows/comfy_workflows.py deploy --hero Drakness --engine firered --dry-run
```

### Video (MiniMax)

`data/animation/_sets/<group>/<hero>/*.json` cards turn a finished image into a short video prompt. A card names the hero,
the source (`artCard` for art we generated, so the intro is summarised from what we asked for, or `describe` for any outside
image), a look, and a list of `actions`. Each action becomes its own `Motion:` or `Scene:` block with a time range, joined to
the one before by a transition (`flow`, `blend`, `settle`, `hold`, `cut`, or any sentence you type). An action is a reusable
piece (`motion`, `scene`), literal text (a plain string or `beat`), and can carry `with` (things that happen together).

```bash
python tools/generators/gen_animation.py                                   # cards -> prompts/<group>/<Hero>/video/
python tools/workflows/comfy_workflows.py make --engine minimax --create   # prompts -> workflows/.test/minimax (ST6 template)
python tools/workflows/comfy_workflows.py deploy --hero Drakness --engine minimax
```

Files are named `<Hero>_Video_<scene or pose it animates>_<Name>`, for example `Drakness_Video_Scene_Staged_EnchantedEvening_Awakening`.

### Splitting a hero: studio to her workspace, scenes where you choose

Every command takes `--class studio|scene` (all studio stages, or just scenes), `--stage`, `--match` and `--dry-run`.
Promote **moves** (the dev copy is retired); `--keep` or `deploy` **copies** (dev keeps its copy).

```bash
# studio done: move it to each sister's own workspace
python tools/workflows/comfy_workflows.py promote --to uat --hero Drakness --class studio --dry-run
# move only chosen scenes to Drakn Sisters; the rest stay in dev
python tools/workflows/comfy_workflows.py promote --to uat --hero Drakness --class scene --match Glamour --dry-run
# copy all sister scenes to Drakn Sisters and keep them in dev too
python tools/workflows/comfy_workflows.py deploy --to uat --group drakn-sisters --class scene --dry-run
``` All workspaces share one output
folder, and the `SaveImage` prefix (`<Hero>/<stage>/...`) sorts renders into hero folders whichever workspace ran them.

## The loop

1. `refresh-dev HERO [STAGE]` regenerates prompts, creates or refreshes the repo workflows and deploys them to dev.
2. Run and refine in dev. Change the input image, seed or prompts as needed.
3. `promote-uat HERO [STAGE]` **moves** approved workflows to the hero's UAT workspace. The dev copy (with your
   tuning) becomes the new repo master, is copied to UAT and is taken out of dev, so it lives in one place. The removed
   copy is kept in `workflows/.sync/backup/`; `--keep` copies instead.
4. `promote-prod HERO [STAGE]` does the same from UAT to the series workspace.

If the destination workspace does not exist yet, the workflow is left where it is (reported as `HOLD`).

## Scripts

Run these from a terminal, or double-click `bin\menu.cmd`. `bin\help.cmd` lists them all.

```text
bin\refresh-dev.cmd Draknara scene           prompts + workflows + deploy to dev
bin\deploy-dev.cmd | deploy-uat.cmd | deploy-prod.cmd HERO [STAGE]
bin\promote-uat.cmd | promote-prod.cmd HERO [STAGE]
bin\status.cmd | workspaces.cmd | inputs.cmd
bin\prompts.cmd | validate.cmd | check.cmd
```

Add `--dry-run` as the last argument to preview. The tool behind them is `tools/workflows/comfy_workflows.py`.

## Rules worth knowing

- **Deploy and promote need a filter** (hero, group, stage or match), or `--all`.
- **Deploy keeps your tuning.** An existing workflow only gets its positive prompt, negative prompt and filename prefix
  updated; input image, seed and toggles stay. `--overwrite` replaces the whole file. A `legacy` workspace (Drakness, which
  still holds hand-made experiments) always gets whole-file replacement.
- **Nothing is deleted;** anything changed or moved out of a workspace is first copied to `workflows/.sync/backup/`.
- **Input images:** new workflows read the A-pose the hero's other workflows already use (`inputs`). Pin one in
  `workspaces.json` under `inputs` once you choose a golden pose.
- **Stage templates:** `deploy-templates` puts the `ST?_` templates in dev. They are the only templates: `make --create` clones
  them (`templates` and `engines` in `workspaces.json`), so tune one in dev, `pull --templates` it back, and every new workflow follows.
- **`X_*` files are never mirrored** (`exclude` in `workspaces.json`, plus `.gitignore`).
- `pull -w <Workspace>` brings workflows that only exist in a workspace into the repo; it is off for `legacy` workspaces.
