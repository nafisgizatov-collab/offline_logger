param([Parameter(Mandatory=$true)][string]$Archive)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
try {
    $archivePath = (Resolve-Path -LiteralPath $Archive).Path
    $scriptPath = Join-Path $PSScriptRoot 'build_zip_log_report.py'
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -u $scriptPath $archivePath --serve
    } elseif (Test-Path -LiteralPath $bundledPython) {
        & $bundledPython -u $scriptPath $archivePath --serve
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -u $scriptPath $archivePath --serve
    } else { throw 'Install Python 3.9 or newer.' }
    if ($LASTEXITCODE -ne 0) { throw 'Archive report generation failed.' }
} catch {
    Write-Host $_ -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
