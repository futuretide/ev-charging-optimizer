import os, requests

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW, exist_ok=True)

# --- 1. NREL EV Chargers for DC ---
NREL_KEY = "Gl9jE0LoYM7TRV1fW4flisvbH99n5QnLrFWOu7yQ"  # paste your actual key here
url = (
    "https://developer.nrel.gov/api/alt-fuel-stations/v1.geojson"
    "?state=DC&fuel_type=ELEC&download=true&api_key=" + NREL_KEY
)

response = requests.get(url)
with open(os.path.join(RAW, "dc_stations.geojson"), "wb") as f:
    f.write(response.content)

print("✅ Downloaded: dc_stations.geojson")
