# scripts/optimize_coverage.py

import os
import geopandas as gpd
import pandas as pd
import pulp

# ── 1. PROJECT ROOT ────────────────────────────────────
# this file lives in PROJECT_ROOT/scripts/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# ── 2. PATHS (all under PROJECT_ROOT/data) ────────────
CAND_FILE  = os.path.join(PROJECT_ROOT, "data", "processed", "candidate_sites_prepped.geojson")
TRACT_FILE = os.path.join(PROJECT_ROOT, "data", "cleaned",   "census_tracts_cleaned.geojson")
POP_FILE   = os.path.join(PROJECT_ROOT, "data", "cleaned",   "acs_population_cleaned.csv")
OUTPUT     = os.path.join(PROJECT_ROOT, "data", "processed", "optimal_sites_coverage.geojson")

# ensure the correct output folder exists
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# ── 3. PARAMETERS ───────────────────────────────────────
N_SITES    = 50
RADIUS_M   = 0.5 * 1609.34  # 0.5 miles in meters

# ── 4. LOAD CANDIDATE SITES ─────────────────────────────
cand = gpd.read_file(CAND_FILE).to_crs(epsg=3857)

# ── 5. LOAD TRACTS & POPULATION ────────────────────────
tracts = gpd.read_file(TRACT_FILE).to_crs(epsg=3857)
pop_df = pd.read_csv(POP_FILE, dtype={'GEOID': str})

# strip the "1400000US" prefix so we can merge on plain 11‑digit GEOID
pop_df['GEOID_short'] = pop_df['GEOID'].str[-11:]
pop_df = pop_df[pop_df['GEOID_short'].str.len() == 11]

# merge into tracts
tracts = (
    tracts
    .merge(pop_df[['GEOID_short','population']],
           left_on='GEOID',
           right_on='GEOID_short',
           how='left')
    .dropna(subset=['population'])
    .copy()
)

# ── 6. BUILD COVERAGE MAPPING ──────────────────────────
covers = {}
for j, poly in tracts.geometry.items():
    covers[j] = [
        i for i, pt in cand.geometry.items()
        if pt.distance(poly) <= RADIUS_M
    ]
# only keep tracts with at least one candidate inside the radius
covers = {j: sites for j, sites in covers.items() if sites}
served = list(covers)

print(f">> candidates: {len(cand)}, tracts w/ pop: {len(tracts)}, coverable tracts: {len(served)}")

# ── 7. FORMULATE MILP ───────────────────────────────────
prob = pulp.LpProblem("EV_Coverage", pulp.LpMaximize)
x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in cand.index}
y = {j: pulp.LpVariable(f"y_{j}", cat="Binary") for j in served}

# maximize covered population
prob += pulp.lpSum(tracts.at[j,'population'] * y[j] for j in served)

# budget constraint
prob += pulp.lpSum(x[i] for i in cand.index) <= N_SITES

# coverage constraints
for j, sites in covers.items():
    prob += pulp.lpSum(x[i] for i in sites) >= y[j]

# ── 8. SOLVE & WRITE OUTPUT ─────────────────────────────
solver = pulp.GLPK_CMD(msg=True)
prob.solve(solver)

selected = [i for i in cand.index if pulp.value(x[i]) > 0.5]
opt = cand.loc[selected].to_crs(epsg=4326)
opt.to_file(OUTPUT, driver="GeoJSON")

print(f"✅ Coverage MVP: selected {len(opt)} sites → {OUTPUT}")
