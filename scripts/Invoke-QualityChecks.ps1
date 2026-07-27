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

if ($results.Count -gt 0) {
    $results | Format-Table -AutoSize | Out-String | Write-Host
    throw "PSScriptAnalyzer found $($results.Count) issue(s)."
}

Write-Host 'PSScriptAnalyzer checks passed.'
