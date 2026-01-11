# Combat System Calculations

**Last Updated**: January 10, 2026  
**Status**: MVP uses HP/Mana/ATK/DEF with ability system, Phase 2 adds elemental counters, Phase 3 adds status effects  
**Related**: [game-bible.md](game-bible.md) Section 8, [starter-cards.json](../specs/starter-cards.json), [deck-progression-rules.md](deck-progression-rules.md)

---

## Overview

Sovereign Territories combat evolves across 3 phases:
- **MVP (Tactical)**: HP/Mana/ATK/DEF stats, ability system, 8×8 tactical battles
- **Phase 2 (Elemental)**: Fire > Earth > Water > Fire counter-play (1.5× damage multiplier)
- **Phase 3 (Advanced)**: Status effects (burn, freeze, stun), terrain modifiers (forest, water, mountains)

**Design Philosophy**: Start with tactical depth (positioning, abilities, hero synergies), add complexity post-launch once core gameplay is proven.

---

## ❌ **MVP CLARIFICATION: Elemental Mechanics**

**Critical Design Note** (Updated January 10, 2026):

- ❌ **NOT in MVP**: Elemental counter-play (Fire > Earth > Water > Fire with 1.5× damage multiplier)
- ❌ **NOT in MVP**: Element-specific buffs (Fire Aura only buffs Fire units)
- ❌ **NOT in MVP**: Terrain element interactions (Fire units stronger on lava tiles)

- ✅ **MVP ONLY**: **Elements are visual flavor and identity**
  - Fire heroes look red/orange, use flame VFX
  - Water heroes look blue/cyan, use water VFX
  - Earth heroes look brown/green, use stone/root VFX
  - **Damage formula is identical**: `Damage = ATK - DEF` (no element multipliers)
  - **Example**: Aria (Fire) attacking Thalor (Water) uses same formula as Aria attacking Gaia (Earth)

**Why This Decision**:
1. **Simplicity**: New players learn 1 damage formula, not 6 element interactions
2. **Balance**: Easier to balance 3 starter decks (Fire/Water/Earth) when they're numerically equal
3. **Iteration Speed**: Can ship MVP faster without tuning element multiplier math
4. **Phase 2 Upgrade Path**: Once core loop validated, add counter-play as expansion feature

**Phase 2 Design** (Future):
- Fire > Earth (burns forests, 1.5× damage)
- Earth > Water (dams rivers, 1.5× damage)
- Water > Fire (extinguishes flames, 1.5× damage)
- Lightning > Water (conducts, 1.5× damage)
- Wind > Lightning (disperses electricity, 1.5× damage)
- Frost > Wind (freezes air, 1.5× damage)

**For MVP**: Treat all elements as cosmetic themes. Focus playtesting on ability balance (Aria's Blazing Strike vs Thalor's Tidal Wave), not element counters.

---

## MVP Combat Formula (8-Week Implementation)

### Card Stats (Simple)

**All Cards Have**:
- **Attack**: Offensive power (1-100 scale)
- **Defense**: Damage reduction (0-50 scale)
- **Type**: Hero, Unit, Building, Tactic

**Example Cards**:
```
Common Goblin Raider
- Attack: 10
- Defense: 5

Rare Elven Archer
- Attack: 25
- Defense: 10

Epic Fire Mage
- Attack: 40
- Defense: 15

Legendary Dragon Knight
- Attack: 70
- Defense: 30
```

---

### Damage Calculation (MVP)

**Formula**:
```
Damage = Attacker Attack - Defender Defense
Minimum Damage = 1 (always deal at least 1 damage)
```

**Example Combat**:
```
Goblin Raider (Attack 10) attacks Elven Archer (Defense 10)
Damage = 10 - 10 = 0 → Minimum 1 damage
(Goblin is weak but can still chip away)

Elven Archer (Attack 25) attacks Goblin Raider (Defense 5)
Damage = 25 - 5 = 20 damage
(Archer deals strong damage to weak unit)

Fire Mage (Attack 40) attacks Dragon Knight (Defense 30)
Damage = 40 - 30 = 10 damage
(High defense reduces damage significantly)
```

---

### Unit Death (MVP)

**MVP uses "One-Hit Removal"**:
- Any damage removes unit from battlefield (simplified for MVP)
- No HP tracking (simplifies UI, speeds up battles)
- Tactical focus: positioning, card advantage, not HP management

**Example**:
```
Goblin Raider attacks Elven Archer
- Damage = 10 - 10 = 1 (minimum)
- Elven Archer is removed from battlefield (killed)
- Goblin Raider survives (attacker doesn't take counter-damage in MVP)
```

**Phase 2 Change**: Units have Health pools, survive multiple attacks (see below).

---

### Critical Hits (MVP - Simple)

**Formula**:
```
Critical Chance = 10% (flat rate for all units)
Critical Damage = 1.5× normal damage
```

**Example**:
```
Fire Mage (Attack 40) attacks Dragon Knight (Defense 30)
Normal Damage = 40 - 30 = 10
Critical Damage = 10 × 1.5 = 15 damage
(10% chance to crit on each attack)
```

**Phase 3 Change**: Critical chance based on Speed stat (see Advanced Combat).

---

### Rarity Budget (Anti-Pay-to-Win)

**Purpose**: Prevent whales from fielding all-Legendary decks.

**Rarity Point Costs**:
- Common: 1 point
- Uncommon: 2 points
- Rare: 4 points
- Epic: 8 points
- Legendary: 16 points
- Mythic: 32 points

**Deck Budget by Player Level**:
- Level 1-5: 60 points (1 Epic + 19 Commons = 1×8 + 19×1 = 27 points)
- Level 10: 80 points (2 Epics + 18 Commons = 2×8 + 18×1 = 34 points)
- Level 20: 120 points (3 Epics + 17 Commons = 3×8 + 17×1 = 41 points)
- Level 30: 200 points (2 Legendaries + 18 Commons = 2×16 + 18×1 = 50 points)

**Example F2P Deck** (Level 1, 60-point budget):
```
1× Epic Fire Mage (8 points, Attack 40, Defense 15)
19× Common Goblins/Archers (19 points, Attack 10-15, Defense 5-10)
Total: 27 points (fits budget)
```

**Example Whale Deck** (Level 1, 60-point budget):
```
INVALID: 6× Legendary Dragons (6×16 = 96 points) - EXCEEDS BUDGET
VALID: 3× Legendary Dragons (3×16 = 48 points) + 12× Commons (12 points) = 60 points

Whale has 3 strong units (Legendary Dragons) but only 15 total cards (vs F2P's 20)
Whale loses card advantage, F2P can swarm with numbers
```

**Verdict**: Rarity Budget prevents pay-to-win. Whales have stronger individual cards but fewer total cards.

---

### PvP Matchmaking (Deck Power Brackets)

**Purpose**: F2P players fight F2P, whales fight whales.

**Deck Power Calculation**:
```
Deck Power = Sum of (Card Attack + Card Defense) for all cards in deck
```

**Example Decks**:
```
F2P Deck (20 cards, mostly Commons):
- 1× Epic Fire Mage (Attack 40 + Defense 15 = 55)
- 19× Commons (avg Attack 12 + Defense 7 = 19 each)
Total Deck Power = 55 + (19 × 19) = 416

Whale Deck (15 cards, 3 Legendaries):
- 3× Legendary Dragons (Attack 70 + Defense 30 = 100 each)
- 12× Commons (avg Attack 12 + Defense 7 = 19 each)
Total Deck Power = (3 × 100) + (12 × 19) = 528
```

**Matchmaking Brackets**:
- Bronze (Deck Power 0-400): Mostly F2P, beginner decks
- Silver (Deck Power 401-600): Mid-tier F2P, light spenders
- Gold (Deck Power 601-900): Competitive F2P, moderate whales
- Platinum (Deck Power 901+): Hardcore whales, max-rarity decks

**Verdict**: F2P player (416 Deck Power) matches in Bronze bracket, never faces Whale (528 Deck Power in Silver). Fair matchmaking.

---

## Phase 2 Combat (Post-MVP, Month 2-3) - RPG Stats

### Card Stats (RPG System)

**All Cards Have**:
- **Health**: Hit points (10-200 scale, survives multiple attacks)
- **Mana**: Powers abilities (10-100 scale, costs 5-50 per ability)
- **Stamina**: Movement on battle board (1-5 hexes per turn)
- **Attack**: Physical damage (replaces simple Attack stat)
- **Defense**: Damage reduction (replaces simple Defense stat)

**Example Cards** (Phase 2):
```
Common Goblin Raider
- Health: 20
- Mana: 10
- Stamina: 3 hexes/turn
- Attack: 10
- Defense: 5

Epic Fire Mage
- Health: 50
- Mana: 80
- Stamina: 2 hexes/turn
- Attack: 40
- Defense: 15
- Ability: Fireball (30 Mana, 60 damage, 3-hex range)

Legendary Dragon Knight
- Health: 150
- Mana: 50
- Stamina: 4 hexes/turn
- Attack: 70
- Defense: 30
- Ability: Dragon Breath (40 Mana, 100 AOE damage, 5-hex cone)
```

---

### Damage Calculation (Phase 2)

**Formula**:
```
Damage = Attacker Attack - Defender Defense
Health Remaining = Defender Health - Damage
Unit Dies if Health ≤ 0
```

**Example Combat**:
```
Fire Mage (Attack 40) attacks Goblin Raider (Defense 5, Health 20)
Damage = 40 - 5 = 35
Goblin Health = 20 - 35 = -15 (dies in one hit)

Goblin Raider (Attack 10) attacks Fire Mage (Defense 15, Health 50)
Damage = 10 - 15 = -5 → Minimum 1 damage
Fire Mage Health = 50 - 1 = 49 (survives, barely scratched)
```

---

### Ability System (Phase 2)

**TODO: Create ability template system (10-20 ability archetypes for designers)**  
**TODO: Design AOE targeting UI (cone, circle, line-of-sight preview)**  
**TODO: Determine cooldown reduction mechanics (CDR stat, items, hero abilities?)**

**Mana Costs**:
- Basic abilities: 10-20 Mana (melee strikes, minor buffs)
- Intermediate abilities: 30-40 Mana (spells, ranged attacks)
- Ultimate abilities: 50-100 Mana (AOE damage, healing, summons)

**Ability Examples**:
```
Fireball (Fire Mage)
- Cost: 30 Mana
- Damage: 60 (ignores Defense)
- Range: 3 hexes
- Cooldown: 2 turns

Dragon Breath (Dragon Knight)
- Cost: 40 Mana
- Damage: 100 AOE (hits all units in 5-hex cone)
- Range: 5 hexes
- Cooldown: 3 turns

Heal (Cleric)
- Cost: 20 Mana
- Effect: Restore 50 Health to target ally
- Range: 4 hexes
- Cooldown: 1 turn
```

**TODO: Should abilities crit? (2× Fireball damage = 120 instead of 60?)**  
**TODO: Design ability interrupts (can Silence stop casting? Stun cancel channeling?)**

**Mana Regeneration**:
- Out of combat: 10 Mana per minute (600 Mana per hour)
- In combat: 5 Mana per turn (slower regen during battle)
- Consumables: Mana Potion restores 50 Mana instantly (see [rpg-systems-spec.md](rpg-systems-spec.md))

**TODO: Should regen scale with unit rarity? (Legendary = 8 Mana/turn, Common = 3?)**

---

### Stamina System (Phase 2)

**Movement on Battle Board**:
- Each unit has Stamina (1-5 hexes per turn)
- Moving 1 hex costs 1 Stamina
- Attacking costs 0 Stamina (can move THEN attack)
- Abilities may cost Stamina (e.g., "Charge: Move 3 hexes, attack, costs 3 Stamina")

**Example Turn**:
```
Dragon Knight (Stamina 4)
- Turn 1: Move 4 hexes forward (4 Stamina used)
- Turn 1: Attack enemy (0 Stamina cost)
- Turn 2: Stamina refills to 4, can move again
```

**Stamina Regeneration**:
- Out of combat: Full refill in 5 minutes
- In combat: Full refill each turn
- Consumables: Stamina Potion refills instantly (see [rpg-systems-spec.md](rpg-systems-spec.md))

---

### Realm Map Army Health (Phase 2)

**Combined Health Display**:
- Sovereign's army shows as percentage (0-100%)
- Percentage = (Total Current Health) / (Total Max Health)

**Example**:
```
Army Composition:
- 1× Dragon Knight (150/150 Health)
- 5× Goblins (20/20 Health each = 100 total)
- 2× Fire Mages (50/50 Health each = 100 total)

Total Max Health = 150 + 100 + 100 = 350
Total Current Health = 350 (all units at full)
Army Health % = 350 / 350 = 100%

After Battle (some units wounded):
- Dragon Knight: 50/150 Health (-100 damage)
- Goblins: 2 died, 3 remaining at 15/20 each = 45 total
- Fire Mages: 1 died, 1 at 30/50 = 30 total

Total Current Health = 50 + 45 + 30 = 125
Army Health % = 125 / 350 = 36% (shows on Realm Map)
```

**Health Regeneration** (Phase 2):
- Out of combat: 1% max Health per minute (full heal in ~100 minutes)
- Large armies take longer (350 Health = 350 minutes to full heal = 5.8 hours)
- Consumables: Health Potion restores 20% max Health instantly (see [rpg-systems-spec.md](rpg-systems-spec.md))

---

## Phase 3 Combat (Post-MVP, Month 4-6) - Advanced Mechanics

### Elemental Interactions

**Element Triangle**:
```
Fire > Earth (+50% damage)
Earth > Water (+50% damage)
Water > Fire (+50% damage)
```

**Example**:
```
Fire Mage (Attack 40, Fire element) attacks Earth Golem (Defense 30, Earth element)
Base Damage = 40 - 30 = 10
Elemental Bonus = 10 × 1.5 = 15 damage (Fire > Earth)

Earth Golem (Attack 35, Earth element) attacks Fire Mage (Defense 15, Fire element)
Base Damage = 35 - 15 = 20
No Elemental Bonus (Earth neutral to Fire, only Fire > Earth applies)
```

**Neutral Elements**:
- Lightning, Holy, Shadow (no weakness/resistance)
- Deal normal damage to all elements

---

### Status Effects

**TODO: Determine exact durations and damage values (2-5 turns? percentage vs flat damage?)**  
**TODO: Design stacking mechanics (can 2 Burn effects stack? diminishing returns?)**  
**TODO: Create purge/cleanse system (can Water Mage cleanse Burn? Priest purge Poison?)**

**Burn** (Fire element):
- Effect: 5 damage per turn for 3 turns
- Total Damage: 15 over time
- Example: Fire Mage's Fireball inflicts Burn on hit

**TODO: Should Burn scale with attacker's Attack stat? (10% of Attack/turn instead of flat 5?)**

**Freeze** (Water element):
- Effect: Skip next turn (unit cannot move or attack)
- Duration: 1 turn
- Example: Ice Mage's Frostbolt freezes target for 1 turn

**TODO: Should Freeze have slow phase after? (1 turn frozen, 1 turn -50% speed?)**  
**TODO: Can Fire attacks melt Freeze early? (thaw mechanic)**

**Poison** (Earth element):
- Effect: 10% max Health per turn for 3 turns
- Total Damage: 30% max Health
- Example: Goblin Assassin's Poison Blade inflicts Poison

**TODO: Should Poison reduce healing? (-50% healing effectiveness while poisoned)**  
**TODO: Can Antidote consumable cure Poison? (see rpg-systems-spec.md)**

**Stun** (Lightning element):
- Effect: Skip next turn + cannot be healed
- Duration: 1 turn
- Example: Lightning Bolt ability stuns target

---

### Terrain Modifiers (Phase 3)

**TODO: Finalize exact percentage bonuses for each terrain type**  
**TODO: Design stacking rules (do Forest + Mountain combine? +10% + 20% = +30%?)**  
**TODO: Determine line-of-sight mechanics (does Forest block ranged attacks?)**

**Mountain Hexes**:
- +20% Defense for units on mountains
- Impassable (unless unit has Flying)

**Water Hexes**:
- -20% Movement (costs 2 Stamina to move 1 hex)
- Impassable (unless unit has Swimming or Flying)

**Forest Hexes**:
- +10% Evasion (10% chance to dodge attacks)
- Passable (costs 1 Stamina per hex)

**Plains Hexes**:
- No modifiers (normal terrain)
- Passable (costs 1 Stamina per hex)

**TODO: Add Hills terrain (+10% Defense, +1 range for archers?)**  
**TODO: Add Desert terrain (-1 Stamina per turn, thirst effect?)**  
**TODO: Add Snow terrain (Freeze effect on units without Cold Resist?)**

---

### Critical Hit System (Phase 3 - Speed-Based)

**TODO: Design diminishing returns formula (prevent 100% crit at high Speed differences)**  
**TODO: Determine if shields block crits (75% crit resistance for Shield units?)**  
**TODO: Create crit visual feedback (red damage numbers, screen shake, particles)**

**Formula**:
```
Critical Chance = (Attacker Speed - Defender Speed) / 10
Maximum Crit Chance = 50%
Minimum Crit Chance = 5%
```

**Example**:
```
Elven Archer (Speed 30) attacks Goblin (Speed 10)
Crit Chance = (30 - 10) / 10 = 2% → Minimum 5%

Dragon (Speed 50) attacks Turtle (Speed 5)
Crit Chance = (50 - 5) / 10 = 4.5% → Rounds to 5%

Lightning Assassin (Speed 80) attacks Dragon Knight (Speed 20)
Crit Chance = (80 - 20) / 10 = 6% → 6% crit chance
```

**Critical Damage**:
- 2× normal damage (Phase 3, increased from MVP's 1.5×)

**TODO: Should critical hits have bonus effects? (Burn on fire crits, Freeze on water crits?)**  
**TODO: Design crit counter-tactics (items/abilities that reduce enemy crit chance)**

---

## Implementation Roadmap

### MVP (Week 1-8)
- ✅ Simple Attack/Defense stats (1-100 scale)
- ✅ One-hit removal (no Health pools)
- ✅ 10% flat critical chance
- ✅ Rarity Budget (60-200 points by level)
- ✅ PvP Matchmaking (Deck Power brackets)
- ❌ No elemental interactions
- ❌ No status effects
- ❌ No terrain modifiers

### Phase 2 (Month 2-3)
- ❌ Health/Mana/Stamina stats (RPG system)
- ❌ Ability system (Mana costs, cooldowns)
- ❌ Health regeneration (1% per minute out of combat)
- ❌ Realm Map army health % display
- ❌ Consumables (Potions/Scrolls, see [rpg-systems-spec.md](rpg-systems-spec.md))

### Phase 3 (Month 4-6)
- ❌ Elemental interactions (Fire > Earth > Water > Fire)
- ❌ Status effects (Burn, Freeze, Poison, Stun)
- ❌ Terrain modifiers (Mountain, Water, Forest, Plains)
- ❌ Speed-based critical chance

---

**For MVP implementation details, see**: [mvp-scope-final.md](mvp-scope-final.md)  
**For economy balance, see**: [economy-system.md](economy-system.md)  
**For RPG systems, see**: [rpg-systems-spec.md](rpg-systems-spec.md)  
**For data specifications, see**: [card-schema.json](specs/card-schema.json)
