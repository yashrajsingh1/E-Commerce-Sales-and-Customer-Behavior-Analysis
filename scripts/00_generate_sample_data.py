# =============================================================================
# Synthetic Data Generator
# Generates a realistic fake Online Retail II dataset for demo/testing.
# Replace data/raw/online_retail_II.xlsx with the real Kaggle file later.
# =============================================================================
import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs("data/raw", exist_ok=True)

N = 200_000   # number of transaction rows

# --- REFERENCE DATA ---
products = [
    ("85123A", "White Hanging Heart T-Light Holder", 2.55),
    ("22423",  "Regency Cakestand 3 Tier",           12.75),
    ("85099B", "Jumbo Bag Red Retrospot",              4.25),
    ("84879",  "Assorted Colour Bird Ornament",        1.69),
    ("47566",  "Party Bunting",                        4.95),
    ("20725",  "Lunch Bag Red Retrospot",              1.85),
    ("22720",  "Set Of 3 Cake Tins Pantry Design",    4.95),
    ("POST",   "Postage",                              18.0),
    ("22197",  "Popcorn Holder",                       0.85),
    ("84997B", "Pink 3 Tier Cake Tin",                27.95),
    ("21929",  "Jumbo Bag Pink Polkadot",              1.65),
    ("22086",  "Paper Chain Kit 50s Christmas",        2.55),
    ("21980",  "Skull Shoulder Bag",                   1.65),
    ("22111",  "Scottie Dog Hot Water Bottle",        4.25),
    ("21212",  "Pack of 72 Retrospot Cake Cases",      0.42),
    ("22457",  "Natural Slate Heart Chalkboard",       1.25),
    ("22469",  "Heart Of Wicker Small",                1.65),
    ("79321",  "Chilli Lights",                        8.50),
    ("22090",  "Paper Bunting White Lace",             2.95),
    ("21977",  "Assorted Cactus Notebook",             1.45),
]

countries = [
    ("United Kingdom", 0.82),
    ("Germany",        0.04),
    ("France",         0.04),
    ("EIRE",           0.02),
    ("Spain",          0.01),
    ("Netherlands",    0.01),
    ("Belgium",        0.01),
    ("Switzerland",    0.01),
    ("Portugal",       0.01),
    ("Australia",      0.01),
    ("Norway",         0.01),
    ("Denmark",        0.005),
    ("Sweden",         0.005),
]

country_names = [c[0] for c in countries]
country_probs = [c[1] for c in countries]
country_probs[-1] += 1 - sum(country_probs)   # normalise

# Weighted product selection (some sell more)
prod_weights = np.array([0.10,0.08,0.09,0.07,0.06,0.08,0.06,
                          0.03,0.07,0.04,0.05,0.05,0.04,0.05,
                          0.04,0.03,0.03,0.04,0.03,0.05])
prod_weights /= prod_weights.sum()

# --- GENERATE ---
print("Generating synthetic transaction data …")

# Date range: Dec 2009 – Dec 2011
date_range = pd.date_range("2009-12-01", "2011-12-09", freq="h")

# Seasonal weight — boost Nov/Dec
month_weights = {1:0.7,2:0.7,3:0.8,4:0.8,5:0.9,6:0.9,
                 7:0.85,8:0.85,9:0.95,10:1.0,11:1.5,12:1.6}
hour_weights   = {h: (1.5 if 9<=h<=15 else 0.4 if h<7 or h>20 else 1.0)
                  for h in range(24)}

# Build timestamp distribution
ts_weights = np.array([
    month_weights.get(d.month, 1.0) * hour_weights.get(d.hour, 1.0)
    for d in date_range
])
ts_weights /= ts_weights.sum()

timestamps = np.random.choice(date_range, size=N, p=ts_weights)

# Customer IDs: 4,500 customers with power-law frequency
customer_ids = np.random.zipf(1.5, size=N) % 4000 + 12000

# Invoice numbers: group ~5 rows per invoice
invoice_ids = np.repeat(np.arange(10000, 10000 + N // 5 + 1),
                        repeats=5)[:N]
invoice_ids = [f"{i}" for i in invoice_ids]

# Add ~3% cancellations
cancel_mask = np.random.random(N) < 0.03
for i in range(N):
    if cancel_mask[i]:
        invoice_ids[i] = "C" + invoice_ids[i]

# Product selection
prod_indices = np.random.choice(len(products), size=N, p=prod_weights)
stock_codes   = [products[i][0] for i in prod_indices]
descriptions  = [products[i][1] for i in prod_indices]
base_prices   = np.array([products[i][2] for i in prod_indices])

# Quantities: mostly 1–12, occasional bulk
quantities = np.where(
    np.random.random(N) < 0.05,
    np.random.randint(50, 300, N),
    np.random.randint(1, 12, N)
)
quantities[cancel_mask] = -quantities[cancel_mask]   # negative for cancellations

# Price: add small noise
prices = (base_prices * np.random.uniform(0.9, 1.1, N)).round(2)

# Countries
chosen_countries = np.random.choice(country_names, size=N, p=country_probs)

# Missing CustomerID (~20%)
cust_ids = customer_ids.astype(float)
cust_ids[np.random.random(N) < 0.20] = np.nan

df = pd.DataFrame({
    "Invoice":     invoice_ids,
    "StockCode":   stock_codes,
    "Description": descriptions,
    "Quantity":    quantities,
    "InvoiceDate": timestamps,
    "Price":       prices,
    "Customer ID": cust_ids,
    "Country":     chosen_countries,
})

df.sort_values("InvoiceDate", inplace=True)
df.reset_index(drop=True, inplace=True)

# Save as XLSX (the format the cleaning script expects)
output = "data/raw/online_retail_II.xlsx"
print(f"Saving {len(df):,} rows to {output} …")
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Year 2010-2011", index=False)

print(f"Done. File size: {os.path.getsize(output)/1e6:.1f} MB")
print(f"Rows: {len(df):,}  |  Columns: {df.shape[1]}")
print(df.head(3).to_string())
