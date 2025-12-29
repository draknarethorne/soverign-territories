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

The game adopts a **2.5D isometric view** for maps and castles, combined with **2D top-down grids** for tactical battles, evoking the feel of classic board games like Catan or tabletop RPGs. No full 3D modeling is used to maintain a stylized, accessible look suitable for mobile and PC platforms.

### Isometric Map View (2.5D)
- **Camera Angle**: 45-degree isometric projection for strategic overview
- **Zoom Levels**: 3 levels (World view, State view, Local view) with smooth transitions
- **Pan & Rotate**: Two-finger pan on mobile, mouse drag on PC; 90-degree rotation snapping
- **Visual Depth**: Layered sprites create depth without 3D rendering
- **Tile Rendering**: Hand-painted terrain tiles (grass, water, mountains, forests) with seasonal variants
- **Building Visuals**: 2.5D sprites for castles, towers, walls with upgrade animations (town → castle)
- **Unit Figurines**: Stylized chess-piece aesthetic for deployed units (see Section 11.5)

### Tactical Battle Grid (2D Top-Down)
- **Grid Layout**: 8x8 square grid with clear tile boundaries
- **Unit Sprites**: 2D character art with directional facing (4 directions)
- **Movement Arrows**: Visual path indicators for movement previews
- **Attack Ranges**: Highlighted tiles showing attack zones (melee = adjacent, ranged = 3-5 tiles)
- **Status Indicators**: HP bars, buff icons, turn order displayed above units
- **Environmental Effects**: Animated terrain features (burning tiles, water ripples, fog of war)

### Art Style Principles
- **Stylized Realism**: Painterly art style inspired by Civilization VI and Fire Emblem
- **Vibrant Color Palette**: High saturation for mobile visibility, distinct color coding per theme
- **Consistent Proportions**: Units scaled 1:1.5 height-to-width for readability
- **Modular Assets**: Reusable components (armor pieces, weapons) for efficient art production
- **Theme Flexibility**: Base art templates support skin swaps (medieval, sci-fi, norse)

### Performance Optimization
- **Sprite Atlases**: All sprites batched into atlases for reduced draw calls (<50 per frame)
- **Asset Streaming**: Addressables load/unload assets dynamically based on visible area
- **Level of Detail (LOD)**: Simplified sprites at high zoom levels
- **Particle Budget**: Max 100 active particles on mobile, 300 on PC
- **Target Performance**: 60 FPS on iPhone 12 / Samsung S21, 30 FPS on iPhone 8

## Gameplay Loop

Sovereign Territories is designed around a **5-minute core loop** for engagement, with deeper **30-minute sessions** for strategic play and **AFK progression** for retention.

### Core 5-Minute Loop (Mobile-Friendly)
1. **Login & Collect**: Daily rewards, energy refill notifications, AFK resource collection
2. **Quick Battle**: 1-2 PvE saga battles or expedition rolls (3-5 minutes)
3. **Card Management**: Open 1 pack, combine/upgrade 2-3 cards in Codex
4. **Social Check**: Alliance chat, accept gifts, send resources
5. **Logout**: Set auto-battle for next AFK period

### Extended 30-Minute Session (Deep Engagement)
1. **Collect Cards**: 
   - **Packs**: Open 3-5 packs from daily gems, quest rewards, or purchases
   - **Quests**: Complete 2-3 daily quests ("Win 3 battles", "Place 5 buildings")
   - **AFK Rewards**: Claim resources from placed buildings (check every 4-8 hours)
   - **Trades**: Browse auction house for rare cards, sell duplicates
   - **Events**: Participate in weekly expeditions (10-15 minutes)

2. **Build Decks**: 
   - **Battle Decks**: Assemble 20-30 card decks with heroes, units, tactics, equipment
   - **Building Decks**: Create 15-20 card decks for economic structures
   - **Synergy Planning**: Build theme-based decks (e.g., 20 Norse cards for frost immunity)
   - **Codex Management**: Combine cards for stars, attach boosters, split stacks
   - **Deck Slots**: Unlock via castle leveling (start with 3, max 10 at Level 30)

3. **Deploy on Maps**: 
   - **Battle Deployments**: Position hero stacks on State/County maps for territorial control
   - **Building Placement**: Place farms, mines, turrets on optimal terrain tiles
   - **Territory Management**: Monitor multiple castles/forts, upgrade to increase slots
   - **Resource Optimization**: Balance production (food, lumber, ore) with storage limits
   - **Tile Codex Views**: Use territory views to strategize card placements

4. **Engage in Combat**: 
   - **PvE Saga**: Progress through story campaign (5-10 battles per session)
   - **PvP Matches**: Ranked battles for Elo rating (3-5 matches per session)
   - **Alliance Events**: Contribute decks to large-scale wars (check every 2-4 hours)
   - **Auto-Battle**: Set tactics for AFK battles, check results periodically
   - **Boss Fights**: Tackle weekly boss challenges with guild coordination

5. **Progress and Expand**: 
   - **Castle Leveling**: Earn XP to unlock deck slots, building limits, PvP eligibility (Level 10)
   - **Hero Skill Trees**: Allocate points to customize legendary heroes
   - **Territory Expansion**: Conquer new regions on PvE maps for resources
   - **Alliance Participation**: Join after Level 5, contribute to treasury, vote on diplomacy
   - **Seasonal Progression**: Climb leaderboards, unlock battle pass tiers

### AFK Progression Loop (Retention)
- **Building Production**: Placed buildings generate resources passively (check every 4-8 hours)
- **Auto-Battle Earnings**: Set tactics, let AI fight battles while offline (capped at 8 hours)
- **Energy Recharge**: Full energy refill every 12 hours (login prompt)
- **Daily Reset**: New quests, shop refresh, event updates at midnight (local time)
- **Weekly Events**: Expedition boards, tournaments, alliance wars (check 2-3 times per week)

### Session Flow Example (Typical Player)
- **Morning (5 min)**: Login → Collect AFK rewards → Spend energy on 2 saga battles → Check alliance chat → Logout
- **Lunch (10 min)**: Open daily pack → Upgrade 3 cards → Place 2 new buildings → Start auto-battles → Logout
- **Evening (30 min)**: PvP matches → Expedition roll → Auction house trading → Guild event contribution → Castle upgrades → Logout
- **Before Bed (3 min)**: Claim battle results → Set overnight auto-battles → Daily quest check → Logout

### Retention Hooks
- **Energy System**: 1 energy per 30 minutes, 100 max cap (encourages 2-3 logins per day)
- **Login Streaks**: Day 7 reward = guaranteed legendary (don't break streak)
- **Limited Events**: Weekly expeditions, seasonal tournaments (FOMO)
- **Alliance Dependencies**: Guild buffs, treasury contributions (social obligation)
- **AFK Optimization**: Players return to optimize building placements, check production

## Key Mechanics

Sovereign Territories combines multiple proven gameplay systems into a cohesive whole. Each mechanic reinforces the others, creating depth without overwhelming complexity.

### Turn-Based Strategy with Auto-Battle
**Core Philosophy**: Respect player time while maintaining strategic depth
- **Manual Play**: Full tactical control for competitive PvP and boss battles (8x8 grid, move-attack-ability per turn)
- **Auto-Battle**: AI executes pre-programmed tactics for grinding, AFK play, and repeated content
- **Hybrid Mode**: Switch between manual/auto mid-battle (1-time toggle per battle)
- **Speed Options**: 1x, 2x, 4x, Instant (skip animations entirely for VIP 4+)
- **Strategic Programming**: Players "teach" AI via tactic cards ("Focus Healers", "Defend Objective", "Aggressive Push")
- **AFK Benefits**: Queue up to 10 battles while offline (VIP 5), collect results on next login

**Why It Works**: 
- Casual players use auto-battle for accessibility
- Hardcore players manual-play for competitive edge
- No time wasted on repetitive content (PvE farming)
- Tactics system adds deck-building layer ("How will AI use my deck?")

### Deterministic Combat (No RNG)
**Core Philosophy**: Skill-based outcomes, no gambling
- **Math-Based Resolution**: Damage = `(Attack × Multipliers) - (Defense × Terrain)`, always same result
- **Elemental Triangle**: Fire > Water > Earth > Fire (1.5x damage advantage, 0.75x disadvantage)
- **Class Bonuses**: Archers +25% vs infantry, Cavalry +25% vs archers, Infantry +25% vs cavalry
- **Terrain Modifiers**: Hills +20% defense, forests +20% cover, water -50% movement
- **Buff Stacking**: Transparent calculations (hover for tooltip: "35% attack = +20% hero + 15% tactic")
- **No Crits/Dodges** (except): Optional "Arena Mode" with 10% crit chance for variety

**Why It Works**:
- Players can plan 3-5 turns ahead with certainty
- Losses feel fair ("I made a tactical error" vs "bad RNG")
- Replays are 100% reproducible (VOD-friendly for streamers)
- Balancing is easier (no RNG swings hide balance issues)

### Cards as Game Pieces (Physical Representation)
**Core Philosophy**: Merge card game collection with board game positioning
- **Deck = Army**: Your 20-30 card deck deploys as 8 units on battlefield
- **Hero Stacks**: Attach 5-10 unit cards to 1 hero = combined stats (e.g., 5 archers = 500 HP, 250 attack)
- **Map Positioning**: Heroes placed on State/County/Global maps as figurines
- **Visual Feedback**: Figurines evolve based on card composition (cavalry stack = mounted statue)
- **Territory Control**: Each controlled territory displays your card stacks as visual ownership markers

**Why It Works**:
- Card collecting feels tangible ("I see my collection on the map")
- Positioning matters (flanking, chokepoints, terrain advantages)
- Social status ("Look at my Tier 3 castle with legendary hero figurine")
- No disconnect between collection and gameplay (unlike pure CCGs where decks are abstract)

### Building Placement and AFK Economy
**Core Philosophy**: Passive progression for retention, strategic placement for depth
- **Building Cards**: Separate deck from battle cards (15-25 buildings: farms, mines, turrets, walls)
- **Map Placement**: Drop buildings on optimal terrain (farms on fertile land = +50% production)
- **AFK Generation**: Buildings produce resources 24/7 (capped at 8 hours, requires login to collect)
- **Synergy Bonuses**: Adjacent buildings boost each other (farm + mill = +25% food)
- **Defense**: Placed buildings defend territories in PvP (turrets auto-attack invaders)
- **Resource Types**: 5 resources (food, water, lumber, ore, gold) with different sources/sinks

**Production Rates** (examples):
- Level 1 Farm (fertile tile): 5 food/hour (40 food per 8-hour session)
- Level 3 Mine (mountain): 12 ore/hour (96 ore per session)
- Level 5 Bank (trade route): 25 gold/hour (200 gold per session)

**Why It Works**:
- Rewards 2-3 daily logins (collect every 8 hours)
- Strategic depth (where to place buildings, which to upgrade first)
- Economic alternative to grinding battles (AFK players can still progress)
- Retention hook ("I need to check my production in 4 hours")

### PvE to PvP Progression (Safe Learning Curve)
**Core Philosophy**: Master mechanics in PvE before facing human opponents
- **Levels 1-9**: PvE only (Saga campaign, Territorial Conquest vs AI, Expeditions)
- **Level 10 Unlock**: Ranked PvP, alliance wars, competitive tournaments
- **Alliance Join**: Level 5+ (contribute to treasury, chat, but no wars until Level 10)
- **Gradual Complexity**: 
  - Levels 1-5: Learn cards, battles, deck-building
  - Levels 5-10: Economy, alliances, territory management
  - Level 10+: PvP, meta strategies, endgame content

**Why It Works**:
- New players aren't stomped by veterans immediately
- 20-30 hours of PvE content before PvP (master fundamentals)
- Optional PvE-only playstyle (some players never touch PvP)
- Alliance membership before wars (social bonding without competitive pressure)

### AFK Features (Accessibility for Busy Lives)
**Core Philosophy**: Progress without grinding
- **Auto-Battle Queue**: Set tactics, queue 10 battles, collect results next login
- **AFK Production**: Buildings generate resources offline (8-hour cap)
- **Energy Overflow**: Unused energy accumulates (max 100-200 depending on VIP)
- **Simplified Modes**: Expedition = board game with 1 click per turn, minimal engagement
- **Battle Pass**: Progression via time, not just active play (dailies auto-complete for VIP 5)

**Why It Works**:
- Respects player time (no 6-hour grinding sessions required)
- Retention via convenience ("I can progress while at work")
- Appeals to older demographics (30-50 year olds with jobs/families)
- Monetization via speed-ups (whales pay to progress faster, not stronger)

## Monetization

Sovereign Territories follows a **"pay-for-speed" and "pay-for-look-and-feel"** model, ensuring **zero pay-to-win**. Paying players progress faster and look cooler, but never gain gameplay advantages over free players.

### Pay-for-Speed (Convenience)
**Philosophy**: Time is money, but skill determines victory

**What Players Can Buy**:
1. **Energy Refills**: 50 energy for 100 gems (normally recharges 1 per 30 min)
   - Max 5 refills per day (prevent no-lifing)
   - VIP players get faster natural recharge (1 per 10 min at VIP 5)

2. **Battle Speed-Ups**: 
   - 2x speed: Free for all players
   - 4x speed: VIP 2+ only
   - Instant skip: VIP 4+ only (no animations, instant results)

3. **Extra Deck Slots**: 
   - $2.99 for +1 deck slot (max 12 total, vs 10 for free players)
   - Quality-of-life for theorycrafters, not competitive advantage

4. **Premium Card Packs**: 
   - $4.99 for 10-card pack (2 rares, 1 epic guaranteed)
   - Free players get same cards via quests, auction house, AFK rewards
   - No exclusive cards (all cards obtainable for free)

5. **Battle Pass** ($9.99 per season):
   - 2x rewards per tier vs free track
   - Exclusive cosmetics (skins, emotes, borders)
   - Pays for itself at Tier 20 (gem value)

**What Is NOT For Sale**:
- ❌ Stat boosts (no +10% damage for $$$)
- ❌ Exclusive OP cards (no "pay $50 for legendary that dominates meta")
- ❌ Extra deck size in battles (everyone gets 20-30 cards, period)
- ❌ Better RNG (no "pay for higher legendary drop rates" beyond pity system)

### Pay-for-Look-and-Feel (Cosmetics)
**Philosophy**: Flex your style, not your wallet

**Cosmetic Options**:
1. **Card Skins**: 
   - Alternate art for existing cards (same stats, different visuals)
   - Example: Thor (classic art) vs Thor (animated lightning premium skin)
   - $2.99 per skin OR 500 gems

2. **Battle VFX**:
   - Premium visual effects (golden card glow, rainbow explosions)
   - Animated emotes (fireworks, confetti on victory)
   - $4.99 for VFX pack OR VIP 5 exclusive

3. **Soundtracks**:
   - Alternate music themes (orchestral, electronic, jazz)
   - $1.99 per soundtrack OR unlock via achievements

4. **Avatar Customization**:
   - Borders/frames (bronze, silver, gold, diamond, animated)
   - Titles ("Master Tactician", "Undefeated", "Whale Lord")
   - Profile banners (seasonal, event-exclusive)
   - Mix of free (achievements) and paid ($0.99-2.99)

5. **Building Skins**:
   - Castles with different architectural styles (Japanese pagoda, futuristic skyscraper)
   - $4.99 per castle skin OR 1,000 gems

### Pricing Strategy
**Target Audiences**:
- **Free Players (70%)**: Fully viable, can reach top 10% with skill and time
- **Minnows (20%)**: $5-20/month on VIP 1-2, battle pass, occasional pack
- **Dolphins (8%)**: $20-100/month on VIP 3-4, cosmetics, energy refills
- **Whales (2%)**: $100-500+/month on VIP 5, all cosmetics, max convenience

**Revenue Projections** (for 10,000 DAU):
- Free players: $0 (but drive retention, content for whales)
- Minnows: $10/month average × 2,000 = $20,000/month
- Dolphins: $50/month average × 800 = $40,000/month
- Whales: $200/month average × 200 = $40,000/month
- **Total**: ~$100,000/month = $1.2M annual revenue

**Fair Monetization Metrics**:
- **Conversion Rate**: 5-10% (industry standard: 2-5%, we aim higher via battle pass value)
- **ARPU** (Average Revenue Per User): $10/month
- **ARPPU** (Average Revenue Per Paying User): $20-30/month (VIP 2-3 sweet spot)
- **Whale Contribution**: 40-60% of revenue (standard for F2P)

### Anti-Whale Protections
**Prevent Pay-to-Win Creep**:
1. **Spending Caps**: 
   - Max 5 energy refills per day ($5 ceiling)
   - No "unlimited gem bundles" (prevents runaway spending)
   - VIP 5 cap at $100 lifetime (can't buy VIP 6 for $1000)

2. **Ranked Matchmaking**: 
   - Elo-based, not spend-based (whales fight whales at high Elo)
   - Free players at 2500 Elo beat whales at 2000 Elo

3. **Skill Ceiling**: 
   - Deck-building knowledge > card quantity
   - Meta decks use 80% common/rare cards (accessible to all)
   - Legendary cards are situational, not auto-win

4. **Community Backlash Prevention**:
   - Transparent monetization (no hidden costs)
   - Listen to feedback (monthly surveys on monetization fairness)
   - Nerf OP paid cards within 48 hours if community complains

### Ethical Considerations
**Responsible Monetization**:
- **No Loot Box Gambling** (cards are collectibles, not slots):
  - Packs show exact odds (5% legendary)
  - Pity system guarantees legendary within 30 packs (transparent)
  - No "one more pack" addiction mechanics

- **Spending Warnings**:
  - "You've spent $50 this month. Continue?" popup at $25, $50, $100 thresholds
  - Spending limits (parents can set $20/month cap for kids)
  - Cooldown periods (24-hour wait for purchases >$50)

- **COPPA Compliance** (kids under 13):
  - No IAP for <13 without parental verification
  - Simplified monetization (gems hidden for minors)

- **GDPR Privacy**:
  - No selling player data to third parties (ever)
  - Transparent tracking ("We use data for balancing, not ads")

## Retention and Stickiness

Sovereign Territories uses proven retention mechanics from top F2P games, balanced to respect player time while encouraging regular engagement.

### Daily Login Incentives
**7-Day Streak Rewards**:
- Day 1: 50 gold + 10 energy
- Day 2: 100 gold + 1 common pack
- Day 3: 150 gold + 20 energy
- Day 4: 200 gold + 1 rare pack
- Day 5: 250 gold + 30 energy
- Day 6: 300 gold + 1 epic pack
- **Day 7: 500 gold + 50 gems + 1 LEGENDARY CARD** (big payoff)

**Psychology**:
- Escalating rewards create anticipation ("Just 2 more days to legendary!")
- Sunk cost fallacy ("I've logged in 6 days, can't break streak now")
- VIP 3+ gets streak protection (1 forgiveness per month = no reset if 1 day missed)

### Energy System (Session Pacing)
**How It Works**:
- **Energy Cap**: 100 for free players, 200 for VIP 5
- **Recharge Rate**: 1 energy per 30 minutes (free), 1 per 10 minutes (VIP 5)
- **Energy Costs**: 
  - PvE battle: 5 energy
  - PvP match: 10 energy
  - Expedition roll: 3 energy
  - Boss battle: 20 energy

**Optimal Login Pattern**:
- **Morning** (8 AM): 100 energy cap reached → spend 50 on 10 battles → start recharge
- **Lunch** (12 PM): 60 energy accumulated → spend 30 on 6 battles → start recharge
- **Evening** (6 PM): 90 energy accumulated → spend 50 on PvP + quests → start recharge
- **Before Bed** (10 PM): 60 energy → spend on AFK queue → overnight recharge

**Why It Works**:
- Encourages 2-4 logins per day (industry sweet spot)
- Prevents burnout (can't grind 12 hours straight)
- Creates urgency ("Energy is wasting if I don't log in")
- Monetization: Whales buy refills ($1 per 50 energy, 5x per day max)

### Limited-Time Events (FOMO)
**Weekly Rotation**:
- **Week 1**: Expedition Event (exclusive cards)
- **Week 2**: Double XP Weekend
- **Week 3**: Alliance Tournament (guild competition)
- **Week 4**: Seasonal Boss Battle (limited-time legendary reward)

**Seasonal Content** (3-month cycles):
- **Season 1: Norse Invasion**: Exclusive Thor skin, Valhalla map, frost-themed cards
- **Season 2: Cyber Uprising**: Sci-fi units, neon city map, hacking mechanics
- **Season 3: Medieval Renaissance**: Knights, castles, jousting tournaments

**Why It Works**:
- FOMO (Fear of Missing Out): "I need to play this week or miss exclusive content"
- Variety: Prevents staleness (new content every week)
- Social pressure: Friends talking about events you missed

### Alliance Dependencies (Social Obligation)
**Guild Retention Mechanics**:
1. **Daily Contributions**:
   - Donate 100 gold to alliance treasury daily (earn alliance XP)
   - Leaderboard for top contributors (recognition + rewards)
   - Guild buffs require maintenance (members must contribute to keep +10% gold active)

2. **Alliance Events**:
   - Alliance wars every 2 weeks (guilds rely on active members)
   - Shared rewards (entire guild gets legendary pack if top 10 alliance)
   - Inactive members kicked (social pressure to stay active)

3. **Social Bonding**:
   - Alliance chat creates friendships
   - Co-op battles (2v2, 3v3 with guildmates)
   - Guild bragging rights ("Our alliance holds 3 wonders!")

**Why It Works**:
- **80% of retention** comes from social features in successful F2P games
- Leaving alliance = losing friends, buffs, shared resources
- Peer pressure: "Don't let the team down" obligation

### AFK Optimization (Passive Engagement)
**Resource Production**:
- Buildings generate resources every hour (max 8-hour accumulation)
- Notifications: "Your farm is full! Collect 200 food" (push notification after 4 hours)
- Optimization puzzle: "Which buildings should I upgrade for max AFK income?"

**Auto-Battle Results**:
- Queue 10 battles before bed, collect results in morning
- "You won 8/10 battles! Earned 1,500 gold, 2 rare cards, 300 XP"
- Encourages login to see results and re-queue

**Why It Works**:
- Rewards players for returning ("I made progress while sleeping!")
- Creates check-in habit (morning coffee + game check-in ritual)
- Low-stress engagement (no grinding required)

### Progression Treadmill (Always a Goal)
**Short-Term Goals** (1-3 days):
- "Complete daily quest for 200 gems"
- "Win 10 battles for rare pack"
- "Reach Level 6 to unlock auction house"

**Medium-Term Goals** (1-2 weeks):
- "Collect 50 Norse cards for theme bonus"
- "Reach Gold rank in PvP (1500 Elo)"
- "Save 10,000 gold for legendary auction purchase"

**Long-Term Goals** (1-3 months):
- "Reach Level 30 for max deck slots"
- "Complete card collection (500/500)"
- "Reach Grandmaster rank (top 100 globally)"

**Infinite Goals** (never-ending):
- **Prestige System**: Reset castle at Level 50 for permanent +5% XP bonus (repeatable)
- **Endless Tower**: 100+ floor PvE challenge (leaderboard for highest floor)
- **Seasonal Ladders**: Elo resets every 3 months (climb again for seasonal rewards)

**Why It Works**:
- Always something to work toward (prevents "I've beaten the game" quit-point)
- Varied goals appeal to different player types:
  - **Achievers**: Level up, collect cards, complete achievements
  - **Competitors**: Climb PvP ladder, beat leaderboards
  - **Socializers**: Build alliance, make friends
  - **Explorers**: Unlock all themes, discover synergies

### Retention Metrics & Targets
**Industry Benchmarks** (for strategy games):
- **Day 1 (D1) Retention**: 40-50% (target: 45%)
- **Day 7 (D7) Retention**: 15-25% (target: 20%)
- **Day 30 (D30) Retention**: 8-15% (target: 10%)

**Our Retention Drivers**:
- **Energy System**: Encourages 2-3 logins per day (boosts D1-D7)
- **7-Day Login Streak**: Legendary reward on Day 7 (hooks players through first week)
- **Alliance Social**: Guilds boost D30 retention by 2-3x (friends keep you playing)
- **AFK Mechanics**: Low-stress engagement for busy players (prevents burnout)

**Churn Prevention**:
- **Lapsed Player Re-Engagement**: 
  - Email after 3 days: "Your alliance misses you! +100 free energy"
  - Push notification after 7 days: "Come back for welcome-back legendary pack!"
  - In-game bonus after 14 days: 2x XP for next week
- **Exit Surveys**: "Why are you leaving?" popup on uninstall (collect feedback)
- **Win-Back Campaigns**: Target churned players 30-60 days later with exclusive offers

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

### Uncommon



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
**2.5D rotating globe** with continents, oceans, and climate zones visible. Zoom out to see entire world; zoom in to see State-level detail.

### Scale & Scope
- **Size**: 200-500 territories (castles, cities, landmarks)
- **Playtime**: 3-month seasons with persistent progress
- **Player Count**: 50-200 players per server (alliances of 10-30 members)
- **Reset**: Partial reset every season (territories reset, cards/progression persist)

### Gameplay
**Alliance Politics**: Form/join alliances, declare wars, negotiate peace treaties
- **Diplomacy System**: Vote on war declarations (requires 60% alliance approval)
- **Treaty Types**: Non-Aggression Pacts (NAP), Resource Sharing, Joint Defense
- **Territory Trading**: Alliances can gift/trade territories for strategic positioning

**Wonder Control**: Capture and hold 5-10 wonders for powerful server-wide buffs
- **Examples**: 
  - Great Library: +20% XP for all alliance members
  - Colossus: +30% gold production from mines
  - World Tree: +1 energy regeneration per hour
- **Capture Mechanics**: Control adjacent territories + win siege battle
- **Wonder Defense**: Wonders have 10,000+ HP, require coordinated alliance attacks

**PvE Expansion**: Start with 1 castle, expand against 1-3 AI opponents (Risk-style)
- **AI Difficulty**: Scales with player level (Easy = passive, Hard = aggressive expansion)
- **Resource Scramble**: Compete for resource-rich territories (ore mountains, fertile plains)
- **Victory Conditions**: Eliminate all AI capitals OR hold 50% of territories for 7 days

### Control Mechanics
**Majority of Capitals**: Alliance controlling most capitals (5+ out of 10) wins season
- **Capital Importance**: Capitals generate 5x resources, provide alliance-wide buffs
- **Multi-Castle Strategy**: Players can hold 3-10 castles across map (based on level)
- **Defense Requirements**: Each castle requires garrison (minimum 3 hero stacks)

### Building Placement
**Castles & Forts**: Primary structures for territory control
- **Castle Slots**: 
  - Level 1: 5 building slots (3 production, 2 defense)
  - Level 5: 10 slots (6 production, 4 defense)
  - Level 10: 20 slots (12 production, 8 defense)
- **Fort Slots**: Smaller outposts with 3 slots (1 production, 2 defense)
- **Scaling**: Slots increase with lord level (+1 slot per 2 levels)

**Building Types for Global Map**:
- **Production**: Mines (ore), Farms (food), Lumber Mills (wood), Banks (gold)
- **Defense**: Walls (+50% defense), Turrets (auto-attack), Moats (slow enemies)
- **Special**: Wonder Monuments (boost wonder capture speed), Teleport Gates (fast travel)

### Strategic Depth
- **Terrain Advantages**: Coastal castles get trade bonuses, mountain castles get defense bonuses
- **Supply Lines**: Territories must be connected for resource flow (cut lines to starve enemies)
- **Seasonal Events**: Mid-season invasions (AI barbarians attack all players), final week rush

### Rewards
- **Season End**: Top 3 alliances get exclusive legendary cards, titles, themes
- **Personal Ranking**: Individual contribution (captures, defenses) earns bonus rewards

## Tier 2: State Map (Monthly War)

### View
**Hex grid overlay** on isometric terrain. Each hex is a playable tile (50-100 hexes per state).

### Scale & Scope
- **Size**: 50-100 hexes per state map
- **Playtime**: 1-month campaigns with weekly checkpoints
- **Player Count**: 10-30 players per state (subset of global server)
- **Reset**: Monthly reset with rewards based on final holdings

### Gameplay
**Castle Placement**: Establish main castle on strategic hex, expand with forts and towns
- **Hex Selection**: Choose starting hex based on terrain preferences (mountains = defense, plains = expansion)
- **Expansion Strategy**: Capture adjacent hexes to grow territory
- **Defensive Lines**: Build walls and garrisons on border hexes to prevent invasions

**Sieges**: Multi-phase battles to capture enemy castles
- **Phase 1 - Breach Walls**: Destroy castle walls (5,000 HP) using siege units (catapults, battering rams)
- **Phase 2 - Inner Courtyard**: Fight defenders in tactical battle (8x8 grid)
- **Phase 3 - Throne Room**: Final boss battle against castle lord (legendary hero with elite guards)
- **Duration**: Sieges last 3-7 days with continuous reinforcement battles
- **Defense**: Defenders can reinforce between battles, place buildings for auto-defense

**PvE Building Decks**: Place structures on hexes for economy and defense
- **Turrets**: Auto-attack enemies within 3-hex radius (range attacks)
- **Garrisons**: House 5-10 unit stacks for auto-defense
- **Barracks**: Recover 10% unit HP per hour for stationed units
- **Walls**: +50% defense to castle hex, must be destroyed before siege
- **Resource Extractors**: Mines, farms, lumber mills placed on optimal terrain

### Terrain System
**Hex Types & Bonuses**:
- **Fertile Plains**: +50% food production from farms, +10% movement speed
- **Mountains**: +100% ore production from mines, +30% defense, -20% movement speed
- **Forests**: +50% lumber production, +20% defense (cover), +10% ambush chance
- **Water**: +50% fish production, -50% movement (requires boats), impassable for most units
- **Deserts**: -20% food production, +20% movement speed, sandstorms (random debuffs)
- **Swamps**: -30% movement speed, disease debuff (-5% HP per turn), rare herb resources

**Terrain Stacking**: Multiple bonuses apply (e.g., forest mountain = +30% defense + lumber + ore)

### Random Generation
**Procedural Map Creation**:
- **Seed-Based**: Each state has unique seed for reproducible maps
- **Biome Distribution**: 30% plains, 25% forests, 20% mountains, 15% water, 10% special
- **Resource Clustering**: Ore-rich regions (3-5 mountain hexes together), farming belts
- **Strategic Landmarks**: Rivers (natural borders), mountain passes (chokepoints), lakes (fishing hubs)
- **Replayability**: 1000+ possible map configurations ensure no two campaigns are identical

### Strategic Depth
- **Chokepoints**: Control mountain passes or bridges to limit enemy movement
- **Resource Wars**: Fight for fertile/ore-rich regions to boost economy
- **Scorched Earth**: Destroy enemy buildings when retreating to deny resources
- **Hex Influence**: Control 7+ adjacent hexes to form a "province" with bonus yields

### Building Placement Mechanics
- **Hex Limits**: Each hex holds 1 castle OR 1 fort OR 2-3 buildings (based on hex size)
- **Terrain Restrictions**: 
  - Farms only on plains/fertile land
  - Mines only on mountains
  - Fishing huts only on water/coast
  - Turrets on any defensive hex
- **Synergy Bonuses**: Adjacent buildings boost each other (mill + farm = +25% food)

### Rewards
- **Monthly Ranking**: Top 3 players per state get exclusive state-themed cards
- **Hex Control**: Each hex controlled at month end grants resources (gold, gems, packs)

## Tier 3: County Map (Weekly Reset)

### View
**District grid overlay** (20x20 tiles) with visible resource nodes and building placements.

### Scale & Scope
- **Size**: 20x20 = 400 tiles per county
- **Playtime**: 1-week cycles with daily objectives
- **Player Count**: 5-15 players per county (competitive resource gathering)
- **Reset**: Weekly reset, resources/buildings cleared, new map generated

### Gameplay
**Resource Scrambles**: Competitive PvE race to claim resource-rich tiles
- **Spawn Events**: Every 6 hours, new resource nodes appear (ore veins, lumber stands, fishing spots)
- **First-Come-First-Served**: First player to place building on resource node claims it
- **Node Depletion**: Resources deplete after 100-500 harvests, forcing relocation
- **Contested Tiles**: Multiple players can attack each other's buildings to steal nodes (PvP-lite)

**Production Buildings**: Place economic structures on tiles for AFK income
- **Placement Strategy**: 
  - Farms on fertile tiles (plains, river valleys): 5-10 food/hour
  - Mines on ore nodes (mountains, caves): 3-8 ore/hour
  - Lumber mills on forests: 4-7 wood/hour
  - Fishing huts on water tiles: 3-6 fish/hour
  - Banks on trade routes (roads, markets): 10-20 gold/hour
- **Upgrade Tiers**: Level 1 → 2 → 3 buildings with increasing production (2x, 4x, 8x)
- **Maintenance Costs**: Buildings require 10% of production as upkeep (food for workers)

### Terrain & Biome System
**Dynamic Biomes**: Each weekly reset features different biome distribution
- **Temperate**: Balanced mix (40% plains, 30% forest, 20% water, 10% mountains)
- **Arid**: Low water (10% water, 60% desert, 20% rocky, 10% oasis)
- **Tundra**: Cold climate (50% snow, 30% ice, 15% taiga, 5% mountain)
- **Tropical**: High fertility (40% jungle, 30% rainforest, 20% swamp, 10% beach)

**Biome Effects on Production**:
- **Water Tiles**: +50% fish production, boats required for access, -50% building stability
- **Dirt/Plains**: Neutral stats, versatile for farms, roads, markets
- **Forest**: +30% lumber, -20% movement, ambush risk in PvP
- **Mountain**: +80% ore, -40% movement, high defensibility
- **Desert**: -30% food, +40% solar energy (future tech theme), sandstorms
- **Swamp**: +20% rare herbs (alchemy), -50% movement, disease risk

### Strategic Depth
**Resource Chain Optimization**:
- **Synergy Chains**: Farm + Mill + Bakery = 3x food production
- **Transport Routes**: Roads connecting buildings reduce upkeep by 20%
- **Storage Limits**: Warehouses increase resource caps (base: 1000, max: 10,000 per resource)
- **Market Trading**: Sell excess resources to NPCs or players at market tiles

**Competition Mechanics**:
- **Tile Raids**: Attack undefended buildings to steal 1 day of production
- **Defense**: Place garrison buildings (guards, traps) to deter raids
- **Alliances**: Temporary truces with other players to share resource-rich regions
- **Scoreboard**: Weekly leaderboard for most resources produced (rewards: gems, rare cards)

### AFK Optimization
- **Offline Production**: Buildings produce resources 24/7, capped at 8-hour accumulation
- **Push Notifications**: Alert when storage is full ("Your warehouse is overflowing!")
- **Auto-Sell**: Optional setting to auto-sell excess resources to NPCs
- **Protection Period**: New buildings have 24-hour immunity to raids

### Rewards
- **Weekly Top 10**: Bonus gems (500-100), rare building cards, exclusive county banners
- **Milestone Rewards**: Produce 10,000 total resources = legendary card
- **Daily Quests**: "Place 5 buildings" (50 gems), "Harvest 1000 resources" (1 rare pack)

## Tier 4: Local Map (Daily Mission)

### View
**8x8 tactical grid** (chess-board style) with 2D top-down perspective for clarity.

### Scale & Scope
- **Size**: 8x8 = 64 tiles per battle
- **Playtime**: 5-15 minutes per battle
- **Player Count**: 1v1 PvP, 1vAI PvE, or 2v2 co-op
- **Reset**: Daily missions, infinite PvP availability

### Gameplay
**Tactical Battles**: Core combat system for all engagements
- **Deployment Phase**: 
  - Players place units on their side (rows 1-2 for player, rows 7-8 for opponent)
  - Max 8 units per side (hero + 7 unit stacks)
  - Formation strategy: Frontline tanks, backline archers, flanking cavalry
- **Turn-Based Combat**: 
  - Initiative order determined by speed stats (see Section 8.1)
  - Each unit gets 1 action per turn: Move OR Attack OR Ability
  - Turns alternate: Player 1 unit → Player 2 unit → P1 → P2 (based on initiative)
- **Win Conditions**: 
  - Eliminate all enemy units, OR
  - Capture central objective tile (flag on C4/D4), OR
  - Survive 20 turns (defender wins)

**Building Integration**: Placed buildings provide tactical buffs during battles
- **Turret**: Auto-attacks 1 random enemy per turn (30-50 damage)
- **Fortification**: Units on fortified tiles get +30% defense
- **Healing Station**: Units adjacent to station recover 10% HP per turn
- **Trap Tiles**: Hidden traps deal 50 damage when enemy steps on them (1-time use)
- **Wall Segments**: Impassable tiles that block movement, must destroy (200 HP)

### Environment & Biome Effects
**Biome-Based Tactical Bonuses**:
- **Forest**: 
  - Cover tiles (green highlight): +20% defense, +10% evasion
  - Ambush mechanic: Units hidden in forest can't be targeted until they attack
  - Fire vulnerability: Fire attacks deal 2x damage to forest tiles, create burning tiles
- **Desert**: 
  - Sandstorm events (random turns): All ranged attacks -30% accuracy
  - Heat exhaustion: Units lose 2% HP per turn (mitigated by water resource)
  - Oasis tiles: Restore 5% HP per turn to units standing on them
- **Snow/Ice**: 
  - Slippery tiles: Movement costs 2 tiles instead of 1
  - Frost damage: Water units deal +25% damage in snow biomes
  - Blizzard events: Vision reduced to 3-tile radius
- **Swamp**: 
  - Slow movement: All units move at 50% speed
  - Poison gas: 5% chance per turn to inflict poison (-3% HP for 3 turns)
  - Quicksand tiles: Trap units for 1 turn (can't move or attack)
- **Mountain**: 
  - High ground: Units on elevated tiles get +20% attack range and damage
  - Chokepoints: Narrow passes force single-file movement (tactics advantage)
  - Avalanche events: Random tiles collapse, dealing 100 damage to units on them
- **Grassland/Plains**: 
  - Neutral terrain: No bonuses or penalties
  - Cavalry bonus: Mounted units get +15% movement speed
  - Open field: No cover, ranged units have advantage

### Strategic Depth
**Positional Tactics**:
- **Flanking**: Attacking from side/rear grants +25% damage bonus
- **Zone Control**: Tanks hold frontline while archers attack from safety
- **Chokepoints**: Force enemies through narrow paths (1-2 tile wide)
- **Kiting**: Ranged units retreat while shooting (hit-and-run)
- **Pincer Movement**: Attack from two sides simultaneously for +50% damage

**Building Destruction**:
- **Siege Mechanics**: Catapults and battering rams target buildings (3x damage)
- **Collateral Damage**: Destroyed buildings create rubble tiles (impassable)
- **Resource Denial**: Destroying enemy production buildings stops resource flow
- **Reward**: Destroying enemy buildings grants 100 gold + 10% of stored resources

### Auto-Battle Integration
- **Tactics Assignment**: Pre-program AI behavior (see Section 8.1)
  - "Focus Healers": Prioritize healing units
  - "Defend Objective": Guard flag tile
  - "Aggressive Push": Advance and attack nearest enemy
  - "Kite & Shoot": Maintain distance, use ranged attacks
- **Manual Override**: Switch to manual control mid-battle (1-time use per battle)
- **Speed Settings**: 1x, 2x, 4x battle speed for quick resolution
- **Skip Animations**: Instant results for repeat battles (PvE farming)

### Daily Missions
- **PvE Challenges**: 
  - "Defeat 5 enemies in 10 turns" (50 gems)
  - "Win without losing a unit" (1 rare pack)
  - "Destroy all enemy buildings" (100 gold)
- **PvP Ladder**: 
  - 3 daily ranked matches for bonus rewards
  - Win streak bonuses: 3 wins = 50 gems, 5 wins = 1 epic pack, 10 wins = 1 legendary card
- **Co-op Missions**: 
  - 2v2 against elite AI bosses
  - Shared rewards (both players get 75% of total loot)

### Rewards
- **Victory**: 50-200 gold, 10-50 XP, 1-5 common cards, rare chance for epic/legendary
- **Defeat**: 10 gold, 5 XP (consolation prize)
- **Perfect Victory** (no units lost): 2x rewards + bonus rare card
- **First Win of Day**: 100 gems + 1 guaranteed rare pack

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
The VIP system rewards consistent spending with perks that enhance convenience and social status, but **never gameplay power**. It's designed for retention without creating pay-to-win imbalance.

### VIP Tier Structure
**Progression**: Unlock VIP tiers by cumulative gem spending (lifetime, not monthly)

- **VIP 0 (Free Player)**:
  - 100 max energy (recharges 1 per 30 minutes)
  - 3 deck slots
  - 1 free pack per week
  - Basic chat emotes (10 options)
  - Standard auction house fees (10%)

- **VIP 1** (100 gems lifetime = $1 USD):
  - +20 max energy (120 total)
  - +1 deck slot (4 total)
  - Daily free common pack (1 per day)
  - +5 chat emotes (15 total)
  - -1% auction house fees (9%)
  - VIP badge (bronze) next to username
  - Skip tutorial option for alt accounts

- **VIP 2** (500 gems = $5):
  - +30 max energy (130 total, faster recharge: 1 per 25 min)
  - +1 deck slot (5 total)
  - Daily free rare pack (1 per day)
  - +10 chat emotes (25 total)
  - -2% auction fees (8%)
  - VIP badge (silver)
  - Auto-battle speed: 2x unlocked
  - Alliance treasury contribution UI shortcut
  - Priority matchmaking (10% faster queue times)

- **VIP 3** (2,000 gems = $20):
  - +50 max energy (150 total, 1 per 20 min)
  - +2 deck slots (7 total)
  - Daily free epic pack (1 per day)
  - +20 chat emotes + custom emote upload (45 total)
  - -3% auction fees (7%)
  - VIP badge (gold)
  - Auto-battle speed: 4x unlocked
  - Gifting: Send 5 gifts per day (vs 3 for free)
  - Resource storage +20%
  - Exclusive VIP-only chat channel
  - Login streak protection: 1 missed day forgiven per month

- **VIP 4** (5,000 gems = $50):
  - +70 max energy (170 total, 1 per 15 min)
  - +2 deck slots (9 total)
  - Daily free epic pack + weekly legendary pack
  - All emotes unlocked + animated emotes
  - -4% auction fees (6%)
  - VIP badge (platinum)
  - Auto-battle: Instant results (skip animations entirely)
  - Gifting: Send 10 gifts per day
  - Resource storage +50%
  - Exclusive VIP-4 avatar frames
  - Alliance leadership: VIP-only alliance creation
  - Priority customer support (24-hour response)

- **VIP 5** (10,000 gems = $100):
  - +100 max energy (200 total, 1 per 10 min)
  - +1 deck slot (10 total, max)
  - Daily free legendary pack
  - Custom chat name colors + font styles
  - -5% auction fees (5%, minimum)
  - VIP badge (diamond)
  - Auto-battle: Queue 10 battles at once
  - Gifting: Unlimited
  - Resource storage +100%
  - Exclusive legendary VIP-only cards (cosmetic variants, same stats)
  - Private 1-on-1 matches with friends (custom rules)
  - Developer Q&A access (monthly AMA)
  - Eternal login streak protection (never resets)

### Daily Rewards System
**Login Streaks**: Consecutive logins grant escalating rewards

**Free Player Rewards** (7-day cycle):
- Day 1: 50 gold, 10 energy
- Day 2: 100 gold, 1 common pack
- Day 3: 150 gold, 20 energy
- Day 4: 200 gold, 1 rare pack
- Day 5: 250 gold, 30 energy
- Day 6: 300 gold, 1 epic pack
- **Day 7: 500 gold, 50 gems, 1 legendary card** (guaranteed)
- Resets to Day 1, but Day 7 reward only once per week

**VIP Bonus Rewards** (added on top):
- VIP 1: +25% gold on all days
- VIP 2: +50% gold, +1 rare pack on Day 4
- VIP 3: +100% gold, +1 epic pack on Day 6
- VIP 4: +150% gold, Day 7 reward = 2 legendary cards
- VIP 5: +200% gold, Day 7 reward = 3 legendary cards + exclusive VIP skin

**Streak Protection**:
- Free players: Lose all progress if 1 day missed
- VIP 3+: 1 forgiveness per month (VIP 5: infinite forgiveness)
- Grace period: 4-hour buffer after midnight (login by 4am counts for previous day)

### VIP Exclusives (Cosmetic Only)
- **Avatar Frames**: Animated borders around profile picture (gold, platinum, diamond)
- **Card Skins**: Alternate art for existing cards (same stats, different visuals)
- **Chat Effects**: Sparkles, emojis, animated text for VIP 4+
- **Profile Badges**: Special titles ("Platinum Patron", "Diamond Sovereign")
- **Battle VFX**: Premium visual effects for VIP 5 (golden card glow, special victory animations)

### Anti-Pay-to-Win Design
- **No Stat Advantages**: VIP players don't get stronger cards, just more convenience
- **Energy Cap**: VIP energy recharges faster, but can't exceed daily active limit (200 = ~6 hours play)
- **Deck Slots**: Max 10 slots prevents analysis paralysis, equal for VIP 5 and free at endgame
- **Auction Fees**: 5% minimum prevents market manipulation
- **Free Legendary Path**: Free players can still get Day 7 legendary weekly

### VIP Monetization Philosophy
- **Pay-for-Speed**: VIP players progress faster (more energy, packs), but don't become stronger
- **Pay-for-Convenience**: Auto-battle speed, queue multiple battles, priority support
- **Pay-for-Status**: Cosmetics, badges, exclusive social features for prestige
- **Whale-Friendly**: VIP 5 targets spenders, but doesn't lock content behind paywall
- **Fair Free Play**: Free players can achieve 90% of VIP 5 progression with time investment

### Analytics & Balance
- **Target VIP Distribution**: 70% VIP 0, 15% VIP 1-2, 10% VIP 3-4, 5% VIP 5
- **ARPPU Target**: $15-30 per paying user (focused on VIP 2-3)
- **Whale Revenue**: VIP 4-5 expected to generate 40-60% of total revenue
- **Conversion Rate**: 5-10% of free players convert to VIP 1+ within 30 days

## 5.3 The Auction House (Player Market)

### Overview
A **true player-driven free market** where supply and demand determine prices. The Auction House is the economic heart of Sovereign Territories, fostering community interaction, price discovery, and strategic trading.

### How to Play

**Accessing the Market**:
- **Unlock**: Available at castle Level 5 (prevents early-game market flooding)
- **Location**: Dedicated Auction House tab in main menu (UI: medieval marketplace theme)
- **Fees**: 10% house cut on all sales (reduced to 5% for VIP 5)
- **Currency**: Gold only (gems cannot be traded to prevent real-money trading)

**Listing Items**:
1. **Select Card**: Choose from inventory (unlisted cards only)
2. **Set Price**: 
   - **Fixed Price**: Instant buyout (e.g., 500 gold)
   - **Auction**: Starting bid + buyout option (e.g., start 100g, buyout 500g)
3. **Duration**: 24 hours, 48 hours, or 7 days
4. **Quantity**: List 1-100 copies of same card (bulk discount encouraged)
5. **Preview**: See estimated market value based on recent sales
6. **Confirm**: Pay 1% listing fee upfront (refunded if sold)

**Bidding Mechanics**:
- **Minimum Increment**: +5% of current bid (prevents penny-bidding spam)
- **Proxy Bidding**: Set max bid, system auto-bids up to your limit
- **Escrow**: Bid amount locked in escrow until outbid or auction ends
- **Anti-Snipe Extension**: Auction extends 60 seconds if bid placed in final 30 seconds
- **Notifications**: Push notifications for outbid alerts (opt-in)

**Instant Buyout**:
- **One-Click Purchase**: Pay listed price, card delivered instantly
- **Bulk Discount**: Buying 10+ copies gives 5% discount
- **Price Warnings**: Alert if price >150% of market average ("This seems expensive!")

**Advanced Search & Filters**:
- **By Rarity**: Common, Rare, Epic, Legendary
- **By Type**: Hero, Unit, Building, Tactic, Equipment
- **By Theme**: Norse, Medieval, Sci-Fi, etc.
- **By Price**: Min/max gold range
- **By Seller**: Favorite traders, alliance members
- **By Stats**: Min attack, min HP, specific abilities
- **Sort Options**: Lowest price, ending soon, newly listed, popularity

### Offline Mode
**Persistent Listings**:
- Listings remain active even when offline
- Automated bidding system continues
- Sales notifications on next login
- Auto-delivery to inventory (no manual collection)

**Watchlist**:
- Favorite up to 50 listings for price tracking
- Alerts when watched item price drops 10%
- Historical price charts (last 30 days)

### Market Dynamics

**Supply & Demand**:
- **Popular Cards**: High demand drives prices up (e.g., meta heroes = 5,000-10,000 gold)
- **Oversupply**: Common cards flood market, prices drop to vendor minimum (10-50 gold)
- **Seasonal Fluctuations**: New expansion release crashes old card prices (-30-50%)
- **Event Impact**: Limited-time events spike demand for specific themes (e.g., Norse week = +200% for Thor)

**Price Discovery**:
- **Market Average**: System calculates 7-day rolling average per card
- **Suggested Price**: Listing UI shows recommended price (±15% of average)
- **Price Trends**: Up/down arrows indicate recent price movement
- **Whales vs Free Players**: Whales stabilize market by buying underpriced cards, flipping for profit

**Anti-Manipulation Safeguards**:
- **Volume Limits**: 
  - Max 10 legendary cards listed per player at once
  - Max 50 epic cards per player
  - Unlimited common/rare
- **Price Floors**: Cards cannot be listed below vendor sell price (prevents value destruction)
- **Price Ceilings**: Cards cannot exceed 5x market average (prevents price gouging)
- **Wash Trading Detection**: System flags accounts buying/selling between own alt accounts
- **Bot Prevention**: Captcha for rapid purchases (>10 per minute)

### Strategic Trading

**Buy Low, Sell High**:
- **Weekend Dips**: Prices drop Saturday-Sunday (high supply from weekend players)
- **Weekday Peaks**: Prices rise Monday-Wednesday (low supply, high demand)
- **Patch Speculation**: Buy cards expected to be buffed, sell before nerfs
- **Expansion Pre-Buy**: Stock up on staples before expansion (prices rise 20-40%)

**Flipping for Profit**:
- **Snipe Underpriced**: Buy cards listed 30-50% below market, relist at average
- **Bulk Arbitrage**: Buy 100 commons at 10g each, sell bundle at 15g each
- **Cross-Market Trading**: Buy on low-pop servers, sell on high-pop (future feature)

**Collection Completion**:
- **Missing Cards**: Use auction to fill gaps in collection (faster than packs)
- **Duplicate Fodder**: Sell extra copies to fund legendary purchases
- **Set Bonus Hunting**: Complete theme sets (20 Norse cards) via market shopping

### Player Tips

**For Sellers**:
- **Undercut by 5%**: List slightly below market average for fast sales
- **Auction for Rares**: Let bidding war drive up price for rare/legendary cards
- **Bundle Discounts**: Sell 10-packs of commons for bulk buyers
- **Weekend Sales**: List commons Friday night when demand spikes
- **Relist Failed Auctions**: If no bids, reduce starting price by 10-20%

**For Buyers**:
- **Patience Pays**: Wait for weekend dips to buy (20-30% savings)
- **Snipe Auctions**: Bid in final 10 seconds for less competition (but beware auto-extend)
- **Buy in Bulk**: 10+ copies = 5% discount
- **Check Market History**: Review 30-day price chart before overpaying
- **Set Price Alerts**: Get notified when target cards drop to desired price

### Restrictions

**Non-Tradable Items**:
- **Starter Cards**: Tutorial reward cards are soul-bound (cannot sell/trade)
- **VIP Exclusive Cards**: Cosmetic variants stay with VIP account
- **Event-Locked**: Some seasonal cards locked for 30 days after acquisition
- **Gems**: Cannot be sold or traded (prevents real-money trading)

**Account Requirements**:
- **Level Gate**: Must be castle Level 5+ to sell (prevents bot spam)
- **Verified Email**: Require email verification to list items (anti-fraud)
- **Trade Cooldown**: New accounts have 7-day cooldown before selling (prevents hacks/chargebacks)

### Economy Health Monitoring

**Developer Tools**:
- **Inflation Tracking**: Monitor total gold in economy, velocity, hoarding
- **Price Anomaly Alerts**: Flag 500%+ price spikes (investigate manipulation)
- **Banned Card Removal**: Pull items from market if exploit discovered
- **Emergency Rollback**: Revert trades if dupe bug detected (rare, with compensation)

**Transparency Reports**:
- **Monthly Market Stats**: Published blog post with:
  - Top 10 most-traded cards
  - Average prices per rarity tier
  - Total gold transacted
  - Price trend analysis
- **Player Confidence**: Builds trust in market fairness

### Future Expansion Features
- **Cross-Server Trading**: Buy/sell across regional servers (planned for Year 2)
- **Trade Chat**: Dedicated channel for WTB/WTS spam
- **Rental System**: Rent legendary cards for 24-hour trials (test before buying)
- **NFT Integration**: Optional blockchain-based card ownership (controversial, under review)

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
Multi-channel chat system with rich diplomacy tools for PvP/PvE interactions. Designed for cross-cultural communication with built-in translation and moderation.

### Chat Channels

**Global Chat**:
- **Scope**: Server-wide (1000-5000 players)
- **Purpose**: General discussion, LFG (looking for group), trading, announcements
- **Rate Limit**: 1 message per 5 seconds (prevents spam)
- **Visibility**: Last 100 messages cached, older messages archived
- **Moderation**: Auto-filter profanity, human mods review reports

**Regional Chat**:
- **Scope**: State/Territory-level (50-200 players)
- **Purpose**: Local coordination, territory politics, recruitment
- **Rate Limit**: 1 message per 3 seconds
- **Geo-Based**: Automatically join based on controlled territories
- **Language**: Auto-detect region language (English, Spanish, Chinese, etc.)

**Alliance Chat**:
- **Scope**: Guild members only (10-100 players)
- **Purpose**: Strategy, coordination, resource sharing, social bonding
- **Rate Limit**: 1 message per 2 seconds (more permissive for strategy)
- **Features**: 
  - Pinned messages (officers only) for important announcements
  - Voice notes (30-second max)
  - Image sharing (screenshots of battles, memes)
  - Alliance-only emotes and stickers
- **Privacy**: Private, invisible to non-members

**Whispers (Private Messages)**:
- **Scope**: 1-on-1 direct messaging
- **Purpose**: Trade negotiations, friend coordination, private discussions
- **Rate Limit**: 1 message per second
- **Features**:
  - Message history (last 100 messages, 7-day retention)
  - Block/mute individual players
  - Offline messaging (delivered on next login)
  - Read receipts (optional, toggle in settings)
- **Privacy**: Encrypted end-to-end (not readable by devs except for reports)

**Battle Chat**:
- **Scope**: Active battle participants (2-4 players in co-op/PvP)
- **Purpose**: Real-time tactics coordination during battles
- **Rate Limit**: Unlimited during battle
- **Features**:
  - Pre-set quick messages ("Attack left!", "Focus healer!", "Retreat!")
  - Tactical ping system (click tile to alert teammates)
  - Voice chat (optional, toggle in settings)
- **Duration**: Chat log deleted 10 minutes after battle ends

### Diplomacy System

**Diplomatic Statuses** (Alliance-to-Alliance):
1. **Neutral** (Default): 
   - No restrictions, can attack or trade freely
   - No shared vision or buffs
   - Auction house trades allowed

2. **Ally** (Friendly):
   - **Requirements**: Both alliances vote to ally (60% approval)
   - **Benefits**: 
     - Shared territory vision (see ally movements on map)
     - +10% gold/resource production when adjacent to ally territories
     - Free passage through ally lands (no movement penalty)
     - Joint alliance events (combined strength for raids)
   - **Restrictions**: 
     - Cannot attack ally territories (auto-decline)
     - Cannot bid against allies in auction house (optional gentleman's agreement)
   - **Duration**: Minimum 7 days, renewable monthly
   - **Termination**: 48-hour notice required, vote to cancel

3. **War** (Hostile):
   - **Requirements**: Alliance leader declares war, 24-hour warning period
   - **Effects**: 
     - All members marked as hostile (red name tags)
     - Territory attacks enabled (no neutral ground)
     - Bonus loot for defeating enemy players (+25% resources)
     - Alliance-wide war leaderboard (tracks kills, captures)
   - **Restrictions**:
     - Cannot trade with enemy alliance (auction house blocked)
     - Diplomatic immunity revoked (spies can infiltrate)
   - **Duration**: Minimum 14 days, peace treaty requires both sides to vote
   - **Surrender**: Losing alliance can offer terms (gold tribute, territory concessions)

**Voting Mechanics**:
- **Proposal**: Alliance leader/officers create diplomacy proposals
- **Vote Period**: 24-48 hours for members to vote (yes/no/abstain)
- **Quorum**: 50% of active members must vote (logged in last 7 days)
- **Approval**: 60% yes votes required for ally/war declarations
- **Veto**: Alliance leader can veto any vote (limited to 1 per month)
- **Notification**: Push notifications for important votes ("War declaration vote active!")

**Treaty Types**:
1. **Non-Aggression Pact (NAP)**:
   - Agree not to attack each other for 30 days
   - Penalty for breaking: -50% resources for 7 days (economic punishment)
   - Useful for temporary truces during expansion

2. **Resource Sharing Agreement**:
   - Share 10% of resource production with ally
   - Both alliances benefit (symbiotic economy)
   - Auto-trades resources at NPC vendor prices

3. **Joint Defense Treaty**:
   - Automatically join defense when ally is attacked
   - Shared reinforcements (troops can defend ally territories)
   - Risk: Dragged into wars you didn't choose

4. **Vassal/Protectorate**:
   - Smaller alliance becomes vassal of larger alliance
   - Vassal pays 15% gold tribute, receives protection
   - Useful for new players to learn under experienced alliance

### Translation Features

**Auto-Translate**:
- **Languages**: 10+ supported (English, Spanish, French, German, Japanese, Chinese, Korean, Portuguese, Russian, Arabic)
- **Toggle**: Players can enable/disable auto-translate per channel
- **Accuracy**: Uses Google Translate API, 80-90% accuracy for general chat
- **Formatting**: Original message shown in gray, translation in color
- **Example**: 
  - Player A (Spanish): "Necesitamos atacar el castillo norte"
  - Player B sees: "We need to attack the north castle"

**Cultural Sensitivity**:
- **Regional Profanity Filters**: Adjusted per language (what's offensive in English may not be in Japanese)
- **Emoji Support**: Unicode emojis work across all languages
- **Time Zone Display**: Show sender's local time (helps coordinate across continents)

### Rich Communication

**Voice Notes**:
- **Duration**: 10-30 seconds per voice note
- **Format**: Compressed audio (Opus codec, 32kbps)
- **Size Limit**: 500KB per note (prevent spam)
- **Playback**: In-game audio player with waveform visualization
- **Usage**: Strategy explanations, rallying cries, voice intros

**Emojis & Stickers**:
- **Default Pack**: 50 free emojis (smile, laugh, cry, angry, thumbs up, etc.)
- **Alliance Packs**: Custom stickers uploaded by alliance leaders (10 max)
- **VIP Packs**: Exclusive animated emojis for VIP 3+ (sparkles, confetti, explosions)
- **Seasonal Packs**: Holiday-themed stickers (Halloween ghosts, Christmas trees)
- **Usage**: React to messages, express emotions quickly

**Image Sharing** (Limited):
- **Allowed**: Screenshots of battles, deck compositions, map strategies
- **Size Limit**: 2MB per image (compressed to 500KB server-side)
- **Moderation**: Images manually reviewed for NSFW content (24-hour delay)
- **Restrictions**: Disabled in global chat (alliance/whisper only) to prevent spam

### Moderation & Safety

**Profanity Filter**:
- **Auto-Filter**: Replace offensive words with asterisks ("f***", "s***")
- **Customizable**: Players can adjust filter strictness (off/medium/strict)
- **Language-Specific**: Different word lists for each language
- **Bypass Detection**: System flags creative spelling ("fck", "sh!t") as violations

**Report System**:
- **How to Report**: Right-click username → Report → Select reason
- **Reasons**: 
  - Spam (repetitive messages)
  - Harassment (personal attacks, bullying)
  - Hate speech (racism, sexism, homophobia)
  - Scam (fake trades, phishing)
  - Real-money trading (RMT)
- **Evidence**: Last 10 messages from reported player auto-attached
- **Review**: Human moderators review within 24 hours
- **Penalties**: Warning → 24h mute → 7-day ban → permanent ban

**Mute/Block Features**:
- **Mute**: Hide messages from specific player (you still see them in friend list)
- **Block**: Complete ignore (no messages, no friend requests, no trades)
- **Alliance Block**: Alliance leaders can block entire enemy alliances from chat
- **Duration**: Permanent until manually unblocked

### Player Tips

**For Communication**:
- Use alliance chat for coordination; keep global chat for social/recruiting
- Enable auto-translate for international alliances
- Use voice notes for complex strategies (faster than typing)
- React with emojis to acknowledge messages without cluttering chat

**For Diplomacy**:
- Form alliances early for economic bonuses (+10% production)
- Declare war strategically (during enemy's weak period, e.g., after expansion)
- Honor NAPs to build reputation (other alliances more likely to ally with trustworthy players)
- Use whispers for backroom deals (negotiate before public votes)

**For Safety**:
- Report harassment immediately; don't engage with trolls
- Block spammers to clean up chat feed
- Never share personal info (real name, address, phone) in chat
- Be wary of trade scams (use auction house escrow for safety)

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

The Universal Engine allows seamless expansions without rewrites, adding themes, mechanics, and content for long-term engagement. Each expansion is designed as a **modular content pack** that integrates with the core game while introducing fresh aesthetics and strategic depth.

## 7.1 Expansion Structure

### Overview
Expansions drop **quarterly** (4 per year), introducing new themes, cards, and mechanics while maintaining core rules. Each expansion adds 50-100 cards, 2-3 new map biomes, and 1-2 unique mechanics.

### Design Philosophy
- **Backward Compatibility**: New cards work with existing decks (no forced obsolescence)
- **Meta Shifts**: Intentionally introduce counters to dominant strategies (keeps PvP fresh)
- **Theme Diversity**: Each expansion targets different player fantasies (medieval, sci-fi, fantasy, historical)
- **Free Content**: 30-40% of expansion cards earnable via free progression (packs, quests)
- **Paid Content**: 60-70% available via premium packs or auction house (monetization)

### Expansion Examples

#### **Expansion 1: Storm Rising** (Elemental Theme)
**Release**: Quarter 2, Year 1  
**Tagline**: "Harness the fury of nature"

**New Elements**:
- **Lightning**: High burst damage, chain attacks (hits 3 targets), low HP units
- **Wind**: High speed, evasion bonuses, movement buffs (+2 tiles per turn)

**New Cards** (60 total):
- 3 Legendary Heroes: 
  - **Tempest Queen**: Lightning hero, ability = "Chain Lightning" (hits all enemies in a line)
  - **Skylord**: Wind hero, ability = "Tornado" (shuffles enemy positions randomly)
  - **Stormbringer**: Hybrid, summons lightning elementals as units
- 10 Epic Units: Lightning Drakes, Wind Elementals, Storm Riders (cavalry)
- 20 Rare Units: Shock Troopers, Gale Archers, Thunderbirds
- 15 Common Units: Spark Sprites, Breeze Scouts, Cloud Walkers
- 10 Buildings: Lightning Rod (generates energy), Wind Turbine (boosts production), Storm Tower (AoE defense)
- 2 New Tactics: "Kite & Strike" (ranged hit-and-run), "Overcharge" (sacrifice HP for +50% damage)

**New Biomes**:
- **Floating Islands**: Sky-based maps, air units get +30% speed, ground units can't reach
- **Thunder Plains**: Open fields with random lightning strikes (10% chance per turn to hit random unit for 100 damage)

**New Mechanics**:
- **Chain Lightning**: Attacks jump to adjacent enemies (max 3 jumps, -25% damage per jump)
- **Wind Buffs**: Units gain +1 movement per turn stacking (max +5, resets on attack)
- **Weather Events**: Dynamic storms alter battlefield (lightning boosts electric units, wind scatters projectiles)

**Narrative**:
- Campaign: 20-stage saga where players unite elemental clans to stop a cataclysm
- Boss: **Primordial Tempest** (legendary boss with 3 phases: lightning, wind, combined)

**Balance Impact**:
- **Counters Fire Meta**: Lightning deals +25% damage to fire units (water conducts electricity)
- **Mobility Meta**: Wind units dominate speed-based strategies
- **AoE Nerf**: Chain lightning punishes stacked formations (encourages spreading)

---

#### **Expansion 2: Iron Legion** (Military/Modern Theme)
**Release**: Quarter 4, Year 1  
**Tagline**: "Modern warfare meets strategic dominance"

**New Mechanics**:
- **Range Stat**: Units now have attack range (melee = 1, rifle = 3, sniper = 5, artillery = 7)
- **Armor**: Replaces "Defense" for modern units; reduces damage by flat amount (e.g., 50 armor = -50 damage per hit)
- **Cover System**: Units behind walls/buildings get +50% evasion vs ranged

**New Cards** (70 total):
- 4 Legendary Heroes:
  - **General Patton**: Tank commander, ability = "Blitzkrieg" (all units move 2x speed for 1 turn)
  - **Sniper Ace**: Stealth hero, ability = "Headshot" (1-shot kill on any non-hero unit, 5-turn cooldown)
  - **Engineer Chief**: Support hero, builds fortifications mid-battle
  - **Pilot Commander**: Air superiority, commands helicopters and jets
- 15 Epic Units: Tanks (high armor, slow), Attack Helicopters (air units), Snipers (ultra-long range)
- 25 Rare Units: Riflemen, Grenadiers, Medics (healing units), APCs (armored transports)
- 20 Common Units: Infantry, Scouts, Engineers
- 6 Buildings: Bunkers (heavy defense), Airfields (spawn helicopters), Armories (boost attack)

**New Biomes**:
- **Urban Warfare**: City maps with buildings for cover, destructible walls
- **Desert Combat**: Wide-open maps favoring ranged units, sandstorms reduce vision

**New Tactics**:
- **Suppressive Fire**: Reduce enemy accuracy by 30% (useful for advancing)
- **Flanking Maneuver**: Ignore armor if attacking from sides/rear

**Narrative**:
- Campaign: 25-stage modern military campaign, from WWII to futuristic warfare
- Boss: **Mech Titan** (giant robot with missile barrages and EMP attacks)

**Balance Impact**:
- **Range Dominance**: Outranges medieval archers (3 vs 2 range)
- **Armor > Defense**: Flat reduction better against swarms, worse against single-target nukes
- **Anti-Magic**: Modern units immune to elemental effects (fire, lightning don't affect tanks)

---

#### **Expansion 3: Valhalla** (Norse Mythology Theme)
**Release**: Quarter 2, Year 2  
**Tagline**: "Where heroes feast eternal"

**New Mechanics**:
- **Rage**: Attack increases as HP decreases (e.g., at 50% HP, +25% attack; at 25% HP, +50% attack)
- **Berserker Mode**: Units can sacrifice defense for +100% attack (glass cannon strategy)
- **Resurrection**: Fallen heroes revive once per battle at 25% HP (Viking immortality theme)

**New Cards** (80 total):
- 5 Legendary Heroes:
  - **Thor**: Lightning god, hammer throw (AoE stun)
  - **Odin**: Wisdom god, summons ravens for vision, buffs all allies
  - **Loki**: Trickster, creates illusion units (fake copies)
  - **Freya**: Valkyrie queen, revives 1 dead unit per turn
  - **Jormungandr**: World Serpent, poison AoE attacks
- 20 Epic Units: Berserkers (rage mechanic), Valkyries (flying healers), Frost Giants (ice damage)
- 30 Rare Units: Viking Raiders, Shield Maidens, Longship Marines
- 20 Common Units: Thralls, Spearmen, Archers
- 5 Buildings: Mead Hall (boosts morale), Runestone (magic buffs), Longship Dock (naval units)

**New Biomes**:
- **Frozen Tundra**: Ice terrain slows movement, frost attacks deal +30% damage
- **Yggdrasil Grove**: Mystical forest with healing springs, ancient tree grants buffs

**New Tactics**:
- **Last Stand**: Units gain +100% stats when surrounded (3+ enemies adjacent)
- **Viking Funeral**: On death, explode for AoE damage (50% of max HP)

**Narrative**:
- Campaign: 30-stage epic saga through Norse realms (Midgard, Asgard, Jotunheim)
- Boss: **Ragnarok Event** (fight waves of giants, serpents, and Fenrir wolf)

**Balance Impact**:
- **High-Risk High-Reward**: Rage mechanic rewards aggressive play
- **Resurrection Meta**: Encourages targeting heroes first (prevent revives)
- **Frost vs Fire**: Ice counters fire, creates new elemental triangle

---

#### **Expansion 4: Cyber Dominion** (Sci-Fi/Cyberpunk Theme)
**Release**: Quarter 4, Year 2  
**Tagline**: "The future is now"

**New Mechanics**:
- **Hacking**: Disable enemy buildings or units for 1-3 turns (cyber warfare)
- **Energy Shields**: Absorb first 100-500 damage per turn (regenerates)
- **Drone Swarms**: Deploy multiple weak units at once (quantity over quality)

**New Cards** (75 total):
- 4 Legendary Heroes:
  - **AI Overlord**: Robot commander, controls drone swarms
  - **Netrunner**: Hacker hero, disables enemy abilities
  - **Cyborg Assassin**: Stealth + tech, teleportation ability
  - **Megacorp CEO**: Economic hero, generates gold during battles
- 18 Epic Units: Mechs, Cyborgs, Combat Drones, Hoverbikes
- 28 Rare Units: Androids, Hackers, Energy Troopers
- 20 Common Units: Drones, Robots, Turrets
- 5 Buildings: Data Centers (hacking hub), Shield Generators, Factories (spawn drones)

**New Biomes**:
- **Neon Cityscape**: Vertical maps with rooftops and alleys
- **Wasteland**: Post-apocalyptic ruins, radiation zones (-5% HP per turn)

**New Tactics**:
- **Overload**: Sacrifice energy shield to deal massive AoE damage
- **Cloaking**: Units invisible for 2 turns (can't be targeted)

**Narrative**:
- Campaign: 25-stage rebellion against megacorps
- Boss: **Rogue AI** (adapts tactics mid-battle, learns from player moves)

**Balance Impact**:
- **Tech vs Magic**: Hacking disables magical abilities
- **Shield Meta**: Regenerating shields counter DoT (damage-over-time)
- **Drone Rush**: Swarm strategy counters single-target nukes

---

### Seasonal Content

**Limited-Time Themes** (2-4 weeks each):
- **Halloween**: Undead units, haunted castle maps, pumpkin-themed cosmetics
- **Winter Festival**: Ice elementals, snowman units, holiday skins
- **Summer Splash**: Beach maps, pirate units, nautical themes
- **Lunar New Year**: Dragon units, firework VFX, Asian-inspired heroes

**Exclusive Rewards**:
- Seasonal legendary cards (limited availability, returns yearly)
- Event-only cosmetics (skins, emotes, avatar frames)
- Double XP/gold weekends

**FOMO Strategy**:
- Encourages collection ("Get Thor before he's gone!")
- Annual rotation keeps content fresh without permanent removal

## 7.2 Implementation

### Modding Support
**Community Content Creation**:
- **Unity Modding Tools**: Release official SDK for custom cards, maps
- **Workshop Integration**: Steam Workshop or in-game browser for mods
- **Approval Process**: Best mods promoted to official content (revenue share with creator)
- **Restrictions**: Mods can't affect PvP balance (cosmetic/PvE only)

**Example Mods**:
- Custom card art (anime-style heroes)
- Fan-made campaigns (40K Warhammer theme)
- Map editor (create custom 8x8 battle grids)

### Balance Philosophy
**Meta Shifts**:
- **Intentional Counters**: Each expansion introduces cards that counter previous meta
- **Power Creep Avoidance**: New cards aren't strictly better, just different
- **Rotation Option** (Future): Limit ranked PvP to last 2 expansions (like Hearthstone Standard)
- **Eternal Format**: Separate queue for all cards (Wild mode)

**Patch Cadence**:
- **Bi-Weekly Hotfixes**: Minor stat tweaks (+5% HP, -10% cost)
- **Monthly Balances**: Major reworks (ability changes, rarity shifts)
- **Expansion Previews**: 2 weeks early access for testers to find broken combos

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

### XP Sources
- **PvE Battles**: 10-50 XP per victory (scales with difficulty)
- **PvP Matches**: 25-100 XP per match (win = full, loss = 25%)
- **Daily Quests**: 50-200 XP per quest completed
- **Weekly Challenges**: 500-1000 XP for tournament participation
- **Alliance Events**: 100-500 XP for contributions
- **First Win of Day**: Bonus 100 XP
- **Login Streaks**: 50 XP per day (cumulative up to 350 XP on day 7)

### XP Progression Curve
**Level Requirements** (exponential curve to encourage long-term play):
- Level 1 → 2: 100 XP
- Level 2 → 3: 250 XP
- Level 3 → 4: 500 XP
- Level 4 → 5: 1,000 XP
- Level 5 → 10: 2,000 XP per level (total: 10,000 XP)
- Level 10 → 20: 5,000 XP per level (total: 50,000 XP)
- Level 20 → 30: 10,000 XP per level (total: 100,000 XP)
- Level 30+: 15,000 XP per level (no cap, infinite progression)

**Total XP to Level 30**: ~160,000 XP (estimated 60-90 days of active play)

### Unlock Milestones
- **Level 5**: Unlock Auction House, join alliances
- **Level 10**: PvP ranked matchmaking, alliance wars, State Map access
- **Level 15**: Unlock Expedition board game mode
- **Level 20**: County Map access, advanced building decks
- **Level 25**: Global Map access, wonder control
- **Level 30**: Max deck slots (10), prestige titles, endgame content
- **Level 40**: Legendary achievement badge, developer Q&A access
- **Level 50**: Eternal title, custom avatar frame, name in credits

### Titles & Badges
**Earned at Milestones**:
- Level 10: "Veteran Commander"
- Level 20: "Master Tactician"
- Level 30: "Sovereign Lord"
- Level 40: "Legendary Conqueror"
- Level 50: "Eternal Sovereign" (displayed next to username)

**Special Titles** (achievement-based):
- "Undefeated" (50 PvP wins without loss)
- "Whale Hunter" (defeat 10 VIP 5 players)
- "Economy Tycoon" (1,000,000 gold earned)
- "Card Collector" (500+ unique cards)

## 9.2 Castle/Lord Leveling

Your main castle acts as a hub, leveling with XP to unlock features. Higher levels increase deck slots (e.g., Level 10 allows 10-slot decks), enable more complex tactics, and provide passive buffs like increased gold income. At Level 10, players become eligible for PvP alliances and top-tier maps. Players can join alliances earlier, contributing resources and experience for alliance bonuses (e.g., 10% boost to earnings).

### Castle XP & Leveling
**Separate from Player XP**: Castle levels via territory control and building upgrades

**Castle XP Sources**:
- **Holding Territories**: 10 XP per hour per controlled territory
- **Building Upgrades**: 100-500 XP per building level
- **Winning Defenses**: 200 XP per successful defense
- **Wonder Control**: 500 XP per hour (Global Map wonders)
- **Alliance Contributions**: 50 XP per 1,000 gold donated to alliance

**Castle Level Benefits**:
- **Level 1**: 3 deck slots, 5 building slots, 3 hero stacks max
- **Level 5**: 5 deck slots, 10 building slots, 5 hero stacks, +10% gold production
- **Level 10**: 7 deck slots, 15 building slots, 7 hero stacks, +25% gold, unlock State Map
- **Level 15**: 8 deck slots, 20 building slots, 10 hero stacks, +50% gold, unlock County Map
- **Level 20**: 9 deck slots, 30 building slots, 15 hero stacks, +75% gold, unlock Global Map
- **Level 25**: 10 deck slots (max), 40 building slots, 20 hero stacks, +100% gold, prestige castle skin
- **Level 30**: Mega-castle visual upgrade, +150% gold, legendary lord status

### Lord Skill Tree
**Unlocks at Castle Level 5**: Allocate skill points (1 per castle level)

**Skill Tree Branches**:
1. **Economic** (Gold & Resources):
   - **Tax Collector**: +5/10/15/20/25% gold from territories
   - **Resource Boost**: +5/10/15/20/25% food/lumber/ore production
   - **Market Savvy**: -1/-2/-3/-4/-5% auction house fees
   - **Warehouse Manager**: +10/20/30/40/50% storage capacity

2. **Military** (Combat & Defense):
   - **Strategic Mind**: +5/10/15/20/25% XP from battles
   - **Fortifications**: +10/20/30/40/50% building HP
   - **Elite Training**: +2/4/6/8/10% unit attack and HP
   - **Siege Master**: +20/40/60/80/100% damage to enemy buildings

3. **Diplomatic** (Alliance & Social):
   - **Charisma**: +5/10/15/20/25% alliance contribution efficiency
   - **Negotiator**: -10/-20/-30/-40/-50% war declaration costs
   - **Mentor**: +5/10/15% XP for all alliance members (aura buff)
   - **Diplomat**: +1/2/3 max alliance allies

4. **Arcane** (Magic & Special):
   - **Mana Reserves**: +10/20/30/40/50 max energy
   - **Energy Recharge**: -5/-10/-15/-20/-25% energy recharge time
   - **Card Luck**: +1/2/3/4/5% legendary drop rate from packs
   - **AFK Efficiency**: +10/20/30/40/50% AFK resource production

**Respec Cost**: 500 gems (can reset skill tree once per month)

### Multiple Castles
**Secondary Castles** (Unlocked at Player Level 15):
- Hold up to 5 castles simultaneously (1 main + 4 secondary)
- Each castle levels independently
- Secondary castles have 50% building slots of main castle
- Useful for controlling multiple regions on Global Map
- Maintenance cost: 1,000 gold per day per secondary castle

## 9.3 Deck Storage and Management

Decks can be saved and switched instantly, supporting multiple strategies. Storage is limited by castle level, encouraging progression. Dismantling isn't required, preserving builds for PvE or PvP.

### Deck Slots
**Progressive Unlocks**:
- **Castle Level 1**: 3 deck slots (1 battle deck, 1 building deck, 1 experimental)
- **Castle Level 5**: 5 slots (2 battle, 2 building, 1 flex)
- **Castle Level 10**: 7 slots (3 battle, 3 building, 1 flex)
- **Castle Level 20**: 9 slots (4 battle, 4 building, 1 flex)
- **Castle Level 25**: 10 slots (max: 5 battle, 5 building)

**VIP Bonus**: VIP 5 gets +2 extra slots (12 total)

### Deck Management UI
**Features**:
1. **Quick Switch**: Dropdown menu to switch active deck (1-click)
2. **Deck Templates**: Save deck compositions with names ("PvP Aggro", "PvE Farm", "Norse Theme")
3. **Copy Deck**: Duplicate existing deck as starting point for variations
4. **Import/Export**: Share deck codes with friends ("ST-DECK-ABC123")
5. **Auto-Complete**: AI suggests cards to fill empty slots based on theme/synergy
6. **Deck Comparison**: Side-by-side view of 2 decks (shows stat differences)
7. **Win Rate Tracking**: Display win/loss record per deck (data-driven optimization)
8. **Deck Tags**: Color-code and label decks (red = PvP, blue = PvE, green = Economy)

### Deck Building Constraints
**Battle Decks**:
- **Size**: 20-30 cards (smaller = faster cycling, larger = more options)
- **Hero Limit**: 1 legendary hero OR 2 epic heroes OR 3 rare heroes
- **Unit Limit**: Max 20 unit cards (stacks counted individually)
- **Tactic Limit**: Max 5 tactics (AI behavior slots)
- **Equipment Limit**: Max 10 equipment cards (attached to heroes)
- **Theme Bonus**: 20+ cards of same theme = synergy buff (see Section 2.3)

**Building Decks**:
- **Size**: 15-25 cards
- **Production Limit**: Max 10 production buildings (farms, mines, etc.)
- **Defense Limit**: Max 10 defense buildings (turrets, walls, etc.)
- **Special Limit**: Max 5 special buildings (wonders, teleports, etc.)
- **Terrain Matching**: Must have buildings for available terrain (e.g., don't bring fishing huts to desert map)

### Deck Validation
**Pre-Battle Checks**:
- **Minimum Size**: Battle deck must have ≥15 cards, building deck ≥10 cards
- **Illegal Cards**: Flag cards banned in current mode (e.g., OP cards banned in ranked)
- **Synergy Warnings**: Alert if deck has anti-synergies (e.g., fire + water units = neutral)
- **Missing Roles**: Warn if deck lacks tank, healer, or DPS (suggest adding)
- **Over-Budget**: Some modes have "deck cost" limits (total rarity points ≤100)

### Smart Deck Suggestions
**AI-Powered Recommendations**:
- **Meta Decks**: Copy top 100 player decks (with permission)
- **Counter Decks**: AI suggests decks to counter current PvP meta
- **Beginner Decks**: Pre-built starter decks for new players (Norse Aggro, Medieval Control)
- **Theme Optimizer**: Auto-fill to reach 20-card theme bonus
- **Budget Decks**: Builds using common/rare cards only (F2P friendly)

### Deck Sharing & Community
**Social Features**:
- **Deck Codes**: 12-character codes to share decks ("ST-DECK-ABC123")
- **Deck Library**: Browse community-submitted decks, filter by theme/mode/rating
- **Upvote/Downvote**: Rate decks (best decks rise to top)
- **Comments**: Discuss decks, suggest improvements
- **Deck Guides**: Write 500-word guides explaining deck strategy (formatting support)
- **Streamer Decks**: Featured decks from top streamers/pro players

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

### Elo Rating System

**Rating Tiers**:
- **Bronze** (0-999 Elo): Beginner tier, learning mechanics
- **Silver** (1000-1499): Intermediate, basic strategy mastery
- **Gold** (1500-1999): Advanced, meta awareness required
- **Platinum** (2000-2499): Expert, top 10% of players
- **Diamond** (2500-2999): Elite, top 3% of players
- **Master** (3000-3499): Pro-level, top 1%
- **Grandmaster** (3500+): Top 100 players globally

**Starting Elo**: New players begin at 1200 (Silver tier)

**Elo Calculation** (Standard chess formula with modifications):
- **Win**: +16 to +32 Elo (more for beating higher-rated opponent)
- **Loss**: -16 to -32 Elo (less for losing to higher-rated opponent)
- **Draw**: 0 Elo (rare in this game)
- **Formula**: `NewElo = OldElo + K * (ActualScore - ExpectedScore)`
  - `K = 32` for <30 games, `K = 24` for 30-100 games, `K = 16` for 100+ games
  - `ExpectedScore = 1 / (1 + 10^((OpponentElo - YourElo) / 400))`
  - `ActualScore = 1` for win, `0` for loss

**Example**:
- Player A (1500 Elo) vs Player B (1600 Elo)
- Expected: A has 36% win chance, B has 64% win chance
- If A wins: A gains +26 Elo (upset bonus), B loses -26 Elo
- If B wins: B gains +10 Elo (expected), A loses -10 Elo

**Rank Decay**:
- **Inactivity Penalty**: -10 Elo per day after 7 days of no ranked matches
- **Max Decay**: Down to tier minimum (e.g., Platinum can't decay below 2000)
- **Protection**: VIP 3+ has 14-day inactivity grace period (VIP 5: no decay)

### Matchmaking Queues

**Ranked Queue** (Elo-based):
- **Match Range**: ±150 Elo (tighter at high ranks: ±75 for Master+)
- **Queue Time**: Target <60 seconds, expand range after 2 minutes (+50 Elo per minute)
- **Best-of-3**: Optional Bo3 format for Diamond+ (more competitive)
- **Seasons**: 3-month ranked seasons, soft reset (Elo *= 0.75 + 300 at season end)
- **Rewards**: Season-end rewards based on peak Elo (not current)

**Casual Queue** (MMR-based, hidden rating):
- **Match Range**: ±300 MMR (wider for faster queues)
- **No Elo Change**: Win/loss doesn't affect ranked rating
- **Experimental Decks**: Safe space to test new strategies
- **Same Rewards**: Reduced rewards (50% of ranked gold/XP)

**Alliance Queue** (Guild Lobbies):
- **Premade Groups**: 2v2, 3v3, 5v5 alliance teams
- **Alliance Elo**: Separate rating for team play
- **Coordination**: Voice chat enabled, shared vision
- **Tournaments**: Weekly alliance tournaments with brackets

**Custom Lobbies** (Friend Matches):
- **Private Matches**: Invite-only, custom rules
- **Custom Rules**: Adjust HP (50%-200%), starting gold, deck cost limits
- **No Rewards**: Purely for fun, no XP/gold/Elo
- **Spectator Mode**: Friends can watch matches live (30-second delay to prevent cheating)

### Matchmaking Fairness

**Anti-Smurfing**:
- **Rapid Elo Gain**: New accounts that win >70% get accelerated Elo (+50 per win) until proper tier
- **Phone Verification**: Ranked requires verified phone number (1 account per number)
- **Behavioral Analysis**: Detect unnatural play patterns (e.g., intentionally losing to drop Elo)

**Prevent Exploits**:
- **Queue Dodging Penalty**: -10 Elo + 10-minute ban for leaving queue after match found
- **AFK Detection**: Auto-forfeit if no action for 60 seconds, -20 Elo penalty
- **Win Trading**: Ban both accounts if detected trading wins (manual review)

**VIP Matchmaking**:
- **Priority Queue**: VIP 2+ get 10-20% faster queue times (fill gaps in matches)
- **No Skill Advantage**: VIP players still matched by Elo (no pay-to-win matchmaking)
- **VIP-Only Queue**: Optional VIP 5 queue for whale-only matches (prestige)

### Seasonal Rewards

**End-of-Season Rewards** (based on peak Elo):
- **Bronze**: 500 gold, 1 rare pack, bronze border
- **Silver**: 1,000 gold, 2 rare packs, silver border
- **Gold**: 2,000 gold, 1 epic pack, gold border, exclusive card back
- **Platinum**: 5,000 gold, 2 epic packs, platinum border, exclusive avatar frame
- **Diamond**: 10,000 gold, 1 legendary pack, diamond border, exclusive legendary card skin
- **Master**: 25,000 gold, 3 legendary packs, master border, exclusive title ("Master Tactician")
- **Grandmaster**: 50,000 gold, 5 legendary packs, grandmaster border, name in Hall of Fame, developer shoutout

**Rank-Up Rewards** (instant rewards when reaching new tier):
- First time reaching Silver: 100 gems
- First time reaching Gold: 250 gems
- First time reaching Platinum: 500 gems + 1 legendary card
- First time reaching Diamond: 1,000 gems + exclusive skin
- First time reaching Master: 2,500 gems + eternal title

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

Sovereign Territories uses a modern, scalable tech stack: **Unity client** + **Nakama server** + **Docker deployment**. This architecture supports cross-platform play (mobile, PC, web) with real-time multiplayer and offline progression.

## 12.1 Technology Stack

### Client Side (Unity 2021+ LTS)
**Game Engine**: Unity 2021.3 LTS or newer
- **Rendering**: Universal Render Pipeline (URP) for mobile optimization
- **UI Framework**: Unity UI Toolkit (formerly UI Elements) for responsive design
- **Input**: New Input System for cross-platform control (touch, mouse, keyboard, gamepad)
- **Asset Management**: Addressables for dynamic loading/unloading (memory optimization)
- **Serialization**: JsonUtility for card data, battle logs, player state
- **Networking**: Nakama Unity SDK (WebSocket + REST)

**Supported Platforms**:
- **Mobile**: iOS 12+, Android 7.0+ (API 24)
- **PC**: Windows 10+, macOS 10.14+
- **Web**: WebGL 2.0 (Chrome, Firefox, Safari, Edge)

**Performance Targets**:
- **Mobile**: 60 FPS on iPhone 12 / Samsung S21, 30 FPS on iPhone 8
- **PC**: 144 FPS on mid-tier GPUs (GTX 1060, RTX 3050)
- **Memory**: <1GB RAM on mobile, <2GB on PC
- **Load Times**: <2 seconds for main menu, <5 seconds for battle

### Server Side (Nakama)
**Game Server**: Nakama 3.x (Go-based)
- **Database**: CockroachDB (distributed SQL for horizontal scaling)
- **Real-Time**: WebSocket for live multiplayer, chat, notifications
- **REST API**: HTTP/2 for matchmaking, leaderboards, IAP validation
- **Authentication**: Email, Google, Apple, Facebook, Steam login
- **Serverless Logic**: Go/Lua/TypeScript for custom game logic (match handlers, economy)

**Nakama Features Used**:
- **Matchmaking**: Skill-based matching (Elo), party system
- **Groups**: Alliance management, chat channels, leaderboards
- **Storage**: Player accounts, decks, inventory, progression
- **Leaderboards**: Global, alliance, seasonal rankings
- **Notifications**: Push notifications (Firebase Cloud Messaging)
- **In-App Purchases**: Receipt validation (Apple StoreKit, Google Play Billing)

**Deployment** (Docker Compose):
- **Containers**: Nakama server, CockroachDB, Redis (caching), Grafana (monitoring)
- **Orchestration**: Kubernetes for auto-scaling (handle 10,000+ concurrent players)
- **Regions**: US-East, US-West, EU-West, Asia-Pacific (low latency)
- **CDN**: Cloudflare for asset delivery (card images, audio files)

### Infrastructure
**Cloud Provider**: AWS (Amazon Web Services)
- **Compute**: EC2 instances (t3.medium for Nakama, m5.large for DB)
- **Storage**: S3 for assets (images, audio), RDS for backups
- **Load Balancing**: ALB (Application Load Balancer) for traffic distribution
- **Auto-Scaling**: Scale up to 50 Nakama instances during peak hours (Saturday evenings)
- **Backup**: Daily DB snapshots, 30-day retention

**Cost Estimation** (for 10,000 DAU):
- **Servers**: $500/month (Nakama + DB)
- **Storage**: $100/month (S3 + backups)
- **Bandwidth**: $200/month (CDN + data transfer)
- **Total**: ~$800/month (scales linearly with DAU)

## 12.2 WebSockets for Real-Time

**Connection Management**:
- **Persistent Connection**: Client maintains WebSocket for real-time updates
- **Reconnection**: Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s)
- **Heartbeat**: Ping every 30 seconds to keep connection alive (detect disconnects)
- **Session Tokens**: JWT tokens for authentication, refreshed every 24 hours

**Real-Time Features**:
- **Chat**: Instant message delivery (Global, Alliance, Whisper channels)
- **Battle Updates**: Turn-by-turn state sync (action → server validation → broadcast to opponent)
- **Notifications**: Alliance invites, trade offers, attack alerts
- **Live Events**: Real-time expedition rolls, alliance war updates
- **Matchmaking**: Queue status, match found notifications

**Message Protocol** (JSON over WebSocket):
```json
{
  "type": "battle_action",
  "battleId": "b123",
  "playerId": "p456",
  "action": "move",
  "unitId": "u789",
  "fromTile": [2, 3],
  "toTile": [3, 4],
  "timestamp": 1672531200
}
```

**Latency Optimization**:
- **Binary Protocol**: Consider Protocol Buffers for 30-50% size reduction (future)
- **Compression**: Gzip compression for messages >1KB
- **Batching**: Combine multiple actions into 1 message (reduce round-trips)
- **Client Prediction**: Show movement immediately, reconcile with server response

## 12.3 Offline Play & Sync

**Offline Modes**:
1. **PvE Campaign**: Playable fully offline (sync progress on reconnect)
2. **Deck Building**: Edit decks offline, sync on next login
3. **Collection View**: Browse cards offline (cached data)
4. **AFK Production**: Resources accumulate offline (capped at 8 hours)

**Data Persistence**:
- **Local Storage**: PlayerPrefs for settings, SQLite for card collection (Unity)
- **Cloud Save**: Nakama storage syncs to server every 5 minutes
- **Conflict Resolution**: Last-write-wins for non-critical data (deck edits), server-authoritative for economy (gold, cards)

**Sync Strategy**:
1. **On Login**: Download full player state (account, inventory, progression)
2. **Incremental Sync**: Upload actions queue (battles, card combines, purchases)
3. **Conflict Detection**: Server rejects actions with stale timestamps (>5 minutes old)
4. **Rollback**: If sync fails, show error and revert to last known good state

**Offline Limits**:
- **Max Offline Time**: 7 days (after that, force re-sync to prevent data drift)
- **Action Queue**: Max 100 queued actions (e.g., 100 PvE battles fought offline)
- **Storage Cap**: 50MB local cache (delete old assets to stay under limit)

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

# SECTION 17: ADDITIONAL FEATURES FOR COMPLETE GAMER EXPERIENCE

This section covers quality-of-life features, social enhancements, and engagement mechanics that elevate Sovereign Territories from a good game to a great one.

## 17.1 Achievements & Collections

### Achievement System
**Categories**:
1. **Combat Mastery**:
   - "First Blood": Win your first battle (10 gems)
   - "Centurion": Win 100 battles (100 gems)
   - "Warlord": Win 1,000 battles (500 gems + legendary card)
   - "Undefeated": Win 50 PvP matches without a loss (1,000 gems + title)

2. **Economy Tycoon**:
   - "Merchant": Sell 10 cards on auction house (50 gems)
   - "Mogul": Earn 1,000,000 gold lifetime (500 gems)
   - "Philanthropist": Donate 100,000 gold to alliance (250 gems + title)

3. **Card Collector**:
   - "Novice Collector": Own 50 unique cards (25 gems)
   - "Master Collector": Own 500 unique cards (500 gems)
   - "Complete Collection": Own all cards in one expansion (2,000 gems + exclusive border)

4. **Exploration**:
   - "World Traveler": Capture territories on all 4 map tiers (100 gems)
   - "Wonder Seeker": Capture 5 different wonders (250 gems)
   - "Conquistador": Control 100 territories simultaneously (500 gems)

5. **Social Butterfly**:
   - "Friendly": Add 10 friends (25 gems)
   - "Alliance Leader": Create and grow alliance to 50 members (500 gems)
   - "Diplomat": Form 3 alliances with other guilds (100 gems)

**Hidden Achievements** (surprise rewards):
- "Lucky Streak": Open 3 legendary cards in a row from packs (1,000 gems)
- "Giant Slayer": Defeat a VIP 5 player while being VIP 0 (500 gems + title)
- "Speedrunner": Win a battle in under 2 minutes (100 gems)

**Showcase**:
- Display achievements on profile page (badges, progress bars)
- Leaderboards for achievement points (competitive collection)
- Seasonal achievements (limited-time, rotate quarterly)

### Card Collection Tracking
**Collection Book**:
- Visual grid of all cards (owned, missing, duplicates)
- Filter by expansion, rarity, theme, type
- Stats: 342/500 cards owned (68% complete)
- Missing cards highlighted with "How to Obtain" hints

**Set Completion Bonuses**:
- Complete Norse set (50/50 cards): +10% frost damage for Norse decks
- Complete Medieval set: +5% gold from territories
- Complete Sci-Fi set: +10% energy recharge speed

## 17.2 Daily Login Calendar & Streaks

### Login Calendar
**Monthly Calendar** (30 days):
- Day 1-6: Common rewards (gold, energy, common packs)
- Day 7: Rare pack + 50 gems
- Day 14: Epic pack + 100 gems
- Day 21: Legendary pack + 250 gems
- Day 30: Mega reward (2 legendary packs + 500 gems + exclusive skin)

**Streak Bonuses**:
- 7-day streak: +10% XP for next week
- 14-day streak: +15% gold for next week
- 30-day streak: Permanent +5% bonus to all rewards (stacks monthly)
- 100-day streak: Eternal title "Devoted Sovereign" + 2,000 gems

### Comeback Rewards
**Lapsed Players** (gone >7 days):
- Welcome back pack (5 rare cards + 500 gold)
- 2x XP for next 7 days
- Free energy refill (100 energy)
- Personalized quest ("Complete 3 battles for 200 gems")

## 17.3 Referral & Invite System

### Friend Referral Program
**How It Works**:
1. Share referral code with friends (unique 8-character code: "ST-REF-ABC123")
2. Friend signs up and reaches Level 5
3. Both players get rewards

**Rewards**:
- **Referrer**: 100 gems per successful referral (max 10 referrals = 1,000 gems)
- **Referee**: 50 gems + starter pack (10 rare cards)
- **Milestone Bonuses**: 
  - 3 referrals: 1 epic card
  - 5 referrals: 1 legendary card + exclusive avatar frame
  - 10 referrals: VIP 1 status (free) + eternal title "Recruiter"

### Alliance Recruitment
**Guild Finder**:
- Browse alliances by size, activity, language, playstyle
- Filters: Casual, Competitive, PvE-focused, PvP-focused
- Apply to join (leaders approve/deny within 24 hours)
- Auto-join guilds (open recruitment, no approval needed)

**Recruitment Tools**:
- Alliance leaders post recruitment ads (text + banner image)
- "Looking for Group" channel in global chat
- Weekly spotlight: Featured alliances on main menu

## 17.4 Seasonal Events & Battle Pass

### Seasonal Battle Pass (3-month cycle)
**Free Track** (all players):
- 30 tiers of rewards (gold, energy, common/rare packs)
- Tier 30 reward: 1 epic card + 100 gems

**Premium Track** ($9.99 USD):
- 50 tiers of rewards (2x rewards per tier)
- Exclusive rewards: 3 legendary cards, 1,000 gems, exclusive skins
- Tier 50 reward: Mythic card (ultra-rare, 1 per season)

**Progression**:
- Earn XP from battles, quests, events (500 XP per tier)
- Casual players reach Tier 30 in ~6 weeks
- Hardcore players reach Tier 50 in ~4 weeks

**FOMO Factor**:
- Seasonal skins (never return, collector's items)
- Leaderboard for fastest battle pass completion (top 100 get bonus gems)

### Limited-Time Events (2-week cycles)
**Event Types**:
1. **Double XP Weekend**: 2x XP from all battles (Friday-Sunday)
2. **Gold Rush**: 2x gold from territories (7 days)
3. **Legendary Jackpot**: Legendary drop rate increased from 2% to 5% (3 days)
4. **Alliance War**: Server-wide alliance vs alliance battles (14 days)
5. **Themed Events**: Halloween (undead units +20% stats), Winter (frost damage +30%)

**Event Rewards**:
- Participation trophies (play 10 battles = 100 gems)
- Leaderboard prizes (top 100 = exclusive cards)
- Event-exclusive skins (time-limited, may return next year)

## 17.5 Spectator Mode & Replays

### Live Spectator Mode
**Watch Live Battles**:
- Friends can spectate your battles in real-time (30-second delay to prevent cheating)
- Alliance members can watch alliance war battles
- Public spectating for top 100 ranked players (streamer mode)

**Spectator UI**:
- View both players' perspectives (toggle between)
- See hidden information (both players' hands, tactics) after 30-second delay
- Chat with other spectators (whisper mode, doesn't disturb players)

### Replay System
**Save & Share Replays**:
- Auto-save last 10 battles
- Manually save favorite replays (max 50 saved)
- Share replay codes (12-character: "ST-REPLAY-XYZ789")
- Upload to community replay library (vote best replays)

**Replay Features**:
- Pause, rewind, fast-forward controls
- Camera angles (follow unit, bird's-eye, cinematic)
- Annotations (draw on screen, add text notes)
- Export to video (MP4, 720p/1080p) for YouTube/TikTok

**Content Creator Tools**:
- Streamer overlay (hide sensitive info, show QR code for donations)
- Highlight reel generator (AI picks best moments from battle)
- Tournament mode (bracket visualization, auto-commentary placeholders)

## 17.6 Guild vs Guild Features

### Alliance Warfare
**Territory Control**:
- Alliances declare war, fight for control of State/Global map territories
- Territory yields resources (gold, gems) to controlling alliance
- Shared treasury: Members contribute, leaders spend on buffs

**Guild Buffs**:
- **Economic**: +10% gold production for all members (costs 50,000 gold to activate, lasts 7 days)
- **Military**: +5% attack for all members (costs 100,000 gold, lasts 7 days)
- **Social**: +20% XP for all members (costs 75,000 gold, lasts 7 days)

**Guild vs Guild Tournaments**:
- Quarterly GvG brackets (top 32 alliances)
- Best-of-5 format (5 battles, most wins advance)
- Finals streamed on Twitch/YouTube with developer commentary
- Prizes: Exclusive legendary cards, alliance banners, eternal titles

### Alliance Leaderboards
**Rankings**:
1. **Power Ranking**: Total Elo of all members
2. **Economic Ranking**: Total gold earned by alliance
3. **Territory Control**: Number of territories held
4. **War Record**: Win/loss ratio in alliance wars

**Rewards** (monthly reset):
- Top 3 alliances: Exclusive legendary card for all members
- Top 10: 500 gems per member
- Top 50: Exclusive alliance banner skin

## 17.7 Customization & Personalization

### Player Profile
**Profile Elements**:
- Avatar (unlocked via achievements, VIP, events)
- Border/Frame (Bronze, Silver, Gold, Platinum, Diamond, Grandmaster)
- Title ("Master Tactician", "Undefeated", "Recruiter")
- Banner (background image, customizable)
- Stats showcase (win rate, total battles, territories controlled)

**Privacy Settings**:
- Hide profile (invisible to non-friends)
- Hide win/loss record (avoid toxicity)
- Anonymous mode (hide username in global chat)

### Card Cosmetics
**Alternate Art**:
- Unlock alternate card art via achievements, events, VIP
- Example: Thor (base art) vs Thor (animated lightning art)
- Same stats, different visuals (pay-for-look-and-feel)

**Card Backs**:
- Customize deck card backs (50+ designs)
- Seasonal card backs (Halloween pumpkins, Winter snowflakes)
- Prestige card backs (reach Grandmaster rank)

**Emotes & Taunts**:
- Pre-battle emotes ("Good luck!", "Prepare to lose!")
- Victory emotes (dance, fireworks, confetti)
- Unlock via achievements, VIP, or purchase (100 gems per emote)

## 17.8 Tutorial & New Player Experience

### Interactive Tutorial
**Phase 1: Basics** (5 minutes):
- Learn UI navigation (main menu, codex, deck builder)
- Build your first deck (pre-selected cards)
- Fight first battle (scripted AI, guaranteed win)

**Phase 2: Intermediate** (10 minutes):
- Unlock auction house, alliance system
- Build economy (place first buildings on map)
- Test auto-battle mode

**Phase 3: Advanced** (15 minutes):
- PvP tutorial (fight friendly AI mimic)
- Learn tactics system (program AI behavior)
- Castle leveling & skill trees

**Skip Option**: 
- Experienced players can skip tutorial (if played similar games)
- Claim tutorial rewards without playing (500 gold, 10 common cards, 50 gems)

### Guided Progression Path
**Suggested Quests**:
- "Reach Level 5 to unlock auction house" (200 gems)
- "Join an alliance for bonuses" (100 gems)
- "Build your first themed deck" (150 gems)
- "Win 10 PvE battles" (1 rare pack)

**Tooltips & Help**:
- Contextual tooltips (hover over element for explanation)
- Help button (opens wiki page for current screen)
- Video tutorials (30-second clips for complex features)

## 17.9 Community & Social Features

### Weekly Spotlight
**Featured Content**:
- Player of the Week (top Elo gainer, featured on main menu)
- Deck of the Week (community-voted best deck)
- Alliance of the Week (most active guild)

**Rewards for Featured**:
- 500 gems + exclusive title "Spotlighted"
- 7 days of fame (profile highlighted in-game)
- Developer interview (optional, posted on blog)

### Community Challenges
**Server-Wide Goals**:
- "Collectively win 1,000,000 battles this week" (all players contribute)
- Reward: All players get 1 legendary pack
- Creates camaraderie, encourages participation

### Forums & Discord Integration
**In-Game Forums**:
- Deck discussions, strategy guides, bug reports
- Upvote/downvote system (best posts rise to top)
- Developer responses (tagged "Official")

**Discord Integration**:
- Official Discord server (invite link in-game)
- Role sync (link account, get VIP roles in Discord)
- Bot commands (check stats, deck lookup via Discord)

## 17.10 Endgame & Prestige Systems

### Prestige Mode (Level 50+)
**Reset for Bonuses**:
- Reset castle to Level 1, keep all cards and progression
- Unlock prestige bonuses:
  - Prestige 1: +5% XP permanently
  - Prestige 2: +10% gold permanently
  - Prestige 3: +15% energy recharge speed permanently
- Prestige cosmetics (glowing avatar border, unique title)

### Infinite Scaling Content
**Endless PvE Tower**:
- 100-floor tower with escalating difficulty
- Each floor = battle with +10% enemy stats
- Rewards: Gems, cards, exclusive cosmetics (every 10 floors)
- Leaderboard for highest floor reached

**Mythic Raids** (for Level 40+ players):
- 10-player co-op battles against ultra-powerful bosses
- Weekly reset, limited attempts (3 per week)
- Rewards: Mythic cards (highest rarity, 0.1% drop rate)
- Requires deep coordination, voice chat recommended

# SECTION 18: IMMEDIATE NEXT STEPS (Technical)

This section outlines the **roadmap for Phase 1 (Prototype)** and actionable tasks for launching the Minimum Viable Product (MVP) within 3-6 months.

## 18.1 Development Phases

### Phase 1: Prototype (Months 1-2)
**Goal**: Playable core loop with 1 gameplay mode

**Milestones**:
1. **Week 1-2**: Set up development environment
   - Install Unity 2021.3 LTS, Nakama server, Docker
   - Configure GitHub repo, CI/CD pipeline (GitHub Actions)
   - Create project structure (folders: Assets/Scripts, Assets/Prefabs, Assets/Data)

2. **Week 3-4**: Implement card system
   - Create card data model (JSON Schema from `docs/specs/card-schema.json`)
   - Build card manager (CRUD operations: create, read, update, delete)
   - Design card UI (card display, stats visualization)
   - Implement pack opening system (gacha mechanics, pity timer)

3. **Week 5-6**: Implement battle system
   - Build 8x8 tactical grid (2D top-down view)
   - Implement turn-based combat (move, attack, abilities)
   - Add combat resolution (damage calculation, elemental interactions)
   - Create basic AI for PvE (random moves, target selection)

4. **Week 7-8**: Integrate Nakama server
   - Set up Nakama authentication (email login)
   - Implement player account storage (decks, inventory, progression)
   - Test real-time multiplayer (1v1 PvP battles)
   - Deploy to staging server (AWS EC2 instance)

**Deliverable**: Playable prototype with 20 cards, 1 PvE campaign (5 battles), 1v1 PvP mode

### Phase 2: Alpha (Months 3-4)
**Goal**: Expand content, add economy and social features

**Milestones**:
1. **Week 9-10**: Economy systems
   - Implement currencies (gold, gems, resources)
   - Build auction house (listing, bidding, escrow)
   - Add VIP system (tier unlocks, perks)
   - Create AFK production (building placement, offline rewards)

2. **Week 11-12**: Map hierarchy
   - Implement Tier 4 (8x8 local battles) - already done in Phase 1
   - Add Tier 3 (County Map with resource scrambles)
   - Design procedural map generation (random terrain, biomes)
   - Build territory control mechanics (capture, defend)

3. **Week 13-14**: Social features
   - Implement alliance system (create, join, chat)
   - Add friend system (add, gift, co-op battles)
   - Build global/alliance/whisper chat channels
   - Integrate matchmaking (Elo-based ranked queue)

4. **Week 15-16**: Polishing & testing
   - Balance card stats (playtests with 10-20 testers)
   - Fix bugs (focus on crash fixes, economy exploits)
   - Optimize performance (60 FPS on mobile target)
   - Prepare for closed beta

**Deliverable**: Alpha build with 100 cards, 3 map tiers, economy, alliances, matchmaking

### Phase 3: Beta (Months 5-6)
**Goal**: Content expansion, polish, and player testing

**Milestones**:
1. **Week 17-18**: Content creation
   - Add Saga Campaign (30 PvE battles with story)
   - Create Expedition board game mode
   - Design daily/weekly quests
   - Implement achievement system

2. **Week 19-20**: Advanced features
   - Build Tier 1-2 maps (State, Global)
   - Add alliance events (wars, tournaments)
   - Implement seasonal battle pass
   - Create spectator mode & replays

3. **Week 21-22**: Closed beta testing
   - Recruit 500-1000 beta testers (Discord, Reddit, forums)
   - Collect feedback (surveys, analytics, crash reports)
   - Balance adjustments based on data
   - Fix critical bugs

4. **Week 23-24**: Launch preparation
   - Finalize monetization (IAP pricing, VIP tiers)
   - Submit to App Store & Google Play (review process: 1-2 weeks)
   - Marketing campaign (trailer, social media, influencers)
   - Server load testing (simulate 10,000 CCU)

**Deliverable**: Beta build ready for soft launch (1-2 regions)

### Phase 4: Launch (Month 7+)
**Goal**: Public release and live operations

**Milestones**:
1. **Week 25**: Soft launch (Canada, Australia, Philippines)
   - Monitor metrics (retention, monetization, crashes)
   - A/B test features (pack pricing, VIP perks)
   - Iterate based on feedback

2. **Week 26-28**: Global launch
   - Release worldwide (iOS, Android, PC)
   - 24/7 customer support (in-game + email)
   - Live ops calendar (weekly events, daily quests)
   - First expansion announced (Storm Rising in 3 months)

3. **Ongoing**: Post-launch support
   - Bi-weekly balance patches
   - Monthly content updates (new cards, maps, events)
   - Quarterly expansions (50-100 cards each)
   - Community engagement (forums, Discord, social media)

## 18.2 Technical Tasks (Priority Order)

### High Priority (Must-Have for Prototype)
1. **Card Data Pipeline**:
   - Validate JSON schemas (ajv-cli)
   - Generate TypeScript types (json-schema-to-typescript)
   - Build card importer (Google Sheets → JSON)
   - Create card editor UI (Unity custom inspector)

2. **Battle System Core**:
   - Grid manager (8x8 tile system, pathfinding)
   - Unit controller (movement, attack, abilities)
   - Combat resolver (damage calculation, deterministic)
   - AI tactics (basic: random, medium: focus-healers, hard: optimal)

3. **Server Integration**:
   - Nakama authentication (email, OAuth)
   - Player storage (account, inventory, decks)
   - Matchmaking API (Elo-based queues)
   - Real-time battles (WebSocket sync)

### Medium Priority (Alpha Features)
4. **Economy Systems**:
   - Currency manager (gold, gems, resources)
   - Auction house backend (Nakama storage)
   - IAP integration (Unity IAP, receipt validation)
   - AFK production calculator

5. **Map Hierarchy**:
   - Procedural map generator (Perlin noise for terrain)
   - Territory control logic (capture, defend, ownership)
   - Building placement system (tile limits, synergies)

6. **Social Infrastructure**:
   - Alliance CRUD (create, join, leave, promote/demote)
   - Chat system (channels, filters, moderation)
   - Friend system (add, remove, gifting)

### Low Priority (Beta/Post-Launch)
7. **Content Creation Tools**:
   - Card balance analyzer (win rates, usage stats)
   - Event scheduler (in-game calendar, push notifications)
   - Localization pipeline (10+ languages)

8. **Polish & QoL**:
   - Tutorial system (interactive, skippable)
   - Achievements & collectibles
   - Spectator mode & replays
   - Battle pass progression

## 18.3 Team Structure

**Minimum Team** (5 people):
- **1 Game Designer**: Card balance, game systems, quests
- **2 Unity Engineers**: Client-side features, UI, gameplay
- **1 Backend Engineer**: Nakama server, API, database
- **1 Artist/UI Designer**: Card art, UI mockups, VFX

**Recommended Team** (10 people):
- Add: Project Manager, QA Tester, Marketing Lead, Community Manager, Sound Designer

## 18.4 Budget Estimate

**MVP Development** (6 months):
- **Team Salaries**: $150,000 (5 people × $5,000/month)
- **Server Costs**: $5,000 (staging + testing)
- **Software Licenses**: $5,000 (Unity Pro, Adobe CC, Git LFS)
- **Art Assets**: $10,000 (Asset Store, commissioned art)
- **Marketing**: $10,000 (trailer, ads, influencers)
- **Total**: ~$180,000

**Post-Launch** (per month):
- **Server**: $800-5,000 (scales with DAU)
- **Team**: $25,000+ (depends on team size)
- **Marketing**: $5,000-50,000 (user acquisition)

## 18.5 Success Metrics

**Prototype KPIs**:
- Playable from start to finish (5 battles without crashes)
- 10 internal playtesters complete tutorial
- Combat feels fair (balanced win rates)

**Alpha KPIs**:
- 100 beta testers, 40% D1 retention
- <2% crash rate
- Positive feedback (>7/10 average rating)

**Beta KPIs**:
- 1,000 beta testers, 30% D7 retention, 10% D30 retention
- 3% conversion rate (free → paying)
- $0.50 ARPU (average revenue per user)

**Launch KPIs**:
- 100,000 downloads in first month
- 40% D1, 20% D7, 10% D30 retention
- $1.00+ ARPU, 5% conversion rate
- Top 100 in Strategy category (App Store/Google Play)

