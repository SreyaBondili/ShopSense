# ShopSense Tri-Role Streamlit Dashboards

ShopSense Milestone 3 includes three distinct role-specific dashboards built with **Streamlit** and **Plotly**, connected directly to the FastAPI REST backend via JWT authentication and strict Role-Based Access Control (RBAC).

## Available Dashboards

| Dashboard | File | Target Audience | Features |
|---|---|---|---|
| **Admin Dashboard** | `dashboard/admin_dashboard.py` | Marketplace Admins | Marketplace KPIs (GMV, AOV, Units, Assumed Profit), Customer Intelligence (RFM Segments, Frequent vs Non-Frequent), Recommendation Intelligence, Inventory Intelligence (Demand Forecast & Stock), Revenue Trends, Vendor Rankings, Product Contribution, Scheduler Lifecycle, MLflow Tracking, PDF/Excel Exports |
| **Vendor Dashboard** | `dashboard/vendor_dashboard.py` | Vendors / Sellers | Scoped Shop KPIs, Marketplace Share, Revenue Trends, Top Products, Low-Stock Alerts, Stock Turnover, Marketplace Benchmark, Product Demand Forecast, Shop PDF/Excel Exports |
| **Customer Dashboard** | `dashboard/customer_dashboard.py` | Customers / Buyers | Personalized Recommendations (Collaborative Filtering + Affinity), Personal Order History, Spend & Recency, Customer Segment Badge, Customer Wishlist (Add/Remove) |

## Running the Dashboards

Ensure the FastAPI backend is running first:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 1. Admin Dashboard
```bash
streamlit run dashboard/admin_dashboard.py --server.port 8501
```

### 2. Vendor Dashboard
```bash
streamlit run dashboard/vendor_dashboard.py --server.port 8502
```

### 3. Customer Dashboard
```bash
streamlit run dashboard/customer_dashboard.py --server.port 8503
```
