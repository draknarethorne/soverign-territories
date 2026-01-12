# 🎮 Sovereign Territories

<div align="center">

![Status](https://img.shields.io/badge/Status-Design%20Complete-success)
![Unity](https://img.shields.io/badge/Unity-2021%2B-black?logo=unity)
![C#](https://img.shields.io/badge/C%23-.NET%20Standard%202.1-purple?logo=csharp)
![Nakama](https://img.shields.io/badge/Nakama-3.x-green)
![Platforms](https://img.shields.io/badge/Platforms-iOS%20%7C%20Android%20%7C%20PC-blue)

**"Build the Deck. Rule the Map. Automate the Empire."**

*A hybrid strategy game merging Risk-style territorial conquest, Pokemon TCG deck-building, and Heroes of Might and Magic tactical combat with AFK progression.*

[🎯 Game Bible](docs/game-bible.md) • [📚 Documentation](docs/) • [🔧 Quick Start](#-quick-start) • [🏗️ Architecture](#-project-structure)

</div>

---

## 🎮 What is Sovereign Territories?

A multi-genre fusion designed for **collectors**, **strategists**, and **time-conscious players**:

### Core Pillars

🎴 **TCG Deck-Building** (Pokemon TCG, Hearthstone)
- Collect 140+ cards across 6 rarity tiers (Common → Mythic)
- Strategic deck construction with rarity budget system
- Open packs, chase legendaries, build thematic decks

🗺️ **Territorial Conquest** (Risk, Civilization)
- Alliance wars, 3-month seasonal campaigns
- 200-500 territory global map
- Diplomatic negotiations and resource trading

⚔️ **Tactical Combat** (Heroes of Might and Magic, Fire Emblem)
- Hero-led armies with equipment and abilities
- 8×8 grid turn-based battles
- Formation tactics, terrain modifiers, counter-play

💰 **AFK Progression** (Idle games, mobile strategy)
- Place economy cards on tiles for passive income
- Auto-battle campaigns while offline
- Daily login rewards and milestone systems

---

## 📊 Project Status

| Component | Status | Progress | Location |
|-----------|--------|----------|----------|
| **🎨 Game Design** | ✅ Complete | 100% | [`docs/game-bible.md`](docs/game-bible.md) |
| **📋 Card Data** | 🟡 In Progress | 131/174 | [`data/cards/base-set/`](data/cards/base-set/) |
| **🎁 Phase 2 Expansion** | 🔵 Planned | 48 cards | [`data/cards/phase-2-expansion/`](data/cards/phase-2-expansion/) |
| **📦 Pack Systems** | ✅ Complete | 16/16 | [`data/products/packs/`](data/products/packs/) |
| **🎁 Reward Systems** | ✅ Complete | 100% | [`data/products/rewards/`](data/products/rewards/) |
| **📐 JSON Schemas** | ✅ Complete | 33 schemas | [`data/schemas/`](data/schemas/) |
| **🎮 Unity Project** | 🔴 Not Started | 0% | `src/unity/` (planned) |
| **🖥️ Nakama Server** | 🔴 Not Started | 0% | `server/` (planned) |

**Recent Updates** (Jan 11, 2026):
- ✅ **Base Set Restructure**: 131-card battle-focused MVP (Fire/Water/Earth balanced)
- ✅ **Element Parity Achieved**: All 3 elements now have 5 heroes, balanced units/tactics
- ✅ **Rarity System Overhaul**: maxStars fusion progression, native star variability
- ✅ **Phase 2 Expansion Created**: Deferred 48 economy cards (buildings/equipment/workers)
- ✅ **Mythic Tier Deferred**: Base set focuses Common→Legendary, Mythics for expansions
- ✅ **Major Architecture Overhaul**: Separated runtime data from documentation
- ✅ **Created 33 validation schemas** for all game systems
- ✅ **Single source of truth** architecture (each card = 1 JSON file)

---

## 🏗️ Project Structure

```
soverign-territories/
├── 📁 data/                    # Runtime game data (shipped with game)
│   ├── cards/                  # Card definitions by series
│   │   └── base-set/           # Base Set: 140 cards
│   │       ├── heroes/         # 10 hero cards (Epic/Legendary)
│   │       ├── units/          # 16 unit cards (Common/Uncommon/Rare)
│   │       ├── tactics/        # 3 tactic cards (spell effects)
│   │       └── buildings/      # 1 building card (economy)
│   ├── products/               # Packs, boxes, bundles
│   │   ├── packs/              # 16 pack types (Standard, Element, Premium)
│   │   ├── boxes/              # 3 starter boxes (tutorial rewards)
│   │   └── rewards/            # Daily/weekly/monthly login rewards
│   ├── schemas/                # 33 JSON schemas (validation)
│   ├── manifests/              # Series configs, card pools
│   ├── collection/             # Collection tracking data
│   └── decks/                  # Starter deck configs
│
├── 📁 tools/                   # Build scripts & utilities (not shipped)
│   ├── generators/             # Card importers, doc generators
│   ├── validators/             # Schema validation scripts
│   └── importers/              # Data sync tools
│
├── 📁 docs/                    # Documentation ONLY (Markdown files)
│   ├── game-bible.md           # Master design document (5,800+ lines)
│   ├── specs/                  # Technical specs (battle, economy, etc.)
│   ├── design/                 # Design philosophy, competitive analysis
│   ├── mvp/                    # MVP roadmap and implementation guides
│   └── archive/                # Superseded documents
│
├── 📁 src/                     # Source code (future)
│   ├── unity/                  # Unity 2021+ LTS project (planned)
│   └── nakama/                 # Nakama 3.x server modules (planned)
│
└── 📁 .github/                 # GitHub workflows, Copilot agents
    └── agents/                 # AI agents for design & code
```

### Why This Structure?

✅ **Industry Standard**: Follows Unity (95% of projects), Hearthstone, MTG Arena conventions  
✅ **Clear Separation**: Runtime data (`data/`) vs documentation (`docs/`) vs source code (`src/`)  
✅ **CI/CD Ready**: Build scripts in `tools/`, easy to automate  
✅ **Team Friendly**: Designers edit `data/`, developers edit `src/`, writers edit `docs/`  
✅ **Version Control**: JSON data tracked separately from code  

---

## 🚀 Quick Start

### For Game Designers

1. **📖 Read the Vision**: [`docs/game-bible.md`](docs/game-bible.md) - 5,800+ line master design doc
2. **🎯 Review MVP Scope**: [`docs/mvp/mvp-scope-final.md`](docs/mvp/mvp-scope-final.md) - 8-week roadmap
3. **🎴 Browse Cards**: [`docs/codex/base-set/COMPLETE-CARD-LIST.md`](docs/codex/base-set/COMPLETE-CARD-LIST.md) - All 140 Base Set cards
4. **📦 Check Packs**: [`data/products/packs/`](data/products/packs/) - 16 pack definitions with drop rates
5. **🧭 Navigation**: [`docs/QUICK-START.md`](docs/QUICK-START.md) - Where to find everything

### For Developers

1. **🏗️ Architecture**: [`docs/PROJECT-STRUCTURE-ANALYSIS.md`](docs/PROJECT-STRUCTURE-ANALYSIS.md) - Industry standards analysis
2. **🔍 File Locations**: [`docs/FILE-LOCATIONS.md`](docs/FILE-LOCATIONS.md) - Comprehensive file guide
3. **📐 Data Schemas**: [`data/schemas/`](data/schemas/) - 33 JSON schemas for validation
4. **🎴 Card Architecture**: [`docs/codex/ARCHITECTURE.md`](docs/codex/ARCHITECTURE.md) - Single source of truth pattern
5. **🔧 Unity Guide**: [`docs/mvp/unity-implementation-guide.md`](docs/mvp/unity-implementation-guide.md) - Implementation roadmap

### For Contributors

1. **Clone Repository**:
   ```bash
   git clone https://github.com/scottmelmer/soverign-territories.git
   cd soverign-territories
   ```

2. **Validate Data**:
   ```powershell
   # Run schema validation (requires PowerShell)
   .\tools\generators\validate-base-set.ps1
   ```

3. **Generate Documentation**:
   ```powershell
   # Generate card reference docs from data/
   .\tools\generators\generate-card-reference.ps1
   ```

---

## 🎯 Design Philosophy

### F2P Respect (80-90% Content Accessible)
- ✅ Complete Base Set collection in 5-6 months F2P
- ✅ No forced PvP, no raid timers, no pay-to-win
- ✅ Opt-in PvP with bracketed matchmaking (Level 15+)
- ✅ AFK progression respects player time

### Strategic Depth
- ✅ 6-tier rarity system (Common → Mythic) with visual progression
- ✅ Deck-building with rarity budget (prevents all-Legendary decks)
- ✅ Multi-hero armies (Epic+ heroes lead independent stacks)
- ✅ Formation tactics, terrain modifiers, counter-play

### Collector Appeal
- ✅ 140+ cards in Base Set (Fire, Water, Earth, Lightning, Wind, Frost, Neutral)
- ✅ Thematic decks (mono-element, multi-element synergies)
- ✅ Seasonal exclusives and event cards
- ✅ Pity systems (Legendary/50 packs, Mythic milestone)

### Live Service Model
- ✅ 30-day daily login cycle (11,250 Gold + 895 Gems + 13 packs/month)
- ✅ Weekly events, monthly campaigns, 3-month seasonal wars
- ✅ Gradual content expansion (new card series, maps, modes)

---

## 📚 Key Documents

### Core Design
| Document | Purpose | Lines | Status |
|----------|---------|-------|--------|
| [game-bible.md](docs/game-bible.md) | Master design document | 5,800+ | ✅ Complete |
| [mvp-scope-final.md](docs/mvp/mvp-scope-final.md) | 8-week MVP roadmap | 800+ | ✅ Complete |
| [PROJECT-STRUCTURE-ANALYSIS.md](docs/PROJECT-STRUCTURE-ANALYSIS.md) | Architecture rationale | 608 | ✅ Complete |

### Card Data
| Document | Purpose | Cards | Status |
|----------|---------|-------|--------|
| [COMPLETE-CARD-LIST.md](docs/codex/base-set/COMPLETE-CARD-LIST.md) | All 140 Base Set cards | 140 | ✅ Complete |
| [data/cards/base-set/](data/cards/base-set/) | Individual card JSONs | 30 | 🟡 21% |
| [data/schemas/card-schema.json](data/schemas/card-schema.json) | Card validation schema | - | ✅ Complete |

### Systems Specs
| Document | Purpose | Status |
|----------|---------|--------|
| [specs/battle-schema.md](docs/specs/battle-schema.md) | Combat system | ✅ Complete |
| [specs/progression-schema.md](docs/specs/progression-schema.md) | Player leveling | ✅ Complete |
| [specs/pack-schema.md](docs/specs/pack-schema.md) | Pack opening system | ✅ Complete |
| [specs/economy-node-schema.md](docs/specs/economy-node-schema.md) | AFK income | 🟡 Phase 2 |

---

## 🛠️ Technical Stack

### Frontend
- **Engine**: Unity 2021+ LTS (2.5D isometric maps, 2D tactical battles)
- **Language**: C# (.NET Standard 2.1)
- **UI**: Unity UI Toolkit (recommended) or UGUI
- **Platforms**: iOS, Android, Steam (PC)

### Backend
- **Server**: Nakama 3.x (open-source game server)
- **Database**: PostgreSQL (Nakama default)
- **Real-time**: WebSockets (chat, matchmaking, live battles)
- **Authentication**: Nakama accounts (email, Google, Apple, Steam)

### Infrastructure
- **Version Control**: Git (GitHub)
- **CI/CD**: GitHub Actions (planned)
- **Deployment**: Docker containers for Nakama
- **Cloud**: TBD (AWS, Google Cloud, or Azure)

---

## 📈 Roadmap

### ✅ Phase 0: Design (Complete)
- Game bible, card design, system specs
- Industry analysis, competitive research
- F2P economy balancing, progression curves

### 🔵 Phase 1: MVP (8 Weeks - Ready to Start)
**Week 1-2**: Core Systems
- Card data loading, deck builder, collection tracker
- Battle manager (turn system, damage calculation)
- Basic UI (card viewer, deck editor, battle grid)

**Week 3-4**: Campaign Mode
- 5-battle tutorial campaign
- AI opponents, victory conditions
- Rewards system (Gold, Gems, packs)

**Week 5-6**: Progression
- Player leveling (1-30), deck size unlocks
- Pack opening with pity systems
- Daily login rewards (30-day cycle)

**Week 7-8**: Polish
- Audio/VFX placeholders
- Tutorial flow, onboarding
- Balance testing, bug fixes

### 🟡 Phase 2: RPG Systems (Months 2-3)
- Hero leveling, equipment system
- Multi-hero armies, formation tactics
- County Map exploration (20-40 tiles)

### 🟡 Phase 3: PvP & Social (Months 4-6)
- Matchmade Arena (1v1, Level 15+)
- Alliance system (Level 10+)
- Leaderboards, seasonal rankings

### 🔴 Phase 4: Endgame (Months 7-12)
- Alliance Wars (50v50, Level 30+)
- Global Map (200-500 territories)
- Live events, seasonal campaigns

---

## 🤝 Contributing

This project is currently in **design phase** and not yet open for external contributions. However, design feedback is welcome!

### How to Provide Feedback
1. **Design Questions**: Open a GitHub issue tagged `design-feedback`
2. **Balance Concerns**: Reference specific cards/systems in issue
3. **Technical Suggestions**: Provide rationale and industry examples

### Code Contributions (Future)
Once the Unity project begins, we'll accept:
- Bug fixes, performance optimizations
- UI/UX improvements
- Unit tests for game systems

---

## 📜 License

**Proprietary** - All rights reserved. This project is not open-source.

---

## 🔗 Links

- **Repository**: [github.com/scottmelmer/soverign-territories](https://github.com/scottmelmer/soverign-territories)
- **Game Bible**: [docs/game-bible.md](docs/game-bible.md)
- **Quick Start**: [docs/QUICK-START.md](docs/QUICK-START.md)
- **Architecture**: [docs/PROJECT-STRUCTURE-ANALYSIS.md](docs/PROJECT-STRUCTURE-ANALYSIS.md)

---

<div align="center">

**Built with ❤️ by a solo developer dreaming big**

*"The best TCG meets the best strategy meets the best tactics - with none of the grind."*

![Unity](https://img.shields.io/badge/Made%20with-Unity-black?logo=unity)
![C#](https://img.shields.io/badge/Powered%20by-C%23-purple?logo=csharp)
![Nakama](https://img.shields.io/badge/Backend-Nakama-green)

</div>
