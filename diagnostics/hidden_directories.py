"""Hidden directory and Alternate Data Stream detection module."""

import os
import ctypes
import subprocess
from typing import List, Dict, Any
from pathlib import Path


class HiddenDirectoryAnalyzer:
    """Detects hidden directories and Alternate Data Streams."""

    # File attribute constants
    FILE_ATTRIBUTE_HIDDEN = 0x02
    FILE_ATTRIBUTE_SYSTEM = 0x04

    # Known legitimate hidden/system directories
    WHITELIST = {
        'system volume information',
        '$recycle.bin',
        '$windows.~bt',
        '$windows.~ws',
        'recovery',
        'documents and settings',
        'config.msi',
        'msocache',
        'boot',
        'perflogs',
        'windowsapps',
        'winsxs',
        'assembly',
        'installer',
        'microsoft.net',
        'windows.old',
        '$sysreset'
    }

    # Scan locations
    SCAN_PATHS = [
        'C:\\',
        'C:\\Windows',
        'C:\\ProgramData',
    ]

    def __init__(self):
        self.items: List[Dict[str, Any]] = []
        self.kernel32 = ctypes.windll.kernel32

    def _get_file_attributes(self, path: str) -> int:
        """Get file attributes using Windows API."""
        try:
            attrs = self.kernel32.GetFileAttributesW(path)
            return attrs if attrs != -1 else 0
        except Exception:
            return 0

    def _is_hidden(self, path: str) -> bool:
        """Check if path has Hidden attribute."""
        attrs = self._get_file_attributes(path)
        return bool(attrs & self.FILE_ATTRIBUTE_HIDDEN)

    def _is_system(self, path: str) -> bool:
        """Check if path has System attribute."""
        attrs = self._get_file_attributes(path)
        return bool(attrs & self.FILE_ATTRIBUTE_SYSTEM)

    def _is_hidden_system(self, path: str) -> bool:
        """Check if path has both Hidden and System attributes."""
        attrs = self._get_file_attributes(path)
        return (bool(attrs & self.FILE_ATTRIBUTE_HIDDEN) and
                bool(attrs & self.FILE_ATTRIBUTE_SYSTEM))

    def _get_attributes_string(self, path: str) -> str:
        """Get human-readable attributes string."""
        attrs = self._get_file_attributes(path)
        parts = []

        if attrs & self.FILE_ATTRIBUTE_HIDDEN:
            parts.append('Hidden')
        if attrs & self.FILE_ATTRIBUTE_SYSTEM:
            parts.append('System')
        if attrs & 0x01:  # READ_ONLY
            parts.append('ReadOnly')
        if attrs & 0x20:  # ARCHIVE
            parts.append('Archive')

        return ', '.join(parts) if parts else 'Normal'

    def _is_whitelisted(self, name: str) -> bool:
        """Check if directory name is in the whitelist."""
        return name.lower() in self.WHITELIST

    def _get_dir_size(self, path: str) -> str:
        """Get approximate directory size (non-recursive for speed)."""
        try:
            total = 0
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total += entry.stat().st_size
                    except (OSError, PermissionError):
                        pass

            # Format size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if total < 1024:
                    return f"{total:.1f} {unit}"
                total /= 1024
            return f"{total:.1f} TB"
        except Exception:
            return 'Unknown'

    def _scan_alternate_data_streams(self, path: str) -> List[Dict[str, Any]]:
        """Scan for Alternate Data Streams in a directory."""
        ads_items = []

        try:
            # Use PowerShell to find ADS
            cmd = f'Get-ChildItem -Path "{path}" -Force -ErrorAction SilentlyContinue | ForEach-Object {{ Get-Item -Path $_.FullName -Stream * -ErrorAction SilentlyContinue }} | Where-Object {{ $_.Stream -ne ":$DATA" }} | Select-Object FileName,Stream,Length | ConvertTo-Csv -NoTypeInformation'

            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True, text=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    for line in lines[1:]:  # Skip header
                        try:
                            parts = line.strip().strip('"').split('","')
                            if len(parts) >= 2:
                                filename = parts[0].strip('"')
                                stream = parts[1].strip('"')
                                length = parts[2].strip('"') if len(parts) > 2 else '0'

                                # Skip Zone.Identifier (common, benign ADS from downloads)
                                if stream.lower() == 'zone.identifier':
                                    continue

                                ads_items.append({
                                    'path': filename,
                                    'name': f"{os.path.basename(filename)}:{stream}",
                                    'type': 'Alternate Data Stream',
                                    'attributes': f'Stream: {stream}',
                                    'size': f'{length} bytes',
                                    'whitelisted': False,
                                    'severity': 'Warning',
                                    'details': f'Hidden data stream "{stream}" attached to file'
                                })
                        except (ValueError, IndexError):
                            continue
        except Exception:
            pass

        return ads_items

    def _scan_directory(self, base_path: str, depth: int = 1) -> List[Dict[str, Any]]:
        """Scan a directory for hidden items."""
        items = []

        try:
            with os.scandir(base_path) as it:
                for entry in it:
                    try:
                        if not entry.is_dir(follow_symlinks=False):
                            continue

                        full_path = entry.path
                        name = entry.name

                        is_hidden = self._is_hidden(full_path)
                        is_system = self._is_system(full_path)
                        is_whitelisted = self._is_whitelisted(name)

                        # Only report if hidden
                        if is_hidden or is_system:
                            if is_hidden and is_system:
                                item_type = 'Hidden+System Directory'
                                severity = 'Warning' if not is_whitelisted else 'OK'
                            elif is_hidden:
                                item_type = 'Hidden Directory'
                                severity = 'OK'
                            else:
                                item_type = 'System Directory'
                                severity = 'OK'

                            items.append({
                                'path': full_path,
                                'name': name,
                                'type': item_type,
                                'attributes': self._get_attributes_string(full_path),
                                'size': self._get_dir_size(full_path),
                                'whitelisted': is_whitelisted,
                                'severity': severity,
                                'details': 'Known Windows directory' if is_whitelisted else 'Unknown hidden directory'
                            })

                        # Recursively scan if not too deep
                        if depth > 0:
                            items.extend(self._scan_directory(full_path, depth - 1))

                    except (OSError, PermissionError):
                        continue

        except (OSError, PermissionError):
            pass

        return items

    def scan(self) -> List[Dict[str, Any]]:
        """Scan for hidden directories and Alternate Data Streams."""
        self.items = []

        # Add user-specific paths
        user_home = os.path.expanduser('~')
        scan_paths = list(self.SCAN_PATHS)
        scan_paths.append(os.path.join(user_home, 'AppData', 'Local'))
        scan_paths.append(os.path.join(user_home, 'AppData', 'Roaming'))

        # Scan for hidden directories
        for base_path in scan_paths:
            if os.path.exists(base_path):
                self.items.extend(self._scan_directory(base_path, depth=1))

        # Scan for ADS in key locations
        ads_scan_paths = [
            user_home,
            os.path.join(user_home, 'Desktop'),
            os.path.join(user_home, 'Downloads'),
            os.path.join(user_home, 'Documents'),
            'C:\\ProgramData'
        ]

        for ads_path in ads_scan_paths:
            if os.path.exists(ads_path):
                self.items.extend(self._scan_alternate_data_streams(ads_path))

        # Sort by severity and whitelisted status
        severity_order = {'Critical': 0, 'Warning': 1, 'OK': 2}
        self.items.sort(key=lambda x: (
            x.get('whitelisted', False),  # Non-whitelisted first
            severity_order.get(x['severity'], 3)
        ))

        return self.items

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts."""
        summary = {
            'total': len(self.items),
            'hidden_dirs': 0,
            'hidden_system_dirs': 0,
            'ads': 0,
            'whitelisted': 0,
            'suspicious': 0,
            'Critical': 0,
            'Warning': 0,
            'OK': 0
        }

        for item in self.items:
            severity = item.get('severity', 'OK')
            summary[severity] = summary.get(severity, 0) + 1

            item_type = item.get('type', '')
            if 'Alternate Data Stream' in item_type:
                summary['ads'] += 1
            elif 'Hidden+System' in item_type:
                summary['hidden_system_dirs'] += 1
            else:
                summary['hidden_dirs'] += 1

            if item.get('whitelisted'):
                summary['whitelisted'] += 1
            elif severity in ('Warning', 'Critical'):
                summary['suspicious'] += 1

        return summary
