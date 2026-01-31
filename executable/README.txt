Windows System Diagnostic Tool - Executable Build
=================================================

This folder contains the build scripts to create a standalone executable.

BUILDING THE EXECUTABLE
-----------------------

Option 1: Run the batch file (Recommended)
   Double-click: build.bat

   This will:
   - Install required dependencies
   - Build the executable using PyInstaller
   - Place the result in executable\SystemDiagnostic\

Option 2: Manual build
   1. Open Command Prompt in the project root folder
   2. Run: pip install -r requirements.txt pyinstaller
   3. Run: pyinstaller --noconfirm executable\SystemDiagnostic.spec
   4. Find executable in: dist\SystemDiagnostic\SystemDiagnostic.exe


AFTER BUILDING
--------------

The executable folder will contain:
   SystemDiagnostic\
   ├── SystemDiagnostic.exe    <- Main executable
   ├── _internal\              <- Required libraries
   └── ... (other support files)

To distribute: Copy the entire SystemDiagnostic folder.


REQUIREMENTS
------------

To build:
   - Python 3.8 or higher
   - pip (Python package manager)
   - Internet connection (to download dependencies)

To run the built executable:
   - Windows 10/11
   - No Python installation required
   - Administrator privileges recommended for full functionality


TROUBLESHOOTING
---------------

"Python is not installed"
   Download from https://python.org
   During install, check "Add Python to PATH"

"pip not found"
   Run: python -m pip install --upgrade pip

Build fails with import errors:
   Run: pip install customtkinter psutil wmi pywin32

Executable crashes on startup:
   Try building with console enabled for debugging:
   Edit SystemDiagnostic.spec, change console=False to console=True


NOTES
-----

- The executable does NOT require admin rights to run, but some
  diagnostic features work better with elevation.

- The built executable is self-contained and includes all
  dependencies. No Python installation needed on target machines.

- File size will be approximately 50-100 MB due to bundled libraries.
