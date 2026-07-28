# Deck and Formation Rules

**Last updated:** July 2026
**Authority:** Deck legality, rarity costs, and MVP formation constraints
**Related:** `docs/mvp/solo-dev-realistic-mvp.md`, `docs/design/combat-calculation-spec.md`, `data/schemas/deck-schema.json`

## Scope

These rules define the MVP's collection-to-battle boundary. They intentionally avoid long-term player-level unlock schedules until the baseline has been tested.

## MVP formation

A player selects exactly six battle-capable cards for each encounter:

- exactly **one** hero;
- five support units;
- no buildings, workers, economy cards, or unattached tactics in the formation;
- each selected card must be owned and battle-legal.

The hero is a deck identity rule, not a promise that hero rarity makes a formation automatically stronger. Multi-hero formats are a future mode and must not be inferred from this document.

## Collection deck versus active formation

The starter collection/deck contains 20 cards. The active six-card formation is selected from that collection. The larger collection provides alternatives; it does not create a draw, reserve, persistent-health, or replacement system in MVP.

## Copy limit

No non-hero card ID may appear more than three times in a 20-card deck. A hero is limited to one copy by the single-hero rule.

Examples:

- `1 Hero + 3 Guards + 2 Archers + 14 other legal cards` is valid with respect to copies.
- `1 Hero + 4 Guards + 15 other cards` is invalid.
- A six-card formation can include at most three copies of a non-hero card and exactly one hero.

## Rarity costs

| Rarity | Cost |
| --- | ---: |
| Common | 1 |
| Uncommon | 2 |
| Rare | 4 |
| Epic | 8 |
| Legendary | 16 |
| Mythic | 32 |

The rarity budget is calculated as the sum of selected deck card costs. A 20-card MVP starter deck uses a **40-point budget**. This permits a clear starter hero and varied supports while preventing a full high-rarity deck.

### Valid starter example

| Cards | Cost each | Total |
| --- | ---: | ---: |
| 1 Epic hero | 8 | 8 |
| 2 Rare supports | 4 | 8 |
| 4 Uncommon supports | 2 | 8 |
| 16 Common supports | 1 | 16 |
| **20 cards total** |  | **40** |

This example follows the three-copy limit by using distinct support card IDs where a row quantity exceeds three.

### Formation check

The active formation is a legal subset of the saved deck. Its own rarity total is shown for player clarity but does not create a second budget unless a later mode explicitly defines one.

## Validation order

1. Verify deck has exactly 20 cards for the MVP starter format.
2. Verify exactly one hero.
3. Verify no non-hero card has more than three copies.
4. Verify all cards are battle-legal or otherwise correctly excluded.
5. Sum rarity costs and require a total at or below 40.
6. When starting a battle, verify the selected formation has exactly six cards, exactly one hero, and belongs to the legal deck.

## MVP progression

The MVP can grant cards and show player progress, but it does **not** need to unlock deck sizes, multi-hero formations, Arena, alliance systems, castles, or map modes. Card fusion and equipment are Phase 1.1 gates, not requirements for basic deck validation.

## Future design gates

| Topic | Earliest phase | Required decision |
| --- | --- | --- |
| Deck-size growth | 1.1 | Define content acquisition pace and a budget curve that preserves the copy limit. |
| Fusion/equipment | 1.1 | Define upgrade caps and acquisition economy after baseline balance data. |
| Multi-hero formats | 2+ | Define formation roles, budget trade-offs, and encounter balance. |
| Element synergies/counters | 2+ | Define rules in combat spec; elements have no mechanical MVP effect. |
| PvP/ranked budgets | 1.1+ | Define matchmaking and anti-pay-to-win rules from measured collection data. |

## Contract ownership

This file owns the human-readable rule. `data/schemas/deck-schema.json` and related card/trainer-deck schemas own the machine-readable contract. A rule change must update design, schema, validator/tooling, and tests together.
