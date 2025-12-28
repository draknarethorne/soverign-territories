Here is the Final Consolidated Master Design Document (Version 4.7).

This version is a complete, line-by-line review and expansion of the entire document. Sections have been re-organized for logical flow (Philosophy -> Core Systems -> Gameplay -> Economy/Social -> Advanced Mechanics -> Technical/Pipeline). Light sections have been expanded with deeper details, examples, and best-of-class concepts from referenced genres (e.g., HoMM for strategy, Slay the Spire for deck-building). Each section now reads as a comprehensive player's guide/reference manual, explaining systems, mechanics, and how to play. This serves as the "cheat-guide" for gameplay, enabling detailed architecture and coding plans.

# PROJECT: SOVEREIGN TERRITORIES

## Master Game Design Document (The Complete Codex)

Version: 4.7

Owner: [User] ("The Architect")

## Table of Contents

1. Core Philosophy
2. The Card System (Assets & Collection)
3. The Map Hierarchy (The World)
4. Gameplay Modes
5. Economy & Trading
6. Social Infrastructure
7. Extension Roadmap (Future Proofing)
8. Combat Mechanics
9. Progression & Balance
10. Multiplayer & Matchmaking
11. User Interface & Experience
12. Technical Integration
13. Content Pipeline & Iteration
14. Legal & Compliance
15. Sound & Polish
16. Edge Cases
17. Immediate Next Steps (Technical)

# SECTION 1: CORE PHILOSOPHY

## Game Tagline

"Build the Deck. Rule the Map. Automate the Empire."

## Overview

Sovereign Territories is a hybrid strategy game that merges the territorial conquest of Risk, the strategic deck-building of Pokémon TCG, and the tactical army management of Heroes of Might and Magic (HoMM). Players collect and customize cards to build powerful decks, deploy them as units on a multi-tiered map, and engage in turn-based battles that can be automated for passive play.

The game features a "Universal Engine" that allows seamless integration of different themes—such as Medieval Fantasy, Sci-Fi, or Mythic—without changing the core ruleset. This ensures endless replayability and expansion potential.

## Visual Style and Perspective

The game adopts a 2.5D isometric view for maps and castles, combined with 2D top-down grids for tactical battles, evoking the feel of classic board games like Catan or tabletop RPGs. No full 3D modeling is used to maintain a stylized, accessible look suitable for mobile and PC platforms.

## Gameplay Loop

1. **Collect Cards**: Acquire cards through packs, quests, or trades.
2. **Build Decks**: Assemble decks with heroes, units, tactics, and equipment.
3. **Deploy on Maps**: Position your decks as game pieces on the world map to control territories.
4. **Engage in Combat**: Fight turn-based battles, either manually or via auto-battle.
5. **Progress and Expand**: Level up, unlock new content, and participate in events.

## Key Mechanics

- **Turn-Based Strategy**: All actions are turn-based, with AI tactics allowing for "auto-battle" modes. This enables AFK gameplay for defending territories or participating in events.
- **Deterministic Combat**: Battles are resolved through math-based calculations involving power, elements, classes, and buffs. No random dice rolls (except in special arena modes), making decisions strategic and predictable.
- **Card as Game Pieces**: Decks are not just collections; they are positioned on maps as heroes and units, combining card game depth with board game positioning.
- **AFK Features**: Automate battles and map actions to allow players to progress even when not actively playing.

## Monetization

The game follows a "pay-for-speed" or "pay-for-look-and-feel" model, ensuring no pay-to-win elements. Players can purchase energy refills, faster animations, cosmetic skins, or alternate soundtracks to enhance their experience without affecting balance.

## Retention and Stickiness

Daily logins reward players with refreshes, events, and progression boosts. Energy systems, spawns, and chances encourage multiple sessions per day.

## Inspirations

Drawing from best-of-class games:

- **Heroes of Might and Magic**: Tactical unit positioning, hero leadership, and map exploration.
- **Slay the Spire**: Deep deck-building with synergies and upgrades.
- **Risk**: Territory control and alliance warfare.

## Open-Source References

- Slay the Spire (GitHub): Deck-building mechanics and card collection.
- OpenTTD (GitHub): Board game-style map management and resource control.
- FreeCiv (GitHub): Alliance diplomacy and turn-based strategy.

# SECTION 2: THE CARD SYSTEM (Assets & Collection)

Everything in Sovereign Territories revolves around cards. Cards represent heroes, units, buildings, tactics, and equipment, which players collect, customize, and deploy. Decks are built from these cards and positioned as game pieces on maps, allowing for strategic depth akin to HoMM's hero-led armies or Slay the Spire's synergistic card combos.

## 1. Card Types

### Heroes

Heroes are unique commanders that lead your formations. They are immortal but can suffer "Wound" timers after defeat, preventing immediate redeployment. Heroes provide passive buffs to attached units, such as increased attack for fire-themed heroes.

- **Examples**: "General Patton" (boosts infantry morale), "Thor" (lightning damage buffs).
- **How They Work**: Position a hero on the map as a game piece; attach units and tactics to form a stack. In combat, the hero's stats combine with the stack for resolution.
- **Inspiration from HoMM**: Heroes level up and gain abilities, similar to HoMM's artifact-wielding commanders.

### Units

Units form the backbone of your army. They include melee fighters, ranged archers, cavalry, and more. In PvP, common units can permadie, creating tension in resource management.

- **Examples**: Basic Archer (ranged, low HP), Elite Cavalry (high speed, charge attacks).
- **How They Work**: Stack multiple unit cards of the same type to form squads. Stats scale with stack size, but AoE attacks can decimate stacks.
- **Inspiration from Slay the Spire**: Units can have status effects, like buffs or debuffs, applied via tactics.

### Buildings

Buildings are defensive or productive structures placed in castle slots. They generate resources or provide buffs.

- **Examples**: Wall (defense boost), Gold Mine (income generator).
- **How They Work**: Played into your castle on the state map. In combat, buildings can be targeted or provide area buffs.
- **Inspiration from Risk**: Fortifications that must be sieged, similar to Risk's territories.

### Tactics

Tactics are AI modules that program auto-battle behavior. Attach them to heroes or units for customized strategies.

- **Examples**: "Focus Healers" (prioritize healing targets), "Flank Left" (maneuver around enemies).
- **How They Work**: Equipped to stacks; AI follows the tactic during auto-battle. Overrides default behavior for tactical depth.
- **Inspiration from Chess Engines**: Pre-programmed strategies, like Stockfish's opening books.

### Equipment

Equipment cards attach to heroes for stat boosts and visuals. Acquired from events or packs.

- **Examples**: "Excalibur Sword" (+attack), "Dragon Scale Armor" (+defense).
- **How They Work**: Socket-compatible; visual effects appear on the hero's game piece (e.g., glowing sword).
- **Inspiration from RPGs**: Gear slots, like in HoMM's artifacts.

## 2. Rarities and Customization

### Basic/Common

Generalized cards for basic builds. No specialization.

- **Stats**: Base values only.

### Rare

Creative variants with minor customization.

- **Stats**: Slight boosts; some options for stat allocation.

### Epic

Named cards with boostable stats via skill trees.

- **Stats**: Customizable points (e.g., +fire damage or +healing). Visual effects on map.
- **Example**: Allocate points to increase HP or speed.

### Legendary

Highly customizable with full skill trees and equipment slots.

- **Stats**: Limits encourage strategy; unique abilities.
- **Example**: Thor with a rage mechanic (attack increases as HP drops).

### Pre-Built Decks

Themed starter decks for quick play. Customize by swapping cards.

## 2.5 Stacking and Formations

### Concept

Cards stack onto a hero to form a unit stack, acting as one entity in battle. Stats combine mathematically.

### Attachment Rules

Compatibility based on tags (e.g., healing tactics only on healer heroes).

### Deck Count Impact

Core cards count fully; attachments are bonus or half-slots.

### Withdrawal

Use special items to detach cards, adding strategy.

## 3. The "Theme" System (Extensions)

Build theme decks for synergy bonuses (e.g., 20 Norse cards grant frost immunity).

## 4. Deck Drawing (The Store)

### Pack System

Buy packs with gems or gold. Pity timers guarantee legendaries.

### Visuals

Animated pack openings with VFX.

## Open-Source References

- Slay the Spire (GitHub): Gacha and pity systems.
- Hearthstone Clone (GitHub): Card collection and deck-building.
- Card Game Simulator (GitHub): Pack opening animations.

# SECTION 3: THE MAP HIERARCHY (The World)

The world is fractal, with time scaling to map size. Shields protect castles temporarily.

## Tier 1: Global Map (Quarterly Season)

### View

2.5D globe.

### Gameplay

Alliance politics; control wonders for buffs.

### Control

Majority of capitals.

## Tier 2: State Map (Monthly War)

### View

Hex grid.

### Gameplay

Castle placement; sieges.

### Terrain

Hexes affect stats.

## Tier 3: County Map (Weekly Reset)

### View

District grid.

### Gameplay

Resource scrambles.

### Terrain

Dynamic biomes.

## Tier 4: Local Map (Daily Mission)

### View

8x8 grid.

### Gameplay

Tactical battles.

### Environment

Biome-based bonuses.

## Open-Source References

- OpenTTD (GitHub): Multi-tier maps.
- FreeCiv (GitHub): Hex grids.
- Catan Clones (GitHub): Procedural maps.

# SECTION 4: GAMEPLAY MODES

Sovereign Territories offers a variety of gameplay modes to cater to different playstyles, from solo PvE progression to large-scale alliance PvP. Each mode integrates the core mechanics of deck-building, map control, and auto-battle, providing depth for casual and hardcore players.

## 4.1 The Saga Campaign (PvE Story Mode)

### Overview
The Saga Campaign is a linear, story-driven PvE journey that serves as the game's tutorial and primary progression path. Players embark on a "hero's journey" across themed maps, battling AI enemies and bosses to unlock new cards, resources, and story elements.

### How to Play
- **Entry**: Accessible from the main menu; requires a basic deck to start.
- **Progression**: Advance through stages by defeating enemies. Each stage is a tactical battle on an 8x8 grid.
- **Boss Stages**: Every 10th stage features a powerful boss with phases (e.g., initial attack phase, then healing phase). Defeating bosses grants rare loot.
- **Energy System**: Uses daily energy (recharges hourly). Run out, and wait or buy refills.
- **Rewards**: Primary source of "Fodder Cards" (common units for deck-building) and XP for leveling.

### Mechanics
- **Story Integration**: Narrative elements tie into the universal themes (e.g., Norse saga with Thor as a boss).
- **Difficulty Scaling**: Stages increase in complexity; optional hard mode for extra rewards.
- **Auto-Battle Option**: For AFK progression, but manual control unlocks full loot potential.

### Player Tips
- Focus on building a balanced deck early; use Saga to test synergies.
- Save energy for boss stages to maximize rewards.

### Inspiration
- Slay the Spire: Run-based progression with escalating difficulty.

## 4.2 The Stacking Mechanic (Tactical Combat Core)

### Overview
Stacking is the core tactical mechanic, allowing players to combine multiple unit cards into squads for efficient mobile gameplay. This addresses screen size limitations while adding strategic depth.

### How to Play
- **Formation**: In deck-building, select multiple cards of the same type (e.g., 5 Archer cards) and place them on one tile as a "Archer Squad."
- **Stats Scaling**: Squad HP and attack multiply (e.g., 5x HP, 5x attack), but vulnerabilities increase.
- **Vulnerabilities**: Highly susceptible to Area of Effect (AoE) attacks like fireballs or artillery, which can wipe entire stacks.
- **Terrain Interaction**: Stacking restricted in dense terrain (e.g., forests prevent large stacks).

### Mechanics
- **Stack Limits**: Max stack size based on deck slots or castle level.
- **Breakdown**: In battle, stacks can be targeted individually or as a group.
- **Strategic Trade-offs**: Larger stacks hit harder but are riskier.

### Player Tips
- Use stacking for PvE rushes, but spread out in PvP to avoid AoE wipes.
- Combine with tactics for auto-battle efficiency.

### Inspiration
- Heroes of Might and Magic: Unit stacks with combined stats.

## 4.3 The Expedition (Weekly Side Game)

### Overview
A mini-board game mode that resets weekly, offering light-hearted, luck-based gameplay. Think Mario Party meets Monopoly, integrated with the game's card economy.

### How to Play
- **Board**: Procedurally generated path with spaces for rewards, penalties, or events.
- **Movement**: Roll dice (or buy extra moves) to advance. Land on spaces to gain cards, gold, or challenges.
- **Objective**: Reach the end first for a grand prize (e.g., legendary card).
- **Multiplayer**: Up to 4 players; compete in real-time or async.

### Mechanics
- **Dice Rolls**: Random but influenced by VIP bonuses (e.g., +1 to rolls).
- **Events**: Spaces trigger mini-games, like quick card battles or trivia.
- **Monetization**: Buy extra moves or dice rerolls for pay-for-speed.

### Player Tips
- Save moves for critical rolls; use expeditions to farm rare cards without energy cost.
- Weekly reset encourages return plays.

### Inspiration
- Mario Party: Fun, random events on a board.

## 4.4 Alliance Events (PVP/PVE Hybrid)

### Overview
Large-scale events where alliances engage in coordinated wars, blending PvP sieges with PvE objectives. Designed for community play with auto-battle support.

### How to Play
- **Setup**: Alliances declare wars on maps; events last hours to days.
- **Phases**: Initial PvE scrambles, then PvP attacks on castles.
- **Participation**: Players contribute decks for auto-battle; limited direct control for key moments (e.g., heal allies).
- **Scale**: Hundreds of players; outcomes based on collective strength.

### Mechanics
- **Auto-Battle Dominance**: Most action is AI-driven; players set tactics beforehand.
- **Limited Interaction**: Short windows for direct commands (e.g., 5-minute "hero moments").
- **Rewards**: Shared based on alliance performance; top contributors get bonuses.

### Player Tips
- Coordinate with alliance chat; focus on strong decks for auto-contribution.
- Use for social bonding and large rewards.

### Inspiration
- FreeCiv: Alliance diplomacy and wars.

## 4.5 Daily/Weekly Challenges & Events

### Overview
Recurring content to maintain engagement, from simple quests to competitive tournaments.

### Daily Challenges
- **Quests**: E.g., "Win 3 PvE battles" or "Collect 10 gold mines."
- **Rewards**: Energy refills, card packs, or spawns.
- **Reset**: Midnight; encourages daily logins.

### Weekly Challenges
- **Tournaments**: PvP brackets with themed decks (e.g., "Fire Elemental Only").
- **Scrambles**: Time-limited map rushes for resources.
- **Leaderboards**: Top players get exclusive skins or titles.

### Mechanics
- **Progress Tracking**: In-game UI shows streaks and completions.
- **Retention Hooks**: Missed days reset streaks, but VIP preserves them.

### Player Tips
- Complete dailies for steady progression; weeklies for big rewards.
- Use auto-battle for efficiency.

### Inspiration
- Slay the Spire: Daily runs; Chess Engines: AI for tournaments.

## Open-Source References

- Slay the Spire (GitHub): Campaign progression and loot systems.
- Mario Party Clone (GitHub): Expedition-style mini-games.
- Chess Engines (e.g., Stockfish on GitHub): AI tactics for auto-battle.

# SECTION 5: ECONOMY & TRADING

The economy in Sovereign Territories is player-driven, with multiple currencies fueling deck-building, map actions, and social features. Trading systems encourage community interaction, while monetization ensures fair progression.

## 5.1 Currencies

### Overview
Four main currencies drive the game's loops: Energy for actions, Gold for in-game purchases, Gems for premium features, and Tokens for exclusive items.

### Energy (Stamina)
- **Purpose**: Powers map movements, battles, and expeditions.
- **Recharge**: Hourly (full reset prompts logins); daily cap.
- **Sources**: Daily rewards, quests, VIP bonuses.
- **Sinks**: All active gameplay; encourages strategic use.

### Gold (Coins)
- **Purpose**: Buys cards, upgrades, and basic items.
- **Sources**: Taxes from territories, battles, mines.
- **Sinks**: Pack purchases, building constructions.

### Gems
- **Purpose**: Hard currency for speed-ups and cosmetics.
- **Sources**: Real-money purchases, events, achievements.
- **Sinks**: Energy refills, pack guarantees, VIP upgrades.

### Sovereign Tokens
- **Purpose**: Rare currency for exclusive skins/themes.
- **Sources**: Quests, leaderboards, seasonal events.
- **Sinks**: Limited-time purchases.

### Player Tips
- Balance energy for dailies; save gems for emergencies.

## 5.2 VIP Levels & Daily Rewards

### Overview
VIP system rewards consistent spending with perks, enhancing retention without pay-to-win.

### How It Works
- **Levels**: Unlocked by gem spending (e.g., Level 1: 100 gems).
- **Perks**: Extra energy, gold multipliers, faster recharges, exclusive packs.
- **Daily Rewards**: Login streaks grant free items; VIP preserves streaks.

### Mechanics
- **Streak Bonuses**: Day 7 gives legendary cards.
- **VIP Exclusives**: Higher levels unlock chat emotes or alliance boosts.

### Player Tips
- VIP for whales; free players rely on streaks.

## 5.3 The Auction House (Player Market)

### Overview
A true free market where players buy/sell cards, fostering economy depth.

### How to Play
- **Listing**: Place cards in virtual stalls; set prices or auctions.
- **Bidding**: Watch auctions; escrow ensures safety.
- **Search**: Filters by rarity, type, price.

### Mechanics
- **Tax**: 10% house cut.
- **Restrictions**: Starting cards unsellable.
- **Offline Mode**: Listings persist.

### Player Tips
- Sell duplicates; buy rares cheaply.

## 5.4 Monetization Model

### Overview
Pay-for-speed (convenience) or pay-for-look-and-feel (cosmetics), no pay-to-win.

### Pay-for-Speed
- Energy refills, battle skips, extra moves.

### Pay-for-Look-and-Feel
- Skins, themes, soundtracks.

### Analytics
- Track 80/20 rule for balance.

### Player Tips
- Optional; free progression viable.

## Open-Source References

- EVE Online Market Clones (GitHub): Player-driven auction systems.
- Supercell Analytics (unofficial docs): Monetization models.
- Open-Source IAP Libraries (GitHub, e.g., Unity IAP samples): In-app purchase handling.

# SECTION 6: SOCIAL INFRASTRUCTURE

Social features build community, from alliances for large-scale play to friends for casual co-op. Integrated with Nakama for real-time interaction.

## 6.1 Alliance System

### Overview
Alliances are guilds for cooperative play, enabling shared resources and joint events.

### How to Play
- **Join/Create**: Search or found alliances; invite players.
- **Hierarchy**: Leader > Generals > Officers > Members; promote via contributions.
- **Bank**: Shared treasury for donations; funds buffs/tech trees.
- **Events**: Joint raids, tournaments; coordinated PvP.

### Mechanics
- **Ranks**: Based on activity/donations; higher ranks unlock perks.
- **Limits**: Server-wide caps to prevent monopolies.

### Player Tips
- Join active alliances for events; contribute regularly for ranks.

## 6.2 Chat & Diplomacy

### Overview
Multi-channel chat with diplomacy tools for PvP/PvE interactions.

### How to Play
- **Channels**: Global, Regional, Alliance, Whispers.
- **Diplomacy**: Set statuses (Neutral/Ally/War); vote on declarations.
- **Translation**: Auto-translate for international players.

### Mechanics
- **Voice Notes/Emojis**: Rich communication.
- **Moderation**: Reports for toxicity.

### Player Tips
- Use alliance chat for coordination; whispers for trades.

## 6.3 Friend System & Gifting

### Overview
Friends enable co-op and gifting for social bonds.

### How to Play
- **Add Friends**: Invite via ID or in-game.
- **Co-op**: Joint PvE battles.
- **Gifting**: Send cards/resources; VIP for bonuses.

### Mechanics
- **Limits**: Daily gifts to prevent spam.
- **Rewards**: Gifting streaks unlock bonuses.

### Player Tips
- Gift commons to friends; co-op for faster progression.

## Open-Source References

- FreeCiv (GitHub): Alliance systems and diplomacy.
- Discord Bots (GitHub): Chat and translation APIs.
- Nakama Examples (GitHub): Social features and matchmaking.

# SECTION 7: EXTENSION ROADMAP (Future Proofing)

The Universal Engine allows seamless expansions without rewrites, adding themes, mechanics, and content for long-term engagement.

## 7.1 Expansion Structure

### Overview
Expansions drop periodically, introducing new themes, cards, and mechanics while maintaining core rules.

### Examples
- **Expansion 1: Storm Rising** (Elemental Theme)
  - Adds: Lightning, Wind elements.
  - Biomes: Floating Islands, Thunder Plains.
  - Mechanics: Chain lightning for AoE; wind buffs movement.
- **Expansion 2: Iron Legion** (Military Theme)
  - Adds: Tanks, Helicopters, Modern Soldiers.
  - Mechanics: "Range" stat increases; "Armor" replaces "Defense."
- **Expansion 3: Valhalla** (Norse Theme)
  - Adds: Viking Heroes, Longships, Frost Giants.
  - Mechanics: "Rage" (attack increases with HP loss).

### Seasonal Content
- Limited-time themes (e.g., Halloween with undead units).
- Exclusive rewards; encourages collection.

## 7.2 Implementation
- **Modding Support**: Community mods via Unity tools.
- **Balance**: Expansions introduce meta shifts for replayability.

## Open-Source References

- Modding Frameworks (e.g., Unity Modding Tools on GitHub): Expansion support.
- Slay the Spire Expansions (GitHub): Theme additions.
- Open-Source Game Engines (Godot): Universal engine concepts.

# SECTION 8: COMBAT MECHANICS

Combat is turn-based, deterministic, and grid-based, with AI support for auto-battle. Inspired by chess and card games.

## 8.1 System Overview

### Turn Structure
- Players alternate actions: move, attack, use tactics.
- Units have speed for initiative order.

### Resolution
- Damage = Attack - Defense, factoring elements, buffs, terrain.
- AoE affects stacks multiplicatively.
- PvP ends when objectives met or units depleted.

### AI Integration
- Tactics program auto-behavior; overrides for AFK.

## 8.2 PvE vs. PvP
- PvE: Scripted enemies with phases.
- PvP: Player decks; Elo-based.

## Open-Source References

- Chess Engines (Stockfish on GitHub): Deterministic turn-based logic.
- Slay the Spire (GitHub): Card-based combat resolution.
- Battle Chess Clones (GitHub): Grid-based tactics.

# SECTION 9: PROGRESSION & BALANCE

Progression is free, with RPG elements for depth. Balance ensures no dominant strategies.

## 9.1 Leveling
- XP from battles unlocks slots/upgrades.

## 9.2 Castle/Lord Leveling
- Levels unlock deck slots; higher for larger armies.

## 9.3 Deck Storage
- Save decks; switch for strategies.

## 9.4 RPG Elements
- Equip items; skill trees for abilities.

## 9.5 Rarities & Balance
- Counters (e.g., fire vs. water); expansions shift meta.

## 9.6 Achievements & Leaderboards
- Badges/titles; global/alliance boards.

## Open-Source References

- Slay the Spire (GitHub): Progression and rarity systems.
- Hearthstone Balance Tools (unofficial): Meta analysis.
- Unity Analytics Samples (GitHub): Playtesting frameworks.

# SECTION 10: MULTIPLAYER & MATCHMAKING

Multiplayer uses Elo for fair PvP; alliances for guilds.

## 10.1 Matchmaking
- Elo-based; alliances enable lobbies.

## 10.2 Anti-Cheat
- Server validation; reports/mutes.

## 10.3 Diplomacy
- Voting for war declarations.

## Open-Source References

- Nakama Matchmaking (GitHub): Elo and lobbies.
- Photon Examples (GitHub): Anti-cheat and multiplayer.
- FreeCiv (GitHub): Diplomacy voting.

# SECTION 11: USER INTERFACE & EXPERIENCE

Touch-optimized UI for mobile; tutorials for onboarding.

## 11.1 Design
- Swipe zoom; HUD with health bars.

## 11.2 Tutorials
- Overlays; progressive unlocks.

## 11.3 Notifications
- Alerts for events.

## Open-Source References

- Unity UI Samples (GitHub): Touch interfaces.
- Godot UI Frameworks (GitHub): Mobile optimizations.
- Slay the Spire UI (GitHub): HUD and tutorials.

# SECTION 12: TECHNICAL INTEGRATION

Unity client + Nakama server; Docker deployment.

## 12.1 Stack
- WebSockets for real-time.

## 12.2 Offline
- Cache/sync.

## Open-Source References

- Nakama Unity Client (GitHub): Server integration.
- Unity Netcode Samples (GitHub): Offline sync.
- Docker Compose Examples (GitHub): Deployment.

# SECTION 13: CONTENT PIPELINE & ITERATION

Agile sprints; analytics for balance.

## 13.1 Process
- Prototype core first.

## 13.2 Testing
- A/B for balance.

## Open-Source References

- Unity Version Control (GitHub): Pipeline management.
- A/B Testing Libraries (GitHub): Balance testing.
- Open-Source Analytics (e.g., Matomo on GitHub): DAU tracking.

# SECTION 14: LEGAL & COMPLIANCE

Standards for safety; IAP disclosures.

## 14.1 Standards
- COPPA, GDPR.

## 14.2 IAP
- Clear disclosures.

## Open-Source References

- GDPR Libraries (GitHub): Compliance tools.
- Unity IAP Docs: IAP handling.
- Open-Source Legal Templates (GitHub): Disclosures.

# SECTION 15: SOUND & POLISH

Thematic audio for immersion.

## 15.1 Audio
- Music/SFX.

## Open-Source References

- Freesound (GitHub integrations): Audio assets.
- Unity Audio Samples (GitHub): Sound design.
- Open-Source Music Engines (e.g., FMOD samples).

# SECTION 16: EDGE CASES

Handling disconnects and griefing.

## 16.1 Handling
- Auto-save.

## 16.2 Griefing
- Reports/bans.

## Open-Source References

- Nakama Error Handling (GitHub): Disconnect management.
- Open-Source Chat Moderation (GitHub): Anti-griefing.
- Unity Save Systems (GitHub): Auto-save.

# Immediate Next Steps (Technical)

Deploy server, build card manager, etc.

# SECTION 1: CORE PHILOSOPHY

"Build the Deck. Rule the Map. Automate the Empire."

A hybrid strategy game combining the territory control of Risk, the deck-building depth of Pokémon, and the tactical progression of Heroes of Might & Magic. The game is built on a "Universal Engine" designed to support multiple themes (Medieval, Sci-Fi, Mythic) within the same ruleset. Perspective: 2.5D and 2D (isometric/board-like views, no full 3D modeling). Turn-based gameplay with AI tactics enabling "auto-battle" in all scenarios for AFK defending/joining monthly/weekly events. Focus: Collecting cards, growing/building decks, positioning decks/cards as game-pieces (heroes/avatars on maps/castles). Board game look/feel: Decks are cards, combined with game-pieces. Combat: Deterministic math-based (power, elements, classes, buffs)—no random dice (except arena). Decisions logic-based. Monetization: "Pay-for-speed" or "pay-for-look-and-feel" model. Stickiness: Daily logins for rewards/refreshes, events, and progression; multiple sessions via energy resets, spawns, and chances.

## Open-Source References
- Slay the Spire (GitHub): Deck-building mechanics and card collection.
- OpenTTD (GitHub): Board game-style map management and resource control.
- FreeCiv (GitHub): Turn-based strategy with alliances and diplomacy.

# SECTION 2: THE CARD SYSTEM (Assets & Collection)

Everything in the game is a card. Decks represent formations with heroes/units, positioned as game-pieces on maps/castles. Flexible system for AFK battles: Base tactics on heroes/units (e.g., aggressive, defensive); attach custom tactics for overrides. Unit types: Fighting/melee, ranged/archers, land/water/air, scouts, mages, vehicles/riders. Stats: Base power, HP, speed, defense; modifiers from elements (fire, water), buffs, terrain.

## 1. Card Types

- Heroes: Unique Commanders (e.g., "General Patton," "Thor"). Immortal but suffer "Wound" timers. They provide passive buffs to the stack they lead.
- Units: The Army. Ranged, Infantry, Cavalry, Tanks, Dragons. If "Common" units die in PvP, they are Lost (Permadeath), creating a constant need for reinforcements.
- Buildings: Structures (Walls, Mines, Towers). Played into "Castle Slots" on the State Map to defend territory or produce Gold.
- Tactics: AI Logic Modules (e.g., "Focus Healers", "Flank Left"). Equipped to Units/Heroes to program their auto-battle behavior.
- Equipment: Weapons/Armor (e.g., "Excalibur Sword," "Dragon Scale Armor"). Cards that attach to Heroes for stat boosts and visual effects. Drawn from special packs or events.

## 2. Rarities and Customization

- **Basic/Common**: Generalized cards (e.g., basic archer, wall). No specialization; used for fodder or basic builds.
- **Rare**: More creative generalized cards (e.g., elite scout, enchanted tower). Some minor customization options.
- **Epic**: Specific named cards (e.g., "Stormbringer the Mage"). Boostable with scrolls/books from PvE, draws, events. Limited points for specialization (skill tree-like: allocate to stats/abilities, e.g., +fire damage or +healing). Visual effects on map figures (e.g., boosted fire stat glows red border).
- **Legendary**: Specific named cards (e.g., "Thor the Thunderer"). Highly boostable; equip weapons/armor for RPG-like customization (e.g., find/equip swords in events). Skill trees for unique abilities. Visual effects (e.g., halos for healing boosts). Not all stats max out; limits encourage strategy.
- **Pre-Built Decks**: Buy themed decks (e.g., fire elemental, with hero, units, tactics, buildings). Customize by swapping cards. Saved decks in storage; loose cards in codex.

## 2.5 Stacking and Formations

- **Concept**: Cards "stack" onto a Hero card to form a single "Unit Stack" (e.g., Hero on top, with attached Tactics, Buffs, Equipment). During battle, the stack acts as one entity; math combines all cards' stats/buffs for combat resolution. Stacks are positioned as game-pieces on maps/castles.
- **Attachment Rules**: Socket-like compatibility—certain cards fit specific Heroes (e.g., healing Tactics only on Heroes with "Healer" tag; no attaching ranged Tactics to melee-only Heroes). Equipment (weapons/armor) attaches to Heroes for RPG boosts.
- **Deck Count Impact**: Core cards (Heroes, Units, Buildings) count fully towards deck/formation size (e.g., 10-card deck limit). Attachments (Tactics, Buffs, Equipment) are "bonus cards" and don't count towards the total, allowing larger effective decks without increasing slots. Alternatively, attachments count as 0.5 slots for balance.
- **Withdrawal**: Use "Special Items" (earned in events) to remove a card from a stack (e.g., to reuse elsewhere), adding risk/reward to stacking.
- **Equipment as Cards**: Equipment (swords, armor) are cards drawn from special packs/events, bought/traded like others. Attach to Heroes for visual effects and stat boosts (e.g., +damage sword).

## 3. The "Theme" System (Extensions)

- Core Set: The base game (Medieval Fantasy).
- Expansion Series: Future content drops (e.g., "Iron Legion" - Modern Military).
- Tag Synergy: Cards have tags (e.g., NORSE, MECH). Building a "Theme Deck" (e.g., 20 NORSE cards) grants synergy bonuses, encouraging players to collect specific sets.

## 4. Deck Drawing (The Store)

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

A "Fractal" world where time scale matches map scale. 2.5D/2D views for board game feel. Shields: Activate temporary protection (24-72 hours) on castles to opt out of PVP attacks (earned via quests or gems).

## Tier 1: Global Map (Quarterly Season)

- View: 2.5D Continental Globe (isometric projection).
- Gameplay: Alliance Politics/PVP. Control "Wonders" (neutral PVE objectives) for server-wide buffs. Limited alliances; wars are siege-like with coordinated attacks.
- Control: Based on owning the majority of Tier 2 Capitals. Zoom in reveals Tier 2 hexes under control.
- Terrain: Global biomes affect alliance buffs (e.g., desert alliances get +gold).

## Tier 2: State Map (Monthly War)

- View: Regional Kingdom (Hex Grid, 2D top-down).
- Gameplay: Castle Placement/PVP with PVE scrambles. Individual commanders place/attack castles; alliances coordinate sieges.
- Control: Occupying territory here taxes the players in Tier 3. Hex ownership determines Tier 3 spawns.
- Terrain: Hex types (mountains, plains) modify building/unit stats (e.g., towers +range on hills).
- Shields: Castle shields prevent PVP raids but allow PVE.

## Tier 3: County Map (Weekly Reset)

- View: District Scale (~10km, 2D grid).
- Gameplay: Resource Scramble/PVE with optional PVP. Weekly campaigns: PVE-only, joint alliance PVE, or PVP vs. one alliance. Players get X turns/day; auto-battle for AFK.
- Objective: Capture Gold Mines and Mana Wells for weekly income. Procedurally generated every Monday.
- Terrain: Dynamic biomes affect unit movement (e.g., swamps slow vehicles).

## Tier 4: Local Map (Daily Mission)

- View: Tactical 8x8 Battle Grid (Tabletop Style, 2D).
- Gameplay: PvE Dungeons and PvP Duels/PVE. Deck vs. deck battles; auto or manual control.
- Environment: Randomly generated biomes (Desert, Castle Gate, Jungle) based on Tier 3 location. Terrain bonuses/penalties (e.g., cover +defense).
- Spawns: Based on Tier 3 ownership; PVE enemies spawn in dungeons.

## Open-Source References
- OpenTTD (GitHub): Multi-tier map hierarchies and resource management.
- FreeCiv (GitHub): Hex grids and territory control.
- Catan (GitHub clones): Procedurally generated maps and resource scramble.

# SECTION 4: GAMEPLAY MODES

## 1. The Saga Campaign (PvE Story)

- Concept: A linear "Journey" map separate from the political world. PVE-focused; auto or manual control.
- Progression: Unlock stages by defeating AI. Every 10th stage is a Boss.
- Resource: Uses "Energy" (daily recharge).
- Loot: The primary source of XP and "Fodder Cards" (Common units).

## 2. The "Stacking" Mechanic (Tactical Combat)

- Problem: Mobile screens are too small for 60 units.
- Solution: Squad Stacking.
  - Play 5 "Archer" cards on one tile = 1 "Archer Squad" Token.
  - Stats: 5x HP, 5x Attack.
  - Risk: Highly vulnerable to Area of Effect (AoE) damage (Fireballs/Artillery). Terrain affects stacking (e.g., no stacking in forests).

## 3. The Expedition (Weekly Side Game)

- Concept: A mini-board game (Mario Party style) that resets weekly.
- Mechanic: Limited daily moves. Roll dice to land on rewards.
- Monetization: Buy extra "Moves" to finish the board before Sunday night.

## 4. Alliance Events (PVP/PVE Hybrid)

- Types: Limited human interaction (direct attacks/heals for short periods) + full auto-battle at scale (turn-based fast for RTS feel).
- Scale: Large alliance vs. alliance; ongoing conquest on maps.
- Options: PVE-only campaigns, PVP vs. one alliance, joint alliance PVE.

## 5. Daily/Weekly Challenges & Events

- Daily: Quests (e.g., win 3 PVE battles) for rewards; energy refreshes, spawns appear.
- Weekly: Themed scrambles, tournaments, or alliance raids. Leaderboards for top performers.
- Retention: Encourages multiple logins; pay-for-speed for boosts.

## Open-Source References
- Slay the Spire (GitHub): Campaign progression and loot systems.
- Mario Party Clone (GitHub): Expedition-style mini-games.
- Chess Engines (e.g., Stockfish on GitHub): AI tactics for auto-battle.

# SECTION 5: ECONOMY & TRADING

## 1. Currencies

- Stamina/Energy: For moves/actions on maps (recharges hourly/daily; full resets prompt logins).
- Gold/Coins: Earned from taxes/maps; used for upgrades/builds.
- Gems: Hard currency (bought with $$); for packs, speed boosts, cosmetics.
- Sovereign Tokens: From quests; for exclusive skins/themes.

## 2. VIP Levels & Daily Rewards

- VIP: Unlocked via gem spending; grants daily bonuses (extra energy, gold multipliers, faster recharges).
- Daily Rewards: Login streaks for free items (cards, energy); refreshes at midnight.

## 3. The Auction House (Player Market)

- Concept: True free market; bidding, watching, search filters, escrow for safety.
- Features: Quick sell, player ratings, featured listings (premium).
- Offline: List in castle stalls.
- Tax: 10% system cut.
- Restriction: Starting cards unsellable.

## 4. Monetization Model (Pay-for-Speed/Look-and-Feel)

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

- Hierarchy: Leader -> Generals -> Officers -> Members (promotions via contributions).
- Bank: Shared treasury; donations (gold/gems) for buffs/tech tree.
- Events: Joint raids, tournaments.
- Ranks: Based on activity/donations.

## 2. Chat & Diplomacy

- Channels: Global, Region, Alliance, Whispers; voice notes/emojis.
- Translation: Auto-translate for international play.
- Diplomacy: Status settings (Neutral/Ally/War); voting for declarations.

## 3. Friend System & Gifting

- Friends: Invite, co-op PVE, gifting cards/resources.
- Gifting: Free; VIP bonuses.

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
- Seasonal Content: Limited-time themes (holidays) with exclusive rewards/cards.

## Open-Source References
- Modding Frameworks (e.g., Unity Modding Tools on GitHub): Expansion support.
- Slay the Spire Expansions (GitHub): Theme additions.
- Open-Source Game Engines (Godot): Universal engine concepts.

# SECTION 8: COMBAT MECHANICS

- **System**: Turn-based on 8x8 grid. Players alternate actions: move, attack, or use tactics. Units have speed stat for initiative. AI tactics enable auto-battle for AFK scenarios. Deck formations: Hero/leader + units + buffs/tactics; calculate rolled-up stats (power, HP, etc.) with modifiers.
- **Resolution**: Deterministic: Damage = Attack - Defense (factoring elements, classes, buffs, terrain). AoE affects stacked units multiplicatively. PvP ends when one side has no units or objectives captured. No random dice; logic-based. Unit types interact (e.g., air ignores land terrain).
- **PvE AI**: Scripted tactics; bosses have phases.
- **Alignment**: Pay-for-speed allows skipping animations or auto-resolving non-critical battles.

## Open-Source References
- Chess Engines (Stockfish on GitHub): Deterministic turn-based logic.
- Slay the Spire (GitHub): Card-based combat resolution.
- Battle Chess Clones (GitHub): Grid-based tactics.

# SECTION 9: PROGRESSION & BALANCE

- **Leveling**: Gain XP from battles/campaigns to unlock deck slots and card upgrades (+1 stat per level).
- **Castle/Lord Leveling**: Your main castle (lord) levels up with XP, unlocking more deck slots (e.g., Level 1: 3 slots, Level 10: 10 slots). Higher levels allow larger armies and more complex tactics.
- **Deck Storage**: Save built decks without dismantling them; switch between saved decks for different strategies (e.g., PvP vs. PvE). Storage limited by castle level.
- **RPG Elements**: Equip weapons/armor on heroes from events/loot; skill trees for heroes (allocate points to abilities like +damage or +healing). Visual effects on equipped items (e.g., glowing sword).
- **Rarity**: Common (1x stats), Rare (2x), Epic (3x), Legendary (5x).
- **Balance**: Soft counters (e.g., fire weak to water). Playtesting ensures no dominant strategies; expansions introduce meta shifts.
- **Achievements & Leaderboards**: Unlock badges/titles for milestones (e.g., conquer 10 hexes). Global/alliance boards for conquests, deck power, donations.
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

- **Design**: Touch-optimized; swipe zoom, drag placement. HUD shows stacked units with health bars. Zoom in/out UI for map layers.
- **Tutorials**: Interactive overlays; progressive unlocks.
- **Push Notifications & Alerts**: Opt-in alerts for energy refills, events, attacks (if shields down).
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

