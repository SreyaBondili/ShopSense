"""
API Performance Test Suite — ShopSense Milestone 3, Task 4.
Uses time.perf_counter to measure response times per endpoint.
Runs against the live FastAPI server via TestClient (no network needed).

Target: p95 <= 300 ms for analytics endpoints.
PDF/Excel report endpoints get a separate 3000 ms limit (I/O-heavy).
"""
import time
import statistics
import json
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app

client = TestClient(app, raise_server_exceptions=False)

ADMIN_EMAIL = "admin@shopsense.com"
ADMIN_PASSWORD = "Admin@123"
PERF_ITERATIONS = 20          # Requests per endpoint for the pytest-based test
P95_TARGET_MS = 300           # ms — analytics endpoints
REPORT_TARGET_MS = 3000       # ms — PDF/Excel endpoints (I/O heavy)

# ─── Helpers ────────────────────────────────────────────────────────────────

def login_admin() -> str:
    for path in ["/api/auth/login", "/auth/login"]:
        resp = client.post(path, json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        if resp.status_code == 200:
            return resp.json().get("access_token", "")
    return ""


def measure_endpoint(method: str, url: str, headers: dict, iterations: int = PERF_ITERATIONS) -> dict:
    """Measure response times for an endpoint and return stats."""
    times_ms = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        if method.upper() == "GET":
            resp = client.get(url, headers=headers)
        else:
            resp = client.request(method, url, headers=headers)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        times_ms.append(elapsed_ms)

    avg = statistics.mean(times_ms)
    p95 = sorted(times_ms)[int(len(times_ms) * 0.95) - 1]
    max_t = max(times_ms)

    return {
        "url": url,
        "iterations": iterations,
        "avg_ms": round(avg, 2),
        "p95_ms": round(p95, 2),
        "max_ms": round(max_t, 2),
        "times_ms": [round(t, 2) for t in times_ms],
    }


def print_result(label: str, stats: dict, target_ms: int):
    passed = stats["p95_ms"] <= target_ms
    status = "PASS" if passed else "FAIL"
    print(
        f"\n  [{status}] {label}\n"
        f"    avg={stats['avg_ms']:.1f}ms  p95={stats['p95_ms']:.1f}ms  max={stats['max_ms']:.1f}ms  "
        f"(target p95 <= {target_ms}ms)"
    )
    return passed


# ─── Test Class ─────────────────────────────────────────────────────────────

class TestAPIPerformance:
    """One test function per endpoint; all share the same admin token."""

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, request):
        """Login once per class and store results for the final report."""
        token = login_admin()
        request.cls.headers = {"Authorization": f"Bearer {token}"}
        request.cls.results = []
        yield
        # Write JSON + markdown report after all tests in class finish
        _write_report(request.cls.results)

    def _run(self, label: str, url: str, target_ms: int = P95_TARGET_MS):
        stats = measure_endpoint("GET", url, self.headers)
        passed = print_result(label, stats, target_ms)
        self.results.append({**stats, "label": label, "target_ms": target_ms, "passed": passed})
        assert passed, (
            f"p95 latency {stats['p95_ms']:.1f}ms exceeds {target_ms}ms target for {url}"
        )

    def test_01_analytics_revenue(self):
        self._run("GET /api/analytics/revenue", "/api/analytics/revenue")

    def test_02_analytics_vendor_performance(self):
        self._run("GET /api/analytics/vendor-performance", "/api/analytics/vendor-performance")

    def test_03_analytics_customers(self):
        self._run("GET /api/analytics/customers", "/api/analytics/customers")

    def test_04_forecast_month(self):
        self._run("GET /api/forecast/11", "/api/forecast/11")

    def test_05_recommend_user(self):
        self._run("GET /api/recommend/1", "/api/recommend/1")

    def test_06_scheduler_status(self):
        self._run("GET /api/scheduler/status", "/api/scheduler/status")

    def test_07_mlflow_status(self):
        self._run("GET /api/analytics/mlflow-status", "/api/analytics/mlflow-status")

    def test_08_pdf_report(self):
        """PDF report endpoint: higher latency target (I/O heavy)."""
        self._run(
            "GET /api/reports/revenue (PDF)",
            "/api/reports/revenue?format=pdf",
            target_ms=REPORT_TARGET_MS,
        )

    def test_09_excel_report(self):
        """Excel report endpoint: higher latency target (I/O heavy)."""
        self._run(
            "GET /api/reports/revenue (Excel)",
            "/api/reports/revenue?format=excel",
            target_ms=REPORT_TARGET_MS,
        )


# ─── Report Writer ──────────────────────────────────────────────────────────

def _write_report(results: list):
    os.makedirs("docs/evidence", exist_ok=True)

    # JSON
    with open("docs/evidence/performance_report.json", "w") as f:
        json.dump({"results": results, "p95_target_ms": P95_TARGET_MS}, f, indent=2)

    # Markdown
    all_pass = all(r["passed"] for r in results)
    with open("docs/evidence/performance_report.md", "w", encoding="utf-8") as f:
        f.write("# ShopSense API Performance Report — Milestone 3 Task 4\n\n")
        f.write(f"**Target:** p95 <= {P95_TARGET_MS} ms (analytics), <= {REPORT_TARGET_MS} ms (PDF/Excel)  \n")
        f.write(f"**Iterations per endpoint:** {PERF_ITERATIONS}  \n")
        f.write(f"**Overall result:** {'ALL PASS' if all_pass else 'SOME FAILURES'}  \n\n")
        f.write("| Endpoint | Avg (ms) | p95 (ms) | Max (ms) | Target (ms) | Result |\n")
        f.write("|----------|----------|----------|----------|-------------|--------|\n")
        for r in results:
            icon = "PASS" if r["passed"] else "FAIL"
            f.write(
                f"| {r['label']} | {r['avg_ms']} | {r['p95_ms']} | {r['max_ms']} | {r['target_ms']} | {icon} |\n"
            )
        f.write("\n> **Note:** TestClient measurements reflect single-threaded latency ")
        f.write("within the test process. Locust headless results (50 concurrent users, 60 s) ")
        f.write("are saved separately in `docs/evidence/locust_stats_stats.csv`.\n")

    print("\nPerformance report written to docs/evidence/performance_report.md")
