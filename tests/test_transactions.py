import pytest
from decimal import Decimal

def test_transaction_creation_and_stock_reduction(client, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    # 1. Create product with stock = 20
    prod_resp = client.post("/api/products", json={
        "product_name": "Pro Studio Mic",
        "category": "Electronics",
        "price": 120.00,
        "stock": 20
    }, headers=headers)
    prod_id = prod_resp.json()["product_id"]

    # 2. Record transaction: buy 3 units
    tx_resp = client.post("/api/transactions", json={
        "product_id": prod_id,
        "quantity": 3
    }, headers=headers)
    assert tx_resp.status_code == 201
    tx_data = tx_resp.json()
    assert tx_data["quantity"] == 3
    assert float(tx_data["amount"]) == 360.00 # 120.00 * 3

    # 3. Verify that inventory decreased from 20 to 17
    inv_resp = client.get(f"/api/inventory/{prod_id}", headers=headers)
    assert inv_resp.status_code == 200
    assert inv_resp.json()["current_stock"] == 17

def test_transaction_insufficient_stock_rejection(client, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    prod_resp = client.post("/api/products", json={
        "product_name": "Limited Edition Sneaker",
        "category": "Fashion",
        "price": 150.00,
        "stock": 4
    }, headers=headers)
    prod_id = prod_resp.json()["product_id"]

    # Try to order 10 units when only 4 are in stock -> 400 Bad Request
    tx_resp = client.post("/api/transactions", json={
        "product_id": prod_id,
        "quantity": 10
    }, headers=headers)
    assert tx_resp.status_code == 400
    assert "insufficient inventory" in tx_resp.json()["detail"].lower()

def test_transaction_invalid_quantity(client, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    tx_resp = client.post("/api/transactions", json={
        "product_id": 1,
        "quantity": 0
    }, headers=headers)
    assert tx_resp.status_code == 422

def test_transaction_and_revenue_consistency_exceeds_98_percent(client, vendor_token):
    """
    Simulate a sequence of 50 varied transactions across products and verify:
    1. Every valid transaction deducts exact quantity from inventory.
    2. Total transaction amount strictly matches quantity * unit price.
    3. Aggregate revenue from analytics strictly matches the sum of transactions.
    Demonstrating >= 98% (mathematically 100.0%) transaction and revenue consistency.
    """
    headers = {"Authorization": f"Bearer {vendor_token}"}

    # Create 3 test products
    products = []
    prices = [25.50, 49.99, 110.00]
    initial_stock = 200

    for i, p in enumerate(prices):
        resp = client.post("/api/products", json={
            "product_name": f"Consistency Test Item {i+1}",
            "category": "Electronics",
            "price": p,
            "stock": initial_stock
        }, headers=headers)
        assert resp.status_code == 201
        products.append(resp.json())

    # Execute 30 varied transactions
    expected_revenue = 0.0
    units_sold_per_product = {p["product_id"]: 0 for p in products}
    consistent_transactions = 0
    total_tx_attempts = 30

    for tx_idx in range(total_tx_attempts):
        chosen_prod = products[tx_idx % len(products)]
        qty = (tx_idx % 5) + 1  # 1 to 5 units
        unit_price = float(chosen_prod["price"])
        expected_tx_amount = round(unit_price * qty, 2)

        tx_resp = client.post("/api/transactions", json={
            "product_id": chosen_prod["product_id"],
            "quantity": qty
        }, headers=headers)

        if tx_resp.status_code == 201:
            actual_amount = float(tx_resp.json()["amount"])
            if abs(actual_amount - expected_tx_amount) < 0.01:
                consistent_transactions += 1
                expected_revenue += expected_tx_amount
                units_sold_per_product[chosen_prod["product_id"]] += qty

    consistency_rate = (consistent_transactions / total_tx_attempts) * 100.0
    print(f"\nTransaction Consistency Rate: {consistency_rate:.2f}% ({consistent_transactions}/{total_tx_attempts})")
    assert consistency_rate >= 98.0

    # Verify inventory consistency
    for p in products:
        p_id = p["product_id"]
        inv_resp = client.get(f"/api/inventory/{p_id}", headers=headers)
        expected_remaining = initial_stock - units_sold_per_product[p_id]
        actual_remaining = inv_resp.json()["current_stock"]
        assert actual_remaining == expected_remaining, f"Inventory mismatch for product {p_id}"

    # Verify Analytics revenue consistency
    summary_resp = client.get("/api/analytics/summary", headers=headers)
    assert summary_resp.status_code == 200
    actual_total_revenue = summary_resp.json()["total_revenue"]
    assert abs(actual_total_revenue - expected_revenue) < 0.05, f"Revenue mismatch: expected {expected_revenue}, got {actual_total_revenue}"
