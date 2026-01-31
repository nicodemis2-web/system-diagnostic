"""Utility functions for the diagnostic tool."""

from utils.admin import is_admin, run_as_admin
from utils.report import ReportGenerator

__all__ = [
    'is_admin',
    'run_as_admin',
    'ReportGenerator'
]
