# =============================================================================
# Step 1: Data Cleaning
# Project : E-Commerce Sales and Customer Behavior Analysis
# Dataset : Online Retail II (UCI Machine Learning Repository)
#           https://archive.ics.uci.edu/ml/datasets/Online+Retail+II
# Author  : [Your Name]
# =============================================================================
# HOW TO GET THE DATASET
# 1. Go to: https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci
# 2. Download "online_retail_II.xlsx"
# 3. Place it inside:  data/raw/online_retail_II.xlsx
# =============================================================================

import pandas as pd
import numpy as np
import os

# ------------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------------
RAW_PATH       = "data/raw/online_retail_II.xlsx"
PROCESSED_PATH = "data/processed/cleaned_retail.csv"

print("Loading dataset … (this may take 30–60 seconds for a large xlsx)")
sheet1 = pd.read_excel(RAW_PATH, sheet_name="Year 2009-2010", engine="openpyxl")
sheet2 = pd.read_excel(RAW_PATH, sheet_name="Year 2010-2011", engine="openpyxl")
df = pd.concat([sheet1, sheet2], ignore_index=True)
print(f"  Sheet 1 (2009-2010): {len(sheet1):,} rows")
print(f"  Sheet 2 (2010-2011): {len(sheet2):,} rows")

print(f"\nRaw shape : {df.shape}")
print(df.head())
print("\nColumn dtypes:\n", df.dtypes)
print("\nMissing values:\n", df.isnull().sum())

# ------------------------------------------------------------------
# 2. RENAME COLUMNS  (standard snake_case)
# ------------------------------------------------------------------
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
# Expected columns after rename:
# invoice, stockcode, description, quantity, invoicedate,
# price, customer_id, country

print("\nRenamed columns:", df.columns.tolist())

# ------------------------------------------------------------------
# 3. REMOVE DUPLICATES
# ------------------------------------------------------------------
before = len(df)
df.drop_duplicates(inplace=True)
print(f"\nDuplicates removed : {before - len(df)}")

# ------------------------------------------------------------------
# 4. HANDLE MISSING VALUES
# ------------------------------------------------------------------
# Drop rows where customer_id is missing (we can't do RFM without it)
df.dropna(subset=["customer_id"], inplace=True)

# Drop rows where description is missing
df.dropna(subset=["description"], inplace=True)

print(f"Shape after dropping nulls : {df.shape}")

# ------------------------------------------------------------------
# 5. FIX DATA TYPES
# ------------------------------------------------------------------
df["customer_id"]  = df["customer_id"].astype(int)
df["invoicedate"]  = pd.to_datetime(df["invoicedate"])
df["quantity"]     = pd.to_numeric(df["quantity"], errors="coerce")
df["price"]        = pd.to_numeric(df["price"],    errors="coerce")

# ------------------------------------------------------------------
# 6. REMOVE INVALID RECORDS
# ------------------------------------------------------------------
# Cancelled orders start with 'C'
cancelled = df["invoice"].astype(str).str.startswith("C")
print(f"\nCancelled orders found : {cancelled.sum()}")
df = df[~cancelled]

# Remove negative / zero quantity or price (data errors)
df = df[(df["quantity"] > 0) & (df["price"] > 0)]

print(f"Shape after removing invalid records : {df.shape}")

# ------------------------------------------------------------------
# 7. ENGINEER NEW COLUMNS
# ------------------------------------------------------------------
df["total_sales"]  = df["quantity"] * df["price"]          # revenue per line
df["year"]         = df["invoicedate"].dt.year
df["month"]        = df["invoicedate"].dt.month
df["month_name"]   = df["invoicedate"].dt.strftime("%b")
df["day_of_week"]  = df["invoicedate"].dt.day_name()
df["hour"]         = df["invoicedate"].dt.hour
df["quarter"]      = df["invoicedate"].dt.quarter

# ------------------------------------------------------------------
# 8. STANDARDISE TEXT COLUMNS
# ------------------------------------------------------------------
df["description"] = df["description"].str.strip().str.title()
df["country"]     = df["country"].str.strip()

# ------------------------------------------------------------------
# 9. OUTLIER TREATMENT  (IQR capping on total_sales)
# ------------------------------------------------------------------
Q1  = df["total_sales"].quantile(0.25)
Q3  = df["total_sales"].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers = ((df["total_sales"] < lower) | (df["total_sales"] > upper)).sum()
print(f"\nOutliers detected in total_sales : {outliers}")

# Cap (winsorise) rather than drop so we keep the order
df["total_sales"] = df["total_sales"].clip(lower=lower, upper=upper)

# ------------------------------------------------------------------
# 10. SAVE CLEANED DATA
# ------------------------------------------------------------------
os.makedirs("data/processed", exist_ok=True)
df.to_csv(PROCESSED_PATH, index=False)
print(f"\nCleaned data saved -> {PROCESSED_PATH}")
print(f"Final shape : {df.shape}")

# ------------------------------------------------------------------
# 11. QUICK SUMMARY REPORT
# ------------------------------------------------------------------
print("\n" + "="*50)
print("DATA QUALITY SUMMARY")
print("="*50)
print(f"Total transactions  : {len(df):,}")
print(f"Unique customers    : {df['customer_id'].nunique():,}")
print(f"Unique products     : {df['stockcode'].nunique():,}")
print(f"Countries covered   : {df['country'].nunique():,}")
print(f"Date range          : {df['invoicedate'].min().date()} -> {df['invoicedate'].max().date()}")
print(f"Total revenue (£)   : {df['total_sales'].sum():,.2f}")
print("="*50)
