@echo off
REM Windows System Diagnostic Tool - Build Script
REM This script creates a standalone executable

echo ========================================
echo  Building Windows System Diagnostic Tool
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Navigate to project root
cd /d "%~dp0\.."

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable...
echo.

REM Run PyInstaller with the spec file
pyinstaller --noconfirm executable\SystemDiagnostic.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Move the executable to the executable folder
echo.
echo Moving files to executable folder...
if exist "dist\SystemDiagnostic" (
    xcopy /E /Y "dist\SystemDiagnostic\*" "executable\SystemDiagnostic\" >nul
    rmdir /S /Q "dist" 2>nul
    rmdir /S /Q "build" 2>nul
)

echo.
echo ========================================
echo  Build Complete!
echo  Executable located at:
echo  executable\SystemDiagnostic\SystemDiagnostic.exe
echo ========================================
echo.
pause
