# Terminology Guide - Standardization Reference

**Last Updated**: December 30, 2025  
**Status**: Canonical reference for all Sovereign Territories documentation  
**Purpose**: Ensure consistent naming across game-bible.md, tutorial-flow.md, schemas, UI text

---

## Map Hierarchy (CRITICAL - Use Consistently)

### Tier 1: World Map
- **Map Name**: World Map (NOT "Global Map")
- **Tiles**: Territories (NOT "States" or "Provinces")
- **Tile Count**: 200-500 Territories
- **Purpose**: Alliance wars, 3-month seasons, server-wide events
- **Example Usage**: "The World Map displays 200 Territories controlled by alliances."

### Tier 2: Territory Map
- **Map Name**: Territory Map (NOT "State Map" or "Province Map")
- **Tiles**: Realms (NOT "Provinces" or "Counties")
- **Tile Count**: 50-100 Realms per Territory
- **Purpose**: 1-month campaigns, castle sieges, alliance coordination
- **Example Usage**: "Click Territory to zoom into Territory Map (50 Realms)."

### Tier 3: Realm Map
- **Map Name**: Realm Map (NOT "County Map" or "Province Map")
- **Tiles**: Locations (NOT "Tiles" or "Hexes")
- **Tile Count**: 20-40 Locations per Realm
- **Purpose**: HoMM-style exploration, PvE/PvP battles, resource gathering
- **Example Usage**: "The Realm Map contains 40 Locations (Towns, Dungeons, Treasure Nodes)."

### Tier 4: Battle Map
- **Map Name**: Battle Map (NOT "Combat Map" or "Tactical Map")
- **Tiles**: Hexes (8×8 grid)
- **Tile Count**: 64 hexes total
- **Purpose**: Turn-based tactical combat, unit placement, abilities
- **Example Usage**: "Deploy units on the Battle Map (8×8 hex grid)."

---

## Location Types (Realm Map)

### Town
- **Definition**: Small settlement, heals army instantly, safe zone (no battles)
- **Count**: 3-5 per Realm
- **Example Usage**: "Move to Town Location to heal your army to 100%."

### City
- **Definition**: Large settlement, heals army + equipment shop + RPG shops (Phase 2)
- **Count**: 1 per Realm (capital)
- **Example Usage**: "Cities unlock the Alchemist and Scribe shops (Phase 2)."

### Dungeon
- **Definition**: PvE battle location, Epic/Legendary loot, multi-stage encounters
- **Count**: 5-10 per Realm
- **Example Usage**: "Clear the Dungeon to earn a Legendary card."

### Mine
- **Definition**: Resource production location, place Worker card for Ore (Phase 2)
- **Count**: 2-5 per Realm
- **Example Usage**: "Deploy a Miner card at the Mine to produce 10 Ore/hour (Phase 2)."

### Ruins
- **Definition**: Ancient location, treasure nodes (Gold/Gems), one-time loot
- **Count**: 5-10 per Realm
- **Example Usage**: "Explore the Ruins to find 500 Gold and 50 Gems."

### Monster Spawn
- **Definition**: Random PvE encounter, Common → Mythic enemies, respawns daily
- **Count**: 10-20 per Realm
- **Example Usage**: "Monster Spawns contain Common → Rare enemies in starting Realms."

### Treasure Node
- **Definition**: Gold/Gems loot, no battle, one-time reward
- **Count**: 5-10 per Realm
- **Example Usage**: "Collect Treasure Node for 1,000 Gold (no battle required)."

### Empty Space
- **Definition**: No content, passable terrain, acts as buffer between important Locations
- **Count**: 10-20 per Realm
- **Example Usage**: "Empty Space hexes allow movement but have no rewards."

---

## Terrain Types (Realm Map)

### Plains
- **Definition**: Default terrain, 1 Movement Point per hex, no modifiers
- **Movement Cost**: 1 Movement Point
- **Battle Modifier**: None
- **Example Usage**: "Plains hexes are passable and cost 1 Movement Point."

### Forest
- **Definition**: Tree-covered terrain, 1 Movement Point per hex, +10% Evasion (Phase 3)
- **Movement Cost**: 1 Movement Point
- **Battle Modifier** (Phase 3): +10% Evasion for units on Forest hexes
- **Example Usage**: "Forests provide +10% Evasion in battles (Phase 3)."

### Mountain
- **Definition**: Impassable terrain (blocks movement), acts as natural barrier
- **Movement Cost**: IMPASSABLE (unless unit has Flying ability)
- **Battle Modifier** (Phase 3): +20% Defense if somehow passable
- **Example Usage**: "Mountains block movement unless your units have Flying."

### Water
- **Definition**: Impassable terrain (blocks movement), acts as natural barrier
- **Movement Cost**: IMPASSABLE (unless unit has Swimming/Flying)
- **Battle Modifier** (Phase 3): -20% Movement (2 Stamina per hex if passable)
- **Example Usage**: "Water hexes are impassable unless you have Swimming or Flying units."

---

## Player Title (CRITICAL - Use Consistently)

### "Sovereign" (Preferred)
- **Usage**: All design documents, game bible, tutorial flow, UI text
- **Capitalization**: Always capitalize ("Sovereign", not "sovereign")
- **Example**: "The Sovereign controls multiple Realms across the World Map."

### "Player" (Avoid in Design Docs)
- **Usage**: Code comments, technical documentation ONLY
- **Example**: `// Player class stores Sovereign's deck data`
- **Never in UI**: Don't show "player" to users, always use "Sovereign"

### "Lord" / "Commander" / "General" (Avoid)
- **Reason**: Too generic (every strategy game uses these)
- **Exception**: Flavor text in card descriptions ("Lord of Flames" as hero title, not player title)

---

## Occupation Terminology

### Occupy Location
- **Definition**: Win battle at Location on Realm Map → Location becomes owned
- **Example**: "Occupy the Dungeon Location to earn +1% Gold production (Phase 2)."

### Control Realm
- **Definition**: Occupy all Locations in Realm (20-40 battles) → Realm becomes controlled
- **Example**: "Control the Realm by occupying all 40 Locations (+5% Power bonus)."

### Dominate Territory
- **Definition**: Control all Realms in Territory (50-100 castle sieges) → Territory becomes dominated
- **Example**: "Your alliance Dominates the Territory (+100% Power to all members)."

### Rule World
- **Definition**: Dominate all Territories on World Map → Alliance victory, season rewards
- **Example**: "The winning alliance Rules the World for 3 months (exclusive Mythic rewards)."

---

## Currency Names

### Gold (Soft Currency)
- **Display**: Gold (with coin icon)
- **Earning**: Battle rewards, daily login, battle chests
- **Spending**: Packs, Potions, Scrolls, Card Combining (cannot buy with real money)
- **Example**: "Buy a Standard Pack for 1,000 Gold."

### Gems (Premium Currency)
- **Display**: Gems (with gem icon)
- **Earning**: Daily login (10/day F2P), purchases ($0.99-$19.99)
- **Spending**: Premium Packs, Energy Refills, Speed-Ups (Phase 2)
- **Example**: "Buy a Premium Pack for 100 Gems (10% shiny rate)."

### Food (Resource Currency, Phase 2)
- **Display**: Food (with wheat icon)
- **Earning**: Granary buildings (10-50 Food/hour), battle chests
- **Spending**: Battle entry, deployment, upgrades
- **Example**: "Deploy a Granary on Location to produce 10 Food/hour (Phase 2)."

### Lumber (Resource Currency, Phase 2)
- **Display**: Lumber (with wood log icon)
- **Earning**: Sawmill buildings (10-50 Lumber/hour), battle chests
- **Spending**: Equipment crafting, construction, upgrades
- **Example**: "Craft a Wooden Shield for 100 Lumber (Phase 2)."

### Ore (Resource Currency, Phase 2)
- **Display**: Ore (with metal ore icon)
- **Earning**: Mine buildings (5-25 Ore/hour), battle chests
- **Spending**: High-tier equipment, upgrades, card combining
- **Example**: "Craft an Iron Sword for 200 Ore (Phase 2)."

### Energy (Stamina Currency)
- **Display**: Energy (with lightning bolt icon)
- **Earning**: Natural refill (1 per 6 minutes = 240/day), starting 100
- **Spending**: Battle entry (10 Energy per battle)
- **Example**: "You have 100/340 Energy (can fight 10 battles today)."

### Movement Points (Movement Currency)
- **Display**: Movement Points (with boot icon)
- **Earning**: Daily refill (10 Movement Points at midnight)
- **Spending**: Realm Map movement (1 Movement Point per hex)
- **Example**: "You have 7/10 Movement Points (can move 7 hexes today)."

### Arena Tokens (PvP Currency, Phase 3)
- **Display**: Arena Tokens (with sword icon)
- **Earning**: PvP wins (10 Tokens), PvP losses (2 Tokens)
- **Spending**: PvP Store exclusive cards/equipment
- **Example**: "Buy a PvP-exclusive Legendary card for 5,000 Arena Tokens."

---

## Card Types

### Hero
- **Definition**: Powerful leader unit, unique abilities, 1 per deck limit
- **Example**: "Flame Warlord (Epic Hero, Fire element, 40 Attack, 15 Defense)."

### Unit
- **Definition**: Standard combat card, can have multiple in deck
- **Example**: "Goblin Raider (Common Unit, 10 Attack, 5 Defense)."

### Building
- **Definition**: Economy or military structure, placed on Locations (Phase 2)
- **Example**: "Granary (Common Building, produces 10 Food/hour)."

### Worker
- **Definition**: Resource production card, placed on Mines/Farms (Phase 2)
- **Example**: "Miner (Common Worker, produces 10 Ore/hour at Mine)."

### Tactic
- **Definition**: Single-use ability card, used in battle (MVP) or replaced by Scrolls (Phase 2)
- **Example**: "Fireball (Rare Tactic, 60 damage, 3-hex range)."

### Equipment
- **Definition**: Hero attachment card, +Attack/Defense/Health/Mana bonuses
- **Example**: "Iron Sword (Rare Equipment, +15 Attack, 1 socket)."

---

## Rarity Levels

### Common (1★)
- **Color**: White/Gray
- **Drop Rate**: 70% (Standard Pack)
- **Rarity Points**: 1 point
- **Example**: "Common Goblin Raider (1★, 10 Attack, 5 Defense)."

### Uncommon (1-2★)
- **Color**: Green
- **Drop Rate**: 20% (Standard Pack)
- **Rarity Points**: 2 points
- **Example**: "Uncommon Elven Archer (2★, 25 Attack, 10 Defense)."

### Rare (2-3★)
- **Color**: Blue
- **Drop Rate**: 8% (Standard Pack)
- **Rarity Points**: 4 points
- **Example**: "Rare Fire Mage (3★, 40 Attack, 15 Defense)."

### Epic (3-4★)
- **Color**: Purple
- **Drop Rate**: 1.5% (Standard Pack), guaranteed in Epic Booster
- **Rarity Points**: 8 points
- **Example**: "Epic Flame Warlord (4★ Hero, 50 Attack, 20 Defense)."

### Legendary (5★)
- **Color**: Orange/Gold
- **Drop Rate**: 0.5% (Standard Pack), guaranteed every 50 packs (pity)
- **Rarity Points**: 16 points
- **Example**: "Legendary Dragon Knight (5★ Hero, 70 Attack, 30 Defense)."

### Mythic (6★)
- **Color**: Rainbow/Prismatic
- **Drop Rate**: 0.1% (Standard Pack), boss drops only
- **Rarity Points**: 32 points
- **Example**: "Mythic Phoenix Lord (6★ Hero, 100 Attack, 50 Defense, resurrection ability)."

---

## Element Names

### Fire
- **Color**: Red/Orange
- **Advantage**: Fire > Earth (+50% damage, Phase 3)
- **Weakness**: Water > Fire (+50% damage to Fire, Phase 3)
- **Example**: "Fire Mage (Fire element, strong vs Earth, weak vs Water)."

### Water
- **Color**: Blue/Cyan
- **Advantage**: Water > Fire (+50% damage, Phase 3)
- **Weakness**: Earth > Water (+50% damage to Water, Phase 3)
- **Example**: "Water Elemental (Water element, strong vs Fire, weak vs Earth)."

### Earth
- **Color**: Green/Brown
- **Advantage**: Earth > Water (+50% damage, Phase 3)
- **Weakness**: Fire > Earth (+50% damage to Earth, Phase 3)
- **Example**: "Stone Golem (Earth element, strong vs Water, weak vs Fire)."

### Lightning (Neutral, Phase 2)
- **Color**: Yellow/Electric Blue
- **Advantage**: None (neutral damage)
- **Weakness**: None (no weakness)
- **Example**: "Lightning Assassin (Lightning element, neutral to all)."

### Holy (Neutral, Phase 2)
- **Color**: White/Gold
- **Advantage**: None (neutral damage)
- **Weakness**: None (no weakness)
- **Example**: "Cleric (Holy element, healing abilities)."

### Shadow (Neutral, Phase 2)
- **Color**: Black/Purple
- **Advantage**: None (neutral damage)
- **Weakness**: None (no weakness)
- **Example**: "Shadow Assassin (Shadow element, stealth abilities)."

---

## Battle Terminology

### Manual Combat
- **Definition**: Sovereign controls units directly (drag-to-move, click-to-attack)
- **Example**: "Play in Manual Combat to learn formations and tactics."

### Auto-Battle
- **Definition**: AI plays both sides, instant resolve or speed controls (1×/2×/4×)
- **Example**: "Use Auto-Battle to skip tutorial battles (instant resolve)."

### Deployment Zone
- **Definition**: Top 2 rows of Battle Map (Sovereign's starting area)
- **Example**: "Place units in the Deployment Zone before battle starts."

### Victory Condition
- **Definition**: Eliminate all enemy units OR time limit (20 turns, defender wins if draw)
- **Example**: "Win the battle by eliminating all Goblin Raiders."

### Battle Chest
- **Definition**: Loot container earned after battle (Bronze/Silver/Gold/Platinum tiers)
- **Example**: "Open Bronze Battle Chest for 50 Gold and 1× Common card."

---

## Schema File Naming (For Developers)

### Map Schemas
- `world-map-schema.json` (NOT global-map-schema.json)
- `territory-map-schema.json` (NOT state-map-schema.json)
- `realm-map-schema.json` (NOT county-map-schema.json)
- `battle-map-schema.json`

### Location Schemas
- `location-schema.json` (Town, City, Dungeon, Mine, Ruins, Monster Spawn, Treasure Node)
- `occupation-schema.json` (Location/Realm/Territory ownership)

### Economy Schemas
- `currency-schema.json` (Gold, Gems, Food, Lumber, Ore, Energy, Movement Points)
- `economy-node-schema.json` (Granary, Sawmill, Mine production buildings - Phase 2)
- `treasure-node-schema.json` (Gold/Gems loot nodes)

### Combat Schemas
- `card-schema.json` (Hero, Unit, Building, Worker, Tactic, Equipment)
- `card-stats-schema.json` (Health/Mana/Stamina for Phase 2)
- `battle-chest-schema.json` (Bronze/Silver/Gold/Platinum loot tables)

### Progression Schemas
- `sovereign-progression-schema.json` (Player leveling, Location/Realm/Territory buffs)
- `pack-schema.json` (Standard/Element/Epic/Premium Packs)

### RPG Schemas (Phase 2)
- `consumable-schema.json` (Potions, Scrolls)
- `shop-schema.json` (Alchemist, Scribe, Jeweler)
- `socket-schema.json` (Jewel/Rune slots, Diablo-style)

---

## Common Mistakes to Avoid

### ❌ Incorrect: "Global Map"
- ✅ Correct: "World Map"

### ❌ Incorrect: "State Map" or "Province Map"
- ✅ Correct: "Territory Map"

### ❌ Incorrect: "County Map"
- ✅ Correct: "Realm Map"

### ❌ Incorrect: "player controls the map"
- ✅ Correct: "Sovereign controls the map"

### ❌ Incorrect: "Capture Location"
- ✅ Correct: "Occupy Location"

### ❌ Incorrect: "Own Realm"
- ✅ Correct: "Control Realm"

### ❌ Incorrect: "Conquer Territory"
- ✅ Correct: "Dominate Territory"

### ❌ Incorrect: "tile" (when referring to Realm Map hexes)
- ✅ Correct: "Location" (Realm Map), "hex" (Battle Map)

### ❌ Incorrect: "county-map-schema.json"
- ✅ Correct: "realm-map-schema.json"

---

## Quick Reference Table

| Concept | Correct Term | Avoid |
|---------|-------------|-------|
| Player | Sovereign | player, lord, commander |
| Tier 1 Map | World Map | Global Map |
| Tier 1 Tiles | Territories | States, Provinces |
| Tier 2 Map | Territory Map | State Map, Province Map |
| Tier 2 Tiles | Realms | Provinces, Counties |
| Tier 3 Map | Realm Map | County Map, Province Map |
| Tier 3 Tiles | Locations | tiles, hexes |
| Tier 4 Map | Battle Map | Combat Map, Tactical Map |
| Tier 4 Tiles | hexes | tiles, squares |
| Acquire Location | Occupy Location | capture, take, claim |
| Acquire Realm | Control Realm | own, capture, occupy |
| Acquire Territory | Dominate Territory | conquer, own, control |
| Soft Currency | Gold | gold, coins |
| Hard Currency | Gems | gems, crystals, premium currency |
| Stamina | Energy | stamina, AP, action points |
| Movement | Movement Points | movement, MP, steps |

---

**Use this guide when**:
- Writing game bible sections
- Creating tutorial text
- Naming JSON schemas
- Writing UI text
- Reviewing design documents
- Onboarding new team members

**For implementation details, see**:
- [game-bible.md](game-bible.md)
- [tutorial-flow.md](tutorial-flow.md)
- [map-tier-progression.md](map-tier-progression.md)
- [mvp-scope-final.md](mvp-scope-final.md)
