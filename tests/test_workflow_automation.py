"""
ShopSense - Milestone 3 Module 9: Automated Workflow & Pipeline Testing
Target Metric: Workflow Success Rate = 100% (under normal operations)

Validates:
1. Manual and scheduled pipeline trigger execution.
2. Execution types: 'Manual' vs 'Scheduled'.
3. Three configured schedule policies with frequencies, last run, next run, status.
4. Non-generic operation summaries based on real DB/model results.
5. Execution history persistence across restarts.
6. Graceful failure handling and dynamic reliability rate computation.
"""

import os
import json
import pytest
from app.scheduler.scheduler_service import workflow_scheduler, HISTORY_FILE
from app.services import mlflow_service

def test_workflow_scheduler_pipeline_execution():
    # 1. Trigger automated retrain job manually
    retrain_res = workflow_scheduler.trigger_workflow_manually("retrain")
    assert retrain_res["status"] == "success"
    assert "retrain_demand_forecasting_model" in retrain_res["jobs_triggered"]

    # 2. Trigger automated analytics & reports job manually
    analytics_res = workflow_scheduler.trigger_workflow_manually("analytics")
    assert analytics_res["status"] == "success"
    assert "refresh_analytics_and_reports" in analytics_res["jobs_triggered"]

    # 3. Retrieve workflow status & audit history
    status_data = workflow_scheduler.get_workflow_status()
    assert status_data["scheduler_status"].upper() in ["RUNNING", "OPERATIONAL", "STOPPED"]
    assert status_data["total_jobs_executed"] >= 2

    # Verify execution history integrity
    history = status_data["execution_history"]
    assert len(history) >= 2
    for entry in history:
        assert entry["status"] in ["SUCCESS", "FAILURE"]
        assert entry["duration_seconds"] >= 0.0
        assert "timestamp" in entry
        assert entry["execution_type"] in ["Manual", "Scheduled"]
        assert len(entry["operation_summary"]) > 10
        # Ensure generic placeholder is replaced with real operation details
        assert entry["operation_summary"] != "Executed successfully"

    # 4. Verify MLflow Model Registry integration
    mlflow_status = mlflow_service.get_mlflow_status()
    assert mlflow_status["target_achieved"] is True
    assert mlflow_status["latest_metrics"]["accuracy_pct"] >= 80.0
    assert len(mlflow_status["registered_versions"]) >= 1

    print("\n--- AUTOMATED WORKFLOW VALIDATION REPORT ---")
    print(f"Workflow Status: {status_data['scheduler_status']}")
    print(f"Total Executed Jobs: {status_data['total_jobs_executed']}")
    print(f"Failed Jobs: {status_data['failed_jobs_count']}")
    print(f"Reliability Rate: {status_data['reliability_success_rate']}%")

def test_schedule_policies_configuration():
    """Verify that all three mentor-mandated schedule policies are configured."""
    status_data = workflow_scheduler.get_workflow_status()
    policies = status_data.get("schedule_policies", [])
    assert len(policies) == 3

    policy_ids = [p["job_id"] for p in policies]
    assert "retrain_forecasting_job" in policy_ids
    assert "daily_cron_retrain_job" in policy_ids
    assert "refresh_analytics_job" in policy_ids

    for p in policies:
        assert p["job_name"] is not None
        assert p["frequency"] is not None
        assert p["last_run"] is not None
        assert p["next_run"] is not None
        assert p["status"] in ["ACTIVE", "PAUSED", "SCHEDULED"]

def test_scheduled_vs_manual_execution_and_failure_handling():
    """Test manual and scheduled execution separately, including failed-job handling."""
    # 1. Scheduled Execution test
    scheduled_res = workflow_scheduler._execute_retrain_job(trigger_type="Scheduled")
    assert scheduled_res["status"] == "SUCCESS"
    assert scheduled_res["event"]["execution_type"] == "Scheduled"
    assert "Accuracy:" in scheduled_res["summary"]

    # 2. Manual Execution test
    manual_res = workflow_scheduler._execute_analytics_refresh_job(trigger_type="Manual")
    assert manual_res["status"] == "SUCCESS"
    assert manual_res["event"]["execution_type"] == "Manual"
    assert "Consolidated" in manual_res["summary"]

    # 3. Failed-Job Handling test
    before_status = workflow_scheduler.get_workflow_status()
    before_failed = before_status["failed_jobs_count"]
    before_total = before_status["total_jobs_executed"]

    fail_res = workflow_scheduler.simulate_failed_job(
        job_name="Payment Gateway Reconciliation",
        error_msg="Connection timeout during bank sync",
        trigger_type="Manual"
    )
    assert fail_res["status"] == "FAILURE"
    assert fail_res["event"]["execution_type"] == "Manual"
    assert "failed" in fail_res["summary"].lower()

    after_status = workflow_scheduler.get_workflow_status()
    assert after_status["failed_jobs_count"] == before_failed + 1
    assert after_status["total_jobs_executed"] == before_total + 1
    assert after_status["reliability_success_rate"] < 100.0 or before_total == 0

    # 4. Recovery: Subsequent successful execution brings reliability back up
    rec_res = workflow_scheduler._execute_analytics_refresh_job(trigger_type="Scheduled")
    assert rec_res["status"] == "SUCCESS"
    recovered_status = workflow_scheduler.get_workflow_status()
    assert recovered_status["reliability_success_rate"] > after_status["reliability_success_rate"]

    # Clean up simulated test failure so production state returns to 100% operational
    workflow_scheduler.execution_history = [
        e for e in workflow_scheduler.execution_history
        if e.get("job_id") != "simulated_failure_job"
    ]
    workflow_scheduler._save_history()

def test_scheduler_persistence():
    """Verify that execution records are persisted and reloadable across restarts."""
    assert os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "execution_history" in data
        assert "policy_last_runs" in data
        assert len(data["execution_history"]) > 0

    # Test loading into a new manager instance simulation
    hist = data["execution_history"]
    assert hist[0]["job_name"] is not None
    assert hist[0]["execution_type"] in ["Manual", "Scheduled"]
