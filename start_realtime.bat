@echo off
echo ============================================
echo   Real-Time Fake News Detector
echo   Starting server...
echo ============================================
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if requirements are installed
echo Checking dependencies...
pip show beautifulsoup4 >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements_realtime.txt
)

echo.
echo Starting Real-Time Fake News Detection Server...
echo.
echo Open your browser and go to:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app_realtime.py

pause
