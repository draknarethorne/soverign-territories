# Trainer Deck Schema

**Version**: 1.0  
**Last Updated**: December 30, 2025  
**Purpose**: Pre-constructed 20-card starter decks for onboarding (inspired by Pokemon Trainer Decks)

---

## Overview

Trainer Decks are **pre-built 20-card decks** given to new players during the tutorial (Step 6 in tutorial-flow.md). They provide an immediate, playable deck without requiring players to understand deck-building complexity.

**Two Deck Types**:
1. **Curated Decks**: Named Epic hero + themed synergy (e.g., "Flame Warlord Deck")
2. **Element Decks**: Random Epic + varied support cards (e.g., "Fire Element Deck")

**Inspiration**: Pokemon Trainer Decks / Battle Boxes (ready-to-play, balanced, teach mechanics)

---

## Key Fields

### Identification
- **deckId**: Unique identifier (pattern: `trainer_[name]`, e.g., `trainer_flame_warlord`)
- **deckName**: Display name shown in selection screen (e.g., "Flame Warlord Deck")
- **deckType**: `curated` (named Epic) or `element` (random Epic)

### Theme
- **element**: Primary element theme (fire, water, earth, wind, dark, light, neutral)
- **guaranteedEpic**: Specific card ID for Curated (e.g., `flame_warlord`) or `"random"` for Element
- **playstyle**: Brief strategy description (e.g., "Aggressive burn stacking", "Defensive sustain")
- **recommendedFor**: Target player archetype (e.g., "Beginners", "Aggressive players")

### Contents
- **cardList**: Exactly **20 cards** with quantities (e.g., `{ cardId: "pyromancer", quantity: 2 }`)
- **rarityDistribution**: Guaranteed breakdown for Element decks (1 Epic, 2-4 Rare, 6-10 Uncommon, 6-10 Common)
- **previewCards**: 5 cards shown in selection screen (includes guaranteed Epic)

### Metadata
- **unlocksAtLevel**: Player level requirement (default: 1 for tutorial decks)
- **isTutorialDeck**: Boolean (true for 6 tutorial options, false for post-tutorial unlocks)
- **schemaVersion**: Integer version for data migration

---

## Mechanics

### Curated Decks (Named Epic + Synergy)
**Example**: Flame Warlord Deck
- **Guaranteed Epic**: Flame Warlord (hero card)
- **Synergy**: Fire units (Pyromancer, Fire Elemental), Burn tactics
- **Fixed Composition**: Exact 20 cards defined in `cardList`
- **Replayability**: Deterministic (same cards every time)

**Design Philosophy**: Teaches cohesive deck themes, introduces specific playstyle

### Element Decks (Random Epic + Varied Support)
**Example**: Fire Element Deck
- **Random Epic**: Any Fire Epic hero (Flame Warlord, Inferno Drake, etc.)
- **Varied Support**: Random Fire units/tactics matching rarity distribution
- **Dynamic Composition**: `cardList` is card pool (20+ cards), random selection on grant
- **Replayability**: High (different Epic each time)

**Design Philosophy**: Teaches element identity, encourages experimentation

---

## Tutorial Integration

**Step 6** in [tutorial-flow.md](../mvp/tutorial-flow.md):
1. Player sees 6 Trainer Deck options (3 Curated, 3 Element)
2. Player selects one (e.g., "Balanced Explorer" = Curated Water deck)
3. System grants exact 20 cards from `cardList`
4. Fallback logic: If player's random pack draw missed cards, grant for free (one-time gift)
5. Remaining 9 cards (31 total - 20 in deck) go to Codex inactive storage

**Trainer Deck Options** (tutorial):
- Aggro Rush (Curated Fire)
- Defensive Builder (Curated Earth)
- Balanced Explorer (Curated Water)
- Fire Element Deck (Element Fire)
- Water Element Deck (Element Water)
- Earth Element Deck (Element Earth)

---

## Differences from Starter Deck Schema

| Feature | Trainer Deck | Starter Deck |
|---------|--------------|--------------|
| **Card Count** | 20 cards (fixed) | 11-20 cards (variable) |
| **Complexity** | High (curated/element types) | Low (simple precon) |
| **Guaranteed Epic** | Yes (always 1 Epic) | No (rarity varies) |
| **Tutorial Use** | Yes (Step 6 selection) | No (post-tutorial unlocks) |
| **Rarity Distribution** | Tracked for Element decks | Not tracked |
| **Fallback Logic** | Auto-grants missing cards | Not specified |

**Use Trainer Deck for**: Tutorial onboarding (Step 6)  
**Use Starter Deck for**: Post-tutorial precon unlocks (Level 5, 10, 15)

---

## Example JSON

### Curated Deck (Flame Warlord)
```json
{
  "deckId": "trainer_flame_warlord",
  "deckName": "Flame Warlord Deck",
  "deckType": "curated",
  "element": "fire",
  "guaranteedEpic": "flame_warlord",
  "cardList": [
    { "cardId": "flame_warlord", "quantity": 1 },
    { "cardId": "pyromancer", "quantity": 2 },
    { "cardId": "fire_elemental", "quantity": 2 },
    { "cardId": "flamestrike_tactic", "quantity": 1 },
    { "cardId": "fire_scout", "quantity": 3 },
    { "cardId": "ember_archer", "quantity": 2 },
    { "cardId": "burn_ward", "quantity": 1 },
    { "cardId": "ash_tower", "quantity": 1 },
    { "cardId": "magma_shield", "quantity": 1 },
    { "cardId": "fire_worker", "quantity": 2 },
    { "cardId": "flame_forge", "quantity": 1 },
    { "cardId": "inferno_tactic", "quantity": 1 },
    { "cardId": "smoke_bomb", "quantity": 1 },
    { "cardId": "fire_sword", "quantity": 1 }
  ],
  "playstyle": "Aggressive burn stacking, overwhelm with early damage",
  "recommendedFor": "Aggressive players who like fast-paced offense",
  "previewCards": ["flame_warlord", "pyromancer", "fire_elemental", "flamestrike_tactic", "ember_archer"],
  "unlocksAtLevel": 1,
  "isTutorialDeck": true,
  "schemaVersion": 1
}
```

### Element Deck (Fire Random)
```json
{
  "deckId": "trainer_fire_random",
  "deckName": "Fire Element Deck",
  "deckType": "element",
  "element": "fire",
  "guaranteedEpic": "random",
  "cardList": [
    { "cardId": "flame_warlord", "quantity": 1 },
    { "cardId": "inferno_drake", "quantity": 1 },
    { "cardId": "pyromancer", "quantity": 2 },
    { "cardId": "fire_elemental", "quantity": 2 },
    { "cardId": "ember_archer", "quantity": 2 },
    { "cardId": "fire_scout", "quantity": 3 },
    { "cardId": "flamestrike_tactic", "quantity": 1 },
    { "cardId": "inferno_tactic", "quantity": 1 },
    { "cardId": "fire_worker", "quantity": 2 },
    { "cardId": "flame_forge", "quantity": 1 },
    { "cardId": "ash_tower", "quantity": 1 },
    { "cardId": "magma_shield", "quantity": 1 },
    { "cardId": "fire_sword", "quantity": 1 },
    { "cardId": "burn_ward", "quantity": 1 }
  ],
  "rarityDistribution": {
    "epic": 1,
    "rare": 3,
    "uncommon": 8,
    "common": 8
  },
  "playstyle": "Varied Fire strategies, learn elemental identity",
  "recommendedFor": "Beginners who want to explore Fire element",
  "previewCards": ["random_epic", "pyromancer", "fire_elemental", "flamestrike_tactic", "ember_archer"],
  "unlocksAtLevel": 1,
  "isTutorialDeck": true,
  "schemaVersion": 1
}
```

---

## Engine Integration

### Server (Nakama)
- **Deck Library**: Store all Trainer Decks in database
- **Grant Logic**: On tutorial Step 6, grant selected deck's 20 cards to player
- **Fallback**: If `cardList` card missing from player inventory, auto-grant (one-time gift)
- **Validation**: Ensure `cardList` totals exactly 20 cards (quantity sum)

### Client (Unity)
- **Selection UI**: Display 6 Trainer Decks with preview cards, playstyle, element icons
- **Preview Rendering**: Show 5 preview cards in carousel
- **Deck Confirmation**: Player confirms choice, server grants cards
- **Codex Update**: Show "New!" badge on granted cards

### Events
- **DeckSelected**: Triggered when player chooses Trainer Deck
- **CardsGranted**: Triggered when 20 cards added to inventory
- **TutorialComplete**: Triggered when deck selection finishes (Step 6)

---

## Validation Rules

**Required Fields**:
- deckId, deckName, deckType, element, guaranteedEpic, cardList, playstyle, recommendedFor, unlocksAtLevel, isTutorialDeck, schemaVersion

**Constraints**:
- `cardList` must total exactly 20 cards (sum of all `quantity` fields)
- `previewCards` must contain exactly 5 card IDs
- `guaranteedEpic` must be specific card ID (Curated) or `"random"` (Element)
- `rarityDistribution` only for Element decks (sum must equal 20)
- `isTutorialDeck` true for first 6 decks (tutorial options)

**Cross-Schema Validation**:
- All `cardId` in `cardList` must exist in card-schema.json
- `element` must match valid elements in card-schema.json
- `guaranteedEpic` card (if specific) must have rarity = Epic

---

## Design Notes

**Why 20 Cards?**
- Matches tutorial card count (20 from packs + 6 from Trainer Deck = 26 total, with overlap)
- Small enough for new players to understand
- Large enough for deck diversity

**Why Curated vs Element?**
- **Curated**: For players who want guided experience (specific hero, clear theme)
- **Element**: For players who want randomness (replayability, explore element)

**Why Guarantee Epic?**
- Every Trainer Deck feels special (players get 1 Epic hero immediately)
- Introduces hero mechanics early (Epic cards have abilities)
- Differentiates Trainer Decks from random packs

---

## Related Schemas

- **[card-schema.json](card-schema.json)** - Defines individual cards in `cardList`
- **[starter-deck-schema.json](starter-deck-schema.json)** - Simpler precon decks for post-tutorial unlocks
- **[pack-schema.json](pack-schema.json)** - Random card packs (contrast with fixed Trainer Decks)
- **[tutorial-schema.json](tutorial-schema.json)** - Step 6 (Trainer Deck selection)

---

**Document Status**: Companion to trainer-deck-schema.json  
**Last Updated**: December 30, 2025  
**Maintained By**: @Soverign-Beast-Mode agent
