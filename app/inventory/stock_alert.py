import os
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "inventory.csv")

def get_inventory_df():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    from app.database import engine
    return pd.read_sql("SELECT * FROM inventory", engine)

def low_stock_alert():
    """
    Mentor Step 10: Low Stock Alert
    Returns inventory items where current_stock <= reorder_level
    """
    inventory = get_inventory_df()
    alerts = inventory[
        inventory["current_stock"] <= inventory["reorder_level"]
    ]
    return alerts

def replenishment():
    """
    Mentor Step 11: Replenishment Recommendation
    reorder_qty = reorder_level * 2 - current_stock
    """
    inventory = get_inventory_df()
    inventory["reorder_qty"] = (
        inventory["reorder_level"] * 2 - inventory["current_stock"]
    )
    return inventory[["product_id", "reorder_qty"]]
