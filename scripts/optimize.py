# File: scripts/optimize.py

import sys, os
# Ensure project root (where config.py lives) is on the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DEFAULT_N_SITES, DEFAULT_COVERAGE_WEIGHT, DEFAULT_MIN_DISTANCE
from scripts.dgal_model import optimize_dgal

def main():
    # 1. Project root
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # 2. Input / output paths
    CAND_PREP       = os.path.join(ROOT, "data", "processed", "candidate_sites_prepped.geojson")
    TRACTS_MERGED   = os.path.join(ROOT, "data", "cleaned",   "merged_data.geojson")
    OUTPUT_SELECTED = os.path.join(ROOT, "data", "processed", "optimal_sites_dgal.geojson")

    # 3. Field names & defaults
    DEMAND_FIELD = "demand_score"

    # 4. Run the DGAL model with unified defaults
    selected_gdf, obj_val = optimize_dgal(
        candidate_geojson=CAND_PREP,
        tract_geojson=TRACTS_MERGED,
        N_sites=DEFAULT_N_SITES,
        output_path=OUTPUT_SELECTED,
        demand_field=DEMAND_FIELD,
        coverage_weight=DEFAULT_COVERAGE_WEIGHT,
        min_distance=DEFAULT_MIN_DISTANCE,
    )

    # 5. Summary
    print(f"✅ Selected {len(selected_gdf)} sites")
    print(f"🔢 Objective value: {obj_val}")
    print(f"📂 Results saved to: {OUTPUT_SELECTED}")

if __name__ == "__main__":
    main()
