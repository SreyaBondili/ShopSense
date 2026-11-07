import io
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_report(report_type: str, data: Dict[str, Any]) -> io.BytesIO:
    """
    Milestone 3 Module 6: Generate Professional PDF Analytics Report using ReportLab.
    Supports: 'revenue', 'vendors', 'products', 'customers', 'inventory'.
    """
    buffer = io.BytesIO()
    # Use landscape for wide tables
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=14
    )
    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )
    body_cell_style = ParagraphStyle(
        'BodyCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#1E293B')
    )

    elements = []
    timestamp_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Document Header
    title_map = {
        "revenue": "ShopSense — Advanced Revenue & Financial Report",
        "vendors": "ShopSense — Vendor Performance & Marketplace Benchmarking Report",
        "products": "ShopSense — Product Catalog & Sales Analytics Report",
        "customers": "ShopSense — Customer Intelligence & Segmentation Report",
        "inventory": "ShopSense — Inventory Intelligence & Replenishment Report"
    }
    report_title = title_map.get(report_type.lower(), "ShopSense — Business Intelligence Report")

    elements.append(Paragraph(report_title, title_style))
    elements.append(Paragraph(f"Generated automatically on {timestamp_str} | Platform: ShopSense Multi-Vendor Analytics", subtitle_style))
    elements.append(Spacer(1, 10))

    # Summary KPI Table
    if "summary_metrics" in data:
        metrics = data["summary_metrics"]
        kpi_data = [
            [Paragraph(f"<b>{k}</b>", body_cell_style) for k in metrics.keys()],
            [Paragraph(f"<font color='#4F46E5'><b>{v}</b></font>", body_cell_style) for v in metrics.values()]
        ]
        kpi_table = Table(kpi_data)
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EEF2FF')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#C7D2FE')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E7FF')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 16))

    # Detailed Records Table
    headers = data.get("headers", [])
    rows = data.get("rows", [])

    if headers and rows:
        table_content = [[Paragraph(f"<b>{h}</b>", header_cell_style) for h in headers]]
        for r in rows:
            table_content.append([Paragraph(str(c), body_cell_style) for c in r])

        data_table = Table(table_content, repeatRows=1)
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        elements.append(data_table)
    else:
        elements.append(Paragraph("No records found for this reporting period.", body_cell_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
