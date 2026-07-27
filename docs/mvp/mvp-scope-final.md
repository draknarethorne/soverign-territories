# MVP Scope Final - Implementation Roadmap

**Last Updated**: January 10, 2026  
**Status**: Ready for Unity implementation  
**Target Completion**: 16-24 weeks solo dev (see [solo-dev-realistic-mvp.md](solo-dev-realistic-mvp.md) for realistic timeline)  
**ASPIRATIONAL Timeline**: 8 weeks full-time team (original estimate, NOT REALISTIC for solo dev)  
**Related**: [game-bible.md](../game-bible.md), [starter-deck-design.md](../design/starter-deck-design.md), [campaign-structure.md](../design/campaign-structure.md)

---

## ⚠️ TIMELINE CLARIFICATION (January 10, 2026)

**This document's "8-week" estimate assumed**:
- Full-time team (40-60 hours/week per person)
- 2-3 developers (Unity dev, backend dev, UI/UX designer)
- Pre-existing art assets or contractor support

**ACTUAL Reality for Solo Dev**:
- Part-time solo developer (10-15 hours/week)
- Learning Unity + Nakama from scratch
- Creating all systems, art, design simultaneously
- **Realistic Timeline**: 16-24 weeks (see [solo-dev-realistic-mvp.md](solo-dev-realistic-mvp.md))

**Use This Document For**:
- ✅ Feature scope definition (what's in MVP vs Phase 2)
- ✅ Week-by-week feature breakdown (use as template, multiply by 2-3×)
- ✅ Dependency mapping (what must be built first)

**Use [solo-dev-realistic-mvp.md](solo-dev-realistic-mvp.md) For**:
- ✅ Actual sprint planning
- ✅ Realistic milestone dates
- ✅ Risk mitigation strategies

---

## ✅ July 2026 Baseline Re-Alignment (Authoritative Override)

To stay consistent with current project direction and solo-dev constraints:

- **MVP baseline** = tutorial + pack opening + deck building + deterministic tactical combat + linear PvE campaign + foundational progression.
- **Phase 1.1 stretch** = async arena, scroll crafting, and expanded monetization loops.
- **MVP completion does not require** live/async PvP, battle pass, VIP systems, or advanced map conquest layers.

If this document conflicts with `solo-dev-realistic-mvp.md`, use the solo-dev file as scheduling/scope authority.

---

## MVP Philosophy

**Core Focus**: Prove the game loop works before adding complexity.
- ✅ Tutorial (discovery-based, 5-minute onboarding, achievement rewards)
- ✅ Deck building (6-slot formation, tactic attachment, star ranks)
- ✅ Pack opening (Standard/Element/Epic Packs, collector appeal)
- ⚠️ **Crafting System** (scroll-based, targeted card acquisition) - Phase 1.1 stretch if core MVP is stable
- ⚠️ **Async Arena PvP** (matchmade battles, Colosseum Tokens) - Phase 1.1 stretch if core MVP is stable
- ✅ Campaign Mode (60-80 battles, 4 Territories, 9 Realms, boss fights)
- ✅ Combat (8×8 tactical grid, auto-battle + manual, tactic AI control)
- ❌ No Food/Lumber/Ore economy (Phase 2)
- ❌ No live PvP (async only for MVP, live in Phase 2)
- ❌ No alliances (Phase 3)
- ❌ No Territory/World Maps (Phase 3)

**Success Metric**: Player completes tutorial, builds custom deck, wins 10 battles, and buys 1 pack with earned Gold. If this feels fun, proceed to Phase 1.1 stretch features.

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

**Stats** (RPG Standard):
- **Health**: 10-100 scale (death at 0 HP)
- **Mana**: 10-100 scale (tactics cost mana, basic attack FREE)
- **Attack**: 1-100 scale
- **Defense**: 0-50 scale
- ✅ Health + Mana (RPG standard, prevents tactic spam)

**Tutorial UI**:
- ✅ EULA screen (Step 1)
- ✅ Trainer Deck selection (Step 6, 6 options)
- ✅ Pack opening animation (Steps 6, 23, 27, 28)
- ✅ Codex (view all owned cards, filter by rarity/element)
- ✅ Deck Builder (drag-and-drop, 20-card limit)

**Deliverables**:
- [ ] card-schema.json validated (all 100 cards, add Health/Mana to all cards)
- [ ] CardData C# class (Health, Mana, Attack, Defense properties)
- [ ] CardManager singleton (load cards from JSON, cache, track current HP/Mana)
- [ ] **Inventory System** (Gold, Gems, Stamina, **Resurrection Scrolls**, **Potions**, future items)
  - **Gold**: Battle rewards, daily login, pack duplicates
  - **Gems**: Premium currency (IAP only for MVP)
  - **Stamina**: Battle cost (10/battle), regen 1 per 5 min, max 100 (can bank beyond via daily login)
  - **Resurrection Scrolls** (📜): Use instead of Gold to resurrect dead cards (0 HP → 1 HP)
    - Starting kit: 5 scrolls (tutorial teaches usage)
    - Daily login: Day 3, Day 5, Day 7 give scrolls (4 scrolls/week)
    - Daily Challenge: 1 scroll/completion (incentive for daily play)
    - Weekly missions: 5 scrolls/week (incentive for weekly grind)
    - World boss clear: 3 scrolls (Stage X-9 first-time clear)
  - **Potions** (Phase 1.5 - Design now, implement post-launch):
    - **Health Potion** (🧪): Restore 50 HP instant (whale convenience)
    - **Mana Potion** (🔮): Restore 50 mana instant (whale convenience, tactic spam enabler)
    - **Stamina Potion** (⚡): Restore 50 Stamina instant (already planned)
    - **Future**: XP Boosters, Gold Multipliers, Pack Tickets
- [ ] **HUD UI** (top bar: Gold, Gems, Stamina, Scrolls, Player Level, XP bar)
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
- ✅ **MVP Hero Rule**: Exactly 1 hero in the 6-slot formation (5 support cards)
- ✅ **Star Rank Progression**: Same card name can be different star ranks (Knight 1★ vs Knight 3★)
- ✅ **Tactic Attachment**: Attach tactics = star rank (3★ card = 3 tactic slots)
- ✅ **Collection View**: Grid of owned cards, sorted by star rank/rarity/element
- ✅ **Auto-Fill Options**: Highest Power, Most Stars, Balanced, Last Used
- ✅ **Visual Feedback**: Star count (★★★), border color (Bronze/Silver/Gold), tactic slot icons
- ✅ **Deck Validation**: Can use same card name at different star ranks (Knight 1★ + Knight 3★ = valid)

**Why Deck Size Matters** (20-50 card collection, 6 active):
- **Variety**: Choose 1 hero identity and rotate support packages around it
- **Counter Builds**: Anti-tank deck vs boss, anti-swarm vs hordes
- **Star Rank Options**: Use Knight 3★ OR Knight 1★ depending on tactic budget
- **Future (Phase 2)**: Reserve/Draw system - if unit dies in battle, draw replacement from deck
- **Future (Phase 2)**: Multi-hero armies - explicit mode expansion, not MVP baseline

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

**Tactic Effects** (AI Instruction + Gameplay Effect + Mana Cost):

**Combat AI Tactics** (Control targeting/movement):
- **"Boss Slayer"** (Uncommon, 2★, **0 mana**): AI targets highest-HP enemy (200+ HP priority) + +50% damage vs bosses
- **"Aggressive Assault"** (Common, 1★, **0 mana**): AI moves toward nearest enemy + +10% damage on first attack
- **"Defensive Stance"** (Common, 1★, **0 mana**): AI stays in back row (don't chase) + +20% block chance while stationary

**Healing AI Tactics** (Control who gets healed):
- **"Heal Hero"** (Uncommon, 2★, **0 mana**): AI targets hero with lowest HP% (not just lowest HP) + Restore 50 HP
- **"Heal Lowest HP"** (Common, 1★, **0 mana**): AI targets any ally with lowest HP + Restore 50 HP (default behavior)
- **"Heal All Allies"** (Rare, 3★, **20 mana**): AI activates when 3+ allies below 50% HP + Restore 30 HP to ALL allies (AOE)

**Spell Targeting Tactics** (Control ability usage):
- **"Fireball Barrage"** (Rare, 3★, **25 mana**): AI casts on boss/high-HP target + 200 fire damage + 50 AOE splash
- **"Lightning Strike"** (Rare, 3★, **20 mana**): AI casts on enemy with highest attack + 150 lightning damage + 10% stun

**Stat Buff Tactics** (Passive bonuses, no AI logic):
- **"Charge"** (Common, 1★, **5 mana**): Attack twice on first turn
- **"Guardian"** (Common, 1★, **5 mana**): +20% HP + Taunt (enemies attack this unit first)
- **"Volley"** (Uncommon, 2★, **15 mana**): Attack 3 enemies at once (50% damage each)
- **"Defensive Ward"** (Uncommon, 2★, **10 mana**): +50% damage reduction + heal 5 HP when blocking
- **Regeneration** (Rare, 3★, **15 mana**): Heal 10% max HP per turn (3 turns)
- **AOE Blessing** (Rare, 3★, **25 mana**): Heal all allies for 5 HP/turn (3 turns)
- **Lightning Bolt** (Epic, 4★, **30 mana**): Deal 100% extra damage + stun (1 turn)
- **Time Warp** (Epic, 4★, **50 mana**): Take 2 turns in a row (5-turn cooldown)
- **Phoenix Rebirth** (Epic, 4★, **40 mana**): Resurrect at 50% HP if killed (once per battle)
- **Annihilation** (Legendary, 5★, **50 mana**): Instant kill 1 enemy (once per battle)

**Mana Cost Philosophy**:
- ✅ **Basic Attack**: 0 mana (always available, prevents deadlock)
- ✅ **Low-cost tactics** (5-10 mana): Spam 2-4 times per battle (Knight with 20 mana)
- ✅ **Mid-cost tactics** (15-25 mana): Use 1-2 times per battle (strategic timing)
- ✅ **High-cost tactics** (30-50 mana): Once per battle (Epic heroes with 60-100 mana)
- ✅ **Whale limiter**: Even all-Legendary deck can't spam 5 Fireballs in 1 turn (not enough mana!)
- ✅ **F2P viable**: Commons with 10-20 mana can still use low-cost tactics (5-10 mana)

**Deliverables**:
- [ ] **CardFusionManager.cs** (combine duplicates, star rank up, stat recalculation)
- [ ] **FusionUI scene** (drag duplicates to fuse, show before/after stats, border glow animation)
- [ ] **DeckBuilderUI scene** (6-slot selection grid, tactic attachment UI, auto-fill button)
- [ ] **CardHPManaPersistence system** (save HP + Mana values between battles, show HP/Mana bars on deck screen)
- [ ] **HealingSystem.cs** (Gold cost heal for HP + Mana, AFK regen timers, checkpoint auto-heals)
- [ ] **Tactic mana costs** (validate tactic.ManaCost <= card.CurrentMana before activation)

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
  [Deck Builder shows HP status]:
  ✅ Water Mage (60/80, 75% HP) - READY (yellow HP bar)
  ⚠️ Knight #1 (10/30, 33% HP) - RISKY (red HP bar)
  ❌ Healer (0/20, DEAD) - CAN'T USE (red X icon, "Visit Temple")
  ✅ Archer (8/15, 53% HP) - READY (yellow HP bar)
  ✅ Scout (15/15, 100% HP) - READY (green HP bar)
  ✅ Knight #2 (25/30, 83% HP) - READY (green HP bar)
  
  [Available Reserves]:
  ✅ Archer #2 (15/15, 100% HP) - FRESH
  ✅ Scout #2 (15/15, 100% HP) - FRESH
  ✅ Knight #3 (30/30, 100% HP) - FRESH
  ... (11 more fresh cards)

  [Player Options]:
  Option A: Replace dead Healer with Archer #2 (free, deck rotation)
  Option B: Visit Temple screen → Heal Healer for 20 Gold (instant)
  Option C: Visit Temple screen → Heal All for 55 Gold (whale convenience)
  Option D: Wait AFK, Healer auto-heals 1 HP per 10 min (3.3 hours to full)
  
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
- [ ] **Temple UI** (main menu screen: list damaged cards, show HP + Mana, individual heal buttons, HEAL ALL button)
- [ ] **TempleManager.cs** (track card HP + Mana, AFK regen timers, Gold payment OR Scroll usage for resurrection)
- [ ] **AFK Regen System** (Health: 1 HP per 10 min, Mana: 1 per 2 min, ONLY for cards in active deck 6-50 cards)
  - **Active Deck** (6-50 cards): AFK regen ACTIVE (Health 1 per 10 min, Mana 1 per 2 min, offline progression)
  - **Codex Storage**: AFK regen PAUSED (⏸️ no healing until added back to active deck)
  - **Dead Cards (0 HP)**: AFK regen FROZEN (❌ no healing/mana regen, must pay 2× Gold OR 1 Scroll to resurrect)
- [ ] **Healing Options**: 
  - **Health**: [Heal Health: 20 Gold] (1 Gold per HP)
  - **Mana**: [Heal Mana: 30 Gold] (1 Gold per mana)
  - **Both**: [HEAL ALL: 50 Gold] (restores HP + Mana, whale convenience)
  - **Resurrection**: [Resurrect: 20 Gold (2× HP cost)] OR [Use 1 Scroll 📜] (restores to 1 HP + 50% mana)
- [ ] **BattleMap C# class** (8×8 grid, preset spawn coordinates for 6 player units + 6 enemy units)
- [ ] **BattleManager singleton** (turn system, tactic activation logic, win/loss detection)
- [ ] **Movement system** (click unit → highlight valid tiles → click to move, A* pathfinding)
- [ ] **Attack system** (click enemy in range, calculate damage with tactic modifiers, death animation)
- [ ] **Auto-Battle AI** (tactic-aware: prioritize targets, use cooldowns strategically)
- [ ] **Victory screen UI** (XP/Gold/Card rewards, HP damage summary, "Visit Temple" button)

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

### Week 5-6: Campaign Mode & Battle Progression

**Campaign Structure** (NEW: World → Territory → Realm → Battle hierarchy):
- ✅ **1 World**: "The Forgotten Lands"
- ✅ **4 Territories**: Greenwood Valley (starting) → Ashen Peaks → Frozen Wastes → Shadowlands (final)
- ✅ **9 Realms**: Distributed as 1 + 2 + 3 + 3 across territories
- ✅ **~60-80 Battles**: Variable number per realm (5-20 battles, increases with difficulty)
- ✅ Territory progression: Complete all battles in Territory 1 to unlock Territory 2
- ✅ Linear unlocking: Battle 1-1 → 1-2 → ... → 4-20 (must complete previous to unlock next)
- ✅ Boss battles: Mini-bosses (end of realm), Territory bosses (final realm), World boss (Battle 4-20)
- ✅ 3-star rating: Victory, Speed Clear (<10 turns), Perfect Victory (no deaths + hero >80% HP)

**Why This Alignment**:
- ✅ Introduces map terminology (World → Territory → Realm → Battle) without full exploration system
- ✅ Simplified UI: Static list-based (like Fire Emblem), no 2.5D map rendering needed
- ✅ Sets up Phase 3 expansion: Weekly rotating Territories, full World Map exploration
- ✅ Clean marketing: "Sovereign Territories: Conquer The Forgotten Lands" (World 1 name)

**Territory Distribution**:
```
TERRITORY 1: Greenwood Valley (Starting)
├─ Realm 1: Goblin Wastes (Battles 1-1 to 1-5, MINI-BOSS at 1-5)

TERRITORY 2: Ashen Peaks (Mid-game)
├─ Realm 2: Volcanic Badlands (Battles 2-1 to 2-5, MINI-BOSS at 2-5)
└─ Realm 3: Magma Caverns (Battles 2-6 to 2-10, TERRITORY BOSS at 2-10)

TERRITORY 3: Frozen Wastes (Late-game)
├─ Realm 4: Icewind Dale (Battles 3-1 to 3-5, MINI-BOSS at 3-5)
├─ Realm 5: Frostfang Mountains (Battles 3-6 to 3-10, MINI-BOSS at 3-10)
└─ Realm 6: Glacier Throne (Battles 3-11 to 3-15, TERRITORY BOSS at 3-15)

TERRITORY 4: Shadowlands (Final)
├─ Realm 7: Dark Forest (Battles 4-1 to 4-5, MINI-BOSS at 4-5)
├─ Realm 8: Necropolis (Battles 4-6 to 4-10, MINI-BOSS at 4-10)
└─ Realm 9: Demon's Gate (Battles 4-11 to 4-20, WORLD BOSS at 4-20)
```

**Battle Types**:
- ✅ Regular battles: 3-7 card enemy decks, increasing difficulty
- ✅ Mini-boss battles (end of realm): 7-10 card decks, Rare/Epic heroes, guaranteed Rare+ card
- ✅ Territory boss battles (final realm): 12-15 card decks, Epic/Legendary heroes, guaranteed Epic+ card
- ✅ World boss (Battle 4-20): Mythic "Demon Overlord", 20-card deck, guaranteed Legendary card

**Rewards Per Battle**:
- ✅ First clear: 100-500 Gold, 50-200 XP, 1-3 cards (rarity increases with territory)
- ✅ 3-star clear: +1 Epic card (choice from 3 options)
- ✅ Replays: 50% reduced rewards (encourages progression over farming)

**Daily Quest/Bounty Board** (NEW - Phase 1A):
- ✅ 5 quest slots with /con difficulty (EverQuest/WoW color system: Green/Blue/White/Yellow/Red)
- ✅ Randomized enemy decks (spawn pools, different each time)
- ✅ Individual refresh timers (4-6h after completion)
- ✅ Daily midnight reset (EST/UTC, ALL 5 quests refresh)
- ✅ Difficulty-based rewards:
  - Green: 100 Gold, 50 XP
  - Blue: 250 Gold, 100 XP, 1 Common card
  - White: 500 Gold, 200 XP, 1 Uncommon card
  - Yellow: 1,000 Gold, 500 XP, 1 Rare card
  - Red: 2,500 Gold, 1,000 XP, 1 Epic card, 3 Resurrection Scrolls
- ✅ Combat quests only (Defeat, Mini-Boss, Survival, Speed Clear, Perfect Victory)
- ❌ NO reroll option (Phase 2)
- ❌ NO named mobs (Phase 2)
- ❌ NO economy/collection quests (Phase 2)

**Stamina System**:
- ✅ Tutorial battles (Battles 1-1 to 1-4): 0 Stamina (unlosable)
- ✅ Post-tutorial battles: 10 Stamina per battle
- ✅ Daily Quest battles: 10 Stamina per quest (same as campaign)
- ✅ Daily refill: 240 Stamina/day (24 battles max = campaign OR quests OR mix)
- ✅ Starting Stamina: 100 (10 battles to start)
- ✅ **Stamina Banking**: Can exceed 100 max (daily login rewards stack, unclaimed refills bank)
- ✅ **Natural AFK moment**: F2P depletes 100 Stamina → Log out → 8h later: 100 Stamina + healed cards

**Deliverables**:
- [ ] CampaignManager C# class (World/Territory/Realm/Battle hierarchy, progression tracking, 3-star rating)
- [ ] World/Territory Map UI (static list-based, progress bars showing "Territory 2: 7/10 Battles ⏳")
- [ ] Realm Progress UI (battle list with star ratings, lock/unlock states)
- [ ] **QuestBoardManager C# class** (5 quest slots, /con difficulty, refresh timers, spawn pool generation)
- [ ] **Quest Board UI** ("Bounty Board" button on main menu, color-coded difficulty, timer display)
- [ ] **Spawn Pool System** (JSON defines enemy deck generation, weighted RNG, power scaling)
- [ ] 3-star rating system (turn count, deaths, hero health tracking)
- [ ] Enemy AI decks (~60-80 fixed campaign decks + spawn pool system for quests)
- [ ] Daily midnight reset (quest refresh, PlayerPrefs timer tracking)
- [ ] Replay rewards reduction (50% Gold/XP after first clear)
- ❌ Loot drop system (Phase 2 - defer for balancing)
- ❌ Named mob spawns (Phase 2)
- ❌ Campaign Nightmare Mode (Phase 2)

**What Moves to Phase 2**:
- ❌ Realm Map (40-tile hex grid) - Phase 2 Months 4-6
- ❌ Open-world exploration - Phase 2
- ❌ Fog of war, Movement Points - Phase 2
- ❌ Territory occupation - Phase 2
- ❌ AFK economy cards - Phase 2

---

### Week 7: Scroll-Based Crafting System ⭐ Phase 1.1 Stretch

**Purpose**: Fix RNG hell - players can target specific cards instead of relying only on pack luck (Hearthstone dust parity)

**Scroll-Based Crafting** (Simpler than Hearthstone Dust):
- ✅ **6 Scroll Types**: Common, Uncommon, Rare, Epic, Legendary, Mythic (match card rarities)
- ✅ **Duplicate Conversion**: 5 duplicates → 1 Scroll (same rarity)
  - Example: 5 Common Knights → 1 Common Scroll
  - Epic/Legendary: 3:1 and 2:1 ratios (rarer cards, lower conversion threshold)
- ✅ **Scroll Usage**: 1 Scroll → Craft any card (same rarity)
  - Example: 1 Common Scroll → Pick from 30 Common cards → Craft Healer
- ✅ **Simple UI**: "Craft Common Card" → Show 30 Commons → Pick one → Confirm

**Why Scrolls > Hearthstone Dust**:
- ✅ No crafting cost database (Scrolls are currency, not per-card recipes)
- ✅ Simple UI (pick from 30 Commons, not search 1,500+ cards)
- ✅ Future-proof (add new cards, scrolls still work without database updates)
- ✅ Monetization (sell scrolls in Market: Common $0.49, Legendary $9.99)

**Crafting Hall UI**:
```
╔═══════════════════════════════════════════════════════╗
║                  ⚒️ CRAFTING HALL                    ║
╠═══════════════════════════════════════════════════════╣
║ YOUR SCROLLS:                                         ║
║   📜 Common Scrolls: 12                               ║
║   📜 Uncommon Scrolls: 5                              ║
║   📜 Rare Scrolls: 2                                  ║
║                                                       ║
║ CRAFT A CARD:                                         ║
║ [Craft Common Card] (Costs: 1 Common Scroll)         ║
║ [Craft Uncommon Card] (Costs: 1 Uncommon Scroll)     ║
║ [Craft Rare Card] (Costs: 1 Rare Scroll) 🔒 Need 1   ║
║                                                       ║
║ CONVERT DUPLICATES:                                   ║
║ [Convert 5 Common Dupes → 1 Common Scroll]           ║
║   (You have 47 excess Commons)                        ║
║ [CONVERT ALL RARITIES] (Smart convert: 9 scrolls)    ║
╚═══════════════════════════════════════════════════════╝
```

**F2P vs Whale Balance**:
- **F2P Path**: Earn scrolls from duplicates (slow but free)
  - Opening 25 packs (125 cards) = ~50 Commons → 10 Common Scrolls → 10 targeted Commons
- **Whale Path**: Buy scrolls with Gold or IAP (instant targeted acquisition)
  - Common Scroll: 100 Gold OR $0.49
  - Legendary Scroll: 10,000 Gold OR $9.99

**Deliverables (Week 7, 5 days)**:
- [ ] **Day 1-2**: Crafting Hall UI (scroll inventory, craft buttons, convert buttons, card selection screen)
- [ ] **Day 3**: CraftingManager.cs singleton (scroll inventory, duplicate conversion, craft logic, Nakama storage)
- [ ] **Day 4**: Scroll Market tab (buy scrolls with Gold/IAP, bundle offers)
- [ ] **Day 5**: Testing & polish (conversion logic, crafting validation, IAP receipt handling)

---

### Week 8: Async Arena PvP System ⭐ Phase 1.1 Stretch

**Purpose**: Add daily engagement loop + skill-based rewards (Clash of Clans async PvP parity)

**Async Arena** (No Live PvP for MVP):
- ✅ **Unlock**: Level 5 (after tutorial, ~Week 1 of play)
- ✅ **Matchmaking**: Attack AI-controlled player decks (no live opponents, no websockets)
- ✅ **Bracketed Tiers**: Level 1-9, 10-14, 15-19, 20+ (prevents whale stomp)
- ✅ **Colosseum Tokens**: Skill-only currency (can't buy with money, prevents P2W)
- ✅ **Token Shop**: Exclusive cards (Gladiator, Arena Champion) + Arena Packs

**Why Async > Live PvP for MVP**:
- ✅ No websockets (Nakama HTTP API only, simpler deployment)
- ✅ No turn server (AI plays opponent's deck, no live coordination)
- ✅ Mobile-friendly (play on your schedule, no 10-min commitment)
- ✅ Fast iteration (fix AI balance without coordinating 2 players)

**Arena Structure**:
```
🥉 Bronze Arena (Level 1-9)
  - Rewards: 10-20 Tokens/win, 5 Tokens/loss
  - Season end: 100 Tokens (participation trophy)

🥈 Silver Arena (Level 10-14)
  - Rewards: 20-40 Tokens/win, 10 Tokens/loss
  - Season end: 300 Tokens + 1 Rare card

🥇 Gold Arena (Level 15-19)
  - Rewards: 40-80 Tokens/win, 20 Tokens/loss
  - Season end: 800 Tokens + 1 Epic card

💎 Diamond Arena (Level 20+)
  - Rewards: 80-150 Tokens/win, 40 Tokens/loss
  - Season end: 2,000 Tokens + 1 Legendary card
```

**Arena UI**:
```
╔═══════════════════════════════════════════════════════╗
║                   ⚔️ ARENA PVP                        ║
╠═══════════════════════════════════════════════════════╣
║ YOUR RANK:                                            ║
║   🥈 Silver Arena (Level 12)                          ║
║   Tokens: 450 / 800 (to Gold Arena reward)           ║
║                                                       ║
║ TODAY'S BATTLES:                                      ║
║   Battles played: 3 / 5 (2 free battles left)        ║
║                                                       ║
║ [FIND OPPONENT] (10 Stamina, matchmake vs Level 10-14)║
║ [VIEW COLOSSEUM MARKET] (spend Tokens on exclusive   ║
║  cards, can't buy with Gold/Gems)                     ║
╚═══════════════════════════════════════════════════════╝
```

**Colosseum Market** (Token-Only Shop):
- **Exclusive Cards**: Gladiator Hero (500 Tokens, Epic 5★), Arena Champion (2,000 Tokens, Legendary 5★)
- **Arena Pack**: 5 cards, 80% Arena-exclusive (300 Tokens)
- **Cosmetics**: Colosseum Banner title (100 Tokens)

**Daily Battle Limit**:
- 5 free battles/day (reset at midnight UTC)
- 6th+ battles: 100 Gems each (whale unlock, max 10/day)

**F2P vs Whale Balance**:
- **F2P**: 5 battles/day = 100-200 Tokens/day → Arena Champion in 10-20 days (grind reward)
- **Whales**: Can't buy tokens with money (pure skill currency), only extra battles (100 Gems each)

**Deliverables (Week 8, 5 days)**:
- [ ] **Day 1-2**: Arena Home UI (rank, season, battles left, find opponent, matchmaking, opponent preview)
- [ ] **Day 3**: ArenaManager.cs singleton (matchmaking SQL query, tier logic, token rewards, daily battle limit)
- [ ] **Day 4**: Colosseum Market UI (token shop, exclusive cards, Arena Pack)
- [ ] **Day 5**: Testing & polish (matchmaking speed, AI deck loading, token economy balance)

---

### Week 7-8: Stores & Progression (REBALANCED - Core Only)

**Player Leveling**:
- ✅ Level 1-20 progression (tutorial ends at Level 2, Arena unlocks at Level 5)
- ✅ XP requirements: Level 1 = 0, Level 2 = 100, Level 3 = 300, Level 5 = 1,000, Level 10 = 5,000, Level 20 = 50,000
- ✅ XP sources: Battle wins (50-200 XP), Arena wins (100 XP), quest completion

**Pack Market**:
- ✅ Standard Pack (5 cards): $0.99 OR 1,000 Gold
- ✅ Element Booster (5 cards): $1.99 OR 2,000 Gold
- ✅ Epic Booster (5 cards): $4.99 OR 5,000 Gold
- ✅ Mega Pack (20 cards, 1 Legendary): $19.99 (money only, whale bait)
- ✅ **Scroll Market Tab** (NEW): Buy scrolls with Gold/IAP (Common $0.49 → Legendary $9.99)

**Daily Login** (Streak Bonuses):
- ✅ 7-day reward cycle (streak required, missing 1 day = reset to Day 1):
  - Day 1: 500 Gold + 50 Stamina
  - Day 2: 1× Common card + 50 Stamina
  - Day 3: 500 Gold + 50 Stamina + **1 Resurrection Scroll 📜**
  - Day 4: 1× Uncommon card + 100 Stamina
  - Day 5: 1,000 Gold + 100 Stamina + **1 Resurrection Scroll 📜**
  - Day 6: 1× Rare card + 100 Stamina
  - Day 7: 1× Standard Pack (5 cards) + 200 Stamina (JACKPOT!) + **2 Resurrection Scrolls 📜**
- ✅ **Weekly total**: 3,000 Gold + 650 Stamina + **4 Resurrection Scrolls** (enough for 2 Epic deaths)

**Gold Earning** (Updated with Crafting/PvP):
- ✅ Battle rewards: 50-200 Gold per battle
- ✅ Arena wins: 50 Gold + Colosseum Tokens
- ✅ Daily login: 500 Gold (7-day cycle)
- ✅ Duplicate conversion: No Gold (convert to Scrolls instead)
- ✅ Total daily: ~800 Gold/day (500 login + 300 battles/Arena)

**Deliverables (Week 7-8 Core)**:
- [ ] PlayerLevel C# class (XP tracking, level-up rewards, Arena unlock at Level 5)
- [ ] PackStore UI (buy packs with Gold OR money, Scroll Market tab, IAP integration)
- [ ] DailyLogin system (7-day cycle, reward claims, streak tracking)
- [ ] Gold/Gem/Token display UI (HUD top bar: Gold, Gems, Stamina, Tokens, Scrolls, Player Level)

**What's Deferred to Phase 1.1 (Month 2)**:
- ❌ **Battle Pass** (30-day season, Free/Paid tracks) → Phase 1.1
- ❌ **Advanced Analytics** (heatmaps, funnel analysis, cohort retention) → Phase 1.1
- ❌ **Stamina Refills IAP** (Small/Large/Unlimited) → Phase 1.1 (Stamina system stays, IAP refills defer)
- ❌ **First-Time Offers** (Starter Pack, Whale Welcome Pack) → Phase 1.1

**Why This Works**:
- ✅ **Crafting + PvP** fix critical competitive gaps (Hearthstone dust parity + engagement loop)
- ✅ **Battle Pass deferred** = Non-critical (nice-to-have, not MVP blocker)
- ✅ **Analytics deferred** = Post-launch optimization (collect data in Phase 1.1)
- ✅ **Timeline intact** = 8 weeks maintained (Week 7 = Crafting, Week 8 = Arena PvP + Stores)

---

## Total MVP Scope

### What's Included (8-Week Deliverables)

**Core Systems**:
- ✅ Tutorial (28 steps, 0-60 minutes)
- ✅ Card system (~100 cards, HP/Mana/Attack/Defense baseline)
- ✅ Deck building (6 Trainer Decks, drag-drop builder)
- ✅ Combat (8×8 battle map, manual + auto-battle)
- ✅ Campaign Mode (72 stages, 8 worlds, 3-star rating)
- ✅ Daily Challenge (bonus rewards, login incentive)
- ✅ Pack Market (Standard/Element/Epic Packs, Gold only)
- ✅ Stamina system (10 per battle, 240 refill/day)
- ✅ Daily login (7-day reward cycle)
- ✅ Player leveling (Level 1-5 progression)

**Phase 1.1 Stretch Add-ons**:
- ⚠️ Scroll crafting system
- ⚠️ Async Arena PvP
- ⚠️ IAP/advanced monetization modules (Battle Pass, refill offers)

**Total Content**:
- ✅ 100 cards (6 Epics, 30 Units, 20 Buildings, 20 Tactics, 14 Equipment, 10 Workers)
- ✅ 6 Trainer Decks (20 cards each)
- ✅ 5 packs in tutorial (20 Trainer + 5 Element #1 + 6 Step 23 + 5 Element #2 = 36 cards)
- ✅ 5-10 PvE battles (Realm Map enemies)
- ✅ 1 Realm Map (40 Locations, single-player only)

---

### What's Deferred (Post-MVP)

**Phase 1.1 (Month 2)**:
- ❌ Battle Pass (30-day season, Free/Paid tracks, exclusive rewards)
- ❌ Advanced Analytics (heatmaps, funnel analysis, cohort retention)
- ❌ Stamina Refills IAP (Small $0.99, Large $3.99, Unlimited $9.99)
- ❌ First-Time Offers (Starter Pack, Whale Welcome Pack)
- ❌ Device optimization (iOS/Android framerate, build size)

**Phase 2 (Month 3-5)**:
- ❌ Food/Lumber/Ore economy (production buildings, auto-collection)
- ❌ RPG card stats expansion (Health/Mana/Stamina per-card variation)
- ❌ Consumables (Potions/Scrolls from battle chests)
- ❌ RPG shops (Alchemist, Scribe, Jeweler)
- ❌ Premium Packs (Gem currency, 10% shiny rate)
- ❌ Daily/Weekly quests (economy/collection quests, named mobs)
- ❌ **Live PvP** (websockets, turn timer, ranked ladder, ELO matchmaking)

**Phase 3 (Month 6-9)**:
- ❌ Territory Map (Realm occupation, 1-month campaigns)
- ❌ World Map (Territory wars, 3-month seasons)
- ❌ Occupation mechanics (Location → Realm → Territory)
- ❌ Alliances (chat, donations, co-op events, guild wars)
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
19. Stamina system (10 per battle, 240 refill/day)
20. Tutorial flow (Steps 16-27, Realm Map exploration)

### Week 7 (Stores & Progression)
21. Pack Market UI (buy packs, opening animation)
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
- ✅ Pack Market works (buy with Gold, opening animation)
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
2. PvP Colosseum (1v1 ranked matches, Colosseum Tokens)
3. Alliances (chat, donations, PvE events)
4. Elemental interactions (Fire > Earth > Water)
5. Status effects (Burn, Freeze, Poison)

---

**For combat details, see**: [combat-calculation-spec.md](combat-calculation-spec.md)  
**For economy details, see**: [economy-system.md](economy-system.md)  
**For RPG systems, see**: [rpg-systems-spec.md](rpg-systems-spec.md)  
**For map progression, see**: [map-tier-progression.md](map-tier-progression.md)  
**For tutorial flow, see**: [tutorial-flow.md](tutorial-flow.md)
