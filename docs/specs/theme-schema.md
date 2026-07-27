# Theme Schema — card synergies and bonuses

This document explains the theme schema for deck-building synergies.

## Key Fields

- `themeId`, `name`, `description` — Identifiers.
- `requiredTags` — Card tags for theme membership.
- `thresholds` — Count requirements and bonuses.
- `visualTheme` — Aesthetic (Norse, etc.).

## Mechanics

- Bonuses activate at card counts.
- Multipliers stack with other effects.
- Encourages themed deck-building.

## Engine Integration

- Server checks deck composition; applies bonuses.
- Client shows theme progress.
