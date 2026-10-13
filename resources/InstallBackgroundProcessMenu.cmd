@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0InstallBackgroundProcessMenu.ps1" > "%~dp0InstallBackgroundProcessMenu.log" 2>&1
set "INSTALL_RESULT=%ERRORLEVEL%"
type "%~dp0InstallBackgroundProcessMenu.log"
if not "%INSTALL_RESULT%"=="0" (
  echo Installation failed. See the error above.
) else (
  echo Installed. Close and reopen the folder window.
)
pause
