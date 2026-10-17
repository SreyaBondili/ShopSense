import pytest

def test_inventory_lifecycle_and_status(client, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    # 1. Create a product with stock = 15, reorder_level default is 10
    prod_resp = client.post("/api/products", json={
        "product_name": "Smart Fitness Band",
        "category": "Electronics",
        "price": 49.99,
        "stock": 15
    }, headers=headers)
    prod_id = prod_resp.json()["product_id"]

    # 2. Check initial inventory status -> IN STOCK
    inv_resp = client.get(f"/api/inventory/{prod_id}", headers=headers)
    assert inv_resp.status_code == 200
    assert inv_resp.json()["current_stock"] == 15
    assert inv_resp.json()["status"] == "IN STOCK"

    # 3. Update stock to 8 (<= reorder_level of 10) -> LOW STOCK
    upd_resp1 = client.put(f"/api/inventory/{prod_id}", json={"current_stock": 8}, headers=headers)
    assert upd_resp1.status_code == 200
    assert upd_resp1.json()["current_stock"] == 8
    assert upd_resp1.json()["status"] == "LOW STOCK"

    # 4. Update stock to 0 -> OUT OF STOCK
    upd_resp2 = client.put(f"/api/inventory/{prod_id}", json={"current_stock": 0}, headers=headers)
    assert upd_resp2.status_code == 200
    assert upd_resp2.json()["current_stock"] == 0
    assert upd_resp2.json()["status"] == "OUT OF STOCK"

def test_inventory_negative_stock_rejection(client, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    prod_resp = client.post("/api/products", json={
        "product_name": "Wireless Charger",
        "category": "Electronics",
        "price": 25.0,
        "stock": 10
    }, headers=headers)
    prod_id = prod_resp.json()["product_id"]

    # Attempt to set negative stock count -> 422 Unprocessable Entity
    resp = client.put(f"/api/inventory/{prod_id}", json={"current_stock": -5}, headers=headers)
    assert resp.status_code == 422
