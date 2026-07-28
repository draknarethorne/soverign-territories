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
are documented in [the archive-to-canon reconciliation](docs/working/archive-canon-reconciliation-jul2026.md).

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

## Repository layout

- `data/` — runtime card/product/progression data and schemas.
- `data/schemas/` — machine-readable contracts for validation and implementation.
- `docs/` — vision, MVP plan, design rules, governance, and historical records.
- `scripts/` and `tools/` — validation, generation, and maintenance utilities.
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
