param([Parameter(Mandatory=$true)][string]$Dataset)
$ErrorActionPreference = 'Stop'
$projectPath = Split-Path -Parent $PSScriptRoot
$rawDestination = Join-Path $projectPath 'data/raw'
$originalSource = (Resolve-Path -LiteralPath $Dataset).Path
if (-not (Test-Path -LiteralPath (Join-Path $originalSource 'phishark2026_public_metadata.csv'))) {
    throw 'The original metadata CSV is not present in the supplied dataset directory.'
}
if (Test-Path -LiteralPath $rawDestination) { throw 'data/raw already exists; nothing was overwritten.' }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $rawDestination) | Out-Null
New-Item -ItemType Junction -Path $rawDestination -Target $originalSource | Select-Object Name,LinkType,Target
