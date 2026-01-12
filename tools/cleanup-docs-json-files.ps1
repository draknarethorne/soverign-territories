# Sovereign Territories - Cleanup Docs JSON Files
# Purpose: Complete migration of all runtime JSON files from docs/ to data/

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOVEREIGN TERRITORIES - DOCS CLEANUP" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# PHASE 1: Move Schema JSONs to data/schemas/
Write-Host "PHASE 1: Moving Schema JSONs..." -ForegroundColor Yellow

$schemasToMove = @(
    "ability-schema.json", "achievement-schema.json", "alliance-schema.json",
    "audio-schema.json", "battle-schema.json", "campaign-schema.json",
    "card-schema.json", "deck-schema.json", "deployment-schema.json",
    "diplomacy-schema.json", "economy-node-schema.json", "equipment-schema.json",
    "event-schema.json", "expedition-schema.json", "leaderboard-schema.json",
    "map-schema.json", "matchmaking-schema.json", "notification-schema.json",
    "pack-schema.json", "player-schema.json", "progression-schema.json",
    "quest-schema.json", "resource-schema.json", "reward-schema.json",
    "session-schema.json", "starter-deck-schema.json", "store-schema.json",
    "tactic-schema.json", "theme-schema.json", "trade-schema.json",
    "trainer-deck-schema.json", "tutorial-schema.json", "ui-schema.json"
)

New-Item -ItemType Directory -Force -Path "data/schemas" | Out-Null
Write-Host "  Created data/schemas/" -ForegroundColor Green

$schemaCount = 0
foreach ($schema in $schemasToMove) {
    $sourcePath = "docs/specs/$schema"
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath "data/schemas/$schema"
        Write-Host "  Copied $schema" -ForegroundColor Gray
        $schemaCount++
    }
}
Write-Host "`n  Total Schemas Migrated: $schemaCount`n" -ForegroundColor Green

# PHASE 2: Move Collection Data
Write-Host "PHASE 2: Moving Collection Data..." -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "data/collection" | Out-Null

$collectionCount = 0
Get-ChildItem "docs/collection" -Filter "*.json" | ForEach-Object {
    Copy-Item $_.FullName "data/collection/$($_.Name)"
    Write-Host "  Copied $($_.Name)" -ForegroundColor Gray
    $collectionCount++
}
Write-Host "`n  Total Collection Files: $collectionCount`n" -ForegroundColor Green

# PHASE 3: Move Starter Deck Specs
Write-Host "PHASE 3: Moving Starter Deck Specs..." -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "data/decks/starter" | Out-Null

if (Test-Path "docs/specs/starter-cards.json") {
    Copy-Item "docs/specs/starter-cards.json" "data/decks/starter/starter-cards.json"
    Write-Host "  Copied starter-cards.json`n" -ForegroundColor Gray
}

# PHASE 4: Move Special Files
Write-Host "PHASE 4: Moving Special Card Data..." -ForegroundColor Yellow

if (Test-Path "docs/specs/cards/fire/fire-heroes.json") {
    New-Item -ItemType Directory -Force -Path "data/cards/base-set/element-lists" | Out-Null
    Copy-Item "docs/specs/cards/fire/fire-heroes.json" "data/cards/base-set/element-lists/fire-heroes.json"
    Write-Host "  Copied fire-heroes.json" -ForegroundColor Gray
}

if (Test-Path "docs/codex/_schema.json") {
    Copy-Item "docs/codex/_schema.json" "data/schemas/codex-schema.json"
    Write-Host "  Copied codex schema" -ForegroundColor Gray
}

if (Test-Path "docs/codex/base-set/fire/HERO_ARIA_FLAME_KNIGHT.json") {
    New-Item -ItemType Directory -Force -Path "data/archive/legacy-format" | Out-Null
    Copy-Item "docs/codex/base-set/fire/HERO_ARIA_FLAME_KNIGHT.json" "data/archive/legacy-format/HERO_ARIA_FLAME_KNIGHT.json"
    Write-Host "  Archived legacy hero format" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "MIGRATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Schemas:    $schemaCount files moved to data/schemas/" -ForegroundColor White
Write-Host "Collection: $collectionCount files moved to data/collection/" -ForegroundColor White
Write-Host "`nNext: Review and delete duplicates in docs/" -ForegroundColor Yellow
