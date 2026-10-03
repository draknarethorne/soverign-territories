# Documentation Audit - January 6, 2026

**Audit Purpose**: Identify outdated, duplicate, or misaligned documents after iterative design updates  
**Core Philosophy Check**: "Pokemon TCG meets Slay the Spire meets Baldur's Gate, NOT Clash of Clans"  
**MVP Focus**: Card collection + deck-building + tactical campaign battles (NOT Territory Maps)  
**Solo Dev Reality**: 16-24 weeks part-time (NOT 8 weeks full-time team)

---

## Executive Summary

### ✅ Documents That Are Current & Aligned
1. **solo-dev-realistic-mvp.md** (Jan 1, 2026) - ✅ PERFECT alignment, realistic 16-24 week timeline
2. **competitive-analysis.md** (Jan 1, 2026) - ✅ UPDATED, removed Clash references, focuses on Pokemon/Slay the Spire/Baldur's Gate
3. **tactics-system-clarification.md** (Dec 31, 2025) - ✅ CURRENT, dual-purpose AI + effects design
4. **mvp-crafting-pvp-additions.md** (Dec 31, 2025) - ✅ CURRENT, scroll crafting + async Arena PvP
5. **game-bible.md** (core sections) - ✅ MOSTLY CURRENT, but has some outdated references (see below)

### ⚠️ Documents That Need Updates (Misaligned with New Vision)
1. **mvp-scope-final.md** - ⚠️ Still says "8-week timeline", conflicts with solo-dev-realistic-mvp.md (16-24 weeks)
2. **final-mvp-review-dec2025.md** - ⚠️ Pre-dates solo dev clarification, still has Clash of Clans comparisons
3. **map-tier-progression.md** - ⚠️ Positions Territory/World Maps as core features, NOT clearly marked Phase 2-3
4. **gameplay-modes-spec.md** - ⚠️ Treats Territory conquest as Phase 2-3, needs alignment with solo dev timeline
5. **README.md** - ⚠️ Tagline is outdated: "Rule the Map. Automate the Empire" should be "Conquer the Campaign. Level Your Heroes"

### 🗑️ Documents That Should Be Archived/Removed
1. **final-mvp-review-dec2025.md** - Superseded by solo-dev-realistic-mvp.md (same purpose, but outdated assumptions)
2. **tutorial-system-redesign.md** (if it exists) - Likely superseded by tutorial-flow.md + mvp-scope-final.md
3. **competitive-analysis.md** (old sections) - Still has 40+ Clash of Clans references that need scrubbing

---

## Detailed Analysis

### 1. Timeline Conflicts (CRITICAL ISSUE)

**Problem**: You have TWO conflicting MVP timelines:
- **mvp-scope-final.md**: "8-week timeline" (assumes full-time team)
- **solo-dev-realistic-mvp.md**: "16-24 week timeline" (realistic solo part-time)

**Impact**: Confusing for implementation - which timeline is authoritative?

**Recommendation**:
- **Option A** (Clean break): Archive mvp-scope-final.md → docs/archive/, make solo-dev-realistic-mvp.md the authoritative timeline
- **Option B** (Update in place): Update mvp-scope-final.md header to say "ASPIRATIONAL 8-week timeline (full-time), see solo-dev-realistic-mvp.md for REALISTIC 16-24 week solo timeline"
- **Option C** (Merge): Merge best parts of both into single mvp-scope-REALISTIC-final.md

**My Recommendation**: **Option A** - Archive old 8-week timeline, make solo-dev-realistic-mvp.md authoritative. Cleaner, less confusion.

---

### 2. Competitive Positioning (MOSTLY FIXED, BUT...)

**competitive-analysis.md Status**:
- ✅ Header updated (Jan 1, 2026) with solo dev context
- ✅ Executive Summary updated (Pokemon TCG + Slay the Spire + Baldur's Gate)
- ⚠️ **Still has 40+ Clash of Clans references** in body sections (not all removed)

**Search Results** (from grep):
- Line 119: "Clash of Clans model" (async PvP comparison)
- Line 126-187: Multiple Clash references in comparison tables
- Line 258: "Clash of Clans = Base-building only"
- Line 323: "Clash of Clans = FORCED raids"
- Line 560: "Clash of Clans standard" (conversion rate)

**Recommendation**:
- **Keep Clash references ONLY for specific comparisons** (e.g., "Async PvP uses Clash of Clans attack-AI-decks model")
- **Remove Clash from primary positioning** (e.g., replace "Clash of Clans depth" with "Heroes of Might and Magic depth")
- **Add disclaimer**: "Clash of Clans referenced for specific mechanics (async PvP, alliance wars), NOT as primary inspiration"

**Specific Edits Needed**:
```markdown
OLD: "Dual Progression (Player + Castle) - Clash of Clans depth"
NEW: "Dual Progression (Player + Castle) - Heroes of Might and Magic depth"

OLD: "50v50 Alliance Wars - Clash of Clans epic scale"
NEW: "50v50 Alliance Wars - Epic scale (similar to Clash of Clans clan wars, but card-based)"

OLD: "Clash of Clans standard (10-15% conversion)"
NEW: "Mobile TCG standard (10-15% conversion, similar to Clash/Hearthstone)"
```

---

### 3. Map Hierarchy Positioning (CRITICAL MISALIGNMENT)

**map-tier-progression.md Issues**:
- Positions Territory Maps and World Maps as **core features**
- Uses language like "MVP FOCUS" for Realm Map (good) but doesn't clearly mark Territory/World as Phase 2-3
- **Risk**: Could be interpreted as "Territory Maps are part of MVP" (they're NOT)

**Current Structure**:
```markdown
## Tier 4: Battle Map (8×8) ← MVP
## Tier 3: Realm Map (20-40 Locations) ← **MVP FOCUS**
## Tier 2: Territory Map (50-100 Realms) ← NOT CLEARLY MARKED
## Tier 1: World Map (200-500 Territories) ← NOT CLEARLY MARKED
```

**Recommended Structure**:
```markdown
## Tier 4: Battle Map (8×8 Tactical Grid) ✅ MVP
## Tier 3: Realm Map (20-40 Locations) ✅ **MVP FOCUS** ← Single Realm, linear progression
## Tier 2: Territory Map (50-100 Realms) ❌ PHASE 2-3 (NOT MVP)
## Tier 1: World Map (200-500 Territories) ❌ PHASE 3+ (NOT MVP)
```

**Add to Top of Document**:
```markdown
---
**IMPORTANT - MVP SCOPE CLARIFICATION**:
- ✅ **MVP**: Battle Map (8×8 tactical) + **SINGLE Realm Map** (40 Locations, linear campaign)
- ❌ **NOT MVP**: Territory Maps, World Maps, multi-Realm exploration
- 📅 **Phase 2-3**: Territory/World Maps are your long-term vision, NOT MVP scope
- 🎯 **MVP Focus**: Validate core loop (card collection + deck-building + tactical campaign battles)
---
```

---

### 4. Tagline Alignment (CRITICAL BRAND ISSUE)

**Current Taglines** (Conflicting):
- **game-bible.md**: "Build the Deck. Rule the Map. Automate the Empire."
- **solo-dev-realistic-mvp.md**: "Build the Deck. Conquer the Campaign. Level Your Heroes."
- **README.md**: "Build the Deck. Rule the Map. Automate the Empire."

**Problem**: "Rule the Map" implies Territory conquest is core (it's NOT in MVP)

**Recommended Tagline** (Aligned with MVP focus):
```markdown
PRIMARY: "Build the Deck. Conquer the Campaign. Level Your Heroes."
ALTERNATE: "Build the Deck. Battle Tactically. Explore the Realm."
PHASE 2-3: "Build the Deck. Rule the Map. Automate the Empire." (future vision)
```

**Files to Update**:
1. game-bible.md (line 40-45, update to primary tagline)
2. README.md (line 3, update to primary tagline)
3. mvp-scope-final.md (if not archived, update tagline)
4. All promotional materials (Steam page, website, etc.)

---

### 5. Document Redundancy (MERGE CANDIDATES)

#### A. **final-mvp-review-dec2025.md** vs **solo-dev-realistic-mvp.md**

**Overlap**: Both documents assess MVP competitive position and timeline

**final-mvp-review-dec2025.md** (Dec 31, 2025):
- 547 lines, pre-dates solo dev clarification
- Still has 8-week timeline
- Still compares heavily to Clash of Clans
- Rating: 4.2-4.4/5 based on 8-week MVP

**solo-dev-realistic-mvp.md** (Jan 1, 2026):
- 405 lines, POST solo dev clarification
- 16-24 week realistic timeline
- Focuses on Pokemon/Slay the Spire/Baldur's Gate
- Includes mental health, kill criteria, success criteria

**Recommendation**: **Archive final-mvp-review-dec2025.md**
- Move to docs/archive/ with note: "Superseded by solo-dev-realistic-mvp.md (Jan 1, 2026)"
- Keep solo-dev-realistic-mvp.md as authoritative competitive/timeline doc
- **Preserve**: Good competitive analysis sections (can copy into solo-dev-realistic-mvp.md if needed)

---

#### B. **competitive-analysis.md** vs **solo-dev-realistic-mvp.md**

**Overlap**: Both have competitive positioning sections

**competitive-analysis.md** (771 lines):
- Deep competitive tables (Pokemon TCG, Slay the Spire, Hearthstone, etc.)
- Feature-by-feature comparison (Collection, Combat, Progression, Monetization)
- Phase 1/1.1/2/3 recommendations
- Final ratings table

**solo-dev-realistic-mvp.md** (405 lines):
- Solo dev reality check (10-15 hrs/week, first game, hobby)
- Realistic timeline (16-24 weeks, aggressive vs conservative)
- Scope prioritization (Tier 1-4, what to cut)
- Mental health, kill criteria, success criteria

**Recommendation**: **Keep both, but clarify roles**
- **competitive-analysis.md**: Deep competitive comparison (market analysis, feature tables)
- **solo-dev-realistic-mvp.md**: Personal implementation roadmap (realistic timeline, scope management)
- **Update competitive-analysis.md header**: "For solo dev realistic timeline, see solo-dev-realistic-mvp.md"

---

#### C. **mvp-scope-final.md** vs **solo-dev-realistic-mvp.md**

**Overlap**: Both define MVP scope and timeline

**mvp-scope-final.md** (827 lines):
- Week-by-week breakdown (Week 1-2: Cards, Week 3-4: Deck Building, etc.)
- Detailed deliverables (card-schema.json, CardData C# class, etc.)
- 100 cards breakdown (6 heroes, 30 units, 20 tactics, etc.)
- Campaign structure (60-80 battles, 4 Territories, 9 Realms)

**solo-dev-realistic-mvp.md** (405 lines):
- Realistic timeline (16-24 weeks, not 8 weeks)
- Scope prioritization (Tier 1-4)
- Art strategy (placeholder → commission)
- Mental health & sustainability

**Recommendation**: **Merge or clearly differentiate**
- **Option A** (Merge): Combine into mvp-scope-REALISTIC-final.md (best of both)
- **Option B** (Keep separate, update headers):
  - **mvp-scope-final.md**: Rename to "mvp-scope-ASPIRATIONAL.md" (8-week ideal, full-time team assumptions)
  - **solo-dev-realistic-mvp.md**: "mvp-scope-REALISTIC.md" (16-24 week solo dev reality)
- **Option C** (Archive old, keep new):
  - Archive mvp-scope-final.md → docs/archive/
  - Update solo-dev-realistic-mvp.md to include week-by-week deliverables from old doc

**My Recommendation**: **Option C** - Archive aspirational timeline, expand realistic timeline with deliverables

---

### 6. Gameplay Modes Alignment

**gameplay-modes-spec.md Issues**:
- Still treats Territory conquest as Phase 2-3 (good)
- But doesn't clarify MVP = SINGLE Realm Map only
- **Risk**: Could be interpreted as "3-5 Realm Maps for MVP" (too ambitious for solo 16-24 weeks)

**Current Text** (Line 50):
```markdown
### MVP Scope
- ✅ **Must Have**: 3-5 Realm Maps (60-200 Locations total)
- ✅ **Must Have**: Tutorial Realm Map (20 Locations, scripted battles)
```

**Recommended Update**:
```markdown
### MVP Scope (Solo Dev 16-24 Weeks)
- ✅ **Must Have**: 1 Realm Map (40 Locations, linear campaign) ← **MVP FOCUS**
  - Tutorial Realm: First 10 Locations (scripted battles, teaches mechanics)
  - Main Campaign: Locations 11-40 (difficulty scaling, boss at 40)
- ⏸️ **Nice to Have** (if time): 2nd Realm Map (40 more Locations) ← Only if ahead of schedule
- ❌ **Phase 2**: 3-5 Realm Maps (multi-region exploration) ← NOT MVP
```

---

### 7. Assets & Art References

**assets.md Status**: ⚠️ Needs review for alignment
- Currently references "Territory Map", "World Map" tilesets
- **Risk**: Could imply Territory/World Maps are MVP scope (they're NOT)

**Recommendation**:
Add MVP scope clarification:
```markdown
## MVP Art Priority (Solo Dev, Placeholder First)

**Tier 1** (Essential for MVP):
- ✅ 100 card portraits (placeholder rectangles + AI-generated heroes OK)
- ✅ 8×8 tactical grid tiles (simple squares, grass/mountain/water)
- ✅ Single Realm Map tileset (40 hexes, 5-6 Location types)
- ✅ UI elements (buttons, icons, health bars)

**Tier 2** (Nice to Have):
- ⏸️ Commissioned card art (50 cards, if alpha validates)
- ⏸️ Animated abilities (fireball, heal, etc.)

**Tier 3** (Phase 2-3, NOT MVP):
- ❌ Territory Map tilesets (50-100 Realm hexes) ← Phase 2
- ❌ World Map tilesets (200-500 Territory hexes) ← Phase 3
- ❌ 3D hero figurines (tabletop aesthetic) ← Phase 3+
```

---

## Consolidation Recommendations

### Documents to Archive (Move to docs/archive/)

1. **final-mvp-review-dec2025.md**
   - **Why**: Superseded by solo-dev-realistic-mvp.md
   - **Note**: "Replaced by solo-dev-realistic-mvp.md (Jan 1, 2026) - Pre-dated solo dev clarification"

2. **mvp-scope-final.md** (OPTIONAL)
   - **Why**: Conflicts with solo-dev-realistic-mvp.md (8-week vs 16-24 week)
   - **Alternative**: Rename to mvp-scope-ASPIRATIONAL.md and update header
   - **Note**: "Aspirational 8-week timeline (full-time team). For realistic solo dev timeline, see solo-dev-realistic-mvp.md"

3. **Any tutorial-system-redesign.md** (if exists)
   - **Why**: Likely superseded by tutorial-flow.md
   - Check if it exists, archive if redundant

---

### Documents to Update (In-Place Edits)

#### Priority 1 (CRITICAL - Misalignment with core vision)

1. **README.md**
   - Update tagline: "Build the Deck. Conquer the Campaign. Level Your Heroes."
   - Update "Quick Start" to reference solo-dev-realistic-mvp.md as primary timeline

2. **game-bible.md**
   - Update tagline (line ~40): "Build the Deck. Conquer the Campaign. Level Your Heroes."
   - Add Phase callouts to Section 4 (Gameplay Modes):
     - Realm Map PvE: ✅ MVP
     - Territory Maps: ❌ Phase 2-3
     - World Maps: ❌ Phase 3

3. **map-tier-progression.md**
   - Add MVP scope disclaimer (top of doc)
   - Mark Tier 2/Tier 1 as "PHASE 2-3 (NOT MVP)"
   - Clarify MVP = SINGLE Realm Map (40 Locations)

4. **gameplay-modes-spec.md**
   - Update MVP scope: 1 Realm Map (not 3-5)
   - Add solo dev timeline callouts (16-24 weeks)

#### Priority 2 (Important - Clarity improvements)

5. **competitive-analysis.md**
   - Scrub remaining Clash of Clans positioning references
   - Add disclaimer: "Clash referenced for specific mechanics (async PvP), NOT primary inspiration"
   - Replace "Clash of Clans depth" → "Heroes of Might and Magic depth"

6. **assets.md**
   - Add MVP art priority tiers (placeholder first, commission later)
   - Mark Territory/World Map tilesets as Phase 2-3

#### Priority 3 (Nice to Have - Consistency polish)

7. **mvp-crafting-pvp-additions.md**
   - Update timeline: Note that "8-week timeline" is aspirational, solo dev = 16-24 weeks
   - Add: "Crafting/Arena PvP are Tier 2 (strongly recommended), can defer to Phase 1.1 if behind"

8. **tactics-system-clarification.md**
   - No changes needed (already current)

9. **solo-dev-realistic-mvp.md**
   - Consider adding week-by-week deliverables from mvp-scope-final.md (if archiving old doc)

---

## Proposed File Moves

### Archive (docs/design → docs/archive)
```
docs/design/final-mvp-review-dec2025.md → docs/archive/final-mvp-review-dec2025-SUPERSEDED.md
```

### Archive (docs/mvp → docs/archive) - OPTIONAL
```
docs/mvp/mvp-scope-final.md → docs/archive/mvp-scope-ASPIRATIONAL-8week.md
```

### Keep (docs/mvp)
```
docs/mvp/solo-dev-realistic-mvp.md ← Primary authoritative timeline
docs/mvp/tutorial-flow.md ← Current, no changes needed
docs/mvp/mvp-crafting-pvp-additions.md ← Current, minor timeline note
docs/mvp/unity-implementation-guide.md ← Current, no changes needed
docs/mvp/local-development-setup.md ← Current, no changes needed
```

### Keep (docs/design)
```
docs/design/competitive-analysis.md ← Update (scrub Clash positioning)
docs/design/tactics-system-clarification.md ← Current, no changes
docs/design/map-tier-progression.md ← Update (add MVP scope disclaimer)
docs/design/gameplay-modes-spec.md ← Update (1 Realm Map for MVP)
docs/design/assets.md ← Update (add MVP art priority)
docs/design/economy-system.md ← Current (Phase 2 focus, no MVP conflict)
docs/design/combat-calculation-spec.md ← Current, no changes
docs/design/rpg-systems-spec.md ← Current (Phase 2 focus, no MVP conflict)
docs/design/terminology-guide.md ← Current, no changes
docs/design/design-todos-phase2-3.md ← Current, no changes
```

---

## Summary of Required Actions

### Immediate (CRITICAL - Align with core vision)

1. ✅ **Archive final-mvp-review-dec2025.md** → docs/archive/ (superseded by solo-dev-realistic-mvp.md)
2. ✅ **Update README.md tagline** → "Build the Deck. Conquer the Campaign. Level Your Heroes."
3. ✅ **Update game-bible.md tagline** → "Build the Deck. Conquer the Campaign. Level Your Heroes."
4. ✅ **Add MVP scope disclaimer to map-tier-progression.md** → Territory/World Maps are Phase 2-3, NOT MVP
5. ✅ **Update gameplay-modes-spec.md MVP scope** → 1 Realm Map (40 Locations), not 3-5 Realm Maps

### Short-Term (Important - Reduce confusion)

6. ✅ **Scrub competitive-analysis.md Clash positioning** → Remove "Clash of Clans depth" → "Heroes of Might and Magic depth"
7. ✅ **Add disclaimer to competitive-analysis.md** → "Clash referenced for mechanics, NOT primary inspiration"
8. ✅ **Decide on mvp-scope-final.md fate** → Archive OR rename to mvp-scope-ASPIRATIONAL.md
9. ✅ **Update assets.md with MVP art priority** → Placeholder first, Territory/World tilesets Phase 2-3

### Optional (Nice to Have - Polish)

10. ⏸️ **Merge mvp-scope-final.md deliverables into solo-dev-realistic-mvp.md** (if archiving old doc)
11. ⏸️ **Update mvp-crafting-pvp-additions.md** → Note Tier 2 priority (can defer to Phase 1.1 if behind)
12. ⏸️ **Review all docs/specs/*.md** → Ensure no Territory/World Map references in MVP sections

---

## Verification Checklist

After making updates, verify:

- [ ] No document says "8-week MVP" without also mentioning "16-24 week solo dev realistic"
- [ ] No document positions Clash of Clans as primary inspiration (only reference for specific mechanics)
- [ ] All documents use tagline "Build the Deck. Conquer the Campaign. Level Your Heroes." (NOT "Rule the Map")
- [ ] Territory Maps and World Maps clearly marked as "Phase 2-3 (NOT MVP)" everywhere
- [ ] MVP scope = 1 Realm Map (40 Locations, linear campaign) consistently documented
- [ ] solo-dev-realistic-mvp.md referenced as authoritative timeline document

---

**Audit Completed**: January 6, 2026  
**Recommended Priority**: Execute "Immediate" actions first (critical alignment), then "Short-Term" (reduce confusion)  
**Estimated Time**: ~2-3 hours for all updates (spread across multiple sessions to avoid fatigue)
