# Base Set Master Execution Plan

**Date**: January 11, 2026  
**Objective**: Build complete, production-ready card architecture for 140-card Base Set  
**Status**: EXECUTION IN PROGRESS

---

## Success Criteria

✅ All 140 Base Set cards fully defined (stats, abilities, lore, art references)  
✅ All products defined (3 starter boxes, 9 pack types, daily rewards)  
✅ Consistent naming conventions (no conflicts, no copyright issues)  
✅ Modular directory structure (series expansion-ready)  
✅ Complete documentation (loading strategy, collection tracking)  
✅ Validation scripts (ensure no duplicate IDs, valid references)

---

## Phase 1: Architecture Validation ✅

**Deliverables**:
- [x] card-architecture-codex-series.md (comprehensive design doc)
- [x] Directory structure created: codex/{series}/{element}/
- [x] Naming conventions defined (HERO_, UNIT_, TACTIC_, BUILDING_)
- [x] Collection numbering system (BS-001 to BS-140)

**Validation Checks**:
- [x] No copyrighted names (unique world lore)
- [x] Consistent ID format (CATEGORY_NAME_VARIANT)
- [x] Series code unique (BS = Base Set, EF = Elemental Fury, etc.)

---

## Phase 2: Base Set Infrastructure

**Deliverables**:
1. `docs/codex/base-set/series-manifest.json` (series metadata)
2. `docs/codex/_schema.json` (card validation schema)
3. `docs/codex/README.md` (codex philosophy, usage)
4. `docs/products/README.md` (product system overview)
5. `docs/collection/README.md` (collection tracking strategy)

**Validation Checks**:
- [ ] Series manifest has all required fields (seriesId, totalCards, etc.)
- [ ] Schema covers all card types (Hero, Unit, Tactic, Building)
- [ ] READMEs explain system to new developers

---

## Phase 3: Fire Element Cards (25 Cards)

**Card Breakdown**:
- **Heroes** (5): BS-001 to BS-005
  - BS-001: Aria, Flame Knight (Epic, starter hero, AOE burst)
  - BS-002: Ragnar, Inferno Berserker (Rare, budget aggro, snowball)
  - BS-003: Cinder, Flame Mage (Uncommon, ranged mage)
  - BS-004: Blaze, Dragon Rider (Legendary, flying, massive AOE)
  - BS-005: Ember, Phoenix Guardian (Epic, support healer, revive)

- **Units** (16): BS-006 to BS-021
  - **Common** (10): Fire Soldier, Ember Scout, Flame Imp, Scorch Elemental, Lava Golem, Ash Warrior, Cinder Beast, Molten Hound, Pyro Sprite, Ember Wolf
  - **Uncommon** (4): Goblin Raider, Phoenix Hatchling, Flame Sentinel, Inferno Guard
  - **Rare** (2): Ember Legionnaire, Fire Dragon Whelp

- **Tactics** (3): BS-022 to BS-024
  - BS-022: Fireball (Rare, single-target burst)
  - BS-023: Flame Shield (Uncommon, damage reduction buff)
  - BS-024: Inferno (Epic, AOE board clear)

- **Buildings** (1): BS-025
  - BS-025: Forge (Uncommon, Fire-themed economy building)

**Validation Checks**:
- [ ] All 25 files created (individual JSON per card)
- [ ] Collection numbers sequential (BS-001 to BS-025)
- [ ] Rarity distribution matches plan (10 Common, 4 Uncommon, 2 Rare, 2 Epic, 1 Legendary)
- [ ] No duplicate cardIds
- [ ] All art assets referenced (even if placeholders)

---

## Phase 4: Water Element Cards (25 Cards)

**Card Breakdown**:
- **Heroes** (5): BS-026 to BS-030
  - BS-026: Thalor, Tide Guardian (Epic, starter hero, defensive tank)
  - BS-027: Marina, Sea Witch (Rare, budget control, freeze)
  - BS-028: Coral, Wave Caller (Uncommon, ranged healer)
  - BS-029: Leviathan, Ocean Tyrant (Legendary, massive HP, tidal AOE)
  - BS-030: Aqua, Storm Sage (Epic, support buffer, mana regen)

- **Units** (16): BS-031 to BS-046
  - **Common** (10): Water Scout, Aqua Healer, Frost Soldier, Sea Sprite, Tidal Warrior, Reef Guardian, Current Elemental, Wave Rider, Nautilus Shell, Coral Construct
  - **Uncommon** (4): Sea Serpent, Water Elemental, Frost Archer, Tidal Knight
  - **Rare** (2): Frost Paladin, Kraken Spawn

- **Tactics** (3): BS-047 to BS-049
  - BS-047: Tidal Wave (Rare, AOE damage + heal)
  - BS-048: Aqua Shield (Uncommon, shield buff)
  - BS-049: Deluge (Epic, mass heal + cleanse)

- **Buildings** (1): BS-050
  - BS-050: Aquarium (Uncommon, Water-themed economy building)

---

## Phase 5: Earth Element Cards (25 Cards)

**Card Breakdown**:
- **Heroes** (5): BS-051 to BS-055
  - BS-051: Gaia, Stone Sentinel (Epic, starter hero, balanced tank)
  - BS-052: Thorne, Root Warden (Rare, budget tank, regen)
  - BS-053: Moss, Grove Keeper (Uncommon, support healer, nature)
  - BS-054: Terra, World Shaper (Legendary, terrain manipulation, massive DEF)
  - BS-055: Clay, Earth Shaman (Epic, support buffer, summon minions)

- **Units** (16): BS-056 to BS-071
  - **Common** (10): Earth Warrior, Boulder Beast, Stone Scout, Root Elemental, Clay Golem, Granite Soldier, Moss Creature, Pebble Spirit, Mud Construct, Vine Familiar
  - **Uncommon** (4): Rock Golem, Stone Guardian, Treant Protector, Earth Drake
  - **Rare** (2): Titan Guard, Ancient Colossus

- **Tactics** (3): BS-072 to BS-074
  - BS-072: Earthquake (Rare, AOE damage, stun)
  - BS-073: Stone Shield (Uncommon, DEF buff)
  - BS-074: Gaia's Blessing (Epic, mass heal + damage reduction)

- **Buildings** (1): BS-075
  - BS-075: Quarry (Uncommon, Earth-themed economy building)

---

## Phase 6: Lightning Element Cards (15 Cards)

**Card Breakdown**:
- **Heroes** (4): BS-076 to BS-079
  - BS-076: Ragnarok, God of Thunder (Legendary, campaign reward, massive burst)
  - BS-077: Volt, Storm Caller (Epic, chain lightning, speed)
  - BS-078: Spark, Lightning Mage (Rare, ranged burst)
  - BS-079: Thunder, Sky Warrior (Uncommon, fast melee)

- **Units** (9): BS-080 to BS-088
  - **Common** (5): Lightning Scout, Volt Sprite, Storm Elemental, Thunder Imp, Spark Familiar
  - **Uncommon** (3): Storm Knight, Voltage Guard, Thunder Drake
  - **Rare** (1): Tempest Titan

- **Tactics** (2): BS-089 to BS-090
  - BS-089: Lightning Bolt (Rare, single-target massive damage)
  - BS-090: Chain Lightning (Epic, multi-target bounce)

---

## Phase 7: Wind Element Cards (15 Cards)

**Card Breakdown**:
- **Heroes** (4): BS-091 to BS-094
  - BS-091: Zephyr, Sky Sovereign (Epic, flying, speed)
  - BS-092: Gale, Wind Rider (Rare, ranged, mobility)
  - BS-093: Breeze, Air Mage (Uncommon, support buffer)
  - BS-094: Tempest, Storm Lord (Legendary, flying, AOE knockback)

- **Units** (9): BS-095 to BS-103
  - **Common** (5): Wind Scout, Air Sprite, Gale Elemental, Breeze Familiar, Cloud Wisp
  - **Uncommon** (3): Sky Knight, Wind Archer, Cyclone Drake
  - **Rare** (1): Hurricane Titan

- **Tactics** (2): BS-104 to BS-105
  - BS-104: Gust (Uncommon, knockback utility)
  - BS-105: Tornado (Epic, AOE displacement)

---

## Phase 8: Frost Element Cards (15 Cards)

**Card Breakdown**:
- **Heroes** (4): BS-106 to BS-109
  - BS-106: Glacius, Ice King (Epic, control, freeze)
  - BS-107: Blizzard, Frost Warden (Rare, tank, slow)
  - BS-108: Icicle, Ice Mage (Uncommon, ranged control)
  - BS-109: Winterfell, Eternal Frost (Legendary, mass freeze, immunity)

- **Units** (9): BS-110 to BS-118
  - **Common** (5): Frost Scout, Ice Sprite, Snow Elemental, Chill Imp, Frozen Familiar
  - **Uncommon** (3): Ice Knight, Frost Archer, Blizzard Drake
  - **Rare** (1): Glacier Titan

- **Tactics** (2): BS-119 to BS-120
  - BS-119: Ice Shard (Rare, damage + slow)
  - BS-120: Blizzard (Epic, AOE freeze)

---

## Phase 9: Neutral Cards (20 Cards)

**Card Breakdown**:
- **Heroes** (8): BS-121 to BS-128
  - **Common** (2): Sentinel, Guardian Recruit
  - **Uncommon** (3): Mercenary Leader, Wandering Knight, Scholar Mage
  - **Rare** (2): Veteran Commander, Arcane Sage
  - **Epic** (1): Malakar, Demon Overlord (Location 40 boss reward, Mythic technically but counted as Epic for balance)

- **Tactics** (6): BS-129 to BS-134
  - BS-129: Heal (Common, basic heal)
  - BS-130: Shield (Common, basic defense buff)
  - BS-131: Charge (Uncommon, movement + damage)
  - BS-132: Inspire (Rare, buff all allies)
  - BS-133: Dispel (Rare, remove buffs/debuffs)
  - BS-134: Resurrection (Legendary, revive dead unit)

- **Buildings** (6): BS-135 to BS-140
  - **Common** (3): Barracks, Farm, Mine
  - **Uncommon** (2): Mage Tower, Temple
  - **Rare** (1): Monument

---

## Phase 10: Product Definitions

### **Starter Boxes** (3 products)
1. `fire-starter-box.json` (15 cards: BS-001 + 14 support)
2. `water-starter-box.json` (15 cards: BS-026 + 14 support)
3. `earth-starter-box.json` (15 cards: BS-051 + 14 support)

### **Booster Packs** (9 products)
1. `welcome-pack.json` (5 cards, hero guarantee, tutorial reward)
2. `standard-pack.json` (5 cards, 1,000 Gold, all Base Set)
3. `element-booster-fire.json` (5 cards, Fire-only)
4. `element-booster-water.json` (5 cards, Water-only)
5. `element-booster-earth.json` (5 cards, Earth-only)
6. `rare-pack.json` (5 cards, guaranteed Rare+)
7. `epic-pack.json` (5 cards, guaranteed Epic+)
8. `hero-pack.json` (5 cards, 2 heroes guaranteed)
9. `legendary-pack.json` (5 cards, guaranteed Legendary)
10. `mythic-pack.json` (5 cards, choice of 3 Mythic heroes)

### **Daily Rewards**
1. `daily-login-rewards.json` (Day 1-7 rewards)

---

## Phase 11: Documentation

1. `docs/codex/README.md` (how to add new cards)
2. `docs/products/README.md` (how to create new packs/boxes)
3. `docs/collection/README.md` (collection tracking strategy)
4. `docs/collection/series-checklist-base-set.json` (140-card checklist)
5. Build script: `scripts/compile-cards.ps1` (merge all JSONs)
6. Validation script: `scripts/validate-codex.ps1` (check for duplicate IDs, missing references)

---

## Phase 12: Validation & Commit

**Final Checks**:
- [ ] All 140 cards created (no gaps in BS-001 to BS-140)
- [ ] All cardIds unique (no duplicates)
- [ ] All product references valid (no orphaned card IDs)
- [ ] Rarity distribution matches plan (56 Common, 42 Uncommon, 25 Rare, 12 Epic, 4 Legendary, 1 Mythic)
- [ ] Art asset references follow convention (Art/Cards/BS-XXX_Name.png)
- [ ] No copyrighted names used

**Commit Message**:
```
Complete Base Set codex + product system (140 cards, Jan 11 2026)

- 140 cards fully defined (stats, abilities, lore, art)
- Modular codex architecture (series/element/card.json)
- 3 starter boxes (Fire, Water, Earth)
- 9 booster packs (Standard, Element Boosters, Rare/Epic/Legendary)
- Daily login rewards system
- Collection tracking infrastructure
- Build + validation scripts

Card Breakdown:
- Fire: 25 cards (BS-001 to BS-025)
- Water: 25 cards (BS-026 to BS-050)
- Earth: 25 cards (BS-051 to BS-075)
- Lightning: 15 cards (BS-076 to BS-090)
- Wind: 15 cards (BS-091 to BS-105)
- Frost: 15 cards (BS-106 to BS-120)
- Neutral: 20 cards (BS-121 to BS-140)

Ready for Unity implementation (CardManager, PackOpener, CollectionTracker).
```

---

## Naming Conventions (Copyright-Safe)

### **World Lore**: "Sovereign Realms" (our unique universe)
- **Geography**: Ashen Citadel (Fire), Coral Depths (Water), Verdant Highlands (Earth), Storm Peaks (Lightning), Sky Isles (Wind), Frozen Wastes (Frost)
- **Factions**: Ember Legion (Fire), Tidal Order (Water), Stone Compact (Earth), Volt Covenant (Lightning), Sky Clans (Wind), Frost Brotherhood (Frost)

### **Hero Names** (Avoid Copyrights):
- ❌ Don't use: Mario, Pikachu, Gandalf, Thor, Elsa, etc.
- ✅ Use: Aria, Thalor, Gaia, Ragnarok (Norse mythology, public domain), Zephyr (Greek mythology), Glacius (Latin root)

### **Unit Names** (Generic Fantasy):
- ✅ Soldier, Scout, Warrior, Knight, Archer, Mage, Elemental, Golem, Drake, Titan
- ✅ Prefixes: Fire, Water, Earth, Lightning, Wind, Frost, Storm, Thunder, etc.

### **Tactic Names** (Common Terms):
- ✅ Fireball, Lightning Bolt, Heal, Shield, Charge, Earthquake (generic spell names, not copyrighted)

---

## Estimated Time: 4-6 Hours Continuous Work

**Phase 1-2**: 30 minutes (infrastructure)  
**Phase 3-9**: 3-4 hours (140 card definitions)  
**Phase 10**: 45 minutes (product definitions)  
**Phase 11**: 30 minutes (documentation)  
**Phase 12**: 15 minutes (validation + commit)

**Total**: 5-6 hours of focused execution without interruption.

---

**Status**: READY TO EXECUTE. Beginning Phase 2...
