"""Disk health and space analysis module."""

import os
import psutil
import subprocess
from typing import List, Dict, Any
from pathlib import Path


class DiskAnalyzer:
    """Analyzes disk health, space, and fragmentation."""

    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"

    def _get_space_severity(self, percent_free: float) -> str:
        """Determine severity based on free space percentage."""
        if percent_free < 5:
            return 'Critical'
        elif percent_free < 10:
            return 'Warning'
        return 'OK'

    def _get_smart_status(self, drive_letter: str) -> str:
        """Get SMART status for a drive using WMI."""
        try:
            # Use PowerShell to query SMART status
            result = subprocess.run(
                ['powershell', '-Command',
                 f'Get-WmiObject -Namespace root\\wmi -Class MSStorageDriver_FailurePredictStatus 2>$null | '
                 f'Select-Object InstanceName, PredictFailure | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                # Parse result - simplified check
                if 'true' in result.stdout.lower():
                    return 'Warning - Failure Predicted'
                return 'OK'
        except Exception:
            pass
        return 'Unknown'

    def _get_temp_folder_size(self) -> Dict[str, Any]:
        """Calculate size of temp folders."""
        temp_paths = [
            Path(os.environ.get('TEMP', '')),
            Path(os.environ.get('TMP', '')),
            Path('C:/Windows/Temp'),
        ]

        total_size = 0
        file_count = 0

        for temp_path in temp_paths:
            try:
                if temp_path.exists():
                    for item in temp_path.rglob('*'):
                        try:
                            if item.is_file():
                                total_size += item.stat().st_size
                                file_count += 1
                        except (PermissionError, OSError):
                            pass
            except (PermissionError, OSError):
                pass

        return {
            'size': self._format_bytes(total_size),
            'size_bytes': total_size,
            'file_count': file_count
        }

    def scan(self) -> List[Dict[str, Any]]:
        """Scan all drives for health and space information."""
        self.items = []

        # Get disk partitions
        partitions = psutil.disk_partitions()

        for partition in partitions:
            try:
                # Skip CD-ROM drives and network drives
                if 'cdrom' in partition.opts.lower() or partition.fstype == '':
                    continue

                usage = psutil.disk_usage(partition.mountpoint)
                percent_free = 100 - usage.percent
                severity = self._get_space_severity(percent_free)

                # Get SMART status for physical drives
                drive_letter = partition.device[0] if partition.device else ''
                smart_status = self._get_smart_status(drive_letter)

                self.items.append({
                    'drive': partition.device,
                    'mount_point': partition.mountpoint,
                    'file_system': partition.fstype,
                    'total': self._format_bytes(usage.total),
                    'used': self._format_bytes(usage.used),
                    'free': self._format_bytes(usage.free),
                    'percent_used': f"{usage.percent}%",
                    'smart_status': smart_status,
                    'severity': severity
                })

            except (PermissionError, OSError):
                pass

        # Add temp folder analysis
        temp_info = self._get_temp_folder_size()
        if temp_info['size_bytes'] > 1024 * 1024 * 500:  # > 500 MB
            temp_severity = 'Warning'
        elif temp_info['size_bytes'] > 1024 * 1024 * 1024:  # > 1 GB
            temp_severity = 'Critical'
        else:
            temp_severity = 'OK'

        self.items.append({
            'drive': 'Temp Folders',
            'mount_point': 'Various',
            'file_system': 'N/A',
            'total': 'N/A',
            'used': temp_info['size'],
            'free': 'N/A',
            'percent_used': f"{temp_info['file_count']} files",
            'smart_status': 'N/A',
            'severity': temp_severity
        })

        # Sort by severity
        severity_order = {'Critical': 0, 'Warning': 1, 'OK': 2}
        self.items.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return self.items

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of disk status."""
        summary = {
            'total_drives': len([i for i in self.items if i['drive'] != 'Temp Folders']),
            'low_space_drives': 0,
            'smart_warnings': 0
        }
        for item in self.items:
            if item['severity'] in ['Critical', 'Warning'] and item['drive'] != 'Temp Folders':
                summary['low_space_drives'] += 1
            if 'Warning' in item.get('smart_status', '') or 'Failure' in item.get('smart_status', ''):
                summary['smart_warnings'] += 1
        return summary
