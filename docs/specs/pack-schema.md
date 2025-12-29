# Pack Schema — card packs and gacha

This document explains the pack schema for card acquisition mechanics.

## Key Fields

- `packId`, `name` — Identifiers.
- `cost` — Currency and amount.
- `contents` — Rarity probabilities and card pools.
- `guarantees` — Pity system for fairness.

## Mechanics

- Pity timers ensure legendaries.
- VFX for openings.
- Analytics for balance.

## Engine Integration

- Server handles pulls; client animates.
- Events: Pack purchases logged.