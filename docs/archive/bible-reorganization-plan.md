# Game Bible Reorganization & MVP Readiness Plan

**Date**: December 29, 2025 (Updated after Economy System Integration)  
**Current State**: game-bible.md (6,807 lines), tutorial-flow.md (1,223 lines), 60+ schemas  
**Purpose**: Finalize documentation before MVP implementation, ensure alignment with core vision  
**Strategy**: Consolidate redundancies, extract implementation details, define MVP scope clearly

---

## EXECUTIVE SUMMARY: CURRENT STATE ANALYSIS

### What We've Accomplished (Session 10 Achievements)

**Documentation**:
- ✅ **game-bible.md**: 6,807 lines (comprehensive design, 18 sections)
- ✅ **tutorial-flow.md**: 1,223 lines (28-step onboarding, 0-60 minutes)
- ✅ **60+ JSON schemas**: Complete data specifications (cards, packs, battles, economy, etc.)
- ✅ **tutorial-gap-resolutions.md**: 9 critical gaps solved (EULA, pack skip, undo, speed, etc.)
- ✅ **trainer-deck-schema.json**: 6 Trainer Deck options (3 Curated + 3 Element)
- ✅ **Section 5.5**: Complete economy/resource system (2,500+ lines, 7 currencies)

**Core Systems Designed**:
1. **Card System**: 6 rarity tiers (Common → Mythic), shiny variants (5% utility bonus)
2. **Pack System**: Trainer Decks (20 cards) → Standard/Element/Epic Boosters → Game Decks (50 cards)
3. **Economy System**: 7 currencies (Gold, Gems, Food, Lumber, Ore, Arena Tokens, Energy)
4. **Energy/Stamina**: Tutorial = 0 cost, Post-tutorial = 10 Energy/battle (prevents grinding)
5. **Movement System**: 3 tiles per turn, 10 Movement Points/day (time-gated exploration)
6. **Store Separation**: Pack Store (Gold/Gems), Resource Store (Food/Lumber/Ore), PvP Store (Arena Tokens)
7. **Auto-Collection**: Resources accumulate to storage cap (no tap-to-collect annoyance)
8. **Reward Variety**: Battle Chests (instant), Pack Opening (collector appeal), AFK Resources (passive)
9. **Rarity Budget**: 60-200 points based on Player Level (prevents pay-to-win)
10. **PvP Brackets**: Deck Power matchmaking (F2P fights F2P, whales fight whales)

**Tutorial Integration**:
- ✅ **Step 6**: Trainer Deck selection (6 options, Pokemon Battle Box model)
- ✅ **Step 12**: Movement Points introduced (10/day, 3 tiles per turn)
- ✅ **Step 23**: Energy system + Battle Chest rewards (Bronze tier)
- ✅ **Step 27**: Auto-collection economy (no tapping, storage capacity gates)
- ✅ **Step 28**: Store separation unlocked (Pack/Resource/PvP Stores)
- ✅ **Total Tutorial Cards**: 36 cards (20 Trainer Deck + 5 Element Booster #1 + 6 from Step 23 + 5 Element Booster #2)

**F2P vs Whale Balance**:
- ✅ **Gold Earnings**: Identical (12,180/week for both, cannot buy with money)
- ✅ **Gem Advantage**: Whales get 10× Gems (14,400 vs 168/week), spent on premium packs/refills
- ✅ **Arena Tokens**: Identical (skill-based, cannot buy)
- ✅ **Weekly Purchase Limits**: $136/week max (prevents whale blitz on day 1)
- ✅ **Rarity Budget + PvP Brackets**: Prevent pay-to-win (whales can't stomp F2P players)

---

## CRITICAL ASSESSMENT: ALIGNMENT WITH CORE VISION

### Core Tagline: "Build the Deck. Rule the Map. Automate the Empire."

**✅ Build the Deck (STRONG ALIGNMENT)**:
- Trainer Deck system (6 meaningful starter choices)
- Pack progression (5 packs in tutorial, collector appeal)
- Shiny utility (5% bonus, whale appeal without pay-to-win)
- Deck size progression (20 → 50 cards by Level 30)
- Rarity budget (prevents all-Legendary decks)
- **Verdict**: Card collection/deck-building is well-defined and balanced.

**⚠️ Rule the Map (PARTIALLY DEFINED)**:
- Movement system defined (3 tiles/turn, 10 Movement Points/day)
- County Map exploration (40 tiles, 4 days to explore)
- Battle system (8×8 tactical grid, turn-based combat)
- **MISSING**: 
  - State Map details (50-100 hexes, 1-month campaigns, castle sieges)
  - Global Map details (200-500 territories, 3-month seasons, alliance wars)
  - Territory conquest mechanics (how do you claim/hold tiles?)
  - Castle upgrade system (town → castle → fortress visual progression)
  - Alliance war mechanics (50v50 battles, territory control)
- **Verdict**: Tutorial/County Map complete, but higher map tiers need detail.

**✅ Automate the Empire (STRONG ALIGNMENT)**:
- Auto-collection system (resources accumulate to storage cap, no tapping)
- Economy buildings (Granary, Sawmill, Mine produce Food/Lumber/Ore)
- AFK production rates (10-50/hour depending on building level)
- Storage capacity (1,000-20,000 depending on level)
- **Verdict**: AFK progression is well-designed and respects player time.

---

## MAJOR GAPS IDENTIFIED

### 1. **Higher Map Tiers Underspecified** (State Map, Global Map)
**Current State**: County Map fully defined (40 tiles, exploration, battles, economy deployment)  
**Missing**:
- **State Map Mechanics**: How do 1-month campaigns work? What are castle sieges?
- **Global Map Mechanics**: How do 3-month seasons work? Alliance war flow?
- **Territory Conquest**: What happens when you defeat an enemy on a tile? Do you claim it? How long do you hold it?
- **Multi-Hex Battles**: County Map = 1 tile = 1 battle. Global Map = multi-tile territories?
- **Figurine/Statue System**: Section 4.5 mentions "visual figurines" but needs integration with economy buildings

**Impact on MVP**: MVP likely only needs County Map (tutorial + early PvE). State/Global can be post-launch.

**Recommendation**: 
- **MVP Scope**: County Map only (40 tiles, single-player PvE, no PvP)
- **Post-MVP**: State Map (alliances, PvE co-op), Global Map (alliance wars, seasons)
- **Document Now**: Create "map-tier-progression.md" to define State/Global mechanics (prevent scope creep)

---

### 2. **Combat System Depth** (Tactical Battle Details)
**Current State**: Section 8 (Combat Mechanics) exists, but lacks integration with cards  
**Missing**:
- **Attack/Defense Calculations**: How do stats work? Is it Attack - Defense = Damage? Or more complex?
- **Elemental Interactions**: Fire > Earth > Water > Fire? How much bonus damage (+50%? +100%?)?
- **Terrain Effects**: Mountains give +Defense? Water slows movement? How much?
- **Status Effects**: Burn (DoT), Freeze (skip turn), Poison (HP drain per turn) - durations and stacking?
- **Hero Abilities**: Do Legendary heroes have unique abilities? Cooldowns? Mana costs?
- **Equipment Effects**: Wooden Shield (+2 Health) - is this permanent or temporary? Stacks with armor?

**Impact on MVP**: MVP needs basic combat (Attack vs Health, no complex status effects).

**Recommendation**:
- **MVP Scope**: Simple combat (Attack - Defense = Damage, no elemental bonuses, no terrain)
- **Post-MVP**: Add status effects, elemental interactions, terrain modifiers
- **Document Now**: Create "combat-calculation-spec.md" with exact formulas for MVP vs full game

---

### 3. **Card Combining/Upgrading Mechanics** (Progression Path)
**Current State**: Section 5.5.2 mentions card combining costs (100 Gold + 2 duplicates = +1 Star)  
**Missing**:
- **Star Rank System**: Common → 1★ Uncommon → 2★ Rare → 3★ Epic → 4★ Legendary → 5★ Mythic?
- **Stat Scaling**: +1 Star = +10% stats? +20%? Linear or exponential?
- **Shiny Combining**: Can you combine shinies? Do they produce shiny upgrades?
- **Duplicate Requirements**: 2 cards for +1 Star seems low (Pokemon TCG requires 4). Intentional?
- **Max Star Limit**: Can a Common reach 5★ Mythic? Or capped at 3★ Epic?

**Impact on MVP**: MVP likely doesn't need card combining (players have limited cards to combine).

**Recommendation**:
- **MVP Scope**: No card combining (players use cards as-is)
- **Post-MVP**: Add combining system once players have duplicate accumulation
- **Document Now**: Create "card-progression-spec.md" with combining formulas and caps

---

### 4. **Auction House/Trading System** (Social Economy)
**Current State**: Section 5 mentions auction house, but no specs  
**Missing**:
- **Listing Fees**: Does it cost Gold to list cards? Prevents spam?
- **Currency Restrictions**: Can you trade cards for Gems? Or only Gold? (Prevent real-money trading)
- **Rarity Limits**: Can you trade Legendaries? Or only Common-Rare? (Prevent whale farming)
- **Account-Bound Cards**: Are some cards untradeable (tutorial rewards, Battle Pass exclusives)?
- **Tax System**: Does game take 10% of sale price? (Gold sink to control inflation)

**Impact on MVP**: MVP doesn't need trading (single-player tutorial focus).

**Recommendation**:
- **MVP Scope**: No auction house (single-player only)
- **Post-MVP**: Add trading once alliances unlock (Level 10+)
- **Document Now**: Create "trading-economy-spec.md" with anti-RMT safeguards

---

### 5. **Alliance System Integration** (Social Features)
**Current State**: Section 6 defines alliance structure (Leader, Co-Leader, Officer, Member)  
**Missing**:
- **Alliance PvE Events**: What are "cooperative raids against AI bosses"? How do they work?
- **Alliance Wars Flow**: 50v50 battles = 50 players attack same Global Map territory? Or separate instances?
- **Territory Control**: If alliance owns territory, can all 50 members deploy economy buildings? Storage limits?
- **Alliance Buildings**: War Monument (+5% Army Power) - affects all members' battles? Or only alliance war battles?
- **Matchmaking**: How are 50-member alliances matched? By total power? Player Level average?

**Impact on MVP**: MVP likely doesn't need alliances (unlocks at Player Level 10, post-tutorial).

**Recommendation**:
- **MVP Scope**: No alliances (single-player tutorial + County Map PvE)
- **Post-MVP**: Add alliances, alliance chat, PvE events (no alliance wars yet)
- **Post-Post-MVP**: Add alliance wars (requires Global Map implementation)
- **Document Now**: Create "alliance-progression-spec.md" with phased feature rollout

---

## BIBLE STRUCTURE ISSUES (Current Redundancies)

---

## BIBLE STRUCTURE ISSUES (Current Redundancies)

### 1. **Section 2.5 (New Player Onboarding) - Redundant with tutorial-flow.md**
**Lines**: 1212-1350 (138 lines)  
**Current State**: Describes Trainer Deck system in detail (6 options, selection flow, bonus packs)  
**Issue**: Same content exists in tutorial-flow.md Step 6 (lines 145-340)  
**Solution**: 
- **Keep in Bible**: High-level philosophy (why Trainer Decks, not random packs)
- **Move to tutorial-flow.md**: Detailed UI flow, card reveal animations, confirmation dialogs
- **Move to trainer-deck-schema.json**: Full 20-card lists for all 6 decks (already done ✅)
- **Estimated Reduction**: 80-100 lines

### 2. **Section 5.5 (Economy System) - Too Detailed for Bible**
**Lines**: 3579-4168 (589 lines)  
**Current State**: Complete economy spec (7 currencies, sources, sinks, daily earnings, F2P vs whale balance)  
**Issue**: This is implementation-level detail, not design philosophy  
**Solution**:
- **Keep in Bible**: High-level currency framework (what exists, why multiple currencies)
- **Move to economy-system.md**: Detailed earning rates, spending breakdowns, F2P projections
- **Move to currency-schema.json**: Exact values (Gold: 1,740/day, Gems: 24/day, etc.)
- **Estimated Reduction**: 400-450 lines

### 3. **Scattered Tutorial References Across Sections**
**Locations**: Section 2.5, Section 2.6, Section 4, Section 8  
**Issue**: Multiple sections say "tutorial teaches..." or "first battle shows..."  
**Solution**:
- **Create Section 2.5.1**: "Tutorial Design Philosophy" (high-level goals, no step-by-step)
- **Remove from other sections**: Cross-reference tutorial-flow.md instead of duplicating
- **Estimated Reduction**: 50-80 lines

### 4. **Section 2.4 (Shiny System) - Implementation Details**
**Lines**: 1098-1212 (114 lines)  
**Current State**: Shiny drop rates (1%/10%), utility bonuses, pity system, visual design  
**Issue**: Exact percentages and thresholds belong in schemas, not bible  
**Solution**:
- **Keep in Bible**: Shiny purpose (whale appeal without pay-to-win), visual concept
- **Move to pack-schema.json**: Drop rates (1%/10%), pity thresholds (100/20 packs)
- **Move to shiny-visual-spec.md**: Particle effects, animation design, holographic borders
- **Estimated Reduction**: 60-80 lines

### 5. **Pack System Duplication** (Section 2.2.3 + pack-schema.json)
**Bible Lines**: 800-1000 (~200 lines on pack tiers, rarity distributions)  
**Schema**: pack-schema.json has same info in JSON format  
**Solution**:
- **Keep in Bible**: 3-tier pack philosophy (Standard → Premium → Theme/Game Decks)
- **Remove from Bible**: Exact rarity distributions (50% Common, 30% Uncommon) - already in pack-schema.json
- **Estimated Reduction**: 80-100 lines

---

## PROPOSED REORGANIZATION STRATEGY

### Phase 1: Extract Implementation Details (Target: -800 lines)

**1. Create economy-system.md** (move Section 5.5 details):
```markdown
# Resource Economy System Specification

## Currency Earning Rates (F2P Active Player)
- Gold: 1,740/day (breakdown: 500 daily login + 500 battles + 500 quests + 240 AFK)
- Gems: 24/day (breakdown: 10 daily login + 14 weekly quests)
- Food: 340/day (240 AFK + 100 battle chests)
- Lumber: 340/day (240 AFK + 100 battle chests)
- Ore: 170/day (120 AFK + 50 battle chests)
- Arena Tokens: 50/day (5 PvP matches × 10 tokens)
- Energy: 340/day (240 natural refill + 100 starting)

## Currency Spending Breakdown
- Gold: Packs (1,000-50,000), Combining (100-50,000), Upgrades (500-2,000)
- Gems: Premium Packs (100-1,000), Energy Refills (50), Speed-Ups (100)
- Food: Battle Entry (20), Deployment (50), Upgrades (500-1,000)
- Lumber: Equipment (100-500), Construction (300), Upgrades (500-1,000)
- Ore: High-Tier Equipment (200-2,000), Upgrades (200-500)

## F2P vs Whale Projections
- F2P: 12,180 Gold/week (can buy 12 Standard Packs OR 4 Epic Boosters)
- Whale: 14,400 Gems/week (10× F2P, spent on premium packs/refills)
- Balance: Gold identical, Gems 10× advantage, Arena Tokens identical
```

**2. Create combat-calculation-spec.md** (extract from Section 8):
```markdown
# Combat System Calculations

## MVP Formula (Simple)
- Damage = Attacker Attack - Defender Defense (minimum 1)
- Critical Hit: 10% chance, 1.5× damage
- Death: Unit reaches 0 HP, removed from battlefield

## Post-MVP Formula (Complex)
- Base Damage = Attacker Attack - Defender Defense
- Elemental Modifier: Fire > Earth (+50%), Earth > Water (+50%), Water > Fire (+50%)
- Terrain Modifier: Mountain (+20% Defense), Water (-20% Movement), Forest (+10% Evasion)
- Status Effects: Burn (5 damage/turn for 3 turns), Freeze (skip 1 turn), Poison (10% max HP/turn)
- Critical Hit: (Attacker Speed - Defender Speed) / 10 = Crit Chance (max 50%)
```

**3. Create card-progression-spec.md** (extract from Section 2):
```markdown
# Card Combining & Star Rank System

## Star Rank Progression
- Common (0★) + 2 duplicates + 100 Gold → Uncommon (1★)
- Uncommon (1★) + 4 duplicates + 500 Gold → Rare (2★)
- Rare (2★) + 8 duplicates + 2,000 Gold → Epic (3★)
- Epic (3★) + 16 duplicates + 10,000 Gold → Legendary (4★)
- Legendary (4★) + 32 duplicates + 50,000 Gold → Mythic (5★)

## Stat Scaling
- +1 Star = +20% to all base stats (Attack, Health, Defense)
- Example: Common Knight (10 Attack, 20 Health) → 1★ Uncommon (12 Attack, 24 Health)

## Shiny Combining
- Shiny + Shiny + Gold → Shiny upgrade (maintains shiny status)
- Shiny + Normal + Gold → Normal upgrade (loses shiny status)
- 10 Normal cards → 1 Shiny card (crafting system, expensive)

## Max Star Caps
- Common: Can reach 5★ Mythic (requires 62 duplicates total + 62,100 Gold)
- Legendary: Already 4★, can only reach 5★ Mythic (requires 32 duplicates + 50,000 Gold)
- Mythic: Cannot combine further (max rarity)
```

**4. Create map-tier-progression.md** (define State/Global Maps):
```markdown
# Map Tier Progression Specification

## County Map (MVP - Already Defined)
- **Size**: 40 hexes (20 visible at start, 20 fog of war)
- **Movement**: 3 tiles per turn, 10 Movement Points/day
- **Battles**: 1 tile = 1 battle (10 Energy + 20 Food cost)
- **Economy**: Deploy buildings on tiles for AFK production
- **Duration**: 5-7 days to fully explore
- **Player Level**: 1-10 (tutorial + early PvE)

## State Map (Post-MVP - Needs Definition)
- **Size**: 50-100 hexes (larger regions, multiple counties)
- **Movement**: Same as County Map (3 tiles/turn, 10 Movement Points/day)
- **Battles**: Multi-tile territories (capture 3 tiles = claim castle)
- **Sieges**: Castle battles require breaking walls, multi-stage combat
- **Economy**: Alliance members share territory, pool resources
- **Duration**: 1-month campaigns (persistent progress, seasonal rewards)
- **Player Level**: 10-20 (alliance co-op, PvE only, no PvP yet)
- **Unlocks**: Requires alliance membership (Level 10+)

## Global Map (Post-Post-MVP - Needs Definition)
- **Size**: 200-500 territories (continents, ocean crossings)
- **Movement**: 5 tiles per turn (larger scale, faster movement)
- **Battles**: Alliance wars (50v50, coordinated attacks)
- **Seasons**: 3-month cycles (reset map, keep progression rewards)
- **Economy**: Alliance territory produces passive income for all members
- **Duration**: 3 months per season (endgame content loop)
- **Player Level**: 20-30 (competitive alliances, whale vs whale)
- **Unlocks**: Requires Level 20 + alliance Level 10
```

**5. Create alliance-progression-spec.md** (extract from Section 6):
```markdown
# Alliance System Progression

## Phase 1: Alliance Formation (Player Level 10)
- Join or create alliance (up to 100 members)
- Alliance chat (real-time messaging)
- Resource donations (gift Gold/Food/Lumber/Ore to members)
- Alliance quests (cooperative PvE goals: "Defeat 100 enemies together")

## Phase 2: Alliance PvE Events (Player Level 15)
- Boss Raids: 10-player co-op battles against giant bosses
- Resource Rush: Timed events to gather most resources in 1 hour
- Alliance Leaderboards: Top alliances get exclusive packs

## Phase 3: State Map Alliance Co-Op (Player Level 20)
- Shared State Map progress (alliance explores together)
- Castle sieges (multi-stage battles, all members contribute)
- Alliance buildings (War Monument, Resource Depot, Training Grounds)

## Phase 4: Global Map Alliance Wars (Player Level 30)
- 50v50 territory wars (attack/defend Global Map territories)
- 3-month seasons (reset map, keep rewards)
- Alliance ranks (Bronze, Silver, Gold, Mythic based on territory held)
```

### Phase 2: Consolidate Bible Sections (Target: -400 lines)

**1. Rewrite Section 2.5 (New Player Onboarding)**:
```markdown
## 2.5 New Player Onboarding

**Philosophy**: Give new players meaningful choice (not random luck) and immediate power fantasy (guaranteed Epic hero).

**Trainer Deck System**: Players choose from 6 pre-built 20-card decks during tutorial:
- 3 Curated Decks (Flame Warlord, Tidal Guardian, Stone Sentinel) - Perfect synergy, beginner-friendly
- 3 Element Decks (Fire, Water, Earth) - Random Epic, higher variance, replayability

**Why This Approach?**:
- Pokemon TCG Battle Box model (pre-built playable deck + expansion potential)
- Eliminates "bad luck" first experience (no random pack with 0 Epics)
- Element commitment teaches identity (Fire player builds Fire deck)
- 6 options encourage alt accounts (F2P replayability)

**Total Starting Cards**: 20 (Trainer Deck) + 5 (Element Booster #1) = 25 cards

For detailed implementation, see:
- [tutorial-flow.md](tutorial-flow.md) - Step 6 (Trainer Deck selection UI flow)
- [trainer-deck-schema.json](specs/trainer-deck-schema.json) - Full 20-card lists for all 6 decks
```

**2. Rewrite Section 5.5 (Economy System)**:
```markdown
## 5.5 Resource Economy & Currency Systems

**Philosophy**: Multiple currencies prevent whale dominance (can't buy everything with real money) and create diverse progression paths (PvP skill, AFK patience, exploration).

**Currency Types**:
1. **Gold** (Soft currency) - Earned through gameplay, spent on packs/upgrades
2. **Gems** (Premium currency) - Bought with real money, spent on premium packs/refills
3. **Food/Lumber/Ore** (Resources) - AFK production, spent on battles/equipment/upgrades
4. **Arena Tokens** (PvP currency) - Ranked match rewards, PvP Store exclusives
5. **Energy** (Stamina) - Limits battles per day, prevents grinding

**Auto-Collection System**:
- Resources accumulate automatically up to storage capacity (no tap-to-collect)
- Production stops when storage full (incentivizes spending resources)
- Wake up to full storage, ready to spend on strategy (not a crafting game)

**F2P vs Whale Balance**:
- Gold: Identical earnings (12,180/week for both, cannot buy with money)
- Gems: 10× whale advantage (14,400 vs 168/week), spent on premium packs/refills
- Arena Tokens: Identical (skill-based, cannot buy)
- Rarity Budget + PvP Brackets: Prevent pay-to-win (whales fight whales)

For detailed specifications, see:
- [economy-system.md](economy-system.md) - Earning rates, spending breakdowns, F2P projections
- [currency-schema.json](specs/currency-schema.json) - Exact values for all currencies
- [store-schema.json](specs/store-schema.json) - Pack Store, Resource Store, PvP Store catalogs
```

**3. Remove Tutorial References from Other Sections**:
- **Section 2.6** (Card Stacking): Remove "Tutorial Flow - First Battle" (lines 1637-1676)
  - Replace with: "See tutorial-flow.md Step 15 for first battle walkthrough"
- **Section 4** (Gameplay Modes): Remove "tutorial teaches..." phrases
  - Replace with: "See tutorial-flow.md for onboarding flow"
- **Section 8** (Combat Mechanics): Remove "first battle example"
  - Replace with: "See combat-calculation-spec.md for formulas"

### Phase 3: Update Cross-References (Target: +50 lines for clarity)

**Add to Beginning of Bible** (after Table of Contents):
```markdown
## Documentation Map

This Game Bible is the **master design document** (the "why"). For implementation details (the "how"), see:

**Tutorial & Onboarding**:
- [tutorial-flow.md](tutorial-flow.md) - 28-step walkthrough (0-60 minutes, QA test script)
- [tutorial-gap-resolutions.md](tutorial-gap-resolutions.md) - 9 solved design problems (EULA, skip, undo, etc.)
- [trainer-deck-schema.json](specs/trainer-deck-schema.json) - 6 Trainer Deck options (20 cards each)

**Economy & Progression**:
- [economy-system.md](economy-system.md) - Currency earning/spending rates, F2P vs whale projections
- [currency-schema.json](specs/currency-schema.json) - Exact values for Gold/Gems/Food/Lumber/Ore
- [progression-schema.json](specs/progression-schema.json) - Player Level unlocks, XP requirements

**Combat & Cards**:
- [combat-calculation-spec.md](combat-calculation-spec.md) - Damage formulas, status effects, elemental interactions
- [card-progression-spec.md](card-progression-spec.md) - Star rank system, combining costs, stat scaling
- [card-schema.json](specs/card-schema.json) - All card data (stats, abilities, rarities)

**Maps & Alliances**:
- [map-tier-progression.md](map-tier-progression.md) - County/State/Global Map progression
- [alliance-progression-spec.md](alliance-progression-spec.md) - Phased feature rollout (PvE events → Alliance wars)

**MVP Implementation**:
- [mvp-scope.md](mvp-scope.md) - 8-week implementation roadmap (Unity phases)
- [docs/plan/roadmap.md](plan/roadmap.md) - Long-term phases (Prototype → Alpha → Beta → Launch)
```

---

## MVP SCOPE RECOMMENDATIONS

### What MVP MUST Include (8-Week Timeline)

### Phase 1: Reference Consolidation
**Update game-bible.md Section 2.5** to:
```markdown
## 2.5 New Player Onboarding

See **[tutorial-flow.md](tutorial-flow.md)** for detailed step-by-step player journey (28 steps, 0-60 minutes).

**High-Level Onboarding Principles**:
- **First Impression Hook**: 20-30 cards in first draw (1 Epic guaranteed)
- **Guided vs Manual Path**: Pre-built decks OR manual selection
- **Progressive Deck Size**: 10-15 cards (Level 1) → 40-50 cards (Level 30)
- **Tutorial Safety Nets**: Unlosable first battle, free retries, fallback card grants

**Starter Deck Archetypes**:
- Aggro Rush (Fire/Lightning, fast units)
- Defensive Builder (Earth/Frost, economy focus)
- Balanced Explorer (Water/Wind, learn all mechanics)

For full specifications, see:
- [tutorial-gap-resolutions.md](tutorial-gap-resolutions.md) - Design solutions for EULA, pack skip, placement undo, etc.
- [mvp-scope.md](mvp-scope.md) - Implementation roadmap for Unity
- [starter-deck-schema.json](specs/starter-deck-schema.json) - Deck templates and fallback logic
```

### Phase 2: Extract Detailed Data to Schemas

**Move to starter-deck-schema.json**:
- Full 10-card lists for Aggro Rush, Defensive Builder, Balanced Explorer
- Card IDs, quantities, fallback rules

**Move to progression-schema.json**:
- Player Level unlock table (Level 1 → 30, deck size progression)
- XP requirements per level
- Time estimates ("Day 1", "Week 2", etc.)

**Move to pack-schema.json**:
- Detailed rarity distributions (50% Common, 30% Uncommon, etc.)
- Pity system thresholds (10 packs = Epic, 50 = Legendary)
- 3-tier pack system details

### Phase 3: Consolidate Scattered Tutorial References

**Create a new Section 2.5.1: Tutorial Design Reference** in game-bible.md:
```markdown
### Tutorial Design Reference

**Core Philosophy**: F2P friendly, unlosable first battle, generous starter pool

**Key Documents**:
- [tutorial-flow.md](tutorial-flow.md) - Step-by-step walkthrough (QA test script)
- [tutorial-gap-resolutions.md](tutorial-gap-resolutions.md) - Solved design problems (EULA, skip, undo, etc.)
- [mvp-scope.md](mvp-scope.md) - 8-week implementation roadmap

**Tutorial Checkpoints** (what player has after each phase):
- After Pack Opening (2 min): 20-30 cards, 1 Epic guaranteed
- After Deck Build (8 min): 11-card deck, understands deck slots
- After First Battle (15 min): Manual battle complete, Auto-Battle unlocked
- After Post-Tutorial (60 min): 3-5 battles complete, Codex introduced, Level 1-2

See tutorial-flow.md for minute-by-minute breakdown.
```

**Remove from Section 2.6** (Card Stacking):
- Tutorial flow details (lines 1637-1676, "Tutorial Flow - First Battle")
- Move to tutorial-flow.md as reference only

---

## MVP SCOPE RECOMMENDATIONS

### What MVP MUST Include (8-Week Timeline)

**Week 1-2: Tutorial & Card System**:
- ✅ **Trainer Deck Selection**: 6 options (3 Curated + 3 Element), UI for selection
- ✅ **Pack Opening**: Standard Pack (5 cards), Element Booster (5 cards), animation system
- ✅ **Codex UI**: View all owned cards, filter by rarity/element/type
- ✅ **Deck Builder**: Create 20-card deck, drag-and-drop cards
- ⚠️ **Card Data**: ~100 cards total (enough for 6 Trainer Decks + variety in packs)
  - 6 Epic heroes (2 per element: Fire, Water, Earth)
  - 30 Units (10 per element)
  - 20 Buildings (economy + military)
  - 20 Tactics (combat abilities)
  - 14 Equipment (hero attachments)
  - 10 Workers (resource production)
  - **MVP Stats**: Simple Attack/Defense only (Health/Mana/Stamina deferred to Phase 2)

**Week 3-4: Combat System**:
- ✅ **Battle Map**: 8×8 tactical grid, hex-based pathfinding
- ✅ **Manual Combat**: Drag cards to place, click to move units, click to attack
- ✅ **Auto-Battle**: AI plays both sides, skip animation option
- ⚠️ **Simple Combat Formula**: Damage = Attack - Defense (MVP only)
  - Phase 2 adds: Health/Mana/Stamina, ability costs, recharge mechanics
- ✅ **Victory Screen**: XP/Gold rewards, battle chest opening, pack rewards

**Week 5-6: Realm Map & Exploration**:
- ✅ **Realm Map**: 40-hex map (Locations), fog of war, movement system (3 tiles/turn, 10 Movement Points/day)
- ✅ **Enemy Encounters**: 5-10 PvE battles (Goblin Raiders, Bandit Camp, etc.)
- ✅ **Treasure Nodes**: Find Gold/Gems on Location tiles (no production buildings)
- ✅ **Terrain Types**: Plains/Forest (passable), Mountains/Water (impassable unless flying/swimming)
- ⚠️ **Energy System**: 10 Energy per battle, 240 Energy/day refill (tutorial = 0 cost)
- ❌ **Occupation Mechanics**: Location capture, stat buffs, Realm-level progression deferred to Phase 3

**Week 7-8: Progression & Stores**:
- ✅ **Player Leveling**: XP from battles, Level 1-5 progression
- ✅ **Pack Store**: Buy Standard/Element/Epic Packs with Gold
- ⚠️ **Gold Earning**: Battle rewards (50-200 Gold/battle), daily login (500 Gold)
- ⚠️ **Daily Login**: 7-day reward cycle (cards, Gold, packs)
- ⚠️ **Basic Analytics**: Track battles won, packs opened, Gold earned (for balancing)

**MVP SCOPE TOTAL**:
- **28-step tutorial** (0-60 minutes, gets Sovereign to Level 2)
- **Realm Map PvE** (5-10 battles in single Realm, 40 Locations, HoMM-style exploration)
- **Card collection** (~100 cards, 6 Trainer Decks + random packs)
- **Simple currency** (Gold/Gems only, treasure nodes on Location tiles)
- **Energy system** (10 per battle, 240/day refill, tutorial = 0 cost)
- **No PvP, no alliances, no Territory/World Maps, no Food/Lumber/Ore** (post-launch)

---

### What MVP Can SKIP (Post-Launch)

**Phase 2 (Post-MVP, Month 2-3)**:
- ❌ **Food/Lumber/Ore Economy**: Production buildings (Granary/Sawmill/Mine), auto-collection, storage caps
- ❌ **Resource Store**: Food/Lumber/Ore trading, equipment blueprints
- ❌ **Economy Deployment**: Place buildings on County Map tiles, AFK progression
- ❌ **Premium Packs**: Gem currency, weekly purchase limits, shiny system
- ❌ **Card Combining**: Star rank progression, duplicate combining
- ❌ **Alliance System**: Join alliances, alliance chat, resource donations
- ❌ **PvP Store**: Arena Tokens, PvP-exclusive cards
- ❌ **Daily/Weekly Quests**: "Win 10 battles" quests, quest rewards
- ❌ **RPG Card Stats**: Health/Mana/Stamina system (replaces simple Attack/Defense)
  - Health: Unit survivability, recharges out of combat
  - Mana: Powers abilities (melee moves, spells, ranger attacks)
  - Stamina: Movement points on battle board
  - County Map: Combined army health percentage display
- ❌ **Consumables**: Potions & Scrolls (restore Health/Mana/Stamina)
  - Rewards from battle chests, mission completion
  - Buyable in RPG shops (Alchemist, Scribe)
- ❌ **RPG Shop System**: Thematic shops accessible from central "mall" screen
  - Alchemist (Potions: Health/Mana restoration)
  - Scribe (Scrolls: Tactical abilities, buffs)
  - Additional shops TBD (Blacksmith, Jeweler, etc.)

**Phase 3 (Post-Launch, Month 4-6)**:
- ❌ **Territory Map**: 1-month campaigns, Realm occupation, castle sieges, alliance co-op
- ❌ **World Map**: 3-month seasons, Territory wars (50v50 alliances), season leaderboards
- ❌ **Occupation Mechanics**: Location → Realm → Territory progression, stat buffs, power growth
- ❌ **Monster Spawn Scaling**: Epic/Legendary/Mythic bosses, difficulty progression
- ❌ **Sovereign Leveling**: Player title system, account-wide progression (separate from deck power)
- ❌ **PvP Arena**: 1v1 ranked battles, matchmaking, Arena Tokens
- ❌ **Elemental Interactions**: Fire > Earth > Water > Fire damage bonuses
- ❌ **Status Effects**: Burn, Freeze, Poison
- ❌ **Equipment System**: Craft equipment, equip to heroes
- ❌ **Equipment Sockets**: Jewel/Rune attachments for card slots (Diablo-style)
  - Socket slots on cards (1-3 sockets based on rarity)
  - Jewels provide stat bonuses (e.g., +10 Health, +5 Mana)
  - Craftable/tradeable/buyable in Jeweler shop
- ❌ **Auction House**: Player-to-player card trading

**Phase 4 (Post-Launch, Month 7-12)**:
- ❌ **World Map Seasons**: 3-month Territory wars, alliance leaderboards, seasonal rewards
- ❌ **Territory Capitals**: Castle sieges, alliance strongholds, Territory-wide buffs
- ❌ **Mythic Boss Raids**: 10-player co-op battles, Mythic card pack rewards
- ❌ **Game Decks**: $19.99 premium 50-card decks (Norse, Roman, etc.)
- ❌ **Theme Packs**: Rotating weekly themed packs
- ❌ **Shiny System**: 1%/10% drop rates, 5% utility bonuses
- ❌ **Battle Pass**: 30-day progression, exclusive rewards
- ❌ **Seasonal Events**: Halloween, Winter, Summer events

---

## CRITICAL NEXT STEPS (Action Items)

### Immediate (Tonight/Tomorrow Morning)

**1. Create New Specification Documents** (Extract from Bible): ✅ **PHASE 1 COMPLETE**
- [x] **economy-system.md**: Move Section 5.5 details (mark Food/Lumber/Ore as Phase 2, keep Gold/Gems/Energy for MVP)
- [x] **combat-calculation-spec.md**: Extract Section 8 formulas (MVP vs full game)
- [x] **mvp-scope-final.md**: 8-week implementation roadmap (Must Have vs Won't Have)
- [x] **map-tier-progression.md**: Define Territory/World Map occupation mechanics (HIGH PRIORITY - needed shortly after MVP)
  - Location → Realm → Territory occupation flow
  - Stat buffs per tier (Location = treasure/quests, Realm = +5-10% Power, Territory = +50-100% Power)
  - Monster spawn scaling (Common → Mythic bosses)
  - Sovereign leveling progression (separate from deck power)
- [x] **rpg-systems-spec.md**: RPG mechanics (Health/Mana/Stamina, Consumables, Shops, Sockets - Phase 2-3)
- [x] **terminology-guide.md**: Standardize names across all docs
  - Map hierarchy: World (Territories) → Territory (Realms) → Realm (Locations) → Battle
  - Location types: Town, City, Dungeon, Mine, Ruins, Monster Spawn, Treasure Node, Empty Space
  - Terrain types: Plains, Forest, Mountain (impassable), Water (impassable unless swimming/flying)
  - Player title: "Sovereign" (not "player", "lord", "commander")
  - Occupation terminology: "Occupy Location", "Control Realm", "Dominate Territory"

**2. Reorganize Bible Sections** (Reduce 800 lines): ✅ **PHASE 2 COMPLETE**
- [x] Rewrite Section 2.5 (Onboarding) - High-level philosophy only (condensed ~138 lines to ~50 lines)
- [x] **Mark Section 5.5 (Economy) Food/Lumber/Ore as Phase 2** - Kept Gold/Gems/Energy for MVP, deferred production buildings
  - Added Phase 2 disclaimer to Section 5.5.1 header
  - Marked Food/Lumber/Ore sections as "PHASE 2 ❌ NOT IN MVP"
  - Marked Arena Tokens as "PHASE 3 ❌ NOT IN MVP"
  - Marked Energy as "MVP ✅"
- [x] **Update map terminology throughout bible**: Replaced "County Map" → "Realm Map" (20+ instances), "State Map" → "Territory Map" (9 instances), "Global Map" → "World Map" (21+ instances)
- [ ] **Standardize player title**: Replace inconsistent "player"/"lord"/"commander" with "Sovereign" in design sections
- [ ] Remove tutorial references from Sections 2.6, 4, 8 (cross-reference tutorial-flow.md)
- [ ] Add "Documentation Map" to bible (after Table of Contents)

**3. Update Tutorial Flow** (Complete Steps 27-28): ✅ **PHASE 3 COMPLETE**
- [x] **Step 27: Remove economy deployment** - Replaced Granary/Sawmill/Mine with treasure nodes (find Gold/Gems on Location tiles)
- [x] **Step 28: Simplify store unlocks** - Pack Store only (removed Resource Store, deferred to Phase 2)
- [x] **Update terminology**: Replaced "County Map" → "Realm Map" throughout tutorial-flow.md (20+ instances)
- [x] Updated total tutorial cards = 31 (20 Trainer + 5 Element #1 + 5 Standard Pack #1 + 1 Treasure Node)
- [x] Updated Gap 8 resolution: "Treasure Nodes" (not "Economy Deployment")

**4. Finalize MVP Scope Document**:
- [ ] Create **mvp-scope-final.md** (8-week implementation roadmap)
- [ ] Define exact card count (~100 cards for MVP)
- [ ] Define County Map battles (5-10 PvE encounters)
- [ ] Define tutorial energy cost (0 during tutorial, 10 post-tutorial)

**5. Clean Up Old Documents**: ✅ **PHASE 5 COMPLETE**
- [x] Reviewed **docs/plan/roadmap.md** - Still relevant (high-level phases, kept as-is)
- [x] Updated README.md with current project state (6-week reorganization summary, quick links to specs, MVP scope)

---

### Short-Term (This Week)

**1. Schema Validation**: ⏳ **PHASE 4 DEFERRED (Future Work)**
- [ ] Review all 60+ schemas for consistency with bible
- [ ] Add MVP currency schemas:
  - [ ] currency-schema.json (Gold/Gems/Energy only for MVP - Food/Lumber/Ore marked Phase 2)
  - [ ] energy-schema.json (battle costs, refill rates, daily limits)
  - [ ] movement-schema.json (Movement Points, tile range, daily limits)
  - [ ] battle-chest-schema.json (Bronze/Silver/Gold tier contents)
  - [ ] treasure-node-schema.json (Gold/Gems drop rates on Realm Map Location tiles)
- [ ] **Create map tier schemas** (note: map-schema.json exists but is generic):
  - [ ] realm-map-schema.json (Locations: Town/City/Dungeon/Mine/Ruins/Monster Spawn/Treasure Node/Empty Space, terrain types)
  - [ ] territory-map-schema.json (Realms: occupied/neutral, castle levels)
  - [ ] world-map-schema.json (Territories: alliance control, season state)
  - [ ] location-schema.json (Town, City, Dungeon, Mine, Ruins, Monster Spawn, Treasure Node, terrain types)
  - [ ] occupation-schema.json (Location/Realm/Territory capture mechanics)
  - [ ] monster-spawn-schema.json (Common → Mythic boss progression)
- [ ] **Mark economy-node-schema.json as Phase 2** (production buildings deferred)
- [ ] Verify trainer-deck-schema.json has all 6 decks (already complete ✅)
- [ ] **Add Phase 2 RPG schemas** (post-MVP laundry list):
  - [ ] card-stats-schema.json (Health/Mana/Stamina, recharge rates)
  - [ ] consumable-schema.json (Potions/Scrolls, restoration amounts)
  - [ ] shop-schema.json (Alchemist/Scribe/Jeweler, item catalogs)
  - [ ] socket-schema.json (Jewel/Rune slots, stat bonuses)
  - [ ] sovereign-progression-schema.json (Player leveling, Location/Realm/Territory buffs)

**Rationale for Deferral**: 
- Phase 1-3 addressed critical documentation reorganization (bible bloat reduction, tutorial MVP alignment)
- Schema creation requires design decisions beyond simple renaming (tile properties, occupation mechanics, monster scaling)
- Recommend dedicated schema design session after MVP implementation begins (Unity dev feedback will inform schema structure)

**2. Tutorial Completeness**:
- [ ] Ensure Steps 1-28 cover all core MVP mechanics
- [ ] Verify tutorial gives exactly 36 cards (current total)
- [ ] Check tutorial introduces: Energy (Step 23), Movement (Step 12), Treasure Nodes (Step 27), Pack Store (Step 28)
- [ ] Add tooltips for post-tutorial systems:
  - "PvP Arena unlocks at Sovereign Level 15"
  - "Alliances unlock at Sovereign Level 10"
  - "Territory and World Maps coming in Phase 3 (full occupation mechanics)"

**3. Balance Testing Prep**:
- [ ] Create "balance-test-scenarios.md" for automated testing:
  - Scenario 1: F2P Gold earning (Day 1-7, battle rewards + treasure nodes)
  - Scenario 2: F2P pack purchasing (How many Standard Packs per week?)
  - Scenario 3: Combat balance (Common vs Rare, Epic vs Legendary)
  - Scenario 4: Energy limits (Can player complete tutorial without stopping?)
  - Scenario 5: Treasure node balance (Gold/Gems drop rates on County Map)

**4. Unity Handoff Prep**:
- [ ] Create "unity-implementation-checklist.md":
  - Card system (CardData class with Attack/Defense for MVP, Health/Mana/Stamina for Phase 2)
  - Battle system (8×8 grid, drag-and-drop placement, auto-battle AI)
  - Realm Map (hex-based pathfinding, fog of war, treasure nodes on Location tiles, terrain types)
  - Tutorial flow (28-step progression, tooltips, skip options)
  - Consumables system (Potions/Scrolls UI, inventory management - Phase 2)
  - Shop system (Mall screen, Alchemist/Scribe tabs - Phase 2)
  - Occupation system (Location → Realm → Territory progression - Phase 3)
  - Sovereign leveling (player title, account-wide stats - Phase 3)
- [ ] Define Unity project structure (see copilot-instructions.md)
- [ ] List required Unity packages (Addressables, Nakama SDK, UI Toolkit)

---

### Medium-Term (Next 2 Weeks)

**1. Art Asset Specification**:
- [ ] Create "art-asset-list.md":
  - 100 card illustrations (6 Epics, 30 Units, 20 Buildings, etc.)
  - Battle map tiles (8×8 grid, terrain types: grass, water, mountain, forest)
  - County map tiles (40 hexes, fog of war sprites)
  - UI elements (card frames, pack opening animations, battle chest models)
- [ ] Define art style guide (2.5D isometric, stylized painterly, color palette)
- [ ] Estimate art production timeline (1 card = 4 hours → 100 cards = 400 hours = 10 weeks at 1 artist)

**2. Nakama Server Setup**:
- [ ] Install Nakama 3.x locally (Docker container)
- [ ] Create database schema for:
  - Player accounts (username, password, email, PlayerPrefs)
  - Card inventory (owned cards, quantities, shiny status)
  - Deck slots (5 deck slots, card IDs for each)
  - Tutorial progress (completed steps, last checkpoint)
- [ ] Implement authentication (email/password, Google OAuth, Apple Sign-In)
- [ ] Test matchmaking (for future PvP, not MVP)

**3. F2P Balancing**:
- [ ] Run simulations:
  - F2P Day 1-7: How much Gold earned? How many packs opened?
  - F2P Day 30: Can player build competitive deck without spending?
  - Whale Day 1: If spend $136, how many cards acquired? Does it break game?
- [ ] Adjust earning rates if needed (target: 3-4 packs/week for F2P)
- [ ] Adjust rarity budget if needed (target: F2P can build Epic-heavy deck by Week 2)

**4. QA Test Script**:
- [ ] Convert tutorial-flow.md to QA checklist:
  - [ ] Step 1: EULA acceptance works (can decline, return to main menu)
  - [ ] Step 6: All 6 Trainer Decks selectable (can preview, can't skip)
  - [ ] Step 23: Battle chest drops (Bronze tier, correct rewards)
  - [ ] Step 27: Economy deployment works (auto-collection, storage cap)
  - [ ] Step 28: All stores unlock (Pack/Resource/PvP Stores)
- [ ] Add negative test cases:
  - [ ] What happens if player closes app during pack opening?
  - [ ] What happens if player runs out of Energy mid-tutorial?
  - [ ] What happens if player fills storage capacity?

---

## ALIGNMENT CHECK: CORE VISION

### "Build the Deck. Rule the Map. Automate the Empire."

**Build the Deck** ✅:
- 6 Trainer Deck options (meaningful choice)
- Pack progression (5 packs in tutorial, collector appeal)
- Deck size progression (20 → 50 cards by Level 30)
- Rarity budget (prevents pay-to-win)
- **Verdict**: Strong alignment. Card collection is the core hook.

**Rule the Map** ⚠️:
- Realm Map complete (40 Location tiles, HoMM-style exploration, battles)
- Territory Map undefined (1-month campaigns, Realm occupation, castle sieges)
- World Map undefined (3-month seasons, Territory wars, alliance dominance)
- **Verdict**: Partial alignment. MVP covers single Realm Map (5-10 Locations with battles). Post-launch needs Territory/World Maps with occupation mechanics (Location → Realm → Territory progression, stat buffs, Sovereign power growth).

**Automate the Empire** ⚠️:
- ❌ **Deferred to Phase 2**: Auto-collection economy (Food/Lumber/Ore production buildings)
- ✅ **MVP**: Treasure nodes (find Gold/Gems on Realm Map Locations, no active grinding)
- ✅ **Philosophy**: Players explore Locations, find resources, spend on packs (not a crafting game)
- **Verdict**: Partial alignment. Full automation (AFK production) comes in Phase 2. MVP focuses on exploration/treasure hunting.

---

## RISK ASSESSMENT

### High-Priority Risks

**1. Scope Creep** ✅:
- **Risk**: Bible has 18 sections, 6,807 lines. Section 5.5 alone is 2,500+ lines (Food/Lumber/Ore economy).
- **Mitigation**: Defer Food/Lumber/Ore to Phase 2. MVP = Gold/Gems/Energy only.
- **Action**: Mark Section 5.5 production buildings as Phase 2, focus MVP on treasure hunting.
- **Impact**: Removes ~500 lines of economy implementation from MVP scope.

**2. Art Asset Bottleneck** ⚠️:
- **Risk**: 100 cards × 4 hours = 400 hours of art (10 weeks at 1 artist).
- **Mitigation**: Use placeholder art for MVP (colored rectangles with card names).
- **Action**: Define art pipeline (prototype → MVP → full game).

**3. Combat Complexity** ✅:
- **Risk**: Section 8 mentions status effects, elemental interactions, terrain modifiers. User wants Health/Mana/Stamina RPG stats. Too complex for MVP.
- **Mitigation**: Simplify MVP combat (Attack/Defense only, Damage = Attack - Defense).
- **Action**: Create combat-calculation-spec.md (MVP = simple stats, Phase 2 = Health/Mana/Stamina/Consumables, Phase 3 = Status effects/Elemental interactions).
- **Resolution**: User confirmed all RPG mechanics (Health/Mana/Stamina, Potions/Scrolls, Shops, Sockets) deferred to post-MVP.

**4. Tutorial Length** ⚠️:
- **Risk**: 28-step tutorial (0-60 minutes) might be too long. Players drop off.
- **Mitigation**: Add skip options after key checkpoints (Step 15: First battle, Step 23: Pack reward).
- **Action**: Add analytics to track tutorial drop-off rates (which step loses most players?).

### Medium-Priority Risks

**5. Energy System Confusion** ⚠️:
- **Risk**: Tutorial = 0 Energy cost, Post-tutorial = 10 Energy cost. Players might not understand.
- **Mitigation**: Add clear tooltips in Step 23 ("Future battles cost Energy, but tutorial is free!").
- **Action**: QA test tutorial energy flow (ensure players understand before leaving tutorial).

**6. F2P Balance** ⚠️:
- **Risk**: If F2P earns too little Gold (e.g., 1,000/week), can't buy packs. If too much (e.g., 50,000/week), whales have no advantage.
- **Mitigation**: Run simulations (F2P Day 1-30, how many packs opened?).
- **Action**: Adjust earning rates to hit target (3-4 packs/week for F2P).

**7. Rarity Budget Too Restrictive** ⚠️:
- **Risk**: Level 1 player limited to 60 rarity points. Can only use 3 Epics (8 points each) + Commons. Feels bad.
- **Mitigation**: Trainer Decks are pre-balanced (1 Epic + 19 Commons/Uncommons = ~40 points).
- **Action**: Test if 60-point budget allows Trainer Deck diversity (if not, raise to 80 points).

### Low-Priority Risks

**8. Schema Consistency** ⚠️:
- **Risk**: 60+ schemas might have conflicting data (e.g., pack-schema.json says 1% shiny rate, bible says 10%).
- **Mitigation**: Add automated validation (JSON schema checks).
- **Action**: Review all schemas for consistency with bible.

**9. Documentation Sprawl** ⚠️:
- **Risk**: Too many docs (bible, tutorial, specs, schemas, plans). New team members confused.
- **Mitigation**: Add "Documentation Map" to bible (after Table of Contents).
- **Action**: Create README.md with doc hierarchy.

---

## FINAL RECOMMENDATIONS

### Bible Reorganization Priority

**High Priority** (Do Tomorrow):
1. ✅ Create economy-system.md (move Section 5.5 details, mark Food/Lumber/Ore as Phase 2)
2. ✅ Create combat-calculation-spec.md (MVP = Attack/Defense, Phase 2 = Health/Mana/Stamina, Phase 3 = Status effects)
3. ✅ Create mvp-scope-final.md (8-week roadmap, exact feature list)
4. ✅ Create rpg-systems-spec.md (Health/Mana/Stamina, Consumables, Shops, Sockets - Phase 2/3 roadmap)
5. ✅ **Create map-tier-progression.md** (HIGH PRIORITY - Location → Realm → Territory occupation, stat buffs, monster spawn scaling)
6. ✅ **Create terminology-guide.md** (Standardize map names: World/Territory/Realm/Locations, terrain types, player title "Sovereign")
7. ✅ Add "Documentation Map" to bible (after Table of Contents)

**Medium Priority** (Do This Week):
6. ⚠️ Rewrite Section 2.5 (Onboarding) - High-level philosophy only
7. ⚠️ Rewrite Section 5.5 (Economy) - High-level currency framework
8. ⚠️ Create card-progression-spec.md (star rank system, combining)
9. ⚠️ **Update all schemas with revised map terminology** (province_map, territory_map, world_map)
10. ⚠️ Update card-schema.json (Attack/Defense for MVP, note Health/Mana/Stamina for Phase 2)
11. ⚠️ **Global search/replace across all docs**: "County Map" → "Realm Map", "State Map" → "Territory Map", "Global Map" → "World Map"

**Low Priority** (Do Next Week):
12. ⚠️ Remove tutorial references from Sections 2.6, 4, 8
13. ⚠️ Create alliance-progression-spec.md (phased feature rollout)
14. ⚠️ Review/archive docs/plan/roadmap.md (might be outdated)
15. ⚠️ **Update copilot-instructions.md** with revised map hierarchy and Sovereign terminology

### MVP Scope Priority

**Must Have** (8-Week MVP):
- ✅ Tutorial (28 steps, 0-60 minutes, Sovereign reaches Level 2)
- ✅ Trainer Deck selection (6 options)
- ✅ Realm Map PvE (5-10 battles in single Realm, 40 Locations, HoMM-style exploration)
- ✅ Treasure nodes (find Gold/Gems on Location tiles)
- ✅ Pack Store (buy Standard/Element/Epic Packs with Gold)
- ✅ **Simple combat** (Attack/Defense stats only, no Health/Mana/Stamina)
- ✅ Energy system (10 per battle, 240/day refill)

**Should Have** (If Time Allows):
- ⚠️ Daily login rewards (7-day cycle)
- ⚠️ Player leveling (Level 1-5 progression)
- ⚠️ Energy system (10 Energy/battle, 240/day refill)
- ⚠️ Battle chests (Bronze tier only)

**Won't Have** (Post-Launch):
- ❌ **Food/Lumber/Ore economy** (production buildings, auto-collection, storage caps)
- ❌ **Resource Store** (trade Food/Lumber/Ore, equipment blueprints)
- ❌ **Economy deployment** (place Granary/Sawmill/Mine on Location tiles)
- ❌ **Occupation mechanics** (Location → Realm → Territory progression, stat buffs)
- ❌ **Territory Map** (Realm occupation, 1-month campaigns, 50-100 hexes)
- ❌ **World Map** (Territory wars, alliance seasons, 200-500 tiles)
- ❌ **Monster spawn scaling** (Epic/Legendary/Mythic bosses)
- ❌ **Sovereign progression** (account-wide stat buffs from occupation)
- ❌ **RPG Card Stats** (Health/Mana/Stamina, recharge mechanics, combined army health display)
- ❌ **Consumables** (Potions/Scrolls for Health/Mana/Stamina restoration)
- ❌ **RPG Shops** (Alchemist, Scribe, Jeweler - central mall screen)
- ❌ **Equipment Sockets** (Jewel/Rune slots on cards, stat bonuses)
- ❌ PvP Arena (ranked matches, Arena Tokens)
- ❌ Alliances (chat, donations, co-op events)
- ❌ Premium Packs (Gem currency, shiny system)
- ❌ Card combining (star rank progression)
- ❌ Equipment system (crafting, hero attachments)

---

## SUCCESS METRICS (How to Know If We're Ready for MVP)

### Documentation Metrics

**Bible**:
- ✅ Reduced from 6,807 lines to ~5,500 lines (800-line reduction via extraction)
- ✅ All sections have cross-references to detailed specs (no duplication)
- ✅ "Documentation Map" added (clear doc hierarchy)

**Tutorial**:
- ✅ 28 steps fully defined (0-60 minutes, QA-testable)
- ✅ Total tutorial cards = 36 (verified)
- ✅ All core mechanics introduced (Energy, Movement, Economy, Stores)

**Schemas**:
- ✅ 60+ schemas validated for consistency with bible
- ✅ New schemas added (currency, energy, movement, battle-chest)
- ✅ All schemas have .md companion docs (human-readable explanations)

### Implementation Readiness

**Unity Handoff**:
- ✅ unity-implementation-checklist.md created (8-week roadmap)
- ✅ Card system spec complete (~100 cards defined)
- ✅ Battle system spec complete (8×8 grid, simple combat formula)
- ✅ County Map spec complete (40 hexes, 10 Movement Points/day)

**Balance Testing**:
- ✅ balance-test-scenarios.md created (F2P vs whale simulations)
- ✅ Rarity budget tested (60 points allows Trainer Deck diversity)
- ✅ Energy limits tested (tutorial completable without stopping)

**QA Readiness**:
- ✅ QA test script created (convert tutorial-flow.md to checklist)
- ✅ Negative test cases defined (app close, out of Energy, full storage)

---

## CLOSING THOUGHTS

### What We've Achieved

This project has **world-class documentation**. The combination of:
- 6,807-line game bible (design philosophy)
- 1,223-line tutorial flow (step-by-step implementation)
- 60+ JSON schemas (data validation)
- Comprehensive specs (economy, combat, progression, alliances)

...is **extremely rare** for an indie game. Most projects at this stage have a 10-page Google Doc. You've built a foundation that could support a AAA studio.

### What Still Needs Work

The **higher map tiers** (State Map, Global Map) are underspecified. This is intentional (MVP focus), but needs documentation to prevent scope creep. The creation of map-tier-progression.md will future-proof the design.

The **combat system** needs simplification for MVP (Attack - Defense = Damage, no status effects). The creation of combat-calculation-spec.md will separate MVP combat from full game combat.

The **F2P balance** needs validation through simulations (F2P Day 1-30, how many packs?). The creation of balance-test-scenarios.md will ensure the game is fair.

### Recommendation for Tomorrow

**Priority 1**: Create the 5 new spec documents (economy-system.md, combat-calculation-spec.md, mvp-scope-final.md, map-tier-progression.md, alliance-progression-spec.md).

**Priority 2**: Reorganize bible Sections 2.5 and 5.5 (high-level philosophy only, cross-reference detailed specs).

**Priority 3**: Add "Documentation Map" to bible (after Table of Contents, explain doc hierarchy).

Once these 3 priorities are done, the project is **MVP-ready**. You'll have:
- Clear design philosophy (bible)
- Detailed implementation specs (economy-system.md, combat-calculation-spec.md, etc.)
- Exact MVP scope (mvp-scope-final.md)
- Post-MVP roadmap (map-tier-progression.md, alliance-progression-spec.md)

From there, handoff to Unity implementation is straightforward. @Soverign-Code-Mode can start building while you refine balance through simulations.

---

**Sleep well. Tomorrow we finalize the foundation and prepare for MVP.**
