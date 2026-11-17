# ShopSense Milestone 3 — Machine Learning Justification & Integrity Report

## 1. Demand Forecasting Model Selection: Random Forest Regressor

### Justification vs Alternatives

| Model Evaluated | Pros | Cons in E-Commerce Marketplace | Decision |
|---|---|---|---|
| **Random Forest Regressor** *(Selected)* | • Captures non-linear seasonality, holiday bursts, and day-of-week demand velocity.<br>• Robust against single-day outliers without overfitting.<br>• Native feature importance tracking for inventory managers.<br>• Fast retraining (< 1 second) in automated cron pipelines. | Does not extrapolate long-term macro trends beyond feature boundaries. | **Adopted for Milestone 3 production pipeline.** |
| **ARIMA / SARIMAX** | Strong linear statistical foundation for smooth uni-variate series. | Requires strict stationarity; struggles with intermittent zero-sales days and multi-category cross-effects; high fitting latency. | Rejected |
| **Prophet (Meta)** | Handles holidays and flexible trend changes easily. | Heavy C++ binary dependencies (`pystan` / `cmdstanpy`), slow training, over-smooths localized inventory stockout shocks. | Rejected |
| **LSTM / GRU Neural Networks** | High capacity for complex sequence patterns. | Severely overfits on small/medium daily series (68 daily points); uninterpretable black box; requires GPU acceleration. | Rejected |

---

## 2. Leakage Prevention & Chronological Evaluation Integrity

In earlier iterations of Milestone 2, rolling features utilized centered rolling windows (`center=True`), which leaked future sales information into past feature rows. In Milestone 3, strict chronological isolation is enforced:

1. **Chronological Holdout Split:**
   - Transactions are strictly sorted by date.
   - **Training Set:** The earliest 80% of days (e.g. Days 1–54).
   - **Test Holdout Set:** The latest 20% of days (e.g. Days 55–68).
   - No randomized shuffling (`shuffle=False`).
2. **Backward-Looking Feature Engineering:**
   - Features include `day_of_week`, `day_of_month`, `month`, `is_weekend`, `lag_1_day`, `lag_7_days`, and an exponential moving average (`span=28`, strictly backward-looking).
   - Test rows are evaluated sequentially using only past knowledge.
3. **Evaluation Metric — Weighted Absolute Percentage Error (WAPE):**
   $$\text{WAPE} = \frac{\sum_{t} |y_t - \hat{y}_t|}{\sum_{t} y_t}$$
   $$\text{Accuracy \%} = \max(0, (1 - \text{WAPE}) \times 100)$$
   - On the real held-out test data, the model achieves **85.84% WAPE Accuracy**, exceeding the mentor's $\ge 80\%$ benchmark.

---

## 3. Customer Segmentation Methodology (RFM + K-Means)

- **Feature Space:** Normalized Recency, Frequency, and Monetary Value via `StandardScaler`.
- **Optimal Clusters:** $K=4$, sorted by spend to produce intuitive mentor-aligned tiers:
  1. **High Spenders:** Premium tier with highest spend and brand loyalty.
  2. **Frequent Buyers:** High order frequency and consistent repeat velocity.
  3. **Occasional Buyers:** Moderate velocity with recent purchasing.
  4. **Dormant Users:** Low volume and extended inactivity.
- **Segmentation Quality Metric:**
  $$\text{Quality \%} = \frac{\text{Normalized Silhouette} + \text{10-Seed ARI Stability}}{2} \times 100$$
  - Normalized Silhouette: $\frac{s + 1}{2} = \frac{0.552 + 1}{2} = 0.7760$ (77.6%)
  - Adjusted Rand Index (ARI) Stability across 10 random seeds: $0.9993$ (99.9%)
  - **Overall Segmentation Quality:** **88.76%**, exceeding the mentor's $\ge 85\%$ benchmark.

---

## 4. Collaborative Filtering Recommender Engine

- **Algorithm:** Item-based collaborative filtering computing cosine similarities over the User $\times$ Product co-occurrence matrix:
  $$\text{sim}(i, j) = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\| \|\mathbf{v}_j\|}$$
- **Cold-Start Fallback:** Automatically serves globally popular in-stock items when a customer has no purchase history.
- **Affinity Tiebreaker:** Customer's most-purchased category breaks ranking ties.
- **Offline Evaluation (Leave-Last-Purchase-Out):**
  - Hit-Rate@5 = $20.65\%$.
  - Random baseline = $\frac{5}{59} = 8.47\%$.
  - Lift over random = $\mathbf{2.44\times}$.
