Here is the Final Consolidated Master Design Document (Version 5.0).

This version incorporates Territory/Tile Codex Views, visual figurine/statue representations of deployed cards, deployment limits per territory, and visual upgrades from towns to castles. Everything is card-centric, with figurine visuals based on card stacks and territory levels.

# PROJECT: SOVEREIGN TERRITORIES

## Master Game Design Document (The Complete Codex)

Version: 5.0

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
17. Additional Features for Complete Gamer Experience
18. Immediate Next Steps (Technical)

# SECTION 1: CORE PHILOSOPHY

## Game Tagline

"Build the Deck. Rule the Map. Automate the Empire."

## Overview

Sovereign Territories is a hybrid strategy game that merges the territorial conquest of Risk, the strategic deck-building of Pokémon TCG, and the tactical army management of Heroes of Might and Magic (HoMM). Players collect and customize cards to build powerful decks, deploy them as units on a multi-tiered map, and engage in turn-based battles that can be automated for passive play. A key feature is the PvE Territorial Conquest Campaign, where players build economies on maps against AI opponents, placing building cards for AFK resource production (food, water, lumber, ore, gold) and strategic advantages, allowing safe progression before unlocking PvP alliances at higher levels.

The game features a "Universal Engine" that allows seamless integration of different themes—such as Medieval Fantasy, Sci-Fi, or Mythic—without changing the core ruleset. This ensures endless replayability and expansion potential.

## Visual Style and Perspective

The game adopts a 2.5D isometric view for maps and castles, combined with 2D top-down grids for tactical battles, evoking the feel of classic board games like Catan or tabletop RPGs. No full 3D modeling is used to maintain a stylized, accessible look suitable for mobile and PC platforms.

## Gameplay Loop

1. **Collect Cards**: Acquire cards through packs, quests, trades, or AFK rewards.
2. **Build Decks**: Assemble battle decks with heroes, units, tactics, equipment; build building decks for structures.
3. **Deploy on Maps**: Position battle decks as units on maps; place building cards for defense, production, and AFK resource generation.
4. **Engage in Combat**: Fight turn-based battles, either manually or via auto-battle.
5. **Progress and Expand**: Level up castles/lords, expand territories, participate in PvP alliances (after Level 10), and manage AFK economies.

## Key Mechanics

- **Turn-Based Strategy**: All actions are turn-based, with AI tactics allowing for "auto-battle" modes. This enables AFK gameplay for defending territories or participating in events.
- **Deterministic Combat**: Battles are resolved through math-based calculations involving power, elements, classes, and buffs. No random dice rolls (except in special arena modes), making decisions strategic and predictable.
- **Card as Game Pieces**: Decks are not just collections; they are positioned on maps as heroes and units, combining card game depth with board game positioning.
- **Building Placement and AFK Economy**: Place building cards on map tiles for defense, production, and passive resource generation (food, water, lumber, ore, gold) based on terrain and synergies.
- **PvE to PvP Progression**: Start with safe PvE territorial conquest against AI, building economies; unlock PvP alliances at Level 10 for competitive play.
- **AFK Features**: Automate battles, map actions, and production to allow players to progress even when not actively playing.

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

Buildings are static structures placed on map tiles to provide defensive boosts, resource production, or strategic advantages. Unlike units, buildings are drawn from separate "Building Decks" and can be left on maps for AFK benefits. They include production buildings (e.g., mines, farms), defensive structures (e.g., turrets, walls), and support buildings (e.g., barracks for unit recovery, storage for resource accumulation).

- **Examples**: Gold Mine (produces gold over time), Farm (produces food), Turret (auto-attacks enemies), Barracks (recovers unit HP), Storage Warehouse (increases resource cap).
- **How They Work**: Drawn from building decks or purchased. Placed on specific map tiles (e.g., resource-rich hexes for mines). Provide passive effects like +defense to adjacent tiles or AFK resource generation. In battles, buildings can be targeted for destruction, adding siege mechanics. Limits on placement based on castle/lord level (e.g., Level 1 castle allows 3 buildings).
- **Inspiration from Supreme Commander**: Base-building with production and defense, but card-based placement.

### Building Decks

Separate from battle decks, building decks contain cards for structures. Players build and draw from these decks to place buildings on maps. Synergies exist (e.g., placing a Mill near a Farm boosts food production).

- **Drawing**: Use energy or gold to draw from building decks. Can buy specific cards with gold/gems.
- **Placement**: On PvE maps, players hold multiple castles/forts, each with slots for buildings. Placement affects production (e.g., terrain bonuses: +50% on fertile land).
- **AFK Production**: While offline, placed buildings generate resources based on their level and terrain. E.g., a Level 3 Mine on ore-rich tile produces 10 ore/hour.

### Tactics

Tactics are AI modules that program auto-battle behavior. Attach them to heroes or units for customized strategies.

- **Examples**: "Focus Healers" (prioritize healing targets), "Flank Left" (maneuver around enemies).
- **How They Work**: Equipped to stacks; AI follows the tactic during auto-battle. Overrides default behavior for tactical depth.
- **Inspiration from Chess Engines**: Pre-programmed strategies, like Stockfish's opening books.

## Tactic Data Model (Engine Schema)

The tactic schema for AI behavior has been moved to a standalone spec: [docs/specs/tactic-schema.json](docs/specs/tactic-schema.json).
Use that file for tactic validation, AI simulation, and attachment rules.

### Equipment

Equipment cards attach to heroes for stat boosts and visuals. Acquired from events or packs.

- **Examples**: "Excalibur Sword" (+attack), "Dragon Scale Armor" (+defense).
- **How They Work**: Socket-compatible; visual effects appear on the hero's game piece (e.g., glowing sword).

## Equipment Data Model (Engine Schema)

The equipment schema for hero gear has been moved to a standalone spec: [docs/specs/equipment-schema.json](docs/specs/equipment-schema.json).
Use that file for equipment compatibility, stat calculations, and visual effects.

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

### Card Leveling and Combining

Cards can be leveled up by combining multiple copies (stars) or attaching other cards for boosts. This is done in the Codex view.

- **Combining for Stars**: Merge identical cards to increase star level (e.g., 3x Common Archer → 1x 3-Star Archer with boosted stats). Higher stars provide multiplicative bonuses (e.g., +50% attack per star).
- **Attaching Boosters**: Attach equipment, tactics, or other cards to a base card for temporary or permanent stat boosts. E.g., Attach a "Fire Rune" to boost fire damage.
- **Splitting Stacks**: For a cost (e.g., rare Sovereign Tokens or gems), split a combined card back into components. Useful for redistributing resources.
- **Mechanics**: Combining requires the cards to be in your collection; attached cards can be detached without cost but may lose progress.

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

## 2.6 Card Data Model (Engine Schema)

The authoritative card schema has been moved to a standalone spec for engineering use: [docs/specs/card-schema.json](docs/specs/card-schema.json).
Use that file for client/server serialization, validation, and migrations. The `abilities` and `effects` fields reference the `ability-schema` in `docs/specs/ability-schema.json`.

The deck schema for battle and building decks has been moved to a standalone spec: [docs/specs/deck-schema.json](docs/specs/deck-schema.json).
Use that file for deck validation, slot limits, and card compatibility checks.


## 3. The "Theme" System (Extensions)

Build theme decks for synergy bonuses (e.g., 20 Norse cards grant frost immunity).

## Theme Data Model (Engine Schema)

The theme schema for synergies has been moved to a standalone spec: [docs/specs/theme-schema.json](docs/specs/theme-schema.json).
Use that file for theme validation, bonus calculations, and deck synergy checks.

## 4. Deck Drawing (The Store)

### Pack System

Buy packs with gems or gold. Pity timers guarantee legendaries.

### Visuals

Animated pack openings with VFX.

## Pack Data Model (Engine Schema)

The pack schema for card acquisition has been moved to a standalone spec: [docs/specs/pack-schema.json](docs/specs/pack-schema.json).
Use that file for gacha mechanics, pity systems, and pack validation.

## Open-Source References

- Slay the Spire (GitHub): Gacha and pity systems.
- Hearthstone Clone (GitHub): Card collection and deck-building.
- Card Game Simulator (GitHub): Pack opening animations.

# SECTION 3: THE MAP HIERARCHY (The World)

The world is fractal, with time scaling to map size. Shields protect castles temporarily. Maps support random generation for replayability, with terrain affecting production and battles. Players place building cards on map tiles to build economies, with limits based on castle/lord level.

## Tier 1: Global Map (Quarterly Season)

### View

2.5D globe.

### Gameplay

Alliance politics; control wonders for buffs. In PvE, start small and expand against AI opponents, occupying territories for resources.

### Control

Majority of capitals. Players can hold multiple castles across the map.

### Building Placement

Place castles and forts; each allows building slots (e.g., 5 slots at Level 1, scaling with lord level).

## Tier 2: State Map (Monthly War)

### View

Hex grid.

### Gameplay

Castle placement; sieges. PvE mode allows building decks to place turrets, garrisons, barracks on hexes.

### Terrain

Hexes affect stats and production: Fertile land boosts farms (+food), mountains boost mines (+ore), forests provide cover (+defense).

### Random Generation

Maps are procedurally generated with varying terrain, ensuring replayability like Diablo dungeons.

## Tier 3: County Map (Weekly Reset)

### View

District grid.

### Gameplay

Resource scrambles. Place production buildings on tiles for AFK income.

### Terrain

Dynamic biomes: Water tiles boost fishing huts, dirt tiles for farms.

## Tier 4: Local Map (Daily Mission)

### View

8x8 grid.

### Gameplay

Tactical battles. Buildings placed here provide local buffs (e.g., turret defends a corner).

### Environment

Biome-based bonuses; buildings interact with environment (e.g., windmill on plains for extra production).

## Open-Source References

- OpenTTD (GitHub): Multi-tier maps.
- FreeCiv (GitHub): Hex grids.
- Catan Clones (GitHub): Procedural maps.

## Map Data Model (Engine Schema)

The authoritative map and tile schema has been extracted to a standalone spec: [docs/specs/map-schema.json](docs/specs/map-schema.json).
Use that file for map serialization, pathfinding constraints, and server-side tile validation. Event hooks and production rules are specified in the schema and implementation notes there.

The deployment schema for tile deployments has been moved to a standalone spec: [docs/specs/deployment-schema.json](docs/specs/deployment-schema.json).
Use that file for managing unit/building placements, stack limits, and codex view data.

# SECTION 4: GAMEPLAY MODES

Sovereign Territories offers a variety of gameplay modes to cater to different playstyles, from solo PvE progression to large-scale alliance PvP. Each mode integrates the core mechanics of deck-building, map control, and auto-battle, providing depth for casual and hardcore players.

## 4.1 The Saga Campaign (PvE Story Mode)

### Overview
The Saga Campaign is a linear, story-driven PvE journey that serves as the game's tutorial and primary progression path. Players embark on a "hero's journey" across themed maps, battling AI enemies and bosses to unlock new cards, resources, and story elements.

The campaign schema for Saga progression has been moved to a standalone spec: [docs/specs/campaign-schema.json](docs/specs/campaign-schema.json).

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

The expedition schema for board game mode has been moved to a standalone spec: [docs/specs/expedition-schema.json](docs/specs/expedition-schema.json).

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

## 4.5 Territorial Conquest Campaign (PvE Map Mode)

### Overview
A persistent PvE mode where players engage in turn-based territorial conquest against 1-3 AI opponents on multi-tier maps, emulating Risk with deck-building and economy building. Start small on the global map, build decks, occupy territories for AFK resources, level up castles and lords. Allows safe progression before unlocking PvP.

### How to Play
- **Entry**: Available from start; no prerequisites, but PvP requires reaching Level 10.
- **Setup**: Choose a random or themed map (e.g., fantasy world). Begin with one castle; AI opponents start similarly.
- **Turns**: Turn-based; players move units, place buildings, attack territories. AI progresses in parallel, simulating live opponents.
- **Objectives**: Conquer all enemy capitals or hold key territories for a set time. Can be played in parallel with PvP once eligible.
- **Progression**: As you expand, unlock higher map tiers, more building slots, and stronger AI.

### Mechanics
- **Building Economy**: Draw from building decks to place turrets, garrisons, barracks, mines, farms on map tiles. Limits based on castle/lord level (e.g., Level 1: 3 buildings per castle).
- **AFK Production**: While offline, placed buildings generate resources (food, water, lumber, ore, gold) based on card levels and terrain. E.g., Farm on fertile tile: 5 food/hour.
- **Resource Management**: Spend resources to buy cards, upgrade buildings, or recruit units. Storage buildings increase caps.
- **Multiple Castles**: Hold forts and castles across the map; each provides building slots and defense.
- **Terrain Effects**: Maps have random generation; water boosts fishing, forests lumber, mountains ore. Affects battles (e.g., cover for defense) and production.
- **Replayability**: Random maps allow re-playing for leveling, but diminishing returns after efficiency drops.
- **Territory/Tile Codex Views**: Each occupied territory (castle, fort, town) has a codex view showing deployment slots, card type limits, and current stacks. Players click a tile to see what cards are deployed there and manage deployments.
- **Visual Representations (Figurines/Statues)**: Occupied tiles display figurines/statues representing the stacked cards deployed there. Visual appearance changes based on:
  - **Card Composition**: Different hero types and unit stacks render as unique figurines (e.g., a general with cavalry creates a mounted statue).
  - **Territory Level**: Towns appear as modest structures; leveling to castles upgrades the visual (e.g., castle walls, larger statues).
  - **Stacking**: Multiple cards in a stack combine visually into a layered or grouped figurine.
- **Deployment Limits Per Tile**: Each tile (based on territory level and type) has limits:
  - Max hero slots (e.g., 1 hero per castle tile).
  - Max unit stacks (e.g., 5 unit stacks per castle, 2 per fort).
  - Building placement limits (e.g., 3 buildings per castle, 1 per fort).
  - Type restrictions (e.g., turrets only on walls, farms only on fertile terrain).

### Player Tips
- Focus on PVE to build resources safely; use AFK time to accumulate wealth.
- Balance battle decks for attacks and building decks for economy.
- Upgrade lord/castle to increase slots and production multipliers.
- Use tile codex views to strategically position hero stacks and buildings.
- Watch figurine visuals evolve as you level territories and add cards.

### Inspiration
- Risk: Territorial conquest against AI.
- Supreme Commander: Base-building and resource production on maps.

## 4.6 Daily/Weekly Challenges & Events

### Overview
Recurring content to maintain engagement, from simple quests to competitive tournaments.

The quest schema for daily and weekly challenges has been moved to a standalone spec: [docs/specs/quest-schema.json](docs/specs/quest-schema.json).

### Daily Challenges
- **Quests**: E.g., "Win 3 PvE battles" or "Collect 10 gold mines."
- **Rewards**: Energy refills, card packs, or spawns.
- **Reset**: Midnight; encourages daily logins.

### Weekly Challenges
- **Tournaments**: PvP brackets with themed decks (e.g., "Fire Elemental Only").
- **Scrambles**: Time-limited map rushes for resources.
- **Leaderboards**: Top players get exclusive skins or titles.

The leaderboard schema for competitive rankings has been moved to a standalone spec: [docs/specs/leaderboard-schema.json](docs/specs/leaderboard-schema.json).

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

## Event Data Model (Engine Schema)

The event schema has been moved to a standalone spec for engineering: [docs/specs/event-schema.json](docs/specs/event-schema.json).
Use that file for challenge scheduling, reward distribution, leaderboard calculations, and event participation tracking. Saga campaigns, expeditions, and tournaments are structured in the schema.

# SECTION 5: ECONOMY & TRADING

The economy in Sovereign Territories is player-driven, with multiple currencies fueling deck-building, map actions, and social features. Trading systems encourage community interaction, while monetization ensures fair progression.

## 5.1 Currencies

### Overview
Multiple currencies and resources drive the game's loops: Energy for actions, Gold for purchases, Gems for premium, Tokens for exclusives, and Resources (Food, Water, Lumber, Ore) for building and sustaining empires.

### Energy (Stamina)
- **Purpose**: Powers map movements, battles, and expeditions.
- **Recharge**: Hourly (full reset prompts logins); daily cap.
- **Sources**: Daily rewards, quests, VIP bonuses.
- **Sinks**: All active gameplay; encourages strategic use.

### Gold (Coins)
- **Purpose**: Buys cards, upgrades, and basic items.
- **Sources**: Taxes from territories, battles, mines, AFK production.
- **Sinks**: Pack purchases, building constructions, card buys.

### Resources (Food, Water, Lumber, Ore)
- **Purpose**: Sustain buildings and units; spent on upgrades or sold for gold.
- **Sources**: AFK production from placed buildings (e.g., farms for food, mines for ore), battles, territories.
- **Sinks**: Building maintenance, unit recruitment, trading.
- **Storage**: Buildings like warehouses increase caps; excess decays if over limit.

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

### 5.1.5 AFK Production Mechanics

- **How It Works**: Placed building cards on PvE maps generate resources passively. Production rate depends on building level, terrain bonuses (e.g., +50% on optimal tiles), and synergies (e.g., adjacent buildings boost each other).
- **Examples**: Level 2 Farm on fertile hex: 8 food/hour; Mine on mountain: 6 ore/hour.
- **Limits**: Capped by storage buildings; overflow leads to loss or reduced efficiency.
- **Upgrades**: Level up buildings with resources/gold to increase output.
- **Strategy**: Place strategically for max AFK gains; monitor via UI notifications.

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

## Economy & Trade Data Models (Engine Schemas)

The resource and trade schemas have been moved to standalone specs for engineering: [docs/specs/resource-schema.json](docs/specs/resource-schema.json) and [docs/specs/trade-schema.json](docs/specs/trade-schema.json).
Use those files for currency management, production calculations, auction validation, and marketplace transactions. Sensitive financial data is encrypted and server-only.

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

## Player & Account Data Model (Engine Schema)

The player and alliance schemas have been moved to standalone specs for engineering: [docs/specs/player-schema.json](docs/specs/player-schema.json) and [docs/specs/alliance-schema.json](docs/specs/alliance-schema.json).
Use those files for account storage, leaderboards, matchmaking, and alliance management. Sensitive fields and transactions are described in the schema notes and should remain server-only.

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

Combat in Sovereign Territories is the heart of the game, blending strategic depth with accessibility. All battles are turn-based on an 8x8 grid, ensuring deterministic outcomes based on math rather than luck. This allows players to master tactics while enabling auto-battle for AFK play, making it suitable for both casual and competitive gamers.

The battle schema for combat encounters has been moved to a standalone spec: [docs/specs/battle-schema.json](docs/specs/battle-schema.json).

The reward schema for all game rewards has been moved to a standalone spec: [docs/specs/reward-schema.json](docs/specs/reward-schema.json).

## 8.1 System Overview

The combat system emphasizes planning and execution, where every action counts. Players position their deck-formed units on the grid, then engage in alternating turns. Units are derived from stacked cards, combining stats for powerful formations.

### Turn Structure
- **Initiative**: Determined by unit speed stats; faster units act first.
- **Actions**: Move (limited range), attack (melee/ranged), or activate tactics/buffs.
- **Phases**: Movement phase followed by action phase, preventing simultaneous moves.

### Initiative & Turn Order (Deterministic)

- **Initiative Score** = `BaseSpeed + SpeedBuffs + (StackBonus)` where `StackBonus = log(stackSize + 1)` to give diminishing returns for very large stacks.
- Units are sorted by Initiative Score descending at the start of each round. Ties are broken by `unitId` deterministic ordering.
- Use a fixed simulation tick (e.g., 100ms) for visuals; all authoritative decisions are made on discrete turn boundaries to keep client prediction simple.

### Stack Math (Precise Combination Rules)

- **Stack HP** = `BaseHP × stackSize × HPMultiplier(level)` where `HPMultiplier(level)` is defined per card (e.g., 1 + 0.1*(level-1)).
- **Stack Attack** = `BaseAttack × stackSize × AttackMultiplier(level)`.
- **Stack Defense** = `BaseDefense × (1 + 0.05*(stackSize-1))` (defense scales with diminishing returns to favor numbers but reduce absolute tanking).
- **AoE Interaction**: AoE damage applies to stacks as absolute damage; apply damage to stack HP, then calculate casualties as `floor(damage / BaseHP)` for units removed, leaving fractional HP on remainder.
- **Overkill**: No damage spillover to other stacks unless an ability explicitly states "splash overflow".


### Resolution
Combat resolution is purely mathematical, ensuring fairness. Damage calculations incorporate elements (e.g., fire beats water), class bonuses (e.g., archers vs. infantry), terrain modifiers (e.g., hills boost defense), and buffs from equipment or tactics. Area of Effect (AoE) attacks, like fireballs, multiply damage against stacked units, adding risk-reward to formations.

**Detailed Damage Formula** (inspired by Slay the Spire's clarity):
- Base Damage = (Attacker's Attack Stat × Stack Multiplier) × Elemental Multiplier × Buff Factor
- Elemental Multiplier: 1.5x advantage (e.g., Fire vs. Water), 0.75x disadvantage, 1.0x neutral.
- Defense Reduction: Damage = Base Damage - (Defender's Defense Stat × Terrain Bonus × Stack Defense Multiplier)
- Final Damage: Capped at 0; overkill doesn't carry over unless specified by abilities.
- Example: A stack of 3 Fire Archers (Attack 10 each, total 30) attacking Water Infantry (Defense 5) on neutral terrain: 30 × 1.5 × 1.0 - (5 × 1.0 × 1.0) = 45 - 5 = 40 damage.

**Win/Loss Conditions** (best-in-class from Chess and HoMM):
- **PvE Battles**: Eliminate all enemy units or survive a set number of turns (e.g., defend for 10 turns). Boss battles may require reducing boss HP to 0 across phases.
- **PvP Battles**: Eliminate all opponent units, capture a central objective (e.g., flag on grid), or achieve a point threshold (e.g., control 5+ tiles).
- **Alliance Events**: Alliance with most surviving units or captured territories wins; individual contributions earn personal rewards.
- **Draws**: Rare, resolved by Elo adjustment or rematch; no draws in PvE.

**Building Integration in Combat** (inspired by Civilization's tile improvements):
- Buildings on the battle grid (if the map tile has them) provide passive buffs: e.g., +20% defense for units on fortified tiles, or resource generation interrupts if destroyed.
- Siege Mechanics: Attacking enemy castles requires breaching walls (reduce building HP first), adding a pre-combat phase. Buildings can be targeted for AoE or direct attacks, yielding resources if destroyed.

### AI Integration
Programmable tactics allow players to set AI behaviors, such as "focus healers" or "flank left," enabling auto-battle during AFK scenarios. This keeps the game engaging even when offline, with tactics evolving as players unlock more options.

**Player Agency in Auto-Battle** (balancing automation with control, like in auto-chess games):
- Tactics provide base AI; players can queue "interrupt commands" (e.g., "Heal now" or "Retreat") that trigger at specific moments, with a cooldown to prevent spam.
- "Hero Moments": In key battles, allow 1-2 manual actions per turn during auto-mode, chosen from a simplified menu.
- Override Toggle: Switch to full manual mid-battle, but at a cost (e.g., reduced XP or energy penalty).

## 8.2 PvE vs. PvP Differences

- **PvE Battles**: Feature scripted AI with phases (e.g., a boss starts aggressive, then switches to defensive). Designed for progression, with loot drops tied to performance.
- **PvP Battles**: Player vs. player, using Elo matchmaking for balanced matches. Decks are pitted against each other, with objectives like capturing points or eliminating units.

## 8.3 Advanced Features

- **Stack Vulnerabilities**: Large stacks are AoE magnets, encouraging tactical spreading.
- **Elemental Interactions**: A rock-paper-scissors system (fire > water > earth > fire) adds depth.
- **Buff/Debuff System**: Temporary effects from tactics, lasting 2-5 turns.

## Player Tips
- Experiment with tactics in PvE before PvP.
- Use terrain to your advantage; position archers on hills.

## Open-Source References

- Chess Engines (Stockfish on GitHub): Deterministic turn-based logic.
- Slay the Spire (GitHub): Card-based combat resolution.
- Battle Chess Clones (GitHub): Grid-based tactics.

# SECTION 9: PROGRESSION & BALANCE

Progression in Sovereign Territories is designed to be rewarding and endless, with RPG-like depth to keep players invested. From leveling castles to customizing heroes, every action contributes to long-term growth. Balance is maintained through soft counters and meta shifts, ensuring strategies remain viable while expansions introduce new challenges.

## 9.1 Leveling Mechanics

Players earn XP from battles, quests, and events. This XP unlocks deck slots, allowing larger formations, and card upgrades like stat boosts. Leveling is free and tied to engagement, with milestones granting titles or bonuses.

## 9.2 Castle/Lord Leveling

Your main castle acts as a hub, leveling with XP to unlock features. Higher levels increase deck slots (e.g., Level 10 allows 10-slot decks), enable more complex tactics, and provide passive buffs like increased gold income. At Level 10, players become eligible for PvP alliances and top-tier maps. Players can join alliances earlier, contributing resources and experience for alliance bonuses (e.g., 10% boost to earnings).

## 9.3 Deck Storage and Management

Decks can be saved and switched instantly, supporting multiple strategies. Storage is limited by castle level, encouraging progression. Dismantling isn't required, preserving builds for PvE or PvP.

## 9.4 RPG Elements

Heroes gain skill trees, allocating points to abilities like +damage or healing. Equipment from events adds visuals and stats, creating personalized units.

## 9.5 Rarities and Balance

Cards have rarities affecting stats, with counters (e.g., water counters fire) preventing dominance. Expansions introduce new cards, shifting metas and requiring adaptation.

## 9.6 Difficulty Scaling and Balancing (Best-in-Class from Slay the Spire and Hearthstone)

- **Dynamic Scaling**: Enemy strength scales with player level (e.g., +10% stats per 5 levels). PvE AI adapts tactics based on player performance (e.g., more aggressive after losses).
- **Soft Counters**: Overpowered decks face increased encounter rates with counters (e.g., fire-heavy decks encounter more water enemies). Meta shifts via patches adjust card power levels.
- **Player Feedback Loops**: Post-battle analytics show win rates by card/element; A/B testing on new cards ensures balance.
- **Accessibility Options**: Difficulty modifiers (e.g., -25% enemy HP) for new players, adjustable in settings.

## 9.7 Endgame Content (Inspired by Civilization's Endless Modes)

Beyond max level, focus on infinite progression:
- **Meta Wars**: Seasonal events where top alliances compete in escalating PvP tournaments, with rewards like exclusive themes.
- **Player-Created Challenges**: User-generated maps and decks, rated by community votes, for endless replayability.
- **Infinite PvP Ladder**: Climb ranks with rematches; top tiers unlock cosmetic rewards and influence game updates.
- **Legacy Systems**: Permanent achievements (e.g., "Conqueror of 100 Maps") that persist across seasons, encouraging long-term play.

## 9.8 Achievements and Leaderboards

Achievements reward milestones with badges and unlocks. Leaderboards track conquests, deck power, and donations, fostering competition.

The achievement schema has been moved to a standalone spec: [docs/specs/achievement-schema.json](docs/specs/achievement-schema.json).

## Player Tips
- Focus on castle leveling for endgame power.
- Balance PvE/PvP to maintain progression.

## Progression Data Model (Engine Schema)

The progression schema has been moved to a standalone spec for engineering: [docs/specs/progression-schema.json](docs/specs/progression-schema.json).
Use that file for leveling calculations, unlock validation, VIP perks, and achievement tracking. XP formulas and castle scaling are detailed in the schema notes.

## Open-Source References

- Slay the Spire (GitHub): Progression and rarity systems.
- Hearthstone Balance Tools (unofficial): Meta analysis.
- Unity Analytics Samples (GitHub): Playtesting frameworks.

# SECTION 10: MULTIPLAYER & MATCHMAKING

Multiplayer emphasizes fair, community-driven PvP with alliance support. Matchmaking uses Elo for balanced encounters, while anti-cheat ensures integrity.

## 10.1 Matchmaking System

Elo-based ratings match players of similar skill. Alliances enable guild lobbies for coordinated play, adding strategy beyond individual decks.

## Matchmaking Data Model (Engine Schema)

The matchmaking schema for Elo and lobbies has been moved to a standalone spec: [docs/specs/matchmaking-schema.json](docs/specs/matchmaking-schema.json).
Use that file for rating calculations, lobby management, and anti-cheat enforcement.

## 10.2 Anti-Cheat Measures

Server-side validation prevents exploits. Reports and mutes handle griefing, with bans for severe cases.

## 10.3 Diplomacy Features

Voting systems for war declarations, with chat for negotiations.

The diplomacy schema for alliances and treaties has been moved to a standalone spec: [docs/specs/diplomacy-schema.json](docs/specs/diplomacy-schema.json).

## Player Tips
- Join alliances for better matchmaking and events.

## Open-Source References

- Nakama Matchmaking (GitHub): Elo and lobbies.
- Photon Examples (GitHub): Anti-cheat and multiplayer.
- FreeCiv (GitHub): Diplomacy voting.

# SECTION 11: USER INTERFACE & EXPERIENCE

The UI is touch-optimized for mobile, with intuitive navigation. Tutorials guide new players, while notifications keep veterans engaged.

The UI schema for interface elements has been moved to a standalone spec: [docs/specs/ui-schema.json](docs/specs/ui-schema.json).

## 11.1 Design Principles

Swipe gestures for zooming, drag-and-drop for placement. HUD displays unit health and buffs clearly.

## 11.2 Tutorials and Onboarding

Progressive overlays teach mechanics, from deck-building to combat. Skip options for experienced players.

The tutorial schema for onboarding flows has been moved to a standalone spec: [docs/specs/tutorial-schema.json](docs/specs/tutorial-schema.json).

## 11.3 Notifications and Alerts

Opt-in push notifications for energy refills, attacks, or events.

The notification schema for in-game alerts has been moved to a standalone spec: [docs/specs/notification-schema.json](docs/specs/notification-schema.json).

## 11.4 Accessibility and Inclusivity (Best-in-Class from Modern Games like The Sims)

- **Colorblind Support**: High-contrast modes, color-coded alternatives (e.g., symbols for elements), and customizable UI themes.
- **Simplified Controls**: One-handed mode for mobile, voice commands via Unity's accessibility plugins, and adjustable button sizes.
- **Audio Cues**: Screen reader compatibility, audio descriptions for battles, and sound-based feedback for actions.
- **Difficulty Modifiers**: Reduced animation speeds, auto-skip options, and text-to-speech for tutorials.
- **Internationalization**: Full localization with cultural sensitivity, ensuring inclusive representation in themes.

## 11.5 Codex and Card Views

The Codex is the central hub for viewing, managing, and upgrading cards. No separate castle/town views; everything is card-centric and territory-focused.

- **Global Codex View**: Grid or list of all owned cards, filterable by type (hero, unit, building, etc.), rarity, star level, or placement status (e.g., "Placed on Map X").
- **Map-Specific View**: When viewing a map, overlay or filter shows cards placed on that map, with indicators for their positions and stats. Click on any territory to access its tile codex.
- **Tile/Territory Codex View**: Click on any occupied territory (castle, fort, town) to open a detailed codex showing:
  - All deployed cards (heroes, units, buildings) on that tile as a stack.
  - Available deployment slots and limits (e.g., "1/1 hero slots, 3/5 unit stacks, 2/3 buildings").
  - Card type restrictions and terrain bonuses specific to that tile.
  - **Visual Figurine Representation**: Shows how deployed cards appear as figurines/statues on the tile, with upgrades reflecting territory level (town to castle).
  - Options to add/remove/rearrange cards on the tile.
- **Figurine/Statue System**: Occupied tiles display visual representations based on:
  - **Card Composition**: Hero type + unit stacks render as unique figurines (e.g., cavalry general on horseback).
  - **Territory Level**: Towns show modest structures; castles show grander visuals (walls, banners, larger statues).
  - **Stacking**: Multiple cards visually layer or group into one composed figurine.
- **Card Detail View**: Tap a card to see stats, attached boosts, star level, options to combine/split, and current deployment (e.g., "Deployed on State Map, Blackfort Castle").
- **Combining/Splitting UI**: Drag-and-drop to merge cards for stars or attach boosters. Splitting costs resources (e.g., 100 Sovereign Tokens).
- **Filters and Search**: Search by name, filter by unplaced/placed/deployed, view by deck, or filter by territory/map.

### Player Tips
- Use the Codex to plan upgrades before placing cards on maps.
- Check map views to see card distributions for strategy.

## Player Tips
- Use tutorials to master stacking early.

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

## 12.3 Cross-Platform Sync and Features (Inspired by Unity's Multi-Platform Best Practices)

- **Account Linking**: Unified accounts across mobile (iOS/Android), PC (Windows/Mac), and web via Nakama's authentication, with cloud saves for seamless progression.
- **Platform Optimizations**: Touch-first UI for mobile, mouse/keyboard support for PC, with adaptive controls (e.g., swipe vs. click-and-drag).
- **Sync Mechanics**: Real-time sync for multiplayer; offline queue for actions, resolving on reconnect. Data integrity via conflict resolution (e.g., last-write-wins for non-critical changes).
- **Performance**: Unity's Addressables for asset loading, ensuring smooth cross-device play without data loss.

## 12.4 Network Model & Determinism

- **Server-Authoritative Model**: All combat resolution, card state changes, economy transactions, and matchmaking decisions occur server-side. Clients send intents/commands; server validates and returns state deltas.
- **Deterministic Simulation for Replays**: Combat logs should include a compact deterministic event log so clients can replay battles for VODs without resimulating randomness.
- **Latency Handling**: Use client-side prediction for movement visuals, but require server reconciliation for authoritative state; use an action queue with sequence numbers.
- **Tick Rate**: Use a fixed authoritative tick (e.g., 10 ticks/sec) for multiplayer interactions; turn actions are batched on turn boundaries for tactical matches.

## 12.5 Analytics, Instrumentation & Testing Hooks

- **Event List (minimum)**: `battle_start`, `battle_end`, `battle_action`, `card_combined`, `card_split`, `purchase`, `auction_listing`, `match_found`, `match_result`, `resource_produced`, `building_destroyed`, `vip_purchase`.
- **Client Tags**: Include `clientVersion`, `platform`, `region`, and `schemaVersion` in telemetry to correlate issues.
- **A/B Testing Hooks**: Feature flags server-side to roll out balancing changes and see win-rate deltas.
- **Automated Playtests**: Headless bots that run thousands of simulated matches to identify balance outliers before patching.

## 12.6 Economy Controls & Anti-Cheat

- **Inflation Controls**: Sink design (crafting costs, maintenance, storage decay) with weekly monitoring metrics (currency velocity, top percent hoarding).
- **Server Validation**: All currency and inventory changes validated on server; client-only UI ops never change authoritative state.
- **Anti-Cheat**: Server-side rate limits, anomaly detection for impossible actions (e.g., combining more copies than owned), and signed receipts for IAP validation.
- **Rollback & Dispute**: Maintain reversible transaction logs for manual audits and automated rollback if fraud detected.

## Open-Source References

- Nakama Unity Client (GitHub): Server integration.
- Unity Netcode Samples (GitHub): Offline sync.
- Docker Compose Examples (GitHub): Deployment.

# SECTION 13: CONTENT PIPELINE & ITERATION

Sovereign Territories follows an agile development methodology inspired by best-in-class live service games like Clash Royale (Supercell) and League of Legends (Riot Games). The pipeline emphasizes rapid prototyping, data-driven balance, and continuous iteration based on player feedback.

## 13.1 Development Process

### Agile Sprint Structure
- **2-Week Sprints**: Feature development, testing, and deployment
- **Daily Standups**: 15-minute team syncs on progress and blockers
- **Sprint Planning**: Prioritize features based on player data and roadmap
- **Retrospectives**: Post-sprint reviews to improve process

### Prototyping Philosophy
- **Core First**: Implement card system, combat, and economy before polish
- **Vertical Slice**: Complete one gameplay mode end-to-end before expanding
- **Throwaway Prototypes**: Rapid experiments to validate mechanics (1-3 days)
- **Playable Builds**: Weekly playable builds for internal testing

### Content Creation Pipeline
1. **Design**: Game designers create card/map specs using schemas
2. **Art**: Artists create assets (2.5D sprites, UI elements, VFX)
3. **Implementation**: Engineers integrate using Unity + Nakama
4. **Testing**: QA validates functionality and balance
5. **Deployment**: Server-side updates via Nakama (no client download for data)

### Version Control & Collaboration
- **Git Workflow**: Feature branches → PR → Code review → Merge to main
- **Unity Collaborate**: Scene and asset versioning
- **Schema Versioning**: All schemas have `schemaVersion` for migrations
- **Changelog**: Auto-generated from Git commits for patch notes

## 13.2 Testing & Quality Assurance

### Automated Testing (Inspired by Riot Games)
- **Unit Tests**: 80% code coverage for core systems (combat math, pathfinding)
- **Integration Tests**: Server-client communication, matchmaking, economy
- **Headless Bots**: Simulate 1000+ AI matches for balance testing
- **Regression Tests**: Prevent old bugs from reappearing
- **CI/CD**: GitHub Actions runs tests on every commit

### Playtesting
- **Internal Alpha**: Weekly team playtests (30-60 minutes)
- **Closed Beta**: 100-1000 external testers for 4-8 weeks
- **A/B Testing**: Test card balance, UI changes, pricing (see Section 13.3)
- **Focus Groups**: Qualitative feedback on new features

### Balance Testing
- **Win Rate Analysis**: Target 48-52% win rate for all card archetypes
- **Meta Tracking**: Monitor deck popularity, adjust overused/underused cards
- **Simulation**: Run 10,000+ simulated battles with different deck compositions
- **Patch Cadence**: Balance updates every 2 weeks, major patches monthly

### Performance Testing
- **Load Testing**: Stress test servers with 10,000+ concurrent players
- **Mobile Optimization**: Target 60 FPS on mid-tier devices (iPhone 12, Samsung S21)
- **Network Testing**: Simulate poor connections (high latency, packet loss)
- **Memory Profiling**: Keep RAM usage < 1GB on mobile

## 13.3 Analytics & Data-Driven Design (Inspired by Supercell)

### Key Performance Indicators (KPIs)
- **Retention**: Day 1 (>40%), Day 7 (>20%), Day 30 (>10%)
- **Engagement**: Sessions/day (2-3), Session length (15-30 min)
- **Monetization**: ARPU (>$0.50), ARPPU (>$10), Conversion rate (>3%)
- **Technical**: Crash rate (<1%), Load time (<2 seconds)

### A/B Testing Framework
- **Feature Flags**: Server-side toggles for gradual rollout (10% → 50% → 100%)
- **Variants**: Test 2-3 variants simultaneously (e.g., card cost 3 vs 4 vs 5)
- **Statistical Significance**: Minimum 10,000 players per variant, p < 0.05
- **Rollback**: Instant revert if metrics degrade (e.g., retention drops >5%)

### Analytics Events (See session-schema.json)
Minimum tracked events:
- `battle_start`, `battle_end`, `battle_action`
- `card_combined`, `card_split`, `purchase`
- `auction_listing`, `match_found`, `match_result`
- `resource_produced`, `building_destroyed`, `vip_purchase`

### Dashboards & Monitoring
- **Real-Time**: Grafana dashboards for live metrics (DAU, revenue, errors)
- **Historical**: BigQuery/Redshift for deep analysis (cohorts, funnels)
- **Alerts**: PagerDuty for critical issues (crash rate spike, server downtime)
- **Player Support**: Tools to view individual player states for debugging

## 13.4 Live Operations (Inspired by Clash Royale)

### Content Cadence
- **Weekly**: Expeditions, limited-time offers, alliance events
- **Bi-Weekly**: Balance patches, bug fixes
- **Monthly**: New cards (3-5), seasonal themes
- **Quarterly**: Expansions (50+ cards, new maps, mechanics)

### Seasonal Content
- **Seasons**: 3-month cycles with unique themes (e.g., Norse, Sci-Fi)
- **Battle Pass**: 50-tier progression with exclusive rewards
- **Leaderboards**: Seasonal rankings reset every quarter
- **Meta Shifts**: Intentional balance changes to keep game fresh

### Community Engagement
- **Patch Notes**: Transparent communication of changes
- **Developer Blogs**: Behind-the-scenes on design decisions
- **Social Media**: Daily content on Twitter, Reddit, Discord
- **Feedback Loops**: Monthly surveys, in-game feedback buttons

## 13.5 Content Tools & Automation

### Schema-Driven Development
- **JSON Schemas**: All game data validated against schemas (see docs/specs/)
- **Code Generation**: TypeScript and C# types auto-generated from schemas
- **Hot Reloading**: Server-side data updates without client patches
- **Version Migration**: Automated schema migrations on updates

### Content Editors
- **Unity Editor**: Custom inspectors for card creation, map editing
- **Web Tools**: Internal dashboards for balancing, event scheduling
- **Spreadsheets**: Google Sheets integration for rapid iteration

## Open-Source References

- Unity Version Control (GitHub): Pipeline management and collaboration
- A/B Testing Libraries (GitHub, e.g., Growthbook): Feature flags and experimentation
- Open-Source Analytics (e.g., Matomo, PostHog on GitHub): DAU tracking and funnels
- Unity Test Framework (GitHub): Automated testing examples
- Grafana (GitHub): Real-time dashboards and monitoring

# SECTION 14: LEGAL & COMPLIANCE

Sovereign Territories adheres to international standards for player safety, data privacy, and fair monetization. Compliance is built into the game's core design, not bolted on later.

## 14.1 Privacy & Data Protection

### GDPR (General Data Protection Regulation)
**Applies to**: All players in EU, EEA, UK

**Requirements**:
- **Consent**: Explicit opt-in for telemetry, marketing, cookies (see session-schema.json)
- **Right to Access**: Players can download their data via in-game menu
- **Right to Erasure**: Account deletion removes all PII within 30 days
- **Data Minimization**: Only collect necessary data (no tracking beyond gameplay)
- **Privacy Policy**: Clear, accessible policy in 10+ languages
- **Data Portability**: Export account data in JSON format

**Implementation**:
- Session schema tracks consent flags (`telemetryConsent`, `marketingConsent`)
- Server-side anonymization of device IDs, IP addresses
- No third-party analytics without consent
- Cookie banner on web version

### CCPA (California Consumer Privacy Act)
**Applies to**: Players in California, USA

**Requirements**:
- **Do Not Sell**: Players can opt out of data sharing
- **Disclosure**: List all data collected and shared with third parties
- **Deletion**: Same as GDPR (30-day window)

**Implementation**:
- "Do Not Sell My Info" link in settings
- No sale of player data to third parties (we don't sell data, period)

### COPPA (Children's Online Privacy Protection Act)
**Applies to**: Players under 13 in USA

**Requirements**:
- **Age Gate**: Ask for birthdate on first launch
- **Parental Consent**: Require verifiable parental consent for <13
- **Limited Data**: No behavioral advertising, location tracking for <13
- **No Chat**: Disable chat for <13 or use pre-approved messages only

**Implementation**:
- Age verification on account creation
- If <13: Restricted mode (no chat, limited data collection, no ads)
- Parent email verification via COPPA-compliant service (e.g., SuperAwesome)

### Data Security
- **Encryption**: All data encrypted at rest (AES-256) and in transit (TLS 1.3)
- **Access Control**: Role-based access to player data (engineers, support, analytics)
- **Audit Logs**: Track all data access for compliance audits
- **Breach Notification**: Notify affected players within 72 hours of breach

## 14.2 In-App Purchase Compliance

### Platform Policies
**Apple App Store**:
- No misleading IAP descriptions
- Clear pricing in local currency
- Restore purchases button for non-consumables
- Family Sharing support for non-consumables
- No "loot boxes" without odds disclosure

**Google Play**:
- No deceptive practices (fake urgency, hidden costs)
- Odds disclosure for randomized items (card packs)
- Refund policy (14 days, no questions asked)
- Age-appropriate content ratings

### Fair Monetization Principles
- **No Pay-to-Win**: Paying players don't get gameplay advantages (pay-for-speed, cosmetics only)
- **Transparent Odds**: Pack opening shows exact probabilities (e.g., 5% legendary)
- **Pity System**: Guaranteed legendary after 30 packs (documented in pack-schema.json)
- **No Dark Patterns**: No fake timers, manipulative UI, or predatory tactics
- **Clear Pricing**: All prices shown in local currency before purchase
- **No Surprise Charges**: Explicit confirmation before all purchases

### IAP Disclosures
- **Terms of Service**: Linked in store, accessible from settings
- **Refund Policy**: Apple/Google handle refunds per platform policy
- **Currency Disclaimer**: "Gems are virtual currency with no real-world value"
- **Age Restriction**: "In-app purchases available. Parental supervision recommended."

### Odds Disclosure (for Card Packs)
Example from pack opening screen:
```
Card Pack Odds:
- Common: 70%
- Rare: 20%
- Epic: 8%
- Legendary: 2%
Pity system: Guaranteed legendary within 30 packs
```

## 14.3 Content Rating & Age Appropriateness

### ESRB (USA): E10+ (Everyone 10+)
**Reasoning**: Fantasy violence (card battles), mild combat themes
**Content Descriptors**: Fantasy Violence

### PEGI (Europe): PEGI 7
**Reasoning**: Non-realistic violence, no inappropriate language
**Content Descriptors**: Violence

### Platform Compliance
- **Apple**: 9+ rating (Infrequent/Mild Cartoon or Fantasy Violence)
- **Google**: IARC rating (Everyone 10+)

### Content Guidelines
- **No Gore/Blood**: Card battles are stylized, not realistic
- **No Profanity**: Chat has profanity filter, pre-approved emotes
- **No Gambling**: Card packs are skill-based progression, not gambling
- **Cultural Sensitivity**: Diverse themes, no stereotypes or offensive content

## 14.4 Community Safety & Moderation

### Chat Moderation
- **Profanity Filter**: Auto-filter offensive words (customizable per region)
- **Report System**: Players can report toxic behavior, spam, harassment
- **Mute/Block**: Players can mute/block individuals
- **Moderators**: Human review of reports, warnings → temporary bans → permanent bans

### Anti-Harassment Policy
- **Zero Tolerance**: Hate speech, threats, doxxing = instant ban
- **Appeals Process**: Players can appeal bans via support ticket
- **Transparency**: Monthly reports on moderation actions

### Alliance Moderation
- **Leader Tools**: Kick members, set alliance policies
- **Report Alliance**: Players can report entire alliances for organized harassment

## 14.5 Intellectual Property

### Trademarks
- "Sovereign Territories" trademark filed in US, EU, Japan
- Logo, icon, card art protected under copyright

### User-Generated Content
- **Alliance Names**: Prohibited names (profanity, trademarks, hate speech)
- **Custom Decks**: Players own their deck compositions, not the cards
- **Fan Art**: Encourage fan art, credit creators, don't monetize without permission

### Third-Party Assets
- **Licensed Assets**: Unity Asset Store, Freesound (Creative Commons)
- **Attribution**: Credit third-party assets in game credits
- **Open-Source**: Nakama, Unity packages (comply with licenses)

## 14.6 Terms of Service & EULA

### Key Clauses
- **Account Ownership**: Accounts owned by the company, not players
- **Virtual Currency**: No real-world value, no refunds except as required by law
- **Cheating**: Use of hacks, bots, exploits = ban
- **Termination**: Company reserves right to terminate accounts for ToS violations
- **Dispute Resolution**: Binding arbitration (USA), courts (EU)

### Updates & Communication
- **ToS Updates**: 30-day notice before major changes
- **Email Notifications**: Critical updates emailed to players
- **In-Game Notices**: Patch notes, event announcements

## 14.7 Regional Considerations

### China
- **Real-Name Registration**: Required by law
- **Playtime Limits**: Minors limited to 3 hours/week
- **No Loot Boxes**: Packs must show exact contents or odds

### South Korea
- **Shutdown Law**: No gameplay for minors midnight-6am
- **Probability Disclosure**: All randomized rewards must show odds

### Japan
- **Kompu Gacha Ban**: No "complete the set" mechanics
- **Gambling Laws**: Card packs comply with non-gambling regulations

## Open-Source References

- GDPR Compliance Libraries (GitHub): Cookie consent, data export tools
- Unity IAP Documentation: Platform-compliant purchase flows
- Open-Source Legal Templates (GitHub): Terms of Service, Privacy Policy templates
- COPPA Compliance Services: SuperAwesome, Privo for age verification
- IARC Rating System: International Age Rating Coalition for content ratings

# SECTION 15: SOUND & POLISH

Audio design in Sovereign Territories creates immersion, provides feedback, and enhances accessibility. Inspired by best-in-class games like The Witcher 3 (adaptive music) and The Last of Us Part II (accessibility), our audio system is both functional and artistic.

The audio schema for all sound assets has been moved to a standalone spec: [docs/specs/audio-schema.json](docs/specs/audio-schema.json).

## 15.1 Music Composition

### Adaptive Music System (Inspired by The Witcher 3)
- **Layered Tracks**: Music dynamically changes based on game state
  - **Exploration**: Calm, ambient base layer
  - **Combat Start**: Add percussion layer
  - **Low HP**: Add intense string layer
  - **Victory**: Transition to triumphant fanfare
- **Seamless Transitions**: Crossfade between layers (2-3 seconds)
- **Theme Consistency**: Each theme (medieval, sci-fi, norse) has unique music palette

### Music Categories
- **Main Menu**: Epic orchestral theme, sets tone for game
- **Map Exploration**: Ambient, territory-specific (forests = woodwinds, mountains = brass)
- **Battle Music**: Intense, rhythmic, escalates with battle intensity
- **Victory/Defeat**: Short stingers (5-10 seconds)
- **Expedition Board Game**: Upbeat, playful (Mario Party-inspired)
- **Campaign Story**: Narrative-driven, thematic per campaign

### Composition Style
- **Medieval Theme**: Orchestral (strings, brass, woodwinds), Celtic influences
- **Sci-Fi Theme**: Synthesizers, electronic beats, ambient pads
- **Norse Theme**: Epic choir, percussion, horns (Vikings TV series inspiration)

### Implementation
- **Unity Audio Mixer**: Separate volume controls (Music, SFX, Ambient, UI, Voiceover)
- **Dynamic Intensity**: Battle music layers enabled/disabled based on HP, turn count
- **Looping**: All music loops seamlessly using loop points (audio-schema.json)

## 15.2 Sound Effects (SFX)

### Feedback-Driven Design (Inspired by Hearthstone)
Every player action has audio feedback:
- **Card Play**: Satisfying "snap" sound when placing cards
- **Combat Hit**: Impact sounds matched to damage (light tap for 5 damage, heavy thud for 50)
- **Building Placement**: Construction sound (hammer, stone-on-stone)
- **Resource Collection**: Coins jingling, gem chime, wood chopping
- **Level Up**: Triumphant "ding" with visual sparkle
- **Notification**: Gentle chime for alerts

### SFX Categories
- **UI Sounds**: Button clicks, menu transitions, card flips
- **Combat Sounds**: Sword clashes, magic spells, explosions, unit deaths
- **Environmental**: Ambient sounds (wind, water, birds) based on map biome
- **Social**: Chat message received, trade offer, alliance invitation

### Variation to Avoid Repetition
- **3-5 Variants**: Each SFX has 3-5 variations played randomly
- **Pitch Randomization**: ±10% pitch shift for organic feel
- **Spatial Audio**: Position SFX at source (card placement at tile position)

### Implementation
- **AudioSource Pooling**: Reuse 32 AudioSource components for performance
- **Priority System**: Important sounds (voiceover, victory) override background
- **Distance Attenuation**: Ambient sounds fade with camera distance

## 15.3 Voiceover & Localization

### Tutorial Voiceover
- **Narrator**: Professional voice actor guides new players
- **Localization**: 10+ languages (English, Spanish, French, German, Japanese, Chinese, Korean, Portuguese, Russian, Arabic)
- **Subtitles**: Always displayed, synchronized with audio
- **Skip Option**: Players can skip tutorial VO

### Character Voiceover (Future Expansion)
- **Hero Lines**: Unique voice lines for legendary heroes (e.g., Thor: "For Asgard!")
- **Victory/Defeat Quotes**: Short one-liners after battles
- **Cultural Authenticity**: Norse heroes speak with Scandinavian accents, etc.

### Localization Pipeline
- **Text Localization**: UI strings in `localization.json` files
- **Audio Localization**: Separate audio files per language (audio-schema.json)
- **Cultural Sensitivity**: Avoid idioms, slang, culturally-specific references

## 15.4 Accessibility Features (Inspired by The Last of Us Part II)

### Audio Accessibility
- **Subtitles**: All voiceover and important SFX have subtitles
- **Visual Cues**: On-screen icons when audio plays (e.g., sword icon for attack SFX)
- **Screen Reader Support**: Text-to-speech for blind players (iOS VoiceOver, Android TalkBack)
- **Haptic Feedback**: Controller/phone vibration for critical audio (battle hits, notifications)
- **Audio Descriptions**: Optional narration describing visual events

### Colorblind Support
- **High-Contrast Mode**: Adjustable UI contrast (150%, 200%)
- **Color Alternatives**: Elements use symbols + colors (e.g., Fire = red + flame icon)
- **Colorblind Filters**: Deuteranopia, Protanopia, Tritanopia filters

### Control Accessibility
- **One-Handed Mode**: UI elements movable to left/right side (mobile)
- **Button Size**: Adjustable touch targets (50%, 100%, 150%, 200%)
- **Simplified Controls**: Auto-battle for players with dexterity issues
- **Voice Commands**: "Attack", "Retreat", "End Turn" via speech recognition (future)

### Difficulty Modifiers
- **Reduced Animation Speed**: 0.5x speed for players with cognitive disabilities
- **Auto-Skip**: Automatically skip non-interactive scenes
- **Assist Mode**: Reduced enemy difficulty for casual players

## 15.5 Visual Polish

### Particle Effects (VFX)
- **Card Play**: Glow, sparkle, trail effects based on rarity
- **Combat**: Impact flashes, elemental effects (fire, water, lightning)
- **Level Up**: Fireworks, confetti, screen flash
- **Rare Drops**: Legendary beam of light from card packs

### Animations
- **Card Flip**: 3D flip animation when revealing cards
- **Unit Movement**: Smooth grid-to-grid transitions (0.3 seconds)
- **Building Construction**: Scaffold-to-complete animation (1 second)
- **Victory Pose**: Hero victory animation at battle end

### UI Polish
- **Smooth Transitions**: Fade in/out, slide animations (0.3-0.5 seconds)
- **Micro-Interactions**: Button press feedback (scale down 5%, bounce back)
- **Loading Screens**: Animated tips, lore snippets, rotating models
- **Tooltips**: Smooth appear/disappear with icons and formatted text

### Performance Optimization
- **Particle Pooling**: Reuse VFX instances
- **LOD System**: Reduce particle count on low-end devices
- **60 FPS Target**: Maintain smooth framerate on mid-tier devices (iPhone 12, Samsung S21)
- **Adaptive Quality**: Auto-adjust graphics based on device performance

## 15.6 Monetization via Premium Audio

### Premium Soundtracks (Pay-for-Look-and-Feel)
- **Alternate Themes**: Purchase orchestral, electronic, or jazz soundtracks
- **Exclusive Music**: VIP-only tracks, seasonal event music
- **Unlock Method**: Gems (500-1000), VIP Level 3+, achievement rewards
- **Audio Gallery**: Players can preview and purchase in-game

### Premium SFX Packs
- **Sci-Fi SFX**: Laser sounds, robotic voices for sci-fi theme
- **Fantasy SFX**: Magic spells, dragon roars for fantasy theme

## 15.7 Implementation Details

### Unity Audio System
- **Audio Mixer**: 5 groups (Master, Music, SFX, Ambient, UI, Voiceover)
- **Volume Controls**: Independent sliders for each group (saved in PlayerPrefs)
- **Ducking**: Lower music volume when voiceover plays (-10dB)
- **Reverb Zones**: Environmental reverb (cathedral = long reverb, forest = short)

### Asset Pipeline
- **Compression**: 
  - Music: OGG Vorbis, Quality 7 (streaming for files >1MB)
  - SFX: WAV uncompressed for <100KB, OGG for >100KB
  - Voiceover: OGG Vorbis, Quality 5
- **Addressables**: Dynamic loading/unloading for memory optimization
- **Memory Budget**: 50MB max loaded audio at any time

### Platform Considerations
- **iOS**: AAC format support, respect silent mode switch
- **Android**: OGG format, handle audio focus (pause when call received)
- **Web**: MP3 fallback for browsers without OGG support

## Open-Source References

- Freesound (GitHub integrations): Free audio assets (CC0, CC-BY licenses)
- Unity Audio Samples (GitHub): Adaptive music examples, audio mixer setups
- FMOD Integration (GitHub): Advanced audio middleware (future expansion)
- The Last of Us Part II (GDC talks): Accessibility best practices
- Unity Addressables (GitHub): Dynamic audio loading examples

# SECTION 16: EDGE CASES

Edge case handling is critical for player trust and retention. This section covers disconnect recovery, data corruption, exploits, platform-specific issues, economic anomalies, and social problems.

## 16.1 Disconnect & Network Issues

### Mid-Battle Disconnection
**Scenario**: Player loses internet connection during PvP battle

**Handling**:
1. **Grace Period**: 30 seconds to reconnect
2. **AI Takeover**: If not reconnected, AI plays remaining turns using player's tactics
3. **Reconnect Flow**: Player rejoins battle mid-turn if reconnected within 2 minutes
4. **Fair Loss**: If disconnect >2 minutes, count as loss (no Elo penalty if <3 disconnects/day)
5. **Penalties**: Repeated disconnects (>5/day) = temporary matchmaking ban (1 hour)

**Implementation**:
- Server saves battle state every turn
- WebSocket reconnection with state sync
- Client displays "Reconnecting..." overlay

### Server Downtime
**Scenario**: Server maintenance or unexpected outage

**Handling**:
1. **Scheduled Maintenance**: 24-hour notice, during low-traffic hours (2-4 AM local time)
2. **Compensation**: Free energy, card packs for downtime >1 hour
3. **Offline Mode**: Single-player campaign playable offline (sync progress on reconnect)
4. **Status Page**: Public status page (status.sovereignterritories.com) with uptime metrics

### Packet Loss & High Latency
**Scenario**: Player on poor connection (>500ms latency, 20% packet loss)

**Handling**:
1. **Latency Indicator**: UI shows connection quality (green/yellow/red)
2. **Turn Extension**: Auto-extend turn timer by latency amount (max +30 seconds)
3. **Client Prediction**: Local prediction with server reconciliation
4. **Graceful Degradation**: Disable animations, reduce update frequency

## 16.2 Data Corruption & Recovery

### Corrupted Save Data
**Scenario**: Player's account data becomes corrupted (rare bug, storage failure)

**Handling**:
1. **Daily Backups**: Server backs up all accounts daily (7-day retention)
2. **Auto-Recovery**: Server detects corruption, restores from most recent backup
3. **Manual Recovery**: Support team can restore from specific backup point
4. **Compensation**: Restore lost progress + bonus resources for inconvenience

### Schema Migration Failure
**Scenario**: New schema version breaks old data

**Handling**:
1. **Migration Scripts**: Automated scripts convert old schema to new (e.g., v1 → v2)
2. **Backward Compatibility**: Server supports N-1 schema versions
3. **Staging Tests**: Test migrations on staging environment before production
4. **Rollback Plan**: Instant rollback to previous server version if migrations fail
5. **Canary Deployment**: Deploy to 1% of players first, monitor for errors

### Duplicate Items (Dupe Bug)
**Scenario**: Bug allows players to duplicate cards or currency

**Handling**:
1. **Detection**: Server monitors for impossible inventory changes (e.g., +1000 gems without purchase)
2. **Anomaly Alerts**: Automated alerts for suspicious activity
3. **Rollback**: Remove duplicated items, restore to legitimate state
4. **Bans**: Intentional exploits = permanent ban; accidental = warning + rollback
5. **Hotfix**: Immediate server patch to close exploit

## 16.3 Exploit Prevention

### Timing Attacks
**Scenario**: Player manipulates local clock to cheat timers (energy recharge, event deadlines)

**Handling**:
1. **Server-Side Time**: All timers use server timestamp, not client
2. **Sync Validation**: Reject requests with suspicious timestamps (>1 hour drift)
3. **NTP Sync**: Client syncs with server time on every session start

### Replay Attacks
**Scenario**: Player captures network request and replays to duplicate actions

**Handling**:
1. **Request Nonces**: One-time unique IDs for each request
2. **Signature Validation**: HMAC signatures prevent request tampering
3. **Sequence Numbers**: Reject out-of-order or duplicate sequence numbers

### Client-Side Hacks
**Scenario**: Modified client sends invalid data (e.g., infinite HP, instant win)

**Handling**:
1. **Server Validation**: All actions validated server-side (never trust client)
2. **Sanity Checks**: Reject impossible values (e.g., damage >10,000)
3. **Behavioral Analysis**: Detect inhuman patterns (e.g., 100 actions in 1 second)
4. **Bans**: Hacked clients = instant permanent ban

### Auction Sniping
**Scenario**: Player uses bot to snipe auctions in final seconds

**Handling**:
1. **Anti-Snipe Extension**: Auction extends 60 seconds if bid placed in final 30 seconds
2. **Rate Limiting**: Max 10 bids/minute per player
3. **Captcha**: Require captcha for bids in final 60 seconds (prevents bots)

## 16.4 Platform-Specific Issues

### iOS App Store Rejection
**Scenario**: Apple rejects update for policy violation

**Handling**:
1. **Pre-Submission Review**: Internal checklist for App Store guidelines
2. **Appeals Process**: Detailed explanation to Apple if rejected
3. **Hot Fix**: Server-side updates for non-client changes (no resubmission needed)
4. **Age Rating**: Ensure content matches E10+ rating

### Android Fragmentation
**Scenario**: Game crashes on specific Android devices (e.g., Samsung Galaxy S7)

**Handling**:
1. **Device Testing**: Test on 20+ devices (high, mid, low-end)
2. **Crash Reporting**: Unity Cloud Diagnostics tracks device-specific crashes
3. **Conditional Features**: Disable heavy VFX on low-end devices
4. **Min SDK**: Android 7.0+ (API 24) to avoid legacy issues

### Web Browser Compatibility
**Scenario**: Game doesn't load on Safari or Firefox

**Handling**:
1. **Browser Testing**: QA tests on Chrome, Safari, Firefox, Edge
2. **Fallbacks**: MP3 audio fallback (Safari doesn't support OGG)
3. **WebGL 2.0**: Minimum requirement, show error for unsupported browsers

## 16.5 Economic Edge Cases

### Negative Balance
**Scenario**: Bug causes player to have -500 gold

**Handling**:
1. **Prevention**: Server validates all transactions (debit before credit)
2. **Correction**: If detected, set balance to 0 + compensate 500 gold
3. **Root Cause**: Investigate and fix bug that caused negative balance

### Overflow Errors
**Scenario**: Player accumulates 2 billion gold (integer overflow)

**Handling**:
1. **Use Long/BigInt**: Store currency as 64-bit integers (max 9 quintillion)
2. **Caps**: Soft cap at 1 billion gold with warning (invest in buildings, cards)
3. **Overflow Protection**: Server rejects transactions that would overflow

### Inflation Spiral
**Scenario**: AFK economy produces too much gold, devalues currency

**Handling**:
1. **Weekly Monitoring**: Track total gold in economy, velocity, top 1% holdings
2. **Sinks**: Increase costs (auctions, upgrades) if inflation detected
3. **Decay**: Storage decay for excess resources (see resource-schema.json)
4. **Seasonal Resets**: Partial economy reset every 3 months (leaderboards, not inventories)

### Market Manipulation
**Scenario**: Whales buy all legendaries on auction house, resell at 10x price

**Handling**:
1. **Price Limits**: Max listing price = 5x market average
2. **Volume Limits**: Max 10 legendaries per player on auction
3. **Cooldowns**: 24-hour cooldown between buying and reselling same card
4. **Monitoring**: Alert if single player controls >20% of legendary market

## 16.6 Social & Community Issues

### Harassment & Toxicity
**Scenario**: Player harasses others in chat, uses slurs

**Handling**:
1. **Profanity Filter**: Auto-filter offensive words (customizable per region)
2. **Report System**: Right-click player → Report → Select reason
3. **Human Review**: Support team reviews reports within 24 hours
4. **Escalation**: Warning → 24h mute → 7-day ban → permanent ban
5. **Appeals**: Players can appeal via support ticket

### Alliance Griefing
**Scenario**: Player joins alliance, steals treasury, leaves

**Handling**:
1. **Role Permissions**: Only leaders/officers can withdraw from treasury
2. **Withdrawal Limits**: Max 10% of treasury per withdrawal, 24-hour cooldown
3. **Audit Logs**: Track all treasury transactions with timestamps
4. **Multi-Sig**: Require 2+ officers to approve large withdrawals (>10,000 gold)

### Impersonation
**Scenario**: Player creates account with name similar to famous streamer (e.g., "Ninja_Official")

**Handling**:
1. **Verification Badges**: Verified checkmark for official streamers, devs
2. **Name Blacklist**: Reserve famous names, trademarks
3. **Reports**: Players can report impersonation
4. **Forced Rename**: Change impersonator's name + warning

### GDPR Deletion Requests
**Scenario**: Player requests account deletion under GDPR

**Handling**:
1. **Deletion Flow**: Settings → Privacy → Delete Account → Confirm via email
2. **Grace Period**: 7-day grace period to cancel deletion
3. **Data Removal**: Delete all PII within 30 days
4. **Anonymization**: Convert account to "[Deleted User]" for leaderboard history
5. **No Recovery**: Permanent deletion, no account recovery

## 16.7 Payment & Refund Issues

### Failed Payment
**Scenario**: Player's credit card is declined during IAP

**Handling**:
1. **Retry Prompt**: "Payment failed. Try again?"
2. **Alternative Methods**: Offer PayPal, Google Pay, Apple Pay
3. **Support Contact**: Link to support if repeated failures

### Refund Abuse
**Scenario**: Player makes purchase, requests refund, keeps items

**Handling**:
1. **Revocation**: Remove items if refund granted
2. **Platform Refunds**: Apple/Google handle refunds, notify server
3. **Abuse Detection**: Flag accounts with >3 refunds, investigate
4. **Bans**: Repeated refund abuse = ban from IAP

### Double Charge
**Scenario**: Player charged twice for single purchase

**Handling**:
1. **Idempotency**: Server uses transaction IDs to prevent double fulfillment
2. **Refund**: Immediately refund duplicate charge via platform
3. **Compensation**: Extra gems for inconvenience

## 16.8 Testing & QA for Edge Cases

### Chaos Engineering
- **Network Simulation**: Test with packet loss, latency, disconnects
- **Server Failures**: Randomly kill server instances, ensure recovery
- **Load Spikes**: Simulate 10,000 concurrent players, test scaling

### Penetration Testing
- **Security Audits**: Annual third-party security audits
- **Bug Bounty**: Reward players for finding exploits (responsible disclosure)
- **Ethical Hacking**: Internal red team tests for vulnerabilities

### Regression Testing
- **Automated Tests**: 1000+ test cases run on every commit
- **Canary Deployments**: Test on 1% of players before full rollout
- **Rollback Drills**: Practice instant rollback (target <5 minutes)

## Open-Source References

- Nakama Error Handling (GitHub): Disconnect recovery, graceful degradation examples
- Open-Source Chat Moderation (GitHub, e.g., Perspective API): Toxicity detection
- Unity Save Systems (GitHub): Auto-save, cloud sync patterns
- Chaos Engineering Tools (GitHub, e.g., Chaos Monkey): Failure injection testing
- OWASP Security Guidelines: Web/mobile security best practices

# Immediate Next Steps (Technical)

Deploy server, build card manager, etc.

