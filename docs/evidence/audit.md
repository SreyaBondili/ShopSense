# ShopSense Milestone 3 — Comprehensive System Audit

**Audit Date:** November 7, 2026  
**Auditor:** Antigravity AI Engine  
**System Under Test:** ShopSense Multi-Vendor E-Commerce Analytics Platform  
**Repository:** `https://github.com/SreyaBondili/ShopSense.git` (`main`)  
**Status:** Pre-Remediation Baseline Audit (No code changes applied prior to this audit)

---

## (a) Backend Route Audit & Role-Based Access Control (RBAC) Assessment

### 1. Exhaustive Backend Route Inventory & Vulnerability Matrix

| Router Prefix | Method & Endpoint | Current Auth Dependency | Intended Role | Current Behavior / Role Leakage Vulnerability | Security Severity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Auth** | `POST /auth/register` | Public (None) | Public | Allows self-registration. Anyone can register as `VENDOR` or `CUSTOMER` (or `ADMIN` if passcode supplied). | Low (By Design) |
| **Auth** | `POST /auth/login` | Public (None) | Public | Issues JWT bearer token based on email/password. | Clean |
| **Auth** | `GET /auth/me` | `get_current_active_user` | Any Authenticated | Returns profile for authenticated user. | Clean |
| **Vendors** | `POST /api/vendors` | `get_current_active_user` | ADMIN | **VULNERABLE:** Any authenticated role (including `CUSTOMER`) can trigger vendor onboarding; falls to default status. | **CRITICAL** |
| **Vendors** | `GET /api/vendors` | `get_current_active_user` | ADMIN | **VULNERABLE:** Service checks `if role == VENDOR: return own; else: return all`. Non-vendors (i.e. `CUSTOMER`) fall into `else` and receive **all vendor records**, emails, phone numbers, commission rates, and statuses. | **CRITICAL** |
| **Vendors** | `GET /api/vendors/{id}` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** Only blocks other vendors if `role == VENDOR`. A `CUSTOMER` is not blocked and can view confidential vendor data by ID. | **CRITICAL** |
| **Vendors** | `PUT /api/vendors/{id}` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** Only blocks vendor from altering status/commission. A `CUSTOMER` is not restricted and can modify vendor details. | **CRITICAL** |
| **Vendors** | `DELETE /api/vendors/{id}` | `require_admin` | ADMIN | Restricted to `ADMIN` only. | Clean |
| **Products** | `POST /api/products` | `get_current_active_user` | ADMIN, VENDOR | **VULNERABLE:** Missing role check. A `CUSTOMER` can call this endpoint to add products into catalog. | **HIGH** |
| **Products** | `GET /api/products` | `get_current_active_user` | Public / Any Auth | Catalog browsing. Accessible to all authenticated users. | Clean |
| **Products** | `GET /api/products/{id}` | `get_current_active_user` | Public / Any Auth | Single product details. Accessible to all authenticated users. | Clean |
| **Products** | `PUT /api/products/{id}` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** Service checks ownership only if `role == VENDOR`. `CUSTOMER` is not rejected at route level. | **HIGH** |
| **Products** | `DELETE /api/products/{id}` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** Service checks ownership only if `role == VENDOR`. `CUSTOMER` is not rejected at route level. | **HIGH** |
| **Inventory** | `GET /api/inventory` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** `CUSTOMER` can view warehouse inventory stock levels across all products and locations. | **HIGH** |
| **Inventory** | `GET /api/inventory/alerts` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** `CUSTOMER` can inspect stock shortages, critical stock levels, and supply chain warnings. | **MEDIUM** |
| **Inventory** | `GET /api/inventory/turnover`| `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** `CUSTOMER` can inspect COGS, stock valuation, and inventory turnover ratios. | **MEDIUM** |
| **Inventory** | `GET /api/inventory/forecast`| `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** `CUSTOMER` can view ML demand forecasts and replenishment predictions. | **MEDIUM** |
| **Inventory** | `GET /api/inventory/replenishment` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** `CUSTOMER` can view supplier reorder suggestions and safety stock figures. | **MEDIUM** |
| **Inventory** | `GET /api/inventory/{id}` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** `CUSTOMER` can view warehouse coordinates and bin locations. | **MEDIUM** |
| **Inventory** | `PUT /api/inventory/{id}` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** `CUSTOMER` can alter physical warehouse stock counts and reorder triggers. | **CRITICAL** |
| **Transactions** | `POST /api/transactions` | `get_current_active_user` | Any Auth (scoped) | Creates order. If `CUSTOMER`, should automatically bind `user_id` from token. Currently allows arbitrary payloads. | **HIGH** |
| **Transactions** | `GET /api/transactions` | `get_current_active_user` | ADMIN, VENDOR (own), CUSTOMER (own) | **VULNERABLE:** Filters by vendor if `role == VENDOR`. For non-vendors (`CUSTOMER`), returns **all global platform transactions** across all users. | **CRITICAL** |
| **Transactions** | `GET /api/transactions/{id}` | `get_current_active_user` | ADMIN, VENDOR (own), CUSTOMER (own) | **VULNERABLE:** No customer ownership verification. A `CUSTOMER` can view other customers' transactions. | **HIGH** |
| **Analytics** | `GET /api/analytics/revenue` | `get_current_active_user` | ADMIN | **VULNERABLE:** Executive BI, GMV, total profit (30%), COGS (70%), and vendor rankings exposed to `CUSTOMER` and `VENDOR`. | **CRITICAL** |
| **Analytics** | `GET /api/analytics/mlflow-status` | `get_current_active_user` | ADMIN | **VULNERABLE:** MLflow model registry runs, parameters, and model artifacts exposed to `CUSTOMER` and `VENDOR`. | **HIGH** |
| **Analytics** | `POST /api/analytics/mlflow-retrain` | `require_admin` | ADMIN | Enforces `require_admin`. | Clean |
| **Analytics** | `GET /api/analytics/summary` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** Platform-wide revenue KPIs exposed to `CUSTOMER`. | **HIGH** |
| **Analytics** | `GET /api/analytics/customers` | `get_current_active_user` | ADMIN | **VULNERABLE:** Full customer directory, emails, order counts, and lifetime spending exposed to `CUSTOMER` and `VENDOR`. | **CRITICAL** |
| **Analytics** | `GET /api/analytics/segments` | `get_current_active_user` | ADMIN | **VULNERABLE:** K-Means customer cluster distributions exposed to `CUSTOMER` and `VENDOR`. | **MEDIUM** |
| **Analytics** | `GET /api/analytics/vendor-performance` | `get_current_active_user` | ADMIN | **VULNERABLE:** Competitive vendor performance rankings exposed to `CUSTOMER` and `VENDOR`. | **HIGH** |
| **Analytics** | `GET /api/analytics/product-performance`| `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** Global product margin and unit sales performance exposed to `CUSTOMER`. | **MEDIUM** |
| **Analytics** | `GET /api/analytics/revenue-trend` | `get_current_active_user` | ADMIN, VENDOR (own) | **VULNERABLE:** Financial revenue trends exposed to `CUSTOMER`. | **MEDIUM** |
| **Analytics** | `GET /api/analytics/category-performance` | `get_current_active_user` | ADMIN, VENDOR (own) | Accessible to any authenticated user. | **LOW** |
| **Recommendations** | `GET /api/recommendations` | `get_current_active_user` | CUSTOMER (own), ADMIN | Uses `current_user.user_id` from token. | Clean |
| **Recommendations** | `GET /api/recommendations/evaluation` | `get_current_active_user` | ADMIN | **VULNERABLE:** Model evaluation metrics (Precision@K, Recall@K, Coverage) accessible to `CUSTOMER`. | **MEDIUM** |
| **Reports** | `GET /api/reports/pdf` | `get_current_active_user` | ADMIN, VENDOR (scoped) | **VULNERABLE:** `CUSTOMER` can download executive PDF reports for revenue, vendors, products, and inventory. | **CRITICAL** |
| **Reports** | `GET /api/reports/excel` | `get_current_active_user` | ADMIN, VENDOR (scoped) | **VULNERABLE:** `CUSTOMER` can download complete Excel workbooks containing all financial data. | **CRITICAL** |
| **Scheduler** | `GET /api/scheduler/status` | `get_current_active_user` | ADMIN | **VULNERABLE:** Background job schedules, policy execution history, and cron timestamps accessible to `CUSTOMER` and `VENDOR`. | **HIGH** |
| **Scheduler** | `POST /api/scheduler/trigger` | `require_admin` | ADMIN | Enforces `require_admin`. | Clean |
| **Compatibility** | `GET /analytics/revenue` | Public (None) | ADMIN | **VULNERABLE:** Zero authentication. Returns full revenue BI to any anonymous internet request. | **CRITICAL** |
| **Compatibility** | `GET /analytics/vendor-performance` | Public (None) | ADMIN | **VULNERABLE:** Zero authentication. Returns vendor metrics to any unauthenticated caller. | **CRITICAL** |
| **Compatibility** | `GET /analytics/customers` | Public (None) | ADMIN | **VULNERABLE:** Zero authentication. Returns all customer data without credentials. | **CRITICAL** |
| **Compatibility** | `GET /forecast/{month}` | Public (None) | ADMIN | **VULNERABLE:** Zero authentication. Exposes forecast models to unauthenticated callers. | **HIGH** |
| **Compatibility** | `GET /recommend/{customer_id}` | Public (None) | CUSTOMER (own), ADMIN | **VULNERABLE:** Zero authentication. Allows any caller to query recommendations for arbitrary user IDs. | **HIGH** |

---

## (b) Frontend Route & Menu Item Audit

### 1. Current State in React (`frontend/src/App.jsx`)
In the existing single-page architecture:
- Navigation is controlled entirely by client-side state (`currentPage`) inside `App.jsx`.
- When `user.role === 'CUSTOMER'`:
  - Navigation menu shows: `Shop` (`ShopPage`), `My Cart` (`CartPage`), `My Orders` (`MyOrdersPage`).
  - Menu items for `Vendors`, `Products`, `Inventory`, `Transactions`, `Analytics` are omitted from the sidebar.
- When `user.role === 'ADMIN'`:
  - Navigation menu shows: `Dashboard`, `Vendors`, `Products`, `Inventory`, `Transactions`, `Analytics`.
- When `user.role === 'VENDOR'`:
  - Navigation menu shows: `Dashboard`, `My Products`, `Inventory`, `Transactions`, `Analytics`.

### 2. The Known Security Flaw
1. **Client-side State Forgery / Storage Tampering:** User information is stored in `localStorage.shopsense_user`. If a logged-in Customer modifies their `localStorage.shopsense_user` role to `ADMIN`, the sidebar instantly exposes the `Vendors` menu item, and the main view renders `VendorsPage`.
2. **Missing Route Guard:** `App.jsx` lacks a formal `ProtectedRoute` component or URL path handler. If a component or script calls `setCurrentPage('Vendors')`, the `VendorsPage` renders and calls `api.getVendors()`.
3. **Backend Fails to Validate:** As audited in section (a), the backend `GET /api/vendors` endpoint validates only that a JWT token is present. Because the caller is not `VENDOR`, the backend defaults to the `ADMIN` branch and returns all 16 vendor profiles to the customer.

---

## (c) Dashboard Audit

| Dashboard | File / Implementation | Role | Charts / Visualizations Included |
| :--- | :--- | :--- | :--- |
| **Admin Dashboard (React)** | `frontend/src/pages/DashboardPage.jsx` | ADMIN | - Total Sales, Total Orders, Total Products, Net Margin KPI cards<br>- Revenue Trends (Area Chart)<br>- Sales by Category (Donut/Pie Chart)<br>- Top Vendors by Sales (Bar Chart)<br>- Recent Transactions Table |
| **Analytics BI Suite (React)**| `frontend/src/pages/AnalyticsPage.jsx` | ADMIN | - 8 Tabs: Revenue, Vendors, Customers, Recommendations, Inventory, AI Models (MLflow), Automation, Reports<br>- GMV, AOV, Gross Profit, Target-vs-Actual Benchmarking<br>- RFM Customer Segmentation Scatter & Pie<br>- Demand Forecasting actual vs predicted line chart<br>- APScheduler Execution History & Policy Table |
| **Streamlit Monolith** | `dashboard/dashboard.py` | ADMIN, VENDOR, CUSTOMER | - Single monolithic script (933 lines) using radio button navigation<br>- Admin: Revenue KPIs, Top Products, Low Stock alerts, Turnover<br>- Customer: Simple product grid with buy buttons and basic order history<br>- **Missing:** Independent `admin_dashboard.py`, `vendor_dashboard.py`, `customer_dashboard.py` files with dedicated role scoping and Plotly visualizations. |

---

## (d) Recommendation Service & Algorithm Audit

* **Service File:** `app/services/recommendation_service.py`
* **Current Algorithm:**
  1. Constructs an interaction matrix (Users $\times$ Products) from historical transaction records.
  2. Computes pairwise **User-User Cosine Similarity** on interaction vectors.
  3. Recommends top products purchased by similar users that the target user has not yet purchased.
  4. Fallback: Category-based popularity and stock-level sorting for cold-start users.
* **Evaluation Flaws & Fake Numbers Detected:**
  - In `evaluate_recommendations()` (line 182):
    ```python
    relevance_pct = round(max(avg_precision, 81.2), 2)
    ```
    An artificial floor of `81.2%` is enforced if `avg_precision` falls below it.
  - Does NOT implement a strict **leave-last-purchase-out** offline evaluation protocol.
  - Lacks segment-level recommendation endpoints (`GET /api/recommend/segment/{segment}`).

---

## (e) Forecasting Model & Data Leakage Audit

* **Service Files:** `app/services/mlflow_service.py` and `app/services/forecasting_service.py`
* **Current Evaluation Protocol:**
  - Evaluates using `train_test_split(X, y, test_size=0.20, random_state=...)`.
  - **Data Leakage Issue #1 (Random Splitting):** A standard random split is used on time-series records instead of a strict **chronological hold-out** (e.g. earliest 80% of days for training, most recent 20% of days for testing). This allows the model to train on future days and predict past days.
  - **Data Leakage Issue #2 (Centering & Backfill):**
    ```python
    daily_df["smoothed_demand"] = daily_df["total_quantity"].rolling(7, min_periods=1, center=True).mean()
    daily_df["lag_1"] = daily_df["smoothed_demand"].shift(1).bfill().fillna(0)
    ```
    `center=True` incorporates future dates into the current moving average, and `.bfill()` propagates future values backward into initial timestamps.
* **Operation Summary Mislabeling:**
  - The APScheduler operation summary reports: `"Retrained Random Forest model on 2840 historical sales records..."`.
  - `2840` is actually the total quantity of units sold across all transactions, not the number of training sample rows. The actual number of daily aggregated training rows is $\approx 60-90$.

---

## (f) Scheduler History & Fault-Injection Audit

* **Service File:** `app/scheduler/scheduler_service.py`
* **History Storage:** Single persistent file at `data/scheduler_history.json`.
* **Current Shared-State Flaw:**
  - When `simulate_failed_job()` is executed (or triggered via `/api/scheduler/trigger?job_type=test_failure`), it invokes:
    ```python
    self._record_execution(
        job_id="simulated_failure_job",
        job_name=job_name,
        execution_type=trigger_type,
        status="FAILURE",
        ...
    )
    ```
  - This appends directly to `self.execution_history` and is saved to `data/scheduler_history.json`.
  - The workflow reliability rate is calculated as:
    $$\text{Reliability Rate} = \frac{\text{Successful Executions}}{\text{Total Executions}} \times 100\%$$
  - Consequently, running a simulated test failure **pollutes production history** and directly lowers the production reliability metric below 100%. Fault-injection runs must be tagged with `is_test=True` and excluded from the production reliability calculation.

---

## (g) Streamlit Audit

* **Installed Version:** Streamlit `1.66.0` is installed in `.venv`.
* **Current File Structure:**
  - `dashboard/dashboard.py` exists as a monolithic 933-line prototype combining all roles in a single file with simple Streamlit widgets.
  - Dedicated files requested by the mentor spec (`dashboard/admin_dashboard.py`, `dashboard/vendor_dashboard.py`, `dashboard/customer_dashboard.py`) **do not exist yet**.
  - `dashboard/README.md` is currently missing.

---

## Conclusion & Action Plan

With this baseline audit complete, the system weaknesses are mapped and documented. We now proceed systematically to implement:
1. **Task 1:** Reusable `require_roles()` security dependency on all routes + object-level access controls + frontend ProtectedRoute and error handling.
2. **Task 2:** Item-based collaborative filtering recommendation engine with leave-last-purchase-out evaluation.
3. **Task 3:** Standardized RFM segmentation with honest quality metrics.
4. **Task 4:** Locust performance load tests and optimization.
5. **Task 5:** Tri-role Streamlit dashboards + React dashboard alignment.
6. **Task 6:** Comprehensive dashboard consistency verification.
7. **Task 7:** Workflow validation with `is_test` exclusion logic.
8. **Task 8:** Chronological train/test forecasting without data leakage.
9. **Task 9:** Business logic, targets, and Indian currency standardization.
10. **Task 10:** Non-destructive schema additions (wishlists, persisted recommendations, insight profiles).
11. **Task 11:** Full architecture and traceability documentation.
12. **Task 12:** Full test suite execution and verification.
