import geopandas as gpd
import os

# ── Define Input and Output File Paths ───────────────────────────
# Input: GeoJSON file with enriched candidate EV charging sites
in_path = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\processed\candidate_sites_enriched.geojson"

# Output: GeoJSON file where demand scores will be saved
out_path = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\processed\candidate_sites_scored.geojson"

# Ensure that the output directory exists
os.makedirs(os.path.dirname(out_path), exist_ok=True)

# ── Load Enriched Candidate Sites ────────────────────────────────
# Read the input GeoJSON into a GeoDataFrame
gdf = gpd.read_file(in_path)

# ── Calculate Demand Score for Each Site ─────────────────────────
# Ensure that 'AADT' (Average Annual Daily Traffic) and 'population' columns are numeric
gdf["AADT"] = gdf["AADT"].astype(float)
gdf["population"] = gdf["population"].astype(float)

# Calculate demand score as the product of AADT and population
gdf["demand_score"] = gdf["AADT"] * gdf["population"]

# ── Save Updated GeoDataFrame to Output File ─────────────────────
# Write the updated GeoDataFrame with demand scores to a new GeoJSON file
gdf.to_file(out_path, driver="GeoJSON")

# Print success message with number of processed sites and output file location
print(f"✅ Demand score added for {len(gdf)} sites →\n  {out_path}")
