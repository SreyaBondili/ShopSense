# ShopSense Milestone 3 — Shopping & Analytics Workflow

## 1. End-to-End Workflow Diagram

The workflow encompasses customer purchasing, transactional persistence, scheduled ML pipeline retraining, and automated reporting.

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Customer / Buyer
    participant UI as React / Streamlit Client
    participant API as FastAPI REST Gateway
    participant DB as MySQL Database
    participant ML as MLflow & Scikit-Learn
    participant Sched as APScheduler Service
    actor Admin as Marketplace Admin

    %% Shopping & Purchase Flow
    Customer->>UI: Browse Catalog & Recommendations
    UI->>API: GET /api/recommend/{user_id}
    API-->>UI: Top 5 Personalized Products (CF + Category Affinity)
    Customer->>UI: Add to Cart / Wishlist & Checkout
    UI->>API: POST /api/transactions
    API->>DB: INSERT transaction & UPDATE inventory stock
    DB-->>API: Transaction Confirmed
    API-->>UI: HTTP 201 Created

    %% Automated Workflow Pipeline Flow
    Note over Sched: Periodic Interval (Every 2h) or Cron (02:00 AM)
    Sched->>Sched: Trigger Retrain Demand Forecasting Pipeline
    Sched->>DB: Fetch Chronological Daily Sales Series
    DB-->>Sched: Historical Units Sold (Train: earliest 80%, Test: latest 20%)
    Sched->>ML: Train RandomForestRegressor & Compute WAPE
    ML->>ML: Log Params, Metrics & Register Version 'InventoryForecast'
    Sched->>DB: Refresh Customer RFM Segments (K=4) & Quality
    Sched->>Sched: Record Execution in scheduler_history.json

    %% Admin Intelligence & Monitoring Flow
    Admin->>UI: Open Admin Dashboard
    UI->>API: GET /api/analytics/revenue & /api/scheduler/status
    API-->>UI: Consolidated Marketplace KPIs, Forecast & Pipeline Health
    Admin->>UI: Click Export PDF Report
    UI->>API: GET /api/reports/revenue?format=pdf
    API-->>UI: Generated PDF Stream
```

---

## 2. Core Operational Stages

1. **Transactional Stage:**
   - Real-time cart additions, inventory deduction with optimistic locking, and customer orders.
2. **Analytics & Segmentation Stage:**
   - RFM feature extraction (`Recency`, `Frequency`, `Monetary`).
   - K-Means clustering ($K=4$) with normalized silhouettes and 10-seed Adjusted Rand Index stability check.
   - Frequent vs Non-Frequent customer classification based on empirical median order frequency.
3. **Forecasting & ML Lifecycle Stage:**
   - Aggregated daily sales extraction without future leakage (`center=False`, backward lag features).
   - Strict chronological 80/20 train/test holdout evaluation.
   - Automated registration in the MLflow Model Registry.
4. **Automated Pipeline Resilience Stage:**
   - Controlled simulated failure injection tagged `is_test=True`.
   - Production reliability formula excludes test failures while preserving full audit history.
