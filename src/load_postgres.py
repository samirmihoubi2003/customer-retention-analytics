"""Load generated CSV files into PostgreSQL, replacing tables for a repeatable local demo."""
import argparse
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

FILES = ["clean_sales", "orders", "rfm_segments", "cohort_retention", "monthly_kpis"]


def main():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit(
            "Define DATABASE_URL, e.g. postgresql+psycopg2://retail:retail@localhost:5434/retail"
        )
    engine = create_engine(url)
    for name in FILES:
        path = Path("data/processed") / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        df = pd.read_csv(path)
        if name in ("clean_sales", "orders"):
            df["invoice_date"] = pd.to_datetime(df["invoice_date"])
        df.to_sql(
            name,
            engine,
            if_exists="replace",
            index=False,
            chunksize=10000,
            method="multi",
        )
        print(f"{name}: {len(df)} rows")
    engine.dispose()


if __name__ == "__main__":
    main()
parser = argparse.ArgumentParser()
parser.add_argument("--input", ...)
parser.add_argument("--output", ...)
args = parser.parse_args()
run(args.input, args.output)
