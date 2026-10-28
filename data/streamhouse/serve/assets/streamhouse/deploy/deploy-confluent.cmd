@echo off
cd /d "%~dp0.."
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3 is required. Install Python and Terraform first.
  pause
  exit /b 1
)
py -3 scripts\deploy.py up %*
if errorlevel 1 pause
