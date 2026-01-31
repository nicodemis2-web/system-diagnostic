"""Report generation utilities for exporting diagnostic results."""

import os
from datetime import datetime
from typing import Dict, List, Any
import html


class ReportGenerator:
    """Generates HTML reports from diagnostic results."""

    def __init__(self):
        self.results: Dict[str, List[Dict[str, Any]]] = {}
        self.system_info: Dict[str, str] = {}

    def set_system_info(self, info: Dict[str, str]):
        """Set system information for the report header."""
        self.system_info = info

    def add_results(self, category: str, items: List[Dict[str, Any]]):
        """Add diagnostic results for a category."""
        self.results[category] = items

    def _get_severity_color(self, severity: str) -> str:
        """Get CSS color for severity level."""
        colors = {
            'critical': '#dc3545',
            'high': '#dc3545',
            'warning': '#ffc107',
            'medium': '#ffc107',
            'ok': '#28a745',
            'low': '#28a745',
            'info': '#17a2b8'
        }
        return colors.get(severity.lower(), '#6c757d')

    def _escape(self, text: str) -> str:
        """HTML escape text."""
        return html.escape(str(text)) if text else ''

    def generate_html(self) -> str:
        """Generate complete HTML report."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Diagnostic Report - {timestamp}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        .header .timestamp {{
            opacity: 0.8;
            font-size: 14px;
        }}
        .system-info {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .system-info h2 {{
            margin-top: 0;
            color: #1a1a2e;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        .system-info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .system-info-item {{
            background: #f8f9fa;
            padding: 10px 15px;
            border-radius: 5px;
        }}
        .system-info-item label {{
            font-weight: 600;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .system-info-item span {{
            display: block;
            font-size: 16px;
            color: #333;
        }}
        .category {{
            background: white;
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .category-header {{
            background: #1a1a2e;
            color: white;
            padding: 15px 20px;
            font-size: 18px;
            font-weight: 600;
        }}
        .category-content {{
            padding: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #f8f9fa;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            border-bottom: 2px solid #e0e0e0;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 14px;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .severity {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }}
        .no-data {{
            padding: 30px;
            text-align: center;
            color: #666;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Windows System Diagnostic Report</h1>
        <div class="timestamp">Generated: {timestamp}</div>
    </div>
'''

        # System Info Section
        if self.system_info:
            html_content += '''
    <div class="system-info">
        <h2>System Information</h2>
        <div class="system-info-grid">
'''
            for label, value in self.system_info.items():
                html_content += f'''
            <div class="system-info-item">
                <label>{self._escape(label)}</label>
                <span>{self._escape(value)}</span>
            </div>
'''
            html_content += '''
        </div>
    </div>
'''

        # Category Sections
        category_titles = {
            'startup': 'Startup Programs',
            'services': 'Windows Services',
            'processes': 'Process Resource Usage',
            'disk': 'Disk Health',
            'drivers': 'Driver Status',
            'scheduled': 'Scheduled Tasks'
        }

        for category, items in self.results.items():
            title = category_titles.get(category, category.title())
            html_content += f'''
    <div class="category">
        <div class="category-header">{self._escape(title)}</div>
        <div class="category-content">
'''

            if items:
                # Build table headers from first item keys
                headers = list(items[0].keys())
                html_content += '''
            <table>
                <thead>
                    <tr>
'''
                for header in headers:
                    display_header = header.replace('_', ' ').title()
                    html_content += f'                        <th>{self._escape(display_header)}</th>\n'

                html_content += '''
                    </tr>
                </thead>
                <tbody>
'''

                for item in items:
                    html_content += '                    <tr>\n'
                    for header in headers:
                        value = item.get(header, '')
                        if header.lower() in ['severity', 'impact', 'status']:
                            color = self._get_severity_color(str(value))
                            html_content += f'                        <td><span class="severity" style="background-color: {color}">{self._escape(value)}</span></td>\n'
                        else:
                            html_content += f'                        <td>{self._escape(value)}</td>\n'
                    html_content += '                    </tr>\n'

                html_content += '''
                </tbody>
            </table>
'''
            else:
                html_content += '''
            <div class="no-data">No issues found</div>
'''

            html_content += '''
        </div>
    </div>
'''

        html_content += '''
    <div class="footer">
        Generated by Windows System Diagnostic Tool
    </div>
</body>
</html>
'''
        return html_content

    def save_report(self, filepath: str) -> bool:
        """Save the report to a file."""
        try:
            html_content = self.generate_html()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False
