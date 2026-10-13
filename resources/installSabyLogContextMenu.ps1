param([switch]$Uninstall)
$ErrorActionPreference = 'Stop'
try {
    if (!$Uninstall) {
        . (Join-Path $PSScriptRoot 'PythonRuntime.ps1')
        $python = Resolve-SabyPython
        Write-Host ('Python проверен: ' + $python)
    }
    $installers = @('InstallSabyLogReportMenu.ps1', 'InstallZipLogReportMenu.ps1')
    foreach ($installer in $installers) {
        $path = Join-Path $PSScriptRoot $installer
        if (!(Test-Path -LiteralPath $path)) { throw "Missing file: $path" }
    }
    foreach ($installer in $installers) {
        # Separate processes keep each installer's exit and Add-Type isolated.
        $installerArguments = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $PSScriptRoot $installer))
        if ($Uninstall) { $installerArguments += '-Uninstall' }
        & powershell.exe @installerArguments
        if ($LASTEXITCODE -ne 0) { throw "Failed: $installer (exit $LASTEXITCODE)" }
    }
    if (!$Uninstall) {
        $menuKeys = @('Directory\shell\SabyLogReport', 'Directory\Background\shell\SabyLogReport', 'SystemFileAssociations\.zip\shell\SabyOfflineLogReport', 'SystemFileAssociations\.7z\shell\SabyOfflineLogReport', '7-Zip.7z\shell\SabyOfflineLogReport')
        $regLines = @('Windows Registry Editor Version 5.00', '')
        foreach ($menuKey in $menuKeys) {
            $key = 'HKCU:\Software\Classes\' + $menuKey
            $label = (Get-Item -LiteralPath $key).GetValue('')
            $command = (Get-Item -LiteralPath ($key + '\command')).GetValue('')
            $escapedCommand = $command.Replace('\', '\\').Replace('"', '\"')
            $nativeKey = 'HKEY_CURRENT_USER\Software\Classes\' + $menuKey
            $regLines += @("[$nativeKey]", ('@="' + $label + '"'), ('"MUIVerb"="' + $label + '"'), '"Icon"="powershell.exe,0"', '', "[$nativeKey\command]", ('@="' + $escapedCommand + '"'), '')
        }
        $regLines | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'InstallSabyLogContextMenu.reg') -Encoding Unicode
    }
    if ($Uninstall) { Write-Host 'Both Saby log context menu entries removed.' }
    else { Write-Host 'Both Saby log context menu entries installed. Reopen the folder window.' }
} catch {
    Write-Host ($_ | Out-String) -ForegroundColor Red
    exit 1
}
