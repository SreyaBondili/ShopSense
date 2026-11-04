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
    - Returns full product-level items table as well as high/low summaries.
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
            "items": [],
            "high_turnover_products": [],
            "low_turnover_products": []
        }

    # Aggregate sales by product
    sales_map = {}
    qty_sold_map = {}
    for t in trans_rows:
        pid = t.product_id
        sales_map[pid] = sales_map.get(pid, 0.0) + float(t.amount)
        qty_sold_map[pid] = qty_sold_map.get(pid, 0) + int(t.quantity)

    items = []
    total_revenue = 0.0
    total_inv_value = 0.0

    for prod, inv in prod_rows:
        price = float(prod.price)
        stock = int(inv.current_stock)
        inv_val = round(stock * price, 2)
        prod_revenue = sales_map.get(prod.product_id, 0.0)
        units_sold = qty_sold_map.get(prod.product_id, 0)
        cogs = round(prod_revenue * 0.70, 2)
        turnover = round(cogs / inv_val, 2) if inv_val > 0 else (round(cogs / price, 2) if price > 0 else 0.0)

        total_revenue += prod_revenue
        total_inv_value += inv_val

        # Velocity label
        if turnover >= 3.0:
            velocity = "High Turnover"
        elif turnover >= 1.0:
            velocity = "Moderate"
        else:
            velocity = "Slow Moving"

        items.append({
            "product_id": prod.product_id,
            "product_name": prod.product_name,
            "category": prod.category,
            "vendor_id": prod.vendor_id,
            "vendor_name": prod.vendor.business_name if prod.vendor else f"Vendor #{prod.vendor_id}",
            "warehouse": inv.warehouse or "Main Warehouse",
            "price": price,
            "current_stock": stock,
            "reorder_level": int(inv.reorder_level),
            "units_sold": units_sold,
            "revenue": round(prod_revenue, 2),
            "inventory_value": inv_val,
            "cogs": cogs,
            "turnover_rate": turnover,
            "velocity": velocity
        })

    total_cogs = round(total_revenue * 0.70, 2)
    overall_turnover = round(total_cogs / total_inv_value, 2) if total_inv_value > 0 else 0.0

    # Sort products by turnover descending
    sorted_items = sorted(items, key=lambda x: x["turnover_rate"], reverse=True)
    high_turnover = sorted_items[:5]
    low_turnover = sorted_items[-5:] if len(sorted_items) > 5 else []

    return {
        "overall_turnover_rate": overall_turnover,
        "total_cogs": total_cogs,
        "total_inventory_value": round(total_inv_value, 2),
        "items": sorted_items,
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
            elif stock <= (reorder // 2):
                action = "High Priority: Stock critically low, reorder immediately"
                priority = "HIGH"
            else:
                action = "Place Purchase Order to maintain safety buffer"
                priority = "WARNING"

            alerts.append({
                "product_id": prod.product_id,
                "product_name": prod.product_name,
                "category": prod.category,
                "price": float(prod.price),
                "vendor_id": prod.vendor_id,
                "vendor_name": prod.vendor.business_name if prod.vendor else f"Vendor #{prod.vendor_id}",
                "warehouse": inv.warehouse or "Main Warehouse",
                "current_stock": stock,
                "reorder_level": reorder,
                "safety_stock": reorder,
                "shortage": shortage,
                "status": status,
                "priority": priority,
                "urgency": priority,
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
    where Target Stock = max(Reorder Level * 2, Reorder Level + (Daily Forecast Demand * Lead Time)).
    
    Mentor Requirements:
    - Safety Stock = Reorder Level (buffer maintained against stockouts)
    - Reorder Quantity = Target Stock - Current Stock
    - Urgency based on remaining stock levels relative to safety stock
    - Uses real MySQL data for transaction velocity and current stock
    """
    p_query = db.query(Product, Inventory).join(Inventory, Product.product_id == Inventory.product_id)

    if current_user.role == UserRole.VENDOR and current_user.vendor:
        p_query = p_query.filter(Product.vendor_id == current_user.vendor.vendor_id)

    rows = p_query.all()

    # Calculate daily sales per product from transaction history
    tx_query = db.query(Transaction)
    if current_user.role == UserRole.VENDOR and current_user.vendor:
        tx_query = tx_query.filter(Transaction.vendor_id == current_user.vendor.vendor_id)

    tx_rows = tx_query.all()

    daily_sales = {}
    for t in tx_rows:
        daily_sales[t.product_id] = daily_sales.get(t.product_id, 0) + int(t.quantity)

    # Estimate average daily velocity over the active platform period (approx 60-70 operational days)
    platform_days = 60.0

    recommendations = []
    for prod, inv in rows:
        stock = int(inv.current_stock)
        safety_stock = int(inv.reorder_level)
        total_sales = daily_sales.get(prod.product_id, 0)
        daily_demand = max(0.5, round(total_sales / platform_days, 1))

        # Mentor's formula: Target Stock is at least 2 * safety buffer + lead-time demand
        lead_time_demand = int(round(daily_demand * lead_time_days))
        target_stock = max(safety_stock * 2, safety_stock + lead_time_demand)
        suggested_qty = max(0, target_stock - stock)

        # Flag any item needing replenishment (stock <= safety_stock OR current stock < target)
        if stock <= safety_stock or suggested_qty > 0:
            if stock == 0:
                urgency = "CRITICAL"
                reason = "Product is completely out of stock with active customer demand."
            elif stock <= (safety_stock // 2):
                urgency = "HIGH"
                reason = f"Critical shortage: stock ({stock}) is far below safety threshold ({safety_stock})."
            elif stock <= safety_stock:
                urgency = "MEDIUM"
                reason = f"Stock level ({stock}) is at or below safety reorder level ({safety_stock})."
            else:
                urgency = "LOW"
                reason = f"Proactive reorder for anticipated supplier lead-time ({lead_time_days} days)."

            # Make sure we recommend at least (safety_stock * 2 - stock) if stock <= safety_stock (mentor formula)
            mentor_reorder_qty = max(suggested_qty, (safety_stock * 2) - stock) if stock <= safety_stock else suggested_qty

            unit_price = float(prod.price)
            estimated_cost = round(mentor_reorder_qty * unit_price * 0.70, 2)

            recommendations.append({
                "product_id": prod.product_id,
                "product_name": prod.product_name,
                "category": prod.category,
                "vendor_id": prod.vendor_id,
                "vendor_name": prod.vendor.business_name if prod.vendor else f"Vendor #{prod.vendor_id}",
                "warehouse": inv.warehouse or "Main Warehouse",
                "price": unit_price,
                "current_stock": stock,
                "reorder_level": safety_stock,
                "safety_stock": safety_stock,
                "daily_demand": daily_demand,
                "target_stock": target_stock,
                "recommended_order_quantity": mentor_reorder_qty,
                "suggested_reorder_quantity": mentor_reorder_qty,
                "reorder_qty": mentor_reorder_qty,
                "estimated_cost": estimated_cost,
                "urgency": urgency,
                "priority": urgency,
                "reason": reason
            })

    # Sort: CRITICAL first, then HIGH, then MEDIUM, then LOW, then by quantity
    urgency_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    recommendations.sort(key=lambda x: (urgency_order.get(x["urgency"], 4), -x["recommended_order_quantity"]))
    return recommendations
