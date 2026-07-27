# Deck Progression & Management Rules

**Last Updated**: January 10, 2026  
**Status**: CRITICAL - Defines deck size limits, rarity budgets, unlock progression  
**Related**: [starter-deck-design.md](starter-deck-design.md), [campaign-structure.md](campaign-structure.md), [economy-system.md](economy-system.md)

---

## Overview

**Purpose**: Define how players unlock larger decks, rarity budgets scale, and deck-building constraints.

**Goals**:
1. **Gradual Unlock**: Start simple (20 cards), expand as players learn (40 cards at campaign completion)
2. **Rarity Balance**: Prevent all-Legendary decks, encourage strategic composition
3. **F2P Fairness**: Budget scales with Player Level (free for everyone)
4. **Clear Rules**: No ambiguity (exactly N cards, exactly X rarity points)

---

## Deck Size Progression

### **Deck Size by Player Level**

| Player Level | Max Deck Size | Rarity Budget | How to Unlock |
|--------------|---------------|---------------|---------------|
| 1 (Tutorial) | 20 cards | 64 points | Complete Tutorial Step 5 (choose starter deck) |
| 5 | 25 cards | 84 points | Complete Location 5 (campaign) |
| 10 | 30 cards | 104 points | Defeat Goblin Warlord (Location 10 boss) |
| 15 | 35 cards | 124 points | Complete Location 15 (Monster Lair) |
| 20 | 40 cards | 144 points | Defeat Orc Chieftain (Location 20 boss) |
| 25 | 45 cards | 164 points | Arena PvP unlock (Phase 1.1) |
| 30 | 50 cards | 184 points | Alliance Wars unlock (Phase 2) |

**Formula**:
```
Max Deck Size = 20 + (Player Level ÷ 5) × 5
Rarity Budget = 64 + (Player Level × 4)
```

**Examples**:
- Level 1: 20 cards, 64 points
- Level 10: 30 cards, 104 points
- Level 20: 40 cards, 144 points
- Level 30: 50 cards, 184 points

---

## Rarity Budget System

### **Rarity Point Costs**

| Rarity | Stars | Points | Example Cards |
|--------|-------|--------|---------------|
| Common | 1★ | 1 point | Fire Scout, Aqua Healer, Scorch Elemental |
| Uncommon | 1★ | 2 points | Goblin Raider, Sea Serpent, Earth Warrior |
| Rare | 2★ | 4 points | Ember Legionnaire, Frost Paladin, Rock Golem |
| Epic | 3★ | 8 points | Aria (Flame Knight), Thalor (Tide Guardian), Gaia (Stone Sentinel) |
| Legendary | 5★ | 16 points | Ragnarok (God of Thunder), Merlin (Archmage Eternal) |
| Mythic | 6★ | 32 points | Terra (World Shaper), Malakar (Demon Overlord) |

**Why This System**:
- **Uncommon = 2× Common**: preserves meaningful rarity separation early
- **Rare = 4× Common** (4 points): Specialized units cost more but aren't overpowered
- **Epic = 8× Common** (8 points): Heroes are powerful, limit 1 per deck
- **Legendary/Mythic = 16-32× Common**: Late-game chase cards, very expensive

---

### **Budget Scaling Formula**

```
Rarity Budget = 64 + (Player Level × 4)
```

**Rationale**:
- **Level 1 (64 points)**: 1× Epic hero (8 pts) + 19× Commons (19 pts) = **27 points used** ✅ (plenty of room)
- **Level 10 (104 points)**: 1× Epic hero (8 pts) + 3× Rare units (12 pts) + 26× Commons (26 pts) = **46 points used** ✅
- **Level 20 (144 points)**: 1× Epic hero (8 pts) + 1× Legendary (16 pts) + 5× Rare (20 pts) + 34× Commons (34 pts) = **78 points used** ✅
- **Level 30 (184 points)**: 1× Mythic (32 pts) + 1× Legendary (16 pts) + 10× Rare (40 pts) + 45× Commons (45 pts) = **133 points used** ✅

**Design Goal**: Budget should allow 1-2 high-rarity cards + rest Commons/Uncommons. Prevents all-Epic decks.

---

## Deck Composition Rules

### **Card Limits**

1. **Hero Limit (MVP)**: **Exactly 1 hero card per deck**.
  Why: simplifies balancing and preserves clear deck identity. Phase 2+ may introduce multi-hero formats as explicit alternate modes.

1. **3-of Rule**: **Max 3 copies of same card** (applies to non-heroes)
   - **Example**: Can have 3× Ember Legionnaire, but not 4×
   - **Why**: Prevents mono-card decks (all Goblin Raiders), encourages variety

1. **Rarity Budget**: **Total rarity points ≤ Player Level budget**
   - **Example**: Level 10 player (104 points) cannot field deck worth 105 points
   - **Why**: Prevents pay-to-win (whales can't buy all Legendaries and dominate)

1. **Deck Size Minimum**: **Must use at least 10 cards** (even if max is 50)
   - **Why**: Prevents edge case (Level 30 player with 3-card deck)

---

### **Validation Logic (Pseudocode)**

```csharp
public bool ValidateDeck(Deck deck, int playerLevel)
{
    int maxDeckSize = 20 + (playerLevel / 5) * 5;
    int rarityBudget = 64 + (playerLevel * 4);
    
    // Rule 1: Deck size within bounds
    if (deck.Cards.Count < 10 || deck.Cards.Count > maxDeckSize)
        return false;
    
    // Rule 2: Exactly 1 hero for MVP
    var heroes = deck.Cards.Where(c => c.Type == CardType.Hero).ToList();
    if (heroes.Count != 1)
        return false;
    
    // Rule 3: Max 3 copies of same card
    var duplicates = deck.Cards.GroupBy(c => c.CardId).Where(g => g.Count() > 3);
    if (duplicates.Any())
        return false;
    
    // Rule 4: Rarity budget not exceeded
    int totalRarityPoints = deck.Cards.Sum(c => c.RarityPoints);
    if (totalRarityPoints > rarityBudget)
        return false;
    
    return true;
}
```

---

## Deck Archetypes (Emergent, Not Enforced)

### **Aggro Deck** (Fire-focused)
- **Strategy**: High attack, low defense. Win fast before enemy stabilizes.
- **Example Composition** (Level 10, 30 cards):
  - 1× Aria, Flame Knight (Epic 3★, 8 pts)
  - 3× Ember Legionnaire (Rare 2★, 12 pts)
  - 3× Goblin Raider (Uncommon 1★, 6 pts)
  - 23× Fire Soldier (Uncommon 1★, 46 pts)
  - **Total**: 30 cards, 72 rarity points ✅

**Strengths**: Fast victories (turns 1-10)  
**Weaknesses**: Weak to control (Water decks), loses if battle drags past turn 15

---

### **Control Deck** (Water-focused)
- **Strategy**: High defense, healing. Outlast enemy, win through attrition.
- **Example Composition** (Level 10, 30 cards):
  - 1× Thalor, Tide Guardian (Epic 3★, 8 pts)
  - 3× Frost Paladin (Rare 2★, 12 pts)
  - 3× Water Elemental (Rare 2★, 12 pts)
  - 3× Aqua Healer (Common 0★, 3 pts)
  - 20× Frost Soldier (Uncommon 1★, 40 pts)
  - **Total**: 30 cards, 75 rarity points ✅

**Strengths**: Survives aggro, heals through damage  
**Weaknesses**: Slow to close out games, weak to large-scale AOE

---

### **Midrange Deck** (Earth-focused)
- **Strategy**: Balanced attack/defense. Adapts to enemy strategy.
- **Example Composition** (Level 10, 30 cards):
  - 1× Gaia, Stone Sentinel (Epic 3★, 8 pts)
  - 3× Rock Golem (Rare 2★, 12 pts)
  - 3× Stone Guardian (Rare 2★, 12 pts)
  - 3× Earth Warrior (Uncommon 1★, 6 pts)
  - 20× Boulder Beast (Uncommon 1★, 40 pts)
  - **Total**: 30 cards, 78 rarity points ✅

**Strengths**: Versatile, no hard counters  
**Weaknesses**: No clear win condition, requires skilled play

---

### **Rainbow Deck** (Multi-element, Phase 2+)
- **Strategy**: Mix all elements, gain versatility bonus.
- **Example Composition** (Level 20, 40 cards):
  - 1× Aria (Fire Epic, 8 pts)
  - 1× Ragnarok (Lightning Legendary, 16 pts)
  - 2× Ember Legionnaire (Fire Rare, 8 pts)
  - 2× Frost Paladin (Water Rare, 8 pts)
  - 2× Rock Golem (Earth Rare, 8 pts)
  - 16× Commons + 16× Uncommons (48 pts)
  - **Total**: 40 cards, 96 rarity points ✅

**Strengths**: Counters all mono-element decks (Phase 2 synergy bonus)  
**Weaknesses**: No element-specific bonuses (Fire Aura only buffs Fire units)

---

## Unlock Progression Timeline

### **Tutorial → Location 10** (Level 1 → Level 10)

**Deck Size**: 20 cards → 30 cards (+10)  
**Rarity Budget**: 64 points → 104 points (+40)

**What This Unlocks**:
- Can field 1× Epic hero + 3× Rare units + 26× Commons (solid mid-tier deck)
- Enough budget for multiple Rare units (enables specialized strategies)

**Player Timeline**: ~1 week casual play

---

### **Location 10 → Location 20** (Level 10 → Level 20)

**Deck Size**: 30 cards → 40 cards (+10)  
**Rarity Budget**: 104 points → 144 points (+40)

**What This Unlocks**:
- Can field 1× Legendary card (Ragnarok, Merlin)
- Enough budget for Legendary + Epic hero + 5× Rare units
- True deck diversity (aggro, control, midrange all viable)

**Player Timeline**: ~2 weeks casual play

---

### **Location 20 → Campaign Complete** (Level 20 → Level 30, Phase 2+)

**Deck Size**: 40 cards → 50 cards (+10)  
**Rarity Budget**: 144 points → 184 points (+40)

**What This Unlocks**:
- Can field 1× Mythic card (Terra, Malakar)
- Mythic + Legendary + Epic + 10× Rare units + Commons = dream deck
- Competitive PvP-ready decks

**Player Timeline**: ~3-4 weeks casual play (Arena PvP, Alliance Wars)

---

## Card Acquisition Pacing

### **Cards Needed per Deck Size**

| Player Level | Deck Size | Cards Needed | Cards from Tutorial | Cards from Campaign | Cards from Packs |
|--------------|-----------|--------------|---------------------|---------------------|------------------|
| 1 | 20 | 20 | 20 (15 starter + 5 Welcome Pack) | 0 | 0 |
| 5 | 25 | 25 | 20 | 5 (Locations 1-5) | 0 |
| 10 | 30 | 30 | 20 | 10 (Locations 1-10) | 5 (1 Hero Pack) |
| 15 | 35 | 35 | 20 | 15 (Locations 1-15) | 5 (Daily Login packs) |
| 20 | 40 | 40 | 20 | 20 (Locations 1-20) | 10 (Epic Pack + Daily) |
| 30 | 50 | 50 | 20 | 40 (Campaign complete) | 15 (Packs + Quests) |

**F2P Viability**: Player can reach 40-card deck (Level 20) entirely F2P through tutorial + campaign + daily login. No pack purchases required.

---

## Deck-Building UI Flow

### **Step 1: Select Hero** (Mandatory)
- UI shows all owned heroes (Aria, Thalor, Gaia, etc.)
- Player taps 1 hero
- Hero card "locks in" at top of screen
- Rarity budget updates: **X/Y points used** (X = hero's rarity points, Y = player's budget)

### **Step 2: Add Support Cards** (Fill to max deck size)
- UI shows all owned cards (sorted by rarity: Common → Mythic)
- Player taps cards to add to deck
- Each tap adds 1 copy (max 3 copies per card, except heroes)
- Rarity budget updates in real-time
- **Validation Errors**:
  - "Deck too large (31/30 cards)" — red text, cannot save
  - "Rarity budget exceeded (108/104 points)" — red text, cannot save
  - "Max 3 copies of Ember Legionnaire" — card grayed out

### **Step 3: Save Deck**
- If validation passes: "Deck saved successfully!" (green checkmark)
- If validation fails: "Fix errors before saving" (red X, list of errors)

### **Optional: Deck Presets**
- **Starter Fire Deck** (auto-fill with Fire cards)
- **Starter Water Deck** (auto-fill with Water cards)
- **Starter Earth Deck** (auto-fill with Earth cards)
- **Custom Deck 1-5** (player-created, save/load)

---

## Design Philosophy

**Why These Rules Work**:

1. **Simple Start**: 20 cards (tutorial) is small enough to understand quickly
2. **Gradual Complexity**: +5 cards every 5 levels = predictable unlock schedule
3. **Rarity Budget Fairness**: Whales can't buy power (budget same for F2P vs paid players)
4. **3-of Rule Balance**: Prevents boring mono-decks, encourages variety
5. **Hero Limit Flavor**: 1 hero = deck has identity ("Aria's army" not "3 generic heroes")
6. **F2P Friendly**: Campaign rewards = 60+ cards (enough for competitive deck by Level 20)

---

**Next Steps**:
1. Implement deck validation logic in DeckManager.cs
2. Create deck-building UI mockups (Unity UI Toolkit)
3. Balance rarity budget formula (playtest: is 64 points enough for Level 1?)
4. Design deck preset system (save/load 5 decks per player)
