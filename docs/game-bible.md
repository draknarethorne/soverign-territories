Here is the Final Consolidated Master Design Document (Version 4.1).

This version integrates everything we have discussed: the Maps, Stacking, Campaigns, Cards, Auction House, Chat, and the Expansion Roadmap. It now includes enhanced sections on Combat Mechanics, Progression & Balance, Monetization (pay-for-speed/look-and-feel model), Multiplayer, UI/UX, Technical Integration, and more. Clarifications: 2.5D/2D perspective (no 3D modeling); turn-based with AI auto-battle for AFK defending/joining events; focus on card collecting, deck-building, and positioning decks/cards as game-pieces (heroes/avatars on maps/castles); board game look/feel with decks as cards and game-piece combinations; deterministic combat based on math (power, elements, classes, buffs)—no random dice except possibly in arena battles. Decisions are logic-based. Open-source references added for prototyping. You can copy and paste this entire block into your Google Doc as the single source of truth.

# PROJECT: SOVEREIGN TERRITORIES

## Master Game Design Document (The Complete Codex)

Version: 4.1

Owner: [User] ("The Architect")

# SECTION 1: CORE PHILOSOPHY

"Build the Deck. Rule the Map. Automate the Empire."

A hybrid strategy game combining the territory control of Risk, the deck-building depth of Pokémon, and the tactical progression of Heroes of Might & Magic. The game is built on a "Universal Engine" designed to support multiple themes (Medieval, Sci-Fi, Mythic) within the same ruleset. Perspective: 2.5D and 2D (isometric/board-like views, no full 3D modeling). Turn-based gameplay with AI tactics enabling "auto-battle" in all scenarios for AFK defending/joining monthly/weekly events. Focus: Collecting cards, growing/building decks, positioning decks/cards as game-pieces (heroes/avatars on maps/castles). Board game look/feel: Decks are cards, combined with game-pieces. Combat: Deterministic math-based (power, elements, classes, buffs)—no random dice (except arena). Decisions logic-based. Monetization: "Pay-for-speed" or "pay-for-look-and-feel" model.

## Open-Source References
- Slay the Spire (GitHub): Deck-building mechanics and card collection.
- OpenTTD (GitHub): Board game-style map management and resource control.
- FreeCiv (GitHub): Turn-based strategy with alliances and diplomacy.

# SECTION 2: THE CARD SYSTEM (Assets & Collection)

Everything in the game is a card. Decks represent formations with heroes/units, positioned as game-pieces on maps/castles.

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
- Visuals: Opening a pack is a high-fidelity 2.5D animation (tearing the foil, cards flipping with VFX).

## Open-Source References
- Slay the Spire (GitHub): Gacha and pity systems.
- Hearthstone Clone (GitHub, e.g., "hearthstone-clone"): Card collection and deck-building.
- Card Game Simulator (GitHub): Pack opening animations.

# SECTION 3: THE MAP HIERARCHY (The World)

A "Fractal" world where time scale matches map scale. 2.5D/2D views for board game feel.

## Tier 1: Global Map (Quarterly Season)

- View: 2.5D Continental Globe (isometric projection).
- Gameplay: Alliance Politics. Control "Wonders" for server-wide buffs.
- Control: Based on owning the majority of Tier 2 Capitals.

## Tier 2: State Map (Monthly War)

- View: Regional Kingdom (Hex Grid, 2D top-down).
- Gameplay: Castle Placement. Your physical base sits here.
- Control: Occupying territory here taxes the players in Tier 3.

## Tier 3: County Map (Weekly Reset)

- View: District Scale (~10km, 2D grid).
- Gameplay: Resource Scramble. Procedurally generated every Monday.
- Objective: Capture Gold Mines and Mana Wells for weekly income.

## Tier 4: Local Map (Daily Mission)

- View: Tactical 8x8 Battle Grid (Tabletop Style, 2D).
- Gameplay: PvE Dungeons and PvP Duels.
- Environment: Randomly generated biomes (Desert, Castle Gate, Jungle) based on the location in Tier 3.

## Open-Source References
- OpenTTD (GitHub): Multi-tier map hierarchies and resource management.
- FreeCiv (GitHub): Hex grids and territory control.
- Catan (GitHub clones): Procedurally generated maps and resource scramble.

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

## Open-Source References
- Slay the Spire (GitHub): Campaign progression and loot systems.
- Mario Party Clone (GitHub): Expedition-style mini-games.
- Chess Engines (e.g., Stockfish on GitHub): AI tactics for auto-battle.

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

## 3. Monetization Model (Pay-for-Speed/Look-and-Feel)

- Core Principle: No pay-to-win. Purchases enhance experience without altering balance.
- Pay-for-Speed: Buy energy refills, extra expedition moves, or fast-forward battle animations.
- Pay-for-Look-and-Feel: Purchase card skins, map themes, avatar customizations, or alternate soundtracks.
- Analytics: Track to ensure 80% of revenue from 20% of players; focus on retention via free progression.

## Open-Source References
- EVE Online Market Clones (GitHub): Player-driven auction systems.
- Supercell Analytics (unofficial docs): Monetization models.
- Open-Source IAP Libraries (GitHub, e.g., Unity IAP samples): In-app purchase handling.

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

## Open-Source References
- FreeCiv (GitHub): Alliance systems and diplomacy.
- Discord Bots (GitHub): Chat and translation APIs.
- Nakama Examples (GitHub): Social features and matchmaking.

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

## Open-Source References
- Modding Frameworks (e.g., Unity Modding Tools on GitHub): Expansion support.
- Slay the Spire Expansions (GitHub): Theme additions.
- Open-Source Game Engines (Godot): Universal engine concepts.

# SECTION 8: COMBAT MECHANICS

- **System**: Turn-based on 8x8 grid. Players alternate actions: move, attack, or use tactics. Units have speed stat for initiative. AI tactics enable auto-battle for AFK scenarios.
- **Resolution**: Deterministic: Damage = Attack - Defense (factoring elements, classes, buffs). AoE affects stacked units multiplicatively. PvP ends when one side has no units or objectives captured. No random dice; logic-based.
- **PvE AI**: Scripted tactics; bosses have phases.
- **Alignment**: Pay-for-speed allows skipping animations or auto-resolving non-critical battles.

## Open-Source References
- Chess Engines (Stockfish on GitHub): Deterministic turn-based logic.
- Slay the Spire (GitHub): Card-based combat resolution.
- Battle Chess Clones (GitHub): Grid-based tactics.

# SECTION 9: PROGRESSION & BALANCE

- **Leveling**: Gain XP from battles/campaigns to unlock deck slots and card upgrades (+1 stat per level).
- **Rarity**: Common (1x stats), Rare (2x), Epic (3x), Legendary (5x).
- **Balance**: Soft counters (e.g., fire weak to water). Playtesting ensures no dominant strategies; expansions introduce meta shifts.
- **Alignment**: Free progression; pay-for-speed buys extra quests or energy.

## Open-Source References
- Slay the Spire (GitHub): Progression and rarity systems.
- Hearthstone Balance Tools (unofficial): Meta analysis.
- Unity Analytics Samples (GitHub): Playtesting frameworks.

# SECTION 10: MULTIPLAYER & MATCHMAKING

- **Matchmaking**: Elo-based for PvP; alliances enable guild lobbies.
- **Anti-Cheat**: Server validation; reports/mutes for griefing.
- **Diplomacy**: Voting for war declarations.
- **Alignment**: Pay-for-look-and-feel: Alliance cosmetics.

## Open-Source References
- Nakama Matchmaking (GitHub): Elo and lobbies.
- Photon Examples (GitHub): Anti-cheat and multiplayer.
- FreeCiv (GitHub): Diplomacy voting.

# SECTION 11: USER INTERFACE & EXPERIENCE

- **Design**: Touch-optimized; swipe zoom, drag placement. HUD shows stacked units with health bars.
- **Tutorials**: Interactive overlays.
- **Mobile-First**: Portrait mode, collapsible menus.
- **Alignment**: Pay-for-speed: Skip tutorials.

## Open-Source References
- Unity UI Samples (GitHub): Touch interfaces.
- Godot UI Frameworks (GitHub): Mobile optimizations.
- Slay the Spire UI (GitHub): HUD and tutorials.

# SECTION 12: TECHNICAL INTEGRATION

- **Stack**: Unity client + Nakama server (WebSockets for real-time). Data in JSON/ProtoBuf.
- **Offline**: Cache maps; sync on reconnect. Auto-battle for AFK.
- **Deployment**: Docker for server.
- **Alignment**: Pay-for-look-and-feel: HD assets.

## Open-Source References
- Nakama Unity Client (GitHub): Server integration.
- Unity Netcode Samples (GitHub): Offline sync.
- Docker Compose Examples (GitHub): Deployment.

# SECTION 13: CONTENT PIPELINE & ITERATION

- **Process**: Agile sprints; prototype core loop first.
- **Testing**: A/B for balance; beta feedback.
- **Analytics**: Unity/Nakama for DAU/MAU.
- **Alignment**: Pay-for-speed: Early expansion access.

## Open-Source References
- Unity Version Control (GitHub): Pipeline management.
- A/B Testing Libraries (GitHub): Balance testing.
- Open-Source Analytics (e.g., Matomo on GitHub): DAU tracking.

# SECTION 14: LEGAL & COMPLIANCE

- **Standards**: COPPA for under-13s; GDPR for EU.
- **IAP**: Clear disclosures.
- **Alignment**: Consult legal for monetization.

## Open-Source References
- GDPR Libraries (GitHub): Compliance tools.
- Unity IAP Docs: IAP handling.
- Open-Source Legal Templates (GitHub): Disclosures.

# SECTION 15: SOUND & POLISH

- **Audio**: Thematic music/SFX (e.g., epic battles).
- **Alignment**: Pay-for-look-and-feel: Alternate tracks.

## Open-Source References
- Freesound (GitHub integrations): Audio assets.
- Unity Audio Samples (GitHub): Sound design.
- Open-Source Music Engines (e.g., FMOD samples).

# SECTION 16: EDGE CASES

- **Handling**: Auto-save on disconnect; maintenance notifications.
- **Griefing**: Reports/bans.

## Open-Source References
- Nakama Error Handling (GitHub): Disconnect management.
- Open-Source Chat Moderation (GitHub): Anti-griefing.
- Unity Save Systems (GitHub): Auto-save.

# Immediate Next Steps (Technical)

- Server: Deploy the Docker container (Nakama + CockroachDB).
- Client: Build the "Card Manager" in Unity (2.5D/2D focus).
  - Goal: Verify you can load a JSON file of cards (Medieval + Military) and display them in the "Codex" view.
- Art: Generate 1 Frame and 1 Unit Art for two different themes to prove the visual consistency.
- Prototype: Implement basic combat mechanics using Unity's Tilemap and reference open-source projects like Slay the Spire for card resolution.
- Balance: Set up playtesting framework with Unity Analytics.
- Research: Review open-source references for frameworks (e.g., start with Slay the Spire clone for deck-building).

This document is now your "Constitution." It contains the DNA of the entire project.

