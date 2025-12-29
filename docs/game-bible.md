Here is the Final Consolidated Master Design Document (Version 5.0).

This version incorporates Territory/Tile Codex Views, visual figurine/statue representations of deployed cards, deployment limits per territory, and visual upgrades from towns to castles. Everything is card-centric, with figurine visuals based on card stacks and territory levels.

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

Combat in Sovereign Territories is the heart of the game, blending strategic depth with accessibility. All battles are turn-based on an 8x8 grid, ensuring deterministic outcomes based on math rather than luck. This allows players to master tactics while enabling auto-battle for AFK play, making it suitable for both casual and competitive gamers.

## 8.1 System Overview

The combat system emphasizes planning and execution, where every action counts. Players position their deck-formed units on the grid, then engage in alternating turns. Units are derived from stacked cards, combining stats for powerful formations.

### Turn Structure
- **Initiative**: Determined by unit speed stats; faster units act first.
- **Actions**: Move (limited range), attack (melee/ranged), or activate tactics/buffs.
- **Phases**: Movement phase followed by action phase, preventing simultaneous moves.

### Resolution
Combat resolution is purely mathematical, ensuring fairness. Damage calculations incorporate elements (e.g., fire beats water), class bonuses (e.g., archers vs. infantry), terrain modifiers (e.g., hills boost defense), and buffs from equipment or tactics. Area of Effect (AoE) attacks, like fireballs, multiply damage against stacked units, adding risk-reward to formations.

### AI Integration
Programmable tactics allow players to set AI behaviors, such as "focus healers" or "flank left," enabling auto-battle during AFK scenarios. This keeps the game engaging even when offline, with tactics evolving as players unlock more options.

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

## 9.6 Achievements and Leaderboards

Achievements reward milestones with badges and unlocks. Leaderboards track conquests, deck power, and donations, fostering competition.

## Player Tips
- Focus on castle leveling for endgame power.
- Balance PvE/PvP to maintain progression.

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

## 11.4 Codex and Card Views

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

#   S E C T I O N   1 7 :   A D D I T I O N A L   F E A T U R E S   F O R   C O M P L E T E   G A M E R   E X P E R I E N C E 
 
 T o   f i l l   g a p s   a n d   e n s u r e   a   t y p i c a l   g a m e r   e x p e r i e n c e ,   w e ' v e   a d d e d   t h e s e   e l e m e n t s . 
 
 # #   1 7 . 1   O n b o a r d i n g   a n d   T u t o r i a l s 
 
 -   * * D e t a i l e d   F l o w * * :   S t a r t   w i t h   c a r d   b a s i c s ,   t h e n   d e c k - b u i l d i n g ,   m a p   p l a c e m e n t ,   a n d   c o m b a t .   I n t e r a c t i v e   q u e s t s   g u i d e   f i r s t   h o u r s . 
 -   * * A c c e s s i b i l i t y * * :   V o i c e - o v e r   f o r   t u t o r i a l s ;   a d j u s t a b l e   t e x t   s i z e s . 
 
 # #   1 7 . 2   A c c e s s i b i l i t y   O p t i o n s 
 
 -   * * F e a t u r e s * * :   C o l o r b l i n d   m o d e s ,   h i g h - c o n t r a s t   U I ,   o n e - h a n d e d   p l a y ,   s u b t i t l e s   f o r   a u d i o . 
 -   * * I n s p i r a t i o n * * :   E n s u r e s   i n c l u s i v i t y ,   l i k e   i n   m o d e r n   m o b i l e   g a m e s . 
 
 # #   1 7 . 3   E n d g a m e   a n d   L o n g - T e r m   G o a l s 
 
 -   * * C o n t e n t * * :   H i g h - l e v e l   a l l i a n c e s ,   m e t a - m a s t e r y ,   c o s m e t i c   c o l l e c t i o n s . 
 -   * * R e t e n t i o n * * :   S e a s o n a l   e v e n t s ,   l e a d e r b o a r d s   r e s e t   m o n t h l y . 
 
 # #   1 7 . 4   C r o s s - P l a t f o r m   P l a y 
 
 -   * * S y n c * * :   A c c o u n t s   a c r o s s   m o b i l e / P C ;   c l o u d   s a v e s . 
 
 # #   1 7 . 5   C o m m u n i t y   a n d   E x t e r n a l   F e a t u r e s 
 
 -   * * F o r u m s / D i s c o r d * * :   O f f i c i a l   c h a n n e l s   f o r   d i s c u s s i o n s . 
 -   * * E s p o r t s   P o t e n t i a l * * :   T o u r n a m e n t s   f o r   c o m p e t i t i v e   p l a y e r s . 
 
 # #   1 7 . 6   M o n e t i z a t i o n   B a l a n c e   C h e c k s 
 
 -   * * N o   G a p s * * :   E n s u r e   f r e e   p r o g r e s s i o n ;   o p t i o n a l   I A P s . 
 
 T h i s   f i l l s   a n y   g a m e p l a y   h o l e s ,   a l i g n i n g   w i t h   e x p e c t a t i o n s . 
 
 