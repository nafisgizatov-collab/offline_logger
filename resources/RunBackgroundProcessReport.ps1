param([Parameter(Mandatory=$true)][string]$Folder)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
try {
    $folderPath = (Resolve-Path -LiteralPath $Folder).Path
    $scriptPath = Join-Path $PSScriptRoot 'build_nine_methods_report.py'
    . (Join-Path $PSScriptRoot 'PythonRuntime.ps1')
    $python = Resolve-SabyPython
    & $python -u $scriptPath $folderPath --serve
    if ($LASTEXITCODE -ne 0) { throw 'Report generation failed.' }
} catch {
    Write-Host $_ -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
