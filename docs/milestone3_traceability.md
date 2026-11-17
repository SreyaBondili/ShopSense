# ShopSense Milestone 3 — Requirements & Deliverables Traceability Matrix

This matrix maps all 15 official deliverables across Modules 1 through 9 of Milestone 3 to their concrete codebase implementations, automated test files, and verification evidence documents.

| Deliverable ID | Module & Description | Target Evaluation Criterion | Implementation Files | Automated Test Suite | Verification Evidence |
|---|---|---|---|---|---|
| **DEL-01** | **Module 1.A:** Multi-Role Authentication & Security | Role claim in JWT; 401 unauthenticated, 403 unauthorized | `app/utils/security.py`<br>`app/routes/auth.py` | `tests/test_auth.py`<br>`tests/test_rbac.py` | `docs/evidence/audit.md` |
| **DEL-02** | **Module 1.B:** Product & Inventory Catalog | Scoped catalog retrieval and validation | `app/models/product.py`<br>`app/routes/products.py` | `tests/test_products.py`<br>`tests/test_inventory.py` | Postman #6–11 |
| **DEL-03** | **Module 1.C:** Multi-Vendor Transaction Processing | Order placement, stock deduction | `app/models/transaction.py`<br>`app/routes/transactions.py` | `tests/test_transactions.py` | Consistency #2–3 |
| **DEL-04** | **Module 1.D:** Demand Forecasting Pipeline | WAPE Accuracy $\ge 80\%$, strictly chronological holdout | `app/services/forecasting_service.py`<br>`app/routes/analytics.py` | `tests/test_milestone3_services.py` | Accuracy: **85.84%** (`forecasting_service.py`) |
| **DEL-05** | **Module 2.A:** Advanced Revenue Analysis & GMV | Gross profit, 70% assumed COGS, MoM growth | `app/services/revenue_service.py`<br>`app/routes/analytics.py` | `tests/test_analytics.py`<br>`tests/test_dashboard_consistency.py` | Consistency: **100.0%** |
| **DEL-06** | **Module 2.B:** Customer Behavior Analytics & RFM | K-Means ($K=4$), Frequent vs Non-Frequent flags | `app/services/customer_analytics_service.py` | `tests/test_milestone2.py` | Quality: **88.76%** ($\ge 85\%$) |
| **DEL-07** | **Module 2.C:** Item-Based Recommender Engine | Collaborative filtering + popularity fallback | `app/services/recommendation_service.py` | `tests/test_milestone3_services.py`<br>`tests/test_rbac.py` | Hit-Rate@5: **20.65%** ($2.44\times$ lift) |
| **DEL-08** | **Module 3:** MLflow Model Lifecycle & Tracking | Experiment tracking, model artifact, version registry | `app/services/mlflow_service.py` | `tests/test_milestone3_services.py` | MLflow version registered (`InventoryForecast`) |
| **DEL-09** | **Module 4:** Workflow Automation (APScheduler) | Every 2h interval, Daily 02:00 AM cron, 30m refresh | `app/scheduler/scheduler_service.py`<br>`app/routes/scheduler.py` | `tests/test_workflow_automation.py` | Reliability: **100.0%** (100/100 runs) |
| **DEL-10** | **Module 5:** Tri-Role BI Dashboards (Streamlit) | Role-specific dashboards (Admin, Vendor, Customer) | `dashboard/admin_dashboard.py`<br>`dashboard/vendor_dashboard.py`<br>`dashboard/customer_dashboard.py` | `tests/test_dashboard_consistency.py` | Consistency: **100.0%** across 3 roles |
| **DEL-11** | **Module 6:** Performance Testing Under Simulated Load | p95 $\le 300$ ms with 50 concurrent users | `tests/performance/locustfile.py`<br>`app/utils/cache.py` | `tests/performance/test_api_performance.py` | p95 = **290 ms** (`docs/evidence/performance_report.md`) |
| **DEL-12** | **Module 7:** Automated Document & Report Generation | PDF (ReportLab) & Excel (openpyxl) | `app/services/report_service.py`<br>`app/routes/reports.py` | `tests/performance/test_api_performance.py` | Reports exported |
| **DEL-13** | **Module 8:** Automated Data Consistency Verification | Consistency accuracy $\ge 99\%$ | `tests/test_dashboard_consistency.py` | `tests/test_dashboard_consistency.py` | Consistency: **100.0%** |
| **DEL-14** | **Module 9:** Bug Fix & Access Control Audit | Customer denied vendor directory access | `app/routes/vendors.py`<br>`frontend/src/components/ProtectedRoute.jsx` | `tests/test_rbac.py` | `docs/evidence/audit.md` |
| **DEL-15** | **Task 10:** Schema Alignment & Customer Wishlist | Additive tables: wishlist, recommendations, insight | `app/models/wishlist.py`<br>`app/routes/wishlist.py` | `tests/test_wishlist.py` | Tables created |
