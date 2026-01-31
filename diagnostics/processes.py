"""Process resource monitoring module."""

import psutil
import time
from typing import List, Dict, Any
from collections import defaultdict


class ProcessAnalyzer:
    """Analyzes running processes for resource usage."""

    def __init__(self):
        self.items: List[Dict[str, Any]] = []
        self.sample_interval = 2.0  # seconds for CPU sampling

    def _get_severity(self, cpu_percent: float, memory_mb: float) -> str:
        """Determine severity based on resource usage."""
        if cpu_percent > 50 or memory_mb > 2000:
            return 'Critical'
        elif cpu_percent > 20 or memory_mb > 1000:
            return 'Warning'
        return 'OK'

    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"

    def scan(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Scan running processes for resource usage."""
        self.items = []
        process_data = {}

        # First pass: collect initial CPU times
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc.cpu_percent()  # Initialize CPU measurement
                process_data[proc.pid] = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Wait for sample interval
        time.sleep(self.sample_interval)

        # Second pass: collect actual measurements
        for pid, proc in process_data.items():
            try:
                with proc.oneshot():
                    name = proc.name()
                    cpu_percent = proc.cpu_percent()
                    memory_info = proc.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)

                    try:
                        io_counters = proc.io_counters()
                        disk_read = io_counters.read_bytes
                        disk_write = io_counters.write_bytes
                    except (psutil.AccessDenied, AttributeError):
                        disk_read = 0
                        disk_write = 0

                    severity = self._get_severity(cpu_percent, memory_mb)

                    self.items.append({
                        'pid': pid,
                        'name': name,
                        'cpu_percent': round(cpu_percent, 1),
                        'memory_mb': round(memory_mb, 1),
                        'disk_read': self._format_bytes(disk_read),
                        'disk_write': self._format_bytes(disk_write),
                        'severity': severity
                    })

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort by CPU + Memory impact
        self.items.sort(key=lambda x: (x['cpu_percent'] + x['memory_mb'] / 100), reverse=True)

        # Return top N
        self.items = self.items[:top_n]
        return self.items

    def get_system_totals(self) -> Dict[str, Any]:
        """Get overall system resource usage."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        return {
            'cpu_percent': cpu_percent,
            'memory_total_gb': round(memory.total / (1024**3), 1),
            'memory_used_gb': round(memory.used / (1024**3), 1),
            'memory_percent': memory.percent
        }

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts by severity."""
        summary = {'Critical': 0, 'Warning': 0, 'OK': 0}
        for item in self.items:
            severity = item.get('severity', 'OK')
            summary[severity] = summary.get(severity, 0) + 1
        return summary
