from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.utils.security import get_current_active_user
from app.models.user import User, UserRole
from app.services import revenue_service, analytics_service, replenishment_service, customer_analytics_service
from app.reports.pdf_generator import generate_pdf_report
from app.reports.excel_generator import generate_excel_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def _build_report_dataset(report_type: str, db: Session, current_user: User):
    report_type = report_type.lower()

    if report_type == "revenue":
        rev = revenue_service.get_advanced_revenue_analysis(db, current_user)
        headers = ["Rank", "Vendor Name", "Revenue (INR)", "Contribution (%)", "Total Orders", "Units Sold"]
        rows = [
            [v["rank"], v["vendor_name"], f"Rs. {v['revenue']:,.2f}", f"{v['contribution_pct']}%", v["orders"], v["units"]]
            for v in rev["vendor_rankings"]
        ]
        summary = {
            "Total Revenue": f"Rs. {rev['total_revenue']:,.2f}",
            "GMV": f"Rs. {rev['gmv']:,.2f}",
            "Orders Count": f"{rev['total_orders']:,}",
            "Units Sold": f"{rev['units_sold']:,}",
            "Average Order Value": f"Rs. {rev['average_order_value']:,.2f}",
            "Gross Profit (30%)": f"Rs. {rev['gross_profit']:,.2f}",
            "Monthly Target Status": rev["benchmarking"]["status"]
        }
        filename = "ShopSense_Revenue_Report"

    elif report_type == "vendors":
        vendors_data = analytics_service.get_vendor_performance(db, current_user)
        headers = ["Vendor ID", "Business Name", "Category", "Revenue (INR)", "Orders", "Units Sold", "Status"]
        rows = [
            [v.vendor_id, v.business_name, v.category, f"Rs. {v.total_revenue:,.2f}", v.transaction_count, v.total_quantity_sold, v.status]
            for v in vendors_data
        ]
        total_rev = sum(v.total_revenue for v in vendors_data)
        summary = {
            "Total Vendors": str(len(vendors_data)),
            "Total Vendor Revenue": f"Rs. {total_rev:,.2f}",
            "Average Revenue / Vendor": f"Rs. {total_rev / max(1, len(vendors_data)):,.2f}"
        }
        filename = "ShopSense_Vendors_Report"

    elif report_type == "products":
        prods = analytics_service.get_product_performance(db, current_user)
        headers = ["Product ID", "Product Name", "Category", "Price", "Units Sold", "Revenue (INR)", "Stock Status"]
        rows = [
            [p.product_id, p.product_name, p.category, f"Rs. {p.price:,.2f}", p.units_sold, f"Rs. {p.revenue:,.2f}", p.stock_status]
            for p in prods
        ]
        summary = {
            "Total Products": str(len(prods)),
            "Total Product Revenue": f"Rs. {sum(p.revenue for p in prods):,.2f}",
            "Total Units Sold": f"{sum(p.units_sold for p in prods):,}"
        }
        filename = "ShopSense_Products_Report"

    elif report_type == "customers":
        cust_data = customer_analytics_service.get_customer_behavior_analytics(db, current_user)
        headers = ["Customer ID", "Name", "Email", "Total Orders", "Total Spent (INR)", "AOV (INR)", "Preferred Category"]
        rows = [
            [c["user_id"], c["customer_name"], c["email"], c["total_orders"], f"Rs. {c['total_spent']:,.2f}", f"Rs. {c['average_order_value']:,.2f}", c["preferred_category"]]
            for c in cust_data["customers"]
        ]
        summary = {
            "Total Active Customers": str(cust_data["total_customers"]),
            "Total Spending": f"Rs. {cust_data['total_spending']:,.2f}",
            "Average Order Value": f"Rs. {cust_data['average_order_value']:,.2f}"
        }
        filename = "ShopSense_Customers_Report"

    elif report_type == "inventory":
        turnover = replenishment_service.get_inventory_turnover(db, current_user)
        headers = ["Product ID", "Product Name", "Category", "Warehouse", "Stock", "Inventory Value", "COGS", "Turnover Rate", "Velocity"]
        rows = [
            [i["product_id"], i["product_name"], i["category"], i["warehouse"], f"{i['current_stock']} units", f"Rs. {i['inventory_value']:,.2f}", f"Rs. {i['cogs']:,.2f}", f"{i['turnover_rate']}x", i["velocity"]]
            for i in turnover["items"]
        ]
        summary = {
            "Total Inventory Valuation": f"Rs. {turnover['total_inventory_value']:,.2f}",
            "Total COGS": f"Rs. {turnover['total_cogs']:,.2f}",
            "Overall Turnover Rate": f"{turnover['overall_turnover_rate']}x",
            "Total Products Tracked": str(len(turnover["items"]))
        }
        filename = "ShopSense_Inventory_Report"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report type '{report_type}'. Allowed types: 'revenue', 'vendors', 'products', 'customers', 'inventory'."
        )

    return {
        "headers": headers,
        "rows": rows,
        "summary_metrics": summary,
        "filename": filename
    }

@router.get("/pdf")
def export_pdf_report(
    type: str = Query("revenue", description="Report type: revenue, vendors, products, customers, inventory"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Module 6: Download generated PDF business intelligence report."""
    dataset = _build_report_dataset(type, db, current_user)
    pdf_buffer = generate_pdf_report(type, dataset)
    filename = f"{dataset['filename']}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/excel")
def export_excel_report(
    type: str = Query("revenue", description="Report type: revenue, vendors, products, customers, inventory"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Module 6: Download generated Excel (.xlsx) analytical spreadsheet."""
    dataset = _build_report_dataset(type, db, current_user)
    excel_buffer = generate_excel_report(type, dataset)
    filename = f"{dataset['filename']}.xlsx"

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
