import os
import pandas as pd

# Define paths
RAW_DIR = os.path.join("..", "data", "raw")
PROCESSED_DIR = os.path.join("..", "data", "processed")

def clean_data():
    print("=== Starting Day 2: Data Cleaning ===")
    
    # --- 1. CLEAN NAV HISTORY ---
    nav_path = os.path.join(RAW_DIR, "02_nav_history.csv")
    if os.path.exists(nav_path):
        df_nav = pd.read_csv(nav_path)
        
        # Convert date to standard datetime format [cite: 153]
        df_nav['date'] = pd.to_datetime(df_nav['date'])
        
        # Sort values chronologically [cite: 153]
        df_nav = df_nav.sort_values(by=['amfi_code', 'date'])
        
        # Drop duplicates [cite: 153]
        df_nav = df_nav.drop_duplicates(subset=['amfi_code', 'date'])
        
        # Handle weekends/holidays by forward-filling missing NAV values [cite: 104, 105, 253]
        # To do this correctly per fund, we group by amfi_code and ffill
        df_nav['nav'] = df_nav.groupby('amfi_code')['nav'].ffill()
        
        # Filter out bad records where NAV is zero or negative [cite: 153]
        df_nav = df_nav[df_nav['nav'] > 0]
        
        df_nav.to_csv(os.path.join(PROCESSED_DIR, "clean_nav.csv"), index=False)
        print(f"[SUCCESS] Cleaned NAV history: {len(df_nav)} rows saved.")

    # --- 2. CLEAN INVESTOR TRANSACTIONS ---
    tx_path = os.path.join(RAW_DIR, "08_investor_transactions.csv")
    if os.path.exists(tx_path):
        df_tx = pd.read_csv(tx_path)
        
        # Standardize transaction types to uppercase text [cite: 153]
        df_tx['transaction_type'] = df_tx['transaction_type'].str.strip().str.upper()
        
        # Validate amounts are strictly positive numbers [cite: 153]
        df_tx = df_tx[df_tx['amount_inr'] > 0]
        
        # Fix date formats [cite: 153]
        df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
        
        df_tx.to_csv(os.path.join(PROCESSED_DIR, "clean_transactions.csv"), index=False)
        print(f"[SUCCESS] Cleaned transactions: {len(df_tx)} rows saved.")
        
    # --- 3. COPY OTHER MASTER FILES ---
    # For fields that don't need extensive structural repair, we move them to processed
    for master_file in ["01_fund_master.csv", "07_scheme_performance.csv"]:
        src = os.path.join(RAW_DIR, master_file)
        if os.path.exists(src):
            df = pd.read_csv(src)
            df.to_csv(os.path.join(PROCESSED_DIR, master_file), index=False)

if __name__ == "__main__":
    clean_data()