# Customer Behavior & Retention Analytics

**Portfolio project | Python • SQL • PostgreSQL • Power BI • pytest • Docker • GitHub Actions**

End-to-end analysis of historical UK online retail transactions to understand customer buying behavior, purchase frequency, RFM segmentation and monthly cohort retention.

> Status: runnable ETL/analytics code and SQL included. Power BI report must be built locally; do not claim dashboard visuals are completed before publishing screenshots.

## Data source
UCI Online Retail II, Daqing Chen (2012), DOI: [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D), CC BY 4.0. Historical data: Dec 2009–Dec 2011. Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii.

## Quick start — Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Download online_retail_II.xlsx from UCI and put it in data/raw/
python src/explore_data.py       # First exploration (original script)
python -m src.pipeline         # Data cleaning and analytics
python -m pytest -q           # Unit tests
```

Generated files in `data/processed/`: `clean_sales.csv`, `orders.csv`, `rfm_segments.csv`, `cohort_retention.csv`, `monthly_kpis.csv`, `quality_report.json`.

## Optional PostgreSQL

```powershell
docker compose up -d
$env:DATABASE_URL='postgresql+psycopg2://retail:retail@localhost:5434/retail'
python -m src.load_postgres
```

Connect DBeaver or psql to localhost:5434, database `retail`, user/password `retail`/`retail`. Execute `sql/analysis.sql`. Local development passwords only: change them for any remote deployment.

## Methodology and definitions

- `Invoice` identifies an order, while each raw row is an **order line** (item). Order counts use distinct invoices (per customer).
- Exact duplicate rows are removed as a documented modeling choice; some could represent distinct identically recorded items, so compare results with and without deduplication before business use.
- Cancellations (`Invoice` beginning with C) and lines with non-positive quantity/price are excluded from **positive-sales analysis**; do not interpret sales as net revenue or refunds-adjusted financial results.
- Anonymous `Customer ID` rows are excluded, so the customer analysis is for identified customers, not all sales.
- RFM = recency (days since last purchase), frequency (distinct invoices) and monetary (positive line sales). Simple five-rank segments are explanatory, not validated business segments.
- Cohort month = first observed purchase month. Monthly retention is active customers in cohort at period N / initial cohort size. Month 0 = 100%. This is **observed** repeat behavior, not causal loyalty or a churn prediction.
- First and last observed months may be partial; more recent cohorts lack long follow-up. Prior activity before observation is unknown.
- Currency from source is GBP (£); neither inflation nor VAT are adjusted here.

## Repository structure

- `src/explore_data.py`: original exploratory analysis and printouts
- `src/pipeline.py`: extract, cleaning and analytics
- `src/load_postgres.py`: local PostgreSQL importer
- `sql/analysis.sql`: SQL KPI queries
- `tests/`: independent tests using synthetic test rows
- `.github/workflows/ci.yml`: automatic tests on pushes and pull requests
- `powerbi/README.md`: dashboard implementation guide

## Quality checks

Run `python -m pytest -q`. CI uses small generated fixtures and does not require downloading or redistributing UCI data.

## Results

Real results should be added **after running the dataset**: see `data/processed/quality_report.json`. Add a screenshot to this section when the Power BI report exists. Never substitute fixture metrics for dataset results.

## License and attribution

Code MIT license. Original dataset remains under its separate CC BY 4.0 license and is not committed to Git.
