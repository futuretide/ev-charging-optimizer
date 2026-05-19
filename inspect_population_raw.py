# File: inspect_population_raw.py

import os
import pandas as pd

# Build the path
path = os.path.join("data", "raw", "population", "ACSST5Y2022.B01003-Data.csv")
print("Looking for:", path)
print("Exists?   ", os.path.exists(path))

# If it exists, print the first few column names
if os.path.exists(path):
    cols = pd.read_csv(path, nrows=0).columns.tolist()
    print("Columns:", cols)
