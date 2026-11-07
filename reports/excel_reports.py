import pandas as pd
import os

def generate_excel_report(output_filename: str = "RevenueReport.xlsx"):
    """
    Mentor Module 6: Excel Report Export reference function.
    """
    CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "transactions.csv")
    if os.path.exists(CSV_PATH):
        report = pd.read_csv(CSV_PATH)
    else:
        from app.database import engine
        report = pd.read_sql("SELECT * FROM transactions", engine)

    report.to_excel(output_filename, index=False)
    print(f"Generated {output_filename} with {len(report)} records")

if __name__ == "__main__":
    generate_excel_report()
