# Sovereign Territories — Game Bible

**Version:** July 2026 reset
**Role:** Long-term vision and player-experience guardrails
**Implementation authority:** MVP details belong to `docs/mvp/`, rule details to `docs/design/`, and runtime contracts to `data/schemas/`.

## The promise

**MVP tagline:** *Build the Deck. Conquer the Campaign. Level Your Heroes.*
**Future vision:** *Build the Deck. Rule the Map. Automate the Empire.*

Sovereign Territories is a card-driven strategy game. Players collect a themed roster,
shape it into a tactical formation, win readable battles, and—only after that foundation
works—expand into a living world of territorial control and long-term empire choices.

The game should combine the collector satisfaction of a card game, the tactical clarity of
turn-based battles, and the strategic aspiration of grand-map conquest without asking
players to perform repetitive, coercive, or opaque chores.

## Core pillars

1. **Strategic clarity** — visible information, deterministic early combat, and choices
   that can be understood before they are made.
2. **Collector identity** — cards have distinctive visual themes and roles, while roster
   growth creates new tactical options rather than mandatory power purchases.
3. **Respect for player time** — short, complete sessions; no dependence on forced
   check-ins, loss aversion, social pressure, or punitive streak design.
4. **Fair competition** — competitive systems, if added, must protect skill expression,
   collection fairness, and player safety.
5. **Phased ambition** — maps, economies, social systems, and live operations are earned
   through validated player value, not assumed as MVP requirements.

## MVP: prove the tactical loop

The MVP is a local-first, single-player vertical slice:

- a small, validated card collection and starter deck;
- one six-card formation with exactly one hero;
- deterministic HP/Mana/ATK/DEF combat on an 8×8 board;
- a short authored linear PvE campaign;
- basic rewards, progress saving, and a concise learn-by-doing onboarding path.

Elements establish visual and thematic identity in the MVP. They do not create damage
multipliers. There are no critical hits, terrain modifiers, persistent injuries, map
occupation, multi-hero formations, PvP, alliances, crafting, economy deployment, or
live-service monetization requirements in the MVP.

`docs/mvp/solo-dev-realistic-mvp.md` is the scheduling and scope authority. If this
vision conflicts with it on implementation work, the MVP document wins.

## Player experience

### Collection and deck identity

Cards are the player's strategic vocabulary. A new player receives a stable, legal
starter collection rather than being blocked by random acquisition. The game teaches
players how to choose a hero and five support cards, then lets combat demonstrate why
positioning and card roles matter.

Visual identity can use elemental colors, rarity treatment, portraits, and faction
motifs. Mechanical rarity and progression rules must be kept in the dedicated deck
specification so visual excitement does not hide balance rules.

### Tactical combat

Battlefields are compact 8×8 square grids. Players make legible movement, targeting,
and limited ability decisions. In the first release, a visible state and the same action
sequence produce the same outcome. This supports learning, tuning, accessibility, and
reliable playtest feedback.

### Campaign

The first campaign is a sequence of authored encounters with lightweight stage framing.
It introduces collection, formation, basic combat, rewards, and a boss—not a world map
simulation. Narrative and art should make a small campaign feel like a place without
requiring exploration, pathfinding, fog-of-war, or territorial systems.

## Long-term vision

The following systems are valuable expansion directions, but they are not promises of a
specific date, economy number, or server scale.

### Phase 1.1 — deepen a proven loop

Possible additions, admitted one at a time after playtest evidence:

- more campaign content and card variety;
- a carefully balanced progression feature such as fusion or crafting;
- optional local asynchronous challenge;
- expanded accessibility, analytics, or platform support.

### Phase 2 — strategic expansion

If the campaign loop is retained and the content pipeline is sustainable, Phase 2 may
introduce a small exploration or economy prototype, deeper card customization, and
carefully specified elemental or terrain mechanics. Each system needs a standalone
balance model and data contract before production.

### Phase 3+ — social conquest

Territorial maps, AFK empire management, trade, alliances, ranked competition, and
seasonal wars are the long-term Sovereign Territories fantasy. They require moderation,
anti-cheat, privacy, live operations, backend capacity, and anti-pay-to-win design. They
must be built as opt-in systems with safe alternatives for players who prefer PvE.

## Monetization and player trust

The MVP is judged on enjoyment and clarity, not monetization sophistication. Any future
business model must prefer cosmetics and optional convenience over combat power; state
odds and limits clearly; respect player privacy; avoid manipulative scarcity; and leave a
credible path for non-paying players to enjoy the core game.

No purchase, VIP status, or time-limited design should override fair combat or force
players into social obligation.

## Technical direction

Unity/C# is the intended client stack. The first slice is local-first and should minimize
external service dependencies. Nakama/PostgreSQL and real-time infrastructure are future
options when a defined online feature needs them, rather than MVP prerequisites.

Runtime data and schemas are stored in `data/`, especially `data/schemas/`. Documentation
explains intent; schemas, validators, and implementation enforce contracts.

## Governance

| Question | Canonical source |
| --- | --- |
| What can ship in MVP? | `docs/mvp/solo-dev-realistic-mvp.md` |
| What is the build order? | `docs/mvp/mvp-scope-final.md` |
| How does combat resolve? | `docs/design/combat-calculation-spec.md` |
| What makes a deck/formation legal? | `docs/design/deck-progression-rules.md` |
| How is the player introduced? | `docs/mvp/tutorial-flow.md` |
| What are future map and mode gates? | `docs/design/map-tier-progression.md`, `docs/design/gameplay-modes-spec.md` |
| What validates runtime data? | `data/schemas/*.json` |

## Feasibility checkpoint

This vision is feasible only as staged work. The 16–24 week part-time MVP is feasible as
a contained tactical vertical slice; it is not feasible as a full card-service game with
100+ cards, 60+ stages, online PvP, AFK systems, maps, and social infrastructure. The
reconciliation report records the evidence and readiness gates:
`docs/working/archive-canon-reconciliation-jul2026.md`.
