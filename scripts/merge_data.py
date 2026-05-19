# File: scripts/merge_data.py

import os
import pandas as pd
import geopandas as gpd

# 1. Locate project root (one level up from this script file)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 2. Define paths
INCOME_CLEAN = os.path.join(ROOT, "data", "cleaned", "acs_income_cleaned.csv")
POP_CLEAN    = os.path.join(ROOT, "data", "cleaned", "acs_population_cleaned.csv")
TRACTS_CLEAN = os.path.join(ROOT, "data", "cleaned", "census_tracts_cleaned.geojson")
MERGED_OUT   = os.path.join(ROOT, "data", "cleaned", "merged_data.geojson")

# 3. Load cleaned datasets
income = pd.read_csv(INCOME_CLEAN, dtype=str)
pop    = pd.read_csv(POP_CLEAN,    dtype=str)
tracts = gpd.read_file(TRACTS_CLEAN)

# 4. Normalize GEOID to 11‐character strings everywhere
for df in (income, pop):
    df["GEOID"] = df["GEOID"].astype(str).str.strip().str.zfill(11)
tracts["GEOID"] = tracts["GEOID"].astype(str).str.zfill(11)

# 5. Convert numeric fields back to numbers
income["median_income"] = pd.to_numeric(income["median_income"], errors="coerce")
pop   ["population"]    = pd.to_numeric(pop   ["population"],    errors="coerce")

# 6. Merge: start from tracts so geometry is preserved
merged = (
    tracts
    .merge(income, on="GEOID", how="left")
    .merge(pop,    on="GEOID", how="left")
)

# 7. Report any missing values
print(f"Tracts total:             {len(merged)}")
print(f"Missing median_income:    {merged['median_income'].isna().sum()}")
print(f"Missing population:       {merged['population'].isna().sum()}")

# 8. Save to GeoJSON
os.makedirs(os.path.dirname(MERGED_OUT), exist_ok=True)
merged.to_file(MERGED_OUT, driver="GeoJSON")
print(f"✅ Merged file saved → {MERGED_OUT}")
