Here is the Final Consolidated Master Design Document (Version 4.4).

This version integrates everything we have discussed: the Maps, Stacking, Campaigns, Cards, Auction House, Chat, and the Expansion Roadmap. It now includes enhanced sections on Combat Mechanics, Progression & Balance, Monetization (pay-for-speed/look-and-feel model), Multiplayer, UI/UX, Technical Integration, and more. Clarifications: 2.5D/2D perspective (no 3D modeling); turn-based with AI auto-battle for AFK defending/joining events; focus on card collecting, deck-building, and positioning decks/cards as game-pieces (heroes/avatars on maps/castles); board game look/feel with decks as cards and game-piece combinations; deterministic combat based on math (power, elements, classes, buffs)—no random dice except possibly in arena battles. Decisions are logic-based. Added common features for stickiness/retention: shields, enhanced alliances/friends, improved auction house, comprehensive currencies/VIP, daily/weekly events, achievements/leaderboards, notifications, seasonal content, and tutorials. Expanded card system with rarities, boosting/specialization, visual effects, pre-built decks, and RPG-like hero customization. Open-source references added for prototyping. You can copy and paste this entire block into your Google Doc as the single source of truth.

# PROJECT: SOVEREIGN TERRITORIES

## Master Game Design Document (The Complete Codex)

Version: 4.4

Owner: [User] ("The Architect")

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

## 2. Rarities and Customization

- **Basic/Common**: Generalized cards (e.g., basic archer, wall). No specialization; used for fodder or basic builds.
- **Rare**: More creative generalized cards (e.g., elite scout, enchanted tower). Some minor customization options.
- **Epic**: Specific named cards (e.g., "Stormbringer the Mage"). Boostable with scrolls/books from PvE, draws, events. Limited points for specialization (skill tree-like: allocate to stats/abilities, e.g., +fire damage or +healing). Visual effects on map figures (e.g., boosted fire stat glows red border).
- **Legendary**: Specific named cards (e.g., "Thor the Thunderer"). Highly boostable; equip weapons/armor for RPG-like customization (e.g., find/equip swords in events). Skill trees for unique abilities. Visual effects (e.g., halos for healing boosts). Not all stats max out; limits encourage strategy.
- **Pre-Built Decks**: Buy themed decks (e.g., fire elemental, with hero, units, tactics, buildings). Customize by swapping cards. Saved decks in storage; loose cards in codex.

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

