"""Admin privilege handling utilities."""

import ctypes
import sys
import os


def is_admin() -> bool:
    """Check if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin(script_path: str = None) -> bool:
    """
    Attempt to restart the application with admin privileges.

    Args:
        script_path: Path to the script to run. Defaults to current script.

    Returns:
        True if elevation was requested, False if already admin or failed.
    """
    if is_admin():
        return False

    if script_path is None:
        script_path = sys.argv[0]

    try:
        # Use ShellExecuteW to trigger UAC elevation
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            f'"{script_path}"',
            None,
            1  # SW_SHOWNORMAL
        )
        return True
    except Exception:
        return False


def get_admin_status_text() -> str:
    """Get a human-readable admin status string."""
    if is_admin():
        return "Running as Administrator"
    return "Running as Standard User (some features limited)"
