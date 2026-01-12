# 🚀 Quick Start - Sovereign Territories

> **Fast navigation for finding cards, packs, and game data**

---

## 📍 Where Everything Lives

### 🎴 Cards
**Location**: [`data/cards/base-set/`](../data/cards/base-set/)

```
data/cards/base-set/
├── heroes/        # 10 hero cards (BS-001 to BS-005, BS-026 to BS-030)
├── units/         # 16 unit cards (BS-006 to BS-021)
├── tactics/       # 3 tactic cards (BS-022 to BS-024)
└── buildings/     # 1 building card (BS-025)
```

**Quick Access**:
- Fire Hero Aria: [`hero-aria-flame-knight.json`](../data/cards/base-set/heroes/hero-aria-flame-knight.json)
- Fire Unit: [`unit-fire-soldier.json`](../data/cards/base-set/units/unit-fire-soldier.json)
- Fire Tactic: [`tactic-fireball.json`](../data/cards/base-set/tactics/tactic-fireball.json)

### 📦 Packs
**Location**: [`data/products/packs/`](../data/products/packs/)

**16 Pack Types**:
- Universal: [`standard-pack.json`](../data/products/packs/standard-pack.json) (1,000 Gold)
- Element Boosters: `element-booster-{fire,water,earth,lightning,wind,frost}.json` (1,500 Gold each)
- Premium: [`epic-pack.json`](../data/products/packs/epic-pack.json), [`legendary-pack.json`](../data/products/packs/legendary-pack.json), [`hero-pack.json`](../data/products/packs/hero-pack.json)
- Rewards: [`daily-reward-pack.json`](../data/products/packs/daily-reward-pack.json), [`weekly-reward-pack.json`](../data/products/packs/weekly-reward-pack.json), [`monthly-reward-pack.json`](../data/products/packs/monthly-reward-pack.json)

### 🎁 Login Rewards
**Location**: [`data/products/rewards/daily-login-rewards.json`](../data/products/rewards/daily-login-rewards.json)

30-day cycle: 11,250 Gold + 895 Gems + 13 packs/month

### 📐 Schemas
**Location**: [`data/schemas/`](../data/schemas/)

33 validation schemas for all game systems (cards, packs, battles, progression, etc.)

### 📚 Card Reference
**Location**: [`docs/codex/base-set/COMPLETE-CARD-LIST.md`](codex/base-set/COMPLETE-CARD-LIST.md)

Human-readable table of all 140 Base Set cards

---

## 🎯 Quick Tasks

### View All Cards
```bash
# PowerShell
Get-ChildItem data/cards/base-set -Recurse -Filter "*.json"

# Or browse in VS Code
Explorer: data/cards/base-set/
```

### View All Packs
```bash
Get-ChildItem data/products/packs -Filter "*.json"
```

### Validate Card Data
```powershell
.\tools\generators\validate-base-set.ps1
```

---

## 🗂️ Architecture Principles

### ✅ Single Source of Truth
- Each card = **1 JSON file** with **all** metadata (stats, abilities, lore)
- Packs reference **card pools**, NOT individual cards
- Example: [`standard-pack.json`](../data/products/packs/standard-pack.json) has `"cardPool": "base-set-all"` (not a list of 140 card IDs)

### ✅ Correct Pattern
**Card File** ([`hero-aria-flame-knight.json`](../data/cards/base-set/heroes/hero-aria-flame-knight.json)):
```json
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "stats": {"health": 80, "attack": 45},
  "abilities": [{"name": "Blazing Strike", "damage": 70}]
}
```

**Pack File** ([`standard-pack.json`](../data/products/packs/standard-pack.json)):
```json
{
  "productId": "standard-pack",
  "cardPool": "base-set-all",  // ← References pool, not cards
  "rarityDistribution": {"Common": 65, "Legendary": 0.5}
}
```

**Runtime** (Unity C#):
```csharp
// PackOpener generates card IDs based on rarityDistribution
List<string> cardIds = PackOpener.OpenPack("standard-pack"); // ["HERO_ARIA", "UNIT_FIRE_SOLDIER", ...]

// CardManager fetches full card data
foreach (string id in cardIds) {
    CardData card = CardManager.GetCard(id); // Loads from data/cards/base-set/
    Debug.Log($"{card.name}: {card.stats.health} HP");
}
```

### ❌ Wrong Pattern (What We Don't Do)
```json
// ❌ DON'T duplicate stats in pack file
{
  "productId": "standard-pack",
  "cards": [
    {"cardId": "HERO_ARIA", "health": 80, "attack": 45},  // ← Duplicated!
    {"cardId": "UNIT_FIRE_SOLDIER", "health": 20, "attack": 16}
  ]
}
```

---

## 📊 File Counts

| Type | Complete | Remaining | Total |
|------|----------|-----------|-------|
| **Cards** | 30 | 110 | 140 |
| **Packs** | 16 | 0 | 16 |
| **Boxes** | 3 | 0 | 3 |
| **Rewards** | 1 | 0 | 1 |
| **Schemas** | 33 | 0 | 33 |

---

## 🔗 Full Documentation

For comprehensive file locations and examples:
- [📍 FILE-LOCATIONS.md](FILE-LOCATIONS.md) - Detailed file guide (500+ lines)
- [🏗️ PROJECT-STRUCTURE-ANALYSIS.md](PROJECT-STRUCTURE-ANALYSIS.md) - Architecture rationale (600+ lines)
- [📚 docs/codex/ARCHITECTURE.md](codex/ARCHITECTURE.md) - Card data architecture
- [📖 README.md](../README.md) - Project overview

---

**Last Updated**: January 11, 2026  
**Source**: `data/` directory (runtime game data)
