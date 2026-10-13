param([switch]$Uninstall)
$ErrorActionPreference = 'Stop'
trap {
    Write-Host ($_ | Out-String) -ForegroundColor Red
    Write-Host $_.ScriptStackTrace
    exit 1
}
$keys = @(
    'HKCU:\Software\Classes\Directory\shell\SabyLogReport',
    'HKCU:\Software\Classes\Directory\Background\shell\SabyLogReport'
)
if ($Uninstall) {
    foreach ($key in $keys) {
        if (Test-Path -LiteralPath $key) { Remove-Item -LiteralPath $key -Recurse -Force }
    }
    Write-Host 'Context menu removed.'
    exit
}
$runner = Join-Path $PSScriptRoot 'RunSabyLogReport.ps1'
if (!(Test-Path -LiteralPath $runner)) { throw "Missing file: $runner" }
if (!(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'SabyLogReport.cmd'))) { throw 'Report script is missing.' }
for ($i = 0; $i -lt $keys.Count; $i++) {
    $key = $keys[$i]
    $argument = if ($i -eq 0) { '%1' } else { '%V' }
    New-Item -Path $key -Force | Out-Null
    Set-Item -LiteralPath $key -Value 'Построить отчет по логам'
    New-ItemProperty -LiteralPath $key -Name MUIVerb -Value 'Построить отчет по логам' -PropertyType String -Force | Out-Null
    New-ItemProperty -LiteralPath $key -Name Position -Value 'Top' -PropertyType String -Force | Out-Null
    New-ItemProperty -LiteralPath $key -Name Icon -Value 'powershell.exe,0' -PropertyType String -Force | Out-Null
    New-Item -Path "$key\command" -Force | Out-Null
    $command = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $runner + '" -Folder "' + $argument + '"'
    Set-Item -LiteralPath "$key\command" -Value $command
}
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class SabyLogReportShell {
    [DllImport("shell32.dll")]
    public static extern void SHChangeNotify(uint eventId, uint flags, IntPtr item1, IntPtr item2);
}
'@
[SabyLogReportShell]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)
Write-Host 'Context menu installed for the current user; Explorer notified.'
