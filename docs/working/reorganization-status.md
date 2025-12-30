# Documentation Reorganization Status

**Date**: December 30, 2024  
**Purpose**: Track bible cleanup and spec extraction progress  
**Note**: This is a working document - move to archive when complete

---

## Completed Work

### Phase 1-5 (December 29-30, 2024) ✅
- ✅ Created 6 core specification documents (3,386 lines)
  - economy-system.md
  - combat-calculation-spec.md
  - mvp-scope-final.md
  - rpg-systems-spec.md
  - map-tier-progression.md
  - terminology-guide.md
- ✅ Updated game-bible.md with Documentation Map and Phase markers
- ✅ Condensed Section 2.5 (Onboarding) from ~138 to ~50 lines
- ✅ Updated Section 5.5 (Economy) with Phase 2/3 disclaimers
- ✅ Global terminology update (County→Realm, State→Territory, Global→World)
- ✅ Updated tutorial-flow.md (treasure nodes, simplified stores, 31 cards)
- ✅ Updated README.md with project overview

### Phase 6 (December 30, 2024) ✅
- ✅ Created gameplay-modes-spec.md (detailed mode mechanics with TODOs)
- ✅ Condensed Section 4 (Gameplay Modes) from ~600 to ~100 lines
- ✅ Condensed Section 8 (Combat Mechanics) from ~300 to ~100 lines
- ✅ Moved bible-reorganization-plan.md to docs/working/
- ✅ Created this status tracker

---

## Current Bible State

**Total Lines**: ~6,300 (down from 6,807)  
**Reduction**: ~500 lines removed (condensed, not deleted - moved to spec docs)

### Sections Still Needing Work

#### High Priority (Bloat + Tutorial Redundancies)
- [ ] **Section 2.6 (Card Stacking)**: 400+ lines, some tutorial overlap with Section 4.2
  - **Action**: Review for redundancies, keep HoMM-style rules, reference gameplay-modes-spec.md
  - **Target**: Reduce to ~200 lines
  
- [ ] **Section 5 (Economy & Trading)**: 1,200+ lines, lots of Phase 2-3 content
  - **Action**: Mark auction house (5.3) as Phase 3, move detailed trade rules to new trade-spec.md
  - **Target**: Reduce to ~600 lines

- [ ] **Section 9 (Progression & Balance)**: 800+ lines, detailed XP tables
  - **Action**: Move exact XP values to progression-spec.md, keep high-level in bible
  - **Target**: Reduce to ~400 lines

- [ ] **Section 13 (Content Pipeline)**: 500+ lines, implementation details
  - **Action**: Move to separate development-process.md (not part of game design)
  - **Target**: Remove entirely from bible or reduce to ~50 lines

#### Medium Priority (Mostly Fine, Minor Cleanup)
- [ ] **Section 6 (Player & Alliance)**: 400 lines, schemas already extracted
  - **Action**: Quick review for Phase 3 PvP disclaimers
  - **Target**: No major changes needed

- [ ] **Section 7 (Leaderboards & Seasons)**: 200 lines, Phase 4 content
  - **Action**: Add "PHASE 4 ❌ NOT IN MVP" header
  - **Target**: No major changes needed

- [ ] **Section 10-12 (UI, Social, Tech)**: 800 lines total
  - **Action**: Review for implementation details that belong in separate docs
  - **Target**: Possible 20-30% reduction

#### Low Priority (Already Concise)
- ✅ **Section 1 (Core Philosophy)**: Clean, high-level overview
- ✅ **Section 2 (Card System)**: Visual design is important, keep detailed
- ✅ **Section 3 (Map Hierarchy)**: Referenced map-tier-progression.md already

---

## Remaining Gaps to Address

### Design Gaps (From bible-reorganization-plan.md)
These are now tracked as TODO comments in spec files:

1. **Combat Formulas** (combat-calculation-spec.md):
   - TODO: Define exact elemental multipliers (Phase 3)
   - TODO: Design terrain effect formulas
   - TODO: Create status effect durations (Burn/Freeze/Poison)

2. **Gameplay Modes** (gameplay-modes-spec.md):
   - TODO: Define 100-card MVP pool (which cards in tutorial?)
   - TODO: Design boss battle phases (enrage, health gates)
   - TODO: Create 10-20 auto-battle tactic templates

3. **Map Progression** (map-tier-progression.md):
   - TODO: Define Realm occupation flow (garrison requirements)
   - TODO: Design castle siege phases (walls, courtyard, throne room)
   - TODO: Determine Territory buff scaling (+50-100% Power)

4. **RPG Systems** (rpg-systems-spec.md):
   - TODO: Create consumable item catalog (10-20 Potions/Scrolls)
   - TODO: Design RPG shop pricing (Alchemist/Scribe cost balancing)
   - TODO: Define equipment socket system (1-3 sockets based on rarity)

5. **Economy** (economy-system.md):
   - TODO: Finalize Phase 2 Food/Lumber/Ore production rates
   - TODO: Design AFK collection caps (12-hour offline limit)
   - TODO: Create auction house listing fees and tax rates

### Schema Work (Deferred to Future)
- [ ] Create realm-map-schema.json (Locations, terrain types)
- [ ] Create territory-map-schema.json (Realms, castle levels)
- [ ] Create world-map-schema.json (Territories, alliance control)
- [ ] Create treasure-node-schema.json (Gold/Gems drop rates)
- [ ] Update economy-node-schema.json with Phase 2 marker
- [ ] Create card-stats-schema.json (Health/Mana/Stamina - Phase 2)
- [ ] Create consumable-schema.json (Potions/Scrolls - Phase 2)

---

## Next Steps (Phase 7 Plan)

### Immediate (Today/Tomorrow)
1. [ ] Condense Section 2.6 (Card Stacking) - review for tutorial redundancies
2. [ ] Mark Section 5.3 (Auction House) as Phase 3
3. [ ] Extract Section 9 XP tables to progression-spec.md
4. [ ] Move Section 13 (Content Pipeline) to development-process.md
5. [ ] Add Phase markers to Sections 6-7-10-11-12
6. [ ] Commit Phase 7 changes to git

### Short-Term (This Week)
- [ ] Create trade-spec.md (extract auction house details from Section 5.3)
- [ ] Create progression-spec.md (extract XP tables from Section 9)
- [ ] Review all sections for inline TODO comments (move from reorg plan to spec docs)
- [ ] Final bible line count check (target: <6,000 lines)

### Medium-Term (Next 2 Weeks)
- [ ] Address design TODOs in spec files (boss mechanics, tactic templates, etc.)
- [ ] Create missing schemas (realm-map, territory-map, treasure-node)
- [ ] Write development-process.md (agile workflow, testing, analytics)
- [ ] Archive working documents to docs/archive/

---

## Success Metrics

**Bible Cleanup**:
- ✅ Target: <6,000 lines (currently 6,300, was 6,807)
- ✅ All Phase 2-4 features clearly marked with ❌ NOT IN MVP
- ✅ Redundancies eliminated (tutorial flow only in tutorial-flow.md)
- ✅ Implementation details extracted to spec docs

**Spec Coverage**:
- ✅ 7 spec documents created (economy, combat, MVP scope, RPG, maps, terminology, gameplay)
- 🔄 TODO comments added inline for design gaps (in progress)
- ⏳ Schemas deferred to Unity implementation phase

**Developer Readiness**:
- ✅ README.md provides clear entry point
- ✅ Quick reference links to all specs
- ✅ MVP scope clearly separated from post-MVP
- ✅ Bible remains authoritative source (high-level), specs provide details

---

## Notes

- Keep bible as **quick reference** - developers should read it first to understand vision
- Spec docs are **implementation guides** - exact formulas, TODOs for gaps
- Working docs (this file, bible-reorganization-plan.md) are **transient** - archive when done
- All design gaps now tracked via inline TODOs in spec files (not separate gap documents)
