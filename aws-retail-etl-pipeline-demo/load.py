"""
LOAD stage
----------
Writes the unified, standardised dataset to a query-ready output.

In the real pipeline this stage writes partitioned Parquet files to S3,
which are then queried directly through Amazon Athena for price and
sellout reporting. Here, it writes a local CSV/Parquet to demonstrate
the same "query-ready" output shape.
"""

import pandas as pd
from transform import transform_all


def load(df: pd.DataFrame, output_dir: str = "warehouse"):
    import os
    os.makedirs(output_dir, exist_ok=True)

    csv_path = f"{output_dir}/sales_unified.csv"
    parquet_path = f"{output_dir}/sales_unified.parquet"

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"Loaded {len(df)} rows -> {csv_path}")
    print(f"Loaded {len(df)} rows -> {parquet_path} (Athena/Glue-ready)")


if __name__ == "__main__":
    unified = transform_all()
    load(unified)
