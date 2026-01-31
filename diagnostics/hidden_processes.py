"""Hidden process detection module."""

import psutil
import subprocess
import os
from typing import List, Dict, Any, Set


class HiddenProcessAnalyzer:
    """Detects hidden or suspicious processes using multiple enumeration methods."""

    # Known system processes that legitimately have no/missing parent
    SYSTEM_ORPHAN_WHITELIST = {
        'system', 'registry', 'smss.exe', 'csrss.exe', 'wininit.exe',
        'services.exe', 'lsass.exe', 'svchost.exe', 'memory compression'
    }

    # Common process name typosquatting targets
    MIMICRY_TARGETS = {
        'svchost.exe': ['svch0st.exe', 'scvhost.exe', 'svchosts.exe', 'svchosl.exe'],
        'csrss.exe': ['csrs.exe', 'cssrs.exe', 'csrss.com', 'csrs.com'],
        'lsass.exe': ['lsas.exe', 'lsassa.exe', 'isass.exe', 'lsass.com'],
        'services.exe': ['service.exe', 'servlces.exe'],
        'explorer.exe': ['explor3r.exe', 'exp1orer.exe', 'explorer.com'],
        'rundll32.exe': ['runddl32.exe', 'rundl132.exe', 'rundll.exe'],
        'cmd.exe': ['crnd.exe', 'cmd.com'],
        'powershell.exe': ['powershel.exe', 'powershell.com', 'p0wershell.exe']
    }

    # Suspicious executable locations
    SUSPICIOUS_PATHS = [
        'temp', 'tmp', 'downloads', 'appdata\\local\\temp',
        'appdata\\roaming', '$recycle.bin', 'programdata'
    ]

    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def _get_psutil_processes(self) -> Dict[int, Dict]:
        """Get processes using psutil."""
        processes = {}
        for proc in psutil.process_iter(['pid', 'name', 'ppid', 'exe']):
            try:
                info = proc.info
                processes[info['pid']] = {
                    'pid': info['pid'],
                    'name': info['name'] or 'Unknown',
                    'ppid': info['ppid'] or 0,
                    'path': info['exe'] or ''
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes

    def _get_wmi_processes(self) -> Dict[int, Dict]:
        """Get processes using WMI via PowerShell."""
        processes = {}
        try:
            cmd = 'Get-CimInstance Win32_Process | Select-Object ProcessId,Name,ParentProcessId,ExecutablePath | ConvertTo-Csv -NoTypeInformation'
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
                            # Parse CSV line
                            parts = line.strip().strip('"').split('","')
                            if len(parts) >= 3:
                                pid = int(parts[0].strip('"'))
                                name = parts[1].strip('"') if len(parts) > 1 else 'Unknown'
                                ppid = int(parts[2].strip('"')) if len(parts) > 2 and parts[2].strip('"').isdigit() else 0
                                path = parts[3].strip('"') if len(parts) > 3 else ''

                                processes[pid] = {
                                    'pid': pid,
                                    'name': name,
                                    'ppid': ppid,
                                    'path': path
                                }
                        except (ValueError, IndexError):
                            continue
        except Exception:
            pass
        return processes

    def _get_tasklist_processes(self) -> Dict[int, Dict]:
        """Get processes using tasklist command."""
        processes = {}
        try:
            result = subprocess.run(
                ['tasklist', '/FO', 'CSV', '/NH'],
                capture_output=True, text=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    try:
                        parts = line.strip().strip('"').split('","')
                        if len(parts) >= 2:
                            name = parts[0].strip('"')
                            pid = int(parts[1].strip('"'))

                            processes[pid] = {
                                'pid': pid,
                                'name': name,
                                'ppid': 0,  # tasklist doesn't provide parent
                                'path': ''  # tasklist doesn't provide path
                            }
                    except (ValueError, IndexError):
                        continue
        except Exception:
            pass
        return processes

    def _check_name_mimicry(self, name: str) -> List[str]:
        """Check if process name mimics a system process."""
        flags = []
        name_lower = name.lower()

        for target, mimics in self.MIMICRY_TARGETS.items():
            for mimic in mimics:
                if name_lower == mimic.lower():
                    flags.append(f'Possible mimicry of {target}')
                    break

        return flags

    def _check_suspicious_path(self, path: str) -> List[str]:
        """Check if executable is in a suspicious location."""
        flags = []
        if not path:
            return flags

        path_lower = path.lower()
        for suspicious in self.SUSPICIOUS_PATHS:
            if suspicious in path_lower:
                flags.append(f'Executable in suspicious location: {suspicious}')
                break

        return flags

    def _check_orphan_process(self, proc: Dict, all_pids: Set[int]) -> List[str]:
        """Check if process has a missing parent (orphan)."""
        flags = []
        name_lower = proc['name'].lower()

        # Skip known system processes
        if name_lower in self.SYSTEM_ORPHAN_WHITELIST:
            return flags

        ppid = proc.get('ppid', 0)

        # PID 0 and 4 are system processes
        if ppid not in (0, 4) and ppid not in all_pids:
            flags.append('Orphan process (parent not found)')

        return flags

    def _get_severity(self, detection_method: str, flags: List[str]) -> str:
        """Determine severity based on detection method and flags."""
        if detection_method == 'Enumeration Discrepancy':
            return 'Critical'

        if any('mimicry' in f.lower() for f in flags):
            return 'Critical'

        if any('suspicious location' in f.lower() for f in flags):
            return 'Warning'

        if any('orphan' in f.lower() for f in flags):
            return 'Warning'

        if any('missing' in f.lower() for f in flags):
            return 'Warning'

        return 'OK'

    def scan(self) -> List[Dict[str, Any]]:
        """Scan for hidden or suspicious processes."""
        self.items = []

        # Collect processes from all sources
        psutil_procs = self._get_psutil_processes()
        wmi_procs = self._get_wmi_processes()
        tasklist_procs = self._get_tasklist_processes()

        all_pids = set(psutil_procs.keys()) | set(wmi_procs.keys()) | set(tasklist_procs.keys())

        # Track which PIDs we've already reported
        reported_pids = set()

        # Check for enumeration discrepancies
        for pid in all_pids:
            in_psutil = pid in psutil_procs
            in_wmi = pid in wmi_procs
            in_tasklist = pid in tasklist_procs

            sources_found = []
            sources_missing = []

            if in_psutil:
                sources_found.append('psutil')
            else:
                sources_missing.append('psutil')
            if in_wmi:
                sources_found.append('WMI')
            else:
                sources_missing.append('WMI')
            if in_tasklist:
                sources_found.append('tasklist')
            else:
                sources_missing.append('tasklist')

            # Get process info from any available source
            proc = psutil_procs.get(pid) or wmi_procs.get(pid) or tasklist_procs.get(pid)
            if not proc:
                continue

            flags = []
            detection_method = 'Normal'

            # Check for discrepancy (process hiding from some APIs)
            if len(sources_missing) > 0 and len(sources_found) > 0:
                # Only flag if missing from a major source
                if 'psutil' in sources_missing or 'WMI' in sources_missing:
                    detection_method = 'Enumeration Discrepancy'
                    flags.append(f'Not visible to: {", ".join(sources_missing)}')

            # Check for name mimicry
            flags.extend(self._check_name_mimicry(proc['name']))

            # Check for suspicious path
            flags.extend(self._check_suspicious_path(proc['path']))

            # Check for orphan process
            flags.extend(self._check_orphan_process(proc, all_pids))

            # Check for missing executable path
            if not proc['path'] and proc['name'].lower() not in self.SYSTEM_ORPHAN_WHITELIST:
                flags.append('Missing executable path')

            # Only report if there are issues
            if flags or detection_method != 'Normal':
                severity = self._get_severity(detection_method, flags)

                self.items.append({
                    'pid': pid,
                    'name': proc['name'],
                    'path': proc['path'] or 'N/A',
                    'ppid': proc['ppid'],
                    'detection_method': detection_method,
                    'sources_found': sources_found,
                    'sources_missing': sources_missing,
                    'flags': flags,
                    'severity': severity,
                    'details': '; '.join(flags) if flags else 'Enumeration discrepancy detected'
                })
                reported_pids.add(pid)

        # Sort by severity
        severity_order = {'Critical': 0, 'Warning': 1, 'OK': 2}
        self.items.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return self.items

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts."""
        summary = {
            'total': len(self.items),
            'discrepancies': 0,
            'mimicry': 0,
            'orphans': 0,
            'suspicious_path': 0,
            'Critical': 0,
            'Warning': 0,
            'OK': 0
        }

        for item in self.items:
            severity = item.get('severity', 'OK')
            summary[severity] = summary.get(severity, 0) + 1

            if item.get('detection_method') == 'Enumeration Discrepancy':
                summary['discrepancies'] += 1

            flags = item.get('flags', [])
            for flag in flags:
                flag_lower = flag.lower()
                if 'mimicry' in flag_lower:
                    summary['mimicry'] += 1
                if 'orphan' in flag_lower:
                    summary['orphans'] += 1
                if 'suspicious location' in flag_lower:
                    summary['suspicious_path'] += 1

        return summary
