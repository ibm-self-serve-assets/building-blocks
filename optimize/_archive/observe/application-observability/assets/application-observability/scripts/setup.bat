@echo off
echo ==========================================
echo Instana Observability Dashboard Setup
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version

if %errorlevel% neq 0 (
    echo Error: Python is not installed
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python detected

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed

REM Create .env file if it doesn't exist
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo .env file created
    echo.
    echo IMPORTANT: Please edit .env file with your Instana credentials
    echo    Required settings:
    echo    - INSTANA_BASE_URL
    echo    - INSTANA_API_TOKEN
    echo    - INSTANA_APPLICATION_NAME (default: finvault)
) else (
    echo.
    echo .env file already exists
)

REM Create logs directory
if not exist logs mkdir logs

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file with your Instana credentials:
echo    notepad .env
echo.
echo 2. Run the application:
echo    scripts\run.bat
echo.
echo 3. Access the dashboard at:
echo    http://localhost:8050
echo.

pause

@REM Made with Bob
