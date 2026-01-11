# Campaign Structure - 40 Locations (Single Realm Map)

**Last Updated**: January 10, 2026  
**Status**: CRITICAL - Defines PvE progression, enemy scaling, reward economy  
**Related**: [starter-deck-design.md](starter-deck-design.md), [economy-system.md](economy-system.md), [combat-calculation-spec.md](combat-calculation-spec.md)

---

## Overview

**MVP Campaign**: 1 Realm Map with **40 Locations** (linear progression, no branching paths).

**Goals**:
1. **Teach Core Mechanics**: Locations 1-10 = tutorial extension (move, attack, abilities)
2. **Difficulty Scaling**: Locations 11-40 = progressive challenge (3 cards → 15 cards)
3. **Reward Loop**: Gold + Cards + XP drive deck-building and progression
4. **Boss Milestones**: Locations 10, 20, 30, 40 = special battles with unique rewards
5. **Completion Time**: 6-10 hours for average player (2-3 weeks casual play)

**Total Rewards**:
- **Gold**: 4,575 Gold (~4-5 Standard Packs)
- **Cards**: 41 card drops (10 Common, 10 Uncommon, 10 Rare, 10 Epic, 1 Legendary)
- **XP**: ~12,000 XP (Level 1 → Level 18-20)
- **Special Packs**: 3× Hero Packs (Locations 10, 20, 30), 1× Mythic Pack (Location 40)

---

## 40-Location Breakdown

### **Location Types** (40 total)

| Type | Count | Purpose | Rewards | Enemy Strength |
|------|-------|---------|---------|----------------|
| **Tutorial Town** | 8 | Safe zones, free heal | 50-100 Gold, 1× Common card | 3-5 cards (all Commons) |
| **Dungeon** | 15 | Standard battles | 100-200 Gold, 1× card (rarity scales) | 5-12 cards (mixed rarities) |
| **Mine** | 5 | Resource nodes | 2× Gold (no card) | 4-8 cards (focus Gold reward) |
| **Ruins** | 5 | Treasure chests | 1× Rare+ card guaranteed | 6-10 cards (higher difficulty) |
| **Monster Lair** | 3 | Respawning enemies | 150-300 Gold, 1× Epic card | 8-12 cards (Epic boss included) |
| **Boss Arena** | 4 | Major milestones | Special packs (Hero/Mythic) | 10-15 cards (multi-phase fights) |

**Total**: 40 Locations

---

## Enemy Deck Scaling Formulas

### **Enemy Card Count**
```
Enemy Deck Size = 3 + (Location × 0.3)
```

**Examples**:
- Location 1: 3 + (1 × 0.3) = **3 cards**
- Location 10: 3 + (10 × 0.3) = **6 cards**
- Location 20: 3 + (20 × 0.3) = **9 cards**
- Location 30: 3 + (30 × 0.3) = **12 cards**
- Location 40: 3 + (40 × 0.3) = **15 cards** (Boss)

---

### **Enemy Rarity Distribution**

| Locations | Common % | Uncommon % | Rare % | Epic % | Legendary % |
|-----------|----------|------------|--------|--------|-------------|
| 1-10 | 100% | 0% | 0% | 0% | 0% |
| 11-20 | 75% | 25% | 0% | 0% | 0% |
| 21-30 | 50% | 30% | 20% | 0% | 0% |
| 31-39 | 30% | 30% | 25% | 15% | 0% |
| 40 (Boss) | 20% | 20% | 20% | 30% | 10% |

**Example Enemy Decks**:

**Location 5** (6 cards):
- 6× Common enemies (Goblin Raider, Orc Scout, Wolf Pack)

**Location 15** (7 cards):
- 5× Common, 2× Uncommon (adds challenge, teaches counter-play)

**Location 25** (10 cards):
- 5× Common, 3× Uncommon, 2× Rare (requires deck optimization)

**Location 40 - Final Boss** (15 cards):
- 3× Common, 3× Uncommon, 3× Rare, 4× Epic, 2× Legendary (epic showdown)

---

## Reward Scaling Formulas

### **Gold Rewards**
```
Gold = 50 + (Location × 5)
```

**Examples**:
- Location 1: 50 + (1 × 5) = **55 Gold**
- Location 10: 50 + (10 × 5) = **100 Gold**
- Location 20: 50 + (20 × 5) = **150 Gold**
- Location 30: 50 + (30 × 5) = **200 Gold**
- Location 40: 50 + (40 × 5) = **250 Gold**

**Total Campaign Gold**: 
```
Sum(55 to 250 in increments of 5) = 4,575 Gold
```

**Pack Equivalent**: 4,575 Gold = 4× Standard Packs (4,000 Gold) + 575 Gold leftover

---

### **Card Drop Rewards**

**Drop Rate by Location**:
- Locations 1-10: 1× Common card per win
- Locations 11-20: 1× Uncommon card per win
- Locations 21-30: 1× Rare card per win
- Locations 31-40: 1× Epic card per win (Location 40 = Legendary)

**Total Cards from Campaign** (41 drops):
- 10× Common (Locations 1-10)
- 10× Uncommon (Locations 11-20)
- 10× Rare (Locations 21-30)
- 10× Epic (Locations 31-39)
- 1× Legendary (Location 40 boss reward)

**Combined with Tutorial** (20 cards):
- Player has **61 cards** after completing campaign + tutorial

---

### **XP Rewards**
```
XP = 100 + (Location × 10)
```

**Examples**:
- Location 1: 100 + (1 × 10) = **110 XP**
- Location 10: 100 + (10 × 10) = **200 XP**
- Location 40: 100 + (40 × 10) = **500 XP**

**Total Campaign XP**: 
```
Sum(110 to 500 in increments of 10) = 12,200 XP
```

**Player Level After Campaign** (assuming 600 XP per level):
```
12,200 XP ÷ 600 XP/level ≈ Level 20
```

---

## Boss Battles (Special Mechanics)

### **Location 10 - Mid-Boss: "Goblin Warlord"**

**Enemy Deck** (6 cards):
- 1× **Goblin Warlord** (Rare 2★ boss) — 80 HP, 50 MP, 38 ATK, 22 DEF
  - **Boss Ability**: **"Call Reinforcements"** (passive)
    - Every 3 turns, spawn 2× Goblin Raiders (15 HP, 15 ATK)
    - Max 18 total enemies (original 6 + 12 spawns)
- 3× **Goblin Elite** (Uncommon 1★) — 35 HP, 25 ATK, 12 DEF
- 2× **Goblin Raider** (Common 0★) — 15 HP, 18 ATK, 5 DEF

**Special Mechanic**: Turn timer (must defeat boss before Turn 20 or lose)

**Rewards**:
- 300 Gold
- 1× **Hero Pack** (5 cards, 1× Rare hero guaranteed, 10% shiny chance)
- Checkpoint: All player cards restore to 100% HP (free heal)

**Strategy Tips** (in-game hint):
> "Focus the Goblin Warlord first! Use AOE abilities (Aria's Blazing Strike, Gaia's Earthquake) to clear spawns."

---

### **Location 20 - Mid-Boss: "Orc Chieftain"**

**Enemy Deck** (9 cards):
- 1× **Orc Chieftain** (Epic 3★ boss) — 120 HP, 60 MP, 48 ATK, 28 DEF
  - **Boss Ability**: **"Battle Rage"** (passive)
    - When HP drops below 50%, gain +30% Attack and +2 Move
- 3× **Orc Berserker** (Rare 2★) — 55 HP, 35 ATK, 10 DEF
- 3× **Orc Shaman** (Uncommon 1★) — 40 HP, 30 MP, 20 ATK, 15 DEF
  - **Ability**: **"Heal Chieftain"** (15 mana) — Restore 30 HP to Orc Chieftain
- 2× **Orc Grunt** (Common 0★) — 30 HP, 22 ATK, 8 DEF

**Special Mechanic**: Enrage phase (boss changes behavior at 50% HP)

**Rewards**:
- 500 Gold
- 1× **Epic Pack** (5 cards, 1× Epic hero guaranteed, 15% shiny chance)
- Checkpoint: All player cards restore to 100% HP + 50% MP

**Strategy Tips**:
> "Kill the Shamans first! They heal the boss. Save your hero's ultimate for the enrage phase."

---

### **Location 30 - Mid-Boss: "Dragon Wyrmling"**

**Enemy Deck** (12 cards):
- 1× **Dragon Wyrmling** (Legendary 5★ boss) — 180 HP, 80 MP, 60 ATK, 35 DEF
  - **Boss Ability**: **"Flame Breath"** (40 mana, 2-turn cooldown)
    - Deal 80 fire damage to 3 enemies in a cone
  - **Passive**: **"Dragon Scales"** — Take -20% damage from all sources
- 4× **Dragonkin Warrior** (Epic 3★) — 70 HP, 45 ATK, 18 DEF
- 4× **Dragonkin Mage** (Rare 2★) — 50 HP, 40 MP, 35 ATK, 12 DEF
- 3× **Kobold Servant** (Uncommon 1★) — 25 HP, 18 ATK, 6 DEF

**Special Mechanic**: Multi-phase fight (Phase 1: Ground, Phase 2: Dragon flies, melee units can't attack)

**Rewards**:
- 800 Gold
- 1× **Legendary Pack** (5 cards, 1× Legendary hero guaranteed, 25% shiny chance)
- Checkpoint: All player cards restore to 100% HP, unlock new deck slot (+5 cards max deck size)

**Strategy Tips**:
> "Bring ranged units! The dragon flies in Phase 2. Use defensive tactics to survive Flame Breath."

---

### **Location 40 - Final Boss: "Demon Overlord Malakar"**

**Enemy Deck** (15 cards):
- 1× **Malakar, Demon Overlord** (Mythic 6★ boss) — 250 HP, 100 MP, 75 ATK, 40 DEF
  - **Phase 1 Ability**: **"Hellfire Nova"** (35 mana, 3-turn cooldown)
    - Deal 90 fire damage to all enemies, heal 20 HP
  - **Phase 2 Ability** (below 50% HP): **"Summon Inferno"** (50 mana, once per phase)
    - Summon 3× Demon Generals (Epic 3★, 60 HP, 40 ATK)
  - **Passive**: **"Dark Aura"** — All enemy units gain +15% Attack while Malakar is alive
- 4× **Demon General** (Epic 3★) — 80 HP, 50 ATK, 22 DEF
- 4× **Hellhound** (Rare 2★) — 60 HP, 42 ATK, 15 DEF
- 3× **Imp Warlock** (Uncommon 1★) — 35 HP, 30 MP, 28 ATK, 10 DEF
- 3× **Possessed Soldier** (Common 0★) — 25 HP, 20 ATK, 8 DEF

**Special Mechanic**: 
- **Phase 1** (Turns 1-15): Standard battle
- **Phase 2** (Below 50% HP): Malakar summons 3 Demon Generals, enrages (+50% Attack)
- **Turn Limit**: Must defeat boss before Turn 30 (or Malakar summons infinite demons)

**Rewards**:
- 1,000 Gold
- 1× **Mythic Pack** (5 cards, choose 1 of 3 Mythic heroes):
  - **Ragnarok, God of Thunder** (Lightning 6★) — 200 HP, 90 MP, 80 ATK, 35 DEF
  - **Merlin, Archmage Eternal** (Arcane 6★) — 150 HP, 120 MP, 60 ATK, 40 DEF
  - **Terra, World Shaper** (Earth 6★) — 220 HP, 80 MP, 70 ATK, 45 DEF
- **Campaign Completion Achievement**: "Conqueror of the Realm" (cosmetic title)
- **Unlock**: New Game+ mode (replay campaign with harder enemies, better rewards)

**Strategy Tips**:
> "This is it! Use all your best cards. Focus Malakar in Phase 1 to prevent summons. Save hero ultimates for Phase 2."

---

## Location-by-Location Breakdown (1-40)

### **Locations 1-10: Tutorial Extension**

| Location | Type | Enemy Deck | Gold | Card Drop | Notes |
|----------|------|------------|------|-----------|-------|
| 1 | Tutorial Town | 3× Goblin (Common) | 55 | 1× Fire Scout (Common) | First real battle after tutorial |
| 2 | Tutorial Town | 3× Wolf (Common) | 60 | 1× Water Scout (Common) | Introduces beast enemies |
| 3 | Dungeon | 4× Goblin (Common) | 65 | 1× Earth Scout (Common) | First 4-enemy battle |
| 4 | Mine | 4× Orc (Common) | 140 (2× Gold) | None | Teaches resource nodes |
| 5 | Dungeon | 4× Bandit (Common) | 75 | 1× Goblin Raider (Common) | Introduces human enemies |
| 6 | Ruins | 5× Skeleton (Common) | 80 | 1× Fire Soldier (Uncommon) | First Uncommon drop |
| 7 | Dungeon | 5× Zombie (Common) | 85 | 1× Frost Soldier (Common) | Undead enemies |
| 8 | Tutorial Town | 5× Spider (Common) | 90 | 1× Earth Warrior (Common) | Monster enemies |
| 9 | Dungeon | 5× Cultist (Common) | 95 | 1× Scorch Elemental (Common) | Magic enemies |
| 10 | **BOSS ARENA** | **6 cards (Goblin Warlord)** | **300** | **1× Hero Pack** | Mid-boss, checkpoint heal |

**Total**: 1,125 Gold, 9 Common cards + 1 Hero Pack

---

### **Locations 11-20: Difficulty Ramp**

| Location | Type | Enemy Deck | Gold | Card Drop | Notes |
|----------|------|------------|------|-----------|-------|
| 11 | Dungeon | 6× (5 Common, 1 Uncommon) | 105 | 1× Sea Serpent (Uncommon) | First Uncommon enemies |
| 12 | Mine | 6× (5 Common, 1 Uncommon) | 230 (2× Gold) | None | Resource node |
| 13 | Dungeon | 7× (5 Common, 2 Uncommon) | 115 | 1× Vine Archer (Uncommon) | Ranged enemies |
| 14 | Ruins | 7× (5 Common, 2 Uncommon) | 120 | 1× Flame Imp (Rare) | Rare drop |
| 15 | Monster Lair | 7× (5 Common, 2 Uncommon) | 250 | 1× Phoenix Hatchling (Rare) | Epic enemy boss |
| 16 | Dungeon | 7× (5 Common, 2 Uncommon) | 130 | 1× Boulder Beast (Uncommon) | Tanky enemies |
| 17 | Dungeon | 8× (6 Common, 2 Uncommon) | 135 | 1× Elven Archer (Uncommon) | Elven enemies |
| 18 | Tutorial Town | 8× (6 Common, 2 Uncommon) | 140 | 1× Tidal Mage (Uncommon) | Safe zone checkpoint |
| 19 | Dungeon | 8× (6 Common, 2 Uncommon) | 145 | 1× Nature Mage (Uncommon) | Nature enemies |
| 20 | **BOSS ARENA** | **9 cards (Orc Chieftain)** | **500** | **1× Epic Pack** | Mid-boss, enrage mechanic |

**Total**: 1,770 Gold, 9 Uncommon cards + 1 Rare + 1 Epic Pack

---

### **Locations 21-30: Advanced Tactics**

| Location | Type | Enemy Deck | Gold | Card Drop | Notes |
|----------|------|------------|------|-----------|-------|
| 21 | Dungeon | 9× (4 Common, 3 Uncommon, 2 Rare) | 155 | 1× Ember Legionnaire (Rare) | First Rare enemies |
| 22 | Mine | 9× (4 Common, 3 Uncommon, 2 Rare) | 330 (2× Gold) | None | Resource node |
| 23 | Dungeon | 10× (5 Common, 3 Uncommon, 2 Rare) | 165 | 1× Frost Paladin (Rare) | Paladin enemies |
| 24 | Ruins | 10× (5 Common, 3 Uncommon, 2 Rare) | 170 | 1× Rock Golem (Rare) | Golem boss |
| 25 | Dungeon | 10× (5 Common, 3 Uncommon, 2 Rare) | 175 | 1× Water Elemental (Rare) | Elemental enemies |
| 26 | Dungeon | 11× (5 Common, 3 Uncommon, 3 Rare) | 180 | 1× Forest Druid (Rare) | Druid enemies |
| 27 | Monster Lair | 11× (5 Common, 3 Uncommon, 3 Rare) | 350 | 1× Stone Guardian (Rare) | Epic rare boss |
| 28 | Dungeon | 11× (5 Common, 3 Uncommon, 3 Rare) | 190 | 1× Ember Legionnaire (Rare) | Elite units |
| 29 | Tutorial Town | 11× (5 Common, 3 Uncommon, 3 Rare) | 195 | 1× Elven Archer (Rare) | Safe zone checkpoint |
| 30 | **BOSS ARENA** | **12 cards (Dragon Wyrmling)** | **800** | **1× Legendary Pack** | Legendary boss, multi-phase |

**Total**: 2,710 Gold, 9 Rare cards + 1 Legendary Pack

---

### **Locations 31-40: Endgame Challenge**

| Location | Type | Enemy Deck | Gold | Card Drop | Notes |
|----------|------|------------|------|-----------|-------|
| 31 | Dungeon | 12× (3 Common, 3 Uncommon, 3 Rare, 3 Epic) | 205 | 1× Aria (Epic) | Epic hero enemy |
| 32 | Mine | 12× (3 Common, 3 Uncommon, 3 Rare, 3 Epic) | 430 (2× Gold) | None | Resource node |
| 33 | Dungeon | 13× (4 Common, 3 Uncommon, 3 Rare, 3 Epic) | 215 | 1× Thalor (Epic) | Epic hero enemy |
| 34 | Ruins | 13× (4 Common, 3 Uncommon, 3 Rare, 3 Epic) | 220 | 1× Gaia (Epic) | Epic hero enemy |
| 35 | Monster Lair | 13× (4 Common, 3 Uncommon, 3 Rare, 3 Epic) | 450 | 1× Legendary Unit (Epic) | Epic monster boss |
| 36 | Dungeon | 14× (4 Common, 4 Uncommon, 3 Rare, 3 Epic) | 230 | 1× Epic Unit | Elite enemies |
| 37 | Dungeon | 14× (4 Common, 4 Uncommon, 3 Rare, 3 Epic) | 235 | 1× Epic Unit | Mixed armies |
| 38 | Tutorial Town | 14× (4 Common, 4 Uncommon, 3 Rare, 3 Epic) | 240 | 1× Epic Unit | Final checkpoint |
| 39 | Dungeon | 14× (4 Common, 4 Uncommon, 3 Rare, 3 Epic) | 245 | 1× Epic Unit | Pre-boss gauntlet |
| 40 | **BOSS ARENA** | **15 cards (Demon Overlord)** | **1,000** | **1× Mythic Pack** | Final boss, campaign complete |

**Total**: 3,470 Gold, 9 Epic cards + 1 Mythic Pack

---

## Progression Summary

### **Total Campaign Rewards**:

**Gold**: 4,575 Gold total
- Standard battles: 3,275 Gold
- Boss battles: 1,300 Gold (Locations 10, 20, 30, 40)

**Cards**: 41 card drops
- 10× Common (Locations 1-10)
- 10× Uncommon (Locations 11-20)
- 10× Rare (Locations 21-30)
- 10× Epic (Locations 31-39)
- 1× Legendary (Location 40)

**Special Packs**:
- 1× Hero Pack (Location 10)
- 1× Epic Pack (Location 20)
- 1× Legendary Pack (Location 30)
- 1× Mythic Pack (Location 40 - choose 1 of 3)

**XP**: 12,200 XP (Level 1 → ~Level 20)

**Deck Size Unlocks**:
- Start: 20 cards
- Location 10: +5 cards (25 total)
- Location 20: +5 cards (30 total)
- Location 30: +5 cards (35 total)
- Location 40: +5 cards (40 total)

---

## Player Progression Curve

### **Week 1 (Casual Player: 1-2 hours/day)**

**Day 1**:
- Complete tutorial (20 cards)
- Locations 1-5 (5 battles, ~30 min)
- **Total**: 20 cards + 5 Common drops = 25 cards, 375 Gold

**Day 2-3**:
- Locations 6-10 (5 battles, ~45 min)
- **Location 10 Boss**: Goblin Warlord (Hero Pack reward)
- **Total**: 30 cards + 5 from Hero Pack = 35 cards, 800 Gold

**Day 4-7**:
- Locations 11-20 (10 battles, ~2 hours)
- **Location 20 Boss**: Orc Chieftain (Epic Pack reward)
- **Total**: 45 cards + 10 Uncommon drops + 5 from Epic Pack = 60 cards, 2,500 Gold

**Week 1 Result**: Player has 60 cards, 2,500 Gold (2 Standard Packs), Level 12-15

---

### **Week 2 (Casual Player)**

**Day 8-10**:
- Locations 21-30 (10 battles, ~3 hours)
- **Location 30 Boss**: Dragon Wyrmling (Legendary Pack reward)
- **Total**: 75 cards + 10 Rare drops + 5 from Legendary Pack = 90 cards, 5,000 Gold

**Day 11-14**:
- Locations 31-40 (10 battles, ~4 hours)
- **Location 40 Final Boss**: Demon Overlord (Mythic Pack reward)
- **Total**: 105 cards + 10 Epic drops + 5 from Mythic Pack = 120 cards, 9,000 Gold

**Week 2 Result**: Campaign complete, 120+ cards, ~9,000 Gold (9 Standard Packs), Level 20

---

## Difficulty Balancing

### **Enemy Power Scaling**

**Formula**:
```
Enemy Power = Base Stats × (1 + Location × 0.05)
```

**Example**: Goblin Raider
- **Base**: 15 HP, 18 ATK, 5 DEF
- **Location 1**: 15 HP, 18 ATK, 5 DEF (base)
- **Location 10**: 15 × 1.5 = 23 HP, 18 × 1.5 = 27 ATK, 5 × 1.5 = 8 DEF
- **Location 20**: 15 × 2 = 30 HP, 18 × 2 = 36 ATK, 5 × 2 = 10 DEF
- **Location 40**: 15 × 3 = 45 HP, 18 × 3 = 54 ATK, 5 × 3 = 15 DEF

**Why This Works**:
- Location 1: Player has 20 cards (15 starter + 5 Welcome Pack)
- Location 10: Player has ~35 cards (starter + Welcome Pack + 10 drops + packs)
- Location 20: Player has ~60 cards (starter + drops + bought packs)
- Location 40: Player has 100+ cards (full collection)

---

## Replay Value (New Game+)

**Unlocked**: After completing Location 40

**Changes**:
- All enemies have +50% stats
- All boss battles have new Phase 3 mechanics
- Rewards doubled (2× Gold, 2× card drops)
- New exclusive Legendary cards (only available in New Game+)

**Purpose**: Endgame content for players who want challenge after completing campaign

---

## Design Philosophy

**Why This Structure Works**:

1. **Linear Progression**: No branching = clear path, no confusion for new players
2. **Difficulty Curve**: 3 cards → 15 cards = smooth ramp, always challenging but fair
3. **Boss Milestones**: Every 10 Locations = sense of accomplishment, special rewards
4. **Reward Density**: 40 battles × ~115 Gold average = 4,600 Gold (~4-5 packs) = enough to keep opening packs weekly
5. **Card Drops**: 41 guaranteed drops = F2P-friendly, don't need to buy packs to progress
6. **Completion Time**: 6-10 hours = ~2 weeks casual play = right length for MVP (not too short, not too grindy)

---

**Next Steps**:
1. Implement enemy AI (Location 1-10 = basic, Location 11-40 = use abilities strategically)
2. Balance boss mechanics (turn limits, enrage timers, spawn rates)
3. Create boss voicelines (Goblin Warlord: "You dare challenge me?!")
4. Design New Game+ exclusive rewards
