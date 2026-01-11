# Base Set Complete Card List (All 140 Cards)

**Purpose**: Master reference for all Base Set cards. Build scripts generate full JSON from this data.

**Format**: CollectionNumber | CardID | Name | Type | Element | Rarity | HP | Mana | ATK | DEF | Move | Range | Notes

---

## Fire Element (BS-001 to BS-025)

### Heroes (5)
| # | ID | Name | Rarity | HP | Mana | ATK | DEF | Move | Range | Key Ability |
|---|---|---|---|---|---|---|---|---|---|---|
| BS-001 | HERO_ARIA_FLAME_KNIGHT | Aria, Flame Knight | Epic | 80 | 60 | 45 | 12 | 3 | 1 | Blazing Strike (70 AOE) |
| BS-002 | HERO_RAGNAR_INFERNO_BERSERKER | Ragnar, Inferno Berserker | Rare | 70 | 50 | 50 | 8 | 4 | 1 | Rage Strike (snowball) |
| BS-003 | HERO_CINDER_FLAME_MAGE | Cinder, Flame Mage | Uncommon | 50 | 80 | 30 | 10 | 2 | 3 | Flame Bolt (ranged) |
| BS-004 | HERO_BLAZE_DRAGON_RIDER | Blaze, Dragon Rider | Legendary | 100 | 70 | 60 | 20 | 5 | 1 | Dragon Breath (100 AOE), Flying |
| BS-005 | HERO_EMBER_PHOENIX_GUARDIAN | Ember, Phoenix Guardian | Epic | 75 | 65 | 40 | 18 | 3 | 1 | Phoenix Rebirth (revive) |

### Units Common (10)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Notes |
|---|---|---|---|---|---|---|---|---|---|
| BS-006 | UNIT_FIRE_SOLDIER | Fire Soldier | 30 | 20 | 20 | 8 | 2 | 1 | Basic melee |
| BS-007 | UNIT_EMBER_SCOUT | Ember Scout | 25 | 15 | 18 | 5 | 3 | 1 | Fast flanker |
| BS-008 | UNIT_FLAME_IMP | Flame Imp | 20 | 25 | 22 | 4 | 2 | 2 | Ranged |
| BS-009 | UNIT_SCORCH_ELEMENTAL | Scorch Elemental | 35 | 30 | 25 | 6 | 2 | 1 | Elemental |
| BS-010 | UNIT_LAVA_GOLEM | Lava Golem | 40 | 15 | 18 | 12 | 1 | 1 | Tank |
| BS-011 | UNIT_ASH_WARRIOR | Ash Warrior | 28 | 20 | 21 | 7 | 2 | 1 | Balanced |
| BS-012 | UNIT_CINDER_BEAST | Cinder Beast | 32 | 18 | 24 | 5 | 3 | 1 | Fast attacker |
| BS-013 | UNIT_MOLTEN_HOUND | Molten Hound | 26 | 22 | 23 | 6 | 3 | 1 | Pack hunter |
| BS-014 | UNIT_PYRO_SPRITE | Pyro Sprite | 22 | 28 | 19 | 4 | 2 | 2 | Ranged support |
| BS-015 | UNIT_EMBER_WOLF | Ember Wolf | 29 | 19 | 22 | 7 | 3 | 1 | Fast melee |

### Units Uncommon (4)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-016 | UNIT_GOBLIN_RAIDER | Goblin Raider | 35 | 25 | 28 | 9 | 3 | 1 | Raid (+dmg vs low HP) |
| BS-017 | UNIT_PHOENIX_HATCHLING | Phoenix Hatchling | 30 | 35 | 26 | 8 | 2 | 1 | Rebirth 25%, Flying |
| BS-018 | UNIT_FLAME_SENTINEL | Flame Sentinel | 45 | 30 | 24 | 14 | 2 | 1 | Guard (allies -20% dmg) |
| BS-019 | UNIT_INFERNO_GUARD | Inferno Guard | 42 | 28 | 26 | 12 | 2 | 1 | Retaliate (15 dmg back) |

### Units Rare (2)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-020 | UNIT_EMBER_LEGIONNAIRE | Ember Legionnaire | 50 | 40 | 35 | 16 | 2 | 1 | Blazing Charge (move 4 + attack) |
| BS-021 | UNIT_FIRE_DRAGON_WHELP | Fire Dragon Whelp | 55 | 45 | 38 | 14 | 3 | 1 | Fire Breath (60 AOE), Flying |

### Tactics (3)
| # | ID | Name | Rarity | Mana Cost | Effect |
|---|---|---|---|---|---|
| BS-022 | TACTIC_FIREBALL | Fireball | Rare | 25 | 50 damage (range 5) |
| BS-023 | TACTIC_FLAME_SHIELD | Flame Shield | Uncommon | 20 | +15 DEF for 3 turns, attackers take 5 dmg |
| BS-024 | TACTIC_INFERNO | Inferno | Epic | 40 | 35 AOE damage + burning ground |

### Buildings (1)
| # | ID | Name | Rarity | HP | DEF | Effect |
|---|---|---|---|---|---|---|
| BS-025 | BUILDING_FORGE | Forge | Uncommon | 60 | 20 | +10% Fire production (Phase 2) |

---

## Water Element (BS-026 to BS-050)

### Heroes (5)
| # | ID | Name | Rarity | HP | Mana | ATK | DEF | Move | Range | Key Ability |
|---|---|---|---|---|---|---|---|---|---|---|
| BS-026 | HERO_THALOR_TIDE_GUARDIAN | Thalor, Tide Guardian | Epic | 100 | 55 | 30 | 28 | 2 | 1 | Tidal Wave (50 dmg + heal) |
| BS-027 | HERO_MARINA_SEA_WITCH | Marina, Sea Witch | Rare | 65 | 70 | 32 | 15 | 2 | 3 | Frost Curse (slow enemy) |
| BS-028 | HERO_CORAL_WAVE_CALLER | Coral, Wave Caller | Uncommon | 55 | 75 | 25 | 18 | 2 | 3 | Wave Surge (ranged), HP regen |
| BS-029 | HERO_LEVIATHAN_OCEAN_TYRANT | Leviathan, Ocean Tyrant | Legendary | 120 | 60 | 55 | 35 | 2 | 1 | Tsunami (80 AOE pushback), -30% dmg taken |
| BS-030 | HERO_AQUA_STORM_SAGE | Aqua, Storm Sage | Epic | 70 | 80 | 35 | 22 | 2 | 2 | Mana Flood (restore 30 mana all allies) |

### Units Common (10)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range |
|---|---|---|---|---|---|---|---|---|
| BS-031 | UNIT_WATER_SCOUT | Water Scout | 28 | 18 | 19 | 9 | 3 | 1 |
| BS-032 | UNIT_AQUA_HEALER | Aqua Healer | 25 | 35 | 15 | 8 | 2 | 2 |
| BS-033 | UNIT_FROST_SOLDIER | Frost Soldier | 32 | 22 | 20 | 10 | 2 | 1 |
| BS-034 | UNIT_SEA_SPRITE | Sea Sprite | 23 | 30 | 18 | 6 | 2 | 2 |
| BS-035 | UNIT_TIDAL_WARRIOR | Tidal Warrior | 31 | 20 | 21 | 11 | 2 | 1 |
| BS-036 | UNIT_REEF_GUARDIAN | Reef Guardian | 36 | 18 | 19 | 13 | 1 | 1 |
| BS-037 | UNIT_CURRENT_ELEMENTAL | Current Elemental | 30 | 28 | 23 | 7 | 2 | 1 |
| BS-038 | UNIT_WAVE_RIDER | Wave Rider | 27 | 24 | 22 | 8 | 3 | 1 |
| BS-039 | UNIT_NAUTILUS_SHELL | Nautilus Shell | 40 | 15 | 16 | 14 | 1 | 1 |
| BS-040 | UNIT_CORAL_CONSTRUCT | Coral Construct | 34 | 20 | 18 | 12 | 1 | 1 |

### Units Uncommon (4)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-041 | UNIT_SEA_SERPENT | Sea Serpent | 38 | 30 | 27 | 10 | 2 | 1 | Constrict (target -1 Move) |
| BS-042 | UNIT_WATER_ELEMENTAL | Water Elemental | 35 | 40 | 25 | 12 | 2 | 2 | Splash (AOE 1) |
| BS-043 | UNIT_FROST_ARCHER | Frost Archer | 32 | 35 | 28 | 9 | 2 | 3 | Freeze Shot (slow) |
| BS-044 | UNIT_TIDAL_KNIGHT | Tidal Knight | 48 | 32 | 26 | 15 | 2 | 1 | Shield Wall (+DEF to allies) |

### Units Rare (2)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-045 | UNIT_FROST_PALADIN | Frost Paladin | 52 | 42 | 34 | 18 | 2 | 1 | Ice Aura (enemies -10% ATK) |
| BS-046 | UNIT_KRAKEN_SPAWN | Kraken Spawn | 58 | 48 | 40 | 16 | 2 | 2 | Tentacle Slam (AOE 2) |

### Tactics (3)
| # | ID | Name | Rarity | Mana Cost | Effect |
|---|---|---|---|---|---|
| BS-047 | TACTIC_TIDAL_WAVE | Tidal Wave | Rare | 28 | 45 AOE damage + 20 heal to caster |
| BS-048 | TACTIC_AQUA_SHIELD | Aqua Shield | Uncommon | 22 | +18 DEF for 3 turns |
| BS-049 | TACTIC_DELUGE | Deluge | Epic | 42 | 30 heal to all allies + cleanse |

### Buildings (1)
| # | ID | Name | Rarity | HP | DEF | Effect |
|---|---|---|---|---|---|---|
| BS-050 | BUILDING_AQUARIUM | Aquarium | Uncommon | 65 | 22 | +10% Water production (Phase 2) |

---

## Earth Element (BS-051 to BS-075)

### Heroes (5)
| # | ID | Name | Rarity | HP | Mana | ATK | DEF | Move | Range | Key Ability |
|---|---|---|---|---|---|---|---|---|---|---|
| BS-051 | HERO_GAIA_STONE_SENTINEL | Gaia, Stone Sentinel | Epic | 90 | 58 | 36 | 20 | 2 | 1 | Earthquake (55 AOE) |
| BS-052 | HERO_THORNE_ROOT_WARDEN | Thorne, Root Warden | Rare | 75 | 55 | 34 | 22 | 2 | 1 | Root Grasp (immobilize), HP regen |
| BS-053 | HERO_MOSS_GROVE_KEEPER | Moss, Grove Keeper | Uncommon | 60 | 70 | 28 | 16 | 2 | 2 | Nature's Heal (heal ally) |
| BS-054 | HERO_TERRA_WORLD_SHAPER | Terra, World Shaper | Legendary | 110 | 65 | 50 | 40 | 2 | 1 | Landslide (90 AOE), terrain manipulation |
| BS-055 | HERO_CLAY_EARTH_SHAMAN | Clay, Earth Shaman | Epic | 78 | 68 | 38 | 24 | 2 | 1 | Summon Golem (spawn minion) |

### Units Common (10)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range |
|---|---|---|---|---|---|---|---|---|
| BS-056 | UNIT_EARTH_WARRIOR | Earth Warrior | 32 | 20 | 21 | 10 | 2 | 1 |
| BS-057 | UNIT_BOULDER_BEAST | Boulder Beast | 35 | 18 | 20 | 12 | 1 | 1 |
| BS-058 | UNIT_STONE_SCOUT | Stone Scout | 29 | 19 | 19 | 9 | 3 | 1 |
| BS-059 | UNIT_ROOT_ELEMENTAL | Root Elemental | 31 | 26 | 22 | 8 | 2 | 1 |
| BS-060 | UNIT_CLAY_GOLEM | Clay Golem | 38 | 16 | 18 | 14 | 1 | 1 |
| BS-061 | UNIT_GRANITE_SOLDIER | Granite Soldier | 33 | 21 | 21 | 11 | 2 | 1 |
| BS-062 | UNIT_MOSS_CREATURE | Moss Creature | 27 | 28 | 20 | 7 | 2 | 1 |
| BS-063 | UNIT_PEBBLE_SPIRIT | Pebble Spirit | 24 | 24 | 19 | 6 | 3 | 1 |
| BS-064 | UNIT_MUD_CONSTRUCT | Mud Construct | 36 | 17 | 17 | 13 | 1 | 1 |
| BS-065 | UNIT_VINE_FAMILIAR | Vine Familiar | 26 | 25 | 20 | 8 | 2 | 2 |

### Units Uncommon (4)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-066 | UNIT_ROCK_GOLEM | Rock Golem | 50 | 28 | 26 | 16 | 1 | 1 | Fortify (+5 DEF when not moving) |
| BS-067 | UNIT_STONE_GUARDIAN | Stone Guardian | 48 | 30 | 25 | 18 | 1 | 1 | Taunt (forces enemy attacks) |
| BS-068 | UNIT_TREANT_PROTECTOR | Treant Protector | 45 | 35 | 24 | 15 | 2 | 1 | Root Shield (allies +DEF) |
| BS-069 | UNIT_EARTH_DRAKE | Earth Drake | 42 | 32 | 29 | 14 | 3 | 1 | Tremor (AOE 1 melee) |

### Units Rare (2)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-070 | UNIT_TITAN_GUARD | Titan Guard | 60 | 40 | 36 | 20 | 1 | 1 | Immovable (cannot be pushed) |
| BS-071 | UNIT_ANCIENT_COLOSSUS | Ancient Colossus | 65 | 45 | 38 | 22 | 1 | 1 | Stoneskin (-40% dmg) |

### Tactics (3)
| # | ID | Name | Rarity | Mana Cost | Effect |
|---|---|---|---|---|---|
| BS-072 | TACTIC_EARTHQUAKE | Earthquake | Rare | 30 | 48 AOE damage + stun 1 turn |
| BS-073 | TACTIC_STONE_SHIELD | Stone Shield | Uncommon | 24 | +20 DEF for 3 turns |
| BS-074 | TACTIC_GAIAS_BLESSING | Gaia's Blessing | Epic | 45 | 35 heal all allies + -20% dmg for 2 turns |

### Buildings (1)
| # | ID | Name | Rarity | HP | DEF | Effect |
|---|---|---|---|---|---|---|
| BS-075 | BUILDING_QUARRY | Quarry | Uncommon | 70 | 24 | +10% Earth production (Phase 2) |

---

## Lightning Element (BS-076 to BS-090)

### Heroes (4)
| # | ID | Name | Rarity | HP | Mana | ATK | DEF | Move | Range | Key Ability |
|---|---|---|---|---|---|---|---|---|---|---|
| BS-076 | HERO_RAGNAROK_GOD_OF_THUNDER | Ragnarok, God of Thunder | Legendary | 95 | 75 | 65 | 18 | 4 | 2 | Mjolnir Strike (120 single target) |
| BS-077 | HERO_VOLT_STORM_CALLER | Volt, Storm Caller | Epic | 72 | 68 | 48 | 14 | 4 | 2 | Chain Lightning (35 × 4 bounces) |
| BS-078 | HERO_SPARK_LIGHTNING_MAGE | Spark, Lightning Mage | Rare | 58 | 80 | 42 | 12 | 3 | 3 | Lightning Bolt (65 damage) |
| BS-079 | HERO_THUNDER_SKY_WARRIOR | Thunder, Sky Warrior | Uncommon | 65 | 50 | 40 | 15 | 4 | 1 | Thunderclap (40 AOE 1) |

### Units Common (5)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range |
|---|---|---|---|---|---|---|---|---|
| BS-080 | UNIT_LIGHTNING_SCOUT | Lightning Scout | 26 | 22 | 24 | 6 | 4 | 1 |
| BS-081 | UNIT_VOLT_SPRITE | Volt Sprite | 22 | 28 | 22 | 5 | 3 | 2 |
| BS-082 | UNIT_STORM_ELEMENTAL | Storm Elemental | 30 | 30 | 28 | 7 | 3 | 1 |
| BS-083 | UNIT_THUNDER_IMP | Thunder Imp | 24 | 26 | 26 | 6 | 3 | 2 |
| BS-084 | UNIT_SPARK_FAMILIAR | Spark Familiar | 25 | 24 | 25 | 6 | 4 | 1 |

### Units Uncommon (3)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-085 | UNIT_STORM_KNIGHT | Storm Knight | 40 | 35 | 36 | 11 | 4 | 1 | Lightning Strike (bonus dmg 1/turn) |
| BS-086 | UNIT_VOLTAGE_GUARD | Voltage Guard | 42 | 32 | 34 | 13 | 3 | 1 | Static Shield (reflect 10 dmg) |
| BS-087 | UNIT_THUNDER_DRAKE | Thunder Drake | 38 | 38 | 38 | 10 | 4 | 1 | Shock (stun 1 turn), Flying |

### Units Rare (1)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-088 | UNIT_TEMPEST_TITAN | Tempest Titan | 56 | 50 | 50 | 15 | 3 | 2 | Storm Fury (AOE 2, chain 3) |

### Tactics (2)
| # | ID | Name | Rarity | Mana Cost | Effect |
|---|---|---|---|---|---|
| BS-089 | TACTIC_LIGHTNING_BOLT | Lightning Bolt | Rare | 32 | 70 single-target damage (instant) |
| BS-090 | TACTIC_CHAIN_LIGHTNING | Chain Lightning | Epic | 40 | 40 damage, chains to 4 enemies |

---

## Wind Element (BS-091 to BS-105)

### Heroes (4)
| # | ID | Name | Rarity | HP | Mana | ATK | DEF | Move | Range | Key Ability |
|---|---|---|---|---|---|---|---|---|---|---|
| BS-091 | HERO_ZEPHYR_SKY_SOVEREIGN | Zephyr, Sky Sovereign | Epic | 75 | 65 | 44 | 16 | 5 | 1 | Cyclone (50 AOE knockback), Flying |
| BS-092 | HERO_GALE_WIND_RIDER | Gale, Wind Rider | Rare | 62 | 60 | 38 | 14 | 5 | 3 | Gale Force (push 3 tiles) |
| BS-093 | HERO_BREEZE_AIR_MAGE | Breeze, Air Mage | Uncommon | 56 | 72 | 32 | 12 | 4 | 3 | Air Slash (ranged), +2 Move to ally |
| BS-094 | HERO_TEMPEST_STORM_LORD | Tempest, Storm Lord | Legendary | 85 | 70 | 58 | 20 | 5 | 2 | Hurricane (75 AOE, displace all), Flying |

### Units Common (5)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range |
|---|---|---|---|---|---|---|---|---|
| BS-095 | UNIT_WIND_SCOUT | Wind Scout | 24 | 20 | 22 | 5 | 5 | 1 |
| BS-096 | UNIT_AIR_SPRITE | Air Sprite | 21 | 26 | 20 | 4 | 4 | 2 |
| BS-097 | UNIT_GALE_ELEMENTAL | Gale Elemental | 28 | 28 | 26 | 6 | 4 | 1 |
| BS-098 | UNIT_BREEZE_FAMILIAR | Breeze Familiar | 23 | 24 | 23 | 5 | 5 | 2 |
| BS-099 | UNIT_CLOUD_WISP | Cloud Wisp | 22 | 30 | 21 | 4 | 4 | 2 |

### Units Uncommon (3)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-100 | UNIT_SKY_KNIGHT | Sky Knight | 38 | 32 | 34 | 10 | 5 | 1 | Aerial Assault (+dmg from move), Flying |
| BS-101 | UNIT_WIND_ARCHER | Wind Archer | 32 | 36 | 32 | 9 | 4 | 4 | Piercing Shot (ignore 30% DEF) |
| BS-102 | UNIT_CYCLONE_DRAKE | Cyclone Drake | 36 | 36 | 36 | 11 | 5 | 1 | Whirlwind (AOE 1), Flying |

### Units Rare (1)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-103 | UNIT_HURRICANE_TITAN | Hurricane Titan | 52 | 48 | 46 | 14 | 4 | 2 | Tornado (AOE 3 knockback) |

### Tactics (2)
| # | ID | Name | Rarity | Mana Cost | Effect |
|---|---|---|---|---|---|
| BS-104 | TACTIC_GUST | Gust | Uncommon | 18 | Push target 2 tiles, 20 damage |
| BS-105 | TACTIC_TORNADO | Tornado | Epic | 38 | 38 AOE damage + displace 2 tiles |

---

## Frost Element (BS-106 to BS-120)

### Heroes (4)
| # | ID | Name | Rarity | HP | Mana | ATK | DEF | Move | Range | Key Ability |
|---|---|---|---|---|---|---|---|---|---|---|
| BS-106 | HERO_GLACIUS_ICE_KING | Glacius, Ice King | Epic | 88 | 62 | 40 | 26 | 2 | 2 | Glacial Prison (freeze 3 enemies) |
| BS-107 | HERO_BLIZZARD_FROST_WARDEN | Blizzard, Frost Warden | Rare | 82 | 58 | 36 | 24 | 2 | 1 | Frost Armor (+30% DEF) |
| BS-108 | HERO_ICICLE_ICE_MAGE | Icicle, Ice Mage | Uncommon | 60 | 76 | 34 | 18 | 2 | 3 | Ice Shard (40 dmg + slow) |
| BS-109 | HERO_WINTERFELL_ETERNAL_FROST | Winterfell, Eternal Frost | Legendary | 105 | 68 | 52 | 32 | 2 | 2 | Absolute Zero (freeze all, immune to freeze) |

### Units Common (5)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range |
|---|---|---|---|---|---|---|---|---|
| BS-110 | UNIT_FROST_SCOUT | Frost Scout | 28 | 20 | 20 | 9 | 3 | 1 |
| BS-111 | UNIT_ICE_SPRITE | Ice Sprite | 24 | 28 | 19 | 7 | 2 | 2 |
| BS-112 | UNIT_SNOW_ELEMENTAL | Snow Elemental | 32 | 26 | 22 | 10 | 2 | 1 |
| BS-113 | UNIT_CHILL_IMP | Chill Imp | 23 | 30 | 21 | 6 | 2 | 2 |
| BS-114 | UNIT_FROZEN_FAMILIAR | Frozen Familiar | 26 | 24 | 20 | 8 | 3 | 1 |

### Units Uncommon (3)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-115 | UNIT_ICE_KNIGHT | Ice Knight | 46 | 32 | 30 | 16 | 2 | 1 | Frost Aura (enemies -1 Move) |
| BS-116 | UNIT_FROST_ARCHER | Frost Archer | 34 | 36 | 32 | 11 | 2 | 4 | Freeze Arrow (slow target) |
| BS-117 | UNIT_BLIZZARD_DRAKE | Blizzard Drake | 40 | 38 | 34 | 14 | 3 | 1 | Ice Breath (30 AOE slow), Flying |

### Units Rare (1)
| # | ID | Name | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|
| BS-118 | UNIT_GLACIER_TITAN | Glacier Titan | 64 | 46 | 42 | 20 | 1 | 1 | Permafrost (immune to slow, freeze) |

### Tactics (2)
| # | ID | Name | Rarity | Mana Cost | Effect |
|---|---|---|---|---|---|
| BS-119 | TACTIC_ICE_SHARD | Ice Shard | Rare | 28 | 52 damage + slow (−1 Move for 2 turns) |
| BS-120 | TACTIC_BLIZZARD | Blizzard | Epic | 42 | 35 AOE damage + freeze 1 turn |

---

## Neutral Element (BS-121 to BS-140)

### Heroes (8)
| # | ID | Name | Rarity | HP | Mana | ATK | DEF | Move | Range | Key Ability |
|---|---|---|---|---|---|---|---|---|---|---|
| BS-121 | HERO_SENTINEL_GUARDIAN_PRIME | Sentinel, Guardian Prime | Common | 45 | 30 | 25 | 15 | 2 | 1 | Shield Bash (30 dmg + stun) |
| BS-122 | HERO_WARDEN_RECRUIT | Warden, Recruit | Common | 42 | 28 | 24 | 14 | 3 | 1 | Rally (allies +2 ATK) |
| BS-123 | HERO_MERCENARY_CAPTAIN | Mercenary Captain | Uncommon | 68 | 45 | 38 | 18 | 3 | 1 | Inspire (+10% all stats to allies) |
| BS-124 | HERO_KNIGHT_WANDERER | Knight Wanderer | Uncommon | 72 | 42 | 36 | 20 | 3 | 1 | Defend (redirect damage to self) |
| BS-125 | HERO_SCHOLAR_SAGE | Scholar Sage | Uncommon | 55 | 85 | 30 | 16 | 2 | 3 | Arcane Bolt (40 dmg, restore 15 mana) |
| BS-126 | HERO_VETERAN_COMMANDER | Veteran Commander | Rare | 80 | 55 | 42 | 22 | 2 | 1 | Battle Tactics (allies +3 Move for 1 turn) |
| BS-127 | HERO_ARCANE_SAGE | Arcane Sage | Rare | 62 | 90 | 38 | 18 | 2 | 3 | Spell Mastery (−20% mana costs) |
| BS-128 | HERO_MALAKAR_DEMON_OVERLORD | Malakar, Demon Overlord | Epic | 150 | 90 | 75 | 30 | 3 | 2 | Hellfire Nova (90 AOE + heal), Phase 2 summons |

### Tactics (6)
| # | ID | Name | Rarity | Mana Cost | Effect |
|---|---|---|---|---|---|
| BS-129 | TACTIC_HEAL | Heal | Common | 18 | Restore 35 HP to target ally |
| BS-130 | TACTIC_SHIELD | Shield | Common | 16 | +12 DEF to target for 3 turns |
| BS-131 | TACTIC_CHARGE | Charge | Uncommon | 20 | +2 Move and +10 ATK for 1 turn |
| BS-132 | TACTIC_INSPIRE | Inspire | Rare | 35 | All allies +15% ATK and +15% DEF for 2 turns |
| BS-133 | TACTIC_DISPEL | Dispel | Rare | 28 | Remove all buffs from enemies, debuffs from allies |
| BS-134 | TACTIC_RESURRECTION | Resurrection | Legendary | 60 | Revive dead ally at 50% HP (once per battle) |

### Buildings (6)
| # | ID | Name | Rarity | HP | DEF | Effect |
|---|---|---|---|---|---|---|
| BS-135 | BUILDING_BARRACKS | Barracks | Common | 50 | 18 | +10% unit training speed (Phase 2) |
| BS-136 | BUILDING_FARM | Farm | Common | 45 | 15 | +5 Gold/hour (Phase 2) |
| BS-137 | BUILDING_MINE | Mine | Common | 48 | 20 | +3 Gold/hour (Phase 2) |
| BS-138 | BUILDING_MAGE_TOWER | Mage Tower | Uncommon | 55 | 22 | +15% mana regeneration (Phase 2) |
| BS-139 | BUILDING_TEMPLE | Temple | Uncommon | 60 | 24 | +10% HP regeneration (Phase 2) |
| BS-140 | BUILDING_MONUMENT | Monument | Rare | 70 | 28 | +20% XP gain (Phase 2) |

---

## Summary

**Total Cards**: 140
- **Fire**: 25 (5 heroes, 16 units, 3 tactics, 1 building)
- **Water**: 25 (5 heroes, 16 units, 3 tactics, 1 building)
- **Earth**: 25 (5 heroes, 16 units, 3 tactics, 1 building)
- **Lightning**: 15 (4 heroes, 9 units, 2 tactics)
- **Wind**: 15 (4 heroes, 9 units, 2 tactics)
- **Frost**: 15 (4 heroes, 9 units, 2 tactics)
- **Neutral**: 20 (8 heroes, 6 tactics, 6 buildings)

**By Rarity**:
- Common: 56 cards (40%)
- Uncommon: 42 cards (30%)
- Rare: 25 cards (18%)
- Epic: 12 cards (9%)
- Legendary: 4 cards (3%)
- Mythic: 1 card (<1%) - Malakar (technically Epic rarity points but thematic Mythic)

**Total Rarity Points**: 
- Common/Uncommon (98 cards × 1pt) = 98
- Rare (25 cards × 4pt) = 100
- Epic (12 cards × 8pt) = 96
- Legendary (4 cards × 16pt) = 64
- **Total**: 358 rarity points across 140 cards

**Build Script**: Run `scripts/generate-full-codex.ps1` to create individual JSON files from this master list.
