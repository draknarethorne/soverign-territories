# Tactic Schema — AI behavior modules

This document explains the tactic schema for programmable auto-battle AI.

## Key Fields

- `tacticId`, `name`, `description` — Identifiers.
- `targetType` — Hero, unit, or stack attachment.
- `priorityRules` — Conditions, actions, weights for AI decisions.
- `movementBehavior` — Aggressive, defensive, etc.
- `targetingPreferences` — Preferred targets.
- `unlocksAtLevel` — Progression gating.

## Mechanics

- Attach to stacks for auto-battle.
- Rules override default AI.
- Weights determine action priority.

## Engine Integration

- Server simulates AI; client previews.
- Events: Tactic usage logged for balance.