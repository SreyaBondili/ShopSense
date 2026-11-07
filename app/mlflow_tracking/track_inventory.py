import os
import mlflow
from app.database import get_db
from app.services.mlflow_service import train_and_log_inventory_model

def run_tracking():
    """
    Mentor Module 3: MLflow Model Registry script.
    Executes training and registers InventoryForecast.
    """
    db = next(get_db())
    result = train_and_log_inventory_model(db, run_notes="Stand-alone track_inventory execution")
    print("=" * 60)
    print("MLFLOW TRACKING COMPLETE")
    print(f"Run ID: {result['run_id']}")
    print(f"Registered Model: {result['registered_model']}")
    print(f"Accuracy: {result['metrics']['accuracy_pct']}%")
    print(f"MAE: {result['metrics']['mae']} units")
    print(f"Target >= 80% Achieved: {result['metrics']['target_achieved']}")
    print("=" * 60)
    return result

if __name__ == "__main__":
    run_tracking()
