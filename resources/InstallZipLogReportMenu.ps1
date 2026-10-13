param([switch]$Uninstall)
$ErrorActionPreference = 'Stop'
trap { Write-Host ($_ | Out-String) -ForegroundColor Red; exit 1 }
$keys = @('.zip', '.7z') | ForEach-Object { 'HKCU:\Software\Classes\SystemFileAssociations\' + $_ + '\shell\SabyOfflineLogReport' }
$keys += 'HKCU:\Software\Classes\7-Zip.7z\shell\SabyOfflineLogReport'
if ($Uninstall) {
    foreach ($key in $keys) { if (Test-Path -LiteralPath $key) { Remove-Item -LiteralPath $key -Recurse -Force } }
    exit
}
$runner = Join-Path $PSScriptRoot 'RunZipLogReport.ps1'
foreach ($file in @($runner, (Join-Path $PSScriptRoot 'build_zip_log_report.py'), (Join-Path $PSScriptRoot 'build_background_report.py'))) {
    if (!(Test-Path -LiteralPath $file)) { throw "Missing file: $file" }
}
foreach ($key in $keys) {
New-Item -Path "$key\command" -Force | Out-Null
Set-Item -LiteralPath $key -Value 'Построить отчет логов оффлайн'
New-ItemProperty -LiteralPath $key -Name MUIVerb -Value 'Построить отчет логов оффлайн' -PropertyType String -Force | Out-Null
New-ItemProperty -LiteralPath $key -Name Icon -Value 'powershell.exe,0' -PropertyType String -Force | Out-Null
New-ItemProperty -LiteralPath $key -Name MultiSelectModel -Value 'Single' -PropertyType String -Force | Out-Null
Set-Item -LiteralPath "$key\command" -Value ('powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $runner + '" -Archive "%1"')
}
# Also emit a native import file for Explorer outside isolated registry views.
$regLines = @('Windows Registry Editor Version 5.00', '')
$command = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $runner + '" -Archive "%1"'
$escapedCommand = $command.Replace('\', '\\').Replace('"', '\"')
foreach ($key in $keys) {
    $nativeKey = $key.Replace('HKCU:', 'HKEY_CURRENT_USER')
    $regLines += @("[$nativeKey]", '@="Построить отчет логов оффлайн"', '"MUIVerb"="Построить отчет логов оффлайн"', '"Icon"="powershell.exe,0"', '"MultiSelectModel"="Single"', '', "[$nativeKey\command]", ('@="' + $escapedCommand + '"'), '')
}
$regLines | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'InstallArchiveLogMenu.reg') -Encoding Unicode
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class ZipReportShell {
 [DllImport("shell32.dll")]
 public static extern void SHChangeNotify(uint eventId, uint flags, IntPtr item1, IntPtr item2);
}
'@
[ZipReportShell]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)
Write-Host 'ZIP and 7z context menus installed. Close and reopen the folder window.'
