# Sovereign Territories - MVP Scope & Implementation Roadmap

**Version**: 1.0  
**Last Updated**: December 29, 2025  
**Purpose**: Define Minimum Viable Product for Unity development

---

## MVP Philosophy

**Core Question**: What's the minimum we can build to validate the core loop and get players excited?

**Answer**: **15-minute tutorial loop** - Account → Cards → Deck → Battle → Victory

**Why This MVP?**:
- ✅ Validates core hook (card collecting is fun)
- ✅ Validates core loop (tactical combat works)
- ✅ Validates player onboarding (can new players succeed?)
- ✅ Small enough to build in 4-8 weeks (solo dev or small team)
- ✅ Large enough to be a playable demo for investors/publishers

**Out of Scope for MVP** (Post-MVP features):
- ❌ Alliances, PvP, Global Map (too complex)
- ❌ Economy building deployment (nice-to-have, not core)
- ❌ Multiple county maps (1 tutorial map only)
- ❌ Nakama backend (local save only for MVP)
- ❌ Monetization (no IAP, no ads, just gameplay validation)

---

## MVP Phase Breakdown

### Phase 1: Core Foundation (Week 1-2)
**Goal**: Get cards on screen, basic UI navigation

#### 1.1 Project Setup
- [ ] Create Unity 2021 LTS project
- [ ] Set up folder structure (Scripts/, Prefabs/, Scenes/, Resources/)
- [ ] Import UI Toolkit package
- [ ] Set up Git ignore (Library/, Temp/, Builds/)
- [ ] Create build pipeline (Android/iOS/PC builds)

**Deliverable**: Empty project that compiles and runs on target platforms

---

#### 1.2 Card Data System (ScriptableObjects)
**Files to Create**:
- `Assets/Scripts/Cards/CardData.cs` - Base card data model
- `Assets/Scripts/Cards/CardType.cs` - Enum (Hero, Unit, Building, Tactic)
- `Assets/Scripts/Cards/Rarity.cs` - Enum (Common → Mythic)
- `Assets/Scripts/Cards/Element.cs` - Enum (Fire, Water, Earth, etc.)
- `Assets/Resources/Cards/` - Folder for CardData ScriptableObjects

**CardData.cs Structure**:
```csharp
[CreateAssetMenu(fileName = "New Card", menuName = "Cards/Card Data")]
public class CardData : ScriptableObject
{
    [Header("Basic Info")]
    public string cardId;
    public string cardName;
    public CardType cardType;
    public Rarity rarity;
    public Element element;
    
    [Header("Combat Stats")]
    public int attack;
    public int defense;
    public int health;
    public int movement;
    
    [Header("Visuals")]
    public Sprite cardArt;
    public Sprite cardFrame;
    public string description;
    
    public int GetRarityPoints()
    {
        return rarity switch
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
```

**Test Cards to Create** (ScriptableObjects):
- 1× Epic: Water Mage (hero)
- 2× Uncommon: Knight (unit)
- 2× Uncommon: Archer (unit)
- 2× Common: Scout (unit)
- 1× Rare: Healer (unit)
- 1× Uncommon: Granary (building)
- 1× Uncommon: Watchtower (building)
- 1× Rare: Adaptive Strategy (tactic)

Total: 11 cards (Balanced Explorer starter deck)

**Deliverable**: 11 CardData ScriptableObjects that display in Unity Inspector

---

#### 1.3 Card Visual Prefab
**Files to Create**:
- `Assets/Prefabs/CardVisual.prefab` - Visual representation of a card
- `Assets/Scripts/UI/CardVisualController.cs` - Updates card visuals from CardData

**CardVisual Prefab Structure** (UI Toolkit or UGUI):
```
CardVisual
├── CardFrame (Image - rarity color border)
├── CardArt (Image - hero/unit portrait)
├── CardName (Text)
├── StatsPanel
│   ├── AttackIcon + AttackValue (Text)
│   ├── DefenseIcon + DefenseValue (Text)
│   └── HealthIcon + HealthValue (Text)
└── RarityBadge (Image - star icon × rarity)
```

**CardVisualController.cs**:
```csharp
public class CardVisualController : MonoBehaviour
{
    public Image cardFrame;
    public Image cardArt;
    public TextMeshProUGUI cardName;
    public TextMeshProUGUI attackValue;
    public TextMeshProUGUI defenseValue;
    public TextMeshProUGUI healthValue;
    
    public void SetCardData(CardData data)
    {
        cardArt.sprite = data.cardArt;
        cardName.text = data.cardName;
        attackValue.text = data.attack.ToString();
        defenseValue.text = data.defense.ToString();
        healthValue.text = data.health.ToString();
        
        // Set frame color based on rarity
        cardFrame.color = GetRarityColor(data.rarity);
    }
    
    private Color GetRarityColor(Rarity rarity)
    {
        return rarity switch
        {
            Rarity.Common => Color.gray,
            Rarity.Uncommon => Color.green,
            Rarity.Rare => Color.blue,
            Rarity.Epic => new Color(0.8f, 0f, 0.8f), // Purple
            Rarity.Legendary => new Color(1f, 0.8f, 0f), // Gold
            Rarity.Mythic => new Color(1f, 0.3f, 0f), // Red-orange
            _ => Color.white
        };
    }
}
```

**Deliverable**: CardVisual prefab that displays card data correctly

---

#### 1.4 Card Collection System
**Files to Create**:
- `Assets/Scripts/Cards/CardCollection.cs` - Player's card inventory (ScriptableObject)
- `Assets/Scripts/Cards/CardManager.cs` - Singleton manager for card operations

**CardCollection.cs** (ScriptableObject for save data):
```csharp
[CreateAssetMenu(fileName = "Card Collection", menuName = "Cards/Collection")]
public class CardCollection : ScriptableObject
{
    public List<CardData> ownedCards = new List<CardData>();
    
    public void AddCard(CardData card)
    {
        ownedCards.Add(card);
    }
    
    public void RemoveCard(CardData card)
    {
        ownedCards.Remove(card);
    }
    
    public int GetCardCount(CardData card)
    {
        return ownedCards.Count(c => c.cardId == card.cardId);
    }
}
```

**CardManager.cs** (Singleton for global access):
```csharp
public class CardManager : MonoBehaviour
{
    public static CardManager Instance { get; private set; }
    public CardCollection playerCollection;
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    public void GrantStarterCards()
    {
        // Load all starter cards from Resources
        CardData[] starterCards = Resources.LoadAll<CardData>("Cards/Starter");
        foreach (var card in starterCards)
        {
            playerCollection.AddCard(card);
        }
    }
}
```

**Deliverable**: Card collection system that stores owned cards

---

### Phase 2: Onboarding Flow (Week 3-4)
**Goal**: Player can open cards, build deck, see battle

#### 2.1 Main Menu Scene
**Scene**: `Scenes/MainMenu.unity`

**UI Elements**:
- Background image (county map art)
- "Sovereign Territories" title logo
- "Start Your Journey" button (large, center)
- "Settings" button (small, bottom-right)
- "Quit" button (small, bottom-left)

**Script**: `Scripts/UI/MainMenuController.cs`
```csharp
public class MainMenuController : MonoBehaviour
{
    public void OnStartJourneyClicked()
    {
        // For MVP: Skip account creation, go straight to card draw
        SceneManager.LoadScene("CardDraw");
    }
    
    public void OnSettingsClicked()
    {
        // MVP: Basic settings (audio volume, graphics quality)
        SettingsPanel.SetActive(true);
    }
    
    public void OnQuitClicked()
    {
        Application.Quit();
    }
}
```

**Deliverable**: Main menu that loads card draw scene

---

#### 2.2 Card Draw Scene (Pack Opening)
**Scene**: `Scenes/CardDraw.unity`

**UI Elements**:
- 5 card packs (Image sprites, glowing)
- "Open Packs" button
- Pack opening animation (simple fade/scale, no complex VFX for MVP)
- Card reveal grid (4 cards per pack × 5 packs = 20 cards)

**Script**: `Scripts/UI/PackOpeningController.cs`
```csharp
public class PackOpeningController : MonoBehaviour
{
    public List<CardData> cardPool; // All possible starter cards
    public GameObject cardVisualPrefab;
    public Transform cardGridParent;
    
    private List<CardData> drawnCards = new List<CardData>();
    
    public void OpenPacks()
    {
        // Draw 20 cards with guaranteed distribution
        drawnCards = DrawStarterCards();
        
        // Display cards one-by-one (simple version for MVP)
        StartCoroutine(RevealCards());
    }
    
    private List<CardData> DrawStarterCards()
    {
        List<CardData> cards = new List<CardData>();
        
        // Guaranteed 1 Epic in first 2 packs
        cards.Add(GetRandomCard(Rarity.Epic));
        
        // 5 Rares
        for (int i = 0; i < 5; i++)
            cards.Add(GetRandomCard(Rarity.Rare));
        
        // 8 Uncommons
        for (int i = 0; i < 8; i++)
            cards.Add(GetRandomCard(Rarity.Uncommon));
        
        // 6 Commons
        for (int i = 0; i < 6; i++)
            cards.Add(GetRandomCard(Rarity.Common));
        
        return cards;
    }
    
    private IEnumerator RevealCards()
    {
        foreach (var card in drawnCards)
        {
            // Instantiate card visual
            GameObject cardObj = Instantiate(cardVisualPrefab, cardGridParent);
            cardObj.GetComponent<CardVisualController>().SetCardData(card);
            
            // Simple fade-in animation (MVP)
            cardObj.GetComponent<CanvasGroup>().alpha = 0;
            LeanTween.alphaCanvas(cardObj.GetComponent<CanvasGroup>(), 1f, 0.5f);
            
            yield return new WaitForSeconds(0.6f); // 0.5s animation + 0.1s pause
        }
        
        // Add to player collection
        foreach (var card in drawnCards)
        {
            CardManager.Instance.playerCollection.AddCard(card);
        }
        
        // Show "Build Deck" button
        buildDeckButton.SetActive(true);
    }
}
```

**Deliverable**: Player sees 20 cards revealed (simple animation, no fancy VFX)

---

#### 2.3 Deck Builder Scene (Guided Path Only for MVP)
**Scene**: `Scenes/DeckBuilder.unity`

**UI Elements**:
- "Choose Your Playstyle" header
- 3 cards showing starter decks (Aggro, Defensive, Balanced)
- Deck preview (shows 11 cards in chosen deck)
- "Confirm" button

**Script**: `Scripts/UI/DeckBuilderController.cs`
```csharp
public class DeckBuilderController : MonoBehaviour
{
    public CardData[] balancedExplorerDeck; // 11 cards assigned in Inspector
    
    public void OnChooseBalancedExplorer()
    {
        // For MVP: Just assign pre-made deck
        PlayerDeck.Instance.SetActiveDeck(balancedExplorerDeck.ToList());
        
        // Load County Map scene
        SceneManager.LoadScene("CountyMap");
    }
}
```

**PlayerDeck.cs** (Singleton for active deck):
```csharp
public class PlayerDeck : MonoBehaviour
{
    public static PlayerDeck Instance { get; private set; }
    public List<CardData> activeDeck = new List<CardData>();
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    public void SetActiveDeck(List<CardData> deck)
    {
        activeDeck = deck;
    }
}
```

**Deliverable**: Player chooses Balanced Explorer deck, loads County Map

---

### Phase 3: County Map & Battle (Week 5-6)
**Goal**: Player can move army, trigger battle, win

#### 3.1 County Map Scene (Tutorial Map Only)
**Scene**: `Scenes/CountyMap.unity`

**Map Design**:
- 7×7 tile grid (simple square tiles for MVP)
- Start tile (green, player army icon)
- 1 Path tile (gray)
- 1 Enemy spawn (red, goblin icon)
- Fog of war (black tiles, reveal on approach)

**Script**: `Scripts/Map/CountyMapController.cs`
```csharp
public class CountyMapController : MonoBehaviour
{
    public GameObject playerArmyIcon;
    public GameObject enemySpawnIcon;
    public Tile[,] mapTiles; // 7×7 grid
    
    private Vector2Int playerPosition = new Vector2Int(0, 0);
    private Vector2Int enemyPosition = new Vector2Int(2, 0);
    
    private void Start()
    {
        // Place player army on Start tile
        playerArmyIcon.transform.position = GetTilePosition(playerPosition);
        
        // Place enemy spawn 2 tiles away
        enemySpawnIcon.transform.position = GetTilePosition(enemyPosition);
    }
    
    public void OnPlayerArmyClicked()
    {
        // Highlight movement range (adjacent tiles)
        HighlightMovementRange(playerPosition, 3);
    }
    
    public void OnTileClicked(Vector2Int tilePos)
    {
        // If tile has enemy, trigger battle
        if (tilePos == enemyPosition)
        {
            LoadBattle();
        }
        else
        {
            // Move player army
            MovePlayerArmy(tilePos);
        }
    }
    
    private void LoadBattle()
    {
        // Store enemy data for battle scene
        BattleManager.Instance.SetEnemyDeck(GetEnemyDeck());
        
        // Load battle scene
        SceneManager.LoadScene("Battle");
    }
}
```

**Deliverable**: Player can click army, click enemy, trigger battle

---

#### 3.2 Battle Scene (Tactical Combat)
**Scene**: `Scenes/Battle.unity`

**Battle Grid**:
- 7×7 tile grid (3 rows player, 3 rows enemy, 1 middle)
- Card placement UI (hand of 11 cards at bottom)
- "End Turn" button
- HP/Attack/Defense display for each unit

**Script**: `Scripts/Battle/BattleManager.cs`
```csharp
public class BattleManager : MonoBehaviour
{
    public static BattleManager Instance { get; private set; }
    
    public Tile[,] battleGrid; // 7×7
    public List<CardData> playerDeck;
    public List<CardData> enemyDeck;
    
    private List<BattleUnit> playerUnits = new List<BattleUnit>();
    private List<BattleUnit> enemyUnits = new List<BattleUnit>();
    
    private void Awake()
    {
        if (Instance == null) Instance = this;
    }
    
    private void Start()
    {
        // Load player deck from PlayerDeck singleton
        playerDeck = PlayerDeck.Instance.activeDeck;
        
        // Enter placement phase
        EnterPlacementPhase();
    }
    
    private void EnterPlacementPhase()
    {
        // Display player cards in hand
        foreach (var card in playerDeck)
        {
            GameObject cardObj = Instantiate(cardVisualPrefab, handParent);
            cardObj.GetComponent<CardVisualController>().SetCardData(card);
            cardObj.GetComponent<DraggableCard>().enabled = true;
        }
    }
    
    public void OnCardPlaced(CardData card, Vector2Int gridPos)
    {
        // Instantiate unit on battle grid
        BattleUnit unit = Instantiate(battleUnitPrefab, GetTilePosition(gridPos), Quaternion.identity);
        unit.Initialize(card);
        playerUnits.Add(unit);
    }
    
    public void OnEndTurnClicked()
    {
        // Process player turn
        // Process enemy turn (AI)
        // Check victory/defeat
    }
}
```

**BattleUnit.cs** (Unit behavior on grid):
```csharp
public class BattleUnit : MonoBehaviour
{
    public CardData cardData;
    public int currentHP;
    public Vector2Int gridPosition;
    
    public void Initialize(CardData data)
    {
        cardData = data;
        currentHP = data.health;
    }
    
    public void MoveTo(Vector2Int newPos)
    {
        gridPosition = newPos;
        transform.position = BattleManager.Instance.GetTilePosition(newPos);
    }
    
    public void Attack(BattleUnit target)
    {
        int damage = Mathf.Max(0, cardData.attack - target.cardData.defense);
        target.TakeDamage(damage);
    }
    
    public void TakeDamage(int damage)
    {
        currentHP -= damage;
        if (currentHP <= 0)
        {
            Die();
        }
    }
    
    private void Die()
    {
        // Simple death: Destroy game object
        Destroy(gameObject);
    }
}
```

**Deliverable**: Player can place cards, move, attack, win battle

---

### Phase 4: Victory & Loop (Week 7-8)
**Goal**: Player wins, gets rewards, returns to map

#### 4.1 Victory Screen
**Scene**: `Scenes/VictoryScreen.unity`

**UI Elements**:
- "VICTORY!" text (large, animated)
- Rewards box (+100 XP, +500 Gold, +1 Card)
- "Continue" button

**Script**: `Scripts/UI/VictoryScreenController.cs`
```csharp
public class VictoryScreenController : MonoBehaviour
{
    public TextMeshProUGUI xpText;
    public TextMeshProUGUI goldText;
    public GameObject rewardCardVisual;
    
    private void Start()
    {
        // Display rewards
        xpText.text = "+100 XP";
        goldText.text = "+500 Gold";
        
        // Award random Common card
        CardData rewardCard = GetRandomCard(Rarity.Common);
        rewardCardVisual.GetComponent<CardVisualController>().SetCardData(rewardCard);
        CardManager.Instance.playerCollection.AddCard(rewardCard);
    }
    
    public void OnContinueClicked()
    {
        // Return to County Map
        SceneManager.LoadScene("CountyMap");
    }
}
```

**Deliverable**: Victory screen shows rewards, returns to County Map

---

## MVP Feature Checklist

### Core Systems (Must-Have)
- [x] CardData ScriptableObjects (11 test cards)
- [x] Card visual prefab (displays stats, rarity color)
- [x] Card collection system (tracks owned cards)
- [x] Player deck system (active 11-card deck)
- [ ] Main menu (Start Journey button)
- [ ] Pack opening (20-card draw with animation)
- [ ] Deck builder (choose Balanced Explorer only)
- [ ] County Map (7×7 grid, 1 enemy spawn)
- [ ] Battle system (7×7 grid, card placement, turn-based combat)
- [ ] Victory screen (rewards, return to map)

### MVP Scope (15-Minute Loop)
1. Launch game → Main Menu
2. Click "Start Journey" → Pack Opening
3. Watch 20 cards revealed (12 seconds total, simplified animation)
4. Click "Build My Deck" → Deck Builder
5. Choose "Balanced Explorer" → County Map
6. Click army → Click enemy → Battle loads
7. Place 11 cards on grid (tutorial guides first 5, auto-places rest)
8. Attack enemies for 3-5 turns → Win
9. Victory screen → +100 XP, +500 Gold, +1 Card
10. Return to County Map → Can fight again (loop)

**Total Time**: ~15 minutes for first loop, 5 minutes for repeat loops

---

## Post-MVP Features (NOT in MVP)

### Phase 2 (After MVP validation):
- Codex UI (card management, filtering, deck editing)
- Auto-Battle toggle
- Multiple starter decks (Aggro, Defensive)
- Enemy AI improvements (tactics, formations)
- 5-10 more tutorial battles (difficulty curve)
- Player leveling (XP → Level 2 → bigger deck)

### Phase 3 (Backend integration):
- Nakama authentication
- Cloud save (deck persistence)
- Pack shop (buy with gold)
- Daily login rewards

### Phase 4 (Content expansion):
- Multiple county maps (3-5 maps)
- Boss battles (unique mechanics)
- Economy card deployment (resource nodes)
- Alliance system (join/create guilds)

### Phase 5 (Monetization):
- IAP (gem packs, premium packs)
- VIP system (convenience perks)
- Seasonal events (limited cards)

---

## MVP Success Metrics

**We know MVP is successful if**:
1. ✅ First-time player completes 15-minute tutorial without confusion
2. ✅ Player wins first battle easily (tutorial is unlosable)
3. ✅ Player understands card stats (attack, defense, HP)
4. ✅ Player wants to play again (loops back to County Map)
5. ✅ Build runs at 60 FPS on mid-tier mobile (iPhone 12)
6. ✅ No game-breaking bugs (crashes, softlocks)

**Feedback to Collect**:
- "Was pack opening exciting?" (Yes/No + why)
- "Did you understand combat?" (Yes/No + what was confusing)
- "Would you keep playing?" (1-10 scale)
- "What should we build next?" (Open-ended)

---

## Development Timeline (Solo Dev, Part-Time)

**Week 1-2**: Project setup + Card system (ScriptableObjects, visuals, collection)  
**Week 3-4**: Onboarding (Main Menu, Pack Opening, Deck Builder)  
**Week 5-6**: County Map + Battle (grid movement, combat, victory)  
**Week 7-8**: Polish + Testing (animations, sounds, bug fixes)  

**Total**: 8 weeks (2 months) part-time (~20 hours/week = 160 hours total)

**Milestones**:
- End of Week 2: Can see cards in Unity Inspector
- End of Week 4: Can open packs and build deck
- End of Week 6: Can fight and win battle
- End of Week 8: MVP playable start-to-finish

---

## Technical Debt & Shortcuts for MVP

**Things we're NOT doing properly in MVP** (will refactor post-MVP):
- ❌ No Nakama backend (local save only, PlayerPrefs)
- ❌ No proper save system (deck/collection reset on app restart)
- ❌ No unit tests (manual testing only)
- ❌ No localization (English only)
- ❌ No advanced VFX (simple fade/scale animations)
- ❌ No sound/music (placeholder only)
- ❌ No settings menu (audio, graphics, controls)
- ❌ Hard-coded tutorial enemy (no procedural generation)
- ❌ Single battle formation (no player choice)
- ❌ Simplified AI (random move, attack nearest)

**Why these shortcuts are OK**:
- MVP goal is to validate core loop, not ship production
- These are "nice-to-haves" that don't affect gameplay validation
- Can refactor later with proper architecture

---

## Next Steps After MVP Completion

1. **Playtest with 10-20 users** (friends, family, indie game Discord)
2. **Collect feedback** (survey, video recordings of play sessions)
3. **Analyze metrics** (how many complete tutorial? where do they drop off?)
4. **Decide**: Build Phase 2 (Codex, Auto-Battle) OR pivot based on feedback
5. **If successful**: Plan Nakama integration, monetization, content expansion

---

## File Structure for MVP

```
soverign-territories/
├── Assets/
│   ├── Scenes/
│   │   ├── MainMenu.unity
│   │   ├── CardDraw.unity
│   │   ├── DeckBuilder.unity
│   │   ├── CountyMap.unity
│   │   ├── Battle.unity
│   │   └── VictoryScreen.unity
│   ├── Scripts/
│   │   ├── Cards/
│   │   │   ├── CardData.cs
│   │   │   ├── CardCollection.cs
│   │   │   ├── CardManager.cs
│   │   │   ├── PlayerDeck.cs
│   │   │   └── Enums/ (CardType, Rarity, Element)
│   │   ├── UI/
│   │   │   ├── MainMenuController.cs
│   │   │   ├── PackOpeningController.cs
│   │   │   ├── DeckBuilderController.cs
│   │   │   ├── CardVisualController.cs
│   │   │   └── VictoryScreenController.cs
│   │   ├── Map/
│   │   │   ├── CountyMapController.cs
│   │   │   └── Tile.cs
│   │   └── Battle/
│   │       ├── BattleManager.cs
│   │       ├── BattleUnit.cs
│   │       └── TurnSystem.cs
│   ├── Prefabs/
│   │   ├── CardVisual.prefab
│   │   ├── BattleUnit.prefab
│   │   └── Tile.prefab
│   ├── Resources/
│   │   └── Cards/
│   │       ├── Starter/ (11 CardData ScriptableObjects)
│   │       └── Rewards/ (Common cards for battle rewards)
│   └── Art/
│       ├── CardFrames/ (rarity borders)
│       ├── CardArt/ (hero/unit portraits - placeholder for MVP)
│       └── UI/ (buttons, backgrounds)
└── docs/
    ├── game-bible.md (systems reference)
    ├── tutorial-flow.md (player journey)
    └── mvp-scope.md (this document)
```

---

**Ready to build!** Use this document as the implementation roadmap. Start with Week 1 (Card Data System), validate it works, then move to Week 2 (UI flow).
