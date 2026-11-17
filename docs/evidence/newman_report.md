# ShopSense Postman / Newman Automated Test Report

- **Total Tests Executed:** 28
- **Passed:** 28
- **Failed:** 0
- **Success Rate:** 100.0%
- **Overall Evaluation:** ALL TESTS PASSED

| # | Folder | Test Name | Method | Endpoint | Status Code | Latency | Result |
|---|---|---|---|---|---|---|---|
| 1 | Authentication & Role Security | Admin Login | `POST` | `/auth/login` | 200 | 607.42 ms | PASS |
| 2 | Authentication & Role Security | Vendor Login | `POST` | `/auth/login` | 200 | 365.75 ms | PASS |
| 3 | Authentication & Role Security | Customer Login | `POST` | `/auth/login` | 200 | 309.28 ms | PASS |
| 4 | Authentication & Role Security | Invalid Login Credentials (Negative Test) | `POST` | `/auth/login` | 401 | 6.99 ms | PASS |
| 5 | Authentication & Role Security | Unauthorized Access (No Token Negative Test) | `GET` | `/api/analytics/revenue` | 401 | 58.55 ms | PASS |
| 6 | Core E-Commerce & Inventory | Get Products Catalog | `GET` | `/api/products` | 200 | 52.92 ms | PASS |
| 7 | Core E-Commerce & Inventory | Get Vendors List | `GET` | `/api/vendors` | 200 | 16.1 ms | PASS |
| 8 | Core E-Commerce & Inventory | Get Inventory Stock & Warehouses | `GET` | `/api/inventory` | 200 | 84.84 ms | PASS |
| 9 | Core E-Commerce & Inventory | Get Low-Stock Shortage Alerts | `GET` | `/api/inventory/alerts` | 200 | 23.48 ms | PASS |
| 10 | Core E-Commerce & Inventory | Get Inventory Turnover Analytics | `GET` | `/api/inventory/turnover` | 200 | 70.23 ms | PASS |
| 11 | Core E-Commerce & Inventory | Get Transactions History | `GET` | `/api/transactions` | 200 | 117.66 ms | PASS |
| 12 | Business Intelligence & Analytics | Advanced Revenue Analytics & GMV | `GET` | `/api/analytics/revenue` | 200 | 198.92 ms | PASS |
| 13 | Business Intelligence & Analytics | Vendor Performance Leaderboard | `GET` | `/api/analytics/vendor-performance` | 200 | 167.81 ms | PASS |
| 14 | Business Intelligence & Analytics | Customer Purchasing Behavior | `GET` | `/api/analytics/customers` | 200 | 759.81 ms | PASS |
| 15 | Business Intelligence & Analytics | Customer Segmentation (K-Means) | `GET` | `/api/analytics/segments` | 200 | 318.03 ms | PASS |
| 16 | Business Intelligence & Analytics | Inventory Demand Forecast | `GET` | `/api/inventory/forecast?horizon=14` | 200 | 421.58 ms | PASS |
| 17 | Business Intelligence & Analytics | Personalized Recommendations | `GET` | `/api/recommendations?limit=5` | 200 | 69.27 ms | PASS |
| 18 | AI Model Management & Operations | Get MLflow Model Status & Registry | `GET` | `/api/analytics/mlflow-status` | 200 | 1179.36 ms | PASS |
| 19 | AI Model Management & Operations | Trigger Model Retraining | `POST` | `/api/analytics/mlflow-retrain` | 200 | 9880.1 ms | PASS |
| 20 | Automation & Monitoring (APScheduler) | Get Automation Pipeline Status | `GET` | `/api/scheduler/status` | 200 | 14.81 ms | PASS |
| 21 | Automation & Monitoring (APScheduler) | Trigger Automated Workflow Manually | `POST` | `/api/scheduler/trigger?job_type=all` | 200 | 8037.73 ms | PASS |
| 22 | Reports & Exports | Download PDF Report (Revenue) | `GET` | `/api/reports/pdf?type=revenue` | 200 | 63.87 ms | PASS |
| 23 | Reports & Exports | Download Excel Report (Revenue) | `GET` | `/api/reports/excel?type=revenue` | 200 | 55.92 ms | PASS |
| 24 | Mentor Reference Compatibility Endpoints | Direct Revenue Analytics | `GET` | `/analytics/revenue` | 200 | 11.83 ms | PASS |
| 25 | Mentor Reference Compatibility Endpoints | Direct Vendor Performance | `GET` | `/analytics/vendor-performance` | 200 | 5.84 ms | PASS |
| 26 | Mentor Reference Compatibility Endpoints | Direct Customer Analytics | `GET` | `/analytics/customers` | 200 | 9.29 ms | PASS |
| 27 | Mentor Reference Compatibility Endpoints | Direct Demand Forecast | `GET` | `/forecast/2026-11` | 200 | 720.38 ms | PASS |
| 28 | Mentor Reference Compatibility Endpoints | Direct Customer Recommendation | `GET` | `/recommend/1` | 200 | 33.51 ms | PASS |
