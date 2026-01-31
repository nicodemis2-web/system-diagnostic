"""Scheduled tasks analysis module."""

import subprocess
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from datetime import datetime


class ScheduledTasksAnalyzer:
    """Analyzes scheduled tasks for potential issues."""

    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def _parse_datetime(self, dt_str: str) -> str:
        """Parse datetime string to readable format."""
        if not dt_str or dt_str == 'N/A':
            return 'Never'
        try:
            # Handle various datetime formats
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    dt = datetime.strptime(dt_str.split('.')[0], fmt)
                    return dt.strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    continue
            return dt_str[:19] if len(dt_str) > 19 else dt_str
        except Exception:
            return dt_str

    def _get_severity(self, trigger: str, state: str, is_microsoft: bool) -> str:
        """Determine severity based on task characteristics."""
        trigger_lower = trigger.lower()

        # Disabled tasks are OK
        if state.lower() == 'disabled':
            return 'OK'

        # Tasks that run at startup/login from non-MS sources are warnings
        if not is_microsoft:
            if any(t in trigger_lower for t in ['logon', 'startup', 'boot', 'system start']):
                return 'Warning'
            if any(t in trigger_lower for t in ['minute', 'hour']) and 'daily' not in trigger_lower:
                return 'Warning'  # Frequently running tasks

        return 'OK'

    def scan(self) -> List[Dict[str, Any]]:
        """Scan scheduled tasks."""
        self.items = []

        try:
            # Get scheduled tasks using schtasks
            result = subprocess.run(
                ['schtasks', '/query', '/fo', 'CSV', '/v'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Parse header to find column indices
                    header = self._parse_csv_line(lines[0])
                    header = [h.strip('"') for h in header]

                    # Find relevant column indices
                    cols = {}
                    for i, h in enumerate(header):
                        h_lower = h.lower()
                        if 'taskname' in h_lower:
                            cols['name'] = i
                        elif 'status' in h_lower and 'last' not in h_lower:
                            cols['status'] = i
                        elif 'triggers' in h_lower or 'trigger' in h_lower:
                            cols['trigger'] = i
                        elif 'last run' in h_lower:
                            cols['last_run'] = i
                        elif 'next run' in h_lower:
                            cols['next_run'] = i
                        elif 'author' in h_lower:
                            cols['author'] = i
                        elif 'task to run' in h_lower:
                            cols['action'] = i

                    # Parse data rows
                    for line in lines[1:]:
                        if not line.strip():
                            continue

                        parts = self._parse_csv_line(line)

                        try:
                            name = parts[cols.get('name', 0)].strip('"') if 'name' in cols else ''
                            status = parts[cols.get('status', 1)].strip('"') if 'status' in cols else ''
                            trigger = parts[cols.get('trigger', 2)].strip('"') if 'trigger' in cols else ''
                            last_run = parts[cols.get('last_run', 3)].strip('"') if 'last_run' in cols else ''
                            author = parts[cols.get('author', 4)].strip('"') if 'author' in cols else ''

                            # Skip empty or system tasks
                            if not name or name.startswith('\\'):
                                continue

                            # Check if Microsoft task
                            is_microsoft = 'microsoft' in author.lower() if author else False

                            # Filter to show only startup/login tasks and non-MS tasks
                            trigger_lower = trigger.lower()
                            show_task = (
                                not is_microsoft or
                                any(t in trigger_lower for t in ['logon', 'startup', 'boot'])
                            )

                            if show_task and trigger:
                                severity = self._get_severity(trigger, status, is_microsoft)

                                self.items.append({
                                    'name': name.split('\\')[-1] if '\\' in name else name,
                                    'full_path': name,
                                    'status': status,
                                    'trigger': trigger[:50] + '...' if len(trigger) > 50 else trigger,
                                    'last_run': self._parse_datetime(last_run),
                                    'author': author[:30] if author else 'Unknown',
                                    'type': 'Microsoft' if is_microsoft else 'Third-Party',
                                    'severity': severity
                                })

                        except (IndexError, KeyError):
                            continue

        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            print(f"Error scanning scheduled tasks: {e}")

        # Sort: third-party first, then by severity
        severity_order = {'Critical': 0, 'Warning': 1, 'OK': 2}
        self.items.sort(key=lambda x: (
            0 if x['type'] == 'Third-Party' else 1,
            severity_order.get(x['severity'], 3)
        ))

        # Limit to reasonable number
        self.items = self.items[:100]

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

    def get_summary(self) -> Dict[str, int]:
        """Get summary of scheduled tasks."""
        summary = {
            'total': len(self.items),
            'third_party': 0,
            'startup_tasks': 0,
            'warnings': 0
        }
        for item in self.items:
            if item['type'] == 'Third-Party':
                summary['third_party'] += 1
            if any(t in item['trigger'].lower() for t in ['logon', 'startup', 'boot']):
                summary['startup_tasks'] += 1
            if item['severity'] == 'Warning':
                summary['warnings'] += 1
        return summary
