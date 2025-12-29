# Deployment Schema — tile deployments

This document explains the deployment schema for managing units and buildings on map tiles.

## Key Fields

- `deploymentId`, `tileId`, `playerId` — Identifiers.
- `deployedItems` — Array of heroes, units, buildings with stack sizes.
- `limits` — Max slots per tile type.

## Mechanics

- Limits based on territory level (castle: 3 buildings, etc.).
- Stacking: Units combine stats.
- Codex View: UI for managing deployments.

## Engine Integration

- Server enforces limits; client previews.
- Events: Deployments affect battles and production.