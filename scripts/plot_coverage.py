# scripts/plot_coverage.py

import os
import geopandas as gpd
import matplotlib.pyplot as plt

# 1. Locate project root (one level up from this script)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# 2. Paths to data and output
TRACT_FILE = os.path.join(PROJECT_ROOT, "data", "cleaned",   "census_tracts_cleaned.geojson")
OPT_FILE   = os.path.join(PROJECT_ROOT, "data", "processed", "optimal_sites_coverage.geojson")
FIG_DIR    = os.path.join(PROJECT_ROOT, "figures")
FIG_PATH   = os.path.join(FIG_DIR, "coverage_map.png")

# 3. Make sure figures folder exists
os.makedirs(FIG_DIR, exist_ok=True)

# 4. Load GeoDataFrames
tracts = gpd.read_file(TRACT_FILE).to_crs(epsg=4326)
opt    = gpd.read_file(OPT_FILE).to_crs(epsg=4326)

# 5. Plot
fig, ax = plt.subplots(figsize=(8, 8))
tracts.boundary.plot(ax=ax, linewidth=0.5)
opt.plot(ax=ax, marker='o', markersize=40)

ax.set_title("Coverage‑MVP: EV Charger Sites in Washington, DC")
ax.set_axis_off()
plt.tight_layout()

# 6. Save the figure
fig.savefig(FIG_PATH, dpi=300)
print(f"✅ Map saved to {FIG_PATH}")

# 7. Show on screen
plt.show()
