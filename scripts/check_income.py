import pandas as pd

# ── Define Path to the Raw Income Data ────────────────────────────
# Absolute path to the ACS income CSV file
file_path = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\raw\acs_income\ACSST5Y2022.S1901-Data.csv"

# ── Load the CSV Data ────────────────────────────────────────────
# Read the CSV file while skipping the first row which contains additional metadata or headers
df = pd.read_csv(file_path, skiprows=1)

# ── Inspect the Loaded Data ──────────────────────────────────────
# Print the list of column names to understand the structure of the dataset
print("📊 Columns in the file:")
print(df.columns.tolist())

# Display the first few rows to inspect sample data entries
print("\n🔍 Sample rows:")
print(df.head())
