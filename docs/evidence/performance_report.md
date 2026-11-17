# ShopSense API Performance Report — Milestone 3 Task 4

**Target:** p95 <= 300 ms (analytics), <= 3000 ms (PDF/Excel)  
**Iterations per endpoint:** 20  
**Overall result:** ALL PASS  

| Endpoint | Avg (ms) | p95 (ms) | Max (ms) | Target (ms) | Result |
|----------|----------|----------|----------|-------------|--------|
| GET /api/analytics/revenue | 8.78 | 10.26 | 10.46 | 300 | PASS |
| GET /api/analytics/vendor-performance | 11.78 | 16.03 | 16.59 | 300 | PASS |
| GET /api/analytics/customers | 14.34 | 16.45 | 20.83 | 300 | PASS |
| GET /api/forecast/11 | 14.41 | 20.77 | 29.07 | 300 | PASS |
| GET /api/recommend/1 | 12.62 | 16.16 | 16.58 | 300 | PASS |
| GET /api/scheduler/status | 14.36 | 16.15 | 16.46 | 300 | PASS |
| GET /api/analytics/mlflow-status | 9.12 | 14.01 | 15.15 | 300 | PASS |
| GET /api/reports/revenue (PDF) | 10.08 | 10.65 | 11.29 | 3000 | PASS |
| GET /api/reports/revenue (Excel) | 11.04 | 13.33 | 13.87 | 3000 | PASS |

> **Note:** TestClient measurements reflect single-threaded latency within the test process. Locust headless results (50 concurrent users, 60 s) are saved separately in `docs/evidence/locust_stats_stats.csv`.
