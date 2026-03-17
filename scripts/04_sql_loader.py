# =============================================================================
# Step 4 (Helper): Load CSVs into SQLite and run queries
# =============================================================================
import sqlite3
import pandas as pd

DB = "ecommerce.db"
conn = sqlite3.connect(DB)

print("Loading tables into SQLite …")
pd.read_csv("data/processed/cleaned_retail.csv")\
  .to_sql("retail", conn, if_exists="replace", index=False)
pd.read_csv("data/processed/rfm_segments.csv")\
  .to_sql("rfm",    conn, if_exists="replace", index=False)

print("Tables created: retail, rfm")

# --- Run a sample query ---
query = """
SELECT
    country,
    ROUND(SUM(total_sales), 2)  AS total_revenue,
    COUNT(DISTINCT customer_id) AS customers
FROM retail
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10
"""
result = pd.read_sql(query, conn)
print("\nTop 10 Countries by Revenue:")
print(result.to_string(index=False))

conn.close()
print(f"\nDatabase saved -> {DB}")
print("Open sql/business_queries.sql and run any query via this script.")
