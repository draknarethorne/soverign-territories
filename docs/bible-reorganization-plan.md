# Game Bible Reorganization Plan

**Date**: December 29, 2025  
**Purpose**: Reduce game-bible.md density (6,082 lines → ~4,500 lines target)  
**Strategy**: Extract detailed tutorials/specs to separate documents, keep high-level design in bible

---

## Current Structure Issues

1. **Onboarding section too detailed** (Section 2.5, lines 1094-1250 = 156 lines)
   - Contains tutorial flow details now covered in tutorial-flow.md
   - Pre-built deck lists should be in starter-deck-schema.json
   - Deck size progression table should be in progression-schema.json

2. **Scattered tutorial content** (multiple sections reference onboarding)
   - Section 2.5: New Player Onboarding
   - Section 2.6: Card Stacking (includes tutorial flow for County Map)
   - Multiple sections mention "first battle" and "tutorial teaches..."

3. **Data that belongs in schemas**:
   - Detailed pack rarity distributions → pack-schema.json
   - Specific card stats → card-schema.json
   - Formation presets → deployment-schema.json

4. **Repetition across docs**:
   - Tutorial flow exists in both game-bible.md AND tutorial-flow.md
   - Pack system exists in both game-bible.md AND (needs) pack-schema.json updates

---

## Reorganization Strategy

### Phase 1: Reference Consolidation
**Update game-bible.md Section 2.5** to:
```markdown
## 2.5 New Player Onboarding

See **[tutorial-flow.md](tutorial-flow.md)** for detailed step-by-step player journey (28 steps, 0-60 minutes).

**High-Level Onboarding Principles**:
- **First Impression Hook**: 20-30 cards in first draw (1 Epic guaranteed)
- **Guided vs Manual Path**: Pre-built decks OR manual selection
- **Progressive Deck Size**: 10-15 cards (Level 1) → 40-50 cards (Level 30)
- **Tutorial Safety Nets**: Unlosable first battle, free retries, fallback card grants

**Starter Deck Archetypes**:
- Aggro Rush (Fire/Lightning, fast units)
- Defensive Builder (Earth/Frost, economy focus)
- Balanced Explorer (Water/Wind, learn all mechanics)

For full specifications, see:
- [tutorial-gap-resolutions.md](tutorial-gap-resolutions.md) - Design solutions for EULA, pack skip, placement undo, etc.
- [mvp-scope.md](mvp-scope.md) - Implementation roadmap for Unity
- [starter-deck-schema.json](specs/starter-deck-schema.json) - Deck templates and fallback logic
```

### Phase 2: Extract Detailed Data to Schemas

**Move to starter-deck-schema.json**:
- Full 10-card lists for Aggro Rush, Defensive Builder, Balanced Explorer
- Card IDs, quantities, fallback rules

**Move to progression-schema.json**:
- Player Level unlock table (Level 1 → 30, deck size progression)
- XP requirements per level
- Time estimates ("Day 1", "Week 2", etc.)

**Move to pack-schema.json**:
- Detailed rarity distributions (50% Common, 30% Uncommon, etc.)
- Pity system thresholds (10 packs = Epic, 50 = Legendary)
- 3-tier pack system details

### Phase 3: Consolidate Scattered Tutorial References

**Create a new Section 2.5.1: Tutorial Design Reference** in game-bible.md:
```markdown
### Tutorial Design Reference

**Core Philosophy**: F2P friendly, unlosable first battle, generous starter pool

**Key Documents**:
- [tutorial-flow.md](tutorial-flow.md) - Step-by-step walkthrough (QA test script)
- [tutorial-gap-resolutions.md](tutorial-gap-resolutions.md) - Solved design problems (EULA, skip, undo, etc.)
- [mvp-scope.md](mvp-scope.md) - 8-week implementation roadmap

**Tutorial Checkpoints** (what player has after each phase):
- After Pack Opening (2 min): 20-30 cards, 1 Epic guaranteed
- After Deck Build (8 min): 11-card deck, understands deck slots
- After First Battle (15 min): Manual battle complete, Auto-Battle unlocked
- After Post-Tutorial (60 min): 3-5 battles complete, Codex introduced, Level 1-2

See tutorial-flow.md for minute-by-minute breakdown.
```

**Remove from Section 2.6** (Card Stacking):
- Tutorial flow details (lines 1637-1676, "Tutorial Flow - First Battle")
- Move to tutorial-flow.md as reference only

---

## Expected Outcome

**Before**:
- game-bible.md: 6,082 lines (dense, hard to navigate)
- tutorial content scattered across 3+ sections
- No clear spec ownership (schemas vs bible)

**After**:
- game-bible.md: ~4,500 lines (high-level design, cross-references detailed docs)
- tutorial-flow.md: Step-by-step implementation guide (QA/devs)
- tutorial-gap-resolutions.md: Solved design problems (9 gaps)
- mvp-scope.md: Implementation roadmap (Unity phases)
- Schemas: All data specifications (card stats, pack odds, deck templates)

**Benefits**:
- ✅ Bible focuses on "why" (design philosophy, player psychology)
- ✅ Flow doc focuses on "how" (step-by-step execution)
- ✅ Schemas focus on "what" (exact data, validation rules)
- ✅ MVP doc focuses on "when" (implementation priority, week-by-week)
- ✅ Easier to maintain (update one doc without breaking others)
- ✅ Easier to onboard new team members (clear doc hierarchy)

---

## Implementation Checklist

- [ ] Update game-bible.md Section 2.5 (consolidate, cross-reference tutorial-flow.md)
- [ ] Extract detailed starter deck lists to starter-deck-schema.json examples
- [ ] Extract deck size progression table to progression-schema.json
- [ ] Remove tutorial flow from Section 2.6 (Card Stacking), add cross-reference
- [ ] Update pack-schema.json with 3-tier system details from game-bible.md Section 2.2.3
- [ ] Add "Documentation Map" section to game-bible.md (explains doc hierarchy)
- [ ] Verify all cross-references are correct (no broken links)
- [ ] Commit reorganization with detailed summary

---

**Total Estimated Line Reduction**: 1,500-1,800 lines removed from bible (moved to specs/docs)
**New Target**: game-bible.md at 4,200-4,500 lines (30% reduction)
