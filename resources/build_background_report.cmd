@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0RunPythonReport.ps1" %*
set "REPORT_RESULT=%ERRORLEVEL%"
if not "%REPORT_RESULT%"=="0" pause
exit /b %REPORT_RESULT%
