# File: ev_dgs_sensitivity.py

import sys
import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

# ──────────────────────────────────────────────────────────────────────────────
# Adjust this to your local project root before running
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
# ──────────────────────────────────────────────────────────────────────────────

from config import DEFAULT_N_SITES, DEFAULT_COVERAGE_WEIGHT, DEFAULT_MIN_DISTANCE
from scripts.dgal_model import optimize_dgal

# Data paths
TRACTS_FP = PROJECT_ROOT / "data/cleaned/merged_data.geojson"
CAND_FP   = PROJECT_ROOT / "data/processed/candidate_sites_prepped.geojson"
OPT_FP    = PROJECT_ROOT / "data/processed/optimal_sites_dgal.geojson"

# Load base GeoDataFrames
gdf_tracts = gpd.read_file(TRACTS_FP)

# ──────────────────────────────────────────────────────────────────────────────
# 1) Demand vs. Coverage‐Weight Trade‐off
# ──────────────────────────────────────────────────────────────────────────────
weights = [0, 25, 50, 75, 100]
demands, covers, times_w = [], [], []

for w in weights:
    t0 = time.time()
    sel, obj = optimize_dgal(
        candidate_geojson=str(CAND_FP),
        tract_geojson=str(TRACTS_FP),
        N_sites=DEFAULT_N_SITES,
        coverage_weight=w,
        min_distance=DEFAULT_MIN_DISTANCE,
        output_path=None
    )
    times_w.append(time.time() - t0)
    demands.append(obj)
    covered = gpd.sjoin(gdf_tracts, sel.to_crs(gdf_tracts.crs),
                        predicate="contains", how="left")
    covers.append(covered["index_right"].notnull().sum())

fig, ax = plt.subplots()
ax.plot(weights, demands, marker="o", label="Demand objective")
ax.set_xlabel("Coverage weight (λ)")
ax.set_ylabel("Objective value")
ax2 = ax.twinx()
ax2.plot(weights, covers, marker="s", color="C1", label="Tracts covered")
ax2.set_ylabel("Tracts covered")
fig.suptitle("Trade‐off: Demand vs Coverage Weight")
ax.legend(loc="upper left")
ax2.legend(loc="upper right")
fig.savefig(PROJECT_ROOT / "tradeoff_demand_coverage.png", dpi=300)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# 2) Sensitivity: Objective vs. Number of Chargers (N_sites)
# ──────────────────────────────────────────────────────────────────────────────
n_sites_list = [10, 20, 30, 40, 50, 75, 100]
objs_n, times_n = [], []

for n in n_sites_list:
    t0 = time.time()
    sel, obj = optimize_dgal(
        candidate_geojson=str(CAND_FP),
        tract_geojson=str(TRACTS_FP),
        N_sites=n,
        coverage_weight=DEFAULT_COVERAGE_WEIGHT,
        min_distance=DEFAULT_MIN_DISTANCE,
        output_path=None
    )
    objs_n.append(obj)
    times_n.append(time.time() - t0)

fig, ax = plt.subplots()
ax.plot(n_sites_list, objs_n, marker="o")
ax.set_xlabel("Number of chargers (N_sites)")
ax.set_ylabel("Objective value")
ax.set_title("Sensitivity: Objective vs N_sites")
fig.savefig(PROJECT_ROOT / "sensitivity_objective_n_sites.png", dpi=300)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# 3) Heat‐map: Distance to Nearest Selected Charger
# ──────────────────────────────────────────────────────────────────────────────
# Compute centroid distances
centroids = gdf_tracts.copy()
centroids["centroid"] = centroids.geometry.centroid
coords_tr = [(p.x, p.y) for p in centroids["centroid"]]

sel = gpd.read_file(OPT_FP).to_crs(gdf_tracts.crs)
coords_opt = [(p.x, p.y) for p in sel.geometry]
tree = cKDTree(coords_opt)
dists, _ = tree.query(coords_tr, k=1)
gdf_tracts["dist_to_charger"] = dists

fig, ax = plt.subplots(figsize=(8,6))
gdf_tracts.plot(column="dist_to_charger", legend=True, ax=ax)
ax.set_title("Distance to Nearest Selected Charger")
ax.set_axis_off()
fig.savefig(PROJECT_ROOT / "heatmap_distance_to_charger.png", dpi=300)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# 4) Coverage by Income Quintile
# ──────────────────────────────────────────────────────────────────────────────
gdf_tracts["income_q"] = pd.qcut(gdf_tracts["median_income"], 5, labels=False)
covered = gpd.sjoin(gdf_tracts, sel[["geometry"]],
                    predicate="contains", how="left")
cover_counts = covered.groupby("income_q")["index_right"]\
                      .apply(lambda s: s.notnull().sum())
total_counts = gdf_tracts.groupby("income_q").size()
frac_covered  = cover_counts / total_counts

fig, ax = plt.subplots()
frac_covered.plot(kind="bar", ax=ax)
ax.set_xlabel("Income Quintile (0=lowest → 4=highest)")
ax.set_ylabel("Fraction of tracts covered")
ax.set_title("Coverage by Income Quintile")
fig.savefig(PROJECT_ROOT / "coverage_by_quintile.png", dpi=300)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# 5) Distribution of Chargers per Tract
# ──────────────────────────────────────────────────────────────────────────────
charger_counts = covered.loc[covered["index_right"].notnull()]\
                       .groupby("GEOID").size()
dist_counts   = charger_counts.value_counts().sort_index()

fig, ax = plt.subplots()
dist_counts.plot(kind="bar", ax=ax)
ax.set_xlabel("Chargers per tract")
ax.set_ylabel("Number of tracts")
ax.set_title("Distribution of Chargers per Tract")
fig.savefig(PROJECT_ROOT / "chargers_per_tract_distribution.png", dpi=300)
plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# 6) Solver Performance Profile
# ──────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots()
ax.plot(weights, times_w, marker="o", label="λ sweep")
ax.plot(n_sites_list, times_n, marker="s", label="N_sites sweep")
ax.set_xlabel("Parameter value")
ax.set_ylabel("Solve time (s)")
ax.set_title("Solver Performance Profiles")
ax.legend()
fig.savefig(PROJECT_ROOT / "solver_performance.png", dpi=300)
plt.close(fig)

print("✅ All sensitivity and exploratory visuals generated (six PNGs).")
