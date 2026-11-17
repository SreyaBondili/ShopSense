"""
ShopSense Vendor Dashboard — Milestone 3 Module 5 & Task 5.
Streamlit + Plotly analytics dashboard scoped strictly to authenticated Vendor's shop data.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dashboard.api_client import ApiClient

st.set_page_config(
    page_title="ShopSense Vendor Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
api = ApiClient(base_url=BACKEND_URL)

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-header { color: #64748B; font-size: 1rem; margin-bottom: 1.5rem; }
    .kpi-card { background: white; padding: 1.2rem; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #0F172A; }
    .kpi-label { font-size: 0.85rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-sub { font-size: 0.75rem; color: #94A3B8; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

if "vendor_auth_token" not in st.session_state:
    st.session_state.vendor_auth_token = None
if "vendor_user_info" not in st.session_state:
    st.session_state.vendor_user_info = None

def vendor_login():
    st.markdown('<div class="main-header">ShopSense Vendor Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Sign in to manage your shop, products, stock alerts, and revenue analytics</div>', unsafe_allow_html=True)
    with st.form("vendor_login_form"):
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Vendor Email", value="")
        with col2:
            password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In to Vendor Portal", use_container_width=True)
        if submitted:
            try:
                res = api.login(email, password)
                if res.get("role") not in ["VENDOR", "ADMIN"]:
                    st.error("Access Denied: Only registered vendors can access this portal (HTTP 403).")
                else:
                    st.session_state.vendor_auth_token = res["access_token"]
                    st.session_state.vendor_user_info = res
                    st.success("Authenticated as Vendor!")
                    st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")

if not st.session_state.vendor_auth_token:
    st.sidebar.title("🏪 Vendor Sign-in")
    vendor_login()
    st.stop()

token = st.session_state.vendor_auth_token
user = st.session_state.vendor_user_info
headers = {"Authorization": f"Bearer {token}"}

st.sidebar.title("🏪 Vendor Workspace")
st.sidebar.markdown(f"**Seller:** {user.get('full_name', 'Vendor')}")
st.sidebar.markdown(f"*{user.get('email', '')}*")
nav_choice = st.sidebar.radio("Navigation", ["Overview", "My Products", "Low-Stock Alerts", "Orders"])

if st.sidebar.button("Sign Out"):
    st.session_state.vendor_auth_token = None
    st.session_state.vendor_user_info = None
    st.rerun()

# ----------------- OVERVIEW TAB -----------------
if nav_choice == "Overview":
    st.markdown('<div class="main-header">Shop Performance & Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Scoped analytics for your store, benchmarked against marketplace averages</div>', unsafe_allow_html=True)

    # Export Buttons
    col_e1, col_e2, _ = st.columns([1, 1, 4])
    with col_e1:
        st.link_button("📥 Export Shop PDF", f"{BACKEND_URL}/api/reports/products?format=pdf")
    with col_e2:
        st.link_button("📊 Export Shop Excel", f"{BACKEND_URL}/api/reports/products?format=excel")

    st.write("")

    # Fetch Vendor-Scoped Analytics
    try:
        # Vendor summary
        rev_res = requests.get(f"{BACKEND_URL}/api/analytics/revenue", headers=headers).json()
        vendor_perf = requests.get(f"{BACKEND_URL}/api/analytics/vendor-performance", headers=headers).json()
        my_products = requests.get(f"{BACKEND_URL}/api/products", headers=headers).json()
    except Exception as e:
        st.error(f"Error fetching vendor analytics: {e}")
        st.stop()

    summary = rev_res.get("summary", {})
    bench = rev_res.get("benchmarking", {})

    # Top KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Shop Revenue</div>
            <div class="kpi-value">₹{summary.get('total_revenue', 0):,.2f}</div>
            <div class="kpi-sub">Total sales generated</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Orders Fulfilled</div>
            <div class="kpi-value">{summary.get('total_transactions', 0):,}</div>
            <div class="kpi-sub">Customer transactions</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Units Sold</div>
            <div class="kpi-value">{summary.get('total_units_sold', 0):,}</div>
            <div class="kpi-sub">Physical inventory sold</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Order Value</div>
            <div class="kpi-value">₹{summary.get('average_order_value', 0):,.2f}</div>
            <div class="kpi-sub">Basket size</div>
        </div>""", unsafe_allow_html=True)
    with k5:
        # Marketplace share
        share = bench.get("market_share_pct", 100.0) if bench else 100.0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Market Share</div>
            <div class="kpi-value">{share:.1f}%</div>
            <div class="kpi-sub">Of total marketplace GMV</div>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # Benchmark vs Marketplace Average
    st.subheader("📊 Shop vs Marketplace Benchmark")
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        m_trend = rev_res.get("monthly_trend", [])
        if m_trend:
            df_m = pd.DataFrame(m_trend)
            fig_t = px.line(df_m, x="month", y="revenue", title="Store Revenue Trend", markers=True)
            st.plotly_chart(fig_t, use_container_width=True)
    with b_col2:
        top_prods = rev_res.get("product_rankings", [])
        if top_prods:
            df_tp = pd.DataFrame(top_prods).head(5)
            fig_tp = px.bar(df_tp, x="revenue", y="product_name", orientation="h", title="Top Selling Store Products")
            st.plotly_chart(fig_tp, use_container_width=True)

elif nav_choice == "My Products":
    st.markdown('<div class="main-header">Product Inventory & Pricing</div>', unsafe_allow_html=True)
    try:
        products = api.get_products(token)
        st.dataframe(pd.DataFrame(products), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to fetch products: {e}")

elif nav_choice == "Low-Stock Alerts":
    st.markdown('<div class="main-header">Inventory Health & Low-Stock Alerts</div>', unsafe_allow_html=True)
    try:
        inv = api.get_inventory(token)
        df_inv = pd.DataFrame(inv)
        if not df_inv.empty and "stock" in df_inv.columns:
            low_stock = df_inv[df_inv["stock"] < 15]
            if not low_stock.empty:
                st.warning(f"⚠️ {len(low_stock)} products require restocking (stock < 15 units):")
                st.dataframe(low_stock, use_container_width=True)
            else:
                st.success("✅ All store products have healthy stock levels.")
        st.subheader("All Store Inventory")
        st.dataframe(df_inv, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to fetch inventory: {e}")

elif nav_choice == "Orders":
    st.markdown('<div class="main-header">Shop Orders & Transactions</div>', unsafe_allow_html=True)
    try:
        txs = api.get_transactions(token)
        st.dataframe(pd.DataFrame(txs), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to fetch transactions: {e}")
