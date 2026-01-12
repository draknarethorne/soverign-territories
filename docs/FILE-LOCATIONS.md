# 📍 File Locations Guide - Sovereign Territories

> **Quick Navigation**: Where to find cards, packs, schemas, and all game data

---

## 🗂️ Quick Reference Table

| What | Where | Count | Status |
|------|-------|-------|--------|
| **🎴 Individual Cards** | [`data/cards/base-set/`](../data/cards/base-set/) | 30/140 | 🟡 21% |
| **📦 Packs** | [`data/products/packs/`](../data/products/packs/) | 16 | ✅ Complete |
| **📦 Starter Boxes** | [`data/products/boxes/`](../data/products/boxes/) | 3 | ✅ Complete |
| **🎁 Rewards** | [`data/products/rewards/`](../data/products/rewards/) | 1 | ✅ Complete |
| **📐 Schemas** | [`data/schemas/`](../data/schemas/) | 33 | ✅ Complete |
| **📋 Manifests** | [`data/manifests/`](../data/manifests/) | 2 | ✅ Complete |
| **🗂️ Collection** | [`data/collection/`](../data/collection/) | 1 | ✅ Complete |
| **🃏 Starter Decks** | [`data/decks/starter/`](../data/decks/starter/) | 1 | ✅ Complete |
| **📚 Card Reference** | [`docs/codex/base-set/COMPLETE-CARD-LIST.md`](codex/base-set/COMPLETE-CARD-LIST.md) | 140 | ✅ Complete |

---

## 🎴 Individual Card Files (Single Source of Truth)

### 📂 Location: `data/cards/base-set/`

Cards are organized by type in subdirectories:

```
data/cards/base-set/
├── heroes/              # Hero cards (10/25 complete)
│   ├── hero-aria-flame-knight.json             (BS-001, Epic Fire)
│   ├── hero-ragnar-inferno-berserker.json      (BS-002, Rare Fire)
│   ├── hero-cinder-flame-mage.json             (BS-003, Uncommon Fire)
│   ├── hero-blaze-dragon-rider.json            (BS-004, Legendary Fire)
│   ├── hero-ember-phoenix-guardian.json        (BS-005, Epic Fire)
│   ├── hero-thalor-tide-guardian.json          (BS-026, Epic Water)
│   ├── hero-marina-sea-witch.json              (BS-027, Rare Water)
│   ├── hero-coral-wave-caller.json             (BS-028, Uncommon Water)
│   ├── hero-leviathan-ocean-tyrant.json        (BS-029, Legendary Water)
│   └── hero-aqua-storm-sage.json               (BS-030, Epic Water)
│
├── units/               # Unit cards (16/90 complete)
│   ├── unit-fire-soldier.json                  (BS-006, Common Fire)
│   ├── unit-ember-scout.json                   (BS-007, Common Fire)
│   ├── unit-ash-warrior.json                   (BS-008, Common Fire)
│   ├── unit-pyro-sprite.json                   (BS-009, Common Fire)
│   ├── unit-molten-hound.json                  (BS-010, Common Fire)
│   ├── unit-flame-imp.json                     (BS-011, Common Fire)
│   ├── unit-cinder-beast.json                  (BS-012, Common Fire)
│   ├── unit-scorch-elemental.json              (BS-013, Common Fire)
│   ├── unit-goblin-raider.json                 (BS-014, Uncommon Fire)
│   ├── unit-ember-wolf.json                    (BS-015, Uncommon Fire)
│   ├── unit-flame-sentinel.json                (BS-016, Uncommon Fire)
│   ├── unit-phoenix-hatchling.json             (BS-017, Uncommon Fire)
│   ├── unit-lava-golem.json                    (BS-018, Uncommon Fire)
│   ├── unit-inferno-guard.json                 (BS-019, Uncommon Fire)
│   ├── unit-ember-legionnaire.json             (BS-020, Rare Fire)
│   └── unit-fire-dragon-whelp.json             (BS-021, Rare Fire)
│
├── tactics/             # Tactic (spell) cards (3/20 complete)
│   ├── tactic-fireball.json                    (BS-022, Rare Fire)
│   ├── tactic-flame-shield.json                (BS-023, Uncommon Fire)
│   └── tactic-inferno.json                     (BS-024, Epic Fire)
│
└── buildings/           # Building (economy) cards (1/5 complete)
    └── building-forge.json                     (BS-025, Uncommon Fire)
```

### ✅ Complete Card Example

**File**: [`data/cards/base-set/heroes/hero-aria-flame-knight.json`](../data/cards/base-set/heroes/hero-aria-flame-knight.json)

```json
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "collectionNumber": "BS-001",
  "name": "Aria, Flame Knight",
  "type": "Hero",
  "element": "Fire",
  "rarity": {
    "tier": "Epic",
    "stars": 3,
    "points": 8
  },
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

**Key Principles**:
- ✅ **All stats in card file** (HP, attack, abilities defined ONCE)
- ✅ **Rarity points** calculated from tier (Epic = 8 points)
- ✅ **Acquisition paths** listed (which packs drop this card)
- ✅ **Lore text** for UI display

---

## 📦 Pack Files (Reference Pools, Not Individual Cards)

### 📂 Location: `data/products/packs/`

**16 Pack Files** (all complete):

```
data/products/packs/
├── standard-pack.json                 # Universal pack (1,000 Gold, all elements)
├── welcome-pack.json                  # Tutorial reward (3 guaranteed heroes)
│
├── element-booster-fire.json          # Fire-only (1,500 Gold)
├── element-booster-water.json         # Water-only (1,500 Gold)
├── element-booster-earth.json         # Earth-only (1,500 Gold)
├── element-booster-lightning.json     # Lightning-only (1,500 Gold)
├── element-booster-wind.json          # Wind-only (1,500 Gold)
├── element-booster-frost.json         # Frost-only (1,500 Gold)
│
├── rare-pack.json                     # Rare+ guaranteed (2,500 Gold)
├── epic-pack.json                     # Epic+ guaranteed (4,000 Gold)
├── legendary-pack.json                # Legendary guaranteed (7,500 Gold)
├── hero-pack.json                     # Hero-focused (3,500 Gold)
├── mythic-pack.json                   # Malakar milestone (20,000 Gold)
│
├── daily-reward-pack.json             # Free daily login (hero control)
├── weekly-reward-pack.json            # Free weekly login (guaranteed hero)
└── monthly-reward-pack.json           # Free monthly login (Epic+ hero)
```

### ✅ Pack Structure Example

**File**: [`data/products/packs/standard-pack.json`](../data/products/packs/standard-pack.json)

```json
{
  "productId": "standard-pack",
  "productName": "Standard Pack",
  "price": {"gold": 1000},
  "cardsPerPack": 5,
  "cardPool": "base-set-all",  // ← References pool, NOT individual cards
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
    "epicPity": 10,
    "legendaryPity": 50
  }
}
```

**Key Principles**:
- ✅ **No card stats** in pack file (only references `"cardPool": "base-set-all"`)
- ✅ **Rarity distribution** for randomization
- ✅ **Pity system** for bad-luck protection

---

## 🎁 Reward Systems

### 📂 Location: `data/products/rewards/`

**File**: [`data/products/rewards/daily-login-rewards.json`](../data/products/rewards/daily-login-rewards.json)

30-day login cycle with progressive rewards:
- **Gold**: 11,250 total/month
- **Gems**: 895 total/month
- **Packs**: 13/month (8 daily + 4 weekly + 1 monthly)
- **Guaranteed Heroes**: 5/month (controlled hero saturation)

---

## 📐 JSON Schemas (Validation Rules)

### 📂 Location: `data/schemas/`

**33 Schema Files** for all game systems:

```
data/schemas/
├── card-schema.json               # Card validation rules
├── pack-schema.json               # Pack definition validation
├── reward-schema.json             # Reward system validation
├── battle-schema.json             # Combat system rules
├── progression-schema.json        # Player leveling rules
├── deck-schema.json               # Deck building rules
├── achievement-schema.json        # Achievement tracking
├── alliance-schema.json           # Alliance system
├── audio-schema.json              # Audio configuration
├── campaign-schema.json           # Campaign structure
├── deployment-schema.json         # Deployment rules
├── diplomacy-schema.json          # Diplomacy mechanics
├── economy-node-schema.json       # AFK economy
├── equipment-schema.json          # Equipment system
├── event-schema.json              # Live events
├── expedition-schema.json         # Expeditions
├── leaderboard-schema.json        # Rankings
├── map-schema.json                # Map generation
├── matchmaking-schema.json        # PvP matchmaking
├── notification-schema.json       # Push notifications
├── player-schema.json             # Player data
├── quest-schema.json              # Quest system
├── resource-schema.json           # Resource definitions
├── session-schema.json            # Session management
├── starter-deck-schema.json       # Starter decks
├── store-schema.json              # In-game store
├── tactic-schema.json             # Tactic cards
├── theme-schema.json              # Visual themes
├── trade-schema.json              # Trading system
├── trainer-deck-schema.json       # AI decks
├── tutorial-schema.json           # Tutorial flow
├── ui-schema.json                 # UI configuration
└── codex-schema.json              # Codex structure
```

---

## 🗂️ How to Navigate

### 🔍 Find a Specific Card

1. **By Collection Number**: Check [`docs/codex/base-set/COMPLETE-CARD-LIST.md`](codex/base-set/COMPLETE-CARD-LIST.md) (table with all 140 cards)
2. **By Type**: Browse [`data/cards/base-set/{heroes,units,tactics,buildings}/`](../data/cards/base-set/)
3. **By Element**: Use element-lists in [`data/cards/base-set/element-lists/`](../data/cards/base-set/element-lists/)

### 📦 Find Pack Drop Rates

1. Go to [`data/products/packs/`](../data/products/packs/)
2. Open desired pack JSON (e.g., `standard-pack.json`)
3. Check `rarityDistribution` and `pitySystem` fields

### 🎁 Check Daily Rewards

1. Open [`data/products/rewards/daily-login-rewards.json`](../data/products/rewards/daily-login-rewards.json)
2. Find day number (1-30) in `rewards` array
3. Check `rewardType` (Gold, Gems, Pack, etc.)

---

## ✅ Architecture Verification Checklist

### ✅ Good Practices (What We Do)
- ✅ Each card = 1 JSON file with **all** metadata
- ✅ Packs reference **card pools** (`"cardPool": "base-set-all"`)
- ✅ No stat duplication (HP/attack defined **once** in card file)
- ✅ Runtime data in `data/`, documentation in `docs/`
- ✅ JSON schemas in `data/schemas/` for validation

### ❌ Bad Practices (What We Avoid)
- ❌ ~~Card stats in pack files~~ (use card pools instead)
- ❌ ~~Master card array with all stats~~ (individual files only)
- ❌ ~~Runtime JSON in `docs/` folder~~ (docs/ is Markdown only)
- ❌ ~~Monolithic data files~~ (split by type/series)

---

## 🚀 Next Steps

### For Developers
1. **Validate Data**: `.\tools\generators\validate-base-set.ps1`
2. **Generate Remaining Cards**: `.\tools\generators\generate-all-base-set-cards.ps1`
3. **Sync to Unity**: `.\tools\importers\sync-data-to-unity.ps1` (future)

### For Designers
1. **Review Cards**: [`docs/codex/base-set/COMPLETE-CARD-LIST.md`](codex/base-set/COMPLETE-CARD-LIST.md)
2. **Check Balance**: Compare hero stats, rarity budgets
3. **Test Economy**: Run F2P progression simulation

---

## 📊 Progress Summary

| Category | Complete | Remaining | Total |
|----------|----------|-----------|-------|
| **Heroes** | 10 | 15 | 25 |
| **Units** | 16 | 74 | 90 |
| **Tactics** | 3 | 17 | 20 |
| **Buildings** | 1 | 4 | 5 |
| **TOTAL CARDS** | **30** | **110** | **140** |

| Category | Status |
|----------|--------|
| **Packs** | ✅ 16/16 Complete |
| **Boxes** | ✅ 3/3 Complete |
| **Rewards** | ✅ 1/1 Complete |
| **Schemas** | ✅ 33/33 Complete |
| **Manifests** | ✅ 2/2 Complete |

---

**Last Updated**: January 11, 2026  
**Source of Truth**: `data/` directory (runtime game data)  
**Documentation**: `docs/` directory (Markdown reference files only)
