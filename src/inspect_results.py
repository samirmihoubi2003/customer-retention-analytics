"""Display customer analytics results from generated CSV files."""

from pathlib import Path
import pandas as pd

BASE = Path("data/processed")


def main():
    orders = pd.read_csv(BASE / "orders.csv")
    monthly = pd.read_csv(BASE / "monthly_kpis.csv")
    rfm = pd.read_csv(BASE / "rfm_segments.csv")
    cohort = pd.read_csv(BASE / "cohort_retention.csv")

    print("\n=== GLOBAL KPIs ===")
    print("Total Orders:", orders["invoice"].nunique())
    print("Unique Customers:", orders["customer_id"].nunique())
    print("Total Sales (GBP):", round(orders["revenue"].sum(), 2))
    print("Average Order Value (GBP):", round(orders["revenue"].sum() / len(orders), 2))

    print("\n=== LAST 5 MONTHS ===")
    print(monthly.tail(5).to_string(index=False))

    print("\n=== RFM CUSTOMER SEGMENTS ===")
    segments = rfm.groupby("segment").agg(
        customers=("customer_id", "nunique"), sales_gbp=("monetary", "sum")
    )
    print(segments.round(2).to_string())

    print("\n=== COHORT RETENTION SAMPLE ===")
    print(cohort.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
