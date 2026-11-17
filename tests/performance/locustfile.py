"""
Locust performance load test for ShopSense Milestone 3.
Simulates marketplace load on analytics, forecasting, and ML endpoints.

Usage (headless):
    locust -f tests/performance/locustfile.py \
        --headless -u 50 -r 10 -t 30s \
        --csv docs/evidence/locust_stats \
        --host http://127.0.0.1:8000
"""
import os
import sys
import random
from locust import HttpUser, task, between

# Add project root to sys.path so security helper is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.utils.security import create_access_token

class AnalyticsUser(HttpUser):
    """Simulates active marketplace admin users querying analytics endpoints."""
    wait_time = between(0.05, 0.25)
    token: str = ""
    user_id: int = 55

    def on_start(self):
        """Generate verified JWT admin token for requests."""
        self.token = create_access_token({
            "sub": str(self.user_id),
            "email": "bsreya1610@gmail.com",
            "role": "ADMIN"
        })

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

    @task(3)
    def analytics_revenue(self):
        self.client.get("/api/analytics/revenue", headers=self._headers(), name="/api/analytics/revenue")

    @task(3)
    def analytics_vendor_performance(self):
        self.client.get("/api/analytics/vendor-performance", headers=self._headers(), name="/api/analytics/vendor-performance")

    @task(3)
    def analytics_customers(self):
        self.client.get("/api/analytics/customers", headers=self._headers(), name="/api/analytics/customers")

    @task(2)
    def forecast_month(self):
        month = random.choice([10, 11, 12])
        self.client.get(f"/api/forecast/{month}", headers=self._headers(), name="/api/forecast/{month}")

    @task(2)
    def recommend_user(self):
        uid = random.choice([1, 2, 5, 10, 55])
        self.client.get(f"/api/recommend/{uid}", headers=self._headers(), name="/api/recommend/{user_id}")

    @task(1)
    def scheduler_status(self):
        self.client.get("/api/scheduler/status", headers=self._headers(), name="/api/scheduler/status")

    @task(1)
    def mlflow_status(self):
        self.client.get("/api/analytics/mlflow-status", headers=self._headers(), name="/api/analytics/mlflow-status")
