from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from app.models.transaction import Transaction
from app.models.product import Product
from app.models.vendor import Vendor
from app.models.inventory import Inventory
from app.models.user import User, UserRole

def _get_scoped_dataframes(
    db: Session,
    current_user: User,
    vendor_id_filter: Optional[int] = None
) -> Dict[str, pd.DataFrame]:
    """Helper to query transactions, products, vendors, and inventory into Pandas DataFrames."""
    # Determine effective vendor filter
    effective_vendor_id = None
    if current_user.role == UserRole.VENDOR:
        effective_vendor_id = current_user.vendor.vendor_id if current_user.vendor else -1
    elif vendor_id_filter:
        effective_vendor_id = vendor_id_filter

    # 1. Fetch transactions
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

    t_rows = t_query.all()
    if t_rows:
        df_trans = pd.DataFrame([{
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
        } for r in t_rows])
    else:
        df_trans = pd.DataFrame(columns=[
            "transaction_id", "product_id", "vendor_id", "quantity",
            "amount", "transaction_date", "product_name", "category", "price", "vendor_name"
        ])

    # 2. Fetch products (join Inventory for reorder_level — Item 5)
    p_query = db.query(
        Product.product_id,
        Product.product_name,
        Product.category,
        Product.price,
        Product.stock,
        Product.vendor_id,
        Vendor.business_name.label("vendor_name"),
        Inventory.reorder_level.label("reorder_level")
    ).join(Vendor, Product.vendor_id == Vendor.vendor_id)\
     .outerjoin(Inventory, Inventory.product_id == Product.product_id)

    if effective_vendor_id is not None:
        p_query = p_query.filter(Product.vendor_id == effective_vendor_id)

    p_rows = p_query.all()
    if p_rows:
        df_prod = pd.DataFrame([{
            "product_id": r.product_id,
            "product_name": r.product_name,
            "category": r.category,
            "price": float(r.price),
            "stock": int(r.stock),
            "vendor_id": r.vendor_id,
            "vendor_name": r.vendor_name,
            "reorder_level": int(r.reorder_level) if r.reorder_level is not None else 10
        } for r in p_rows])
    else:
        df_prod = pd.DataFrame(columns=[
            "product_id", "product_name", "category", "price", "stock",
            "vendor_id", "vendor_name", "reorder_level"
        ])

    # 3. Fetch vendors
    v_query = db.query(Vendor)
    if effective_vendor_id is not None:
        v_query = v_query.filter(Vendor.vendor_id == effective_vendor_id)
    v_rows = v_query.all()
    if v_rows:
        df_vend = pd.DataFrame([{
            "vendor_id": r.vendor_id,
            "business_name": r.business_name,
            "owner_name": r.owner_name,
            "category": r.category,
            "status": r.status.value if hasattr(r.status, "value") else str(r.status)
        } for r in v_rows])
    else:
        df_vend = pd.DataFrame(columns=[
            "vendor_id", "business_name", "owner_name", "category", "status"
        ])

    return {"transactions": df_trans, "products": df_prod, "vendors": df_vend}

def get_summary(
    db: Session,
    current_user: User,
    vendor_id: Optional[int] = None
) -> Dict[str, Any]:
    dfs = _get_scoped_dataframes(db, current_user, vendor_id)
    df_t = dfs["transactions"]
    df_p = dfs["products"]
    df_v = dfs["vendors"]

    total_rev = round(float(df_t["amount"].sum()), 2) if not df_t.empty else 0.0
    total_tx = int(len(df_t))
    total_qty = int(df_t["quantity"].sum()) if not df_t.empty else 0
    atv = round(total_rev / total_tx, 2) if total_tx > 0 else 0.0

    return {
        "total_revenue": total_rev,
        "total_transactions": total_tx,
        "total_quantity_sold": total_qty,
        "average_transaction_value": atv,
        "total_vendors": int(len(df_v)),
        "total_products": int(len(df_p))
    }

def get_vendor_performance(
    db: Session,
    current_user: User
) -> List[Dict[str, Any]]:
    # Admin sees all vendors; Vendor sees only their own
    dfs = _get_scoped_dataframes(db, current_user)
    df_t = dfs["transactions"]
    df_p = dfs["products"]
    df_v = dfs["vendors"]

    if df_v.empty:
        return []

    # Aggregate transactions by vendor
    if not df_t.empty:
        t_agg = df_t.groupby("vendor_id").agg(
            total_revenue=("amount", "sum"),
            total_transactions=("transaction_id", "count"),
            total_quantity_sold=("quantity", "sum")
        ).reset_index()
    else:
        t_agg = pd.DataFrame(columns=["vendor_id", "total_revenue", "total_transactions", "total_quantity_sold"])

    # Aggregate products count by vendor
    if not df_p.empty:
        p_agg = df_p.groupby("vendor_id").agg(
            product_count=("product_id", "count")
        ).reset_index()
    else:
        p_agg = pd.DataFrame(columns=["vendor_id", "product_count"])

    merged = df_v.merge(t_agg, on="vendor_id", how="left").merge(p_agg, on="vendor_id", how="left")
    merged["total_revenue"] = merged["total_revenue"].fillna(0.0).round(2)
    merged["total_transactions"] = merged["total_transactions"].fillna(0).astype(int)
    merged["total_quantity_sold"] = merged["total_quantity_sold"].fillna(0).astype(int)
    merged["product_count"] = merged["product_count"].fillna(0).astype(int)

    # Sort descending by revenue
    merged = merged.sort_values(by="total_revenue", ascending=False)

    return merged.to_dict(orient="records")

def get_product_performance(
    db: Session,
    current_user: User,
    vendor_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    dfs = _get_scoped_dataframes(db, current_user, vendor_id)
    df_t = dfs["transactions"]
    df_p = dfs["products"]

    if df_p.empty:
        return []

    if not df_t.empty:
        t_agg = df_t.groupby("product_id").agg(
            total_revenue=("amount", "sum"),
            quantity_sold=("quantity", "sum")
        ).reset_index()
    else:
        t_agg = pd.DataFrame(columns=["product_id", "total_revenue", "quantity_sold"])

    merged = df_p.merge(t_agg, on="product_id", how="left")
    merged["total_revenue"] = merged["total_revenue"].fillna(0.0).round(2)
    merged["quantity_sold"] = merged["quantity_sold"].fillna(0).astype(int)

    # Calculate inventory status using per-product reorder_level (Item 5)
    def compute_status(row) -> str:
        stock = int(row.get("stock", row.get("current_stock", 0)))
        reorder = int(row.get("reorder_level", 10))
        if stock == 0:
            return "OUT OF STOCK"
        elif stock <= reorder:
            return "LOW STOCK"
        return "IN STOCK"

    merged["inventory_status"] = merged.apply(compute_status, axis=1)
    merged = merged.rename(columns={"stock": "current_stock"})
    merged = merged.drop(columns=["reorder_level"], errors="ignore")
    merged = merged.sort_values(by="total_revenue", ascending=False)

    return merged.to_dict(orient="records")

def get_revenue_trend(
    db: Session,
    current_user: User,
    vendor_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    dfs = _get_scoped_dataframes(db, current_user, vendor_id)
    df_t = dfs["transactions"]

    if df_t.empty:
        return []

    df_t["date"] = df_t["transaction_date"].dt.strftime("%Y-%m-%d")
    trend = df_t.groupby("date").agg(
        revenue=("amount", "sum"),
        transactions_count=("transaction_id", "count"),
        quantity_sold=("quantity", "sum")
    ).reset_index()

    trend["revenue"] = trend["revenue"].round(2)
    trend = trend.sort_values(by="date", ascending=True)

    return trend.to_dict(orient="records")

def get_category_performance(
    db: Session,
    current_user: User,
    vendor_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    dfs = _get_scoped_dataframes(db, current_user, vendor_id)
    df_t = dfs["transactions"]
    df_p = dfs["products"]

    if df_p.empty:
        return []

    # Category products count
    p_cat = df_p.groupby("category").agg(products_count=("product_id", "count")).reset_index()

    if not df_t.empty:
        t_cat = df_t.groupby("category").agg(
            revenue=("amount", "sum"),
            units_sold=("quantity", "sum")
        ).reset_index()
    else:
        t_cat = pd.DataFrame(columns=["category", "revenue", "units_sold"])

    merged = p_cat.merge(t_cat, on="category", how="left")
    merged["revenue"] = merged["revenue"].fillna(0.0).round(2)
    merged["units_sold"] = merged["units_sold"].fillna(0).astype(int)
    merged = merged.sort_values(by="revenue", ascending=False)

    return merged.to_dict(orient="records")
