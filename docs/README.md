# 📚 Sovereign Territories Documentation

> **Primary MVP Tagline**: "Build the Deck. Conquer the Campaign. Level Your Heroes."
> 
> **Future Vision Tagline (Phase 2-3)**: "Build the Deck. Rule the Map. Automate the Empire."

Welcome to the comprehensive documentation for **Sovereign Territories** - a hybrid strategy game merging Pokemon TCG deck-building, Risk-style conquest, and Heroes of Might and Magic tactical combat.

---

## 🎯 Quick Start

**New to the project?** Start here (in this order):
1. 📖 Read [game-bible.md](game-bible.md) - Vision and design principles (not implementation detail source)
2. 🎯 Read [mvp/solo-dev-realistic-mvp.md](mvp/solo-dev-realistic-mvp.md) - **Authoritative MVP timeline and scope** (16-24 weeks)
3. 🗺️ Read [mvp/mvp-scope-final.md](mvp/mvp-scope-final.md) - Feature/dependency breakdown (8-week plan is aspirational only)
4. 🎓 Walk through [mvp/tutorial-flow.md](mvp/tutorial-flow.md) - Player onboarding (28 steps, 0-60 min)
5. 🔍 Browse [specs/](specs/) - machine-readable source of truth for system contracts
6. 💻 Start coding with [mvp/unity-implementation-guide.md](mvp/unity-implementation-guide.md)

---

## 📊 Documentation Status

![Bible Status](https://img.shields.io/badge/Bible-4,194_lines-blue)
![Specs](https://img.shields.io/badge/Specs-67_files-green)
![TODOs](https://img.shields.io/badge/TODOs-87_consolidated-yellow)
![MVP Ready](https://img.shields.io/badge/MVP-Ready_for_Unity-brightgreen)

**Last Major Update**: July 27, 2026 (MVP-first canonicalization pass started)

**Current Canonicalization Focus**:
- ✅ Preserve ambition, but enforce MVP firewall and phase boundaries
- ✅ Keep `game-bible.md` as vision doc; move executable rules to focused design/spec docs
- ✅ Use `mvp/solo-dev-realistic-mvp.md` as authoritative schedule baseline
- ✅ Use JSON schemas + focused design docs as implementation truth for tooling and scripts
- 🔄 Normalize tone and monetization language to player-respect principles
- 🔄 Roll out cross-repo quality baseline (pre-commit, markdownlint, governance guides)

**Latest Audit**: [AUDIT-DOCUMENTATION-QUALITY-BRANDING-JUL2026.md](AUDIT-DOCUMENTATION-QUALITY-BRANDING-JUL2026.md)

---

## 📖 Core Documentation

### ✅ Canonical Source of Truth Matrix

| Topic | Primary Source | Secondary Source | Rule |
|------|-----------------|------------------|------|
| Vision, pillars, long-term direction | [game-bible.md](game-bible.md) | `docs/game-bible-review.md` | Vision only, avoid hard implementation formulas here |
| MVP timeline/scope reality | [mvp/solo-dev-realistic-mvp.md](mvp/solo-dev-realistic-mvp.md) | [mvp/mvp-scope-final.md](mvp/mvp-scope-final.md) | Solo-dev doc wins on schedule and scope conflicts |
| Tutorial flow | [mvp/tutorial-flow.md](mvp/tutorial-flow.md) | [mvp/tutorial-gap-resolutions.md](mvp/tutorial-gap-resolutions.md) | Tutorial docs own exact onboarding sequence |
| Progression/deck constraints | [design/deck-progression-rules.md](design/deck-progression-rules.md) | `game-bible.md` refs only | Keep formulas in one canonical design doc |
| Data contracts | [specs/*.json](specs/) | [specs/*.md](specs/) | Schemas are implementation contract for scripts/tools |
| Combat formulas by phase | [design/combat-calculation-spec.md](design/combat-calculation-spec.md) | `game-bible.md` summary | Design spec owns exact formulas |

### 🎮 Master Design
| Document | Purpose | Status | Lines |
|----------|---------|--------|-------|
| [game-bible.md](game-bible.md) | Complete game vision (MVP through Phase 4) | ✅ Authoritative | 4,194 |
| [design/terminology-guide.md](design/terminology-guide.md) | Canonical naming reference | ✅ Stable | ~200 |

**Key Bible Sections**:
- **Section 1**: Overview & Core Pillars (F2P fairness, opt-in PvP, AFK progression)
- **Section 2**: Card System (6 rarities, 6 types, Rarity Budget deck constraints)
- **Section 4**: Gameplay Modes (8 modes from Realm Map PvE to World Map seasons)
- **Section 5**: Economy & Trading (Multi-currency system: Gold/Gems/Stamina + Food/Lumber/Ore)
- **Section 8**: Combat Mechanics (MVP Attack/Defense → Phase 2 Health/Mana/Stamina)
- **Section 9**: Progression (Player Level 1-30, Castle Level 1-15)

---

## 🚀 MVP Implementation

### Essential MVP Documents
| Document | Purpose | Status | Phase |
|----------|---------|--------|-------|
| [mvp/solo-dev-realistic-mvp.md](mvp/solo-dev-realistic-mvp.md) | Authoritative scope and timeline baseline (16-24 weeks) | ✅ Authoritative | MVP |
| [mvp/mvp-scope-final.md](mvp/mvp-scope-final.md) | 8-week decomposition template, dependencies, deliverables | ✅ Supporting | MVP |
| [mvp/tutorial-flow.md](mvp/tutorial-flow.md) | 28-step player journey (0-60 min) | ✅ Complete | MVP |
| [mvp/tutorial-gap-resolutions.md](mvp/tutorial-gap-resolutions.md) | 9 critical design decisions resolved | ✅ Complete | MVP |
| [mvp/unity-implementation-guide.md](mvp/unity-implementation-guide.md) | C# code examples, project structure | ✅ Ready | MVP |

**MVP Scope** (15-minute core loop):
1. Launch → Account → EULA
2. Open 20 starter cards (4 packs × 5 cards)
3. Choose Balanced Explorer deck (11 cards)
4. Progress a linear campaign path (lightweight map presentation)
5. Trigger battle → Place cards on 8×8 grid
6. Win battle → Rewards (Gold, XP, +1 card)
7. Return to campaign progression loop (fight more battles)

---

## 🔧 Implementation Specs

### Core Systems (Priority P0 - MVP Blocking)
| Spec | Covers | Files | Status |
|------|--------|-------|--------|
| **Card System** | 6 rarities, 6 types, stats, rarity budget | [card-schema.json](specs/card-schema.json), [pack-schema.json](specs/pack-schema.json), [trainer-deck-schema.json](specs/trainer-deck-schema.json) | ✅ Ready |
| **Battle System** | 8×8 tactical grid, Attack/Defense formula | [battle-schema.json](specs/battle-schema.json), [ability-schema.json](specs/ability-schema.json) | ✅ Ready |
| **Tutorial** | 28-step onboarding, EULA, safety nets | [tutorial-schema.json](specs/tutorial-schema.json) | ✅ Ready |
| **Deck Management** | 20-card decks, rarity budget validation | [deck-schema.json](specs/deck-schema.json), [starter-deck-schema.json](specs/starter-deck-schema.json) | ✅ Ready |
| **Progression** | Player Level 1-30, XP curves, unlocks | [progression-schema.json](specs/progression-schema.json), [player-schema.json](specs/player-schema.json) | ✅ Ready |

### Supporting Systems (Priority P1 - Post-MVP)
| Spec | Covers | Files | Phase |
|------|--------|-------|-------|
| **Economy** | Gold/Gems/Food/Lumber/Ore, AFK production | [resource-schema.json](specs/resource-schema.json), [economy-system.md](design/economy-system.md) | Phase 2 |
| **Equipment** | Sockets, Jewels/Runes, stats | [equipment-schema.json](specs/equipment-schema.json) | Phase 2 |
| **RPG Stats** | Health/Mana/Stamina, consumables | [rpg-systems-spec.md](design/rpg-systems-spec.md) | Phase 2 |
| **Map Tiers** | World/Territory/Realm/Battle hierarchy | [map-schema.json](specs/map-schema.json), [map-tier-progression.md](design/map-tier-progression.md) | Phase 3 |
| **PvP** | Colosseum, Territory Wars, Alliance Wars | [matchmaking-schema.json](specs/matchmaking-schema.json), [alliance-schema.json](specs/alliance-schema.json) | Phase 3 |

---

## 📁 Document Organization

```
docs/
├── game-bible.md (4,194 lines - master reference)
├── README.md (this file - documentation hub)
│
├── mvp/ (MVP-critical documents)
│   ├── mvp-scope-final.md (8-week roadmap)
│   ├── tutorial-flow.md (28-step journey)
│   ├── tutorial-gap-resolutions.md (9 design decisions)
│   └── unity-implementation-guide.md (C# code examples)
│
├── specs/ (67 files - 33 JSON + 34 MD companions)
│   ├── card-schema.json + card-schema.md
│   ├── pack-schema.json + pack-schema.md
│   ├── battle-schema.json + battle-schema.md
│   ├── tutorial-schema.json + tutorial-schema.md
│   └── ... (30 more schema pairs)
│
├── design/ (Deep-dive design specs)
│   ├── economy-system.md (currency rates, F2P balance)
│   ├── combat-calculation-spec.md (formulas, Phase 2-3 mechanics)
│   ├── rpg-systems-spec.md (Health/Mana/Stamina, equipment)
│   ├── map-tier-progression.md (World→Territory→Realm→Battle)
│   ├── gameplay-modes-spec.md (8 modes with TODOs)
│   ├── terminology-guide.md (canonical terms)
│   ├── assets.md (visual guide)
│   └── design-todos-phase2-3.md (87 consolidated TODOs)
│
├── assets/examples/ (28 JPEGs - battle maps, cards, UI mockups)
│
└── archive/ (completed/superseded documents)
    ├── mvp-scope.md (superseded by mvp-scope-final.md)
    ├── bible-reorganization-plan.md (condensing complete)
    ├── reorganization-status.md (replaced by this README)
    └── documentation-status-report.md (cleanup complete)
```

---

## 🎯 Design TODOs

**All TODOs consolidated**: See [design/design-todos-phase2-3.md](design/design-todos-phase2-3.md)

**Summary**:
- **Total**: 87 design decisions needed
- **Phase 2 (P0)**: 8 blocking TODOs (elemental multipliers, socket counts, AFK rates)
- **Phase 2 (P1)**: 35 nice-to-have TODOs (status effects, consumables, terrain)
- **Phase 3 (P2)**: 44 future TODOs (PvP modes, alliance wars, roguelike)

**Critical Path** (must resolve before Phase 2):
1. Elemental multipliers (Fire vs Water = 1.25× or 1.5×?)
2. Terrain bonuses (Forest +10% Evasion, Mountain +20% Defense?)
3. Status effect durations (Burn/Freeze/Poison = 2-3 turns?)
4. Socket counts by rarity (Mythic = 3 or 4 sockets?)
5. AFK production rates (30 Food/hour with 12-hour cap?)
6. Battle Food cost (20 per battle for F2P balance?)

---

## 🛠️ Tech Stack

**Unity Implementation**:
- **Engine**: Unity 2021 LTS
- **Language**: C# (.NET Standard 2.1)
- **Platforms**: Mobile (iOS/Android) + PC (Steam)
- **UI Framework**: Unity UI Toolkit (recommended) or UGUI
- **Art Style**: 2.5D isometric maps, 2D tactical battles (stylized painterly)

**Backend** (Phase 3):
- **Server**: Nakama 3.x (open-source game server)
- **Database**: PostgreSQL (Nakama default)
- **Real-time**: WebSockets for chat, matchmaking, live battles
- **Authentication**: Nakama accounts (email, Google, Apple, Steam)

**MVP Scope** (Local only):
- **Save System**: Local-first save flow (PlayerPrefs acceptable for prototype)
- **Backend**: Optional for MVP baseline; required for Phase 1.1 async PvP rollout
- **IAP**: Optional stretch for Phase 1.1 (not required for MVP completion)

---

## 📚 Key Concepts

### Card System
- **6 Rarity Tiers**: Common (1★) → Uncommon (1-2★) → Rare (2-3★) → Epic (3-4★) → Legendary (5★) → Mythic (6★)
- **6 Card Types**: Heroes, Units, Buildings, Workers, Tactics, Equipment
- **Rarity Budget**: Deck building constraint (see canonical values in `design/deck-progression-rules.md`)
- **Battle vs Economy Cards**: Separate pools (10-50 battle cards, 10-15 economy cards)

### Progression
- **Dual System**: Player Level (account-wide, deck size) vs Castle Level (per-territory, building slots)
- **MVP unlock focus**: campaign progression, deck growth, and card upgrades
- **Post-MVP unlock focus**: alliances, expanded PvP modes, and territorial systems

### Economy
- **Currencies**: Gold (earned), Gems (premium), Stamina (battle stamina)
- **Resources** (Phase 2+): Food (battles), Lumber (buildings), Ore (equipment)
- **AFK Progression**: Economy cards generate passive income (30 Food/hour, 12-hour cap)
- **F2P Balance**: 80-90% content accessible without spending

### Combat (MVP)
- **Grid**: 8×8 tactical grid (3 rows player, 3 rows enemy, 2 middle)
- **Stats**: HP/Mana/Attack/Defense in MVP baseline (elemental/status systems post-MVP)
- **Formula**: Damage = Attacker's Attack - Defender's Defense (minimum 1)
- **Determinism**: no elemental counters or crit RNG in MVP baseline
- **Placement**: 6-unit battle formation with tactical positioning

---

## 🎮 Game Modes

**MVP** (Realm Map PvE):
- Linear campaign progression with lightweight map framing
- NPC battles (monsters, bandits, bosses)
- Optional movement/exploration presentation (defer full map complexity)
- Stamina cost baseline: 10 per battle (canonical values in MVP docs)

**Phase 2** (Campaign & Expeditions):
- 3 chapters with narrative arcs
- Boss battles with 2-3 phases
- Roguelike Expeditions (random board, mini-battles)

**Phase 3** (PvP & Endgame):
- **Colosseum PvP**: 1v1/3v3 matchmaking, ELO brackets
- **Territory Wars**: 10v10 alliance battles, castle sieges
- **World Map**: 200-500 territories, 3-month seasons, 50v50 wars

---

## 📖 Visual Reference

**Visual Assets**: See [design/assets.md](design/assets.md) for:
- 28 example images (battle maps, card mockups, UI screens)
- Color palette (Fire=red/orange, Water=blue, Earth=brown/green)
- Element-driven visual design (gradients, glows, backgrounds)

**Card Visual Breakdown**:
- Frame color = rarity (Gray/Green/Blue/Purple/Gold/Red-orange)
- Background = element (Fire, Water, Earth, etc.)
- Stars = rarity tier (1-6 stars)
- Stats = Attack/Defense/Health icons

---

## 📄 Schema Reference

**All Schemas**: See [specs/README.md](specs/README.md) for:
- 33 JSON schemas (machine-readable)
- 34 markdown companions (human-readable)
- CI validation instructions
- Versioning guidelines

**Critical Schemas for MVP**:
1. [card-schema.json](specs/card-schema.json) - Card data structure
2. [pack-schema.json](specs/pack-schema.json) - Pack contents, probabilities
3. [deck-schema.json](specs/deck-schema.json) - Deck validation rules
4. [battle-schema.json](specs/battle-schema.json) - Combat grid, turn system
5. [tutorial-schema.json](specs/tutorial-schema.json) - 28-step flow
6. [player-schema.json](specs/player-schema.json) - Account data
7. [progression-schema.json](specs/progression-schema.json) - XP curves

---

## 🚀 Getting Started (Unity Developers)

**Week 1-2: Core Foundation**
1. Create Unity 2021 LTS project
2. Set up folder structure (Scripts/, Prefabs/, Scenes/, Resources/)
3. Create CardData.cs ScriptableObject (see unity-implementation-guide.md)
4. Create 11 test cards (Balanced Explorer starter deck)
5. Create CardVisual prefab with rarity colors

**Week 3-4: Onboarding Flow**
6. Create MainMenu scene (Start Journey button)
7. Create CardDraw scene (pack opening with 20-card reveal)
8. Create DeckBuilder scene (choose Balanced Explorer)
9. Implement pack opening animation (simple fade-in)

**Week 5-6: County Map & Battle**
10. Create CountyMap scene (7×7 grid, 1 enemy spawn)
11. Create Battle scene (8×8 tactical grid)
12. Implement card placement (drag-and-drop onto grid)
13. Implement combat (Attack - Defense = damage)
14. Add turn system (player turn → enemy turn → check victory)

**Week 7-8: Victory Loop & Polish**
15. Create VictoryScreen scene (rewards display)
16. Implement reward system (+100 XP, +500 Gold, +1 card)
17. Bug fixes, optimization (60 FPS on mobile)
18. Playtest with 5-10 users

**See**: [mvp/unity-implementation-guide.md](mvp/unity-implementation-guide.md) for full C# code examples

---

## 📧 Contact & Contribution

**Project Status**: Active development (MVP Phase)  
**Target Launch**: Q2 2026 (MVP), Q4 2026 (Phase 2), 2027 (Phase 3)  

**Documentation Maintained By**:
- Design: @Soverign-Beast-Mode agent (Claude Sonnet 4.5)
- Code: @Soverign-Code-Mode agent (GPT-5.1-Codex)
- Unity: @Soverign-Unity-Builder agent (GPT-4o)

**Last Documentation Audit**: July 27, 2026  
**Next Planned Update**: Post-MVP playtest feedback (Week 9)

---

**Document Version**: 2.0 (Post-Cleanup)  
**Bible Version**: 4,194 lines (38% reduction complete)  
**Specs Count**: 67 files (33 JSON + 34 MD)  
**TODOs**: 87 (all Phase 2-3, none blocking MVP)
