@echo off
cd /d "%~dp0.."
where py >nul 2>nul
if errorlevel 1 (
  echo [start] Python 3 is required. Download it from https://www.python.org/downloads/
  pause
  exit /b 1
)
py -3 scripts\start.py %*
if errorlevel 1 pause
