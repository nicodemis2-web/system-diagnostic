@echo off
REM Windows System Diagnostic Tool - Build Script
REM This script creates a standalone executable

setlocal enabledelayedexpansion

echo ========================================
echo  Building Windows System Diagnostic Tool
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
    REM Verify it's not the Windows Store stub by checking for actual output
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

REM Check if spec file exists
if not exist "executable\SystemDiagnostic.spec" (
    echo ERROR: SystemDiagnostic.spec not found
    echo Expected location: executable\SystemDiagnostic.spec
    pause
    exit /b 1
)

echo Building executable...
echo Running: %PYTHON_CMD% -m PyInstaller --noconfirm executable\SystemDiagnostic.spec
echo.

REM Run PyInstaller with the spec file
%PYTHON_CMD% -m PyInstaller --noconfirm executable\SystemDiagnostic.spec
set "PYINSTALLER_EXIT=%errorlevel%"

REM Check if build succeeded by looking for output files
if not exist "dist\SystemDiagnostic\SystemDiagnostic.exe" (
    echo.
    echo ========================================
    echo  ERROR: Build failed
    echo ========================================
    echo.
    echo The executable was not created.
    echo Check the output above for specific errors.
    echo.
    echo Common issues:
    echo   - Missing dependencies (run pip install again)
    echo   - Antivirus blocking PyInstaller
    echo   - Insufficient disk space
    echo.
    pause
    exit /b 1
)

REM Move the executable to the executable folder
echo.
echo Moving files to executable folder...
if exist "dist\SystemDiagnostic" (
    if not exist "executable\SystemDiagnostic\" mkdir "executable\SystemDiagnostic\"
    xcopy /E /Y "dist\SystemDiagnostic\*" "executable\SystemDiagnostic\" >nul
    if errorlevel 1 (
        echo WARNING: Failed to copy some files
    )
    rmdir /S /Q "dist" 2>nul
    rmdir /S /Q "build" 2>nul
    echo Files moved successfully.
) else (
    echo WARNING: dist\SystemDiagnostic folder not found
    echo The executable may be in a different location.
)

echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo Executable located at:
echo   %~dp0SystemDiagnostic\SystemDiagnostic.exe
echo.
echo To run the application:
echo   1. Navigate to executable\SystemDiagnostic\
echo   2. Double-click SystemDiagnostic.exe
echo.
pause
