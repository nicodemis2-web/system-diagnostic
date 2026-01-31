"""Results panel with tabbed interface for diagnostic results."""

import customtkinter as ctk
from typing import Dict, List, Any, Optional
from ui.widgets import ResultsTable, SummaryCard, StatusIndicator


class ResultsPanel(ctk.CTkFrame):
    """Tabbed panel for displaying diagnostic results."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="transparent")

        # Create tabview
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)

        # Create tabs
        self.tabs = {}
        self.tables = {}

        self._create_tabs()

    def _create_tabs(self):
        """Create all result tabs."""
        tab_configs = {
            'Startup': ['Name', 'Path', 'Source', 'Impact'],
            'Services': ['Name', 'Display Name', 'Status', 'Type', 'Severity'],
            'Processes': ['PID', 'Name', 'CPU %', 'Memory (MB)', 'Disk Read', 'Disk Write', 'Severity'],
            'Disk': ['Drive', 'File System', 'Total', 'Used', 'Free', 'SMART', 'Severity'],
            'Drivers': ['Name', 'Status', 'Error', 'Severity'],
            'Tasks': ['Name', 'Status', 'Trigger', 'Last Run', 'Type', 'Severity'],
            'Summary': []  # Special tab
        }

        for tab_name, columns in tab_configs.items():
            tab = self.tabview.add(tab_name)
            self.tabs[tab_name] = tab

            if columns:  # Regular results tab
                table = ResultsTable(tab, columns=columns)
                table.pack(fill="both", expand=True, padx=5, pady=5)
                self.tables[tab_name] = table
            else:  # Summary tab
                self._setup_summary_tab(tab)

    def _setup_summary_tab(self, tab):
        """Set up the summary tab with overview cards."""
        # Top frame for summary cards
        self.summary_cards_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.summary_cards_frame.pack(fill="x", padx=10, pady=10)

        # Create placeholder cards
        self.summary_cards = {}

        cards_config = [
            ('startup', 'Startup Items', '0', 'Programs starting with Windows'),
            ('services', 'Third-Party Services', '0', 'Non-Microsoft auto-start services'),
            ('processes', 'High Resource', '0', 'Processes using significant resources'),
            ('disk', 'Disk Issues', '0', 'Drives with low space or issues'),
            ('drivers', 'Driver Problems', '0', 'Drivers with errors'),
            ('tasks', 'Scheduled Tasks', '0', 'Third-party scheduled tasks')
        ]

        for i, (key, title, value, subtitle) in enumerate(cards_config):
            card = SummaryCard(
                self.summary_cards_frame,
                title=title,
                value=value,
                subtitle=subtitle,
                status='info'
            )
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            self.summary_cards[key] = card

        # Configure grid weights
        for i in range(3):
            self.summary_cards_frame.columnconfigure(i, weight=1)
        self.summary_cards_frame.rowconfigure(0, weight=1)
        self.summary_cards_frame.rowconfigure(1, weight=1)

        # Recommendations frame
        self.recommendations_frame = ctk.CTkFrame(tab)
        self.recommendations_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        rec_label = ctk.CTkLabel(
            self.recommendations_frame,
            text="Recommendations",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        rec_label.pack(anchor="w", padx=15, pady=(15, 10))

        self.recommendations_list = ctk.CTkScrollableFrame(
            self.recommendations_frame,
            fg_color="transparent"
        )
        self.recommendations_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def load_startup_results(self, data: List[Dict[str, Any]]):
        """Load startup analysis results."""
        if 'Startup' in self.tables:
            table = self.tables['Startup']
            table.clear()
            for item in data:
                table.add_row([
                    item.get('name', ''),
                    item.get('path', '')[:50] + '...' if len(item.get('path', '')) > 50 else item.get('path', ''),
                    item.get('source', ''),
                    item.get('impact', 'Low')
                ], item.get('impact', 'Low'))

    def load_services_results(self, data: List[Dict[str, Any]]):
        """Load services analysis results."""
        if 'Services' in self.tables:
            table = self.tables['Services']
            table.clear()
            for item in data:
                table.add_row([
                    item.get('name', ''),
                    item.get('display_name', '')[:30] + '...' if len(item.get('display_name', '')) > 30 else item.get('display_name', ''),
                    item.get('status', ''),
                    item.get('type', ''),
                    item.get('severity', 'OK')
                ], item.get('severity', 'OK'))

    def load_processes_results(self, data: List[Dict[str, Any]]):
        """Load process analysis results."""
        if 'Processes' in self.tables:
            table = self.tables['Processes']
            table.clear()
            for item in data:
                table.add_row([
                    str(item.get('pid', '')),
                    item.get('name', ''),
                    str(item.get('cpu_percent', 0)),
                    str(item.get('memory_mb', 0)),
                    item.get('disk_read', ''),
                    item.get('disk_write', ''),
                    item.get('severity', 'OK')
                ], item.get('severity', 'OK'))

    def load_disk_results(self, data: List[Dict[str, Any]]):
        """Load disk analysis results."""
        if 'Disk' in self.tables:
            table = self.tables['Disk']
            table.clear()
            for item in data:
                table.add_row([
                    item.get('drive', ''),
                    item.get('file_system', ''),
                    item.get('total', ''),
                    item.get('used', ''),
                    item.get('free', ''),
                    item.get('smart_status', ''),
                    item.get('severity', 'OK')
                ], item.get('severity', 'OK'))

    def load_drivers_results(self, data: List[Dict[str, Any]]):
        """Load driver analysis results."""
        if 'Drivers' in self.tables:
            table = self.tables['Drivers']
            table.clear()
            for item in data:
                table.add_row([
                    item.get('name', '')[:40] + '...' if len(item.get('name', '')) > 40 else item.get('name', ''),
                    item.get('status', ''),
                    item.get('error_description', ''),
                    item.get('severity', 'OK')
                ], item.get('severity', 'OK'))

    def load_tasks_results(self, data: List[Dict[str, Any]]):
        """Load scheduled tasks results."""
        if 'Tasks' in self.tables:
            table = self.tables['Tasks']
            table.clear()
            for item in data:
                table.add_row([
                    item.get('name', ''),
                    item.get('status', ''),
                    item.get('trigger', ''),
                    item.get('last_run', ''),
                    item.get('type', ''),
                    item.get('severity', 'OK')
                ], item.get('severity', 'OK'))

    def update_summary(self, summaries: Dict[str, Dict[str, Any]]):
        """Update the summary tab with collected data."""
        # Update startup card
        if 'startup' in summaries:
            s = summaries['startup']
            high_count = s.get('High', 0)
            total = sum(s.values())
            status = 'warning' if high_count > 3 else 'ok' if high_count == 0 else 'info'
            self.summary_cards['startup'].update_value(str(total), status)

        # Update services card
        if 'services' in summaries:
            s = summaries['services']
            count = s.get('third_party', 0)
            status = 'warning' if count > 10 else 'ok'
            self.summary_cards['services'].update_value(str(count), status)

        # Update processes card
        if 'processes' in summaries:
            s = summaries['processes']
            critical = s.get('Critical', 0) + s.get('Warning', 0)
            status = 'critical' if s.get('Critical', 0) > 0 else 'warning' if critical > 0 else 'ok'
            self.summary_cards['processes'].update_value(str(critical), status)

        # Update disk card
        if 'disk' in summaries:
            s = summaries['disk']
            issues = s.get('low_space_drives', 0) + s.get('smart_warnings', 0)
            status = 'critical' if s.get('smart_warnings', 0) > 0 else 'warning' if issues > 0 else 'ok'
            self.summary_cards['disk'].update_value(str(issues), status)

        # Update drivers card
        if 'drivers' in summaries:
            s = summaries['drivers']
            issues = s.get('total_issues', 0)
            status = 'critical' if s.get('critical', 0) > 0 else 'warning' if issues > 0 else 'ok'
            self.summary_cards['drivers'].update_value(str(issues), status)

        # Update tasks card
        if 'scheduled' in summaries:
            s = summaries['scheduled']
            count = s.get('third_party', 0)
            status = 'warning' if s.get('warnings', 0) > 0 else 'ok'
            self.summary_cards['tasks'].update_value(str(count), status)

        # Generate recommendations
        self._generate_recommendations(summaries)

    def _generate_recommendations(self, summaries: Dict[str, Dict[str, Any]]):
        """Generate recommendations based on scan results."""
        # Clear existing recommendations
        for widget in self.recommendations_list.winfo_children():
            widget.destroy()

        recommendations = []

        # Check startup items
        if 'startup' in summaries:
            high_impact = summaries['startup'].get('High', 0)
            if high_impact > 5:
                recommendations.append(('critical', f"You have {high_impact} high-impact startup programs. Consider disabling unnecessary ones in Task Manager > Startup."))
            elif high_impact > 2:
                recommendations.append(('warning', f"You have {high_impact} high-impact startup programs that may slow boot time."))

        # Check services
        if 'services' in summaries:
            third_party = summaries['services'].get('third_party', 0)
            if third_party > 15:
                recommendations.append(('warning', f"You have {third_party} third-party services set to auto-start. Review and disable unnecessary services."))

        # Check processes
        if 'processes' in summaries:
            critical = summaries['processes'].get('Critical', 0)
            if critical > 0:
                recommendations.append(('critical', f"{critical} process(es) are using excessive resources. Check the Processes tab for details."))

        # Check disk
        if 'disk' in summaries:
            if summaries['disk'].get('smart_warnings', 0) > 0:
                recommendations.append(('critical', "SMART warnings detected! Back up your data immediately and consider replacing the drive."))
            if summaries['disk'].get('low_space_drives', 0) > 0:
                recommendations.append(('warning', "Low disk space detected. Free up space to improve system performance."))

        # Check drivers
        if 'drivers' in summaries:
            critical_drivers = summaries['drivers'].get('critical', 0)
            if critical_drivers > 0:
                recommendations.append(('critical', f"{critical_drivers} driver(s) have errors. Update or reinstall affected drivers."))

        # Check scheduled tasks
        if 'scheduled' in summaries:
            warnings = summaries['scheduled'].get('warnings', 0)
            if warnings > 0:
                recommendations.append(('info', f"{warnings} scheduled task(s) may affect startup performance."))

        # Add recommendations or show "all good" message
        if not recommendations:
            recommendations.append(('ok', "No significant issues found. Your system appears to be in good health."))

        for status, text in recommendations:
            self._add_recommendation(status, text)

    def _add_recommendation(self, status: str, text: str):
        """Add a recommendation to the list."""
        frame = ctk.CTkFrame(self.recommendations_list, fg_color=("gray90", "gray20"))
        frame.pack(fill="x", pady=3, padx=5)

        indicator = StatusIndicator(frame, status=status)
        indicator.pack(side="left", padx=(10, 5), pady=10)

        label = ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont(size=12),
            anchor="w",
            wraplength=600
        )
        label.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)

    def select_tab(self, tab_name: str):
        """Select a specific tab."""
        if tab_name in self.tabs:
            self.tabview.set(tab_name)
