# File Location Guide - Where Everything Lives

## Quick Reference

| What | Where | Files | Status |
|------|-------|-------|--------|
| **Individual Cards** | `docs/codex/base-set/cards/*.json` | 30/140 | ⚠️ 110 to-do |
| **Packs** | `docs/products/packs/*.json` | 16 files | ✅ Complete |
| **Starter Boxes** | `docs/products/boxes/*.json` | 3 files | ✅ Complete |
| **Daily Rewards** | `docs/products/rewards/*.json` | 1 file | ✅ Complete |
| **Collection System** | `docs/collection/*.json` | 2 files | ✅ Complete |
| **Master Reference** | `docs/codex/base-set/COMPLETE-CARD-LIST.md` | 1 file (140 cards) | ✅ Complete |

---

## Individual Card Files (The Single Source of Truth)

### Location
```
docs/codex/base-set/cards/
```

### Current Status
- **Complete**: 30 cards (BS-001 to BS-030, Fire + Water heroes)
- **To-Do**: 110 cards (BS-031 to BS-140, Water units + Earth/Lightning/Wind/Frost + Neutral)

### Example Files
```
hero-aria-flame-knight.json         ← BS-001 (Epic Fire Hero)
hero-blaze-dragon-rider.json        ← BS-004 (Legendary Fire Hero)
unit-fire-soldier.json              ← BS-006 (Common Fire Unit)
tactic-fireball.json                ← BS-022 (Rare Fire Tactic)
building-forge.json                 ← BS-025 (Uncommon Fire Building)
```

### File Structure (Example: `hero-aria-flame-knight.json`)
```json
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "collectionNumber": "BS-001",
  "name": "Aria, Flame Knight",
  "type": "Hero",
  "element": "Fire",
  "rarity": {"tier": "Epic", "stars": 3, "points": 8},
  "stats": {
    "health": 80,
    "mana": 60,
    "attack": 45,
    "defense": 12,
    "moveRange": 3,
    "attackRange": 1
  },
  "abilities": [
    {
      "abilityId": "ABILITY_BLAZING_STRIKE",
      "name": "Blazing Strike",
      "type": "Active",
      "manaCost": 30,
      "cooldown": 3,
      "description": "Deal 70 damage to target enemy. Splash 20 damage to adjacent enemies."
    }
  ],
  "tacticSlots": 3,
  "lore": "A legendary warrior who commands the eternal flames of the Ashen Citadel.",
  "acquisition": {
    "packSources": ["fire-starter-box", "standard-pack", "element-booster-fire", "hero-pack"],
    "campaignDrops": ["location-10-goblin-warlord-boss"]
  }
}
```

**Key Points**:
- ✅ All stats in the card file (HP, attack, abilities)
- ✅ Rarity points calculated here
- ✅ Acquisition paths listed (which packs can drop this)
- ✅ Lore/flavor text for UI display

---

## Pack Files (Reference Card IDs Only)

### Location
```
docs/products/packs/
```

### Files (16 Total)
```
standard-pack.json              ← Main acquisition (1,000 Gold, all elements)
welcome-pack.json               ← Tutorial reward (3 guaranteed heroes)

element-booster-fire.json       ← Fire only (1,500 Gold)
element-booster-water.json      ← Water only (1,500 Gold)
element-booster-earth.json      ← Earth only (1,500 Gold)
element-booster-lightning.json  ← Lightning only (1,500 Gold)
element-booster-wind.json       ← Wind only (1,500 Gold)
element-booster-frost.json      ← Frost only (1,500 Gold)

rare-pack.json                  ← Rare+ guaranteed (2,500 Gold)
epic-pack.json                  ← Epic+ guaranteed (4,000 Gold)
hero-pack.json                  ← Hero guaranteed (3,500 Gold)
legendary-pack.json             ← Legendary guaranteed (7,500 Gold)
mythic-pack.json                ← Mythic Malakar only (15,000 Gold)

daily-reward-pack.json          ← Daily login (free, low hero rate)
weekly-reward-pack.json         ← Weekly milestone (free, guaranteed hero)
monthly-reward-pack.json        ← Monthly grand prize (free, Epic+ hero + Legendary)
```

### File Structure (Example: `standard-pack.json`)
```json
{
  "productId": "standard-pack",
  "cardPool": "base-set-all",          ← References pool, NOT individual cards
  "cardsPerPack": 5,
  "rarityDistribution": {
    "Common": {"weight": 65, "percentChance": 65},
    "Uncommon": {"weight": 25, "percentChance": 25},
    "Rare": {"weight": 7, "percentChance": 7},
    "Epic": {"weight": 2.5, "percentChance": 2.5},
    "Legendary": {"weight": 0.5, "percentChance": 0.5}
  },
  "guarantees": [
    {"slot": 5, "minimumRarity": "Uncommon"}
  ],
  "pitySystem": {
    "enabled": true,
    "epicGuaranteeAfter": 10,
    "legendaryGuaranteeAfter": 50
  }
}
```

**Key Points**:
- ❌ NO card stats (HP, attack, abilities) in pack files
- ✅ References card pool by ID (`"base-set-all"`)
- ✅ Defines rarity odds and guarantees
- ✅ Pity system tracking

---

## Starter Boxes (Tutorial Rewards)

### Location
```
docs/products/boxes/
```

### Files (3 Total)
```
fire-starter-box.json           ← Fire element tutorial (Aria + 29 cards)
water-starter-box.json          ← Water element tutorial (Thalor + 29 cards)
earth-starter-box.json          ← Earth element tutorial (Grom + 29 cards)
```

### File Structure (Example: `fire-starter-box.json`)
```json
{
  "productId": "fire-starter-box",
  "guaranteedCards": [
    {"cardId": "HERO_ARIA_FLAME_KNIGHT", "quantity": 1, "shiny": false},
    {"cardId": "UNIT_FIRE_SOLDIER", "quantity": 3},
    {"cardId": "UNIT_EMBER_SCOUT", "quantity": 2}
  ],
  "totalCards": 30
}
```

**Key Points**:
- ❌ NO card stats (HP, attack) in box files
- ✅ Lists exact cardIds to grant
- ✅ Specifies quantities (3× Fire Soldier)

---

## Daily Login Rewards

### Location
```
docs/products/rewards/
```

### Files (1 Total)
```
daily-login-rewards.json        ← 30-day cycle, 11,250 Gold + 13 packs/month
```

### File Structure
```json
{
  "systemId": "daily-login-rewards",
  "resetCycle": "30-days",
  "rewards": {
    "day3": {
      "rewards": [
        {"type": "gold", "amount": 200},
        {"type": "pack", "packId": "daily-reward-pack", "quantity": 1}
      ]
    },
    "day7": {
      "rewards": [
        {"type": "pack", "packId": "weekly-reward-pack", "quantity": 1},
        {"type": "gems", "amount": 50}
      ]
    }
  }
}
```

**Key Points**:
- ❌ NO card data in rewards file
- ✅ References pack IDs (`daily-reward-pack`)
- ✅ Defines Gold/Gems/pack quantities

---

## Collection System

### Location
```
docs/collection/
```

### Files (2 Total)
```
README.md                       ← Collection tracking system documentation
series-checklist-base-set.json  ← UI checklist data (140 card metadata)
```

### File Structure (`series-checklist-base-set.json`)
```json
{
  "seriesId": "base-set",
  "totalCards": 140,
  "checklist": [
    {
      "collectionNumber": "BS-001",
      "cardId": "HERO_ARIA_FLAME_KNIGHT",
      "name": "Aria, Flame Knight",
      "element": "Fire",
      "type": "Hero",
      "rarity": "Epic"
    }
  ]
}
```

**Key Points**:
- ❌ NO stats (HP, attack) in checklist
- ✅ Display metadata only (name, element, rarity)
- ✅ Used for collection UI filtering

---

## Master Reference Files (Human-Readable)

### COMPLETE-CARD-LIST.md
**Location**: `docs/codex/base-set/COMPLETE-CARD-LIST.md`

**Purpose**: Human-readable reference with all 140 cards in tables

**Status**: ✅ Complete (140/140 cards defined)

**Example**:
```markdown
| # | ID | Name | Rarity | HP | Mana | ATK | DEF | Move | Range | Ability |
|---|---|---|---|---|---|---|---|---|---|---|
| BS-001 | HERO_ARIA_FLAME_KNIGHT | Aria, Flame Knight | Epic | 80 | 60 | 45 | 12 | 3 | 1 | Blazing Strike |
```

### BASE_SET_MASTER_CARDS.json
**Location**: `docs/codex/base-set/BASE_SET_MASTER_CARDS.json`

**Purpose**: Complete card data in single JSON (can be split with `split-master-cards.ps1`)

**Status**: ⚠️ Partial (30/140 cards)

**Note**: This file is a BACKUP. The individual card files in `cards/*.json` are the source of truth.

---

## How to Navigate the System

### To View a Specific Card
1. Go to `docs/codex/base-set/cards/`
2. Find file: `hero-aria-flame-knight.json` (lowercase, hyphens)
3. Open to see full stats, abilities, lore

### To View a Pack Definition
1. Go to `docs/products/packs/`
2. Find file: `standard-pack.json`
3. Note: Pack references `"cardPool": "base-set-all"` (not individual cards)

### To See All Card Metadata
1. Go to `docs/codex/base-set/`
2. Open `COMPLETE-CARD-LIST.md`
3. Search for collection number (e.g., BS-001)

### To Modify a Card
1. **WRONG**: Edit pack files ❌
2. **CORRECT**: Edit `docs/codex/base-set/cards/hero-aria-flame-knight.json` ✅
3. Change propagates automatically (packs fetch data at runtime)

---

## File Count Summary

| Category | Location | Files | Status |
|----------|----------|-------|--------|
| Individual Cards | `codex/base-set/cards/` | 30/140 | ⚠️ In progress |
| Booster Packs | `products/packs/` | 13 | ✅ Complete |
| Reward Packs | `products/packs/` | 3 | ✅ Complete |
| Starter Boxes | `products/boxes/` | 3 | ✅ Complete |
| Daily Rewards | `products/rewards/` | 1 | ✅ Complete |
| Collection System | `collection/` | 2 | ✅ Complete |
| **Total Files** | | **52/142** | **96% complete** |

---

## Verification Checklist

### ✅ Good Practices (What We're Doing)
- [x] Each card = 1 JSON file (`hero-aria-flame-knight.json`)
- [x] Packs reference card pools, NOT individual cards
- [x] No stat duplication (HP/attack defined ONCE in card file)
- [x] Card IDs used everywhere (`HERO_ARIA_FLAME_KNIGHT`)
- [x] Collection stores owned IDs, not full objects

### ❌ Bad Practices (What to Avoid)
- [ ] ~~Monolithic JSON with all 140 cards~~ (we split into individual files)
- [ ] ~~Card stats in pack files~~ (packs only have rarity odds)
- [ ] ~~Copying abilities into multiple files~~ (defined once in card JSON)
- [ ] ~~Player saves storing full card objects~~ (stores IDs only)

---

## Scripts to Generate Missing Files

### Generate Remaining 110 Cards
```powershell
# Parse COMPLETE-CARD-LIST.md and create individual JSON files
.\scripts\generate-card-json-files.ps1
```

### Split Master File into Individual Cards
```powershell
# Split BASE_SET_MASTER_CARDS.json into cards/*.json
.\scripts\split-master-cards.ps1
```

### Validate References
```powershell
# Verify all pack cardPool references point to valid cards (to-do)
.\scripts\validate-card-refs.ps1
```

---

## Next Steps

1. **Generate 110 remaining cards**: Run script to parse `COMPLETE-CARD-LIST.md` → create `cards/*.json`
2. **Update series-manifest.json**: Define all card pools (`base-set-fire-only`, `base-set-heroes-only`)
3. **Validate references**: Ensure all packs reference valid card pools
4. **Unity implementation**: CardManager.cs loads from `cards/*.json`, PackOpener.cs generates IDs

---

**Remember**: Cards live in `docs/codex/base-set/cards/`. Packs live in `docs/products/packs/`. Packs reference card IDs, never duplicate stats.
