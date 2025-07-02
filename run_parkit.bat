@echo off
echo Starting ParkIT - Parking Management System
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

:: Check if requirements are installed
echo Checking dependencies...
python -c "import PyQt5, cv2, numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
)

:: Run the application
echo Starting ParkIT application...
echo.
python main.py

:: Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
) 