# Starter Deck Design - Choose Your Element

**Last Updated**: January 10, 2026  
**Status**: CRITICAL - Defines tutorial flow, first-time user experience  
**Related**: [tutorial-flow.md](../mvp/tutorial-flow.md), [card-schema.json](../specs/card-schema.json)

---

## Overview

**Philosophy**: The starter experience must be **fun, exciting, and give immediate gratification**. Players choose their element, get a starter deck, and immediately open a bonus pack (with guaranteed hero + shiny chance) to hook them on the collection loop.

**Goals**:
1. **Meaningful Choice**: 3 element options (Fire, Water, Earth) with distinct playstyles
2. **Immediate Gratification**: Bonus pack opens immediately after choosing starter
3. **Hero Guarantee**: Every pack contains 1 hero (Common → Legendary)
4. **Shiny Hook**: 10% chance for shiny variant (visual upgrade, same stats)
5. **Retention Loop**: Daily/weekly packs keep players coming back

---

## Starter Deck Selection Flow

### **Tutorial Step 1: Choose Your Element**

**UI Screen**: 3 glowing portals, each representing an element.

**Presentation**:
```
"Welcome, Sovereign! Choose your path to power..."

[Fire Portal]          [Water Portal]         [Earth Portal]
🔥 Crimson flames      💧 Azure tides         🌍 Emerald earth
AGGRESSIVE             DEFENSIVE              BALANCED
High Attack            High Defense           Versatile
Fast victories         Outlast enemies        Adapt to any foe

Hero: ARIA             Hero: THALOR           Hero: GAIA
Flame Knight           Tide Guardian          Stone Sentinel
```

**Player Action**: Tap/click 1 portal to receive starter deck.

---

## Starter Deck Compositions (15 Cards Each)

### **🔥 FIRE STARTER DECK** (Aggressive Playstyle)

**Philosophy**: High attack, low defense. Win fast or lose fast. Teaches aggro tactics.

**Contents** (15 cards total):

#### **1× Epic Hero: Aria, Flame Knight**
- **Type**: Hero
- **Element**: Fire
- **Rarity**: Epic (3★)
- **Stats**:
  - Health: 80 HP
  - Mana: 60 MP
  - Attack: 45 (highest starter hero Attack)
  - Defense: 12 (lowest starter hero Defense)
- **Ability**: **"Blazing Strike"** (30 mana, 3-turn cooldown)
  - Deal 70 fire damage to target enemy
  - If target dies, deal 20 splash damage to adjacent enemies
- **Passive**: **"Inferno Aura"**
  - All allied Fire units gain +15% Attack while Aria is alive
- **Tactic Slots**: 3
- **Lore**: "Once a royal guard, Aria abandoned her post to seek glory on the battlefield. Her blade burns with eternal flame."

#### **3× Rare Fire Units**

1. **Ember Legionnaire** (Rare 2★)
   - **Stats**: 55 HP, 20 MP, 32 ATK, 10 DEF
   - **Ability**: **"Charge"** (10 mana) — Move +2 tiles and attack same turn
   - **Tactic Slots**: 2

2. **Phoenix Hatchling** (Rare 2★)
   - **Stats**: 40 HP, 40 MP, 25 ATK, 8 DEF
   - **Ability**: **"Rebirth"** (30 mana, 1× per battle) — If killed, resurrect at 50% HP next turn
   - **Tactic Slots**: 2

3. **Flame Imp** (Rare 2★)
   - **Stats**: 45 HP, 35 MP, 28 ATK, 9 DEF
   - **Ability**: **"Fireball"** (20 mana) — Deal 35 fire damage to 1 enemy
   - **Tactic Slots**: 2

#### **6× Uncommon Fire Units**

4-5. **Goblin Raider** (Uncommon 1★) × 2
   - **Stats**: 30 HP, 15 MP, 22 ATK, 6 DEF
   - **Ability**: **"Reckless Strike"** (5 mana) — +50% damage, -30% defense for 1 turn
   - **Tactic Slots**: 1

6-7. **Fire Soldier** (Uncommon 1★) × 2
   - **Stats**: 35 HP, 10 MP, 20 ATK, 8 DEF
   - **Ability**: None (basic attack only)
   - **Tactic Slots**: 1

8-9. **Flame Archer** (Uncommon 1★) × 2
   - **Stats**: 25 HP, 12 MP, 18 ATK, 5 DEF
   - **Ability**: **Ranged Attack** — Can attack from 3 tiles away
   - **Tactic Slots**: 1

#### **5× Common Fire Support**

10-11. **Fire Scout** (Common 0★) × 2
   - **Stats**: 20 HP, 8 MP, 15 ATK, 4 DEF
   - **Ability**: **"Sprint"** (5 mana) — Move +1 tile this turn
   - **Tactic Slots**: 1

12-13. **Scorch Elemental** (Common 0★) × 2
   - **Stats**: 18 HP, 15 MP, 16 ATK, 3 DEF
   - **Ability**: None (basic attack only)
   - **Tactic Slots**: 1

14. **Fire Shaman** (Common 0★)
   - **Stats**: 15 HP, 25 MP, 10 ATK, 5 DEF
   - **Ability**: **"Minor Fireball"** (12 mana) — Deal 20 fire damage to 1 enemy
   - **Tactic Slots**: 1

**Total Rarity Points**: 8 (Epic) + 12 (3× Rare) + 6 (6× Uncommon) + 5 (5× Common) = **31 points**

---

### **💧 WATER STARTER DECK** (Defensive Playstyle)

**Philosophy**: High defense, healing. Outlast enemies, win through attrition. Teaches control tactics.

**Contents** (15 cards total):

#### **1× Epic Hero: Thalor, Tide Guardian**
- **Type**: Hero
- **Element**: Water
- **Rarity**: Epic (3★)
- **Stats**:
  - Health: 100 HP (highest starter hero HP)
  - Mana: 55 MP
  - Attack: 30 (lowest starter hero Attack)
  - Defense: 28 (highest starter hero Defense)
- **Ability**: **"Tidal Wave"** (28 mana, 3-turn cooldown)
  - Deal 50 water damage to 3 enemies in a line
  - Heal 20 HP to self
- **Passive**: **"Ocean's Embrace"**
  - All allied Water units gain +20% Defense while Thalor is alive
- **Tactic Slots**: 3
- **Lore**: "Guardian of the Azure Isles, Thalor commands the ocean's fury. His shield has never been broken."

#### **3× Rare Water Units**

1. **Frost Paladin** (Rare 2★)
   - **Stats**: 65 HP, 25 MP, 24 ATK, 18 DEF
   - **Ability**: **"Shield Ally"** (12 mana) — Grant +15 DEF to 1 ally for 2 turns
   - **Tactic Slots**: 2

2. **Water Elemental** (Rare 2★)
   - **Stats**: 50 HP, 40 MP, 22 ATK, 14 DEF
   - **Ability**: **"Healing Tide"** (22 mana) — Restore 35 HP to 1 ally
   - **Tactic Slots**: 2

3. **Elven Archer** (Rare 2★)
   - **Stats**: 42 HP, 30 MP, 28 ATK, 10 DEF
   - **Ability**: **"Piercing Arrow"** (18 mana) — Ignore 50% of target's defense
   - **Tactic Slots**: 2

#### **6× Uncommon Water Units**

4-5. **Sea Serpent** (Uncommon 1★) × 2
   - **Stats**: 48 HP, 20 MP, 20 ATK, 12 DEF
   - **Ability**: **"Aquatic Movement"** — Move through water tiles (mountains block)
   - **Tactic Slots**: 1

6-7. **Frost Soldier** (Uncommon 1★) × 2
   - **Stats**: 40 HP, 10 MP, 18 ATK, 10 DEF
   - **Ability**: None (basic attack only)
   - **Tactic Slots**: 1

8-9. **Water Scout** (Uncommon 1★) × 2
   - **Stats**: 32 HP, 15 MP, 16 ATK, 8 DEF
   - **Ability**: **"Quick Step"** (6 mana) — Move +1 tile this turn
   - **Tactic Slots**: 1

#### **5× Common Water Support**

10-11. **Aqua Healer** (Common 0★) × 2
   - **Stats**: 22 HP, 30 MP, 8 ATK, 6 DEF
   - **Ability**: **"Minor Heal"** (15 mana) — Restore 20 HP to 1 ally
   - **Tactic Slots**: 1

12-13. **Ice Sprite** (Common 0★) × 2
   - **Stats**: 18 HP, 20 MP, 12 ATK, 5 DEF
   - **Ability**: **"Frostbolt"** (10 mana) — Deal 18 water damage to 1 enemy
   - **Tactic Slots**: 1

14. **Tidal Mage** (Common 0★)
   - **Stats**: 20 HP, 25 MP, 10 ATK, 7 DEF
   - **Ability**: **"Water Shield"** (12 mana) — Grant +8 DEF to self for 2 turns
   - **Tactic Slots**: 1

**Total Rarity Points**: 8 (Epic) + 12 (3× Rare) + 6 (6× Uncommon) + 5 (5× Common) = **31 points**

---

### **🌍 EARTH STARTER DECK** (Balanced Playstyle)

**Philosophy**: Moderate attack/defense, versatile abilities. Adapts to any situation. Teaches flexible tactics.

**Contents** (15 cards total):

#### **1× Epic Hero: Gaia, Stone Sentinel**
- **Type**: Hero
- **Element**: Earth
- **Rarity**: Epic (3★)
- **Stats**:
  - Health: 90 HP
  - Mana: 58 MP
  - Attack: 36 (balanced)
  - Defense: 20 (balanced)
- **Ability**: **"Earthquake"** (32 mana, 3-turn cooldown)
  - Deal 55 earth damage to all enemies on ground tiles
  - Cannot damage flying units (Phase 2+ mechanic)
- **Passive**: **"Stone Skin"**
  - All allied Earth units take -10% damage from all sources
- **Tactic Slots**: 3
- **Lore**: "Born from the mountain's heart, Gaia is immovable. The earth itself bends to her will."

#### **3× Rare Earth Units**

1. **Rock Golem** (Rare 2★)
   - **Stats**: 70 HP, 15 MP, 26 ATK, 16 DEF
   - **Ability**: **"Fortify"** (10 mana) — Gain +10 DEF, cannot move for 1 turn
   - **Tactic Slots**: 2

2. **Forest Druid** (Rare 2★)
   - **Stats**: 48 HP, 38 MP, 24 ATK, 12 DEF
   - **Ability**: **"Nature's Blessing"** (20 mana) — Restore 25 HP + 10 MP to 1 ally
   - **Tactic Slots**: 2

3. **Stone Guardian** (Rare 2★)
   - **Stats**: 58 HP, 25 MP, 28 ATK, 14 DEF
   - **Ability**: **"Taunt"** (8 mana) — Force enemies to attack this unit for 2 turns
   - **Tactic Slots**: 2

#### **6× Uncommon Earth Units**

4-5. **Earth Warrior** (Uncommon 1★) × 2
   - **Stats**: 42 HP, 12 MP, 22 ATK, 10 DEF
   - **Ability**: **"Power Strike"** (8 mana) — Deal +50% damage on next attack
   - **Tactic Slots**: 1

6-7. **Vine Archer** (Uncommon 1★) × 2
   - **Stats**: 35 HP, 15 MP, 20 ATK, 7 DEF
   - **Ability**: **Ranged Attack** — Can attack from 3 tiles away
   - **Tactic Slots**: 1

8-9. **Boulder Beast** (Uncommon 1★) × 2
   - **Stats**: 50 HP, 10 MP, 18 ATK, 12 DEF
   - **Ability**: None (tanky basic attacker)
   - **Tactic Slots**: 1

#### **5× Common Earth Support**

10-11. **Earth Scout** (Common 0★) × 2
   - **Stats**: 28 HP, 10 MP, 16 ATK, 6 DEF
   - **Ability**: **"Pathfinder"** (6 mana) — Reveal fog of war 2 tiles around this unit
   - **Tactic Slots**: 1

12-13. **Stone Elemental** (Common 0★) × 2
   - **Stats**: 25 HP, 12 MP, 15 ATK, 8 DEF
   - **Ability**: None (basic attack only)
   - **Tactic Slots**: 1

14. **Nature Mage** (Common 0★)
   - **Stats**: 20 HP, 28 MP, 12 ATK, 6 DEF
   - **Ability**: **"Earthen Spike"** (14 mana) — Deal 22 earth damage to 1 enemy
   - **Tactic Slots**: 1

**Total Rarity Points**: 8 (Epic) + 12 (3× Rare) + 6 (6× Uncommon) + 5 (5× Common) = **31 points**

---

## Bonus Pack (Opened Immediately After Choosing Starter)

### **"Welcome Pack"** (5 cards)

**Purpose**: Give immediate dopamine hit, introduce pack-opening mechanics, guarantee 1 hero.

**Drop Rates**:
1. **1× Hero (Guaranteed)** — Rarity distribution:
   - 50% Common hero (0★)
   - 30% Uncommon hero (1★)
   - 15% Rare hero (2★)
   - 4% Epic hero (3★)
   - 1% Legendary hero (5★)

2. **4× Support Cards** — Standard distribution:
   - 60% Common (2-3 cards)
   - 25% Uncommon (1 card)
   - 12% Rare (0-1 cards)
   - 3% Epic (0 cards, 3% chance)

**Shiny Chance**: 10% per card (independent rolls)
- **Shiny Effect**: Golden border, particle effects, animated portrait
- **Stats**: Identical to normal version (cosmetic only)
- **Trade Value**: Phase 2+ (shinies worth 5× normal for trading)

**Example Welcome Pack** (Fire player):
- 1× **Ignis, Flame Striker** (Uncommon 1★ hero) — 60 HP, 40 MP, 28 ATK, 10 DEF
- 1× **Scorch Elemental** (Common 0★, SHINY ✨) — Same stats, golden border
- 1× **Fire Soldier** (Uncommon 1★)
- 1× **Goblin Raider** (Common 0★)
- 1× **Flame Tactic: Fireball** (Common 0★ tactic) — 20 mana, deal 25 fire damage

**Result**: Player now has **20 cards total** (15 starter + 5 Welcome Pack).

---

## Tutorial Flow with New Starter System

### **Updated Tutorial Steps 1-5**

**Step 1: Choose Your Element** (NEW)
- UI: 3 portals (Fire, Water, Earth)
- Player taps 1 portal
- Reward: 15-card starter deck for chosen element

**Step 2: Open Your Welcome Pack** (NEW)
- UI: Glowing pack appears (element-themed)
- Player taps to open (animation: cards fly out one-by-one)
- Reveal sequence:
  1. Card 1 (support) — flip animation
  2. Card 2 (support) — flip animation
  3. Card 3 (support) — flip animation
  4. Card 4 (support) — flip animation
  5. **Card 5 (hero)** — **EPIC reveal animation** (2 seconds, hero portrait zooms in, voiceline plays)
- Reward: 5 cards (1 hero guaranteed)

**Step 3: Meet Your Hero**
- Cutscene: Chosen starter hero (Aria/Thalor/Gaia) introduces themselves
- Voiceline: "I am [Name], and together we shall conquer this realm!"
- Tutorial: "Heroes lead your armies. They have powerful abilities and can equip tactics."

**Step 4: First Battle (Auto-Battle Tutorial)**
- Enemy: 3× Goblin Raider (guaranteed easy win)
- Player deck: Auto-selected 6 cards from starter + Welcome Pack
- Battle plays automatically (no player input)
- Tutorial: "Watch how your hero fights! Aria's Blazing Strike deals massive damage."

**Step 5: Deck Builder Tutorial**
- UI: Show full 20-card collection
- Tutorial: "Build your deck! You can use up to 20 cards at Level 1."
- Guided choice: "Add 5 more cards to your deck (choose any cards)"
- Reward: Unlocked deck builder

---

## Daily/Weekly Pack Rewards (Retention Hooks)

### **Daily Login Rewards**

**Every 24 Hours**:
- **Day 1**: 500 Gold
- **Day 2**: 1× Standard Pack (5 cards, no hero guarantee)
- **Day 3**: 750 Gold
- **Day 4**: 1× Element Booster Pack (5 cards, same element as starter, no hero guarantee)
- **Day 5**: 1,000 Gold
- **Day 6**: 1× Standard Pack
- **Day 7**: 1× **Epic Pack** (5 cards, 1× Epic hero guaranteed, 20% shiny chance)

**Resets weekly**. Players who login 7 days straight get Epic Pack (retention driver).

---

### **Weekly Quest Rewards**

**Complete 3/5 Quests → 1× Rare Pack**

**Quest Examples**:
1. "Win 10 battles" → 1,000 Gold
2. "Defeat 5 Epic enemies" → 500 Gold + 50 XP
3. "Use 3 different elements in battle" → 1× Element Booster Pack
4. "Open 5 packs" → 1,000 Gold
5. "Complete 5 campaign battles without losing a card" → 1× Rare Pack

**Complete 5/5 Quests → 1× Epic Pack** (big retention driver)

---

### **Campaign Milestone Rewards**

**Location 10 (Mini-Boss)**:
- 1× **Hero Pack** (5 cards, 1× Rare hero guaranteed)

**Location 20 (Mid-Boss)**:
- 1× **Epic Pack** (5 cards, 1× Epic hero guaranteed)

**Location 30**:
- 1× **Legendary Pack** (5 cards, 1× Legendary hero guaranteed, 30% shiny chance)

**Location 40 (Final Boss)**:
- 1× **Mythic Pack** (5 cards, 1× Mythic hero guaranteed — choose from 3 options)
- **Mythic Heroes** (6★):
  - **Ragnarok, God of Thunder** (Lightning)
  - **Merlin, Archmage Eternal** (Arcane)
  - **Terra, World Shaper** (Earth)

---

## Pack Types Summary (MVP)

| Pack Type | Cost | Cards | Hero Guarantee | Shiny Chance | Availability |
|-----------|------|-------|----------------|--------------|--------------|
| **Welcome Pack** | FREE (1× ever) | 5 | 1× (Common-Legendary) | 10% | Tutorial Step 2 |
| **Standard Pack** | 1,000 Gold | 5 | No | 5% | Store, Daily Login |
| **Element Booster** | 1,500 Gold | 5 | No (but 80% match element) | 5% | Store, Quests |
| **Rare Pack** | 3,000 Gold | 5 | 1× Rare hero | 8% | Weekly Quest |
| **Epic Pack** | 5,000 Gold | 5 | 1× Epic hero | 15% | Day 7 Login, Campaign |
| **Hero Pack** | 4,000 Gold | 5 | 1× Rare hero | 10% | Location 10 reward |
| **Legendary Pack** | 10,000 Gold | 5 | 1× Legendary hero | 25% | Location 30 reward |
| **Mythic Pack** | 20,000 Gold | 5 | 1× Mythic (choose 3) | 40% | Location 40 reward |

---

## Card Series Breakdown (100 Cards for MVP)

**To ensure game isn't boring from the start, we need a full card pool.** Here's the breakdown:

### **By Rarity** (100 cards total):

| Rarity | Count | Purpose | Example |
|--------|-------|---------|---------|
| Common (0★) | 40 | Filler, easy to collect | Fire Scout, Aqua Healer |
| Uncommon (1★) | 30 | Build variety, minor abilities | Goblin Raider, Sea Serpent |
| Rare (2★) | 18 | Specialized units, stronger | Ember Legionnaire, Rock Golem |
| Epic (3★) | 9 | Powerful heroes, deck anchors | Aria, Thalor, Gaia |
| Legendary (5★) | 3 | Iconic heroes, campaign rewards | Ragnarok, Merlin, Terra |

**Total**: 100 cards

---

### **By Type** (100 cards total):

| Type | Count | Purpose |
|------|-------|---------|
| **Heroes** | 25 | 9 Epic (starters + elements), 3 Legendary, 13 Common/Uncommon heroes |
| **Units** | 50 | Combat troops (soldiers, archers, beasts) |
| **Tactics** | 15 | Spells/scrolls (Fireball, Heal, Shield) |
| **Buildings** | 10 | Economy cards (Phase 2, MVP = 10 for variety) |

**Total**: 100 cards

---

### **By Element** (100 cards total):

| Element | Count | Heroes | Units | Tactics |
|---------|-------|--------|-------|---------|
| **Fire** | 18 | 3 (Aria + 2 others) | 12 | 3 |
| **Water** | 18 | 3 (Thalor + 2 others) | 12 | 3 |
| **Earth** | 18 | 3 (Gaia + 2 others) | 12 | 3 |
| **Lightning** | 12 | 2 (Ragnarok + 1 Epic) | 8 | 2 |
| **Wind** | 12 | 2 (1 Epic, 1 Rare) | 8 | 2 |
| **Frost** | 12 | 2 (1 Epic, 1 Rare) | 8 | 2 |
| **Neutral** | 10 | 0 | 6 (multi-element support) | 4 (generic tactics) |

**Total**: 100 cards

---

## Design Philosophy Recap

**Why This Starter System Works**:

1. **Meaningful Choice**: 3 elements (Fire, Water, Earth) with distinct playstyles (aggro, control, balanced)
2. **Immediate Hook**: Welcome Pack opens immediately (dopamine hit, hero guaranteed)
3. **Shiny Chase**: 10% shiny chance creates "whale moment" (even F2P can get lucky)
4. **Retention Loops**:
   - Daily Login → Day 7 Epic Pack (players return weekly)
   - Weekly Quests → Complete 5/5 for Epic Pack (engagement driver)
   - Campaign Milestones → Legendary/Mythic packs at Locations 30/40 (progression carrot)
5. **Full Card Series**: 100 cards ensures variety, discovery, meta evolution

**F2P Friendly**:
- Starter deck (15 cards) + Welcome Pack (5 cards) = **20 cards for FREE**
- Daily Login Week 1 = 3,000 Gold + 2 Standard Packs = ~3,000 Gold worth of value
- Campaign rewards = 41 cards (guaranteed drops) + ~5,000 Gold (5 packs) = **60+ cards in Week 1**

**Monetization (Phase 1.1)**:
- Premium Track: $9.99/month = 5× Epic Packs, 10,000 Gold, 30% shiny chance
- Mega Packs: $4.99 = 1× Legendary Pack (guaranteed Legendary hero)
- Battle Pass: $19.99 = 50-tier rewards (heroes, shinies, Gold)

---

**Next Steps**:
1. Create `starter-cards.json` with all 45 starter cards (15 per element)
2. Define remaining 55 cards for 100-card MVP pool
3. Implement pack-opening animation flow
4. Balance daily/weekly reward math (ensure F2P gets ~2 packs/week)
