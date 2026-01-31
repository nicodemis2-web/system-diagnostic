"""Network connection analysis module."""

import psutil
import socket
from typing import List, Dict, Any


class NetworkConnectionAnalyzer:
    """Analyzes network connections for suspicious activity."""

    # Suspicious ports commonly used by malware/backdoors
    SUSPICIOUS_PORTS = {
        4444, 4445, 5555, 6666, 6667, 31337, 12345, 54321,
        1337, 8080, 9999, 7777, 3389, 5900, 5901, 1234
    }

    # Well-known service ports that are typically safe
    KNOWN_SAFE_PORTS = {
        80, 443, 53, 22, 21, 25, 110, 143, 993, 995, 587,
        123, 67, 68, 137, 138, 139, 445, 3306, 5432, 27017
    }

    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def _get_process_info(self, pid: int) -> Dict[str, str]:
        """Get process name and path for a PID."""
        if pid == 0 or pid is None:
            return {'name': 'System', 'path': ''}

        try:
            proc = psutil.Process(pid)
            return {
                'name': proc.name(),
                'path': proc.exe() if proc.exe() else ''
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return {'name': 'Unknown', 'path': ''}

    def _is_external_ip(self, ip: str) -> bool:
        """Check if an IP address is external (not local/private)."""
        if not ip or ip in ('', '*', '0.0.0.0', '::'):
            return False

        try:
            # Check for loopback
            if ip.startswith('127.') or ip == '::1':
                return False

            # Check for private ranges
            if ip.startswith('10.'):
                return False
            if ip.startswith('192.168.'):
                return False
            if ip.startswith('172.'):
                parts = ip.split('.')
                if len(parts) >= 2:
                    second_octet = int(parts[1])
                    if 16 <= second_octet <= 31:
                        return False

            # Check for link-local
            if ip.startswith('169.254.'):
                return False
            if ip.startswith('fe80:'):
                return False

            return True
        except Exception:
            return False

    def _check_orphaned(self, pid: int) -> bool:
        """Check if a connection is orphaned (process no longer exists)."""
        if pid == 0 or pid is None:
            return True

        try:
            psutil.Process(pid)
            return False
        except psutil.NoSuchProcess:
            return True

    def _get_severity(self, flags: List[str]) -> str:
        """Determine severity based on flags."""
        if 'orphaned' in flags and 'external_ip' in flags:
            return 'Critical'
        if 'suspicious_port' in flags:
            return 'Critical'
        if 'orphaned' in flags:
            return 'Warning'
        if 'external_ip' in flags and 'unknown_process' in flags:
            return 'Warning'
        if flags:
            return 'Warning'
        return 'OK'

    def _format_address(self, addr) -> tuple:
        """Format address tuple to string and port."""
        if addr:
            return (addr.ip if hasattr(addr, 'ip') else str(addr[0]),
                    addr.port if hasattr(addr, 'port') else addr[1])
        return ('*', 0)

    def scan(self) -> List[Dict[str, Any]]:
        """Scan all network connections for suspicious activity."""
        self.items = []

        try:
            connections = psutil.net_connections(kind='all')
        except psutil.AccessDenied:
            # Without admin, we can only see our own connections
            try:
                connections = psutil.net_connections(kind='inet')
            except psutil.AccessDenied:
                return self.items

        for conn in connections:
            try:
                flags = []
                details_parts = []

                # Get addresses
                local_addr, local_port = self._format_address(conn.laddr)
                remote_addr, remote_port = self._format_address(conn.raddr)

                # Get process info
                pid = conn.pid if conn.pid else 0
                proc_info = self._get_process_info(pid)

                # Check for orphaned connection
                if self._check_orphaned(pid):
                    flags.append('orphaned')
                    details_parts.append('Process no longer exists')

                # Check for suspicious ports
                if local_port in self.SUSPICIOUS_PORTS:
                    flags.append('suspicious_port')
                    details_parts.append(f'Suspicious local port {local_port}')
                if remote_port in self.SUSPICIOUS_PORTS:
                    flags.append('suspicious_port')
                    details_parts.append(f'Suspicious remote port {remote_port}')

                # Check for external IP connections
                if self._is_external_ip(remote_addr):
                    flags.append('external_ip')
                    if proc_info['name'] == 'Unknown':
                        flags.append('unknown_process')
                        details_parts.append('External connection from unknown process')

                # Check for listening on all interfaces
                if local_addr in ('0.0.0.0', '::') and conn.status == 'LISTEN':
                    flags.append('listening_all')
                    details_parts.append('Listening on all interfaces')

                # Determine protocol
                protocol = 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP'

                # Get status
                status = conn.status if hasattr(conn, 'status') and conn.status else 'N/A'

                severity = self._get_severity(flags)

                # Format addresses for display
                local_display = f"{local_addr}:{local_port}" if local_port else local_addr
                remote_display = f"{remote_addr}:{remote_port}" if remote_port else remote_addr

                self.items.append({
                    'protocol': protocol,
                    'local_address': local_addr,
                    'local_port': local_port,
                    'remote_address': remote_addr,
                    'remote_port': remote_port,
                    'local_display': local_display,
                    'remote_display': remote_display,
                    'status': status,
                    'pid': pid,
                    'process_name': proc_info['name'],
                    'process_path': proc_info['path'],
                    'flags': flags,
                    'severity': severity,
                    'details': '; '.join(details_parts) if details_parts else 'Normal connection'
                })

            except Exception:
                continue

        # Sort by severity (Critical first, then Warning, then OK)
        severity_order = {'Critical': 0, 'Warning': 1, 'OK': 2}
        self.items.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return self.items

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts."""
        summary = {
            'total': len(self.items),
            'suspicious': 0,
            'orphaned': 0,
            'external': 0,
            'listening': 0,
            'Critical': 0,
            'Warning': 0,
            'OK': 0
        }

        for item in self.items:
            severity = item.get('severity', 'OK')
            summary[severity] = summary.get(severity, 0) + 1

            flags = item.get('flags', [])
            if 'suspicious_port' in flags:
                summary['suspicious'] += 1
            if 'orphaned' in flags:
                summary['orphaned'] += 1
            if 'external_ip' in flags:
                summary['external'] += 1
            if item.get('status') == 'LISTEN':
                summary['listening'] += 1

        return summary
