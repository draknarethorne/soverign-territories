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
- ✅ Created reorganization-status.md (this document)
- ✅ Added 75+ inline TODOs to specs (combat, economy, RPG systems)

### Phase 7 (December 30, 2024) ✅
- ✅ Condensed Section 5 (Economy & Trading) from ~970 to ~250 lines
  - Marked VIP system as Phase 2 (post-MVP)
  - Marked Auction House as Phase 3 (post-MVP)
  - Referenced economy-system.md for full currency specs
  - Removed detailed trading strategies and VIP tier breakdowns
- ✅ Created docs/README.md - Comprehensive documentation hub (270+ lines)
- ✅ Enhanced README.md with visual polish (badges, Mermaid diagrams, icons)
- ✅ Created docs/ASSETS.md - Complete visual asset guide (500+ lines)

---

## Current Bible State

**Total Lines**: 5,190 (down from 6,807)  
**Reduction**: 1,617 lines removed (~24% reduction)  
**Status**: ✅ **BELOW TARGET** (<6,000 lines achieved!)

### Major Reductions Achieved
- Section 2.5 (Onboarding): ~138 → ~50 lines (-88 lines)
- Section 4 (Gameplay Modes): ~600 → ~100 lines (-500 lines)
- Section 5 (Economy & Trading): ~970 → ~250 lines (-720 lines)
- Section 8 (Combat Mechanics): ~300 → ~100 lines (-200 lines)
- **Total Saved**: ~1,508 lines from condensing alone

### Documentation Enhancements
- ✅ docs/README.md: GitHub auto-displays when viewing docs/ folder
- ✅ Mermaid diagrams: System architecture, roadmap timeline, MVP Gantt chart
- ✅ Status badges: Unity, C#, Nakama versions, Bible status, Phase progress
- ✅ Icon conventions: 🎴 🗺️ ⚔️ 💰 💎 ⚡ for visual navigation
- ✅ ASSETS.md: Complete art style guide with 100 card list, color palette, tool recommendations

### Sections Still Available for Optional Condensing

#### Could Condense Further (If Desired)
- [ ] **Section 2.6 (Card Stacking)**: ~400 lines
  - Current: Detailed HoMM-style stacking rules
  - Opportunity: Could reference gameplay-modes-spec.md for stack math examples
  - Estimated Savings: ~150-200 lines
  
- [ ] **Section 9 (Progression & Balance)**: ~340 lines
  - Current: XP tables and level scaling formulas
  - Opportunity: Could extract exact XP values to progression-spec.md
  - Estimated Savings: ~150-200 lines

- [ ] **Section 13 (Content Pipeline)**: ~126 lines
  - Current: Implementation workflow details
  - Opportunity: Could move to separate development-process.md
  - Estimated Savings: Remove entirely (~126 lines)

**Note**: Since we're already at 5,190 lines (well below 6,000), further condensing is **optional**. Bible is now a concise quick reference while specs provide detailed implementation guides.
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
