# Tutorial Gap Resolutions
**Version**: 1.0  
**Date**: December 29, 2025  
**Purpose**: Design solutions for 9 critical gaps in tutorial-flow.md

---

## Gap 1: EULA/Privacy Acceptance Flow

### Problem
Tutorial-flow.md skips straight to account creation without legally required Terms of Service and Privacy Policy acceptance. This violates App Store/Google Play requirements.

### Solution
Add pre-login EULA screen with mandatory checkbox acceptance.

**Flow**:
```
Step 1A: Splash Screen (2 seconds)
↓
Step 1B: EULA/Privacy Screen
┌─────────────────────────────────────┐
│ Welcome to Sovereign Territories    │
│                                     │
│ Before you start:                   │
│ [Scrollable text box - 200 words]  │
│ Terms of Service summary            │
│ Privacy Policy summary              │
│                                     │
│ ☐ I accept the Terms and Privacy   │
│                                     │
│ [Read Full Terms] [Read Privacy]    │
│                                     │
│ [Continue] (disabled until checked) │
└─────────────────────────────────────┘
↓
Step 2: Main Menu (only if accepted)
```

**Text Content** (summary version):
```
By playing Sovereign Territories you agree to:
• Collect cards, battle enemies, and manage territories
• Age requirement: 13+ (COPPA compliance)
• Data we collect: Email (optional), device ID, gameplay stats
• Data usage: Save progress, improve game, send updates
• No selling of personal data to third parties
• Full details: [Read Full Terms] [Read Privacy Policy]
```

### Rationale
- **Legal compliance**: Required for App Store/Google Play approval
- **User transparency**: Players know what they're agreeing to
- **Industry standard**: Pokemon GO, Hearthstone, Marvel Snap all use this flow
- **One-time friction**: Only shown once per account, minimal impact on onboarding

### Industry Reference
- **Pokemon GO**: Full-screen EULA before login, checkbox required
- **Hearthstone**: Links to Terms/Privacy in login screen (Blizzard account assumed accepted)
- **Marvel Snap**: EULA checkbox + "By continuing you agree to..." text

**Best Practice**: **Checkbox + scrollable summary + full text links** (Pokemon GO model)

### Implementation Notes
**Unity Scene**: `Scenes/EULA.unity` (loads after Splash, before MainMenu)

**PlayerPrefs Storage**:
```csharp
PlayerPrefs.SetInt("EULA_Accepted_v1", 1); // Version tracking for updates
PlayerPrefs.SetString("EULA_Accept_Date", DateTime.UtcNow.ToString());
```

**Script**: `Scripts/UI/EULAController.cs`
```csharp
public class EULAController : MonoBehaviour
{
    public Toggle acceptCheckbox;
    public Button continueButton;
    
    void Start()
    {
        // Check if already accepted
        if (PlayerPrefs.GetInt("EULA_Accepted_v1", 0) == 1)
        {
            // Skip EULA, go to Main Menu
            SceneManager.LoadScene("MainMenu");
            return;
        }
        
        // Disable Continue button until checkbox checked
        acceptCheckbox.onValueChanged.AddListener(OnCheckboxChanged);
        continueButton.interactable = false;
    }
    
    void OnCheckboxChanged(bool isChecked)
    {
        continueButton.interactable = isChecked;
    }
    
    public void OnContinueClicked()
    {
        PlayerPrefs.SetInt("EULA_Accepted_v1", 1);
        PlayerPrefs.SetString("EULA_Accept_Date", DateTime.UtcNow.ToString());
        SceneManager.LoadScene("MainMenu");
    }
}
```

### Edge Cases
- **Player declines**: Continue button stays disabled, stuck on EULA screen until they accept
- **Offline mode**: EULA stored locally (PlayerPrefs), no server call needed
- **Terms update**: Bump version (`EULA_Accepted_v2`), re-prompt existing users on next launch
- **Under 13**: Add "Are you 13 or older?" checkbox (if No → "Ask parent to play")

### Changes to Tutorial-Flow.md
**Before**:
```
Step 1: Splash Screen → Main Menu
```

**After**:
```
Step 1A: Splash Screen (2 sec)
Step 1B: EULA/Privacy Acceptance (15-30 sec, one-time)
Step 2: Main Menu
```

---

## Gap 2: Card Pool Fallback Logic

### Problem
Tutorial gives 20 random cards, then asks player to build 11-card Balanced Explorer deck. **No guarantee those 20 cards include required cards** (1 Hero, 6 Units, 2 Buildings, 2 Tactics).

**Example failure**:
- Player draws 15 Units, 3 Buildings, 2 Heroes, 0 Tactics
- Balanced Explorer needs 2 Tactics → **Can't build deck!**

### Solution
**Guaranteed starter pool** with weighted draw + fallback grants.

**New Draw Logic**:
```
Phase 1: Guaranteed Cards (10 cards)
- 1× Epic Hero (Water Mage, fixed)
- 2× Rare Units (Knight, Healer)
- 4× Uncommon Units (Archer × 2, Scout × 2)
- 2× Uncommon Buildings (Granary, Watchtower)
- 1× Rare Tactic (Adaptive Strategy)

Phase 2: Random Cards (10 cards)
- 5× Rare or better (from starter pool)
- 5× Common/Uncommon (from starter pool)

Total: 20 cards with deck-building guaranteed
```

**If deck still can't be built** (edge case):
```
[Deck Builder screen]:
"Hmm, you need 2 more Units to build this deck."
[Button: "Get Missing Cards (Free)"]

→ System grants 2 free Common Units
→ Deck builder reloads with complete pool
```

### Rationale
- **No player frustration**: Can't get stuck unable to progress
- **Psychological safety**: Tutorial feels generous, not stingy
- **F2P friendly**: Free grants for tutorial only (not exploitable)
- **Industry standard**: All CCGs ensure first deck is buildable

### Industry Reference
- **Hearthstone**: Starter decks are pre-built (no deck building in tutorial)
- **Pokemon TCG**: Tutorial gives fixed 60-card deck, no randomness
- **Marvel Snap**: Random starter pool but **deck size auto-adjusts** (can't get stuck)

**Best Practice**: **Fixed guaranteed pool + random bonus** (hybrid approach)

### Implementation Notes
**Script**: `Scripts/Cards/StarterPackGenerator.cs`
```csharp
public List<CardData> GenerateStarterPack()
{
    List<CardData> pack = new List<CardData>();
    
    // Phase 1: Guaranteed cards (10)
    pack.Add(GetCard("water_mage")); // Epic Hero
    pack.Add(GetCard("knight"));
    pack.Add(GetCard("healer"));
    pack.Add(GetCard("archer"));
    pack.Add(GetCard("archer")); // Duplicate
    pack.Add(GetCard("scout"));
    pack.Add(GetCard("scout")); // Duplicate
    pack.Add(GetCard("granary"));
    pack.Add(GetCard("watchtower"));
    pack.Add(GetCard("adaptive_strategy"));
    
    // Phase 2: Random (10)
    for (int i = 0; i < 5; i++)
        pack.Add(GetRandomCard(Rarity.Rare)); // or better
    for (int i = 0; i < 5; i++)
        pack.Add(GetRandomCard(Rarity.Common, Rarity.Uncommon));
    
    return pack;
}

public void ValidateDeckBuildable(List<CardData> pool, DeckTemplate template)
{
    Dictionary<CardType, int> poolCount = CountCardTypes(pool);
    Dictionary<CardType, int> deckNeeds = template.GetRequirements();
    
    foreach (var requirement in deckNeeds)
    {
        CardType type = requirement.Key;
        int needed = requirement.Value;
        int available = poolCount[type];
        
        if (available < needed)
        {
            // Grant missing cards
            int missing = needed - available;
            for (int i = 0; i < missing; i++)
            {
                CardData freeCard = GetDefaultCard(type, Rarity.Common);
                pool.Add(freeCard);
            }
        }
    }
}
```

### Edge Cases
- **Player draws duplicate Epics**: Allow overflow, keep extras for later
- **Starter deck changes post-launch**: Version flag (`starter_pool_v2`) triggers re-grant
- **Exploits**: Fallback only triggers in tutorial (Level 0-1), not repeatable

### Changes to Tutorial-Flow.md
**Update Step 5**:
```markdown
**System Actions**:
1. Generate 20-card starter pool (10 guaranteed + 10 random)
2. Validate Balanced Explorer deck is buildable
3. If missing cards, auto-grant Common versions (silent, no UI)
4. Display 20 cards in grid
```

---

## Gap 3: Pack Opening Skip Behavior

### Problem
Tutorial shows 20 cards at 4 seconds each = **80 seconds of forced animation**. Players want to skip after seeing first pack (novelty worn off).

### Solution
**Progressive skip unlock** - First pack unskippable, rest skippable.

**Flow**:
```
Pack 1 (4 cards):
- Card 1: Full animation (4 sec) [No skip button]
- Card 2: Full animation (4 sec) [No skip button]
- Card 3: Full animation (4 sec) [No skip button]
- Card 4: Full animation (4 sec) [No skip button]
Total: 16 seconds

After Pack 1 completes:
[Button appears]: "Skip to Results" (bottom-right)

Pack 2-5 (16 cards):
- Option A: Watch animations (tap cards one-by-one)
- Option B: Tap "Skip to Results" → All 16 cards appear instantly in grid

Total time if skip: 16 sec (Pack 1) + 1 sec (Skip) = 17 seconds
Total time if watch: 16 sec + 64 sec = 80 seconds
```

### Rationale
- **Respect player time**: Veteran players skip, new players enjoy spectacle
- **First impression**: Force first pack to showcase animation quality
- **Psychological hook**: Seeing 1 Epic reveal builds excitement
- **Industry standard**: Most CCGs allow skip after first pack

### Industry Reference
- **Hearthstone**: No skip in tutorial, but normal packs have "Open All" button
- **Marvel Snap**: Instant reveal option in settings (default off)
- **Pokemon TCG**: "Skip" button appears after 2 cards in pack

**Best Practice**: **First pack mandatory, rest skippable** (Pokemon model)

### Implementation Notes
**Script**: `Scripts/UI/PackOpeningController.cs`
```csharp
private int packsOpened = 0;
public Button skipButton;

private IEnumerator RevealCards()
{
    foreach (var pack in allPacks) // 5 packs total
    {
        packsOpened++;
        
        // First pack: No skip
        if (packsOpened == 1)
        {
            skipButton.gameObject.SetActive(false);
            yield return RevealPackSlow(pack); // 4 cards × 4 sec
        }
        else
        {
            // Packs 2-5: Show skip button
            skipButton.gameObject.SetActive(true);
            skipButton.onClick.AddListener(SkipToResults);
            
            // If player clicks Skip, break loop
            if (playerClickedSkip)
                break;
            else
                yield return RevealPackSlow(pack);
        }
    }
    
    // If skipped, show all remaining cards instantly
    if (playerClickedSkip)
    {
        foreach (var remainingCard in remainingCards)
        {
            InstantReveal(remainingCard);
        }
    }
}
```

### Edge Cases
- **Skip during Epic reveal**: Always finish current card animation, then skip rest
- **Accidental skip**: Add confirmation dialog ("Skip remaining packs? [Yes] [No]")
- **Settings override**: Add setting "Always Skip Pack Animations" (disabled by default)

### Changes to Tutorial-Flow.md
**Update Step 6**:
```markdown
**Pack Opening Phases**:
1. Pack 1 (Cards 1-4): Full animation, no skip (16 sec)
2. "Skip to Results" button appears
3. Packs 2-5 (Cards 5-20): Skippable (1 sec if skip, 64 sec if watch)

**Design Decision**: First pack unskippable to showcase VFX
```

---

## Gap 4: Placement Undo Mechanics

### Problem
Tutorial asks player to manually place 11 cards on 7×7 grid. **What if they misplace a card and want to undo?** No undo = frustration.

### Solution
**"Reset Formation" button** before battle starts + drag-to-reposition.

**UI Elements**:
```
[Battle Placement Screen]
┌─────────────────────────────────────┐
│ Place Your Cards (11/11 placed)    │
│ [Battle Grid: 7×7]                  │
│                                     │
│ [Hand: Empty - all cards placed]   │
│                                     │
│ [Reset Formation] [Start Battle]   │
└─────────────────────────────────────┘
```

**Mechanics**:
1. **Drag-to-reposition**: Tap placed card → Drag to new tile → Releases, updates position
2. **Reset Formation**: Returns all cards to hand, clears grid (confirmation dialog)
3. **Auto-save**: Formation saved as player places (if they leave and return, cards still placed)

**Confirmation Dialog**:
```
"Reset formation and return all cards to hand?"
[Cancel] [Reset]
```

### Rationale
- **Player agency**: Let players experiment with formations
- **Tutorial safety**: Can't "fail" placement by misclicking
- **Matches map deployment**: County Map has "Cancel Deployment" for economy cards
- **Industry standard**: All tactics games allow undo before committing

### Industry Reference
- **XCOM**: Can reposition units before "End Turn"
- **Fire Emblem**: Undo button rewinds last action
- **Heroes of Might and Magic**: Can rearrange army before battle starts

**Best Practice**: **Drag-to-reposition + full reset button** (XCOM model)

### Implementation Notes
**Script**: `Scripts/Battle/PlacementManager.cs`
```csharp
public class PlacementManager : MonoBehaviour
{
    private Dictionary<CardData, Vector2Int> placedCards = new Dictionary<CardData, Vector2Int>();
    
    public void OnCardDragged(CardData card, Vector2Int newPosition)
    {
        // Check if tile is valid placement zone (player's 3 rows)
        if (IsValidPlacementZone(newPosition))
        {
            // If card already placed, remove old position
            if (placedCards.ContainsKey(card))
                placedCards.Remove(card);
            
            // Update new position
            placedCards[card] = newPosition;
            UpdateGridVisuals();
        }
    }
    
    public void OnResetFormationClicked()
    {
        // Show confirmation dialog
        ShowDialog("Reset formation?", () =>
        {
            // Return all cards to hand
            foreach (var card in placedCards.Keys)
            {
                ReturnToHand(card);
            }
            placedCards.Clear();
            UpdateGridVisuals();
        });
    }
}
```

### Edge Cases
- **Mid-drag cancel**: If player releases card on invalid tile, return to original position
- **Overlapping cards**: Highlight invalid tiles red, prevent placement
- **Reset during tutorial**: Tutorial text updates ("Try again! Place your Hero first.")

### Changes to Tutorial-Flow.md
**Update Step 15**:
```markdown
**UI Elements**:
- [Reset Formation] button (bottom-left, always visible)
- [Start Battle] button (bottom-right, enabled when 11/11 placed)
- Drag-to-reposition: Tap card → Drag → Release on new tile
```

---

## Gap 5: Enemy Turn Animation Speed

### Problem
Enemy AI turn takes 10-20 seconds (move 5 units, attack). **Players want faster combat.** No speed control = tedium.

### Solution
**Battle Speed settings** - 1×, 2×, 4×, Instant (unlocks after tutorial).

**Settings Menu**:
```
[Settings → Battle]
┌─────────────────────────────────────┐
│ Battle Speed:                       │
│ ◉ 1× Normal (default)               │
│ ○ 2× Fast                           │
│ ○ 4× Very Fast                      │
│ ○ Instant (no animations)           │
│                                     │
│ Note: Unlocks after first battle   │
└─────────────────────────────────────┘
```

**Animation Timing**:
| Speed | Movement | Attack | Death | Turn Time (5 units) |
|-------|----------|--------|-------|----------------------|
| 1×    | 1.0 sec  | 1.5 sec| 1.0 sec| 20 seconds          |
| 2×    | 0.5 sec  | 0.75 sec| 0.5 sec| 10 seconds         |
| 4×    | 0.25 sec | 0.4 sec| 0.25 sec| 5 seconds          |
| Instant| 0 sec   | 0 sec  | 0 sec | 1 second (teleport) |

### Rationale
- **Player preference**: Some love animations, some want efficiency
- **Respects time**: Veterans can blitz through battles
- **Tutorial pacing**: Force 1× for first battle (learn mechanics), unlock 2×/4× after
- **Competitive advantage**: PvP uses 1× only (no speed advantage)

### Industry Reference
- **Fire Emblem**: Battle animation toggle (On/Off)
- **Pokemon**: "Fast mode" in settings (2× animations)
- **Auto Chess**: Speed slider 1×/2×/4× during battles

**Best Practice**: **Graduated speed options** (Pokemon + Auto Chess model)

### Implementation Notes
**Script**: `Scripts/Battle/AnimationSpeedManager.cs`
```csharp
public enum BattleSpeed { Normal = 1, Fast = 2, VeryFast = 4, Instant = 0 }

public class AnimationSpeedManager : MonoBehaviour
{
    public static BattleSpeed CurrentSpeed = BattleSpeed.Normal;
    
    public static float GetAnimationDuration(float baseTime)
    {
        if (CurrentSpeed == BattleSpeed.Instant)
            return 0f;
        else
            return baseTime / (int)CurrentSpeed;
    }
    
    // Usage:
    // float moveDuration = AnimationSpeedManager.GetAnimationDuration(1.0f);
    // LeanTween.move(unit, targetPos, moveDuration);
}
```

**PlayerPrefs Storage**:
```csharp
PlayerPrefs.SetInt("Battle_Speed", (int)BattleSpeed.Fast); // 1, 2, 4, or 0
```

### Edge Cases
- **Instant mode readability**: Show damage numbers longer (1 sec) even if animation is 0 sec
- **Tutorial override**: First battle forced to 1× (ignore settings)
- **PvP fairness**: Disable speed settings in PvP (both players see 1×)

### Changes to Tutorial-Flow.md
**Add to Step 28 (Tutorial Complete)**:
```markdown
**Unlocked Settings**:
- Battle Speed (1×/2×/4×/Instant)
- Auto-Battle Toggle
```

---

## Gap 6: Card Reward Destination

### Problem
After battle, player gets +1 card reward. **Where does it go?** Auto-add to Codex (invisible) or prompt player to choose?

### Solution
**Auto-add to Codex + notification** (no interruption, show in post-battle summary).

**Victory Screen**:
```
┌─────────────────────────────────────┐
│ 🎉 VICTORY! 🎉                      │
│                                     │
│ Rewards:                            │
│ +100 XP                             │
│ +500 Gold                           │
│                                     │
│ New Card Acquired:                  │
│ [Card visual: Forest Ranger]        │
│ (Auto-added to Codex)               │
│                                     │
│ [View Codex] [Continue]             │
└─────────────────────────────────────┘
```

**No interruption** - Player can tap [Continue] without managing deck.

**Optional**: Tap [View Codex] → See full collection with new card highlighted (gold border).

### Rationale
- **No friction**: Don't interrupt victory high with deck management
- **Transparency**: Player sees what they got (not hidden)
- **Codex is the hub**: All card management happens in Codex, not mid-battle
- **Industry standard**: Most CCGs auto-add rewards, show in collection later

### Industry Reference
- **Hearthstone**: All pack cards auto-add to collection, "New!" badge in Collection
- **Marvel Snap**: Cards auto-unlock, notification popup (can tap to view or skip)
- **Pokemon TCG**: Reward cards auto-add, shown in post-match summary

**Best Practice**: **Auto-add + notification + Codex highlight** (Hearthstone model)

### Implementation Notes
**Script**: `Scripts/Rewards/RewardManager.cs`
```csharp
public void GrantBattleReward()
{
    CardData rewardCard = GetRandomCard(Rarity.Common);
    
    // Add to player collection
    CardManager.Instance.playerCollection.AddCard(rewardCard);
    
    // Mark as "New" for Codex UI
    PlayerPrefs.SetInt($"Card_{rewardCard.cardId}_New", 1);
    
    // Show in victory screen
    VictoryScreen.Instance.DisplayRewardCard(rewardCard);
}
```

**Codex UI**:
```csharp
public void DisplayCardInCodex(CardData card)
{
    // If card is new, show gold border
    bool isNew = PlayerPrefs.GetInt($"Card_{card.cardId}_New", 0) == 1;
    if (isNew)
    {
        cardVisual.border.color = Color.gold;
        cardVisual.newBadge.SetActive(true);
    }
}
```

### Edge Cases
- **Duplicate cards**: Show count (e.g., "Forest Ranger (×3)")
- **Codex full**: No limit on collection size (scale-up grid)
- **Player never opens Codex**: "New!" badges stay until viewed

### Changes to Tutorial-Flow.md
**Update Step 23 (Victory Screen)**:
```markdown
**Rewards Display**:
- +100 XP, +500 Gold
- +1 Common Card (auto-added to Codex, highlighted with "New!" badge)
- [View Codex] button (optional)
- [Continue] button (returns to County Map)
```

---

## Gap 7: Auto-Battle Loss Handling

### Problem
After first battle, player unlocks Auto-Battle (AI plays for them). **What if they lose?** Retry as manual or auto-retry?

### Solution
**Auto-retry once, then offer manual retry** (smart fallback).

**Flow**:
```
Player enables Auto-Battle → Taps enemy
↓
Auto-Battle runs (5-10 seconds)
↓
Result: DEFEAT
↓
[Auto-Battle Defeat Screen]:
"Your army was defeated!"
- Casualties: 3 units lost
- XP penalty: -10 XP

Auto-retry? (1 free retry)
[Try Again (Auto)] [Fight Manually]
```

**Auto-retry logic**:
- First loss: Auto-retry once (free, no penalty)
- Second loss: Force manual battle or retreat

**If player retreats**:
```
"Retreat and heal your army?"
- No casualties (units restored)
- No XP loss
- Can retry later
[Retreat] [Fight Manually]
```

### Rationale
- **Forgiving**: One free retry prevents frustration
- **Learning opportunity**: Manual mode teaches tactics if auto fails
- **No death spiral**: Retreat prevents losing all units
- **Industry standard**: Most idle games have retry mechanics

### Industry Reference
- **AFK Arena**: Auto-retry up to 3 times, then manual option
- **Idle Heroes**: Infinite auto-retries (no penalty)
- **Fire Emblem**: Manual only (no auto-battle)

**Best Practice**: **1 free auto-retry, then manual fallback** (AFK Arena lite model)

### Implementation Notes
**Script**: `Scripts/Battle/AutoBattleManager.cs`
```csharp
private int autoRetryCount = 0;

public void OnAutoBattleDefeat()
{
    if (autoRetryCount < 1)
    {
        // Free retry
        autoRetryCount++;
        ShowDialog("Auto-Battle failed! Retry?", () =>
        {
            RestartAutoBattle();
        });
    }
    else
    {
        // Force manual or retreat
        ShowDialog("Auto-Battle failed twice!", 
            onManual: () => StartManualBattle(),
            onRetreat: () => RetreatFromBattle()
        );
    }
}

private void RetreatFromBattle()
{
    // Restore units, no penalties
    RestorePlayerArmy();
    SceneManager.LoadScene("CountyMap");
}
```

### Edge Cases
- **Player spams auto-retry**: Cap at 1 free retry per battle (not per session)
- **Tutorial battles**: Unlosable (auto-battle always wins)
- **Boss battles**: Disable auto-battle (force manual for challenge)

### Changes to Tutorial-Flow.md
**Update Step 24 (Auto-Battle Unlock)**:
```markdown
**Auto-Battle Mechanics**:
- Toggle on County Map (before entering battle)
- Runs instantly (5-10 sec simulation)
- 1 free retry if defeated
- After 2nd defeat: Manual battle or Retreat
```

---

## Gap 8: Economy Card Deployment Full Flow

### Problem
Tutorial mentions deploying economy cards on resource nodes but doesn't define **retrieval, income display, time cost, tile limits**.

### Solution
**Deploy → Generate → Retrieve** cycle with time-based collection.

**Full Flow**:
```
Step 1: Discover Resource Node (Gold Mine)
↓
[County Map Tile: Gold Mine icon (yellow)]
Player taps tile → "Gold Mine discovered!"
↓
Step 2: Deploy Economy Card
↓
[Deployment Menu]:
Available Economy Cards:
- Granary (Food production, doesn't match Gold)
- Mine (Gold production, MATCHES!)

[Player selects Mine card]
"Deploy Mine on Gold Mine?"
[Deploy] [Cancel]
↓
Step 3: Mine Deployed
↓
[Tile visual changes]:
- Gold Mine + Mine building icon
- Timer: "0/60 min" (production starts)
- Income: "+100 Gold/hour"

[Mine card removed from deck]
(Stays on tile until retrieved)
↓
Step 4: Wait for Production (AFK)
↓
[Player returns 30 min later]
[Tile visual]:
- Timer: "30/60 min"
- Accumulated: +50 Gold (ready to collect)
↓
Step 5: Collect Income
↓
[Player taps tile]:
"Collect +50 Gold?"
[Collect] [Wait for Full (60 min)]

[Player taps Collect]:
- +50 Gold added to inventory
- Timer resets to 0/60 min
- Production continues
↓
Step 6: Retrieve Building (Optional)
↓
[Player taps tile]:
[Building Menu]:
- Collect Income: +100 Gold (60 min elapsed)
- Retrieve Building (returns Mine card to deck)

[Player taps Retrieve]:
"Retrieve Mine building?"
- Stops production
- Returns Mine card to deck
- Tile returns to empty Gold Mine

[Retrieve] [Cancel]
```

### Rationale
- **AFK progression**: Passive income respects player time
- **Strategic choice**: Deploy Mine for income OR keep in deck for battles
- **Retrieval mechanic**: Prevents permanent card loss, allows redeployment
- **Time-based**: Encourages daily logins (Clash of Clans model)

### Industry Reference
- **Clash of Clans**: Buildings produce resources over time, no retrieval (permanent)
- **Fallout Shelter**: Rooms generate resources, tap to collect
- **Idle Champions**: Heroes auto-generate gold, no manual collection

**Best Practice**: **Tap-to-collect + optional retrieval** (Fallout Shelter + retrieval twist)

### Implementation Notes
**Script**: `Scripts/Economy/ResourceNodeController.cs`
```csharp
public class ResourceNode : MonoBehaviour
{
    public ResourceType resourceType; // Gold, Food, Stone
    public CardData deployedCard; // Economy card on this tile
    public float productionRate; // 100 gold/hour
    public float accumulatedIncome; // How much gold is waiting
    public DateTime deployTime; // When building was placed
    
    public void DeployBuilding(CardData economyCard)
    {
        deployedCard = economyCard;
        deployTime = DateTime.UtcNow;
        productionRate = economyCard.incomeRate; // 100/hour
        
        // Remove from player deck
        PlayerDeck.Instance.activeDeck.Remove(economyCard);
    }
    
    public void CollectIncome()
    {
        // Calculate time elapsed
        TimeSpan elapsed = DateTime.UtcNow - deployTime;
        float hours = (float)elapsed.TotalHours;
        
        accumulatedIncome = productionRate * hours;
        
        // Grant income
        PlayerResources.Instance.AddGold((int)accumulatedIncome);
        
        // Reset timer
        deployTime = DateTime.UtcNow;
        accumulatedIncome = 0;
    }
    
    public void RetrieveBuilding()
    {
        // Collect final income
        CollectIncome();
        
        // Return card to deck
        PlayerDeck.Instance.activeDeck.Add(deployedCard);
        
        // Clear tile
        deployedCard = null;
    }
}
```

### Edge Cases
- **Offline income cap**: Max 12 hours of production (prevents infinite AFK)
- **Multiple buildings on 1 tile**: Not allowed (1 tile = 1 building)
- **Building destroyed**: If tile is conquered in PvP, building returns to deck (no loss)
- **No matching building**: Can deploy ANY economy card, but mismatched types give 50% income

### Changes to Tutorial-Flow.md
**Update Step 27 (Economy Deployment)**:
```markdown
**Economy Deployment Flow**:
1. Discover Gold Mine (resource node)
2. Deploy Mine card (matches Gold resource type)
3. Production starts: +100 Gold/hour (background)
4. Collect income: Tap tile → +Gold (can collect partial or wait for full)
5. Retrieve building: Tap tile → Retrieve → Card returns to deck
6. Offline income cap: 12 hours max (prevents infinite AFK)
```

---

## Gap 9: Tutorial Failure Recovery

### Problem
Tutorial's first battle is designed to be **unlosable** (player has 11 cards, enemy has 3 weak cards). But what if a bug causes a loss, or player force-quits mid-battle?

### Solution
**"Try Again" resurrection** (free for first 3 battles) + force-win fallback.

**Scenario 1: Player Loses Tutorial Battle** (impossible but handle it):
```
[Defeat Screen]:
"Defeat... but every hero stumbles once."

"Try Again?"
[Resurrect (Free)] [Retreat]

[Player taps Resurrect]:
- All units restored to full HP
- Battle restarts from placement phase
- Tutorial text: "Let's adjust your formation!"
```

**Scenario 2: Player Force-Quits Mid-Battle**:
```
[On relaunch]:
"Welcome back! Your battle is still in progress."

[Resume Battle] [Retreat to County Map]

[If player retreats]:
- No penalties (units restored, no XP loss)
- Can retry battle later
```

**Scenario 3: Player Loses 3 Times** (extremely unlikely):
```
[After 3rd defeat]:
"This battle seems tough. Let's skip it for now."

[Auto-Win]:
- Player granted victory rewards (XP, gold, cards)
- Tutorial advances to next step
- Analytics flag: "Tutorial_AutoWin_Triggered" (investigate bug)
```

### Rationale
- **Zero frustration**: Tutorial should NEVER block progress
- **Debug safety**: If balance is broken, player can still advance
- **Analytics insight**: Track auto-wins to detect bugs
- **Industry standard**: Most tutorials have failsafes

### Industry Reference
- **Pokemon**: Tutorial battles are scripted (opponent always uses weak moves)
- **Fire Emblem**: "Casual Mode" allows unlimited retries (no permadeath)
- **Hearthstone**: Tutorial opponents follow scripted AI (can't lose unless you AFK)

**Best Practice**: **Free retries + auto-win failsafe** (Pokemon + Fire Emblem hybrid)

### Implementation Notes
**Script**: `Scripts/Battle/TutorialBattleManager.cs`
```csharp
private int tutorialRetryCount = 0;

public void OnPlayerDefeated()
{
    if (BattleManager.Instance.isTutorialBattle)
    {
        tutorialRetryCount++;
        
        if (tutorialRetryCount <= 3)
        {
            // Free retry
            ShowDialog("Try again? (Free resurrection)", () =>
            {
                RestartBattle();
            });
        }
        else
        {
            // Auto-win failsafe
            Analytics.LogEvent("Tutorial_AutoWin_Triggered");
            
            ShowDialog("Let's skip this battle.", () =>
            {
                GrantVictoryRewards();
                SceneManager.LoadScene("CountyMap");
            });
        }
    }
}
```

### Edge Cases
- **Player intentionally loses**: Still counts as retry (max 3)
- **Bug causes infinite loop**: Auto-win after 10 minutes of battle time
- **Player retreats**: Doesn't count as retry, can re-enter battle

### Changes to Tutorial-Flow.md
**Add to Step 23 (Victory Screen)**:
```markdown
**Tutorial Safety Nets**:
- If defeated: Free resurrection (max 3 times)
- If force-quit: Resume battle or retreat (no penalties)
- If defeated 3× (impossible): Auto-win granted, analytics flag triggered
```

---

## Summary: Updates Needed

### Tutorial-Flow.md Changes
1. **Step 1A**: Add EULA/Privacy acceptance screen (15-30 sec)
2. **Step 5**: Update card draw logic (10 guaranteed + 10 random)
3. **Step 6**: Add "Skip to Results" button after Pack 1
4. **Step 15**: Add "Reset Formation" button + drag-to-reposition
5. **Step 17-22**: Note battle speed (1× forced for tutorial, unlocks after)
6. **Step 23**: Clarify reward cards auto-add to Codex (no interruption)
7. **Step 24**: Add auto-battle retry logic (1 free retry, then manual)
8. **Step 27**: Add full economy deployment flow (deploy → collect → retrieve)
9. **Step 23**: Add tutorial safety nets (free resurrection × 3)

### New Schema Files Needed
1. **pack-schema.json**: Define pack structure (cards per pack, rarity weights)
2. **starter-deck-schema.json**: Define guaranteed cards + fallback logic
3. **economy-node-schema.json**: Define resource nodes, production rates, deployment

### Existing Schema Updates
1. **tutorial-schema.json**: Add EULA step, deployment flow, safety nets
2. **battle-schema.json**: Add placement undo, speed settings
3. **card-schema.json**: Add `incomeRate` field for economy cards

### Game-Bible.md Updates
1. **Section 2.5 (Onboarding)**: Reference tutorial-flow.md for details (reduce bible bloat)
2. **Section 2.3 (Economy Cards)**: Add deployment/retrieval mechanics
3. **Section 3.3 (Battle)**: Add speed settings, placement undo

---

**All 9 gaps resolved!** Ready to implement in Unity or update documentation.
