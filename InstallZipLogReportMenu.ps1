param([switch]$Uninstall)
$ErrorActionPreference = 'Stop'
trap { Write-Host ($_ | Out-String) -ForegroundColor Red; exit 1 }
$key = 'HKCU:\Software\Classes\SystemFileAssociations\.zip\shell\SabyOfflineLogReport'
if ($Uninstall) {
    if (Test-Path -LiteralPath $key) { Remove-Item -LiteralPath $key -Recurse -Force }
    exit
}
$runner = Join-Path $PSScriptRoot 'RunZipLogReport.ps1'
foreach ($file in @($runner, (Join-Path $PSScriptRoot 'build_zip_log_report.py'), (Join-Path $PSScriptRoot 'build_background_report.py'))) {
    if (!(Test-Path -LiteralPath $file)) { throw "Missing file: $file" }
}
New-Item -Path "$key\command" -Force | Out-Null
Set-Item -LiteralPath $key -Value 'Построить отчет логов оффлайн'
New-ItemProperty -LiteralPath $key -Name MUIVerb -Value 'Построить отчет логов оффлайн' -PropertyType String -Force | Out-Null
New-ItemProperty -LiteralPath $key -Name Icon -Value 'powershell.exe,0' -PropertyType String -Force | Out-Null
New-ItemProperty -LiteralPath $key -Name MultiSelectModel -Value 'Single' -PropertyType String -Force | Out-Null
Set-Item -LiteralPath "$key\command" -Value ('powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $runner + '" -Archive "%1"')
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class ZipReportShell {
 [DllImport("shell32.dll")]
 public static extern void SHChangeNotify(uint eventId, uint flags, IntPtr item1, IntPtr item2);
}
'@
[ZipReportShell]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)
Write-Host 'ZIP context menu installed. Close and reopen the folder window.'
