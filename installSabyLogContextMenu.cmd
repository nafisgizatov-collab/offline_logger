@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0resources\installSabyLogContextMenu.ps1" %* > "%~dp0resources\installSabyLogContextMenu.log" 2>&1
set "INSTALL_RESULT=%ERRORLEVEL%"
type "%~dp0resources\installSabyLogContextMenu.log"
if not "%INSTALL_RESULT%"=="0" (echo Installation failed.) else (echo Done.)
pause
exit /b %INSTALL_RESULT%
