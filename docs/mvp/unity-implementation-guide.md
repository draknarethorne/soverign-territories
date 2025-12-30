# Sovereign Territories - Unity Implementation Guide

**Version**: 1.0  
**Last Updated**: December 30, 2025  
**Purpose**: Technical reference for Unity developers implementing the MVP

---

## Quick Reference

**Unity Version**: 2021 LTS or newer  
**Target Platforms**: Mobile (iOS/Android) + PC (Steam)  
**UI Framework**: Unity UI Toolkit (recommended) or UGUI  
**Backend**: Local save only for MVP (Nakama integration Phase 3)

**Related Documents**:
- [mvp-scope-final.md](mvp-scope-final.md) - 8-week implementation roadmap
- [tutorial-flow.md](tutorial-flow.md) - Exact player journey for tutorial
- [game-bible.md](../game-bible.md) - Master design reference
- [docs/specs/](../specs/) - JSON schemas for all game systems

---

## Project Structure

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
    └── mvp/
        ├── tutorial-flow.md (player journey)
        ├── unity-implementation-guide.md (this file)
        └── mvp-scope-final.md (8-week roadmap)
```

---

## Core Systems Implementation

### 1. Card Data System (ScriptableObjects)

**Files to Create**:
- `Assets/Scripts/Cards/CardData.cs` - Base card data model
- `Assets/Scripts/Cards/CardType.cs` - Enum (Hero, Unit, Building, Tactic, Equipment, Worker)
- `Assets/Scripts/Cards/Rarity.cs` - Enum (Common → Mythic)
- `Assets/Scripts/Cards/Element.cs` - Enum (Fire, Water, Earth, Wind, Dark, Light, Neutral)
- `Assets/Resources/Cards/` - Folder for CardData ScriptableObjects

#### CardData.cs
```csharp
using UnityEngine;

namespace SovereignTerritories.Cards
{
    [CreateAssetMenu(fileName = "New Card", menuName = "Sovereign Territories/Card Data")]
    public class CardData : ScriptableObject
    {
        [Header("Basic Info")]
        public string cardId;
        public string cardName;
        [TextArea(3, 5)]
        public string description;
        public CardType cardType;
        public Rarity rarity;
        public Element element;
        
        [Header("Combat Stats (MVP: Attack/Defense Only)")]
        public int attack;
        public int defense;
        public int health; // Phase 2: Health/Mana/Stamina
        public int movement;
        
        [Header("Economy Stats (Phase 2: AFK Cards)")]
        public int incomeRate; // Resources per hour
        public string incomeType; // "gold", "food", "lumber", "ore"
        
        [Header("Visuals")]
        public Sprite cardArt;
        public Sprite cardFrame;
        public Color rarityColor;
        
        /// <summary>
        /// Calculates rarity point cost for deck budget system
        /// </summary>
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
        
        /// <summary>
        /// Gets rarity color for UI display
        /// </summary>
        public Color GetRarityColor()
        {
            return rarity switch
            {
                Rarity.Common => new Color(0.7f, 0.7f, 0.7f), // Gray
                Rarity.Uncommon => new Color(0.2f, 0.8f, 0.2f), // Green
                Rarity.Rare => new Color(0.2f, 0.5f, 1f), // Blue
                Rarity.Epic => new Color(0.8f, 0.2f, 0.8f), // Purple
                Rarity.Legendary => new Color(1f, 0.8f, 0f), // Gold
                Rarity.Mythic => new Color(1f, 0.3f, 0f), // Red-orange
                _ => Color.white
            };
        }
    }
}
```

#### CardType.cs
```csharp
namespace SovereignTerritories.Cards
{
    public enum CardType
    {
        Hero,      // Epic+ only, leads armies
        Unit,      // Common-Legendary, combat units
        Building,  // Common-Epic, territory improvements (Phase 2+)
        Tactic,    // Common-Rare, battle abilities
        Equipment, // Uncommon-Legendary, hero gear (Phase 2+)
        Worker     // Common-Uncommon, economy cards (Phase 2+)
    }
}
```

#### Rarity.cs
```csharp
namespace SovereignTerritories.Cards
{
    public enum Rarity
    {
        Common = 0,     // 1 rarity point
        Uncommon = 1,   // 2 rarity points
        Rare = 2,       // 4 rarity points
        Epic = 3,       // 8 rarity points
        Legendary = 4,  // 16 rarity points
        Mythic = 5      // 32 rarity points
    }
}
```

#### Element.cs
```csharp
namespace SovereignTerritories.Cards
{
    public enum Element
    {
        Fire,      // Red/Orange, aggressive
        Water,     // Blue, control/healing
        Earth,     // Brown/Green, defense/economy
        Wind,      // Cyan/White, movement/speed (Phase 2+)
        Dark,      // Purple/Black, debuffs (Phase 2+)
        Light,     // Yellow/White, buffs (Phase 2+)
        Neutral    // Gray, no element bonuses
    }
}
```

---

### 2. Card Collection System

#### CardCollection.cs (ScriptableObject for Save Data)
```csharp
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace SovereignTerritories.Cards
{
    [CreateAssetMenu(fileName = "Card Collection", menuName = "Sovereign Territories/Card Collection")]
    public class CardCollection : ScriptableObject
    {
        public List<CardData> ownedCards = new List<CardData>();
        
        /// <summary>
        /// Adds a card to the collection
        /// </summary>
        public void AddCard(CardData card)
        {
            ownedCards.Add(card);
        }
        
        /// <summary>
        /// Removes a card from the collection
        /// </summary>
        public void RemoveCard(CardData card)
        {
            ownedCards.Remove(card);
        }
        
        /// <summary>
        /// Gets count of a specific card
        /// </summary>
        public int GetCardCount(CardData card)
        {
            return ownedCards.Count(c => c.cardId == card.cardId);
        }
        
        /// <summary>
        /// Gets all unique cards (no duplicates)
        /// </summary>
        public List<CardData> GetUniqueCards()
        {
            return ownedCards.GroupBy(c => c.cardId)
                             .Select(g => g.First())
                             .ToList();
        }
    }
}
```

#### CardManager.cs (Singleton for Global Access)
```csharp
using UnityEngine;

namespace SovereignTerritories.Cards
{
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
        
        /// <summary>
        /// Grants all starter cards (called on first launch)
        /// </summary>
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
}
```

---

### 3. Player Deck System

#### PlayerDeck.cs (Singleton for Active Deck)
```csharp
using System.Collections.Generic;
using UnityEngine;

namespace SovereignTerritories.Cards
{
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
        
        /// <summary>
        /// Sets the active battle deck
        /// </summary>
        public void SetActiveDeck(List<CardData> deck)
        {
            activeDeck = deck;
        }
        
        /// <summary>
        /// Validates deck against rarity budget rules
        /// </summary>
        public bool IsValidDeck()
        {
            int totalPoints = 0;
            foreach (var card in activeDeck)
            {
                totalPoints += card.GetRarityPoints();
            }
            
            // MVP: 100 points max for 11-card deck
            return totalPoints <= 100;
        }
    }
}
```

---

### 4. Card Visual System

#### CardVisualController.cs
```csharp
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace SovereignTerritories.UI
{
    public class CardVisualController : MonoBehaviour
    {
        [Header("Visual Components")]
        public Image cardFrame;
        public Image cardArt;
        public TextMeshProUGUI cardName;
        public TextMeshProUGUI attackValue;
        public TextMeshProUGUI defenseValue;
        public TextMeshProUGUI healthValue;
        public Image[] rarityStars; // 1-6 stars based on rarity
        
        private Cards.CardData _cardData;
        
        /// <summary>
        /// Updates all visual elements from CardData
        /// </summary>
        public void SetCardData(Cards.CardData data)
        {
            _cardData = data;
            
            // Basic info
            cardName.text = data.cardName;
            
            // Stats
            attackValue.text = data.attack.ToString();
            defenseValue.text = data.defense.ToString();
            healthValue.text = data.health.ToString();
            
            // Art
            cardArt.sprite = data.cardArt;
            
            // Rarity color
            cardFrame.color = data.GetRarityColor();
            
            // Rarity stars (1-6)
            int starCount = (int)data.rarity + 1;
            for (int i = 0; i < rarityStars.Length; i++)
            {
                rarityStars[i].enabled = i < starCount;
            }
        }
        
        public Cards.CardData GetCardData()
        {
            return _cardData;
        }
    }
}
```

---

### 5. Pack Opening System

#### PackOpeningController.cs
```csharp
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using SovereignTerritories.Cards;

namespace SovereignTerritories.UI
{
    public class PackOpeningController : MonoBehaviour
    {
        [Header("Card Pool")]
        public List<CardData> cardPool; // All possible starter cards
        
        [Header("UI References")]
        public GameObject cardVisualPrefab;
        public Transform cardGridParent;
        public GameObject buildDeckButton;
        
        private List<CardData> drawnCards = new List<CardData>();
        
        /// <summary>
        /// Opens tutorial starter packs (20 cards total)
        /// </summary>
        public void OpenTutorialPacks()
        {
            // Draw 20 cards with guaranteed distribution
            drawnCards = DrawStarterCards();
            
            // Display cards one-by-one
            StartCoroutine(RevealCards());
        }
        
        private List<CardData> DrawStarterCards()
        {
            List<CardData> cards = new List<CardData>();
            
            // Tutorial guaranteed distribution (from tutorial-flow.md):
            // - 10 guaranteed cards (curated list)
            // - 10 random cards (weighted by rarity)
            
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
        
        private CardData GetRandomCard(Rarity targetRarity)
        {
            // Filter card pool by rarity
            List<CardData> pool = cardPool.FindAll(c => c.rarity == targetRarity);
            
            // Return random card from pool
            return pool[Random.Range(0, pool.Count)];
        }
        
        private IEnumerator RevealCards()
        {
            foreach (var card in drawnCards)
            {
                // Instantiate card visual
                GameObject cardObj = Instantiate(cardVisualPrefab, cardGridParent);
                cardObj.GetComponent<CardVisualController>().SetCardData(card);
                
                // Simple fade-in animation (MVP)
                CanvasGroup canvasGroup = cardObj.GetComponent<CanvasGroup>();
                if (canvasGroup == null)
                    canvasGroup = cardObj.AddComponent<CanvasGroup>();
                
                canvasGroup.alpha = 0;
                LeanTween.alphaCanvas(canvasGroup, 1f, 0.5f);
                
                yield return new WaitForSeconds(0.6f); // 0.5s animation + 0.1s pause
            }
            
            // Add all cards to player collection
            foreach (var card in drawnCards)
            {
                CardManager.Instance.playerCollection.AddCard(card);
            }
            
            // Show "Build Deck" button
            buildDeckButton.SetActive(true);
        }
    }
}
```

---

### 6. Battle System

#### BattleManager.cs
```csharp
using System.Collections.Generic;
using UnityEngine;

namespace SovereignTerritories.Battle
{
    public class BattleManager : MonoBehaviour
    {
        public static BattleManager Instance { get; private set; }
        
        [Header("Battle Grid")]
        public Tile[,] battleGrid; // 8×8 for MVP
        
        [Header("Decks")]
        public List<Cards.CardData> playerDeck;
        public List<Cards.CardData> enemyDeck;
        
        private List<BattleUnit> playerUnits = new List<BattleUnit>();
        private List<BattleUnit> enemyUnits = new List<BattleUnit>();
        
        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        private void Start()
        {
            // Load player deck from PlayerDeck singleton
            playerDeck = Cards.PlayerDeck.Instance.activeDeck;
            
            // Enter placement phase
            EnterPlacementPhase();
        }
        
        /// <summary>
        /// Phase 1: Player places cards on grid
        /// </summary>
        private void EnterPlacementPhase()
        {
            // Display player cards in hand
            // Allow drag-and-drop onto grid (rows 0-2 for player)
            // Tutorial: Guide first 5 placements, auto-place rest
        }
        
        /// <summary>
        /// Called when player drags card onto grid
        /// </summary>
        public void OnCardPlaced(Cards.CardData card, Vector2Int gridPos)
        {
            // Instantiate unit on battle grid
            // Add to playerUnits list
        }
        
        /// <summary>
        /// Phase 2: Combat resolution (turn-based)
        /// </summary>
        public void OnEndTurnClicked()
        {
            // Process player turn (movement, attacks)
            // Process enemy turn (AI)
            // Check victory/defeat conditions
        }
    }
}
```

#### BattleUnit.cs
```csharp
using UnityEngine;
using SovereignTerritories.Cards;

namespace SovereignTerritories.Battle
{
    public class BattleUnit : MonoBehaviour
    {
        public CardData cardData;
        public int currentHP;
        public Vector2Int gridPosition;
        
        /// <summary>
        /// Initializes unit from CardData
        /// </summary>
        public void Initialize(CardData data)
        {
            cardData = data;
            currentHP = data.health;
        }
        
        /// <summary>
        /// Moves unit to new grid position
        /// </summary>
        public void MoveTo(Vector2Int newPos)
        {
            gridPosition = newPos;
            transform.position = BattleManager.Instance.GetTilePosition(newPos);
        }
        
        /// <summary>
        /// Attacks target unit (MVP: simple Attack - Defense formula)
        /// </summary>
        public void Attack(BattleUnit target)
        {
            int damage = Mathf.Max(0, cardData.attack - target.cardData.defense);
            target.TakeDamage(damage);
        }
        
        /// <summary>
        /// Takes damage and checks for death
        /// </summary>
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
            // Phase 2: Death animation, loot drops
            Destroy(gameObject);
        }
    }
}
```

---

## MVP Implementation Checklist

### Week 1-2: Core Foundation
- [ ] Create Unity 2021 LTS project
- [ ] Set up folder structure (Scripts/, Prefabs/, Scenes/, Resources/)
- [ ] Create CardData.cs with all enums (CardType, Rarity, Element)
- [ ] Create 11 CardData ScriptableObjects (Balanced Explorer starter deck)
- [ ] Create CardVisual prefab with rarity colors
- [ ] Create CardCollection.cs and CardManager.cs
- [ ] Test: Can see 11 cards in Unity Inspector with correct stats

### Week 3-4: Onboarding Flow
- [ ] Create MainMenu scene (Start Journey button)
- [ ] Create CardDraw scene (pack opening with 20-card reveal)
- [ ] Implement PackOpeningController.cs with fade-in animation
- [ ] Create DeckBuilder scene (choose Balanced Explorer only for MVP)
- [ ] Implement PlayerDeck.cs singleton
- [ ] Test: Can open packs, see 20 cards, choose deck

### Week 5-6: County Map & Battle
- [ ] Create CountyMap scene (7×7 grid, 1 enemy spawn)
- [ ] Implement CountyMapController.cs with army movement
- [ ] Create Battle scene (8×8 grid for tactical combat)
- [ ] Implement BattleManager.cs with card placement
- [ ] Implement BattleUnit.cs with Attack/Defense formula
- [ ] Add turn system (player turn → enemy turn → check victory)
- [ ] Test: Can move on map, trigger battle, place cards, attack, win

### Week 7-8: Victory Loop & Polish
- [ ] Create VictoryScreen scene (rewards display)
- [ ] Implement reward system (+100 XP, +500 Gold, +1 card)
- [ ] Add simple animations (fade in/out between scenes)
- [ ] Add placeholder sound effects (button clicks, card reveals)
- [ ] Bug fixes and optimization (60 FPS on mobile)
- [ ] **Playtest with 5-10 users**, collect feedback

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

## Testing Checklist

**Before declaring MVP complete**:
- [ ] Player can complete full 15-minute loop without crashes
- [ ] Card stats display correctly (attack, defense, health, rarity)
- [ ] Pack opening reveals all 20 cards (no stuck animations)
- [ ] Deck builder assigns Balanced Explorer deck correctly
- [ ] County Map allows army movement and battle trigger
- [ ] Battle grid accepts card placement in player rows (0-2)
- [ ] Combat damage formula works (Attack - Defense = damage)
- [ ] Victory screen awards rewards (+100 XP, +500 Gold, +1 card)
- [ ] Can return to County Map and fight again (loop works)
- [ ] Build runs at 60 FPS on mid-tier mobile (iPhone 12, Samsung S21)

**Stretch Goals** (if time permits):
- [ ] Tutorial tooltips for first battle (explain movement, attack)
- [ ] Card hover effect (zoom on mouseover)
- [ ] Battle speed toggle (1×, 2×, 4× for repeat battles)
- [ ] Simple audio (background music, SFX for attacks)

---

## Next Steps After MVP

1. **Playtest with 10-20 users** (friends, family, indie game Discord)
2. **Collect feedback** (survey, video recordings of play sessions)
3. **Analyze metrics** (how many complete tutorial? where do they drop off?)
4. **Decide**: Build Phase 2 (Codex, Auto-Battle, Economy) OR pivot
5. **If successful**: Plan Nakama integration, monetization, content expansion

---

**Document Status**: Ready for Unity implementation  
**Maintained By**: @Soverign-Unity-Builder agent  
**Last Reviewed**: December 30, 2025
