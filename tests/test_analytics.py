import pytest

def test_analytics_metrics_and_role_scoping(client, admin_token, vendor_token, other_vendor_token):
    # 1. Vendor 1 adds a product and records transaction
    v1_headers = {"Authorization": f"Bearer {vendor_token}"}
    p1 = client.post("/api/products", json={
        "product_name": "Analytics Product 1",
        "category": "Electronics",
        "price": 100.0,
        "stock": 50
    }, headers=v1_headers).json()

    client.post("/api/transactions", json={
        "product_id": p1["product_id"],
        "quantity": 2
    }, headers=v1_headers) # Revenue = $200

    # 2. Vendor 2 adds a product and records transaction
    v2_headers = {"Authorization": f"Bearer {other_vendor_token}"}
    p2 = client.post("/api/products", json={
        "product_name": "Analytics Product 2",
        "category": "Fashion",
        "price": 50.0,
        "stock": 50
    }, headers=v2_headers).json()

    client.post("/api/transactions", json={
        "product_id": p2["product_id"],
        "quantity": 3
    }, headers=v2_headers) # Revenue = $150

    # 3. Check Vendor 1's Analytics: should see ONLY their $200 revenue
    v1_summary = client.get("/api/analytics/summary", headers=v1_headers).json()
    assert v1_summary["total_revenue"] == 200.0
    assert v1_summary["total_transactions"] == 1
    assert v1_summary["total_quantity_sold"] == 2

    # 4. Check Vendor 2's Analytics: should see ONLY their $150 revenue
    v2_summary = client.get("/api/analytics/summary", headers=v2_headers).json()
    assert v2_summary["total_revenue"] == 150.0
    assert v2_summary["total_transactions"] == 1
    assert v2_summary["total_quantity_sold"] == 3

    # 5. Check Admin Analytics: should see marketplace total = $200 + $150 = $350
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_summary = client.get("/api/analytics/summary", headers=admin_headers).json()
    assert admin_summary["total_revenue"] == 350.0
    assert admin_summary["total_transactions"] == 2
    assert admin_summary["total_quantity_sold"] == 5

    # 6. Check Vendor Performance API
    v_perf = client.get("/api/analytics/vendor-performance", headers=admin_headers).json()
    assert len(v_perf) >= 2
    top_vendor = v_perf[0]
    assert top_vendor["total_revenue"] == 200.0 # Vendor 1 is highest

    # 7. Check Product Performance API
    p_perf = client.get("/api/analytics/product-performance", headers=admin_headers).json()
    assert len(p_perf) >= 2
    prod_names = [p["product_name"] for p in p_perf]
    assert "Analytics Product 1" in prod_names
    assert "Analytics Product 2" in prod_names

    # 8. Check Category Performance API
    cat_perf = client.get("/api/analytics/category-performance", headers=admin_headers).json()
    cats = {c["category"]: c["revenue"] for c in cat_perf}
    assert cats.get("Electronics") == 200.0
    assert cats.get("Fashion") == 150.0
