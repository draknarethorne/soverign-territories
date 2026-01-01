# MVP Additions: Crafting & PvP Systems (Phase 1 Scope Expansion)

**Document Purpose**: Address critical competitive gaps identified in competitive analysis  
**Status**: Proposed for MVP inclusion (8-week timeline remains, rebalanced priorities)  
**Date**: December 31, 2025  
**Priority**: ⭐⭐⭐⭐⭐ **CRITICAL** - Both systems required for competitive parity

---

## Executive Summary

**Problem Identified**:
1. **No Crafting in MVP** = RNG hell (players open 50 packs, never get Legendary they want)
2. **No PvP in Phase 1** = Late engagement driver (Hearthstone/Gwent have Day 1 PvP)

**Solution**: Add **simplified versions** to MVP without breaking 8-week timeline:
1. **Scroll-Based Crafting** (Week 7) - Targeted card acquisition, duplicate conversion
2. **Async Arena PvP** (Week 8) - Matchmade battles vs AI-controlled player decks

**Timeline Impact**: ✅ **NONE** - Rebalance Week 7-8 deliverables (defer analytics, polish to Phase 1.1)

**Expected Impact**:
- **Crafting**: Reduce duplicate frustration by 80%, increase pack purchase intent by 30%
- **PvP**: Increase Day 7 retention by 20%, add daily engagement loop
- **Ratings**: MVP projection increases from 4.0-4.2/5 → **4.2-4.4/5**

---

## Part 1: Scroll-Based Crafting System (MVP Version)

### Design Philosophy

**Hearthstone Model** (Rejected for MVP):
- Dust system (disenchant any card → dust, craft any card with dust)
- Complex UI (search 1,500+ cards, filter, preview, confirm)
- Requires crafting cost database (1,500 cards × 6 rarities = 9,000 entries)
- **Too complex for 8-week MVP**

**Our Model** (Simplified, Scroll-Based):
- **Scrolls** are craftable items (like Pokemon TCG's Rare Candy)
- 6 scroll types (Common, Uncommon, Rare, Epic, Legendary, Mythic)
- **Duplicate Conversion**: 5 duplicates → 1 Scroll (same rarity)
- **Scroll Usage**: 1 Scroll → Craft any card (same rarity)
- **Simple UI**: "Craft Common Card" → Show 30 Commons → Pick one

**Why Scrolls Work**:
- ✅ **No crafting database** - Scrolls are currency, not recipes
- ✅ **Simple conversion** - 5 dupes → 1 Scroll (easy math)
- ✅ **Simple UI** - Pick from rarity pool (30-50 cards), not 1,500+ search
- ✅ **Monetization** - Sell scrolls in Market ($0.99 for Rare Scroll)
- ✅ **Future-proof** - Add new cards, scrolls still work (no database updates)

---

### Scroll Types & Acquisition

**6 Scroll Rarities**:
```
📜 Common Scroll (Bronze)
  - Craft: Any Common card (30 options in MVP)
  - Earn: 5 Common duplicates → 1 Common Scroll
  - Buy: 100 Gold OR $0.49 (whale shortcut)

📜 Uncommon Scroll (Silver)
  - Craft: Any Uncommon card (25 options in MVP)
  - Earn: 5 Uncommon duplicates → 1 Uncommon Scroll
  - Buy: 500 Gold OR $0.99

📜 Rare Scroll (Gold)
  - Craft: Any Rare card (20 options in MVP)
  - Earn: 5 Rare duplicates → 1 Rare Scroll
  - Buy: 2,000 Gold OR $2.99

📜 Epic Scroll (Platinum)
  - Craft: Any Epic card (15 options in MVP)
  - Earn: 3 Epic duplicates → 1 Epic Scroll (lower conversion, rarer cards)
  - Buy: 5,000 Gold OR $4.99

📜 Legendary Scroll (Prismatic)
  - Craft: Any Legendary card (10 options in MVP)
  - Earn: 2 Legendary duplicates → 1 Legendary Scroll (very rare)
  - Buy: 10,000 Gold OR $9.99

📜 Mythic Scroll (Rainbow)
  - Craft: Any Mythic card (5 options in MVP)
  - Earn: 2 Mythic duplicates → 1 Mythic Scroll
  - Buy: 50,000 Gold OR $19.99 (ultra-whale)
```

**Duplicate Conversion Ratios**:
- Commons/Uncommons/Rares: **5:1** (common dupes, generous conversion)
- Epics: **3:1** (rarer, lower conversion threshold)
- Legendaries/Mythics: **2:1** (ultra-rare, high value)

**Why These Ratios**:
- ✅ **F2P Viable**: Opening 25 packs (125 cards) = ~50 Commons → 10 Common Scrolls → 10 targeted Commons
- ✅ **Anti-Whale**: Can't spam $1,000 to get 100 Legendary Scrolls (Gold caps scroll purchases)
- ✅ **Pity Alignment**: Legendary every 50 packs = ~25 dupes → 12 Legendary Scrolls (if unlucky)

---

### Crafting UI (Week 7, 2 Days)

**Main Menu Button**: "⚒️ Crafting" (next to Market, Codex)

**Crafting Screen**:
```
╔═══════════════════════════════════════════════════════╗
║                  ⚒️ CRAFTING HALL                    ║
║                (Scribe's Workshop)                    ║
╠═══════════════════════════════════════════════════════╣
║ YOUR SCROLLS:                                         ║
║   📜 Common Scrolls: 12                               ║
║   📜 Uncommon Scrolls: 5                              ║
║   📜 Rare Scrolls: 2                                  ║
║   📜 Epic Scrolls: 0                                  ║
║   📜 Legendary Scrolls: 0                             ║
║   📜 Mythic Scrolls: 0                                ║
║                                                       ║
║ CRAFT A CARD:                                         ║
║ [Craft Common Card] (Costs: 1 Common Scroll)         ║
║ [Craft Uncommon Card] (Costs: 1 Uncommon Scroll)     ║
║ [Craft Rare Card] (Costs: 1 Rare Scroll) 🔒 Need 1   ║
║ [Craft Epic Card] (Costs: 1 Epic Scroll) 🔒 Need 1   ║
║ [Craft Legendary Card] (Costs: 1 Legendary Scroll) 🔒║
║ [Craft Mythic Card] (Costs: 1 Mythic Scroll) 🔒      ║
║                                                       ║
║ CONVERT DUPLICATES:                                   ║
║ [Convert 5 Common Dupes → 1 Common Scroll]           ║
║   (You have 47 excess Commons)                        ║
║ [Convert 5 Uncommon Dupes → 1 Uncommon Scroll]       ║
║   (You have 12 excess Uncommons)                      ║
║ [Convert 5 Rare Dupes → 1 Rare Scroll]               ║
║   (You have 3 excess Rares) 🔒 Need 2 more            ║
╚═══════════════════════════════════════════════════════╝
```

**Player Action**: Taps "Craft Common Card"

**Crafting Selection Screen**:
```
╔═══════════════════════════════════════════════════════╗
║            SELECT A COMMON CARD TO CRAFT              ║
║             (Costs: 1 Common Scroll 📜)               ║
╠═══════════════════════════════════════════════════════╣
║ [Filter: All Elements | Fire | Water | Earth]        ║
║ [Filter: All Types | Heroes | Units | Buildings]     ║
║                                                       ║
║ AVAILABLE COMMON CARDS (30 total):                   ║
║                                                       ║
║ ┌─────────────┬─────────────┬─────────────┐          ║
║ │ Fire Knight │   Footman   │   Archer    │          ║
║ │   (Fire)    │  (Neutral)  │  (Neutral)  │          ║
║ │  You own: 3 │  You own: 7 │  You own: 2 │          ║
║ │  [CRAFT]    │  [CRAFT]    │  [CRAFT]    │          ║
║ └─────────────┴─────────────┴─────────────┘          ║
║ ┌─────────────┬─────────────┬─────────────┐          ║
║ │   Farmer    │  Lumberjack │    Miner    │          ║
║ │  (Economy)  │  (Economy)  │  (Economy)  │          ║
║ │  You own: 5 │  You own: 1 │  You own: 0 │ ✨ NEW   ║
║ │  [CRAFT]    │  [CRAFT]    │  [CRAFT]    │          ║
║ └─────────────┴─────────────┴─────────────┘          ║
║ ... (24 more cards, scroll to view)                  ║
╚═══════════════════════════════════════════════════════╝
```

**Player Action**: Taps "Craft" on Miner (0 owned)

**Confirmation Dialog**:
```
╔═══════════════════════════════════════════════════════╗
║              CONFIRM CRAFTING                         ║
╠═══════════════════════════════════════════════════════╣
║ Craft: [Miner] (Common Economy Card)                 ║
║                                                       ║
║ Cost: 1 Common Scroll 📜                              ║
║ (You have 12 Common Scrolls, will have 11 after)     ║
║                                                       ║
║ Stats:                                                ║
║   - Generates: 10 Ore/hour (when placed on map)      ║
║   - HP: 10, ATK: 5 (weak in combat)                  ║
║                                                       ║
║ [CONFIRM CRAFT] [CANCEL]                             ║
╚═══════════════════════════════════════════════════════╝
```

**Player Action**: Taps "CONFIRM CRAFT"

**System Actions**:
1. Deduct 1 Common Scroll (12 → 11)
2. Grant 1 Miner card (add to Codex)
3. Show reward animation (card flips, "Crafted!" text)
4. Return to Crafting Hall

**Total UI Work**: 3 screens (Crafting Hall, Card Selection, Confirmation) = **2 days** (Week 7)

---

### Duplicate Conversion UI (Week 7, 1 Day)

**Crafting Hall → "Convert Duplicates" Button**:

**Conversion Screen**:
```
╔═══════════════════════════════════════════════════════╗
║           CONVERT DUPLICATES TO SCROLLS               ║
║               (Scribe's Recycling)                    ║
╠═══════════════════════════════════════════════════════╣
║ YOUR EXCESS CARDS:                                    ║
║   - 47 Common duplicates (9× Fire Knight, 7× Footman)║
║   - 12 Uncommon duplicates (3× Archer, 2× Cleric)    ║
║   - 3 Rare duplicates (2× Fireball, 1× Heal)         ║
║   - 0 Epic duplicates                                 ║
║                                                       ║
║ CONVERSION OPTIONS:                                   ║
║                                                       ║
║ [Convert 5 Common Dupes → 1 Common Scroll]           ║
║   (You can convert 9 times, get 9 Scrolls)           ║
║   [CONVERT ALL] (45 dupes → 9 Scrolls, keep 2 spare) ║
║                                                       ║
║ [Convert 5 Uncommon Dupes → 1 Uncommon Scroll]       ║
║   (You can convert 2 times, get 2 Scrolls)           ║
║   [CONVERT ALL] (10 dupes → 2 Scrolls, keep 2 spare) ║
║                                                       ║
║ [Convert 5 Rare Dupes → 1 Rare Scroll] 🔒            ║
║   (You have 3 dupes, need 2 more)                    ║
║   [LOCKED UNTIL 5 RARES]                             ║
║                                                       ║
║ [CONVERT ALL RARITIES] (Smart convert: 9 Common + 2  ║
║  Uncommon Scrolls, save Rares for later)             ║
╚═══════════════════════════════════════════════════════╝
```

**Player Action**: Taps "CONVERT ALL RARITIES"

**System Actions**:
1. Convert 45 Common dupes → 9 Common Scrolls (keep 2 spare)
2. Convert 10 Uncommon dupes → 2 Uncommon Scrolls (keep 2 spare)
3. Show conversion animation (cards swirl into scroll icon)
4. Update Crafting Hall inventory (12 + 9 = 21 Common Scrolls, 5 + 2 = 7 Uncommon Scrolls)

**Total UI Work**: 1 screen (Conversion) + animations = **1 day** (Week 7)

---

### Crafting System Backend (Week 7, 2 Days)

**CraftingManager.cs** (Singleton):
```csharp
public class CraftingManager : MonoBehaviour
{
    // Scroll inventory (stored server-side in Nakama metadata)
    public Dictionary<Rarity, int> Scrolls = new Dictionary<Rarity, int>
    {
        { Rarity.Common, 0 },
        { Rarity.Uncommon, 0 },
        { Rarity.Rare, 0 },
        { Rarity.Epic, 0 },
        { Rarity.Legendary, 0 },
        { Rarity.Mythic, 0 }
    };

    // Conversion ratios (duplicates → scrolls)
    private Dictionary<Rarity, int> ConversionRatios = new Dictionary<Rarity, int>
    {
        { Rarity.Common, 5 },      // 5 Commons → 1 Scroll
        { Rarity.Uncommon, 5 },    // 5 Uncommons → 1 Scroll
        { Rarity.Rare, 5 },        // 5 Rares → 1 Scroll
        { Rarity.Epic, 3 },        // 3 Epics → 1 Scroll
        { Rarity.Legendary, 2 },   // 2 Legendaries → 1 Scroll
        { Rarity.Mythic, 2 }       // 2 Mythics → 1 Scroll
    };

    // Convert duplicates to scrolls
    public bool ConvertDuplicates(Rarity rarity, int duplicateCount)
    {
        int ratio = ConversionRatios[rarity];
        int scrollsEarned = duplicateCount / ratio;
        int spareDuplicates = duplicateCount % ratio;

        if (scrollsEarned > 0)
        {
            Scrolls[rarity] += scrollsEarned;
            // Remove duplicates from Codex (server-side update)
            CardManager.Instance.RemoveCards(rarity, scrollsEarned * ratio);
            // Save to Nakama
            SaveScrolls();
            return true;
        }
        return false; // Not enough dupes
    }

    // Craft a card using a scroll
    public bool CraftCard(string cardId, Rarity rarity)
    {
        if (Scrolls[rarity] >= 1)
        {
            Scrolls[rarity]--;
            // Grant card to player (server-side)
            CardManager.Instance.AddCard(cardId);
            // Save to Nakama
            SaveScrolls();
            return true;
        }
        return false; // Not enough scrolls
    }

    // Save scrolls to Nakama metadata
    private void SaveScrolls()
    {
        // Nakama storage write (JSON serialization)
        var scrollData = new Dictionary<string, object>
        {
            { "commonScrolls", Scrolls[Rarity.Common] },
            { "uncommonScrolls", Scrolls[Rarity.Uncommon] },
            { "rareScrolls", Scrolls[Rarity.Rare] },
            { "epicScrolls", Scrolls[Rarity.Epic] },
            { "legendaryScrolls", Scrolls[Rarity.Legendary] },
            { "mythicScrolls", Scrolls[Rarity.Mythic] }
        };
        NakamaClient.Instance.WriteStorageObjects("scrolls", scrollData);
    }
}
```

**Total Backend Work**: 1 singleton class + Nakama integration = **2 days** (Week 7)

---

### Scroll Monetization (Market Integration)

**Pack Market → New Tab: "Scrolls"**:
```
╔═══════════════════════════════════════════════════════╗
║                    📜 SCROLL MARKET                   ║
║              (Purchase Crafting Scrolls)              ║
╠═══════════════════════════════════════════════════════╣
║ BUY SCROLLS:                                          ║
║                                                       ║
║ [Common Scroll] (100 Gold OR $0.49)                  ║
║   - Craft any Common card                             ║
║   [BUY 1] [BUY 5 for $1.99]                          ║
║                                                       ║
║ [Uncommon Scroll] (500 Gold OR $0.99)                ║
║   - Craft any Uncommon card                           ║
║   [BUY 1] [BUY 3 for $1.99]                          ║
║                                                       ║
║ [Rare Scroll] (2,000 Gold OR $2.99)                  ║
║   - Craft any Rare card                               ║
║   [BUY 1] [BUY 2 for $4.99]                          ║
║                                                       ║
║ [Epic Scroll] (5,000 Gold OR $4.99)                  ║
║   - Craft any Epic card                               ║
║   [BUY 1]                                             ║
║                                                       ║
║ [Legendary Scroll] (10,000 Gold OR $9.99)            ║
║   - Craft any Legendary card                          ║
║   [BUY 1]                                             ║
║                                                       ║
║ [Mythic Scroll] (50,000 Gold OR $19.99)              ║
║   - Craft any Mythic card                             ║
║   [BUY 1] (ULTRA-WHALE)                              ║
╚═══════════════════════════════════════════════════════╝
```

**Revenue Model**:
- **F2P Path**: Earn scrolls from duplicates (slow but free)
- **Dolphin Path**: Buy Rare/Epic Scrolls with Gold ($3-5/scroll)
- **Whale Path**: Buy Legendary/Mythic Scrolls with IAP ($10-20/scroll)

**Expected Revenue**:
- **Dolphins** (10% of paying players): $5-10/month on Rare/Epic Scrolls
- **Whales** (1% of paying players): $50-100/month on Legendary/Mythic Scrolls
- **ARPU Increase**: +$1-2/month (10% conversion × $10 avg spend)

---

### Crafting System Integration Timeline (Week 7)

**Day 1 (Monday)**: UI Design
- [ ] Crafting Hall screen (scroll inventory, craft buttons, convert buttons)
- [ ] Card Selection screen (filter by rarity/element/type, craft button)
- [ ] Confirmation dialog (show card stats, cost, confirm/cancel)

**Day 2 (Tuesday)**: UI Implementation
- [ ] Unity UI Toolkit prefabs (CraftingHallUI, CardSelectionUI, ConfirmationDialog)
- [ ] Button callbacks (craft, convert, filter, confirm, cancel)
- [ ] Animation states (card flip, scroll swirl, confirmation glow)

**Day 3 (Wednesday)**: Backend Integration
- [ ] CraftingManager.cs singleton (scroll inventory, conversion logic, craft logic)
- [ ] Nakama storage (read/write scroll data, save player metadata)
- [ ] CardManager integration (add/remove cards from Codex)

**Day 4 (Thursday)**: Monetization
- [ ] Scroll Market tab (buy scrolls with Gold/IAP)
- [ ] IAP integration (Apple/Google in-app purchases for scrolls)
- [ ] Bundle offers (5 Common Scrolls for $1.99, etc.)

**Day 5 (Friday)**: Testing & Polish
- [ ] Test duplicate conversion (5 dupes → 1 scroll, 47 dupes → 9 scrolls)
- [ ] Test crafting (1 scroll → 1 card, edge cases)
- [ ] Test IAP (buy scrolls with real money, receipt validation)
- [ ] Bug fixes (edge cases, UI polish, animation timing)

**Total Time**: 5 days (Week 7) = **Within 8-week MVP timeline** ✅

---

## Part 2: Async Arena PvP System (MVP Version)

### Design Philosophy

**Hearthstone Model** (Rejected for MVP):
- Live 1v1 with turn timer (30 seconds/turn)
- Matchmaking queue (websockets, server hosting)
- Reconnection handling (dropped connections, pause/resume)
- Emotes, concede button, real-time chat
- **Too complex for 8-week MVP** (requires Nakama websockets, turn server, reconnection logic)

**Clash of Clans Model** (Adopted for MVP):
- **Async PvP** - Attack AI-controlled player bases
- **No live opponents** - Opponent's deck plays via AI (no websockets needed)
- **Simple matchmaking** - Match player level ±2 levels (SQL query)
- **Rewards on win/loss** - Colosseum Tokens (can't be bought, skill-only currency)
- **Bracketed tiers** - Level 1-9, 10-14, 15-19, 20+ (prevents whale stomp)

**Why Async Works for MVP**:
- ✅ **No websockets** - Nakama HTTP API only (simpler deployment)
- ✅ **No turn server** - AI plays opponent's deck (no live coordination)
- ✅ **Fast iteration** - Fix AI balance without coordinating 2 players
- ✅ **Mobile-friendly** - Play on your schedule (no 10-min commitment)
- ✅ **Monetization test** - Colosseum Tokens → Exclusive cards (proves PvP economy)

---

### Arena Structure

**Unlock**: Level 5 (after tutorial, ~Week 1 of play)

**Arena Tiers** (Bracketed by Player Level):
```
🥉 Bronze Arena (Level 1-9)
  - Opponents: Level 1-9 players
  - Matchmaking: Random from pool (no ELO)
  - Rewards: 10-20 Tokens/win, 5 Tokens/loss
  - Season rewards: 100 Tokens (participation trophy)

🥈 Silver Arena (Level 10-14)
  - Opponents: Level 10-14 players
  - Matchmaking: Random from pool
  - Rewards: 20-40 Tokens/win, 10 Tokens/loss
  - Season rewards: 300 Tokens + 1 Rare card

🥇 Gold Arena (Level 15-19)
  - Opponents: Level 15-19 players
  - Matchmaking: Random from pool
  - Rewards: 40-80 Tokens/win, 20 Tokens/loss
  - Season rewards: 800 Tokens + 1 Epic card

💎 Diamond Arena (Level 20+)
  - Opponents: Level 20+ players
  - Matchmaking: Random from pool (future: ELO-based)
  - Rewards: 80-150 Tokens/win, 40 Tokens/loss
  - Season rewards: 2,000 Tokens + 1 Legendary card
```

**Season**: 30 days (resets monthly, keeps tier placement)

---

### Arena UI (Week 8, 2 Days)

**Main Menu Button**: "⚔️ Arena" (next to Battle, Codex)

**Arena Home Screen**:
```
╔═══════════════════════════════════════════════════════╗
║                   ⚔️ ARENA PVP                        ║
║              (Async Matchmade Battles)                ║
╠═══════════════════════════════════════════════════════╣
║ YOUR RANK:                                            ║
║   🥈 Silver Arena (Level 12)                          ║
║   Tokens: 450 / 800 (to Gold Arena reward)           ║
║   Season ends in: 18 days                             ║
║                                                       ║
║ TODAY'S BATTLES:                                      ║
║   Battles played: 3 / 5 (2 free battles left)        ║
║   Win/Loss record: 2-1 (66% win rate)                ║
║                                                       ║
║ [FIND OPPONENT] (10 Stamina, matchmake vs Level 10-14)║
║                                                       ║
║ REWARDS:                                              ║
║   - Win: 20-40 Colosseum Tokens                       ║
║   - Loss: 10 Tokens                                   ║
║   - Season end (Silver): 300 Tokens + 1 Rare card    ║
║                                                       ║
║ [VIEW COLOSSEUM MARKET] (spend Tokens on exclusive   ║
║  cards, can't buy with Gold/Gems)                     ║
║                                                       ║
║ [VIEW LEADERBOARD] (top 100 players in your tier)    ║
╚═══════════════════════════════════════════════════════╝
```

**Player Action**: Taps "FIND OPPONENT"

**Matchmaking Screen**:
```
╔═══════════════════════════════════════════════════════╗
║                  FINDING OPPONENT...                  ║
╠═══════════════════════════════════════════════════════╣
║ [Spinner animation]                                   ║
║                                                       ║
║ Searching for Silver Arena opponents (Level 10-14)...║
║                                                       ║
║ (This takes 1-3 seconds, queries Nakama database)    ║
╚═══════════════════════════════════════════════════════╝
```

**System Actions** (Matchmaking Logic):
1. Query Nakama: `SELECT user_id, deck_id, player_level FROM players WHERE player_level BETWEEN 10 AND 14 AND arena_tier = 'silver' ORDER BY RANDOM() LIMIT 1`
2. Load opponent's deck (6 cards + tactics)
3. Show opponent preview screen

**Opponent Preview Screen**:
```
╔═══════════════════════════════════════════════════════╗
║                  OPPONENT FOUND!                      ║
╠═══════════════════════════════════════════════════════╣
║ Opponent: [Player_54821]                             ║
║ Level: 12 (Silver Arena)                              ║
║ Win Rate: 58% (14 wins, 10 losses)                    ║
║                                                       ║
║ OPPONENT'S DECK (AI-controlled):                      ║
║   [Water Mage 3★] (Epic, 180 HP, 90 ATK)             ║
║   [Knight 2★] × 2 (Uncommon, 30 HP, 15 ATK each)     ║
║   [Archer 2★] × 2 (Common, 15 HP, 8 ATK each)        ║
║   [Healer 1★] (Common, 10 HP, 5 ATK)                 ║
║                                                       ║
║ [BATTLE] (10 Stamina, start Arena match)             ║
║ [CANCEL] (return to Arena home, no Stamina cost)     ║
╚═══════════════════════════════════════════════════════╝
```

**Player Action**: Taps "BATTLE"

**System Actions**:
1. Deduct 10 Stamina (100 → 90)
2. Load battle scene (8x8 grid)
3. Player's 6-card deck spawns (manual placement OR auto-deploy)
4. Opponent's 6-card deck spawns (AI-controlled, uses opponent's saved deck)
5. Battle plays (player vs AI, same combat rules as PvE)
6. Victory/Defeat screen

---

### Arena Battle Flow (Same as PvE)

**Battle Setup**:
- Player's deck: 6 cards (manual placement or auto-deploy)
- Opponent's deck: 6 cards (AI-controlled, uses saved formation from opponent's profile)
- Combat: Same 8x8 grid, same turn-based rules, same tactic activation

**AI Behavior** (Simple for MVP):
- Move toward nearest player unit (A* pathfinding)
- Attack lowest-HP target in range (prioritize kills)
- Use tactics on cooldown (Fireball → lowest HP, Heal → lowest ally HP)
- Retreat if HP < 30% (move away from player units)

**Victory Rewards**:
```
╔═══════════════════════════════════════════════════════╗
║                     VICTORY!                          ║
╠═══════════════════════════════════════════════════════╣
║ You defeated: [Player_54821] (Level 12)              ║
║                                                       ║
║ Rewards:                                              ║
║   +35 Colosseum Tokens (Silver tier win)             ║
║   +100 XP                                             ║
║   +50 Gold                                            ║
║                                                       ║
║ Arena Record: 3-1 (75% win rate)                      ║
║ Next battle: Free (2/5 daily battles remaining)      ║
║                                                       ║
║ [RETURN TO ARENA] [FIND NEXT OPPONENT]               ║
╚═══════════════════════════════════════════════════════╝
```

**Defeat Rewards**:
```
╔═══════════════════════════════════════════════════════╗
║                      DEFEAT                           ║
╠═══════════════════════════════════════════════════════╣
║ You were defeated by: [Player_54821] (Level 12)      ║
║                                                       ║
║ Consolation Rewards:                                  ║
║   +10 Colosseum Tokens (Silver tier loss)            ║
║   +50 XP                                              ║
║                                                       ║
║ Arena Record: 2-2 (50% win rate)                      ║
║ Next battle: Free (2/5 daily battles remaining)      ║
║                                                       ║
║ [RETURN TO ARENA] [REMATCH] (play vs same opponent)  ║
╚═══════════════════════════════════════════════════════╝
```

---

### Colosseum Token Economy

**Token Earn Rates** (Can't Buy Tokens - Skill-Only Currency):
```
Bronze Arena (Level 1-9):
  - Win: 10-20 Tokens
  - Loss: 5 Tokens
  - Season end: 100 Tokens

Silver Arena (Level 10-14):
  - Win: 20-40 Tokens
  - Loss: 10 Tokens
  - Season end: 300 Tokens + 1 Rare

Gold Arena (Level 15-19):
  - Win: 40-80 Tokens
  - Loss: 20 Tokens
  - Season end: 800 Tokens + 1 Epic

Diamond Arena (Level 20+):
  - Win: 80-150 Tokens
  - Loss: 40 Tokens
  - Season end: 2,000 Tokens + 1 Legendary
```

**Daily Battle Limit**:
- 5 free battles/day (reset at midnight UTC)
- 6th+ battles: 100 Gems each (whale unlock, max 10/day)

**Why Daily Limits**:
- ✅ **Prevent grinding** - Can't farm 1,000 Tokens/day (preserves exclusivity)
- ✅ **Session pacing** - 5 battles = 30-50 min (mobile-friendly)
- ✅ **Whale unlock** - Pay 100 Gems for extra battles (monetization)

---

### Colosseum Market (Token Exclusive Shop)

**Main Menu → Arena → "View Colosseum Market"**:

**Colosseum Market Screen**:
```
╔═══════════════════════════════════════════════════════╗
║              🏛️ COLOSSEUM MARKET                     ║
║          (Tokens Only - Can't Buy with Gold!)        ║
╠═══════════════════════════════════════════════════════╣
║ YOUR TOKENS: 450                                      ║
║                                                       ║
║ EXCLUSIVE CARDS (Arena-Only):                        ║
║                                                       ║
║ [Gladiator Hero] (Epic, 5★)                          ║
║   Cost: 500 Tokens                                    ║
║   Stats: 100 HP, 50 ATK, "First Strike" passive      ║
║   [BUY] 🔒 Need 50 more Tokens                        ║
║                                                       ║
║ [Arena Champion] (Legendary, 5★)                     ║
║   Cost: 2,000 Tokens                                  ║
║   Stats: 200 HP, 100 ATK, "Unbreakable" passive      ║
║   [BUY] 🔒 Need 1,550 Tokens                          ║
║                                                       ║
║ [Colosseum Banner] (Cosmetic)                        ║
║   Cost: 100 Tokens                                    ║
║   Equip as player title (shows in Arena matches)     ║
║   [BUY]                                               ║
║                                                       ║
║ PACKS:                                                ║
║                                                       ║
║ [Arena Pack] (5 cards, 80% Arena-exclusive)          ║
║   Cost: 300 Tokens                                    ║
║   [BUY]                                               ║
║                                                       ║
║ [Epic Arena Pack] (5 cards, guaranteed Epic/Legendary)║
║   Cost: 1,000 Tokens                                  ║
║   [BUY] 🔒 Need 550 Tokens                            ║
╚═══════════════════════════════════════════════════════╝
```

**Why Token-Only Shop Works**:
- ✅ **Pure skill reward** - Can't buy tokens with money (prevents P2W)
- ✅ **Exclusive cards** - Gladiator/Champion only available via Arena (collector appeal)
- ✅ **Engagement driver** - Daily 5 battles = 100-200 Tokens/day (grind incentive)
- ✅ **Whale limiter** - Even whales must play Arena (skill > spending)

---

### Arena Backend (Week 8, 2 Days)

**ArenaManager.cs** (Singleton):
```csharp
public class ArenaManager : MonoBehaviour
{
    // Matchmaking query (Nakama SQL)
    public async Task<Opponent> FindOpponent()
    {
        int playerLevel = PlayerDataManager.Instance.PlayerLevel;
        string tier = GetArenaTier(playerLevel);
        int minLevel = GetTierMinLevel(tier);
        int maxLevel = GetTierMaxLevel(tier);

        // Query Nakama for random opponent in same tier
        var query = $"SELECT user_id, deck_id, player_level, username, win_rate FROM players WHERE player_level BETWEEN {minLevel} AND {maxLevel} AND arena_tier = '{tier}' ORDER BY RANDOM() LIMIT 1";
        var result = await NakamaClient.Instance.SQLQuery(query);

        // Load opponent's deck from Nakama storage
        var opponentDeck = await LoadOpponentDeck(result.user_id, result.deck_id);

        return new Opponent
        {
            UserId = result.user_id,
            Username = result.username,
            Level = result.player_level,
            WinRate = result.win_rate,
            Deck = opponentDeck
        };
    }

    // Determine arena tier based on player level
    private string GetArenaTier(int level)
    {
        if (level <= 9) return "bronze";
        if (level <= 14) return "silver";
        if (level <= 19) return "gold";
        return "diamond";
    }

    // Reward tokens on battle end
    public void RewardTokens(bool victory)
    {
        int tokens = CalculateTokenReward(victory);
        PlayerDataManager.Instance.ColosseumTokens += tokens;
        SaveToNakama();
    }

    // Calculate token reward based on tier + win/loss
    private int CalculateTokenReward(bool victory)
    {
        string tier = GetArenaTier(PlayerDataManager.Instance.PlayerLevel);
        
        if (tier == "bronze")
            return victory ? UnityEngine.Random.Range(10, 21) : 5;
        if (tier == "silver")
            return victory ? UnityEngine.Random.Range(20, 41) : 10;
        if (tier == "gold")
            return victory ? UnityEngine.Random.Range(40, 81) : 20;
        if (tier == "diamond")
            return victory ? UnityEngine.Random.Range(80, 151) : 40;
        
        return 0;
    }
}
```

**Total Backend Work**: 1 singleton class + Nakama matchmaking = **2 days** (Week 8)

---

### Arena Integration Timeline (Week 8)

**Day 1 (Monday)**: UI Design
- [ ] Arena Home screen (rank, season, battles left, find opponent button)
- [ ] Matchmaking screen (spinner, searching text)
- [ ] Opponent Preview screen (deck display, stats, battle/cancel buttons)

**Day 2 (Tuesday)**: UI Implementation
- [ ] Unity UI Toolkit prefabs (ArenaHomeUI, MatchmakingUI, OpponentPreviewUI)
- [ ] Button callbacks (find opponent, battle, cancel, view market)
- [ ] Victory/Defeat screens (token rewards, record display)

**Day 3 (Wednesday)**: Backend Integration
- [ ] ArenaManager.cs singleton (matchmaking, tier logic, token rewards)
- [ ] Nakama SQL queries (find opponent, load deck, save battle results)
- [ ] Daily battle limit (5 free, 6+ costs Gems, reset timer)

**Day 4 (Thursday)**: Colosseum Market
- [ ] Colosseum Market UI (token shop, exclusive cards, Arena Pack)
- [ ] Token spending (buy cards, buy packs, deduct tokens)
- [ ] Exclusive card data (Gladiator, Arena Champion, cosmetics)

**Day 5 (Friday)**: Testing & Polish
- [ ] Test matchmaking (query speed, opponent diversity, edge cases)
- [ ] Test battles (AI plays opponent deck, victory/defeat rewards)
- [ ] Test token economy (earn rates, market prices, daily limits)
- [ ] Bug fixes (matchmaking failures, AI bugs, token sync)

**Total Time**: 5 days (Week 8) = **Within 8-week MVP timeline** ✅

---

## MVP Timeline Rebalance (8 Weeks Total)

### Original Week 7-8 Plan (Baseline):
- **Week 7**: Progression, Pack Market, Battle Pass, Stamina Refills, Daily Login, Analytics
- **Week 8**: Polish, QA, bug fixes, device testing, build optimization

### New Week 7-8 Plan (With Crafting + PvP):
- **Week 7 (Days 1-5)**: **Crafting System** (UI, backend, monetization, testing)
- **Week 8 (Days 1-5)**: **Arena PvP System** (UI, matchmaking, Colosseum Market, testing)

### What Gets Deferred to Phase 1.1 (Month 2):
- ❌ **Advanced Analytics** (heatmaps, funnel analysis, cohort retention) → Phase 1.1
- ❌ **Battle Pass** (30-day progression, exclusive Legendary) → Phase 1.1
- ❌ **Stamina Refills** (IAP, daily unlimited) → Phase 1.1 (Stamina system stays, refills defer)
- ❌ **Device Testing** (polish iOS/Android builds, framerate optimization) → Phase 1.1

### Why This Works:
- ✅ **Crafting** fixes critical RNG hell (Hearthstone parity)
- ✅ **Arena PvP** adds daily engagement loop (Clash of Clans parity)
- ✅ **Core systems complete** (Tutorial, Combat, Campaign, Crafting, PvP)
- ✅ **Deferred items are non-critical** (Battle Pass nice-to-have, analytics post-launch)

---

## Expected Impact on MVP Ratings

### Before Crafting + PvP (Original MVP):
- **Projected Rating**: ⭐⭐⭐⭐ **4.0-4.2/5**
- **Strengths**: Unique mechanics, F2P-friendly, tactical depth
- **Complaints**: "No crafting, stuck with RNG" / "No PvP, boring after tutorial"

### After Crafting + PvP (Enhanced MVP):
- **Projected Rating**: ⭐⭐⭐⭐ **4.2-4.4/5** (+0.2 stars)
- **Strengths**: "Crafting fixed RNG!" / "Arena PvP is addictive" / "F2P-friendly TCG"
- **Complaints**: "Still no live PvP" / "Tutorial too long" (both defer to Phase 1.1/2)

### Revenue Impact:
- **Scroll Sales**: +$1-2 ARPU/month (10% conversion × $10-20 avg spend)
- **Arena Engagement**: +20% Day 7 retention (daily battle loop)
- **Total ARPU**: $5-7/month (up from $3-5 without Crafting/PvP)

---

## Go/No-Go Decision (MVP Complete)

### GO to Phase 1.1 if:
- ✅ Tutorial completion >70% (discovery-based redesign)
- ✅ Day 7 retention >25% (Arena PvP drives daily play)
- ✅ Crafting usage >30% (players convert dupes to scrolls)
- ✅ Arena battles >3/day avg (engagement metric)
- ✅ Scroll purchases >10% conversion (monetization proven)

### PIVOT if:
- ⚠️ Crafting confusing (players don't understand scroll conversion)
- ⚠️ Arena ignored (players prefer PvE only)
- ⚠️ Token economy broken (whales exploit daily battles)

---

## Summary

**Problem**: MVP lacked crafting (RNG hell) and PvP (late engagement driver)  
**Solution**: Add **Scroll-Based Crafting** (Week 7) + **Async Arena PvP** (Week 8)  
**Timeline**: ✅ **8 weeks maintained** (defer Battle Pass, analytics to Phase 1.1)  
**Expected Impact**: +0.2 stars rating (4.2-4.4/5), +$2 ARPU/month, +20% Day 7 retention

**Recommendation**: ✅ **APPROVE** - Both systems critical for competitive parity, MVP-ready designs, no timeline risk.

---

**Next Steps**:
1. Update [mvp-scope-final.md](mvp-scope-final.md) with Week 7-8 rebalance
2. Update [competitive-analysis.md](competitive-analysis.md) to reflect MVP additions
3. Create crafting-schema.json (6 scroll types, conversion ratios, craft costs)
4. Create arena-schema.json (tiers, matchmaking rules, token rewards)
5. Begin implementation Week 7 (Crafting System)

**Version**: 1.0  
**Status**: Proposed for approval  
**Date**: December 31, 2025
