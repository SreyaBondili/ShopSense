"""
ShopSense Customer Dashboard — Milestone 3 Module 5 & Task 5.
Streamlit shopping, recommendation, and account portal for authenticated customers.
"""
import streamlit as st
import pandas as pd
import requests
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dashboard.api_client import ApiClient

st.set_page_config(
    page_title="ShopSense Customer Portal",
    page_icon="🛒",
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
    .rec-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1rem; margin-bottom: 0.8rem; }
    .rec-title { font-weight: 600; font-size: 1.1rem; color: #1E293B; }
    .rec-price { color: #2563EB; font-weight: 700; font-size: 1.2rem; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

if "cust_auth_token" not in st.session_state:
    st.session_state.cust_auth_token = None
if "cust_user_info" not in st.session_state:
    st.session_state.cust_user_info = None

def customer_login():
    st.markdown('<div class="main-header">Welcome to ShopSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Sign in to view your orders, personalized recommendations, and wishlist</div>', unsafe_allow_html=True)
    with st.form("cust_login_form"):
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Customer Email", value="snigdha@gmail.com")
        with col2:
            password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In as Customer", use_container_width=True)
        if submitted:
            try:
                res = api.login(email, password)
                st.session_state.cust_auth_token = res["access_token"]
                st.session_state.cust_user_info = res
                st.success("Authenticated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")

if not st.session_state.cust_auth_token:
    st.sidebar.title("🛒 Customer Login")
    customer_login()
    st.stop()

token = st.session_state.cust_auth_token
user = st.session_state.cust_user_info
uid = user.get("user_id") or user.get("id") or 1
headers = {"Authorization": f"Bearer {token}"}

st.sidebar.title("🛍️ My ShopSense")
st.sidebar.markdown(f"**Customer:** {user.get('full_name', 'Shopper')}")
st.sidebar.markdown(f"*{user.get('email', '')}*")
nav_choice = st.sidebar.radio("Navigation", ["Home & Recommendations", "My Orders", "My Wishlist", "Browse Catalog"])

if st.sidebar.button("Sign Out"):
    st.session_state.cust_auth_token = None
    st.session_state.cust_user_info = None
    st.rerun()

# ----------------- HOME & RECOMMENDATIONS -----------------
if nav_choice == "Home & Recommendations":
    st.markdown(f'<div class="main-header">Hello, {user.get("full_name", "Shopper")}! 👋</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Personalized product picks powered by Item-Based Collaborative Filtering</div>', unsafe_allow_html=True)

    # Fetch Customer Insight / Segment & Orders
    try:
        txs = requests.get(f"{BACKEND_URL}/api/transactions", headers=headers).json()
        orders = txs if isinstance(txs, list) else []
        total_spent = sum(t.get("amount", 0) for t in orders)
        order_count = len(orders)
        rec_res = requests.get(f"{BACKEND_URL}/api/recommend/{uid}", headers=headers).json()
        recs = rec_res.get("recommendations", [])
        strategy = rec_res.get("strategy", "collaborative_filtering")
    except Exception as e:
        orders = []
        recs = []
        total_spent = 0
        order_count = 0
        strategy = "popularity_fallback"

    # KPI Banner
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Spend</div>
            <div class="kpi-value">₹{total_spent:,.2f}</div>
            <div class="kpi-sub">Lifetime orders</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Orders</div>
            <div class="kpi-value">{order_count}</div>
            <div class="kpi-sub">Completed purchases</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        aov = (total_spent / order_count) if order_count > 0 else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Purchase</div>
            <div class="kpi-value">₹{aov:,.2f}</div>
            <div class="kpi-sub">Per order basket</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        seg_label = "High Spenders" if total_spent > 5000 else ("Frequent Buyers" if order_count > 10 else "Valued Shopper")
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Customer Tier</div>
            <div class="kpi-value" style="font-size: 1.4rem; color: #2563EB;">{seg_label}</div>
            <div class="kpi-sub">RFM Segment badge</div>
        </div>""", unsafe_allow_html=True)

    st.write("")
    st.subheader(f"✨ Recommended For You ({strategy.replace('_', ' ').title()})")

    if recs:
        r_cols = st.columns(len(recs) if len(recs) <= 5 else 5)
        for i, item in enumerate(recs[:5]):
            with r_cols[i % len(r_cols)]:
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-title">{item.get('product_name', 'Item')}</div>
                    <div style="color: #64748B; font-size: 0.85rem;">{item.get('category', '')}</div>
                    <div class="rec-price">₹{float(item.get('price', 0)):,.2f}</div>
                    <div style="font-size: 0.75rem; color: #10B981; margin-top: 4px;">Score: {item.get('score', 1.0):.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"❤️ Wishlist", key=f"wish_{item.get('product_id')}"):
                    pid = item.get("product_id")
                    requests.post(f"{BACKEND_URL}/api/wishlist/{pid}", headers=headers)
                    st.toast("Added to your wishlist!")
    else:
        st.info("Start browsing and purchasing products to receive personalized collaborative filtering recommendations!")

elif nav_choice == "My Orders":
    st.markdown('<div class="main-header">My Order History</div>', unsafe_allow_html=True)
    try:
        txs = requests.get(f"{BACKEND_URL}/api/transactions", headers=headers).json()
        if txs:
            st.dataframe(pd.DataFrame(txs), use_container_width=True)
        else:
            st.info("You haven't placed any orders yet.")
    except Exception as e:
        st.error(f"Failed to fetch order history: {e}")

elif nav_choice == "My Wishlist":
    st.markdown('<div class="main-header">Saved Wishlist Items</div>', unsafe_allow_html=True)
    try:
        w_res = requests.get(f"{BACKEND_URL}/api/wishlist", headers=headers).json()
        items = w_res.get("wishlist", [])
        if items:
            for it in items:
                w_col1, w_col2, w_col3 = st.columns([3, 1, 1])
                with w_col1:
                    st.markdown(f"**{it.get('product_name')}** — *{it.get('category')}*")
                with w_col2:
                    st.markdown(f"**₹{it.get('product_price', 0):,.2f}**")
                with w_col3:
                    if st.button("Remove", key=f"del_{it.get('product_id')}"):
                        requests.delete(f"{BACKEND_URL}/api/wishlist/{it.get('product_id')}", headers=headers)
                        st.rerun()
        else:
            st.info("Your wishlist is empty. Add items from recommendations or catalog!")
    except Exception as e:
        st.error(f"Failed to fetch wishlist: {e}")

elif nav_choice == "Browse Catalog":
    st.markdown('<div class="main-header">Shop Catalog</div>', unsafe_allow_html=True)
    try:
        prods = requests.get(f"{BACKEND_URL}/api/products", headers=headers).json()
        st.dataframe(pd.DataFrame(prods), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to fetch catalog: {e}")
