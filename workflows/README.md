# Workflows

Workflows are generated from the prompts and stored by **set**, mirroring `prompts/`. ComfyUI workspaces are **deploy
targets**; which workspace is dev, which is acceptance and which makes the final art is configuration
(`workspaces.json`), not folder structure. The repo copy is always the master.

```text
workflows/
  <set>/<Hero>/<Hero>_Qwen_<Stage>_<Name>.json   set = prompt group (drakn-sisters, angel-primes, ...)
  _templates/                                    Qwen masters that new files are cloned from, plus the ST1-ST4 stage templates
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
- **Stage templates:** `deploy-templates` puts the `ST?_` templates (FireRed, Flux, Qwen polish...) in dev.
- **`X_*` files are never mirrored** (`exclude` in `workspaces.json`, plus `.gitignore`).
- `pull -w <Workspace>` brings workflows that only exist in a workspace into the repo; it is off for `legacy` workspaces.
