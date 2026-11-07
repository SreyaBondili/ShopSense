import io
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def generate_excel_report(report_type: str, data: Dict[str, Any]) -> io.BytesIO:
    """
    Milestone 3 Module 6: Generate Formatted Excel Spreadsheet using openpyxl and Pandas.
    Features:
    - Sheet 1: Executive KPI Summary
    - Sheet 2: Detailed Data Records with styled headers and alternating rows
    """
    buffer = io.BytesIO()
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sheet 1: Executive Summary
    ws_summary = wb.create_sheet(title="Executive Summary")
    ws_summary.views.sheetView[0].showGridLines = True

    # Title styling
    ws_summary.merge_cells("A1:D1")
    title_cell = ws_summary["A1"]
    title_cell.value = f"ShopSense — {report_type.capitalize()} Analytics Report"
    title_cell.font = Font(name="Arial", size=16, bold=True, color="4F46E5")

    ws_summary["A2"] = f"Report Generated: {timestamp_str} | Platform: ShopSense Multi-Vendor Analytics"
    ws_summary["A2"].font = Font(name="Arial", size=9, italic=True, color="64748B")

    # Metrics table
    if "summary_metrics" in data:
        ws_summary["A4"] = "KPI Metric"
        ws_summary["B4"] = "Value"
        ws_summary["A4"].font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        ws_summary["B4"].font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        ws_summary["A4"].fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
        ws_summary["B4"].fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")

        row_idx = 5
        for k, v in data["summary_metrics"].items():
            ws_summary.cell(row=row_idx, column=1, value=k).font = Font(name="Arial", size=10, bold=True)
            ws_summary.cell(row=row_idx, column=2, value=str(v)).font = Font(name="Arial", size=10)
            row_idx += 1

    # Sheet 2: Detailed Data
    ws_data = wb.create_sheet(title="Detailed Records")
    ws_data.views.sheetView[0].showGridLines = True

    headers = data.get("headers", [])
    rows = data.get("rows", [])

    if headers:
        for col_idx, h in enumerate(headers, 1):
            cell = ws_data.cell(row=1, column=col_idx, value=h)
            cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for row_idx, r in enumerate(rows, 2):
            fill_color = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
            for col_idx, val in enumerate(r, 1):
                cell = ws_data.cell(row=row_idx, column=col_idx, value=val)
                cell.font = Font(name="Arial", size=9.5)
                cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

    # Auto-fit column widths
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(buffer)
    buffer.seek(0)
    return buffer
