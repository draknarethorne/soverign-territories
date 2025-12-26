Yes, the previous draft touched on the economy, but to make this a truly complete "Game Bible," we need to explicitly detail the Social Architecture (Chat/Alliances), the Gacha Mechanics (Deck Drawing), and the Trading System (Auction House).

Here is the Final Consolidated Master Design Document (Version 3.0).

This version integrates everything we have discussed: the Maps, Stacking, Campaigns, Cards, Auction House, Chat, and the Expansion Roadmap. You can copy and paste this entire block into your Google Doc as the single source of truth.

# PROJECT: SOVEREIGN TERRITORIES

## Master Game Design Document (The Complete Codex)

Version: 3.0

Owner: [User] ("The Architect")

# SECTION 1: CORE PHILOSOPHY

"Build the Deck. Rule the Map. Automate the Empire."

A hybrid strategy game combining the territory control of Risk, the deck-building depth of Pokémon, and the tactical progression of Heroes of Might & Magic. The game is built on a "Universal Engine" designed to support multiple themes (Medieval, Sci-Fi, Mythic) within the same ruleset.

# SECTION 2: THE CARD SYSTEM (Assets & Collection)

Everything in the game is a card.

## 1. Card Types

- Heroes: Unique Commanders (e.g., "General Patton," "Thor"). Immortal but suffer "Wound" timers. They provide passive buffs to the stack they lead.
- Units: The Army. Ranged, Infantry, Cavalry, Tanks, Dragons. If "Common" units die in PvP, they are Lost (Permadeath), creating a constant need for reinforcements.
- Buildings: Structures (Walls, Mines, Towers). Played into "Castle Slots" on the State Map to defend territory or produce Gold.
- Tactics: AI Logic Modules (e.g., "Focus Healers", "Flank Left"). Equipped to Units/Heroes to program their auto-battle behavior.

## 2. The "Theme" System (Extensions)

- Core Set: The base game (Medieval Fantasy).
- Expansion Series: Future content drops (e.g., "Iron Legion" - Modern Military).
- Tag Synergy: Cards have tags (e.g., NORSE, MECH). Building a "Theme Deck" (e.g., 20 NORSE cards) grants synergy bonuses, encouraging players to collect specific sets.

## 3. Deck Drawing (The Store)

- The Pack System: Players buy digital "Booster Packs" using Gems or Gold.
  - Standard Pack: 5 Cards (Mostly Common/Rare).
  - Theme Pack: 5 Cards (Guaranteed from a specific Series, e.g., "Storm Rising").
- The Pity Timer: "Bad Luck Protection." If you open 19 packs without a Legendary, the 20th pack is Guaranteed Legendary.
- Visuals: Opening a pack is a high-fidelity 3D animation (tearing the foil, cards flipping with VFX).

# SECTION 3: THE MAP HIERARCHY (The World)

A "Fractal" world where time scale matches map scale.

## Tier 1: Global Map (Quarterly Season)

- View: 3D Continental Globe.
- Gameplay: Alliance Politics. Control "Wonders" for server-wide buffs.
- Control: Based on owning the majority of Tier 2 Capitals.

## Tier 2: State Map (Monthly War)

- View: Regional Kingdom (Hex Grid).
- Gameplay: Castle Placement. Your physical base sits here.
- Control: Occupying territory here taxes the players in Tier 3.

## Tier 3: County Map (Weekly Reset)

- View: District Scale (~10km).
- Gameplay: Resource Scramble. Procedurally generated every Monday.
- Objective: Capture Gold Mines and Mana Wells for weekly income.

## Tier 4: Local Map (Daily Mission)

- View: Tactical 8x8 Battle Grid (Tabletop Style).
- Gameplay: PvE Dungeons and PvP Duels.
- Environment: Randomly generated biomes (Desert, Castle Gate, Jungle) based on the location in Tier 3.

# SECTION 4: GAMEPLAY MODES

## 1. The Saga Campaign (PvE Story)

- Concept: A linear "Journey" map separate from the political world.
- Progression: Unlock stages by defeating AI. Every 10th stage is a Boss.
- Resource: Uses "Energy" (daily recharge).
- Loot: The primary source of XP and "Fodder Cards" (Common units).

## 2. The "Stacking" Mechanic (Tactical Combat)

- Problem: Mobile screens are too small for 60 units.
- Solution: Squad Stacking.
  - Play 5 "Archer" cards on one tile = 1 "Archer Squad" Token.
  - Stats: 5x HP, 5x Attack.
  - Risk: Highly vulnerable to Area of Effect (AoE) damage (Fireballs/Artillery).

## 3. The Expedition (Weekly Side Game)

- Concept: A mini-board game (Mario Party style) that resets weekly.
- Mechanic: Limited daily moves. Roll dice to land on rewards.
- Monetization: Buy extra "Moves" to finish the board before Sunday night.

# SECTION 5: ECONOMY & TRADING

## 1. Currencies

- Gold (Soft): Earned via taxes and gameplay. Used for upgrades.
- Gems (Hard): Bought with $$. Used for Packs and Cosmetics.
- Sovereign Tokens: Earned via "Contracts" (Quests). Used for exclusive skins.

## 2. The Auction House (Player Market)

- Concept: A true free market. Players can sell their rare cards to others.
- The "Offline Store": You don't need to be online. List an item in your Castle's "Market Stall."
- The Tax: The System takes a 10% Cut of all sales. This prevents inflation.
- Restriction: "Starting Cards" cannot be sold (prevents re-rolling abuse).

# SECTION 6: SOCIAL INFRASTRUCTURE

## 1. Alliance System

- Hierarchy: Leader -> Generals -> Officers -> Members.
- Bank: Alliances have a shared "Treasury" (Gold/Resources) funded by taxes.
- Tech Tree: Alliances donate resources to unlock buffs (e.g., "+5% Move Speed on Global Map").

## 2. Chat & Diplomacy

- Channels: Global, Region, Alliance, and "Whisper" (Private).
- Translation: Auto-translate feature for international servers (using an API).
- Diplomacy Tools: Alliance Leaders can set status with other Alliances:
  - Neutral: Normal rules.
  - Ally: Cannot attack each other; shared vision on map.
  - War: Attack bonuses active; kill notifications broadcast to all members.

# SECTION 7: EXTENSION ROADMAP (Future Proofing)

The "Universal Engine" allows for endless expansion without code rewrites.

- Expansion 1: "Storm Rising" (Elemental Theme)
  - Adds: Lightning and Wind elements.
  - Biomes: Floating Islands, Thunder Plains.
- Expansion 2: "Iron Legion" (Military Theme)
  - Adds: Tanks, Helicopters, Modern Soldiers.
  - Mechanic: "Range" stat increases; "Armor" replaces "Defense."
- Expansion 3: "Valhalla" (Norse Theme)
  - Adds: Viking Heroes, Longships, Frost Giants.
  - Mechanic: "Rage" mechanic (Attack increases as HP decreases).

# Immediate Next Steps (Technical)

- Server: Deploy the Docker container (Nakama + CockroachDB).
- Client: Build the "Card Manager" in Unity.
  - Goal: Verify you can load a JSON file of cards (Medieval + Military) and display them in the "Codex" view.
- Art: Generate 1 Frame and 1 Unit Art for two different themes to prove the visual consistency.

This document is now your "Constitution." It contains the DNA of the entire project.

