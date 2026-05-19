# scripts/select_top_sites.py

import geopandas as gpd
import os

# ─── CONFIGURATION ────────────────────────────────────────
N_SITES    = 50
INPUT      = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\processed\candidate_sites_prepped.geojson"
OUTPUT     = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\processed\optimal_sites.geojson"

# make sure output folder exists
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# ─── LOAD & PICK TOP‑N ────────────────────────────────────
gdf = gpd.read_file(INPUT)

# sort by demand_score descending and take the top N_SITES
top50 = gdf.sort_values("demand_score", ascending=False).head(N_SITES)

# ─── SAVE RESULTS ────────────────────────────────────────
top50.to_file(OUTPUT, driver="GeoJSON")
print(f"✅ Greedy MVP: selected {len(top50)} sites → {OUTPUT}")
