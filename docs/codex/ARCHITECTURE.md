# Card Data Architecture - Single Source of Truth

## Core Principle
**Each card is defined ONCE in its own JSON file. Everything else references by ID.**

## File Structure

```
docs/codex/base-set/
├── BASE_SET_MASTER_CARDS.json      # Complete collection (can be split into individual files)
├── series-manifest.json             # Series metadata + card ID lists
├── COMPLETE-CARD-LIST.md           # Human-readable reference (all 140 cards)
└── cards/                          # Individual card JSON files (30 complete, 110 to-do)
    ├── hero-aria-flame-knight.json
    ├── hero-ragnar-inferno-berserker.json
    ├── unit-fire-soldier.json
    └── ... (140 total)
```

## Card JSON Schema

**Full card definition** (`docs/codex/base-set/cards/hero-aria-flame-knight.json`):
```json
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "collectionNumber": "BS-001",
  "name": "Aria, Flame Knight",
  "type": "Hero",
  "element": "Fire",
  "rarity": {"tier": "Epic", "stars": 3, "points": 8},
  "stats": {"health": 80, "mana": 60, "attack": 45, "defense": 12, "moveRange": 3, "attackRange": 1},
  "abilities": [
    {"abilityId": "ABILITY_BLAZING_STRIKE", "name": "Blazing Strike", ...}
  ],
  "tacticSlots": 3,
  "lore": "A legendary warrior...",
  "acquisition": {"packSources": ["fire-starter-box", "standard-pack", ...], "campaignDrops": [...]}
}
```

## Pack JSON Schema

**Packs reference card pools, NOT individual cards** (`docs/products/packs/standard-pack.json`):
```json
{
  "productId": "standard-pack",
  "cardPool": "base-set-all",          ← Pool ID, not individual card list
  "cardsPerPack": 5,
  "rarityDistribution": {...},         ← How to pick cards from pool
  "guarantees": [{slot: 5, minimumRarity: "Uncommon"}]
}
```

**Element boosters reference element-specific pools**:
```json
{
  "productId": "element-booster-fire",
  "cardPool": "base-set-fire-only",    ← Fire cards only (BS-001 to BS-025)
  "cardsPerPack": 5
}
```

## Card Pool Definitions

Card pools are defined in `docs/codex/base-set/series-manifest.json`:

```json
{
  "seriesId": "base-set",
  "cardPools": {
    "base-set-all": {
      "description": "All 140 Base Set cards",
      "cardRange": "BS-001 to BS-140",
      "totalCards": 140
    },
    "base-set-fire-only": {
      "description": "Fire element cards only",
      "cardRange": "BS-001 to BS-025",
      "cardIds": ["HERO_ARIA_FLAME_KNIGHT", "HERO_RAGNAR_INFERNO_BERSERKER", ...]
    },
    "base-set-heroes-only": {
      "description": "All heroes (any element)",
      "filterBy": {"type": "Hero"},
      "estimatedCount": 33
    }
  }
}
```

## Runtime Card Loading (Unity)

### CardManager.cs (Pseudocode)
```csharp
public class CardManager {
    private Dictionary<string, CardData> _cardDatabase;
    
    // Load all cards at startup
    public void Initialize() {
        _cardDatabase = new Dictionary<string, CardData>();
        
        // Option 1: Load individual card files
        var cardFiles = Resources.LoadAll<TextAsset>("Cards/BaseSet");
        foreach (var file in cardFiles) {
            var card = JsonUtility.FromJson<CardData>(file.text);
            _cardDatabase[card.cardId] = card;
        }
        
        // Option 2: Load master file and cache
        var master = Resources.Load<TextAsset>("BASE_SET_MASTER_CARDS");
        var masterData = JsonUtility.FromJson<MasterCardList>(master.text);
        foreach (var card in masterData.cards) {
            _cardDatabase[card.cardId] = card;
        }
    }
    
    // Get card by ID (runtime lookup)
    public CardData GetCard(string cardId) {
        return _cardDatabase[cardId];
    }
}
```

### PackOpener.cs (Pseudocode)
```csharp
public class PackOpener {
    // Open pack: Generate 5 card IDs, then fetch full data
    public List<CardData> OpenPack(string packId) {
        var packDef = LoadPackDefinition(packId);  // Load standard-pack.json
        var cardIds = GenerateCardIds(packDef);    // ["UNIT_FIRE_SOLDIER", "HERO_ARIA_FLAME_KNIGHT", ...]
        
        // Fetch full card data from CardManager
        var cards = new List<CardData>();
        foreach (var cardId in cardIds) {
            cards.Add(CardManager.Instance.GetCard(cardId));
        }
        return cards;
    }
    
    private List<string> GenerateCardIds(PackDefinition pack) {
        // Load card pool
        var pool = LoadCardPool(pack.cardPool);  // "base-set-all" → 140 card IDs
        
        // Apply rarity distribution
        var cardIds = new List<string>();
        for (int i = 0; i < pack.cardsPerPack; i++) {
            var rarity = RollRarity(pack.rarityDistribution);
            var cardId = PickRandomCard(pool, rarity);
            cardIds.Add(cardId);
        }
        
        // Apply guarantees
        if (pack.guarantees exists for slot 5) {
            cardIds[4] = PickRandomCard(pool, "Uncommon+");
        }
        
        return cardIds;
    }
}
```

## Benefits of This Architecture

### ✅ Single Source of Truth
- Card stats defined ONCE in `cards/*.json`
- Packs, decks, collection just store card IDs
- Update a card → automatically reflects everywhere

### ✅ No Duplication
- Standard Pack references "base-set-all" pool
- Fire Booster references "base-set-fire-only" pool
- No copying HP/ATK/abilities into pack files

### ✅ Scalability
- Add new card: Drop 1 JSON file in `cards/` folder
- Add new pack: Reference existing card pools
- Add new series: Create new `series-manifest.json`

### ✅ Save Data Efficiency
- Player collection stores `["HERO_ARIA_FLAME_KNIGHT", "UNIT_FIRE_SOLDIER"]`
- NOT full card objects with stats
- Saves: 10KB (IDs) vs 1MB (full cards)

### ✅ Versioning & Balancing
- Card nerfs/buffs: Update 1 file
- No risk of desync between pack definitions
- Easy rollback: Revert single card JSON

## To-Do Items

### Immediate
- [x] Create `split-master-cards.ps1` script
- [x] Split 30 complete cards into individual files
- [ ] Generate remaining 110 cards from `COMPLETE-CARD-LIST.md`
- [ ] Update `series-manifest.json` with all card pool definitions

### Phase 2
- [ ] Unity CardManager.cs implementation
- [ ] Unity PackOpener.cs implementation
- [ ] Nakama RPC: AddCardsToCollection (stores IDs only)
- [ ] Collection UI: Fetch full card data for display

## Example: How Daily Reward Pack Works

1. **Pack Definition** (`daily-reward-pack.json`):
   ```json
   {
     "cardPool": "base-set-all",
     "cardsPerPack": 5,
     "heroRestriction": {"maxRarity": "Epic", "chanceModifier": 0.3}
   }
   ```

2. **Runtime** (Player opens pack):
   - PackOpener generates 5 card IDs: `["UNIT_FIRE_SOLDIER", "UNIT_EMBER_SCOUT", "TACTIC_HEAL", "UNIT_GOBLIN_RAIDER", "HERO_CINDER_FLAME_MAGE"]`
   - CardManager fetches full data for each ID
   - Display pack opening animation with full card details

3. **Save to Collection**:
   - Nakama storage: `ownedCards["BS-006"] = {quantity: 2, shiny: false}`
   - NOT: `ownedCards["BS-006"] = {name: "Fire Soldier", hp: 30, ...}` ← WRONG!

## Scripts

- `split-master-cards.ps1` - Split BASE_SET_MASTER_CARDS.json into individual files
- `generate-card-json-files.ps1` - Generate cards from COMPLETE-CARD-LIST.md (needs fixing)
- `validate-card-refs.ps1` - Verify all pack references point to valid card IDs (to-do)

---

**Remember**: Cards are defined ONCE. Everything else just references `cardId` or `collectionNumber`.
