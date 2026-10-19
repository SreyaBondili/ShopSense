import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add parent and dashboard directories to sys.path
_PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DASHBOARD_DIR = os.path.abspath(os.path.dirname(__file__))
for _p in (_PARENT_DIR, _DASHBOARD_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import importlib

try:
    import dashboard.api_client as _api_module
    importlib.reload(_api_module)
    ApiClient = _api_module.ApiClient
except Exception:
    import api_client as _api_module
    importlib.reload(_api_module)
    ApiClient = _api_module.ApiClient

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
            portal_mode = st.radio(
                "Select Role:",
                ["Admin", "Vendor", "Customer"],
                horizontal=True,
                key="portal_mode"
            )

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


        with tab_register:
            st.subheader("Register New Account")
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_pw = st.text_input("Password (min 6 chars)", type="password", key="reg_pw")
            reg_role = st.selectbox(
                "Role:",
                ["CUSTOMER", "VENDOR", "ADMIN"],
                format_func=lambda r: {"CUSTOMER": "Customer", "VENDOR": "Vendor", "ADMIN": "Admin"}[r],
                key="reg_role"
            )
            admin_code = None
            reg_phone = None
            reg_bname = None
            reg_cat = None

            if reg_role == "ADMIN":
                admin_code = st.text_input("Admin Passcode", type="password", key="reg_admin_code", help="Admin Security Passcode (Admin@123)")
            elif reg_role == "VENDOR":
                reg_bname = st.text_input("Business / Store Name", key="reg_bname", placeholder="e.g. Apex Electronics")
                reg_phone = st.text_input("Phone Number", key="reg_phone", placeholder="e.g. 9876543210")
                reg_cat = st.selectbox(
                    "Store Category",
                    ["Electronics", "Fashion", "Books", "Home & Kitchen", "Beauty & Personal Care", "General"],
                    key="reg_cat"
                )

            if st.button("Create Account", type="primary", use_container_width=True):
                if not reg_name or not reg_email or not reg_pw:
                    st.error("All fields are required.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif reg_role == "ADMIN" and not admin_code:
                    st.error("Admin Security Passcode is required to register an Admin account.")
                elif reg_role == "VENDOR" and not reg_phone:
                    st.error("Phone number is required for Vendor onboarding.")
                else:
                    try:
                        with st.spinner("Creating account..."):
                            resp = api.register(
                                reg_name.strip(),
                                reg_email.strip(),
                                reg_pw,
                                reg_role,
                                admin_secret=admin_code,
                                phone=reg_phone.strip() if reg_phone else None,
                                business_name=reg_bname.strip() if reg_bname else None,
                                category=reg_cat.strip() if reg_cat else None
                            )
                            st.success(f"Account for '{reg_name}' created successfully! You can now sign in.")
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
    st.markdown(f"Logged in as **{user_name}**")

    # Fetch Summary KPIs
    try:
        summary = api.get_summary(token)
    except Exception as e:
        st.error(f"Could not load analytics summary: {e}")
        return

    # Top KPI Metrics
    if role == "ADMIN":
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
        with c2:
            st.metric("Total Orders", f"{summary['total_transactions']:,}")
        with c3:
            st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
        with c4:
            st.metric("Avg Order Value", f"${summary['average_transaction_value']:,.2f}")
        with c5:
            st.metric("Total Vendors", f"{summary['total_vendors']}")
        with c6:
            st.metric("Total Products", f"{summary['total_products']}")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
        with c2:
            st.metric("Total Orders", f"{summary['total_transactions']:,}")
        with c3:
            st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
        with c4:
            st.metric("Avg Order Value", f"${summary['average_transaction_value']:,.2f}")
        with c5:
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
                        err_msg = str(e)
                        if "409" in err_msg or "already registered" in err_msg:
                            st.error(f"⚠️ A vendor with that email is already registered. If they self-registered, you can find them in the list below and change their status to ACTIVE.")
                        else:
                            st.error(f"Vendor onboarding error: {err_msg}")

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
                        err_msg = str(e)
                        if "409" in err_msg or "already exists" in err_msg:
                            st.error(f"⚠️ A product with that name already exists in this vendor's catalog. Use a different name or update the existing product.")
                        else:
                            st.error(f"Product creation failed: {err_msg}")

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
                file_name=f"shopsense_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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
    if role == "ADMIN":
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
        with m2:
            st.metric("Total Transactions", f"{summary['total_transactions']:,}")
        with m3:
            st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
        with m4:
            st.metric("Avg Order Value", f"${summary['average_transaction_value']:,.2f}")
        with m5:
            st.metric("Total Vendors", f"{summary['total_vendors']}")
        with m6:
            st.metric("Total Products", f"{summary['total_products']}")
    else:
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
        with m2:
            st.metric("Total Transactions", f"{summary['total_transactions']:,}")
        with m3:
            st.metric("Units Sold", f"{summary['total_quantity_sold']:,}")
        with m4:
            st.metric("Avg Order Value", f"${summary['average_transaction_value']:,.2f}")
        with m5:
            st.metric("Total Products", f"{summary['total_products']}")

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
# 8. CUSTOMER VIEWS
# ==========================================
def render_customer_catalog():
    token = st.session_state["token"]
    st.title("Products")

    try:
        products = api.get_products(token)
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return

    if not products:
        st.info("No products available.")
        return

    # Filters
    col_search, col_cat = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("Search Products", "").strip().lower()
    with col_cat:
        categories = ["All Categories"] + sorted(list(set(p.get("category", "General") for p in products)))
        selected_category = st.selectbox("Category", categories)

    # Filtered products
    filtered = products
    if search_query:
        filtered = [p for p in filtered if search_query in p.get("product_name", "").lower()]
    if selected_category != "All Categories":
        filtered = [p for p in filtered if p.get("category") == selected_category]

    st.write(f"Showing **{len(filtered)}** products:")

    cols_per_row = 3
    for i in range(0, len(filtered), cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(filtered):
                p = filtered[i + j]
                with row_cols[j]:
                    stock_qty = p.get("stock", 0)
                    if stock_qty == 0:
                        stock_badge = "OUT OF STOCK"
                    elif stock_qty <= 10:
                        stock_badge = f"LOW STOCK ({stock_qty})"
                    else:
                        stock_badge = f"IN STOCK ({stock_qty})"

                    with st.container(border=True):
                        st.subheader(p.get("product_name", "Product"))
                        st.write(f"Category: **{p.get('category', 'General')}**")
                        st.write(f"Price: **${float(p.get('price', 0.0)):,.2f}**")
                        st.write(f"Status: **{stock_badge}**")
                        vendor_disp = p.get("vendor_name") or f"Vendor #{p.get('vendor_id', '')}"
                        st.write(f"Vendor: {vendor_disp}")

                        if stock_qty > 0:
                            qty = st.number_input(
                                "Quantity",
                                min_value=1,
                                max_value=stock_qty,
                                value=1,
                                step=1,
                                key=f"cust_qty_{p['product_id']}"
                            )
                            if st.button("Buy", key=f"cust_buy_{p['product_id']}", type="primary", use_container_width=True):
                                try:
                                    res = api.create_transaction(token, {
                                        "product_id": p["product_id"],
                                        "quantity": qty
                                    })
                                    st.success(f"Order placed successfully! Transaction ID: {res['transaction_id']}")
                                    st.rerun()
                                except Exception as err:
                                    st.error(f"Error placing order: {err}")

def render_customer_orders():
    token = st.session_state["token"]
    user_name = st.session_state.get("user_name", "Customer")
    st.title("My Orders")
    st.markdown(f"Order history for **{user_name}**")

    try:
        txs = api.get_transactions(token)
        if txs:
            df = pd.DataFrame(txs)
            st.dataframe(
                df[["transaction_id", "product_name", "vendor_name", "quantity", "amount", "transaction_date"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("You have not placed any orders yet. Head over to the Products catalog to buy items!")
    except Exception as e:
        st.error(f"Error fetching orders: {e}")

def render_customer_profile():
    st.title("Profile")
    user_name = st.session_state.get("user_name", "Customer")
    user_email = st.session_state.get("user", "")
    role = st.session_state.get("role", "CUSTOMER")

    with st.container(border=True):
        st.subheader(user_name)
        st.write(f"Email: **{user_email}**")
        st.write(f"Role: **{role}**")
        st.write("Status: **ACTIVE**")

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
            if role == "CUSTOMER":
                nav_options = ["Products", "Orders", "Profile"]
            elif role == "ADMIN":
                nav_options = ["Dashboard", "Vendors", "Products", "Inventory", "Transactions", "Analytics"]
            else:  # VENDOR
                nav_options = ["Dashboard", "Products", "Inventory", "Transactions", "Analytics"]

            chosen_page = st.radio("Navigation", nav_options, index=0)

            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                logout()

        # Render chosen page based on role and selection
        if role == "CUSTOMER":
            if chosen_page == "Products":
                render_customer_catalog()
            elif chosen_page == "Orders":
                render_customer_orders()
            elif chosen_page == "Profile":
                render_customer_profile()
        else:
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

