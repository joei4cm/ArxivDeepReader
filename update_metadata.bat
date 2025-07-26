@echo off
echo ArXiv Deep Reader - Metadata Auto-Updater
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing/updating dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Warning: Failed to install some dependencies
    echo You may need to install them manually:
    echo pip install beautifulsoup4 lxml
    echo.
)

REM Run the metadata updater
echo.
echo Running metadata updater...
python update_metadata.py

echo.
echo Press any key to exit...
pause >nul