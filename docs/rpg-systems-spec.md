# RPG Systems Specification - Post-MVP

**Last Updated**: December 30, 2025  
**Status**: Phase 2 (Month 2-3) and Phase 3 (Month 4-6)  
**Related**: [combat-calculation-spec.md](combat-calculation-spec.md), [economy-system.md](economy-system.md)

---

## Overview

RPG systems add depth post-MVP:
- **Phase 2**: Health/Mana/Stamina card stats, Consumables (Potions/Scrolls), RPG Shops (Alchemist/Scribe)
- **Phase 3**: Equipment Sockets (Jewel/Rune slots, Diablo-style stat bonuses)

**Design Philosophy**: MVP uses simple Attack/Defense for easy onboarding. Phase 2 adds RPG complexity for long-term engagement (abilities, healing, resource management).

---

## Phase 2: RPG Card Stats (Month 2-3)

### Health System

**All Units Have Health Pools** (replaces MVP's one-hit removal):
- **Common units**: 10-30 Health
- **Uncommon units**: 40-70 Health
- **Rare units**: 80-120 Health
- **Epic units**: 130-180 Health
- **Legendary units**: 200-300 Health
- **Mythic units**: 400-600 Health

**Damage Calculation**:
```
Damage = Attacker Attack - Defender Defense
Defender Health = Current Health - Damage
Unit Dies if Health ≤ 0
```

**Example Combat**:
```
Fire Mage (Attack 40) attacks Goblin Raider (Defense 5, Health 20)
Damage = 40 - 5 = 35
Goblin Health = 20 - 35 = -15 (dies in one hit, same as MVP)

Fire Mage (Attack 40) attacks Dragon Knight (Defense 30, Health 150)
Damage = 40 - 30 = 10
Dragon Knight Health = 150 - 10 = 140 (survives, tanks damage)
```

**Health Regeneration** (Out of Combat):
- Passive regen: 1% max Health per minute
- Full heal time: 100 minutes (1 hour 40 minutes for 100% Health)
- Example: 150 Health unit = 150 minutes to full heal = 2.5 hours

**Health Regeneration** (In Combat):
- No passive regen (must use abilities or consumables)
- Heal spell: Restore 50-100 Health (costs Mana)
- Health Potion: Restore 20% max Health instantly

---

### Mana System

**All Spellcaster Units Have Mana**:
- **Melee units** (Warriors, Archers): 0 Mana (physical attacks only)
- **Spellcasters** (Mages, Clerics, Shamans): 50-100 Mana
- **Heroes**: 80-150 Mana (hybrid physical/magical abilities)

**Mana Costs**:
- Basic abilities: 10-20 Mana (minor buffs, weak spells)
- Intermediate abilities: 30-40 Mana (Fireball, Lightning Bolt, Heal)
- Ultimate abilities: 50-100 Mana (AOE damage, mass healing, summons)

**Ability Examples**:
```
Fireball (Fire Mage)
- Cost: 30 Mana
- Damage: 60 (ignores Defense)
- Range: 3 hexes
- Cooldown: 2 turns

Lightning Bolt (Lightning Mage)
- Cost: 40 Mana
- Damage: 80 (ignores Defense)
- Effect: Stun target for 1 turn
- Range: 5 hexes
- Cooldown: 3 turns

Mass Heal (Cleric)
- Cost: 50 Mana
- Effect: Restore 30 Health to all allies within 3 hexes
- Range: 3-hex radius
- Cooldown: 4 turns

Dragon Breath (Dragon Knight)
- Cost: 80 Mana
- Damage: 100 AOE (hits all units in 5-hex cone)
- Range: 5 hexes
- Cooldown: 5 turns
```

**Mana Regeneration** (Out of Combat):
- Passive regen: 10 Mana per minute
- Full restore time: 100 Mana = 10 minutes
- Example: Fire Mage (80 Mana) = 8 minutes to full restore

**Mana Regeneration** (In Combat):
- Passive regen: 5 Mana per turn
- Consumables: Mana Potion restores 50 Mana instantly
- Abilities: Some cards have "Meditate" (skip turn, restore 30 Mana)

---

### Stamina System

**All Units Have Stamina** (movement on battle map):
- **Heavy units** (Warriors, Golems): 1-2 hexes per turn
- **Medium units** (Archers, Mages): 3-4 hexes per turn
- **Light units** (Scouts, Assassins): 5-6 hexes per turn
- **Flying units** (Dragons, Phoenixes): 8-10 hexes per turn (ignore terrain)

**Movement Costs**:
- Moving 1 hex: 1 Stamina
- Attacking: 0 Stamina (can move THEN attack)
- Abilities: Some cost Stamina (e.g., "Charge: Move 3 hexes, attack, costs 3 Stamina")

**Stamina Regeneration** (Out of Combat):
- Instant refill: 5 minutes
- Example: Dragon (10 Stamina) refills in 5 minutes

**Stamina Regeneration** (In Combat):
- Full refill each turn (no accumulation across turns)
- Consumables: Stamina Potion refills instantly (used for multi-turn movement)

**Example Turn**:
```
Dragon Knight (Stamina 4)
- Turn 1: Move 4 hexes forward (4 Stamina used)
- Turn 1: Attack enemy (0 Stamina cost)
- Turn 2: Stamina refills to 4, can move again
```

---

### Realm Map Army Health Display

**Combined Health Percentage**:
- Sovereign's army shows as 0-100% on Realm Map
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

**Health Display on Realm Map**:
- 100%: Green (full army, ready to fight)
- 75-99%: Yellow (wounded, still strong)
- 50-74%: Orange (weakened, risky to fight)
- 25-49%: Red (critical, retreat recommended)
- 0-24%: Dark Red (near death, heal before fighting)

**Healing Options** (Phase 2):
- Passive regen: 1% max Health per minute (350 Health = 350 minutes = 5.8 hours to full)
- Health Potion: Restore 20% max Health instantly (350 × 0.2 = 70 Health)
- Rest at Town: Full heal instantly (free, requires Town Location on map)

---

## Phase 2: Consumables (Month 2-3)

### Health Potions

**Effect**: Restore 20% max Health to target unit instantly

**Earning Sources**:
- Battle chests: 1-3 Health Potions (Bronze = 1, Silver = 2, Gold = 3)
- Quest rewards: 5-10 Health Potions (Phase 2)
- RPG Shop: Alchemist sells Health Potions (200 Gold each, cannot buy with Gems)

**Usage**:
- Click unit, select "Use Health Potion" from menu
- Instant heal (no turn cost)
- Cannot use in combat (out-of-combat only for MVP Phase 2)

**Example**:
```
Dragon Knight (50/150 Health, wounded after battle)
Use Health Potion: 150 × 0.2 = 30 Health restored
New Health: 50 + 30 = 80/150 Health (53% army health)
```

**Stacking**:
- Inventory limit: 99 Health Potions (prevents hoarding)
- Can use multiple potions on same unit (1 per click)

---

### Mana Potions

**Effect**: Restore 50 Mana to target unit instantly

**Earning Sources**:
- Battle chests: 1-3 Mana Potions (Bronze = 1, Silver = 2, Gold = 3)
- Quest rewards: 5-10 Mana Potions
- RPG Shop: Alchemist sells Mana Potions (300 Gold each, rarer than Health)

**Usage**:
- Click unit, select "Use Mana Potion"
- Instant restore (no turn cost)
- Can use in combat (Phase 3, MVP Phase 2 = out-of-combat only)

**Example**:
```
Fire Mage (30/80 Mana, used Fireball twice)
Use Mana Potion: +50 Mana
New Mana: 30 + 50 = 80/80 Mana (full restore)
```

---

### Stamina Potions

**Effect**: Refill Stamina to max instantly

**Earning Sources**:
- Battle chests: 1-2 Stamina Potions (rare)
- Quest rewards: 3-5 Stamina Potions
- RPG Shop: Alchemist sells Stamina Potions (100 Gold each, common)

**Usage**:
- Used automatically during Realm Map movement (not manual)
- If unit runs out of Movement Points, prompt: "Use Stamina Potion? (1 remaining)"
- Click Yes: Refill 10 Movement Points, continue moving

**Example**:
```
Sovereign has 0/10 Movement Points (used all today)
Wants to move 5 more hexes to reach Town
System prompts: "Use Stamina Potion? (3 remaining)"
Sovereign clicks Yes: +10 Movement Points, moves 5 hexes, 5 MP remain for tomorrow
```

---

### Scrolls (Tactical Abilities)

**Effect**: Single-use abilities (replaces equipping Tactic cards to deck)

**Earning Sources**:
- Battle chests: 1-3 Scrolls (random rarity)
- Quest rewards: 5-10 Scrolls
- RPG Shop: Scribe sells Scrolls (500-2,000 Gold based on rarity)

**Scroll Types**:
- **Fireball Scroll** (Uncommon): 60 damage, 3-hex range, single-use
- **Lightning Bolt Scroll** (Rare): 80 damage + Stun, 5-hex range, single-use
- **Mass Heal Scroll** (Epic): Restore 30 Health to all allies, single-use
- **Summon Phoenix Scroll** (Legendary): Summon Phoenix unit (20 Health, 5 turns), single-use

**Usage**:
- Click Scroll icon in battle UI, select target hex, confirm
- Scroll is consumed (removed from inventory)
- No Mana cost (Scrolls bypass Mana system)

**Strategic Value**:
- Deck slots saved (no need to equip Tactic cards)
- Flexibility (carry 10 Scrolls, use situationally)
- F2P advantage (earn Scrolls from chests, don't need to buy packs)

---

## Phase 2: RPG Shop System (Month 2-3)

### Shop Types

**Alchemist** (Potions):
- Health Potion: 200 Gold (restore 20% max Health)
- Mana Potion: 300 Gold (restore 50 Mana)
- Stamina Potion: 100 Gold (refill Movement Points)
- Mega Health Potion: 1,000 Gold (restore 50% max Health, Phase 3)

**Scribe** (Scrolls):
- Fireball Scroll: 500 Gold
- Lightning Bolt Scroll: 1,000 Gold
- Mass Heal Scroll: 2,000 Gold
- Summon Phoenix Scroll: 5,000 Gold

**Central Mall Screen** (Phase 2):
- Combines Pack Store, Alchemist, Scribe into one UI
- Tabs: Packs | Potions | Scrolls
- Prevents navigation bloat (no separate shop screens)

**Future Shops** (Phase 3+):
- Jeweler: Equipment Sockets (Jewel/Rune slots)
- Blacksmith: Equipment crafting (Lumber/Ore recipes)
- PvP Store: Arena Token exclusives

---

### Shop UI Flow

**Central Mall Screen**:
```
[Packs] [Potions] [Scrolls]

Packs Tab:
- Standard Pack: 1,000 Gold (5 cards)
- Element Booster: 2,000 Gold (5 cards)
- Epic Booster: 5,000 Gold (5 cards)
- Premium Pack: 100 Gems (5 cards, 10% shiny rate)

Potions Tab:
- Health Potion: 200 Gold (x99 inventory limit)
- Mana Potion: 300 Gold (x99 inventory limit)
- Stamina Potion: 100 Gold (x99 inventory limit)

Scrolls Tab:
- Fireball Scroll: 500 Gold (x99 inventory limit)
- Lightning Bolt Scroll: 1,000 Gold (x99 inventory limit)
- Mass Heal Scroll: 2,000 Gold (x99 inventory limit)
```

**Purchase Flow**:
1. Sovereign clicks "Potions" tab
2. Selects "Health Potion" (200 Gold)
3. Quantity slider: 1-99 (default 1)
4. Confirms: "Buy 5× Health Potion for 1,000 Gold?"
5. Transaction completes, inventory updated

---

## Phase 3: Equipment Sockets (Month 4-6)

### Socket System (Diablo-Style)

**Rarity-Based Sockets**:
- Common equipment: 0 sockets (no attachments)
- Uncommon equipment: 1 socket
- Rare equipment: 1 socket
- Epic equipment: 2 sockets
- Legendary equipment: 2 sockets
- Mythic equipment: 3 sockets

**Socket Types**:
- **Jewel Slots**: Stat bonuses (+Attack, +Defense, +Health, +Mana)
- **Rune Slots**: Elemental affinity (+10% Fire damage, +10% Water resistance)

**Example Equipment**:
```
Epic Fire Sword (2 sockets)
- Base Stats: +20 Attack
- Socket 1: Ruby (+10 Attack)
- Socket 2: Fire Rune (+10% Fire damage)
- Total Bonus: +30 Attack, +10% Fire damage

Mythic Dragon Armor (3 sockets)
- Base Stats: +40 Defense
- Socket 1: Diamond (+20 Defense)
- Socket 2: Emerald (+50 Health)
- Socket 3: Earth Rune (+10% Earth resistance)
- Total Bonus: +60 Defense, +50 Health, +10% Earth resistance
```

---

### Jewel Types

**Attack Jewels**:
- Minor Ruby: +5 Attack (common drop)
- Ruby: +10 Attack (uncommon drop)
- Flawless Ruby: +20 Attack (rare drop)

**Defense Jewels**:
- Minor Diamond: +5 Defense
- Diamond: +10 Defense
- Flawless Diamond: +20 Defense

**Health Jewels**:
- Minor Emerald: +20 Health
- Emerald: +50 Health
- Flawless Emerald: +100 Health

**Mana Jewels**:
- Minor Sapphire: +10 Mana
- Sapphire: +20 Mana
- Flawless Sapphire: +40 Mana

**Earning Sources**:
- Battle chests: 1-3 Jewels (Bronze = Minor, Gold = Flawless)
- Quest rewards: 5-10 Jewels
- Jeweler Shop: 500-5,000 Gold (cannot buy with Gems)

---

### Rune Types (Elemental)

**Offensive Runes**:
- Fire Rune: +10% Fire damage
- Water Rune: +10% Water damage
- Earth Rune: +10% Earth damage
- Lightning Rune: +10% Lightning damage

**Defensive Runes**:
- Fire Resistance Rune: -10% Fire damage taken
- Water Resistance Rune: -10% Water damage taken
- Earth Resistance Rune: -10% Earth damage taken
- Lightning Resistance Rune: -10% Lightning damage taken

**Earning Sources**:
- Boss battles: 1× Rune (guaranteed from Epic/Legendary bosses)
- PvP Arena rewards: 1-3 Runes (top 100 players)
- Jeweler Shop: 2,000-10,000 Gold (rare, cannot buy with Gems)

---

### Socket Removal & Replacement

**Removing Jewels/Runes**:
- Cost: 100 Gold per socket
- Jewel/Rune is destroyed (not returned to inventory)
- Use case: Replacing Minor Ruby (+5 Attack) with Flawless Ruby (+20 Attack)

**Example**:
```
Epic Fire Sword (2 sockets)
- Socket 1: Minor Ruby (+5 Attack)
- Socket 2: Fire Rune (+10% Fire damage)

Sovereign finds Flawless Ruby (+20 Attack)
- Clicks "Remove Socket 1" (100 Gold)
- Minor Ruby is destroyed
- Inserts Flawless Ruby (+20 Attack)
- New Stats: +40 Attack (base +20, Flawless Ruby +20), +10% Fire damage
```

---

## Implementation Roadmap

### Phase 2 (Month 2-3)
- [ ] Health/Mana/Stamina stats (add to card-schema.json)
- [ ] Health Potions (restore 20% max Health, inventory system)
- [ ] Mana Potions (restore 50 Mana, out-of-combat use)
- [ ] Stamina Potions (refill Movement Points on Realm Map)
- [ ] Scrolls (single-use abilities, bypass Mana system)
- [ ] Alchemist Shop (buy Potions with Gold)
- [ ] Scribe Shop (buy Scrolls with Gold)
- [ ] Central Mall Screen (Packs/Potions/Scrolls tabs)
- [ ] Realm Map army health % display

### Phase 3 (Month 4-6)
- [ ] Equipment Sockets (1-3 slots based on rarity)
- [ ] Jewels (Attack/Defense/Health/Mana bonuses)
- [ ] Runes (Elemental affinity, offensive/defensive)
- [ ] Jeweler Shop (buy Jewels/Runes with Gold)
- [ ] Socket removal system (100 Gold, destroys old Jewel/Rune)
- [ ] Mana Potions in combat (Phase 3, instant restore during battle)

---

**For combat formulas, see**: [combat-calculation-spec.md](combat-calculation-spec.md)  
**For economy balance, see**: [economy-system.md](economy-system.md)  
**For MVP scope, see**: [mvp-scope-final.md](mvp-scope-final.md)  
**For data specifications, see**: [card-schema.json](specs/card-schema.json), [consumable-schema.json](specs/consumable-schema.json), [shop-schema.json](specs/shop-schema.json), [socket-schema.json](specs/socket-schema.json)
