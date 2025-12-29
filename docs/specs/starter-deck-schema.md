# Starter Deck Schema — pre-built decks

This document explains the starter deck schema for beginner onboarding.

## Key Fields

- `starterDeckId`, `name`, `description` — Identifiers.
- `theme`, `difficulty` — Categorization.
- `cards` — Fixed card list.
- `unlocksAtLevel` — Progression gating.

## Mechanics

- Provided to new players.
- Can be customized after unlocking.
- Teaches game mechanics.

## Engine Integration

- Server provides decks; client loads.
- Events: Unlocks trigger tutorials.