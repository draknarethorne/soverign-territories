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
[Background: Animated county map with fog]
[Center: "Sovereign Territories" title logo]

[Large Button: "START YOUR JOURNEY"]
[Small Button: "Settings"]
[Small Button: "Quit"]
```

**Player Action**: Taps "START YOUR JOURNEY"

**Design Decisions Needed**:
- [ ] Background animation (subtle parallax? moving fog?)
- [ ] Audio: Menu music theme (orchestral? epic? calm?)

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

**Design Decisions Needed**:
- [ ] Default name format (Player_12345 vs Sovereign_12345 vs random adjective+noun)
- [ ] Can change name later? (Yes, recommend unlocking at Level 3)
- [ ] EULA/Privacy acceptance (required by law - add checkbox before buttons)
- [ ] Offline mode support (if no internet, show "Offline Mode Available" with limited features)

**Gap**: EULA/Privacy policy acceptance is legally required but not currently designed

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
**Screen**: Card Draw Intro
```
[Fade in: Mystical card vault opening]
[Narrator text: "Your journey begins with these cards..."]
[Animated: 5 glowing card packs floating]
[Button: "Open Packs"] (pulsing)
```

**Player Action**: Taps "Open Packs"

**Design Decisions Needed**:
- [ ] Narrator voice (text only or voice-over?)
- [ ] Cinematic skip (allow skip after 1 second? or force watch first time?)
- [ ] Music shift (calm → exciting as packs appear)

---

### Step 6: Pack Opening Animation (CRITICAL MOMENT)
**Screen**: Pack Opening
```
[Center: First pack (glowing gold)]
[Pack expands, tears open]
[4 cards flip one-by-one with sound effects]

Card 1: [Common Spearman] - quick reveal, white glow
Card 2: [Common Farm] - quick reveal, white glow
Card 3: [Uncommon Knight] - medium reveal, green shimmer
Card 4: [EPIC FIRE WARRIOR] - SLOW reveal, PURPLE PARTICLE BURST, screen shake

[Text: "EPIC! Fire Warrior!"]
[Sound: Epic fanfare]
```

**System Actions**:
1. Guaranteed 1 Epic in first 5 packs (player always gets Epic in pack 1-2 for excitement)
2. Total draws: 20 cards (5 packs × 4 cards each)
3. Distribution enforced:
   - 1 Epic (guaranteed in first 2 packs)
   - 5 Rare
   - 8-10 Uncommon
   - 6-8 Common
   - 3% Legendary chance (replaces 1 Rare if triggered)

**Pack Opening Flow**:
- Pack 1: 3 Common + 1 Epic (HOOK - early dopamine hit)
- Pack 2-4: Mix of Common/Uncommon/Rare (build anticipation)
- Pack 5: Guaranteed Rare minimum (finish strong)

**Player Experience**:
- Total time: 60-90 seconds (4-5 seconds per card × 20 cards)
- Skippable after Pack 1 (Button: "Skip to Results" appears)
- Can re-watch pack openings in Codex later (replay animation)

**Design Decisions Needed**:
- [ ] Pack opening speed (4 seconds per card = 80 seconds total, too long?)
- [ ] Skip behavior (instant reveal all or fast-forward animation?)
- [ ] Epic reveal choreography (screen shake intensity, particle duration)
- [ ] Sound design (unique chime per rarity, voice lines?)
- [ ] Legendary near-miss (show "gold glow" that fades to purple if 3% fails?)

**Gap**: Pack opening animation specifics need Unity VFX design

---

### Step 7: Collection Overview
**Screen**: Your Starting Collection
```
[Header: "Your Starting Collection - 20 Cards"]
[Grid view: All 20 cards displayed]
[Sorting: Rarity (Epic → Common), then alphabetical]

[Highlighted: Epic Fire Warrior] (pulsing border)
[Text: "Your first Epic hero! Let's build a deck around it."]

[Button: "Build My Deck"] (large, pulsing)
```

**Player Action**: Taps "Build My Deck"

**System Actions**:
1. Cache all 20 cards in Codex
2. Mark all as "new" (badge indicator)
3. Prepare deck builder UI

**Design Decisions Needed**:
- [ ] Grid vs List view (grid = see card art, list = see stats)
- [ ] Filter/Sort controls (unlock later or show grayed out?)
- [ ] Tap card for details (modal popup with full stats?)

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

## Phase 4: County Map Introduction (8-10 Minutes)

### Step 12: Map Camera Intro
**Screen**: County Map - Tutorial Start
```
[Camera: Zoomed out view of County Map]
[Background: Lush green terrain with fog of war covering 70% of map]

[Visible: Start tile (glowing green), 1 Path tile, 1 Enemy Spawn (red)]
[Fog: Everything else hidden]

[Tutorial Overlay]:
"This is the County Map - your army's battlefield!"
[Arrow pointing to Start tile]

[Your Army Icon: Epic Water Mage portrait + "11 units" badge]
[Enemy Spawn Icon: Goblin face + "6 units" badge]

[Button: "Next"] (advances tutorial)
```

**Player Action**: Taps "Next"

**Tutorial Steps** (Sequential overlays):
1. "This is your army" (highlights player stack)
2. "These are enemy spawns" (highlights goblin camp)
3. "Tap your army to select it" (waits for player to tap)

**System Actions**:
1. Load county map (Tutorial_Map_01)
2. Place player army on Start tile
3. Place 1 enemy spawn 2 tiles away
4. Disable all other interactions until tutorial completes

**Design Decisions Needed**:
- [ ] Camera zoom level (show 5×5 tiles? 7×7? whole map?)
- [ ] Fog of war style (black fog? semi-transparent? animated swirl?)
- [ ] Army icon representation (hero portrait or generic army icon?)

---

### Step 13: Movement Tutorial
**Screen**: Move Your Army
```
[Tutorial Overlay]:
"Tap the enemy camp to move and attack!"
[Arrow pointing from your army to goblin camp]
[Goblin camp pulsing red]

[Movement Range: Green highlight on 3 adjacent tiles]
[Enemy Tile: Red highlight (attack target)]
```

**Player Action**: 
1. Taps goblin camp tile
2. Army moves (1-second walk animation)
3. Army reaches goblin camp

**System Actions**:
1. Calculate movement path (2 tiles)
2. Play walk animation (army sprite moves along path)
3. Trigger battle transition

**Design Decisions Needed**:
- [ ] Movement animation speed (instant, 0.5 sec/tile, 1 sec/tile?)
- [ ] Movement path visual (dotted line preview before confirming?)
- [ ] Can cancel movement mid-animation? (tap elsewhere to stop?)

**Gap**: Movement animation style needs Unity animator setup

---

### Step 14: Battle Transition
**Screen**: Battle Start Cinematic
```
[Animation: Camera zooms from County Map into Battle Map]
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

### Step 15: Battle Map - Card Placement (Manual Required)
**Screen**: Tactical Battle - Placement Phase
```
[Top: Battle Map Grid - 7×7 tiles]
[Your Side: Bottom 3 rows (green tint)]
[Enemy Side: Top 3 rows (red tint, grayed out)]
[No Man's Land: Middle row (neutral)]

[Bottom: Your Hand - 11 cards displayed]
[Cards: Epic Water Mage, 2× Knight, 2× Archer, 2× Scout, 1× Healer, 1× Granary, 1× Watchtower, 1× Tactic]

[Tutorial Overlay]:
"Place your hero in the front line!"
[Highlight: Water Mage card pulsing]
[Highlight: Center-front tile (row 5, col 4) pulsing green]
```

**Player Action**: Drags Water Mage card to center-front tile

**Visual Feedback**:
- Card lifts off hand (zoom 1.2x)
- Drag ghost shows placement preview
- Tile glows green (valid placement)
- Snap animation when placed
- Card locks in place, border turns blue

**System Actions**:
1. Validate placement (front row allowed for heroes)
2. Lock card to tile
3. Remove card from hand
4. Advance tutorial

**Tutorial Sequence** (Each step waits for player action):
1. "Place your hero" → Player places Water Mage (center-front)
2. "Place your Knights" → Player places 2 Knights (left/right of hero)
3. "Place your Archers in back" → Player places 2 Archers (back row)
4. "Place your Healer" → Player places Healer (behind hero)
5. "Great! We'll auto-place the rest." → System auto-places remaining 5 cards (Scouts, buildings)

**Design Decisions Needed**:
- [ ] Can undo placement before battle starts? (Recommend YES - "Reset Formation" button)
- [ ] Time limit for placement? (Recommend NO for tutorial, add 60-second timer post-tutorial)
- [ ] Invalid placement feedback (red X, "Can't place here" tooltip?)
- [ ] Auto-place algorithm (if player doesn't place all cards, where do they go?)

**Gap**: Placement undo/reset mechanics need design

---

### Step 16: Enemy Placement (Auto)
**Screen**: Enemy Placement Phase
```
[Tutorial text: "Enemy forces deploy!"]

[Enemy units auto-place in 2 seconds]:
- Goblin Chief (center-front, Enemy side row 3)
- 3× Goblin Warrior (front line spread)
- 2× Goblin Archer (back line)

[Animation: Cards slide into position from top of screen]
[Sound: Enemy war cry]

[Text: "Battle begins!"]
[Button: "Start Battle"]
```

**Player Action**: Taps "Start Battle"

**System Actions**:
1. Enemy AI uses "Basic Formation" (tanks front, ranged back)
2. Initialize turn order (player goes first for tutorial)
3. Lock all placements, enter combat phase

**Design Decisions Needed**:
- [ ] Enemy placement animation speed (instant or 2-second animation?)
- [ ] Enemy formation variety (always same for tutorial, random post-tutorial?)

---

### Step 17: Turn 1 - Movement Tutorial
**Screen**: Your Turn - Move Phase
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

[Each action: 1-second animation]
[Total enemy turn: 4-5 seconds]

[Text: "Enemy Turn Complete"]
[Auto-advances to Player Turn 2]
```

**Design Decisions Needed**:
- [ ] Enemy turn speed (1× speed, 2× speed, instant?)
- [ ] Can player skip enemy turn? (Recommend YES - "Skip" button appears after 1 second)
- [ ] Enemy AI "thinking" animation (hourglass icon?)

**Gap**: Enemy turn animation speed control (settings menu option?)

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

**Design Decisions Needed**:
- [ ] When to stop tutorial? (after 2 manual turns, or once player deals 50% damage?)
- [ ] Failure handling (if player loses tutorial battle - retry or resurrect for free?)

**Gap**: Tutorial battle is designed to be unlosable, but need failure recovery flow

---

### Step 23: Victory Screen
**Screen**: Victory!
```
[Background: Animated victory fanfare]
[Large text: "VICTORY!"]
[Fireworks VFX]

[Rewards Box]:
📊 +100 XP (Player Level: 1 → 1, 100/250 XP to Level 2)
💰 +500 Gold (Total: 500 Gold)
🎴 +1 Common Card: [Spearman] (revealed with animation)
🏆 Achievement Unlocked: "First Victory"

[Button: "Continue"]
```

**Player Action**: Taps "Continue"

**System Actions**:
1. Award XP, gold, card
2. Add card to Codex (not auto-added to deck)
3. Check for level-up (no, still Level 1)
4. Unlock "Auto-Battle" feature for future battles
5. Return to County Map

**Design Decisions Needed**:
- [ ] Victory fanfare duration (3 seconds? 5 seconds? skippable?)
- [ ] Card reward destination (Codex or prompt "Add to Deck?")
- [ ] Achievement notification (modal popup or toast notification?)

**Gap**: Where do card rewards go? (Codex auto-add or player choice?)

---

## Phase 6: Post-Tutorial Loop (15-60 Minutes)

### Step 24: County Map - Auto-Battle Unlock
**Screen**: County Map - After First Battle
```
[Camera returns to County Map]
[Player army back on Start tile]
[Fog of War: Revealed 2 more tiles (nearby path + another enemy spawn)]

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
2. Battle auto-plays in 5-10 seconds
3. Victory (guaranteed for tutorial spawns)
4. Rewards screen (same as manual)
5. "That was fast! Auto-Battle is great for farming." (tutorial text)

**Design Decisions Needed**:
- [ ] Auto-Battle speed (5 seconds, 10 seconds, instant with results?)
- [ ] Can cancel mid-auto-battle? (switch to manual control?)
- [ ] Auto-Battle loss handling (if AI loses, retry as manual?)

---

### Step 25: County Map - 3-5 More Battles
**Tutorial Goals**:
1. Defeat 3-5 more easy spawns (2-6 units each)
2. Reach Player Level 2 (unlock 15-20 card deck size)
3. Find first resource node (Gold Mine - introduces Economy cards)
4. Unlock Codex tutorial (after 3 battles)

**Rewards Accumulation**:
- Total XP: 500-700 (reach Level 2)
- Total Gold: 2,500-3,000
- Total Cards: 5-8 new cards (mix of Commons/Uncommons)

**Design Decisions Needed**:
- [ ] Tutorial pacing (how many battles before Codex tutorial?)
- [ ] Enemy difficulty curve (all easy or gradual increase?)
- [ ] Resource node introduction (when do we teach Economy cards?)

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

### Step 27: First Resource Node (Economy Card Introduction)
**Screen**: County Map - Gold Mine Discovered
```
[Player army explores, reveals Gold Mine tile]
[Gold Mine: Neutral tile, no enemies, gold icon]

[Tutorial Overlay]:
"You found a Gold Mine! Deploy Economy Cards here for passive income."

[Player moves army onto Gold Mine]
[Prompt: "Deploy Economy Cards?"]
  - Option 1: Deploy Now (opens Economy card menu)
  - Option 2: Skip (can deploy later)
```

**If Player Chooses "Deploy Now"**:
```
[Economy Card Menu]:
Available Economy Cards in Deck:
- 1× Granary (Food production)
- 1× Watchtower (Vision, no income)

[Tutorial text]:
"You don't have a Mine building yet! You can deploy other buildings or wait to get a Mine card."

[Player deploys Granary]:
- Granary placed on Gold Mine tile
- Tile shows: Gold Mine + Granary icon + "+20 Food/hour"
- Granary card removed from deck (stays on tile)
```

**Tutorial Text**: "Your Granary will produce food while you're away! To retrieve it, return here later."

**Design Decisions Needed**:
- [ ] Economy card tutorial timing (now or later?)
- [ ] Force economy deployment or optional?
- [ ] What if player has no matching building for node type?

**Gap**: Economy card deployment flow needs full design (retrieval, income display, etc.)

---

### Step 28: Tutorial Complete - Freedom Unlocked
**Screen**: Tutorial Complete!
```
[Major Achievement Popup]:
"🎉 Tutorial Complete! 🎉"

Unlocked:
✅ Auto-Battle (fast combat)
✅ Codex (manage collection)
✅ County Map (explore freely)
✅ Daily Login Rewards (start tomorrow)
✅ Pack Shop (buy packs with gold)

[Rewards]:
- 1,000 Gold bonus
- 1 Rare Pack (5 cards)
- "Tutorial Graduate" title

[Next Steps]:
- Complete County Map (defeat Boss)
- Join Alliance (unlock at Level 10)
- Try Arena PvP (unlock at Level 15)

[Button: "Continue Playing"]
```

**Player Action**: Taps "Continue Playing"

**System unlocks**:
1. Full County Map access (10-20 tiles, 1 Boss)
2. Pack shop available
3. Daily rewards start tomorrow
4. Settings menu unlocked (audio, controls, name change)

---

## Summary: Tutorial Completion Checklist

**By end of 15-minute tutorial, player has**:
✅ Created account and chosen name  
✅ Opened 20 starter cards (1 Epic guaranteed)  
✅ Built first deck (11-15 cards, Balanced Explorer theme)  
✅ Received bonus pack (5 cards)  
✅ Learned County Map navigation  
✅ Fought first manual battle (card placement, movement, attack)  
✅ Won first battle (unlosable tutorial)  
✅ Unlocked Auto-Battle  
✅ Collected 500-1,000 gold, 5-8 new cards  
✅ Reached Level 1-2 (100-250 XP)  
✅ Introduced to Codex (card management)  
✅ Introduced to Economy cards (optional deployment)  

**Player is now ready for**:
- County Map free exploration (10-20 battles to Boss)
- Pack purchases (buy with gold)
- Deck customization (swap cards in Codex)
- Economy building (deploy buildings on resource nodes)

---

## Open Gaps & Design Decisions Needed

### Critical Gaps:
1. **EULA/Privacy acceptance flow** (legally required, not designed)
2. **Card pool fallback logic** (what if starter deck can't be built from 20 cards?)
3. **Pack opening skip behavior** (instant reveal or fast-forward animation?)
4. **Placement undo mechanics** (can player reset formation before battle?)
5. **Enemy turn animation speed** (settings option for 1×, 2×, 4×, instant?)
6. **Card reward destination** (auto-add to Codex or prompt "Add to Deck?")
7. **Auto-Battle loss handling** (retry as manual or auto-retry?)
8. **Economy card deployment full flow** (retrieval, income display, tile limits)
9. **Tutorial failure recovery** (if player loses tutorial battle - impossible but need plan)

### Design Decisions Needed:
- [ ] Splash screen duration and logo animation style
- [ ] Default player name format (Player_12345 vs Sovereign_12345)
- [ ] Name change policy (free first change, then cost?)
- [ ] Pack opening speed (4 sec/card too slow?)
- [ ] Legendary near-miss effect (show gold glow that fades?)
- [ ] Grid vs List view for Codex
- [ ] Movement animation speed (instant, 0.5 sec, 1 sec?)
- [ ] Attack animation length (0.5 sec, 1 sec, 2 sec?)
- [ ] Death animation style (shatter, fade, dissolve?)
- [ ] Victory fanfare duration (3 sec, 5 sec, skippable?)
- [ ] Auto-Battle speed (5 sec, 10 sec, instant?)
- [ ] Codex tutorial timing (after 3 battles or Level 2?)
- [ ] Economy card tutorial timing (force now or optional?)

---

## Next Steps

1. **Resolve critical gaps** (EULA, card pool fallback, placement undo)
2. **Make design decisions** (animation speeds, UI layouts, timing)
3. **Create Unity scene breakdown** (Tutorial_01_CardDraw, Tutorial_02_DeckBuild, etc.)
4. **Write QA test script** (literal step-by-step checklist for testing)
5. **Build MVP scope document** (what to implement in Phase 1)
