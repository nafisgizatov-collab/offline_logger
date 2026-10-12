param([switch]$Uninstall)
$ErrorActionPreference = 'Stop'
try {
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
    if ($Uninstall) { Write-Host 'Both Saby log context menu entries removed.' }
    else { Write-Host 'Both Saby log context menu entries installed. Reopen the folder window.' }
} catch {
    Write-Host ($_ | Out-String) -ForegroundColor Red
    exit 1
}
