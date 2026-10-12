@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python "%~dp0build_background_report.py" %*
) else (
  py -3 "%~dp0build_background_report.py" %*
)
if errorlevel 1 pause
