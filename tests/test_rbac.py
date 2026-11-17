"""
ShopSense - Milestone 3 Task 12: Role-Based Access Control (RBAC) Test Suite.
Validates the authorization matrix across all caller types:
  1. Anonymous (Unauthenticated) -> 401 Unauthorized
  2. Customer -> 403 Forbidden on Admin/Vendor routes; 200 on Customer routes
  3. Vendor -> 403 Forbidden on Admin routes & other vendors; 200 on Vendor routes
  4. Admin -> 200 OK across all routes
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.security import create_access_token

client = TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def admin_auth():
    token = create_access_token({"sub": "55", "email": "admin@shopsense.com", "role": "ADMIN"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def vendor_auth():
    token = create_access_token({"sub": "61", "email": "vendor@shopsense.com", "role": "VENDOR"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def customer_auth():
    token = create_access_token({"sub": "56", "email": "customer@shopsense.com", "role": "CUSTOMER"})
    return {"Authorization": f"Bearer {token}"}

# ----------------- 1. ANONYMOUS ACCESS (401) -----------------
def test_unauthenticated_requests_return_401():
    """Unauthenticated requests to protected endpoints must return 401."""
    protected_paths = [
        "/api/vendors",
        "/api/analytics/revenue",
        "/api/analytics/customers",
        "/api/analytics/vendor-performance",
        "/api/scheduler/status",
        "/api/analytics/mlflow-status",
        "/api/wishlist"
    ]
    for path in protected_paths:
        resp = client.get(path)
        assert resp.status_code == 401, f"Expected 401 for anonymous access to {path}, got {resp.status_code}"

# ----------------- 2. CUSTOMER RBAC CHECKS (403 on Vendor/Admin routes) -----------------
def test_customer_cannot_access_vendors_page_or_api(customer_auth):
    """KNOWN BUG FIX: Customer must NEVER be able to access vendor management endpoints."""
    # GET /api/vendors
    resp = client.get("/api/vendors", headers=customer_auth)
    assert resp.status_code == 403, f"Expected 403 for Customer GET /api/vendors, got {resp.status_code}"

    # GET /api/vendors/{id}
    resp2 = client.get("/api/vendors/36", headers=customer_auth)
    assert resp2.status_code == 403, f"Expected 403 for Customer GET /api/vendors/36, got {resp2.status_code}"

def test_customer_cannot_access_admin_analytics_or_scheduler(customer_auth):
    """Customer cannot access marketplace analytics, scheduler, or MLflow."""
    assert client.get("/api/analytics/revenue", headers=customer_auth).status_code == 403
    assert client.get("/api/analytics/vendor-revenue", headers=customer_auth).status_code == 403
    assert client.get("/api/analytics/vendor-recommendations", headers=customer_auth).status_code == 403
    assert client.get("/api/recommendations/vendor", headers=customer_auth).status_code == 403
    assert client.get("/api/analytics/customers", headers=customer_auth).status_code == 403
    assert client.get("/api/analytics/vendor-performance", headers=customer_auth).status_code == 403
    assert client.get("/api/scheduler/status", headers=customer_auth).status_code == 403
    assert client.get("/api/analytics/mlflow-status", headers=customer_auth).status_code == 403

def test_customer_can_access_own_wishlist_and_catalog(customer_auth):
    """Customer can access catalog and own wishlist."""
    # Catalog
    cat_resp = client.get("/api/products", headers=customer_auth)
    assert cat_resp.status_code == 200

    # Wishlist
    w_resp = client.get("/api/wishlist", headers=customer_auth)
    assert w_resp.status_code == 200
    assert "wishlist" in w_resp.json()

def test_customer_object_level_recommendations_scoping(customer_auth, admin_auth):
    """Customer can only access own recommendations; accessing another user's id returns 403."""
    # Own recommendations (user_id 56)
    own_resp = client.get("/api/recommend/56", headers=customer_auth)
    assert own_resp.status_code == 200

    # Another customer's recommendations (user_id 57) -> 403 Forbidden
    other_resp = client.get("/api/recommend/57", headers=customer_auth)
    assert other_resp.status_code == 403, f"Expected 403 for cross-user recommendations access, got {other_resp.status_code}"

    # Admin CAN access other user's recommendations
    admin_view_resp = client.get("/api/recommend/57", headers=admin_auth)
    assert admin_view_resp.status_code == 200

# ----------------- 3. VENDOR RBAC CHECKS -----------------
def test_vendor_cannot_access_global_analytics_or_scheduler(vendor_auth):
    """Vendor cannot view global revenue, customer segments, scheduler, MLflow, or global recommendations evaluation."""
    assert client.get("/api/analytics/revenue", headers=vendor_auth).status_code == 403
    assert client.get("/api/recommendations/evaluation", headers=vendor_auth).status_code == 403
    assert client.get("/api/analytics/customers", headers=vendor_auth).status_code == 403
    assert client.get("/api/scheduler/status", headers=vendor_auth).status_code == 403
    assert client.get("/api/analytics/mlflow-status", headers=vendor_auth).status_code == 403

def test_vendor_can_view_own_scoped_products_and_inventory(vendor_auth):
    """Vendor can access products catalog, inventory status, and vendor-scoped recommendations."""
    assert client.get("/api/products", headers=vendor_auth).status_code == 200
    assert client.get("/api/inventory", headers=vendor_auth).status_code == 200
    assert client.get("/api/analytics/vendor-recommendations", headers=vendor_auth).status_code == 200
    assert client.get("/api/recommendations/vendor", headers=vendor_auth).status_code == 200

# ----------------- 4. ADMIN RBAC CHECKS (200 OK across all routes) -----------------
def test_admin_has_full_access(admin_auth):
    """Admin has full 200 OK access across all endpoints."""
    assert client.get("/api/vendors", headers=admin_auth).status_code == 200
    assert client.get("/api/analytics/revenue", headers=admin_auth).status_code == 200
    assert client.get("/api/analytics/customers", headers=admin_auth).status_code == 200
    assert client.get("/api/analytics/vendor-performance", headers=admin_auth).status_code == 200
    assert client.get("/api/scheduler/status", headers=admin_auth).status_code == 200
    assert client.get("/api/analytics/mlflow-status", headers=admin_auth).status_code == 200
    assert client.get("/api/recommend/56", headers=admin_auth).status_code == 200
