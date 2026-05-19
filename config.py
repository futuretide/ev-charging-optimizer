# config.py

# ──────────────────────────────────────────────────────────────────────────────
# Core defaults
# ──────────────────────────────────────────────────────────────────────────────
# How many chargers to place by default
DEFAULT_N_SITES = 50

# Weight given to covering each new tract in the objective
DEFAULT_COVERAGE_WEIGHT = 100.0   # was 25.0

# Minimum allowed distance (in meters) between any two selected sites
DEFAULT_MIN_DISTANCE = 500.0      # was 750.0

# ──────────────────────────────────────────────────────────────────────────────
# Centralized thresholds for candidate filtering & safety caps
# ──────────────────────────────────────────────────────────────────────────────
# Number of top‐scored candidates to keep before optimization
PRE_FILTER_N = 2000               # was 500

# Safety cap inside the DGAL model for very large inputs
MAX_INPUT_SITES = 2000            # unchanged
