"""Driver status analysis module."""

import subprocess
from typing import List, Dict, Any


class DriverAnalyzer:
    """Analyzes driver status and identifies problematic drivers."""

    # Status codes that indicate problems
    PROBLEM_STATUS_CODES = {
        1: 'Device not configured',
        3: 'Driver corrupted',
        10: 'Device cannot start',
        12: 'Resource conflict',
        14: 'Device needs restart',
        16: 'Cannot identify resources',
        18: 'Needs reinstall',
        19: 'Registry corrupted',
        21: 'Windows removing device',
        22: 'Device disabled',
        24: 'Device not present',
        28: 'Drivers not installed',
        29: 'Device disabled by firmware',
        31: 'Device not working',
        32: 'Driver disabled',
        33: 'Cannot determine resources',
        34: 'Cannot determine IRQ',
        35: 'Cannot determine IRQ table',
        36: 'Cannot determine IRQ translation',
        37: 'Cannot determine DMA',
        38: 'Cannot determine DMA type',
        39: 'Driver registry entry corrupted',
        40: 'Driver missing/corrupted',
        41: 'Device failed to load',
        42: 'Device cannot start',
        43: 'Device reported problems',
        44: 'Device stopped',
        45: 'Device not connected',
        46: 'Device not available',
        47: 'Cannot use device',
        48: 'Device software blocked',
        49: 'Registry too large',
        52: 'Driver not digitally signed',
    }

    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def _get_severity(self, config_manager_error_code: int, is_signed: bool) -> str:
        """Determine severity based on error code and signature."""
        if config_manager_error_code != 0:
            return 'Critical'
        if not is_signed:
            return 'Warning'
        return 'OK'

    def scan(self) -> List[Dict[str, Any]]:
        """Scan for driver issues using WMI."""
        self.items = []

        try:
            # Query PnP devices with potential issues
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-WmiObject Win32_PnPEntity | '
                 'Select-Object Name, DeviceID, Status, ConfigManagerErrorCode | '
                 'ConvertTo-Csv -NoTypeInformation'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    for line in lines[1:]:
                        parts = self._parse_csv_line(line)
                        if len(parts) >= 4:
                            name = parts[0].strip('"')
                            device_id = parts[1].strip('"')
                            status = parts[2].strip('"')
                            error_code_str = parts[3].strip('"')

                            try:
                                error_code = int(error_code_str) if error_code_str else 0
                            except ValueError:
                                error_code = 0

                            # Only include devices with issues
                            if error_code != 0 or status not in ['OK', '']:
                                error_description = self.PROBLEM_STATUS_CODES.get(
                                    error_code, f'Unknown error ({error_code})'
                                ) if error_code != 0 else 'Status issue'

                                severity = 'Critical' if error_code != 0 else 'Warning'

                                self.items.append({
                                    'name': name or 'Unknown Device',
                                    'device_id': device_id[:60] + '...' if len(device_id) > 60 else device_id,
                                    'status': status or 'Unknown',
                                    'error_code': error_code,
                                    'error_description': error_description,
                                    'severity': severity
                                })

        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            print(f"Error scanning drivers: {e}")

        # Also check for unsigned drivers
        self._scan_unsigned_drivers()

        # Sort by severity
        severity_order = {'Critical': 0, 'Warning': 1, 'OK': 2}
        self.items.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return self.items

    def _scan_unsigned_drivers(self):
        """Scan for unsigned drivers."""
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-WmiObject Win32_PnPSignedDriver | '
                 'Where-Object { $_.IsSigned -eq $false } | '
                 'Select-Object DeviceName, DriverVersion | '
                 'ConvertTo-Csv -NoTypeInformation'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    for line in lines[1:]:
                        parts = self._parse_csv_line(line)
                        if len(parts) >= 2:
                            name = parts[0].strip('"')
                            version = parts[1].strip('"')

                            if name:
                                # Check if already in list
                                existing = [i for i in self.items if name in i.get('name', '')]
                                if not existing:
                                    self.items.append({
                                        'name': name,
                                        'device_id': 'N/A',
                                        'status': 'Unsigned',
                                        'error_code': 0,
                                        'error_description': f'Unsigned driver (v{version})',
                                        'severity': 'Warning'
                                    })

        except Exception:
            pass

    def _parse_csv_line(self, line: str) -> List[str]:
        """Parse a CSV line handling quoted fields."""
        parts = []
        current = ""
        in_quotes = False

        for char in line:
            if char == '"':
                in_quotes = not in_quotes
                current += char
            elif char == ',' and not in_quotes:
                parts.append(current)
                current = ""
            else:
                current += char

        if current:
            parts.append(current)

        return parts

    def get_summary(self) -> Dict[str, int]:
        """Get summary of driver issues."""
        summary = {
            'total_issues': len(self.items),
            'critical': 0,
            'warnings': 0,
            'unsigned': 0
        }
        for item in self.items:
            if item['severity'] == 'Critical':
                summary['critical'] += 1
            elif item['severity'] == 'Warning':
                summary['warnings'] += 1
            if 'Unsigned' in item.get('status', ''):
                summary['unsigned'] += 1
        return summary
