import os
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "transactions.csv")

def get_customer_stats():
    """
    Mentor Step 15: Customer Behavior Analytics
    transactions.groupby("customer_id").agg({"amount": "sum", "transaction_id": "count"})
    """
    if os.path.exists(CSV_PATH):
        transactions = pd.read_csv(CSV_PATH)
    else:
        from app.database import engine
        transactions = pd.read_sql("SELECT transaction_id, user_id, amount, quantity FROM transactions", engine)

    customer_col = "user_id" if "user_id" in transactions.columns else "customer_id"
    customer_stats = (
        transactions.groupby(customer_col)
        .agg({
            "amount": "sum",
            "transaction_id": "count"
        })
        .rename(columns={"transaction_id": "total_orders", "amount": "total_spent"})
    )
    return customer_stats
