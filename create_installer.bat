@echo off
:: Complete installer creation script for Image Labeling Tool
:: This script creates both the executable and the installer

echo ========================================
echo  Image Labeling Tool - Complete Build
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

echo Step 1: Installing build dependencies...
echo.

:: Install required packages
pip install pyinstaller pillow

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Setting up build environment...
echo.

:: Create necessary directories
if not exist "assets" mkdir assets
if not exist "build" mkdir build
if not exist "dist" mkdir dist
if not exist "installer_output" mkdir installer_output

:: Create a basic icon if it doesn't exist
if not exist "assets\icon.ico" (
    echo Creating default icon...
    echo NOTE: You can replace assets\icon.ico with your custom icon
)

:: Create LICENSE file if it doesn't exist
if not exist "LICENSE.txt" (
    echo Creating LICENSE file...
    echo MIT License > LICENSE.txt
    echo. >> LICENSE.txt
    echo Copyright (c) 2024 Image Labeling Tool Team >> LICENSE.txt
    echo. >> LICENSE.txt
    echo Permission is hereby granted, free of charge, to any person obtaining a copy >> LICENSE.txt
    echo of this software and associated documentation files (the "Software"), to deal >> LICENSE.txt
    echo in the Software without restriction, including without limitation the rights >> LICENSE.txt
    echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell >> LICENSE.txt
    echo copies of the Software, and to permit persons to whom the Software is >> LICENSE.txt
    echo furnished to do so, subject to the following conditions: >> LICENSE.txt
    echo. >> LICENSE.txt
    echo The above copyright notice and this permission notice shall be included in all >> LICENSE.txt
    echo copies or substantial portions of the Software. >> LICENSE.txt
    echo. >> LICENSE.txt
    echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR >> LICENSE.txt
    echo IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, >> LICENSE.txt
    echo FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE >> LICENSE.txt
    echo AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER >> LICENSE.txt
    echo LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, >> LICENSE.txt
    echo OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE >> LICENSE.txt
    echo SOFTWARE. >> LICENSE.txt
)

echo.
echo Step 3: Building executable...
echo.

:: Build the executable
pyinstaller --clean build.spec

if errorlevel 1 (
    echo ERROR: Executable build failed
    pause
    exit /b 1
)

echo.
echo Step 4: Testing executable...
echo.

:: Test if the executable runs
if exist "dist\ImageLabelingTool.exe" (
    echo Executable created successfully: dist\ImageLabelingTool.exe
    echo File size: 
    dir "dist\ImageLabelingTool.exe" | find "ImageLabelingTool.exe"
) else (
    echo ERROR: Executable not found
    pause
    exit /b 1
)

echo.
echo Step 5: Checking for Inno Setup...
echo.

:: Check if Inno Setup is installed
where iscc >nul 2>&1
if errorlevel 1 (
    echo WARNING: Inno Setup is not installed or not in PATH
    echo.
    echo To create an installer, please:
    echo 1. Download Inno Setup from https://jrsoftware.org/isdl.php
    echo 2. Install it and add it to your PATH
    echo 3. Run this script again
    echo.
    echo For now, you can use the executable directly from: dist\ImageLabelingTool.exe
    echo.
    goto :skip_installer
)

echo Step 6: Creating Windows installer...
echo.

:: Compile the installer
iscc installer.iss

if errorlevel 1 (
    echo ERROR: Installer creation failed
    echo Check the installer.iss file and try again
    goto :skip_installer
)

echo.
echo Installer created successfully!
dir "installer_output\*.exe" | find ".exe"

:skip_installer

echo.
echo ========================================
echo Build Summary
echo ========================================
echo.

if exist "dist\ImageLabelingTool.exe" (
    echo ✓ Executable: dist\ImageLabelingTool.exe
)

if exist "installer_output\*.exe" (
    echo ✓ Installer: installer_output\Image Labeling Tool_v1.0.0_Setup.exe
) else (
    echo ✗ Installer: Not created (Inno Setup required)
)

echo.
echo Files ready for distribution:
echo - Standalone executable: dist\ImageLabelingTool.exe
if exist "installer_output\*.exe" (
    echo - Windows installer: installer_output\Image Labeling Tool_v1.0.0_Setup.exe
)

echo.
echo Build completed successfully!
echo.

:: Offer to test
set /p test="Do you want to test the executable now? (y/n): "
if /i "%test%"=="y" (
    echo.
    echo Starting Image Labeling Tool...
    start "" "dist\ImageLabelingTool.exe"
)

echo.
pause