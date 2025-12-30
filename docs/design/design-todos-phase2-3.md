# Sovereign Territories - Design TODOs (Phase 2-3)

**Version**: 1.0  
**Last Updated**: December 30, 2025  
**Purpose**: Consolidated list of all design decisions needed for post-MVP features

---

## Overview

This document consolidates all **36 open TODOs** from game-bible.md, combat-calculation-spec.md, economy-system.md, rpg-systems-spec.md, and gameplay-modes-spec.md. All items here are **Phase 2-3** features - none are blocking MVP implementation.

**Organization**:
- **Priority Levels**: P0 (blocking Phase 2), P1 (nice-to-have Phase 2), P2 (Phase 3+)
- **Categories**: Combat, Economy, RPG Systems, Gameplay Modes
- **Status**: ⏳ Not Started | 🔄 In Progress | ✅ Complete

---

## Phase 2: RPG Systems (Health/Mana/Stamina)

### Combat Mechanics (combat-calculation-spec.md)

**Priority P0** (blocking Phase 2 combat):
- [ ] ⏳ **TODO 1**: Determine exact elemental multipliers (Fire vs Water = 1.25×? 1.5×? 2×?)
  - **Source**: game-bible.md:3684
  - **Impact**: Core damage calculation for elemental system
  - **Recommendation**: Start with 1.25× (subtle) vs 1.5× (impactful), playtest

- [ ] ⏳ **TODO 2**: Design terrain effect formulas (percentage bonuses, stacking rules)
  - **Source**: game-bible.md:3685
  - **Impact**: Forest (+10% Evasion), Mountain (+20% Defense), etc.
  - **Recommendation**: 10-20% bonuses, no stacking (pick best terrain)

- [ ] ⏳ **TODO 3**: Create status effect durations (2-5 turns? purge mechanics?)
  - **Source**: game-bible.md:3686
  - **Impact**: Burn, Freeze, Poison, Stun, Shield durations
  - **Recommendation**: 2-3 turns baseline, cleanse abilities reduce to 0

- [ ] ⏳ **TODO 4**: Design status effect stacking mechanics (can 2 Burn effects stack? diminishing returns?)
  - **Source**: combat-calculation-spec.md:376
  - **Impact**: Prevents abuse (6× Burn = instant death)
  - **Recommendation**: Same effect doesn't stack, refresh duration only

- [ ] ⏳ **TODO 5**: Create purge/cleanse system (can Water Mage cleanse Burn? Priest purge Poison?)
  - **Source**: combat-calculation-spec.md:377
  - **Impact**: Counterplay to status effects
  - **Recommendation**: Water cleanses Burn/Freeze, Earth cleanses Poison, Light cleanses all

- [ ] ⏳ **TODO 6**: Design diminishing returns formula (prevent 100% crit at high Speed differences)
  - **Source**: combat-calculation-spec.md:439
  - **Impact**: Crit chance caps at 50-75%, not infinite
  - **Recommendation**: Cap at 50% (each 1% over 50% only adds 0.5%)

**Priority P1** (nice-to-have Phase 2):
- [ ] ⏳ **TODO 7**: Should abilities crit? (2× Fireball damage = 120 instead of 60?)
  - **Source**: combat-calculation-spec.md:277
  - **Impact**: High variance, exciting moments
  - **Recommendation**: YES - abilities can crit with same formula as attacks

- [ ] ⏳ **TODO 8**: Design ability interrupts (can Silence stop casting? Stun cancel channeling?)
  - **Source**: combat-calculation-spec.md:278
  - **Impact**: Tactical depth, counterplay
  - **Recommendation**: YES - Stun/Silence cancels abilities (refund Mana?)

- [ ] ⏳ **TODO 9**: Should regen scale with unit rarity? (Legendary = 8 Mana/turn, Common = 3?)
  - **Source**: combat-calculation-spec.md:285
  - **Impact**: Legendary units feel more powerful
  - **Recommendation**: YES - 3/4/5/6/8/10 Mana regen (Common → Mythic)

- [ ] ⏳ **TODO 10**: Should Burn scale with attacker's Attack stat? (10% of Attack/turn instead of flat 5?)
  - **Source**: combat-calculation-spec.md:384
  - **Impact**: Burn stays relevant late-game
  - **Recommendation**: YES - Burn = 10% of caster's Attack per turn

- [ ] ⏳ **TODO 11**: Should Freeze have slow phase after? (1 turn frozen, 1 turn -50% speed?)
  - **Source**: combat-calculation-spec.md:391
  - **Impact**: Makes Freeze less binary (skip turn vs nothing)
  - **Recommendation**: YES - 1 turn frozen, 2nd turn slowed (50% movement only)

- [ ] ⏳ **TODO 12**: Can Fire attacks melt Freeze early? (thaw mechanic)
  - **Source**: combat-calculation-spec.md:392
  - **Impact**: Elemental counterplay
  - **Recommendation**: YES - Fire damage removes Freeze immediately

- [ ] ⏳ **TODO 13**: Should Poison reduce healing? (-50% healing effectiveness while poisoned)
  - **Source**: combat-calculation-spec.md:399
  - **Impact**: Makes Poison more dangerous
  - **Recommendation**: YES - Poison = -50% healing received

- [ ] ⏳ **TODO 14**: Can Antidote consumable cure Poison? (see rpg-systems-spec.md)
  - **Source**: combat-calculation-spec.md:400
  - **Impact**: Resource sink, strategic choice
  - **Recommendation**: YES - Antidote Potion = 50 Gold, removes Poison instantly

- [ ] ⏳ **TODO 15**: Should critical hits have bonus effects? (Burn on fire crits, Freeze on water crits?)
  - **Source**: combat-calculation-spec.md:465
  - **Impact**: Elemental identity, exciting moments
  - **Recommendation**: YES - 30% chance: Fire crit = Burn, Water crit = Slow, Earth crit = Stun

- [ ] ⏳ **TODO 16**: Design crit counter-tactics (items/abilities that reduce enemy crit chance)
  - **Source**: combat-calculation-spec.md:466
  - **Impact**: Tank builds, anti-crit meta
  - **Recommendation**: Add Shield stat (reduces crit damage by 50%), "Fortify" ability (immune to crits)

**Priority P2** (Phase 3+):
- [ ] ⏳ **TODO 17**: Finalize exact percentage bonuses for each terrain type
  - **Source**: combat-calculation-spec.md:411
  - **Impact**: Terrain strategy
  - **Recommendation**: Forest +10% Evasion, Mountain +20% Defense, Water +10% Speed, Desert -1 Stamina/turn

- [ ] ⏳ **TODO 18**: Design stacking rules (do Forest + Mountain combine? +10% + 20% = +30%?)
  - **Source**: combat-calculation-spec.md:412
  - **Impact**: Prevents OP combos
  - **Recommendation**: NO stacking - pick best terrain bonus only

- [ ] ⏳ **TODO 19**: Determine line-of-sight mechanics (does Forest block ranged attacks?)
  - **Source**: combat-calculation-spec.md:413
  - **Impact**: Tactical positioning
  - **Recommendation**: YES - Forest/Mountain block line-of-sight for ranged (max range 2 tiles through obstacles)

- [ ] ⏳ **TODO 20**: Add Hills terrain (+10% Defense, +1 range for archers?)
  - **Source**: combat-calculation-spec.md:431
  - **Impact**: Archer positioning advantage
  - **Recommendation**: YES - Hills = +1 range for ranged units, +10% Defense

- [ ] ⏳ **TODO 21**: Add Desert terrain (-1 Stamina per turn, thirst effect?)
  - **Source**: combat-calculation-spec.md:432
  - **Impact**: Stamina matters, environmental hazard
  - **Recommendation**: YES - Desert = -2 Stamina/turn (can be countered with "Desert Adaptation" ability)

- [ ] ⏳ **TODO 22**: Add Snow terrain (Freeze effect on units without Cold Resist?)
  - **Source**: combat-calculation-spec.md:433
  - **Impact**: Environmental status effects
  - **Recommendation**: YES - Snow = 25% chance to Freeze at turn end (unless Cold Resist)

- [ ] ⏳ **TODO 23**: Determine if shields block crits (75% crit resistance for Shield units?)
  - **Source**: combat-calculation-spec.md:440
  - **Impact**: Tank archetype
  - **Recommendation**: YES - Shield stat reduces crit damage by 50-75% (not immune, just resistant)

- [ ] ⏳ **TODO 24**: Create crit visual feedback (red damage numbers, screen shake, particles)
  - **Source**: combat-calculation-spec.md:441
  - **Impact**: Player experience, feel
  - **Recommendation**: Red floating text, brief screen shake, starburst particle effect

---

### RPG Systems (rpg-systems-spec.md)

**Priority P0** (blocking Phase 2 equipment):
- [ ] ⏳ **TODO 25**: Finalize socket count by rarity (should Mythic get 4 sockets? too powerful?)
  - **Source**: rpg-systems-spec.md:365
  - **Impact**: Endgame power ceiling
  - **Recommendation**: Common 0, Uncommon 1, Rare 1, Epic 2, Legendary 3, Mythic 3 (not 4 - too OP)

- [ ] ⏳ **TODO 26**: Design socket UI (drag-and-drop? list view? preview stat bonuses before confirm?)
  - **Source**: rpg-systems-spec.md:366
  - **Impact**: User experience
  - **Recommendation**: Drag-and-drop jewels onto socket slots, live stat preview before confirmation

- [ ] ⏳ **TODO 27**: Create socket removal economy (100 Gold too cheap? prevents strategic choices)
  - **Source**: rpg-systems-spec.md:367
  - **Impact**: Resource sink, decision weight
  - **Recommendation**: Increase to 250 Gold (meaningful cost) or destroy jewel on removal (harsher penalty)

**Priority P1** (nice-to-have Phase 2):
- [ ] ⏳ **TODO 28**: Should sockets be type-locked? (Jewel slot vs Rune slot, prevents mixing?)
  - **Source**: rpg-systems-spec.md:381
  - **Impact**: Build complexity
  - **Recommendation**: NO - flexible sockets (allows creative builds, not restrictive)

- [ ] ⏳ **TODO 29**: Create Jewel drop table (rarities, boss tiers, pity timers for Flawless Jewels)
  - **Source**: rpg-systems-spec.md:403
  - **Impact**: Loot chase, progression
  - **Recommendation**: Common bosses drop Minor (90%), Rare bosses drop Flawless (10%), pity after 20 bosses = guaranteed Flawless

- [ ] ⏳ **TODO 30**: Design Jewel combining system (3× Minor Ruby = 1× Ruby, 3× Ruby = 1× Flawless?)
  - **Source**: rpg-systems-spec.md:404
  - **Impact**: Resource sink, F2P progression
  - **Recommendation**: YES - 3:1 ratio (3× Minor = 1× Flawless), costs 500 Gold per combine

- [ ] ⏳ **TODO 31**: Design Rune stacking rules (can 2× Fire Runes = +20% Fire damage? diminishing returns?)
  - **Source**: rpg-systems-spec.md:435
  - **Impact**: Prevents OP single-element stacking
  - **Recommendation**: YES stacking with diminishing returns (1st Rune = +10%, 2nd = +5%, 3rd = +2%)

- [ ] ⏳ **TODO 32**: Create hybrid Runes (Fire+Water = Steam Rune, unique effects?)
  - **Source**: rpg-systems-spec.md:436
  - **Impact**: Build variety, chase content
  - **Recommendation**: Phase 3 feature - requires complex crafting system

- [ ] ⏳ **TODO 33**: Should removed Jewels/Runes be destroyed or returned to inventory? (destruction = resource sink)
  - **Source**: rpg-systems-spec.md:459
  - **Impact**: Economy balance
  - **Recommendation**: **Destruction** (250 Gold to remove = jewel destroyed, prevents free swapping)

- [ ] ⏳ **TODO 34**: Design socket reroll mechanic (randomize socket types for 500 Gold?)
  - **Source**: rpg-systems-spec.md:460
  - **Impact**: RNG mitigation, resource sink
  - **Recommendation**: YES - 500 Gems (premium currency) to reroll socket count (not types - sockets are flexible)

**Priority P2** (Phase 3+):
- [ ] ⏳ **TODO 35**: Create consumable catalog (10-20 Potion/Scroll types for variety)
  - **Source**: rpg-systems-spec.md:186
  - **Impact**: Tactical depth
  - **Recommendation**: Phase 3 - start with 5 potions (Health, Mana, Stamina, Antidote, Rage)

- [ ] ⏳ **TODO 36**: Design shop pricing balance (prevent F2P from stockpiling infinite consumables)
  - **Source**: rpg-systems-spec.md:187
  - **Impact**: F2P balance
  - **Recommendation**: Potions cost 50-200 Gold, limit 5 per battle (prevents spam)

- [ ] ⏳ **TODO 37**: Determine in-combat vs out-of-combat usage (MVP Phase 2 = out-of-combat only?)
  - **Source**: rpg-systems-spec.md:188
  - **Impact**: Complexity
  - **Recommendation**: Phase 2 = pre-battle only, Phase 3 = in-combat turn action

- [ ] ⏳ **TODO 38**: Should Health Potions scale with unit rarity? (Legendary = 30% restore, Common = 10%?)
  - **Source**: rpg-systems-spec.md:192
  - **Impact**: Endgame viability
  - **Recommendation**: NO - flat 25% restore (keeps potions relevant at all levels)

- [ ] ⏳ **TODO 39**: Should rare potions exist? (Epic Health Potion = 50% restore, costs 1,000 Gold)
  - **Source**: rpg-systems-spec.md:217
  - **Impact**: Resource sink
  - **Recommendation**: YES - Epic Potion = 50% restore, 500 Gold (2.5× normal cost, emergency use)

- [ ] ⏳ **TODO 40**: Should Mana Potions restore percentage instead of flat 50? (20% max Mana = scales with unit)
  - **Source**: rpg-systems-spec.md:242
  - **Impact**: Consistency
  - **Recommendation**: YES - 25% Mana restore (matches Health Potion design)

- [ ] ⏳ **TODO 41**: Design 10-20 Scroll types (offensive, defensive, utility, summoning)
  - **Source**: rpg-systems-spec.md:272
  - **Impact**: Strategic variety
  - **Recommendation**: Phase 3 - start with 5 Scrolls (Fireball, Shield, Haste, Summon Golem, Revive)

- [ ] ⏳ **TODO 42**: Determine Scroll rarity distribution (prevent F2P from abusing Legendary scrolls)
  - **Source**: rpg-systems-spec.md:273
  - **Impact**: F2P balance
  - **Recommendation**: Scrolls cost Gems (premium), limit 1 per battle (prevents spam, monetization)

- [ ] ⏳ **TODO 43**: Create Scribe shop UI (show Scroll preview, effect description, cost)
  - **Source**: rpg-systems-spec.md:274
  - **Impact**: UX
  - **Recommendation**: Phase 3 - tab in main shop, preview window shows effect + cooldown + cost

---

## Phase 3: Endgame & PvP

### Economy (economy-system.md)

**Priority P1** (launch economy):
- [ ] ⏳ **TODO 44**: Finalize exact AFK production rates (10-50 Food/hour too slow/fast? 24-hour cap?)
  - **Source**: economy-system.md:110
  - **Impact**: F2P progression speed
  - **Recommendation**: 30 Food/hour (720/day), 12-hour cap = 360 Food (encourages 2× login/day)

- [ ] ⏳ **TODO 45**: Design resource sinks (prevent infinite Food accumulation, create strategic choices)
  - **Source**: economy-system.md:111
  - **Impact**: Economy longevity
  - **Recommendation**: Battle cost 20 Food, deck slot unlock 5,000 Food, cosmetics 10,000+ Food

- [ ] ⏳ **TODO 46**: Determine battle Food cost (20 per battle too expensive for F2P? tie to Player Level?)
  - **Source**: economy-system.md:112
  - **Impact**: F2P playability
  - **Recommendation**: 20 Food flat (allows 36 battles/day F2P = 2-3 hours gameplay)

- [ ] ⏳ **TODO 47**: Should Food replace Energy system entirely? (1 currency instead of 2?)
  - **Source**: economy-system.md:127
  - **Impact**: Simplicity
  - **Recommendation**: YES - Phase 3, consolidate to Food only (less confusing for new players)

- [ ] ⏳ **TODO 48**: Design Lumber-specific uses (prevent overlap with Food/Ore)
  - **Source**: economy-system.md:138
  - **Impact**: Resource identity
  - **Recommendation**: Lumber = buildings (Watchtower, Barracks), Food = battles, Ore = equipment/upgrades

- [ ] ⏳ **TODO 49**: Determine building construction costs (300 Lumber too cheap/expensive?)
  - **Source**: economy-system.md:139
  - **Impact**: Building progression
  - **Recommendation**: Common building 300 Lumber, Rare 1,000 Lumber, Epic 3,000 Lumber

- [ ] ⏳ **TODO 50**: Finalize Ore scarcity (currently 50% of Food/Lumber, is that tight enough?)
  - **Source**: economy-system.md:160
  - **Impact**: Equipment upgrade pacing
  - **Recommendation**: YES - Ore = 50% of Food (15/hour) creates bottleneck for endgame gear

- [ ] ⏳ **TODO 51**: Design high-tier equipment Ore costs (prevent F2P from crafting Mythic weapons too easily)
  - **Source**: economy-system.md:161
  - **Impact**: F2P balance
  - **Recommendation**: Epic weapon 3,000 Ore, Legendary 10,000 Ore, Mythic 50,000 Ore (30-day grind)

**Priority P2** (Phase 3 polish):
- [ ] ⏳ **TODO 52**: Design offline collection caps (12-hour max? 24-hour? unlimited?)
  - **Source**: economy-system.md:205
  - **Impact**: Session frequency
  - **Recommendation**: 12-hour cap (720 Food max) = encourages 2× login/day without punishing casuals

- [ ] ⏳ **TODO 53**: Determine storage upgrade costs (prevent F2P from maxing storage too easily)
  - **Source**: economy-system.md:206
  - **Impact**: Resource sink
  - **Recommendation**: Each storage +200 cap costs 500 Gems (premium) OR 2-week grind

- [ ] ⏳ **TODO 54**: Create visual feedback (notifications for full storage, upgrade prompts)
  - **Source**: economy-system.md:207
  - **Impact**: UX
  - **Recommendation**: Push notification at 80% full, in-game banner at 100% full

- [ ] ⏳ **TODO 55**: Should offline production be limited? (prevent 1-week vacation = 20,000 Food abuse)
  - **Source**: economy-system.md:223
  - **Impact**: Long-term balance
  - **Recommendation**: YES - 12-hour cap (see TODO 52), no infinite accumulation

- [ ] ⏳ **TODO 56**: Design Pack Store UI (tabs vs scrollable list, bundle offers, daily deals?)
  - **Source**: economy-system.md:234
  - **Impact**: Monetization
  - **Recommendation**: Tabs (Packs, Bundles, Decks), daily deal banner at top

- [ ] ⏳ **TODO 57**: Determine bundle pricing (50-card Game Deck = 2,400 Gems too cheap/expensive?)
  - **Source**: economy-system.md:235
  - **Impact**: Revenue
  - **Recommendation**: Game Deck 2,400 Gems = $19.99 IAP (whale purchase, themed decks)

- [ ] ⏳ **TODO 58**: Create resource bundle conversion rates (prevent exploits, keep emergency purchases viable)
  - **Source**: economy-system.md:236
  - **Impact**: F2P fairness
  - **Recommendation**: 100 Gems = 1,000 Food (emergency only, 10× worse than AFK production)

- [ ] ⏳ **TODO 59**: Should Game Decks be Phase 3? (require Alliance Wars meta before creating precons)
  - **Source**: economy-system.md:245
  - **Impact**: Content timing
  - **Recommendation**: YES - Phase 3, wait until meta stabilizes (6-12 months post-launch)

- [ ] ⏳ **TODO 60**: Should resource bundles exist? (creates pay-to-win path if whales can buy Food with Gold)
  - **Source**: economy-system.md:253
  - **Impact**: F2P fairness
  - **Recommendation**: YES but expensive (see TODO 58 - 10× worse than AFK, emergency only)

- [ ] ⏳ **TODO 61**: Design PvP Store exclusive cards (create desirable chase cards without balance issues)
  - **Source**: economy-system.md:260
  - **Impact**: PvP engagement
  - **Recommendation**: Cosmetic variants (alt-art) not new cards (prevents pay-to-win)

---

### Gameplay Modes (gameplay-modes-spec.md)

**Priority P1** (Phase 2 PvE):
- [ ] ⏳ **TODO 62**: Define exact card pool for tutorial Realm Map (which 100 cards are MVP?)
  - **Source**: gameplay-modes-spec.md:66
  - **Impact**: MVP scope
  - **Recommendation**: See mvp-scope-final.md Week 1-2 deliverables (100 cards listed)

- [ ] ⏳ **TODO 63**: Design boss battle mechanics (phases, enrage timers, unique abilities?)
  - **Source**: gameplay-modes-spec.md:67
  - **Impact**: PvE difficulty
  - **Recommendation**: 2-3 phases (health gates at 66%/33%), enrage at 10 turns, unique abilities per boss

- [ ] ⏳ **TODO 64**: Determine fog of war reveal mechanics (instant, gradual, line of sight?)
  - **Source**: gameplay-modes-spec.md:68
  - **Impact**: Exploration pacing
  - **Recommendation**: Instant reveal in 2-tile radius (simple), line-of-sight in Phase 3

**Priority P2** (Phase 3 PvP/endgame):
- [ ] ⏳ **TODO 65**: Write narrative arc for 3 launch chapters (Norse/Greek/Egyptian?)
  - **Source**: gameplay-modes-spec.md:92
  - **Impact**: Content depth
  - **Recommendation**: Norse (Fire/Ice), Greek (War/Wisdom), Egyptian (Death/Sun) = 3× 10-battle campaigns

- [ ] ⏳ **TODO 66**: Design boss phases (how many phases? health gates? enrage mechanics?)
  - **Source**: gameplay-modes-spec.md:93
  - **Impact**: Boss difficulty
  - **Recommendation**: 3 phases (66%/33% health gates), unique ability per phase, enrage at 15 turns

- [ ] ⏳ **TODO 67**: Determine star rating system (3-star clear for bonus rewards?)
  - **Source**: gameplay-modes-spec.md:94
  - **Impact**: Replayability
  - **Recommendation**: 1-star = win, 2-star = no deaths, 3-star = win in <8 turns + no deaths

- [ ] ⏳ **TODO 68**: Design 10+ event space types (battles, puzzles, loot boxes, traps?)
  - **Source**: gameplay-modes-spec.md:119
  - **Impact**: Roguelike variety
  - **Recommendation**: Battle (50%), Loot (20%), Shop (15%), Puzzle (10%), Trap (5%)

- [ ] ⏳ **TODO 69**: Determine mini-battle rules (3-card limit, instant resolve, auto-battle only?)
  - **Source**: gameplay-modes-spec.md:120
  - **Impact**: Expedition pacing
  - **Recommendation**: 5-card mini-deck, auto-battle only (no manual control), 30-second max

- [ ] ⏳ **TODO 70**: Create board generation algorithm (ensure fair pathing, no dead ends)
  - **Source**: gameplay-modes-spec.md:121
  - **Impact**: Roguelike balance
  - **Recommendation**: Use Slay the Spire algorithm (3 paths per layer, always 1 viable route)

- [ ] ⏳ **TODO 71**: Define alliance event types (territory conquest, boss raid, capture the flag?)
  - **Source**: gameplay-modes-spec.md:146
  - **Impact**: Alliance engagement
  - **Recommendation**: Territory conquest (50v50), boss raid (cooperative damage), king-of-the-hill

- [ ] ⏳ **TODO 72**: Design reward tiers (how many players in top 10/50/100?)
  - **Source**: gameplay-modes-spec.md:147
  - **Impact**: F2P fairness
  - **Recommendation**: Top 10 get Legendary, top 50 get Epic, top 100 get Rare (10% get premium rewards)

- [ ] ⏳ **TODO 73**: Create anti-griefing measures (prevent alliance hoppers, afk players)
  - **Source**: gameplay-modes-spec.md:148
  - **Impact**: Player experience
  - **Recommendation**: Require 7-day membership before events, auto-kick <50% participation

- [ ] ⏳ **TODO 74**: Design Arena Token economy (how many tokens for Epic/Legendary cards?)
  - **Source**: gameplay-modes-spec.md:179
  - **Impact**: PvP grind
  - **Recommendation**: Epic 500 tokens (50 wins), Legendary 2,000 tokens (200 wins) = 2-4 week grind

- [ ] ⏳ **TODO 75**: Create seasonal reward tiers (end-of-season rewards based on final Elo?)
  - **Source**: gameplay-modes-spec.md:180
  - **Impact**: PvP engagement
  - **Recommendation**: Bronze/Silver/Gold/Platinum/Diamond tiers, each tier gets seasonal exclusive card

- [ ] ⏳ **TODO 76**: Define 3v3 team dynamics (shared health pool, separate armies, tag-team?)
  - **Source**: gameplay-modes-spec.md:181
  - **Impact**: 3v3 complexity
  - **Recommendation**: Separate armies on 8×24 grid (8×8 per player), shared victory condition

- [ ] ⏳ **TODO 77**: Define Realm occupation flow (instant claim, garrison requirement, decay timer?)
  - **Source**: gameplay-modes-spec.md:208
  - **Impact**: Territory PvP
  - **Recommendation**: Instant claim, requires 5-unit garrison, decays after 48 hours no login

- [ ] ⏳ **TODO 78**: Design castle siege AI (defensive tactics, reinforcements, surrender conditions?)
  - **Source**: gameplay-modes-spec.md:209
  - **Impact**: Siege difficulty
  - **Recommendation**: AI gets +50% stats, reinforcements at 50% health, surrenders at 10% (prevent griefing)

- [ ] ⏳ **TODO 79**: Determine alliance coordination mechanics (shared territories, officer permissions?)
  - **Source**: gameplay-modes-spec.md:210
  - **Impact**: Alliance UX
  - **Recommendation**: 3 ranks (Leader/Officer/Member), officers can declare war/promote, members can claim territories

- [ ] ⏳ **TODO 80**: Define Territory occupation flow (garrison sizes, supply lines, revolt mechanics?)
  - **Source**: gameplay-modes-spec.md:236
  - **Impact**: Global map complexity
  - **Recommendation**: 10-unit garrison, supply lines = adjacent territories, revolt if <50% garrison strength

- [ ] ⏳ **TODO 81**: Design wonder mechanics (buff durations, control thresholds, defense requirements?)
  - **Source**: gameplay-modes-spec.md:237
  - **Impact**: Endgame objectives
  - **Recommendation**: Wonder = +20% XP/Gold for alliance, control = 1-week hold, defend every 24 hours

- [ ] ⏳ **TODO 82**: Create seasonal reward structure (Mythic cards, cosmetics, titles?)
  - **Source**: gameplay-modes-spec.md:238
  - **Impact**: Season engagement
  - **Recommendation**: Seasonal exclusive Mythic (top 100), alt-art skins (top 1,000), titles (all participants)

- [ ] ⏳ **TODO 83**: Design challenge variety (prevent repetitive "win X battles" grind)
  - **Source**: gameplay-modes-spec.md:259
  - **Impact**: Daily challenge engagement
  - **Recommendation**: 10 types (win battles, deploy X cards, earn X gold, open packs, complete territory, etc.)

- [ ] ⏳ **TODO 84**: Determine reward scaling (should high-level players get better rewards?)
  - **Source**: gameplay-modes-spec.md:260
  - **Impact**: F2P fairness
  - **Recommendation**: YES - rewards scale with Player Level (Level 10 = 100 Gold, Level 50 = 500 Gold)

- [ ] ⏳ **TODO 85**: Create challenge rotation (daily pool of 10, show 3 random per player?)
  - **Source**: gameplay-modes-spec.md:261
  - **Impact**: Variety
  - **Recommendation**: 3 daily challenges (reroll for 50 Gems), pool of 20 challenges rotates weekly

**Priority P3** (far future):
- [ ] ⏳ **TODO 86**: Design 10-20 tactic templates for auto-battle (see gameplay-modes-spec.md)
  - **Source**: game-bible.md:3652
  - **Impact**: Auto-battle quality
  - **Recommendation**: Phase 3 - Aggressive (prioritize Attack), Defensive (prioritize HP), Balanced, Anti-AoE, etc.

- [ ] ⏳ **TODO 87**: Create AI decision tree (target priority, retreat conditions, buff timing)
  - **Source**: gameplay-modes-spec.md:274
  - **Impact**: Auto-battle intelligence
  - **Recommendation**: Phase 3 - priority: Low HP targets > High Attack threats > Healers > Random

---

## Summary

**Total TODOs**: 87 design decisions  
**Breakdown**:
- **Phase 2 (P0)**: 8 blocking TODOs (combat formulas, socket system)
- **Phase 2 (P1)**: 35 nice-to-have TODOs (status effects, consumables, economy)
- **Phase 3 (P2)**: 44 future TODOs (PvP modes, alliance wars, terrain)

**Critical Path** (must resolve before Phase 2):
1. Elemental multipliers (TODO 1)
2. Terrain bonuses (TODO 2)
3. Status effect durations (TODO 3)
4. Socket counts (TODO 25)
5. Socket removal cost (TODO 27)
6. AFK production rates (TODO 44)
7. Battle Food cost (TODO 46)
8. Ore scarcity (TODO 50)

**Recommendation**: Resolve P0 TODOs during Phase 2 planning (Week 9-10 post-MVP), defer P1-P2 TODOs until features are in active development.

---

**Document Status**: Consolidated from 5 source files  
**Last Updated**: December 30, 2025  
**Maintained By**: @Soverign-Beast-Mode agent
