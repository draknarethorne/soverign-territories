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

Algorithms Integration
- Pathfinding uses A* as detailed in `algorithms.md`.
- AoE calculations for abilities use tile enumeration functions from `algorithms.md`.

Event Scripting
- Maps can have scripted events (e.g., random encounters, resource spawns).
- Events are defined in `eventSchema` array; triggered by time or player actions.
- Example: Resource node depletion after N harvests.
- Engine: Server manages event timers; clients receive event notifications.

Terrain Effects
- Hexes affect production and combat: Fertile (+food), Mountain (+ore), Forest (+defense/cover).
- Combat modifiers: Hills (+ranged attack), Rivers (movement penalty).
- Building synergies: Adjacent buildings boost output (e.g., Mill near Farm +50% food).

Building Placement Rules
- Limits per territory: Castle (3 buildings), Fort (1), Town (0).
- Terrain restrictions: Mines on mountains, Farms on plains.
- AFK Production: Buildings generate resources based on level and bonuses.
- Engine: Server validates placement; calculates production ticks.
