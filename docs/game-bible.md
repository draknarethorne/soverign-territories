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

Sovereign Territories uses a **6-tier rarity system** with distinct visual identities, star progression, and leveling mechanics. **Element determines frame color** (fire=red, water=blue, etc.), while **rarity determines frame complexity** (border ornateness, holographic effects, animations).

### Rarity Tiers Overview

**Visual Hierarchy**: Element defines **frame color**, Rarity defines **effects & complexity**

| Rarity | Star Range | Leveling | Drop Rate | Visual Identity |
|--------|------------|----------|-----------|-----------------|
| **Common** | 1★ (fixed) | Cannot level | 70% | Simple frame, matte finish, small badge |
| **Uncommon** | 1-2★ | +1 level max | 20% | Decorative corners, subtle glow, gem badge |
| **Rare** | 2-3★ | +1 level max | 8% | Ornate frame, holographic shimmer, animated badge |
| **Epic** | 3-4★ | +1 level max | 1.5% | Complex runes, particle glow, pulsing badge |
| **Legendary** | 5★ (fixed) | Cannot level* | 0.48% | Animated frame, radiant aura, crown badge |
| **Mythic** | 6★ (fixed) | Cannot level* | 0.02% | Ultra-ornate frame, screen glow, creature badge |

*Future: Epic/Legendary may gain +2 leveling (3-5★ / 5-7★) while maintaining rarity-based stat advantages

### Common - 1 Star

**Visual Design**:
- **Frame Color**: Determined by element (Fire=red, Water=blue, Earth=green, Lightning=yellow, Wind=cyan, Frost=light blue)
- **Frame Style**: Simple thin border with minimal decoration, matte finish
- **Background**: Light gradient of element color (fire = red-orange fade, water = blue-teal fade)
- **Star Display**: Single white star at bottom center of card
- **Rarity Indicator**: Small circular badge in top-right corner with "C" or dot pattern
- **Finish**: Matte, no special effects or shine

**Gameplay Characteristics**:
- **Starting Stars**: Always 1★ (cannot be increased)
- **Leveling**: **Cannot level up** (stays at base stats permanently)
- **Customization**: None (pure stat values, no skill points)
- **Use Case**: Fodder for combining, early-game units, bulk army stacks
- **Examples**: Basic Archer, Spearman, Scout, Farm (building), Mine (building)

**Why Commons Don't Level**:
- Simplicity for new players (no decision paralysis)
- Encourages progression to higher rarities
- Prevents common-only meta dominance
- Maintains economy value (always abundant supply for auction house)

### Uncommon - 1-2 Stars

**Visual Design**:
- **Frame Color**: Determined by element (same color family as Common)
- **Frame Style**: Medium border with decorative corners, subtle embossed patterns
- **Background**: Richer gradient of element color with slight texture (fire = flame wisps, water = ripples)
- **Star Display**: 1-2 white stars at bottom, unfilled slots show as dim outlines
- **Rarity Indicator**: Hexagonal gem badge in top-right corner with soft glow animation
- **Finish**: Semi-gloss with faint shimmer overlay

**Gameplay Characteristics**:
- **Starting Stars**: 1★ by default
- **Leveling**: Can level up to **2★** (one level upgrade)
  - Requires: Combine with duplicate OR spend resources (1,000 gold + 50 XP)
  - Stat Boost: +25% to all base stats at 2★
- **Customization**: Minor (choose 1 of 2 passive bonuses when leveling to 2★)
  - Example: Fire Warrior → choose "+10% attack" OR "+10% HP"
- **Use Case**: Early-to-mid game core units, niche specialists
- **Examples**: Elite Archer, Heavy Infantry, Healer, Barracks (building)

**Leveling Process**:
1. Obtain duplicate Uncommon card (from pack, quest, or auction)
2. In Codex, select "Combine for Stars" option
3. Card upgrades from 1★ to 2★, visual star fills in with green glow animation
4. Choose 1 passive bonus from 2 options (decision is permanent)

### Rare - 2-3 Stars

**Visual Design**:
- **Frame Color**: Determined by element with metallic sheen added
- **Frame Style**: Ornate border with geometric patterns, beveled edges, crystal accents
- **Background**: Deep gradient of element color with animated subtle effects (fire = flowing embers, water = wave shimmer)
- **Star Display**: 2-3 white stars with element-colored glow around them
- **Rarity Indicator**: Crystalline gem badge with slow rotation animation and inner light
- **Finish**: Glossy holographic overlay with rainbow shimmer at angles

**Gameplay Characteristics**:
- **Starting Stars**: 2★ by default
- **Leveling**: Can level up to **3★** (one level upgrade)
  - Requires: Combine 2 duplicates OR spend 5,000 gold + 200 XP
  - Stat Boost: +40% to all base stats at 3★
- **Customization**: Moderate (allocate 3 skill points across 3 stats when leveling)
  - Example: At 3★, distribute +3 points across Attack/Defense/HP (e.g., +2 Attack, +1 HP)
- **Use Case**: Mid-game powerhouses, strategic deck staples
- **Examples**: Dragon Knight, Archmage, Siege Engine, Turret (building), Granary (building)

**Skill Point Allocation**:
- **3 Points Total** to distribute at 3★
- **Options**: Attack, Defense, HP, Speed, Range (depending on card type)
- **Limits**: Max 2 points in any single stat (prevents min-maxing)
- **Respec**: Costs 100 gems to reset allocation (once per month free)

### Epic - 3-4 Stars

**Visual Design**:
- **Frame Color**: Determined by element with rich metallic finish and color depth
- **Frame Style**: Highly ornate border with intricate patterns, mystical runes matching element theme
- **Background**: Vibrant element gradient with animated energy particles (fire = floating embers, lightning = crackling arcs)
- **Star Display**: 3-4 white stars with strong element-colored aura and pulse effect
- **Rarity Indicator**: Large ornate gem badge with pulsing energy rings and particle effects
- **Finish**: Premium holographic with prismatic rainbow and parallax depth effect
- **Special**: Faint element-themed particle effects around entire card border

**Gameplay Characteristics**:
- **Starting Stars**: 3★ by default
- **Leveling**: Can level up to **4★** (one level upgrade)
  - Requires: Combine 3 duplicates OR spend 20,000 gold + 1,000 XP
  - Stat Boost: +60% to all base stats at 4★
- **Customization**: High (skill tree with 5 nodes, unlock 3 at 4★)
  - Example: "Thor" at 4★ → unlock 3 of 5 abilities: [Chain Lightning, Thunder Shield, Rage Mode, Mjolnir Throw, Storm Call]
- **Use Case**: Late-game specialists, named heroes, powerful buildings
- **Examples**: Thor, Merlin, Odin, Fortress (building), Wonder Monument (building)

**Skill Tree System**:
- **5 Total Nodes** per Epic card (unique to each card)
- **3 Unlockable** at 4★ (choose wisely, permanent)
- **Synergies**: Some nodes combo with others (e.g., "Chain Lightning" + "Storm Call" = extended chain range)
- **Visual Feedback**: Unlocked abilities show glowing nodes on card art

### Legendary - 5 Stars

**Visual Design**:
- **Frame Color**: Determined by element with radiant metallic sheen and golden highlights
- **Frame Style**: Ultra-ornate animated border with flowing energy matching element (fire = flame trails, water = liquid gold flows)
- **Background**: Rich element gradient with radiant aura and animated environment effects
- **Star Display**: 5 white stars in arc formation with intense element-colored glow and rhythmic pulse
- **Rarity Indicator**: Majestic crown or phoenix badge with animated light rays and rotation
- **Finish**: Premium animated holographic with 3D parallax depth and element-specific shine
- **Special**: Border animates with element energy flow, subtle screen glow when hovered

**Gameplay Characteristics**:
- **Starting Stars**: 5★ by default (max stars)
- **Leveling**: **Cannot level** (already at peak power, balanced for fairness)
- **Customization**: Maximum (full skill tree with 10 nodes, all unlockable over time)
  - Unlock progression: 2 nodes at acquisition, +1 node per 500 hero XP (earned in battles)
  - Example: "Ragnarok Thor" → unlock all 10 abilities eventually: [Chain Lightning III, Thunder Shield II, Rage Mode, Mjolnir Throw, Storm Call, Lightning Strike, Thor's Fury, Berserker, Immortal Wrath, Godly Presence]
- **Equipment Slots**: 3 slots (weapon, armor, accessory)
- **Use Case**: Endgame heroes, win conditions, status symbols
- **Examples**: Ragnarok Thor, Merlin the Eternal, Gaia Prime, Emperor's Castle (building)

**Why Legendaries Don't Level**:
- **Balance**: All Legendary cards equal at 5★ prevents power creep
- **Fairness**: Free and paying players both get 5★ legendaries (no advantage)
- **Skill Tree Progression**: Unlocking 10 nodes provides progression without star inflation
- **Collectibility**: 5★ rarity maintains prestige ("I have the same Thor as the pros")

### Mythic - 6 Stars

**Visual Design**:
- **Frame Color**: Determined by element with transcendent iridescent sheen and cosmic highlights
- **Frame Style**: Impossibly ornate animated border with living element energy (fire = sentient flames, water = cascading torrents)
- **Background**: Hyper-saturated element gradient with reality-warping effects and animated cosmic particles
- **Star Display**: 6 white stars in hexagon formation, slowly rotating with element-colored energy trails
- **Rarity Indicator**: Mythical creature badge (dragon, phoenix, leviathan) matching element with full animation
- **Finish**: Ultimate holographic with screen-wide subtle glow effect (accessibility-friendly dimming option)
- **Special**: Card pulses with element energy, screen border glows element color when in hand, deploy animation has screen flash

**Gameplay Characteristics**:
- **Starting Stars**: 6★ by default (beyond legendary)
- **Leveling**: **Cannot level** (already transcendent)
- **Customization**: Ultimate (12-node skill tree + 5 equipment slots)
  - All nodes unlockable, but requires 10,000 hero XP total (months of play)
  - Example: "Primordial Chaos" → 12 reality-bending abilities
- **Equipment Slots**: 5 slots (weapon, armor, accessory, relic, artifact)
- **Use Case**: Ultra-rare seasonal rewards, tournament prizes, whale targets
- **Drop Rate**: 0.02% (1 in 5,000 packs), pity timer at 500 packs
- **Examples**: Primordial Chaos, The World Serpent, Infinity Nexus (building)

**Mythic Acquisition**:
- **Battle Pass**: Tier 50 reward (1 random Mythic per season)
- **Grand Tournaments**: Top 100 global PvP players per season
- **Seasonal Events**: Complete 50-stage endgame challenge
- **Packs**: 0.02% drop rate with 500-pack pity timer (not recommended)
- **Auction House**: Tradeable, but expect 1,000,000+ gold prices

**Balance Consideration**:
- **Power Level**: Mythics are ~20% stronger than Legendaries in perfect conditions
- **Situational**: Require specific deck synergies to reach full potential
- **Not Auto-Win**: Skilled players with Legendary decks can beat Mythic decks
- **Flex Factor**: Primarily for collectors and whales (prestige > power)

---

## Visual Design System: Elements + Rarities

### Core Philosophy (Pokemon-Style Approach)

**Element Drives Frame Color** - Just like Pokemon TCG where Fire cards are red, Water are blue, and Grass are green, element determines the primary visual identity.

**Rarity Drives Complexity & Effects** - Border ornateness, holographic quality, animation, and badge sophistication increase with rarity.

**Stars Show Progression** - Simple white stars (with element-colored glow) at bottom indicate current power level.

### 3-Way Visual System

**1. Element (Primary Frame Color & Theme)**

Element determines the **color palette and thematic motifs** for every card:

| Element | Frame Color | Background | Motifs |
|---------|-------------|------------|--------|
| **Fire** | Red-Orange | Warm red gradients | Flames, embers, lava cracks |
| **Water** | Blue | Cool blue gradients | Waves, ripples, bubbles |
| **Earth** | Brown-Green | Natural earth tones | Vines, stone, crystals |
| **Lightning** | Yellow-Purple | Electric gradients | Arcs, sparks, storm clouds |
| **Wind** | Cyan-White | Airy light tones | Swirls, clouds, feathers |
| **Frost** | Light Blue-White | Icy gradients | Snowflakes, ice shards, aurora |

**Why Element = Color**:
- **Instant Recognition**: Players identify card type at a glance (critical in fast gameplay)
- **Collection Organization**: Fire deck looks cohesive, all red-orange frames together
- **Deckbuilding UX**: Easier to spot element mismatches when building mono-element decks
- **Proven Model**: Pokemon's success validates element-driven color scheme

**2. Rarity (Border Complexity & Visual Effects)**

Rarity determines **how fancy the frame is** and **what special effects** appear:

| Rarity | Frame Complexity | Holographic | Animation | Badge |
|--------|------------------|-------------|-----------|-------|
| **Common** | Thin simple border | None | None | Small dot |
| **Uncommon** | Medium decorative | Faint shimmer | None | Gem (static) |
| **Rare** | Ornate geometric | Rainbow holo | Subtle | Gem (rotating) |
| **Epic** | Intricate runes | Prismatic | Particles | Large (pulsing) |
| **Legendary** | Ultra-ornate | Premium holo | Full border | Crown (animated) |
| **Mythic** | Transcendent | Screen glow | Everything | Creature (living) |

**Progressive Complexity**:
- **Common**: Bare minimum - clean and readable
- **Uncommon**: Slight flair - corner decorations, subtle texture
- **Rare**: Obviously special - beveled edges, crystal accents, holo shine
- **Epic**: Premium feel - animated particles, deep frame detail
- **Legendary**: Jaw-dropping - flowing energy, 3D depth, radiant glow
- **Mythic**: Impossible - reality-bending effects, screen presence

**3. Stars (Progression Level)**

Stars show **current power level** within the rarity tier:

- **Color**: White stars with element-colored glow/aura (fire card = white stars with red glow)
- **Position**: Bottom center of card in horizontal row or arc
- **Unfilled Slots**: Dim outline shows max potential (e.g., 1★ Uncommon shows 2 slots, 1 filled, 1 outline)
- **Animation**: Stars pulse softly with element energy at Rare+ rarities

### Card Anatomy (Visual Breakdown)

```
┌─────────────────────────────────┐
│ [Badge]               [Element] │ ← Top: Rarity badge (left), Element icon (right)
│                                 │
│                                 │
│         [Card Art]              │ ← Center: Illustration with element-colored background
│                                 │
│                                 │
├─────────────────────────────────┤
│  [Name]              [Cost]     │ ← Name bar with element-colored background
├─────────────────────────────────┤
│                                 │
│     [Stats & Abilities]         │ ← Text box with element-tinted background
│                                 │
├─────────────────────────────────┤
│        ★ ★ ★ ☆ ☆               │ ← Bottom: Star progression (white stars, element glow)
└─────────────────────────────────┘
  ↑ Frame border color = Element
  ↑ Frame complexity = Rarity
```

### Visual Examples (Element + Rarity Combos)

**Fire Element Common Archer (1★)**:
- **Frame**: Thin red-orange border, matte finish
- **Background**: Light red gradient with subtle flame texture
- **Stars**: 1 white star at bottom (no glow on commons)
- **Badge**: Small circular dot in top-right
- **Effect**: None
- **Overall Feel**: Simple, clean, clearly Fire-type

**Water Element Rare Mage (2★)**:
- **Frame**: Ornate blue border with wave patterns, beveled edges
- **Background**: Deep blue gradient with animated ripple effect
- **Stars**: 2 white stars with blue glow, 1 dim outline showing 3★ potential
- **Badge**: Crystalline gem badge with slow rotation
- **Effect**: Rainbow holographic shimmer overlay
- **Overall Feel**: Premium, clearly Water-type, obviously Rare quality

**Lightning Element Legendary Thor (5★)**:
- **Frame**: Ultra-ornate yellow-purple border with flowing electric energy animation
- **Background**: Vibrant electric gradient with crackling arcs and storm clouds
- **Stars**: 5 white stars in arc with intense yellow-purple glow and pulse
- **Badge**: Majestic crown with animated light rays
- **Effect**: Premium holographic + 3D parallax + border energy flow + screen glow on hover
- **Overall Feel**: Jaw-dropping, unmistakably Lightning-type, obviously Legendary

**Earth Element Mythic Gaia (6★)**:
- **Frame**: Impossibly ornate brown-green border with living vines and crystal growths
- **Background**: Hyper-saturated earth gradient with cosmic particles and reality-warp
- **Stars**: 6 white stars in hexagon rotating with green-brown energy trails
- **Badge**: Animated dragon/tree-spirit creature with breathing animation
- **Effect**: Ultimate holographic + screen glow + element energy pulse + deploy screen flash
- **Overall Feel**: Transcendent, clearly Earth-type, unmistakably Mythic rarity

### Design Benefits of This System

**1. Clarity**: Element color = instant card type recognition (fire deck is all red frames)
**2. Collectibility**: Rarity effects make opening packs exciting (holo shimmer = rare!)
**3. Progression**: Stars show power within rarity (my 3★ Rare beats your 2★ Rare)
**4. Cohesion**: Fire cards look like a family (same color, different complexity levels)
**5. Proven**: Matches Pokemon/Magic Arena success model (element = color, rarity = foil/effects)
**6. Accessibility**: Colorblind players can identify rarity by border complexity even if color is hard to see
**7. Future-Proof**: Easy to add new elements (just assign new color) or rarities (add new effect tier)

---

## Card Leveling and Combining System

### Leveling Mechanics by Rarity

**Common (1★ Fixed)**:
- ❌ **Cannot level up**
- **Why**: Keeps commons accessible and prevents common-only meta
- **Alternative**: Combine multiples into higher-rarity cards (future feature)

**Uncommon (1★ → 2★)**:
- ✅ **Can level once** (1★ to 2★)
- **Method 1**: Combine with 1 duplicate Uncommon
- **Method 2**: Spend 1,000 gold + 50 XP
- **Stat Boost**: +25% to all stats
- **Customization**: Choose 1 of 2 passive bonuses

**Rare (2★ → 3★)**:
- ✅ **Can level once** (2★ to 3★)
- **Method 1**: Combine with 2 duplicate Rares
- **Method 2**: Spend 5,000 gold + 200 XP
- **Stat Boost**: +40% to all stats
- **Customization**: Allocate 3 skill points across stats

**Epic (3★ → 4★)**:
- ✅ **Can level once** (3★ to 4★)
- **Method 1**: Combine with 3 duplicate Epics
- **Method 2**: Spend 20,000 gold + 1,000 XP
- **Stat Boost**: +60% to all stats
- **Customization**: Unlock 3 of 5 skill tree nodes

**Legendary (5★ Fixed)**:
- ❌ **Cannot level up** (already max stars)
- **Progression**: Unlock skill tree nodes via hero XP (earned in battles)
- **Equipment**: Attach 3 equipment cards for stat boosts

**Mythic (6★ Fixed)**:
- ❌ **Cannot level up** (transcendent)
- **Progression**: Unlock 12-node skill tree via hero XP
- **Equipment**: Attach 5 equipment cards

### Combining Process (Step-by-Step)

**Example: Leveling an Uncommon from 1★ to 2★**

1. **Open Codex**: Navigate to card collection view
2. **Select Card**: Click on your 1★ Uncommon "Elite Archer"
3. **Choose Method**:
   - Option A: "Combine with Duplicate" (requires 1 more Elite Archer in inventory)
   - Option B: "Level with Resources" (costs 1,000 gold + 50 XP)
4. **Confirm**: Animation shows stars merging, second star fills in with green glow
5. **Customization**: Choose passive bonus:
   - "+10% Attack" OR "+10% HP" (permanent decision)
6. **Result**: Elite Archer is now 2★ with +25% stats and chosen bonus

**Splitting Cards (Reverse Process)**:
- **Cost**: 100 Sovereign Tokens (rare currency) OR 500 gems
- **Function**: Split a leveled card back to base stars + return duplicate(s)
- **Example**: Split 2★ Uncommon → get 1★ Uncommon + 1★ Uncommon duplicate
- **Use Case**: Redistribute resources, sell duplicates, undo mistakes
- **Limitation**: Lose chosen passive bonus (resets to base)

---

## Shiny Variants (Collectible Cosmetics)

### What Are Shinies?

**Shiny cards** are **cosmetic-only variants** of existing cards with alternate art, special animations, and enhanced visual effects. They have **identical stats** to normal versions but are extremely rare and collectible.

**Visual Differences**:
- **Alternate Art**: Completely different illustration (e.g., normal Thor = classic armor, shiny Thor = modern tactical gear)
- **Holographic Effect**: Prismatic rainbow shimmer overlays entire card
- **Animated Background**: Living elements (flames move, water flows, lightning crackles)
- **Particle Effects**: Sparkles, light trails, or elemental particles around card
- **Shiny Badge**: Small star icon with "SHINY" text in corner (doesn't replace rarity badge)

**Example Comparisons**:
- **Normal Fire Archer**: Static fire background, simple arrow sprite
- **Shiny Fire Archer**: Animated flames, archer sprite has glowing eyes, arrows leave trails

### Shiny Rarity & Drop Rates

**Any card can be shiny** (Common to Mythic), with **utility bonuses for collectors**:

### Shiny Drop Rates (Pack Type Dependent)

**Standard Packs** (Earned through play):
- **Shiny Chance**: 1% per card (same as current system)
- **F2P Accessible**: ~1 shiny every 100 cards (20 packs)
- **Pity System**: Guaranteed shiny after 100 packs

**Premium Packs** (Purchased with gems/money):
- **Shiny Chance**: 10% per card (10× higher than standard)
- **Whale Appeal**: ~1 shiny every 10 cards (2 packs)
- **Pity System**: Guaranteed Rare+ shiny after 20 premium packs

**Pack Type Examples**:
| Pack Type | Cost | Shiny Rate | Avg Shinies/Pack | F2P Access |
|-----------|------|------------|------------------|------------|
| **Standard Pack** | 1,000 Gold | 1% | 0.05 (1 per 20 packs) | ✅ Daily quests |
| **Element Booster** | 1,500 Gold | 1% | 0.05 | ✅ Campaign rewards |
| **Premium Standard** | 100 Gems ($0.99) | 10% | 0.5 (1 per 2 packs) | ❌ Gem purchase only |
| **Premium Element** | 150 Gems ($1.49) | 10% | 0.5 | ❌ Gem purchase only |
| **Epic Booster** | 3,000 Gold | 1% | 0.05 | ✅ Weekly quests |
| **Premium Epic** | 300 Gems ($2.99) | 10% | 0.5 | ❌ Gem purchase only |
| **Shiny Guaranteed** | 1,000 Gems ($9.99) | 100% | 1.0 (always 1 shiny) | ❌ Special events |

**Rarity Distribution** (Within Shiny Drops):
- Common Shiny: 60% (if shiny procs, 60% chance it's Common)
- Uncommon Shiny: 25%
- Rare Shiny: 12%
- Epic Shiny: 2.5%
- Legendary Shiny: 0.5%
- Mythic Shiny: 0.001% (ultra-rare, special events only)

### Shiny Utility System (Collector Advantage)

**Map Deployment Bonuses**:
Shinies provide **5% production/combat bonuses** when deployed on County/State maps:

**Economy Buildings** (Deployed on resource nodes):
- **Normal Mine**: +100 Gold/hour
- **Shiny Mine**: +105 Gold/hour (5% production boost)
- **Stacking**: 2 Shiny economy cards on same territory = +10% total (cumulative)

**Battle Units** (Deployed in formations):
- **Normal Knight**: 30 Attack, 40 Defense
- **Shiny Knight**: 31 Attack, 42 Defense (rounded up, 5% boost)
- **Stacking**: All-shiny formation (5 shinies) = +25% stats (powerful but rare)

**Visual Indicators**:
- **Battle Map**: Shiny units have golden aura, particle trail
- **County Map**: Shiny buildings have animated gold shimmer
- **Codex**: Shiny cards have holographic border, star icon

**Why This Works**:
- ✅ **Collector Value**: Shinies aren't just cosmetic (5% edge)
- ✅ **Not Pay-to-Win**: 5% boost ≠ game-breaking (skill still matters)
- ✅ **Whale Appeal**: All-shiny deck = flex + slight edge
- ✅ **F2P Competitive**: Normal cards 95% as good (no paywalls)
- ✅ **Stacking Incentive**: Collect multiple shinies for bigger bonuses

### Shiny Pity System (Anti-Frustration)

**Pity Counters** (Separate for Standard vs Premium Packs):

**Standard Pack Pity** (F2P Accessible):
1. **Any Shiny**: Guaranteed shiny after **100 packs** without shiny
   - Rarity: 60% Common, 25% Uncommon, 12% Rare, 2.5% Epic, 0.5% Legendary
2. **Rare+ Shiny**: Guaranteed Rare/Epic/Legendary shiny after **500 packs**
   - Distribution: 80% Rare, 18% Epic, 2% Legendary

**Premium Pack Pity** (Gem Purchase):
1. **Any Shiny**: Guaranteed shiny after **20 packs** without shiny (5× faster)
2. **Rare+ Shiny**: Guaranteed Rare/Epic/Legendary shiny after **50 packs**

**Mythic Shiny** (No Pity):
- **Ultra-Exclusive**: No pity timer, 0.001% drop rate
- **Acquisition**: Special events, tournament rewards, 500k+ packs (theoretical)

### Shiny Acquisition Methods

**Primary Sources** (All Players):
1. **Pack Openings**: 
   - Standard Packs: 1% shiny rate (F2P accessible)
   - Premium Packs: 10% shiny rate (gem purchase)
2. **Seasonal Events**: "Shiny Week" - 2× shiny drop rates for 7 days
3. **Battle Pass**: Tier 40 reward = 1 guaranteed Rare+ shiny (free track)
4. **Daily Login Rewards**: Day 28 = Choose 1 Legendary (option to select shiny variant)
5. **Campaign Milestones**: Complete State Map = 1 random Rare+ shiny

**Secondary Sources** (Whale/Grind):
6. **Shiny Guaranteed Pack**: 1,000 gems ($9.99) = 1 guaranteed shiny (random rarity)
7. **Auction House**: Players can trade shinies (expect 10× normal card price)
8. **Crafting**: Combine 10 normal versions → 1 shiny version (costly but deterministic)
9. **VIP Bonuses**: VIP 5 gets +1% shiny rate in all packs (2% Standard, 11% Premium)

### Weekly Purchase Limits (Anti-Whale-Blitz)

**Purpose**: Prevent whales from "buying 1,000 packs day 1" and dominating instantly.

**Weekly Shop Caps** (Resets every Monday 00:00 UTC):

**Gold Purchases** (Unlimited):
- ✅ **Standard Packs**: Unlimited (1,000 gold each)
- ✅ **Element Boosters**: Unlimited (1,500 gold each)
- ✅ **Epic Boosters**: Unlimited (3,000 gold each)
- **Why Unlimited**: Gold is earned through play (prevents F2P frustration)

**Gem Purchases** (Weekly Limits):
| Pack Type | Cost | Weekly Limit | Rationale |
|-----------|------|--------------|-----------|
| **Premium Standard Pack** | 100 Gems | 10/week | Prevents infinite shiny farming |
| **Premium Element Booster** | 150 Gems | 5/week | Limits element-specific shinies |
| **Premium Epic Booster** | 300 Gems | 3/week | Prevents Epic spam |
| **Shiny Guaranteed Pack** | 1,000 Gems | 1/week | Ultra-premium (1 guaranteed shiny) |
| **Game Deck** | 2,000 Gems | 1/week | Prevents instant 300-card collection |

**Real Money Purchases** (Weekly Limits):
| Item | Price | Weekly Limit | Rationale |
|------|-------|--------------|-----------|
| **5-Pack Bundle** | $4.99 | 5/week | Max 25 Standard Packs/week ($24.95) |
| **Premium 5-Pack Bundle** | $9.99 | 3/week | Max 15 Premium Packs/week ($29.97) |
| **Game Deck** | $19.99 | 1/week | Max 1 Game Deck/week (50 cards) |
| **Battle Pass** | $4.99 | 1/month | Monthly subscription (not weekly) |

**Total Whale Spending Cap** (Week 1):
- 10 Premium Standard Packs: 1,000 Gems ($9.90)
- 5 Premium Element Boosters: 750 Gems ($7.50)
- 3 Premium Epic Boosters: 900 Gems ($9.00)
- 1 Shiny Guaranteed Pack: 1,000 Gems ($9.99)
- 1 Game Deck: 2,000 Gems ($19.99)
- 5× 5-Pack Bundles: $24.95
- 3× Premium 5-Pack Bundles: $29.97
- 1× Game Deck direct: $19.99
- 1× Battle Pass: $4.99
- **Total Max Spend**: ~$136/week

**Weekly Limit UI**:
```
[Pack Shop - Premium Standard Pack]
Cost: 100 Gems
Weekly Limit: 7/10 remaining

[Purchase] [Purchase 5] [Purchase 10 (Max)]

Limit resets in: 3 days, 14 hours
```

**Why Weekly Limits Work**:
- ✅ **Prevents Day 1 Stomp**: Whale can't buy 1,000 packs instantly (max ~100/week)
- ✅ **Sustains Revenue**: Whales spend every week (recurring income)
- ✅ **F2P Fairness**: Whale gets 100 packs/week, F2P gets 10 packs/week (10× gap, not 1000×)
- ✅ **Progression Pacing**: Even whales take months to collect all shinies
- ✅ **Event FOMO**: "Shiny Week" doubles value (encourages weekly engagement)

### Shiny Balance Philosophy

**Why Shinies Have Utility (5% Bonus)**:
- **Collector Reward**: Shinies feel special beyond just visuals
- **Whale Justification**: Spending $100/week has tangible benefit (5% edge)
- **Not Pay-to-Win**: 5% boost ≠ game-breaking (Normal Knight: 30 Attack, Shiny Knight: 31 Attack)
- **Skill > Spending**: Good player with normal cards beats bad player with shinies
- **F2P Accessible**: 1% drop rate in free packs (patience rewarded)

**Why Premium Packs Exist (10× Shiny Rate)**:
- **Whale Appeal**: $10 for 2 Premium Packs = ~1 shiny (predictable value)
- **Time vs Money**: F2P grinds 100 packs for shiny, whale buys 10 packs ($50)
- **Not Exclusive**: F2P can still get shinies (just slower)
- **Weekly Limits**: Even whales can't buy infinite shinies (10 Premium Packs/week max)

**Why Weekly Caps Matter**:
- **Prevents Power Spike**: No "buy 1,000 packs, dominate PvP day 1"
- **Sustains Engagement**: Whales return every week to hit cap (retention)
- **F2P Competitive**: 10× spending gap (not 1000×) keeps matches fair
- **Trading Economy**: Limits on new shinies entering market (auction house value stable)

**Preventing Shiny Inflation**:
- **No Gameplay Advantage**: Shinies = normal cards (same stats, same abilities)
- **Low Drop Rates**: Even with pity, takes months to collect multiple shinies
- **No Shiny-Only Rewards**: Can't lock content behind "must have shiny" walls
- **Dust System** (Future): Convert excess shinies to currency for targeted shiny crafting

### Shiny Showcase Features

**Profile Display**:
- **Shiny Showcase Tab**: Display up to 5 favorite shinies on profile
- **Shiny Counter**: "23/500 Shinies Collected" badge
- **Shiny Leaderboard**: Global ranking for most shinies owned (whale competition)

**In-Battle VFX**:
- **Entrance Animation**: Shiny cards have special deploy animations (sparkles, screen flash)
- **Glow Effect**: Shiny units on battlefield have subtle aura (doesn't obstruct gameplay)
- **Victory Poses**: Shiny heroes have unique victory animations

**Social Bragging**:
- **Chat Links**: Share shiny card in alliance chat (clickable card preview)
- **Shiny Trading**: Whisper trade offers for specific shinies
- **Flex Emotes**: "Look at my shiny!" emote for BM (bad manners) post-victory

---

### Summary Table: Full Rarity System

| Rarity | Stars | Leveling | Drop % | Shiny % | Visual Effects (Frame Complexity) |
|--------|-------|----------|--------|---------|-----------------------------------|
| Common | 1★ | ❌ None | 70% | 0.7% | Simple, matte (element-colored) |
| Uncommon | 1-2★ | ✅ +1 | 20% | 0.2% | Decorative, subtle glow (element-colored) |
| Rare | 2-3★ | ✅ +1 | 8% | 0.08% | Ornate, holographic (element-colored) |
| Epic | 3-4★ | ✅ +1* | 1.5% | 0.015% | Complex runes, particles (element-colored) |
| Legendary | 5★ | ❌ None* | 0.48% | 0.0048% | Animated, radiant (element-colored) |
| Mythic | 6★ | ❌ None | 0.02% | 0.0002% | Ultra-ornate, screen glow (element-colored) |

*Future expansion: Epic 3-5★ (+2 leveling), Legendary 5-7★ (+2 leveling)

**Key Design Principle**: Element determines frame **color**, rarity determines frame **complexity**. A Fire Epic has a red ornate frame; a Water Epic has a blue ornate frame (same complexity, different color).

**Rarity-Based Stat Scaling**: Rarity defines **base stats**, leveling multiplies that base. Higher rarity always wins at equal stars.
- Example: 5★ Epic (base 100 attack × 1.6 = 160) < 5★ Legendary (base 150 attack = 150, no leveling)
- Future: With +2 leveling, 5★ Epic could reach 200 attack (100 × 2.0), surpassing base Legendary but requiring heavy investment

---

## 2.5 New Player Onboarding: Trainer Decks & Game Decks

### Trainer Deck System (Starter Onboarding)

**Goal**: Give new players meaningful choice and immediate power fantasy while teaching core mechanics. Inspired by Pokemon TCG Trainer Decks and Battle Boxes.

**The Selection**:
Instead of random pack opening, players choose from **6 Trainer Decks** during onboarding:

**CURATED DECKS** (3 options - Named Epic + Pre-Built Synergy):
1. **Flame Warlord Deck** (Fire Element) - Aggressive burn-stacking playstyle
2. **Tidal Guardian Deck** (Water Element) - Defensive sustain with healing chains
3. **Stone Sentinel Deck** (Earth Element) - Terrain control and area denial

**ELEMENT DECKS** (3 options - Random Epic + Varied Support):
4. **Fire Element Deck** - Guaranteed Fire Epic (random from pool), 19 varied cards
5. **Water Element Deck** - Guaranteed Water Epic (random from pool), 19 varied cards
6. **Earth Element Deck** - Guaranteed Earth Epic (random from pool), 19 varied cards

**Deck Contents**: Each Trainer Deck contains exactly **20 cards**:
- 1× Epic Hero (named for Curated, random for Element decks)
- 6× Units (element-themed or varied)
- 2× Buildings (economy or military)
- 1× Worker (resource production)
- 8× Tactics (combat abilities)
- 2× Equipment (hero attachments)

**Key Differences**:
- **Curated Decks**: Perfect synergy out-of-the-box (all Fire cards work together), recommended for beginners
- **Element Decks**: Higher variance, deckbuilding challenge, better replayability for experienced players
- **Permanent Choice**: Selection cannot be changed (encourages alt accounts for F2P engagement)

**Why 20 Cards vs 10-15 Deck Limit?**:
- **Immediate Playability**: All 20 cards fit in first deck slot (no storage confusion)
- **Future Expansion**: Players unlock deck size progression to 50 cards by Level 30
- **Collection Start**: Strong foundation for themed deckbuilding (Fire player gets Fire synergy immediately)
- **Pokemon Model**: Matches Battle Box design (pre-built playable deck + expansion potential)

### Trainer Deck Selection Flow (Tutorial Step 6)

**Screen**: "Choose Your Starting Path"
- **6 Options Displayed**: 2 rows × 3 columns grid
  - **Top Row**: Curated Decks (Flame Warlord, Tidal Guardian, Stone Sentinel)
  - **Bottom Row**: Element Decks (Fire, Water, Earth)
- **Preview System**: Hovering shows 5 sample cards from deck
- **Commitment Warning**: "This choice is permanent and cannot be changed. Choose wisely!"

**Selection Steps**:
1. Player hovers over decks → Preview popup shows Epic hero + 4 support cards
2. Player clicks "SELECT" → Confirmation dialog appears
3. Player confirms → 20 cards instantly added to Codex
4. **Reveal Animation**: Cards flip one-by-one (Epic first with 3-sec dramatic reveal + screen shake)
5. **Bonus Reward**: 4 Standard Booster Packs (5 cards each) offered after reveal
   - **Total Starting Cards**: 20 (Trainer Deck) + 20 (Bonus Packs) = **40 cards**
   - **Skip Option**: Can skip bonus packs and open later in Pack Shop

**Why This Flow?**:
- **Meaningful Choice**: Curated vs Random appeals to different player psychologies
- **Element Commitment**: Choosing Fire locks early playstyle, teaches identity
- **Replayability**: 6 starting options vs 1 random draw (encourages multiple accounts)
- **Power Fantasy**: Guaranteed Epic hero from minute 1 (no "bad luck" first experience)

### Starting Deck Size Constraints

**Player Level 1 (New Player)**:
- **Deck Size**: 20 cards (fixed for Trainer Deck)
- **Why Fixed Start**: 
  - Trainer Decks are pre-balanced (20 cards optimal)
  - No deck editing confusion (play immediately)
  - Teaches full card type diversity (heroes, units, buildings, tactics, equipment)
  - Encourages mastery before deckbuilding freedom

**Total Collection Size** (Unlimited):
- **Codex Capacity**: Unlimited storage for all owned cards
- **Active vs Inactive**: Cards in deck slots are "active", rest stored in Codex
- **Inactive Benefits**: Can still be viewed, traded, combined, upgraded in Codex

### Deck Size Progression (Player Level Scaling)

As players gain **Player XP** (from battles, quests, events), their **Player Level** increases, unlocking larger deck sizes:

| Player Level | Max Deck Size | How to Reach | Estimated Time (Active Player) |
|--------------|---------------|--------------|--------------------------------|
| **1** | 20 cards (fixed Trainer Deck) | Start of game | Day 1 |
| **3** | 20-25 cards | Complete tutorial campaign (5 battles) | Day 1-2 |
| **5** | 25-30 cards | Complete first saga chapter (10 battles) | Day 3-5 |
| **10** | 30-35 cards | Reach County Map, join alliance | Week 1-2 |
| **15** | 35-40 cards | Complete State Map PvE | Week 3-4 |
| **20** | 40-45 cards | Reach Global Map | Month 1-2 |
| **30** | 45-50 cards (max) | Endgame content, prestige | Month 3-6 |

**Why Progressive Scaling?**:
- **F2P Accessible**: All players can reach max deck size through normal play (no paywall)
- **Natural Progression**: Deck size grows as player skill and collection grow
- **Active Player Advantage**: More active play = faster leveling = earlier access to bigger decks
- **Strategic Depth**: Larger decks unlock more complex combos and deck archetypes

### Game Deck System (Post-Launch Premium Content)

**Purpose**: Offer curated 50-card decks for collectors and players who want to skip pack RNG. Models Pokemon Battle Boxes.

**Format**: 
- **50 cards per Game Deck** (full playable collection)
- **Guaranteed Contents**: 1 Legendary, 2-3 Epics, 10 Rares, ~20 Uncommons, ~17 Commons
- **No Duplicates**: Each card is unique within the deck
- **Theme-Based**: Norse Conquest, Roman Legion, Modern Military, Greek Mythology, etc.

**Pricing**:
- **Real Money**: $19.99 USD (premium option, instant purchase)
- **Earned Gold**: 50,000 Gold (grindable option, ~2-3 weeks active play)
- **Premium Gems**: 2,000 Gems (convertible currency, ~$20 value)

**Expansion Path**:
- **Launch**: 3 Curated Trainer Decks (Fire/Water/Earth), 3 Random Element Decks (free)
- **Month 1-3**: Add Wind/Dark/Light Trainer Decks (free unlocks via campaign)
- **Year 1**: Release 6 Game Decks (Norse, Roman, Greek, Egyptian, Sci-Fi, Fantasy) at $19.99 each
- **Seasonal**: Limited-edition Game Decks (Halloween, Winter, Summer) with exclusive Legendary cards

**Why Game Decks?**:
- **Whale Appeal**: $120 to own all 6 Game Decks (collector completionist)
- **F2P Accessible**: Can buy with earned gold (respects non-payers)
- **Content Drops**: New Game Deck = new theme = marketing event
- **Skip RNG**: Players tired of pack gambling can buy guaranteed cards
- **Multi-Element Design**: Later Game Decks can mix elements (Norse = Fire + Earth, Greek = Water + Wind)

**Example Game Deck**: 
**"Norse Conquest" Game Deck** ($19.99 / 50,000 Gold):
- 1× Legendary: Odin Allfather (Hero, summons ravens)
- 3× Epic: Thor Thunderlord, Freya Valkyrie, Loki Trickster
- 10× Rare Norse units (Berserkers, Shieldmaidens, Frost Giants)
- 20× Uncommon Norse buildings/tactics (Longhouses, Rune Stones, Blizzard)
- 16× Common Norse workers/equipment (Blacksmiths, Fur Cloaks)
- **Theme**: Fire + Earth synergy (burn damage + fortifications)

**Unlock Requirements**:
- Player Level 10+ (prevents new players from bypassing progression)
- Tutorial complete (ensures players understand mechanics)
- Available in Pack Shop under "Game Decks" tab

---

## 2.6 Card Stacking, Formations & Map Deployment

### Overview: Heroes of Might and Magic Meets Modern CCGs

Sovereign Territories borrows heavily from **Heroes of Might and Magic** army stacking while adding modern flexibility. Instead of forcing exact card duplication, we allow **cross-theme, same-type stacking** to create diverse armies from your collection.

**Core Principles**:
1. **Stacking**: Multiple cards occupy a single tile, combining stats into one powerful unit
2. **Formations**: Pre-defined placement patterns for quick deployment
3. **Visual Representation**: High-rarity cards = 3D figures, low-rarity = card sprites
4. **Auto vs Manual**: Choose convenience or strategic control
5. **Map Scaling**: 1 deck per tile on Global Map → zoom into battle with full deck

---

### Card Stacking System (HoMM-Style Armies)

#### What Is Stacking?

**Stacking** combines multiple cards of the **same unit type** onto a single map tile, merging them into one powerful army stack.

**Example**:
- 3x Elf Archer (Common)
- 2x Human Crossbowman (Uncommon)
- 1x Dwarven Marksman (Rare)

All 6 cards stack onto **one tile** as "Ranged Stack Alpha" with combined stats.

#### Stacking Rules (Cross-Theme Flexibility)

**✅ Valid Stacking Combinations**:
- **Same Unit Type Across Themes**: 
  - Elf Archers + Human Crossbowmen + Dwarven Marksmen = "Ranged Stack" ✅
  - Norse Berserker + Samurai Warrior + Knight = "Melee Stack" ✅
  - Fire Mage + Ice Mage + Lightning Wizard = "Caster Stack" ✅
- **Same Rarity (Optional Bonus)**: 
  - All Uncommon cards in stack = +10% to all stats (synergy bonus)
  - All Rare+ cards in stack = +20% to all stats
- **Mixed Rarity Allowed**: 
  - Common + Rare + Epic in same stack = no penalty, just combined stats

#### Stacking Rules (Map-Dependent Flexibility)

**IMPORTANT**: Stacking rules differ based on which map layer you're on:

**On County Map (Strategic Layer)** → **Full Army Stacks Allowed**:
- ✅ **Mix ALL Card Types**: Epic heroes + Archers + Healers + Walls + Buildings in ONE stack
- ✅ **Cross-Theme**: Elf + Human + Dwarf units together
- ✅ **Mixed Rarity**: Common + Rare + Epic + Legendary in same stack
- **Why**: County map represents your entire army moving as one force (like HoMM heroes with their armies)
- **Visual**: Stack shows as single icon/flag with lead hero portrait

**On Battle Map (Tactical Layer)** → **Unit Type Stacking**:
- ✅ **Same Unit Type Only**: Archers stack with archers, warriors with warriors
- ✅ **Cross-Theme Still Allowed**: Elf Archers + Human Crossbowmen = valid
- ❌ **No Mixed Types**: Archers + Warriors = separate stacks on battle grid
- **Why**: Battle map is where you deploy formations (tanks front, archers back)
- **Visual**: Each unit type gets its own tile position on tactical grid

**Stacking Hierarchy by Map Layer**:

| Map Layer | Stack Composition | Visual | Example |
|-----------|-------------------|--------|---------|
| **Global Map** | Entire deck = 1 icon | Flag/banner with deck name | "Fire Rush Deck" icon on territory |
| **County Map** | Full army stack (10-50 cards all types) | Hero portrait + army count | "Thor + 24 units" moving as one |
| **Battle Map** | Separated by unit type | Individual stacks on grid tiles | 3× Archer stacks, 2× Warrior stacks, 1× Hero |

**Example Flow**:
1. **Global Map**: You deploy "Viking Deck" to Territory A (appears as single flag)
2. **Zoom to County Map**: "Viking Deck" appears as Thor (hero portrait) + 14 unit cards = 1 movable stack
3. **Move stack to enemy spawn**: Engage battle
4. **Zoom to Battle Map**: 15 cards separate into formation:
   - Thor (Epic hero) → Front center tile
   - 3× Archers (mixed elf/human) → Back row left
   - 2× Berserkers (warriors) → Front row right
   - 1× Healer → Rear center
   - Etc.

---

#### Mixed-Type Stacking (County Map Only)

**✅ Valid County Map Stack Combinations**:
- **Epic Hero + Units + Buildings + Workers**:
  - Example: Thor + 5 Archers + 3 Warriors + 2 Healers + 1 Farm + 1 Mine = 13-card stack
- **Cross-Theme Mixed Army**:
  - Example: Elf Archers + Human Knights + Dwarf Miners + Norse Healer = 1 stack
- **Economy + Battle Mix**:
  - Example: 10 battle cards + 5 economy cards (buildings/workers) = 15-card stack

**❌ Invalid Battle Map Combinations**:
- Archers + Warriors on same battle grid tile = ❌ (must separate into different tiles)
- Hero + Archers on same battle tile = ❌ (hero gets own tile)
- Farm + Archers on same battle tile = ❌ (buildings don't deploy to battle grid)

**Why This Matters**:
- **County Map** = Strategic movement (armies travel together, like HoMM)
- **Battle Map** = Tactical deployment (separate unit types for formation strategy)
- **Simplifies county exploration** (don't micromanage 50 individual units)
- **Adds depth to battles** (formation positioning matters)

---

#### Stack Stat Calculation (Mathematical Precision)

**Stack HP** = `Σ(BaseHP × HPMultiplier(rarity) × StarMultiplier(stars))` for all cards in stack
**Stack Attack** = `Σ(BaseAttack × AttackMultiplier(rarity) × StarMultiplier(stars))`
**Stack Defense** = `Average(Defense values) × (1 + 0.05 × (stackSize - 1))` (diminishing returns)
**Stack Speed** = `Min(Speed values)` (slowest card determines stack movement)

**Example Stack Math** (County Map Full Army):
- 1x Epic Thor (HP: 100, Attack: 20, Defense: 15, Speed: 4)
- 3x Common Elf Archer (HP: 10, Attack: 5, Defense: 2, Speed: 3)
- 2x Uncommon Human Crossbowman (HP: 15, Attack: 7, Defense: 3, Speed: 2)
- 1x Rare Healer (HP: 20, Attack: 2, Defense: 5, Speed: 2)
- Total: 7 battle cards in county stack

**County Map Stats** (moving as one army):
- HP = 100 + (10×3) + (15×2) + 20 = 100 + 30 + 30 + 20 = **180 HP**
- Attack = 20 + (5×3) + (7×2) + 2 = 20 + 15 + 14 + 2 = **51 Attack**
- Defense = ((15+2+2+2+3+3+5)/7) × (1 + 0.05×6) = 4.57 × 1.3 = **5.94 Defense**
- Speed = Min(4, 3, 3, 3, 2, 2, 2) = **2 Speed** (entire army moves at healer speed)

**Battle Map Stats** (separated into unit type stacks):
- Thor: 100 HP, 20 Attack, 15 Defense, 4 Speed (solo hero)
- Archer Stack (3× Elf): 30 HP, 15 Attack, ~2.3 Defense, 3 Speed
- Crossbow Stack (2× Human): 30 HP, 14 Attack, 3 Defense, 2 Speed
- Healer (solo): 20 HP, 2 Attack, 5 Defense, 2 Speed

**Same-Rarity Bonus** (applies to battle map stacks only):
- Archer stack (all Common) = +10% stats = 33 HP, 16.5 Attack
- Crossbow stack (all Uncommon) = +10% stats = 33 HP, 15.4 Attack

---

#### Deck Composition Limits (Rarity Budget System)

To prevent "all Legendary" decks while still allowing creativity, we use a **Rarity Point Budget**:

**Rarity Point Costs**:
- Common = 1 point
- Uncommon = 2 points
- Rare = 4 points
- Epic = 8 points
- Legendary = 16 points
- Mythic = 32 points

**Deck Budget by Player Level**:

| Player Level | Battle Card Limit | Rarity Point Budget | Example Deck Composition |
|--------------|-------------------|---------------------|--------------------------|
| **1-5** | 10-15 cards | 50 points | 5 Legendaries (80 pts) = ❌ TOO HIGH |
| **1-5** | 10-15 cards | 50 points | 1 Epic (8) + 5 Rare (20) + 9 Common (9) = 37 pts ✅ |
| **10-15** | 25-30 cards | 120 points | 2 Legendary (32) + 3 Epic (24) + 10 Rare (40) + 15 Common (15) = 111 pts ✅ |
| **20-25** | 35-40 cards | 200 points | 3 Legendary (48) + 5 Epic (40) + 15 Rare (60) + 17 Common (17) = 165 pts ✅ |
| **30+** | 40-50 cards | 300 points | 5 Legendary (80) + 8 Epic (64) + 20 Rare (80) + 17 Common (17) = 241 pts ✅ |

**Example Scenarios**:
- **"5 Legendary Whale Deck"** (Level 30):
  - 5 Legendary = 80 points
  - Remaining budget: 220 points
  - Can add: 27 Epics (216 pts) OR 55 Rares (220 pts) OR 220 Commons
  - **Result**: Extremely top-heavy, very few cards (5-32 total)
  
- **"Balanced Mid-Range Deck"** (Level 20):
  - 2 Legendary (32) + 5 Epic (40) + 12 Rare (48) + 20 Common (20) = 140 points
  - Total: 39 cards
  - **Result**: Good mix, flexible strategies

**Economy Cards** (Separate Budget):
- **Not counted against rarity budget**
- Separate limit: 10-15 economy cards per deck
- Types: Buildings (Farm, Mine, Turret, Wall), Workers (Farmer, Miner, Scout)
- Can deploy to county map tiles, don't go to battle map

**Total Deck Composition**:
- **Battle Cards**: 10-50 (based on Player Level) within rarity budget
  - Heroes, Units, Tactics, Equipment
  - Used for combat and exploration
  - Can be split into multiple hero-led armies on county map
- **Economy Cards**: 10-15 (separate category, not counted in rarity budget)
  - Buildings: Farm, Mine, Lumber Mill, Turret, Wall
  - Workers: Farmer, Miner, Lumberjack, Scout
  - Deployed to captured tiles for AFK income
  - Left behind when army moves (must return to retrieve)
- **Max Total Deck**: 50 battle + 15 economy = **65 cards** (Level 30+ only)

**Why Separate Categories?**:
- ✅ **Clarity**: Battle cards fight, economy cards generate income
- ✅ **Strategy**: Decide which tiles deserve resource investment
- ✅ **Risk/Reward**: Leave valuable workers behind, or keep army flexible?
- ✅ **Economy Management**: Economy cards are strategic deployments, not combat filler

**Card Category Breakdown**:

| Category | Types | Count Limit | Counted in Rarity Budget? | Use Case |
|----------|-------|-------------|---------------------------|----------|
| **Battle Cards** | Heroes, Units, Tactics, Equipment | 10-50 (Player Level) | ✅ Yes | Combat, exploration, formations |
| **Economy Cards** | Buildings, Workers | 10-15 (fixed) | ❌ No | AFK income, tile upgrades |

**Example Level 20 Deck**:
- **Battle Cards** (35 total, 200 rarity points):
  - 2 Legendary Heroes (32 pts)
  - 5 Epic Units (40 pts)
  - 12 Rare Units (48 pts)
  - 16 Common/Uncommon Units (20 pts)
  - Total: 140 points (under 200 budget ✅)
- **Economy Cards** (12 total, separate):
  - 3 Farms
  - 2 Mines
  - 1 Lumber Mill
  - 3 Farmers
  - 2 Miners
  - 1 Turret

**Why Rarity Budget System?**:
- ✅ **Prevents "5 Legendary Only" decks** (too expensive, need filler)
- ✅ **Encourages diversity** (mix rarities for better value)
- ✅ **Allows whales to flex** (can still build heavy Legendary decks, just fewer cards)
- ✅ **F2P viable** (Common/Uncommon decks are cheap, can compete with strategy)
- ✅ **Scales with progression** (higher level = bigger budget = more power)
- ✅ **Economy cards separate** (don't compete with battle card budget)

---

### Formation System (Auto-Deployment Presets)

#### What Are Formations?

**Formations** are pre-defined placement patterns that automatically position your stacks on the battlefield based on strategic templates.

**Think Party-Based RPGs**: Tank in front, DPS in middle, healers in back.

#### Formation Presets (Built-In Templates)

**1. "Frontline Vanguard" Formation**:
- **Epic/Legendary Heroes**: Front row center (tiles 1-3)
- **Melee Units**: Front row flanks (tiles 4-6)
- **Ranged Units**: Back row (tiles 7-12)
- **Healers/Casters**: Rear center (tiles 13-15)
- **Use Case**: Aggressive push, protect backline, classic army formation

**2. "Defensive Turtle" Formation**:
- **Tanks/Walls**: Surround perimeter (tiles 1, 3, 6, 9, 12, 15)
- **Ranged Units**: Inner ring (tiles 2, 5, 8, 11, 14)
- **Healers**: Absolute center (tile 7)
- **Epic Heroes**: Behind walls (tiles 4, 10)
- **Use Case**: Hold position, outlast opponent, protect key units

**3. "Flanking Cavalry" Formation**:
- **Fast Units (Cavalry, Scouts)**: Far left/right flanks (tiles 1, 6, 9, 15)
- **Archers**: Center back (tiles 7, 8)
- **Melee Infantry**: Center front (tiles 4, 5)
- **Epic Heroes**: Mobile positions (tiles 2, 11)
- **Use Case**: Pincer attack, surround enemy, mobility-focused

**4. "Epic Showcase" Formation**:
- **Epic+ Cards**: Prominently displayed in front (tiles 2, 5, 8, 11)
- **Rare Support**: Behind Epics (tiles 3, 6, 9, 12)
- **Commons/Uncommons**: Fill gaps
- **Use Case**: Flex your collection, status display, whale competition

**5. "Balanced Wedge" Formation**:
- **Tank**: Front center tip (tile 1)
- **Melee DPS**: Diagonal flanks (tiles 2, 3, 4, 6)
- **Ranged**: Back triangle (tiles 7, 8, 9)
- **Healers**: Rear (tiles 10, 11)
- **Use Case**: Versatile, all-around solid, beginner-friendly

#### Custom Formation Editor

**Create Your Own**:
1. Open **Formation Manager** in Codex
2. Name your formation ("My PvP Build", "Fire Rush", etc.)
3. Drag stacks onto 15-tile grid (visual editor)
4. Save formation (up to 10 custom formations per player)
5. Apply to any deck with 1-click

**Formation Slots**:
- **Free Players**: 5 custom formation slots
- **VIP 3**: 10 custom formation slots
- **VIP 5**: 20 custom formation slots + share with alliance

**Formation Tags** (Auto-Sort):
- Tag stacks as: Tank, DPS, Ranged, Healer, Caster, Support
- Formation auto-fills based on tags (AI places tanks in front)
- Override individual positions manually if needed

---

### Manual vs Auto Deployment

#### Auto-Deployment (Quick Play)

**When**: 
- Campaign battles (PvE)
- Daily missions
- AFK auto-battles
- Quick PvP matches

**How**:
1. Select deck
2. Choose formation preset (or use default)
3. Click "Deploy"
4. System auto-places all stacks based on formation rules
5. Battle starts immediately

**Benefits**:
- ⏱️ **Speed**: Deploy in 2 seconds
- 🎮 **Convenience**: Perfect for farming/grinding
- 📱 **Mobile-Friendly**: One-tap deployment
- ♿ **Accessibility**: Reduces decision fatigue

#### Manual Deployment (Strategic Control)

**When**:
- High-stakes PvP tournaments
- Alliance wars
- Guild vs Guild events
- Ranked matches
- Special events with setup days

**How**:
1. Select deck
2. Battle map displayed with terrain
3. Drag each stack individually onto desired tiles
4. Consider terrain bonuses (hills, forests, rivers)
5. Finalize placement
6. Battle starts

**Benefits**:
- 🧠 **Strategy**: Optimize for specific map/enemy
- 🏆 **Competitive Edge**: Outsmart opponents with positioning
- 🎯 **Terrain Mastery**: Place archers on hills, cavalry on plains
- 💎 **Skill Expression**: Separate good players from great

#### Event Setup Days (Pre-Battle Planning)

**For Major Events**:
- **Register Early**: 3-7 days before event starts
- **Map Revealed**: See terrain layout in advance
- **Setup Phase**: Manually place formations
- **Deadline**: 24 hours before event (or auto-deploy happens)
- **Locked In**: Can't change once event starts

**Example Timeline**:
- **Day 1 (Monday)**: "Alliance War Week" announced, map revealed
- **Days 2-5 (Tue-Fri)**: Players register, manually deploy formations
- **Day 6 (Saturday 12pm)**: Deployment deadline, auto-deploy for unfinished
- **Day 6 (Saturday 2pm)**: Event starts, battles resolve
- **Day 7 (Sunday)**: Results posted, rewards distributed

**Why Setup Days?**:
- ✅ Allows casual players to participate without time pressure
- ✅ Lets hardcore players optimize every placement
- ✅ Creates community discussion ("Where did you put your Epic tank?")
- ✅ Reduces server load (not everyone deploying simultaneously)

---

### Map Tiers & Deck Deployment

#### Zoom Level System (Risk → HoMM Transition)

Sovereign Territories uses a **multi-tier zoom system** where you deploy decks at macro level and zoom into battles at micro level.

**Global Map** (Risk-Style):
- **View**: Entire continent, 50-100 territories
- **Deployment**: **1 deck per territory/tile**
- **Representation**: Deck shown as single icon/flag
- **Click Territory**: Zoom into County Map

**County Map** (Regional View):
- **View**: 10-20 tiles representing county divisions
- **Deployment**: **Full deck spreads across tiles** (15-30 stacks)
- **Representation**: Each stack = separate unit on map
- **Click Stack**: Zoom into Battle Map

**Battle Map** (Tactical Grid):
- **View**: 15x15 grid (or custom size based on map)
- **Deployment**: **Stacks positioned on grid tiles**
- **Representation**: 3D units or card sprites
- **Combat**: Turn-based tactical battles (HoMM style)

#### Multiple Decks on Large Maps

**Tutorial/Local Maps** (Level 1-5 Players):
- **Restriction**: **1 deck only** (simplicity for new players)
- **Deck Size**: 10-15 cards
- **Stacks**: 3-5 stacks max

**State Maps** (Level 10+ Players):
- **Restriction**: **1-2 decks** (can deploy second deck to different territory)
- **Deck Size**: 25-30 cards each
- **Stacks**: 7-10 stacks per deck

**County Maps** (Level 15+ Players):
- **Restriction**: **2-3 decks** (spread forces across region)
- **Deck Size**: 30-35 cards each
- **Stacks**: 10-15 stacks per deck

**Global Maps** (Level 20+ Players):
- **Restriction**: **Up to 5 decks** (1 deck per territory controlled)
- **Deck Size**: 40-50 cards each
- **Stacks**: 15+ stacks per deck
- **Multi-Front Warfare**: Manage multiple battles simultaneously (like HoMM campaign)

**Example Scenario**:
- Player controls 3 territories on Global Map
- Deploys **Deck A** to Territory 1 (aggressive fire theme)
- Deploys **Deck B** to Territory 2 (defensive earth theme)
- Deploys **Deck C** to Territory 3 (economy buildings)
- Enemy attacks Territory 1 → zooms into Battle Map with Deck A's stacks

---

### PvE Campaign: County Map Exploration (Tutorial & Progression)

#### Tutorial Flow (First Battle - Manual Required)

**Goal**: Teach core mechanics with easy victory, manual movement required.

**Setup**:
1. Player receives starter deck (10-15 cards: 1 Epic, 5 Rare, 9 Common/Uncommon)
2. Sets formation using "Balanced Explorer" preset
3. Deck appears on **Global Map** as single flag icon
4. Zoom into **County Map** → deck appears as Epic hero portrait + "14 units" label

**First Battle**:
1. **County Map**: Player sees single PvE spawn (red enemy flag) nearby
2. **Move Order**: Click your army stack → click adjacent tile → army moves (teach movement)
3. **Engage Combat**: Move stack onto enemy spawn tile → battle triggers
4. **Zoom to Battle Map**: 15 cards from your deck separate into formation on tactical grid (5x5 or 7x7)
5. **Manual Placement Required**: 
   - Tutorial highlights each card type
   - "Place your Epic Hero in front" → player drags Thor to front center
   - "Place Archers in back row" → player drags 3 Archer cards to back tiles
   - "Place Healer behind hero" → player drags Healer to rear center
   - Etc. until all cards placed
6. **Turn-Based Combat Begins**:
   - Tutorial forces manual movement each turn
   - "Move Thor forward 2 tiles to attack goblin"
   - "Use Archer to shoot from range"
   - "Healer stays back and casts heal on Thor"
7. **Easy Victory**: 
   - Enemy: 5× Common Goblin + 1× Uncommon Goblin Chief (total: 6 cards, ~40 HP total)
   - Player: 15 cards, ~150 HP total
   - Player wins in 3-5 turns even with suboptimal play
8. **Rewards**: 100 XP, 500 gold, 1 Common card, "First Victory" achievement

**Post-Tutorial**:
- **Auto-Battle Unlocked**: "You can now use Auto-Battle for future fights! (or continue manual)"
- **Next 3-5 Battles**: Similar easy spawns, player can choose auto or manual
- **Quick Wins**: Teaches players the county map flow without frustration

---

#### County Map Structure (Open Exploration, Non-Linear)

**Map Design Philosophy**:
- **Not Linear Stages**: Unlike "Stage 1 → Stage 2 → Boss", county maps are open exploration
- **Fog of War**: Map starts mostly hidden, reveals as you explore
- **Static Spawns**: Enemy camps/spawns don't roam (expansion feature)
- **Respawning**: Defeated spawns respawn after 1-6 hours (for farming)
- **Goal**: Find and defeat the Boss (always on map), but path is player's choice
- **Buffs Along the Way**: Capture key locations for permanent bonuses

**Example County Map Layout** (Medium Difficulty):
```
    [Fog] [Fog] [?Mine?] [Fog] [Fog]
    [Fog] [Spawn][  Path  ][Spawn][Fog]
  [Start] [Path][Buff Shrine][Path][Town]
    [Fog] [Path][   Fog   ][Spawn][Fog]
    [Fog] [Fog] [?Boss?] [Fog] [Fog]
```

**Tile Types**:
- **Start**: Where your army begins (safe zone, can't be attacked)
- **Path**: Empty tiles, safe to traverse
- **Spawn**: Enemy camps (2-8 cards each, various difficulties)
- **Fog**: Unrevealed tiles (might contain spawns, resources, or nothing)
- **Buff Shrine**: Capture for +10% ATK or +10% HP (permanent for this map)
- **Resource Nodes**: Gold Mine, Lumber Mill, Farm (can garrison economy cards)
- **Town**: Capture for +1 "Flex Hero" (temporary ally for this map only)
- **Boss**: Final objective, always present but location varies

**Map Sizes**:
- **Tutorial County**: 5x5 tiles (25 total), 3 spawns, 1 boss
- **Easy County**: 7x7 tiles (49 total), 5-8 spawns, 1 boss, 2 buff shrines, 1 town
- **Medium County**: 10x10 tiles (100 total), 10-15 spawns, 1 boss, 3 buff shrines, 2 towns
- **Hard County**: 12x12 tiles (144 total), 20-30 spawns, 1 boss, 5 buff shrines, 3 towns
- **Elite County**: 15x15 tiles (225 total), 40-50 spawns, 1 elite + 1 boss, 8 buff shrines, 5 towns

---

#### Splitting Your Deck into Multiple Armies (Multi-Hero System)

**Core Concept**: Each **Epic+ hero** in your deck can lead their own independent army stack on the county map.

**How It Works**:
- **Single Hero Deck**: If you have 1 Epic hero + 14 units → **1 army stack** on county map
- **Multi-Hero Deck**: If you have 3 Epic heroes + 30 units → **up to 3 army stacks** (divide units between heroes)
- **Visual**: Each Epic+ hero = **3D miniature figurine** on county map (looks like tabletop wargaming)
- **Movement**: Each army moves independently (like HoMM multiple heroes)

**Deck Deployment Example**:

**Starting Deck** (Level 15 Player, 30 battle cards):
- 1× Legendary Thor (hero)
- 2× Epic Fire Mage (hero), Epic Knight (hero)
- 10× Rare/Uncommon warriors, archers, healers
- 15× Common scouts, spearmen
- 2× Rare tactics

**County Map Deployment Options**:

**Option 1: Single Mega-Army** (Conservative):
- **Army 1**: Thor + 2 Epic heroes + all 27 units = 1 powerful stack
- **Visual**: Thor figurine (3D) + "29 units" badge
- **Pros**: Maximum power concentration, hard to defeat
- **Cons**: Slow movement (one stack at a time), can't cover multiple objectives

**Option 2: Three Hero-Led Armies** (Aggressive):
- **Army 1**: Thor + 10 units (heavy hitters) = main force
  - Visual: Thor 3D figurine + "10 units" badge
- **Army 2**: Fire Mage + 8 units (ranged support)
  - Visual: Fire Mage 3D figurine + "8 units" badge
- **Army 3**: Knight + 9 units (fast cavalry)
  - Visual: Knight 3D figurine + "9 units" badge
- **Pros**: Cover more ground, explore faster, multi-pronged attacks
- **Cons**: Each army weaker individually, risk of defeat in detail

**Option 3: Mixed Strategy** (Balanced):
- **Army 1**: Thor + Fire Mage + 20 units = main army (26 cards)
  - Visual: Thor figurine (lead) + Fire Mage figurine behind + "24 units" badge
- **Army 2**: Knight + 7 units = scout/flanking force (8 cards)
  - Visual: Knight figurine + "7 units" badge
- **Pros**: Strong main force + flexible scout army
- **Cons**: Scout army vulnerable if caught alone

---

#### Hero-Less Stacks (Lower Rarity Units)

**Question**: Can you deploy Common/Uncommon cards without a hero?

**Answer**: **Yes, but visually distinct and mechanically limited.**

**Visual Representation by Stack Type**:

| Stack Composition | Visual on County Map | Movement | Example |
|-------------------|---------------------|----------|---------|
| **Epic+ Hero + Units** | 3D miniature figurine (hero) + unit count badge | Full speed | Thor figurine + "15 units" |
| **Rare Hero + Units** | Premium card sprite standing upright + unit badge | Full speed | Rare Mage card + "8 units" |
| **No Hero, 5+ Units** | Thick/layered card sprite standing upright | 75% speed | "10 Archers" thick card |
| **No Hero, 2-4 Units** | Standard card sprite standing upright | 50% speed | "3 Scouts" card sprite |
| **Single Scout** | Flat card sprite (lying down) | 100% speed | "Scout" flat card (fast but fragile) |

**Thick Card Visual** (5+ cards, no hero):
- **Appearance**: Card stack that looks physically thicker
- **Count Badge**: "×10 Archers" displayed prominently
- **Example**: 10× Uncommon Archers = appears as layered/thick card sprite standing upright on tile
- **Why**: Shows multiple cards without rendering 10 separate sprites (performance optimization)

**Single Scout Mechanic**:
- **Use Case**: Sacrifice 1 Common Scout to reveal fog of war
- **Visual**: Single flat card sprite (vulnerable, low profile)
- **Movement**: Fastest (no army to slow down)
- **Combat**: Dies instantly if engaged (suicide scouting for intel)
- **Strategy**: "Is this spawn too strong? Send scout to find out before committing main army"

---

#### Splitting Process (Dividing Your Deck)

**Step-by-Step**:

1. **Deploy Full Deck to County Map**: All 30 battle cards appear as 1 stack (lead hero)
2. **Right-Click Stack** → "Manage Armies"
3. **Army Management UI Opens**:
   - Shows all heroes in deck (Legendary Thor, Epic Fire Mage, Epic Knight)
   - Shows all units sorted by type (warriors, archers, healers, etc.)
4. **Drag Units to Heroes**:
   - Drag 10 warriors → assign to Thor
   - Drag 8 archers → assign to Fire Mage
   - Drag 9 cavalry → assign to Knight
   - Leave 2× tactics unassigned (shared resource pool)
5. **Confirm Split**: 3 separate army stacks now visible on county map
6. **Each Army Gets Formation**:
   - Thor's Army: "Frontline Vanguard" formation
   - Fire Mage's Army: "Defensive Turtle" formation
   - Knight's Army: "Flanking Cavalry" formation

**Re-Merge Armies**:
- Move two hero stacks onto same tile
- Right-click → "Merge Armies"
- Units combine into single stack (lead hero = highest rarity)
- Can split again later (unlimited splits/merges)

---

#### Economy Card Deployment (Strategic Tile Upgrades)

**How Economy Cards Work**:

**1. Capture Tile with Resource Node**:
- Defeat spawn guarding **Gold Mine** tile
- Tile now controlled (shows your faction color)

**2. Deploy Economy Cards**:
- Open **Economy Card Menu** (while army on tile)
- Select cards to deploy:
  - 1× Mine (building) → +50 gold/hour AFK
  - 2× Miner (worker) → +25 gold/hour each (+50 total)
  - Total: +100 gold/hour from this tile
- Cards are **removed from army deck** and **placed on tile**

**3. Army Leaves Tile**:
- Move army to next objective
- Economy cards **stay behind** (static deployment)
- Tile shows: Small flag + Mine icon + "3 economy cards" badge
- AFK income continues (100 gold/hour) even when army is elsewhere

**4. Retrieval**:
- **Problem**: Want to move Miners to different tile
- **Solution**: Send hero back to original tile
- **Process**: Army moves onto tile → "Retrieve Economy Cards" → select which to take → cards added back to army deck
- **Strategic Decision**: Is it worth the time to retrieve, or leave them?

**Economy Card Deployment Limits**:

| Resource Node Type | Max Economy Cards Per Tile | AFK Income Bonus |
|--------------------|------------------------------|------------------|
| **Gold Mine** | 5 (1 Mine + 4 Miners) | +200 gold/hour max |
| **Farm** | 5 (1 Farm + 4 Farmers) | +50 food/hour max |
| **Lumber Mill** | 5 (1 Mill + 4 Lumberjacks) | +50 wood/hour max |
| **Turret/Wall Tile** | 3 (Defensive structures only) | No income, +defense |

**Why Retrieval Matters**:
- ✅ **Economy cards are limited** (only 10-15 in deck)
- ✅ **Opportunity cost**: Miners on Tile A can't help Tile B
- ✅ **Strategic redeployment**: Move workers to better tiles as you progress
- ❌ **Time cost**: Hero must backtrack (wastes turns in PvP or empowers enemies in PvE)

---

#### Time Pressure Mechanics (Turn Cost)

**PvE County Maps** (Optional Difficulty Modifier):

**"Enemy Grows Stronger" Mechanic**:
- **Every 5 turns** you take, all enemy spawns gain **+10% HP and ATK**
- **Turn Counter**: Visible in top-right corner ("Turn 15 - Enemies +30% stronger")
- **Strategy**: Rush boss before enemies scale too high, OR farm buff shrines to offset
- **Example**:
  - Turn 1-5: Enemies at 100% power
  - Turn 6-10: Enemies at 110% power
  - Turn 11-15: Enemies at 120% power
  - Turn 30+: Enemies at 160% power (hard mode)

**Why Time Pressure?**:
- ✅ Discourages infinite farming (get stronger, but so do enemies)
- ✅ Rewards efficient pathing (plan route to boss)
- ✅ Makes retrieving economy cards risky (every turn counts)
- ❌ Can disable for "Casual Mode" (no time pressure, farm forever)

**PvP County Battles** (Guild vs Guild Events):

**"Skip Turn" Mechanic**:
- **Problem**: Hero is backtracking to retrieve economy cards
- **Solution**: Click "Skip Turn" → hero doesn't move this turn
- **Cost**: Opponent gets extra turn (2 actions vs your 1)
- **Strategy**: Only skip if absolutely necessary (repositioning, waiting for reinforcements)
- **Visual**: Grayed-out hero icon shows "Skipped Turn" status

**Example PvP Scenario**:
- **Turn 10**: You send Knight back to retrieve 2 Miners from captured mine
- **Turn 11**: Knight reaches mine tile, retrieves Miners (but enemy gets 2 actions this turn)
- **Turn 12**: Knight returns to main army with Miners, ready to redeploy elsewhere
- **Cost**: Enemy used 2 extra actions (captured additional tile, recruited flex hero)

---

#### Visual Design Summary (County Map Representation)

**What You See on County Map**:

| Unit Type | Visual | Example |
|-----------|--------|---------|
| **Legendary Hero + Army** | Large 3D figurine (gold glow) + badge | Thor miniature + "25 units" |
| **Epic Hero + Army** | Medium 3D figurine + badge | Fire Mage miniature + "12 units" |
| **Rare Hero + Army** | Standing card sprite (premium) + badge | Rare Knight card + "8 units" |
| **Uncommon Units Only (5+)** | Thick/layered card sprite + badge | "10 Archers" thick card |
| **Common Units Only (2-4)** | Standard card sprite + badge | "3 Scouts" card |
| **Single Scout** | Flat card sprite (low profile) | "Scout" flat card |
| **Resource Tile (Yours)** | Small flag + building icon + count | Flag + Mine icon + "3 cards" |
| **Enemy Spawn** | Red flag + difficulty color | Red flag (purple = elite spawn) |

**Animation/VFX**:
- **3D Figurines**: Idle animations (breathing, weapon shifts)
- **Card Sprites**: Gentle hover/glow effect
- **Movement**: Units slide smoothly between tiles (no teleporting)
- **Combat Engage**: Visual effect when stack enters enemy tile (clash animation)

---

#### County Map Gameplay Loop (Revised)

**Player Journey with Multiple Armies & Resource Management**:

1. **Deploy Deck to County Map**: Full 30 battle cards + 10 economy cards
2. **Split into Hero-Led Armies**: 
   - Thor + 15 units (main force)
   - Fire Mage + 10 units (support force)
   - Knight + 5 units (scout force)
3. **Explore with Multiple Armies**:
   - Thor pushes center (strong spawns)
   - Fire Mage flanks left (medium spawns)
   - Knight scouts right (reveals fog fast)
4. **Capture Resource Nodes**:
   - Thor defeats spawn guarding Gold Mine
   - Deploy 1 Mine + 2 Miners (3 economy cards placed)
   - Thor continues forward, economy cards stay behind (+100 gold/hour AFK)
5. **Recruit Flex Heroes**:
   - Fire Mage captures Town 1 → +1 Rare Healer (temp ally)
   - Knight captures Town 2 → +1 Epic Berserker (temp ally)
6. **Buff Shrines**:
   - Thor captures Shrine of Power → +10% ATK (permanent for map)
7. **Resource Redeployment**:
   - Knight backtracks to Gold Mine (Turn 20)
   - Retrieves 2 Miners (Turn 21)
   - Redeploys Miners to newly captured Lumber Mill (Turn 22)
   - Cost: 3 turns (enemy grew +6% stronger during this time)
8. **Merge for Boss**:
   - All 3 armies converge on Boss tile
   - Right-click → "Merge All Armies"
   - Final force: Thor + Fire Mage + Knight + 30 units + 3 flex heroes = **36 cards**
9. **Boss Battle**:
   - Zoom to Battle Map
   - Deploy formation (all 36 cards)
   - Defeat boss (25-card enemy deck)
10. **Victory**:
    - Collect rewards (Legendary card, 10,000 XP)
    - Flex heroes removed
    - Resource cards stay on county tiles (for AFK income until you complete map)
    - Mark county complete, return to Global Map

**Key Takeaways**:
- ✅ **Multiple heroes = multiple armies** (epic+ heroes lead independently)
- ✅ **Resource cards separate from battle cards** (strategic tile upgrades)
- ✅ **Retrieval costs time** (turns in PvE, actions in PvP)
- ✅ **Visual clarity** (3D figurines for heroes, card sprites for units, thick cards for stacks)
- ✅ **Time pressure optional** (enemies grow stronger in PvE, skip turns risky in PvP)

---

#### Flex Heroes & Temporary Allies (Power Scaling)

**Concept**: As you explore county map, find temporary hero cards that join for this map only.

**How Flex Heroes Work**:
1. **Capture Town Tile**: Defeat spawn guarding town
2. **Recruit Flex Hero**: Town offers 1 random Rare/Epic hero to join
3. **Add to Deck (Temporary)**: Flex hero added to current army stack
4. **Duration**: Only for this county map (removed when map complete)
5. **Power Scaling**: Can reach 50 total battle cards if you find all flex heroes

**Example County Map with Flex Heroes**:
- **Starting Deck**: 15 battle cards (your permanent collection)
- **Town 1**: +1 Rare Fire Mage (temp) → now 16 cards
- **Town 2**: +1 Epic Knight (temp) → now 17 cards
- **Buff Shrine 1**: +10% ATK boost → all cards stronger
- **Town 3**: +2 Uncommon Archers (temp) → now 19 cards
- **Boss Area**: +1 Legendary Dragon (temp, only if you captured all towns) → now 20 cards
- **Final Boss Battle**: You have 20 cards vs Boss with 25 cards

**Why Flex Heroes?**:
- ✅ **Power Scaling**: Even with small starting deck, you grow stronger as you explore
- ✅ **Replayability**: Different towns offer different flex heroes each playthrough
- ✅ **Strategy**: Do you rush boss or explore for flex heroes first?
- ✅ **F2P Friendly**: Don't need huge collection to beat hard counties (flex heroes help)
- ✅ **No Permanent Bloat**: Flex heroes disappear after map, don't clutter Codex

**Flex Hero Pool** (Random per Town):
- **Uncommon Flex** (60% chance): Basic units (Archer, Spearman, Scout)
- **Rare Flex** (30% chance): Specialists (Healer, Mage, Cavalry)
- **Epic Flex** (9% chance): Named heroes (Sir Lancelot, Merlin, Odin)
- **Legendary Flex** (1% chance, final town only): Mythic heroes (Thor, Dragon, Phoenix)

---

#### Static Spawns & Respawning (Farming System)

**Spawn Behavior**:
- **Static Placement**: Spawns don't move or patrol (future expansion: roaming enemies)
- **Visible on Map**: Once fog cleared, spawns show as red flag icons
- **Difficulty Indicators**: 
  - Gray flag = Easy (1-3 Common cards)
  - Green flag = Normal (3-5 Common/Uncommon)
  - Blue flag = Hard (5-8 Uncommon/Rare)
  - Purple flag = Elite (8-12 Rare/Epic)
  - Gold flag = Boss (15-25 Epic/Legendary)

**Respawn Timers**:
- **Easy Spawns**: Respawn after 1 hour (quick farming)
- **Normal Spawns**: Respawn after 3 hours
- **Hard Spawns**: Respawn after 6 hours
- **Elite Spawns**: Respawn after 12 hours
- **Boss**: Respawn after 24 hours (or only once per county instance)

**Why Respawning?**:
- ✅ **Farming**: Players can grind spawns for XP/gold/cards without progressing
- ✅ **Deck Testing**: Try new formations against known enemies
- ✅ **Casual Play**: Don't feel rushed to complete county in one session
- ✅ **AFK Grinding**: Set auto-battle, check back in 6 hours, spawns refreshed

**Farming Efficiency**:
- **Easy Spawn**: 50 XP, 100 gold, 10% chance Common card (1-hour respawn)
- **Normal Spawn**: 100 XP, 300 gold, 20% chance Uncommon (3-hour respawn)
- **Hard Spawn**: 200 XP, 800 gold, 30% chance Rare (6-hour respawn)
- **Elite Spawn**: 500 XP, 2,000 gold, 50% chance Epic (12-hour respawn)
- **Boss**: 2,000 XP, 10,000 gold, 100% Legendary card (24-hour respawn)

---

#### Minimum Battle Power (Optional Rule - TBD)

**Consideration**: Should there be a minimum stack strength to engage spawns?

**Option A: No Minimum** (Current Design):
- ✅ Single Scout card can engage any spawn
- ✅ Scouts reveal spawn composition before committing full army
- ✅ High-risk, high-reward (sacrifice scout for intel)
- ❌ Can feel "gamey" (suicide scouts for info)

**Option B: Minimum Battle Power Required**:
- Spawn shows "Power Level: 500" indicator
- Your stack must have combined HP+Attack ≥ 500 to engage
- Example: 1× Scout (HP:5, ATK:3) = 8 power → can't engage 500 power spawn
- Example: 10-card army (HP:150, ATK:50) = 200 power → can engage
- ✅ Prevents suicide scouts
- ❌ Less flexible, forces larger armies

**Recommended**: **Option A (No Minimum)** for launch, add Option B as difficulty modifier for Hard/Elite counties.

---

#### County Map Flow Summary

**Player Journey**:
1. **Enter County Map**: Full deck (15 cards) as single army stack on start tile
2. **Explore**: Move stack to reveal fog of war, discover spawns/resources/towns
3. **Engage Spawns**: Battle for XP/gold/cards, respawn for farming if desired
4. **Capture Resources**: Deploy economy cards (farms, mines, workers) to tiles
5. **Garrison Defense**: Leave 3-5 battle cards at key tiles to defend
6. **Split Army**: Divide main force from garrison/scouts as needed
7. **Recruit Flex Heroes**: Find towns, add temporary allies (up to 50 total cards)
8. **Buff Shrines**: Capture for permanent +10% stat boosts
9. **Find Boss**: Non-linear path, boss location varies
10. **Final Battle**: Zoom to battle map, deploy full army + flex heroes vs boss
11. **Victory**: Complete county, rewards (Legendary card, 10,000 XP, unlock next county)
12. **Global Map**: Return to global view, flex heroes removed, county marked complete

**Visual Flow**:
```
Global Map (Risk View)
    ↓ [Zoom into County Territory]
County Map (HoMM Strategic View)
  - Move army stacks
  - Split decks
  - Garrison tiles
  - Explore fog
  - Engage spawns
    ↓ [Engage Spawn]
Battle Map (HoMM Tactical View)
  - Deploy formation
  - Turn-based combat
  - Manual or auto-battle
    ↓ [Victory]
County Map (Return)
  - Continue exploration
  - Or complete boss and exit
```

---

### Visual Representation (3D Figures vs Card Sprites)

#### Rarity-Based Visual Styling

**Epic, Legendary, Mythic Cards** → **3D Miniature Figures**:
- **Model**: Detailed 3D character model (similar to tabletop miniatures)
- **Height**: 1.5-2x normal card height when placed on map
- **Animation**: Idle animations (breathing, weapon twirl, magic glow)
- **VFX**: Element-specific effects (fire hero has flame aura)
- **Collectibility**: Premium feel, showpiece units
- **Example**: Epic Thor = 3D Viking warrior with hammer, lightning crackling

**Rare Cards** → **Premium Card Sprites with Stand**:
- **Model**: 2D card sprite on small 3D stand/pedestal
- **Height**: 1.2x normal card height
- **Animation**: Gentle glow, card hovers slightly
- **VFX**: Border shimmer matching element color
- **Example**: Rare Fire Mage = glowing card standing upright on tile

**Common & Uncommon Cards** → **Flat Card Sprites**:
- **Model**: 2D card sprite lying flat or at slight angle
- **Height**: 1x normal card height
- **Animation**: Minimal (slight pulse on selection)
- **VFX**: None (performance optimization)
- **Example**: Common Archer = simple card sprite on tile

#### Stack Visual Representation

**How Stacks Appear on Map**:

**Small Stacks (2-3 cards)**:
- Display **lead card** (highest rarity in stack)
- Small badge showing stack count ("×3")
- Other cards appear as ghosted/faded copies behind lead

**Medium Stacks (4-6 cards)**:
- Display **lead card** prominently
- 2-3 other cards fanned behind in arc formation
- Stack count badge ("×6")
- Mixed 3D figures + card sprites if rarities mixed

**Large Stacks (7-10 cards)**:
- Display **top 3 cards** in formation
- Remaining cards shown as small icons in stack UI
- Click stack → opens detailed stack view
- Stack count badge ("×10") with glow effect

**Visual Example (5-Card Ranged Stack)**:
```
Front View on Map:
  [Epic Elf Archer 3D Figure] ← Lead card, largest
  [Uncommon Human Crossbow Sprite] ← Second card, medium
  [Common Archer Sprite] ← Third card, small
  [×5 Badge] ← Stack count indicator
  [Ranged Icon] ← Unit type indicator
```

#### Hover/Click Details

**Hover Over Stack** (Desktop):
- Tooltip shows all cards in stack
- Combined stats displayed
- Element type, unit type icons
- Quick actions: Move, Attack, Split Stack

**Click Stack** (Mobile/Desktop):
- Opens **Stack Detail Panel**:
  - List of all cards (with mini portraits)
  - Combined stats breakdown
  - Active buffs/debuffs
  - Formation position
  - Actions: Attack, Move, Use Ability, Split, Merge

**Split Stack Feature**:
- Right-click stack → "Split Stack"
- Drag slider to divide cards into 2 stacks
- Example: 10-card stack → split into 6-card + 4-card stacks
- Useful for spreading forces, avoiding AoE damage

---

### Leaderboards & Competitive Metrics

#### Event Leaderboards (Automated PvP Scoring)

**Formation-Based Auto-Battles**:
- Players register deck + formation
- System runs battles between all registered players (round-robin or Swiss)
- AI controls both sides using programmed tactics
- Results determine rankings

**Leaderboard Categories**:

**1. Most Damage in Single Turn**:
- Tracks highest damage dealt by one stack in one turn
- Encourages glass cannon builds (all attack, no defense)
- Rewards: Bonus gems, "Devastator" title

**2. Most Total Damage in Battle**:
- Cumulative damage across entire battle
- Favors sustained DPS over burst
- Rewards: Rare cards, "Destroyer" title

**3. Most Healing**:
- Total HP restored to allied units
- Encourages healer-focused decks
- Rewards: Healer-themed cosmetics, "Lifebringer" title

**4. Fastest Victory**:
- Lowest turn count to win
- Rewards aggressive, efficient strategies
- Rewards: Speed boost items, "Blitz" title

**5. Most Efficient (Damage per Card)**:
- Total damage ÷ number of cards deployed
- Rewards quality over quantity builds
- Rewards: Deck slots, "Tactician" title

**6. Tankiest Defense (Damage Absorbed)**:
- Total damage taken without dying
- Encourages defensive, high-HP builds
- Rewards: Defense equipment, "Immovable" title

**7. Best Formation Positioning**:
- AI judges terrain usage, unit spacing, synergies
- Rewards strategic placement
- Rewards: Formation slots, "Strategist" title

#### Alliance Competition

**Guild vs Guild Leaderboards**:
- Top 10 players per alliance contribute to alliance score
- Alliance with highest combined scores wins week
- Rewards: Alliance bonuses, exclusive alliance banners
- Encourages cooperation ("Let me take a support role so you can DPS")

**Weekly Themes**:
- **Week 1**: "Fire Week" (fire element cards get +20% stats, leaderboard for fire damage)
- **Week 2**: "Healer Week" (most healing wins)
- **Week 3**: "Speed Week" (fastest victories)
- **Week 4**: "Tank Week" (most damage absorbed)

**Why Variety Matters**:
- ✅ Prevents meta stagnation (different builds shine each week)
- ✅ Encourages deck diversity (can't use same deck every week)
- ✅ Rewards different playstyles (not just "who has most Legendaries")
- ✅ F2P competitive (strategy > card rarity for some categories)

---

### Map Generation (Pre-Set vs Procedural)

#### Map Types

**1. Pre-Set Campaign Maps** (HoMM Campaign Style):
- **Design**: Hand-crafted by developers
- **Features**: Unique terrain, scripted events, boss locations
- **Use Case**: Story campaign, tutorial, special events
- **Replayability**: Fixed layout, but different strategies/decks
- **Example**: "The Frozen Wastes" campaign map with ice obstacles

**2. Procedurally Generated Maps** (Diablo/Slay the Spire Style):
- **Design**: Algorithm creates unique map each time
- **Seed**: Random seed saved to database (players can share seeds)
- **Features**: Random terrain, resource node placement, neutral mobs
- **Use Case**: Daily missions, quick PvP, infinite replayability
- **Example**: "Daily Conquest" generates new map every 24 hours

**3. Player-Created Maps** (Future Feature):
- **Design**: Map editor for community
- **Features**: Place terrain, objectives, starting zones
- **Use Case**: Custom scenarios, alliance training grounds
- **Curation**: Best maps featured by developers

#### Generated Map Database

**How It Works**:
1. Event announced: "Weekly Tournament - Seed #47382"
2. Server generates map from seed, saves to database
3. All players get exact same map layout
4. Players deploy formations during setup phase
5. Battles resolve simultaneously
6. Map saved permanently (can replay historical events)

**Benefits**:
- ✅ **Fairness**: Everyone plays on same map
- ✅ **Skill Testing**: Can't memorize maps, must adapt
- ✅ **Replayability**: Infinite unique maps
- ✅ **Storage**: Save map data (not just seed) for tournaments

---

### Summary: Stacking, Formations & Deployment

| Aspect | Key Features | HoMM Inspiration | Modern Twist |
|--------|--------------|------------------|--------------|
| **Stacking** | 2-10 cards per tile, same unit type, cross-theme allowed | ✅ Army stacks | Cross-theme flexibility |
| **Formations** | 5 presets + custom editor, auto/manual placement | ✅ Hero armies | Party-based RPG templates |
| **Visual** | 3D figures (Epic+), card sprites (Common/Uncommon) | ✅ Unit figures | Rarity-based styling |
| **Maps** | Multi-tier zoom (Global→County→Battle) | ✅ Strategic→Tactical | Risk-style world map |
| **Deployment** | 1 deck per territory on Global, full deck in battle | ✅ Campaign heroes | Multiple deck management |
| **Events** | Setup days, auto-battles, leaderboards | ✅ PvP tournaments | Competitive metrics |

**Design Philosophy**: **Simplicity through automation, depth through customization**. Casual players use auto-deploy with presets, hardcore players manually place every stack for terrain advantage.

---

## 2.7 Card Data Model (Engine Schema)

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

**Design Philosophy**: **Hybrid Universal + Specialized Model**

Sovereign Territories uses a **3-tier pack system** inspired by best-in-class card games:
1. **Universal Packs** (default, like Pokemon TCG) - contain both Battle and Economy cards
2. **Specialized Boosters** (targeted progression) - focus on specific card types
3. **Premium Theme Packs** (themed collections) - element/faction-specific bundles

This balances **simplicity for new players** with **targeted progression for veterans**, while creating **diverse monetization options** without diluting card acquisition.

---

#### Tier 1: Universal Packs (Core Acquisition)

**Standard Pack** (Default pack for all rewards/purchases):
- **Contents**: 5 cards total
  - 3-4 Battle Cards (Heroes, Units, Tactics, Equipment)
  - 1-2 Economy Cards (Buildings, Workers)
- **Rarity Distribution**:
  - 3 Common/Uncommon (60% chance each)
  - 1 Rare or better (8% Rare, 1.5% Epic, 0.5% Legendary)
  - 1 Guaranteed Economy Card (any rarity, follows same odds)
- **Why This Works**:
  - ✅ **Pokemon-Style Familiarity**: Mix of card types in every pack
  - ✅ **Guaranteed Economy Cards**: Players always build economic foundation
  - ✅ **Simple Onboarding**: New players don't need to choose pack types
  - ✅ **Free-to-Play Path**: All content obtainable from one pack type

**Cost**:
- **Gold**: 1,000 gold per pack (earned via AFK production, quests)
- **Gems**: 100 gems per pack ($1 USD value)
- **Free Sources**: Daily login (1 per day), quest rewards (2-5 per week), alliance gifts

**Pity System** (Universal Packs):
- **Legendary Guarantee**: Every 50 packs without Legendary = guaranteed Legendary in pack 50
- **Epic Guarantee**: Every 10 packs without Epic = guaranteed Epic in pack 10
- **Counter Visible**: UI shows "Pity Counter: 12/50 packs" to build anticipation
- **Separate Trackers**: Battle and Economy pity counters are separate (prevents all-building Legendary packs)

---

#### Tier 2: Specialized Boosters (Targeted Progression)

**Purpose**: Allow players to focus on specific deck-building needs without diluting universal pack value.

**Battle Booster Pack**:
- **Contents**: 5 cards, **all Battle Cards**
  - No Economy Cards included
  - Increased Epic/Legendary rates (+50% chance)
  - Guaranteed 1 Rare or better
- **Rarity Distribution**:
  - 2 Common/Uncommon (60%)
  - 2 Rare (12% Epic, 2% Legendary)
  - 1 Guaranteed Rare+ (10% Epic, 3% Legendary)
- **Use Case**: 
  - Competitive players building tournament decks
  - Players who already have economy established
  - Targeting specific hero/unit synergies
- **Cost**:
  - 1,500 gold per pack (50% premium over Standard)
  - 150 gems per pack
  - **Not available for free** (premium option only)

**Economy Booster Pack**:
- **Contents**: 5 cards, **all Economy Cards**
  - No Battle Cards included
  - Guaranteed 1 Rare+ building or worker
  - Higher chance of Legendary buildings (2% vs 0.5%)
- **Rarity Distribution**:
  - 2 Common buildings/workers (Farms, Mines, Farmers, Miners)
  - 2 Uncommon buildings (Lumber Mills, Barracks, Turrets)
  - 1 Guaranteed Rare+ (12% Rare Fortress, 2.5% Epic Wonder, 0.5% Legendary Monument)
- **Use Case**:
  - Players expanding AFK production infrastructure
  - New castle setup (need 10-15 economy cards per territory)
  - Alliance members pooling resources for guild bases
- **Cost**:
  - 800 gold per pack (20% cheaper than Standard, economy focus)
  - 80 gems per pack
  - **Available as alliance reward** (guild treasury purchases)

**Why Separate Boosters?**:
- ✅ **Respect Player Time**: Veterans don't want economy cards when chasing Legendaries
- ✅ **New Player Safety**: Cheaper Economy Packs help establish AFK income early
- ✅ **Strategic Choice**: "Do I need heroes or buildings right now?"
- ✅ **Monetization Diversity**: Whales buy Battle Boosters, F2P grind Economy Packs

**Pity System** (Specialized Boosters):
- **Separate Pity Trackers**: Battle Booster pity ≠ Economy Booster pity ≠ Universal Pack pity
- **Battle Booster**: Guaranteed Legendary every 30 packs (vs 50 for Universal)
- **Economy Booster**: Guaranteed Legendary building every 40 packs
- **UI Display**: "Battle Pity: 12/30 | Economy Pity: 8/40 | Universal: 25/50"

---

#### Tier 3: Premium Theme Packs (Curated Collections)

**Purpose**: Themed bundles for specific playstyles, elements, or factions. High monetization potential with collector appeal.

**Element Theme Packs** (e.g., "Fire Dominion Pack", "Frost Legion Pack"):
- **Contents**: 10 cards, **all from one element**
  - 6-7 Battle Cards (Fire heroes, Fire units, Fire tactics)
  - 3-4 Economy Cards (Fire-themed buildings, workers)
  - **Guaranteed 1 Epic+ from theme** (e.g., Fire Dragon hero, Volcano building)
- **Rarity Distribution**:
  - 4 Common/Uncommon (theme-locked)
  - 4 Rare (theme-locked)
  - 2 Epic+ (1 Epic guaranteed, 10% chance for Legendary)
- **Use Case**:
  - Mono-element deck builders
  - Collectors completing element sets
  - New players choosing faction identity
- **Cost**:
  - 3,000 gold per pack (3× Standard, but guaranteed Epic+)
  - 300 gems per pack ($3 USD)
  - **Limited-Time**: Rotates weekly (Fire week, Water week, etc.)

**Faction Theme Packs** (e.g., "Norse Pantheon", "Medieval Knights", "Sci-Fi Mechs"):
- **Contents**: 15 cards, **all from one faction/theme**
  - 10 Battle Cards (Norse heroes: Thor, Odin, Loki + Viking warriors)
  - 5 Economy Cards (Longhouse, Blacksmith, Norse workers)
  - **Guaranteed 2 Epic+ from faction** (e.g., Thor + Valhalla building)
- **Rarity Distribution**:
  - 5 Common/Uncommon
  - 6 Rare
  - 4 Epic+ (2 Epic guaranteed, 20% for Legendary, 5% for Mythic)
- **Use Case**:
  - Thematic deck builders ("Pure Norse army")
  - Lore collectors
  - Event preparation (Norse-themed alliance wars)
- **Cost**:
  - **Premium Only**: $9.99 USD (cannot buy with gold)
  - **Limited Availability**: Monthly rotation, 48-hour flash sales
  - **Collector Value**: Exclusive alternate card art (same stats, unique visuals)

**Starter Theme Packs** (New Player Bundles):
- **Contents**: 30 cards, **pre-built synergistic deck**
  - 20 Battle Cards (balanced hero + units + tactics)
  - 10 Economy Cards (starter buildings for AFK income)
  - **Guaranteed 1 Legendary hero** (choose from 3: Thor, Fire Mage, or Knight)
  - **Guaranteed 3 Epic units** matching hero element
- **Rarity Distribution**:
  - 1 Legendary hero (choice)
  - 3 Epic units (synergistic)
  - 10 Rare cards (support)
  - 16 Common/Uncommon (filler)
- **Use Case**:
  - **One-Time Purchase**: New players skip grinding, jump straight to competitive decks
  - **Catch-Up Mechanic**: Returning players after hiatus
- **Cost**:
  - **$19.99 USD** (one-time offer, first 7 days only)
  - **Best Value**: Equivalent to 200 Standard Packs worth of curated cards

**Seasonal Event Packs** (Limited-Time):
- **Contents**: 8 cards, **event-exclusive cards**
  - 5 Battle Cards (Halloween-themed heroes, Christmas units, etc.)
  - 3 Economy Cards (Haunted Farm, Santa's Workshop, etc.)
  - **Guaranteed 1 Event-Exclusive Legendary** (cannot obtain elsewhere)
- **Rarity Distribution**:
  - 1 Event Legendary (100% exclusive)
  - 2 Event Epic (exclusive variants)
  - 5 Event Rare/Common (cosmetic reskins of existing cards)
- **Use Case**:
  - **FOMO Monetization**: "Get this before it's gone forever!"
  - **Collector Prestige**: Show off exclusive holiday cards
  - **Seasonal Meta**: Event cards have thematic bonuses (e.g., Halloween cards +20% power in October)
- **Cost**:
  - 5,000 gold per pack (expensive, limited stock per player)
  - 500 gems per pack ($5 USD)
  - **Max 10 packs per player per event** (prevents hoarding)

---

#### Pack Comparison Table

| Pack Type | Cards | Battle:Economy Ratio | Epic+ Rate | Cost (Gold) | Cost (Gems) | Best For |
|-----------|-------|----------------------|------------|-------------|-------------|----------|
| **Standard (Universal)** | 5 | 3-4:1-2 | 2% | 1,000g | 100 | F2P daily grind, new players |
| **Battle Booster** | 5 | 5:0 | 5% | 1,500g | 150 | Competitive PvP, hero chasers |
| **Economy Booster** | 5 | 0:5 | 3% | 800g | 80 | AFK income builders, new castles |
| **Element Theme** | 10 | 6-7:3-4 | 20% | 3,000g | 300 | Mono-element decks, collectors |
| **Faction Theme** | 15 | 10:5 | 30% | N/A | $9.99 | Thematic decks, lore fans |
| **Starter Bundle** | 30 | 20:10 | 50% | N/A | $19.99 | New players (one-time) |
| **Seasonal Event** | 8 | 5:3 | 100% | 5,000g | 500 | Collectors, FOMO |

---

#### Why This System Works

**For New Players**:
- ✅ **Simple Default**: Standard Packs are the "training wheels" (like Pokemon booster packs)
- ✅ **Guaranteed Economy**: Every pack has buildings, so you always build AFK income
- ✅ **Accessible**: Can earn 7-10 Standard Packs per week F2P (daily login + quests)

**For Mid-Game Players**:
- ✅ **Strategic Choice**: "I need heroes" → Battle Booster, "I need economy" → Economy Booster
- ✅ **Gold Efficiency**: Economy Packs are cheaper (800g vs 1,000g), better for resource management
- ✅ **Thematic Identity**: Element/Faction packs let you commit to playstyle

**For Whales/Collectors**:
- ✅ **Premium Options**: Faction Theme Packs ($9.99) and Seasonal Event Packs (exclusive Legendaries)
- ✅ **FOMO Monetization**: Limited-time packs drive impulse purchases
- ✅ **Prestige**: Exclusive card art, alternate cosmetics

**For Developers**:
- ✅ **Diverse Monetization**: 7 pack types = 7 price points = broader revenue capture
- ✅ **Controlled Economy**: Separate pity systems prevent exploit (can't game one pack type)
- ✅ **Event Flexibility**: Seasonal packs drive retention spikes every quarter
- ✅ **Analytics-Friendly**: Track which pack types sell best, adjust drop rates per pack

---

#### Pack Opening Experience (Visual Design)

**Standard Pack Opening**:
1. Player taps pack in inventory
2. Pack expands with element-themed animation (fire = flames, water = ripples)
3. Cards flip one-by-one with rarity reveal:
   - **Common**: Matte glow, soft chime
   - **Rare**: Holographic shimmer, brighter chime
   - **Epic**: Particle burst, epic orchestra swell
   - **Legendary**: Screen flash, radiant beam of light, choir fanfare
4. Final card "lingers" in center (if Legendary, camera zooms in dramatically)
5. "Tap to continue" → cards added to collection

**Multi-Pack Opening** (Batch Mode):
- **Skip Animations**: Open 10 packs at once, instant results screen
- **Highlight Legendaries**: Auto-pause on Legendary cards for dopamine hit
- **Summary**: "You got 2 Legendaries, 8 Epics, 25 Rares!"

**VIP Perks**:
- **VIP 3+**: Can batch-open up to 10 packs at once
- **VIP 5**: "Instant Open" button (skip all animations, jump to results)

---

### Visuals

Animated pack openings with VFX (described above).

**Pack Art Design**:
- **Standard Pack**: Neutral silver/gold with Sovereign Territories logo
- **Battle Booster**: Red/orange with crossed swords emblem
- **Economy Booster**: Green/brown with coin stack emblem
- **Element Theme**: Color-coded (Fire = red flames, Water = blue waves, etc.)
- **Faction Theme**: Unique art per faction (Norse = runes, Medieval = castle, Sci-Fi = circuits)
- **Seasonal Event**: Holiday-themed (Halloween = pumpkin, Christmas = snowflake)

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

---

# SECTION 5.5: RESOURCE ECONOMY & CURRENCY SYSTEMS

## 5.5.1 Currency Overview

**Core Philosophy**: Multiple currencies prevent whale dominance (can't buy everything with real money) and create diverse progression paths (PvP skill, AFK patience, exploration, grinding).

**Currency Types**:
1. **Gold** (Soft currency - earned through gameplay)
2. **Gems** (Premium currency - bought with real money or earned slowly)
3. **Food** (Resource - AFK gathering, exploration)
4. **Lumber** (Resource - AFK gathering, exploration)
5. **Ore** (Resource - AFK gathering, exploration)
6. **Arena Tokens** (PvP currency - ranked match rewards only)
7. **Energy** (Stamina - battle cost, prevents grinding)

**No "Coins" Separate Currency**: Real money purchases use Gems directly (simplicity, no conversion confusion).

---

## 5.5.2 Gold (Soft Currency)

**Definition**: Primary earned currency for card collection and progression.

**Sources** (How Players Earn Gold):
- **Battle Victory**: 50-200 Gold per battle (scales with difficulty)
- **Tutorial Rewards**: 4,500 Gold total (tutorial completion)
- **Daily Login**: 100-500 Gold (Day 1-28 progression)
- **Weekly Quests**: 500 Gold per quest (5/7 quests = 2,500 Gold/week)
- **AFK Production**: Economy buildings generate 10-100 Gold/hour (Granary, Sawmill, Mine)
- **Alliance Donations**: Other members can gift Gold (100-1,000 per donation)
- **Achievements**: 1,000-5,000 Gold for milestones (first Legendary, 100 battles won, etc.)
- **Seasonal Events**: 2,000-10,000 Gold for event completion
- **Selling Cards**: Duplicate cards → Gold (Common: 10 Gold, Legendary: 1,000 Gold)

**Sinks** (How Players Spend Gold):
- **Pack Purchases**: 
  - Standard Pack: 1,000 Gold (5 random cards)
  - Element Booster: 1,500 Gold (5 cards, 80% element match)
  - Epic Booster: 3,000 Gold (5 cards, guaranteed Epic)
  - Game Deck: 50,000 Gold (50 cards, 1 Legendary, 2-3 Epics, 1/week limit)
- **Card Combining**: 
  - +1 Star: 100 Gold + 2 duplicate cards (Common → 1★ Uncommon)
  - +2 Stars: 500 Gold + 4 duplicate cards (Uncommon → 2★ Rare)
  - +3 Stars: 2,000 Gold + 8 duplicate cards (Rare → 3★ Epic)
  - +4 Stars: 10,000 Gold + 16 duplicate cards (Epic → 4★ Legendary)
  - +5 Stars: 50,000 Gold + 32 duplicate cards (Legendary → 5★ Mythic)
- **Building Upgrades**:
  - Granary Level 2: 500 Gold (increases Food production +20%)
  - Sawmill Level 2: 500 Gold (increases Lumber production +20%)
  - Mine Level 2: 500 Gold (increases Ore production +20%)
- **Name Change**: 100 Gold (first change free, subsequent changes cost Gold)
- **Speed-Ups**: 50 Gold per hour (speed up building retrieval, card combining timers)
- **Resource Trading**: 1,000 Gold → 500 Food/Lumber/Ore (emergency conversion)

**Earn Rate vs Spend Rate** (F2P Balance):
- **F2P Player**: ~3,000 Gold/week (daily login + quests + battles)
- **Spending Goal**: 1 Standard Pack/day (7,000 Gold/week) OR save for Game Deck (50k Gold = 16 weeks)
- **Result**: F2P players can buy 3-4 packs/week with Gold, requires choices (packs vs upgrades)

---

## 5.5.3 Gems (Premium Currency)

**Definition**: Premium currency for premium content, shortcuts, and exclusive packs.

**Sources** (How Players Earn Gems):
- **Real Money Purchases**:
  - Starter Pack: $4.99 = 500 Gems (one-time purchase)
  - Small Pack: $4.99 = 500 Gems (5/week limit)
  - Medium Pack: $9.99 = 1,100 Gems (3/week limit, 10% bonus)
  - Large Pack: $19.99 = 2,500 Gems (1/week limit, 25% bonus)
  - Battle Pass: $4.99 = 1,000 Gems over 30 days (Tier 1-40 rewards, 1/month limit)
- **Free Gem Sources**:
  - Daily Login: 10-50 Gems (Day 7, 14, 21, 28 bonus days)
  - Achievements: 50-500 Gems (first Epic pull, 50 battles won, etc.)
  - Weekly Quests: 100 Gems per 7/7 quest completion (encourages consistency)
  - Alliance Wars: 200-1,000 Gems for winning alliance (monthly season rewards)
  - Seasonal Events: 500-2,000 Gems for event completion

**Earn Rate** (Free Gems):
- **F2P Player**: ~500 Gems/month (daily login + weekly quests + achievements)
- **Active Player**: ~1,000 Gems/month (adds alliance wars + events)
- **Whale**: Unlimited (real money purchases, $136/week max)

**Sinks** (How Players Spend Gems):
- **Premium Packs**:
  - Premium Standard Pack: 100 Gems (5 cards, 10% shiny rate, 10/week limit)
  - Premium Element Booster: 150 Gems (5 cards, element match, 10% shiny, 5/week limit)
  - Premium Epic Booster: 300 Gems (5 cards, guaranteed Epic, 10% shiny, 3/week limit)
  - Shiny Guaranteed Pack: 1,000 Gems (5 cards, 100% shiny, 1/week limit)
- **Energy Refills**: 50 Gems per refill (restores max Energy, unlimited purchases)
- **Instant Speed-Ups**: 100 Gems per instant completion (building retrieval, card combining)
- **VIP Pass**: $4.99/month = auto-buy for 500 Gems (daily bonuses: +10% Gold, +10% XP, +1 Energy refill/day)
- **Cosmetic Items**:
  - Card Backs: 200-500 Gems (visual customization for deck)
  - Battle Emotes: 100-300 Gems (chat expressions during PvP)
  - Hero Skins: 500-1,000 Gems (alternate art for Legendary heroes)

**Spending Comparison**:
- **F2P Player**: 500 Gems/month → 5 Premium Standard Packs OR 1 Energy refill/day for 10 days
- **Whale**: $136/week → 14,400 Gems/month → 10 Premium Standard + 5 Premium Element + 3 Premium Epic + 1 Shiny Guaranteed + leftover for refills

---

## 5.5.4 Food (AFK Resource)

**Definition**: Consumable resource for unit maintenance and battle entry costs.

**Sources** (How Players Earn Food):
- **AFK Production** (Auto-Collected):
  - Granary: 10 Food/hour (Level 1), 20 Food/hour (Level 2), 40 Food/hour (Level 3)
  - Farm: 50 Food/hour (Level 1), 100 Food/hour (Level 2), 200 Food/hour (Level 3)
  - **Auto-Collection**: Resources accumulate up to storage capacity, then stop
  - **Storage Capacity**: 1,000 Food (Level 1 storage), 5,000 (Level 2), 20,000 (Level 3)
  - **No Tapping Required**: Check in when you want to spend, not to collect
- **Battle Rewards**: 20-100 Food per battle chest (bronze/silver/gold tier)
- **Exploration**: County Map resource nodes (100-500 Food per node, respawns daily)
- **Daily Login**: 500-2,000 Food (Day 7, 14, 21, 28 bonus days)
- **Alliance Donations**: Members can gift Food (100-1,000 per donation)
- **Gold Trading**: 1,000 Gold → 500 Food (emergency conversion)

**Production Rate** (AFK Gathering):
- **Early Game** (1 Granary Level 1): 240 Food/day (10/hour × 24 hours)
- **Mid Game** (2 Granaries Level 2 + 1 Farm Level 1): 2,160 Food/day
- **Late Game** (3 Granaries Level 3 + 2 Farms Level 3): 7,680 Food/day

**Sinks** (How Players Spend Food):
- **Battle Entry Cost**: 20 Food per battle (prevents grinding, encourages AFK production)
- **Unit Deployment**: 50 Food per unit deployed on County Map (stack of 5 units = 250 Food)
- **Building Upgrades**:
  - Granary Level 2: 500 Food (ironic sink: spend Food to make more Food)
  - Farm Level 2: 1,000 Food
  - Mine Level 2: 300 Food (miners need to eat)
- **Card Combining**: 100 Food per combine (represents feeding units during training)
- **Resource Trading**: 500 Food → 1,000 Gold (sell surplus for Gold)

**Consumption vs Production**:
- **20 Food/battle**: Player with 2,160 Food/day can fight 108 battles/day (unrealistic due to Energy limits)
- **Energy System**: Caps battles at ~24/day (480 Food/day consumption)
- **Result**: Food accumulates naturally, players rarely run out (AFK progression)

---

## 5.5.5 Lumber (AFK Resource)

**Definition**: Crafting resource for equipment, building construction, and upgrades.

**Sources** (How Players Earn Lumber):
- **AFK Production** (Auto-Collected):
  - Sawmill: 10 Lumber/hour (Level 1), 20 Lumber/hour (Level 2), 40 Lumber/hour (Level 3)
  - Forest: 50 Lumber/hour (Level 1), 100 Lumber/hour (Level 2), 200 Lumber/hour (Level 3)
  - **Auto-Collection**: Resources accumulate up to storage capacity, then stop
  - **Storage Capacity**: 1,000 Lumber (Level 1 storage), 5,000 (Level 2), 20,000 (Level 3)
  - **No Tapping Required**: Check in when you want to spend, not to collect
- **Battle Rewards**: 20-100 Lumber per battle chest (bronze/silver/gold tier)
- **Exploration**: County Map resource nodes (100-500 Lumber per node, respawns daily)
- **Daily Login**: 500-2,000 Lumber (Day 7, 14, 21, 28 bonus days)
- **Alliance Donations**: Members can gift Lumber (100-1,000 per donation)
- **Gold Trading**: 1,000 Gold → 500 Lumber (emergency conversion)

**Production Rate** (AFK Gathering):
- **Early Game** (1 Sawmill Level 1): 240 Lumber/day
- **Mid Game** (2 Sawmills Level 2 + 1 Forest Level 1): 2,160 Lumber/day
- **Late Game** (3 Sawmills Level 3 + 2 Forests Level 3): 7,680 Lumber/day

**Sinks** (How Players Spend Lumber):
- **Equipment Crafting**:
  - Wooden Shield: 100 Lumber (+2 Health for equipped hero)
  - Hunting Bow: 200 Lumber (+1 Attack, +1 Range for equipped hero)
  - Siege Ladder: 500 Lumber (tactical item, allows wall climbing in battles)
- **Building Construction**:
  - Deploy new economy building: 300 Lumber (one-time cost per building)
  - Sawmill: 500 Lumber (ironic: spend Lumber to build Lumber factory)
  - Farm: 400 Lumber (wooden barn construction)
- **Building Upgrades**:
  - Sawmill Level 2: 500 Lumber
  - Forest Level 2: 1,000 Lumber
  - Granary Level 2: 300 Lumber (wooden storage expansion)
- **Card Combining**: 50 Lumber per combine (building training dummies, wooden targets)
- **Resource Trading**: 500 Lumber → 1,000 Gold (sell surplus for Gold)

**Usage Pattern**:
- **Early Game**: Spend on equipment (Wooden Shield, Hunting Bow)
- **Mid Game**: Spend on building construction (deploy more economy buildings)
- **Late Game**: Spend on upgrades (Level 3 buildings for max production)

---

## 5.5.6 Ore (AFK Resource)

**Definition**: Advanced crafting resource for high-tier equipment and building upgrades.

**Sources** (How Players Earn Ore):
- **AFK Production** (Auto-Collected):
  - Mine: 5 Ore/hour (Level 1), 10 Ore/hour (Level 2), 20 Ore/hour (Level 3)
  - Quarry: 25 Ore/hour (Level 1), 50 Ore/hour (Level 2), 100 Ore/hour (Level 3)
  - **Auto-Collection**: Resources accumulate up to storage capacity, then stop
  - **Storage Capacity**: 500 Ore (Level 1 storage), 2,500 (Level 2), 10,000 (Level 3)
  - **No Tapping Required**: Check in when you want to spend, not to collect
- **Battle Rewards**: 10-50 Ore per battle chest (bronze/silver/gold tier)
- **Exploration**: County Map resource nodes (50-250 Ore per node, respawns daily)
- **Daily Login**: 250-1,000 Ore (Day 7, 14, 21, 28 bonus days)
- **Alliance Donations**: Members can gift Ore (50-500 per donation)
- **Gold Trading**: 1,000 Gold → 250 Ore (emergency conversion, expensive)

**Production Rate** (AFK Gathering):
- **Early Game** (1 Mine Level 1): 120 Ore/day
- **Mid Game** (2 Mines Level 2 + 1 Quarry Level 1): 1,080 Ore/day
- **Late Game** (3 Mines Level 3 + 2 Quarries Level 3): 3,840 Ore/day

**Sinks** (How Players Spend Ore):
- **Equipment Crafting**:
  - Iron Sword: 200 Ore (+3 Attack for equipped hero)
  - Iron Armor: 300 Ore (+5 Health for equipped hero)
  - Steel Shield: 500 Ore (+3 Health, +1 Defense for equipped hero)
  - Mythic Weapon: 2,000 Ore (+5 Attack, +2 Range, Legendary-tier equipment)
- **Building Upgrades**:
  - Mine Level 2: 500 Ore
  - Quarry Level 2: 1,000 Ore
  - Granary Level 3: 200 Ore (stone foundation)
  - Sawmill Level 3: 200 Ore (steel saw blades)
- **Card Combining**: 25 Ore per combine (forging stronger units)
- **Resource Trading**: 250 Ore → 1,000 Gold (sell surplus for Gold)

**Scarcity Design**:
- **Ore is Rare**: Slowest production rate (120 Ore/day vs 240 Food/Lumber)
- **High-Value Sinks**: Mythic equipment costs 2,000 Ore (17 days of production for 1 item)
- **Result**: Players must choose (upgrade buildings OR craft equipment, can't do both)

---

## 5.5.7 Arena Tokens (PvP Currency)

**Definition**: Exclusive currency earned from ranked PvP matches, usable only in PvP Store.

**Sources** (How Players Earn Arena Tokens):
- **Ranked Match Victory**: 10-50 Tokens (scales with bracket: Bronze = 10, Mythic = 50)
- **Ranked Match Loss**: 5 Tokens (participation reward, encourages trying)
- **Weekly Ranking Rewards**:
  - Top 100: 500 Tokens
  - Top 10: 1,000 Tokens
  - Rank 1: 2,000 Tokens
- **Alliance War Victory**: 200-500 Tokens for winning alliance
- **Seasonal Ranked Rewards**: 1,000-5,000 Tokens at season end (resets monthly)

**Earn Rate**:
- **Casual Player**: 5 matches/week × 10 Tokens = 50 Tokens/week
- **Active Player**: 20 matches/week × 20 Tokens = 400 Tokens/week
- **Competitive Player**: 50 matches/week × 30 Tokens + weekly ranking = 2,000+ Tokens/week

**Sinks** (How Players Spend Arena Tokens):
- **PvP-Exclusive Packs**:
  - Arena Champion Pack: 500 Tokens (5 cards, guaranteed Rare, PvP-themed cards only)
  - Gladiator Booster: 1,000 Tokens (5 cards, guaranteed Epic, PvP-exclusive Epics)
- **PvP-Exclusive Cards**:
  - Arena Champion Hero: 2,000 Tokens (Legendary hero, only obtainable in PvP Store)
  - Tournament Tactician: 500 Tokens (Epic support card, PvP utility focus)
- **Cosmetic Items**:
  - Arena Title Badge: 200-500 Tokens ("Gladiator", "Duelist", "Champion" titles)
  - Ranked Card Back: 1,000 Tokens (exclusive card back for ranked players)
  - Victory Emote: 300 Tokens (special emote for PvP matches)

**Store Separation**:
- **Cannot Buy with Gold/Gems**: Arena Tokens only obtainable through PvP
- **Cannot Trade**: Arena Tokens are account-bound (prevents farming on alt accounts)
- **Result**: PvP players have exclusive content (rewards skill, not spending)

---

## 5.5.8 Energy (Stamina System)

**Definition**: Stamina resource that limits battles per day, prevents endless grinding, encourages AFK progression.

**Core Mechanics**:
- **Max Energy**: Based on Player Level
  - Level 1-10: 100 Max Energy
  - Level 11-20: 150 Max Energy
  - Level 21-30: 200 Max Energy
  - Level 31+: 250 Max Energy
- **Battle Cost**: 
  - Tutorial Campaign: 0 Energy (unlimited battles, no interruption)
  - County Map Battle: 10 Energy per battle
  - Random Campaign: 10 Energy per battle
  - Boss Battle: 20 Energy
  - Alliance War: 0 Energy (alliance events are unlimited during war periods)
- **Refill Rate**: 1 Energy per 6 minutes (10 Energy/hour, 240 Energy/day)
- **Daily Battle Limit**: 
  - Free Player: 24 battles/day (240 Energy refill / 10 per battle)
  - With Refills: Unlimited (Gem refills allow more battles, but Food cost still limits)

**Refill Options**:
- **Wait**: Free, 1 Energy per 6 minutes (natural refill)
- **Gem Refill**: 50 Gems per full refill (instant, unlimited purchases)
- **Level-Up**: Full Energy refill on level-up (automatic, incentivizes progression)
- **VIP Pass**: +1 free Energy refill/day ($4.99/month perk)

**Tutorial Exception**:
- **Campaign Energy**: 0 Energy cost (players can complete tutorial without stopping)
- **Introduction**: Step 23 (after first battle victory) → Tooltip: "Future battles cost Energy, but the campaign is free!"
- **Post-Tutorial**: County Map battles cost 10 Energy (players learn mechanic without blocking tutorial)

**Design Philosophy**:
- **Prevents Grinding**: Can't farm 1,000 battles on day 1 (limits F2P hardcore grinders)
- **Encourages AFK**: Natural refill (240 Energy/day) = 24 battles/day = incentivizes checking in multiple times
- **Whale Option**: Gem refills (50 Gems × 10 refills = 500 Gems/day = $5/day) = 240 extra battles/day
- **Food Gating**: Even with infinite Energy refills, Food cost (20 Food/battle) limits battles to ~380/day (7,680 Food production / 20 per battle)

**Energy vs Food Balance**:
- **Energy Limits**: 24 battles/day (free)
- **Food Limits**: 380 battles/day (max production)
- **Result**: Energy is primary gate (Food rarely runs out), whales can spend Gems for 10× more battles

---

## 5.5.9 County Map Movement System

**Definition**: Turn-based movement for deployed card stacks on County Map, limits exploration pacing.

**Core Mechanics**:
- **Movement Range**: 3 tiles per turn (hex-based County Map)
- **Turn Cost**: 1 Movement Point per turn
- **Max Movement Points**: 10 per day (resets at midnight UTC)
- **Movement Point Refill**: None (daily cap only, cannot refill with Gems)

**Movement Rules**:
- **Deployed Stack**: Player deploys hero + units on County Map (Step 12 of tutorial)
- **Each Turn**: Player can move stack up to 3 tiles in any direction
- **Obstacles**: Rivers, mountains block movement (must path around)
- **Enemy Tiles**: Moving onto enemy tile triggers battle (costs 10 Energy + 20 Food + 1 Movement Point)
- **Resource Nodes**: Moving onto resource node collects resources (100-500 Food/Lumber/Ore, costs 1 Movement Point)

**Daily Exploration Limit**:
- **10 Movement Points**: Can move 30 tiles/day (3 tiles × 10 turns)
- **County Map Size**: 40 tiles total (can explore 75% of map in 1 day if straight line)
- **Realistic Exploration**: Obstacles, battles, backtracking = 5-7 days to fully explore 1 County Map
- **Result**: Exploration is paced, can't blitz entire map in 1 session

**Tutorial Integration**:
- **Step 12**: Deploy first stack, move 3 tiles to PvE enemy (costs 1 Movement Point)
- **Step 13**: Battle PvE enemy, win, return to starting tile (costs 1 Movement Point to return)
- **Tooltip**: "You have 10 Movement Points per day. Plan your route carefully!"
- **Post-Tutorial**: Full County Map unlocked (40 tiles, 10 Movement Points/day = 4 days to fully explore)

**No Gem Refills** (Intentional):
- **Energy**: Can refill with Gems (whale advantage for battles)
- **Movement Points**: Cannot refill (prevents whales from exploring entire map instantly)
- **Result**: Exploration is time-gated for everyone (F2P and whales explore at same pace)

**Alliance Coordination**:
- **Shared Map**: Alliance members share County Map progress (if one member explores tile, all see it)
- **Coordination**: Members can split exploration (Member A goes north, Member B goes south)
- **Result**: Alliances explore faster collectively (10 members × 10 Movement Points = 100 tiles/day)

---

## 5.5.10 Store Separation

**Philosophy**: Three distinct stores prevent currency confusion and create exclusive progression paths.

---

### Pack Store (Gold & Gems)

**Purpose**: Card collection, pack opening, deck building.

**Currency**: Gold (unlimited purchases) or Gems (weekly limits).

**Items Available**:

**Standard Packs** (Always Available):
- Standard Pack: 1,000 Gold OR 100 Gems (5 random cards, 1% shiny, unlimited Gold purchases, 10 Premium/week)
- Element Booster: 1,500 Gold OR 150 Gems (5 cards, 80% element match, unlimited Gold, 5 Premium/week)
- Epic Booster: 3,000 Gold OR 300 Gems (5 cards, guaranteed Epic, unlimited Gold, 3 Premium/week)
- Shiny Guaranteed Pack: 1,000 Gems ONLY (5 cards, 100% shiny, 1/week limit)

**Theme Packs** (Rotating Weekly):
- Viking Conquest Pack: 2,000 Gold OR 200 Gems (5 cards, Norse theme, guaranteed Rare)
- Roman Legion Pack: 2,000 Gold OR 200 Gems (5 cards, Roman theme, guaranteed Rare)
- Elemental Chaos Pack: 2,500 Gold OR 250 Gems (5 cards, pure Fire/Water/Earth/Air, guaranteed Epic)
- Seasonal Event Pack: 3,000 Gold OR 300 Gems (5 cards, limited-time event theme, guaranteed Epic)

**Game Decks** (Expansion Content):
- Starter Game Deck: 50,000 Gold OR $19.99 (50 cards, 1 Legendary, 2-3 Epics, 1/week limit)
- Norse Mythology Deck: 75,000 Gold OR $29.99 (50 cards, Norse theme, 2 Legendaries, expansion)
- Roman Empire Deck: 75,000 Gold OR $29.99 (50 cards, Roman theme, 2 Legendaries, expansion)
- Mythic Realms Deck: 100,000 Gold OR $49.99 (75 cards, fantasy theme, 3 Legendaries, premium expansion)

**Store UI**:
- **Tab 1: Earn with Gold** (Standard, Element, Epic Boosters - unlimited purchases)
- **Tab 2: Premium Packs** (Gem purchases with weekly limits displayed: "10/10 this week")
- **Tab 3: Theme Packs** (Rotating weekly, preview next week's theme)
- **Tab 4: Game Decks** (Expansion content, preview future decks)

---

### Resource Store (Food, Lumber, Ore)

**Purpose**: Trade surplus resources for items, convert between resource types, emergency Gold purchases.

**Currency**: Food, Lumber, Ore (no Gold/Gems required).

**Items Available**:

**Resource Trading** (Always Available):
- 500 Food → 1,000 Gold (sell surplus Food)
- 500 Lumber → 1,000 Gold (sell surplus Lumber)
- 250 Ore → 1,000 Gold (sell surplus Ore, higher value)
- 1,000 Gold → 500 Food/Lumber/Ore (emergency conversion, expensive)
- 500 Food → 250 Lumber (resource swap)
- 500 Lumber → 250 Ore (resource swap)

**Equipment Blueprints** (Unlock Crafting):
- Wooden Shield Blueprint: 300 Lumber (unlocks crafting recipe)
- Hunting Bow Blueprint: 500 Lumber
- Iron Sword Blueprint: 500 Ore
- Iron Armor Blueprint: 800 Ore
- Steel Shield Blueprint: 1,200 Ore
- Mythic Weapon Blueprint: 5,000 Ore (Legendary-tier equipment)

**Building Blueprints** (Unlock New Buildings):
- Farm Blueprint: 1,000 Food (unlocks Farm deployment)
- Forest Blueprint: 1,000 Lumber (unlocks Forest deployment)
- Quarry Blueprint: 1,000 Ore (unlocks Quarry deployment)
- Advanced Granary Blueprint: 2,000 Food (unlocks Level 3 upgrade)

**Consumable Items**:
- Energy Potion: 500 Food (restores 50 Energy, emergency refill without Gems)
- Movement Scroll: 1,000 Lumber (+3 Movement Points, one-time use)
- Battle Banner: 500 Ore (+5% Attack for all units in next battle, one-time use)

**Store UI**:
- **Tab 1: Trading** (Resource conversions: Food/Lumber/Ore ↔ Gold)
- **Tab 2: Blueprints** (Equipment and building recipes)
- **Tab 3: Consumables** (Energy potions, movement scrolls, battle items)

---

### PvP Store (Arena Tokens Only)

**Purpose**: Exclusive rewards for ranked PvP players, encourages competitive play.

**Currency**: Arena Tokens (cannot use Gold/Gems/resources).

**Items Available**:

**PvP-Exclusive Packs**:
- Arena Champion Pack: 500 Tokens (5 cards, guaranteed Rare, PvP-themed cards)
- Gladiator Booster: 1,000 Tokens (5 cards, guaranteed Epic, PvP-exclusive Epics)
- Mythic Arena Pack: 5,000 Tokens (10 cards, 1 Legendary, best PvP cards)

**PvP-Exclusive Cards** (Cannot Get from Other Packs):
- Arena Champion (Legendary Hero): 2,000 Tokens (Fire element, 40 Attack/50 Health, PvP-focused abilities)
- Tournament Tactician (Epic Unit): 500 Tokens (Support unit, +10% Attack to all allies in PvP)
- Duelist's Blade (Epic Equipment): 800 Tokens (+5 Attack, +1 Range, PvP-only equipment)

**Cosmetic Items**:
- Arena Title Badge: 200-500 Tokens ("Gladiator", "Duelist", "Champion", "Legend" titles, display in profile)
- Ranked Card Back: 1,000 Tokens (exclusive card back, shows rank tier: Bronze/Silver/Gold/Mythic)
- Victory Emote Pack: 300 Tokens (5 emotes: "Good Game", "Well Played", "Oops", "Thinking", "GG")
- Mythic Frame: 2,000 Tokens (golden animated border for profile, prestige item)

**Seasonal Exclusives** (Reset Monthly):
- Season 1 Champion Card: 3,000 Tokens (limited-time Legendary, only in Season 1)
- Season 1 Emote: 500 Tokens (limited-time cosmetic, never available again)

**Store UI**:
- **Tab 1: Packs** (Arena Champion, Gladiator Booster, Mythic Arena Pack)
- **Tab 2: Cards** (PvP-exclusive Legendaries, Epics, Equipment)
- **Tab 3: Cosmetics** (Titles, card backs, emotes, frames)
- **Tab 4: Seasonal** (Limited-time items, resets monthly)

---

## 5.5.11 Reward Variety & Splash Moments

**Philosophy**: Three distinct reward types (chests, packs, resources) create varied progression and maintain engagement.

---

### Battle Chests (Immediate Gratification)

**Definition**: Loot boxes earned from battle victories, opened immediately for Gold/XP/cards/resources.

**Chest Tiers** (Based on Battle Difficulty):
- **Bronze Chest** (Easy PvE): 50-100 Gold, 100-200 XP, 20-50 Food/Lumber/Ore, 10% chance for Common card
- **Silver Chest** (Medium PvE/PvP): 100-200 Gold, 200-400 XP, 50-100 Food/Lumber/Ore, 30% chance for Uncommon card
- **Gold Chest** (Hard PvE/Boss): 200-500 Gold, 400-800 XP, 100-200 Food/Lumber/Ore, 50% chance for Rare card, 5% chance for Epic card

**Opening Animation**:
1. Chest appears on Victory Screen (bronze/silver/gold glow)
2. Tap to open → Chest lid flips open with particle effects
3. Contents pop out sequentially: Gold counter animates (+150!), XP bar fills, resources fly to HUD, card flips if present
4. Total duration: 3-5 seconds (quick but satisfying)

**Tutorial Integration**:
- **Step 23**: First battle victory → Bronze Chest (50 Gold, 100 XP, 20 Food, Common card)
- **Tooltip**: "You earned a Battle Chest! Tap to open your rewards."
- **Post-Tutorial**: All battles drop chests (tier scales with difficulty)

---

### Pack Opening (Collector Appeal)

**Definition**: Card packs purchased from Pack Store, opened with 5-card reveal animation.

**Opening Animation** (Already Defined):
1. Pack appears on screen (Standard/Element/Epic/Shiny visual)
2. Tap to open → Pack tears open, cards fly out
3. Cards flip one-by-one: 1 sec per card (Common/Uncommon/Rare), 3 sec for Epic/Legendary (dramatic reveal)
4. Shiny reveal: Golden aura, animated shimmer, special sound effect
5. Total duration: 5-15 seconds (depending on rarities)

**Tutorial Integration**:
- **Step 6**: Trainer Deck (20 cards, Epic reveal is 3 sec dramatic) + Element Booster #1 (5 cards)
- **Step 23**: Standard Pack (5 cards, first self-earned pack)
- **Step 27**: Element Booster #2 (5 cards, economy milestone reward)
- **Step 28**: 2 Standard Packs (10 cards, tutorial completion)
- **Total**: 5 packs opened in tutorial (45 cards total)

---

### Resource Accumulation (AFK Progression)

**Definition**: Resources generated by economy buildings while playing or AFK, auto-collected up to storage capacity.

**Auto-Collection System**:
1. **No Tapping Required**: Buildings produce resources continuously
2. **Storage Capacity**: Resources accumulate up to max storage (1,000-20,000 depending on level)
3. **Production Stops**: When storage is full, production halts until player spends resources
4. **Visual Indicator**: HUD shows "Food: 850/1,000" (yellow = near capacity, red = full)
5. **Spend to Progress**: Player checks in to spend resources on upgrades, equipment, etc.

**Production Rates** (Already Defined):
- **Granary**: 10 Food/hour (Level 1), 20 Food/hour (Level 2), 40 Food/hour (Level 3)
- **Sawmill**: 10 Lumber/hour (Level 1), 20 Lumber/hour (Level 2), 40 Lumber/hour (Level 3)
- **Mine**: 5 Ore/hour (Level 1), 10 Ore/hour (Level 2), 20 Ore/hour (Level 3)

**Storage Upgrades**:
- **Level 1 Storage**: 1,000 Food, 1,000 Lumber, 500 Ore (starting capacity, fills in ~41 hours AFK)
- **Level 2 Storage**: 5,000 Food, 5,000 Lumber, 2,500 Ore (fills in ~8 days AFK)
- **Level 3 Storage**: 20,000 Food, 20,000 Lumber, 10,000 Ore (fills in ~20 days AFK)

**Design Philosophy**:
- **No Tap-Tap-Tap**: Unlike Clash of Clans or similar games, no need to manually collect
- **Wake Up to Full Storage**: Check in after sleeping, storage is full, ready to spend
- **Spend to Continue**: Player spends resources on meaningful choices (upgrade buildings OR craft equipment)
- **Not a Crafting Game**: Spend resources on strategic choices, not micromanaging production queues

**Tutorial Integration**:
- **Step 27**: Deploy economy building, resources auto-accumulate
- **Tooltip**: "Resources accumulate automatically up to storage capacity. Spend them to keep producing!"
- **Post-Tutorial**: Full economy system unlocked (deploy 10+ buildings, wake up to full storage)

---

## 5.5.12 Currency Balance Summary

**Daily Earnings** (F2P Active Player):
- **Gold**: 500 (daily login) + 500 (5 battles × 100) + 500 (1 weekly quest / 7 days) + 240 (AFK production) = **1,740 Gold/day**
- **Gems**: 10 (daily login, bonus days) + 14 (weekly quest / 7 days) = **24 Gems/day**
- **Food**: 240 (AFK Granary) + 100 (5 battles × 20) = **340 Food/day** (surplus after 100 Food spent on battles)
- **Lumber**: 240 (AFK Sawmill) + 100 (5 battles × 20) = **340 Lumber/day**
- **Ore**: 120 (AFK Mine) + 50 (5 battles × 10) = **170 Ore/day**
- **Arena Tokens**: 50 (5 PvP matches × 10) = **50 Tokens/day** (if active in PvP)
- **Energy**: 240 (natural refill) + 100 (starting) = **340 Energy/day** (enough for 34 battles, capped at 24)

**Weekly Earnings** (F2P Active Player):
- **Gold**: 12,180/week (can buy 12 Standard Packs OR 4 Epic Boosters OR save for Game Deck in 4 weeks)
- **Gems**: 168/week (can buy 1 Premium Standard Pack with 68 Gems left over)
- **Food**: 2,380/week (enough for 119 battles + building upgrades)
- **Lumber**: 2,380/week (enough for 23 equipment crafts + building upgrades)
- **Ore**: 1,190/week (enough for 5 Iron Swords + building upgrades)
- **Arena Tokens**: 350/week (can buy 1 Arena Champion Pack every 1.5 weeks)

**Whale Comparison** ($136/week):
- **Gold**: Same as F2P (12,180/week, cannot buy Gold with real money)
- **Gems**: 14,400/week (10× F2P, can buy 144 Premium Standard Packs OR 28 Energy refills/day)
- **Food/Lumber/Ore**: 10× F2P (AFK production scales with Energy refills → more battles → more chest drops)
- **Arena Tokens**: Same as F2P (skill-based, cannot buy with money)

**Design Philosophy**:
- **Gold Equality**: F2P and whales earn Gold at same rate (skill and time investment matter)
- **Gem Advantage**: Whales get 10× Gems (premium packs, energy refills, shortcuts)
- **Resource Advantage**: Whales get 10× resources (more battles via Energy refills → more chest drops)
- **Arena Equality**: Whales cannot buy Arena Tokens (PvP rewards skill, not spending)
- **Deck Power Brackets**: Rarity budget + PvP matchmaking prevent pay-to-win (whales fight whales)

---

# SECTION 6: SOCIAL INFRASTRUCTURE

Social features build community, from alliances for large-scale play to friends for casual co-op. Integrated with Nakama for real-time interaction.

## 6.1 Alliance System

### Overview
Alliances are guilds for cooperative play, enabling shared resources and joint events. Players unlock alliance features progressively as they level up their account, ensuring new players master PvE fundamentals before entering competitive multiplayer.

### Player Level Progression: Safe Growth to Competitive Play

**Design Philosophy**: Players should grow to Level 30 through **safe PvE content** without being constantly raided by high-level players. PvP is **opt-in**, not forced. This prevents new players from wasting resources healing expensive Epic/Legendary units while learning the game.

#### Level 10: Alliance Join (Social Foundation)
**Unlocks**:
- Join or create an alliance (up to 100 members)
- Access alliance chat and diplomacy channels
- Participate in **Alliance PvE Events** (cooperative raids against AI bosses)
- Donate to alliance treasury for buffs
- Vote on alliance decisions (ally/war declarations)

**What You CAN'T Do Yet**:
- ❌ Join PvP Arena battles (requires Level 15)
- ❌ Participate in Alliance Wars (requires Level 30)
- ❌ Deploy to active PvP maps (requires Level 20)

**Why This Level?**:
- By Level 10, players have 25-30 card decks and understand deck building
- Alliance PvE events teach coordination without PvP risk
- Social bonding builds community before competitive pressure
- Players learn alliance mechanics (treasury, voting, diplomacy) in safe environment

---

#### Level 15: Controlled PvP (Matchmade Arenas)
**Unlocks**:
- **1v1 Arena**: Matchmade battles against players within ±3 levels
- **3v3 Arena**: Team battles with alliance members or random teammates
- **Bracketed Rewards**: Separate reward pools for Level 15-19, 20-24, 25-29, 30+ brackets
- **No Territory Loss**: Arena battles don't affect your map territories (safe practice)

**What You CAN'T Do Yet**:
- ❌ Deploy to active PvP maps (requires Level 20)
- ❌ Raid other players' territories (requires Level 20)
- ❌ Participate in Alliance Wars (requires Level 30)

**Why This Level?**:
- Players have 30-35 card decks and multiple Epic heroes
- Controlled matchmaking prevents Level 30 stomps
- No permanent losses (territories safe) = low-risk experimentation
- Learn PvP tactics before open-world map battles

**Bracketed Matchmaking Prevents Unfair Fights**:
| Player Level Bracket | Matchmaking Pool | Max Deck Size | Typical Deck Power |
|----------------------|------------------|---------------|---------------------|
| **15-19** | Only Level 15-19 players | 30-35 cards | 2-3 Epics, mostly Rares |
| **20-24** | Only Level 20-24 players | 35-40 cards | 3-5 Epics, 1 Legendary |
| **25-29** | Only Level 25-29 players | 40-45 cards | 5+ Epics, 2-3 Legendaries |
| **30+** | All Level 30+ players | 40-50 cards | Full Legendary/Mythic decks |

---

#### Level 20: Active PvP Maps (Open-World Conquest)
**Unlocks**:
- Deploy decks to **Active PvP Maps** (open-world territorial conquest)
- Raid other players' territories (steal resources, capture tiles)
- Defend your territories from raids (auto-battle or manual)
- **Warning**: Your territories CAN be attacked by other Level 20+ players
- Participate in **Regional Competitions** (State/County-level leaderboards)

**What You CAN'T Do Yet**:
- ❌ Participate in Alliance Wars (requires Level 30)

**Why This Level?**:
- Players have 35-40 card decks with solid Legendary cards
- Enough experience to defend territories effectively
- Resources to heal units after losses (3-4 weeks of AFK income built up)
- Understand risk/reward of open-world PvP

**Opt-In System**:
- **PvE-Only Toggle**: Players can stay in "PvE Mode" indefinitely (territories never attacked)
- **Opt Into PvP**: Click "Enable PvP Mode" to deploy to Active PvP Maps
- **Once Enabled**: Cannot disable for 7 days (prevents exploit of "turn off when losing")
- **Rewards**: PvP maps have 2× resource nodes and exclusive Legendary card packs

**Safe Zone Protection**:
- **First 24 Hours**: New PvP territories have "Shield" (cannot be attacked)
- **Beginner Bracket**: Level 20-24 players matched against similar levels on dedicated maps
- **Anti-Griefing**: If you're attacked 3× in 24 hours, auto-shield activates for 12 hours

---

#### Level 30: Alliance Wars (Large-Scale Guild Battles)
**Unlocks**:
- Participate in **Alliance Wars** (50v50 guild wars every 2 weeks)
- Coordinate with alliance for large-scale territory control
- Contribute multiple decks to alliance war efforts
- Compete for server-wide leaderboards and prestige rewards

**Why This Level?**:
- Players have max 40-50 card decks with full Legendary/Mythic options
- Months of experience in PvE, Arena PvP, and Active PvP Maps
- Enough resources to sustain multi-battle campaigns
- Deep understanding of strategy, formations, and meta

**Alliance War Mechanics**:
- 2-week war seasons (Week 1: Preparation, Week 2: Active war)
- Each alliance declares 1 enemy alliance (voted by members)
- Shared map with 50+ contested tiles
- Alliance members contribute decks to "War Pool" (up to 3 decks per player)
- Officers assign decks to defend key tiles
- Victory = Legendary packs for entire alliance, exclusive cosmetics, server bragging rights

---

### How to Play (Alliance Features by Level)

| Player Level | Alliance Features Available | PvP Risk | Time to Reach (Active Player) |
|--------------|----------------------------|----------|-------------------------------|
| **1-9** | ❌ No alliance access | ✅ Zero (PvE only) | Days 1-7 |
| **10-14** | ✅ Join alliance, PvE events, chat, donations | ✅ Zero (PvE only) | Week 1-2 |
| **15-19** | ✅ + Matchmade Arena (1v1/3v3) | ⚠️ Low (no territory loss) | Week 2-4 |
| **20-29** | ✅ + Active PvP Maps (opt-in) | ⚠️ Medium (can be raided) | Month 1-3 |
| **30+** | ✅ + Alliance Wars | ⚠️ High (large-scale wars) | Month 3-6 |

### Mechanics
- **Join/Create**: Search or found alliances; invite players (Level 10+).
- **Hierarchy**: Leader > Generals > Officers > Members; promote via contributions.
- **Bank**: Shared treasury for donations; funds buffs/tech trees.
- **Events**: Joint PvE raids (Level 10+), Arena tournaments (Level 15+), Alliance Wars (Level 30+).
- **Ranks**: Based on activity/donations; higher ranks unlock perks.
- **Limits**: Server-wide caps to prevent monopolies.

### Player Tips
- **Level 10-14**: Join active alliance for PvE events; learn coordination in safe environment.
- **Level 15-19**: Practice PvP in Arenas (no risk) before committing to Active PvP Maps.
- **Level 20+**: Only opt into Active PvP Maps when you have resources to heal losses.
- **Level 30+**: Contribute to Alliance Wars for prestige and exclusive Legendary packs.
- **If you want to experiment early**: Arena PvP at Level 15 lets you test strategies without consequences.

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

---

### Player Level vs Castle Level (Critical Design Distinction)

Sovereign Territories uses **two parallel progression systems** that serve different purposes:

1. **Player Level** (Account-Wide Avatar Progression)
2. **Castle Level** (Per-Castle Territory Progression)

Both are **100% F2P accessible**—active players level faster, but there is no paywall.

---

#### Player Level (Your Avatar/Account)

**What It Represents**: Your personal mastery and unlocked capabilities across the entire game. This is **your meta-progression** that never resets.

**How to Gain Player XP**:
- Campaign battles, daily quests, weekly events, monthly challenges
- PvP victories, alliance contributions, achievements
- Battle Pass tiers (seasonal)
- First-time achievements (one-time bonuses)

**Player Level Benefits (Applied to ALL Your Castles)**:

| Player Level | Max Deck Size | Key Unlocks | F2P Timeline (Active Player) |
|--------------|---------------|-------------|------------------------------|
| **1** | 10-15 cards | Tutorial, first castle, PvE county maps | Day 1 |
| **3** | 15-20 cards | Auction house access | Day 1-2 |
| **5** | 20-25 cards | Daily quests, saga battles | Day 3-5 |
| **10** | 25-30 cards | **Alliance join**, Alliance PvE events, State Map | Week 1-2 |
| **15** | 30-35 cards | **Controlled PvP** (1v1/3v3 Arena), Secondary castles (up to 5) | Week 2-4 |
| **20** | 35-40 cards | **Active PvP Maps** (open-world conquest), County Map, Advanced tactics | Month 1-2 |
| **25** | 40-45 cards | Prestige cosmetics, Global Map access | Month 2-3 |
| **30** | 40-50 cards (max) | All content unlocked, legendary frame, Alliance Wars | Month 3-6 |

**Why Player Level Matters**:
- ✅ **Persistent**: Never lost, even if castles are destroyed
- ✅ **Deck Size Scaling**: Prevents new players from being overwhelmed by 50-card decks
- ✅ **Content Gating**: Learn basics before accessing complex systems
- ✅ **Social Status**: Visible rank badge shows experience
- ✅ **F2P Fairness**: Cannot be purchased—everyone earns through play
- ❌ **No Direct Power**: Does NOT make cards stronger (Level 50 player with Commons loses to Level 10 with Legendaries)

---

#### Castle Level (Your Territory Bases)

**What It Represents**: The strength and development of a **specific castle** you control on the map. **Think of it as your "Base Level"** for that location.

**How to Gain Castle XP** (Separate from Player XP):
- Holding territories (10 XP/hour per territory)—AFK passive income
- Building upgrades (100-500 XP per level)
- Winning defenses (200 XP per successful defense)
- Wonder control (500 XP/hour, contested)
- Alliance contributions (50 XP per 1,000 gold donated)

**Castle Level Benefits (Specific to Each Castle)**:

| Castle Level | Building Slots | Hero Stacks Max | Deck Slots | Gold Bonus | Map Tier |
|--------------|----------------|-----------------|------------|------------|----------|
| **1** | 5 | 3 | 3 | +0% | Tutorial |
| **5** | 10 | 5 | 5 | +10% | Local |
| **10** | 15 | 7 | 7 | +25% | State |
| **15** | 20 | 10 | 8 | +50% | County |
| **20** | 30 | 15 | 9 | +75% | Global |
| **25** | 40 | 20 | 10 | +100% | Prestige skin |
| **30** | 50 | 25 | 10 | +150% | Mega-castle |

**Why Castle Level Matters**:
- ✅ **Territory Control**: Higher-level castles hold more buildings and defend better
- ✅ **Economic Bonuses**: Gold bonuses encourage leveling your main economic castle
- ✅ **Multiple Instances**: Control up to 5 castles (Player Level 15+), each with independent Castle Levels
- ✅ **Strategic Choices**: Level one mega-castle OR spread XP across multiple castles
- ✅ **AFK Progression**: Holding territory generates Castle XP passively
- ❌ **Can Be Lost**: If castle is destroyed on the map, you lose that Castle Level (but keep Player Level)

---

#### System Comparison Table

| System | What It Affects | How to Level | Persistent? | F2P Timeline |
|--------|-----------------|--------------|-------------|--------------|
| **Player Level** | Deck size, feature unlocks, content access | Battles, quests, events | ✅ Always | Day 1 → Month 6 for max |
| **Castle Level** | Building slots, hero stacks, deck storage, gold bonus | Territory control, buildings | ❌ Lost if destroyed | Hour 1 → Month 2 per castle |

---

#### Example Scenario

**You are Player Level 20**:
- Unlocked 35-card decks (usable in ALL battles, regardless of castle)
- Unlocked Global Map access
- Can control up to 5 castles simultaneously

**You have 3 castles**:
1. **Main Castle** (Castle Level 25): Fully upgraded, +100% gold, 40 building slots
2. **Resource Castle** (Castle Level 10): Mining region, 15 building slots
3. **PvP Border Castle** (Castle Level 5): Defense outpost, 10 building slots

**Your Player Level 20** gives you 35-card decks for every battle.
**Your Castle Levels** determine how many buildings and defenses each castle can deploy.

---

#### Design Philosophy

**Player Level** = **Who you are** (skill, experience, mastery)
**Castle Level** = **What you control** (territory, resources, power)

You are always progressing your account (Player Level) even if your territorial holdings (Castles) fluctuate.

---

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

