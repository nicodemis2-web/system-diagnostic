#!/usr/bin/env python3
"""
Windows System Diagnostic Tool

A GUI application that identifies startup issues and problematic
applications causing system slowdowns on Windows.
"""

import sys
import os

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    """Main entry point for the application."""
    # Create and run the application
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
