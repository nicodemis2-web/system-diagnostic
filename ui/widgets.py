"""Custom widgets for the diagnostic tool UI."""

import customtkinter as ctk
from typing import List, Dict, Any, Optional, Callable


# Professional color scheme inspired by enterprise tech design
class Colors:
    """Professional color palette."""
    # Primary colors
    PRIMARY_BLUE = "#2ea3f2"
    PRIMARY_BLUE_HOVER = "#1a8cd8"
    PRIMARY_BLUE_DARK = "#1e6fa8"

    # Backgrounds
    BG_DARK = "#1a1a2e"
    BG_DARKER = "#12121f"
    BG_CARD = "#232340"
    BG_CARD_ALT = "#1e1e35"
    BG_HEADER = "#16213e"

    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0b0"
    TEXT_MUTED = "#6c6c7c"

    # Status colors
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#3b82f6"

    # Borders
    BORDER = "#2a2a45"
    BORDER_LIGHT = "#3a3a55"


class StatusIndicator(ctk.CTkFrame):
    """A colored status indicator widget."""

    COLORS = {
        'critical': Colors.DANGER,
        'high': Colors.DANGER,
        'warning': Colors.WARNING,
        'medium': Colors.WARNING,
        'ok': Colors.SUCCESS,
        'low': Colors.SUCCESS,
        'info': Colors.INFO,
        'unknown': Colors.TEXT_MUTED
    }

    def __init__(self, master, status: str = 'ok', text: str = '', **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="transparent")

        color = self.COLORS.get(status.lower(), self.COLORS['unknown'])

        self.indicator = ctk.CTkLabel(
            self,
            text="●",
            text_color=color,
            font=ctk.CTkFont(size=12)
        )
        self.indicator.pack(side="left", padx=(0, 6))

        if text:
            self.label = ctk.CTkLabel(
                self,
                text=text,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=Colors.TEXT_PRIMARY
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

        self.configure(
            corner_radius=8,
            fg_color=Colors.BG_CARD,
            border_width=1,
            border_color=Colors.BORDER
        )

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        self.title_label.pack(pady=(20, 8), padx=20)

        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=350,
            height=8,
            corner_radius=4,
            progress_color=Colors.PRIMARY_BLUE,
            fg_color=Colors.BG_DARKER
        )
        self.progress_bar.pack(pady=12, padx=20)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text="Initializing...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Colors.TEXT_SECONDARY
        )
        self.status_label.pack(pady=(0, 20), padx=20)

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

        self.configure(fg_color="transparent")

        self.columns = columns
        self.rows: List[ctk.CTkFrame] = []
        self.header_frame: Optional[ctk.CTkFrame] = None
        self.col_count = len(columns)

        # Create header
        self._create_header()

    def _create_header(self):
        """Create the table header row."""
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_HEADER,
            corner_radius=6
        )
        self.header_frame.pack(fill="x", pady=(0, 4))

        # Configure grid columns for header
        for i in range(self.col_count):
            self.header_frame.grid_columnconfigure(i, weight=1, uniform="col")

        for i, col in enumerate(self.columns):
            label = ctk.CTkLabel(
                self.header_frame,
                text=col.upper(),
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w",
                justify="left"
            )
            label.grid(row=0, column=i, sticky="w", padx=12, pady=12)

    def clear(self):
        """Clear all data rows."""
        for row in self.rows:
            row.destroy()
        self.rows = []

    def add_row(self, values: List[str], severity: str = 'ok'):
        """Add a row to the table."""
        # Alternate row colors
        if len(self.rows) % 2 == 0:
            bg_color = Colors.BG_CARD
        else:
            bg_color = Colors.BG_CARD_ALT

        row_frame = ctk.CTkFrame(
            self,
            fg_color=bg_color,
            corner_radius=4
        )
        row_frame.pack(fill="x", pady=1)

        # Configure grid columns for row
        for i in range(self.col_count):
            row_frame.grid_columnconfigure(i, weight=1, uniform="col")

        for i, value in enumerate(values):
            # Check if this is a severity column
            if i < len(self.columns) and self.columns[i].lower() in ['severity', 'impact']:
                indicator = StatusIndicator(row_frame, status=str(value), text=str(value))
                indicator.grid(row=0, column=i, sticky="w", padx=12, pady=10)
            else:
                label = ctk.CTkLabel(
                    row_frame,
                    text=str(value),
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=Colors.TEXT_PRIMARY,
                    anchor="w",
                    justify="left"
                )
                label.grid(row=0, column=i, sticky="w", padx=12, pady=10)

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
    """A summary card widget showing key metrics. Clickable to view details."""

    def __init__(self, master, title: str, value: str, subtitle: str = '', status: str = 'info', command: Callable = None, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command
        self.default_bg = Colors.BG_CARD
        self.hover_bg = Colors.BG_CARD_ALT

        self.configure(
            corner_radius=8,
            fg_color=self.default_bg,
            border_width=1,
            border_color=Colors.BORDER,
            cursor="hand2" if command else "arrow"
        )

        self.title_label = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=Colors.TEXT_MUTED
        )
        self.title_label.pack(pady=(16, 4), padx=16, anchor="w")

        # Status color
        colors = {
            'critical': Colors.DANGER,
            'warning': Colors.WARNING,
            'ok': Colors.SUCCESS,
            'info': Colors.PRIMARY_BLUE
        }
        color = colors.get(status.lower(), colors['info'])

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=color
        )
        self.value_label.pack(pady=(0, 4), padx=16, anchor="w")

        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=Colors.TEXT_SECONDARY
            )
            self.subtitle_label.pack(pady=(0, 12), padx=16, anchor="w")
        else:
            self.value_label.pack_configure(pady=(0, 12))

        # "View details" link
        self.details_label = ctk.CTkLabel(
            self,
            text="View details →",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Colors.PRIMARY_BLUE
        )
        self.details_label.pack(pady=(0, 16), padx=16, anchor="w")

        # Bind click events to card and all children
        if command:
            self._bind_click_events()

    def _bind_click_events(self):
        """Bind click and hover events to card and children."""
        widgets = [self, self.title_label, self.value_label, self.details_label]
        if hasattr(self, 'subtitle_label'):
            widgets.append(self.subtitle_label)

        for widget in widgets:
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_click(self, event):
        """Handle click event."""
        if self.command:
            self.command()

    def _on_enter(self, event):
        """Handle mouse enter - show hover state."""
        self.configure(fg_color=self.hover_bg, border_color=Colors.PRIMARY_BLUE)

    def _on_leave(self, event):
        """Handle mouse leave - restore normal state."""
        self.configure(fg_color=self.default_bg, border_color=Colors.BORDER)

    def set_command(self, command: Callable):
        """Set or update the click command."""
        self.command = command
        self.configure(cursor="hand2" if command else "arrow")
        if command:
            self._bind_click_events()

    def update_value(self, value: str, status: str = None):
        """Update the displayed value."""
        self.value_label.configure(text=value)
        if status:
            colors = {
                'critical': Colors.DANGER,
                'warning': Colors.WARNING,
                'ok': Colors.SUCCESS,
                'info': Colors.PRIMARY_BLUE
            }
            color = colors.get(status.lower(), colors['info'])
            self.value_label.configure(text_color=color)


class ActionButton(ctk.CTkButton):
    """A styled action button."""

    def __init__(self, master, text: str, icon: str = '', command: Callable = None, style: str = 'primary', **kwargs):
        # Set colors based on style
        if style == 'primary':
            fg_color = Colors.PRIMARY_BLUE
            hover_color = Colors.PRIMARY_BLUE_HOVER
            text_color = Colors.TEXT_PRIMARY
        elif style == 'secondary':
            fg_color = Colors.BG_CARD
            hover_color = Colors.BG_CARD_ALT
            text_color = Colors.TEXT_PRIMARY
        elif style == 'success':
            fg_color = Colors.SUCCESS
            hover_color = "#0ea572"
            text_color = Colors.TEXT_PRIMARY
        elif style == 'danger':
            fg_color = Colors.DANGER
            hover_color = "#dc2626"
            text_color = Colors.TEXT_PRIMARY
        else:
            fg_color = Colors.PRIMARY_BLUE
            hover_color = Colors.PRIMARY_BLUE_HOVER
            text_color = Colors.TEXT_PRIMARY

        display_text = f"{icon}  {text}" if icon else text

        super().__init__(
            master,
            text=display_text,
            command=command,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            corner_radius=6,
            height=42,
            border_width=0,
            **kwargs
        )


class SectionHeader(ctk.CTkFrame):
    """A section header with title and optional subtitle."""

    def __init__(self, master, title: str, subtitle: str = '', **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="transparent")

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        self.title_label.pack(anchor="w")

        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=Colors.TEXT_SECONDARY
            )
            self.subtitle_label.pack(anchor="w", pady=(2, 0))
