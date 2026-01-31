"""Windows services analysis module."""

import subprocess
from typing import List, Dict, Any


class ServicesAnalyzer:
    """Analyzes Windows services for potential issues."""

    # Microsoft service prefixes/patterns to identify MS services
    MS_SERVICE_PATTERNS = [
        'windows', 'microsoft', 'wmi', 'wua', 'wsearch', 'wlan',
        'wdi', 'wer', 'wcn', 'wbc', 'vss', 'vds', 'uxsms', 'usb',
        'upnp', 'ui0', 'tzautoupdate', 'trkwks', 'themes', 'tablet',
        'sys', 'svc', 'spooler', 'smart', 'shell', 'sens', 'security',
        'scard', 'sam', 'rpc', 'remote', 'ras', 'power', 'plug', 'pla',
        'perf', 'pca', 'p2p', 'nsi', 'network', 'netlogon', 'msi',
        'mps', 'mpeg', 'lm', 'license', 'lanman', 'ksm', 'keyiso',
        'iphlp', 'iprip', 'ikeext', 'hid', 'gpsvc', 'font', 'fdphost',
        'event', 'eap', 'dot3', 'dns', 'dfs', 'device', 'defragsvc',
        'dcom', 'crypt', 'core', 'com', 'clipboard', 'cert', 'browser',
        'bits', 'base', 'audio', 'appx', 'appv', 'app', 'action', '.net'
    ]

    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def _is_microsoft_service(self, name: str, display_name: str) -> bool:
        """Check if service appears to be a Microsoft service."""
        combined = (name + display_name).lower()
        for pattern in self.MS_SERVICE_PATTERNS:
            if pattern in combined:
                return True
        return False

    def _get_severity(self, state: str, is_ms: bool) -> str:
        """Determine severity based on service state and type."""
        if state.lower() == 'stopped':
            return 'OK'
        if not is_ms:
            return 'Warning'  # Non-MS service running at startup
        return 'OK'

    def scan(self) -> List[Dict[str, Any]]:
        """Scan Windows services."""
        self.items = []

        try:
            # Use sc query to get service information
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-Service | Where-Object {$_.StartType -eq "Automatic"} | '
                 'Select-Object Name, DisplayName, Status, StartType | '
                 'ConvertTo-Csv -NoTypeInformation'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Skip header
                    for line in lines[1:]:
                        # Parse CSV line
                        parts = self._parse_csv_line(line)
                        if len(parts) >= 4:
                            name = parts[0].strip('"')
                            display_name = parts[1].strip('"')
                            status = parts[2].strip('"')
                            start_type = parts[3].strip('"')

                            is_ms = self._is_microsoft_service(name, display_name)
                            severity = self._get_severity(status, is_ms)

                            self.items.append({
                                'name': name,
                                'display_name': display_name,
                                'status': status,
                                'start_type': start_type,
                                'type': 'Microsoft' if is_ms else 'Third-Party',
                                'severity': severity
                            })

        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            print(f"Error scanning services: {e}")

        # Sort: Third-party first, then by status
        self.items.sort(key=lambda x: (
            0 if x['type'] == 'Third-Party' else 1,
            0 if x['status'] == 'Running' else 1
        ))

        return self.items

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

    def get_third_party_count(self) -> int:
        """Get count of third-party services."""
        return sum(1 for item in self.items if item['type'] == 'Third-Party')

    def get_summary(self) -> Dict[str, int]:
        """Get summary of services by type and status."""
        summary = {
            'total': len(self.items),
            'third_party': 0,
            'microsoft': 0,
            'running': 0,
            'stopped': 0
        }
        for item in self.items:
            if item['type'] == 'Third-Party':
                summary['third_party'] += 1
            else:
                summary['microsoft'] += 1
            if item['status'] == 'Running':
                summary['running'] += 1
            else:
                summary['stopped'] += 1
        return summary
