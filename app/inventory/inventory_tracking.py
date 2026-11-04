import os
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "inventory.csv")

def get_inventory_df():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    from app.database import engine
    return pd.read_sql("SELECT * FROM inventory", engine)

def inventory_status():
    """
    Mentor Step 6: Inventory Tracking
    Status: Available if current_stock > reorder_level else Low Stock
    """
    inventory = get_inventory_df()
    inventory["Status"] = (
        inventory["current_stock"] > inventory["reorder_level"]
    )
    inventory["Status"] = inventory["Status"].map({
        True: "Available",
        False: "Low Stock"
    })
    return inventory

def turnover_rate(cogs: float, avg_inventory: float) -> float:
    """
    Mentor Step 7: Inventory Turnover Rate
    Inventory Turnover = Cost of Goods Sold / Average Inventory
    """
    if avg_inventory <= 0:
        return 0.0
    return round(cogs / avg_inventory, 2)
