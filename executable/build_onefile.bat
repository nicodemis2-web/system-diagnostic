@echo off
REM Windows System Diagnostic Tool - Single File Build Script
REM Creates a single .exe file (larger but easier to distribute)

echo ========================================
echo  Building Single-File Executable
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Navigate to project root
cd /d "%~dp0\.."

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt pyinstaller

echo.
echo Building single-file executable...
echo This may take several minutes...
echo.

REM Build single file executable
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "SystemDiagnostic" ^
    --add-data "diagnostics;diagnostics" ^
    --add-data "ui;ui" ^
    --add-data "utils;utils" ^
    --collect-data customtkinter ^
    --hidden-import customtkinter ^
    --hidden-import psutil ^
    --hidden-import wmi ^
    --hidden-import win32com.client ^
    --hidden-import pythoncom ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Move to executable folder
echo.
echo Moving executable...
if exist "dist\SystemDiagnostic.exe" (
    move /Y "dist\SystemDiagnostic.exe" "executable\SystemDiagnostic.exe" >nul
    rmdir /S /Q "dist" 2>nul
    rmdir /S /Q "build" 2>nul
    del /Q "SystemDiagnostic.spec" 2>nul
)

echo.
echo ========================================
echo  Build Complete!
echo  Executable: executable\SystemDiagnostic.exe
echo ========================================
echo.
pause
