@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0InstallZipLogReportMenu.ps1" > "%~dp0InstallZipLogReportMenu.log" 2>&1
set "INSTALL_RESULT=%ERRORLEVEL%"
type "%~dp0InstallZipLogReportMenu.log"
if not "%INSTALL_RESULT%"=="0" (echo Installation failed.) else (echo Installed.)
pause
