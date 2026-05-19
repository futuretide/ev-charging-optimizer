import geopandas as gpd

# Absolute path to your traffic shapefile
TRAFFIC_PATH = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\raw\traffic\2023_Traffic_Volume.shp"

try:
    traffic = gpd.read_file(TRAFFIC_PATH)
    print(f"✅ Loaded {len(traffic)} rows from traffic shapefile.")
    print("📌 Columns available:")
    print(list(traffic.columns))
    
    # Show a few rows with AADT and geometry only
    print("\n📝 Preview of AADT and geometry:")
    if "AADT" in traffic.columns:
        print(traffic[["AADT", "geometry"]].head())
    else:
        print("⚠️ AADT column not found, showing geometry only:")
        print(traffic[["geometry"]].head())

except Exception as e:
    print("❌ Failed to load traffic shapefile:", e)
