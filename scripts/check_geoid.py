import os
import pandas as pd
import geopandas as gpd

# ── Locate Project Root Directory ─────────────────────────────────
# Get the absolute path to the project's root directory
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# ── Load Cleaned Data Files ───────────────────────────────────────
# Load cleaned population data (ACS - American Community Survey)
pop = pd.read_csv(os.path.join(ROOT, "data", "cleaned", "acs_population_cleaned.csv"))

# Load cleaned income data (ACS)
inc = pd.read_csv(os.path.join(ROOT, "data", "cleaned", "acs_income_cleaned.csv"))

# Load cleaned census tract geometries
tracts = gpd.read_file(os.path.join(ROOT, "data", "cleaned", "census_tracts_cleaned.geojson"))

# ── Inspect Loaded Data ──────────────────────────────────────────
# Print column names of each loaded dataset to verify successful loading and structure
print("Population columns:", pop.columns.tolist())
print("Income     columns:", inc.columns.tolist())
print("Tracts     columns:", tracts.columns.tolist())
