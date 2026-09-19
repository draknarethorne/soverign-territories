# Codex Ideation — Lookup Vocabularies

> **Status:** Ideation reference — the working vocabularies used while designing the codex.
> These are the canonical value pools that feed card fields. They map to
> [`../../../data/schemas/codex-schema.json`](../../../data/schemas/codex-schema.json) as noted
> below and are **extensible** (new values can be added as fresh card ideas emerge).

## Field mapping

| Lookup column | Card field | Schema note |
| --- | --- | --- |
| Element | `element` | Enum in codex-schema (10 elements + Neutral) |
| Class | `class` | Free string (documented pool below) |
| Troop Archetype | `archetype` | Free string (documented pool below) |
| Race | `race` | Free string (documented pool below) |
| Rarity Tier | `rarity.tier` | Enum in codex-schema |
| Card Series | `series.seriesName` | Set/expansion name |
| Creature Type | `creatureType` / `companion` | Free string; broad or specific species |

---

## Elements (10 + Neutral)

Darkness · Fire · Grass · Ice · Water · Light · Earth · Lightning · Wind · Poison ·
**Neutral** (element-agnostic cards)

## Rarity tiers (0–7)

| # | Tier | Rarity points | Role |
| ---: | --- | ---: | --- |
| 7 | Transcendent | 64 | Apex chase — the Drakn heroines |
| 6 | Mythic | 32 | Marquee heroes, Elder Dragons |
| 5 | Legendary | 16 | Chase cards |
| 4 | Epic | 8 | Strong heroes/units |
| 3 | Rare | 4 | Specialist units |
| 2 | Uncommon | 2 | Core units |
| 1 | Common | 1 | Bulk troops |
| 0 | Basic | 0 | Foundation/token tier (e.g., spawned minions; no budget cost) |

## Card series (base + expansion name pool)

- **Base Series** — the launch set (ST-### numbering; see the base-set decision in
  [`ideation_codex.md`](ideation_codex.md)).
- Expansion name pool: **Sovereign Dawn** · **Nether Realm** · **Primal Wilds** ·
  **Celestial Gate** · **Awakening** · **Shadow Sovereign**.

## Classes

| | | | |
| --- | --- | --- | --- |
| Alchemist | Assassin | Bard | Beast |
| Beast Lord | Berserker | Cleric | Dragon |
| Druid | Elder Dragon | Enchanter | Knight |
| Magician | Marksman | Monk | Necromancer |
| Paladin | Ranger | Rogue | Shadow Knight |
| Shaman | Summoner | Warrior | Wizard |

## Troop archetypes

| | | |
| --- | --- | --- |
| Aerial / Flying | Assassin / Burst DPS | Caster / Magic |
| Control / Disruptor | Defense / Tank | Melee / Striker |
| Ranged / Artillery | Siege / Heavy | Specialist / Hybrid |
| Summoner / Spawner | Support / Healer | Swarm / Skirmisher |

## Races

| | | |
| --- | --- | --- |
| Barbarian | Beastkin | Celestial |
| Construct | Dark Elf | Demon |
| Dragon | Dwarf | High Elf |
| Human | Orc | Undead |
| Wood Elf | Beast | n/a |

## Creature types / species

> Broad taxonomy values (Humanoid, Dragon, Beast, Elemental, Undead, Construct, Spirit) sit
> alongside specific species used for creature cards and bonded companions.

| | | | |
| --- | --- | --- | --- |
| Angel | Basilisk | Big Cat | Boar |
| Cave Bat | Dire Bear | Dire Wolf | Dragon |
| Elemental | Fairy | Falcon | Forest Spider |
| Frost Owl | Giant Eagle | Goblin | Golem |
| Griffon | Gryphon | Humanoid | Phoenix |
| Pixie | Puma | Reaper | Serpent |
| Shadow Panther | Shark | Skeleton | Spectre |
| Succubus | Treant | War Hound | Wild Boar |
| Wolf | n/a | | |
