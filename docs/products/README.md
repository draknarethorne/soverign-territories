# Products System Documentation

## Overview
The Sovereign Territories product system separates **card definitions** (codex) from **acquisition methods** (products). This ensures cards are defined once and referenced by products.

## Product Types

### 1. Starter Boxes (3 total)
**Purpose**: Tutorial rewards, pre-constructed decks for new players

**Files**:
- [fire-starter-box.json](boxes/fire-starter-box.json) - Aria + 14 Fire support cards
- [water-starter-box.json](boxes/water-starter-box.json) - Thalor + 14 Water support cards
- [earth-starter-box.json](boxes/earth-starter-box.json) - Gaia + 14 Earth support cards

**Key Features**:
- Fixed card list (15 cards each)
- Free (tutorial reward)
- Pre-balanced for learning (1 Epic hero + 9 Common + 3 Uncommon + 2 Rare)
- Recommended deck included for immediate play

**Player Experience**:
1. Complete tutorial → choose element (Fire/Water/Earth)
2. Receive starter box → auto-build deck
3. Play first battle with pre-constructed deck

---

### 2. Booster Packs (10 total)

#### **Universal Packs** (Entry-level)
- **Welcome Pack** ([welcome-pack.json](packs/welcome-pack.json))
  - 5 cards, guaranteed Uncommon+ hero
  - Tutorial reward (1× limit)
  - Perfect for new players
  
- **Standard Pack** ([standard-pack.json](packs/standard-pack.json))
  - 5 cards, guaranteed Uncommon+
  - 1,000 Gold / 100 Gems / $0.99
  - Default pack for F2P progression
  - **Pity System**: Epic every 10 packs, Legendary every 50 packs

#### **Element Boosters** (Targeted acquisition)
- **Fire Element Booster** ([element-booster-fire.json](packs/element-booster-fire.json))
- **Water Element Booster** ([element-booster-water.json](packs/element-booster-water.json))
- **Earth Element Booster** ([element-booster-earth.json](packs/element-booster-earth.json))
  - 5 cards, Fire/Water/Earth only
  - 1,500 Gold / 150 Gems / $1.49
  - Higher rarity rates for element-specific cards
  - 12% shiny chance (vs 10% standard)
  - **Milestone Reward**: Free booster when completing element collection (25 cards)

#### **Premium Packs** (Whale-tier)
- **Hero Pack** ([hero-pack.json](packs/hero-pack.json))
  - 4,000 Gold / $3.99
  - Guaranteed 2 heroes (Uncommon+ and Rare+)
  - 15% shiny chance
  
- **Rare Pack** ([rare-pack.json](packs/rare-pack.json))
  - 3,000 Gold / $2.99
  - All 5 cards guaranteed Rare+
  - Unlocks at Level 15 (+ free reward pack)
  
- **Epic Pack** ([epic-pack.json](packs/epic-pack.json))
  - 5,000 Gold / $4.99
  - All 5 cards guaranteed Epic+
  - Unlocks at Level 20 (+ free reward pack)
  
- **Legendary Pack** ([legendary-pack.json](packs/legendary-pack.json))
  - 10,000 Gold / $9.99
  - Guaranteed 1 Legendary + 4 Epic+
  - Unlocks at Level 25
  - **Milestone Reward**: Free pack at 100 Base Set cards
  
- **Mythic Pack** ([mythic-pack.json](packs/mythic-pack.json))
  - 20,000 Gold / $19.99
  - **CHOICE CARD**: Malakar, Demon Overlord (BS-128)
  - 4 additional Epic+ cards
  - Unlocks at Level 30
  - **Milestone Reward**: Complete all 140 Base Set → free Mythic Pack
  - 30% shiny chance
  - 1× purchase limit

---

## Pity System

**Scope**: Tracks across all universal packs (Standard, Element Boosters)

**Guarantees**:
- **Epic**: Every 10 packs without an Epic → next pack guarantees Epic+
- **Legendary**: Every 50 packs without a Legendary → next pack guarantees Legendary

**Tracked Packs**: `standard-pack`, `element-booster-fire`, `element-booster-water`, `element-booster-earth`

**Not Tracked**: Premium packs (Hero/Rare/Epic/Legendary/Mythic) have their own guarantees

**Example**:
```
Player opens:
- 5× Standard Pack → no Epic
- 3× Fire Element Booster → no Epic
- 2× Water Element Booster → no Epic
Total = 10 packs → NEXT PACK (any tracked type) guarantees Epic+
```

---

## Shiny Variants

**Shiny Chance by Pack**:
- Standard: 10%
- Element Boosters: 12%
- Hero Pack: 15%
- Rare Pack: 18%
- Epic Pack: 20%
- Legendary Pack: 25%
- Mythic Pack: 30%

**Shiny Implementation**:
- Same cardId (no separate "HERO_ARIA_SHINY")
- Different art asset path: `BS-001_Aria_Portrait_Shiny.png`
- Collection tracks: "Regular" + "Shiny" versions
- No gameplay difference (cosmetic only)

---

## Monetization Strategy

### F2P Path (80% content accessible)
- **Free Packs**: Welcome Pack, Daily Login (Standard Pack every 7 days)
- **Gold Earning**: 500 Gold/day from quests → 2 Standard Packs/day
- **Element Completion**: Free Element Booster when completing 25 cards
- **Milestone Rewards**: Free Rare/Epic/Legendary packs at levels 15/20/25
- **Final Milestone**: Complete 140 cards → free Mythic Pack (Malakar)

**F2P Timeline** (casual play):
- Week 1: Starter Box + Welcome Pack + 10 Standard Packs = ~20 unique cards
- Month 1: 60 Standard Packs + milestones = ~60 unique cards (40% complete)
- Month 3: 180 Standard Packs + all milestones = ~100 unique cards (70% complete)
- Month 6: 360 Standard Packs + grind = 140 cards (100% complete, claim Malakar)

### Mid-Tier Spender ($10-30/month)
- **Recommended**: 10× Standard Packs ($10) + Element Boosters for favorite element
- **Accelerates**: Collection to 50% in 2 weeks, 100% in 2-3 months
- **Best Value**: Epic Pack at Level 20 ($5 for 5 Epic+ cards)

### Whale ($50+/month)
- **Full Set Speed**: 1-2 weeks via Legendary/Mythic Packs
- **Shiny Hunting**: Premium packs have higher shiny rates (18-30%)
- **Collection Flexing**: Multiple Mythic Packs to get shiny Malakar

---

## Product Creation Guidelines

### Adding New Packs (Series 2+)
1. Copy template from existing pack
2. Update `series` field: `"series": "elemental-fury"`
3. Update `cardPool`: `"cardPool": "elemental-fury-all"`
4. Maintain rarity distribution ratios
5. Scale prices for power creep (Series 2 Standard = 1,200 Gold?)

### Product Schema
```json
{
  "productId": "unique-kebab-case-id",
  "productName": "Display Name",
  "productType": "booster-pack | starter-box | specialty-pack",
  "series": "base-set | elemental-fury | heroes-ascended",
  "element": "Fire | Water | Earth | ...",
  "price": { "gold": 0, "gems": 0, "realMoney": {"usd": 0} },
  "cardsPerPack": 5,
  "cardPool": "base-set-all | base-set-fire-only | ...",
  "guarantees": [ { "slot": 1-5, "minimumRarity": "Rare", ... } ],
  "rarityDistribution": { "Common": {"weight": 65, ...}, ... },
  "specialFeatures": { "shinyChance": 10, "heroBoost": false },
  "pitySystem": { "enabled": true, "epicGuaranteeAfter": 10 },
  "availability": { "unlockLevel": 1, "purchaseLimit": null }
}
```

---

## Daily Login Rewards

**File**: `docs/products/rewards/daily-login-rewards.json` (to be created)

**Structure**:
```json
{
  "day1": { "gold": 100 },
  "day2": { "gold": 150 },
  "day3": { "gold": 200, "pack": "standard-pack" },
  "day4": { "gold": 250 },
  "day5": { "gold": 300 },
  "day6": { "gold": 400 },
  "day7": { "pack": "rare-pack", "gems": 50 }
}
```

**Cycle**: Resets every 7 days  
**Missed Days**: Do NOT reset counter (encourages consistency without punishing breaks)

---

## Collection Milestones

**Triggers** (defined in [series-manifest.json](../codex/base-set/series-manifest.json)):

| Milestone | Reward | Source |
|---|---|---|
| 10 cards | 250 Gold | Base Set manifest |
| 25 cards | Standard Pack | Base Set manifest |
| 50 cards | Rare Pack | Base Set manifest |
| 75 cards | Epic Pack | Base Set manifest |
| 100 cards | Legendary Pack | legendary-pack.json |
| 140 cards | Mythic Pack + "Base Set Master" title | mythic-pack.json |
| Complete Fire (25) | "Ember Legion Champion" + Fire Booster | element-booster-fire.json |
| Complete Water (25) | "Tidal Order Champion" + Water Booster | element-booster-water.json |
| Complete Earth (25) | "Stone Compact Champion" + Earth Booster | element-booster-earth.json |

---

## Unity Integration (Phase 2)

### PackOpener.cs Pseudocode
```csharp
public class PackOpener {
    public async Task<List<CardInstance>> OpenPack(string productId) {
        var product = LoadProductDefinition(productId);
        var results = new List<CardInstance>();
        
        for (int slot = 1; slot <= product.cardsPerPack; slot++) {
            var guarantee = product.guarantees.Find(g => g.slot == slot);
            var card = RollCard(product.cardPool, product.rarityDistribution, guarantee);
            
            // Check shiny
            if (Random.Range(0, 100) < product.specialFeatures.shinyChance) {
                card.isShiny = true;
            }
            
            results.Add(card);
        }
        
        // Track pity
        if (product.pitySystem.enabled) {
            UpdatePityCounter(results);
        }
        
        return results;
    }
}
```

---

## FAQ

**Q: Can I get duplicate cards?**  
A: Yes. Duplicates convert to "card shards" (dust system, Phase 2) or contribute to collection milestones (e.g., 3× Aria = "Aria Mastery" achievement).

**Q: Do starter boxes count toward collection milestones?**  
A: Yes. Starter box cards count as owned cards for milestones.

**Q: Can I buy Element Boosters for Lightning/Wind/Frost?**  
A: Not in Base Set. Those elements (15 cards each) are in the universal Standard Pack pool. Future expansion may add Lightning/Wind/Frost Boosters.

**Q: What happens if I buy Mythic Pack before completing 140 cards?**  
A: Mythic Pack is **locked** until you complete all 140 Base Set cards (progression requirement enforced in availability.requiresProgression).

**Q: Can I get Malakar from Standard Packs?**  
A: Yes, Malakar (BS-128) is a Neutral Epic hero in the Base Set pool. Mythic Pack guarantees him (choice card), but he can drop naturally from any pack.

---

**Summary**: The product system balances **F2P respect** (free packs, milestones, achievable 100% completion) with **monetization hooks** (premium packs, shiny hunting, time acceleration). All products reference the codex (single source of truth), enabling easy expansion to Series 2+.
