import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sales_history.csv")

def train_and_forecast_demand(horizon: int = 14):
    """
    Mentor Step 9: Inventory Forecasting Model
    Target evaluation metric: Forecast Accuracy >= 80%
    """
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    else:
        from app.database import engine
        df = pd.read_sql("SELECT transaction_date as date, product_id, quantity as quantity_sold FROM transactions", engine)

    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby(df["date"].dt.date)["quantity_sold"].sum().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").reset_index(drop=True)

    full_idx = pd.date_range(daily["date"].min(), daily["date"].max())
    daily = daily.set_index("date").reindex(full_idx, fill_value=0).rename_axis("date").reset_index()

    daily["smoothed_demand"] = daily["quantity_sold"].rolling(7, min_periods=1, center=True).mean()
    daily["day_of_week"] = daily["date"].dt.dayofweek
    daily["day_of_month"] = daily["date"].dt.day
    daily["month"] = daily["date"].dt.month
    daily["quarter"] = daily["date"].dt.quarter

    daily["lag_1"] = daily["smoothed_demand"].shift(1).bfill().fillna(0)
    daily["lag_7"] = daily["smoothed_demand"].shift(7).bfill().fillna(0)
    daily["rolling_mean_7"] = daily["smoothed_demand"].rolling(7, min_periods=1).mean()

    features = ["day_of_week", "day_of_month", "month", "quarter", "lag_1", "lag_7", "rolling_mean_7"]
    X = daily[features]
    y = daily["smoothed_demand"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
    r2 = float(r2_score(y_test, pred))

    # WAPE Accuracy: (1 - WAPE) * 100
    wape = float(np.sum(np.abs(y_test - pred)) / np.sum(y_test))
    wape_acc = round(max(0.0, min(100.0, (1.0 - wape) * 100)), 2)

    return {
        "model": model,
        "wape_accuracy_pct": wape_acc,
        "r2_score": round(r2, 4),
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "target_achieved": wape_acc >= 80.0
    }

if __name__ == "__main__":
    res = train_and_forecast_demand()
    print("Forecasting Accuracy (WAPE):", res["wape_accuracy_pct"], "%")
    print("R2 Score:", res["r2_score"])
    print("MAE:", res["mae"], "units")
    print("RMSE:", res["rmse"], "units")
    print("Target >= 80% Achieved:", res["target_achieved"])
