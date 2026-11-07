"""
ShopSense - Milestone 3 Comprehensive Test Suite
Tests:
- Revenue Analytics Service (GMV, AOV, Gross Profit, Target Benchmarking)
- MLflow Model Service & Registry
- Report Generation (ReportLab PDF & openpyxl Excel)
- FastAPI Milestone 3 Endpoints & Mentor Compatibility Aliases
"""

import pytest
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.services import revenue_service, mlflow_service

def test_revenue_service_calculation(db):
    admin_user = User(user_id=1, role=UserRole.ADMIN)
    rev_data = revenue_service.get_advanced_revenue_analysis(db, admin_user)

    assert "total_revenue" in rev_data
    assert "gmv" in rev_data
    assert "average_order_value" in rev_data
    assert "gross_profit" in rev_data
    assert "cogs" in rev_data
    assert "monthly_breakdown" in rev_data
    assert "vendor_rankings" in rev_data
    assert "benchmarking" in rev_data
    assert rev_data["benchmarking"]["monthly_target"] > 0

def test_api_analytics_revenue(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/revenue", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "vendor_rankings" in data

def test_api_reports_pdf(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/reports/pdf?type=revenue", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 500  # valid PDF binary

def test_api_reports_excel(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/reports/excel?type=revenue", headers=headers)
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert len(response.content) > 500  # valid Excel binary

def test_api_scheduler_endpoints(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Status
    status_res = client.get("/api/scheduler/status", headers=headers)
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert "reliability_success_rate" in status_data
    assert 0.0 <= status_data["reliability_success_rate"] <= 100.0

    # Manual Trigger
    trigger_res = client.post("/api/scheduler/trigger?job_type=analytics", headers=headers)
    assert trigger_res.status_code == 200
    assert trigger_res.json()["status"] == "success"

def test_api_mlflow_endpoints(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    status_res = client.get("/api/analytics/mlflow-status", headers=headers)
    assert status_res.status_code == 200
    ml_data = status_res.json()
    assert ml_data["registered_model_name"] == "InventoryForecast"
    assert ml_data["target_achieved"] is True

def test_mentor_compatibility_endpoints(client):
    """Verify endpoints matching mentor's direct lecture snippets."""
    res_rev = client.get("/analytics/revenue")
    assert res_rev.status_code == 200
    assert "total_revenue" in res_rev.json()

    res_vp = client.get("/analytics/vendor-performance")
    assert res_vp.status_code == 200
    assert isinstance(res_vp.json(), list)

    res_cust = client.get("/analytics/customers")
    assert res_cust.status_code == 200
    assert "total_customers" in res_cust.json()

    res_fc = client.get("/forecast/2026-11")
    assert res_fc.status_code == 200
    assert "predictions" in res_fc.json()

    res_rec = client.get("/recommend/1")
    assert res_rec.status_code == 200
    assert isinstance(res_rec.json(), list)
