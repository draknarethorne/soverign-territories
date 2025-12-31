# MVP Scope Final - 8-Week Implementation Roadmap

**Last Updated**: December 30, 2025  
**Status**: Ready for Unity implementation  
**Target Completion**: 8 weeks (2 months)  
**Related**: [game-bible.md](game-bible.md), [tutorial-flow.md](tutorial-flow.md), [economy-system.md](economy-system.md)

---

## MVP Philosophy

**Core Focus**: Prove the game loop works before adding complexity.
- ✅ Tutorial (28 steps, 0-60 minutes, gets Sovereign to Level 2)
- ✅ Deck building (6 Trainer Deck options, 20-card decks)
- ✅ Pack opening (Standard/Element/Epic Packs, collector appeal)
- ✅ Realm Map exploration (40 Locations, HoMM-style movement)
- ✅ Simple combat (Attack/Defense, no RPG stats yet)
- ❌ No Food/Lumber/Ore economy (Phase 2)
- ❌ No PvP (Phase 3)
- ❌ No alliances (Phase 3)
- ❌ No Territory/World Maps (Phase 3)

**Success Metric**: Player completes tutorial, builds custom deck, wins 5 Realm Map battles, buys 1 pack with earned Gold. If this feels fun, proceed to Phase 2.

---

## Week-by-Week Breakdown

### Week 1-2: Card System & Tutorial UI

**Card Data** (~100 cards total):
- ✅ 6 Epic heroes (2 per element: Fire, Water, Earth)
  - Flame Warlord, Inferno Pyromancer (Fire)
  - Tidal Guardian, Stormcaller Aquamancer (Water)
  - Stone Sentinel, Earthshaker Geomancer (Earth)
- ✅ 30 Units (10 per element)
  - Fire: Goblin Raiders, Flame Imps, Phoenix Hatchlings
  - Water: Elven Archers, Water Elementals, Sea Serpents
  - Earth: Dwarf Warriors, Stone Golems, Treants
- ✅ 20 Buildings (economy + military)
  - Granary, Sawmill, Mine (Phase 2 economy, art only for MVP)
  - Barracks, Archery Range, Mage Tower (military)
- ✅ 20 Tactics (combat abilities)
  - Fireball, Lightning Bolt, Heal, Shield Wall, Charge
- ✅ 14 Equipment (hero attachments)
  - Wooden Shield, Leather Armor, Iron Sword, Steel Helmet
- ✅ 10 Workers (resource production, Phase 2)
  - Farmers, Lumberjacks, Miners (art only for MVP)

**Stats** (Simple for MVP):
- Attack: 1-100 scale
- Defense: 0-50 scale
- ❌ No Health/Mana/Stamina (Phase 2)

**Tutorial UI**:
- ✅ EULA screen (Step 1)
- ✅ Trainer Deck selection (Step 6, 6 options)
- ✅ Pack opening animation (Steps 6, 23, 27, 28)
- ✅ Codex (view all owned cards, filter by rarity/element)
- ✅ Deck Builder (drag-and-drop, 20-card limit)

**Deliverables**:
- [ ] card-schema.json validated (all 100 cards)
- [ ] CardData C# class (Attack/Defense properties)
- [ ] CardManager singleton (load cards from JSON, cache)
- [ ] Codex UI (Unity UI Toolkit, grid view, filters)
- [ ] Deck Builder UI (drag-drop, validation, save/load)
- [ ] Trainer Deck selection UI (6 buttons, preview cards, confirm)

---

### Week 3-4: Card Fusion & Deck Building

**Card Fusion System** (Star Rank Progression):
- ✅ **Flexible Star Ranks**: Commons 1-3★, Uncommons 1-4★, Rares 2-5★, Epics 3-6★, Legendaries 5-7★, Mythics 6-8★
- ✅ **Fusion Mechanic**: Combine duplicates + Gold to increase star rank
- ✅ **Stat Scaling**: +50% stats per star rank (e.g., 1★→2★ = +50% HP/ATK)
- ✅ **Tactic Slot Unlocks**: Tactic slots = star rank (1★=1 tactic, 2★=2 tactics, etc.)
- ✅ **Rarity Base Multipliers**: Epic base stats = 8× Common base (ensures rarity > star rank)
- ✅ **Visual Progression**: Star count (★★★) + border color (Bronze→Silver→Gold→Platinum→Prismatic)

**Fusion Costs** (MVP - First 3 Rarities):
- Common 1★→2★: 1 duplicate + 500 Gold
- Common 2★→3★: 2 duplicates + 2,000 Gold (MAX: 3 tactics)
- Uncommon 1★→2★: 1 duplicate + 1,000 Gold
- Uncommon 2★→3★: 2 duplicates + 5,000 Gold
- Uncommon 3★→4★: 4 duplicates + 10,000 Gold (MAX: 4 tactics)
- Rare 2★→3★: 2 duplicates + 10,000 Gold
- Rare 3★→4★: 4 duplicates + 20,000 Gold
- Rare 4★→5★: 8 duplicates + 50,000 Gold (MAX: 5 tactics)

**Deck Builder** (6-Slot Battle Formation):
- ✅ **6-Slot System**: Select 6 cards from 20-50 card collection for battle
- ✅ **No Stacking**: Each slot = 1 individual card (can't stack 10 Knights into 1 slot)
- ✅ **Star Rank Progression**: Same card name can be different star ranks (Knight 1★ vs Knight 3★)
- ✅ **Tactic Attachment**: Attach tactics = star rank (3★ card = 3 tactic slots)
- ✅ **Collection View**: Grid of owned cards, sorted by star rank/rarity/element
- ✅ **Auto-Fill Options**: Highest Power, Most Stars, Balanced, Last Used
- ✅ **Visual Feedback**: Star count (★★★), border color (Bronze/Silver/Gold), tactic slot icons
- ✅ **Deck Validation**: Can use same card name at different star ranks (Knight 1★ + Knight 3★ = valid)

**Why Deck Size Matters** (20-50 card collection, 6 active):
- **Variety**: Choose 6 Fire heroes OR 6 Water heroes (element synergy builds)
- **Counter Builds**: Anti-tank deck vs boss, anti-swarm vs hordes
- **Star Rank Options**: Use Knight 3★ OR Knight 1★ depending on tactic budget
- **Future (Phase 2)**: Reserve/Draw system - if unit dies in battle, draw replacement from deck
- **Future (Phase 2)**: Multi-hero armies - split 50-card deck across 3 heroes on Realm Map

**Battle Formation Screen** (Pre-Battle):
```
[Select 6 Cards for Battle]

[Your Collection: 20 cards total]
  ✅ Epic Water Mage (3★) - [Selected, Slot 1] - 80 HP, 40 ATK, 3 Tactic Slots
  ✅ Uncommon Knight (2★) - [Selected, Slot 2] - 30 HP, 15 ATK, 2 Tactic Slots
  ✅ Common Healer (2★) - [Selected, Slot 3] - 15 HP, 7.5 ATK, 2 Tactic Slots
  ✅ Common Archer (2★) - [Selected, Slot 4] - 15 HP, 7.5 ATK, 2 Tactic Slots
  ✅ Common Scout (1★) - [Selected, Slot 5] - 10 HP, 5 ATK, 1 Tactic Slot
  ✅ Uncommon Knight (1★) - [Selected, Slot 6] - 20 HP, 10 ATK, 1 Tactic Slot
  ⬜ Common Healer (1★) - Not selected (weaker than 2★ version)
  ⬜ Building (Granary) - Grayed out (can't use in battles, Realm Map only)
  ... (12 more cards not selected)

[Tactic Assignment Screen]:
  Slot 1: Water Mage (3★) → [Arcane Focus] [Regeneration] [Time Warp] (3 tactics attached)
  Slot 2: Knight (2★) → [Charge] [Guardian] (2 tactics attached)
  Slot 3: Healer (2★) → [Defensive Ward] [AOE Blessing] (2 tactics attached)
  Slot 4: Archer (2★) → [Volley] [Poison Arrows] (2 tactics attached)
  Slot 5: Scout (1★) → [Smoke Bomb] (1 tactic attached)
  Slot 6: Knight (1★) → [Charge] (1 tactic attached)

Total Cards Used: 6 units + 11 tactics = 17 cards from 20-card deck

[Button: Start Battle]
```

**Combat System** (8×8 Tactical Grid):
- ✅ **6 Active Units**: Player's 6-slot formation spawns on grid in preset positions
- ✅ **Preset Spawn Positions**:
  - Slot 1 (Hero): Center-front (Row 5, Col 4)
  - Slots 2-3: Front flanks (Row 5, Cols 3 & 5)
  - Slots 4-5: Back line (Row 6, Cols 3 & 5)
  - Slot 6: Support (Row 6, Col 4)
- ✅ **Turn-Based Combat**: Player turn → AI turn → repeat until victory/defeat
- ✅ **Movement**: Click unit → click tile (3-5 tiles/turn based on unit speed stat)
- ✅ **Attack**: Click unit → click enemy in range → damage calculation
- ✅ **Tactic Activation**: Passive tactics (always on), Active tactics (triggered by conditions)
- ✅ **Win Condition**: All enemy units destroyed
- ✅ **Loss Condition**: All player units destroyed (hero death = instant loss for MVP)

**Stat Calculation** (Base × Star Multiplier):
- **Rarity Base Stats**: Common=10 HP, Uncommon=20 HP, Rare=40 HP, Epic=80 HP, Legendary=160 HP, Mythic=320 HP
- **Star Multiplier**: 1★=1×, 2★=1.5×, 3★=2.25×, 4★=3.375×, 5★=5.06×, 6★=7.59×, 7★=11.39×, 8★=17.09×
- **Example**: 3★ Epic = 80 HP base × 2.25 = 180 HP
- **Example**: 3★ Common = 10 HP base × 2.25 = 22.5 HP (Epic still 8× stronger at same star rank!)

**Tactic Effects** (Examples for MVP):
- **Charge** (Common, 1★): Attack twice on first turn
- **Guardian** (Common, 1★): +20% HP, reduce damage to adjacent allies by 10%
- **Volley** (Uncommon, 2★): Attack 3 enemies at once (50% damage each)
- **Defensive Ward** (Uncommon, 2★): +50% damage reduction, heal 5 HP when blocking
- **Regeneration** (Rare, 3★): Heal 10% max HP per turn
- **AOE Blessing** (Rare, 3★): Heal all allies for 5 HP/turn
- **Time Warp** (Epic, 4★): Take 2 turns in a row (5-turn cooldown)
- **Annihilation** (Legendary, 5★): Instant kill 1 enemy (once per battle)

**Deliverables**:
- [ ] **CardFusionManager.cs** (combine duplicates, star rank up, stat recalculation)
- [ ] **FusionUI scene** (drag duplicates to fuse, show before/after stats, border glow animation)
- [ ] **DeckBuilderUI scene** (6-slot selection grid, tactic attachment UI, auto-fill button)
- [ ] **CardHPPersistence system** (save HP values between battles, show HP bars on deck screen)
- [ ] **HealingSystem.cs** (Gold cost heal, rest timer, checkpoint auto-heals)

**Persistent HP System** (NEW - deck size matters):
- ✅ **Cards keep HP between battles** (don't auto-heal to full after victory)
- ✅ **Dead/injured cards rest for 3 stages** (auto-heal after) OR heal instantly with Gold
- ✅ **Heal costs**: 
  - 100 Gold per card (instant full HP)
  - 500 Gold for all cards (bundle discount)
- ✅ **Auto-heal checkpoints**: 
  - 50% HP restore after mini-boss (Stage X-5)
  - 100% HP restore after world boss (Stage X-9)
- ✅ **Deck rotation strategy**: Use fresh cards (100% HP) while injured ones rest
- ✅ **Healer value**: Heal allies mid-battle to reduce post-battle Gold costs
- ✅ **Visual feedback**: HP bars on deck selection screen (green=>yellow=>red)

**Example HP Flow**:
```
After Battle (Stage 1-1):
  Epic Water Mage: 60/80 HP (took 20 damage, still usable)
  Knight #1: 10/30 HP (33% HP, risky to use)
  Healer: 0/20 HP (DEAD, must rest OR heal)
  Archer: 8/15 HP (53% HP, usable but weak)
  Scout: 15/15 HP (100% HP, untouched)
  Knight #2: 25/30 HP (83% HP, light damage)

Pre-Battle (Stage 1-2):
  [Deck Status]:
  ✅ Water Mage (60/80, 75% HP) - READY (yellow HP bar)
  ⚠️ Knight #1 (10/30, 33% HP) - RISKY (red HP bar)
  ❌ Healer (0/20, DEAD) - RESTING (2 stages left, grayed out)
  ✅ Archer (8/15, 53% HP) - READY (yellow HP bar)
  ✅ Scout (15/15, 100% HP) - READY (green HP bar)
  ✅ Knight #2 (25/30, 83% HP) - READY (green HP bar)
  
  [Available Reserves]:
  ✅ Archer #2 (15/15, 100% HP) - FRESH
  ✅ Scout #2 (15/15, 100% HP) - FRESH
  ✅ Knight #3 (30/30, 100% HP) - FRESH
  ... (11 more fresh cards)

  [Player Options]:
  Option A: Replace dead Healer with Archer #2 (free, rotation)
  Option B: Heal Healer for 100 Gold (instant use)
  Option C: Heal ALL cards for 500 Gold (whale option)
  Option D: Wait 2 stages, Healer auto-heals for free
  
Selected Formation:
  [Slot 1]: Water Mage (60/80, damaged but strong)
  [Slot 2]: Knight #3 (30/30, FRESH from reserves)
  [Slot 3]: Archer #2 (15/15, FRESH from reserves)
  [Slot 4]: Archer #1 (8/15, wounded but usable)
  [Slot 5]: Scout (15/15, undamaged)
  [Slot 6]: Knight #2 (25/30, light damage)

Why 20-card deck matters:
  - 6 cards in battle took damage
  - 14 cards fresh in reserves
  - Need backups for injured rotation
  - Smaller deck = forced healing costs (monetization)
```
- [ ] **TacticData.cs** (ScriptableObject: effect type, trigger condition, stat modifiers, cooldowns)
- [ ] **BattleFormationUI** (pre-battle screen showing 6 selected cards + attached tactics)
- [ ] **Star rank visuals** (★★★ display on cards, border colors: Bronze/Silver/Gold/Platinum)
- [ ] **BattleMap C# class** (8×8 grid, preset spawn coordinates for 6 player units + 6 enemy units)
- [ ] **BattleManager singleton** (turn system, tactic activation logic, win/loss detection)
- [ ] **Movement system** (click unit → highlight valid tiles → click to move, A* pathfinding)
- [ ] **Attack system** (click enemy in range, calculate damage with tactic modifiers, death animation)
- [ ] **Auto-Battle AI** (tactic-aware: prioritize targets, use cooldowns strategically)
- [ ] **Victory screen UI** (XP/Gold/Card rewards, fusion prompt if duplicate earned)

---

### Week 5-6: Combat System

**Battle Map**:
- ✅ 8×8 hex grid (64 tiles total)
- ✅ Terrain types: Plains only (Mountains/Water in Phase 3)
- ✅ Fog of war: None for MVP (reveal all tiles)
- ✅ Camera: Top-down isometric, drag to pan, pinch to zoom

**Manual Combat**:
- ✅ 6-card formation spawns on grid (preset positions based on slot numbers)
- ✅ Click unit to select, click tile to move (highlight valid moves)
- ✅ Click enemy to attack (damage = ATK - DEF, tactic modifiers applied)
- ✅ Turn-based: Player → AI → Player (no simultaneous moves)
- ✅ **HP Reduction**: Units lose HP when attacked, die at 0 HP
- ✅ **Healer Mechanics**: Healer units can target allies to restore HP (reduces post-battle Gold costs)
- ✅ **Tactic Activation**: Passive tactics (always on), Active tactics (click to activate with cooldowns)

**Auto-Battle**:
- ✅ AI plays both sides (skip animation option)
- ✅ Simple AI: Attack nearest enemy, prioritize low-Defense targets
- ✅ Speed controls: 1×, 2×, 4× speed, or instant resolve

**Victory Screen**:
- ✅ XP gained (50-200 based on enemy difficulty)
- ✅ Gold reward (50-200 based on enemy difficulty)
- ✅ Card reward (1-3 cards based on stage, duplicates trigger fusion prompt)
- ✅ **HP Damage Summary**: Show which cards took damage, current HP vs max HP
- ✅ **Healing Options**:
  - Free: Dead cards rest for 3 stages (grayed out in deck)
  - 100 Gold: Heal 1 card to full HP instantly
  - 500 Gold: Heal all cards to full HP (bundle discount)
- ✅ **Auto-Heal Checkpoints**: Mini-boss (X-5) = 50% HP restore, World boss (X-9) = 100% HP restore
- ✅ Battle chest opening (Bronze tier for MVP)
- ✅ **Fusion Prompt** (if duplicate earned): "You have 2 Knights! Fuse to rank up?"

**Deliverables**:
- [ ] **CardFusionManager.cs** (combine duplicates, star rank up, stat recalculation)
- [ ] **FusionUI scene** (drag duplicates to fuse, show before/after stats, border animation)
- [ ] **DeckBuilderUI scene** (6-slot selection, tactic attachment, auto-fill options, HP bars)
- [ ] **CardHPPersistence.cs** (save HP values after battle, load into deck builder, rest timer)
- [ ] **HealingSystem.cs** (Gold cost validation, instant heal, rest countdown, checkpoint auto-heal)
- [ ] **TacticData.cs** (ScriptableObject for tactic effects, triggers, cooldowns)
- [ ] **BattleFormationUI** (show 6 selected cards + tactics + current HP before battle starts)
- [ ] **BattleMap C# class** (8×8 grid, preset spawn positions for 6 units)
- [ ] **BattleManager singleton** (turn system, tactic activation, HP tracking, win/loss conditions)
- [ ] **Movement system** (click unit → click tile, A* pathfinding)
- [ ] **Attack system** (click enemy, damage calculation, HP reduction, tactic modifiers, death animation)
- [ ] **Healing mechanics** (Healer targets ally, restore HP, show heal numbers)
- [ ] **Auto-Battle AI** (tactic-aware: prioritize targets, use cooldowns, heal allies when low HP)
- [ ] **VictoryScreen UI** (XP/Gold/Cards, HP damage summary, healing options, fusion prompts)
- [ ] **Auto-Battle AI** (basic targeting, tactic-aware behavior)
- [ ] **Victory screen UI** (XP/Gold/Card display, fusion prompt for duplicates)
- [ ] **Star rank visuals** (★★★ display, border colors: Bronze/Silver/Gold/Platinum)

---

### Week 5-6: Campaign Mode & Stage Progression

**Campaign Structure**:
- ✅ 8 Worlds × 9 Stages = 72 total battles (linear progression)
- ✅ World themes: Goblin Plains, Bandit Forests, Orc Wastelands, Undead Crypts, Dragon Peaks, Demon Wastes, Celestial Realm, Void Dimension
- ✅ Boss battles: Stages X-5 (mini-boss), X-9 (world boss)
- ✅ Unlock system: Beat Stage 1-1 to unlock 1-2, beat 1-9 to unlock World 2
- ✅ 3-star rating: Speed (under 10 turns), No Deaths (full army survives), Full Health (hero >80% HP)

**Stage Types**:
- ✅ Regular stages (1-1 to 1-4, 1-6 to 1-8): 3-7 card enemy decks, increasing difficulty
- ✅ Mini-boss stages (X-5): 7-10 card decks, Rare/Epic heroes
- ✅ World boss stages (X-9): 12-15 card decks, Epic/Legendary heroes
- ✅ Final boss (8-9): Mythic Void Lord, 20-card deck

**Rewards Per Stage**:
- ✅ First clear: 100-500 Gold, 50-200 XP, 1-3 cards (rarity increases with world)
- ✅ 3-star clear: +1 Epic card (choice from 3 options)
- ✅ Replays: 50% reduced rewards (encourages progression over farming)

**Daily Event**:
- ✅ Daily Challenge Stage: Random unlocked stage, 2× rewards, 3 attempts/day
- ✅ Total daily value: ~1,000 Gold (= 1 Standard Pack purchase incentive)

**Energy System**:
- ✅ Tutorial battles (Stages 1-1 to 1-4): 0 Energy (unlosable)
- ✅ Post-tutorial battles: 10 Energy per battle
- ✅ Daily refill: 240 Energy/day (24 battles max)
- ✅ Starting Energy: 100 (10 battles to start)

**Deliverables**:
- [ ] CampaignManager C# class (stage unlocking, progression tracking, 3-star rating)
- [ ] Stage Select UI (world map view, 9 stage icons per world, lock/unlock states)
- [ ] 3-star rating system (turn count, deaths, hero health tracking)
- [ ] Enemy AI decks (72 pre-built decks, JSON data files)
- [ ] Daily Challenge system (random stage selection, timer, 2× rewards multiplier)
- [ ] Replay rewards reduction (50% Gold/XP after first clear)

**What Moves to Phase 2**:
- ❌ Realm Map (40-tile hex grid) - Phase 2 Months 4-6
- ❌ Open-world exploration - Phase 2
- ❌ Fog of war, Movement Points - Phase 2
- ❌ Territory occupation - Phase 2
- ❌ AFK economy cards - Phase 2

---

### Week 7-8: Progression, Stores & Monetization

**Player Leveling**:
- ✅ Level 1-5 progression (tutorial ends at Level 2)
- ✅ XP requirements: Level 1 = 0, Level 2 = 100, Level 3 = 300, Level 4 = 600, Level 5 = 1,000
- ✅ XP sources: Battle wins (50-200 XP), quest completion (Phase 2)

**Pack Store**:
- ✅ Standard Pack (5 cards): $0.99 OR 1,000 Gold
- ✅ Element Booster (5 cards): $1.99 OR 2,000 Gold
- ✅ Epic Booster (5 cards): $4.99 OR 5,000 Gold
- ✅ Mega Pack (20 cards, 1 Legendary): $19.99 (money only, whale bait)
- ✅ Pack opening animation (reveal 1 card at a time, skip option)

**Battle Pass**:
- ✅ Monthly season: $4.99 (30-day cycle)
- ✅ Free Track: 5 Standard Packs, 2,000 Gold, 100 Gems
- ✅ Paid Track: 10 Standard Packs, 1 Epic Booster, 1 Exclusive Legendary, 5,000 Gold, 500 Gems
- ✅ Progress: 10 XP per battle, 3,000 XP to max (300 battles = ~10-15 days)

**Energy Refills**:
- ✅ Small Refill: $0.99 (100 Energy = 10 battles)
- ✅ Large Refill: $3.99 (500 Energy = 50 battles)
- ✅ Daily Unlimited: $9.99 (infinite battles for 24 hours)

**First-Time Offers** (one-time only):
- ✅ Starter Pack: $0.99 (2 Standard Packs, 500 Gold, 100 Gems, first 7 days)
- ✅ New Player Bundle: $4.99 (1 Epic Booster, 1 Legendary choice, 2,000 Gold, first 14 days)
- ✅ Whale Welcome Pack: $49.99 (5 Mega Packs, 1 Mythic, 30-day Battle Pass, first 30 days)

**Gold Earning**:
- ✅ Battle rewards: 50-200 Gold per battle
- ✅ Daily login: 500 Gold (7-day cycle)
- ✅ Battle chests: 50-500 Gold (Bronze tier for MVP)
- ✅ Total daily: ~700 Gold/day (500 login + 200 battles)

**Daily Login**:
- ✅ 7-day reward cycle:
  - Day 1: 500 Gold
  - Day 2: 1× Common card
  - Day 3: 500 Gold
  - Day 4: 1× Uncommon card
  - Day 5: 1,000 Gold
  - Day 6: 1× Rare card
  - Day 7: 1× Standard Pack (5 cards)
- ✅ Resets weekly (Day 8 = Day 1)

**Analytics** (Basic Tracking):
- ✅ Battles won/lost
- ✅ Packs opened (Standard/Element/Epic)
- ✅ Gold earned/spent
- ✅ Tutorial completion rate (% of players who finish 28 steps)
- ✅ Session length (average time per session)

**Deliverables**:
- [ ] PlayerLevel C# class (XP tracking, level-up rewards)
- [ ] PackStore UI (buy packs with Gold OR money, IAP integration)
- [ ] BattlePass system (30-day season, Free/Paid tracks, XP progression)
- [ ] EnergyRefill system (IAP, instant refill)
- [ ] FirstTimeOffer system (one-time bundles, 7/14/30 day timers)
- [ ] DailyLogin system (7-day cycle, reward claims)
- [ ] Analytics tracking (Nakama server, Unity Analytics, revenue tracking)
- [ ] Gold/Gem display UI (current balances, earn/spend notifications)

---

## Total MVP Scope

### What's Included (8-Week Deliverables)

**Core Systems**:
- ✅ Tutorial (28 steps, 0-60 minutes)
- ✅ Card system (~100 cards, simple Attack/Defense stats)
- ✅ Deck building (6 Trainer Decks, drag-drop builder)
- ✅ Combat (8×8 battle map, manual + auto-battle)
- ✅ Campaign Mode (72 stages, 8 worlds, 3-star rating)
- ✅ Daily Challenge (bonus rewards, login incentive)
- ✅ Pack Store (Standard/Element/Epic/Mega packs, IAP integration)
- ✅ Battle Pass ($4.99/month, exclusive rewards)
- ✅ Energy Refills ($0.99-$9.99, whale monetization)
- ✅ Energy system (10 per battle, 240 refill/day)
- ✅ Pack Store (Standard/Element/Epic Packs, Gold only)
- ✅ Daily login (7-day reward cycle)
- ✅ Player leveling (Level 1-5 progression)

**Total Content**:
- ✅ 100 cards (6 Epics, 30 Units, 20 Buildings, 20 Tactics, 14 Equipment, 10 Workers)
- ✅ 6 Trainer Decks (20 cards each)
- ✅ 5 packs in tutorial (20 Trainer + 5 Element #1 + 6 Step 23 + 5 Element #2 = 36 cards)
- ✅ 5-10 PvE battles (Realm Map enemies)
- ✅ 1 Realm Map (40 Locations, single-player only)

---

### What's Deferred (Post-MVP)

**Phase 2 (Month 2-3)**:
- ❌ Food/Lumber/Ore economy (production buildings, auto-collection)
- ❌ RPG card stats (Health/Mana/Stamina)
- ❌ Consumables (Potions/Scrolls)
- ❌ RPG shops (Alchemist, Scribe, Jeweler)
- ❌ Premium Packs (Gem currency, 10% shiny rate)
- ❌ Card combining (star rank progression)
- ❌ Daily/Weekly quests

**Phase 3 (Month 4-6)**:
- ❌ Territory Map (Realm occupation, 1-month campaigns)
- ❌ World Map (Territory wars, 3-month seasons)
- ❌ Occupation mechanics (Location → Realm → Territory)
- ❌ PvP Arena (1v1 ranked matches)
- ❌ Alliances (chat, donations, co-op events)
- ❌ Elemental interactions (Fire > Earth > Water)
- ❌ Status effects (Burn, Freeze, Poison)
- ❌ Equipment sockets (Jewel/Rune attachments)

**Phase 4 (Month 7-12)**:
- ❌ Alliance wars (50v50 Territory battles)
- ❌ Game Decks ($19.99 premium 50-card decks)
- ❌ Shiny system (1%/10% drop rates)
- ❌ Battle Pass (30-day progression)
- ❌ Seasonal events (Halloween, Winter, Summer)

---

## Implementation Order (Critical Path)

### Week 1 (Foundation)
1. Unity project setup (2021+ LTS, UI Toolkit, Addressables)
2. Nakama server setup (Docker, PostgreSQL, authentication)
3. Card data loading (JSON → C# CardData class)
4. Codex UI (grid view, filters, card preview)

### Week 2 (Deck Building)
5. Deck Builder UI (drag-drop, 20-card limit, save/load)
6. Trainer Deck selection UI (6 options, preview, confirm)
7. Tutorial flow (Steps 1-6, EULA → Trainer Deck selection)

### Week 3 (Combat Foundation)
8. Battle Map (8×8 hex grid, camera controls)
9. Unit placement (drag cards to board, validation)
10. Movement system (click to move, A* pathfinding)
11. Attack system (click enemy, damage calculation)

### Week 4 (Combat Polish)
12. Auto-Battle AI (basic targeting, speed controls)
13. Victory screen (XP/Gold display, chest opening)
14. Tutorial flow (Steps 7-15, first battle walkthrough)

### Week 5 (Realm Map Foundation)
15. Realm Map (40-hex map, fog of war, camera)
16. Movement system (3 tiles/turn, 10 Movement Points/day)
17. Enemy encounters (5-10 battles, simple AI)

### Week 6 (Realm Map Polish)
18. Treasure nodes (Gold/Gems, collect on entry)
19. Energy system (10 per battle, 240 refill/day)
20. Tutorial flow (Steps 16-27, Realm Map exploration)

### Week 7 (Stores & Progression)
21. Pack Store UI (buy packs, opening animation)
22. Daily login system (7-day cycle, reward claims)
23. Player leveling (XP tracking, level-up rewards)

### Week 8 (Polish & QA)
24. Tutorial flow (Step 28, tutorial complete)
25. Analytics tracking (Nakama, Unity Analytics)
26. Bug fixes (QA testing, balance tweaks)
27. Build for iOS/Android/PC (test on devices)

---

## Success Criteria (MVP Complete)

### Technical Metrics
- ✅ All 28 tutorial steps playable (0 crashes)
- ✅ All 100 cards loadable (0 missing data errors)
- ✅ Battle system works (manual + auto-battle)
- ✅ Realm Map works (movement, fog of war, encounters)
- ✅ Pack Store works (buy with Gold, opening animation)
- ✅ Builds run on iOS/Android/PC (60 FPS, <100 MB download)

### Player Experience Metrics
- ✅ Tutorial completion rate: >70% (target 80%)
- ✅ Average session length: 15-30 minutes
- ✅ Battles won (first 5 battles): >80% win rate (tutorial is easy)
- ✅ Packs bought (first week): Average 2-3 packs per player
- ✅ Retention (Day 1): >50% (target 60%)
- ✅ Retention (Day 7): >20% (target 30%)

### Go/No-Go Decision
- **GO to Phase 2** if:
  - Tutorial completion >70%
  - Day 7 retention >20%
  - Players buy packs with earned Gold (monetization proven)
  - Combat feels fun (manual + auto-battle balance)

- **PIVOT** if:
  - Tutorial drop-off >50% (too long/confusing)
  - Players don't buy packs (economy broken)
  - Combat feels tedious (consider simplifying further)

---

## Dependencies & Risks

### Critical Dependencies
- ✅ Unity 2021+ LTS (stable version)
- ✅ Nakama 3.x (Docker deployment, PostgreSQL)
- ✅ Card art (100 cards × 4 hours = 400 hours = 10 weeks at 1 artist)
  - **Mitigation**: Use placeholder art for MVP (colored rectangles with card names)
- ✅ UI/UX design (Codex, Deck Builder, Battle Map, Realm Map)
  - **Mitigation**: Use Unity UI Toolkit default styles, polish in Phase 2

### High Risks
- ⚠️ **Scope Creep**: Adding Phase 2 features to MVP (Health/Mana/Stamina, Food/Lumber/Ore)
  - **Mitigation**: Strict feature freeze after Week 6, focus on polish
- ⚠️ **Tutorial Length**: 28 steps (0-60 minutes) might be too long
  - **Mitigation**: Add skip options after Step 15 (first battle), track analytics
- ⚠️ **Art Asset Bottleneck**: 100 cards need illustrations
  - **Mitigation**: Placeholder art for MVP, commission real art in Phase 2
- ⚠️ **Combat Balance**: Simple Attack/Defense might be too basic
  - **Mitigation**: Test with 10-20 players, iterate formulas, add complexity in Phase 2

---

## Next Steps (After MVP)

### Phase 2 Priorities (If MVP Successful)
1. RPG card stats (Health/Mana/Stamina)
2. Consumables (Potions/Scrolls from battle chests)
3. RPG shops (Alchemist, Scribe, mall screen)
4. Food/Lumber/Ore economy (production buildings, auto-collection)
5. Premium Packs (Gem currency, 10% shiny rate)

### Phase 3 Priorities (If Phase 2 Successful)
1. Territory Map (Realm occupation, 1-month campaigns)
2. PvP Arena (1v1 ranked matches, Arena Tokens)
3. Alliances (chat, donations, PvE events)
4. Elemental interactions (Fire > Earth > Water)
5. Status effects (Burn, Freeze, Poison)

---

**For combat details, see**: [combat-calculation-spec.md](combat-calculation-spec.md)  
**For economy details, see**: [economy-system.md](economy-system.md)  
**For RPG systems, see**: [rpg-systems-spec.md](rpg-systems-spec.md)  
**For map progression, see**: [map-tier-progression.md](map-tier-progression.md)  
**For tutorial flow, see**: [tutorial-flow.md](tutorial-flow.md)
