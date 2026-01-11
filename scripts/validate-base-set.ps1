# Base Set Validation Script
# Purpose: Validate all Base Set cards, products, and references
# Run this before committing changes to ensure data integrity

param(
    [switch]$Verbose = $false
)

$ErrorCount = 0
$WarningCount = 0

function Write-ValidationError {
    param([string]$Message)
    Write-Host "❌ ERROR: $Message" -ForegroundColor Red
    $script:ErrorCount++
}

function Write-ValidationWarning {
    param([string]$Message)
    Write-Host "⚠️  WARNING: $Message" -ForegroundColor Yellow
    $script:WarningCount++
}

function Write-ValidationSuccess {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host " Base Set Validation Script" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ==========================
# 1. Validate Card List
# ==========================
Write-Host "📋 Validating Complete Card List..." -ForegroundColor Cyan

$cardListPath = "c:\Soverign-Territories\soverign-territories\docs\codex\base-set\COMPLETE-CARD-LIST.md"
if (-not (Test-Path $cardListPath)) {
    Write-ValidationError "COMPLETE-CARD-LIST.md not found at $cardListPath"
} else {
    $cardListContent = Get-Content $cardListPath -Raw
    
    # Count collection numbers
    $collectionNumbers = [regex]::Matches($cardListContent, 'BS-(\d{3})')
    $uniqueNumbers = $collectionNumbers | ForEach-Object { $_.Value } | Sort-Object -Unique
    
    if ($uniqueNumbers.Count -ne 140) {
        Write-ValidationError "Expected 140 unique collection numbers, found $($uniqueNumbers.Count)"
    } else {
        Write-ValidationSuccess "All 140 collection numbers present (BS-001 to BS-140)"
    }
    
    # Check for gaps
    for ($i = 1; $i -le 140; $i++) {
        $expected = "BS-{0:D3}" -f $i
        if ($uniqueNumbers -notcontains $expected) {
            Write-ValidationError "Missing collection number: $expected"
        }
    }
    
    # Validate rarity distribution
    $rarityMatches = @{
        Common = ([regex]::Matches($cardListContent, '\| Common \|')).Count
        Uncommon = ([regex]::Matches($cardListContent, '\| Uncommon \|')).Count
        Rare = ([regex]::Matches($cardListContent, '\| Rare \|')).Count
        Epic = ([regex]::Matches($cardListContent, '\| Epic \|')).Count
        Legendary = ([regex]::Matches($cardListContent, '\| Legendary \|')).Count
    }
    
    $expectedRarities = @{
        Common = 56
        Uncommon = 42
        Rare = 25
        Epic = 12
        Legendary = 4
    }
    
    foreach ($rarity in $expectedRarities.Keys) {
        $actual = $rarityMatches[$rarity]
        $expected = $expectedRarities[$rarity]
        if ($actual -ne $expected) {
            Write-ValidationError "Rarity mismatch: $rarity (expected $expected, found $actual)"
        } else {
            Write-ValidationSuccess "Rarity distribution correct: $rarity = $actual cards"
        }
    }
}

# ==========================
# 2. Validate Products
# ==========================
Write-Host ""
Write-Host "📦 Validating Products..." -ForegroundColor Cyan

$productsPath = "c:\Soverign-Territories\soverign-territories\docs\products"

# Validate starter boxes
$starterBoxes = @("fire-starter-box.json", "water-starter-box.json", "earth-starter-box.json")
foreach ($box in $starterBoxes) {
    $boxPath = Join-Path $productsPath "boxes\$box"
    if (-not (Test-Path $boxPath)) {
        Write-ValidationError "Missing starter box: $box"
    } else {
        $boxData = Get-Content $boxPath -Raw | ConvertFrom-Json
        
        # Validate fixed contents
        if ($boxData.totalCards -ne 15) {
            Write-ValidationError "$box: Expected 15 cards, found $($boxData.totalCards)"
        } else {
            Write-ValidationSuccess "$box: Contains 15 cards"
        }
        
        # Validate all card references exist in card list
        foreach ($card in $boxData.fixedContents) {
            if (-not ($cardListContent -match $card.collectionNumber)) {
                Write-ValidationError "$box: References non-existent card $($card.collectionNumber)"
            }
        }
    }
}

# Validate packs
$packs = @(
    "welcome-pack.json",
    "standard-pack.json",
    "element-booster-fire.json",
    "element-booster-water.json",
    "element-booster-earth.json",
    "hero-pack.json",
    "rare-pack.json",
    "epic-pack.json",
    "legendary-pack.json",
    "mythic-pack.json"
)

foreach ($pack in $packs) {
    $packPath = Join-Path $productsPath "packs\$pack"
    if (-not (Test-Path $packPath)) {
        Write-ValidationError "Missing pack: $pack"
    } else {
        $packData = Get-Content $packPath -Raw | ConvertFrom-Json
        
        # Validate basic structure
        if (-not $packData.productId) {
            Write-ValidationError "$pack: Missing productId"
        }
        if (-not $packData.cardsPerPack) {
            Write-ValidationError "$pack: Missing cardsPerPack"
        }
        
        # Validate rarity distribution adds up to reasonable percentage
        $totalWeight = 0
        foreach ($rarity in $packData.rarityDistribution.PSObject.Properties) {
            $totalWeight += $rarity.Value.weight
        }
        
        if ($totalWeight -lt 95 -or $totalWeight -gt 105) {
            Write-ValidationWarning "$pack: Rarity distribution weights sum to $totalWeight% (expected ~100%)"
        }
        
        Write-ValidationSuccess "$pack: Structure valid"
    }
}

Write-ValidationSuccess "All 10 packs validated"

# ==========================
# 3. Validate Infrastructure
# ==========================
Write-Host ""
Write-Host "🏗️  Validating Infrastructure..." -ForegroundColor Cyan

$codexPath = "c:\Soverign-Territories\soverign-territories\docs\codex"

# Check schema
$schemaPath = Join-Path $codexPath "_schema.json"
if (-not (Test-Path $schemaPath)) {
    Write-ValidationError "Missing card schema: _schema.json"
} else {
    Write-ValidationSuccess "Card schema present"
}

# Check series manifest
$manifestPath = Join-Path $codexPath "base-set\series-manifest.json"
if (-not (Test-Path $manifestPath)) {
    Write-ValidationError "Missing series manifest: base-set/series-manifest.json"
} else {
    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.totalCards -ne 140) {
        Write-ValidationError "Manifest totalCards mismatch (expected 140, found $($manifest.totalCards))"
    } else {
        Write-ValidationSuccess "Series manifest valid (140 cards)"
    }
}

# Check README files
$readmes = @(
    "codex\README.md",
    "products\README.md"
)

foreach ($readme in $readmes) {
    $readmePath = Join-Path "c:\Soverign-Territories\soverign-territories\docs" $readme
    if (-not (Test-Path $readmePath)) {
        Write-ValidationWarning "Missing documentation: $readme"
    } else {
        Write-ValidationSuccess "Documentation present: $readme"
    }
}

# ==========================
# 4. Summary
# ==========================
Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host " Validation Summary" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($ErrorCount -eq 0 -and $WarningCount -eq 0) {
    Write-Host "🎉 ALL VALIDATIONS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Card List: 140 cards (BS-001 to BS-140)"
    Write-Host "✅ Rarity Distribution: Correct (56 Common, 42 Uncommon, 25 Rare, 12 Epic, 4 Legendary)"
    Write-Host "✅ Products: 3 starter boxes + 10 packs"
    Write-Host "✅ Infrastructure: Schema, manifest, documentation"
    Write-Host ""
    Write-Host "🚀 Ready to commit and proceed with implementation!"
    exit 0
} elseif ($ErrorCount -eq 0) {
    Write-Host "⚠️  VALIDATION PASSED WITH WARNINGS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Warnings: $WarningCount" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Review warnings above before committing."
    exit 0
} else {
    Write-Host "❌ VALIDATION FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Errors: $ErrorCount" -ForegroundColor Red
    Write-Host "Warnings: $WarningCount" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Fix errors above before committing."
    exit 1
}
