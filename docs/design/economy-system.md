# Resource Economy System Specification

**Last Updated**: December 30, 2025  
**Status**: Phase 2 (Post-MVP) for Food/Lumber/Ore, MVP for Gold/Gems/Energy  
**Related**: [game-bible.md](game-bible.md) Section 5.5, [currency-schema.json](specs/currency-schema.json)

---

## Overview

Sovereign Territories uses a **multi-currency economy** to prevent whale dominance and create diverse progression paths:
- **Gold**: Earned through gameplay, cannot be bought (F2P fairness)
- **Gems**: Premium currency, whale advantage but limited by weekly caps
- **Food/Lumber/Ore**: Resource currencies (Phase 2 - deferred post-MVP)
- **Colosseum Tokens**: PvP skill-based currency (Phase 3 - post-MVP)
- **Energy**: Stamina system to limit grinding (MVP)

**Design Philosophy**: Multiple currencies ensure whales cannot buy everything. Gold is identical for F2P and whales, creating fair progression. Gems provide whale advantage but are limited by weekly purchase caps ($136/week max).

---

## MVP Currencies (Phase 1 - 8-Week Implementation)

### Gold (Soft Currency)

**Earning Sources** (F2P Active Player):
- Daily Login: 500 Gold/day (7-day cycle)
- Battle Rewards: 50-200 Gold per battle (average 100)
  - Tutorial battles: 50 Gold (5 battles = 250 Gold)
  - Realm Map battles: 100-200 Gold (10 battles = 1,500 Gold)
- Battle Chests: 50-500 Gold (Bronze = 50, Silver = 100, Gold = 300, Platinum = 500)
- Quest Completion: 100-1,000 Gold (Phase 2 - not in MVP)
- **Total Daily (MVP)**: ~700 Gold/day (500 login + 200 battles)
- **Total Weekly (MVP)**: ~4,900 Gold/week

**Spending Breakdown** (MVP):
- Standard Pack (5 cards): 1,000 Gold
- Element Booster (5 cards): 2,000 Gold
- Epic Booster (5 cards): 5,000 Gold
- Card Combining (Phase 2): 100-50,000 Gold
- Equipment Blueprints (Phase 2): 500-2,000 Gold

**F2P vs Whale Balance**:
- Gold CANNOT be bought with real money (hard limit)
- Whales earn IDENTICAL Gold to F2P players
- This ensures F2P can buy 4-5 Standard Packs per week (fair progression)

---

### Gems (Premium Currency)

**Earning Sources** (F2P Player):
- Daily Login: 10 Gems/day (7-day cycle)
- Weekly Quests: 14 Gems/week (Phase 2 - not in MVP)
- **Total Daily (F2P MVP)**: 10 Gems/day
- **Total Weekly (F2P MVP)**: 70 Gems/week

**Earning Sources** (Whale Player):
- Purchase: $0.99 = 100 Gems, $4.99 = 550 Gems, $19.99 = 2,400 Gems
- Weekly Cap: $136/week max (prevents whale blitz)
  - 1× $19.99 pack = 2,400 Gems
  - 3× $4.99 packs = 1,650 Gems
  - 10× $0.99 packs = 1,000 Gems
  - **Max Total**: ~5,000 Gems/week (if spending full $136)
- Daily Login: 10 Gems/day (same as F2P)
- **Total Weekly (Whale)**: ~5,070 Gems/week (70× F2P advantage)

**Spending Breakdown** (MVP):
- Premium Pack (5 cards, 10% shiny rate): 100 Gems (Phase 2 - not in MVP)
- Energy Refill (100 Energy): 50 Gems (Phase 2 - not in MVP)
- Speed-Up (instant card combining): 100 Gems (Phase 2 - not in MVP)

**F2P vs Whale Balance**:
- Whales get 70× more Gems than F2P (5,070 vs 70/week)
- BUT Gems only buy premium packs (cosmetic advantage, not power)
- Rarity Budget prevents whale decks from dominating PvP (see [combat-calculation-spec.md](combat-calculation-spec.md))

---

### Energy (Stamina System)

**Purpose**: Prevent grinding, encourage daily login (not whale advantage)

**Earning Sources**:
- Starting Energy: 100 Energy (when tutorial ends)
- Natural Refill: 1 Energy per 6 minutes (240 Energy/day)
- Daily Max: 340 Energy total (100 starting + 240 refill)

**Spending**:
- Battle Cost: 10 Energy per battle
- Tutorial Battles: 0 Energy (free, unlosable)
- Post-Tutorial Battles: 10 Energy each
- **Daily Battles**: 34 battles/day max (340 Energy ÷ 10)

**Refill Options** (Phase 2 - not in MVP):
- Gem Refill: 50 Gems = 100 Energy (5 extra battles)
- Consumable: Energy Potion (from battle chests, cannot buy with Gold)

**F2P vs Whale Balance**:
- Energy is TIME-GATED (cannot buy infinite refills)
- Whales can buy 1 refill/day max (50 Gems = 5 extra battles)
- F2P: 34 battles/day, Whale: 39 battles/day (14% advantage, not gamebreaking)

---

## Phase 2 Currencies (Post-MVP, Month 2-3)

### Food (Resource Currency)

**TODO: Finalize exact AFK production rates (10-50 Food/hour too slow/fast? 24-hour cap?)**  
**TODO: Design resource sinks (prevent infinite Food accumulation, create strategic choices)**  
**TODO: Determine battle Food cost (20 per battle too expensive for F2P? tie to Player Level?)**

**Earning Sources** (F2P Active Player):
- AFK Production: Granary buildings generate 10-50 Food/hour (24-hour cap)
  - Level 1 Granary: 10 Food/hour (240 Food/day)
  - Level 5 Granary: 50 Food/hour (1,200 Food/day)
- Battle Chests: 50-200 Food (Bronze = 50, Silver = 100, Gold = 200)
- Quest Rewards: 100-500 Food
- **Total Daily (Phase 2)**: 340 Food/day (240 AFK + 100 chests)

**Spending Breakdown**:
- Battle Entry: 20 Food per battle (limits grinding without Energy)
- Deployment: 50 Food to place building on Realm Map Location
- Upgrades: 500-1,000 Food to upgrade Granary/Sawmill/Mine

**TODO: Should Food replace Energy system entirely? (1 currency instead of 2?)**

**F2P vs Whale Balance**:
- Food CANNOT be bought with Gems (prevents pay-to-win)
- Whales must wait for AFK production (time-gated)
- Storage capacity limits production (1,000-20,000 based on level)

---

### Lumber (Resource Currency)

**TODO: Design Lumber-specific uses (prevent overlap with Food/Ore)**  
**TODO: Determine building construction costs (300 Lumber too cheap/expensive?)**

**Earning Sources** (F2P Active Player):
- AFK Production: Sawmill buildings generate 10-50 Lumber/hour
- Battle Chests: 50-200 Lumber
- Quest Rewards: 100-500 Lumber
- **Total Daily (Phase 2)**: 340 Lumber/day (240 AFK + 100 chests)

**Spending Breakdown**:
- Equipment Crafting: 100-500 Lumber (Wooden Shield, Leather Armor)
- Construction: 300 Lumber to build new Granary/Sawmill/Mine
- Upgrades: 500-1,000 Lumber to upgrade buildings

**F2P vs Whale Balance**:
- Lumber CANNOT be bought with Gems
- Time-gated AFK production (storage cap limits accumulation)

---

### Ore (Resource Currency)

**TODO: Finalize Ore scarcity (currently 50% of Food/Lumber, is that tight enough?)**  
**TODO: Design high-tier equipment Ore costs (prevent F2P from crafting Mythic weapons too easily)**

**Earning Sources** (F2P Active Player):
- AFK Production: Mine buildings generate 5-25 Ore/hour (half of Food/Lumber)
- Battle Chests: 25-100 Ore (rarer than Food/Lumber)
- Quest Rewards: 50-250 Ore
- **Total Daily (Phase 2)**: 170 Ore/day (120 AFK + 50 chests)

**Spending Breakdown**:
- High-Tier Equipment: 200-2,000 Ore (Iron Sword, Steel Armor, Mythic Weapons)
- Upgrades: 200-500 Ore to upgrade buildings
- Card Combining (high tiers): 500 Ore + 50,000 Gold = Legendary → Mythic

**F2P vs Whale Balance**:
- Ore is RAREST resource (intentional bottleneck)
- Cannot buy with Gems (prevents pay-to-win)
- Forces strategic spending (upgrade buildings OR craft equipment, not both)

---

## Phase 3 Currencies (Post-MVP, Month 4-6)

### Arena Tokens (PvP Currency)

**Earning Sources** (Skill-Based Only):
- PvP Match Win: 10 Arena Tokens
- PvP Match Loss: 2 Arena Tokens (consolation)
- Daily PvP Limit: 5 matches/day (50 Tokens if 5-0, 10 Tokens if 0-5)
- **Total Daily**: 10-50 Tokens (skill-based, cannot buy)

**Spending**:
- PvP Market Exclusive Cards: 500-5,000 Tokens
- PvP Market Equipment: 1,000-10,000 Tokens
- Season Rewards: Top 100 players get exclusive Mythic cards

**F2P vs Whale Balance**:
- Colosseum Tokens CANNOT be bought with Gems (pure skill)
- Whales with weak decks earn LESS than skilled F2P players
- Matchmaking uses Deck Power brackets (see [combat-calculation-spec.md](combat-calculation-spec.md))

---

## Auto-Collection System (Phase 2)

**TODO: Design offline collection caps (12-hour max? 24-hour? unlimited?)**  
**TODO: Determine storage upgrade costs (prevent F2P from maxing storage too easily)**  
**TODO: Create visual feedback (notifications for full storage, upgrade prompts)**

**Philosophy**: No tap-to-collect annoyance. Resources accumulate automatically.

**Mechanics**:
- Buildings produce Food/Lumber/Ore continuously (10-50 per hour)
- Resources accumulate up to **storage capacity** (1,000-20,000 based on level)
- Production STOPS when storage is full (incentivizes spending resources)
- Player wakes up to full storage, ready to spend on strategy

**Example**:
- Level 1 Granary: 10 Food/hour, 1,000 Food storage
- After 100 hours (4+ days), storage is full (10 × 100 = 1,000)
- Production stops until player spends Food on battles/upgrades
- Player spends 500 Food, production resumes

**TODO: Should offline production be limited? (prevent 1-week vacation = 20,000 Food abuse)**

**Design Intent**:
- NOT a crafting game (no "check in every hour to collect")
- Encourages strategic spending (deploy buildings, fight battles, upgrade)
- Time-gating prevents whale advantage (cannot buy infinite resources)

---

## Store Separation (Phase 2)

**TODO: Design Pack Market UI (tabs vs scrollable list, bundle offers, daily deals?)**  
**TODO: Determine bundle pricing (50-card Game Deck = 2,400 Gems too cheap/expensive?)**  
**TODO: Create resource bundle conversion rates (prevent exploits, keep emergency purchases viable)**

**Pack Market** (Gold/Gems):
- Standard Pack: 1,000 Gold (5 cards)
- Element Booster: 2,000 Gold (5 cards)
- Epic Booster: 5,000 Gold (5 cards)
- Premium Pack: 100 Gems (5 cards, 10% shiny rate)
- Game Deck: 2,400 Gems OR 50,000 Gold (50 cards, themed)

**TODO: Should Game Decks be Phase 3? (require Alliance Wars meta before creating precons)**

**Resource Market** (Food/Lumber/Ore):
- Food Bundles: 1,000 Food for 500 Gold (emergency purchase)
- Lumber Bundles: 1,000 Lumber for 500 Gold
- Ore Bundles: 500 Ore for 1,000 Gold (rarer, more expensive)
- Equipment Blueprints: 500-2,000 Gold (craft with Lumber/Ore)

**TODO: Should resource bundles exist? (creates pay-to-win path if whales can buy Food with Gold)**

**PvP Store** (Colosseum Tokens - Phase 3):
- Exclusive Cards: 500-5,000 Colosseum Tokens
- Exclusive Equipment: 1,000-10,000 Colosseum Tokens
- Season Rewards: Mythic cards for top players

**TODO: Design PvP Store exclusive cards (create desirable chase cards without balance issues)**

---

## F2P vs Whale Projections

### F2P Player (30-Day Progression)

**Day 1**:
- Tutorial: 500 Gold (5 battles × 100 Gold)
- Daily Login: 500 Gold
- Battle Chests: 200 Gold
- **Total**: 1,200 Gold (can buy 1 Standard Pack)

**Week 1** (MVP):
- Gold: 4,900 (700/day × 7)
- Gems: 70 (10/day × 7)
- Packs Bought: 4× Standard Packs (4,000 Gold) OR 2× Element Boosters (4,000 Gold)
- Total Cards: 36 (tutorial) + 20 (packs) = 56 cards

**Week 2-4** (MVP):
- Gold: 14,700 (4,900 × 3)
- Packs Bought: 14× Standard Packs OR 7× Element Boosters
- Total Cards: 56 + 70 = 126 cards

**Month 1 Total** (MVP):
- Gold Earned: 21,000 (700/day × 30)
- Packs Bought: 21× Standard Packs (105 cards) OR 10× Element Boosters (50 cards)
- **Total Collection**: 36 (tutorial) + 105 = 141 cards

---

### Whale Player (30-Day Progression)

**Day 1**:
- Spend $19.99 = 2,400 Gems
- Tutorial: 500 Gold (same as F2P)
- Daily Login: 500 Gold + 10 Gems
- **Total**: 1,000 Gold + 2,410 Gems

**Week 1** (MVP):
- Spend: $136 (weekly cap) = 5,000 Gems
- Gold: 4,900 (same as F2P)
- Gems: 5,070 (5,000 purchased + 70 daily)
- Packs Bought (Gold): 4× Standard Packs
- Packs Bought (Gems - Phase 2): 50× Premium Packs (5,000 Gems ÷ 100) = 250 cards with 10% shiny rate
- **Total Cards**: 36 (tutorial) + 20 (Gold packs) + 250 (Gem packs) = 306 cards

**Month 1 Total** (MVP without Phase 2 Gem purchases):
- Spend: $544 ($136 × 4 weeks)
- Gold Earned: 21,000 (same as F2P)
- Gems Earned: 20,280 (5,070 × 4)
- **Total Collection (MVP)**: 36 (tutorial) + 105 (Gold packs) = 141 cards (SAME as F2P in MVP)
- **Total Collection (Phase 2)**: 141 + 2,028 Premium Pack cards = 2,169 cards (15× F2P collection)

---

## Balance Analysis

### Gold Advantage
- **F2P**: 21,000 Gold/month = 21 Standard Packs = 105 cards
- **Whale**: 21,000 Gold/month = 21 Standard Packs = 105 cards
- **Verdict**: IDENTICAL (whales cannot buy Gold, fair progression)

### Gem Advantage
- **F2P**: 280 Gems/month (10/day × 28) = 2 Premium Packs (Phase 2) = 10 cards
- **Whale**: 20,280 Gems/month = 202 Premium Packs (Phase 2) = 1,010 cards
- **Verdict**: 100× advantage BUT mitigated by:
  - Rarity Budget (prevents all-Legendary decks, see [combat-calculation-spec.md](combat-calculation-spec.md))
  - PvP Brackets (whales fight whales, F2P fights F2P)
  - Shiny 5% utility (not gamebreaking, cosmetic appeal)

### Time-Gating (Energy/Food/Lumber/Ore)
- **F2P**: 34 battles/day, 340 Food/day (Phase 2), 340 Lumber/day, 170 Ore/day
- **Whale**: 39 battles/day (14% advantage with Gem refills), SAME resources (cannot buy)
- **Verdict**: Time-gated resources prevent whale dominance in Phase 2 economy

---

## Implementation Roadmap

### MVP (Week 1-8)
- ✅ Gold earning (battles, daily login, battle chests)
- ✅ Gold spending (Pack Store: Standard/Element/Epic Packs)
- ✅ Energy system (10 per battle, 240 refill/day, tutorial = 0 cost)
- ❌ Gems (display only, no purchases in MVP)
- ❌ Food/Lumber/Ore (Phase 2)

### Phase 2 (Month 2-3)
- ❌ Gem purchases ($0.99 - $19.99, weekly cap $136)
- ❌ Premium Packs (100 Gems, 10% shiny rate)
- ❌ Food/Lumber/Ore production (Granary/Sawmill/Mine buildings)
- ❌ Auto-collection system (storage caps, AFK accumulation)
- ❌ Resource Store (trade Food/Lumber/Ore for Gold)

### Phase 3 (Month 4-6)
- ❌ Colosseum Tokens (PvP wins, skill-based)
- ❌ PvP Store (exclusive cards, equipment)
- ❌ Season leaderboards (top 100 Mythic rewards)

---

**For MVP implementation details, see**: [mvp-scope-final.md](mvp-scope-final.md)  
**For combat balance, see**: [combat-calculation-spec.md](combat-calculation-spec.md)  
**For data specifications, see**: [currency-schema.json](specs/currency-schema.json)
