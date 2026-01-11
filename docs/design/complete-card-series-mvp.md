# Complete Card Series - MVP (140 Cards)

**Last Updated**: January 11, 2026  
**Status**: CRITICAL - Defines all 140 cards for MVP, modular file structure  
**Related**: [starter-deck-design.md](starter-deck-design.md), [campaign-structure.md](campaign-structure.md), [deck-progression-rules.md](deck-progression-rules.md)

---

## Overview

**Total Cards**: 140 (expanded from original 100-card plan)  
**Rationale**: 120 minimum for variety, 140 optimal for meta diversity + future-proofing

**Goals**:
1. **Variety**: Players encounter new cards every 2-3 battles (40 Location campaign = 60+ cards seen)
2. **Discovery**: Meta evolves as players experiment with 140 combinations
3. **Future-Proof**: Room for nerfs/buffs without "dead" cards
4. **F2P Friendly**: 50% Commons/Uncommons (easy to collect), 15% Legendary+ (chase cards)

---

## Card Count by Rarity

| Rarity | Count | % of Total | Purpose | Example Cards |
|--------|-------|------------|---------|---------------|
| **Common (0★)** | 56 | 40% | Filler, deck volume, F2P accessible | Fire Scout, Water Scout, Earth Scout |
| **Uncommon (1★)** | 42 | 30% | Specialized troops, minor synergies | Goblin Raider, Sea Serpent, Boulder Beast |
| **Rare (2★)** | 25 | 18% | Named units, strong abilities | Ember Legionnaire, Frost Paladin, Rock Golem |
| **Epic (3★)** | 12 | 9% | Powerful heroes, deck anchors | Aria, Thalor, Gaia, Zephyr, Glacius |
| **Legendary (5★)** | 4 | 3% | Iconic heroes, endgame rewards | Ragnarok, Merlin, Terra, Leviathan |
| **Mythic (6★)** | 1 | <1% | Ultimate boss drop | Malakar (Demon Overlord, Location 40 reward) |

**Total**: 140 cards

**Rarity Point Budget Validation**:
- Level 1 (64 points): 1× Epic (8) + 56× Common (56) = **64 points** ✅
- Level 20 (144 points): 1× Legendary (16) + 1× Epic (8) + 6× Rare (24) + 96× Common/Uncommon (96) = **144 points** ✅
- Level 30 (184 points): 1× Mythic (32) + 1× Legendary (16) + 1× Epic (8) + 10× Rare (40) + 88× Common/Uncommon (88) = **184 points** ✅

---

## Card Count by Type

| Type | Count | Purpose | Examples |
|------|-------|---------|----------|
| **Heroes** | 35 | Deck leaders, unique abilities | Aria, Thalor, Gaia, Ragnarok, Merlin |
| **Units** | 70 | Combat troops (melee, ranged, flying) | Fire Soldier, Goblin Raider, Dragon Whelp |
| **Tactics** | 21 | Spells/scrolls (damage, heal, buff) | Fireball, Heal, Shield Wall, Lightning Bolt |
| **Buildings** | 14 | Economy cards (Phase 2 income, MVP = art/variety) | Barracks, Mage Tower, Temple, Monument |

**Total**: 140 cards

**Type Distribution by Rarity**:
- **Heroes**: 10 Common, 10 Uncommon, 8 Rare, 6 Epic, 4 Legendary, 1 Mythic = 35 (need leaders at all budgets)
- **Units**: 40 Common, 25 Uncommon, 12 Rare, 3 Epic = 70 (bulk of decks)
- **Tactics**: 5 Common, 6 Uncommon, 4 Rare, 3 Epic, 2 Legendary, 1 Mythic = 21 (high-impact, limited quantity)
- **Buildings**: 6 Common, 6 Uncommon, 2 Rare = 14 (mostly flavor for MVP)

---

## Card Count by Element

| Element | Count | Heroes | Units | Tactics | Buildings | Notes |
|---------|-------|--------|-------|---------|-----------|-------|
| **Fire** | 25 | 5 (Aria + 4 others) | 16 | 3 | 1 (Forge) | Aggressive playstyle |
| **Water** | 25 | 5 (Thalor + 4 others) | 16 | 3 | 1 (Aquarium) | Defensive/healing playstyle |
| **Earth** | 25 | 5 (Gaia + 4 others) | 16 | 3 | 1 (Quarry) | Balanced playstyle |
| **Lightning** | 15 | 4 (Ragnarok + 3) | 9 | 2 | 0 | Burst damage, expansion element |
| **Wind** | 15 | 4 (Zephyr + 3) | 9 | 2 | 0 | Speed/mobility, expansion element |
| **Frost** | 15 | 4 (Glacius + 3) | 9 | 2 | 0 | Control/slow, expansion element |
| **Neutral** | 20 | 8 (multi-element) | 0 | 6 (generic) | 12 (all buildings) | Multi-element support |

**Total**: 140 cards

**Starter Elements** (Fire/Water/Earth): 75 cards (54% of pool)  
**Expansion Elements** (Lightning/Wind/Frost): 45 cards (32% of pool)  
**Neutral**: 20 cards (14% of pool)

---

## Modular File Structure

**Problem**: Monolithic starter-cards.json (600+ lines) will become 3,000+ lines for 140 cards (unmaintainable).

**Solution**: Break into logical groups by element + type.

### **Proposed Directory Structure**

```
docs/specs/cards/
├── README.md                      # Card loading strategy, validation rules
├── _schema.json                   # JSON schema for card validation
├── fire/
│   ├── fire-heroes.json           # 5 Fire heroes (Aria + 4 others)
│   ├── fire-units-common.json     # 10 Common Fire units
│   ├── fire-units-uncommon.json   # 4 Uncommon Fire units
│   ├── fire-units-rare.json       # 2 Rare Fire units
│   ├── fire-tactics.json          # 3 Fire tactics (Fireball, Flame Shield, etc.)
│   └── fire-buildings.json        # 1 Fire building (Forge)
├── water/
│   ├── water-heroes.json          # 5 Water heroes (Thalor + 4 others)
│   ├── water-units-common.json    # 10 Common Water units
│   ├── water-units-uncommon.json  # 4 Uncommon Water units
│   ├── water-units-rare.json      # 2 Rare Water units
│   ├── water-tactics.json         # 3 Water tactics (Tidal Wave, Aqua Shield, etc.)
│   └── water-buildings.json       # 1 Water building (Aquarium)
├── earth/
│   ├── earth-heroes.json          # 5 Earth heroes (Gaia + 4 others)
│   ├── earth-units-common.json    # 10 Common Earth units
│   ├── earth-units-uncommon.json  # 4 Uncommon Earth units
│   ├── earth-units-rare.json      # 2 Rare Earth units
│   ├── earth-tactics.json         # 3 Earth tactics (Earthquake, Stone Shield, etc.)
│   └── earth-buildings.json       # 1 Earth building (Quarry)
├── lightning/
│   ├── lightning-heroes.json      # 4 Lightning heroes (Ragnarok + 3 others)
│   ├── lightning-units.json       # 9 Lightning units (all rarities)
│   └── lightning-tactics.json     # 2 Lightning tactics
├── wind/
│   ├── wind-heroes.json           # 4 Wind heroes (Zephyr + 3 others)
│   ├── wind-units.json            # 9 Wind units (all rarities)
│   └── wind-tactics.json          # 2 Wind tactics
├── frost/
│   ├── frost-heroes.json          # 4 Frost heroes (Glacius + 3 others)
│   ├── frost-units.json           # 9 Frost units (all rarities)
│   └── frost-tactics.json         # 2 Frost tactics
├── neutral/
│   ├── neutral-heroes.json        # 8 Neutral heroes (multi-element)
│   ├── neutral-tactics.json       # 6 Neutral tactics (Heal, Shield, etc.)
│   └── neutral-buildings.json     # 12 Neutral buildings (Barracks, Tower, etc.)
└── compiled/
    └── all-cards-compiled.json    # Auto-generated master file (Unity build process)
```

**Benefits**:
- ✅ **Maintainability**: Edit fire-heroes.json (50 lines) vs all-cards.json (3,000 lines)
- ✅ **Collaboration**: Multiple designers can edit different elements simultaneously
- ✅ **Version Control**: Git diffs show "changed fire-units-common.json" not "changed line 1,247"
- ✅ **Testing**: Load fire/ folder only for Fire deck testing
- ✅ **Expansion**: Add dark/ folder for Phase 2 without touching existing files

---

## Card Loading Strategy (Unity)

### **Option 1: Runtime Loading** (Recommended for MVP)

**How It Works**:
1. Unity stores cards as ScriptableObjects in `Assets/Resources/Cards/`
2. Mirror structure: `Resources/Cards/fire/fire-heroes.asset`, etc.
3. CardManager.cs loads all cards at startup:
   ```csharp
   void Awake()
   {
       CardData[] fireHeroes = Resources.LoadAll<CardData>("Cards/fire/fire-heroes");
       CardData[] waterUnits = Resources.LoadAll<CardData>("Cards/water/water-units-common");
       // ... etc for all 25 files
       
       allCards.AddRange(fireHeroes);
       allCards.AddRange(waterUnits);
       // Total: 140 cards loaded into memory (~2-5MB)
   }
   ```

**Pros**:
- Simple to implement (Unity handles file loading)
- Easy debugging (load fire/ only during Fire deck testing)
- Fast iteration (edit ScriptableObject, hit Play)

**Cons**:
- 25 file loads at startup (~100-200ms on mobile)
- Cannot hot-reload cards without app restart

---

### **Option 2: Compiled JSON** (Phase 2 optimization)

**How It Works**:
1. Build script merges all 25 JSON files → `all-cards-compiled.json`
2. Unity loads single JSON at startup (faster)
3. Deserialize into CardData objects

**Build Script** (PowerShell):
```powershell
# compile-cards.ps1
$output = @()
Get-ChildItem -Path "docs/specs/cards/" -Recurse -Filter "*.json" -Exclude "_schema.json" | ForEach-Object {
    $json = Get-Content $_.FullName | ConvertFrom-Json
    $output += $json
}
$output | ConvertTo-Json -Depth 10 | Out-File "docs/specs/cards/compiled/all-cards-compiled.json"
```

**Pros**:
- Single file load (~10-20ms vs 100-200ms)
- Easier to version control compiled output
- Can compress JSON (gzip reduces 3MB → 500KB)

**Cons**:
- Requires build step (forget to run = stale data)
- Harder to debug (must trace back to source file)

---

### **Recommendation: Hybrid Approach**

**Development** (MVP Phase):
- Use **Runtime Loading** (Option 1)
- Load individual JSON files (easy editing, fast iteration)
- CardManager.cs validates all cards at startup (catches typos)

**Production** (Phase 1.1+):
- Use **Compiled JSON** (Option 2)
- Build script runs on Unity pre-build hook
- Shipped game loads single compressed JSON (faster startup)

---

## Card Naming Convention

**Format**: `{CATEGORY}_{NAME}_{VARIANT}`

**Examples**:
- `HERO_ARIA_FLAME_KNIGHT` (Epic Fire hero)
- `UNIT_FIRE_SOLDIER` (Common Fire unit)
- `UNIT_GOBLIN_RAIDER` (Uncommon neutral unit)
- `TACTIC_FIREBALL` (Rare Fire tactic)
- `BUILDING_BARRACKS` (Common neutral building)

**Why This Format**:
- ✅ Searchable: `grep "HERO_"` finds all heroes
- ✅ Sortable: `HERO_` sorts before `UNIT_`
- ✅ Collision-Free: `UNIT_FIRE_SOLDIER` ≠ `HERO_FIRE_KNIGHT`
- ✅ Unity-Friendly: Matches C# enum convention

---

## Card Definition Template

**JSON Schema** (all cards follow this format):

```json
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "name": "Aria, Flame Knight",
  "type": "Hero",
  "element": "Fire",
  "rarity": "Epic",
  "rarityStars": 3,
  "rarityPoints": 8,
  
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
      "usesPerBattle": 99,
      "description": "Deal 70 damage to target enemy. Splash 20 damage to adjacent enemies.",
      "targetType": "SingleEnemy",
      "aoeRadius": 1
    },
    {
      "abilityId": "ABILITY_INFERNO_AURA",
      "name": "Inferno Aura",
      "type": "Passive",
      "description": "All Fire units gain +15% ATK (Phase 2 feature).",
      "buffType": "Attack",
      "buffValue": 0.15,
      "affectedUnits": "Fire"
    }
  ],
  
  "tacticSlots": 3,
  "lore": "A legendary warrior who commands the eternal flames...",
  "artAsset": "Art/Cards/Heroes/Fire/aria_flame_knight.png",
  "voicelineActor": "Jane Doe",
  "collectionTier": 1,
  "packSources": ["Standard Pack", "Element Booster (Fire)", "Hero Pack"],
  "campaignDrops": ["Location 10 (Goblin Warlord boss)", "New Game+ any boss"],
  
  "designNotes": "Starter Fire hero. High ATK, low DEF = aggressive playstyle. Blazing Strike is single-target burst (counters high-HP tanks). Inferno Aura is deferred to Phase 2 (element synergies)."
}
```

---

## Card Distribution Goals

### **By Acquisition Source**

| Source | Cards Available | Rarity Distribution | Purpose |
|--------|-----------------|---------------------|---------|
| **Starter Decks** | 45 (15 Fire, 15 Water, 15 Earth) | 3 Epic, 9 Rare, 18 Uncommon, 15 Common | Teach basics |
| **Welcome Pack** | 5 (1 hero guaranteed) | 50% Common, 30% Uncommon, 15% Rare, 4% Epic, 1% Legendary | Hook moment |
| **Campaign Drops** | 60 (Locations 1-40) | 20 Common, 15 Uncommon, 15 Rare, 8 Epic, 2 Legendary | Progression rewards |
| **Daily Login** | 7 (Day 1-7) | 5 Common, 1 Uncommon, 1 Epic (Day 7) | Retention |
| **Weekly Quests** | 5 (5/5 quest complete) | 3 Uncommon, 1 Rare, 1 Epic | Engagement |
| **Gold Purchase** | 140 (all cards) | Varies by pack type | F2P + whale monetization |

**F2P Player (2 weeks)**:
- Starter: 15 cards
- Welcome Pack: 5 cards
- Campaign: 30 cards (halfway)
- Daily Login: 7 cards
- Weekly Quests: 5 cards
- **Total**: 62 cards (44% of 140) ✅ (enough for competitive deck)

**Whale Player (2 weeks)**:
- All above + 50,000 Gold spent on packs (~50 packs = 250 cards, duplicates converted to shards)
- **Collection**: 120/140 unique cards (86%) ✅ (near-complete, still chasing Mythic/Legendary)

---

## Next Steps

### **Immediate (This Session)**:
1. ✅ Define complete 140-card series breakdown
2. ⏳ Create directory structure: `docs/specs/cards/{element}/{type}.json`
3. ⏳ Define all Fire cards (25 cards: 5 heroes, 16 units, 3 tactics, 1 building)
4. ⏳ Define all Water cards (25 cards: 5 heroes, 16 units, 3 tactics, 1 building)
5. ⏳ Define all Earth cards (25 cards: 5 heroes, 16 units, 3 tactics, 1 building)

### **Follow-Up (Next Session)**:
6. Define Lightning/Wind/Frost elements (15 each, 45 total)
7. Define Neutral cards (20 total: 8 heroes, 6 tactics, 12 buildings)
8. Create `_schema.json` for JSON validation
9. Create `README.md` in `cards/` with loading strategy
10. Write build script: `compile-cards.ps1`

### **Unity Implementation**:
- Import JSON → ScriptableObjects (CardData.cs)
- CardManager.cs: Load all cards at startup, cache in Dictionary<string, CardData>
- Validation: Ensure all cardIds unique, rarity budgets valid

---

**Design Philosophy**: "140 cards is the sweet spot - enough variety for meta evolution, small enough to balance in MVP timeline."
