# Economy Node Schema

**Version**: 1.0  
**Last Updated**: December 30, 2025  
**Purpose**: Defines resource-generating nodes on maps for AFK progression (Phase 2+)

---

## Overview

Economy Nodes are **placeable resource generators** on the Realm Map and Territory Map. Players deploy Economy cards (Workers, Buildings) onto these nodes to produce Food, Lumber, or Ore passively while offline.

**Core Mechanic**: "Deploy once, collect periodically" - not tap-to-collect grind

**Phase**: Phase 2+ (not in MVP)

---

## Key Fields

### Identification
- **nodeId**: Unique identifier (e.g., `realm_farm_01`, `territory_mine_05`)
- **nodeType**: Type of resource node (`farm`, `lumber_mill`, `mine`, `quarry`, `fishing_spot`)
- **mapType**: Map tier where node exists (`realm`, `territory`, `world`)
- **coordinates**: `{ x: number, y: number }` - Tile position on map

### Resource Production
- **resourceType**: Type produced (`food`, `lumber`, `ore`)
- **baseRate**: Base production per hour (e.g., 30 Food/hour)
- **maxCapacity**: Maximum storage before collection required (e.g., 720 Food = 24 hours)
- **collectionInterval**: Minimum time between collections (e.g., 3600 seconds = 1 hour)

### Deployment
- **requiredCardType**: Card type allowed (`worker`, `building`, `both`)
- **requiredElement**: Optional element filter (e.g., `earth` for farms, `fire` for forges)
- **requiredLevel**: Minimum card level to deploy (1-30)
- **deploymentSlots**: Number of cards deployable (1-3 slots per node)

### State
- **isOccupied**: Boolean (true if player has card deployed)
- **occupyingPlayerId**: Player UUID who owns this node
- **deployedCards**: Array of card IDs currently deployed (max = deploymentSlots)
- **lastCollectionTime**: Unix timestamp of last resource collection
- **currentStoredAmount**: Current accumulated resources waiting for collection

---

## Mechanics

### Deployment Flow
1. **Player selects node** on Realm Map (map-schema.json)
2. **System validates**:
   - Node is not occupied OR player owns it
   - Player has eligible Economy card (Worker/Building matching node requirements)
   - Card meets level requirement
3. **Player deploys card** from Codex (not from battle deck - separate pool)
4. **Production starts** at `baseRate` per hour
5. **Resources accumulate** until `maxCapacity` reached (overflow wasted)

### Collection Flow
1. **Player taps node** (or "Collect All" button)
2. **System calculates**: `timeSinceLastCollection * baseRate` (capped at maxCapacity)
3. **Resources added** to player's global inventory (resource-schema.json)
4. **lastCollectionTime updated** to current time
5. **Production continues** (card remains deployed)

### Retrieval Flow
1. **Player removes card** from node (optional - can leave deployed indefinitely)
2. **Production stops** immediately
3. **Card returns** to Codex inactive pool
4. **Node becomes available** for other players (if not player-owned territory)

---

## Node Types

### Farm (Food Production)
- **resourceType**: `food`
- **baseRate**: 30 Food/hour (720 Food/day)
- **requiredCardType**: `worker` (Farmer, Peasant)
- **requiredElement**: `earth` (optional - Earth workers get +20% bonus)
- **deploymentSlots**: 1-2 (upgradeable with Building cards)

### Lumber Mill (Lumber Production)
- **resourceType**: `lumber`
- **baseRate**: 20 Lumber/hour (480 Lumber/day)
- **requiredCardType**: `worker` (Lumberjack, Axeman)
- **requiredElement**: None (all elements valid)
- **deploymentSlots**: 1-2

### Mine (Ore Production)
- **resourceType**: `ore`
- **baseRate**: 15 Ore/hour (360 Ore/day)
- **requiredCardType**: `worker` (Miner, Excavator)
- **requiredElement**: `earth` (optional - Earth workers get +30% bonus)
- **deploymentSlots**: 1 (Ore is scarcest resource)

### Quarry (Mixed Lumber/Ore)
- **resourceType**: `lumber` or `ore` (player chooses)
- **baseRate**: 10 Lumber/hour OR 8 Ore/hour
- **requiredCardType**: `worker`
- **deploymentSlots**: 2 (flexible resource choice)

### Fishing Spot (Food + Bonus)
- **resourceType**: `food`
- **baseRate**: 40 Food/hour (higher than Farm)
- **requiredCardType**: `worker` (Fisherman)
- **requiredElement**: `water` (required - Water-exclusive node)
- **deploymentSlots**: 1 (limited availability on map)

---

## Production Modifiers

### Card Rarity Bonuses
- **Common Worker**: +0% (base rate)
- **Uncommon Worker**: +10%
- **Rare Worker**: +25%
- **Epic Worker**: +50%
- **Legendary Worker**: +100%

**Example**: Epic Farmer on Farm node = 30 × 1.5 = 45 Food/hour

### Card Level Bonuses
- **Level 1-10**: +0-10% (1% per level)
- **Level 11-20**: +10-20%
- **Level 21-30**: +20-30%

**Example**: Level 20 Farmer = +20% bonus

### Element Synergy
- **Matching Element**: +20% (Earth worker on Farm)
- **Mismatched Element**: +0% (Fire worker on Farm - still works, no bonus)

### Building Upgrades (Phase 3)
- **Granary Building**: +1 deployment slot to Farm (allows 2 workers)
- **Sawmill Building**: Lumber Mill produces 25% faster
- **Forge Building**: Mine produces +5 Ore/hour flat bonus

---

## Capacity & Overflow

### Max Capacity Design
- **12-hour cap**: `baseRate × 12` (encourages 2× login/day)
- **24-hour cap**: `baseRate × 24` (casual-friendly, max 1× login/day)

**Current Design**: 24-hour cap (720 Food, 480 Lumber, 360 Ore)

**Overflow Behavior**:
- If player doesn't collect for >24 hours, excess production is **wasted** (not banked)
- Push notification at 80% capacity: "Your farm is almost full!"
- In-game banner at 100% capacity: "Collect resources now!"

---

## Ownership & Contention

### Owned Nodes (Player's Territory)
- **Private**: Only deploying player can use
- **Duration**: Permanent (until player loses territory in PvP)
- **No Contention**: Safe from other players

### Public Nodes (Neutral Territory)
- **First-Come-First-Served**: Any player can deploy
- **Duration**: Until player retrieves card OR territory claimed
- **Contention Risk**: If territory captured by enemy, node resets (cards returned to Codex)

### Contested Nodes (Active PvP Maps - Phase 3)
- **Timed Ownership**: Deploy for 1-hour sessions
- **PvP Flag**: Other players can challenge for node (battle to evict)
- **Risk/Reward**: Higher production rates (+50%) but dangerous

---

## Tutorial Integration

**Step 27** in [tutorial-flow.md](../mvp/tutorial-flow.md):
1. Player completes first Realm Map battle (Step 23)
2. Tutorial unlocks **1 Economy card** (Common Farmer)
3. Player taps **Farm node** on Realm Map (highlighted, glowing)
4. Tutorial guides: "Deploy your Farmer to generate Food while offline"
5. Player drags Farmer card onto node
6. Production starts (30 Food/hour)
7. Tutorial: "Come back in 4-8 hours to collect!"

**Post-Tutorial**:
- Players unlock more Economy cards from packs (10-15% of pack contents)
- Players discover more nodes on Realm Map (40 locations, ~10 Economy nodes)
- Players deploy multiple cards across multiple nodes
- Players upgrade cards to increase production rates

---

## Example JSON

### Farm Node (Realm Map)
```json
{
  "nodeId": "realm_farm_01",
  "nodeType": "farm",
  "mapType": "realm",
  "coordinates": { "x": 12, "y": 8 },
  "resourceType": "food",
  "baseRate": 30,
  "maxCapacity": 720,
  "collectionInterval": 3600,
  "requiredCardType": "worker",
  "requiredElement": "earth",
  "requiredLevel": 1,
  "deploymentSlots": 1,
  "isOccupied": true,
  "occupyingPlayerId": "player_12345",
  "deployedCards": ["farmer_common_lv5"],
  "lastCollectionTime": 1735587600,
  "currentStoredAmount": 120,
  "schemaVersion": 1
}
```

### Mine Node (Territory Map)
```json
{
  "nodeId": "territory_mine_05",
  "nodeType": "mine",
  "mapType": "territory",
  "coordinates": { "x": 25, "y": 15 },
  "resourceType": "ore",
  "baseRate": 15,
  "maxCapacity": 360,
  "collectionInterval": 3600,
  "requiredCardType": "worker",
  "requiredElement": null,
  "requiredLevel": 5,
  "deploymentSlots": 1,
  "isOccupied": false,
  "occupyingPlayerId": null,
  "deployedCards": [],
  "lastCollectionTime": null,
  "currentStoredAmount": 0,
  "schemaVersion": 1
}
```

---

## Engine Integration

### Server (Nakama)
- **Node State**: Store all Economy Nodes in database (per-map)
- **Production Calculation**: Server-authoritative (prevents time cheating)
- **Collection API**: `collectEconomyNode(nodeId)` → returns resource amount
- **Deployment API**: `deployCardToNode(nodeId, cardId)` → validates and deploys
- **Anti-Cheat**: Validate `lastCollectionTime` (prevent time travel exploits)

### Client (Unity)
- **Node Rendering**: Show nodes on Realm Map with resource icons (wheat, log, pickaxe)
- **Deployment UI**: Drag-and-drop Economy cards from Codex onto nodes
- **Collection UI**: "Collect All" button, individual node tap
- **Visual Feedback**: Glowing nodes when resources ready, progress bars for capacity

### Events
- **NodeDeployed**: Triggered when card deployed to node
- **ResourcesCollected**: Triggered when player collects (for analytics)
- **CapacityReached**: Triggered at 100% capacity (for notifications)
- **NodeContested**: Triggered if PvP player challenges (Phase 3)

---

## Validation Rules

**Required Fields**:
- nodeId, nodeType, mapType, coordinates, resourceType, baseRate, maxCapacity, requiredCardType, deploymentSlots, isOccupied, schemaVersion

**Constraints**:
- `baseRate` must be positive integer (1-100)
- `maxCapacity` must be >= baseRate × 12 (minimum 12-hour cap)
- `deploymentSlots` must be 1-3
- `requiredLevel` must be 1-30
- `currentStoredAmount` cannot exceed `maxCapacity`

**Cross-Schema Validation**:
- `deployedCards` must exist in card-schema.json
- `occupyingPlayerId` must exist in player-schema.json
- `resourceType` must match resource-schema.json types

---

## Design Notes

**Why AFK Progression?**
- Respects player time (no need to tap-collect every hour)
- Encourages daily login (24-hour cap)
- Creates strategic choice (deploy high-rarity cards for better rates vs save for battles)

**Why Resource Caps?**
- Prevents infinite accumulation (whales can't stockpile 100,000 Food)
- Balances F2P vs whale (everyone capped at 720 Food/day per node)
- Creates login rhythm (2× daily collection optimal)

**Why Node Ownership?**
- PvE-friendly (players keep nodes on Realm Map)
- PvP-exciting (contested nodes on Territory Map = risk/reward)
- Social (alliances can coordinate node control on World Map)

---

## Related Schemas

- **[card-schema.json](card-schema.json)** - Defines Worker/Building cards deployable to nodes
- **[resource-schema.json](resource-schema.json)** - Defines Food/Lumber/Ore inventory
- **[map-schema.json](map-schema.json)** - Defines Realm/Territory maps containing nodes
- **[deployment-schema.json](deployment-schema.json)** - General deployment rules (may overlap)
- **[tutorial-schema.json](tutorial-schema.json)** - Step 27 (Economy node deployment)

---

**Document Status**: Companion to economy-node-schema.json  
**Last Updated**: December 30, 2025  
**Maintained By**: @Soverign-Beast-Mode agent
