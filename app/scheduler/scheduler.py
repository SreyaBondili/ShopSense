from apscheduler.schedulers.blocking import BlockingScheduler
from app.database import get_db
from app.services.mlflow_service import train_and_log_inventory_model

def retrain_model():
    """Mentor Step 4: Daily Forecast Update"""
    print("Retraining Model and logging to MLflow...")
    db = next(get_db())
    res = train_and_log_inventory_model(db, run_notes="Mentor scheduler.py standalone run")
    print(f"Model retrained. Accuracy: {res['metrics']['accuracy_pct']}%, MAE: {res['metrics']['mae']}")

def start_stand_alone_scheduler():
    scheduler = BlockingScheduler()
    # Mentor: scheduler.add_job(retrain_model, 'cron', hour=2)
    scheduler.add_job(retrain_model, 'cron', hour=2)
    print("Standalone scheduler initialized for daily retrain at 02:00 AM.")
    return scheduler

if __name__ == "__main__":
    retrain_model()
