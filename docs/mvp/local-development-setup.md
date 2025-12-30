# Local Development Setup Guide

**Last Updated**: December 30, 2025  
**Target Audience**: New developers setting up Sovereign Territories for the first time  
**Time Required**: 2-4 hours (includes downloads)  
**Related Docs**: [unity-implementation-guide.md](unity-implementation-guide.md), [unity-nakama-frameworks.md](../references/unity-nakama-frameworks.md)

---

## 📋 Overview

This guide walks you through setting up your local development environment for **Sovereign Territories**. You'll install:
1. **Unity 6 LTS** (game client development)
2. **Visual Studio Code** (C# scripting, JSON editing)
3. **Docker Desktop** (Nakama server, Phase 2+)
4. **Git** (version control, already installed)
5. **Free placeholder art assets** (learning phase)

**By the end**: You'll have a working Unity project with placeholder cards, ready to implement the MVP.

---

## 🎯 Phase 1: Unity Setup (MVP Focus)

**Goal**: Build the game client (Codex, Deck Builder, Pack Opening) without server dependency.

### Step 1: Install Unity Hub (20 minutes)

#### Download Unity Hub
1. Go to [https://unity.com/download](https://unity.com/download)
2. Click **"Download Unity Hub"**
3. Run installer: `UnityHubSetup.exe`
4. Accept defaults (install to `C:\Program Files\Unity Hub\`)

#### Install Unity 6 LTS (Recommended)
1. Open **Unity Hub**
2. Click **"Installs"** tab (left sidebar)
3. Click **"Install Editor"** → Choose **"6000.x LTS"** (Unity 6, recommended version shown)
4. Click **"Install"** (Unity 6 installs core editor first, modules come later)
5. Wait for download (3-5 GB, 15-20 minutes)

**Add Modules After Installation** (optional, can do later):
1. In Unity Hub **"Installs"** tab, find Unity 6 LTS
2. Click **⚙️ (gear icon)** → **"Add Modules"**
3. Select:
   - ✅ **Microsoft Visual Studio Community 2022** (C# IDE - recommended)
   - ✅ **Android Build Support** (for mobile later - optional)
   - ✅ **iOS Build Support** (Mac only - optional)
   - ✅ **Documentation** (offline help - optional)
4. Click **"Install"**

**For MVP**: Just the core editor is fine. Add Android/iOS modules when ready to build mobile versions.

**Why Unity 6 LTS?**
- Latest LTS (stable, no breaking changes for 2 years)
- Better performance than Unity 2021
- Improved UI Toolkit (better for card UI)
- Fully compatible with Nakama Unity SDK
- Modern C# features (.NET Standard 2.1)

**Alternative: Unity 2021 LTS**
- If you need older tutorials that reference Unity 2021, install **2021.3.x LTS** instead
- Both versions work fine for Sovereign Territories

---

### Step 2: Create Unity Project (10 minutes)

#### New Project Setup
1. Open **Unity Hub**
2. Click **"Projects"** tab → **"New Project"**
3. Select **"2D Core"** template
4. Configure:
   - **Project Name**: `SovereignTerritories`
   - **Location**: `C:\Soverign-Territories\soverign-territories\src\`
   - **Unity Version**: `6000.x LTS` (or `2021.3.x LTS` if you installed that)
5. Click **"Create Project"** (2-3 minutes to initialize)

#### Verify Project Structure
Unity creates:
```
src/
├── Assets/
│   ├── Scenes/
│   │   └── SampleScene.unity (default scene)
│   ├── Scripts/ (create this manually)
│   └── Resources/ (create this manually)
├── Packages/
│   └── manifest.json (package dependencies)
├── ProjectSettings/
│   └── (Unity config files)
└── SovereignTerritories.sln (Visual Studio solution)
```

#### Create Folder Structure
1. In Unity Editor, right-click **Assets** folder (Project panel)
2. Create folders:
   - `Assets/Scripts/Cards/`
   - `Assets/Scripts/Battle/`
   - `Assets/Scripts/UI/`
   - `Assets/Prefabs/`
   - `Assets/Resources/CardData/`
   - `Assets/Art/Placeholder/`

---

### Step 3: Install Unity Packages (15 minutes)

#### Required Packages
1. In Unity Editor: **Window** → **Package Manager**
2. Install these packages (click **"+"** → **"Add package by name"**):

| Package | Name | Why Needed |
|---------|------|------------|
| **Newtonsoft.Json** | `com.unity.nuget.newtonsoft-json` | Parse card-schema.json |
| **Addressables** | `com.unity.addressables` | Dynamic card loading (Phase 2) |
| **Input System** | `com.unity.inputsystem` | Touch controls (mobile) |
| **TextMeshPro** | `com.unity.textmeshpro` | Better text rendering |

**How to Install**:
```
1. Click "+" in top-left of Package Manager
2. Select "Add package by name..."
3. Paste: com.unity.nuget.newtonsoft-json
4. Click "Add"
5. Repeat for other packages
```

#### Verify Installation
- **Window** → **Package Manager** → Filter: **"In Project"**
- Should see all 4 packages listed

---

### Step 4: Download Free Placeholder Art (30 minutes)

**Goal**: Get functional art to test systems before commissioning custom art.

#### A. Card Frames & UI (Kenney.nl)
1. Go to [https://kenney.nl/assets/boardgame-pack](https://kenney.nl/assets/boardgame-pack)
2. Click **"Download"** (free, no account needed)
3. Extract `boardgame-pack.zip` to `Downloads/`
4. Copy to project:
   - **Card frames**: `boardgame-pack/PNG/Cards/` → `Assets/Art/Placeholder/Cards/`
   - **Tokens**: `boardgame-pack/PNG/Tokens/` → `Assets/Art/Placeholder/Tokens/`
   - **Dice/Icons**: `boardgame-pack/PNG/Dice/` → `Assets/Art/Placeholder/Icons/`

**What You Get**:
- 52 card back designs (use for rarity tiers)
- Token frames (use for unit portraits)
- Dice, coins, meeples (UI elements)

#### B. Fantasy Character Portraits (OpenGameArt)
1. Go to [https://opengameart.org/content/fantasy-hero-set](https://opengameart.org/content/fantasy-hero-set)
2. Download **"Fantasy Hero Set"** (CC0 license)
3. Extract to `Assets/Art/Placeholder/Portraits/`

**Alternative Sources**:
- [https://opengameart.org/content/lpc-heroes](https://opengameart.org/content/lpc-heroes) (100+ characters)
- [https://itch.io/game-assets/free/tag-portrait](https://itch.io/game-assets/free/tag-portrait)

#### C. Icon Set (Game-Icons.net)
1. Go to [https://game-icons.net/](https://game-icons.net/)
2. Search and download icons:
   - **Attack**: Search "sword" → Download SVG
   - **Defense**: Search "shield" → Download SVG
   - **Health**: Search "heart" → Download SVG
   - **Mana**: Search "potion" → Download SVG
   - **Fire**: Search "fire" → Download SVG
   - **Water**: Search "water-drop" → Download SVG
   - **Earth**: Search "mountains" → Download SVG
   - **Lightning**: Search "lightning" → Download SVG
3. Save to `Assets/Art/Placeholder/Icons/`

**Convert SVG to PNG** (Unity doesn't support SVG natively):
- Use [https://svgtopng.com/](https://svgtopng.com/) (free online tool)
- Upload SVG, set size: 128x128px, download PNG

#### D. Map Tiles (Itch.io) - Optional for Phase 2
1. Go to [https://itch.io/game-assets/free/tag-isometric](https://itch.io/game-assets/free/tag-isometric)
2. Download **"Isometric Medieval Tiles"** (free)
3. Save to `Assets/Art/Placeholder/MapTiles/`

---

### Step 5: Import Art to Unity (15 minutes)

#### Import Settings
1. Select all images in `Assets/Art/Placeholder/`
2. In **Inspector** panel (right side), set:
   - **Texture Type**: `Sprite (2D and UI)`
   - **Sprite Mode**: `Single`
   - **Pixels Per Unit**: `100`
   - **Filter Mode**: `Bilinear`
   - **Compression**: `None` (for placeholder quality)
3. Click **"Apply"**

#### Create Sprite Atlas (Performance)
1. Right-click `Assets/Art/Placeholder/Cards/`
2. **Create** → **2D** → **Sprite Atlas**
3. Name it `CardAtlas`
4. Drag all card frames into atlas
5. **Settings**: Max size 2048x2048, format RGBA32

**Why?**: Reduces draw calls (100 cards = 1 draw call instead of 100)

---

### Step 6: First Unity Tutorial (2-3 hours)

**Before writing code**, learn Unity basics:

#### Option A: Ruby's Adventure 2D (RECOMMENDED)
- **Link**: [https://learn.unity.com/project/ruby-s-2d-rpg](https://learn.unity.com/project/ruby-s-2d-rpg)
- **Time**: 3 hours
- **Teaches**: 
  - UI systems (inventory = your Codex)
  - Scripting basics (MonoBehaviour, Start/Update)
  - Input handling (click, drag-drop)
  - Prefabs (card templates)
- **Outcome**: You'll understand how to build Codex UI

#### Option B: Create with Code (Faster)
- **Link**: [https://learn.unity.com/course/create-with-code](https://learn.unity.com/course/create-with-code)
- **Time**: 1.5 hours (Unit 1 only)
- **Teaches**:
  - C# syntax (variables, functions, classes)
  - GameObject basics
  - Inspector usage
- **Outcome**: Understand Unity fundamentals

**Choose Ruby's Adventure** if you want UI focus (closest to ST).

---

## 🎯 Phase 2: Visual Studio Code Setup (Optional)

**Goal**: Better C# editing than Visual Studio Community (lighter, faster).

### Install VS Code (10 minutes)

1. Download: [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. Install with defaults
3. Open VS Code
4. Install extensions (click Extensions icon, left sidebar):
   - ✅ **C#** (by Microsoft) - C# syntax highlighting
   - ✅ **Unity Code Snippets** (by Kleber Silva) - Unity autocomplete
   - ✅ **Unity Tools** (by Tobiah Zarlez) - Unity integration
   - ✅ **GitHub Copilot** (optional, $10/month student free) - AI code completion

### Configure Unity to Use VS Code
1. In Unity Editor: **Edit** → **Preferences** → **External Tools**
2. **External Script Editor**: Browse to `C:\Users\[YourName]\AppData\Local\Programs\Microsoft VS Code\Code.exe`
3. Click **"Regenerate project files"**
4. Test: Double-click any `.cs` file in Unity → should open in VS Code

---

## 🎯 Phase 3: Docker & Nakama Setup (Phase 2+ Only)

**⚠️ SKIP THIS FOR NOW** - Focus on Unity first. Come back when implementing multiplayer (Week 9+).

### Install Docker Desktop (20 minutes)

#### Download & Install
1. Go to [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. Download **Docker Desktop for Windows**
3. Run installer (requires restart)
4. Launch Docker Desktop
5. Sign in with Docker Hub account (free, create at [https://hub.docker.com/signup](https://hub.docker.com/signup))

#### Verify Installation
```powershell
# Open PowerShell
docker --version
# Should output: Docker version 24.x.x

docker run hello-world
# Should download and run test container
```

### Install Nakama Server (15 minutes)

#### Create Docker Compose File
1. Create folder: `C:\Soverign-Territories\soverign-territories\server\`
2. Create file: `server\docker-compose.yml`

**Copy this content**:
```yaml
version: '3'
services:
  postgres:
    image: postgres:12.2-alpine
    environment:
      - POSTGRES_DB=nakama
      - POSTGRES_PASSWORD=localdb
    volumes:
      - data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  nakama:
    image: heroiclabs/nakama:3.17.1
    entrypoint:
      - "/bin/sh"
      - "-ecx"
      - >
        /nakama/nakama migrate up --database.address postgres:localdb@postgres:5432/nakama &&
        exec /nakama/nakama --config /nakama/data/nakama-config.yml --database.address postgres:localdb@postgres:5432/nakama        
    restart: unless-stopped
    links:
      - "postgres:db"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./data:/nakama/data
    ports:
      - "7349:7349"
      - "7350:7350"
      - "7351:7351"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7350/"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  data:
```

3. Create file: `server\data\nakama-config.yml`

**Copy this content**:
```yaml
name: sovereign-territories
data_dir: "./data/"

logger:
  stdout: true
  level: "info"
  file: ""

console:
  port: 7351
  username: "admin"
  password: "password"

socket:
  server_key: "defaultkey"
  port: 7350

session:
  encryption_key: "defaultencryptionkey"
  token_expiry_sec: 7200
```

#### Start Nakama Server
```powershell
# Navigate to server folder
cd C:\Soverign-Territories\soverign-territories\server

# Start Nakama (first run takes 2-3 minutes)
docker-compose up -d

# Check status
docker-compose ps
# Should show nakama and postgres as "Up"

# View logs
docker-compose logs -f nakama
# Press Ctrl+C to exit logs
```

#### Access Nakama Console
1. Open browser: [http://localhost:7351](http://localhost:7351)
2. Login:
   - **Username**: `admin`
   - **Password**: `password`
3. You should see Nakama dashboard (empty, no users yet)

#### Stop Nakama Server
```powershell
# Stop containers (data persists)
docker-compose down

# Stop and delete all data (fresh start)
docker-compose down -v
```

---

## 🎯 Phase 4: Test Your Setup (30 minutes)

**Goal**: Verify everything works before writing game code.

### Test 1: Create First Unity Script

1. In Unity Editor: Right-click `Assets/Scripts/` → **Create** → **C# Script**
2. Name it: `TestSetup`
3. Double-click to open in VS Code
4. Replace contents with:

```csharp
using UnityEngine;

public class TestSetup : MonoBehaviour
{
    void Start()
    {
        Debug.Log("Unity setup successful! Ready to build Sovereign Territories.");
        
        // Test JSON parsing
        string json = "{\"cardName\":\"Test Card\",\"attack\":10}";
        var card = JsonUtility.FromJson<TestCard>(json);
        Debug.Log($"Parsed card: {card.cardName}, Attack: {card.attack}");
    }
}

[System.Serializable]
public class TestCard
{
    public string cardName;
    public int attack;
}
```

5. Save file (Ctrl+S)
6. In Unity: Drag `TestSetup.cs` onto **Main Camera** in Hierarchy
7. Click **Play** button (top center)
8. Check **Console** panel (bottom): Should see "Unity setup successful!"

**✅ If you see the message**: Unity is working correctly!

### Test 2: Load Placeholder Art

1. In Unity: **Assets/Art/Placeholder/Cards/** → Select any card image
2. Drag it into **Scene** view (center panel)
3. Sprite should appear in scene
4. Delete it (select sprite in Hierarchy, press Delete)

**✅ If sprite appeared**: Art importing works!

### Test 3: Test JSON Parsing (Card Schema)

1. Create file: `Assets/Resources/test-card.json`
2. Copy this content:

```json
{
  "cardId": "test_hero_001",
  "name": "Test Fire Hero",
  "rarity": "epic",
  "element": "fire",
  "attack": 45,
  "defense": 30,
  "description": "A test hero for setup verification"
}
```

3. Create script: `Assets/Scripts/Cards/CardLoader.cs`

```csharp
using UnityEngine;

public class CardLoader : MonoBehaviour
{
    void Start()
    {
        // Load JSON from Resources folder
        TextAsset jsonFile = Resources.Load<TextAsset>("test-card");
        
        if (jsonFile != null)
        {
            Debug.Log("JSON file loaded successfully!");
            Debug.Log(jsonFile.text);
        }
        else
        {
            Debug.LogError("Failed to load test-card.json");
        }
    }
}
```

4. Attach `CardLoader.cs` to Main Camera
5. Click **Play**
6. Check **Console**: Should see JSON content

**✅ If JSON printed**: Card data loading works!

---

## 🎯 What's Next?

**You now have**:
- ✅ Unity 6 LTS (or 2021 LTS) installed
- ✅ Project created with folder structure
- ✅ Free placeholder art imported
- ✅ JSON parsing verified
- ✅ Docker + Nakama (optional, for later)

**Next Steps** (Week 1 of MVP):
1. Read [unity-implementation-guide.md](unity-implementation-guide.md)
2. Create `CardData` ScriptableObject
3. Build Codex UI (6-card grid)
4. Load cards from `card-schema.json`
5. Display card details on click

**Recommended Order**:
1. **Day 1-2**: Complete Ruby's Adventure tutorial (learn UI basics)
2. **Day 3**: Create CardData class (copy from unity-implementation-guide.md)
3. **Day 4**: Build simple Codex grid (6 cards hardcoded)
4. **Day 5**: Load cards from JSON (replace hardcoded data)
5. **Day 6-7**: Add filters (by rarity, element) and card detail panel

---

## 📚 Helpful Resources

### Unity Learning
- **Official Tutorials**: [https://learn.unity.com/](https://learn.unity.com/)
- **Scripting Reference**: [https://docs.unity3d.com/ScriptReference/](https://docs.unity3d.com/ScriptReference/)
- **YouTube**: Brackeys (beginner-friendly), Code Monkey (advanced patterns)

### Free Art Sources
- **Kenney.nl**: [https://kenney.nl/assets](https://kenney.nl/assets) (1000+ free assets)
- **OpenGameArt**: [https://opengameart.org/](https://opengameart.org/) (CC0 license)
- **Itch.io**: [https://itch.io/game-assets/free](https://itch.io/game-assets/free)
- **Game-Icons.net**: [https://game-icons.net/](https://game-icons.net/) (3600+ icons)

### Nakama Learning (Phase 2+)
- **Getting Started**: [https://heroiclabs.com/docs/nakama/getting-started/](https://heroiclabs.com/docs/nakama/getting-started/)
- **Unity SDK**: [https://github.com/heroiclabs/nakama-unity](https://github.com/heroiclabs/nakama-unity)
- **Examples**: [https://heroiclabs.com/docs/nakama/tutorials/](https://heroiclabs.com/docs/nakama/tutorials/)

### ST Project Docs
- **Game Bible**: [game-bible.md](../game-bible.md) (master design doc)
- **MVP Scope**: [mvp-scope-final.md](mvp-scope-final.md) (8-week roadmap)
- **Tutorial Flow**: [tutorial-flow.md](tutorial-flow.md) (28-step journey)
- **Unity Guide**: [unity-implementation-guide.md](unity-implementation-guide.md) (C# code examples)

---

## ⚠️ Troubleshooting

### Unity Won't Start
- **Error**: "License activation failed"
- **Fix**: 
  1. Open Unity Hub → **"Preferences"** → **"Licenses"**
  2. Click **"Activate New License"** → **"Unity Personal"** → **"Get a free license"**
  3. Sign in with Unity account (create at [https://id.unity.com/](https://id.unity.com/))

### VS Code Won't Open C# Files
- **Error**: Unity still opens Visual Studio Community
- **Fix**:
  1. Unity → **Edit** → **Preferences** → **External Tools**
  2. **External Script Editor**: Manually browse to `Code.exe`
  3. Click **"Regenerate project files"**
  4. Restart Unity

### Docker Won't Start
- **Error**: "WSL 2 installation is incomplete"
- **Fix**:
  1. Open PowerShell as Administrator
  2. Run: `wsl --install`
  3. Restart computer
  4. Launch Docker Desktop again

### Placeholder Art Looks Blurry
- **Error**: Sprites are pixelated or blurry
- **Fix**:
  1. Select image in Unity Project panel
  2. **Inspector** → **Filter Mode**: `Point (no filter)`
  3. **Compression**: `None`
  4. Click **"Apply"**

### JSON Won't Parse
- **Error**: `JsonUtility.FromJson returns null`
- **Fix**:
  - Ensure class has `[System.Serializable]` attribute
  - Field names must EXACTLY match JSON keys (case-sensitive)
  - Use Newtonsoft.Json for complex nested objects:
    ```csharp
    using Newtonsoft.Json;
    var card = JsonConvert.DeserializeObject<CardData>(json);
    ```

---

## 🎉 Success Checklist

Before proceeding to Week 1 of MVP implementation, verify:

- [ ] Unity 6 LTS (or 2021 LTS) installed and launches successfully
- [ ] Project created at `src/SovereignTerritories/`
- [ ] Folder structure created (Scripts/Cards/, Prefabs/, Resources/CardData/)
- [ ] 4 Unity packages installed (Newtonsoft.Json, Addressables, Input System, TextMeshPro)
- [ ] Placeholder art downloaded and imported (Kenney boardgame pack, portraits, icons)
- [ ] Ruby's Adventure tutorial completed (or Create with Code Unit 1)
- [ ] Test scripts run successfully (TestSetup.cs, CardLoader.cs)
- [ ] VS Code configured as external editor (optional)
- [ ] Docker + Nakama running (optional, skip for now)

**If all checked**: You're ready to build the game! 🚀

**Next Document**: [unity-implementation-guide.md](unity-implementation-guide.md) → Start Week 1 (Card System)

---

**Document Status**: Active development setup guide  
**Last Updated**: December 30, 2025  
**Maintained By**: @Soverign-Beast-Mode agent  
**Questions?**: Check [unity-nakama-frameworks.md](../references/unity-nakama-frameworks.md) for technical deep-dives
