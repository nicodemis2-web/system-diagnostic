# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Windows System Diagnostic Tool
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the project root directory
project_root = os.path.abspath(os.path.join(SPECPATH, '..'))

# Collect customtkinter data files (themes, etc.)
ctk_datas = collect_data_files('customtkinter')

a = Analysis(
    [os.path.join(project_root, 'main.py')],
    pathex=[project_root],
    binaries=[],
    datas=ctk_datas,
    hiddenimports=[
        'customtkinter',
        'psutil',
        'wmi',
        'win32com',
        'win32com.client',
        'pythoncom',
        'pywintypes',
        'winreg',
        # Include all our modules
        'diagnostics',
        'diagnostics.startup',
        'diagnostics.services',
        'diagnostics.processes',
        'diagnostics.disk',
        'diagnostics.drivers',
        'diagnostics.scheduled',
        'diagnostics.hidden_processes',
        'diagnostics.hidden_directories',
        'ui',
        'ui.main_window',
        'ui.results_panel',
        'ui.widgets',
        'utils',
        'utils.admin',
        'utils.report',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SystemDiagnostic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window - GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: icon='path/to/icon.ico'
    uac_admin=False,  # Set to True to always request admin
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SystemDiagnostic',
)
