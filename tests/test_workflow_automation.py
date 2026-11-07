"""
ShopSense - Milestone 3 Module 9: Automated Workflow & Pipeline Testing
Target Metric: Workflow Success Rate = 100%

Validates:
1. Manual and scheduled pipeline trigger execution.
2. Step tracking: extraction, model retraining, MLflow logging, report generation.
3. Zero job failures across automated runs.
4. Execution time recording per step.
"""

import pytest
from app.scheduler.scheduler_service import workflow_scheduler
from app.services import mlflow_service
from app.database import SessionLocal

def test_workflow_scheduler_pipeline_execution():
    # 1. Trigger automated retrain job
    retrain_res = workflow_scheduler.trigger_workflow_manually("retrain")
    assert retrain_res["status"] == "success"
    assert "retrain_demand_forecasting_model" in retrain_res["jobs_triggered"]

    # 2. Trigger automated analytics & reports job
    analytics_res = workflow_scheduler.trigger_workflow_manually("analytics")
    assert analytics_res["status"] == "success"
    assert "refresh_analytics_and_reports" in analytics_res["jobs_triggered"]

    # 3. Retrieve workflow status & audit history
    status_data = workflow_scheduler.get_workflow_status()
    assert status_data["scheduler_status"].upper() in ["RUNNING", "OPERATIONAL", "STOPPED"]
    assert status_data["reliability_success_rate"] == 100.0
    assert status_data["failed_jobs_count"] == 0
    assert status_data["total_jobs_executed"] >= 2

    # Verify execution history integrity
    history = status_data["execution_history"]
    assert len(history) >= 2
    for entry in history:
        assert entry["status"] == "SUCCESS"
        assert entry["duration_seconds"] >= 0.0
        assert "timestamp" in entry

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
