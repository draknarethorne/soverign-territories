# Collection Tracking System

**Purpose**: Track player card collections, milestones, and element mastery for Sovereign Territories.

---

## Player Collection Schema

### Nakama Storage Structure
```json
{
  "collection": "player_collections",
  "userId": "user-uuid",
  "data": {
    "ownedCards": {
      "BS-001": {
        "cardId": "HERO_ARIA_FLAME_KNIGHT",
        "collectionNumber": "BS-001",
        "quantity": 1,
        "shiny": false,
        "acquiredDate": "2026-01-15T10:30:00Z",
        "source": "fire-starter-box"
      },
      "BS-006": {
        "cardId": "UNIT_FIRE_SOLDIER",
        "collectionNumber": "BS-006",
        "quantity": 3,
        "shiny": true,
        "acquiredDate": "2026-01-16T14:22:00Z",
        "source": "standard-pack"
      }
    },
    "totalUniqueCards": 42,
    "totalCards": 68,
    "seriesProgress": {
      "base-set": {
        "uniqueCards": 42,
        "totalCards": 140,
        "percentComplete": 30,
        "milestonesCompleted": ["10-cards", "25-cards"],
        "milestonesPending": ["50-cards", "75-cards", "100-cards", "140-cards"]
      }
    },
    "elementProgress": {
      "Fire": {
        "uniqueCards": 12,
        "totalCards": 25,
        "percentComplete": 48,
        "masteryComplete": false
      },
      "Water": {
        "uniqueCards": 8,
        "totalCards": 25,
        "percentComplete": 32,
        "masteryComplete": false
      },
      "Neutral": {
        "uniqueCards": 5,
        "totalCards": 20,
        "percentComplete": 25,
        "masteryComplete": false
      }
    },
    "achievements": {
      "first-pack-opened": {
        "achievedDate": "2026-01-15T10:25:00Z",
        "rewardClaimed": true
      },
      "first-shiny-acquired": {
        "achievedDate": "2026-01-16T14:22:00Z",
        "cardId": "BS-006",
        "rewardClaimed": false
      }
    }
  }
}
```

---

## Collection Milestones (Base Set)

### Global Milestones
Defined in [series-manifest.json](../codex/base-set/series-manifest.json)

| Cards Collected | Reward | Trigger ID | Auto-Grant |
|---|---|---|---|
| 10 | 250 Gold | `milestone-10-cards` | ✅ |
| 25 | 1× Standard Pack | `milestone-25-cards` | ✅ |
| 50 | 1× Rare Pack | `milestone-50-cards` | ✅ |
| 75 | 1× Epic Pack | `milestone-75-cards` | ✅ |
| 100 | 1× Legendary Pack | `milestone-100-cards` | ✅ |
| 140 | 1× Mythic Pack + "Base Set Master" title | `milestone-140-cards` | ✅ |

**Implementation**:
- Check `totalUniqueCards` after every card acquisition
- If new count crosses threshold → grant reward immediately
- Mark milestone as completed in `seriesProgress.milestonesCompleted`
- Prevent duplicate rewards (check milestone not already in completed array)

---

### Element Mastery Milestones

**Triggers**: Complete all cards for an element

| Element | Cards Required | Reward | Trigger ID |
|---|---|---|---|
| Fire | 25/25 | Fire Element Booster + "Ember Legion Champion" title | `element-mastery-fire` |
| Water | 25/25 | Water Element Booster + "Tidal Order Champion" title | `element-mastery-water` |
| Earth | 25/25 | Earth Element Booster + "Stone Compact Champion" title | `element-mastery-earth` |
| Lightning | 15/15 | Lightning Element Booster + "Volt Covenant Champion" title | `element-mastery-lightning` |
| Wind | 15/15 | Wind Element Booster + "Sky Clans Champion" title | `element-mastery-wind` |
| Frost | 15/15 | Frost Element Booster + "Frost Brotherhood Champion" title | `element-mastery-frost` |
| Neutral | 20/20 | Hero Pack + "Sovereign Realms Diplomat" title | `element-mastery-neutral` |

**Implementation**:
```csharp
public void CheckElementMastery(string element) {
    var elementCards = GetCardsForElement(element);
    var ownedCards = playerCollection.ownedCards.Count(c => c.element == element);
    
    if (ownedCards >= elementCards.TotalCards && !elementProgress[element].masteryComplete) {
        // Grant reward
        GrantElementBooster(element);
        GrantTitle($"{element} Champion");
        
        // Mark complete
        elementProgress[element].masteryComplete = true;
        SaveCollection();
    }
}
```

---

## Card Acquisition Flow

### 1. Pack Opening
```csharp
public async Task<List<CardInstance>> OpenPack(string packId) {
    // Open pack (PackOpener.cs)
    var cards = await PackOpener.OpenPack(packId);
    
    // Add to collection
    foreach (var card in cards) {
        AddCardToCollection(card);
    }
    
    // Check milestones
    CheckGlobalMilestones();
    CheckElementMastery(card.element);
    
    return cards;
}
```

### 2. Adding Cards
```csharp
public void AddCardToCollection(CardInstance card) {
    var collectionNum = card.collectionNumber;
    
    if (!ownedCards.ContainsKey(collectionNum)) {
        // First copy - increment unique count
        ownedCards[collectionNum] = new OwnedCard {
            cardId = card.cardId,
            collectionNumber = collectionNum,
            quantity = 1,
            shiny = card.isShiny,
            acquiredDate = DateTime.UtcNow,
            source = card.source
        };
        totalUniqueCards++;
    } else {
        // Duplicate - increment quantity
        ownedCards[collectionNum].quantity++;
        
        // If shiny and didn't have shiny before, update
        if (card.isShiny && !ownedCards[collectionNum].shiny) {
            ownedCards[collectionNum].shiny = true;
            TriggerAchievement("first-shiny-acquired", collectionNum);
        }
    }
    
    totalCards++;
    SaveCollection();
}
```

---

## Duplicate Card Handling

### Phase 1 (MVP): Quantity Tracking Only
- Cards can be owned multiple times (quantity field)
- No duplicate conversion system yet
- Allows "playset" ownership (e.g., 3× Fire Soldier for deck)

### Phase 2: Card Shards System
```json
{
  "ownedCards": {
    "BS-001": {
      "quantity": 1,
      "shards": 0
    },
    "BS-006": {
      "quantity": 3,
      "shards": 15
    }
  },
  "totalShards": 15
}
```

**Shard Conversion** (Phase 2 feature):
- 4th+ copy of Common → 5 shards
- 4th+ copy of Uncommon → 10 shards
- 3rd+ copy of Rare → 25 shards
- 2nd+ copy of Epic → 50 shards
- 2nd+ copy of Legendary → 100 shards

**Shard Usage**:
- 100 shards → 1× Standard Pack
- 500 shards → 1× Rare Pack
- Craft specific cards (Rare = 100 shards, Epic = 400 shards, Legendary = 1,600 shards)

---

## Collection UI Mockup

### Series Checklist
```
Base Set (42/140 cards - 30% complete)
═══════════════════════════════════════

Fire (12/25 - 48%)
[✅] BS-001 Aria, Flame Knight
[✅] BS-002 Ragnar, Inferno Berserker
[ ] BS-003 Cinder, Flame Mage
[✅] BS-004 Blaze, Dragon Rider (SHINY ✨)
...

Water (8/25 - 32%)
[✅] BS-026 Thalor, Tide Guardian
[ ] BS-027 Marina, Sea Witch
...

Milestones
✅ 10 cards (250 Gold)
✅ 25 cards (Standard Pack)
⏳ 50 cards (Rare Pack) - 8 cards away
⏳ 140 cards (Mythic Pack + "Base Set Master") - 98 cards away
```

---

## Collection Statistics

### Tracking Metrics
- **Total Unique Cards**: Unique collection numbers owned (no duplicates counted)
- **Total Cards**: All cards including duplicates
- **Series Progress**: % completion per series (base-set, elemental-fury, etc.)
- **Element Progress**: % completion per element
- **Shiny Collection**: Count of unique shiny variants owned
- **Rarity Breakdown**: Cards owned per rarity tier

**Example**:
```json
{
  "stats": {
    "totalUniqueCards": 42,
    "totalCards": 68,
    "shinyCount": 3,
    "rarityBreakdown": {
      "Common": 18,
      "Uncommon": 12,
      "Rare": 8,
      "Epic": 3,
      "Legendary": 1
    }
  }
}
```

---

## Achievement System Integration

**Collection Achievements**:
- "First Steps" - Open your first pack ✅
- "Shiny Hunter" - Acquire your first shiny card ✨
- "Element Master" - Complete any element collection 🔥💧🌍
- "Base Set Master" - Complete all 140 Base Set cards 🏆
- "The Collector" - Own 500 total cards (including duplicates)
- "Rainbow Collection" - Own at least 1 card from every element

**Implementation**: Store in `player_collections.achievements` object, check on card acquisition.

---

## Unity CollectionTracker.cs Pseudocode

```csharp
public class CollectionTracker : MonoBehaviour {
    private Dictionary<string, OwnedCard> ownedCards = new Dictionary<string, OwnedCard>();
    private SeriesManifest baseSetManifest;
    
    public async Task Initialize() {
        // Load collection from Nakama
        var storageData = await NakamaClient.ReadStorageObjects("player_collections");
        ownedCards = DeserializeCollection(storageData);
        
        // Load series manifest for milestones
        baseSetManifest = LoadSeriesManifest("base-set");
    }
    
    public void AddCard(CardInstance card) {
        bool isNew = !ownedCards.ContainsKey(card.collectionNumber);
        
        if (isNew) {
            ownedCards[card.collectionNumber] = new OwnedCard(card);
            CheckMilestones();
            CheckElementMastery(card.element);
        } else {
            ownedCards[card.collectionNumber].quantity++;
        }
        
        SaveCollection();
    }
    
    private void CheckMilestones() {
        int uniqueCount = ownedCards.Count;
        
        // Check each milestone in manifest
        foreach (var milestone in baseSetManifest.collectionMilestones) {
            if (uniqueCount >= milestone.cardsRequired && !milestone.claimed) {
                GrantMilestoneReward(milestone);
                milestone.claimed = true;
            }
        }
    }
    
    public int GetElementProgress(string element) {
        int owned = ownedCards.Count(c => c.Value.element == element);
        int total = baseSetManifest.elementBreakdown[element];
        return (owned * 100) / total;
    }
}
```

---

## F2P Collection Timeline (Detailed)

**Daily Gold Earnings** (500 Gold/day from quests + dailies):
- Week 1: 3,500 Gold → 3× Standard Packs → ~12-15 unique cards
- Month 1: 15,000 Gold → 15× Standard Packs → ~40-50 unique cards (+ starter box, welcome pack, milestones)
- Month 3: 45,000 Gold → 45× Standard Packs → ~80-90 unique cards
- Month 6: 90,000 Gold → 90× Standard Packs → ~120-140 unique cards (100% completion)

**Milestones Accelerate**:
- 50 cards → free Rare Pack (1,500 Gold value)
- 75 cards → free Epic Pack (2,500 Gold value)
- 100 cards → free Legendary Pack (5,000 Gold value)
- Total milestone value: ~15,000 Gold equivalent

**Result**: F2P player completes Base Set in 5-6 months with consistent daily play.

---

## Summary

**Collection Tracking System**:
- ✅ Nakama storage schema defined
- ✅ Milestones documented (global + element mastery)
- ✅ Duplicate handling (quantity tracking, Phase 2 shards)
- ✅ Achievement integration
- ✅ Unity pseudocode (CollectionTracker.cs)
- ✅ F2P timeline validated (6 months to 100%)

**Next Implementation**:
1. Create Nakama RPC endpoint: `AddCardsToCollection(cardIds[])`
2. Implement milestone checking logic
3. Build collection UI (series checklist, element progress bars)
4. Create shiny card visual effects (animated borders, particle effects)
