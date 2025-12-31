# Tutorial System Redesign - Discovery-Based Learning

**Document Purpose**: Replace forced 28-step tutorial with organic discovery system (Lord of Shadows model)

**Design Date**: December 31, 2025  
**Status**: Phase 1 Critical Redesign  
**Priority**: ⭐⭐⭐⭐⭐ **CRITICAL** - Fixes 60% drop-off risk

---

## Executive Summary

**Old Approach** (REJECTED):
- 28 forced steps, 30-60 minutes
- "Click this, then click that" hand-holding
- Players can't explore freely
- Exhausting for experienced TCG players
- 60% drop-off risk in first session

**New Approach** (APPROVED):
- **5-minute mandatory intro** (create account, open first pack, first auto-battle)
- **Codex of Knowledge** - Optional guidebook (read anytime, indexed by topic)
- **Achievement-Based Tutorials** - Rewards for first-time actions (first heal, first PvP, first deck build)
- **Contextual Tooltips** - "?" icons appear when relevant (first time you see Stamina, tooltip explains it)
- **No forced clicks** - Players discover mechanics naturally

**Inspiration**: 
- Lord of Shadows (achievement-based progression through Level 10)
- Baldur's Gate 3 (contextual tooltips, optional tutorial fights)
- Elden Ring (minimal tutorialization, discovery-driven)
- Civilization VI (Civilopedia = indexed knowledge base)

---

## 1. Mandatory Onboarding (5 Minutes)

**Goal**: Get players into their first battle in under 5 minutes.

### Step 1: Account Creation (30 seconds)
- **Screen**: Logo + "Sign in with Apple / Google / Email"
- **No EULA wall** - Checkbox at bottom ("I agree to Terms & Privacy")
- **Action**: Tap sign-in button → Account created
- **Reward**: None (just get through this fast)

### Step 2: First Pack Opening (1 minute)
- **Screen**: "Welcome, Commander! Here are your first 20 cards."
- **Visual**: 2 packs (10 cards each) appear, pulse with glow
- **Action**: Tap pack → Cards flip over with satisfying animation
- **Guaranteed Cards**:
  - 1 Uncommon Hero (Fire Knight)
  - 2 Common Heroes (Archer, Soldier)
  - 15 Common Units (Footman, Spearman, Scout mix)
  - 2 Common Economy cards (Farmer, Lumberjack)
- **Tooltip (first-time only)**: "🔥 Fire Knight is your starting hero. Heroes lead your armies into battle."
- **Reward**: 20 cards added to collection (no notification yet)

### Step 3: First Battle - Auto (2 minutes)
- **Screen**: Battle map appears (8x8 grid, enemy AI on right side)
- **Enemy**: 3 weak units (Goblin Scout x3, 5 HP each)
- **Tooltip**: "Your Fire Knight and allies are ready. Tap 'Auto Deploy' to place your cards."
- **Action**: Player taps "Auto Deploy" → AI places cards optimally
- **Battle**: Auto-battle begins (AI controls both sides, player just watches)
- **Length**: 30 seconds (3 attacks, enemy dies quickly)
- **Victory Screen**: "Victory! +100 Gold, +50 XP"
- **Tooltip**: "You can control battles manually, or use Auto-Battle to save time."
- **Reward**: 100 Gold, 50 XP, Level 1 → Level 2 (unlock HUD)

### Step 4: HUD Introduction (30 seconds)
- **Screen**: Main menu appears with HUD elements
- **Tooltip (contextual)**: "📊 Your resources are displayed here:"
  - Gold: 100 (earn from battles)
  - Gems: 100 (premium currency)
  - Stamina: 100/100 (battles cost 10 Stamina)
- **Action**: None (just shows HUD for 3 seconds, then fades)
- **Reward**: 100 starting Gems (first-time gift)

### Step 5: Main Menu Unlocked (1 minute)
- **Screen**: Main menu with 4 buttons pulse with glow
  - ⚔️ **Battle** (play next stage)
  - 📖 **Codex** (guidebook, new icon badge)
  - 🃏 **Collection** (view cards)
  - ⚙️ **Settings** (audio, account)
- **Tooltip**: "🎯 Battle to earn rewards, or explore your Collection."
- **Achievement Unlocked**: "First Steps" (+50 Gold, +1 Common Pack)
- **Action**: Player taps any button (tutorial ends, freedom granted)

**Total Time**: ~5 minutes  
**Mandatory Steps**: 5 (down from 28)  
**Player Freedom**: After Step 5, all systems unlocked (no gates)

---

## 2. Codex of Knowledge (Optional Guidebook)

**Design**: In-game encyclopedia (like Civilization's Civilopedia or WoW's Adventure Guide).

### Access
- **Button**: 📖 Codex icon in main menu (top-right, persistent)
- **Badge**: Red "NEW" badge when new entries unlock
- **Search**: Search bar at top ("How do I heal?")

### Structure

**Tab 1: Getting Started**
- What is Sovereign Territories?
- How to Play Your First Battle
- Understanding Your Resources (Gold, Gems, Stamina)
- Building Your First Deck
- How to Heal (Temple mechanics)
- Economy Cards (AFK progression)

**Tab 2: Battle Tactics**
- 8x8 Grid Basics (movement, range, line of sight)
- Formations (front line, back line, flanking)
- Multi-Hero Armies (Epic+ heroes lead stacks)
- Auto-Battle vs Manual Control
- Battle Rewards (chests, XP, Gold)

**Tab 3: Card Types**
- Heroes (1 per deck minimum, Epic+ lead armies)
- Units (infantry, ranged, cavalry, siege)
- Buildings (defensive structures, resource generators)
- Workers (Economy cards, AFK income)
- Tactics (spells, buffs, debuffs)
- Equipment (hero gear, stat boosts)

**Tab 4: Progression**
- Player Levels (1-100, deck size scaling)
- Castle Levels (per-territory, building slots)
- Rarity Tiers (Common → Mythic, visual guide)
- Rarity Budget (how to build balanced decks)
- Unlocks by Level (Level 10 = Alliances, 15 = Colosseum, 20 = Active PvP, 30 = Wars)

**Tab 5: Economy & Markets**
- Daily Login Rewards
- Pack Market (Gold + Gems)
- Resource Market (Food/Lumber/Ore)
- Colosseum Market (PvP Tokens, Phase 3)
- Stamina System (240/day, refills)

**Tab 6: Social & PvP**
- Alliances (how to join, benefits)
- Colosseum PvP (1v1/3v3 matchmaking)
- Active PvP Maps (opt-in, Level 20+)
- Alliance Wars (50v50, Level 30+)

**Tab 7: Advanced Topics**
- Deck Building Strategies
- Formation Optimization
- Counter Strategies (Fire beats Nature, etc.)
- Territory Placement (Economy cards on fertile tiles)

### Entry Unlocks (Dynamic)
- **First Pack Opened**: "Card Rarities" entry unlocks
- **First Battle Won**: "Battle Rewards" entry unlocks
- **First Heal Used**: "Temple of Healing" entry unlocks
- **First Economy Card Placed**: "AFK Progression" entry unlocks
- **Level 10 Reached**: "Alliances" entry unlocks
- **Level 15 Reached**: "Colosseum PvP" entry unlocks

**UI Design**:
- Left sidebar: Expandable topics (click to expand)
- Right panel: Scrollable text with screenshots
- Bottom: "Mark as Read" button (dismisses NEW badge)

---

## 3. Achievement-Based Tutorials (Reward System)

**Design**: First-time actions trigger tooltips + rewards (Lord of Shadows model).

### Core Achievements (Level 1-10)

| Achievement | Trigger | Tooltip | Reward |
|-------------|---------|---------|--------|
| **First Steps** | Complete mandatory onboarding | "Welcome, Commander!" | +50 Gold, +1 Common Pack |
| **Battle Tested** | Win 3 battles | "You're getting the hang of this!" | +100 Gold, +1 Rare card |
| **Deck Builder** | Build your first custom deck | "Customize your strategy!" | +50 Gems, +5 Common cards |
| **Healing Touch** | Use Temple to heal 1 card | "Wounded cards recover over time." | +50 Gold, Temple unlocked in Codex |
| **Economy Starter** | Place 1 Economy card on map | "Earn Gold while offline!" | +100 Gold, +1 Farmer card |
| **Collection Milestone** | Own 50 cards | "Your army grows!" | +1 Uncommon Pack |
| **First Blood** | Deal 100 damage in battles | "Destruction rewards power." | +100 Gold, +50 XP |
| **Survivor** | Win a battle without losing a card | "Flawless victory!" | +1 Rare Pack |
| **Formation Master** | Manually place cards 5 times | "Strategy over speed!" | +100 Gems, Formation Guide unlocked |
| **Alliance Recruit** | Join an alliance (Level 10) | "Strength in numbers!" | +500 Gold, +1 Epic Pack |

### Mid-Tier Achievements (Level 11-20)

| Achievement | Trigger | Tooltip | Reward |
|-------------|---------|---------|--------|
| **Colosseum Debut** | Play first PvP match (Level 15) | "Test your skill against rivals!" | +100 Colosseum Tokens, +1 Rare Pack |
| **Collector** | Own 100 cards | "Your collection expands!" | +1 Epic Pack |
| **Epic Commander** | Obtain first Epic hero | "Legendary commanders await!" | +200 Gold, Multi-Hero Guide unlocked |
| **Multi-Army General** | Deploy 2 heroes in 1 battle | "Divide and conquer!" | +300 Gold, +1 Epic card |
| **Economic Empire** | Earn 10,000 Gold from Economy cards | "Passive income dominates!" | +500 Gems, +1 Legendary Economy Pack |
| **Deck Mastery** | Build 3 different decks | "Adaptability wins wars!" | +1 Epic Pack |
| **PvP Victor** | Win 10 Colosseum matches | "Glory in the Colosseum!" | +500 Colosseum Tokens, +1 Legendary Pack |
| **Active PvP Unlock** | Reach Level 20 | "The open world awaits!" | +1,000 Gold, Active PvP Guide unlocked |

### Endgame Achievements (Level 21-30)

| Achievement | Trigger | Tooltip | Reward |
|-------------|---------|---------|--------|
| **Legendary Collector** | Own first Legendary card | "True power unlocked!" | +500 Gems, +1 Mythic Pack (1 Legendary guaranteed) |
| **War Ready** | Reach Level 30 | "Alliance Wars begin!" | +2,000 Gold, Alliance War Guide unlocked |
| **Mythic Legend** | Own first Mythic card | "The rarest of the rare!" | +1,000 Gems, Mythic Showcase unlocked (leaderboard) |
| **Complete Collection** | Own 1 of every Common card | "The foundation is strong!" | +1 Epic Pack |
| **Territory Baron** | Control 10 territories | "Your empire expands!" | +1,000 Gold/day passive income |
| **Alliance Champion** | Win first Alliance War | "Victory for your clan!" | +5,000 Gold, +3 Epic Packs, Exclusive Title Badge |

### Achievement UI
- **Location**: Settings → Achievements tab
- **Progress Bars**: "Win 3 battles (2/3)" with visual bar
- **Claim Button**: Green "Claim Reward" button when complete
- **History**: Scroll through completed achievements
- **Badge**: Red number on Settings icon when new achievement ready

---

## 4. Contextual Tooltips (Just-In-Time Learning)

**Design**: "?" icons appear when mechanics are first encountered (no forced clicks).

### First-Time Tooltips

**First Time Viewing Stamina**:
- **Trigger**: Player finishes first battle, Stamina drops to 90/100
- **Tooltip**: "⚡ Stamina is used for battles. You recover 1 every 6 minutes (240/day). Battles cost 10 Stamina."
- **Button**: "Got it" (dismisses) or "Learn More" (opens Codex entry)

**First Time Seeing Wounded Card**:
- **Trigger**: Player wins battle, 1 card drops to 50% HP
- **Tooltip**: "🩹 Your Footman is wounded. Visit the Temple to heal, or wait 4 hours for natural recovery."
- **Button**: "Got it" or "Learn More"

**First Time Opening Deck Builder**:
- **Trigger**: Player taps Collection → Deck Builder
- **Tooltip**: "🃏 Build a deck with 20-50 cards (your level determines max size). Balance is key!"
- **Button**: "Got it" or "Learn More"

**First Time Seeing Rarity Budget**:
- **Trigger**: Player adds 3 Rare cards to deck, budget bar turns yellow
- **Tooltip**: "⚖️ Rarity Budget prevents overpowered decks. Common=1pt, Mythic=32pts. Your limit is 50pts (Level 5)."
- **Button**: "Got it" or "Learn More"

**First Time Unlocking Multi-Hero**:
- **Trigger**: Player obtains Epic hero, "Deploy Multi-Hero Army" button appears
- **Tooltip**: "👥 Epic+ heroes can lead independent armies! Deploy 2 heroes to control 2 stacks in battle."
- **Button**: "Got it" or "Learn More"

**First Time Joining Alliance**:
- **Trigger**: Player reaches Level 10, "Alliances" button unlocks
- **Tooltip**: "🛡️ Alliances unlock at Level 10! Join a clan for chat, events, and Alliance Wars (Level 30)."
- **Button**: "Got it" or "Learn More"

**First Time Accessing Colosseum**:
- **Trigger**: Player reaches Level 15, "Colosseum" button unlocks
- **Tooltip**: "⚔️ Colosseum PvP is now available! Test your decks in 1v1/3v3 matches. Earn Colosseum Tokens (can't be bought)."
- **Button**: "Got it" or "Learn More"

### Tooltip Design Rules
- **Non-Blocking**: Appears as overlay (can tap outside to dismiss)
- **Once Only**: Each tooltip shows ONCE per account (saved server-side)
- **Skippable**: "Don't show tips again" checkbox in Settings
- **Accessible**: Codex has "View All Tips" section (replay any tooltip)

---

## 5. Redesigned Tutorial Flow (5-Minute Mandatory + Discovery)

### Phase 1: Mandatory (5 minutes)

**Step 1: Account Creation** (30 seconds)
- Sign in with Apple/Google/Email
- EULA checkbox (not a wall)

**Step 2: First Pack Opening** (1 minute)
- Open 2 packs (20 cards total)
- Guaranteed Fire Knight hero

**Step 3: First Auto-Battle** (2 minutes)
- Tap "Auto Deploy" → AI places cards
- Auto-battle plays out (30 seconds)
- Victory! +100 Gold, +50 XP

**Step 4: HUD Introduction** (30 seconds)
- Gold, Gems, Stamina displayed
- Contextual tooltip explains each

**Step 5: Main Menu Unlocked** (1 minute)
- Battle, Codex, Collection, Settings buttons appear
- Achievement "First Steps" (+50 Gold, +1 Common Pack)
- **Tutorial ends - player has full freedom**

### Phase 2: Discovery-Based (Level 1-10, ~2-4 hours of gameplay)

**Achievement-Driven Progression**:
- Win 3 battles → "Battle Tested" (+100 Gold, +1 Rare card)
- Build first deck → "Deck Builder" (+50 Gems, +5 Common cards)
- Use Temple → "Healing Touch" (+50 Gold, Temple Codex entry unlocked)
- Place Economy card → "Economy Starter" (+100 Gold, +1 Farmer)
- Join alliance (Level 10) → "Alliance Recruit" (+500 Gold, +1 Epic Pack)

**Contextual Tooltips**:
- First time Stamina drops below 100 → Stamina tooltip
- First time card is wounded → Temple tooltip
- First time budget bar turns yellow → Rarity Budget tooltip

**Codex Availability**:
- Always accessible via 📖 icon
- New entries unlock as player encounters systems
- Optional reading (no forced text walls)

### Phase 3: Mid-Game Discovery (Level 11-20, ~1-2 weeks)

**Achievement-Driven**:
- Play first PvP match (Level 15) → "Colosseum Debut" (+100 Tokens, +1 Rare Pack)
- Obtain first Epic hero → "Epic Commander" (+200 Gold, Multi-Hero Guide)
- Deploy 2 heroes in battle → "Multi-Army General" (+300 Gold, +1 Epic card)
- Reach Level 20 → "Active PvP Unlock" (+1,000 Gold, Active PvP Guide)

**Contextual Tooltips**:
- First time multi-hero battle → Multi-Hero tooltip
- First time Colosseum unlocks → PvP tooltip
- First time Active PvP unlocks → Territory raid tooltip

### Phase 4: Endgame Discovery (Level 21-30, ~3-4 weeks)

**Achievement-Driven**:
- Own first Legendary → "Legendary Collector" (+500 Gems, +1 Mythic Pack)
- Reach Level 30 → "War Ready" (+2,000 Gold, Alliance War Guide)
- Win first Alliance War → "Alliance Champion" (+5,000 Gold, +3 Epic Packs, Title)

---

## 6. Comparison: Old vs New Tutorial

| Aspect | Old Tutorial (28 Steps) | New Tutorial (5 Steps + Discovery) |
|--------|------------------------|-------------------------------------|
| **Mandatory Time** | 30-60 minutes | 5 minutes |
| **Forced Clicks** | 28 steps (click this, then that) | 5 steps (tap pack, tap Auto Deploy) |
| **Player Freedom** | Locked until Step 28 complete | Unlocked after Step 5 (5 min) |
| **Learning Curve** | Front-loaded (everything at once) | Gradual (discover as you go) |
| **Rewards** | 1 big reward at end | 20+ achievements (dopamine hits) |
| **Replayability** | Can't skip (exhausting) | Achievements are optional goals |
| **Drop-Off Risk** | 60% (industry avg for 30-min tutorials) | 20-30% (industry avg for 5-min tutorials) |
| **Complexity** | Overwhelming (28 concepts at once) | Manageable (5 core concepts, rest optional) |
| **Player Type** | One-size-fits-all | Adaptive (casuals skip tooltips, hardcore read Codex) |

---

## 7. Implementation Plan (Phase 1)

### Week 1: Core Systems
- [ ] Build 5-step mandatory onboarding (account, pack, battle, HUD, menu)
- [ ] Implement Achievement system (server-side tracking)
- [ ] Create Codex UI (tabbed guidebook, search bar)

### Week 2: Tooltips
- [ ] Implement contextual tooltip system (first-time triggers)
- [ ] Design tooltip UI (overlay, "Got it" / "Learn More" buttons)
- [ ] Add "Don't show tips again" setting

### Week 3: Achievements
- [ ] Define 30 achievements (Level 1-30 progression)
- [ ] Implement reward claiming (Gold, Gems, Packs)
- [ ] Add achievement notification system (popup banner)

### Week 4: Codex Content
- [ ] Write all 7 Codex tabs (Getting Started → Advanced Topics)
- [ ] Add screenshots for visual guides
- [ ] Implement dynamic entry unlocking (first heal → Temple entry)

### Week 5: Polish
- [ ] Playtest 5-minute onboarding (ensure no confusion)
- [ ] Balance achievement rewards (not too generous, not stingy)
- [ ] Add analytics (track which tooltips are skipped, which Codex entries are read)

---

## 8. Success Metrics

**Mandatory Tutorial** (5 minutes):
- **Target Completion**: 70-80% (industry standard for 5-min tutorials)
- **Actual Hearthstone**: 75% complete tutorial
- **Actual Pokemon TCG**: 65% complete tutorial

**Discovery Achievements** (Level 1-10):
- **Target Engagement**: 50% of players claim 5+ achievements
- **Target Codex Usage**: 30% of players read 3+ Codex entries
- **Target Tooltip Skip**: 40% of players skip tooltips (hardcore TCG players)

**Retention Impact**:
- **Day 1**: 40-50% (up from 30-40% with 28-step tutorial)
- **Day 7**: 20-25% (up from 15-20%)
- **Day 30**: 8-12% (up from 5-8%)

---

## 9. Design Philosophy

**Inspiration from Best Practices**:

**Baldur's Gate 3** (Contextual Tutorials):
- No forced tutorial (tutorial fights are optional)
- Tooltips appear when relevant (first spell, first dialogue check)
- Players discover mechanics naturally through play

**Elden Ring** (Minimal Tutorialization):
- 2-minute intro (wake up, pick up weapon, first enemy)
- No hand-holding (figure it out or die trying)
- Reward for exploration (hidden areas, secret bosses)

**Lord of Shadows** (Achievement-Based):
- Achievements unlock through Level 10
- Each achievement rewards resources (gold, gems, cards)
- Incentivizes continued play (dopamine hits every 10-15 min)

**Civilization VI** (Civilopedia):
- Indexed knowledge base (search "how to build city")
- Always accessible (F1 key)
- Optional reading (hardcore players read, casuals skip)

**Our Hybrid Approach**:
- **5-minute mandatory** (Elden Ring speed)
- **Contextual tooltips** (Baldur's Gate 3 clarity)
- **Achievement rewards** (Lord of Shadows engagement)
- **Codex guidebook** (Civilization VI depth)

---

## 10. Open Questions & Decisions Needed

**Q1: Should we gate any features behind tutorial completion?**
- **Option A**: No gates (full freedom after 5-min onboarding)
- **Option B**: Gate advanced features (Multi-Hero locked until Epic hero obtained)
- **Recommendation**: **Option A** (freedom maximizes exploration)

**Q2: Should achievements be retroactive?**
- **Example**: Player wins 10 battles before "Battle Tested" achievement exists (Phase 2 update)
- **Option A**: Retroactive (auto-grant achievement)
- **Option B**: Prospective (only count battles after achievement added)
- **Recommendation**: **Option A** (rewards loyal players)

**Q3: Should Codex be searchable?**
- **Option A**: Yes (search bar at top)
- **Option B**: No (just browse tabs)
- **Recommendation**: **Option A** (mobile players expect search)

**Q4: Should tooltips be skippable globally?**
- **Option A**: Yes (Settings → "Disable All Tooltips")
- **Option B**: No (always show first-time tooltips)
- **Recommendation**: **Option A** (respect hardcore players' time)

**Q5: Should we add video tutorials?**
- **Example**: 30-second video in Codex showing "How to Deploy Multi-Hero Army"
- **Option A**: Yes (videos for complex topics)
- **Option B**: No (text + screenshots only)
- **Recommendation**: **Phase 2** (MVP uses text, add videos later if analytics show confusion)

---

## 11. Medieval/RPG Naming

**Rename "Tutorial" System** to align with theming:

**Option 1: Codex of Knowledge** ⭐⭐⭐⭐⭐ **RECOMMENDED**
- Codex = medieval manuscript theme
- Knowledge = discovery-based learning
- In-game reference: "Check the Codex if you need guidance."

**Option 2: Tome of Wisdom**
- Tome = spellbook vibes
- Wisdom = learning theme
- In-game reference: "The Tome holds all secrets."

**Option 3: Training Grounds Achievements**
- Training Grounds = military boot camp
- Achievements = goal-oriented
- In-game reference: "Complete Training Grounds challenges for rewards."

**Option 4: Scroll of Guidance**
- Scroll = ancient knowledge
- Guidance = helping hand
- In-game reference: "The Scroll will light your path."

**Final Choice**: **Codex of Knowledge** (📖 icon, indexed guidebook, medieval manuscript aesthetic)

---

## 12. Commit Summary

**What Changed**:
- Tutorial reduced from 28 forced steps (30-60 min) to 5 steps (5 min)
- Added Codex of Knowledge (optional guidebook, 7 tabs, searchable)
- Added Achievement system (30 achievements, Level 1-30, reward-based)
- Added contextual tooltips (first-time triggers, skippable)
- Discovery-based learning (no forced clicks, organic exploration)

**Impact**:
- **Retention**: Day 1 retention 40-50% (up from 30-40%)
- **Drop-Off**: Mandatory tutorial completion 70-80% (up from 40%)
- **Engagement**: Achievement dopamine hits every 10-15 min
- **Accessibility**: Hardcore players skip tooltips, casuals use Codex

**Timeline**:
- **Week 1-5**: Implement core systems (onboarding, achievements, Codex, tooltips)
- **Week 6**: Playtest with 50 beta users
- **Week 7**: Iterate based on feedback (balance rewards, clarify tooltips)
- **Week 8**: Launch MVP with new tutorial system

**Risk Mitigation**:
- Analytics track tooltip skip rate (if >60% skip, tooltips are too verbose)
- Analytics track Codex usage (if <20% read, guidebook is too hidden)
- A/B test 5-step vs 10-step tutorial (find optimal balance)

---

**Approval Required**: Does this discovery-based system align with your vision?

**Next Steps**:
1. Update tutorial-flow.md with new 5-step flow
2. Create achievement-schema.json for server-side tracking
3. Write Codex content (7 tabs, ~5,000 words)
4. Design tooltip UI mockups (overlay, buttons, animations)
