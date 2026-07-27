# Deck Schema — battle and building decks

This document explains the deck schema for managing player card collections and formations.

## Key Fields

- `deckId`, `playerId` — Identifiers.
- `deckType` — Battle or building.
- `cards` — Array of cardId, quantity, level.
- `maxSlots` — Limit based on player level.
- `isActive` — Current deck in use.

## Mechanics

- Battle decks: For combat units/heroes.
- Building decks: For structures.
- Validation: Ensure card compatibility and slot limits.

## Engine Integration

- Server validates deck builds; client previews.
- Events: Deck saves persist; switching is instant.
