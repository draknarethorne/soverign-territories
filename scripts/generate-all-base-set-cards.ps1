# Base Set Complete Card Generation Script
# Purpose: Generate full JSON files for all 140 Base Set cards from the master card list
# Source: docs/codex/base-set/COMPLETE-CARD-LIST.md
# Output: Individual JSON files in docs/codex/base-set/{element}/CARD_ID.json

# Import card list data
$cardListPath = "c:\Soverign-Territories\soverign-territories\docs\codex\base-set\COMPLETE-CARD-LIST.md"
$outputBasePath = "c:\Soverign-Territories\soverign-territories\docs\codex\base-set"

# Helper function to generate card JSON
function New-CardJson {
    param(
        [string]$CardId,
        [string]$CollectionNumber,
        [string]$Name,
        [string]$Type,
        [string]$Element,
        [string]$Rarity,
        [int]$Health,
        [int]$Mana,
        [int]$Attack,
        [int]$Defense,
        [int]$MoveRange,
        [int]$AttackRange,
        [string]$PrimaryAbility,
        [string]$SecondaryAbility,
        [string]$Lore,
        [bool]$Flying = $false
    )

    $rarityMap = @{
        "Common" = @{ tier = "Common"; stars = 0; points = 1 }
        "Uncommon" = @{ tier = "Uncommon"; stars = 1; points = 1 }
        "Rare" = @{ tier = "Rare"; stars = 2; points = 4 }
        "Epic" = @{ tier = "Epic"; stars = 3; points = 8 }
        "Legendary" = @{ tier = "Legendary"; stars = 5; points = 16 }
    }

    $card = @{
        cardId = $CardId
        collectionNumber = $CollectionNumber
        series = @{
            seriesId = "base-set"
            seriesName = "Base Set"
            cardNumber = [int]($CollectionNumber -replace "BS-", "")
            totalCards = 140
        }
        name = $Name
        type = $Type
        element = $Element
        rarity = $rarityMap[$Rarity]
        stats = @{
            health = $Health
            mana = $Mana
            attack = $Attack
            defense = $Defense
            moveRange = $MoveRange
            attackRange = $AttackRange
        }
        abilities = @()
        tacticSlots = if ($Type -eq "Hero") { 3 } else { 0 }
        lore = $Lore
        art = @{
            portraitAsset = "Art/Cards/$CollectionNumber`_Portrait.png"
            fullArtAsset = "Art/Cards/$CollectionNumber`_FullArt.png"
            shinyPortrait = "Art/Cards/$CollectionNumber`_Portrait_Shiny.png"
            voicelineActor = "TBD"
        }
        acquisition = @{
            packSources = @("standard-pack")
            campaignDrops = @()
            dailyLoginRewards = @()
        }
        meta = @{
            designNotes = "Base Set card - generated from master list"
            balanceHistory = @()
        }
    }

    if ($Flying) {
        $card.stats.flying = $true
    }

    if ($PrimaryAbility) {
        # Parse ability from string (simplified - full parser would be more complex)
        $card.abilities += @{
            abilityId = "$CardId`_ABILITY_1"
            name = $PrimaryAbility
            type = "Active"
            manaCost = 25
            cooldown = 3
            description = "Primary ability - see design notes for details"
        }
    }

    return $card | ConvertTo-Json -Depth 10
}

# Example usage (Fire element heroes)
$fireHeroes = @(
    @{
        CardId = "HERO_ARIA_FLAME_KNIGHT"
        CollectionNumber = "BS-001"
        Name = "Aria, Flame Knight"
        Type = "Hero"
        Element = "Fire"
        Rarity = "Epic"
        Health = 80; Mana = 60; Attack = 45; Defense = 12; MoveRange = 3; AttackRange = 1
        PrimaryAbility = "Blazing Strike"
        SecondaryAbility = "Inferno Aura"
        Lore = "A legendary warrior who commands the eternal flames of the Ashen Citadel."
    },
    @{
        CardId = "HERO_RAGNAR_INFERNO_BERSERKER"
        CollectionNumber = "BS-002"
        Name = "Ragnar, Inferno Berserker"
        Type = "Hero"
        Element = "Fire"
        Rarity = "Rare"
        Health = 70; Mana = 50; Attack = 50; Defense = 8; MoveRange = 4; AttackRange = 1
        PrimaryAbility = "Rage Strike"
        Lore = "A fierce berserker whose rage fuels his attacks, growing stronger with each kill."
    },
    @{
        CardId = "HERO_CINDER_FLAME_MAGE"
        CollectionNumber = "BS-003"
        Name = "Cinder, Flame Mage"
        Type = "Hero"
        Element = "Fire"
        Rarity = "Uncommon"
        Health = 50; Mana = 80; Attack = 30; Defense = 10; MoveRange = 2; AttackRange = 3
        PrimaryAbility = "Flame Bolt"
        Lore = "A master of flame magic, raining fire upon enemies from afar."
    },
    @{
        CardId = "HERO_BLAZE_DRAGON_RIDER"
        CollectionNumber = "BS-004"
        Name = "Blaze, Dragon Rider"
        Type = "Hero"
        Element = "Fire"
        Rarity = "Legendary"
        Health = 100; Mana = 70; Attack = 60; Defense = 20; MoveRange = 5; AttackRange = 1
        PrimaryAbility = "Dragon Breath"
        Lore = "Commander of the legendary fire drakes, feared across the Sovereign Realms."
        Flying = $true
    },
    @{
        CardId = "HERO_EMBER_PHOENIX_GUARDIAN"
        CollectionNumber = "BS-005"
        Name = "Ember, Phoenix Guardian"
        Type = "Hero"
        Element = "Fire"
        Rarity = "Epic"
        Health = 75; Mana = 65; Attack = 40; Defense = 18; MoveRange = 3; AttackRange = 1
        PrimaryAbility = "Phoenix Rebirth"
        Lore = "Blessed by the eternal phoenix, she rises from death once per battle."
    }
)

# Generate Fire heroes (example - full script would iterate all 140 cards)
foreach ($hero in $fireHeroes) {
    $json = New-CardJson @hero
    $elementFolder = $hero.Element.ToLower()
    $outputPath = Join-Path $outputBasePath "$elementFolder\$($hero.CardId).json"

    # Create directory if not exists
    $dir = Split-Path $outputPath -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    # Write JSON file
    Set-Content -Path $outputPath -Value $json -Encoding UTF8
    Write-Host "✅ Generated: $($hero.CollectionNumber) - $($hero.Name)"
}

Write-Host ""
Write-Host "🔥 Fire heroes generated (5/140 cards)"
Write-Host "📋 Next: Run full generation for all elements (Water, Earth, Lightning, Wind, Frost, Neutral)"
Write-Host "📂 Output: docs/codex/base-set/{element}/CARD_ID.json"
Write-Host ""
Write-Host "To generate all 140 cards, expand this script with:"
Write-Host "  - Water (25 cards, BS-026 to BS-050)"
Write-Host "  - Earth (25 cards, BS-051 to BS-075)"
Write-Host "  - Lightning (15 cards, BS-076 to BS-090)"
Write-Host "  - Wind (15 cards, BS-091 to BS-105)"
Write-Host "  - Frost (15 cards, BS-106 to BS-120)"
Write-Host "  - Neutral (20 cards, BS-121 to BS-140)"
