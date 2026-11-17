import pytest

def test_inventory_turnover_analytics(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/inventory/turnover", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "overall_turnover_rate" in data
    assert "total_cogs" in data
    assert "total_inventory_value" in data
    assert "high_turnover_products" in data
    assert "low_turnover_products" in data

def test_low_stock_alerts_system(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/inventory/alerts", headers=headers)
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)
    for alert in alerts:
        assert "product_id" in alert
        assert "current_stock" in alert
        assert "reorder_level" in alert
        assert "status" in alert
        assert alert["status"] in ["LOW STOCK", "OUT OF STOCK"]
        assert "recommended_action" in alert

def test_inventory_forecasting_random_forest(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/inventory/forecast?horizon=14", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["success", "insufficient_data"]
    if data["status"] == "success":
        assert data["model_type"] == "RandomForestRegressor"
        assert "metrics" in data
        assert "mae" in data["metrics"]
        assert "rmse" in data["metrics"]
        assert "accuracy_pct" in data["metrics"]
        assert data["metrics"]["accuracy_pct"] >= 80.0
        assert "forecast" in data
        assert len(data["forecast"]) == 14

def test_replenishment_recommendation_engine(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/inventory/replenishment?lead_time_days=5", headers=headers)
    assert res.status_code == 200
    recs = res.json()
    assert isinstance(recs, list)
    for r in recs:
        assert "suggested_reorder_quantity" in r
        assert r["suggested_reorder_quantity"] >= 0
        assert r["priority"] in ["HIGH", "MEDIUM", "LOW"]
        assert "reason" in r

def test_customer_behavior_analytics(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/analytics/customers", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_customers" in data
    assert "total_spending" in data
    assert "average_order_value" in data
    assert "customers" in data

def test_customer_segmentation_kmeans(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/analytics/segments", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "silhouette_score" in data["metrics"]
    assert data["metrics"]["silhouette_score"] >= 0.85
    assert "segments" in data
    assert len(data["segments"]) >= 1

def test_product_recommendations_cosine_similarity(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/recommendations?limit=5", headers=headers)
    assert res.status_code == 200
    recs = res.json()
    assert isinstance(recs, list)
    for r in recs:
        assert "product_id" in r
        assert "product_name" in r
        assert "recommendation_reason" in r

def test_recommendation_evaluation_metrics(client, admin_token, db, vendor_user, customer_user):
    from app.models.product import Product
    from app.models.transaction import Transaction
    from datetime import datetime

    # Seed products and customer purchase history so collaborative filtering has data to evaluate
    p1 = Product(product_name="Wireless Mouse", category="Electronics", price=25.0, stock=50, vendor_id=vendor_user.vendor.vendor_id)
    p2 = Product(product_name="Mechanical Keyboard", category="Electronics", price=75.0, stock=30, vendor_id=vendor_user.vendor.vendor_id)
    p3 = Product(product_name="USB-C Hub", category="Electronics", price=35.0, stock=40, vendor_id=vendor_user.vendor.vendor_id)
    db.add_all([p1, p2, p3])
    db.commit()
    db.refresh(p1)
    db.refresh(p2)
    db.refresh(p3)

    t1 = Transaction(user_id=customer_user.user_id, vendor_id=vendor_user.vendor.vendor_id, product_id=p1.product_id, quantity=1, amount=25.0, transaction_date=datetime.now())
    db.add(t1)
    db.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/recommendations/evaluation?k=5", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "relevance_pct" in data["metrics"]
    assert data["metrics"]["relevance_pct"] >= 75.0
    assert "catalog_coverage_pct" in data["metrics"]
