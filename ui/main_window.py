"""Main application window."""

import customtkinter as ctk
import platform
import psutil
import threading
from typing import Optional, Callable
from tkinter import filedialog, messagebox

from ui.results_panel import ResultsPanel
from ui.widgets import ActionButton, ProgressCard, Colors
from utils.admin import is_admin, get_admin_status_text
from utils.report import ReportGenerator
from diagnostics import (
    StartupAnalyzer,
    ServicesAnalyzer,
    ProcessAnalyzer,
    DiskAnalyzer,
    DriverAnalyzer,
    ScheduledTasksAnalyzer,
    HiddenProcessAnalyzer,
    HiddenDirectoryAnalyzer,
    NetworkConnectionAnalyzer
)


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Windows System Diagnostic Tool")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Set appearance - use custom dark theme
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=Colors.BG_DARK)

        # Initialize analyzers
        self.startup_analyzer = StartupAnalyzer()
        self.services_analyzer = ServicesAnalyzer()
        self.process_analyzer = ProcessAnalyzer()
        self.disk_analyzer = DiskAnalyzer()
        self.driver_analyzer = DriverAnalyzer()
        self.scheduled_analyzer = ScheduledTasksAnalyzer()
        self.hidden_process_analyzer = HiddenProcessAnalyzer()
        self.hidden_directory_analyzer = HiddenDirectoryAnalyzer()
        self.network_analyzer = NetworkConnectionAnalyzer()

        # Report generator
        self.report_generator = ReportGenerator()

        # Scan state
        self.is_scanning = False
        self.scan_thread: Optional[threading.Thread] = None
        self.scan_results = {}
        self.summaries = {}

        # Build UI
        self._build_ui()

        # Update system info
        self._update_system_info()

    def _build_ui(self):
        """Build the main UI layout."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self._build_header()

        # Action bar
        self._build_action_bar()

        # Main content area
        self._build_main_content()

        # Status bar
        self._build_status_bar()

    def _build_header(self):
        """Build the header section with system info."""
        header_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_HEADER,
            corner_radius=0,
            height=70
        )
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)

        # Inner container for padding
        inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=0)

        # Left side - Title
        title_frame = ctk.CTkFrame(inner, fg_color="transparent")
        title_frame.pack(side="left", fill="y", pady=12)

        title_label = ctk.CTkLabel(
            title_frame,
            text="System Diagnostic",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Windows Performance & Health Analysis",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle_label.pack(anchor="w")

        # Right side - System info
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="right", fill="y", pady=12)

        self.system_info_label = ctk.CTkLabel(
            info_frame,
            text="Loading system info...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Colors.TEXT_SECONDARY,
            justify="right"
        )
        self.system_info_label.pack(anchor="e")

        # Admin status
        admin_text = "Administrator" if is_admin() else "Standard User"
        admin_color = Colors.SUCCESS if is_admin() else Colors.WARNING
        self.admin_label = ctk.CTkLabel(
            info_frame,
            text=f"● {admin_text}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=admin_color
        )
        self.admin_label.pack(anchor="e", pady=(4, 0))

    def _build_action_bar(self):
        """Build the action buttons bar."""
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=16)

        # Buttons container
        btn_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_container.pack(side="left")

        # Full scan button
        self.full_scan_btn = ActionButton(
            btn_container,
            text="Run Full Scan",
            icon="⬤",
            command=self._run_full_scan,
            style="primary",
            width=160
        )
        self.full_scan_btn.pack(side="left", padx=(0, 12))

        # Quick scan button
        self.quick_scan_btn = ActionButton(
            btn_container,
            text="Quick Scan",
            icon="◐",
            command=self._run_quick_scan,
            style="secondary",
            width=140
        )
        self.quick_scan_btn.pack(side="left", padx=(0, 12))

        # Export button
        self.export_btn = ActionButton(
            btn_container,
            text="Export Report",
            icon="↗",
            command=self._export_report,
            style="secondary",
            width=140
        )
        self.export_btn.pack(side="left")

        # Progress card (hidden by default)
        self.progress_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        self.progress_frame.pack(side="right")

        self.progress_card = ProgressCard(self.progress_frame, title="Scanning...")

    def _build_main_content(self):
        """Build the main content area with results panel."""
        content_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_DARKER,
            corner_radius=12
        )
        content_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 16))

        self.results_panel = ResultsPanel(content_frame)
        self.results_panel.pack(fill="both", expand=True, padx=2, pady=2)

    def _build_status_bar(self):
        """Build the status bar."""
        status_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_HEADER,
            corner_radius=0,
            height=36
        )
        status_frame.grid(row=3, column=0, sticky="ew")
        status_frame.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready  •  Click 'Run Full Scan' to analyze your system",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_SECONDARY
        )
        self.status_label.pack(side="left", padx=24, pady=8)

        # Version info
        version_label = ctk.CTkLabel(
            status_frame,
            text="v1.0.0",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.TEXT_MUTED
        )
        version_label.pack(side="right", padx=24, pady=8)

    def _update_system_info(self):
        """Update system information display."""
        try:
            # CPU info
            cpu_name = platform.processor() or "Unknown CPU"
            # Truncate long CPU names
            if len(cpu_name) > 40:
                cpu_name = cpu_name[:40] + "..."

            # RAM info
            ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)

            # OS info
            os_info = f"{platform.system()} {platform.release()}"

            info_text = f"{cpu_name}\n{ram_gb} GB RAM  •  {os_info}"

            self.system_info_label.configure(text=info_text)

            # Store for report
            self.system_info = {
                'CPU': cpu_name,
                'RAM': f"{ram_gb} GB",
                'OS': os_info,
                'Architecture': platform.machine()
            }

        except Exception as e:
            self.system_info_label.configure(text="System info unavailable")
            self.system_info = {}

    def _set_buttons_enabled(self, enabled: bool):
        """Enable or disable scan buttons."""
        state = "normal" if enabled else "disabled"
        self.full_scan_btn.configure(state=state)
        self.quick_scan_btn.configure(state=state)
        self.export_btn.configure(state=state)

    def _run_full_scan(self):
        """Run a full system scan."""
        if self.is_scanning:
            return

        self.is_scanning = True
        self._set_buttons_enabled(False)

        # Show progress
        self.progress_card.pack(fill="x", padx=0, pady=0)
        self.progress_card.set_progress(0, "Initializing full scan...")

        # Run scan in thread
        self.scan_thread = threading.Thread(target=self._perform_full_scan)
        self.scan_thread.daemon = True
        self.scan_thread.start()

    def _run_quick_scan(self):
        """Run a quick scan (startup and processes only)."""
        if self.is_scanning:
            return

        self.is_scanning = True
        self._set_buttons_enabled(False)

        # Show progress
        self.progress_card.pack(fill="x", padx=0, pady=0)
        self.progress_card.set_progress(0, "Initializing quick scan...")

        # Run scan in thread
        self.scan_thread = threading.Thread(target=self._perform_quick_scan)
        self.scan_thread.daemon = True
        self.scan_thread.start()

    def _perform_full_scan(self):
        """Perform full scan in background thread."""
        try:
            steps = [
                ("Analyzing startup programs...", self._scan_startup, 0.08),
                ("Scanning Windows services...", self._scan_services, 0.18),
                ("Monitoring process resources...", self._scan_processes, 0.35),
                ("Checking disk health...", self._scan_disk, 0.45),
                ("Analyzing drivers...", self._scan_drivers, 0.55),
                ("Scanning scheduled tasks...", self._scan_scheduled, 0.65),
                ("Detecting hidden processes...", self._scan_hidden_processes, 0.74),
                ("Scanning for hidden files...", self._scan_hidden_files, 0.86),
                ("Analyzing network connections...", self._scan_network, 0.95),
            ]

            for status, func, progress in steps:
                self.after(0, lambda s=status, p=progress: self.progress_card.set_progress(p, s))
                func()

            # Complete
            self.after(0, self._scan_complete)

        except Exception as e:
            self.after(0, lambda: self._scan_error(str(e)))

    def _perform_quick_scan(self):
        """Perform quick scan in background thread."""
        try:
            steps = [
                ("Analyzing startup programs...", self._scan_startup, 0.3),
                ("Monitoring process resources...", self._scan_processes, 0.7),
            ]

            for status, func, progress in steps:
                self.after(0, lambda s=status, p=progress: self.progress_card.set_progress(p, s))
                func()

            # Complete
            self.after(0, self._scan_complete)

        except Exception as e:
            self.after(0, lambda: self._scan_error(str(e)))

    def _scan_startup(self):
        """Scan startup programs."""
        results = self.startup_analyzer.scan()
        self.scan_results['startup'] = results
        self.summaries['startup'] = self.startup_analyzer.get_summary()
        self.after(0, lambda: self.results_panel.load_startup_results(results))

    def _scan_services(self):
        """Scan Windows services."""
        results = self.services_analyzer.scan()
        self.scan_results['services'] = results
        self.summaries['services'] = self.services_analyzer.get_summary()
        self.after(0, lambda: self.results_panel.load_services_results(results))

    def _scan_processes(self):
        """Scan running processes."""
        results = self.process_analyzer.scan()
        self.scan_results['processes'] = results
        self.summaries['processes'] = self.process_analyzer.get_summary()
        self.after(0, lambda: self.results_panel.load_processes_results(results))

    def _scan_disk(self):
        """Scan disk health."""
        results = self.disk_analyzer.scan()
        self.scan_results['disk'] = results
        self.summaries['disk'] = self.disk_analyzer.get_summary()
        self.after(0, lambda: self.results_panel.load_disk_results(results))

    def _scan_drivers(self):
        """Scan driver status."""
        results = self.driver_analyzer.scan()
        self.scan_results['drivers'] = results
        self.summaries['drivers'] = self.driver_analyzer.get_summary()
        self.after(0, lambda: self.results_panel.load_drivers_results(results))

    def _scan_scheduled(self):
        """Scan scheduled tasks."""
        results = self.scheduled_analyzer.scan()
        self.scan_results['scheduled'] = results
        self.summaries['scheduled'] = self.scheduled_analyzer.get_summary()
        self.after(0, lambda: self.results_panel.load_tasks_results(results))

    def _scan_hidden_processes(self):
        """Scan for hidden or suspicious processes."""
        results = self.hidden_process_analyzer.scan()
        self.scan_results['hidden_processes'] = results
        self.summaries['hidden_processes'] = self.hidden_process_analyzer.get_summary()
        self.after(0, lambda: self.results_panel.load_hidden_processes_results(results))

    def _scan_hidden_files(self):
        """Scan for hidden directories and ADS."""
        results = self.hidden_directory_analyzer.scan()
        self.scan_results['hidden_files'] = results
        self.summaries['hidden_files'] = self.hidden_directory_analyzer.get_summary()
        self.after(0, lambda: self.results_panel.load_hidden_files_results(results))

    def _scan_network(self):
        """Scan network connections."""
        results = self.network_analyzer.scan()
        self.scan_results['network'] = results
        self.summaries['network'] = self.network_analyzer.get_summary()
        self.after(0, lambda: self.results_panel.load_network_results(results))

    def _scan_complete(self):
        """Handle scan completion."""
        self.is_scanning = False
        self._set_buttons_enabled(True)

        # Hide progress
        self.progress_card.pack_forget()

        # Update summary
        self.results_panel.update_summary(self.summaries)

        # Switch to summary tab
        self.results_panel.select_tab("Summary")

        # Update status
        total_issues = (
            self.summaries.get('startup', {}).get('High', 0) +
            self.summaries.get('drivers', {}).get('critical', 0) +
            self.summaries.get('disk', {}).get('low_space_drives', 0) +
            self.summaries.get('hidden_processes', {}).get('Critical', 0) +
            self.summaries.get('hidden_files', {}).get('suspicious', 0) +
            self.summaries.get('network', {}).get('Critical', 0)
        )

        if total_issues > 0:
            self.status_label.configure(
                text=f"Scan complete  •  Found {total_issues} item(s) requiring attention",
                text_color=Colors.WARNING
            )
        else:
            self.status_label.configure(
                text="Scan complete  •  No critical issues found",
                text_color=Colors.SUCCESS
            )

    def _scan_error(self, error_msg: str):
        """Handle scan error."""
        self.is_scanning = False
        self._set_buttons_enabled(True)
        self.progress_card.pack_forget()
        self.status_label.configure(
            text=f"Scan error: {error_msg}",
            text_color=Colors.DANGER
        )
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error_msg}")

    def _export_report(self):
        """Export results to HTML report."""
        if not self.scan_results:
            messagebox.showwarning("No Data", "Please run a scan first before exporting.")
            return

        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            title="Save Diagnostic Report"
        )

        if not filepath:
            return

        try:
            # Set up report
            self.report_generator.set_system_info(self.system_info)

            # Add all results
            for category, results in self.scan_results.items():
                self.report_generator.add_results(category, results)

            # Save
            if self.report_generator.save_report(filepath):
                self.status_label.configure(
                    text=f"Report exported successfully",
                    text_color=Colors.SUCCESS
                )
                messagebox.showinfo("Export Complete", f"Report saved to:\n{filepath}")
            else:
                messagebox.showerror("Export Error", "Failed to save the report.")

        except Exception as e:
            messagebox.showerror("Export Error", f"Error saving report:\n{str(e)}")
