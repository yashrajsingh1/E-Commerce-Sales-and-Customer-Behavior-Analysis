# =============================================================================
# Step 3: Customer Segmentation using RFM Analysis
# Project : E-Commerce Sales and Customer Behavior Analysis
# =============================================================================
# RFM stands for:
#   R – Recency    : How recently did the customer purchase?
#   F – Frequency  : How often do they purchase?
#   M – Monetary   : How much money do they spend?
#
# Each metric is scored 1-5 (5 = best). Customers are then labelled into
# business-meaningful segments.
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

CLEANED   = "data/processed/cleaned_retail.csv"
REPORT_DIR = "reports"
RFM_OUTPUT = "data/processed/rfm_segments.csv"
os.makedirs(REPORT_DIR, exist_ok=True)

# ------------------------------------------------------------------
# LOAD
# ------------------------------------------------------------------
df = pd.read_csv(CLEANED, parse_dates=["invoicedate"])
print(f"Loaded {len(df):,} rows")

# ------------------------------------------------------------------
# SNAPSHOT DATE  (day after the last transaction in the dataset)
# ------------------------------------------------------------------
snapshot_date = df["invoicedate"].max() + pd.Timedelta(days=1)
print(f"Snapshot date : {snapshot_date.date()}")

# ------------------------------------------------------------------
# CALCULATE RFM METRICS PER CUSTOMER
# ------------------------------------------------------------------
rfm = (df.groupby("customer_id")
         .agg(
             last_purchase   = ("invoicedate", "max"),
             frequency       = ("invoice",     "nunique"),   # unique orders
             monetary        = ("total_sales", "sum")        # total spend
         )
         .reset_index())

rfm["recency"] = (snapshot_date - rfm["last_purchase"]).dt.days
rfm.drop(columns=["last_purchase"], inplace=True)

print("\nRFM Head:")
print(rfm.head())
print("\nRFM Describe:")
print(rfm.describe().round(2))

# ------------------------------------------------------------------
# SCORE  (quintile-based, 1–5)
# Note: for Recency, lower days = better -> scores are reversed
# ------------------------------------------------------------------
rfm["R_score"] = pd.qcut(rfm["recency"],   q=5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"),
                          q=5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"),
                          q=5, labels=[1, 2, 3, 4, 5]).astype(int)

rfm["RFM_score"]  = rfm["R_score"].astype(str) \
                  + rfm["F_score"].astype(str) \
                  + rfm["M_score"].astype(str)

rfm["RFM_total"]  = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

# ------------------------------------------------------------------
# SEGMENTATION LABELS
# ------------------------------------------------------------------
def assign_segment(row):
    r, f, m = row["R_score"], row["F_score"], row["M_score"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 2:
        return "Recent Customers"
    elif r >= 3 and f >= 2 and m >= 2:
        return "Potential Loyalists"
    elif r == 3 and f == 1:
        return "Promising"
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    elif r <= 2 and f >= 2 and m >= 2:
        return "Need Attention"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    else:
        return "Others"

rfm["segment"] = rfm.apply(assign_segment, axis=1)

# ------------------------------------------------------------------
# SEGMENT SUMMARY TABLE
# ------------------------------------------------------------------
seg_summary = (rfm.groupby("segment")
                   .agg(
                       customer_count = ("customer_id", "count"),
                       avg_recency    = ("recency",     "mean"),
                       avg_frequency  = ("frequency",   "mean"),
                       avg_monetary   = ("monetary",    "mean"),
                       total_revenue  = ("monetary",    "sum")
                   )
                   .reset_index()
                   .sort_values("total_revenue", ascending=False)
                   .round(2))

print("\nSegment Summary:")
print(seg_summary.to_string(index=False))

seg_summary.to_csv(f"{REPORT_DIR}/rfm_segment_summary.csv", index=False)

# ------------------------------------------------------------------
# VISUALISATION 1 – Segment Distribution (Pie + Bar)
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Pie
sizes  = seg_summary["customer_count"]
labels = seg_summary["segment"]
axes[0].pie(sizes, labels=labels, autopct="%1.1f%%",
            colors=sns.color_palette("Set2", len(sizes)),
            startangle=140)
axes[0].set_title("Customer Segment Distribution")

# Bar – total revenue per segment
axes[1].barh(seg_summary["segment"], seg_summary["total_revenue"],
             color=sns.color_palette("Blues_d", len(seg_summary)))
axes[1].xaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))
axes[1].set_title("Total Revenue by Segment")
axes[1].set_xlabel("Revenue (£)")

plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/09_rfm_segment_distribution.png")
plt.close()
print("Saved: 09_rfm_segment_distribution.png")

# ------------------------------------------------------------------
# VISUALISATION 2 – RFM Score Heatmap (R vs F coloured by avg M)
# ------------------------------------------------------------------
pivot = rfm.pivot_table(index="R_score", columns="F_score",
                        values="monetary", aggfunc="mean")

fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)
ax.set_title("Average Monetary Value: R-score vs F-score")
ax.set_xlabel("Frequency Score (F)")
ax.set_ylabel("Recency Score (R)")
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/10_rfm_heatmap.png")
plt.close()
print("Saved: 10_rfm_heatmap.png")

# ------------------------------------------------------------------
# VISUALISATION 3 – Scatter: Frequency vs Monetary coloured by segment
# ------------------------------------------------------------------
palette = sns.color_palette("Set1", rfm["segment"].nunique())
seg_map = {s: i for i, s in enumerate(rfm["segment"].unique())}
colors  = [palette[seg_map[s]] for s in rfm["segment"]]

fig, ax = plt.subplots(figsize=(9, 5))
scatter = ax.scatter(rfm["frequency"], rfm["monetary"],
                     c=colors, alpha=0.5, s=20)
ax.set_xlabel("Frequency (# of Orders)")
ax.set_ylabel("Monetary Value (£)")
ax.set_title("Customer Clusters: Frequency vs Monetary")

handles = [plt.Line2D([0], [0], marker="o", color="w",
                       markerfacecolor=palette[i], label=s, markersize=8)
           for s, i in seg_map.items()]
ax.legend(handles=handles, title="Segment", bbox_to_anchor=(1.01, 1),
          loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/11_rfm_scatter.png")
plt.close()
print("Saved: 11_rfm_scatter.png")

# ------------------------------------------------------------------
# SAVE FINAL RFM TABLE
# ------------------------------------------------------------------
rfm.to_csv(RFM_OUTPUT, index=False)
print(f"\nRFM segments saved -> {RFM_OUTPUT}")

# ------------------------------------------------------------------
# BUSINESS INSIGHTS PRINT
# ------------------------------------------------------------------
print("\n" + "="*55)
print("RFM BUSINESS INSIGHTS")
print("="*55)
champions = rfm[rfm["segment"] == "Champions"]
at_risk   = rfm[rfm["segment"] == "At Risk"]
lost      = rfm[rfm["segment"] == "Lost"]

print(f"Champions       : {len(champions):,} customers "
      f"| Avg spend £{champions['monetary'].mean():,.0f}")
print(f"At Risk         : {len(at_risk):,} customers "
      f"| Avg spend £{at_risk['monetary'].mean():,.0f} -- re-engage!")
print(f"Lost            : {len(lost):,} customers "
      f"| Avg spend £{lost['monetary'].mean():,.0f}")

print("""
RECOMMENDED ACTIONS:
  Champions       -> VIP loyalty programme, early product access
  Loyal Customers -> Upsell premium lines, referral bonuses
  At Risk         -> Win-back email with discount, survey why they left
  Lost            -> Low-cost reactivation campaign or write off
  Recent Customers-> Onboarding series to increase 2nd purchase
""")
