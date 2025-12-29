Map Schema — notes and examples

Intent
- The map schema models coordinate systems, tiles, ownership, and production. Use the JSON schema for storage and transport.

Coordinate systems
- `square` maps use `{x,y}` integers.
- `hex` maps use axial `{q,r}` coordinates. Provide conversion helpers to cube coordinates on the server.

Tile responsibilities
- Each tile contains `terrain`, `terrainModifiers` (e.g., moveCost), `structures` (building instances), `deployedStacks`, and `production` state.
- `visibility` is per-player; server computes fog-of-war and publishes deltas.

Pathfinding
- Server runs A* using per-tile `moveCost`. `moveRange` for units is the total movement budget per turn.
- Clients can run the same algorithm for prediction but must reconcile with server authoritative moves.

Examples
- See `map-schema.json` for structure. Typical API flows:
  - `placeStructure(mapId, coord, cardInstanceId)`
  - `moveStack(stackId, path)` — server validates path cost <= `moveRange`.

Scaling notes
- Store tiles as a compact keyed collection (e.g., `mapId:tiles` map). Diff updates are preferred over full map sends.
