# Split BASE_SET_MASTER_CARDS.json into Individual Card Files
# Single Source of Truth: Each card gets its own JSON file

param(
    [string]$InputFile = "docs/codex/base-set/BASE_SET_MASTER_CARDS.json",
    [string]$OutputDir = "docs/codex/base-set/cards"
)

Write-Host "Splitting master card file into individual JSON files..." -ForegroundColor Cyan
Write-Host "Input: $InputFile" -ForegroundColor Gray
Write-Host "Output: $OutputDir" -ForegroundColor Gray

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "Created directory: $OutputDir" -ForegroundColor Green
} else {
    # Clean existing cards
    Remove-Item "$OutputDir\*.json" -Force
    Write-Host "Cleared existing card files" -ForegroundColor Yellow
}

# Load master JSON
$masterData = Get-Content $InputFile -Raw | ConvertFrom-Json
$cardCount = 0

foreach ($card in $masterData.cards) {
    # Generate filename from cardId (lowercase with hyphens)
    $filename = $card.cardId.ToLower().Replace("_", "-") + ".json"
    $filepath = Join-Path $OutputDir $filename

    # Save individual card JSON
    $card | ConvertTo-Json -Depth 10 | Set-Content -Path $filepath -Encoding UTF8

    $cardCount++
    $rarityStars = if ($card.rarity.stars) { ("*" * $card.rarity.stars) } else { "" }
    Write-Host "  [$cardCount] $($card.collectionNumber) - $($card.name) ($($card.rarity.tier) $rarityStars)" -ForegroundColor Gray
}

Write-Host "`nSplit complete!" -ForegroundColor Green
Write-Host "Total cards: $cardCount" -ForegroundColor Cyan
Write-Host "Output directory: $OutputDir" -ForegroundColor Cyan

# Verify against expected count
if ($cardCount -eq 140) {
    Write-Host "All 140 Base Set cards split successfully!" -ForegroundColor Green
} else {
    Write-Host "Warning: Expected 140 cards, found $cardCount in master file" -ForegroundColor Yellow
    Write-Host "Note: Master file may be incomplete. Generate remaining cards from COMPLETE-CARD-LIST.md" -ForegroundColor Yellow
}
