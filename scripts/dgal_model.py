# File: scripts/dgal_model.py

import os
import sys
from pathlib import Path

# ── Setup Project Paths ───────────────────────────────────────────
# Add project root directory to Python path for importing project modules (like config.py)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import geopandas as gpd
from scipy.spatial import cKDTree

# ── Pyomo Optimization Library ────────────────────────────────────
from pyomo.environ import (
    ConcreteModel, Set, Param, Var, Binary,
    Objective, Constraint, ConstraintList,
    SolverFactory, maximize
)

# ── Project Configuration ─────────────────────────────────────────
from config import (
    DEFAULT_N_SITES,
    DEFAULT_COVERAGE_WEIGHT,
    DEFAULT_MIN_DISTANCE,
    MAX_INPUT_SITES
)

def optimize_dgal(candidate_geojson: str,
                  tract_geojson: str,
                  N_sites: int = DEFAULT_N_SITES,
                  output_path: str = None,
                  demand_field: str = 'demand_score',
                  coverage_weight: float = DEFAULT_COVERAGE_WEIGHT,
                  min_distance: float = DEFAULT_MIN_DISTANCE):
    """
    Optimize EV charger placement using DGAL (Decision Guidance and Location) model.

    This function selects optimal candidate sites based on demand, while enforcing
    no-clumping constraints (minimum distance between sites) and maximizing coverage.

    Args:
        candidate_geojson (str): Path to candidate sites GeoJSON.
        tract_geojson (str): Path to census tracts GeoJSON.
        N_sites (int): Maximum number of sites to select.
        output_path (str): Optional path to save selected sites GeoJSON.
        demand_field (str): Column name to use for demand score.
        coverage_weight (float): Weight given to tract coverage in the objective.
        min_distance (float): Minimum allowed distance between selected sites.

    Returns:
        selected_gdf (GeoDataFrame): Selected optimal sites.
        objective_val (float): Objective function value at optimum.
    """

    # ── Step 1: Load candidate sites and tracts ─────────────────────
    sites = gpd.read_file(candidate_geojson)
    tracts = gpd.read_file(tract_geojson).to_crs(sites.crs)  # align coordinate reference system (CRS)

    # ── Step 2: Pre-filter candidates by demand ────────────────────
    # If too many sites, limit to top MAX_INPUT_SITES with highest demand
    if len(sites) > MAX_INPUT_SITES:
        top_idx = sites[demand_field].nlargest(MAX_INPUT_SITES).index
        sites = sites.loc[top_idx]

    # ── Step 3: Build coverage mapping ─────────────────────────────
    # Map each tract to sites that intersect it (i.e., potential coverage)
    covers = {
        tract_idx: [
            site_idx
            for site_idx, site_geom in zip(sites.index, sites.geometry)
            if site_geom.intersects(tract_geom)
        ]
        for tract_idx, tract_geom in tracts.geometry.items()
    }

    # ── Step 4: Precompute close site pairs (no-clumping constraint) ─
    site_list = list(sites.index)
    coords = [(pt.x, pt.y) for pt in sites.geometry]  # extract (x, y) coordinates
    tree = cKDTree(coords)
    pairs = tree.query_pairs(r=min_distance)
    close_pairs = [(site_list[i], site_list[j]) for i, j in pairs]

    # ── Step 5: Initialize Pyomo optimization model ─────────────────
    model = ConcreteModel()
    model.SITES = Set(initialize=site_list)
    model.TRACTS = Set(initialize=list(tracts.index))

    # ── Step 6: Load demand scores into model parameters ────────────
    demand_dict = sites[demand_field].to_dict()
    model.demand = Param(model.SITES, initialize=demand_dict)

    # ── Step 7: Define decision variables ───────────────────────────
    model.x = Var(model.SITES, domain=Binary)   # Site selection variable (0 or 1)
    model.y = Var(model.TRACTS, domain=Binary)  # Tract coverage variable (0 or 1)

    # ── Step 8: Define objective function ───────────────────────────
    # Maximize total demand + coverage bonus
    def _objective(m):
        return (
            sum(m.demand[i] * m.x[i] for i in m.SITES) +
            coverage_weight * sum(m.y[j] for j in m.TRACTS)
        )
    model.obj = Objective(rule=_objective, sense=maximize)

    # ── Step 9: Add site selection limit constraint ─────────────────
    model.site_limit = Constraint(expr=sum(model.x[i] for i in model.SITES) <= N_sites)

    # ── Step 10: Add coverage constraints ───────────────────────────
    # A tract is covered if at least one covering site is selected
    def _cover(m, j):
        return sum(m.x[i] for i in covers[j]) >= m.y[j]
    model.coverage = Constraint(model.TRACTS, rule=_cover)

    # ── Step 11: Add no-clumping constraints ────────────────────────
    # Prevent selection of site pairs that are too close to each other
    model.no_clump = ConstraintList()
    for i_idx, j_idx in close_pairs:
        model.no_clump.add(model.x[i_idx] + model.x[j_idx] <= 1)

    # ── Step 12: Solve the optimization model ───────────────────────
    solver = SolverFactory('cbc')
    solver.solve(model, tee=True)

    # ── Step 13: Extract selected sites ─────────────────────────────
    selected_idx = [i for i in model.SITES if model.x[i].value >= 0.5]
    selected_gdf = sites.loc[selected_idx].copy()

    # ── Step 14: Evaluate objective value ───────────────────────────
    objective_val = model.obj()

    # ── Step 15: Optionally save selected sites to GeoJSON ──────────
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        selected_gdf.to_file(output_path, driver="GeoJSON")

    return selected_gdf, objective_val


# ── Allow Running as Standalone Script ────────────────────────────
if __name__ == '__main__':
    import argparse

    # Setup CLI arguments
    parser = argparse.ArgumentParser(description='Run DGAL optimization')
    parser.add_argument('--candidates', default=str(BASE_DIR / 'data' / 'processed' / 'candidate_sites_prepped.geojson'))
    parser.add_argument('--tracts',    default=str(BASE_DIR / 'data' / 'cleaned'   / 'merged_data.geojson'))
    parser.add_argument('--output',    default=str(BASE_DIR / 'data' / 'processed' / 'optimal_sites_dgal.geojson'))
    parser.add_argument('--n_sites',   type=int,   default=DEFAULT_N_SITES)
    parser.add_argument('--weight',    type=float, default=DEFAULT_COVERAGE_WEIGHT)
    parser.add_argument('--min_dist',  type=float, default=DEFAULT_MIN_DISTANCE)
    args = parser.parse_args()

    # Run optimization
    sel, obj_val = optimize_dgal(
        candidate_geojson=args.candidates,
        tract_geojson=args.tracts,
        N_sites=args.n_sites,
        coverage_weight=args.weight,
        min_distance=args.min_dist,
        output_path=args.output
    )
    
    # Output summary
    print(f"✅ Selected {len(sel)} sites, objective={obj_val:.2f}")
