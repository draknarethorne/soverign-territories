# Equipment Schema — hero gear and boosts

This document explains the equipment schema for hero customization.

## Key Fields

- `equipmentId`, `name`, `description` — Identifiers.
- `slot` — Weapon, armor, etc.
- `rarity` — Common to legendary.
- `stats` — Attack, defense, etc. bonuses.
- `abilities` — Granted abilities.
- `visualEffect` — Appearance on figurine.

## Mechanics

- Socket-compatible with heroes.
- Acquired from packs/events.
- Permanent or temporary attachments.

## Engine Integration

- Server validates compatibility; client displays visuals.
- Events: Equipment changes trigger updates.