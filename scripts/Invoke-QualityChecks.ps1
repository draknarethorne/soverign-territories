Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) {
    throw "PSScriptAnalyzer is required. Install with: Install-Module PSScriptAnalyzer -Scope CurrentUser"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$settings = Join-Path $repoRoot 'PSScriptAnalyzerSettings.psd1'

$paths = @(
    (Join-Path $repoRoot 'scripts'),
    (Join-Path $repoRoot 'tools')
) | Where-Object { Test-Path $_ }

if ($paths.Count -eq 0) {
    Write-Host 'No PowerShell directories found to analyze.'
    exit 0
}

$results = @()
foreach ($path in $paths) {
    $results += Invoke-ScriptAnalyzer -Path $path -Settings $settings -Recurse
}

$warningResults = @($results | Where-Object { $_.Severity -eq 'Warning' })
$errorResults = @($results | Where-Object { $_.Severity -eq 'Error' })
$warningCount = $warningResults.Count

if ($results.Count -gt 0) {
    $results | Format-Table -AutoSize | Out-String | Write-Host
}

if ($errorResults.Count -gt 0) {
    throw "PSScriptAnalyzer found $($errorResults.Count) error issue(s)."
}

if ($warningCount -gt 0) {
    Write-Host "PSScriptAnalyzer warnings (non-blocking in Phase 1): $warningCount"
}

Write-Host 'PSScriptAnalyzer checks passed (blocking errors: none).'
