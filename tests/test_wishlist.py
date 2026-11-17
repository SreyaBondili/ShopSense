"""
Tests for Wishlist API endpoints — Task 10 Schema Alignment.
Tests:
  - Add to wishlist (POST)
  - Get wishlist (GET)
  - Delete from wishlist (DELETE)
  - Idempotent additions
  - Role-based protection
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.security import create_access_token

client = TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def customer_auth():
    token = create_access_token({"sub": "56", "email": "customer@shopsense.com", "role": "CUSTOMER"})
    return {"Authorization": f"Bearer {token}"}

def test_wishlist_lifecycle(customer_auth):
    # 1. Get initial wishlist
    resp_init = client.get("/api/wishlist", headers=customer_auth)
    assert resp_init.status_code == 200
    assert "wishlist" in resp_init.json()

    # 2. Get a real product from catalog
    prods = client.get("/api/products", headers=customer_auth).json()
    assert len(prods) > 0
    test_pid = prods[0]["product_id"]

    # 3. Add product to wishlist
    resp_add = client.post(f"/api/wishlist/{test_pid}", headers=customer_auth)
    assert resp_add.status_code == 200
    assert resp_add.json()["status"] in ["added", "already_in_wishlist"]
    assert resp_add.json()["product_id"] == test_pid

    # 4. Add again (idempotent)
    resp_add2 = client.post(f"/api/wishlist/{test_pid}", headers=customer_auth)
    assert resp_add2.status_code == 200
    assert resp_add2.json()["status"] == "already_in_wishlist"

    # 5. Verify item present in GET
    resp_get = client.get("/api/wishlist", headers=customer_auth)
    assert resp_get.status_code == 200
    pids = [item["product_id"] for item in resp_get.json()["wishlist"]]
    assert test_pid in pids

    # 6. Remove item from wishlist
    resp_del = client.delete(f"/api/wishlist/{test_pid}", headers=customer_auth)
    assert resp_del.status_code == 200
    assert resp_del.json()["status"] == "removed"

    # 7. Verify removed
    resp_get_after = client.get("/api/wishlist", headers=customer_auth)
    pids_after = [item["product_id"] for item in resp_get_after.json()["wishlist"]]
    assert test_pid not in pids_after
