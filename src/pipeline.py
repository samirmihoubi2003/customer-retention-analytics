"""ETL + customer analytics for UCI Online Retail II."""

from pathlib import Path
import argparse
import json
import pandas as pd

REQUIRED = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]


# 1. Read original Excel file
def read_source(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return pd.concat(pd.read_excel(path, sheet_name=None).values(), ignore_index=True)


# 2. Clean raw data
def clean_orders(raw: pd.DataFrame):
    """Return cleaned positive sales and a data quality report."""

    missing_cols = set(REQUIRED) - set(raw.columns)

    if missing_cols:
        raise ValueError(f"Missing columns: {sorted(missing_cols)}")

    df = raw[REQUIRED].copy()

    report = {
        "input_rows": len(df),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "missing_customer_rows": int(df["Customer ID"].isna().sum()),
    }

    # Remove exact duplicate rows
    df = df.drop_duplicates().copy()
    report["after_dedup_rows"] = len(df)

    # Remove cancelled invoices
    canceled = df["Invoice"].astype("string").str.upper().str.startswith("C", na=False)

    report["cancellation_rows"] = int(canceled.sum())
    df = df.loc[~canceled].copy()

    # Convert data types
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    # Keep valid identified customer purchases
    valid = (
        df["Customer ID"].notna()
        & df["InvoiceDate"].notna()
        & df["Quantity"].gt(0)
        & df["Price"].gt(0)
    )

    report["invalid_or_anonymous_rows_after_cancellations"] = int((~valid).sum())

    df = df.loc[valid].copy()

    # Standardize column names and types
    df["customer_id"] = df["Customer ID"].astype("int64").astype(str)

    df["invoice"] = df["Invoice"].astype(str)
    df["stock_code"] = df["StockCode"].astype(str)

    df["description"] = df["Description"].fillna("").astype(str)

    df["country"] = df["Country"].astype(str)
    df["quantity"] = df["Quantity"].astype("int64")
    df["unit_price"] = df["Price"].astype(float)
    df["invoice_date"] = df["InvoiceDate"]

    # Calculate revenue for each sales line
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)

    df = df[
        [
            "invoice",
            "stock_code",
            "description",
            "quantity",
            "invoice_date",
            "unit_price",
            "customer_id",
            "country",
            "revenue",
        ]
    ]

    report["clean_rows"] = len(df)

    report["definition"] = (
        "Identified customers, positive sales only, "
        "cancellations excluded; gross positive-line sales, "
        "not net accounting revenue."
    )

    return df, report


# 3. Create invoice-level table
def invoice_table(lines: pd.DataFrame) -> pd.DataFrame:

    return lines.groupby(["customer_id", "invoice"], as_index=False).agg(
        invoice_date=("invoice_date", "min"),
        revenue=("revenue", "sum"),
        country=("country", "first"),
    )


# 4. RFM customer segmentation
def make_rfm(orders: pd.DataFrame, reference_date=None) -> pd.DataFrame:

    if orders.empty:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "recency_days",
                "frequency",
                "monetary",
                "r_score",
                "f_score",
                "m_score",
                "segment",
            ]
        )

    # Reference date - corrected version
    if reference_date is not None:
        ref = pd.Timestamp(reference_date)
    else:
        last_date = pd.Timestamp(orders["invoice_date"].max())
        ref = last_date.normalize() + pd.DateOffset(days=1)

    rfm = orders.groupby("customer_id", as_index=False).agg(
        last_purchase=("invoice_date", "max"),
        frequency=("invoice", "nunique"),
        monetary=("revenue", "sum"),
    )

    # Calculate Recency
    rfm["recency_days"] = (ref - rfm["last_purchase"]).dt.days

    # Calculate RFM scores
    for col, score, ascending in [
        ("recency_days", "r_score", False),
        ("frequency", "f_score", True),
        ("monetary", "m_score", True),
    ]:

        ranks = rfm[col].rank(method="first", ascending=True)

        quintiles = (
            pd.cut(ranks, bins=5, labels=False, include_lowest=True).astype(int) + 1
        )

        if col == "recency_days":
            rfm[score] = 6 - quintiles
        else:
            rfm[score] = quintiles

    # Assign customer segments
    def segment(row):

        if row.r_score >= 4 and row.f_score >= 4:
            return "Champions"

        if row.r_score <= 2 and row.f_score >= 4:
            return "At Risk"

        if row.r_score >= 4 and row.f_score <= 2:
            return "New / Promising"

        if row.r_score <= 2 and row.f_score <= 2:
            return "Hibernating"

        return "Regular"

    rfm["segment"] = rfm.apply(segment, axis=1)

    return rfm.drop(columns="last_purchase")


# 5. Cohort retention analysis
def cohort_retention(orders: pd.DataFrame) -> pd.DataFrame:

    if orders.empty:
        return pd.DataFrame(
            columns=[
                "cohort_month",
                "period_number",
                "active_customers",
                "cohort_size",
                "retention_rate",
            ]
        )

    activity = orders[["customer_id", "invoice_date"]].copy()

    activity["order_month"] = activity["invoice_date"].dt.to_period("M")

    activity = activity.drop_duplicates(["customer_id", "order_month"])

    first = activity.groupby("customer_id")["order_month"].min().rename("cohort_month")

    activity = activity.join(first, on="customer_id")

    activity["period_number"] = (
        (activity["order_month"].dt.year - activity["cohort_month"].dt.year) * 12
        + activity["order_month"].dt.month
        - activity["cohort_month"].dt.month
    )

    out = (
        activity.groupby(["cohort_month", "period_number"], as_index=False)[
            "customer_id"
        ]
        .nunique()
        .rename(columns={"customer_id": "active_customers"})
    )

    sizes = out.loc[
        out.period_number.eq(0), ["cohort_month", "active_customers"]
    ].rename(columns={"active_customers": "cohort_size"})

    out = out.merge(sizes, on="cohort_month", validate="many_to_one")

    out["retention_rate"] = (out.active_customers / out.cohort_size).round(4)

    out["cohort_month"] = out["cohort_month"].astype(str)

    return out


# 6. Monthly business KPIs
def monthly_kpis(orders: pd.DataFrame) -> pd.DataFrame:

    if orders.empty:
        return pd.DataFrame(
            columns=[
                "month",
                "orders",
                "customers",
                "revenue",
                "average_order_value",
            ]
        )

    d = orders.copy()

    d["month"] = d["invoice_date"].dt.to_period("M").astype(str)

    kpis = d.groupby("month", as_index=False).agg(
        orders=("invoice", "nunique"),
        customers=("customer_id", "nunique"),
        revenue=("revenue", "sum"),
    )

    kpis["average_order_value"] = (kpis.revenue / kpis.orders).round(2)

    return kpis


# 7. Main ETL pipeline
def run(input_file: Path, output_dir: Path):

    output_dir.mkdir(parents=True, exist_ok=True)

    # Read and clean data
    lines, report = clean_orders(read_source(input_file))

    # Create invoice table
    orders = invoice_table(lines)

    # Generate analytical tables
    tables = {
        "clean_sales": lines,
        "orders": orders,
        "rfm_segments": make_rfm(orders),
        "cohort_retention": cohort_retention(orders),
        "monthly_kpis": monthly_kpis(orders),
    }

    # Save tables as CSV
    for name, frame in tables.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)

    # Save data quality report
    (output_dir / "quality_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf8"
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))

    print("Generated:", ", ".join(tables))


# 8. Program entry point
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", default="data/raw/online_retail_II.xlsx", type=Path)

    parser.add_argument("--output", default="data/processed", type=Path)

    args = parser.parse_args()

    run(args.input, args.output)
