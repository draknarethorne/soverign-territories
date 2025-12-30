# Gameplay Modes Specification

**Purpose**: Detailed mechanics for all game modes (MVP and post-MVP)  
**Status**: Working document with inline TODOs for areas needing design decisions  
**Last Updated**: December 30, 2024

---

## Overview

Sovereign Territories offers multiple gameplay modes catering to different playstyles:
- **MVP**: Realm Map PvE (tutorial + progression)
- **Phase 2**: Alliance PvE Events, Daily/Weekly Challenges
- **Phase 3**: Territory Map conquest, Arena PvP, Alliance Wars
- **Phase 4**: World Map seasons, Expeditions

---

## 4.1 Realm Map PvE (MVP - Tutorial & Progression)

**For tutorial flow details, see [tutorial-flow.md](tutorial-flow.md)**

### Overview
The Realm Map is a **20-40 Location hex grid** for single-player exploration and combat. This is the **primary MVP mode** - a linear progression path teaching core mechanics through scripted battles.

### How to Play
- **Entry**: Accessible from main menu after tutorial Step 12
- **Progression**: Move army (3 tiles/turn, 10 Movement Points/day) to explore Locations
- **Battles**: Engage Monster Spawns or occupy neutral Locations
- **Treasure Nodes**: Find 5-10 treasure chests containing Gold/Gems/cards
- **Boss**: Final Location contains Epic/Legendary boss (harder difficulty, rare loot)

### Location Types
- **Town** (5-8 per map): Basic Gold rewards (300-500), Common/Uncommon enemies
- **City** (2-3 per map): High Gold rewards (1,000-2,000), Rare enemies
- **Dungeon** (3-5 per map): Card rewards (Uncommon/Rare), multi-battle chains
- **Mine** (2-4 per map): Gem rewards (10-20), moderate enemies
- **Ruins** (3-5 per map): Mixed rewards, puzzle elements
- **Monster Spawn** (10-15 per map): Respawning enemies (Common → Epic rarity)
- **Treasure Node** (5-10 per map): One-time rewards (+300 Gold, +10 Gems, +1 card)
- **Empty Space** (8-12 per map): Movement tiles, fog of war

### Battle Grid (8×8 Tactical)
- **Player Deck**: 20-50 cards (based on Player Level)
- **Enemy Deck**: 3-15 cards (scales with Location difficulty)
- **Auto-Battle**: Unlocked after tutorial Step 24
- **Energy Cost**: 10 Energy per battle (240 Energy/day = 24 battles)

### Rewards
- **Gold**: 50-500 per battle (scales with difficulty)
- **Gems**: 10-20 per treasure node (5-10 nodes per map)
- **Cards**: Battle Chests (Bronze tier 70%, Silver 25%, Gold 5%)
  - Bronze: 50 Gold, 100 XP, 1 Common card
  - Silver: 200 Gold, 300 XP, 1 Uncommon card
  - Gold: 500 Gold, 500 XP, 1 Rare card
- **XP**: 100-500 per battle (Player Level progression)

### MVP Scope
- ✅ **Must Have**: 3-5 Realm Maps (60-200 Locations total)
- ✅ **Must Have**: Tutorial Realm Map (20 Locations, scripted battles)
- ✅ **Must Have**: Treasure nodes (one-time Gold/Gems rewards)
- ✅ **Must Have**: Monster Spawns (Common → Epic rarity, respawning)
- ❌ **Won't Have**: Economy deployment (deferred to Phase 2)
- ❌ **Won't Have**: Multi-Realm occupation (deferred to Phase 3)

**TODO: Define exact card pool for tutorial Realm Map (which 100 cards are MVP?)**  
**TODO: Design boss battle mechanics (phases, enrage timers, unique abilities?)**  
**TODO: Determine fog of war reveal mechanics (instant, gradual, line of sight?)**

---

## 4.2 Saga Campaign (Phase 2 - Story-Driven PvE)

**Schema**: [docs/specs/campaign-schema.json](docs/specs/campaign-schema.json)

### Overview
Linear story mode unlocked at Player Level 10. Features themed chapters (Norse, Greek, Egyptian) with narrative cutscenes and unique boss fights.

### How to Play
- **Entry**: Player Level 10+, basic deck required
- **Progression**: Linear stages (1 → 50+), defeat enemies to advance
- **Boss Stages**: Every 10th stage has multi-phase boss (e.g., Thor: Aggro phase → Heal phase → Enrage)
- **Energy System**: 10 Energy/battle, same as Realm Map
- **Rewards**: Primary source of Common/Uncommon "fodder cards" + XP

### Mechanics
- **Story Integration**: Dialogue boxes between battles (skippable)
- **Difficulty Scaling**: Each chapter introduces new mechanics (e.g., Chapter 3 = elemental interactions)
- **Hard Mode**: Optional replay at 2x difficulty for 2x rewards
- **Auto-Battle**: Available if Player Level ≥ Stage Level

**TODO: Write narrative arc for 3 launch chapters (Norse/Greek/Egyptian?)**  
**TODO: Design boss phases (how many phases? health gates? enrage mechanics?)**  
**TODO: Determine star rating system (3-star clear for bonus rewards?)**

---

## 4.3 Expeditions (Phase 4 - Weekly Board Game Mode)

**Schema**: [docs/specs/expedition-schema.json](docs/specs/expedition-schema.json)

### Overview
Weekly mini-game mode mixing board game mechanics (Mario Party) with card battles. Resets every Monday.

### How to Play
- **Entry**: Player Level 15+, unlocked via weekly quest
- **Board**: Procedurally generated path (30-50 spaces)
- **Movement**: Roll dice (1-6) or buy extra moves (50 Gems/move)
- **Spaces**: Rewards (Gold/cards), penalties (lose turn), mini-battles (3-card quick combat)
- **Objective**: Reach end first for grand prize (Epic/Legendary card)
- **Multiplayer**: 2-4 players, real-time or async

### Mechanics
- **Dice Rolls**: Base 1d6, VIP bonuses (+1 for VIP 5+)
- **Event Spaces**: Trigger mini-games (card battle, trivia, slot machine)
- **Monetization**: Buy dice rerolls (10 Gems), extra moves (50 Gems)
- **Weekly Reset**: New board layout, fresh leaderboard

**TODO: Design 10+ event space types (battles, puzzles, loot boxes, traps?)**  
**TODO: Determine mini-battle rules (3-card limit, instant resolve, auto-battle only?)**  
**TODO: Create board generation algorithm (ensure fair pathing, no dead ends)**

---

## 4.4 Alliance Events (Phase 3 - PvE/PvP Hybrid)

### Overview
Large-scale events where alliances coordinate to complete objectives. Mix of PvE raids (defeat AI bosses together) and PvP sieges (attack rival castles).

### How to Play
- **Entry**: Alliance member, Player Level 10+
- **Duration**: 2-7 days per event
- **Phases**: 
  1. **PvE Scramble** (Day 1-2): Alliance defeats AI-controlled territories for points
  2. **PvP Warfare** (Day 3-5): Attack rival alliance castles, defend own
  3. **Final Push** (Day 6-7): Control wonders/objectives for bonus points
- **Participation**: Contribute decks for auto-battle OR manual key moments
- **Scale**: 50-200 players per alliance

### Mechanics
- **Auto-Battle Dominance**: 80% of battles are AI-driven with preset tactics
- **Hero Moments**: 5-minute windows for direct commands (heal allies, target priority)
- **Rewards**: Alliance ranking (top 3 alliances get Legendary packs), individual contribution (top 10 players get Epic packs)
- **Coordination**: Alliance chat, shared war map, officer commands

**TODO: Define alliance event types (territory conquest, boss raid, capture the flag?)**  
**TODO: Design reward tiers (how many players in top 10/50/100?)**  
**TODO: Create anti-griefing measures (prevent alliance hoppers, afk players)**

---

## 4.5 Arena PvP (Phase 3 - Ranked 1v1/3v3)

**For matchmaking details, see [combat-calculation-spec.md](combat-calculation-spec.md) Appendix**

### Overview
Competitive PvP unlocked at Player Level 15. Features Elo-based matchmaking and Arena Token rewards (cannot be purchased).

### How to Play
- **Entry**: Player Level 15+, deck with 20-50 cards
- **Modes**: 
  - **1v1 Arena**: Standard ranked, Elo matchmaking
  - **3v3 Brawl**: Team battles, shared Elo (need 2 friends or auto-match)
- **Seasons**: 3-month cycles, Elo resets to 50% of previous season
- **Rewards**: Arena Tokens (1-10 per win, skill-based scaling)

### Matchmaking Brackets (Prevents Pay-to-Win)
- **Bronze** (Elo 0-999): New players, basic decks
- **Silver** (Elo 1000-1499): Intermediate, mixed rarity decks
- **Gold** (Elo 1500-1999): Advanced, rarity budget enforced
- **Platinum** (Elo 2000-2499): Expert, meta decks
- **Diamond** (Elo 2500+): Masters, top 1% players

### Deck Power Matchmaking
- **Total Rarity Points**: Sum of all cards in deck (Common=1, Mythic=32)
- **Brackets**: ±20% deck power variance (prevents whale stomping)
- **Example**: 120-point deck fights 96-144 point decks only

**TODO: Design Arena Token economy (how many tokens for Epic/Legendary cards?)**  
**TODO: Create seasonal reward tiers (end-of-season rewards based on final Elo?)**  
**TODO: Define 3v3 team dynamics (shared health pool, separate armies, tag-team?)**

---

## 4.6 Territory Map Conquest (Phase 3 - Monthly Campaigns)

**For occupation mechanics, see [map-tier-progression.md](map-tier-progression.md)**

### Overview
Mid-tier map (50-100 Realms) for alliance-based PvE/PvP conquest. 1-month campaigns with castle sieges and Realm occupation.

### How to Play
- **Entry**: Player Level 10+, alliance required
- **Map**: 50-100 hexes (Realms), each containing 20-40 Locations
- **Occupation**: Defeat Realm boss → claim Realm → gain +5-10% Power buff
- **Castle Sieges**: Attack enemy castles (multi-phase battles: walls → courtyard → throne room)
- **Duration**: 1 month per campaign

### Mechanics
- **Realm Buffs**: Each occupied Realm grants stat bonuses (+5-10% Attack/Defense)
- **Castle Levels**: Territory castles have separate levels (1-30), determine defense strength
- **Siege Phases**: 
  1. Breach Walls (destroy 3 wall segments, AoE damage vs buildings)
  2. Courtyard Battle (standard 8×8 combat)
  3. Throne Room (boss fight vs castle lord)
- **Rewards**: Occupying Realm = AFK Gold/Gems production (Phase 2 economy)

**TODO: Define Realm occupation flow (instant claim, garrison requirement, decay timer?)**  
**TODO: Design castle siege AI (defensive tactics, reinforcements, surrender conditions?)**  
**TODO: Determine alliance coordination mechanics (shared territories, officer permissions?)**

---

## 4.7 World Map Seasons (Phase 4 - Quarterly Alliance Wars)

**For full map hierarchy, see [map-tier-progression.md](map-tier-progression.md)**

### Overview
Top-tier map (200-500 Territories) for alliance dominance. 3-month seasons with Territory wars and seasonal leaderboards.

### How to Play
- **Entry**: Player Level 20+, alliance required
- **Map**: 200-500 hexes (Territories), each containing 50-100 Realms
- **Seasons**: 3-month cycles, Territory control resets each season
- **Alliance Wars**: 50v50 battles for Territory control
- **Rewards**: Seasonal leaderboard (top 3 alliances get exclusive Mythic cards)

### Mechanics
- **Territory Buffs**: Each occupied Territory grants massive bonuses (+50-100% Power)
- **Wonders**: 5-10 unique Locations on World Map (e.g., Great Pyramid, Stonehenge)
  - Control wonder = alliance-wide buff (e.g., +20% Gold production)
  - Contested = hourly battles for control
- **Capitals**: Each Territory has capital city (hardest to siege, best rewards)
- **Seasonal Meta**: Balance patches every 2 weeks to shift strategies

**TODO: Define Territory occupation flow (garrison sizes, supply lines, revolt mechanics?)**  
**TODO: Design wonder mechanics (buff durations, control thresholds, defense requirements?)**  
**TODO: Create seasonal reward structure (Mythic cards, cosmetics, titles?)**

---

## 4.8 Daily/Weekly Challenges (Phase 2 - Retention Hooks)

### Overview
Quick objectives that reset daily/weekly for bonus rewards. Encourages return play without requiring long sessions.

### Daily Challenges (Reset 00:00 UTC)
- **Win 3 Battles** → +300 Gold
- **Deploy 5 Buildings** → +100 Food (Phase 2)
- **Open 2 Packs** → +1 Standard Pack
- **Complete 5/7 Daily Quests** → +2 Standard Packs (weekly bonus)

### Weekly Challenges (Reset Monday 00:00 UTC)
- **Win 20 Battles** → +1 Epic Booster
- **Reach Realm Map Boss** → +500 Gems
- **Join 1 Alliance Event** → +1,000 Gold
- **Spend 5,000 Gold** → +1 Rare card (player choice)

**TODO: Design challenge variety (prevent repetitive "win X battles" grind)**  
**TODO: Determine reward scaling (should high-level players get better rewards?)**  
**TODO: Create challenge rotation (daily pool of 10, show 3 random per player?)**

---

## Cross-Mode Features

### Auto-Battle AI (All Modes)
- **Tactics System**: Preset AI behaviors (focus healers, flank left, defend flag)
- **Hero Moments**: 1-2 manual actions per turn during auto-mode (cooldown prevents spam)
- **Override Toggle**: Switch to full manual mid-battle (costs XP penalty)
- **Smart Targeting**: AI prioritizes low-HP enemies, avoids overkill

**TODO: Define 10-20 tactic templates (aggressive, defensive, balanced, anti-AoE, etc.)**  
**TODO: Create AI decision tree (target priority, retreat conditions, buff timing)**

### Reward Variety (All Modes)
- **Battle Chests**: Instant rewards (Gold/XP/cards), Bronze/Silver/Gold tiers
- **Pack Opening**: Collector appeal, Standard/Element/Epic Boosters
- **AFK Resources**: Phase 2 economy (Food/Lumber/Ore from occupied Realms)
- **Arena Tokens**: Phase 3 PvP currency (skill-based, cannot buy)

---

## Phasing Summary

| Mode | Phase | Player Level | MVP Status |
|------|-------|--------------|------------|
| Realm Map PvE | MVP | 1+ | ✅ Must Have |
| Saga Campaign | Phase 2 | 10+ | ❌ Post-MVP |
| Daily/Weekly Challenges | Phase 2 | 5+ | ❌ Post-MVP |
| Alliance PvE Events | Phase 2 | 10+ | ❌ Post-MVP |
| Arena PvP (1v1/3v3) | Phase 3 | 15+ | ❌ Post-MVP |
| Territory Map Conquest | Phase 3 | 10+ | ❌ Post-MVP |
| Expeditions (Board Game) | Phase 4 | 15+ | ❌ Post-MVP |
| World Map Seasons | Phase 4 | 20+ | ❌ Post-MVP |

---

**Next Steps**:
1. Finalize tutorial Realm Map design (20 Locations, exact enemy placements)
2. Define exact card pool for MVP (100 cards total, which rarities/elements?)
3. Create boss battle phases for tutorial (Step 25 final boss mechanics)
4. Design auto-battle AI decision tree (when to retreat, heal, focus fire)
