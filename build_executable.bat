@echo off
:: Build script for creating Windows executable of Image Labeling Tool
:: This script automates the entire build process

echo ========================================
echo  Image Labeling Tool - Build Script
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher and add it to PATH
    pause
    exit /b 1
)

echo Step 1: Installing required packages...
echo.

:: Install PyInstaller and dependencies
pip install pyinstaller
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Creating assets directory and icon...
echo.

:: Create assets directory
if not exist "assets" mkdir assets

:: Check if icon exists, if not, create a placeholder
if not exist "assets\icon.ico" (
    echo No icon file found. You can add assets\icon.ico for a custom icon.
    echo Using default icon for now.
)

echo.
echo Step 3: Building executable with PyInstaller...
echo.

:: Build the executable using the spec file
pyinstaller build.spec

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo Step 4: Build completed successfully!
echo.
echo The executable is located at: dist\ImageLabelingTool.exe
echo.

:: Optional: Test the executable
set /p test="Do you want to test the executable? (y/n): "
if /i "%test%"=="y" (
    echo.
    echo Testing executable...
    start "" "dist\ImageLabelingTool.exe"
)

echo.
echo ========================================
echo Build process completed successfully!
echo ========================================
echo.
echo Files created:
echo - dist\ImageLabelingTool.exe (Main executable)
echo - build\ (Build cache - can be deleted)
echo.
echo You can now distribute the ImageLabelingTool.exe file.
echo.
pause