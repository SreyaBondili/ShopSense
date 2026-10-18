import pytest

def test_create_product_by_vendor(client, vendor_token, vendor_user):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    payload = {
        "product_name": "Mechanical Gaming Keyboard",
        "category": "Electronics",
        "price": 89.99,
        "stock": 25
    }
    resp = client.post("/api/products", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["product_name"] == "Mechanical Gaming Keyboard"
    assert data["vendor_id"] == vendor_user.vendor.vendor_id
    assert float(data["price"]) == 89.99
    assert data["stock"] == 25

    # Check that inventory was automatically created!
    inv_resp = client.get(f"/api/inventory/{data['product_id']}", headers=headers)
    assert inv_resp.status_code == 200
    assert inv_resp.json()["current_stock"] == 25
    assert inv_resp.json()["status"] == "IN STOCK"

def test_product_validation_negative_price(client, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    payload = {
        "product_name": "Invalid Price Product",
        "category": "Electronics",
        "price": -10.0,
        "stock": 5
    }
    resp = client.post("/api/products", json=payload, headers=headers)
    assert resp.status_code == 422

def test_product_validation_negative_stock(client, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    payload = {
        "product_name": "Invalid Stock Product",
        "category": "Electronics",
        "price": 20.0,
        "stock": -5
    }
    resp = client.post("/api/products", json=payload, headers=headers)
    assert resp.status_code == 422

def test_vendor_cannot_modify_other_vendor_product(client, vendor_token, other_vendor_token, other_vendor_user):
    # Other vendor creates a product
    resp = client.post("/api/products", json={
        "product_name": "Bob's Denim Jacket",
        "category": "Fashion",
        "price": 75.0,
        "stock": 10
    }, headers={"Authorization": f"Bearer {other_vendor_token}"})
    assert resp.status_code == 201
    prod_id = resp.json()["product_id"]

    # First vendor tries to modify or delete Bob's product -> 403 Forbidden
    mod_resp = client.put(f"/api/products/{prod_id}", json={"price": 10.0}, headers={"Authorization": f"Bearer {vendor_token}"})
    assert mod_resp.status_code == 403

    del_resp = client.delete(f"/api/products/{prod_id}", headers={"Authorization": f"Bearer {vendor_token}"})
    assert del_resp.status_code == 403

def test_delete_product_with_sales_history_refused(client, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    # 1. Create product
    prod_resp = client.post("/api/products", json={
        "product_name": "Sales History Protected Item",
        "category": "Electronics",
        "price": 49.99,
        "stock": 10
    }, headers=headers)
    assert prod_resp.status_code == 201
    pid = prod_resp.json()["product_id"]

    # 2. Record a transaction against it
    tx_resp = client.post("/api/transactions", json={
        "product_id": pid,
        "quantity": 1
    }, headers=headers)
    assert tx_resp.status_code == 201

    # 3. Attempt to delete product -> must return 409 Conflict
    del_resp = client.delete(f"/api/products/{pid}", headers=headers)
    assert del_resp.status_code == 409
    assert "sales history" in del_resp.json()["detail"].lower()

def test_suspended_vendor_cannot_update_product(client, admin_token, vendor_token, vendor_user):
    v_headers = {"Authorization": f"Bearer {vendor_token}"}
    a_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Vendor creates product
    prod_resp = client.post("/api/products", json={
        "product_name": "Pre-Suspension Product",
        "category": "Electronics",
        "price": 25.0,
        "stock": 10
    }, headers=v_headers)
    assert prod_resp.status_code == 201
    pid = prod_resp.json()["product_id"]

    # 2. Admin suspends vendor
    vid = vendor_user.vendor.vendor_id
    sus_resp = client.put(f"/api/vendors/{vid}", json={"status": "SUSPENDED"}, headers=a_headers)
    assert sus_resp.status_code == 200

    # 3. Suspended vendor tries to update product -> 403
    up_resp = client.put(f"/api/products/{pid}", json={"price": 30.0}, headers=v_headers)
    assert up_resp.status_code == 403

    # Clean up vendor status back to ACTIVE for other tests
    client.put(f"/api/vendors/{vid}", json={"status": "ACTIVE"}, headers=a_headers)
