from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

from app.models.transaction import Transaction
from app.models.product import Product
from app.models.vendor import Vendor
from app.models.user import User, UserRole

def get_advanced_revenue_analysis(
    db: Session,
    current_user: User,
    vendor_id_filter: Optional[int] = None
) -> Dict[str, Any]:
    """
    Milestone 3 Module 2: Advanced Revenue Analysis & Marketplace Benchmarking
    - Gross Merchandise Value (GMV)
    - Total Revenue & Units Sold
    - Average Order Value (AOV)
    - Daily, Weekly, and Monthly Revenue Trends
    - Month-over-Month Revenue Growth Percentage
    - Profit/Loss Analysis (COGS @ 70%, Gross Profit @ 30%)
    - Vendor Revenue Contribution & Rankings
    - Product Revenue & Sales Rankings
    - Marketplace Benchmarking vs Configurable Target
    """
    effective_vendor_id = None
    if current_user.role == UserRole.VENDOR and current_user.vendor:
        effective_vendor_id = current_user.vendor.vendor_id
    elif vendor_id_filter:
        effective_vendor_id = vendor_id_filter

    # 1. Fetch transactions with product & vendor info
    t_query = db.query(
        Transaction.transaction_id,
        Transaction.product_id,
        Transaction.vendor_id,
        Transaction.quantity,
        Transaction.amount,
        Transaction.transaction_date,
        Product.product_name,
        Product.category,
        Product.price,
        Vendor.business_name.label("vendor_name")
    ).join(Product, Transaction.product_id == Product.product_id)\
     .join(Vendor, Transaction.vendor_id == Vendor.vendor_id)

    if effective_vendor_id is not None:
        t_query = t_query.filter(Transaction.vendor_id == effective_vendor_id)

    rows = t_query.all()

    if not rows:
        return {
            "total_revenue": 0.0,
            "gmv": 0.0,
            "total_orders": 0,
            "units_sold": 0,
            "average_order_value": 0.0,
            "cogs": 0.0,
            "gross_profit": 0.0,
            "profit_margin_pct": 30.0,
            "daily_revenue": [],
            "weekly_revenue": [],
            "monthly_revenue": [],
            "monthly_breakdown": [],
            "revenue_growth_pct": 0.0,
            "vendor_rankings": [],
            "product_rankings": [],
            "benchmarking": {
                "monthly_target": 150000.0,
                "current_month_revenue": 0.0,
                "target_achievement_pct": 0.0,
                "status": "Below Target"
            }
        }

    df = pd.DataFrame([{
        "transaction_id": r.transaction_id,
        "product_id": r.product_id,
        "vendor_id": r.vendor_id,
        "quantity": int(r.quantity),
        "amount": float(r.amount),
        "transaction_date": pd.to_datetime(r.transaction_date),
        "product_name": r.product_name,
        "category": r.category,
        "price": float(r.price),
        "vendor_name": r.vendor_name
    } for r in rows])

    # Core Financial Metrics
    total_revenue = round(float(df["amount"].sum()), 2)
    gmv = total_revenue  # In marketplace platform, GMV = total value of merchandise sold
    total_orders = int(len(df))
    units_sold = int(df["quantity"].sum())
    aov = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

    # Profit / Loss Analysis (70% standard wholesale COGS ratio, 30% gross profit)
    cogs = round(total_revenue * 0.70, 2)
    gross_profit = round(total_revenue - cogs, 2)
    profit_margin_pct = round((gross_profit / total_revenue) * 100, 2) if total_revenue > 0 else 30.0

    # 1. Daily Revenue (last 30 days of transactions)
    df["date"] = df["transaction_date"].dt.date
    daily_grouped = df.groupby("date").agg(
        revenue=("amount", "sum"),
        orders=("transaction_id", "count"),
        units=("quantity", "sum")
    ).reset_index().sort_values("date")

    daily_revenue = [{
        "date": d["date"].strftime("%Y-%m-%d"),
        "revenue": round(float(d["revenue"]), 2),
        "orders": int(d["orders"]),
        "units": int(d["units"])
    } for _, d in daily_grouped.tail(30).iterrows()]

    # 2. Weekly Revenue
    df["week"] = df["transaction_date"].dt.to_period("W").astype(str)
    weekly_grouped = df.groupby("week").agg(
        revenue=("amount", "sum"),
        orders=("transaction_id", "count"),
        units=("quantity", "sum")
    ).reset_index().sort_values("week")

    weekly_revenue = [{
        "week": w["week"],
        "revenue": round(float(w["revenue"]), 2),
        "orders": int(w["orders"]),
        "units": int(w["units"])
    } for _, w in weekly_grouped.tail(12).iterrows()]

    # 3. Monthly Revenue & Growth %
    df["month"] = df["transaction_date"].dt.to_period("M").astype(str)
    monthly_grouped = df.groupby("month").agg(
        revenue=("amount", "sum"),
        orders=("transaction_id", "count"),
        units=("quantity", "sum")
    ).reset_index().sort_values("month")

    # Calculate MoM Growth Percentage
    monthly_grouped["growth_pct"] = monthly_grouped["revenue"].pct_change().fillna(0.0) * 100.0

    monthly_revenue = [{
        "month": m["month"],
        "revenue": round(float(m["revenue"]), 2),
        "orders": int(m["orders"]),
        "units": int(m["units"]),
        "growth_pct": round(float(m["growth_pct"]), 2)
    } for _, m in monthly_grouped.iterrows()]

    latest_growth = monthly_revenue[-1]["growth_pct"] if len(monthly_revenue) > 0 else 0.0

    # 4. Vendor Benchmarking & Rankings
    vendor_grouped = df.groupby(["vendor_id", "vendor_name"]).agg(
        revenue=("amount", "sum"),
        orders=("transaction_id", "count"),
        units=("quantity", "sum")
    ).reset_index()

    vendor_grouped["rank"] = vendor_grouped["revenue"].rank(ascending=False, method="min").astype(int)
    vendor_grouped["contribution_pct"] = round((vendor_grouped["revenue"] / total_revenue) * 100, 2)
    vendor_grouped = vendor_grouped.sort_values("revenue", ascending=False)

    vendor_rankings = [{
        "rank": int(v["rank"]),
        "vendor_id": int(v["vendor_id"]),
        "vendor_name": str(v["vendor_name"]),
        "revenue": round(float(v["revenue"]), 2),
        "contribution_pct": float(v["contribution_pct"]),
        "orders": int(v["orders"]),
        "units": int(v["units"])
    } for _, v in vendor_grouped.iterrows()]

    # 5. Product Rankings (Top 10)
    prod_grouped = df.groupby(["product_id", "product_name", "category"]).agg(
        revenue=("amount", "sum"),
        units_sold=("quantity", "sum"),
        orders=("transaction_id", "count")
    ).reset_index()
    prod_grouped["rank"] = prod_grouped["revenue"].rank(ascending=False, method="min").astype(int)
    prod_grouped = prod_grouped.sort_values("revenue", ascending=False)

    product_rankings = [{
        "rank": int(p["rank"]),
        "product_id": int(p["product_id"]),
        "product_name": str(p["product_name"]),
        "category": str(p["category"]),
        "revenue": round(float(p["revenue"]), 2),
        "units_sold": int(p["units_sold"]),
        "orders": int(p["orders"])
    } for _, p in prod_grouped.head(10).iterrows()]

    # 6. Marketplace Benchmarking vs Sales Targets
    # Standard monthly target: ₹1,50,000 for marketplace
    monthly_target = 150000.0 if current_user.role == UserRole.ADMIN else 35000.0
    current_month_rev = monthly_revenue[-1]["revenue"] if monthly_revenue else total_revenue
    target_achievement_pct = round((current_month_rev / monthly_target) * 100, 2)
    target_status = "Target Exceeded" if target_achievement_pct >= 100 else ("On Track" if target_achievement_pct >= 75 else "Needs Acceleration")

    benchmarking = {
        "monthly_target": monthly_target,
        "current_month_revenue": current_month_rev,
        "target_achievement_pct": target_achievement_pct,
        "status": target_status,
        "avg_revenue_per_vendor": round(total_revenue / len(vendor_grouped), 2) if len(vendor_grouped) > 0 else 0.0,
        "top_vendor_concentration_pct": vendor_rankings[0]["contribution_pct"] if vendor_rankings else 0.0
    }

    return {
        "total_revenue": total_revenue,
        "gmv": gmv,
        "total_orders": total_orders,
        "units_sold": units_sold,
        "average_order_value": aov,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "profit_margin_pct": profit_margin_pct,
        "daily_revenue": daily_revenue,
        "weekly_revenue": weekly_revenue,
        "monthly_revenue": monthly_revenue,
        "monthly_breakdown": monthly_revenue,
        "revenue_growth_pct": latest_growth,
        "vendor_rankings": vendor_rankings,
        "product_rankings": product_rankings,
        "benchmarking": benchmarking
    }
