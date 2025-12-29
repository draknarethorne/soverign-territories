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

### Equipment

Equipment cards attach to heroes for stat boosts and visuals. Acquired from events or packs.

- **Examples**: "Excalibur Sword" (+attack), "Dragon Scale Armor" (+defense).
- **How They Work**: Socket-compatible; visual effects appear on the hero's game piece (e.g., glowing sword).

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

## 10.2 Anti-Cheat Measures

Server-side validation prevents exploits. Reports and mutes handle griefing, with bans for severe cases.

## 10.3 Diplomacy Features

Voting systems for war declarations, with chat for negotiations.

## Player Tips
- Join alliances for better matchmaking and events.

## Open-Source References

- Nakama Matchmaking (GitHub): Elo and lobbies.
- Photon Examples (GitHub): Anti-cheat and multiplayer.
- FreeCiv (GitHub): Diplomacy voting.

# SECTION 11: USER INTERFACE & EXPERIENCE

The UI is touch-optimized for mobile, with intuitive navigation. Tutorials guide new players, while notifications keep veterans engaged.

## 11.1 Design Principles

Swipe gestures for zooming, drag-and-drop for placement. HUD displays unit health and buffs clearly.

## 11.2 Tutorials and Onboarding

Progressive overlays teach mechanics, from deck-building to combat. Skip options for experienced players.

## 11.3 Notifications and Alerts

Opt-in push notifications for energy refills, attacks, or events.

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

