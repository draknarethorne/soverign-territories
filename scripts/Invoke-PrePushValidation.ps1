Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        throw 'Node.js is required for schema validation pre-push checks.'
    }

    if (-not (Get-Command ajv -ErrorAction SilentlyContinue)) {
        throw 'ajv-cli is required. Install with: npm install -g ajv-cli json-schema-to-typescript'
    }

    $schemas = Get-ChildItem -Path 'docs/specs' -Filter '*.json' -File
    foreach ($schema in $schemas) {
        & ajv validate -s $schema.FullName -d $schema.FullName | Out-Null
    }

    Write-Host "Pre-push schema validation passed for $($schemas.Count) schema files."
}
finally {
    Pop-Location
}
