# Generate Individual Card JSON Files from Master Card List
# Single Source of Truth: Each card = 1 JSON file in docs/codex/base-set/cards/

param(
    [string]$InputFile = "docs/codex/base-set/COMPLETE-CARD-LIST.md",
    [string]$OutputDir = "docs/codex/base-set/cards"
)

Write-Host "Generating individual card JSON files..." -ForegroundColor Cyan
Write-Host "Input: $InputFile" -ForegroundColor Gray
Write-Host "Output: $OutputDir" -ForegroundColor Gray

# Create output directory if it doesn't exist
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "Created directory: $OutputDir" -ForegroundColor Green
}

# Read the markdown file
$content = Get-Content $InputFile -Raw

# Parse card entries (table rows starting with | BS-)
$cardPattern = '^\|\s*(BS-\d+)\s*\|\s*([A-Z_]+)\s*\|\s*([^|]+?)\s*\|'
$lines = $content -split "`n"

$cardCount = 0
$currentElement = "Unknown"
$currentType = "Unknown"

foreach ($line in $lines) {
    # Track current element section
    if ($line -match '^## (\w+) Element') {
        $currentElement = $matches[1]
        Write-Host "`nProcessing $currentElement cards..." -ForegroundColor Yellow
    }

    # Track current card type
    if ($line -match '^### (Heroes|Units|Tactics|Buildings)') {
        $currentType = $matches[1] -replace 's$', ''  # Singular form
    }

    # Parse card line
    if ($line -match $cardPattern) {
        $collectionNumber = $matches[1]
        $cardId = $matches[2]

        # Split line by pipes and clean up
        $fields = $line -split '\|' | ForEach-Object { $_.Trim() } | Where-Object { $_ }

        # Parse based on card type
        $card = @{
            cardId = $cardId
            collectionNumber = $collectionNumber
            series = "base-set"
        }

        # Determine element (Neutral if BS-121+)
        if ($collectionNumber -match 'BS-1[2-4]\d') {
            $card.element = "Neutral"
        } else {
            $card.element = $currentElement
        }

        # Parse fields based on type
        if ($currentType -eq "Hero") {
            $card.type = "Hero"
            $card.name = $fields[2]
            $card.rarity = $fields[3]
            $card.hp = [int]$fields[4]
            $card.mana = [int]$fields[5]
            $card.attack = [int]$fields[6]
            $card.defense = [int]$fields[7]
            $card.movement = [int]$fields[8]
            $card.range = [int]$fields[9]
            $card.ability = $fields[10]
        }
        elseif ($currentType -eq "Unit") {
            $card.type = "Unit"
            $card.name = $fields[2]

            # Check if rarity is specified (Uncommon/Rare units)
            if ($fields.Count -gt 9) {
                $card.rarity = $fields[3]
                $card.hp = [int]$fields[4]
                $card.mana = [int]$fields[5]
                $card.attack = [int]$fields[6]
                $card.defense = [int]$fields[7]
                $card.movement = [int]$fields[8]
                $card.range = [int]$fields[9]
                $card.ability = if ($fields.Count -gt 10) { $fields[10] } else { $null }
            } else {
                # Common units (no rarity specified)
                $card.rarity = "Common"
                $card.hp = [int]$fields[3]
                $card.mana = [int]$fields[4]
                $card.attack = [int]$fields[5]
                $card.defense = [int]$fields[6]
                $card.movement = [int]$fields[7]
                $card.range = [int]$fields[8]
                $card.ability = if ($fields.Count -gt 9) { $fields[9] } else { $null }
            }
        }
        elseif ($currentType -eq "Tactic") {
            $card.type = "Tactic"
            $card.name = $fields[2]
            $card.rarity = $fields[3]
            $card.manaCost = [int]$fields[4]
            $card.effect = $fields[5]
        }
        elseif ($currentType -eq "Building") {
            $card.type = "Building"
            $card.name = $fields[2]
            $card.rarity = $fields[3]
            $card.hp = [int]$fields[4]
            $card.defense = [int]$fields[5]
            $card.effect = $fields[6]
        }

        # Calculate rarity points
        $rarityPoints = switch ($card.rarity) {
            "Common" { 1 }
            "Uncommon" { 2 }
            "Rare" { 4 }
            "Epic" { 8 }
            "Legendary" { 16 }
            "Mythic" { 32 }
            default { 1 }
        }
        $card.rarityPoints = $rarityPoints

        # Add metadata
        $card.createdDate = (Get-Date -Format "yyyy-MM-dd")
        $card.version = "1.0"

        # Generate filename (lowercase, hyphens)
        $filename = "$($cardId.ToLower()).json"
        $filepath = Join-Path $OutputDir $filename

        # Convert to JSON and save
        $json = $card | ConvertTo-Json -Depth 5
        $json | Set-Content -Path $filepath -Encoding UTF8

        $cardCount++
        Write-Host "  [$cardCount] $collectionNumber - $($card.name) ($($card.rarity))" -ForegroundColor Gray
    }
}

Write-Host "`nGeneration complete!" -ForegroundColor Green
Write-Host "Total cards generated: $cardCount" -ForegroundColor Cyan
Write-Host "Output directory: $OutputDir" -ForegroundColor Cyan

# Verify count
if ($cardCount -eq 140) {
    Write-Host "All 140 Base Set cards generated successfully!" -ForegroundColor Green
} else {
    Write-Host "Warning: Expected 140 cards, generated $cardCount" -ForegroundColor Yellow
}
