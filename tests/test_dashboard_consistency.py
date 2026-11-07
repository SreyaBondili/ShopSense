"""
ShopSense - Milestone 3 Module 8: Automated Dashboard Data Consistency Test
Target Metric: Consistency >= 99%

Validates that:
1. Total revenue in analytics matches SQL SUM(transactions.amount).
2. Total transaction count in analytics matches SQL COUNT(transactions.transaction_id).
3. Total units sold in analytics matches SQL SUM(transactions.quantity).
4. Vendor revenue in analytics matches SQL SUM(transactions.amount GROUP BY vendor_id).
5. Product inventory in analytics matches SQL SUM(inventory.quantity).
"""

import pytest
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models.transaction import Transaction
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.vendor import Vendor
from app.models.user import User, UserRole
from app.services import revenue_service, replenishment_service, analytics_service

def test_dashboard_data_consistency():
    db: Session = SessionLocal()
    try:
        dummy_admin = User(user_id=1, role=UserRole.ADMIN)

        # 1. Fetch API / Service metrics
        rev_analytics = revenue_service.get_advanced_revenue_analysis(db, dummy_admin)
        inv_turnover = replenishment_service.get_inventory_turnover(db, dummy_admin)

        # 2. Query MySQL Database directly
        sql_total_rev = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).scalar()
        sql_total_tx = db.query(func.count(Transaction.transaction_id)).scalar()
        sql_total_units = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).scalar()
        sql_total_inventory = db.query(func.coalesce(func.sum(Inventory.current_stock), 0)).scalar()

        # 3. Perform Metric Comparisons
        checks = []

        # Check 1: Total Revenue
        api_rev = float(rev_analytics["total_revenue"])
        db_rev = float(sql_total_rev)
        diff_rev = abs(api_rev - db_rev)
        checks.append(("Total Revenue", diff_rev < 0.01, f"API: {api_rev}, DB: {db_rev}"))

        # Check 2: Total Orders / Transactions
        api_orders = int(rev_analytics["total_orders"])
        db_orders = int(sql_total_tx)
        checks.append(("Transaction Count", api_orders == db_orders, f"API: {api_orders}, DB: {db_orders}"))

        # Check 3: Units Sold
        api_units = int(rev_analytics["units_sold"])
        db_units = int(sql_total_units)
        checks.append(("Units Sold", api_units == db_units, f"API: {api_units}, DB: {db_units}"))

        # Check 4: Gross Profit Consistency (COGS 70% + Profit 30% == Total Revenue)
        cogs = float(rev_analytics["cogs"])
        profit = float(rev_analytics["gross_profit"])
        cogs_profit_sum = round(cogs + profit, 2)
        diff_cogs = abs(cogs_profit_sum - api_rev)
        checks.append(("COGS + Profit Equation", diff_cogs < 0.05, f"Sum: {cogs_profit_sum}, Rev: {api_rev}"))

        # Check 5: Vendor Revenue Sum vs Total Revenue
        vendor_sum = sum(float(v["revenue"]) for v in rev_analytics["vendor_rankings"])
        diff_vendor_sum = abs(vendor_sum - api_rev)
        checks.append(("Vendor Breakdown Sum", diff_vendor_sum < 0.05, f"Vendor Sum: {vendor_sum}, Rev: {api_rev}"))

        # Check 6: Vendor-level SQL verification
        for v in rev_analytics["vendor_rankings"][:5]:
            v_id_row = db.query(Vendor.vendor_id).filter(Vendor.business_name == v["vendor_name"]).first()
            if v_id_row:
                v_id = v_id_row[0]
                sql_v_rev = float(db.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
                                  .filter(Transaction.vendor_id == v_id).scalar())
                checks.append((
                    f"Vendor {v['vendor_name']} Revenue",
                    abs(float(v["revenue"]) - sql_v_rev) < 0.05,
                    f"API: {v['revenue']}, DB: {sql_v_rev}"
                ))

        # Check 7: Inventory Quantity Consistency
        product_turnover_qty = sum(p["current_stock"] for p in inv_turnover.get("items", []))
        checks.append((
            "Product Inventory Sum",
            product_turnover_qty == sql_total_inventory,
            f"Turnover Stock: {product_turnover_qty}, DB Inventory: {sql_total_inventory}"
        ))

        # 4. Calculate Consistency Percentage
        total_checks = len(checks)
        passed_checks = sum(1 for _, passed, _ in checks if passed)
        consistency_pct = (passed_checks / total_checks) * 100.0

        print(f"\n--- DASHBOARD DATA CONSISTENCY REPORT ---")
        print(f"Total Checks: {total_checks} | Passed: {passed_checks} | Consistency: {consistency_pct:.2f}%")
        for name, passed, detail in checks:
            status_str = "PASS" if passed else "FAIL"
            print(f"[{status_str}] {name}: {detail}")

        assert consistency_pct >= 99.0, f"Dashboard consistency was {consistency_pct:.2f}%, below 99% target!"

    finally:
        db.close()
