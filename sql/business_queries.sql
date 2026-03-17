-- =============================================================================
-- Step 4: SQL Queries for Business Questions
-- Project : E-Commerce Sales and Customer Behavior Analysis
-- Database: SQLite / PostgreSQL compatible
-- =============================================================================
-- HOW TO USE
-- 1. Import cleaned_retail.csv into your database as table: retail
-- 2. Import rfm_segments.csv as table: rfm
-- Quick SQLite setup (Python):
--   import sqlite3, pandas as pd
--   conn = sqlite3.connect("ecommerce.db")
--   pd.read_csv("data/processed/cleaned_retail.csv").to_sql("retail", conn)
--   pd.read_csv("data/processed/rfm_segments.csv").to_sql("rfm",    conn)
-- =============================================================================


-- =============================================================================
-- SECTION A: REVENUE ANALYSIS
-- =============================================================================

-- A1. Total Revenue, Orders, and Customers
SELECT
    ROUND(SUM(total_sales), 2)          AS total_revenue,
    COUNT(DISTINCT invoice)             AS total_orders,
    COUNT(DISTINCT customer_id)         AS total_customers,
    ROUND(SUM(total_sales) /
          COUNT(DISTINCT invoice), 2)   AS avg_order_value
FROM retail;


-- A2. Monthly Revenue Trend
SELECT
    year,
    month,
    ROUND(SUM(total_sales), 2)          AS monthly_revenue,
    COUNT(DISTINCT invoice)             AS monthly_orders,
    COUNT(DISTINCT customer_id)         AS active_customers
FROM retail
GROUP BY year, month
ORDER BY year, month;


-- A3. Top 10 Revenue Months (ranked)
SELECT
    year,
    month,
    ROUND(SUM(total_sales), 2)          AS revenue,
    RANK() OVER (ORDER BY SUM(total_sales) DESC) AS revenue_rank
FROM retail
GROUP BY year, month
ORDER BY revenue DESC
LIMIT 10;


-- A4. Quarter-over-Quarter Revenue Growth
WITH quarterly AS (
    SELECT
        year,
        quarter,
        SUM(total_sales) AS revenue
    FROM retail
    GROUP BY year, quarter
)
SELECT
    year,
    quarter,
    ROUND(revenue, 2)                   AS revenue,
    ROUND(LAG(revenue) OVER
          (ORDER BY year, quarter), 2)  AS prev_quarter_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY year, quarter))
        / LAG(revenue) OVER (ORDER BY year, quarter) * 100
    , 2)                                AS qoq_growth_pct
FROM quarterly
ORDER BY year, quarter;


-- =============================================================================
-- SECTION B: PRODUCT ANALYSIS
-- =============================================================================

-- B1. Top 10 Products by Revenue
SELECT
    stockcode,
    description,
    ROUND(SUM(total_sales), 2)  AS total_revenue,
    SUM(quantity)               AS units_sold,
    ROUND(AVG(price), 2)        AS avg_price
FROM retail
GROUP BY stockcode, description
ORDER BY total_revenue DESC
LIMIT 10;


-- B2. Top 10 Products by Units Sold
SELECT
    stockcode,
    description,
    SUM(quantity)               AS units_sold,
    ROUND(SUM(total_sales), 2)  AS total_revenue
FROM retail
GROUP BY stockcode, description
ORDER BY units_sold DESC
LIMIT 10;


-- B3. Products with Declining Sales (compare first vs second half of data)
WITH half AS (
    SELECT
        stockcode,
        description,
        SUM(CASE WHEN month <= 6  THEN total_sales ELSE 0 END) AS h1_revenue,
        SUM(CASE WHEN month > 6   THEN total_sales ELSE 0 END) AS h2_revenue
    FROM retail
    GROUP BY stockcode, description
)
SELECT
    stockcode,
    description,
    ROUND(h1_revenue, 2)  AS h1_revenue,
    ROUND(h2_revenue, 2)  AS h2_revenue,
    ROUND(h2_revenue - h1_revenue, 2)  AS change
FROM half
WHERE h1_revenue > 0
ORDER BY change ASC
LIMIT 10;


-- =============================================================================
-- SECTION C: CUSTOMER ANALYSIS
-- =============================================================================

-- C1. Top 20 Customers by Revenue
SELECT
    customer_id,
    COUNT(DISTINCT invoice)    AS total_orders,
    ROUND(SUM(total_sales), 2) AS total_spent,
    ROUND(AVG(total_sales), 2) AS avg_order_value,
    MIN(DATE(invoicedate))     AS first_purchase,
    MAX(DATE(invoicedate))     AS last_purchase
FROM retail
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 20;


-- C2. Customer Retention: Repeat vs Single-Purchase Customers
SELECT
    CASE WHEN order_count = 1 THEN 'One-Time Buyer'
         ELSE 'Repeat Buyer'
    END                         AS customer_type,
    COUNT(*)                    AS customer_count,
    ROUND(COUNT(*) * 100.0 /
          SUM(COUNT(*)) OVER(), 2) AS pct_of_total
FROM (
    SELECT customer_id, COUNT(DISTINCT invoice) AS order_count
    FROM retail
    GROUP BY customer_id
) t
GROUP BY customer_type;


-- C3. Average Days Between Orders per Customer
WITH order_dates AS (
    SELECT
        customer_id,
        DATE(invoicedate)   AS order_date,
        LAG(DATE(invoicedate)) OVER
            (PARTITION BY customer_id ORDER BY invoicedate) AS prev_date
    FROM retail
    GROUP BY customer_id, DATE(invoicedate)
)
SELECT
    ROUND(AVG(JULIANDAY(order_date) - JULIANDAY(prev_date)), 1)
        AS avg_days_between_orders
FROM order_dates
WHERE prev_date IS NOT NULL;


-- C4. New Customers per Month
SELECT
    year,
    month,
    COUNT(DISTINCT customer_id) AS new_customers
FROM (
    SELECT
        customer_id,
        MIN(year)  AS year,
        MIN(month) AS month
    FROM retail
    GROUP BY customer_id
) t
GROUP BY year, month
ORDER BY year, month;


-- =============================================================================
-- SECTION D: GEOGRAPHIC ANALYSIS
-- =============================================================================

-- D1. Revenue by Country
SELECT
    country,
    ROUND(SUM(total_sales), 2)  AS total_revenue,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(DISTINCT invoice)     AS orders
FROM retail
GROUP BY country
ORDER BY total_revenue DESC;


-- D2. Contribution of UK vs Rest of World
SELECT
    CASE WHEN country = 'United Kingdom' THEN 'United Kingdom'
         ELSE 'Rest of World'
    END                           AS region,
    ROUND(SUM(total_sales), 2)    AS revenue,
    ROUND(SUM(total_sales) * 100.0
          / SUM(SUM(total_sales)) OVER(), 2) AS revenue_share_pct
FROM retail
GROUP BY region
ORDER BY revenue DESC;


-- =============================================================================
-- SECTION E: TIME / BEHAVIOUR ANALYSIS
-- =============================================================================

-- E1. Best Day of Week for Sales
SELECT
    day_of_week,
    ROUND(SUM(total_sales), 2)  AS total_revenue,
    COUNT(DISTINCT invoice)     AS total_orders
FROM retail
GROUP BY day_of_week
ORDER BY total_revenue DESC;


-- E2. Peak Shopping Hours
SELECT
    hour,
    ROUND(SUM(total_sales), 2)  AS revenue,
    COUNT(DISTINCT invoice)     AS orders
FROM retail
GROUP BY hour
ORDER BY revenue DESC;


-- E3. Average Order Value by Country (top 10 countries)
SELECT
    country,
    ROUND(SUM(total_sales) / COUNT(DISTINCT invoice), 2) AS avg_order_value,
    COUNT(DISTINCT invoice)                              AS total_orders
FROM retail
GROUP BY country
HAVING total_orders >= 10
ORDER BY avg_order_value DESC
LIMIT 10;


-- =============================================================================
-- SECTION F: RFM-LINKED QUERIES
-- =============================================================================

-- F1. Revenue contribution by RFM segment
SELECT
    r.segment,
    COUNT(DISTINCT r.customer_id)       AS customers,
    ROUND(SUM(ret.total_sales), 2)      AS segment_revenue,
    ROUND(SUM(ret.total_sales) * 100.0
          / SUM(SUM(ret.total_sales)) OVER(), 2) AS revenue_share_pct
FROM rfm AS r
JOIN retail AS ret ON r.customer_id = ret.customer_id
GROUP BY r.segment
ORDER BY segment_revenue DESC;


-- F2. Champions vs Lost: head-to-head comparison
SELECT
    r.segment,
    COUNT(DISTINCT r.customer_id)          AS customers,
    ROUND(AVG(r.recency), 1)               AS avg_recency_days,
    ROUND(AVG(r.frequency), 1)             AS avg_orders,
    ROUND(AVG(r.monetary), 2)              AS avg_spend
FROM rfm AS r
WHERE r.segment IN ('Champions', 'Lost')
GROUP BY r.segment;


-- F3. At-Risk customers with high lifetime value (re-engage priority)
SELECT
    r.customer_id,
    r.recency,
    r.frequency,
    ROUND(r.monetary, 2) AS total_spent
FROM rfm AS r
WHERE r.segment = 'At Risk'
  AND r.monetary > (SELECT AVG(monetary) FROM rfm)
ORDER BY r.monetary DESC
LIMIT 20;
