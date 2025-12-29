Card Schema — notes and examples

This document explains intent, key fields, and engine expectations for `card-schema.json`.

Key intent
- Cards are the canonical game assets. Server owns canonical instances; clients get sanitized views.
- The schema supports all card types: `hero`, `unit`, `building`, `tactic`, `equipment`.

Important fields and engine notes
- `id`, `name`, `type`, `rarity`, `level`, `schemaVersion` — required.
- `stats` — base stats used for stack math; server applies level multipliers.
- `attackType`, `attackRange`, `aoeRadius`, `attackSpeed` — determine targeting and resolution. All ranges are tile-based.
- `moveRange`, `moveType`, `movementCostModifiers` — used by pathfinding and movement validation.
- `abilities` — reference `ability-schema.json`; ability resolution occurs server-side.
- `production` — only for building cards; includes `resourceType` and `ratePerHour`.

Examples
- See `card-schema.json` for validation. Minimal example:

```json
{
  "id": "unit-archer-001",
  "name": "Field Archer",
  "type": "unit",
  "rarity": "common",
  "level": 1,
  "stats": { "attack": 8, "defense": 2, "hp": 30, "speed": 5 },
  "attackType": "ranged",
  "attackRange": 3,
  "moveRange": 2,
  "moveType": "walk",
  "stackSize": 5,
  "schemaVersion": 1
}
```

Edge cases
- `moveType: fly` should ignore tile `moveCost` but still respect `passable=false` tiles that are explicitly forbidden.
- Buildings with `durability` require separate repair endpoints; `durability` is distinct from unit HP.

Validation
- Use `ajv` to validate card payloads produced by the editor pipeline and server-side ingestion.
