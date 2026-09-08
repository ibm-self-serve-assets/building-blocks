@echo off
REM IBM Concert Insights Dashboard - Setup and Run Script (Windows)

echo ==========================================
echo IBM Concert Insights Dashboard Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit the .env file with your IBM Concert credentials:
    echo   - CONCERT_BASE_URL
    echo   - C_API_KEY
    echo   - INSTANCE_ID
    echo.
    pause
)

REM Validate .env configuration
echo Validating configuration...
findstr /C:"your_api_key_here" .env >nul
if not errorlevel 1 (
    echo.
    echo ERROR: .env file still contains placeholder values!
    echo Please edit .env with your actual IBM Concert credentials.
    pause
    exit /b 1
)
echo Configuration looks good.
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo ==========================================
echo Starting IBM Concert Insights Dashboard
echo ==========================================
echo.
echo The dashboard will be available at: http://127.0.0.1:8050
echo Press Ctrl+C to stop the server
echo.

REM Run the application
python app.py

pause

@REM Made with Bob
