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

---

## Documentation Map

**This game bible is the master design document. For implementation details, reference these supporting documents**:

### Core Specifications (Implementation Details)
- **[mvp-scope-final.md](mvp-scope-final.md)** - 8-week MVP roadmap, Must Have vs Won't Have features
- **[economy-system.md](economy-system.md)** - Currency earning rates, F2P vs whale balance, Phase 2 Food/Lumber/Ore economy
- **[combat-calculation-spec.md](combat-calculation-spec.md)** - MVP Attack/Defense formulas, Phase 2 RPG stats, Phase 3 elemental interactions
- **[rpg-systems-spec.md](rpg-systems-spec.md)** - Health/Mana/Stamina mechanics, Consumables, RPG Shops, Equipment Sockets (Phase 2-3)
- **[map-tier-progression.md](map-tier-progression.md)** - World→Territory→Realm→Battle hierarchy, occupation mechanics, monster scaling
- **[terminology-guide.md](terminology-guide.md)** - Canonical reference for map names, player title (Sovereign), occupation terms

### Tutorial & Onboarding
- **[tutorial-flow.md](tutorial-flow.md)** - 28-step tutorial progression (0-60 minutes), exact card rewards, UI flow

### Data Specifications (Schemas)
- **docs/specs/*.json** - 60+ JSON schemas for cards, packs, economy, combat, maps, progression

### Project Management
- **[bible-reorganization-plan.md](bible-reorganization-plan.md)** - Reorganization roadmap, action items, Phase 1-5 tracking
- **[README.md](../README.md)** - Project overview, tech stack, quick start guide

**Where to Find What**:
- **Game design philosophy** → This bible (Sections 1-18)
- **Exact earning rates, formulas** → Supporting specs (economy-system.md, combat-calculation-spec.md)
- **MVP feature list** → mvp-scope-final.md
- **Tutorial step-by-step** → tutorial-flow.md
- **Terminology standards** → terminology-guide.md

---

# SECTION 1: CORE PHILOSOPHY

## Game Tagline

"Build the Deck. Rule the Map. Automate the Empire."

## Overview

Sovereign Territories is a **multi-genre hybrid strategy game** that blends the best mechanics from decades of gaming:

**Genre DNA**:
- **TCG/CCG** (Pokemon TCG, Magic: The Gathering): Deck-building, rarity systems, card collection, strategic composition
- **Party-Based RPG** (Baldur's Gate, Neverwinter Nights, Diablo): Heroes with Health/Mana/Stamina, equipment slots, leveling progression, consumables
- **Tactical Strategy** (Heroes of Might and Magic, Fire Emblem): Grid-based combat, hero-led armies, formations, terrain advantages
- **Territorial Conquest** (Risk, Diplomacy): Map control, alliances, conquest campaigns, seasonal wars
- **Tabletop Wargaming** (Warhammer 40K/Fantasy): 3D hero figurines on maps, visual unit stacks, deployment strategy
- **Roguelike** (Diablo, Slay the Spire): Procedurally generated maps, random encounters, endless replayability
- **RTS** (Supreme Commander, Warcraft II): Deck composition replaces unit production, no tedious base building
- **AFK/Idle Games**: Passive resource production, auto-battle, offline progression, come-back rewards

**Core Loop**: Collect cards → Build decks → Deploy heroes (with RPG stats) → Conquer maps → Level up → Unlock new content → Repeat with new themes/seasons.

**What Makes This Different**: We take the **fun parts** (opening packs, leveling heroes, strategic battles, exploration) and **avoid the tedium** (forced resource collection, waiting for buildings, repetitive unit production, tap-to-collect grind). This is a game about **strategic depth and collection progression**, not babysitting production queues.

The game features a "Universal Engine" that allows seamless integration of different themes—such as Medieval Fantasy, Sci-Fi, Norse Mythology, Historical, or Modern Warfare—without changing the core ruleset. This ensures endless replayability and expansion potential.

### Key Features
- **Heroes as RPG Characters**: Each hero card has Health, Mana, Stamina (Phase 2), equipment slots, and unique abilities
- **No Forced Grind**: AFK resource production replaces tap-to-collect mechanics; auto-battle for PvE farming
- **PvE-First Progression**: Safe territorial conquest campaigns against AI before unlocking PvP at higher levels
- **Multi-Tier Maps**: World Map (Risk-style) → Territory Map (regional control) → Realm Map (exploration) → Battle Map (tactical combat)
- **Come-Back Gameplay**: Daily rewards, login bonuses, pack openings, hero leveling—not production timers

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
   - **Battle Deployments**: Position hero stacks on State/Realm Maps for territorial control
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
- **Map Positioning**: Heroes placed on State/County/World Maps as figurines
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
Shinies provide **5% production/combat bonuses** when deployed on County/Territory Maps:

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
- **Realm Map**: Shiny buildings have animated gold shimmer
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
5. **Campaign Milestones**: Complete Territory Map = 1 random Rare+ shiny

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

## 2.5 New Player Onboarding: Philosophy & Trainer Deck System

**For complete tutorial flow (28 steps, UI mockups, exact rewards), see [tutorial-flow.md](tutorial-flow.md)**

### Onboarding Philosophy

**Goal**: Get Sovereigns from "What is this game?" to "I understand and want more" in 30-60 minutes.

**Key Principles**:
1. **Power Fantasy First**: Give Epic hero immediately (no "bad luck" first experience)
2. **Meaningful Choice**: 6 Trainer Deck options (Fire/Water/Earth Curated or Element), not random
3. **Playable Immediately**: 20-card Trainer Deck fits in first deck slot, works out-of-the-box
4. **Learn by Doing**: Tutorial uses actual gameplay (battles, deck building, Realm Map exploration)
5. **Respect Player Time**: Skip options after first battle, auto-battle for grinders

**Tutorial Duration**:
- **Minimum**: 30 minutes (skip all optional text, auto-battle)
- **Maximum**: 60 minutes (read all lore, manual battles, explore all UI)
- **Average**: 45 minutes (first-time players, moderate pace)

### Trainer Deck System (Starter Onboarding)

**The Selection** (Tutorial Step 6):
Instead of random pack opening, Sovereigns choose from **6 Trainer Decks**:

**CURATED DECKS** (3 options - Named Epic + Pre-Built Synergy):
1. **Flame Warlord Deck** (Fire Element) - Aggressive burn-stacking playstyle
2. **Tidal Guardian Deck** (Water Element) - Defensive sustain with healing chains
3. **Stone Sentinel Deck** (Earth Element) - Terrain control and area denial

**ELEMENT DECKS** (3 options - Random Epic + Varied Support):
4. **Fire Element Deck** - Guaranteed Fire Epic (random from pool), 19 varied cards
5. **Water Element Deck** - Guaranteed Water Epic (random from pool), 19 varied cards
6. **Earth Element Deck** - Guaranteed Earth Epic (random from pool), 19 varied cards

**Why This Design?**:
- **Curated Decks**: Perfect synergy out-of-the-box (all Fire cards work together), recommended for beginners
- **Element Decks**: Higher variance, deckbuilding challenge, better replayability for experienced players
- **Permanent Choice**: Selection cannot be changed (encourages alt accounts for F2P engagement)
- **Inspiration**: Pokemon TCG Trainer Decks and Battle Boxes (pre-built playable decks)

**Deck Contents**: Each Trainer Deck contains exactly **20 cards**:
- 1× Epic Hero (named for Curated, random for Element decks)
- 6× Units (element-themed or varied)
- 2× Buildings (economy or military - art only for MVP, functional in Phase 2)
- 1× Worker (resource production - art only for MVP, functional in Phase 2)
- 8× Tactics (combat abilities)
- 2× Equipment (hero attachments)

**Starting Collection** (After Tutorial):
- **Trainer Deck**: 20 cards (selected at Step 6)
- **Bonus Packs**: 16 cards (Element Booster at Step 6, 6 cards at Step 23, Element Booster at Step 27)
- **Total**: 36 cards by tutorial completion (Step 28)

**For exact card lists, reveal animations, and UI flow, see [tutorial-flow.md](tutorial-flow.md)**

---

## 2.6 Card Stacking, Formations & Map Deployment

> **See [combat-mechanics.md](specs/combat-mechanics.md) for complete stacking formulas, formation templates, and map deployment mechanics.**

### Core Mechanics (Heroes of Might and Magic Inspiration)

**Stacking System**:
- Multiple cards occupy single tile, combine stats into one powerful unit
- **Same Unit Type Stacking**: Archers + Crossbowmen = "Ranged Stack" ✅
- **Cross-Theme Allowed**: Elf + Human + Dwarf units stack together
- **Mixed Rarity**: Common + Epic in same stack (no penalty)

**Map Layer Stacking Rules**:
- **Realm Map** (Strategic): Full army stacks (heroes + units + buildings)
- **Battle Map** (Tactical): Separated by unit type (archers back, warriors front)

**Visual Representation**:

**Visual Representation**:
- **Epic+ Cards**: 3D miniature figures (animated, VFX effects)
- **Rare Cards**: Premium card sprites on stands
- **Common/Uncommon**: Flat card sprites

### Rarity Budget System (Deck Constraints)

**Purpose**: Prevent "all Legendary" decks while allowing creativity

**Rarity Point Costs**:
- Common = 1pt, Uncommon = 2pt, Rare = 4pt, Epic = 8pt, Legendary = 16pt, Mythic = 32pt

**Deck Budgets by Player Level**:

| Player Level | Battle Card Limit | Rarity Budget | Example Deck |
|--------------|-------------------|---------------|--------------|
| **1-5** | 10-15 cards | 50 pts | 1 Epic (8) + 5 Rare (20) + 9 Common (9) = 37 pts ✅ |
| **10-15** | 25-30 cards | 120 pts | 2 Legendary (32) + 3 Epic (24) + 10 Rare (40) + 15 Common (15) = 111 pts ✅ |
| **20-25** | 35-40 cards | 200 pts | 3 Legendary (48) + 5 Epic (40) + 15 Rare (60) + 17 Common (17) = 165 pts ✅ |
| **30+** | 40-50 cards | 300 pts | 5 Legendary (80) + 8 Epic (64) + 20 Rare (80) + 17 Common (17) = 241 pts ✅ |

**Economy Cards** (Separate):
- **Not counted in rarity budget** (separate 10-15 card limit)
- Types: Buildings (Farm, Mine, Turret), Workers (Farmer, Miner)
- Deploy to Realm Map tiles for AFK income
- Left behind when army moves (must retrieve to redeploy)

### Formation System (Auto-Deployment Presets)

**Built-In Formations**:
1. **Frontline Vanguard**: Heroes front, melee flanks, ranged back
2. **Defensive Turtle**: Tanks surround, ranged center, healers protected
3. **Flanking Cavalry**: Fast units on flanks, archers center
4. **Epic Showcase**: Premium cards prominently displayed (status flex)
5. **Balanced Wedge**: Tank front, melee sides, ranged rear

**Custom Formation Editor**:
- Create up to 5-20 custom formations (VIP increases slots)
- Drag units onto grid, save template
- Auto-fill by unit tags (Tank, DPS, Ranged, Healer)

**Auto vs Manual Deployment**:
- **Auto**: Quick PvE/farming, one-click deploy
- **Manual**: High-stakes PvP, terrain optimization, tournament setup days

### Map Tiers & Multi-Army System

**Zoom Levels** (Risk → Heroes of Might and Magic):
- **World Map**: 1 deck per territory (flag icon)
- **Realm Map**: Full deck spreads into hero-led armies (10-20 tiles)
- **Battle Map**: Tactical grid combat (15×15 tiles)

**Multi-Hero Armies**:
- **Each Epic+ hero** can lead independent army on Realm Map
- **Example**: 3 Epic heroes + 30 units = 3 separate army stacks
- **Visual**: Thor (3D figure) + "10 units" badge
- **Strategy**: Split for exploration, merge for boss battles

**Army Composition Examples**:
- **Single Army**: Thor + 29 units = 1 powerful stack
- **Split Army**: Thor + 10 units, Fire Mage + 8 units, Knight + 9 units = 3 stacks
- **Hero-Less Stacks**: 10× Archers = thick card sprite (75% movement speed)

### Realm Map Exploration (PvE Campaigns)

**Map Structure** (Non-Linear Exploration):
- **Fog of War**: Reveals as you explore
- **Static Spawns**: Enemy camps (respawn 1-24 hours for farming)
- **Resource Nodes**: Gold Mines, Farms, Lumber Mills
- **Buff Shrines**: +10% ATK/HP (permanent per map)
- **Towns**: Recruit Flex Heroes (temporary allies)
- **Boss**: Final objective (defeat to complete county)

**Economy Card Deployment**:
1. Capture resource node (defeat spawn)
2. Deploy economy cards: 1 Mine + 2 Miners = +100 gold/hour AFK
3. Army leaves tile, cards stay behind
4. Retrieve later (costs turns) or leave permanently

**Flex Heroes** (Temporary Allies):
- Towns offer random Rare/Epic heroes for this map only
- Grow from 15-card starting deck to 50-card army
- Removed when map complete (no permanent bloat)

**Time Pressure** (Optional):
- Every 5 turns, enemies gain +10% HP/ATK
- Discourages infinite farming, rewards efficient pathing
- Can disable for "Casual Mode"

### Competitive Features

**Event Setup Days** (Tournament Deployment):
- 3-7 days to manually place formations
- Map revealed in advance for strategic planning
- Battles resolve simultaneously (AI vs AI)
- Leaderboards: Most Damage, Fastest Victory, Tankiest Defense

**Map Generation**:
- **Pre-Set**: Hand-crafted campaign maps (story mode)
- **Procedural**: Random seed per event (fair, replayable)
- **Player-Created**: Community map editor (future)

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

## Tier 1: World Map (Quarterly Season)

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

**Building Types for World Map**:
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

## Tier 2: Territory Map (Monthly War)

### View
**Hex grid overlay** on isometric terrain. Each hex is a playable tile (50-100 hexes per state).

### Scale & Scope
- **Size**: 50-100 hexes per Territory Map
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

## Tier 3: Realm Map (Weekly Reset)

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

**For detailed mode mechanics, rewards, and phasing, see [gameplay-modes-spec.md](gameplay-modes-spec.md)**

Sovereign Territories offers multiple gameplay modes catering to different playstyles:
- **MVP**: Realm Map PvE (tutorial + progression)
- **Phase 2**: Alliance PvE Events, Daily/Weekly Challenges, Saga Campaign
- **Phase 3**: Territory Map conquest, Arena PvP (1v1/3v3), Alliance Wars
- **Phase 4**: World Map seasons, Expeditions (board game mode)

---

## 4.1 Realm Map PvE (MVP - Tutorial & Progression)

**For tutorial flow, see [tutorial-flow.md](tutorial-flow.md)**

### Overview
The Realm Map is the **primary MVP mode**: a 20-40 Location hex grid for single-player exploration teaching core mechanics through scripted battles.

### Key Features
- **Map**: 20-40 hexes (Locations: Town, City, Dungeon, Mine, Ruins, Monster Spawn, Treasure Node)
- **Movement**: 3 tiles/turn, 10 Movement Points/day (time-gated exploration)
- **Battles**: 8×8 tactical grid, 20-50 card decks, auto-battle after tutorial
- **Energy**: 10 Energy/battle (240 Energy/day = 24 battles max)
- **Rewards**: Gold (50-500/battle), Gems (10-20/treasure node), Battle Chests (Bronze/Silver/Gold)
- **Boss**: Final Location with Epic/Legendary boss (harder difficulty, rare loot)

### MVP Scope
- ✅ 3-5 Realm Maps (60-200 Locations total)
- ✅ Treasure nodes (one-time Gold/Gems/card rewards)
- ✅ Monster Spawns (Common → Epic rarity)
- ❌ Economy deployment (Phase 2)
- ❌ Multi-Realm occupation (Phase 3)

---

## 4.2 Saga Campaign (Phase 2 - Story PvE) ❌ NOT IN MVP

**Schema**: [docs/specs/campaign-schema.json](docs/specs/campaign-schema.json)

Linear story mode (Player Level 10+) with themed chapters, boss phases, and narrative cutscenes. Primary source of Common/Uncommon fodder cards.

---

## 4.3 Expeditions (Phase 4 - Board Game) ❌ NOT IN MVP

**Schema**: [docs/specs/expedition-schema.json](docs/specs/expedition-schema.json)

Weekly mini-game mode (Player Level 15+) mixing board game mechanics (Mario Party) with card battles. Roll dice, land on event spaces, race to finish for Legendary rewards.

---

## 4.4 Alliance Events (Phase 3 - PvE/PvP Hybrid) ❌ NOT IN MVP

Large-scale alliance events (50-200 players) combining PvE raids and PvP sieges. Auto-battle dominant with "hero moments" for key decisions.

---

## 4.5 Arena PvP (Phase 3 - Ranked Matches) ❌ NOT IN MVP

**For matchmaking, see [combat-calculation-spec.md](combat-calculation-spec.md) Appendix**

Competitive 1v1/3v3 PvP (Player Level 15+) with Elo matchmaking and Arena Token rewards (skill-based, cannot buy).

---

## 4.6 Territory/World Maps (Phase 3-4 - Alliance Conquest) ❌ NOT IN MVP

**For occupation mechanics, see [map-tier-progression.md](map-tier-progression.md)**

- **Territory Map** (Phase 3): 50-100 Realms, 1-month campaigns, castle sieges
- **World Map** (Phase 4): 200-500 Territories, 3-month seasons, alliance wars
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

**See [economy-system.md](economy-system.md) for complete currency specs, earning rates, and F2P balance calculations.**

The economy in Sovereign Territories uses **multiple currencies** to prevent whale dominance and create diverse progression paths:
- **Gold** (soft currency) - Cannot be bought, F2P fairness
- **Gems** (premium) - Whale advantage but capped at $136/week
- **Energy** (stamina) - Time-gated, limits grinding
- **Food/Lumber/Ore** (Phase 2) - AFK production, cannot buy with Gems
- **Arena Tokens** (Phase 3) - Skill-based PvP currency

## 5.1 MVP Currencies (Phase 1)

### Gold (Soft Currency)
**Cannot be bought with real money** - F2P fairness pillar

**Earning** (F2P Player):
- Daily Login: 500 Gold/day
- Battle Rewards: 100-200 Gold per battle
- Battle Chests: 50-500 Gold (Bronze → Platinum)
- **Total**: ~700 Gold/day (4,900/week)

**Spending**:
- Standard Pack: 1,000 Gold (5 cards)
- Element Booster: 2,000 Gold (5 cards)
- Epic Booster: 5,000 Gold (5 cards)

**F2P Balance**: Can buy 4-5 Standard Packs per week

### Gems (Premium Currency)
**Weekly purchase cap**: $136/week maximum (prevents whale blitz)

**Earning** (F2P):
- Daily Login: 10 Gems/day (70/week)

**Earning** (Whale):
- Purchase: $0.99 = 100 Gems, $4.99 = 550 Gems, $19.99 = 2,400 Gems
- **Total**: ~5,070 Gems/week (70× F2P advantage)

**Spending** (Phase 2):
- Premium Pack: 100 Gems (10% shiny rate)
- Energy Refill: 50 Gems (100 Energy)
- Speed-Up: 100 Gems (instant combining)

**F2P Balance**: Rarity Budget prevents whale decks from dominating PvP

### Energy (Stamina System)
**Purpose**: Prevent grinding, encourage daily login

**Mechanics**:
- Starting: 100 Energy (tutorial completion)
- Refill: 1 Energy per 6 minutes (240/day)
- Daily Max: 340 Energy total
- Battle Cost: 10 Energy per battle
- **Daily Battles**: 34 battles/day max

**Refills** (Phase 2):
- Gem Refill: 50 Gems = 100 Energy
- Energy Potion: From battle chests (cannot buy)

## 5.2 Phase 2 Currencies (Month 2-3)

### Food/Lumber/Ore (Resource Economy)
**AFK Production** - Cannot buy with Gems (time-gated)

**Food**:
- Production: Granary 10-50 Food/hour (24-hour cap)
- Spending: Battle entry (20 Food), deployment (50 Food), upgrades (500-1,000 Food)
- **Total**: 340 Food/day (240 AFK + 100 chests)

**Lumber**:
- Production: Sawmill 10-50 Lumber/hour
- Spending: Equipment crafting (100-500 Lumber), construction (300 Lumber), upgrades (500-1,000 Lumber)
- **Total**: 340 Lumber/day

**Ore** (Rarest):
- Production: Mine 5-25 Ore/hour (half of Food/Lumber)
- Spending: High-tier equipment (200-2,000 Ore), card combining (500 Ore for Legendary → Mythic)
- **Total**: 170 Ore/day (intentional bottleneck)

**Auto-Collection**:
- Resources accumulate to storage cap (1,000-20,000)
- Production stops when full (incentivizes spending)
- No tap-to-collect annoyance

**F2P Balance**: Whales must wait for AFK production (cannot buy infinite resources)

## 5.3 VIP System (Phase 2 - Post-MVP)

**Philosophy**: Pay-for-convenience, never pay-to-win

**VIP Tiers** (Unlocked by cumulative Gem spending):
- **VIP 0 (Free)**: 100 max energy, 3 deck slots
- **VIP 1** ($1): +20 energy, +1 deck slot, daily common pack
- **VIP 2** ($5): +30 energy, +1 deck slot, daily rare pack, 2× auto-battle
- **VIP 3** ($20): +50 energy, +2 deck slots, daily epic pack, 4× auto-battle
- **VIP 4** ($50): +70 energy, +2 deck slots, weekly legendary pack, instant auto-battle
- **VIP 5** ($100): +100 energy, +1 deck slot (10 max), daily legendary pack, queue 10 battles

**VIP Perks** (Convenience only):
- Faster energy recharge (1 per 30min → 1 per 10min)
- More deck slots (3 → 10)
- Auto-battle speed (1× → instant results)
- Reduced auction fees (10% → 5%)
- Cosmetic rewards (avatar frames, card skins, chat effects)

**Anti-Pay-to-Win**:
- VIP players get **no stat advantages**
- Energy cap prevents infinite grinding (200 max = 6 hours/day)
- Rarity Budget prevents all-Legendary VIP decks
- Free players get Day 7 legendary weekly (same as VIP)

**Daily Login Rewards** (7-day cycle):
- Days 1-6: Gold, Energy, Common/Rare/Epic Packs
- **Day 7**: 500 Gold, 50 Gems, 1 Legendary Card (VIP 5 gets 3 Legendaries)
- Streak protection: Free = none, VIP 3+ = 1 forgiveness/month

**Monetization Balance**:
- 70% players stay VIP 0 (viable free path)
- 15% convert to VIP 1-2 ($1-$5 spenders)
- 10% reach VIP 3-4 ($20-$50 spenders)
- 5% reach VIP 5 ($100+ whales, generate 40-60% revenue)

## 5.4 Auction House (Phase 3 - Post-MVP)

**Status**: Phase 3 feature (Month 4-6), not in MVP

**Overview**: Player-driven free market where supply and demand determine prices.

**Core Mechanics**:
- **Unlock**: Castle Level 5+ (prevents early-game flooding)
- **Currency**: Gold only (Gems cannot be traded)
- **Fees**: 10% house cut (VIP 5 = 5%)
- **Listing**: Fixed price or auction (24h/48h/7d duration)
- **Bidding**: Proxy bidding, anti-snipe extension (+60s if bid in final 30s)
- **Filters**: Rarity, Type, Theme, Price range, Stats

**Market Dynamics**:
- **Supply & Demand**: Meta cards = 5,000-10,000 Gold, commons = 10-50 Gold
- **Price Discovery**: 7-day rolling average, suggested pricing
- **Seasonal Fluctuations**: New expansions crash old card prices (-30-50%)
- **Anti-Manipulation**: Volume limits, price floors/ceilings, wash trading detection

**Trading Strategies**:
- **Buy Low/Sell High**: Weekend dips (Saturday-Sunday), weekday peaks (Monday-Wednesday)
- **Flipping**: Snipe underpriced cards 30-50% below market, relist at average
- **Collection Completion**: Use auction to fill gaps (faster than packs)

**Restrictions**:
- **Non-Tradable**: Tutorial cards (soul-bound), VIP cosmetics, event-locked items (30-day hold)
- **Requirements**: Level 5+, verified email, 7-day trade cooldown for new accounts

**Economy Monitoring**:
- **Inflation Tracking**: Developer tools monitor gold velocity, hoarding
- **Transparency Reports**: Monthly market stats (top 10 cards, price trends)
- **Emergency Rollback**: Revert trades if dupe bug discovered

**Future Features** (Phase 4):
- Cross-server trading
- Trade chat channel
- 24-hour card rental system

## 5.5 Monetization Model

**Philosophy**: Pay-for-speed (convenience) or pay-for-cosmetics, **never pay-to-win**

**Pay-for-Speed** (Phase 2):
- Energy refills (50 Gems = 100 Energy)
- Auto-battle speed (2× → instant)
- Queue multiple battles (VIP 5 only)

**Pay-for-Cosmetics**:
- Card skins (alternate art, same stats)
- Avatar frames, chat effects
- VIP-only legendary cosmetic variants

**F2P Fairness**:
- Gold cannot be bought (prevents pay-to-win)
- Rarity Budget limits deck power (whales can't run all-Legendary)
- VIP players progress faster, not stronger

**Analytics & Balance**:
- Target 80/20 rule: 80% players free, 20% paying
- Whale revenue (VIP 5) = 40-60% of total
- ARPPU target: $15-30 per paying user

## Data Schemas

See standalone specs for engineering:
- [resource-schema.json](specs/resource-schema.json) - Currency management, production calculations
- [trade-schema.json](specs/trade-schema.json) - Auction validation, marketplace transactions

---

# SECTION 5.5: RESOURCE ECONOMY & CURRENCY SYSTEMS

**For complete earning rates, F2P projections, and implementation details, see [economy-system.md](economy-system.md)**

**IMPORTANT**: Food/Lumber/Ore economy is **PHASE 2** (Month 2-3). MVP uses Gold/Gems/Energy only.

## 5.5.1 Currency Overview

**Core Philosophy**: Multiple currencies prevent whale dominance (can't buy everything with real money) and create diverse progression paths (PvP skill, AFK patience, exploration, grinding).

**MVP Currency Types** (8-Week Implementation):
1. **Gold** (Soft currency - earned through gameplay, **cannot buy with real money**)
2. **Gems** (Premium currency - bought with real money or earned slowly, **$136/week cap**)
3. **Energy** (Stamina - battle cost, **time-gated** to 24 battles/day)

**Phase 2 Currency Types** (Month 2-3 - **DEFERRED POST-MVP**):
4. **Food** (**PHASE 2** - AFK gathering, production buildings, auto-collection)
5. **Lumber** (**PHASE 2** - AFK gathering, production buildings, auto-collection)
6. **Ore** (**PHASE 2** - AFK gathering, production buildings, auto-collection)

**Phase 3 Currency Types** (Month 4-6 - **DEFERRED POST-LAUNCH**):
7. **Arena Tokens** (**PHASE 3** - PvP ranked match rewards, skill-based, cannot buy)

**No "Coins" Separate Currency**: Real money purchases use Gems directly (simplicity, no conversion confusion).

---

## 5.5.2 Gold (Soft Currency) - **MVP**

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

## 5.5.4 Food (AFK Resource) - **PHASE 2** ❌ **NOT IN MVP**

**For complete Food economy details, see [economy-system.md](economy-system.md) Phase 2 section**

**MVP Status**: Food is deferred to Phase 2 (Month 2-3). MVP uses treasure nodes on Realm Map for resource rewards instead of production buildings.

**Definition**: Consumable resource for unit maintenance and battle entry costs.

**Sources** (How Players Earn Food):
- **AFK Production** (Auto-Collected):
  - Granary: 10 Food/hour (Level 1), 20 Food/hour (Level 2), 40 Food/hour (Level 3)
  - Farm: 50 Food/hour (Level 1), 100 Food/hour (Level 2), 200 Food/hour (Level 3)
  - **Auto-Collection**: Resources accumulate up to storage capacity, then stop
  - **Storage Capacity**: 1,000 Food (Level 1 storage), 5,000 (Level 2), 20,000 (Level 3)
  - **No Tapping Required**: Check in when you want to spend, not to collect
- **Battle Rewards**: 20-100 Food per battle chest (bronze/silver/gold tier)
- **Exploration**: Realm Map resource nodes (100-500 Food per node, respawns daily)
- **Daily Login**: 500-2,000 Food (Day 7, 14, 21, 28 bonus days)
- **Alliance Donations**: Members can gift Food (100-1,000 per donation)
- **Gold Trading**: 1,000 Gold → 500 Food (emergency conversion)

**Production Rate** (AFK Gathering):
- **Early Game** (1 Granary Level 1): 240 Food/day (10/hour × 24 hours)
- **Mid Game** (2 Granaries Level 2 + 1 Farm Level 1): 2,160 Food/day
- **Late Game** (3 Granaries Level 3 + 2 Farms Level 3): 7,680 Food/day

**Sinks** (How Players Spend Food):
- **Battle Entry Cost**: 20 Food per battle (prevents grinding, encourages AFK production)
- **Unit Deployment**: 50 Food per unit deployed on Realm Map (stack of 5 units = 250 Food)
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

## 5.5.5 Lumber (AFK Resource) - **PHASE 2** ❌ **NOT IN MVP**

**For complete Lumber economy details, see [economy-system.md](economy-system.md) Phase 2 section**

**MVP Status**: Lumber is deferred to Phase 2 (Month 2-3). MVP uses treasure nodes on Realm Map for resource rewards instead of production buildings.

**Definition**: Crafting resource for equipment, building construction, and upgrades.

**Sources** (How Players Earn Lumber):
- **AFK Production** (Auto-Collected):
  - Sawmill: 10 Lumber/hour (Level 1), 20 Lumber/hour (Level 2), 40 Lumber/hour (Level 3)
  - Forest: 50 Lumber/hour (Level 1), 100 Lumber/hour (Level 2), 200 Lumber/hour (Level 3)
  - **Auto-Collection**: Resources accumulate up to storage capacity, then stop
  - **Storage Capacity**: 1,000 Lumber (Level 1 storage), 5,000 (Level 2), 20,000 (Level 3)
  - **No Tapping Required**: Check in when you want to spend, not to collect
- **Battle Rewards**: 20-100 Lumber per battle chest (bronze/silver/gold tier)
- **Exploration**: Realm Map resource nodes (100-500 Lumber per node, respawns daily)
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

## 5.5.6 Ore (AFK Resource) - **PHASE 2** ❌ **NOT IN MVP**

**For complete Ore economy details, see [economy-system.md](economy-system.md) Phase 2 section**

**MVP Status**: Ore is deferred to Phase 2 (Month 2-3). MVP uses treasure nodes on Realm Map for resource rewards instead of production buildings.

**Definition**: Advanced crafting resource for high-tier equipment and building upgrades.

**Sources** (How Players Earn Ore):
- **AFK Production** (Auto-Collected):
  - Mine: 5 Ore/hour (Level 1), 10 Ore/hour (Level 2), 20 Ore/hour (Level 3)
  - Quarry: 25 Ore/hour (Level 1), 50 Ore/hour (Level 2), 100 Ore/hour (Level 3)
  - **Auto-Collection**: Resources accumulate up to storage capacity, then stop
  - **Storage Capacity**: 500 Ore (Level 1 storage), 2,500 (Level 2), 10,000 (Level 3)
  - **No Tapping Required**: Check in when you want to spend, not to collect
- **Battle Rewards**: 10-50 Ore per battle chest (bronze/silver/gold tier)
- **Exploration**: Realm Map resource nodes (50-250 Ore per node, respawns daily)
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

## 5.5.7 Arena Tokens (PvP Currency) - **PHASE 3** ❌ **NOT IN MVP**

**For complete Arena Token economy details, see [economy-system.md](economy-system.md) Phase 3 section**

**MVP Status**: Arena Tokens are deferred to Phase 3 (Month 4-6). MVP is single-player tutorial + Realm Map PvE only (no PvP).

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

## 5.5.8 Energy (Stamina System) - **MVP** ✅

**For complete Energy system details, see [economy-system.md](economy-system.md) MVP section**

**Definition**: Stamina resource that limits battles per day, prevents endless grinding, encourages AFK progression.

**Core Mechanics**:
- **Max Energy**: Based on Player Level
  - Level 1-10: 100 Max Energy
  - Level 11-20: 150 Max Energy
  - Level 21-30: 200 Max Energy
  - Level 31+: 250 Max Energy
- **Battle Cost**: 
  - Tutorial Campaign: 0 Energy (unlimited battles, no interruption)
  - Realm Map Battle: 10 Energy per battle
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
- **Post-Tutorial**: Realm Map battles cost 10 Energy (players learn mechanic without blocking tutorial)

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

## 5.5.9 Realm Map Movement System

**Definition**: Turn-based movement for deployed card stacks on Realm Map, limits exploration pacing.

**Core Mechanics**:
- **Movement Range**: 3 tiles per turn (hex-based Realm Map)
- **Turn Cost**: 1 Movement Point per turn
- **Max Movement Points**: 10 per day (resets at midnight UTC)
- **Movement Point Refill**: None (daily cap only, cannot refill with Gems)

**Movement Rules**:
- **Deployed Stack**: Player deploys hero + units on Realm Map (Step 12 of tutorial)
- **Each Turn**: Player can move stack up to 3 tiles in any direction
- **Obstacles**: Rivers, mountains block movement (must path around)
- **Enemy Tiles**: Moving onto enemy tile triggers battle (costs 10 Energy + 20 Food + 1 Movement Point)
- **Resource Nodes**: Moving onto resource node collects resources (100-500 Food/Lumber/Ore, costs 1 Movement Point)

**Daily Exploration Limit**:
- **10 Movement Points**: Can move 30 tiles/day (3 tiles × 10 turns)
- **Realm Map Size**: 40 tiles total (can explore 75% of map in 1 day if straight line)
- **Realistic Exploration**: Obstacles, battles, backtracking = 5-7 days to fully explore 1 Realm Map
- **Result**: Exploration is paced, can't blitz entire map in 1 session

**Tutorial Integration**:
- **Step 12**: Deploy first stack, move 3 tiles to PvE enemy (costs 1 Movement Point)
- **Step 13**: Battle PvE enemy, win, return to starting tile (costs 1 Movement Point to return)
- **Tooltip**: "You have 10 Movement Points per day. Plan your route carefully!"
- **Post-Tutorial**: Full Realm Map unlocked (40 tiles, 10 Movement Points/day = 4 days to fully explore)

**No Gem Refills** (Intentional):
- **Energy**: Can refill with Gems (whale advantage for battles)
- **Movement Points**: Cannot refill (prevents whales from exploring entire map instantly)
- **Result**: Exploration is time-gated for everyone (F2P and whales explore at same pace)

**Alliance Coordination**:
- **Shared Map**: Alliance members share Realm Map progress (if one member explores tile, all see it)
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

**For exact damage formulas and calculations, see [combat-calculation-spec.md](combat-calculation-spec.md)**

**Schemas**: [battle-schema.json](specs/battle-schema.json), [reward-schema.json](specs/reward-schema.json)

Combat is the heart of Sovereign Territories: turn-based battles on an 8×8 grid with deterministic math (no RNG). Supports both manual control and auto-battle with programmable tactics.

---

## 8.1 Core System (MVP)

### Battle Grid
- **8×8 Tactical Grid**: Chess-style positioning
- **Turn-Based**: Alternating player/enemy turns (no real-time)
- **Initiative**: Faster units act first (Speed stat determines order)
- **Deterministic**: No dice rolls, pure math-based outcomes

### Turn Structure
1. **Movement Phase**: Units move up to their range (1-3 tiles)
2. **Action Phase**: Attack (melee/ranged) or activate ability
3. **Resolution Phase**: Damage calculations, status effects apply

### MVP Combat Formula (Simplified)
```
Damage = Attacker's Attack - Defender's Defense
If Damage < 0, Damage = 0 (no overkill)
If Damage ≥ Defender's Health, unit dies (one-hit removal)
```

**Example**: Fire Archer (30 Attack) vs Water Infantry (10 Defense, 25 Health)
- Damage = 30 - 10 = 20
- Result: Water Infantry takes 20 damage, survives with 5 Health

---

## 8.2 Stacking System (HoMM-Inspired)

**For full stacking rules, see Section 2.6**

### Stack Math (MVP)
- **Stack HP** = `BaseHP × stackSize` (linear scaling)
- **Stack Attack** = `BaseAttack × stackSize` (linear scaling)
- **AoE Vulnerability**: AoE attacks hit ALL units in stack (risk-reward trade-off)

**Example**: 3× Elf Archer (10 HP, 8 Attack each)
- Stack HP = 10 × 3 = 30 HP total
- Stack Attack = 8 × 3 = 24 Attack
- Fireball (20 AoE damage) → kills 2 archers (20 damage / 10 HP = 2 casualties)

---

## 8.3 Auto-Battle & Tactics (MVP)

### Programmable AI
Players set tactics before battle, AI executes automatically:
- **Aggressive**: Focus lowest HP enemies first
- **Defensive**: Prioritize high-threat targets (ranged > melee)
- **Balanced**: Mix of offense/defense based on HP %

### Hero Moments (Phase 2)
- 1-2 manual actions per turn during auto-mode (heal ally, change target)
- Cooldown prevents spam (once per 3 turns)
- Override toggle: Switch to full manual (costs XP penalty)

**TODO: Design 10-20 tactic templates for auto-battle (see gameplay-modes-spec.md)**

---

## 8.4 Win/Loss Conditions

### PvE (MVP)
- **Standard**: Eliminate all enemy units
- **Survival**: Survive X turns (e.g., 10 turns vs waves)
- **Boss**: Reduce boss HP to 0 (may have multiple phases)

### PvP (Phase 3) ❌ NOT IN MVP
- **Elimination**: Kill all opponent units
- **Capture**: Control central flag for 3 turns
- **Points**: Control 5+ tiles at turn 15

---

## 8.5 Phase 2-3 Advanced Features ❌ NOT IN MVP

**For detailed formulas, see [combat-calculation-spec.md](combat-calculation-spec.md)**

### Phase 2: RPG Stats
- **Health/Mana/Stamina** replaces simple HP (see rpg-systems-spec.md)
- **Consumables**: Potions/Scrolls for mid-battle healing
- **Status Effects**: Burn (DoT), Freeze (skip turn), Poison (HP drain)

### Phase 3: Elemental Interactions
- **Rock-Paper-Scissors**: Fire > Earth > Water > Fire
- **Damage Bonus**: 1.5× advantage, 0.75× disadvantage
- **Terrain Modifiers**: Hills (+20% Defense), Water (-50% Movement)

**TODO: Define exact elemental multipliers (see combat-calculation-spec.md Phase 3 section)**
**TODO: Design terrain effect formulas (percentage bonuses, stacking rules)**
**TODO: Create status effect durations (2-5 turns? purge mechanics?)**

---

## Open-Source References

- **Chess Engines** (Stockfish): Deterministic turn-based logic
- **Slay the Spire**: Card-based combat, clear damage formulas
- **Battle Chess Clones**: Grid-based tactics visualization

# SECTION 9: PROGRESSION & BALANCE

> **See [progression-schema.json](specs/progression-schema.json) for complete XP formulas, unlock thresholds, and achievement tracking.**

Progression uses **two parallel systems**: Player Level (account-wide, unlocks features) and Castle Level (per-territory, unlocks buildings/slots). Balance maintained through soft counters, dynamic scaling, and meta shifts.

---

## 9.1 Dual Progression Systems

### Player Level (Account-Wide)

### Player Level (Account-Wide)

**What It Is**: Personal mastery, unlocks content/features across entire game

**How to Level**: Battles (10-100 XP), daily quests (50-200 XP), events, achievements

**Key Unlocks**:
- **Level 10**: Alliance join, PvE events, 25-30 card decks
- **Level 15**: Arena PvP (1v1/3v3), secondary castles (up to 5)
- **Level 20**: Active PvP Maps (open-world), Realm Map, 35-40 card decks
- **Level 30**: Max deck size (50 cards), Alliance Wars, all content unlocked

**F2P Timeline**: Level 30 in 3-6 months of active play (~160,000 XP total)

**Why It Matters**:
- ✅ Persistent (never lost), gates content to prevent overwhelm
- ❌ No direct power (Level 50 with Commons loses to Level 10 with Legendaries)

### Castle Level (Per-Territory)

**What It Is**: Strength/development of specific castle on map (like "base level")

**How to Level**: Holding territories (10 XP/hour), building upgrades (100-500 XP), winning defenses (200 XP)

**Key Benefits**:

| Castle Level | Building Slots | Hero Stacks | Deck Slots | Gold Bonus |
|--------------|----------------|-------------|------------|------------|
| **1** | 5 | 3 | 3 | +0% |
| **10** | 15 | 7 | 7 | +25% |
| **20** | 30 | 15 | 9 | +75% |
| **30** | 50 | 25 | 10 | +150% |

**Why It Matters**:
- ✅ Economic bonuses, territory control, AFK progression
- ❌ Can be lost if castle destroyed (but keep Player Level)

### Lord Skill Tree (Castle Level 5+)

**4 Branches** (1 skill point per castle level):
1. **Economic**: +25% gold, -5% auction fees, +50% storage
2. **Military**: +10% unit stats, +100% siege damage, +50% building HP
3. **Diplomatic**: +25% alliance efficiency, +3 max allies
4. **Arcane**: +50 energy, +5% legendary drop rate, +50% AFK production

**Respec**: 500 gems, once per month

### Multiple Castles (Player Level 15+)

- Hold up to 5 castles (1 main + 4 secondary)
- Each levels independently
- Secondary castles have 50% building slots
- Maintenance: 1,000 gold/day per secondary

---

## 9.2 Deck Management

**Deck Slots** (Progressive Unlocks):
- **Castle Level 1**: 3 deck slots (1 battle deck, 1 building deck, 1 experimental)
- **Castle Level 5**: 5 slots (2 battle, 2 building, 1 flex)
- **Castle Level 10**: 7 slots (3 battle, 3 building, 1 flex)
- **Castle Level 20**: 9 slots (4 battle, 4 building, 1 flex)
**Deck Slots** (Progressive Unlocks):
- Castle Level 1: 3 slots | Level 10: 7 slots | Level 25: 10 slots (max)
- VIP 5: +2 extra slots (12 total)

**Deck Features**:
- Quick switch (1-click dropdown), templates, copy/import/export
- Auto-complete (AI suggests cards), win rate tracking, deck tags
- Share deck codes ("ST-DECK-ABC123"), community deck library

**Deck Constraints**:
- **Battle Decks**: 20-30 cards, max 1 Legendary hero OR 2 Epic heroes
- **Building Decks**: 15-25 cards, max 10 production + 10 defense buildings
- **Theme Bonus**: 20+ cards of same theme = synergy buff

---

## 9.3 Balance Systems

**Difficulty Scaling** (Dynamic):
- Enemy strength scales with Player Level (+10% stats per 5 levels)
- PvE AI adapts tactics based on player performance
- Soft counters: Fire-heavy decks encounter more water enemies
- Meta shifts via patches adjust card power

**Endgame Content** (Infinite Progression):
- **Meta Wars**: Seasonal alliance PvP tournaments
- **Infinite Ladder**: Climb ranks, top tiers unlock cosmetics
- **Player Challenges**: User-generated maps rated by community
- **Legacy Achievements**: Permanent titles across seasons

**Achievements & Titles**:
- Milestones: "Veteran Commander" (Lv 10), "Sovereign Lord" (Lv 30)
- Special: "Whale Hunter" (defeat 10 VIP 5 players), "Card Collector" (500+ unique)

> **See [achievement-schema.json](specs/achievement-schema.json) for complete achievement system and [progression-schema.json](specs/progression-schema.json) for XP formulas.**

---

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
- **Card Detail View**: Tap a card to see stats, attached boosts, star level, options to combine/split, and current deployment (e.g., "Deployed on Territory Map, Blackfort Castle").
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

> **See individual spec files in [docs/specs/](specs/) for schemas, versioning, and data validation.**

Sovereign Territories follows agile development inspired by Clash Royale and League of Legends. Emphasis on rapid prototyping, data-driven balance, and continuous iteration.

---

## 13.1 Development Process

**Agile Structure**:
- 2-week sprints, daily standups, retrospectives
- Core first: Card system, combat, economy before polish
- Weekly playable builds for testing

**Content Pipeline**:
1. Design: Specs using JSON schemas
2. Art: 2.5D sprites, UI, VFX
3. Implementation: Unity + Nakama
4. Testing: QA + automated tests
5. Deployment: Server-side updates (no client download for data)

**Version Control**: Git workflow (feature branches → PR → code review → main)

---

## 13.2 Testing & Quality Assurance

**Automated Testing**:
- Unit tests (80% coverage), integration tests, regression tests
- Headless bots simulate 1000+ AI matches for balance
- CI/CD via GitHub Actions

**Playtesting**:
- Internal alpha (weekly team play), closed beta (100-1000 testers, 4-8 weeks)
- A/B testing: Card balance, UI changes, pricing
- Win rate target: 48-52% for all archetypes

**Performance Targets**:
- 60 FPS on mid-tier mobile (iPhone 12, Samsung S21)
- <1GB RAM usage, <2 second load time, <1% crash rate

---

## 13.3 Analytics & KPIs

**Key Metrics**:
- **Retention**: Day 1 (>40%), Day 7 (>20%), Day 30 (>10%)
- **Engagement**: 2-3 sessions/day, 15-30 min sessions
- **Monetization**: ARPU >$0.50, ARPPU >$10, conversion >3%

**A/B Testing**:
- Feature flags for gradual rollout (10% → 50% → 100%)
- Minimum 10,000 players per variant, instant rollback if metrics degrade

**Tracked Events** (see session-schema.json):
- `battle_start/end`, `card_combined`, `purchase`, `match_result`, `vip_purchase`

**Monitoring**: Grafana (real-time), BigQuery (historical), PagerDuty (alerts)

---

## 13.4 Live Operations

**Content Cadence**:
- **Weekly**: Events, limited offers
- **Bi-Weekly**: Balance patches, bug fixes
- **Monthly**: New cards (3-5), seasonal themes
- **Quarterly**: Expansions (50+ cards, new maps)

**Seasonal Content**:
- 3-month seasons with themes (Norse, Sci-Fi, etc.)
- Battle Pass (50 tiers), leaderboard resets, meta shifts

**Community Engagement**:
- Transparent patch notes, developer blogs
- Daily social media (Twitter, Reddit, Discord)
- Monthly surveys, in-game feedback buttons

---

## 13.5 Content Tools

**Schema-Driven Development**:
- JSON schemas validate all game data (see docs/specs/)
- Code generation: Auto-generate TypeScript/C# types
- Hot reloading: Server-side updates without client patches

**Content Editors**:
- Unity custom inspectors (cards, maps)
- Web dashboards (balancing, events)
- Google Sheets integration for rapid iteration

---

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
- Alliances declare war, fight for control of State/World Map territories
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
   - Add Tier 3 (Realm Map with resource scrambles)
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

---

# 19. Inspirations & Credits

Sovereign Territories is a **multi-genre hybrid** that cherry-picks the best mechanics from decades of gaming while avoiding the tedious grind. Below are the games, systems, and design philosophies that inspire this project.

## 19.1 Core Mechanical Influences

### TCG/CCG (Trading/Collectible Card Games)
- **Pokémon TCG**: Deck-building, rarity tiers, pack opening, evolution mechanics, type advantages
- **Magic: The Gathering**: Mana systems, stack mechanics, instant-speed interactions, legendary rule
- **Hearthstone**: Digital card polish, clear UI/UX, accessible deck sizes
- **Slay the Spire**: Rarity budgets, synergy-driven deck building, relics (equipment)

### Party-Based RPGs
- **Baldur's Gate Series**: Party composition, tactical pause, Health/Mana/Stamina systems, equipment slots
- **Neverwinter Nights**: D&D ruleset adaptation, hero leveling, attribute progression (STR/DEX/INT/WIS/CON/CHA)
- **Diablo Series**: Procedurally generated maps, loot drops, randomized replay value, skill trees
- **Pillars of Eternity**: Deep character progression, engagement mechanics, combat formations

### Tactical Strategy
- **Heroes of Might and Magic III**: Army composition, hero-led armies, turn-based tactical combat, resource management, castle sieges
- **Fire Emblem Series**: Grid-based combat, unit positioning, terrain effects, permadeath tension (applied to Ironman mode)
- **XCOM Series**: Squad tactics, overwatch mechanics, cover systems, multi-hero synergies

### Territorial Conquest
- **Risk**: Map control, alliance dynamics, seasonal wars, territory capture
- **Diplomacy**: Alliance negotiation, strategic betrayal, fog of war
- **Civilization Series**: Territory expansion, multi-tier maps (city/region/world), victory conditions

### Real-Time Strategy (RTS)
- **Supreme Commander/Total Annihilation**: Deck = army composition (no production queues), macro-scale thinking
- **Warcraft II/III**: Hero units, army formations, fog of war mechanics
- **StarCraft**: Asymmetric factions, micro/macro balance, strategic depth

### Tabletop Wargaming
- **Warhammer 40,000/Fantasy**: 3D hero figurines on maps, visual unit stacks, army painting themes, faction identity
- **D&D Miniatures**: Grid combat, line-of-sight rules, terrain interactions

### Roguelike/Roguelite
- **Slay the Spire**: Rarity budgets, procedural encounters, deck synergy rewards
- **Hades**: Persistent progression (meta-unlocks), replayable runs with variety
- **Diablo**: Randomized maps, loot tables, replay incentive

### Idle/AFK Games
- **AFK Arena**: Offline progression, auto-battle modes, daily login rewards
- **Idle Heroes**: Hero collection, fusion mechanics, idle resource generation
- **Mobile Legends Adventure**: AFK campaign progression, energy systems

### Mobile Strategy
- **Clash Royale**: Real-time PvP matchmaking, deck-based combat, seasonal ladders
- **Clash of Clans**: Alliance wars, base layout strategy (adapted to castle building)

## 19.2 Thematic Inspirations

### Medieval Fantasy
- **Game of Thrones/ASOIAF**: Political intrigue, alliance dynamics, seasonal campaigns
- **Lord of the Rings**: Epic scale, multiple factions, thematic elements

### Norse Mythology
- **God of War (2018)**: Norse aesthetic, hero progression, epic bosses
- **Vikings (TV Series)**: Exploration, conquest, clan warfare

### Historical Strategy
- **Total War Series**: Large-scale battles, territorial control, diplomacy
- **Age of Empires**: Resource management (adapted to AFK systems), civilization progression

### Sci-Fi/Modern Warfare
- **StarCraft**: Asymmetric faction balance, macro-scale thinking
- **Command & Conquer**: Base building (adapted to static castle layouts), tech trees

### Board Games
- **Catan**: Resource tile placement (economy cards on map tiles)
- **Dominion**: Deck-building, engine-building mechanics
- **Small World**: Territory control with limited unit counts

## 19.3 Design Philosophy

### What We **EMBRACE** (The Fun Parts):
✅ **Card Collecting**: Opening packs, hunting rare cards, building themed decks  
✅ **Hero Progression**: Leveling heroes, Health/Mana/Stamina stats, equipment upgrades  
✅ **Strategic Depth**: Deck composition, tactical positioning, formations, synergy combos  
✅ **Map Exploration**: Multi-tier maps (Global/State/County/Battle), PvE campaigns  
✅ **Come-Back Gameplay**: Daily rewards, quest chains, offline progression (no mandatory grind)  
✅ **Alliance Wars**: 50v50 coordinated attacks, shared victories, territory control  
✅ **AFK Progression**: Place economy cards on tiles for passive income (respects player time)  

### What We **AVOID** (The Tedious Parts):
❌ **Forced Resource Gathering**: No tap-tap-tap collection, no timber/stone/ore micro-management  
❌ **Waiting for Production**: No 2-hour unit queues, no "upgrade in progress" timers  
❌ **Repetitive Base Building**: No rebuilding defenses daily, no compulsive wall repairs  
❌ **Grind-Wall Monetization**: No $99 speedup packs, no pay-to-skip-pain mechanics  
❌ **Unfair Matchmaking**: No whale vs. F2P stomps, no forced PvP raids  

**Core Principle**: If a mechanic makes you say "ugh, I have to do this again?", we either automate it (AFK systems), make it optional (tactics cards), or remove it entirely. The game respects your time and rewards **strategic thinking**, not **compulsive clicking**.

---

**Final Note**: Sovereign Territories stands on the shoulders of giants. Every card draw, every tactical decision, every alliance forged—these mechanics were refined over decades by brilliant designers. This project honors their work by combining the **best parts** into something new, while cutting the **tedious parts** that players endure out of habit, not fun.

---

**Document Version**: 2.0 (Last Updated: January 2025)  
**Lines**: 5,405+ (Condensed from 6,807 in Phase 7-10 reorganization)  
**Target**: <6,000 lines (✅ ACHIEVED: 1,806 lines below target)
