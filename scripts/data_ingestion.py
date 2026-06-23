import os
import pandas as pd

RAW_DIR = os.path.join("..", "data", "raw")

TARGET_CSV_FILES = [
    "01_fund_master.csv", "02_nav_history.csv", "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv", "05_category_inflows.csv", "06_industry_folio_count.csv",
    "07_scheme_performance.csv", "08_investor_transactions.csv", "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

def ingest_and_audit():
    print("=== Launching Multi-Dataset Quality Audit Process ===\n")
    loaded_dfs = {}
    
    # --- 1. Load & Dynamic Structural Analysis ---
    for file in TARGET_CSV_FILES:
        path = os.path.join(RAW_DIR, file)
        if not os.path.exists(path):
            print(f"[CRITICAL] Missing target input vector: {file}")
            continue
            
        df = pd.read_csv(path)
        loaded_dfs[file] = df
        
        print(f"File: {file}")
        print(f" -> Matrix Dimensionality (Shape): {df.shape}")
        print(f" -> Column Data Mappings (dtypes):\n{df.dtypes.to_string()}")
        print(f" -> Head Vector Snippet:\n{df.head(2).to_string()}\n")
        print("-" * 60)

    # --- 2. Fund Master Granularity & Domain Scope Mapping ---
    if "01_fund_master.csv" in loaded_dfs:
        fm = loaded_dfs["01_fund_master.csv"]
        print("\n=== Fund Master Categorical Cardinality Dimensions ===")
        print(f"Unique AMCs Mapped: {fm['fund_house'].nunique()}")
        print(f"Unique Broad Categories Mapped: {fm['category'].unique()}")
        print(f"Unique Sub-Categories Mapped: {fm['sub_category'].nunique()}")
        print(f"Risk Profile Grades Mapped: {fm['risk_category'].unique()}\n")

    # --- 3. Cross-Table Relational Key Alignment Check ---
    if "01_fund_master.csv" in loaded_dfs and "02_nav_history.csv" in loaded_dfs:
        master_codes = set(loaded_dfs["01_fund_master.csv"]["amfi_code"].unique())
        history_codes = set(loaded_dfs["02_nav_history.csv"]["amfi_code"].unique())
        
        mismatches = master_codes - history_codes
        
        print("=== Cross-Relational Data Quality Integrity Summary ===")
        if not mismatches:
            print("[DATA QUALITY PASS] 100% relational cross-alignment. Every structural code key matches perfectly.")
        else:
            print(f"[DATA QUALITY ALERT] Found {len(mismatches)} master codes isolated from time-series logs.")
            print(f"Mismatched Code Sequences: {mismatches}")

if __name__ == "__main__":
    ingest_and_audit()