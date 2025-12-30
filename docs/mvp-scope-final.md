# MVP Scope Final - 8-Week Implementation Roadmap

**Last Updated**: December 30, 2025  
**Status**: Ready for Unity implementation  
**Target Completion**: 8 weeks (2 months)  
**Related**: [game-bible.md](game-bible.md), [tutorial-flow.md](tutorial-flow.md), [economy-system.md](economy-system.md)

---

## MVP Philosophy

**Core Focus**: Prove the game loop works before adding complexity.
- ✅ Tutorial (28 steps, 0-60 minutes, gets Sovereign to Level 2)
- ✅ Deck building (6 Trainer Deck options, 20-card decks)
- ✅ Pack opening (Standard/Element/Epic Packs, collector appeal)
- ✅ Realm Map exploration (40 Locations, HoMM-style movement)
- ✅ Simple combat (Attack/Defense, no RPG stats yet)
- ❌ No Food/Lumber/Ore economy (Phase 2)
- ❌ No PvP (Phase 3)
- ❌ No alliances (Phase 3)
- ❌ No Territory/World Maps (Phase 3)

**Success Metric**: Player completes tutorial, builds custom deck, wins 5 Realm Map battles, buys 1 pack with earned Gold. If this feels fun, proceed to Phase 2.

---

## Week-by-Week Breakdown

### Week 1-2: Card System & Tutorial UI

**Card Data** (~100 cards total):
- ✅ 6 Epic heroes (2 per element: Fire, Water, Earth)
  - Flame Warlord, Inferno Pyromancer (Fire)
  - Tidal Guardian, Stormcaller Aquamancer (Water)
  - Stone Sentinel, Earthshaker Geomancer (Earth)
- ✅ 30 Units (10 per element)
  - Fire: Goblin Raiders, Flame Imps, Phoenix Hatchlings
  - Water: Elven Archers, Water Elementals, Sea Serpents
  - Earth: Dwarf Warriors, Stone Golems, Treants
- ✅ 20 Buildings (economy + military)
  - Granary, Sawmill, Mine (Phase 2 economy, art only for MVP)
  - Barracks, Archery Range, Mage Tower (military)
- ✅ 20 Tactics (combat abilities)
  - Fireball, Lightning Bolt, Heal, Shield Wall, Charge
- ✅ 14 Equipment (hero attachments)
  - Wooden Shield, Leather Armor, Iron Sword, Steel Helmet
- ✅ 10 Workers (resource production, Phase 2)
  - Farmers, Lumberjacks, Miners (art only for MVP)

**Stats** (Simple for MVP):
- Attack: 1-100 scale
- Defense: 0-50 scale
- ❌ No Health/Mana/Stamina (Phase 2)

**Tutorial UI**:
- ✅ EULA screen (Step 1)
- ✅ Trainer Deck selection (Step 6, 6 options)
- ✅ Pack opening animation (Steps 6, 23, 27, 28)
- ✅ Codex (view all owned cards, filter by rarity/element)
- ✅ Deck Builder (drag-and-drop, 20-card limit)

**Deliverables**:
- [ ] card-schema.json validated (all 100 cards)
- [ ] CardData C# class (Attack/Defense properties)
- [ ] CardManager singleton (load cards from JSON, cache)
- [ ] Codex UI (Unity UI Toolkit, grid view, filters)
- [ ] Deck Builder UI (drag-drop, validation, save/load)
- [ ] Trainer Deck selection UI (6 buttons, preview cards, confirm)

---

### Week 3-4: Combat System

**Battle Map**:
- ✅ 8×8 hex grid (64 tiles total)
- ✅ Terrain types: Plains only (Mountains/Water in Phase 3)
- ✅ Fog of war: None for MVP (reveal all tiles)
- ✅ Camera: Top-down isometric, drag to pan, pinch to zoom

**Manual Combat**:
- ✅ Drag cards from hand to place on board (1 card = 1 unit)
- ✅ Click unit to select, click tile to move (highlight valid moves)
- ✅ Click enemy to attack (simple damage = Attack - Defense)
- ✅ Turn-based: Player → AI → Player (no simultaneous moves)

**Auto-Battle**:
- ✅ AI plays both sides (skip animation option)
- ✅ Simple AI: Attack nearest enemy, prioritize low-Defense targets
- ✅ Speed controls: 1×, 2×, 4× speed, or instant resolve

**Victory Screen**:
- ✅ XP gained (50-200 based on enemy difficulty)
- ✅ Gold reward (50-200 based on enemy difficulty)
- ✅ Battle chest opening (Bronze tier for MVP)
- ✅ Pack reward (Element Booster at Steps 23, 27)

**Deliverables**:
- [ ] BattleMap C# class (8×8 hex grid, pathfinding)
- [ ] BattleManager singleton (turn system, win/loss conditions)
- [ ] Unit placement (drag-drop from hand to board)
- [ ] Movement system (click to move, A* pathfinding)
- [ ] Attack system (click enemy, damage calculation, remove unit)
- [ ] Auto-Battle AI (basic targeting, no advanced tactics)
- [ ] Victory screen UI (XP/Gold display, chest opening animation)

---

### Week 5-6: Realm Map & Exploration

**Realm Map**:
- ✅ 40-hex map (Locations)
- ✅ Fog of war: 20 Locations visible at start, 20 hidden
- ✅ Movement: 3 tiles per turn, 10 Movement Points/day
- ✅ Terrain: Plains, Forest, Mountain (impassable), Water (impassable)
- ✅ Camera: Top-down isometric, drag to pan, pinch to zoom

**Enemy Encounters** (5-10 PvE battles):
- ✅ Goblin Raiders (Common, 3-card deck)
- ✅ Bandit Camp (Uncommon, 5-card deck)
- ✅ Orc Warband (Rare, 7-card deck)
- ✅ Ancient Ruins (Epic, 10-card deck, Realm Boss)

**Treasure Nodes**:
- ✅ Gold Node: 100-500 Gold (5-10 nodes on map)
- ✅ Gem Node: 10-50 Gems (2-5 nodes on map)
- ✅ Empty Locations: No reward, passable

**Energy System**:
- ✅ Tutorial battles: 0 Energy cost (unlosable)
- ✅ Post-tutorial battles: 10 Energy per battle
- ✅ Daily refill: 240 Energy/day (24 battles max)
- ✅ Starting Energy: 100 (10 battles to start)

**Deliverables**:
- [ ] RealmMap C# class (40-hex map, fog of war, pathfinding)
- [ ] Movement system (3 tiles/turn, 10 Movement Points/day)
- [ ] Enemy encounters (5-10 battles, simple AI)
- [ ] Treasure nodes (Gold/Gems, collect on tile entry)
- [ ] Energy system (10 per battle, 240 refill/day, UI display)
- [ ] Realm Map UI (hex grid, unit display, fog of war)

---

### Week 7-8: Progression & Stores

**Player Leveling**:
- ✅ Level 1-5 progression (tutorial ends at Level 2)
- ✅ XP requirements: Level 1 = 0, Level 2 = 100, Level 3 = 300, Level 4 = 600, Level 5 = 1,000
- ✅ XP sources: Battle wins (50-200 XP), quest completion (Phase 2)

**Pack Store**:
- ✅ Standard Pack (5 cards): 1,000 Gold
- ✅ Element Booster (5 cards): 2,000 Gold
- ✅ Epic Booster (5 cards): 5,000 Gold
- ✅ Pack opening animation (reveal 1 card at a time, skip option)

**Gold Earning**:
- ✅ Battle rewards: 50-200 Gold per battle
- ✅ Daily login: 500 Gold (7-day cycle)
- ✅ Battle chests: 50-500 Gold (Bronze tier for MVP)
- ✅ Total daily: ~700 Gold/day (500 login + 200 battles)

**Daily Login**:
- ✅ 7-day reward cycle:
  - Day 1: 500 Gold
  - Day 2: 1× Common card
  - Day 3: 500 Gold
  - Day 4: 1× Uncommon card
  - Day 5: 1,000 Gold
  - Day 6: 1× Rare card
  - Day 7: 1× Standard Pack (5 cards)
- ✅ Resets weekly (Day 8 = Day 1)

**Analytics** (Basic Tracking):
- ✅ Battles won/lost
- ✅ Packs opened (Standard/Element/Epic)
- ✅ Gold earned/spent
- ✅ Tutorial completion rate (% of players who finish 28 steps)
- ✅ Session length (average time per session)

**Deliverables**:
- [ ] PlayerLevel C# class (XP tracking, level-up rewards)
- [ ] PackStore UI (buy packs with Gold, opening animation)
- [ ] DailyLogin system (7-day cycle, reward claims)
- [ ] Analytics tracking (Nakama server, Unity Analytics)
- [ ] Gold display UI (current Gold, earn/spend notifications)

---

## Total MVP Scope

### What's Included (8-Week Deliverables)

**Core Systems**:
- ✅ Tutorial (28 steps, 0-60 minutes)
- ✅ Card system (~100 cards, simple Attack/Defense stats)
- ✅ Deck building (6 Trainer Decks, drag-drop builder)
- ✅ Combat (8×8 battle map, manual + auto-battle)
- ✅ Realm Map (40 Locations, HoMM-style exploration)
- ✅ Treasure nodes (Gold/Gems on Realm Map)
- ✅ Energy system (10 per battle, 240 refill/day)
- ✅ Pack Store (Standard/Element/Epic Packs, Gold only)
- ✅ Daily login (7-day reward cycle)
- ✅ Player leveling (Level 1-5 progression)

**Total Content**:
- ✅ 100 cards (6 Epics, 30 Units, 20 Buildings, 20 Tactics, 14 Equipment, 10 Workers)
- ✅ 6 Trainer Decks (20 cards each)
- ✅ 5 packs in tutorial (20 Trainer + 5 Element #1 + 6 Step 23 + 5 Element #2 = 36 cards)
- ✅ 5-10 PvE battles (Realm Map enemies)
- ✅ 1 Realm Map (40 Locations, single-player only)

---

### What's Deferred (Post-MVP)

**Phase 2 (Month 2-3)**:
- ❌ Food/Lumber/Ore economy (production buildings, auto-collection)
- ❌ RPG card stats (Health/Mana/Stamina)
- ❌ Consumables (Potions/Scrolls)
- ❌ RPG shops (Alchemist, Scribe, Jeweler)
- ❌ Premium Packs (Gem currency, 10% shiny rate)
- ❌ Card combining (star rank progression)
- ❌ Daily/Weekly quests

**Phase 3 (Month 4-6)**:
- ❌ Territory Map (Realm occupation, 1-month campaigns)
- ❌ World Map (Territory wars, 3-month seasons)
- ❌ Occupation mechanics (Location → Realm → Territory)
- ❌ PvP Arena (1v1 ranked matches)
- ❌ Alliances (chat, donations, co-op events)
- ❌ Elemental interactions (Fire > Earth > Water)
- ❌ Status effects (Burn, Freeze, Poison)
- ❌ Equipment sockets (Jewel/Rune attachments)

**Phase 4 (Month 7-12)**:
- ❌ Alliance wars (50v50 Territory battles)
- ❌ Game Decks ($19.99 premium 50-card decks)
- ❌ Shiny system (1%/10% drop rates)
- ❌ Battle Pass (30-day progression)
- ❌ Seasonal events (Halloween, Winter, Summer)

---

## Implementation Order (Critical Path)

### Week 1 (Foundation)
1. Unity project setup (2021+ LTS, UI Toolkit, Addressables)
2. Nakama server setup (Docker, PostgreSQL, authentication)
3. Card data loading (JSON → C# CardData class)
4. Codex UI (grid view, filters, card preview)

### Week 2 (Deck Building)
5. Deck Builder UI (drag-drop, 20-card limit, save/load)
6. Trainer Deck selection UI (6 options, preview, confirm)
7. Tutorial flow (Steps 1-6, EULA → Trainer Deck selection)

### Week 3 (Combat Foundation)
8. Battle Map (8×8 hex grid, camera controls)
9. Unit placement (drag cards to board, validation)
10. Movement system (click to move, A* pathfinding)
11. Attack system (click enemy, damage calculation)

### Week 4 (Combat Polish)
12. Auto-Battle AI (basic targeting, speed controls)
13. Victory screen (XP/Gold display, chest opening)
14. Tutorial flow (Steps 7-15, first battle walkthrough)

### Week 5 (Realm Map Foundation)
15. Realm Map (40-hex map, fog of war, camera)
16. Movement system (3 tiles/turn, 10 Movement Points/day)
17. Enemy encounters (5-10 battles, simple AI)

### Week 6 (Realm Map Polish)
18. Treasure nodes (Gold/Gems, collect on entry)
19. Energy system (10 per battle, 240 refill/day)
20. Tutorial flow (Steps 16-27, Realm Map exploration)

### Week 7 (Stores & Progression)
21. Pack Store UI (buy packs, opening animation)
22. Daily login system (7-day cycle, reward claims)
23. Player leveling (XP tracking, level-up rewards)

### Week 8 (Polish & QA)
24. Tutorial flow (Step 28, tutorial complete)
25. Analytics tracking (Nakama, Unity Analytics)
26. Bug fixes (QA testing, balance tweaks)
27. Build for iOS/Android/PC (test on devices)

---

## Success Criteria (MVP Complete)

### Technical Metrics
- ✅ All 28 tutorial steps playable (0 crashes)
- ✅ All 100 cards loadable (0 missing data errors)
- ✅ Battle system works (manual + auto-battle)
- ✅ Realm Map works (movement, fog of war, encounters)
- ✅ Pack Store works (buy with Gold, opening animation)
- ✅ Builds run on iOS/Android/PC (60 FPS, <100 MB download)

### Player Experience Metrics
- ✅ Tutorial completion rate: >70% (target 80%)
- ✅ Average session length: 15-30 minutes
- ✅ Battles won (first 5 battles): >80% win rate (tutorial is easy)
- ✅ Packs bought (first week): Average 2-3 packs per player
- ✅ Retention (Day 1): >50% (target 60%)
- ✅ Retention (Day 7): >20% (target 30%)

### Go/No-Go Decision
- **GO to Phase 2** if:
  - Tutorial completion >70%
  - Day 7 retention >20%
  - Players buy packs with earned Gold (monetization proven)
  - Combat feels fun (manual + auto-battle balance)

- **PIVOT** if:
  - Tutorial drop-off >50% (too long/confusing)
  - Players don't buy packs (economy broken)
  - Combat feels tedious (consider simplifying further)

---

## Dependencies & Risks

### Critical Dependencies
- ✅ Unity 2021+ LTS (stable version)
- ✅ Nakama 3.x (Docker deployment, PostgreSQL)
- ✅ Card art (100 cards × 4 hours = 400 hours = 10 weeks at 1 artist)
  - **Mitigation**: Use placeholder art for MVP (colored rectangles with card names)
- ✅ UI/UX design (Codex, Deck Builder, Battle Map, Realm Map)
  - **Mitigation**: Use Unity UI Toolkit default styles, polish in Phase 2

### High Risks
- ⚠️ **Scope Creep**: Adding Phase 2 features to MVP (Health/Mana/Stamina, Food/Lumber/Ore)
  - **Mitigation**: Strict feature freeze after Week 6, focus on polish
- ⚠️ **Tutorial Length**: 28 steps (0-60 minutes) might be too long
  - **Mitigation**: Add skip options after Step 15 (first battle), track analytics
- ⚠️ **Art Asset Bottleneck**: 100 cards need illustrations
  - **Mitigation**: Placeholder art for MVP, commission real art in Phase 2
- ⚠️ **Combat Balance**: Simple Attack/Defense might be too basic
  - **Mitigation**: Test with 10-20 players, iterate formulas, add complexity in Phase 2

---

## Next Steps (After MVP)

### Phase 2 Priorities (If MVP Successful)
1. RPG card stats (Health/Mana/Stamina)
2. Consumables (Potions/Scrolls from battle chests)
3. RPG shops (Alchemist, Scribe, mall screen)
4. Food/Lumber/Ore economy (production buildings, auto-collection)
5. Premium Packs (Gem currency, 10% shiny rate)

### Phase 3 Priorities (If Phase 2 Successful)
1. Territory Map (Realm occupation, 1-month campaigns)
2. PvP Arena (1v1 ranked matches, Arena Tokens)
3. Alliances (chat, donations, PvE events)
4. Elemental interactions (Fire > Earth > Water)
5. Status effects (Burn, Freeze, Poison)

---

**For combat details, see**: [combat-calculation-spec.md](combat-calculation-spec.md)  
**For economy details, see**: [economy-system.md](economy-system.md)  
**For RPG systems, see**: [rpg-systems-spec.md](rpg-systems-spec.md)  
**For map progression, see**: [map-tier-progression.md](map-tier-progression.md)  
**For tutorial flow, see**: [tutorial-flow.md](tutorial-flow.md)
