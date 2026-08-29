"""
EXTRACT stage
-------------
In the real pipeline, this stage runs as an AWS Lambda function triggered
by new files landing in an S3 bucket (uploaded via an automated Outlook
connector that retrieves retailer email attachments, including
password-protected ones). Here, it simply reads local sample files to
demonstrate the same extraction and file-type routing logic.
"""

import os
import pandas as pd


RAW_DIR = "sample_inputs"
STAGED_DIR = "staged"


def extract_all(raw_dir: str = RAW_DIR) -> dict:
    """Reads every raw retailer file and returns {filename: DataFrame}."""
    os.makedirs(STAGED_DIR, exist_ok=True)
    extracted = {}

    for filename in os.listdir(raw_dir):
        path = os.path.join(raw_dir, filename)

        if filename.endswith(".csv"):
            # try comma first, fall back to semicolon (common in EU exports)
            try:
                df = pd.read_csv(path)
                if df.shape[1] == 1:
                    raise ValueError("likely wrong delimiter")
            except (pd.errors.ParserError, ValueError):
                df = pd.read_csv(path, sep=";")

        elif filename.endswith(".xlsx"):
            # some retailer exports have a junk header block before the real table
            df = pd.read_excel(path, skiprows=2)

        else:
            print(f"Skipping unrecognised file type: {filename}")
            continue

        extracted[filename] = df
        print(f"Extracted {filename}: {df.shape[0]} rows, {df.shape[1]} columns")

    return extracted


if __name__ == "__main__":
    extract_all()
