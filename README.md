# E-Commerce Sales and Customer Behavior Analysis

> **A complete Business Analyst portfolio project** demonstrating data cleaning,
> exploratory analysis, customer segmentation (RFM), SQL-based business intelligence,
> and an interactive Power BI dashboard.

---

## Problem Statement

An e-commerce retailer operating across multiple countries wants to understand
**what is driving revenue**, **who their most valuable customers are**, and
**where they are losing business**. The company needs actionable insights to
inform marketing, inventory, and retention strategy.

---

## Business Objectives

| # | Objective |
|---|-----------|
| 1 | Identify revenue trends across time, geography, and product lines |
| 2 | Segment customers by value using RFM analysis |
| 3 | Determine peak shopping periods to optimise promotions |
| 4 | Highlight at-risk and lost customers for re-engagement campaigns |
| 5 | Build a self-service Power BI dashboard for the business team |

---

## Dataset

| Attribute | Detail |
|-----------|--------|
| Name | Online Retail II |
| Source | [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Online+Retail+II) |
| Kaggle mirror | [mashlyn/online-retail-ii-uci](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci) |
| Period | December 2009 – December 2011 |
| Rows | ~1,067,371 transactions |
| Columns | 8 (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, Price, CustomerID, Country) |
| Countries | 38 |

---

## Project Workflow

```
Raw Data
   │
   ▼
01_data_cleaning.py   ← Remove nulls, duplicates, cancelled orders
   │                     Engineer: total_sales, year, month, hour …
   ▼
02_eda.py             ← 8 charts: trends, geography, products, time patterns
   │
   ▼
03_rfm_analysis.py    ← Score customers 1–5 on Recency / Frequency / Monetary
   │                     Label into 8 segments: Champions → Lost
   ▼
04_sql_loader.py      ← Load CSVs into SQLite; run SQL in business_queries.sql
   │
   ▼
Power BI              ← 3-page dashboard (Overview | Products | Segmentation)
   │
   ▼
Business Insights + Recommendations  (docs/business_insights.md)
```

---

## Folder Structure

```
E-Commerce Sales and Customer Behavior Analysis/
│
├── data/
│   ├── raw/
│   │   └── online_retail_II.xlsx        ← download from Kaggle
│   └── processed/
│       ├── cleaned_retail.csv
│       └── rfm_segments.csv
│
├── scripts/
│   ├── 01_data_cleaning.py
│   ├── 02_eda.py
│   ├── 03_rfm_analysis.py
│   └── 04_sql_loader.py
│
├── sql/
│   └── business_queries.sql
│
├── reports/
│   ├── 00_kpi_summary.csv
│   ├── 01_monthly_revenue_trend.png
│   ├── 02_top_countries_revenue.png
│   ├── 03_top_products.png
│   ├── 04_revenue_by_dow.png
│   ├── 05_revenue_by_hour.png
│   ├── 06_order_value_distribution.png
│   ├── 07_quarterly_revenue.png
│   ├── 08_correlation_heatmap.png
│   ├── 09_rfm_segment_distribution.png
│   ├── 10_rfm_heatmap.png
│   └── 11_rfm_scatter.png
│
├── powerbi/
│   └── dashboard_design_guide.txt
│
├── docs/
│   ├── business_insights.md
│   ├── resume_bullets.md
│   └── interview_questions.md
│
├── requirements.txt
└── README.md
```

---

## KPIs Tracked

| KPI | Description |
|-----|-------------|
| Total Revenue (£) | Sum of all transaction values |
| Total Orders | Count of unique invoices |
| Total Customers | Count of unique customer IDs |
| Average Order Value | Revenue ÷ Orders |
| Repeat Customer Rate | % customers with >1 order |
| Revenue by Country | Geographic split |
| Top Products | By units & revenue |
| Monthly Growth Rate | MoM revenue % change |
| RFM Segments | 8-tier customer classification |

---

## Tools & Libraries

| Tool | Purpose |
|------|---------|
| Python (Pandas, NumPy) | Data cleaning & feature engineering |
| Matplotlib / Seaborn | Exploratory visualisations |
| SQLite / SQL | Business queries |
| Power BI Desktop | Interactive dashboard |
| Excel | Stakeholder reporting |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/ecommerce-ba-portfolio.git
cd ecommerce-ba-portfolio

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download dataset and place in data/raw/

# 4. Run pipeline in order
python scripts/01_data_cleaning.py
python scripts/02_eda.py
python scripts/03_rfm_analysis.py
python scripts/04_sql_loader.py

# 5. Open Power BI → connect to data/processed/ CSVs
#    Follow powerbi/dashboard_design_guide.txt
```

---

## Key Findings (sample)

- **November–December** is the highest-revenue period — holiday season spike
- **United Kingdom** accounts for ~85% of total revenue
- **Champions segment** (top 8% of customers) drive ~40% of revenue
- **At-Risk customers** have 3× higher lifetime value than average — re-engage via email
- **Thursday 10–12 AM** is peak shopping window — best time for promotional emails

---

## License

This project uses a public dataset. Code is open-source under the MIT License.

---

*Built as a Business Analyst portfolio project | Tools: Python · SQL · Power BI · Excel*
