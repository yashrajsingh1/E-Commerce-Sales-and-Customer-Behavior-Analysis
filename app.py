# =============================================================================
# Dashboard : E-Commerce Sales and Customer Behavior Analysis
# Run with  : streamlit run app.py
# =============================================================================

import streamlit as st
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
)

REPORT_DIR = Path("reports")
PROCESSED  = Path("data/processed")

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.title("🛒 E-Commerce Sales & Customer Behavior")
st.caption("UCI Online Retail II Dataset  |  2009 – 2011")

# ------------------------------------------------------------------
# KPI CARDS
# ------------------------------------------------------------------
kpi_path = REPORT_DIR / "00_kpi_summary.csv"
if kpi_path.exists():
    kpi = pd.read_csv(kpi_path).set_index("KPI")["Value"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Revenue",      f"£{float(kpi['Total Revenue (£)']):,.0f}")
    c2.metric("Total Orders",       f"{int(float(kpi['Total Orders'])):,}")
    c3.metric("Total Customers",    f"{int(float(kpi['Total Customers'])):,}")
    c4.metric("Total Products",     f"{int(float(kpi['Total Products'])):,}")
    c5.metric("Avg Order Value",    f"£{float(kpi['Average Order Value (£)']):,.2f}")

st.divider()

# ------------------------------------------------------------------
# TABS
# ------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Sales Analysis", "👥 RFM Segments", "📋 Data Tables"])

# ── Tab 1 : Sales Analysis ────────────────────────────────────────
with tab1:
    charts = [
        ("01_monthly_revenue_trend.png",   "Monthly Revenue Trend"),
        ("07_quarterly_revenue.png",        "Quarterly Revenue Breakdown"),
        ("02_top_countries_revenue.png",    "Top 10 Countries by Revenue"),
        ("03_top_products.png",             "Top 10 Best-Selling Products"),
        ("04_revenue_by_dow.png",           "Revenue by Day of Week"),
        ("05_revenue_by_hour.png",          "Revenue by Hour of Day"),
        ("06_order_value_distribution.png", "Order Value Distribution"),
        ("08_correlation_heatmap.png",      "Correlation Heatmap"),
    ]

    # Full-width charts
    for fname, title in charts[:2]:
        p = REPORT_DIR / fname
        if p.exists():
            st.subheader(title)
            st.image(str(p), use_container_width=True)

    # Side-by-side pairs
    for i in range(2, len(charts), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(charts):
                fname, title = charts[i + j]
                p = REPORT_DIR / fname
                if p.exists():
                    with col:
                        st.subheader(title)
                        st.image(str(p), use_container_width=True)

# ── Tab 2 : RFM Segments ─────────────────────────────────────────
with tab2:
    rfm_charts = [
        ("09_rfm_segment_distribution.png", "Segment Distribution & Revenue"),
        ("10_rfm_heatmap.png",              "RFM Score Heatmap"),
        ("11_rfm_scatter.png",              "Customer Clusters: Frequency vs Monetary"),
    ]

    # First chart full-width
    p = REPORT_DIR / rfm_charts[0][0]
    if p.exists():
        st.subheader(rfm_charts[0][1])
        st.image(str(p), use_container_width=True)

    # Next two side-by-side
    cols = st.columns(2)
    for i, col in enumerate(cols):
        fname, title = rfm_charts[i + 1]
        p = REPORT_DIR / fname
        if p.exists():
            with col:
                st.subheader(title)
                st.image(str(p), use_container_width=True)

    # Segment summary table
    seg_path = REPORT_DIR / "rfm_segment_summary.csv"
    if seg_path.exists():
        st.divider()
        st.subheader("Segment Summary")
        seg_df = pd.read_csv(seg_path)
        seg_df.columns = [c.replace("_", " ").title() for c in seg_df.columns]
        seg_df = seg_df.sort_values("Total Revenue", ascending=False)

        # Format numeric columns
        for col in ["Avg Recency", "Avg Frequency", "Avg Monetary", "Total Revenue"]:
            if col in seg_df.columns:
                if col == "Avg Recency":
                    seg_df[col] = seg_df[col].apply(lambda x: f"{x:.0f} days")
                elif col == "Avg Frequency":
                    seg_df[col] = seg_df[col].apply(lambda x: f"{x:.1f}")
                else:
                    seg_df[col] = seg_df[col].apply(lambda x: f"£{x:,.0f}")

        st.dataframe(seg_df, use_container_width=True, hide_index=True)

# ── Tab 3 : Data Tables ───────────────────────────────────────────
with tab3:
    st.subheader("Cleaned Transaction Data (sample)")
    cleaned_path = PROCESSED / "cleaned_retail.csv"
    if cleaned_path.exists():
        df = pd.read_csv(cleaned_path, parse_dates=["invoicedate"], nrows=5000)
        st.dataframe(df.head(200), use_container_width=True)
        st.caption(f"Showing 200 of {len(df):,} loaded rows (full file: 779,425 rows)")
    else:
        st.warning("Run `python scripts/01_data_cleaning.py` first.")

    st.divider()
    st.subheader("RFM Segments (all customers)")
    rfm_path = PROCESSED / "rfm_segments.csv"
    if rfm_path.exists():
        rfm_df = pd.read_csv(rfm_path)
        st.dataframe(rfm_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Run `python scripts/03_rfm_analysis.py` first.")
