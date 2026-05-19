import os
import geopandas as gpd
import pandas as pd

# —————————————————————————————————————————————
# Paths (adjust if needed)
# —————————————————————————————————————————————
ROOT         = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRACTS_FILE  = os.path.join(ROOT, "data", "cleaned",   "merged_data.geojson")
CAND_FILE    = os.path.join(ROOT, "data", "processed","candidate_sites_prepped.geojson")
SELECTED     = os.path.join(ROOT, "data", "processed","optimal_sites_dgal.geojson")

def main():
    # 1) Load
    tracts     = gpd.read_file(TRACTS_FILE)
    candidates = gpd.read_file(CAND_FILE)
    selected   = gpd.read_file(SELECTED)

    # 2) Ensure same CRS for spatial join
    selected = selected.to_crs(tracts.crs)

    # 3) Cast numeric columns
    tracts["population"]    = pd.to_numeric(tracts["population"], errors="coerce")
    candidates["demand_score"] = pd.to_numeric(candidates["demand_score"], errors="coerce")
    selected["demand_score"]   = pd.to_numeric(selected["demand_score"], errors="coerce")

    # 4) Spatial join to mark which tracts are served
    served = gpd.sjoin(
        tracts, 
        selected[["geometry"]], 
        how="left", 
        predicate="intersects"
    )
    served["served"] = ~served["index_right"].isnull()

    # 5) Compute metrics
    total_tracts    = len(served)
    tracts_served   = served["served"].sum()
    pop_total       = served["population"].sum()
    pop_served      = served.loc[served["served"], "population"].sum()
    total_demand    = candidates["demand_score"].sum()
    demand_selected = selected["demand_score"].sum()

    # 6) Print summary
    print(f"Tracts served:      {tracts_served} of {total_tracts}  ({tracts_served/total_tracts:.1%})")
    print(f"Population served:  {pop_served:,.0f} of {pop_total:,.0f}  ({pop_served/pop_total:.1%})")
    print(f"Demand captured:    {demand_selected:,.0f} of {total_demand:,.0f}  ({demand_selected/total_demand:.1%})")

if __name__ == "__main__":
    main()
