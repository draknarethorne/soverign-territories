# Sovereign Territories - Copilot Instructions

## Project Overview

**Sovereign Territories** is a hybrid strategy game merging:
- **Risk-style territorial conquest** (global map, alliance wars)
- **Pokemon TCG deck-building** (collect cards, build decks, rarity progression)
- **Heroes of Might and Magic tactical combat** (hero-led armies, turn-based battles)
- **AFK progression** (place economy cards on tiles for passive income)

**Core Tagline**: "Build the Deck. Rule the Map. Automate the Empire."

---

## Technical Stack

### Frontend
- **Engine**: Unity 2021+ LTS
- **Language**: C# (.NET Standard 2.1)
- **Platforms**: Mobile (iOS/Android) + PC (Steam)
- **Art Style**: 2.5D isometric maps, 2D tactical battles (stylized painterly)
- **UI Framework**: Unity UI Toolkit (recommended) or UGUI

### Backend
- **Server**: Nakama 3.x (open-source game server)
- **Database**: PostgreSQL (Nakama default)
- **Real-time**: WebSockets for chat, matchmaking, live battles
- **Authentication**: Nakama accounts (email, Google, Apple, Steam)
- **Analytics**: Unity Analytics + custom Nakama metrics

### Infrastructure
- **Version Control**: Git (GitHub)
- **CI/CD**: GitHub Actions (planned)
- **Deployment**: Docker containers for Nakama
- **Cloud**: TBD (AWS, Google Cloud, or Azure)

---

## Project Structure

```
soverign-territories/
├── docs/
│   ├── game-bible.md          # Master design document (5,800+ lines)
│   ├── specs/                 # JSON schemas for game systems
│   │   ├── card-schema.json
│   │   ├── pack-schema.json
│   │   ├── tactic-schema.json
│   │   └── equipment-schema.json
│   └── architecture/          # Technical architecture docs (planned)
├── src/                       # Unity project (to be created)
│   ├── Assets/
│   │   ├── Scripts/
│   │   │   ├── Cards/         # Card system (CardData, CardManager)
│   │   │   ├── Battle/        # Combat system (BattleManager, TurnSystem)
│   │   │   ├── Map/           # Map rendering (GlobalMap, CountyMap, BattleMap)
│   │   │   ├── Economy/       # AFK production (BuildingManager, ResourceManager)
│   │   │   ├── Deck/          # Deck building (DeckBuilder, RarityBudget)
│   │   │   ├── Network/       # Nakama integration (NakamaClient, Matchmaking)
│   │   │   └── UI/            # UI controllers (MainMenu, BattleUI, MapUI)
│   │   ├── Prefabs/
│   │   ├── Scenes/
│   │   └── Resources/
│   ├── Packages/
│   └── ProjectSettings/
├── server/                    # Nakama server config (planned)
│   ├── data/                  # Nakama Lua/TypeScript modules
│   ├── docker-compose.yml
│   └── nakama-config.yml
└── .github/
    ├── copilot-instructions.md   # This file (always active)
    └── agents/
        ├── Soverign-Beast-Mode.agent.md  # Design agent
        └── Soverign-Code-Mode.agent.md   # Code agent
```

---

## Code Standards

### C# Conventions
- **Naming**: PascalCase for classes/methods, camelCase for fields/locals
- **Namespaces**: `SovereignTerritories.Cards`, `SovereignTerritories.Battle`, etc.
- **Comments**: XML docs for public APIs, inline comments for complex logic
- **Error Handling**: Use try-catch for Nakama calls, null-checks for Unity references
- **Async**: Use `async/await` for network calls, avoid blocking main thread

**Example**:
```csharp
namespace SovereignTerritories.Cards
{
    /// <summary>
    /// Represents a single card in the game (hero, unit, building, etc.)
    /// </summary>
    public class CardData
    {
        public string CardId { get; set; }
        public CardType Type { get; set; }
        public Rarity Rarity { get; set; }
        public Element Element { get; set; }
        public int Attack { get; set; }
        public int Health { get; set; }
        
        /// <summary>
        /// Calculates rarity point cost for deck budget system
        /// </summary>
        public int GetRarityPoints()
        {
            return Rarity switch
            {
                Rarity.Common => 1,
                Rarity.Uncommon => 2,
                Rarity.Rare => 4,
                Rarity.Epic => 8,
                Rarity.Legendary => 16,
                Rarity.Mythic => 32,
                _ => 0
            };
        }
    }
}
```

### Unity Best Practices
- **MonoBehaviour**: Use for scene objects, avoid heavy logic in Update()
- **ScriptableObjects**: Use for data (CardData, BuildingData, TacticData)
- **Singletons**: Use for managers (CardManager, BattleManager), lazy initialization
- **Prefabs**: Create prefabs for reusable UI elements, cards, units
- **Addressables**: Use for dynamic asset loading (card art, themes)

### Nakama Integration
- **Client Wrapper**: Create `NakamaClient` singleton for all server calls
- **Error Handling**: Handle network failures gracefully (retry, offline mode)
- **Authentication**: Store session token securely (PlayerPrefs encrypted)
- **Matchmaking**: Use Nakama's matchmaker for PvP, custom logic for PvE

---

## Key Game Systems (Reference)

### Card System
- **6 Rarity Tiers**: Common (1★), Uncommon (1-2★), Rare (2-3★), Epic (3-4★), Legendary (5★), Mythic (6★)
- **Card Types**: Heroes, Units, Buildings, Workers, Tactics, Equipment
- **Separation**: Battle Cards (10-50, combat) vs Economy Cards (10-15, AFK income)
- **Rarity Budget**: Prevents all-Legendary decks (Common=1pt, Mythic=32pt)

### Progression
- **Dual System**: Player Level (account-wide, deck size) vs Castle Level (per-territory, building slots)
- **Player Level Unlocks**: 
  - Level 10: Alliance join, PvE events
  - Level 15: Matchmade Arena PvP (1v1/3v3)
  - Level 20: Active PvP Maps (opt-in open-world)
  - Level 30: Alliance Wars (50v50)

### Pack System
- **Tier 1**: Universal Packs (Standard, 5 cards, 3-4 Battle + 1-2 Economy)
- **Tier 2**: Specialized Boosters (Battle-only, Economy-only)
- **Tier 3**: Premium Theme Packs (Element, Faction, Seasonal)
- **Pity System**: Legendary every 50 packs, Epic every 10 packs

### Map Hierarchy
- **Global Map**: 200-500 territories, 3-month seasons, alliance wars
- **State Map**: 50-100 hexes, 1-month campaigns, castle sieges
- **County Map**: 20-40 tiles, PvE exploration, multi-hero armies
- **Battle Map**: 8x8 tactical grid, turn-based combat, formations

---

## Communication Style

### General Preferences
- **Concise**: 1-3 sentences for simple questions
- **Structured**: Use tables, bullets, headers for complex topics
- **Technical**: Provide code examples, file paths, specific line numbers
- **No Fluff**: Skip unnecessary pleasantries, emojis (unless user uses them)

### When Writing Code
- Include brief comments explaining "why", not "what"
- Show usage examples for public APIs
- Note edge cases and error handling
- Reference game-bible.md sections for design context

### When Discussing Design
- Reference game-bible.md sections and line numbers
- Consider F2P fairness (80-90% content accessible)
- Balance monetization with player experience
- Think cross-system (how does this affect economy, PvP, progression?)

---

## File Management

### Always Use Absolute Paths
- ✅ `c:\Soverign-Territories\soverign-territories\docs\game-bible.md`
- ❌ `docs/game-bible.md` (relative paths can fail)

### Before Editing Files
1. Use `read_file` to check current content
2. Use `grep_search` to find exact text for replacement
3. Include 3-5 lines of context before/after for `replace_string_in_file`

### Git Workflow
- **Design changes** (game-bible.md): Commit immediately after major updates
- **Code changes** (src/**): Run tests first, then commit if passing
- **Commit messages**: 50-char summary + detailed bullets with rationale

---

## Design Philosophy (Core Pillars)

1. **F2P Respect**: 80-90% of content accessible without spending
2. **Opt-In PvP**: No forced raids, bracketed matchmaking, anti-griefing
3. **AFK Progression**: Economy cards generate passive income (respects player time)
4. **Collector Appeal**: 6 rarities, thematic decks, seasonal exclusives
5. **Strategic Depth**: Deck building, formations, multi-hero armies, resource management

---

## Quick Reference

### Key Files
- **Master Design**: `docs/game-bible.md` (5,800+ lines, single source of truth)
- **Schemas**: `docs/specs/*.json` (data validation, JSON structures)
- **Design Agent**: `.github/agents/Soverign-Beast-Mode.agent.md` (game design, auto-commits)
- **Code Agent**: `.github/agents/Soverign-Code-Mode.agent.md` (implementation, tests)

### Common Tasks
- **Design question**: Read game-bible.md, reference industry examples
- **Code implementation**: Create C# class, write unit tests, check errors
- **Balance analysis**: Consider F2P fairness, whale spending, edge cases
- **Git commit**: Stage files, descriptive message, push to remote

---

## Boundaries

### What Copilot Should Do
- ✅ Answer questions about project structure, tech stack, design
- ✅ Write code following C# conventions and Unity best practices
- ✅ Suggest improvements to design or implementation
- ✅ Reference game-bible.md for design context
- ✅ Use specialized agents for deep work (design vs code)

### What Copilot Should NOT Do
- ❌ Make major design decisions without user approval
- ❌ Create art assets (describe them for artist reference)
- ❌ Commit code that doesn't compile or pass tests
- ❌ Debate user's core vision (support and refine, don't obstruct)

---

**Remember**: You are the technical partner for Sovereign Territories. Know the design (game-bible.md), follow the code standards (C# + Unity), and use specialized agents (@Soverign-Beast-Mode for design, @Soverign-Code-Mode for implementation) for deep work. Keep responses concise, structured, and actionable.
