import geopandas as gpd
import os

# ── Define the Shapefile Path ────────────────────────────────────
# Absolute path to the census tracts shapefile
shapefile_path = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\raw\census_tracts\tl_2022_11_tract.shp"

# ── Load the Shapefile ──────────────────────────────────────────
# Read the shapefile into a GeoDataFrame using GeoPandas
gdf = gpd.read_file(shapefile_path)

# ── Output Information ───────────────────────────────────────────
# Notify that the shapefile has been successfully loaded
print("✅ Census tract shapefile loaded.")

# Print the list of column names available in the GeoDataFrame
print("🧾 Columns:", list(gdf.columns))

# Display the first 5 rows of the GeoDataFrame to inspect the data
print("📍 First 5 rows:")
print(gdf.head())
