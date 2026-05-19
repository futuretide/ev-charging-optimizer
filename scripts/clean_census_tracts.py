import geopandas as gpd
import os

# Input and output paths
input_path = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\raw\census_tracts\tl_2022_11_tract.shp"
output_path = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\cleaned\census_tracts_cleaned.geojson"

# Load the shapefile
gdf = gpd.read_file(input_path)
print("✅ Shapefile loaded.")

# Keep only useful columns
gdf_cleaned = gdf[["GEOID", "geometry"]].copy()
print("🧹 Cleaned columns:", gdf_cleaned.columns.tolist())

# Ensure output folder exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Save as GeoJSON
gdf_cleaned.to_file(output_path, driver="GeoJSON")
print(f"✅ Cleaned shapefile saved to: {output_path}")
