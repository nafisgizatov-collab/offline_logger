@echo off
setlocal
set "SABY_UPDATE_SELF=%~f0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try { $text=[IO.File]::ReadAllText($env:SABY_UPDATE_SELF,[Text.Encoding]::UTF8); $marker='#'+'__POWERSHELL_PAYLOAD__'; & ([ScriptBlock]::Create($text.Substring($text.IndexOf($marker)+$marker.Length))); exit 0 } catch { Write-Host $_ -ForegroundColor Red; exit 1 }"
set "UPDATE_RESULT=%ERRORLEVEL%"
if not "%UPDATE_RESULT%"=="0" echo Install / update failed. See the error above.
pause
exit /b %UPDATE_RESULT%
#__POWERSHELL_PAYLOAD__
param([string]$PackagePath, [string]$Destination = (Join-Path $env:LOCALAPPDATA 'SabyOfflineLogger\offline_logger-main'), [switch]$SkipMenu)
$ErrorActionPreference = 'Stop'
$stage = Join-Path ([IO.Path]::GetTempPath()) ('saby-update-' + [guid]::NewGuid().ToString())
try {
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    $archive = Join-Path $stage 'logger.zip'
    if ($PackagePath) { Copy-Item -LiteralPath $PackagePath -Destination $archive }
    else {
        Write-Host 'Downloading latest Offline Logger...'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest 'https://github.com/nafisgizatov-collab/offline_logger/archive/refs/heads/main.zip' -OutFile $archive -UseBasicParsing
    }
    $unpacked = Join-Path $stage 'package'
    Expand-Archive -LiteralPath $archive -DestinationPath $unpacked
    $source = Join-Path $unpacked 'offline_logger-main'
    foreach ($name in @('installSabyLogContextMenu-Windows.cmd', 'resources\installSabyLogContextMenu.ps1', 'resources\build_background_report.py', 'resources\SabyLogReport.cmd', 'resources\build_zip_log_report.py')) {
        if (!(Test-Path -LiteralPath (Join-Path $source $name) -PathType Leaf)) { throw "Incomplete download: $name" }
    }
    $resources = Join-Path $Destination 'resources'
    New-Item -ItemType Directory -Path $resources -Force | Out-Null
    foreach ($file in Get-ChildItem -LiteralPath (Join-Path $source 'resources') -File) {
        $target = Join-Path $resources $file.Name
        if (($file.Name -in @('UI-console-keys', 'UI-console-ignore')) -and (Test-Path -LiteralPath $target)) {
            Write-Host ('Keeping local settings: ' + $file.Name)
            continue
        }
        Copy-Item -LiteralPath $file.FullName -Destination $target -Force
    }
    Copy-Item -LiteralPath (Join-Path $source 'installSabyLogContextMenu-Windows.cmd') -Destination (Join-Path $Destination 'installSabyLogContextMenu-Windows.cmd') -Force
    if (!$SkipMenu) {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $resources 'installSabyLogContextMenu.ps1')
        if ($LASTEXITCODE -ne 0) { throw 'Context menu installation failed.' }
    }
    Write-Host ('Installed / updated: ' + $Destination)
    Write-Host 'Local UI-console settings preserved. Reopen Explorer windows.'
} finally {
    if (Test-Path -LiteralPath $stage) {
        $resolved = [IO.Path]::GetFullPath($stage)
        $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\')
        if (([IO.Path]::GetDirectoryName($resolved) -ne $tempRoot) -or !([IO.Path]::GetFileName($resolved).StartsWith('saby-update-'))) { throw 'Unsafe cleanup path' }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}
