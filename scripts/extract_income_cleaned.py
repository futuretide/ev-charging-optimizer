# File: scripts/extract_income_cleaned.py

import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_INCOME     = os.path.join(ROOT, "data", "raw", "acs_income", "ACSST5Y2022.S1901-Data.csv")
CLEANED_INCOME = os.path.join(ROOT, "data", "cleaned", "acs_income_cleaned.csv")

def main():
    # Skip the second row (labels) so we only get real data
    df = pd.read_csv(RAW_INCOME, skiprows=[1])

    # Rename and pull only the fields we need
    df = df.rename(columns={
        "GEO_ID": "GEOID",
        "S1901_C01_001E": "median_income"
    })

    # Drop the “00Geography” entry and any non-tract codes
    # Extract the last 11 characters so that “1400000US11001000101” → “11001000101”
    df["GEOID"] = df["GEOID"].astype(str).str.strip().str[-11:]

    df_clean = df[["GEOID", "median_income"]].copy()
    df_clean["median_income"] = pd.to_numeric(df_clean["median_income"], errors="coerce")

    os.makedirs(os.path.dirname(CLEANED_INCOME), exist_ok=True)
    df_clean.to_csv(CLEANED_INCOME, index=False)
    print(f"✅ Cleaned income saved to {CLEANED_INCOME}")

if __name__ == "__main__":
    main()
