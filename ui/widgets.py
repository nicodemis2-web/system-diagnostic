"""Custom widgets for the diagnostic tool UI."""

import customtkinter as ctk
from typing import List, Dict, Any, Optional, Callable


class StatusIndicator(ctk.CTkFrame):
    """A colored status indicator widget."""

    COLORS = {
        'critical': '#dc3545',
        'high': '#dc3545',
        'warning': '#ffc107',
        'medium': '#ffc107',
        'ok': '#28a745',
        'low': '#28a745',
        'info': '#17a2b8',
        'unknown': '#6c757d'
    }

    def __init__(self, master, status: str = 'ok', text: str = '', **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="transparent")

        color = self.COLORS.get(status.lower(), self.COLORS['unknown'])

        self.indicator = ctk.CTkLabel(
            self,
            text="●",
            text_color=color,
            font=ctk.CTkFont(size=14)
        )
        self.indicator.pack(side="left", padx=(0, 5))

        if text:
            self.label = ctk.CTkLabel(
                self,
                text=text,
                font=ctk.CTkFont(size=12)
            )
            self.label.pack(side="left")

    def set_status(self, status: str, text: str = None):
        """Update the status indicator."""
        color = self.COLORS.get(status.lower(), self.COLORS['unknown'])
        self.indicator.configure(text_color=color)
        if text is not None and hasattr(self, 'label'):
            self.label.configure(text=text)


class ProgressCard(ctk.CTkFrame):
    """A card widget showing scan progress."""

    def __init__(self, master, title: str = "Scanning...", **kwargs):
        super().__init__(master, **kwargs)

        self.configure(corner_radius=10)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(pady=(15, 5), padx=15)

        self.progress_bar = ctk.CTkProgressBar(self, width=300)
        self.progress_bar.pack(pady=10, padx=15)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text="Initializing...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 15), padx=15)

    def set_progress(self, value: float, status: str = None):
        """Update progress (0.0 to 1.0) and optional status text."""
        self.progress_bar.set(value)
        if status:
            self.status_label.configure(text=status)

    def set_title(self, title: str):
        """Update the title."""
        self.title_label.configure(text=title)


class ResultsTable(ctk.CTkScrollableFrame):
    """A scrollable table widget for displaying results."""

    def __init__(self, master, columns: List[str], **kwargs):
        super().__init__(master, **kwargs)

        self.columns = columns
        self.rows: List[ctk.CTkFrame] = []
        self.header_frame: Optional[ctk.CTkFrame] = None

        # Create header
        self._create_header()

    def _create_header(self):
        """Create the table header row."""
        self.header_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray25"))
        self.header_frame.pack(fill="x", pady=(0, 2))

        for i, col in enumerate(self.columns):
            label = ctk.CTkLabel(
                self.header_frame,
                text=col,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            label.pack(side="left", fill="x", expand=True, padx=10, pady=8)

    def clear(self):
        """Clear all data rows."""
        for row in self.rows:
            row.destroy()
        self.rows = []

    def add_row(self, values: List[str], severity: str = 'ok'):
        """Add a row to the table."""
        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.pack(fill="x", pady=1)

        # Alternate row colors
        if len(self.rows) % 2 == 0:
            row_frame.configure(fg_color=("gray95", "gray17"))

        for i, value in enumerate(values):
            # Check if this is a severity column
            if i < len(self.columns) and self.columns[i].lower() in ['severity', 'impact', 'status']:
                indicator = StatusIndicator(row_frame, status=str(value), text=str(value))
                indicator.pack(side="left", fill="x", expand=True, padx=10, pady=6)
            else:
                label = ctk.CTkLabel(
                    row_frame,
                    text=str(value),
                    font=ctk.CTkFont(size=11),
                    anchor="w"
                )
                label.pack(side="left", fill="x", expand=True, padx=10, pady=6)

        self.rows.append(row_frame)

    def load_data(self, data: List[Dict[str, Any]], key_mapping: Optional[Dict[str, str]] = None):
        """Load data from a list of dictionaries."""
        self.clear()

        for item in data:
            values = []
            severity = 'ok'

            for col in self.columns:
                # Use key mapping if provided
                key = key_mapping.get(col, col.lower().replace(' ', '_')) if key_mapping else col.lower().replace(' ', '_')
                value = item.get(key, '')

                # Check for severity
                if col.lower() in ['severity', 'impact']:
                    severity = str(value).lower()

                values.append(value)

            self.add_row(values, severity)


class SummaryCard(ctk.CTkFrame):
    """A summary card widget showing key metrics."""

    def __init__(self, master, title: str, value: str, subtitle: str = '', status: str = 'info', **kwargs):
        super().__init__(master, **kwargs)

        self.configure(corner_radius=10)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        self.title_label.pack(pady=(15, 5), padx=15)

        # Status color
        colors = {
            'critical': '#dc3545',
            'warning': '#ffc107',
            'ok': '#28a745',
            'info': '#17a2b8'
        }
        color = colors.get(status.lower(), colors['info'])

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color
        )
        self.value_label.pack(pady=0, padx=15)

        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray60")
            )
            self.subtitle_label.pack(pady=(0, 15), padx=15)
        else:
            self.value_label.pack_configure(pady=(0, 15))

    def update_value(self, value: str, status: str = None):
        """Update the displayed value."""
        self.value_label.configure(text=value)
        if status:
            colors = {
                'critical': '#dc3545',
                'warning': '#ffc107',
                'ok': '#28a745',
                'info': '#17a2b8'
            }
            color = colors.get(status.lower(), colors['info'])
            self.value_label.configure(text_color=color)


class ActionButton(ctk.CTkButton):
    """A styled action button."""

    def __init__(self, master, text: str, icon: str = '', command: Callable = None, style: str = 'primary', **kwargs):
        # Set colors based on style
        colors = {
            'primary': ("#1a73e8", "#1557b0"),
            'secondary': ("gray70", "gray30"),
            'success': ("#28a745", "#1e7b34"),
            'danger': ("#dc3545", "#a71d2a")
        }
        fg_color = colors.get(style, colors['primary'])

        display_text = f"{icon} {text}" if icon else text

        super().__init__(
            master,
            text=display_text,
            command=command,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=fg_color[0],
            hover_color=fg_color[1],
            corner_radius=8,
            height=40,
            **kwargs
        )
