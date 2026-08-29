"""
Generates sample "retailer" sales export files in a few different, messy
formats (different column names, date formats, delimiters) to simulate the
kind of inconsistent inputs a real multi-retailer ingestion pipeline has
to standardise.

None of this represents any real retailer or company data - it's purely
synthetic, for demonstration purposes.
"""

import os
import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(1)
os.makedirs("sample_inputs", exist_ok=True)

PRODUCTS = ["SKU-1001", "SKU-1002", "SKU-1003", "SKU-1004"]


def random_dates(n, start="2026-01-01"):
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    return [start_dt + timedelta(days=random.randint(0, 60)) for _ in range(n)]


# Retailer A: clean-ish CSV, ISO dates
rows_a = []
for d in random_dates(40):
    rows_a.append({
        "Date": d.strftime("%Y-%m-%d"),
        "Product_SKU": random.choice(PRODUCTS),
        "Units_Sold": random.randint(1, 50),
        "Unit_Price_EUR": round(random.uniform(9.99, 49.99), 2),
    })
pd.DataFrame(rows_a).to_csv("sample_inputs/retailer_a_sales.csv", index=False)


# Retailer B: European date format, semicolon delimiter, German column names
rows_b = []
for d in random_dates(35):
    rows_b.append({
        "Datum": d.strftime("%d.%m.%Y"),
        "Artikelnummer": random.choice(PRODUCTS),
        "Menge": random.randint(1, 50),
        "Preis": str(round(random.uniform(9.99, 49.99), 2)).replace(".", ","),
    })
pd.DataFrame(rows_b).to_csv("sample_inputs/retailer_b_sales.csv", index=False, sep=";")


# Retailer C: Excel export with an extra header row and different structure
rows_c = []
for d in random_dates(30):
    rows_c.append({
        "sale_date": d.strftime("%m/%d/%Y"),
        "sku": random.choice(PRODUCTS),
        "qty": random.randint(1, 50),
        "price_each": round(random.uniform(9.99, 49.99), 2),
        "currency": "EUR",
    })
df_c = pd.DataFrame(rows_c)
with pd.ExcelWriter("sample_inputs/retailer_c_sales.xlsx") as writer:
    df_c.to_excel(writer, index=False, startrow=2)  # simulate an extra header block

print("Generated 3 sample retailer files in ./sample_inputs/")
