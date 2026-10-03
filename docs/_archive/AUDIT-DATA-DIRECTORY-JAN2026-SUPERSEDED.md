# 🔍 Data Directory Comprehensive Audit - January 11, 2026

## Executive Summary

**Files Audited**: 90 JSON files in `data/` directory  
**Critical Violations**: 2 files (BASE_SET_MASTER_CARDS.json, fire-heroes.json)  
**Borderline Cases**: 1 file (series-checklist - acceptable for UX)  
**Duplication Detected**: ~705 lines of duplicated card metadata  
**Potential Savings**: 97% reduction (replace 705 lines with ~20 lines of ID references)  

---

## 🚨 Critical Issues

### Issue #1: BASE_SET_MASTER_CARDS.json (435 lines)
**File**: `data/manifests/BASE_SET_MASTER_CARDS.json`  
**Problem**: Contains **full card definitions** for 30 cards (stats, abilities, lore)  
**Severity**: CRITICAL  
**Duplication**: Same data exists in `data/cards/base-set/{type}/*.json`

**Example violation**:
```json
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "stats": {"health": 80, "attack": 45},  ← Duplicated!
  "abilities": [{"name": "Blazing Strike"}]  ← Duplicated!
}
```

**Correct approach**: Manifest should only list card IDs, not full data
```json
{
  "seriesId": "base-set",
  "cardIds": ["HERO_ARIA_FLAME_KNIGHT", "UNIT_FIRE_SOLDIER", ...]
}
```

---

### Issue #2: fire-heroes.json (270 lines)
**File**: `data/cards/base-set/element-lists/fire-heroes.json`  
**Problem**: Contains **full card definitions** for 5 Fire heroes  
**Severity**: HIGH  
**Duplication**: Same data exists in `data/cards/base-set/heroes/*.json`

**Example violation**:
```json
{
  "cards": [
    {
      "cardId": "HERO_ARIA_FLAME_KNIGHT",
      "stats": {"health": 80},  ← Duplicated from hero-aria-flame-knight.json!
      "abilities": [...]  ← Duplicated!
    }
  ]
}
```

**Correct approach**: Element list should only reference IDs
```json
{
  "element": "Fire",
  "cardType": "Hero",
  "cardIds": [
    "HERO_ARIA_FLAME_KNIGHT",
    "HERO_RAGNAR_INFERNO_BERSERKER",
    "HERO_CINDER_FLAME_MAGE",
    "HERO_BLAZE_DRAGON_RIDER",
    "HERO_EMBER_PHOENIX_GUARDIAN"
  ]
}
```

---

### Issue #3: series-checklist-base-set.json (56 lines) - BORDERLINE ACCEPTABLE
**File**: `data/collection/series-checklist-base-set.json`  
**Status**: ⚠️ **Borderline acceptable** - Collection-specific metadata justifies minimal duplication  
**Severity**: LOW (acceptable for UX performance)

**Current Structure**:
```json
{
  "collectionNumber": "BS-001",
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "name": "Aria, Flame Knight",
  "element": "Fire",
  "type": "Hero",
  "rarity": "Epic"
}
```

**Analysis**:
- ✅ **Adds value**: Collection number (BS-001) unique to checklist  
- ✅ **Adds value**: Display name for UI ("Aria, Flame Knight")  
- ⚠️ **Duplicates**: Element/type/rarity (could be derived from card files)

**Verdict**: **Keep as-is** - Collection checklists are a special case where minimal duplication is acceptable for UI performance. The alternative (JOIN 140 card files to build checklist UI) would be inefficient.  

---

## ✅ Files Using Correct Architecture

### Starter Boxes (CORRECT)
**Files**: `fire-starter-box.json`, `water-starter-box.json`, `earth-starter-box.json`  
**Structure**: ✅ References card IDs only, no stat duplication

```json
{
  "fixedContents": [
    {"cardId": "HERO_ARIA_FLAME_KNIGHT", "quantity": 1},
    {"cardId": "UNIT_FIRE_SOLDIER", "quantity": 3}
  ]
}
```

### Pack Files (CORRECT)
**Files**: All 16 pack files  
**Structure**: ✅ References card pools, no individual card data

```json
{
  "productId": "standard-pack",
  "cardPool": "base-set-all",  ← References pool, not cards
  "rarityDistribution": {...}
}
```

### Starter Decks (CORRECT - Fixed Today)
**File**: `starter-decks.json`  
**Structure**: ✅ References card IDs only (was 854 lines, now 118 lines)

```json
{
  "starterDecks": [
    {
      "deckId": "STARTER_FIRE",
      "cardIds": ["HERO_ARIA_FLAME_KNIGHT", ...]
    }
  ]
}
```

---

## 🎯 Card ID Naming Convention (Proposed)

### Current Problem
**Current IDs**: `HERO_ARIA_FLAME_KNIGHT`  
**Issue**: No series namespace - same hero in multiple series would conflict

**Example conflict**:
```
HERO_ARIA_FLAME_KNIGHT  ← Base Set version (80 HP, 45 ATK)
HERO_ARIA_FLAME_KNIGHT  ← Expansion Set version (90 HP, 50 ATK, new ability)
```

### Proposed Solution: Series-Namespaced IDs

**Format**: `{SERIES}_{TYPE}_{NAME}`

**Base Set Example**:
```
BS_HERO_ARIA_FLAME_KNIGHT          ← Base Set (BS)
BS_UNIT_FIRE_SOLDIER               ← Base Set
BS_TACTIC_FIREBALL                 ← Base Set
```

**Expansion Set Example**:
```
EX1_HERO_ARIA_FLAME_KNIGHT         ← Expansion 1 (different stats/abilities)
EX1_HERO_ARIA_CHAMPION             ← Promoted version with new ID
```

**Seasonal Set Example**:
```
W2026_HERO_ARIA_WINTER_KNIGHT      ← Winter 2026 seasonal variant
S2026_HERO_ARIA_SUMMER_KNIGHT      ← Summer 2026 seasonal variant
```

### Benefits
✅ **No conflicts**: Same hero can exist in multiple series with different stats  
✅ **Clear provenance**: Instantly know which series a card belongs to  
✅ **Easy filtering**: `SELECT * FROM cards WHERE cardId LIKE 'BS_%'`  
✅ **Cross-series balance**: Base Set Aria vs Expansion Aria are separate cards  
✅ **Seasonal variants**: Winter Aria can have ice-themed abilities  

### Migration Path
1. **Phase 1**: Add `seriesPrefix` field to all cards (keep current IDs for backward compatibility)
2. **Phase 2**: Generate new IDs with series prefix
3. **Phase 3**: Update all references (packs, decks, manifests)
4. **Phase 4**: Deprecate old IDs

---

## 📋 Recommended Actions (Immediate)

### 1. Delete Duplicate Data Files

**BASE_SET_MASTER_CARDS.json**:
- ❌ DELETE: Full card definitions (435 lines)
- ✅ CREATE: `base-set-card-list.json` (just IDs, ~30 lines)

**fire-heroes.json**:
- ❌ DELETE: Full hero definitions (270 lines)
- ✅ CREATE: `fire-hero-ids.json` (just IDs, ~10 lines)

**series-checklist-base-set.json**:
- ✅ **KEEP AS-IS**: Collection-specific metadata (collection numbers) justifies minimal duplication
- No action required

### 2. Create Correct Manifest Structure

**New File**: `data/manifests/base-set-card-list.json`
```json
{
  "seriesId": "base-set",
  "seriesName": "Base Set",
  "totalCards": 140,
  "releaseDate": "2026-Q1",
  "cardIds": [
    "BS_HERO_ARIA_FLAME_KNIGHT",
    "BS_HERO_RAGNAR_INFERNO_BERSERKER",
    "BS_UNIT_FIRE_SOLDIER",
    // ... 137 more IDs
  ],
  "cardPools": {
    "base-set-all": {
      "description": "All 140 Base Set cards",
      "filters": {"series": "base-set"}
    },
    "base-set-fire-only": {
      "description": "Fire element cards only",
      "filters": {"series": "base-set", "element": "Fire"}
    }
  }
}
```

### 3. Create Element Reference Lists (ID-Only)

**New File**: `data/cards/base-set/element-lists/fire-ids.json`
```json
{
  "element": "Fire",
  "totalCards": 25,
  "heroes": [
    "BS_HERO_ARIA_FLAME_KNIGHT",
    "BS_HERO_RAGNAR_INFERNO_BERSERKER",
    "BS_HERO_CINDER_FLAME_MAGE",
    "BS_HERO_BLAZE_DRAGON_RIDER",
    "BS_HERO_EMBER_PHOENIX_GUARDIAN"
  ],
  "units": [
    "BS_UNIT_FIRE_SOLDIER",
    "BS_UNIT_EMBER_SCOUT",
    // ... 18 more
  ],
  "tactics": [
    "BS_TACTIC_FIREBALL",
    "BS_TACTIC_FLAME_SHIELD",
    "BS_TACTIC_INFERNO"
  ],
  "buildings": [
    "BS_BUILDING_FORGE"
  ]
}
```

---

## 🏗️ Correct Data Architecture

### Single Source of Truth Flow

```
1. CARD DATA (Source of Truth)
   data/cards/base-set/heroes/hero-aria-flame-knight.json
   └─ Contains: Stats, abilities, lore, art, acquisition

2. MANIFESTS (References Only)
   data/manifests/base-set-card-list.json
   └─ Contains: Card IDs, series metadata, pool definitions

3. ELEMENT LISTS (References Only)
   data/cards/base-set/element-lists/fire-ids.json
   └─ Contains: Card IDs grouped by element/type

4. PRODUCTS (References Only)
   data/products/packs/standard-pack.json
   └─ Contains: Card pool references (not individual cards)

5. DECKS (References Only)
   data/decks/starter/starter-decks.json
   └─ Contains: Card IDs for deck composition

6. RUNTIME (Unity C#)
   CardManager.GetCard("BS_HERO_ARIA_FLAME_KNIGHT")
   └─ Loads from data/cards/base-set/heroes/hero-aria-flame-knight.json
```

### Update Workflow Example

**Scenario**: Buff Aria's HP from 80 → 85

**Correct** (Single Source of Truth):
1. Edit `data/cards/base-set/heroes/hero-aria-flame-knight.json`
2. Change: `"health": 85`
3. Done! ✅ (Change reflects everywhere automatically)

**Wrong** (Current Duplication):
1. Edit `data/cards/base-set/heroes/hero-aria-flame-knight.json`
2. Edit `data/manifests/BASE_SET_MASTER_CARDS.json` (find Aria, change HP)
3. Edit `data/cards/base-set/element-lists/fire-heroes.json` (find Aria, change HP)
4. Pray you didn't miss any other files ❌

---

## 📊 File Audit Summary

| File Category | Total Files | Architecture | Action |
|---------------|-------------|--------------|--------|
| **Individual Cards** | 30 | ✅ Correct (single source) | None |
| **Pack Files** | 16 | ✅ Correct (pool references) | None |
| **Starter Boxes** | 3 | ✅ Correct (ID references) | None |
| **Starter Decks** | 1 | ✅ Correct (ID references) | None |
| **Daily Rewards** | 1 | ✅ Correct (pack references) | None |
| **Schemas** | 33 | ✅ Correct (validation rules) | None |
| **Master Cards Manifest** | 1 | ❌ WRONG (full card data) | DELETE |
| **Element Lists** | 1 | ❌ WRONG (full card data) | DELETE |
| **Series Checklist** | 1 | ⚠️ UNKNOWN | AUDIT |

**Total Duplication**: ~705 lines (435 from manifest + 270 from element list)  
**Savings from Cleanup**: ~97% reduction (replace with ~20 lines of IDs)

---

## 🎯 Proposed Card ID Migration

### Phase 1: Add Series Prefix Field (Non-Breaking)

Update all card files:
```json
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",  ← Keep for backward compatibility
  "seriesPrefix": "BS",
  "canonicalId": "BS_HERO_ARIA_FLAME_KNIGHT",  ← New canonical ID
  "collectionNumber": "BS-001"
}
```

### Phase 2: Generate New IDs Script

Create `tools/generators/migrate-card-ids-to-series-prefix.ps1`:
- Read all card files
- Generate new IDs with series prefix
- Update all references (packs, decks, manifests)
- Create migration report

### Phase 3: Unity Implementation

```csharp
// Support both old and new IDs during transition
public class CardManager {
    public static CardData GetCard(string cardId) {
        // Try new ID format first
        CardData card = LoadFromFile($"data/cards/base-set/{cardId}.json");
        
        // Fall back to old ID format
        if (card == null && !cardId.StartsWith("BS_")) {
            card = LoadFromFile($"data/cards/base-set/BS_{cardId}.json");
        }
        
        return card;
    }
}
```

### Phase 4: Deprecation Timeline

- **Week 1**: Add `canonicalId` field to all cards
- **Week 2**: Update all references to use `canonicalId`
- **Week 3**: Rename files to use new ID format
- **Week 4**: Remove `cardId` field, keep only `canonicalId`

---

## 🔗 Files to Create

1. `data/manifests/base-set-card-list.json` (replaces BASE_SET_MASTER_CARDS.json)
2. `data/cards/base-set/element-lists/fire-ids.json` (replaces fire-heroes.json)
3. `data/cards/base-set/element-lists/water-ids.json`
4. `data/cards/base-set/element-lists/earth-ids.json`
5. `data/cards/base-set/element-lists/lightning-ids.json`
6. `data/cards/base-set/element-lists/wind-ids.json`
7. `data/cards/base-set/element-lists/frost-ids.json`
8. `data/cards/base-set/element-lists/neutral-ids.json`
9. `tools/generators/migrate-card-ids-to-series-prefix.ps1`

---

## ✅ Validation Checklist

After cleanup, verify:
- [ ] No JSON file in `data/` contains duplicated card stats/abilities
- [ ] All manifests reference card IDs only (no full card objects)
- [ ] All element lists reference card IDs only
- [ ] All product files (packs, boxes) reference IDs or pools only
- [ ] All deck files reference card IDs only
- [ ] Card IDs include series prefix (BS_, EX1_, etc.)
- [ ] Single source of truth: `data/cards/{series}/{type}/*.json`

---

**Audit Date**: January 11, 2026  
**Auditor**: @Soverign-Beast-Mode (Design Agent)  
**Status**: ✅ Audit complete, violations identified  
**Next Step**: Clean up duplicate files, implement series-prefixed IDs
