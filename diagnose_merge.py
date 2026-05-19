# File: diagnose_merge.py
import pandas as pd
import geopandas as gpd

inc = pd.read_csv("data/cleaned/acs_income_cleaned.csv", dtype=str)
pop = pd.read_csv("data/cleaned/acs_population_cleaned.csv", dtype=str)
tracts = gpd.read_file("data/cleaned/census_tracts_cleaned.geojson")

print("Income rows:", len(inc))
print(" Income sample GEOIDs:", inc.GEOID.iloc[:5].tolist())
print("Population rows:", len(pop))
print(" Pop sample GEOIDs:", pop.GEOID.iloc[:5].tolist())
print("Tracts rows:", len(tracts))
print(" Tracts sample GEOIDs:", tracts.GEOID.iloc[:5].tolist())
