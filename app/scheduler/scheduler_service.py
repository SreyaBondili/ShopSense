import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

class WorkflowSchedulerManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorkflowSchedulerManager, cls).__new__(cls)
            cls._instance.scheduler = BackgroundScheduler(daemon=True)
            cls._instance.is_running = False
            cls._instance.execution_history = []
            cls._instance.stats = {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "last_run_time": None,
                "last_job_name": None,
                "next_run_time": None
            }
        return cls._instance

    def _execute_retrain_job(self):
        start_t = time.time()
        job_name = "Retrain_Inventory_Forecasting_MLflow"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            from app.database import get_db
            from app.services.mlflow_service import train_and_log_inventory_model
            db = next(get_db())
            res = train_and_log_inventory_model(db, run_notes="Scheduled Retrain Job (APScheduler)")

            duration = round(time.time() - start_t, 2)
            self.stats["total_runs"] += 1
            self.stats["successful_runs"] += 1
            self.stats["last_run_time"] = timestamp
            self.stats["last_job_name"] = job_name

            event = {
                "run_id": self.stats["total_runs"],
                "timestamp": timestamp,
                "job_name": job_name,
                "status": "SUCCESS",
                "duration_seconds": duration,
                "details": f"Model retrained and registered. Accuracy: {res['metrics']['accuracy_pct']}%, MAE: {res['metrics']['mae']}"
            }
            self.execution_history.insert(0, event)
            if len(self.execution_history) > 30:
                self.execution_history.pop()

        except Exception as e:
            duration = round(time.time() - start_t, 2)
            self.stats["total_runs"] += 1
            self.stats["failed_runs"] += 1
            self.stats["last_run_time"] = timestamp
            self.stats["last_job_name"] = job_name

            event = {
                "run_id": self.stats["total_runs"],
                "timestamp": timestamp,
                "job_name": job_name,
                "status": "FAILURE",
                "duration_seconds": duration,
                "details": str(e)
            }
            self.execution_history.insert(0, event)

    def _execute_analytics_refresh_job(self):
        start_t = time.time()
        job_name = "Refresh_Marketplace_Analytics"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            from app.database import get_db
            from app.services.replenishment_service import get_inventory_turnover
            from app.models.user import User, UserRole
            db = next(get_db())
            admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
            if admin:
                get_inventory_turnover(db, admin)

            duration = round(time.time() - start_t, 2)
            self.stats["total_runs"] += 1
            self.stats["successful_runs"] += 1
            self.stats["last_run_time"] = timestamp
            self.stats["last_job_name"] = job_name

            event = {
                "run_id": self.stats["total_runs"],
                "timestamp": timestamp,
                "job_name": job_name,
                "status": "SUCCESS",
                "duration_seconds": duration,
                "details": "Refreshed turnover analytics, COGS valuation, and alerts."
            }
            self.execution_history.insert(0, event)
            if len(self.execution_history) > 30:
                self.execution_history.pop()

        except Exception as e:
            duration = round(time.time() - start_t, 2)
            self.stats["total_runs"] += 1
            self.stats["failed_runs"] += 1
            self.stats["last_run_time"] = timestamp
            self.stats["last_job_name"] = job_name

            event = {
                "run_id": self.stats["total_runs"],
                "timestamp": timestamp,
                "job_name": job_name,
                "status": "FAILURE",
                "duration_seconds": duration,
                "details": str(e)
            }
            self.execution_history.insert(0, event)

    def start_scheduler(self, interval_hours: int = 2):
        """Start the background scheduler with configured interval and cron schedules."""
        if not self.is_running:
            # 1. Periodic retraining every interval_hours (Mentor: every 2 hours)
            self.scheduler.add_job(
                self._execute_retrain_job,
                trigger=IntervalTrigger(hours=interval_hours),
                id="retrain_forecasting_job",
                name="Inventory Demand Retrain Pipeline",
                replace_existing=True
            )

            # 2. Daily Cron at 02:00 AM (Mentor: daily cron hour=2)
            self.scheduler.add_job(
                self._execute_retrain_job,
                trigger=CronTrigger(hour=2, minute=0),
                id="daily_cron_retrain_job",
                name="Daily Scheduled Model Refresh (02:00 AM)",
                replace_existing=True
            )

            # 3. Analytics cache refresh every 30 minutes
            self.scheduler.add_job(
                self._execute_analytics_refresh_job,
                trigger=IntervalTrigger(minutes=30),
                id="refresh_analytics_job",
                name="Marketplace Analytics Refresh",
                replace_existing=True
            )

            self.scheduler.start()
            self.is_running = True

            # Perform an initial execution to establish baseline reliability
            if self.stats["total_runs"] == 0:
                self._execute_retrain_job()
                self._execute_analytics_refresh_job()

    def trigger_workflow_manually(self, job_type: str = "all") -> Dict[str, Any]:
        """Manually trigger workflow jobs for live demo and evaluation."""
        triggered = []
        if job_type in ["retrain", "all"]:
            self._execute_retrain_job()
            triggered.append("retrain_demand_forecasting_model")
        if job_type in ["analytics", "all"]:
            self._execute_analytics_refresh_job()
            triggered.append("refresh_analytics_and_reports")

        status_info = self.get_workflow_status()
        status_info["status"] = "success"
        status_info["jobs_triggered"] = triggered
        status_info["message"] = f"Triggered jobs: {', '.join(triggered)}"
        return status_info

    def get_workflow_status(self) -> Dict[str, Any]:
        """Compute workflow metrics and return execution history."""
        total = self.stats["total_runs"]
        success = self.stats["successful_runs"]
        failed = self.stats["failed_runs"]

        # Mentor Evaluation Metric: Workflow Success Rate = (success / total) * 100
        reliability_pct = round((success / total) * 100.0, 2) if total > 0 else 100.0
        target_achieved = (reliability_pct == 100.0) and (total > 0)

        # Get next scheduled run time
        next_run = None
        jobs = []
        scheduled_jobs = []
        if self.is_running:
            for j in self.scheduler.get_jobs():
                nxt = j.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if j.next_run_time else None
                jobs.append({
                    "id": j.id,
                    "name": j.name,
                    "next_run_time": nxt
                })
                scheduled_jobs.append({
                    "id": j.id,
                    "name": j.name,
                    "trigger": str(j.trigger),
                    "next_run_time": nxt
                })
                if nxt and (next_run is None or nxt < next_run):
                    next_run = nxt

        return {
            "status": "success",
            "scheduler_status": "RUNNING" if self.is_running else "STOPPED",
            "is_running": self.is_running,
            "configured_interval": "Every 2 Hours + Daily 02:00 AM Cron",
            "reliability_pct": reliability_pct,
            "reliability_success_rate": reliability_pct,
            "target_threshold": 100.0,
            "target_achieved": target_achieved,
            "total_jobs_executed": total,
            "failed_jobs_count": failed,
            "stats": {
                "total_runs": total,
                "successful_runs": success,
                "failed_runs": failed,
                "last_run_time": self.stats["last_run_time"],
                "next_run_time": next_run
            },
            "active_jobs": jobs,
            "scheduled_jobs": scheduled_jobs,
            "history": self.execution_history[:15],
            "execution_history": self.execution_history[:15]
        }

workflow_scheduler = WorkflowSchedulerManager()
