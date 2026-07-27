# Migrate Project Structure - Phase 1-3
# Separates runtime data from documentation

Write-Host "=== Sovereign Territories Structure Migration ===" -ForegroundColor Cyan
Write-Host "Phase 1-3: Create new structure, copy files, update references`n" -ForegroundColor Yellow

# Phase 1: Create New Directory Structure
Write-Host "[Phase 1] Creating new directory structure..." -ForegroundColor Green

$directories = @(
    "data/cards/base-set/heroes",
    "data/cards/base-set/units",
    "data/cards/base-set/tactics",
    "data/cards/base-set/buildings",
    "data/products/packs",
    "data/products/boxes",
    "data/products/rewards",
    "data/progression",
    "data/balance",
    "data/manifests",
    "tools/validators",
    "tools/generators",
    "tools/importers"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    } else {
        Write-Host "  Exists: $dir" -ForegroundColor DarkGray
    }
}

# Phase 2: Copy Files to New Structure
Write-Host "`n[Phase 2] Copying files to new structure..." -ForegroundColor Green

# Copy card JSONs (organized by type)
if (Test-Path "docs/codex/base-set/cards") {
    Write-Host "  Copying card files..." -ForegroundColor Gray

    Get-ChildItem "docs/codex/base-set/cards/hero-*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName -Destination "data/cards/base-set/heroes/" -Force
        Write-Host "    → $($_.Name) → heroes/" -ForegroundColor DarkGray
    }

    Get-ChildItem "docs/codex/base-set/cards/unit-*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName -Destination "data/cards/base-set/units/" -Force
        Write-Host "    → $($_.Name) → units/" -ForegroundColor DarkGray
    }

    Get-ChildItem "docs/codex/base-set/cards/tactic-*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName -Destination "data/cards/base-set/tactics/" -Force
        Write-Host "    → $($_.Name) → tactics/" -ForegroundColor DarkGray
    }

    Get-ChildItem "docs/codex/base-set/cards/building-*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName -Destination "data/cards/base-set/buildings/" -Force
        Write-Host "    → $($_.Name) → buildings/" -ForegroundColor DarkGray
    }
}

# Copy product files
if (Test-Path "docs/products/packs") {
    Write-Host "  Copying pack files..." -ForegroundColor Gray
    Copy-Item "docs/products/packs/*.json" -Destination "data/products/packs/" -Force
    $packCount = (Get-ChildItem "data/products/packs/*.json").Count
    Write-Host "    → $packCount pack files copied" -ForegroundColor DarkGray
}

if (Test-Path "docs/products/boxes") {
    Write-Host "  Copying box files..." -ForegroundColor Gray
    Copy-Item "docs/products/boxes/*.json" -Destination "data/products/boxes/" -Force
    $boxCount = (Get-ChildItem "data/products/boxes/*.json").Count
    Write-Host "    → $boxCount box files copied" -ForegroundColor DarkGray
}

if (Test-Path "docs/products/rewards") {
    Write-Host "  Copying reward files..." -ForegroundColor Gray
    Copy-Item "docs/products/rewards/*.json" -Destination "data/products/rewards/" -Force
    $rewardCount = (Get-ChildItem "data/products/rewards/*.json").Count
    Write-Host "    → $rewardCount reward files copied" -ForegroundColor DarkGray
}

# Copy manifest files
if (Test-Path "docs/codex/base-set/BASE_SET_MASTER_CARDS.json") {
    Write-Host "  Copying manifest files..." -ForegroundColor Gray
    Copy-Item "docs/codex/base-set/BASE_SET_MASTER_CARDS.json" -Destination "data/manifests/" -Force
    Write-Host "    → BASE_SET_MASTER_CARDS.json" -ForegroundColor DarkGray
}

if (Test-Path "docs/codex/base-set/series-manifest.json") {
    Copy-Item "docs/codex/base-set/series-manifest.json" -Destination "data/manifests/" -Force
    Write-Host "    → series-manifest.json" -ForegroundColor DarkGray
}

# Move build scripts to tools/
if (Test-Path "scripts") {
    Write-Host "  Moving build scripts to tools/..." -ForegroundColor Gray
    Copy-Item "scripts/*.ps1" -Destination "tools/generators/" -Force
    $scriptCount = (Get-ChildItem "tools/generators/*.ps1").Count
    Write-Host "    → $scriptCount scripts moved" -ForegroundColor DarkGray
}

# Phase 3: Summary
Write-Host "`n[Phase 3] Migration Summary" -ForegroundColor Green

$heroCount = (Get-ChildItem "data/cards/base-set/heroes/*.json" -ErrorAction SilentlyContinue).Count
$unitCount = (Get-ChildItem "data/cards/base-set/units/*.json" -ErrorAction SilentlyContinue).Count
$tacticCount = (Get-ChildItem "data/cards/base-set/tactics/*.json" -ErrorAction SilentlyContinue).Count
$buildingCount = (Get-ChildItem "data/cards/base-set/buildings/*.json" -ErrorAction SilentlyContinue).Count
$totalCards = $heroCount + $unitCount + $tacticCount + $buildingCount

Write-Host "`nFiles Migrated:" -ForegroundColor Cyan
Write-Host "  Cards: $totalCards total" -ForegroundColor White
Write-Host "    - Heroes: $heroCount" -ForegroundColor Gray
Write-Host "    - Units: $unitCount" -ForegroundColor Gray
Write-Host "    - Tactics: $tacticCount" -ForegroundColor Gray
Write-Host "    - Buildings: $buildingCount" -ForegroundColor Gray
Write-Host "  Packs: $packCount" -ForegroundColor White
Write-Host "  Boxes: $boxCount" -ForegroundColor White
Write-Host "  Rewards: $rewardCount" -ForegroundColor White
Write-Host "  Scripts: $scriptCount (moved to tools/)" -ForegroundColor White

Write-Host "`nNew Structure:" -ForegroundColor Cyan
Write-Host "  data/cards/base-set/heroes/     ← Hero cards" -ForegroundColor Gray
Write-Host "  data/cards/base-set/units/      ← Unit cards" -ForegroundColor Gray
Write-Host "  data/products/packs/            ← Pack definitions" -ForegroundColor Gray
Write-Host "  tools/generators/               ← Build scripts" -ForegroundColor Gray

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Review new /data structure" -ForegroundColor White
Write-Host "  2. Update scripts to use /data instead of /docs" -ForegroundColor White
Write-Host "  3. Generate reference docs from /data" -ForegroundColor White
Write-Host "  4. Clean up old /docs structure (remove JSONs, keep .md)" -ForegroundColor White
Write-Host "  5. Update FILE-LOCATIONS.md to reflect new structure" -ForegroundColor White

Write-Host "`nMigration complete! Files copied (originals preserved)." -ForegroundColor Green
