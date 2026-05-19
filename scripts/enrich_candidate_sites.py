# File: scripts/enrich_candidate_sites.py

import os
import sys
from pathlib import Path

# ── Add Project Root to Python Path ────────────────────────────────
# This ensures that project-level modules like config.py can be imported
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
from sklearn.preprocessing import MinMaxScaler

def main():
    # ── Define File Paths ───────────────────────────────────────────
    ROOT          = BASE_DIR
    CAND_RAW      = ROOT / "data" / "processed" / "candidate_sites_raw.geojson"
    TRACTS_MERGED = ROOT / "data" / "cleaned"   / "merged_data.geojson"
    STATIONS      = ROOT / "data" / "raw"       / "dc_stations.geojson"
    CAND_SCORED   = ROOT / "data" / "processed" / "candidate_sites_scored.geojson"

    # ── Step 1: Load GeoSpatial Data and Project to Metric CRS ───────
    # Load candidate sites, merged tracts, and existing stations data
    # Reproject all data to EPSG:3857 (metric units) to enable distance calculations
    candidates = gpd.read_file(CAND_RAW).to_crs(epsg=3857)
    tracts     = gpd.read_file(TRACTS_MERGED).to_crs(epsg=3857)
    stations   = gpd.read_file(STATIONS).to_crs(epsg=3857)

    # ── Step 2: Spatial Join to Attach Population and Income ─────────
    # Select only relevant columns from tracts and spatially join with candidates
    tracts_sel = tracts[["GEOID", "population", "median_income", "geometry"]]
    enriched   = gpd.sjoin(candidates, tracts_sel, how="left", predicate="intersects")

    # ── Step 3: Remove Candidates Without Population/Income Data ────
    # Drop candidates that did not intersect with any tract (i.e., no population data)
    before = len(enriched)
    enriched = enriched.dropna(subset=["population", "median_income"])
    print(f"Filtered out {before - len(enriched)} orphan sites; {len(enriched)} remain.")

    # ── Step 4: Normalize Population and Income Features ────────────
    # Convert columns to float to ensure numeric scaling
    enriched["population"]    = enriched["population"].astype(float)
    enriched["median_income"] = enriched["median_income"].astype(float)

    # Apply Min-Max scaling to normalize population and income between 0 and 1
    scaler = MinMaxScaler()
    enriched["pop_norm"] = scaler.fit_transform(enriched[["population"]])
    enriched["inc_norm"] = scaler.fit_transform(enriched[["median_income"]])

    # ── Step 5: Calculate Distance to Nearest Existing Station ──────
    # Compute Euclidean distance to nearest existing station
    coords_sites = np.vstack(enriched.geometry.apply(lambda p: (p.x, p.y)))
    coords_stn   = np.vstack(stations.geometry.apply(lambda p: (p.x, p.y)))
    tree = cKDTree(coords_stn)
    dist, _ = tree.query(coords_sites, k=1)

    # Normalize distances so that nearer sites get higher score (1 - normalized distance)
    enriched["dist_norm"] = 1 - scaler.fit_transform(dist.reshape(-1, 1))

    # ── Step 6: Calculate Final Demand Score ────────────────────────
    # Weighted sum of normalized population, income, and distance
    w_pop, w_inc, w_dist = 1.0, 1.0, 0.5
    enriched["demand_score"] = (
        w_pop  * enriched["pop_norm"] +
        w_inc  * enriched["inc_norm"] +
        w_dist * enriched["dist_norm"]
    )

    # ── Step 7: Cleanup Intermediate Columns and Save ───────────────
    # Remove temporary normalized columns
    enriched = enriched.drop(
        columns=["index_right", "pop_norm", "inc_norm", "dist_norm"], errors="ignore"
    )

    # Ensure output directory exists and save enriched candidate sites
    os.makedirs(CAND_SCORED.parent, exist_ok=True)
    enriched.to_file(CAND_SCORED, driver="GeoJSON")

    print(f"✅ Scored {len(enriched)} sites → {CAND_SCORED}")

# ── Entry Point ───────────────────────────────────────────────────
if __name__ == "__main__":
    main()
