"""Startup program analysis module."""

import os
import winreg
from typing import List, Dict, Any
from pathlib import Path


class StartupAnalyzer:
    """Analyzes startup programs from registry and startup folders."""

    # Known resource-heavy applications
    HIGH_IMPACT_APPS = {
        'steam', 'discord', 'spotify', 'teams', 'slack', 'skype',
        'onedrive', 'dropbox', 'googledrive', 'icloud', 'adobe',
        'creative cloud', 'vmware', 'virtualbox', 'docker',
        'mcafee', 'norton', 'avast', 'avg', 'kaspersky', 'bitdefender',
        'itunes', 'epicgames', 'origin', 'battlenet', 'gog galaxy',
        'corsair', 'razer', 'logitech', 'steelseries', 'nzxt',
        'nvidia', 'amd', 'geforce', 'radeon'
    }

    MEDIUM_IMPACT_APPS = {
        'java', 'update', 'helper', 'sync', 'tray', 'agent',
        'monitor', 'service', 'daemon', 'launcher', 'updater',
        'assistant', 'companion', 'manager'
    }

    REGISTRY_LOCATIONS = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
    ]

    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def _get_impact_rating(self, name: str, path: str) -> str:
        """Determine impact rating based on application name/path."""
        name_lower = name.lower()
        path_lower = path.lower()

        # Check for high impact apps
        for app in self.HIGH_IMPACT_APPS:
            if app in name_lower or app in path_lower:
                return "High"

        # Check for medium impact apps
        for app in self.MEDIUM_IMPACT_APPS:
            if app in name_lower or app in path_lower:
                return "Medium"

        return "Low"

    def _scan_registry_location(self, hkey, subkey: str, source: str) -> List[Dict[str, Any]]:
        """Scan a single registry location for startup items."""
        items = []
        try:
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        impact = self._get_impact_rating(name, value)
                        items.append({
                            'name': name,
                            'path': value,
                            'source': source,
                            'impact': impact
                        })
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass
        except PermissionError:
            pass
        return items

    def _scan_startup_folder(self, folder_path: Path, source: str) -> List[Dict[str, Any]]:
        """Scan a startup folder for shortcut files."""
        items = []
        try:
            if folder_path.exists():
                for item in folder_path.iterdir():
                    if item.suffix.lower() in ['.lnk', '.exe', '.bat', '.cmd']:
                        impact = self._get_impact_rating(item.stem, str(item))
                        items.append({
                            'name': item.stem,
                            'path': str(item),
                            'source': source,
                            'impact': impact
                        })
        except PermissionError:
            pass
        return items

    def scan(self) -> List[Dict[str, Any]]:
        """Perform full startup scan."""
        self.items = []

        # Scan registry locations
        registry_sources = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU\\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM\\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run", "HKLM\\Run (x86)"),
        ]

        for hkey, subkey, source in registry_sources:
            self.items.extend(self._scan_registry_location(hkey, subkey, source))

        # Scan startup folders
        user_startup = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        common_startup = Path(os.environ.get('PROGRAMDATA', '')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

        self.items.extend(self._scan_startup_folder(user_startup, "User Startup Folder"))
        self.items.extend(self._scan_startup_folder(common_startup, "Common Startup Folder"))

        # Sort by impact (High first)
        impact_order = {'High': 0, 'Medium': 1, 'Low': 2}
        self.items.sort(key=lambda x: impact_order.get(x['impact'], 3))

        return self.items

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts by impact level."""
        summary = {'High': 0, 'Medium': 0, 'Low': 0}
        for item in self.items:
            impact = item.get('impact', 'Low')
            summary[impact] = summary.get(impact, 0) + 1
        return summary
