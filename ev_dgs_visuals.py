# ev_dgs_visuals.py

import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path

# 1) Base directory & file paths
BASE = Path(__file__).resolve().parent
TRACTS_FP = BASE/'data'/'cleaned'/'merged_data.geojson'
CAND_FP   = BASE/'data'/'processed'/'candidate_sites_prepped.geojson'
OPT_FP    = BASE/'data'/'processed'/'optimal_sites_dgal.geojson'

# 2) Load tracts (this sets our CRS)
gdf_tracts = gpd.read_file(TRACTS_FP)
tract_crs  = gdf_tracts.crs

# 3) Load & reproject candidates + optimals
gdf_cand = gpd.read_file(CAND_FP).to_crs(tract_crs)
gdf_opt  = gpd.read_file(OPT_FP).to_crs(tract_crs)

# ——————————————————————————————————————————————————————————————
# 1. Choropleth of demand proxy (population × income)
# ——————————————————————————————————————————————————————————————
gdf_tracts['demand'] = gdf_tracts['population'] * gdf_tracts['median_income']
fig, ax = plt.subplots(figsize=(8, 6))
gdf_tracts.plot(
    column='demand',
    cmap='viridis',
    legend=True,
    legend_kwds={'label': "Population × Income"},
    ax=ax
)
ax.set_title('Demand Proxy by Census Tract')
ax.set_axis_off()
fig.savefig(BASE/'choropleth_demand.png', dpi=300)
plt.close(fig)

# ——————————————————————————————————————————————————————————————
# 2. Map of pre‐filtered candidates
# ——————————————————————————————————————————————————————————————
fig, ax = plt.subplots(figsize=(8, 6))
gdf_tracts.boundary.plot(ax=ax, color='lightgray', linewidth=0.5)
gdf_cand.plot(ax=ax, markersize=5, color='blue', alpha=0.6)
ax.set_title(f"{len(gdf_cand)} Pre‐filtered Candidate Sites")
ax.set_axis_off()
fig.savefig(BASE/'candidates_map.png', dpi=300)
plt.close(fig)

# ——————————————————————————————————————————————————————————————
# 3. Map of optimal sites
# ——————————————————————————————————————————————————————————————
fig, ax = plt.subplots(figsize=(8, 6))
gdf_tracts.boundary.plot(ax=ax, color='lightgray', linewidth=0.5)
gdf_opt.plot(ax=ax, markersize=20, color='red', marker='*')
ax.set_title(f"{len(gdf_opt)} Optimal Sites Selected")
ax.set_axis_off()
fig.savefig(BASE/'optimal_sites_map.png', dpi=300)
plt.close(fig)

# ——————————————————————————————————————————————————————————————
# 4. Coverage heatmap (covered vs uncovered)
# ——————————————————————————————————————————————————————————————
# Spatial‐join: mark which tracts contain at least one optimal site
joined = gpd.sjoin(gdf_tracts, gdf_opt[['geometry']], how='left', predicate='contains')
gdf_tracts['covered'] = joined['index_right'].notnull()

fig, ax = plt.subplots(figsize=(8, 6))
gdf_tracts.plot(
    column='covered',
    categorical=True,
    legend=True,
    legend_kwds={'title': 'Covered'},
    ax=ax
)
ax.set_title('Coverage by Tract (Covered vs Uncovered)')
ax.set_axis_off()
fig.savefig(BASE/'coverage_heatmap.png', dpi=300)
plt.close(fig)

print("✅ All visuals generated in the project root:")
print("   • choropleth_demand.png")
print("   • candidates_map.png")
print("   • optimal_sites_map.png")
print("   • coverage_heatmap.png")
