# Performance Tests

This directory contains Milestone 3 Task 4 performance testing infrastructure.

## Files

| File | Purpose |
|------|---------|
| `locustfile.py` | Locust load test: 50 concurrent users, analytics endpoints |
| `test_api_performance.py` | Pytest-based p95 latency test, 20 iterations per endpoint |

## Running the Locust Headless Test

**Requires the FastAPI server to be running first:**

```bash
# Terminal 1: Start the server
cd ShopSense
.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Run Locust headless
.venv\Scripts\locust -f tests/performance/locustfile.py \
    --headless -u 50 -r 10 -t 60s \
    --csv docs/evidence/locust_stats \
    --host http://localhost:8000
```

Results are saved to `docs/evidence/locust_stats_stats.csv`.

## Running the Pytest Performance Test

The pytest test uses FastAPI's TestClient (no live server needed):

```bash
cd ShopSense
.venv\Scripts\pytest tests/performance/test_api_performance.py -v -s
```

Output includes avg, p95, max per endpoint and writes:
- `docs/evidence/performance_report.md`
- `docs/evidence/performance_report.json`

## Target Criteria

| Endpoint Type | p95 Target |
|---------------|-----------|
| Analytics / ML / Scheduler | ≤ 300 ms |
| PDF / Excel Reports | ≤ 3000 ms |
