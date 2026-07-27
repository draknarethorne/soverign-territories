# MVP Architecture Reassessment (July 2026)

**Date**: 2026-07-27  
**Purpose**: Full step-back review before engineering start, using current repo state + independent feedback + solo-dev reality.

---

## Executive conclusion

Sovereign Territories has a strong long-term vision, but implementation documents drifted into overlapping and contradictory assumptions.

This reassessment sets a **build-safe baseline**:

- Keep the long-term vision intact.
- Narrow MVP to the minimum strategic core loop.
- Resolve simple contradictions immediately.
- Flag major post-MVP decisions explicitly (instead of accidental scope creep).

---

## Baseline decisions (effective now)

### 1) MVP scope baseline

MVP must prove:

1. Card acquisition loop (packs + rewards)
2. Deck construction/validation
3. Deterministic 8x8 tactical battles
4. Linear PvE campaign progression
5. Foundational progression (player level + card rank-up)

**Not required for MVP completion** (can move to Phase 1.1):

- Async Arena PvP
- Scroll crafting
- Battle pass / VIP-style systems
- Territory/World strategic conquest layers

### 2) Combat baseline

MVP combat uses:

- HP/Mana/Attack/Defense
- Deterministic damage (`ATK - DEF`, min 1)
- No elemental counters in MVP
- No crit RNG in MVP

### 3) Deck/hero baseline

MVP deck model:

- One active battle formation of 6 units/cards
- **Single-hero limit in MVP** (hero + support units)
- Rarity budget enforced by canonical progression rules

Multi-hero builds remain a post-MVP expansion axis.

### 4) Canonical ownership

- Vision/narrative: `docs/game-bible.md`
- MVP schedule authority: `docs/mvp/solo-dev-realistic-mvp.md`
- MVP decomposition template: `docs/mvp/mvp-scope-final.md`
- Combat formulas: `docs/design/combat-calculation-spec.md`
- Deck/progression constraints: `docs/design/deck-progression-rules.md`
- Data contracts: `docs/specs/*.json`

---

## Discrepancies found and disposition

## A) Combat contradictions (FIX NOW)

### Issue A: Conflicting MVP combat rules

`docs/design/combat-calculation-spec.md` simultaneously claimed:

- MVP uses HP/Mana/ATK/DEF, and
- MVP uses one-hit removal + no HP tracking, and
- MVP has flat crit RNG.

### Decision A: Deterministic HP-based MVP combat

Adopt deterministic HP-based MVP combat with **no crit RNG** and **no elemental counters**.

---

## B) Progression and budget inconsistencies (FIX NOW)

### Issue B: Inconsistent rarity-point math

Rarity point costs and deck examples drifted (notably Uncommon cost and examples using conflicting totals).

### Decision B: Standardize rarity-point ladder

Standardize rarity points to:

- Common 1
- Uncommon 2
- Rare 4
- Epic 8
- Legendary 16
- Mythic 32

Refresh example math and keep one canonical formula source.

---

## C) Hero model drift (FIX NOW)

### Issue C: MVP hero model drift

Some docs promote multi-hero MVP while others imply single-hero identity and simpler balancing.

### Decision C: Single-hero MVP baseline

MVP = single-hero deck identity. Multi-hero = post-MVP expansion.

---

## D) MVP feature creep (FIX NOW)

### Issue D: MVP scope creep in planning doc

`mvp-scope-final.md` marked crafting + async arena as MVP-critical, while realistic planning treats these as deferable if timeline pressure occurs.

### Decision D: Reclassify stretch features

Reclassify these as Phase 1.1 / stretch unless core loop delivery is ahead of schedule.

---

## E) Monetization/tone mismatch (FIX NOW where simple)

### Issue E: Monetization tone conflict

Several sections use aggressive framing that conflicts with player-respect positioning.

### Decision E: Player-respect language baseline

Normalize language and policy framing:

- mechanical fairness first
- cosmetics/convenience over power
- avoid exploitative framing in core philosophy docs

---

## F) Map strategy ambiguity (FIX NOW in planning docs)

### Issue F: Map complexity ambiguity

Some sections imply explorable Realm-map complexity as MVP default while other docs describe simpler linear campaign progression.

### Decision F: Linear campaign baseline for MVP

Baseline MVP campaign as linear battle progression with lightweight map presentation; advanced map layers remain Phase 2-3.

---

## Major decisions still open (DECIDE LATER, non-blocking MVP)

1. Exact Phase 2 elemental multipliers (1.25 vs 1.5 etc)
2. Socket counts and late-game RPG stat scaling
3. Territory control buff magnitudes at large scale
4. Long-term monetization packaging specifics (Battle Pass depth, cadence)
5. Final async PvP ranking economy and season reset policy

These should be captured as Phase 2+ design gates, not solved during MVP engineering kickoff.

---

## Engineering kickoff guidance

Before coding sprints start:

1. Freeze MVP baseline above.
2. Keep all non-baseline ideas in Phase 1.1+ backlog.
3. Enforce schema-first change flow:
   - design rule -> schema -> tool/script -> implementation.
4. Require each implementation task to cite canonical doc path.

---

## Success criteria for this reassessment

- No contradictory MVP combat model across canonical docs.
- No contradictory deck budget/rarity math in canonical docs.
- MVP timeline and scope read consistently in docs hub and MVP planning docs.
- Major post-MVP decisions are visible as deliberate gates, not hidden drift.
