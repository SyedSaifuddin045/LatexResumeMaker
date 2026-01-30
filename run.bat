@echo off
echo Starting ATS Resume Genius...
echo Checking dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies. Please ensure Python is installed and added to PATH.
    pause
    exit /b
)

echo Launching Application...
python main.py
if %errorlevel% neq 0 (
    echo Application crashed.
    pause
)
