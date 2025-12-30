# Campaign Mode Restructure - Phase 1 MVP Pivot

**Date**: December 30, 2025  
**Purpose**: Document the shift from "Realm Map exploration" to "Campaign Mode progression" for MVP Phase 1  
**Status**: Pending approval → Will update 3 MVP docs + game-bible.md

---

## Executive Summary

### **The Strategic Pivot**

**Old MVP Approach**:
- Realm Map exploration (40-tile hex grid, open-world)
- Players wander freely, discover battles randomly
- Hard to gate progression, monetize, or create daily events

**New MVP Approach**:
- **Campaign Mode** (8 Worlds × 9 Stages = 72 linear battles)
- Clear progression (Stage 1-1 → 1-2 → ... → 8-9)
- Traditional mobile game structure (Candy Crush, Clash of Clans)
- Easy to gate, monetize, and add daily events

**Long-Term Vision** (Post-Phase 2):
- BOTH systems co-exist (player choice)
- Campaign Mode = story-driven, linear progression, beginner-friendly
- Realm Map = open-world, territory control, AFK income, veteran content
- Both lead to PvP readiness (different training paths)

---

## Changes Required by Document

### **1. mvp-scope-final.md** ✏️

**Section**: Week 5-6 (lines 105-135)

**BEFORE**:
```markdown
### Week 5-6: Realm Map & Exploration

**Realm Map**:
- ✅ 40-hex map (Locations)
- ✅ Fog of war: 20 Locations visible at start, 20 hidden
- ✅ Movement: 3 tiles per turn, 10 Movement Points/day
- ✅ Terrain: Plains, Forest, Mountain (impassable), Water (impassable)
- ✅ Camera: Top-down isometric, drag to pan, pinch to zoom

**Enemy Encounters** (5-10 PvE battles):
- ✅ Goblin Raiders (Common, 3-card deck)
- ✅ Bandit Camp (Uncommon, 5-card deck)
- ✅ Orc Warband (Rare, 7-card deck)
- ✅ Ancient Ruins (Epic, 10-card deck, Realm Boss)

**Treasure Nodes**:
- ✅ Gold Node: 100-500 Gold (5-10 nodes on map)
- ✅ Gem Node: 10-50 Gems (2-5 nodes on map)
- ✅ Empty Locations: No reward, passable
```

**AFTER**:
```markdown
### Week 5-6: Campaign Mode & Stage Progression

**Campaign Structure**:
- ✅ 8 Worlds × 9 Stages = 72 total battles (linear progression)
- ✅ World themes: Goblin Plains, Bandit Forests, Orc Wastelands, Undead Crypts, Dragon Peaks, Demon Wastes, Celestial Realm, Void Dimension
- ✅ Boss battles: Stages X-5 (mini-boss), X-9 (world boss)
- ✅ Unlock system: Beat Stage 1-1 to unlock 1-2, beat 1-9 to unlock World 2
- ✅ 3-star rating: Speed (under 10 turns), No Deaths (full army survives), Full Health (hero >80% HP)

**Stage Types**:
- ✅ Regular stages (1-1 to 1-4, 1-6 to 1-8): 3-7 card enemy decks, increasing difficulty
- ✅ Mini-boss stages (1-5, 2-5, etc.): 7-10 card decks, Rare/Epic heroes
- ✅ World boss stages (1-9, 2-9, etc.): 12-15 card decks, Epic/Legendary heroes
- ✅ Final boss (8-9): Mythic Void Lord, 20-card deck

**Rewards Per Stage**:
- ✅ First clear: 100-500 Gold, 50-200 XP, 1-3 cards (rarity increases with world difficulty)
- ✅ 3-star clear: +1 Epic card (choice from 3 options)
- ✅ Replays: 50% reduced rewards (encourages progression over farming)

**Daily/Weekly Events**:
- ✅ Daily Event Stage: Random stage from unlocked worlds, 2× rewards, 3 attempts/day
- ✅ Weekly Boss Rush: Fight 5 world bosses in a row, leaderboard rewards
```

**Deliverables** (Updated):
```markdown
- [ ] CampaignManager C# class (stage unlocking, progression tracking)
- [ ] Stage Select UI (world map view, 9 stage icons per world, lock/unlock states)
- [ ] 3-star rating system (turn count, deaths, hero health tracking)
- [ ] Enemy AI decks (72 pre-built decks, JSON data)
- [ ] Daily Event system (random stage selection, timer, bonus rewards)
- [ ] Replay rewards reduction (50% Gold/XP after first clear)
```

**What MOVES to Phase 2**:
```markdown
❌ Realm Map (40-tile hex grid) - Phase 2 Months 4-6
❌ Open-world exploration - Phase 2
❌ Fog of war, Movement Points - Phase 2
❌ Territory occupation - Phase 2
❌ AFK economy cards - Phase 2
```

---

### **2. tutorial-flow.md** ✏️

**Sections to Update**: Steps 12-27 (all "Realm Map" references)

**Key Changes**:

**Step 12: Realm Map Introduction → Campaign Mode Introduction**

**BEFORE** (line 533):
```markdown
### Step 12: Realm Map Introduction
**Screen**: Realm Map - Tutorial Start

[Camera: Zoomed out view of Realm Map]
[Tutorial Overlay]: "This is the Realm Map - your army's battlefield!"
[Map: 20-40 hexes visible, 20 fog-of-war tiles]
[Player's Army Stack: Hero + units on starting tile]
```

**AFTER**:
```markdown
### Step 12: Campaign Mode Introduction
**Screen**: Campaign World Select

[Header: "Campaign Mode - Choose Your Battle"]
[World 1: Goblin Plains] - UNLOCKED (green glow)
  - Icon: Goblin face, green grasslands background
  - Progress: 0/9 stages completed
  - [TAP TO START] button

[Worlds 2-8: LOCKED] (grayed out, padlock icons)
  - Bandit Forests, Orc Wastelands, Undead Crypts, Dragon Peaks, Demon Wastes, Celestial Realm, Void Dimension

[Tutorial Text]: "Complete stages to unlock new worlds and face epic bosses!"
```

**Step 13: First Battle Preparation → Stage 1-1 Select**

**BEFORE** (line 580):
```markdown
### Step 13: First Battle Preparation
[Player clicks enemy Location on Realm Map]
[Prompt: "Battle Goblin Raiders?"]
  - Yes (10 Energy) - Recommended
  - No (return to map)
```

**AFTER**:
```markdown
### Step 13: Stage 1-1 - First Campaign Battle
**Screen**: Stage Select (World 1)

[9 stage icons in horizontal row]:
  - Stage 1-1: UNLOCKED (green, pulsing START button)
    - Enemy: Goblin Raiders (3-card deck)
    - Rewards: 100 Gold, 1 Common card
  - Stages 1-2 to 1-9: LOCKED (complete 1-1 to unlock 1-2)

[Tutorial Text]: "Tap Stage 1-1 to begin your first campaign battle!"
[Player taps Stage 1-1]
```

**Step 24: Return to Realm Map → Return to Campaign Map**

**BEFORE** (line 1077):
```markdown
### Step 24: Realm Map - Auto-Battle Unlock
**Screen**: Realm Map - After First Battle

[Camera returns to Realm Map]
[Player's army stack on cleared Location (green checkmark)]
[Fog-of-war tiles revealed (3 new tiles visible)]
```

**AFTER**:
```markdown
### Step 24: Campaign Progress - Auto-Battle Unlock
**Screen**: Stage Select (World 1)

[Stage 1-1: COMPLETED] ✅ (gold star icon, "3-STAR CLEAR" badge)
[Stage 1-2: UNLOCKED] 🔓 (green glow, START button)
[Stages 1-3 to 1-9: LOCKED] 🔒 (complete 1-2 to unlock 1-3)

[Tutorial Popup]:
"Congratulations! Stage 1-1 complete!"
✅ Auto-Battle UNLOCKED (skip animations in future battles)
✅ Stage 1-2 UNLOCKED (continue your journey)
```

**Step 25: 3-5 More Battles → Tutorial Stages 1-2 to 1-4**

**BEFORE** (line 1153):
```markdown
### Step 25: Realm Map - 3-5 More Battles
[Player explores Realm Map, fights 3-5 more enemies]
[Enemy types: Bandits (Uncommon), Orcs (Rare), Treasure Guardians (Epic)]
```

**AFTER**:
```markdown
### Step 25: Tutorial Campaign - Stages 1-2 to 1-4
[Player progresses through Stages 1-2, 1-3, 1-4]

Stage 1-2: Goblin Ambush (4-card deck)
  - Rewards: 150 Gold, 1 Common card
  
Stage 1-3: Goblin Camp (5-card deck, Uncommon hero)
  - Rewards: 200 Gold, 1 Uncommon card
  
Stage 1-4: Goblin Fortress (6-card deck, Uncommon hero)
  - Rewards: 250 Gold, 1 Uncommon card
  - Unlocks Stage 1-5 (mini-boss)
```

**Step 27: Treasure Node → Stage 1-5 Mini-Boss**

**BEFORE** (line 1206):
```markdown
### Step 27: First Treasure Node (Resource Reward)
**Screen**: Realm Map - Treasure Chest Discovered

[Player army explores, reveals Treasure Chest tile]
[Treasure Chest: Neutral tile, no enemies, sparkling chest icon]

[Tutorial Overlay]: "You found a Treasure Node! Defeat the guardian to claim Gold and Gems."
```

**AFTER**:
```markdown
### Step 27: Stage 1-5 - First Mini-Boss Battle
**Screen**: Stage Select (World 1)

[Stage 1-5: UNLOCKED] (Boss icon: Goblin Warchief portrait, red glow)
[Enemy: Goblin Warchief - Mini-Boss]
  - 7-card deck (Rare hero + 6 units)
  - Total Power: 300 (player has ~250, challenging but winnable)
  
[Tutorial Text]: "Mini-Boss ahead! Prepare your best deck!"
[Rewards]: 500 Gold, 100 XP, 1 Rare card (guaranteed)
```

---

### **3. unity-implementation-guide.md** ✏️

**Section**: Week 5-6 code examples (lines 684-735)

**BEFORE**:
```csharp
// Week 5-6: County Map & Battle
public class RealmMap : MonoBehaviour
{
    public int mapSizeX = 8;
    public int mapSizeY = 5;
    public HexTile[,] tiles;
    
    void GenerateMap()
    {
        // Create 40-tile hex grid
        // Fog of war system
        // Movement Points tracking
    }
}
```

**AFTER**:
```csharp
// Week 5-6: Campaign Mode & Stage Progression
public class CampaignManager : MonoBehaviour
{
    public int totalWorlds = 8;
    public int stagesPerWorld = 9;
    
    [System.Serializable]
    public class CampaignStage
    {
        public int worldId;         // 1-8
        public int stageId;         // 1-9
        public string stageName;    // "Stage 1-1: Goblin Ambush"
        public bool isUnlocked;
        public bool isCompleted;
        public int starRating;      // 0-3
        public StageType type;      // Regular, MiniBoss, WorldBoss
    }
    
    public enum StageType { Regular, MiniBoss, WorldBoss }
    
    void UnlockNextStage(int worldId, int stageId)
    {
        // If completed Stage 1-1, unlock 1-2
        // If completed Stage 1-9, unlock World 2
    }
    
    int CalculateStarRating(int turnCount, int deaths, float heroHealthPercent)
    {
        int stars = 1; // Base: completed
        if (turnCount <= 10) stars++;
        if (deaths == 0) stars++;
        if (heroHealthPercent >= 0.8f) stars++;
        return stars;
    }
}
```

---

### **4. game-bible.md** 📖 (Most Important)

**Section**: 4.1 Realm Map PvE (lines 2063-2090)

**BEFORE**:
```markdown
## 4.1 Realm Map PvE (MVP - Tutorial & Progression)

### Overview
The Realm Map is the **primary MVP mode**: a 20-40 Location hex grid for single-player exploration teaching core mechanics through scripted battles.

### Key Features
- **Map**: 20-40 hexes (Locations: Town, City, Dungeon, Mine, Ruins, Monster Spawn, Treasure Node)
- **Movement**: 3 tiles/turn, 10 Movement Points/day (time-gated exploration)
- **Battles**: 8×8 tactical grid, 20-50 card decks, auto-battle after tutorial
- **Energy**: 10 Energy/battle (240 Energy/day = 24 battles max)
- **Rewards**: Gold (50-500/battle), Gems (10-20/treasure node), Battle Chests (Bronze/Silver/Gold)
- **Boss**: Final Location with Epic/Legendary boss (harder difficulty, rare loot)

### MVP Scope
- ✅ 3-5 Realm Maps (60-200 Locations total)
- ✅ Treasure nodes (one-time Gold/Gems/card rewards)
- ✅ Monster Spawns (Common → Epic rarity)
- ❌ Economy deployment (Phase 2)
- ❌ Multi-Realm occupation (Phase 3)
```

**AFTER**:
```markdown
## 4.1 Campaign Mode (Phase 1 MVP - Story Progression)

**For tutorial flow, see [mvp/tutorial-flow.md](mvp/tutorial-flow.md)**

### Overview
Campaign Mode is the **primary Phase 1 mode**: a linear story-driven progression system with 8 themed worlds and 72 pre-designed battles. Traditional mobile game structure (Candy Crush, Clash of Clans) optimized for clear goals, daily events, and monetization.

### Structure

**Main Story Path** (8 Worlds × 9 Stages = 72 core battles):
- **Mandatory Progression**: Stage 1-1 → 1-2 → ... → 1-9 → World 2
  - Stages X-1 to X-4: Regular battles (3-6 card enemy decks)
  - Stage X-5: Mini-Boss (7-10 card deck, Rare/Epic hero)
  - Stages X-6 to X-8: Advanced battles (7-10 card decks)
  - Stage X-9: World Boss (12-15 card deck, Epic/Legendary hero)
- **Final Boss**: Stage 8-9 (Mythic Void Lord, 20-card deck, ultimate challenge)

**Side Quests** (5-10 per world, ~60 optional battles total):
- **Optional Branches**: Unlock via story choices or exploration
- **Can Dead-End**: No exit path, just rewards (Gold, cards, equipment)
- **Examples**:
  - World 1: "Rescue the Village" (3-stage quest chain, Rare hero reward)
  - World 2: "Bandit Hideout" (single battle, 1,000 Gold + Epic equipment)
  - World 3: "Ancient Ruins" (5-stage gauntlet, Legendary card choice)
- **Unlock Conditions**: 
  - Story Choice (Stage 2-3: "Help Merchant" vs "Raid Caravan")
  - Exploration (find hidden tile on main path)
  - Achievement (3-star clear Stage 1-5 unlocks bonus quest)

**Branching Paths** (2-3 per world):
- **Story Choices with Consequences**:
  - Stage 2-3 Choice: "Alliance" path (unlock Merchant quests) vs "Betrayal" path (unlock Bandit quests)
  - Stage 4-7 Choice: "Holy" path (Paladin hero reward) vs "Dark" path (Necromancer hero reward)
  - Paths converge at World Boss (Stage X-9), but side content differs
- **No Wrong Choices**: Both paths lead to World Boss, just different rewards/story
- **Replay Value**: Players can replay world to see alternate path (reduced rewards after first clear)

### Progression
- **Linear Unlocking**: Complete Stage 1-1 to unlock 1-2, complete 1-9 to unlock World 2
- **3-Star Rating System**: 
  - ⭐ Victory (complete battle)
  - ⭐⭐ Speed Clear (under 10 turns)
  - ⭐⭐⭐ Perfect Clear (no deaths + hero >80% HP)
- **Replay Rewards**: 50% reduced Gold/XP after first clear (encourages progression over farming)

### Rewards
- **First Clear**: 100-500 Gold, 50-200 XP, 1-3 cards (rarity scales with world difficulty)
- **3-Star Clear**: +1 Epic card (player choice from 3 options)
- **Mini-Boss Clear**: +500 Gold, +1 Rare card (guaranteed)
- **World Boss Clear**: +1,000 Gold, +200 XP, +1 Epic/Legendary card

### Daily/Weekly Events

**Daily Event: "Challenge Stage"** (Single Battle)
- **Structure**: Random stage from unlocked worlds (1 battle only)
- **Rewards**: 2× Gold (300-600), 2× XP, +50 Gems bonus
- **Total Daily Value**: ~1,000 Gold equivalent (= 1 Standard Pack)
- **Attempts**: 3/day (resets midnight)
- **Strategy**: Designed to drive pack purchase ("I earned 1,000 Gold from daily, I'll buy 1 Standard Pack!")
- **Difficulty**: Scales to player's highest unlocked world (World 3 unlocked = World 3 challenge)

**Weekly Event: "Boss Hunt Mini-Campaign"** (5-Stage Event)
- **Structure**: Themed mini-campaign (Stages X.1 → X.5)
  - Example: "Demon Invasion Week"
    - Stage 1: Demon Scouts (5-card deck)
    - Stage 2: Demon Warriors (7-card deck)
    - Stage 3: Demon Mages (9-card deck)
    - Stage 4: Demon Generals (11-card deck)
    - Stage 5: **RANDOM BOSS** (Demon Lord, Demon King, or Arch-Demon)
- **Random Boss Mechanic**: 
  - 3 possible bosses per event (all Epic/Legendary)
  - Server randomly assigns boss at event start (all players fight same boss that week)
  - Boss card GUARANTEED if you beat Stage X.5
  - Example: Week 1 = Demon Lord (Epic Fire hero), Week 2 = Demon King (Legendary Fire hero)
- **Leaderboard**: Speed clear times for Stage X.5 boss
  - Top 100: +1 Legendary card (random)
  - Top 10: +500 Gems
  - #1: +1 Mythic card (player choice)
- **Attempts**: Unlimited (but Energy still costs 10 per battle)
- **Reset**: Monday 00:00 (weekly cycle)

**Event Design Philosophy**:
- **Daily**: Quick 5-minute session, pack purchase incentive, casual-friendly
- **Weekly**: 20-30 minute mini-campaign, boss card chase (collector appeal), competitive leaderboard
- **Random Boss**: Creates FOMO ("This week is Demon King! I need that card!"), encourages weekly login
- **Replayability**: Boss rotation = 3 weeks to collect all 3 variants (Demon Lord, King, Arch-Demon)

### Energy System
- **Tutorial battles** (Stages 1-1 to 1-4): 0 Energy (unlosable, teaches mechanics)
- **Post-tutorial battles**: 10 Energy per battle
- **Daily refill**: 240 Energy/day (24 battles max)
- **Starting Energy**: 100 (10 battles to start)

### Phase 1A: Core Campaign Launch (8-9 Weeks)
**Goal**: Ship fast, validate core loop, start revenue

- ✅ 72 main story battles (8 worlds × 9 stages, linear only)
- ✅ 3-star rating system (Victory, Speed, Perfect)
- ✅ Daily Challenge Stage (1 battle, 3 attempts, pack purchase incentive)
- ✅ **Async PvP Arena** (AI plays opponent decks, Elo ranking, Arena Store)
- ✅ Pack Store (Standard, Element, Epic packs)
- ✅ Battle Pass ($4.99/month, exclusive campaign rewards)
- ✅ Energy system (10 per battle, 240 daily refill)
- ✅ Replay system (50% reduced rewards after first clear)
- ❌ NO side quests (defer to Phase 1.5)
- ❌ NO branching paths (defer to Phase 1.5)
- ❌ NO weekly boss hunt (defer to Phase 1.5)
- ❌ NO Realm Map (Phase 2)

**Timeline**: 8-9 weeks (original 8 + 1 week for Arena)

---

### Phase 1.5: Depth Update (2-3 Weeks) - Optional Post-Launch
**Goal**: Add replayability IF players request more content

- ✅ Side quests for Worlds 1-4 (20-30 optional battles)
- ✅ Branching paths (1-2 choice points in Worlds 1-4)
- ✅ Weekly Boss Hunt (5-stage mini-campaign, random boss, leaderboard)
- ✅ Hidden quests (unlock via 3-star clears)

**Timeline**: 2-3 weeks (30-60 days post-launch)
**Condition**: Only if retention data shows players want more content

---

### Phase 2: Realm Map Expansion (2-3 Months)
**Goal**: Add strategic depth, AFK progression

- ✅ Open-world Realm Map (40-80 tile hex grid)
- ✅ Territory occupation, AFK economy, multi-hero armies
- ✅ Campaign Worlds 5-8 expansion (if Phase 1 successful)
- ✅ Resource nodes (Gold/Food/Lumber/Ore)

**Timeline**: 2-3 months (3-4 months post-Phase 1A launch)

---

## Phase 1A Monetization Strategy 💰

### Core Revenue Streams (Month 1-3)

**1. Pack Store** (Primary Revenue - 60-70% of income)
```
Standard Pack (5 cards): $0.99
  - Rarity: 50% Common, 30% Uncommon, 15% Rare, 4% Epic, 1% Legendary
  - OR 1,000 Gold (earnable in 1-2 days)

Element Booster (5 cards, 80% element match): $1.99
  - Same rarity distribution, targeted element
  - OR 2,000 Gold (earnable in 3-4 days)

Epic Booster (5 cards, guaranteed 1 Epic): $4.99
  - Rarity: 20% Epic, 40% Rare, 30% Uncommon, 10% Common
  - OR 5,000 Gold (earnable in 7-10 days)

Mega Pack (20 cards, guaranteed 1 Legendary): $19.99
  - Premium option for whales
  - Cannot be bought with Gold (money only)
```

**Why This Works**:
- ✅ $0.99 impulse buy (low barrier to first purchase)
- ✅ Gold prices are HIGH (1-10 days grinding) → encourages buying
- ✅ Mega Pack = whale bait (exclusive to money)
- ✅ Pity system prevents bad luck (Legendary every 50 packs)

**Expected Revenue**: $3-$8 per paying user per month

---

**2. Battle Pass** (Secondary Revenue - 20-30% of income)
```
Monthly Battle Pass: $4.99
  - 30-day season (resets monthly)
  - Free Track: 5 Standard Packs, 2,000 Gold, 100 Gems
  - Paid Track: 10 Standard Packs, 1 Epic Booster, 1 Exclusive Legendary, 5,000 Gold, 500 Gems
  - Progress: Earn XP from battles (10 XP per battle, 3,000 XP to max)
```

**Why This Works**:
- ✅ $4.99 = industry standard (Clash Royale, Brawl Stars)
- ✅ Exclusive Legendary = FOMO (can't get this card elsewhere)
- ✅ Monthly reset = recurring revenue (not one-time)
- ✅ 3,000 XP = 300 battles = ~10-15 days of play (achievable)

**Expected Conversion**: 10-15% of active players buy Battle Pass

---

**3. Energy Refills** (Tertiary Revenue - 5-10% of income)
```
Small Refill (100 Energy): $0.99
  - 10 battles worth
  - Instant refill (no wait)

Large Refill (500 Energy): $3.99
  - 50 battles worth
  - Better value (20% discount vs 5× small)

Daily Unlimited Energy (24 hours): $9.99
  - Infinite battles for 1 day
  - Weekend grind option
```

**Why This Works**:
- ✅ Whales spam battles for Arena ranking (competitive spending)
- ✅ Daily unlimited = "weekend warrior" option
- ✅ $0.99 = impulse buy when stuck on boss

**Expected Revenue**: Whales only (1-2% of players), but high spend ($50-$200/month)

---

**4. Arena Store** (Exclusive Currency - Retention Hook)
```
Arena Tokens (Earned, NOT Bought):
  - Win Arena battle: 10 tokens
  - Top 100 weekly: 500 bonus tokens
  - Cannot be purchased with money (skill-gated)

Arena Store Rewards:
  - Exclusive Legendary card: 1,000 tokens (10 weeks of grinding OR top 100 finish)
  - Epic card: 200 tokens (2-3 weeks)
  - Cosmetics (card backs, hero skins): 500-1,000 tokens
```

**Why This Works**:
- ✅ Skill-gated rewards (F2P can compete with whales)
- ✅ Encourages Arena play (retention)
- ✅ No pay-to-win (money can't buy Arena Tokens)
- ✅ Cosmetics = flex (shows off Arena mastery)

**Expected Revenue**: $0 direct, but drives Energy refill sales (whales spam Arena for tokens)

---

**5. First-Time Buyer Offers** (Conversion Optimization)
```
Starter Pack (One-time only): $0.99
  - 2 Standard Packs (2× value)
  - 500 Gold
  - 100 Gems
  - Available first 7 days only (FOMO)

New Player Bundle (One-time only): $4.99
  - 1 Epic Booster
  - 1 Guaranteed Legendary (choice from 3 options)
  - 2,000 Gold
  - Available first 14 days only

Whale Welcome Pack (One-time only): $49.99
  - 5 Mega Packs (100 cards, 5 Legendaries)
  - 1 Exclusive Mythic card
  - 30-day Battle Pass (free)
  - Available first 30 days only
```

**Why This Works**:
- ✅ $0.99 converts 30-50% of players (psychological barrier broken)
- ✅ Time-limited = FOMO ("Buy now or miss out!")
- ✅ Whale pack identifies high spenders early

**Expected Revenue**: 30-50% of players buy Starter Pack

---

### Revenue Projections (Phase 1A)

**Conservative** (1,000 DAU, 5% paying):
```
50 paying users × $10/month ARPU = $500/month
- Pack sales: $300/month (60%)
- Battle Pass: $150/month (30%)
- Energy refills: $50/month (10%)
```

**Optimistic** (5,000 DAU, 10% paying):
```
500 paying users × $25/month ARPU = $12,500/month
- Pack sales: $7,500/month (60%)
- Battle Pass: $3,125/month (25%)
- Energy refills: $1,250/month (10%)
- First-time offers: $625/month (5%)
```

**Whale Scenario** (10,000 DAU, 15% paying, 2% whales):
```
1,500 paying users:
  - 1,300 dolphins × $15/month = $19,500
  - 200 whales × $150/month = $30,000
  - Total: $49,500/month
```

---

### F2P Viability Check ✅

**Daily Earnings (F2P)**:
```
- Daily login: 500 Gold
- Daily Challenge (3 attempts): 1,000 Gold + 50 Gems
- Campaign battles (10/day): 2,000 Gold
- Total: 3,500 Gold/day + 50 Gems
```

**Monthly F2P vs Paid**:
```
F2P Player (Month 1):
  - ~100 Standard Packs earned
  - ~5 Epic cards from Arena Store
  - ~1 Legendary from pity system (50 packs)
  - Deck strength: 70% of whale deck

Battle Pass Player ($4.99/month):
  - ~120 Standard Packs
  - ~6 Epic cards
  - ~2 Legendaries (1 pity + 1 exclusive from pass)
  - Deck strength: 85% of whale deck

Whale ($50/month):
  - ~200 Standard Packs
  - ~15 Epic cards
  - ~4 Legendaries
  - Deck strength: 100% (best possible)
```

**Result**: F2P can reach 70% of whale power in 1 month → Fair monetization ✅

---

### Anti-Pay-to-Win Safeguards

1. **Arena Elo Matchmaking**: Whales fight whales, F2P fight F2P
2. **Arena Tokens Can't Be Bought**: Exclusive rewards require skill
3. **Campaign 3-Star Ratings**: Skill challenge, whales can't buy 3-stars
4. **Replay Rewards Nerfed**: Can't farm same stage infinitely
5. **Energy Cap**: Whales can't spam 100 battles/day (240 Energy max)

---

## 4.2 Realm Map Exploration (Phase 2 - Open-World Conquest)

**Status**: NOT IN MVP (deferred to Phase 2, Months 4-6)

### Overview
Realm Map is the **Phase 2 expansion mode**: a 40-tile hex grid for open-world exploration, territory control, and AFK resource production. Unlocks after completing Campaign World 3 (Player Level 10+).

### Key Features
- **Map**: 40-80 hexes (Towns, Cities, Dungeons, Mines, Ruins, Monster Spawns, Resource Nodes)
- **Movement**: 3 tiles/turn, 10 Movement Points/day (time-gated exploration)
- **Fog of War**: 20 tiles visible at start, 20 hidden (reveal by exploring)
- **Territory Occupation**: Capture tiles for permanent control, place economy cards for AFK income
- **Multi-Hero Armies**: Deploy 1-3 Epic+ heroes as independent stacks on map

### Economy Integration
- **Building Placement**: Place economy cards (Granary, Sawmill, Mine) on captured tiles
- **AFK Production**: Buildings generate Gold/Food/Lumber/Ore while offline (5-50 resources/hour)
- **Resource Management**: Spend resources to buy packs, upgrade buildings, recruit units
- **Storage Buildings**: Increase resource caps (Warehouse, Vault)

### Battles
- **Enemy Encounters**: 10-20 PvE battles (Common → Legendary bosses)
- **Energy Cost**: 10 Energy/battle (same as Campaign Mode)
- **Rewards**: Gold (100-1,000), Gems (20-100), Battle Chests (Silver/Gold/Platinum)

### Relationship to Campaign Mode
- **Parallel Progression**: Both modes co-exist post-Phase 2
- **Player Choice**: 
  - **Campaign Mode**: Story-driven, linear, clear goals, daily events (beginner-friendly)
  - **Realm Map**: Open-world, strategic, AFK income, multi-hero armies (veteran-oriented)
- **Both Lead to PvP**: Complete Campaign World 5 OR occupy 10 Realm Map tiles → unlock Arena PvP (Level 15+)

### MVP Scope (Phase 2 - Months 4-6)
- ✅ 3-5 Realm Maps (120-400 total tiles)
- ✅ Fog of war, Movement Points, territory occupation
- ✅ Economy card deployment (buildings generate AFK income)
- ✅ Multi-hero armies (1-3 heroes per map)
- ✅ Resource nodes (Gold/Food/Lumber/Ore, respawn daily)
- ❌ PvP territory wars (Phase 3)
- ❌ Alliance map control (Phase 3)

---

## Example: World 2 - Bandit Forests (Branching Design)

### Main Story Path (Mandatory)
```
Stage 2-1: Forest Ambush (4-card deck, Common bandits)
  ↓
Stage 2-2: Bandit Scouts (5-card deck, Uncommon hero)
  ↓
Stage 2-3: CHOICE POINT - "The Merchant's Plea"
  → Choice A: "Help the Merchant" (unlock Merchant Quest chain)
  → Choice B: "Raid the Caravan" (unlock Bandit Quest chain)
  → Choice C: "Ignore and Continue" (skip side quests, proceed to 2-4)
  ↓
Stage 2-4: Forest Outpost (6-card deck, Uncommon hero)
  ↓
Stage 2-5: MINI-BOSS - Bandit Captain (8-card deck, Rare hero)
  → Rewards: 500 Gold, 1 Rare card
  ↓
Stage 2-6: Deep Woods (7-card deck, Rare hero)
  ↓
Stage 2-7: Bandit Fortress (8-card deck, Rare hero)
  ↓
Stage 2-8: Throne Room Approach (9-card deck, Epic hero)
  ↓
Stage 2-9: WORLD BOSS - Bandit Lord (14-card deck, Legendary hero)
  → Rewards: 1,000 Gold, 1 Legendary "Bandit Lord" card
```

### Side Quest A: "Merchant's Alliance" (Choice A from 2-3)
```
Stage 2-3A.1: "Escort the Merchant" (5-card deck, guards)
  → Rewards: 300 Gold, +Merchant Rep
  ↓
Stage 2-3A.2: "Defend the Warehouse" (6-card deck, bandit raiders)
  → Rewards: 400 Gold, 1 Uncommon equipment
  ↓
Stage 2-3A.3: "Raid the Bandit Camp" (7-card deck, Rare hero)
  → Rewards: 1,000 Gold, 1 Epic "Merchant Guard Captain" card
  → DEAD END (return to Stage 2-4 on main path)
```

### Side Quest B: "Bandit's Honor" (Choice B from 2-3)
```
Stage 2-3B.1: "Raid the Caravan" (5-card deck, guards)
  → Rewards: 800 Gold (higher than Quest A), -Merchant Rep
  ↓
Stage 2-3B.2: "Join the Bandit Crew" (6-card deck, initiation battle)
  → Rewards: 500 Gold, 1 Rare "Bandit Thief" card
  ↓
Stage 2-3B.3: "Betray the Bandits" (8-card deck, Rare hero + crew)
  → Rewards: 1,500 Gold, 1 Epic "Double-Crosser" card
  → DEAD END (return to Stage 2-4 on main path)
```

### Hidden Side Quest: "Ancient Ruins" (Unlock: 3-star clear Stage 2-5)
```
Stage 2-5H.1: "Ruins Entrance" (7-card deck, undead guardians)
  → Rewards: 300 Gold, +Exploration Points
  ↓
Stage 2-5H.2: "Crypt Chamber" (9-card deck, Epic undead hero)
  → Rewards: 500 Gold, 1 Epic equipment
  ↓
Stage 2-5H.3: "Final Treasure Room" (11-card deck, Legendary lich)
  → Rewards: 2,000 Gold, 1 Legendary card (choice of 3)
  → DEAD END (secret treasure obtained)
```

### Choice Consequences
- **Merchant Alliance Path**: Lower Gold rewards, but unlock "Merchant Discount" (10% off all packs in World 2)
- **Bandit Honor Path**: Higher Gold rewards, but lose Merchant Discount
- **Ignore Both**: No side quest rewards, but faster progression to World Boss
- **Hidden Ruins**: Highest rewards, but requires 3-star clear of Mini-Boss (skill gate)

### Total World 2 Content
- **Main Path**: 9 mandatory battles (2-1 → 2-9)
- **Side Quests**: 7 optional battles (3 from Merchant, 3 from Bandit, 3 from Hidden Ruins)
- **Total**: 16 battles (9 mandatory + 7 optional)
- **Replay Value**: 3 different side quest outcomes per playthrough

---

## Campaign Mode Summary (Updated)

**Schema**: [docs/specs/campaign-schema.json](docs/specs/campaign-schema.json)

Linear story mode (Player Level 20+) with themed chapters, boss phases, and narrative cutscenes. Primary source of Common/Uncommon fodder cards.

**Note**: "Saga Campaign" is DIFFERENT from "Campaign Mode" (Phase 1). Saga is narrative-heavy with cutscenes, Campaign Mode is gameplay-focused with clear progression.
```

**NEW SECTION TO ADD** (after 4.3):
```markdown
---

## 4.X Campaign Mode vs Realm Map: Design Philosophy

### Why BOTH Systems Co-Exist (Phase 2+)

**Player Personas**:

1. **Story-Driven Players** (40-50% of playerbase)
   - Want clear goals, linear progression, daily quests
   - Prefer "beat Stage 1-1, unlock 1-2" simplicity
   - Enjoy boss battles, leaderboards, competitive events
   - **Primary Mode**: Campaign Mode
   - **Secondary Mode**: Realm Map (optional, post-Level 10)

2. **Strategic Players** (30-40% of playerbase)
   - Want open-world exploration, territory control, AFK income
   - Prefer "place buildings, manage economy, multi-hero armies" complexity
   - Enjoy long-term planning, resource optimization, empire-building
   - **Primary Mode**: Realm Map
   - **Secondary Mode**: Campaign Mode (for daily event rewards)

3. **Casual Players** (10-20% of playerbase)
   - Want quick 5-minute sessions, auto-battle, easy rewards
   - **Primary Mode**: Campaign Mode daily events (3 attempts, done)
   - **Secondary Mode**: None (log in, collect, log out)

### Progression Pathways

**Path 1: Campaign-First** (Recommended for new players)
1. Tutorial → Campaign World 1 (Stages 1-1 to 1-9)
2. Reach Player Level 5 → Daily Event Stages unlock
3. Complete Campaign World 3 → Realm Map unlocks (Level 10)
4. Complete Campaign World 5 OR occupy 10 Realm tiles → Arena PvP unlocks (Level 15)
5. Endgame: Campaign daily events + Realm Map AFK income + Arena PvP

**Path 2: Realm Map-First** (For veterans who skip Campaign)
1. Tutorial → Campaign Stages 1-1 to 1-4 (mandatory, teaches mechanics)
2. Reach Player Level 10 → Realm Map unlocks
3. Focus on Realm Map exploration, ignore Campaign
4. Occupy 10 Realm tiles → Arena PvP unlocks (Level 15)
5. Endgame: Realm Map territory wars + Alliance Wars + Arena PvP

**Path 3: Hybrid** (Most common post-Phase 2)
1. Complete Campaign World 1-2 (learn mechanics)
2. Unlock Realm Map (Level 10), start building AFK economy
3. Do Campaign daily events for bonus rewards
4. Do Realm Map for long-term resource production
5. Endgame: Both modes contribute to overall progression

### Monetization Differences

**Campaign Mode**:
- ✅ Energy refills ($0.99 for 100 Energy = 10 more battles)
- ✅ World unlocks ($4.99 to skip World 2, unlock World 3 early)
- ✅ Event attempt bundles ($1.99 for +3 daily event attempts)
- ✅ Battle Pass ($4.99/month, exclusive campaign rewards)

**Realm Map**:
- ✅ Building Packs ($3.99 for 5 economy cards)
- ✅ Realm Expansion ($9.99 to unlock 2nd/3rd map)
- ✅ Speedups ($0.99 to instantly collect AFK resources)
- ✅ Hero Bundles ($14.99 for Legendary hero + 20 synergy cards)

### Development Sequencing

**Phase 1 (Months 1-3)**: Campaign Mode ONLY
- 72 battles, 8 worlds, 3-star system, daily events
- No Realm Map, no economy cards, no open-world

**Phase 2 (Months 4-6)**: Add Realm Map
- Unlock at Player Level 10 (after Campaign World 3)
- 3-5 maps, economy cards, AFK production, multi-hero armies
- Campaign Mode stays (daily events, weekly boss rush)

**Phase 3 (Months 7-12)**: Add PvP + Alliances
- Arena PvP unlocks at Level 15 (via Campaign OR Realm Map)
- Alliance Wars use Realm Map tiles as battlegrounds
- Campaign Mode gets alliance-only event stages

### Why This Design Succeeds

1. **Phase 1 Focus**: Campaign Mode is faster to build, easier to market, proven monetization
2. **Phase 2 Expansion**: Realm Map adds depth without invalidating Campaign progress
3. **Player Retention**: Different modes appeal to different personas (50% story, 40% strategy, 10% casual)
4. **Monetization Layers**: Campaign = energy/events, Realm Map = buildings/expansion, PvP = cosmetics/passes
5. **Endgame Variety**: Veterans can choose daily focus (Campaign events vs Realm Map economy vs Arena PvP)

### Inspiration
- **Campaign Mode**: Candy Crush (linear stages), Clash of Clans (star rating), Raid Shadow Legends (boss rush)
- **Realm Map**: Heroes of Might and Magic (hex exploration), AFK Arena (AFK income), Clash of Clans (territory building)
```

---

## Summary of Changes

### Files to Update (4 total)

1. ✅ **mvp-scope-final.md** (Week 5-6 section, ~30 line replacement)
2. ✅ **tutorial-flow.md** (Steps 12-27 references, ~15 edits)
3. ✅ **unity-implementation-guide.md** (Week 5-6 code examples, ~50 line replacement)
4. ✅ **game-bible.md** (Section 4.1 rewrite, NEW 4.X section added, ~300 lines total)

### Commits Needed (3 total)

**Commit 1**: MVP Docs - Campaign Mode Restructure
- mvp-scope-final.md
- tutorial-flow.md
- unity-implementation-guide.md
- Message: "Pivot Phase 1 from Realm Map exploration to Campaign Mode progression (8 worlds × 9 stages)"

**Commit 2**: Game Bible - Add Campaign Mode System
- game-bible.md (Section 4.1 rewrite)
- Message: "Add Campaign Mode as Phase 1 MVP system, move Realm Map to Phase 2"

**Commit 3**: Game Bible - Dual Progression Design
- game-bible.md (NEW Section 4.X)
- Message: "Document Campaign Mode vs Realm Map co-existence, player personas, monetization strategy"

---

## Campaign Mode Summary (Updated)

### Total Content (Phase 1 MVP)
- **Main Story**: 72 battles (8 worlds × 9 stages)
- **Side Quests**: 40-60 battles (5-10 per world)
- **Total Battles**: 112-132 battles (vs original 72)
- **Branching Points**: 16-24 choice moments (2-3 per world)
- **Hidden Quests**: 8-16 secret battles (1-2 per world, unlock via achievements)
- **Daily Events**: 1 battle/day (infinite variety, rotates through unlocked stages)
- **Weekly Events**: 5 battles/week (themed mini-campaign, random boss)

### Development Timeline (Phased Approach)

**Phase 1A: Core Campaign** (8-9 Weeks)
- Week 1-2: Card system + Tutorial UI (existing plan)
- Week 3-4: Combat system (existing plan)
- Week 5-6: Campaign Mode (72 battles, stage select UI)
- Week 7-8: Progression + Stores (existing plan)
- **Week 9: Async PvP Arena** (deck submission, Elo matchmaking, Arena Store)

**Phase 1.5: Depth Update** (2-3 Weeks) - Post-Launch Content
- Week 1: Side quests for Worlds 1-2 (10-15 battles)
- Week 2: Branching paths + choice UI (unlock logic)
- Week 3: Weekly Boss Hunt (5-stage event, random boss, leaderboard)

**Phase 2: Realm Map** (2-3 Months) - Major Expansion
- Month 1: Hex grid map, fog of war, movement system
- Month 2: Territory occupation, economy cards, AFK production
- Month 3: Multi-hero armies, resource nodes, Campaign Worlds 5-8

### Why This Is Worth It
1. ✅ **RPG Feel**: Player choices matter, branching paths, consequences
2. ✅ **Replay Value**: 3× the content (main path + 2 side quest variants per world)
3. ✅ **Retention**: Hidden quests encourage 3-star mastery, not just completion
4. ✅ **Monetization**: Daily events drive pack purchases, Weekly events drive boss card chase
5. ✅ **Competitive Players**: Leaderboards for weekly boss speed clears
6. ✅ **Casual Players**: Can skip side quests, just do main path (still 72 battles)
7. ✅ **Differentiation**: "It's not just linear stages, there are choices and secrets!" (marketing hook)

### Comparison to Competitors

| Feature | Sovereign Territories | Clash of Clans | Raid: Shadow Legends | Slay the Spire |
|---|---|---|---|---|
| Main Story Battles | 72 | 100+ | 500+ | 50+ |
| Side Quests | 40-60 | ❌ None | ✅ 100+ | ❌ None |
| Branching Paths | ✅ 2-3/world | ❌ Linear | ❌ Linear | ✅ 3/run |
| Choice Consequences | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| Daily Events | ✅ 1 battle | ❌ None | ✅ 1 dungeon | ❌ None |
| Weekly Events | ✅ 5-stage campaign | ✅ Clan Wars | ✅ Tournaments | ❌ None |
| Random Boss Rewards | ✅ Boss card drop | ❌ No | ✅ Random loot | ✅ Relics |

**Result**: We're combining **Slay the Spire's branching/choices** with **Raid's event structure** and **Clash's progression pacing**. **Unique positioning.**

---

## Approval Checklist

Before I execute these changes, please confirm:

- [x] **Campaign Mode structure approved?** (8 worlds × 9 stages main path, 5-10 side quests/world)
- [x] **Branching paths approved?** (2-3 choice points/world, consequences, dead-end side quests)
- [x] **3-star rating system approved?** (Victory, Speed, Perfect)
- [x] **Daily event approved?** (1 battle, 3 attempts, ~1,000 Gold rewards = pack purchase incentive)
- [x] **Weekly event approved?** (5-stage mini-campaign, random boss, boss card reward if beaten)
- [x] **Phase 1 timeline extension approved?** (10-12 weeks instead of 8 weeks for branching content)
- [x] **Phase 1 = Campaign ONLY, Phase 2 = Add Realm Map?** (sequencing correct)
- [x] **Both modes co-exist post-Phase 2?** (player choice, not replacement)
- [x] **Realm Map unlocks at Level 10 (Campaign World 3)?** (gate timing)
- [x] **Both modes lead to PvP at Level 15?** (Campaign World 5 OR 10 Realm tiles)

Once approved, I will:
1. Update all 4 files (mvp-scope-final.md, tutorial-flow.md, unity-implementation-guide.md, game-bible.md)
2. Create 3 commits with detailed messages
3. Push to remote
4. Archive this CAMPAIGN-MODE-RESTRUCTURE.md to docs/archive/

---

**Status**: ⏳ AWAITING USER APPROVAL
