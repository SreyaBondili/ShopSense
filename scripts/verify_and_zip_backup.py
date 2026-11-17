import os
import shutil

backup_dir = r"D:\ShopSense_Backup\ShopSense_Project_Backup_20261115_201500"
zip_path = r"D:\ShopSense_Backup\ShopSense_Project_Backup_20261115_201500.zip"

required_items = [
    "app/main.py",
    "app/models/user.py",
    "app/models/vendor.py",
    "app/models/product.py",
    "app/models/transaction.py",
    "app/services/auth_service.py",
    "app/services/forecasting_service.py",
    "app/services/recommendation_service.py",
    "frontend/package.json",
    "frontend/src/pages/LoginPage.jsx",
    "frontend/src/pages/VendorsPage.jsx",
    "frontend/dist/index.html",
    "dashboard/dashboard.py",
    "mlflow_data/mlflow.db",
    "requirements.txt",
    ".env",
    "tests/test_auth.py",
    "tests/test_rbac.py",
    "tests/performance/test_api_performance.py",
    "scripts/migrate_m3_fields.py"
]

print("VERIFYING BACKUP FILES IN FOLDER:")
missing = []
for item in required_items:
    full_p = os.path.join(backup_dir, item.replace("/", os.sep))
    exists = os.path.exists(full_p)
    size = os.path.getsize(full_p) if exists else 0
    status = "OK" if exists else "MISSING"
    print(f"  [{status}] {item:40} ({size} bytes)")
    if not exists:
        missing.append(item)

assert len(missing) == 0, f"Missing items: {missing}"
print("All key project backup files verified successfully.")

print(f"Creating compressed ZIP archive at {zip_path}...")
base_name = zip_path.replace(".zip", "")
shutil.make_archive(base_name, "zip", backup_dir)
zip_size = os.path.getsize(zip_path)
print(f"ZIP created successfully: {zip_path} ({zip_size / 1024 / 1024:.2f} MB)")
