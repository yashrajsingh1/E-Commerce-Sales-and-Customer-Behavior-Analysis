# =============================================================================
# Dashboard : E-Commerce Sales and Customer Behavior Analysis
# Run with  : streamlit run app.py
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
)

PROCESSED  = Path("data/processed")
REPORT_DIR = Path("reports")

# ------------------------------------------------------------------
# DATA LOADING
# ------------------------------------------------------------------
@st.cache_data
def load_transactions():
    full = PROCESSED / "cleaned_retail.csv"
    sample = PROCESSED / "sample_retail.csv"
    if full.exists():
        df = pd.read_csv(full, parse_dates=["invoicedate"])
        is_sample = False
    elif sample.exists():
        df = pd.read_csv(sample, parse_dates=["invoicedate"])
        is_sample = True
    else:
        return None, False
    return df, is_sample

@st.cache_data
def load_rfm():
    p = PROCESSED / "rfm_segments.csv"
    return pd.read_csv(p) if p.exists() else None

df_full, is_sample = load_transactions()
rfm = load_rfm()

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.title("🛒 E-Commerce Sales & Customer Behavior")
st.caption("UCI Online Retail II  |  2009 – 2011  |  UK-based online retailer")

if is_sample:
    st.info("Live demo uses a 5,000-row sample. Clone the repo and run the pipeline locally for the full 779K-row dataset.", icon="ℹ️")

# ------------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")

    if df_full is not None:
        years = sorted(df_full["year"].unique())
        sel_years = st.multiselect("Year", years, default=years)

        countries = sorted(df_full["country"].unique())
        sel_countries = st.multiselect(
            "Country (top 10 by revenue)",
            options=sorted(
                df_full.groupby("country")["total_sales"].sum()
                       .nlargest(10).index.tolist()
            ),
            default=[],
            placeholder="All countries",
        )
    else:
        sel_years, sel_countries = [], []

    st.divider()
    st.markdown("**Stack**")
    st.markdown("Python · Pandas · Plotly · Streamlit · SQLite")
    st.markdown("[GitHub Repo](https://github.com/yashrajsingh1/E-Commerce-Sales-and-Customer-Behavior-Analysis)")

# ------------------------------------------------------------------
# APPLY FILTERS
# ------------------------------------------------------------------
if df_full is not None:
    df = df_full.copy()
    if sel_years:
        df = df[df["year"].isin(sel_years)]
    if sel_countries:
        df = df[df["country"].isin(sel_countries)]
else:
    df = None

# ------------------------------------------------------------------
# KPI CARDS
# ------------------------------------------------------------------
kpi_path = REPORT_DIR / "00_kpi_summary.csv"

if df is not None:
    total_rev   = df["total_sales"].sum()
    total_orders = df["invoice"].nunique()
    total_cust  = df["customer_id"].nunique()
    total_prod  = df["stockcode"].nunique()
    avg_order   = df.groupby("invoice")["total_sales"].sum().mean()
    top_country = df.groupby("country")["total_sales"].sum().idxmax()
elif kpi_path.exists():
    kpi = pd.read_csv(kpi_path).set_index("KPI")["Value"]
    total_rev    = float(kpi["Total Revenue (£)"])
    total_orders = int(float(kpi["Total Orders"]))
    total_cust   = int(float(kpi["Total Customers"]))
    total_prod   = int(float(kpi["Total Products"]))
    avg_order    = float(kpi["Average Order Value (£)"])
    top_country  = kpi["Top Country"]
else:
    total_rev = total_orders = total_cust = total_prod = avg_order = top_country = None

if total_rev is not None:
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Revenue",   f"£{total_rev:,.0f}")
    c2.metric("Total Orders",    f"{int(total_orders):,}")
    c3.metric("Customers",       f"{int(total_cust):,}")
    c4.metric("Products",        f"{int(total_prod):,}")
    c5.metric("Avg Order Value", f"£{avg_order:,.2f}")
    c6.metric("Top Country",     str(top_country))

st.divider()

# ------------------------------------------------------------------
# TABS
# ------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Sales Analysis", "👥 RFM Segments", "🔍 Data Explorer"])

COLORS = px.colors.qualitative.Plotly

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — SALES ANALYSIS
# ═══════════════════════════════════════════════════════════════════
with tab1:
    if df is None:
        st.warning("Transaction data not found. Run `python scripts/01_data_cleaning.py` first.")
    else:
        # ── Monthly Revenue Trend ─────────────────────────────────
        monthly = (df.groupby(["year", "month"])["total_sales"]
                     .sum().reset_index()
                     .assign(period=lambda x: pd.to_datetime(
                         x["year"].astype(str) + "-" + x["month"].astype(str)))
                     .sort_values("period"))

        fig = px.area(monthly, x="period", y="total_sales",
                      title="Monthly Revenue Trend",
                      labels={"period": "Month", "total_sales": "Revenue (£)"},
                      color_discrete_sequence=["#1f77b4"],
                      template="plotly_white")
        fig.update_traces(line_width=2)
        fig.update_yaxes(tickprefix="£", tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

        # ── Row: Quarterly + Day of Week ─────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            quarterly = (df.groupby(["year", "quarter"])["total_sales"]
                           .sum().reset_index()
                           .assign(label=lambda x:
                               x["year"].astype(str) + " Q" + x["quarter"].astype(str)))
            fig = px.bar(quarterly, x="label", y="total_sales",
                         title="Quarterly Revenue",
                         labels={"label": "Quarter", "total_sales": "Revenue (£)"},
                         color="total_sales", color_continuous_scale="Blues",
                         template="plotly_white")
            fig.update_yaxes(tickprefix="£", tickformat=",.0f")
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            dow = (df.groupby("day_of_week")["total_sales"]
                     .sum().reindex(day_order).reset_index())
            fig = px.bar(dow, x="day_of_week", y="total_sales",
                         title="Revenue by Day of Week",
                         labels={"day_of_week": "Day", "total_sales": "Revenue (£)"},
                         color="total_sales", color_continuous_scale="Purples",
                         template="plotly_white")
            fig.update_yaxes(tickprefix="£", tickformat=",.0f")
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        # ── Row: Top Countries + Top Products ────────────────────
        col1, col2 = st.columns(2)

        with col1:
            country_rev = (df.groupby("country")["total_sales"]
                             .sum().nlargest(10).reset_index())
            fig = px.bar(country_rev, x="total_sales", y="country",
                         orientation="h",
                         title="Top 10 Countries by Revenue",
                         labels={"total_sales": "Revenue (£)", "country": ""},
                         color="total_sales", color_continuous_scale="Blues",
                         template="plotly_white")
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            fig.update_xaxes(tickprefix="£", tickformat=",.0f")
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            top_prod = (df.groupby("description")["quantity"]
                          .sum().nlargest(10).reset_index())
            fig = px.bar(top_prod, x="quantity", y="description",
                         orientation="h",
                         title="Top 10 Best-Selling Products",
                         labels={"quantity": "Units Sold", "description": ""},
                         color="quantity", color_continuous_scale="Greens",
                         template="plotly_white")
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        # ── Row: Revenue by Hour + Order Value Distribution ──────
        col1, col2 = st.columns(2)

        with col1:
            hourly = df.groupby("hour")["total_sales"].sum().reset_index()
            fig = px.bar(hourly, x="hour", y="total_sales",
                         title="Revenue by Hour of Day",
                         labels={"hour": "Hour (24h)", "total_sales": "Revenue (£)"},
                         color_discrete_sequence=["#4C72B0"],
                         template="plotly_white")
            fig.update_yaxes(tickprefix="£", tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            order_vals = df.groupby("invoice")["total_sales"].sum()
            cap = order_vals.quantile(0.99)
            fig = px.histogram(order_vals[order_vals < cap],
                               title="Order Value Distribution (99th pct cap)",
                               labels={"value": "Order Value (£)", "count": "Orders"},
                               nbins=60, color_discrete_sequence=["#1f77b4"],
                               template="plotly_white")
            fig.update_xaxes(tickprefix="£")
            st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 2 — RFM SEGMENTS
# ═══════════════════════════════════════════════════════════════════
with tab2:
    if rfm is None:
        st.warning("RFM data not found. Run `python scripts/03_rfm_analysis.py` first.")
    else:
        seg_summary_path = REPORT_DIR / "rfm_segment_summary.csv"
        seg_summary = pd.read_csv(seg_summary_path) if seg_summary_path.exists() else (
            rfm.groupby("segment").agg(
                customer_count=("customer_id", "count"),
                avg_recency=("recency", "mean"),
                avg_frequency=("frequency", "mean"),
                avg_monetary=("monetary", "mean"),
                total_revenue=("monetary", "sum"),
            ).reset_index()
        )

        # ── Row: Segment Count + Revenue Pie ─────────────────────
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(seg_summary.sort_values("customer_count", ascending=True),
                         x="customer_count", y="segment", orientation="h",
                         title="Customers per Segment",
                         labels={"customer_count": "Customers", "segment": ""},
                         color="segment", template="plotly_white",
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(seg_summary, values="total_revenue", names="segment",
                         title="Revenue Share by Segment",
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         hole=0.4, template="plotly_white")
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        # ── RFM Scatter ───────────────────────────────────────────
        fig = px.scatter(rfm, x="frequency", y="monetary",
                         color="segment", opacity=0.6, size_max=8,
                         title="Customer Clusters: Frequency vs Monetary Value",
                         labels={"frequency": "Frequency (# orders)",
                                 "monetary": "Monetary Value (£)",
                                 "segment": "Segment"},
                         color_discrete_sequence=px.colors.qualitative.Set1,
                         template="plotly_white",
                         hover_data={"recency": True, "R_score": True,
                                     "F_score": True, "M_score": True})
        fig.update_yaxes(tickprefix="£")
        st.plotly_chart(fig, use_container_width=True)

        # ── RFM Heatmap ───────────────────────────────────────────
        pivot = rfm.pivot_table(index="R_score", columns="F_score",
                                values="monetary", aggfunc="mean")
        fig = px.imshow(pivot, text_auto=".0f",
                        title="Avg Monetary Value: R-score vs F-score",
                        labels={"x": "Frequency Score (F)",
                                "y": "Recency Score (R)",
                                "color": "Avg £"},
                        color_continuous_scale="YlOrRd",
                        template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        # ── Segment Summary Table ─────────────────────────────────
        st.subheader("Segment Summary")
        disp = seg_summary.copy().sort_values("total_revenue", ascending=False)
        disp.columns = [c.replace("_", " ").title() for c in disp.columns]
        st.dataframe(
            disp.style.format({
                "Customer Count": "{:,.0f}",
                "Avg Recency":    "{:.0f} days",
                "Avg Frequency":  "{:.1f}",
                "Avg Monetary":   "£{:,.0f}",
                "Total Revenue":  "£{:,.0f}",
            }),
            use_container_width=True, hide_index=True,
        )

        # Download button
        st.download_button(
            "Download RFM Segment Summary (CSV)",
            data=seg_summary.to_csv(index=False),
            file_name="rfm_segment_summary.csv",
            mime="text/csv",
        )

# ═══════════════════════════════════════════════════════════════════
# TAB 3 — DATA EXPLORER
# ═══════════════════════════════════════════════════════════════════
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Transaction Sample")
        tx_path_full   = PROCESSED / "cleaned_retail.csv"
        tx_path_sample = PROCESSED / "sample_retail.csv"

        if tx_path_full.exists():
            tx = pd.read_csv(tx_path_full, nrows=2000, parse_dates=["invoicedate"])
            st.caption(f"Showing 2,000 of 779,425 rows (full dataset)")
        elif tx_path_sample.exists():
            tx = pd.read_csv(tx_path_sample, parse_dates=["invoicedate"])
            st.caption(f"Showing 5,000-row demo sample")
        else:
            tx = None
            st.warning("Run `python scripts/01_data_cleaning.py` to generate transaction data.")

        if tx is not None:
            st.dataframe(tx, use_container_width=True, hide_index=True)
            st.download_button(
                "Download Sample (CSV)",
                data=tx.to_csv(index=False),
                file_name="sample_transactions.csv",
                mime="text/csv",
            )

    with col2:
        st.subheader("RFM Customer Table")
        if rfm is not None:
            seg_filter = st.multiselect(
                "Filter by segment", rfm["segment"].unique(),
                default=[], placeholder="All segments"
            )
            rfm_disp = rfm if not seg_filter else rfm[rfm["segment"].isin(seg_filter)]
            st.caption(f"Showing {len(rfm_disp):,} customers")
            st.dataframe(rfm_disp, use_container_width=True, hide_index=True)
            st.download_button(
                "Download RFM Table (CSV)",
                data=rfm_disp.to_csv(index=False),
                file_name="rfm_segments.csv",
                mime="text/csv",
            )
        else:
            st.warning("Run `python scripts/03_rfm_analysis.py` to generate RFM data.")
