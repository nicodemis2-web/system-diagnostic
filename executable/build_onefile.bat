@echo off
REM Windows System Diagnostic Tool - Single File Build Script
REM Creates a single .exe file (larger but easier to distribute)

setlocal enabledelayedexpansion

echo ========================================
echo  Building Single-File Executable
echo ========================================
echo.

REM Initialize Python command variable
set "PYTHON_CMD="
set "PIP_CMD="

REM Method 1: Try the 'py' launcher (most reliable on Windows)
echo Searching for Python installation...
py --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py"
    set "PIP_CMD=py -m pip"
    echo Found Python via 'py' launcher
    goto :python_found
)

REM Method 2: Try common installation paths
set "PYTHON_PATHS=%LOCALAPPDATA%\Programs\Python\Python312\python.exe;%LOCALAPPDATA%\Programs\Python\Python311\python.exe;%LOCALAPPDATA%\Programs\Python\Python310\python.exe;%LOCALAPPDATA%\Programs\Python\Python39\python.exe;%LOCALAPPDATA%\Programs\Python\Python38\python.exe;C:\Python312\python.exe;C:\Python311\python.exe;C:\Python310\python.exe;C:\Python39\python.exe;C:\Python38\python.exe"

for %%p in (%PYTHON_PATHS%) do (
    if exist "%%p" (
        set "PYTHON_CMD=%%p"
        set "PIP_CMD=%%p -m pip"
        echo Found Python at: %%p
        goto :python_found
    )
)

REM Method 3: Try 'python' command (may fail due to Windows Store alias)
python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do (
        echo %%v | findstr /C:"Python" >nul
        if not errorlevel 1 (
            set "PYTHON_CMD=python"
            set "PIP_CMD=pip"
            echo Found Python via 'python' command
            goto :python_found
        )
    )
)

REM Method 4: Try 'python3' command
python3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python3"
    set "PIP_CMD=pip3"
    echo Found Python via 'python3' command
    goto :python_found
)

REM Python not found - show detailed error
echo.
echo ========================================
echo  ERROR: Python not found!
echo ========================================
echo.
echo Tried the following methods:
echo   1. 'py' launcher (Python Launcher for Windows)
echo   2. Common installation paths
echo   3. 'python' command
echo   4. 'python3' command
echo.
echo Please install Python 3.8+ from https://python.org
echo.
echo During installation, make sure to:
echo   [x] Check "Add Python to PATH"
echo   [x] Check "Install py launcher"
echo.
echo If Python is already installed, you may need to:
echo   1. Disable Windows App Execution Aliases:
echo      Settings ^> Apps ^> Advanced app settings ^> App execution aliases
echo      Turn OFF "python.exe" and "python3.exe"
echo   2. Or add Python to your PATH manually
echo.
pause
exit /b 1

:python_found
echo.

REM Display Python version
echo Python version:
%PYTHON_CMD% --version
echo.

REM Navigate to project root
cd /d "%~dp0\.."
echo Working directory: %CD%
echo.

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found in %CD%
    echo Make sure you're running this from the correct location.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
echo Running: %PIP_CMD% install -r requirements.txt pyinstaller
echo.
%PIP_CMD% install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo.
    echo ========================================
    echo  ERROR: Failed to install dependencies
    echo ========================================
    echo.
    echo Possible solutions:
    echo   1. Run this script as Administrator
    echo   2. Try: %PIP_CMD% install --user -r requirements.txt pyinstaller
    echo   3. Check your internet connection
    echo.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully.
echo.
echo Building single-file executable...
echo This may take several minutes...
echo.

REM Build single file executable
%PYTHON_CMD% -m PyInstaller --noconfirm ^
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
    --hidden-import diagnostics.hidden_processes ^
    --hidden-import diagnostics.hidden_directories ^
    --hidden-import diagnostics.network_connections ^
    main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo  ERROR: Build failed
    echo ========================================
    echo.
    echo Check the output above for specific errors.
    echo Common issues:
    echo   - Missing dependencies (run pip install again)
    echo   - Antivirus blocking PyInstaller
    echo   - Insufficient disk space
    echo.
    pause
    exit /b 1
)

REM Move to executable folder
echo.
echo Moving executable...
if exist "dist\SystemDiagnostic.exe" (
    move /Y "dist\SystemDiagnostic.exe" "executable\SystemDiagnostic.exe" >nul
    if errorlevel 1 (
        echo WARNING: Failed to move executable
    ) else (
        echo Executable moved successfully.
    )
    rmdir /S /Q "dist" 2>nul
    rmdir /S /Q "build" 2>nul
    del /Q "SystemDiagnostic.spec" 2>nul
) else (
    echo WARNING: dist\SystemDiagnostic.exe not found
    echo The executable may be in a different location.
)

echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo Executable located at:
echo   %~dp0SystemDiagnostic.exe
echo.
echo Note: Single-file builds are larger and slower to start
echo than folder builds, but easier to distribute.
echo.
pause
