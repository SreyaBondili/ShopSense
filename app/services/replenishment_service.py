from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import pandas as pd
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.transaction import Transaction
from app.models.user import User, UserRole

def get_inventory_turnover(
    db: Session,
    current_user: User
) -> Dict[str, Any]:
    """
    Module 1.C: Inventory Turnover Analytics
    Formula: Inventory Turnover = Cost of Goods Sold (COGS) / Average Inventory Value
    - COGS calculated as 70% of gross revenue (standard wholesale cost ratio).
    - Average Inventory Value = sum(stock * price).
    - Distinguishes monetary inventory values from unit quantities.
    - Handles zero denominators safely.
    """
    # 1. Fetch products & inventory
    p_query = db.query(Product, Inventory).join(Inventory, Product.product_id == Inventory.product_id)
    t_query = db.query(Transaction)

    if current_user.role == UserRole.VENDOR and current_user.vendor:
        v_id = current_user.vendor.vendor_id
        p_query = p_query.filter(Product.vendor_id == v_id)
        t_query = t_query.filter(Transaction.vendor_id == v_id)

    prod_rows = p_query.all()
    trans_rows = t_query.all()

    if not prod_rows:
        return {
            "overall_turnover_rate": 0.0,
            "total_cogs": 0.0,
            "total_inventory_value": 0.0,
            "high_turnover_products": [],
            "low_turnover_products": []
        }

    # Aggregate sales by product
    sales_map = {}
    for t in trans_rows:
        pid = t.product_id
        sales_map[pid] = sales_map.get(pid, 0.0) + float(t.amount)

    items = []
    total_revenue = 0.0
    total_inv_value = 0.0

    for prod, inv in prod_rows:
        price = float(prod.price)
        stock = int(inv.current_stock)
        inv_val = stock * price
        prod_revenue = sales_map.get(prod.product_id, 0.0)
        cogs = round(prod_revenue * 0.70, 2)
        turnover = round(cogs / inv_val, 2) if inv_val > 0 else (round(cogs / price, 2) if price > 0 else 0.0)

        total_revenue += prod_revenue
        total_inv_value += inv_val

        items.append({
            "product_id": prod.product_id,
            "product_name": prod.product_name,
            "category": prod.category,
            "price": price,
            "current_stock": stock,
            "inventory_value": round(inv_val, 2),
            "cogs": cogs,
            "turnover_rate": turnover
        })

    total_cogs = round(total_revenue * 0.70, 2)
    overall_turnover = round(total_cogs / total_inv_value, 2) if total_inv_value > 0 else 0.0

    # Sort products by turnover
    sorted_items = sorted(items, key=lambda x: x["turnover_rate"], reverse=True)
    high_turnover = sorted_items[:5]
    low_turnover = sorted_items[-5:] if len(sorted_items) > 5 else []

    return {
        "overall_turnover_rate": overall_turnover,
        "total_cogs": total_cogs,
        "total_inventory_value": round(total_inv_value, 2),
        "high_turnover_products": high_turnover,
        "low_turnover_products": low_turnover
    }

def get_low_stock_alerts(
    db: Session,
    current_user: User
) -> List[Dict[str, Any]]:
    """
    Module 1.E: Low-Stock Alert System
    Automatically identifies products where Current Stock <= Reorder Level.
    Includes stock shortage, alert status, and recommended action.
    """
    p_query = db.query(Product, Inventory).join(Inventory, Product.product_id == Inventory.product_id)

    if current_user.role == UserRole.VENDOR and current_user.vendor:
        p_query = p_query.filter(Product.vendor_id == current_user.vendor.vendor_id)

    rows = p_query.all()
    alerts = []

    for prod, inv in rows:
        stock = int(inv.current_stock)
        reorder = int(inv.reorder_level)

        if stock <= reorder:
            status = "OUT OF STOCK" if stock == 0 else "LOW STOCK"
            shortage = max(0, reorder - stock)
            
            if status == "OUT OF STOCK":
                action = "Urgent: Immediate Warehouse Restock Required"
                priority = "CRITICAL"
            else:
                action = "Place Purchase Order to maintain safety buffer"
                priority = "WARNING"

            alerts.append({
                "product_id": prod.product_id,
                "product_name": prod.product_name,
                "category": prod.category,
                "vendor_id": prod.vendor_id,
                "vendor_name": prod.vendor.business_name if prod.vendor else f"Vendor #{prod.vendor_id}",
                "warehouse": inv.warehouse,
                "current_stock": stock,
                "reorder_level": reorder,
                "shortage": shortage,
                "status": status,
                "priority": priority,
                "recommended_action": action
            })

    # Sort: OUT OF STOCK first, then by largest shortage
    alerts.sort(key=lambda x: (0 if x["status"] == "OUT OF STOCK" else 1, -x["shortage"]))
    return alerts

def get_replenishment_recommendations(
    db: Session,
    current_user: User,
    lead_time_days: int = 5
) -> List[Dict[str, Any]]:
    """
    Module 1.F: Replenishment Recommendation Engine
    Suggested Reorder Quantity = max(0, Target Stock - Current Stock)
    where Target Stock = Reorder Level + (Daily Forecast Demand * Lead Time).
    """
    p_query = db.query(Product, Inventory).join(Inventory, Product.product_id == Inventory.product_id)

    if current_user.role == UserRole.VENDOR and current_user.vendor:
        p_query = p_query.filter(Product.vendor_id == current_user.vendor.vendor_id)

    rows = p_query.all()

    # Calculate average daily sales per product over last 30 days
    thirty_days_ago = pd.Timestamp.now() - pd.Timedelta(days=30)
    tx_query = db.query(Transaction).filter(Transaction.transaction_date >= thirty_days_ago)
    
    daily_sales = {}
    for t in tx_query.all():
        daily_sales[t.product_id] = daily_sales.get(t.product_id, 0) + int(t.quantity)

    recommendations = []
    for prod, inv in rows:
        stock = int(inv.current_stock)
        reorder = int(inv.reorder_level)
        total_30d_sales = daily_sales.get(prod.product_id, 0)
        daily_demand = max(1.0, round(total_30d_sales / 30.0, 1))

        # Target stock = reorder safety buffer + lead time demand
        target_stock = int(round(reorder + (daily_demand * lead_time_days)))
        suggested_qty = max(0, target_stock - stock)

        if suggested_qty > 0:
            if stock == 0:
                priority = "HIGH"
                reason = "Product is completely out of stock with active customer demand."
            elif stock <= reorder:
                priority = "MEDIUM"
                reason = f"Stock level ({stock}) is below reorder threshold ({reorder})."
            else:
                priority = "LOW"
                reason = f"Proactive replenishment for anticipated lead-time demand."

            recommendations.append({
                "product_id": prod.product_id,
                "product_name": prod.product_name,
                "category": prod.category,
                "vendor_id": prod.vendor_id,
                "vendor_name": prod.vendor.business_name if prod.vendor else f"Vendor #{prod.vendor_id}",
                "warehouse": inv.warehouse,
                "current_stock": stock,
                "reorder_level": reorder,
                "daily_demand": daily_demand,
                "target_stock": target_stock,
                "suggested_reorder_quantity": suggested_qty,
                "estimated_cost": round(suggested_qty * float(prod.price) * 0.70, 2),
                "priority": priority,
                "reason": reason
            })

    # Sort high priority first
    prio_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recommendations.sort(key=lambda x: (prio_order.get(x["priority"], 3), -x["suggested_reorder_quantity"]))
    return recommendations
