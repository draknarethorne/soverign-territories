# Sovereign Territories

> **Build the Deck. Conquer the Campaign. Level Your Heroes.**

Sovereign Territories is a card-driven tactical strategy game in design. The first
release is planned as a local-first PvE vertical slice: collect a small roster, build a
six-card formation around one hero, and conquer a short campaign through deterministic
8×8 battles.

Territorial conquest, empire automation, alliances, and large-scale competition are
long-term aspirations—not current MVP commitments.

## Project status

| Area | Status |
| --- | --- |
| Vision and MVP reconciliation | In progress |
| Runtime data and schemas | Present under `data/` |
| Unity client | Not started |
| Online backend | Not started; not required for the MVP baseline |
| Implementation readiness | Not yet claimed |

The repository has baseline quality checks, but quality checks alone cannot prove that a
game plan, data subset, and implementation scope agree. The evidence and readiness gates
are in [docs/STATUS.md](docs/STATUS.md).

## MVP baseline

- a compact validated card subset and starter collection;
- one six-card formation with exactly one hero;
- deterministic HP/Mana/ATK/DEF tactical PvE on an 8×8 grid;
- 8–12 authored campaign encounters and a boss;
- local save state, basic rewards, and concise onboarding;
- small external playtests before expanding scope.

Not part of the MVP: PvP, alliances, territory maps, AFK economy, crafting, fusion,
equipment, IAP, battle passes, live events, and backend services.

## Documentation

Start with the [documentation hub](docs/README.md), then read:

1. [Game Bible](docs/game-bible.md) — vision and principles.
2. [Feasible Solo-Developer MVP](docs/mvp/solo-dev-realistic-mvp.md) — scope authority.
3. [MVP Dependency Plan](docs/mvp/mvp-scope-final.md) — build order and acceptance checks.
4. [Combat Specification](docs/design/combat-calculation-spec.md) and
   [Deck Rules](docs/design/deck-progression-rules.md) — executable design rules.

## Art and video pipeline

Use regular **64-bit CPython 3.14** for the repository's image-processing tools.
Python 3.12 compatibility is retained; routine CI uses 3.14, with 3.12/3.13
compatibility runs available on explicit dispatch. Dependency
setup and the distinction from ComfyUI's Python are in the
[photo-library runtime guide](docs/art/original-photos.md#python-runtime-and-dependencies).

Card art and short video clips are generated from small JSON files, never hand-written prompts. The guides:

- [Tutorial: creating art JSON](docs/art/tutorial-art.md) and [tutorial: creating video JSON](docs/art/tutorial-video.md), by hand or with an AI.
- [Workflows and launchers](workflows/README.md): the ComfyUI workspaces (one home per set, temporary copies on request), the Qwen, FireRed and MiniMax engines, and
  hand-curated workflows.
- [Art structure reference](data/art/README.md) and [status](docs/STATUS.md).

The commands you will run most (from the repo root; `bin\help.cmd` lists every launcher):

```text
bin\validate.cmd                        # data checks and tool tests (--quick or --full add the validator self-test)
bin\prompts.cmd                         # art JSON -> prompts
bin\refresh.cmd Draknora scene      # prompts -> workflows -> the home workspace (add --dry-run to preview)
bin\animate.cmd Drakness                # video cards -> prompts -> MiniMax workflows -> the home workspace
bin\status.cmd --hero Drakness          # what is where
```

## Setting up a development machine

The repository holds code, data and docs. The photo library, ComfyUI and model
caches live outside it. Set up a new Windows machine in this order:

1. **Tools.** Install git (with Git Credential Manager), the GitHub CLI `gh`
   (`gh auth login`), regular 64-bit **CPython 3.14** (`py -3.14`), Node.js LTS
   (markdownlint runs through it), PowerShell 5.1+ (Windows built-in) and VS Code
   with GitHub Copilot. ComfyUI Desktop is needed only for art/video rendering.
2. **Clone and branch.**

   ```bat
   git clone https://github.com/draknarethorne/soverign-territories.git
   cd soverign-territories
   git switch work/sandbox-rebase-acceptance
   ```

   Check [docs/recap/README.md](docs/recap/README.md) for the active branch and
   resume handoff before switching.
3. **Python environment.** In a new venv, install the pinned dependencies and
   the hooks. The full notes, including the warning never to install into
   ComfyUI's embedded Python, are in the
   [runtime guide](docs/art/original-photos.md#python-runtime-and-dependencies).

   ```bat
   py -3.14 -m venv .venv-processing
   call .venv-processing\Scripts\activate.bat
   python -m pip install -r requirements-intake.txt
   python -m pip install pre-commit==4.6.1
   python -m pre_commit install
   ```

   Use `requirements.txt` instead for validators/galleries only (no intake). The
   intake models (Mask R-CNN, LaMa) download once, with pinned hashes, into
   `%LOCALAPPDATA%\sovereign-territories`.
4. **Machine paths.** [workflows/workspaces.json](workflows/workspaces.json)
   records this project's library and ComfyUI roots (the `B:` drive layout:
   `B:\Sovereign Territories`, `B:\Sovereign Territories Sandbox\Working`,
   `B:\Comfy-Desktop\...`). On a machine with different drives, set the user
   environment variables below instead of editing the tracked file:

   | Variable | Points to |
   | --- | --- |
   | `SOVEREIGN_TERRITORIES_PRODUCTION_ROOT` | the Production photo library |
   | `SOVEREIGN_TERRITORIES_SANDBOX_WORKING_ROOT` | the sandbox `Working` library |
   | `SOVEREIGN_TERRITORIES_MODEL_CACHE_ROOT` | the model cache (optional) |
   | `SOVEREIGN_TERRITORIES_INSTALLS_ROOT` | the ComfyUI installs folder |
   | `SOVEREIGN_TERRITORIES_INPUTS_ROOT`, `..._OUTPUT_ROOT` | the ComfyUI input/output roots |
   | `SOVEREIGN_TERRITORIES_SHARED_INPUT_ROOT`, `..._SHARED_OUTPUT_ROOT` | shared ComfyUI input/output |

   Overrides are recorded in every run's configuration receipt. Changing them
   between steps of one sandbox run makes its verification refuse to continue,
   so finish or restart a run on the machine that started it.
5. **Data that git does not carry.** Copy these yourself. Each is git-ignored
   or outside the repository:
   - the Production library and, if you continue a sandbox run, the whole
     sandbox folder (its `_sandbox-state` holds the run evidence);
   - `feedback\` (raw user notes; never bulk-clear it) and any legacy notes in
     `tmp\` (scratch otherwise);
   - ComfyUI installs, models and the `ComfyUI-Inputs`/`Outputs` folders.
6. **Verify.** `bin\check.cmd` (pre-commit hooks, markdownlint, data
   validation) and `bin\validate.cmd --quick` (isolated mutation smoke checks,
   not the image unit suite). `bin\help.cmd`
   lists every launcher; `bin\library-check.cmd` confirms the library paths
   resolve.

### How the work is organised

- **Launchers first.** Run `bin\*.cmd` (`cmd /c bin\name.cmd ...`) rather than
  calling `tools\` scripts directly; most preview with `--dry-run` and check
  read-only with `--check`. New routines become launchers.
- **Plans and status.** [docs/STATUS.md](docs/STATUS.md) holds the current
  decisions; [docs/plans/](docs/plans/README.md) owns the work, with tagged
  checkboxes (`- [ ] **P1 ai** ID ...`) that `bin\todo.cmd` turns into
  [docs/todo.md](docs/todo.md). Raw feedback goes in `feedback\<topic>.md`
  and is quoted word for word in its owning plan.
- **Handoffs.** [docs/recap/](docs/recap/README.md) pins the current resume
  recap; read it first on a new machine.
- **Quality.** [docs/QUALITY-GATES.md](docs/QUALITY-GATES.md) defines routine
  versus targeted/deep validation. Scratch output goes under the git-ignored
  `tmp\`.
- **AI agents.** [.github/copilot-instructions.md](.github/copilot-instructions.md)
  is the shared working contract; the specialised agents are listed in
  [.github/agents/](.github/agents/AGENT-SELECTION-GUIDE.md).

## Repository layout

- `data/` — runtime card/product/progression data and schemas.
- `data/schemas/` — machine-readable contracts for validation and implementation.
- `data/art/`, `data/animation/` — art and video source JSON; `prompts/` and `workflows/` are generated from them.
- `docs/` — vision, MVP plan, design rules, governance, and historical records.
- `scripts/` and `tools/` — validation, generation, workflow sync and maintenance utilities; `bin/` has the quick launchers.
- `src/` — reserved for the future Unity client and server modules.

## Intended technology direction

- **Client:** Unity and C#.
- **MVP persistence:** local-first.
- **Future online services:** Nakama/PostgreSQL only when an approved online feature
  requires them.

## Quality and contributions

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/QUALITY-GATES.md](docs/QUALITY-GATES.md)
for the repository quality contract. The project is not currently accepting broad external
implementation work while the MVP source-of-truth and data subset are reconciled.

## License

Proprietary — all rights reserved.
