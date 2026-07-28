# Sovereign Territories — Feasible Solo-Developer MVP

**Last updated:** July 2026
**Authority:** MVP scope, schedule, and go/no-go decisions
**Audience:** Part-time first-game solo developer (about 10–15 hours/week)

## Purpose

This document protects the smallest version of Sovereign Territories that can prove its core promise: collect a few cards, form a legal party, solve readable tactical PvE battles, and earn a meaningful reward. It does not attempt to ship the full live-service strategy game.

The long-term vision remains card-driven territorial conquest. It becomes eligible only after this baseline is playtested and passes its decision gate.

## MVP definition

### Required baseline

1. A compact, validated local card set and one starter collection.
2. Pack/reward grant and a collection view sufficient to understand owned cards.
3. Deck validation and a six-card battle formation with **exactly one hero**.
4. Deterministic 8×8, turn-based PvE combat using HP, Mana, ATK, and DEF.
5. A short linear campaign of hand-authored encounters with a small tutorial layer.
6. Local save/load, basic reward progression, and feedback instrumentation.

### Explicitly not required

These features are Phase 1.1 or later, even if existing data or designs mention them:

- card fusion, equipment, persistent injury/Temple healing, crafting, or broad Codex/achievement systems;
- async or live PvP, leaderboards, matchmaking, alliances, chat, trading, or backend accounts;
- map exploration, territory placement, AFK production, castle systems, and multi-hero formations;
- battle pass, VIP, IAP, timed events, and advanced store packages;
- elemental counters, terrain modifiers, critical-hit RNG, status effects, and complex auto-battle tactics.

## Content limits

| Area | MVP limit | Why |
| --- | --- | --- |
| Playable cards | 18–30 hand-balanced cards | Enough choices for replayable parties without a content-production project. |
| Starter collection | One prevalidated 20-card collection | Guarantees a legal formation and avoids randomized onboarding failures. |
| Active formation | Six cards: one hero plus five supports | Makes tactical readability and balance tractable. |
| Campaign | 8–12 authored encounters plus one boss | Tests learning, difficulty, rewards, and replay interest. |
| Maps | Static campaign/stage selection and 8×8 combat board | Avoids exploration, pathfinding, fog, and world-map work. |
| Platform | Windows development build first | Mobile/PC release targets follow only after the slice is stable. |

## Delivery plan: 16–24 weeks

| Milestone | Weeks | Acceptance outcome |
| --- | ---: | --- |
| Foundation | 1–4 | Load validated card data; inspect collection; persist a local profile. |
| Deck and battle slice | 5–9 | Build a legal one-hero formation; complete one deterministic battle manually. |
| Campaign loop | 10–14 | Play through 8–12 encounters; earn and spend basic rewards; save progress. |
| Onboarding and balance | 15–18 | A new tester reaches the first victory without developer help. |
| Playtest and hardening | 19–24 | Fix critical defects, document results, and make the Phase 1.1 decision. |

The schedule is capacity-based, not a promise of a public launch date. If a milestone slips, reduce content first; do not add systems to compensate.

## Combat and data rules

- Damage is `max(1, ATK - DEF)`.
- Cards survive until HP reaches zero.
- Mana limits explicitly authored abilities; basic attack costs no Mana.
- Elements are visual identity only; no counter multipliers in MVP.
- Combat contains no critical-hit RNG, terrain modifiers, or status effects.
- Exact combat and deck constraints are owned by `docs/design/combat-calculation-spec.md` and `docs/design/deck-progression-rules.md`.
- Runtime contracts live in `data/schemas/`; implementation must not treat prose as a data contract.

## Playtest decision gate

Run at least two small rounds with players unfamiliar with the design. Continue to Phase 1.1 only if evidence shows that players can understand the formation, finish the first battle, and voluntarily attempt more campaign encounters.

Track at minimum onboarding completion, voluntary campaign continuation, deck/turn-flow confusion, battle duration/loss rate, reported enjoyment, and any defect that blocks saving, battling, or receiving rewards.

### Phase 1.1 admission criteria

Add **one** stretch system at a time only after the baseline is stable and playtest data identifies a need:

1. improve campaign/card variety;
2. add a restrained progression feature such as fusion **or** crafting;
3. assess local asynchronous challenge before any online PvP;
4. add backend/IAP work only after a separate privacy, operations, and business plan.

## Risks and responses

| Risk | Response |
| --- | --- |
| Card/content volume grows | Keep the MVP subset small and reuse only validated data. |
| Tactical combat becomes complex | Cut abilities before adding systems; preserve readable move/attack decisions. |
| Unity learning slows progress | Build one vertical slice end-to-end before polishing any screen. |
| Data contracts diverge | Update design → `data/schemas/` → validators/tools → implementation, in that order. |
| Desire for the full map game returns | Record it in the phased vision; do not reopen MVP scope without replacing an existing requirement. |

## Readiness statement

This is a **planning baseline**, not an implementation-readiness claim. Readiness requires the reconciliation gates in `docs/working/archive-canon-reconciliation-jul2026.md`, a verified data subset, and agreement across the canonical MVP, combat, deck, and tutorial documents.
