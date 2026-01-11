# Card Architecture: Codex + Series System

**Last Updated**: January 11, 2026  
**Status**: CRITICAL DESIGN - Defines card metadata organization, series expansion strategy  
**Related**: [complete-card-series-mvp.md](complete-card-series-mvp.md), [starter-deck-design.md](starter-deck-design.md)

---

## Design Philosophy

**Inspired By**: Pokemon TCG (Base Set, Jungle, Fossil series) + Magic: The Gathering (Alpha, Beta, Unlimited, expansion sets)

**Core Principles**:
1. **Codex = Source of Truth** - Cards defined ONCE with canonical stats, never duplicated
2. **Products Reference Codex** - Boxes, packs, decks only store card IDs + quantities/rates
3. **Series-First Organization** - Cards belong to series (Base Set, Elemental Fury, etc.)
4. **Collection Numbering** - Every card has series number (e.g., "BS-001/140" = Base Set #1 of 140)
5. **Future-Proof Expansion** - Adding Series 2 doesn't touch Series 1 files

---

## Entity Types (Terminology)

### **Codex** (Canonical Card Definitions)
- **What**: Single source of truth for all card stats, abilities, art, lore
- **Where**: `docs/codex/{series}/{element}/`
- **Example**: `docs/codex/base-set/fire/HERO_ARIA_FLAME_KNIGHT.json`
- **Contains**: HP, Mana, ATK, DEF, abilities, art assets, voicelines, collection number
- **Never Contains**: Drop rates, pack probabilities, deck composition (those are in products)

### **Box** (Starter Products)
- **What**: Pre-constructed card collections given to new players or sold
- **Where**: `docs/products/boxes/`
- **Example**: `fire-starter-box.json`
- **Contains**: List of card IDs + quantities (e.g., "HERO_ARIA_FLAME_KNIGHT × 1")
- **Types**: 
  - **Starter Boxes** (free, tutorial reward, 15 cards)
  - **Theme Boxes** (paid, 30 cards around archetype like "Dragon's Fury")
  - **Complete Decks** (paid, 40-50 cards, ready-to-play competitive deck)

### **Pack** (Randomized Booster Products)
- **What**: Randomized card bundles with rarity-based drop rates
- **Where**: `docs/products/packs/`
- **Example**: `standard-pack.json`
- **Contains**: 
  - Card pool (which cards can drop, e.g., "all Base Set cards")
  - Rarity distribution (e.g., "5 cards: 3 Common, 1 Uncommon, 1 Rare+")
  - Hero guarantee rules (e.g., "1 hero guaranteed per pack")
  - Shiny chance (e.g., "10% per card")
- **Types**: Standard, Element Booster, Rare, Epic, Legendary, Mythic

### **Deck** (Player Gameplay Loadout)
- **What**: 20-50 card collections players build for battles
- **Where**: Player save data (not static files, runtime only)
- **Contains**: List of card IDs + validation rules (rarity budget, 3-of limit, 1 hero)
- **Types**: 
  - **Player Decks** (custom, saved in player account)
  - **AI Enemy Decks** (campaign encounters, defined in `docs/campaign/`)
  - **Preset Decks** (optional templates for new players)

---

## Directory Structure (Series + Codex Architecture)

```
docs/
├── codex/                                    # Canonical card definitions (source of truth)
│   ├── README.md                             # Codex philosophy, card ID conventions
│   ├── _schema.json                          # JSON schema for card validation
│   │
│   ├── base-set/                             # Series 1: "Base Set" (140 cards, MVP)
│   │   ├── series-manifest.json              # Series metadata (name, release date, card count)
│   │   ├── fire/
│   │   │   ├── HERO_ARIA_FLAME_KNIGHT.json              # BS-001 (Base Set card #1)
│   │   │   ├── HERO_RAGNAR_INFERNO_BERSERKER.json       # BS-002
│   │   │   ├── HERO_CINDER_FLAME_MAGE.json              # BS-003
│   │   │   ├── HERO_BLAZE_DRAGON_RIDER.json             # BS-004
│   │   │   ├── HERO_EMBER_PHOENIX_GUARDIAN.json         # BS-005
│   │   │   ├── UNIT_FIRE_SOLDIER.json                   # BS-006 (Common)
│   │   │   ├── UNIT_EMBER_SCOUT.json                    # BS-007
│   │   │   ├── UNIT_FLAME_IMP.json                      # BS-008
│   │   │   └── ... (18 more Fire cards)
│   │   ├── water/
│   │   │   ├── HERO_THALOR_TIDE_GUARDIAN.json           # BS-026
│   │   │   └── ... (24 more Water cards)
│   │   ├── earth/
│   │   │   ├── HERO_GAIA_STONE_SENTINEL.json            # BS-051
│   │   │   └── ... (24 more Earth cards)
│   │   ├── lightning/
│   │   │   ├── HERO_RAGNAROK_GOD_OF_THUNDER.json        # BS-076 (Legendary)
│   │   │   └── ... (14 more Lightning cards)
│   │   ├── wind/
│   │   │   ├── HERO_ZEPHYR_SKY_SOVEREIGN.json           # BS-091
│   │   │   └── ... (14 more Wind cards)
│   │   ├── frost/
│   │   │   ├── HERO_GLACIUS_ICE_KING.json               # BS-106
│   │   │   └── ... (14 more Frost cards)
│   │   └── neutral/
│   │       ├── HERO_SENTINEL_GUARDIAN.json              # BS-121
│   │       ├── TACTIC_HEAL.json                         # BS-122
│   │       ├── BUILDING_BARRACKS.json                   # BS-135
│   │       └── ... (19 more Neutral cards)
│   │
│   ├── elemental-fury/                       # Series 2: "Elemental Fury" (Phase 1.1, 80 cards)
│   │   ├── series-manifest.json              # EF series metadata
│   │   ├── fire/
│   │   │   ├── HERO_VULCAN_FORGE_MASTER.json            # EF-001
│   │   │   └── ... (new Fire cards for Series 2)
│   │   └── ... (other elements)
│   │
│   └── heroes-ascended/                      # Series 3: "Heroes Ascended" (Phase 2, 100 cards)
│       ├── series-manifest.json
│       └── ... (new elements like Dark, Light, Arcane)
│
├── products/                                  # Card products (reference codex via IDs)
│   ├── boxes/                                 # Starter boxes, theme boxes, complete decks
│   │   ├── fire-starter-box.json              # 15 cards (tutorial Fire choice)
│   │   ├── water-starter-box.json             # 15 cards (tutorial Water choice)
│   │   ├── earth-starter-box.json             # 15 cards (tutorial Earth choice)
│   │   ├── dragon-fury-theme-box.json         # 30-card Dragon-themed pre-con (Phase 1.1)
│   │   └── competitive-aggro-deck.json        # 50-card competitive deck (paid product)
│   │
│   ├── packs/                                 # Booster packs (define drop rates)
│   │   ├── welcome-pack.json                  # Tutorial bonus pack (5 cards, 1 hero guaranteed)
│   │   ├── standard-pack.json                 # 5 cards, 1,000 Gold
│   │   ├── element-booster-fire.json          # 5 cards, Fire-only pool
│   │   ├── element-booster-water.json
│   │   ├── element-booster-earth.json
│   │   ├── rare-pack.json                     # 5 cards, guaranteed Rare+
│   │   ├── epic-pack.json                     # 5 cards, guaranteed Epic+
│   │   ├── hero-pack.json                     # 5 cards, 2 heroes guaranteed
│   │   ├── legendary-pack.json                # 5 cards, guaranteed Legendary
│   │   └── mythic-pack.json                   # 5 cards, choice of 3 Mythic heroes
│   │
│   └── daily-login-rewards.json               # Day 1-7 rewards (reference pack IDs)
│
├── campaign/                                  # AI enemy decks (campaign encounters)
│   ├── location-01-goblin-camp.json           # Enemy deck for Location 1 (3 cards)
│   ├── location-10-goblin-warlord-boss.json   # Boss deck (6 cards)
│   └── ... (40 location decks)
│
└── collection/                                # Collection tracking metadata
    ├── series-checklist-base-set.json         # "Collect all 140 Base Set cards"
    └── achievements.json                      # "Complete Fire element", "Own all Legendaries"
```

---

## Codex Schema (Card Definition Format)

**File**: `docs/codex/_schema.json`

Every card in the codex follows this structure:

```json
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "collectionNumber": "BS-001",
  "series": {
    "seriesId": "base-set",
    "seriesName": "Base Set",
    "cardNumber": 1,
    "totalCards": 140,
    "releaseDate": "2026-06-01"
  },
  
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
  "lore": "A legendary warrior who commands the eternal flames...",
  
  "art": {
    "portraitAsset": "Art/Cards/BS-001_Aria_Portrait.png",
    "fullArtAsset": "Art/Cards/BS-001_Aria_FullArt.png",
    "shinyPortrait": "Art/Cards/BS-001_Aria_Portrait_Shiny.png",
    "voicelineActor": "Jane Doe"
  },
  
  "gameplay": {
    "tacticSlots": 3,
    "deckBuildingRules": {
      "maxCopies": 1,
      "uniqueHero": true
    }
  },
  
  "acquisition": {
    "packSources": [
      "fire-starter-box",
      "standard-pack",
      "element-booster-fire",
      "hero-pack"
    ],
    "campaignDrops": [
      "location-10-goblin-warlord-boss"
    ],
    "dailyLoginRewards": [
      "day-7"
    ]
  },
  
  "meta": {
    "designNotes": "Starter Fire hero. High ATK, low DEF = glass cannon aggro.",
    "balanceHistory": [
      {"date": "2026-01-11", "change": "Initial design", "author": "Lead Designer"}
    ]
  }
}
```

**Key Fields**:
- `cardId`: Unique identifier (NEVER changes, used everywhere)
- `collectionNumber`: Human-readable series number ("BS-001" = Base Set #1)
- `series`: Metadata about which expansion this belongs to
- `acquisition`: Where players get this card (boxes, packs, campaign)
- `art.shinyPortrait`: Separate asset for shiny variant (10% chance)

---

## Series Manifest Schema

**File**: `docs/codex/base-set/series-manifest.json`

```json
{
  "seriesId": "base-set",
  "seriesName": "Base Set",
  "seriesCode": "BS",
  "releaseDate": "2026-06-01",
  "totalCards": 140,
  "description": "The foundational card series featuring Fire, Water, Earth, Lightning, Wind, and Frost elements.",
  
  "cardBreakdown": {
    "byRarity": {
      "Common": 56,
      "Uncommon": 42,
      "Rare": 25,
      "Epic": 12,
      "Legendary": 4,
      "Mythic": 1
    },
    "byElement": {
      "Fire": 25,
      "Water": 25,
      "Earth": 25,
      "Lightning": 15,
      "Wind": 15,
      "Frost": 15,
      "Neutral": 20
    },
    "byType": {
      "Hero": 35,
      "Unit": 70,
      "Tactic": 21,
      "Building": 14
    }
  },
  
  "collectionMilestones": [
    {"cardsOwned": 20, "reward": "500 Gold", "achievement": "Getting Started"},
    {"cardsOwned": 50, "reward": "Rare Pack", "achievement": "Collector"},
    {"cardsOwned": 100, "reward": "Epic Pack", "achievement": "Master Collector"},
    {"cardsOwned": 140, "reward": "Mythic Pack", "achievement": "Base Set Complete"}
  ],
  
  "packsAvailable": [
    "standard-pack",
    "element-booster-fire",
    "element-booster-water",
    "element-booster-earth",
    "rare-pack",
    "epic-pack",
    "hero-pack",
    "legendary-pack",
    "mythic-pack"
  ],
  
  "legalInFormats": ["Standard", "Unlimited"],
  "rotationDate": null
}
```

---

## Box Product Schema

**File**: `docs/products/boxes/fire-starter-box.json`

```json
{
  "productId": "fire-starter-box",
  "productName": "Fire Starter Box",
  "productType": "StarterBox",
  "price": {
    "gold": 0,
    "realMoney": 0
  },
  "acquisition": ["Tutorial Step 1 (choose Fire portal)"],
  
  "cardList": [
    {"cardId": "HERO_ARIA_FLAME_KNIGHT", "quantity": 1},
    {"cardId": "UNIT_EMBER_LEGIONNAIRE", "quantity": 3},
    {"cardId": "UNIT_FLAME_SENTINEL", "quantity": 3},
    {"cardId": "UNIT_FIRE_MAGE", "quantity": 3},
    {"cardId": "UNIT_FIRE_SOLDIER", "quantity": 2},
    {"cardId": "UNIT_EMBER_SCOUT", "quantity": 2},
    {"cardId": "TACTIC_FIREBALL", "quantity": 1}
  ],
  
  "totalCards": 15,
  "guaranteedRarities": {
    "Epic": 1,
    "Rare": 3,
    "Uncommon": 6,
    "Common": 5
  },
  
  "description": "Choose the path of fire and command Aria, Flame Knight, in devastating aggressive strategies.",
  "artAsset": "Art/Products/fire_starter_box.png"
}
```

**Key Points**:
- `cardList`: References codex via `cardId` (no duplicate stats)
- `quantity`: How many copies of each card
- Fixed contents (not randomized)

---

## Pack Product Schema

**File**: `docs/products/packs/standard-pack.json`

```json
{
  "packId": "standard-pack",
  "packName": "Standard Pack",
  "packType": "Booster",
  "price": {
    "gold": 1000,
    "realMoney": 0.99
  },
  
  "cardCount": 5,
  "cardPool": {
    "series": ["base-set"],
    "elements": ["Fire", "Water", "Earth", "Lightning", "Wind", "Frost", "Neutral"],
    "excludedCards": []
  },
  
  "rarityDistribution": [
    {"slot": 1, "rarities": ["Common"], "weights": [100]},
    {"slot": 2, "rarities": ["Common"], "weights": [100]},
    {"slot": 3, "rarities": ["Common", "Uncommon"], "weights": [70, 30]},
    {"slot": 4, "rarities": ["Uncommon"], "weights": [100]},
    {"slot": 5, "rarities": ["Rare", "Epic", "Legendary"], "weights": [85, 13, 2]}
  ],
  
  "guarantees": {
    "heroGuarantee": {
      "enabled": true,
      "minHeroes": 1,
      "logic": "If no hero in slots 1-4, slot 5 becomes random hero from card pool"
    },
    "shinyChance": {
      "enabled": true,
      "chancePerCard": 0.10,
      "logic": "Each card independently has 10% chance to be shiny variant"
    },
    "pitySystem": {
      "enabled": true,
      "epicPity": {"every": 10, "guarantee": "Epic+"},
      "legendaryPity": {"every": 50, "guarantee": "Legendary"}
    }
  },
  
  "description": "5 cards from the Base Set. Guaranteed 1 hero and at least 1 Rare+ card.",
  "artAsset": "Art/Products/standard_pack.png"
}
```

**Key Points**:
- `cardPool`: Which cards can appear (by series, element, rarity)
- `rarityDistribution`: Each slot has weighted rarity chances
- `guarantees`: Hero guarantee, shiny chance, pity system rules
- **No duplicate card stats** - pack logic queries codex at runtime

---

## Pack Product Schema (Element Booster)

**File**: `docs/products/packs/element-booster-fire.json`

```json
{
  "packId": "element-booster-fire",
  "packName": "Element Booster: Fire",
  "packType": "ElementBooster",
  "price": {
    "gold": 1500,
    "realMoney": 1.49
  },
  
  "cardCount": 5,
  "cardPool": {
    "series": ["base-set"],
    "elements": ["Fire"],
    "excludedCards": []
  },
  
  "rarityDistribution": [
    {"slot": 1, "rarities": ["Common", "Uncommon"], "weights": [60, 40]},
    {"slot": 2, "rarities": ["Common", "Uncommon"], "weights": [60, 40]},
    {"slot": 3, "rarities": ["Uncommon", "Rare"], "weights": [70, 30]},
    {"slot": 4, "rarities": ["Uncommon", "Rare"], "weights": [50, 50]},
    {"slot": 5, "rarities": ["Rare", "Epic", "Legendary"], "weights": [70, 25, 5]}
  ],
  
  "guarantees": {
    "heroGuarantee": {
      "enabled": true,
      "minHeroes": 1,
      "logic": "At least 1 Fire hero guaranteed"
    },
    "shinyChance": {
      "enabled": true,
      "chancePerCard": 0.10
    }
  },
  
  "description": "5 Fire element cards from the Base Set. Perfect for building aggressive decks.",
  "artAsset": "Art/Products/element_booster_fire.png"
}
```

---

## Deck Schema (Player-Created)

**File**: Runtime only (saved in player account, not static files)

```json
{
  "deckId": "player-deck-001",
  "deckName": "Fire Aggro Rush",
  "ownerPlayerId": "player_12345",
  "createdDate": "2026-06-15T10:30:00Z",
  "lastModified": "2026-06-20T14:22:00Z",
  
  "cardList": [
    {"cardId": "HERO_ARIA_FLAME_KNIGHT", "quantity": 1},
    {"cardId": "UNIT_EMBER_LEGIONNAIRE", "quantity": 3},
    {"cardId": "UNIT_GOBLIN_RAIDER", "quantity": 3},
    {"cardId": "UNIT_FIRE_SOLDIER", "quantity": 10},
    {"cardId": "TACTIC_FIREBALL", "quantity": 2},
    {"cardId": "UNIT_EMBER_SCOUT", "quantity": 11}
  ],
  
  "totalCards": 30,
  "rarityBudgetUsed": 46,
  "rarityBudgetMax": 104,
  "playerLevel": 10,
  
  "validation": {
    "valid": true,
    "errors": []
  },
  
  "stats": {
    "wins": 23,
    "losses": 12,
    "winRate": 0.657,
    "averageBattleLength": 8.3
  }
}
```

**Key Points**:
- References codex via `cardId`
- Validation happens at save (rarity budget, 3-of rule, 1 hero)
- Stats tracked per deck (wins, losses, win rate)

---

## Card Loading Strategy (Unity)

### **Startup Process**:

1. **Load Series Manifests** (know what series exist)
   ```csharp
   List<SeriesManifest> allSeries = LoadAllSeries("docs/codex/*/series-manifest.json");
   // Result: [Base Set, Elemental Fury, Heroes Ascended]
   ```

2. **Load Codex** (all cards from all series)
   ```csharp
   Dictionary<string, CardData> codex = new Dictionary<string, CardData>();
   
   foreach (var series in allSeries)
   {
       var cards = LoadCardsFromSeries(series.seriesId);
       foreach (var card in cards)
       {
           codex[card.cardId] = card; // HERO_ARIA_FLAME_KNIGHT → CardData
       }
   }
   // Result: 140 cards in memory (Base Set only for MVP)
   ```

3. **Load Products** (boxes, packs)
   ```csharp
   Dictionary<string, BoxProduct> boxes = LoadAllBoxes("docs/products/boxes/");
   Dictionary<string, PackProduct> packs = LoadAllPacks("docs/products/packs/");
   ```

4. **Ready to Play**
   - Tutorial Step 1: Open "fire-starter-box" → Query codex for card IDs → Grant 15 cards
   - Player opens pack: Roll rarities → Query codex for matching cards → Grant random cards

---

### **Collection Tracking**:

**Player Collection** (runtime, saved in Nakama):
```json
{
  "playerId": "player_12345",
  "collection": {
    "HERO_ARIA_FLAME_KNIGHT": {
      "owned": 2,
      "shiny": 1,
      "firstAcquired": "2026-06-15T10:30:00Z"
    },
    "UNIT_FIRE_SOLDIER": {
      "owned": 15,
      "shiny": 0,
      "firstAcquired": "2026-06-15T10:31:00Z"
    }
  },
  
  "seriesProgress": {
    "base-set": {
      "cardsOwned": 45,
      "totalCards": 140,
      "completionPercent": 32.1,
      "missingCards": ["HERO_BLAZE_DRAGON_RIDER", "HERO_RAGNAROK_GOD_OF_THUNDER", ...]
    }
  },
  
  "achievements": [
    {"achievementId": "base-set-20-cards", "completed": true, "date": "2026-06-16"},
    {"achievementId": "base-set-50-cards", "completed": false}
  ]
}
```

**Collection UI**:
- "You own 45/140 Base Set cards (32%)"
- "Missing: HERO_BLAZE_DRAGON_RIDER (Legendary), ..."
- Filter by series, element, rarity, owned/missing
- Click card → Show acquisition sources ("Available in: Standard Pack, Hero Pack, Location 30 boss")

---

## Expansion Strategy (Adding Series 2)

**Phase 1.1**: "Elemental Fury" (80 cards, 3 months post-MVP)

1. Create new series folder:
   ```
   docs/codex/elemental-fury/
   ├── series-manifest.json (EF series, 80 cards)
   ├── fire/
   │   ├── HERO_VULCAN_FORGE_MASTER.json (EF-001)
   │   └── ...
   └── ... (new cards for all elements)
   ```

2. Create new packs:
   ```
   docs/products/packs/elemental-fury-pack.json (card pool = elemental-fury series only)
   ```

3. Update collection UI:
   - "Base Set: 140/140 (100%) ✅"
   - "Elemental Fury: 12/80 (15%) ⏳"

**NO changes to Base Set files** - completely separate, clean expansion.

---

## Card Numbering Convention

### **Base Set** (BS-001 to BS-140):
- Fire: BS-001 to BS-025 (25 cards)
- Water: BS-026 to BS-050 (25 cards)
- Earth: BS-051 to BS-075 (25 cards)
- Lightning: BS-076 to BS-090 (15 cards)
- Wind: BS-091 to BS-105 (15 cards)
- Frost: BS-106 to BS-120 (15 cards)
- Neutral: BS-121 to BS-140 (20 cards)

### **Elemental Fury** (EF-001 to EF-080):
- Fire: EF-001 to EF-015 (15 cards)
- ... (new elements, variants)

### **Heroes Ascended** (HA-001 to HA-100):
- Dark: HA-001 to HA-020 (20 cards)
- Light: HA-021 to HA-040 (20 cards)
- ... (new elements)

---

## Benefits of This Architecture

✅ **Codex = Single Source of Truth**
- Change Aria's stats → Edit 1 file (`HERO_ARIA_FLAME_KNIGHT.json`)
- No duplicate data in boxes/packs/decks

✅ **Products Reference Codex**
- Packs define drop rates, NOT card stats
- Boxes define contents, NOT card stats
- Easy to add new packs ("Fire Mega Pack" = change drop rates, not cards)

✅ **Series Expansion**
- Add Series 2 → New folder, no touching Series 1
- Collection UI auto-updates (shows new series)
- Players can filter by series ("Show me Base Set only")

✅ **Collection Tracking**
- "You own 45/140 Base Set cards"
- "You own 12/80 Elemental Fury cards"
- Achievements per series ("Complete Base Set Fire element")

✅ **Monetization**
- Sell themed boxes ("Dragon Fury: 30 cards, all Dragon-type")
- Sell complete decks ("Pro Aggro Fire: 50 cards, competitive-ready")
- Packs reference series (can sell "Legacy Pack" = random card from any series)

---

## Next Steps (Implementation)

### **Immediate** (This Session):
1. ✅ Design architecture (this document)
2. ⏳ Create Base Set series manifest
3. ⏳ Migrate fire-heroes.json → individual codex files (BS-001 to BS-005)
4. ⏳ Create fire-starter-box.json (references codex)
5. ⏳ Create standard-pack.json (drop rates + hero guarantee)

### **Follow-Up** (Next Session):
6. Define all 140 Base Set cards (migrate to codex structure)
7. Create all box products (starter boxes, theme boxes)
8. Create all pack products (Standard, Element Boosters, Rare/Epic/Legendary)
9. Write Unity CardManager.cs (load codex, query by ID)
10. Write Unity PackOpener.cs (roll rarities, query codex, grant cards)

---

**Design Philosophy**: "Codex is the bible. Products are prayers that reference the bible. Never duplicate scripture."
