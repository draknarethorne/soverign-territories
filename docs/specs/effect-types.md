# Effect Types and Resolution

This document details the types of effects abilities can apply, their resolution order, and how they interact with the game engine.

## Effect Categories

### Direct Effects

- **Damage**: Reduces health by calculated amount
- **Heal**: Increases health by calculated amount
- **Buff/Debuff**: Modifies stats (attack, defense, speed) temporarily

### Status Effects

- **Stun**: Prevents actions for duration
- **Poison**: Damage over time
- **Shield**: Absorbs damage

### Control Effects

- **Teleport**: Moves unit to new position
- **Summon**: Creates temporary unit
- **Transform**: Changes unit type temporarily

## Resolution Order

Effects resolve in this sequence to ensure deterministic outcomes:

1. **Targeting**: Validate targets based on ability rules
2. **Pre-Effects**: Apply buffs/debuffs that modify calculations
3. **Damage/Heal**: Calculate and apply primary effects
4. **Status Application**: Apply ongoing effects
5. **Post-Effects**: Trigger procs, cleanup

### Example Resolution

```json
{
  "ability": "Fireball",
  "target": "enemy_unit",
  "effects": [
    {"type": "damage", "value": 50, "element": "fire"},
    {"type": "status", "name": "burn", "duration": 3}
  ]
}
```

Resolution:

1. Check if target is valid (in range, not immune)
2. Apply elemental multiplier (fire vs target element)
3. Deal 50 * multiplier damage
4. Apply burn status (5 damage/turn for 3 turns)

## Stacking Rules

- **Buffs**: Stack additively unless specified otherwise
- **Debuffs**: Stack multiplicatively for percentages
- **Status**: Unique statuses overwrite; multiple instances extend duration

## Engine Integration

- **Server**: Validates and applies all effects
- **Client**: Predicts effects for responsiveness, corrects with server state
- **Persistence**: Effects stored in unit state, synced via Nakama
- **Events**: Effect application triggers game events for UI/animations