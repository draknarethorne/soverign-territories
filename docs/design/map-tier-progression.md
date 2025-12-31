# Map Tier Progression - Location → Realm → Territory → World

**Last Updated**: December 30, 2025  
**Status**: HIGH PRIORITY - Defines core map hierarchy, occupation mechanics, stat buffs  
**Related**: [game-bible.md](game-bible.md) Section 4, [mvp-scope-final.md](mvp-scope-final.md), [combat-calculation-spec.md](combat-calculation-spec.md)

---

## Overview

Sovereign Territories uses a **4-tier map hierarchy**:
1. **World Map** → Territories (200-500 tiles, alliance wars, 3-month seasons)
2. **Territory Map** → Realms (50-100 hexes, 1-month campaigns, castle sieges)
3. **Realm Map** → Locations (20-40 hexes, HoMM exploration, PvE/PvP battles) ← **MVP**
4. **Battle Map** → 8×8 tactical grid (turn-based combat, formations)

**Occupation Flow**:
- Occupy **Location** (single hex on Realm Map) → +1 Location buff
- Control **Realm** (entire Realm Map, 20-40 Locations) → +5-10% Power
- Dominate **Territory** (entire Territory Map, 50-100 Realms) → +50-100% Power
- Rule **World** (entire World Map, 200-500 Territories) → Alliance victory, season rewards

**Design Philosophy**: Start small (Location combat), scale up (Realm control), culminate in massive alliance wars (Territory domination). Each tier adds strategic depth (resource production → castle sieges → alliance coordination).

---

## Tier 4: Battle Map (8×8 Tactical Grid)

**Scope**: Individual combat encounter (1-5 minutes)

**Map Size**:
- 8×8 hex grid (64 tiles total)
- 4× deployment zone (player side, top 2 rows)
- 4× no-man's-land (middle 4 rows)
- 4× enemy zone (AI side, bottom 2 rows)

**Terrain** (MVP = Plains only, Phase 3 adds variety):
- **Plains**: No modifiers, 1 Stamina per hex
- **Forest** (Phase 3): +10% Evasion, 1 Stamina per hex
- **Mountain** (Phase 3): +20% Defense, impassable (unless Flying)
- **Water** (Phase 3): -20% Movement (2 Stamina per hex), impassable (unless Swimming/Flying)

**Victory Conditions**:
- Eliminate all enemy units (manual combat)
- AI resolve (auto-battle, instant)
- Time limit: 20 turns (draw if no winner, defender wins)

**Example Battle**:
```
Sovereign (20 cards) vs Goblin Raider Camp (5 cards)
- Sovereign deploys 10 units (top 2 rows)
- Goblin AI deploys 5 units (bottom 2 rows)
- Turn 1: Sovereign moves Fire Mage forward, attacks Goblin
- Turn 2: AI moves Goblin Archer, attacks Fire Mage
- Turn 5: Sovereign eliminates all Goblins, wins battle
- Rewards: 100 Gold, 50 XP, Bronze Battle Chest
```

**No Occupation** (Battle Map is ephemeral, no persistent control):
- Winning battle advances Realm Map progress (occupies Location)
- Battle Map disappears after combat (no revisit)

---

## Tier 3: Realm Map (20-40 Locations) ← **MVP FOCUS**

**Scope**: Single explorable region (HoMM-style, 1-2 hours of content)

**Map Size**:
- 20-40 hex tiles (Locations)
- Fog of war: 50% visible at start, 50% hidden (explore to reveal)
- MVP = 40 Locations (1 Realm total)
- Phase 2 = 100+ Locations (5-10 Realms available)

**Location Types**:
- **Town** (3-5 per Realm): Heal army instantly, recruit units (Phase 2)
- **City** (1 per Realm): Heal + buy equipment + RPG shops (Phase 2)
- **Dungeon** (5-10 per Realm): PvE battles, Epic/Legendary loot
- **Mine** (2-5 per Realm): Ore production (Phase 2, place Worker card)
- **Ruins** (5-10 per Realm): Treasure nodes (Gold/Gems, one-time loot)
- **Monster Spawn** (10-20 per Realm): Random PvE encounters (Common → Mythic)
- **Treasure Node** (5-10 per Realm): Gold/Gems loot, no battle
- **Empty Space** (10-20 per Realm): No content, passable terrain

**Terrain Types**:
- **Plains**: 1 Movement Point per hex, no modifiers
- **Forest**: 1 Movement Point per hex, no modifiers (MVP), +10% Evasion (Phase 3)
- **Mountain**: Impassable (blocks movement, acts as barrier)
- **Water**: Impassable (blocks movement, acts as barrier)

**Movement System**:
- 10 Movement Points per day (refills at midnight)
- Moving 1 hex costs 1 Movement Point
- Entering Location triggers event (battle, treasure, heal)

**Occupation Mechanics** (MVP):
- **Occupy Location**: Win battle at Location → Location becomes "Occupied" (green flag)
- **Occupation Buffs** (Phase 2): Each Location grants +1% Gold production OR +5 Stamina/day
- **Total Buffs**: 40 Locations = +40% Gold production OR +200 Stamina/day (choose at occupation)

**Example Realm Map** (MVP):
```
Realm: "Forest of Trials" (40 Locations)

Starting Location: Town (center of map, free heal)
Visible Locations (20):
- 2× Towns (heal points)
- 5× Dungeons (Epic loot, PvE battles)
- 3× Treasure Nodes (500 Gold, 50 Gems)
- 10× Monster Spawns (Common → Rare enemies)

Hidden Locations (20, fog of war):
- 1× City (unlock equipment shop)
- 3× Dungeons (Legendary loot)
- 2× Treasure Nodes (1,000 Gold, 100 Gems)
- 10× Monster Spawns (Epic → Mythic enemies)
- 4× Empty Space

Total Battles: 5-10 (Dungeons + Monster Spawns)
Total Exploration Time: 1-2 hours (40 Locations × 2 minutes each)
```

---

### Realm Map Progression (MVP)

**Week 1** (Tutorial Complete):
- Sovereign starts at central Town (Location 1/40)
- Movement Points: 10/day
- Visible Locations: 20 (fog of war hides 20)
- First battle: Monster Spawn (3× Common Goblins)
- First treasure: Treasure Node (500 Gold)

**Week 2** (Exploration):
- Occupied Locations: 10/40 (25% of Realm)
- Battles won: 3 (Dungeons)
- Total Gold earned: 2,000 (battles + treasures)
- Packs bought: 2× Standard Packs (1,000 Gold each)

**Week 3** (Completion):
- Occupied Locations: 30/40 (75% of Realm)
- Battles won: 8 (all Dungeons + Monster Spawns)
- Final boss: Mythic Dragon (Location 40, City)
- Reward: 5,000 Gold, 1× Epic Booster Pack, 1× Legendary card

**Phase 2** (Realm Control):
- Occupy all 40 Locations → "Control Realm" achievement
- Realm Buff: +10% Power when fighting in this Realm (PvP/PvE)
- Unlock next Realm: "Desert of Storms" (40 new Locations)

---

## Tier 2: Territory Map (50-100 Realms) ← **PHASE 3**

**Scope**: Regional conquest (1-month campaign, alliance coordination)

**Map Size**:
- 50-100 hex tiles (Realms)
- Each Realm contains 20-40 Locations (nested maps)
- Total content: 50 Realms × 40 Locations = 2,000 Locations (massive)

**Realm Types**:
- **Starter Realms** (5-10): Easy PvE, tutorial-level enemies
- **Mid-Tier Realms** (20-40): Moderate PvE, Rare/Epic loot
- **High-Tier Realms** (10-20): Hard PvE, Legendary/Mythic loot
- **Capital Realm** (1): Alliance headquarters, castle sieges, Territory control

**Occupation Mechanics** (Phase 3):
- **Occupy Realm**: Control all Locations in Realm (20-40 battles)
- **Realm Buffs**: +5% Gold production, +10% XP gain, +50 Stamina/day
- **Total Buffs**: 50 Realms = +250% Gold, +500% XP, +2,500 Stamina/day (massive power)

**PvP Realm Occupation** (Phase 3):
- Active PvP Realms: 10-20 Realms are "contested" (Sovereigns can attack each other)
- Passive PvE Realms: 30-40 Realms are "safe zones" (no PvP, AI enemies only)
- Alliance Wars: 50v50 battles for Capital Realm control

**Example Territory Map** (Phase 3):
```
Territory: "Kingdom of Fire" (50 Realms)

Starter Realms (10):
- Forest of Trials (MVP Realm, 40 Locations, Common → Rare enemies)
- Plains of Beginnings (40 Locations, tutorial-level)
- River Valley (40 Locations, Water-themed)

Mid-Tier Realms (30):
- Desert of Storms (40 Locations, Earth-themed, Rare → Epic enemies)
- Volcanic Wastes (40 Locations, Fire-themed, Epic loot)
- Frozen Tundra (40 Locations, Water-themed, Legendary loot)

High-Tier Realms (9):
- Shadow Abyss (40 Locations, Shadow-themed, Mythic enemies)
- Dragon's Peak (40 Locations, Dragon bosses, Mythic loot)

Capital Realm (1):
- Citadel of Flames (40 Locations, alliance headquarters, castle sieges)
- Control Capital → Dominate Territory (+100% Power to entire alliance)

Total Content: 50 Realms × 40 Locations = 2,000 Locations (6-12 months of exploration)
```

---

### Territory Map Progression (Phase 3)

**Month 1** (Early Exploration):
- Alliance occupies 5 Starter Realms (200 Locations total)
- Each member controls 1-2 Realms (40-80 Locations each)
- Alliance Buff: +25% Gold production (5 Realms × 5% each)

**Month 2** (Mid-Tier Conquest):
- Alliance occupies 20 Realms (800 Locations total)
- Members specialize (Fire Sovereigns take Volcanic Wastes, Water takes Frozen Tundra)
- Alliance Buff: +100% Gold production (20 Realms × 5% each)

**Month 3** (Capital Siege):
- Alliance occupies 40 Realms (1,600 Locations total)
- Final push: Castle siege on Capital Realm (50v50 PvP battle)
- Victory: +100% Power to all alliance members for next 30 days
- Season rewards: Mythic card, exclusive Title, 50,000 Gold

---

## Tier 1: World Map (200-500 Territories) ← **PHASE 4**

**Scope**: Global conquest (3-month seasons, alliance dominance)

**Map Size**:
- 200-500 hex tiles (Territories)
- Each Territory contains 50-100 Realms (nested maps)
- Each Realm contains 20-40 Locations (nested maps)
- **Total content**: 200 Territories × 50 Realms × 40 Locations = 400,000 Locations (absurd scale, algorithmic generation)

**Territory Types**:
- **Neutral Territories** (150-400): No alliance control, AI-defended
- **Alliance Territories** (50-100): Controlled by top alliances, PvP contested
- **Capital Territories** (1-5): Alliance headquarters, major castle sieges
- **Legendary Territories** (1-3): World bosses, Mythic loot, server-wide events

**Occupation Mechanics** (Phase 4):
- **Dominate Territory**: Alliance controls all Realms in Territory (50-100 castle sieges)
- **Territory Buffs**: +50% Gold production, +100% XP gain, +500 Energy/day
- **Total Buffs**: 50 Territories = +2,500% Gold, +5,000% XP, +25,000 Energy/day (whale-tier power)

**Alliance Wars** (Phase 4):
- Season length: 3 months (90 days)
- Top 10 alliances compete for Territory control
- Weekly battles: 50v50 castle sieges (Territory vs Territory)
- Season end: Alliance with most Territories wins, exclusive Mythic rewards

**Example World Map** (Phase 4):
```
World: "Sovereign Realms" (200 Territories)

Neutral Territories (150):
- Kingdom of Fire (50 Realms, Fire-themed)
- Kingdom of Water (50 Realms, Water-themed)
- Kingdom of Earth (50 Realms, Earth-themed)

Alliance Territories (45, contested):
- Dragon Empire (10 Territories, controlled by "Dragons United" alliance)
- Phoenix Dynasty (10 Territories, controlled by "Phoenix Rising" alliance)
- Elemental Alliance (10 Territories, controlled by "Elemental Masters" alliance)

Capital Territories (4):
- Citadel of Flames (Dragon Empire capital)
- Palace of Tides (Phoenix Dynasty capital)
- Earthen Fortress (Elemental Alliance capital)
- Neutral Sanctuary (server hub, no PvP)

Legendary Territory (1):
- Mythic Nexus (world boss, server-wide event, 1,000 Sovereigns co-op)

Total Content: 200 Territories × 50 Realms × 40 Locations = 400,000 Locations (impossible to fully explore, algorithmic generation)
```

---

### World Map Progression (Phase 4)

**Season 1** (Month 1-3):
- 100 alliances compete for 50 Alliance Territories
- Weekly castle sieges: 50v50 PvP battles
- Top 10 alliances control 5 Territories each (250 Realms, 10,000 Locations)

**Season 2** (Month 4-6):
- Top 10 alliances from Season 1 get +10% Power bonus
- New alliances challenge for Territories (200v200 mega-battles)
- Legendary Territory event: Mythic Dragon world boss (server-wide co-op)

**Season 3** (Month 7-9):
- Alliance domination: Top 3 alliances control 15 Territories each (750 Realms)
- Final showdown: 500v500 castle siege for World Champion title
- Victory rewards: Exclusive Mythic card, $10,000 cash prize (esports tier)

---

## Occupation Buff Summary

### Location Buffs (Phase 2)
- **Per Location**: +1% Gold production OR +5 Energy/day (choose at occupation)
- **Example**: 40 Locations = +40% Gold OR +200 Energy/day

### Realm Buffs (Phase 3)
- **Per Realm**: +5% Gold production, +10% XP gain, +50 Energy/day
- **Example**: 50 Realms = +250% Gold, +500% XP, +2,500 Energy/day

### Territory Buffs (Phase 4)
- **Per Territory**: +50% Gold production, +100% XP gain, +500 Energy/day
- **Example**: 50 Territories = +2,500% Gold, +5,000% XP, +25,000 Energy/day

**Total Power** (Maxed Sovereign in Phase 4):
```
Base Stats: 1,000 Gold/day, 100 XP/battle, 240 Energy/day

With Max Buffs:
- Gold: 1,000 + (1,000 × 2,500%) = 26,000 Gold/day (26× F2P)
- XP: 100 + (100 × 5,000%) = 5,100 XP/battle (51× F2P)
- Energy: 240 + 25,000 = 25,240 Energy/day (105× F2P)

Reality Check: These buffs require occupying 400,000 Locations (impossible solo, requires massive alliance).
```

---

## Monster Spawn Scaling (Realm Map)

**MVP**: Common → Rare enemies (easy progression)

**Location 1-10** (Starting Area):
- Common enemies (3-5 cards, 10-20 Attack, 5-10 Defense)
- Rewards: 50 Gold, 25 XP, Bronze chest

**Location 11-20** (Mid Realm):
- Uncommon enemies (5-7 cards, 20-30 Attack, 10-15 Defense)
- Rewards: 100 Gold, 50 XP, Silver chest

**Location 21-30** (Late Realm):
- Rare enemies (7-10 cards, 30-50 Attack, 15-25 Defense)
- Rewards: 200 Gold, 100 XP, Gold chest

**Location 31-40** (Boss Area):
- Epic enemies (10-15 cards, 50-70 Attack, 25-40 Defense)
- Rewards: 500 Gold, 200 XP, Platinum chest, 1× Epic card

**Phase 3** (High-Tier Realms):
- Legendary bosses (15-20 cards, 70-100 Attack, 40-60 Defense)
- Mythic bosses (20-25 cards, 100-150 Attack, 60-80 Defense)
- Rewards: 5,000 Gold, 1,000 XP, 1× Legendary/Mythic card

---

## Implementation Roadmap

### MVP (Week 1-8)
- ✅ Battle Map (8×8 grid, Plains terrain only)
- ✅ Realm Map (40 Locations, fog of war, HoMM exploration)
- ✅ Location types (Town, Dungeon, Treasure Node, Monster Spawn)
- ✅ Movement system (10 Movement Points/day, 1 MP per hex)
- ✅ Monster scaling (Common → Epic enemies)
- ❌ No Realm/Territory/World Maps (Phase 3-4)
- ❌ No occupation buffs (Phase 2)

### Phase 2 (Month 2-3)
- ❌ Location occupation buffs (+1% Gold OR +5 Energy per Location)
- ❌ Realm expansion (5-10 Realms, 200-400 Locations total)
- ❌ Resource production (Mines on Locations, place Worker cards)

### Phase 3 (Month 4-6)
- ❌ Territory Map (50-100 Realms, 2,000-4,000 Locations)
- ❌ Realm occupation buffs (+5% Gold, +10% XP, +50 Energy per Realm)
- ❌ Castle sieges (50v50 alliance battles for Capital Realm)
- ❌ Active PvP Realms (10-20 contested, 30-40 safe zones)

### Phase 4 (Month 7-12)
- ❌ World Map (200-500 Territories, 400,000 Locations, algorithmic generation)
- ❌ Territory occupation buffs (+50% Gold, +100% XP, +500 Energy per Territory)
- ❌ Alliance seasons (3-month cycles, world domination)
- ❌ Legendary Territories (world bosses, server-wide events)

---

**For combat details, see**: [combat-calculation-spec.md](combat-calculation-spec.md)  
**For MVP scope, see**: [mvp-scope-final.md](mvp-scope-final.md)  
**For economy balance, see**: [economy-system.md](economy-system.md)  
**For data specifications, see**: [realm-map-schema.json](specs/realm-map-schema.json), [territory-map-schema.json](specs/territory-map-schema.json), [world-map-schema.json](specs/world-map-schema.json), [location-schema.json](specs/location-schema.json), [occupation-schema.json](specs/occupation-schema.json)
