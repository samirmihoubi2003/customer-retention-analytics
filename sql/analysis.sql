-- Run after python -m src.load_postgres
-- KPI by month: each invoice is counted once in the orders table.
SELECT date_trunc('month', invoice_date)::date AS month,
       COUNT(*) AS invoice_count,
       COUNT(DISTINCT customer_id) AS active_customers,
       ROUND(SUM(revenue)::numeric,2) AS sales_gbp,
       ROUND(AVG(revenue)::numeric,2) AS average_order_value_gbp
FROM orders
GROUP BY 1 ORDER BY 1;

-- Distribution of customers and spending by RFM segment.
SELECT segment, COUNT(*) AS customers,
       ROUND(SUM(monetary)::numeric,2) AS customer_sales_gbp
FROM rfm_segments GROUP BY segment ORDER BY customers DESC;

-- Cohort retention, where month 0 is always 100%.
SELECT cohort_month, period_number, active_customers, cohort_size,
       ROUND((retention_rate*100)::numeric,2) AS retention_pct
FROM cohort_retention ORDER BY cohort_month,period_number;
