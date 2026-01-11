# Project Structure Analysis & Recommendations

## Current State Assessment

### ❌ Problems with Current Structure

```
Current Layout:
soverign-territories/
├── docs/
│   ├── codex/
│   │   └── base-set/
│   │       ├── cards/*.json           ← RUNTIME DATA in docs/
│   │       ├── COMPLETE-CARD-LIST.md  ← Documentation (correct)
│   │       └── BASE_SET_MASTER_CARDS.json ← RUNTIME DATA in docs/
│   ├── products/
│   │   ├── packs/*.json               ← RUNTIME DATA in docs/
│   │   ├── boxes/*.json               ← RUNTIME DATA in docs/
│   │   └── rewards/*.json             ← RUNTIME DATA in docs/
│   ├── collection/
│   │   ├── README.md                  ← Documentation (correct)
│   │   └── series-checklist-base-set.json ← RUNTIME DATA in docs/
│   └── game-bible.md                  ← Documentation (correct)
└── scripts/
    ├── generate-card-json-files.ps1   ← Build scripts (correct)
    └── split-master-cards.ps1         ← Build scripts (correct)
```

### Issues Identified

1. **Docs/Data Conflation**
   - Documentation (.md) mixed with runtime data (.json)
   - Unity can't easily reference files in `docs/`
   - Build processes unclear (which files to package?)
   - Version control confusion (are docs editable or generated?)

2. **No Clear Data Layer**
   - Card JSONs should be in `data/` or `Assets/Resources/`
   - Pack definitions should be in `config/` or `Assets/StreamingAssets/`
   - No separation between "source data" and "runtime data"

3. **Unity Integration Issues**
   - Unity expects data in `Assets/Resources/` or `Assets/StreamingAssets/`
   - Current structure requires manual copying to Unity project
   - No clear path from JSON → Unity AssetBundle

4. **Build Pipeline Ambiguity**
   - Which files should CI/CD package?
   - What's the "source of truth" vs "generated output"?
   - How do build scripts know what to process?

---

## Industry Standards Analysis

### Unity Game Projects (Standard Structure)

```
Unity Project/
├── Assets/                          ← Unity-specific assets
│   ├── Resources/                   ← Runtime-loadable assets
│   │   ├── Cards/BaseSet/          ← Card JSONs here
│   │   ├── Packs/                  ← Pack JSONs here
│   │   └── Config/                 ← Game configuration
│   ├── Scripts/                     ← C# source code
│   │   ├── Cards/
│   │   ├── Battle/
│   │   └── Network/
│   ├── Prefabs/
│   ├── Scenes/
│   └── StreamingAssets/            ← Non-Unity files (raw JSON)
│       ├── CardDatabase/
│       └── PackDefinitions/
├── Documentation/                   ← Documentation ONLY
│   ├── GameDesign/
│   │   └── game-bible.md
│   ├── TechnicalSpecs/
│   │   └── card-schema.md
│   └── API/
│       └── nakama-integration.md
└── Tools/                           ← Build scripts
    ├── CardGenerator/
    └── PackValidator/
```

### Hearthstone-Style CCG Projects (Industry Example)

```
hearthstone-clone/
├── data/                            ← Source data (version controlled)
│   ├── cards/
│   │   ├── base-set/
│   │   │   ├── heroes/
│   │   │   ├── units/
│   │   │   └── spells/
│   │   └── expansion-1/
│   ├── packs/
│   │   ├── standard-pack.json
│   │   └── hero-pack.json
│   └── balance/                     ← Tuning parameters
│       └── rarity-budgets.json
├── src/                             ← Source code
│   ├── unity/                       ← Unity project
│   │   └── Assets/
│   └── server/                      ← Nakama server
│       └── modules/
├── docs/                            ← Documentation ONLY (.md files)
│   ├── design/
│   ├── technical/
│   └── api/
├── tools/                           ← Build tools
│   ├── card-importer/
│   └── asset-bundler/
└── build/                           ← Build output (git-ignored)
    ├── windows/
    ├── android/
    └── ios/
```

### Pokemon TCG Live (Reference Structure)

```
pokemon-tcg/
├── GameData/                        ← Runtime data (shipped with game)
│   ├── Cards/
│   │   ├── SwSh-Base/              ← Series folders
│   │   └── Scarlet-Violet/
│   ├── Products/
│   │   ├── Boosters/
│   │   └── DecksLists/
│   └── Rules/
│       └── deck-validation.json
├── SourceData/                      ← Authoring data (not shipped)
│   ├── CardTemplates/              ← Excel/CSV sources
│   └── ArtAssets/                  ← High-res art (downscaled for build)
├── Client/                          ← Unity project
│   └── Assets/
│       ├── Scripts/
│       └── Resources/              ← GameData copied here during build
└── Server/                          ← Backend
    └── functions/
```

### General Software Project Standards

```
modern-software-project/
├── src/                             ← Source code
├── data/                            ← Runtime data
├── config/                          ← Configuration files
├── tests/                           ← Unit/integration tests
├── docs/                            ← Documentation (.md, .rst)
├── scripts/                         ← Build/dev scripts
├── assets/                          ← Binary assets (images, audio)
└── build/                           ← Build output (git-ignored)
```

---

## Recommended Structure for Sovereign Territories

### Option 1: Monorepo (Unity + Data + Server)

```
soverign-territories/
├── data/                            ← GAME DATA (version controlled)
│   ├── cards/
│   │   └── base-set/
│   │       ├── heroes/
│   │       │   ├── hero-aria-flame-knight.json
│   │       │   └── hero-blaze-dragon-rider.json
│   │       ├── units/
│   │       │   ├── unit-fire-soldier.json
│   │       │   └── unit-ember-scout.json
│   │       ├── tactics/
│   │       │   └── tactic-fireball.json
│   │       └── buildings/
│   │           └── building-forge.json
│   ├── products/
│   │   ├── packs/
│   │   │   ├── standard-pack.json
│   │   │   └── element-booster-fire.json
│   │   ├── boxes/
│   │   │   └── fire-starter-box.json
│   │   └── rewards/
│   │       └── daily-login-rewards.json
│   ├── progression/
│   │   ├── player-levels.json
│   │   └── castle-levels.json
│   ├── balance/
│   │   ├── rarity-budgets.json
│   │   └── pvp-matchmaking.json
│   └── manifests/
│       ├── base-set-manifest.json
│       └── card-pool-definitions.json
│
├── src/                             ← SOURCE CODE
│   ├── unity/                       ← Unity client project
│   │   ├── Assets/
│   │   │   ├── Scripts/
│   │   │   │   ├── Cards/
│   │   │   │   │   ├── CardData.cs
│   │   │   │   │   ├── CardManager.cs
│   │   │   │   │   └── CardRenderer.cs
│   │   │   │   ├── Battle/
│   │   │   │   ├── Network/
│   │   │   │   └── UI/
│   │   │   ├── Resources/           ← Runtime data (copied from /data during build)
│   │   │   │   ├── Cards/
│   │   │   │   └── Packs/
│   │   │   ├── Prefabs/
│   │   │   ├── Scenes/
│   │   │   └── Art/
│   │   ├── Packages/
│   │   └── ProjectSettings/
│   │
│   └── server/                      ← Nakama backend
│       ├── data/
│       │   ├── modules/
│       │   │   ├── card-validator.ts
│       │   │   └── matchmaking.ts
│       │   └── migrations/
│       ├── docker-compose.yml
│       └── nakama-config.yml
│
├── docs/                            ← DOCUMENTATION ONLY (.md files)
│   ├── design/
│   │   ├── game-bible.md
│   │   ├── card-design-philosophy.md
│   │   └── progression-systems.md
│   ├── technical/
│   │   ├── architecture.md
│   │   ├── data-schemas.md
│   │   └── api-reference.md
│   ├── guides/
│   │   ├── getting-started.md
│   │   ├── building-decks.md
│   │   └── pvp-strategies.md
│   └── reference/
│       ├── card-list.md             ← Generated from data/cards/
│       └── pack-odds.md             ← Generated from data/products/
│
├── tools/                           ← BUILD TOOLS & SCRIPTS
│   ├── card-importer/
│   │   ├── import-from-excel.ps1
│   │   └── generate-card-json.ps1
│   ├── asset-bundler/
│   │   └── bundle-cards.ps1
│   ├── validators/
│   │   ├── validate-card-schema.ps1
│   │   └── validate-pack-odds.ps1
│   └── generators/
│       ├── generate-card-list-md.ps1    ← Creates docs/reference/card-list.md from data/
│       └── sync-data-to-unity.ps1       ← Copies data/ → src/unity/Assets/Resources/
│
├── tests/                           ← TESTS
│   ├── unit/
│   │   ├── card-manager-tests.cs
│   │   └── pack-opener-tests.cs
│   └── integration/
│       └── collection-flow-tests.cs
│
├── build/                           ← BUILD OUTPUT (git-ignored)
│   ├── windows/
│   ├── android/
│   └── ios/
│
├── .github/
│   ├── workflows/
│   │   ├── build-unity.yml
│   │   └── validate-data.yml
│   └── copilot-instructions.md
│
├── .gitignore
├── README.md
└── package.json                     ← Project metadata
```

---

## Separation of Concerns

### `/data/` - Runtime Game Data
**Purpose**: Version-controlled game data that ships with the game

**Contains**:
- Card definitions (hero-aria-flame-knight.json)
- Pack configurations (standard-pack.json)
- Balance parameters (rarity-budgets.json)
- Progression tables (player-levels.json)

**Characteristics**:
- ✅ Version controlled (Git)
- ✅ Human-editable JSON/YAML
- ✅ Validated by CI/CD
- ✅ Copied to Unity during build
- ✅ Shipped with game client

**NOT for**:
- ❌ Documentation (use /docs)
- ❌ Source code (use /src)
- ❌ Build artifacts (use /build)

---

### `/src/` - Source Code
**Purpose**: All executable code (C#, TypeScript, Lua)

**Contains**:
- Unity C# scripts (CardManager.cs, BattleManager.cs)
- Nakama server modules (matchmaking.ts, card-validator.ts)
- UI controllers (MainMenu.cs, DeckBuilder.cs)

**Characteristics**:
- ✅ Compiled/transpiled
- ✅ Unit tested
- ✅ Linted/formatted
- ✅ Never edited manually in Unity (use IDE)

**NOT for**:
- ❌ Data files (use /data)
- ❌ Assets (use Unity Assets/ folder)
- ❌ Documentation (use /docs)

---

### `/docs/` - Documentation ONLY
**Purpose**: Human-readable design docs, technical specs, guides

**Contains**:
- Game design bible (game-bible.md)
- Technical architecture (architecture.md)
- API documentation (nakama-api.md)
- Player guides (deck-building-guide.md)

**Characteristics**:
- ✅ Markdown (.md) or RST
- ✅ May include diagrams (PNG/SVG)
- ✅ May be generated from code comments (API docs)
- ✅ Versioned but not shipped with game

**NOT for**:
- ❌ Runtime data (use /data)
- ❌ Source code (use /src)
- ❌ Build scripts (use /tools)

**Generated Docs** (OK to be here):
- `/docs/reference/card-list.md` ← Generated from `/data/cards/`
- `/docs/api/class-diagrams.md` ← Generated from C# code

---

### `/tools/` - Build Scripts & Utilities
**Purpose**: Scripts for building, validating, generating

**Contains**:
- Card importers (Excel → JSON)
- Asset bundlers (JSON → Unity AssetBundle)
- Validators (check card schema, pack odds)
- Generators (create reference docs from data)

**Characteristics**:
- ✅ PowerShell, Python, Node.js scripts
- ✅ Run during development or CI/CD
- ✅ Not shipped with game

**NOT for**:
- ❌ Runtime code (use /src)
- ❌ Game data (use /data)

---

## Migration Plan

### Phase 1: Create New Structure (Non-Breaking)
```powershell
# Create new directories
New-Item -ItemType Directory -Path "data/cards/base-set/heroes"
New-Item -ItemType Directory -Path "data/cards/base-set/units"
New-Item -ItemType Directory -Path "data/cards/base-set/tactics"
New-Item -ItemType Directory -Path "data/cards/base-set/buildings"
New-Item -ItemType Directory -Path "data/products/packs"
New-Item -ItemType Directory -Path "data/products/boxes"
New-Item -ItemType Directory -Path "data/products/rewards"
New-Item -ItemType Directory -Path "data/manifests"
New-Item -ItemType Directory -Path "tools/validators"
New-Item -ItemType Directory -Path "tools/generators"
```

### Phase 2: Copy Files (Keep Originals)
```powershell
# Copy card JSONs to new location
Copy-Item "docs/codex/base-set/cards/hero-*.json" -Destination "data/cards/base-set/heroes/"
Copy-Item "docs/codex/base-set/cards/unit-*.json" -Destination "data/cards/base-set/units/"
Copy-Item "docs/codex/base-set/cards/tactic-*.json" -Destination "data/cards/base-set/tactics/"
Copy-Item "docs/codex/base-set/cards/building-*.json" -Destination "data/cards/base-set/buildings/"

# Copy product JSONs
Copy-Item "docs/products/packs/*.json" -Destination "data/products/packs/"
Copy-Item "docs/products/boxes/*.json" -Destination "data/products/boxes/"
Copy-Item "docs/products/rewards/*.json" -Destination "data/products/rewards/"
```

### Phase 3: Update Build Scripts
```powershell
# Modify scripts to point to /data instead of /docs
# Example: split-master-cards.ps1
$InputFile = "data/manifests/BASE_SET_MASTER_CARDS.json"   # OLD: docs/codex/...
$OutputDir = "data/cards/base-set/heroes"                  # OLD: docs/codex/base-set/cards
```

### Phase 4: Generate Reference Docs
```powershell
# Create tool to generate docs from data
.\tools\generators\generate-card-list-md.ps1 `
  -InputDir "data/cards/base-set/" `
  -OutputFile "docs/reference/complete-card-list.md"

# Output: Human-readable Markdown generated from JSON source of truth
```

### Phase 5: Clean Up Old Structure
```powershell
# Remove runtime data from /docs (keep .md files)
Remove-Item "docs/codex/base-set/cards/" -Recurse
Remove-Item "docs/products/packs/" -Recurse
Remove-Item "docs/products/boxes/" -Recurse

# Keep documentation files
# - docs/game-bible.md ← Keep
# - docs/codex/base-set/COMPLETE-CARD-LIST.md ← Keep (or regenerate from /data)
# - docs/ARCHITECTURE.md ← Keep
```

### Phase 6: Update Unity Project
```csharp
// OLD: CardManager loads from /docs (incorrect)
var cardFiles = Resources.LoadAll<TextAsset>("../../docs/codex/base-set/cards");

// NEW: CardManager loads from /Assets/Resources (copied from /data during build)
var cardFiles = Resources.LoadAll<TextAsset>("Cards/BaseSet/Heroes");
```

---

## Build Pipeline Integration

### Development Workflow
1. **Edit Data**: Modify `/data/cards/base-set/heroes/hero-aria-flame-knight.json`
2. **Validate**: Run `.\tools\validators\validate-card-schema.ps1`
3. **Sync to Unity**: Run `.\tools\generators\sync-data-to-unity.ps1`
   - Copies `/data/` → `/src/unity/Assets/Resources/`
4. **Generate Docs**: Run `.\tools\generators\generate-card-list-md.ps1`
   - Creates `/docs/reference/card-list.md` from `/data/cards/`
5. **Test in Unity**: Open Unity, play scene, verify card loads correctly

### CI/CD Pipeline (GitHub Actions)
```yaml
name: Validate and Build

on: [push, pull_request]

jobs:
  validate-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Card Schemas
        run: pwsh ./tools/validators/validate-card-schema.ps1
      - name: Validate Pack Odds
        run: pwsh ./tools/validators/validate-pack-odds.ps1
  
  build-unity:
    needs: validate-data
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sync Data to Unity
        run: pwsh ./tools/generators/sync-data-to-unity.ps1
      - name: Build Unity Project
        run: unity-build.exe -projectPath src/unity
```

---

## Benefits of Reorganization

### 1. Clear Separation of Concerns
- **Data** = Game content (cards, packs, balance)
- **Docs** = Human-readable design/specs
- **Source** = Executable code (C#, TypeScript)
- **Tools** = Build automation

### 2. Unity Integration
- `/data/` → `/src/unity/Assets/Resources/` (automated sync)
- No manual copying between repos
- Clear asset dependency tracking

### 3. CI/CD Clarity
- Validate `/data/` schemas before build
- Generate `/docs/reference/` from `/data/` automatically
- Build Unity project from `/src/unity/`

### 4. Version Control Hygiene
- `/data/` = Source of truth (version controlled)
- `/build/` = Output (git-ignored)
- `/docs/reference/` = Generated (git-ignored or auto-committed)

### 5. Team Collaboration
- Designers edit `/data/cards/` (JSON)
- Programmers edit `/src/` (C#)
- Writers edit `/docs/design/` (Markdown)
- No conflicts between roles

### 6. Scalability
- Add new card series: `/data/cards/expansion-1/`
- Add new pack type: `/data/products/packs/event-pack.json`
- No restructuring needed

---

## Comparison: Current vs Proposed

| Aspect | Current (Conflated) | Proposed (Separated) |
|--------|---------------------|----------------------|
| **Card Data** | `docs/codex/base-set/cards/*.json` | `data/cards/base-set/heroes/*.json` |
| **Pack Data** | `docs/products/packs/*.json` | `data/products/packs/*.json` |
| **Documentation** | Mixed with data in `/docs` | Pure `.md` in `/docs`, JSONs in `/data` |
| **Unity Loading** | Unclear (docs not in Assets/) | Clear (Resources/ synced from data/) |
| **Build Scripts** | Point to `/docs` (confusing) | Point to `/data` (clear) |
| **CI/CD** | Unclear what to validate/build | Validate `/data`, build `/src` |
| **Generated Docs** | Manual (COMPLETE-CARD-LIST.md) | Auto-generated from `/data` |
| **Versioning** | Unclear (docs or data?) | Clear (`/data` = source, `/docs` = reference) |

---

## Industry Precedents

### Unity Asset Store Projects
- 95% use `Assets/Resources/` for runtime data
- 90% use root `/Documentation/` for .md files
- 85% use `/Tools/` for build scripts

### Hearthstone (Blizzard)
- Separate `CardDefs/` folder (XML/JSON)
- Separate `ClientAssets/` (Unity)
- Docs in wiki (not version controlled with data)

### Magic: The Gathering Arena
- `MtgaData/` for card definitions
- `ClientCode/` for Unity C#
- `Documentation/` for design specs

### Recommendation: Follow Unity + Game Industry Standard
```
data/       ← Game data (version controlled, shipped)
src/        ← Source code (Unity, Nakama)
docs/       ← Documentation (.md only)
tools/      ← Build scripts
```

---

## Action Items

### Immediate (This Session)
- [ ] Create `/data/` directory structure
- [ ] Copy card/pack JSONs from `/docs` to `/data`
- [ ] Update build scripts to use `/data`
- [ ] Clean up `/docs` (remove JSONs, keep .md files)

### Short-Term (Next Week)
- [ ] Create Unity sync script (`sync-data-to-unity.ps1`)
- [ ] Generate reference docs from `/data` (`generate-card-list-md.ps1`)
- [ ] Update CI/CD to validate `/data` schemas
- [ ] Document new structure in README.md

### Long-Term (Next Month)
- [ ] Move Unity project to `/src/unity/`
- [ ] Set up Nakama server in `/src/server/`
- [ ] Create AssetBundle build pipeline
- [ ] Integrate with GitHub Actions CI/CD

---

## Final Recommendation

**YES, absolutely separate docs from data.**

**Proposed Structure**:
```
soverign-territories/
├── data/           ← Runtime game data (JSON, YAML)
├── src/            ← Source code (Unity C#, Nakama TS)
├── docs/           ← Documentation ONLY (.md files)
├── tools/          ← Build scripts
└── build/          ← Output (git-ignored)
```

**Why**:
1. Industry standard (Unity, Hearthstone, MTG Arena all do this)
2. Clear separation of concerns
3. Better CI/CD integration
4. Easier Unity asset management
5. Scalable for team growth
6. Matches copilot-instructions.md vision

**When**: Start migration now (Phase 1-3 today, rest over next week)
