"""
ShopSense - Milestone 3 Module 7: Locust API Load & Performance Testing
Evaluates 95th-percentile response time (target <= 300ms) under concurrent load.
Tests:
- GET /analytics/revenue
- GET /analytics/vendor-performance
- GET /analytics/customers
- GET /forecast/2026-11
- GET /recommend/1
- GET /health
"""

from locust import HttpUser, task, between
import random

class ShopSenseAnalyticsUser(HttpUser):
    # Simulated think time between user requests: 0.5 to 2.0 seconds
    wait_time = between(0.5, 2.0)

    @task(3)
    def test_revenue_analytics(self):
        """Test Advanced Revenue Analytics endpoint."""
        self.client.get("/analytics/revenue", name="/analytics/revenue")

    @task(2)
    def test_vendor_performance(self):
        """Test Multi-Vendor Performance endpoint."""
        self.client.get("/analytics/vendor-performance", name="/analytics/vendor-performance")

    @task(2)
    def test_customer_analytics(self):
        """Test Customer Intelligence endpoint."""
        self.client.get("/analytics/customers", name="/analytics/customers")

    @task(1)
    def test_inventory_forecast(self):
        """Test ML Demand Forecasting endpoint."""
        self.client.get("/forecast/2026-11", name="/forecast/{month}")

    @task(2)
    def test_personalized_recommendation(self):
        """Test Cosine Similarity Recommendation endpoint."""
        customer_id = random.choice([1, 2, 3, 4, 5])
        self.client.get(f"/recommend/{customer_id}", name="/recommend/{customer_id}")

    @task(1)
    def test_system_health(self):
        """Test System health endpoint."""
        self.client.get("/health", name="/health")
