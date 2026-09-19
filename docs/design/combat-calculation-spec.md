# Combat Calculation Specification

**Last updated:** July 2026
**Authority:** Combat rules for the MVP baseline
**Related:** `docs/mvp/solo-dev-realistic-mvp.md`, `docs/design/deck-progression-rules.md`, `data/schemas/battle-schema.json`

## MVP combat contract

MVP combat is deterministic, local-first, turn-based PvE on an 8×8 square grid. Its purpose is to test tactical positioning and clear card-role decisions without hidden randomness or system layering.

### Card combat fields

Each battle-capable card has:

- **HP**: current and maximum health; a card is defeated at zero HP;
- **Mana**: resource spent only by authored active abilities;
- **ATK**: offensive stat;
- **DEF**: flat mitigation stat;
- movement range, attack range, and a small authored ability set only where data supports it.

Buildings, workers, territory resources, and deployment systems are outside the MVP battle model.

## Damage resolution

For a standard attack:

$$
\operatorname{damage} = \max(1, \operatorname{ATK}_{attacker} - \operatorname{DEF}_{defender})
$$

Then:

$$
\operatorname{HP}_{new} = \max(0, \operatorname{HP}_{current} - \operatorname{damage})
$$

A defender is defeated when $\operatorname{HP}_{new}=0$.

### Example

An attacker with ATK 12 targets a defender with DEF 5 and 20 current HP:

- damage is `max(1, 12 - 5) = 7`;
- defender HP becomes `20 - 7 = 13`.

An attacker with ATK 4 targets DEF 5:

- damage is `max(1, 4 - 5) = 1`;
- the defender still loses one HP.

## Mana and abilities

- Basic attacks cost zero Mana, preventing deadlock.
- Active abilities may spend a fixed, data-authored Mana cost.
- An ability may not resolve if current Mana is lower than its cost.
- Ability effects must be deterministic in MVP: fixed damage, fixed heal, fixed range, or fixed duration.
- The first vertical slice should include only enough abilities to validate this rule; no generic effect engine is required before playtesting.

## Explicit MVP exclusions

The following systems must not change combat outcomes in MVP:

- elemental strengths, weaknesses, or same-element bonuses;
- critical hits, dodge, accuracy rolls, random targeting, or random loot;
- terrain modifiers, weather, line-of-sight special cases, status effects, and damage-over-time;
- stack mathematics, multi-hero armies, persistent injury, consumable healing, or resurrection;
- PvP brackets, Elo, matchmaking, server reconciliation, or auto-battle strategy programming.

Elements remain visual and thematic identity only. The same visible stats and actions must produce the same result regardless of element.

## Determinism requirements

For a given serialized battle state and input sequence, resolution must be reproducible. Implementations should record:

- encounter identifier and initial card state;
- turn/action sequence;
- deterministic result (damage, HP, Mana, defeat, victory/loss).

No random seed is needed until a later phase introduces a deliberately designed random system.

## Future design gates

| System | Earliest phase | Required design decision before implementation |
| --- | --- | --- |
| More abilities and tactical effects | 1.1 | Define effect vocabulary, targeting, UI, and balance limits. |
| Fusion/equipment/persistent health | 1.1+ | Prove the simple combat/reward loop first. |
| Elemental interactions and terrain | 2+ | Finalize the 10-element cycle chart (see below), publish multipliers/stacking/counterplay, and rebalance the card set. |
| Status effects and critical RNG | 2+ | Define duration, cleanse, caps, accessibility, and deterministic replay behavior. |
| Async/live PvP | 1.1+ | Define authoritative backend, cheating model, matchmaking, and privacy/operations plan. |

## Elemental cycles — Phase 2 proposal (not MVP)

> **Status:** Proposed · elements are visual-only until this chart is finalized and the card
> set is rebalanced. The 10 elements are: Darkness, Fire, Grass, Ice, Water, Light, Earth,
> Lightning, Wind, Poison (plus Neutral for element-agnostic cards).

The current design intent groups the ten elements into strength/weakness relationships:

- **Duality** — **Light ⟷ Darkness**: mutual opposites, each strong against the other.
- **Primal triangle** — **Fire / Water / Earth**: a rock-paper-scissors cycle.
- **Storm quad** — **Ice / Lightning / Wind / Poison**: a four-element cycle.

**Open decisions before this becomes canonical**:

1. **Grass placement.** Grass is not yet in a cycle. Recommended option: fold Grass into the
   primal group to form a **Fire → Grass → Water → Earth → Fire** four-cycle (cleanly
   covering all four), or pair it opposite another element.
2. **Direction of the primal cycle.** Confirm who beats whom (e.g., Water > Fire > Earth >
   Water) and the exact multiplier (1.25× vs 1.5×).
3. **Structure of the storm group.** Confirm whether Ice/Lightning/Wind/Poison is a single
   4-cycle or two dual pairs.
4. **Neutral behavior.** Confirm Neutral deals/receives normal damage to all elements.

Until these are decided and the card set is rebalanced, MVP combat treats elements as
identity only.

## Data and implementation notes

The prose describes the rule intent. Runtime representation and validation are owned by `data/schemas/`, with any MVP subset verified before implementation. If the schema cannot express a required baseline field, update the design, schema, validator/tooling, and only then implementation.
