"""Results panel with tabbed interface for diagnostic results."""

import customtkinter as ctk
from typing import Dict, List, Any, Optional
from ui.widgets import ResultsTable, SummaryCard, StatusIndicator, Colors


class ResultsPanel(ctk.CTkFrame):
    """Tabbed panel for displaying diagnostic results."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="transparent")

        # Create tabview
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=8,
            fg_color=Colors.BG_DARK,
            segmented_button_fg_color=Colors.BG_CARD,
            segmented_button_selected_color=Colors.PRIMARY_BLUE,
            segmented_button_selected_hover_color=Colors.PRIMARY_BLUE_HOVER,
            segmented_button_unselected_color=Colors.BG_CARD,
            segmented_button_unselected_hover_color=Colors.BG_CARD_ALT,
            text_color=Colors.TEXT_PRIMARY,
            text_color_disabled=Colors.TEXT_MUTED
        )
        self.tabview.pack(fill="both", expand=True, padx=8, pady=8)

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
            'Hidden Proc': ['PID', 'Name', 'Path', 'Detection', 'Flags', 'Severity'],
            'Hidden Files': ['Type', 'Path', 'Attributes', 'Size', 'Severity'],
            'Network': ['Protocol', 'Local', 'Remote', 'Process', 'Status', 'Severity'],
            'Summary': []  # Special tab
        }

        for tab_name, columns in tab_configs.items():
            tab = self.tabview.add(tab_name)
            tab.configure(fg_color="transparent")
            self.tabs[tab_name] = tab

            if columns:  # Regular results tab
                table = ResultsTable(tab, columns=columns)
                table.pack(fill="both", expand=True, padx=4, pady=4)
                self.tables[tab_name] = table
            else:  # Summary tab
                self._setup_summary_tab(tab)

    def _setup_summary_tab(self, tab):
        """Set up the summary tab with overview cards."""
        # Main container with scrolling
        main_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        # Top frame for summary cards
        self.summary_cards_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        self.summary_cards_frame.pack(fill="x", padx=8, pady=(8, 16))

        # Create placeholder cards with click handlers to navigate to tabs
        self.summary_cards = {}

        # Map card keys to tab names
        card_to_tab = {
            'startup': 'Startup',
            'services': 'Services',
            'processes': 'Processes',
            'disk': 'Disk',
            'drivers': 'Drivers',
            'tasks': 'Tasks',
            'hidden_processes': 'Hidden Proc',
            'hidden_files': 'Hidden Files',
            'network': 'Network'
        }

        cards_config = [
            ('startup', 'Startup Items', '—', 'Programs starting with Windows'),
            ('services', 'Third-Party Services', '—', 'Non-Microsoft auto-start services'),
            ('processes', 'High Resource', '—', 'Processes using significant resources'),
            ('disk', 'Disk Issues', '—', 'Drives with low space or issues'),
            ('drivers', 'Driver Problems', '—', 'Drivers with errors'),
            ('tasks', 'Scheduled Tasks', '—', 'Third-party scheduled tasks'),
            ('hidden_processes', 'Hidden Processes', '—', 'Suspicious or hidden processes'),
            ('hidden_files', 'Hidden Files/Dirs', '—', 'Hidden directories and ADS'),
            ('network', 'Network Issues', '—', 'Suspicious connections')
        ]

        for i, (key, title, value, subtitle) in enumerate(cards_config):
            # Create click handler for this card
            tab_name = card_to_tab[key]
            command = lambda t=tab_name: self.select_tab(t)

            card = SummaryCard(
                self.summary_cards_frame,
                title=title,
                value=value,
                subtitle=subtitle,
                status='info',
                command=command
            )
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
            self.summary_cards[key] = card

        # Configure grid weights
        for i in range(3):
            self.summary_cards_frame.columnconfigure(i, weight=1)
        self.summary_cards_frame.rowconfigure(0, weight=1)
        self.summary_cards_frame.rowconfigure(1, weight=1)
        self.summary_cards_frame.rowconfigure(2, weight=1)

        # Recommendations section header
        rec_header = ctk.CTkLabel(
            main_scroll,
            text="RECOMMENDATIONS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=Colors.TEXT_MUTED
        )
        rec_header.pack(anchor="w", padx=16, pady=(8, 12))

        # Recommendations frame
        self.recommendations_frame = ctk.CTkFrame(
            main_scroll,
            fg_color=Colors.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=Colors.BORDER
        )
        self.recommendations_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.recommendations_list = ctk.CTkFrame(
            self.recommendations_frame,
            fg_color="transparent"
        )
        self.recommendations_list.pack(fill="both", expand=True, padx=12, pady=12)

        # Initial empty state message
        self._add_recommendation('info', 'Run a scan to see recommendations for improving system performance.')

    def load_startup_results(self, data: List[Dict[str, Any]]):
        """Load startup analysis results."""
        if 'Startup' in self.tables:
            table = self.tables['Startup']
            table.clear()
            for item in data:
                path = item.get('path', '')
                if len(path) > 50:
                    path = path[:50] + '...'
                table.add_row([
                    item.get('name', ''),
                    path,
                    item.get('source', ''),
                    item.get('impact', 'Low')
                ], item.get('impact', 'Low'))

    def load_services_results(self, data: List[Dict[str, Any]]):
        """Load services analysis results."""
        if 'Services' in self.tables:
            table = self.tables['Services']
            table.clear()
            for item in data:
                display_name = item.get('display_name', '')
                if len(display_name) > 30:
                    display_name = display_name[:30] + '...'
                table.add_row([
                    item.get('name', ''),
                    display_name,
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
                name = item.get('name', '')
                if len(name) > 40:
                    name = name[:40] + '...'
                table.add_row([
                    name,
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

    def load_hidden_processes_results(self, data: List[Dict[str, Any]]):
        """Load hidden process analysis results."""
        if 'Hidden Proc' in self.tables:
            table = self.tables['Hidden Proc']
            table.clear()
            for item in data:
                path = item.get('path', '')
                if len(path) > 40:
                    path = '...' + path[-37:]
                flags = ', '.join(item.get('flags', []))
                if len(flags) > 30:
                    flags = flags[:27] + '...'
                table.add_row([
                    str(item.get('pid', '')),
                    item.get('name', ''),
                    path,
                    item.get('detection_method', ''),
                    flags,
                    item.get('severity', 'OK')
                ], item.get('severity', 'OK'))

    def load_hidden_files_results(self, data: List[Dict[str, Any]]):
        """Load hidden files/directories analysis results."""
        if 'Hidden Files' in self.tables:
            table = self.tables['Hidden Files']
            table.clear()
            for item in data:
                path = item.get('path', '')
                if len(path) > 50:
                    path = '...' + path[-47:]
                table.add_row([
                    item.get('type', ''),
                    path,
                    item.get('attributes', ''),
                    item.get('size', ''),
                    item.get('severity', 'OK')
                ], item.get('severity', 'OK'))

    def load_network_results(self, data: List[Dict[str, Any]]):
        """Load network connection analysis results."""
        if 'Network' in self.tables:
            table = self.tables['Network']
            table.clear()
            for item in data:
                local = item.get('local_display', '')
                remote = item.get('remote_display', '')
                if len(local) > 25:
                    local = local[:22] + '...'
                if len(remote) > 25:
                    remote = remote[:22] + '...'
                process = item.get('process_name', '')
                if item.get('pid'):
                    process = f"{process} ({item.get('pid')})"
                table.add_row([
                    item.get('protocol', ''),
                    local,
                    remote,
                    process,
                    item.get('status', ''),
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

        # Update hidden processes card
        if 'hidden_processes' in summaries:
            s = summaries['hidden_processes']
            count = s.get('total', 0)
            critical = s.get('Critical', 0)
            warning = s.get('Warning', 0)
            status = 'critical' if critical > 0 else 'warning' if warning > 0 else 'ok'
            self.summary_cards['hidden_processes'].update_value(str(count), status)

        # Update hidden files card
        if 'hidden_files' in summaries:
            s = summaries['hidden_files']
            suspicious = s.get('suspicious', 0)
            status = 'warning' if suspicious > 0 else 'ok'
            self.summary_cards['hidden_files'].update_value(str(suspicious), status)

        # Update network card
        if 'network' in summaries:
            s = summaries['network']
            scan_error = s.get('scan_error')
            if scan_error:
                # Show error state if scan failed/timed out
                self.summary_cards['network'].update_value('!', 'warning')
            else:
                issues = s.get('suspicious', 0) + s.get('orphaned', 0)
                critical = s.get('Critical', 0)
                status = 'critical' if critical > 0 else 'warning' if issues > 0 else 'ok'
                self.summary_cards['network'].update_value(str(issues), status)

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
                recommendations.append(('critical', f"You have {high_impact} high-impact startup programs. Consider disabling unnecessary ones in Task Manager → Startup tab."))
            elif high_impact > 2:
                recommendations.append(('warning', f"You have {high_impact} high-impact startup programs that may slow boot time."))

        # Check services
        if 'services' in summaries:
            third_party = summaries['services'].get('third_party', 0)
            if third_party > 15:
                recommendations.append(('warning', f"You have {third_party} third-party services set to auto-start. Review and disable unnecessary services using services.msc."))

        # Check processes
        if 'processes' in summaries:
            critical = summaries['processes'].get('Critical', 0)
            if critical > 0:
                recommendations.append(('critical', f"{critical} process(es) are using excessive resources. Check the Processes tab for details."))

        # Check disk
        if 'disk' in summaries:
            if summaries['disk'].get('smart_warnings', 0) > 0:
                recommendations.append(('critical', "SMART warnings detected! Back up your data immediately and consider replacing the affected drive."))
            if summaries['disk'].get('low_space_drives', 0) > 0:
                recommendations.append(('warning', "Low disk space detected on one or more drives. Free up space to improve system performance."))

        # Check drivers
        if 'drivers' in summaries:
            critical_drivers = summaries['drivers'].get('critical', 0)
            if critical_drivers > 0:
                recommendations.append(('critical', f"{critical_drivers} driver(s) have errors. Update or reinstall affected drivers from Device Manager."))

        # Check scheduled tasks
        if 'scheduled' in summaries:
            warnings = summaries['scheduled'].get('warnings', 0)
            if warnings > 0:
                recommendations.append(('info', f"{warnings} scheduled task(s) run at startup which may affect boot performance."))

        # Check hidden processes
        if 'hidden_processes' in summaries:
            s = summaries['hidden_processes']
            critical = s.get('Critical', 0)
            discrepancies = s.get('discrepancies', 0)
            mimicry = s.get('mimicry', 0)
            if mimicry > 0:
                recommendations.append(('critical', f"{mimicry} process(es) detected with names mimicking system processes. This may indicate malware."))
            if discrepancies > 0:
                recommendations.append(('critical', f"{discrepancies} process(es) found hiding from standard enumeration APIs. Investigate immediately."))
            if critical > 0 and mimicry == 0 and discrepancies == 0:
                recommendations.append(('warning', f"{critical} suspicious process(es) detected. Check the Hidden Proc tab for details."))

        # Check hidden files
        if 'hidden_files' in summaries:
            s = summaries['hidden_files']
            suspicious = s.get('suspicious', 0)
            ads = s.get('ads', 0)
            if ads > 0:
                recommendations.append(('warning', f"{ads} Alternate Data Stream(s) found. These can be used to hide malicious content."))
            if suspicious > 0:
                recommendations.append(('warning', f"{suspicious} suspicious hidden director(ies) found outside known system locations."))

        # Check network connections
        if 'network' in summaries:
            s = summaries['network']
            scan_error = s.get('scan_error')
            if scan_error:
                recommendations.append(('warning', f"Network scan encountered an issue: {scan_error}. Try running as Administrator."))
            else:
                suspicious_ports = s.get('suspicious', 0)
                orphaned = s.get('orphaned', 0)
                if suspicious_ports > 0:
                    recommendations.append(('critical', f"{suspicious_ports} connection(s) using suspicious ports commonly used by malware. Investigate immediately."))
                if orphaned > 0:
                    recommendations.append(('warning', f"{orphaned} orphaned network connection(s) found (process no longer exists)."))

        # Add recommendations or show "all good" message
        if not recommendations:
            recommendations.append(('ok', "No significant issues found. Your system appears to be running well."))

        for status, text in recommendations:
            self._add_recommendation(status, text)

    def _add_recommendation(self, status: str, text: str):
        """Add a recommendation to the list."""
        frame = ctk.CTkFrame(
            self.recommendations_list,
            fg_color=Colors.BG_CARD_ALT,
            corner_radius=6
        )
        frame.pack(fill="x", pady=4)

        indicator = StatusIndicator(frame, status=status)
        indicator.pack(side="left", padx=12, pady=12)

        label = ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
            justify="left",
            wraplength=700
        )
        label.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=12)

    def select_tab(self, tab_name: str):
        """Select a specific tab."""
        if tab_name in self.tabs:
            self.tabview.set(tab_name)
