import pandas as pd

# Absolute path to the population data file
file_path = r"C:\Users\as212\OneDrive\Desktop\ev-dgs\data\raw\population\ACSDT5Y2022.B01003-Data.csv"

# Load the data
try:
    df = pd.read_csv(file_path)
    print("✅ Population data loaded successfully.")
    print("📊 Columns in the file:")
    print(df.columns.tolist())

    print("\n🔍 Sample rows:")
    print(df.head())
except Exception as e:
    print("❌ Error loading the file:", e)
