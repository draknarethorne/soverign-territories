Ability Schema — notes and examples

Purpose
- Define abilities as discrete effects with targeting, durations, cooldowns, and visual metadata. Abilities are referenced by cards via `abilities`.

Core concepts
- `abilityId`, `name`, `description`, `cooldown`.
- `effects`: array of effect objects (e.g., damage, heal, buff, debuff) with typed parameters.
- `targeting`: rules to compute affected units/tiles (single, cone, radius, line), must map to engine tile-enumeration utilities.

Example ability (single-target heal):

```json
{
  "abilityId": "abl-heal-01",
  "name": "Minor Heal",
  "description": "Heals a friendly stack within 2 tiles for 20 HP.",
  "cooldown": 3,
  "effects": [ { "type": "heal", "amount": 20 } ],
  "targeting": { "type": "tileRadius", "range": 2, "allyOnly": true },
  "schemaVersion": 1
}
```

Notes for engine implementers
- Ability resolution should be deterministic and server-side. Include event logs for each effect for replay and debugging.
- Effects may reference `statusIds` for buff/debuff lifecycles; store durations and unique instance IDs for expiry.

Effect Typing and Resolution Order
- Effect types defined in `effect-types.md`.
- Resolution order: Targeting → Pre-Effects → Damage/Heal → Status → Post-Effects.
- Example: Fireball applies damage then burn status.
- Engine: Server validates targeting; applies effects in order.
