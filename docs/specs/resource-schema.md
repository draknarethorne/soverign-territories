# Resource Schema — currencies and economy

This document explains the resource schema for managing player economies, including currencies, production, and storage.

## Key Fields

- `stamina`, `maxStamina` — Stamina for battles; recharges hourly.
- `gold` — Primary currency for purchases.
- `gems` — Premium currency from IAP.
- `sovereignTokens` — Rare for exclusives.
- `resources` — Object with food, water, lumber, ore.
- `resourceCaps` — Storage limits; excess decays.

## Production Mechanics

- AFK production from buildings: Rate = BaseRate * Level * TerrainBonus * Synergies.
- Storage: Warehouses increase caps; overflow reduces efficiency.

## Engine Integration

- Server tracks all transactions for auditability.
- Client syncs deltas; validates against caps.
- Events: Production ticks every hour; notifications for full storage.
