"""
TRANSFORM stage
----------------
Standardises the inconsistent column names, date formats, and decimal
separators from each retailer into one unified schema:

    sale_date (YYYY-MM-DD), sku, units_sold, unit_price_eur, source_retailer

In the real pipeline, this logic runs inside the AWS Step Functions
workflow and writes the standardised output back to S3 as query-ready
Parquet/CSV for Amazon Athena.
"""

import pandas as pd

from extract import extract_all


# Column-mapping "recipes" per retailer file pattern. In the real pipeline
# these mappings grow over time as new retailer formats are onboarded.
RETAILER_SCHEMAS = {
    "retailer_a_sales.csv": {
        "columns": {"Date": "sale_date", "Product_SKU": "sku",
                    "Units_Sold": "units_sold", "Unit_Price_EUR": "unit_price_eur"},
        "date_format": "%Y-%m-%d",
        "decimal_comma": False,
    },
    "retailer_b_sales.csv": {
        "columns": {"Datum": "sale_date", "Artikelnummer": "sku",
                    "Menge": "units_sold", "Preis": "unit_price_eur"},
        "date_format": "%d.%m.%Y",
        "decimal_comma": True,
    },
    "retailer_c_sales.xlsx": {
        "columns": {"sale_date": "sale_date", "sku": "sku",
                    "qty": "units_sold", "price_each": "unit_price_eur"},
        "date_format": "%m/%d/%Y",
        "decimal_comma": False,
    },
}


def standardise(filename: str, df: pd.DataFrame) -> pd.DataFrame:
    schema = RETAILER_SCHEMAS[filename]

    df = df.rename(columns=schema["columns"])
    df = df[list(schema["columns"].values())]

    if schema["decimal_comma"]:
        df["unit_price_eur"] = (
            df["unit_price_eur"].astype(str).str.replace(",", ".").astype(float)
        )

    df["sale_date"] = pd.to_datetime(df["sale_date"], format=schema["date_format"])
    df["sale_date"] = df["sale_date"].dt.strftime("%Y-%m-%d")

    df["source_retailer"] = filename.replace("_sales.csv", "").replace("_sales.xlsx", "")

    # basic data-quality checks (a lightweight version of what the real
    # pipeline does to catch malformed rows before they hit the warehouse)
    before = len(df)
    df = df.dropna(subset=["sale_date", "sku", "units_sold", "unit_price_eur"])
    df = df[(df["units_sold"] > 0) & (df["unit_price_eur"] > 0)]
    dropped = before - len(df)
    if dropped:
        print(f"  {filename}: dropped {dropped} invalid rows during validation")

    return df


def transform_all() -> pd.DataFrame:
    extracted = extract_all()
    standardised_frames = []

    for filename, df in extracted.items():
        if filename not in RETAILER_SCHEMAS:
            print(f"No schema mapping for {filename}, skipping")
            continue
        standardised_frames.append(standardise(filename, df))

    unified = pd.concat(standardised_frames, ignore_index=True)
    unified["total_revenue_eur"] = (
        unified["units_sold"] * unified["unit_price_eur"]
    ).round(2)

    print(f"\nUnified dataset: {len(unified)} rows across "
          f"{unified['source_retailer'].nunique()} retailers")
    return unified


if __name__ == "__main__":
    result = transform_all()
    print(result.head())
