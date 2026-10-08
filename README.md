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
