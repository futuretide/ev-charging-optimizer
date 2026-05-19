import geopandas as gpd
from shapely.geometry import Point
import os, pandas as pd

streets_path = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\raw\streets\Roadway_Block.shp"
out_path     = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\processed\candidate_sites_raw.geojson"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

streets = gpd.read_file(streets_path)[["geometry"]].to_crs("EPSG:3857")

# endpoints of each segment
endpts = [Point(c) for g in streets.geometry for c in (g.coords[0], g.coords[-1])]
end_gdf = gpd.GeoDataFrame(geometry=endpts, crs=streets.crs)
end_gdf["x"] = end_gdf.geometry.x.round()
end_gdf["y"] = end_gdf.geometry.y.round()

# degree of each node
counts = end_gdf.groupby(["x", "y"]).size().reset_index(name="degree")

# keep nodes with degree ≥ 2, then create geometry
nodes_df = counts[counts["degree"] >= 2].copy()
nodes_df["geometry"] = gpd.points_from_xy(nodes_df["x"], nodes_df["y"], crs=streets.crs)
nodes = gpd.GeoDataFrame(nodes_df, geometry="geometry").to_crs("EPSG:4326")

nodes[["degree", "geometry"]].to_file(out_path, driver="GeoJSON")
print(f"✅ {len(nodes)} candidate points saved → {out_path}")
