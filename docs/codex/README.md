# Codex Documentation

**Purpose**: The Codex is the single source of truth for all card definitions in Sovereign Territories.

**Philosophy**: "Define once, reference everywhere." Cards are never duplicated - products (boxes, packs, decks) reference card IDs from the codex.

---

## Directory Structure

```
codex/
├── _schema.json                  # JSON schema for card validation
├── README.md                     # This file
├── base-set/                     # Series 1 (140 cards, MVP)
│   ├── series-manifest.json      # Series metadata
│   ├── fire/                     # 25 Fire cards (BS-001 to BS-025)
│   ├── water/                    # 25 Water cards (BS-026 to BS-050)
│   ├── earth/                    # 25 Earth cards (BS-051 to BS-075)
│   ├── lightning/                # 15 Lightning cards (BS-076 to BS-090)
│   ├── wind/                     # 15 Wind cards (BS-091 to BS-105)
│   ├── frost/                    # 15 Frost cards (BS-106 to BS-120)
│   └── neutral/                  # 20 Neutral cards (BS-121 to BS-140)
└── elemental-fury/               # Series 2 (Phase 1.1)
```

---

## Card Naming Convention

**Format**: `{CATEGORY}_{NAME}_{VARIANT}.json`

**Examples**:
- `HERO_ARIA_FLAME_KNIGHT.json` (Hero named Aria, variant "Flame Knight")
- `UNIT_FIRE_SOLDIER.json` (Generic Fire soldier unit)
- `TACTIC_FIREBALL.json` (Fireball spell)
- `BUILDING_BARRACKS.json` (Barracks building)

**Rules**:
- All caps, underscores only
- CATEGORY must be: HERO, UNIT, TACTIC, BUILDING
- NAME should be unique within element (avoid HERO_ARIA and UNIT_ARIA in same element)
- VARIANT optional for heroes (HERO_ARIA vs HERO_ARIA_FLAME_KNIGHT)

---

## Collection Numbering

**Format**: `{SERIES_CODE}-{NUMBER}`

**Examples**:
- `BS-001` = Base Set, card #1
- `BS-140` = Base Set, card #140
- `EF-001` = Elemental Fury, card #1

**Numbering Order** (within each series):
1. Fire element (ascending rarity: Common → Legendary)
2. Water element
3. Earth element
4. Lightning element
5. Wind element
6. Frost element
7. Neutral element

---

## How to Add a New Card

1. **Choose Series**: Determine which series this belongs to (base-set, elemental-fury, etc.)

2. **Assign Collection Number**: 
   - Check series-manifest.json for next available number
   - Follow element ordering (Fire → Water → Earth → Lightning → Wind → Frost → Neutral)

3. **Create JSON File**:
   ```bash
   # Example: Adding new Fire hero to Base Set
   docs/codex/base-set/fire/HERO_NEW_FIRE_HERO.json
   ```

4. **Use Schema Template**:
   ```json
   {
     "cardId": "HERO_NEW_FIRE_HERO",
     "collectionNumber": "BS-026", // Next available
     "series": {
       "seriesId": "base-set",
       "seriesName": "Base Set",
       "cardNumber": 26,
       "totalCards": 140
     },
     "name": "Hero Name",
     "type": "Hero",
     "element": "Fire",
     ... (see _schema.json for full template)
   }
   ```

5. **Validate**:
   ```powershell
   # Run validation script
   ./scripts/validate-codex.ps1
   ```

6. **Update Series Manifest**:
   - Increment `totalCards` if adding to existing series
   - Update `cardBreakdown` rarity/element counts

---

## Card ID Best Practices

✅ **Good IDs**:
- `HERO_ARIA_FLAME_KNIGHT` (specific, descriptive)
- `UNIT_FIRE_SOLDIER` (element + type)
- `TACTIC_FIREBALL` (clear spell name)

❌ **Bad IDs**:
- `HERO_FIRE_1` (not descriptive)
- `UNIT_BASIC` (too generic)
- `ARIA` (missing category prefix)

---

## Avoiding Copyright Issues

**Use**:
- Public domain names (Aria, Gaia, Thalor - original creations)
- Mythology names (Ragnarok - Norse, Zephyr - Greek)
- Generic fantasy terms (Soldier, Mage, Drake, Elemental)

**Avoid**:
- Trademarked names (Mario, Pikachu, Gandalf)
- Direct game references (Firaga from Final Fantasy, Ice Barrage from RuneScape)

---

## Shiny Variants

Shiny variants are **cosmetic only** (same stats, different art).

**Implementation**:
- Single card definition contains both normal + shiny art paths
- `art.portraitAsset` = normal version
- `art.shinyPortrait` = shiny version (golden border overlay)
- No separate card ID for shiny (runtime flag in player collection)

**Example**:
```json
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "art": {
    "portraitAsset": "Art/Cards/BS-001_Aria_Portrait.png",
    "shinyPortrait": "Art/Cards/BS-001_Aria_Portrait_Shiny.png"
  }
}
```

---

## Updating Existing Cards

**Balance Changes**:
1. Edit card JSON (change stats, abilities)
2. Add entry to `meta.balanceHistory`:
   ```json
   {
     "date": "2026-07-15",
     "change": "Reduced Blazing Strike damage from 70 → 60",
     "author": "Lead Designer",
     "reason": "Too dominant in aggro meta"
   }
   ```
3. Update `releaseDate` in series manifest if major patch

**Art Updates**:
- Simply update `art.portraitAsset` path
- Keep old asset files for rollback if needed

---

## Loading Strategy (Unity)

**Startup**:
```csharp
// CardManager.cs
Dictionary<string, CardData> codex = new Dictionary<string, CardData>();

// Load all series
var series = LoadAllSeries("docs/codex/*/series-manifest.json");

foreach (var s in series)
{
    var cards = LoadCardsFromSeries(s.seriesId);
    foreach (var card in cards)
    {
        codex[card.cardId] = card;
    }
}
```

**Runtime Queries**:
```csharp
// Get specific card
CardData aria = codex["HERO_ARIA_FLAME_KNIGHT"];

// Get all Fire cards
var fireCards = codex.Values.Where(c => c.element == "Fire");

// Get all heroes in Base Set
var baseHeroes = codex.Values.Where(c => c.type == "Hero" && c.series.seriesId == "base-set");
```

---

**Remember**: Codex is read-only at runtime. Only tools/editors modify these files, never game code.
