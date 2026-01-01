# Sovereign Territories - Realistic Solo Developer MVP

**Last Updated**: January 1, 2026  
**Developer**: Solo indie, part-time (evenings/weekends), first game project  
**Full-Time Job**: Software/AI Engineer until April 2027  
**Realistic Timeline**: 16-24 weeks (4-6 months, not 8 weeks)  
**Core Philosophy**: TCG/Adventure/RPG hybrid (Pokemon TCG meets Slay the Spire meets Baldur's Gate)

---

## Development Reality Check

### Who I Am
- **Solo indie developer** making my first game
- **Part-time** (evenings/weekends, ~10-15 hours/week)
- **Software/AI engineer** full-time until April 2027
- **Hobby project** (passion-driven, but realistic about time constraints)
- **Capable but constrained** (I can code this, but I have limited hours)

### What I'm NOT Trying to Be
- ❌ **NOT Clash of Clans** - I'm not making a base-builder PvP game
- ❌ **NOT RTS grind** - No forced resource collection, no tap-to-collect monotony
- ❌ **NOT base-building focused** - Maps/Territory conquest is Phase 2-3 (NOT MVP)
- ❌ **NOT full-time studio** - Can't compete with 8-week AAA timelines

### What I AM Trying to Be
- ✅ **Pokemon TCG** - Card collection, deck-building, rarity progression
- ✅ **Slay the Spire** - Campaign runs, roguelike elements, strategic depth
- ✅ **Baldur's Gate** - Party-based RPG, heroes with Health/Mana, equipment
- ✅ **Heroes of Might and Magic** - Tactical 8×8 grid battles, hero-led armies
- ✅ **Fire Emblem** - Turn-based tactics, formations, strategic positioning

**Core Tagline**: "Build the Deck. Conquer the Campaign. Level Your Heroes."  
(NOT "Conquer the Map" - maps are Phase 2-3)

---

## MVP Philosophy (Scope Discipline)

**Success Metric**: Player completes tutorial, builds custom deck, wins 10 campaign battles, levels hero to 5, fuses first card to 2★, plays 3 Arena matches. If this feels fun, proceed to Phase 1.1.

### ✅ Must Have (Core Loop)
1. **Card System** (100 cards: 6 heroes, 30 units, 20 tactics, 20 buildings, 14 equipment, 10 workers)
2. **Pack Opening** (Standard/Element/Epic Packs, collector dopamine)
3. **Deck Building** (20-50 cards, 6-slot formations, tactic attachment)
4. **Campaign Mode** (60-80 battles, 4 Territories, 9 Realms, boss fights)
5. **8×8 Tactical Combat** (manual placement, auto-battle option, tactic AI)
6. **Star Rank Fusion** (1★→8★, duplicate progression)
7. **RPG Heroes** (Health/Mana stats, equipment slots, leveling)
8. **Discovery Tutorial** (5-min onboarding, 30 achievements, Codex)
9. **Scroll Crafting** (duplicate conversion → targeted cards, fixes RNG)
10. **Async Arena PvP** (5 battles/day, Colosseum Tokens, skill rewards)

### ⏸️ Nice to Have (If Time Allows)
- Battle Pass (defer to Phase 1.1 if tight on time)
- Advanced analytics (basic Unity Analytics sufficient for MVP)
- Colorblind mode (accessibility important, but not blocking MVP launch)

### ❌ Won't Have (Phase 2-3)
- **Territory/World Maps** - This is my long-term vision, but NOT MVP
- **Alliance Wars** (50v50) - Phase 3 endgame content
- **Live PvP** - Async Arena sufficient for MVP, live battles Phase 2
- **Economy Cards Deployment** - Food/Lumber/Ore system Phase 2
- **Building/Castle Management** - No base-building in MVP (avoiding RTS grind)

---

## Realistic Timeline (16-24 Weeks)

### Why NOT 8 Weeks?
- **Solo Part-Time**: 10-15 hours/week (not 40-60 hours/week for pro team)
- **First Game**: Learning Unity/Nakama as I go (expect 20-30% time on R&D)
- **Art Bottleneck**: 100 cards needs art (placeholder first, commission later if viable)
- **Testing Time**: Need 2-4 weeks for playtesting/balance (can't rush this)

### Aggressive Timeline (16 Weeks / 4 Months)
**Assumptions**: 15 hours/week avg, minimal art (placeholders), no major rewrites

**Weeks 1-4: Card System & UI Foundation** (~60 hours)
- Card data structures (CardData, CardManager, JSON loading)
- Pack opening UI (animation, rarity reveal)
- Collection/Codex UI (grid view, filters, search)
- Deck Builder UI (drag-drop, validation, save/load)
- Tutorial framework (5-step onboarding, achievement system)
- **Deliverable**: Can open packs, view collection, build decks (no combat yet)

**Weeks 5-8: Combat System** (~60 hours)
- 8×8 grid rendering (tile manager, unit placement)
- Turn-based combat logic (move, attack, tactic usage)
- Auto-battle AI (tactic instruction system)
- Battle UI (HP bars, turn order, ability buttons)
- **Deliverable**: Can play 1v1 battles with AI (no campaign yet)

**Weeks 9-12: Campaign Mode** (~60 hours)
- Campaign structure (4 Territories, 9 Realms, 60 battles)
- Enemy deck generation (difficulty scaling)
- Progression system (XP, leveling, unlock gates)
- Reward distribution (Gold, Stamina, packs)
- **Deliverable**: 60-battle linear campaign with boss fights

**Weeks 13-14: Crafting & Arena PvP** (~30 hours)
- Scroll crafting system (duplicate conversion, UI)
- Async Arena matchmaking (SQL queries, AI opponent decks)
- Colosseum Token shop (exclusive cards)
- **Deliverable**: Can craft cards, play 5 Arena battles/day

**Weeks 15-16: Polish & Testing** (~30 hours)
- Bug fixes, balance tuning
- Placeholder art refinement
- Internal playtesting (friends/family)
- Performance optimization (60 FPS mobile target)
- **Deliverable**: Playable MVP, ready for soft launch

**Total: 240 hours over 16 weeks** (15 hours/week avg)

---

### Conservative Timeline (24 Weeks / 6 Months)
**Assumptions**: 10 hours/week avg, art iteration, 1-2 major rewrites expected

**Weeks 1-6: Card System & UI** (~60 hours, same as aggressive)
**Weeks 7-12: Combat System** (~60 hours, +2 weeks for AI tuning)
**Weeks 13-18: Campaign Mode** (~60 hours, +2 weeks for 80 battles)
**Weeks 19-21: Crafting & Arena** (~30 hours, +1 week for Arena balance)
**Weeks 22-24: Polish & Testing** (~30 hours, +1 week for alpha feedback)

**Total: 240 hours over 24 weeks** (10 hours/week avg)

---

## Scope Prioritization (What to Cut If Behind)

### Tier 1: Absolutely Essential (Cannot Ship Without)
1. ✅ Card collection (100 cards minimum)
2. ✅ Deck building (20-card basic decks)
3. ✅ Combat system (8×8 grid, manual + auto-battle)
4. ✅ Campaign (40-60 battles minimum, can reduce from 80)
5. ✅ Tutorial (5-min onboarding, basic achievements)

### Tier 2: Strongly Recommended (Defer Only If Critical)
1. ⚠️ Scroll crafting (RNG mitigation, but can launch without)
2. ⚠️ Async Arena PvP (engagement loop, competitive validation)
3. ⚠️ Star rank fusion (progression depth, but 1★ cards work)
4. ⚠️ Equipment system (RPG flavor, but can launch with hero stats only)

### Tier 3: Nice to Have (Defer to Phase 1.1 Without Guilt)
1. ⏸️ Battle Pass (monetization, but Gold/Gem IAP sufficient for MVP)
2. ⏸️ Advanced analytics (Unity Analytics basic events OK for MVP)
3. ⏸️ Colorblind mode (accessibility important, but not blocking)
4. ⏸️ Localization (English-only MVP acceptable)

### Tier 4: Phase 2+ (Do NOT Add to MVP)
1. ❌ Territory/World Maps (your long-term vision, but not MVP scope)
2. ❌ Alliance system (social endgame, Phase 3)
3. ❌ Live PvP (async Arena sufficient for MVP)
4. ❌ Economy cards deployment (Food/Lumber/Ore, Phase 2)
5. ❌ Building/castle management (avoiding base-builder grind)

---

## Art Strategy (Solo Dev Reality)

### MVP Art Approach
**Goal**: Playable prototype, not polished launch (iterate if traction)

**Option 1: Placeholder Art** (Fastest, $0 cost)
- Use colored rectangles with text labels ("Fire Knight", "Goblin Raider")
- Icon packs from Kenney.nl or OpenGameArt (free, CC0 license)
- AI-generated placeholders (Midjourney, DALL-E) for hero portraits
- **Timeline**: 1-2 weeks to assemble 100 card placeholders
- **Cost**: $0 (or $50 Midjourney subscription for hero art)
- **Pro**: Ship MVP fast, validate gameplay before art investment
- **Con**: Not commercially viable (but fine for alpha/beta testing)

**Option 2: Commissioned Card Art** (Slower, $5k-10k budget)
- Hire freelance artist ($50-100 per card × 100 cards = $5k-10k)
- Upwork, Fiverr, ArtStation for vetted illustrators
- Style reference: Fire Emblem, Hearthstone, Gwent
- **Timeline**: 4-8 weeks (artist produces 12-25 cards/week)
- **Cost**: $5k-10k (stretch goal, only if MVP validated)
- **Pro**: Commercially viable, professional polish
- **Con**: High upfront cost, delays MVP launch

**Recommended Hybrid Approach**:
1. **Phase 0** (Weeks 1-16): Placeholder art + AI heroes (ship MVP alpha)
2. **Phase 1 Validation** (Weeks 17-20): Soft launch, gather feedback (100-500 playtesters)
3. **Phase 1.1 Polish** (Weeks 21-32): Commission 50 cards if retention >20% (heroes + meta cards)
4. **Phase 2 Full Art** (Weeks 33+): Commission remaining 50 cards + new expansions

---

## Technology Stack (Solo Dev Optimized)

### Why Unity?
- ✅ I'm a software engineer (C# is comfortable)
- ✅ Cross-platform (mobile + PC from single codebase)
- ✅ Asset Store (CardGameKit, UI Toolkit examples)
- ✅ Large community (Stack Overflow, YouTube tutorials)

### Why Nakama?
- ✅ Open-source game server (no AWS/Google Cloud complexity)
- ✅ Built-in matchmaking, leaderboards, player accounts
- ✅ Docker deployment (I can host on DigitalOcean $20/month)
- ✅ PostgreSQL backend (familiar with SQL)

### What I'm NOT Using (Avoiding Complexity)
- ❌ Custom server (Node.js/Python) - Nakama handles this
- ❌ Firebase/Playfab - Nakama is cheaper + more control
- ❌ Photon - Don't need real-time multiplayer (async Arena only)
- ❌ Blockchain/NFTs - Avoid hype, focus on gameplay

---

## Success Metrics (Realistic Expectations)

### Alpha Launch (MVP Complete, Week 16-24)
**Target**: 100-500 playtesters (friends, Reddit, Discord)
- **Retention**: 30% Day 7 (high for alpha, self-selected testers)
- **Session Length**: 20-30 min avg
- **Feedback**: Survey 50+ players (NPS score, feature requests)
- **Goal**: Validate core loop (Is deck-building + combat fun?)

### Beta Launch (Phase 1.1, Week 25-36)
**Target**: 1,000-5,000 players (soft launch, TestFlight/Google Play)
- **Retention**: 15-20% Day 7 (industry standard for indie TCG)
- **Monetization**: 2-5% conversion (starter packs, Battle Pass)
- **ARPU**: $1-3/month (low for MVP, iterate pricing)
- **Goal**: Validate monetization (Will players pay?)

### Public Launch (Phase 2, Week 37+)
**Target**: 10,000-50,000 players (App Store/Google Play/Steam)
- **Retention**: 10-15% Day 30 (sustainable for indie game)
- **Monetization**: 5-10% conversion (F2P mature)
- **ARPU**: $5-10/month (healthy for solo dev)
- **Revenue Target**: 10k players × 5% conversion × $10 ARPU = $5k/month

**Sustainability Threshold**: $3k-5k/month revenue = quit full-time job, go indie full-time

---

## Risk Mitigation (What Could Go Wrong)

### Technical Risks
1. **Unity Learning Curve** ⚠️ High
   - Mitigation: Follow tutorials (Brackeys, CodeMonkey), use Asset Store templates
   - Contingency: 20% time budget for R&D/rewrites
   
2. **Nakama Integration** ⚠️ Medium
   - Mitigation: Start with local SQLite, add Nakama Week 13-16
   - Contingency: Can ship single-player MVP if Nakama blocks (defer Arena to Phase 1.1)

3. **Performance (60 FPS Mobile)** ⚠️ Medium
   - Mitigation: Profile early (Unity Profiler), optimize sprite batching
   - Contingency: Target iPhone 12+ / Samsung S21+ (not iPhone 8)

### Content Risks
1. **100 Cards Too Many** ⚠️ High
   - Mitigation: Start with 50 cards (3 heroes, 15 units, 10 tactics)
   - Contingency: Can ship 50-card MVP, add 50 more in Phase 1.1

2. **80 Campaign Battles Too Many** ⚠️ Medium
   - Mitigation: Reduce to 40 battles (2 Territories, 5 Realms)
   - Contingency: Procedural generation (random enemy decks) if time-strapped

3. **Art Budget Overrun** ⚠️ Low
   - Mitigation: Placeholder art for MVP (validate before commissioning)
   - Contingency: AI art + icon packs (free/cheap)

### Scope Risks
1. **Feature Creep** ⚠️ **CRITICAL**
   - Mitigation: **Lock scope after Week 4** (no new features until MVP ships)
   - Contingency: Use Tier 1-4 prioritization (cut Tier 3-4 ruthlessly)

2. **Perfectionism** ⚠️ High
   - Mitigation: "Ship ugly, iterate fast" (alpha doesn't need polish)
   - Contingency: Set hard deadline (Week 16 or Week 24), ship no matter what

---

## Phase Roadmap (Solo Dev Reality)

### Phase 1 MVP (Weeks 1-16 or 1-24)
**Goal**: Validate core loop (deck-building + combat + campaign)
- ✅ 50-100 cards (placeholder art)
- ✅ 40-80 campaign battles
- ✅ 8×8 tactical combat
- ✅ Deck building + star fusion
- ✅ Scroll crafting (if time)
- ✅ Async Arena PvP (if time)
- ❌ Territory/World Maps (Phase 2-3)
- ❌ Alliance Wars (Phase 3)

**Timeline**: 16 weeks (aggressive) or 24 weeks (conservative)  
**Budget**: $0-500 (AI art, Nakama hosting)  
**Expected Revenue**: $0 (alpha testing, no monetization)

---

### Phase 1.1 Polish (Weeks 17-32, ~4 months)
**Goal**: Soft launch beta, commission art for top 50 cards
- ✅ Commissioned hero art (6 heroes × $75 = $450)
- ✅ Commissioned meta cards (20 cards × $50 = $1,000)
- ✅ Battle Pass ($10/month, revenue validation)
- ✅ Colorblind mode (accessibility)
- ✅ Balance pass (nerf/buff top decks)
- ✅ Analytics dashboard (Unity Analytics + Nakama)

**Timeline**: 16 weeks (part-time)  
**Budget**: $1,500-2,000 (art commission)  
**Expected Revenue**: $500-2,000 (100-500 beta players, 5% conversion)

---

### Phase 2 Content Expansion (Months 7-12)
**Goal**: Public launch, add 100 new cards, economy cards, live PvP
- ✅ +100 new cards (Lightning + Nature elements, full art)
- ✅ Economy cards deployment (Food/Lumber/Ore, AFK income)
- ✅ Live PvP Colosseum (websockets, real-time)
- ✅ Seasonal campaigns (monthly events)
- ✅ Localization (Spanish, Portuguese)
- ❌ Territory Maps (defer to Phase 3)

**Timeline**: 6 months (part-time)  
**Budget**: $5,000-10,000 (art, marketing)  
**Expected Revenue**: $3,000-10,000/month (10k-50k players, $5-10 ARPU)

---

### Phase 3 Endgame (Month 13+, Post-April 2027 Full-Time)
**Goal**: Territory Maps, Alliance Wars, your original vision fully realized
- ✅ **Territory/World Maps** (Risk-style conquest, your big vision)
- ✅ Alliance Wars (50v50, seasonal)
- ✅ Card skins (cosmetic monetization)
- ✅ Live events, tournaments
- ✅ Expansions (Metal, Divine, Dark elements)

**Timeline**: 6-12 months (full-time indie dev, if revenue sustainable)  
**Budget**: $10,000-20,000/year (art, marketing, server costs)  
**Expected Revenue**: $5,000-15,000/month (50k-200k players, sustainable indie studio)

---

## Mental Health & Sustainability

### Avoiding Burnout
- **10-15 hours/week max** (not 20-30 hours, protect family/health time)
- **1-2 evenings/week off** (mandatory rest, prevent crunch)
- **4-week sprints** (not continuous grind, review progress monthly)
- **Celebrate milestones** (first pack opened, first battle won, first player feedback)

### When to Pivot
**Kill Criteria** (If any 2 are true after Phase 1.1):
1. Day 7 retention <10% (core loop not fun)
2. Conversion <1% (monetization broken)
3. Negative feedback >50% (fundamental design flaw)

**If Kill Criteria Met**:
- Option 1: Shelve project, apply learnings to Game #2
- Option 2: Pivot to single-player premium ($5-10 Steam game)
- Option 3: Open-source project, build community

### When to Go Full-Time
**Success Criteria** (All 3 must be true):
1. $5,000+/month revenue sustained for 6 months
2. Day 30 retention >10% (player base stable)
3. Manageable workload (can maintain quality solo)

**If Success Criteria Met (April 2027+)**:
- Quit full-time job, indie dev full-time
- Hire freelance artist (ongoing card production)
- Focus on Phase 3 (Territory Maps, your big vision)

---

## Summary: What I'm Actually Building

**NOT**: Clash of Clans clone, base-builder, PvP-focused RTS grind  
**YES**: Pokemon TCG meets Slay the Spire meets Baldur's Gate meets Heroes of Might and Magic

**MVP Core** (16-24 weeks):
- 100 cards (placeholder art)
- 60-80 battle campaign (Slay the Spire progression)
- 8×8 tactical combat (Heroes of Might and Magic battles)
- Deck building + star fusion (Pokemon TCG collection)
- RPG heroes with Health/Mana (Baldur's Gate depth)
- Scroll crafting + Async Arena PvP (if time allows)

**Phase 2-3 Vision** (Territory Maps, Alliance Wars):
- This is my long-term goal, but NOT MVP
- Need to validate core loop first (deck-building + combat + campaign)
- If MVP fails, Territory Maps won't save it
- If MVP succeeds, Territory Maps are the endgame hook

**Development Philosophy**:
- "Ship ugly, iterate fast" (alpha doesn't need polish)
- "Core loop first, nice-to-haves later" (Tier 1 > Tier 2 > Tier 3 > Tier 4)
- "Validate before invest" (placeholder art → commission if retention >20%)
- "Protect mental health" (10-15 hours/week, 4-week sprints, celebrate wins)

---

**Document Version**: 1.0  
**Last Updated**: January 1, 2026  
**Next Review**: Week 4 (lock MVP scope) + Week 16/24 (alpha launch postmortem)
