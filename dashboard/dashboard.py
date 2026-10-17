import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add parent directory to path to allow importing app modules if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from dashboard.api_client import ApiClient
except (ImportError, ModuleNotFoundError):
    from api_client import ApiClient

# Page configuration
st.set_page_config(
    page_title="ShopSense – Multi-Vendor Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API Client
BACKEND_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
api = ApiClient(base_url=BACKEND_URL)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .status-badge-active {
        background-color: #d4edda;
        color: #155724;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .status-badge-pending {
        background-color: #fff3cd;
        color: #856404;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .status-badge-suspended {
        background-color: #f8d7da;
        color: #721c24;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "vendor_id" not in st.session_state:
    st.session_state["vendor_id"] = None

def logout():
    st.session_state["token"] = None
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.session_state["vendor_id"] = None
    st.rerun()

# ==========================================
# 1. AUTHENTICATION (LOGIN / REGISTER)
# ==========================================
def render_auth_page():
    st.title("🛍️ ShopSense – Multi-Vendor Analytics Platform")

    _, col1, _ = st.columns([1, 2, 1])

    with col1:
        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            st.subheader("Login to your Account")
            login_email = st.text_input("Email Address", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")

            if st.button("Sign In", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please enter both email and password.")
                else:
                    try:
                        with st.spinner("Authenticating..."):
                            resp = api.login(login_email.strip(), login_password)
                            st.session_state["token"] = resp["access_token"]
                            st.session_state["user"] = resp["email"]
                            st.session_state["user_name"] = resp["full_name"]
                            st.session_state["role"] = resp["role"]
                            st.session_state["vendor_id"] = resp.get("vendor_id")
                            st.success(f"Welcome back, {resp['full_name']}!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")

            st.markdown("---")
            st.markdown("**Quick Demo Logins:**")
            col_admin, col_vendor = st.columns(2)
            with col_admin:
                if st.button("🔑 Quick Admin Login", use_container_width=True):
                    try:
                        resp = api.login("admin@shopsense.com", "Admin@123")
                        st.session_state["token"] = resp["access_token"]
                        st.session_state["user"] = resp["email"]
                        st.session_state["user_name"] = resp["full_name"]
                        st.session_state["role"] = resp["role"]
                        st.session_state["vendor_id"] = resp.get("vendor_id")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Demo login failed: {str(e)}")
            with col_vendor:
                if st.button("🏪 Quick Vendor Login", use_container_width=True):
                    try:
                        resp = api.login("techworld@example.com", "Vendor@123")
                        st.session_state["token"] = resp["access_token"]
                        st.session_state["user"] = resp["email"]
                        st.session_state["user_name"] = resp["full_name"]
                        st.session_state["role"] = resp["role"]
                        st.session_state["vendor_id"] = resp.get("vendor_id")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Demo login failed: {str(e)}")

        with tab_register:
            st.subheader("Register New Account")
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_pw = st.text_input("Password (min 6 chars)", type="password", key="reg_pw")
            reg_role = st.selectbox("Role", ["VENDOR", "ADMIN"], key="reg_role")

            if st.button("Register", use_container_width=True):
                if not reg_name or not reg_email or not reg_pw:
                    st.error("All fields are required.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    try:
                        with st.spinner("Creating account..."):
                            resp = api.register(reg_name, reg_email, reg_pw, reg_role)
                            st.success("Account created successfully! You can now sign in.")
                    except Exception as e:
                        st.error(f"Registration error: {str(e)}")


# ==========================================
# 2. DASHBOARD VIEW (ADMIN / VENDOR)
# ==========================================
def render_dashboard_page():
    role = st.session_state["role"]
    token = st.session_state["token"]
    user_name = st.session_state.get("user_name", "User")
    
    st.title(f"📊 {'Marketplace Executive Dashboard' if role == 'ADMIN' else 'Vendor Performance Portal'}")
    st.markdown(f"Logged in as **{user_name}** ({role})")

    # Fetch Summary KPIs
    try:
        summary = api.get_summary(token)
    except Exception as e:
        st.error(f"Could not load analytics summary: {e}")
        return

    # Top KPI Metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
    with c2:
        st.metric("Total Transactions", f"{summary['total_transactions']:,}")
    with c3:
        st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
    with c4:
        st.metric("Avg Order Value", f"${summary['average_transaction_value']:,.2f}")
    with c5:
        if role == "ADMIN":
            st.metric("Total Vendors", f"{summary['total_vendors']}")
        else:
            st.metric("Total Products", f"{summary['total_products']}")

    st.markdown("---")

    # Visualizations
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📈 Revenue Over Time")
        trend_data = api.get_revenue_trend(token)
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            fig_trend = px.area(
                df_trend,
                x="date",
                y="revenue",
                title="Daily Revenue Trend",
                labels={"date": "Transaction Date", "revenue": "Revenue ($)"},
                markers=True
            )
            fig_trend.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No transaction history recorded yet.")

    with col_right:
        st.subheader("🥧 Category Distribution")
        cat_data = api.get_category_performance(token)
        if cat_data:
            df_cat = pd.DataFrame(cat_data)
            fig_cat = px.pie(
                df_cat,
                names="category",
                values="revenue",
                title="Revenue by Product Category",
                hole=0.4
            )
            fig_cat.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data available.")

    # Second row of charts
    c_bottom1, c_bottom2 = st.columns(2)

    with c_bottom1:
        if role == "ADMIN":
            st.subheader("🏆 Vendor Performance Breakdown")
            v_perf = api.get_vendor_performance(token)
            if v_perf:
                df_v = pd.DataFrame(v_perf)
                fig_v = px.bar(
                    df_v,
                    x="business_name",
                    y="total_revenue",
                    color="category",
                    title="Revenue by Vendor",
                    labels={"business_name": "Vendor", "total_revenue": "Revenue ($)"}
                )
                fig_v.update_layout(template="plotly_white")
                st.plotly_chart(fig_v, use_container_width=True)
            else:
                st.info("No vendor metrics recorded.")
        else:
            st.subheader("📦 Product Sales Performance")
            p_perf = api.get_product_performance(token)
            if p_perf:
                df_p = pd.DataFrame(p_perf)
                fig_p = px.bar(
                    df_p,
                    x="product_name",
                    y="total_revenue",
                    color="quantity_sold",
                    title="Revenue by Product",
                    labels={"product_name": "Product", "total_revenue": "Revenue ($)"}
                )
                fig_p.update_layout(template="plotly_white")
                st.plotly_chart(fig_p, use_container_width=True)
            else:
                st.info("No product metrics available.")

    with c_bottom2:
        st.subheader("📊 Top Selling Products")
        p_perf = api.get_product_performance(token)
        if p_perf:
            df_top = pd.DataFrame(p_perf).sort_values(by="quantity_sold", ascending=False).head(5)
            fig_top = px.bar(
                df_top,
                x="quantity_sold",
                y="product_name",
                orientation="h",
                title="Top 5 Products by Units Sold",
                labels={"quantity_sold": "Units Sold", "product_name": "Product"}
            )
            fig_top.update_layout(template="plotly_white", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("No sales data available.")

# ==========================================
# 3. VENDOR MANAGEMENT PAGE (ADMIN ONLY)
# ==========================================
def render_vendors_page():
    token = st.session_state["token"]
    role = st.session_state["role"]

    st.title("🏢 Vendor Management & Onboarding")

    if role != "ADMIN":
        st.warning("Only Marketplace Administrators can manage vendor accounts.")
        return

    # Add Vendor Expandable Form
    with st.expander("➕ Onboard New Vendor", expanded=False):
        with st.form("add_vendor_form"):
            c1, c2 = st.columns(2)
            with c1:
                b_name = st.text_input("Business Name *")
                o_name = st.text_input("Owner Name *")
                v_email = st.text_input("Vendor Email *")
            with c2:
                v_phone = st.text_input("Phone Number * (10-15 digits)")
                v_cat = st.selectbox("Category *", [
                    "Electronics", "Fashion", "Books", "Home & Kitchen",
                    "Beauty & Personal Care", "Sports & Fitness", "Automotive", "Other"
                ])
                v_comm = st.number_input("Commission Rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)

            submitted = st.form_submit_button("Register & Activate Vendor", type="primary")
            if submitted:
                if not b_name or not o_name or not v_email or not v_phone:
                    st.error("Please complete all required fields.")
                else:
                    try:
                        api.create_vendor(token, {
                            "business_name": b_name,
                            "owner_name": o_name,
                            "email": v_email,
                            "phone": v_phone,
                            "category": v_cat,
                            "commission_rate": v_comm,
                            "status": "ACTIVE"
                        })
                        st.success(f"Vendor '{b_name}' successfully onboarded!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Vendor onboarding error: {str(e)}")

    # Filter and Search
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        search_kw = st.text_input("🔍 Search vendors...", "")
    with f2:
        cat_filter = st.selectbox("Category Filter", ["All", "Electronics", "Fashion", "Books", "Home & Kitchen", "Beauty & Personal Care"])
    with f3:
        status_filter = st.selectbox("Status Filter", ["All", "ACTIVE", "PENDING", "SUSPENDED"])

    try:
        vendors = api.get_vendors(token, search=search_kw, category=cat_filter, status=status_filter)
        if vendors:
            df_v = pd.DataFrame(vendors)
            st.dataframe(
                df_v[["vendor_id", "business_name", "owner_name", "email", "phone", "category", "commission_rate", "status", "created_at"]],
                use_container_width=True,
                hide_index=True
            )

            # Quick Actions Section
            st.subheader("⚙️ Vendor Actions")
            sel_vendor_id = st.selectbox("Select Vendor to manage", [v["vendor_id"] for v in vendors], format_func=lambda x: f"Vendor #{x} - {[v['business_name'] for v in vendors if v['vendor_id']==x][0]}")
            curr_vendor = next(v for v in vendors if v["vendor_id"] == sel_vendor_id)

            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                new_status = st.selectbox("Change Status", ["ACTIVE", "PENDING", "SUSPENDED"], index=["ACTIVE", "PENDING", "SUSPENDED"].index(curr_vendor["status"]))
                if st.button("Update Status"):
                    try:
                        api.update_vendor(token, sel_vendor_id, {"status": new_status})
                        st.success(f"Status for Vendor #{sel_vendor_id} changed to {new_status}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
            with col_act2:
                new_rate = st.number_input("Update Commission (%)", value=float(curr_vendor["commission_rate"]), min_value=0.0, max_value=100.0)
                if st.button("Save Commission"):
                    try:
                        api.update_vendor(token, sel_vendor_id, {"commission_rate": new_rate})
                        st.success("Commission updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update commission: {e}")
            with col_act3:
                st.write("Danger Zone:")
                if st.button("🗑️ Delete Vendor", type="secondary"):
                    try:
                        api.delete_vendor(token, sel_vendor_id)
                        st.success(f"Vendor #{sel_vendor_id} removed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Deletion failed: {e}")
        else:
            st.info("No vendors found matching criteria.")
    except Exception as e:
        st.error(f"Error loading vendors: {e}")

# ==========================================
# 4. PRODUCT CATALOG PAGE
# ==========================================
def render_products_page():
    token = st.session_state["token"]
    role = st.session_state["role"]

    st.title("📦 Product Catalog Management")

    # Add Product Form
    with st.expander("➕ Add New Product", expanded=False):
        with st.form("add_product_form"):
            c1, c2 = st.columns(2)
            with c1:
                p_name = st.text_input("Product Name *")
                p_cat = st.selectbox("Category *", [
                    "Electronics", "Fashion", "Books", "Home & Kitchen",
                    "Beauty & Personal Care", "Sports & Fitness", "Toys & Games", "Other"
                ])
                p_price = st.number_input("Unit Price ($) *", min_value=0.01, value=49.99, step=1.0)
            with c2:
                p_stock = st.number_input("Initial Inventory Stock *", min_value=0, value=20, step=1)
                p_vendor_id = None
                if role == "ADMIN":
                    all_vendors = api.get_vendors(token)
                    v_options = {v["vendor_id"]: v["business_name"] for v in all_vendors}
                    if v_options:
                        p_vendor_id = st.selectbox("Assign to Vendor", options=list(v_options.keys()), format_func=lambda x: f"{v_options[x]} (ID: {x})")
                    else:
                        st.warning("No vendors available. Please onboard a vendor first.")

            submitted = st.form_submit_button("Add Product to Catalog", type="primary")
            if submitted:
                if not p_name:
                    st.error("Product name is required.")
                else:
                    payload = {
                        "product_name": p_name,
                        "category": p_cat,
                        "price": p_price,
                        "stock": p_stock
                    }
                    if role == "ADMIN" and p_vendor_id:
                        payload["vendor_id"] = p_vendor_id
                    try:
                        api.create_product(token, payload)
                        st.success(f"Product '{p_name}' successfully added and inventory initialized!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Product creation failed: {e}")

    # Search & Filters
    f1, f2 = st.columns([3, 1])
    with f1:
        search_kw = st.text_input("🔍 Search products...", "")
    with f2:
        cat_filter = st.selectbox("Category", ["All", "Electronics", "Fashion", "Books", "Home & Kitchen", "Beauty & Personal Care"])

    try:
        products = api.get_products(token, search=search_kw, category=cat_filter)
        if products:
            df_p = pd.DataFrame(products)
            st.dataframe(
                df_p[["product_id", "product_name", "category", "price", "stock", "vendor_name", "created_at"]],
                use_container_width=True,
                hide_index=True
            )

            # Edit/Delete Product Section
            st.subheader("✏️ Edit Product Details")
            sel_prod_id = st.selectbox("Select product to edit", [p["product_id"] for p in products], format_func=lambda x: f"#{x} - {[p['product_name'] for p in products if p['product_id']==x][0]}")
            curr_prod = next(p for p in products if p["product_id"] == sel_prod_id)

            e1, e2, e3 = st.columns(3)
            with e1:
                edit_price = st.number_input("New Price ($)", value=float(curr_prod["price"]), min_value=0.01, step=1.0)
            with e2:
                edit_stock = st.number_input("Sync Stock", value=int(curr_prod["stock"]), min_value=0, step=1)
            with e3:
                st.write("Actions:")
                col_save, col_del = st.columns(2)
                with col_save:
                    if st.button("Save Edits"):
                        try:
                            api.update_product(token, sel_prod_id, {"price": edit_price, "stock": edit_stock})
                            st.success("Product updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")
                with col_del:
                    if st.button("🗑️ Delete"):
                        try:
                            api.delete_product(token, sel_prod_id)
                            st.success("Product deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {e}")
        else:
            st.info("No products found.")
    except Exception as e:
        st.error(f"Error fetching products: {e}")

# ==========================================
# 5. INVENTORY MANAGEMENT PAGE
# ==========================================
def render_inventory_page():
    token = st.session_state["token"]
    st.title("📋 Inventory Management & Warehouse Tracking")

    status_filter = st.selectbox("Filter by Stock Status", ["All", "IN STOCK", "LOW STOCK", "OUT OF STOCK"])

    try:
        inv_items = api.get_inventory(token, status=status_filter)
        if inv_items:
            df_inv = pd.DataFrame(inv_items)

            # Summary KPIs for Inventory
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                st.metric("Total Tracked Items", len(df_inv))
            with i2:
                in_stock_cnt = len(df_inv[df_inv["status"] == "IN STOCK"])
                st.metric("In Stock", in_stock_cnt)
            with i3:
                low_stock_cnt = len(df_inv[df_inv["status"] == "LOW STOCK"])
                st.metric("Low Stock Alerts", low_stock_cnt)
            with i4:
                out_stock_cnt = len(df_inv[df_inv["status"] == "OUT OF STOCK"])
                st.metric("Out of Stock", out_stock_cnt)

            st.dataframe(
                df_inv[["inventory_id", "product_name", "vendor_name", "current_stock", "reorder_level", "warehouse", "status", "updated_at"]],
                use_container_width=True,
                hide_index=True
            )

            # Stock Adjustment Section
            st.subheader("📦 Update Inventory Levels")
            sel_item_id = st.selectbox("Select product to restock", [item["product_id"] for item in inv_items], format_func=lambda x: f"Product #{x} - {[item['product_name'] for item in inv_items if item['product_id']==x][0]}")
            curr_item = next(item for item in inv_items if item["product_id"] == sel_item_id)

            u1, u2, u3 = st.columns(3)
            with u1:
                new_stock = st.number_input("Current Stock Count", value=int(curr_item["current_stock"]), min_value=0, step=1)
            with u2:
                new_reorder = st.number_input("Reorder Threshold", value=int(curr_item["reorder_level"]), min_value=0, step=1)
            with u3:
                new_warehouse = st.text_input("Warehouse Location", value=str(curr_item["warehouse"]))

            if st.button("Update Inventory Record", type="primary"):
                try:
                    api.update_inventory(token, sel_item_id, {
                        "current_stock": new_stock,
                        "reorder_level": new_reorder,
                        "warehouse": new_warehouse
                    })
                    st.success("Inventory updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")
        else:
            st.info("No inventory records found.")
    except Exception as e:
        st.error(f"Error loading inventory: {e}")

# ==========================================
# 6. TRANSACTIONS PAGE
# ==========================================
def render_transactions_page():
    token = st.session_state["token"]
    role = st.session_state["role"]
    st.title("💳 Transaction Management & Sales Ledger")

    # Transaction Creation Form
    with st.expander("🛒 Record New Sale / Order", expanded=False):
        products = api.get_products(token)
        if products:
            p_dict = {p["product_id"]: p for p in products if p["stock"] > 0}
            if p_dict:
                sel_p_id = st.selectbox(
                    "Select Product to Sell",
                    options=list(p_dict.keys()),
                    format_func=lambda x: f"{p_dict[x]['product_name']} | Price: ${p_dict[x]['price']} | Available: {p_dict[x]['stock']} in stock"
                )
                selected_prod = p_dict[sel_p_id]
                col_q, col_calc = st.columns(2)
                with col_q:
                    qty = st.number_input("Quantity to purchase", min_value=1, max_value=selected_prod["stock"], value=1, step=1)
                with col_calc:
                    est_total = float(selected_prod["price"]) * qty
                    st.write(f"**Total Transaction Value:** `${est_total:,.2f}`")

                if st.button("Confirm & Complete Transaction", type="primary"):
                    try:
                        resp = api.create_transaction(token, {
                            "product_id": sel_p_id,
                            "quantity": qty
                        })
                        st.success(f"Transaction #{resp['transaction_id']} executed! Stock automatically decremented.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Transaction failed: {e}")
            else:
                st.warning("All products are currently out of stock. Please restock via the Inventory tab.")
        else:
            st.info("No products available to purchase.")

    # Historical Transactions Table
    try:
        tx_list = api.get_transactions(token)
        if tx_list:
            df_tx = pd.DataFrame(tx_list)
            st.subheader(f"📜 Sales History ({len(df_tx)} Total Transactions)")
            st.dataframe(
                df_tx[["transaction_id", "product_name", "vendor_name", "quantity", "amount", "transaction_date"]],
                use_container_width=True,
                hide_index=True
            )

            # Export to CSV
            csv = df_tx.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Transactions CSV",
                data=csv,
                file_name=f"shopsense_transactions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
        else:
            st.info("No transaction records recorded yet.")
    except Exception as e:
        st.error(f"Error fetching transactions: {e}")

# ==========================================
# 7. ANALYTICS & REPORTING PAGE
# ==========================================
def render_analytics_page():
    token = st.session_state["token"]
    role = st.session_state["role"]
    st.title("📈 Marketplace Analytics & Performance Reports")

    # Overview KPIs
    summary = api.get_summary(token)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
    with m2:
        st.metric("Total Transactions", f"{summary['total_transactions']:,}")
    with m3:
        st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
    with m4:
        st.metric("Avg Transaction Value", f"${summary['average_transaction_value']:,.2f}")

    st.markdown("---")

    # Revenue Trend Chart
    st.subheader("📅 Time-Series Revenue Aggregation")
    trend_data = api.get_revenue_trend(token)
    if trend_data:
        df_trend = pd.DataFrame(trend_data)
        fig = px.bar(
            df_trend,
            x="date",
            y="revenue",
            text_auto=True,
            title="Revenue Aggregated by Date",
            labels={"date": "Date", "revenue": "Revenue ($)"}
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    # Vendor & Product Performance Tables
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.subheader("🏢 Vendor Revenue Breakdown")
        v_data = api.get_vendor_performance(token)
        if v_data:
            df_v = pd.DataFrame(v_data)
            st.dataframe(
                df_v[["business_name", "category", "total_revenue", "total_transactions", "total_quantity_sold"]],
                use_container_width=True,
                hide_index=True
            )
            csv_v = df_v.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Vendor Metrics CSV",
                csv_v,
                "vendor_performance.csv",
                "text/csv"
            )

    with col_t2:
        st.subheader("🏷️ Product Sales Ranking")
        p_data = api.get_product_performance(token)
        if p_data:
            df_p = pd.DataFrame(p_data)
            st.dataframe(
                df_p[["product_name", "category", "total_revenue", "quantity_sold", "inventory_status"]],
                use_container_width=True,
                hide_index=True
            )
            csv_p = df_p.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Product Metrics CSV",
                csv_p,
                "product_performance.csv",
                "text/csv"
            )

# ==========================================
# MAIN APPLICATION ROUTER
# ==========================================
def main():
    if not st.session_state["token"]:
        render_auth_page()
    else:
        role = st.session_state["role"]
        user_email = st.session_state["user"]
        user_name = st.session_state.get("user_name", "User")

        # Sidebar Navigation
        with st.sidebar:
            st.title("🛍️ ShopSense")
            st.caption(f"Role: **{role}**")
            st.write(f"👤 {user_name}")
            st.write(f"📧 {user_email}")
            st.markdown("---")

            # Nav items depend on role
            nav_options = ["Dashboard", "Products", "Inventory", "Transactions", "Analytics"]
            if role == "ADMIN":
                nav_options.insert(1, "Vendors")

            chosen_page = st.radio("Navigation", nav_options, index=0)

            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                logout()

        # Render chosen page
        if chosen_page == "Dashboard":
            render_dashboard_page()
        elif chosen_page == "Vendors":
            render_vendors_page()
        elif chosen_page == "Products":
            render_products_page()
        elif chosen_page == "Inventory":
            render_inventory_page()
        elif chosen_page == "Transactions":
            render_transactions_page()
        elif chosen_page == "Analytics":
            render_analytics_page()

if __name__ == "__main__":
    main()
