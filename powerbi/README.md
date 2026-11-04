# Power BI dashboard build guide

1. After running ETL, open Power BI Desktop > Get data > Text/CSV.
2. Import `monthly_kpis.csv`, `rfm_segments.csv`, `cohort_retention.csv` and `orders.csv` from `data/processed/`.
3. Set `orders.invoice_date` as Date/Time and numerical fields as Decimal / Whole number.
4. Cards: Total Sales = SUM(orders[revenue]); Orders = DISTINCTCOUNT(orders[invoice]); Customers = DISTINCTCOUNT(orders[customer_id]); AOV = DIVIDE([Total Sales], [Orders]).
5. Line chart: monthly_kpis[month] vs monthly_kpis[revenue].
6. Bar chart: rfm_segments[segment] vs distinct count of rfm_segments[customer_id].
7. Cohort heatmap: Matrix rows cohort_retention[cohort_month], columns period_number, values retention_rate, conditional formatting; format as percentage.
8. Document that partial first/last months and incomplete cohort observation windows limit interpretation.
9. Save `customer_retention.pbix` locally; create screenshots `powerbi/dashboard.png` (add screenshot explicitly via `git add -f` only if needed; PBIX deliberately ignored).

These are construction instructions, **not** a claim that a Power BI dashboard is already finished.
