# Sovereign Territories Documentation

**MVP tagline:** *Build the Deck. Conquer the Campaign. Level Your Heroes.*
**Future vision:** *Build the Deck. Rule the Map. Automate the Empire.*

## Current status

The project is in design and pre-implementation reconciliation. Quality gates pass at their
current baseline, but that does **not** establish implementation readiness. Canonical
scope, data-contract location, starter content, and feasibility must agree before the MVP
is described as ready for Unity work.

See `working/archive-canon-reconciliation-jul2026.md` for evidence, active corrections,
and the readiness gates.

## Read in this order

1. [Game Bible](game-bible.md) — player promise, principles, and phased vision.
2. [Feasible Solo-Developer MVP](mvp/solo-dev-realistic-mvp.md) — authoritative MVP
   scope and schedule.
3. [MVP Dependency Plan](mvp/mvp-scope-final.md) — build order and acceptance checks.
4. [Combat Calculation Specification](design/combat-calculation-spec.md) — deterministic
   battle rules.
5. [Deck and Formation Rules](design/deck-progression-rules.md) — legality, one-hero
   formation, copy limit, and rarity budget.
6. [MVP Tutorial Flow](mvp/tutorial-flow.md) — short onboarding sequence.
7. [Archive-to-Canon Reconciliation](working/archive-canon-reconciliation-jul2026.md) —
   archive dispositions and readiness evidence.

## Canonical source matrix

| Concern | Primary source | Rule |
| --- | --- | --- |
| Vision and long-term phases | `game-bible.md` | Vision does not override executable MVP details. |
| MVP scope and schedule | `mvp/solo-dev-realistic-mvp.md` | Wins on MVP scope/scheduling conflicts. |
| MVP delivery order | `mvp/mvp-scope-final.md` | Defines dependencies and acceptance checks. |
| Combat rules | `design/combat-calculation-spec.md` | Owns exact combat behavior. |
| Formation/deck rules | `design/deck-progression-rules.md` | Owns copy, hero, rarity, and budget behavior. |
| Tutorial | `mvp/tutorial-flow.md` | Owns required onboarding sequence. |
| Runtime data contracts | `../data/schemas/*.json` | Schemas, validators, and runtime tooling are authoritative. |
| Art-direction pipeline | `../data/art/README.md` | Authoritative for how card art is produced (identity files, components, templates, `gen_prompt.py`). |
| Hero/dragon vision roster | `codex/heroes/ideation_codex.md` | The 10-element / 30-hero long-horizon roster + the Sundering storyline. **Ideation-tier vision**, not MVP scope — a subset ships first. |
| Art ↔ gameplay seam | `working/art-gameplay-reconciliation-oct2026.md` | Ordered plan to reconcile art data vs gameplay data vs schemas. |

## Phases

| Phase | Approved focus |
| --- | --- |
| MVP | Local-first cards, a meaningful starter deck from **3–4 elements** (subset of the vision roster), deterministic 8×8 PvE, short linear campaign, save/reward loop. |
| 1.1 | Only evidence-backed expansion of campaign/content or one progression/async experiment at a time. |
| 2+ | Exploration, economies, deeper progression, or more elements/heroes from the vision roster after separate design and data validation. |
| 3+ | PvP, alliances, territory conquest, trade, and live-service operations after fairness and operational gates. |

> **Vision vs. MVP:** `codex/heroes/ideation_codex.md` describes the full 10-element / 30-hero arc (the 10 Drakn
> sisters, their 10 bound heroes, their 10 Elder Dragons, introduced across generations Pokémon-style). The art
> phase proved we can *produce* art for all of it; the MVP ships a **subset of elements**, not the whole roster.
> The two are a staged timeline, not a contradiction — see the reconciliation plan for the open "which 3–4
> elements seed the MVP" decision.

## Data and tooling

- Runtime game data: `../data/`
- Machine-readable schemas: `../data/schemas/` (35 schema files currently present)
- Cards: `../data/cards/`
- Products/rewards: `../data/products/`
- Art-direction source + pipeline: `../data/art/` (see `../data/art/README.md`); generated prompts in `../prompts/`
- Validation and generation utilities: `../scripts/` and `../tools/`

When a game rule changes, follow: design rule → schema → validator/tooling → implementation
→ tests → high-level reference. Do not implement numeric behavior from the game bible.

## Governance and audit trail

- [Documentation/quality audit](AUDIT-DOCUMENTATION-QUALITY-BRANDING-JUL2026.md)
- [Documentation reset plan](working/documentation-reset-plan-jul2026.md)
- [Quality gates](QUALITY-GATES.md)
- [Change management](CHANGE-MANAGEMENT.md)
- [Archive index](archive/README.md)

## Readiness rule

Do not use "MVP ready" until the five readiness gates in the reconciliation document are
checked. The present plan is intentionally honest about unresolved data-subset and
cross-document work.
