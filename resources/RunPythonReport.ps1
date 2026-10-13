param([Parameter(ValueFromRemainingArguments=$true)][string[]]$ReportArguments)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
try {
    . (Join-Path $PSScriptRoot 'PythonRuntime.ps1')
    $python = Resolve-SabyPython
    & $python (Join-Path $PSScriptRoot 'build_background_report.py') @ReportArguments
    exit $LASTEXITCODE
} catch { Write-Host $_ -ForegroundColor Red; exit 1 }
