# File: scripts/filter_candidates.py

import os
import sys
from pathlib import Path

# Ensure config.py is importable
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import geopandas as gpd
from shapely.ops import unary_union
from config import PRE_FILTER_N

def main():
    scored_fp   = BASE_DIR / 'data' / 'processed' / 'candidate_sites_scored.geojson'
    prep_fp     = BASE_DIR / 'data' / 'processed' / 'candidate_sites_prepped.geojson'
    stations_fp = BASE_DIR / 'data' / 'raw'   / 'dc_stations.geojson'

    os.makedirs(prep_fp.parent, exist_ok=True)

    # 1. Load scored candidates and remember original CRS
    cands_orig = gpd.read_file(scored_fp)
    original_crs = cands_orig.crs

    # 2. Project candidates to metric CRS for accurate buffering
    metric_crs = "EPSG:3857"
    cands = cands_orig.to_crs(metric_crs)

    # 3. Load existing stations, project, and buffer by 500 m
    stations = gpd.read_file(stations_fp).to_crs(metric_crs)
    BUFFER_DIST = 500.0  # meters
    station_buffer = unary_union(stations.geometry.buffer(BUFFER_DIST))

    # 4. Drop candidates within the station buffer
    before = len(cands)
    cands = cands[~cands.geometry.within(station_buffer)]
    dropped = before - len(cands)
    print(f"⚠️  Dropped {dropped} candidates within {BUFFER_DIST:.0f} m of existing stations")

    # 5. Restore to original CRS for downstream compatibility
    cands = cands.to_crs(original_crs)

    # 6. Sort by demand_score and keep the top PRE_FILTER_N
    top = cands.sort_values('demand_score', ascending=False).head(PRE_FILTER_N)

    # 7. Save the pre-filtered candidates
    top.to_file(prep_fp, driver='GeoJSON')
    print(f"✅ Kept {len(top)} top candidates → {prep_fp}")

if __name__ == '__main__':
    main()
