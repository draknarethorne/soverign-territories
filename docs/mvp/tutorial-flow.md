# Sovereign Territories - Tutorial Flow & Player Onboarding

**Version**: 1.0  
**Last Updated**: December 29, 2025  
**Purpose**: Step-by-step player experience for the first 15-60 minutes of gameplay

---

## Overview

This document walks through the **exact player journey** from app launch to first victory, calling out every UI screen, decision point, animation, and gap that needs design/development decisions.

**Target Experience**:
- **First 15 minutes**: Account → Card Draw → Deck Build → First Battle → Victory
- **First Hour**: 5-10 tutorial battles, Codex introduction, basic economy understanding
- **Goal**: Player feels excited about their cards, understands combat, wants to keep playing

**Design Pillars**:
1. **Immediate Gratification**: Player sees cool cards in first 2 minutes
2. **Agency Without Overwhelm**: Offer choice (deck type) without decision paralysis
3. **Easy First Win**: Tutorial battle is unlosable, teaches core mechanics
4. **Codex Discovery**: Players understand collection/storage early
5. **No Economy Stress**: Skip castle building, resource gathering until post-tutorial

---

## Phase 1: Launch & Account Creation (0-2 Minutes)

### Step 1: App Launch
**Screen**: Splash Screen
```
[Sovereign Territories Logo]
[Animated: Crown materializing from cards]
[Loading bar: "Loading assets..." 0-100%]
```

**Design Decisions Needed**:
- [ ] Splash duration (2-3 seconds minimum for asset loading)
- [ ] Logo animation style (fade in, particle effect, crown assembly?)
- [ ] Loading bar visibility (always show or only if loading >3 seconds?)

---

### Step 2: Main Menu (First-Time Player)
**Screen**: Main Menu
```
[Background: Animated Realm Map with fog]
[Center: "Sovereign Territories" title logo]

[Large Button: "START YOUR JOURNEY"]
[Small Button: "Settings"]
[Small Button: "Quit"]
```

**Player Action**: Taps "START YOUR JOURNEY"

**Design Decisions**:
- Background animation: Subtle parallax with moving fog (2-3 layers)
- Audio: Epic orchestral theme (60-90 sec loop, fade on scene transition)

---

### Step 2B: EULA/Privacy Acceptance (One-Time, Legally Required)
**Screen**: Terms of Service
```
[Header: "Welcome to Sovereign Territories"]

[Scrollable Text Box - 200 words]:
"By playing Sovereign Territories you agree to:
• Collect cards, battle enemies, manage territories
• Age requirement: 13+ (COPPA compliance)
• Data we collect: Email (optional), device ID, gameplay stats
• Data usage: Save progress, improve game, send updates
• No selling of personal data to third parties
• Full details: [Read Full Terms] [Read Privacy Policy]"

[☐ I accept the Terms of Service and Privacy Policy]

[Continue] (disabled until checked)
```

**Player Action**: 
1. Scrolls through terms (optional)
2. Checks acceptance box
3. Taps "Continue"

**System Actions**:
1. Store acceptance: `PlayerPrefs.SetInt("EULA_Accepted_v1", 1)`
2. Store date: `PlayerPrefs.SetString("EULA_Accept_Date", DateTime.UtcNow)`
3. Skip this screen on future launches (already accepted)

**Edge Cases**:
- Player declines (unchecks box): Continue button stays disabled, cannot proceed
- Under 13: Show "Ask a parent or guardian to play" (require 13+ checkbox)
- Terms update: Bump version to `EULA_Accepted_v2`, re-prompt existing users

**Implementation Notes**: See tutorial-gap-resolutions.md Gap 1 for full legal text and Unity code

---

### Step 3: Account Creation
**Screen**: Welcome Screen
```
[Header: "Welcome, Sovereign!"]
[Text: "Choose how you'd like to continue:"]

[Button: Continue as Guest] (auto-generates "Player_12345")
[Button: Sign In with Email]
[Button: Sign In with Google]
[Button: Sign In with Apple] (iOS only)
[Button: Sign In with Steam] (PC only)
```

**Player Action**: Taps "Continue as Guest" (fastest path)

**System Actions**:
1. Generate unique device ID
2. Create Nakama account (device auth)
3. Assign default name: "Player_[random 5-digit number]"
4. Store session token locally (PlayerPrefs encrypted)

**Design Decisions**:
- Default name format: `Player_12345` (5-digit random number)
- Name change: Free once at Level 3, then 100 gold per change
- Offline mode: Not supported in MVP (requires Nakama for all features)

---

### Step 4: Name Selection (Optional)
**Screen**: Name Your Sovereign (Skippable)
```
[Header: "Name Your Sovereign"]
[Text: "You can change this later in Settings"]

[Input Field: "Player_54821"] (pre-filled with default)
[Character Limit: 15 characters]
[Validation: No profanity, no special characters]

[Button: Continue] (enabled if valid name)
[Link: "Skip for now"]
```

**Player Action**: Types "Scott" → Taps "Continue"

**System Actions**:
1. Validate name (length, profanity filter)
2. Check uniqueness (if taken, suggest "Scott_123")
3. Update Nakama user profile
4. Store name locally

**Design Decisions Needed**:
- [ ] Name validation rules (profanity filter level, Unicode support?)
- [ ] Uniqueness requirement (allow duplicates with discriminator #1234?)
- [ ] Name change cost later (free first change, then 500 gems?)

---

## Phase 2: Initial Card Draw (2-5 Minutes) - THE HOOK

### Step 5: Opening Cinematic
**Screen**: Trainer Deck Selection Intro
```
[Fade in: Mystical card vault opening]
[Narrator text: "Your journey begins with these cards..."]
[Animated: 6 glowing Trainer Decks appearing in a circle]
[Text: "Choose your path..." fades in]
[Button: "Choose Your Deck"] (pulsing)
```

**Player Action**: Taps "Choose Your Deck"

**Design Decisions Needed**:
- [ ] Narrator voice (text only or voice-over?)
- [ ] Cinematic skip (allow skip after 1 second? or force watch first time?)
- [ ] Music shift (calm → exciting as packs appear)

---

I fee### Step 6: Trainer Deck Selection (CRITICAL MOMENT - THE HOOK)
**Screen**: Choose Your Starting Path
```
[Header: "Choose Your Trainer Deck"]
[Subtitle: "Begin your journey with 20 curated cards"]

[6 Deck Options in 2 rows × 3 columns]

ROW 1: CURATED DECKS (Named Epic Hero + Themed Support)
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ FLAME WARLORD DECK  │ TIDAL GUARDIAN DECK │ STONE SENTINEL DECK │
│ [Fire Element]      │ [Water Element]     │ [Earth Element]     │
│                     │                     │                     │
│ Epic: Flame Warlord │ Epic: Tidal Guard   │ Epic: Stone Sentinel│
│ 20 Fire-synergy     │ 20 Water-synergy    │ 20 Earth-synergy    │
│ cards included      │ cards included      │ cards included      │
│                     │                     │                     │
│ [Preview 5 Cards]   │ [Preview 5 Cards]   │ [Preview 5 Cards]   │
│ [SELECT]            │ [SELECT]            │ [SELECT]            │
└─────────────────────┴─────────────────────┴─────────────────────┘

ROW 2: ELEMENT DECKS (Guaranteed Epic + Random Support)
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ FIRE ELEMENT DECK   │ WATER ELEMENT DECK  │ EARTH ELEMENT DECK  │
│ [Fire Element]      │ [Water Element]     │ [Earth Element]     │
│                     │                     │                     │
│ Epic: Random Fire   │ Epic: Random Water  │ Epic: Random Earth  │
│ 20 varied cards     │ 20 varied cards     │ 20 varied cards     │
│ (more randomness)   │ (more randomness)   │ (more randomness)   │
│                     │                     │                     │
│ [? ? ? ? ?]         │ [? ? ? ? ?]         │ [? ? ? ? ?]         │
│ [SELECT]            │ [SELECT]            │ [SELECT]            │
└─────────────────────┴─────────────────────┴─────────────────────┘

[Bottom: "Need help choosing?" tooltip - explains Curated vs Random]
```

**Deck Categories**:

**CURATED DECKS** (3 options):
- **Guaranteed Contents**: Specific named Epic + pre-built theme
- **Playstyle**: Locked synergy (all cards work together)
- **Appeal**: New players, collectors, competitive (meta-ready)

**ELEMENT DECKS** (3 options):
- **Guaranteed Contents**: Epic from element pool + random support
- **Playstyle**: Higher variance, deckbuilding challenge
- **Appeal**: Replayability, players who like RNG

---

**Curated Deck #1: Flame Warlord Deck** (Fire Element)
- **Epic Hero**: Flame Warlord (Fire, 5★)
  - Melee attacker, burn damage-over-time, aggressive playstyle
- **20 Cards Total**:
  - 1× Flame Warlord (Epic Hero)
  - 6× Fire Units (Pyromancer ×2, Fire Knight ×2, Ember Scout ×2)
  - 2× Fire Buildings (Forge, Barracks)
  - 1× Fire Worker (Coal Miner)
  - 8× Fire Tactics (Fireball, Flame Wall, Scorched Earth, etc.)
  - 2× Fire Equipment (Flaming Sword, Ember Shield)
- **Synergy Theme**: Burn stacking (units apply burn, hero amplifies damage)
- **Recommended For**: Aggressive players, beginners (straightforward)

**Curated Deck #2: Tidal Guardian Deck** (Water Element)
- **Epic Hero**: Tidal Guardian (Water, 5★)
  - Tank/healer hybrid, defensive auras, sustain playstyle
- **20 Cards Total**:
  - 1× Tidal Guardian (Epic Hero)
  - 6× Water Units (Cleric ×2, Guardian ×2, Frost Mage ×2)
  - 2× Water Buildings (Temple, Granary)
  - 1× Water Worker (Fisher)
  - 8× Water Tactics (Heal Wave, Ice Shield, Tidal Surge, etc.)
  - 2× Water Equipment (Healing Staff, Frost Armor)
- **Synergy Theme**: Healing chain (units heal adjacent allies, hero amplifies)
- **Recommended For**: Defensive players, beginners (forgiving)

**Curated Deck #3: Stone Sentinel Deck** (Earth Element)
- **Epic Hero**: Stone Sentinel (Earth, 5★)
  - Ranged DPS, area control, terrain manipulation
- **20 Cards Total**:
  - 1× Stone Sentinel (Epic Hero)
  - 6× Earth Units (Forest Ranger ×2, Druid ×2, Earth Elemental ×2)
  - 2× Earth Buildings (Grove, Quarry)
  - 1× Earth Worker (Lumberjack)
  - 8× Earth Tactics (Entangle, Earthquake, Stone Wall, etc.)
  - 2× Earth Equipment (Thornbow, Earth Armor)
- **Synergy Theme**: Terrain control (slow enemies, increase movement cost)
- **Recommended For**: Tactical players, intermediate skill

---

**Element Deck #4: Fire Element Deck** (Random Fire Cards)
- **Epic Hero**: Random Fire Epic (from pool of 5-8 Fire Epics)
  - Could be: Flame Warlord, Phoenix Knight, Inferno Mage, etc.
- **20 Cards Total**:
  - 1× Random Fire Epic Hero (guaranteed)
  - 19× Random cards (60% Fire element, 40% mixed)
  - Rarity distribution: 1 Epic, 3 Rares, 8 Uncommons, 8 Commons
- **Variance**: High (each player gets different deck)
- **Synergy**: Not guaranteed (requires deckbuilding skill)
- **Recommended For**: Experienced players, replayability

**Element Deck #5: Water Element Deck** (Random Water Cards)
- Same structure as Fire Element Deck, but Water pool
- **Epic Hero**: Random Water Epic (Tidal Guardian, Sea Witch, Frost King, etc.)

**Element Deck #6: Earth Element Deck** (Random Earth Cards)
- Same structure as Fire Element Deck, but Earth pool
- **Epic Hero**: Random Earth Epic (Stone Sentinel, Forest Lord, Terra Golem, etc.)

---

**Selection Flow**:
1. Player hovers over deck → Preview popup shows 5 sample cards
2. Player clicks "SELECT" → Confirmation dialog:
   ```
   "Start your journey with the [Flame Warlord Deck]?
   This choice is permanent and cannot be changed.
   
   [CONFIRM] [BACK]"
   ```
3. Player confirms → Deck is granted (20 cards instantly added to Codex)
4. **Reveal Animation**: Cards flip one-by-one (same animation as old pack opening)
   - Epic Hero revealed FIRST (3 sec dramatic reveal, screen shake)
   - Remaining 19 cards revealed in batches of 5 (1 sec each)
   - Total time: 3 sec (Epic) + 19 sec (others) = **22 seconds**
   - **Skippable after Epic** (button appears after hero reveal)

**Fallback Logic** (Gap 2 Resolution):
- Not needed (all Trainer Decks are pre-validated to build Balanced Explorer deck)
- Each deck includes minimum: 1 Hero, 6 Units, 2 Buildings, 2 Tactics

**Bonus Element Booster** (Immediate - Reinforces Choice):
After Trainer Deck reveal animation completes:
```
[Screen: Welcome Bonus]
"Welcome to the [Fire/Water/Earth] path! Here's an Element Booster to strengthen your deck."
[1 glowing pack appears - colored to match element (red/blue/green)]
[Auto-opens after 2 seconds - no skip option]
```

**Element Booster Contents** (5 cards):
- **Guaranteed**: 80%+ cards match Trainer Deck element
- **Fire Booster** (if Fire Trainer Deck):
  - 4× Fire cards (mix of Common/Uncommon/Rare)
  - 1× Random card (any element, for variety)
- **Water/Earth Boosters**: Same structure (4 element + 1 random)

**Rarity Distribution**:
- 2× Common (60% element match)
- 2× Uncommon (90% element match)  
- 1× Rare (100% element match, reinforces synergy)

**Why Immediate Element Booster?**:
- ✅ **Pokemon Store Experience**: Buy Battle Deck → Get matching booster
- ✅ **Synergy Reinforcement**: Fire player gets more Fire cards (25 total Fire-themed)
- ✅ **Immediate Collection Growth**: 20 → 25 cards in 30 seconds
- ✅ **Element Identity**: Reinforces "I'm a Fire player" commitment
- ✅ **Not Overwhelming**: 5 cards only (not 20 random like old design)

**Total Starting Cards**: 20 (Trainer Deck) + 5 (Element Booster) = **25 cards**

**Player Experience**:
- **Fast path**: 22 sec (Trainer reveal) + 15 sec (Element Booster) = **37 seconds total**
- **Element commitment**: Choosing Fire Deck locks you into Fire playstyle + gets Fire booster
- **Replayability**: 6 starting options × different Element Booster contents

**Design Decisions** (Resolved):
- ✅ Starter system: Trainer Deck (20 curated cards) instead of random packs
- ✅ Deck options: 6 total (3 Curated named Epics + 3 Random Element decks)
- ✅ Elements: Fire, Water, Earth (Wind/Dark/Light expansion later)
- ✅ Epic reveal speed: 3 sec dramatic reveal with screen shake + fanfare
- ✅ Card reveal speed: 1 sec/card for non-Epics (19 cards = 19 sec)
- ✅ **Element Booster**: 1 pack (5 cards, 80% element match) after Trainer Deck reveal
- ✅ Skip behavior: Can skip after Epic reveal (22 sec mandatory, rest skippable)
- ✅ Permanence: Trainer Deck choice is permanent (encourages alt accounts)
- ✅ Sound design: Unique chime per rarity (Common=ping, Uncommon=chime, Rare=bell, Epic=orchestra hit)
- ✅ Legendary near-miss: Not in starter packs (too confusing for tutorial)

---

### Step 7: Collection Overview
**Screen**: Your Starting Collection
```
[Header: "Your Starting Collection - 25 Cards"]
[Grid view: All 25 cards displayed (5 rows × 5 columns)]
[Sorting: Rarity (Epic → Common), then alphabetical]

[Highlighted: Epic Flame Warlord/Tidal Guardian/Stone Sentinel] (gold pulsing border)
[Text: "Your first Epic hero! Let's build a deck around it."]

[Button: "Build My Deck"] (large, center, pulsing)
```

**Player Action**: Taps "Build My Deck"

**System Actions**:
1. Add all 25 cards to Codex (20 Trainer + 5 Element Booster)
2. Mark all cards as "New!" (gold badge indicator)
3. Validate Balanced Explorer deck is buildable from pool
4. If missing cards for deck: Silent auto-grant (see Fallback Logic in Step 6)
5. Load deck builder scene

**Design Decisions** (Resolved):
- ✅ Grid view default (shows card art for visual appeal)
- ✅ Filter/Sort controls hidden until tutorial complete (reduce cognitive load)
- ✅ Tap card for details: Shows modal popup with full stats (Attack, Defense, HP, Ability text)
- ✅ **Total starting cards: 25** (20 Trainer Deck + 5 Element Booster)

---

## Phase 3: Deck Building (5-8 Minutes)

### Step 8: Deck Builder - Choice Point
**Screen**: Choose Your Path
```
[Header: "Build Your First Deck"]
[Subheader: "Choose how you'd like to start"]

[Left Card: "Build For Me"]
  - [Icon: Automated wand]
  - [Text: "Recommended for new players"]
  - [Badge: "+5 Bonus Cards"]
  
[Right Card: "I'll Build My Own"]
  - [Icon: Manual tools]
  - [Text: "For card game veterans"]
  - [Badge: "Full Control"]

[Bottom text: "Don't worry - you can change your deck anytime!"]
```

**Player Action**: Taps "Build For Me" (guided path)

**Design Decisions Needed**:
- [ ] Badge clarity ("+5 Bonus Cards" = bonus pack, make that clear?)
- [ ] Can switch paths mid-tutorial? (lock in choice or allow back button?)
- [ ] Analytics tracking (% of players choosing each path)

---

### Step 9: Guided Path - Choose Your Playstyle
**Screen**: Select Your Starter Deck
```
[Header: "Choose Your Playstyle"]

[Three Large Cards - Horizontal Carousel]:

[Card 1: AGGRO RUSH]
  [Image: Fire Warrior hero portrait]
  [Element Icons: Fire 🔥 Lightning ⚡]
  [Text: "Fast & Aggressive"]
  [Stats Preview: "10 cards, High Attack, Low Defense"]
  [Button: "View Details"]
  
[Card 2: DEFENSIVE BUILDER] (Selected - blue border)
  [Image: Stone Golem hero portrait]
  [Element Icons: Earth 🌍 Frost ❄️]
  [Text: "Slow & Steady"]
  [Stats Preview: "12 cards, High Defense, Economy Focus"]
  [Button: "View Details"]
  
[Card 3: BALANCED EXPLORER]
  [Image: Water Mage hero portrait]
  [Element Icons: Water 💧 Wind 🌪️]
  [Text: "Versatile & Adaptive"]
  [Stats Preview: "11 cards, Balanced, Learn All Mechanics"]
  [Button: "View Details"]

[Bottom Button: "Choose Balanced Explorer"] (confirms selection)
```

**Player Action**: 
1. Swipes through carousel (sees all 3 options)
2. Taps "View Details" on Balanced Explorer
3. Sees full deck list modal (11 cards with icons)
4. Taps "Choose Balanced Explorer"

**System Actions**:
1. Analyze player's 20-card pool
2. Auto-select 11 best-matching cards for Balanced Explorer theme:
   - 1× Epic Water Mage (guaranteed from initial draw)
   - 2× Uncommon Knights (if player has them, else substitute similar units)
   - 2× Uncommon Archers (if available)
   - 2× Common Scouts
   - 1× Rare Healer (if available, else give free copy)
   - 1× Uncommon Granary (building)
   - 1× Uncommon Watchtower (building)
   - 1× Rare Tactic: "Adaptive Strategy"
3. **Fallback Logic** (if player's pool doesn't match):
   - Missing cards are given for FREE (one-time gift)
   - Player notified: "We've added 3 cards to complete your deck!"
4. Remaining 9 cards go to Codex inactive storage

**Design Decisions Needed**:
- [ ] "View Details" modal design (show full deck list, card art, stats?)
- [ ] Fallback gifts (give free cards or auto-adjust deck composition?)
- [ ] Can player go back and choose different deck? (allow back navigation)

**Gap**: Need fallback logic for card pool mismatches (what if player didn't draw a Healer?)

---

### Step 10: Deck Confirmation
**Screen**: Your Deck is Ready!
```
[Header: "Your Balanced Explorer Deck"]
[Deck visual: 11 cards displayed in formation preview]

[Center: Epic Water Mage (large)]
[Surrounding: 10 other cards (smaller icons)]

[Stats Summary]:
- Total Attack: 85
- Total Defense: 120
- Total HP: 450
- Deck Size: 11/15 cards (can add 4 more later)

[Button: "This Looks Great!"]
```

**Player Action**: Taps "This Looks Great!"

**System Actions**:
1. Finalize deck composition
2. Set as active deck in Deck Slot 1
3. Award bonus pack (5 cards) for choosing guided path

---

### Step 11: Bonus Pack Reward
**Screen**: Bonus Pack Opening
```
[Header: "Bonus Pack!"]
[Text: "For starting with a guide, here are 5 bonus cards!"]

[Pack Opening Animation - Same as Step 6 but faster]
- 5 cards revealed (1 per second)
- Guaranteed 1 Rare minimum
- Cards added to Codex (not auto-added to deck)

[Text: "These cards are in your Codex - you can swap them into your deck anytime!"]
[Button: "Got It!"]
```

**Player Action**: Taps "Got It!"

**Design Decisions Needed**:
- [ ] Bonus pack timing (before or after first battle?)
- [ ] Rarity distribution (same as standard pack or better odds?)

---

## Phase 4: Campaign Mode Introduction (8-10 Minutes)

### Step 12: Campaign World Select
**Screen**: Campaign Mode - World 1 Selection
```
[Camera: Campaign world selection screen]
[Background: Stylized map of 8 worlds in a branching path]

[Header: "Campaign Mode - Begin Your Journey"]

[World 1: Goblin Plains] - UNLOCKED (glowing green)
  - Icon: Goblin face on green grasslands
  - Progress: 0/9 stages completed
  - [TAP TO START] button (pulsing)

[Worlds 2-8: LOCKED] (grayed out, padlock icons)
  - World 2: Bandit Forests (requires World 1 completion)
  - World 3: Orc Wastelands
  - World 4: Undead Crypts
  - World 5: Dragon Peaks
  - World 6: Demon Wastes
  - World 7: Celestial Realm
  - World 8: Void Dimension

[Tutorial Overlay]:
"Complete stages to unlock new worlds and face epic bosses!"
[Arrow pointing to World 1]

[Button: "Next"] (advances tutorial)
```

**Player Action**: Taps "Next"

**Tutorial Steps** (Sequential overlays):
1. "This is your army" (highlights player stack)
2. "These are enemy spawns" (highlights goblin camp, 2 tiles away)
3. **"You have 10 Movement Points per day"** (highlights Movement Points HUD)
   - Tooltip: "Each move costs 1 Movement Point. You can move 3 tiles per turn."
4. "Tap your army to select it" (waits for player to tap)

**System Actions**:
1. Load Realm Map (Tutorial_Map_01)
2. Place player army on Start tile
3. Place 1 enemy spawn 2 tiles away
4. Initialize HUD: Movement Points (10/10), Energy (100/100), Resources (0/0/0)
5. Disable all other interactions until tutorial completes

**Movement Point System Introduction**:
- **Movement Points**: 10/day (resets midnight UTC)
- **Movement Range**: 3 tiles per turn (1 Movement Point = move up to 3 tiles)
- **Enemy is 2 tiles away**: Player will reach enemy in 1 turn (costs 1 Movement Point, 9 remaining)
- **Visual**: After first move, HUD updates to "9/10 Movement Points"

**Design Decisions Needed**:
- [ ] Camera zoom level (show 5×5 tiles? 7×7? whole map?)
- [ ] Fog of war style (black fog? semi-transparent? animated swirl?)
- [ ] Army icon representation (hero portrait or generic army icon?)

---

### Step 13: Stage 1-1 - First Campaign Battle
**Screen**: Stage Select - World 1
```
[Header: "World 1: Goblin Plains - Stage Select"]

[9 stage icons in horizontal row]:
  Stage 1-1: UNLOCKED (green glow, "START" button)
    - Enemy: Goblin Raiders (3-card deck)
    - Rewards: 100 Gold, 1 Common card
    - First Time Bonus: Tutorial stage (0 Energy)
  
  Stages 1-2 to 1-9: LOCKED (grayed out, padlock icons)
    - "Complete Stage 1-1 to unlock"

[Tutorial Text]:
"Your first battle! Defeat the Goblin Raiders to progress."
[Arrow pointing to Stage 1-1 START button]

[Player taps START]

[Battle Confirmation]:
"Stage 1-1: Goblin Raiders"
  - Enemy Power: 50 (3 Common cards)
  - Your Power: 120 (11 cards from Tutorial Deck)
  - Energy Cost: 0 (Tutorial battle, free)
  - Buttons: [Begin Battle!] [Cancel]
```

**Player Action**: Taps "Begin Battle!" (0 Energy for tutorial)

**Transition**: Fade to black → Camera zooms from World Map into Battle Map (3-second cinematic)

**Design Decisions Needed**:
- [ ] World map visual style (branching path? linear row? illustrated map?)
- [ ] Stage icon design (numbered circles? thematic icons?)
- [ ] Lock/unlock animation (fade in? slide in? sparkle effect?)
- [ ] Stage completion indicator (stars below icon? checkmark overlay?)

---

### Step 14: Battle Transition
**Screen**: Battle Start Cinematic
```
[Animation: Camera zooms from Campaign World Map into Battle Map]
[Effect: Screen flash, particle burst]
[Sound: Battle horn]

[Text appears: "BATTLE!"]
[Screen transitions to tactical grid]
```

**Duration**: 1-2 seconds

**Design Decisions Needed**:
- [ ] Transition style (fade, zoom, shatter?)
- [ ] Skippable? (allow skip after first battle)

---

## Phase 5: First Tactical Battle (10-15 Minutes) - CORE LOOP

### Step 15: Deck Builder - Select 6 Cards for Battle
**Screen**: Battle Formation - Deck Builder
```
[Header: "Select 6 Cards for Battle"]

[Your Collection: 20 cards total]
(Cards auto-sorted by star rank, then rarity)

[Available Cards]:
  ✅ Epic Water Mage (1★) - [AUTO-SELECTED, Slot 1] (Hero, 80 HP, 40 ATK)
    → Border: Bronze, 1 Tactic Slot
  ✅ Uncommon Knight (1★) - [AUTO-SELECTED, Slot 2] (20 HP, 10 ATK)
    → Border: Bronze, 1 Tactic Slot
  ✅ Uncommon Knight (1★) - [AUTO-SELECTED, Slot 3] (20 HP, 10 ATK)
    → Border: Bronze, 1 Tactic Slot
  ✅ Common Archer (1★) - [AUTO-SELECTED, Slot 4] (10 HP, 5 ATK)
    → Border: Bronze, 1 Tactic Slot
  ✅ Common Scout (1★) - [AUTO-SELECTED, Slot 5] (10 HP, 5 ATK)
    → Border: Bronze, 1 Tactic Slot
  ✅ Common Healer (1★) - [AUTO-SELECTED, Slot 6] (10 HP, 5 ATK)
    → Border: Bronze, 1 Tactic Slot
  ⬜ Common Knight (1★) × 3 copies - Not selected (tutorial uses Uncommon Knights)
  ⬜ Common Archer (1★) × 4 copies - Not selected (have 1 Archer already)
  ⬜ Common Scout (1★) × 4 copies - Not selected (have 1 Scout already)
  ⬜ Common Healer (1★) × 3 copies - Not selected (have 1 Healer already)
  ⬜ Building (Granary) - [GRAYED OUT] "Can't use in battles"
  ⬜ Building (Watchtower) - [GRAYED OUT] "Realm Map only (Phase 2)"

[Tutorial Text]:
"We've selected your 6 strongest cards automatically."
"You'll get more choices as you collect cards and rank them up!"

[Button: "Next - Attach Tactics"] (advances to tactic assignment)
```

**Player Action**: Taps "Next - Attach Tactics"

**System Actions**:
1. Lock 6-card selection (tutorial auto-picks)
2. Transition to Tactic Assignment screen
3. Show tactic attachment tutorial

**Design Decisions**:
- ✅ Tutorial auto-selects 6 cards (player can customize post-tutorial)
- ✅ Grayed out cards show why unusable ("Economy cards can't battle")
- ✅ Collection shows star count (★) and border color even at 1★
- ✅ Future: Manual selection screen (drag cards to 6 slots, swap tactics between battles)

---

### Step 15A: Tactic Assignment
**Screen**: Attach Tactics to Cards
```
[Header: "Attach Tactics to Power Up Your Cards!"]

[6 Selected Cards with Tactic Slots]:

[Slot 1]: Epic Water Mage (1★)
  [Tactic Slot 1]: [Empty] ← Tutorial highlights
  Available Tactics: Arcane Focus (Common), Regeneration (Rare), Time Warp (Epic)

[Slot 2]: Uncommon Knight (1★)
  [Tactic Slot 1]: [Empty]
  
[Slot 3]: Uncommon Knight (1★)
  [Tactic Slot 1]: [Empty]

[Slot 4]: Common Archer (1★)
  [Tactic Slot 1]: [Empty]

[Slot 5]: Common Scout (1★)
  [Tactic Slot 1]: [Empty]

[Slot 6]: Common Healer (1★)
  [Tactic Slot 1]: [Empty]

[Tutorial Text]:
"Drag 'Charge' tactic to your Knight!"
[Arrow pointing to Slot 2 + Charge tactic card]

[Tutorial Tactics Available]:
  - Charge (Common): "Attack twice on first turn"
  - Guardian (Common): "+20% HP, protect adjacent allies"
  - Volley (Common): "Attack 3 enemies at once"
  - Defensive Ward (Uncommon): "+50% damage reduction"

[Tutorial Forces Assignment]:
  Slot 1: Water Mage → (No tactic for tutorial - hero is strong enough)
  Slot 2: Knight → Charge (player drags this one)
  Slot 3: Knight → Guardian (tutorial auto-assigns after player does Slot 2)
  Slot 4: Archer → Volley (auto-assigned)
  Slot 5: Scout → (Empty - tutorial shows empty slot is OK)
  Slot 6: Healer → Defensive Ward (auto-assigned)
```

**Player Action**: Drags "Charge" tactic to Knight (Slot 2)

**Visual Feedback**:
- Tactic card lifts, follows cursor
- Slot 2 highlights green when tactic hovers over it
- Tactic snaps into slot with click sound
- Tactic icon appears in slot (sword icon for Charge)

**System Actions**:
1. Tutorial auto-assigns remaining tactics (Guardian, Volley, Defensive Ward)
2. Show preview: "Knight + Charge = 2× attack on Turn 1!"
3. Advance to battle grid

**Tutorial Text**:
"Tactics don't use slots - they attach to cards!"
"At 2★, you'll unlock a 2nd tactic slot per card!"
"Build your way to 6★ for 6 tactics on one card!"

**Design Decisions**:
- ✅ Tutorial teaches 1 tactic manually, auto-assigns rest (avoid tedium)
- ✅ Shows empty slot is OK (Scout has no tactic, still usable)
- ✅ Preview window shows tactic effect ("2× attack first turn")
- ✅ Tactic icons color-coded: Common=gray, Uncommon=green, Rare=blue, Epic=purple

---

### Step 16: Battle Grid - Preset Formation
**Screen**: Tactical Battle Map (8×8 Grid)
```
[Top: Enemy Side - 3 rows]
Row 1 (Enemy back):  [  ][  ][  ][Goblin Archer][  ][Goblin Archer][  ][  ]
Row 2 (Enemy mid):   [  ][  ][  ][  ][  ][  ][  ][  ]
Row 3 (Enemy front): [  ][Goblin Warrior][  ][Goblin Chief][  ][Goblin Warrior][  ][  ]

Row 4 (No Man's Land): [  ][  ][  ][  ][  ][  ][  ][  ]

Row 5 (Player front): [  ][  ][Knight #2][Water Mage][Knight #1][  ][  ][  ]
Row 6 (Player mid):   [  ][  ][Archer][Healer][Scout][  ][  ][  ]
Row 7 (Player back):  [  ][  ][  ][  ][  ][  ][  ][  ]
Row 8 (Player back):  [  ][  ][  ][  ][  ][  ][  ][  ]

[Unit Details Shown on Cards]:
  Water Mage (1★): 80 HP, 40 ATK, no tactics
  Knight #1 (1★) + Charge: 20 HP, 10 ATK, [⚔️ Charge icon]
  Knight #2 (1★) + Guardian: 24 HP (20 base +20%), 10 ATK, [🛡️ Guardian icon]
  Archer (1★) + Volley: 10 HP, 5 ATK, [🎯 Volley icon]
  Healer (1★) + Defensive Ward: 15 HP (10 base +50%), 5 ATK, [🔰 Ward icon]
  Scout (1★): 10 HP, 5 ATK, no tactics

[Tutorial Overlay]:
"Your units are ready! Knight has Charge - he'll attack twice this turn!"
[Arrow pointing to Knight #1]

[Button: "Start Battle"]
```

**Player Action**: Taps "Start Battle"

**System Actions**:
1. Preset formation spawns (no manual placement for tutorial)
2. Tactic effects activate (Guardian +20% HP applied to Knight #2)
3. Turn 1 begins (player's turn)

**Design Decisions**:
- ✅ Tutorial uses preset formation (skip manual placement complexity)
- ✅ Post-tutorial: Player can choose formation in advanced mode (future)
- ✅ Cards show tactic icons on battlefield (visual reminder)
- ✅ HP bars show tactic boosts (+4 HP green text for Guardian Knight)

---

### Step 17: Turn 1 - Charge Tactic Demo
**Screen**: Your Turn - Movement Phase
```
[Battle Grid: All units placed]
[Your Water Mage: Glowing blue border (selected)]
[Movement Range: 2-3 tiles forward highlighted green]

[Tutorial Overlay]:
"Tap Water Mage, then tap where to move!"
[Arrow: Water Mage → Forward tile]
```

**Player Action**: 
1. Taps Water Mage (select)
2. Taps forward tile (2 spaces ahead)
3. Water Mage moves forward

**Visual Feedback**:
- Movement animation (0.5 seconds, smooth slide)
- Unit stats appear above card (HP: 50/50, ATK: 15, DEF: 10)

**System Actions**:
1. Calculate movement cost (2 tiles = 2 movement points, Water Mage has 3 movement)
2. Update Water Mage position
3. Check for adjacent enemies (none yet)
4. Advance tutorial

**Design Decisions Needed**:
- [ ] Movement path preview (show dotted line before confirming?)
- [ ] Movement speed (instant, 0.3 sec, 0.5 sec, 1 sec?)
- [ ] Stat display timing (always visible or on-hover?)

---

### Step 18: Turn 1 - Attack Tutorial
**Screen**: Your Turn - Attack Phase
```
[Water Mage: Now in attack range of Goblin Warrior]
[Goblin Warrior: Red highlight (attackable)]

[Tutorial Overlay]:
"Tap the Goblin to attack!"
[Arrow: Water Mage → Goblin Warrior]
```

**Player Action**: Taps Goblin Warrior

**Combat Resolution**:
```
[Animation: Water Mage casts water blast]
[VFX: Blue wave hits Goblin]
[Damage numbers: "-15" (red) appear above Goblin]
[Goblin HP bar: 20/20 → 5/20]

[Sound: Water splash, Goblin grunt]
```

**System Actions**:
1. Calculate damage: Water Mage ATK (15) - Goblin DEF (0) = 15 damage
2. Apply damage to Goblin HP (20 → 5)
3. Check if Goblin dies (no, 5 HP remaining)
4. Water Mage's turn ends (action spent)

**Tutorial Text**: "Great hit! The Goblin is weakened!"

**Design Decisions Needed**:
- [ ] Damage formula visibility (show calculation tooltip?)
- [ ] Attack animation length (0.5 sec, 1 sec, 2 sec?)
- [ ] Overkill animation (if attack kills unit, does it disintegrate immediately?)

---

### Step 19: Turn 1 - End Turn
**Screen**: End Turn Phase
```
[Tutorial Overlay]:
"You've moved and attacked! Click 'End Turn' to finish."

[Bottom-right: "End Turn" button pulsing]
```

**Player Action**: Taps "End Turn"

**System Actions**:
1. Lock player units (no more actions)
2. Trigger enemy turn
3. Hide tutorial overlay (enemy turn is auto-played)

---

### Step 20: Turn 1 - Enemy Turn (Auto-Play)
**Screen**: Enemy Turn
```
[Top banner: "Enemy Turn"]
[All enemy units glow red briefly]

[Enemy AI Actions - Animated]:
1. Goblin Warrior (damaged) moves BACK 1 tile (AI retreats low HP units)
2. Goblin Chief moves forward 2 tiles
3. Goblin Chief attacks Knight (Knight: 30 HP → 22 HP)
4. Goblin Archer shoots at Water Mage (Water Mage: 50 HP → 43 HP)

[Each action: 1-second animation at 1× speed]
[Total enemy turn: 4-5 seconds at 1× speed]

[Text: "Enemy Turn Complete"]
[Auto-advances to Player Turn 2]
```

**Battle Speed Settings** (Gap 5 Resolution):
- **Tutorial**: Locked to **1× Normal speed** (forces player to learn animations)
- **Post-Tutorial Unlock**: Settings menu adds Battle Speed options
  - 1× Normal: 1.0 sec movement, 1.5 sec attack, 1.0 sec death
  - 2× Fast: 0.5 sec movement, 0.75 sec attack, 0.5 sec death
  - 4× Very Fast: 0.25 sec movement, 0.4 sec attack, 0.25 sec death
  - Instant: 0 sec animations (units teleport, damage instant, but show numbers 1 sec)

**Settings Menu** (unlocks Step 28):
```
[Battle Speed]:
◉ 1× Normal (default)
○ 2× Fast
○ 4× Very Fast
○ Instant (no animations)

Note: PvP battles always use 1× speed (fair for both players)
```

**Design Decisions** (Resolved):
- ✅ Enemy turn speed: 1× forced for tutorial, player choice post-tutorial
- ✅ Skip enemy turn: Not in tutorial (need to see what happened), available post-tutorial
- ✅ Enemy AI "thinking": No animation (instant decision, just execute actions)

---

### Step 21: Turn 2 - Finishing Move
**Screen**: Your Turn - Turn 2
```
[Tutorial Overlay]:
"Use your Archer to finish the wounded Goblin!"
[Highlight: Archer card + Wounded Goblin (5 HP)]
```

**Player Action**:
1. Taps Archer
2. Taps wounded Goblin Warrior
3. Archer shoots (arrow animation)
4. Goblin takes 12 damage (5 HP → 0 HP, DIES)

**Death Animation**:
- Goblin card shatters (glass effect)
- Disappears from board
- "DEFEATED" text floats up
- +10 XP floats to player XP bar

**Tutorial Text**: "Excellent! One enemy down!"

**Design Decisions Needed**:
- [ ] Death animation style (shatter, fade, dissolve, burn?)
- [ ] XP gain visibility (show immediately or in end-of-battle summary?)
- [ ] Loot drops (do units drop gold/items immediately or only at battle end?)

---

### Step 22: Turns 3-5 - Tutorial Stops Micromanaging
**Screen**: Free Play (Tutorial watches, doesn't interrupt)
```
[Tutorial Overlay (top-right corner, minimized)]:
"Keep fighting! You're doing great!"

[Player has full control]:
- Move any unit
- Attack any enemy
- Use tactic cards (if any)
- End turn when ready

[Enemy continues auto-playing on their turns]
```

**Battle Progression**:
- Turn 3: Player kills another Goblin, enemy retreats wounded units
- Turn 4: Player's Knights engage Goblin Chief (high HP tank)
- Turn 5: Final Goblin dies, battle ends

**Victory Condition**: All 6 enemy units defeated

**Tutorial Safety Nets** (Gap 9 Resolution - Tutorial Failure Recovery):
This battle is designed to be **unlosable** (player has 11 cards, enemy has 6 weak cards), but handle edge cases:

1. **If player loses** (impossible but handle it):
   - Defeat screen: "Defeat... but every hero stumbles once."
   - Button: "Try Again (Free Resurrection)"
   - If tapped: All units restored to full HP, battle restarts from placement phase
   - Tutorial text: "Let's adjust your formation!"

2. **If player force-quits mid-battle**:
   - On relaunch: "Welcome back! Your battle is still in progress."
   - Buttons: [Resume Battle] [Retreat to Realm Map]
   - Retreat: No penalties (units restored, no XP loss, can retry later)

3. **If player loses 3 times** (extremely unlikely, indicates bug):
   - After 3rd defeat: "This battle seems tough. Let's skip it for now."
   - Auto-Win: Player granted victory rewards (XP, gold, cards)
   - Tutorial advances to next step
   - Analytics flag: `Tutorial_AutoWin_Triggered` (developer notification)

**Free Retries**: First 3 battles allow unlimited free resurrections (no death penalty, no resource cost)

---

### Step 23: Victory Screen, Battle Chest & Pack Reward
**Screen**: Victory!
```
[Background: Animated victory fanfare, golden particles]
[Large text: "VICTORY!" (3-second animation, skippable after 1 sec)]
[Fireworks VFX: 2-second burst]

[Bronze Chest appears: Small bronze chest model, glowing]
[Text: "Battle Chest Earned! Tap to open."]
[Button: "Open Chest"] (pulsing, cannot skip)
```

**Battle Chest Opening Animation** (NEW):
- Player taps "Open Chest"
- **Bronze Chest** (easy PvE battle tier):
  - Lid flips open with particle effects (1-second animation)
  - Contents reveal sequentially (3 seconds total):
    * 💰 +50 Gold (coin icon flies to HUD, "+50!" popup)
    * 📊 +100 XP (progress bar fills, "100/250 to Level 2")
    * 🌾 +20 Food (wheat icon flies to HUD, "+20!" popup)
    * 🎴 +1 Common Card (Footman flips, 10% drop chance, guaranteed for tutorial)

**Tooltip After Chest**:
```
"Bronze Chests drop from easy battles.
Harder battles drop Silver or Gold Chests with better rewards!"
```

**Energy System Introduction**:
```
[After chest opening, Energy tutorial appears]

📊 ENERGY SYSTEM UNLOCKED

"This battle cost 0 Energy (Tutorial Campaign is free!)"

"Post-tutorial battles cost 10 Energy each."
"You refill 1 Energy every 6 minutes (240 Energy/day)."
"Your max Energy: 100 (enough for 10 battles before waiting)"

[HUD shows: Energy meter 100/100 (yellow lightning icon)]

[Button: "Got it!"] (dismiss tutorial)
```

**Pack Reward** (After Energy Tutorial):
```
[Screen: Victory Bonus]

🎁 **BONUS: Standard Booster Pack Earned!**
[Glowing pack icon bounces in]
[Text: "You've earned your first pack for beating the tutorial battle! Tap to open."]
[Button: "Open Pack"] (pulsing, cannot skip)
```

**Pack Opening Animation**:
- Player taps "Open Pack"
- **Standard Pack** (5 cards, fully random - any element):
  - **Purpose**: Cross-element exposure (Fire player sees Water/Earth cards)
  - **Rarity**: 3 Common, 1 Uncommon, 1 Rare (standard distribution)
  - **Animation**: Same flip animation as Trainer Deck (1 sec/card = 5 sec total)
  - **Result**: 5 new cards auto-added to Codex

**After Pack Opening**:
```
[Screen returns to victory summary]

🏆 BATTLE REWARDS SUMMARY:
- Bronze Chest: 50 Gold, 100 XP, 20 Food, 1 Common card (Footman)
- Standard Pack: 5 random cards (Healer, Scout, Farm, Archer, Knight)

📊 Player Level: 1 (100/250 XP to Level 2)
💰 Gold: 4,550 (4,500 from tutorial + 50 from chest)
🌾 Food: 20 (first resource earned!)

🎴 Total Cards: 31 (25 from Trainer Deck + Element Booster + 1 from chest + 5 from pack)

[Optional Button: "View Codex"]
[Primary Button: "Continue"]

🏆 Achievement Unlocked: "First Victory" (toast notification, top-right)
```

**Player Action**: Taps "Continue" (most common) or "View Codex" (optional)

**Card Reward Destination** (Gap 6 Resolution):
- **Auto-add to Codex** (no interruption, no deck management mid-victory)
- **"New!" Badge**: Cards highlighted in Codex with gold border
- **No prompt**: Don't ask "Add to Deck?" (interrupts victory high)
- **Optional**: "View Codex" button lets player inspect immediately if curious
- **Replay**: Codex shows all acquired cards with timestamps

**Why Battle Chest + Pack Here?**:
- ✅ **Reward Variety**: Chest (instant Gold/XP/resources) + Pack (collector appeal)
- ✅ **Energy System Introduction**: Explain without blocking (tutorial = 0 cost)
- ✅ **Resource Introduction**: First Food earned (20 Food for future battles)
- ✅ **Pokemon Store Feel**: "I won, I get to open a pack!" (dopamine spike)
- ✅ **Cross-Element Exposure**: Fire player sees Water/Earth cards (variety)
- ✅ **Collection Growth**: 25 → 31 cards (6 new: 1 from chest, 5 from pack)

**Total Cards After Step 23**: 25 (starting) + 1 (chest) + 5 (pack) = **31 cards**

**NEW: Fusion Tutorial** (Triggered if duplicate earned):
```
[If chest/pack gave duplicate Knight]:

[Popup appears]:
"⭐ Card Fusion Unlocked! ⭐"

[Screen shows Fusion UI]:
Uncommon Knight (1★)
  Owned: 3 copies (2 from Trainer Deck + 1 from reward)
  Current Stats: 20 HP, 10 ATK
  Border: Bronze (1★)
  Tactic Slots: 1

[Fusion Button]: "Fuse to 2★"
  Cost: 1 duplicate + 1,000 Gold
  New Stats: 30 HP (+50%), 15 ATK (+50%)
  Border: Bronze→Silver
  Tactic Slots: 2 (unlocks 2nd slot!)

[Tutorial Text]:
"Combine duplicates to increase Star Rank!"
"Higher stars = better stats + more Tactic Slots!"

[Player taps "Fuse to 2★"]:
  - Animation: 2 Knight cards merge with golden light
  - Sound: Metallic clink, ascending chime
  - Result: Knight becomes 2★ (★★☆ display)
  - Border changes: Bronze → Silver (visual progression)
  - New Tactic Slot appears: [Empty Slot 2]

[Post-Fusion Screen]:
Uncommon Knight (2★)
  Stats: 30 HP, 15 ATK (+50% from 1★!)
  Border: Silver ★★☆
  Tactic Slots: 2 (can now attach 2 tactics!)
  
[Tutorial Text]:
"Your Knight is now 2★! Attach a 2nd tactic in the Deck Builder."
"Keep collecting Knights to unlock 3★, then 4★!"
"At 4★, Uncommons max out with 4 Tactic Slots!"

[Button: "Continue"]
```

**If No Duplicate Earned** (Chest/pack gave new cards only):
- Skip fusion tutorial (will trigger on first duplicate later)
- Show tooltip: "Collect duplicates to unlock Fusion!"

**Total Cards After Fusion**: 31 cards total, Knight now 2★ (consumes 1 duplicate)

**System Actions**:
1. Award Bronze Chest: 50 Gold, 100 XP, 20 Food, 1 Common card
2. Update HUD: Gold (4,500 → 4,550), XP (0 → 100/250), Food (0 → 20)
3. Introduce Energy system (tutorial popup, no cost yet)
4. Award pack: 1 Standard Pack → Auto-open (cannot skip)
5. Award 5 random cards → Add to Codex (mark as "New!")
6. Store badges: `PlayerPrefs.SetInt("Card_[id]_New", 1)` for each card
7. Unlock Auto-Battle feature (shown in next step)
8. Return to Realm Map

**Design Decisions** (Resolved):
- ✅ Victory fanfare duration: 3 seconds total, skippable after 1 second
- ✅ **Battle Chest tier: Bronze (easy PvE battles)**
- ✅ **First pack timing: After first battle victory (earned reward)**
- ✅ **Pack type: Standard Pack (5 random cards, cross-element exposure)**
- ✅ Card reward destination: Auto-add to Codex with "New!" badge (no prompt)
- ✅ Achievement notification: Toast notification (top-right, 3-second fade)
- ✅ **Energy introduction: After chest, before pack (teaches mechanic without blocking)**

---

## Phase 6: Post-Tutorial Loop (15-60 Minutes)

### Step 24: Realm Map - Auto-Battle Unlock
**Screen**: Realm Map - After First Battle
```
[Camera returns to Realm Map]
[Player army back on Start tile]
[Fog of War: Revealed 2 more tiles (nearby path + another enemy spawn)]

[HUD Update]:
- Movement Points: 9/10 (1 used for first battle turn)
- Energy: 100/100 (tutorial battles still free)
- Food: 20 (from battle chest)

[Tutorial Overlay]:
"Great job! You can now use Auto-Battle for faster fights."
[Auto-Battle toggle appears in army UI]

[New Enemy Spawn visible: Goblin Scout Camp (3 units)]
```

**Player Action**: Moves army to new spawn

**Choice Point**:
```
[Battle Start Screen]:
[Button: "Manual Battle"] (like before)
[Button: "Auto-Battle"] (NEW - uses pre-set formation + AI combat)
```

**Player Choice**: Taps "Auto-Battle" (trying new feature)

**Auto-Battle Flow**:
1. Cards auto-place using "Balanced Formation" preset
2. Battle auto-plays in 10 seconds (5-8 turns compressed)
3. Victory (guaranteed for tutorial spawns)
4. Rewards screen (same as manual)
5. Tutorial text: "That was fast! Auto-Battle is great for farming."

**Auto-Battle Loss Handling** (Gap 7 Resolution):
If Auto-Battle results in defeat (should not happen in tutorial, but handle it):

1. **Defeat Screen**:
   ```
   "Your army was defeated!"
   - Casualties: 3 units lost (visual shows cards)
   - XP penalty: -10 XP (minor setback)
   
   Auto-retry? (1 free retry)
   [Try Again (Auto)] [Fight Manually] [Retreat]
   ```

2. **First Loss**: Offer **1 free auto-retry** (system reruns battle, no penalty)
   - If retry wins: Continue normally
   - If retry loses: Force choice (Manual or Retreat)

3. **Second Loss**: Force manual battle or retreat
   - Manual: Player takes control, retry with manual placement
   - Retreat: Return to Realm Map, units restored, no casualties (safe escape)

4. **Retreat Mechanic**:
   - No unit loss (all cards returned to deck)
   - No XP penalty
   - Can re-challenge later
   - Tutorial text: "Sometimes retreating is the smart choice."

**Auto-Battle Settings** (unlocked Step 28):
- Speed: 5 sec (Instant) / 10 sec (Fast) / 15 sec (Normal with animations)
- Free Retries: 1 per battle (prevents frustration)
- Retreat: Always available (no trap battles)

**Design Decisions** (Resolved):
- ✅ Auto-Battle speed: 10 seconds default (shows key moments), instant option in settings
- ✅ Cancel mid-auto-battle: No (let battle finish, only 10 seconds)
- ✅ Auto-Battle loss: 1 free retry, then manual or retreat (AFK Arena lite model)

---

### Step 25: Campaign Progression - Stages 1-2 to 1-4
**Screen**: Stage Select - World 1

[Player progresses through Stages 1-2, 1-3, 1-4]
[Each stage unlocks the next upon completion]

**Stage Sequence**:
1. **Stage 1-2**: Goblin Ambush (4-card deck, 80 Power)
   - Rewards: 150 Gold, 50 XP, 1 Common card
   - Energy: 10 Energy deducted (100 → 90)
   - Auto-Battle option now available

2. **Stage 1-3**: Goblin Camp (5-card deck, 120 Power, Uncommon hero)
   - Rewards: 200 Gold, 75 XP, 1 Uncommon card
   - Energy: 10 Energy deducted (90 → 80)

3. **Stage 1-4**: Goblin Fortress (6-card deck, 160 Power, Uncommon hero)
   - Rewards: 250 Gold, 100 XP, 1 Uncommon card
   - Energy: 10 Energy deducted (80 → 70)
   - Unlocks Stage 1-5 (mini-boss)

**Rewards Accumulation**:
- Total XP: 500-700 (reach Level 2)
- Total Gold: 1,200-1,500 (from Stages 1-1 to 1-4)
- Total Cards: 4-6 new cards (mix of Commons/Uncommons)

**Design Decisions Needed**:
- [ ] Tutorial pacing (how many stages before Codex tutorial?)
- [ ] Enemy difficulty curve (gradual increase in deck size + hero rarity)
- [ ] Energy refill prompts (when to suggest first Energy purchase?)

---

### Step 26: Codex Introduction
**Screen**: Codex Tutorial
```
[Trigger: After 3 battles, tutorial prompts]:
"You've collected 8 new cards! Check your Codex to manage them."

[Codex UI]:
- Left panel: Filters (Rarity, Element, Type)
- Center: Grid view of all owned cards (25 total)
- Right panel: Selected card details
- Bottom: "Add to Deck" button

[Tutorial Overlay]:
"This is your Codex - your card collection!"
[Highlights new cards with "NEW" badge]

"Tap a card to see details"
"Add cards to your deck (15-20 max at Level 2)"
```

**Player Actions**:
1. Taps new Uncommon Archer card
2. Sees stats, abilities, rarity
3. Taps "Add to Deck"
4. Deck updates (11 → 12 cards)

**Design Decisions Needed**:
- [ ] Codex tutorial timing (after 3 battles or after Level 2?)
- [ ] Filter tutorial (teach immediately or unlock later?)
- [ ] Duplicate card indicators (show "x3" badge?)

---

### Step 27: Stage 1-5 - First Mini-Boss Battle
**Screen**: Stage Select - World 1
```
[Stage 1-5: UNLOCKED] (Boss icon: Goblin Warchief portrait, red glow)

[Boss Preview Screen]:
"⚔️ MINI-BOSS: Goblin Warchief ⚔️"
Enemy: 7-card deck (Rare hero + 6 units)
Total Power: 200 (player has ~180, challenging but winnable)
Rewards: 500 Gold, 100 XP, 1 Rare card (guaranteed)
Energy Cost: 10 Energy

[Tutorial Text]:
"Mini-Boss ahead! These battles are harder but give better rewards!"
"Tip: Use your strongest cards and position them carefully."

[Buttons]:
  - Begin Battle (10 Energy)
  - View Enemy Deck (preview cards)
  - Return (go back to stage select)
```

**Phase 2 Note**: Treasure nodes (Gold/Gems on map tiles) are deferred to Phase 2 Realm Map. MVP uses stage rewards instead.

**Boss Battle Flow**:
1. Player battles Goblin Warchief (7-card deck, Rare hero)
2. Battle is harder than previous stages (requires strategy)
3. Victory awards bonus rewards

**Victory & Rewards**:
```
[Victory Screen]:
"⚔️ MINI-BOSS DEFEATED! ⚔️"

Rewards:
- +500 Gold
- +100 XP
- +1 Rare card (player choice from 3 options)

[Player Total After]:
- Gold: ~1,500 (from Stages 1-1 to 1-5)
- XP: Level 2 (425/600 XP toward Level 3)
- Cards: 31 (25 starting + 5 from Standard Pack + 1 from boss)

[Stage 1-6: UNLOCKED] (green glow, next stage available)

[Button: "Continue Campaign"]
```

**Why Mini-Bosses Replace Treasure Nodes?**:
- ✅ **Simpler MVP**: No map exploration, just stage progression
- ✅ **Active Engagement**: Boss battles are skill tests, not random loot
- ✅ **Paced Rewards**: Every 5th stage is a mini-boss (predictable, fair)
- ✅ **Rare Card Source**: Guaranteed Rare card every mini-boss (collector appeal)

**Total Cards After Step 27**: 25 (starting) + 5 (Standard Pack) + 1 (boss) = **31 cards**

---

### Step 28: Tutorial Complete - Freedom Unlocked - **MVP**
**Screen**: Tutorial Complete!
```
[Major Achievement Popup]:
"🎉 Tutorial Complete! 🎉"

Unlocked:
✅ Auto-Battle (fast combat, skip animations)
✅ Battle Speed Settings (1×/2×/4×/Instant)
✅ Codex (manage collection, deck builder)
✅ Campaign Mode (continue World 1, unlock Worlds 2-8)
✅ **Daily Challenge (bonus rewards, starts tomorrow)**
✅ **Pack Store (buy packs with Gold or Money)**
✅ **Battle Pass (optional $4.99/month, exclusive rewards)**

[Rewards]:
- 1,000 Gold bonus (Total: ~2,500 Gold)
- "Tutorial Graduate" title badge

[Button: "Continue Playing"]
```

**MVP Store Note**: Only Pack Store and Battle Pass are available in MVP. Resource Store (Food/Lumber/Ore), Arena Store (PvP Tokens), and Realm Map are deferred to Phase 2.

**Player Action**: Taps "Continue Playing"

**System Unlocks**:
1. **Full Campaign Mode**: 
   - World 1: Stages 1-6 to 1-9 now unlocked (complete to unlock World 2)
   - Stage 1-9: Goblin King (World Boss, 12-card deck, Epic/Legendary hero)
   - Worlds 2-8: Locked (requires World 1 completion)

2. **Pack Store** (MVP - Gold Only):
   ```
   [Pack Store Screen]
   
   AVAILABLE PACKS (Gold):
   - Standard Pack (5 cards): 1,000 Gold
     - 50% Common, 30% Uncommon, 15% Rare, 4% Epic, 1% Legendary
     - Average rarity: ~7 stars per pack (1.4 stars/card)
   
   - Element Booster (5 cards, 80% element match): 1,500 Gold
     - Same rarity distribution as Standard
     - 4/5 cards match chosen element (Fire/Water/Earth)
   
   [Your Gold: 4,300] [Your Gems: 110]
   [Note: "Gem purchases unlock at Player Level 5"]
   ```

**Why Simplified Store for MVP?**:
- ✅ **No Gem Purchases Yet**: Players must reach Level 5 before Gem Store unlocks (prevents impulse buying in first hour)
- ✅ **No Resource Store**: Food/Lumber/Ore economy is Phase 2 (not in MVP)
- ✅ **No PvP Store**: Arena Tokens are Phase 3 (not in MVP)
- ✅ **Gold Sinks**: Players can spend tutorial Gold on packs immediately (retention hook)

3. **Daily Login Rewards** (starts next login):
   - Day 1-6: +200 Gold/day
   - Day 7: +1,000 Gold + 1 Standard Pack
   - Day 14: +2,000 Gold + 1 Element Booster
   - Day 21: +3,000 Gold + 20 Gems
   - Day 28: +5,000 Gold + 1 Rare card (player choice from pool of 10)

4. **Settings Menu**: Audio, battle speed (1×/2×/4×/Instant), name change (100 Gold after first free change)

**Total Cards After Step 28**: 31 (no pack opening yet, players can buy packs with Gold)

---

**Total Gold After Tutorial**: ~2,500 Gold (2 Standard Packs OR 1 Element Booster OR save for Epic Booster)

**Shiny Chance in Tutorial Packs**: 
- 31 cards received × 1% shiny rate = **~0.31 average shinies** (27% chance of 1 shiny, 73% chance of 0)

---

## Summary: Tutorial Completion Checklist - **MVP**

**By end of 15-20 minute tutorial, player has**:
✅ Created account and chosen name  
✅ Chosen Trainer Deck (20 cards, 1 Epic guaranteed)  
✅ Received Element Booster #1 (5 cards, reinforce element synergy)  
✅ Built first deck (20 cards, element-themed)  
✅ Learned Campaign Mode progression  
✅ Fought first manual battle (card placement, movement, attack)  
✅ Won first battle + **earned Standard Pack** (5 cards, cross-element variety)  
✅ Unlocked Auto-Battle  
✅ Collected 1,500-2,500 Gold from battles  
✅ Reached Level 1-2 (100-250 XP)  
✅ Introduced to Codex (card management)  
✅ **Defeated mini-boss Stage 1-5 + earned 1 Rare card** (Step 27)  
✅ **Tutorial Complete: 1,000 Gold bonus**  
✅ **Daily Challenge unlocked** (starts tomorrow, 2× rewards)  

**Total Collection**: 31 cards (25 starting + 5 from Standard Pack + 1 from mini-boss)

**Player is now ready for**:
- Campaign Mode progression (Stages 1-6 to 1-9, unlock World 2)
- Pack Store purchases (Standard Pack $0.99/1,000 Gold, Battle Pass $4.99/month)
- Daily Challenge rewards (1 random stage/day, 2× rewards)
- Deck customization (swap cards in Codex)
- **Phase 2**: Realm Map (open-world hex grid, AFK economy, territory control)

---

## All Critical Gaps RESOLVED ✅

All 9 critical gaps have been integrated directly into the tutorial flow above. For detailed design rationale and implementation notes, see [tutorial-gap-resolutions.md](tutorial-gap-resolutions.md).

**Gap Resolution Summary**:
1. ✅ **EULA/Privacy** - Mandatory checkbox screen (Step 2B, App Store compliance)
2. ✅ **Card Pool Fallback** - 10 guaranteed cards + silent auto-grant (Step 6, no stuck players)
3. ✅ **Pack Skip** - First pack mandatory, rest skippable (Step 6, 21 sec vs 80 sec)
4. ✅ **Placement Undo** - Drag-to-reposition + Reset Formation button (Step 15, XCOM model)
5. ✅ **Battle Speed** - Settings for 1×/2×/4×/Instant (Step 20, unlocks Step 28)
6. ✅ **Card Rewards** - Auto-add to Codex with "New!" badge (Step 23, Hearthstone model)
7. ✅ **Auto-Battle Loss** - 1 free retry, then manual or retreat (Step 24, AFK Arena lite)
8. ✅ **Treasure Nodes** - MVP uses treasure nodes (one-time rewards) instead of economy deployment (Step 27, Phase 2 feature)
9. ✅ **Tutorial Failure** - Free resurrection ×3 + auto-win failsafe (Step 22, Pokemon model)

**All Design Decisions RESOLVED ✅**:
- ✅ Splash duration: 2-3 seconds (asset loading time)
- ✅ Default name: `Player_12345` (5-digit random)
- ✅ Name change: Free once at Level 3, then 100 gold
- ✅ Pack opening: 4 sec/card standard, 3 sec for Epic
- ✅ Pack skip: First pack mandatory (21 sec fast path)
- ✅ Codex view: Grid default (visual appeal)
- ✅ Movement speed: 1.0 sec at 1×, adjustable post-tutorial
- ✅ Attack length: 1.5 sec at 1×, adjustable post-tutorial
- ✅ Death animation: Shatter effect (0.5 sec at 1×)
- ✅ Victory fanfare: 3 sec total, skippable after 1 sec
- ✅ Auto-Battle speed: 10 sec default, instant option available
- ✅ Codex tutorial: After 3 battles (Step 26)
- ✅ Economy tutorial: Optional after first resource node (Step 27)

---

## Implementation-Ready Specifications

This document is now **QA-ready** and **developer-ready**:
- ✅ All UI screens defined (28 steps, minute-by-minute)
- ✅ All player actions specified (tap, drag, choice points)
- ✅ All system responses documented (validations, animations, rewards)
- ✅ All edge cases handled (failures, retries, cancellations)
- ✅ All animations timed (durations, speeds, skip behavior)

**For Unity Implementation**: See [mvp-scope.md](mvp-scope.md) for:
- Week-by-week build plan (8 weeks to MVP)
- Code examples (CardData, BattleManager, PackOpening)
- Scene structure (EULA → MainMenu → CardDraw → DeckBuilder → Battle)
- File organization (Scripts/, Prefabs/, Scenes/)

**For QA Testing**: Use this document as literal test script:
- Follow each step exactly (Step 1 → Step 28)
- Verify all UI elements appear as described
- Test all edge cases (skip, undo, retry, retreat)
- Confirm timings match specifications (pack opening, battle speed)
