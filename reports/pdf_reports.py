from reportlab.pdfgen import canvas
import os

def generate_report(output_filename: str = "RevenueReport.pdf"):
    """
    Mentor Module 6: PDF Report Export reference function.
    """
    pdf = canvas.Canvas(output_filename)
    pdf.drawString(100, 750, "ShopSense — Revenue Analytics Report")
    pdf.drawString(100, 720, "Generated via ReportLab PDF Engine")
    pdf.save()
    print(f"Generated {output_filename}")

if __name__ == "__main__":
    generate_report()
