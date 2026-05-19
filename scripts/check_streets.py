import geopandas as gpd
from pathlib import Path

STREETS_PATH = Path(
    r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\raw\streets\Roadway_Block.shp"
)

try:
    streets = gpd.read_file(STREETS_PATH)
    print(f"✅ Loaded {len(streets)} street segments")
    print("📌 Columns:", list(streets.columns)[:10])
    print(streets.head())
except Exception as e:
    print("❌ Could not read shapefile:", e)
