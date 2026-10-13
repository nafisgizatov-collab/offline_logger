param([Parameter(Mandatory=$true)][string]$Folder)
$ErrorActionPreference = 'Stop'
try {
    $folderPath = (Resolve-Path -LiteralPath $Folder).Path
    if (!(Test-Path -LiteralPath $folderPath -PathType Container)) { throw 'Select a folder.' }
    & (Join-Path $PSScriptRoot 'SabyLogReport.cmd') $folderPath
    if ($LASTEXITCODE -ne 0) { throw 'Report generation failed.' }
} catch {
    Write-Host $_ -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
