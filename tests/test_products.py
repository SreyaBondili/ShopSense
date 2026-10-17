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
