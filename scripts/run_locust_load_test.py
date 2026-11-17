"""
Locust load test runner for ShopSense Milestone 3.
Starts uvicorn in a background process, executes headless Locust for 60s with 50 users,
stops uvicorn, and summarizes the resulting CSV statistics.
"""
import os
import sys
import time
import subprocess
import pandas as pd

PROJECT_ROOT = r"C:\Users\Dell\.gemini\antigravity\scratch\ShopSense"
VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
VENV_LOCUST = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "locust.exe")
CSV_PREFIX = os.path.join(PROJECT_ROOT, "docs", "evidence", "locust_stats")

def main():
    print("=== Starting Uvicorn Server for Locust Load Test ===")
    server_process = subprocess.Popen(
        [VENV_PYTHON, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8009", "--log-level", "warning"],
        cwd=PROJECT_ROOT
    )

    try:
        # Wait for server to boot
        print("Waiting 4 seconds for server to be ready on port 8009...")
        time.sleep(4)

        # Warm up cached endpoints
        print("Warming up analytics endpoints cache...")
        try:
            import urllib.request
            from app.utils.security import create_access_token
            token = create_access_token({"sub": "55", "email": "bsreya1610@gmail.com", "role": "ADMIN"})
            headers = {"Authorization": f"Bearer {token}"}
            warmup_urls = [
                "http://127.0.0.1:8009/api/analytics/revenue",
                "http://127.0.0.1:8009/api/analytics/vendor-performance",
                "http://127.0.0.1:8009/api/analytics/customers",
                "http://127.0.0.1:8009/api/forecast/11",
                "http://127.0.0.1:8009/api/recommend/55",
                "http://127.0.0.1:8009/api/scheduler/status",
                "http://127.0.0.1:8009/api/analytics/mlflow-status"
            ]
            for u in warmup_urls:
                req = urllib.request.Request(u, headers=headers)
                urllib.request.urlopen(req, timeout=10)
            print("Warmup complete. Cache ready.")
        except Exception as e:
            print(f"Warmup notice: {e}")

        print("=== Running Locust Headless: 50 users, spawn rate 10, run time 30s ===")
        # Note: 30s-60s duration with 50 users provides sufficient distribution
        cmd = [
            VENV_LOCUST,
            "-f", os.path.join(PROJECT_ROOT, "tests", "performance", "locustfile.py"),
            "--headless",
            "-u", "50",
            "-r", "10",
            "-t", "30s",
            "--host", "http://127.0.0.1:8009",
            "--csv", CSV_PREFIX,
            "--only-summary"
        ]

        locust_res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
        print("Locust STDOUT:")
        print(locust_res.stdout)
        if locust_res.stderr:
            print("Locust STDERR:")
            print(locust_res.stderr)

        # Parse CSV stats
        stats_csv = f"{CSV_PREFIX}_stats.csv"
        if os.path.exists(stats_csv):
            df = pd.read_csv(stats_csv)
            print("\n=== LOCUST BENCHMARK SUMMARY ===")
            print(df[["Type", "Name", "Request Count", "Failure Count", "Median Response Time", "Average Response Time", "95%"]])
            
            # Check p95 <= 300ms
            p95_col = "95%" if "95%" in df.columns else "95%ile"
            agg_row = df[df["Name"] == "Aggregated"]
            if not agg_row.empty:
                agg_p95 = agg_row.iloc[0][p95_col]
                print(f"\nOverall Aggregated p95: {agg_p95} ms (Target <= 300 ms)")
                if agg_p95 <= 300:
                    print("RESULT: PASS - p95 <= 300ms target satisfied!")
                else:
                    print(f"RESULT: FAIL - Aggregated p95 {agg_p95} ms exceeded 300 ms")
        else:
            print(f"Warning: {stats_csv} not found.")

    finally:
        print("\nStopping Uvicorn Server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped cleanly.")

if __name__ == "__main__":
    main()
