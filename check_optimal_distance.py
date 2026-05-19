import geopandas as gpd

# Load
opt   = gpd.read_file("data/processed/optimal_sites_dgal.geojson")
stns  = gpd.read_file("data/raw/dc_stations.geojson").to_crs(opt.crs)

# For each optimal site, compute distance to nearest station
from scipy.spatial import cKDTree
coords_opt = [(p.x, p.y) for p in opt.geometry]
coords_stn = [(p.x, p.y) for p in stns.geometry]
tree = cKDTree(coords_stn)
dists, _ = tree.query(coords_opt, k=1)

min_dist = dists.min()
print(f"Minimum distance from any optimal site to an existing station: {min_dist:.1f} m")
assert min_dist >= 500, "ERROR: Some optimal sites are too close to existing stations!"
