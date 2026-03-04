@echo off
echo ==========================================
echo Starting Instana Observability Dashboard
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Error: Virtual environment not found
    echo Please run scripts\setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo Error: .env file not found
    echo Please copy .env.example to .env and configure it
    echo.
    echo Quick setup:
    echo   copy .env.example .env
    echo   notepad .env
    pause
    exit /b 1
)

echo Configuration validated
echo.
echo ==========================================
echo Starting server...
echo ==========================================
echo.

REM Run the application
python -m src.app

REM Deactivate on exit
call venv\Scripts\deactivate.bat

pause

@REM Made with Bob
