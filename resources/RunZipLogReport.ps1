param([Parameter(Mandatory=$true)][string]$Archive)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
try {
    $archivePath = (Resolve-Path -LiteralPath $Archive).Path
    $scriptPath = Join-Path $PSScriptRoot 'build_zip_log_report.py'
    . (Join-Path $PSScriptRoot 'PythonRuntime.ps1')
    $python = Resolve-SabyPython
    & $python -u $scriptPath $archivePath --serve
    if ($LASTEXITCODE -ne 0) { throw 'Archive report generation failed.' }
} catch {
    Write-Host $_ -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
