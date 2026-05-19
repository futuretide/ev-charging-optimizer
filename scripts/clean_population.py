# File: scripts/clean_population.py

import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_POP     = os.path.join(ROOT, "data", "raw", "population", "ACSDT5Y2022.B01003-Data.csv")
CLEANED_POP = os.path.join(ROOT, "data", "cleaned", "acs_population_cleaned.csv")

def main():
    # 1. Load, skipping that second metadata row
    df = pd.read_csv(RAW_POP, skiprows=[1], dtype=str)

    # 2. Rename columns
    df = df.rename(columns={
        "GEO_ID": "GEOID",
        "B01003_001E": "population"
    })

    # 3. Trim down to the last 11 characters (drop the 1400000US prefix)
    df["GEOID"] = df["GEOID"].str.strip().str[-11:]

    # 4. Convert population to numeric (non-numeric → NaN), then drop NaNs
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df = df.dropna(subset=["population"])

    # 5. Keep only valid 11-digit GEOIDs
    df = df[df["GEOID"].str.match(r"^\d{11}$")]

    # 6. Subset and write
    df_clean = df[["GEOID", "population"]]
    os.makedirs(os.path.dirname(CLEANED_POP), exist_ok=True)
    df_clean.to_csv(CLEANED_POP, index=False)
    print(f"✅ Cleaned population saved to {CLEANED_POP} ({len(df_clean)} rows)")

if __name__ == "__main__":
    main()
