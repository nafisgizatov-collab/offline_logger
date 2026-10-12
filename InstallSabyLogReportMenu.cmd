@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0InstallSabyLogReportMenu.ps1" > "%~dp0InstallSabyLogReportMenu.log" 2>&1
set "INSTALL_RESULT=%ERRORLEVEL%"
type "%~dp0InstallSabyLogReportMenu.log"
if not "%INSTALL_RESULT%"=="0" (
  echo Installation failed. See the error above.
) else (
  echo Installed. Close and reopen the folder window.
)
pause
