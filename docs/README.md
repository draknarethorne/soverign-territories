# Sovereign Territories Documentation

**MVP tagline:** *Build the Deck. Conquer the Campaign. Level Your Heroes.*
**Future vision:** *Build the Deck. Rule the Map. Automate the Empire.*

## Current status

Design and art are ahead of gameplay data; there is no Unity project yet. Starter decks,
packs, and manifests are out of sync with the current card set. [STATUS.md](STATUS.md) is
the single working document: current state, decisions made, open decisions, next work,
data debt, and the readiness gates.

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
7. [Project Status](STATUS.md) — what is true now, what is decided, what is next.

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
| How to create art and video | `art/tutorial-art.md`, `art/tutorial-video.md` | Step-by-step for writing and tuning the art and animation JSON, by hand or with an AI assistant. |
| ComfyUI workflows and launchers | `../workflows/README.md` | Workspaces (one home per set, temporary copies on request, `zz_` guards), the Qwen, FireRed and MiniMax engines, hand-curated workflows, the common commands and `../bin/*.cmd`. |
| Hero/dragon vision roster | `codex/heroes/sovereign_dawn_codex.md` | The 10-element / 30-hero long-horizon roster + the Sundering storyline (`SD-001` to `SD-030`). **Ideation-tier vision**, not MVP scope — a subset ships first. A roster, not the codex: the JSON wins. |
| Angel Primes roster and builds | `codex/heroes/angel_primes_codex.md`, `angel_primes_physique.md` | The 22 angels (a proposed exclusive `AP-001` to `AP-022` series): element, alignment, colours, and why each is built as they are. The art identities win. |
| Current state, decisions, backlog | `STATUS.md` | Wins on "what is done / open / next". Rules still live in the rows above. |
| Render QA | `art/output-qa-checklist.md` | Human check of rendered images (identity, anatomy, text, wardrobe). |
| Art packs, dynamic ComfyUI prompts | `art/art-packs-and-comfy-node-proposal.md` | Proposal: zip packs of art JSON and custom nodes on one shared prompt library. |

## Phases

| Phase | Approved focus |
| --- | --- |
| MVP | Local-first cards, a meaningful starter deck from **3–4 elements** (subset of the vision roster), deterministic 8×8 PvE, short linear campaign, save/reward loop. |
| 1.1 | Only evidence-backed expansion of campaign/content or one progression/async experiment at a time. |
| 2+ | Exploration, economies, deeper progression, or more elements/heroes from the vision roster after separate design and data validation. |
| 3+ | PvP, alliances, territory conquest, trade, and live-service operations after fairness and operational gates. |

> **Vision vs. MVP:** `codex/heroes/sovereign_dawn_codex.md` describes the full 10-element / 30-hero arc (the 10 Drakn
> sisters, their 10 bound heroes, their 10 Elder Dragons, introduced across generations Pokémon-style). The art
> phase proved we can *produce* art for all of it; the MVP ships a **subset of elements**, not the whole roster.
> The two are a staged timeline, not a contradiction — see the reconciliation plan for the open "which 3–4
> elements seed the MVP" decision.

## Data and tooling

- Runtime game data: `../data/`
- Machine-readable schemas: `../data/schemas/` (narrative notes for them in `specs/`)
- Cards: `../data/cards/`
- Products/rewards: `../data/products/`
- Art-direction source + pipeline: `../data/art/` (see `../data/art/README.md`); generated prompts in `../prompts/`
- Animation (video) source: `../data/animation/` (see `art/tutorial-video.md`); generated ComfyUI workflows in `../workflows/`
- Validation, generation and workflow utilities: `../tools/` (validators, generators, `workflows/comfy_workflows.py`); quick launchers in `../bin/`

When a game rule changes, follow: design rule → schema → validator/tooling → implementation
→ tests → high-level reference. Do not implement numeric behavior from the game bible.

## Governance and audit trail

- [Quality gates](QUALITY-GATES.md)
- [Change management](CHANGE-MANAGEMENT.md)
- [Release checklist](RELEASE-CHECKLIST.md)
- [Archive index](_archive/README.md)

## The `_archive` convention

Every archive folder in the repo is named `_archive` (`docs/_archive`, `data/_archive`, `prompts/_archive`, ...). It is a
recycle bin: content stays reachable without digging through git, until a later purge. Rules:

- Nothing under an `_archive` folder is current, and it is **not** read as documentation or data unless explicitly
  requested (assistants, searches, link checks, and validators skip it).
- Move superseded material there with `git mv`; do not edit it afterwards, and do not link to it from current docs.
- Active folders that start with an underscore (`data/art/_templates`, `_sets`, `_schema`) are **not** archives.

## Readiness rule

Do not use "MVP ready" until the readiness gates in [STATUS.md](STATUS.md) are checked.
