# =============================================================================
# Step 2: Exploratory Data Analysis (EDA)
# Project : E-Commerce Sales and Customer Behavior Analysis
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")

# ------------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------------
sns.set_theme(style="whitegrid", palette="Blues_d")
plt.rcParams.update({"figure.dpi": 130, "axes.titlesize": 13,
                     "axes.labelsize": 11})

CLEANED   = "data/processed/cleaned_retail.csv"
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# ------------------------------------------------------------------
# LOAD
# ------------------------------------------------------------------
df = pd.read_csv(CLEANED, parse_dates=["invoicedate"])
print(f"Loaded {len(df):,} rows × {df.shape[1]} columns")

# =============================================================================
# EDA 1 – Monthly Revenue Trend
# =============================================================================
monthly = (df.groupby(["year", "month"])["total_sales"]
             .sum()
             .reset_index()
             .assign(period=lambda x: pd.to_datetime(
                 x["year"].astype(str) + "-" + x["month"].astype(str))))
monthly.sort_values("period", inplace=True)

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(monthly["period"], monthly["total_sales"], marker="o",
        linewidth=2, color="#1f77b4")
ax.fill_between(monthly["period"], monthly["total_sales"], alpha=0.15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
ax.set_title("Monthly Revenue Trend")
ax.set_xlabel("Month")
ax.set_ylabel("Total Revenue (£)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/01_monthly_revenue_trend.png")
plt.close()
print("Saved: 01_monthly_revenue_trend.png")

# Business Insight:
peak_month = monthly.loc[monthly["total_sales"].idxmax()]
print(f"\n[INSIGHT] Peak revenue month: {peak_month['period'].strftime('%B %Y')} "
      f"-> £{peak_month['total_sales']:,.0f}")

# =============================================================================
# EDA 2 – Top 10 Countries by Revenue
# =============================================================================
country_rev = (df.groupby("country")["total_sales"]
                 .sum()
                 .sort_values(ascending=False)
                 .head(10)
                 .reset_index())

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(country_rev["country"][::-1],
               country_rev["total_sales"][::-1],
               color=sns.color_palette("Blues_d", 10))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))
ax.set_title("Top 10 Countries by Revenue")
ax.set_xlabel("Total Revenue (£)")
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/02_top_countries_revenue.png")
plt.close()
print("Saved: 02_top_countries_revenue.png")

# =============================================================================
# EDA 3 – Top 10 Best-Selling Products
# =============================================================================
top_products = (df.groupby("description")["quantity"]
                  .sum()
                  .sort_values(ascending=False)
                  .head(10)
                  .reset_index())

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(top_products["description"][::-1],
        top_products["quantity"][::-1],
        color=sns.color_palette("Greens_d", 10))
ax.set_title("Top 10 Best-Selling Products (by Units Sold)")
ax.set_xlabel("Total Quantity Sold")
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/03_top_products.png")
plt.close()
print("Saved: 03_top_products.png")

# =============================================================================
# EDA 4 – Sales by Day of Week
# =============================================================================
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow = (df.groupby("day_of_week")["total_sales"]
         .sum()
         .reindex(day_order)
         .reset_index())

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(dow["day_of_week"], dow["total_sales"],
       color=sns.color_palette("Purples_d", 7))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))
ax.set_title("Revenue by Day of Week")
ax.set_xlabel("Day")
ax.set_ylabel("Revenue (£)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/04_revenue_by_dow.png")
plt.close()
print("Saved: 04_revenue_by_dow.png")

# =============================================================================
# EDA 5 – Revenue by Hour of Day
# =============================================================================
hourly = (df.groupby("hour")["total_sales"]
            .sum()
            .reset_index())

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(hourly["hour"], hourly["total_sales"], color="#4C72B0")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))
ax.set_title("Revenue by Hour of Day")
ax.set_xlabel("Hour (24h)")
ax.set_ylabel("Revenue (£)")
ax.set_xticks(range(0, 24))
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/05_revenue_by_hour.png")
plt.close()
print("Saved: 05_revenue_by_hour.png")

# =============================================================================
# EDA 6 – Distribution of Order Values
# =============================================================================
order_vals = df.groupby("invoice")["total_sales"].sum()

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(order_vals[order_vals < order_vals.quantile(0.99)], bins=60,
             color="#1f77b4", edgecolor="white")
axes[0].set_title("Order Value Distribution (99th pct cap)")
axes[0].set_xlabel("Order Value (£)")
axes[0].set_ylabel("Count")

axes[1].boxplot(order_vals[order_vals < order_vals.quantile(0.99)],
                patch_artist=True,
                boxprops=dict(facecolor="#AEC6CF"))
axes[1].set_title("Order Value Boxplot")
axes[1].set_ylabel("Order Value (£)")

plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/06_order_value_distribution.png")
plt.close()
print("Saved: 06_order_value_distribution.png")

# =============================================================================
# EDA 7 – Quarterly Revenue Breakdown
# =============================================================================
quarterly = (df.groupby(["year", "quarter"])["total_sales"]
               .sum()
               .reset_index()
               .assign(label=lambda x: x["year"].astype(str) + " Q" + x["quarter"].astype(str)))

fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(quarterly["label"], quarterly["total_sales"],
       color=sns.color_palette("muted", len(quarterly)))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))
ax.set_title("Quarterly Revenue Breakdown")
ax.set_xlabel("Quarter")
ax.set_ylabel("Revenue (£)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/07_quarterly_revenue.png")
plt.close()
print("Saved: 07_quarterly_revenue.png")

# =============================================================================
# EDA 8 – Correlation Heatmap
# =============================================================================
numeric_cols = ["quantity", "price", "total_sales", "hour", "month", "quarter"]
corr = df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            linewidths=0.5, ax=ax)
ax.set_title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/08_correlation_heatmap.png")
plt.close()
print("Saved: 08_correlation_heatmap.png")

# =============================================================================
# SUMMARY STATS TABLE  -> saved as CSV for Power BI / Excel
# =============================================================================
summary = {
    "Total Revenue (£)"       : df["total_sales"].sum(),
    "Total Orders"            : df["invoice"].nunique(),
    "Total Customers"         : df["customer_id"].nunique(),
    "Total Products"          : df["stockcode"].nunique(),
    "Average Order Value (£)" : df.groupby("invoice")["total_sales"].sum().mean(),
    "Top Country"             : df.groupby("country")["total_sales"].sum().idxmax(),
}
summary_df = pd.DataFrame(summary.items(), columns=["KPI", "Value"])
summary_df.to_csv(f"{REPORT_DIR}/00_kpi_summary.csv", index=False)
print("\nKPI Summary:")
print(summary_df.to_string(index=False))
