# 🎨 Visual Assets & Art Style Guide

**Last Updated**: December 30, 2024  
**Status**: Design Phase (No assets created yet)

---

## 📋 Overview

This document outlines the visual asset requirements, art style guidelines, and production priorities for **Sovereign Territories**. Assets will be created in phases aligned with development milestones.

---

## 🎯 Art Style Summary

| Element | Style | Reference Games |
|---------|-------|-----------------|
| **Maps** | 2.5D Isometric | Age of Empires II, Civilization VI |
| **Battles** | 2D Tactical Grid | Fire Emblem, Advance Wars |
| **Cards** | Painterly/Illustrated | Hearthstone, Legends of Runeterra |
| **UI** | Dark theme + gold accents | Gwent, Slay the Spire |
| **Color Palette** | Medieval fantasy | Browns, golds, deep blues, forest greens |

---

## 🎴 Card Assets (Priority 1 - MVP Week 1-2)

### Card Frames by Rarity

| Rarity | Border Color | Particle Effects | Stat Count |
|--------|--------------|------------------|------------|
| **Common** (1★) | Gray/Silver | None | 3-5 stats |
| **Uncommon** (1-2★) | Green | Faint glow | 4-6 stats |
| **Rare** (2-3★) | Blue | Moderate glow | 5-7 stats |
| **Epic** (3-4★) | Purple | Strong glow + sparkles | 6-8 stats |
| **Legendary** (5★) | Orange/Gold | Animated flames/light | 7-10 stats |
| **Mythic** (6★) | Rainbow/Prismatic | Animated particles + shine | 8-12 stats |

### Card Frame Templates Needed
- ✅ Base frame layout (PSD/Figma template)
- ✅ 6 rarity border variants
- ✅ 6 card type icons (Hero, Unit, Building, Worker, Tactic, Equipment)
- ✅ 4 element icons (Fire 🔥, Water 💧, Earth 🌍, Lightning ⚡)
- ✅ Stat icons (Attack ⚔️, Defense 🛡️, Health ❤️, Mana 💙, Stamina ⚡)

### Card Illustrations (100 Cards for MVP)

**Heroes** (20 cards):
- 5 Fire Heroes (Fire Mage, Dragon Knight, Phoenix Rider, etc.)
- 5 Water Heroes (Ice Mage, Sea Serpent Rider, etc.)
- 5 Earth Heroes (Stone Golem, Nature Druid, etc.)
- 5 Lightning Heroes (Storm Mage, Thunder Paladin, etc.)

**Units** (40 cards):
- 10 Common units (Goblin Raider, Skeleton Warrior, Elven Archer, etc.)
- 10 Uncommon units (Ogre, Centaur, Harpy, etc.)
- 10 Rare units (Griffon, Wyvern, Treant, etc.)
- 10 Epic units (Dragon, Phoenix, Kraken, etc.)

**Buildings** (20 cards - Economy focus):
- 5 Production (Granary, Sawmill, Mine, Quarry, Fishery)
- 5 Defense (Watchtower, Barracks, Wall, Castle, Fortress)
- 5 Special (Alchemist, Blacksmith, Temple, Academy, Market)
- 5 Wonder (Mythic tier, Phase 4)

**Workers** (10 cards - AFK collection):
- 3 Food workers (Farmer, Shepherd, Baker)
- 3 Lumber workers (Lumberjack, Carpenter, Shipwright)
- 3 Ore workers (Miner, Blacksmith, Jeweler)
- 1 Mythic worker (Legendary Artisan)

**Tactics** (5 cards - MVP limited):
- Fireball (damage spell)
- Heal (restoration)
- Shield (defensive buff)
- Speed Boost (movement buff)
- Summon Goblin (basic summon)

**Equipment** (5 cards - MVP limited):
- Fire Sword (weapon)
- Dragon Armor (armor)
- Iron Shield (shield)
- Health Amulet (accessory)
- Mana Ring (accessory)

---

## 🗺️ Map Assets (Priority 2 - MVP Week 3-4)

### Realm Map Tileset (2.5D Isometric)

**Terrain Types**:
- 🌲 Forest (green, dense trees)
- ⛰️ Mountain (gray/brown, rocky peaks)
- 💧 Water (blue, rivers/lakes)
- 🌾 Plains (light green, grass)
- 🏜️ Desert (tan/yellow, sand dunes) - Phase 3
- ❄️ Snow (white, icy) - Phase 3

**Location Icons**:
- 🏰 Castle (player stronghold)
- 🏘️ Town (resource location)
- 🌲 Forest Camp (exploration point)
- ⛏️ Mine (ore source)
- 🏛️ Ruins (treasure node)
- 🐲 Dragon Lair (boss location)
- 🌊 Shipyard (water access)
- 🏔️ Mountain Pass (chokepoint)

**UI Overlays**:
- Fog of War (dark/grayed out unexplored areas)
- Movement Path (highlighted tiles showing hero route)
- Location Tooltips (name, type, status)

---

## ⚔️ Battle Assets (Priority 2 - MVP Week 3-4)

### Battle Grid (8×8 Tactical Map)

**Tile Types**:
- ⬜ Empty (walkable)
- 🟩 Forest (cover, +10% Evasion)
- 🟫 Mountain (high ground, +20% Defense)
- 🟦 Water (impassable unless Flying/Swimming)
- 🟨 Plains (normal movement)

**Unit Sprites** (2D side-view or top-down):
- Placeholder sprites (100 units, color-coded by type)
- Hero portraits (20 heroes, detailed face art)
- Unit death animations (fade out, particle effects)

**Battle UI Elements**:
- Turn indicator (whose turn it is)
- Initiative bar (turn order display)
- Unit health bars (HP remaining)
- Attack/Defense stats (tooltip display)
- Action buttons (Move, Attack, Ability, End Turn)

---

## 🎮 UI/UX Assets (Priority 3 - MVP Week 5-8)

### Main Menu
- Logo (Sovereign Territories, stylized medieval font)
- Background art (castle, world map, or fantasy landscape)
- Menu buttons (Play, Deck, Store, Settings, Quit)
- Daily Login popup (reward display)

### Deck Builder
- Deck list (scrollable card collection)
- Card filters (Rarity, Element, Type, Cost)
- Deck stats (Rarity Budget bar, card count)
- Drag-and-drop zones (collection → deck)

### Pack Opening
- Pack 3D model (Standard, Element, Epic)
- Card flip animation (back → front reveal)
- Rarity reveal effects (glow, particles, sound)
- New card indicator (first time obtained)

### Battle UI
- Grid overlay (8×8 hex or square tiles)
- Unit selection (highlight, stats display)
- Combat log (damage numbers, effects)
- Victory/Defeat screen (rewards display)

### Progression UI
- Player Level display (current level, XP bar)
- Level-up popup (rewards unlocked)
- Achievement notifications (toast popups)

### Tutorial UI
- Tooltip arrows (pointing to UI elements)
- Highlight boxes (pulsing borders around tutorial targets)
- Text boxes (instruction text, character dialogue)
- Skip Tutorial button (for returning players)

---

## 🎨 Icon Library

### Currency Icons
- 💰 Gold (soft currency, cannot buy)
- 💎 Gems (premium currency)
- ⚡ Energy (stamina system)
- 🍖 Food (resource currency, Phase 2)
- 🪵 Lumber (resource currency, Phase 2)
- ⚒️ Ore (resource currency, Phase 2)
- 🎟️ Arena Tokens (PvP currency, Phase 3)

### Stat Icons
- ⚔️ Attack (offensive power)
- 🛡️ Defense (damage reduction)
- ❤️ Health (hit points)
- 💙 Mana (ability resource)
- ⚡ Stamina (movement points)
- 🏃 Speed (initiative/turn order)
- 🎯 Accuracy (hit chance)
- 🌟 Luck (crit chance)

### Status Effect Icons
- 🔥 Burn (5 damage/turn)
- ❄️ Freeze (skip next turn)
- 🧪 Poison (10% HP/turn)
- ⚡ Stun (cannot move/attack)
- 🛡️ Shield (damage reduction)
- ⚡ Haste (extra movement)
- 🐌 Slow (reduced movement)

---

## 🖼️ Asset Production Phases

### Phase 1: MVP Core (Week 1-4)
**Goal**: Playable prototype with placeholder art
- ✅ Card frame templates (6 rarities)
- ✅ 100 card illustrations (can use AI-generated placeholders initially)
- ✅ Basic UI mockups (Main Menu, Deck Builder, Battle Grid)
- ✅ Currency/Stat icons (16-32px)

**Tools**:
- **Design**: Figma (UI mockups, wireframes)
- **Illustration**: Procreate, Photoshop, or Midjourney/DALL-E (AI placeholders)
- **Icons**: Flaticon, Noun Project (royalty-free), or custom SVGs

### Phase 2: Polish & Effects (Week 5-8)
**Goal**: Polished MVP with animations
- ✅ Pack opening animations (3D models or 2D sprite animations)
- ✅ Battle grid effects (attack animations, hit particles)
- ✅ UI transitions (fade in/out, slide animations)
- ✅ Victory/Defeat screens

**Tools**:
- **Animation**: Spine 2D, Unity Animator
- **Particles**: Unity Particle System
- **Sound**: Royalty-free SFX libraries (Freesound, Zapsplat)

### Phase 3: Post-MVP Art (Month 2-6)
**Goal**: Replace placeholders with final art
- ✅ High-quality card illustrations (commission artists)
- ✅ Map tilesets (Territory Map, World Map)
- ✅ Character portraits (Heroes, NPCs)
- ✅ Seasonal themes (holiday skins, event cards)

---

## 📐 Technical Specifications

### Card Dimensions
- **Resolution**: 512×768px (2:3 aspect ratio)
- **DPI**: 300 DPI for print quality
- **Format**: PNG with transparency
- **File Size**: <500KB per card (optimize for mobile)

### UI Elements
- **Resolution**: 1920×1080px (design for desktop, scale for mobile)
- **Safe Zone**: 10% margin from screen edges
- **Touch Targets**: Minimum 44×44px (iOS guidelines)
- **Format**: PNG or SVG (vectors preferred for icons)

### Map Tiles
- **Tile Size**: 256×256px (isometric) or 128×128px (top-down)
- **Atlas**: Combine into texture atlases for performance
- **Format**: PNG with transparency
- **LOD**: Consider Level of Detail for large maps

---

## 🎨 Color Palette

### Primary Colors
```
Gold:        #FFD700 (UI highlights, Legendary cards)
Dark Brown:  #3E2723 (background, UI panels)
Deep Blue:   #1A237E (water, ice elements)
Forest Green:#2E7D32 (earth, nature elements)
Fire Red:    #C62828 (fire elements, damage)
```

### Rarity Colors
```
Common:      #9E9E9E (Gray)
Uncommon:    #4CAF50 (Green)
Rare:        #2196F3 (Blue)
Epic:        #9C27B0 (Purple)
Legendary:   #FF9800 (Orange)
Mythic:      #E91E63 (Magenta/Rainbow)
```

### UI Colors
```
Background:  #212121 (Dark gray)
Panel:       #424242 (Medium gray)
Text:        #FFFFFF (White)
Accent:      #FFD700 (Gold)
Error:       #F44336 (Red)
Success:     #4CAF50 (Green)
```

---

## 🖌️ Art Style Guidelines

### Card Illustrations
- **Style**: Painterly, semi-realistic (not pixel art or cartoon)
- **Lighting**: Dramatic lighting, rim lights on characters
- **Framing**: Character-focused (70% of card space)
- **Background**: Subtle environment hints (castle, forest, battlefield)
- **Detail**: High detail on face/armor, softer background

### Map Art
- **Style**: Isometric 2.5D (like Age of Empires II, Civ VI)
- **Scale**: Readable from zoomed out view
- **Landmarks**: Iconic shapes (castles, mountains, forests)
- **Fog of War**: Desaturated gray overlay, smooth edges

### UI Design
- **Theme**: Medieval fantasy, dark UI with gold accents
- **Typography**: Serif font for headings (Cinzel, Trajan Pro), sans-serif for body (Roboto, Open Sans)
- **Borders**: Ornate frames (medieval scrollwork, stone textures)
- **Buttons**: Raised 3D effect, gold highlights on hover

---

## 🛠️ Asset Creation Tools

### Recommended Tools
| Tool | Purpose | Cost |
|------|---------|------|
| **Figma** | UI/UX design, wireframes | Free |
| **Photoshop** | Card illustrations, digital painting | $20/month |
| **Procreate** | iPad illustration (alternative to PS) | $13 one-time |
| **Blender** | 3D models (pack boxes, map tiles) | Free |
| **Spine 2D** | 2D animation (card reveals, effects) | $69-$339 |
| **Unity** | Game engine, particle effects | Free |
| **Midjourney** | AI placeholder art (initial prototypes) | $10/month |
| **DALL-E 3** | AI placeholder art (alternative) | $20/month |

### Free Asset Libraries
- **Icons**: Flaticon, Noun Project, Font Awesome
- **Textures**: OpenGameArt, Textures.com
- **SFX**: Freesound, Zapsplat, OpenGameArt
- **Music**: Incompetech, BenSound, OpenGameArt

---

## 📊 Asset Tracking

**Total Assets Needed (MVP)**:
- 🎴 100 card illustrations
- 🖼️ 6 card frame templates
- 🗺️ 8 map terrain types (256×256px each)
- 🏰 20 location icons
- ⚔️ 50 unit sprites (placeholder → final)
- 🎨 40 UI screens (mockups)
- 🔊 50 sound effects (battle, UI, ambient)
- 🎵 5 music tracks (main menu, battle, exploration, victory, defeat)

**Production Estimate**:
- **Solo designer**: 16-24 weeks (full-time)
- **Small team (2-3 artists)**: 8-12 weeks
- **Outsource (freelancers)**: 8-16 weeks ($5,000-$15,000 budget)
- **AI-assisted (placeholders)**: 2-4 weeks (replace with final art later)

---

## 🎯 Asset Priorities for MVP

### Week 1-2 (Cards & UI)
1. Card frame templates (6 rarities) - **Critical**
2. 31 tutorial card illustrations - **Critical**
3. Main Menu mockup - **Critical**
4. Deck Builder mockup - **High**
5. Currency icons (Gold/Gems/Energy) - **High**

### Week 3-4 (Combat & Map)
1. Battle grid tiles (8×8) - **Critical**
2. 50 unit sprites (placeholders OK) - **Critical**
3. Realm Map tileset (8 terrain types) - **High**
4. Attack/Defense stat icons - **High**
5. Battle UI mockup - **Medium**

### Week 5-6 (Stores & Progression)
1. Pack Store UI - **Critical**
2. Pack 3D models (Standard/Element/Epic) - **High**
3. Card flip animation - **High**
4. Progression UI (Level, XP bar) - **Medium**
5. Victory/Defeat screens - **Medium**

### Week 7-8 (Polish)
1. Tutorial tooltips/arrows - **High**
2. Sound effects (50 SFX) - **Medium**
3. Music tracks (5 tracks) - **Medium**
4. Particle effects (attack, crit, level up) - **Low**
5. Final card illustrations (replace placeholders) - **Low** (can be post-MVP)

---

## 📝 Notes for Artists

**Important Guidelines**:
- All assets must work on mobile (1080×1920 portrait, 720×1280 minimum)
- Cards must be readable at small sizes (thumbnails in Deck Builder)
- UI must support colorblind modes (don't rely solely on color)
- Icons should work at 32×32px minimum (mobile tap targets)
- Avoid text in images (use Unity TextMeshPro for localization)

**Feedback Loops**:
- Submit mockups early for approval before final production
- Create 3-5 card frame variations for A/B testing
- Test UI on actual devices (iOS, Android) for readability
- Iterate on particle effects (performance vs visual impact)

---

## 🔗 External Resources

- **Art Reference**: [Pinterest Board](https://pinterest.com) (TBD - create board with Hearthstone, LoR, Fire Emblem references)
- **Color Palette**: [Coolors.co](https://coolors.co) (generate palette from screenshots)
- **Typography**: [Google Fonts](https://fonts.google.com) (Cinzel, Roboto recommended)
- **Icons**: [Flaticon](https://flaticon.com), [Noun Project](https://thenounproject.com)

---

**Last Updated**: December 30, 2024  
**Next Update**: Add concept art examples once visual direction is finalized
