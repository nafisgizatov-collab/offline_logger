@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0installSabyLogContextMenu.ps1" %* > "%~dp0installSabyLogContextMenu.log" 2>&1
set "INSTALL_RESULT=%ERRORLEVEL%"
type "%~dp0installSabyLogContextMenu.log"
if not "%INSTALL_RESULT%"=="0" (echo Installation failed.) else (echo Done.)
pause
