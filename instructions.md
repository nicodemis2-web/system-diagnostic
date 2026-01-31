# Windows System Diagnostic Tool

A comprehensive GUI application that identifies startup issues and problematic applications causing system slowdowns on Windows.

## Installation

### Option 1: Run from Source (Developers)

```bash
pip install -r requirements.txt
python main.py
```

**Requirements:**
- Python 3.8 or higher
- Windows 10/11
- Administrator privileges recommended (for full functionality)

### Option 2: Run Standalone Executable (End Users)

If you have the pre-built executable:

1. Navigate to `executable\SystemDiagnostic\`
2. Double-click `SystemDiagnostic.exe`

No Python installation required.

---

## Building the Executable

To create a standalone executable that can run on any Windows machine without Python:

### Standard Build (Recommended)

Creates a folder containing the executable and its dependencies (~20-30 MB total).

1. Double-click `executable\build.bat`
2. Wait for the build to complete
3. Find the result in `executable\SystemDiagnostic\SystemDiagnostic.exe`

**To distribute:** Copy the entire `SystemDiagnostic` folder.

### Single-File Build

Creates a single `.exe` file (~50-80 MB). Easier to share but larger and slower to start.

1. Double-click `executable\build_onefile.bat`
2. Wait for the build to complete (may take several minutes)
3. Find the result at `executable\SystemDiagnostic.exe`

**To distribute:** Copy just the single `.exe` file.

### Build Requirements

- Python 3.8 or higher installed
- pip (Python package manager)
- Internet connection (to download PyInstaller and dependencies)

### Build Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python is not installed" | Install from https://python.org (check "Add to PATH") |
| "pip not found" | Run: `python -m pip install --upgrade pip` |
| Build fails with import errors | Run: `pip install customtkinter psutil wmi pywin32` |
| Executable crashes on start | Edit `.spec` file, change `console=False` to `console=True` to see errors |

---

## What This Tool Checks

### 1. Startup Programs

**What it checks:**
- Registry locations where Windows stores auto-start programs:
  - `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
  - `HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run`
  - `HKEY_LOCAL_MACHINE\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run`
- User startup folder (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`)
- Common startup folder (`%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Startup`)

**Why it matters:**
Every program that starts with Windows increases boot time and consumes system resources. Many applications add themselves to startup without explicit user consent. Over time, accumulated startup programs can significantly slow down your computer's boot process and reduce available memory.

**Impact Ratings:**
- **High** - Known resource-heavy apps (Steam, Discord, Spotify, cloud sync apps, gaming clients, RGB software, antivirus suites)
- **Medium** - Update helpers, sync agents, tray applications, background services
- **Low** - Lightweight utilities and system components

**Recommendation:** Disable high-impact startup items you don't need immediately available. You can always launch them manually when needed.

---

### 2. Windows Services

**What it checks:**
- All services configured to start automatically with Windows
- Distinguishes between Microsoft and third-party services
- Identifies services that are running vs stopped

**Why it matters:**
Windows services run in the background continuously, consuming CPU and memory even when you're not actively using the associated application. Third-party services from installed software often set themselves to auto-start unnecessarily.

**What to look for:**
- Third-party services set to "Automatic" that you don't need running constantly
- Services from uninstalled applications that remain on your system
- Multiple services from the same application (some apps install several)

**Recommendation:** Review third-party services and change unnecessary ones from "Automatic" to "Manual" start type using `services.msc`.

---

### 3. Process Resource Usage

**What it checks:**
- CPU usage per process (sampled over 2 seconds for accuracy)
- Memory consumption (RAM) per process
- Disk read/write activity per process
- Identifies the top 20 resource-consuming processes

**Why it matters:**
Runaway processes or poorly optimized applications can consume excessive resources, causing system slowdowns, high temperatures, and reduced battery life on laptops. Identifying these allows you to take action.

**Severity Levels:**
- **Critical** - CPU > 50% or Memory > 2GB
- **Warning** - CPU > 20% or Memory > 1GB
- **OK** - Normal resource usage

**Recommendation:** Investigate critical and warning processes. If they're not actively being used, consider closing them or finding lighter alternatives.

---

### 4. Disk Health

**What it checks:**
- Free space on all drives (flags drives with < 10% free)
- SMART status (Self-Monitoring, Analysis, and Reporting Technology)
- Temporary file accumulation across system temp folders

**Why it matters:**

**Low disk space** causes:
- Windows cannot create temporary files or virtual memory
- Applications crash or fail to save data
- System updates fail to install
- Overall system performance degrades significantly

**SMART warnings** indicate:
- The drive is predicting its own failure
- Data loss may be imminent
- Immediate backup is critical

**Temp file buildup:**
- Wastes disk space
- Can contain old/corrupted cached data
- Should be cleaned periodically

**Severity Levels:**
- **Critical** - Less than 5% free space or SMART failure predicted
- **Warning** - Less than 10% free space or temp files > 500MB
- **OK** - Adequate free space and healthy drive

**Recommendation:** Maintain at least 15-20% free space on your system drive. If SMART warnings appear, back up immediately and plan drive replacement.

---

### 5. Driver Status

**What it checks:**
- All Plug and Play devices via Windows Management Instrumentation (WMI)
- Devices with error codes (failed to start, resource conflicts, corrupted drivers)
- Unsigned drivers that may pose security or stability risks

**Why it matters:**
Problematic drivers are a leading cause of:
- Blue Screen of Death (BSOD) crashes
- Hardware not functioning correctly
- System instability and freezes
- Security vulnerabilities (unsigned drivers)

**Common Error Codes:**
| Code | Meaning |
|------|---------|
| 1 | Device not configured correctly |
| 10 | Device cannot start |
| 12 | Resource conflict with another device |
| 22 | Device is disabled |
| 28 | Drivers not installed |
| 31 | Device not working properly |
| 43 | Device reported problems and was stopped |
| 52 | Driver is not digitally signed |

**Recommendation:** Update or reinstall drivers showing errors. For unsigned drivers, obtain signed versions from the manufacturer or consider whether the device is necessary.

---

### 6. Scheduled Tasks

**What it checks:**
- All scheduled tasks registered with Windows Task Scheduler
- Tasks triggered at logon, startup, or boot
- Frequently-running tasks (every minute/hour)
- Third-party vs Microsoft tasks

**Why it matters:**
Scheduled tasks run automatically at specified times or events. Poorly configured tasks can:
- Slow down login/startup
- Consume resources at inopportune times
- Run unnecessary maintenance or update checks
- Persist after software is uninstalled

**What to look for:**
- Third-party tasks running at every logon
- Tasks from uninstalled applications
- Tasks running very frequently (every few minutes)
- Unknown tasks with suspicious paths

**Recommendation:** Review third-party scheduled tasks in Task Scheduler (`taskschd.msc`). Disable or delete tasks from applications you no longer use.

---

## Scan Types

### Full Scan
Checks all six diagnostic categories. Takes longer but provides complete system analysis.

### Quick Scan
Checks only:
- Startup programs
- Process resource usage

Use for a fast overview of immediate performance concerns.

---

## Understanding the Summary Tab

After scanning, the Summary tab displays:

### Metric Cards
- **Startup Items** - Total programs starting with Windows
- **Third-Party Services** - Non-Microsoft auto-start services
- **High Resource** - Processes using excessive CPU/memory
- **Disk Issues** - Drives with low space or health warnings
- **Driver Problems** - Devices with errors
- **Scheduled Tasks** - Third-party scheduled tasks

### Color Coding
- 🟢 **Green (OK)** - No issues detected
- 🟡 **Yellow (Warning)** - Potential concerns worth reviewing
- 🔴 **Red (Critical)** - Issues requiring immediate attention

### Recommendations
Automatically generated suggestions based on scan results, prioritized by severity.

---

## Exporting Reports

Click **Export Report** to save results as an HTML file. The report includes:
- System information
- All scan results organized by category
- Color-coded severity indicators
- Timestamp for reference

Useful for:
- Documenting system state before/after changes
- Sharing with technical support
- Keeping records of system health over time

---

## Administrator Privileges

Some checks require administrator access:
- SMART disk status (requires WMI access)
- Certain service details
- Some driver information

The tool displays "✓ Admin" or "⚠ Limited" in the toolbar.

**To run as administrator:**

*From Source:*
1. Right-click `main.py`
2. Select "Open with" → Python
3. Or open Command Prompt as Admin and run: `python main.py`

*Executable:*
1. Right-click `SystemDiagnostic.exe`
2. Select "Run as administrator"

*Create Admin Shortcut:*
1. Right-click `SystemDiagnostic.exe` → Create shortcut
2. Right-click the shortcut → Properties
3. Click "Advanced" → Check "Run as administrator"
4. Click OK

---

## Comparing Results

To verify scan accuracy, compare with built-in Windows tools:

| This Tool | Windows Equivalent |
|-----------|-------------------|
| Startup Programs | Task Manager → Startup tab |
| Services | services.msc |
| Processes | Task Manager → Processes/Details |
| Disk Health | This PC (right-click drive → Properties) |
| Drivers | Device Manager (devmgmt.msc) |
| Scheduled Tasks | Task Scheduler (taskschd.msc) |

---

## Troubleshooting

### Scan Issues

**Scan takes too long:**
- Process monitoring requires a 2-second sample period
- Driver and scheduled task scans query WMI which can be slow
- Use Quick Scan for faster results

**Some data shows as "Unknown":**
- Run as administrator for full access
- Some system processes restrict access to their information

### Running from Source

**Application doesn't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python 3.8+ is installed
- Check that you're running on Windows (Linux/macOS not supported)

**Import errors:**
- Run: `pip install customtkinter psutil wmi pywin32`

### Executable Issues

**Executable won't start:**
- Windows SmartScreen may block it → Click "More info" → "Run anyway"
- Antivirus may quarantine it → Add an exception for the executable
- Missing Visual C++ Runtime → Install from Microsoft

**Executable starts slowly:**
- Single-file builds extract to temp folder on each launch (normal)
- First launch may trigger antivirus scan (normal)
- Use the folder-based build for faster startup

**"Windows protected your PC" message:**
- This appears for unsigned executables
- Click "More info" → "Run anyway"
- Or right-click → Properties → Check "Unblock" → Apply

**Executable crashes immediately:**
- Rebuild with `console=True` in the .spec file to see error messages
- Ensure all dependencies were available during build
- Try rebuilding after running: `pip install --upgrade pyinstaller`

---

## Safety Notes

This tool is **read-only** and does not modify your system. It only:
- Reads registry values
- Queries running processes
- Reads disk information
- Queries WMI for device/driver status
- Reads scheduled task configuration

No changes are made to startup programs, services, drivers, or any system settings. Any modifications must be done manually using the appropriate Windows tools.

---

## Project Structure

```
system_diagnostic/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── instructions.md         # This documentation
│
├── diagnostics/            # Diagnostic analysis modules
│   ├── startup.py          # Startup program scanner
│   ├── services.py         # Windows services analyzer
│   ├── processes.py        # Process resource monitor
│   ├── disk.py             # Disk health checker
│   ├── drivers.py          # Driver status analyzer
│   └── scheduled.py        # Scheduled tasks scanner
│
├── ui/                     # User interface components
│   ├── main_window.py      # Main application window
│   ├── results_panel.py    # Tabbed results display
│   └── widgets.py          # Custom UI widgets
│
├── utils/                  # Utility modules
│   ├── admin.py            # Admin privilege handling
│   └── report.py           # HTML report generator
│
└── executable/             # Build scripts and output
    ├── build.bat           # Standard build script
    ├── build_onefile.bat   # Single-file build script
    ├── SystemDiagnostic.spec  # PyInstaller configuration
    └── README.txt          # Build instructions
```

---

## Distribution

### Distributing the Executable

**Folder Build (Recommended):**
1. Build using `build.bat`
2. Zip the entire `executable\SystemDiagnostic\` folder
3. Share the zip file
4. Users extract and run `SystemDiagnostic.exe`

**Single-File Build:**
1. Build using `build_onefile.bat`
2. Share `SystemDiagnostic.exe` directly
3. Users run the single file (no extraction needed)

### Distributing Source Code

Include these files/folders:
- `main.py`
- `requirements.txt`
- `diagnostics/`
- `ui/`
- `utils/`
- `instructions.md` (optional)
- `executable/` (optional, for users who want to build)

Users install dependencies with: `pip install -r requirements.txt`

---

## Version History

**v1.0.0** - Initial Release
- Startup programs analysis
- Windows services analysis
- Process resource monitoring
- Disk health checking
- Driver status detection
- Scheduled tasks analysis
- HTML report export
- Dark-themed GUI with customtkinter
