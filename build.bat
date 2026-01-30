@echo off
echo Building ATS Resume Genius (Directory Mode)...
echo ----------------------------------

:: Install Requirements if missing
pip install pyinstaller -q

:: Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

echo Running PyInstaller...
:: Build command
:: --onedir: create a directory with exe and dependencies (fixes many DLL issues)
:: --noconfirm: overwrite output
:: --windowed: no console
:: --add-data: assets
:: --hidden-import: ensure clr (pythonnet) is found
pyinstaller --noconfirm --onedir --windowed --icon "icon.ico" ^
    --hidden-import "clr" ^
    --add-data "gui;gui" ^
    --add-data "templates;templates" ^
    --add-data "icon.ico;." ^
    --name "ATS_Resume_Genius" ^
    main.py

echo ----------------------------------
if exist "dist\ATS_Resume_Genius\ATS_Resume_Genius.exe" (
    echo Build Successful!
    echo Executable is located in folder: dist\ATS_Resume_Genius\
    echo You can run the .exe inside that folder.
) else (
    echo Build Failed. Check logs.
)
pause
