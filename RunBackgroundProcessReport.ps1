param([Parameter(Mandatory=$true)][string]$Folder)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
try {
    $folderPath = (Resolve-Path -LiteralPath $Folder).Path
    $scriptPath = Join-Path $PSScriptRoot 'build_nine_methods_report.py'
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -u $scriptPath $folderPath --serve
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -u $scriptPath $folderPath --serve
    } elseif (Test-Path -LiteralPath $bundledPython) {
        & $bundledPython -u $scriptPath $folderPath --serve
    } else {
        throw 'Install Python 3.9 or newer.'
    }
    if ($LASTEXITCODE -ne 0) { throw 'Report generation failed.' }
} catch {
    Write-Host $_ -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
